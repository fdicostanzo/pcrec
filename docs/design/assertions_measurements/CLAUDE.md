# docs/design/assertions_measurements — the [M6.1] design lane's instruments

The measurements behind `../assertions_design.md` (module `assertions`: `\b`
`\B`, `\A` `\z` `\Z`, `(?m)` multiline `^`/`$`, `\G`, `\K`).

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
