#!/usr/bin/env python3
"""studies/tt4m_batchrun/batchrun.py — [TT-4M] darwin batched-build validation.

Measures, on THIS Mac, whether batching K pcrec-generated matchers into
ONE gcc link (shape L: one gcc invocation naming N distinct .c sources
plus a generated dispatch main(), each source its own translation unit by
construction) beats the harness's own one-process-per-pattern path
(pcrec spawn + gcc spawn + a `timeout`-wrapped matcher-run spawn per
case), and by how much, holding the per-case execution shape IDENTICAL
between the two paths so the measured delta is the gcc-invocation-count
lever alone (see docs/dev/tt4m_darwin_validation.md for why exec-batching
is out of this row's scope -- [TT-4.1] already measured that lever on
Linux and it is not what Frank's directive here is about).

Never touches tests/harness/ or src/. Reads real patterns/cases collected
by collect_patterns.py/extract_cases.py; spawns build/pcrec, gcc-16 (or
$CC), and $TIMEOUT_BIN exactly as tests/harness/run.sh would, from a
scratch working directory.

Subcommands:
  baseline   the unbatched harness shape: per pattern, pcrec spawn (prefix
             "rx", fresh dir) + gcc spawn (tests/harness/driver.c
             unmodified, default RXT_PREFIX=rx) + one timeout-wrapped
             matcher-run spawn per case.
  batched    shape L: per BATCH of N patterns, N pcrec spawns (distinct
             prefixes rxNNNN, one shared batch dir) + ONE gcc spawn
             (dispatch.c + the N gen.c files named as separate arguments)
             + one timeout-wrapped matcher-run spawn per case (same
             per-case shape as baseline -- see module docstring).
  parallel   [TT-4M] STEP 2 (2a): P CONCURRENT shape-L batch pipelines,
             each an independent `batched` SUBPROCESS (self-reinvocation,
             own sub-pool + own workdir -- the SAME shape tests/harness/
             run.sh's own PROCS>1 fan-out uses: N.B. that PROCS shards
             FILES, this shards BATCHES, which is the harness-adoption
             analogue since a batch here is the harness's proposed
             dispatch unit). The corpus's BATCHES (not raw rows) are
             round-robined across P workers so worker shard sizes stay
             even regardless of how batch-size N divides the pool. Wall
             is the PARENT's own outer wall clock (workers genuinely
             overlap; summing each worker's own wall would double-count
             concurrent time); CPU is read via THIS process's
             RUSAGE_CHILDREN after every worker is reaped, which per
             POSIX wait(2) semantics cascades a worker's own
             RUSAGE_CHILDREN (its pcrec/gcc/run grandchildren) up into
             this total the moment the worker itself terminates -- cross-
             checked against the SUM of each worker's own self-reported
             cpu total (should closely agree; a gap beyond interpreter-
             startup noise would be a bug in this reasoning, not just a
             number to report).
  failure-iso  plants a syntax error in one batch member's gen.c COPY and
             measures shape L's all-or-nothing compile-failure cost
             against the per-pattern fallback cost to recover the batch's
             other good members.

Every subcommand prints one JSON object to stdout: wall seconds, CPU
seconds (sum of child user+sys via resource.getrusage(RUSAGE_CHILDREN)
deltas), exact process-spawn counts by kind (pcrec/gcc/run), and per-case
(prefix, subject, startpos) -> (stdout, exit_code) so a caller can diff
baseline vs batched for the answer-identity check.

Usage:
  batchrun.py baseline  --pool DIR --pcrec PATH --cc CC --timeout-bin BIN
                         --gencflags '...' --driver PATH --run-secs N
                         --out results.json
  batchrun.py batched   (same flags) --batch-size N --out results.json
  batchrun.py failure-iso --pool DIR --pcrec PATH --cc CC --gencflags '...'
                         --batch-size N --out results.json
"""
import argparse
import json
import os
import resource
import shutil
import subprocess
import sys
import time

def read_manifest(pool_dir):
    rows = []
    with open(os.path.join(pool_dir, "manifest.tsv")) as f:
        f.readline()
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 5:
                rows.append(dict(zip(["prefix", "source_file", "features", "flags", "pattern"], parts)))
    return rows

def read_cases(pool_dir):
    """prefix -> [(subject_raw, startpos), ...], from cases.tsv (written by
    extract_cases.py alongside the manifest)."""
    cases = {}
    with open(os.path.join(pool_dir, "cases.tsv")) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            prefix, subj, pos = parts
            cases.setdefault(prefix, []).append((subj, pos))
    return cases

class Spawner:
    """Wraps subprocess.run, counting calls by KIND and accumulating wall
    and (child) CPU time. CPU is measured via getrusage(RUSAGE_CHILDREN)
    DELTAS around each call -- exact for THIS process tree as long as
    nothing else forks concurrently in the same interpreter, true here
    (this script runs single-threaded, serial spawns only, by design: a
    parallel-mode sweep is a SEPARATE, later concern -- see the memo)."""
    def __init__(self):
        self.counts = {}
        self.wall = {}
        self.cpu = {}

    def run(self, kind, argv, **kw):
        self.counts[kind] = self.counts.get(kind, 0) + 1
        ru0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = time.perf_counter()
        r = subprocess.run(argv, capture_output=True, text=True, **kw)
        t1 = time.perf_counter()
        ru1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        self.wall[kind] = self.wall.get(kind, 0.0) + (t1 - t0)
        self.cpu[kind] = self.cpu.get(kind, 0.0) + \
            ((ru1.ru_utime - ru0.ru_utime) + (ru1.ru_stime - ru0.ru_stime))
        return r

    def summary(self):
        return {
            "counts": dict(self.counts),
            "wall_by_kind": {k: round(v, 4) for k, v in self.wall.items()},
            "cpu_by_kind": {k: round(v, 4) for k, v in self.cpu.items()},
            "total_wall": round(sum(self.wall.values()), 4),
            "total_cpu": round(sum(self.cpu.values()), 4),
            "total_procs": sum(self.counts.values()),
        }

def pcrec_argv(pcrec, prefix, row, out_c):
    argv = [pcrec, "-p", prefix]
    if "i" in row["flags"]:
        argv += ["-i"]
    if row["features"]:
        argv += ["--features", row["features"]]
    argv += ["-o", out_c, "--", row["pattern"]]
    return argv

def run_cases(sp, timeout_bin, run_secs, exe, extra_argv_prefix, cases):
    """extra_argv_prefix: [] for baseline (t subj pos), [index] for batched
    (dispatch index subj pos). Returns {(subj,pos): (stdout, rc)}."""
    out = {}
    for subj, pos in cases:
        argv = [timeout_bin, str(run_secs), exe] + extra_argv_prefix + [subj, pos]
        r = sp.run("run", argv)
        out[(subj, pos)] = (r.stdout, r.returncode)
    return out

def cmd_baseline(args):
    rows = read_manifest(args.pool)
    if args.limit:
        rows = rows[:args.limit]
    cases_by_prefix = read_cases(args.pool)
    sp = Spawner()
    workdir = args.workdir or "/tmp/tt4m_baseline"
    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    gencflags = args.gencflags.split()
    results = {"cases": {}, "compile_failures": []}
    for row in rows:
        bdir = os.path.join(workdir, row["prefix"])
        os.makedirs(bdir, exist_ok=True)
        gen_c = os.path.join(bdir, "gen.c")
        r = sp.run("pcrec", pcrec_argv(args.pcrec, "rx", row, gen_c))
        if r.returncode != 0 or not os.path.exists(os.path.join(bdir, "gen.h")):
            results["compile_failures"].append({"prefix": row["prefix"], "stage": "pcrec", "err": r.stderr})
            continue
        exe = os.path.join(bdir, "t")
        r = sp.run("gcc", [args.cc] + gencflags + ["-I", bdir, "-o", exe, args.driver, gen_c])
        if r.returncode != 0:
            results["compile_failures"].append({"prefix": row["prefix"], "stage": "gcc", "err": r.stderr})
            continue
        cases = cases_by_prefix.get(row["prefix"], [])
        out = run_cases(sp, args.timeout_bin, args.run_secs, exe, [], cases)
        for (subj, pos), (stdout, rc) in out.items():
            results["cases"][f"{row['prefix']}\t{subj}\t{pos}"] = {"stdout": stdout, "rc": rc}
    results["spawns"] = sp.summary()
    results["n_patterns"] = len(rows)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(results["spawns"], indent=1))

def cmd_batched(args):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import dispatch_gen
    rows = read_manifest(args.pool)
    if args.limit:
        rows = rows[:args.limit]
    cases_by_prefix = read_cases(args.pool)
    sp = Spawner()
    workdir = args.workdir or "/tmp/tt4m_batched"
    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    gencflags = args.gencflags.split()
    N = args.batch_size
    batches = [rows[i:i+N] for i in range(0, len(rows), N)]
    results = {"cases": {}, "compile_failures": [], "batch_size": N, "n_batches": len(batches)}
    for bi, batch in enumerate(batches):
        bdir = os.path.join(workdir, f"batch{bi:04d}")
        os.makedirs(bdir, exist_ok=True)
        member_srcs = []
        prefixes = []
        pcrec_ok = True
        for row in batch:
            gen_c = os.path.join(bdir, f"{row['prefix']}.c")
            r = sp.run("pcrec", pcrec_argv(args.pcrec, row["prefix"], row, gen_c))
            if r.returncode != 0 or not os.path.exists(os.path.join(bdir, f"{row['prefix']}.h")):
                results["compile_failures"].append({"batch": bi, "prefix": row["prefix"], "stage": "pcrec", "err": r.stderr})
                pcrec_ok = False
                continue
            member_srcs.append(gen_c)
            prefixes.append(row["prefix"])
        if not prefixes:
            continue
        drv = os.path.join(bdir, "dispatch.c")
        argv_save = sys.argv
        try:
            sys.argv = ["dispatch_gen.py"] + prefixes
            import io
            buf = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = buf
            try:
                dispatch_gen.main()
            finally:
                sys.stdout = old_stdout
            with open(drv, "w") as f:
                f.write(buf.getvalue())
        finally:
            sys.argv = argv_save
        exe = os.path.join(bdir, "t")
        # Shape L: ONE gcc invocation, N+1 separate .c source arguments
        # (dispatch.c + each member's gen.c) -- each its own translation
        # unit by construction (gcc still preprocesses/compiles each .c
        # file independently), avoiding the PCREC_FEATURE_SET/
        # PCREC_FEATURE_MODULES TU-concatenation collision by never
        # concatenating source at all.
        r = sp.run("gcc", [args.cc] + gencflags + ["-I", bdir, "-o", exe, drv] + member_srcs)
        if r.returncode != 0:
            results["compile_failures"].append({"batch": bi, "stage": "gcc-link", "err": r.stderr, "members": prefixes})
            continue
        for idx, row in enumerate(batch):
            if row["prefix"] not in prefixes:
                continue
            cases = cases_by_prefix.get(row["prefix"], [])
            out = run_cases(sp, args.timeout_bin, args.run_secs, exe, [str(idx)], cases)
            for (subj, pos), (stdout, rc) in out.items():
                results["cases"][f"{row['prefix']}\t{subj}\t{pos}"] = {"stdout": stdout, "rc": rc}
    results["spawns"] = sp.summary()
    results["n_patterns"] = len(rows)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(results["spawns"], indent=1))

def _write_subpool(dst_pool, shard_rows, cases_by_prefix):
    os.makedirs(dst_pool, exist_ok=True)
    with open(os.path.join(dst_pool, "manifest.tsv"), "w") as f:
        f.write("prefix\tsource_file\tfeatures\tflags\tpattern\n")
        for row in shard_rows:
            f.write("\t".join([row["prefix"], row["source_file"], row["features"], row["flags"], row["pattern"]]) + "\n")
    with open(os.path.join(dst_pool, "cases.tsv"), "w") as f:
        for row in shard_rows:
            for subj, pos in cases_by_prefix.get(row["prefix"], []):
                f.write(f"{row['prefix']}\t{subj}\t{pos}\n")

def cmd_parallel(args):
    rows = read_manifest(args.pool)
    if args.limit:
        rows = rows[:args.limit]
    cases_by_prefix = read_cases(args.pool)
    N = args.batch_size
    P = args.procs
    batches = [rows[i:i + N] for i in range(0, len(rows), N)]
    # Shard BATCHES (not raw rows) round-robin across P workers, so worker
    # shard sizes stay even regardless of how N divides len(rows) -- a
    # trailing short batch cannot pile onto one worker.
    shards = [[] for _ in range(P)]
    for i, b in enumerate(batches):
        shards[i % P].extend(b)

    workdir = args.workdir or "/tmp/tt4m_parallel"
    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)

    script = os.path.abspath(__file__)
    procs = []
    worker_outs = []
    worker_shard_batches = []
    t0 = time.perf_counter()
    ru0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    for wi, shard_rows in enumerate(shards):
        if not shard_rows:
            continue
        n_shard_batches = sum(1 for i, b in enumerate(batches) if i % P == wi)
        worker_shard_batches.append(n_shard_batches)
        subpool = os.path.join(workdir, f"pool{wi}")
        _write_subpool(subpool, shard_rows, cases_by_prefix)
        wworkdir = os.path.join(workdir, f"work{wi}")
        wout = os.path.join(workdir, f"out{wi}.json")
        werr = os.path.join(workdir, f"err{wi}.log")
        worker_outs.append((wout, werr))
        cmd = [sys.executable, script, "batched",
               "--pool", subpool, "--pcrec", args.pcrec, "--cc", args.cc,
               "--timeout-bin", args.timeout_bin, "--gencflags", args.gencflags,
               "--run-secs", str(args.run_secs), "--batch-size", str(N),
               "--out", wout, "--workdir", wworkdir]
        with open(werr, "w") as ef:
            procs.append(subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=ef))
    rcs = [p.wait() for p in procs]
    t1 = time.perf_counter()
    ru1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    wall_elapsed = t1 - t0
    cpu_outer = (ru1.ru_utime - ru0.ru_utime) + (ru1.ru_stime - ru0.ru_stime)

    merged_cases = {}
    compile_failures = []
    agg_counts, agg_wall, agg_cpu = {}, {}, {}
    worker_summaries = []
    for wi, ((wout, werr), rc) in enumerate(zip(worker_outs, rcs)):
        entry = {"worker": wi, "rc": rc, "batches": worker_shard_batches[wi]}
        if rc != 0 or not os.path.exists(wout):
            with open(werr) as ef:
                entry["stderr_tail"] = ef.read()[-2000:]
            worker_summaries.append(entry)
            continue
        d = json.load(open(wout))
        merged_cases.update(d["cases"])
        compile_failures.extend(d.get("compile_failures", []))
        for k, v in d["spawns"]["counts"].items():
            agg_counts[k] = agg_counts.get(k, 0) + v
        for k, v in d["spawns"]["wall_by_kind"].items():
            agg_wall[k] = agg_wall.get(k, 0) + v
        for k, v in d["spawns"]["cpu_by_kind"].items():
            agg_cpu[k] = agg_cpu.get(k, 0) + v
        entry["spawns"] = d["spawns"]
        worker_summaries.append(entry)

    results = {
        "n": N, "procs": P,
        "n_batches": len(batches), "n_workers_used": len(worker_outs),
        "wall_elapsed": round(wall_elapsed, 4),
        "cpu_outer_rusage_children": round(cpu_outer, 4),
        "agg_counts": agg_counts,
        "agg_wall_by_kind": {k: round(v, 4) for k, v in agg_wall.items()},
        "agg_cpu_by_kind": {k: round(v, 4) for k, v in agg_cpu.items()},
        "agg_cpu_sum": round(sum(agg_cpu.values()), 4),
        "n_patterns": len(rows),
        "cases": merged_cases,
        "compile_failures": compile_failures,
        "worker_summaries": worker_summaries,
    }
    with open(args.out, "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps({k: v for k, v in results.items() if k not in ("cases",)}, indent=1))

def cmd_failure_iso(args):
    """Plants a syntax error in ONE batch member's gen.c COPY, measures
    shape L's all-or-nothing compile-failure cost, then measures the
    per-pattern fallback cost (baseline shape, same corrupted source dir
    so the planted error still fires for that one member and the OTHER
    N-1 members recompile individually) to recover the batch."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import dispatch_gen
    rows = read_manifest(args.pool)[:args.batch_size]
    workdir = args.workdir or "/tmp/tt4m_failiso"
    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    gencflags = args.gencflags.split()
    sp_batch = Spawner()
    bdir = os.path.join(workdir, "batch")
    os.makedirs(bdir, exist_ok=True)
    prefixes = []
    for i, row in enumerate(rows):
        gen_c = os.path.join(bdir, f"{row['prefix']}.c")
        r = sp_batch.run("pcrec", pcrec_argv(args.pcrec, row["prefix"], row, gen_c))
        if r.returncode != 0:
            print(f"skip {row['prefix']}: pcrec failed", file=sys.stderr)
            continue
        prefixes.append(row["prefix"])
        if i == 0:
            with open(gen_c, "a") as f:
                f.write("\nTHIS IS A PLANTED SYNTAX ERROR;\n")
    drv = os.path.join(bdir, "dispatch.c")
    argv_save = sys.argv
    import io
    try:
        sys.argv = ["dispatch_gen.py"] + prefixes
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            dispatch_gen.main()
        finally:
            sys.stdout = old_stdout
        with open(drv, "w") as f:
            f.write(buf.getvalue())
    finally:
        sys.argv = argv_save
    member_srcs = [os.path.join(bdir, f"{p}.c") for p in prefixes]
    exe = os.path.join(bdir, "t")
    r = sp_batch.run("gcc", [args.cc] + gencflags + ["-I", bdir, "-o", exe] + [drv] + member_srcs)
    batch_failed = (r.returncode != 0)

    # Fallback: recompile the OTHER (uncorrupted) N-1 members individually,
    # baseline shape, against the SAME (corrupted) source directory --
    # each member still has its OWN prefix from the batch above, so we
    # link each against tests/harness-style driver.c reproduction (the
    # dispatch driver with one prefix also works and needs no new file).
    sp_fallback = Spawner()
    fallback_results = []
    for row in rows:
        if row["prefix"] not in prefixes:
            continue
        gen_c = os.path.join(bdir, f"{row['prefix']}.c")
        if row["prefix"] == prefixes[0]:
            # the corrupted member: recompiling it alone still fails --
            # this is the one whose failure the batch correctly attributed
            drv1 = os.path.join(bdir, f"drv_{row['prefix']}.c")
            argv_save = sys.argv
            try:
                sys.argv = ["dispatch_gen.py", row["prefix"]]
                buf = io.StringIO(); old = sys.stdout; sys.stdout = buf
                try:
                    dispatch_gen.main()
                finally:
                    sys.stdout = old
                with open(drv1, "w") as f:
                    f.write(buf.getvalue())
            finally:
                sys.argv = argv_save
            exe1 = os.path.join(bdir, f"t_{row['prefix']}")
            r = sp_fallback.run("gcc", [args.cc] + gencflags + ["-I", bdir, "-o", exe1, drv1, gen_c])
            fallback_results.append({"prefix": row["prefix"], "rc": r.returncode, "expected_fail": True})
            continue
        drv1 = os.path.join(bdir, f"drv_{row['prefix']}.c")
        argv_save = sys.argv
        try:
            sys.argv = ["dispatch_gen.py", row["prefix"]]
            buf = io.StringIO(); old = sys.stdout; sys.stdout = buf
            try:
                dispatch_gen.main()
            finally:
                sys.stdout = old
            with open(drv1, "w") as f:
                f.write(buf.getvalue())
        finally:
            sys.argv = argv_save
        exe1 = os.path.join(bdir, f"t_{row['prefix']}")
        r = sp_fallback.run("gcc", [args.cc] + gencflags + ["-I", bdir, "-o", exe1, drv1, gen_c])
        fallback_results.append({"prefix": row["prefix"], "rc": r.returncode, "expected_fail": False})

    results = {
        "batch_size": len(prefixes),
        "batch_link_failed": batch_failed,
        "batch_spawns": sp_batch.summary(),
        "fallback_spawns": sp_fallback.summary(),
        "fallback_results": fallback_results,
    }
    with open(args.out, "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(results, indent=1))

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    common = dict(
        pool=("--pool", dict(required=True)),
        pcrec=("--pcrec", dict(required=True)),
        cc=("--cc", dict(default="gcc-16")),
        timeout_bin=("--timeout-bin", dict(default="timeout")),
        gencflags=("--gencflags", dict(default="-O1 -std=gnu11 -Wall -Wextra -Werror")),
        driver=("--driver", dict(default=None)),
        run_secs=("--run-secs", dict(type=int, default=10)),
        out=("--out", dict(required=True)),
        workdir=("--workdir", dict(default=None)),
        limit=("--limit", dict(type=int, default=None)),
    )
    def add_common(p, keys):
        for k in keys:
            flag, kw = common[k]
            p.add_argument(flag, **kw)

    p = sub.add_parser("baseline")
    add_common(p, ["pool", "pcrec", "cc", "timeout_bin", "gencflags", "driver", "run_secs", "out", "workdir", "limit"])
    p.set_defaults(func=cmd_baseline)

    p = sub.add_parser("batched")
    add_common(p, ["pool", "pcrec", "cc", "timeout_bin", "gencflags", "run_secs", "out", "workdir", "limit"])
    p.add_argument("--batch-size", type=int, required=True)
    p.set_defaults(func=cmd_batched)

    p = sub.add_parser("parallel")
    add_common(p, ["pool", "pcrec", "cc", "timeout_bin", "gencflags", "run_secs", "out", "workdir", "limit"])
    p.add_argument("--batch-size", type=int, required=True)
    p.add_argument("--procs", type=int, required=True)
    p.set_defaults(func=cmd_parallel)

    p = sub.add_parser("failure-iso")
    add_common(p, ["pool", "pcrec", "cc", "gencflags", "out", "workdir"])
    p.add_argument("--batch-size", type=int, required=True)
    p.set_defaults(func=cmd_failure_iso)

    args = ap.parse_args()
    if args.cmd == "baseline" and not args.driver:
        print("baseline needs --driver (path to tests/harness/driver.c)", file=sys.stderr)
        sys.exit(2)
    args.func(args)

if __name__ == "__main__":
    main()
