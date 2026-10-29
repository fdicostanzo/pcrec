# p910 — designs for primed candidates P9 (leading keyword set) and P10 (presence reject)

Lane p910 (opus), 2026-10-29, branch `lane/p910` at main b05ccfc0b. DESIGN AND MEASURE ONLY: nothing
under `src/`, `cli/`, `lib/`, `memfn/` or `tests/` changed (no build go). Every number is a user-space
INSTRUCTION count (`instructions:u` read by `perf_event_open` around the bench's own find-all, best of
5-7 repeats, `taskset -c 7`; repeatable to a few instructions) unless it says cycles. The box was NOT
quiet (queue jobs 680-ic3-test and others ran throughout), so cycle figures are ratios only and no
wall-clock claim is made. Twins are hand edits of pcrec's OWN emitted `rx.c` in scratch, built by the
generators in `docs/dev/lanes/p910_evidence/` (their diffs are there too), never pcrec code.

## Summary

1. **Premise holds.** All 10 cells resolve to patterns that compile at HEAD (b05ccfc0b, pcrec
   0.2.0-beta) with the bench's flags; stamps below.
2. **P9: the brief's mechanism is half right, and the half that is wrong is the useful part.** The
   five cells do not lack a keyword-set candidate finder in general; they lack a CANDIDATE SKIP AT
   THE SECOND IDLE STATE. A leading `\b` gives the forward scan two seed states (previous byte
   non-word / word). The emitted skip is gated on `forward_state == 0`, so on word-dense text the
   machine sits in the other seed (state 22) and steps the full table on EVERY byte: 65,525 of
   65,536 bytes of `t-letters-064k`, 16.0 instructions/byte, `perf` 100% in the prefilter's step
   loop. The scan-edge pass refuses that state as an edge (its precondition (8): the start skip
   RESEEDS into it) and the stay-skip picker refuses it (63 stay bytes < the 192 threshold).
   - **Fix (twin `autofind`): the start skip runs at EVERY seed state, and it is the window FIND**
     over the leading alternation's per-offset sets (the `kset_walk` fact) plus the look-behind term
     the leading `\b` implies at offset -1. Answer-identical on 350 files / 4,002 matches (span
     hashes). Instructions vs today's auto: x1.98 (ctx throughput), x1.24-1.40 (bounded short),
     x1.64 / x1.59 (dense `a ` / `ab ` counter-subjects), x1.33 (word prose), x1.03 (level-context
     logs), x1.11-1.16 (stress). Never slower in instructions in any regime measured.
   - **The DFA-local alternative (`autoseed`: a stay skip at the word seed) is REJECTED by its own
     numbers:** best on random letters (x2.28-2.56) but SLOWER than today on short-word text
     (x0.88 instructions on `a a a`, x0.95 on prose) — the short-run loss P4 is about.
   - **level-context is not a P9 cell at the scalar layer:** 97-98% of its bytes are already
     skipped; no twin moves it beyond x1.03-1.13. It trails rust only (x3.78) and is AHEAD of jit;
     its gap is the SIMD multi-literal search (rust's Teddy), i.e. the `-fmemfn-simd` thread.
     The same holds for the remaining ctx gap to rust after the fix (scalar walk ~7-8 instr/B).
3. **P10: confirmed as selflip found, and the pre-scan framing holds.** The PRESENCE slot's row
   `one-attempt` (G2) declines the required-byte check on a one-attempt route; forced VM emits it.
   G2's premise ("the check would scan the window the attempt reads anyway") is false on rate:
   memchr runs ~0.038 cycles/B here, the DFA attempt 2.64 (email-owasp) and the hybrid's 7.4
   (iso8601). A plain pre-check (twin `pre`) is x83-94 on the hazard subjects and x560 WORSE on
   1 MiB prose. **The design is a PACED presence check** (twin `paced`): the attempt runs as
   today; only when it has read `max(D0, rest >> 6)` bytes and is still alive does the check run,
   once. Hazard subjects x26-35 fewer instructions (x27-49 cycles); attempts that die early never
   reach it; a worst-case witness built to hurt it costs x1.19-1.79 instructions (bound: 1 + 64/r,
   r = measured rate ratio, <= x2 here). It is a deterministic online schedule with a proven
   bound, not a route choice and not a density estimate, so it does not contradict selflip.
   **Codegen risk found:** any edit to the direct-threaded attempt function moved gcc's register
   allocation (8.0 -> 10.1-12.1 instr/B on a long-surviving attempt, even for the one-line `pre`
   twin); the build carries a hot-loop identity gate.
4. **Shared mechanism:** P9 and P10 share none with each other or with P1. P9 shares the DFA
   loop's skip/edge block with P4+P8 (the same admission question from the other side); P10's
   checkpoint must count table steps, not scan-edge bytes, to compose with P4+P8.
5. **Census (jobs 690/691, both GREEN) and corrections to the first draft.** P9: 34 bench
   artifacts (not 5-6 cells) have the uncovered second seed, 28 scan-shaped; only 6 are measured.
   P10: 19 bench ids carry `one-attempt` with a required byte, 15 twinned, 0 answer differences
   over 1,222 file-runs; `paced` gains x14-20 on THREE patterns (email-owasp, iso8601 and the
   unlisted email-nested-plus), is neutral to +4% on the rest, worst single file x1.37. See
   "Corrections" below.

## Premise test

| cell | pattern (bench file) | compiles at HEAD | auto route stamps |
|---|---|---|---|
| bounded ctx-lazy-64 / -256 / -1024 | `\b(?:fail\|abort\|panic)\b.{0,N}?\b(?:disk\|memory\|socket\|quota)\b` | yes | VM, `collapsed-prefilter` (dfa overflowed >32000 states), VM prefilter `hybrid` / `count-collapsed`, DFA prefilter `first-class-bounded`, REQ_BYTE 97 (`a`), REQ_RUN none, SCAN_EDGE none |
| bounded ctx-greedy-256 | same, `.{0,256}` | yes | same |
| loglines level-context | `\b(?:ERROR\|FATAL\|CRIT)\b.{0,200}?\b(?:timeout\|timed out\|refused\|denied\|unreachable)\b` | yes | same shape, REQ_BYTE 101 (`e`) |
| capability email-owasp | `^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$` | yes | DFA, `DFA_SCAN attempt`, REQ_BYTE 64 (`@`), **REQ_WHY one-attempt** (forced VM: `emitted`) |
| capability moment-iso8601 | `^\s*((?:[+-]\d{6}\|\d{4})-...)$` | yes | VM + hybrid, `attempt`, REQ_BYTE 45 (`-`), **REQ_WHY one-attempt** (forced VM: `emitted`) |
| capability trim-nested-star / evil-alt-nested / pwd-strength-chain | `^(\s+)*$` / `^(([a-z]+)*)+$` / lookahead chain | yes | VM + hybrid, attempt, **REQ_BYTE none** |

Premise holds. One correction to the P10 cell list: only email-owasp and moment-iso8601 have a
required byte, so only they are P10 cells; trim-nested-star, evil-alt-nested and
pwd-strength-chain have nothing to reject on (their x2-x4 is the hybrid's two passes over a
matching run, selflip's "one clean separator", and [SCANEDGE-SET]'s territory; the targets file
already credits the landed scan-edge work with trim-nested-star).

## P9 stamps and twin

**Where the time goes (auto, ctx-lazy-64, `t-letters-064k`).** The hybrid's `rx_prefilter` is a
forward unanchored DFA with a candidate skip:

    if (forward_state == 0 && last_accept_position == (size_t)-1) {  /* the ONLY skip */
        while (... && !rx_start_bytes[subject[scan_position]]) scan_position++;
        ... forward_state = rx_forward_seed_state[class(subject[scan_position - 1])];  /* RESEED */
    }

The seed table is `{0, 0, 22, 22, ...}`: after a non-word byte the machine starts in state 0,
after a word byte in state 22 (the leading `\b` cannot hold there). Both are IDLE states (no
thread but the unanchored start loop). State 22 self-loops on the 63 word bytes and leaves to 0 on
every other byte. A counter planted in the step (evidence `mk_p9_twins.py` era, `*-autocount`):

| subject | stepped at state 0 | stepped at state 22 | stepped elsewhere | skipped |
|---|---:|---:|---:|---:|
| ctx `t-letters-064k` (65,536 B) | 0 | **65,525** | 0 | 11 |
| ctx stress (1 MiB, keywords + near misses) | 7,784 | 503,223 | 306,472 | 321,337 |
| level-context `t-1024k-fail` | 2,343 | 21,872 | 2,343 | **1,022,063** |
| level-context `t-1024k-hit` | 2,630 | 32,093 | 21,655 | **991,205** |

`perf record -e instructions:u` + `perf annotate`: 100% of samples in `rx_prefilter`, on the
table-step instructions (transition load `movzwl`, accept test `cmpb`, `cmov` of the last-accept).
Per byte: auto 16.0 instructions, ~6.5 cycles; forced VM 12.9 (its first-class start walk fires an
anchored attempt on the 11.5% of letters in `{a,f,p}`; each dies on `\b`).

Why nothing else catches state 22: `pick_skip_states` (emit_dfa.c) takes a stay skip only at a
state staying on >= 192 of 256 bytes (an M2.1 constant) and state 22 stays on 63; the scan-edge
pass (`src/opt/scanedge.c`) finds state 22 scan-shaped (unbounded self-loop, uniform exit) but
precondition (8) refuses a head the prefilter's reseed can install mid-body, and state 22 is
exactly that head. The pass's own comment records the population: "9 of the 11 corpus artifacts
this rule cost an edge ... all `\b`/`\B` shapes".

**Twins** (all from the shipped artifacts; generators and diffs in `p910_evidence/`):

| twin | what changed |
|---|---|
| `autoseed` | DFA-local: state 22 gets a stay skip over its own stay set (read off the artifact's tables) |
| `autofind` | the brief's shape inside the hybrid: the skip runs at EVERY seed state (0 and 22) and is a window FIND: `(c == 0 or s[c-1] not \w)` and `s[c+j] in S_j`, j = 0..3 (S_j the alternation's per-offset sets: `{a,f,p}{a,b}{i,n,o}{i,l,r}`, the `kset_walk` fact's sets); scalar walk on offset 0 |
| `autofind2` | as autofind, the walk tests offset 0 and the -1 term together, branch-free |
| `vmfind` / `vmfind0` / `vmfindm1` / `vmfind2` | forced-VM artifact, its first-class start walk replaced by the window FIND (with / without the -1 term / walking on the -1 term / branch-free pair), anchored VM verify at each candidate |

**Answer identity:** 0 differences in match count and span hash across every variant, 350 file
runs (bench throughput + short subjects of both sets, two seeded 1 MiB stress subjects carrying
the keywords, near misses and both context sets, two edge subjects) and 4,002 matches per variant.

**Instructions, find-all, sum over the group (auto / twin):**

| pattern | group | vm | autoseed | **autofind** | vmfind | vmfind0 |
|---|---|---|---|---|---|---|
| ctx-lazy-64 / -256 / -1024 | throughput (5 files) | x1.25 | x2.28 | **x1.98** | x2.01 | x2.03 |
| ctx-greedy-256 | throughput | x1.40 | x2.56 | **x2.23** | x2.26 | x2.28 |
| ctx-lazy-64 | bounded short (49) | x1.16 | x1.27 | **x1.29** | x1.46 | x1.43 |
| ctx-lazy-256 / -1024 | stress | x0.85 / x0.71 | x1.12 / x1.11 | **x1.14 / x1.13** | x0.92 / x0.76 | x0.89 / x0.74 |
| ctx-lazy-64 | counter `a ` x 32768 | x0.52 | **x0.88** | **x1.64** | x1.77 | |
| ctx-lazy-64 | counter word prose 1 MiB | x0.97 | **x0.95** | **x1.33** | x1.35 | |
| level-context | throughput (12 files) | x1.13 | x1.01 | **x1.03** | x1.07 | x1.03 |
| level-context | short (112) | x1.14 | x1.00 | **x1.03** | x1.04 | x1.04 |

(`t-letters-064k` per byte: auto 16.0, autoseed 7.0, autofind 8.1, vmfind 8.0 instructions;
cycles, ratio only and noisy on this busy box, auto 6.4-6.6, autoseed 1.0-2.1, autofind 1.9-5.9. Counter-subject per byte:
`a ` auto 23.0, autoseed 26.0, autofind 14.0; prose auto 10.4, autoseed 11.0, autofind 7.8.
`p9_results.tsv.gz`, `p9_counter.tsv`.)

Readings:
- The forced VM's x2.1-2.4 bench win on the letters subjects is the same fact seen from the other
  side: its start walk is a cheap table walk; auto's is a full DFA step at state 22.
- The window FIND wins in every regime because it never enters the step at an idle state; the
  stay skip at state 22 wins only where words are long (it pays a loop entry and a mispredict per
  word). That is the decision between them, and it is measured, not argued.
- The -1 term matters little at the scalar walk (vmfind vs vmfind0 within 2-6%): the multi-offset
  sets already reject the `{a,f,p}` letters. Walking ON the -1 term (vmfindm1) is best on letters
  and worst on logs (x0.79): a scan-position choice, which is the kit's (D157), on its priors.
- Against the bench: jit is x1.84-1.91 faster than auto on these cells; the fix removes x2-3 of
  auto's cost on the dominant subjects, so pcrec would sit at or ahead of jit (PROJECTION from
  instruction and cycle ratios, not a timing). Rust's x19 is a vector multi-literal search; the
  scalar walk stays ~7-8 instructions/byte, so most of rust's lead is the SIMD half and is left
  to the `-fmemfn-simd` thread, as the brief asked.

## P9 design

**Goals.** (G1) on word-dense subjects, a pattern with a leading context assertion stops paying a
full DFA step per byte at an idle state: ctx throughput >= x1.8 fewer instructions, bench cells
at or ahead of pcre2-jit. (G2) no regime regresses: every counter-subject (dense starts, short
words, prose, logs) within the null band or better. (G3) one mechanism: the existing start-skip
site, not a new skip kind. Priority G2 > G1 > G3. Non-goals: SIMD multi-literal search (the
kit's SIMD layer); the VM route's own start scan (vmfind shows the same FIND helps it; that is
the same site on another route, a follow-up, not this row).

**The mechanism, general form.** A forward unanchored machine has a SEED FAMILY: one start state
per look-behind context class (`rx_forward_seed_state`). Every seed is idle. Today the start skip
(the kit's PF site) runs at seed 0 only; the general statement is: **the start skip runs at every
seed state, and its predicate is the candidate WINDOW: the per-offset sets every match carries
from its own start (`kset_walk`) plus the look-behind term the leading context implies at offset
-1.** For `\b` with a word-only first set that term is "`s[c-1]` not a word byte, or `c` is the
subject start"; for `\B` it is the word bytes; for `(?m)^` it is `\n` (the MLINE site already sends
exactly such a -1 term); for a width-1 lookbehind it is its set. These are [DD-11.5]'s span-context
facts (D168 part 1: "per-offset sets at negative offsets ... `\b` via the fold"), so P9 adds no fact
of its own: it consumes `kset_walk` and the span-context producer.

**As a declared first-match row** (emit_dfa.c's candidate table, START slot; the predicate is over
the compile alone):

| order | row | applies when | the start skip |
|---|---|---|---|
| 1 | `seed-window` (new) | the forward scan has a seed family of >= 2 states AND the window has a term the offset-0 set lacks (a -1 context term, or a `kset_walk` set at offset >= 1) | runs at every seed state; the PF site states the whole window (offset -1 .. k-1); after a hit the state is reseeded from `s[c-1]` as today |
| 2.. | today's rows (`first-class-bounded`, `byte-class`, offset rows ...) | unchanged | at seed 0, as today |

Deny flag: one new `-fno-seed-window` bit (the change's alpha OFF arm, D144 item 4), so the bench
can A/B it as `pcrec-auto-noseedwin`.

**Correctness argument.** Each seed state is the start of the unanchored loop under one context;
skipping from a seed to the next position satisfying a NECESSARY condition of every match start,
then reseeding from that position's previous byte, is what today's state-0 skip already does. The
window terms are necessary (kset_walk's own soundness argument; the -1 term is the leading
assertion's consequence, passed as an over-approximation exactly as the walk passes assertions).
Scan-edge precondition (8) is untouched: the reseed still writes only seeds, and a seed that is an
edge head is still refused; this row makes the refusal cost nothing because the head is never
stepped at.

**What pcrec hands the kit (facts only, D157).** The PF site gains: SET terms at offsets 1..k-1
(the `kset_walk` sets, OPTIONAL terms exactly as the OFS site's), and one READS-BELOW SET term at
-1 (the context set, with the "satisfied at the subject start" bit the MLINE site states). Which
term the walk scans on, whether the -1 term is tested at all, and the form, are the kit's
(vmfindm1 vs vmfind shows the choice is regime-dependent; the kit's rate priors decide).

**Population (compile census, corpus + bench).** Job 690 (5,588 patterns, one `--features all`
compile each, no subject run; `p910_evidence/census.tsv.gz`): corpus 4,763 compiled of 5,196 (433
refused: 431 `rc1`, i.e. constructs pcrec rejects by design, plus 2 `rc125` that are not
explained here and not counted); bench 368 of 392 (24 refused, all `rc1`: unsupported modules,
e.g. `syntax/cnd-group`, `utf8/cls-w-ucp`, and the altwide `clsa/clsd/s/w` 1024+ rows). None of
the ten premise cells is among the refused. Counted from the emitted C (a `rx_forward_seed_state`
table with >= 2 distinct values, and the `forward_state == 0` skip gate), not from the row's
predicate:

| population | compiled | seed family >= 2 | of those, state-0 skip gate present | seed shape `scan` (single exit door) | `scan` with stay >= 60 (the word seed) |
|---|---:|---:|---:|---:|---:|
| corpus | 4,763 | 281 (279 two seeds, 2 three) | 213 | 106 | 62 (of the 213 gated) |
| bench | 368 | 34 | 33 | 28 | 25 |

So the defect is not five cells: **34 bench artifacts** (33 gated) carry a second idle seed the
skip never covers, 28 of them scan-shaped, 25 on a word-class seed (`\b...` patterns: hex8, bignum,
uuid, `\bcat\b`, aws key, github pat, the isbn/luhn/member twins, `level-context`, the altwide
`wb-256/512`). This lane MEASURED only the five ctx cells and `level-context` (above); the
other 28 are admitted by structure and UNMEASURED, and a short-word subject is exactly where the
measured DFA-local alternative lost, so each needs its card row (d), not an assumption. The one
ungated bench member (`utf8/asr-b-midchar`, lone `\B`) has no start skip at all and is not a
P9 customer.

**Remodel overlap (D153).** [DD-11.5] (the -1 term is its span-context producer's output; that
producer currently DECLINES on these artifacts, `span_facts` "decline:erased-nfa" on the
count-collapsed rung, so P9 either waits for the producer to answer on the collapsed language or
reads the context from the seed family itself); [MEMFN] PF site (delegated; the window is new
facts on an existing site, a kit byte move = pcrec abi event in the same commit); [MATCH-SPLIT]
none. P4+P8 shares the loop block (see Shared mechanism).

**Existing rows.** [CTX-PREFILTER] is lookaround lowering, not this. [START-DENSE] is the retry
slot's adaptive rule, not this. [OPT-LITSCAN] owns literal-run forms; a keyword SET window is not a
run. [OPT-K] (prefix_k.c) picks ONE offset for a skip; the window is all offsets at once. No row
owns "idle seed states get the skip"; this is a new row, or a member of P4+P8 if Frank wants the
loop's skip/edge admission as one row.

**Standing questions.** (1) Regime: instruction counts of the bench's find-all on each regime
named above (throughput no-hit, short, dense starts, short words, prose, logs, stress with hits);
a different regime DOES flip the autoseed-vs-autofind choice, which is why the row takes the
FIND. (2) Independent control: answer identity against today's artifact (span hashes) and the
forced VM; the counter-subjects are regimes chosen to make the twin lose, not derived from its
code. Population counted by the census from the emitted C (seed table present, state-0 gate),
not from the row's own predicate. (3) Regeneration: no data file; the row moves emitted bytes on
every admitted artifact (an abi event, D76/D94, plus the PF site's kit byte move).

## P10 stamps and twin

**Where the time goes.** email-owasp auto is a direct-threaded DFA attempt (`DFA_SCAN attempt`,
fully `^`-anchored, `start_max = 0`): on `t-evil-match-60k` (61,440 random lowercase letters, no
`@`) it walks the whole subject in the `[a-zA-Z0-9_+&*-]+` states, 8.0 instructions / 2.64
cycles per byte, then fails at the end. iso8601's hybrid prefilter is the same attempt shape over
the `^\s*` run, 9.0 instructions / 7.4 cycles per byte (the threaded dispatch over six `\s`
classes). Forced VM on both: `memchr(subject + search_from, '@' or '-', ...)` first (REQ_WHY
`emitted`), 0.096 instructions / 0.038 cycles per byte, reject. selflip measured the same.

**The decline is one declared row.** emit_dfa.c's PRESENCE slot, row 2 `one-attempt`
(`req_one_attempt_applies` -> `req_route_one_attempt`): "G2: the route tries exactly one start
position, and on the VM that one attempt is linear ..., so the check would scan the window the
attempt reads anyway". The premise is about BYTES; the cost is in CYCLES, and memchr is 69x
(email) to 194x (iso8601) cheaper per byte here.

**Twins** (`mk_p10_twins.py`, mechanical over any one-attempt direct-threaded route):

| twin | what changed |
|---|---|
| `pre` | the check at the attempt's entry (= the forced VM's placement, = deleting row 2) |
| `paced` | every state's existing end test reads a local bound set to `start + max(D0, rest >> 6)` (D0 = 16); at that checkpoint, once: if the byte is absent from `[start, n)` return no match, else the bound becomes `n` and the attempt resumes in the same state. EOL views keep reading the real end |
| `paced2` | control: a call-free core that RETURNS at the checkpoint and is re-entered in its state |

**Answer identity:** 0 differences over 208 file runs per variant (capability throughput 18 +
short 75, plus 12 witnesses built for this: late `@`/`-` that matches and that fails, long runs
dying right after the checkpoint, short subjects, empty).

**Instructions, find-all (auto -> twin):**

| subject | email auto | pre | paced | iso8601 auto | pre | paced |
|---|---:|---:|---:|---:|---:|---:|
| `t-evil-match-60k` (hazard) | 491,626 | 5,905 | **16,491 (x30)** | 154 | 5,944 | 155 |
| `t-evil-nearmiss-16k` | 131,184 | 1,681 | **4,523 (x29)** | 154 | 1,720 | 155 |
| `t-trim-match-60k` (hazard) | 112 | 5,905 | 105 | 553,106 | 5,944 | **15,571 (x35)** |
| `t-trim-nearmiss-16k` | 112 | 1,686 | 105 | 147,610 | 1,725 | **4,312 (x34)** |
| `t-1m` prose (attempt dies at once) | 176 | **98,449 (x0.002)** | 193 | 154 | 98,489 | 155 |
| `t-hyb-digits-4k` | 32,874 | 529 | 1,259 (x26) | 190 | 569 | 195 |
| short subjects (75), sum | 13,374 | 9,144 | 12,843 | 12,979 | 12,635 | 13,172 |
| witness: 30,000 class bytes, a killing byte, 1 MiB without the req byte (iso: whitespace) | 240,112 | 101,265 | 286,663 (x0.84) | 270,154 | 101,270 | 269,856 (x1.00) |
| witness: 19,800 letters (dies right after the checkpoint) | 158,512 | 100,310 | 283,959 (x0.56) | | | |
| witness: 60,000 class bytes then a matching tail | 480,239 | 605,943 | 665,985 (x0.72) | 1,260,998 | 1,326,687 | 1,326,720 (x0.95) |

Cycles on the hazard subjects (ratio only): email 162,222 -> 5,975 (x27), iso8601 453,090 -> 9,226
(x49); the forced VM 2,392 / 2,270.

Readings:
- `pre` is the forced VM's answer and is unusable: x560 worse on 1 MiB prose (the attempt dies at
  byte 5; the check reads the whole MiB). This is selflip's sign flip, reproduced.
- `paced` keeps prose at its 150-200 instruction cost (it never reaches the checkpoint) and takes
  x26-35 of the x83-94 on the hazard subjects. The rest of the gap to forced VM is the bound's
  price: the attempt first reads rest/64 bytes.
- **The worst-case witnesses cost x1.19-1.79 instructions, and most of that is NOT the check.**
  Even `pre`, which adds one call before the loop and nothing inside it, moved gcc's register
  allocation of email's threaded loop: 8.0 -> 10.1 instructions/byte (a `lea` reload of the
  target table per step); `paced` 11.1, `paced2` (no call in the core at all) 12.1. iso8601's
  loop moved x1.05. So the twin measures the mechanism and the bound; the hot-loop cost is a
  codegen sensitivity of the direct-threaded attempt that the build must gate (below), not a
  property of the checkpoint.

**Is this the route choice selflip found no static rule for?** No. selflip asked "VM or auto?" at
compile time and showed the answer flips by subject. This row does not choose a route: the route
stays auto's DFA attempt; it places an EXACT necessary-condition test (absence of a required byte
proves no match) at a point where its worst-case cost is bounded by the attempt's own cost so
far. The deciding runtime fact selflip named ("how far the attempt survives vs the distance to
the byte") is exactly what the checkpoint observes, without estimating anything: the attempt's
survival IS the trigger. It is the classic ski-rental schedule: total <= (1 + 64/r) x the
attempt's cost in the worst case (r = DFA cost per byte / memchr cost per byte), and on a hazard
subject the cost is ~(1/64 + 1/r) of today's.

## P10 design

**Goals.** (G1) a one-attempt route never walks a whole long subject that lacks a required byte:
hazard subjects within x2 of the forced VM's reject (instructions). (G2) attempts that die early
pay nothing measurable: short and prose cells within the null band. (G3) the worst case is
BOUNDED and stated: <= x2 of today on any subject on the slowest box. Priority G3 > G2 > G1.
Non-goals: a route switch; a density estimate; a byte cap tuned to a benchmark (PCRE2's apparent
behaviour, INFERRED from the bench numbers only: jit rejects the 60 KiB subjects at memchr speed
but answers 1 MiB prose in 22-29 ns, which reads like a length cap on its required-code-unit
search; not read from PCRE2's code).

**The row** (PRESENCE slot, replacing row 2's unconditional decline; first match):

| order | row | applies when | verdict |
|---|---|---|---|
| 1 | `presence-none` | no necessary byte and no run | none (unchanged) |
| 2 | `one-attempt-paced` (replaces `one-attempt`) | the route tries exactly one start (today's `CAND_BOUND_ONE` reads, unchanged) | the check is DEFERRED to a checkpoint inside the attempt: after `max(D0, (n - start) >> K)` generic-path table steps; once; absent -> no match; present -> continue |
| 3.. | `dominated`, `set-leads`, `emitted` | unchanged | unchanged |

`REQ_WHY`'s token set is CLOSED (rowcon customers): `one-attempt-paced` is a new token, an abi
event with its spec hunk (D80) and identity re-pin (D76/D94).

**The two constants are derived, not tuned** (memory: suspect tuning constants):
- `K` from the measured rate ratio r = (attempt cycles per table step) / (memchr cycles per byte):
  2.64 / 0.038 = 69 (email DFA), 7.4 / 0.038 = 194 (hybrid), selflip 53 (0.38 vs 0.0072 ns/B).
  `K = floor(log2(min r))` = 5 with selflip's 53, 6 with this lane's 69; the bound is
  1 + 2^K / r, so K = 5 bounds the worst case at x1.6 on every measured route and K = 6 at
  x2.2 on selflip's ratio. The twin used K = 6. The measurement card below re-measures r on the
  three boxes (Zen 1's 2x128-bit AVX2 memchr is the slowest, so its r is the binding one).
- `D0` = memchr's fixed call cost in table steps (so a short subject never pays a call it cannot
  win back): measured per-call cost / per-step cost; the twin's 16 is a placeholder, labelled
  UNMEASURED DEFAULT until the card fills it.

**Where the checkpoint lives.** In the per-state end test of the GENERIC path only (the test every
direct-threaded state already has), so it counts table steps. A scan edge or stay skip consumes
bytes at near-memchr cost and keeps its own bound; counting its bytes would fire the check early
for no gain. That is also the composition rule with P4+P8.

**Build gate (the codegen finding).** The attempt's per-byte instructions on a long-surviving
witness (60,000 class bytes then a match) must be IDENTICAL to today's, per admitted artifact
class (DFA attempt, hybrid prefilter attempt). Three twin placements all perturbed gcc's loop; the
build finds a placement that does not (candidates: the bound in the register `subject_length`
already occupies with the real end spilled; the check behind a `cold` noinline call; a sibling
entry), and the gate decides, not argument.

**What pcrec hands the kit.** Nothing new: the check's memchr is the existing presence (PRE) site
with the same facts; only WHERE pcrec places its use moves. If the kit later owns the attempt
loop, the checkpoint is a hook the loop states, not a kit method.

**Population (compile census).** Same job 690 (`census.tsv.gz`): `REQ_WHY one-attempt` is stamped on
**267 corpus** artifacts (266 with a required byte; 188 VM, 79 DFA; 209 `DFA_SCAN attempt`, 58 with
none) and **19 bench** artifacts, all with a required byte (15 distinct patterns once the
`sentinel/` copies are folded; 13 DFA, 6 VM; 18 `attempt`). Job 691 (`p10_controls.tsv.gz`) ran
the `pre` and `paced` twins over all 19 ids' own subject sets (throughput + short, 47-92 files
each): 15 twinned (1,222 file-runs per variant), 4 not (`syntax/anc-g-uc`, `unusual/va-tenant`,
`utf8/asr-a-z`, `utf8/lit-anchored-run`: not a direct-threaded one-attempt route, the generator
asserts; no twin was hand-built for them).

- **Answer identity: 0 differences** (match count + span hash) of `auto` vs `pre` vs `paced` over
  all 1,222 file-runs. Weak as a MATCH test: the bench subject sets carry only 37 matches in
  total (they are reject-heavy by design), so the match side rests on the 208 earlier file runs
  and their 12 witnesses.
- **Who gains** (sum of instructions over the pattern's set, `paced`/`auto`): email-owasp 0.06
  (x16), moment-iso8601 0.05 (x20), **email-nested-plus 0.07 (x14)**; cycles x15 / x15 / x13.
  Their best single files are x30-36 (`t-evil-*`, `t-trim-*`: the hazard pair above).
  `ipv4-near-miss` 0.86-0.93, `uuid-near-miss` 0.92-0.93 (small gains: the checkpoint finds the
  byte absent at D0 and returns early). `anc-a-uc`/`anc-caret` 1.00, `winpath-near-miss` 1.02,
  `logparse-atomic` / `-removed` **1.04** (cycles 0.99; a required byte present on every subject,
  so the check is pure overhead: 3-7% instructions, hidden in cycles).
- **Worst single file:** x1.37 instructions (`email-owasp`, `t-hyb-embed-1k`, 350 -> 480 on a
  1 KiB subject), x1.36 on a 24-byte email line; 125 of 1,222 files above x1.05, 9 above x1.25,
  all of them subjects of a few hundred instructions where the fixed call cost dominates.
- **`pre` (the forced VM's placement) is unusable on 7 of 15:** `winpath-near-miss` x44 in sum
  (x864 on its worst file), `logparse-atomic` x1.77, per-file worst x466-x661 on the email /
  iso8601 / logparse patterns' 1 MiB subjects. `paced` has no such file.
- **Not measured:** the 267 corpus artifacts (no subjects; the corpus is `.rxt` rows, not
  throughput files), the 4 untwinned bench ids, and the Zen 1 / Mac ratios the card needs.

**Remodel overlap.** [MATCH-SPLIT] none; [OPT-REVEND] / [COMPOUND] none on one-attempt routes
(they own LOCATE/rev-end, which `dominated` already reads first); P4+P8 (scan edges change the
per-byte cost the bound assumes; handled by counting table steps); [MEMFN] PRE site unchanged.

**Existing rows.** [ADAPTIVE-ARM] holds selflip's candidate T2 (`one-attempt-deferred`, filed,
not built, under Frank's 2026-10-21 adaptive-methods caveat). This design is that member with the
twin, the bound and the codegen gate; whether it is "adaptive" in the caveat's sense is a
question for Frank (below). [OPT-REQBYTE] (completed) built the check; [SEL-COST] is the route
question this does not ask; targets_2026-10-26's proposed [REQBYTE-REJECT] was never filed.

**Standing questions.** (1) Regime: per-call instruction counts on the bench's capability subjects
(short, throughput, hazard) and adversarial witnesses; the regime that would flip it (an attempt
that dies just after the checkpoint on a long subject without the byte) is bounded, measured
x0.56 instructions on the twin, and the bound is the design. (2) Independent control: answer
identity against today's artifact and the forced VM (span hashes); the witnesses are constructed
from the bound's worst case, not from the twin's code; population counted by the census from
emitted stamps. (3) Regeneration: r and D0 are measured constants; re-measuring moves K/D0 and the
emitted bytes of every admitted artifact: an abi event, and a measurement-set entry if they go
into `measure_store/` (D166) rather than limits.def.

## Corrections to the first draft (after the census)

1. **P10 cell list was short by one.** The Premise test says only email-owasp and moment-iso8601
   have a required byte and are P10 cells. The census says 19 bench ids (15 distinct) are
   `one-attempt` with a required byte, and the controls show a THIRD gaining pattern,
   `capability/email-nested-plus` (VM route, byte `@`): x14 instructions, x13 cycles. The
   statement "trim-nested-star / evil-alt-nested / pwd-strength-chain have nothing to reject on"
   stands (no required byte). `anc-*`, `ipv4/uuid-near-miss`, `winpath-near-miss`,
   `logparse-atomic` are admitted too but gain nothing.
2. **"Hot-loop cost is not the check" was not the whole story for the neutral cases:**
   `logparse-atomic` (+4% instructions, 0% cycles) and the short email lines (x1.36) are
   admitted, unrejectable, and pay a small fixed price. The design's G2 ("within the null band")
   holds in cycles but not in instructions for these; the card should read cycles for G2 and say
   so. The bound claim ("<= x2 of today") held on every file (max x1.37).
3. **"Five cells" for P9 under-stated the population** (34 bench artifacts, 281 corpus). The
   mechanism claim (a skip is missing at the second idle seed) is unchanged; the breadth is new
   and unmeasured. Nothing in the census contradicts the central claims of either design.
4. **The identity claim for P10 was 208 file runs** (draft); with job 691 it is 1,222 more, but
   the bench sets hold only 37 matches, so the match-bearing evidence is still the first 208
   plus the witnesses, and I am saying so rather than reading 1,430 runs as match coverage.
5. **Evidence note:** the draft's `CLAUDE.md` for `p910_evidence/` listed `census.tsv.gz` and
   `p10_controls.tsv.gz` as pending; they are committed now.

## Shared mechanism

- **P9 and P10: none.** P9 is a start-candidate skip at idle states of an unanchored scan; P10 is
  the placement of a presence check inside an anchored one-attempt route. Different routes,
  different slots (START vs PRESENCE), no shared site.
- **P9 and P1 (reverse walk, revwalk_report.md): no.** P1 recovers a start backwards from an INNER
  landmark; P9's keyword set is at offset 0 (the landmark IS the start; no walk back). Both feed a
  kit FIND site, which is shared infrastructure, not a shared mechanism.
- **P10 and P1: no** (P10's routes are anchored; P1 is for unanchored inner landmarks).
- **P9 and P4+P8: the same loop block from the other side.** The skip/edge admission in the DFA
  loop (scan-edge preconditions, the stay-skip threshold) is what leaves the seed state stepped;
  P9 answers it with the start skip instead of an edge, and the autoseed twin is a measured data
  point for P4's pricing question (a skip on short runs loses: x0.88 on `a a a`). If Frank wants
  one row for "what the DFA loop skips, where", P9 is its third member.
- **P10 and P4+P8:** compose (the checkpoint counts table steps, not edge bytes). iso8601's 7.4
  cycles/byte `\s*` run is itself a P4/P8 customer (a stay skip or edge on the leading
  self-loop would cut its hazard cost before P10 does anything).

## Measurement cards

**Card P9 (`seed-window`).** Instruments: `p910_evidence/drv.c` (the bench's find-all), the
built artifact vs `-fno-seed-window`. Rows: (a) bounded ctx-* throughput (letters, digits) and
short subjects; (b) loglines level-context throughput and short; (c) counter-subjects: `a ` x
32768, `ab ` x 21845, 1 MiB word prose, the two stress subjects (gen_stress.py, seeds 1/2);
(d) the census's admitted bench members (altwide `wb-*` and the rest by id). Read: instructions:u
(gate) and cycles:u on a quiet box (bench window, D144 add. 4 for the official verdict). Pass:
(a) >= x1.8 instructions; (b)-(d) no row worse than the null band (instructions within 2%,
cycles within the bench's band); answer identity on all, against today's artifact and forced VM.

**Card P10 (`one-attempt-paced`).** Instruments: `drv.c`; artifact vs `-fno-...` deny. Rows: (a)
capability throughput + short subjects for every admitted bench pattern (job 691's set); (b)
the hazard pair (`t-evil-*`, `t-trim-*`); (c) the witnesses (`p910_evidence/gen_witness.py`: late byte matching / failing, dies-after-checkpoint at 1x and 1.5x the
checkpoint, short, empty). Constants: r = attempt cycles/step on a 60 KiB hazard run / memchr
cycles/byte, per route class, on each box (this box, ubuntubudu Zen 1, the Mac); D0 = memchr call
cycles on a 16-byte subject / cycles per step. Pass: (b) >= x20 instructions; (a) within the null
band; (c) <= the stated bound 1 + 2^K / r; the HOT-LOOP GATE (instructions/byte on the
60,000-then-match witness identical to today's); answer identity throughout.

## Questions for Frank

1. **P9: build the start skip at every seed state as the window FIND, rather than admitting the
   seed state as a scan edge or stay skip?** The forces: the edge/stay route is DFA-local and needs
   no new facts, and it wins most on random letters (x2.3-2.6); but it loses on short-word text
   (`a a a` x0.88 instructions; prose x0.95), which is P4's own short-run finding.
   The FIND wins everywhere I measured (x1.03 to x2.2) and reuses the PF site plus two facts we
   already own ([DD-11.5]'s context, `kset_walk`). My leaning: the FIND, filed as its own row (or
   as the third member of P4+P8 if you would rather see the loop's skip/edge admission as one row).
2. **P9 sequencing against [DD-11.5]:** the -1 term should come from DD-11.5's span-context
   producer, which today declines on the count-collapsed route these cells take. Leaning: let the
   P9 build read the context from the seed family (the machine already distinguishes the contexts)
   for the -1 term, so it does not wait on DD-11.5, and fold it into the producer when that lands.
   The alternative is to wait.
3. **P10: is a paced presence check "an adaptive method" under your 2026-10-21 caveat?** It does
   not estimate a density or switch between methods; it is one exact check at a fixed schedule
   with a stated worst case (<= x2, measured x1.2-1.8 on witnesses built to hurt it, most of which
   is a gcc register-allocation side effect the build gates). Leaning: it is not, and it should
   leave [ADAPTIVE-ARM] as its own row (the targets file's proposed [REQBYTE-REJECT] name fits),
   ranked after P9 because it moves three bench cells (email-owasp, iso8601, email-nested-plus:
   x14-20 on the capability sets; self-trails, not library trails).
4. **P10's price on patterns it cannot help:** `paced` costs 3-7% instructions (0% cycles) on
   `logparse-atomic` and up to x1.37 on 1 KiB email lines. Accept as the insurance premium, or
   gate the row to routes whose required byte is NOT in the first D0 steps' reach (not known at
   compile time)? Leaning: accept; it is the bound, and cycles show nothing.
5. **P9 breadth:** the structure admits 34 bench / 213 gated corpus artifacts but only six are
   measured. Leaning: build the row with card (d) as the gate, per-id, and let a pattern whose
   short-word subject regresses decline on its own measurement rather than argue it now.
6. **P10's `K`:** 5 (worst case x1.6 on every ratio measured so far, hazard gain ~x25) or 6
   (worst case up to x2.2 on selflip's ratio, gain ~x35)? Leaning: decide on the card's Zen 1
   ratio; until then 5, the conservative one.

## STATE AT HANDOFF

- STATE: done (report complete; census jobs 690 and 691 both GREEN and folded in by lane p910fin).
- Rulings file `docs/dev/lanes/p910_rulings.md` is empty of entries; none applied.
- OWED: none. Nothing was re-run; the P9 twins measured only the five ctx cells and level-context,
  and the other 28 bench P9 members are UNMEASURED by design (card row (d)). The P10 numbers for
  the 4 untwinned ids and the corpus 267 are likewise unmeasured (no subjects / no twin).
- Unexplained: 2 corpus/bench compiles returned `rc125` (`tests/vars/caseless.rxt:152`,
  `capability/mojibake-curly-quote`; both have a `\xff`/`\x93` byte in the pattern). Not
  investigated; it does not touch any cell.
- Nothing under `src/`, `cli/`, `lib/`, `memfn/`, `tests/` changed; no build go.
