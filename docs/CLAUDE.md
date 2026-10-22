# docs/ — project working documents

Process and status documents for pcrec. The architecture itself lives in
../APPROACH.md; these files track execution against it.

## Subdirectories

- `dev/` — development-process documents (plan, journal, decisions, issues, reviews). See `dev/CLAUDE.md`.
- `design/` — living design documents, with panel outcomes and refutations inline. See `design/CLAUDE.md`.
- `spec/` — the contract: how the tool and its surfaces work, no build history. See `spec/CLAUDE.md`.
- `guide/` — human use-case guide tier (D80); points at `spec/`, never restates it. See `guide/CLAUDE.md`.
- `measurements/` — archived probe output (D35), evidence only, no check reads it; written by `scripts/measure.sh`. Own CLAUDE.md.

## Files

- `pcre2_compliance.md` — construct-by-construct PCRE2 compliance; three components of different provenance ([DOC-DRV]): generated registry index (`pcrec --list-syntax`), hand-written survey tables, keyed annotations. Refresh via the `compliance-refresh` skill.
- `pcre2_compliance_annotations.txt` — the keyed annotation store (data, not prose); edit, then run `tests/registry/compliance_section.py --write-annotations`.
- `pcre2_options.md` — [PC-5] PCRE2 option-by-option dispositions (ruled D38).
- `testing.md` — harness usage, env vars, measured runtimes, sanitizer/lint battery, oracle exclusions, the artifact-size log. The `.rxt` format is `spec/rxt_format.md`.

## Rules

- Update this file when files or subdirectories are added/removed or change role.
- In the compliance page's generated index, `status`/`roadmap` are the registry's own fields, not shipped status; read its `built` column.

Per-file detail (verbatim): NOTES.md in this directory.

History (not auto-injected): docs/dev/history/claude_md/ (frozen archive).
