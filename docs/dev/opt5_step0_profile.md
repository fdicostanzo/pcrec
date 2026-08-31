# [OPT-5] STEP 0 — MEASUREMENT: why the counted DFA loses to pcrec's own VM

Lane `opt5m`, 2026-08-31. Measurement only: **nothing under `src/` changed**.
Filed here (not `docs/dev/reviews/`) for the same reason
`opt3_dfa_scan_measurement.md` is — this is a measurement memo, not a
compiled-checkpoint critic panel.

## 0. The answer in five lines

1. **`perf` is unavailable on this box** (`perf_event_paranoid=4`, confirmed
   directly — `Error: No supported events found`), so this follows
   `opt3_dfa_scan_measurement.md`'s precedent: reproduction with a real
   driver, calibrated wall-time-to-cycles, and static disassembly stand in
   for `perf stat`/`perf record`.
2. **The mechanism is a dependency-chain shape, not a cache or table-size
   effect.** The VM compiles `[a-z]{0,n}` into a plain possessified scalar
   loop (`(unsigned)(subject[i]-97)<=25u`) whose loop-carried state is just
   an incrementing cursor — each iteration's load address is independent of
   the *value* any previous iteration loaded. The DFA's per-byte transition
   loads `next_state[state*width+class]`, where `state` is the *value the
   previous iteration's load returned* — a genuine pointer-chasing chain.
   This is the exact loop shape `opt3` already proved latency-bound (7-cycle
   loop-carried chain, ~2x spare issue width) on the email DFA — and by
   [ENG-FORM] (D82) the loop skeleton is now emitted **once**, shared by
   every DFA machine, so that diagnosis applies here by construction, not by
   analogy.
3. **The digits asymmetry is not a per-byte effect at all.** The bench's
   `large-subject-throughput` regime is genuine **find-all**: on a nullable
   pattern with no in-class byte, it issues one `rx_search` call *per
   subject byte* (16,385 calls on `t-digits-016k`), each of which is O(1)
   regardless of `n`. The ~1.7-2.0x DFA-over-VM win on digits is a **fixed
   per-call overhead** ratio (DFA ~3.6-4.9 ns/call vs VM ~7.1-8.7 ns/call),
   flat across every rung — not a scan cost.
4. **I-21's prediction is supported by mechanism, not just by data**: no
   count crossover exists on either axis because neither ratio depends on
   `n` — the letters ratio depends on whether the loop-carried chain is
   data- or address-dependent (a structural property of the engine, not the
   count), and the digits ratio depends on fixed per-call overhead (also
   count-independent).
5. **This is not a threshold — it does not belong in `limits.def`.** The
   knee is a property of the *subject* (does the run stay in-class?), which
   a compile-time count knob cannot see. The general fix is to give the
   DFA's single-class counted-repeat the same address-only-dependent loop
   the VM already emits — not to pick a different engine at a different
   count.

## 1. Method

- Box: same as `opt3` (AMD Ryzen 5 1600, 12 cores). Calibrated clock via the
  same dependent add-chain technique (`asm volatile("":"+r"(v))` per
  iteration to defeat strength-reduction — the naive version folds to a
  closed form and reports "0 seconds", a trap worth recording): median
  **3.3749 GHz** (5 runs, range 3.2852-3.3799, ~load1 0.3-0.4 throughout).
- `perf stat`/`perf record` refused (`perf_event_paranoid=4`, scope mandate
  forbids lowering it — a system-config change). No counter-based figures
  below; static disassembly + controlled timing experiments replace them,
  as `opt3` §1 already established as this box's substitute.
- Load checked before every timed phase: 0.25-0.58 throughout, well under
  the 2.0 discard threshold; every timed run below is admitted.
- Artifacts: `worktrees/opt5m/build/pcrec` (built once, `make -j4`, this
  worktree, commit 263b013 base) compiling `[a-z]{0,n}` for n = 256, 4096,
  16384, `auto` (selects DFA at every rung, confirmed by `RX_ENGINE "dfa"`,
  `RX_ENGINE_SEL "selected"`) and `--engine=vm` (`RX_ENGINE "vm"`,
  `RX_ENGINE_SEL "forced"`). `RX_DFA_TABLE "premultiplied"` on every DFA
  artifact — these are POST-[OPT-3] artifacts already, not the pre-fix
  baseline `opt3` measured.
- Subjects: copied read-only from `pcrec-bench/bench/bounded/throughput/`
  (`t-letters-004k/016k/064k.bin`, `t-digits-016k.bin`) and
  `pcrec-bench/bench/bounded/subjects/` (`l-00/01/03.bin`, for the
  [OPT-VMLIT] measurement). Byte histograms confirm the class assumption
  directly rather than by inference: `t-letters-004k.bin` is 100% `[a-z]`
  (4096/4096 bytes), `t-digits-016k.bin` is 0% `[a-z]` (0/16384 bytes, all
  ASCII digits).

## 2. Reproduction — and a correction to the brief's own premise

The brief's driver sketch (one `rx_search(buf,n,0,caps)` call per timed
iteration, `pcrec-bench`'s `eng_pcrec.c` shape) reproduces the **letters**
numbers closely but is wrong by **4 orders of magnitude** on **digits**:

| driver | `t-digits-016k`, `auto` n=16384 | bench's own figure |
|---|---|---|
| single `rx_search(buf,n,0,...)` call | 3.99 ns/call | 82,601.5 ns/call |

The cause: `subbench.toml`'s `throughput` regime passes `--find-all` to
`testees/pcrec/driver.c` (its own header says so:
"`{0,n}`... under find-all search there is no end anchor"). Its find-all
loop (`driver.c:548-565`) calls `do_search` **repeatedly**, advancing
`pos = (end > pos) ? end : pos+1` after every match, until `pos > len`. On a
subject with no in-class byte, `{0,n}` is nullable, so **every position is a
valid zero-length match** — the loop runs once per byte plus one, calling
`rx_search` 16,385 times on a 16,384-byte digit subject. `eng_pcrec.c`
(single call, no `--find-all`) is a *different* driver for a *different*
regime (`csv5`'s no-match rows use it, for instance) — the STEP-0 brief
picked the wrong sibling. This matters beyond bookkeeping: **the digits
"win" is a fixed-per-call-overhead effect amplified by call count, not a
scan-speed effect** (§4).

`fadriver.c` (built here, reproducing `driver.c`'s exact find-all loop)
closes the gap. Reproduction, 3 trials each, load1 0.25-0.39:

| subject | pattern | testee | median ns | bench's figure | delta |
|---|---|---|---|---|---|
| `t-letters-004k` (n=256, 17 matches) | `cls-upto-256` | auto (DFA) | 14,905-14,980 | 14,986.3-15,032.0 | -0.3% to -0.9% |
| `t-letters-004k` (n=256, 17 matches) | `cls-upto-256` | vm | 2,842-2,897 | 2,907.8-2,963.2 | -2.2% to -1.1% |
| `t-letters-004k` (n=4096, 2 matches) | `cls-upto-4096` | auto (DFA) | 14,804-14,873 | 14,873.8-14,908.8 | -0.5% to -0.2% |
| `t-letters-004k` (n=4096, 2 matches) | `cls-upto-4096` | vm | 2,461-2,494 | 2,527.8-2,751.1 | in bench's range |
| `t-digits-016k` (n=16384, 16,385 matches) | `cls-upto-16384` | auto (DFA) | 58,425-58,587 | 82,758.7 | **-29.3%** |
| `t-digits-016k` (n=16384, 16,385 matches) | `cls-upto-16384` | vm | 116,805-116,891 | 140,543.0 | **-16.9%** |

Letters reproduce to within ~1-2% (well inside the bench's own trial spread
— its `t-letters-004k` VM row spans 2,527.8-2,751.1 across sessions).
**Digits do not** — this build is static/non-PIC while the bench compiles
each artifact `-fPIC -shared` and `dlopen`s it (`adapter.py`'s "COMPILE
COST" section). The digits per-call cost is small enough (a few ns) that
PIC's GOT-indirection tax is a real fraction of it; on letters the per-call
cost is two orders of magnitude larger, so the same tax is noise. **The
ratio and the mechanism are unaffected** — DFA beats VM on digits in both
builds, VM beats DFA on letters in both builds, by the same order of
magnitude — but the absolute digits figures below are this build's, not a
repin of the bench's, and are reported as such.

## 3. The mechanism: data-dependent vs address-dependent loop-carried chains

### 3.1 The DFA's forward transition loop (`gcc -O2`, `rx_search`, n=16384)

```asm
1600: movzbl (%rdi,%rdx,1),%eax      ; eax = subject[scan_position]           LOAD 1 (independent: address = base+cursor)
1604: movzbl (%rbx,%rax,1),%eax      ; eax = byte_class[eax]                  LOAD 2 (depends on LOAD 1's byte value)
1608: add    %r9d,%eax               ; eax = PREV forward_state + class       <-- r9d is what LOAD 3 returned LAST iteration
160b: mov    %eax,%eax               ; zero-extend index
160d: movzwl (%r11,%rax,2),%r9d      ; r9d = next_state[eax]                  LOAD 3 (address depends on r9d from iter i-1)
1612: cmp    $0xffff,%r9d
1619: je     162e                    ; dead state -> break
161b: add    $0x1,%rdx               ; scan_position++
161f: cmpb   $0x0,0x0(%rbp,%r9,1)    ; is_accepting[r9d]                      LOAD 4 (depends on LOAD 3)
1625: cmovne %rdx,%rcx               ; last_accept_position = scan_position
1629: cmp    %rdx,%r10
162c: jne    1600
```

The table is already `RX_DFA_TABLE "premultiplied"` — this is `opt3`'s "v1"
representation (`add`+load, not `lea`+`lea`+`movslq`+load), the fix that
took the email DFA from 10.714 to 7.751 cycles/byte. Even so, **`next_state`
at line 160d is addressed by `r9d`, which is the *value* `next_state`
returned the previous iteration.** That is the textbook pointer-chasing
shape: iteration i+1's LOAD 3 cannot issue its address computation until
iteration i's LOAD 3 has *returned data*, not merely been issued. The
reverse pass (`165a`-`16ac`, finding `match_start`) is the identical shape
against `rx_reverse_next_state`.

### 3.2 The VM's possessified span-loop (`rx_match_anchored`, n=16384)

Source (`emit_vm.c`'s output, unedited):

```c
// span-loop cursor {0,16384}, stride 1, greedy, POSSESSIFIED (no frame, no giveback)
rx_L0: {
    unsigned long it_ = 0;
    rx_span_cursor = scan_position;
    while (rx_span_cursor + 1 <= subject_length && it_ < 16384UL
           && ((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u)) { rx_span_cursor += 1; it_++; }
}
```

Disassembly of the hot loop:

```asm
15e0: lea    0x1(%rdx),%rax          ; rax = cursor + 1
15e4: mov    %rax,%rcx
15e7: sub    %rdi,%rcx               ; rcx = rax - base   (iteration count)
15ea: cmp    $0x4001,%rcx            ; it_ < 16384 ?
15f1: je     160d                    ; cap reached -> exit
15f3: cmp    %rax,%r8                ; rax <= subject_length ?
15f6: jb     160d                    ; bounds -> exit
15f8: mov    %rax,%rdx               ; cursor = rax
15fb: movzbl -0x1(%r9,%rdx,1),%eax   ; eax = subject[cursor-1]               LOAD (address = base + cursor, cheap arithmetic on rdx from iter i-1)
1601: sub    $0x61,%eax               ; eax -= 'a'
1604: cmp    $0x19,%eax               ; <= 25 (unsigned)?
1607: jbe    15e0                     ; in class -> loop
1609: sub    $0x1,%rdx                ; out of class: back up one
```

No table load at all — the "table" here is two immediate constants (`0x61`,
`0x19`) baked into the instruction stream. **The loop-carried register is
`rdx`, a cursor**, and next iteration's load address is `rdx+1` — computable
the instant `rdx` is known, with no dependency on what the *previous byte's
value was* or on any load's *result*. Consecutive iterations' loads are
address-independent of each other's data, so the CPU can issue them
back-to-back (limited by decode/issue width and L1 bandwidth, not by
load-to-use latency). It is not vectorized (`gcc -O2` did not auto-vectorize
this particular bounded scan), but it does not need to be — the fix here is
address-independence, which this loop already has, not SIMD width.

This is a direct, structural confirmation of hypothesis (b)/(c): the counted
DFA's per-byte walk **is** the scalar table loop from
`studies/simd1/JOURNAL.md` §15 (branchless classify beats it 2-3x); the
VM's counter loop is a *different, already-fast* loop in the other engine,
not the same loop repeated. The distinguishing fact isn't "table lookup vs
no table lookup" in the abstract — it's whether the loop-carried register
feeds an address (cheap, parallel) or is fed *by* a load (serial).

## 4. Measured cost, and the letters/digits asymmetry explained

### 4.1 Letters: per-byte cost, flat with `n`, ratio 5.1x-6.1x

Own `fadriver.c` measurements (find-all, 3 trials, `t-letters-004k`):

| n | DFA outer, ns (17 or 2 matches) | VM outer, ns | DFA ns/byte | VM ns/byte | ratio |
|---|---|---|---|---|---|
| 256 | 14,905-14,980 | 2,842-2,897 | 3.64 | 0.70 | **5.19x** |
| 4096 | 14,804-14,874 | 2,461-2,511 | 3.62 | 0.60 | **5.98x** |
| 16384 | 14,816-14,875 | 2,467-2,511 | 3.62 | 0.60 | **6.00x** |

(bench's own figures, per §2, land in the same range: 5.14x/5.86x/5.56x.)
**Both engines' ns/byte are flat across a 64x change in table size** (256 to
16384 → forward table 1,028 B to 65,540 B, ~3 KB total working set at n=256
counting forward+reverse+class arrays, ~131 KB at n=16384). A cache/capacity
effect would show a knee somewhere in that range; there is none — direct
confirmation that this is latency, not bandwidth or capacity.

Converting to cycles (median calib 3.3749 GHz, forward+reverse combined
since `rx_search` walks every byte twice — once each direction — to resolve
`match_start`): DFA ≈ 3.62 ns/byte × 3.3749 ≈ **12.2 cycles/byte total, ≈6.1
cycles/byte/pass** — in the same neighborhood as `opt3`'s premultiplied
"v1" figure of 7.751 cycles/byte (single pass, a different/richer 18-class
machine; the two are not the same measurement, but they corroborate the
same mechanism at the same order of magnitude). VM ≈ 0.60 ns/byte × 3.3749
≈ **2.0 cycles/byte** for the whole possessified scan (one pass; no reverse
walk is needed since the possessified span sets its own bounds directly).

### 4.2 Digits: fixed per-call cost, flat with `n`, ratio 1.75x-2.0x

`t-digits-016k`, `fadriver.c` (this build; §2 explains the ~1.3-1.4x gap
from the bench's `-fPIC` build):

| n | DFA, ns per `rx_search` call | VM, ns per `rx_search` call | ratio |
|---|---|---|---|
| 256 | 3.57-3.70 | 7.12-7.67 | 1.99x-2.07x |
| 4096 | 3.56-3.71 | 7.14-7.20 | 2.00x-2.02x |
| 16384 | 3.57-3.58 | 7.13-7.13 | 2.00x |

(bench's own build, §2's table: 82,758.7/16,385 = 5.05 ns DFA vs
140,543.0/16,385 = 8.58 ns VM → **1.70x** — same direction, smaller gap,
consistent with PIC narrowing a fixed-cost ratio less than it narrows an
absolute one.) **Flat across `n` in both builds** — exactly what "the first
byte fails classification, both engines bail after one load" predicts: at
n=256 the DFA's table has only 514 entries and at n=16384 it has 32,770,
and the cost is identical, because the walk never gets past state 0.

Why is DFA's fixed cost lower? `rx_search` on the DFA artifact is one flat
function — no auxiliary state. The VM's `rx_search` (§ read of `vm_16384.c`
lines 284-320) binds a `rx_run_state` to stack buffers, calls
`rx_run_state_init` (a loop zeroing `RX_NSLOTS` slots plus two budget
counters), calls `rx_match_anchored` through a real function boundary, and
on success calls `rx_report_captures`. None of that work is wasted in the
letters case (it's a rounding error against ~15,000 ns of real scanning),
but on digits it **is** the entire cost, and it is measurably larger than
the DFA's flat-function overhead — hence DFA's ~2x win, constant regardless
of `n`.

## 5. I-21 (the standing prediction): supported by mechanism

> letters → the VM wins at every rung including 64/128; digits → the DFA
> wins at every rung; no count crossover exists on either axis.

**Supported.** Both halves are now mechanism-backed, not just
data-backed: the letters ratio is a property of which engine's loop carries
a data-dependent vs address-dependent load, which `n` cannot change (it
only changes the table's *size*, and §4.1 shows size doesn't move the
per-byte cost). The digits ratio is a property of each engine's *fixed
per-call overhead*, which by definition doesn't scale with `n` either. There
is no mechanism by which a count threshold could produce a crossover on
either axis, because `n` is not a causal variable in either ratio — only
"does the byte stream stay in-class" is, and that's a run-time subject
property, invisible at compile time.

## 6. [OPT-VMLIT] free measurement: the literal-stepping share

The brief pointed at `bench/email/` for "ctx / level-context" cells;
`bench/email/patterns/` holds only `orig`/`factored`/`floor` (opt3's
subjects), none of which has the literal-word-alternation shape
[OPT-VMLIT] is about. The shape it names — `\b(?:fail|abort|panic)\b...`
— is `bench/bounded`'s `ctx-lazy-256`/`ctx-greedy-256` family. Substituted
here, noted rather than silently swapped.

`--emit-ir` on `\b(?:fail|abort|panic)\b.{0,256}?\b(?:disk|memory|socket|quota)\b`
(`--engine=vm`) confirms the shape directly: every literal word compiles to
a **chain of one-byte `consume` nodes**, one label per character (`L4`
consumes `'f'` → `L9` consumes `'a'` → `L10` consumes `'i'` → `L11` consumes
`'l'` for "fail"; four separate labels for a four-byte word). The emitted C
is one bounds-check-and-compare per byte:

```c
rx_L4: if (scan_position < subject_length && (subject[scan_position] == 102)) { scan_position++; goto rx_L9; }
       goto rx_fail;
```

— never a `memcmp`/`strcmp`, confirming [OPT-VMLIT]'s premise structurally.
The lazy gap (`L20`-`L23`) retries the full 4-branch, 4-9-byte alternation
at **every cursor position** in the gap when no context word follows a
trigger — `bench/bounded/subjects/l-03.bin` is designed exactly for this
("trigger `panic` and no context word after it... the lazy gap walks its
full count and finds nothing").

Timing (single-call driver, 3 trials, `t-letters`-style build, `ctx-lazy-256`):

| subject | bytes | outcome | ns/call | ns/byte |
|---|---|---|---|---|
| `l-00` | 50 | matches immediately | 406-411 | 8.12-8.22 |
| `l-01` | 110 | matches after one gap walk | 1,035-1,043 | 9.41-9.48 |
| `l-03` | 251 | **no match anywhere** — full unanchored scan, full gap walk at the trigger, alternation retried at every position | 3,987-4,016 | **15.88-16.00** |

`l-03`'s worst-case cost is ~1.7-2.0x the ns/byte of a subject that resolves
quickly. **This is a bound, not a percentage** — no `perf` counters means no
direct cycles-in-literal-compare figure, and the ~2x also carries the
outer unanchored attempt loop's own per-position alternation-entry cost
(most of the 251 positions fail on the very first literal byte of `fail`
/`abort`/`panic`, which is cheap; the 256-byte gap walk at the one real
trigger position is where the literal-chain-per-position cost concentrates).
**Recommendation**: if [OPT-VMLIT] is chartered, it needs its own
instrumented-counter measurement (a scratch copy counting literal-consume
invocations vs total steps, `opt3`'s §3 technique) rather than inferring a
share from this proxy. What this measurement DOES establish, cleanly: the
codegen shape (one branch per literal byte, no memcmp) is confirmed, the
worst-case subject the bench already ships (`l-03`) is the right instrument
for that follow-up measurement, and the cost is large enough (~2x) to be
worth that follow-up.

## 7. Selection-rule implication

**Not a threshold. Does not belong in `limits.def`.** A `limits.def` row is
a compile-time value gated on something the compiler can see (a count, a
nesting depth, a size). Both ratios measured here are **independent of
`n`** — §4.1 and §4.2 each show flat behavior across a 64x range of the
only compile-time-visible quantity in the pattern. The variable that
actually decides the winner — whether the subject's bytes stay inside the
class — is a **run-time** property the compiler cannot observe. No count
knob, however placed, can express "pick the VM when the input will mostly
match the class" — that information doesn't exist at compile time for a
`{0,n}` pattern in general (it does for some patterns via static analysis
of what feeds the pattern, but that is out of scope here).

The general mechanism fix is therefore not "move the DFA/VM boundary" but
**give the DFA's single-class counted-repeat the VM's own loop shape**: when
a DFA's per-byte transition graph reduces to "stay in one class, count up to
n" (which is exactly what `[a-z]{0,n}`'s automaton *is* — every one of its
useful states differs only in count, not in which bytes it accepts), emit
the same address-only-dependent bounded scan the VM's possessifier already
produces, instead of walking a premultiplied transition table one dependent
load at a time. This is NOT [OPT-SIMD]'s territory in the narrow sense —
the VM's existing scalar loop already beats the DFA 5-6x with no vector
instructions at all, because it fixes the dependency-chain shape, not the
per-byte work. A SIMD run-extension (classify+clz, `studies/simd1`) is a
**further** win on top of that fix, not a substitute for it — worth stating
explicitly since [OPT-5]'s charter text currently reads as if SIMD is the
first-order fix; the data here says address-independence is, and it's
already sitting in the VM's own emitter.

Framed as a general mechanism (not a special case, per
`pcrec-general-mechanisms-not-special-cases`): any DFA state region that is
isomorphic to "count bytes matching one fixed class, up to a bound" —
whether it's the whole pattern (`[a-z]{0,n}`) or a sub-region reached
through some prefix — is a candidate for this representation. `{0,n}` over
a single class is the simplest instance, not a special case of it.

## 8. Reproduction

```
build/pcrec -p rx -o out.c -- '[a-z]{0,N}'                 # auto, N in {256,4096,16384}
build/pcrec -p rx --engine=vm -o out.c -- '[a-z]{0,N}'     # forced VM
```

Scratch artifacts, drivers (`driver.c` single-call, `fadriver.c` find-all
matching `pcrec-bench/testees/pcrec/driver.c:548-565`), calibration
(`calib.c`) and binaries are under
`/tmp/claude-1001/-home-duxevents-pcrec/6aca71a8-fde5-46c1-aaf1-1563828c0714/scratchpad/opt5m/`
(session scratchpad, not committed, per the scope mandate).
