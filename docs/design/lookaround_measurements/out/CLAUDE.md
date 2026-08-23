# docs/design/lookaround_measurements/out — archived probe output

Verbatim output of `../probes/`. **Every file here is written by
`../probes/archive.sh`**, so the provenance header cannot drift between them:
probe path and args, the commit the probe was last changed at, the commit and
branch the run was made from, whether the working tree was clean at run time,
the date, and the python3, libpcre2 and gcc versions. Same intent as
`scripts/measure.sh` / `docs/measurements/` (D35), scoped to this lane.

**R30 M7's rule, inherited through the backrefs lane: `archive.sh` is the ONLY
writer of this directory.** A hand-written header imitating the archiver is
worse than no header — a reader cannot tell a stamped file from an asserted
one without git archaeology. No file here was hand-written. R32 D1/C14 found
the backrefs lane's archiver stamping the WRONG MODULE in all eight of its
files; this lane's stamp was re-scoped at creation and the whole set is
archived in ONE batch from a committed tree, which is the same remedy.

**Every header says `DIRTY`, and that is inherent to the archiver rather than
sloppiness**: `archive.sh` redirects into the file it is about to stamp, so
the file is already modified when `git status --porcelain` runs. What matters
is WHAT the dirty list contains — in every file here it is `out/` files only.

**Evidence for the [M6.6.1] panel (R33), never an oracle.** No check in
`make test` reads anything here; re-run the probe to re-measure.

## The files

| file | probe | what it answers |
|---|---|---|
| `premises.txt` | `probe_premises.sh` | §1: every lookaround spelling's refusal on HEAD, the six registry rows and their D65 `built` column, the `(*` doorway naming module `verbs` for twelve lookaround spellings, `vm_cut`/`vm_atomic` as they are in `src/`, the seam's three entries |
| `spellings.txt` | `probe_spellings.py` | §2 axis A: compile status of every spelling in both oracles, the DISCRIMINATORS (direction, polarity, width, atomicity), the degenerate bodies, quantified lookaround, nesting, and the match-START cells §5 uses |
| `lookbehind_length.txt` | `probe_lookbehind_length.py` | §2 axis B: which bodies compile and with which error number; the TWO-LEVEL preference order; the bisected `max_varlookbehind` default and the fixed-length ceiling; `PCRE2_INFO_MAXLOOKBEHIND` for composite bodies; the subject-start and startpos cells |
| `captures.txt` | `probe_captures.py` | §2 axis C / §3: captures retained by a positive lookaround, discarded by a negative one, unset when a positive one fails after partially capturing; the empty-iteration cells; `\K`'s refusal and the extra-option bit; the budget witness |
| `prefilter_hazard.txt` | `probe_prefilter_hazard.py` | §5: H1/H2/H3 on the erasure, with the SHARP anchored-at-true-start form of H3 alongside the naive one, `erase()` fixture-tested, both vacuity guards |
| `d66_subset.txt` | `probe_d66_subset.py` | §5/§6: the positive control's equivalences, the `(?m)^` self-oracle in both directions, and the sweep that finds the H3 hazard coexisting with a live prefilter-window ceiling |

## Probe defects this lane found by running its own instruments

Recorded here because each produced a confident wrong number, which is worse
than an error, and because every one is a shape this project has catalogued
before:

1. **`PCRE2_INFO_MAXLOOKBEHIND` at the documentation-order index 23** read a
   different field and answered `0` for `(?<=abc)x`. Caught by `la_oracle`'s
   behavioural self-check; the real index (15) was derived by sweeping 0..31
   for the one that answers 3/0/2/5 on four patterns, with a cell that
   separates it from `MINLENGTH`.
2. **`PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK` at 0x8000** did nothing. The probe's
   own guard said "this block measured nothing"; a 32-bit sweep found exactly
   one bit (0x40) that turns `(?=a\K)x` from err 199 into ok, with two
   controls (an unrelated lookbehind error must survive; plain `\K` must stay
   legal).
3. **The budget axis was VACUOUS** — `(?=(a+)+c)x` measured 0.0000 s at every
   size because PCRE2's own required-code-unit start optimization never ran
   the match. Both arms are kept so the vacuity is visible.
4. **The `(?m)^` self-oracle put `(?m)` on ONE ARM ONLY**, so a `$` tail meant
   different things on the two sides and the probe reported three
   disagreements that are about `$`, not about the expansion. Corrected, and
   the uncorrected number is still reported beside the corrected one.
5. **S1's tail set could not see the defect S2 found** — it used `("", "x",
   "\w")` and reported zero for the `(?m)^` row while S2's `$`-bearing set
   reported three. Fixed by scoping every arm.
6. **S3's first population could not contain a qualifying shape.** Every tail
   was nullable, so the emitter raised no clamp site, so condition (a) read
   "none" on all 36 shapes and "0 qualifying" was the only answer the sweep
   could give. A reachability guard now asserts that at least one erasure
   really does stamp `"prefilter-window"`; on the corrected population 20 of
   30 do, and 16 of 30 shapes qualify.
7. **The oracle compared two report shapes as if they were semantics.**
   libpcre2 truncates trailing unset ovector pairs, so a group living only
   inside a negative lookahead is reported as NO group while python reports
   one unset group. `la_oracle.ngroups()` pads both sides to
   `PCRE2_INFO_CAPTURECOUNT` (index also derived by sweep) so a difference in
   the table is a difference in semantics.
