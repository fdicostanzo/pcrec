# docs/design/assertions_measurements — the [M6.1] design lane's instruments

The measurements behind `../assertions_design.md` (module `assertions`: `\b`
`\B`, `\A` `\z` `\Z`, `(?m)` multiline `^`/`$`, `\G`, `\K`).

Kept separate from `../eng_brep_measurements/`, `../possessify_impl/` and their
siblings for the reason those are separate from each other: never confuse one
lane's numbers with another's. This lane's distinguishing property is that
**two of its four instruments read pcrec itself and two do not**, and the
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

The D47.5 multiline-gate question is answered by **re-running
`../eng_brep_measurements/probes/probe_dollar_multiline_pcre2.py`**, not by a
second instrument — a lane that rebuilds the probe it is checking cannot detect
that the original moved. Its output is archived here as
`out/dollar_multiline_rerun.txt`, and `assertions_design.md` §8.4 records that
today's figures differ from the ones `eng_brep_design.md` §2.5 cites while the
qualitative result holds.

## `out/`

Archived probe OUTPUT, each with a source header (repo commit, tool versions,
date) on the `docs/measurements/` precedent (D35). Evidence for the panel,
never an oracle — no check reads these files.

Maintenance: update this file when probes or outputs are added/removed or their
roles change.
