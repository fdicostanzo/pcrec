# Lane r45f report: R-45 reply rev 6 (review r25, R5-1..R5-6 as ruled)

Lane r45f (opus), 2026-11-16. DESIGN ONLY: no code, no timing, no box jobs, no build, no edits
to `memfn/docs/requests.md` or `responses.md`. Worktree `worktrees/r45`, branch
`lane/memfn-r45` (started at 92ef0613f). Input: the ruled review
`/var/tmp/pcrec-pcrec/scratch/crit-memfn-r45e/review.md` (its RULED section). Code facts read at
origin/main `ed9677782b76b8b5b64f571185776fea785581ae` (fetched at lane start; local main
`a66bf0877` is ahead and unpushed).

## Summary

- The review is filed unchanged as `docs/dev/reviews/2026-11-16-r25-memfn-r45e.md` (`cmp`
  identical to the scratch copy) and indexed in `docs/dev/reviews/CLAUDE.md`. Number choice:
  r19-r23 are taken; no r24 or r25 exists on main, origin/main, this branch,
  `lane/memfn-d3wire`, any local branch or any worktree. The brief names this review "r25", so
  r25 was used and r24 left free (it may be held for another round). If r24 was meant, it is a
  file rename plus two index lines.
- `docs/design/memfn/r45_reply.md` is rev 6, opening with "Changes in rev 6" by R5 id.
  `docs/design/memfn/CLAUDE.md`'s r45_reply line now says rev 6.
- R5-1 restates the mover predicate in the segmenter's terms and withdraws "h\* >= 32 moves
  nothing". R5-2 adds step (5): any twice-void C1-C2 cell forces h\* = 64, and the pick from
  the cells that were read is recorded but not shipped. R5-3 to R5-6 are text fixes. §8 is 38
  lines (limit 40) and matches the body.
- Every drill was re-run with a new script against the rule as written in rev 6: (i)-(xi)
  unchanged; r25's drills V and N added as (xii) and (xiii); a missing-regime drill added as
  (xiv). Two property searches were also run.

## Fixes by id

- **R5-1 (mover predicate, segmenter's terms).** Read at origin/main `ed9677782`:
  `memfn/src/window.c` `merge` (C-MEET) turns each alternative's spans into ONE position per
  offset. That position is the AND of every span stating that offset, plus a separate
  verify-YES meet that `rd_set` tests on a PARKED-entry alternative without reseed. `plan_of`
  sorts the plan positions by offset. `find_groups` groups consecutive offsets by the compare
  key `c_run` gives.
  - Today's kind-1 run compare joins positions only inside ONE stated span of length 2 or
    more (`c_run`'s `same` test). The new kind-2 one-class repeat is stated as a maximal run
    of consecutive offsets with one byte-identical multi-member set, ACROSS span boundaries
    and into a cover's sides. This is the kit manager's ruling, written into §3 "The forms".
  - Predicate (§3 "Which sites move"): over EVERY window alternative (the site's own and each
    pre-check part's), a run of 2 or more consecutive stated offsets with one identical set of
    2 or more members, under either meet, whose LAST offset is >= h\*.
  - Witness `\w{32}\B`, checked read-only with the main tree's `build/pcrec -p rx --features
    assertions,classes` into lane scratch: it emits `RX_DFA_SCAN "cover"`, and the chain tests
    `s[c + 32]` with the same `\w` range test as `+ 30`.
  - Kin: `\w{k}\B` and `\W{k}\B` (`\W{8}\B` emits a cover). Not kin: `\d{32}\B` (its after
    side is `\w`) and `\B\w{32}` (no cover).
  - Re-derived at width 32. The largest stated offset is 32: the cover's after side
    (`known.c` `cover_window`); the pre-check run states 0..31; the prefix walk stays below 24.
    So h\* = 64 moves nothing, h\* = 32 moves only the cover kin, and h\* <= 24 makes no
    nothing-moves claim. The rev-5 change row is marked superseded.
- **R5-2 (void).** New R1 step (5): steps (1)-(4) run over the cells that were read. A
  twice-void cell gives the term 1 to each head whose text is I there and no term to any other
  head, and dominance reads only the cells read. The pick from those cells is RECORDED. If any
  C1-C2 cell is void twice, h\* = 64, labelled with the void cells and the recorded pick. So a
  void never removes a competitor and never lowers h\*. Two rejected readings are stated with
  evidence:
  - rev 5's +infinity reading gives h\* = 24 on drill V, where reading the cell clean gives 32;
  - a "skip the void cell, refuse an unread pick" variant gives an h\* below the clean reading
    in 35 of 200,000 random cases. Its mechanism: a head whose loss was in the void cell joins
    E and dominates a larger head.
  Step (5) also settles R5-7 (a) (the label) and (b) (no void cell in dominance). R5-7 (c)
  points at cover_cap.md §11.4 row 1.
- **R5-3 (bench lever reader).** "The regimes' methods" gains the case where a regime's method
  cannot run on the kit's harness. The bench then compiles that regime's CARD cells through
  `build/pcrec-harness --harness=span-head=N`, which is TEST-ONLY. Added with it:
  - a bench-only question: can the bench do this, or can the method be ported to the kit's
    script? If neither, those cells are twice-void and step (5) applies;
  - a G7 fence note: pcrec-bench is not scanned.
  The lever's reader list gains the bench (this case only). "The bench is NOT a reader" now
  reads "for the WIDTH cells". §7 lists the bench question.
- **R5-4 (identity population).** The identity check now covers EVERY predicted mover at h\*,
  cover or not, plus every card pattern and every census cover. It compiles each pattern twice
  at pcrec level: the frozen binary's lever, and the rebuilt `build/pcrec`. It then compares
  the emitted C bytes. At h\* = 64 the predicted set is empty. §6 Q2 is updated.
- **R5-5 (predictor record).** No record exposes per-site window statements on main. The only
  statement record under `PCREC_MF_ROUTE_TRACE` is `MFPRES`, which holds counts, and
  `span_facts` is gone. The reply names a NEW pcrec-side trace record, `MFWSTMT` (main's
  build), beside `MFPRES`. It writes one line per stated span with these fields:
  - site id, site kind, and whether the span belongs to the site or to part i;
  - the alternative, its entry, and whether it reseeds;
  - the span index, start, len, verify, core_lo and core_len;
  - the span's sets, as 64 hex digits each.
  The reply also names the predictor change and a trace-build pass in the sweep. The record is
  in §7's main list and in the §11.1 edit.
- **R5-6 (dominance wording).** The same text now appears in §0, the R1 step (3) clause, §7
  and §8: "dominated (faster beyond `f` in at least one cell and never slower beyond `f`) by
  the fewest others".
- **§8.** Rewritten (3): the rule with the R5-6 wording, the void step, the predicate in
  segmenter terms with its witness, h\* = 64 / 32 consequences, MFWSTMT, the identity
  population, and the bench lever case. Line count 38 by
  `awk '/^## 8\./{f=1} f' | awk '/^```$/{c++; next} c==1' | wc -l`.

## Drills

Script `/var/tmp/pcrec-pcrec/scratch/memfn/r45f/drills6.py` (scratch, not committed). It
implements R0 and R1 steps (1)-(5) as written in rev 6. Mode `rev5` reproduces rev 5's
+infinity reading, and mode `skip` is the rejected variant. Run with
`python3 -I drills6.py`. Output, verbatim:

```
(xii) V k=24 cell twice-void under REV 5's reading (for the record): E=[24, 32, 64] kept=[24] h*=24
(i) all equal: E=[0, 1, 2, 4, 8, 16, 24, 32, 64] kept=[0, 1, 2, 4, 8, 16, 24, 32, 64] h0=64 h*=64 [grid top (64, CHOSEN), on a measured tie of every finite head]
(ii) I wins one k=24 cell: E=[24, 32, 64] kept=[24, 32, 64] h0=64 h*=64 [grid top (64, CHOSEN), on a measured tie of [24, 32, 64]]
(iii) L faster everywhere: E=[0] kept=[0] h0=0 h*=0 [MEASURED]
(iv) all within noise: E=[0, 1, 2, 4, 8, 16, 24, 32, 64] kept=[0, 1, 2, 4, 8, 16, 24, 32, 64] h0=64 h*=64 [grid top (64, CHOSEN), on a measured tie of every finite head]
(v) I wins at k=60: E=[64] kept=[64] h0=64 h*=64 [grid top (64, CHOSEN): every shorter finite head measured slower beyond f]
(vi) near-equal chain: E=[1, 2] kept=[1, 2] h0=2 h*=2 [MEASURED]
(vii) base: E=[8] kept=[8] h0=8 h*=8 [MEASURED]
(vii) + losing h=4: E=[8] kept=[8] h0=8 h*=8 [MEASURED]
(viii) (ii) with 64 failing G2: E=[24, 32] kept=[24, 32] h0=32 h*=32 [MEASURED]
(viii) every h failing G2: every finite h removed by R0 -> no form ships (plan A fallback)
(ix) dominance cycle: E=[8, 16, 32, 64] kept=[8, 16, 32] h0=32 h*=32 [MEASURED; CYCLE: kept those dominated by the fewest (1)]
R3-1 H(8)/H(32): E=[8, 16, 24, 32, 64] kept=[8, 32] h0=32 h*=32 [MEASURED]
(x) base: E=[8, 16] kept=[8, 16] h0=16 h*=16 [MEASURED]
(x) + h=4 at 0.95: E=[4, 8] kept=[4, 8] h0=8 h*=8 [MEASURED]
(x) + h=4 at 0.985: E=[4, 8, 16] kept=[4, 8, 16] h0=16 h*=16 [MEASURED]
(xi) base: E=[8, 16] kept=[8, 16] h0=16 h*=16 [MEASURED]
(xi) + h=12: E=[8, 12, 16] kept=[8, 12] h0=12 h*=12 [MEASURED]
(xii) V clean k=24 cell: E=[8, 24, 32, 64] kept=[8, 24, 32] h0=32 h*=32 [MEASURED; CYCLE: kept those dominated by the fewest (1)]
(xii) V k=24 cell twice-void: E=[8] kept=[8] h0=8 h*=64 [grid top (64, CHOSEN): twice-void cell(s) k=[24]; the read cells' pick H(8) recorded, not shipped]
(xii) V k=40 cell twice-void: E=[8, 24, 32] kept=[32] h0=32 h*=64 [grid top (64, CHOSEN): twice-void cell(s) k=[40]; the read cells' pick H(32) recorded, not shipped]
(xiii) N NOT-WARM-only loss of H(8): E=[0, 1, 2, 4, 16, 24, 32, 64] kept=[0, 1, 2, 4, 16, 24, 32, 64] h0=64 h*=64 [grid top (64, CHOSEN), on a measured tie of [0, 1, 2, 4, 16, 24, 32, 64]]
(xiv) regime void: H(8) wins hit-dense, NOT-WARM void: E=[8] kept=[8] h0=8 h*=64 [grid top (64, CHOSEN): twice-void cell(s) k=[32, 24]; the read cells' pick H(8) recorded, not shipped]
search (100000 random 3-cell cases, one cell voided): h* below the same cell read clean: rev 6 0; rejected skip variant 0
wider search (200000 random 4-cell cases, 1-2 cells voided, f in .02/.03/.05): h* below the same cells read clean: rev 6 0; rejected skip variant 35 (first: k=[24, 24, 60, 36] void=[1] f=0.05: clean h*=32, skip h*=24)
```

Readings:
- (i)-(xi) match rev 4/5's stated results exactly, because no drill has a void cell.
- (xii), r25's drill V: read clean, h\* = 32. Rev 5's reading gives 24 (the defect). Under
  rev 6, the k = 24 cell void twice gives h\* = 64 with the recorded pick 8, and the k = 40
  cell void twice gives 64 with the recorded pick 32.
- (xiii), r25's drill N: h\* = 64, and the NOT-WARM loss moved h, not the width default.
- (xiv), a regime missing: h\* = 64, labelled with both void cells.
- Searches: under rev 6 the void reading is never below the clean reading (0 of 100,000 and
  0 of 200,000 cases). This holds by construction, since a void yields 64. The `skip` variant
  falls below the clean reading in 35 of 200,000 cases.
- The 32->24 void drill named in the brief is (xii).

## STATE AT HANDOFF

- STATE: done. Commits on `lane/memfn-r45`: the deliver file (unchanged), the review copy with
  its index, rev 6 with the memfn index line, and this report.
- Rulings file `docs/dev/lanes/r45f_rulings.md`: empty at every re-read. Last entry applied:
  none.
- Open for the kit manager:
  - the review number (r25 used; r24 is free everywhere checked);
  - step (5) is the lane's form of the ruled "a void cell never helps another head". Its cost
    is stated in §3: one twice-void cell forfeits that night's win.
- An untracked `r45d.done` file at the worktree root is stale and not this lane's. It was
  left alone. `scripts/lanecheck --deliver WT/docs/dev/lanes/r45f_deliver.txt --dir WT r45f`
  reports exactly one issue: "the tree is not clean: r45d.done". Lane r45e hit the same
  issue. The lane does not commit or delete another lane's file, and it does not edit the
  manager's deliver file to add a dirty-ok line. So lanecheck ends at rc=1 on that one
  issue; every other check passes.
- OWED: none
