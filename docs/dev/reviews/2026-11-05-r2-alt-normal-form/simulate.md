# simulate lens findings (SIM-), critic round alt-normal-form, 2026-11-05

Method: implemented the note's rules from its TEXT first (`mine.py`: width
groups, sibling merge to fixpoint, hull, info 8-ceil(log2|S|), floor 16;
`mybest.py`: s2c/s3/s3m run model), then diffed against `pred.py` and
`stage_pred.tsv`. Review build `$W/build/pcrec`. Compiles run: about 2800
(foldsweep 1454, byte-spelled stage-1 sweep 742, pred rerun ~170, growth
sample ~340, rest small). All scripts and outputs are in this directory.

## Findings

### SIM-1 (doc, low) G4 says "at least 1417" and depends on an unstated member-count bound
- CONFIRMED by recount. 1417 = 766 (cube products, incl. 24 ASCII) + 253
  (exact non-cube) + 398 (superset hull). But §5 stage 3 and §10 leave the
  replacement for `pos_set` (today PCREC_MAX_REQ_RUN_POS_SET = 2, RULED in
  limits.def with a two-arm-scan rationale) as "a declared row with evidence".
  My recount of position sizes: exact non-cube classes have max position size
  2 (249) or 3 (4); hull classes max 2 (388), 3 (9), 4 (1). So the kept count
  is 1403 at bound 2, 1416 at bound 3, 1417 only at bound >= 4. G4/§4.3's
  1417 therefore silently assumes a bound of 4 (or no bound; pred.py's
  `ok()` uses `len(s) < 256`, i.e. NO bound), against a ruled limit whose
  stated reason ("a wider set is a third arm no cell asks for") the note does
  not address. Fix: state the bound the 1417 assumes, give 1403 for bound 2.
- Also G4 says "at least 766" while Gate U2 says "766 exactly": pick one.
- Repro: `mine.py` (position-size table), `confl`-free; bytes in `mine.py` run.

### SIM-2 (design/doc, medium) the fixpoint is not confluent: the "normal form" is order-dependent in SHAPE
- CONFIRMED (`confl.py`, `bigcls.py`). §3 says the result "is exact whatever the
  order, and the order makes it reproducible". True for exactness; false as a
  normal form: different merge orders end in different BRANCH COUNTS.
  Random small grids (w 2-3, alphabet 2-4, 3-9 points, exhaustive orders,
  3000 trials): 679 (23%) have >1 distinct final branch count (e.g. points
  {(0,2),(0,3),(1,0),(3,0),(3,1),(3,2),(3,3)} end in 3 or 4 branches).
  On real UTF-8 box lists (u8 box decomposition of the Unicode category,
  ascending-first-pair vs descending-first-pair): \p{Lu} 663 boxes -> 76 vs 66;
  \p{L} 825 -> 336 vs 329; \p{N}, dot, Greek, Cyrillic equal. The 1454 fold
  classes are immune (all 1491 width groups confluent, max group 4 branches),
  so G4/§8 numbers are unaffected. But "one owner of the normal form" (G3,
  §11 D-next "Alternations have one normal form") is not canonical on wide
  classes: language-equal alternations can reduce to different forms, hull
  stays equal. Wording should say "a reproducible reduction", or the build
  should state a canonical strategy (e.g. per-position grouping), and the
  stage-1 table/size predictions on wide classes are order-sensitive.
- Complexity of "scan pairs ascending, merge first applicable" is unstated:
  \p{L} costs 13.0M pair compares in my model; sorted input keeps siblings
  adjacent so typical cost is low, but no bound or cap is stated and a
  grouped (hash by all-but-one position) algorithm is the standard cure.
  SUSPECTED (compile-time) for classes with thousands of interleaved boxes.

### SIM-3 (answer-gate/process, medium) Gate U1's "predicted set" is not computable as stated, and is one-sided
- CONFIRMED that no observable exists: `--emit-facts`/`--emit-ir` expose no
  lowered-branch count (checked output of `--emit-facts` for `(?i)xβy` and
  `[^é]`; `--help` lists no tree dump). "Computed on the BASE compiler before
  the build: utf8 compiles with a non-ASCII class whose lowering has more than
  one branch" needs either a new base-compiler instrument or an external
  re-implementation of u8_box (shares nothing with the compiler, but then it
  is my `bigcls.py` model, not "the base compiler").
- And the predicate is a superset test: movers must be a SUBSET of
  "multi-branch classes"; that set is nearly every non-ASCII-class compile
  (dot, [^x], \w UCP), so U1 can only catch a mover with NO multi-branch class
  (e.g. an ASCII-only utf8 pattern), which B0's second clause already covers.
  A tighter computable predicate exists: "some class has two same-width boxes
  differing at exactly one byte position after merge" (a script over u8 boxes).
- Related, SIM-4 below: the movers are far more than the note lists.

### SIM-4 (speed/gate scope, medium) stage 1 moves every utf8 compile with `.`, `[^x]`, \p, not just "possible" cls-/prp-
- CONFIRMED by spelling. The 3-byte branches `[e1-ec][80-bf][80-bf]` and
  `[ee-ef][80-bf][80-bf]` of `.` differ in ONE position, so the merge fires on
  dot (and any negated class). Byte-spelled dot: `x.y` 480 -> 448 entries,
  `.*foo` 495 -> 462 (-7%). 20 of 76 bench/utf8 patterns contain `.`, `[^`,
  \p, \W etc. (cls-dot, cls-dot-rep, qnt-dot-bounded, cls-neg-*, prp-*, lit-
  mixed-ascii, ci-neg-fold). §5 lists these as "(possible)"; for dot it is
  certain. U4 must treat them as predicted movers (D186 unit bar per regime),
  and any wide fixture / pinned artifact containing a utf8 dot is re-pinned
  under B0-adjacent "movers manifest". Effort: small (change a word, widen the
  predicted-mover list); blast radius: the utf8 bench and every pinned utf8
  whole-file fixture.
- Note the byte-spelled UNMERGED dot gave 480, not today's 512, so the s0-
  style control does not hold for `.` (different lowering path); I could not
  verify a base-equals-control for wide classes.

### SIM-5 (doc, low-medium) §8 / §5 quoted table numbers for partial-merge letters are not what stage 1 produces
- CONFIRMED (`true_s1.py`). pred.py's s1 spelling leaves non-product groups
  as today's boxes; the note admits it "UNDER-states stage 1" but quotes the
  numbers as predicted movers (§5: `(?i)Ελληνικά` 1430 -> 1170, `(?i)αβγ`
  160 -> 128). Spelling the owner's real output (`ce[92 b2]|cf 90` for β):
  αβγ 160 -> 112 (-30%, not -20%), Ελληνικά 1430 -> 1040 (-27%, not -18%).
  The other 8 rows I recomputed equal the note exactly (abcdÀefgh 121,
  москва 900, straße 429, é 9, information_schema 960, select 192, привет
  мир 1296, naïve café 143). Direction is safe (U3 is "<= base"), but G5's
  and §5's absolute figures should be the partial-merge ones or flagged.

### SIM-6 (design, low) stage 2b's flagship example is already fixed by stage 2
- CONFIRMED. §5 stage 2b: "Fixes the measured non-composition `(?:ab|aB)xy`
  (run 3) vs `a(?:b|B)xy` (run 4)" (re-measured on the review build: 3 vs
  4). But stage 2's `rr_alt` hull over equal-width `all` branches already
  yields `a[bB]` (hull of `ab`,`aB`) and thus 4 without any altcls change
  (cf. its own probe `(?:ab|Ab)(?:cd|Cd)(?:ef|Ef)` 4 -> 6). 2b's gate cannot
  show this as a 2b mover; its distinct benefit is AST-level (suffix/any-key
  factoring, VM/DFA tables), which §5 should name as the predicted movers.

### SIM-7 (design, low) R1-R3 and "unit-pure" hold, but the ranking is coarse in a way worth stating
- CONFIRMED the claim: info(S)=8-ceil(log2|S|) equals popcount(K) for every
  cube (|S|=2^k -> 8-k, k=0..8, and req.c's `rn_info` is Sum popcount(mask));
  today's positions are cubes of <=2 members, so stage 3 is unit-pure on them.
- Drill on constructed candidates (arithmetic, rule from §4.4): 11
  three-member positions = 66 bits beats an exact 8-byte run (64): a long
  superset run outranks a shorter exact run, as the note says (R2 census
  only LISTS the flip; R3 is built "only then"). A 3-set (6) ties a 4-cube
  (6), `a` wins ties (leftmost), though the 3-set is truly more selective
  (6.41 vs 6 bits); 5..8-member sets all charge 5 bits; a 2-member NON-cube
  set charges 7 like a cube pair but needs a set test, not `(s&K)==T`.
  Realistic: per-letter hull of Greek beta = 7 + 6 = 13 bits, so a 5-beta
  caseless literal (65 bits) outranks an 8-byte exact run on lead-byte-heavy
  text. None of this is a defect, but R2 has no pass/fail: only a "census
  lists" action and a trigger (R3) whose evidence regime (real Cyrillic/Greek
  text) is not in the corpus or bench list the census runs over. State that
  R2's census is a listing and that the stage-3 D186 choice bar needs the
  real-text regime BEFORE landing, not after an R3 trigger.

### SIM-8 (doc, low) control caveat in §8 is explained: it holds only for a class that is the whole pattern
- CONFIRMED (traced). §8 says the byte spelling of bare `(?i)k`/`(?i)s`
  emits 60-72 entries vs utf8's 48, "cause not traced". The mismatch is for
  patterns that are a single class only: today/s0 entries `ß` 60/90, `ſ` 30/45,
  `ᲂ` 70/105 vs embedded `xk` 105/105, `xs` 72/72, `kx` 175/175, `sx` 120/120,
  `ks` 180/180, `xß` 126/126. So the s0 control is valid whenever the class
  is not the whole pattern; the two bench cells ci-kelvin (`(?i)k`) and
  ci-long-s (`(?i)s`) are exactly the whole-pattern case, so for those two
  cells the spelled control cannot predict the table direction (as §5
  already says); embedding them (`xk`, `kx`) would give a usable proxy.

## PROBED-AND-HELD

- Census 1454 simple fold classes: held (my recount from CaseFolding.txt:
  C+S entries grouped by target; 1454).
- Shapes 24 ASCII + 489 exact cube contiguous + 253 exact cube non-contiguous
  + 253 exact non-cube (54 contig + 199 noncontig) + 37 mixed + 398 superset
  (132 + 1 + 265): 1454 total, equals
  fold_shapes.txt. Mine: cube products 766, set products 253, 2-group
  superset 398, mixed 37 (766+253+398+37=1454).
- 513 measured today: rerun of `foldsweep.py` (1454 compiles) on the review
  build, keep = req_whole_run positions == 8 + class width: 513 = 24 (w1) +
  210 (w2) + 279 (w3); 37 mixed none; 904 not kept. Equals 24+489.
- 766 after stage 1: byte-spelled merged form of each non-ASCII class
  (`s1sweep.py`, 742 compiles): all 742 cube-product classes keep the full
  run (262 at 10, 381 at 11, 99 at 12); +24 ASCII = 766; set products and
  multi2 do not (5-8 positions), as predicted. Hence "+253 (513 -> 766)"
  holds; 253 is also the exact non-cube count (coincidence, not a link).
- +253 exact / +398 superset (§4.3): recount identical; hull positions 388
  classes within 2 members (see SIM-1 for the 14 wider).
- 37 mixed-width classes (§4.5): held (35 mixed-length + 2 ASCII+multibyte).
- pred.py rerun on the review build: stage_pred.tsv reproduced byte-identical
  (16 patterns). My independent s2c/s3/s3m model (`mybest.py`, written before
  reading pred.py) agrees on all 16 x 3 inferred cells. Divergences between
  pred.py and the note's text: none in values; only (a) pred.py's `ok()` has
  no member-count bound (SIM-1) and (b) its tie rule is leftmost via strict >.
- §8 table: today/s0/s1/s3/s3m columns and entries held for every row except
  the two partial-merge rows (SIM-5); the table omits pred's s2c column and
  its scan/pf columns, which also matched `ci-greek-run` offset-set -> handoff.
- stage2_byte_probes.txt: 8 probes rerun on the review build, all identical
  (including `(?:ab|aB)xy` 3 vs `a(?:b|B)xy` 4).
- G5/U3 no table growth: 169 stratified fold classes (`x<X>y`, utf8 today vs
  byte-spelled merged form), 0 grew (27 same/15 shrink cube, 32/11 setprod,
  31/6 mixed, 44/1 multi2) plus all 28 pred rows. Sample only, not the
  census U3 requires.
- B0: lower_ops[] dispatch per encoding and `if (ascii) return NULL` in
  lower_class_utf8 verified in src/opt/lower_enc.c:327-332,427-429; control
  is independent (base compiler lacks the owner).
- Sibling merge exactness: no counterexample over the fold classes; order
  independence of the branch count holds for all 1491 fold width groups.
- info(S): popcount(K) identity for cubes, 14 < 16 for a (byte, 3-set) pair,
  and 3-set never overstated (6 <= 6.41): held.
- Standing questions: regime stated per number (compile-time facts, Zen 4,
  gcc 15.2; speed owed per stage); U2's control (CaseFolding.txt -> shapes2.py)
  is independent of compiler code and I reproduced it with fresh code and a
  measured byte sweep, though it shares the pos_set=2 domain with the subject
  by construction (SIM-1); populations: the 1454 census is counted, stage-2
  census is explicitly "first deliverable, not yet measured".

END OF FINDINGS
