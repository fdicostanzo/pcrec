# tests/memfn/ — pcrec-side checks of the kit (pcrec-memory-functions)

The checks pcrec runs ON the in-tree kit (`memfn/`; integration.md §10.5,
§17, §20.3). The kit's OWN tests (G2) live in `memfn/tests/`, not here.

- **run_link_checks.sh** — [MEMFN] R4a: `make test-memfn-link`, a `make
  test` section. Two checks born with the kit's link into libpcrec:
  - **C15**: every global defined symbol of `build/libpcrec.a` (`LIB=`
    overrides) begins `pcrec_` — the kit's are `pcrec_mf_*` through
    `MF_NS` — save `c15_allowlist.txt`. Controls: a probe archive compiled
    in the run with one planted unprefixed symbol must yield exactly it
    (and teaches the run the platform's `_` decoration); a population
    floor (200; 457 measured at R4a); reach (`pcrec_mf_options` present);
    every allowlist entry still exported.
  - **C16**: every file under `memfn/include` and `memfn/src` (`KITDIR=`
    overrides; a CLAUDE.md excepted) carries an `SPDX-License-Identifier`
    from D145's list (0BSD, Unlicense, CC0-1.0, spelled in the script) in
    its first 5 lines and a `Provenance:` line in its first 10, and
    `memfn/PROVENANCE.md` has exactly one row per file with the same
    licence. Control: a synthetic kit with six planted defects must be
    flagged for exactly those.
  The header names what neither sees. Sabotage runs against the real tree
  are recorded in `docs/dev/lanes/memfnskel_report.md`.
- **c15_allowlist.txt** — C15's exceptions, one undecorated symbol per
  line, each with its reason. Born EMPTY at R4a (0 measured).
