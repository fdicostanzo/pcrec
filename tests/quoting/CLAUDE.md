# tests/quoting/ — module `quoting` (\Q...\E) corpus

The module's ONLY test corpus, and it is D27-BLINDED by construction:
authored 2026-08-31 in a cell (`scripts/mk_d27_cell.sh qd27` — allowlist
rxt_format.md, testing.md, pcrec.h, prebuilt build/) by an author denied
`src/` and `tests/`, from `man pcre2pattern` + the libpcre2-8 10.46
oracle ONLY, while the implementation lane worked in parallel. The
implementation lane wrote NO tests here (tests derived from the code
inherit the code author's alphabet — D27's premise); its own validation
was a scratch differential probe set, see the [M4-QUOTING] journal entry.

## Files

- `d27/*.rxt` — 9 corpus files, 52 blocks, 95 oracle-checked cells.
  Every block carries a `features` list naming `quoting` (the module is
  NOT in `std1`) PLUS any std1 module its pattern also uses — the .rxt
  `features` directive maps literally to `--features`, which REPLACES the
  default set (the blinded author could not know std1's composition;
  the lists were completed at landing review, 2026-08-31, a config-only
  change — no expectation was touched). Every expectation was MEASURED against libpcre2-8 10.46 through
  `d27/oracle_probe.c`, never reasoned. Discovered by the harness's
  recursive `find tests -name '*.rxt'` like any corpus file.
- `d27/oracle_probe.c` — the oracle: a small CLI over libpcre2-8
  (compile/match/errmsg modes; build with
  `gcc -O2 -o oracle_probe oracle_probe.c -lpcre2-8`). The BINARY is
  not committed.
- `d27/checker.py` — independent re-verifier: a FRESH parser of the
  on-disk .rxt files (not the generator's in-memory state) that
  re-queries the oracle for every cell. Run from `d27/` after building
  the probe: `python3 checker.py` — expect 95/95, 100% agreement.
- `d27/gen_corpus.py` — the generator (deterministic; asserts every
  case's oracle answer matches the author's stated intent before
  writing). Kept for regeneration/audit, not run by `make test`.
- `d27/FINDINGS.md` — the author's record: NO documentation/oracle
  divergence found; two under-specified behaviours resolved empirically
  (`\Qab\E+` repeats only the last quoted char; empty `\Q\E` is
  transparent to quantifier attachment); the two error codes reached
  through quoting (106, 109) recorded as provenance, not wording pins
  (D26).

Mech coverage for the module's two load-bearing parser guards lives in
tests/mech/sabotages/S210_*/S211_* (wired by the implementation lane;
their detectors are reject-table accept-controls, chosen because this
corpus did not exist yet at wiring time — see each row's header).
