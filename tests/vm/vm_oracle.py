#!/usr/bin/env python3
"""tests/vm/vm_oracle.py — the [M4.5b] VM emitter's capture-correctness check.

WHAT IT COMPARES, and why it is three things and not one:

  1. CAPTURES AGAINST AN ORACLE. Every group span the emitted VM reports is
     checked against python `re`'s match.span(k) (D4: python `re` is the base
     tier's oracle; libpcre2 joins as a differential at M7/M4.7 and the
     three-way rule of engine_m4.md §3.6 applies from there). Expectations are
     never written by hand — a hand-written span is an expectation derived
     from the implementation's own alphabet, which is the failure D27 exists
     to catch.

  2. THE §3.7 DIFFERENTIAL, AS A GATE. The DFA and the VM compute the match
     SPAN by completely independent methods (priority subset construction vs.
     backtracking), so they must agree exactly — §6.1's claim. That claim's
     span-equality half is BELIEVED-WITH-GATE, not STRUCTURAL: the R21 panel
     found a live counterexample (K17) by running §13's own P-1 probe, so it
     is a property to be CHECKED PER PATTERN FAMILY, not assumed.

     The gate runs `--engine=vm`, which disables the prefilter (D44/R21 E-6).
     That is the whole point: under the hybrid the VM is HANDED the DFA's own
     answer as its anchored window, so `span(VM) == span(DFA)` is close to a
     TAUTOLOGY — the VM could get $0.END or a capture wrong while trivially
     agreeing on $0.START. Only a prefilter-free run is a genuinely
     independent second derivation.

  3. THE HYBRID AGAINST VM-ONLY. Same pattern, same subjects, two engines
     that share no derivation of the span. A disagreement means the prefilter
     handed the VM a window it should not have.

Usage:  python3 tests/vm/vm_oracle.py [--quick] [--jobs N] [--cases FILE]
Env:    PCREC (default build/pcrec), CC (default gcc)
"""

import os
import re
import subprocess
import sys
import tempfile
import shutil
import itertools
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PCREC = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))
CC = os.environ.get("CC", "gcc")
GENCFLAGS = os.environ.get(
    "GENCFLAGS", "-O1 -std=gnu11 -Wall -Wextra -Werror").split()
if os.environ.get("LINTGEN", "0") == "1":
    GENCFLAGS.append("-fanalyzer")

DRIVER = os.path.join(ROOT, "tests", "vm", "vm_driver.c")


# ---------------------------------------------------------------- the cases
#
# Subjects are chosen per pattern from a small alphabet sweep rather than
# hand-picked per case: a hand-picked subject set is the same
# derived-from-the-implementation hazard as a hand-picked expectation.

def sweep(alphabet, maxlen):
    out = [""]
    for n in range(1, maxlen + 1):
        out += ["".join(t) for t in itertools.product(alphabet, repeat=n)]
    return out


# Hand-written PATTERNS (not expectations) covering the base tier's capture
# shapes, each named for the property it is there to expose.
CORE_PATTERNS = [
    # --- flat groups, the shape with no backtracking at all
    "(a)", "(ab)", "(a)(b)", "(a)b(c)", "((a))", "((a)(b))",
    # --- alternation: which branch's writes survive (§3.2's second bullet)
    "(a)|(b)", "(a)b|(a)c", "(a|b)", "(a|b)(c|d)", "x(a|ab)y",
    "(ab|a)b", "(a|ab)b", "(?:(a)|(b))+",
    # --- greedy vs lazy: which side is the fallthrough (§2.2 property 3)
    "(a*)", "(a+)", "(a?)", "(a*?)", "(a+?)", "(a??)",
    "(a*)b", "(a*?)b", "(a*)(a*)", "(a+)(a+)", "(.*)(.*)",
    "(a*)a", "(a*?)a",
    # --- REPEATED groups: a later iteration overwrites, and if the loop then
    #     exits normally the overwrite must stand (§3.2 first bullet)
    "(a)*", "(a)+", "(a)*b", "(a)+b", "(a)?", "(a){2}", "(a){2,3}",
    "(ab)*", "(ab)+", "(ab)*c", "((a)b)*", "(a(b))*",
    # --- and a failed final iteration must restore to the SUCCESSFUL
    #     earlier iteration's value, not to unset (§3.2's `((a)|b)+` case)
    "((a)|b)+", "((a)|b)*", "((a)|b){2}", "(?:(a)|(b))*c",
    # --- NULLABLE bodies under an unbounded quantifier: the §3.3 guard
    "(a*)*", "(a*)+", "(|a)+", "(a|)+", "((?:))*", "(a?)*", "(a??)*",
    "(a*)*b", "(a*?)*", "()*", "()+", "(){0}", "(a*)*a",
    # --- BOUNDED repeats, where the guard must NOT apply (E-2, MEASURED:
    #     60/225,240 divergences with the guard, 0 without)
    "(a*?){1,2}b", "(a*){1,2}", "(a*){0,2}", "(a*?){0,2}b", "(a?){2}",
    "(a*){2}", "(|a){2}", "(a|){1,3}", "(?:ab|a){0,2}?b",
    # --- the K17/K18 family: the trap templates' own shapes, capturing.
    #     K18 is a DFA-construction known_fail; the VM's §3.3 guard is a
    #     SEPARATE mechanism, so the VM handling these correctly is expected
    #     and touches nothing on the ratchet.
    "(a*?(b*)*)*", "(a*?(b*)+)*", "(a??(b*)*)*", "(a*?(b*|a*)*)*",
    "(a*?((b*)*)*)*", "((a|b*?)?)*", "(?:(a)|(b*?))?*" if False else "((a)|(b*?))*",
    "(b*?(a*)*)*", "(b*?(a*)*)+", "(b*?(a*)*)?",
    # --- anchors inside groups
    "(^a)", "(a$)", "(^)", "($)", "(^a$)", "(^|a)b", "(a|^)b",
    # --- classes and the cursor rung's own shapes (§2.5)
    "([a-c]+)", "([a-c]*)b", "([^a]*)a", "(\\d+)", "(\\w+)", "(\\s*)a",
    "(a)(?:b)(c)", "(.)(.)", "(..)*", "(...)?",
    # --- deterministic fixed-stride bodies WITH captures (D44.1's extension)
    "(ab)*c", "(ab)+c", "(a(b))+", "((a)(b))*", "(abc){2,}", "(ab){1,3}",
    # --- long runs: the rung that keeps `a*` off the frame bound at all
    "(a*)$", "(a+)$", "a*(b)", ".*(b)",
    # --- nesting depth
    "((((a))))", "(((a)|b)|c)", "((a)*)*", "(((a)*)*)*",
]

# --- GENERATED patterns -----------------------------------------------------
#
# The hand list above is an alphabet chosen by the person who wrote the
# emitter, which is exactly the bias D27 exists to counter and exactly why the
# fuzzer's TRAP TEMPLATES exist: tests/fuzz/CLAUDE.md records that the R2-M1
# preference bug needed three things at once and four seeded runs missed it,
# and that the K17 family's joint probability under an unbiased generator is
# ~1e-4..1e-5 per pattern. Those templates are reused here verbatim in shape,
# instantiated with CAPTURING groups instead of `(?:`, because the property
# under test moved: the DFA's priority construction owned those spans before,
# the VM's own priority/empty handling owns them now, and they are different
# mechanisms that can fail independently.
#
# K18 note: it is a DFA-CONSTRUCTION known_fail (the closure's `seen` memo vs.
# the path-dependent empty-iteration rule). The VM's S3.3 guard is a separate
# mechanism, so the VM getting these right is EXPECTED and touches nothing on
# the ratchet, which pins the DFA path.
TRAP_TEMPLATES = [
    "({a}{b}|{a}){q}{b}",       # overlapping-prefix branches, R2-M1 shape
    "({a}|{a}{b}){q}{b}",       # same, preferred branch is the SHORT one
    "(|{a}){q}",                # nullable PREFERRED branch (R2-S1 shape)
    "({a}|){q}{b}",             # nullable trailing branch
    "({a}{a}|{a}){q}{a}",       # overlapping same-letter runs
    "{a}({b}|{b}{a}){q}{a}",    # trap behind a literal prefix
    "({a}*?({b}*)*)*",          # K17's own repro shape, capturing
    "({a}*?({b}*)*){q}",        # same body under every outer quantifier
    "({a}??({b}*)+){q}",        # lazy `??` prefix, inner `+`
    "({a}*?({b}*|{a}*)*){q}",   # nullable ALTERNATION as the inner body
    "({a}*?(({b}*)*)*){q}",     # one nesting level deeper again
    "(({a}|{b}*?)?)*",          # K18's own repro shape, capturing
    "(({a})|({b}*?))*",         # two groups, one nullable and lazy
    # cursor-rung shapes: deterministic fixed-stride bodies, D44.1's extension
    "({a}{b}){q}{a}", "(({a})({b})){q}", "({a}{a}{b}){q}{b}",
    "{a}({b}{a}){q}{b}", "(({a}{b}){{2}}){q}",
]
TRAP_QUANTS = ["*", "+", "?", "*?", "+?", "{0,2}", "{0,2}?", "{1,3}?", "{2,}?",
               "{2,3}", "{0,1}", "{1,2}?"]


def generated():
    """Every trap template x every quantifier x a two-letter alphabet."""
    import itertools as it
    for tmpl, q, (a, b) in it.product(TRAP_TEMPLATES, TRAP_QUANTS,
                                      [("a", "b")]):
        yield tmpl.format(a=a, b=b, q=q)


# Alphabet per pattern is derived from the pattern's own literal bytes plus a
# neighbour, so subjects actually exercise the branches.
def alphabet_for(pat):
    letters = sorted(set(c for c in pat if c.isalnum()))
    if not letters:
        letters = ["a"]
    letters = letters[:3]
    if "b" not in letters and len(letters) < 3:
        letters.append("b")
    return letters


def cases(quick):
    maxlen = 3 if quick else 4
    pats = list(CORE_PATTERNS)
    if not quick:
        pats += sorted(set(generated()))
    for pat in pats:
        alpha = alphabet_for(pat)
        subs = sweep(alpha, maxlen)
        if "\\d" in pat:
            subs += sweep(["1", "2", "a"], 3)
        if "\\w" in pat or "\\s" in pat:
            subs += sweep(["a", " ", "_"], 3)
        if "\n" not in pat:
            subs += ["a\nb", "\n", "aa\n"]
        yield pat, sorted(set(subs))


# ------------------------------------------------------------------- oracle

def oracle(pat, subj, startpos=0):
    """python `re`'s answer as the flat [s0,e0,s1,e1,...] the driver prints.

    `Pattern.search(string, pos)` is the right oracle for a non-zero startpos
    and not merely a convenient one: python does NOT let `^` match at `pos`,
    only at the real start of the string, which is exactly the contract
    lib/pcrec.h states for the emitted searcher ("`^` anchors to absolute
    offset 0 regardless of startpos"). The `re.match`-with-a-slice
    alternative would disagree on every `^` pattern.
    """
    try:
        rx = re.compile(pat.encode("latin-1"))
    except re.error:
        return None
    b = subj.encode("latin-1")
    if startpos > len(b):
        return "nomatch"
    m = rx.search(b, startpos)
    if not m:
        return "nomatch"
    out = []
    for k in range(rx.groups + 1):
        s, e = m.span(k)
        out.append((s, e))
    return out


def esc(s):
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\r":
            out.append("\\r")
        elif 32 <= ord(ch) < 127:
            out.append(ch)
        else:
            out.append("\\x%02x" % ord(ch))
    return "".join(out)


# ------------------------------------------------------------------ compile

def build(workdir, pat, extra):
    d = tempfile.mkdtemp(dir=workdir)
    cfile = os.path.join(d, "gen.c")
    r = subprocess.run([PCREC, "-p", "rx"] + extra + ["-o", cfile, "--", pat],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None, "pcrec failed: " + r.stderr.strip()
    exe = os.path.join(d, "t")
    r = subprocess.run([CC] + GENCFLAGS + ["-DVM_CHECK_ANCHORED", "-I", d,
                                           "-o", exe, DRIVER, cfile],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None, "gcc failed: " + r.stderr.strip()[:1200]
    return exe, None


def run(exe, subj, startpos=0):
    argv = [exe, esc(subj)] + ([str(startpos)] if startpos else [])
    r = subprocess.run(argv, capture_output=True, text=True)
    if r.returncode != 0:
        return "DRIVER_EXIT_%d: %s" % (r.returncode, r.stderr.strip()[:300])
    line = r.stdout.strip()
    if line == "nomatch":
        return "nomatch"
    if line.startswith("err_"):
        return line
    parts = line.split()
    if parts[0] != "match":
        return "BAD_OUTPUT: " + line
    nums = [int(x) for x in parts[1:]]
    return list(zip(nums[0::2], nums[1::2]))


# --------------------------------------------------------------------- main

def check_pattern(workdir, pat, subs):
    fails = []
    built = {}
    for mode, extra in (("auto", []), ("vmonly", ["--engine=vm"])):
        exe, err = build(workdir, pat, extra)
        if err:
            fails.append("%-24s [%s] BUILD: %s" % (pat, mode, err))
            return fails, 0
        built[mode] = exe

    n = 0
    for subj in subs:
        want = oracle(pat, subj)
        if want is None:
            return fails, 0          # python rejects the pattern: not our tier
        got_auto = run(built["auto"], subj)
        got_vm = run(built["vmonly"], subj)
        n += 1

        # (1) captures against the oracle
        if got_auto != want:
            fails.append('%-24s "%s" auto: got %s want %s'
                         % (pat, esc(subj), got_auto, want))
        # (2)+(3) the §3.7 differential, run prefilter-free so it is
        # independent rather than tautological
        if got_vm != want:
            fails.append('%-24s "%s" --engine=vm: got %s want %s'
                         % (pat, esc(subj), got_vm, want))
        if got_auto != got_vm:
            fails.append('%-24s "%s" HYBRID/VM-ONLY DIVERGENCE: %s vs %s'
                         % (pat, esc(subj), got_auto, got_vm))

        # STARTPOS. Its own axis because the two engines reach it by
        # completely different routes: the hybrid hands `startpos` to the DFA
        # prefilter and anchors the VM at whatever window comes back, while
        # --engine=vm begins its own scan there. And `^` must still anchor to
        # ABSOLUTE offset 0 either way (lib/pcrec.h's stated contract), which
        # is a rule a start-offset implementation gets wrong by default.
        for sp in (1, 2):
            if sp > len(subj):
                continue
            w = oracle(pat, subj, sp)
            ga = run(built["auto"], subj, sp)
            gv = run(built["vmonly"], subj, sp)
            n += 1
            if ga != w:
                fails.append('%-24s "%s"@%d auto: got %s want %s'
                             % (pat, esc(subj), sp, ga, w))
            if gv != w:
                fails.append('%-24s "%s"@%d --engine=vm: got %s want %s'
                             % (pat, esc(subj), sp, gv, w))
    return fails, n


def main():
    quick = "--quick" in sys.argv
    jobs = 4
    if "--jobs" in sys.argv:
        jobs = int(sys.argv[sys.argv.index("--jobs") + 1])

    if not os.path.exists(PCREC):
        sys.exit("vm_oracle: no pcrec binary at %s (run make first)" % PCREC)

    workdir = tempfile.mkdtemp(prefix="vmoracle.")
    allfails, total, npat = [], 0, 0
    try:
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            futs = [ex.submit(check_pattern, workdir, p, s)
                    for p, s in cases(quick)]
            for f in futs:
                fails, n = f.result()
                allfails += fails
                total += n
                npat += 1
    finally:
        if os.environ.get("KEEP", "0") != "1":
            shutil.rmtree(workdir, ignore_errors=True)
        else:
            print("vm_oracle: KEEP=1, temp dir: " + workdir, file=sys.stderr)

    for line in allfails[:80]:
        print("FAIL: " + line)
    if len(allfails) > 80:
        print("... and %d more" % (len(allfails) - 80))
    print("vm_oracle: %d patterns, %d pattern/subject pairs checked against "
          "python re, %d failures" % (npat, total, len(allfails)))
    return 1 if allfails else 0


if __name__ == "__main__":
    sys.exit(main())
