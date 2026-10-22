# tests/lookaround — module `lookaround` ([M6.6.2])

`(?=X)` `(?!X)` `(?<=X)` `(?<!X)` and the two non-atomic spellings `(?*X)`
`(?<*X)`. Design: `docs/design/lookaround_design.md`, panel-approved at R33.

**ALL SIX CONSTRUCTS ARE BUILT AS OF WAVE D.** Wave B+C landed the lookahead
half and DECLINED the three `(?<` tails at `WANT_RESULT`, which is what kept
their registry rows `unbuilt`; wave D landed the back-step seam entry, deleted
the decline, and added the five lookbehind files (`lookbehind.rxt`,
`lookbehind_widths.rxt`, `startpos.rxt`, `nonatomic_behind.rxt`,
`workbudget.rxt`). Wave E adds `prefilter.rxt`, wave F `alpha_spellings.rxt`.
`gated.rxt` carried the split's own three enabled-but-unbuilt cells and wave D
RETIRED them — they would now be pinning a lie, and `lookbehind.rxt` asserting
the same three spellings compile and match is the control that says the count
going down is the module landing.

## Files

- **gen_corpus.py** — the generator, and it exists FOR THE `# pcre2-only` MARKING rather than for convenience.
- **lookahead.rxt** — `(?=` and `(?!`: bodies, contexts, degenerate forms.
- **captures.rxt** — the four polarity/outcome combinations with `g` lines: retention inside a positive assertion, the undo when a positive one fails, the discard inside a ...
- **quantified.rxt** — `(?=a)*` and family, including §2.6's five empty-iteration cells.
- **nonatomic_ahead.rxt** — `(?*` only, and `# pcre2-only` IN ITS ENTIRETY (python has no `(?*` at all, G5) — computed, not declared, ten blocks of ten.
- **lookbehind.rxt** — `(?<=` and `(?<!` with FIXED bodies and SAME-length alternatives, which is what keeps the file python-verifiable: python's rule is narrower than ...
- **lookbehind_widths.rxt** — DIFFERENT-length branches, `# pcre2-only` in its entirety (G1).
- **startpos.rxt** — `ms`/`ns` cells over a lookbehind, and **the axis a startpos-blind corpus would miss entirely**.
- **nonatomic_behind.rxt** — `(?<*`, `# pcre2-only` (G5), carrying §3.6's measured witness `(?<*(a)|(ba))c\2` on "bacba" BY NAME **and its atomic control** ...
- **workbudget.rxt** — §3.7's long-subject LEADING multi-branch lookbehind (R33 C1-6), so the `n·Σk_i` charge shape is MEASURED rather than reasoned about.
- **refused.rxt** — the `perr` cells: §2.5's VARIABLE-WIDTH family (and their libpcre2 verdicts are NOT one verdict — pcrec AGREES with PCRE2's err 125 on the unbounded ...
- **gated.rxt** — the module gate and D65's `built` column, cell by cell: the closed gate, the wrong module, the three lookbehind rows' enabled-but-unbuilt refusal (the ...
- **alpha_spellings.rxt** — ALL TWELVE `(*` alpha spellings ([M6.6.2] wave F; design §2.1, §10.2), 26 blocks / 52 cells / 2 `perr`, and `# pcre2-only` in its ENTIRETY — ...
- **prefilter.rxt** — §10.1(1)'s qualifying shapes, and the ONE file in this directory whose cells were chosen by MEASURING A COMPILER rather than by reading the design.
- **run_lookaround_diff.sh** — the behavioural instrument, `make test-lookaround`, four sections.
- `d27/` — the [M6.6.3] BLINDED corpus (D27): 7 .rxt files (457 blocks, 1,819 harness cases after acceptance triage) written from the design extract and the oracles only, ...
- `run_expansion_diff.sh`, `expand_corpus.py` — section "`run_expansion_diff.sh` + `expand_corpus.py` — THE SUBSTITUTION DRIVER (wave E2)" (history file)

## What this directory does NOT hold

- **The proof that the ceiling is DROPPED in the artifact.** `prefilter.rxt`
  asserts the ANSWERS; that the stamp, the `--emit-ir` description and the two
  lines that BUILD the ceiling all agree is `[M6.6-LOOKAROUND rule 1]` in
  `tests/codegen/run_codegen_tests.sh`, which is the same function
  `[M6.4-ATOMIC rule 1]` calls. R31 E3's finding is why both exist: a check on
  the stamp alone is GREEN on a half-done edit that leaves the ceiling live.
- **The byte-identity gate** is `tests/codegen/run_lookaround_identity.sh`,
  opt-in as `make test-lookaround-identity`, on the ruling
  `test-atomic-identity` and `test-backrefs-identity` have.
- **The `\K`-refusal's module attribution** and the six rows' closed-gate
  diagnostics live in `tests/reject/`: a `perr` block asserts only THAT a
  pattern is rejected, never WHY, and for a module boundary the why is the
  point.
- **`(?=(?i))*`**, which libpcre2 accepts and pcrec refuses. It is not a cell
  here because it is not this module's question: pcrec refuses `((?i))*` and
  `(?>(?i))*` the same way, and `src/parse/parse.c`'s A_CAP arm records the
  pre-existing question. Giving the lookaround its own cell would be giving
  one question two homes.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__lookaround.md`.
