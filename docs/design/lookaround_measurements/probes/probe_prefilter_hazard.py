#!/usr/bin/env python3
"""[M6.6.1] §5 -- THE PREFILTER, argued THEN measured.

THE ARGUMENT the charter asks for: a lookaround is ZERO-WIDTH and PURELY A
CONSTRAINT, so deleting it from a pattern can only ADD strings to the language.
That much is a one-line proof. The charter then asks for the measurement,
because `atomic_groups_design.md` §4 and `backrefs_design.md` §7 both found
that "superset" is not the property the hybrid actually needs.

WHAT THE HYBRID NEEDS, from the emitter as it ships (src/gen/emit_vm.c:5283-
5319, `v.mrl_win`, and select_engine.c:450-541, `fit.prefilter`), is THREE
separate properties, and they are separately falsifiable:

  H1  REJECTION.   erase(P) matches nowhere  =>  P matches nowhere.
  H2  START.       leftmost-start(erase(P)) <= leftmost-start(P).
                   (A start that is too EARLY costs work; too LATE loses
                   matches. This is what the prefilter seeds the VM with.)
  H3  END.         end(erase(P)) >= end(P).
                   This is the one the atomic lane found FALSE for its own
                   construct, at 114 cells of silent match loss in the DEFAULT
                   engine, because `v.mrl_win` feeds the prefilter's window
                   END to the [M4.6d] MRL pruning as a CEILING.

H3 IS MEASURED TWICE, AND ONLY THE SECOND FORM IS THE SHARP ONE. The obvious
comparison -- leftmost end of erase(P) against leftmost end of P -- CONFLATES
two failures, because when H2 puts the erased match at an EARLIER START the
two ends are not about the same candidate at all, and the emitted retry loop
re-asks the prefilter at every start it advances to (emit_vm.c's H2 note:
"its span START stays a lower bound ... and the emitted loop already re-asks
it on every retry"). The sharp form fixes the start: at the candidate start
the true match uses, does the erased pattern ANCHORED THERE end at or after
the true end? Both columns are reported, the naive one labelled as such, so a
reader can see that the two populations differ -- which they do.

THE ERASURE IS SPELLED OUT, not `sed`-ed. backrefs_measurements' own probe
defect list records a `sed 's/\\\\1//'` that erased a backreference to EPSILON
-- a different and unsound approximation from the one being argued about. Here
the erasure DELETES the whole lookaround group, brackets and body, which is
exactly the approximation the superset argument is about, and `erase()` is
tested against a fixture table at import so it cannot be silently wrong.

VACUITY GUARDS. A table of zeros proves nothing unless the population contains
cells that COULD be non-zero (R32's finding against this project's own
instruments). Two guards, both hard failures:
  * the POSITIVE CONTROL family must produce at least one H3 violation, or
    the probe reports that it measured nothing;
  * the population must contain at least one subject on which erase(P) and P
    give DIFFERENT spans, or the erasure is not being exercised at all.
"""
import importlib.util
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
_spec = importlib.util.spec_from_file_location(
    "la_oracle", os.path.join(_HERE, "la_oracle.py"))
la = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(la)

# --------------------------------------------------------------------------
# THE ERASER
# --------------------------------------------------------------------------
_OPENERS = ("(?=", "(?!", "(?<=", "(?<!", "(?<*", "(?*")


def erase(pat):
    """Delete every lookaround group -- delimiters and body -- from `pat`.

    Bracket-aware and escape-aware and class-aware, because `[(]` and `\\(` are
    not group openers and a lookaround may nest inside another group. A
    QUANTIFIER directly after a deleted lookaround is deleted with it: `(?=a)*`
    erases to nothing, not to a dangling `*`, which would not compile at all
    and would silently turn every such cell into an ERR row."""
    out = []
    i, n = 0, len(pat)
    incls = False
    while i < n:
        c = pat[i]
        if c == "\\" and i + 1 < n:
            out.append(pat[i:i + 2])
            i += 2
            continue
        if incls:
            if c == "]":
                incls = False
            out.append(c)
            i += 1
            continue
        if c == "[":
            incls = True
            out.append(c)
            i += 1
            continue
        hit = next((o for o in sorted(_OPENERS, key=len, reverse=True)
                    if pat.startswith(o, i)), None)
        if hit is None:
            out.append(c)
            i += 1
            continue
        # skip the balanced group
        depth = 0
        j = i
        jn = False
        jc = False
        while j < n:
            ch = pat[j]
            if ch == "\\":
                j += 2
                continue
            if jc:
                if ch == "]":
                    jc = False
                j += 1
                continue
            if ch == "[":
                jc = True
                j += 1
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        del jn
        # eat a quantifier that was attached to the group we just removed
        while j < n and pat[j] in "*+?":
            j += 1
        if j < n and pat[j] == "{":
            k = pat.find("}", j)
            if k > 0 and all(ch.isdigit() or ch == "," for ch in pat[j + 1:k]):
                j = k + 1
                while j < n and pat[j] in "*+?":
                    j += 1
        i = j
    return "".join(out)


_ERASE_FIXTURES = [
    (r"(?=a)b", r"b"),
    (r"(?!a)b", r"b"),
    (r"(?<=a)b", r"b"),
    (r"(?<!a)b", r"b"),
    (r"a(?=b)c", r"ac"),
    (r"(?=(a|b))c", r"c"),
    (r"(?=a)*b", r"b"),
    (r"(?=a){2,3}b", r"b"),
    (r"(?=a(b))c", r"c"),                 # a nested group goes with it
    (r"[(?=a]b", r"[(?=a]b"),             # inside a class: NOT a lookaround
    (r"\(?=a\)b", r"\(?=a\)b"),           # escaped: NOT a lookaround
    (r"(?:a(?=b))c", r"(?:a)c"),          # nested inside an ordinary group
    (r"(?=a)(?!b)c", r"c"),               # two in a row
    (r"a(?<=b)|ab", r"a|ab"),             # the alternation shape H3 breaks on
    (r"(?*a)b", r"b"),
    (r"(?<*a)b", r"b"),
    (r"a(?=b)", r"a"),
]
_ERASE_PROBLEMS = [(p, erase(p), w) for p, w in _ERASE_FIXTURES
                   if erase(p) != w]


def show(v):
    if v == "ERR":
        return "ERR"
    if v is None:
        return "nomatch"
    return "(%d,%d)" % (v[0][0], v[0][1])


def span(v):
    if v is None or v == "ERR":
        return None
    return v[0]


# --------------------------------------------------------------------------
# THE POPULATION
# --------------------------------------------------------------------------
# Each family: (name, pattern, [subjects], expect_h3_violation)
FAMILIES = [
    ("lead-pos-la",  r"(?=\w)\w+",          ["  abc", "abc", "a b", "", " a"], False),
    ("lead-neg-la",  r"(?!ab)\w\w",         ["abcd", "xycd", "ab", "aab"], False),
    ("lead-pos-lb",  r"(?<=,)\w+",          ["ab,cd", ",ab", "abcd", "a,,b"], False),
    ("lead-neg-lb",  r"(?<!\w)\w+",         ["ab cd", " abc", "abc", "a-b"], False),
    ("trail-pos-la", r"\w+(?=,)",           ["ab,cd", "abcd", ",ab,", "a,b,"], False),
    ("trail-pos-lb", r"\w+(?<=b)",          ["abc", "ab", "cba", "xbxb"], False),
    ("mid-neg-la",   r"a(?!b)\w",           ["abac", "aab", "acab", "aa"], False),
    ("word-pair",    r"(?<!\w)\w+(?!\w)",   ["ab cd", "abc", " a ", "a-b"], False),
    # --- the POSITIVE CONTROL. The alternation shape: a branch whose
    # lookaround FAILS is preferred in the erased pattern and rejected in the
    # real one, so the erased match ENDS EARLIER than the real one.
    ("H3-control",   r"a(?!b)|ab",          ["ab", "ac", "abab", "xab"], True),
    ("H3-control-2", r"a(?<=xa)|ab",        ["ab", "xa", "xab", "abab"], True),
    ("H3-control-3", r"(?:a(?=c)|ab)c?",    ["abc", "ac", "ab", "abcabc"], True),
]

print("libpcre2:", la.version())
print("python3  :", sys.version.split()[0])
print("la_oracle SELFCHECK:", la.SELFCHECK or "none")
print("erase() fixture problems:", _ERASE_PROBLEMS or "none")
if _ERASE_PROBLEMS:
    print("!! the eraser is wrong; every number below is about a different")
    print("!! approximation from the one this section argues about")

print()
print("=" * 78)
print("THE ERASURES, printed in full (backrefs §0.3 defect 2: an erasure")
print("nobody can read is an erasure nobody can check)")
print("=" * 78)
for name, pat, _s, _v in FAMILIES:
    print("%-14s %-24s ->  %s" % (name, pat, erase(pat) or "(empty)"))

print()
print("=" * 78)
print("H1 / H2 / H3, cell by cell")
print("=" * 78)
print("%-14s %-10s | %-12s | %-12s | %-5s %-5s %-7s %-5s" %
      ("family", "subject", "P", "erase(P)", "H1", "H2", "H3nai", "H3sharp"))
print("-" * 86)
tot = {"H1": 0, "H2": 0, "H3naive": 0, "H3sharp": 0}
cells = 0
differing = 0
ctrl_h3 = 0
PCRE2_ANCHORED = 0x80000000


def anchored_at(pat, subj, at):
    """The erased pattern's match ANCHORED at `at` -- the candidate start the
    prefilter would have seeded the VM with. PCRE2_ANCHORED (0x80000000) is
    asserted behaviourally the first time it is used, below."""
    return la.search(pat, subj, at, PCRE2_ANCHORED)


# ASSERT the anchored bit rather than trusting it: `b` must match "ab" at
# startoffset 0 UNanchored and NOT match anchored there.
_A_OK = (la.search("b", "ab", 0) is not None
         and anchored_at("b", "ab", 0) is None
         and anchored_at("b", "ab", 1) is not None)
if not _A_OK:
    print("!! PCRE2_ANCHORED (0x80000000) does not anchor -- the SHARP H3")
    print("!! column below measured nothing")

for name, pat, subjects, expect in FAMILIES:
    er = erase(pat)
    for s in subjects:
        t = la.search(pat, s)
        e = la.search(er, s) if er else ((0, 0), [])
        ts, es = span(t), span(e)
        cells += 1
        h1 = "-" if es is not None or ts is None else "FAIL"
        if es is None and ts is not None:
            tot["H1"] += 1
        h2 = h3n = h3s = "-"
        if ts is not None and es is not None:
            if es[0] > ts[0]:
                h2 = "FAIL"
                tot["H2"] += 1
            if es[1] < ts[1]:
                h3n = "FAIL"
                tot["H3naive"] += 1
            if es != ts:
                differing += 1
        # the SHARP form: erase(P) anchored at the TRUE match's own start
        if ts is not None and er:
            a = span(anchored_at(er, s, ts[0]))
            if a is None:
                h3s = "H1@s"          # nothing there at all: an H1 failure
                tot["H1"] += 1
            elif a[1] < ts[1]:
                h3s = "FAIL"
                tot["H3sharp"] += 1
                if expect:
                    ctrl_h3 += 1
        print("%-14s %-10s | %-12s | %-12s | %-5s %-5s %-7s %-5s" %
              (name, repr(s), show(t), show(e), h1, h2, h3n, h3s))

print()
print("TOTALS over %d cells:" % cells)
print("  H1 violations (rejection unsound)          : %d" % tot["H1"])
print("  H2 violations (erased start too LATE)      : %d" % tot["H2"])
print("  H3 violations, NAIVE leftmost-vs-leftmost  : %d" % tot["H3naive"])
print("  H3 violations, SHARP anchored-at-true-start: %d  <- THE NUMBER THAT" % tot["H3sharp"])
print("                                                    MATTERS")
print("cells where erase(P) and P give DIFFERENT spans: %d" % differing)
print()
print("VACUITY GUARDS")
if ctrl_h3 == 0:
    print("  !! FAILED: the POSITIVE CONTROL families produced NO SHARP H3")
    print("  !! violation.")
    print("  !! A zero in the H3 column is then unfalsifiable and this probe")
    print("  !! measured nothing about H3.")
else:
    print("  ok: the positive control produced %d H3 violation(s), so a zero"
          % ctrl_h3)
    print("      in that column would have been a real result")
if differing == 0:
    print("  !! FAILED: erase(P) never differed from P on any subject --")
    print("  !! the erasure is not being exercised")
else:
    print("  ok: %d cells exercise the erasure" % differing)

# --------------------------------------------------------------------------
# THE IN-PCREC ARM
# --------------------------------------------------------------------------
print()
print("=" * 78)
print("IN-PCREC ARM: what the SHIPPED emitter does with the erased pattern")
print("=" * 78)
print("pcrec cannot compile a lookaround, so this arm compiles the ERASURE --")
print("which is exactly the machine the hybrid would attach as a prefilter --")
print("and reads the artifact's own stamps. It answers ONE question: would the")
print("MRL ceiling (`v.mrl_win`, emit_vm.c:5319) be live on these patterns?")
print("If it would, H3's violations are silent match loss in the DEFAULT")
print("engine, exactly as they were for atomic groups (114 cells).")
print()
PCREC = os.path.join(_ROOT, "build", "pcrec")
if not os.path.exists(PCREC):
    print("  no build/pcrec -- arm SKIPPED (not silently empty: this line is it)")
else:
    print("%-24s | %-8s | %-10s | %s" %
          ("erased pattern", "engine", "prefilter", "prune ceiling"))
    for name, pat, _s, _v in FAMILIES:
        er = erase(pat)
        if not er:
            continue
        # a capture group forces the VM, which is where a prefilter lives at
        # all; without one these erasures compile to the DFA and the question
        # does not arise. The wrapper is stated rather than hidden.
        wrapped = "(" + er + ")"
        try:
            r = subprocess.run(
                ["/usr/bin/gnutimeout", "20", PCREC, "-p", "rx", "-o", "-",
                 wrapped],
                capture_output=True, text=True, cwd=_ROOT)
        except Exception as ex:                             # noqa: BLE001
            print("%-24s | EXC %s" % (er, str(ex)[:40]))
            continue
        if r.returncode != 0:
            print("%-24s | refused: %s" % (er, r.stderr.strip()[:44]))
            continue
        c = r.stdout
        def stamp(nm):
            for line in c.splitlines():
                if nm in line and "#define" in line:
                    return line.split(nm, 1)[1].strip().strip('"')
            return "-"
        print("%-24s | %-8s | %-10s | %s" %
              (wrapped, stamp("RX_ENGINE ")[:8], stamp("RX_VM_PREFILTER"),
               stamp("RX_VM_PRUNE_CEILING")))
    print()
    print("# and the same question asked of the artifact's own IR listing:")
    r = subprocess.run(
        ["/usr/bin/gnutimeout", "20", PCREC, "-p", "rx", "--emit-ir",
         "-o", "/dev/null", r"((?:a|ab)c?)"],
        capture_output=True, text=True, cwd=_ROOT)
    for line in r.stdout.splitlines():
        if "prefilter" in line or "ceiling" in line:
            print("   ", line.strip())
