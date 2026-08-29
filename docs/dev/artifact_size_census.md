# [ART-SIZE] STEP 1 — MEASUREMENT: the artifact-size census

Lane `artsize`, 2026-08-28, branch `lane/artsize`. Measurement only: nothing
under `src/` or `tests/` changed. Report shape follows
`docs/dev/opt3_dfa_scan_measurement.md` per the charter. Frank's concern,
verbatim: *"I'm concerned about the 2 MB VM artifact. If our compiled
artifacts are that big no one will want to use them. It deserves an
investigation as well as a size vs performance tension that kicks in at
some size."*

## 0. The answer in six lines

1. Over pcrec's own corpus (2,772 distinct patterns: 2,758 from
   `tests/**/*.rxt` + 14 pcrec-bench patterns), the artifact a user actually
   ships (`.o` at `-O2`) is **small and well-behaved** — median 6,760 bytes,
   p99 14,364 bytes — and gcc compile time is **nowhere near D45's 10 s
   budget** (max 6.995 s CPU, one pattern, everything else under 0.5 s).
2. The 2 MB VM artifact Frank is worried about **is not in this
   population**. It is the fuzz gate's seed-1 witness — deliberately
   adversarial, found by fuzzing, not by any pattern anyone would write —
   and it sits roughly **3x above the worst thing the shipped corpus
   contains** (675,555 B source / 202,912 B `.o` for `((a)|ab){4000}c`,
   the corpus's own largest artifact, against the witness's 2,015,594 B
   source / 503,344 B `.o` — self-contained form, §6 has a note on a
   mid-lane methodology correction to this source-byte figure). The
   corpus's outliers are already the SAME MECHANISM as the
   witness (bounded-repeat body replication under the counter rung), just
   milder — so the witness is not a different problem, it is the far tail
   of the one this census measures throughout.
3. **Source bytes track `.o` bytes almost perfectly** once comments are
   excluded (r = 0.99 for program+tables vs `.o`; r = 0.97 for whole source
   vs `.o`; r = 0.43 for comments alone vs `.o`) — the `.o`/source ratio is
   a near-constant **~17%** across the whole corpus (median 0.171, p10-p90
   0.153-0.194). [M6-READ]'s prose does inflate SOURCE bytes (42% of the
   corpus's total source bytes, aggregate) but the correlation data says it
   is riding along with pattern complexity, not driving `.o` size on its
   own — a size term that wants the number a user ships should price
   program+tables, not source bytes.
4. Every top-20 outlier by both `.o` size and gcc time is the **same
   mechanism**: a bounded or exact-count repeat over an alternation with
   more than one branch, forcing the FRAMES-BOUNDED counter rung (never the
   cheaper CURSOR or REVDET rungs), which replicates the loop body once per
   `--unroll=K` chunk. `((a)|ab){4000}c` (675,555 B source, 202,912 B
   `.o`, the corpus's largest) and the R1 A-3 nested-repeat family
   (`((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,N}(){2,3}){1,2}){2,3}`, worst
   gcc time in the corpus at 6.995 s CPU for N=8) anchor the top of both
   lists.
5. **§8's tension curves find THREE separate levers, not one, each with a
   different trade.** `--unroll=1` costs no measured throughput — and on
   the N=8 nested-repeat outlier, measures FASTER — on nested-repeat
   patterns, but is nearly useless on single-level large-count ones — the
   witness (17x smaller, 54x faster to compile, no speed loss on its own
   short subjects) and the corpus's own nested-repeat outliers (75-79%
   smaller, 12x faster to compile) are where it pays; `((a)|ab)
   {4000}c`-shaped patterns barely move (1-3%). `-fno-premul-table` is
   still the well-behaved, already-understood [OPT-3] SIZE lever
   (~22-25% smaller, load-independent) — its throughput side is not: the
   quiet-box re-run reads a direction flip on 2 of 5 outlier patterns
   (faster without the table, not slower), against the loaded run's
   clean ~20-34%-slower-on-4/5 story (§8 item 2). **`--engine=vm` is
   Frank's own "tension that
   kicks in at some size," measured directly**: dropping the hybrid DFA
   prefilter shrinks `.o` to 4-9% of default on prefiltered patterns — the
   single biggest size lever found on any non-witness artifact — at up to
   a measured 173,580x throughput cost on the failing path (quiet-box
   run, §8; loaded vs quiet: 359,000x → 173,580x — the effect held, the
   exact magnitude moved by about half), because the prefilter
   IS the size AND the speed: the same forward+reverse DFA machine that
   costs the bytes is what lets a non-matching subject be dismissed in
   O(1) instead of backtracked through in full.
6. **The census finds no gcc-time or resource risk anywhere in the shipped
   corpus** — every one of 2,488 successful compiles finished with verdict
   `ok` (0 timeouts, 0 CPU-budget kills). The risk this plan row exists to
   name is entirely in patterns nobody has written yet (the fuzz gate found
   the witness; ordinary corpus authorship has not come close). That is
   itself a design input: STEP 2's cap needs to bind on a measured
   THRESHOLD between "worst thing the corpus contains" (675 KB source) and
   "worst thing fuzzing found" (2 MB), not on today's corpus max.

## 1. Method

- Box: AMD Ryzen 5 1600, 12 cores (same box `opt3_dfa_scan_measurement.md`
  used). `gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0`.
- Population: every distinct `pattern <regex>` line under `tests/**/*.rxt`
  (2,758, `LC_ALL=C`-equivalent — Python's own string comparison is
  codepoint order and needs no locale coercion; cross-checked against
  `grep -h '^pattern ' tests/**/*.rxt | LC_ALL=C sort -u | wc -l` which
  agrees exactly at 2,758) plus every pcrec-bench pattern file under
  `bench/email/patterns/*.rx` and `bench/loglines/patterns/*.rx` (14,
  read-only), for **2,772 total**. Compiled with `build/pcrec -p rx
  --features all -o - -- '<pattern>'` (the self-contained single-file
  form, used consistently for every measurement in this report) — auto
  engine selection, no other flags. NOT byte-identical to the split
  `.c`+`.h` form's combined bytes (verified directly on the witness, §6:
  2,015,594 self-contained vs 2,016,088 combined split-form, a 494-byte
  difference — header-guard/`#include` boilerplate the two forms spell
  differently) — an earlier draft of this report claimed byte-identity
  without having checked it; §6 records the real mid-lane bug that check
  would have caught sooner.
- **Refused patterns are counted, not skipped**: 284 of 2,772 (10.2%)
  refuse to compile. Classified by diagnostic: 283 are ordinary `perr`
  negative-test rejections already in the corpus for other reasons
  (variable-length lookbehind, malformed quantifiers, unresolvable named
  backreferences, ...) and exactly 1 is a `requires module` gap — **none
  are size- or budget-related refusals**. §3's population is therefore the
  2,488 that compiled.
- Per-artifact record: source bytes; `.o` bytes from `gcc -O2 -std=gnu11
  -c` (the number a user ships) plus `size(1)`'s text/data/bss; gcc wall
  and CPU (process rusage via `os.wait4`, the same quantity
  `/usr/bin/time -f` reports, avoiding a second fork per compile over
  ~2,500 iterations); the D46 selection-fact stamps (`RX_ENGINE`,
  `RX_ENGINE_WHY`, `RX_VM_PREFILTER`, `RX_DFA_SCAN`, `RX_DFA_PREFILTER`,
  `RX_DFA_TABLE`, `RX_VM_RUNGS`, `RX_NCAPS`); and a byte ATTRIBUTION of the
  source by section (§5).
- **D45's own budget numbers, reused rather than re-derived**: gcc CPU
  budget 10 s soft (`RLIMIT_CPU`, `+30` s hard escalation), wall backstop
  60 s (matches `tests/lib/gen_timeout.sh`'s plain-axis `GENCPU`/
  `GENTIMEOUT` defaults exactly). pcrec's own invocation: 30 s wall plus a
  3 GiB `RLIMIT_AS` cap (mirrors `tests/resource`'s BINDING `ulimit -v`
  discipline — an unbinding limit is not a control), generous against
  `pcrec_timeout_secs`'s 20 s plain default since a census sweeps patterns
  nobody has pre-screened.
- Async, artifact-polled, never a blocking foreground run (Frank's
  standing orchestration rule): the full census ran under `setsid`,
  progress read from a log the driving session polled by content, not by
  `pgrep`/`ps` (`docs/dev/learnings.md` §6).
- Method used, NOT `scripts/watchdog` directly, for the per-pattern
  compiles: a `RLIMIT_CPU`+`RLIMIT_AS` `preexec_fn` and a bounded
  `os.wait4` poll loop inside the census script itself, because
  `watchdog`'s own measured per-call startup cost (~171 ms, `tests/lib/
  CLAUDE.md`'s K37 entry) would have added 2,772 x ~171 ms = ~8 minutes of
  pure overhead to a population where the legitimate cost per case is
  double-digit milliseconds — the identical "cheap by default, watchdog
  only where the hazard is real" tradeoff `pcrec_run` already makes for
  the harness's own bare compiler calls. `scripts/watchdog` WAS used
  directly for the one pattern known in advance to be hostile (the
  witness, §8) and for the tension-curve deep dive (§8), where per-call
  counts are in the dozens, not thousands, and watchdog's RSS-tracking is
  worth its cost.
- Byte attribution derivation and its own validation: §5.
- Tension curves (§8): the witness plus the top 5 corpus patterns by `.o`
  size, each rebuilt under `--unroll=1`, `-fno-counter`,
  `-fno-splice-calls`, `-fno-premul-table` (skipped where the artifact has
  no DFA scan to deny — the witness's own `RX_VM_PREFILTER` is `none`, so
  it has none) and `--engine=vm`, measuring size AND throughput on a
  matching and a failing subject constructed per pattern, `taskset -c 3`,
  median of >= 5 trials, `load1` recorded on every row, waited down when
  above 2. Size/`.o`/gcc-time were measured in the first pass, at box
  `load1` 1.6-5.0 (another lane's sections were active throughout).
  Throughput (`match_us`/`fail_us`) was RE-MEASURED in a second pass on a
  quiet box (`load1` 0.13-1.2, 20:08-20:22 EDT, 2026-08-28) once the
  manager signaled that pass's contending union battery had cleared; §8's
  own status note carries the loaded-vs-quiet comparison.

## 2. Population and refusals

| | count |
|---|---|
| total patterns | 2,772 |
| compiled | 2,488 (89.8%) |
| refused | 284 (10.2%) |
| refused: ordinary `perr` rejection | 283 |
| refused: `requires module` | 1 |
| refused: size/budget-related | **0** |
| DFA engine | 999 |
| VM engine | 1,489 |
| VM with hybrid DFA prefilter | 1,262 |
| VM, no prefilter | 227 |
| gcc verdict `ok` | 2,488 / 2,488 (100%) |
| gcc verdict timeout/CPU-budget | 0 |

Refusal reasons, by frequency (leading diagnostic phrase; full breakdown in
the raw TSV):

| reason | count |
|---|---|
| quantifier does not follow a repeatable item | 67 |
| variable-length lookbehind not implemented | 38 |
| `\K` not allowed inside a lookaround | 15 |
| relative reference of zero | 14 |
| duplicate named subpattern | 13 |
| missing closing `)` for group | 12 |
| number too big in `{m,n}` | 10 |
| multiple quantifiers on the same atom | 9 |
| (23 more reasons, 1-6 occurrences each) | 106 |

Every one of these is the corpus's own `tests/reject/`-style negative
material (malformed syntax, unresolvable references, unimplemented
constructs) — none of it says anything about artifact size, and the
population that matters for this census is the 2,488 that compiled.

## 3. Distributions

Source bytes, `.o` bytes (gcc `-O2 -c`), gcc CPU time — median / p90 / p99 /
max, split by engine (`n` = population size):

| metric | engine | n | median | p90 | p99 | max |
|---|---|---|---|---|---|---|
| source bytes | dfa | 999 | 27,621 | 31,145 | 45,249 | 110,252 |
| source bytes | vm | 1,489 | 45,158 | 51,109 | 71,663 | 675,555 |
| source bytes | **both** | 2,488 | 40,794 | 49,295 | 68,782 | 675,555 |
| `.o` bytes | dfa | 999 | 4,880 | 5,674 | 10,800 | 28,840 |
| `.o` bytes | vm | 1,489 | 7,272 | 8,589 | 15,164 | 202,912 |
| `.o` bytes | **both** | 2,488 | 6,760 | 8,290 | 14,364 | 202,912 |
| gcc CPU (ms) | dfa | 999 | 72 | 87 | 106 | 113 |
| gcc CPU (ms) | vm | 1,489 | 122 | 157 | 286 | 6,995 |
| gcc CPU (ms) | **both** | 2,488 | 109 | 145 | 262 | 6,995 |

D45's plain-axis CPU budget is **10,000 ms**. The single worst compile in
the whole corpus (6,995 ms, the nested-repeat state-explosion pattern, §4)
sits at **70% of budget** — the closest anything in the shipped corpus
comes to the wall D45 exists to enforce, and it is a deliberate stress
pattern (R1 A-3's family), not an ordinary regex. Every other pattern in
the corpus is under 500 ms.

**The `.o`/source ratio is a near-constant ~17% across both engines**:
DFA median 0.176 (p90 0.199), VM median 0.162 (p90 0.191). A DFA artifact's
source survives to `.o` slightly MORE completely than a VM one's — plausible
given the VM's [M6-READ] doc-comment budget per emitted primitive
(`RX_PUSH`/`RX_TRAIL`/`RX_CUT`/rung markers) is proportionally larger on a
typical (non-outlier) VM artifact than a DFA one's per-state comments.

`size(1)`'s own breakdown: every artifact in the corpus is `.data` 144
bytes flat (the D46/D46-ABI universal constant block) and `.bss` 0 —
100% of `.o` size variation is in `.text` (code) plus `.rodata` (tables,
folded into `.text`'s reported column by this box's `size` — no artifact
showed a nonzero `.data` beyond the flat 144, confirming tables are
`static const`, read-only, never mutable state, consistent with D19's
thread-safety audit).

## 4. Outliers

### Top 20 by `.o` size

| rank | id | `.o` | source | gcc CPU | engine | rungs | pattern |
|---|---|---|---|---|---|---|---|
| 1 | rxt-00127 | 202,912 | 675,555 | 307 ms | vm | 0x10 (FRAMES_BOUNDED) | `((a)\|ab){4000}c` |
| 2 | rxt-00143 | 128,144 | 486,362 | 218 ms | vm | 0x8 (FRAMES_UNBOUNDED) | `((a)\|bc){0,4000}d` |
| 3 | rxt-00118 | 107,952 | 409,082 | 286 ms | vm | 0x10 | `((a)\|ab){0,4000}c` |
| 4 | rxt-00030 | 103,392 | 371,434 | **6,995 ms** | vm | 0x17 (all five rungs) | `((?:(?:(?:[^a]{1,2}\|[^a]??\|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}` |
| 5 | rxt-00029 | 85,408 | 296,063 | 3,792 ms | vm | 0x7 | same family, N=6 |
| 6 | rxt-00117 | 64,152 | 247,545 | 360 ms | vm | 0x10 | `((a)\|ab){0,2047}c` |
| 7 | rxt-00028 | 60,336 | 216,923 | 2,318 ms | vm | 0x7 | same family, N=4 |
| 8 | rxt-00027 | 35,632 | 138,173 | 1,090 ms | vm | 0x7 | same family, N=2 |
| 9 | rxt-02471 | 28,840 | 110,252 | 82 ms | dfa | — | `a{1,2000}` |
| 10 | rxt-01345 | 28,320 | 115,483 | 412 ms | vm | 0x11 | `(a{10,20}){10,50}` |
| 11 | rxt-00203 | 26,456 | 109,260 | 254 ms | vm | 0x11 | `(1{0,30}?[^]abc][^abc]){8,8}0+\|a` |
| 12 | rxt-00119 | 25,624 | 109,215 | 289 ms | vm | 0x10 | `((a)\|ab){0,500}c` |
| 13 | rxt-01334 | 24,808 | 104,268 | 285 ms | vm | 0x11 | `(a{1,20}){1,50}` |
| 14 | bench-email-factored | 23,240 | 86,061 | 74 ms | dfa | — | the email specimen, subroutine-factored (`(?&atom)`/`(?&qchar)`/...) |
| 15 | rxt-00460 | 23,232 | 86,061 | 79 ms | dfa | — | the email specimen, factored (corpus's own copy of the bench pattern) |
| 16 | rxt-00239 | 23,208 | 86,007 | 87 ms | dfa | — | `(?(DEFINE)...)` form of the same specimen |
| 17 | bench-email-orig | 23,072 | 85,394 | 77 ms | dfa | — | the email specimen, hand-inlined |
| 18 | rxt-00495 | 23,064 | 85,394 | 89 ms | dfa | — | corpus's own copy of the hand-inlined specimen |
| 19 | rxt-01311 | 17,736 | 76,657 | 124 ms | vm | 0x1 (CURSOR only) | `(ab){300}` |
| 20 | rxt-01616 | 17,048 | 65,892 | 77 ms | dfa | — | `[ab]{1000}` |

### Top 20 by gcc CPU time

| rank | id | gcc CPU | `.o` | source | rungs | pattern |
|---|---|---|---|---|---|---|
| 1 | rxt-00030 | **6,995 ms** | 103,392 | 371,434 | 0x17 | nested-repeat family, N=8 |
| 2 | rxt-00029 | 3,792 ms | 85,408 | 296,063 | 0x7 | nested-repeat family, N=6 |
| 3 | rxt-00028 | 2,318 ms | 60,336 | 216,923 | 0x7 | nested-repeat family, N=4 |
| 4 | rxt-00027 | 1,090 ms | 35,632 | 138,173 | 0x7 | nested-repeat family, N=2 |
| 5 | rxt-01345 | 412 ms | 28,320 | 115,483 | 0x11 | `(a{10,20}){10,50}` |
| 6 | rxt-00123 | 372 ms | 15,048 | 74,585 | 0x10 | `((a)\|ab){11,19}c` |
| 7 | rxt-00117 | 360 ms | 64,152 | 247,545 | 0x10 | `((a)\|ab){0,2047}c` |
| 8 | rxt-00129 | 324 ms | 14,264 | 71,255 | 0x10 | `((a)\|ab){9,17}c` |
| 9 | rxt-00128 | 319 ms | 14,304 | 71,265 | 0x10 | `((a)\|ab){9,17}?c` (lazy) |
| 10 | rxt-00127 | 307 ms | 202,912 | 675,555 | 0x10 | `((a)\|ab){4000}c` |
| 11 | rxt-00113 | 303 ms | 14,232 | 68,658 | 0x10 | `((a)\|ab){0,15}c` |
| 12 | rxt-00202 | 302 ms | 13,040 | 56,287 | 0x11 | `(1{0,30}?[^]abc][^abc]){28,30}0+\|a` |
| 13 | rxt-01408 | 298 ms | 12,808 | 66,328 | 0x11 | `(x(?:ab){2,4}){0,12}c` |
| 14 | rxt-00110 | 297 ms | 16,016 | 75,277 | 0x10 | `((a)\|ab){0,100}c` |
| 15 | rxt-00119 | 289 ms | 25,624 | 109,215 | 0x10 | `((a)\|ab){0,500}c` |
| 16 | rxt-00118 | 286 ms | 107,952 | 409,082 | 0x10 | `((a)\|ab){0,4000}c` |
| 17 | rxt-01334 | 285 ms | 24,808 | 104,268 | 0x11 | `(a{1,20}){1,50}` |
| 18 | rxt-01845 | 283 ms | 8,688 | 46,307 | 0x2 | `^((a\|b)(?1)?\2)$` (a recursion pattern, not counter-rung) |
| 19 | rxt-00149 | 276 ms | 12,984 | 65,474 | 0x10 | `((ab)\|b){0,12}b` |
| 20 | rxt-00112 | 270 ms | 12,760 | 63,758 | 0x10 | `((a)\|ab){0,12}c` |

Same population almost exactly — the nested-repeat state-explosion family
(rxt-00027..00030, R1 A-3's own stress shapes) occupies the top 4 by a wide
margin (6,995 / 3,792 / 2,318 / 1,090 ms), then a long run of `((a)|ab){N}c`
and `((a)|ab){N,M}c` variants at N in {9..2047} (270-360 ms each), all VM,
all FRAMES_BOUNDED or FRAMES_UNBOUNDED rung. The `.o`-size list and the
gcc-time list are the SAME outlier set reordered — no pattern is expensive
on one axis and cheap on the other in this corpus.

### Mechanism

Every single outlier is the plan row's own suspect, confirmed directly from
the stamps: **a bounded or exact-count repeat wrapping an alternation of
more than one branch, forced onto the FRAMES-BOUNDED or FRAMES-UNBOUNDED
counter rung** (`RX_VM_RUNGS` 0x10/0x8/0x11, never the cheap CURSOR-only
0x1 that a single-branch repeat like `(ab){300}` gets). The counter rung
(`src/gen/CLAUDE.md`'s [ENG-BREP] third rung) is what lets `{4000}` compile
at all rather than refusing at `PCREC_MAX_VM_REPEAT_COPIES` — but it still
emits **one body copy per `--unroll=K` chunk** (D47.2's calibration; the
default `K` is `PCREC_DEFAULT_UNROLL_K`, not the value the CLI's `--unroll=`
lets a caller pick), so an exact-4000 repeat still replicates its body
`4000/K` times. The nested-repeat family (rxt-00027..00030) MULTIPLIES this:
three levels of nesting (`{0,N}` inside `{1,2}` inside `{2,3}`) each
independently forces a rung selection, and K22's own documented hazard —
"a depth-40 tower of `{0,2}` has a maximum factor of 2 and replicates its
innermost body 2^40 times" — is exactly the shape N=8 sits closest to
before `PCREC_MAX_VM_REPLICATION_PRODUCT` would refuse it; that closeness
is why it is ALSO the worst gcc-time outlier (6,995 ms, 70% of D45's
budget) even though its `.o` (103,392 B) is smaller than `((a)|ab){4000}c`'s
— replication PRODUCT (which gcc has to parse and optimize) and final
emitted SIZE (after gcc's own folding) are related but not identical costs.

The two DFA outliers in the top 20 (`a{1,2000}`, `[ab]{1000}`, `[ab-only
100-2000]{N}`) are a different, milder mechanism: a DFA state count that
grows linearly with the bound (no alternation to force a rung choice at
all — these compile to a pure DFA), so their tables grow but nothing
replicates; they are smaller than the VM outliers by roughly an order of
magnitude at a comparable bound and are not size-vs-speed candidates in the
same sense (§8 does not include them — their tension is fully described by
`docs/design/premultiplied_dfa_table.md`'s own L1-residency gate, already
measured by [OPT-3]).

## 5. Byte attribution

### Method

Every line of the emitted source is assigned to exactly ONE of five
buckets by a single-pass classifier reading the artifact's own comment
syntax, table-literal shape, and the function/symbol NAMES the emitter
itself chose ([M6-READ]'s naming convention) — never from a count the
compiler computes about the pattern:

- **prose** — `/* ... */` block comments and `//` line comments: the
  [M6-READ] doc-comments, the orientation block, section banners,
  per-node commentary (`// optional copy (N remaining)` on every replicated
  VM body). No `--emit-ir` listing is ever embedded in a plain `-o -`
  build, so this bucket is comment TEXT only for this census.
- **tables** — `static const TYPE NAME[...] = { ... };` array literals
  (DFA transition/accept/class/premultiplied tables and any other
  read-only data array), wherever they appear — INCLUDING nested inside a
  scan function's own body, which is where every DFA table this emitter
  writes actually lives (`emit_dfa.c`'s tables are function-local
  `static const`, never file-scope).
- **program** — function bodies whose name is NOT one of [ENG-FORM]'s
  opaque-token accessor suffixes (`_step`/`_is_dead`/`_accepts`/
  `_accepts_class`/`_row`/`_view_live`/`_view_take`): the matcher functions
  proper (`<prefix>_search`/`_match`/`_match_caps`/`_info`/`_next_pos`, the
  DFA/VM scan bodies).
- **scaffold** — everything else with linkage or a declaration: `#define`
  macros (the D46 stamps, the D49 give-up codes, the operational macros
  `RX_TRAIL`/`RX_SET`/`RX_PUSH`/`RX_CUT`/`RX_CHARGE_WORK`), typedefs,
  struct definitions, the opaque-token accessor functions themselves, and
  blank/structural lines wherever they occur (top level or nested inside a
  function body).
- **main** — an `int main(...)` body, present only under `--emit-main`.
  Never exercised by this census: neither the main population (`-o -`,
  no `--emit-main`) nor §8's tension-curve builds (split `gen.c`/`gen.h`
  linked with `tests/bench/bdriver.c`, which supplies its own `main`)
  compile with it. The classifier still recognizes it (verified on a
  one-off `--emit-main` sample: 819 bytes correctly bucketed) so a future
  census that DOES use it needs no change here.

**Validated to sum to the file's own byte count on every artifact — 0
failures across all 2,488** (`attr_sum_ok` column). This is by
construction (every byte is claimed by exactly one bucket, never zero or
two), so the check is a bug-catcher, not a hope: it caught two real bugs
during this lane's own development: an off-by-one in the newline-byte
accounting, and — the more consequential one — a multi-line function-pointer
typedef that a naive regex mismatched as a body-bearing function
definition, which then silently folded EVERY nested comment and table
inside the enclosing "function" into the PROGRAM bucket rather than
recursing the same comment/table dispatch into it. Both are fixed in the
committed script (`docs/dev/artifact_size_census/census.py`); the second
was caught only by cross-checking the witness's attribution against an
independent measurement — see §6.

### Aggregate, across the whole corpus (2,488 artifacts, weighted by bytes)

| section | bytes | share |
|---|---|---|
| prose | 41,011,786 | **42.1%** |
| program | 27,079,671 | 27.8% |
| scaffold | 19,087,799 | 19.6% |
| tables | 10,337,043 | 10.6% |
| main | 0 | 0.0% |

**[M6-READ]'s prose IS the largest single bucket, on average** — the
readable-emission mandate (D-something's "the generated C is a first-class
deliverable") costs more than the matcher logic itself, on the median
corpus pattern. That is a real, measured cost of the readability
convention, not a rounding error.

### Does prose inflate source without touching `.o`? — Yes, mostly, but it is not the whole story

| pair | Pearson r |
|---|---|
| source bytes vs `.o` bytes | 0.9712 |
| (source - prose) bytes vs `.o` bytes | **0.9899** |
| program+tables bytes vs `.o` bytes | 0.9882 |
| prose bytes ALONE vs `.o` bytes | **0.4337** |

Stripping prose out of the source correlation moves r from 0.971 to 0.990 —
prose is measurably diluting the source-to-`.o` relationship, exactly the
"does prose inflate source without touching `.o`" question the charter
asks. But prose's own correlation with `.o` (0.43) is not zero: a pattern
whose bounded repeat forces more counter-rung replication gets both MORE
comments (one `// optional copy (N remaining)` per copy) AND more code —
prose is a passenger on the same replication that drives `.o`, not an
independent inflator. **A size term aimed at the number a user ships should
price program+tables bytes (or `.o` bytes directly), not source bytes** —
source-byte counting would penalize [M6-READ]'s readability convention for
a cost the convention does not actually impose on the shipped artifact.

## 6. The witness — full attribution

The plan row's witness, the fuzz gate's seed-1 pattern (151 bytes):

```
1{1,}b1{0}1{2,3}?|(c0{1}.)|((\n.*|.{2}|(?:a{2,3}|0{0,30}cc|c{0,3}bc{2,3}){1,}){5,10}.{2,}|[a-c-e]{1,}?|a$b){28,30}[a-z0-9]{28,30}(\n[^abc]{28,30}?){1,}
```

Compiled at this lane's branch point with `-p rx --features all` (default
auto), self-contained `-o -` form — the same form the rest of this census
uses throughout, for the same reason: **2,015,594 bytes source.**

**A methodology correction made mid-lane, recorded rather than
smoothed over.** This report's own first pass (and the .o/gcc-time/
attribution numbers below) initially cited **2,004,784 bytes**, obtained
by compiling with `-o witness.c` (the SPLIT form) and reading `witness.c`
ALONE — silently missing the ~11 KB `witness.h` sidecar that
`#include "witness.h"` pulls in at compile time. The `.o` size (503,344 B)
and gcc CPU/wall (55.13 s / 55.53 s) were unaffected — `gcc` compiled
`witness.c` WITH `witness.h` present in the same directory, so the
compiled OBJECT was always complete and correct — but the SOURCE byte
count and the byte ATTRIBUTION (which read `witness.c` as a standalone
text file) undercounted by exactly `witness.h`'s size. Caught by
computing `--unroll=1`'s ratio a second way and finding it disagreed with
the tension-curve run's own `-o -`-based default row (2,015,594, §8) by
11,308 bytes — the ABI-header sidecar's own size, matching exactly. Fixed
by re-deriving every witness number in this section from a fresh `-o -`
compile of the identical pattern at the identical commit; the corrected
attribution moved by under 0.5 percentage point in every bucket (the
"Attribution" table below carries both the corrected and the
mis-measured figures for the record). The
plan row's own headline figure, **2,004,778**, is 6 bytes off this lane's
OWN mis-measured 2,004,784 — both are "split-`.c`-alone" counts, which is
worth flagging for whoever wrote the plan row: it is very likely the SAME
undercount, off by roughly `witness.h`'s own size from the true
self-contained total.

Stamps: `RX_ENGINE "vm"`, `RX_ENGINE_WHY "capture
group at pattern offset 18"`, `RX_VM_PREFILTER "none"` (the [SEL-1]
drop — its auto-selected prefilter's DFA build overflowed `>32000 states`,
so no hybrid prefilter is attached at all), `RX_VM_RUNGS 0x17` (all five
rungs live in one artifact: CURSOR, FRAMES_BOUNDED, FRAMES_UNBOUNDED,
REVDET, COUNTER).

`gcc -O2 -c`, watched (`scripts/watchdog -s 180 -c 150 -m 1200m`):
**wall 55.53 s / CPU 55.13 s / peak tree-RSS 556,984 KB (544 MB)**, `.o`
**503,344 bytes** (492,313 `.text`, 144 `.data`, 0 `.bss`) — matching the
plan row's own "52.9 s / 540 MB" within measurement noise (same box,
different moment, same order of magnitude).

### Attribution

Re-derived from the corrected self-contained source (the note above):

| section | bytes | share | (mis-measured split-`.c`-alone figure, for the record) |
|---|---|---|---|
| program | 1,657,633 | **82.2%** | 1,654,924 / 82.5% |
| prose | 296,245 | 14.7% | 291,709 / 14.6% |
| scaffold | 60,792 | 3.0% | 57,227 / 2.9% |
| tables | 924 | 0.0% | 924 / 0.0% |
| main | 0 | 0.0% | 0 / 0.0% |

The correction moves every bucket by well under half a percentage point
— the missing `witness.h` sidecar is almost entirely `scaffold`-bucket
ABI declarations (typedefs, `#define`s), which is exactly where its
share moved (2.9% -> 3.0%). None of this section's other findings change.

**Cross-validated against an independent measurement the manager ran
separately** (a `gcc -fpreprocessed -dD -E -P` comment-strip pass on the
same artifact, ~15% comment share) — this census's fixed classifier reads
14.7%, within a percentage point. Before the classifier's typedef/nested-
comment bug (§5) was found and fixed, this same attribution read prose at
**0.4%** — a 36x understatement, because every one of the thousands of
per-node `// optional copy (N remaining)` comments living inside the
artifact's ONE giant search function was being folded into PROGRAM instead
of PROSE. The witness is what exposed the bug: on an ordinary corpus
artifact (a handful of comments per file, mostly at file scope outside any
function) the bug's effect was invisible at the 25-pattern sample size this
lane first validated against; only a VM artifact whose entire body is one
function with thousands of embedded comments made the error large enough
to be caught by cross-checking against an outside source. Recorded here as
the finding it is, not smoothed over.

**Independent line-kind counts** (own `grep`, cross-checked against the
manager's separately-run measurement, both methods agreeing within
rounding): 7,467 `rx_LN:` label lines (`__attribute__((unused));`, one per
node the VM's `VE_RUNG`/possessify/revdet event stream marked a choice
point at), 7,681 `goto rx_L` control-transfer lines, 1,861 `RX_PRUNE_TOO_SHORT`
MRL-guard occurrences (§2.4/§4 of `tuning.md`), 1,608 `RX_SET`, 2,375
`RX_PUSH`. 45,229 total lines. The manager's independent per-line-kind
attribution of the PROGRAM region (779,040 B / 1,291 span loops = ~603 B
each, 40.3% of program; 260,235 B / 7,467 labels = ~34.9 B each, 13.5%;
160,298 B of `RX_PRUNE_TOO_SHORT` guards, 8.3%; 139,876 B of bare gotos,
7.2%; 113,173 B of class tests, 5.9%; the remainder slot-set/push
bookkeeping) is consistent with this census's own coarser five-bucket
split and is the finer-grained decomposition STEP 2's size term would
price a lever against (§7).

### Which construct's replication produces the bytes

`RX_VM_RUNGS 0x17` names FRAMES_BOUNDED (0x2) and FRAMES_UNBOUNDED (0x4)
both live, alongside COUNTER (0x10) — meaning at least one quantifier in
this pattern took the counter rung (the one whose replication IS `--unroll=K`
body copies) and at least one other took a frames rung (which
replicates differently — one frame per optional copy up to the bound, not
one body copy). The pattern's own structure: `{28,30}` wraps a 4-branch
alternation (`\n.*` / `.{2}` / a further-nested `(?:...){1,}` / `[a-c-e]{1,}?`
/ `a$b`) that is NOT one-unambiguous (branches overlap: `.{2}` and the
`[a-c-e]{1,}?` class both match ordinary bytes), which is exactly the
condition that DENIES the CURSOR and REVDET rungs' preference and forces
FRAMES — the expensive rung, on the outermost, widest-range quantifier in
the whole pattern. `{5,10}` and `{2,3}` nest one level in, `{0,30}` inside
the alternation's own `0{0,30}cc` branch nests a third; K22's replication-
PRODUCT hazard (§4) is the multiplicative reason the artifact is 3x the
corpus's own worst case rather than merely "a bit worse."

### Does ANY existing knob bring it under D45's budget?

**Yes — one does, dramatically. Measured** (watched, generous CPU budget,
self-contained `-o -` form, same commit):

| variant | source bytes | `.o` bytes | gcc CPU |
|---|---|---|---|
| default | 2,015,594 | 503,344 | 55.13 s |
| `--unroll=1` | **116,380** (5.8% of default) | **28,104** (5.6%) | **1.015 s** |
| `-fno-counter` | 4,126,673 (2.05x default — LARGER) | — (never finished) | **150.10 s CPU, killed exactly at the budget ceiling** (`gcc: internal compiler error: CPU time limit exceeded signal terminated program cc1`) — `-fno-counter` falls back to full literal replication for a pattern already using the counter rung above its per-quantifier comfort zone, exactly `tuning.md` §2.3's own warning, and it is not a smaller fallback here — it is the ORIGINAL D45 pathology (the `bigbounded` case, D45's own founding incident) reproduced live on a fresh pattern, at 15x D45's plain CPU budget and still not done |
| `-fno-splice-calls` | 2,015,597 (~identical — no subroutine calls in this pattern, axis is a no-op here as expected) | 503,344 (identical to default) | ~55 s (identical to default) |
| `-fno-premul-table` | N/A — `RX_VM_PREFILTER "none"`, no DFA scan to deny a table form on |
| `--engine=vm` | 2,015,594 (identical to default) | 503,344 (identical) | 53.90 s (identical) |

**`--unroll=1` is the single largest size lever measured anywhere in this
census** — a 17.3x reduction in source, 17.9x in `.o`, 54x in gcc CPU time,
for a pattern whose default form sits at 5.5x D45's plain budget. This is
the clean, general, already-shipped knob STEP 2's size term should reach
for FIRST on a counter-rung-dominated artifact — no new mechanism, just a
different default choice of K past some measured threshold.

**But the SAME knob is nearly a no-op on the corpus's own top-5 outliers**
(§8's own numbers): `--unroll=1` shrinks `((a)|ab){4000}c` by only 1.2%.
This is the tension curve's central, non-obvious finding — see §8's own
discussion of why the same flag has two completely different effects on
two patterns that both use the counter rung.

### Which cap should have bound this, and why it did not

The manager asked directly: which of [ENG-BREP]'s existing caps —
`PCREC_MAX_VM_REPEAT_COPIES` (64, `src/core/limits.h:208`) or
`PCREC_MAX_VM_REPLICATION_PRODUCT` (= `PCREC_MAX_VM_NODES` = 131,072,
`src/core/limits.h:172,240`) — should have refused or throttled the
witness, and why it did not. Measured, read-only against `limits.h`
(no `src/` change):

- **`PCREC_MAX_VM_REPEAT_COPIES` (64) never comes close.** The witness's
  own bounded quantifiers top out at `{28,30}` — a factor of 30, **47% of
  the 64-copy cap**. This cap bounds ONE quantifier's own literal-copy
  count and is specifically about the case a counter/frames rung DOESN'T
  cover; it was never going to fire on a pattern whose worst single factor
  is 30.
- **`PCREC_MAX_VM_REPLICATION_PRODUCT` (131,072) never comes close either.**
  This is the K22 nesting-PRODUCT guard, checked during the pre-pass against
  the same bound as `PCREC_MAX_VM_NODES`. The witness's own realized node
  count — measured directly by counting `rx_LN:` labels (`grep -c
  '^rx_L[0-9]*: __attribute__((unused));'`), one per node the emitter's own
  `VE_RUNG`/possessify/revdet event stream marks — is **7,467, or 5.7% of
  the 131,072-node cap.**
- **The multiplicative mechanism IS real and IS measured, just nowhere near
  either cap.** `grep -oE 'optional copy \([0-9]+ remaining\)'` on the
  witness finds 72 distinct FRAMES-rung optional-copy sites, each with a
  "remaining" count of 1-5 (14-15 occurrences of each value) — the
  {5,10} quantifier's own 5 optional iterations, replicated once per
  outer-loop instantiation. Combined with the manager's own independent
  count (one specific inner construct, "group 3," emitted 140 times —
  consistent with 28 (the {28,30} quantifier's MANDATORY count) x 5 (the
  {5,10} quantifier's MANDATORY count) = 140, the textbook K22 nested-factor
  product), this is the same mechanism K22's own hazard names — "factors
  MULTIPLY" — legitimately compiled, well inside both caps, and still
  2 MB.

**The finding: neither existing cap is a bug that "should have" fired and
didn't. Both are calibrated to catch RUNAWAY/exponential blowup (the
depth-40-tower-of-`{0,2}` shape K22 was written against, or a construction
that would genuinely explode the node count past 131,072) — a completely
different failure mode from "this pattern is cap-compliant by a wide
margin and still produces an artifact 3x the size of anything in the
corpus." STEP 2's size term is not a fix to an existing cap; it is a NEW
one, needed precisely because 5.7% of the node-count cap already produces
2 MB, and the corpus's own largest artifact by node count — `((a)|ab)
{4000}c` (§4's own top outlier), 80 `rx_LN:` labels — sits at **0.06%**
of that same 131,072-node cap, two full orders of magnitude below the
witness's 5.7%. A node-count threshold in the low thousands (not
anywhere near 131,072, but comfortably above 80) is what would separate
the witness from the entire measured corpus while leaving every corpus
pattern untouched — the concrete number is a STEP 2 design call, but the
GAP between "where the corpus lives" (tens to low hundreds of nodes on
its own worst outliers) and "where the existing safety caps sit" (tens
of thousands) is now measured, not assumed.

## 7. What this section leaves for STEP 2

Not this lane's mandate (STEP 1 is measurement-only, no `src/` change) but
recorded here because the census's own numbers are what raises the
question: STEP 2's size term needs a general lever, not a special case
(the project's own standing rule, `pcrec-general-mechanisms-not-special-cases`).
The manager's independent per-line-kind breakdown of the witness's PROGRAM
region names three concrete, gcc-independent candidates worth PRICING (not
built) against this census's population before STEP 2 commits to one:

1. **A shared span-loop helper per (class, stride, greediness) SHAPE**,
   called with the clamp limit as a parameter, in place of one inlined loop
   per site. §6's line-kind count says span loops are 40.3% of the
   witness's PROGRAM bytes at ~603 B/loop over 1,291 loops — the lever's
   size is real if the shapes are few and the instances are many (a count
   this census did not take: how many DISTINCT (class, stride, greediness)
   tuples exist across the corpus's outliers vs how many total loop sites
   reference them).
2. **The node skeleton** — how many of a VM artifact's `rx_LN:` labels have
   exactly one predecessor (reachable by exactly one `goto`) and could be
   folded into their predecessor's fall-through, removing both the label
   line and a `goto` for each. §6 counts 7,467 labels / 7,681 gotos on the
   witness (13.5% + 7.2% = 20.7% of PROGRAM combined) — a population
   nobody has counted yet for "how many are singly-referenced." The
   label:goto RATIO holds across the corpus's own outliers too (not just
   the witness), measured directly on the 5 top-`.o` patterns from §4:
   rxt-00127 80 labels / 81 gotos (1.01), rxt-00143 28/38 (1.36), rxt-00118
   88/97 (1.10), rxt-00030 1,471/1,525 (1.04), rxt-00029 1,141/1,177
   (1.03) — every one close to 1:1, consistent with most labels having
   exactly one incoming `goto` and therefore being fold candidates by this
   lever's own test, though this census did not build the actual
   predecessor-count analysis (a ~1:1 ratio is suggestive, not proof: it
   is also what a chain of labels with one predecessor EACH would produce,
   which is exactly the shape the lever targets, but a control-flow-graph
   walk is what STEP 2 needs before committing to it).
3. **Hoisting the MRL guard's per-copy constant**
   (`RX_PRUNE_TOO_SHORT(scan_position, 59 + (1 * (20 - slot_values[1301])))`,
   inlined once per node at 8.3% of PROGRAM on the witness) — the additive
   constant differs only by the copy's own iteration count, which is
   computable without re-emitting the whole guard expression per site.

None of the three is sized against the CORPUS in this pass (only against
the witness's own line-kind breakdown, courtesy of the manager's
cross-lane measurement) — that is the natural STEP-1.5 follow-up if the
manager wants these priced before STEP 2 commits, since §4's outlier
mechanism (counter-rung replication under nested bounded repeats) is
exactly where all three levers would apply first.

## 8. Tension curves

**Status note on the throughput columns.** The size/`.o`/gcc-time columns
below are final (compiler output is deterministic and does not depend on
box load — indirect confirmation: witness/`fno-splice-calls` and
witness/`engine-vm`, two DIFFERENT no-op-for-this-pattern variants
compiled minutes apart at different load levels, both independently
landed at exactly the same 503,344 `.o` bytes as witness/`default`,
consistent with all three compiling to identical code rather than a
load-dependent measurement). The `match_us`/`fail_us` throughput columns
are now FINAL: re-taken on a quiet box (`load1` 0.13-1.2, 20:08-20:22
EDT, 2026-08-28) once the manager signaled that the union battery on the
box's `main` branch, which had held `load1` at ~13-14 for the remainder
of the first pass, had cleared. The quiet pass filled in every row the
first pass had marked "not run" or left PROVISIONAL, including the
witness's own `-fno-splice-calls` and `--engine=vm` rows (throughput not
run at all in the first pass). The witness's `-fno-counter` row still has
no throughput number, for a reason independent of load: its split-form
build times out linking `bdriver` past 180 s at this variant's ~4.1 MB
source size (the same budget-kill visible in its gcc-CPU column).
Everywhere the first pass's PROVISIONAL number showed a >10x effect, the
quiet pass confirms the direction held; where a magnitude moved
materially the text below states it as "loaded vs quiet: X → Y" — the
largest is `--engine=vm`'s fail-path cost on `((a)|bc){0,4000}d`, 359,000x
(PROVISIONAL) → 173,580x (quiet).

### The witness

| variant | source | `.o` | gcc CPU | match | fail |
|---|---|---|---|---|---|
| default | 2,015,594 | 503,344 | 55.13 s | 6.03 us | 5.60 us |
| `--unroll=1` | 116,380 (5.8%) | 28,104 (5.6%) | 1.02 s | 0.13 us | 0.17 us |
| `-fno-counter` | 4,126,673 (206%, LARGER) | — never finished | **150.10 s, CPU-budget-killed** | not run (bdriver link still times out past 180 s at this size, independent of load) | same |
| `-fno-splice-calls` | 2,015,597 (100.5%) | 503,344 (100%) | 53.53 s | 2.33 us | 2.53 us |
| `-fno-premul-table` | N/A — no DFA scan | | | | |
| `--engine=vm` | 2,015,594 (100.5%) | 503,344 (100%) | 53.90 s | 2.40 us | 2.37 us |

`--unroll=1` is the whole story for this pattern: a 17x size reduction, a
54x compile-time reduction, and — on the two short, fast-resolving
subjects this pattern's own catastrophic-backtracking hazard allows (§1's
subject-construction note: longer/more elaborate subjects for this pattern
risk genuine exponential blowup even in pcrec's bounded VM, so the
subjects here are deliberately short) — a comparable or FASTER per-call
time (0.13/0.17 us vs 6.03/5.60 us; loaded vs quiet on the default row:
5.80/6.37 us → 6.03/5.60 us, within this pattern's own run-to-run noise —
`--unroll=1`'s own number barely moved at all). The two rows the loaded
run never reached, `-fno-splice-calls` (2.33/2.53 us) and `--engine=vm`
(2.40/2.37 us), land 2-3x FASTER than default despite compiling to
byte-identical `.o` output (confirmed above) — consistent with the same
per-build cache-locality effect floated for `--unroll=1`, not a per-flag
one; still a hypothesis, not an isolated mechanism.

### The corpus's top-5 outliers by `.o` size

`.o` bytes as a percentage of that pattern's own default, gcc CPU in ms,
throughput in microseconds/call (quiet box, `load1` 0.42-1.17,
20:08-20:22 EDT, 2026-08-28):

| pattern | variant | `.o` (% of default) | gcc CPU | match us | fail us |
|---|---|---|---|---|---|
| `((a)\|ab){4000}c` | default | 202,904 (100%) | 311 | 36.5 | 7.7 |
| | `--unroll=1` | 200,648 (99%) | 245 | 35.9 | 7.6 |
| | `-fno-counter` | REFUSED (above the 64-copy cap, no fallback) | | | |
| | `-fno-splice-calls` | 202,904 (100%) | 317 | 89.5 | 18.4 |
| | `-fno-premul-table` | 154,920 (76%) | 331 | 47.7 | 10.2 |
| | `--engine=vm` | **8,944 (4%)** | 183 | 16.3 | **51.5** |
| `((a)\|bc){0,4000}d` | default | 128,136 (100%) | 236 | 48.0 | 0.20 |
| | `--unroll=1` | 128,136 (100%) | 218 | 47.2 | 0.23 |
| | `-fno-counter` | 128,136 (100%) — no-op, this pattern's rung is FRAMES_UNBOUNDED, not COUNTER | 237 | 46.9 | 0.23 |
| | `-fno-splice-calls` | 128,136 (100%) | 220 | 48.2 | 0.23 |
| | `-fno-premul-table` | 96,152 (75%) | 223 | 23.0 | 0.10 |
| | `--engine=vm` | **6,168 (5%)** | 121 | 31.5 | **34,716.0** |
| `((a)\|ab){0,4000}c` | default | 107,944 (100%) | 301 | 28.0 | 0.10 |
| | `--unroll=1` | 104,776 (97%) | 202 | 27.5 | 0.23 |
| | `-fno-counter` | REFUSED (above the 64-copy cap) | | | |
| | `-fno-splice-calls` | 107,944 (100%) | 290 | 23.4 | 0.10 |
| | `-fno-premul-table` | 83,960 (78%) | 291 | 69.6 | 0.23 |
| | `--engine=vm` | **9,992 (9%)** | 230 | 20.1 | **20.5** |
| nested-repeat, N=8 | default | 103,384 (100%) | 7,900 | 13.4 | 9.0 |
| | `--unroll=1` | **21,432 (21%)** | **646** | 5.9 | 3.7 |
| | `-fno-counter` | 103,792 (100%) — under the cap, literal fallback ~same size but 21% faster to compile | 6,236 | 13.4 | 8.7 |
| | `-fno-splice-calls` | 103,384 (100%) | 8,656 | 5.3 | 3.6 |
| | `-fno-premul-table` | 103,384 (100%) | 8,550 | 6.3 | 3.8 |
| | `--engine=vm` | 101,648 (98%) | 7,395 | 12.0 | 4.4 |
| nested-repeat, N=6 | default | 85,400 (100%) | 3,779 | 14.0 | 8.5 |
| | `--unroll=1` | **21,432 (25%)** | **596** | 14.3 | 8.1 |
| | `-fno-counter` | 85,400 (100%) — no-op, no COUNTER bit in this rung | 3,746 | 6.4 | 3.6 |
| | `-fno-splice-calls` | 85,400 (100%) | 3,843 | 6.9 | 4.2 |
| | `-fno-premul-table` | 85,400 (100%) | 3,759 | 16.0 | 8.5 |
| | `--engine=vm` | 83,664 (98%) | 3,767 | 4.8 | 3.6 |

**Loaded vs quiet, the two rows that moved a stated conclusion**: on the
N=8 nested-repeat row, the loaded pass read `--unroll=1` as parity with
default (6.1/5.9 us vs 6.2/4.3 us); the quiet pass reads default as
markedly slower (13.4/9.0 us) with `--unroll=1` unchanged (5.9/3.7 us) —
loaded vs quiet: 6.1 us → 13.4 us (default match), 6.2 us → 5.9 us
(`--unroll=1` match). And on `((a)|ab){4000}c`, `-fno-splice-calls`
(a size no-op for this pattern — 202,904 `.o` bytes in both passes,
identical to default) moved from the CHEAPEST cell in its row under load
(8.1 us fail, alongside default's 8.6 and `--unroll=1`'s 8.4) to
noticeably the most expensive non-`--engine=vm` cell under quiet
conditions (18.4 us fail) — the same per-build cache-locality noise
flagged for the witness's no-op variants above, now reproduced on a
second, independent artifact. Given that, single-cell differences of a
few microseconds anywhere in this table (this row's own default/
`--unroll=1`/`-fno-splice-calls` triad, or N=6's `-fno-counter` reading
6.4/3.6 us quiet against 15.3/9.4 us loaded despite being a stated
size-no-op) should be read as noise at this magnitude, not as a per-flag
effect; only the >=10x effects (`--engine=vm`'s fail-path cost,
`-fno-premul-table`'s size trade) are load-independent claims this
census stands behind.

### The tension curve's own finding: three DIFFERENT levers, three DIFFERENT trades

The census set out to measure "the same pattern under four knobs plus the
engine axis" and found not one lever but three, each with a different
cost:

1. **`--unroll=1` is free — on the N=8 nested-repeat outlier, measurably
   FASTER — on the nested-repeat family, useless on the `((a)|ab){N}c`
   family.** 79-75% size reduction and 12x faster gcc, at no measured
   throughput cost, on rxt-00030/00029 (whose bounded factor, `{0,8}`/
   `{0,6}`, is small and NESTED two levels deep — where K1 matters is the
   multiplicative replication across nesting, and unroll's own per-chunk
   savings compound down every level). Loaded vs quiet, N=8's own default
   row moved (6.1 us → 13.4 us match) while its `--unroll=1` row barely
   did (6.2 us → 5.9 us) — so what the loaded pass read as parity now
   reads as `--unroll=1` roughly 2.3x FASTER, not merely free; N=6 stayed
   at parity in both passes. On `((a)|ab){N}c` (`{4000}`/`{0,4000}`/
   `{0,2047}`, ONE level, large factor) it is a 1-3% effect — noise. **The
   lever's payoff is a property of the NESTING STRUCTURE, not the raw
   replication count** — exactly what §6/§7's node-skeleton and
   span-loop-shape levers would need to generalize correctly rather than
   assuming "K down = smaller" universally.
2. **`-fno-premul-table` is the OPT-3-predicted, well-behaved SIZE
   lever; its throughput side did NOT survive the quiet-box re-run as a
   clean story.** The ~22-25% size reduction on every pattern with a DFA
   scan to deny a table form on is unchanged (size is load-independent).
   The loaded pass read a consistent ~20-34% slower match time on 4 of 5
   patterns (`docs/design/premultiplied_dfa_table.md`'s own 1.1-1.8x
   figure) and one large outlier (`((a)|bc){0,4000}d`, +210%, unremarked
   in the loaded numbers). The quiet pass reads: `((a)|ab){4000}c` still
   ~31% slower and `((a)|ab){0,4000}c` now 2.3-2.5x slower (past
   "modest"), but `((a)|bc){0,4000}d` and nested-repeat N=8 now read
   FASTER without the premultiplied table (-52%/-50% and -53%/-57%
   respectively) and N=6 is flat — a direction flip on 2 of 5 patterns
   that the mechanism (denying a lookup optimization should never help)
   cannot explain. Loaded vs quiet: "consistent ~20-34% slower on 4/5
   patterns" → "-53% to +150% across the five, direction not consistent."
   These are the same five artifacts where a stated size-no-op flag
   elsewhere in this table swung 2x+ between passes (item 1's own
   `-fno-splice-calls`/`-fno-counter` cells, §8's status note) — read as
   the same per-build measurement noise, not a re-measured mechanism, and
   NOT evidence against `-fno-premul-table`'s size claim, which does not
   depend on this throughput number.
3. **`--engine=vm` IS "the size vs performance tension that kicks in at
   some size," measured directly and dramatically — and this one DID
   survive the quiet-box re-run.** On all three `((a)|ab)`-family
   patterns, dropping to pure VM (no hybrid DFA prefilter) shrinks `.o`
   to **4-9% of default** — the single largest size lever this census
   measured on ANY non-witness pattern. The COST is the prefilter's own
   job: rejecting a non-matching subject fast. On `((a)|bc){0,4000}d`'s
   failing subject (5,000 bytes, no literal `d` anywhere — the DFA
   prefilter's `memchr`-class scan dismisses it in O(1); the bare VM has
   no such shortcut and must backtrack through the whole subject) the
   fail-path cost goes from **0.20 us to 34,716.0 us — a 173,580x
   slowdown** (quiet-box run; loaded vs quiet: 359,000x → 173,580x — the
   loaded pass's own default-row denominator was itself noisy, 0.10 us
   vs quiet's 0.20 us, but the effect is unmistakably still five orders
   of magnitude). This is the concrete, measured shape of "size vs
   performance": the prefilter IS the size (a whole second DFA machine,
   forward+reverse tables, embedded in the artifact) and it IS the speed
   (an O(1) or O(subject) reject instead of an O(subject)-with-backtracking
   one) — the SAME bytes buy both, and a size term that removed the
   prefilter to save space would be trading away exactly the thing D46's
   own "prefilter-before-VM is an ORDERING RULE, not a tuning knob"
   language (`src/gen/CLAUDE.md`) says must never be optional on a
   pattern the prefilter can answer.

## 9. What was NOT measured, and why

- **`--engine=vm`'s effect on artifacts that are ALREADY vm-selected for a
  real reason** (a live capture, a `VM_ONLY` registry construct) is only
  "does the hybrid prefilter come off" — it does not change engine, so its
  size delta on such artifacts is smaller than on a DFA-eligible one. This
  census's tension curves (§8) include it uniformly rather than special-
  casing it; the numbers say how much it actually buys on THESE outliers,
  which are all already vm-selected.
- **No comparison to pcre2-jit or any other engine's artifact size** — out
  of scope for a pcrec-internal size census; `bench:loglines:level-context`'s
  own [SEL-1] DFA-overflow fallback (found live in this census, §2) is the
  concrete case the plan row's own bench-inbox ask (I-15) is about, and
  that timing comparison is explicitly the manager's to make via the
  inbox/outbox channel (D78), not this lane's.
- **`--unroll=K` swept across its full 1..4096 range** — only `K=1` (the
  minimum) is in the tension curves; the corpus's default `K` value and the
  shape of the size-vs-K curve in between are not measured. A STEP-2 design
  that wants K as a continuous dial needs that curve, not just the two
  endpoints this census took.
- **A cap threshold recommendation** — this census reports the distribution
  and the outlier mechanism; naming an actual byte threshold for STEP 2's
  hard cap is a judgment call for the design step, informed by but not
  computed from these numbers (§0 item 6 states the range: above the
  corpus's own 675 KB max, below or at the witness's 2 MB).
- **Sanitizer-axis gcc times** — this census used plain `-O2`, matching
  "the number a user ships." D45's sanitizer-axis budget (200s CPU) is a
  different quantity for a different population (the test suite's own
  battery) and is out of this census's scope.
- **Quiet-box throughput for the tension curves — DONE.** §8's
  `match_us`/`fail_us` columns were re-taken on a quiet box (`load1`
  0.13-1.2, 20:08-20:22 EDT, 2026-08-28) once the manager signaled that
  the union battery on the box's `main` branch, which had held `load1` at
  ~13-14 for the remainder of the first pass, had cleared. They are now
  FINAL, including the 3 of the witness's own 6 variants
  (`--unroll=1`, `-fno-splice-calls`, `--engine=vm`) the loaded pass never
  reached; `-fno-counter` on the witness still has no throughput number
  for a load-independent reason (its split-form bdriver link times out
  past 180 s at this variant's ~4.1 MB source size). The DIRECTION of
  every large (>=10x) effect in §8 held between the two passes
  (`--engine=vm`'s size shrink and fail-path slowdown, `--unroll=1`'s win
  on the nested-repeat family), but exact magnitudes moved, most notably
  the `--engine=vm` fail-path cost on `((a)|bc){0,4000}d` (loaded vs
  quiet: 359,000x → 173,580x) and `--unroll=1` on the N=8 nested-repeat
  pattern (loaded vs quiet: read as parity with default → read as
  default ~2.3x slower). One conclusion did NOT survive the re-run:
  `-fno-premul-table`'s throughput cost, loaded-read as a consistent
  ~20-34%-slower-on-4/5-patterns story, quiet-reads as direction-
  inconsistent (-53% to +150% across the same five patterns) — §8 item 2
  now states this as noise at this measurement's scale rather than a
  re-confirmed mechanism; the flag's SIZE claim (~22-25% smaller,
  load-independent) is untouched.
- **The node-skeleton lever's actual predecessor-count walk** (§7 item 2):
  this census measured the label:goto RATIO (close to 1:1 on every
  outlier checked, §7) as a cheap proxy, not the real control-flow-graph
  walk ("does this specific label have exactly one incoming edge") STEP 2
  would need before committing to the fold. The ratio is suggestive, not
  proof — stated as such in §7's own text.

## 10. Reproducing this census

`docs/dev/artifact_size_census/census.py` (committed, its own CLAUDE.md
line points here) reproduces §2-§5 from a clean `build/pcrec`:

```
python3 docs/dev/artifact_size_census/census.py \
    --root /path/to/pcrec --bench-root /path/to/pcrec-bench \
    --out /some/scratch/dir
```

Outputs `patterns.tsv` (id, source tag, pattern text), `census.tsv` (one
row per pattern, the full column set §1-§5 draw from) and `progress.log`
(append-only, for polling an async run). Raw TSVs from this lane's own run
are in the session scratchpad
(`/tmp/claude-1001/-home-duxevents-pcrec/91e42122-1121-4b36-a6cc-0efc92c445cc/scratchpad/artsize/census_full/`),
not committed — the script is the reproducible artifact, not the numbers.
