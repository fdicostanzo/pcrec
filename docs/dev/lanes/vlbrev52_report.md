# vlbrev52 report: `docs/design/vlookbehind.md` rev 5.2 (stage 2), readiness review r6 vlb4 applied

Lane vlbrev52 (opus), 2026-11-10. Branch `lane/vlbrev52`, cut from `lane/vlbrev51` (rev 5.1,
`53c9c9561`). DESIGN TEXT ONLY: no `src/`, `tests/`, `docs/spec/`, `plan.md` or `known_issues.md`
edits (their rows and hunks are drafted below or in the note for the manager). Input: main's
`docs/dev/reviews/2026-11-10-r6-vlb4-readiness.md` and its RULINGS (RDY-1: first fault in written
order; RDY-3: lookbehinds nested in lookaheads are followed, the HEAD call twin is a K-row whose fix
rides V1; the other items as proposed).

Evidence: `docs/dev/lanes/vlbrev52_evidence/` (listed in the note's §15).
- Every libpcre2 claim rev 5.2 adds was run against libpcre2 10.46 with the refusal offset
  (`ora2.py`, `cells52_*.out`).
- pcrec claims were run on a `build/pcrec` copied from the main tree (built 06:59 2026-11-10;
  main's only later `src/` change, `e813451b6` sartie, does not touch lookbehind code). Single
  compiles only; a full suite held the box.
- libpcre2's check order was READ by one pcre2-reader (D181). Its note passes
  `scripts/check_pcre2_note.sh` (rc 0). **For the manager:** commit
  `/var/tmp/pcrec-pcrec/scratch/pcre2notes/lookbehind_check_order.md` as
  `docs/dev/pcre2_notes/lookbehind_check_order.md`; the note cites it by that slug.

## STATE AT HANDOFF

**Done, committed on `lane/vlbrev52`:**
- `docs/design/vlookbehind.md` rev 5.2:
  - the status line, a "REVISION 5.2 (readiness r6 vlb4, ruled) — read first" block, and rev
    5.1's G7/G10 bullets marked superseded;
  - §0 G1 (RDY-3's class and the K-row twin; the PCRE2 DEFINE bug) and G2 (DC-7);
  - §6.2.1-§6.2.9 edited in place, marked `[vlb4 RDY-n]` / `[vlb4 DC-n]`;
  - §9 (the re-cut), §11 (the standing questions at rev 5.2), §15 (rev 5.2's evidence) and the new
    §16g.
- `docs/design/vlb_d27_extract.md`: RE-CUT from rev 5.2 (RDY-9).
- `docs/design/CLAUDE.md`: the entry says "stage 2 rev 5.2".
- `docs/dev/lanes/vlbrev52_evidence/`, the critic's `diffcheck.md` included.
- Checks: `make test-plan-lint` rc 0 (2 passed, 0 failed); `make test-doc-lint` rc 0 (7 passed,
  0 failed). Both were run after the last design commit. Logs:
  `/var/tmp/pcrec-pcrec/scratch/vlbrev52/planlint2.log` and `doclint2.log`.
- No rulings file was named in the brief, and none exists in the worktree.

**Per RDY item (where it is fixed):**
- **RDY-1 (ruled):** post-order is withdrawn. §6.2.2 "Which lookbehind is reported" states
  libpcre2's order, measured and read, with the counter-cells. "The judging walk" (steps 1-6)
  then specifies one walk in written order:
  - met lookbehinds are judged where they are met;
  - a path of groups entered by reference or call;
  - the innermost lookbehind is blamed;
  - per-branch running sums;
  - the walk runs at both timings (the parse hook judges at the outermost close);
  - order 3 is defined by the walk.

  The walk decides WHICH lookbehind is reported and the table decides WHY. The rows sit in §6.2.5,
  the pins in gate 7, and SV16, SV18 and SV19 in §6.2.7. V1/V3 carry it.
- **RDY-2:** the clamp moves to `PCREC_W_UNBOUNDED − 1`, in the lookbehind entries, for
  `lo`/`hi`/`hs` (§6.2.1, §6.2.3, V2). The ceiling sentence prints the true figure, and "more than
  65535" at the clamp. Stage 1's 2^48 cell moves to the ceiling sentence. Gate 7 pins both figures,
  and SV15 gains the 65536 plant.
- **RDY-3 (ruled):** the edge walk meets lookbehinds inside lookaheads. It searches a DEFINE that
  sits inside the lookahead, and it never follows a lookahead's own references or calls (§6.2.1,
  §6.2.2). The table has the cells and controls (§6.2.5). Gate 3 EXTRA, gate 7, SV17, the
  ¶5a/¶5c hunks and the extract carry it too. The K-row is drafted below.
- **RDY-4:** S172 is listed (§6.2.7). Its anchor STAYS under the ruled order, and its header gains
  the in-walk clause.
- **RDY-5:** order 4 tests `hs` first, which is a stated change from HEAD's nesting (§6.2.2). The
  within-branch cells go on the one K-row.
- **RDY-6:** rxt_compose.c's injection sets the mark (§6.2.1; V2 readers).
- **RDY-7:** the obstacle is `cx->job`, and the route is `compile_driver`'s front half (§6.2.4). The
  extract carries the cli.md hunk.
- **RDY-8:** row t IS target t, and `cg_index` is used only for `struct CallGraph`'s own arrays.
  Per-round publishing is kept, and the row sets are stated (§6.2.1, V1).
- **RDY-9:** the extract is re-cut. It states the written-order rule, the two-lookbehind exception,
  the lookahead cells, ¶5a's text, the clamp's 2^40 cell, the PCRE2 DEFINE divergence and the
  cli.md hunk.
- **RDY-10:** ¶5a is re-worded to the re-entry fact, with RDY-3's clause (§6.2.8).
- **RDY-11:** `pcre2only=4`, covering every latent-accept row (DC-4 corrected my 3). SV9's second
  witness is dropped.

**Found by this lane (beyond the review):**
- libpcre2 10.46 never measures a lookbehind inside a `(?(DEFINE)...)` inside another lookbehind.
  So it accepts `(?<=a(?(DEFINE)(?<=b+)))x`, and through a call it matches `axb` WRONGLY at
  [1-2) (`cells52_definelb.out`). pcrec refuses both at HEAD and keeps refusing them. This is
  stated in §0 G1, with a §9¶2a hunk and a declared gate-3 class. An upstream issue is drafted
  below.
- Rev 5.1's region-based re-entry closure would have refused `((?<=\2))(a(?(DEFINE)(?<=\1)))`,
  which libpcre2 ACCEPTS. Order 3 is therefore defined by the judging walk (§6.2.2 step 3).

**The critic (TASK 2):** one opus critic, read-only and blinded to this report, ran the diff check.
Its file is `/var/tmp/pcrec-pcrec/scratch/vlbrev52/diffcheck.md`, with a copy in the evidence
directory.
- **Its verdicts on rev 5.2 as first committed (`da5e3a3a3`):**
  - V1 READY WITH TEXT FIXES (DC-9, DC-7);
  - V2 READY WITH TEXT FIXES (DC-1);
  - V3 READY WITH TEXT FIXES (DC-2, DC-3, DC-5, DC-8);
  - V4 READY;
  - V5 READY WITH TEXT FIXES (DC-4);
  - V6 READY WITH TEXT FIXES (DC-4, DC-6, DC-2's cell);
  - V7 READY WITH TEXT FIXES (DC-2's sentence).
- **Design-level problems: none.**
- It traced every pinned RDY-1/RDY-3 cell, the re-entry rows, the accept rows, the DEFINE rows and
  the duplicate-name rows by hand. Each matches libpcre2's offset.

**What I changed after it (one round, all applied, commit `a1488f59d`):**
- DC-1 (MEDIUM): the clamp moves from "under the lexical flag" to the lookbehind entries, for
  `lo`/`hi`/`hs`. Under the lexical flag alone, `hi` stayed saturated, and rule 0's false sentence
  would have printed. This adds a §6.2.3 bullet and changes V2.
- DC-2 (MEDIUM): running sums are per branch at every level. A group adds its maximum when it is
  complete. Four libpcre2 cells in a §6.2.5 row and gate 7, plus the extract's sentence.
- DC-3: step 5's hold widens G5's class to cells that agree at HEAD (`(a)(?<=\1(?<=c+))x\2`). The
  widening is stated, pinned with pcrec's predicted answer and put on the K-row. It is the price
  of the ruling: holding the nested refusal is what gives `(a)(?<=b+(?<=\1+))x` @3.
- DC-4: `pcre2only=4` (the `(*ACCEPT)` row is a latent ACCEPT), and the PCRE2-bug cells are a third
  declared class.
- DC-5: at parse, lookbehinds the walk did not meet are judged after it (`(?<=a(?(DEFINE)(?<=b+))c+)x`
  @0, one more stage-1 offset move).
- DC-6: SV17's second witness compiles.
- DC-7: G2 and gate 2 gain the lookahead-nested call cycle as a refusal-only exception.
- DC-8: the stop mapping is completed. A match-time-length item stops the running-sum check, and
  rule 0 waits for the branches.
- DC-9: there is one walk. Its home is mod_lookaround.c (V3), which calls it with no table at
  parse and with V1's table at postresolve. `pcrec_callgraph_lookbehind_recurses` retires (V1),
  and S1454 re-anchors to the walk's call.

Rechecked after the fixes: `make test-plan-lint` and `make test-doc-lint` are green (above). No
second critic round, per the brief.

**Validation owed:** none for this lane, which is design text only. The build lane owes gate 7's
pinned answers. Every post-stage-2 pcrec offset in rev 5.2 is PREDICTED by hand-tracing the walk
(§15), not measured.

**For the manager:**
1. Commit the pcre2-reader note (above).
2. File the K-rows below. One is new (K143). One MERGES K141 and K142 (drafted by vlbrev51, not
   yet on main) as the critic and the review recommended. Keep or merge as you prefer; the note
   says "one K-row".
3. Decide whether to send the upstream PCRE2 issue below (outward-facing: your call).
4. An unlock, not scheduled: the walk carries each stop's kind. So the one K-row's REASON half
   (G17/RDY-5) becomes "print the stop's kind instead of the table's first row" once someone
   wants it.

## Drafted: known_issues row (RDY-3's HEAD call twin; next number after the pending K140-K142 → K143)

```
## K143 — OPEN (found by review 2026-11-10 r6 vlb4 RDY-3; drafted by lane vlbrev52; fix rides [VLOOKBEHIND] stage 2 V1) — a call cycle through a lookbehind nested in a LOOKAHEAD compiles; libpcre2 refuses it, and the matcher gives up

**Witness:** `((?=(?<=(?2))))(a(?=(?<=(?1))))`: libpcre2 10.46 REJECT 125 @4. pcrec at main d600e06fc COMPILES it (K127's length walk, `cg_length_calls`, returns at every lookaround, so it never meets the lookbehind inside the lookahead). The `--emit-main` matcher (gcc -O1) answers no match on `a` and `ba`, and GIVES UP (`frames`, rc 3) on `aa` and `aaa`: the call cycle at match time stops at the frame budget. Offset twin: `((?<=(?2)))(a(?=(?<=(?1))))` is libpcre2 @1, pcrec @16. docs/dev/lanes/vlbrev52_evidence/k_calltwin_run.out, cells52_rdy3.out. Accept-set tier (G1). **Fix:** [VLOOKBEHIND] stage 2's judging walk meets lookbehinds nested in lookaheads (vlookbehind.md §6.2.1, §6.2.2); gate 7 pins both cells, SV17 plants the descent.
```

## Drafted: ONE known_issues row for "which fault is reported" (merges vlbrev51's K141 and K142)

```
## K141 — OPEN (found by reviews 2026-11-10 r5 vlb3 G5/G17 and r6 vlb4 RDY-5 + diff check DC-3; drafted by lanes vlbrev51, vlbrev52) — pcrec can report a different fault than libpcre2's first in written order: a deferred lookbehind refusal loses to diagnostics raised before postresolve, and within one lookbehind the reason follows pcrec's rule-table order

**Witnesses (D26 tier 2: which error, which offset or which sentence; no answer moves):**
- Before postresolve (calls today; every reference-bearing lookbehind after [VLOOKBEHIND] stage 2): `(a)(?<=(?1)|b+)(?<=c+)x` refuses @15 (libpcre2 125 @3); `(a)(?<=(?1)|b+)x\2` gives the `\2` resolution error (libpcre2 125 @3); `(a)(?<=(?1)|b+(?C1))x` gives the callout sentence (libpcre2 125 @3); under `--engine=dfa`, the VM-only refusal. After stage 2 also `(?<=b+\1)(c(?<=d+))x` (libpcre2 @0, pcrec @11) and, through stage 2's hold of a nested refusal (vlookbehind.md §6.2.2 step 6), cells that agree at HEAD: `(a)(?<=\1(?<=c+))x\2`, `(a)(?<=(?1)(?<=c+))x\2` (libpcre2 125 @9, @11), `(a)(?<=\1(?<=c+)(?C1))x`, `(a)(?<=\1|(?<=c+))x\3`.
- The reason within one lookbehind: `(?<=(?:b{60000}){2}|c+)x` (libpcre2 187 @0; pcrec the unbounded sentence: last-written-first branch loop); `(?<=(?:a{40000}){2}(?:a+){0})y` (libpcre2 187 @0; pcrec "unbounded" after stage 2: order 4 before order 6).
- Evidence: docs/dev/lanes/vlbrev51_evidence/pcrec_head51_misc.out, cells51b.out; vlbrev52_evidence/cells52_order.out, the critic's probes in diffcheck.md.

**Fix (not scheduled):** (a) record the first parse-time fault's offset and let postresolve's refusal win when its lookbehind comes first in written order; (b) print the judging walk's stop kind instead of the rule table's first row (stage 2's walk carries it). Each is a reject-table byte move (the manager's call). WHICH lookbehind is reported among deferred lookbehinds is NOT on this row: stage 2's judging walk follows libpcre2's order (review r6 vlb4 RDY-1, ruled).
```

(If K141/K142 are already filed separately, append the RDY-5 cell to K142 and the DC-3 cells to
K141 instead.)

## Drafted: upstream PCRE2 issue (outward-facing; the manager or Frank decides whether to send)

```
Title: lookbehind inside (?(DEFINE)...) inside another lookbehind is never length-checked; a call to it matches wrongly

PCRE2 10.46 (also checked: nothing newer here). A lookbehind written inside a (?(DEFINE)...) group that is itself inside another lookbehind is never checked for a fixed or bounded length:

  /(?<=a(?(DEFINE)(?<=b+)))x/        compiles (max lookbehind 1); expected: error 125 (as /(?(DEFINE)(?<=b+))x/ gives)
  /(?<=a(?(DEFINE)(?<g>(?<=b+))))x(?&g)/   compiles, and matches "axb" at offset 1, length 1 -- but at offset 2 the preceding character is "x", so (?<=b+) should fail

Compare: /(?<=a(?=(?(DEFINE)(?<=b+))))x/ correctly gives error 125 at offset 18, and /(?<=a)x(?<=b+)/ gives 125.
It looks as if the lookbehind length check skips DEFINE groups while measuring the outer lookbehind's branches, and the top-level scan then skips over the whole outer lookbehind, so the inner one is never visited.
```

(The last sentence is a behavioural inference; it names no source location, per D181.)

## Drafted: spec hunks

They are in the note (§6.2.8, the V4 unit): ¶5a re-worded (RDY-10, RDY-3); ¶5c's re-entry bullet
gains the lookahead clause; and §9¶2a gains the refuse-side DEFINE clause. The last one states
behaviour HEAD already has, not stage 2's.

## The invariant behind §6.2.2 step 3 (sketch)

A walk stops on a fault of L only in these cases:
- (a) an item with `hs` unbounded: order 4 holds, because L's branch `hs` is unbounded;
- (b) a finite running `hi` passing 65535: that branch's `hi` exceeds 65535, so order 6 holds, or
  order 8 if a later match-time item makes `hi` unbounded with `hs` finite;
- (c) a duplicate-name reference on L's width path: order 1 holds;
- (d) a reference or call whose target encloses the item, or is on the path.

Case (d) splits further:
- **The target encloses the item.** Either the item lies lexically in L, so the target contains L
  (order 3) or lies inside L as a self-referencing group, whose `hs` saturates (order 4). Or the
  item lies in a reached body with no lookbehind in between, which is a self-cycle of that group:
  `hs` saturates, order 4.
- **The target g is on the path.** g was entered earlier, and the walk reached the item from g's
  body. If g was entered by L's own walk with no lookbehind in between, the groups form a width
  cycle: `hs` saturates, order 4. If g was entered by a lower walk J, then L was met inside the
  region of some group h entered after g, or of g itself. If it was g, g contains L, so order 3.
  Otherwise L reaches g, g reaches h, and h contains L, so order 3 holds again.

So every stop maps to a refusing row, and the build asserts it. Conversely, a lookbehind no walk
stops on passes every row except a closure-based order 3. That is why order 3 is defined by the
walk (`((?<=\2))(a(?(DEFINE)(?<=\1)))`, libpcre2 ACCEPT).

Skipping a lookbehind already judged is safe for the same reason. Re-walking one that passed
could stop only on a cycle through its own body, and its own walk would have met that cycle
first.
