# Lane rxtread: one `.rxt` grammar for `oracle` and `var` (report)

Lane rxtread (sonnet), branch `lane/rxtread`, 2026-10-10. Plan row `[RXT-READERS]`.

## 1. Census

- Corpus (`*.rxt`, `*.rxtin`): the only `oracle` lines are `oracle pcre2` and `oracle pcre2/10.46` (docs/design/startset/edge/*.rxt, one fixture). No hyphenated defname, no `oracle none` in any block or file.
- Real hyphenated engine ids exist outside the corpus: `pcre2-interp` and `pcre2-dfa` are the bench's testee/oracle slugs (tests/bench/compare results; `variant` already takes a defname for the same reason, per the comment on `oracle_ref_ok`). `OracleId` names in tests/oracle are `libpcre2` (the hyphen appears only in store directory names, which are not `.rxt` engine-refs).
- Meaning of `oracle none <reason>`: format_design.md 2.9 gives it one, at file level or block scope (a counted, printed skip, AR-3). The census did not contradict the brief's framing.

## 2. Ruling as applied

- A hyphenated engine id is real, so all three legs accept a `defname` engine half (`pcre2-dfa`, `pcre2-dfa/10.46`).
- `oracle none <reason>` is accepted in a block by all three legs (counted skip); bare `oracle none` is refused by all three, class `value-shape`.
- `var <ident> "<value>"` and `var-unset <ident>`: malformed lines (`var 1x "v"`, `var a b`, `var-unset a b`) are refused by all three, class `value-shape`.

Changes: leg A `src/parse/rxt_source.c` (new `var_line_ok`, called where `var`/`var-unset` were skipped; no emitted text changes, no abi event); leg B `tests/harness/run.sh` (oracle regex, `none` arm, malformed-`var` arm so the class agrees); leg C `tests/harness/verify_rxt.py` (oracle regex, `none` arm). Spec: `docs/spec/rxt_format.md` 3.1 para 2, 1.5 paras 12-13 (same paragraphs, numbering unchanged).

## 3. Fixture table (tests/rxtsource/fixtures, driven from run_rxtsource_tests.sh)

| fixture | cell | A | B | C |
|---|---|---|---|---|
| oracle_forms_accept | bare, versioned, hyphenated, hyphenated+version, `none <reason>` in blocks | accept | accept | accept |
| oracle_none_bare | `oracle none` | value-shape | value-shape | value-shape |
| oracle_bad_engine | `oracle 1pcre2` | value-shape | value-shape | value-shape |
| oracle_empty_version | `oracle pcre2/` | value-shape | value-shape | value-shape |
| var_bad_name | `var 1x "v"` | value-shape | value-shape | value-shape |
| var_unquoted | `var a b` | value-shape | value-shape | value-shape |
| var_unset_extra | `var-unset a b` | value-shape | value-shape | value-shape |

Classes are read off each leg's own output by `check_refusal_all3`. The var accept cells already existed (`var_bindings_accept`).

## 4. Validation

- `make strict`: rc 0.
- `make test-rxtsource` (after the fixes): 298 passed, 0 failed (first run had 5 failures that found two real leg gaps: B/C treated bare `oracle none` as an engine named `none`, and B classed malformed `var` as `unknown-token-in-scope`; both fixed).
- Full `make test`, `-j4 -Otarget`: OWED. Log `worktrees/rxtread/build/lane/test.log`, completion line `DONE rc=N`; verdict is `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` (empty = green).
- `make test-spec-history`: see handback.
