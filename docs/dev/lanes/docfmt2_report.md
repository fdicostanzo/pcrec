# docfmt2 — lane report

Lane docfmt2 (opus), 2026-11-10. DESIGN ONLY; no real file converted. Branch
lane/docfmt, on top of rev 1 (a8e23570407a; tip at start 6b5525796).

## Delivered (commits on lane/docfmt)

- dfaf8522d — `docs/dev/reviews/2026-11-10-r1-docfmt.md` (the coordinator's
  draft, verbatim) + its directory (COMMON, the five critic texts, verify.md),
  with a "Rulings (manager, 2026-11-10)" section: every finding's ruled
  disposition = the proposed one, and where rev 2 discharges it. Listed in
  docs/dev/reviews/CLAUDE.md. Copy edit: `docs/spec/tuning.md` LINE cites in
  the copies rewritten to `§2.10¶3` (test-spec-history scans the tree).
- ab00d8966 — plan row [DOC-INDEX] (Active, STATE:started; charter = the
  owner's 2026-11-10 ask; refs the design, appendix, review, D192) and
  **D192** in decisions.md: the owner's six answers of 2026-11-10 (next free
  number on main: main's last was D191). plan_lint: 340 rows, 0 violations.
- 6ea705ed9 — `docs/design/doc_index_format.md` rev 2 (45,298 B = 44.2 KB,
  under the 45 KB bound) + `docs/design/doc_index_format_appendix.md` (new,
  A-I: addendum census, owner table + witnesses, cite forms, worked examples,
  C8 population, file census, kit proposal text, reader table, other-file
  verdicts); docs/design/CLAUDE.md line updated (12,283 B, under its cap).

## Validation

Design only: no make run. Pre-commit staged checks 52 passed, 0 failed on
each commit (spec-history staged line/dangling cites included; the new
`tuning.md §2.10¶3` cite resolves). No `<ruling file>.md:<line>` cite in the
design or appendix (grep). Worked statements measured with python: D26 200
chars (line 276 B), D47 194 (258 B), D191 182 (222 B). The inbound lists in
appendix D come from a throwaway prototype of `doc_cites.py --inbound` run
over main's decisions.md (scratch/docfmt2/inbound.py, not committed).

## STATE AT HANDOFF

- STATE: done. Rev 2 committed; ready for the RE-CHECK round the review
  recommends before T1's and unit 1's build go.
- D number used: **D192**.
- Finding → section map (rev 2 design §, appendix letter):

| finding | discharged in |
|---|---|
| F1 | §2.2 ownership/numbering/extent, §5.2 owner table + control, §2.1 a<k> note, §5.1 q2; appendix A, B (witnesses) |
| F2 | §0 G4, §2.3 routing rows 1 and 3 (aliases, `Dn.k`), §2.2 old labels greppable, §2.4 C13, §5.2 resolver; appendix C |
| F3 | §5.3 inbound pass + questions 3, 6, 7; §2.3 level 1 `later:`; §2.7 later rulings rewrite earlier lines; §0 G5 |
| F4 | §2.1 "one ruling" + rulings list + C11; appendix D (D26, D47, D191 rewritten, planted-line witnesses) |
| F5 | §5.2 exclusion set, already-converted test, idempotence, landing baseline |
| F6 | §2.4 "The section" (born in T1) and "Hooks"; §5 T1, unit 1 and T2 rows (readers, shims, acceptance); appendix H |
| F7 | §2.4 C8; §5 unit 1 row (cite-to-id pass, critic recipe); appendix E |
| F8 | §2.3 routing table, completed-row levels, `--work` never reads the archive |
| F9 | §2.1 slug row (per-profile grammar, provisional `-`, 1.S writers), §2.4 C5 + ratchet; PLAN: §10 unit 2 (`now?` slot, caps) |
| F10 | §3 (sizes recomputed, runway, always-on choice) |
| F11 | §0 G1, §2.3 `--rev` and content search, §5 unit 1 row (post_compact, critic freeze, COMMON recipes, memory step); PLAN: §5 unit 2/3 rows, §10 |
| F12, F13 | PLAN: §10 unit 2 (with leanings) |
| F14 | §1.1 + appendix F (DOC now); PLAN: §10 units 3, 4 |
| F15 | §5 order + landing + D153 check, §5.3 gate (S3-S8 after S1), §5.4 cost/trigger/stop table; COST-9 in §5 unit 3 row and §10 |
| F16 | §2 family paragraph, §4, §9 unlocks with triggers (no plan rows) |
| F17 | §1.1, appendix A and F |

- Readiness self-check: §10 (T1 and unit 1, each gating finding and its
  section).
- New design choices made in rev 2 (answer-free or within the ruled fixes):
  the RULINGS LIST beside any statement with `(+n)` (makes F4's "n equals"
  mechanical, C11); the `test-doc-lint` section is born in T1 (the structural
  lists move once); `(was:)` on every heading-form addendum, inline labels
  kept as the first body line; an `old_end` column ruled for markers inside a
  foreign entry; three planted lines per statement batch as the critic's own
  control; doc_lint's decisions profile is born in unit 1 so T2 can move after
  unit 1 without leaving decisions unlinted.
- Open questions for the owner, in plain words: none new. The rev-1
  question stands (should the per-line limits, like the 200-character
  statement, also be soft? leaning: keep them hard; rev 2's counted rulings
  list makes a hard 200 easier to live with). FYI for the owner: the decisions
  index will likely sit at or near its 48 KB soft cap from day one (worked
  lines average 252 B), so the gestalt line, his chosen revisit trigger, may
  fire soon after 1.S.
- For the MANAGER (an answer-free choice, per F10): whether the plan index is
  always-on. Recommendation: hold it out; the manager greps STATE:started at
  wake and serves the rest by `entry --work`.
- No rulings file named in the brief; none applied. The deliver file
  docs/dev/lanes/docfmt2_deliver.txt was manager-written and is left as is
  (untracked, listed under dirty-ok). Rev 1's manager-written
  docfmt1_deliver.txt was untracked here and lanecheck refused the dirty
  tree, so it is committed unchanged (the precedent docfmt1 set for rev 0's
  file); drop it at landing if deliver files stay untracked on main.
- Next: the RE-CHECK critic round on rev 2 (fix-induced findings + readiness
  per unit); then the owner's build go for T1; unit K (send appendix G to the
  kit) after the re-check.
