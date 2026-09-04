# Lane ccd2 — [CC-DIFF] STEP 2 and [OPT-DIAL] STEP 0

**Branch `lane/ccd2`, on `main` at abi 20. Written 2026-09-04 entirely under
the box `.hold` (`.hold_ack` written at 10:46), so every number below comes
from SINGLE COMPILES and no timing loop was run.** The one measurement this
row most needs is a quiet-box item and is named in §6.

---

## 0. What exists, in one screen

| | |
|---|---|
| **The ladder** | `pcrec_options.vm_entry_shape`, a four-rung ordinal (`plain`/`shared`/`forward`/`inline`), emitted from `src/gen/emit_vm.c`, with `--vm-entry-shape=N` and AUTO |
| **The size term** | `VM_INLINE_CHAIN_MAX_BYTES` = 4,096, a `limits.def` selection knee, placed inside a measured gap |
| **The stamps** | `<PREFIX>_VM_ENTRY_SHAPE` (closed token) and `<PREFIX>_VM_PROGRAM_BYTES` (the number the term compared) |
| **The probe** | `tests/codegen/run_inline_capability.sh` — NEEDED under gcc 15.2.0, REDUNDANT under clang 21.1.8, both verdicts reproduced |
| **The inventory** | `docs/design/opt_dial_inventory.md` — 21 switches audited, a draft policy table, the spelling question |
| **Validated** | `make strict` clean; 70 emit-compile-answer runs over 14 patterns x 409 subjects, **0 mismatches**; four rungs compile `-Wall -Wextra -Werror` |
| **Not validated** | `make test`, `make test-codegen`, `make test-axes`, the identity gate, and every ns/call number — all post-lift |

**The headline is not the size term. It is that rung `forward` dominates the
shape [CC-DIFF] STEP 1 shipped**: identical object-code properties, half the
`.text` and half the gcc time, at every width measured. §3.

---

## 1. What STEP 1 conflated

STEP 1(a) put `always_inline` on the eight VM entry-chain statics of a
frameless artifact and measured `dig-upto-16` at 0.611. That one attribute
does two things at once:

1. it deletes the entry's 152-byte frame, its `-fstack-protector-strong`
   canary and its out-of-line call — where the measured win came from;
2. it replicates the matcher body into **all six entries**, because six
   entries each honour it.

On the small programs STEP 1 measured, (2) SHRANK the artifact (`.text`
1,561 -> 1,417) and was therefore invisible. `[ENG-ISL]` made 70 KB programs
frameless, the same gate fired, and isl1 measured `.text` x3.8 and gcc x4.3 on
`w-256` (its §4.2). That is what filed this step.

**The ladder exists to price (1) and (2) apart**, which is exactly what
Frank's wrapper-forward question asked for: *"why can't `rx_match` call
`rx_match_in` with the stack buffer?"*

---

## 2. The four rungs, as built

`pcrec_options.vm_entry_shape`, an ORDINAL like `unroll_k` and not a bit,
ordered min-size to max-speed because that is the direction `[OPT-DIAL]`'s
dial runs in. `--vm-entry-shape=N`, 0 = AUTO.

| N | token | what is emitted |
|---|---|---|
| 1 | `plain` | no attribute anywhere — the pre-`[CC-DIFF]` shape. One body; six entries, each with frame, canary and call |
| 2 | `shared` | body `noinline` (ONE copy, called); the three un-suffixed entries FORWARD to their `_in` siblings through a static empty descriptor |
| 3 | `forward` | the same forwards; body inlined into the three `_in` entries — THREE copies |
| 4 | `inline` | six copies — STEP 1(a) as shipped |

The forwarding entry is literally three instructions. `objdump` on `w-64`
rung 2:

```
0000000000003ec0 <rx_search>:
    3ec0:  endbr64
    3ec4:  lea    0x0(%rip),%r8
    3ecb:  jmp    3db0 <rx_search_in>
```

No frame, no canary, no local at all — which is the whole of why the forward
is free. Compare rung 1's:

```
0000000000003e80 <rx_search>:
    3e80:  endbr64
    3e84:  sub    $0x98,%rsp            <- the 152-byte frame
    3e8b:  mov    %fs:0x28,%rax         <- the canary
    ...
```

### 2.1 The legality predicate has a SECOND term, and it is a correctness term

Rungs 2-4 need `has_push` false, exactly as STEP 1's gate did. **Rungs 2 and 3
need more.** They bind a static EMPTY descriptor, so the artifact must
provably never WRITE the working storage — and `has_push` does not say that.

**The trail is storage a frameless artifact can still write.** `(abc)(def)`
emits no `RX_PUSH` and stamps `RX_VM_FRAMELESS 1`, and it saves two capture
slots through `RX_SET` -> `RX_TRAIL`, which writes `run->trail[]`. Binding a
zero-capacity descriptor there would make `RX_TRAIL` return `RX_R_FRAMES`:
**a match turned into a give-up, a silent wrong answer.**

`Vm.emitted_set` is that second term, set by `vm_set` in the same call that
writes the bytes — `emitted_push`'s discipline, and for its reason. The
legality pair is then:

```c
const bool may_attr = !has_push;                   /* rungs 2, 3, 4 */
const bool may_fwd  = !touches_storage && !tiered; /* rungs 2, 3    */
```

`tiered` declines the forward as braces rather than as a case: a tiered entry
is a fast-tier run plus a `FRAMES` escalation ([OPT-1]), which a forward would
delete rather than re-spell. A storage-untouched artifact can never reach a
`FRAMES` give-up in the first place — `RX_PUSH` and `RX_TRAIL` are its only two
sites — so the two conditions are expected never to co-occur, and the term
costs nothing.

### 2.2 The fallback is by INTENT, and the first draft had it backwards

`shared` and `plain` are the two ONE-BODY rungs; `forward` and `inline` the
two copying ones. Where a forward rung is illegal, `shared` falls to `plain`
and `forward` falls to `inline`. The first draft promoted BOTH to `inline`,
which would have answered a caller asking for minimum size with the largest
artifact on the ladder.

Observed working, in the identity run's own shape column: `cap2`
(`(abc)(def)`, frameless but trail-touching) reads `plain` at rung 2 and
`inline` at rungs 3 and 4; `email` (framed) reads `plain` at all four.

---

## 3. THE LADDER — 20 artifacts, four rungs, single compiles

gcc 15.2.0, `-O2 -std=gnu11 -c`, `.text` from `size`, wall and RSS from
`/usr/bin/time -v`. `prog` is the artifact's own `RX_VM_PROGRAM_BYTES`.
Subjects: `[a-z]{0,8}`, `\d{1,16}`, `[0-9a-f]{32}`, `[12][0-9]{3}`, an IPv4
shape, a 16-byte literal, the bench's `w-8`/`w-64`/`w-96`/`w-256` (read-only),
and `wp-K` — the first K words of `w-64`'s own alternation, constructed here
to fill the width gaps and labelled as such, never a corpus or bench pattern.

### 3.1 `.text`, bytes

| prog | subject | plain | shared | forward | inline |
|---|---|---|---|---|---|
| 645 | `[a-z]{0,8}` | 1,824 | 1,520 | **968** | 1,600 |
| 646 | `\d{1,16}` | 1,822 | 1,518 | **934** | 1,534 |
| 695 | `[0-9a-f]{32}` | 1,898 | 1,594 | **1,002** | 1,602 |
| 818 | `[12][0-9]{3}` | 1,938 | 1,634 | **1,066** | 1,826 |
| 2,618 | 16-byte literal | 1,294 | **1,078** | 1,542 | 2,710 |
| 2,993 | IPv4 shape | 2,460 | **2,140** | 2,428 | 4,516 |
| 3,222 | wp-2 | 2,243 | 1,939 | **1,723** | 3,051 |
| 4,024 | wp-3 | 2,352 | 2,064 | **2,016** | 3,664 |
| 5,183 | wp-4 | 2,568 | **2,280** | 2,568 | 4,680 |
| 5,985 | wp-5 | 2,685 | **2,397** | 2,717 | 5,093 |
| 6,954 | wp-6 | 2,900 | **2,612** | 3,052 | 5,748 |
| 8,558 | w-8 | 2,950 | **2,670** | 3,878 | 7,318 |
| 12,514 | wp-12 | 3,521 | **3,225** | 5,401 | 10,353 |
| 17,776 | wp-16 | 4,178 | **3,882** | 7,338 | 14,210 |
| 26,226 | wp-24 | 6,778 | **6,482** | 12,394 | 24,258 |
| 36,217 | wp-32 | 9,219 | **8,915** | 16,771 | 32,947 |
| 55,858 | wp-48 | 13,142 | **12,854** | 25,062 | 49,534 |
| 79,451 | w-64 | 18,320 | **18,036** | 35,444 | 69,516 |
| 119,802 | w-96 | 26,354 | **26,082** | 57,898 | 115,650 |
| 305,686 | w-256 | 47,783 | **47,515** | 149,787 | 296,643 |

Two more subjects are in the run and are the controls: `email` (framed) reads
2,728 at all four rungs, and `cap2` (frameless, trail-touching) reads 2,526 /
2,446 / 2,446 / 2,446. **A framed artifact is untouched by every rung.**

### 3.2 gcc wall and peak RSS, the extremes

| | shared | forward | inline |
|---|---|---|---|
| w-8 gcc / RSS | 0.10 s / 32 MB | 0.17 s / 33 MB | 0.29 s / 36 MB |
| w-64 | 0.52 s / 54 MB | 1.51 s / 89 MB | 2.66 s / 112 MB |
| w-256 | 2.04 s / 102 MB | 8.17 s / 317 MB | 13.61 s / 365 MB |

### 3.3 THE STRUCTURAL TABLE, and it is the same on every one of the 20

`objdump -dr` for `__stack_chk` references, `objdump --disassemble=rx_search`
for the frame, `nm` for the chain symbols.

| rung | entry frame | `__stack_chk` refs | chain symbols out of line | body copies |
|---|---|---|---|---|
| `plain` | yes | 7 (3 on a small artifact) | 2 | 1 |
| `shared` | no | 5 (1) | 1 | 1 |
| `forward` | no | **0** | **0** | 3 |
| `inline` | no | **0** | **0** | 6 |

**`shared` DOES NOT DELETE THE CANARY, and that is the qualification the
whole rung turns on.** It moves it off the three un-suffixed entries and
leaves it in the three `_in` entries, because `<prefix>_run_state`'s own
`slot_values[]` array trips `-fstack-protector-strong` there and the
out-of-line body stops gcc proving it dead. That is precisely the mechanism
[CC-DIFF] STEP 0 measured at **0.986 — i.e. nothing** — when it tried eliding
the buffers without inlining. So `shared`'s run time may sit much closer to
`plain`'s than to `inline`'s, and nothing here says which. §6.

### 3.4 THE FINDING: `forward` is `inline` at half the price

| | 646 | 2,618 | 8,558 | 17,776 | 79,451 | 305,686 |
|---|---|---|---|---|---|---|
| `forward` / `inline` `.text` | 0.61 | 0.57 | 0.53 | 0.52 | 0.51 | 0.50 |

Twenty artifacts, no exception, range 0.50-0.61. And §3.3 says the two rungs
are structurally IDENTICAL: no frame, no canary anywhere in the artifact, no
out-of-line chain symbol. **The six copies were never what the mechanism
needed** — there are three distinct call shapes, and the `_in` entries are
where they live; the sixth copy exists only because six entries each honour
an attribute.

This is Frank's wrapper-forward question answered in the emitter, and it is
the reason AUTO no longer selects `inline`.

### 3.5 THE SIZE TERM, and the gap it sits in

The remaining choice is `forward` against `shared`, and it does have a knee:

| prog | 646 | 818 | 3,222 | 4,024 | **gap** | 5,183 | 8,558 | 79,451 | 305,686 |
|---|---|---|---|---|---|---|---|---|---|
| `forward`/`shared` `.text` | 0.62 | 0.65 | 0.89 | 0.98 | | 1.13 | 1.45 | 1.97 | 3.15 |

Below about four kilobytes of program `forward` is SMALLER than `shared` as
well as structurally better; above it, its two extra body copies start to
cost and the price rises without bound. **`VM_INLINE_CHAIN_MAX_BYTES` = 4,096
sits inside the one measured gap the crossing falls in** (4,024 at 0.98x,
5,183 at 1.13x).

AUTO therefore reads: at or below the term take `forward`, above it take
`shared`; where the forward rungs are illegal, `inline` below and `plain`
above — the two shapes that shipped after and before STEP 1 respectively, so
neither step down is novel code.

**ONE HONEST WEAKNESS IN THE TERM.** Program bytes is an imperfect predictor:
the 16-byte literal at prog 2,618 has `forward`/`shared` = 1.43, well above
the trend, while `wp-2` at prog 3,222 reads 0.89. The relation is not
monotone, so a scalar term will be wrong on individual artifacts in both
directions. It is the proxy the emitter already has (`job->vmsb.len`, the
buffer the program was just emitted into) and the alternative is a second
analysis, which this file's standing rule forbids.

---

## 4. The capability probe

`tests/codegen/run_inline_capability.sh`. Frank asked (2026-09-03 23:0x)
whether there is a guard telling us the compiler already has the
optimisation. **A preprocessor test cannot answer it**:
`__has_attribute(always_inline)` says the attribute is understood, never that
the inlining would have happened without it. The capability is observable only
in object code.

**Method.** Compile `\d{1,16}` (STEP 0's own `dig-upto-16` cell) under the
harness's `CC` at rung `inline` and again with the attribute gone, and ask
`nm` whether `rx_search_run` / `rx_match_anchored` survive.

**Arm B is built twice and the two must agree.** Its convenient spelling is
the emitter's own `plain` rung — the subject's own author, which
`docs/dev/learnings.md` §3 forbids as a sole control. So the file ALSO builds
arm B by a textual `sed` removal, which knows nothing about the emitter, and
is red if the two spellings differ in source or in symbol table.

**MEASURED: the two spellings are byte-identical apart from the paired
header's `#include`.** `--vm-entry-shape=1` really is `--vm-entry-shape=4`
with the attribute deleted, which is a stronger statement than the check
needs and is worth recording.

**Both verdicts reproduced, which is the non-vacuity that makes either one
worth reading:**

```
gcc 15.2.0    arm A: <none>   arm B: rx_match_anchored rx_search_run   -> NEEDED
clang 21.1.8  arm A: <none>   arm B: <none>                            -> REDUNDANT
```

The gcc arm is STEP 0's own `nm` witness reproduced, which had lived only in
its report.

**It is a census line and never red on a verdict.** Pinning either answer
would go red on a compiler upgrade that changed nothing about pcrec. It is red
on exactly two things, both failures of the probe rather than verdicts: the
witness stopping being frameless (the `[MECH-REACH]` shape — a witness that
stopped reaching its site), and a symbol table that cannot be read or two
arm-B spellings that disagree.

---

## 5. Answer identity, as far as the hold allows

14 patterns x 5 shape settings (AUTO plus the four rungs) x 409 subjects, each
run as a find-all loop reporting every span and every capture group, compared
by digest against the AUTO build.

**70 runs, 0 mismatches.** The populations all fire: framed artifacts
(`email`, `(\w+)\s+\1`, `a(b|c)+d`, `(?<=foo)bar`) read `plain` where the rung
is illegal; trail-touching frameless artifacts (`(abc)(def)`,
`([a-z]+)@([a-z]+)\.([a-z]{2,4})`) take the intent-preserving fallback; the
wide alternations exercise `shared` and `forward` on real island programs.

**THREE OF THE FOURTEEN ARE VACUOUS AND I AM SAYING SO**: `[0-9a-f]{32}`,
`(?<=foo)bar` and `(?>a*)ab` matched NOTHING on this subject set (all three
hash to the all-nomatch digest), so they tested the emitter and not the
answers. Eleven witnesses are real. The corpus sweep that would close this is
`make test` plus `make test-axes`, both post-lift.

Every one of the four rungs also compiles `-Wall -Wextra -Werror`, which is
the generated-code standard.

---

## 6. WHAT IS NOT MEASURED, and it is the number this row turns on

**No ns/call was taken. The box was held all day and a timing harness that
caveats instead of refusing is worse than none.**

The run-time arm currently in evidence is isl1's ladder (§12.2 of its report):
`inline` against `plain` at a flat **16-23%** across two width decades. Rungs
`forward` and `shared` are NEW POINTS and neither has been timed.

Two questions, in priority order:

1. **Is `shared` at `plain`'s run time or at `inline`'s?** §3.3 says it keeps a
   canary in each `_in` entry and re-pays one call, which is structurally the
   shape STEP 0 measured at 0.986 (nothing). If `shared` is near `plain`, the
   size term is doing real work and 4,096 is roughly right. If it is near
   `inline`, `shared` dominates everything and the term becomes nearly moot.
2. **Is `forward` at `inline`'s run time?** Structurally they are identical, so
   the only way `inline` wins is gcc specialising the search bump-along
   separately in `rx_search` — which is measurable and is why `inline` is kept
   as a reachable rung rather than deleted.

Also unmeasured, and all post-lift: `make test`, `make test-codegen`,
`make test-axes` over the new ordinal, the identity gate, and the bench's own
altwide arms (this box, `gcc -O2`, one subject shape).

---

## 7. The abi event, and the D94 site list BY GREP

**This branch changes emitted scaffolding and is therefore an abi event.** The
forwarding entries, the static descriptor and the two new stamp lines all sit
ABOVE `goto <prefix>_L0;`, so `run_recursion_identity.sh`'s comparison (A) —
the VM program region — is expected UNMOVED, and comparison (B) moves.

**The branch does NOT bump the number** (brief's instruction); the merging
session assigns it. Grepping the tree for readers of the current value found
**SEVEN**, and a hand-enumerated list would plausibly have stopped at four:

| # | site | what it holds |
|---|---|---|
| 1 | `src/gen/emit_dfa.c:1662` | `sb_puts(c, "    .abi = 20,\n");` — the stamp |
| 2 | `src/gen/emit_dfa.c:~1525` | the `.abi` comment's per-artifact-kind breakdown; r37 A12 requires a new paragraph, not just a digit |
| 3 | `tests/codegen/run_codegen_tests.sh:2758` | `ABI_EXPECT=20` |
| 4 | `tests/codegen/run_codegen_tests.sh:2760` | the `bad` message's cumulative event narrative, which gains a `20->21` clause |
| 5 | `tests/codegen/run_recursion_identity.sh:699` | `FILEPIN="${RECURSION_IDENTITY_FILEPIN:-8d68ddc2}"` — comparison (B)'s pin, re-pinned to this change's last src commit in the same change |
| 6 | `docs/spec/match_api.md:159` | "`rx_info.abi` is `20`" |
| 7 | `docs/spec/match_api.md:1801` | "`rx_info.abi` is `20` on every artifact today ([DD-13b.W1.3] bumped it …)" — the event list, which gains this row's paragraph |

`make test-codegen` before delivering, per the situation index.

---

## 8. The spec hunks on this branch (D80)

- `docs/spec/tuning.md` **§2.21**, new: `--vm-entry-shape=N`, the rung table,
  the legality rule, AUTO and the size term, the two stamps. Placed after
  §2.20 and before §3.
- `docs/spec/match_api.md` **§6.3**: the two new family-(b) stamps with their
  IFFs, plus an amendment to `<PREFIX>_VM_FRAMELESS`'s STEP 1 paragraph —
  its "the entry chain is inlined" reading is now a NECESSARY and no longer a
  SUFFICIENT condition, because a frameless artifact can take any of the four
  rungs. `<PREFIX>_VM_ENTRY_SHAPE` carries the rest.
- `src/core/limits.def`: the `VM_INLINE_CHAIN_MAX_BYTES` row with the ladder
  at the row, `kind` "selection knee", `override` FLAG (`--vm-entry-shape=N`
  overrides the decision the threshold makes), `anchor` "" — it bounds a
  compiler-side selection, not a promise to a caller, so `limits.md` §3 wants
  no entry (that file's own rule).
- Per-directory `CLAUDE.md`: `src/gen/` (the ladder section), `tests/codegen/`
  (the probe), `docs/design/` (the inventory).

---

## 9. [OPT-DIAL] STEP 0 — the inventory

`docs/design/opt_dial_inventory.md`. The finding is a count:

> Of pcrec's twenty-one generation-time switches, **FOUR** carry a measured
> two-axis exchange rate and belong on a dial. **TWO** are measured pure wins
> and must never be on it. The remaining **FIFTEEN** are unmeasured on at
> least one axis — nearly always on SIZE, because pcrec has measured time far
> more often than bytes.

On the dial: `--vm-entry-shape` (this wave's), `--unroll=K`, `--engine`,
`-fno-premul-table`. Off it as pure wins: `-fno-start-pinned`,
`-fno-alt-island`. The document carries every switch's numbers with citations,
a draft five-column policy table, and §7's list of the measurements that would
move the fifteen.

**Three things in it want the manager's attention specifically.**

**(a) A FOURTH BUCKET THE CHARTER DID NOT ANTICIPATE.** `-fno-splice-calls`
and `-fno-prefilter-collapse` are measured on BOTH axes and reverse sign on
time with the SUBJECT POPULATION (SPLICE is 8-26% faster on a mixed corpus and
up to 14% slower on a lexical-only one, at 5x the bytes per call site; the
collapsed prefilter is 2.7x faster on a rejected subject and catastrophically
slower on `((a)|b){0,400}c`). A speed-vs-size ordinal cannot express "faster
if your subjects reach the call site". Recommendation: both off the dial, with
`tuning.md` saying they are chosen from the workload rather than the profile.

**(b) `--engine` HAS THE BIGGEST LEVER AND THE MOST VIOLENT RANGE.**
`--engine=vm` reaches 4-9% of object size at up to 173,580x slower on the fail
path. Its policy-table row is deliberately FLAT in every column: one dial
position that could turn a 0.2 us answer into a 35 ms one is not a dial
position. Reaching it needs a per-pattern predicate, which is its own row.

**(c) ONE RULING WORTH MAKING BEFORE THE DIAL IS BUILT.** The policy table
must be an ALLOWLIST: the dial may not set a switch that has no measured rate.
A profile that quietly denied `-fno-possessify` because "min size probably
means less of everything" is exactly the guess this inventory exists to
prevent.

**The spelling question**, three alternatives with trade-offs in the document.
Recommendation: **named profiles** (`--tune=size|balanced|speed`) with a
`<PREFIX>_TUNE` token stamp — a closed token is what D82 wants for a
selection, it extends without renumbering, and three names is an honest match
to how much substance the table has. `-O`-family letters read better but
collide with the reader's expectation that `-O` addresses the C compiler's
optimisation of the artifact, which pcrec does not control.

---

## 10. What I need ruled

1. **The abi number**, and whether this branch rides another event (§7).
2. **AUTO's default changing from `inline` to `forward`.** It is measured on
   size and gcc and NOT on run time (§6). The conservative alternative is to
   ship the ladder with AUTO reproducing today's behaviour (`inline` below the
   term, `shared` above) and move the default after the quiet-box ladder. I
   built the measured-better default because the structural evidence is
   uniform across 20 artifacts, but the ruling is the manager's.
3. **`--vm-entry-shape` as a permanent public surface.** The brief allowed an
   internal switch. I built a documented ordinal because (i) the size term
   needs something for a caller to override, (ii) `test-axes` needs a spelling
   to sweep, and (iii) it is `[OPT-DIAL]`'s first native rung — the dial's
   whole premise is per-switch ordinals. If the manager wants less surface,
   the reduction is to keep AUTO and the term and drop the CLI parse.
4. **Whether `<PREFIX>_VM_PROGRAM_BYTES` earns its place.** It makes the term
   auditable and it moves bytes on EVERY VM artifact including framed ones,
   which costs the "a framed artifact is byte-identical" property STEP 1 had.
5. **The dial's spelling** (§9) and the allowlist ruling.

---

## 11. Disclosure

Injected context that shaped decisions: the repository `CLAUDE.md` (the
situation index's rows on abi bumps being D76/D94 events found BY GREP, on
`gnutimeout` over `timeout`, and on the spec being the contract under D80 —
all three changed what I did); the memory index line
`pcrec-general-mechanisms-not-special-cases`, which is why the trail term is
`Vm.emitted_set` on `vm_set` rather than a `(abc)(def)`-shaped exception; and
`pcrec-build-under-measurement` (D77), which is why the inventory is a
document and why §6 states what is unmeasured rather than estimating it.

`wp-K` patterns are constructed from `w-64`'s own word list and are labelled
as constructed wherever they are cited; they are not bench or corpus patterns.
Everything read from `/home/duxevents/pcrec-bench` was read-only.
