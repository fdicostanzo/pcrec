# process.md crit-memfn-sp1c
- 17:11 freeze: SUBJECT=3ecb647c7 BASE=7b671bc2c main=42fca94ec RULINGS_FREEZE=42fca94ec (decisions/plan)
- 17:12 worktree + BASE git-archive export at $R/base; build both nice make -j2 unlocked
- 17:20 COMMON written; lenses EMIT(opus) CONTRACT(opus) CHECK(sonnet) SLOT(opus); launching
- 17:13-17:24 four critics launched together (background, unnamed); ALL returned in the launch turn with complete files and lanecheck DONE markers (lanewatch rc=0). No resend, no nudge.
  - EMIT opus: 1 finding (maintenance), 1,409 compiles; dual-spelling plant with its own sabotage control; 0 movers.
  - CONTRACT opus: 5 findings (design/doc/maintenance); ~300 compiles + 3 kit drivers (40k+40k+200k random cases); disclosed one incidental read of a denied journal line (grep over memfn/ printed it; informed nothing). Lesson: COMMON's grep exclusion applied to git pathspecs but a plain `grep -rn` over memfn/ still reached the denied file.
  - CHECK sonnet: 5 findings (test gaps); ~230 compiles; consumer plants.
  - SLOT opus: 7 findings + standing (a)/(b); ~82 compiles.
  - Overlaps: TIE-row strict-order/after-walk (CONTRACT-3, SLOT-1, EMIT-1); rank_pos[0] assertion absent (CHECK-1, CONTRACT-2, SLOT-6); cube-mass wording (CONTRACT-4, SLOT-5).
- 17:25-17:30 verifier (sonnet) returned in the launch turn; verify.md complete, lanecheck DONE. 14 findings verified: 12 HOLDS, CHECK-2 PARTLY (p3a part REFUTED), CONTRACT-2 HOLDS (assertion absent; divergence unshown).
- 17:31 coordinator re-ran the crafted-input verdicts: the verifier's cmp.sh never deleted old outputs and printed MOVED when the plant binary FAILED; the CHECK-1 plants (both the critic's and verifier's) and CHECK-2's p3a are mostly LOUD internal errors (mf_define refusals), not silent moves. Silent: CHECK-1 only `(?i)enzyme -fmemfn-simd`; CHECK-2 p3b `x.*(?i)abcdef` (default, -e utf8). CHECK-4 re-run with fresh outputs: holds.
- 17:33 draft written ($R/review.md, critic texts + verify.md in review/). Freeze drift: none (main still 42fca94ec). Time freeze->draft ~22 min. Round compiles ~2,300 (EMIT 1,409; CONTRACT ~300; CHECK ~230; SLOT ~82; verifier ~60; coordinator ~40) — under the 3k cap. Nothing ran past 20:00.

## Process observations
- All five agents returned inside their launch turn with complete files and passing lanecheck markers; no resend, no nudge, no lost reply. The FILE+lanecheck+lanewatch pattern made the "nested reply lost" warning moot this round.
- The MF_TRACE pair + BASE archive built by the coordinator up front were used by EMIT and CONTRACT at once; no critic built its own trace pair.
- Plant-compare scripts conflated "plant compiler failed" with "bytes moved" (CHECK and verifier both). Only the coordinator's §6.2 re-run caught it: it downgraded CHECK-1 and CHECK-2's p3a from "silent, only a byte sweep sees" to "mostly loud".
- The verifier's "REFUTED" on CHECK-2 p3a was RIGHT in direction (the hello-world witness reacts) but for the wrong reason (it reacts by FAILING, i.e. loudly); the re-run rule earned its keep again.
- Blinding: CONTRACT read one denied journal line via a recursive grep over memfn/ (disclosed; informed nothing).
- Lens table: EMIT and CONTRACT both did byte-identity sweeps (overlap ~100 compiles); acceptable since each had a different method (dual plant vs direct kit differential). The standing questions on SLOT produced the round's most useful forward material (U-a..U-d).

## Proposed changes
1. SKILL §4 check-adequacy row / guide critics.md: "classify every plant compare as SAME / SILENT-MOVE (rc 0, bytes differ) / LOUD (rc != 0); delete outputs before each compare; a LOUD plant is caught by every corpus compile and is not a test gap." (Motivation: CHECK-1/CHECK-2 overclaimed silence; verifier cmp.sh printed MOVED on a failed compile.)
2. COMMON template denylist: "plain `grep -r` ignores git pathspecs: pass `--exclude=` for each denied file, or use `git grep` with the pathspecs." (Motivation: CONTRACT's incidental journal read.)
3. SKILL §6.2 verifier brief: the verifier's DELIVER should require, per plant claim, the plant compiler's exit code next to the byte verdict.

## Framework notes
- Coordinator pattern on a small no-mover unit: ~22 minutes freeze-to-draft, the manager untouched until hand-back. The cost driver was critic depth (EMIT 1,409 compiles), not coordination. For no-mover units the dual-spelling plant (old spelling recomputed beside the new, DUALBAD + reach counters) was the strongest single method — it turns "identical on N patterns" into "identical at K reaches of each replaced computation" with a sabotage control; worth naming in the emitted-vs-replaced lens text for refactor-shaped subjects.
