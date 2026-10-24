# tests/subst — the subst artifact's checks ([M4-SUBST])

`make test-subst` (in `TEST_SECTIONS`, CI shard 3; mech arm `subst`). The
contract is `docs/spec/subst_api.md`; the design `docs/design/replace_design.md` §R4 (the R4 interface: pieces,
maps, the check, the support unit, replace-all; lane substb2).

## Files

- `run_subst_tests.sh` — the section: the cells (below), the template
  compiler's refusals (exit 1 with a template offset), the reserved-prefix and
  mode refusals, the header contract (`#error` beside another abi's rx block,
  `-o -` self-contained, ASCII output, an rx and a subst header of one prefix
  and `sq`/`sQ` subst headers in one TU), the utf8 template checks, one group-name grammar on both sides, the
  subst-block prefix reservation, the option census (below), `--unset=` unknown on every path, the case-only-prefix
  `#error`; the support unit (`--emit-support` alone, refusals, identical
  bytes, ASCII, the implementation and STATIC builds); then the cells AGAIN
  under ASan+UBSan (replace-all's stack batch, S1500; `ASAN=0` skips, a
  compiler without libasan SKIPs loudly). Module subst-extended rides the
  same section: its cells (`../subst-extended/cells.tsv`) in both passes,
  its refusals under `--features subst-extended`, and the `--features`
  rule of `--subst`.
- `run_subst_tests.py` — compiles every cell's rx (`-p rN`) and template
  (`-p sN`) and the support unit, generates one table, builds the driver once
  against libpcre2 when linkable, and checks every arm. Floors: `REACH_NEED`
  tokens (per cell file, by its directory) each carried by a passing cell
  (K35), and a pcre2-compared count. Template prefixes `utf8:` then `ext:`;
  a `rxt:NAME` pattern is a composed rx from `NAME.rxtin` here.
- `subst_drv.c` — the driver (its header lists every arm): per cell the
  check over the by-name helper's map (and against an abi + 1 record, and
  with no map), the spec's per-match, batch and generic (rx_info.next) recipes,
  replace-all (fits, size-only, exact, one short, ENDED
  iterator), no map and a hand map, the element's refusals (room, a slot
  past ncap, an unknown flag, an end past len, variables), a NOGROUP map
  under STRICT, the element without GAPS, and `pcre2_substitute` (GLOBAL or
  first, UNSET_EMPTY unless STRICT, and REPLACEMENT_ONLY) over the same
  input (EXTENDED for an `ext:` template; never for a P2 `na` cell); a case
  template's scratch at exactly its `sneed` (`scr`); a cell's `LIMIT@START`
  starts both at START. Every out carries scratch. Then the `unit` line
  (flatten's saturation, the helper on number -1 and under MAP_ABSENT).
- `cells.tsv` — the cells: ID FLAGS PATTERN TEMPLATE STRICT LIMIT SUBJECT VARS
  EXPECT P2 LABEL REACH. `P2` states libpcre2's answer where it differs
  (labelled with the subst_api.md §9 row) or `same`.
- `cli_option_census.py` — every option `--help` and `--list-axes` document,
  refused with `--subst` and `--emit-support` by its presence (a default value
  included), each spelling's positive control a pattern compile; an
  undocumented-to-it option fails the run (CHK-7).
- `composed.rxtin` — a composed rx (a delivered group, `ngroups` 0, `ncaps` 2)
  for the `composed` cell: the no-map form refused at the context setup.

- `run_d27.sh` — `make test-subst-d27` (its own section, CI shard 1; NOT in
  the mech arm, it is ~1,500 cases): runs the D27 blinded corpus in `d27/`
  and scores it (every family's case count, no FAIL/FINDING/FIXED?, the API
  drivers and the CLI suite clean). SKIPS loudly without libpcre2.
- `d27/` — the D27 blinded corpus (lane substd27), adopted; own CLAUDE.md.

Without libpcre2 the oracle arms are skipped (`SKIP: subst oracle`); every
other arm runs. Sabotage rows: S1346-S1382 (re-anchored on R4 by substb2;
S1349, the glue's LIMIT cap, and S1364, the glue's VLA batch, were RETIRED
with the glue), S1500-S1504, S1530-S1539 (module subst-extended and the
composed-rx witness, lane substext), and S1580-S1583 (review r1 fixes). Maintenance: update this file when files
are added/removed.
