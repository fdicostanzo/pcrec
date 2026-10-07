# MFTRACE — the kit's selection trace (format)

[MEMFN-ROWCON] N1 (`docs/design/memfn/row_contracts.md` §3-§4). Written by
`memfn/src/gate.c`, called from the two selection walks
(`compose.c` `select_arm` / `mf_use`, `runcmp.c` `rc_row_of`).

## Turning it on

`MF_TRACE` is a compile-time switch, OFF by default. The kit compiles with
`KITFLAGS = $(CFLAGS) …`, so a traced pcrec is

    make BUILD_DIR=<scratch dir> CFLAGS="-O2 -g -DMF_TRACE"

and needs no pcrec source change. Records go to stderr; nothing reaches an
artifact. A trace build is a SCRATCH build: its reach counters are
process-wide (not per art), so it is neither quiet nor re-entrant.

## Records

Every record is one line, `MFTRACE <kind>` then space-separated
`key=value` tokens, keys in the order given. Each selection writes one
`SEL`, one `ROW` per row it evaluated (in table order, up to and including
the chosen one), and one `END`.

    MFTRACE SEL table=T art=A site=H phase=P <what>
    MFTRACE ROW table=T art=A site=H phase=P row=R verdict=V gate=G fields=F
    MFTRACE END table=T art=A site=H phase=P chosen=R would_decline=W fields=F

- `table`: `arms` (the composer's arm table) or `runcmp` (the run compare's
  rows).
- `art`: the art's number in the process (1, 2, … in `mf_art_begin` order;
  pcrec makes one per Job attempt).
- `site`: the site's handle (`arms`), or `-` (`runcmp`: the run walk has no
  handle).
- `phase`: `define` (the arm walk in `mf_define`, over the site and the
  define hooks), `use` (the re-check of the chosen arm in `mf_use`, every
  use and every `mf_call`, over the use hooks), `run` (the run compare's
  walk over one RUN term; it runs inside a define or a use).
- `<what>` on `SEL`: `form=… op=… handoff=…` (arms; the classes of those
  fields), or `run=<class> len=<run_len>` (runcmp).
- `verdict` on `ROW`, what the walk did with the row:
  - `DENIED:<deny>` — skipped by a deny bit (`MF_D_RUN_OVERLAP`); the gate
    is not asked (`gate=-`);
  - `PRED_FALSE` — its predicate did not hold;
  - `CHOSEN` — its predicate held; the walk stops;
  - `RECHECK` — the `use` phase's one row, the chosen arm re-checked.
- `gate`: `PASS`, `DECLINED`, or `-` (not asked). In N1 the gate is in
  WARN mode: a `DECLINED` row is still evaluated and may be `CHOSEN`.
- `fields`: `-`, or every field the gate declines, comma-joined, each
  `name:R1:UNSTATED` (rule 1: the row uses it and it is unstated) or
  `name:R2:<class>` (rule 2: stated, and the row does not serve its class).
  Field and class names are `memfn/src/fields.def`'s.
- `chosen` on `END`: the chosen row, or `-` (no row applied: the kit then
  refuses the site).
- `would_decline`: `1` iff the WARN gate declined the chosen row (its
  `fields` are repeated on `END`), `0` if it passed, `-` with no row.

`grep 'MFTRACE END' | grep 'would_decline=1'` is the would-decline census.

## Reach (at exit)

At process exit, one line per row of each table, in table order, and one
per (row, used field, class) cell that was reached:

    MFTRACE REACH table=T row=R chosen=N
    MFTRACE REACH table=T row=R field=F class=C n=N

- `chosen`: how many selections chose the row (`define` and `run` phases;
  a `use` re-check is not a selection). Every row is listed, 0 included.
- A cell counts, for each `END` with a chosen row, each field the row USES
  at that phase on that site, by the value's class (`UNSTATED` where the
  field was unstated). Only nonzero cells are printed.
- The run walk is asked twice for a FUNC part's run (once declaring its
  helpers, once rendering), so `runcmp` counts are per walk, not per
  compare.
