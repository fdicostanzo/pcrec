# Lane decsurvey — report

**Brief (manager, 2026-10-06).** A read-only survey of decision families
that are still dispersed. The deliverable is
`docs/design/decision_families_survey.md` plus its `docs/design/CLAUDE.md`
entry. Frank's charter: "forest for the trees".

**Delivered** on `lane/decsurvey`, branched off main `74379fe0`:

- `docs/design/decision_families_survey.md`
- `docs/design/CLAUDE.md` (one new entry)
- this report

Nothing under `src/`, `cli/`, `lib/` or `tests/` changed. No make was run.

## Method

Four sonnet sub-surveys each wrote a scratch report: `emit_vm.c`; `compile.c`
with `select_engine.c` and `src/opt`; `src/facts` with `src/ir`; and the stamp
vocabularies against their write sites. A teammate note covered `emit_dfa.c`,
`clskit.c` and `runcmp.c`. I re-read every claimed inconsistency at its
lines.

The probes ran on the main tree's `build/pcrec` (mtime 2026-10-06 11:48).
They were compile-only stamp reads and `--emit-ir` listings: no matcher was
run and nothing was timed. The scratch files live under the untracked
`.scratch/` and are not committed.

## Headline

13 families are ranked. Six inconsistencies were found:

- **Probed (4):**
  - §4.2: `run-pinned` is unreachable whenever the run reader and the
    offset-k pick disagree. That includes plain rarity-vs-cost-model cases,
    not only ties: `\d\dxyz`, `[0-9][0-9]hello`.
  - §4.3: bits 18 and 21 (`-fno-size-term`, `-fno-scan-edge`) move
    `rx_info.flags` on `abc`, while their masked sibling `-fno-view-edge`
    does not. This is the K68 shape.
  - §4.4: on `a*` with `--engine=vm`, the `--emit-ir` `prune-ceiling` row
    reads `subject-end` while the stamp reads `none`.
  - §4.7: `--unroll=8 -fno-size-term` stamps `option`, an implicit
    precedence.
- **Read-confirmed (2), not reachable at the shipped raise-only caps:**
  - §4.1: `fit_collapse_applies` lacks the gate's collapsible-rep and
    nullable conjuncts that its own comment claims, which wastes an attempt.
  - §4.5: the `--emit-ir` prefilter reason chain names `-fno-prefilter` after
    a [PF-DROP] retry.
- **Also read (§4.6):** the `ENGINE_SEL` registry order differs from
  `esel_of`'s order. The arms are disjoint, so no artifact gets a wrong
  token.

## Recommended order (survey §6)

1. An [AXES-DENY-MASK] addendum: ask the owner whether bits 18 and 21 are
   unmasked on purpose.
2. A new [DEC-FALLBACK] row: one fallback ladder (fold [SEL-1] into
   `fit_rungs[]`, with stamp tokens as columns).
3. Re-scope [TIE-ALIGN] to cover non-tie disagreement too.
4. [DEC-ROUTE] together with the D148 `cand_rows[]` rename.

The rest are filed under triggers: [DEC-RUNG], [DEC-KINDATTR] and
[DEC-LIMITS], with [DEC-STAMPS] folded into [LIST-TABLES] STEP 0.

## Not done / caveats

- plan.md was not edited; the rows are paste-ready in survey §6.
- No probe could reach §4.1 or §4.5, because the caps are raise-only from
  the CLI. They need a lowered-cap reference build.
- The `emit_dfa.c` line numbers in §3.4 come from the teammate note; I
  spot-checked them at 10379-10412 and 6650-6820.
- `build/pcrec` may predate the latest merge. The stamps probed are not
  touched by ssbuild3 (abi 64).
