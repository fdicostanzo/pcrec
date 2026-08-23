#!/usr/bin/env python3
"""studies/tt4_batching/proto/bench.py — [TT-4.1] Stage B batching prototype.

Measures three compile SHAPES over a FIXED pool of TOTAL real generated
patterns (collect_patterns.py's output: rxNNNN.c/rxNNNN.h pairs, distinct
prefixes, all sharing one --features set), at batch size N in
{1,4,16,64,256} (patterns split into TOTAL/N batches of N):

  C (baseline): one gcc call per PATTERN -- compile the pattern's gen.c
    plus a single-pattern dispatch driver, in one compile+link call
    (dispatch_gen.py with one prefix reproduces driver.c's exact protocol,
    so this is the harness's own shape, same GENCFLAGS).
  A (link-batching): one `gcc -c` per pattern in the batch, plus one `gcc -c`
    for the batch's dispatch driver, then ONE link of all N+1 objects.
  B (TU-batching): concatenate the N patterns' gen.c bodies into one file,
    compile THAT plus the dispatch driver in ONE gcc call (compile+link).

Each (shape, N) cell is measured SERIALLY (batches built one after another,
clean per-call attribution) and with 12-way PARALLELISM over batches
(concurrent.futures, matching the harness's own PROCS=$(nproc) shape),
repeated REPS times, reporting median and min wall. Peak RSS is taken from
the single largest-N TU compile under `/usr/bin/time -v`. Every batched
executable's output is diff-checked against the SAME pattern's baseline
(shape C) single-matcher output on a few subjects, so a faster-but-wrong
prototype cannot pass silently. A separate --failure-isolation run plants a
syntax error in one batch member and times shape B's all-or-nothing cost.

Usage:
  bench.py --patterns DIR --outdir DIR --sizes 1,4,16,64,256 --total 256
           [--reps 3] [--parallel 12] [--gencflags '-O1 -std=gnu11 -Wall -Wextra -Werror']
  bench.py --patterns DIR --outdir DIR --failure-isolation N
"""
import argparse
import concurrent.futures
import glob
import json
import os
import shutil
import statistics
import subprocess
import sys
import time

def read_manifest(patterns_dir, total):
    manifest = os.path.join(patterns_dir, "manifest.tsv")
    prefixes = []
    with open(manifest) as f:
        f.readline()
        for line in f:
            prefixes.append(line.split("\t", 1)[0])
    return prefixes[:total]

def dispatch_gen(script_dir, prefixes, out_c):
    subprocess.run([sys.executable, os.path.join(script_dir, "dispatch_gen.py")] + prefixes,
                    stdout=open(out_c, "w"), check=True)

def run_cc(gcc_argv, cwd=None):
    t0 = time.monotonic()
    r = subprocess.run(gcc_argv, cwd=cwd, capture_output=True, text=True)
    t1 = time.monotonic()
    return r.returncode, t1 - t0, r.stdout + r.stderr

def build_batch_C(script_dir, patterns_dir, workdir, prefix, gencflags):
    """Baseline: one gcc call, compile+link, for ONE pattern."""
    d = os.path.join(workdir, f"C_{prefix}")
    os.makedirs(d, exist_ok=True)
    drv = os.path.join(d, "drv.c")
    dispatch_gen(script_dir, [prefix], drv)
    src = os.path.join(patterns_dir, f"{prefix}.c")
    exe = os.path.join(d, "t")
    argv = ["gcc"] + gencflags + ["-I", patterns_dir, "-o", exe, drv, src]
    rc, wall, out = run_cc(argv)
    return rc, wall, out, exe

def build_batch_A(script_dir, patterns_dir, workdir, prefixes, gencflags, batch_id):
    """Link-step batching: -c per member + driver, then one link."""
    d = os.path.join(workdir, f"A_{batch_id}")
    os.makedirs(d, exist_ok=True)
    drv = os.path.join(d, "drv.c")
    dispatch_gen(script_dir, prefixes, drv)
    total_wall = 0.0
    objs = []
    outs = []
    for p in prefixes:
        src = os.path.join(patterns_dir, f"{p}.c")
        obj = os.path.join(d, f"{p}.o")
        rc, wall, out = run_cc(["gcc"] + gencflags + ["-I", patterns_dir, "-c", "-o", obj, src])
        total_wall += wall
        outs.append(out)
        if rc != 0:
            return rc, total_wall, "\n".join(outs), None
        objs.append(obj)
    drv_obj = os.path.join(d, "drv.o")
    rc, wall, out = run_cc(["gcc"] + gencflags + ["-I", patterns_dir, "-c", "-o", drv_obj, drv])
    total_wall += wall
    outs.append(out)
    if rc != 0:
        return rc, total_wall, "\n".join(outs), None
    exe = os.path.join(d, "t")
    rc, wall, out = run_cc(["gcc"] + gencflags + ["-o", exe, drv_obj] + objs)
    total_wall += wall
    outs.append(out)
    return rc, total_wall, "\n".join(outs), exe

def build_batch_B(script_dir, patterns_dir, workdir, prefixes, gencflags, batch_id, measure_rss=False):
    """TU batching: concatenate gen.c bodies, one gcc call compile+link."""
    d = os.path.join(workdir, f"B_{batch_id}")
    os.makedirs(d, exist_ok=True)
    drv = os.path.join(d, "drv.c")
    dispatch_gen(script_dir, prefixes, drv)
    tu = os.path.join(d, "batch_tu.c")
    with open(tu, "w") as out_f:
        for p in prefixes:
            with open(os.path.join(patterns_dir, f"{p}.c")) as in_f:
                out_f.write(in_f.read())
                out_f.write("\n")
    exe = os.path.join(d, "t")
    argv = ["gcc"] + gencflags + ["-I", patterns_dir, "-o", exe, drv, tu]
    if measure_rss:
        rss_out = os.path.join(d, "time.out")
        argv = ["/usr/bin/time", "-v", "-o", rss_out] + argv
        rc, wall, out = run_cc(argv)
        max_rss = None
        if os.path.exists(rss_out):
            for line in open(rss_out):
                if "Maximum resident set size" in line:
                    max_rss = int(line.split(":")[1].strip())
        return rc, wall, out, exe, max_rss
    rc, wall, out = run_cc(argv)
    return rc, wall, out, exe

def chunk(lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]

def check_output(exe, index, subject, expected):
    r = subprocess.run([exe, str(index), subject], capture_output=True, text=True)
    return r.stdout == expected

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--sizes", default="1,4,16,64,256")
    ap.add_argument("--total", type=int, default=256)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--parallel", type=int, default=12)
    ap.add_argument("--gencflags", default="-O1 -std=gnu11 -Wall -Wextra -Werror")
    ap.add_argument("--failure-isolation", type=int, default=None,
                     help="N: plant a syntax error in one member of an N-batch, "
                          "time shape B's all-or-nothing failure cost")
    args = ap.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    gencflags = args.gencflags.split()
    os.makedirs(args.outdir, exist_ok=True)
    all_prefixes = read_manifest(args.patterns, args.total)
    if len(all_prefixes) < args.total:
        print(f"WARNING: manifest has only {len(all_prefixes)} patterns, wanted {args.total}", file=sys.stderr)

    if args.failure_isolation is not None:
        N = args.failure_isolation
        batch = all_prefixes[:N]
        d = os.path.join(args.outdir, "failure_isolation")
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)
        # plant a syntax error by corrupting a copy of one member's .c
        src_dir = os.path.join(d, "patterns")
        os.makedirs(src_dir, exist_ok=True)
        for p in batch:
            shutil.copy(os.path.join(args.patterns, f"{p}.c"), src_dir)
            shutil.copy(os.path.join(args.patterns, f"{p}.h"), src_dir)
        victim = os.path.join(src_dir, f"{batch[-1]}.c")
        with open(victim, "a") as f:
            f.write("\nTHIS IS A PLANTED SYNTAX ERROR;\n")
        t0 = time.monotonic()
        rc, wall, out, exe = build_batch_B(script_dir, src_dir, d, batch, gencflags, "fail")
        t1 = time.monotonic()
        print(f"failure-isolation N={N}: shape B batch rc={rc} (expect nonzero) "
              f"wall={t1-t0:.3f}s -- whole batch fails on ONE planted syntax error")
        # cost of falling back to per-pattern for just the batch members:
        t0 = time.monotonic()
        fallback_rcs = []
        for p in batch:
            rc2, wall2, out2, exe2 = build_batch_C(script_dir, args.patterns, d, p, gencflags)
            fallback_rcs.append(rc2)
        t1 = time.monotonic()
        print(f"failure-isolation N={N}: per-pattern fallback for all {N} members "
              f"(the planted-error one still fails elsewhere) wall={t1-t0:.3f}s, "
              f"rcs={fallback_rcs}")
        return

    sizes = [int(x) for x in args.sizes.split(",")]
    results = []

    for N in sizes:
        batches = chunk(all_prefixes, N)
        for shape in ("C", "A", "B"):
            for mode in ("serial", "parallel"):
                walls = []
                for rep in range(args.reps):
                    d = os.path.join(args.outdir, f"run_{shape}_{N}_{mode}_{rep}")
                    shutil.rmtree(d, ignore_errors=True)
                    os.makedirs(d, exist_ok=True)
                    t0 = time.monotonic()
                    failures = 0
                    if shape == "C":
                        tasks = all_prefixes  # one gcc call per PATTERN, not per batch
                        def do_C(p, d=d):
                            rc, wall, out, exe = build_batch_C(script_dir, args.patterns, d, p, gencflags)
                            return rc
                        if mode == "serial":
                            for p in tasks:
                                if do_C(p) != 0:
                                    failures += 1
                        else:
                            with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as ex:
                                for rc in ex.map(do_C, tasks):
                                    if rc != 0:
                                        failures += 1
                    else:
                        build_fn = build_batch_A if shape == "A" else build_batch_B
                        def do_batch(item, d=d, build_fn=build_fn):
                            bid, members = item
                            rc, wall, out, exe = build_fn(script_dir, args.patterns, d, members, gencflags, bid)
                            return rc
                        items = list(enumerate(batches))
                        if mode == "serial":
                            for item in items:
                                if do_batch(item) != 0:
                                    failures += 1
                        else:
                            with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as ex:
                                for rc in ex.map(do_batch, items):
                                    if rc != 0:
                                        failures += 1
                    t1 = time.monotonic()
                    walls.append(t1 - t0)
                    if failures:
                        print(f"WARNING: shape={shape} N={N} mode={mode} rep={rep}: {failures} batch(es) failed to compile", file=sys.stderr)
                    shutil.rmtree(d, ignore_errors=True)
                median_w = statistics.median(walls)
                min_w = min(walls)
                print(f"shape={shape} N={N:>4} mode={mode:<8} median={median_w:>8.3f}s min={min_w:>8.3f}s reps={walls}")
                results.append({"shape": shape, "N": N, "mode": mode, "median": median_w, "min": min_w, "reps": walls})

    with open(os.path.join(args.outdir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # peak RSS on the largest-N TU compile
    biggest_N = max(sizes)
    biggest_batch = chunk(all_prefixes, biggest_N)[0]
    d = os.path.join(args.outdir, "rss_probe")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    rc, wall, out, exe, max_rss = build_batch_B(script_dir, args.patterns, d, biggest_batch, gencflags, "rss", measure_rss=True)
    print(f"peak RSS for the N={biggest_N} TU compile (shape B): rc={rc} wall={wall:.3f}s max_rss_kb={max_rss}")

    # correctness check: baseline vs one N=biggest batch, a few subjects per pattern
    print("\ncorrectness check: baseline (shape C) vs the same batch's shape-B executable")
    ok = 0
    bad = 0
    check_batch = biggest_batch[:min(8, len(biggest_batch))]
    for i, p in enumerate(check_batch):
        d2 = os.path.join(args.outdir, "correctness_baseline")
        os.makedirs(d2, exist_ok=True)
        rc, wall, out, base_exe = build_batch_C(script_dir, args.patterns, d2, p, gencflags)
        if rc != 0:
            continue
        for subject in ("a", "abcabc", "", "xyz"):
            r_base = subprocess.run([base_exe, "0", subject], capture_output=True, text=True)
            r_batch = subprocess.run([exe, str(i), subject], capture_output=True, text=True)
            if r_base.stdout == r_batch.stdout and r_base.returncode == r_batch.returncode:
                ok += 1
            else:
                bad += 1
                print(f"  MISMATCH pattern={p} subject={subject!r}: baseline={r_base.stdout!r}(rc={r_base.returncode}) "
                      f"batch={r_batch.stdout!r}(rc={r_batch.returncode})")
    print(f"correctness: {ok} matched, {bad} mismatched")

if __name__ == "__main__":
    main()
