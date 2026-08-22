"""probe_expand_cost.py -- MEASURED, IN-PCREC (the expansion arm), plus a
PROTOTYPE size model.

Charter (c): whether the finite-language expansion rewrite -- Frank's
2026-08-12 design note, engine_m4.md 5.2's `discharge` socket -- SHIPS in
module `backrefs` or is chartered as a follow-on with VM-only semantics
first.

THE MEASUREMENT IS EXACT AND NOT MODELLED, and that is the point. pcrec
cannot compile `(a|b)\\1`, but it CAN compile `aa|bb` -- the expansion's
OUTPUT -- today, right now, with no new code. So for each finite-group
backref family this probe:

  1. computes L(G), the referenced group's finite language, and writes
     out the EXPANSION as a real pattern (each word w contributing
     `w w`, synchronized);
  2. hands that pattern to the SHIPPED compiler on the DFA path
     (`--no-captures`, see below) and records whether it compiles, what
     it costs in emitted bytes, DFA states and gcc compile time, or
     which cap refused it;
  3. reports where the size-estimate obligation 5.2 hands the rewrite
     author has to DECLINE.

WHY `--no-captures` IS NOT A CONVENIENCE HERE BUT THE WHOLE ANSWER.
`src/opt/select_engine.c`'s `forces_captures` returns ENGM_VM whenever
`cx->want_caps && cx->ncap > 0`, and captures are ON BY DEFAULT (D42.1).
A backreference pattern has a capturing group BY CONSTRUCTION -- there is
nothing to refer back to otherwise -- so on a default build every backref
pattern is VM-forced by the CAPTURES row no matter what the backrefs row
says, and no expansion can discharge that. Verified directly on the built
compiler in the CAPTURES arm below. The expansion's entire customer set
is therefore `--no-captures` builds.
"""
import itertools
import os
import re
import subprocess
import sys
import tempfile
import time

REPO = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()
PCREC = os.path.join(REPO, "build", "pcrec")

# From src/core/limits.h, quoted here so a reader can see what the numbers
# below are being compared against. Read live rather than transcribed.
def limits():
    out = {}
    txt = open(os.path.join(REPO, "src", "core", "limits.h")).read()
    for k in ("PCREC_MAX_NFA_STATES", "PCREC_MAX_DFA_STATES_TABLE",
              "PCREC_MAX_DFA_STATES_GOTO", "PCREC_MAX_TABLE_ENTRIES"):
        m = re.search(k + r"\s*=\s*(\d+)", txt)
        if m:
            out[k] = int(m.group(1))
    return out


# (tag, referenced group's language as an explicit finite set, the source
#  backref pattern it comes from)
FAMILIES = [
    ("alt2",     ["a", "b"],                              r"(a|b)\1"),
    ("quote",    ['"', "'"],                              r'(["\'])\1'),
    ("lit3",     ["abc"],                                 r"(abc)\1"),
    ("cls3",     [c for c in "abc"],                       r"([abc])\1"),
    ("cls26",    [chr(c) for c in range(ord("a"), ord("z") + 1)],
     r"([a-z])\1"),
    ("cls2x2",   ["".join(p) for p in itertools.product("ab", repeat=2)],
     r"([ab]{2})\1"),
    ("cls26x2",  ["".join(p) for p in itertools.product(
        [chr(c) for c in range(ord("a"), ord("z") + 1)], repeat=2)],
     r"([a-z]{2})\1"),
    ("cls26x3",  None,   r"([a-z]{3})\1"),      # 17,576 words -- built lazily
    ("cls26x4",  None,   r"([a-z]{4})\1"),      # 456,976 words
    ("alt5x3",   ["".join(p) for p in itertools.product("abcde", repeat=3)],
     r"((?:a|b|c|d|e){3})\1"),
]

LAZY = {
    "cls26x3": lambda: ["".join(p) for p in itertools.product(
        [chr(c) for c in range(ord("a"), ord("z") + 1)], repeat=3)],
    "cls26x4": lambda: ["".join(p) for p in itertools.product(
        [chr(c) for c in range(ord("a"), ord("z") + 1)], repeat=4)],
}


def expansion(words):
    """The rewrite, as `engine_m4.md` 5.2's note states it: one alternative
    per word of L(G), the reference SYNCHRONIZED (the same word twice).
    Capture-erased, which is what `--no-captures` already gives us."""
    return "|".join(re.escape(w) + re.escape(w) for w in words)


def compile_one(pat, extra=()):
    """Compile with the SHIPPED binary and report (ok, bytes, states, gcc_s,
    err). `states` is read off the emitted artifact's own table, never
    modelled."""
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "m.c")
        t0 = time.time()
        try:
            r = subprocess.run([PCREC, "-p", "rx", "--no-captures", *extra,
                                "-o", out, "--", pat],
                               capture_output=True, text=True, timeout=300)
        except OSError as e:
            # E2BIG. Not a probe failure -- a RESULT: past a few hundred
            # kilobytes the expansion cannot even be HANDED to a compiler
            # through argv. Recorded rather than crashed on, which is what
            # this probe's first run did.
            return (False, 0, 0, time.time() - t0, 0.0,
                    "cannot be passed at all: %s" % e.strerror)
        t_pcrec = time.time() - t0
        if r.returncode != 0:
            msg = (r.stderr.strip().splitlines() or [""])[-1]
            return (False, 0, 0, t_pcrec, 0.0, msg[:60])
        c = open(out).read()
        nbytes = len(c)
        # R32 C15: the `states` read that used to sit here was DEAD -- no
        # caller printed it, and its regex matched nothing on a DFA
        # artifact anyway. Emitted BYTES is what this probe actually
        # reports and what the size-estimate obligation needs, so the dead
        # read is gone rather than left to look like evidence.
        states = 0
        t0 = time.time()
        g = subprocess.run(["gcc", "-O2", "-c", "-I", td, "-o",
                            os.path.join(td, "m.o"), out],
                           capture_output=True, text=True, timeout=600)
        t_gcc = time.time() - t0
        if g.returncode != 0:
            return (False, nbytes, states, t_pcrec, t_gcc,
                    "gcc FAILED: " + (g.stderr.strip().splitlines()
                                      or [""])[0][:44])
        return (True, nbytes, states, t_pcrec, t_gcc, "")


def captures_arm():
    print("=" * 78)
    print("0. THE CAPTURES ARM -- can the expansion EVER discharge the VM on")
    print("   a default (captures-on) build?")
    print("=" * 78)
    rows = [
        ("(abc)(abc)", (), "the expansion's OUTPUT, captures ON"),
        ("(abc)(abc)", ("--no-captures",), "the same, captures OFF"),
        ("abcabc", (), "the same LANGUAGE with no groups at all"),
        ("(a|b)(a|b)", (), "the alt2 expansion, captures ON"),
        ("(a|b)(a|b)", ("--no-captures",), "the same, captures OFF"),
    ]
    print("%-14s %-16s %-34s %s" % ("pattern", "flags", "engine", "cell"))
    print("-" * 96)
    for pat, extra, note in rows:
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "m.c")
            r = subprocess.run([PCREC, "-p", "rx", *extra, "-o", out, "--",
                                pat], capture_output=True, text=True,
                               timeout=60)
            if r.returncode != 0:
                eng = "REFUSED"
            else:
                c = open(out).read()
                m = re.search(r'#define RX_ENGINE "(\w+)"', c)
                w = re.search(r'#define RX_ENGINE_WHY "([^"]*)"', c)
                eng = (m.group(1) if m else "dfa (no stamp)")
                if w:
                    eng += " -- " + w.group(1)
        print("%-14s %-16s %-34s %s"
              % (pat, " ".join(extra) or "(default)", eng[:34], note))
    print()
    print("If the captures-ON rows say `vm ... capture group`, then on a")
    print("default build the CAPTURES row forces the VM independently of")
    print("anything the backrefs row does, and the expansion buys nothing.")
    print()


def main():
    if not os.path.exists(PCREC):
        print("build/pcrec ABSENT -- this probe measures the SHIPPED")
        print("compiler and refuses to report modelled numbers instead.")
        return 2
    L = limits()
    print("pcrec caps, read live from src/core/limits.h:")
    for k, v in L.items():
        print("  %-28s %d" % (k, v))
    print()
    captures_arm()

    print("=" * 78)
    print("1. THE EXPANSION, COMPILED. Each row's pattern is the REWRITE'S")
    print("   OUTPUT handed to the shipped compiler on the DFA path.")
    print("=" * 78)
    print("%-10s %-18s %-8s %-8s %-9s %-7s %-7s %s"
          % ("family", "backref pattern", "|L(G)|", "pat len", "emitted",
             "pcrec s", "gcc s", "outcome"))
    print("-" * 118)
    nrows = 0
    for tag, words, src in FAMILIES:
        if words is None:
            words = LAZY[tag]()
        pat = expansion(words)
        ok, nbytes, states, tp, tg, err = compile_one(pat)
        nrows += 1
        print("%-10s %-18s %-8d %-8d %-9s %-7.2f %-7.2f %s"
              % (tag, src, len(words), len(pat),
                 ("%d B" % nbytes) if nbytes else "-", tp, tg,
                 "compiled" if ok else ("REFUSED: " + err)))
    print()
    print("=" * 78)
    print("2. WHERE `discharge` MUST DECLINE -- the boundary, bisected on")
    print("   the SHIPPED compiler rather than estimated.")
    print("=" * 78)
    alpha = [chr(c) for c in range(ord("a"), ord("z") + 1)]

    def wordset(k):
        """The first k words of {a..z}^3, so the family is one family and
        only its SIZE varies -- the arm-vs-arm shape this project's probes
        use so a divergence cannot be attributed to a shape change."""
        return ["".join(t) for t in itertools.islice(
            itertools.product(alpha, repeat=3), k)]

    lo, hi = 1, 17576
    # confirm the endpoints before bisecting; a bisection between two
    # endpoints that both compile (or both refuse) reports a boundary that
    # is not there.
    ok_lo = compile_one(expansion(wordset(lo)))[0]
    ok_hi = compile_one(expansion(wordset(hi)))[0]
    print("  endpoint check: k=%d compiles=%s ; k=%d compiles=%s"
          % (lo, ok_lo, hi, ok_hi))
    if not ok_lo or ok_hi:
        print("  ENDPOINTS DO NOT BRACKET A BOUNDARY -- refusing to bisect")
    else:
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if compile_one(expansion(wordset(mid)))[0]:
                lo = mid
            else:
                hi = mid
        okrow = compile_one(expansion(wordset(lo)))
        badrow = compile_one(expansion(wordset(hi)))
        print("  LARGEST |L(G)| that compiles : %d  (pattern %d B, emitted %s,"
              " gcc %.2f s)"
              % (lo, len(expansion(wordset(lo))),
                 "%d B" % okrow[1], okrow[4]))
        print("  SMALLEST that does not       : %d  -> %s"
              % (hi, badrow[5]))
        print()
        print("  That number is what 5.2's size-estimate obligation has to")
        print("  predict BEFORE committing the rewrite: past it the expansion")
        print("  produces a pattern the DFA refuses, and a rewrite that")
        print("  expands and then fails has destroyed a VM answer that was")
        print("  available.")

    print()
    print("The VM-ONLY comparison for the same families, so the expansion's")
    print("cost has something to be a cost AGAINST:")
    print("%-10s %-18s %-9s %-7s %s"
          % ("family", "erased pattern", "emitted", "gcc s", "outcome"))
    print("-" * 78)
    # R32 C16: this loop used to stop at FAMILIES[:6], which excluded
    # cls26x2 -- the ONLY family whose expansion is large enough for the
    # comparison to say anything. The two E2BIG/over-cap families are
    # excluded by name (their un-expanded form is what compiles), not by
    # a slice that silently dropped a live row.
    for tag, words, src in [f for f in FAMILIES
                            if f[0] not in ("cls26x3", "cls26x4")]:
        if words is None:
            words = LAZY[tag]()
        # the VM's own shape: the group's sub-pattern, ONCE, plus a compare
        # the VM does at run time and no pattern text represents. The nearest
        # honest stand-in is the group's own sub-pattern twice UNSYNCHRONIZED,
        # which is what the pattern would be if the backref were erased.
        alt = "(?:" + "|".join(re.escape(w) for w in words) + ")"
        ok, nbytes, states, tp, tg, err = compile_one(alt + alt)
        print("%-10s %-18s %-9s %-7.2f %s"
              % (tag, src, ("%d B" % nbytes) if nbytes else "-", tg,
                 "compiled" if ok else ("REFUSED: " + err)))
    if nrows == 0:
        print("REFUSING to report: no family ran")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
