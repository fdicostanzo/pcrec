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

**`pcrec --list-axes` ([CHK-2], `docs/spec/registry.md` §6) is the
machine-readable view of this same table** — every bit-flag axis below
plus the six DFA layer-1 axes (table representation, prefilter, view,
seed, accept, direction) that have no CLI flag at all, one TSV row per
(axis, candidate). It answers what THIS BUILD thinks its axes are; this
document remains the promise about what denying/forcing one DOES.

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
strategy that cannot be denied cannot be differentially tested"). Nine of
the twelve axes in §2 are D47.3's family — the deny-only seven, the force
pair (§2.5), and the two engine-selecting denials — and eight of those
nine exist **because** they have a differential that checks this exact
claim directly: compile the same pattern twice, once with the strategy and
once without, link both into one driver, and sweep subjects comparing
span, every capture slot, and the failure surface. The ninth, §2.5's force
pair, is the family's one exception — its own correctness already rides
an existing, already-validated suite (§2.5 states which), so it earns no
NEW differential of its own even though it is D46's canonical
motivating case for the observable/forceable principle. `--unroll=` is the
deny family's value parameter and `--engine=` is the coarsest-grained
member of the same observable/forceable principle, one level up.

**Who this document is for.** A contributor building or reviewing a
differential test needs to know, per axis: what it denies/forces, whether
it can be relied on to leave the answer unchanged (so the denied build is
a valid ground truth) or whether it can move the pattern between engines
(so a differential comparing spans across the axis needs the engine
difference accounted for separately), and which check already carries the
evidence. A stranger tuning performance needs the same table read the
other way: which knobs are safe to flip without re-verifying correctness,
and which one is a `--engine`-shaped do-or-die request.

## 2. The thirteen axes

Each subsection: what it controls, the default, the stamp it leaves in an
emitted artifact (verified by an emitted-artifact diff, command given),
whether it is ANSWER-IDENTITY-preserving or ENGINE-SELECTING, and the
one-sentence reason the axis exists.

**`make test-axes` ([CHK-2], `tests/axes/run_axes.sh`) is the sweep that
enforces every axis's answer-identity promise stated below** — the whole
`.rxt` corpus, per case, under every deny/force flag and the `--engine=`
axis, compared against the default build (D80: the spec names its own
enforcement). Opt-in, like the sanitizer battery; see `docs/testing.md`
"Answer-identity sweep" for runtimes and how to read a failure, and its
"classification rule" subsection for how a documented refusal (§2.3's
replication cap, §2.5's force-prefilter refusal) or a budget boundary
moving (a give-up or per-case timeout on either side) is distinguished
from a genuine answer disagreement.

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
#define RX_VM_STRATS 0x1u
$ build/pcrec -p rx --engine=vm -fno-possessify --emit-main -o /tmp/b.c '(x)(?:a|bc)+d'; grep RX_VM_STRATS /tmp/b.c
#define RX_VM_STRATS 0x2u
```

(`0x1u` is `PCREC_VM_STRAT_POSSESSIVE`, `0x2u` is `PCREC_VM_STRAT_BACKTRACKING` — the named bit constants, `lib/pcrec.h`'s
`PCREC_RX_ABI_H` block; the annotation is this document's, the emitted line carries only the hex value.
`rx_info.flags` and every other field of the initializer are unchanged
between the two builds except `frame_capacity`, which grows because a
backtracking build needs a frame the possessive one does not — verified
on this same pattern: `.frame_capacity = 3` possessified,
`.frame_capacity = 4` under `-fno-possessify`; `docs/spec/match_api.md`
§6.3 records the same effect on its own example.) **Reason it exists:** possessification is
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
rungdiff: 205 patterns agreed, 0 diverged, 0 refused by pcrec
rungdiff: 106 of 205 took the REVERSE-DETERMINISTIC rung
rungdiff: 395757 pattern-subject-startpos cells compared
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
counterkdiff: 59 patterns agreed, 0 diverged, 0 refused by pcrec
counterkdiff: 45 of 59 took the COUNTER rung
counterkdiff: 541899 pattern-subject-startpos cells compared
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
mrldiff: 146 pattern-engine pairs agreed, 0 diverged, 0 refused by pcrec
mrldiff: 138 of 146 carried at least one CLAMPED quantifier
mrldiff: 202458 pattern-subject-startpos cells compared
mrldiff: 22 cell(s) excused by the answer-more asymmetry (pinned expectation 22)
mrldiff: 22 excused cell(s) refereed against the pure DFA engine; 0 pattern-engine pair(s) had no referee available
mrldiff: rung coverage complete (mask 0x1f): every rung MRL emits a form for was reached
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
#define RX_VM_PREFILTER "hybrid"
$ build/pcrec -p rx -fno-prefilter --emit-main -o /tmp/d.c 'a(b|c)+d'; grep RX_VM_PREFILTER /tmp/d.c
#define RX_VM_PREFILTER "none"
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

**Identity is modulo WHICH BUDGET BINDS.** The prefilter changes how much WORK a search does before it answers, never the answer — but a give-up is a bound on work, so on a subject that sits near a budget the two builds can differ by a GIVE-UP CODE where neither is wrong: measured 2026-08-26 ([ENG-FORM]'s answer gate, pre-existing), `((a)|bc){0,4000}d` over 1 MB of `a` is `no match` with the hybrid's DFA prefilter and `PCREC_ERR_WORK` without it. A sweep that compares answers across this axis must classify a give-up on either side as budget-bound (reported, floored), not as a disagreement.

**[SEL-1] (2026-08-28) A THIRD OFF-ROUTE, AND IT IS BEFORE THE TWO FLAG
ROUTES FOR THE SAME REASON THE BACKREFERENCE/CALL ROUTES ARE (§4, `-fprefilter`'s force branch above): no flag explains it, so naming one would be a
diagnostic lie. Under `auto`, with neither `-fprefilter` nor `-fno-prefilter`
requested, an auto-selected prefilter whose own DFA build OVERFLOWS a cap
(state count, table entries, K7's element budget — the identical caps
`--engine=dfa` can hit) is DROPPED rather than refused: `fit.prefilter`
comes out `false` and the artifact stamps `RX_VM_PREFILTER "none"`, exactly
as if `-fno-prefilter` had been passed, though `--emit-ir`'s `; prefilter`
line does not claim that flag's credit (it reads the same `RX_ENGINE_WHY`
overflow text §2.11 states, not `-fno-prefilter`). `-fprefilter` itself is
UNCHANGED — forcing the prefilter on a pattern whose DFA cannot be built
still REFUSES with today's diagnostic (§2.11), because a caller who named
the flag asked for the machine that overflows. See §2.11 for the mechanism
(`src/opt/select_engine.c`'s `forces_dfa_overflow`, `Ctx.dfa_disabled`) and
the cost bound; this entry states the PREFILTER-side half of the same single
mechanism, not a second one.

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
#define RX_ALTCLS_MERGES 1
#define RX_ALTCLS_FACTORED 0
```

**Reason it exists:** same D47.3 claim; two bits because the two rewrite
stages are separately useful to pin.

**Differential (both bits):** `tests/altcls/run_altdiff.sh` (denies both
`-fno-altcls-merge -fno-altcls-factor` together against the pass live, the
shared driver). Population, measured this session (`bash tests/altcls/
run_altdiff.sh`):

```
altdiff: 41 patterns agreed, 0 diverged, 0 refused by pcrec
altdiff: 30 of 41 had at least one ALTCLS merge or factor
altdiff: 35995 pattern-subject-startpos cells compared
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

The stamp is TWO counts, `<PREFIX>_VM_CALL_SPLICED` and
`<PREFIX>_VM_CALL_LINKED` (never a single `<PREFIX>_VM_CALLS`): `SPLICED +
LINKED` is every call site the emitter wrote, and the interesting question
is their ratio (`src/gen/emit_vm.c`; `lib/pcrec.h`'s comment on the
`PCREC_NO_SPLICE_CALLS` bit names the same pair). **Reason the axis exists:** the SPLICE-vs-
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
PASS: §5 A == B: 279 of 322 corpus patterns compiled on BOTH linkages (43 refused on both), 28458 cells compared over 24 subjects x every startpos, span AND every group span, 0 disagreements between the SPLICE-linked and the LINKAGE-linked artifact
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

**[SEL-1] (2026-08-28) `auto`'s DO-OR-DIE POSTURE HAS ONE EXCEPTION, AND IT
IS ABOUT A CAP THE PATTERN COULD NOT HAVE ADVERTISED IN ADVANCE.** Every
other DO-OR-DIE refusal above is decided by an AST-level analysis before any
automaton is built — the pattern either carries a construct the requested
engine cannot honour, or it does not. A DFA-cap overflow (state count, table
entries, the K7 subset-element budget — `src/core/limits.h`, every cap
`src/ir/dfa.c`'s two "pattern too complex" sites cover) is discovered only by
attempting the BUILD, and under `auto` — with neither `--engine=dfa` nor
`-fprefilter` in play — that overflow is a SELECTION OUTCOME rather than a
refusal: the compile falls back to the VM (`RX_ENGINE "vm"`, `RX_ENGINE_WHY`
naming the cap, e.g. `"dfa overflowed: >32000 states"`), and if the pattern
was already VM-selected for another reason and only its auto-selected
PREFILTER's DFA overflowed, the prefilter is DROPPED (`RX_VM_PREFILTER
"none"`) rather than refused. `--engine=dfa` and `-fprefilter` are UNCHANGED
by this — both still refuse with today's diagnostic
(`"pattern too complex for the DFA engine (>N states; try --engine=vm)"`),
because a caller who named the engine explicitly asked for the machine that
cannot be built, and that request stays do-or-die.

**THE COST BOUND**: the fallback compile is at most ONE refused DFA build
dearer than asking for `--engine=vm` directly. The overflowing build's own
cost is bounded by the K7 budget (`src/core/limits.h`'s `PCREC_MAX_SUBSET_
ELEMS` entry: ~0.9 s / ~216 MB at the worst state-cap refusal measured
there); `src/core/compile.c`'s retry never re-attempts that construction — it
reruns the pipeline once with the DFA excluded from selection outright
(`Ctx.dfa_disabled`, consumed by `src/opt/select_engine.c`'s
`forces_dfa_overflow` row and by the prefilter derivation together, in one
step), so a pattern that would have needed a prefilter DFA never builds it
twice. Verified live (the witness `\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:
timeout|timed out|refused|denied|unreachable)\b`, `--features all`):

```
$ time build/pcrec -p rx --features all --engine=auto -o /tmp/a.c "$P"
real  0m0.52s
$ grep -E 'RX_ENGINE |RX_ENGINE_WHY|RX_VM_PREFILTER' /tmp/a.c
#define RX_ENGINE "vm"
#define RX_ENGINE_WHY "dfa overflowed: >32000 states at pattern offset 0"
#define RX_VM_PREFILTER "none"
$ build/pcrec -p rx --features all --engine=dfa -o /tmp/d.c "$P"
pcrec: pattern too complex for the DFA engine (>32000 states; try --engine=vm)
$ build/pcrec -p rx --features all --engine=vm -fprefilter -o /tmp/v.c "$P"
pcrec: pattern too complex for the DFA engine (>32000 states; try --engine=vm)
```

`RX_ENGINE_WHY`'s text carries the ordinary `"... at pattern offset N"` suffix
every `why` goes through (`why_text`, `src/opt/select_engine.c`) even though
this reason is not tied to one AST node — offset 0 by convention, the same
position the two `ctx_fail` sites in `src/ir/dfa.c` already report at. If the
pattern's engine choice is ALSO forced by a real construct (a live capture, a
`VM_ONLY` registry row), that reason wins `RX_ENGINE_WHY` on the ordinary
first-wins rule (§5.5) — the overflow's own effect (drop the prefilter) still
applies independently, through `Ctx.dfa_disabled` rather than through `why`.
Witness: `tests/vm/run_vm_tests.sh` §3b.

**A FALLBACK CAN SHIP A VM ARTIFACT THE DFA REFUSAL USED TO SUPPRESS, AND ONLY
THE VM'S OWN CAPS BOUND IT THEN** (K41, `docs/dev/known_issues.md`, found by
the manager's landing battery, 2026-08-28). Before this row, a pattern whose
DFA build overflowed was refused outright — the VM PROGRAM that pattern would
have emitted was never built, so nothing about the VM emitter's own limits
mattered for it. Under the fallback, that VM program IS built and shipped, and
the DFA-side caps this section otherwise governs (state count, table entries,
K7's subset-element budget) have nothing more to say about it: from that point
on, the only bounds on the artifact are the VM emitter's OWN caps
(`src/core/limits.h`) — `PCREC_MAX_VM_NODES` (131,072 emitted-node budget),
`PCREC_MAX_VM_REPEAT_COPIES` (64, one bounded repeat's own replication
ceiling) and `PCREC_MAX_VM_REPLICATION_PRODUCT` (nested-repeat products, tied
to `PCREC_MAX_VM_NODES`'s own value). K41's measured witness is a case those
caps do not fully cover today: a deeply-nested, wide bounded-repeat pattern
whose VM artifact compiles fine as pcrec's own output but is large enough
(2,004,778 bytes) that `gcc -O2 -c` itself hits a CPU-time resource limit —
52.9 s / 540 MB, `internal compiler error: CPU time limit exceeded`. That is a
test-harness/toolchain-visible cost (D45's gcc compile-time budget), not a
pcrec correctness defect, and the fix direction (a VM-side emitted-PROGRAM-SIZE
cap, refusing before emission the way the DFA-side caps already do) is
chartered separately rather than built here — see K41's own entry.

### 2.12 `-fno-tiered-entry` — `PCREC_NO_TIERED_ENTRY` (bit 14)

**ANSWER-IDENTITY-preserving**, and the strongest such claim in this
section: the tier it denies is a pure cost transformation whose two shapes
are proved to answer identically by construction, not by sampling
(`docs/spec/match_api.md` §10.9).

**What it controls.** On an artifact whose stamped default storage does not
fit inside one 4 KB page, `<prefix>_search`/`_match`/`_match_caps` run the
match on a page-budgeted on-stack buffer and escalate to the stamped default
— by calling a non-inlined internal function that owns it and re-runs from
scratch — on `PCREC_ERR_FRAMES` and on nothing else. Denying emits the
SINGLE-TIER shape those entries had before `[OPT-1]`. Default: the tier is
ON. Deny-only, `-fno-possessify`'s shape rather than `§2.5`'s force pair:
there is one entry shape per artifact, so there is nothing to address and
nothing to force.

**Reason it exists.** gcc's stack-clash protection probes every page of a
function's frame on every call, so a 98,512-byte storage local cost 233.8
ns on a subject that matches in a few hundred instructions
(`docs/design/two_tier_entry.md` §1). The flag is both the bisect lever for
that optimization and the build an identity gate can compare the old entry
against — the second control `tests/codegen/run_tiered_entry.sh` §5 uses,
in the shape `-fno-splice-calls` gives module `recursion`.

**The stamp.** `<PREFIX>_FAST_FRAMES`/`<PREFIX>_FAST_TRAIL` (match_api.md
§6.3(b)) — VM-only, `.c`-private, on every VM artifact. Under the denial
they equal `<PREFIX>_RESUME_FRAMES`/`_TRAIL_FRAMES`, which is the same
reading three answer-preserving degenerate cases produce and is the
document's only spelling of "this artifact has one tier". **MASKED out of
`rx_info.flags`** (`src/gen/emit_dfa.c`'s `strategy_denials`), for the
mask's own reason: it changes no answer, so two artifacts that behave
identically must not differ in their reflection surface over it, and what
the emitter DID is already reported by the stamp.

**The stamp anchors on `RX_FAST_`, not on `RX_(FAST|RESUME|TRAIL)`**: the
looser pattern also matches the four §10.4 sizing macros and the `RX_TRAIL`
undo macro, so it prints seven lines rather than two. Re-run and verified at
this commit:

```
$ build/pcrec -p rx --engine=vm --features recursion -o - -- '^(a(?1)?b)$' \
    | grep -E '^#define RX_FAST_'
#define RX_FAST_FRAMES 47
#define RX_FAST_TRAIL 71
$ build/pcrec -p rx --engine=vm --features recursion -fno-tiered-entry -o - \
    -- '^(a(?1)?b)$' | grep -E '^#define RX_FAST_'
#define RX_FAST_FRAMES 2048
#define RX_FAST_TRAIL 3072
```

(47/71 is this artifact's page-budgeted pair; 2048/3072 is the stamped default,
and `FAST == RESUME`/`TRAIL` is how a reader tells that the tier is off.)

### 2.13 `-fno-premul-table` — `PCREC_NO_PREMUL_TABLE` (bit 15)

**ANSWER-IDENTITY-preserving.** The axis changes the ENCODING of a DFA
state, not the machine: the same states, the same byte classes, the same
transitions, written down differently.

**What it controls.** A DFA scan's transition table normally holds
`next_state * classes` rather than `next_state`, so the emitted step is
`state = table[state + class]` (`unsigned short` cells, `65535` for dead)
and the loop's carried dependency chain is `add, load` rather than
`lea, lea, movslq, load`. Denying it emits the INDEXED form — the tables
and the loop exactly as they shipped before `[OPT-3]`. Default: the
pre-multiplied form is ON, subject to the generation-time bound below.
Deny-only, `§2.12`'s shape rather than `§2.5`'s force pair: there is one
table form per machine and the compiler picks it, so there is nothing to
address and nothing to force.

**Reason it exists.** `[OPT-3]` STEP 1 measured the DFA scan as
LATENCY-bound — 10.7 cycles/byte on the comparative bench's throughput
subjects, of which 7 are that address-arithmetic chain, with two
independent streams nearly halving the per-byte cost — and the
pre-multiplied form as **1.276x** on those three subjects,
answer-identical over 40,469 answer lines across 91 subjects
(`docs/dev/opt3_dfa_scan_measurement.md` §5, §7). The flag is both the
bisect lever for that optimization and the build the identity comparison
uses as its control.

**The shipped form measures larger than that estimate**: re-measured on
the emitter rather than on a patched artifact, `1.794x` on the same three
subjects, which puts pcrec ahead of PCRE2-JIT on all three
(`docs/design/premultiplied_dfa_table.md` §13 carries the table, the
answer gate and the attribution for the difference).

**The bound, and it is not this flag.** The form is REFUSED at generation
time, per machine, when that machine's `states * classes` exceeds
**65,535** — a CORRECTNESS condition and not a budget: a cell must fit
`unsigned short` and stay distinguishable from the dead sentinel. The
forward and reverse machines are decided separately, which is why
`"mixed"` exists. A tighter 16,384-entry SIZE BUDGET was specified and
then DELETED on a measurement (`docs/design/premultiplied_dfa_table.md`
§7): the pre-multiplied form still wins across the whole L2-resident
band — 1.107x at 18,432 entries, 1.097x at 36,864, and **1.287x on the
corpus's own largest machine at 40,010** — because the two chain cycles
the transform removes are removed whatever the load costs, and the accept
table's growth is a `.rodata` cost rather than a per-byte one.

**The stamp.** `<PREFIX>_DFA_TABLE` (§3), on every artifact that contains
a DFA scan. **MASKED out of `rx_info.flags`** (`src/gen/emit_dfa.c`'s
`strategy_denials`), for the mask's own reason: it changes no answer, so
two artifacts that behave identically must not differ in their reflection
surface over it, and what the emitter DID is already reported by the
stamp. Re-run and verified at this commit:

```
$ build/pcrec -p rx --no-captures -o - -- '(?:[a-z]+)@(?:[a-z]+)' \
    | grep -E '^#define RX_DFA_TABLE'
#define RX_DFA_TABLE "premultiplied"
$ build/pcrec -p rx --no-captures -fno-premul-table -o - \
    -- '(?:[a-z]+)@(?:[a-z]+)' | grep -E '^#define RX_DFA_TABLE'
#define RX_DFA_TABLE "indexed"
```

and the generation-time bound switching on its own, on the
state-explosion family `[01]*1[01]{k}` (the forward machine's entry count
in brackets). Every pattern in pcrec's own corpus is inside the bound —
the largest is 40,010 entries — so the ABOVE-bound side is exercised by
one member past what the corpus contains:

```
k=12  [36,864]  RX_DFA_TABLE "premultiplied"
k=13  [73,728]  RX_DFA_TABLE "mixed"          (forward indexed, reverse pre-multiplied)
```

## 3. The DFA side's own stamps

**CLOSED 2026-08-25 by plan row `[DD-13]`; this section stated the gap while
it was open.** A DFA artifact now carries three D46 selection stamps, in the
same position of the file a VM artifact carries its own:

```
$ build/pcrec -p rx -o - --no-captures -- 'abc' | grep -E '^#define RX_(ENGINE|DFA_)'
#define RX_ENGINE "dfa"
#define RX_DFA_SCAN "unanchored"
#define RX_DFA_PREFILTER "memchr"
#define RX_DFA_TABLE "premultiplied"
```

`docs/spec/match_api.md` §6.3 is the contract; in short:

- `RX_ENGINE` is **unconditional** — present on every artifact both engines
  produce, `"vm"` or `"dfa"`, from one emitter so the two cannot drift. This
  is what makes `#if`-ing on it safe, which §6.3 used to warn it was not.
- `RX_DFA_SCAN` is `"unanchored"` (the O(n) forward+reverse table pair),
  `"attempt"` (the per-start computed-goto loop a `^`/`\A`-bearing pattern
  takes) or `"empty"` (`[DD-13c]`: the pattern provably matches nothing, so
  the body is one `return 0` and there is no loop of either shape in it).
  Nothing else a consumer can read distinguishes them: all three stamp
  `RX_ENGINE "dfa"` and all three set `rx_info.engine` to
  `PCREC_ENGINE_DFA`. The unanchored/attempt split itself is plan row
  `[OS-4]`'s subject.
- `RX_DFA_PREFILTER` names the candidate-start mechanism, one of `"none"`,
  `"memchr"`, `"byte-class"`, `"memchr-bounded"`, `"byte-class-bounded"`.
  The `-bounded` pair is `[DD-13]` (b): under a `$`/`\Z`/`\z` view or a word
  context every skip is bounded at `n - 1` and the `memchr` arm loses its
  early-out, so the same candidate table buys measurably less. `"none"`'s
  largest cause is not "no filter was wanted" but **the start state ACCEPTS**
  — `\bx*`, `a*`, `.*`, `$` — where no skip is sound at all, because a skipped
  run is a run of positions at which the pattern owes an empty match.
  MEASURED over the corpus (2,772 patterns, `tests/codegen/run_dfa_stamps.sh`,
  2026-08-25). **995 DFA artifacts**: `none` 380, `memchr` 327, `byte-class`
  176, `memchr-bounded` 61, `byte-class-bounded` 51; `unanchored` 811 /
  `attempt` 180 / `empty` 4. **1,263 VM hybrids** (§3.1): `memchr` 825,
  `none` 264, `byte-class` 137, `memchr-bounded` 20, `byte-class-bounded` 17;
  `unanchored` 1,071 / `attempt` 188 / `empty` 4. **Every artifact that
  contains a DFA scan** (2,258): `memchr` 1,152, `none` 644, `byte-class` 313,
  `memchr-bounded` 81, `byte-class-bounded` 68; `unanchored` 1,882 / `attempt`
  368 / `empty` 8. The remaining 225 VM artifacts are non-hybrid and carry
  neither macro; 289 corpus patterns are refused under `--features all`.

- `RX_DFA_TABLE` (`[OPT-3]`, 2026-08-26) names the ENCODING of that scan's
  transition table, one of `"premultiplied"`, `"indexed"`, `"mixed"` or
  `"none"`. `docs/spec/match_api.md` §6.3 states the value set; §2.13 above
  is the axis, and `docs/design/premultiplied_dfa_table.md` the design.
  `"none"` is not a failure: `"attempt"` scans have no numeric transition
  table at all (their states are labels and a step is a computed `goto`),
  and neither does `"empty"`. Unlike `RX_DFA_SCAN` and `RX_DFA_PREFILTER`
  it has **no `rx_info` mirror** — §3.2's mirrors were a separate D40
  decision for a header-less consumer, no such consumer reads them yet, and
  match_api.md §6.3 states the trigger that would make this one owed.

`RX_ENGINE_WHY` is still VM-only, and that is about the FACT rather than the
engine: it names the construct that FORCED the VM, and a DFA artifact was not
forced — `rx_info.engine_why` is `NULL` there for the same reason.

### 3.1 A VM HYBRID carries these too (`[DD-13c]`, 2026-08-25)

The stamps belong to the MECHANISM, not to the artifact kind that usually
carries it, and the §6.1 hybrid is where those two come apart. A hybrid is a
VM artifact whose `fit.prefilter` is on: it INLINES the DFA emitter's own
scan as a `static` function and runs it ahead of the program, tables, D11
bound and candidate-start filter included. That is the mechanism the email
specimen's ~23x actually comes from — and until `[DD-13c]` it was the one
artifact kind that stamped nothing about it, so a bench harness could bucket
every artifact by scan shape EXCEPT the ones where the scan does the work.

```
$ build/pcrec -p rx -o - -- 'a(b|c)+d' | grep -E '^#define RX_(ENGINE|VM_PREFILTER|DFA_)'
#define RX_ENGINE "vm"
#define RX_ENGINE_WHY "capture group at pattern offset 1"
#define RX_VM_PREFILTER "hybrid"
#define RX_DFA_SCAN "unanchored"
#define RX_DFA_PREFILTER "memchr"
#define RX_DFA_TABLE "premultiplied"
```

The two prefilter macros are **two different selections**: `_VM_PREFILTER`
says whether the VM runs a capture-erased DFA ahead of its program at all,
`_DFA_PREFILTER` says what candidate-start filter that scan itself carries.
A non-hybrid VM artifact carries neither `_DFA_*` macro — the relation is an
IFF and `docs/spec/match_api.md` §6.3 (a) states it as one.

### 3.2 …and `rx_info` carries the same two facts at RUN time (`[DD-13c]`)

**For the bench and every other header-less consumer.** The macros above are
preprocessor-only, so a harness that `dlopen`s an artifact, an FFI binding, or
a tool walking several `<prefix>_info` symbols in one image could not read
them at all — it had to parse the emitted C. Since `[DD-13c]` (Frank's D40
addendum) `struct rx_info` carries two more fields, appended at the END of the
struct beside `engine` and `engine_why`:

```c
const char *scan;       /* "unanchored" | "attempt" | "empty", or NULL */
const char *prefilter;  /* the candidate-start mechanism; never NULL */
```

They mirror `<PREFIX>_DFA_SCAN` and `<PREFIX>_DFA_PREFILTER` exactly, are
written from the SAME emitter derivation (never a second computation), and
`tests/codegen/run_dfa_stamps.sh` asserts field == macro on every compiled
artifact of both engines. `scan` is `NULL` on a VM artifact that is not a
hybrid, and **a non-NULL `scan` on a VM artifact IS "this is a hybrid"** — the
runtime reading of `RX_VM_PREFILTER "hybrid"`, which had no `rx_info` mirror
before. `prefilter` is never `NULL`: it reads the DFA's vocabulary wherever
`scan` is non-NULL and the VM's `"none"` where it is not. The full rule, with
the reason the string `"hybrid"` never appears in the field, is
`docs/spec/match_api.md` §6.

**A BENCH ROW CAN NOW BE BUCKETED WITHOUT READING THE ARTIFACT'S SOURCE**, on
either surface, for every artifact kind — which is the gap `[DD-13]`'s row
opened against and `[DD-13c]` closes for the hybrid.

**This is not a `-f` axis and has no CLI spelling.** It is observability of a
selection the compiler makes on its own, which is what D46 asks for; there is
no knob here to deny or force. `tests/codegen/run_dfa_stamps.sh` holds each
stamp to the loop it names (every verdict derived from the emitted matcher
text, then compared against the macro) and asserts the hybrid iff in both
directions. `rx_info.abi` moved `3` -> `4` with `[DD-13]`'s stamps and
`5` -> `6` with `[DD-13c]`'s (`[OPT-1]`'s two-tier entry took `4` -> `5` in
between). [DD-13]'s was a D76 event only — the version of
the emitted SCAFFOLDING, not of the struct. [DD-13c]'s is both: the same kind
of scaffolding change PLUS a real (append-only) struct growth, §3.2.

§2.5 (`-fno-prefilter`) governs `RX_VM_PREFILTER`, which is the VM's own
axis; the DFA scan's candidate-start filter is a different vocabulary and a
different stamp (`RX_DFA_PREFILTER`, this section).

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
| `flags` bit `PCREC_NO_TIERED_ENTRY` | `-fno-tiered-entry` | §2.12 |
| `flags` bit `PCREC_NO_PREMUL_TABLE` | `-fno-premul-table` | §2.13 |
| `unroll_k` (`PCREC_UNROLL_K_DEFAULT` = 0) | `--unroll=K` | §2.10 |
| `engine` (`PCREC_ENGINE_AUTO`/`_DFA`/`_VM`) | `--engine=E` | §2.11 |

`step_budget`, `work_budget` and `frame_capacity` are resource-bound
fields, not strategy-selection tuning axes — `docs/spec/limits.md` is
their home, not this document.
