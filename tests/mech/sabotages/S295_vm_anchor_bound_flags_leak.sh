# S295 — [K68] PCREC_NO_VM_ANCHOR_BOUND DROPPED BACK OUT OF THE
# rx_info.flags STRATEGY-DENIAL MASK (src/gen/emit_dfa.c).
#
# K68's fix added the three [OPTLOOP.1] batch-1 whole-window pre-check bits
# (PCREC_NO_VM_ANCHOR_BOUND/PCREC_NO_END_WINDOW/PCREC_NO_REQ_BYTE, bits
# 28-30) to `emit_info_def`'s `strategy_denials` mask, on the same grounds
# every other member of that mask joined it: each is ANSWER-IDENTITY-
# PRESERVING (docs/dev/known_issues.md K68; lib/pcrec.h's own comment on
# each bit), so denying it must not make two identically-behaving artifacts
# differ in their reflection surface. This plant drops ONE of the three,
# `PCREC_NO_VM_ANCHOR_BOUND`, back out — the S65/S67 shape (a mask member
# removed) applied to K68's own bits, one bit rather than the whole family,
# to prove the detector localises to the SPECIFIC bit dropped rather than to
# "the mask changed somewhere".
#
# WHAT ACTUALLY HAPPENS: the raw `pcrec_options.flags` word's bit 28 now
# leaks straight into `rx_info.flags` whenever `-fno-vm-anchor-bound` is
# passed — on EVERY artifact, including K68's own repro
# (`/user|/users`, which has no `^`/`\A`/`\G` for the analysis to act on at
# all) and every `abc$`-shaped witness where only PCREC_NO_END_WINDOW is
# engaged. Every existing correctness check in the tree is silent to this
# (the match behaviour is genuinely unchanged — the .rxt corpus, both
# oracles and the vm differential all still agree), which is exactly why
# this is a structural row and not an answer-level one: tests/codegen/
# run_prechecks.sh §6 is the only thing that reads `rx_info.flags` as a
# NUMBER for these three bits rather than trusting the mask is complete.
SAB_ID="S295-vm-anchor-bound-flags-leak"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks harness"
SAB_DESC="PCREC_NO_VM_ANCHOR_BOUND dropped from emit_info_def's strategy_denials mask, so -fno-vm-anchor-bound leaks into the emitted rx_info.flags literal on every artifact even though the axis changes no match behavior -- two artifacts that answer identically now differ in their reflection surface over a knob with no observable effect, the exact K68 defect the fix retires"
SAB_DOC_FIGURE="tests/codegen/run_prechecks.sh section 6 is the detector: all three of its -fno-vm-anchor-bound rows fail, reporting .flags = 268435456/268435458-shaped values against the expected baseline, while its -fno-end-window and -fno-req-byte rows (the other two bits, still masked) stay green -- localising the plant to the ONE bit it dropped. Measured on the clean tree at 301 passed / 0 failed. The harness arm is expected to stay GREEN: the leak moves no answer in either direction, which is exactly why this is a structural row. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S295."
# [MECH-REACH] THE PROBE says the MASK MECHANISM still applies to this bit on
# the clean tree: a forced-VM ^-anchored witness under -fno-vm-anchor-bound
# reads the SAME .flags as the undenied baseline (0), which is only true
# while the bit is masked. A later change that stopped masking it, or that
# stopped emitting .flags at all, must read UNREACHED and not green.
SAB_REACH='"$PCREC" -p rx --engine=vm -o "$REACH_TMP/base.c" --pattern "^abc" && "$PCREC" -p rx --engine=vm -fno-vm-anchor-bound -o "$REACH_TMP/deny.c" --pattern "^abc" && [ "$(sed -n "s/^ *\\.flags = \\([0-9]*\\)ULL,\$/\\1/p" "$REACH_TMP/base.c")" = "$(sed -n "s/^ *\\.flags = \\([0-9]*\\)ULL,\$/\\1/p" "$REACH_TMP/deny.c")" ] && echo REACH-VM-ANCHOR-BOUND-MASKED'
SAB_REACH_EXPECT="REACH-VM-ANCHOR-BOUND-MASKED"
SAB_COUNT=1
SAB_BEFORE='                                          PCREC_NO_VM_ANCHOR_BOUND | PCREC_NO_END_WINDOW |
                                          PCREC_NO_REQ_BYTE;'
SAB_AFTER='                                          /* SABOTAGE S295: PCREC_NO_VM_ANCHOR_BOUND
                                           * dropped from the mask -- it now
                                           * leaks into rx_info.flags */
                                          PCREC_NO_END_WINDOW |
                                          PCREC_NO_REQ_BYTE;'
