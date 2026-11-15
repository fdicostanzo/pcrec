#!/usr/bin/env bash
# S711 ([MEMFN] R-12 VMLAZY, lane vmlrid) -- THE EIGHTH NAMED EXCEPTION'S OWN
# NEGATIVE CONTROL: a lazy-prefix change that RESEMBLES VMLAZY's NORMALIZE
# but moves the prefix by a NON-RULED amount must NOT be admitted by
# `run_recursion_identity.sh`'s `lazy_prefix_rewrite` bucket (kit manager
# ruling R1, R-12 VMLAZY, 2026-10-09; S273's shape for the fourth exception).
#
# THE PLANT is one token in the reach test after the capped prefix scan:
# `slot_values[LOW] + rmin*W` becomes `+ rmin*W - 1`. The scan, the cap, the
# member tests and the reach test's slot are all the ruled NORMALIZE
# spelling, so the region differs from the forward-rewritten pre-module
# region by that one offset and nothing else -- and admission is EXACT
# equality, so the pattern must land in `rdiff`, not in the bucket.
#
# AT STRIDE > 1 THE PLANT IS ANSWER-INVISIBLE (the cursor moves on the
# lattice entry + k*W, and entry + (rmin-1)*W < entry + rmin*W - 1 whenever
# W >= 2), so there the identity gate is the ONLY check that can see it:
# `(?:ab){3,}? --engine=vm` emits `slot_values[2] + 5` where the rewrite
# says `+ 6`. At stride 1 it is an ordinary wrong answer (a run one short of
# rmin passes): `a{2,}?[ab] --engine=vm` on "ab" answers `match 0 2` where
# python's re (and the clean tree) say no match.
#
# MECH CANNOT SCORE THE `recidentity` ARM (varland finding 7: the scratch
# tree is `git archive HEAD | tar -x`, no history for the gate's two pinned
# reference builds), so that arm reads SKIPPED-no-git-history by design. The
# row's OWN claim was validated MANUALLY instead: docs/dev/lanes/
# vmlmerge_report.md "§ recursion-identity bucket (lane vmlrid)" -- a
# scratch-built plant compiler's regions, put through the gate's own
# stamp_strip/prog_region/lazy_prefix_rewrite, admitted 0 of the 108
# call-free [vm] movers (the clean tree: 90 alone, the other 18 composed
# with the bref/ctx buckets), the witness diff being exactly the `+ 5`.
# [RECID-A] 2026-10-29: the gate's named exception buckets this row was a
# negative control for (the eighth exception, lazy_prefix_rewrite) were DELETED when comparison (A) was re-based onto
# a post-module commit (docs/dev/lanes/recida_report.md). The plant is still
# caught by the same arm, more simply: the plant's program region differs from
# the base's, and with no exception list to absorb a difference it lands in
# `REGION DIFFERS` and the gate is red. The row's claim stays "an unruled
# emission change is NOT admitted"; only the mechanism that could have admitted
# it is gone. (The arm still reads SKIPPED-no-git-history inside this matrix.)
# RE-AIMED 2026-11-14 (lane mechund) and the figure below re-stated 2026-11-15 (review r1 posts2 PLANTS-2): since
# rule (1) the pre-check masks the old vm_lazy_rmin_prefix.rxt:173 witness (`z(a){3,}?c?` stamps
# RX_REQ_RUN "7a616161@0"), so detection moved to the file's blocks at rxt:265-282, `(?:a{2,}?|x)[ab]` and
# `z(?:a{3,}?|x)c?`: on the emitted-C proxy of the plant ("ab", "abx" -> match 0 2; "zaac" -> match 0 4;
# "zaa" -> match 0 3) four cells flip nomatch -> match.
# REACH RE-AIMED (lane fixposts2d, 2026-11-15, review r4 fixposts2c SABROWS-1): the probe compiled
# `(?:ab){3,}?`, a stride-2 (answer-invisible) witness that is pre-check masked (RX_REQ_RUN
# "616261626162@5") and not in the target .rxt; it now compiles the two detection cells above and
# asserts both the planted reach line (`+ 2`, `+ 3`) and an UNMASKED pre-check (RX_REQ_RUN "none"),
# so a future masking of these cells reads UNREACHED instead of a puzzling UNDETECTED.
SAB_ID="S711-vmlazy-reach-one-byte-short"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="recidentity harness"
SAB_HARNESS_TARGET="tests/base/vm_lazy_rmin_prefix.rxt"
SAB_DESC='the VM cursor rung'"'"'s lazy-prefix reach test asks for rmin * stride - 1 bytes: answer-invisible at stride > 1 (lattice), a wrong answer at stride 1; the row proves the recursion-identity gate'"'"'s R-12 vmlazy-prefix bucket does not admit a resembling non-ruled prefix change'
SAB_DOC_FIGURE="recidentity: SKIPPED-no-git-history inside the mech matrix by construction (varland finding 7); the bucket's non-admission was HAND-MEASURED by lane vmlrid 2026-10-09 (docs/dev/lanes/vmlmerge_report.md, the vmlrid section). STALE FIGURE, SUPERSEDED: the vm_lazy_rmin_prefix.rxt:173 witness quoted at the 2026-10-09 measurement is masked by the pre-check now; the current detection cells are the rxt:265-282 blocks (RE-AIMED comment above), by emitted-C proxy only. Matrix figure at SUBJECT: OWED to the fixposts2d mechrows cloud run (scripts/cloudrun --owner main --kind mechrows --rows S474,S711,S3012 --name fixposts2d-mech). Re-run: bash tests/mech/run_sabotage_matrix.sh S711."
SAB_REACH='"$PCREC" -p rx --engine=vm --features all -o - --pattern "(?:a{2,}?|x)[ab]" | sed "s/^/W1 /"; "$PCREC" -p rx --engine=vm --features all -o - --pattern "z(?:a{3,}?|x)c?" | sed "s/^/W2 /"'
SAB_REACH_EXPECT='W1 #define RX_REQ_RUN "none"
slot_values[2] + 2) goto rx_fail;
W2 #define RX_REQ_RUN "none"
slot_values[2] + 3) goto rx_fail;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            vm_span_reach(v, low, lo_off);
        } else'
SAB_AFTER='            vm_span_reach(v, low, lo_off - 1);  /* SABOTAGE S711 */
        } else'
