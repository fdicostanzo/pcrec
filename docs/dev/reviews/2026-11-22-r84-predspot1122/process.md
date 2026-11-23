# process — r84 predspot1122 (coordinator, opus)
Setup: 18:55-19:01 (freeze, mirror, evidence re-runs ~2 min total, COMMON + 5 briefs, pre-created files).
Critics launched 19:01, all opus, background, unnamed; all five returned in the launch turn (19:08-19:12):
- ruling   a7e52d63a34cbd0b5  520 s  file complete, lanecheck DONE, 10 findings
- examples ab256d128a225b984  486 s  complete, DONE, 4 findings
- names    aabe5fec22d7e4154  622 s  complete, DONE, 9 findings
- flags    a0b28e02c31539ae4  445 s  complete, DONE, 6 findings
- fixind   a853bfbd27d74131e  671 s  complete, DONE, 15 findings
Final replies: all five "ended without delivering a report" (expected; files are the delivery).
2026-11-22T19:12:47-05:00
Verifier a2352c4b74e94536b (opus) 19:13-19:23 (649 s): verify.md complete, lanecheck DONE; 13 items (V1-V12 + COORD-1 as V13); 2 model runs.
Draft review.md: 19:30. Time to draft from launch ~29 min; whole round ~35 min.

## Per lens
- RULING 10 (quote drift 0; 2 design, 8 doc/marking); overlaps: RULING-1 with FLAGS-3 and FIXIND-1/2 (3 lenses), RULING-5 with FIXIND-10, RULING-9 with NAMES-8 and FIXIND-12.
- EXAMPLES 4 (1 design, 3 doc); 21 lines re-derived, 0 differing.
- NAMES 9 (5 answer-in-evidence/undecided, 2 maintenance, 2 design/doc); NAMES-5 overlaps FIXIND-8.
- FLAGS 6 (2 design answer-moving in text, 2 maintenance, 1 doc, 1 definition).
- FIXIND 15 (most productive by count; FIXIND-7 the round's most serious evidence finding, found by a rename probe nobody was briefed for).
- COORD-1: found by the coordinator reading the re-run's SWEEP PASS-line counts.

## Process observations
- All five critics and the verifier returned in their launch turns (background launch behaved as foreground here); no resends, no stalls, no relayed findings, no refused appends.
- The newest model ran in 52 s, not "several minutes"; the full re-run of all ten models took ~2.5 min, so re-running everything was cheap.
- Three lenses (RULING, FLAGS, FIXIND) found the same stale flag readings (C1): the brief gave "every sentence still written under the earlier rule" to FLAGS and "grep revised terms over the whole subject" to FIXIND — overlapping by root concept. Next time assign the earlier-rule sweep for the flags root to ONE lens.
- NAMES-5 and FIXIND-8 found one engine fact from two sides (convention vs reading (a)).
- Blinding: no leak noticed; critics stayed in R/. The branch moved mid-round (manager's own files + record), not read beyond the record diff.

## Proposed changes
1. Skill §6/COMMON template: "For an evidence check that claims every printed line, read its PASS-line status counts; any non-same status not in a declared list is an undeclared red at the freeze." (B7)
2. Lens table, NAMES/grid lenses: add a RENAME drill (bindings named like the receiving macro's parameter). (B1)
3. COMMON: assign the 'earlier-rule sentences' sweep per ROOT to one lens; FIX-INDUCED then takes only the OTHER root's terms (C1 triple-found).

## Framework notes
- A coordinator re-running the evidence itself before briefing paid off directly (COORD-1); it cost ~3 minutes.
- Launcher-dictated lens list + root-concept split worked: each root's completeness question produced one clear definition finding (A6, A7).
