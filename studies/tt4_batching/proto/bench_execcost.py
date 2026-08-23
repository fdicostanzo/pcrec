#!/usr/bin/env python3
"""studies/tt4_batching/proto/bench_execcost.py — [TT-4.1] Stage A2 exec-
cost prototype cell (manager-requested addendum): for a fixed set of
patterns and their REAL cases, compares

  (i)  the harness's OWN shape: one `timeout RUN_SECS "$bdir/t" subj pos`
       spawn PER CASE, from a bash loop using command substitution --
       exactly tests/harness/run.sh:356's own shape, reproduced in a
       generated bash script (never editing run.sh itself);
  (ii) one process invocation PER PATTERN, reading ALL of that pattern's
       cases from stdin in a loop inside the same process (multidriver_gen.py
       -- a tiny purpose-built driver, never tests/harness/driver.c).

Both shapes exercise the SAME compiled matchers and the SAME real cases,
so any wall-time difference is exec/timeout/bash overhead, not matcher
work. 3 repeats, median reported, so [TT-4.2] can compare this
"exec-batching" lever against Stage B's gcc-batching lever on the same
footing.

Usage: bench_execcost.py --patterns POOLDIR --limit 16 --outdir DIR [--reps 3]
"""
import argparse
import os
import shutil
import statistics
import subprocess
import sys
import time

def read_manifest(path, limit):
    rows = []
    with open(path) as f:
        f.readline()
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 5:
                rows.append(parts)
    return rows[:limit] if limit else rows

def cases_for_pattern(source_file, pattern_text):
    import re
    PATTERN_RE = re.compile(r'^pattern (.*)$')
    M_RE = re.compile(r'^m\s+"(.*)"\s+(\d+)\s+(\d+)\s*$')
    N_RE = re.compile(r'^n\s+"(.*)"\s*$')
    MS_RE = re.compile(r'^ms\s+(\d+)\s+"(.*)"\s+(\d+)\s+(\d+)\s*$')
    NS_RE = re.compile(r'^ns\s+(\d+)\s+"(.*)"\s*$')
    cases = []
    in_block = False
    found = False
    with open(source_file, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            m = PATTERN_RE.match(line)
            if m:
                if found:
                    break
                in_block = (m.group(1) == pattern_text)
                if in_block:
                    found = True
                continue
            if not in_block:
                continue
            m = M_RE.match(line)
            if m: cases.append((m.group(1), "0")); continue
            m = N_RE.match(line)
            if m: cases.append((m.group(1), "0")); continue
            m = MS_RE.match(line)
            if m: cases.append((m.group(2), m.group(1))); continue
            m = NS_RE.match(line)
            if m: cases.append((m.group(2), m.group(1))); continue
    return cases

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", required=True)
    ap.add_argument("--limit", type=int, default=16)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--run-secs", default="10")
    ap.add_argument("--timeout-bins", default="/usr/bin/timeout",
                     help="comma-separated list of timeout binaries to run shape (i) "
                          "against, one full measurement per binary -- e.g. "
                          "/usr/bin/timeout,/usr/bin/gnutimeout to compare uutils vs "
                          "GNU coreutils' timeout on the SAME harness shape")
    args = ap.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    manifest = os.path.join(args.patterns, "manifest.tsv")
    rows = read_manifest(manifest, args.limit)
    gencflags = "-O1 -std=gnu11 -Wall -Wextra -Werror".split()

    shutil.rmtree(args.outdir, ignore_errors=True)
    os.makedirs(args.outdir, exist_ok=True)

    all_cases = []  # (prefix, subj, pos)
    for prefix, source_file, features, flags, pattern in rows:
        cs = cases_for_pattern(source_file, pattern)
        for subj, pos in cs:
            all_cases.append((prefix, subj, pos))
    print(f"{len(rows)} patterns, {len(all_cases)} total cases", file=sys.stderr)

    # Build shape-(i) binaries: one harness-equivalent single-pattern driver
    # per pattern (dispatch_gen.py with index 0 only -- byte-identical
    # protocol to tests/harness/driver.c, verified earlier in Stage B).
    harness_bins = {}
    for prefix, source_file, features, flags, pattern in rows:
        drv = os.path.join(args.outdir, f"{prefix}_drv.c")
        subprocess.run([sys.executable, os.path.join(script_dir, "dispatch_gen.py"), prefix],
                        stdout=open(drv, "w"), check=True)
        exe = os.path.join(args.outdir, f"{prefix}_t")
        src = os.path.join(args.patterns, f"{prefix}.c")
        r = subprocess.run(["gcc"] + gencflags + ["-I", args.patterns, "-o", exe, drv, src],
                            capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAILED to build harness-shape binary for {prefix}: {r.stderr}", file=sys.stderr)
            sys.exit(1)
        harness_bins[prefix] = exe

    # Build shape-(ii) binaries: one multi-case driver per pattern.
    multi_bins = {}
    for prefix, source_file, features, flags, pattern in rows:
        drv = os.path.join(args.outdir, f"{prefix}_multi.c")
        with open(drv, "w") as f:
            subprocess.run([sys.executable, os.path.join(script_dir, "multidriver_gen.py"), prefix],
                            stdout=f, check=True)
        exe = os.path.join(args.outdir, f"{prefix}_tmulti")
        src = os.path.join(args.patterns, f"{prefix}.c")
        r = subprocess.run(["gcc"] + gencflags + ["-I", args.patterns, "-o", exe, drv, src],
                            capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAILED to build multi-case binary for {prefix}: {r.stderr}", file=sys.stderr)
            sys.exit(1)
        multi_bins[prefix] = exe

    # ---- shape (i): harness's own per-case exec shape, via a generated
    # bash script reproducing run.sh:356's exact line
    #   out="$(timeout "$RUN_SECS" "$bdir/t" "$subj" "$pos")"
    # for every case, in order. Run once per --timeout-bins entry (default:
    # just the box's real /usr/bin/timeout, i.e. run.sh's own actual
    # behaviour) -- a manager finding (2026-08-23) is that on THIS box
    # /usr/bin/timeout is uutils coreutils 0.8.0, measured costing ~108ms
    # of pure WALL per call at 0 CPU (50x `timeout 5 true` probe), vs. GNU
    # coreutils' timeout (installed here as /usr/bin/gnutimeout, 9.7) at
    # ~4ms/call -- so this comparison isolates how much of shape (i)'s own
    # cost is THIS SPECIFIC BINARY CHOICE rather than fork/exec/subshell
    # overhead in general.
    med_i_by_bin = {}
    for timeout_bin in args.timeout_bins.split(","):
        label = os.path.basename(timeout_bin)
        bash_lines = ["#!/usr/bin/env bash", "set -u"]
        for prefix, subj, pos in all_cases:
            exe = harness_bins[prefix]
            # subj is already .rxt-escaped text; pass through double-quoted
            # exactly as run.sh does (single-quoting the shell script's own
            # literal so subj's backslash escapes reach the C decoder
            # unmolested, matching run.sh's own quoting of $subj).
            safe_subj = subj.replace("'", "'\\''")
            bash_lines.append(f"out=\"$({timeout_bin} {args.run_secs} '{exe}' '{safe_subj}' '{pos}')\"")
        bash_script = os.path.join(args.outdir, f"shape_i_{label}.sh")
        with open(bash_script, "w") as f:
            f.write("\n".join(bash_lines) + "\n")

        walls_i = []
        for rep in range(args.reps):
            t0 = time.monotonic()
            subprocess.run(["bash", bash_script], check=True)
            t1 = time.monotonic()
            walls_i.append(t1 - t0)
        med_i = statistics.median(walls_i)
        min_i = min(walls_i)
        med_i_by_bin[label] = med_i
        print(f"shape=(i) harness-per-case-exec [{label}]  median={med_i:.4f}s min={min_i:.4f}s reps={walls_i}")
    # Use the FIRST --timeout-bins entry (the box's real /usr/bin/timeout by
    # default, matching run.sh's own actual behaviour) as "the" shape-(i)
    # number for the final speed-up line below, if the caller wants a
    # single headline ratio.
    med_i = next(iter(med_i_by_bin.values()))

    # ---- shape (ii): one process per PATTERN, all its cases via stdin.
    cases_by_prefix = {}
    for prefix, subj, pos in all_cases:
        cases_by_prefix.setdefault(prefix, []).append((subj, pos))

    walls_ii = []
    for rep in range(args.reps):
        t0 = time.monotonic()
        for prefix, cs in cases_by_prefix.items():
            stdin_data = "".join(f"{subj}\t{pos}\n" for subj, pos in cs)
            subprocess.run([multi_bins[prefix]], input=stdin_data, text=True,
                            capture_output=True, check=False)
        t1 = time.monotonic()
        walls_ii.append(t1 - t0)
    med_ii = statistics.median(walls_ii)
    min_ii = min(walls_ii)
    print(f"shape=(ii) one-process-per-pattern median={med_ii:.4f}s min={min_ii:.4f}s reps={walls_ii}")

    print(f"\nexec-batching speed-up (median): {med_i/med_ii:.2f}x "
          f"({len(all_cases)} cases across {len(rows)} patterns, "
          f"{len(all_cases)} spawns in shape (i) vs {len(rows)} in shape (ii))")

if __name__ == "__main__":
    main()
