# Limits and give-ups — the resource-bound contract

This is the **spec**, not the design record, per `docs/spec/CLAUDE.md`'s
charter: it states what pcrec promises about the resource bounds an
emitted matcher enforces, and points at `docs/spec/match_api.md` and
`docs/design/` for the reasoning and measurement history rather than
repeating them. Every number below was verified against the shipped
surface (the constant it comes from, the emitted artifact, or a test
that pins it) at the commit this document was written, and the command
that produced each re-measurement is recorded so a reader can redo it.

## 1. Why a budget exists at all

pcrec is an ahead-of-time compiler a developer runs over patterns they
control; it is not a service that accepts untrusted regex from the
internet, and hardening the engine against a deliberately adversarial
pattern is explicitly **out of scope** (D22, `docs/dev/decisions.md`).
What the budgets below buy is narrower and unconditional: **a give-up
is never a false answer.** `docs/spec/match_api.md` §4 states the rule
this document assumes — every give-up code is a negative return
strictly below `-1`, distinct from both a match (`>= 0`) and a clean
no-match (`-1`), and `caps`/`caps_out` are left untouched on every one
of them. A caller that hits a bound gets an honest "I don't know",
never a wrong match or a wrong span. This document is where the
NUMBERS behind that contract live; §4 is where the CODE SPACE and its
propagation rules live, and this document does not restate them.

## 2. The four give-up codes

| Code | Value | Fires when |
|---|---|---|
| `PCREC_ERR_STEPS` | `-2` | the step budget (§3.1) is exhausted |
| `PCREC_ERR_FRAMES` | `-3` | the resume stack or its trail (§3.2) is exhausted — the code names the RESOURCE, not which of the two arrays ran out |
| `PCREC_ERR_WORK` | `-4` | the work budget (§3.1) is exhausted |
| `PCREC_ERR_RECURSE` | `-5`, shares `PCREC_ERR_FLOOR` | reserved; no producer in the default artifact today (D71 item 1) |

`PCREC_ERR_INTERNAL` (below `PCREC_ERR_FLOOR`) is a fifth constant in
the same emitted block and is **not** a give-up — it is the artifact
detecting its own analysis/emission inconsistency. It is out of this
document's scope; `docs/spec/match_api.md` §4 states what it means and
when it fires.

Full semantics — which entries can return which code, the "composed
call sites must trap below the floor" obligation, and why a DFA
artifact emits these constants without ever returning them — are
`docs/spec/match_api.md` §4. This document states the code space only
so the numbers below have somewhere to attach.

## 3. The numbers

### 3.1 Step and work budgets

- **Step budget default: 500,000,000** (D51, `docs/dev/decisions.md`).
  Compiled in as `VM_DEFAULT_STEP_BUDGET` (`src/gen/emit_vm.c:133`) and
  substituted whenever a caller leaves `pcrec_options.step_budget` at
  its sentinel, `PCREC_STEP_BUDGET_DEFAULT` (`lib/pcrec.h:301`) —
  `src/gen/emit_vm.c:7793`. The CLI overrides it per compile with
  `--step-budget=N` (`cli/main.c:56-58`, parsed at `cli/main.c:272-282`);
  `--fno-step-budget` emits no counter at all, for either budget
  (`cli/main.c:64-66`, `174`). At the measured ~50M steps/s, 500M steps
  bounds an honest refusal at roughly 10 s on a pathological input
  (D51) — this is a robustness bound, not a latency guarantee (D22).
- **Work budget default: 1,000,000,000** (D49, `docs/dev/decisions.md`).
  Compiled in as `VM_DEFAULT_WORK_BUDGET` (`src/gen/emit_vm.c:159`),
  substituted the same way at `src/gen/emit_vm.c:7803-7804` from the
  `PCREC_WORK_BUDGET_DEFAULT` sentinel (`lib/pcrec.h:317`). It is a
  SEPARATE counter from the step budget — one work unit per forward-only
  operation the fail label does not see (a frame discarded at a cut, a
  frameless scan iteration) — set by `--work-budget=N`
  (`cli/main.c:59-63`) and reachable only through the same
  `--fno-step-budget` gate (D49's ONE existence gate ruling). Both
  defaults land in `rx_info.step_budget`/`work_budget` (§6,
  `docs/spec/match_api.md`) as `-1` when disabled, a real count
  otherwise.

### 3.2 Frame and trail capacities (D73)

- **Resume-stack default: 2,048 frames. Trail default: 3,072 entries.**
  Compiled in as `VM_DEFAULT_RESUME_FRAMES`/`VM_DEFAULT_TRAIL_FRAMES`
  (`src/gen/emit_vm.c:87-88`), emitted per artifact as
  `<PREFIX>_RESUME_FRAMES`/`<PREFIX>_TRAIL_FRAMES` in the generated
  header (`docs/spec/match_api.md` §10.4) and mirrored on `rx_info` as
  `resume_frames`/`trail_frames` (same section) for a caller with no C
  header. `--backtrack-frames=N` (`cli/main.c:67-69`, parsed at
  `cli/main.c:295-303`) raises the compiled-in capacity per artifact,
  clamped at `VM_MAX_AUTO_RESUME_FRAMES`/`VM_MAX_AUTO_TRAIL_FRAMES`
  (`src/gen/emit_vm.c:100-101`) when left at auto-sizing. Both
  capacities are `0` on a DFA artifact, which has no resume stack to
  size (§10.4's "reserved but unreachable" shape) — a caller must check
  before dividing by either macro.
- **D73 kept these numbers where they were** rather than raising them:
  the run struct they size lives on the un-suffixed entries' own C
  stack frame (§4.4 below), and the caller-provided buffer (§4.3) is
  the ruled path around the ceiling, not a bigger default.
- **[OPT-1], 2026-08-25: the un-suffixed entries reach these capacities in
  TWO STEPS, and the numbers above are unchanged.** Where the stamped
  default does not fit inside one 4 KB page, `<prefix>_search`/`_match`/
  `_match_caps` run first on a small page-budgeted buffer
  (`<PREFIX>_FAST_FRAMES`/`<PREFIX>_FAST_TRAIL`, `match_api.md` §6.3(b))
  and escalate to the full stamped default on a `PCREC_ERR_FRAMES` give-up
  and on nothing else, re-running the match from scratch with both budgets
  refilled (§10.9). **The depth an artifact can reach, and every answer it
  gives, are identical** — the ceiling in this section is the deep tier's
  and is the only one a caller ever observes; a give-up still means the
  stamped default ran out, never the fast tier. `-fno-tiered-entry`
  (`tuning.md` §2.12) removes the tier. What changes is cost, not any
  number in this section: MEASURED on the RFC 5322 **email** specimen
  (16-byte matching subject, N=100k, median of 5, `taskset`, six
  repetitions) its entry went **213–268 → 45.6–48.8 ns/call** and its own
  stack frame **98,512 → 3,168 B**. (§5's 131,216 → 3,184 B is the
  `^(a(?1)?b)$` **recursion** specimen — a different artifact. The two
  specimens are never paired.)
- **[OPT-1] THE TIER IS A BET, AND WHAT IT COSTS WHEN IT LOSES IS A LIMIT
  WORTH STATING HERE.** The wasted fast attempt is bounded by the STEP and
  WORK budgets above, **not** by the fast frame count — sixty frames of
  depth absorb an unbounded amount of backtracking. So an escalating call
  can spend up to **twice** §3.1's step budget of real work before it
  answers, since §10.9 refills both budgets for the deep attempt. And the
  transition is a CLIFF rather than a ramp: MEASURED on `((a)|(aa))+b`
  (tiered vs `-fno-tiered-entry`, N=20k, median of 5), 18.5 vs 207.1 ns at
  n=1 (11× faster) … 186.4 vs 365.3 at n=23 … **568.9 vs 372.9 at n=24**, a
  3.05× jump across one byte, and 1.24–1.53× slower than the single-tier
  entry at every depth above it. **That boundary is a 25-byte subject** (24 `a`s and a `b`) —
  depth is a property of the backtracking, not of the input length. A
  workload measured to sit above its patterns' boundaries should use `_in`
  or `-fno-tiered-entry`. How often real workloads escalate is the open
  measurement `[ENG-PGO]` names.

### 3.3 Compile-time budgets: two different things named "limit"

Two unrelated bounds both get called a "limit" and this document keeps
them apart. **What pcrec PROMISES** is a set of hard state-count
ceilings in `src/core/limits.h` — `PCREC_MAX_NFA_STATES` (131,072,
`src/ir/nfa.c:110-111`), `PCREC_MAX_VM_NODES` (131,072), and their
siblings for DFA states, table entries and subset construction. Cross
any of them and compilation FAILS cleanly, naming the ceiling
(`src/ir/nfa.c:111`'s message is representative) — never a hang, an
OOM, or a silent truncation. These are a CONTRACT: pcrec commits to
rejecting rather than mis-serving an over-large pattern.

**[SEL-1] (2026-08-28) exception, scoped to the THREE DFA-side siblings
alone** (`PCREC_MAX_DFA_STATES_TABLE`/`_GOTO`, `PCREC_MAX_TABLE_ENTRIES`,
`PCREC_MAX_SUBSET_ELEMS` — never `PCREC_MAX_NFA_STATES` or
`PCREC_MAX_VM_NODES`, which have no fallback engine to hand the pattern to).
Under `--engine=auto`, crossing one of these still FAILS the DFA build
exactly as described — same diagnostic, same cost — but the COMPILE no
longer necessarily fails with it: the overflow is a selection outcome (fall
back to the VM; drop an auto-selected prefilter) rather than a refusal, so a
pattern that used to be rejected outright on one of these three ceilings may
now succeed at the VM engine instead. `--engine=dfa` and `-fprefilter` keep
the contract as stated, unconditionally — see `docs/spec/tuning.md` §2.11
for the mechanism and the cost bound this exception is held to.

**[ENG-ABS] (2026-08-29) A SECOND, NARROWER EXCEPTION on the same three
ceilings, and it is not an engine fallback at all.** A DFA artifact carries an
OPTIONAL third machine — the anchored match-here automaton behind
`<PREFIX>_DFA_MATCH "unwrapped"` (`docs/spec/tuning.md` §2.15). It is charged
against the same three ceilings, it is built AFTER the two machines the engine
needs so it can never take budget from them, and crossing a ceiling there
produces **no diagnostic and no fallback engine**: the artifact simply keeps
the search-and-filter form of its anchored entry and stamps that. The set of
patterns pcrec ACCEPTS is unchanged by this machine in either direction —
which is why it adds no ceiling of its own to the list above, and why the
paragraph it follows still describes every way a state-count ceiling can
refuse a pattern.

**[OPT-4] (2026-08-29, as re-ruled) THE PREFILTER-LANGUAGE RETRY, AND IT IS NOT
AN EXCEPTION TO ANY CEILING — it is what happens AFTER one fires.** An earlier
design put a state BUDGET here (`PCREC_PREFILTER_EXACT_NFA_STATES`, 128) that
chose the count-collapsed prefilter by measuring the pattern; Frank reversed it
on a corpus regression and the constant is deleted
(`docs/design/prefilter_count_independence.md` §10a).

What remains is a RETRY, in `compile_driver`'s existing attempt ladder. When
§8's emitted-size caps refuse an artifact, pcrec makes ONE more attempt with
the VM hybrid's prefilter built from the count-collapsed lowering
(`docs/spec/tuning.md` §2.17) — a sound superset whose machine does not scale
with a bounded repeat's count — and refuses only if that is over the caps too.
The [SEL-1] rung above it does the same thing for a DFA STATE cap, where the
alternative is no prefilter at all rather than a refusal.

**THIS IS THE ONE PLACE A CAP IN THIS DOCUMENT IS NOT THE LAST WORD**, and the
contract is still exactly as stated: nothing is emitted past a cap, and a
pattern is refused unless some attempt produces an artifact under it. The retry
adds attempts, never headroom. MEASURED: K41's second fuzz-gate witness is
refused at 670,952 code bytes under the exact language and ships at 152,259
through the retry, stamping
`RX_VM_PREFILTER_LANG_WHY "size cap retry, exact 670952 > 500000"`.

`-fno-prefilter-collapse` denies both rungs, so a caller who would rather be
refused than handed a superset prefilter can be. The retry never applies where
the DFA is the ENGINE, where the language must be exact.

**[OPT-4.1] (2026-08-30) AND IT DOES NOT APPLY WHERE THE COLLAPSED LANGUAGE IS
NULLABLE**, which is the one case where the retry ships NO prefilter rather
than a smaller one. A collapsed language that matches the empty string matches
at every position, so the filter can never dismiss one; the retry then builds
nothing, and the artifact — smaller still than the collapsed one — is what
ships. **The contract above is unchanged in the direction that matters: no
pattern that compiles today stops compiling**, because dropping the prefilter
is strictly smaller than collapsing it, so the size rung still rescues the
compile. On the [SEL-1] rung the same decline leaves the pre-[OPT-4] artifact
and `<PREFIX>_ENGINE_SEL` reads `"declined-nullable"`. `docs/spec/tuning.md`
§2.17 carries the rule, the stamps and the flag interactions (`-fprefilter`
overrides the decline; `-fprefilter-collapse` does not).

**What pcrec does NOT promise is a bound on wall-clock compile TIME**
for a pattern it accepts. D45 (`docs/dev/decisions.md`) is a TEST
HARNESS policy, not a caller-facing contract: every compile of
GENERATED C that pcrec's own test infrastructure performs runs under a
CPU-primary timeout (`GENCPU` 10s plain / 60s under sanitizers, backed
by a looser wall-clock `GENTIMEOUT`) so a runaway compile fails the
test loudly instead of hanging a battery — a guard on the SUITE, whose
own load-sensitivity is a separate open row (`[TT-10]`,
`docs/dev/plan.md`), not a caller promise. A caller compiling
`build/pcrec`'s own C output with their own toolchain gets the
state-count ceilings above and nothing else.

### 3.4 The buffer sizing surface

Beyond the four numbers above, a caller sizing a caller-provided buffer
(§4.3) reads five macros and four `rx_info` fields — `docs/spec/match_api.md`
§10.4 states the arithmetic in full, including the "stamped size 0 means
this engine takes no buffers, check before you divide" rule. This
document does not repeat it.

## 4. Worked example: `^(a(?1)?b)$`, re-measured

This is D73's own example, re-measured against this worktree's build
rather than carried forward from the ruling.

**Command** (from a clean build):

```
build/pcrec -p rx --features all --emit-main -o rec.c '^(a(?1)?b)$'
cc -O2 -o rec rec.c
./rec "$(python3 -c "import sys;n=342;sys.stdout.write('a'*n+'b'*n)")"   # 684-byte subject
./rec "$(python3 -c "import sys;n=343;sys.stdout.write('a'*n+'b'*n)")"   # 686-byte subject
```

**Result, n = 340..344** (subject is `n` `a`s followed by `n` `b`s, so
length `2n`):

| n | subject length | result |
|---|---|---|
| 340 | 680 | `match 0 680` |
| 341 | 682 | `match 0 682` |
| 342 | **684** | `match 0 684` |
| 343 | **686** | `frames` (`PCREC_ERR_FRAMES`) |
| 344 | 688 | `frames` |

This MATCHES the numbers already carried in `docs/spec/match_api.md`
§10.1 exactly: matches up to a 684-byte subject, gives up at 686. No
discrepancy found on re-measurement.

**Why the trail binds first, not the frames.** The resume stack and its
trail are sized identically per the stamped defaults (2,048 / 3,072),
but they do not fill at the same rate: this pattern's recursion costs
roughly 2 resume frames and 9 trail entries per nesting level
(`docs/design/frame_buffer_design.md` §4), so the 3,072-entry trail is
the array that empties first, with roughly two thirds of the 2,048-frame
resume stack still unused at the give-up. §2's `PCREC_ERR_FRAMES` code
is returned either way — it names the resource class, not which of the
two arrays ran out (§2 above, `docs/spec/match_api.md` §4).

## 5. K33: the default entries and the C stack

**The run struct that backs `<prefix>_search`/`_match`/`_match_caps` is
sized by the compiled-in capacities of §3.2, and WHICH FRAME IT LIVES ON
CHANGED AT `[OPT-1]` (2026-08-25).** It used to be a local of the entry
itself. It is now a local of a non-inlined internal function the entry
calls **only on a `PCREC_ERR_FRAMES` give-up** (`docs/spec/match_api.md`
§10.9, the two-tier entry); the entry itself runs on a page-sized buffer.
So there are now TWO numbers, and they answer different questions.
Re-measured with `gcc -O2 -fstack-usage` on a fresh `-p rx --engine=vm
--features recursion` build of `^(a(?1)?b)$` (`make test-stackdepth`,
which runs this exact build and prints both every run):

```
$ make test-stackdepth
PASS: [TS-4] the cause is stated: the call-bearing artifact's DEEP PATH is
134400 B against a 131072 B thread stack (over by 3328 B), while the
call-free control's is 101616 B and fits
PASS: [TS-4/OPT-1] the call-bearing entry's OWN frame is 3184 B, inside one
4096 B page
```

- **The entry's own frame is 3,184 bytes** — under one 4 KB page, which
  is the point of the tier (gcc's stack-clash protection probes per page
  of a frame on every call).
- **The DEEP PATH is 134,400 bytes** — the entry's frame plus the
  internal function's 131,216, which is what a call that escalates
  actually needs. That is the quantity K33 is about, and it exceeds a
  musl-default **128 KB (131,072-byte)** thread stack by 3,328 bytes.
  (131,216 is the LINKED-call figure — a spliced call does not widen the
  frame, `docs/spec/match_api.md` §10.2 — and is the number §5.3 and
  §10.1 carry.)

**SO THE DEFAULT ENTRIES NOW FIT A 128 KB THREAD FOR EVERY MATCH THE FAST
TIER HOLDS, and fault only on a subject deep enough to escalate.** This
document previously said they "SIGSEGV on such a thread even on a subject
well inside the 684-byte matching ceiling above", and that sentence is
now FALSE: `make test-stackdepth`'s arm D matches a 2-byte subject
through `<prefix>_search` on exactly that thread. `docs/dev/known_issues.md`
K33 is accordingly **OPEN, NARROWED** rather than open in full — still open
because which subjects escalate is a property of the pattern and the
subject, so a caller cannot bound it in advance, and because the deep
tier's storage still has no other legal home (a `static` fails the
concurrency contract, a thread-local fails reentrancy, allocation is
forbidden by construction). `[OPT-1]` changed WHEN that storage is
reached, not how big it is. glibc's 8 MB default thread stack is
unaffected either way.

**Note:** `docs/dev/known_issues.md`'s K33 "Cause" paragraph read
131,296 B when this document was written and was CORRECTED to 131,216 by
`[SPEC-1.1]`; **D73's context paragraph in `docs/dev/decisions.md` still
reads 131,296 B** — 80 bytes above the number re-measured here and above
the one that document's own neighbours use. Flagged rather than silently
matched; fixing `decisions.md` is outside this document's own change.

**The remedy for the deep case is still the caller-provided buffer.**
`docs/spec/match_api.md` §10 states the `_in` entries' contract in full —
`<prefix>_search_in`'s own frame is 144 bytes (re-measured in the same run
above, unchanged by `[OPT-1]`: an entry handed the caller's storage never
had a tier to gain), and the same 684-byte subject that still kills the
default entry on a 128 KB thread matches through `_search_in` on that same
thread. It remains the only way to get a GUARANTEE, as opposed to the
tier's very good odds. This document adds no
detail beyond pointing there; the one thing worth restating at THIS
tier is the shape of the fix — a caller on a small-stack thread (musl's
128 KB default is the measured, named case) supplies its own frame and
trail storage instead of using the compiled-in default.

## 6. K34 / D74: a documented divergence, not a bug

On some same-position LEFT recursions — `(a|(?1)a)b` on `"a"` is the
measured case — pcrec gives up with `PCREC_ERR_FRAMES` where libpcre2
10.46 concludes with a clean no-match. This is not a wrong answer under
D26's tier rule (a give-up asserts nothing about the language), and it
is not the general "same position re-entry is always wrong" rule either
— PCRE2's own guard is five conjuncts wide (D74), which is why a
199-deep same-position recursion can still match in both engines.

**Ruled (D74, `docs/dev/decisions.md`): pcrec does NOT adopt PCRE2's
recursion-loop guard.** Reproducing it faithfully needs a stored
subject pointer per active recursion frame plus a `last_used_ptr`
high-water mark threaded through every fail-and-return site of the
emitted VM — new state on the hottest path of the whole emitter, to
reproduce one engine's implementation artefact (which PCRE2 itself
ships a flag to disable) — in exchange for flipping a small, parked
cell class from "gives up" to "wrong kind of gives up avoided" while
creating the INVERSE divergence's mirror image (`((?1)?a)` on `"a"`
already matches here where PCRE2 returns its own error there). The
give-up **stays** pcrec's documented answer for this shape.

**The caller-facing fact this document exists to state:** unlike
PCRE2's `-52`, which has no caller-visible knob besides disabling the
check outright, **pcrec's give-up here is bounded by the same frame
budget as every other recursive pattern** (§3.2/§4 above) — a caller
who needs this class to conclude rather than give up has the same lever
as any other deep-recursion case, the `_in` entries with a larger
buffer (§5).

## 7. What is not limited today

Being honest about the edge of this document's coverage:

- **DFA state count and NFA state count are bounded (§3.3), and since
  [ART-SIZE] the EMITTED SIZE is too (§8) — but compile TIME for an
  accepted pattern is still not.** D45's compile-timeout remains a
  test-harness policy, and its own load-sensitivity is an open,
  unrelated tracking row (`[TT-10]`, `docs/dev/plan.md`), not a number
  this document can cite as a contract. What §8's code-bytes cap gives
  is a bound on the QUANTITY that predicts compile time within one
  mechanism, not a bound on the time itself: the two K41 fuzz witnesses
  invert the ordering (670,650 code bytes at 66.92 s against 1,718,425
  at 55.13 s), so no emitted count the compiler can produce is a
  compile-time oracle.
- **The size term can change a tuned caller's BUDGET verdict.** Choosing
  a different unroll `K` for the same pattern moves the give-up surface
  even though it cannot move a match result: measured on
  `((a)|ab){12}c`, the minimum `--step-budget` that completes runs 89 at
  K=1 to 110 at K=8, the minimum `--backtrack-frames` is 39 at K=1
  against 28 at K=8 (descending `K` RAISES the frame requirement), and
  `<PREFIX>_TRAIL_FRAMES` — a macro §5 names as caller-read — runs 62
  down to 51. Under the DEFAULT budgets the answers are identical; a
  caller who has tuned a budget to the edge should re-check it after an
  emitter change that moves `K`, and `<PREFIX>_UNROLL_K` on the artifact
  is how they see which `K` they got.
- **The step and work budgets are two counters, not one exhaustive
  accounting of "engine effort".** They cover backtrack resumptions and
  forward-only work respectively (§3.1); no single number bounds total
  wall-clock match time, and D22 is explicit that this project does not
  aim for one — a give-up being honest is the guarantee, not a latency
  ceiling.
- **`PCREC_ERR_RECURSE` is reserved but has no producer** in the default
  artifact (§2) — there is no recursion-depth COUNTER shipping today, so
  no number exists to state for it; D71 item 1 names this as a future
  `[V-H]` diagnostic-generation axis, not a gap in this document.

---

## 8. Emitted artifact size ([ART-SIZE], D84)

pcrec bounds how large an artifact it will emit. Two limits, both in
**bytes of emitted C source with comments excluded** — the `.o` you
link is roughly **17 %** of that, so the numbers are quoted both ways:

| limit | default | ≈ `.o` | what it bounds |
|---|---|---|---|
| `PCREC_MAX_VM_EMIT_CODE_BYTES` | 500,000 | ≈ 85 KB | bytes OUTSIDE table initializers — the part gcc must compile as control flow |
| `PCREC_MAX_EMIT_BYTES` | 1,000,000 | ≈ 170 KB | the whole artifact |

**Why two.** The size you ship and the cost gcc pays are different
quantities. Measured: a data-table entry costs gcc 0.905 µs, a
computed-goto jump-table entry 8.7 µs, and a VM node 5.37 ms — a node
is ≈ 5,930× a table entry. So `a{1,31000}` emits 1,367,865 bytes that
gcc compiles in **0.34 s** (cheap to compile, too large to ship: the
total limit refuses it, the code limit does not), while a deeply nested
bounded repeat can emit 670,650 bytes of code that costs gcc **66.92 s**
(both refuse it). One limit would have to get one of those two answers
wrong.

**They are EMERGENCY FAILSAFES, not tuned thresholds** (D84 addendum 3).
Nothing in pcrec's own 2,487-pattern corpus comes near either — the
worst is 283,083 code bytes and 651,415 total, on every optimization
axis — and both are checked AFTER emission and BEFORE anything is
written, so an over-limit compile produces a refusal and no file.

**Neither is deniable, both are overridable UPWARD.**
`-fno-size-term` denies the unroll-ladder SELECTION and never reaches a
limit: a safety refusal a flag turns off is not one. To accept a larger
artifact, raise the limit — `--max-emit-code-bytes=N` /
`--max-emit-bytes=N`, raise-only (a value below the default is refused,
so these can never be used to make a build fail that would have
succeeded). The effective TOTAL cap is stamped on every artifact as
`<PREFIX>_MAX_EMIT_BYTES` (it applies to both engines); the CODE cap,
`<PREFIX>_MAX_EMIT_CODE_BYTES`, is stamped ONLY on a VM artifact — a
pure-DFA artifact has no counter rung and so no code/table split to
bound separately (verified live: `tests/codegen/run_size_term.sh`'s own
"the VM-only size stamps are ABSENT on a DFA artifact" check).

### `--warn-emit-bytes=N` — an ADVISORY warning, never a refusal

**[OPT-4] (2026-08-29).** When an ACCEPTED artifact's total emitted bytes
exceed `N`, pcrec writes ONE line to stderr and then returns the artifact.
It never refuses, never changes what is emitted, and is not a tuning axis:
nothing selects on it and no artifact records it.

```
pcrec: warning: large artifact: 883632 bytes of emitted C source (11418 of
code), over --warn-emit-bytes=250000. Unroll factor K=8 (default); prefilter
language n/a (no VM prefilter). See docs/spec/tuning.md for the levers, or
raise/disable the warning with --warn-emit-bytes.
```

The line names the two stamps that EXPLAIN the size — the unroll factor with
`_UNROLL_K_WHY`'s reason, and the prefilter language — rather than only the
number, because a reader told "883,632 bytes" can only shrug while one told
which lever moved it knows what to reach for.

**Default `250000` total bytes; `0` disables it.** The default is an order of
magnitude under `--max-emit-bytes` on purpose: a warning's value is arriving
while the pattern can still be changed, not at the moment it is refused.

**IT IS THE ONE SIZE OPTION THAT IS NOT RAISE-ONLY, and the asymmetry is the
point.** The two caps above are raise-only so that no caller can manufacture
someone else's refusal. A warning carries no such authority — the build
succeeds either way — so LOWERING it is exactly what a project wanting earlier
notice should do, and lowering it cannot fail anyone's build. It is
`pcrec_options.warn_emit_bytes` for a library caller, and it is **off** for one
who `memset`s the struct rather than calling `pcrec_default_options`: an
embedder has not asked pcrec to write to stderr.

### Handling an oversized artifact

pcrec REFUSES rather than emitting past either limit, and nothing is
written when it refuses.

**This can affect a pattern that compiled before.** These limits landed
with `abi` 11; a pattern that emitted more than 1,000,000 bytes at
`abi` <= 10 compiled then and refuses now. Three shapes in pcrec's own
resource suite are in that class — `a{0,25000}` (1,103,367 bytes),
`[a-z]{0,30000}` (1,323,371) and `(a|b){0,30000}` (1,333,109) — and all
three are TABLE-dominated, so `--unroll` will not shrink them: raise the
cap or reduce the count. That is the deliberate trade (D84: "I'd rather
it FAIL and document how to handle oversized results"), not an
unintended narrowing.

Your options, in the order most callers want them:

0. **Notice it earlier** — `--warn-emit-bytes=N` (above) fires on an
   artifact that still compiles, so the choices below can be made before a
   refusal forces them.
1. **Raise the limit** — `--max-emit-bytes=N` or
   `--max-emit-code-bytes=N` if the size is acceptable to you. **For a
   real build, put the override in the pattern-source file's `config`
   block rather than on the command line**: it then applies per target,
   beside the pattern, to everything built with that config, and it is
   visible to whoever reads the file next. The CLI flags are for
   one-off compiles and for the test harness.

   **The state of that instruction, stated exactly.** It shipped as a
   forward reference — the sentence above named a mechanism that did not
   exist. The `config` block now EXISTS in the `.rxt` format
   (`docs/spec/rxt_format.md`, "The head") and pcrec parses it, including
   the `pcrec <raw flags>` line these two overrides would ride. What is
   NOT yet built is the path that COMPILES from a pattern-source file at
   all — `--source` and `--target` — so today the instruction describes
   where the override BELONGS rather than something a caller can run.
   Until that lands, the CLI flags are the only way to raise either cap,
   and this note is here so a caller reaching this page is told which of
   the two it is instead of discovering it at the command line.
2. **Let the size term choose `K`, or force it.** `--unroll=1` emits one
   body copy per counter-rung iteration and is the largest single size
   lever for a replication-dominated pattern — measured 17× on the fuzz
   gate's own witness. It costs 1–3 % throughput on single-level large
   counts. It does NOT shrink a table- or prefilter-dominated artifact.
3. **Change the engine or the output** where the pattern admits it.
   `--no-captures` and `--engine=dfa` remove the VM body;
   `--engine=vm` removes the hybrid DFA prefilter, which is most of the
   size when the stamps say the artifact is table-dominated — at a large
   cost on non-matching subjects.
4. **Split or rewrite the pattern.** Repetition counts MULTIPLY through
   nesting, so lowering one count INSIDE a nest is worth far more than
   lowering an outer one.
5. **Read the stamps to see which term produced the bytes.**
   `<PREFIX>_UNROLL_K` and `<PREFIX>_UNROLL_K_WHY` (`default` /
   `option` / `denied` / `size-model` / `size-model-declined` /
   `cap-rescue` / `capacity-declined`) plus `<PREFIX>_VM_RUNGS` for node
   replication;
   `<PREFIX>_DFA_TABLE` and `<PREFIX>_VM_PREFILTER` for the prefilter
   and its tables. A table-dominated artifact does not shrink with
   `--unroll`, and option 2 will not help it.

## 8a. `--unroll=K` and the depth an artifact reaches

`K` is answer-identical in the LANGUAGE — an artifact built at any `K`
accepts exactly the same strings, reports the same span and fills the same
capture slots — and it is NOT answer-identical in the DEPTH an artifact
reaches under the default capacities. A smaller `K` raises the per-iteration
frame need, so the same `<PREFIX>_BT_FRAMES` carries a shorter subject
before `PCREC_ERR_FRAMES`.

The artifact says so itself. `rx_info`'s `.subject_ceiling` is the declared
bound (§7's honest-ceiling rule) and it MOVES with `K`:

| pattern | `--unroll=8` | `--unroll=1` |
|---|---|---|
| `^(a(?1)?b)$` | `subject_ceiling` 512 | **341** |
| `((?1)?a)` | 512 | **341** |
| `(((?:a{0,2}b)+c){0,20}d){0,20}e` | 43 | **23** |

MEASURED consequence, and it is a real one: on a 684-byte subject, the five
cells in `tests/recursion/framebuffer.rxt` and `tests/recursion/d27/
sr_depth.rxt` that MATCH at the default `K` return a frames give-up under
`--unroll=1`, with the DEFAULT budgets.

**Two rules follow, and they point in opposite directions on purpose:**

1. **An explicit `--unroll=K` MAY lower the depth this artifact reaches.**
   That is the caller's own choice, it is visible in the stamped
   `.subject_ceiling` before a single subject is run, and the remedies are
   the ordinary ones — raise `frame_capacity` through the options, or use
   `<PREFIX>_search_in` with a caller-supplied buffer (§7).
2. **The size term NEVER lowers it.** A `K` the compiler chooses for you is
   held to a floor: a rung whose artifact would declare LESS capacity than
   the default `K`'s — on `.frame_capacity` or on `.subject_ceiling` — is not
   a candidate, in the ordinary selection or in a cap rescue. When the `K`
   the term wanted is the one the floor removes, the term declines and stamps
   `<PREFIX>_UNROLL_K_WHY "capacity-declined"`. A compiler-chosen `K` that
   turns a match into a give-up would be an answer change no flag asked for,
   and §8's "refuse and document" does not cover it.
