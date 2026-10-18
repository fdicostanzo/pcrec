# ctxspan — lane report (2026-10-18, opus, design only)

Brief: write `docs/design/ctx_span.md` for the re-scoped [DD-11.5] (D168 and D168 addendum 1).
Branch `lane/ctxspan`, from main `2ce4a1124`. Nothing under `src/` was changed. No
`make test`, no batteries, no sweeps. One `make -j16` ran in the worktree (before 20:00),
plus compile-only `--emit-ir` probes and a libpcre2 10.46 equivalence probe
(`build/probe/eqv.c` in the worktree, gitignored: anchored match at every start, all 547
(subject, start) cells over `{a, \n, x}` up to length 4).

## What the note says (resume from here)

- **Part 1, the producer.** `span_facts` is ONE walk. Each zero-width item contributes a
  per-offset set list through a first-match input table (§3.3). Outside span 0 that list is
  a context record `MkCtx {off, set, absent, form}` added to `MkLang`; inside the span it
  intersects `S_d` or ends `exact_len`. `\b`/`\B` go through the fold (§3.4): they need a
  known, non-straddling neighbour set, and the next side must EXIST. It maps onto R-26's
  `ctx[]` with the existing `byte_form` for exactness, so nothing new is asked of the kit.
  Stage 1's source stays kit_proof's machine reading (Q3, ruled). The producer lands at Z2
  as the C8-ctx control and becomes the source at UL-8's trigger.
- **Part 2, the fold.** `(?m)^` and `(?m)$` become `A_CTX` over `{\n}` with a 9-cell
  absent-aware truth function (each side out / in / absent). The six existing functions are
  re-encoded with absent copied from out, which moves zero answers. Two fn-derived
  predicates replace the `N_BOT_M` (BOT-family routing) and `has_end` kind tests. `^`/`\A`,
  `$`/`\Z`, `\z` and `\G` stay kinds (§4.3).

## Census headline (part 2, by grep at `2ce4a1124`)

- `multiline` field: 16 code reads, of which 14 are DELETED and 2 (the parser's `^`/`$`)
  become the generic node choice. Each deleted branch already returned what the `A_CTX` arm
  returns, checked one by one. The field and its 73-line control-3 comment go.
- `N_BOT_M`/`N_EOL_M`: 12 further code lines. 9 are DELETED, and 2 sites (`has_bot`,
  `has_end`) become fn-derived. The newline contributor row, `nl_bit` and the
  `PCREC_NO_MLINECTX` knob are deleted too.
- STAY: 84 code lines naming `A_BOL`/`A_EOL` (case labels and arms; the kinds survive).
  The survey's "38 `A_EOL` refs under `src/opt/`" are these labels, so they are NOT the
  deletion count.
- Abi 80 → 81. Six readers: `emit_dfa.c:54`, `run_codegen_tests.sh:3149`,
  `run_recursion_identity.sh:1262`, `S693:57-58`, `match_api.md` §6¶17 and the
  abi changelog. Byte identity holds except for DFA machines whose context-set list order
  changes (a `(?m)` node ahead of another `A_CTX` set in NFA order). Those are
  answer-identical movers.
- Checks that move: `run_mlinectx_identity.sh` retires. S76/S77/S762/S900 are re-aimed,
  S343 needs a reach check, and `ctx_admits_check.c` extends.

## Probe results (libpcre2 10.46, 547 cells each)

`(?m)$` ≡ `(?![^\n])` (0 differ). `(?m)^` vs `(?<![^\n])`: 40 differ, all after a final
newline. `(?m)^` ≡ `\A|(?<=\n)(?=[\s\S])` (0). `(?m)^x` ≡ `(?<![^\n])x` (0), while
`(?m)^a?` ≢ `(?<![^\n])a?` (40). `\A` ≡ `(?<![\s\S])`, `\z` ≡ `(?![\s\S])` (0). `\bx` ≡
`(?<!\w)x` and `\b\n` ≡ `(?<=\w)\n` (0). `$` vs `(?![^\n])`: 102 differ.

## Contradictions with D168 / add. 1

None. Two precisions:
1. "Width-1 negative lookbehind" means one BYTE on the lowered tree. `(?<!é)` under utf8
   declines.
2. Add. 1's deletion measure (38 `A_EOL` refs) overstates. The deletion is the field-reader
   hazard class.

## Findings filed (§11 of the note)

- F-1: kit_proof §5.2's pass-through overstates `exact_len` on a mid-span `A_CTX`, and C8
  would go red.
- F-2: `src/opt/ctxnode.c` is stale; the file is `src/parse/`.
- F-3: `pcrec_ctx_set_bytes` does not exist; the function is `pcrec_enc_set_bytes`.
- F-4: `src/gen/CLAUDE.md` cites `emit_dfa.c:51`; the define is at `:54`.
- F-5: add. 1's measure (see above).

## Open questions (the note's §5)

Q1 Z2 timing for the context half (leaning: with UL-0). Q2 part 2 first (leaning yes).
Q3 accept the DFA list-order movers (leaning yes). Q4 D62 addendum. Q5 multi-offset `A_CTX`
for `$`/`\Z` (leaning no, [ENG-LOOK]'s). Q6 unsent `pos-start`/`pos-end` rows (leaning keep).

## Unexplained, for the build

`x(?m)$` emits an extra `goto rx_L3; rx_L3:` hop that its `A_CTX` twin `x(?![^\n])` does
not. VM identity under part 2 must account for it (§4.5.3).
