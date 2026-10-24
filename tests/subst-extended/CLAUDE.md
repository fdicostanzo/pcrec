# tests/subst-extended — module subst-extended's cells ([M4-SUBST])

Module `subst-extended` is PCRE2's `SUBSTITUTE_EXTENDED` template dialect
(`docs/spec/subst_api.md` §2¶7-¶14a; conditionals, escapes, case forcing,
the case region of §4¶8 and §4¶22). Its checks run inside `make test-subst`
(`tests/subst/run_subst_tests.sh`), through the same runner, driver and
generic arms as the core cells; see `tests/subst/CLAUDE.md`.

## Files

- `cells.tsv` — the cells, in `tests/subst/run_subst_tests.py`'s columns;
  every template carries `ext:`. Each `same` EXPECT is libpcre2-8 10.46's
  `pcre2_substitute` answer under EXTENDED, and the runner re-asks libpcre2
  on every run. The case-table witnesses (§2¶13a/¶13b), the conditionals,
  the escapes, and four whole-map cells over every code point the oracle
  store's case map lists (`oracle_store/libpcre2-10.46-utf/case-map.tsv`),
  written as raw UTF-8. The ill-formed-UTF-8 case cells are pcrec's own
  (P2 `na`: libpcre2 crashes on them, §9 row 19, upstream U23).
- `gen_cells.py` — how `cells.tsv` was written, from the repo root:
  `python3 -I tests/subst-extended/gen_cells.py
  oracle_store/libpcre2-10.46-utf/case-map.tsv > tests/subst-extended/cells.tsv`
  (libpcre2-8 by ctypes). A developer tool; nothing runs it.

Sabotage rows S1530-S1537, S1539 and S1580 reach through these cells (REACH
tokens); S1536 through the section's refusal rows. Maintenance: update this
file when files are added or removed.
