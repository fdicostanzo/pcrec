"""[DD-14] §5 PROTOTYPE -- the call mechanism, EXECUTED against libpcre2.

`../prototype/callproto.c` implements §5's lowering by hand in pcrec's emitted
idiom -- the frame that carries the return label, the non-popping return, the
fail label's one added line, and the |W| trailed save/restore -- for four
patterns chosen because each one is a design claim:

  P1  ^((a)(?1)?(b))$                     per-level capture save/restore
  P2  ^(?(DEFINE)(?<g>a|ab))(?&g)c$       backtrack INTO a returned call
  P3  ^(a|(?1)a)$                         n-1 same-position nested recursions
  P4  ^(?(DEFINE)(?<g>x|xy))(?&g)(?&g)y$  §5.2's CLOBBER SEQUENCE

and it is compiled TWICE: once as designed, and once with -DBROKEN_ARRAY,
which replaces the frame-carried return label with the plan row's separate
`call_stack[]` indexed by call depth and popped at the return. **The broken
build is the whole point of this probe**: a design section that says "the
obvious alternative has a bug" and does not run it is an argument, and §5.2 is
load-bearing.

REACHABILITY, and this probe has two guards that matter:
  (a) the two builds must AGREE on most cells and DISAGREE on at least one --
      a broken build that agrees everywhere would mean the discriminating
      sequence is not in the corpus, and the bug would be unproven;
  (b) every pattern must produce at least one match and one no-match, or the
      differential is comparing one answer everywhere.

P3's DEPTH cells are compared against libpcre2 only where PCRE2 answers; where
PCRE2 gives rc -52 the prototype gives its own `recurse`, and the row is
scored as AGREED-IN-KIND (both refused to answer) rather than as a match --
which is §3.3's ruling, and the probe prints the two codes so a reader can see
it is not hiding a disagreement.
"""
import importlib.util
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "sr_oracle", os.path.join(_HERE, "sr_oracle.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)

SRC = os.path.normpath(os.path.join(_HERE, "..", "prototype", "callproto.c"))
TMP = os.environ.get("TMPDIR", "/tmp")
GOOD = os.path.join(TMP, "dd14_callproto_good")
BROKEN = os.path.join(TMP, "dd14_callproto_broken")

# (index, pattern, ncap) -- ncap MUST match `ncaps[]` in callproto.c, or the
# comparison reports a REPORT-SHAPE difference as a semantic disagreement.
# The first version had 0 here for the two DEFINE patterns while the C side
# printed 1 group, and six cells came out "DISAGREES WITH libpcre2" for a
# construct that agrees perfectly. That is the two-oracles-compared-across-a-
# report-shape-difference defect, one lane over.
PATS = [
    (0, r"^((a)(?1)?(b))$", 3),
    (1, r"^(?(DEFINE)(?<g>a|ab))(?&g)c$", 1),
    (2, r"^(a|(?1)a)$", 1),
    (3, r"^(?(DEFINE)(?<g>x|xy))(?&g)(?&g)y$", 1),
]

# THE PROTOTYPE HAS NO MINIMUM-LENGTH PRUNE, and one cell depends on it.
# `^(a|(?1)a)$` on "" -- libpcre2 answers NOMATCH because its own start
# optimization rejects a subject shorter than the pattern's minimum length,
# BEFORE the recursion is ever entered; the prototype has no such prune and
# descends until its depth capacity fires. pcrec DOES have the machinery
# (`pcrec_minw`, and the design's §4.4 gives A_CALL a least-fixpoint arm whose
# answer here is 1), so the shipped compiler agrees with libpcre2 and this
# prototype does not. Listed rather than hidden, and scored separately.
MINLEN_CELLS = {(2, "")}

SUBJ = {
    0: ["ab", "aabb", "aaabbb", "aaaabbbb", "aab", "abb", "", "a", "b",
        "abab", "ba", "aabbb", "aaabb", "aabab"],
    1: ["abc", "ac", "abbc", "", "a", "ab", "abcc", "c", "aabc", "bc"],
    2: ["a", "aa", "aaa", "aaaa", "aaaaa", "a" * 10, "a" * 50, "a" * 200,
        "", "b", "ab", "ba", "aab", "a" * 1023, "a" * 1024],
    3: ["xxyy", "xyxy", "xxy", "xyy", "xy", "y", "", "xyxyy", "xxxy",
        "xyy y".replace(" ", ""), "xyxyxy"],
}


def build():
    for out, extra in ((GOOD, []), (BROKEN, ["-DBROKEN_ARRAY"])):
        cmd = ["gcc", "-O2", "-std=gnu11", "-Wall", "-Wextra"] + extra + \
              ["-o", out, SRC]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("BUILD FAILED:", " ".join(cmd))
            print(r.stderr)
            sys.exit(3)
        if r.stderr.strip():
            print("  build warnings for %s:\n%s" % (out, r.stderr))


def run(binary, which, subj):
    r = subprocess.run([binary, str(which), subj], capture_output=True,
                       text=True, timeout=60)
    return r.stdout.strip()


def pcre_answer(pat, subj, ncap):
    r = sr.match_limits(pat, subj)
    if isinstance(r, tuple) and r and r[0] == "ERR":
        return "COMPILE-ERR"
    if isinstance(r, tuple) and r and r[0] == "rc":
        return "giveup(rc=%d)" % r[1]
    if r is None:
        return "nomatch"
    span, groups = r
    out = "match %d %d" % (span[0], span[1])
    for g in groups[:ncap]:
        out += " %d %d" % (g if g else (-1, -1))
    return out


print("libpcre2:", sr.version())
print("python3 :", sys.version.split()[0])
print("sr_oracle.SELFCHECK:", sr.SELFCHECK or "none")
print("prototype source:", SRC)
print()
build()
print("=== the two builds, and the differential against libpcre2 ============")

agree_pcre = disagree_pcre = kindagree = minlen_cells = 0
gb_agree = gb_disagree = 0
outcomes = {}
disagreements = []
gb_rows = []

for which, pat, ncap in PATS:
    print("--- P%d  %s" % (which + 1, pat))
    outcomes[which] = set()
    for subj in SUBJ[which]:
        g = run(GOOD, which, subj)
        b = run(BROKEN, which, subj)
        p = pcre_answer(pat, subj, ncap)
        label = repr(subj if len(subj) <= 12 else "%s...(%d)"
                     % (subj[:8], len(subj)))
        outcomes[which].add("match" if g.startswith("match")
                            else ("giveup" if g in ("recurse", "frames")
                                  else "nomatch"))
        if (which, subj) in MINLEN_CELLS:
            print("  %-16s proto=%-26s broken=%-26s pcre2=%-26s   "
                  "(MINLEN cell: the prototype has no minimum-length prune; "
                  "see MINLEN_CELLS)" % (label, g, b, p))
            minlen_cells += 1
            if g == b:
                gb_agree += 1
            else:
                gb_disagree += 1
                gb_rows.append((pat, subj, g, b))
            continue
        if g.startswith("match") or g == "nomatch":
            if g == p:
                agree_pcre += 1
                mark = ""
            else:
                disagree_pcre += 1
                mark = "   <-- DISAGREES WITH libpcre2"
                disagreements.append((pat, subj, g, p))
        else:
            # the prototype gave up. Score AGREED-IN-KIND only if PCRE2 also
            # refused to answer; otherwise it is a real disagreement.
            if p.startswith("giveup"):
                kindagree += 1
                mark = "   (both refused: %s / %s)" % (g, p)
            else:
                disagree_pcre += 1
                mark = "   <-- prototype gave up where libpcre2 ANSWERED"
                disagreements.append((pat, subj, g, p))
        if g == b:
            gb_agree += 1
        else:
            gb_disagree += 1
            gb_rows.append((pat, subj, g, b))
        print("  %-16s proto=%-26s broken=%-26s pcre2=%-26s%s"
              % (label, g, b, p, mark))
    print()

print("=== TOTALS ==========================================================")
print("  prototype vs libpcre2 : %d agree, %d agreed-in-kind (both refused), "
      "%d DISAGREE, %d excluded as MINLEN cells"
      % (agree_pcre, kindagree, disagree_pcre, minlen_cells))
for pat, subj, g, p in disagreements:
    print("     %s on %r: prototype=%r libpcre2=%r" % (pat, subj, g, p))
print("  designed vs BROKEN_ARRAY: %d agree, %d DISAGREE"
      % (gb_agree, gb_disagree))
for pat, subj, g, b in gb_rows:
    print("     %s on %r: designed=%r broken=%r" % (pat, subj, g, b))
print()

print("=== REACHABILITY GUARDS =============================================")
ok = True
if gb_disagree == 0:
    print("  !! VACUOUS: the BROKEN build agrees on every cell. §5.2's clobber")
    print("     sequence is NOT in this corpus and the bug is UNPROVEN.")
    ok = False
else:
    print("  guard (a): the broken build DISAGREES on %d cell(s) -- §5.2's bug"
          " is reproduced, not argued" % gb_disagree)
if gb_agree == 0:
    print("  !! VACUOUS: the two builds agree NOWHERE, so the difference is "
          "not localised to the clobber sequence")
    ok = False
else:
    print("  guard (a'): and AGREES on %d cell(s), so the difference is "
          "localised" % gb_agree)
for which, pat, _ in PATS:
    got = outcomes[which]
    if len(got) < 2:
        print("  !! VACUOUS: P%d produced only %s" % (which + 1, sorted(got)))
        ok = False
print("  guard (b): every pattern produced at least two distinct outcomes"
      if ok else "  guard (b): FAILED, see above")
if disagree_pcre:
    print("  !! the prototype DISAGREES with libpcre2 on %d cell(s) -- §5's "
          "lowering does not reproduce 10.46" % disagree_pcre)
else:
    print("  the prototype agrees with libpcre2 on every cell it answered")
