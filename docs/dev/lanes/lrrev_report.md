# lrrev — [LOSS-REVIEW] phase 2, fixes.md REVISION 2 (2026-10-11, sonnet)

Branch `lane/lrrev` from main 8359970e. Docs, one plan edit and no-clock
counts only: nothing under `src/`, no `make test`/mech/timing (a heavy chain
held the box); `build/pcrec` was built once for the three counts.

## What changed, by finding id

`docs/dev/optloop/lossreview/fixes.md` is rewritten as revision 2, shape §0-§6
kept, a revision block at the top maps ids to places, each change marked
`[r2 ID]`.

| id | applied as |
|---|---|
| R1 | 4.7M → 3.94M (the 4.7M was phone's seek-iteration count); C1 11 cells; the family claim is "100% by construction" and DENSE-SKIP is counted once (F1); cand 5 is 22.28 ms without C1c, 24.6 with; the median-ratio sentence; "7 of 88"; step numbering (cand 7 = step 9, the table is renumbered) |
| R2 | §4 gives all three orderings and the reach table; the "every ordering" claim is withdrawn; baselines tagged per cause; Q7 |
| R3 | §2.0 overlap table (all overlaps the critic listed, incl. the frameless pool 26.5 > 17.74 and mod-j-uc's 6.5-8 ms with no named candidate) and a remodel-overlap column in §0 |
| R4 | Q1 dropped (D122 add. 3 / D147 add. 6), Q2 answered with the census number, Q3 and Q5 marked manager's, Q4 split 4a/4b, Q7 added with the manager's lean |
| C1 | cand 1 restated: per-cell bands, refute = below the band's low end (Zen 1 vs 7700X noted), the `bak2-static-noinline` arm, the trail inference dropped, Q3 both options with the choice marked manager, the call-site-census UNLOCK (§1 F3) |
| C2 | DENSE-SKIP five-arm per-subject design with the collinearity and (iii) arguments; the boundary-pair skip filed with its trigger count |
| C3 | cand 3 reach split (K101 claimable, HIT-RESTART/C3/stop cost UNKNOWN), the lit-cat `swar` twin owed, near-noise DENSE cells named |
| C4, F7 | cand 6 folded into [OPT-3-RUNEND](a); mover set incl. shipped stays; `stay_len` = 1/(1-mass); reach cut to C5 + what the stay twins show |
| C5, C6 | cand 5(a) reach (mod-j-uc, bak-1 family; bak-2 the only D77 witness); cand 7 gain ~25 ms, labelled derived |
| F1 | the pricing split in §0, §1 F1, cand 5(a), §3 |
| F2, F5, F8 | F1 table = 20 members; PRIOR-COST-UNIFY generalizes `model_cost`; the signature sketch; the independence model labelled; the two kit-form constants and G1's `memchr_form` clause left as an open ruling |
| F3 | the empty `cand_ppm`/`ppm` channel in §1 F2, cands 3/5(b), §3 step 6 (after L1) |
| F4 | ONE SWAR set/cube FIND row in `pffind.c`; OFS BODY/PRE compose it; SET pair vs POSITION pair |
| F6 | cand 5(a) as an adaptive arm; the two families described in §1 and filed in plan.md |

`docs/dev/plan.md`: one dated sentence plus pointer appended to
[PRIOR-COST-UNIFY] (F5's eight members, the `model_cost` generalization), and
two STATE:not-started rows filed after it, [ADAPTIVE-ARM] and [SIZE-KNEE]
(members, general form, D77 trigger, pointer). [SIZE-KNEE]'s trigger wording is
the lane's (the critic gave members and "file not build" only). Anchored
not-started count 149 → 151.

## The three counts (no clock; raw outputs in `docs/dev/optloop/lossreview/rev2/`)

All at main 8359970e's `build/pcrec`; subjects are the 11 capability
throughput subjects regenerated in a `git archive` copy of pcrec-bench and
sha256-checked against the manifest.

1. **ATTEMPT-SPLIT size** (`split_size.txt`; Q2). concat-sqli original:
   389,031 B C / 196,839 B `.o`. The row's construction (original + the four
   `^`-free arms) is **1.384x C, 1.214x `.o`**; the exact twin (`^` arm + the
   `^`-free arms) is **1.109x C, 0.920x `.o`**. Both under the 1.5x line. The
   population half (corpus sweep of `attempt` with `start_max != 0`) was NOT
   run; the bench's single-witness finding is cited.
2. **Word-wait steps** (`wordwait.txt`; `vm/stayprobe.py` unmodified plus a
   new `wordwait.py`). The word-wait state takes 66.5 / 78.9 / 73.8% of a plain
   walk's steps on hex8 / json-constant / dbnames; mean stay run 4.29 / 4.37 /
   4.05 B (under the ~5 B break-even of the [OPT-3-RUNEND] pricing). dbnames'
   shipped stay95/stay110 states take 0 plain-walk steps on these subjects.
3. **Boundary-pair stops vs today's skip entries** (`pairskip.txt`; entries
   reproduce dfa.md's 0.146/0.095/0.067 per byte). hex8: 267,010 / 682,437 =
   **0.391** (trigger "< ~0.3" NOT met, near); dbnames 0.581 (not met);
   json-constant 0.195 (met). So the critic's named cell, hex8, misses the
   trigger narrowly; the call whether to build arm (E) is left to the manager.

## Not applied, or applied in part

- Population counts for cand 1 (artifacts with seam masks), cand 7 (corpus
  `attempt` shape) and the F3 call-site census: not run (no compile sweep
  while the heavy chain held the box); marked as such in §6.
- The D119-eligible subtotal of the 94.3 ms (rank critic 2.2): the comparators
  are TAGGED per cause in §4, but the subtotal is not recomputed.
- The cell-count ordering in the rank critic's text lists cand 2 among the
  "4 each" but its own table gives cand 2 six cells; the table's value is used.
- F5's "eight" members: the critic's list is run_window_start, run_pin,
  req_pick/req_byte, vm_reseed_cal, prefix_k's singleton gate, `pass < 4`,
  MIN_SCAN_CHAIN, FIND_FLOOR_PPM; `deferpre`'s K=64 is carried as a ninth,
  unlabelled constant, as the critic says.
- Citations to the critics' `file:line` numbers (e.g. `prefix_k.c:114-123`,
  `memfn.h:272`, `req.c:646`) are carried as the critics gave them and were not
  re-opened.

## Files

`docs/dev/optloop/lossreview/fixes.md`, `.../rev2/` (scripts, `CLAUDE.md`,
`split_size.txt`, `wordwait.txt`, `pairskip.txt`, `esc.py`, `wordwait.py`,
`pairskip_count.py`), `.../lossreview/CLAUDE.md`, `docs/dev/plan.md`,
this report. Scratch (`build/lr/`) is gitignored.
