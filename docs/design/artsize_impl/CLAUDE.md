# docs/design/artsize_impl/ — the [ART-SIZE] STEP 2 lane's probes and archived outputs

Lane `artsize3`, 2026-08-28. The measurement material behind
`../artifact_size_term.md` (the STEP 2 design note). Kept separate from
`../../dev/artifact_size_census/` (STEP 1's own census script) for the
same never-confuse-the-lanes reason `possessify_impl/` and its siblings
are separate: STEP 1 measured the POPULATION, this lane measured the
MODEL, the LEVERS and the gcc COST, and a reader must be able to tell
which run produced which number.

**READ THIS FIRST if you are about to trust a count from `measure.py`.**
Its first version matched only `rx_L<N>:` labels and only `\w`-typed
`static const` arrays, so it could not see the VM hybrid prefilter's
computed-goto machinery at all — `static const void *const
rx_targets_N[11]` jump tables and `rx_s<N>:` state labels. On K41's second
witness that hid 3,108 tables and 3,108 labels and made the size model read
118,240 B for a 1,220,606 B artifact (r40 finding F1). The classifier's own
regexes were the population nobody counted. The fix is structural, not a
widened pattern: it anchors on `= {` and on the emitter's `rx_` prefix
rather than on a type spelling, and it counts label FAMILIES separately so
an unrecognised family reports nonzero in an `olabels` column instead of
vanishing. **The control that catches this class is
`tests/lib/size_count.sh`** — the shipped, byte-exact definition — run on
the same artifact; `measure.py` agrees with it to the byte on both the
self-contained and the split `.c`+`.h` form, including on the witness.

- `probes/measure.py` — emits every distinct corpus pattern once
  (`-p rx --features all -o -`) and records per artifact: comment-excluded
  bytes (`size_count.sh`'s definition), VM nodes `N` (`rx_L`), prefilter DFA
  states `S` (`rx_s`), any other label family (`olabels`), DATA-table entry
  count `E` and POINTER-table (jump-table) entry count `J`, plus the D46
  stamps.
      python3 probes/measure.py --out corpus_sizes.tsv --jobs 4
- `probes/fit2.py` — the FOUR-term two-intercept joint fit the note's §2.3
  reports, and the script that actually produces its coefficients (r40 F5:
  `fit.py` is single-intercept and cannot).
- `probes/fit.py` — the original single-intercept helper; still the source of
  `load`/`ols`/`pct`, which `fit2.py` imports. Not the note's fit.
- `probes/ksweep.py` — the K curve STEP 1's census (§9) did not take:
  15 subjects x K in {1,2,3,4,6,8,12,16,32}. Produces `ksweep.tsv`.
- `probes/gccfit.py` — gcc's cost over a spread chosen to DECORRELATE nodes
  from data-table entries. Produces `gccfit.tsv`. Its log-log node fit was the
  first version's node-cap derivation and is NO LONGER used for that (note
  §4.6): it survives as the evidence for §4.1's per-unit costs.
- `probes/jfit.py` — the JUMP-table term, measured directly on a decorrelated
  grid (`^(<literal of length n over k letters>)x`: varying k moves `J` at
  fixed `N` and `S`). The corpus cannot fit this coefficient — its `J` tops out
  at 210 entries where K41's second witness carries 34,188. Produces
  `jfit.tsv`.
- `corpus_sizes.tsv` — this lane's run over 2,771 distinct corpus patterns
  (2,487 compiled, 284 refused), 2026-08-28, with the CORRECTED instrument.
- `ksweep.tsv`, `gccfit.tsv`, `jfit.tsv` — the three probe outputs above.
- `k41_w1.txt`, `k41_w2.txt` — both K41 witness patterns, verbatim, extracted
  from `../../dev/known_issues.md` rather than retyped. The model's test cases:
  witness 1 is node-replication (the K rule fixes it), witness 2 is
  prefilter-driven (the cap refuses it).
- `levers/` — the census §7 lever pricing: `classify.py` (the span-loop /
  node-skeleton / MRL-guard classifier), `run_popc.sh`, and the population B
  and C results the note's §5 quotes. Archived per r40 F7.
- `probes/axsweep.py` + `axsweep.tsv` — finding S11: the caps' zero-refusal
  claim re-measured off the default axis, over `--engine=vm` and every deny
  flag (emit only, no gcc). 0 over either cap on all ten axes; `-fno-counter`
  is the only one that moves `N` (1,471 → 1,489) and the axis a future emitter
  change would push over the node cap first.
- `probes/bench_acceptance.sh` — the ACCEPTANCE SURVEY OVER pcrec-bench's OWN
  PATTERNS (2026-08-29, the manager's addition to the delivery bar; the note's
  §4.3a carries the table). The surveys behind §4.3a covered this repository's
  populations, and the bench is the first CONSUMER that would meet a refusal
  unannounced: its patterns live in another repo and are compiled under flags
  the corpus never uses. 18 patterns (`bench/email/patterns/` 3,
  `bench/loglines/patterns/` 11, plus the four `email_specimen/*.rx` in THIS
  repo that the bench pins copies of and that neither survey had covered) ×
  the three flag sets `testees/pcrec/configs.toml` actually pins = 54 emits.
  MEASURED: 54 accepted, 0 refused, 0 `_UNROLL_K_WHY` other than `default` —
  no bench pattern reaches even the 120,000-byte code threshold, so the
  ladder never runs on one and the bench's whole exposure to this row is the
  four stamp lines. Emit only, no gcc, and READ-ONLY in the bench (CLAUDE.md's
  scope mandate: one writer each way, and this lane is not its writer).
