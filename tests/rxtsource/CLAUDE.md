# tests/rxtsource — INV-COMPAT, and the head grammar's only witnesses

[DD-13b.W1.1]. The `.rxt` format grew a HEAD; this directory is where the
claim that nothing existing changed meaning stops being a claim.

`make test-rxtsource`, and a section of `make test`. Cheap on purpose:
three parses of the corpus and NO COMPILES OF THE CORPUS, so it does not
compete with `test-corpus` for the box. [DD-13b.W1.2] added a section that
does compile — a handful of fixture targets, single digits — because
building a `.rxt` source cannot be checked without building one.

## Files

- **`run_rxtsource_tests.sh`** — the whole section.
- **`build_c3_store.py`** — **[C3 THREE-WAY VERDICT, 2026-09-10/11, lane `pyrole`]** the store-capture script behind C3's redesign (below): populates ...
- **`fixtures/*.rxtin`** — head-bearing `.rxt` files.
- `name_dashdot.rxtin` — a definition named `cls-upto-64` and one named `ctx.lazy`, each built through `target = <name>`.
- `target_prefix_collision.rxtin` — `a-b` and `a.b`, both mapping to `a_b`.
- `compose_delivers.rxtin` — all three of D89's tiers in one artifact.
- `compose_root_recursion.rxtin` — Q-W2 (D89 point 3): `(?R)` inside a bound definition is refused because the RULING is missing, not the meaning.
- `compose_unknown_name.rxtin` — a by-name call the closure cannot satisfy RE-RAISES `mod_backrefs.c`'s own sentence at its own offset, which is what keeps the four `perr` ...
- `compose_dup_definition.rxtin` — one name declared in two files of the `lib` closure.
- `bench_altwide_0_2.rxtin` — **THE DOGFOOD**: pcrec-bench's altwide@0.2 pattern set as an `.rxt` source, verbatim, with a provenance header (repo, set, version, the bench ...
- **`wave2_keyword.rxtin` is DELETED** (its keyword, `include`, shipped) and **`include_head.rxtin` replaces it**, asserting the acceptance.

## Maintenance

- The census is a **PIN**, not a derivation. When a corpus file is added
  or removed, change `CENSUS_*` and `RUNSH_*` in a reviewed commit that
  says which file moved. A pin that recomputed itself would agree with a
  shrunk corpus by construction.
- The arm hash moves when `run.sh`'s arm chain changes. That is intended
  and is never incidental — the rule lives in the check's own failure
  message, where a person looking at the failure will read it. New line
  kinds go AFTER the END marker and need no re-pin.
- Update this file when a check, a fixture or a deferred row changes role.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__rxtsource.md`.
