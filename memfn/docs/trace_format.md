# MFTRACE — the kit's selection trace (format)

[MEMFN-ROWCON] N1 (`docs/design/memfn/row_contracts.md` §3-§4); the record
set below is N3's, where the gate ENFORCES (§5). Written by
`memfn/src/gate.c`, called from the kit's one selection walk
(`compose.c` `kit_walk`, R4e'.0, over the composer's arms (`select_arm`),
the run compare's rows (`runcmp.c` `rc_row_of`) and the offset-skip
function's `fn_rows[]` (`ofsskip.c` `fn_select`)) and from `mf_use`'s
re-check.

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
    MFTRACE END table=T art=A site=H phase=P chosen=R would_decline=W fields=F [moved_from=M]

- `table`: `arms` (the composer's arm table), `runcmp` (the run compare's
  rows) or `fn` (the offset-skip function's `fn_rows[]`, R4e'.0: its BODY
  slot's walk, one per FUNC part the offset-skip and pre-check sites
  define). A table with SLOTS writes one selection per slot asked; a slot
  that holds no row is not a selection and writes no record (the PREFIX
  slot, born empty, writes none until its first row lands).
- `art`: the art's number in the process (1, 2, … in `mf_art_begin` order;
  pcrec makes one per Job attempt).
- `site`: the site's handle (`arms`; `fn`: the calling site, the
  offset-skip site or the pre-check composite), or `-` (`runcmp`: the run
  walk has no handle).
- `phase`: `define` (the arm walk in `mf_define`, over the site and the
  define hooks; `mf_emit`'s walk is labelled `define` too, though its gate
  reads the define AND use fields, since the one-call entry holds both hook
  sets: r4gfix; the `fn` walk, inside a define, over the calling site and
  its define hooks), `use` (the re-check of the chosen arm in `mf_use`, every
  use and every `mf_call`, over the use hooks), `run` (the run compare's
  walk over one RUN term; it runs inside a define or a use).
- `<what>` on `SEL`: `form=… op=… handoff=…` (arms and fn; the classes of
  those fields of the site), or `run=<class> len=<run_len>` (runcmp).
- `verdict` on `ROW`, what the walk did with the row:
  - `DENIED:<deny>` — skipped by a deny bit (`MF_D_RUN_OVERLAP`), or,
    printed as plain `DENIED`, by the row's own `--memfn=no-<name>` (an
    options.def row, R4e' batch 1); the gate
    is not asked (`gate=-`);
  - `DECLINED` — the gate declined it (`gate=DECLINED`, its fields), and
    the walk moved on; its predicate was not asked, or was asked and does
    not hold;
  - `DECLINED:PRED_HOLDS` — as `DECLINED`, and its predicate HOLDS: without
    the gate this row was the choice. A trace build asks a declined row's
    predicate for this (every predicate is a pure function of the site and
    the hooks); a non-trace build never does;
  - `PRED_FALSE` — the gate passed it and its predicate did not hold;
  - `CHOSEN` — the gate passed it and its predicate held; the walk stops;
  - `RECHECK` — the `use` phase's one row, the chosen arm re-checked.
- `gate`: `PASS`, `DECLINED`, or `-` (not asked). Since N3 the gate
  ENFORCES: a `DECLINED` row is never `CHOSEN`, and a `RECHECK` with
  `gate=DECLINED` is a use the kit REFUSES.
- `fields`: `-`, or every field the gate declines, comma-joined, each
  `name:R1:UNSTATED` (rule 1: the row uses it and it is unstated) or
  `name:R2:<class>` (rule 2: stated, and the row does not serve its class).
  Field and class names are `memfn/src/fields.def`'s.
- `chosen` on `END`: the chosen row, or `-` (no row served: the kit
  refuses the site, and `fields` are the last declined row's, its total
  fallback's, which the refusal text names), or `none` (R4e' batch 1: an
  OPTIONAL slot chose no row, which is the ordinary answer and NOT a
  refusal: the `fn` table's PREFIX walk, and a PREFIX row's named rung
  re-asked by `kit_ask`; `fields` are the last declined row's, or `-`).
- `would_decline` keeps N1's meaning, so N2's census reads an enforcing
  build unchanged:
  - at `define` and `run`: `1` iff the gate MOVED the selection, i.e. the
    first row whose predicate held was declined (N1: "the WARN gate would
    decline the chosen row"). `fields` are THAT row's failing fields and
    `moved_from=` names it; the chosen row is where the walk went instead.
    `0` if nothing moved, `-` with no row;
  - at `use`: `1` iff the re-check failed, i.e. the kit REFUSED the use
    (`fields` are the ones the refusal names), else `0`.
- `moved_from` (trace builds, define/run only): the row the gate moved the
  selection off. Absent when nothing moved.

`grep 'MFTRACE END' | grep 'would_decline=1'` is the would-decline census:
selections the gate changed, plus refused uses. `chosen=-` lines are the
define/run refusals; `chosen=none` lines are not (an optional slot that
chose nothing).

## Reach (at exit)

At process exit, one line per row of each table, in table order, one
per (row, used field, class) cell that was reached, and one REACH_DROPPED
line:

    MFTRACE REACH table=T row=R chosen=N
    MFTRACE REACH table=T row=R field=F class=C n=N
    MFTRACE REACH_DROPPED n=N

- `chosen`: how many selections chose the row (`define` and `run` phases;
  a `use` re-check is not a selection). Every row is listed, 0 included.
- A cell counts, for each `END` with a chosen row, each field the row USES
  at that phase on that site, by the value's class (`UNSTATED` where the
  field was unstated). Only nonzero cells are printed.
- `REACH_DROPPED`, always the last line: `MFTRACE REACH_DROPPED n=N`, the
  selections whose row found no counter slot (the registry holds 32 rows;
  17 exist at R4e'.0).
  N is 0 in a sound trace; a nonzero N means some row's `chosen` above is
  an undercount, and the census (`n2_report.py`) reports it ([MEMFN-ROWCON]
  N4).
- The run walk is asked twice for a FUNC part's run (once declaring its
  helpers, once rendering), so `runcmp` counts are per walk, not per
  compare.
