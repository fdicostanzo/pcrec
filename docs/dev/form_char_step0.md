# [FORM-CHAR] STEP 0 + [OPT-CLSPACK] STEP 0 — the character-test-form measurement

Lane C′ (`form0`), branch `lane/form0`, worktree `worktrees/form0`, on `main`
at abi 20. Written under the evening box hold — `.hold` present,
`.hold_ack` written 2026-09-04, no `.lift` at the time of writing. Every
number below comes from a SINGLE compile / SINGLE run of each twin (the
`.hold`'s allowed shape); nothing here is a timing number. Timing is owed
to a follow-up run on a quiet box after `.lift` (§6).

No `src/` change on this branch. This is measurement only (D77): the two
questions this STEP 0 exists to answer are (a) is a CLASS test faster than
a folded COMPARE for a caseless literal chain, and (b) is a 256-byte table
load faster than the 32-byte bit array's load+shift+and — on both engines,
with cache footprint (table bytes) counted alongside the runtime cost.
Nothing here is built to ship; a size table is a fact, a timing table is
owed.

## 1. Protocol

**Twins.** Each twin is ONE emitted artifact (`build/pcrec` single compile,
`--emit-main`) with its class-test / scan-edge-test form hand-edited by a
mechanical Python transform (`scripts` kept in the session scratchpad,
described in full in §2 — not committed, per the scope mandate: this lane
touches nothing outside its worktree and its scratch). Each transform:

1. Parses the EMITTED class-bitmap table(s) (`rx*_class_bitmapN[32]` for
   the VM, `rx*_<dir>_scanN[256]` for the DFA scan edge) straight out of the
   base artifact's own text — never re-derives the byte set from the
   pattern, so the twin's set can never disagree with what the compiler
   actually built.
2. Replaces ONLY the table declaration block and the fixed test-expression
   substring at every site with the new form's declaration + test.
3. Nothing else moves. This is CHECKED, not asserted: every twin's
   diff-line count against its base is printed (§2's per-twin lines), and
   is confined to the declaration lines removed/added plus one changed line
   per test site — never a labels, gotos, comments or any other line.

**Compile + correctness.** Each twin compiled once (`gcc -O2 -g -Wall
-Wextra -std=gnu11`), run once per subject listed in each family's own
table below, and its answer (`match a b` / `nomatch`) compared against the
base artifact's answer on the same subject. **Every cell agreed.** No
subject sweep, no oracle beyond the base artifact itself — this rung is a
"did the transform change ONLY the test form" check, not an answer-identity
gate; the base artifact's own correctness is already covered by pcrec's
standing test suite.

**Size.** `size` (text/data/bss) on each compiled `.o`, plus `objdump -h`
for `.rodata` bytes, plus a per-family table-count where the twin's whole
point is the count (family D). Reported now, under the hold — sizing is a
static property of the compiled object and needs no quiet box.

**Timing (owed).** `<prefix>_search` in a find-all loop, `N = 11` rounds,
arms INTERLEAVED round by round, `/proc/loadavg` 1-minute figure gating at
`< 0.5` (refuse, not caveat), median ns/call and ns/byte with the per-round
range, answers checksummed every round — `isl1_report.md` §12's protocol,
copied verbatim. Not run here; §6 names exactly what still needs it.

## 2. Family A — VM literal chain under caselessness (class-vs-compare, D82's `char-match` axis)

Pattern `abcdef` under `-i --engine=vm` (forces the shape the class pool
takes independent of engine selection). D23 already establishes this
compiles to six per-position two-member classes (`'A','a'` … `'F','f'`),
confirmed here directly off the emitted `rx*_class_bitmap0..5[32]` tables:
every one is exactly a case-fold pair (`0x41/0x61` … `0x46/0x66`).

Four twins, one test line pattern each (site 0 shown; all six sites are the
same shape):

| twin | test expression | table decl |
|---|---|---|
| `base` (today) | `((rxA_class_bitmap0[(subject[scan_position]) >> 3] >> ((subject[scan_position]) & 7)) & 1)` | 32B/site |
| `fold` | `((subject[scan_position] | 0x20) == 97)` | none |
| `table` | `(rxA_scan_table0[subject[scan_position]])` | 256B/site |
| `atom` | `((rxA_scan_mask0 >> rxA_scan_atom[subject[scan_position]]) & 1)` | ONE shared 256B table + one 8B mask/site |

The `fold` form is `vm_cls_test`'s own future `ascii-fold` object ([FORM-CHAR]
object 2) generalized to the OR-of-exact-compares fallback for a non-fold
set — never exercised by this pattern's six sites, kept in the transform so
it has no silent special case. The `atom` form is [OPT-CLSPACK]'s general
form: one shared byte→atom partition table plus a 64-bit mask per class,
`atoms[]` built from the byte→(set of classes containing it) signature —
here 6 disjoint classes plus the dead signature, 7 atoms total.

**Correctness** (4 subjects × 4 twins, all agree with `base`): `abcdef`
(match 0 6), `ABCDEF` (match 0 6), `AbCdEf` (match 0 6), `xyz` (nomatch).

**Size**, six sites, `gcc -O2 -c`:

| twin | .text | .rodata | diff lines vs base |
|---|---|---|---|
| `base` | 2,950 | 192 B (6×32) | — |
| `fold` | **1,822** | **0** | 48 |
| `table` | 3,862 | 1,536 B (6×256) | 240 |
| `atom` | 2,062 | **256 B** (shared) | 70 |

`fold` is the outright winner on both axes here: 38% smaller `.text` than
`base` and it deletes the table pool entirely. `table` is dominated on
BOTH axes by every other form — larger code AND 8× the `.rodata` of `base`.
`atom` sits between `fold` and `base` on code size (30% smaller than
`base`, 13% bigger than `fold`) while cutting `.rodata` to a single shared
256-byte table regardless of how many classes exist (§4 pushes this
further). **On code size alone, ranking is `fold` > `atom` > `base` >
`table`, unambiguously** — table is not merely slower-if-anything, it is
worse on the one axis this STEP 0 can measure without the box.

## 3. Family B — a general and a sparse class (bit array vs table vs range compares)

Two patterns, `--engine=vm`, one bitmap-class site each:

- `general`: `[a-zA-Z0-9_]` — 63 members, 4 maximal runs (`0-9`, `A-Z`,
  `_`, `a-z`).
- `sparse`: `[aeiou]` — 5 members, 5 singleton runs (no two vowels are
  adjacent bytes).

Three shapes per pattern (`bitmap` = `base`, already emitted; `table` and
`rangecmp` derived): `rangecmp` is an OR of the class's maximal contiguous
runs, each `vm_cls_test`'s own range shape (`(unsigned)(byte - lo) <= hi -
lo` or an exact compare for a singleton run).

**Correctness**: `general` on `"aZ9_-"` (match 0 1) / `"!!!"` (nomatch);
`sparse` on `"xoy"` (match 1 2, the `o`) / `"xyz"` (nomatch). All three
twins per pattern agree.

**Size**, `gcc -O2 -c`:

| pattern | twin | .text | diff lines vs base |
|---|---|---|---|
| general | `base` (bitmap) | 1,156 | — |
| general | `table` | 1,380 | 40 |
| general | `rangecmp` | 1,188 | 8 |
| sparse | `base` (bitmap) | 1,151 | — |
| sparse | `table` | 1,375 | 40 |
| sparse | `rangecmp` | **1,087** | 8 |

**The table form loses on `.text` at N=1 site too** — +19-24% over the bit
array — which matters because [OPT-CLSPACK]'s crossover argument is about
`.rodata` (32N vs 256+8N bytes), not `.text`; this STEP 0 finds the table
body ALSO costs code size at every scale it was measured at (here and in
§2/§4), never only cache footprint. `rangecmp` is a near-wash against the
bit array on the general (4-run) class (+2.8%) and a clear win on the
sparse (5-singleton) one (-5.6%) — the direction the FORM-CHAR axis would
predict (fewer, cheaper compares beat a table when the set is small and the
runs are few), but the margin is too close on the 4-run case to call
without a timing number.

## 4. Family C — the DFA scan edge (bitmap vs range vs fold)

`emit_dfa.c`'s axis-I `bitmap` body (`scan_test_bitmap`/`scan_tables_bitmap`,
a 256-byte membership table, ONE load — the "misnomer" plan.md's filing
note flags: it is a byte table, not a bit array) against a `range` body (OR
of the run's maximal contiguous ranges) and a `fold` body (the same
ascii-fold compare as family A, since every scan-edge site measured here IS
a caseless letter pair).

**Small witness**: `(?i)a{2,40}Z` under `--engine=dfa --no-captures`. Four
scan-edge sites (forward, two reverse, one anchored machine), every one the
byte set `{'A','a'}` — confirmed by parsing the emitted 256-byte tables
directly, not assumed from the pattern.

**`ci-256`** (pcrec-bench's `bench/altwide/patterns/ci-256.rx`, read-only):
`(?i)` over 256 disjoint lowercase words, forced onto a bitmap scan edge per
plan.md's filing note and the bench's `2026-09-03-altwide-0.2-noedge-ccrerun-1989c62.md`
ledger (§(iii): "the only bitmap edge in altwide", 31/34 siblings take
`range`). Eight scan-edge sites at abi 17, every one confirmed here a
two-member case-fold pair (`F/f`, `M/m` ×3, `O/o` ×2, `R/r`) — so `(?i)`
folding is confirmed the cause: every site this pattern's DFA construction
produced is exactly the shape a caseless letter makes, never an arbitrary
disjoint set.

**Correctness**: small pattern on `"aaZ"` (match 0 3), `"AAaaAAaaZ"` (match
0 9), `"aZ"` (nomatch — below `{2,40}`'s floor), `"bbZ"` (nomatch); ci-256
on four sampled words in mixed case (`dybf`/`DYBF`/`DyBf`, `LIYKXUH`, all
match) plus a miss (`notaword`, nomatch). All twins agree on every cell.

**Size**, `gcc -O2 -c`:

| witness | twin | .text | diff lines vs base |
|---|---|---|---|
| small (4 sites) | `base` (bitmap) | 4,585 | — |
| small | `range` | 3,473 | 88 |
| small | `fold` | **3,425** | 88 |
| ci-256 (8 sites) | `base` (bitmap) | 284,744 | — |
| ci-256 | `range` | 282,536 | 176 |
| ci-256 | `fold` | **282,488** | 176 |

The 256-byte table body costs real code size at BOTH scales: 24-25% more
`.text` on the small witness (4 sites), 0.79-0.80% more on `ci-256` (8
sites, but the artifact is 990 KB total and the scan-edge machinery is a
small fraction of it). `range` and `fold` are within a few bytes of each
other on both witnesses — expected, since every site measured here IS a
case-fold pair, so `range`'s two-compare OR and `fold`'s single masked
compare cost about the same in instructions; a set that were NOT a
fold-pair would separate them, and this STEP 0's witnesses cannot show
that split (§6). What the table form ALSO removes from `.rodata`: 4×256 =
1,024 B (small) / 8×256 = 2,048 B (ci-256) that `range`/`fold` need none of.

**This directly answers the plan row's Frank-question for the DFA side**:
the "misnomer" 256-byte table's one-load cost is real on `.text` in both
directions this STEP 0 can check without a stopwatch — more code AND more
`.rodata` than either alternative, at both a 4-site and an 8-site scale.
Whether that one load is nonetheless faster per byte scanned (the
LATENCY argument the code's own comment makes: "the load is
VALUE-addressed... the dependency-chain property... is intact") is exactly
the number the timing run has to supply; nothing here settles it.

## 5. Family D — the shared atom table at N=16 (crossover check)

Pattern `abcdefghijklmnop` under `-i --engine=vm`: 16 distinct two-member
classes, chosen to sit above the plan row's own stated crossover ("wins
above ~10 bitmap classes"). `atoms[]` computed from each byte's SIGNATURE
(the set of classes containing it) — 16 live signatures plus the dead one,
17 atoms, comfortably under the 64-atom ceiling the design allows.

**Correctness**: `abcdefghijklmnop` (match 0 16), `ABCDEFGHIJKLMNOP`
(match 0 16), `AbCdEfGhIjKlMnOp` (match 0 16), `xyz` (nomatch). All three
twins agree.

**Size**, `gcc -O2 -c`:

| twin | .text | .rodata | table count |
|---|---|---|---|
| `base` (bit array) | 6,498 | 512 B (16×32) | 16 tables |
| `table` (256B/site) | 8,338 | 4,096 B (16×256) | 16 tables |
| `atom` (shared) | **3,818** | **256 B** | **1 table** (+16×8B inline masks) |

**This is the sharpest finding in the note.** At N=16 the shared atom table
is not a space-for-time trade at all on the axis measured here — it is
SMALLER on `.text` than both alternatives (41% smaller than `base`, 54%
smaller than `table`) as well as on `.rodata` (16× smaller than `table`,
2× smaller than `base`). The plan row's own framing ("two dependent loads
+ shift + and vs today's one load + shift + and... if it costs time, it is
a SPACE-PRIORITIZED choice") assumed the atom form is a size win bought
with more instructions; on `.text` bytes at N=16 it is not costing
anything to buy — it looks like a pure win on the one axis measured here.
**The likely mechanism (not verified by disassembly in this pass): the 16
independent `subject[scan_position]` bitmap loads cannot share code between
sites (16 different 32-byte tables, 16 different test expressions), while
16 atom-mask tests share the SAME `atoms[subject[scan_position]]`
subexpression and differ only in which mask constant they shift — a
compiler win `vm_cls_test`'s per-site emission cannot see today.** This
needs the ns/byte number before it changes anything, and it needs a real
disassembly read to confirm the mechanism rather than the size numbers
alone — flagged for the follow-up rather than asserted here.

## 6. What is owed, and to whom

**Timing, all four families, §1's protocol, on a quiet box post-`.lift`.**
Nothing in this note is a speed claim; every ranking above is `.text`/
`.rodata` bytes only. In particular:

- Family A's `fold` win and family D's `atom` win are BOTH size wins
  measured here; whether either is ALSO a speed win (or a speed loss the
  size win doesn't justify) is untested.
- Family C's `range`/`fold` vs `bitmap` split is the one this STEP 0's own
  charter cites the code comment's LATENCY argument against: a
  value-addressed one-load table might still win ns/byte even after losing
  on both size axes here. That argument is exactly what needs a number.
- Family B's `general` `rangecmp` (a near-wash on `.text`) is the cell most
  likely to flip under timing, since a 4-term OR chain has more branches
  than a single table load even where it is not larger in bytes.

**A disassembly read of family D's `atom` twin**, to confirm or refute the
CSE mechanism §5 proposes rather than infer it from `.text` bytes alone.

**A witness whose scan-edge classes are NOT a case-fold pair**, to separate
`range` from `fold` in family C — every site in both of this note's DFA
witnesses happens to be exactly `{c, c^0x20}`, so `range` and `fold`
measure the same shape twice there. `[FORM-CHAR]`'s own `ascii-fold` axis
would need a scan edge over an arbitrary disjoint set (not from
caselessness) to know whether `range`'s OR-of-runs generalizes as cheaply.

**The recommendation this STEP 0 can support before timing**: `table`
(family A/B/C/D's 256-byte-per-site form) is not looking like a candidate
to build ANYWHERE measured here — it lost on `.text` at every scale in
every family, and loses on `.rodata` everywhere except being tied with
nothing. If the timing run reverses that (the value-addressed-load latency
argument holding up), that would be the finding worth widely reporting,
because it would mean this STEP 0's `.text`/`.rodata` numbers are the wrong
axis to have led with. `fold` (family A) and `atom` at N≥16 (family D) are
the two candidates worth carrying into a real build IF the timing agrees
with the size numbers; `atom`'s crossover point (is N=16 actually near
where it starts winning, or does it win even lower?) is unmeasured — this
note built one point above the plan row's ~10-class estimate, not a curve.

## 7. Disclosure

Nothing from injected context shaped a decision beyond what the brief
itself specified. The choice of `ci-256` as family C's real-scale witness,
the small witness pattern `(?i)a{2,40}Z`, family B's two patterns and
family D's N=16 pattern were all chosen by this lane to satisfy the brief's
own descriptions (`ci-256` named explicitly; the others match the shapes
the brief names — "a general class `[a-zA-Z0-9_]` and a sparse class
`[aeiou]`", "a many-class VM artifact (csv/loglines shapes)" generalized to
a synthetic 16-class caseless chain once the loglines corpus patterns
turned out not to carry many DISTINCT bitmap-class sites in one artifact —
`csv5.rx`/`kv-quoted.rx`/`stack-frame.rx` were read and none exceeds a
handful of classes, so the ~10-class crossover point needed a constructed
witness to reach at all). No `src/`, `tests/`, or `docs/spec/` file was
read from `main` or `pcrec-bench` beyond what is cited above. The four
Python transforms (`twin_A.py`/`twin_B.py`/`twin_C.py`/`twin_D.py`) plus
their generation and check harness (`gen_base.sh`, `check_twins.sh`,
`sizes.sh`, `Makefile`) are committed at `studies/form_char_twins/` per the
manager's ruling that a scratch-only deliverable dies with the session —
see that directory's own `README.md`/`CLAUDE.md` for the reproduction
recipe and `results/twin_sizes.tsv` for this note's size tables in raw
form. `make check` there reproduces every correctness cell above (46/46
agreed); `make sizes` reproduces every `.text`/`.rodata` number.
