# tests/partlayout — [ENTRY-TABLE] E1's checks: the part-layout controls

`make test-partlayout` (in `TEST_SECTIONS`; mech arm `partlayout`). The
controls are `--part-layout=CLASS:V`, `--part-inline-rank=R` and
`--part-residual=V` (`docs/spec/tuning.md` §2.51-§2.53); the tables they feed
are `src/gen/part_layout.c`'s; the design is `docs/design/compound_entries.md`
rev 4 §3.4-§3.6. Every row is reached by SETTING ITS CONTROL on a corpus
artifact with a subject of its class (D163 addendum 11), so no synthetic
witness is needed today.

## Files

- **run_partlayout_tests.sh** — the section's entry point: a scratch dir,
  then `run_partlayout.py`. Env `PCREC`, `CC`, `JOBS`.
- **run_partlayout.py** — the seven sections, each with its independent
  control (its header lists them): (1) the independent evaluator over every
  witness x 25 control settings, the five `--tune` positions included;
  (2) the hand fixtures and the per-class file-wins rule through a `.rxt`
  config block; (3) A1 disjointness at every entry rung, and every layout
  write on a `static` definition; (4) gcc's own H1/H2 refusals; (5) the
  attribute census, totality and per-row populations with floors, the
  seam's copyability; (6) I5 neutrality (refusal, stamps, the decision
  sizes `--warn-emit-bytes` reports) over the population and the near-cap
  list, and the all-`auto` set byte-identical to no control, plus the
  -Werror leg: the population, the near-cap list and `werror.txt` compiled
  at the harness's `-O1 -Wall -Wextra -Werror` under both residual ends;
  (7) T2/TM stated UNREACHED (no measurement set exists). ~45 s at
  `JOBS=8`.
- **evaluator.py** — THE INDEPENDENT EVALUATOR. Links nothing from `src/` and
  reads no pcrec listing: the call graph of an attribute-stripped copy of the
  default artifact (`-O0 -fno-inline`, `objdump -dr`: call targets and
  relocations), the owners' `always_inline` read from the default text,
  copyability asked of gcc (its "can never be copied/inlined" refusal), the
  hand class and rank maps, and tuning.md §5.4's preset rows read from the
  SPEC. Judges the real object's `nm` and the stamps.
- **witnesses.tsv** — the witness artifacts with their HAND class and rank
  maps, written from the emitted C. Records why the empty-language hybrid is
  not a witness (gcc's IPA deletes a `return 0;` part whatever its attribute).
- **fixtures.tsv** — HAND-WRITTEN precedence and held-request expectations
  (the row each subject stops at, the stamp, the WHY).
- **writers.tsv** — the hand class map of every attribute writer (A1-A7, the
  layout table); an attribute on a function no row lists fails the census.
- **population.txt** — the subject population (every 4th corpus VM hybrid
  under 200,000 bytes, every compound; 387 patterns at the lane's branch
  point), held to still carry a subject and to a floor.
- **nearcap.txt** — the ten largest corpus VM hybrids, I5's witnesses.
- **werror.txt** — the -Werror leg's NAMED witnesses: the eight distinct
  patterns behind the 135 cases the test-axes arm lost when `shared` was
  `noinline` alone (gcc -O1 reported the caller's `window`
  maybe-uninitialized). All eight fail on that build, all pass on `noipa`.

## Notes

- **The check is the object, not the listing.** Sections 2 and 5 read
  `--emit-facts`' `part-layout` section, which is pcrec's own account; the
  evaluator (section 1) is what holds that account to the compiled object.
  Sabotage S1113 (a shared row writing the inline text) is the case only the
  object sees.
- **gcc 15.2 accepts `inline __attribute__((always_inline))` on an EXPORTED
  callee under `-fPIC`** (a C99 inline definition), so the design's LK-9
  negative test (gcc refuses it) has no gcc detector; the render's own
  "a mark only after `static `" internal error and section 3's text check
  are the detectors instead.
- **`shared` is `noipa`, not the design's `noinline noclone`**: with
  `noinline` gcc still analyses the body across the call, which both
  produced the -Werror failure above and deleted a `return 0;` part.
- Sabotage rows S1111-S1118 name the arm; each was hand-validated against a
  rebuilt copy (`docs/dev/lanes/e1_report.md`).

Maintenance: update this file when files are added/removed or their roles
change.
