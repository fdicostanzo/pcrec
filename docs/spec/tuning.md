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
strategy that cannot be denied cannot be differentially tested"). **Almost
every** bit-flag axis in §2 is D47.3's family — the deny-only ones, the force
pair (§2.5), and the two engine-selecting denials — and all but one of those
exist **because** they have a differential that checks this exact
claim directly: compile the same pattern twice, once with the strategy and
once without, link both into one driver, and sweep subjects comparing
span, every capture slot, and the failure surface. The exception is §2.5's
force pair, the family's only one — its own correctness already rides
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

## 2. The axes

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
overflow text §2.11 states, not `-fno-prefilter`).

**[OPT-4] (2026-08-29) THE DROP IS NOW THE SECOND RUNG, NOT THE FIRST.**
Before the prefilter is dropped, the fallback tries ONE more thing: building
it from the count-collapsed language (§2.17). The ground for dropping it was
that rebuilding would be the IDENTICAL machine that just overflowed — true of
the pattern's own language, false of the collapsed superset, whose size is a
function of the pattern's STRUCTURE alone. So an overflow witness can now come
out `RX_VM_PREFILTER "hybrid"` with
`RX_VM_PREFILTER_LANG "count-collapsed"` and
`RX_VM_PREFILTER_LANG_WHY "dfa overflow retry, exact nfa N"`, beside an
`RX_ENGINE_WHY` that still names the overflow — which is what tells a reader
which rung won. `RX_VM_PREFILTER "none"` remains the outcome when the
COLLAPSED machine overflows too, and when `-fno-prefilter-collapse` is passed
(a caller who denied the axis is not given it by the back door). `-fprefilter` itself is
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

**THE COST BOUND** ([OPT-4], 2026-08-29: **at most TWO**, was one): the
fallback compile is at most two refused DFA builds dearer than asking for
`--engine=vm` directly, and the second is bounded by the first. The retry is
now a two-rung ladder — build the prefilter from the count-collapsed language,
and only if THAT overflows too, drop it (§2.5) — and the collapsed machine's
NFA is strictly smaller than the exact one this compile already built, with a
size that does not depend on any repeat count. A caller who passes
`-fno-prefilter-collapse` skips the new rung entirely and keeps the original
one-build bound. The sentence below describes the second rung, which is
unchanged. The overflowing build's own
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

### 2.14 `-fno-offset-skip` — `PCREC_NO_OFFSET_SKIP` (bit 16)

**ANSWER-IDENTITY-preserving.** The axis changes WHERE the forward DFA
scan starts stepping, not which strings match: every test it adds is a
NECESSARY condition of a match beginning at that position, so it refuses
only starts the stepped scan would refuse.

**What it controls.** A DFA artifact's forward scan filters candidate
match starts on the byte AT the candidate — one `memchr` for a single
value, a 256-entry bitmap walk for a set (§2.5's neighbourhood, and the
five older `<PREFIX>_DFA_PREFILTER` values). With this axis ON the
compiler may instead derive, from the pattern's own prefix, a SET of
`(offset k, byte-set)` tests every match must satisfy — for
`\d{4}-\d{2}-…` a digit at offset 0 AND a `-` at offset 4 — scan for the
rarest member with one `memchr` at its offset, verify the others on each
candidate, and resume from a failed candidate one position later. Denying
it emits the offset-0 filter exactly as it shipped before `[OPT-K]`.
Default: the offset-k form is ON, subject to the selection below.
Deny-only, `§2.13`'s shape rather than `§2.5`'s force pair: the compiler
picks one k-set per artifact from its own cost model, so there is nothing
to address and nothing to force.

**Reason it exists.** `pcrec-bench`'s `loglines@0.1` measured pcrec
**31.8× / 12.2× / 10.1× behind PCRE2-JIT** on `stack-frame`, `uuid` and
`iso-ts`, and the cause was one fact all three share: the byte at offset
0 is in every log line (a digit, a hex digit, a word character), so the
offset-0 filter passed almost every position to a transition loop
measured at **10.7 cycles/byte** (`[OPT-3]`). The selectivity of those
patterns is a CONJUNCTION over offsets, which is what the JIT scans for
and what this axis derives. It is also the bisect lever for the
optimization and the build its identity comparison uses as its control.

**The selection, and it is not this flag.** Whether an artifact gets an
offset-k form is decided at generation time, per artifact, by a cost
model over a static byte-frequency prior
(`docs/design/offset_k_skip.md` §4): the form is adopted only when it is
predicted at least **2×** cheaper than the offset-0 filter, and the
scan offset must be a single byte value unless it is offset 0. Offset 0
is always a member of the set. Neither the k-set cap (**4**) nor the
walk bound (**24** offsets) can refuse a pattern — exceeding either
declines an optimization — which is why `docs/spec/limits.md` says
nothing about them.

**The stamps.** `<PREFIX>_DFA_PREFILTER` gains the values
`"offset-set"` and `"offset-set-bounded"`, and the new sibling
`<PREFIX>_DFA_PREFILTER_OFFSETS` names the chosen offsets with `*` on
the scanned one (`docs/spec/match_api.md` §6.3). **MASKED out of
`rx_info.flags`** (`src/gen/emit_dfa.c`'s `strategy_denials`), for the
mask's own reason: it changes no answer, so two artifacts that behave
identically must not differ in their reflection surface over it, and
what the emitter DID is already reported by the two stamps. Re-run and
verified at this commit:

```
$ build/pcrec -p rx --no-captures --features all -o - \
    -- '\d{4}-\d{2}-\d{2}' | grep -E '^#define RX_DFA_PREFILTER'
#define RX_DFA_PREFILTER "offset-set"
#define RX_DFA_PREFILTER_OFFSETS "0,4*"
$ build/pcrec -p rx --no-captures --features all -fno-offset-skip -o - \
    -- '\d{4}-\d{2}-\d{2}' | grep -E '^#define RX_DFA_PREFILTER'
#define RX_DFA_PREFILTER "byte-class"
#define RX_DFA_PREFILTER_OFFSETS "none"
```

and the SELECTION declining on a pattern with no selective offset — the
same command on `\b[0-9a-f]{32}\b` reads `"byte-class-bounded"` /
`"none"` with the flag ABSENT, which is the axis's own negative control.

**The denied build and the pre-`[OPT-K]` compiler's output differ by
exactly one line**, the `_DFA_PREFILTER_OFFSETS` stamp every `abi` 9
artifact carries. That is the whole of the axis's footprint on a pattern
it declines, and it is what makes the denied build the identity
comparison's control.

### 2.15 `-fno-anchored-dfa` — `PCREC_NO_ANCHORED_DFA` (bit 17)

**ANSWER-IDENTITY-preserving.** The axis changes which MACHINE
`<prefix>_match` runs, not which strings match: the form it enables runs
the pattern's own automaton from `ctx->pos`, which is exactly the
question the entry promises to answer (`docs/spec/match_api.md` §3.2).
The argument that the two forms report the same length on every input is
`docs/design/anchored_match_unwrapped.md` §3.

**What it controls.** A DFA artifact's `<prefix>_match` and
`<prefix>_match_caps` used to run the artifact's ordinary UNANCHORED
search and reject any match whose start is not `ctx->pos`. With this axis
ON the artifact carries a THIRD machine instead — the same subset
construction over the same NFA, rooted at the pattern's own first state
rather than at the start-anywhere self-loop — and runs it forward from
`ctx->pos` with no reverse pass and no candidate skip. Denying it emits
the search-and-filter bodies exactly as they shipped before `[ENG-ABS]`,
and builds no third machine at all. Default: the anchored form is ON,
subject to the selection below. Deny-only, §2.13's shape rather than
§2.5's force pair: the compiler emits the form wherever the machine fits
its caps, so there is nothing to address and nothing to force.

**Reason it exists.** `[OPT-2]` STEP 2
(`docs/dev/opt2_anchored_match_measurement.md`) measured the REVERSE PASS
at **~50 % of the DFA's cost on every matching subject** of the bench's
compliance set: deleting it takes matching subjects from **2.077× behind
the VM to 1.046×** and short valid emails from **1.207× behind to
0.571×**. Under the search-and-filter form that pass exists only to
recover a start the caller already gave. The second motivation is
`[ENG-ABS]`'s original one: a FAILING match-here can skim the remainder
of a long subject hunting a later match the filter then discards, where
an anchored body stops at the first divergent byte. It is also the
bisect lever for the optimization and the build its identity comparison
uses as its control.

**The selection, and it is not this flag.** Whether an artifact gets the
anchored form is decided at generation time, per artifact: the engine
must be the one-pass unanchored DFA (a `^`- or `\G`-bearing pattern is on
the per-start attempt engine and keeps the old form), the artifact must
not be the empty engine, and the anchored machine must BUILD inside the
DFA caps. A machine over a cap DECLINES an optimization — it never
refuses a pattern, and the mandatory machines are built first so the
shared subset-element budget cannot be spent on an optional one — which
is why `docs/spec/limits.md` says nothing about it.

**The stamps.** `<PREFIX>_DFA_MATCH` names the chosen form
(`"unwrapped"` / `"search-filter"`) and `rx_info.match_form` mirrors it
(`docs/spec/match_api.md` §6.3). **MASKED out of `rx_info.flags`**
(`src/gen/emit_dfa.c`'s `strategy_denials`), for the mask's own reason:
it changes no answer, so two artifacts that behave identically must not
differ in their reflection surface over it, and what the emitter DID is
already reported by the stamp. Re-run and verified at this commit:

```
$ build/pcrec -p rx --no-captures --features all -o - \
    -- 'foo[0-9]+bar' | grep -E '^#define RX_DFA_MATCH'
#define RX_DFA_MATCH "unwrapped"
$ build/pcrec -p rx --no-captures --features all -fno-anchored-dfa -o - \
    -- 'foo[0-9]+bar' | grep -E '^#define RX_DFA_MATCH'
#define RX_DFA_MATCH "search-filter"
```

and the SELECTION declining on a pattern the other engine owns — the
same command on `^foo` reads `RX_DFA_SCAN "attempt"` and
`RX_DFA_MATCH "search-filter"` with the flag ABSENT, which is the axis's
own negative control.

**The denied build and the pre-`[ENG-ABS]` compiler's output differ by
exactly two lines**, the `_DFA_MATCH` stamp every `abi` 10 DFA artifact
carries and the `rx_info.match_form` field every `abi` 10 artifact
carries. That is the whole of the axis's footprint on an artifact it
declines, and it is what makes the denied build the identity
comparison's control — a BYTE-IDENTITY claim against the older compiler
would be false, which is D81 (selection facts are stamped
unconditionally) rather than an oversight.

### 2.16 `-fno-size-term` — `PCREC_NO_SIZE_TERM` (bit 18)


**ANSWER-IDENTITY-preserving for match results and captures — and NOT for
the give-up surface.** The axis changes which unroll factor `K` the
counter rung is emitted at. `K` is that rung's chunking factor: the rung
compiles a bounded repeat to `ceil(n/K)` body copies plus a trailed
counter whose arithmetic makes the realized iteration count exact at any
`K >= 1`, so the span and the capture slots are identical at every `K`.
What is NOT identical is what the artifact GIVES UP on: measured on
`((a)|ab){12}c`, the minimum `--step-budget` that completes runs 89 at
`K=1` to 110 at `K=8`, the minimum `--backtrack-frames` is 39 at `K=1`
against 28 at `K=8` (descending `K` RAISES the frame requirement), and
`<PREFIX>_TRAIL_FRAMES` runs 62 down to 51. Under the DEFAULT budgets the
answers are identical; see `limits.md` §7.

**What it controls.** With the axis ON (the default), an artifact whose
COUNTER rung is live and whose emitted size exceeds
`PCREC_SIZE_TERM_THRESHOLD` has its `K` chosen by re-emitting a descending
ladder and taking the smallest emitted node count, kept only if it saves
at least 25 % of the bytes. Denying the axis leaves `K` at `--unroll=K`
or `PCREC_DEFAULT_UNROLL_K`, which is what the compiler emitted before
[ART-SIZE].

**What it does NOT control: the two emitted-size caps.** `-fno-size-term`
denies the SELECTION and never reaches
`PCREC_MAX_VM_EMIT_CODE_BYTES`/`PCREC_MAX_EMIT_BYTES` — a safety refusal a
flag can turn off is not one (D84 ruling 1). A denied build can therefore
still be refused for size, and correctly: denying the term removes the
mechanism that would have made the artifact smaller, it does not make an
oversized artifact acceptable. To accept a larger artifact, RAISE a cap
(`--max-emit-bytes=N`, `--max-emit-code-bytes=N`, raise-only) — see
`limits.md` §8, "Handling an oversized artifact".

**The stamp** is `<PREFIX>_UNROLL_K` (the chosen `K`) beside
`<PREFIX>_UNROLL_K_WHY`, which has SEVEN values — `default`, `option`,
`denied`, `size-model`, `size-model-declined`, `cap-rescue`,
`capacity-declined` — because "the term did not run" has five
distinguishable reasons and a check must be able to tell them apart. Both are unconditional on every VM artifact
(D81).


### 2.17 `-fno-prefilter-collapse` / `-fprefilter-collapse` — `PCREC_NO_PREFILTER_COLLAPSE` (bit 19) / `PCREC_FORCE_PREFILTER_COLLAPSE` (bit 20)


**ANSWER-IDENTITY-preserving, in both directions and including the give-up
surface.** The axis changes only the LANGUAGE the VM hybrid's inlined DFA
recognises, and that DFA is a FILTER: what it owes the VM is a sound
rejection and a lower bound on the match start, both of which a superset
supplies, with the VM re-deriving the answer from every candidate it is
handed (`§2.5`'s hybrid, and `match_api.md` §6.3's H1/H2/H3). The prefilter
is answer-identity-preserving by D46's rule; this is a selection WITHIN it.

**What it controls — FRANK'S RULING B, 2026-08-29.** The DEFAULT builds the
prefilter from the pattern's OWN language. The count-collapsed superset —
every `A_REP` with `rmin > 1` or `rmax > 1` lowered as `X{min(rmin,1),}`, a
superset whose proof never mentions `n`, so the machine and the artifact stop
scaling with the count — is chosen only as an ATTEMPT in `compile_driver`'s
ladder, when the exact machine cannot be built or its artifact cannot ship:

| rung | trigger | `<PREFIX>_VM_PREFILTER_LANG_WHY` |
|---|---|---|
| [SEL-1] | a DFA STATE cap overflowed, so the alternative is NO prefilter | `dfa overflow retry, exact nfa N` |
| [OPT-4] | an emitted-size cap REFUSED the exact artifact, so the alternative is a REFUSAL | `size cap retry, exact N > cap` |

**[OPT-4.1] (2026-08-30) A RUNG IS DECLINED WHEN THE COLLAPSED LANGUAGE IS
NULLABLE, and this is the one condition under which neither rung above fires
even though its trigger did.** If the collapsed language matches the EMPTY
STRING — `[a-z]{0,32768}` collapses to `[a-z]*` — then it matches at every
position, the filter can never dismiss one, and the artifact pays a scan whose
every answer is "maybe". pcrec builds NO prefilter in that case:

- on the **[SEL-1]** rung the artifact is the one that rung's absence would have
  produced (`<PREFIX>_VM_PREFILTER "none"`), and `<PREFIX>_ENGINE_SEL` reads
  **`"declined-nullable"`** — a value that exists precisely so this outcome can
  be told apart from `"overflowed-dfa"`, where no rescue was available at all;
- on the **[OPT-4] size** rung the artifact ships with no prefilter, which is
  strictly SMALLER than the collapsed one, so the rung still rescues the compile
  and nothing that compiles today stops compiling. `<PREFIX>_ENGINE_SEL` reads
  **`"declined-nullable"`** there too ([LIM-1], 2026-08-30 — this used to read
  `"selected"`, indistinguishable from an ordinary compile; both rungs' nullable
  declines are now one value, `match_api.md` §6.3's own value table), and the
  artifact's `<PREFIX>_VM_PREFILTER "none"` is what records the outcome;
- under **`-fprefilter-collapse`** with no rung the prefilter is kept and built
  from the EXACT language — the flag chooses a language, not whether a filter
  exists — and the artifact stamps `_LANG "exact"` /
  `_LANG_WHY "nullable collapsed language"`;
- **`-fprefilter` is do-or-die and is never silently dropped, and what that
  means differs by rung — stated per rung because the general sentence is
  wrong on one of them.** On the **size** rung it OVERRIDES the decline: the
  collapsed prefilter is built for a caller who demanded one, which is also
  what keeps the promise above, since the only prefilter that fits under the
  cap there IS the collapsed one. On the **[SEL-1]** rung it never reaches the
  decline at all — `-fprefilter` makes that rung ineligible, so the compile
  REFUSES rather than shipping a prefilter-less artifact for a caller who asked
  for one. Either way the request is honoured or refused, never answered with
  its opposite. `-fprefilter-collapse` does NOT override the decline on either
  rung: it chooses a LANGUAGE for a filter, not whether one exists.

MEASURED (pcrec-bench O-10, pin 96e44c2, three sets): where structure survives
the collapse the rung is a 2.2-4.6x win (the `ctx` band, and `level-context`
x4.60); where the collapsed language is nullable it was a 1.2-9.9x LOSS
(`[a-z]{0,32768}`: search x3.57 slower, throughput 1.880 -> 6.899 ns/B,
`t-digits-016k` x1.65 — a subject the filter was expected to dismiss and
cannot). Nullability is what separates the two populations, and it is decided
before any machine is built (`pcrec_minw(root) == 0`, `src/opt/mrl.c`).

**[OPT-4.2] (2026-08-31) THE SAME DECLINE, GENERALIZED TO EVERY PREFILTER —
NOT ONLY THE TWO RUNGS ABOVE.** [OPT-4.1]'s gate is scoped to a ladder
ATTEMPT: it only ever asks about the collapsed language, because the two
rungs above are the only places pcrec offers one. But the ORDINARY hybrid —
`auto` (or forced `--engine=vm`) with no cap ever hit — builds the pattern's
own EXACT prefilter unconditionally, and that filter is exactly as useless
when the EXACT language is nullable as a collapsed one is: `(a|b){0,30000}`
matches the empty string at every position (its own language, not merely its
collapsed superset), and until this row landed the ordinary hybrid still
built and shipped that filter regardless. The population GREW when [OPT-5]'s
scan edge landed: patterns like this one that used to be REFUSED by the size
cap (and so took the [OPT-4] size rung's own decline above) now compile
comfortably inside every cap and never reach a rung at all — MEASURED
2026-08-31, `(a|b){0,30000}`: 34,522 B, hybrid/exact.

So the decline is now asked on EVERY prefilter this compiler can build, rung
or not: `<PREFIX>_ENGINE_SEL` reads **`"declined-nullable-default"`**
(`match_api.md` §6.3's own value table — a NEW value, kept separate from
`"declined-nullable"` rather than folded into it, since the two answer
different questions about different populations: a rung OFFERED and REFUSED
a rescue vs. an ordinary compile that never had a rung to begin with) and
`<PREFIX>_VM_PREFILTER` reads `"none"`, exactly as the rung-scoped decline's
artifact does. The same three overrides apply, and `-fprefilter` is the only
asymmetric one for the same reason: it outranks the decline (the artifact
still gets its exact prefilter, on demand), while `-fno-prefilter` and
`-fprefilter-collapse` change nothing about this outcome — the first already
reaches the identical artifact by its own door, and the second's axis (which
LANGUAGE a filter recognises) does not apply once no filter is going to be
built at all.

MEASURED (pcrec-bench O-10, the analogous collapsed shape): the same 1.2-9.9x
loss the collapsed-language decline exists to avoid, since the mechanism is
identical — a filter admitting a zero-length match at every position can
dismiss none of them, whether that filter's language came from the pattern
directly or from a count-collapse. The bench re-measures its `cls-*` hybrid
cells after this lands; their prior 1.2-9.9x loss is the predicted win.

**A NAMED RESIDUAL, so a reader does not mistake this predicate for the whole
question** (`docs/dev/decisions.md` D77 — build under measurement). Nullability
is not the only reason a rescue can fail to pay. A WHOLE-SUBJECT-anchored form
(`(?:P)\z`) whose plain form is DFA-selected is rescued only in the ANCHORED
regime, so its collapsed prefilter can dismiss but is never reached by an
unanchored search: pcrec-bench measured four such cells (`cls-upto-16384`,
`cls-lazy-16384`, `nest2-64`, `nest3-16`, `\z` forms only) as FLAT, costing
+376…+4,560 bytes of `.so` for no movement in either direction. Two of those
four are non-nullable and keep their rescue under the rule above; they are
LEFT ALONE deliberately. **A measured FLAT is not a loss**, and a rung that
buys nothing but bytes is revisited only if a LOSS appears — at which point the
question is the anchored regime's reach, not this predicate.

**THERE IS NO STATE-COUNT KNEE.** An earlier design collapsed whenever the
exact NFA exceeded a measured budget; it was reversed on a corpus regression
(`docs/design/prefilter_count_independence.md` §10a) and
`PCREC_PREFILTER_EXACT_NFA_STATES` is deleted with deliberately nothing in its
place — under ruling B the emitted-size caps are the only quantity that
decides.

**WHAT THE TWO FLAGS DO.**

- `-fprefilter-collapse` collapses wherever a collapsible repeat exists AND the
  collapsed language is not nullable ([OPT-4.1] above; a nullable one is
  declined and stamped, and the artifact keeps its exact prefilter),
  regardless of size or of any rung. It is the ONLY route to literal
  count-INDEPENDENCE, and it is where the costs tabulated below live.
  MEASURED (K39): under it `((a)|b){0,400}c` and `((a)|b){0,4000}c` emit the
  same number of lines, where at the default the second is roughly 2.5x the
  first.
- `-fno-prefilter-collapse` denies BOTH rungs. On a pattern whose exact build
  succeeds it changes nothing and the artifact is byte-identical; on one that
  needed a rung it turns a compile into a REFUSAL, or a prefilter into none.
  **Observing that refusal is the main thing this flag now buys a caller** —
  someone who would rather be told their pattern is oversize than be handed a
  superset prefilter.

**TWO CONJUNCTS ARE CORRECTNESS AND NEITHER FLAG REACHES THEM.** The collapse
never applies when (a) these machines' sole customer is not the VM's prefilter
— i.e. when the DFA is the ENGINE, where a superset would be a miscompile — or
when (b) the pattern has no collapsible counted repeat, in which case the
collapsed lowering IS the exact one. `-fprefilter-collapse` on such a pattern
is HONOURED and vacuous, and the artifact says so
(`_LANG_WHY "no counted repeat"`).

**[OPT-4.1] ADDS A THIRD CONJUNCT THAT IS PERFORMANCE RATHER THAN CORRECTNESS,
AND ONE FLAG DOES REACH IT.** The nullability decline above is not a soundness
rule — a nullable collapsed prefilter would still answer correctly, it would
just never dismiss anything — so unlike the two conjuncts in this paragraph it
is overridable, by `-fprefilter` and by `-fprefilter` alone. The distinction is
worth keeping straight: no flag can make pcrec build a superset prefilter for
the DFA ENGINE, and every flag can be told to build a useless one.

**WHY THE EXACT LANGUAGE IS THE DEFAULT, stated because it is a real trade
and the trade went the other way once.** The exact prefilter is a SHARPER
filter: it seeds the VM at the true leftmost start where the collapsed one
seeds a lower bound the VM must walk forward from, and — because a superset's
span END is not an upper bound (`match_api.md` §6.3, H3) — a collapsed
artifact carries no `<PREFIX>_VM_PRUNE_CEILING "prefilter-window"`, reading
`subject-end` instead. Both cost match time on some subjects; the second also
costs step-budget headroom (see the fourth cost below). What the collapse buys
is size, and under ruling B it is spent only where the alternative is a
refusal or no prefilter at all.

**THE COSTS BELOW ARE `-fprefilter-collapse`'s, NOT THE DEFAULT'S** — that is
what Frank's ruling B changed, and it is why this table now sits under the
FORCE flag. Under the knee default these landed on 23 corpus artifacts that
compiled fine; under ruling B they land only where a caller asked for them, or
on the two ladder rungs, where the alternative is a refusal or no prefilter at
all. MEASURED 2026-08-29, gcc 15 `-O2`, one box; every pair returned the
IDENTICAL answer — same match count, same span — which is the axis being
answer-identity-preserving (D46) at an unbounded step budget. Read the first
row before passing the flag:

| case | collapsed (default) | exact (`-fno-prefilter-collapse`) |
|---|---|---|
| **worst case**, `((a)\|b){0,400}c` on 100,000 `a` then `c` | 9.24 s, **99,601 VM attempts**, 38,776 B | 0.000011 s, **1 attempt**, 55,069 B |
| `(ab){300}` find-all over 64 KB of `ab` | 0.266 s, 246 attempts/search, 34,699 B | 0.006 s, 109 attempts/search, 67,471 B |
| `(ab){300}` find-all over 66 KB that never matches | 0.089 s, 66,001 attempts | 0.006 s, **0 attempts** |
| `((a)\|ab){0,100}c` find-all over 64 KB that matches | 0.028 s, 1,300 attempts, 56,675 B | 0.019 s, 1,300 attempts, 64,817 B |
| `((a)\|ab){0,100}c` over 64 KB that never matches | **0.000006 s** | 0.000016 s |

**THE TWO COSTS ARE SEPARABLE AND THESE ROWS SEPARATE THEM.** Rows 2 and 3
are a pattern whose artifact reads `<PREFIX>_VM_PRUNE_CEILING "none"` under
BOTH languages, so their whole difference is the lost sharp start — the VM
verifying candidates the exact machine would never have offered. Row 4 is the
opposite control: the attempt count is IDENTICAL at 1,300, so its 1.5× is
entirely the lost `"prefilter-window"` ceiling.

**THE TRADE IS NOT ONE-DIRECTIONAL.** Row 5 is a subject the prefilter
rejects outright under either language, and there the collapsed artifact is
~2.7× FASTER, because the smaller DFA scans the subject quicker. A caller
whose traffic is mostly non-matching may be better off at the default even
where a matching subject would favour the exact machine.

**The first row is the shape to worry about**: a long run of the repeat's
body followed by the terminator, where the exact reverse machine names the
true start and the collapsed one names 0. It is the case the design note
predicted before the code was written
(`docs/design/prefilter_count_independence.md` §7.1) and it is worse in
practice than "quadratic where the exact prefilter is linear" reads on the
page.

**AND A FOURTH COST, WHICH IS WHY THIS IS NO LONGER THE DEFAULT.** The lost
`prefilter-window` ceiling does not only make matching slower: it changes which
patterns fit inside a **step budget**. `(a{1,3}){65}` on a long run of `a`s
answers `0,100 90,100` in 0.00 s with the exact prefilter and returns
`PCREC_ERR_STEPS` after 13.34 s with the collapsed one. Answer identity is
preserved in D46's unbounded sense — and `make test-axes` is right to keep
passing — but the step budget is a documented caller-visible bound (DD-2/D22).
The caller does not get a slower answer; they get no answer. That measurement,
found on a base-tier corpus cell by the merge battery, is what reversed the
default (design note §10a).

**The stamp** is `<PREFIX>_VM_PREFILTER_LANG`, `"exact"` or
`"count-collapsed"`, emitted exactly where `<PREFIX>_VM_PREFILTER` reads
`"hybrid"` — an artifact with no prefilter names no language. It reports
what was BUILT, so a request that changed nothing stamps `"exact"`.

**And `<PREFIX>_VM_PREFILTER_LANG_WHY` beside it** (D81's `_WHY`
convention), because `"exact"` alone does not say which of several quite
different situations produced it. SIX values, emitted on the same
condition as the line above (the pre-ruling-B budget value `"exact nfa N > B"`
is GONE with the knee it named — the emitter has not written it since ruling B,
and this table carried it stale until [OPT-4.1] removed it):

| value | meaning |
|---|---|
| `"forced"` | `-fprefilter-collapse`: the caller asked for the collapsed language on a pattern that had something to collapse, and no rung was involved |
| `"exact"` | the pattern's own language — the DEFAULT outcome under ruling B |
| `"no counted repeat"` | nothing to collapse: this pattern's collapsed language IS its exact one. The state `-fprefilter-collapse` is honoured but vacuous in, kept distinct from `"exact"` so a caller who passed the flag knows which of the two happened |
| `"nullable collapsed language"` | [OPT-4.1]: there WAS something to collapse and the collapse was DECLINED, because the collapsed language matches the empty string and such a filter can never dismiss a position. Kept distinct from `"no counted repeat"` for that value's own reason — a caller who passed `-fprefilter-collapse` needs to know the flag reached a POLICY, not a vacuity. Reachable only where a prefilter still exists to stamp; on a ladder rung the same decline leaves none, and `<PREFIX>_ENGINE_SEL "declined-nullable"` is where that outcome is recorded instead |
| `"dfa overflow retry, exact nfa N"` | [SEL-1]'s rung: this pattern's DFA overflowed a STATE cap and the collapsed language is what stands between it and no prefilter at all. `N` is the EXACT machine's size, i.e. the scale of what the collapse avoided |
| `"size cap retry, exact N > cap"` | [OPT-4]'s rung: an emitted-size cap REFUSED the exact artifact. `N` and `cap` are EMITTED BYTES, not NFA states — that is the comparison that caused the retry, and a reader deciding whether to raise a cap instead needs it |

**THERE IS NO `"denied"` VALUE, and its absence is a measurement rather than an
oversight.** Under ruling B `-fno-prefilter-collapse` denies the two ATTEMPTS.
On a pattern whose exact build succeeds it changes nothing, so the honest stamp
is whatever the default stamps — the byte-for-byte recovery promise. On a
pattern that needed an attempt it turns a compile into a REFUSAL or a prefilter
into none, and neither of those leaves an artifact carrying this macro. A value
no witness can reach is a value that should not exist.

The two lines are two readers of one derivation, written at
`src/core/compile.c`'s build gate: `prefilter_lang_why` and
`prefilter_collapsed` cannot disagree, because the ladder that sets the reason
branches on the decision it just made rather than re-walking its conjuncts.
The last two values above are exactly the ones that read `"count-collapsed"`
at the default; `"forced"` is the third, and it is the caller's.

**There is no budget to document.** `PCREC_PREFILTER_EXACT_NFA_STATES` was the
knee this section used to describe and it is deleted — see "What it controls"
above and `docs/design/prefilter_count_independence.md` §10a for the regression
that removed it.


**[OPT-4.2] STRUCTURAL RETIREMENT (2026-09-01): the `_LANG_WHY` value
`"nullable collapsed language"` is no longer reachable.** The collapse
X{m,n} → X{min(m,1),} introduces nullability only when m == 0 or X is
itself nullable — and in both cases the EXACT language is nullable too, so
the [OPT-4.2] general decline (or the rung decline, which emits no
prefilter and therefore no `_LANG` / `_LANG_WHY` at all) fires first.
Verified structurally on both sides (pcrec-bench measured ten shapes, none
reaches it; our own reachability witnesses became `declined_default`
rows at the [OPT-4.2] merge for the same reason). The value string stays
documented as HISTORICAL; nothing emits it. Re-opens only if either side
finds a reachable witness — the argument above says where to look (a
collapsed-nullable language whose exact language is NOT nullable, which
the identity makes empty).

### 2.18 `-fno-scan-edge` — `PCREC_NO_SCAN_EDGE` (bit 21)

**What it controls.** Whether a DFA machine's *counted class runs* are
collapsed into **scan edges**. A run here is a maximal sequence of states that
differ in nothing but how many bytes of ONE fixed class have been counted —
every one of them leaving by the same door on every other byte, and every one
of them carrying the same accept bit. `[a-z]{0,16384}`'s forward machine is
one such run of 16,384 states plus the state that has counted them all;
`[a-z]*` and `[a-z]+` are the unbounded one-state form; `[0-9]{16}` is a run
of sixteen. The pass is `src/opt/scanedge.c` and its header carries the exact
criterion and its preconditions — five in the header, three more stated at
their own sites: (6) a head may not be another state's position-VIEW target,
(7) two chains that link must have their heads in ascending order, and
(8) ([OPT-EDGE] STEP 1, narrowed at STEP 1.1) a head may not be a state any
SEED family names **on a machine whose candidate-start prefilter writes the
state variable** — the `offset-set` pair, whose skip lands past bytes that
LEAVE the start state and must therefore re-seed. The other prefilter forms
skip bytes the machine provably stays parked on and write nothing.

Precondition (5)'s threshold — the shortest bounded run worth collapsing — is
the `PCREC_MIN_SCAN_CHAIN` row of `pcrec --list-limits` (`2` states, a
`selection knee`, no lever). It was re-measured against the STEP 1.1 loop
rather than inherited: `edge` against `-fno-scan-edge` on the same pattern is
not separated by more than the per-round range at `m` = 3, 4 or 8; the
`m` = 2 cell was UNSTABLE on the 2026-09-04 run (median edge/no-edge 1.78,
IQR 0.87, bimodal rounds — measurement instability, not a measured effect;
re-measurement owed, docs/dev/lanes/edge2_report.md §9.3), so D77's
"no gap, no move" leaves it at 2, and the unconditional SIZE win (the chain's
interior states are deleted) is what admits `m` = 2 at all.

**What the artifact does instead.** One `if (state == K) { … }` block per
edge, counting the class's bytes in a loop whose only carried value is the
cursor:

```c
if (forward_state == 0) {
    unsigned long scan_run_length = 0;
    while (scan_position < subject_length && scan_run_length < 16UL
           && (unsigned char)(subject[scan_position] - 48) <= 9)
        { scan_position++; scan_run_length++; }
    if (scan_run_length == 16UL) { forward_state = 2; last_accept_position = scan_position; }
}
```

**WHERE THAT BLOCK SITS CHANGED AT [OPT-EDGE] STEP 1, and it is the reason
the axis costs a machine that never takes an edge nothing at all.** Until
then every edge block was on the loop's GENERIC PATH — one
`if (state == K && …)` evaluated on every iteration at every state, so N
edges cost N compares per byte. Since [OPT-EDGE] the machine's edge HEADS are
renumbered to its TOP rows and the loop's ONE existing per-iteration state
test (`is_dead`, which stopped the walk) is widened to a `<prefix>_<m>_is_stop`
that answers "dead OR a head" in the same single unsigned compare. The edge
blocks move onto a path reached only from that test, so the generic path
carries NO per-edge compare:

```c
for (;;) {
    if (<m>_accepts(state)) last_accept_position = scan_position;
  <prefix>_forward_scan_views:
    if (scan_position >= subject_length) break;
    state = <m>_step(next_state, state, byte_class[subject[scan_position++]]);
    if (!<m>_is_stop(state)) continue;            /* the generic path */
    if (<m>_is_dead(state)) break;
    /* … the edge blocks, unchanged … */
    goto <prefix>_forward_scan_views;
}
```

**A SECOND EMITTED SITE READS THE SAME SENTINEL, and it is the loop's ONE
PER-SEARCH TEST rather than a per-byte one.** The state variable is also
written before the loop, by the start seed (§2.x's mechanism 4: a machine whose
interior start states differ by context class initialises it from
`seed_state[byte_class[subject[search_from - 1]]]`, i.e. to any member of the
family). A search that seeds straight onto a head must reach the edge body
without the generic path, so the loop's entry asks the same question the body
does:

```c
if (<m>_is_stop(state) && !<m>_is_dead(state)) goto <prefix>_forward_scan_edge;
```

folded away entirely on a machine with no seed, where the state IS the start
state and the jump is unconditional or absent. **This entry test was an
equality against the start state until [OPT-EDGE] STEP 1.1**, which was exact
only while precondition (8) refused every other seed target as a head; asking
the general question is what lets (8) narrow.

Four consequences a caller can see. The emitted state NUMBERS of an
edge-bearing machine differ from the pre-[OPT-EDGE] compiler's (the heads are
the top rows); each such machine emits one extra accessor, `<prefix>_<m>_is_stop`
(folded to the constant `1` where every state is a head); an artifact with
no scan edge — which includes every artifact built with this flag — is
byte-identical to the pre-[OPT-EDGE] compiler's; and, by precondition (8),
a machine whose prefilter reseeds may decline an edge it would otherwise take.

**WHAT (8) COSTS, MEASURED. At STEP 1 it cost ELEVEN artifacts an edge**, over
every distinct `pattern` line under `tests/` (2,539 compiled by both
compilers), every one a `\b`/`\B` pattern: `(\b\w+\b)`, `(foo\B)`, `\Bfoo\B`,
`\b\K\w+`, `\b\w+\b`, `\b\w+\b$`, `\b\w+\b\z`, `\b\w+\z`, `\b\w\b`, `\bfoo\B`,
`foo\B`. **At STEP 1.1 all eleven get it back**, and the two the STEP 1 census
called hazardous turn out not to be: the edge each of them lost is on the
REVERSE machine, which carries no candidate-start prefilter at all (every
axis-B candidate requires the forward direction), so nothing in that loop can
reseed. **The narrowed (8) has an EMPTY population on today's corpus** — an
artifact compiled with the precondition removed entirely is byte-identical —
because a machine that takes an `offset-set` prefilter has no scan-shaped chain
in its forward machine to begin with. It is kept, exact and cheap, because the
mechanism it guards is real: the reseed genuinely writes the state variable
MID-BODY, after the loop's one stop test has been passed, where nothing can see
it. `src/gen/emit_dfa.c`'s `dfa_form_derive` re-derives the rule from the
machine it is about to emit, so the day the population stops being empty the
pass and the emitter cannot disagree about it silently.

**Why.** `docs/dev/opt5_step0_profile.md` measured the DFA's ordinary step —
`state = next_state[state + class]`, whose load ADDRESS is the value the
previous iteration's load RETURNED — at ~3.62 ns/byte on an in-class letter
run, against 0.60 for pcrec's own VM compiling the identical language. The
difference is not the table lookup and it is not SIMD: it is whether the
loop-carried register FEEDS an address (cheap, pipelined) or is FED BY a load
(serial). A scan edge gives the DFA the VM's own loop shape.

**It is the one DFA axis whose denial changes the MACHINE.** The run's
interior states are DELETED — the edge replaces them — so this axis moves
per-state table sizes as well as emitted code, and the denied build is the
pre-`[OPT-5]` compiler byte for byte. `-fno-scan-edge` restores both the
states and the table walk. No answer moves either way.

**IT IS TWO AXES, and `--list-axes` reports both.** The emitter models the
mechanism at the two levels D82 separates, and a caller reading the axis
registry sees them as `scan-edge` and `scan-body`:

| axis | candidates | question |
|---|---|---|
| `scan-edge` | `scan-edge`, `table-walk` | per STATE: does this state emit an edge at all? **This is the axis `-fno-scan-edge` denies** — the flag removes the first candidate and the ordinary walk selects the fallback. |
| `scan-body` | `range`, `bitmap` | per EDGE: which run-extension body does that edge use? |

**The stamp** is `<PREFIX>_DFA_SCAN_EDGE` (§3 below and `match_api.md` §6.3)
and it reports the **body** axis's chosen object by name: `"range"` when every
edge the artifact carries tests a contiguous byte range (a subtract-and-compare
against two immediates), `"bitmap"` when a class is not contiguous and the test
is a 256-byte membership read — whose load is addressed by *the byte this
iteration read*, never by a previous iteration's result, so the cursor is still
the only loop-carried register — `"mixed"` when the artifact's machines took
both forms, and `"none"` when the region axis chose `table-walk` everywhere.
Like `<PREFIX>_DFA_TABLE` and `<PREFIX>_DFA_PREFILTER` it is a fact about a DFA
SCAN, so a VM HYBRID that inlines one reports it too ([DD-13c]'s (a)/(b)
split).

**A THIRD BODY IS RESERVED AND IS NOT BUILT.** A SIMD run-extension form —
branchless classify plus count-leading-zeros, `studies/simd1`'s measured shape,
plan row `[OPT-SIMD]`'s territory — belongs at the top of the `scan-body`
preference list: a new candidate object and its test, with nothing above the
axis moving (not the criterion, not the deletion, not the stamp's other
values, not the gates). **Its contract is ISA-NEUTRAL by ruling**: it is "a
SIMD run-extension form, per-ISA gated, with the scalar forms always available
as the fallback", never an SSE2 or a NEON slot. Nothing this axis emits today
is ISA-conditional, and `range`/`bitmap` are the portable baseline that keeps
any per-ISA form optional forever.

**AND THE COUNTED SEQUENCE HAS A PERIOD, WHICH IS 1.** The general shape of
this mechanism is a chain whose advance classes CYCLE with period *k* — *k*
singleton classes being a literal STRING, whose body is a counted loop of
constant-length compares, i.e. `(?:ab){1,100}` collapsing the way `[ab]{1,100}`
does. `DState.scan_period` carries that period so the criterion's output is a
periodic sequence rather than a single class baked into the representation;
only period 1 is built, the emitter asserts it rather than assuming it, and a
period-*k* form is then a criterion extension plus a new `scan-body` object
rather than a rewrite. The refusal is clean either way: a chain whose
mid-period states disagree about their exit target is not scan-shaped and takes
the ordinary walk.

**The boundary, stated rather than left to be discovered.** A run is collapsed
only when every one of its states has NO position view (`$`/`\Z`/`\z` select a
different state at `pos == n-1`/`n`, and a scan passes those positions) and an
accept bit that does not vary with the next byte's class (`\b`, `(?m)$`).
Both are DECLINES, both are free on a pattern carrying none of those
constructs, and a declined run compiles exactly as it did before this axis
existed. At most four edges are collapsed per machine — each is a compare on
the loop's generic path, the budget `pick_skip_states` already spends four of
— and the longest runs are taken first. `ENG_ATTEMPT` (a `^`-anchored
pattern) is not eligible at all: its states are code labels and a step is
`goto *targets_K[class]`, so there is no loop-carried table load to shorten,
which is `[OPT-3]`'s own reason for exempting that engine.


### 2.19 `-fno-start-pinned` — `PCREC_NO_START_PINNED` (bit 22)

**What it controls.** Which of two forms `<prefix>_search`'s post-loop block
takes — the compiler calls this **axis J**, and `--list-axes` reports it as
`search-start`.

A DFA search runs TWO scans over the same bytes. The forward one finds where a
match ENDS; a second, backwards one over an independently built REVERSE machine
finds where that match BEGAN, because the forward tables record only where a
match can end and never where the one that ended there started.

For a large family of patterns the second scan's answer is a compile-time
constant. When the forward machine's start state accepts **unconditionally** —
at every position, under every position view, and in every class context — then
a match exists wherever the search begins, and D3's accept-pruning has removed
the start-anywhere self-loop from every accepting closure before the first byte
is read. No later start is ever spawned, so every accept the forward loop
records belongs to a thread that began at `search_from`, and the backwards scan
would necessarily walk back to exactly that position. `[a-z]{0,4096}`, `a*`,
`.*` and `\w*` are all in this family; `abc`, `[a-z]{4096,}` and `(?m)a*$` are
not.

**What the artifact does instead.** The post-loop block becomes two assignments
and a `return 1`, and — the half that buys more than the time — **the reverse
machine is not emitted at all**: no transition, accept or byte-class table, no
stay tables, no scan-edge membership tables, no `<prefix>_reverse_*` accessor
block, and no reverse scan loop.

```c
if (last_accept_position == (size_t)-1) return 0;
if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)search_from;
                     capture_spans[0][1] = (ptrdiff_t)last_accept_position; }
return 1;
```

**The `last_accept_position == (size_t)-1` gate above it is LOAD-BEARING and
is kept.** A search at `startpos > 0` on a machine whose start state depends on
a context byte can begin in a state with no live closure. It records no accept,
and "no match begins here" is the correct answer; deleting the gate would
report an empty match where there is none. The emitted artifact carries that
sentence above the line, and the compiler additionally DECLINES the elision on
any machine with a dead seed state, so the gate is not the only defence.

**Why.** The two scans are the residual factor of roughly two between the DFA
and pcrec's own VM on a counted class run: since `[OPT-5]` STEP 1 both are
cursor loops, so the DFA does exactly twice the VM's work. `docs/design/
opt5_step2_twopass.md` is the design and carries the proof.

**No answer moves either way, and the denied build is a genuine control.**
This is not the usual "the flag changes nothing observable" claim: the denied
build recovers the match start from an INDEPENDENTLY BUILT automaton — the
emitter's own note on the pair is that "the two machines are independent and
need not agree" — where the default build derives it from a compile-time proof
about the forward machine. Nothing is shared but the answer, which is what
makes `make test-axes`'s sweep over this flag a control rather than a build
comparing itself.

**Deny-only**, `-fno-anchored-dfa`'s shape: the compiler takes the pinned form
wherever the predicate holds, so there is nothing for a caller to address and
nothing to force. A machine the predicate declines emits the reverse pass,
which is a SELECTION OUTCOME and never a refusal. **MASKED out of
`rx_info.flags`** (`src/gen/emit_dfa.c`'s `strategy_denials`): the axis changes
no answer, so two artifacts that behave identically must not differ in their
reflection surface over it — and concretely, so that an artifact the predicate
DECLINES is byte-for-byte the same under the flag as without it. What the
emitter DID is reported by `<PREFIX>_DFA_START` (§3 below) and mirrored at run
time by `rx_info.search_form` (§3.2).

**A VM HYBRID is in scope.** A hybrid inlines this same search body as its
`static <prefix>_prefilter`, so the flag reaches it and the stamp appears on
it. The elision is safe there for a second reason worth stating: the hybrid
consumes the span as a BOUND (`attempt_position = window[0][0]`), never as the
answer, and `search_from` is the strongest sound lower bound there is.


### 2.20 `-fno-alt-island` — `PCREC_NO_ALT_ISLAND` (bit 23)

**What it controls.** Which of two shapes `src/gen/emit_vm.c` lowers an
alternation of literal alternatives into. `--list-axes` reports it as
`alt-island`.

Today's `vm_alt` emits an N-way alternation as a CHAIN: one resume frame per
untried branch, the frame pushed at branch k resuming branch k+1, and each
branch its own run of byte tests. Matching the LAST of 512 branches therefore
costs 511 push/fail/pop round trips on ONE subject byte. The ALTERNATION
ISLAND replaces that with a TRIE over the alternatives' literal bytes: a byte
compare at a node with one child, a `switch` on the subject byte at a node with
several, and one try site per node where an alternative ends.

**What it applies to, and the predicate is about the LANGUAGE rather than the
branch list.** The island is built when the alternation's whole subtree matches
a FINITE set of literal byte strings — every element a single-byte class, every
combination of them enumerable in bounded space. That is deliberately not "each
branch is a literal run": `src/opt/altcls.c`'s stage-2 factoring (§2.7) runs
first and rewrites a wide alternation into a shared literal followed by a
nested alternation, so a branch test declines exactly the patterns the axis
exists for. Asking about the language instead makes the island's answer
independent of how far that earlier pass got.

**What it declines**, each a selection outcome and never a refusal — the
alternation is emitted by the chain unchanged:

| declined | why |
|---|---|
| any element that is not a one-byte class | a trie edge is a byte; a multi-byte class edge would break the disjoint-siblings property the exactness argument rests on (`src/ir/nfa.c`'s rule 2) |
| a quantifier, a group, a capture, a backreference, a lookaround, an assertion, a subroutine call | the language is not a finite literal set, or the VM is needed inside the alternation |
| a **caseless** alternation | D23 folds a caseless literal to a two-member CLASS at parse time, so its alternatives are class-leading before the emitter sees them. This is `[FORM-CHAR]`'s axis, not this one |
| more literal alternatives, or more total literal bytes, than the emitter's own enumeration budget | the cross product of concatenated alternations is exponential in principle; over the budget the island is not built |
| fewer than `VM_ISL_MIN_BRANCHES` (2) literal alternatives | there is no dispatch to make |
| fewer than `VM_ISL_MIN_BRANCHES_PREFIXED` (4), for an island that PUSHES | measured: an island whose alternatives are NOT prefix-free keeps a resume frame, and below that width the trie walk plus the frame is more work than the chain it replaces |

**THE TWO WIDTH KNEES ARE MEASURED, AND THE DISCRIMINATOR IS PREFIX FREEDOM
RATHER THAN WIDTH.** Both are `src/core/limits.def` rows of kind
`selection knee` — `pcrec --list-limits` dumps them beside
`PCREC_DEFAULT_UNROLL_K` and `PCREC_SIZE_TERM_THRESHOLD`, and like those two
they carry no `limits.md` anchor, because that document states what pcrec
promises a CALLER about an emitted matcher's resource bounds and a knee that
steers which lowering fires promises nothing.

A PREFIX-FREE island's candidate chain has one entry, so it pushes nothing and
the artifact comes out frameless; a PREFIX-BEARING one keeps a push. Measured
on a quiet box (`docs/dev/lanes/isl1_report.md` §12.1, island time over chain
time, 11 interleaved rounds, answers checked every round):

| shape | width | island / chain |
|---|---|---|
| `foo\|bar`, prefix-free | 2 | 0.175 |
| `(?:cat\|dog\|cow)s`, prefix-free | 3 | 0.140 |
| `fo\|foo`, prefix-bearing | 2 | 1.131 |
| `(?:ab\|abc)d`, prefix-bearing | 2 | 1.144 |
| `(?:a\|ab\|abc\|abcd)z`, prefix-bearing | 4 | 1.001 |
| 128 alternatives, every path prefix-bearing | 128 | 0.010 |

So the floor for a pushing island is 4 and the floor for a prefix-free one
stays 2: width 4 measured a wash, so it keeps the mechanism at no cost, and a
width floor applied to every island would have thrown away the prefix-free
width-2 population, which is where the largest per-pattern win in the table
is.

**No answer moves either way, and the argument is structural.** Leftmost-first
over an alternation of literals is `min{ i : alternative i matches here }` — a
function of WHICH alternatives match and never of their length or of trie
depth, which is `src/ir/nfa.c:192`'s own counter-example (`abc|a|abd` on "abd"
is the `a` branch, index 1, length 1, not the longer `abd` at index 2). Every
trie edge is one byte, so sibling edges are disjoint and a subject selects ONE
root-to-leaf path; the alternatives that match are exactly the ones that end on
that path. When the continuation fails, PCRE backtracks INTO the alternation
(`(ab|abc)d` on "abcd" must fall from `ab` to `abc`), and the island tries
those alternatives in ascending original index — the order the chain tries them
in.

**There is no runtime deferred mask, and that is a consequence of the same
fact.** Because the walk is a single deterministic path, the set of
alternatives still live when the walk stops is a compile-time function of the
node it stopped at. The emitter writes that list out as a chain of try sites
instead of computing it at run time, so the island allocates no slot.

**IDENTITY IS MODULO WHICH BUDGET BINDS**, exactly as §2.5 states for the
prefilter, and this axis is the second instance. The island charges its trie
walk to the WORK counter; `vm_alt`'s chain spends a STEP per branch resume. So
on a subject where the chain's step budget binds and the island's does not, the
island ANSWERS where the chain returns `PCREC_ERR_STEPS` — measured at the
shipped budget with no flags on three of 4,263 fuzz cells (e.g.
`(?:aabb|baba|abab||ba|aa|bab|b|aabbb|aba|ab)+?q` over a 64-byte a/b subject),
and under a small `--step-budget` on ordinary patterns.

**THE DIRECTION IS ONE-WAY AND THAT IS WHY IT IS SAFE:** the island does
strictly less stepping than the chain for the same alternation, so it can only
answer where the chain gives up, never the reverse — and on the three measured
cells the island's answer is libpcre2's. The axis is answer-identical wherever
neither arm's budget binds, which is every corpus cell: `make test-axes`'s
budget-bound bucket reads 0 over 22,407 of them because no corpus cell
approaches the budget at all.

**THE EMITTED SIZE IS BOUNDED AGAINST THE CHAIN, not against a cap.** The
island is built only where its estimated emitted size is within
`VM_ISL_SIZE_FACTOR` of what `vm_alt` would emit for the same subtree. Without
that rule the axis was able to REFUSE a pattern pcrec accepts without it — a
10-factor cross product, 96 characters, at 897,983 bytes of emitted code
against the 500,000 cap where the chain compiles at 30,179 — because the
enumeration budgets bound the WORD LIST while the emitted size follows the
TRIE, and a cross product blows the second up while the first is comfortable.
**An optimization axis must never narrow what pcrec accepts**;
`tests/island/run_island_tests.sh` carries a cross-product ladder asserting
refusal identity, which no corpus sweep can supply because no corpus pattern
has the shape.

**Deny-only**, `-fno-altcls-factor`'s shape: the emitter takes the island
wherever the predicate holds, so there is nothing for a caller to address and
nothing to force.

**It joins `emit_info_def`'s `strategy_denials` mask**, for that mask's own
reason: the axis changes no answer, so two artifacts that behave identically
must not differ in their reflection surface over it — and concretely, so that
an alternation the predicate DECLINES is byte-for-byte the same under the flag,
which is what makes the declined population a usable reference. What the
emitter DID is reported by `<PREFIX>_VM_ALT_ISLANDS` (`docs/spec/match_api.md`
§6.3), an activity COUNT.

**VM route only.** The DFA route determinizes the same trie for free (that is
why its artifacts are byte-identical under a branch reorder where the VM's are
not), so there is nothing for this axis to select there and no DFA artifact
carries the stamp.


### 2.21 `--vm-entry-shape=N` — the VM entry chain's ORDINAL rung

Not a bit in `pcrec_options.flags`; a separate `int vm_entry_shape` field
(`lib/pcrec.h`), `--unroll=K`'s shape rather than the deny family's. Range
enforced at the CLI: an integer in `0..4` (`cli/main.c`).

**What it selects.** A VM artifact's six entries (`<prefix>_search`,
`_search_in`, `_match`, `_match_in`, `_match_caps`, `_match_caps_in`) sit on
three thin `_run` helpers which sit on one matcher body,
`<prefix>_match_anchored`. This value chooses how many copies of that body the
artifact carries and whether the un-suffixed entries bind storage or forward:

| N | token | shape |
|---|---|---|
| 0 | — | **AUTO** (the default): the size term below chooses |
| 1 | `plain` | no attribute anywhere. ONE body; six entries, each with its own frame, its `-fstack-protector` canary and an out-of-line call |
| 2 | `shared` | the body `noinline` (ONE copy, called); the three un-suffixed entries FORWARD to their `_in` siblings through a static empty descriptor, so they carry no frame and no canary |
| 3 | `forward` | the same forwards, body inlined: THREE copies, in the three `_in` entries. No canary anywhere in the artifact |
| 4 | `inline` | six copies — what `[CC-DIFF]` STEP 1(a) shipped |

**ANSWER-IDENTICAL across every value**, and the emitted matcher program is
byte-identical across all five: what moves is the entry scaffolding above
`goto <prefix>_L0;` and nothing below it.

**WHAT `make test-axes` ACTUALLY SWEEPS, and it is TIERED.** The answer-identity
sweep runs this axis's two REACHABLE-BY-DEFAULT rungs on every run — `forward`
(what AUTO selects below the size term, so the shape most artifacts in the tree
are built at) and `inline` (the ladder's max-speed end) — and all four only
under `AXES_FULL=1`, which the union battery's axes stage exports
(`scripts/battery.sh`). Four permanent full-corpus runs was judged too much for
the day's suite; the battery is where the whole product belongs. **A
default-only green run is therefore a claim about TWO of the four rungs**, and
`tests/axes/run_axes.sh` prints its tier on every run and in its own summary so
a two-rung result cannot be quoted as a four-rung one. What a default run does
not cover is `plain`'s no-attribute emission and `shared`'s `noinline` matcher;
the forward entries and the static empty descriptor land on `shared` AND
`forward`, so that half of the new emitted code is covered by default, which is
why the default pair is `forward`+`inline` rather than `plain`+`inline`.

**A value the artifact cannot honour is a SELECTION OUTCOME, never a
refusal** — `-fno-altcls-factor`'s rule. Values 2-4 need a FRAMELESS artifact
(`<PREFIX>_VM_FRAMELESS 1`): gcc refuses `always_inline` on a function
containing a computed goto, and on a framed artifact the storage is live, so
inlining deletes nothing and only inflates the entry (`[CC-DIFF]` STEP 0
measured 1.032 there). A framed artifact takes `plain` whatever is asked.
Values 2 and 3 need more: the forward binds a NULL descriptor, so the artifact
must provably never WRITE the working storage — no `RX_PUSH`, no linked call
and no `RX_SET`. The trail is real storage even on a frameless artifact
(`(abc)(def)` pushes nothing and saves two capture slots), so frameless alone
is not enough. Where a forward rung is illegal the fallback is by INTENT:
`shared` falls to `plain` and `forward` falls to `inline`, the other rung of
the same body-count family.

**AUTO, and the size term.** `VM_INLINE_CHAIN_MAX_BYTES` (`src/core/limits.def`,
4,096 bytes) is compared against the artifact's own emitted program bytes,
stamped as `<PREFIX>_VM_PROGRAM_BYTES`. At or below it AUTO takes `forward`;
above it, `shared`. Where the forward rungs are illegal AUTO takes `inline`
below the term and `plain` above it — the two shapes that shipped before and
after `[CC-DIFF]` STEP 1 respectively, so neither step is novel.

**THE TERM'S VALUE IS MEASURED ON RUN TIME AS WELL AS SIZE, and the second
measurement says what crossing it COSTS.** A quiet-box ns/call ladder
(2026-09-04; `docs/dev/lanes/ccd2_report.md` §12, seven artifacts from 645 to
305,686 program bytes) reports `forward` within noise of `inline` on six of
seven cells and FASTER at the widest, so `forward` is AUTO's default and
`inline` is the max-speed rung a caller asks for. It also reports **`shared` at
`plain`'s run time everywhere**. So the term does not choose HOW MUCH of the
win an artifact gets: at or below it the artifact takes `forward` and gets ALL
of it (33%-50% against `shared` on this ladder, at FEWER `.text` bytes — the
default trades nothing), and above it the artifact gets NONE of it, because the
rung it falls to is at the unoptimised run time. A caller who wants the win on
a large artifact asks for it with `--vm-entry-shape=3`, paying the `.text` the
ladder prices at 0.067 bytes per ns/call just above the term and 47.7 bytes per
ns/call at 305,686.

**Reason it exists, and it is a measurement.** `[CC-DIFF]` STEP 0
(`docs/dev/ccdiff_step0.md`) found gcc leaving the entry chain out of line
where clang inlines it, costing a 152-byte frame, a stack-protector canary and
a call per search on storage a frameless artifact never touches; STEP 1(a)
fixed that with `always_inline`, which six entries then honoured six times.
`[ENG-ISL]` made WIDE artifacts frameless, and the same gate replicated a
70 KB matcher six times (`.text` x3.8, gcc x4.3 on `w-256`). This value is the
copy count made addressable, and the size term is where it is chosen from the
artifact. `docs/dev/lanes/ccd2_report.md` §3 is the four-rung ladder the term
was placed on.

**What the emitter DID is stamped** — `<PREFIX>_VM_ENTRY_SHAPE` (the token
above) and `<PREFIX>_VM_PROGRAM_BYTES` (the number the term compared), both
`docs/spec/match_api.md` §6.3 family (b), both on every VM artifact including
a hybrid, neither on a pure-DFA artifact. Two stamps rather than one because
four different artifacts can read `plain` for four different reasons (framed,
forward-illegal and large, tiered, or asked for), and the outcome alone does
not say which.

**Not masked out of `rx_info.flags`**, because it is not a flags bit at all;
it has no reflection-surface question to answer.

**[OPT-DIAL] MAY SUBSUME THIS SPELLING, AND THE ORDINAL SURVIVES EITHER WAY.**
`docs/dev/plan.md` `[OPT-DIAL]` charters a SPEED-vs-SIZE DIAL — one option
whose value sets a GROUP of switches from a policy table — and this axis is its
first native rung, the reason being that the dial wants per-switch ORDINALS and
this is one (`docs/design/opt_dial_inventory.md` §2.21 carries the measured
exchange rate that admits it). When the dial lands, the profile SETS this value
and an explicit `--vm-entry-shape=N` OVERRIDES the profile — explicit beats
profile, as D93's file-wins beats the command line — so nothing documented above
is withdrawn; what may change is that most callers stop spelling it.

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

- `RX_DFA_PREFILTER_OFFSETS` (`[OPT-K]`, 2026-08-28) names WHICH offsets
  from the candidate's own start that filter tests, ascending, with `*` on
  the one the scan searches for (`"0,8*,13"`), or `"none"` on every
  artifact whose `RX_DFA_PREFILTER` is not one of the two `offset-set`
  values. `docs/spec/match_api.md` §6.3 states the format; §2.14 above is
  the axis, and `docs/design/offset_k_skip.md` the design. Like
  `RX_DFA_TABLE` it has **no `rx_info` mirror**, for that stamp's reason.

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

- `RX_DFA_UNIFORM_FOLDS` (`[CC-DIFF]` STEP 1, 2026-09-03) is an INTEGER, not
  one of this section's string stamps: how many of this artifact's DFA
  tables were ALL-EQUAL and are therefore NOT EMITTED, with the accessor
  returning the constant instead (`0..6` — the forward machine's two tables
  always in scope, the reverse machine's unless `RX_DFA_START "pinned"`, the
  anchored machine's under `RX_DFA_MATCH "unwrapped"`). `docs/spec/
  match_api.md` §6.3 states the value set and the IFF; there is no tuning
  axis for it in §2 above — unlike every other stamp in this section, the
  fold is not a generation-time CHOICE (no pass decides it, no `-fno-`
  flag denies it), it is what the emitted machine turned out to CONTAIN,
  discovered while the emitter held the table, which is `RX_VM_FRAMELESS`'s
  reasoning one section down and not a new one. `RX_DFA_TABLE` still names
  the ENCODING that was selected even where every table of it folded (it
  still fixes the folded constant's value), so the two stamps read together
  rather than one superseding the other. It has **no `rx_info` mirror**, on
  `RX_DFA_TABLE`'s own precedent and for its stated reason.
  `tests/codegen/run_dfa_uniform_fold.sh` holds it to the emitted text.

- `RX_DFA_MATCH` (`[ENG-ABS]`, 2026-08-29) names which of the two forms
  the artifact's `<prefix>_match` takes — `"unwrapped"` (its own anchored
  machine, run from `ctx->pos`) or `"search-filter"` (the unanchored
  search with non-`ctx->pos` starts rejected). §2.15 above is the axis and
  `docs/design/anchored_match_unwrapped.md` the design. **It DOES have an
  `rx_info` mirror** (`match_form`), unlike the two stamps above, and the
  reason is the trigger `match_api.md` §6.3 named: this one is a
  caller-visible COST property of an entry point the caller calls, not an
  internal encoding choice — §3.2's worst case belongs to one of its two
  values and a header-less consumer needs to know which it linked.
  **It is also the one `RX_DFA_*` stamp a HYBRID does not carry** (§3.1
  below), because a hybrid's `_match` is the VM's own anchored body.

- `RX_DFA_SCAN_EDGE` (`[OPT-5]`, 2026-08-31) names how that scan tests the
  class of a **scan edge** — a counted class run collapsed out of the
  transition table into one bounded cursor loop — as `"range"` (a
  subtract-and-compare against two immediates), `"bitmap"` (a 256-byte
  membership read, for a class whose byte set is not contiguous), `"mixed"`
  (the artifact's machines took both) or `"none"` (it carries no edge).
  §2.18 above is the axis and `src/opt/scanedge.c` the pass;
  `docs/spec/match_api.md` §6.3 states the value set. `"none"` is not a
  failure and is the common answer: `"attempt"` scans are not eligible (their
  states are labels), `"empty"` ones have no loop, and a machine with no
  counted class run has nothing to collapse. Like `RX_DFA_TABLE` it has **no
  `rx_info` mirror**, for that stamp's reason — it is an internal encoding
  choice rather than a cost property of an entry point a caller calls — and
  like it, a HYBRID DOES carry it, because a hybrid inlines this emitter's
  scan and therefore has the fact to report.

- `RX_DFA_START` (`[OPT-5]` STEP 2, 2026-09-02) names which of the two forms
  that scan's ENTRY takes when it recovers the match START — `"pinned"` (the
  start is `search_from` by compile-time proof, and the artifact carries no
  reverse machine at all) or `"reverse-pass"` (the second, backwards scan over
  the artifact's own reverse machine). §2.19 above is the axis and
  `docs/design/opt5_step2_twopass.md` the design;
  `docs/spec/match_api.md` §6.3 states the value set. The two forms are
  **answer-identical** and differ only in cost — roughly a factor of two on a
  counted class run — and in the artifact's size. **It DOES have an `rx_info`
  mirror** (`search_form`), for `RX_DFA_MATCH`'s reason rather than a new one:
  it is a caller-visible COST property of an entry point the caller calls, not
  an internal encoding choice. Unlike `RX_DFA_MATCH`, a **HYBRID DOES carry
  it** — a hybrid inlines this emitter's search body as its prefilter, so it
  has the fact to report, which is `RX_DFA_SCAN_EDGE`'s placement rather than
  `RX_DFA_MATCH`'s.

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
#define RX_DFA_PREFILTER_OFFSETS "none"
#define RX_DFA_TABLE "premultiplied"
```

**`RX_DFA_MATCH` IS ABSENT ABOVE, AND THAT IS THE ONE `_DFA_*` STAMP A
HYBRID DOES NOT CARRY** (`[ENG-ABS]`, 2026-08-29). The four stamps in that
listing describe a DFA SCAN, and a hybrid contains one. `RX_DFA_MATCH`
describes the artifact's `<prefix>_match` ENTRY, and a hybrid's is the VM's
own anchored body — a different mechanism with a different value set. Its
iff is `RX_ENGINE "dfa"`, and `rx_info.match_form` is `NULL` here where
`rx_info.scan` is not.

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

**[OPT-5] STEP 2, 2026-09-02 — a THIRD mirror, and `match_form` was the
second.**

> **`rx_info.search_form`** mirrors `<PREFIX>_DFA_START`. It is the third
> `rx_info` mirror of a DFA selection stamp, and it exists for
> `match_form`'s reason rather than a new one: a header-less consumer that
> `dlopen`s an artifact needs to know which form of `<prefix>_search` it
> linked, because the two differ by roughly a factor of two in cost on a
> counted class run and not at all in answers. Unlike `match_form`, it is
> **non-NULL on a VM HYBRID as well**, because a hybrid inlines this same
> search body as its prefilter; it is NULL only on a plain VM artifact with
> no DFA scan.

It is appended at the END of the struct, after `nentries`, so no existing
member's offset moves, and it rides `rx_info.abi` 15 -> 16.
`tests/codegen/run_search_pinned.sh` asserts field == macro on every compiled
artifact of both engines, including the NULL case.

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
| `flags` bit `PCREC_NO_OFFSET_SKIP` | `-fno-offset-skip` | §2.14 |
| `flags` bit `PCREC_NO_ANCHORED_DFA` | `-fno-anchored-dfa` | §2.15 |
| `flags` bit `PCREC_NO_ALT_ISLAND` | `-fno-alt-island` | §2.20 |
| `unroll_k` (`PCREC_UNROLL_K_DEFAULT` = 0) | `--unroll=K` | §2.10 |
| `engine` (`PCREC_ENGINE_AUTO`/`_DFA`/`_VM`) | `--engine=E` | §2.11 |

`step_budget`, `work_budget` and `frame_capacity` are resource-bound
fields, not strategy-selection tuning axes — `docs/spec/limits.md` is
their home, not this document.

