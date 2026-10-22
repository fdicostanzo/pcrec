# substb's lanes history-index entry, for the landing

This branch carries main's de-bulked CLAUDE.md files (115585ec1), without
`docs/dev/history/claude_md/docs__dev__lanes.md`. At the landing, append this
line to that file's per-lane list (N-1 / D149):

- `substb_report.md` — [M4-SUBST] phase B BUILD (2026-10-22, lanes substb1+substb2, opus; NO rx abi event, abi 84 unchanged: the subst block lives only in subst headers under `PCREC_SUBST_H`): the template compiler (`src/parse/subst_template.c`), the per-template element and `<p>_subst_info` (`src/gen/emit_subst.c`), the generic bind, the glue `pcrec_subst` with the limit argument and ncaps-sized batches, CLI `--subst`/`--subst-file`/`--unset=`, spec `docs/spec/subst_api.md` + match_api §2¶6/§3.8¶2a/§3.8¶9a + cli.md §1.19, `make test-subst` (729/0, 42 cells against `pcre2_substitute` 10.46), mech arm `subst` and rows S1346-S1364. Findings: ctx_init reads vars only BOUND or FRESH+OPT_VARS (not ENDED); OOM aborts on the CLI-only template path; `${site.group}` unparsed; `--features` not consulted for subst modules.
