# docs/design/artsize_impl/ — the [ART-SIZE] STEP 2 lane's probes and archived outputs

Lane `artsize3`, 2026-08-28. The measurement material behind
`../artifact_size_term.md` (the STEP 2 design note). Kept separate from
`../../dev/artifact_size_census/` (STEP 1's own census script) for the
same never-confuse-the-lanes reason `possessify_impl/` and its siblings
are separate: STEP 1 measured the POPULATION, this lane measured the
MODEL and the LEVERS, and a reader must be able to tell which run
produced which number.

- `probes/measure.py` — emits every distinct corpus pattern once
  (`-p rx --features all -o -`) and records, per artifact: comment-excluded
  bytes (`tests/lib/size_count.sh`'s definition, reimplemented and VERIFIED
  byte-for-byte against the shipped shell implementation on six artifacts —
  see the note's §2.1), the emitted VM node count (`rx_LN:` labels), the
  DECLARED table entry count (the sum of every emitted `static const`
  array's declared length — the PRE-EMISSION `states x ncls` quantity, not
  the emitted text bytes, which would make the model circular), goto and
  address-taken-label counts, and the D46 stamps.
      python3 probes/measure.py --out corpus_sizes.tsv --jobs 4
- `probes/fit.py` — the least-squares fit and the error distribution the
  note's §2 reports. Loads `corpus_sizes.tsv`.
- `probes/ksweep.py` — the K curve STEP 1's census (§9) explicitly did not
  take: 15 subjects x K in {1,2,3,4,6,8,12,16,32}. Produces `ksweep.tsv`.
- `corpus_sizes.tsv` — this lane's own run of `measure.py` over 2,771
  distinct corpus patterns (2,487 compiled, 284 refused), 2026-08-28,
  box load1 0.23-1.33. The fit's evidence; the note quotes it throughout.
- `ksweep.tsv` — the K curve. The note's §3 reads the NON-MONOTONICITY
  off this file directly (nested-N8 is 195,443 B at K=3 and 163,386 B at
  K=4), which is why the K rule EVALUATES a ladder rather than descending
  greedily.

The three emitter levers of the census's §7 were priced by a
measurement-only subagent whose numbers are transcribed into the note's
§5 with their provenance; its scratch classifier is not archived here
(the note carries the numbers and the classification rules).
