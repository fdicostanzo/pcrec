# r92 memfn-archrev2 process (coordinator)
- 2026-11-24 12:47 setup start. Subject note commit e3f3b5a1236abc9b8ef56aa0f24360963424fac9 (git log -1 -- note on lane/memfn-arch). Branch tip at launch per brief f0a969bf5; at freeze da763e079 (adds only a journal line, "r92 launched"). Note unchanged after e3f3b5a12.
- T = a0f13ad83a2432f14341831ba4d1ff68964b79d9 (note header). main HEAD at freeze e11c5f4ef; rulings commit (decisions.md/plan.md) c0f8bd689.
- T vs main: only BOILERPLATE.md + memfn/docs/{journal,requests,responses}.md differ -> no cited code site moved; decisions/plan/guide identical.
- T vs e3f3b5a12 under memfn/src memfn/include memfn/tests src tests Makefile memfn/data docs/dev/guide: empty (C-56 re-derived).
- R/tree = git archive T minus docs/dev/lanes/archrev_*/archrev2_* (none at T); journal.md truncated at 4911 (drops the 2026-11-24 entry); responses.md truncated at 3780 (drops the R-48 ack and later). chmod a-w.
- RUL-13 ruling: only record is a denied ledger; COMMON quotes the launcher's verbatim text.
- anchor_map (tools/review/anchor_map.py @654068977) run over R/tree: 265 memfn rows, 0 STALE/MISSING; window.c 59 anchor rows (note says 58 mech rows -- left to the first-unit lens, not briefed).
- ~12:48 four opus critics launched in one message (fuwindow, fuseam, ruling, aggfix), unnamed. All four wrote their pre-created file and CRITIC COMPLETE; times 6-9.5 min; every final reply undeliverable (expected).
- Findings: fuwindow 12, fuseam 7, ruling 8, aggfix 11 = 38 -> 14 consolidated (G1-G14). Overlaps: G1 (FUW-1/2, AGG-8, AGG-5i), G2 (FUW-10, AGG-7), G8 (FUS-6, AGG-9), G9 (FUS-7, AGG-4), G12c (RUL-8, AGG-6). No answer/speed findings.
- Verification inline (all grep/quote claims): 7 claims re-run, all HOLD. No verifier agent.
- Freeze drift at hand-back: none (main e11c5f4ef, subject branch da763e079 unchanged).
- 12:59 draft written; no review worktree to remove (arch mode).

## Process observations
- The r91 lesson (size/gate to first-unit alone) worked: no lens re-derived ranges or counts outside the two first-unit lenses. Residual duplication came from claims that are not size/gate: a NEW unit's claimed effect (ARV-16 deletes the cycle), a row's "small" kind, and the §9 example.
- Splitting first-unit into two lenses (window family / seam units) kept each to under 10 min with full anchor-location coverage.
- The filtered `git archive` R/tree removed all denylist exposure; no critic needed the live repo.

## Proposed changes
1. Skill §4 first-unit row, re-check sentence: "On a re-check, a NEW unit's claimed effect (it deletes X, it unblocks Y) goes to the first-unit lens beside its size and gate." (motivates: G1 found twice.)
2. COMMON template: "Row-kind checks (noted vs remodel, 'small' by judgement (e)) belong to ONE lens (register or aggregation); every §9 owner-question sentence, its EXAMPLE included, belongs to the ruling lens." (G9, G12c found twice.)
3. Skill §4 arch staffing: "When the first-unit scope spans two sections of the subject (planner-side and seam-side), staff two first-unit critics by section." (both delivered in under 10 min.)

## Framework notes
- A light re-check with 4 opus critics and an inline verification reached its draft in about 25 minutes from launch; the coordinator's context held 38 findings without strain.
