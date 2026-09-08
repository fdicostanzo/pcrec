# S-U9 ([M5.0] stage 2; utf8_design.md §8.2, §5.2.1 / r54 E4) -- THE
# BACK-STEP'S DECLARED-LENGTH TEST IS DELETED.
#
# THE CLAIM: `$_back_step` validates that every character run it steps over
# is DECLARED by its lead byte (§5.2.1's repair — "the line the first design
# draft did not have"). Without it the walk and the forward parse can
# disagree about where a character starts, and the lookbehind end-check —
# whose redundancy proof assumes they agree — FIRES.
#
# INVISIBLE ON EVERY WELL-FORMED SUBJECT, AND THE FAILURE IS AN ABORT, NOT A
# WRONG ANSWER: on `C2 80 80` (one continuation byte too many), the clean
# artifact's `(?<!.)x` back-step answers NONE at the ill-formed run, the
# assertion holds, and the match is found; the sabotaged one back-steps to 0,
# the body consumes the well-formed `C2 80` prefix, ends one byte short of
# the entry, and the NEGATIVE arm's end-check returns RX_R_INTERNAL — below
# PCREC_ERR_FLOOR, a composed site's __builtin_trap(). Reachable on a
# WELL-FORMED subject too through a mid-character startpos (§2.6.1.1), which
# is why P-9's instrument sweeps both.
SAB_ID="S-U9-back-step-length-test-deleted"
SAB_FILE="src/gen/enc/enc_utf8.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8"
SAB_DESC="the utf8 back_step's want != end - pos declared-length test is deleted; on an ill-formed continuation run (or a mid-character startpos) the walk and the forward parse disagree, the negative lookbehind's end-check fires RX_R_INTERNAL, and a composed call site traps on a subject the ruling promises will merely not match"
SAB_DOC_FIGURE="PREDICTED (§8.2): tests/utf8/invalid.rxt's (?<! cells over C2 80 80-shaped subjects red as ERROR returns rather than spans. DEMONSTRATED at stage 2 pre-corpus: (?<!.)x on C2 80 80 78 answers match(3,4) clean; sabotaged, rx_search returns the internal-error code."
SAB_REACH='"$PCREC" --features lookaround -e utf8 -p rx -o - -- "(?<!.)x"'
SAB_REACH_EXPECT='Pattern: (?<!.)x'
# RE-POINTED 2026-09-05: the stage-2 lane wrote this population against a
# GUESSED corpus filename; the promoted D27 corpus (merge 698eea61) landed
# with the axis naming, so the pop line named a file that does not exist and
# the first full mech run read the row UNREACHED-UNEXPECTED. Floor unchanged
# where it still holds (K35: rounded down); measured count in parens.
SAB_REACH_POP='tests/utf8/axis08_lookbehind_varwidth.rxt|^pattern .*\(\?<!|6'  # measured 8; the ill-formed SUBJECTS live in axis03/axis10, reached via the directory-wide harness target
#
# [ntriage triage, 2026-09-08] REACHED (reach:ok, pop 8 >= 6) BUT
# UNDETECTED, ZERO CHECKS FAILED, corpus:0fail/1656pass -- MEASURED, not
# assumed: no `.rxt` cell anywhere crosses {a negative lookbehind pattern}
# with {an ill-formed continuation-byte subject}. axis08's own `(?<!.)x`
# cells (this row's own SAB_REACH witness) run only against WELL-FORMED
# subjects ("ax", "zx", "\nx"); axis03/axis10 test ill-formed/surrogate
# subjects against `.`/`[^a]`/`\p{L}`, never a lookbehind. The two-cell
# cross product this row's own comment names (a lookbehind pattern x a
# malformed run) is EMPTY in the corpus today, verified by direct grep of
# every `(?<!` occurrence under tests/utf8/.
#
# ROUTE (b) IN THIS ROW'S OWN COMMENT ("reachable on a WELL-FORMED subject
# too through a mid-character startpos") IS NOW CLOSED BY CONSTRUCTION ON
# THE DEFAULT AXIS: [K50]'s caller-startpos guard (landed after this row
# was written) refuses any non-boundary `search_from` with
# PCREC_ERR_STARTPOS before ANY assertion logic runs -- MEASURED by
# inspecting an emitted utf8 artifact's `rx_search` prologue, which carries
# the guard unconditionally. Only `-fno-startpos-guard` still reaches route
# (b); the default build's sole remaining route is (a), the ill-formed
# continuation run, which the corpus does not exercise.
#
# THIS IS S-U6's EXACT SHAPE (docs/dev/known_issues.md; see that row's own
# UNDETECTED comment): a construct-level `SAB_REACH` proves the doorway is
# open while the BEHAVIOURAL cross product it needs has no witness, and the
# closing witness needs a real oracle answer this project does not have
# freehand. `\xc2\x80\x80x` under `PCRE2_UTF` with no `PCRE2_NO_UTF_CHECK`
# is refused by libpcre2 outright (a malformed-UTF8 error code, not a
# match/nomatch verdict) -- so the honest oracle for "how should pcrec's
# byte-level UTF-8 handling treat an ill-formed run under a lookbehind" is
# not a plain differential probe, it is the same UTF8-vs-libpcre2
# instrument S-U6 names as blocked on a corpus follow-up in the admin
# queue (an ill-formed-subject axis with its own measured libpcre2/
# PCRE2_MATCH_INVALID_UTF answers, axis03/axis10's own precedent). When
# that lands with a `(?<!` cell over an ill-formed run, this row flips NOW
# DETECTED and the expectation is re-measured and changed.
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='"        if (want != end - pos) return $_BACK_STEP_NONE;\n"'
SAB_AFTER='"        (void)want; (void)end;  /* SABOTAGE S-U9: length test deleted */\n"'
