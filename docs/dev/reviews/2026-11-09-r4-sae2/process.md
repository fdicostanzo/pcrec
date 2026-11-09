# crit-sae2 process record
- 10:21 freeze: SUBJECT 8e8960cf8 (lane/sae2), BASE c17a12722 (merge-base with lane/sae1); rulings frozen at main 90ab55fd3 (decisions/plan last touched 6a7fd9b04); design span_arms.md at 2f0ea0b69 (§12c not an ancestor of the subject; L2-only).
- Ruling records: D191 items 2-3 (decisions.md `## D191`) cover zero-width items stop cutting the run, all in E2, and REQ_BYTE "a byte every match CONSUMES". FREEZE NOTES: R-a (A_EMPTY moved from stage 2a into E2) and R-c (E2 owns the spec wording) — no record found in D191 or span_arms §8 at the freeze (§8's E2 row lists "T3 E-4, and E-5"; dependency "stage 2a (as E1)"); by message only. R-d wording: launcher said "contains", D191 says "consumes" — flagged to the contract lens.
- Builds: subject + base (archive export, round dir) nice make -j2, rc 0; five plant builds S1925-S1929 (incremental from subject build copy), rc 0, plant effect spot-checked on S1925.
- Smoke (coordinator, before briefing): ab\Kcd facts differ base/subject (whole run cd -> abcd). Did not pass result to critics; the contract lens gets the manager's question as asked.
- Base worktree created then removed in favour of an archive export (mandate names one worktree).
- 10:24 launched 4 critics (emitted opus, contract opus, checks sonnet, slots opus), background, unnamed. ALL returned in the launch turn (10:28-10:33; 4-9 min each); all files complete, all lanecheck DONE. No resends/nudges.
- Process: slots critic REWROTE its own deliver file (relative report path, nonempty: all) — harmless but a critic edited a coordinator file. emitted critic overran the compile budget by ~150 (declared).
- 10:35 coordinator plant E5ARM (E-5 row arm dropped): [facts-arm] ZP lists 78797a6162 under restore=zero -> the section's expectation 78797a goes red; checks-1 resolved as "caught by [facts-arm], no mech row".
- Rulings re-diffed at critic return: main still 90ab55fd3, no drift.
- 10:37 verifier (sonnet) launched; returned in the launch turn (~4 min), verify.md complete, VERIFY COMPLETE, lanecheck DONE. All CONFIRMED HOLD; checks-1 PARTLY; checks-4 REFUTED as worded (the refutation rests on the existing ms line, not a crafted input; re-read, holds).
- Draft written ~10:45. Time freeze -> draft ~25 min. Rulings re-diffed at hand-back: no drift.

## Per lens
| lens | raised | verified | severity | overlaps |
|---|---|---|---|---|
| emitted | 2 | 2 HOLD | speed (missed fact), doc | EMITTED-2 = SLOTS-3 |
| contract | 5 (1 + 2a-d) | 5 HOLD | doc | CONTRACT-1 = SLOTS-5 |
| checks | 4 | 1 PARTLY, 1 REFUTED, 2 unverified (SUSPECTED) | doc/maintenance | — |
| slots | 6 | 6 HOLD | doc/maintenance | as above |

## Process observations
- Every critic and the verifier returned within the launch turn (4-9 min): narrow single-question briefs plus prebuilt binaries and a ready libpcre2 bounds script made probing cheap. Building the PLANTED compilers in the coordinator's build step (incremental, ~1 min each) let the read-only check lens classify plants without `make`; that is the first round where the check lens did plant compares without a rule bend.
- The slots critic overwrote its deliver file (relative path, `nonempty: all`). Harmless, but a critic wrote a coordinator file.
- Two lenses independently found the REQ_BYTE wording gap (contract, slots) and the `\K`-can-fail mislabel (emitted, slots): the launcher's REQ_BYTE question was both a direct question to one lens and discoverable by another.
- I first created a second git worktree for BASE, then replaced it with an archive export: the mandate names ONE review worktree.

## Proposed changes
1. Skill §3.2 (code mode): "When the diff adds sabotage rows, build each row's PLANTED compiler in the round dir as part of the round's build (archive export + copy of the subject's build/, apply SAB_BEFORE->SAB_AFTER, incremental `nice make -j2`), so the check lens classifies plants without running make (crit-sae2: 5 plants + 1 coordinator plant in ~6 min)." Motivation: the check lens's plant-compare duty conflicts with "critics never run make".
2. Skill §5 COMMON template: "Ship a ready oracle script (libpcre2 bounds via ctypes) in the round dir; python `re` is no oracle for `\K`." Motivation: all four critics used it immediately.
3. Skill §5: "Make DELIVER files read-only (chmod a-w) after writing; a critic rewrote its own (crit-sae2)."
4. Skill §5/COMMON: "Quote each ruling from its RECORD verbatim beside the launcher's restatement; flag a difference to the contract lens" (R-d contains vs consumes).

## Framework notes
- The coordinator pattern fit a small code unit well: one turn of fan-out, one of verification, draft in ~25 min; the manager's context saw none of the probe output. The coordinator's own pre-build of plants is the piece that made a read-only round able to test checks — a capability the manager could not have delegated without a writer lane.
