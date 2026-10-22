#!/usr/bin/env bash
# S693 ([MEMFN] R4e'.0b, lane r4e0b) -- THE ROUTING SHIPS WITHOUT ITS ABI BUMP.
#
# WHAT IT BREAKS. A kit change that moves an emitted byte is a pcrec abi
# event in the same commit (memfn/CLAUDE.md, D76/D94): R4e'.0b moved every
# offset-skip/pre-check function's text and bumped PCREC_ARTIFACT_ABI 69 ->
# 70 (69 is decattr's event, landed first). The plant puts the number back to
# the parent's, so a routed artifact claims the parent's abi. RE-ANCHORED
# 2026-10-09 (lane rq3land): [MEMFN] RQ-3 landed on top as 70 -> 71, so the
# number is 71 and the plant reverts it to 70; the intent (the latest event's
# bump is missing, the artifact names its parent's abi) and the detector are
# unchanged.
#
# WHERE IT IS SEEN. tests/codegen/run_codegen_tests.sh's [DD-14.FB] check
# reads rx_info.abi off a VM and a DFA artifact against ABI_EXPECT (arm
# codegen); an artifact's own shared-block guard reads the same number.
#
# RE-AIMED 2026-10-09 (lane vmlazy, R-12's VMLAZY normalization, abi 70 -> 72;
# 71 is RQ-3's): the row now plants the number this tree's own bump left behind
# (72 back to 70). Same detector, same arm. The manager re-aims it at merge
# if RQ-3's 71 lands in between (the AFTER value is then 71).
#
# RE-AIMED 2026-10-09 (lane vmlmerge, the merge of main's RQ-3 71 under this
# branch's 72): AFTER is 71, the parent's number, so the plant again names
# the latest event's parent (the row's convention); same detector, same arm.
#
# RE-AIMED 2026-10-10 (lane revbuild, [OPT-REVEND] L2, abi 72 -> 73, landed
# on R-12's 72): AFTER is 72, the parent's number; same detector, same arm.
#
# RE-AIMED 2026-10-10 (lane slbuild, [START-LANDING] SL2, abi 73 -> 74): AFTER
# is 73, the parent's number; same detector, same arm.
#
# RE-AIMED 2026-10-11 (lane rlhbuild, [REQ-HANDOFF-L1], abi 74 -> 75): AFTER
# is 74, the parent's number; same detector, same arm.
#
# RE-AIMED 2026-10-11 (lane seambuild, [LOSS-REVIEW] candidate 1, abi 75 ->
# 76): AFTER is 75, the parent's number; same detector, same arm.
#
# RE-AIMED 2026-10-12 (lane cpb4, [COMPOUND] B4, abi 76 -> 77): AFTER is 76,
# the parent's number; same detector, same arm.
#
# RE-AIMED 2026-10-12 (lane b3build/b3land, D164 B3, abi 77 -> 78): AFTER is 77, the
# parent's number; same detector, same arm.
#
# RE-AIMED 2026-10-17 (lane rpunion, [WINDOW-E1] the knowledge-stamp union,
# abi 78 -> 79): AFTER is 78, the parent's number; same detector, same arm.
#
# RE-AIMED 2026-10-18 (lane e1, [ENTRY-TABLE] E1 the part-layout controls,
# abi 79 -> 80): AFTER is 79, the parent's number; same detector, same arm.
#
# RE-AIMED 2026-10-19 (lane ctxbuild, [DD-11.5] P2c the (?m) fold, abi 80 -> 81):
# AFTER is 80, the parent's number; same detector, same arm.
# RE-AIMED 2026-10-21 (lane m0build, [MEASURE-SET] M0, abi 81 -> 82): AFTER is
# 81, the parent's number; same detector, same arm.
# RE-AIMED 2026-10-22 (lane corefix, K128/K129, abi 82 -> 87): AFTER is 82,
# the parent's number; same detector, same arm.
SAB_ID="S693-abi-not-bumped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="PCREC_ARTIFACT_ABI stays 71 (the parent's) while the VMLAZY normalization moves the lazy cursor prefix, so rx_info.abi misnames the artifact"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0b 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0b_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S693."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#define PCREC_ARTIFACT_ABI 87'
SAB_AFTER='#define PCREC_ARTIFACT_ABI 82   /* SABOTAGE S693 */'
