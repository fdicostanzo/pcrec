# docfmt — lane report

Lane docfmt (opus), 2026-11-10. DESIGN ONLY; no real file converted. Branch
lane/docfmt off main 6638e3679.

## Delivered

- `docs/design/doc_index_format.md` rev 0 (31 KB): census (§1), the one
  format (§2: index line grammar, details headings, `scripts/entry` tool and
  one-line awk, plan_lint folded into `doc_lint.py` with a per-file
  PROFILES table, worked examples from D26, D47, D191 and [OPT-REVEND],
  [ANCH-AT], [XARCH-TOKERR]), size targets (§3), other files (§4),
  migration units M0-M13 (§5), risks (§6), owner questions (§7).
- `docs/design/CLAUDE.md`: one listing line (line 117 reworded to fit the
  12 KB cap; check_claudemd_size green).

## Findings worth the manager's attention

- 17 decisions addenda sit inside a LATER entry (five of D163's inside
  D167, D94's inside D112, ...), and D47's two load-bearing addenda are
  top-level `## D47 ADDENDUM` headings after D48: a `^## Dn` cut (the one
  tests/memfn/rows_check.py uses) misses them today. The format fixes this
  by construction (addenda inside their entry, `### Dn.ak`).
- Addenda come in six spellings; 61 numbered, the rest not; 2,708
  `Dn add. k` cites exist, so numbered addenda must keep their numbers.
- rows_check.py (LEDGERS) and tests/memfn/stream_support.tsv are the only
  parsers of decisions.md; plan_lint is the only parser of plan.md.

## Validation

Design only: no make run. Byte sizes measured with `wc -c` / python at
6638e3679; worked-example bytes measured from the doc's own lines.
check_claudemd_size.sh --staged: 52 passed, 0 failed.

## STATE AT HANDOFF

- STATE: done (design rev 0 delivered, committed on lane/docfmt).
- Doc: docs/design/doc_index_format.md (rev 0).
- Projected index sizes: decisions.md 36-46 KB (central 38 KB, 191
  entries at ~200 B), plan.md ~40 KB (339 head lines + 38 `now` lines),
  known_issues.md ~25 KB, upstream_issues.md ~4 KB; proposed lint caps 48 /
  48 / 32 / 12 KB. Decisions grow ~8 KB/month, so the 48 KB cap arrives in
  about 1-2 months unless superseded entries shrink.
- Open questions for the owner (§7, each with a leaning): (1) who writes
  the statements and should Frank read the finished decisions index once
  (leaning yes); (2) one details file per index vs one file per entry
  (leaning one file); (3) should not-started plan rows show next/trigger in
  the index (leaning no); (4) what happens at the decisions cap (leaning:
  shrink superseded, then a "settled" section he picks); (5) kit ledger
  index block, a proposal to the kit (leaning yes, later); (6) known issues
  right after the plan (leaning yes).
- No rulings file named in the brief; none applied.
- Next: owner discussion of §7; on a go, unit M0 (tooling, sonnet), landing
  outside the 2026-11-11 01:00-~14:00 merge freeze.
