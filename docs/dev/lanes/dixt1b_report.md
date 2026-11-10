# dixt1b report — [DOC-INDEX] T1b

## STATE AT HANDOFF

Branch lane/dixt1b, commit 9b8eac350 (plus the report commit). No `src/`, `memfn/` or `scripts/doc_cites.py` edits; no new test script (no TT-9 / K37 / `make test-codegen` run owed).

Files:
- `scripts/INDEX.md` (new): 63 lines, `- <name> <state> — when: ...; does: .... {keywords}`, grouped by section. Covers every top-level file under scripts/ plus `hooks/*` (not `hooks/test_*`); `CLAUDE.md`, `NOTES.md`, `INDEX.md`, `tests/` exempt. Two retired lines: `pcrec_analyze.py` (deleted in b8ae03901, no file) and `m6read_rename_emitted.py` (one-shot rename, file kept; my judgement, the manager may re-mark it live).
- `scripts/doc_profiles.py`: `scripts` profile (form `list`, `exempt` key) and a `fixscripts` fixture.
- `scripts/entry`: list form (`list_index`, `header_block`, `list_lookup`), routing row 6b (script name, `scripts/` prefix optional, extension-less stem; 2+ hits exit 2; rules 2/3/5 skip list profiles), `--lint-scripts`, `--help` text naming levels, profiles, examples; 19 new selftest checks (clean fixture, missing line, new script, new hook, dangling line, missing when/does, missing keywords, duplicate, bad state, header-less live script, malformed line, L0/L2 for shell/docstring headers, `-g -p`, D-key not routed).
- `tests/doc_lint/run_doc_lint.sh`: real-tree `--lint-scripts` plus four plants on a scratch copy of scripts/ (new script, new hook, dangling line, header-less script); `tests/doc_lint/CLAUDE.md`, `scripts/CLAUDE.md` (lists INDEX.md; 4080 B of 4096), `docs/dev/doc_format.md` (routing 6b, the profile row and its form).
- Discoverability: manager SKILL.md wake step 3a; BOILERPLATE.md process-rules line; root CLAUDE.md lookup row widened (18299 of 20480 B).

Checks (verdicts): `make test-doc-lint` 7/7 pass; `entry --selftest` 67 checks 0 failures; `make test-plan-lint` pass; `tests/doc_lint/run_doc_index.sh` DONE rc=0; `make strict` clean (rc=0); `check_claudemd_size.sh --all` clean; `scripts/tests/gestalt.test` 54 pass; pre-commit staged checks 52/52. `-p scripts` grep and `entry boxqueue` work.

Owed / notes:
- The linter is `entry --lint-scripts`, not a separate doc_lint.py (unit 1 owns that name); fold in when unit 1 lands. The profile's `linter` field says so.
- `-g` without `-p` does not search scripts (default stays single/pair profiles); `-p scripts` required.
- The decisions-index half of SKILL.md step 3a reads "once converted" since the profile is dormant until unit 1.
- Ran `make testscripts` only partially (gestalt.test, the one that reads entry).
