# altthink — thought lane: case folds as alternations, one alternation reduction

Lane altthink (opus), 2026-11-05, worktree `worktrees/altthink` cut from main 6071c0a9b. A THINKING lane: no source edits, no build go; one `make -j4` of the unchanged tree for probes. Rulings file `altthink_rulings.md`: empty at every read (no rulings applied). Evidence: `altthink_evidence/` (`f.sh` = the probe wrapper over `--emit-facts`, `shapes2.py` + `fold_shapes.txt` = the fold-class shape count).

**Premise test.**
- `src/opt/lower_enc.c` `lower_class_utf8`: CONFIRMED, with one correction. A class with any member above 0x7F lowers to an `A_WCLASS` (which keeps the code-point set) whose byte child is `A_CAT(A_EMPTY, A_ALT(...))`, one branch per `u8_box` box. If the class is one box (contiguous code points, e.g. Ā/ā) there is a single branch and no `A_ALT`.
- `src/facts/req.c` `rr_alt`: CONFIRMED as the cut. It also has a second cause the brief did not name: the `A_EMPTY` seal around the lowered alternation walks as an assertion (`rb_row_into`, KTEXT_ZERO, then `rr_none(0)`), so it cuts the run on the class's LEFT side as well.

**Survey correction (stop rule, said prominently).** rpsurvey's DERIVED claims "`(?i)москва` 0 → 12" and "`(?i)αβγ` 0 → 6" are wrong.
- о, с and в each have a 3-byte third member (U+1C82, U+1C83, U+1C80, CaseFolding.txt status C), so москва has three mixed-length positions and no through-run exists in any representation.
- β's fold class is Β/β/ϐ, and ϐ (U+03D0, CF 90) has a different lead byte from the other two, so β's second byte has 3 members.
- Realistic numbers for these cells are in §5.

## Executive summary (plain words)

1. **The idea is reasonable, and under UTF-8 half of it already exists.** A caseless UTF-8 letter already becomes an alternation of byte strings at lowering. The rest of the compiler (the automaton, the k-set, the start set) already treats that alternation exactly like a class. The parallel logic Frank sensed is real, but it sits in essentially one place: the required-run analysis. It handles a class well and an alternation badly. Two smaller gaps sit next to it: lowering never factors its alternation, and altcls's two stages do not feed each other.
2. **It would be naive in two readings:** folding into alternations at parse time (that loses the class the VM and the earlier passes use), or any alternation logic that ENUMERATES strings (`(?i)` over 30 letters is 2^30 words). The working form is positional: an alternation of equal-width literal strings is read as one SET per position. That reading is exact when the strings are a full product, and a sound superset when they are not.
3. **Unification is real but modest.** The core idea: a class is an alternation of one-byte strings. With it, req.c's class arm and alternation arm become one rule. About three special cases are deleted outright, two duplicate spellings merge, and several pieces generalize. kset, start set and the automaton need nothing.
4. **Measured wins:**
   - `(?i)abcdÀefgh` (utf8): run 6 today, 10 when À is spelled as an exact product.
   - `(?:ab|Ab)(?:cd|Cd)(?:ef|Ef)` (byte): run 4 today, 6 as classes.
   - `(?i)москва` DFA tables: 380 entries today, 300 in the factored spelling.
   - Of 1454 simple fold classes, 513 keep the run today. Lowering-time factoring alone would raise that to 766, set positions to 1019, and a superset-hull rule to 1417. The 37 mixed-length classes never get a through-run.
5. **Bench cells move less than the survey implied.** Inferred: ci-greek-run 0 → 6 (needs set positions and the superset hull), ci-strasse 3 → 5, ci-moskva 0 → about 4. The single-character cells get no run at all.
6. **Byte stays byte-identical by construction** if the change lives inside UTF-8 lowering (byte folds never make an alternation). Extending the req.c rule to user-written alternations moves byte artifacts too, so it is a separate choice change.
7. **The biggest future customer is [SEQ-FOLD]** (ß↔ss, ligatures): those folds can only be alternations of different lengths.
8. **On the kit hand-off:** sets lose nothing for exact-product folds. A "one of these N strings" fact carries strictly more only for user keyword alternations and mixed-length folds; that is the case for an F10-class kernel, and its evidence is still owed.
9. **No source collision with span_pick 1e.** It is a sequencing collision only: moved run facts move kit arms, so build after 1e lands.

## What I checked vs inferred

| claim | how |
|---|---|
| `lower_class_utf8` output shape, the `A_EMPTY` seal, `u8_box` contiguous boxing | READ `src/opt/lower_enc.c` (`lower_class_utf8`, `u8_box`, `u8_ranges`) |
| `rr_alt` sets `all=false` unconditionally; class vs alt arms | READ `src/facts/req.c` (`rr_alt`, `rn_common_head/tail`, `rn_hull_mask`, `rb_class_into`, `rb_walk_at` A_EMPTY arm) |
| run lengths (today) for every pattern quoted | MEASURED, `--emit-facts` single compiles (`altthink_evidence/f.sh`) |
| kset identical across alt vs class spelling | MEASURED (`x(?:\xc3\x80|\xc3\xa0)abc` vs `x\xc3[\x80\xa0]abc`: same `kset_walk`) |
| DFA table 380 → 300 entries; artifact 26760 → 24366 bytes | MEASURED on a BYTE-MODE spelling of the factored lowering (`-fno-altcls-factor` for the unfactored control); the utf8 compile reproduces 380 |
| altcls stage 2's remainder is not re-merged by stage 1 | MEASURED (`(?:ab|aB)xy` run 3, `a(?:b|B)xy` run 4) |
| VM island declines caseless alternations | MEASURED (`VM_ALT_ISLANDS` 1 vs 0 for `(?:select|union|insert)x` vs `(?i)...`) |
| fold-class shape counts (exact / superset / mixed, cube or not) | COMPUTED from CaseFolding.txt C+S (`shapes2.py`); 489 contiguous-exact-cube matches rpsurvey's measured "keep" count exactly |
| class counts per stage (766, 1019, 1417) | INFERRED from the shape counts and the rules (no modified build) |
| bench cell gains (§5) | INFERRED from the fold data and the rules |
| byte alphabet partition computed from NFA atoms, not re-merged after minimization | READ `src/ir/dfa.c` (`refine_by`, header) + the measured table difference |
| corpus population of byte user alternations the general rr_alt rule would move | NOT MEASURED (needs a modified build; owed to the design lane) |
| compile-time effect | INFERRED only |

## 1. Simplification: naive or reasonable?

**Reasonable, in the shape the code already half-has.** Where each step happens today:
- **Byte.** `(?i)a` is the class `[aA]`, and the byte lowering (`lower_class_byte`) is the identity, so a byte fold is never an alternation.
- **UTF-8.** `(?i)м` is a code-point class `{М, м}`. Lowering turns it into `A_WCLASS{М,м}` over the alternation `d0 9c | d0 bc`.
- **After lowering.** The NFA and DFA, `kset.c` (`pcrec_kset_walk`) and `startset.c` (`ss_walk`) are all shape-blind. MEASURED: the same `kset_walk` for the alternation and the class spelling. Only `req.c`'s run reads the alternation worse than the class.

So "set up folds as alternatives" is already done for UTF-8 below the class node. Applying "alternation logic" (altcls stage 1, `b|B` → `[bB]`) to a byte fold returns the class it started from, which is Frank's "the result might be the same for byte encoding" exactly.

**Conditions under which it would be naive, and whether they hold:**

| naive condition | holds? |
|---|---|
| N1. Folds become alternations AT PARSE (literally `(a|A)`) | Would be naive: it drops the code-point set that `A_WCLASS` keeps. The VM tests a wide class with one decode + set test (`emit_vm.c` `vm_wcls_bytes`/`vm_wcls`), and possessify/revdet/select_engine run BEFORE lowering on code-point classes. altcls stage 1 would also merge single-character alternatives straight back into classes. The right shape is the existing one: class above, alternation below. Not a proposal to adopt. |
| N2. Combinatorial blow-up of concatenated alternations | Holds for any reduction that ENUMERATES the language. `(a|A)(b|B)…` is 2^n words; the VM island (`vm_isl_words`) already enumerates and needs three budgets. It does NOT hold for a POSITIONAL reduction (the per-position hull over equal-width branches is linear and never enumerates). The alternation logic must be positional, with enumeration only under a cap. |
| N3. Losing information the cube/class form carries | Partly holds. A class is EXACT per position. An alternation's per-position hull is exact only when the branch set equals the product of its position sets (1019 of 1454 fold classes). For the other 398 same-length classes (e.g. Β/β/ϐ, Σ/σ/ς) it is a superset. A superset is sound for FACTS (a necessary run, a start set) and unsound for REWRITING the matcher. Keep the two operations apart. |
| N4. Mixed lengths (k/K/K, s/S/ſ, ß/ẞ, о/О/ᲂ; 37 classes; every [SEQ-FOLD] 1:n fold) | Holds as a hard limit: no position product exists, and no representation gives a run THROUGH the letter. Alternation logic offers length-aware forms only (common affixes, first/last-byte sets, length groups, §4). |
| N5. Matcher regressions | Low, if the rewrite lives inside lowering. An exact factoring keeps the language, so the minimal DFA is the same machine up to numbering, with smaller tables (§3). The VM tests wide classes with decode+kit, not their byte child (unless `-fno-cls-kit` or a single code point), so the default VM program is unchanged. |
| N6. Compile-time cost | Low (inferred): positional hull is O(positions); merging siblings over `u8_box`'s branches is about linear in boxes × depth, and lowering already builds every box. |

## 2. Collapsing code paths: the inventory

Every place that derives a literal/run/set/prefix fact from an alternation or a class, or rewrites one:

| site (file:function) | input | from an alternation it computes | consumers | under one reduction |
|---|---|---|---|---|
| `src/opt/altcls.c` stage 1 (merge) / stage 2 (`altcls_factor_run`, `altcls_extend_prefix`) | AST, code points, pre-callgraph | bare single-char branches → one class; prefix factoring on a SINGLE literal byte key | every later pass | **The same normal form at code-point level.** Gap: stage 2's remainders are not fed back to stage 1 (MEASURED `(?:ab|aB)xy` run 3 vs `a(?:b|B)xy` 4) |
| `src/opt/lower_enc.c` `lower_class_utf8` / `u8_box` / `u8_ranges` | code-point class | builds the alternation; boxes merge only CONTIGUOUS code points; adds the `A_EMPTY` seal | NFA, VM byte child, req.c, startset | **The same normal form at byte level, inside the new subtree** (legal under the splice-in-place invariant: the subtree is new nodes) |
| `src/facts/req.c` `rb_class_into` | lowered class | a position = one cube ≤ `pos_set` members, else a gap | `req_run`/`req_whole_run` → emit_dfa pre-check, prefilters, handoff, memfn sites | **Becomes the 1-byte-branch case of the alternation rule** |
| `src/facts/req.c` `rr_alt` + `rn_common_head`/`rn_common_tail`/`rn_hull_mask` | lowered alt | cube-hull common head/tail; `all=false` always | same | **Reader: the per-position hull over equal-width, fully stored branches** |
| `src/facts/req.c` `rb_intersect` (req_set) | lowered alt | bytes necessary in EVERY branch | `req_byte`, `req_set_maxoff` | **Stays distinct**: a different question (a byte somewhere, not a position) |
| `src/facts/req.c` A_EMPTY arm (via `rb_row_into`) | A_EMPTY | breaks contiguity like an assertion | — | **Delete**: A_EMPTY is concatenation's identity (`rr_unit`) |
| `src/facts/kset.c` `pcrec_kset_walk`, `pcrec_span_walk`, `pcrec_run_pin`, `pcrec_width_walk` | NFA frontier | per-offset byte UNION (any shape) | kit window family, span facts, width | **Stays**: already shape-blind (MEASURED identical) and already the "sets" Frank wants handed over |
| `src/facts/startset.c` `ss_walk` | lowered AST | union of first bytes | prefilter, start table | stays (shape-blind) |
| `src/facts/endwin.c` `ew_walk_marked`/`em_tails` | AST | end windows | — | stays (declines multibyte encodings) |
| `src/ir/dfa.c` `refine_by` (byte equivalence classes) | NFA class atoms | `d0 9c | d0 bc` refines 9c and bc apart; `d0 [9c bc]` does not | every DFA table | **Shape-SENSITIVE** today (§3b); an exact normal form or a column merge removes it |
| `src/gen/emit_vm.c` `vm_isl_words`/`vm_isl_build` (alternation island) | AST, post-lowering | enumerates the literal language into a trie; `vm_isl_single` only (a 2-member class declines) | VM program | **Reader** of the normal form; already collided once with altcls (its header: `w-256` got 11 islands, 3.0% larger, because altcls factored first) |
| `src/gen/emit_vm.c` `vm_det_seq`, `vm_wcls` | AST | `A_ALT` declines; wide class → decode+kit | VM | stays (matcher's own class code is out of scope, ruled) |
| `src/opt/possessify.c` `first_of`/`text_first`/`item_first`, `src/opt/revdet.c` `pcrec_revdet_first`/`rd_alt_disjoint` | AST pre-lowering | first-byte sets, branch disjointness | possessify/revdet verdicts | stays (runs before lowering; unaffected) |
| `src/core/cpset.c` `pcrec_cls_cube`/`pcrec_cube_of`/`pcrec_cls_single` | class bitmap | the cube detector | `rb_class_into`, memfn | **D187's ONE derivation** of a cube from a set |
| `src/gen/memfn_sites.c` (`pcrec_memfn_wpos_cube`), `src/core/findings.c` picks, `src/gen/emit_dfa.c` (15 `pcrec_fact_req_run` reads) | facts accessors | — | the kit | readers; benefit automatically; [POS-ONE-DETECTOR] owns their three meanings of a position |

**Special cases a unification would delete or merge (counted):**
- Deleted:
  1. `rr_alt`'s unconditional `o.all = false`. Its own comment calls the general case "a same-literal special case" it declined for want of a measured population (D77). Replaced by the general rule.
  2. `lower_class_utf8`'s `A_CAT(A_EMPTY, alt)` seal. Its comment already calls it REDUNDANT since K123, kept only because removing it moves bytes. Removing it is an emitted-byte move: decide at design whether that is an abi event.
  3. A_EMPTY walked as an assertion in `req.c`.
- Merged:
  4. Two spellings of the position domain (`rb_class_into`'s `pcrec_cls_cube` + `rn_members` test, and `rn_common_head/tail`'s `rn_hull_mask` + `rn_members` test) become one set-position constructor (D187).
  5. altcls's two stages become one fixpoint over a single normal form.
- Generalized, not deleted:
  6. `u8_box`'s contiguous-only boxing (a sibling merge sits on top of it).
  7. `vm_isl_single`'s singleton-only edge (class-edged trie).
  8. [RUN-POS-SET]'s k/s first-byte handling, which falls out of set positions plus length-aware alternation instead of being its own mechanism.

So the unification deletes roughly three things and merges two. The larger simplification is conceptual: there is one rule ("a class is an alternation of one-byte strings; an equal-width literal alternation is a product of position sets"), and the class arm becomes a special case of it.

## 3. Optimizations neither path does today

a. **Runs THROUGH equal-width alternations (speed: prefilter strength).**
   - utf8 fold: `(?i)abcdÀefgh` run 6 today (it starts at À: the seal cuts the left side, `all=false` cuts through). The exact product `abcd\xc3[\x80\xa0]efgh` gives 10. MEASURED both.
   - byte user alternation: `(?:ab|Ab)(?:cd|Cd)(?:ef|Ef)` run 4. The same language spelled as classes, `[aA]b[cC]d[eE]f`, gives 6. MEASURED both.

b. **DFA table size (object size).** The byte alphabet is refined from NFA class atoms (`dfa.c` `refine_by`) and never re-merged after minimization. An alternation of single bytes therefore splits bytes the machine never distinguishes.
   - `(?i)москва` utf8: 380-entry tables. The factored byte spelling of the same language: 300 entries, whole artifact 26760 → 24366 bytes (−9%). MEASURED, byte simulation.
   - Same effect on a small case: `x(?:\xc3\x80|\xc3\xa0)abc` 56 vs `x\xc3[\x80\xa0]abc` 49 entries.

c. **VM islands for caseless keyword alternations.** `(?i)(?:select|union|insert)x` gets no island today (MEASURED `VM_ALT_ISLANDS 0` vs 1 without `(?i)`). A trie whose edges are position sets would take it; the gain is inferred.

d. **Superset-hull runs for non-product folds.** Example: `(?i)αβγ` → `CE[B1 91] {CE CF} {B2 92 90} CE[B3 93]`, 6 positions. This needs set positions (β's tail has 3 members); inferred.

e. **+1 position on each side of a mixed-length letter** (first-byte set `{4B,6B,E2}` for k, last-byte set `{4B,6B,AA}`). Example: `(?i)straße` 3 → 5. Inferred; it needs set positions.

f. **Compile time.** Fewer NFA states for factored lowered classes (`d0 [9c bc]` is 2 class states, `d0 9c | d0 bc` is 4 plus a split). Small; inferred.

## 4. New optimizations in alternation handling itself

- **Exact-product collapse.** A capture-free alternation of literal branches all of width n becomes a concatenation of n position sets, when the branch count equals the product of the per-position set sizes. Soundness is the same as altcls stage 1: distinct literals of equal width are mutually exclusive at a position, so preference cannot matter. altcls's header warns that per-position merging is UNSOUND "in general" (`frank|fred`): the exactness test is the boundary. Example: `(?:ab|Ab|aB|AB)` → `[aA][bB]`.
- **Suffix factoring** (altcls has prefix only). `(A|B)C ≡ AC|BC` in leftmost-first, just as `C(A|B) ≡ CA|CB`, so both directions keep preference (capture-free). Example: `(?:xabc|yabc)` → `[xy]abc`, which today reports run `abc`; a run of `[xy]abc` also needs the 2-cube/set position.
- **Factoring on a set key, not only a single literal byte.** altcls's key is one literal byte "to keep the argument simple". Left distributivity holds for any identical capture-free factor, so `[aA]x|[aA]y` → `[aA][xy]`.
- **Length-group splitting for mixed widths.** Example: `k|K|\x{212A}`, or after [SEQ-FOLD] `ß|ẞ|ss`. Group the branches by width; each group is a product. The facts are (i) the common affixes across groups (sets), (ii) per-group runs, (iii) the bounded set of strings.
- **Trie with set edges** (prefix and suffix shared): the VM island's input generalized, built once and read by the island and by any string-set fact.
- **Kit-facing: a "one of these N literal strings" fact.** Stated as a FACT per D157: "every match contains, or begins with, one of these strings; N ≤ cap". The kit's method is not presumed.
  - Is it richer than sets? Yes, by exactly one thing: the CORRELATION between positions. For an exact-product fold the per-position sets lose nothing, so **folds alone make no case for it**. For user keyword alternations (`\b(true|false|null)\b`, the dfa-hat cell [OPT-A] records as 38.6% of R17-b's ALPHA loss; `942140-dbnames`) and for mixed-length folds, the set hull admits cross-products the strings exclude.
  - Is there a SIMD case? A multi-literal kernel of the F10 class (`docs/design/memfn/requirements.md` F10, tier B) can use the correlation to cut false candidates.
  - Evidence owed: the candidate rate of the hull window vs the string set on bench text, per cell. That is the measurement that would trigger the fact.

## 5. Value assessment

**Who benefits:**

| population | today | with the reduction | measured / inferred |
|---|---|---|---|
| byte folds | classes; never an alternation | **identical by construction** if the change is confined to lowering (`lower_class_byte` returns NULL; `(?i)` under byte or `--ucp` stays ≤ 0xFF) | read |
| utf8 fold classes (1454, simple folds) | 513 keep the whole run (24 ASCII + 489 contiguous exact 2-cube) | + exact factoring at lowering, req.c unchanged: **766** (+253 non-contiguous exact 2-cube, e.g. À/à); + set positions (D187): **1019** (+253 exact non-cube); + superset hull rule in req.c: **1417** (+398); mixed **37** never through | shape counts computed; 489 matches the survey's measured count; stage totals inferred |
| bench `bench/utf8` ci-* cells | ci-strasse 3, ci-moskva 0, ci-greek-run 0, ci-e-acute 0, ci-sigma 0 | ci-greek-run → 6 (needs sets + superset hull); ci-strasse → 5 (sets, +1 each side); ci-moskva → about 4 (о/с/в are mixed-length: best is с's last byte `{81 a1 83}` + к `d0[9a ba]` + в's lead `{d0 e1}`); ci-e-acute/ci-sigma/ci-kelvin/ci-long-s: single character, no run in any form | inferred |
| byte user alternations (`(?:ab|Ab)...`) | cut by `rr_alt` | full run with the general rr_alt rule | per-pattern measured; corpus population NOT measured |
| [SEQ-FOLD] (1:n folds) | n/a (not built) | the main future beneficiary: every ß↔ss, ﬁ↔fi, st↔ﬆ position becomes a mixed-length alternation; without a length-aware reduction each one cuts every run it touches | inferred |
| DFA object size, utf8 caseless | alphabet split by lowered alternatives | 380 → 300 table entries on `(?i)москва` | measured (byte simulation) |

**Cost and risk:**
- The lowering-side normal form is small and well-bounded: a sibling merge over `u8_box` output, with an exactness check.
- The req.c rule is a few lines in `rr_alt`, but its soundness statement changes. `all` would then mean "fixed width and every byte lies in its position's set", not "exactly this literal". Every `req_run` reader must be re-checked for an exactness assumption; `run_pin` is kset's and separate.
- Set positions are D187's own build, already filed under [RUN-POS-SET]/[POS-ONE-DETECTOR].
- The information ranking (`rn_info`, popcount of the mask) needs a set analogue (8 − log2|set|). That is a design question, and it moves the run floor.

**D186 framing:**
- Lowering-side factoring is a UNIT change for byte (zero movers by construction; an emit-diff over the byte corpus can REQUIRE zero) and moves only utf8 artifacts. Under utf8 it is a unit change for the tables and a CHOICE change wherever a longer run flips a scan pick, so it needs utf8 per-regime evidence.
- The general `rr_alt` rule moves byte artifacts with user alternations: a separate choice change with byte evidence.
- Staging them in that order keeps byte frozen through the first step.

**Lenses:**
- Specific vs general: the general form is the class-as-alternation rule; the k/s first-byte rule is a corollary, not a mechanism.
- Core vs derived: the normal form is a property of the tree (core); runs, tables and islands derive from it.
- Fits the architecture vs needs a refactor: fits. Lowering already builds a new subtree; altcls already owns user alternations. One shared normalizer function with two call sites (code-point level in altcls pre-callgraph, byte level inside lowering) respects both pass-order constraints. A single post-lowering pass over USER alternations would collide with the splice-in-place invariant (`pcrec_callgraph_build` caches group bodies), so it must not be proposed as one pass.

**Remodel overlap with span_pick stage 1 unit 1e.** 1e is kit-side: T-FRAME/T-FIND walk, renderers, the `wfD` → `fd` row map, REACH EQUALITY. There is no shared source file. But any change to `req_run` content moves the run positions handed to the kit (via `pcrec_memfn_wpos_cube`), and with them arms and witnesses. Building this during 1e's landing would contaminate 1e's REACH-EQUALITY and arm pins. Byte-identical-by-construction protects byte cells only. Sequence the build after 1e (D153). Set positions also want [POS-ONE-DETECTOR], which is gated on the kit split.

## 6. My additions

- **Survey correction** (top of this report): the москва and αβγ derived numbers came from treating every non-ASCII fold as a 2-member, same-length pair. 37 classes are mixed-length and 398 same-length classes are not exact products. Any plan sized on "0 → 12" is oversized.
- **The left-side cut is the seal, not only `rr_alt`.** `(?i)abcdÀefgh` keeps À and its right neighbours and loses `abcd`. Fixing `rr_alt` alone would still lose the left side under utf8.
- **Adjacent unification, independent of the idea: re-merge the DFA alphabet after minimization** (bytes whose transition columns are identical in every state). This makes table size shape-blind for EVERY pattern (user alternations, folds, altcls output) without any AST rewrite. Trigger: an object-size or cache-pressure cell on a caseless utf8 or wide-alternation pattern. Context atoms and the word set must stay distinct: design question.
- **altcls's stages do not compose** (stage 2's `b|B` remainder is never merged). Small, general, byte-moving. It belongs with the shared normalizer, not as its own fix.
- **Two trie builders already exist and have collided:** altcls stage 2 and the VM island. The general rule (one normal form; readers read it) is what prevents a third.
- **What stays SETS for the kit:** kset already hands per-offset byte sets for any shape, including variable width. So "the hand-off stays sets" is already true for kset. The only cube-typed hand-off is the required run, which D187 already rules into sets. The string-set fact is the one candidate for "richer", and only for non-product languages (§4).
- **Risk:** superset positions weaken a run's information. A long superset run could outrank a shorter exact one under a naive ranking and pick a worse scan member. The ranking must count set size, and a choice-row census must watch it.
- **The general form, with what it unlocks:** "a class is an alternation of one-symbol strings; an equal-width capture-free literal alternation is a product of position sets (exact, which may be rewritten; or superset, facts only); unequal widths split into length groups." Unlocks:
  - [RUN-POS-SET], subsumed. Trigger: already fired.
  - [SEQ-FOLD]'s 1:n folds. Trigger: its first child's design note.
  - [OPT-A]/F10's string-set fact. Trigger: the candidate-rate measurement in §4.
  - Caseless VM islands. Trigger: a VM cell with a caseless keyword alternation.
  - The alphabet merge above.

**The design lane's first questions:**
1. Where the normal form lives: inside `lower_class_utf8` only (byte zero movers, provable by emit-diff), or also as a shared normalizer called from altcls (byte moves, its own evidence)?
2. Exact vs superset: confirm every `req_run` reader tolerates superset positions under a redefined `all`, or keep superset hulls out of `all` and only in common affixes.
3. Ship in the cube domain first (+253 classes, no req.c change), or wait for D187 set positions (+506), given that the bench cells mostly need sets?
4. The information measure for a set position, and what it does to the run floor.
5. Mixed width: +1 affix sets only, or length-group facts? [SEQ-FOLD] decides how far this must go.
6. The string-set fact: the cap, and the candidate-rate measurement that would justify it to the kit.
7. Sequencing: after span_pick 1e and alongside [POS-ONE-DETECTOR], and whether removing the seal is an abi event.

STATE AT HANDOFF: report + evidence committed on `lane/altthink`; no source touched; no owed runs; rulings file empty at every read (no entry applied).
