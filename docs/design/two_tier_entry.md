# The two-tier default entry — `[OPT-1]` STEP 2

**Status: design, written before the code (lane srTier, 2026-08-25).** Plan row
`[OPT-1]`, whose STEP 1 measurement is what this fixes.

## 1. The measured cause

`gcc -fstack-clash-protection` probes every page of a function's frame on EVERY
call. `<prefix>_search` declares a `<prefix>_run_buffers storage` local —
98,512 B for the email specimen's stamped 2048/3072 default, 24 pages — so a
16-byte subject that matches in a few hundred instructions pays 24 probes
first. MEASURED (STEP 1, lane srOpt1, N=100k, median of 5, `taskset -c 11`):
**233.8 ns/call for `rx_search`, 46.3 for `rx_search_in`, 46.2 for `rx_search`
under `-fno-stack-clash-protection`** — the probing is ~99 % of the gap.
Zeroing (144 B, both paths), page faults and frame width were each measured and
excluded. The tax is proportional to the STAMPED DEFAULT: `(\w+)\s+\1` (272 B)
and `(?<=foo)bar` (240 B) pay nothing.

So the cost is not "the buffer is big", it is "**a big buffer is on the frame of
the function every call enters**". The fix moves it off that frame without
changing the depth the artifact reaches.

## 2. The shape

```c
static __attribute__((noinline)) int rx_search_deep(...)   /* the DEEP tier */
{
    rx_run_state run;  rx_run_buffers storage;   /* the D73 default, unchanged */
    rx_run_state_bind(&run, storage.frames, RX_RESUME_FRAMES,
                            storage.trail,  RX_TRAIL_FRAMES);
    return rx_search_run(subject, subject_length, search_from, capture_spans, &run);
}
int rx_search(...)                                          /* the FAST tier */
{
    rx_run_state run;  rx_fast_buffers fast;     /* RX_FAST_FRAMES/_TRAIL */
    int result;
    rx_run_state_bind(&run, fast.frames, RX_FAST_FRAMES,
                            fast.trail,  RX_FAST_TRAIL);
    result = rx_search_run(subject, subject_length, search_from, capture_spans, &run);
    if (result == PCREC_ERR_FRAMES) { RX_TIER_NOTE(); return rx_search_deep(...); }
    return result;
}
```

`noinline` is load-bearing: inlined, the 98 KB is back on `rx_search`'s frame
and the change does nothing.

**There is still ONE run function and one matching loop.** `<prefix>_search_run`
is unchanged; the tiers are two callers of it, exactly as the un-suffixed and
`_in` entries already are — no matcher body is duplicated. **The `_in` entries
are untouched**: they never paid the tax, so they have nothing to escalate
from. `_in(NULL)` still delegates to the un-suffixed entry and so gets the
tiering, which is what §10.3's "the same call" requires.

## 3. Sizing the fast tier

One 4 KB guard page is the ceiling, and the entry's frame holds more than the
two arrays: `slot_values[NSLOTS]`, the run state's scalars, the `rx_ctx`, and
whatever `_run` and `match_anchored` spill when gcc inlines them in (both are
`static`, so it may). The ARRAYS-PLUS-SLOTS budget is therefore **3,072 B**,
leaving 1 KB of headroom:

```
avail = VM_FAST_TIER_BYTES - NSLOTS * sizeof(ptrdiff_t)
total = resume_frames*resume_frame_size + trail_frames*trail_frame_size
fast_frames = resume_frames * avail / total     (integer: rounds DOWN)
fast_trail  = trail_frames  * avail / total
```

The scale keeps the two capacities in the SAME RATIO the emitter chose. That
ratio is derived from the pattern by `vm_cost` (2.000 frames and 8.982 trail
entries per level on the `^(a(?1)?b)$` specimen, `frame_buffer_design.md` §4),
so scaling them independently would give up on the wrong axis first. Worked,
for the email specimen (call-free, 24 B/frame, 16 B/trail, 2048/3072):
`total` = 98,304, `fast_frames` ≈ 60, `fast_trail` ≈ 90, arrays ≈ 2,880 B.

**The budget is asserted against `gcc -fstack-usage`, not trusted** — the
arithmetic is the emitter's claim, gcc's frame is an independent measurement of
it, and §5(c) checks the latter.

### 3.1 When there is ONE tier

`total <= avail` (the default already fits — the common case, and the one STEP 1
measured paying nothing); or `NSLOTS*8 >= VM_FAST_TIER_BYTES` (the run state
alone is over a page); or `fast_frames < 16 || fast_trail < 16` (a tier that
small escalates on nearly everything, and two runs cost more than one). In all
three the artifact emits the shape that ships today: no `_deep`, no
`<prefix>_fast_buffers`, entries unchanged.

**Not a special case folded in beside the general one**: when the two tiers have
the same capacity there is one tier, and emitting two identical tiers would be
the parallel mechanism. `RX_FAST_FRAMES == RX_RESUME_FRAMES` **IS** "this
artifact has one tier", by whichever of the three routes — `-fno-tiered-entry`
(§6) included.

## 4. Why the answers are identical

The claim: every return value and every capture span equals today's single-tier
entry's. It follows from one property.

> **The deep tier's run is a bit-for-bit replay of today's entry, from
> scratch.** Same capacities; `run_state_init` refills both budgets; `_run`
> re-runs the prefilter and the same start-position loop; the VM is
> deterministic. Nothing the fast tier did carries over because nothing COULD:
> the run state is a local of the tier that declared it (§5.3 — no allocation,
> no thread-locals, no mutable statics), so the deep tier starts from an initial
> state by construction.

A match, a no-match, `STEPS`, `WORK` or `INTERNAL` from the fast tier is
returned directly, and equals today's because the two traces coincide until the
smaller capacity first binds — which, on those outcomes, it never did.
`FRAMES` escalates, and the replay yields today's answer whatever it is.

The one genuine difference is INVISIBLE: the fast tier may report `FRAMES` where
today reports `STEPS`, reaching its smaller capacity earlier in the same trace.
That value is never returned — it is the trigger — and the replay then reports
the `STEPS`.

**Budgets RESET on escalation; carrying the remainder would break this.** The
brief offers reset-or-carry; only reset is admissible, because a deep run
started depleted is not a replay and would report `STEPS` where today matches.
It is free (`run_state_init` already does it) and is stated in spec §10.9. Its
cost is that an escalating match does the fast tier's work twice (§7).

## 5. `FRAMES` is exactly "capacity exhausted", and the only trigger

Four emitted sites produce `R_FRAMES`, all four `depth >= cap`: `RX_PUSH` and
`RX_CALL` on `resume_*`, two on `trail_*`. **Trail exhaustion also reports
`FRAMES`**, which is why the tier escalates on the CODE rather than on a depth
it inspects itself.

**The fifth site that mentions a capacity is not a capacity test.** `vm_region`'s
`if (call_frame >= run->resume_cap) return R_INTERNAL` is D72's sentinel test:
`CALL_TOP_NONE` is `(size_t)-1`, out of range for every capacity, and a live
`call_top` is always `< resume_depth <= resume_cap` because `RX_CALL`'s own
guard runs before it assigns one. It fires on the same event under both
capacities. This is the one place identity could have failed silently, so it is
checked (§6) rather than assumed.

## 6. The checks, the stamps, the flag, the ABI

`tests/codegen/run_tiered_entry.sh` (opt-in, `make test-tiered-entry`), on the
`^(a(?1)?b)$` specimen `fb_exact_driver.c` already uses: subjects at **1,
FAST-1, FAST, FAST+1 and DEFAULT frames**, plus n=342 (deep, must MATCH) and
n=343 (deep, must give up `FRAMES`). Three observables from three sources that
can disagree:

- **(a) the escalation site.** Under `-DRX_TEST_TIER_HOOK` the artifact calls
  `extern void <prefix>_tier_escalated(void)`, which the driver counts. An
  extern FUNCTION, not a counter: a mutable static in an artifact is a TS-1
  failure and a §5.3 breach. Without the `-D` the hook is `((void)0)`, so what
  these checks read IS the default artifact's text.
- **(b) the capacity, through the untouched `_in` contract.** `_search_in` with a
  descriptor of exactly `RX_FAST_FRAMES`/`_TRAIL` reproduces the fast tier's
  boundary without going near the tier code. (a) and (b) must agree on every
  subject.
- **(c) `gcc -fstack-usage`.** The un-suffixed entry's frame < 4096; the `_deep`
  static's > 90,000.

Answers: every subject's return and spans must equal `_search_in`'s with a
DEFAULT-sized descriptor — today's execution, through an entry this change does
not touch. **Validation plant (per the brief): bind the default capacity while
stamping the fast one, so the fast tier never escalates.** (b) then predicts
escalation where (a) counts none and (c) reports a 98 KB frame — while the
n=342 ANSWER stays right, which is why an answers-only check would have gone
green.

**Stamps.** `<PREFIX>_FAST_FRAMES`/`_FAST_TRAIL`, VM-only on every VM artifact:
§6.3(b) capacity facts, not §10.4 caller arithmetic, and a DFA artifact has no
tier. **No DFA byte moves.**

**`-fno-tiered-entry` / `PCREC_NO_TIERED_ENTRY` (bit 14)** — D46's
controllability half, deny-only (D47.3: nothing to address, nothing to force).
It emits the single-tier shape verbatim, so it is both the bisect lever and the
way an identity gate can compare the old entry. Masked out of `rx_info.flags`
via `strategy_denials`: it changes no answer, and what it DID change is already
reported by `FAST_FRAMES`.

**`rx_info.abi` 4 → 5** and `run_recursion_identity.sh` comparison **(B)**
re-pinned to this change's last `src` commit (D76/`[TT-11]`, same change).
Comparison **(A)** must be byte-identical: the tier lives in the entry
wrappers, emitted after `<prefix>_accept:`. If (A) moves, the change is wrong
and stops. **Spec (D80):** `match_api.md` §3, §5.3, §10.4, new §10.9;
`limits.md` §3.2; `tuning.md` §2.12.

## 7. What this costs and does not fix

A pattern that genuinely needs depth pays MORE — a wasted fast attempt, bounded
by the fast tier's own capacity (~60 frames plus one prefilter scan), paid only
by calls already going deep. The depth ceiling is unchanged (D73); this is about
the cost of NOT going deep. The `_in` entries gain nothing, having lost nothing.

**K33 narrows, it does not close.** §5.3 measures `<prefix>_search` at
131,216 B and says a 128 KB thread faults **on any subject, a 2-byte one
included**. That sentence becomes false: the entry's frame is under a page, so
such a thread now matches every subject the fast tier holds and faults only on
one that escalates. K33, spec §5.3 and the three arms of
`run_stackdepth_tests.sh` — whose cause-check reads `rx_search`'s frame and
fails when it FITS — are re-derived from `rx_search_deep`'s frame in this
change, and the fast frame becomes a new positive assertion there.
