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

- **DFA state count and NFA state count are bounded (§3.3), but
  compile TIME for an accepted pattern is not** — see §3.3 above; D45's
  compile-timeout is a test-harness policy, and its own
  load-sensitivity is an open, unrelated tracking row (`[TT-10]`,
  `docs/dev/plan.md`), not a number this document can cite as a
  contract.
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
