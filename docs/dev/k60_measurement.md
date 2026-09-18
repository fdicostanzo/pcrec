# K60 — THE MEASUREMENT

Lane `k60meas`, 2026-09-18, branch `lane/k60meas` off `272bf970`.
Chartered by Frank after the manager's first disposition proposal was
rejected for being flag-shaped. **This lane measures K60. It does not fix
it.** Every number below was produced on this Mac (darwin/arm64, gcc-16)
with `make alloc`'s own injected build tree; nothing under `src/` ships
from this branch except a clearly-marked `[K60-PROBE]` commit the manager
drops at merge.

`docs/dev/known_issues.md` K60 is the entry under measurement. **Three of
its factual claims are refuted below**, so read §5 before citing it again.

---

## 0. The headline, in four sentences

There is **one** absorption mechanism with a measured population, and it is
**not** either of the two K60 names. `emit_state_legend`
(`src/gen/emit_dfa.c:3615-3618,3660`) allocates five buffers with raw
`malloc`, returns silently on NULL, and accounts for **every one** of the
40 absorptions in K60's own two witnesses — a deliberate, documented
cosmetic degradation, not a retry-ladder state defect. The second
mechanism K60 names, the `[ART-SIZE]` ladder's blanket catch, **is real and
is much worse than anything K60 measured (68.4%)**, but no witness in the
tree reached it until this lane added one. And K60's "one confirmed
mechanism" — a never-reset `cx.size_cap_refused`/`cx.dfa_overflowed` — is
**refuted by three lines of `compile.c`**: the `Ctx` is a loop-local that
is `memset` at the top of every attempt, so those flags cannot be stale
across attempts and never were.

---

## 1. THE DECISIVE EXPERIMENT — fail-from-N-onward

### 1.1 What was built

`tests/core/alloc_check.c` gained a **SUSTAINED** mode: fail allocation `N`
**and every allocation after it**, against today's single-shot mode (fail
exactly `N`, let every later one succeed). Selected by `--sustained` /
`--both`; the argument-free invocation is unchanged, because
`tests/resource/run_resource_tests.sh` section 2b runs this binary
argument-free under `make test` and greps its output.

The question it settles: single-shot cannot distinguish *"the compile
degraded gracefully"* from *"the next allocation happened to succeed"*,
because in single-shot mode the next allocation always succeeds.

### 1.2 The numbers

`make alloc CC=gcc-16 ALLOC_ARGS="--both --sites"`, this box, quiet:

| witness | pattern / axes | K | single-shot absorbed | sustained absorbed |
|---|---|---:|---:|---:|
| W1 (DFA) | `[a-z]+`, auto | 72 | **15 (20.8%)** | **5 (6.9%)** |
| W2 (VM cursor rung) | `[a-z]{2,10}`, `--engine=vm` | 11 | 0 (0.0%) | 0 (0.0%) |
| W3 (unicode-props/utf8) | `\p{L}`, `-e utf8 --features unicode-props` | 328 | **25 (7.6%)** | **0 (0.0%)** |
| W4 (size-term ladder) | see §2.3 — **added by this lane** | 158 | **108 (68.4%)** | **0 (0.0%)** |

The single-shot column reproduces waveu's filed numbers exactly (15/72 first
at N=57; 25/328 first at N=160; 11/11 clean), which is what makes the
instrument change credible as behaviour-preserving.

### 1.3 What it answers

**Absorption does not survive sustained failure, with one small, fully
explained exception.** W3 collapses 25 → 0 and W4 collapses 108 → 0: under
a genuinely failing allocator every one of those 133 trials ends in a clean
diagnosed refusal. W1 retains 5, and those 5 are **N = 68..72 — the last
five allocations the whole compile makes.** Nothing needs memory after
them, so there is no later allocation for the failure to propagate through.

So the honest reading of the two columns is **not** "single-shot overstated
the benignity". It is:

- The absorbing paths are real and unconditional — they genuinely do not
  need the memory they asked for, in single-shot and sustained alike.
- A *real* allocator failure nonetheless produces a correct refusal in
  almost every case, because the **next** allocation the compile makes is a
  routed one (`arena.c` / `sb.c` → `ctx_nomem`) and it fails too.
- The single-shot rate measures *how much of a compile sits inside an
  absorbing path*. It does not measure *how often a real OOM is masked*.
  The sustained column is the number that measures the second thing, and it
  is **5 of 569 forced failures across all four witnesses (0.9%)**.

This is the strongest evidence in this memo, and it points at disposition
(3) far more than the filed entry does — with one residue named in §6.2.

---

## 2. MECHANISM ATTRIBUTION — every absorption assigned to a named path

### 2.1 How

`tests/core/alloc_inject.h`'s four macros now carry `__FILE__`/`__LINE__`
through to the injector, which reports the forced allocation's own call site
to the parent over the trial pipe (`--sites`). Text substitution rather than
`backtrace()`: on darwin, `backtrace_symbols` cannot name a `static`
function inside a statically linked archive, and every allocation site in
this tree is inside one.

### 2.2 Every absorbed trial, attributed

**148 absorptions across the four witnesses. All 148 have a named site.**

| mechanism | site | W1 | W3 | W4 | total | share |
|---|---|---:|---:|---:|---:|---:|
| **(A)** `emit_state_legend`'s silent degradation | `src/gen/emit_dfa.c:3615,3616,3617,3618,3660` | 15 | 25 | 0 | **40** | 27% |
| **(B)** the `[ART-SIZE]` ladder's blanket catch | `src/core/arena.c:14` (22), `src/core/sb.c:24` (86) | 0 | 0 | 108 | **108** | 73% |
| a stale `cx.size_cap_refused`/`cx.dfa_overflowed` | — | 0 | 0 | 0 | **0** | 0% |

**Mechanism (A) is the third path K60 suspected and could not name, and it
is the only one either of K60's own witnesses has.**
`emit_state_legend` allocates `dist`/`from`/`via`/`queue` (`:3615-3618`) and
`path` (`:3660`) with raw `malloc`, and on NULL `free`s what it has and
`return`s. Its own comment states the policy: *"Degrades SILENTLY on
allocation failure (F3, the review's own finding — a legend is never worth
failing a compile over, but the artifact then carries no comment saying one
was dropped)."* It never calls `ctx_nomem`, never `longjmp`s, and never
reaches `compile_driver`'s recovery point at all.

The counts are exactly `5 × (number of machines whose legend is emitted)`:
W1 emits three legends (forward, reverse, anchored) = 15; W3 emits five
(three on its first attempt, two on the `[K53-SELRETRY]` drop-rung retry
that has the anchored machine dropped) = 25. The measured N ranges say the
same thing — W3's absorbed indices are 160-164, 169-173, 176-180 (attempt 1)
and 312-316, 321-325 (the retry).

**Mechanism (B) is K60's ladder catch, and W4 is its first witness.** All
108 are `ctx_nomem`-routed allocations (`arena_alloc`'s and `sb_grow`'s own
`malloc`/`realloc`), so each one *is* a genuine `longjmp` arriving at
`compile.c:838` carrying a real OOM, and the `st_phase == ST_LADDER` branch
discards it as *"this K is out"* before any other test runs.

### 2.3 W4, and why it had to be added

K60 names the ladder as a mechanism, and **no witness in the tree could
reach it**: the ladder's own gate is `cx.job->fit.chosen == ENGM_VM &&
defo.unroll_k == 0 && (vm_rungs & 0x10) && emit_code > threshold`
(`compile.c:1605-1610`). W1 and W3 are DFA-engine artifacts and are excluded
by the first conjunct; W2 is orders of magnitude below the threshold. A
mechanism with no witness is a mechanism nobody is measuring, which is the
specific way this defect stayed unattributed.

W4 is **a real shipped-corpus pattern**, not a constructed one — found by
§3's corpus sweep as one of only two patterns that take more than one
internal attempt at default flags:

```
((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}
```

Seven internal attempts: the default, all five `SIZE_TERM_LADDER` rungs, and
the final re-emission. 15 ms to compile, 158 allocations — cheap enough for
the R0.4 tier budget.

### 2.4 The refutation of K60's "ONE CONFIRMED MECHANISM"

K60 states that `cx.size_cap_refused` *"is never reset to `false` anywhere
in the retry loop"* and therefore means *"has ANY attempt in this compile's
whole retry history ever been refused"*. **This is wrong, and three lines
of `compile.c` (`:704-706` at `272bf970`) say so:**

```c
for (volatile int attempt = 0; attempt < COMPILE_MAX_ATTEMPTS; attempt++) {
    Ctx cx;
    memset(&cx, 0, sizeof(cx));
```

The `Ctx` is a **loop-local**, zeroed at the top of every attempt. Both
flags are therefore per-attempt by construction — there is nothing to reset
because there is nothing that survives. What *does* cross attempts is
carried deliberately in the `volatile` outer scalars (`dfa_disabled`,
`collapse_reason`, `size_drop_rung`, `size_cap_bytes`, …), each seeded back
into the fresh `Ctx` at `:743-764` by name.

Three further facts close the door on the flag hypothesis:

1. All four flag-reading rungs (`size_eligible`, `drop_eligible`,
   `premul_eligible`, and `ovf_eligible`'s size sibling) require
   `cx.size_cap_refused`, which is written at exactly one site,
   `compile.c:1687`, **immediately before** the cap's own `ctx_fail`. An
   allocation failure arrives with it `false`.
2. `cx.dfa_overflowed` is written only in `src/ir/dfa.c` (`:940`, `:1007`,
   `:1022`), each time immediately before a `ctx_fail` on a mandatory
   machine.
3. For the one machine where it is *not* immediately fatal — the optional
   anchored one — `build_anchored_dfa` **saves and restores it around the
   build** (`compile.c:285`/`:298`), for precisely the reason K60 imagines
   is unhandled: its own comment says *"leaving it set would make a later,
   unrelated `ctx_fail` take [SEL-1]'s retry path for the wrong reason."*

**One narrow residual window survives that argument and is named here rather
than measured** (no witness was found, and constructing one needs an
optional-machine state-cap overflow, whose corpus population
`engabs_reach_probe.md` already records as zero): if a `ctx_nomem` escapes
`build_anchored_dfa` *after* `pcrec_build_dfa` has set `dfa_overflowed` for
the optional machine and *before* the restore at `:298`, the handler sees
`dfa_overflowed == true` on an OOM and `ovf_eligible` is true for the wrong
reason. This is a genuine instance of K60's *shape*, intra-attempt rather
than cross-attempt. The candidate in §4 closes it; so does a `longjmp`-safe
restore.

---

## 3. THE POPULATION

### 3.1 Method

`compile_driver` gained an attempt-counting trace under `PCREC_K60_PROBE=1`
(the `[K60-PROBE]` commit, dropped at merge). Every one of the **3,159
distinct `pattern` lines in the shipped `.rxt` corpus** was compiled with
`--features all`, once at default axes and once under `-e utf8`, and the
`[K60] attempt` lines counted. The `byteid`/`dialsweep` methodology, one
observable over.

### 3.2 The answer: the population is TWO patterns

| axis | patterns | take > 1 internal attempt | share |
|---|---:|---:|---:|
| default | 3,159 | **2** | **0.06%** |
| `-e utf8` | 3,159 | **17** | **0.54%** |

### 3.3 By rung

**Default axis (2 patterns):**

| attempts | rung that engaged | pattern |
|---:|---|---|
| 7 | `[ART-SIZE]` size-term ladder (5 rungs + final) | `((?:(?:(?:[^a]{1,2}\|[^a]??\|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}` |
| 2 | `[SEL-1]`/`[OPT-4]` rung 1, `CR_SEL1` (DFA overflow → count-collapsed prefilter) | `(1{0,30}?[^]abc][^abc]){28,30}0+\|a` |

**`-e utf8` axis (17 patterns):**

| count | attempts | rung that engaged |
|---:|---:|---|
| 11 | 2 | `[K53-SELRETRY]` rung 1, `SDR_NO_ANCHORED` (drop the optional anchored machine) — the `\p{...}`/`\P{...}` family |
| 3 | 2 | `[OPT-4]` size rung, `CR_SIZECAP` — all three end in a refusal (`rc=1`), the lookbehind-over-`\p{L}` family |
| 2 | 8 | `CR_SEL1` **then** the full size-term ladder |
| 1 | 7 | the size-term ladder alone (the default axis's W4, unchanged under utf8) |

### 3.4 Reading it

K60's reachable population — *"a pattern whose compile takes more than one
internal attempt"* — **is a handful, not thousands**, and the defect is
correspondingly far narrower than 15/72 and 25/328 suggest. Those two rates
were never rates over this population: they are rates over *allocation
indices within one compile*, and 40 of the 148 absorptions they contain
(all of W1's and W3's) turn out not to involve a retry attempt at all.

Note the asymmetry the two axes expose: the mechanism-(B) population (the
ladder) is **one pattern on either axis**, while the retry *rungs* other
than the ladder — which mechanism (B) does not run through — account for the
other 16. Widening the population sweep beyond the corpus's own axes
(`--tune`, `--unroll`, forced engines) is not done here; the corpus at
default and utf8 is what the three witnesses' claims are compared against.

---

## 4. THE CANDIDATE FIX — prototyped, measured, NOT LANDED

### 4.1 What was prototyped

The tree has exactly one `longjmp` (`compile.c:30`, always passing `1`) and
five `setjmp` sites, all of which test the value as a boolean. The value is
an unused signalling channel. The candidate gives `ctx_nomem` its own value
(`PCREC_JMP_NOMEM = 2`) and has the recovery point propagate a value-2
arrival immediately — ahead of every rung's eligibility test **and** ahead
of the ladder's blanket catch. **No stored state**: nothing to reset,
nothing to go stale, per-arrival by construction.

Behind two env gates (`PCREC_K60_PROBE` traces, `PCREC_K60_FIX` propagates),
committed separately as `[K60-PROBE]` for the manager to drop
(`dfam12_probe_m2.patch` / `[OPT5M2-PROBE]` precedent).

### 4.2 The measurement

Same four witnesses, same build, probe off vs `PCREC_K60_FIX=1`:

| witness | absorbed, fix OFF | absorbed, fix ON | eliminated |
|---|---:|---:|---|
| W1 (DFA) | 15 | **15** | **0 of 15** |
| W2 (VM cursor rung) | 0 | 0 | — |
| W3 (unicode-props/utf8) | 25 | **25** | **0 of 25** |
| W4 (size-term ladder) | 108 | **0** | **108 of 108** |
| **total** | **148** | **40** | **108 of 148 (73%)** |

With the fix on, every remaining absorption is at
`emit_dfa.c:3615-3618,3660` — mechanism (A), and nothing else.

### 4.3 The verdict: SOUND, and PARTIAL — and the partiality is structural

**It is complete for mechanism (B) and reaches mechanism (A) not at all,
and that is not a tuning gap that a better version of this candidate
closes.** `emit_state_legend` never calls `ctx_nomem` and never `longjmp`s;
there is no arrival at the recovery point to distinguish, so no property of
the `longjmp` value can change its outcome. Any disposition that addresses
only the recovery point leaves 27% of the measured absorptions exactly
where they are.

For the mechanism it does address it is clean:

- It covers **all three** `ctx_nomem`-routed sub-paths at once (the ladder
  catch, the flag-reading rungs, and §2.4's `build_anchored_dfa` window),
  because it sits above all of them.
- **The other four `setjmp` sites are unaffected**, confirmed two ways.
  By reading: `pcrec_count_groups` (`compile.c:1890`) and the three in
  `src/parse/syntax_dump.c` (`:760`, `:1038`, `:1557`) each spell
  `if (setjmp(cx.jb))` and take one action regardless of the value — a `2`
  is as true as a `1`. By running their surfaces: `--count-groups`,
  `--list-syntax` and the class/registry dumps all behave identically with
  the probe built in (`make strict` clean, `make -j4` clean, and the four
  witnesses read identically with the probe OFF — §4.5).

### 4.4 A constraint on any LANDED version

`if ((jmpval = setjmp(cx.jb)) != 0)` — what the probe uses — is **outside**
C11 7.13.1.1p2's list of permitted `setjmp` contexts, which allows only the
bare call as a controlling expression, a comparison against a constant
expression, or `!`. It works on every compiler this project targets; a probe
can afford that and a shipped recovery point should not. The
standards-clean spelling with the same property is:

> keep `if (setjmp(cx.jb))` and have `ctx_nomem` set a **`Ctx` field**
> (`cx.failed_nomem`) that the handler tests first.

That is a field, but it is **not the shape Frank rejected**: the `Ctx` is
`memset` at the top of every attempt (§2.4), so the field is per-arrival by
construction with no reset code, no lifetime to reason about, and no way to
go stale — which is precisely the property the rejected proposal's own
cross-attempt flag lacked, and precisely the property §2.4 shows
`size_cap_refused` already has.

### 4.5 Probe-off identity

- **Behaviour**: the four witnesses read 15/5, 0/0, 25/0, 108/0 with the
  probe built in and both gates unset — identical to the pre-probe build.
- **Emitted bytes, probe OFF**: corpus-wide byte-diff of the probe build
  against a `git archive` build of the branch point `272bf970`, over all
  **3,159** distinct corpus `pattern` lines, `-p rx` at default axes —
  **1,158 identical, 0 differing, 2,001 both-refuse (module-gated,
  unrelated), 0 rc-mismatch.**
- **Emitted bytes, probe ON** (`PCREC_K60_PROBE=1 PCREC_K60_FIX=1`): the
  same sweep. See §7 for its result; the gates change only what is written
  to stderr and what happens at a `PCREC_JMP_NOMEM` arrival, and no such
  arrival is reachable without the injector, so the expected result is the
  same 1,158/0.

  Both sides write **the same basename in different directories**. The
  first run of this sweep did not, and read `identical=0 differing=1158` —
  the `#include` line, this house's recorded `-o`-basename trap
  (`w23fix_report.md`), met for the fourth time. `identical=0` is not a
  plausible shape for a comment-only probe, which is what caught it.

---

## 5. CORRECTIONS OWED TO `docs/dev/known_issues.md` K60

The entry is honest about what it did not trace, and three of the things it
*did* assert are wrong. A future reader should not inherit them.

1. **"ONE CONFIRMED MECHANISM … `cx.size_cap_refused` … is never reset"** —
   refuted (§2.4). The `Ctx` is a loop-local `memset` per attempt. Zero of
   148 measured absorptions involve a stale flag. Disposition (1), which
   proposes resetting those flags, is therefore **a fix for a defect that
   does not exist**; the code already does what it would add.
2. **"W1's `[a-z]+` … this [the ladder catch] is the more likely
   explanation there"** — refuted (§2.2). The ladder cannot run for a
   DFA-engine artifact at all; W1's 15 absorptions are 15 of 15
   `emit_state_legend`.
3. **"whether a THIRD, distinct mechanism is also contributing"** —
   answered: yes, and it is the *only* mechanism in K60's own two
   witnesses. It is `emit_state_legend`'s documented silent degradation.

The entry's own framing — *"the size-term ladder's own documented catch-all
absorbs a genuine OOM"* — is **correct, and understated**: at 68.4% on its
first real witness it is the largest absorption rate this lane measured, and
K60 filed it as the *secondary* explanation of a witness that cannot reach
it.

---

## 6. RECOMMENDATION

The evidence settles two of K60's three dispositions and splits the defect
in two. It does not settle the whole thing, and §6.2 is the part that needs
Frank.

### 6.1 Mechanism (B), the ladder catch — 108 of 148: **take disposition (2)**

The measurement supports it without qualification: the candidate eliminates
**108 of 108**, covers all three `ctx_nomem`-routed sub-paths from one
place, needs no cross-attempt state, and leaves the other four `setjmp`
sites untouched. Land it with §4.4's standards-clean spelling.

**Disposition (1) is refuted** (§5 item 1) and should be struck from the
entry rather than left as an option.

Against landing it at all: the population is **two corpus patterns**
(§3.2), and under a *real* (sustained) allocator failure the ladder
absorption already collapses to 0 (§1.2). So this is a correctness tidy-up
at a recovery point, not a live hazard — a fair argument for deferring it,
and a fair argument that it is cheap enough to just do. The lane's own read
is that it is worth landing, because the absorbed event is a **masked
diagnostic on a library** (K7's rule, one layer up from `abort()`) and the
fix is four lines with a measured 108/108 result and no new state.

### 6.2 Mechanism (A), the legend — 40 of 148: **none of K60's three
dispositions fits, and this is Frank's call**

This is not a retry-ladder state defect. It is a deliberate, documented,
correct-by-intent policy (*"a legend is never worth failing a compile
over"*), and the lane agrees with the policy. What the measurement adds is
the cost the policy's own comment already admits and nobody has priced:

**a dropped legend makes the emitted artifact's bytes allocator-dependent,
with nothing in the artifact saying so.** Under D76/D94 the emitted comment
block *is* contract surface — an `abi` bump's whole ritual exists because
scaffolding bytes are pinned by identity gates — and this path can move
those bytes for a reason no gate can see, reproduce, or explain. §1.3's five
surviving W1 trials are exactly that case: a correct artifact, `rc == 0`,
silently missing a comment block, and no way for the caller to know.

Three ways out, cheapest first; the lane recommends the first:

- **(a) make it loud, not fatal.** Emit a one-line comment in place of the
  legend saying it was dropped for lack of memory. The artifact stays
  self-describing, the byte difference becomes explained rather than
  mysterious, and the policy is untouched. The code's own comment already
  names this as the missing half.
- **(b) route it through `ctx_nomem`.** Consistent with every other
  allocation in the tree, and it makes mechanism (A) vanish into mechanism
  (B)'s fix — at the cost of failing a compile over a comment, which is
  exactly what the F3 finding decided not to do.
- **(c) rule it acceptable as-is** — K60's disposition (3), correctly scoped
  to this mechanism only. Defensible: the population is a cosmetic comment
  under memory pressure. It should then be *stated* in `docs/spec/`, because
  today it is a byte-identity exception recorded only in one emitter comment.

### 6.3 Is any of this reachable without the injector?

**Mechanism (B): effectively no.** A real allocator that fails once fails
again; sustained mode is that regime, and W4 goes 108 → 0. A process whose
`malloc` genuinely returns NULL inside a ladder trial refuses the compile a
few allocations later, correctly diagnosed.

**Mechanism (A): yes, narrowly — and it is the only thing here that is.**
W1's five sustained survivors are the compile's final five allocations. A
real OOM there yields `rc == 0`, a correct artifact, and a missing comment,
with no instrument involved. That is the one outcome in this memo a user
could actually meet, and it is the one §6.2 is about.

---

## 7. OWED

- **§4.5's probe-ON byte-identity arm** was launched as this lane's last
  act per `BOILERPLATE.md`'s DO-THEN-FINISH; the lane's report
  (`lanes/k60meas_report.md` §5) carries its result or names it owed with
  the log path. The probe-OFF arm — the one that matters, since it is the
  claim the `[K60-PROBE]` commit makes about itself — is **complete**:
  1,158/0/2,001/0.
- **Not measured, deliberately**: §2.4's `build_anchored_dfa` window has no
  witness (the optional machine's state-cap overflow has a corpus population
  of zero — `engabs_reach_probe.md`), so its absorption is argued from the
  code and not from a run.
- **Not swept**: population axes beyond default and `-e utf8` (`--tune`,
  `--unroll=K`, forced engines). §3.4 says so rather than implying coverage.
