# VERIFY brief — critic round p48

Read /var/tmp/pcrec-pcrec/scratch/crit-p48/COMMON.md first: its scope mandate, denylist,
probe limits and tools bind you too (your probe dir: /var/tmp/pcrec-pcrec/scratch/crit-p48/verify/).
You may read the three critic files sound.md, design.md, cost.md and subject_p48_report.md.
You do NOT trust a critic's consequence claim: re-derive each one yourself.

Verify these finding ids (each: HOLDS / REFUTED / PARTLY / not verified (why)):
- SOUND-1, COST-1, DESIGN-7 (together: `dfa_start_is_scan_head` has a second reader `s0head`;
  narrowing it moves prefilter placement; harmless today only because of scanedge.c's s0 refusal.
  Quote the lines. Also DESIGN-7's mover class: `x*` (not seeded) emits an UNCONDITIONAL
  `goto ..._scan_edge` that the rule removes — emit it and quote.)
- SOUND-2, COST-2 (the `!= 0` sabotage half is invisible to answer checks; tests/codegen/
  run_scan_edge_census.sh check (2) asserts the entry line on rows the rule removes — quote the
  check and count the manifest rows; whether S227/S764/S780 mention the seedhead/entry)
- DESIGN-1 (row 4's byte-prior price declines `\d+-`, `foo[a-z]*bar`, `id=\d+;`; recompute the
  masses from src/core/findings_table.inc; confirm `id=\d+;` stamps "none"; findings.md §2 paragraph 7 utf8 NONE)
- DESIGN-2 (rows 3/4 omit (6), (8), the s0 `!a` refusal; quote scanedge.c lines)
- DESIGN-3 (measure_store set already holds kit beta/f/xover cards; measures.md one card per
  owner.quantity — quote)
- DESIGN-4 (cap ranking by prior mass would rank `\s` (0.138) and hex (0.305) below row-4 admits;
  census line 584 displaced count; chain_cmp today)
- DESIGN-5 (stay rule vs p>0.70 disagree both ways: count bytes / masses for `[^a-z]`, `[^\w]`,
  `[0-9a-z]`; quote D13 on M2.10 and emit_dfa.c `bestcnt = 191` comment)
- DESIGN-6 (arithmetic 369/922 vs 120/412 against G2's text)
- DESIGN-8 (rows 2/4 two missing-price verdicts; the card text says "row 3"; measure_store has
  no ADVANCE row; DEFAULTS content)
- DESIGN-10 (pick_skip_states `out[4]`/cardinality ranking vs scanedge chain_cmp + cap;
  decision_families_survey.md has no such row)
- COST-3 (abi number at 02a054851 and the grep count of its readers)
- COST-5, COST-6 (plan rows [LANDWALK-EDGEPRICE], [PRIOR-COST-UNIFY], [LIST-TABLES] exist with the
  quoted states/triggers — read ONLY those rows' own lines, located by `grep -n '^- \[TAG\]'`)
- COST-8 (count `scan_span != 0` spellings in emit_dfa.c; scanedge.c:711 kill guard)
Skip: SUSPECTED findings (COST-7, DESIGN-9) except to note whether anything outside the denylist settles them.

Write `verify.md` INCREMENTALLY (create it; it does not exist yet), one `## <ID>` section per id
(grouped ids may share one section headed with all ids), each with a verdict line and the evidence
(command + quoted output / file:line). First section `## SUMMARY` (a one-line verdict per id,
fill it in at the end), last line `VERIFY COMPLETE`.

DELIVER file `verify_deliver.txt` beside it:
report=verify.md
sections: SUMMARY
commit: no
Then run (via a `( cd /var/tmp/pcrec-pcrec/scratch/crit-p48 && ... )` subshell)
`/home/pcrec/projects/pcrec/scripts/lanecheck --deliver /var/tmp/pcrec-pcrec/scratch/crit-p48/verify_deliver.txt --dir /var/tmp/pcrec-pcrec/scratch/crit-p48 verify`
until it prints `lanecheck: DONE rc=0`; then END with a reply of at most 100 words.
