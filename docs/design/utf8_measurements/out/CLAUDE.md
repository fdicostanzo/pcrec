# docs/design/utf8_measurements/out — archived probe output

**Every file here is written by `../probes/archive.sh`.** That is a rule, not
a habit: R30 finding M7 recorded a header HAND-WRITTEN to imitate the archiver
as *"worse than absent provenance"*, because a reader cannot tell stamped from
asserted without git archaeology. If a number is not in a file with an
archiver header, it did not come from a probe.

**Evidence for the [M5.0] panel, never an oracle.** No check in the suite
reads these files. Re-run the probe to re-measure.

**READ THE `ORACLE HOST` LINE FIRST.** This lane's reference libpcre2 (10.46)
is on the old box, not on the machine that holds this repository, so an
archived UTF number is meaningless without knowing which library answered.
The probe's own header (`libpcre2:`) reports what actually answered; the
archiver's block reports what launched the run.

## Files

| file | oracle | what it settles |
|---|---|---|
| `premises.txt` | pcrec on HEAD (local) | what refuses today; the three source sites the design argues against |
| `invalid_utf.txt` | libpcre2 10.46 (remote) | charter (i): invalid UTF-8, three modes |
| `uprops.txt` | libpcre2 10.46 (remote) | charter (ii): 114 spellings, the UTF-gating question, the interval census, PCRE2's Unicode version |
| `caseless.txt` | libpcre2 10.46 (remote) | charter (iii): simple vs full folding, the closure, fold-before-negate |
| `width.txt` | libpcre2 10.46 (remote) | charter (iv): the lookbehind width UNIT |
| `sizing.txt` | pure construction (local) | charter (v): byte-automaton state counts vs pcrec's caps |
| `divergence.txt` | libpcre2 10.46 + python 3.14 (remote) | charter (vi): 28 cells four ways |
| `divergence_local_py311.txt` | libpcre2 10.37 + python 3.11 (local) | the SAME 28 cells on the other python — a deliberate version comparison |

## FOUR INSTRUMENT DEFECTS THIS LANE FOUND BY RUNNING ITS OWN PROBES

Recorded on the house convention that the defects are worth more than the
count: every one of these produced confident output rather than an error.

**1. A transcript that printed a pattern nobody ran.** `probe_caseless.py`
rendered its pattern column with `.decode("latin-1")`, so the two UTF-8 bytes
of U+00DF appeared as `Ã` plus a control character — a row naming a pattern
that was never compiled. **The failure shape is the silent one**: the RESULTS
were correct, only the label was wrong, and a reader has no way to notice that
a pattern column is lying. Cured by `u8_oracle.pshow()` — a function, so the
next probe cannot forget.

**2. A vacuity guard whose pass condition could not be met.**
`probe_invalid.py`'s F3 guard asked `not isinstance(utf_result, tuple)` to
mean "libpcre2 did not answer". But an error row IS a tuple `('ERRM', …)`, so
the condition was **unsatisfiable** and F3 reported `0 of 9` against a column
that plainly differs on all nine. A guard that cannot fire is
indistinguishable from a guard correctly reporting an absence. **It announced
itself only because it was written in the failing direction** — which is the
whole argument for writing them that way.

**3. `-o /dev/null`, reproduced verbatim after reading the entry that names
it.** pcrec writes `OUT.c` *and* a matching `OUT.h`, so a `/dev/null` sink
tries to create `/dev/null.h` and every **compiling** cell reports "Operation
not permitted" — i.e. reads as a refusal, in a probe whose whole job is
telling refusals from compiles. `../../subroutines_measurements/CLAUDE.md`
already records this exact defect (*"`-o /dev/null` making every COMPILING
cell read 'Permission denied'"*). This lane hit it on its first run anyway.
That is the R30 M6 shape — a defect reproduced verbatim by an author who had
read the entry naming it — and it is the argument for a shared fixture rather
than a shared lesson.

**4. A `find_library` that resolves to a third version.** On this Mac,
`ctypes.util.find_library("pcre2-8")` returns **miniconda's** libpcre2
(10.37), not Homebrew's 10.48 and not the reference 10.46. Every "local
comparison" row would have been silently attributed to 10.48. Caught because
`u8_oracle.header()` prints `version()` read **live** from the loaded library
rather than from the machine's package list — the same never-hand-type-a-
version rule `archive.sh`'s ancestors already carry.

## AND ONE NON-DEFECT WORTH THE SAME SPACE

**The python-version alarm was rung and did not sound.** §7.2 of the design
predicted that the two boxes' pythons (3.11/Unicode 14.0.0 here, 3.14/Unicode
16.0.0 there) could make a corpus disagree with itself. The 28-row divergence
table was therefore re-run under both and diffed: **identical, cell for cell,
on all 28 rows.** The section was rewritten to say so rather than keeping a
plausible hazard nobody had checked. The version axis IS live — `\p{L}` is 648
intervals under Unicode 14.0.0 and 677 under 16.0.0 — but on *property data*,
not on the engine-semantic cells that list is made of.
