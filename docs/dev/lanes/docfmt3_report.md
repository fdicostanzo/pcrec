# docfmt3 — lane report

Lane docfmt3 (opus), 2026-11-10. DESIGN ONLY; no real file converted. Branch
lane/docfmt, on top of rev 2 (tip at start 74c467983).

## Delivered (commits on lane/docfmt)

- 44b7cc0fc — `docs/dev/reviews/2026-11-10-r2-docfmt2.md` (the coordinator's
  draft, verbatim) + its directory (COMMON, readyt1, readyu1, faith, fixind,
  verify), with a "Rulings (manager, 2026-11-10)" section: every proposed
  disposition accepted, R2-24 restated as the OWNER's decision. Listed in
  docs/dev/reviews/CLAUDE.md. **D192 item 7** (owner, 2026-11-10, quoted):
  the decisions index is read at wake, the plan index on first need, the
  post-compact hook inlines neither.
- 6f5202a9a — [DOC-INDEX] status/next/refs updated; child row
  **[CITE-FORMS]** filed (R2-27's migration row, not-started, trigger T2 or
  the next cite rule). Copy edit: four `plan.md:<line>` cites in the review
  copies rewritten to section/row names (plan_lint PL14 scans the tree; noted
  in the review file).
- ce4ab02fa + f71d5eb47 — `docs/design/doc_index_format.md`
  rev 3 (48,740 B, under 48 KB = 49,152) and
  `docs/design/doc_index_format_appendix.md` (A-J, ~40 KB; new J = T1's
  gestalt row and plants J1-J10). docs/design/CLAUDE.md says rev 3 (12,283 B,
  same length).

## Validation

Design only: no make run. Pre-commit staged checks 52 passed, 0 failed on
every commit; `plan_lint --root` 341 rows, 0 violations (it was 4 PL14
violations from the review copies before the copy edit). No numeric
`<file>.md:<line>` cite in the design or appendix (grep `\.md:~?[0-9]+` empty;
the examples are written with `N`), so the doc itself is no C8 case after
unit 1.

Measured in scratch (`$PCREC_TMPDIR/scratch/docfmt3/`, not committed) over
main's decisions.md at e9687de27:
- `scan.py`, the §5.2 scan + marker rule as written: 250 candidates = **193
  markers** (h3 71, bold 85, bullet-bold 17, plain 13, h2 7) + 57 mentions.
  193 = the critics' 180 prefix-form markers + the 13 plain-line ones. The
  only plain false positives (two wrapped sentences starting "ADDENDUM, is"
  and "addendum 2 —") are why a plain-class label must begin with its id.
  Placement: 36 id-named markers inside a later entry (34 + D122.a4 in D123 +
  D123.a8 in D124), so 46 outside their own cut with the 7 `##` headings and
  3 id-less D89 markers. 40 id-less markers need a hand ruling.
- `heads2.py`, appendix B's title rule: rules 1/2/3/4 fire 136/45/7/5 times
  (5 `(untitled)`); 28 dates inherited; 27 rows with no `who`. D47's derived
  headings in appendix D come from it (a3/a4 cut at 120 characters).
- Rounding edges for J4: 52592 B → 106%, 52593 B → 107%, 52633 B → 51.3 KB,
  52634 B → 51.4 KB (cap 49152 B).

## STATE AT HANDOFF

- STATE: done. Rev 3 committed; no rulings file named in the brief.
- Finding → section map (rev 3 design §, appendix letter):

| finding | discharged in |
|---|---|
| R2-1 | §5 T1 readers (move the fullsuite_job parenthesis first; `check_claudemd_size.sh --all`) |
| R2-2 | §2.4 soft caps (empty line prints nothing under `--all`, a general rule that deletes the idle-held special case; `GESTALT_ENTRY`); J (row, J1-J3) |
| R2-3 | §2.4 (kind `docs`/`L_docs`, placeholder replaced, `timeout 2`, `"$here/entry"`); J |
| R2-4 | §2.4 (trailer counts the population; one decimal truncated); J4 fixture edges |
| R2-5 | §2.3 (dormant exit 1 + trailer; router plants on fixture profiles; archive live from T1); §5 T1 root CLAUDE.md row (plan only; unit 1 adds rulings); J5 |
| R2-6 | §2.3 (archive row = HEAD_OK form); J6 |
| R2-7 | §2.4 "The section" (trailer touch, tests/doc_lint/CLAUDE.md, `NO-C-RUN`, shard row `test-doc-lint 2 2 ESTIMATED`); §5 T1 (docs/dev/CLAUDE.md, ACCEPTANCE line); J7 |
| R2-8 | §5 T1 readers (monitoring.md, both prompts); H |
| R2-9 | §2.3 (`--rev` with the working tree's table, form by files at SHA, decisions `single` at unit 1; `entry` imports plan_lint's grammar, Policy not an item section; PL18; both key spellings); J8-J10 |
| R2-10 | §5.2 scan + gate (b); A (plain-line class, two placements); B (D122, D123 witnesses; P20) |
| R2-11 | §5.2 control (ii) bijection, (iii) extents byte-exact, (iv) headings, (v) forms, multiset kept as sixth check; B plants P1-P21 with the clause each must fail |
| R2-12 | §5.2 / B `extent_hash` replaces `body_hash`; P21 |
| R2-13 | §5.2 marker rule; A (label regex, 193/57, "148" withdrawn) |
| R2-14 | §2.2 heading line + C3 regex + note rule (`class=note`, `Dn.aK#i`; D47's LANDED NOTE a numbered ruled row); B (`who`, `title`, full `old_label`, title rule table); D (derived D47 headings) |
| R2-15 | A (D147 unnumbered + 2-16; D98's two continuation lines, join for D98 only, P11) |
| R2-16 | §2.4 `floor` column (C9); §5 order (lane/docfmt merges before 1.0); §1 (counts re-taken by the census) |
| R2-17 | §5.2 cite-to-id pass; E (named id wins, content anchor, mismatches listed) |
| R2-18 | §2.1 statement/state rows, §2.4 C4 (a `?` line exempt; caps in characters) |
| R2-19 | §2.4 C13 (C8's exemptions, `dangling_before.tsv` that only shrinks); C (date alias, `addendum k of Dn`, baseline); §2.3 routing row 1 |
| R2-20 | §2.4 C8 (form `:~N`, lists, `../`, not-under-`pcrec-bench/` anchor, plants; plan_completed exempt for every profile); E (26 cites in 11 files incl. chain_profile.md; known cites wait for unit 3) |
| R2-21 | §2.4 Hooks (common git dir; skip without the module, fail with it; `linter`/`extra_paths` columns; `--paths` format; plants); H |
| R2-22 | §2.4 ratchet (`ratchet.tsv` equality baseline, birth row, landing-raise rule); §2.7 (new entries written at once); §5.2 landing baseline |
| R2-23 | §5 unit 1 readers (bench `[inbox]` MANAGER STEP per D78, docs/dev/NOTES.md, D27 allowlists, post_compact MAIN role); H |
| R2-24 | §0 G1, §3 "Which index is read when", §5 units 1 and 2, §7 item 7; D192 item 7 |
| R2-25 | §10 PLAN before T2 |
| R2-26 | §10 PLAN before 1.S (+ appendix D note on the current wrong-n plant) |
| R2-27 | §2.4 one cite-form table (C8/C13 in unit 1); §9 two unlock rows; plan child [CITE-FORMS]; hook manifest NOTED with trigger T2's hook edit |

- Readiness (rev 3 §10): T1 ready; 1.0 ready once lane/docfmt has merged;
  unit 1 ready once 1.0 is in and T1 has landed; 1.S ready once R2-26 is
  fixed in the doc. Each gating finding has a witness that must be red when
  built from rev 2's text (R2-8, R2-23, R2-24 have no mechanical witness;
  the manager checks them in the diff).
- For the manager: the brief's "the manager reads rev 3's §5.2 and appendix B
  against this list" — the list is appendix B's plant table (P1-P21; P20 is
  FAITH-1's D122.a4, P21 the one-line-addendum case of R2-12).
- Two choices I made where the review left a fork, both answer-free:
  (1) R2-9(c) as PL18 in plan_lint at T1 (the review allowed "a PL/doc_lint
  rule"; T2 carries it into doc_lint), so T1 touches plan_lint and its
  selftest; (2) the decisions `single` form for `--rev` is built in unit 1,
  not T1, so the R2-5 rule (decisions dormant at T1) holds without a
  parallel reader at T1.
- New owner questions, in plain words: none. The rev-1 question still stands
  (should the per-line limits, like the 200-character statement, also be
  soft? leaning: keep them hard; a `?` line is exempt anyway).
- Deliver file docs/dev/lanes/docfmt3_deliver.txt is the manager's and left
  untracked (listed under dirty-ok), as is docfmt2's.
- Next: the manager's read of §5.2 + appendix B; then the owner's build go
  for T1; R2-26 fixed in the doc before 1.S; R2-25 before T2.
