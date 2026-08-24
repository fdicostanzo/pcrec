# docs/design/subroutines_measurements/out — archived probe output

Verbatim output of `../probes/`. **Every file here is written by
`../probes/archive.sh`**, so the provenance header cannot drift between them:
probe path and args, the commit the probe was last changed at, the commit and
branch the run was made from, whether the working tree was clean at run time,
the date, and the python3, libpcre2 and gcc versions. Same intent as
`scripts/measure.sh` / `docs/measurements/` (D35), scoped to this lane.

**R30 M7's rule, inherited through three lanes: `archive.sh` is the ONLY
writer of this directory.** A hand-written header imitating the archiver is
worse than no header — a reader cannot tell a stamped file from an asserted
one without git archaeology. No file here was hand-written. R32 D1/C14 found
the backrefs lane's archiver stamping the WRONG MODULE in all eight of its
files; this lane's stamp was re-scoped at creation and checked by reading the
first archived file before the rest were run.

**Every header says `DIRTY`, and that is inherent to the archiver rather than
sloppiness**: `archive.sh` redirects into the file it is about to stamp, so the
file is already modified when `git status --porcelain` runs. What matters is
WHAT the dirty list contains — in every file here it is `out/` files only.

**Evidence for the [DD-14] panel, never an oracle.** No check in `make test`
reads anything here; re-run the probe to re-measure.

## The files

| file | probe | what it is evidence for |
|---|---|---|
| `premises.txt` | `probe_premises.sh` | design §1, P1–P14 |
| `spellings.txt` | `probe_spellings.py` | §2 |
| `captures.txt` | `probe_captures.py` | §3.1, §3.4(b), §3.4(c) |
| `atomicity.txt` | `probe_atomicity.py` | §3.2, §2.6, §3.4(d), §3.4(e), §8.1's quant column |
| `leftrec.txt` | `probe_leftrec.py` | §3.3, §3.4(d), §3.4(f) |
| `linkage.txt` | `probe_linkage.sh` | §6.2, PROTOTYPE |
| `prefilter.txt` | `probe_prefilter.py` | §8.3 |
| `population.txt` | `probe_population.py` | §8.4 |

## THE INSTRUMENT DEFECTS THIS LANE FOUND BY RUNNING ITS OWN PROBES

Nine, plus one the compiler caught. Each is recorded with the number it would
have reported, because a defect list that says only "fixed" teaches nothing.
The design's §0.3 carries the same list for the panel; this is the working
record.

1. **`probe_atomicity` T7 measured no retry at all.** Body `a|b|c|d|e|f|g|h`,
   subject picking the LAST alternative, so every call succeeded on its eighth
   try and no call was ever re-entered after a failing follow. Reported LINEAR
   limits (8n+2) and an "atomic control" **higher** than the backtrackable one
   — which reads as *"the atomic linkage costs more"*, the opposite of the
   truth. The retry-forcing shape gives 2ⁿ and a ratio tending to **2.0**.
   **This one would have gone into the design.**
2. **`probe_leftrec` L9 reported a limit it never reached.** Bisected
   [1, 400000] for the first FAILING subject size, found none, printed
   *"largest n = 399999"*. The default depth limit was never hit. Now it says
   so and reports the heap limit (`rc -63`), which is what actually stops
   PCRE2.
3. **`probe_atomicity` died at row 40 of 80.** `cell()` used the oracle's
   `search()`, which RAISES on any negative rc other than NOMATCH.
   `^(?R)*$` on `""` is `rc -52`, so every row after it measured nothing —
   including all of T6 and T7. Fixed by routing through `match_limits()`.
4. **A callout cell fired no callout.**
   `^(?(DEFINE)((a)(?C1)))(?2)$` calls the INNER group, which does not contain
   the callout. Caught by the probe's own "!! NO CALLOUT FIRED" guard, which
   exists because a silent zero here looks like a measurement.
5. **`probe_premises` reported "Permission denied" for every COMPILING cell.**
   `-o /dev/null` makes the header `/dev/null.h`. Three cells that should have
   read *"compiles"* read as an unexplained failure — and those three cells
   are the ones that establish `\g{1}`/`\1`/`\g1` are already-shipped
   BACKREFERENCES, which §2.2's table depends on.
6. **`sr_oracle`'s match-limit self-check was vacuous.** The subject was one
   the pattern MATCHES, so the limit never fired; the check would have
   reported that `pcre2_set_match_limit_8` does nothing. Fixed with a
   non-matching subject AND a control at a huge limit — the second half
   matters, because a cell that always errors is as vacuous as one that never
   does.
7. **`probe_prefilter` could not feed its own subject.** `--emit-main`'s
   generated `main()` reads the subject from `argv[1]`, and Linux's
   `MAX_ARG_STRLEN` caps one argv element at 128 KiB. A ≥1 MB subject never
   reached the matcher — *"Argument list too long"* before pcrec's own code
   ran. Replaced with a file-reading driver.
8. **`probe_prefilter`'s flag check grepped documentation.** `pcrec --help`
   does not list per-optimization `-fno-*` flags, so the check reported a
   problem on every run for a flag that works fine. It now invokes the flag
   behaviourally.
9. **`probe_population` would have counted class escapes as calls.** A naive
   `\g<` scan counts `tests/backrefs/octal_class.rxt`'s `^[\g<1>]$` — where
   that file's own comment says the class doorway makes those four literal
   one-byte escapes — as a subroutine call. Masked with a character-class pass
   that respects escapes and the leading `]` rule.

**And one the compiler caught rather than the probe**: `gen_linkage.py` at
`k = 0` emitted a `goto` to an undefined label. Listed because `k = 0` is the
prototype's own BASELINE control row, and a baseline that does not build is a
baseline nobody checks.

**The shape all nine share** is the one `pcrec-check-design-lessons` records:
an instrument that reports confidently about a space it never entered. The
remedy in every case was a guard that PRINTS its own reachability — which is
why every probe here ends with one and says VACUOUS out loud.
