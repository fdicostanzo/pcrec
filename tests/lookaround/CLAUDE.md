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

## The files, and every expectation in them is GENERATED

- **gen_corpus.py** — the generator, and it exists FOR THE `# pcre2-only`
  MARKING rather than for convenience. Every cell is driven through libpcre2
  10.46 (the committed ctypes binding at
  `docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`) AND through
  python3 `re` in the same pass; the expectation is libpcre2's (D26), and a
  block is marked `# pcre2-only` exactly where python diverged or could not
  compile it, with the first divergence and the cell count written above the
  marking. **It never asks pcrec anything** — an expectation derived from the
  compiler under test is not an expectation.

  **WHY COMPUTED RATHER THAN DECLARED, and this module is the case that
  proves it.** Design §7 catalogues two expectations a hand-marking would
  have written in and that MEASUREMENT REFUTES: python compiles all fourteen
  quantified lookaround forms and agrees on all nine behavioural cells (G8),
  and the two oracles agree on all 27 capture cells INCLUDING captures in a
  negative lookahead (G9). Marking either family `# pcre2-only` by hand would
  have thrown a working oracle away — R32 C3's finding, which is exactly what
  the backrefs module's generator was built to remove.
- **lookahead.rxt** — `(?=` and `(?!`: bodies, contexts, degenerate forms.
  Carries §3.2.1's two witnesses BY NAME (`(?=(a+)b)a+b` on "aab" is (0,3)
  g1=(0,2); `(?!(a+)b)a+b` on "aab" is NOMATCH), §2.2's atomic discriminator
  `(?=(a|ab))\1$`, and the CAPTURE-FREE `(?=a)b` cell sabotage row S126
  needs — capture-free on purpose, because `(a)(?=b)c` keeps the VM whatever
  the row's `engines` mask says and would mask it.
- **captures.rxt** — the four polarity/outcome combinations with `g` lines:
  retention inside a positive assertion, the undo when a positive one fails,
  the discard inside a negative one, and the trailing-unset control
  `(?!(a)x)(a)` that proves the answer is READ rather than truncated.
- **quantified.rxt** — `(?=a)*` and family, including §2.6's five
  empty-iteration cells. They are here BECAUSE THEY MUST TERMINATE:
  `vm_nullable` answers true for `A_LOOK`, and if it did not the star would
  lose its empty-iteration guard. The failure is NOT a hang — every VM
  artifact carries a step budget, so the lost guard BURNS it and returns
  `PCREC_ERR_STEPS`, which a span-comparing harness scores as an error rather
  than as a mismatch.
- **nonatomic_ahead.rxt** — `(?*` only, and `# pcre2-only` IN ITS ENTIRETY
  (python has no `(?*` at all, G5) — computed, not declared, ten blocks of
  ten. Carries §2.2's non-atomic half and §3.2.1's row 3, which is the arm an
  implementer following "the atomic shape MINUS the cut" is most likely to
  lose the follow-scoping in.
- **lookbehind.rxt** — `(?<=` and `(?<!` with FIXED bodies and SAME-length
  alternatives, which is what keeps the file python-verifiable: python's rule
  is narrower than "same width" (it accepts `(?<=ab|cd)x` and rejects
  `(?<=a|bc)x`), so the divergence is about DIFFERING widths and not about
  alternation at all (G10). Carries design §3.4's B5 guard cells by name
  (`(?<=a)b` on "b" is NOMATCH where `(?<!a)b` is (0,1)), the two
  fixed-width-quantifier cells F3 measured (`a{3}` and `(?:ab){2}` — both are
  `A_REP`s that take a cursor rung whose MRL literal moves with the follow,
  which is why the lookbehind's body is scoped too), captures inside a
  lookbehind, both nesting orders, and the assertion family's own three bodies
  (`\w`, `\n`).
- **lookbehind_widths.rxt** — DIFFERENT-length branches, `# pcre2-only` in its
  entirety (G1). **It carries §2.4's preference-order measurement, which is the
  sharpest cell in the module**: `(?<=(a)|(aa))c` on "aac" answers g1=(1,2) and
  `(?<=(aa)|(a))c` answers g1=(0,2) — top-level branches in WRITTEN order,
  never by length, and an implementation that ordered them by width would get
  exactly one of the two right. It also carries the three ZERO-WIDTH-branch
  cells that FOUND A DEFECT: width 0 is a legal fixed width, and the emitted
  guard for it was `scan_position < 0` — an always-false `size_t` comparison
  the harness's `-Werror` generated build refuses.
- **startpos.rxt** — `ms`/`ns` cells over a lookbehind, and **the axis a
  startpos-blind corpus would miss entirely**. A lookbehind READS SUBJECT BYTES
  BEFORE `startpos` (§3.8, measured in both oracles: `(?<=a)b` on "ab" at
  startpos 1 MATCHES, `(?<!a)b` does not), which is a contract question rather
  than a syntax one. Sabotage row S135 clamps the guard to
  `scan_position - startpos < k`; without this file it could not go red. Every
  block pairs its `ms` cells with startpos-0 controls, because the file is
  about the WINDOW and not about the pattern.
- **nonatomic_behind.rxt** — `(?<*`, `# pcre2-only` (G5), carrying §3.6's
  measured witness `(?<*(a)|(ba))c\2` on "bacba" BY NAME **and its atomic
  control `(?<=(a)|(ba))c\2` in the same file**. That pair is the one thing
  that goes red if the per-branch retry frames are cut: (2,5) with g2=(0,2)
  against NOMATCH, on one subject, from one character's difference in the
  spelling. In the atomic form those frames are discarded by the cut; here they
  are LOAD-BEARING.
- **workbudget.rxt** — §3.7's long-subject LEADING multi-branch lookbehind
  (R33 C1-6), so the `n·Σk_i` charge shape is MEASURED rather than reasoned
  about. Every branch is width 2 so python verifies it. The subjects are 1000
  bytes: the budget itself is only reachable at ~50 MB, which a corpus cannot
  carry, so this file measures the SHAPE and the short cells beside it are the
  control that the answer does not depend on the length.
- **refused.rxt** — the `perr` cells: §2.5's VARIABLE-WIDTH family (and their
  libpcre2 verdicts are NOT one verdict — pcrec AGREES with PCRE2's err 125 on
  the unbounded bodies and refuses what PCRE2 COMPILES on the bounded ones,
  which the generator records per block), §2.7's `\K`-in-lookaround refusal
  (including the three nested spellings an immediate-children check would
  miss) and the unterminated forms. **Every block records BOTH oracles'
  verdicts**, because the agreement here is not agreement: libpcre2 refuses
  `(?=a\K)x` because `\K` is not allowed in a lookaround, python refuses it
  because it has no `\K` AT ALL (design §7, G6).
- **gated.rxt** — the module gate and D65's `built` column, cell by cell:
  the closed gate, the wrong module, the three lookbehind rows'
  enabled-but-unbuilt refusal (the split's own measurement), R33 C2-5's
  masking cell (`(?=a\K)x` WITHOUT `assertions` is refused by the assertions
  gate and never reaches §2.7's check at all), and the control that no row
  outside this module moved. **It opens with a block that must MATCH**: a
  file of nothing but `perr` passes just as well on a compiler that refuses
  everything, which is precisely the state a half-landed module gate puts the
  compiler in.
- **prefilter.rxt** — §10.1(1)'s qualifying shapes, and the ONE file in this
  directory whose cells were chosen by MEASURING A COMPILER rather than by
  reading the design. Design §5.6 drops the MRL window-end ceiling for any
  pattern containing a lookaround, and sabotage row S140 deletes that conjunct
  — so the row can only score DETECTED if the corpus holds a shape whose
  ceiling is really LIVE and whose match is really lost when it comes back.
  **§5.5's own first sweep reported 0 qualifying shapes over a space in which 0
  was the only possible answer**, every tail it used being nullable, so a
  hand-written population here would have been the same failure one directory
  over.

  **SO EVERY CLAMPING CELL WAS QUALIFIED AGAINST THE PRE-WAVE-E COMPILER**:
  compiled by pcrec at `8720029`, its `RX_VM_PRUNE_CEILING` read off the
  artifact as `"prefilter-window"`, its matcher run on these exact subjects and
  observed to answer NOMATCH where the oracle matches. Five clamping blocks
  qualify, including §5.5's measured witness `((?:a(?!q)|aq)(?:xy){0,4}q)` on
  `"aqq"` BY NAME and the NON-ATOMIC `(?*!` form of it, which is the cell that
  separates this module's predicate from [M6.4.2]'s — `pcrec_has_atomic` is
  false for `(?*!`, so an artifact suppressed by the atomic conjunct alone
  would leave that one cell red.

  **TWO CELLS ARE HERE BECAUSE THEY DO *NOT* QUALIFY.** §5.4's sharp H3
  violations `a(?!b)|ab` and `(?:a(?=c)|ab)c?` have the hazard SHAPE and stamp
  `"none"`: no bounded repeat, no clamp site, no ceiling to lose. The shape is
  NECESSARY AND NOT SUFFICIENT, which is the whole distinction §5.5 draws, and
  a corpus built from §5.4's table alone could not go red.

  **AND ONE DIRECTION OF §5.6 IS UNOBSERVABLE FROM ANY CORPUS.** Dropping the
  ceiling for EVERY pattern changes no answer anywhere — it only costs the
  pruning. The erasure control `((?:a|aq)(?:xy){0,4}q)` records the twin's
  answers, but the assertion that it KEEPS its ceiling is structural and lives
  in `tests/codegen/run_codegen_tests.sh` as `[M6.6-LOOKAROUND rule 1c]`.
- **run_lookaround_diff.sh** — the behavioural instrument, `make
  test-lookaround`, four sections. See its own header; two things about it are
  worth knowing before adding to it.

  **ITS SUBJECT SET GREW AT WAVE D, 19 -> 26**, and that is not a detail: the
  sweep is only as sharp as the subjects it runs over, and a differing-width
  lookbehind needs a subject on which ONE branch fits and the other does not
  (`ax`, `bcx`, `cx`), §2.4's preference-order cells need `aac`/`ac`/`c` to
  tell branch 1 from branch 2 by its captures, and §3.6's F4 fourth row is
  measured on `baca` specifically. Growing it re-derives every per-pattern cell
  count in the same change — including §2's, whose disagreement total the
  additions happened to leave at 13.

  **ITS POPULATION GUARDS ARE EXACT NUMBERS AND ONE HAS ALREADY GONE STALE**
  — during the wave that wrote it, when three `\K` cells were added to
  `lookahead.rxt` after §1's count was taken (python has no `\K` at all, so
  all three computed as `# pcre2-only` and the population went 11 to 14). The
  guard FIRED, loudly, which is what it is for; the lesson is the one
  `tests/reject/CLAUDE.md` records about hand-copied figures, and the remedy is
  the same: when a cell is added, re-derive the number from a run and change it
  DELIBERATELY. **Do not relax it to a floor.** A floor would let the
  population SHRINK, and the cells this section exists for are exactly the ones
  no other check in the tree can see.

  **§2 IS THE ONLY ARM IN THIS TREE WHOSE POPULATION MUST DISAGREE WITH
  ITSELF.** `(?=` and `(?*` differ in exactly one emitted line, so a compiler
  that cut BOTH or cut NEITHER answers them identically — and an arm that only
  checked agreement with libpcre2 per pattern would go green on both
  sabotages. It asserts the EXACT number of disagreeing cells (13 of 137 at
  this wave, every one the atomic form saying NOMATCH where the non-atomic
  form matches, never the reverse).

  **§1'S POPULATION GUARD WENT 14 -> 15 AT WAVE E**, and it FIRED to say so —
  the second time it has earned itself. `prefilter.rxt`'s `(?*!` cell is the
  added block. Re-derived from the run and changed deliberately, per the rule
  above.

  **IT REUSES `tests/backrefs/bref_oracle.py` AND `bref_batch.c` RATHER THAN
  COPYING THEM.** Design §10.2 asks for `la_oracle.py` "modelled on" those
  two; modelled-on would have been a THIRD copy of one mechanism
  (`tests/atomic_groups/` already holds the second), and D24 is the standing
  rule against a second home for one fact. Neither file is backref-specific in
  behaviour.

## Every block names `lookaround` in its `features` line

R33 V-10, and it applies to this directory AND to every sabotage row's
detector. `std1` is a FROZEN named set, `{classes, modifiers}`, so it does not
contain this module: a cell that forgot the feature would pass BY REFUSAL, on
a correct compiler and on a sabotaged one alike. That is S108's masking shape
applied to a whole file. Blocks needing `assertions` (the `\K` cells),
`backrefs` (the discriminator), `classes` (the `\w` lookbehind bodies) or
`atomic-groups` (`(?=a)*+`) name those too.

## Census at the wave D landing

Read it from a run — `python3 tests/lookaround/gen_corpus.py` prints the table
and `tests/harness/verify_rxt.py tests/lookaround` prints the python-side one —
rather than from here, for the reason `tests/reject/CLAUDE.md` records about
hand-copied figures. At wave B+C's landing it was **81 blocks / 118 cells / 18
`# pcre2-only` / 16 `perr`**, 166 harness cases, 1,022 pcre2-only cells
re-verified by §1. At wave D's it is **175 blocks / 335 answer cells / 48
`# pcre2-only` / 40 `perr`**, 451 harness cases, 302 python-verified cases, and
§1's pcre2-only population went **14 -> 44 answer-bearing blocks / 4,268
cells** — the biggest single move that guard will ever see, because
`lookbehind_widths.rxt` and `nonatomic_behind.rxt` are `# pcre2-only` in their
entirety.

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
