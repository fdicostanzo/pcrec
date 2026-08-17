#!/usr/bin/env python3
"""hybrid_min.py -- RX_HYBRID_MIN crossover measurement (engine_m4.md S12
ASK-6, S6.2(b)).

THE QUESTION AS DESIGNED: is there a subject length n below which running
the DFA prefilter's two passes before the VM pass is slower than skipping
straight to the VM alone, so that an emitted `<prefix>_search` should carry
a runtime `if (n < RX_HYBRID_MIN)` branch selecting VM-only? S6.2(b)'s
prediction: "nonzero and small -- low hundreds of bytes", targeting bench
case (i)'s 60-byte regime (S12 ASK-6).

THE ANSWER THIS PROBE FINDS: subject length is not the variable that
governs the crossover. An exploratory sweep (recorded in the design note,
not reproduced by this script's default run) varied match OFFSET at FIXED
n and found hybrid's ns/call is flat across n (its cost is the two DFA
passes' own fixed call/setup overhead plus a memchr-speed skip, both
~length-invariant at these scales); VM-only's ns/call grows ROUGHLY
LINEARLY with the OFFSET of the first real match attempt, because its
naive `start=startpos; retry start++ on fail` outer loop (src/gen/emit_vm.c
~4728-4744, the `else` arm taken when no prefilter is attached) pays one
full computed-goto function CALL per candidate start position, not a
vectorized skip. So this script's canonical run sweeps OFFSET at fixed n
(the mechanistically correct axis) across three representative
capture-bearing patterns, and separately sweeps n directly at two FIXED
offsets (0 and "far") to confirm length-invariance holds.

WHY NO BRANCH-STYLE PLACEBO. The MRL clamp/placebo/denied three-arm design
(k23_impl, D51) exists because pruned/denied there differ by ONE conditional
branch inside an otherwise-identical function body, so a mis-attributed
code-layout shift on the SAME function is a first-order confound (the K24
incident: a +28% "regression" that was pure layout on a path never taken).
Hybrid-vs-VM-only here are two ENTIRELY DIFFERENT emitted functions (the
hybrid `<prefix>_search` calls a private forward+reverse DFA pair before the
VM; the VM-only one never emits that pair -- S6.1); there is no shared
function body for a never-taken branch to perturb, so a branch placebo has
no referent. The control used instead: THREE independent full-sweep
re-runs, fresh processes, one pinned core, checked for reproducibility
across runs (the same repetition discipline mrl_impl's throughput.txt
uses) -- and the crossover itself, being a sign flip that reproduces at the
same offset across all three runs and all three patterns, is a much
stronger signal than any percentage tolerance would be.

Run: python3 hybrid_min.py [--full]
Needs `build/pcrec` already built (asserted). Env: PCREC, CC (default gcc),
BENCH_CPU (default 3), REPS (best-of-N per timed point, default 9).
"""
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
PCREC = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))
CC = os.environ.get("CC", "gcc")
BENCH_CPU = os.environ.get("BENCH_CPU", "3")
REPS = int(os.environ.get("REPS", "9"))
BDRIVER = os.path.join(ROOT, "tests", "bench", "bdriver.c")

FULL = "--full" in sys.argv

# Representative capture-bearing patterns: case (i)'s own pattern (the named
# ASK-6 target), case (j)'s own pattern (the other bench capture-bearing
# shape), and k23_impl's short anchored two-group shape for a third body
# complexity.
PATTERNS = {
    "i_alt":     ("a(b|c)+d", b"abcbcd"),
    "j_bits":    ("([01]*)1([01]{8})", b"1" + b"01010101"),
    "kv_anchor": (r"(\d{3})-(\d{4})", b"123-4567"),
}

OFFSET_N = 300
OFFSETS = [0, 2, 4, 6, 8, 10, 12, 16, 24, 40, 80] if FULL else \
          [0, 2, 4, 6, 8, 10, 12, 16, 24, 40]

LENGTH_CHECK_LENGTHS = [60, 300, 1024, 4096] if not FULL else \
                        [60, 300, 1024, 4096, 8192]


def subject_offset(body, n, offset, fill_pre=b"z", fill_post=b"q"):
    assert offset + len(body) <= n, (offset, len(body), n)
    return fill_pre * offset + body + fill_post * (n - offset - len(body))


def build_variant(tmp, pat_key, pattern, extra_flags, tag):
    d = os.path.join(tmp, f"{pat_key}_{tag}")
    os.makedirs(d, exist_ok=True)
    genc = os.path.join(d, "gen.c")
    cmd = [PCREC, "-p", "rx", "-o", genc] + extra_flags + ["--", pattern]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"pcrec build failed for {pat_key}/{tag}: {r.stderr}")
    binf = os.path.join(d, "bdriver")
    cc_cmd = [CC, "-O2", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
              "-I", d, "-o", binf, BDRIVER, genc]
    r = subprocess.run(cc_cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"gcc build failed for {pat_key}/{tag}: {r.stderr}")
    return binf


def run_timed(binf, subject_path, iters):
    cmd = ["taskset", "-c", BENCH_CPU, binf, subject_path, str(iters)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"bdriver failed: {r.stderr}")
    fields = dict(kv.split("=") for kv in r.stdout.strip().split())
    return float(fields["secs"]), int(fields["match"])


def best_of_n_ns_per_call(binf, subject_path, iters, reps, want_match):
    secs_list = []
    for _ in range(reps):
        secs, match = run_timed(binf, subject_path, iters)
        if match != want_match:
            raise RuntimeError(f"expected match={want_match} got {match} "
                                f"({binf}, {subject_path})")
        secs_list.append(secs)
    return (min(secs_list) / iters) * 1e9


def load_check():
    with open("/proc/loadavg") as f:
        return f.read().strip()


def offset_sweep(tmp, out):
    for pat_key, (pattern, body) in PATTERNS.items():
        hybrid_bin = build_variant(tmp, pat_key, pattern, [], "hybrid")
        vmonly_bin = build_variant(tmp, pat_key, pattern, ["-fno-prefilter"], "vmonly")
        out(f"# --- {pat_key} = {pattern!r} (body {len(body)} bytes), n={OFFSET_N} ---")
        out(f"# offset  hybrid_ns  vmonly_ns   delta_pct")
        for offset in OFFSETS:
            if offset + len(body) > OFFSET_N:
                continue
            subj = subject_offset(body, OFFSET_N, offset)
            p = os.path.join(tmp, f"{pat_key}_{offset}.bin")
            with open(p, "wb") as f:
                f.write(subj)
            iters = 300000
            nsh = best_of_n_ns_per_call(hybrid_bin, p, iters, REPS, 1)
            nsv = best_of_n_ns_per_call(vmonly_bin, p, iters, REPS, 1)
            delta = (nsh - nsv) / nsv * 100.0
            out(f"  {offset:6d}  {nsh:9.2f}  {nsv:9.2f}  {delta:+8.2f}")
        out("")


def length_invariance_check(tmp, out):
    out("# ---- length-invariance check: fixed offset, varying n ----")
    for pat_key, (pattern, body) in PATTERNS.items():
        hybrid_bin = build_variant(tmp, pat_key, pattern, [], "hybrid")
        vmonly_bin = build_variant(tmp, pat_key, pattern, ["-fno-prefilter"], "vmonly")
        for offset_label, offset_fn in (("offset=0", lambda n: 0),
                                         ("offset=far", lambda n: max(0, n - len(body) - 10))):
            out(f"# {pat_key} {offset_label}")
            for n in LENGTH_CHECK_LENGTHS:
                offset = offset_fn(n)
                if offset + len(body) > n:
                    continue
                subj = subject_offset(body, n, offset)
                p = os.path.join(tmp, f"{pat_key}_{offset_label}_{n}.bin")
                with open(p, "wb") as f:
                    f.write(subj)
                iters = max(2000, min(500000, int(3e8 / max(n, 1))))
                nsh = best_of_n_ns_per_call(hybrid_bin, p, iters, REPS, 1)
                nsv = best_of_n_ns_per_call(vmonly_bin, p, iters, REPS, 1)
                delta = (nsh - nsv) / nsv * 100.0
                out(f"    n={n:6d}  offset={offset:6d}  hybrid={nsh:9.2f}  vmonly={nsv:9.2f}  delta={delta:+8.2f}")
        out("")


def main():
    if not os.path.isfile(PCREC):
        print(f"hybrid_min.py: {PCREC} not built", file=sys.stderr)
        return 2
    lines = []
    def out(s=""):
        lines.append(s)
        print(s)

    out("# RX_HYBRID_MIN crossover sweep (engine_m4.md S12 ASK-6)")
    out(f"# date: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    out(f"# repo: {subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()}")
    out(f"# pcrec: {PCREC}")
    gccver = subprocess.run([CC, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    out(f"# gcc: {gccver}")
    out(f"# pinning: taskset -c {BENCH_CPU}")
    out(f"# reps: {REPS} per point, best-of-N")
    out(f"# metric: ns/call, min over {REPS} reps (best-of-N: minimum is least contaminated on a shared box)")
    out("#")

    for run_idx in (1, 2, 3):
        out(f"# ================ RUN {run_idx}, load(pre)={load_check()} ================")
        with tempfile.TemporaryDirectory() as tmp:
            offset_sweep(tmp, out)
        out("")

    out("# ================ length-invariance check (run once) ================")
    with tempfile.TemporaryDirectory() as tmp:
        length_invariance_check(tmp, out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
