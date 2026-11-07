# MEAS findings

Subject: target_seam.md rev 0 (e2f9793d1); build tree 5b43f8e9a, gcc 15.2, Zen 4. ~25 compiles used.

## Findings

### MEAS-1 (CONFIRMED, design/answer-check) The dispatcher cell cannot fail on a wrong pick
§7: "its answer equals the answer of the variant it should pick on this CPU". All variants are
answer-identical by construction and by §7's own oracle control. A dispatcher that always picks
`generic`, or picks v3 on a CPU that lacks AVX2 only in the sense of a swapped chain, returns the
same answer, so the cell passes. Outcome that should fail: dispatcher chain reversed (generic first).
Answer-equality: PASSES (cannot fail). Also "should pick" has no independent source: if the test derives
it from `__builtin_cpu_supports` it shares the dispatcher's probe. And on one box only the top rung is
reachable, so the lower rungs of the chain are never exercised. Needs: an observable of WHICH variant ran
(a test-only lever or getter, per pcrec-flag-follows-caller-effect: a test-only lever, not public), a
forced-probe lever to walk every rung, and an independent expectation (cpuid flags read by the test).
Severity design; effort small; blast: §7 only.

### MEAS-2 (CONFIRMED, design) "Variant runs on its own arch" has no check that the variant IS target code
§5 relies on `#pragma GCC target` regions. If the pragma silently fails to apply (placed after the
include, wrong string, ordering with push_options) the variant is generic text, every `.rxt` case still
passes against the oracle, and the skip pin is satisfied. Nothing in §7 checks that the v3 variant's
object contains the target's instructions. Fix: per-variant structural check (objdump/`-S` of the
variant's helpers shows ymm for the AVX2 rung, none in generic), counted per variant (K35).
Severity design/answer-blind; effort small.

### MEAS-3 (CONFIRMED, measurement) `emit_sweep.py --extra -fno-memfn-simd` is a vacuous control and would be refused by the tool as written
Real options (scripts/emit_sweep.py:135-215): `--ref REV` (git archive of a reference build), `--extra=ARGS`
(repeatable, appended to streams 1-4 on BOTH sides), `--extra-base`, `--arms start`. "Moved artifact" =
byte difference between ref's and tree's output for the same argv (identity stream), plus DIFFER counts
against the arm's base for arms. Findings:
 a. `-fno-memfn-simd` IS the default (spec cli.md 1.16p5: "the default"). I emitted `(?i)cat` with and
    without it: `diff` shows only the `#include "cN.h"` filename line. So `--extra=-fno-memfn-simd` runs
    the same bytes as the default arm on both sides; it checks nothing the default run did not. Before
    the build it is also what the sweep would show after (both generic). It cannot fail on the
    "maps to the same generic target" claim, because that claim is only testable if the flag and the
    default could have diverged. The meaningful control is the OPPOSITE: `-fmemfn-simd` at the default
    list (see MEAS-4).
 b. With `--extra`, the tool "fail[s] unless DIFFER_PINS has a floor for it" (:176-178; waiver
    `--no-differ-floor`, :3154). DIFFER_PINS (:465-550) has `-fmemfn-simd` but NO `-fno-memfn-simd` cell
    (grep: no hit). The run as written exits red or needs the waiver, which prints "WAIVED, not checked".
 c. G2 at default flags only reaches the SIMD-off text: MEMFN_FORMS is "none" on all but a handful.
    The pinned count of c-default patterns whose bytes differ at -fmemfn-simd is 22 of 4,624 distinct
    (:515; c-vm 19). So the "0 moved" sweep covers ~0.5% SIMD content by construction: it says nothing
    about the part the design changes (`#if` arms to attributed regions).
 d. `--ref <stamp commit>` works as the independent control (separate git archive build) and the mechanism
    is sound for the stamp-landed baseline; but ref and tree both come from the same repo state minus the
    change, so it checks "unchanged", not "right".
Severity measurement; effort small (add the pin cell or use the opposite arm).

### MEAS-4 (CONFIRMED, design gap) What `-fmemfn-simd` means at the default list is unspecified, and the existing arm pin contradicts §6
§6: default list {generic}, "features are empty, so no level is admitted". Then `-fmemfn-simd` at the default
list renders NO helper (nothing admitted) and its artifacts equal SIMD-off: the pinned DIFFER floor
(22 byte/c-default, 19 c-vm, 15 utf8) would read 0 and the arm fails its own floor, while §6 says
"-fmemfn-simd artifacts DO move: their #if arms go away" (moving to what?). Also today's default `-march`
SIMD-on artifact already contains the SSE2 `w16` rung (I measured `(?i)cat`: `RX_MEMFN_FORMS "vrun@w32+w16"`,
size 2618 vs 2386 SIMD-off); an x86 target with empty features loses that rung. Either `generic` must
mean x86-64 baseline (SSE2) per family, or the SSE2 rung needs its own variant. This also decides what the
G2 sweep means for SIMD-on. Ask the owner (no silent defaults).

### MEAS-5 (CONFIRMED, design) §7's variant list over-counts: the kit has two levels, so v2 and v4 add no distinct plan
`memfn/src/levels.def:41-46` (identical on lane/memfn-s2e 5b6cf41aa): only `w16` (SSE2) and `w32` (AVX2).
"The dev box runs generic, v2, v3 and v4": with `needs` = {sse2}, {avx2}, a v2 variant admits w16 only and
a v4 variant admits the same as v3 (no AVX-512 level exists; pcrec-bench-box-cpu: AVX-512 NOT filed). The
v4 variant would differ from v3 only by compiler retargeting. So the per-variant test population and the
skip pin count variants that cannot differ in kit text. A "variant that buys nothing" is also the §8
concept; §7 and §8 should use one rule (see MEAS-8).

### MEAS-6 (CONFIRMED, measurement) The skip pin is not a population count and has no per-box value
Today's gate (`memfn/tests/run_g2_simd.py:655-667`) only PRINTS "skipped arms: N"; it asserts nothing.
§7 turns it into a pin without saying the value: it differs by box (Zen 4: 0; Zen 1 / ubuntubudu: v4;
Mac: all x86 arms n/a; ubuntu-latest CI runner: AVX-512 varies by runner pool). Needs a per-box table
keyed on a declared box class, AND a floor on the RAN count (a host that wrongly probes "lacks" turns the
suite into all-skips and a pinned skip count of "whatever it was" ratifies it). Population counted should
be cases executed per variant, not arms skipped. Can it fail as written: only if someone sets the number.
Severity measurement.

### MEAS-7 (CONFIRMED, measurement) §8's size stand-in is a weak proxy, and its second metric is near-useless
Recomputed `(?i)cat` (gcc 15.2 -O2, `size` text/data): SIMD-off 2386/224; `-fmemfn-simd` default -march
2618/224; `-march=x86-64-v3` 2922/224. REPRODUCES the note exactly (v2: 2618, znver4: 2962).
 - Proxy validity: it prices kit text growth (the #if build admitting w32+w16 at v3). It does NOT price the
   dispatcher, per-variant stems, duplicated stamps (`RX_ENGINE`, `RX_MEMFN_FORMS`... are file-scope
   `#define`s per stem), or table duplication. Worse, gcc at `-march=v3` retargets ALL scalar code.
 - "Count of artifacts whose two objects are byte-identical in .text": I compiled four SIMD-less
   patterns (`abc`, `a(b|c)+d`, `[0-9]+x`, `foo|bar|baz`; all MEMFN_FORMS "none") at default and v3: sizes
   equal, `.text` NOT byte-identical in any (VEX re-encoding, e.g. `pxor` -> `vpxor`, `movaps` -> `vmovdqa`,
   nop padding; also on `(?i)cat` SIMD-off). So the count reads about 0 for every artifact, including
   those where the variant buys nothing. The metric cannot find the population it exists to find. Use
   `MEMFN_FORMS == "none"` (the kit's own fact) or equal text size as the "buys nothing" test.
 - Internal inconsistency: the prose (5.3 KB, 2.2x) is 2386+2922 (generic + v3), but the sweep formula sums the
   default-march and v3 objects of the SIMD-on build, 2618+2922 = 5540 (2.32x). Pick one denominator.
 - It needs no >50 compile sweep: only ~22 of 4,624 patterns render a SIMD form (emit_sweep pin), so
   for the other ~99.5% the ratio would read ~1.00 for a "v3 variant" that is really a copy. That points to the
   real cost question in MEAS-9.
 - The row's own named first measurement ([XARCH-DEV]: "price the corpus with zen4 and an M1-made set and
   count disagreeing sites") is not what §8 measures; §8 is size only and prices no disagreement. Say so.

### MEAS-8 (CONFIRMED, minor, design) G1 and G3 are checkable but G1's form is a text grep only
G1 "zero #if lines" is a grep of the kit's text; it passes a form that is wrong on the target (a missing
attribute fails to compile only if the harness compiles it inside a region). State both. G3 HELD (below).

### MEAS-9 (CONFIRMED, cost) xN is applied to patterns where it buys nothing; the seam has no elision fact
Per MEAS-7, ~99.5% of patterns render no SIMD form. If pcrec emits one whole matcher per listed target
(§2 "a variant is the WHOLE matcher"), {generic, v3} duplicates every artifact for no change in plan: 2x text
for a v3 body identical to generic modulo encoding. The kit already returns `MEMFN_FORMS "none"` (a fact).
Add a kit->pcrec fact "this art rendered no target-dependent text" (or the bracket marks being empty) and
pcrec drops the variant (the dispatcher then has one target). Without it every fielded dispatcher artifact
pays 2x for nothing. And §8's "carry N complete matchers" quotes cost only where a form exists. Also
contrast D155 addendum 5's stated why for [MEMFN-RTDISPATCH]: "a 500 KB artifact must not need 4-5 whole
copies" (plan row [MEMFN-RTDISPATCH], per-site multiversioning, only the hot helpers duplicated); D188 add. 1 now rules whole
variants, 2-3 of them. For a 500 KB artifact that is 1-1.5 MB. Ruled, so not contested, but the note does
not acknowledge the reversal, and the elision above is how the cost stays proportional to benefit.

### MEAS-10 (CONFIRMED, cost) Test-time and CI cost are not priced
§7 runs every `.rxt` case once per variant. `make test` is ~37-39 min on Linux, ~100-105 min on the Mac
(docs/testing.md:999), and CI runs ~41-min shards against a 65-min step limit (testing.md:1083-1091; a step was
already killed at 55). The `.rxt` compile+run pass is the bulk. Two variants run on the CI runner (AVX2 yes),
four on Zen 4 (but see MEAS-5: two are redundant). Not measured here (no suite run): the share of
the section time that is gcc compile. The design should name that measurement and a per-box variant cap
(run the corpus on `generic` plus the TOP variant, the rest on the 22-pattern SIMD subset). Do not charge every
caller of `make test` x2-x4 for 0.5% of patterns.

### MEAS-11 (CONFIRMED, overlap/abi) "Stamp alone as its own abi event first" should ride another abi event
Facts: `rx_info.abi` is 96 (abi_changelog.md) and moves every few days, so a rider is always near. The stamp
`<PREFIX>_TARGETS "generic"` is constant on every artifact until a second target exists: zero information (D77,
no silent defaults: a default that is never varied is a latent field). [STAMP-REVIEW] (under [IFACE-PUSH],
plan:~1324-1334) leans to REPLACING the informational `#define` stamps with a structured comment block, so a
new `#define` stamp now is likely churn the push removes, and Q2 (rx_info lists variants) is also IFACE-PUSH.
The pcrec-iface-push-later rule says new stamps go "the usual D76 way" meanwhile, so it is allowed, but
costly alone: bump, readers by grep, identity re-pin, spec hunk, and the G2 baseline then must be the stamp
commit. Recommendation: land the stamp in the SAME abi event as the first change that can make it non-constant
(the list option), and make G2's baseline the pre-change commit with the declared +1 line per artifact
(a declared-move mechanism exists for facts: emit_sweep.py:1201-1233). If Frank wants the stamp earlier for
the kit, ride the next scheduled abi event, not a dedicated one.

### MEAS-12 (CONFIRMED, overlap) Overlaps and triggers
- [MEMFN-RTDISPATCH] (plan row): trigger is "more than one architecture selected for runtime support AND a
  hot-loop SIMD form exists -- possibly theoretical today". Measured today: vrun rows are pre-check/find-start
  helpers on ~0.5% of patterns (22/4,624). The end state is built for this one row; the note retires its `freq`
  column but does not mark the row superseded/trigger-met. State which, and that the row's measurement trigger
  is not met by §8 (a size count), only by a SIMD form that beats scalar on a hot loop.
- [IR-FORM] member (4) (kit planning vs emitting) has no row; §2 designs "emitter-shaped" for it. The
  `target.features` fact, `needs` column and bracket marks are exactly what that split would serialise: any
  build of this should wait on or be written as that member, not before it (D153 remodel-first: opt rows
  touching a remodel site wait). Overlap with [DFAREC]/[VMREC] is real: per-variant stems and stamps
  multiply the emitters' stamp lines those rows are re-recording.
- Kit lane/memfn-s2e (span_cards stage 2) rewrites runcmp.c/formhash.c/kit.h which §3 cites: SUSPECTED
  conflict to re-check by the premise lens, not mine.
- [IFACE-PUSH]: rx_info variants (Q2) and the stamp comment block belong there; the flag-bit counter
  (55/64) is touched if `-ftargets` style options are public (flag follows caller effect: a list option is
  a capability, not a deny).

### MEAS-13 (SUSPECTED, cost) Costlier must prove more: nothing in the note names the measured benefit
The only benefit evidence is the linux_results probe cost (0.4-0.6 ns/call) and the kit's forms. The note
prices size (xN) and test time (unpriced) but no speed win from a SIMD variant over the generic one on a
real cell, which is D188's own timed-when-both-hold half. Trigger per piece: stamp (none yet), `needs`
column / attributed regions (G1: the first SIMD form that cannot be written with `#if`), dispatcher (a hot-loop
SIMD form that beats scalar on >1 target), per-variant tests (a second variant in a fielded artifact). Each
should name its measurement before the owner's go.

## PROBED-AND-HELD
- G3 naming premise: emitted `-fmemfn-simd` `(?i)cat` at `-p rx` and `-p rx_v3`, compiled -O0, `nm`: 27 symbols
  each, global overlap only undefined libc (`memchr`, `__stack_chk_fail`). Held (1 pattern, 2 stems).
  Note `rx_info` is a global data symbol per stem (Q2).
- §8 data point `(?i)cat` reproduced exactly (2386/224, 2618/224, 2922/224; 8 size runs).
- `-fno-memfn-simd` byte-equals the default (diff: filename line only; 1 pattern, 3 emits).
- levels.def identical on main and 5b6cf41aa (2 levels).
- `--ref` exists and uses git archive of the reference; `--extra` exists, repeatable, both sides.
