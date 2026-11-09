# process — crit-sar1 (code), coordinator notes

- 10:21 freeze: SUBJECT 79619852e (lane/sar1), BASE c17a12722 = merge-base(lane/sar1, lane/sae1) per launcher
  (skill says merge-base main; launcher overrode: E1 reviewed separately). Rulings freeze: main 90ab55fd3
  (decisions.md/plan.md last touched 6a7fd9b04). D191 record decisions.md:10119.
- FREEZE NOTE: the launcher's three rulings (two §3.4 tie cells; utf8 over-bound reason mover; compound-part
  lever gap out of scope) have no repo record at the freeze (message only).
- Review tree worktrees/crit-sar1 built (nice make -j2, ~40 s). BASE = git archive export in round dir
  (I first created a second worktree crit-sar1-base by mistake — outside the launcher's "your review worktree";
  removed at once via wtprune --force --quiet-min 0; replaced by the archive export).
- Built tools: p2probe, drv.c + cmp1.sh (pcrec rx_search vs libpcre2, captures in full).
- Prebuilt sabotage binaries for S1915..S1921 + S463 (plants/), so the check lens can test "able to fail"
  without running make.
- Hook friction: no_cd_worktree.sh blocked three `cd X && ...` compound commands (two harmless). 

## Agents
| agent | model | launch | end | state |
|---|---|---|---|---|
| emit | opus | 10:25 | 10:37 | file complete, lanecheck DONE; ~950 compiles (over the 800 budget) |
| slot | opus | 10:25 | 10:34 | file complete, DONE |
| contract | opus | 10:25 | 10:29 | file complete, DONE |
| check | sonnet | 10:25 | 10:29 | file complete, DONE |
| verify | sonnet | 10:38 | 10:41 | verify.md complete (VERIFY COMPLETE), DONE |
All four critics returned in the launch turn (background launch still blocked the turn); every final reply was lost
("ended without delivering a report") — files carried everything, as the skill predicts. No resend, nudge or stall.

## Per lens
- emit: 2 raised (speed), 2 verified (EMIT-1 partly: qA{40} sub-claim refuted), 0 answer.
- slot: 5 raised (1 UB/maintenance, 2 doc, 1 simplification, 1 design suspected), 4 verified, 1 not verifiable (design).
- contract: 2 raised (doc), 2 verified. Answered the launcher's reason-order question (CONTRACT-2).
- check: 4 raised (maintenance), 3 verified, 1 needs a plant build.
- Overlaps: none. Time to draft: freeze 10:21 -> draft 10:43 (22 min).

## Freeze drift
- main moved 90ab55fd3 -> 9385168a2 mid-round: span_arms §12d (records the launcher's R1 rulings 1-2 and E2 rulings) and a
  [REQ-EMPTYCAT] plan note. No finding rests on the changed text. The FREEZE NOTE (rulings by message only) is now resolved.

## Blinding / leaks
- None noticed. I added the r3 sae1 review and its scratch dir to the denylist (BASE's own review; would bias the critics).

## Process observations
- Prebuilding every plant of the unit's S range into the round dir (one ~1-min build each, sequential, background) let the
  sonnet check lens classify all 8 plants as SILENT-MOVE/SAME by running witnesses in ~5 min, with no make by critics.
  Worth making standard for code rounds whose subject adds sabotage rows.
- A shared oracle wrapper (cmp1.sh: pcrec rx_search with capture spans vs libpcre2 p2probe) made the answers lens
  cheap: ~34k subject runs. The sae1 round had only p2probe + --emit-main (no captures).
- The no_cd_worktree hook blocked three of my `cd X && ...` commands (one harmless cd into the round dir).
- My mistake: created a second worktree (crit-sar1-base) for BASE; the launcher authorized only worktrees/crit-sar1.
  Removed at once via wtprune; git archive export is the documented BASE form (§3.2).
- wtprune --force on the review worktree saved a diff under worktrees/.wtprune.force/ (tool behaviour, gitignored).
- Scratch size 2.3G (plants/ + base-tree): the manager may delete plants/ after ruling.

## Proposed changes
1. SKILL §3.2 (code mode), append: "When the subject adds or re-aims sabotage rows, build each row's plant ONCE into
   `plants/<id>/` (apply SAB_BEFORE->SAB_AFTER to a `git archive` copy of SUBJECT, `nice make -j2`, record occurrences
   and rc in PLANT_STATUS) and name the dir in COMMON; the check lens classifies each plant against its own witness
   without running make (2026-11-09 sar1: 8 plants, 0 SAME, done in 5 min by a sonnet critic)."
2. COMMON template: ship `tools/cmp1.sh` (pcrec rx_search incl. capture spans vs libpcre2) in every code round whose
   subject can move answers; promote it to `tests/lib/` if the manager agrees (it is ~25 lines + a 15-line driver).
3. critics.md lesson: a tie rule accepted for answer-identical cells still needs a speed probe on its neighbour class
   (EMIT-1/EMIT-2 measured 4-7x losses from the accepted tie).

## Framework notes
- The coordinator pattern again ran fully file-based: 5 nested agents, 0 final replies delivered, 0 lost results.
- Round wall time 22 min for 4 critics + verifier: critics returning in the launch turn means monitoring cost is ~0;
  the costly part is coordinator-side preparation (oracle tool, plants), which pays off across critics.
