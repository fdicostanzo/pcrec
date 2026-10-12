# pcurev — [PRIOR-COST-UNIFY] design note revision 2 (2026-10-11, lane pcurev)

Lane pcurev (opus, design only). Worktree `worktrees/pcurev`, branch
`lane/pcurev` from main `4a9748bb` (abi 75). Charter:
`docs/dev/reviews/2026-10-11-r3-prior-cost-unify.md`, every row ACCEPTED.
Nothing under `src/`, `tests/` or `docs/spec/` changed. The box ran the kit's
heavy slot23, so the lane did no `make test`, mech or timing. It used one
worktree `make -j16` and a few dozen single compiles.

## Delivered

- `docs/design/prior_cost_unify.md`, revision 2. A §R2 block at the top
  lists every change by finding id. Each disposition is marked `[r3 ID]`
  where it lands.
- `docs/design/prior_cost_unify/` (own CLAUDE.md), the instruments the panel
  asked for:
  - `census.py`: the derived census with a completeness check, plus
    `census_disp.tsv` and its output `census.tsv`.
  - `meter_sites.sh` and its output `.tsv`: the site-derived D158 control.
  - `grid.py` and its output `.txt`: the arithmetic grid with planted
    off-by-ones.
  - `island_work.sh` and its output `.txt`: F-8's dynamic witness.
  - `q4_exemplar.sh` and its output `.txt`: K105 under an exemplar bundle.
- `docs/design/CLAUDE.md`: the entry is rewritten, and an entry for the
  instruments directory is added.

## Measured in the lane (all light, worktree build at 4a9748bb)

| what | result |
|---|---|
| census (F5) | 10 roots, 14 readers: 9 MEMBER functions holding 10 decisions (COMPARE 1, PICK 6, VERDICT 3), 3 CARRIER, 2 NOT. Failing direction run both ways: a deleted row reads UNDISPOSITIONED + below floor; a planted `rn_better` row reads STALE |
| meter prototype (S2/F1) | 11 (axis, witness) pairs. Possessify and its two arms: SUBSTITUTES (K102's class). lit-run: DELETES. alt-island: SUBSTITUTES (Δpush −2, Δwork +6). counter/revdet/hyb-reseed/start-set: NONE (static sites cannot see removed attempts; stated as the control's limit) |
| F-8 dynamic | `(foo\|bar\|baz)q` on `fooq`, `--work-budget=2`: default gives up `work`; `-fno-alt-island` answers `match 0 4`; same on auto (artifact VM) and forced VM |
| grid (F3) | U1 pairs 0 disagreements (#3 vs rational advance and vs rev 1's adv_milli, 1,332 cells each; #4/#7 products 17,475 each; #4 admission 749,100). Plants: `>=` reads 4, other rounding 17,471, ceil off-by-one 178, K+1 67 |
| Q4 exemplar | hcolon_in's pattern: default `RX_DFA_PREFILTER "handoff"`; with a 36 KB synthesized colon-dense exemplar (`pcrec-analyze --scan freq`, `-I DIR --analysis=colondense`): `"byte-class"`. FIRST's entry handoff stays (`RX_REQ_HANDOFF "101"`). No timing |

## Findings beyond the panel

1. **F-8: a second D158 violator.** The [ENG-ISL] alternation island charges
   WORK per trie byte where the denied form spends STEPS on resumes, so a
   caller-tuned `--work-budget` gives up where `-fno-alt-island` answers.
   This is K102's class, and D158 add. 1 accepts only K102. It needs a K row
   or an extended allowance (the manager's / Frank's call). It is the
   [EFFORT-BUDGET] study's second witness.
2. **F-11:** on its witness, the lit-run axis derives DELETES (work sites −4)
   where rev 1 declared SUBSTITUTES.
3. **F-7:** the necessary set's pick is spelled twice: `pcrec_req_pick`'s
   last line and `req_set_pick` in the emitter. Answers are identical by
   construction. Fold it when PRESENCE next moves.
4. **F-9:** rev 1 was wrong to say R4 mixes a Zen 1 rate with a Mac gap.
   Rates are box-free, and no shipped verdict mixes boxes.
5. **F-10:** `pcrec_sat_add` computes `a + b` before its cap. It is sound only
   for its callers' 2^40 operands, so rev 2 adds a core-owned unsigned helper
   instead of reusing it.
6. **A5 (an adapter the panel did not name):** `pcrec_dfa_cand_ppm` returns
   10^6 for "no usable scan / ATTEMPT route". Mapping that onto rev 2's NONE
   (zero stops) would flip R4, so U1 maps it to `SET(Σ)`.
7. **Exemplar route (Q4):** an exemplar bundle already declines K105's
   re-entry compile-side, with no build.

## Judgement calls for the manager to check

- **The meter column lives on `axes.def`, one cell per counter** (`le` or
  `gt:<K-row>`), with no default, so a missing cell is a build failure. The
  RETRY rows with no deny are not axes; they stay with LR-S11's twin.
- **The cost is a SCALED NUMERATOR with no division.** `PCREC_OPCOST_CELL_MAX`
  = 2^14 native units, the verify chain ≤ 8 and the bar ≤ 16, giving N × bar
  < 2^62.7. If a future cell exceeds 2^14 cc, the static assert fires first.
- **`flip` is the smallest stop rate reading DECLINE**, and a tie is DECLINE,
  following `prefix_k`'s strict `<`.
- **"Nothing is switch now."** Under F10's no-accessor rule, every U2 that
  prices `stop_reentry` is blocked. #3's cost form is not blocked (it has one
  box's cells), but the grid names it a mover band.
- **The runtime-arm family's table owns all four `vm_reseed_cal` columns.**
  The gap is not moved into the opcost table, which would be a parallel
  table.
- **The [MATCH-SPLIT] END proxy is restricted to single-stay arms**, and
  multi-stay arms are declined under it.

## Owed (not this lane's)

- The time cell for the exemplar route (does the colon-dense exemplar build
  recover hcolon_in's ×1.537?), owed with Q4's decision.
- U1's adapter reach counts (trace build), U4's population meter sweep, and
  every build step.
- F-8's K row (manager).

## Resume point

A follow-up round starts from `prior_cost_unify.md` §R2 and §7: Q1 and Q4
are open for Frank. The instruments re-run from the main tree:
- `python3 docs/design/prior_cost_unify/census.py .`
- `docs/design/prior_cost_unify/meter_sites.sh build/pcrec <scratch>`
- `python3 docs/design/prior_cost_unify/grid.py`
