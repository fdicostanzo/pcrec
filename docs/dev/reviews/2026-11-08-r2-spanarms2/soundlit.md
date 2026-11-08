# CRITIC soundlit: spanarms2
## Findings

### SOUNDLIT-1 (CONFIRMED; speed + doc; effort small text, blast: 7 of 17 §5.7 witnesses and 4 §5.6 movers)
**Every one-character lookaround is `A_CTX`, never `A_LOOK`, at the walk; the note's ITEM row (and T3's
E-5 "a positive lookaround") never names it, so half the witnesses have no plant site.**
`src/parse/ctxnode.c:121-149` (`pcrec_look_t3`, row `ctx-node`): a lookaround whose body language is a
set of single, byte-expressible characters is built as `A_CTX` (`look_fn`: `CTXFN_PREV/NEXT/NOT_*`) at
parse time; `req.c:758` sends `A_CTX` to `rb_row_into` (ZERO), which T3's E-4 makes the bare unit.
Measured at the build tree: `a(?=b)[bc]` and `(?:ab(?=a)){2}` state `span_facts` (`2:97,98`,
`4:97,98,97,98`), which only an `A_CTX` gives (§0's own sentence). Read LITERALLY (positive lookaround =
the `A_LOOK` node, the only node with a body for `rb_walk(w, a->l, ...)`, §5.1), these get no item:
- W-L5 `a(?=b)[bc]`: run `a[bc]` (15 bits, under the floor) not §5.6's `ab`; the plant `ab[bc]` has no site.
- W-RG `(?:ab(?=a)){2}`: no `rg`, plant has no site (run `abab` either way).
- W-A1 `xy[ac](?:(?<=a)b|c)`, W-S1's `(?<=c)`, W-N1's inner `(?<=x)` (run `ab[xy]y`, not `abxy`),
  W-N2's inner `(?=c)`, soundlook (b)/(c)/(d)'s `(?<=a)`, `(?<=b)`, `(?=b)`: same; §5.6 rows
  `[ac][ac]c(?<=ac)(?<=c)d` (`[ac]acd` needs the `(?<=c)` item), `ab[xy](?=(?<=x)y)[xy]` mispredicted.
No answer moves (no guard = a dropped necessary condition). Second reading: the builder treats
`A_CTX` with `CTXFN_NEXT`/`CTXFN_PREV` as a positive lookaround whose item is its set at offset 0/−1
(cube hull, `pos_set`). Also sound (the set is the exact next/previous byte under `byte`, and an
ASCII byte under `utf8`, ctxnode.c:27-33), but the text must SAY it, must restrict to exactly those two
fns (the `(?m)$`/`\b` rows read "absent" and are not items), and the witnesses must be re-derived
under `-fno-ctx-node` or with multi-char bodies. Fix: T1/T3 name `A_CTX`'s two positive fns
(either reading), and re-plant W-L5/W-RG/W-A1/W-S1/W-N1/W-N2 so each guard comes from the node that
carries it.

### SOUNDLIT-2 (CONFIRMED text gap; listing value wrong at L1 under one reading, answer at U-dead; effort: one column in T4/T2; blast: every compile with an empty meet under `?`/`*`/`{0}`/ALT/negative lookaround)
**The dead fact has no combinator rows: EMPTY-MEET says a meet "proves the SUBTREE cannot match"
and "the walk states the dead fact", and §10 U-dead reads it as "a PATTERN ... cannot match ... emit
the constant NOMATCH artifact"; nothing says how a subtree's deadness crosses REP m=0, ALT, or a
negative lookaround.** (§5.2 EMPTY-MEET row, §8 L1 "the dead fact as a listing value", §9 ledger,
§10 U-dead; F21's listing hunk.)
Oracle (libpcre2-8 10.46, p2probe, start 0):
- `x(?:foo(?=bar)baz)?y` on `xy`: M 0 2 (the group is dead, the `?` skips it)
- `x(?:foo(?=bar)baz)*y` on `xy`: M 0 2
- `(?:foo(?=bar)baz){0}x` on `x`: M 0 1
- `(?:foo(?=bar)baz|q)` on `q`: M 0 1
- `x(?!foo(?=bar)baz)y` on `xy`: M 0 2 (dead body under a NEGATIVE lookaround: the assertion always holds)
Reading A (one dead flag per walk, set by any empty meet, which "the walk states" literally says):
all five are listed dead, and at U-dead compile to constant NOMATCH: five deleted matches. The
negative case needs only a build that walks every `A_LOOK` body (one arm, discarding the item for
`neg`), which T1's "positive LOOKAROUND (the unit + item)" does not forbid. Reading B (a per-value
dead bit: CAT = OR, ALT = AND, REP m=0 = false, m>=1 = body's, positive item = body's, negative =
false, `{0}` = false): sound on all five, and is what my model used (0 dead-but-matching across
~20k fuzzed patterns, PROBED-AND-HELD). The text forces neither; A is the literal one. Fix: T4 gets
a DEAD column (the five rules above), U-dead reads the ROOT value's bit, and L1's gate adds
`x(?:foo(?=bar)baz)?y`/`xy` and `x(?!foo(?=bar)baz)y`/`xy` as dead-fact witnesses (each red under
reading A). Today all five list run none; nothing reads dead yet (D77-clean), so this is a text
fix before the listing hunk is written.

### SOUNDLIT-3 (CONFIRMED text gap; answer under one reading at L2 and L3; effort: one word per `++` + one witness; blast: every TOP candidate longer than 32 positions)
**TOP's `++` does not say which end survives the 32-position cap, and the stated offsets are right
only for keep-FIRST (`rn_app`).** (§5.2 TOP row: `tail ++ rg` at `rn_tail_off(maxw, tail.n)`,
`head ++ rg` at 0, `lg ++ head` at `−t`, `lg ++ head ++ rg`.) Both helpers' stated preconditions
hold for every one of those joins (`req.c:303-306`: `a`'s last stored position is really `a`'s
last, true of a tail and of a guard ending at −1; `req.c:320-322`: `b`'s first stored is really
`b`'s first, true of `rg` and of `head`), so the code does not choose for the builder, and W-L9
plants only the extended-length error, not this one.
Repros (libpcre2-8 10.46, p2probe; `A` = 20×`a`, `B` = 20×`b`; T2 row 2 gives `a{20}` and `b{20}`
`all`, c = m = 20 < sat 32):
- AHEAD (L2): `a{20}(?=b{20})` on `AB`: from 0 M 0 20, from 1 N. Keep-first: `a^20 b^12` at 0,
  maxoff 0 (holds). Keep-last (`rn_pre`): `a^8 b^20`, stated at `rn_tail_off(20, 20)` = 0, but it
  sits at 12. A3 admits AHEAD with no code ("K bounds the run's START"): the handoff hits at 12
  with K 0 and resumes at 12, so the match at 0 is skipped, and nothing at or after 12 matches:
  NOMATCH where (0,20) is expected.
- BACK (L3): `(?<=a{20})b{20}` on `AB`: from 0 and from 20 M 20 40; from 21 N. `t` = 20 <=
  `lb_bytes` 20. Keep-first: `a^20 b^12` at −20 (holds at 0). Keep-last: `a^8 b^20` stated at −20,
  but it sits at −8 (offset 12); the omin = maxoff = −20 claim is false, and A3's signed K (L3)
  then skips the attempt at 20.
Not a problem in the rules themselves (keep-first is sound, model PROBED-AND-HELD). Fix: TOP says
"`++` is `rn_app` (keep the first 32 positions, so the candidate's start, and its stated offset,
are unchanged)", and L2/L3 gain this witness pair (planted error: `rn_pre` at TOP).

## PROBED-AND-HELD

**The one question: applying T4 (ITEM, CAT-R, CAT-L, CAT-EDGE, ALT, REP/T2's guard column,
EMPTY-MEET, TOP) literally to the walk's shape, can an answer move? HELD for the rules themselves**
(the three findings above are text gaps where a second reading of the TEXT deletes a match; under
the reading each finding names as the fix, nothing moved).

- **Literal model** (`soundlit/model/t4.py`, written from §5.1/§5.2/T2 text and `req.c:394-490`
  as they are: `rr_cat`'s head/tail/join/best/offset code verbatim, `rr_alt`'s hull, right-folded
  spines as `rb_walk_at` builds them, a fresh value per non-leftmost element, `pos_set` 2, cubes
  `(T,K)`, T2 rows 1-3 with `sat`, the ITEM's four terms, guard-guard meets dropping outward,
  EMPTY-MEET keeping the un-narrowed value, TOP's every candidate checked separately at its stated
  place: head at `p`, tail ending at the match end, best in `[p, p+off]`, `tail ++ rg` from the
  tail's start, `head ++ rg` at `p`, `lg ++ head` and `lg ++ head ++ rg` at `p − t`, plus a dead
  root against any match). Fuzzed random patterns (literals, cube and non-cube classes, `.`, ALT,
  `?`/`*`/`+`/`{m}`/`{m,n}`, positive/negative lookahead/lookbehind nested to depth 4, every
  spine position) against libpcre2-8 10.46 via ctypes at EVERY start offset: **63.5k compiled
  patterns, ~2.9M matches, 0 violations**, across: `MAXN` 32 (22.7k), `MAXN` 3 to force truncation
  and `sat < m` (11.6k), counted repeats `{4}`-`{6}`/`{5,}` of guarded bodies at `MAXN` 3 (10.3k,
  1.48M matches: W-RG at other counts, saturation with a guard, §3.1 pt 3's last sentence),
  a 5-letter alphabet with cube pairs `[xy]` `[bc]` `[ac]` (14.7k), depth 3-4 nesting (guards in a
  group in a CAT in an ALT branch, lookaround in lookaround in repeat; 9.6k). The assertion
  "`all` ⇒ `tail.n == maxw`" (CAT-EDGE's `l.maxw` shift) never fired, so the "`all` but truncated"
  case does not exist: `o.all` requires `!o.head.trunc` (`req.c:463`) and T2 row 2 requires c = m.
- **The checker can fail**: three plants, each caught — CAT-EDGE `rg` leftover carried across a
  non-`all` `r` (41 bad of 2.9k), the same for `lg` across a non-`all` `l` (54 bad), ALT dead as OR
  (39 bad at depth 4; 0 at depth 2, which is why depth 3-4 was added).
- **The model reproduces the note's §5.6/§5.7 predictions** (22 patterns, `wit.py`): `yxz`, `ab`,
  `abcd`, `xy[ac][bc]`, `[ac]acd`, `abxy`, `foobaz`+dead, `bar` rg `baz`, `bar` lg `foo`,
  `(?<=fo{1,3})` lg `o`, `(?<=ab|b)` lg `b`, `[ac]bc`, `[bc]c@2`, `abc` at unbounded,
  `[a-z]?[a-z]a(?=bc)` tail `a` rg `bc` (W-L9's `abc` at 2), `xa[bc]`, `abab` rg `a`, `ac`, `ab`,
  `xy`, `(?<=a(?=b))b` lg `a` — all as the note states (one-char lookarounds treated as items, the
  second reading of SOUNDLIT-1).
- **By hand + oracle, the parts the toy grammar lacks** (8 patterns, p2probe): `ab\K(?<=xab)c` on
  `xabc` from 0/1 M 3 4, from 2 N (run `xabc` at −1 from the ATTEMPT at 1: holds; §2's attempt
  span is what makes it hold); `\G(?<=ab)c` on `abc` from 2 M 2 3, from 0/1 N (`abc` at −2, scan
  from `max(0, 2−2)`); `a(?=bc$)` `xabc` M 1 2 (AHEAD `abc`); `(?<=ab)(?=cd)` on `xabcd` from 0/3
  M 3 3, from 4 N (root `all`, `lg ++ head ++ rg` = `abcd` at −2); `(?:(?<=ab)|(?<=cb))c` `cbc`
  M 2 3 (ALT common tail `[ac]b`, run `[ac]bc` at −2); `ab(?:c(?:d(?<=xabcd)))e` on `xabcde`
  M 1 6 from 0/1, N from 2 (leftover shifted through three `all` levels: `x` at −1, `xabcde`);
  `(?=ab(?<=xab))` on `xab` M 1 1 (lg `x` at −1 inside a lookahead); `(?<=c(?<=bc)d)e` `bcde`
  from 3 M 3 4 (`t` 3 > `lb_bytes` 2: refused; admitted it would also hold, so §5.5's row is a
  refusal, as the note says).
- **`-e utf8` / caseless / straddling** (by reading the lowered-tree rules, `req.c:110-118`,
  `ctxnode.c:27-33`): a multi-byte literal is a CAT of byte positions, so a guard meets bytes at
  exact offsets whether or not it straddles a code point; every variable-byte construct (`(?i)k`
  with U+212A, `(?i)s` with U+017F, `.`, a WCLASS) is an ALT (`all` false) or a gap, so no guard
  crosses it and hulls only widen. No case found where a meet compares positions of different
  alignment. 0 findings.
- **Lookbehind bodies are FORWARD in the tree the walk reads** (`revdet.c:137`, `:346`: back-step
  + forward body), so "the body's TAIL affix at `[-n, 0)`" is the right end. PCRE2 requires the
  body to END at the cursor even for variable length (`(?<=ab?)c` on `axc`: N; on `ac`: M 1 2).
- Not touched: readers beyond T4/TOP (§5.4 is other lenses'); conditionals and verbs are refused
  by this build ("not implemented yet" / "requires module 'verbs'"), so `(*ACCEPT)` inside a body
  cannot reach the item.
- Budget: ~20 pcrec compiles (facts listings), the rest libpcre2 only.
