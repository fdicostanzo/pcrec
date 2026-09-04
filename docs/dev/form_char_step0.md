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
owed for (b) and for (a) on the general/many-class VM class sites — **but
question (a) for the CASELESS LITERAL CHAIN specifically (family A) is
answered without a stopwatch**: a `gcc -O2 -S` check (§2) shows every
fold-pair spelling compiles to identical branchless code with no load at
all, so `table`'s latency argument has nothing to beat there.

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

**The `fold`-vs-`bitarray`/`table` question is CLOSED, not merely
size-favored, and a `gcc -O2 -S` check settles it without a stopwatch.**
Three spellings of the caseless-letter test — `c=='a' || c=='A'` (the
`||` shape `base`'s bit-array test reduces to after the `& 1` masking),
`(c=='a') | (c=='A')` (the bitwise-or shape) and `(c|0x20)=='a'` (`fold`'s
own shape) — compile to the IDENTICAL instruction sequence:

```
andl $-33, %edi   # (or/fold uses `orl $32`)
xorl %eax, %eax
cmpb $65, %dil    # (fold compares $97 -- the lowercase constant)
sete %al
```

One mask op, one compare, one `sete`, NO LOAD, NO BRANCH — `studies/
form_char_twins/asm_evidence.c`, reproducible via `make asm`
(`results/three_spellings.s`, committed). There is therefore no load for
`table`'s one-load LATENCY argument to beat on a fold-pair site: `fold`'s
code has no load to begin with. The open "could a value-addressed load
still win despite losing on size" question this STEP 0's charter poses
does NOT apply to family A — it is closed here, on `.text` evidence alone,
in `fold`'s favor. It DOES still apply to family B (§3) and family D
(§5), where the non-table alternative (the bit array, `rangecmp`) reads
from memory too. `test_nonpair` (`c=='a' || c=='z'`, not a fold pair) is
the control: still branchless, but `cmpb $97; sete; cmpb $122; sete; orl`
— a longer, heavier chain, and exactly the shape family C's `nonpair`
witness (§4) measures on the DFA scan edge.

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

**`nonpair` witness**: `[ace]{2,40}Z` under `--engine=dfa --no-captures` —
the same skeleton as the small witness, but the scanned class is a
3-member set (`{a,c,e}`) that is NOT a case-fold pair by construction, so
`fold_expr`'s fallback engages: on this witness `fold`'s emitted text is
`range`'s own OR-of-runs, VERBATIM. This is the control §6 of the previous
draft of this note flagged as missing.

**Correctness**: small pattern on `"aaZ"` (match 0 3), `"AAaaAAaaZ"` (match
0 9), `"aZ"` (nomatch — below `{2,40}`'s floor), `"bbZ"` (nomatch);
`nonpair` on `"aceaceZ"` (match 0 7), `"aZ"` (nomatch), `"bbbZ"` (nomatch);
ci-256 on four sampled words in mixed case (`dybf`/`DYBF`/`DyBf`,
`LIYKXUH`, all match) plus a miss (`notaword`, nomatch). All twins agree
on every cell (52/52 across the whole note, `studies/form_char_twins`'
`make check`).

**Size**, `gcc -O2 -c`:

| witness | twin | .text | diff lines vs base |
|---|---|---|---|
| small (4 sites, fold pair) | `base` (bitmap) | 4,585 | — |
| small | `range` | 3,473 | 88 |
| small | `fold` | **3,425** | 88 |
| nonpair (4 sites, NOT a fold pair) | `base` (bitmap) | 4,585 | — |
| nonpair | `range` | 3,649 | 88 |
| nonpair | `fold` | 3,649 (byte-identical object to `range`) | 88 |
| ci-256 (8 sites, fold pairs) | `base` (bitmap) | 284,744 | — |
| ci-256 | `range` | 282,536 | 176 |
| ci-256 | `fold` | **282,488** | 176 |

**The `nonpair` witness is the separation the earlier draft of this note
was missing, and it confirms the fallback discipline rather than finding a
new effect**: `range` and `fold` compile to LITERALLY the same object
(`3,649` bytes both, `diff <(objdump -d range) <(objdump -d fold)` empty)
because a non-fold-pair site makes `fold_expr` fall back to `range_expr`'s
own construction — there is nothing for `fold` to do differently. On the
FOLD-PAIR witnesses (`small`, `ci-256`) the two DO diverge, by a small but
real and consistent margin (48 bytes over 4 sites = 12 B/site on `small`;
48 bytes over 8 sites = 6 B/site on `ci-256`) — `fold`'s single
mask-then-compare (§2's asm evidence: `and/or; cmp; sete`, one compare)
against `range`'s OR of two singleton compares (`cmp; sete; cmp; sete;
or`, per §2's `test_nonpair` control). This is the real, if modest,
divergence a genuine ascii-fold shape buys over the general range form —
an earlier draft of this note called the two "within noise of each other"
on the strength of the fold-pair witnesses alone, which understated a
small but reproducible and now compiler-explained effect.

The 256-byte table body costs real code size at every scale measured: 24%
(small) / 20% (nonpair) more `.text` than `range`, 0.79-0.80% more on
`ci-256` (8 sites, but the artifact is 990 KB total and the scan-edge
machinery is a small fraction of it). What the table form ALSO removes
from `.rodata`: 4×256 = 1,024 B (small, nonpair) / 8×256 = 2,048 B
(ci-256) that `range`/`fold` need none of.

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

**Timing on a quiet box post-`.lift`, §1's protocol — but SCOPED now, not
all four families equally.** The `gcc -O2 -S` compiler-equivalence check
(§2) closes family A's speed question without a stopwatch: every fold-pair
spelling (`||`, `|`, the ascii-fold compare) compiles branchless with NO
LOAD, so there is nothing for `table`'s one-load latency to beat there.
What remains genuinely open:

- **Family B**: `table` vs the bit array on a general/sparse VM class, and
  `rangecmp` vs the bit array — BOTH real alternatives here read from
  memory (`rx_class_bitmapN`/`rx_scan_table0` are tables, not compile-time
  constants), so the size-only ranking could still flip. `general`'s
  `rangecmp` (a near-wash on `.text`, +2.8%) is the cell most likely to
  move, since a 4-term OR chain has more branches than a single table load
  even where it is not larger in bytes.
- **Family C**: `table` (the "misnomer" 256-byte scan-edge body) vs
  `range`/`fold` — the code's own LATENCY argument ("the load is
  VALUE-addressed... the dependency-chain property... is intact") is
  exactly the number this needs; nothing size-only settles it, and unlike
  family A the table form here IS the one genuine load among three real
  alternatives.
- **Family D**: the atom table's two dependent loads (`atoms[byte]`, then
  `mask >> that`) vs the bit array's one load+shift+and — the plan row's
  own framing (two loads costs more) is what §5's `.text` numbers already
  contradict at N=16, so timing is what would either confirm the apparent
  free win or explain why it is not free at runtime despite being free in
  bytes.

**A disassembly read of family D's `atom` twin**, to confirm or refute the
CSE mechanism §5 proposes rather than infer it from `.text` bytes alone.

**DELIVERED since the first draft of this note**: a witness whose
scan-edge classes are NOT a case-fold pair (family C's `nonpair`,
`[ace]{2,40}Z`) — it separates `range` from `fold` by CONFIRMING the
fallback discipline (byte-identical objects when the site is not a fold
pair) rather than by finding new divergence, and its existence is what let
the fold-pair witnesses' own small, real `range`/`fold` gap (§4's revised
reading — the earlier draft called it "noise") get correctly attributed to
`fold`'s specialized shape rather than dismissed. `studies/form_char_twins/`'s `make check`/`sizes`/`asm`
reproduces all of §2's and §4's numbers, including this witness.

**The recommendation this STEP 0 can support before timing**: `table`
(every family's 256-byte-per-site form) is not looking like a candidate to
build ANYWHERE measured here — it lost on `.text` at every scale in every
family, and loses on `.rodata` everywhere except being tied with nothing.
Family A's `fold` win is no longer conditional on timing at all — the
compiler evidence closes it — so `fold` is ready to carry into a real
build on its own merits, pending only the ordinary review a `src/` change
gets. `atom` at N≥16 (family D) is the second candidate, still contingent
on the timing run and the disassembly read confirming its apparent
zero-cost win is real rather than an artifact of these particular
witnesses; `atom`'s crossover point (is N=16 actually near where it starts
winning, or does it win even lower?) is unmeasured — this note built one
point above the plan row's ~10-class estimate, not a curve. Family B and
C's rankings stay genuinely undecided pending timing, per the scoped list
above — table vs range vs fold on the scan edge is exactly the case where
the LATENCY argument that closed family A has NOT been closed.

## 7. Disclosure

Nothing from injected context shaped a decision beyond what the brief
itself specified, with one addition: the manager (relaying a question of
Frank's) supplied the finding that gcc folds the three fold-pair spellings
to identical branchless code and asked for it to be recorded, plus the
framing that the "one-load latency could still win" argument therefore
scopes to family B/D's `table`/`atom` comparisons rather than family A's
`fold`. This lane VERIFIED that claim directly (`gcc -O2 -S` on
`asm_evidence.c`, §2) rather than taking it on faith, and built the
`nonpair` witness (§4) the same message asked for — both are now part of
the committed deliverable rather than a note-only addendum. The choice of
`ci-256` as family C's real-scale witness, the small and `nonpair` witness
patterns, family B's two patterns and family D's N=16 pattern were all
chosen by this lane to satisfy the brief's own descriptions (`ci-256` named explicitly; the others match the shapes
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

## 8. Timing (2026-09-04, post-lift)

Run after `.lift`, on the box once load1 fell under the gate. Protocol per
§1 / §6, copied from `docs/dev/lanes/isl1_report.md` §12: `<prefix>_search`
in a find-all loop (`studies/form_char_twins/bench_twin.c`, modelled on
`studies/scan_edge_ladder/bench.c`) over a 131,072-byte subject built per
family, `N = 11` rounds, arms INTERLEAVED round by round, `/proc/loadavg`'s
1-minute figure gating at `< 0.5` (REFUSE and wait, never caveat — the
harness waited twice, 60 s apart, before the box went quiet), median ns/call
and ns/byte reported with the per-round range, every round's answer
(hit count + a position/length checksum, not sampled) compared against that
family's `base` arm. **Zero mismatches across all 132 cells** (4 families ×
11 rounds × 3 arms); all 11 rounds of all 4 families landed at a steady
`load1 = 0.39`. Family A is not re-measured here — §2's `gcc -O2 -S` check
already closed its speed question without a stopwatch.

Driver and orchestration: `studies/form_char_twins/bench_twin.c` +
`time_twins.sh` (committed). Binaries are compiled against
`timing_base/*.c` — the SAME `pcrec` invocations as `gen_base.sh` (see that
script), but WITHOUT `--emit-main`, so `bench_twin.c` supplies its own
`main()` and find-all loop rather than fighting the artifact's own
single-call `main`; `timing_twins/*.c` are the same `twin_B.py`/`twin_C.py`/
`twin_D.py` transforms run against those no-main bases. Both directories are
gitignored (regenerate byte-for-byte from `build/pcrec` + the committed
transforms, same discipline as `base/`/`twins/`). Raw per-round rows:
`results/timing_raw.tsv`; medians/ranges: `results/timing_summary.tsv`.
Subjects (`studies/form_char_twins/subjects/`, gitignored, regenerate from
the Python generator embedded in this session's `time_twins.sh` history —
not itself committed as a separate script for time reasons, see "what
remains unmeasured" below) are 131,072 bytes each: family B a
natural-language-ish mixed-case/digit/punctuation text (both `[a-zA-Z0-9_]`
and `[aeiou]` run over the same text); family C a digit background with
periodic `a`/`A`-runs of length 2-40 followed by `Z`/`z` (misses AND hits,
unlike the compile-only correctness subjects); family D a digit background
with periodic full `abcdefghijklmnop` hits (mixed case) and periodic
right-prefix near-misses (4-12 correct letters then a digit break), to
stress the chain beyond bare entry/skip. No CPU pinning (`taskset`) was
used, unlike `scan_edge_ladder`'s driver — flagged as a real source of the
variance below, not smoothed over.

### 8.1 Family B — general/sparse VM class (bit array vs table vs range compares)

| pattern | arm | median ns/call | range | median ns/byte | range | rounds | load1 |
|---|---|---|---|---|---|---|---|
| general `[a-zA-Z0-9_]` | base (bitmap) | 9.736 | [7.269, 10.368] | 7.8789 | [5.8826, 8.3897] | 11 | 0.39 |
| general | table | 9.378 | [9.038, 9.950] | 7.5890 | [7.3136, 8.0514] | 11 | 0.39 |
| general | rangecmp | 9.164 | [5.297, 10.012] | 7.4160 | [4.2869, 8.1021] | 11 | 0.39 |
| sparse `[aeiou]` | base (bitmap) | 32.524 | [15.771, 36.463] | 6.1507 | [2.9824, 6.8955] | 11 | 0.39 |
| sparse | table | 31.460 | [14.277, 34.069] | 5.9495 | [2.7000, 6.4427] | 11 | 0.39 |
| sparse | rangecmp | 36.234 | [19.088, 40.325] | 6.8521 | [3.6097, 7.6259] | 11 | 0.39 |

**general is a wash within the range** — all three medians sit within 6% of
each other and their ranges overlap almost completely (rangecmp's own range
dips to 5.297, below every other arm's floor, on what reads as a
frequency-scaling outlier rather than a real fast round); the size-only
ranking (`rangecmp` ≈ `base` ≪ `table` on `.text`) does not clearly reverse
at runtime, but it does not confirm either — `table` is not measurably
punished for its extra code and 8× the `.rodata`. **sparse instead
CONTRADICTS the note's tentative size-based prediction**: `rangecmp`, the
form that was smallest on `.text` (-5.6% vs base), is the clear runtime
LOSER here (15% slower than `table`, 11% slower than `base`, highest of the
three arms in 8 of 11 rounds), while `table` — worst on both size axes for
this family — is at least tied with (nominally faster than) the bit array.
A 4-term-vs-5-term OR-of-compares chain costs more at runtime on a sparse
class than either a load-based form, even where it costs fewer bytes.

### 8.2 Family C — the DFA scan edge, small witness (bitmap vs range vs fold)

| witness | arm | median ns/call | range | median ns/byte | range | rounds | load1 |
|---|---|---|---|---|---|---|---|
| small `(?i)a{2,40}Z` | base (bitmap/"table") | 375.706 | [369.908, 419.201] | 1.3042 | [1.2841, 1.4552] | 11 | 0.39 |
| small | range | 378.552 | [372.208, 427.356] | 1.3141 | [1.2921, 1.4835] | 11 | 0.39 |
| small | fold | 376.800 | [370.487, 402.696] | 1.3080 | [1.2861, 1.3979] | 11 | 0.39 |

**A wash, cleanly.** All three medians sit within 0.8% of each other and
every range overlaps every other range almost end to end. The scan edge's
own header comment's LATENCY argument ("the load is VALUE-addressed... the
dependency-chain property... is intact") is not confirmed as a real win
here, but it is not refuted either — `base`'s 256-byte table, which lost
decisively on both `.text` (+24%) and `.rodata` (+1,024 B) against
`range`/`fold` in §4, is NOT a measurable runtime loser on this witness. At
real scale (`ci-256`, 8 fold-pair sites) and on the `nonpair` (non-fold-pair,
range≡fold) witness, timing is still owed — see §8.4.

### 8.3 Family D — N=16 shared atom table (bit array vs table vs atom)

| witness | arm | median ns/call | range | median ns/byte | range | rounds | load1 |
|---|---|---|---|---|---|---|---|
| N=16 `abcdefghijklmnop` -i | base (bit array) | 1147.433 | [635.645, 1405.290] | 2.6963 | [1.4937, 3.3022] | 11 | 0.39 |
| N=16 | table (256B/site) | 874.930 | [485.622, 890.860] | 2.0560 | [1.1411, 2.0934] | 11 | 0.39 |
| N=16 | atom (shared) | 885.042 | [481.214, 1069.307] | 2.0797 | [1.1308, 2.5127] | 11 | 0.39 |

**The sharpest and noisiest result of the run.** `table` and `atom` are
tied with each other (within 1.2% median, overlapping ranges) and BOTH are
~24% faster than the bit array's median — 8 of 11 rounds show this cleanly
(`table`/`atom` clustered 870-890, `base` clustered 1140-1156); rounds 6, 8
and 9 swing wide on one or two arms at a time (e.g. round 8: all three drop
together; round 6: `atom` jumps to 1065 while `base` drops to 646) in a
pattern consistent with CPU frequency-state noise this run did not pin
against (no `taskset` — see the caveat above), not with a real per-round
reversal of which arm wins. **This is the timing question §6 named as open
for family D, and it resolves against the note's blanket "table is not a
candidate anywhere" line**: `table` loses decisively on BOTH size axes
here (§5: +28% `.text`, 16× `.rodata` vs `atom`) yet is a runtime dead heat
with `atom` and a clear win over `base` — the one-load latency argument
DOES win here, it is just that `atom`'s shared table gets the same latency
win at a fraction of the size cost, which is the stronger and more
actionable version of the same finding. `atom`'s §5 "apparent free win" on
size is now also a free win on time at N=16: it matches `table`'s speed
while using 16× less `.rodata` and costing 41% less `.text` than `base`.

### 8.4 What remains unmeasured

Hard stop (17:30 EDT) reached before these could run:

- **Family C at real scale** (`ci-256`, 8 fold-pair sites) and the
  `nonpair` witness (`table` vs `range`/`fold` where the alternatives are
  byte-identical to each other) — both twins and binaries were built during
  `make base`/`make twins` for the size study but were not wired into
  `time_twins.sh`'s family list for time reasons; the script's
  `FAM_SUBJ`/`FAM_ARMS` tables are the two lines to add.
- **CPU pinning** (`taskset -c N`, as `scan_edge_ladder`'s driver does) —
  family D's per-round swings (§8.3) are the direct evidence this would
  tighten the range and likely sharpen an already-clear result rather than
  change its direction.
- **A disassembly read of family D's `atom` twin** to confirm (not just
  infer from `.text` bytes and now runtime parity) the CSE mechanism §5
  proposes for why the shared table costs nothing on either axis.
- **The subject-generator script itself** was not committed as a separate
  file — it was written inline for this run (see §1's note above) rather
  than as a fifth committed `.py`/`.sh`; regenerating the exact three
  subjects requires re-deriving them from this section's description
  rather than re-running a checked-in generator. Flagged as a gap in this
  note's own reproducibility, not hidden.

**Revised recommendation.** Family A (`fold`) is unchanged — closed on
compiler evidence alone. Family D's `atom` graduates from "contingent on
timing" to **supported by both axes measured**: smaller on `.text` and
`.rodata` AND tied with the fastest alternative at runtime, at N=16.
Family B's `table` is still not a candidate on size grounds it never
overcomes (§3), but §8.1's `general` cell shows it is at least not a
runtime loser either — the recommendation against building it stands on
size alone, unweakened but also not reinforced by time. Family B's
`rangecmp` on a sparse/few-singleton class is WEAKER than the size table
alone suggested (§8.1) — a real, if narrow, caution against generalizing
"fewer bytes → faster" to the range-compare form without checking the
compare count. Family C stays genuinely open pending the real-scale and
`nonpair` runs (§8.4).
