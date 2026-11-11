# dixcite report: [DOC-INDEX] 1.0 cite resolver

## STATE AT HANDOFF

Delivered on lane/dixcite (commit ed0558b1c + this report): `scripts/doc_cites.py`,
`docs/dev/doc_index/dangling_before.tsv` (60 rows), `resolution_before.tsv`
(183 keys), two checks added to `tests/doc_lint/run_doc_index.sh`
(selftest + `--check`, `${PCREC_TMPDIR}` braces kept), doc_index/CLAUDE.md line.
Green: `bash tests/doc_lint/run_doc_index.sh` (7/7), `make test-doc-lint`,
`make test-plan-lint`, `make strict`.

Modes: `--summary`, `--inbound ID` (new_id or Dn; shows host entry for cites
inside decisions.md), `--emit-baseline`, `--check`, `--selftest` (plants:
renumbered addendum, new dangling cite, moved owner, baseline-only-shrinks).
Reuses doc_census (table reader, ORDINAL, DATE, ENTRY_HEAD).

Forms resolved: `Dn addendum|add.|ADDENDUM [ordinal|k|k.m|3a|date]`
(unnumbered -> rows with old_number `-`), `addendum k of Dn`, `Dn.aK[#c]`
(by new_id), dotted `Dn.k` and bare `Dn` (entry must exist; bare limited to
D1..D499 so D0/D04/D800 hex noise is not a cite). Population: git ls-files minus
appendix E's exemption set; decisions.md marker lines are skipped.
NOT done (units 2/3, per appendix C): Kn, Un, [TAG] existence, `decisions.md:N`
line cites (appendix E handles them).

Baseline semantics: dangling rows keyed (file, form, cite text) with counts, line
is informational (lines churn). `--check` fails on a NEW dangling cite, on a
baseline row now resolving or gone, and on a cite key whose resolved new_id set
differs from resolution_before.tsv.

Population: 19,480 cites in 1,731 files. Dangling 60 by form: addendum 47,
newid 13, bare 0, dotted 0, of 0 (the 4 `addendum k of Dn` cites sit in exempt
paths today). 10 commonest: D168 addendum x9 (D168 has no unnumbered row),
D146 addendum x7, D155 addendum 6 x5 (the known PROPOSED case; plus D155 add. 6 x2),
D155 addendum x3, D161 add. x3, D2.a1 x3 (doc_control/appendix plant text),
D144 addendum x2, D186 add. x2, D3 addendum 2 x2.
Rows in scripts/doc_census.py, doc_control.py, entry and design appendix are plant
or example text; they sit in the baseline by design. Note for dixt1b: scripts/entry
holds `D26 addendum 2026`/`2025` fixtures and `D26.a9`; editing those strings will
trip `--check` until the baseline row is updated.

## The four existing cite checkers ([CITE-FORMS]; listed, not unified)

1. tests/spec_history/spec_cites.py: `<doc>.md §N`/`§N¶K`/`SN` cites name a
   section that exists in numbered specs, no `<doc>.md:<line>`; floors in
   cite_floors.tsv, exclusions in cite_exclude.tsv.
2. scripts/plan_lint.py PL14 (tree-wide scan, make test): no `plan.md:<line>` cite.
3. scripts/hooks/pre-commit (via tests/spec_history/spec_history.py --staged):
   staged files break no spec rule, including line-number citations; spec_history.py
   itself guards build-history markers in docs/spec/.
4. tests/doc_lint (doc_lint.py/doc_profiles.py, T1; C8 line cites per profile,
   C13 planned): the cite-form table for decisions/known/plan line cites.
(doc_cites.py is a fifth, the Dn.aN resolver; C13 will be this code.)
Check 4 is the one I could not open to confirm exact wording in this lane
(doc_profiles.py is dixt1b's); verify before [CITE-FORMS] work.

## Hand-offs to main
- scripts/CLAUDE.md should list `doc_cites.py` beside `doc_census.py`/`doc_control.py`
  (4084/4096 B, dixt1b's lane; not touched).
