# slbuild — [START-LANDING] SL1-SL3 built

Lane slbuild, 2026-10-10, opus (engine tier). Branch `lane/slbuild` off main
`06d19c67` (abi 73, [OPT-REVEND] L1 + L2 with stage 2 merged). Design:
`docs/design/start_landing.md` revision 2 (§R2, §2, §3, §7, §9); rulings D156
addenda 3 and 4 (Q1-Q4), Q5 resolved.

## 0. STEP 0 — the edit set re-derived, and the design reconciled with main

The design was written at `efc58146` (abi 71), before locate × finish L0
(`c85a1aac`) and [OPT-REVEND] L1 + L2 with stage 2 (abi 73). Its edit set is
re-derived at `06d19c67` as `studies/start_landing/edit_set_main.tsv` (the
design's `edit_set.tsv` is left as written, at its pin). Every `line` entry
occurs exactly once in its file at this pin (counted).

**The census** (`docs/design/start_table/call_graph.py .` at this pin, then
`sabotage_anchors.py . CG studies/start_landing/edit_set_main.tsv --final
after-SL3 --edit-names`): 639 row files, 660 sites, 137 in the family.
- **RE-AIM at SL2 (11):** S07, S221 (`unanch_scan`: pinned's success site and
  the dispatch move into the one success-site emitter), S223 (the
  `start_pinned_assert_routing` line becomes the per-action assertion), S693
  (the abi literal), and S758, S759, S760, S764, S765, S766, S780 (rows inside
  `emit_rev_end`, a `def` this lane edits: the census classes every anchor in a
  rewritten definition as a re-aim; the ones whose anchor TEXT does not move
  re-run unchanged, recorded per row at SL2).
- **RE-RUN at SL2 (28 sites):** the `cand_rows[]` rows (S283, S284, S462, S473,
  S594-S600, S610, S738, S741, S745, S768, S770-S772, S777), the four
  `pf_emit_first_*` rows (S481-S484, the NEXT closers), S566 and S572; 104 sites
  once after SL3.
- The 3 unresolved `src/` sites (S176, S571, S640) are pre-existing and outside
  the family, as at L0 (the tool's exit 2 is theirs).

**What no longer holds as written, and the site it moved to (no design
change):**
1. **SL3's hand is already built** (revbuild L2, `[r2-landing]`): RECOVER asks
   carry `CandSel.hand`; `CAND_HAND_EXISTS` (the composite) and
   `CAND_HAND_WINDOW` (the `rev-end` walk) exist as the design's masks; rows take
   per route (`pinned` EXISTS only, `reverse-pass` both); `dfa_search_start_of`
   reads the PATH's cell (the LOCATE row's `u.locate.recover`); the trace build
   aborts on a hand-less ask (`recover-no-hand`). What is left for SL3 is the
   per-HAND totality check on RECOVER (the self-check has it for FINISH only)
   and the two sabotage rows the design declared unreached until L2.2 (rows 8
   and 13), now reachable. The two new rows' `take` cells (EXISTS only) must
   land WITH the rows in SL2: a row without them would be selected by
   `rev-end`'s WINDOW ask.
2. **`recover_on_path` exists**: it is `cand_recover_asked` (L0 re-spelled
   `pinned`'s P4 as the path's read). The two new predicates call it; no new
   function.
3. **`dfa_search_is_pinned` has two callers, not five** (`emit_unanchored`,
   the orientation block), plus `emit_rev_end`'s two assertions on
   `u.recover.pinned`. R's membership is already L0's member fold
   (`cand_path_members`, `CAND_MR`), and the machine stamps already fold over
   `dfa_member_machines`, so a row whose `.needs` omit R drops it with no stamp
   edit, as designed.
4. **The empty engine stamps `attempt-start`, not `reverse-pass`** (L2.1's
   generated rule): an empty body's path asks no RECOVER, so SL-C1's W0/L0′ is
   structural on the path, and §7.3 §1's witness `a\bb` reads `attempt-start`.
5. **End-pinned fixed-width patterns now take `rev-end`** (WINDOW hand), so
   neither new row applies to them, as §3.3 designed; the design's mover counts
   (bench 155+155, corpus 1,750/1,751) are re-measured at SL2 against this pin.
   The `rev-end` relocate (a tie with no anchored machine) re-enters the
   composite's scan; it runs the PATH's RECOVER row (the WINDOW ask's,
   `reverse-pass`), whose reverse machine the walk already needs.
6. **The `search-start` listing has a fifth row** (`attempt-start`, L2.1's
   absence row). The new rows list 2 and 3, `reverse-pass` 4.
7. **The abi event is 73 -> 74.**

No assumption fails in a way that changes design; the build proceeds.

## 1. SL1 — the facts (no artifact mover)

**Built.** `src/facts/kset.c`: the frontier walk is ONE iterator
(`wstart`/`wclose`/`wadvance`); `wclose` is one closure in two phases (the
exact closure with assertions stopped at, then the passing one), so it also
reports `accept_free` and `asrt`. Two E3 core facts in `facts.def`, owner
`src/facts/kset.c`: `width` (`pcrec_width_walk`, `[bmin, bmax]` over the union
frontier, assertions passed) and `land_char` (`pcrec_land_char`, Λ: per byte,
exact, mid-character read off `PcrecEnc.start_cls`, a re-met mid-character
frontier a cycle via a memo instead of a depth constant, Λ.2 asserted as
K50-NULLGATE). `--emit-facts` lists them (`one-char` / `one-char+guard` /
`declined` with `decline:nullable|assert-at-start|dead-start|alive-not-accept|
assert-after`; `[bmin,bmax]` / `[bmin,inf)`). Spec: `facts_listing.md`
§4.1.2¶7a/¶7b and §4.1.3¶3.

**Checks.**
- (a) Census agreement (`studies/start_landing/agree_sl1.sh`, the design's
  probe functions re-anchored into a scratch copy of HEAD, the same compile):
  bench 734 compiles, 545 agree, 0 disagree, 6 `capped` (the probe's 4096-byte
  width cap: `cls-upto-8192/16384`, `cls-lazy-16384`, where the build reads
  `[0,8192]`/`[0,16384]`); corpus 9,420 compiles, 5,909 agree, 0 disagree, 6
  capped. Summaries in `studies/start_landing/results/slbuild/`.
- (b) The hand-witness table, `tests/codegen/run_facts_checks.sh` §9
  `[facts-sl1]`: 15 literal witnesses written from the definitions (the
  design's 12 plus `a*`, `a|bc`, utf8 `\w+`), REACH over the four reachable
  declines; 9/0. Failing direction: a plant reading an assertion after the
  first character as an accept turns it red on `\w+\b` and `a\bb`.
- Zero-mover gate: `scripts/emit_sweep.py --ref 06d19c67` — c-default,
  c-vm, emit-ir-vm, emit-ir-auto (four arms), stderr, composition, dumps: 0
  movers, 0 asymmetric. The facts stream moves on all 5,125 reached compiles,
  by the two new rows (the listing prints every fact). `make strict` clean.

**Deviation.** The design's hand table wrote `a\bb`'s Λ as "(empty engine)";
§2.4's definition gives `decline:assert-after` (an assertion before the
accept), and the table carries that. `dead-start` has no witness (a start
closure with no consumer, accept or assertion is not a machine this parser
builds); it is the safe answer for one.

**Scope note.** One backup copy of `src/facts/kset.c` was written to `/tmp`
for a failing-direction plant and removed at once; every other scratch file is
under this worktree's `build/scratch/`.
