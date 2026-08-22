# docs/design/backrefs_measurements — the [M6.5.1] design lane's instruments

The measurements behind `../backrefs_design.md` (module `backrefs`: numeric
`\1`..`\99` with PCRE2's octal disambiguation, the `\g` and `\k` spellings,
`(?P=name)`, and `(?J)`/DUPNAMES, which the [M6.5] row rules is implemented
by this module).

**NOTHING IN THIS LANE READS A BACKREFERENCE THROUGH PCREC, BECAUSE PCREC
CANNOT COMPILE ONE.** That single fact shapes the whole directory and a reader
should hold each instrument to it: an arm that claims to measure pcrec's
backref behaviour would be measuring something else. What the in-pcrec arms
here actually do is measure a SEPARATE AXIS on a pattern pcrec CAN compile —
the prefilter axis (`--engine=vm` vs the default, which stamps
`RX_VM_PREFILTER "none"` vs `"hybrid"` for the identical pattern), the
caseless-fold axis (`-i '[X]'` vs the explicit pair), and the expansion's
OUTPUT (`aa|bb` is a pattern today; `(a|b)\1` is not). Each of those is an
exact measurement of the thing the design rules on, obtained without the
construct existing.

Kept separate from `../assertions_measurements/`, `../eng_brep_measurements/`
and their siblings for the reason those are separate from each other: never
confuse one lane's numbers with another's. This lane borrows exactly one file
rather than copying it — `../eng_brep_measurements/probes/pcre2_ctypes.py`,
through `probes/br_oracle.py` — on `probe_z_oracle.py`'s rule that a lane
which re-implements the binding it depends on cannot detect that the original
moved.

## The instruments, and what kind of evidence each produces

- **`probes/br_oracle.py` — NOT A PROBE, the ORACLE HELPER.** Adds the three
  things `pcre2_ctypes.py` does not expose and this lane's questions need:
  compile-time error NUMBERS (the octal question is answered by 115 vs 151 vs
  acceptance, and the binding collapses every failure into one exception
  string), `PCRE2_INFO_NAMETABLE` (the construct `rx_info.groups` mirrors),
  and three option bits. **Every option-bit VALUE is asserted BEHAVIOURALLY at
  import** (`SELFCHECK`), never trusted from a header this box does not have —
  a wrong constant would silently measure the wrong feature, and every probe
  refuses to run if `SELFCHECK` is non-empty.
- **`probes/probe_br_semantics.py` — MEASURED, BOTH ORACLES.** 42 cells across
  eight families (unset, empty, self-reference, forward reference, quantified,
  nested rewrite, startpos, caseless), plus a `PCRE2_MATCH_UNSET_BACKREF` arm
  that prices the option the design declines. Its DIVERGENCE column is the
  deliverable, not a side effect: 10 of 42 cells disagree with python3 `re`,
  and every one of them is python REFUSING A PATTERN PCRE2 COMPILES.
- **`probes/probe_octal_rule.py` — MEASURED, libpcre2 + in-pcrec.** Four axes,
  and the one that matters is B: every accepted multi-digit form carries a
  DISCRIMINATOR subject, because "it compiled" does not distinguish a
  backreference from an octal literal and the whole question is which one it
  is. Axis D drives the SHIPPED `build/pcrec` on the class position, which is
  base syntax (FIX-3/K13) and is therefore the design's must-not-change
  baseline. **Its own first run reported every class cell as "refuses"**
  because `-o /dev/null` makes pcrec write `/dev/null.h`; it uses a real
  temporary directory now.
- **`probes/probe_spellings.py` — MEASURED, BOTH ORACLES.** 25 spellings, each
  with a discriminator. Its second block is the one the registry needs: a
  SUBROUTINE call re-runs the group's pattern, so `^(a|b)\g<1>$` matches
  `"ab"` while `^(a|b)\g{1}$` does not — which is how "the `\g` doorway
  carries two different constructs" became a measurement instead of a claim.
- **`probes/probe_dupnames.py` — MEASURED, libpcre2 only, BY NECESSITY.**
  python3 `re` has no `(?J)` and no `\k`, so this probe is single-oracle and
  says so in its own first line — which is itself the D27 author's answer for
  every DUPNAMES cell. Three questions: the name table's order (it is
  `(name asc, number asc)`, i.e. the [M6.5] row's ruled pcrec layout is
  libpcre2's own), the refusal matrix, and the resolution rule, whose 18 cells
  are chosen to SEPARATE four candidate rules rather than to confirm one.
- **`probes/probe_caseless_fold.py` — MEASURED, libpcre2 + in-pcrec, ALL 256
  BYTES.** Axis A asks libpcre2 which bytes a caseless backreference compare
  folds; axis A′ asks the shipped compiler the same about `cls_casefold`. The
  two sets are identical, which is what lets the design say the seam entry
  reuses pcrec's own fold rather than choosing one. **Its own first run
  reported all 256 bytes DISAGREEING** — it was diffing emitted C past a
  filter that stripped comments only, so it compared the `.flags` stamp and
  the embedded pattern text and never a transition table. The corrected
  filter's derivation is written into the function.
- **`probes/probe_prefilter_cost.sh` — MEASURED, artifact benchmark, and the
  measurement is EXACT rather than a proxy.** Both arms compile the IDENTICAL
  pattern with the IDENTICAL engine and differ only in the prefilter, because
  the prefilter is a separate axis from the construct. It carries a POSITIVE
  CONTROL (if both arms stamp the same `RX_VM_PREFILTER`, the row is comparing
  an artifact with itself and is skipped rather than reported as 1.00x) and a
  BELOW-RESOLUTION guard whose rows are a RESULT, not a failure: for two of
  five idioms the erased approximation matches at offset 0 and filters
  nothing. **Three defects it had, all found by running it**: `sed 's/\\1//'`
  erased backrefs to EPSILON rather than to the referenced sub-pattern (a
  different, unsound approximation); `/bin/sh`'s `echo` interpreted `\b` and
  `\1` as escapes, silently compiling the dupword arm with both word
  boundaries gone; and the filler contained the same word twice in a row, so
  the "nomatch" subject was not one.
- **`probes/probe_erasure_hazard.py` — MEASURED, libpcre2.** The soundness
  half of the prefilter question, which the timing probe cannot ask: is the
  erasure a SUPERSET (FALSE-NEG column, zero in all seven families — so a
  `nomatch` verdict is trustworthy) and does it report the SAME SPAN (SPAN
  DIFF column, large in six of seven — so the hybrid's exact window is not
  available). It carries a **VACUITY GUARD** because its own first run
  reported the `tag` family at 100% selectivity over a population containing
  zero positives, and a structured subject generator for families whose
  positives a random walk never produces.
- **`probes/probe_expand_cost.py` — MEASURED, IN-PCREC, and it is the reason
  the design declines the expansion.** It hands the REWRITE'S OUTPUT to the
  shipped compiler, because `(a|b)\1` does not compile today and `aa|bb` does.
  Its §0 arm is the decisive one and is three lines long: a backreference
  pattern is capture-bearing by construction, captures are on by default, and
  `forces_captures` therefore sends it to the VM whatever the backrefs row
  says — so the expansion's only customer is a `--no-captures` build. §2
  BISECTS the DECLINE boundary on the shipped compiler, with both endpoints
  checked first so the bisection is known to bracket one.
- **`probes/archive.sh` — not a probe, the ARCHIVER.** Every file in `out/` is
  written by it, so one provenance header covers them all and a number can be
  traced to a run rather than to a claim. Copied from
  `../assertions_measurements/probes/archive.sh` and re-scoped, including its
  R30 M7 rule: **the archiver is the ONLY writer of `out/`; a hand edit there
  is a red line, not a formatting choice.** No header in this directory was
  hand-written.

## The pattern across the defect list, worth reading once

Five of the eight instruments had a defect that produced CONFIDENT WRONG
OUTPUT rather than an error, and every one was found by running the probe and
looking at the whole table rather than at the number the design wanted. Four
of the five are the same shape in different clothes: **a measurement whose
population or filter does not contain the thing being measured** — a filter
that never reached a transition table, a subject with no positives, a subject
where the "nomatch" case matched, an erasure that was not the erasure. That is
this project's own recurring finding (`../../.claude`-adjacent house rule: a
control sharing a source with what it controls) one level out, and it is why
every table here prints its denominator.

## `out/`

Archived probe OUTPUT, written ONLY by `probes/archive.sh`, which stamps one
provenance header on every file (probe path and args, the commit the probe was
last changed at, the commit and branch the run was made from, whether the
working tree was clean at run time, the date, and the python3, libpcre2 and
gcc versions). Evidence for the R32 panel, never an oracle — no check reads
these files. See `out/CLAUDE.md`.

Maintenance: update this file when probes or outputs are added/removed or
their roles change.
