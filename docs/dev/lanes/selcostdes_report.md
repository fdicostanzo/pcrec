# selcostdes — [SEL-COST] step 1 + [SEL-SIZE] design (2026-10-03, opus)

Branch `lane/selcostdes` from main c231ffc1 (abi 54). DESIGN ONLY: no change
under `src/`, `cli/`, `lib/` or `tests/`. `make test` was not run, per the
brief. The compiler was built in the worktree (`make -j4 CC=gcc-16`, clean)
for the compile-only census.

## Delivered

- `docs/design/sel_cost.md`: the design note. Its §0 is the answer, §1 the
  per-bucket evidence table, §2 the [SEL-SIZE] census, §3 the admission rule
  (the D77 trigger), §4 the design of record, §5 where each bucket's
  evidence goes instead, and it ends with eight questions for the manager,
  each with a recommendation.
- `docs/design/sel_cost/`: `census.py` and `census_large.tsv`, the
  compile-only census (5,024 compiles, about 5 min on the Mac);
  `percall.c`; `timing_mac.md` (the T1-T3 scratch tables); `CLAUDE.md`.
- `docs/design/CLAUDE.md` index entries.

## Findings (resume from here)

1. No STEP 0 bucket clears D119's bar as a compile-time selection term.
   B, C and D all flip sign with the subject or the regime on identical
   compile-time stamps. A keeps its sign, but it is about 2.5 ns/call
   (`^item` 3.7 vs 1.2 ns), and `dfa_scan=attempt` also selects the
   validators, where the DFA wins ×1.7-×5.1.
2. [SEL-SIZE] is refuted. There are 170 warned (≥250 KB) auto-DFA artifacts,
   108 of them altwide, where the DFA wins ×1.8-×2.0 (Mac) and O-82 A4
   measured forced VM ×25-×229 slower. The `(?:[a-z]{0,N})\z` loss is
   ×6.7-×8.0 at N=256 (67 KB, unwarned) exactly as at N=4096 (477 KB). It
   is the `\z` form losing its scan edge, and that is [OPT-VEDGE]'s
   mechanism.
3. Bucket B persists at abi 54 (VM ×1.10-×1.47 on prose, ×3.08 inside long
   `\p{L}+` runs), but `\p{L}+` is a DFA ×17 win on a letter-free subject.
   It belongs with [OPT-3-RUNEND] (a).
4. When the trigger fires, the mechanism is: pre-build rows as a first-match
   table in `pcrec_select_engine`'s auto arm, and post-build rows through
   [SEL-1]'s retry (`forces_dfa_overflow` gains a reason). Each row gets
   `-fno-sel-<row>` and the family gets `-fno-sel-cost`. A post-build
   decline stamps `ENGINE_SEL "cost-declined"`. No abi bump
   (decisions.md:6408). Constants go in limits.def `"selection knee"` rows.

## Validation

The scratch timings are Mac-only and directional, on a shared box (load1
1.8-5.1). Answers were checked equal on every timed row. There is no Linux
run; none is owed by this lane, since nothing is built.
