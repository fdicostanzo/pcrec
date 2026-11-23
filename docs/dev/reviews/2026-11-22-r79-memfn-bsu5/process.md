# process.md — r79 memfn-bsu5 (code), coordinator
- 13:27 launched (team-lead = kit manager). SUBJECT lane/bsu5 = 28b2da326b7592cb021683f079183812360c6190; BASE = merge-base(lane/bsu5, lane/memfn-k1108) = b51fd80bd27d813f668bf6aed280d80e54866de2 (kit branch 41dd18a3a at freeze). main HEAD at freeze 89eaf2cf0.
- Rulings freeze: decisions.md/plan.md identical between SUBJECT and main (last change 6918cc42b on main, 2026-11-22 10:23). Records: D201 add. 5 decisions.md:10311 (SUBJECT); [BSPAN-CLANG-DIFF] plan.md row (SUBJECT); design block_span.md at SUBJECT (0eceaaee1 last touch).
- BLINDING LEAK (coordinator only): a `git grep BSPAN-CLANG-DIFF` over docs printed one line of docs/dev/lanes/bsu5_report.md:56 (denied): "[BSPAN-CLANG-DIFF] says this rides U5's C6 card: it does, as C6c. Main may want the follow-up item D201 add. 5 asked for to name C6c and the U6 ti..". Not passed to critics. COMMON now excludes the file in every grep.
- 13:28 review tree built UNLOCKED nice -j2 (~1 min, incremental from archive mtimes? no: clean worktree). BASE git-archive built clean in round dir base/.
- 13:33 cards.py plan (rc 0) -> .coord/plan.out; dry --cards C6,C6c JOBS=2 -> dry/ (216 cells gated, 22 texts, 88 exes, failures 0, rc 0).
- Coordinator inline check of CLAIM 1 (no emitted byte): 12 patterns x 4 flag sets, BASE vs SUBJECT build/pcrec, -o files + stderr + rc: 48 pairs, 0 diffs (.coord/c1/). The diff's only code outside tests is memfn/src/formhash.c (entries, test-only) + kit.h mf_form_entry (test struct); no caller of mf_form_hash/mf_form_entry outside formhash.c in src/, cli/, memfn/src.
- Plants (plants/<ID>/tree, SUBJECT archive + review build/, binaries deleted, rebuilt; fx = arm_fixtures driver): S2930 (row's own BEFORE/AFTER); PV32/PV16 (identifier-only edits of the B=32 / B=16 intrinsic prefix); PBODY (parens around the __body return); PV16b/PV32b (loop `<` -> `<=` at B=16 only / B=32 only).
- 13:36 four critics launched in one message, background, unnamed: fidelity (opus), meas (opus), check (sonnet), slot (opus). All four RETURNED IN THE LAUNCH TURN (foreground-like): check 4.5 min, fidelity 7.6 min, slot 7.6 min, meas 10.2 min; each file complete with CRITIC COMPLETE and lanecheck .done. Final replies all undeliverable ("ended without SubagentHandback"), as expected; files were the delivery. No resends, no nudges.
- 13:37-13:39 coordinator's run_finder.sh on SUBJECT, S2930, PV16b, PV32b, PBODY finished (all rc 0 but S2930 rc 1, 4 FAIL). check critic read them after.
- Findings raised: fidelity 5, meas 8, check 7 (1 SUSPECTED), slot 6 = 26 -> 18 consolidated (F1..F18). Overlaps: FIDELITY-5/SLOT-5; MEAS-8/SLOT-4; CHECK-7/SLOT-6; CHECK-5/FIDELITY-4; MEAS-6/FIDELITY-3; FIDELITY-2/MEAS-7 (a partial contradiction, resolved by reading regimes_of's docstring: one item, FIDELITY-2 PARTLY).
- Verification inline (all quote / one-call repros): 10 items, 9 HOLD, 1 PARTLY. No verifier agent (skill §6.2 allows inline when every CONFIRMED is a quote or one-call repro).
- Severity: claim-level F1 (claim 4), F2 (claim 3), F3 (claim 5); measurement F4-F10; doc/design F11-F18. No answer-level finding in the product (claim 1 holds; U5 is test/measurement code).
- Coordinator pre-finding: the B=16 coverage gap (F1) was found by the coordinator while building plants (13:36, before briefing). Not stated in any brief; the PV16b plant was listed neutrally. check found it independently from the plants (CHECK-1).
- Time to draft: ~4 min after the last critic (13:45 -> 13:50).

## Process observations
- Critics returning in the launch turn (all four) made lanewatch unnecessary; the round from launch to draft was ~15 min.
- Building plants for a CLAIM (not only for moved sabotage rows) paid: the plant set PV16b/PV32b turned claim 4 into a one-table answer. The identifier-only plants PV32/PV16 were initially intended as V-text edits; the hash's rename normalization made them SAME, which itself became CHECK-2's evidence.
- The coordinator's own `git grep` of a plan tag over docs/ printed one line of the denied lane report (blinding leak at coordinator level; COMMON's excludes would have prevented it). The coordinator's setup greps should carry COMMON's excludes from the first command.
- The lens table restricts `measurement` to D subjects; a C subject that carries a written-before-data rule record (a design inside code) needs it. It was the most productive lens of the round (8 findings).

## Proposed changes
1. Skill §4 lens table, `measurement` row: subject column `D` -> `D C`, text: "On C, when the code carries a rule record or a card definition written before data (r79 memfn-bsu5: 8 findings, the claim-3 refutation)."
2. Skill §3.2 (plants): "When a claim says a CHECK covers a population (a hash dep stales on X), prebuild one plant per renderer BRANCH the population runs (r79: the k 40 instance hashed only B = 32; every real site ran B = 16)."
3. Skill §3 freeze: "Setup greps over docs/ carry COMMON's excludes from the first command (r79: a plan-tag grep printed a denied lane-report line to the coordinator)."
4. Guide critics.md lessons: the three in review.md.

## Framework notes
- The coordinator pattern held at small cost: one coordinator, four critics returning in ~10 min, inline verification. The coordinator doing a zero-mover claim (claim 1) inline saved a critic seat for a lens with work (slot).
- Coordinator plant-building before briefing gives critics tools without results; the risk (coordinator foreknowledge biasing briefs) was managed by listing plants by EDIT, never by outcome.
