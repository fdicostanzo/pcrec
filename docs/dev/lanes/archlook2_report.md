# Lane archlook2: file review r50 (archlook) and revise the [REQ-LOOKAROUND] architecture note

Lane archlook2 (opus, 2026-11-18). Documents only: no `src/`, `cli/`, `lib/`, `memfn/`, `tests/`,
`scripts/` edit, no `make`, no suite, no queue job; the register in `docs/dev/guide/architecture.md`,
the skill, the guide and `span_arms.md` untouched. Part 2 written as a FRESH architect under
`.claude/skills/pcrec-architect/SKILL.md` (a fix round on a note, briefed from the review).

## STATE AT HANDOFF

- STATE: done. Branch `lane/archlook2`, cut from `lane/archlook` @ e7c814fcf (which holds rev 1 of the note).
- Commits: c82e52b76 (Part 1, the filed review), 2f93a18d2 (Part 2, the note rev 2), and this report's commit.
- Part 1: `docs/dev/reviews/2026-11-18-r50-archlook.md` = the coordinator's draft, number r50, an 18-line
  `RULED (manager, 2026-11-18):` line after every finding's PROPOSED disposition (taken verbatim from the
  manager's dispositions file; nothing added), the freeze-drift line ruled, the verdict RULED, process changes
  HELD. Round files in `docs/dev/reviews/2026-11-18-r50-archlook/` (AGGREGATION, SITEMAP, REGISTER, FIRSTUNIT,
  RULING, COMMON, verify, `firstunit_anchors.py`, `process.md`, `dispositions.md`, CLAUDE.md). The 16 lines
  holding `plan.md:NNN` cites (23 cites) are scrubbed to plan tags, each mapped by the row heading the cited
  line sits under at T; one spec line cite (`findings.md`) became its section. Index line added to
  `docs/dev/reviews/CLAUDE.md`; two older entries (r14, r15 of 2026-11-15) moved to its NOTES.md for size
  (11,835 of 12,288 bytes after). `scripts/plan_lint.py --root .`: 0 violations.
- Part 2: `docs/design/req_lookaround_arch.md` STATUS "DRAFT rev 2 (after review r50)". TREE stays T =
  57fcb5737 for code; the plan row [REQ-LOOKAROUND] is read at main HEAD 2843924a1, and the header says so
  (`git diff --stat 57fcb5737 2843924a1` over src, memfn, lib, cli, docs/spec, docs/dev/guide, decisions.md,
  span_arms.md prints nothing). Every change carries an inline `[r50 An]` tag.
- Rulings file `docs/dev/lanes/archlook2_rulings.md`: empty at every check; last ruling applied: none.
- STOP RULE: not triggered; no ruled disposition was contradicted by the tree or the record.
- OWED: none. Next by the dispositions: one confirm critic on rev 2.

## FINDINGS APPLIED

| finding (critic ids) | applied? | where in rev 2 |
|---|---|---|
| A1 (RULING-1) | applied | MF_SITE_ABI 29 and `MF_HEAD_MAX_UNBOUNDED` in Goals, Requirements, site 16, the kit seam row, F-2; RM-2 and D-7 map "unbounded" onto it at emit_dfa.c:1644 |
| A2 (RULING-2, FIRSTUNIT-3) | applied | site 18: the shadow follows the kit's P4, its fate is D-6; RM-4's consumed extent has two readers (`pcrec_req_pick`, `pcrec_run_pin`); `run_pres_picks.sh` and S453 named; the primitive named by the question `req_byte` answers |
| A3 (RULING-3, REGISTER-2) | applied | facts.h:4-5 cited (Goals, C36); "traded" dropped; D-5: new fields declared in facts.h; the five direct `pos` reads are F-8 for the manager |
| A4 (RULING-4, AGGREGATION-4, REGISTER-1) | applied | owner question context-producer-home rewritten with D172 and the [CTX-FACTS-NEG] fork; contingent ND-1; [CTX-FACTS-NEG] and [NEVER-MATCH] in the planned-rows table |
| A5 (RULING-5) | applied | remodel-go names RM-2 and RM-4's extent as inside L3's go'd text, RM-1/RM-3's merge/RM-5 as new; the leaning orders census, remodel commits, feature (D191.1 quoted) |
| A6 (RULING-6, FIRSTUNIT-1, FIRSTUNIT-7) | applied (the ruled form) | RM-3 merges the arithmetic only; the two ROUNDUP calls stay; two A-POSDOM rows; rev 1's "one row instead of two" deleted; D-8 carries the five differences plus the re-ask block; the premise moves into the one emitter; S813, S814, S1701, S1711 named; the per-caller plant shape handed to D-8 |
| A7 (AGGREGATION-2, AGGREGATION-7, FIRSTUNIT-2, SITEMAP-5) | applied | site 12 lists all ten tests (C12 rewritten, 14 lines) and the 11 value readers (C33); P2's WHERE names the offset-bound family; D-7 (K alone vs the signed interval), D-8 (act through the row or re-test); :9085 leaves RM-2; S467, S1957 named |
| A8 (RULING-7, AGGREGATION-1) | applied (the HOME as the manager ruled) | site 21: the never family (PfNever, derive.c prune, mrl.c minw ceiling, the `empty` LOCATE row) as the ONE home; READY-5 cited as the manager's form his r50 ruling revises; its listing consequences listed as binding checks; P6 and D-9 carry the shared-primitive-or-row choice |
| A9 (RULING-8 a-f) | applied | (a) the owner's words quoted in order; (b) "can be built", the "home" reading marked the manager's; (c) [EARNED-SKIP]'s trigger verbatim and PARKED; (d) F-7 names the ten markers, the replacement text missing; (e) D189 listed as a mapped-site trigger, SUSPECTED, D-11; (f) D62 line corrected (D70 names its discipline; the addendum makes the trigger moot) |
| A10 (RULING-9) | applied | `rn_scan_mass`'s ranking and the compile.c readers' keying are questions with both readings in D-4/D-6 and D-9 |
| A11 (FIRSTUNIT-9, REGISTER-3) | applied | P1/RM-1 widened to every record builder in the run path, the two `ReqRun` writers in its WHERE |
| A12 (FIRSTUNIT-5, REGISTER-4) | applied | `rr_unit`, `rr_pos` in RM-1; `rr_rep_split` :788 and `rb_rep_best_val` :925 named as the feature's own writes; S1910, S1918, S1919, S1923 among RM-1's 15 anchors; P1's "deletes" no longer claims a defect at T |
| A13 (FIRSTUNIT-4, FIRSTUNIT-8, SITEMAP-2) | applied | every gate line names its streams (.c, facts listing, trace build); binding lists from the anchor map (C37) by location; S901 for RM-5; S1887, S1700, S469 (SUSPECTED for L2) named; S1925's reach stated as NOT going blind |
| A14 (SITEMAP-1, -3, -4, REGISTER-5; SITEMAP-6) | applied | site 19 lists the six emit_dfa.c run-pin readers (C34); site 16 WIDEN; C10 = 16; register row 2's WHERE touched at :8992-8993 cited (C44); SITEMAP-6's readers verified at T and added to site 17 (C41) |
| A15 (AGGREGATION-3) | applied | site 8 and D-4: `reach` as TOP rows with an arm column, or a parameter, and why |
| A16 (AGGREGATION-5) | applied (sentence); U-negctx not added (DECLINED) | general form: a negative lookaround is CAT's width-0 unit since E2, probes re-run; F-1 notes the plan row's "stay walls" sentence |
| A17 (AGGREGATION-6) | applied | site 23 states both forms (SHARED through the head column; or a third family with ND-2, correcting event L1 or L2) and leans SHARED; D-10 names `PdHead`; P5 re-triggered on L1/L2 |
| A18 (FIRSTUNIT-6) | applied (DOC) | RM-1 conditional on D-2; RM-4 = the shared primitive only, the consumed-extent accessor with the unit that gives it a value |
| freeze drift | applied | header reads the plan row at main HEAD 2843924a1 and says so |
| process changes | not applied | HELD by the manager |

Per critic id (the review's by-id completeness table): AGGREGATION-1 A8, -2 A7, -3 A15, -4 A4, -5 A16, -6 A17,
-7 A7; SITEMAP-1 A14, -2 A13, -3 A14, -4 A14, -5 A7, -6 A14; REGISTER-1 A4, -2 A3, -3 A11, -4 A12, -5 A14;
FIRSTUNIT-1 A6, -2 A7, -3 A2, -4 A13, -5 A12, -6 A18, -7 A6, -8 A13, -9 A11; RULING-1 A1, -2 A2, -3 A3, -4 A4,
-5 A5, -6 A6, -7 A8, -8 A9, -9 A10. Every one applied through its group as above.

## WHAT MOVED IN THE NOTE

- Header: DRAFT rev 2; plan row read at main HEAD; the anchor map defined; FORM's mechanism list follows
  A8/A15.
- Goals: rule 1 names the three families and D172/[CTX-FACTS-NEG]; rule 2 cites facts.h:4-5, the trade is gone.
- Requirements: rows for D172, READY-5, the three plan rows; MF_SITE_ABI 29; the owner's words in order.
- Site map: sites 3, 7, 8, 10, 12, 15, 16, 17, 18, 19, 20, 21, 22, 23 rewritten; classes changed: 16
  AS-IS→WIDEN, 15 SHARED narrowed to the arithmetic, 21 now the never family's one home, 23 two forms.
- Register: row 2's WHERE cite, row 14's stage-3m caveat; D189 and D62 lines; P1, P2, P3, P4, P5 revised;
  P6 (never family) and contingent ND-1 (two producers), ND-2 (item as third family) added.
- Remodels: stream-naming gate lines; anchor-map binding lists; RM-1 widened and conditional; RM-2 scoped
  off :9085; RM-3 arithmetic only; RM-4 primitive only; RM-5 gains S901; the lookaround witnesses paragraph.
- General form: negative-lookaround sentence fixed; three families; two planned rows added; [EARNED-SKIP]
  and [DESC-DEAD] rows corrected.
- Deleted: RM-3 no longer deletes the premise; the `dead` why token is kept as a rendering.
- Design hand-offs: D-4, D-6, D-7, D-8, D-9, D-10, D-11 extended; D-16 added (the K comment at :7901).
- Commands: C10, C12, C16, C29, C30 corrected; C33-C47 added.
- Findings for the manager: F-1, F-2, F-4, F-6, F-7 revised; F-8, F-9 added.

## OPEN QUESTIONS FOR THE OWNER

1. **context-producer-home** — current behaviour: for `(?<=foo)bar` nothing states `f`, `o`, `o` at −3..−1
   (the run is `bar`, `626172@0`); D168 says one producer, D172 says the window site reads it, and
   [CTX-FACTS-NEG] plans a machine producer of the same sets with this feature as trigger. Choice: (a) one
   producer, L1's item, [CTX-FACTS-NEG] re-scoped to what the item cannot state (`\b`, past the end), or
   (b) two by layer with noted deviation ND-1. Example: `(?<=foo)bar`. Leaning: (a).
2. **remodel-go** — current behaviour: none of the five refactors is built; RM-2 and RM-4's extent are
   already inside L3's go'd text, RM-1, RM-3's merge and RM-5 are new. Choice: covered by D191's go, riding
   each unit as census → remodel commits → feature, or a separate go each. Example: `(?<=foo)bar(\w)\1`
   compiles to identical C after RM-3. Leaning: covered, in that order (D191.1's census-stop binds).

## COMMANDS

- `git -C <wt> rev-parse --show-toplevel`; premise: `git -C <wt> log -1 --format=%h -- docs/design/req_lookaround_arch.md` (0abc1e961), `grep -c '^\*\*A[0-9]' review.md` (18).
- Plan-cite mapping: `git show 57fcb5737:docs/dev/plan.md` and an awk walk from each cited line to the row heading above it (lines 230/231→[VLOOKBEHIND], 234→[RUN-POS-SET], 256/257→[REQ-EMPTYCAT], 539/540→[EARNED-SKIP], 545→[NEVER-MATCH], 861/866→[CTX-FACTS-NEG], 934-939→[REQ-LOOKAROUND], 941→[LOOK-LOCATE], 1357→[REWRITE-ADJ], 1950→[REPEAT-RUN]), then `sed -i -E` on the copies; `grep -rn 'plan\.md:[0-9]'` over the dir: 0.
- `python3 scripts/plan_lint.py --root .` (0 violations, both commits); `bash scripts/check_claudemd_size.sh --staged` (within limits).
- Note commands: C1-C47 in the note's "Commands" section, all at T; rev 2's new runs: C10, C12, C16, C29, C30 (main tree's `build/pcrec`, `timeout 60`), C33-C47; the anchor map over a T export in `$PCREC_TMPDIR/scratch/archlook2/at/`.
- `scripts/entry REQ-LOOKAROUND|CTX-FACTS-NEG|NEVER-MATCH|DESC-DEAD|EARNED-SKIP -l 2` (main HEAD).
- `scripts/lanecheck` (DONE rc=0 before handback).
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">W=/home/pcrec/projects/pcrec/worktrees/archlook2; H=$W/docs/dev/history/claude_md/docs__dev__lanes.md; echo '- `archlook2_report.md` — files review r50 (archlook: ARCHITECTURE round on req_lookaround_arch.md) with the manager'"'"'s ruled dispositions and round files (plan line cites scrubbed to tags), and revises docs/design/req_lookaround_arch.md to DRAFT rev 2: A1-A18 applied as ruled (MF_SITE_ABI 29; never family one home, READY-5 listing kept; RM-3 arithmetic only, two A-POSDOM rows; anchor-map binding lists; offset-bound family; owner questions context-producer-home (D172, [CTX-FACTS-NEG] fork) and remodel-go (census first)) (2026-11-18, lane archlook2, opus; documents only).' >> $H; cat $W/docs/dev/lanes/archlook2_rulings.md; git -C $W add docs/dev/lanes/archlook2_report.md $H; git -C $W commit -q -m "archlook2: lane report + history index line

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EedbhfafYhD2svJG5RCCMx" -- docs/dev/lanes/archlook2_report.md docs/dev/history/claude_md/docs__dev__lanes.md; (cd $W && timeout 120 scripts/lanecheck; echo rc=$?)