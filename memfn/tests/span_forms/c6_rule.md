# Card C6 `span_vector` and C6c: THE RULE (R-47 U5; review 2026-11-22 r79 F2, F5-F8, F12, F13)

Written 2026-11-22 (lane bsu5fix) BEFORE ANY C6 OR C6c TIMING. The rule is the fenced block below; its sha is the first 16
hex of sha-256 over the block's lines (each followed by a newline, the fence lines excluded), the same bytes job 710's
sha covers in `rule_710.md` (`6351bff3901e3955`). `cards.py` computes both shas from these committed files, never from a
literal, and parses the CONSTANTS line from here (`c6selftest` checks both). `cards.py c6selftest` drills the VERDICT on
constructed outcomes. Design of record: docs/design/memfn/block_span.md §8. An edit of the block is a new rule: it moves
the sha, and a results file recorded under the old sha is refused (RECORD).

```
THE RULE (card C6 `span_vector` and its compiler-axis card C6c; R-47 U5, written 2026-11-22 before any timing; it adapts
job 710's rule, rule_710.md, sha 6351bff3901e3955, clause by clause as named at the end):
CLAIM: C6 (layer `on`: -fmemfn-simd=x86-64-v3, gcc -O2): V, the shipped default compile, has NO STANDING LOSS against
  H64@on (the same binary with --memfn=no-span-vector) in any readable cell, on the box the run is on.  V stays CANDIDATE
  until every bench box that runs it reads NO LOSS (Zen 4 here, Zen 1 via main, D144 add. 4); a LOSS on any box blocks
  the level (D155 item 2).  C6c (the SIMD-off layer under the two compilers the bench has SIMD-off arms for: clang -O2,
  `off-clang`; gcc -Os, `off-os`) reads the same claim per layer for plan row [BSPAN-CLANG-DIFF]; it gates nothing.
  Not covered (named gaps): clang -O3 (no bench arm), a -fPIC shared-object build (the bench's arms build
  `-O2 -fPIC -shared`; every cell here is a non-PIC executable), and every box the run is not on.
ARMS: V (build/pcrec, no flag), H64 (build/pcrec --memfn=no-span-vector: today's bytes), H64.b (H64's text timed as a
  third arm, drawing its OWN layout pool: the A/A arm, below).  One frozen binary; the window width and k per pattern
  as cards.py's C6_WIDTH / C6_SITE state them (check_c6 reads k, the block width and the site kind off V's artifact).
CELL = (card, pattern, regime, layer).  Every arm of a cell is timed in LAUNCHES rounds of one launch per arm
  (interleaved, cards.py's launch order); each launch runs a layout variant drawn from its arm's pool of 4 (an in-TU
  prelude and the layer compiler's alignment variant), the draw recorded per launch.
UNIT (fixed now; not a later reader's choice): an arm's reading is the MEDIAN of its LAUNCHES launches' ns/B, and its
  SPREAD is (x[n-1] - x[2]) / median over the launches sorted x[1] <= .. <= x[n] (with n = 5: the middle three, which
  stand for 710's three per-variant readings): one outlier launch at either end cannot widen the floor.
FLOOR = max(FLOOR_MIN, spread(A), spread(B)).  WIN if A < B / (1 + FLOOR); LOSS if A > B * (1 + FLOOR); else TIE.
  A comparison whose FLOOR exceeds SPREAD_MAX is INCONCLUSIVE-NOISE (its arms cannot resolve an effect of twice the
  floor: a bimodal pool or an outlier pair reads here, never as a TIE).
POWER (stated, not gated): "no standing LOSS" admits a per-cell regression below FLOOR_MIN (15 %); under 2 % launch
  noise the critic model of review r79 (meas, drill.py) gives a repeated LOSS per cell with probability 0.075 at 14 %,
  0.505 at 16 % and 0.996 at 20 %.  This box's own noise is what the run reads; the model is not this box.
COMPARISONS per cell: the READING V vs H64 (A = V, B = H64), and the A/A H64.b vs H64 (A = H64.b, B = H64).
RE-TIME: every LOSS and every WIN of the reading, and every non-TIE of the A/A, is re-timed in the same run: all three
  arms of the cell, on a FRESH POOL (cards.py's re-time salt: four new layouts per text, never the first pass's), fresh
  launch draws, the same unit and floor.  It STANDS only if the re-time gives the same verdict; otherwise it is "not
  repeated" and counts as a TIE (both readings listed).  A re-time INCONCLUSIVE-NOISE or NOT-RUN: a reading LOSS stands
  (listed so); a reading WIN does not count (a TIE); an A/A non-TIE stands (it counts toward the A/A rate).
N/A: a cell whose span is never called is N/A: listed with its count, excluded from every count, from the LOSS check
  and from the A/A rate.  The count is the span calls of ONE UNTIMED pass over the cell's subject by an INSTRUMENTED
  build of V's text (a counter in the site's selector; `cards.py dry` builds and prints it), never a timed arm.
  Named cuts, by construction and listed so: near-miss at the window sites with k <= 32 calls the span 0 times (the
  probe lands on each record's miss byte: N/A); near-miss-in is not built at c6_hex1001 (k + 1 > 255: the shift table
  caps at 255, so the plain near-miss already calls the span there at failing depths 0..745); not-warm and
  short-subject are VOID BY METHOD (the kit's approximations, never timed); window k 15, 1001 and scan k 23, 65 are cut
  (both arms render today's bytes: A/A by construction).
CPU-QUIET CONTROL: 710's, unchanged (rule_710.md "CPU-QUIET CONTROL": the quiet sample, CPU7_MAX, NIVCSW_MAX, a void
  launch re-timed up to 2 more times); an arm still short of LAUNCHES valid launches makes both of its cell's
  comparisons INCONCLUSIVE-NOISE.
A/A: at a cell whose A/A has a STANDING (repeated) non-TIE, that cell's reading is INCONCLUSIVE-HARNESS (listed,
  excluded).  THE A/A RATE of a (card, layer) on a box = standing A/A non-TIE cells / A/A-readable cells (non-N/A, run,
  not INCONCLUSIVE-NOISE); it is computed and printed with its single-pass rate beside the verdict.  A rate above
  AA_VOID_MAX, or no A/A-readable cell, makes that (card, layer)'s verdict on that box VOID: the harness failed its own
  control, and the box has not run the card.
WINDOW: no cell starts at or after the job's deadline (710's: min(STOP_AT, the job's start + its cap - 600 s)); a cell
  not started is NOT-RUN, listed; the verdict is prefixed "TRUNCATED: " and NOT-RUN cells count as unreadable below.
READABLE: a cell of the verdict population whose reading is not N/A, not NOT-RUN, not INCONCLUSIVE-NOISE and not
  INCONCLUSIVE-HARNESS.  VERDICT POPULATION of a (card, layer): its non-N/A cells in the timed regimes, not-run included.
VERDICT, per (card, layer, box), FIRST MATCH:
  INCONCLUSIVE-N/A      the verdict population is empty (no cell calls the span)
  VOID                  the A/A rate exceeds AA_VOID_MAX, or no cell's A/A is readable ("A/A FAILED" / "A/A UNREAD")
  LOSS                  a standing LOSS of the reading in any readable cell (listed)
  INCONCLUSIVE-<cause>  fewer than READABLE_MIN of the verdict population is readable; the cause is the most numerous
                        of HARNESS, NOISE, NOT-RUN (a tie in that order)
  NO LOSS               otherwise (for C6: this box counts as run for V's CANDIDATE label)
  Any NOT-RUN cell prefixes the verdict "TRUNCATED: ".  VOID comes before LOSS: a harness that fails its own control
  cannot establish a LOSS either, and a VOID box has not run (V stays CANDIDATE).
RECORD: the result writer writes, as the FIRST line of every C6/C6c results file, `#c6` and tab-separated key=value
  fields: rule=<this block's sha> rule710=<rule_710.md's block sha> form=<mf_form_hash("span-vector")> binary=<sha-256
  of the frozen build/pcrec, 16 hex> cc.<layer>=<sha-256 of cards.py's cc_ident for the layer's compiler, 16 hex> for
  every layer of the file, widths=<pattern:width:site:k,...> and run=<run id>; the decider refuses a file whose rule or
  rule710 sha differs from the live files', or whose header is missing.
REPORTED beside the verdict: W/T/L of the reading per (card, layer), per pattern and per regime; the A/A line (single-
  pass and standing non-TIE counts, the rate, AA_VOID_MAX); the N/A list with counts; the INCONCLUSIVE-NOISE,
  INCONCLUSIVE-HARNESS and NOT-RUN lists; the not-repeated list; the standing WINs (information: a WIN gates nothing).
CONSTANTS: FLOOR_MIN 0.15 (710's); SPREAD_MAX 0.30 (UNMEASURED DEFAULT, twice the floor); AA_VOID_MAX 0.05 (UNMEASURED
  DEFAULT: the critic model's pure-noise A/A rate is ~0.001, its 25 % layout-effect pool ~0.09); READABLE_MIN 0.5 (710's
  half).
710's CLAUSES BY NAME: CLAIM replaced (above); TABLE replaced (the shipped rows T-vwin / T-vscan, block_span.md §3); ARMS
  replaced; CELL replaced (the launches over a pool, UNIT); FLOOR applies (with UNIT's spread); N/A applies (the count
  from the instrumented build, not a depth-profile arm); CPU-QUIET applies unchanged; WINDOW applies; RECORD applies
  (adapted: the header above, no depth profile or walk identity); S dropped with its population (no profile arm); RE-TIME
  applies (adapted: a fresh pool, the A/A included, WINs re-timed everywhere); A/A LINE replaced by the A/A arm and its
  rate; CONTROL dropped (Hspk is not the shipped shape, block_span.md §2); VERDICT replaced (above); REPORTED adapted.
```
