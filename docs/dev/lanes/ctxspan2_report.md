# ctxspan2 — lane report (ctx_span.md revision 2 + kit_proof r4 edits)

Lane `ctxspan2` (opus, design documents only), 2026-10-18, branch `lane/ctxspan2` from main
`3b0f87b55`. Nothing under `src/`, `tests/`, `lib/` or `docs/spec/` changed. The work was
compile-only probes with the worktree's `build/pcrec` (one `make -j16`), python over the
tree, and `make test-spec-history` (11/0). All of it ran before the 00:45 box cutoff.

## Delivered

- `docs/design/ctx_span.md` **revision 2**. It applies review r4: every finding ACCEPTED
  except C3, which Q-r4-1 REJECTED. It applies the rulings Q-r4-1..3. §R2 summarizes the
  changes, and §13 maps every r4 id (A1-A9, B1-B10, C1-C7, U-B1..U-B4, plus C6/A6 from the
  unlocks list and the three rulings) to its discharge.
- `docs/design/kit_proof.md` **r4 edits**, each marked `[r4 <id>]`:
  - **B9**: §5.2's pass-through is limited to position-only kinds. The in-span context rule
    joins UL-0 at Z2. The k-set pass-through's false `exact_len` "on the wire" is stated. X0's
    set equality runs on every site stating `exact_len > 0`, and its subject family gains the
    three witnesses. Sabotage S1149 is PROPOSED.
  - **B1**: one `ctx[]` entry per ITEM, with the per-item / per-offset contradiction removed.
    `MF_MAX_CTX` is 2, derived from stage 1's one source. Stage 1 sends EXACT items only.
    R-26.7 (the exactness fact) is FILED with UL-b/UL-g as its trigger.
  - **Q-r4-3**: UL-0's producer is the extended `pcrec_kset_walk`, with no
    `src/facts/spans.c`.
- `docs/design/kit_proof/witnesses.txt` + `conj.txt` D: the three in-span witnesses, run on
  `conj.py` (machine half). The results are `a(?=b)[a-z]` cover k=2, `\w(?=\d)\w` cover k=2,
  and `[a-z0-9_ ]\b[a-z ]` `exact`.
- `docs/design/ctx_span/` (new, own CLAUDE.md) holds the evidence:
  - `edit_set.tsv`;
  - `call_graph.txt`;
  - `sabotage_anchors.{tsv,summary}` (start_table's script);
  - `derive_rows.py` → `derived_rows.tsv`;
  - `readers.sh` → `readers.txt`;
  - `arm_pairs.py`.
- `docs/design/CLAUDE.md`: the ctx_span entry gains a revision-2 block, and the kit_proof
  entry gains an r4 line. `ctx_span/` is listed. The `kit_proof/CLAUDE.md` evidence entries
  are updated.

## Headlines

- **The `\A`/`\z` census** (§4.6): 15 sites delete. 12 of them are ENGINE sites (the
  `N_BOT`/`N_END` kinds, lowering arms, eps and closure arms, kset labels, VM arms) and 3 are
  AST sites. 109 label tokens go. 8 ANALYSIS sites read `\A`/`\z` as structure and would
  become data recognizers: `SA_BOT`, killed-`^`, `bol_out`, `EM_S`, `EW_Z`, `\z`'s possessify
  transparency, `EM_E`, and D164's `eol_tail_plain`. The leaning is an NFA-level fold as
  step P2d after P2c, keeping the AST kinds: 12 deletions, one generic predicate, zero
  recognizers. This is Q7 for Frank.
- **The derived sabotage population for P2c**: 5 retire (S76, S77, S762, S900, S343), 1
  re-aims (S341, onto A1's bug), and 25 re-run. The derivation reproduces every row the panel
  named, and adds 16 more (S78, S81, S82 and 13 owner rows).
- **The abi readers come from one recipe.** It finds the five readers revision 1 missed:
  match_api §1¶7, §6¶1 row 1, the abi_changelog sentence, kit_proof §6.1's B1 row, and
  memfn's wake.

## New findings

- **N-1**: the k-set walk's bound `PCREC_PREFIX_K_MAX` is 24, below kit_proof's 32. kvcensus
  `whole` counts 1 bench / 2 corpus native and 1 / 1 utf8 bodies with `k` > 24. These would
  decline C8 unless the limit is raised (a D90 re-measure).
- **N-2**: the derived sabotage population is larger than any hand list, for the third time
  by this method.
- **N-3**: `definitions.c`'s `eol_tail_plain` reads `A_END` as structure, so any AST-level `\z`
  fold moves D164's `tagged` form.
- **Not shown, and stated as OWED to the build**: the soundness direction of a forgotten
  `widths.c`/`eol_tail_plain` recognizer under a full fold.

## Not discharged

Nothing. Every r4 id has a discharge row in §13. Two items are designed as text and are
measured only at build. These are claims to check, not gaps:
- CK-4's zero VM, route and possessify movers at P2c;
- P2d's zero movers.

## Resume

A follow-up round starts from §12 (what to attack) and §5 Q7 (P2d). The scripts in
`ctx_span/` are re-run on the build base before the first edit (the README is their
CLAUDE.md).
