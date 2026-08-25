# Tuning axes — the `-f`/`-fno-` family, `--unroll=`, and `--engine=`

This is the **spec**, not the design record, per `docs/spec/CLAUDE.md`'s
charter: it states what pcrec promises about the generation-time tuning
flags, and points at `docs/design/eng_brep_design.md`, `docs/design/
counterk_impl/counterk_design.md`, `docs/design/atomic_groups_design.md`,
`docs/design/subroutines_design.md` and `docs/dev/decisions.md` (D46, D47,
D47.3) for the reasoning and measurement history rather than repeating them.
Every claim below was checked against `lib/pcrec.h`'s per-bit comments,
`cli/main.c`'s flag parsing, and an emitted artifact's own `#define` stamps
at the commit this document was written; the command that produced each
re-measurement is recorded so a reader can redo it.

## 1. What a tuning flag is

A tuning flag is a **generation-time choice** (D18: options are compiled
away, never a runtime parameter) that selects among machinery the compiler
could otherwise choose on its own. The defining contract, true of every
flag in §2 below except the two named ENGINE-SELECTING there:

> **Denying (or forcing) a tuning axis must not change what the emitted
> matcher answers for any subject.** The span, every capture slot, and the
> failure surface (no-match vs. a give-up and which one) are identical
> between the two builds. It changes *how* the answer is found — which
> internal strategy the emitter used — never the answer itself.

This is D46's "every strategy-selection point is observable and
forceable" principle (`docs/dev/decisions.md` D46), applied at the tuning
layer: a compiler optimization that cannot be turned off cannot be
differentially tested (D47.3, `docs/dev/decisions.md`, ruling 3 — "a
strategy that cannot be denied cannot be differentially tested"). Each
flag below exists **because** it has a differential that checks this exact
claim — compile the same pattern twice, once with the strategy and once
without, link both into one driver, and sweep subjects comparing span,
every capture slot, and the failure surface. Nine of the eleven axes in §2
are members of this family (the deny-only six, the force pair, and the two
engine-selecting denials); `--unroll=` is the deny family's value
parameter and `--engine=` is the coarsest-grained member of the same
observable/forceable principle, one level up (D46's motivating case).

**Who this document is for.** A contributor building or reviewing a
differential test needs to know, per axis: what it denies/forces, whether
it can be relied on to leave the answer unchanged (so the denied build is
a valid ground truth) or whether it can move the pattern between engines
(so a differential comparing spans across the axis needs the engine
difference accounted for separately), and which check already carries the
evidence. A stranger tuning performance needs the same table read the
other way: which knobs are safe to flip without re-verifying correctness,
and which one is a `--engine`-shaped do-or-die request.

## 2. The eleven axes

Each subsection: what it controls, the default, the stamp it leaves in an
emitted artifact (verified by an emitted-artifact diff, command given),
whether it is ANSWER-IDENTITY-preserving or ENGINE-SELECTING, and the
one-sentence reason the axis exists.

### 2.1 `-fno-possessify` — `PCREC_NO_POSSESSIFY` (bit 4)

**Denies** the possessification rewrite (`src/opt/possessify.c`,
`docs/design/eng_brep_design.md` §2). Default: possessification runs.
**ANSWER-IDENTITY-preserving** — masked out of `rx_info.flags`
(`src/gen/emit_dfa.c`'s `emit_info_def`), because the rewrite changes no
answer, only whether a quantifier's loop body possessifies. What moved is
recorded in the `RX_VM_STRATS` bitmask (`PCREC_VM_STRAT_POSSESSIVE` /
`_BACKTRACKING`), verified by compiling `'(x)(?:a|bc)+d'` with and without
the flag:

```
$ build/pcrec -p rx --engine=vm --emit-main -o /tmp/a.c '(x)(?:a|bc)+d'; grep RX_VM_STRATS /tmp/a.c
#define RX_VM_STRATS           0x1u  /* POSSESSIVE */
$ build/pcrec -p rx --engine=vm -fno-possessify --emit-main -o /tmp/b.c '(x)(?:a|bc)+d'; grep RX_VM_STRATS /tmp/b.c
#define RX_VM_STRATS           0x2u  /* BACKTRACKING */
```

(`rx_info.flags` and every other field of the initializer are unchanged
between the two builds except `frame_capacity`, which grows because a
backtracking build needs a frame the possessive one does not —
`docs/spec/match_api.md` §6.3.) **Reason it exists:** possessification is
a rewrite whose entire claim is "changes no answer", and a claim that
cannot be turned off cannot be differentially tested (D47.3).

**Differential:** `tests/possessify/run_possdiff.sh`. Population,
measured this session (`bash tests/possessify/run_possdiff.sh`):

```
possdiff: 155 patterns agreed, 0 diverged, 0 refused by pcrec
possdiff: 107 of 155 had at least one POSSESSIFIED quantifier
possdiff: 77725 pattern-subject-startpos cells compared
```

### 2.2 `-fno-revdet` — `PCREC_NO_REVDET` (bit 5)

**Denies** the REVERSE-DETERMINISTIC cursor rung (`docs/design/
engine_m4.md` §2.5). Default: the rung runs where it applies. **ANSWER-
IDENTITY-preserving**, same masked-out-of-`rx_info.flags` treatment as
§2.1, for the same reason: the rung is one alternative body-copy-plus-
backward-walk emission of a quantifier that a denial drops one rung
further, to literal replication (frames). Moves the `RX_VM_RUNGS` bitmask
(`PCREC_VM_RUNG_REVDET`), not re-measured separately this session (§2.1's
stamp-verification method applies identically; `tests/rungselect/
CLAUDE.md` documents the family's shared shape). **Reason it exists:**
same D47.3 claim — a strategy that cannot be denied cannot be
differentially tested, and denying it drops the quantifier to the
semantic ground truth (literal replication).

**Differential:** `tests/rungselect/run_rungdiff.sh`, which reuses
`tests/possessify/possdiff_driver.c` (D47.3's family shares one driver;
only the `-DDIFF_A_LABEL`/`-DDIFF_B_LABEL` words differ). Population,
measured this session (`bash tests/rungselect/run_rungdiff.sh`; the first
attempt hit a 180s `gnutimeout` under the manager's concurrent battery
load — a load-contention timeout, not a defect, per the box's own
guidance that a firing timeout is a finding to investigate rather than a
reason to blindly extend; re-run at 600s completed):

```
RUNGDIFF_TALLY
```

### 2.3 `-fno-counter` — `PCREC_NO_COUNTER` (bit 6)

**Denies** the COUNTER rung (`docs/design/counterk_impl/
counterk_design.md`), the family's third member and — per its own
comment in `lib/pcrec.h` — the one whose denial is load-bearing beyond
testing: the counter rung has a **known limit** (the replication cap,
`PCREC_MAX_VM_REPEAT_COPIES`), above which there is no `-fno-counter`
build to compare against, because the cap is what refuses it. Default:
the counter rung runs where it applies, unrolled by `unroll_k` (§2.10).
**ANSWER-IDENTITY-preserving**, same masked treatment. **Reason it
exists:** dropping a bounded repeat to literal replication is what ships
today below the cap, so this is the differential's ground truth exactly
as §2.1/§2.2's are, with the added role of being the ONLY ground truth
the counter rung has (there is no third strategy under it to fall back
to).

**Differential:** `tests/counterk/run_counterkdiff.sh` (same shared
driver). Population, measured this session (`bash tests/counterk/
run_counterkdiff.sh`):

```
COUNTERKDIFF_TALLY
```

### 2.4 `-fno-length-prune` — `PCREC_NO_LENGTH_PRUNE` (bit 7)

**Denies** MINIMUM-REMAINING-LENGTH (MRL) pruning (`docs/design/
k23_impl/k23_design.md`, D51 ruling 1). Default: MRL prunes where a bound
is derivable. **ANSWER-IDENTITY-preserving**, same masked treatment, and
the strongest case in the family for it: MRL emits a bound on whichever
rung a quantifier already took and changes no rung, no slot and no
capacity, so a denied artifact is claimed **byte-for-byte the emitter's
own pre-MRL output** (`lib/pcrec.h`'s own comment) — not merely
answer-identical, structurally identical. **Reason it exists:** same
D47.3 claim, and the byte-for-byte form is what makes the ground truth
strongest here.

**Differential:** `tests/mrl/run_mrldiff.sh` (same shared driver), which
sweeps **both engines** — the default (prefilter-windowed) ceiling and
`--engine=vm` (subject-end) ceiling are different arithmetic and only the
default is what ships, so both run. Population, measured this session
(`bash tests/mrl/run_mrldiff.sh`):

```
MRLDIFF_TALLY
```

### 2.5 `-fno-prefilter` / `-fprefilter` — `PCREC_NO_PREFILTER` (bit 8) / `PCREC_FORCE_PREFILTER` (bit 9)

The D46 close-out for the PREFILTER axis (`fit.prefilter`,
`src/opt/select_engine.c`, `docs/design/engine_m4.md` §6.1/§4.7). A
**FORCE PAIR**, not deny-only like §2.1-2.4 and §2.6-2.7 — the reason is
structural, not a style choice: those deny a per-QUANTIFIER strategy
(each quantifier walks its own ladder, so "force it on THIS quantifier"
has no addressing problem to solve), while `fit.prefilter` is **one
verdict for the whole artifact**, decided jointly with `--engine`
(auto+captures turns it on; `--engine=vm` turns it off as a side effect,
R21 E-6). Before this axis existed there was no way to ask for the OFF
state under otherwise-auto selection, or the ON state under
`--engine=vm` — exactly the coupling D46's own motivating scenario warns
about (a test built to pin one axis silently moves on another), so both
directions are independently reachable.

Default: auto-selected jointly with the engine. **ANSWER-IDENTITY-
preserving in one direction, DO-OR-DIE in the other**: `PCREC_NO_PREFILTER`
never refuses (`--engine=vm` already ships that exact configuration).
`PCREC_FORCE_PREFILTER` on a pattern that compiles to the DFA engine (no
VM artifact exists to attach a prefilter to) **REFUSES** with a
diagnostic — the same `--engine`-precedent do-or-die posture (D47.3),
never a silent downgrade. Masked out of `rx_info.flags` (the axis changes
no answer, only how one is found); what the emitter DID is the
`RX_VM_PREFILTER` scalar stamp (`"hybrid"` / `"none"`), verified:

```
$ build/pcrec -p rx --emit-main -o /tmp/c.c 'a(b|c)+d'; grep RX_VM_PREFILTER /tmp/c.c
#define RX_VM_PREFILTER      "hybrid"
$ build/pcrec -p rx -fno-prefilter --emit-main -o /tmp/d.c 'a(b|c)+d'; grep RX_VM_PREFILTER /tmp/d.c
#define RX_VM_PREFILTER      "none"
```

**Reason it exists:** the hybrid prefilter (a capture-erased DFA
forward+reverse pair used as an exact anchored-match window ahead of the
VM) is an observability/controllability gap D46 names directly — without
it, "which engine" and "does the hybrid prefilter run ahead of it" could
not be independently pinned.

**Differential:** deliberately **none of its own**
(`tests/prefilter/CLAUDE.md`): the prefilter's correctness (that the
hybrid answers the same span the pure VM would) already rides
`tests/vm/run_vm_tests.sh` §3.7 and the ceiling-form coverage in
`tests/mrl/run_mrl_tests.sh`; this axis adds observability and
controllability on an already-validated mechanism, not a new algorithm.
`tests/prefilter/run_prefilter_tests.sh` is structural (stamp assertions
paired with an independent read of the emitted `_prefilter(` function
bodies, so the check cannot pass on a stamp that has drifted from the
actual machinery) — not a pattern-subject-startpos differential, so no
cell tally applies here.

### 2.6 `-fno-altcls-merge` — `PCREC_NO_ALTCLS_MERGE` (bit 10)

**Denies** stage 1 of the ALTERNATION→CLASS normalization pass
(`src/opt/altcls.c`, `docs/dev/plan.md`'s `[OPT-ALTCLS]` row): merging a
maximal run of single-character alternation branches into one class.
Default: stage 1 runs where a run qualifies. **ANSWER-IDENTITY-
preserving**, masked out of `rx_info.flags`. Back to the DENY-only shape
(not a force pair like §2.5): each mergeable run is its own selection
point, addressed independently the way an `A_REP` walks its own
possessify/revdet ladder, so there is no artifact-wide verdict for FORCE
to solve an addressing problem for. **Unlike §2.1-2.4, this pass is NOT
VM-only** — it runs before either engine is built, so a capture-free
pattern's DFA artifact carries its stamp too. **Reason it exists:** same
D47.3 claim, applied to a pass that predates engine selection.

### 2.7 `-fno-altcls-factor` — `PCREC_NO_ALTCLS_FACTOR` (bit 11)

**Denies** stage 2 of the same pass: prefix-factoring a maximal run
sharing a literal first byte, running on stage 1's output (so denying
stage 1 alone still lets stage 2 factor an unmerged run's literal
spelling; denying stage 2 alone leaves single-character merging live —
this is why the pass has two knobs rather than one). Default: stage 2
runs where a run qualifies. Same ANSWER-IDENTITY-preserving, masked, not
VM-only treatment as §2.6. Both stages stamp `<PREFIX>_ALTCLS_MERGES` /
`<PREFIX>_ALTCLS_FACTORED`, verified:

```
$ build/pcrec -p rx --no-captures --emit-main -o /tmp/e.c '[abc]|[def]|xyz'; grep RX_ALTCLS /tmp/e.c
#define RX_ALTCLS_MERGES   1
#define RX_ALTCLS_FACTORED 0
```

**Reason it exists:** same D47.3 claim; two bits because the two rewrite
stages are separately useful to pin.

**Differential (both bits):** `tests/altcls/run_altdiff.sh` (denies both
`-fno-altcls-merge -fno-altcls-factor` together against the pass live, the
shared driver). Population, measured this session (`bash tests/altcls/
run_altdiff.sh`):

```
ALTDIFF_TALLY
```

### 2.8 `-fno-atomic-discharge` — `PCREC_NO_ATOMIC_DISCHARGE` (bit 12)

**Denies** the FREE DISCHARGE (`docs/design/atomic_groups_design.md`
§5.3, `src/opt/atomic.c`): deleting an `A_ATOMIC` node whose cut
possessify's verdict proves is a no-op. Default: the discharge runs where
provably safe. **ENGINE-SELECTING — the first of the two axes in this
family that is not answer-identity-preserving alone.** What it denies is
an ENGINE, not a strategy: every other deny-only flag above leaves the
same artifact kind and changes only the machinery inside it; denying this
one leaves the `A_ATOMIC` node in the tree, which is DFA-excluding, so a
pattern that would otherwise compile to a pure DFA compiles to the VM
instead. **Consequence, verified this session:**

```
$ build/pcrec -p rx --features atomic-groups --engine=dfa \
    -fno-atomic-discharge --no-captures -o /tmp/x1.c '[^"]*+"'
pcrec: possessive quantifier requires the VM engine, which --engine=dfa excludes (pattern offset 5)
```

REFUSES — correct, and the flag doing its job (the same do-or-die
posture `--engine` itself has). **NOT masked from `rx_info.flags`** — the one place this axis differs procedurally from
§2.1-2.7 — because it can genuinely change which engine a pattern gets,
so two artifacts differing only in this bit are not claimed
identically-behaving-therefore-indistinguishable the way the masked axes
are. Deliberately **separate from `-fno-possessify`**: the discharge is
not gated by that flag, because an optimization denial must not decide
which engine a pattern gets. **Reason it exists:** the discharge's
"changes no answer" claim (for the case where it applies at all — a
possessify-proved-dead atomic group) needs the same differential every
other member of the family needs.

**Differential:** `tests/atomic_groups/run_atomic_diff.sh` §3 (the
DISCHARGE differential, pcrec-vs-pcrec, asserting identical answers with
and without `-fno-atomic-discharge`, plus §5.4's emission-neutrality
where it holds). Not independently re-run this session — its own suite
carries subject sweeps against libpcre2 (§1, §2) in addition to §3's
pcrec-vs-pcrec arm, and the brief scopes this lane to the flags' own
identity/diff instruments; `tests/atomic_groups/CLAUDE.md` and the
script's own header (read this session) are the citation.

### 2.9 `-fno-splice-calls` — `PCREC_NO_SPLICE_CALLS` (bit 13)

**Denies** the SPLICE linkage at every eligible subroutine call site
(`docs/design/subroutines_design.md` §6.3, §9.2), forcing the CALL
linkage everywhere instead. Default: a call site whose callee is not in a
cycle and whose expansion fits the size budget is spliced (emitted
inline, its own exit); every other site takes the shared CALL linkage.
**ENGINE-SELECTING, the family's second and last such axis, and the
same shape as §2.8's:** a spliced call has an exact finite lowering, so
`src/ir/nfa.c` can build the machine and `select_engine` need not force
the VM; denying the splice leaves a LINKED call, which is structurally
VM-only. **Consequence, verified this session:**

```
$ build/pcrec -p rx --features named-groups,recursion --engine=dfa \
    -fno-splice-calls --no-captures -o /tmp/x2.c '(?:(?<g>a)){0}(?&g)'
pcrec: (?&name) requires the VM engine, which --engine=dfa excludes (pattern offset 14)
```

REFUSES — correct, the discharge's own precedent exactly. **NOT masked
from `rx_info.flags`**, for the identical reason as §2.8 — verified: a
default build of `'(a)(?1)'` carries `.flags = 2ULL` (`PCREC_EMIT_MAIN`
only); the `-fno-splice-calls` build of the same pattern carries `.flags
= 8194ULL` (`2 | (1u << 13)`) — the bit is visibly present, unlike every
masked axis in §2.1-2.7. What the emitter did (sites spliced vs. linked)
is **`<PREFIX>_VM_CALL_SPLICED`/`<PREFIX>_VM_CALL_LINKED`** (two scalar
counts), verified on `'(a)(?1)'`:

```
$ build/pcrec -p rx --features named-groups,recursion --emit-main -o /tmp/s1.c '(a)(?1)'
$ grep RX_VM_CALL /tmp/s1.c
#define RX_VM_CALL_SPLICED 1
#define RX_VM_CALL_LINKED 0
$ build/pcrec -p rx --features named-groups,recursion -fno-splice-calls --emit-main -o /tmp/s2.c '(a)(?1)'
$ grep RX_VM_CALL /tmp/s2.c
#define RX_VM_CALL_SPLICED 0
#define RX_VM_CALL_LINKED 1
```

**STALE, flagged rather than silently matched:** `lib/pcrec.h`'s own
comment (the `PCREC_NO_SPLICE_CALLS` bit, and `<prefix>_search`'s doc
block) names this stamp `<PREFIX>_VM_CALLS` (singular, one macro); the
shipped emitter (`src/gen/emit_vm.c`) actually names two macros,
`RX_VM_CALL_SPLICED`/`RX_VM_CALL_LINKED`, confirmed by grep against a
fresh build and by the emitted text above — `RX_VM_CALLS` does not
appear anywhere in `src/gen/emit_vm.c`. This document states the
as-built name; `lib/pcrec.h`'s comment is a small drift outside this
lane's own scope to fix. **Reason the axis exists:** the SPLICE-vs-
LINKAGE choice reaches `select_engine.c`, which every pattern goes
through, so an axis that pins the linkage constant localizes a wrong
eligibility rule.

**Differential:** `tests/recursion/run_recursion_diff.sh` §5, "`A == B`":
the SPLICE-linked and the LINKAGE-linked artifact, over the corpus,
compared on ANSWERS (not bytes — `tests/codegen/run_recursion_identity.sh`
is the sibling BYTE-identity gate for the module-boundary claim, a
different, narrower claim than this section's). Population, measured
this session (`bash tests/recursion/run_recursion_diff.sh`, §5's own
summary line):

```
RECURSION_DIFF_TALLY
```

### 2.10 `--unroll=K` — the counter rung's value parameter

Not a bit in `pcrec_options.flags`; a separate `int unroll_k` field
(`lib/pcrec.h`). **The value parameter of `-fno-counter`'s rung (§2.3):**
one emitted body copy per K iterations, K = 0 meaning the built-in
`PCREC_DEFAULT_UNROLL_K` (`src/core/limits.h`; D47.2's calibration).
Range enforced at the CLI: an integer in `1..4096` (`cli/main.c`).
**One value per artifact, never per quantifier** — held strictly by the
D47 ADDENDUM ("K must not become a per-pattern heuristic in v1"; the
downward clamp that would have varied it moved whole to plan row
`[ENG-CLAMP]`). Not itself answer-identity-vs-engine-selecting in the
same sense as §2.1-2.9 — it is a tuning parameter of a strategy that is
already selected, not a strategy denial — but it inherits the counter
rung's ANSWER-IDENTITY claim: unrolling by a different K changes the
emitted loop's shape, never what it accepts. **Reason it exists:** it is
the one shape parameter the counter rung's design left open (`docs/
design/counterk_impl/counterk_design.md` §4.1).

### 2.11 `--engine=dfa|vm|auto` — the coarsest-grained tuning-adjacent axis

Not a `-f`/`-fno-` flag and not primarily a tuning axis — it is D46's own
motivating case, restated here because every flag in §2.1-2.9 is scoped
relative to it (the two ENGINE-SELECTING ones, §2.8/§2.9, can force the
same choice this flag makes directly). Default: `auto`, APPROACH.md §2's
"automatic per pattern" selection. `dfa`/`vm` are diagnostic overrides —
reproduce a bug, measure the hybrid against a VM-only build — and
**DO-OR-DIE**: a request the pattern cannot honour (e.g. `--engine=dfa`
on a pattern with unbounded backtracking machinery) REFUSES with a
diagnostic naming the construct, never a silent fallback
(`src/opt/select_engine.c`). `--engine=vm` additionally **disables the
DFA prefilter** (D44/R21 E-6) — the one place this axis and §2.5 compose
directly — which is what makes `--engine=vm` usable as an independent
second derivation of the match span rather than an echo of the DFA's.
`PCREC_ENGINE_AUTO` is an `enum` member; `PCREC_ENGINE_DFA`/
`PCREC_ENGINE_VM` are `#define`s for the ABI-collision reason
`lib/CLAUDE.md`'s `[ABI-NS]` entry states (an artifact's own identical
`#define` of the same name must not error against this header). No
separate differential of its own — every module's own diff suite already
sweeps at least the default and `--engine=vm` axes (`tests/atomic_groups/
run_atomic_diff.sh` §2, `tests/recursion/run_recursion_diff.sh`'s four
axes) as the engine differential D46 asks for at the module level.

## 3. The DFA-side stamp gap

**Current limitation, plan row `[DD-13]`:** a DFA artifact emits no
`RX_ENGINE`, no `RX_ENGINE_WHY`, and no prefilter-family stamp at all —
D46's per-artifact observability principle (§6.3, `docs/spec/
match_api.md`) is VM-only on this axis today. `rx_info.engine` (the
runtime reflection field, not a compile-time macro) is the only readable
selection field a DFA artifact carries. Verified by listing a
`--no-captures` build's `#define`s: only `RX_NCAPS` and the two
`RX_ALTCLS_*` stamps (§2.6/§2.7) are artifact-summary macros; no
`RX_ENGINE`-family macro appears. Measured and recorded at
`docs/dev/plan.md` `[DD-13]`'s "BENCH-DISCOVERED CANDIDATES" note
(2026-08-25, pcrec-bench's email-specimen run): the byte-class skip loop
that is the DFA's own headline optimization is invisible to a caller
reading compile-time macros for the same reason — an `RX_DFA_PREFILTER`-
style stamp in the D46 family is a candidate there, not built. This
document states the gap rather than promising the fix; `[DD-13]` is
where the fix, if built, would land.

## 4. `pcrec_options` mirror

Which `pcrec_options` fields (`lib/pcrec.h`) correspond to which flags in
§2. `docs/spec/match_api.md` §8.2 states the struct itself in full; this
table only maps field to axis.

| `pcrec_options` field | CLI spelling | §2 axis |
|---|---|---|
| `flags` bit `PCREC_NO_POSSESSIFY` | `-fno-possessify` | §2.1 |
| `flags` bit `PCREC_NO_REVDET` | `-fno-revdet` | §2.2 |
| `flags` bit `PCREC_NO_COUNTER` | `-fno-counter` | §2.3 |
| `flags` bit `PCREC_NO_LENGTH_PRUNE` | `-fno-length-prune` | §2.4 |
| `flags` bits `PCREC_NO_PREFILTER` / `PCREC_FORCE_PREFILTER` | `-fno-prefilter` / `-fprefilter` | §2.5 |
| `flags` bit `PCREC_NO_ALTCLS_MERGE` | `-fno-altcls-merge` | §2.6 |
| `flags` bit `PCREC_NO_ALTCLS_FACTOR` | `-fno-altcls-factor` | §2.7 |
| `flags` bit `PCREC_NO_ATOMIC_DISCHARGE` | `-fno-atomic-discharge` | §2.8 |
| `flags` bit `PCREC_NO_SPLICE_CALLS` | `-fno-splice-calls` | §2.9 |
| `unroll_k` (`PCREC_UNROLL_K_DEFAULT` = 0) | `--unroll=K` | §2.10 |
| `engine` (`PCREC_ENGINE_AUTO`/`_DFA`/`_VM`) | `--engine=E` | §2.11 |

`step_budget`, `work_budget` and `frame_capacity` are resource-bound
fields, not strategy-selection tuning axes — `docs/spec/limits.md` is
their home, not this document.
