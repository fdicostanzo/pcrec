#!/usr/bin/env python3
"""make_corpus.py — the PRODUCER of tests/counterk/counterk.rxt.

Committed for R24 M-F4's reason: a corpus whose expectations were hand-written,
or produced by a script nobody kept, cannot be re-derived when the oracles move.
Every expectation in that file came from HERE, from BOTH oracles (python3 `re`,
and libpcre2 through ctypes), and a cell the two disagreed on is REPORTED
rather than resolved.

THE ORACLE PLUMBING IS IMPORTED, NOT COPIED, from `../possessify_impl/gen_rxt.py`
— the same choice the rung-select lane made one rung up, and for the same
payoff: that file carries the instrument note this generator would otherwise
rediscover, that `pcre2_match` returns the number of ovector pairs it FILLED
(highest participating group + 1, not the pattern's group count), so reading
only `rc` pairs makes every trailing UNSET group vanish rather than read as
unset. It produced seven phantom "oracle disagreements" on that lane's first
run.

WHAT THIS CORPUS COVERS THAT §8.1's DIFFERENTIAL STRUCTURALLY CANNOT, and it is
the reason this file exists rather than being a second copy of patterns.txt:

    THE DIFFERENTIAL IS BLIND ABOVE THE REPLICATION KNEE. Its ground truth is
    the `-fno-counter` build, and replication is REFUSED above
    PCREC_MAX_VM_REPEAT_COPIES (64) — so at `{0,4000}` there is no ground truth
    to compare against, because the ground truth is what the cap refuses. §8.1
    says so in as many words and §8.5 cell 1 inherits the gap.

    An ORACLE sweep has no such dependency: python and libpcre2 answer
    `((a)|ab){0,4000}c` without caring what pcrec's replication cap is. So the
    high-count blocks below are the ONLY check in the tree that the endgame
    shapes — the ones this whole rung exists for — actually match correctly,
    rather than merely compiling and stamping an honest ceiling.

    That is not a nice-to-have. Every other instrument in this lane verifies
    the rung against shapes replication can also emit; these blocks verify it
    where replication cannot follow.

EVERY PATTERN IS CAPTURE-BEARING, and that is not decoration: under the DEFAULT
engine choice a capture-free pattern routes to the DFA and never reaches
src/gen/emit_vm.c, so the rung would be structurally invisible to it. `.rxt`
blocks carry no engine flag, so the pattern text has to force the VM itself and
a capturing group is what does that. The possessify lane measured this failure
on its own first version (33 of 38 patterns DFA-routed), and this lane
reproduced it in miniature while testing §3.3's preference witness — which is
non-capturing, and was measured against the DFA before the rung stamp was
asserted.

THE COUNTS ARE CHOSEN FOR THEIR RESIDUE MOD K (K = 8), for the reason
tests/counterk/patterns.txt states at length: this rung's boundary arithmetic
IS the mod-K lattice, and a population sharing a residue cannot see a parity
bug. R26 E1/E2 is the precedent; this lane's own first sweep (residues
{4,4,1,1}, 576 green cells) is the local instance.

SUBJECTS STAY SHORT ON THE HIGH-COUNT BLOCKS. §3.5 is explicit that this rung
shrinks emitted SIZE and not FRAMES, so `((a)|ab){0,4000}c` stamps a
subject_ceiling around 307 bytes and returns RX_ERR_FRAMES above it — an honest
give-up, not a wrong answer, but not a matchable cell either. The high-count
blocks therefore use subjects an order of magnitude inside that ceiling, and
the ceiling itself is asserted by §8.5's acceptance cell rather than here.

Usage: python3 docs/design/counterk_impl/make_corpus.py tests/counterk/counterk.rxt
"""
import ctypes, ctypes.util, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "possessify_impl"))
from gen_rxt import emit, py_span, esc   # noqa: E402

# ---------------------------------------------------------------------------
# MEASURED, and it changed this file's design: LIBPCRE2 CANNOT COMPILE THE
# ENDGAME COUNTS AT ALL.
#
#   ((a)|ab){0,2047}c   compiles
#   ((a)|ab){0,2048}c   ERROR 120, "regular expression is too large"
#
# The boundary is exactly 2047 for this shape (bisected). The cause is the same
# one this whole rung exists to remove: PCRE2 REPLICATES a capture-bearing
# quantified group too, so 4000 copies overflow its compiled-pattern limit —
# pcrec's own replication cap and PCRE2's size limit are two spellings of the
# same constraint, and the counter rung lifts pcrec's.
#
# SO AT THE ENDGAME COUNTS PCREC COMPILES A PATTERN PCRE2 REFUSES. That is a
# capability difference worth stating rather than an oracle disagreement worth
# resolving, and D26 is the frame: PCRE2 is the source of truth for what a
# pattern MATCHES, and it has no opinion here because it declined to have one.
#
# WHY THIS NEEDED HANDLING RATHER THAN THE DEFAULT PATH. `gen_rxt.emit` treats
# UNCOMPILABLE-versus-an-answer as a disagreement and DROPS the cell, which is
# right when the two oracles contradict each other. Here it produced blocks with
# a `pattern` line and NO CELLS — vacuous blocks that read as coverage in a file
# listing and assert nothing. §3.6's rule is INVESTIGATE, not filter, and the
# investigation is above: error 120 is a RESOURCE limit, not a semantic verdict.
# So these blocks fall back to python alone, with the reason recorded IN the
# block rather than in a commit message.
def pcre2_error(pat):
    """None if libpcre2 compiles `pat`, else (code, message)."""
    lib = ctypes.CDLL(ctypes.util.find_library("pcre2-8") or "libpcre2-8.so.0")
    lib.pcre2_compile_8.restype = ctypes.c_void_p
    lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t,
                                    ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
    lib.pcre2_get_error_message_8.restype = ctypes.c_int
    lib.pcre2_get_error_message_8.argtypes = [ctypes.c_int, ctypes.c_char_p,
                                              ctypes.c_size_t]
    err = ctypes.c_int(); off = ctypes.c_size_t()
    if lib.pcre2_compile_8(pat.encode(), len(pat.encode()), 0,
                           ctypes.byref(err), ctypes.byref(off), None):
        return None
    buf = ctypes.create_string_buffer(256)
    lib.pcre2_get_error_message_8(err.value, buf, 256)
    return (err.value, buf.value.decode())


def emit_python_only(blocks, out):
    """Blocks where libpcre2 declines to have an opinion. Python is the oracle;
    the REASON libpcre2 is absent is asserted here rather than assumed, so a
    future libpcre2 that grows the limit turns this into a loud failure instead
    of a silently weaker check."""
    for header, pat, subjects in blocks:
        why = pcre2_error(pat)
        if why is None:
            sys.stderr.write(
                "FATAL: %r was routed to the python-only path but libpcre2 "
                "COMPILES it -- move it back to the three-way blocks.\n" % pat)
            sys.exit(2)
        if why[0] != 120:
            sys.stderr.write(
                "FATAL: %r: libpcre2 declines with error %d (%s), not the "
                "SIZE limit this path is justified by. A semantic refusal is "
                "a finding, not a fallback.\n" % (pat, why[0], why[1]))
            sys.exit(2)
        out.write("\n")
        for line in header:
            out.write("# " + line + "\n")
        out.write("# ORACLE: python3 `re` ONLY. libpcre2 refuses this pattern -- "
                  "error %d, \"%s\" --\n" % why)
        out.write("# because it REPLICATES a capture-bearing quantified group "
                  "just as pcrec's frames\n")
        out.write("# rung does, so the count overflows its compiled-pattern "
                  "limit (measured boundary\n")
        out.write("# for this shape: 2047 compiles, 2048 does not). It has no "
                  "opinion here rather than\n")
        out.write("# a different one, which is a CAPABILITY difference and not "
                  "an oracle disagreement.\n")
        out.write("pattern %s\n" % pat)
        for subj in subjects:
            v = py_span(pat, subj)
            if v in (None, "UNCOMPILABLE"):
                out.write('n "%s"\n' % esc(subj))
            else:
                out.write('m "%s" %d %d\n' % (esc(subj), v[0][0], v[0][1]))
                for k in range(1, len(v)):
                    out.write('g %d %d %d\n' % (k, v[k][0], v[k][1]))

# Subjects for the `((a)|ab)` family: runs of the body's own alphabet across the
# loop's boundary counts, with and without the follow, plus mixed runs — because
# the capture question is WHICH iteration last entered a group, and only a mixed
# run asks it.
S = ["", "a", "b", "c", "ac", "bc", "abc", "aac", "abac", "aabc",
     "aaac", "aaaac", "aaaaac", "aaaaaaaac", "aaaaaaaaac", "aaaaaaaaaac",
     "ababababc", "abababababc", "aabbc", "abbc", "baac",
     "aaaaaaaaaaaac", "aaaaaaaaaaaaaaaaac", "ababababababababc",
     "q", "aq", "abq", "za", "zabc"]

# Subjects for the multi-byte / stride > 1 families.
T = ["", "x", "e", "ab", "cd", "abe", "cde", "abcde", "ababe", "cdcde",
     "abcdabcde", "xababe", "xabababe", "abababababe", "cdcdcdcde",
     "xq", "abq", "e", "abcdabcdabcde"]

# Subjects for the possessified family (`((a)|bc)` with follow `d`).
P = ["", "d", "ad", "bcd", "abcd", "aad", "aaad", "bcbcd", "abcbcd",
     "aaaaaaaad", "aaaaaaaaad", "aaaaaaaaaaaad", "bcbcbcbcd",
     "aaaaaaaaaaaaaaaaad", "abcabcd", "q", "aq", "bcq"]

BLOCKS = [
 # ---- RESIDUE AXIS, optional phase ----------------------------------------
 (["RESIDUE 7 mod 8 -- K-1, so the loop NEVER RUNS and the emitter reduces to",
   "vm_opt_chain's output byte-identically (§3.2's structural property). The",
   "block is here as the CONTROL for the ones below it: if the counter rung",
   "changed an answer, this is the count at which it provably did not."],
  "((a)|ab){0,7}c", S),
 (["RESIDUE 0 at exactly K: one trip, zero residue. R25 E3's strictness lives",
   "here -- byte-identity holds at K > NOPT and NOWHERE ELSE, so this count",
   "emits the same NUMBER of body copies as replication and not the same code."],
  "((a)|ab){0,8}c", S),
 (["RESIDUE 1: one trip plus a one-copy tail, the smallest non-empty residue."],
  "((a)|ab){0,9}c", S),
 (["RESIDUE 4: one trip plus a four-copy tail. This is the residue sabotage",
   "S54 (the tail deleted) is visible at and residue 0 is not."],
  "((a)|ab){0,12}c", S),
 (["RESIDUE 7 at two trips -- the largest residue, and the count where the",
   "tail is nearly a whole trip's worth of copies."],
  "((a)|ab){0,15}c", S),
 (["RESIDUE 0 at two trips: the loop runs twice with no tail at all."],
  "((a)|ab){0,16}c", S),
 (["RESIDUE 1 at two trips."],
  "((a)|ab){0,17}c", S),

 (["LAZY at a non-zero residue. §3.3's claim is that a counter LOOP is",
   "preference-equivalent to the NESTED optional chain and not to a chained",
   "one; greedy and lazy must both be swept or half the claim leaves the",
   "corpus silently (R24 S-F1's rule, which cost that lane its lazy result)."],
  "((a)|ab){0,12}?c", S),
 (["LAZY at residue 1, two trips."],
  "((a)|ab){0,17}?c", S),

 # ---- RESIDUE AXIS, mandatory phase ---------------------------------------
 (["MANDATORY PHASE at residue 4 (§3.1). NOPT == 0, so §2.3's carve-out",
   "applies: the optional phase must emit NOTHING, not even a counter reset,",
   "or the byte-identity property §3.2 promises at K > NOPT breaks at every K."],
  "((a)|ab){12}c", S),
 (["MANDATORY PHASE at residue 0 -- an exact multiple of K, where the residue",
   "tail is empty and the trip guard's target label still has to exist."],
  "((a)|ab){16}c", S),
 (["MANDATORY PHASE at residue 1."],
  "((a)|ab){17}c", S),

 # ---- BOTH PHASES AT ONCE --------------------------------------------------
 (["BOTH PHASES LIVE, which is the cell the possessive arm's silent cap lived",
   "in: a mandatory phase at or above K AND an optional phase. Residues varied",
   "on the two halves independently (9 mod 8 = 1, 8 mod 8 = 0)."],
  "((a)|ab){9,17}c", S),
 (["BOTH PHASES, different residues again (11 mod 8 = 3, 8 mod 8 = 0)."],
  "((a)|ab){11,19}c", S),
 (["BOTH PHASES, lazy."],
  "((a)|ab){9,17}?c", S),

 # ---- a second, independently-declining body ------------------------------
 (["A REVERSE-AMBIGUOUS body (rungselect_design.md §5 residual 1). It declines",
   "the revdet rung for a DIFFERENT reason than the alternation above does, so",
   "it is a second independent body on the same axis rather than a rephrasing."],
  "((ab)|b){0,12}b", S),
 (["The same body at residue 1."],
  "((ab)|b){0,17}b", S),

 # ---- NULLABLE bodies ------------------------------------------------------
 (["A NULLABLE body above K (§5's territory), spelled at {0,12} rather than",
   "{0,4} because below K no counter is emitted and the cell would be checking",
   "replication's termination, which D44/R21 E-2 already settled. E-2 also",
   "RULED that the empty-iteration guard exists for rmax == -1 ONLY: with it",
   "applied to bounded repeats, 60 of 225,240 pairs diverge from libpcre2.",
   "These cells are what a regression to that reading would break."],
  "(a?){0,12}b", S),
 (["A nullable body that can consume MORE than one byte per iteration."],
  "(a*){0,12}b", S),
 (["The EMPTY BRANCH form, which is R24's own oracle-split family: python and",
   "libpcre2 agree on every span and can differ on group 1 (python reports an",
   "empty span at the loop's end where libpcre2 reports the last iteration",
   "that consumed). §3.6's rule is INVESTIGATE, not filter -- the span is kept",
   "because both authorities assert it, and a slot-only divergence is dropped",
   "with a note rather than pinned to whichever oracle was asked first."],
  "(|a){0,12}b", S),

 # ---- STRIDE > 1 -----------------------------------------------------------
 (["STRIDE > 1: a nested cursor rung runs INSIDE the counter loop. This is the",
   "shape R26 E1/E2 found an 855-cell differential structurally blind to, and",
   "for this rung it is also §8.1's [R25 E16] nested cell -- the only place an",
   "untrailed inner local could be read across an OUTER trip boundary -- and",
   "the only shape exercising §7.4's one division, the frameless scan's",
   "`(cur - pos) / stride`."],
  "(x(?:ab){2,4}){0,12}c", T),
 (["Branches of DIFFERENT length inside the counter loop, so an iteration's",
   "width is not a constant the emitter can subtract."],
  "((?:ab)|(?:cd)){0,12}e", T),
 (["A two-byte class body at residue 1."],
  "([ab][cd]){0,17}e", T),

 # ---- POSSESSIFIED ---------------------------------------------------------
 (["POSSESSIFIED (§3.4), reached through the possessify PASS rather than",
   "through `+` -- that spelling needs module `atomic-groups`, which has no",
   "producer, so a `+`-written pattern is REFUSED and would test nothing.",
   "`((a)|bc)` qualifies: one-unambiguous, prefix-free, follow disjoint from",
   "its FIRST. U9 is the thing to consult before investigating a disagreement",
   "in this family (PCRE2 10.46 will not backtrack into a preceding item after",
   "a possessive bounded repeat of a group, so python-possessive and",
   "PCRE2-possessive are not interchangeable oracles)."],
  "((a)|bc){0,12}d", P),
 (["POSSESSIFIED with BOTH phases -- the exact shape whose frame peak was",
   "under-counted (max instead of sum) and returned RX_ERR_FRAMES where",
   "replication matched."],
  "((a)|bc){9,20}d", P),
 (["POSSESSIFIED, exact count."],
  "((a)|bc){12}d", P),

 # ---- ABOVE THE REPLICATION KNEE ------------------------------------------
 # The blocks this file exists for. Nothing else in the tree checks these:
 # §8.1's differential cannot, because its ground truth is what the cap
 # refuses, and §8.5's acceptance cell asserts that they COMPILE and stamp an
 # honest ceiling rather than what they MATCH.
 (["ABOVE THE REPLICATION KNEE. `-fno-counter` cannot build this at all --",
   "PCREC_MAX_VM_REPEAT_COPIES refuses 100 copies -- so §8.1's differential is",
   "structurally blind here and this is the ONLY check in the tree that the",
   "answer is right rather than merely produced. Subjects stay far inside the",
   "stamped subject_ceiling (§3.5: this rung shrinks SIZE, not FRAMES)."],
  "((a)|ab){0,100}c", S),
 (["FIVE HUNDRED. The emitted size is K + 500 mod K copies whatever the count",
   "is, so this artifact is the same size as the one above; that is the rung's",
   "entire claim, and these cells are it being true rather than asserted."],
  "((a)|ab){0,500}c", S),
 (["TWO THOUSAND AND FORTY-SEVEN -- the LARGEST count libpcre2 will compile",
   "for this shape, bisected. One more and it answers error 120, 'regular",
   "expression is too large'. So this is the last block in the file where the",
   "three-way rule is even available, and it is deliberately pinned at the",
   "boundary rather than at a round number below it."],
  "((a)|ab){0,2047}c", S),
]

# Blocks above libpcre2's own size limit for this shape. See the long note at
# the top of this file: PCRE2 declines to have an opinion here, which is a
# CAPABILITY difference rather than a disagreement, and the fallback is
# python-only WITH the reason asserted per block.
PY_ONLY_BLOCKS = [
 (["THE ENDGAME COUNT. `((a)|ab){0,4000}c` is D45's own case one body over:",
   "refused by pcrec before this rung existed, compiled now. §8.5 cell 1",
   "asserts that it COMPILES and stamps an honest ceiling; this block asserts",
   "what it MATCHES, which nothing else in the tree does.",
   "",
   "AND PCRE2 CANNOT COMPILE IT AT ALL, which is the finding that reshaped",
   "this file: PCRE2 replicates a capture-bearing quantified group exactly as",
   "pcrec's frames rung does, so it hits its own compiled-pattern limit at the",
   "same kind of boundary pcrec's replication cap sets. The counter rung lifts",
   "pcrec's; PCRE2's stands."],
  "((a)|ab){0,4000}c", S),
 (["The endgame count with a MANDATORY phase, which takes §3.1's loop rather",
   "than §3.2's -- a different emitted shape at the same count."],
  "((a)|ab){4000}c", S),
 (["The endgame count POSSESSIFIED, where the optional phase has no trip and",
   "no K at all (§3.4) and the emitted body is a single re-entered copy."],
  "((a)|bc){0,4000}d", P),
]

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "tests/counterk/counterk.rxt"
    with open(out, "w") as f:
        f.write("# tests/counterk/counterk.rxt -- GENERATED, do not hand-edit.\n")
        f.write("# Producer: docs/design/counterk_impl/make_corpus.py\n")
        f.write("# Expectations come from BOTH oracles (python3 re + libpcre2);\n")
        f.write("# a cell the two disagree on is reported, never silently resolved.\n")
        f.write("#\n")
        f.write("# The high-count blocks at the end are the ONLY check in the tree\n")
        f.write("# that the shapes above the replication knee MATCH correctly:\n")
        f.write("# tests/counterk/'s differential cannot reach them, because its\n")
        f.write("# ground truth is the build the replication cap refuses.\n")
        emit(BLOCKS, f)
        f.write("\n# " + "-" * 70 + "\n")
        f.write("# ABOVE LIBPCRE2'S OWN SIZE LIMIT. Python is the only oracle\n")
        f.write("# below this line, and each block says why in its own header.\n")
        emit_python_only(PY_ONLY_BLOCKS, f)
    sys.stderr.write("wrote %s\n" % out)

if __name__ == "__main__":
    main()
