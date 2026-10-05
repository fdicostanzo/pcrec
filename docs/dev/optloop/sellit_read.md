# SEL-LIT desk read: does auto-loses-to-forced-VM hold beyond litrun's densities?

Lane `sellit` (branch `lane/sellit`), 2026-10-05, read-only desk read (D144
addendum 3, round 2 side item). Charter: `gapreport_2026-10-05.md` §2.14 and
its "What would settle each open question" SEL-LIT bullet;
`judgement_gapreport_2026-10-05.md` row 6. No build, no timing run, no ssh.

## Data and method

- **Pin.** The O-83 round-1 wide bench at `c4c70f2c` (abi 59), reports
  `2026-10-05-*-round1-c4c70f2c.tsv`, as already extracted by the gap-report
  tooling (`gapreport/extract.py` -> `cells.json`, `gap.py` -> `gap_rows.json`;
  this lane read o83read's copies of both, unchanged, and wrote nothing
  there). Timings are the reports' `rank` rows: set-grain median over the
  regime's subjects (`n`), arm `pcrec:auto-caps` vs `pcrec:vm-caps`.
- **Which suites have a forced-VM arm.** Only altwide, capability, litrun,
  syntax, utf8 (the five that appear in `gap_rows.json` with
  `forced={pcrec:vm-caps}`). **bounded, loglines and email-specimen have no
  vm arm in this window**, so they cannot be read here (bench question 1).
- **Stamps** (engine, prefilter family, k-set offsets, `REQ_RUN@idx`,
  `REQ_WHY`) come from the gap report's own compile of each pattern. That
  compile was at abi 60 (the o83read tree); the timings are abi 59.
  Disagreement is possible only where K82 (A)/(C) changed an artifact; the
  stamp-diff and `moved_since_pin` columns say where C3 moved a cell.
- **"Literal-led DFA artifact"** = stamp `RX_ENGINE=dfa` (cells where auto
  already selected the VM are the same program as the forced arm and are
  excluded) and `RX_DFA_PREFILTER` in {`memchr`, `run-pinned`, `offset-set`}
  or their `-bounded` forms. `byte-class` and `none` prefilters are
  class-led, not literal-led, and are only used for context below.
- **"VM wins" bar**: ratio auto/vm >= 1.10 AND the arms' min/max do not
  overlap (vm.max < auto.min). The reverse ("auto wins") is the mirror.
  Absolute deltas are quoted beside every ratio (D144 addendum 1): short-call
  cells are ns-scale, so a x1.2 on a 15 ns call is 3 ns and belongs to
  CALL-FLOOR unless it clears that set's own floor cell.
- `match-compliance` is tier C (not scored) and is listed separately.

## Census (literal-led DFA cells, one count per pattern x regime)

| regime | suite | cells | vm wins (>=1.10, clear) | auto wins (mirror bar) |
|---|---|---|---|---|
| throughput | altwide | 6 | 0 | 5 |
| throughput | capability | 13 | 1 (noise-scale, see below) | 5 |
| throughput | **litrun** | 12 | **11** | 0 |
| throughput | syntax | 42 | 0 | 39 |
| throughput | utf8 | 27 | 0 | 18 |
| throughput | **total** | 100 | **12 (11 litrun)** | **67** |
| short search | altwide | 6 | 1 (the `floor` cell) | 5 |
| short search | capability | 13 | 1 | 8 |
| short search | **litrun** | 12 | **9** (all 12 have ratio > 1; `floor` x1.07 and `lit-l4` x1.08 fall under the bar) | 0 |
| short search | syntax | 42 | 3 | 22 |
| short search | utf8 | 27 | 6 | 8 |
| short search | **total** | 100 | **20 (9 litrun, 11 elsewhere)** | **43** |

`match-compliance` (tier C, unscored): all 59 literal-led DFA cells are the
`whole-subject` form (a separate artifact); vm beats auto on 58/59, median
delta 4.4 ns/call (range -0.5 .. +10.5). It is a per-call-floor population
and is excluded from the verdict.

## Every cell where pcrec-vm clearly beats pcrec-auto on a literal-led DFA artifact

Column notes: `prefilter row` = RX_DFA_PREFILTER family; `RX_DFA_PREFILTER_OFFSETS`
(`*` marks the scanned offset); `REQ_RUN` hex run `@idx`; `REQ_WHY`. "K82 handoff"
reads `docs/design/litscan_k82h.md` §(e): the handoff applies where `req_admit`
returned EMITTED/SET_LEADS with a run, i.e. `REQ_WHY=emitted`; `dominated` rows
have the pre-check elided and the handoff does not apply. K82's handoff landed
at abi 61 AFTER this pin (k82halpha_report.md; known_issues K82 (B), K88).

### Throughput (ns/B; ratio = auto/vm) 

| suite | pattern | auto | vm | ratio | delta | text / density | prefilter row (family; k-set offsets; req_run@idx; REQ_WHY) | K82 handoff |
|---|---|---|---|---|---|---|---|---|
| capability | `wild-semdiv-dollar-trailing-newline-pcre2` | 0.0000 | 0.0000 | x1.49 | 0.0000 ns/B | mixed log+http+source+prose grammar (real-ish) | run-pinned-bounded; 0,1*,2; 616263@1; dominated [C3 moved at pin] | n/a (WHY=dominated) |
| litrun | `lit-l31` | 0.4775 | 0.1024 | x4.66 | 0.3751 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | offset-set; 0,9*; 78797a4142434445@2; emitted | MAY MOVE (WHY=emitted); K88: mat +0.149 ns/B measured |
| litrun | `lit-l40` | 0.2586 | 0.0689 | x3.76 | 0.1897 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | offset-set; 0,9*; 464748494a4b4c4d@4; emitted | MAY MOVE (WHY=emitted) |
| litrun | `lit-l16` | 0.5727 | 0.2655 | x2.16 | 0.3072 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | run-pinned; 0,5,6,7,8,9*,10,11,12; 666768696a6b6c6d@4; dominated | n/a (WHY=dominated) |
| litrun | `lit-l10` | 0.6167 | 0.3709 | x1.66 | 0.2458 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | run-pinned; 0,2,3,4,5,6,7,8,9*; 636465666768696a@7; dominated | n/a (WHY=dominated) |
| litrun | `ctrl-abc-dollar` | 0.0003 | 0.0002 | x1.56 | 0.0001 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | run-pinned-bounded; 0,1*,2; 616263@1; dominated | n/a (WHY=dominated) |
| litrun | `lit-l7` | 1.8081 | 1.2134 | x1.49 | 0.5947 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | run-pinned; 0,1*,2,3,4,5,6; 61626364656667@1; dominated | n/a (WHY=dominated) |
| litrun | `lit-l8` | 1.6143 | 1.1640 | x1.39 | 0.4503 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | run-pinned; 0,1*,2,3,4,5,6,7; 6162636465666768@1; dominated | n/a (WHY=dominated) |
| litrun | `lit-l3` | 1.9351 | 1.4559 | x1.33 | 0.4791 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | run-pinned; 0,1*,2; 616263@1; dominated | n/a (WHY=dominated) |
| litrun | `lit-l4` | 1.7782 | 1.3469 | x1.32 | 0.4313 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | run-pinned; 0,1*,2,3; 61626364@1; dominated | n/a (WHY=dominated) |
| litrun | `floor` | 1.7723 | 1.3691 | x1.29 | 0.4032 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | memchr; none; none; dominated | n/a (WHY=dominated) |
| litrun | `lit-l2` | 1.9067 | 1.7065 | x1.12 | 0.2002 ns/B | tiled dense (mat/fbf/lbf, every window a hit or edge-miss, period L) | offset-set; 0,1*; 6162@1; dominated | n/a (WHY=dominated) |

### Short-subject search (ns/call; ratio = auto/vm) 

| suite | pattern | auto | vm | ratio | delta | text / density | prefilter row (family; k-set offsets; req_run@idx; REQ_WHY) | K82 handoff |
|---|---|---|---|---|---|---|---|---|
| altwide | `floor` | 13.56 | 10.09 | x1.34 | 3.48 ns | short typed fields <=512 B | memchr; none; none; dominated | n/a (WHY=dominated) |
| capability | `wild-semdiv-dollar-trailing-newline-pcre2` | 13.12 | 8.32 | x1.58 | 4.80 ns | short typed fields <=512 B (real validators/secrets) | run-pinned-bounded; 0,1*,2; 616263@1; dominated [C3 moved at pin] | n/a (WHY=dominated) |
| litrun | `lit-l31` | 32.87 | 12.71 | x2.59 | 20.16 ns | short typed fields <=200 B (hit/near-miss, boundary L-1) | offset-set; 0,9*; 78797a4142434445@2; emitted | MAY MOVE (WHY=emitted); K88: mat +0.149 ns/B measured |
| litrun | `lit-l40` | 35.55 | 17.38 | x2.05 | 18.17 ns | short typed fields <=200 B (hit/near-miss, boundary L-1) | offset-set; 0,9*; 464748494a4b4c4d@4; emitted | MAY MOVE (WHY=emitted) |
| litrun | `lit-l16` | 20.55 | 12.27 | x1.68 | 8.28 ns | short typed fields <=200 B (hit/near-miss, boundary L-1) | run-pinned; 0,5,6,7,8,9*,10,11,12; 666768696a6b6c6d@4; dominated | n/a (WHY=dominated) |
| litrun | `ctrl-abc-dollar` | 15.18 | 9.17 | x1.65 | 6.00 ns | short typed fields <=200 B (hit/near-miss, boundary L-1) | run-pinned-bounded; 0,1*,2; 616263@1; dominated | n/a (WHY=dominated) |
| litrun | `lit-l10` | 16.47 | 13.05 | x1.26 | 3.41 ns | short typed fields <=200 B (hit/near-miss, boundary L-1) | run-pinned; 0,2,3,4,5,6,7,8,9*; 636465666768696a@7; dominated | n/a (WHY=dominated) |
| litrun | `lit-l8` | 17.43 | 13.88 | x1.26 | 3.55 ns | short typed fields <=200 B (hit/near-miss, boundary L-1) | run-pinned; 0,1*,2,3,4,5,6,7; 6162636465666768@1; dominated | n/a (WHY=dominated) |
| litrun | `lit-l7` | 17.69 | 14.30 | x1.24 | 3.39 ns | short typed fields <=200 B (hit/near-miss, boundary L-1) | run-pinned; 0,1*,2,3,4,5,6; 61626364656667@1; dominated | n/a (WHY=dominated) |
| litrun | `lit-l2` | 18.58 | 16.02 | x1.16 | 2.57 ns | short typed fields <=200 B (hit/near-miss, boundary L-1) | offset-set; 0,1*; 6162@1; dominated | n/a (WHY=dominated) |
| litrun | `lit-l3` | 18.30 | 15.89 | x1.15 | 2.42 ns | short typed fields <=200 B (hit/near-miss, boundary L-1) | run-pinned; 0,1*,2; 616263@1; dominated | n/a (WHY=dominated) |
| syntax | `anc-dollar` | 11.26 | 9.07 | x1.24 | 2.18 ns | tiny typed fields <=256 B (3-12 B typical) | offset-set-bounded; 0,2*; 646f6e65@0; emitted | MAY MOVE (WHY=emitted) |
| syntax | `anc-z-uc` | 11.24 | 9.09 | x1.24 | 2.15 ns | tiny typed fields <=256 B (3-12 B typical) | offset-set-bounded; 0,2*; 646f6e65@0; emitted | MAY MOVE (WHY=emitted) |
| syntax | `anc-z-lc` | 9.83 | 8.45 | x1.16 | 1.37 ns | tiny typed fields <=256 B (3-12 B typical) | offset-set-bounded; 0,2*; 646f6e65@0; emitted | MAY MOVE (WHY=emitted) |
| utf8 | `lit-run-3` | 9.66 | 7.60 | x1.27 | 2.06 ns | short typed multibyte fields <=512 B | offset-set; 0,1*; 97a5e69cace8aa9e@7; emitted | MAY MOVE (WHY=emitted) |
| utf8 | `lit-nearmiss-run` | 9.65 | 7.61 | x1.27 | 2.04 ns | short typed multibyte fields <=512 B | offset-set; 0,1*; 97a5e69cace8aa9e@7; emitted | MAY MOVE (WHY=emitted) |
| utf8 | `alt-nearmiss` | 10.95 | 9.34 | x1.17 | 1.61 ns | short typed multibyte fields <=512 B | offset-set; 0,1*; e697a5e69cac@5; emitted [C3 moved at pin] | MAY MOVE (WHY=emitted) |
| utf8 | `alt-shared-char` | 15.24 | 13.22 | x1.15 | 2.02 ns | short typed multibyte fields <=512 B | offset-set; 0,1*; e697a5e4@2/fffffffd; emitted [C3 moved at pin] | MAY MOVE (WHY=emitted) |
| utf8 | `lit-1ch-3b` | 11.13 | 9.69 | x1.15 | 1.44 ns | short typed multibyte fields <=512 B | offset-set; 0,1*; e697a5@2; emitted [C3 moved at pin] | MAY MOVE (WHY=emitted) |
| utf8 | `ci-moskva` | 13.03 | 11.47 | x1.14 | 1.56 ns | short typed multibyte fields <=512 B | memchr; none; none; dominated | n/a (WHY=dominated) |

## Reading

1. **Throughput: the sign holds only on litrun.** 11 of the 12 wins are
   litrun. The twelfth, capability `wild-semdiv-dollar-trailing-newline-pcre2`
   (x1.49), is `abc$` over mixed prose at < 0.0001 ns/B for both arms: a
   ratio of two memory-speed numbers, not a cost anyone pays. litrun's own
   `ctrl-abc-dollar` (the same pattern) is 0.0003 vs 0.0002 ns/B. On the
   real-ish text sets the mirror holds hard: syntax 39 of 42 cells and utf8
   18 of 27 are won by auto, 67 of 100 overall against 12.
2. **What makes litrun's densities synthetic.** Its 27 throughput subjects
   are tiled `mat`/`fbf`/`lbf` units of period L (NOTES.md): every L-byte
   window is a full match or an edge-miss, so the prefilter's candidate rate
   is 1/L, the DFA re-enters at every window, and no subject has sparse
   candidates. The `floor` pattern (a single-byte memchr) loses x1.29 on the
   same subjects (1.77 vs 1.37 ns/B), i.e. a good part of litrun's gap at
   L <= 8 is the auto path's per-candidate cost at maximum candidate rate,
   not literal-run speed. The cells where literal length itself matters are
   L >= 16 (lit-l16 x2.16, lit-l40 x3.76, lit-l31 x4.66 with the 0.1 ns/B VM
   memcmp), and those are the cells with no sparse control anywhere in the
   bench.
3. **Short search: no real-text case.** 20 wins: 9 litrun (6-20 ns/call on
   l16/l31/l40/ctrl; 2.4-3.6 on the rest) and 11 elsewhere, every one of them
   1.4-4.8 ns/call. altwide's `floor` cell (no literal, memchr, x1.34 =
   3.5 ns/call) shows that scale is the auto path's per-call entry term
   (CALL-FLOOR, §2.16), not a literal-selection effect; syntax `anc-*`
   (2.2 ns) and utf8 `lit-*` (1.4-2.1 ns) sit inside it. The one non-litrun
   cell above it is capability `wild-semdiv-...` (4.8 ns, the same `abc$` /
   run-pinned-bounded row as litrun's `ctrl-abc-dollar`, 6.0 ns, and
   `moved_since_pin` by C3). Auto wins 43 short-search cells of 100.
4. **Handoff exposure.** Wins with `REQ_WHY=emitted` that the abi-61 handoff
   may already have moved: litrun lit-l31, lit-l40 (offset-set, run emitted),
   syntax anc-dollar/anc-z-uc/anc-z-lc, utf8 lit-run-3/lit-nearmiss-run/
   alt-nearmiss/alt-shared-char/lit-1ch-3b. Measured: `lit-l31` mat REGRESSED
   +0.149 ns/B under the handoff (K88), so that cell's gap widens, not
   closes; `lit-l40` and the short-search cells were not in the k82halpha
   arm set. Every `dominated` row (all of litrun l2-l16, ctrl, floor;
   capability semdiv; utf8 ci-moskva; altwide floor) is untouched by the
   handoff.

## Verdict

**SYNTHETIC ONLY.** Throughput: 11 of 12 vm wins are litrun, the other is
sub-0.0001 ns/B; auto wins 67 of 100 literal-led throughput cells. Short
search: 9 of 20 wins are litrun; the other 11 are 1.4-4.8 ns/call, the
CALL-FLOOR scale (altwide `floor` shows 3.5 ns with no literal at all); auto
wins 43 of 100. Mixed would need a real-text cell with an unambiguous
ns/B-scale vm win; there is none among the five suites that carry a vm arm.
Unread: bounded, loglines, email-specimen (no vm arm). The row should close
as synthetic, with one named residual below.

## If it were selected anyway: what a [SEL-COST] row would need

Only if a sparse-text control (below) comes back vm-faster. In
first-match-table terms (`dfa_pfs[]`/`DFA_SELECT` idiom: ordered predicate
rows, first passing non-denied row executes), one row above the DFA rows:

- **keys on (all compile-time facts):** the whole pattern is ONE exact
  literal (no class, no alternation), literal length L >= L0 with L0 in the
  16..31 band the data brackets (l10 x1.66, l16 x2.16; L < 8 is the
  per-candidate term, not the literal), `RX_DFA_PREFILTER` in
  {offset-set, run-pinned}, window/run emitted from a `req_admit` row, and
  not denied (a new `-fno-sel-vmlit` deny bit).
- **cannot key on density**, the property that decides it: candidate rate is
  a runtime property of the subject, and the compile-time predicate has no
  access to it. That is why the sparse control is the gate.
- Selection target: `RX_ENGINE=vm` with the S2a literal-run lowering.
  Everything else (D77, D119 "algorithmic only" bar) says this would be a
  SELECTION row, not a new engine; its cost model belongs with [SEL-COST].

## Bench-only questions (for the manager to relay)

1. Do bounded, loglines and email-specimen have, or can they cheaply be given,
   a `pcrec-vm` arm? They hold the real-text populations this read cannot
   see (the gap report's §3 has litrun alone with no scalar ceiling).
2. **The sparse control:** one L=16 and one L=40 exact literal over
   non-tiled prose/log text where the literal is rare (candidates per KiB in
   single digits), auto vs vm. litrun has no such subject; this is the one
   measurement that would turn "synthetic only" into a verdict.
3. litrun `floor` is a memchr over subjects where the floor byte recurs every
   L bytes (fbf), so it is dense by construction; confirm that reading, as it
   decides how much of the L <= 8 gap is the per-candidate term.
4. Why is the whole-subject `match-compliance` vm arm faster on 58/59
   literal-led cells (median 4.4 ns/call)? Unscored tier C, so no pcrec work
   hangs on it; it only matters if the answer is "auto's whole-subject
   artifact carries a fixed entry term" (CALL-FLOOR).
