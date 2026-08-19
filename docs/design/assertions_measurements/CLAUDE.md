# docs/design/assertions_measurements — the [M6.1] design lane's instruments

The measurements behind `../assertions_design.md` (module `assertions`: `\b`
`\B`, `\A` `\z` `\Z`, `(?m)` multiline `^`/`$`, `\G`, `\K`).

**[M6.1] BUILT IT AND [M6.2] KEPT ADDING TO IT**, which is why some instruments
here read a compiler that could not compile the construct they measure and
others read one that can: waves B, C, D and E each added or extended a probe as
the construct became real. A reader should check each entry's own tier
(EXACT/PROTOTYPE/MEASURED) rather than assuming the directory has one.

Kept separate from `../eng_brep_measurements/`, `../possessify_impl/` and their
siblings for the reason those are separate from each other: never confuse one
lane's numbers with another's. This lane's distinguishing property is that
**some of its instruments read pcrec itself and some do not**, and the
design doc marks every claim accordingly.

## The instruments, and what kind of evidence each produces

- **`probes/probe_ncls_refine.py` — EXACT, in-pcrec.** Reads the emitted
  artifact's own `<prefix>_fcls[256]` equivalence-class map and
  `<prefix>_facc[]` length and computes what refining the alphabet by the word
  set (`\b`/`\B`'s prerequisite) and by the newline set (`(?m)`'s) costs.
  Post-minimisation, because it reads what pcrec actually emitted. Two
  denominators, on `eng_brep_design.md` §2.6's rule that either alone misleads:
  the realistic set and the `.rxt` corpus.
- **`probes/probe_wordctx_states.py` — PROTOTYPE, and it says so three times.**
  pcrec cannot compile `\b`, so the state count of a context-carrying DFA
  cannot be read off an artifact. Builds the automaton the design proposes and
  minimises it (Moore), reporting the **RATIO** — both arms from one
  constructor, so any divergence from `src/ir/dfa.c` cancels — plus a
  `--calibrate` column against pcrec's own state count on the assertion-free
  arm. Its **one known fidelity gap is stated in the file**: it does not
  priority-prune where `src/core/compile.c:216` does, which is why five corpus
  patterns are reported over-cap rather than silently half-measured.
- **`probes/probe_acc_by_class.sh` — MEASURED, artifact benchmark.** What a
  next-byte-sensitive accept flag costs the forward hot loop. The variant it
  builds is **answer-preserving** (every row of the wide table is that state's
  old bit), so both artifacts report identical matches and the only difference
  is the lookup — which is what makes the timing attributable.
- **`probes/probe_z_oracle.py` — MEASURED, both oracles.** That python3 `re`'s
  `\Z` is PCRE2's `\z`, so the base-tier oracle produces WRONG `.rxt`
  expectations for `\Z`, in the silent direction. Borrows
  `../eng_brep_measurements/probes/pcre2_ctypes.py` rather than carrying a
  second copy.
- **`probes/probe_d475_scope.py` — MEASURED, both oracles.** The D47.5
  scope-blindness finding as CELLS rather than as an argument: for each of five
  `(?m)` placements it reports what the pattern MEANS and what a wrongly-
  exempting gate would compile it to, so "the shipped gate miscompiles this"
  is a table with subjects and spans. It does NOT test pcrec — pcrec refuses
  `(?m)` today, which is exactly what makes the defect latent. Two of its five
  cells are libpcre2-only and the probe says which and why, rather than
  skipping them silently.
- **`probes/probe_startpos_context.py` — MEASURED, libpcre2.** R30 E1: that
  `\b`/`\B`/`(?m)^` at `startpos > 0` depend on `s[startpos-1]`, a byte outside
  the search window, so searching `s` from `startpos` is NOT searching
  `s[startpos:]` from 0. Carries the cells through the S3.1 find-all loop too,
  and includes a CONTROL row whose resumes all land at word boundaries — a
  find-all suite made only of those reports "same" everywhere and proves
  nothing, which is what this probe's own first draft did.
- **`probes/probe_mline_caret_cost.sh` — MEASURED, artifact benchmark.** R30 E2:
  what routing `(?m)^` to ENG_ATTEMPT costs (O(n^2), 3.99x per doubling). Its
  header records the probe's own first finding: an all-'a' subject measures
  NOTHING, because every interior attempt dies on its first byte — a draft using
  that subject would have reported the design's struck sentence as correct.
  **[M6.2 wave C] GAINED A REAL-CONSTRUCT ARM**, additively: the [M6.1] arms
  measure `(?m)^` through STAND-INS (`^ERROR|\nERROR`) because the compiler
  refused the `m` letter, and wave C built it, so arms F and G run the patterns
  themselves under D63's candidate-start prefilter. The stand-ins are KEPT and
  are the honest "before" number — they get no prefilter and could not
  (`\nERROR`'s branch says nothing about the byte BEFORE the start, so every
  predecessor seeds a live state). Landing figures: non-crossing 3x/7x/7x
  against the stand-in and 82x/33x/27x still to go against a plain unanchored
  memchr; crossing unrescued at 3.98-4.01x per doubling and 1.00-1.01x of its
  stand-in, which incidentally confirms the stand-in was faithful.
- **`probes/probe_wswitch_alarm.sh` — MEASURED, self-restoring.** R30 M8: whether
  a new `AKind` enumerator raises a build alarm (15 warnings, 6 files). Appends
  the enumerator, runs `gcc -fsyntax-only`, counts, and restores the header under
  an EXIT trap that VERIFIES the restore. It refuses to report zero when it
  compiled nothing — a defect its own first run had.
- **`probes/harvest_rxt_patterns.sh` — the corpus population.** R30 M6: `LC_ALL=C`
  is load-bearing, not tidiness. Prints the C count, the UTF-8 count and the
  difference every run (1030 / 609 / **421 silently merged**), so the defect is
  visible rather than latent. Exists because the fix must travel as TOOLING: this
  lane reproduced R24 M-F1 verbatim after reading the entry that named it.
- **`probes/probe_wordctx_budget.py` — MEASURED, in-pcrec, BOTH ARMS.**
  [M6.2 wave B] closing §3.5.1's landing condition: the composed state budget,
  taken on the BUILT compiler rather than composed from a prototype's ratio
  and a corpus's worst count. Reads states and ncls off each artifact's own
  emitted tables for PAT and `\bPAT\b` — the same arm-vs-arm shape
  `probe_wordctx_states.py` used, with pcrec on BOTH arms instead of a model
  on both — and then LOCATES the refusal boundary by bisection against both
  caps, ENG_UNANCH's 32,000 and ENG_ATTEMPT's 3.2x tighter 10,000 (§3.4.1
  discloses that the design's whole corpus measurement was blind to the
  second). It reads the ATTEMPT engine's state count too, from its computed-
  goto table count, because that engine emits no accept array at all.
  **It refuted §3.5.1's forecast as an OBSERVATION** (the bound stands): the
  measured ratio's MIN is BELOW 1 — the word context can SHRINK a machine —
  and on §3.5.1's own worst family a leading `\b` RAISES the ceiling by
  pruning start positions and moving the binding constraint from
  `PCREC_MAX_SUBSET_ELEMS` to the state cap. The genuine regression had to be
  looked for and is one repeat count wide on a linear chain, which is why that
  family is in the probe rather than only in the prose.
- **`probes/probe_kreset_identity.sh` — MEASURED, and the ONLY instrument in
  this directory whose reference is a COMMIT rather than a build of this tree.**
  [M6.2 wave E]'s byte-identity claim: a `\K`-free pattern's emitted C is
  unchanged by the wave. The four shipped `tests/codegen/run_*_identity.sh`
  gates build their reference from THIS TREE'S sources with a `-D` knob; wave D
  MEASURED what that costs (under a sabotage BOTH builds are sabotaged, so an
  edit outside the knob's gated region CANCELS — S83's first form left the
  sweep at 1175/1175 identical, and wave B's S71 leaves `run_wordctx_identity`
  at 1135/1135 to this day). This probe builds the reference from a PINNED
  PRE-WAVE COMMIT via `git archive`, so it shares no sources with the subject
  and no edit to the subject can reach it. Strictly stronger, and available
  here only because wave E's claim is ONE-SHOT — there is no ongoing gate to
  keep cheap, which is itself the wave's justified deviation from the
  four-gate precedent (the permanent check is `[M6.2-KRESET rule 1b]`, which
  pins the pre-wave `caps_out` body as a literal).
  Two engine modes, and the second is the one that matters: under the default
  engine most corpus patterns route to the DFA and emit no `caps_out` at all,
  while `--engine=vm` puts every artifact through the function the wave edits.
  **Its REFUSAL-MISMATCH column is the positive control** — the reference
  cannot compile a `\K` pattern at all, so a run reporting zero differing AND
  zero refusal mismatches has either lost its `\K` population or is comparing
  two builds of the same tree.
  Its own first run recorded a defect worth keeping: `set -e` plus
  `a=$(...); ra=$?` ABORTS on the first refused pattern, because an assignment
  from a failing command substitution is itself a failing command — and 395 of
  1369 corpus patterns are refused, so the naive form measured nothing while
  looking like a probe that had finished.
- **`probes/archive.sh` — not a probe, the ARCHIVER.** Every file in `out/` is
  written by it, so one provenance header covers them all and a number can be
  traced to a run rather than to a claim. **R30 M7: the archiver is the ONLY
  writer of `out/`.** One header here was once hand-written into this script's
  format, which is worse than no header — a reader cannot tell a stamped file
  from an asserted one without git archaeology. A hand edit in `out/` is a red
  line, not a formatting choice.

The D47.5 multiline-gate question is answered by **re-running
`../eng_brep_measurements/probes/probe_dollar_multiline_pcre2.py`**, not by a
second instrument — a lane that rebuilds the probe it is checking cannot detect
that the original moved. Its output is archived here as
`out/dollar_multiline_rerun.txt`, and `assertions_design.md` §8.8 records that
today's figures differ from the ones `eng_brep_design.md` §2.5 cites while the
qualitative result holds.

## `out/`

Archived probe OUTPUT, written ONLY by `probes/archive.sh`, which stamps one
provenance header on every file (probe path and args, the probe's own last-change
commit, the run's commit/branch, whether the tree was clean, date, and the
python3/libpcre2/gcc versions). Evidence for the panel, never an oracle — no
check reads these files. See `out/CLAUDE.md`.

Maintenance: update this file when probes or outputs are added/removed or their
roles change.
