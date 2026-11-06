# Soundness lens (SND), round altnf2: alt_normal_form.md rev 1 @ f7fd1a759

Read-only. About 75 single-pattern compiles in total (p1.tsv 50 pairs, p2.tsv 9 pairs, plus about 15 `--emit-facts`/`--emit-main` probes).
Evidence in this directory: `pair.py` (orig vs rewritten, each through libpcre2-8 10.46 AND pcrec), `p1.tsv/.out`, `p2.tsv/.out`.

## Findings

### SND-1: the §3.2 adjacency test, as written, passes an intervening branch that holds `\K` or a capture, and an answer moves (CONFIRMED, answer)

§3.2 says "Capture-free branches of EQUAL width always pass (same span, nothing observable differs)", and its general clause is about STRINGS only ("no string of m is a proper prefix or a proper extension of a string of i or of j"). Both readings let j move past an equal-width m that has a side effect:
- `\K` (capture-free, equal width, so the shortcut says "always pass"): `(?:ab|a\Kd|ad)` on `ad`: libpcre2 and pcrec give (1,2). The merge the test allows, `(?:a[bd]|a\Kd)`, gives (0,2) in both. The overall match moves.
- A capture in m (the string clause passes: m = {ad}, which is neither a proper prefix nor a proper extension of `ab`/`ad`): `(?:ab|(a)d|ad)` on `ad`: group 1 is (0,1) in the original and unset after the merge. With a back-reference, `(?:ab|(a)d|ad)\1?` on `ada`, the overall match goes from (0,3) to (0,2), in pcrec as well as libpcre2 (p1.out rows 1-3).
- Control rows that held: an m with a lookahead, an atomic group, or `^` (p1.out rows 4-6).

The "nothing observable differs" argument holds only when m has no side effect. The fix is in the text and costs little. "Decidable" should mean "has an EXACT §3.5 description spanning the whole branch", which already leaves out captures and treats ZERO kinds (`\K`, assertions) as cuts. The equal-width shortcut should become "equal width AND such a description". Then say that an m whose language meets i's or j's at equal width must be free of captures and `\K`. Today altcls never moves a branch past another (stage 1 merges ADJACENT bare classes only), so this hazard is new with the owner's non-adjacent merge (stage 2b).
Effort: a few lines in §3.2/§6 row 1, plus one sabotage witness: `(?:ab|a\Kd|ad)`/`ad`, (1,2) expected, measured. Blast radius: stage 2b (stage 1 is safe because boxes have no side effects). Note §3.2, §6 row (1), §8a C2.

### SND-2: stage 1's island set-edge reading does not keep "today's word list". It adds islands wherever a lowered box holds a byte RANGE (CONFIRMED, speed/size + a gate that goes red on a correct build)

§5 stage 1 / §8a C3 say `vm_isl_words` reads "a set position INSIDE an `A_WCLASS` as its members ... so the island's word list is today's word list". Today `vm_isl_single` (`emit_vm.c:4011`) declines any A_CLASS with more than one member. `u8_box` already emits multi-member RANGE positions inside `A_WCLASS` whenever code points are contiguous, so these islands are declined today:
- `x(?:[éà]1|q2|r3)y -e utf8 --engine=vm -fno-cls-kit`: `RX_VM_ALT_ISLANDS 1` (two singleton boxes `c3 a0 | c3 a9`).
- `x(?:[éè]1|q2|r3)y` and `x(?:[éê]1|q2|r3)y`: `RX_VM_ALT_ISLANDS 0` (one box `c3 [a8-a9]`, a range).
The reading as written cannot tell a range made by the merge from a range made by `u8_box`. So every utf8 alternation whose wide class has a contiguous pair (`[а-я]`, `[éè]`, most `\p` sub-ranges) gains an island at stage 1. Those are VM speed/size movers that are not in the predicted-mover list, and Gate U4's "`RX_VM_ALT_ISLANDS` equal base vs stage" goes red on a correct build. The answers are safe: the members are disjoint and of equal width (S-i still fails its sabotage).
Fix: (a) mark the positions the merge created and read only those (that is a parallel spelling of "a position"), or better (b) accept the reading in general, list the new islands as predicted movers (U1-style, from the box model), and turn U4 from "equal" into "base ∪ predicted". Effort: text plus a predictor column. Blast radius: VM utf8 only. Note §5 stage 1 Change/U4, §8a C3, §2.3 ledger row "the island's set-edge reading".

### SND-3: S-e cannot fail at the bound stage 3 lands with, and a bound-2 witness exists (CONFIRMED, test-coverage)

Stage 3 "keeps 2 as its starting value" (§4.4), and S-e is "a bound-3 witness, stated". So the stage lands with its hull/set-member-drop sabotage unwitnessed. A bound-2 witness exists among the 249 two-member equal-width fold pairs that differ at one byte by a non-cube xor (CaseFolding 16.0.0). Example: `(?i)xyzłw` (Ł/ł = `c5 81`/`c5 82`, one box `c5 [81-82]`, xor 0x03, so it is outside the cube domain today). Today `req_whole_run 58595ac5/dfdfdfff` (measured). Stage 3 at bound 2: `[xX][yY][zZ] c5 {81,82} [wW]` = 43 bits. With the 82 member dropped it is 44 bits and the sabotaged pre-check rejects `xyzłw` (expected (0,6), measured in libpcre2 and pcrec, p2.out). The bits are computed, not built. Effort: one row. Note §5 stage 3 S-e.

### SND-4: "suffix factoring holds for any A, B, C" needs "C the same node, capture indices included" (CONFIRMED as a hazard of the text, doc)

Right distributivity is sound (p1.out: `\K` in A, back-references into A/B, variable-width C, all SAME). But "any C" invites structural equality that ignores group numbers. `(?:a(x)|b(x))` → `(?:a|b)(x)` on `bx` moves group 2 (1,2) to group 1. With `\2` the rewritten pattern does not compile (libpcre2 ERR115, pcrec "refers to capture group 2"). pcrec refuses branch reset, so a capturing C is never legitimately shared. Text: "C identical as a node, including every capture index (so in pcrec a shared C is capture-free)". Note §3.2, §6 row (3).

### SND-5: the owner's rule table does not say lookaround bodies stay out of reach; prefix factoring in a lookbehind turns an accepted pattern into one pcrec refuses (SUSPECTED for the build, CONFIRMED for the shape; maintenance)

Today altcls treats `A_LOOK` as a leaf. Its comment (`altcls.c:443-455`) calls walking the body "sound" and only declines it because the win is unmeasured. The note's owner "over every alternation spine it walks today" inherits the leaf, but the note never says so. The rewrite is NOT neutral there. `(?<=ab|a)x`, `(?<=xab|xc)y` and `(?<=aab|a(b))x` all compile in pcrec today and agree with libpcre2. Their prefix-factored forms `(?<=a(?:b|))x`, `(?<=x(?:ab|c))y` and `(?<=a(?:ab|(b)))x` are refused ("variable-length lookbehind is not implemented"); libpcre2 accepts both forms and answers the same (p1.out lookbehind rows). If the owner ran after the per-branch width check, the result would be a variable-width lookbehind branch reaching the back end (SUSPECTED; not built). Text: §3.3/§6 should state that the owner does not enter lookaround bodies until [VLOOKBEHIND] lands, or that prefix factoring inside a lookbehind requires equal-width rests. Equal-width merges (stage 1 inside `(?<=[aé])`) are unaffected.

## PROBED-AND-HELD

- §3.2 prefix factoring on a fixed-width capture-free key, rests arbitrary: 26 pairs SAME in libpcre2 and pcrec. Covered: an empty key-branch in its slot (`a(?:b||d|)`), nested rests, rests holding captures, recursion `(?1)` into a rewritten group (`(ab|a|ad)x(?1)`, `^(ab|a|ad)(?1)$`), atomic/possessive/lazy wrappers, `\K` in the key and in the rests, a key with two same-span ways (`(?:a|a)`, `(?:a\K|a)`, `(?:a|a\K)`: order of the K-ways is kept), a back-reference key (also caseless Kelvin, utf8), inline `(?i)` spreading across branches, and utf8 caseless code-point keys (`(?i)k(?:b||d)` on Kelvin `d`). The width-grouped merge across `k` moves (0,3)→(0,4), as the adjacency test predicts.
- §3.2 completeness ("two matches at one start differ only by one being a prefix of the other"): holds for strings; the only gaps are the side effects in SND-1. Equal-width m with a lookahead, an atomic group or `^`: SAME (3 rows).
- Suffix factoring with C capture-free: 4 rows SAME (`\K` in A, back-references to groups in A/B, variable-width shared C).
- The adjacency test against an EMPTY between: blocks every merge across it (`(?:b||d)`), as premise.out showed. Rule order (2)→(3)→(4) on `(?:ab|b|cb)`: right-distributive, no move.
- Out of scope, refused today: branch reset (would also need group-index care: `(?|a(?:(x)|(y)))` moves groups vs `a(?|(x)|(y))`), conditionals, `\C`, `\R`, `\X`.
- §3.4 / §3.5 piece set as a FACT: L(X(G2|G3)Y) = L(XG2Y) ∪ L(XG3Y) is a language identity; per-width hulls are supersets, and CAT across ZERO kinds cuts. No match outside every piece was found or is constructible: the order of preference does not touch the set of matched strings (C1).
- §5 stage 1 C3 answer side: set edges read as members are disjoint singletons of equal width. The island's answer is unchanged (only its COUNT moves, SND-2). The word order for a last-first merge is the X-major order of the merged product (β: `ce92, ceb2, cf90`, the same as today).
- Sabotage witnesses:
  - S-a (`[ce cf][92 b2 90]` matches `ce 90`, libpcre2 (0,2) against NOMATCH): CAN FAIL.
  - S-b (truncating `[4b 6b e2]`: Kelvin (0,1) against (0,3), and `e2 84` (0,1) against NOMATCH): CAN FAIL.
  - S-i (sabotaged island lacks `é`; the island count is 1 in both builds): CAN FAIL.
  - S-d and S-k (premise.out, re-read; S-d still fails if the owner prefix-factors first, since `a(?:[bd]|)` gives (0,2)): CAN FAIL.
  - S-c: today `RX_REQ_RUN 78796162@0`, `RX_DFA_PREFILTER run-pinned` at offsets 0..3. The tree reaching req.c is altcls's `xyab(?:|c)zw`, so the sabotage lands on `(?:|c)`, and either wrong width still yields `xyabzw`/`xyabczw`. PLAUSIBLE (the sabotage was not built).
  - S-g: `(ab)x\1y` VM, `RX_REQ_RUN 616278@2` emitted; A_BREF is TEXT `ANY` in `kindrow.def:70`, so the "UNIT widened to ANY" sabotage reaches it. PLAUSIBLE (not built).
  - S-f: today's run 21 bits measured. Sabotaged `{4b,6b}` is in bound at 2 and at 3. CAN FAIL at either bound.
  - S-e: SND-3.
  - S-p: a fact witness, inert as stated.
  - K123: unaffected (merges are equal width only).

END OF FINDINGS
