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
   artifact and answer-identical, is **1.27x on the bench's own three subjects**
   and takes pcrec from 1.465x slower than PCRE2-JIT to **1.151x**.

## 1. Method

- Box: AMD Ryzen 5 1600, 12 cores, `schedutil`, boost on. Effective clock **under
  the load the timed runs impose** measured directly with a dependent
  `add`-chain calibration loop (1 cycle/add): **3.2781 GHz** (3.2781 / 3.2784 /
  3.2298 over three runs). The idle `scaling_cur_freq` reads 1.36-1.55 GHz, so
  taking the sysfs value or the nominal 3.2 GHz would have mis-scaled every
  cycle figure here — the calibration is not a formality.
- `perf` is **unavailable** on this box: `perf_event_paranoid` is 4 and every
  event is denied. Lowering it is a system-config change the scope mandate
  forbids, so no counter-based figure appears below. Sections 4 and 5 replace it
  with two experiments that answer the same question more directly than
  `instructions`/`cycles` would have.
- Timing: `tests/bench/fdriver.c` (new, see §8), the FIND-ALL regime the bench
  uses, `taskset -c 3`, median of 5 trials, iteration counts chosen so each
  trial runs >= 1 s. `load1` is recorded beside every number; the reported rows
  were taken at load1 <= 0.8 unless the row says otherwise.
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

| skip form | artifact | ns/byte | cycles/byte | GB/s | vs bitmap |
|---|---|---|---|---|---|
| 256-entry bitmap walk (scalar, what `orig` emits) | `orig` | 0.3505 | 1.149 | 2.85 | 1.0x |
| 256-entry bitmap walk (2-byte class twin) | `[@#]example\.com` | 0.3505 | 1.149 | 2.85 | 1.0x |
| `memchr` (glibc AVX2) — **CONTROL 1** | `@example\.com` | **0.0170** | 0.056 | 58.8 | **20.6x** |
| pshufb shufti (studies/simd1) — **CONTROL 2** | `orig` + scratch skip | **0.0501** | 0.164 | 20.0 | **7.0x** |

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
| `t-a` | 6.1914 | 6.4835 | **+4.7% SLOWER** |
| `t-b` | 3.2682 | 3.3025 | **+1.0% SLOWER** |
| `t-c` | 3.2659 | 3.3117 | **+1.4% SLOWER** |

(Answer-gated: identical over 40,470 answer lines.) A skip loop 7x faster per
skipped byte loses time on all three, because it skips ~0 bytes there and its
vector setup is paid on each of `t-b`'s 190,651 entries. **This refutes the SIMD
hypothesis for these subjects directly**, rather than merely failing to confirm
it.

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
| 1 stream (transcription of the emitted loop) | 10.727 | 1.00x |
| 2 streams | 5.437 | **1.97x** |
| 4 streams | 4.724 | 2.27x |
| 8 streams | 3.746 | 2.86x |

Two streams very nearly halve it. **The loop is latency-bound with ~2x spare
issue width**, and the throughput floor is ~3.7 cycles/byte. This is the whole
diagnosis: the 10.7 cycles are a dependency chain, not work.

### Which parts of the chain cost what

Scratch microbenchmark on `t-c`, tables extracted from the real artifact:

| variant | cycles/byte | vs emitted |
|---|---|---|
| v0 — the emitted loop as-is | 10.727 | 1.00x |
| v0b — transition step ONLY (accept bookkeeping + prefilter test deleted) | 10.677 | 1.005x |
| **v1 — transition table PRE-MULTIPLIED by the stride** | **7.769** | **1.38x** |
| v1b — v1 without accept bookkeeping | 6.868 | 1.56x |
| v2 — accept flag FUSED into the table entry | 8.112 | 1.32x |

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
| `t-c` | 3.263 | 3.263 (**100.0%**) | 0.000 (0%) | — (no matches) |
| `t-b` | 3.280 | 3.280 (**100.0%**) | 0.000 (0%) | — (no matches) |
| `t-a` | 6.183 | 6.169 (**99.8%**) = fwd 3.09 + rev 3.09 | 0.013 (0.2%) | **~0** |

Cost per table step is constant across all three — 3.263 / 3.280 / 3.091 ns
(10.70 / 10.75 / 10.13 cycles) — which is the model's own check: **time =
steps x 3.2 ns**, with the skip loop contributing nothing.

### The per-match split on `t-a`

`t-a` is `user.name@sub.example.com ` repeated: 25-byte match + 1 separator = 26
bytes, and 1048576/26 = 40,330 exactly. Per §3 it runs **2.000 table steps per
subject byte** — one forward pass over every byte, then a reverse pass over
every matched byte (the matches tile the subject).

Measured directly: one `rx_search` returning the first match costs **163.1 ns**
(median of 3, 3M iterations). The ~51 bytes that call walks (26 forward to the
death point + 25 reverse) at 3.2 ns/step = 163 ns. And 40,330 x 163.1 ns =
6.58 ms against a measured find-all total of 6.49 ms — **1.2% agreement**.

So there is **no per-match fixed overhead worth naming**. `t-a` costs 1.9x `t-c`
for exactly one reason: **the reverse scan re-traverses every matched byte**.
The charter's formula (t-a cost - scan cost at t-b's rate) / 40,330 gives
75.6 ns/match, but that number is not an overhead — it IS the reverse pass, and
attributing it to "per-match bookkeeping" would be wrong.

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
| `t-a` | 6.1881 | **4.9216** | 1.257x | 3.5448 | 1.746x | 1.388x |
| `t-b` | 3.2694 | **2.5627** | 1.276x | 2.4515 | 1.334x | 1.045x |
| `t-c` | 3.2798 | **2.5221** | 1.300x | 2.6991 | 1.215x | **0.934x** |
| **set** | 12.737 | **10.006** | **1.273x** | 8.695 | **1.465x** | **1.151x** |

**Expected gain: 1.27x on this bench row, closing 68% of the gap to JIT
(1.465x -> 1.151x), and overtaking JIT outright on `t-c`.**

Two constraints the emitter must respect, both decidable at generation time:

1. **Range.** Entries must hold `next*stride`, so the `short` table overflows
   once `states*stride > 32767` (orig: 248*18 = 4,464, comfortable). The emitter
   knows both numbers, so this is a generation-time choice — premultiplied
   `short` under the bound, and either a widened entry type or the current form
   above it. It must not be an unconditional widening: `int` entries double the
   table and this loop is only fast while the tables are L1-resident.
2. **Table size.** The accepting table grows from `states` to `states*stride`
   bytes (orig forward: 249 B -> 4,482 B; reverse: 75 B -> 1,350 B; ~+5.5 KB of
   `.rodata` total). Still L1-resident here, and the 1.27x above already
   includes that cost — but it is the same size question as (1) and should be
   gated by the same rule, not assumed.

This is a general mechanism, not a special case: it applies to every
table-driven DFA artifact both engines emit, and it is answer-preserving by
construction (the identity gate is the control, not the argument).

### Named, not recommended, with its number

`t-a`'s remaining 1.388x against JIT is **entirely the second pass**. At 2.000
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
  and deliberately not committed.
