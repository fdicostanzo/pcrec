# [OPT-3] STEP 1 — MEASUREMENT: attributing the DFA's per-byte cost

Lane `srOpt3`, 2026-08-26. Measurement only: **nothing under `src/` changed**.
Every variant below is a patched SCRATCH COPY of an emitted artifact, built in
the session scratchpad, and every one of them is answer-gated against the
unmodified artifact before any time is reported.

**Filed here, not in `docs/dev/reviews/`.** The brief named
`docs/dev/reviews/2026-08-26-m1-opt3-dfa-scan.md`, but `docs/dev/reviews/`'s own
CLAUDE.md scopes that directory to compiled checkpoint CRITIC PANELS (D6), one
file per checkpoint. Measurement memos live directly in `docs/dev/` —
`tt4_measurement.md`, `tt7_combined_axis.md`, `chain_profile.md`, `tt8_mech.md`.
This is a measurement memo, so it follows that convention.

## 0. The answer in four lines

1. The candidate-start SKIP loop is **not** where the loss lives. On the two
   subjects that carry the bench's cost it skips **zero bytes** — not "few", zero.
2. The whole cost is the TRANSITION loop, at **~3.2 ns (10.7 cycles) per table
   step**, and every subject's time is that constant times its step count.
3. The transition loop is **LATENCY-bound, not throughput-bound**: its
   loop-carried dependency chain is 7 cycles of address arithmetic + load, and
   the core has ~2x spare issue width at one stream.
4. The general fix is therefore **not** [OPT-SIMD]. It is to shorten that chain.
   Pre-multiplying the transition table by its stride, measured on the real
   artifact and answer-identical, is **1.28x on the bench's own three subjects**
   and takes pcrec from 1.466x slower than PCRE2-JIT to **1.149x** — ahead of
   JIT outright on `t-c`. SIMD skipping only starts paying when a pattern's
   non-candidate runs exceed ~32 bytes (measured, §4); these never do.

## 1. Method

- Box: AMD Ryzen 5 1600, 12 cores, `schedutil`, boost on. Effective clock **under
  the load the timed runs impose** measured directly with a dependent
  `add`-chain calibration loop (1 cycle/add): **3.2784 GHz** (median of 5;
  range 3.2298-3.3862, +/-2.4%). The idle `scaling_cur_freq` reads
  1.36-1.55 GHz, so taking the sysfs value or the nominal 3.2 GHz would have
  mis-scaled every cycle figure here — the calibration is not a formality.
  Every cycles/byte figure below carries that +/-2.4% band; none of the
  conclusions turn on it.
- `perf` is **unavailable** on this box: `perf_event_paranoid` is 4 and every
  event is denied. Lowering it is a system-config change the scope mandate
  forbids, so no counter-based figure appears below. Sections 4 and 5 replace it
  with two experiments that answer the same question more directly than
  `instructions`/`cycles` would have.
- Timing: `tests/bench/fdriver.c` (new, see §8), the FIND-ALL regime the bench
  uses, `taskset -c 3`, median of 5 trials, iteration counts chosen so each
  trial runs >= 1 s. `load1` is recorded beside every number. A sibling lane ran
  `make test` for part of the day, so the final battery's rows were taken at
  load1 0.76-1.72 rather than on an idle box. That is visible and bounded rather
  than assumed away: the same quantities were measured at load1 0.17-0.30 earlier
  and agree to within 1.7% (bitmap skip 0.3505 then, 0.3513-0.3566 in the
  battery; `t-c` 3.2631 then, 3.2650 in the battery), which is what a 12-core box
  with the measured thread pinned to one core should do. Per-trial spreads are
  1.002x-1.09x and are printed on every row of the raw log.
- Iteration COUNTS come from an instrumented scratch copy of the artifact that
  increments a counter in each loop, not from arithmetic on the subject.

## 2. Reproduction of the bench, in-tree

Pattern `orig` (`bench/email/patterns/orig.rx`), compiled the way the bench
compiles it (`-p rx --features all`; `--features all` changes only the
`PCREC_FEATURE_*` stamp lines for this pattern — the emitted code is
byte-identical to the default build). Stamps: `RX_ENGINE "dfa"`,
`RX_DFA_SCAN "unanchored"`, `RX_DFA_PREFILTER "byte-class"` — the byte-class
form the charter predicted. Caps and nocaps differ only in `RX_NCAPS`.

| subject | bench ns/byte | in-tree ns/byte | delta |
|---|---|---|---|
| `t-a-valid-addrs` | 6.2388 | 6.1827 | -0.90% |
| `t-b-no-at` | 3.2627 | 3.2801 | +0.53% |
| `t-c-long-atom-run` | 3.2607 | 3.2631 | +0.07% |

(load1 0.17-0.24; the final battery re-measured the same three at load1
0.86-1.11 and got 6.2102 / 3.2722 / 3.2650 — within 0.6% of these.)

Match counts agree exactly (t-a: 40,330). Set-grain against PCRE2-JIT reproduces
the report's ratio independently: **1.465x** here vs the report's `1.467x vs
best`. The reproduction is sound; nothing below rests on a mismatch.

`factored` is the same measurement, not a second one: it compiles to a DFA with
the same 18-class stride and the same `byte-class` prefilter, which is why its
bench numbers track `orig`'s. **It needs `--features all` to compile at all** —
without it pcrec refuses with `requires module 'named-groups'`. That is the
bench's config and is correctly recorded in `bench/email/subbench.toml`; noted
here only because a reader reproducing by hand with a default `pcrec` will hit
the refusal.

## 3. Where the bytes actually go (instrumented artifact)

Counters compiled into a scratch copy: forward transition steps, reverse
transition steps, skip-loop ENTRIES, and skip-loop BYTES SKIPPED.

| subject | matches | fwd steps | rev steps | steps/byte | skip entries | skip bytes |
|---|---|---|---|---|---|---|
| `t-a` | 40,330 | 1,048,576 | 1,048,575 | **2.000** | 80,661 | 40,330 |
| `t-b` | 0 | 1,048,576 | 0 | **1.000** | 190,651 | **0** |
| `t-c` | 0 | 1,048,576 | 0 | **1.000** | 1 | **0** |
| `s-space` (1 MB of `' '`) | 0 | 0 | 0 | 0.000 | 1 | 1,048,576 |

### THE SURPRISE: the skip loop is entered 190,651 times on `t-b` and skips nothing

The charter's reading was "on 1 MB of `a` every byte is a candidate, so the skip
loop never runs". That is right for `t-c` — and the finding is that it is *also*
effectively right for `t-b`, which is ordinary English text where **18% of bytes
are non-candidates**. The skip loop runs 190,651 times there and skips **zero
bytes on every single one of them**.

The cause is structural, and it is in the emitted loop's ORDER:

```c
for (;;) {
    if (rx_forward_is_accepting[forward_state]) last_accept_position = scan_position;
    if (forward_state == 0 && last_accept_position == (size_t)-1) {
        while (scan_position < subject_length && !rx_can_begin_match[subject[scan_position]]) scan_position++;
        ...
    }
    ...
    forward_state = rx_forward_next_state[forward_state * 18 + rx_forward_byte_class[subject[scan_position++]]];
```

The machine only returns to state 0 by *consuming* the byte that killed the
match, so by the time the skip test is reached, `scan_position` already points
PAST that byte — at the next candidate. **The skip loop can only ever skip the
2nd..nth byte of a non-candidate run.** English text's non-candidate runs are
single spaces, i.e. length 1, so it skips nothing at all.

Confirmed by a run-length sweep (1 MB, 8 candidate bytes then k non-candidates):

| k (run length) | 1 | 2 | 4 | 8 | 16 | 32 | 64 |
|---|---|---|---|---|---|---|---|
| mean bytes skipped per entry | **0.00** | 1.00 | 3.00 | 7.00 | 15.00 | 31.00 | 62.99 |

Exactly `k-1`, every time. On `t-a` the mean is 0.50 for the same reason (half
the entries are suppressed by `last_accept_position` after a match).

## 4. The skip loop's cost, isolated (CONTROL 1 and CONTROL 2)

A 1 MB subject containing NO candidate byte never enters the transition loop at
all (`fwd steps = 0` above), so its whole time is the skip loop.

Three such subjects were used (1 MB each of `' '`, `'A'`, `'\n'`) so the result
cannot rest on one byte value. Medians of 5, all three subjects within 1.5%:

| skip form | artifact | ns/byte | cycles/byte | GB/s | vs bitmap |
|---|---|---|---|---|---|
| 256-entry bitmap walk (scalar, what `orig` emits) | `orig` | 0.3513-0.3566 | 1.15-1.17 | 2.8 | 1.0x |
| 256-entry bitmap walk (2-byte class twin) | `[@#]example\.com` | 0.3522-0.3528 | 1.16 | 2.8 | 1.0x |
| `memchr` (glibc AVX2) — **CONTROL 1** | `@example\.com` | **0.0168-0.0169** | 0.055 | 59 | **~21x** |
| pshufb shufti (studies/simd1) — **CONTROL 2** | `orig` + scratch skip | **0.0499-0.0518** | 0.166 | 20 | **~7x** |

CONTROL 1 is a clean isolation: on a subject with no candidate byte the two
artifacts do exactly the same thing (skip to the end, return 0), so the 20.6x is
the scan form and nothing else. The bitmap walk really is ~20x off memchr.

Two things worth recording:

- glibc's `memchr` at **0.0170 ns/byte** is, to three digits, PCRE2-interp's
  0.0169-0.0170 ns/byte on `t-b`/`t-c` in the report. That independently confirms
  [OPT-5]'s reading — interp's required-code-unit check is one `memchr` — from
  this side of the fence. Cross-reference only; [OPT-5] is a separate lever and
  is deliberately kept out of the recommendation below.
- shufti IS exact for this class (verified over all 256 byte values: the 56-byte
  candidate set has zero nibble-pair false positives), so it needs no bitmap
  re-check.

### CONTROL 2 on the subjects that matter: a 7x faster skip loop makes them SLOWER

| subject | `orig` (bitmap skip) | `orig` + shufti skip | change |
|---|---|---|---|
| `t-a` | 6.2102 | 6.4525 | **+3.9% SLOWER** |
| `t-b` | 3.2722 | 3.2841 | **+0.4% SLOWER** |
| `t-c` | 3.2650 | 3.3134 | **+1.5% SLOWER** |

(Answer-gated: identical over 40,470 answer lines.) A skip loop 7x faster per
skipped byte loses time on all three, because it skips ~0 bytes there and its
vector setup is paid on each of `t-b`'s 190,651 entries. **This refutes the SIMD
hypothesis for these subjects directly**, rather than merely failing to confirm
it.

### Where SIMD skipping WOULD pay: the crossover is ~32-byte runs

The same two artifacts over the run-length sweep of §3 (1 MB, 8 candidate bytes
then k non-candidates) locate the break-even exactly:

| k (non-candidate run) | 1 | 2 | 4 | 8 | 16 | **32** | **64** |
|---|---|---|---|---|---|---|---|
| bitmap skip, ns/byte | 3.2857 | 2.9566 | 2.4589 | 1.8355 | 1.2259 | 0.9379 | 0.9139 |
| shufti skip, ns/byte | 3.3221 | 2.9845 | 2.4852 | 1.8567 | 1.2341 | **0.7401** | **0.4121** |
| shufti vs bitmap | 0.99x | 0.99x | 0.99x | 0.99x | 0.99x | **1.27x** | **2.22x** |

Below a ~32-byte run SIMD skipping is a consistent ~1% LOSS; above it the win
grows fast. That is the vector width: a run shorter than one 32-byte chunk never
gets a chunk to itself. So [OPT-SIMD] is not wrong in general — it is wrong for
**this** loop on **these** inputs, and the condition under which it would become
right is now a number rather than a hunch: candidate-start scanning only pays
when a pattern's non-candidate runs routinely exceed ~32 bytes. Neither email
pattern's inputs come close (§3: mean run 0 to 1).

## 5. The transition loop: the instruction-level reading

`gcc -O2` on the emitted artifact; the hot forward loop is 17 instructions:

```
48: cmp    %rsi,%rax                 ; scan_position >= subject_length
4b: jae    8c
4d: movzbl (%rdi,%rax,1),%edx        ; LOAD 1  subject[scan_position]
51: movzbl (%rbx,%rdx,1),%edx        ; LOAD 2  byte_class[b]        (dep on 1)
55: lea    (%rcx,%rcx,8),%ecx        ; CHAIN   state*9
58: lea    (%rdx,%rcx,2),%edx        ; CHAIN   state*18 + class
5b: movslq %edx,%rdx                 ; CHAIN
5e: movswl 0x0(%rbp,%rdx,2),%ecx     ; CHAIN + LOAD 3  next_state[...]
63: test   %ecx,%ecx
65: js     8c                        ; dead
67: movslq %ecx,%rdx
6a: add    $0x1,%rax
6e: movzbl (%r12,%rdx,1),%edx        ; LOAD 4  is_accepting[state]  (off-chain)
73: test   %dl,%dl
75: cmovne %rax,%r8                  ; last_accept_position
79: test   %ecx,%ecx
7b: jne    48
```

**Four dependent loads per byte**, and the loop-carried chain through
`forward_state` is `lea(1) + lea(1) + movslq(1) + load(4)` = **7 cycles**.
Measured: **10.70 cycles/byte**. Branches are perfectly predictable on `t-c`
(one 'a' forever), and the tables total ~9.5 KB, comfortably L1-resident — so
neither mispredicts nor table misses explain the cost.

### Latency or throughput? The two-stream witness (replaces `perf`)

Run K independent DFA streams over K slices of the subject in one loop
(semantically not the pattern — a microarchitectural witness only). If the loop
is bound by its dependency chain, K streams cost the same wall time and ns/byte
falls ~K-fold; if bound by issue/port throughput, ns/byte stays flat.

| variant | cycles/byte | vs 1 stream |
|---|---|---|
| 1 stream (transcription of the emitted loop) | 10.714 | 1.00x |
| 2 streams | 5.456 | **1.96x** |
| 4 streams | 4.721 | 2.27x |
| 8 streams | 3.713 | 2.89x |

Two streams very nearly halve it. **The loop is latency-bound with ~2x spare
issue width**, and the throughput floor is ~3.7 cycles/byte. This is the whole
diagnosis: the 10.7 cycles are a dependency chain, not work.

### Which parts of the chain cost what

Scratch microbenchmark on `t-c`, tables extracted from the real artifact:

| variant | cycles/byte | vs emitted |
|---|---|---|
| v0 — the emitted loop as-is | 10.714 | 1.00x |
| v0b — transition step ONLY (accept bookkeeping + prefilter test deleted) | 10.687 | 1.003x |
| **v1 — transition table PRE-MULTIPLIED by the stride** | **7.751** | **1.38x** |
| v1b — v1 without accept bookkeeping | 6.863 | 1.56x |
| v2 — accept flag FUSED into the table entry | 8.095 | 1.32x |

- The accept-position bookkeeping and the per-byte prefilter test that the
  charter asked about cost **0.05 cycles/byte — nothing**. They are off the
  critical chain and the core absorbs them. Do not spend effort there.
- Pre-multiplying the table (entries hold `next*stride`, so the chain becomes
  `load + add` instead of `lea,lea,movslq,load`) removes **~3 cycles/byte**.
- Fusing accept into the entry is WORSE than v1 (it puts an AND back on the
  chain). Keep the accept probe as a separate, premultiplied-indexed table.

## 6. Attribution table

Per-byte cost decomposed. "Table steps" is the measured step count from §3
multiplied by the measured cost per step.

| subject | total ns/byte | transition loop | skip loop | per-match fixed |
|---|---|---|---|---|
| `t-c` | 3.265 | 3.265 (**100.0%**) | 0.000 (0%) | — (no matches) |
| `t-b` | 3.272 | 3.272 (**100.0%**) | 0.000 (0%) | — (no matches) |
| `t-a` | 6.210 | 6.197 (**99.8%**) = fwd 3.10 + rev 3.10 | 0.013 (0.2%) | **~0** |

Cost per table step is constant across all three — 3.265 / 3.272 / 3.105 ns
(10.70 / 10.73 / 10.18 cycles) — which is the model's own check: **time =
steps x 3.2 ns**, with the skip loop contributing nothing. (`t-a`'s step is ~5%
cheaper because half its steps run the REVERSE table, which is 1,350 entries
against the forward machine's 4,482 and sits further inside L1.)

### The per-match split on `t-a`

`t-a` is `user.name@sub.example.com ` repeated: 25-byte match + 1 separator = 26
bytes, and 1048576/26 = 40,330 exactly. Per §3 it runs **2.000 table steps per
subject byte** — one forward pass over every byte, then a reverse pass over
every matched byte (the matches tile the subject).

Measured directly: one `rx_search` returning the first match costs **158.7 ns**
(median of 3, 3M iterations). The ~51 bytes that call walks (26 forward to the
death point + 25 reverse) at 3.1 ns/step = ~158 ns. And 40,330 x 158.7 ns =
6.40 ms against a measured find-all total of 6.51 ms — **1.7% agreement**.

So there is **no per-match fixed overhead worth naming**. `t-a` costs 1.9x `t-c`
for exactly one reason: **the reverse scan re-traverses every matched byte**.
The charter's formula (t-a cost - scan cost at t-b's rate) / 40,330 gives
76.3 ns/match, but that number is not an overhead — it IS the reverse pass, and
attributing it to "per-match bookkeeping" would be wrong. (Cross-check: the same
premultiplied change that speeds the scan speeds the per-call figure by the same
factor — 158.7 -> 125.2 ns/call, 1.27x, matching the 1.26x it gets on `t-a`
end to end. A fixed per-match cost would not have moved with the table shape.)

## 7. RECOMMENDATION

**Not [OPT-SIMD].** The loss does not live in the skip loop; §3 shows the skip
loop moves zero bytes on the subjects that carry the cost, and §4 shows a 7x
faster skip loop makes all three of them slower. A SIMD candidate scan would win
only on subjects with LONG non-candidate runs — which the bench's set does not
contain and ordinary text does not produce. It does not earn its charter through
this loop (D79 item 4).

**The lever is the transition loop's dependency chain**, and the first move is
the table-width one the charter named:

### Pre-multiply the transition table by its stride

Store `next_state * stride` in the table instead of `next_state`, and index the
accepting table by that premultiplied value. The loop-carried chain drops from
`lea,lea,movslq,load` (7 cycles) to `load,add`.

Measured on the REAL artifact — a patched scratch copy, **answer-identical to
the unmodified artifact over 40,469 answer lines across 91 subjects** (the
bench's 85 compliance subjects, its 3 throughput subjects, and 3 synthetic ones,
comparing every match span and every capture, not just counts):

| subject | baseline | pre-multiplied | gain | PCRE2-JIT | base vs JIT | premul vs JIT |
|---|---|---|---|---|---|---|
| `t-a` | 6.2102 | **4.9243** | 1.261x | 3.5448 | 1.752x | 1.389x |
| `t-b` | 3.2722 | **2.5506** | 1.283x | 2.4515 | 1.335x | 1.040x |
| `t-c` | 3.2650 | **2.5189** | 1.296x | 2.6991 | 1.210x | **0.933x** |
| **set** | 12.747 | **9.994** | **1.276x** | 8.695 | **1.466x** | **1.149x** |

**Expected gain: 1.28x on this bench row, closing 68% of the gap to PCRE2-JIT
(1.466x -> 1.149x), and overtaking JIT outright on `t-c`.** (The baseline column
reproduces the report's own set-grain ratio: 1.466x here, 1.467x there.)

Two constraints the emitter must respect, both decidable at generation time:

1. **Range.** Entries must hold `next*stride`, so the `short` table overflows
   once `states*stride > 32767`. The emitter knows both numbers at generation
   time, so this is a choice, not a risk — premultiplied `short` under the bound,
   the current form above it. It must not become an unconditional widening to
   `int`: that doubles the table, and this loop is only fast while the tables are
   L1-resident. Surveyed over twelve patterns to check how often the bound binds:

   | pattern | states | stride | states x stride | fwd table |
   |---|---|---|---|---|
   | email `orig` | 249 | 18 | 4,482 | 8,964 B |
   | `needleXYZW` | 11 | 9 | 99 | 198 B |
   | `a*b` | 2 | 3 | 6 | 12 B |
   | IPv4 dotted-quad | 20 | 7 | 140 | 280 B |
   | `\w+@\w+\.\w+` | 6 | 4 | 24 | 48 B |
   | URL-ish class | 10 | 8 | 80 | 160 B |
   | `[01]*1[01]{8}` | 768 | 3 | 2,304 | 4,608 B |
   | `[01]*1[01]{11}` | 6,144 | 3 | 18,432 | 36,864 B |
   | `[01]*1[01]{12}` | 12,288 | 3 | **36,864 — OVERFLOW** | 73,728 B |

   Every ordinary pattern is orders of magnitude under the bound. The only family
   that reaches it is `[01]*1[01]{n}` — R1 A-3's deliberate state-explosion
   family — and it first overflows at n=12, where the table is already 73,728 B,
   **2.3x this core's 32 KB L1D**. So the loop there is cache-bound and the chain
   optimization is moot anyway: the honest gate is L1 residency (~16,384 entries),
   which binds *before* `short` overflow does. One rule covers both.
2. **Table size.** The accepting table grows from `states` to `states*stride`
   bytes (orig forward: 249 B -> 4,482 B; reverse: 75 B -> 1,350 B; ~+5.5 KB of
   `.rodata` total). Still L1-resident here, and the 1.27x above already
   includes that cost — but it is the same size question as (1) and should be
   gated by the same rule, not assumed.

This is a general mechanism, not a special case: it applies to every
table-driven DFA artifact both engines emit, and it is answer-preserving by
construction (the identity gate is the control, not the argument).

### Named, not recommended, with its number

`t-a`'s remaining 1.389x against JIT is **entirely the second pass**. At 2.000
steps/byte, a one-pass engine that recovered the match START without a reverse
scan would put `t-a` at ~2.5 ns/byte — ahead of JIT's 3.5448. That is a
substantially larger change than (1) and belongs to its own charter under D77;
it is recorded here because this lane measured its size, not as a proposal.

Levers this lane measured and does NOT recommend: fusing the accept flag into
the table entry (§5, slower than pre-multiplying alone); removing the
accept-position bookkeeping or the per-byte prefilter test (§5, worth 0.05
cycles/byte); SIMD candidate scanning (§4).

## 8. Artifacts of this lane

- `tests/bench/fdriver.c` — the FIND-ALL timing driver. `bdriver.c` times ONE
  `rx_search`; the comparative bench's throughput regime is search-restart-repeat,
  and on a subject with 40,330 matches those are different cost classes. The
  restart rule is transcribed from pcrec-bench's own `testees/pcrec/driver.c`.
- Everything else — patched artifacts, instrumented copies, the shufti skip, the
  variant microbenchmark, the clock calibration, the subject files — is scratch
  and deliberately not committed. Each is reconstructible from this memo: the
  premultiplied artifact is a mechanical rewrite of the two transition tables and
  their two loop lines, the instrumented one adds five counters, and the shufti
  skip is the class's nibble tables plus the loop in §4.
- `make strict` clean on this tree. `make test` was NOT run — another lane owned
  it today — and nothing here changes anything it covers.

## 9. What would have gone wrong without a control

Three of this lane's findings would have come out backwards on the obvious method:

- **Taking the clock from sysfs.** It reads 1.36-1.55 GHz idle and 3.28 GHz under
  load. The transition loop would have been "5 cycles/byte" — below its own
  dependency chain, which would have made the chain diagnosis look impossible.
- **Inferring skip-loop work from the subject's byte histogram.** 18% of `t-b` is
  non-candidate, which predicts a large skip contribution. The instrumented count
  says the true figure is ZERO bytes, for a reason no histogram can see (the loop
  is reached one byte late). The charter's own framing — "on 1 MB of `a` every
  byte is a candidate, so the skip never runs" — was right for `t-c` for the
  stated reason and right for `t-b` for a different one.
- **Timing the SIMD skip only on the subject it was designed for.** On a
  no-candidate subject shufti is 7x faster and the conclusion "SIMD is the fix"
  writes itself. On the three subjects the bench actually measures it is slower
  on all three. CONTROL 2 was worth more as a refutation than it would have been
  as a confirmation.
