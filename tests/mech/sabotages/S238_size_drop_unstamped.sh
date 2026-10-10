# S238 — [K53-SELRETRY] THE DROP RUNG FIRES AND SAYS NOTHING.
#
# S237's sibling in the other direction, and the more dangerous of the two.
# The rung still works — the artifact ships, every answer is right — but
# `<PREFIX>_ENGINE_SEL` falls through to `"selected"`, so an artifact that is
# measurably slower than an unconstrained build (it pays `<prefix>_match`'s
# reverse pass, ~50% of the DFA's time on a matching subject) is
# indistinguishable from a compile where nothing unusual happened.
#
# THAT IS THE EXACT GAP [LIM-1] CLOSED FOR THE OTHER RUNG, one budget over
# (`docs/spec/match_api.md` §6.3's own account of it), and it is why this row
# is separate from S237 rather than a second hunk of it: S237's symptom is a
# REFUSAL and S238's is a silence, so their detectors are different lines. A
# check reading only "did it compile" passes S238 completely.
#
# WHAT SEES IT: `tests/codegen/run_anchored_match.sh` §6a's `wrongsel` arm,
# which asserts the value on each of the three witnesses that took the rung.
# §5's census ALSO fires, and by a different mechanism worth naming — the
# size-drop bucket is keyed on this very stamp, so with it gone the eight
# corpus artifacts fall back into the state-cap OVERFLOW bucket by
# elimination, breaking that bucket's ceiling of 0. The census was written
# that way for this reason: a bucket reached by elimination is one that will
# one day hold something else.
SAB_ID="S238-size-drop-unstamped"
SAB_FILE="src/core/compile.c"
SAB_SUITES="anchoredmatch"
SAB_DESC="an artifact rescued by the optional-contributor drop rung stamps ENGINE_SEL \"selected\", so a caller cannot tell it from an unremarkable compile and the census's size-drop bucket empties into the state-cap overflow one"
SAB_DOC_FIGURE="docs/spec/match_api.md 6.3's ENGINE_SEL table (§6.3.3¶3); docs/spec/limits.md 8's 'The optional-contributor drop'"
SAB_COUNT=2
# REACH: the row's detector rests on the drop rung producing this value at
# all. Same probe as S237 and for the same reason — if `\p{L}` stops taking
# the rung, both rows are certifying nothing.
SAB_REACH='"$PCREC" --features unicode-props -e utf8 -p rx -o - --pattern "\p{L}" | grep -o "size-cap-retry" | head -1'
SAB_REACH_EXPECT='size-cap-retry'
# [TOUR-5] (2026-09-20) RE-AIMED, SAME INTENT, SAME ONE LINE REMOVED. The
# ladder moved out of `pcrec_select_engine` into `esel_of` (r61 F2), so `fit.`
# became `fit->` and the arm gained its own `: ` continuation column. The plant
# still deletes exactly the `size_drop_rung` disjunct and nothing else, so a
# drop-rung-rescued artifact falls through to `!cx->dfa_disabled ?
# ESEL_SELECTED` — the same "selected" silence the header describes.
# [DEC-FALLBACK] B5 (lane decfbB5, 2026-10-08) RE-AIMED, INTENT RE-VERIFIED.
# `esel_of`'s ternary is gone: ENGINE_SEL is the attribution walk's read of
# the fired T1 rows' cells, so "the drop rung does not reach the stamp" is
# now the two optional-contributor drop rows ([K53-SELRETRY]'s
# `drop-anchored` and `drop-premul`, SAB_COUNT=2: their cell lines are
# identical) carrying PASS cells. They still fire and still print their
# notes, but attribute nothing, so a drop-rung-rescued artifact falls
# through the walk to `selected`: the same silence. (`drop-prefilter`'s cell
# stays; S422/S423 own the [PF-DROP] rung.)
SAB_BEFORE='      .cells = { { ESEL_SIZE_CAP_RETRY, ESEL_SIZE_CAP_RETRY }, PFLW_PASS, NULL },'
SAB_AFTER='      .cells = { { ESEL_PASS, ESEL_PASS }, PFLW_PASS, NULL },   /* SABOTAGE S238 */'
