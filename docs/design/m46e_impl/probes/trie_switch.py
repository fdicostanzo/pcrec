#!/usr/bin/env python3
"""trie_switch.py -- candidate-benefit measurement for the VM's trie-factored
first-byte switch (engine_m4.md S2.2 item 4, S6.4's last row).

THE PROPOSAL: emit_vm.c's vm_alt() (src/gen/emit_vm.c:1783) emits an N-branch
alternation as a chain of N-1 RX_PUSH + goto, tried in preference order --
the analogous DFA/NFA construction (src/ir/nfa.c's M2.8 trie, "the D9
machinery") already factors alternations with disjoint prefixes into a
first-byte dispatch with no such chain, for the DFA path. The ASK is whether
the VM's OWN alternation emission should do the same thing where branches are
pairwise-disjoint on their first byte, emitting a switch with NO pushes at
all instead of a push-per-untried-branch chain.

Two things this probe measures, per the brief's bar ("measure the candidate
benefit FIRST: what fraction of the corpus/bench shapes would take the
factored path, and what it saves on at least one real shape"):

1. CANDIDATE FRACTION: corpus_scan() below (a static, non-timed survey) --
   what fraction of the .rxt corpus's patterns are CAPTURE-BEARING (so they
   are VM-forced, D42.1, and could reach vm_alt's chain at all -- a
   capture-free alternation already gets M2.8's trie at the DFA level and
   would see NO benefit from a VM-side switch) AND contain a plain
   (non-`(?:`) top-level alternation group AND have literal branches that are
   pairwise disjoint on their first byte (the same eligibility trie_key()
   checks, approximated on literal text since this probe has no AST access).

2. MEASURED SAVINGS ON A REAL SHAPE: the direct cost of vm_alt's chain,
   isolated by holding the SUBJECT fixed and moving which alternation BRANCH
   matches -- from the first branch (0 pushes needed, the chain's best case)
   to the last of N (N-1 pushes/pops needed, the chain's worst case). A
   first-byte switch would collapse every branch position to the SAME cost
   (the first-branch number), so branch_position_cost() below both measures
   today's chain overhead AND estimates the switch's payoff as (worst branch
   cost - first branch cost).

Run: python3 trie_switch.py
Needs `build/pcrec`. Env: PCREC, CC, BENCH_CPU (default 3), REPS (default 9).
"""
import glob
import os
import re
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


def has_capture(p):
    """Rough scan: a '(' not immediately followed by '?' is capturing.
    Ignores escaped parens/backslash-parity edge cases -- a survey
    approximation, not a parser."""
    i = 0
    while i < len(p):
        c = p[i]
        if c == "\\":
            i += 2
            continue
        if c == "(":
            if i + 1 < len(p) and p[i + 1] == "?":
                i += 1
                continue
            return True
        i += 1
    return False


ALT_RE = re.compile(r"\(([^()?][^()]*(?:\|[^()]*)+)\)")


def corpus_scan():
    files = glob.glob(os.path.join(ROOT, "tests", "*", "*.rxt"))
    patterns = []
    for fn in files:
        with open(fn, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")
                if line.startswith("pattern "):
                    patterns.append(line[len("pattern "):])

    captured = [p for p in patterns if has_capture(p)]
    has_alt = 0
    disjoint = 0
    examples = []
    for p in captured:
        m = ALT_RE.search(p)
        if not m:
            continue
        has_alt += 1
        branches = m.group(1).split("|")
        firsts, ok = [], True
        for b in branches:
            b = b.strip()
            if not b or b[0] in "[\\.^$(){}*+?":
                ok = False
                break
            firsts.append(b[0])
        if ok and len(set(firsts)) == len(firsts) and len(firsts) >= 2:
            disjoint += 1
            if len(examples) < 15:
                examples.append(p)

    return {
        "total_patterns": len(patterns),
        "capture_bearing": len(captured),
        "capture_bearing_with_plain_alt": has_alt,
        "disjoint_first_byte_candidates": disjoint,
        "examples": examples,
    }


def build_variant(tmp, pat_key, pattern, tag):
    d = os.path.join(tmp, f"{pat_key}_{tag}")
    os.makedirs(d, exist_ok=True)
    genc = os.path.join(d, "gen.c")
    cmd = [PCREC, "-p", "rx", "-o", genc, "--", pattern]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"pcrec build failed: {r.stderr}")
    binf = os.path.join(d, "bdriver")
    cc_cmd = [CC, "-O2", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
              "-I", d, "-o", binf, BDRIVER, genc]
    r = subprocess.run(cc_cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"gcc build failed: {r.stderr}")
    return binf


def run_timed(binf, subject_path, iters):
    cmd = ["taskset", "-c", BENCH_CPU, binf, subject_path, str(iters)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"bdriver failed: {r.stderr}")
    fields = dict(kv.split("=") for kv in r.stdout.strip().split())
    return float(fields["secs"]), int(fields["match"])


def best_of_n_ns_per_call(binf, subject_path, iters, reps):
    secs_list = []
    for _ in range(reps):
        secs, match = run_timed(binf, subject_path, iters)
        if match != 1:
            raise RuntimeError(f"no match ({binf}, {subject_path})")
        secs_list.append(secs)
    return (min(secs_list) / iters) * 1e9


def load_check():
    with open("/proc/loadavg") as f:
        return f.read().strip()


# Two shapes: the bench case (c) alternation words (5-way, all disjoint first
# letters) rebuilt CAPTURE-BEARING (case (c) itself is pinned --no-captures
# and never reaches vm_alt at all -- this IS the point being measured: what
# the SAME shape costs once it's VM-forced), and a shorter 3-way HTTP-method-
# style dispatch, a very common disjoint-alternation-with-capture idiom.
SHAPES = {
    "words5": ("(alpha|beta|gamma|delta|epsilon)",
               ["alpha", "beta", "gamma", "delta", "epsilon"]),
    "http3":  ("(GET|POST|PUT) /", ["GET /", "POST /", "PUT /"]),
}


def branch_position_cost(tmp, out):
    for shape_key, (pattern, words) in SHAPES.items():
        binf = build_variant(tmp, shape_key, pattern, "default")
        out(f"# --- {shape_key} = {pattern!r} ---")
        out(f"# branch_idx  word          ns/call")
        n = 200
        results = []
        for idx, word in enumerate(words):
            pad = n - len(word)
            subj = b"z" * pad + word.encode()
            p = os.path.join(tmp, f"{shape_key}_{idx}.bin")
            with open(p, "wb") as f:
                f.write(subj)
            ns = best_of_n_ns_per_call(binf, p, 500000, REPS)
            results.append((idx, word, ns))
            out(f"  {idx:10d}  {word:12s}  {ns:8.2f}")
        first_ns = results[0][2]
        last_ns = results[-1][2]
        out(f"# chain overhead (last - first) = {last_ns - first_ns:+.2f} ns "
            f"({(last_ns - first_ns) / first_ns * 100:+.2f}% of first-branch cost) "
            f"-- upper bound on a first-byte switch's payoff for this shape")
        out("")


def main():
    if not os.path.isfile(PCREC):
        print(f"trie_switch.py: {PCREC} not built", file=sys.stderr)
        return 2

    lines = []
    def out(s=""):
        lines.append(s)
        print(s)

    out("# Trie-factored VM alternation switch: candidate-benefit measurement")
    out("# (engine_m4.md S2.2 item 4 / S6.4)")
    out(f"# date: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    out(f"# repo: {subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()}")
    out(f"# pcrec: {PCREC}")
    out(f"# gcc: {subprocess.run([CC, '--version'], capture_output=True, text=True).stdout.splitlines()[0]}")
    out(f"# pinning: taskset -c {BENCH_CPU}")
    out(f"# reps: {REPS} per point, best-of-N")
    out("#")
    out("# ==== PART 1: corpus candidate-fraction survey (static, one pass) ====")
    scan = corpus_scan()
    out(f"# total 'pattern' lines in tests/*/*.rxt: {scan['total_patterns']}")
    out(f"# capture-bearing (VM-forced under default caps-on, D42.1): {scan['capture_bearing']}")
    out(f"# of those, containing a plain top-level alternation group: {scan['capture_bearing_with_plain_alt']}")
    out(f"# of those, heuristically first-byte-disjoint literal branches (trie-eligible shape): {scan['disjoint_first_byte_candidates']}")
    out(f"# fraction of ALL corpus patterns that are candidates: {scan['disjoint_first_byte_candidates']/scan['total_patterns']*100:.2f}%")
    out(f"# fraction of CAPTURE-BEARING corpus patterns that are candidates: {scan['disjoint_first_byte_candidates']/scan['capture_bearing']*100:.2f}%")
    out("# examples:")
    for e in scan["examples"]:
        out(f"#   {e}")
    out("#")
    out("# note: the two bench capture-bearing shapes (case j: '([01]*)1([01]{8})',")
    out("# DD-9's own capture-bearing floor) and case (c)'s own alternation (pinned")
    out("# --no-captures, so it never reaches vm_alt) are NEITHER a hit for this")
    out("# survey -- no shipped bench case currently exercises this path.")
    out("")

    out("# ==== PART 2: branch-position cost on real shapes, 3 independent runs ====")
    for run_idx in (1, 2, 3):
        out(f"# ---- run {run_idx}, load(pre)={load_check()} ----")
        with tempfile.TemporaryDirectory() as tmp:
            branch_position_cost(tmp, out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
