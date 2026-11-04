# process: crit-memfn-sp1b (code)
- coordinator start 2026-11-04 09:50 EST (opus)
- SUBJECT cca35ffd1f7756cc3a0c719bacea34631c087933 (lane/memfn-sp1b); BASE b0f3d033902198f5228022d61bf2b9ab54b6c48b (= main HEAD at freeze)
- rulings freeze: main's last decisions.md/plan.md commit 7ac40695ef11f07d4e8afe410f43964f8908d531
- review worktree worktrees/crit-memfn-sp1b; build nice make -j2 unlocked
- 09:58 launched emit(opus) contract(opus) check(sonnet) house(sonnet); all four returned in the launch turn (~2-7 min)
- 10:01 all four files complete + lanecheck .done (house 09:54, check 09:58, contract 09:59, emit 10:00). No resends, no nudges.
  - emit (opus): 1 finding (EMIT-1 kit_pos zero value = full cube, maintenance); 1500 compiles at cap (220 void: --analysis lookup misuse); zero byte/REACH/whole-trace diffs.
  - contract (opus): 7 (C-1 stale anchors S1094/S1096 = test-codegen red; C-2 ratchet recipes blind; C-3 kit.h over-claim; C-4 LEFTMOST==LOWER; C-5 window_site §2.1 lacks row; C-6/C-7 suspected); 76 compiles.
  - check (sonnet): 5 (CHECK-1 = C-1 independently; CHECK-2 per-position-cap plant green; CHECK-3 = C-2 partly; CHECK-4 S458 reach parity; CHECK-5 run_finder double count); ~12 compiles + plant builds.
  - house (sonnet): 6 (cube-vs-set rebuilds, call-shape sugar, enum location, CLAUDE.md headroom 56 B).
  - Overlap: stale anchors found by contract AND check; ratchet recipe by contract, check, house; cube/set spelling by contract (C-6) and house (H-1).
- 10:02 verifier (sonnet) launched; 10:04 verify.md complete (VERIFY COMPLETE, .done): 7 HOLDS, 2 PARTLY (CONTRACT-6/HOUSE-1: pcrec guarantees canonical, kit does not; CHECK-5: 3 FAILs not 2), 1 REFUTED (HOUSE-6, limit is 12288). No REFUTED rested on a crafted input (HOUSE-6 is a wc -c), so no re-run needed.
- 10:05 FREEZE DRIFT check: lane branch unmoved; main gained D187 (675ae40d5, owner to the kit, 2026-11-04) naming 1b's non-normal-cube gap and ruling its first step: reported in the draft; R7/R8 dispositions read it. plan.md diff = [RECID-A] only; span_pick/roadmap/window_site unchanged BASE..main.
- 10:12 draft written; review worktree removed (wtprune --force --quiet-min 1: REMOVED). Main tree status unchanged from the round start.
- Compile spend: emit 1500 (cap; 220 void) + 12 setup, contract 76, check ~12, verifier 0, coordinator 4: ~1600 of the ~3k cap. Builds: review tree nice make -j2 unlocked (~3 min); BASE built from `git archive` into the round dir (scratch, not a second worktree: the mandate allowed only the one review worktree); MF_TRACE pcrec pairs via tests/memfn/mk_mftrace_lib.sh into bin/ (~1 min).
- Blinding: no leak noticed. The critics never cited the lane report; the denylist named docs/dev/history (the subject touched the lanes-index history file).
- Time: freeze 09:50 -> draft 10:12 (22 min).

## Process observations
- Every critic and the verifier returned in the launch turn with complete files and a lanecheck DONE; no resends or nudges. Nested final replies were all lost (as expected); files carried everything.
- The highest-value finding (stale anchors, a red test-codegen) came from TWO lenses by two methods (the repo's anchor checker; a hand counter). The lane re-anchored only the plants that named a deleted FUNCTION; the missed ones quoted a function BODY.
- emit hit its 1,500 cap exactly; 220 compiles were void on a misread `--analysis` lookup (DIR/NAME.rxt, the defined name = file name). Briefing the rate regimes would have saved them.
- The emitted C embeds its own output basename (`#include "<name>.h"`); the COMMON note (same basename, two dirs) prevented false movers from the first probe.
- Freeze drift mattered this time: D187 landed mid-round ABOUT this subject (from the lane's own discovery). The skill's freeze diff caught it; two dispositions turn on it.
- Over-staffing: house found little that the contract lens did not (HOUSE-1 = CONTRACT-6; HOUSE-5 = CONTRACT-2's pointer). For a small kit refactor with a design of record, house could have folded into check.

## Proposed changes
1. Skill §5, the check-adequacy lens row or the COMMON template: "Code mode: when the subject deletes or respells kit or src text, the check lens runs `python3 -I scripts/m6read_check_sab_anchors.py` against the review tree (read-only, seconds); a plant may quote a body, not a name." (Observation: S1094/S1096 missed by the lane, a red gate.)
2. COMMON template, rate-sensitive subjects: name the regimes and how to reach each (default prior; `-e utf8` = NONE; `--analysis uniform` = every mass ties; a real bundle `-I DIR --analysis NAME` with DIR/NAME.rxt). (Observation: 220 void compiles.)
3. COMMON template, code mode: "the emitted C names its output basename: compare BASE/SUBJECT under the same basename in two dirs." (Observation: it saved a false mover on the coordinator's own smoke test.)
4. Skill §3 step 2: "When the promise includes MFTRACE REACH equality, build BASE and SUBJECT MF_TRACE pcrec pairs via tests/memfn/mk_mftrace_lib.sh + one gcc link into bin/; a BASE tree may be a `git archive` export in the round dir (no second worktree)." (Observation: ~1 min. It met the one-worktree mandate.)

## Framework notes
- The coordinator pattern cost the launcher one message in and one out for a 4-critic + verifier round, in 22 minutes. Two of the critics' main findings were independently duplicated across lenses; consolidation happened here, not in the launcher's context.
- Mid-round rulings ABOUT the subject (D187) are the case where the coordinator's freeze diff earns its keep: the coordinator can re-read dispositions against the new ruling without breaking the critics' blindness (they finished first).
