# adm1021 report (sonnet, 2026-10-21): F-3 text fix + two plan rows

STATE AT HANDOFF: done, committed on lane/adm1021, nothing owed.

1. F-3. `src/parse/registry.c` bare_rows: the `^` row now reads "already core
   (an A_CTX pin row, the same row \A builds)"; the `$` row's "(unlike
   ^/A_BOL)" became "(unlike ^, an A_CTX pin row)" (A_EOL still exists, so
   its mention stays). Regenerated docs/pcre2_compliance.md with
   `compliance_section.py --write` (2 lines); --check, --check-annotations,
   --names all PASS. `make test-registry`: no `*** [test-` lines.
   Emitted bytes: old vs new binary, same -o path, six patterns (`^a`, `\Aab`,
   `x$`, `(?m)^a|b$`, `a\z`, `a(b|c)+d`) byte-identical; only
   `--list-syntax` differs, in those two rows. No abi event.
   Note: comparing at different -o basenames differs at line 16 (the path),
   so a before/after must share the basename.
2. Rows [MECH-REACHONLY] (apply_here.md §5) and [RECUR-AUDIT] (§8) filed at
   the head of Backlog; `scripts/plan_lint.sh`: 0 violations.
3. K112 untouched, as ruled.
