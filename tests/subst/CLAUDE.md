# tests/subst — the subst artifact's checks ([M4-SUBST])

`make test-subst` (in `TEST_SECTIONS`, CI shard 3; mech arm `subst`). The
contract is `docs/spec/subst_api.md`; the design `docs/design/replace_design.md` §R3.

## Files

- `run_subst_tests.sh` — the section: the cells (below), the template
  compiler's refusals (exit 1 with a template offset), the reserved-prefix and
  mode refusals, the header contract (`#error` beside another abi's rx block,
  `-o -` self-contained, ASCII output, an rx and a subst header of one prefix
  and `sq`/`sQ` subst headers in one TU), the utf8 template checks, the
  subst-block prefix reservation, every pattern option refused with
  `--subst`; then the cells AGAIN under ASan+UBSan (S1364's stack batch
  buffer; `ASAN=0` skips, a compiler without libasan SKIPs loudly).
- `run_subst_tests.py` — compiles every cell's rx (`-p rN`) and template
  (`-p sN`), generates one table, builds the driver once against libpcre2 when
  linkable, and checks every arm. Floors: `REACH_NEED` tokens each carried by a
  passing cell (K35), and a pcre2-compared count.
- `subst_drv.c` — the driver: per cell the bind (and a bind against an abi + 1
  record), the glue at full capacity, size-only, exact, one short, the k = 1
  glue, the LIMIT stop, a dirty iterator, a foreign ncap, an unknown flag, a
  BOUND and an ENDED iterator to the glue, bind with a run short and with an
  rx of no slot, the element with no / too few / unset variables, the
  element without GAPS, and `pcre2_substitute` (GLOBAL or first,
  UNSET_EMPTY or not, and REPLACEMENT_ONLY) over the same input; a cell's
  `LIMIT@START` starts both at START.
- `cells.tsv` — the cells: ID FLAGS PATTERN TEMPLATE UNSET LIMIT SUBJECT VARS
  EXPECT P2 LABEL REACH. `P2` states libpcre2's answer where it differs
  (labelled with the subst_api.md §9 row) or `same`.

- `run_d27.sh` — `make test-subst-d27` (its own section, CI shard 1; NOT in
  the mech arm, it is ~1,500 cases): runs the D27 blinded corpus in `d27/`
  and scores it (every family's case count, no FAIL/FINDING/FIXED?, the API
  drivers and the CLI suite clean). SKIPS loudly without libpcre2.
- `d27/` — the D27 blinded corpus (lane substd27), adopted; own CLAUDE.md.

Without libpcre2 the oracle arms are skipped (`SKIP: subst oracle`); every
other arm runs. Maintenance: update this file when files are added/removed.
