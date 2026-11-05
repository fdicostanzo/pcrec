# altdesign — design note: folds as alternations, one alternation normal form

Lane altdesign (opus), 2026-11-05, worktree `worktrees/altdesign` cut from main 0e811ff4c. Design only, no build go; no edits under src/ cli/ lib/ memfn/src/ tests/. One niced `make -j4` of the unchanged tree for probes. Rulings file `altdesign_rulings.md`: empty at every read (before each commit and before this report); no entry applied.

Deliverables (branch `lane/altdesign`):
- `docs/design/alt_normal_form.md` — the design note (PROPOSED rev 0), with a `docs/design/CLAUDE.md` line.
- `docs/dev/plan.md` — [RUN-POS-SET] restated; [DFA-ALPHA-MERGE] filed (STATE:not-started). `plan_lint` 0 violations.
- `docs/dev/lanes/altdesign_evidence/` — `pred.py` (stage predictor), `stage_pred.tsv` (its output), `stage2_byte_probes.txt`.

## Premise test

`altthink_evidence/f.sh` (re-pointed at this worktree's build) on `(?i)abcdÀefgh -e utf8`: `req_whole_run c38045464748/ffdfdfdfdfdf`, a 6-position run starting at À. CONFIRMED. Stop rule: the code does not contradict altthink on any point the design rests on. One sharpening, stated in note §4.2: the run's `all` flag already means "fixed width, each byte inside its position" (a cube `rr_pos` sets `all = true`; the common-head hull already holds bytes one branch never has). Only `req.c`'s comment still says "exactly one literal". So letting a superset hull into `all` is not a new soundness statement.

## What the note decides

- **One owner.** A new module (proposed `src/opt/altnf.c`) is the only producer of the normal form. Its parts: width groups; an exact sibling merge (two branches that differ at one position become one), run to a fixpoint; and a facts-only superset hull. It has two callers. UTF-8 lowering calls it over `u8_box`'s branches, inside the new subtree, which is legal under splice-in-place. altcls calls it at code-point level, before the call graph. A single post-lowering pass over user alternations is ruled out, because `pcrec_callgraph_build` caches group bodies. `req.c`'s `rr_alt` reads the same hull definition. kset, startset and the NFA/DFA are shape-blind and do not change.
- **Q2: superset allowed in facts, exactness only for rewriting.** I audited every `ReqRun`/`RbRun` reader by file:function (note §4.2 table). Each one reads membership (`(s & K) == T`, `pcrec_memfn_wpos_cube`), exact positions only (`mask == 0xFF`), information or mass, or the `maxoff` bound. None treats the run as the pattern's literal.
- **Q3: do not wait for D187.** Stage 1 is a property of the tree; it gains more automatically once positions become sets.
- **Q4: `info(S) = 8 − ⌈log2|S|⌉`, floor stays 16.** This equals popcount for every cube, so today's runs rank exactly as now.
  - Ranking risk: the run walk reads no prior, so it cannot see byte rates. A long superset run can outrank a shorter exact one.
  - Handling is a declared table R1-R3. R2 is a census of exact→set run flips. R3 narrows only if that census shows a loss: the walk then carries the best exact run beside the best run, and the rate-aware derived pick chooses between them.
- **Q5: length groups now, facts later.** The normal form carries length groups. Facts read one affix position on each side of a mixed-width letter (stage 3m). Per-group facts wait for [SEQ-FOLD]'s note.
- **Q6: the hand-off stays SETS.** The note states three-part evidence that would justify a string-set fact:
  1. a candidate-rate excess on a bench cell;
  2. an F10-class kernel that wins, scalar and SIMD each against its own bar;
  3. the win survives a random-like regime.

  Folds alone never make the case.
- **Q7: sequencing.**
  - Build after span_pick 1e (D153).
  - Stages 1, 2 and 2b do not wait for [POS-ONE-DETECTOR]; stage 3 rides with it.
  - Removing the seal is NOT an abi event. `abi` versions scaffolding (`match_api.md` §6¶17); the seal is program content. The build lane still runs D94's grep over the gate pins, and the critic round may reopen this point.
- **Staging (note §5), each stage with its D186 kind, gates, predicted movers, sabotage witness and deletions:**
  - **1** (byte UNIT, zero byte movers REQUIRED): lowering calls the owner and the seal is deleted. Gates:
    - B0: byte emit diff vs base is empty.
    - U1: utf8 movers ⊆ the predicted set.
    - U2: the fold census reads 766, predicted independently from CaseFolding.txt.
    - U3: no table grows.
    - U4: per-regime bench.
  - **2** (CHOICE): the `rr_alt` hull plus `A_EMPTY` as identity. It moves byte cells.
  - **2b** (CHOICE): altcls calls the owner.
  - **3** (CHOICE): set positions.
  - **3m** (CHOICE): mixed-width affixes.
- **Proposed D-next** (note §11): alternations have one normal form with one owner; a class is the one-symbol case; folds are alternations.

## New measurements (this lane)

All on this box's compiler.

| pattern | today | seal removed only (s0) | stage 1 (s1) | stage 3 (inferred) | stage 3m (inferred) | DFA next-state entries today → s1 |
|---|---|---|---|---|---|---|
| `(?i)abcdÀefgh` | 6 | 6 | 10 | 10 | 10 | 132 → 121 |
| `(?i)москва` | 0 | 0 | 0 | 0 | 4 | 1140 → 900 |
| `(?i)αβγ` | 0 | 3 | 3 | 6 | 6 | 160 → 128 |
| `(?i)straße` | 3 | 3 | 3 | 3 | 5 | 462 → 429 |
| `(?i)Ελληνικά` | 0 | 4 | 10 | 10 | 11 | 1430 → 1170 |
| `(?i)привет мир` | 0 | 4 | 7 | 7 | 8 | 1620 → 1296 |
| `(?i)naïve café` | 8 | 10 | 12 | 12 | 12 | 169 → 143 |

The s0 and s1 columns are MEASURED on byte-pattern spellings of the lowered tree, with altcls denied. The s0 control reproduces today's table counts exactly on every row except k/s. Byte stage-2 probes, all MEASURED today: `abcd()efgh` run 4 and `abcd(?:|)efgh` run 4, both because `A_EMPTY` and an empty-branch alternation cut the run; `abcd(?:ab|ab)efgh` run 6, because altcls's factoring leaves `(?:|)`.

Caveats:
- s1 does not model partial merges (β's `ce [92 b2]|cf 90`), so it understates stage 1.
- The byte spelling of `(?i)k`/`(?i)s` emits 60-72 table entries where utf8 emits 48 for the same lowering. The cause was not traced, so k/s table predictions are omitted.

## Open questions for Frank (plain words; note §12)

1. May the required-run fact use covering byte sets that are wider than any one alternative? For example, "one of 92, b2, 90" for `(?i)β`. It is safe, and a small version already exists today. Leaning: yes, for facts only.
2. Should stage 1 be the UTF-8 lowering alone (byte patterns provably unchanged), with user-written alternations as a later step judged on its own evidence? Leaning: yes.
3. Should set positions (the step that gives `(?i)αβγ` its full run) ride along with [POS-ONE-DETECTOR]? Leaning: yes.

## Notes for the manager

- The brief asked to "append a status line" on [RUN-POS-SET]. plan.md's row format allows ONE status line, rewritten in place. So I rewrote the status. The filed title, status and trigger are kept verbatim in a "Superseded framing" charter line, and the filing's other facts in a "Facts kept" line. The `filed:` line is unchanged.
- The note proposes S-ids by letter (S-a .. S-f) only. The build brief names the range.
- Not measured, and owed to stage 2's first deliverable: the population of byte user alternations whose run moves under the `rr_alt` rule. It needs a modified build.

STATE AT HANDOFF: note, plan rows and evidence committed on `lane/altdesign`. No source touched. No owed runs. Rulings file empty at every read (last entry applied: none). Critic round next (the manager's).
