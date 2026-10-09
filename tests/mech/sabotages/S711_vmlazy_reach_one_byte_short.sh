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
SAB_ID="S711-vmlazy-reach-one-byte-short"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="recidentity harness"
SAB_HARNESS_TARGET="tests/base/vm_lazy_rmin_prefix.rxt"
SAB_DESC='the VM cursor rung'"'"'s lazy-prefix reach test asks for rmin * stride - 1 bytes: answer-invisible at stride > 1 (lattice), a wrong answer at stride 1; the row proves the recursion-identity gate'"'"'s R-12 vmlazy-prefix bucket does not admit a resembling non-ruled prefix change'
SAB_DOC_FIGURE="recidentity: SKIPPED-no-git-history inside the mech matrix by construction (varland finding 7); the bucket's non-admission was HAND-MEASURED by lane vmlrid 2026-10-09 (docs/dev/lanes/vmlmerge_report.md, the vmlrid section). MEASURED solo 2026-10-09 at ca278766: reach:ok(1/1), recidentity:SKIPPED-no-git-history, corpus:1fail/137pass -- DETECTED (SKIPPED -- no oracle), unexpected: 0 (the one harness failure, hand-confirmed: vm_lazy_rmin_prefix.rxt:173, z(a){3,}?c? on "zaac" (engine vm) answers match 0 4 where python re says nomatch -- a stride-1 run one short of rmin). Re-run: bash tests/mech/run_sabotage_matrix.sh S711."
SAB_REACH='"$PCREC" -p rx --engine=vm --features all -o - --pattern "(?:ab){3,}?"'
SAB_REACH_EXPECT='slot_values[2] + 6) goto rx_fail;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            vm_span_reach(v, low, lo_off);
        } else'
SAB_AFTER='            vm_span_reach(v, low, lo_off - 1);  /* SABOTAGE S711 */
        } else'
