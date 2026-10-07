# probes/rowcon/ — [MEMFN-ROWCON] evidence (read-only audits, 2026-10-07)

- `audit_kit_rows.md` — lane rowaudit (sonnet, read-only): the kit's 8
  selectable rows and how they are selected, a field × row matrix
  (honoured/declined/refused/ignored, 8 K96-class suspect cells), 13
  rows-disagree cells, visibility today, and reach from pcrec's corpus
  and from G2.
- `customers.md` — lane rowcust (sonnet, read-only): six pcrec REFERENCE CUSTOMERS for the engine (cand_rows on lane/stc2, dfa_pfs/DFA_SELECT, engine selection, POSS-CTX-TABLE, the axes, C1 trace), each with its hardest-to-host feature.
- `audit_pcrec_tables.md` — lane rowaudit7 (sonnet, read-only): pcrec's
  ~13 first-match tables, prior unification designs (start_table.md,
  decision_families_survey.md, D152) and the kit boundary's implications.

Both are inputs to `../../row_contracts.md`. They are facts at main
92ca17fc, not maintained.
- `hook_census.md` — lane hookcensus (sonnet, read-only, 2026-10-07): every hook text pcrec passes at each delegated site. NO RISKY HOOK: value hooks are bare identifiers, on_miss is `return 0;`, and prefix-derived names are identifiers. It is H2 (SNAPSHOT)'s "not yet" evidence; re-run it when a migration adds a hook.
- `n2_census.sh` / `n2_census.py` / `n2_report.py` — lane rowconn2 (2026-10-07), [MEMFN-ROWCON] N2: the would-decline census. The `.sh` takes `worktrees/.mac-suite.lock`, builds an `-DMF_TRACE` pcrec, runs the `.py` driver (every `--list-axes` arm x both comment tiers x streams c-default/c-vm/composition, built on `scripts/emit_sweep.py`'s corpus and `run`), then the report (`n2_results.md`: population, would-declines with witnesses, the R-6 table, reach). Ends with `== N2 DONE rc=N would_decline=K ==`. `SMOKE=1 TRACEBIN=...` is the <=20-compile lock-free smoke. Resumable per arm (`arm_NNN.json`). Not run in full by the lane; see docs/dev/lanes/rowconn2_report.md.
