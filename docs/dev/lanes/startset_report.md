# startset — START-SET design lane report (2026-10-05, opus)

**Deliverable:** `docs/design/startset.md` plus its instruments in
`docs/design/startset/` (own CLAUDE.md). DESIGN ONLY: nothing under
`src/`, `cli/`, `lib/` or `tests/` changed. Branch `lane/startset`, off main
`a4c752a2` (abi 61).

## What was done
1. **The D77 census at abi 61** (`census.py`, `summarize.py`). Compile-side,
   darwin, every bench export (345; 321 compile) plus 3,521 distinct corpus
   pattern texts (3,147 compile), at `auto` and at `--engine=vm`.
2. **The AST start-set probe** (`fs_probe.c`, linked against
   `build/libpcrec.a`, on the lowered tree).
3. **Hand twins, answer-only, every subject × every startpos, full capture
   vector:**
   - the hybrid narrowed with and without the re-seed;
   - the DFA hat (`T = S ∩ E`);
   - the VM hat's entry/retry seek, including utf8;
   - failing-direction controls for each.
4. **Mac scratch find-all timings** of the VM hat (directional only).
5. **The design note**: rows, soundness, the [MEMFN] site, axis/stamps,
   sabotage S478-S485, the alpha plan and landing bar, stages 0-5, Q1-Q9,
   the three standing questions, and the lenses.

## Census numbers (inline for the handback)
- **VM hat at `auto`** (prefilter-less VM, unanchored):
  - bench 18: 17 with a narrowing start set (FS), **0 with a bounded run**;
  - corpus 166: 59 FS, **10 with a bounded run**.
- **VM hat at `--engine=vm`** (unanchored):
  - bench 294: 273 FS, 89 run;
  - corpus 2,660: 2,263 FS, 363 run;
  - **RUN without FS: 0** on every population.
- **DFA hat** (seeded machine, `T ⊊ E`): bench 18 (9 dfa + 9 hybrid), corpus
  58 (46 + 12). Its bench movers include `level-context` and the four `ctx-*`
  hybrids (the CTX group) and `wild-logparse-quotedstring-grok` (a stated
  do-not-regress cell that moves).
- **Gap report START-SET cells**: 6 reached by the DFA hat and 4 by the VM
  hat. The other 6 already scan with `offset-set` (5 of them gained the
  handoff at abi 61), and neither hat moves them.
- **The give-up surface**: 11 of the corpus's 35 `gu`/budget blocks are
  VM-hat movers.

## Validation (answer-only, complete)
- **Hybrid** `\b(ab|cd)\b`: 17,736,745 cells. Narrowed without the re-seed:
  768 lost. Narrowed with it: 0.
- **DFA**: `\b(?:ab|cd)\b` 768 / 0; `\b[0-9]{2,3}\b` 1,024 / 0;
  json-constant 0 / 0 (reach-limited at length 8).
- **VM hat**: 14 patterns × every startpos (20k-14.9M cells each,
  utf8 included): 0 diffs. Controls (one member dropped): 150,977 / 2,824 / 1.
- **Control C-SS** (`E ⊆ S` on unseeded machines): 685 artifacts, 0
  violations. The drop-one twin fires on all 685.
- **Mac scratch** (directional; base → VM-hat twin, ns/B on capability
  `t-1m`):
  - quoted-delim 3.304 → 0.555 (×6.0);
  - balanced-parens-rec 2.376 → 0.696 (×3.4);
  - aws `--engine=vm` 4.441 → 0.365 (×12.2).

Nothing is owed by this lane. Linux timing is the build's alpha (§7 of the
note).

## Findings a resuming agent needs
- **The re-seed is SOUND on the hybrid.** The brief's "re-seed unsound for
  hybrid" misreads `firstset_design.md` §4.6.5: what it measured is narrowing
  WITHOUT the re-seed.
- **The census's first run was wrong** on all non-ASCII patterns: a
  latin-1-decoded str argv was re-encoded as UTF-8 by Python. The independent
  control caught it (33 violations → 0 after the fix). Recorded in
  `startset/CLAUDE.md`.
- **A reverted prior first-set analysis exists** at `a07a87c6`
  (`src/opt/firstset.c`). Both of its REVISIT-WHEN triggers have fired.
- **K84 must be fixed before any new `dfa_pfs[]` row** (stage 0).
- **The VM hat must keep `pcrec_artifact_has_dfa_scan` false** (K65/K66,
  S484).
- **DFA-hat movers can move three other selections**: the scan edge (via
  `reseeds`), G1 (`REQ_WHY`), and the hybrid's re-seed row (via the
  candidate ppm).

## Questions for Frank
These are Q1-Q9 in the note's §9, each with a recommendation. Headlines:
- **D148** for the shape, and a full D6 panel before build.
- **Build order**: VM hat first, then the DFA hat.
- **Axis**: deny-only `-fno-start-set`, no force flag.
- **The give-up allowance** spec sentence.
- **No early batch gate.**
- **Re-bucket the six offset-set cells** in the next gap report.
- **Stage 4's trigger.**
- **No `possessify` unification.**
- **The rename after stage 3.**
