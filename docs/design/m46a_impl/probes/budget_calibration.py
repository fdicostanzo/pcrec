#!/usr/bin/env python3
# docs/design/m46a_impl/probes/budget_calibration.py — [M4.6a]'s calibration
# sweep for the four runtime-bound defaults (engine_m4.md §4.6, extended;
# see the m46a_impl CLAUDE.md for why the extension is needed at all — §4.6
# as written names only the step budget).
#
# WHAT THIS MEASURES, and how, per bound:
#
#   step budget   (VM_DEFAULT_STEP_BUDGET)     — resumptions at rx_fail:
#   work budget   (VM_DEFAULT_WORK_BUDGET)     — units charged by RX_WORK
#   frame/trail   (VM_DEFAULT_BT_FRAMES/       — PEAK w->btn / w->trn during
#                  VM_DEFAULT_TRAIL_FRAMES)      one rx_search call
#
# all four read DIRECTLY off the real shipped counters (settlement 4, D49 —
# RX_ERR_WORK is on main), not a proxy. This is a GENERIC instrument: it
# patches the four textually-uniform sites every VM artifact emits
# (RX_PUSH's `w->btn++;`, RX_TRAIL's `w->trn++;`, rx_fail:'s
# `if (--w->budget < 0)` line, RX_WORK's `w->work -= ...;` line) rather than
# a shape-specific sed pattern, because the corpus is ~600 distinct patterns
# of unknown shape, not a handful of hand-picked ones. Each site is verified
# to match EXACTLY ONCE per VM artifact before anything is trusted (the
# check-design lesson this project keeps re-learning: a probe that patches
# nothing must not report a silent zero as a real measurement) — see
# `assert_sites`.
#
# THREE LAYERS, because the corpus alone underrepresents what the defaults
# must hold against:
#
#   1. CORPUS+BENCH — every tests/**/*.rxt pattern (excluding known_fail/,
#      which is pathology by definition, D27's own K23 residing there) run
#      against its OWN subjects, plus the tests/bench throughput cases. This
#      is the literal reading of engine_m4.md §4.6. Its own finding: every
#      committed bench THROUGHPUT case compiles `--no-captures` (DD-9's own
#      choice, to isolate the DFA), so none of them touches the VM at all —
#      the bench matrix contributes ZERO signal to VM budget calibration
#      today. Recorded, not silently worked around.
#   2. SCALE — synthetic legitimate large-subject VM-forced probes on
#      representative rung shapes (cursor, frames-bounded, frames-unbounded,
#      revdet), because a correctness corpus is deliberately small and the
#      real question the work/step bounds answer ("how big an ordinary
#      single-pass match can this refuse before it must") only shows up at
#      scale. Anticipates [M4.6b]'s not-yet-landed capture-bearing bench
#      sibling `([01]*)1([01]{8})` at moderate N.
#   3. RATIO — re-anchors the k23_impl lane's retracted 5.24 proxy
#      work-per-step ratio (k23_design.md §12 item 5, R26 M2/E6) against the
#      REAL meter, on the exact shape/size the retracted number came from
#      (`(a{10,20}){10,50}` at 100 bytes, pre-MRL — MRL is [M4.6d], not
#      landed on this branch). This shape is the K23 PATHOLOGY itself and is
#      explicitly NOT a legitimate-workload input to the default (excluded
#      from layers 1/2's maxima); it is measured anyway because the ratio is
#      independently owed as an archived data point.
#
# Usage: budget_calibration.py [--full]
#   --full broadens the SCALE layer's size ladder (slower).
# Env: PCREC (default build/pcrec relative to repo root), CC (default cc),
#      TIMEOUT (default 60, per compile/run subprocess)
#
# Output: TSV blocks to stdout, human-readable section headers, a final
# SUMMARY block with the four measured maxima and their provenance
# (pattern, subject size, layer). Exit 0 always (a measurement probe, not a
# gate — D18); exit 2 only on a broken instrument (no build, a site that
# fails to instrument, a non-vacuity check that comes back empty).

import base64
import os
import re
import subprocess
import sys
import tempfile
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
PCREC = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))
CC = os.environ.get("CC", "cc")
TIMEOUT = int(os.environ.get("TIMEOUT", "60"))

# Big enough not to truncate ANY legitimate corpus/bench/scale need, small
# enough to fit an 8 MB process stack with room to spare (20000*24 +
# 20000*16 = 800000 B for rx_work's two arrays alone). This is a MEASUREMENT
# ceiling, deliberately far above the 128 KB design ceiling D19 imposes on
# the SHIPPED default (src/gen/emit_vm.c:64-69) — the point is to observe
# the true unclamped need, then compare it against that ceiling separately.
BIG_FRAMES = 20000
BIG_STEP = 10**9
BIG_WORK = 10**11


def eprint(*a):
    print(*a, file=sys.stderr)


def require_build():
    if not (os.path.isfile(PCREC) and os.access(PCREC, os.X_OK)):
        eprint(f"no pcrec at {PCREC} -- run make first")
        sys.exit(2)


# ---------------------------------------------------------------------------
# .rxt corpus extraction — the same escape table docs/testing.md defines,
# reused rather than re-invented (tests/harness/driver.c decodes the same
# six escapes at match time).
# ---------------------------------------------------------------------------

ESCAPES = {'"': '"', "\\": "\\", "n": "\n", "t": "\t", "r": "\r",
           "f": "\f", "v": "\v"}


def decode_subject(s):
    out = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c != "\\":
            out.append(ord(c))
            i += 1
            continue
        i += 1
        e = s[i]
        if e == "x":
            out.append(int(s[i + 1:i + 3], 16))
            i += 3
            continue
        out.append(ord(ESCAPES[e]))
        i += 1
    return bytes(out)


LINE_M = re.compile(r'^m "((?:[^"\\]|\\.)*)" (\d+) (\d+)\s*$')
LINE_N = re.compile(r'^n "((?:[^"\\]|\\.)*)"\s*$')
LINE_MS = re.compile(r'^ms (\d+) "((?:[^"\\]|\\.)*)" (\d+) (\d+)\s*$')
LINE_NS = re.compile(r'^ns (\d+) "((?:[^"\\]|\\.)*)"\s*$')


def parse_rxt(path):
    """Returns [(pattern, flags, features, [(startpos, subject_bytes), ...])]
    for every non-perr block in the file."""
    blocks = []
    pat = None
    flags = ""
    features = None
    subs = []

    def flush():
        if pat is not None and subs:
            blocks.append((pat, flags, features, list(subs)))

    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            if line.startswith("pattern "):
                flush()
                pat = line[len("pattern "):]
                flags = ""
                features = None
                subs = []
                continue
            if line.startswith("flags "):
                flags = line[len("flags "):].strip()
                continue
            if line.startswith("features "):
                features = line[len("features "):].strip()
                continue
            if line == "perr":
                pat = None  # no subjects; not a VM-budget input
                continue
            m = LINE_M.match(line)
            if m:
                subs.append((0, decode_subject(m.group(1))))
                continue
            m = LINE_N.match(line)
            if m:
                subs.append((0, decode_subject(m.group(1))))
                continue
            m = LINE_MS.match(line)
            if m:
                subs.append((int(m.group(1)), decode_subject(m.group(2))))
                continue
            m = LINE_NS.match(line)
            if m:
                subs.append((int(m.group(1)), decode_subject(m.group(2))))
                continue
            # g/gp/other directive lines: irrelevant to budget calibration.
    flush()
    return blocks


def collect_corpus():
    """Walks tests/**/*.rxt excluding known_fail/ (pathology by definition,
    not a legitimate workload) and reject/ (perr-only, no subjects)."""
    groups = {}  # (pattern, flags, features) -> list of (startpos, bytes)
    n_files = 0
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "tests")):
        dirnames[:] = [d for d in dirnames if d not in ("known_fail",)]
        if os.path.relpath(dirpath, ROOT).split(os.sep)[:2] == ["tests", "known_fail"]:
            continue
        for fn in filenames:
            if not fn.endswith(".rxt"):
                continue
            n_files += 1
            path = os.path.join(dirpath, fn)
            for pat, flags, features, subs in parse_rxt(path):
                key = (pat, flags, features)
                groups.setdefault(key, []).extend(subs)
    return groups, n_files


# ---------------------------------------------------------------------------
# Generic instrumentation. Four textually-uniform anchors, verified present
# exactly once each before anything downstream is trusted.
# ---------------------------------------------------------------------------

GLOBALS = (
    "static unsigned long long rxprobe_steps = 0, rxprobe_work = 0;\n"
    "static unsigned long long rxprobe_peak_btn = 0, rxprobe_peak_trn = 0;\n"
)

# Each anchor is matched as a STANDALONE LINE (any leading whitespace, an
# optional trailing backslash for macro-body continuations, trailing
# whitespace ignored) so the patch survives exact-spacing differences
# between emitter versions rather than depending on a byte-for-byte
# transcription of today's src/gen/emit_vm.c output. The extra statement is
# APPENDED before any trailing `\`, so a macro-continuation line stays a
# valid continuation.
PATCH_STMTS = [
    ("push", "w->btn++;",
     "if (w->btn > rxprobe_peak_btn) rxprobe_peak_btn = w->btn;"),
    ("trail", "w->trn++;",
     "if (w->trn > rxprobe_peak_trn) rxprobe_peak_trn = w->trn;"),
    ("step", "if (--w->budget < 0) return RX_R_STEPS;",
     "rxprobe_steps++;"),  # order-irrelevant: a local counter, not a check
    ("work", "w->work -= (long long)nw_;",
     "rxprobe_work += (unsigned long long)nw_;"),
]


def patch_line(src, stmt, extra):
    pat = re.compile(r"^([ \t]*)" + re.escape(stmt) + r"([ \t]*\\?)[ \t]*$", re.M)
    matches = list(pat.finditer(src))
    if len(matches) != 1:
        return src, len(matches)
    m = matches[0]
    indent, tail = m.group(1), m.group(2)
    repl = f"{indent}{stmt} {extra}{tail}"
    return src[:m.start()] + repl + src[m.end():], 1


def instrument(src):
    """Returns (patched_src, sites_dict) or (None, sites_dict) if any of the
    four anchors did not match exactly once (a DFA-only artifact legitimately
    matches none of them — that is sites == {0,0,0,0}, a valid all-zero
    result, distinguished from a broken instrument by is_vm below)."""
    sites = {}
    out = src
    for name, stmt, extra in PATCH_STMTS:
        out2, c = patch_line(out, stmt, extra)
        sites[name] = c
        if c == 1:
            out = out2
        elif c > 1:
            return None, sites
    return GLOBALS + out, sites


def is_vm(src):
    return src.count("\nrx_fail: __attribute__((unused));\n") == 1


DRIVER_TMPL = r"""
#include <stdio.h>
#include <string.h>
#include "gen.c"

struct rxprobe_case { const unsigned char *s; size_t n; size_t startpos; };

static const unsigned char CASE_DATA[] = { %(bytes)s };

static struct rxprobe_case CASES[] = { %(cases)s };
#define NCASES ((int)(sizeof(CASES) / sizeof(CASES[0])))

int main(void) {
    for (int i = 0; i < NCASES; i++) {
        rxprobe_steps = 0; rxprobe_work = 0;
        rxprobe_peak_btn = 0; rxprobe_peak_trn = 0;
        ptrdiff_t caps[RX_NCAPS][2];
        int rc = rx_search(CASES[i].s, CASES[i].n, CASES[i].startpos, caps);
        const char *verdict = rc == 1 ? "match" : rc == 0 ? "nomatch"
                             : rc == RX_ERR_STEPS ? "GAVE-UP-STEPS"
                             : rc == RX_ERR_FRAMES ? "GAVE-UP-FRAMES"
                             : rc == RX_ERR_WORK ? "GAVE-UP-WORK" : "?";
        printf("CASE %%d %%s %%zu %%llu %%llu %%llu %%llu\n", i, verdict,
               CASES[i].n, rxprobe_steps, rxprobe_work,
               rxprobe_peak_btn, rxprobe_peak_trn);
    }
    return 0;
}
"""


def build_driver_c(subjects):
    """subjects: list of (startpos, bytes). Returns C source embedding every
    subject as a byte blob with explicit length (never strlen — subjects may
    contain NUL, docs/testing.md)."""
    blob = bytearray()
    offsets = []
    for startpos, b in subjects:
        offsets.append((len(blob), len(b), startpos))
        blob += b
    byte_str = ", ".join(str(b) for b in blob) if blob else "0"
    cases = ", ".join(
        "{ CASE_DATA + %d, %d, %d }" % (off, n, sp) for off, n, sp in offsets
    )
    return DRIVER_TMPL % {"bytes": byte_str, "cases": cases}


def run_group(pattern, flags, features, subjects, frame_cap, step_budget,
              work_budget, engine=None, label=""):
    """Compiles `pattern` once, instruments it, runs every subject, returns
    a list of dicts (or None on REFUSED/instrumentation failure -- logged to
    stderr, never silently dropped)."""
    with tempfile.TemporaryDirectory(prefix="m46a.") as d:
        args = [PCREC, "-p", "rx", "--backtrack-frames=%d" % frame_cap,
                "--step-budget=%d" % step_budget,
                "--work-budget=%d" % work_budget]
        if "i" in flags:
            args.append("-i")
        if features:
            args += ["--features", features]
        if engine:
            args.append("--engine=%s" % engine)
        genc = os.path.join(d, "gen.c")
        args += ["-o", genc, "--", pattern]
        try:
            r = subprocess.run(args, timeout=TIMEOUT, capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            eprint(f"[{label}] COMPILE TIMEOUT: {pattern!r}")
            return None
        if r.returncode != 0:
            eprint(f"[{label}] REFUSED (exit {r.returncode}): {pattern!r} :: {r.stderr.strip()[:160]}")
            return None

        src = open(genc, encoding="utf-8").read()
        if not is_vm(src):
            return []  # DFA-only: a real zero-need answer, not a probe gap

        patched, sites = instrument(src)
        if patched is None:
            eprint(f"[{label}] INSTRUMENTATION FAILED sites={sites}: {pattern!r}")
            return None
        if any(v != 1 for v in sites.values()):
            eprint(f"[{label}] INSTRUMENTATION SITES != 1 ({sites}): {pattern!r}")
            return None
        open(genc, "w", encoding="utf-8").write(patched)

        drv = os.path.join(d, "driver.c")
        open(drv, "w", encoding="utf-8").write(build_driver_c(subjects))
        exe = os.path.join(d, "drv")
        try:
            r = subprocess.run([CC, "-O2", "-I", d, "-o", exe, drv],
                                timeout=TIMEOUT, capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            eprint(f"[{label}] CC TIMEOUT: {pattern!r}")
            return None
        if r.returncode != 0:
            eprint(f"[{label}] CC FAILED: {pattern!r} :: {r.stderr.strip()[:200]}")
            return None

        try:
            r = subprocess.run([exe], timeout=TIMEOUT, capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            eprint(f"[{label}] RUN TIMEOUT: {pattern!r} (a finding, not re-run longer)")
            return None
        if r.returncode != 0:
            eprint(f"[{label}] RUN FAILED (exit {r.returncode}): {pattern!r} :: {r.stderr.strip()[:200]}")
            return None

        rows = []
        for line in r.stdout.splitlines():
            if not line.startswith("CASE "):
                continue
            _, idx, verdict, n, steps, work, btn, trn = line.split()
            rows.append(dict(pattern=pattern, verdict=verdict, n=int(n),
                              steps=int(steps), work=int(work),
                              peak_btn=int(btn), peak_trn=int(trn)))
        return rows


# ---------------------------------------------------------------------------
# Layer 1: corpus + bench
# ---------------------------------------------------------------------------

def layer1_corpus():
    print("\n== LAYER 1: corpus (tests/**/*.rxt, excluding known_fail/) ==")
    groups, n_files = collect_corpus()
    print(f"files scanned: {n_files}   distinct (pattern,flags,features) groups: {len(groups)}")
    all_rows = []
    n_vm = n_dfa = n_refused = 0
    for (pat, flags, features), subs in groups.items():
        rows = run_group(pat, flags, features, subs, BIG_FRAMES, BIG_STEP,
                          BIG_WORK, label="corpus")
        if rows is None:
            n_refused += 1
            continue
        if not rows:
            n_dfa += 1
            continue
        n_vm += 1
        all_rows.extend(rows)
    print(f"groups: vm={n_vm} dfa-only={n_dfa} refused/instr-failed={n_refused}")
    bad = [r for r in all_rows if r["verdict"].startswith("GAVE-UP")]
    if bad:
        print(f"** {len(bad)} corpus cases GAVE UP even at the raised measurement "
              f"ceiling (frames={BIG_FRAMES}, step={BIG_STEP}, work={BIG_WORK}) -- "
              f"this is either a real pathology hiding in the corpus or a probe "
              f"defect; listing up to 5:")
        for r in bad[:5]:
            print("   ", r)
    return all_rows


BENCH_CASES = [
    # (label, pattern, extra pcrec flags, subject-builder(n)->bytes, sizes)
    ("bench-a-needle", "needleXYZW", [], lambda n: (b"x" * (n - 20) + b"needleXYZW" + b"x" * 10), [8_000_000]),
    ("bench-b-allastar", "a*b", [], lambda n: b"a" * n, [8_000_000]),
    ("bench-c-altd-NOCAP", "a(b|c)+d", ["--no-captures"], lambda n: (b"abcbcbcbc" * (n // 9)), [8_000_000]),
    ("bench-c-altd-CAP", "a(b|c)+d", [], lambda n: (b"abcbcbcbc" * (n // 9)), [200_000]),
]


def layer1_bench(full):
    print("\n== LAYER 1b: tests/bench throughput matrix (as committed) ==")
    print("NOTE: every committed THROUGHPUT case compiles --no-captures "
          "(DD-9's choice), so the DFA answers and the VM is never entered -- "
          "recorded as ZERO VM-budget signal from the shipped bench matrix. "
          "The '-CAP' row re-runs case (c)'s pattern WITH captures forced, as "
          "the honest stand-in for what a capture-bearing throughput case "
          "would show (anticipating [M4.6b]).")
    rows = []
    for label, pat, flags, builder, sizes in BENCH_CASES:
        for n in sizes:
            subj = builder(n)
            with tempfile.TemporaryDirectory(prefix="m46a.bench.") as d:
                args = [PCREC, "-p", "rx"] + flags + [
                    "--backtrack-frames=%d" % BIG_FRAMES,
                    "--step-budget=%d" % BIG_STEP,
                    "--work-budget=%d" % BIG_WORK,
                    "-o", os.path.join(d, "gen.c"), "--", pat]
                r = subprocess.run(args, timeout=TIMEOUT, capture_output=True, text=True)
                if r.returncode != 0:
                    eprint(f"[bench] REFUSED: {label} {pat!r} :: {r.stderr.strip()[:160]}")
                    continue
                src = open(os.path.join(d, "gen.c"), encoding="utf-8").read()
                vm = is_vm(src)
                print(f"  {label:22s} n={n:9d} engine={'vm' if vm else 'dfa'}")
                if not vm:
                    continue
                out = run_group(pat, "", None, [(0, subj)], BIG_FRAMES, BIG_STEP,
                                 BIG_WORK, label="bench-" + label)
                if out:
                    for row in out:
                        row["pattern"] = label + " :: " + pat
                    rows.extend(out)
                    for row in out:
                        print("   ->", row)
    return rows


# ---------------------------------------------------------------------------
# Layer 2: SCALE -- synthetic legitimate large-subject VM-forced probes
# ---------------------------------------------------------------------------

SCALE_SHAPES = [
    # (label, pattern, subject_fn(n), rung note)
    ("cursor-match", "([a-z]+)9", lambda n: b"a" * n + b"9", "possessified cursor, MATCH"),
    ("cursor-nomatch", "([a-z]+)9", lambda n: b"a" * n, "possessified cursor, NOMATCH (unanchored restart)"),
    # NOTE: this compiles to the REVERSE-DETERMINISTIC rung (RX_VM_RUNGS
    # 0x8), not the naive frames-unbounded rung the label first assumed --
    # each alternative's LAST byte differs ('a' vs 'b'), so the backwards
    # walk is unambiguous and frame_capacity is O(1) (verified: 3, ceiling
    # 0). The finding is sharper for it: this is the OPTIMIZED rung, and it
    # still charges steps/work linearly in n (one cut per ambiguous
    # position) -- the O(n) cost measured below is inherent to revdet's own
    # accounting, not a fallback-to-frames artifact.
    ("alternation-loop", "(a|b)+c", lambda n: (b"ab" * (n // 2)) + b"c", "revdet rung, capturing repeated alternation"),
    ("frames-bounded-64", "((a)|b){0,64}d", lambda n: (b"ab" * (n // 2))[:n] + b"d", "frames rung, bounded choice body"),
    ("m46b-anticipated", "([01]*)1([01]{8})", lambda n: b"0" * n + b"1" + b"01010101", "[M4.6b]'s not-yet-landed capture-bearing bench sibling"),
]


def layer2_scale(full):
    print("\n== LAYER 2: SCALE (synthetic legitimate large-subject) ==")
    print("TWO ENGINE MODES, and the distinction is load-bearing (found by "
          "running this layer the first time): DEFAULT (auto) is the shipped "
          "production path, where engine_m4.md §4.7's DFA-prefilter-before-VM "
          "ordering rule applies even to capture-bearing patterns -- a NOMATCH "
          "the prefilter can answer never reaches the VM's counters at all. "
          "'--engine=vm' is a DIAGNOSTIC opt-out (used by vm_oracle.py, the "
          "possessify/rungselect/counterk differentials) that disables the "
          "prefilter on purpose, so its numbers are a worst-case UPPER bound "
          "on what the VM alone would need, not a number the shipped default "
          "path ever has to survive. DEFAULT is layer 2's calibration input; "
          "VM-FORCED is recorded for context and for the diagnostic-mode "
          "question (should --engine=vm get its own, larger defaults?).")
    sizes = [1_000, 10_000, 100_000, 1_000_000] if full else [1_000, 100_000]
    rows = []
    for label, pat, subj_fn, note in SCALE_SHAPES:
        print(f"-- {label}: {pat!r} ({note}) --")
        for n in sizes:
            subj = subj_fn(n)
            for engine, tag, keep in ((None, "default", True), ("vm", "vm-forced", False)):
                out = run_group(pat, "", None, [(0, subj)], BIG_FRAMES, BIG_STEP,
                                 BIG_WORK, engine=engine, label="scale-" + label + "-" + tag)
                if out is None:
                    continue
                for row in out:
                    row["pattern"] = label + " [" + tag + "] :: " + pat
                    print(f"   [{tag:9s}] n={row['n']:9d} verdict={row['verdict']:14s} "
                          f"steps={row['steps']:12d} work={row['work']:14d} "
                          f"peak_btn={row['peak_btn']:6d} peak_trn={row['peak_trn']:6d}")
                    if keep:
                        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Layer 3: RATIO re-anchoring (k23_design.md's retracted 5.24 proxy)
# ---------------------------------------------------------------------------

def layer3_ratio():
    print("\n== LAYER 3: RATIO re-anchor -- k23_design.md's retracted 5.24 "
          "work-per-step proxy, re-measured against the REAL RX_ERR_WORK "
          "meter (D49/settlement 4) on the SAME shape/size ==")
    print("NOTE: this shape IS the K23 pathology (the pre-MRL 'shipped arm' "
          "of the exemplar) -- NOT a legitimate workload, so it is excluded "
          "from the layer 1/2 maxima below. Measured for archival purposes "
          "only, as k23_design.md §12 item 5 owes.")
    pat = "(a{10,20}){10,50}"
    subj = b"a" * 100
    out = run_group(pat, "", None, [(0, subj)], BIG_FRAMES, BIG_STEP, BIG_WORK,
                     engine="vm", label="k23-ratio")
    if not out:
        print("   COULD NOT MEASURE (compile/instrument failure -- see stderr)")
        return None
    row = out[0]
    print(f"   pattern={pat!r} n=100 verdict={row['verdict']} "
          f"steps={row['steps']} work={row['work']}")
    if row["steps"] > 0:
        ratio = row["work"] / row["steps"]
        print(f"   REAL-METER work/step ratio: {ratio:.3f} "
              f"(retracted proxy was 5.24; counterk's independently-adopted "
              f"exchange rate, from timing not counts, was ~16)")
        return ratio
    return None


# ---------------------------------------------------------------------------
# Layer 4: FRAME/TRAIL REACH at the SHIPPED default -- what subject_ceiling
# an ordinary capturing/repeated-alternation pattern actually gets today,
# read straight off rx_info (no instrumentation needed: this is a static
# property of the compile, not a runtime count).
# ---------------------------------------------------------------------------

REACH_PATTERNS = [
    ("alt-loop-1tok", "(a|b)+c"),
    ("alt-loop-4tok", "(GET |POST |PUT |DELETE )*X"),
    ("alt-loop-2tok", "(foo|bar)+baz"),
    ("nested-opt", "(a(b|c)?){0,4}d"),
]


def layer4_reach():
    print("\n== LAYER 4: FRAME/TRAIL REACH at the SHIPPED default (1024/1536) ==")
    print("Static property of the compile (rx_info.subject_ceiling), not a "
          "runtime count -- no instrumentation. Answers: for an ORDINARY "
          "capturing/repeated-alternation pattern, past how many subject "
          "bytes does the SHIPPED default's frame/trail capacity become "
          "reachable? A small number here means the corpus's own small-"
          "subject max (layer 1's 298/204) understates real exposure, "
          "because the corpus never repeats these shapes past a few bytes.")
    for label, pat in REACH_PATTERNS:
        with tempfile.TemporaryDirectory(prefix="m46a.reach.") as d:
            genc = os.path.join(d, "gen.c")
            r = subprocess.run([PCREC, "-p", "rx", "--emit-main", "-o", genc,
                                 "--", pat], timeout=TIMEOUT, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"   {label:16s} {pat!r:30s} REFUSED")
                continue
            src = open(genc, encoding="utf-8").read()
            fc = re.search(r"\.frame_capacity = (\d+),", src)
            sc = re.search(r"\.subject_ceiling = (\d+),", src)
            print(f"   {label:16s} {pat!r:30s} frame_capacity="
                  f"{fc.group(1) if fc else '?':6s} subject_ceiling="
                  f"{sc.group(1) if sc else '?'}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def summarize(all_rows):
    print("\n== SUMMARY: measured maxima (layers 1+2, K23-ratio shape EXCLUDED) ==")
    legit = [r for r in all_rows if not r["verdict"].startswith("GAVE-UP")]
    if not legit:
        print("   NO VM ROWS MEASURED -- instrument produced nothing. Treat as "
              "a BROKEN RUN, not a finding of zero need.")
        sys.exit(2)

    def top(key):
        row = max(legit, key=lambda r: r[key])
        return row[key], row

    for key, label in (("steps", "STEP"), ("work", "WORK"),
                        ("peak_btn", "FRAME(bt)"), ("peak_trn", "TRAIL")):
        val, row = top(key)
        print(f"   max {label:10s} = {val:14d}   pattern={row['pattern']!r} "
              f"n={row['n']} verdict={row['verdict']}")
    print(f"\n   groups/cases measured: {len(legit)}")


def main():
    full = "--full" in sys.argv[1:]
    require_build()
    print("== m46a budget_calibration.py ==")
    print("commit  ", subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                                      capture_output=True, text=True).stdout.strip() or "?")
    print("gcc     ", subprocess.run([CC, "--version"], capture_output=True, text=True).stdout.splitlines()[0])
    print("date    ", time.strftime("%Y-%m-%d %H:%M:%S %z"))
    print(f"measurement ceilings: frames={BIG_FRAMES} step={BIG_STEP} work={BIG_WORK} "
          f"(NOT the shipped defaults -- see module docstring)")

    all_rows = []
    all_rows += layer1_corpus()
    all_rows += layer1_bench(full)
    all_rows += layer2_scale(full)
    layer3_ratio()
    layer4_reach()
    summarize(all_rows)


if __name__ == "__main__":
    main()
