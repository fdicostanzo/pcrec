# seam — memfn-s2a

Lens: seam round trip (manifesto principle 9) + emitted-vs-replaced for a zero-mover unit.
SUBJECT f8c513ec8, BASE adb2d44b7. All runs under /var/tmp/pcrec-pcrec/scratch/crit-memfn-s2a/seam/.

## Findings

### SEAM-1 — CONFIRMED — the MFMEAS record covers the handed NOISE but not the handed VALUE; nothing checks the value the fill hands
- Severity: check/design (no answer or speed effect today: no kit row reads a set). Effort: small (one field in
  the digest line, its ks_ref.py twin, §4.2 text). Blast radius: memfn_sites.c meas_record, ks_ref.py `handed`,
  run_part_measures.sh (C), span_cards.md §4.2.
- Where: src/gen/memfn_sites.c:150-182 (the line is `key TAB state TAB noise_e6`); span_cards.md §4.2 CONTRACT-8.
- The record's stated job (§4.2) is to see "a wrong column, scale or sign that a state count cannot (the S983
  column-swap class)". It does that for noise only. The VALUE side is covered only by the stamp, and the
  stamp is the LOADED SET's digest (`set->digest`), not a digest of what was handed, so a fill that hands the
  wrong value column or scale is not seen by any check.
- Repro (plant): copied memfn_sites.c, changed the fill to hand `r->value_e6 + 1`, built a trace pcrec from
  subj-trace's libpcrec.a (`seam/plant/pcrec`). `PCREC_MF_MEAS_TRACE=1 pcrec -p rx -o pl/x.c
  --measures=fx/ok/fx-f2.tsv --pattern 'x[ab]{3}y'`: the record is `- fx-f2@1:e6ea874204cd1dda 2
  a9057c4ff546ae73` both unplanted and planted. It still equals `ks_ref.py handed` (`2 a9057c4ff546ae73`), and
  x.c/x.h are byte-identical. So run_part_measures (C) passes with every handed value wrong.
- Second repro (equal records, different handed facts; harness lever): a copy of fx-f2 with
  `kit.find_hit.walk.random` value 2500000 -> 2500001 and the header digest left as it was
  (`seam/fx-f2-val.tsv`). `pcrec-harness --harness=measures=` on both files prints the same record
  `- fx-f2@1:e6ea874204cd1dda 0 a94e50ebdb8a54a2`. The harness copies the digest verbatim (cli/main.c:146),
  so the record cannot tell the two handed value sets apart. The loader refuses the edited file, as expected.
- Expected: the record should be a full text image of what was handed. Change the line to
  `key TAB value_e6 TAB state TAB noise_e6 LF` (unit too if wanted; unit and source are text) and change
  ks_ref.py's `handed` the same way. Then a value-column or scale bug in the fill, or in the harness reader, is
  red against the file, as S2905 is for noise. The record format is new in this unit and has one reader
  (run_part_measures.sh $6/$7), so this is the cheapest moment to widen it. The promise itself asked only
  for the noise triple, so this is a finding against the promise's scope, not a divergence from it.

### SEAM-2 — CONFIRMED (by reading) — the sibling on the same entry, `mf_akind.present` (mf_kind_state, MF_SITE_ABI 22), is NOT refused when UNSTATED
- Severity: design/maintenance (it predates this unit; it is the family's inconsistency). Effort: small (an
  `analysis_check` at mf_art_begin beside measures_check). Blast radius: kit (compose.c mf_art_begin,
  presence.c kit_byte_rate); g2 api block.
- Where: memfn.h:1266-1284 (mf_kind_state, mf_akind {present, digest "0 without a payload", payload});
  compose.c:917-939 (mf_art_begin checks `ms` only; `an` is stored and never checked);
  presence.c:51-56 (`present == MF_KIND_PRESENT ? payload : NULL`).
- Two inputs of the same entry follow the same house rule ("an UNSTATED zero is refused", memfn/CLAUDE.md:34)
  and are handled differently. After S2a, a measures row with noise_state 0, or an out-of-range state such as
  3, is refused at mf_art_begin (verified: g2_gen.c:2567-2593 cases). An analysis kind with `present` 0, or
  with any value other than PRESENT, is silently read as ABSENT. Its `digest`/`payload` "0/NULL unless
  PRESENT" shape is not checked either, although it is the exact twin of S2a's "UNMEASURED noise must be 0"
  rule.
- Not this unit's to fix. File it for the kit: one check at mf_art_begin for the analysis object as well, or
  better the shared form in the SIBLING section below.

## SIBLING OF A FAMILY

S2a's `noise_state`/`noise_e6` is the third member of a family I would call "a value whose existence is a
fact". Every member found by grep:

| member | where | form | checked where |
|---|---|---|---|
| analysis kind present + digest/payload | memfn.h mf_akind (ABI 22) | state enum {UNSTATED, PRESENT, ABSENT} + value "0 unless PRESENT" | **nowhere** (SEAM-2) |
| measures row noise | memfn.h mf_measure (ABI 24, this unit) | state enum {UNSTATED, MEASURED, UNMEASURED} + value "0 unless MEASURED" | mf_art_begin measures_check |
| measures row VALUE | mf_measure.value_e6 | no state: a NULL row is NOT HANDED (absence = null, measure_sets §4.1) | n/a |
| pcrec-internal value and noise | ks_measures.h KsMeasRow.value_e6 / .noise_e6 | SENTINEL KS_MEAS_EMPTY (INT64_MIN) | loader |
| finder listing basis | memfn.h mf_finder_row.basis | TEXT `MEASURED|DERIVED|UNMEASURED-DEFAULT` | n/a (output) |
| the other UNSTATED-zero enums (need, body, span_class, verify, core, entry, wfloor, SK) | memfn.h | state-only facts | per-reader checks |

Observations:
- Inside pcrec the fact is a SENTINEL (KsMeasRow.noise_e6 == KS_MEAS_EMPTY). On the seam it is a STATE. The
  fill (memfn_sites.c:92) is the one translation point, and it decides MEASURED from the sentinel, not from
  `set->format`. The rule "every format-1 row is UNMEASURED" therefore holds through a loader invariant in
  another file (ks_measures.c:431 sets EMPTY before the format test; ksgen writes KS_MEAS_EMPTY into the
  pre-parse). It is guarded twice: the S2902 plant and meas_store_check's raw-row compare. So it holds today,
  but the fill does not state the rule the spec writes (§4¶2a "when the set is format 2"). A `set->format == 2 &&`
  in the fill would make it local; that is a judgement call, not a defect.
- The same KS_MEAS_EMPTY sentinel means two different things: "a `-` noise" and "a format-1 row (never
  parsed)". The seam state collapses both to UNMEASURED, which is correct for the kit. A future pcrec-side
  reader of KsMeasRow.noise_e6 that needs to tell them apart must read `format`.
- Should they share one form? Yes, on the SEAM: mf_akind's {present, digest} and mf_measure's {noise_state,
  noise_e6} are one shape, a stated tri-state plus a value bound to it, and the kit should check both with one
  function. That fixes SEAM-2 as a by-product. Inside pcrec the sentinel is fine: it is the digest's own
  encoding (INT64_MIN for empty, measures.md §3.3).

## GENERAL FORM + UNLOCKS

General form: **a stated optional quantity**, `{state ∈ {UNSTATED (refused), STATED-with-value,
STATED-absent}, i64 value, bound}`. It has ONE kit check (refuse UNSTATED and out-of-range states; value in
bound when present; value 0 when absent) and ONE text spelling (`-` or the one decimal spelling; the format-2
`noise_e6` cell already is it). With it comes a TEXT IMAGE of every art_begin input, so the seam can be written,
diffed and re-read by another process (principle 9). The MFMEAS record would become that image or its digest
(SEAM-1).

Unlocks, each with its measurable trigger:
1. **One art_begin input check (measures + analysis).** It closes SEAM-2 and removes one hand-written branch
   per new optional field. Trigger: the next field of this shape on the seam (§4.6's deferred bundle sampling
   noise, or a per-kind confidence on mf_akind), or a kit reader of mf_akind beyond byte-rate. Either is the
   second hand copy of the rule.
2. **A handed-value state (null vs absent visible to the kit).** measure_sets §4.1 says "a kit reader that
   needs the distinction asks by request". With the stated form, NULL rows can be handed as STATED-absent
   at no new mechanism cost. Trigger: the first kit row that reads a set key and must treat a measured NULL
   differently from an absent key (row 1's band, span_pick).
3. **Derived noise (span_cards §4.3/§12.1).** A derived row would carry STATED-absent until a quadrature
   producer exists, then STATED-with-value with no seam change. Trigger: a format-2 derived row with a
   producer AND a reader (§4.3's own D77 trigger).
4. **The full handed-set text image (SEAM-1 widened).** `key value unit state noise` lines, so a
   cross-process differential (the harness lever against the loader, BASE against SUBJECT) compares handed
   facts and not object addresses. It makes the `%p` columns retirable. Trigger: the first kit row that reads
   a value (stage 2 row 1). At that point a wrong handed value is an answer/speed mover with no witness.
   Cheapest now, while the record has one reader.

## PROBED-AND-HELD

- **Every constructor of mf_measure / mf_measures, found by grep** (`git grep -E 'mf_measures?\b'` plus
  `mf_art_begin(`, at SUBJECT, in *.c/*.h/*.py/*.sh): cli/main.c:163-166 (harness reader: UNMEASURED, 0);
  src/gen/memfn_sites.c:93-96 (fill: MEASURED iff noise parsed, else UNMEASURED/0);
  tests/memfn/arm_fixtures.c:1562-1563 (UNMEASURED, 0); memfn/tests/g2/g2_gen.c:2573-2586 (positional
  initializers state all 6 fields; the deliberate UNSTATED case is the test). There is no memset, designated
  initializer or struct copy of an mf_measure. Every other mf_art_begin caller passes `ms` NULL (formhash.c,
  g2 x20, g2_simd x2, g2_win x9, arm_fixtures x10, proof_check x4, proven_check), or passes through
  (arm_fixtures fd_render, docs/dev/lanes/r33_sim/probe.c, a wrapper, not built). Compound parts get P's
  object (`in->meas->kit`, memfn_sites.c:116); a retry attempt rebuilds from the same set. pcrec-bench has
  no mf_measure use (grep, worktrees excluded).
- **MEASURED only from a digest that covers it.** The loader sets noise_e6 = EMPTY on every row before the
  format test (ks_measures.c:431-432), so a format-1 set never yields MEASURED. Check: fx-f1noise (numeric
  noise text on every row) gives MEASURED count 0. The harness lever and arm_fixtures always hand UNMEASURED.
  The committed grid1 `.inc` carries KS_MEAS_EMPTY on all 68 rows (`.format = 1`).
- **Kit check** (compose.c:892-915). Order per row: key `kit.`, value bound, noise state (MEASURED: 0..MAX;
  UNMEASURED: ==0; anything else, including 0 and 3..255 of the uint8_t, refused), duplicate key. Every
  branch returns a refusal string, and nothing is clamped.
- **CONTRACT-5 (no kit internal error from a LOADED file via noise).** Format-2 noise 10^15 loads and compiles
  rc 0, noise 0 loads and compiles rc 0, 10^15+1 is a load refusal (mfixtures f2-noise-bound), and the
  `_Static_assert(KS_MEAS_MAX == MF_MEASURE_MAX)` is in meas_store_check.c:40. For contrast, a value_e6 of
  10^15+1 still reaches "internal error: the memfn kit refused ..." (seam/vbig.tsv). That is K138, known and
  ruled out of this unit.
- **CONTRACT-9 layout.** measures_check walks rows[] at mf_art_begin before any `abi` check. Pcrec and the
  kit are built from one tree, as §4.1 says, and nothing claims otherwise. MF_SITE_ABI reaches no text: its
  only non-comment uses are `abi` assignments and compares (compose.c:1011,1067; presence.c:124; window.c;
  formhash.c:244 assigns it into a site, but the form hash covers rendered TEXT only).
- **MFMEAS against ks_ref.py handed, 9 files**: fx-env, fx-f1noise, fx-f2, fx-messy, fx-rich, fx-store,
  fx-f2-class, fx-f2-noise, committed grid1. Count and noise digest are equal on all 9. fx-f2-class gives a
  different stamp and the same noise digest (class is in values_digest, not in the triples, as intended).
  fx-f2-noise gives a different stamp and a different noise digest. The digest line is injective (keys carry
  no TAB/LF; state words are fixed; decimal). Its key order uses strcmp, the same as python's bytes sort.
  Mapping state 0 and states 3..255 to one word `unstated` loses nothing, because the kit refuses both.
- **Positional readers of MFMEAS.** Only tests/compound/run_part_measures.sh ($2 role, $3 stamp, $4/$5
  addresses, the new $6/$7). The new fields are appended after the `%p` columns. A NULL set prints `-\t-`.
- **Zero movers.** 288 BASE/SUBJECT pairs (576 compiles), the same basename in two dirs, comparing x.c, x.h,
  stdout, stderr and rc. 32 patterns: literals, classes, alternations, anchors, (?i)/(?m)/(?s), backrefs,
  lookaround, \x{100} range, x{1000}, the split compound `^\s+|\s+$`. 9 arms: default, `-e utf8`,
  `--emit-main`, `--engine=vm`, `--engine=dfa`, grid1 against grid1, BASE-grid1 against SUBJECT-fx-f2 (format
  2), BASE `-e utf8 --emit-main` against SUBJECT the same plus fx-f2, BASE-grid1 against SUBJECT-fx-f1noise.
  Result: 0 rc differences, 0 file differences, and every `RX_MEASURES` is `""`. Script: seam/sweep.sh.
- **Text round trip.** Every mf_measures field is TSV-spellable: key, unit and source are TSV cells with no
  TAB/LF, value and noise are decimal, the state is an enum word, and the header fields are header text. So
  the seam could be written and re-read. The record is text except its two `%p` columns, which are
  documented as process-local.
