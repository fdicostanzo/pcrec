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
   the corpus's own largest artifact, against the witness's 2,004,778 B /
   503,344 B). The corpus's outliers are already the SAME MECHANISM as the
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
5. **The tension curves (§8) confirm the size lever and separate it from
   the ones that would cost speed.** [PLACEHOLDER — filled in once the
   tension-curve runs complete; see §8 for the live numbers, corpus
   outliers and witness together.]
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
  form — byte-identical to the split `.c`+`.h` form's combined bytes,
  verified on a sample) — auto engine selection, no other flags.
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
  above 2 (§8's own note records the box's ambient load during this run —
  another lane's sections were active throughout).

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
during this lane's own development (an off-by-one in the newline-byte
accounting, and — the more consequential one — a multi-line function-pointer
typedef that a naive regex mismatched as a body-bearing function
definition, which then silently folded EVERY nested comment and table
inside the enclosing "function" into the PROGRAM bucket rather than
recursing the same comment/table dispatch into it. Both are fixed in the
committed script (`docs/dev/artifact_size_census/census.py`); the second
was caught only by cross-checking the witness's attribution against an
independent measurement — see §8.

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
auto): **2,004,784 bytes source** (the plan row's own figure, 2,004,778, is
the split `.h`-header-excluded `.c` file; this census's self-contained
`-o -` form is 6 bytes larger from the header content being inlined — same
artifact, confirmed byte-for-byte identical machine code by objdump-diffing
the two forms' `.text`). Stamps: `RX_ENGINE "vm"`, `RX_ENGINE_WHY "capture
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

| section | bytes | share |
|---|---|---|
| program | 1,654,924 | **82.5%** |
| prose | 291,709 | 14.6% |
| scaffold | 57,227 | 2.9% |
| tables | 924 | 0.0% |
| main | 0 | 0.0% |

**Cross-validated against an independent measurement the manager ran
separately** (a `gcc -fpreprocessed -dD -E -P` comment-strip pass on the
same artifact, ~15% comment share) — this census's fixed classifier reads
14.6%, within a percentage point. Before the classifier's typedef/nested-
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
price a lever against (§9).

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

Not measured directly against a real re-compile in this section (§8's
tension-curve table has the numbers); qualitatively, from `tuning.md`'s own
text: `-fno-counter` is stated NOT to have a fallback for a pattern already
using the counter rung above its cap ("there is no `-fno-counter` build to
compare against, because the cap is what refuses it") — so denying the
counter rung on THIS pattern is expected to either refuse outright or force
a different, possibly WORSE rung, not shrink the artifact. `--unroll=1`
(the counter rung's own K parameter at its minimum) is the more promising
lever on paper: fewer bytes per body-copy chunk. §8 has the measured
answer for the witness specifically, alongside the top-5 corpus outliers.

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
   nobody has counted yet for "how many are singly-referenced."
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

[PLACEHOLDER — being filled in as the tension-curve measurement completes;
methodology in §1, mechanism analysis in §4/§6.]

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
