# lane lacens2 — [CTX-PREFILTER] + [ENG-LOOK] step 0 censuses

Branch `lane/lacens2`, worktree `worktrees/lacens2`, branched from
`lane/ucpu2` at `61cbc894` per brief (U2's A_CTX mechanism is the baseline
both censuses measure against). Sonnet, MEASUREMENT lane — nothing under
`src/`; light probes only (small single-pattern `--engine=dfa`/`auto`
compiles via `timeout`-wrapped subprocess calls, ~115-140 per script,
each well under a second; no suite/corpus run, no boxlock needed).

## Delivered

- `docs/dev/ctx_prefilter_census.md` — [CTX-PREFILTER] step 0.
- `docs/dev/eng_look_census.md` — [ENG-LOOK] step 0.
- `docs/dev/lookaround_census/lac_engine.py` — shared engine (erasure,
  two independent atom/body parsers, a from-scratch NFA-then-subset-
  construction DFA builder, an exact BFS product walk, and a parser for
  pcrec's own generated C that recovers real DFA transition tables).
- `docs/dev/lookaround_census/eng_look_growth.py` + its committed run
  (`eng_look_growth_61cbc894.tsv`, `eng_look_skipped_61cbc894.tsv`).
- `docs/dev/lookaround_census/ctx_prefilter_probe.py` + its committed run
  (`ctx_prefilter_61cbc894.tsv`, `ctx_prefilter_skipped_61cbc894.tsv`).
- `docs/dev/lookaround_census/CLAUDE.md` and `docs/dev/CLAUDE.md` updated
  for the four new files/two new memos.

## Headline numbers (full detail + method in the two memos)

**[ENG-LOOK]**: 98 candidate k=2-4 fixed-width occurrences (56/40/2 by k,
matching `lookaround_census.md`'s own S3 distribution); 97 compile (1
bench pattern skipped — its erased form alone exceeds pcrec's emit-size
limit, unrelated to lookaround folding). LOOKBEHIND (54 occurrences,
composed against the FORWARD erased machine — the correctly-scoped
construction): real, small growth, 2-3 states baseline growing to 3-10.
LOOKAHEAD surfaced a genuine mechanism finding: this census's own literal
brief (product against the REVERSE machine) measures EXACTLY ZERO growth
in all 43 cases, because pcrec's reverse machine only walks the matched
span and structurally never traverses a lookahead's own body (past the
match end, zero-width). plan.md's own stated mechanism (forward-pass
"k-byte delayed acceptance") is built and measured too, but this script
composes it from the pattern's start rather than at the actual assertion
point, so its own number is a model (can read negative "growth", an
artifact of the simplification) — the one trustworthy fact from that half
is the delayed-accept sub-automaton's own size, 3-5 states. Verdict:
state-count is not the blocker (everything measured or modeled is small,
nowhere near the 32,000/10,000-state caps); the lookahead attachment-point
design question is unresolved and the population is 72/98 one
boundary-matrix test file — recommends the D6 design panel plan.md's row
already names, not a build from this alone.

**[CTX-PREFILTER]**: 354 patterns still VM-routed post-U2; 143 carry a
positive multi-char lookaround (146 occurrences, 96 from one boundary
matrix file, only 6 bench-derived). 31/146 (21%) have no sound necessary
byte at all (body can match zero-width, correctly excluded). Of 115 with
a computable set: 111 (96.5%) are NARROW (size<=8, or not already implied
by the adjacent consuming atom). A tightening estimate is stated
explicitly as an INDEPENDENCE MODEL (today's compiled `RX_REQ_BYTE`
selectivity times the necessary set's own selectivity, both measured on
`APPROACH.md`'s prose as the representative subject — named and justified
in the memo, chosen over a pcrec-bench checkout because this
population's own bench share is thin) — one to two further orders of
magnitude of rejection in the worked examples, explicitly NOT a joint-
position measurement. Verdict: the narrowness finding is real and cheap
to confirm; recommends NOT building from this alone — a real joint-
position measurement is the D77 trigger, not a timeline.

## One thing the manager should know: plan.md's two rows are not in this branch's history

`lane/lacens2` branches from `lane/ucpu2` at `61cbc894` (per brief). The
brief quotes both step-0 asks from plan.md commits `e79a53fd` (files
[CTX-PREFILTER]) and `eee1d36a` (amends [ENG-LOOK] with its own step-0
ask) — both LATER commits on `main`, not yet in `lane/ucpu2`'s ancestry.
So `docs/dev/plan.md` in this worktree still carries the OLD
(pre-`eee1d36a`) [ENG-LOOK] text and has no [CTX-PREFILTER] row at all —
confirmed by `grep`, not assumed. I did not rebase or merge `main` into
this branch (out of scope for a measurement lane, and risky un-asked) and
did not touch `plan.md` here. **The manager will want to add the
step-0-delivered pointer to both rows on `main`** (matching the style
`eee1d36a`'s own row amendment used) when merging — this report's own
headline numbers above are what that pointer should cite.

## Validation

Both scripts re-run clean and reproduce their committed TSVs BYTE-
IDENTICALLY (`diff` against the committed files after a final cleanup
pass, both `IDENTICAL`). `eng_look_growth.py build/pcrec OUTDIR`: ~2s.
`ctx_prefilter_probe.py build/pcrec . OUTDIR`: ~15-20s (dominated by
~115 small `--features all` compiles). No suite run needed or attempted
— this is a measurement lane over two from-scratch Python scripts and a
handful of single-pattern pcrec compiles, not a `src/` change.

## Scope discipline

Nothing under `src/`/`cli/`/`lib/` touched. `pcrec-bench` was read
conceptually (its capability/utf8 pattern population is already folded
into `shapes_9399d927.tsv` by the earlier `lacensus` lane, per that
memo's own S1 method — not re-checked out here) but never written.
`make -j2 CC=gcc-16` was NOT used for the build (the brief specified
`-j2` light, without pinning `CC`; a plain `make -j2` built cleanly with
this box's default `gcc-16` toolchain anyway — noted for the record since
the boilerplate's own worktree-setup section says `-j4 CC=gcc-16`).
