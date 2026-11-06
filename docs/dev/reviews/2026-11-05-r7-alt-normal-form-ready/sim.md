# crit-sim findings (lens: simulate THE PROCEDURE, §3.2/§3.3 of subject rev 2)

Method: implemented §3.2 adjacency test + §3.3 rounds M->P->S from the text only (`sim/proc.py`; python -I),
checked against a python `re` leftmost-first oracle (spans AND named captures), THEN read `altnf_proc.py`
and diffed. Scripts: proc.py cells.py conf.py conf2.py exact.py term.py u8.py fold.py never.py cost.py
cost2.py extra.py diffthem.py. UCD: python unicodedata 16.0.0 == third_party/ucd-16.0.0 (checked).

## Findings

### SIM-1 (design, low, unit 1/2b/cross): a zero-difference duplicate is only absorbed when it REACHES its head; the unreachable copy is dead code and survives (and pollutes P/S)
- §3.3 step M (l.320-322) absorbs a member identical to a head only through the fold walk, i.e. only if
  the §3.2 test passes against every branch between. But a copy of an identical, effect-free earlier branch
  can never be selected whatever lies between (the earlier copy matches the same span with the same
  continuation first); nothing moves, so no adjacency test is needed.
- CONFIRMED: `bba|bb|bba|bb` -> M: unchanged (4 branches); MPS: `bb(?:a||a|)` (duplicate `a` arm and TWO
  EMPTY arms in the output). `aaa|aa|aaa` MPS -> `aa(?:a||a)`. Random grid (alphabet abc, width 0-3, 2-4
  branches +1 inserted dup): 1335/6000 lists end different from the list without the dup (M only),
  1318/6000 under MPS. Dropping every branch identical to an earlier one is oracle-exact on 3000 lists
  (340 had a duplicate; 0 inexact).
- Effort small (one pre-pass or a rule row "identical to an earlier branch: drop"), blast radius: altcls
  output size (stage 2b) only; stage 1 boxes are disjoint so it never fires there.

### SIM-2 (design/size, low-medium, unit 2b): P and S see only CONSECUTIVE branches, so an unrelated branch that PASSES the adjacency test still blocks factoring that M would do across it
- §3.2 l.201-202 ("factoring ... reorder nothing") + §3.3 steps P/S (l.324-333). Sibling merge moves a
  branch past any `m` the test passes; factoring does not, though the same test would make the move safe.
- CONFIRMED: `frank|xyz|fred` -> unchanged under {M,P,S} (while `frank|fred` -> `fr(?:ank|ed)`).
  Never-picked drill: inserting one branch of fresh letters (`zz`/`zzz`, cannot merge, passes row 1
  against everything) into a random list of 2-4 branches changes how the OTHERS end under {M,P,S} in
  1286/6000 (`zz`) and 1330/6000 (`zzz`) lists (e.g. `bab|bab|zzz|abb` -> `bab|zzz|abb`, vs `(?:ba|ab)b`
  without `zzz`). Under {M} alone the same insert changes nothing (0/6000 at width 2 and 3; width 1 merges
  with other width-1 branches, not a never-picked branch). So "adding a never-picked branch does not change
  how the others merge" HOLDS for M and FAILS for P/S, exactly at the P/S-vs-M asymmetry. If intended,
  state it (the user's keyword list `foo|<odd one>|foobar` loses its trie); if not, P/S need the same test.

### SIM-3 (speed, low-medium, unit 1/2b): the O(1)-per-fold cost bound (§3.3 l.358-367) covers only same-width writer-free spans; mixed-width word lists stay quadratic
- The prefix count is over branches that are NOT "width-w, WRITES-free". A mixed-length keyword list (the
  common user shape) has a foreign-width branch in nearly every span, so every attempted fold pays
  O(span*w), although row 1 would pass nearly all of them.
- CONFIRMED (my implementation, adjacency calls = the naive cost): single width 6^4=1296 shuffled words:
  102,682 calls (the text's "205k" is not reproduced; O(1) path would make it ~0). Random mixed-width words
  (alphabet 10, widths 3-7) n=200/400/800/1600: calls = 1,294 / 4,937 / 36,857 / 209,112, calls per
  branch 6 / 12 / 46 / 131: quadratic. Also "computed once per round" (l.361) is stale inside a sweep:
  each fold deletes a branch and shifts slots (and there are w*sweeps (w,p) passes per round); the build
  needs a tombstone-conservative count or a Fenwick tree, not stated. Hostile-pattern budget (D-limits)
  for a large alternation is not stated.

### SIM-4 (doc, low): §3.3's quoted outputs mix M-only and full-procedure results
- `ab|abc|ad` -> `a[bd]|abc`, `aaa|ab|aab` -> `aa[ab]|ab`, `ab|a|ad` "unchanged" are the M-only results
  (l.348-350). Under the 2b rule set {M,P,S} they continue: `a(?:[bd]|bc)`, `a(?:a[ab]|b)`, `a(?:b||d)`
  (the last is what §3.2 l.268-269 itself says). All exact (oracle). `aab|bbb|bab` is quoted through S
  correctly (`(?:aa|b[ab])b`). Say which rule set each arrow is.

### SIM-5 (doc, low): width-0 branches
- Step M loops `p` from `w-1` down to 0, which is empty for w=0, so a zero-width duplicate (`(?:|)`, or two
  EMPTY arms a P rests list can hold, SIM-1) is never absorbed; the termination argument (l.340-342
  "every rule strictly lowers the number of position occurrences") is vacuous there. No counterexample to
  termination: 54,225 lists (2-4 branches, widths 0-3, alphabet 2) all terminate and none grows
  `count_pos` (term.py).

### SIM-6 (doc, low): the confluence sentence is true of COUNTS only, and \p{Nd}'s pin is not the best order
- l.407-409/§5 Gate U1b: "Fold classes are confluent under every order." Over the 1454 fold classes
  (CaseFolding C+S) the box COUNT never depends on order (0/1454), but the FORM does for one class
  {U+0395,U+03B5,U+03F5}: `CE[95 B5]|CF B5` (declared) vs `CE 95|[CE CF] B5` (first-first), same count 2.
  Emitted bytes differ per order, so the declared order must be the pinned one (it is).
- `\p{Nd}` 71 -> 39 is not minimal: 38 under 5 of the 24 position orders (e.g. 1,2,3,0). Text says "best
  of the 24" only for `\p{Lu}` (true there, 67); fine, but `\p{Nd}`'s 39 is a worse-than-possible pin.

### SIM-7 (doc, low): P and S are under-specified at two points
- S: "maximal runs of ADJACENT branches ending in an identical node sequence C": the text does not say C is
  the LONGEST common suffix of the run nor that runs are cut by equal LAST position (P says it
  explicitly, "longest run of equal leading positions"). I implemented the P-mirror; unstated.
- P/S heads/rests that are width-0 or hold a non-class item (a nested alternation from a prior round) are
  not mergeable by the "fixed-position set sequences" definition (l.310), so round 2 cannot re-merge a
  branch like `a(?:b||d)`; the re-run rule (l.334-335) re-runs P and S over those. Behaviour fine, wording
  open.

## PROBED-AND-HELD

- Every quoted §3.3 cell: `aaa|aab|aba|bba`, `aab|bbb|bab`, `ab|ab`, `ab|a|ad`, `ab|xy|ad`, `ab|abc|ad`,
  `aaa|ab|aab` and stage 2b's `abx|aby|abz` -> `ab[xyz]`, `xing|ying` -> `[xy]ing`, `xyr|zr` ->
  `(?:xy|z)r`: my implementation reproduces the stated output under the stated rule set (see SIM-4); all
  exact against python `re` (every subject <= 3-4 letters, 5-7 continuations, 0 mismatches).
- Exactness whatever the order: 8,906 (list, order, rule-set) cases over random lists of 2-5 branches
  (set-valued positions, width 0-3, capture-writer branches, all 24-ish position orders sampled, three
  head-walk rules, widths desc) with {M} and {M,P,S}: 0 mismatches (spans AND captures).
- Non-confluence is real as the text says: 15,034/24,672 width-3 lists (alphabet ab, 3-5 branches) end in
  a different form under another position order; head-walk 'latest' vs declared differs in 118/32,940
  mixed-width lists (both exact); text's partial claims about non-confluence hold.
- Gate U1b pins (box splitter written from the UTF-8 encoding rules; unmerged counts first: Lu 664, Nd 71,
  L 827, `.` 10 = the quoted unmerged counts): after step M declared order: Lu 67, Nd 39, L 330, `.` 8;
  Lu first-position-first 105; the 24 position-order counts of Lu are exactly {67,68,81,82,90,91,104,105}
  as quoted. All reproduced. (L over 24 orders: 14 distinct counts 330..375; `.`: 8 under all.)
- Fold-class population: 1454 classes, 2386 boxes -> 1894 after M, 491 classes merge; count order-independent.
- Adjacency test vs altnf_proc.py: 60,000 random lists (set-valued positions, widths 1-3, 2-6 branches):
  my M and the script's `merge` agree on every one (0 differences) after I fixed a slot-identity bug of my
  own (I located a head by cell equality, which conflated two equal `c` branches; the text says "slots").
  Row 1 / row 2 of the text are what the script's `passes()` computes; it is faithful to the text on M.
- Termination (54,225 lists) and strict decrease: no growth anywhere (see SIM-5 for w=0).

## Script comparison (altnf_proc.py, read after my implementation)
- It models step M ONLY (its header says so): no P, S, re-run, no writers (row 2's "WRITES nothing" is
  hard-coded true; no head through zero-width nodes), so the text's claim that the script recomputes the
  review's cells covers `aaa|aab|aba|bba`-class M outputs but NOT `aab|bbb|bab -> (?:aa|b[ab])b`, `(abx|aby|abz)q`,
  `xing|ying`, `xyr|zr`. Where it models the text it matches it exactly (the text matches the script on M,
  no divergence). Its oracle compares the first-match LENGTH only (not which branch), adequate for this form.
