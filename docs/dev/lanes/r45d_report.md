# Lane r45d report: R-45 reply rev 4 (applies fix-induced re-check review r23 as ruled)

Lane r45d (opus), 2026-11-16. DESIGN ONLY: no code, no timing, no box jobs, no build.
Worktree `worktrees/r45`, branch `lane/memfn-r45` (started at daa87c605).

## Summary

- Filed the ruled review r23 unchanged as `docs/dev/reviews/2026-11-16-r23-memfn-r45c.md` and
  indexed it in `docs/dev/reviews/CLAUDE.md`. r23 is free: `git log --all` names no
  `2026-11-16-r23-*` review (main has r19 on 2026-11-16; r20/r22 are this branch's, r21 is on
  `lane/memfn-d3wire`).
- Revised `docs/design/memfn/r45_reply.md` to rev 4, with a "Changes in rev 4" table by r23
  finding id. R3-1 through R3-7 are applied as ruled. R3-8 is NOTED; only its item (b) is
  applied, because §8 had to stay consistent with §1.
- Re-ran every drill with a script that implements R0-R1 exactly as rev 4's table states them
  (Drills below). Every drill agrees with the reply's text.
- **One addition the kit manager must rule: the dominance-cycle clause.** "Beyond `f`" is a
  tolerance, so dominance can be cyclic. A random search found three heads, each dominated by
  another (drill ix). The ruled step then removes every member of E, and the rule has no answer.
  Rev 4 states the general form: keep the members of E dominated by the FEWEST other members.
  This is exactly the ruled step whenever an undominated member exists. In a cycle it keeps
  the cycle and drops the heads that every member beats. The alternative, "skip the step", was
  tried first and rejected: in drill (ix) it ships 64, which every other member of E beats.
- **One refinement main must confirm (R3-6).** r23 offered the simplest disposition, and rev 4
  takes it: B's width cells run on the binary REBUILT with h\* compiled in, after the identity
  check passes. That takes the bench out of the head lever's readers. It also refines step 3 of
  the night order agreed with main, so rev 4 says main confirms it. The other route is spelled
  out as well: if the width cells stay on the lever binary, the bench is a reader, and that is
  a bench-only question.
- R3-5's witness was verified with the main tree's `build/pcrec` (read-only; outputs in lane
  scratch). `[0-9a-f]{32}` emits `#define RX_DFA_SCAN "cover"`, and `[0-9a-f]{33}` and
  `[0-9a-f]{40}` emit no cover.
- Two drill inputs were made realistic: (vi) and (ix). At C1-C2 lengths H(64) renders exactly
  I, so W(64) is 1. Rev 3's (vi) gave H(64) a value of 1.12, and under rev 4's rule that would
  have mattered.
- §8 is 37 lines inside the fence. Every owner question is in plain words, with a slug and a
  leaning.

## Fixes by id

- **R3-1 (FIX-NOW, ruled).** §3's R1 row is now four steps: W, E, dominance, the largest kept h.
  "Why each choice" explains why the dominance step exists: I is the normaliser, so a head that
  wins in some cells and ties in the rest has W of about 1. The H(8)/H(32) drill is in the reply
  and gives h\* = 32, where rev 3 gave 64. The stability trade (§3) and keep-short-spans (§7) now
  say "faster somewhere, slower nowhere". The lane added the cycle clause (Summary).
- **R3-2 (FIX-NOW, ruled).** The false claim "a never-picked value cannot move the pick" is
  replaced by a precise list. A value that is not the minimum cannot move the threshold, and so
  cannot move any OTHER member in or out of E. The threshold's dependence on the best W is
  inherent and accepted. A value that joins E can still move h\*, as E's largest member or by
  dominance. Drills (x) and (xi) show both cases. Wording note: the ruled phrase "cannot move E"
  is true of E's other members only, because the value can join E itself. The reply says that.
- **R3-3 (FIX-NOW, ruled).** h\* = 64 is labelled "h = grid top (64, CHOSEN), on a measured tie
  of every finite head", or "of" the members of E, or "every shorter finite head measured slower
  beyond `f`". The labels appear in the R1 row, the grid note, Goal 3, §0, the drill summary,
  keep-short-spans and §8. R5's loss against I or L is the TRIGGER that extends the grid past
  64 (R5 row, grid note).
- **R3-4 (FIX-NOW, ruled).** "main, with Frank" is now used in §3 "A's fallback", §7
  forms-now-or-next and §8. Rev 3's changes-table F14 row is annotated. A grep finds no "owner
  told" left.
- **R3-5 (FIX-NOW, ruled).** Row (b) now uses `[0-9a-f]{32}` with nothing after it: k = 32,
  last_s = 31, and the cut end is 32 < k, so B5 fires. How we know it is a cover: stage 1's
  `cc_fits` (k <= 32), stage 2's C15 conjunct `k <= W` at the default 32 (cover_cap.md §11.1
  A3), and the `build/pcrec` check above. Its REACH asserts both facts: the pattern takes the
  cover at the default width, and the after side is unstated.
- **R3-6 (FIX-NOW as text, ruled).** The G7 fence is listed as a reader: `cli/CLAUDE.md`'s lever
  rules, and `run_lever_fence.sh`'s `ALLOW` regex plus its comment, wherever
  `--harness=span-head=` is spelled under `tests/`, `scripts/`, `cli/`, `docs/spec/` or
  `docs/guide/` (`memfn/` is not fenced). The bench reader is handled as described in the
  Summary. The night order step 3, the §11.4 edit text and §7's "answered" entry are updated to
  match.
- **R3-7 (FIX-NOW as text, ruled).** The reply now states that L and H render at EVERY window
  span. The reseed, pre-check and run families gain draws at h-1, h and h+1 for every finite
  grid h from 16 to 64. The COUNTED line is per family and per h, and it fails at zero for any
  pair. The runtime line and §6 Q2 are updated.
- **R3-8 (NOTED).** Item (b) is applied in §8 ("every over-read below 4096 reaches B5").
  Items (a), (c), (d) and (e) are build-time notes, recorded in r23 itself.

## Drills

Script: `/var/tmp/pcrec-pcrec/scratch/memfn/r45d/drills.py` (lane scratch, not committed), run
with `python3 -I`. Its rule function is copied verbatim here, so the output can be checked
against the reply's R1 row:

```python
def r1(f, I, H, defective=()):
    hs = sorted(h for h in H if h not in defective)          # R0
    if not hs:
        return None
    cells = range(len(I))
    W = {h: max(H[h][c] / I[c] for c in cells) for h in hs}  # normalised against I
    m = min(W.values())
    E = [h for h in hs if W[h] <= (1 + f) * m]                # one threshold, no chain

    def faster(g, h, c):                                      # g faster than h beyond f in c
        return H[h][c] / H[g][c] > 1 + f

    def dominates(g, h):
        return any(faster(g, h, c) for c in cells) and not any(faster(h, g, c) for c in cells)

    by = {h: sum(1 for g in E if g != h and dominates(g, h)) for h in E}  # computed once, over E
    dominated = {h for h in E if by[h]}
    least = min(by.values())                                  # 0 unless every member is dominated
    surv = [h for h in E if by[h] == least]
    cycle = least > 0                                         # tolerance cycle: every member dominated
    hstar = max(surv)
    if hstar != GRID_TOP:
        label = "MEASURED"
    elif len(E) == 1:
        label = "grid top (64, CHOSEN): every shorter finite head measured slower beyond f"
    elif E == hs:
        label = "grid top (64, CHOSEN), on a measured tie of every finite head"
    else:
        label = "grid top (64, CHOSEN), on a measured tie of " + str(E)
    if cycle:
        label += "; dominance CYCLE: kept those dominated by the fewest (" + str(least) + ")"
    return dict(W={h: round(W[h], 3) for h in hs}, E=E, dominated=sorted(dominated),
```

Output (each drill's E, dominated set, kept set, h\* and label; then each head's W):

```
(i) all equal: E=[0, 1, 2, 4, 8, 16, 24, 32, 64] dominated=[] survivors=[0, 1, 2, 4, 8, 16, 24, 32, 64] h*=64 [grid top (64, CHOSEN), on a measured tie of every finite head]
    W={0: 1.0, 1: 1.0, 2: 1.0, 4: 1.0, 8: 1.0, 16: 1.0, 24: 1.0, 32: 1.0, 64: 1.0}
(ii) I wins one k=24 cell: E=[24, 32, 64] dominated=[] survivors=[24, 32, 64] h*=64 [grid top (64, CHOSEN), on a measured tie of [24, 32, 64]]
    W={0: 1.1, 1: 1.1, 2: 1.1, 4: 1.1, 8: 1.1, 16: 1.1, 24: 1.0, 32: 1.0, 64: 1.0}
(iii) L faster everywhere: E=[0] dominated=[] survivors=[0] h*=0 [MEASURED]
    W={0: 0.8, 1: 1.0, 2: 1.0, 4: 1.0, 8: 1.0, 16: 1.0, 24: 1.0, 32: 1.0, 64: 1.0}
(iv) all within noise: E=[0, 1, 2, 4, 8, 16, 24, 32, 64] dominated=[] survivors=[0, 1, 2, 4, 8, 16, 24, 32, 64] h*=64 [grid top (64, CHOSEN), on a measured tie of every finite head]
    W={0: 1.0, 1: 0.996, 2: 1.005, 4: 1.006, 8: 1.007, 16: 1.008, 24: 1.009, 32: 1.008, 64: 1.007}
(v) I wins at k=60, ties elsewhere: E=[64] dominated=[] survivors=[64] h*=64 [grid top (64, CHOSEN): every shorter finite head measured slower beyond f]
    W={0: 1.08, 1: 1.08, 2: 1.08, 4: 1.08, 8: 1.08, 16: 1.08, 24: 1.08, 32: 1.08, 64: 1.0}
(vi) near-equal chain: E=[1, 2] dominated=[] survivors=[1, 2] h*=2 [MEASURED]
    W={0: 0.94, 1: 0.92, 2: 0.9, 4: 1.12, 8: 1.12, 16: 1.12, 24: 1.12, 32: 1.12, 64: 1.0}
(vii) base: E=[8] dominated=[] survivors=[8] h*=8 [MEASURED]
    W={0: 0.917, 8: 0.9}
(vii) + losing h=4: E=[8] dominated=[] survivors=[8] h*=8 [MEASURED]
    W={0: 0.917, 4: 1.667, 8: 0.9}
(viii) (ii) with 64 failing G2: E=[24, 32] dominated=[] survivors=[24, 32] h*=32 [MEASURED]
    W={0: 1.1, 1: 1.1, 2: 1.1, 4: 1.1, 8: 1.1, 16: 1.1, 24: 1.0, 32: 1.0}
(viii) every h failing G2: every finite h removed by R0 -> no form ships (plan A fallback)
R3-1 H(8)/H(32): E=[8, 16, 24, 32, 64] dominated=[16, 24, 64] survivors=[8, 32] h*=32 [MEASURED]
    W={0: 1.3, 1: 1.2, 2: 1.1, 4: 1.05, 8: 1.0, 16: 1.0, 24: 1.0, 32: 1.0, 64: 1.0}
R3-2 base: E=[8, 16] dominated=[] survivors=[8, 16] h*=16 [MEASURED]
    W={8: 0.97, 16: 0.99, 24: 1.0, 32: 1.0, 64: 1.0}
R3-2 + h=4 at 0.95 (new minimum): E=[4, 8] dominated=[] survivors=[4, 8] h*=8 [MEASURED]
    W={4: 0.95, 8: 0.97, 16: 0.99, 24: 1.0, 32: 1.0, 64: 1.0}
R3-2 + h=4 at 0.985 (in E, not the minimum): E=[4, 8, 16] dominated=[] survivors=[4, 8, 16] h*=16 [MEASURED]
    W={4: 0.985, 8: 0.97, 16: 0.99, 24: 1.0, 32: 1.0, 64: 1.0}
R3-2b base (two cells): E=[8, 16] dominated=[] survivors=[8, 16] h*=16 [MEASURED]
    W={8: 0.97, 16: 0.99, 24: 1.0, 32: 1.0, 64: 1.0}
R3-2b + h=12 (W 0.985, not the minimum, dominates 16): E=[8, 12, 16] dominated=[16] survivors=[8, 12] h*=12 [MEASURED]
    W={8: 0.97, 12: 0.985, 16: 0.99, 24: 1.0, 32: 1.0, 64: 1.0}
(ix) dominance cycle 8>32>16>8: E=[8, 16, 32, 64] dominated=[8, 16, 32, 64] survivors=[8, 16, 32] h*=32 [MEASURED; dominance CYCLE: kept those dominated by the fewest (1)]
    W={8: 1.02, 16: 1.0, 32: 1.0, 64: 1.0}
cycle search (200k random 3-head, 3-cell cases): EMPTY SURVIVOR SET FOUND {8: [0.95, 1.02, 0.99], 16: [0.97, 0.99, 1.0], 32: [0.99, 1.0, 0.97]}
```

Reading. (i), (iv): h\* = 64, CHOSEN, on a tie of every finite head. (ii): 64, CHOSEN, on a tie
of {24, 32, 64}. (iii): 0. (v): 64, CHOSEN, every shorter head slower. (vi): 2. (vii): 8 both
times. (viii): 32 with H(64) failing G2; no form when every head fails. R3-1 drill: 32 (rev 3:
64). R3-2 (x): 16, then 8 once a new minimum is added, then 16 for a non-minimum value. R3-2
(xi): 16, then 12 by dominance. (ix): a cycle; kept {8, 16, 32}, h\* = 32. The cycle search's
last line names the random case that drill (ix) fixes.

## STATE AT HANDOFF

- STATE: done. Branch `lane/memfn-r45`; the reply is at rev 4, and the review r23 file and
  index are committed.
- RULINGS: `docs/dev/lanes/r45d_rulings.md` was empty when the lane started and when it handed
  off. Last entry applied: none.
- For the kit manager: rule the dominance-cycle clause (§3 R1 step 3). Confirm with main the
  R3-6 refinement to night-order step 3 (width cells on the rebuilt binary after the identity
  check).
- OWED: none.
