# l1feat — span_arms L1, the FEATURE (lane l1feat, opus, 2026-11-19)

Branch `lane/l1feat`, cut from `lane/l1build` @ 07c840368. Design of record: `docs/design/span_arms.md`
rev 3.2, §14.4 L1 "Feature (sites 1-9, 21, 23)", "Contract", "abi", "Tests", "Deletes"; §14.3 D-1..D-4,
D-9, D-10, D-13. Scope: this worktree and `/var/tmp/pcrec-pcrec/scratch/l1feat/` only.

## Summary

A positive lookaround is now an ITEM of the necessary-run walk (`src/facts/req.c`). The fixed bytes
of its body narrow the consumed run positions they overlap. For a lookahead these are the body's head
column; for a lookbehind they are the body's description read reversed. A one-character `A_CTX` gives
its set at offset 0 or −1. Every one-byte position of the chosen run joins the necessary set (the TOP
set step). A meet that comes out empty proves no attempt can match, and the listing shows that as
`req_whole_run`'s why `dead`.

The walk changes, all in req.c unless named:

- T3's new E-5i row (mask `look|zero`) sits ahead of E-5.
- `RbRuns` gains `lg`, `rg` and `never`, and `rr_cat` runs CAT-R, CAT-L, the join, CAT-EDGE and never as
  fixed steps.
- `rr_alt` gains a guard post-step.
- TOP is a combining table walked by `RB_ROW_EACH`. It has no rows at L1.
- The `look` arm is added; `zero` gains `req_set` and `req_set_maxoff` (walk_arms.def).
- facts.h/facts_dump.c gain the `dead` why (PF_WHY_DEAD).

Validation:

- **Answers:** `spanarms.rxt` (466 cases) and `presence_deny.rxt` under `--memfn=no-fd-pres-pick` (655)
  are green.
- **Checks:** `run_facts_checks.sh` (16) and `reqcube_check.py` (105) are green. `make strict` is clean.
- **Two-sided compare:** all 54 census-model movers are observed, with equal facts and equal values.
- **Observed but not predicted:** 249 rows (plus 3 that move under utf8 only). Every sampled one falls into
  one of four mechanically tested classes; the full classification is queued (below).

The long gate runs are queued, not read: identity, mech, axes and make test. See STATE AT HANDOFF.

## Census at the base

`docs/dev/lanes/l1build_evidence/census_l1.py` was re-run unedited at the base 07c840368. The base
build is `git archive`d into `scratch/l1feat/trees/base`. Log: `scratch/l1feat/census_base.log`, summary
`census_base_summary.txt`.

- population: 7461 rows (7072 corpus, 389 bench), 5816 distinct texts; 675 with a positive lookaround
- abstained 97; read by the model 578
- PREDICTED MOVERS 54, all corpus: dead 51; req_set, req_byte and req_set_maxoff 3 each; req_whole_run 0
- 5 model movers the base compiler refuses; 1 narrowed with no fact moving
- §14.4's EXPECT rows: 0 disagreements
- `CENSUS-VERDICT: PROCEED (54 predicted movers: 54 (corpus 54, bench 0))` — the record.

## Feature commits

- `1e2a4f5db` is the feature: sites 1-9, 21 and 23.
  - **Guard primitives.** `rn_meet` is THE one meet, with EMPTY-MEET inside it: on a consumed position it
    keeps the value and sets never; on a guard it drops the empty position and everything outward of it.
  - **CAT steps.** `rn_guard_onto_head` (CAT-R) and `rn_guard_onto_tail` (CAT-L), and
    `rn_guard_meet_last`/`rn_guard_meet_first` (CAT-EDGE).
  - **The item.** `rb_look_item` and `rb_ctx_item`, plus `rb_zero_item_into` (E-5i's action).
  - **Head threading.** `RbVal.head` (D-10) is threaded only while inside a lookahead body
    (`RbWalk.ahead`), through `rb_head_node` and `pcrec_ph_node`.
  - **The lookbehind reader.** `pcrec_pd_tail_head` (desc.c) reads a description reversed.
  - **TOP.** `rb_top_rows` is a combining table with no rows, walked by `RB_ROW_EACH` (an all-rows sibling
    of `RB_ROW_SCAN`). `rb_top_set_step` applies the set step before the run floor.
  - **The never family.** A_CAT and A_ALT go through `pcrec_never_by_row`, and A_LOOK through
    `pcrec_ast_row(a).never`. The empty class (`rn_count == 0` in the gap branch) and REP's copies carry
    never; REP gets it through its copies, and the best-only restore copies it.
  - **Reading it.** `pcrec_req_walk(..., bool *never)` reports the bit. `pf_derive_req_walk` writes
    `PF_WHY_DEAD` with status `derived`, outside the decl list. `ReqWalkParams.onebyte_max` comes from the
    encoding descriptor.
  - **Arms on the set facts.** `req_set` and `req_set_maxoff` now carry the restored arms, because the set
    step writes them.
- `91e6724e7` adds the contract, the `[facts-look]` cells, the spanarms.rxt L1 rows, W-T1 in
  presence_deny.rxt, reqcube WIT `ws4`, and `compare_l1.py`.
- `15b9659bd` adds mech rows S3365-S3383, re-aims S1925, adds the rest of §5.7's witness rows and W-L4's
  listing cell.
- `7e28bfd3d` adds `explain_l1.py` and run_axes.sh's mention of `restore=look`.

Decisions recorded here (manager rulings r53):

- **F6, A_CALL/A_BREF NEVER: stays NO.** The run walk is the first reader for which the cell could matter,
  and it needs no NODE answer. It does not follow a call (A_CALL is a gap after its head), and it reads a
  backreference as a gap. NO is the safe direction and no answer moves. The trigger for NODE is a walker
  that follows calls.
- **F7, the head rule on TEXT: stays PLAN, not built.** The feature is the head rule's second caller (the
  trigger fired), but it adds no kind and reads `pcrec_ph_node` unchanged. A switch on TEXT would still
  need per-kind arms for the ZERO kinds that write (`A_KRESET`'s `writes`, `A_LOOK`'s body `writes`) and
  for the callout's row pick. So the general form would save one case group and delete nothing. The
  remaining trigger is the next new AKind ([COND-FAMILY]).
- **Register row 27 closes with this commit.** The run walk's item is `pcrec_ph_node`'s second caller. This
  is the manager's register update at landing.
- **F5 persists.** A_WCLASS sits under the walk's transparent descent, so `pcrec_ph_node`'s A_WCLASS arm is
  not reached from the run walk either; it is a byte-level class inside it.

## Tests and witnesses

- **spanarms.rxt** gains §5.7's L1 rows, each on both engines. Every expectation was taken from
  libpcre2-8 10.46 via `tests/lib/p2probe.c`. The rows:
  - the run and set witnesses: W-L1/L5 `xy(?=bc)[bc]c`, W-S1 `a(?=b)[bc]`, W-L2, W-N1, W-L5 (both
    lookbehinds), W-S4, W-F5, W-L6, W-L7, W-L8 (`ms 1`), W-A1, W-S1 stacking, W-N2, W-F4, W-RG, W-C1, W-E1;
  - the dead family: W-D1, W-D2, W-D8, W-D3..W-D6;
  - the empty-pick set step `\w*(?=a)\w`, and the non-movers `xyz(?<=yz)abc` and `x(?=ab|ac)a.`;
  - W-T1 (66 → 466 cases in total; 0 failed).
- **W-T1 under `--memfn=no-fd-pres-pick`.** The block is also in `tests/litscan/presence_deny.rxt`, which
  `tests/memfn/run_presence.sh [deny-answers]` runs under the flag (655 cases, 0 failed). Observed: at
  default flags, too, the artifact's `rx_reqrun__body` tests the whole 32-position run.
- **`run_facts_checks.sh [facts-look]`** has 19 cells:
  - the `look` arm restores the unit, with `harness:look` on `req_whole_run`, `req_set` and
    `req_set_maxoff`;
  - W-S1's byte move and W-L4 `bar(?=baz)`;
  - W-D1/W-D2/W-D8 listed `dead`, with `dead` ranking above `harness:` (`foo(?=bar)baz` under restore=look
    shows `harness:look`, while W-D8 stays `dead`);
  - W-D3..W-D7 not dead;
  - the `-fno-ctx-node` run equality on `a(?=b)[bc]` and `ab[xy](?=(?<=x)y)[xy]`.

  `[facts-arm]`'s ZP cell `zr req_set` now expects `harness:zero`, because the ZERO row gained
  PF_REQ_SET (D-1).
- **reqcube_check.py** `WIT` gains `ws4` (`x(?=qr)[pq]r`): RX_REQ_BYTE 113 is in req_set.
- **Mech** rows S3365-S3383 are one per §5.7 planted error: W-L5, W-L2, W-L7, W-L6, W-L8, W-A1, W-S1,
  W-N1, W-N2, W-F4, W-RG, W-C1, W-E1, W-T1, W-S4 (codegen), W-D1, W-D2 (facts), the flag sabotage
  (W-D3/4/6/7, facts) and W-L4 (facts).
  - Each has a `SAB_REACH` on its witness. `REACH_ONLY=1`: 19/19 REACHED.
  - Every anchor occurs once in req.c (S3382 uses `SAB_FILE2` for its second edit).
  - S1925 is re-aimed onto `case RB_ZERO_ITEM:`: E-5i's action walks the body as consumed.
  - The full DETECTED verdicts are OWED (the `.mech` job), together with the reach of S1926-S1929, S1653,
    S1887, S1907, S465, S474 and S1930.
- **D27 witnesses** are not this lane's (brief).

## Identity and movers

The two-sided compare is `docs/dev/lanes/l1feat_evidence/compare_l1.py`. It compares the base build and
the feature build over the whole population, every text, with `--emit-facts=byte,utf8`, against the
census model. Output: `scratch/l1feat/compare/compare.txt`; observed movers in `observed.tsv`.

- OBSERVED movers: 306 (byte 303, utf8-only 3). By fact (byte): dead 293, req_whole_run 2, req_set 10,
  req_set_maxoff 10, req_byte 8.
- MODEL movers: 54. Both, agreeing on facts and values: **54 of 54**. MODEL-ONLY: **0**. DIFFER: **0**.
- OBSERVED-ONLY: 249, plus UTF8-ONLY 3. `explain_l1.py` puts each one in a class by a mechanical test.
  An unclassified row is a STOP. The classes:
  - **leaf-dead** — the empty-class leaf: `x[^\x00-\xff]y`, and the many `\p{Block=...}`, `\p{Age=...}`,
    `\p{Bidi_Class:...}` and `\P{^...}` corpus texts whose class holds no byte ≤ 255 under `byte`. The
    text holds no lookaround of any spelling, and it is still `dead` under `--harness=restore=look`. The
    design anticipated it (§14.3: "the empty-class leaf widens `dead` ... the census lists them apart").
    The census population holds only positive-lookaround texts (`has_pos_look`).
  - **spelling** — `(?*`, `(*pla:`, `(*napla:`, `(*positive_lookahead:` and similar. Rewritten to
    `(?=`/`(?<=`, the feature lists the same byte facts, and the model predicts the same movers.
  - **rep-copy** — a guard meets a variable repeat's first or last copy (span arms R1's split), where the
    model reads the repeat as a WALL. Examples: `\w+(?<=a)` (req_set gains `a`), `[a-z]+(?<=a)@x` (run
    `a@x`), `\s+(?<=a)b` and `((?=a))x+\1x` (dead). Test: under `--harness=restore=rep` the item moves
    nothing (the facts equal those under `restore=rep+look`).
  - **utf8-only** — `\w{1,3}(?=a)\W` and two more: dead under utf8 only. Under byte, `\W`'s 193 members
    lie outside the run's 128-member domain, so it is not a run position; under utf8 its first-byte set is
    in the domain.

  A smoke run over 11 rows covering all four classes found 0 unexplained. The full run (252 rows) is OWED:
  `scratch/l1feat/explain.log` and `explain.txt`, completion line `== explain COMPLETE: N unexplained`.
  It waits for the box lock behind l1fix's make test.
- Every observed value checked by hand is sound against the oracle: the dead texts answer NOMATCH in
  libpcre2, and the narrowed bytes are present in every match.
- **Identity (emit_sweep, every stream, base vs the feature build `scratch/l1feat/bin/pcrec`)** is OWED:
  `ident_check.py` reads observed.tsv as its census. The abi is expected unchanged; a scaffolding mover is
  a STOP.

## Contract

`docs/spec/facts_listing.md` changes in the same commit (91e6724e7):

- **§4.1.3¶1:** the precedence order now begins with `dead`.
- **New ¶1a, `dead`:** it appears on `req_whole_run` only. The walk proved that no attempt can match. The
  status stays `derived` and the value is the walk's run. It differs from `decline:dead-start`, and no
  pass consumes it.
- **¶4a:** `zero` gains `req_set`/`req_set_maxoff`, `look` is listed with its facts and its old form, and
  `zero`'s CUT text is kept.

Unchanged and checked: match_api §6.3.7 and tuning §2.27¶4 (the set step keeps them true). The
`dead` why's readers are `fd_why`, `pf_done_why` and `run_facts_checks.sh`. `src/facts/CLAUDE.md` is
updated: the walk_arms `look` arm, desc.c's two readers, and req.c's L1 pieces.

## Deviations from the design

1. **Exact sets, not cube hulls (§5.1).** Meets intersect exact position sets, within the run's domain
   (`rn_admits`, D187 addendum 1). This settles l1build's note.
2. **The set step sets the pick when the set was empty.** The design says the pick is not updated. But
   `pcrec_find_set_pick`'s trace build fails on a nonempty set with pick −1, and the census predicts
   `\w*(?=a)\w` req_byte none→97. So the last joined byte becomes the pick only where the set had none.
3. **Head threading is one `rb_head_node` per node in `rb_walk_at`**, rather than one in every RbVal
   writer as D-10 lists. The transparent kinds (CAP, ATOMIC, WCLASS) descend, so the head of an
   `A_WCLASS` is its byte class (F5).
4. **The lookbehind reader is `pcrec_pd_tail_head`**, the trailing edge only. It is not the
   `pcrec_pd_edge(desc, dir, max_pos)` that the U-edge row names; that row's shared reader is still open
   for [VLOOKBEHIND].
5. **The `dead` bit of the empty-class leaf is not under the `look` arm** (W-D8 stays `dead` under
   `restore=look`). It is D-9's never row, not E-5i's.
6. **Observation, design followed:** `RbVal.runs.head` would subsume the head column for a lookahead (it
   reads REP copies too); kept as designed.

## STATE AT HANDOFF

- Commits on lane/l1feat: 1e2a4f5db, 91e6724e7, 15b9659bd, 7e28bfd3d, plus this report's commit.
- Rulings file: empty; last ruling: none.
- OWED (box queue, batch b20261119140703424787, a frozen snapshot of 7e28bfd3d):
  - `l1feat-b20261119140703424787.ident` — the identity sweep; completion `== ident_check COMPLETE: 0 unexplained`
  - `l1feat-b20261119140703424787.mech` — S3365-S3383, S1925, S1926-S1929, S1653, S1887, S1907, S465, S474, S1930
  - `l1feat-b20261119140703424787.axes` — run_axes.sh, AXES `--harness=restore=look --harness=restore=zero`
  - `l1feat-b20261119140703424787.test` — make test via perfrun (PC-3 included)
  - plus the boxlock run `l1feat-explain` (`scratch/l1feat/explain.log`; `== explain COMPLETE: N unexplained`)
- STOP conditions for the reader of these verdicts: an UNEXPLAINED explain row; an identity mover that is
  not an observed mover; any scaffolding (abi) mover.
