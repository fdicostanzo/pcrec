#!/usr/bin/env bash
# S3263 ([COVER-CAP] stage 2, lane covs2c; R-45 witness row (b), r45read_report.md W12 + C9;
# span4k_report.md "Witness row (b) spec"; cover_cap.md §11.1 B5) -- THE KIT'S PROOF RANGE
# ENDS SHORT OF THE COVER'S AFTER-CONTEXT, AND ONLY pcrec's B5 IS LEFT TO SAY SO.
#
# The kit sizes the proof range it returns to one past the statement (`end` in
# memfn/src/compose.c). The plant cuts it to `last_s + 1` (the cut of the kit's own row (a),
# tests/memfn/run_proof.sh S3242) AND deletes the kit's self-check R-short by its message text
# (SAB_FILE2): one plant cannot witness both checks, because R-short fires first and B5 is then
# never reached (C9). On `[0-9a-f]{32}` with nothing after it (an after-UNSTATED cover at the
# default width 32: k = 32, last_s = 31) the range then ends at offset 31, below k + 1 = 33, and
# pcrec's B5 (`pcrec_cover_proof_diff`, src/gen/known.c) must fail the compile with its named
# internal error "the kit's proof range ends at offset 31, before the cover's after-context at
# 32". With the after side STATED (last_s = 32) the cut range reaches k + 1 and B5 stays silent,
# so the witness must be after-unstated: B5's text firing under the plant is itself that fact.
#
# Detector: the kitproof arm (tests/kitproof/run_cover.sh): the `[0-9a-f]{32}` answer rows'
# harness compile fails ("the harness compile failed"). The matrix has no text field, so the
# arm's red is any failed compile; THAT the failure is B5's text was hand-probed on a planted
# tree (SAB_DOC_FIGURE). Without B5 nothing else refuses: the comparison would run over the
# shortened range silently.
#
# REACH: on the clean tree the witness is a cover (REACH-WHY=[cover]) at the shipped default
# width 32 (--list-limits), its cover record k = 32 with an exact stretch of 32 (the facts
# listing's cover row `cover 32 32`). The REACH does NOT show the after side unstated: the
# listing prints the same row for `\b[0-9a-f]{32}\b`, whose after side is stated (review r32
# F20). That gap cannot hide a miss: a witness that gained a stated after side would leave B5
# silent and the row would read UNDETECTED, loudly.
SAB_ID='S3263-cover-proof-range-short'
SAB_FILE='memfn/src/compose.c'
SAB_SUITES='kitproof'
SAB_DESC='the kit'"'"'s proof range is cut to last_s + 1 and its R-short self-check deleted: an after-unstated cover at the default width must fail the compile on pcrec'"'"'s B5 short-range internal error'
SAB_DOC_FIGURE='HAND-PROBED by lane covs2c 2026-11-16 on a planted tree (both plants): its compiler, given the pattern [0-9a-f]{32}, fails with "internal error: the kit'"'"'s proof range ends at offset 31, before the cover'"'"'s after-context at 32 (src/gen/known.c)" (docs/dev/lanes/covs2c_report.md THE ROWS). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3263.'
SAB_REACH='"$PCREC" --list-limits | grep -q "^PCREC_DEFAULT_WINDOW_SEARCH_WIDTH	32	" && "$PCREC" --features all --emit-facts --pattern "[0-9a-f]{32}" | grep -q "^byte	cover	32	32	" && echo REACH-WIDTH-32-K-32 && bash "$TREE/tests/kitproof/reach.sh" "$TREE" - "[0-9a-f]{32}" --why'
SAB_REACH_EXPECT='REACH-WIDTH-32-K-32
REACH-COVER
REACH-WHY=[cover]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    long end = last_s + 2 > last_t + 1 ? last_s + 2 : last_t + 1;'
SAB_AFTER='    long end = last_s + 1;   /* SABOTAGE S3263 */'
SAB_FILE2='memfn/src/compose.c'
SAB_COUNT2=1
SAB_BEFORE2='    if (end < proof_min_end(last_s))
        return "the proof range ends before the statement'"'"'s following offset";'
SAB_AFTER2='    /* SABOTAGE S3263: R-short deleted */'
