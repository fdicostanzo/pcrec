# S294 — [OPT-REQRUN-ENC] THE RUN'S `!bytekey` DECLINE REVERTS TO LEFTMOST
# (src/opt/reqbyte.c, `rn_scan_index`): under any encoding the byte-frequency
# prior is not keyed to (today, `-e utf8` alone), the necessary-run scan
# member goes back to the run's LEFTMOST byte instead of its RIGHTMOST — the
# pre-2026-09-26 rule, `rb_pick`'s own `!bytekey` fallback un-matched again.
# On a `-e utf8` run that opens mid-character the leftmost byte is a UTF-8
# LEAD BYTE, shared by every character in that script block, so the emitted
# `memchr` stops on nearly every byte of a non-Latin subject instead of the
# rare one the literal needs — the exact O-60 defect this row's own fix
# retired.
#
# THIS ROW'S WHOLE DETECTOR IS ONE STRUCTURAL ARM, and that is a property of
# what the mechanism does rather than a gap in the suite (S266's own
# precedent, one call site over). EVERY member of a necessary run is a byte
# every match must contain, so the `memchr`/`memcmp` pair is SOUND for
# whichever member is scanned and the choice can move a SPEED and nothing
# else: no differential, no oracle, no `.rxt` expectation and no corpus cell
# anywhere in this tree can see this plant. `corpus:0fail` beside a red
# `prechecks` arm is this row working.
#
# WHICH ARM. `tests/codegen/run_prechecks.sh` §3.6/§3.6r (the utf8 multi-byte
# witnesses `é`, `x(é|è)y`, `a\x{1F600}b`, `é@` — all four expect the
# RIGHTMOST member post-fix) and §4.9/§4.9b (the ruling's own acceptance:
# `é@` must stamp the byte `'@'`, never the shared lead byte 195; `Москва`'s
# picked byte must fall OUTSIDE the 0xC2-0xF4 lead-byte range) all revert to
# their PRE-fix (leftmost) values under this plant and fail. §4.9c (the
# `byte`-encoding control) is UNAFFECTED — `bytekey` is true there and this
# line never runs — which is the row's own proof that the plant is scoped to
# the `!bytekey` branch alone.
SAB_ID="S294-reqrun-enc-decline-leftmost"
SAB_FILE="src/opt/reqbyte.c"
SAB_SUITES="prechecks harness"
SAB_DESC="the necessary-run's !bytekey decline reverts to the run's leftmost member instead of its rightmost, so under -e utf8 the emitted memchr/memcmp targets a UTF-8 lead byte on a mid-character run — a pure cost regression with NO answer-level detector anywhere in this tree, since every member of a run is a byte every match must contain, which is why this is a STRUCTURAL row and why a green corpus arm beside a red prechecks arm is the row working"
SAB_DOC_FIGURE="tests/codegen/run_prechecks.sh is the whole detector: §3.6/§3.6r's four utf8 witnesses and §4.9/§4.9b (é@ -> RX_REQ_BYTE \"64\"; Москва outside 0xC2-0xF4) all report the reverted leftmost value. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S294."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree
# é@ under -e utf8 stamps RX_REQ_BYTE "64" (the rightmost member, '@'), not
# the leftmost UTF-8 lead byte 195.
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern "é@" && grep -q "^#define RX_REQ_BYTE \"64\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_RUN \"c3a940@2\"" "$REACH_TMP/o.c" && echo REACH-REQRUN-ENC-RIGHTMOST'
SAB_REACH_EXPECT="REACH-REQRUN-ENC-RIGHTMOST"
SAB_COUNT=1
SAB_BEFORE='    if (!bytekey) return r->n - 1;'
SAB_AFTER='    if (!bytekey) return 0;   /* SABOTAGE S294: the run decline reverted to leftmost */'
