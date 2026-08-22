# docs/design/atomic_groups_measurements — the [M6.4.1] design lane's instruments

The measurements behind `../atomic_groups_design.md` (module `atomic-groups`:
`(?>...)` and the possessive-quantifier spellings `*+` `++` `?+` `{n,m}+`).

**EVERY INSTRUMENT HERE READS A COMPILER THAT CANNOT COMPILE THE CONSTRUCT IT
MEASURES**, and that is this directory's distinguishing property — the opposite
of `../assertions_measurements/`, where some probes read the built construct and
some do not. pcrec refuses every atomic and possessive pattern today, so every
in-pcrec arm below works through a PROXY:

- the **atomicity-ERASED twin** (`(?>` → `(?:`, a two-byte edit), which is
  exactly the machine `src/ir/nfa.c` will build for the prefilter, so the proxy
  is the thing under test rather than a stand-in for it; and
- the **possessify verdict stamp** (`RX_VM_STRATS` bit `0x1`), which is the
  SHIPPED §2.2 analysis answering about a pattern it can compile.

A reader should check each entry's own tier (MEASURED / PROTOTYPE / STRUCTURAL)
rather than assuming the directory has one.

Kept separate from `../assertions_measurements/`, `../eng_brep_measurements/`
and their siblings for the reason those are separate from each other: never
confuse one lane's numbers with another's.

## The instruments, and what kind of evidence each produces

- **`probes/probe_atomic_semantics.py` — MEASURED, BOTH ORACLES.** The design's
  whole interaction table (§6) as 95 cells across 17 sections, libpcre2 10.46
  against python3 3.14, with a per-cell AGREE column and a `BOTH-ERR` verdict
  for cells where both refuse (D26 tier 2 satisfied, tier 3 wording ours).
  Headline: **13 diverging cells**, of which 8 are constructs python cannot
  express or parse at all and **2 are U9's real answer divergence**. Its own
  first run reported three FALSE divergences because `pcre2_match` returns "one
  more than the highest pair that has been SET", so a pattern whose LAST group
  is unset comes back with a SHORTER tuple than python's — the padding
  normalisation and the reason for it are in the file.
- **`probes/probe_uncut_superset.py` — MEASURED, libpcre2, SWEEP.** The hybrid
  hazard (§4) over a generated family rather than three hand-picked cells: 1,260
  patterns × 14 subjects, each with its two-byte-edit uncut twin. Headline:
  sound REJECTION and the START lower bound hold at **0 violations**; the END is
  **REFUTED at 122**, which is what makes the prefilter's span end unusable as
  the emitted MRL ceiling. Builds the twin by TEXT SUBSTITUTION on purpose — a
  hand-written twin can differ in something other than the atomicity, which
  makes every divergence unattributable. It deliberately EXCLUDES the possessive
  suffix spellings, because the suffix can also change what the PRECEDING item
  may do (U9) and mixing the two would make somebody else's quirk look like a
  prefilter finding.
- **`probes/probe_ceiling_shape.sh` — STRUCTURAL, in-pcrec.** The other half of
  §4: that today's emitter really does feed `window[0][1]` to the VM as a
  pruning ceiling, shown in emitted C from a pattern the compiler can build
  TODAY. **Its two negative arms are the point**: under `-fno-prefilter` and
  under `--engine=vm` the same pattern emits `window_end = subject_length` and
  stamps `RX_VM_PRUNE_CEILING "subject-end"`. A probe printing only the positive
  arm could not tell a reader whether it had found a SHAPE or a CONSTANT.
- **`probes/cut_proto.c` + `probes/probe_cut_trail.py` — PROTOTYPE, checked
  against libpcre2.** Five atomic patterns hand-lowered onto the emitted VM's
  own machinery, with `RX_TRAIL`/`RX_SET`/`RX_PUSH`/`RX_CUT` and the fail label
  copied VERBATIM from a real artifact, so a divergence is a divergence in the
  LOWERING and not in the substrate. Headline: **14 rows, 0 disagreeing, 9
  NON-VACUOUS.** The non-vacuity counter is not decoration — a suite of rows
  where the cut changes nothing would pass with `RX_CUT` deleted, and the driver
  FAILS if every row is vacuous.
- **`probes/probe_free_discharge.py` — MEASURED, in-pcrec on one arm and
  libpcre2 on the other.** The free discharge (§5.3): 1,764 patterns × 16
  subjects, verdict read off the shipped possessify pass via the twin's
  `RX_VM_STRATS`, truth read off libpcre2 for both spellings. Headline: **532
  positive-verdict patterns, 0 violations**; 834 of 1,232 negative-verdict
  patterns are rescues the discharge declines. **Prints four CONTROLS every
  run** — two that must diverge with a negative verdict, one that must not with
  a positive one, and U9's witness — because a zero from an instrument that
  cannot fire is worth nothing, which is this project's most-repeated finding.
- **`probes/probe_possessify_under_cut.py` — MEASURED, both arms, and it tests a
  claim nobody in this tree has tested.** Whether possessify's §2.2 verdict,
  validated on a corpus that could not contain a cut, stays sound once cuts
  exist. 48,000 cells over FOUR positions of the quantifier relative to the cut
  (inside the body, wrapping the group, before it, after it), because the hole
  in the subset argument is position-dependent. Headline: **0 violations**, with
  a **non-vacuity counter of 202** so the zero is not an artefact of a family
  where possessification never matters.
- **`probes/probe_rk_alarm.sh` — MEASURED, self-restoring.** What a fifth
  `RegKind` costs (§7.3), on `../assertions_measurements/probes/
  probe_wswitch_alarm.sh`'s shape one enum over. Headline: **0 `-Wswitch`
  diagnostics over 28 files** — the OPPOSITE of `AKind`'s 15, and the fact that
  decides §7.4's ruling. Restores the header under an EXIT trap that VERIFIES
  the restore, and refuses to report zero when it compiled nothing. **Its own
  first run died silently on `set -e` plus an assignment from a failing `ls`** —
  the identical defect `../assertions_measurements/CLAUDE.md` records for
  `probe_kreset_identity.sh`, reproduced by a lane that had read that entry, and
  the note stays in the file for the next one.
- **`probes/archive.sh` — not a probe, the ARCHIVER.** Every file in `out/` is
  written by it. **R30 M7's rule, inherited: the archiver is the ONLY writer of
  `out/`.** A hand edit there is a red line, not a formatting choice.

The `-Wswitch` question for a new `AKind` is answered by **re-running
`../assertions_measurements/probes/probe_wswitch_alarm.sh`**, not by a second
instrument — a lane that rebuilds the probe it is checking cannot detect that
the original moved. Its output is archived here as `out/wswitch_alarm_rerun.txt`
and the design cites it as a re-run.

`probes/pcre2_ctypes.py` is NOT copied here: every probe that needs libpcre2
imports `../../eng_brep_measurements/probes/pcre2_ctypes.py` by path, on
`../assertions_measurements/`'s precedent (one binding, one place it can be
wrong).

## `out/`

Archived probe OUTPUT, written ONLY by `probes/archive.sh`, which stamps one
provenance header on every file (probe path and args, the probe's own
last-change commit, the run's commit/branch, whether the tree was clean, date,
and the python3/libpcre2/gcc versions). Evidence for the [M6.4.1] panel, never
an oracle — no check in `make test` reads these files. See `out/CLAUDE.md`.

Maintenance: update this file when probes or outputs are added/removed or their
roles change.
