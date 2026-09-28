#!/usr/bin/env bash
# S329 — [FIND-TIE] THE RUN READER'S DATA TIE REVERTS TO LEFTMOST
# (src/core/findings.c, `pcrec_find_run_scan_index`): with a real byte-rate
# in hand (not the NONE case S294 already covers), a tie among two or more
# run members sharing the argmin goes back to the LEFTMOST of them instead
# of the RIGHTMOST — the one PICK reader in this file whose data-tie order
# disagreed with its own NONE order until 2026-09-28's fix. `pcrec_find_set_
# pick`'s own candidate order (`[rightmost, 255..0]`) is UNTOUCHED by this
# plant and stays consistent; only the run's scan-member pick reverts.
#
# On the shipped ASCII-only `log`/`weblog` bundles under `-e utf8`, every
# byte >= 0x80 ties at the 2 ppm floor, so a run that opens mid-character
# ties its LEAD byte against its own CONTINUATION bytes — and this plant
# picks the lead byte again, the exact `[OPT-REQRUN-ENC]`/O-60 defect one
# call down from the fallback S294 guards. `[a-z]+@é` under `-e utf8
# --analysis weblog` reverts from `RX_REQ_BYTE "169"` (é's trailing byte)
# back to `"195"` (0xC3, the shared UTF-8 lead byte).
#
# THIS ROW'S WHOLE DETECTOR IS ONE STRUCTURAL ARM, S294's own precedent one
# tie-rule over. Every member of a necessary run is a byte every match must
# contain, so the emitted `memchr`/`memcmp` pair is SOUND for whichever
# member is scanned and the choice can move only a SPEED: no differential,
# no oracle, no `.rxt` expectation and no corpus cell in this tree can see
# this plant. `corpus:0fail` beside a red `prechecks` arm is this row
# working.
#
# WHICH ARM. `tests/codegen/run_prechecks.sh` §4.9c (the `byte`-encoding
# control) STAYS GREEN under this plant — `é@`'s tied pair (0xC3/0xA9) is a
# DATA tie there too, and the row asserts the RIGHTMOST of it (169); the
# plant is not scoped to `-e utf8` and reverts that control too, so §4.9c
# ALSO reddens. §4.10a/§4.10b/§4.10c (`[FIND-TIE]`'s own witnesses, the
# `weblog`/`log` bundles) revert to their pre-fix lead-byte values and fail.
SAB_ID="S329-find-run-scan-data-tie-leftmost"
SAB_FILE="src/core/findings.c"
SAB_SUITES="prechecks harness"
SAB_DESC="the necessary run's PICK reader (pcrec_find_run_scan_index) reverts a DATA tie (a real byte-rate, two or more run members sharing the argmin) to the leftmost candidate instead of the reader's own NONE answer's rightmost — the one PICK reader in findings.c whose two arms disagreed until [FIND-TIE]; a pure cost regression with NO answer-level detector anywhere in this tree, since every member of a run is a byte every match must contain, which is why a green corpus arm beside a red prechecks arm is the row working"
SAB_DOC_FIGURE="tests/codegen/run_prechecks.sh is the whole detector: §4.9c (the byte-encoding tie control, é@ -> RX_REQ_BYTE \"195\" instead of \"169\") and §4.10a/§4.10b/§4.10c ([FIND-TIE]'s own utf8 weblog/log witnesses) all report the reverted leftmost value. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S329."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree
# [a-z]+@é under -e utf8 --analysis weblog stamps RX_REQ_BYTE "169" (é's
# trailing byte), not the tied pair's leftmost lead byte 195.
SAB_REACH='"$PCREC" --features all -p rx -e utf8 --analysis weblog -o "$REACH_TMP/o.c" --pattern "[a-z]+@é" && grep -q "^#define RX_REQ_BYTE \"169\"" "$REACH_TMP/o.c" && echo REACH-FIND-RUN-SCAN-DATA-TIE-RIGHTMOST'
SAB_REACH_EXPECT="REACH-FIND-RUN-SCAN-DATA-TIE-RIGHTMOST"
SAB_COUNT=1
SAB_BEFORE='    for (i = 0; i < n; i++) cand[i] = bytes[n - 1 - i];
    return n - 1 - pcrec_find_pick(rate, cand, n, 0);'
SAB_AFTER='    for (i = 0; i < n; i++) cand[i] = bytes[i];
    return pcrec_find_pick(rate, cand, n, n - 1);   /* SABOTAGE S329: data tie reverts to leftmost */'
