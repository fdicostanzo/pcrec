# memory-functions: R1d, THE INTEGRATION MAP AND THE COMPOSITION MODEL

**REVISION 4 (lane `memfndel4`, 2026-10-05, from main 1c2ba975, design
only): THE CONTRACT REWORKED FROM THE EMITTERS' ACTUAL SHAPES, per the
r3 light panel (`../../dev/reviews/2026-10-05-r3-memfn-delegation.md`,
F1-F13 and G-F1..G-F14, every finding ACCEPTED). Read §R4 first: it
names the seven standing rulings this revision honours and maps every
finding to its section. The new material is §14-§23. Revision 3's §8-§13
stand where §R4 does not override them; the overridden passages carry a
`[rev4]` annotation in place.** D146 is unchanged: pcrec describes a
search site and the kit returns its code.

**REVISION 3 (lane `memfndel`, 2026-10-05, from main 90d396fd, design
only): THE DELEGATION MODEL, per D146 (Frank, 2026-10-05). Read §R3
first. Every changed passage is marked `[rev3]`, and the new material is
§8-§13. Revision 2's K0 capability-and-price query (§7) is SUPERSEDED:
no price crosses the boundary, and pcrec does no cost comparison.** The
project is named **pcrec-memory-functions** ("the kit" below, as
before). Revisions 1 and 2 are kept below and annotated where rev 3
overrides them (house style: refutations inline, not edited away).

**REVISION 2 (lane `memfnk0`, 2026-10-05, from main 68acba37, design
only): the K0 capability-and-price query layer, per Frank's ruling on
Q12. Read §R2 first; every changed passage is marked `[rev2]`, and the
new layer is §7.** Revision 1's text below is kept where it still holds
and annotated in place where it does not (house style: refutations
inline, not edited away).

Owner row: `[MEMFN]` (docs/dev/plan.md), step R1d. Lane `memfnmap`,
2026-10-04, written from main at 8a41efd2 (abi 59), reading `lane/k82fix`
(abi 60, unmerged) for `req_admits[]`. DESIGN ONLY: nothing under `src/`,
`cli/`, `lib/` or `tests/` changes, and no emitted byte moves (D91). Every
table row, stamp, option and emitted text below is DESIGNED, not built.
Building any of it is an `abi` event plus a `docs/spec/` hunk (D76/D94,
D80), behind the trigger its plan step names (§6).

Frank (2026-10-04): *"Don't get too caught up with 'separate project'. We
need to integrate. We use decision tables to organize variants. SIMD
variants might slot into those tables cleanly if given the chance. What
does that mean? Separate projects may mean a product that can be used to
generate the code selected in the decision tables. Or if that doesn't
work, some things are in the remote project and some are local. That
said, a project that allows you to create bespoke high-speed memory
functions stands on its own."* And earlier: is there benefit in
constructing functions TAILORED to the need rather than a fixed set?

Inputs: `requirements.md` (R1: F1-F13, B1a/B1b/B2/B3, RB-*, N-*),
`isa_selection.md` (R1b), `isa_evaluation.md` (R1c), `survey.md` (R2),
`docs/design/compare_stack.md` (the L0-L4 layers, §2's site inventory),
D82 (the form slot), D91 (scalar first, two budgets), D119, D122 and its
addenda 2-3 (every form choice a `DFA_SELECT`-style row; SIMD later = one
row; SWAR admitted now), D139 (one class-form table, sites as bits), D144
item 4 (every optimization its own deny), D145 (generated-output licence
exception), and the tables themselves (§1).

---

## R4. Revision 4: the contract from the emitters' actual shapes `[rev4]`

**What the r3 panel found.** The delegation architecture held, and no
finding is a blocker. But byte-identical, zero-mover migration was not
reachable through rev 3's hooks. Those hooks were written from ideal
sites, and today's sites have shapes the contract could not express. A
site returns on a miss, breaks, or is a whole function. It is an
expression inside pcrec's own `if (guard && EXPR) goto`. It reads a run
counter after the loop, emits helpers lazily, or is tallied into a
stamp. Two errors also repeated earlier ones: the stamp rule
contradicted Frank's Q3, and the shipped deny flags on the migrating
sites were not named. Revision 4 rebuilds the contract by reading each
M1 emitter at main `1c2ba975` (and the handoff on `lane/k82hbuild`,
`9bb97c7c`, abi 61). For every M1 site shape, §15 shows the `mf_site`
and hooks that reproduce today's text byte for byte.

### R4.0 The standing rulings this revision honours

| # | ruling | where it binds here |
|---|---|---|
| 1 | Frank's **Q3** on `litscan_k82h.md`: a stamp goes on EVERY artifact of its family, `none` where it does not apply. Presence never varies within a family (D81) | §18. The stamp is born with its own every-artifact abi event, BEFORE M1's replace commit. It carries no kit version. C11 checks the value, not presence |
| 2 | **D144 item 4**: every optimization keeps its own deny, and every shipped deny on a migrating site keeps working and is swept by the byte-identity gate | §14.10 gives each shipped deny's fate (bits 16, 30, 31, 32, 33, 43, 44, 45, 46, `-fno-offset-skip` …). The kit's per-form switches become real axes. I2 sweeps every `axes.def` axis and every comment tier (§17.1) |
| 3 | **D146**: pcrec carries no arch knowledge and does no cost comparison | §19 lists every remaining place pcrec prices kit-owned search code, with its fate |
| 4 | **D76/D94**: abi changes follow the ritual. Readers are found by grep, including the byte-count reader class | §18.3 (the stamp's own event), §17.4 (per-arm pins, not whole-artifact pins) |
| 5 | Measured terms are OK; tuned cutoffs are not | §19 classifies every pcrec number on a delegated site as a measured term, a ruled semantic bound or a tuned cutoff. Only measured terms and ruled bounds survive in pcrec |
| 6 | **D145**: injected text must carry 0BSD, CC0, Unlicense, or a licence with its own output exception | §20.3: per-file provenance, the translated Rust `memchr` under its Unlicense arm, the kit under 0BSD |
| 7 | **D78**: single writer each way | §20.1: two files from day one. The manager is the sole writer of requests |

### R4.1 Every finding, and where it is answered

| id | finding (short) | disposition in rev 4 | section |
|---|---|---|---|
| F1 | hooks only write values; real sites return/break on a miss, are whole functions, or are expressions inside pcrec's `if` | Three site FORMS (expression, statement, function). An `on_miss` statement hook, an `indent` hook, the opening-keyword hook, and a function name plus parameter list | §14.1, §14.2 |
| F2 | ADVANCE returns only the cursor; the scan edge's post-loop reads the kit's run counter; `scan_test` reads through `dir->peek` | ADVANCE gains a `count` lvalue with a declared start, a bound-reached contract, and a `peek` hook | §14.3 |
| F3 | in-emitter denies (`-fno-run-overlap`) have no channel to the kit; I2 cannot see them silently die | `mf_site.denies` carries every in-emitter deny. I2 sweeps every `axes.def` axis and every comment tier | §14.10, §17.1 |
| F4 | pcrec tallies emitted forms (`RUN_WORDS`, lazy helpers, the row name returned); helper placement moves | A plan/render split: `mf_plan` reports form tallies, helpers and includes before any text is written. Helpers go "before first use" at the two points pcrec uses today | §14.8, §15.6 |
| F5 | empty and wrapped ranges undefined | `hi` is spelled `n − end_back`, never as a wrapping expression. Every site declares its EMPTY outcome: MISS, NOP or EXCLUDED | §14.4 |
| F6 | the K82 gate is ONE site (lead byte + run + whole run + rest of set); ALL_PRESENT has no position; set-leads' order is pcrec's rarity choice; ON_CAND has no order | ALL_PRESENT gains `ret_pred`, the predicate whose leftmost position it RETURNS. ON_CAND visits in ascending order (descending if reversed). `DELEG_SITES` marks the sites whose result is used as a POSITION | §14.3, §14.5, §15.5 |
| F7 | rule 3 (every term holds) contradicts `consumer` and M5 (dropping terms) | REQUIRED vs OPTIONAL terms. RETURN promises `c` ≤ the true leftmost, with every REQUIRED term holding at `c` | §14.5 |
| F8 | totality needs a generic scalar row; a new shape has no baseline; shape bounds unchecked | Every kit table ends in a generic scalar row, tested over a generated predicate space. A new shape's baseline is the portable scalar arm, declared, and is UNREACHED for G1. Shape bounds are `_Static_assert`ed against pcrec's own derivation caps | §14.6 |
| F9 | `plan_hint` "transitional", but the frozen baseline needs it forever | `plan_hint` is permanent while pcrec computes it. At M5 the MODEL itself moves into the kit as the baseline's frozen planner (implement-then-replace, byte-identical), and only then does pcrec stop computing it | §14.9 |
| F10 | `on_cand` text may be copied; labels, statics or control flow out of the loop break that | `on_cand` must be duplicable. A structural check C13 holds it | §14.7 |
| F11 | no lower read guard (N3 reads `s[start−k]`, the reseed reads `s[from−1]`) | Negative term offsets with a `floor` hook. The kit never reads below `floor` | §14.7 |
| F12 | the whole-artifact baseline pin forces re-pins on unrelated abi changes; baseline arms duplicate pcrec helpers | C5 checks a per-ARM digest pinned under `tests/`. The sink adapter exposes pcrec's escapers, so the kit never copies them | §17.4, §14.2 |
| F13 | pcrec still prices kit-owned search code | The list, each with its fate | §19 |
| G-F1 | the movers-only stamp contradicts Q3 | Stamp every artifact. No kit version; form ids or `MF_VOCAB` only. Its own every-artifact abi event, before M1's replace. C11 checks the value | §18 |
| G-F2 | the shipped denies on the migrating sites are unnamed and unswept; per-form switches are not axes | The fate table, I2 over every axis, and per-form switches as `axes.def` rows | §14.10, §17.1 |
| G-F3 | C9 fails on the Mac and is vacuous under `portable` | A header shim, a native-enabled config, and a K35 floor on arms compiled | §17.3 |
| G-F4 | armv8 has no verdict-grade guard | Stated plainly, in the spec too | §17.2 |
| G-F5 | G1's population came from the kit's own `moved`; thin bins; undeclared regime | Movers come from a pcrec-side default-vs-`memfn-off` artifact diff. The regime is declared, and bins are pooled with a floor | §17.2, §21.1 |
| G-F6 | G1's cadence misses kit re-tunes | G1 runs on the movers of EVERY memfn abi event | §17.2 |
| G-F7 | C4's held-out plant is overclaimed and box-dependent | Its scope is stated honestly, the plant count is printed per box, and matching is case-insensitive | §17.5 |
| G-F8 | sabotage rows may not be mech-runnable; the baseline digest lives in the kit | Per-pattern and per-arm pin digests under `tests/memfn/pins/`, an in-tree C11 census, and `SAB_REACH` on every row | §17.4, §17.6 |
| G-F9 | the standing design questions are unanswered | Three sections | §21 |
| G-F10 | freezing the baseline now would freeze K85's open regression and collide with live edits; the handoff is unmerged | M1 is sequenced after `lane/k82hbuild` merges and after K85's re-measure. After migration, edits to delegated emitters are kit-lane work | §16 |
| G-F11 | M1's scope exceeds its trigger; R4a/R4f are circular | M1 is narrowed to the triggering site class's closure under "all callers". R4f's circularity is broken by the opt-in `-fmemfn-native` | §16, §22 |
| G-F12 | `-fno-memfn-native` polarity inverted against house convention | Axis `memfn-native`, default OFF, enabled by `-fmemfn-native` (D112's shape). R4f is the flip | §20.2, §22 |
| G-F13 | one shared request file breaks D78 | Two files from day one | §20.1 |
| G-F14 | analyze/ is the inverse precedent; `mf_*` exported unprefixed from libpcrec; Rust memchr provenance | A symbol policy (`pcrec_mf_*` at link, hidden visibility), and per-file Unlicense provenance | §20.3 |

**Count:** 27 findings. 26 have a design answer here. F9 has one
alternative to Frank's two options, and one sub-question goes to Frank
(Q38).

### R4.2 What revision 4 overrides in revision 3

- §8.2's `mf_site`/`mf_result` and §8.3's hooks are EXTENDED, not
  replaced (§14). Rule 2 gains a caller-guard declaration for
  expression-form VERIFY sites (§14.7). Rule 3 is restated over
  REQUIRED and OPTIONAL terms (§14.5).
- §8.5's profile table: `-fno-memfn-native` "DEFAULT ON" becomes axis
  `memfn-native`, default OFF, enabled by `-fmemfn-native` (§20.2).
  Rows 1-3 are otherwise unchanged.
- §9.4's M1 is narrowed and re-sequenced (§16). M5 now carries the model
  (§14.9).
- §10.1's population and cadence (§17.2). §10.3's stamp (§18). §10.4's
  plant claim (§17.5). §10.5's C5 and C9 (§17.3, §17.4). §10.7's rows
  (§17.6).
- §11.3's single ledger becomes two files (§20.1). §11.1 gains the
  symbol policy (§20.3).
- §12.2's R4a-R4j are replaced by §22. §13's questions are superseded by
  §23 (Q35-Q44). Q24-Q34 are re-derived there, not merely renumbered.

---

## R3. Revision 3: delegation, not a price market `[rev3]`

**The ruling (D146, Frank, 2026-10-05).** pcrec hands a search SITE to
the kit as a description: the operation, its operands, pcrec's proven
facts (span bounds, anchoring, a density hint) and fusion hooks. The kit
returns the code for that site and owns every choice inside it: SIMD
forms compiled per ISA, the always-present scalar fallback, short-span
loop-free paths, libc calls. pcrec does no cost comparison and carries no
architecture knowledge. pcrec's existing scalar forms for delegated sites
migrate into the kit as its scalar arms, implement-then-replace,
byte-identical first. The two projects are tightly coupled, like
pcrec-bench: when pcrec needs compound work ("this check followed by
this check", a scan fused with a verify or a handoff), the kit provides
it. The guard is pcrec's own bench/alpha timing with the kit on vs off.
Revisit when a delegated site's kit code is measured worse than pcrec's
pre-migration form and the kit cannot fix it.

**Why it replaces rev 2.** The r2 panel
(`../../dev/reviews/2026-10-05-r2-memfn-k0.md`) found that the
architecture held and the price layer did not: the regime flips verdicts,
"corners prove dominance" is a model, pcrec's rows were priced from the
kit's own loops, and a recalibration moves bytes with no abi event. Every
one of those is a property of putting MEASURED NUMBERS ON THE BOUNDARY.
Delegation takes the numbers off it. The kit may still measure and
compare, but behind its own tests, and pcrec never reads the result
except as code.

**What rev 3 is, in one paragraph.** pcrec describes a site as an
`mf_site` (§8.2): an operation over a PREDICATE (a conjunction of
position terms: byte sets and masked runs at offsets from the candidate),
the proven span, anchoring, density hints, a policy word and a handoff.
The kit writes the site's code into pcrec's sink through text hooks
(§8.3): subject, read limit, bounds, result variable, cursor, and an
optional per-candidate verify. Compound work is the predicate algebra
plus a vocabulary pcrec extends by request (§8.4). pcrec's only
decisions are WHICH SITES ARE DELEGATED, by operation type, and which
PROFILE each asks for: `baseline` (pcrec's frozen pre-migration text,
the guard's "off" arm), `portable`, or `native` (§8.5). The kit decides
everything else with its own first-match tables and its own measured
data and tests (§8.6). pcrec's scalar forms migrate in customer order,
each byte-identical under the identity gates (§9). The guards are the
kit-on/kit-off timing, the kit's exhaustive tests, the abi ritual for
any kit change that moves a byte, the arch-blindness detector and a
cross-target syntax check (§10). The kit lives in-tree first as
`memfn/`, with a request ledger on D78's shape (§11). option_sets.md's
`vector` family becomes a `memfn` family of three deny bits, and the
first mover is K82's fused scan+verify after the handoff lands (§12).
Questions Q24-Q34 (§13).

### R3.1 What survives from revisions 1 and 2

- **The table inventory** (§1: T1-T9, N1-N7) and the seven sites that do
  not slot cleanly as built (§2.4). They are now the migration's work
  list (§9).
- **`SCAN_ROWS`' site set** (PF, PRE, OFS, STAY, EDGE, VMSPAN, SETREST),
  D139's sites-as-bits shape. The sites stay; the per-site ROWS do not
  (§8.5).
- **The hook idea** (§3.3), narrowed to text hooks with a written
  contract (§8.3). The `fallback` hook dissolves: the scalar fallback is
  the kit's.
- **K1/K2/K3** (§3.3) as the kit's INTERNAL layering: primitives,
  composition generator, stand-alone CLI and reference functions. pcrec
  calls only K2's site entry. K0 is withdrawn.
- **The composition model** (§4: primitive families, C1 classifier and
  C2 shape tables, the fixed library as generic-parameter outputs, the
  scalar byte loop as the only test reference). It is wholly the kit's.
- **The zero-mover stub idea** (rev 2 R4c). It becomes stronger: the
  first migration step routes real sites through the kit at ZERO movers,
  so the delegation path is live code from its first commit (§9.1), not a
  stub.
- **The fixed `portable` default** for `--isa` (§R2 finding 3, Q18):
  never detected from the build box. It is carried as an opaque
  pass-through (§8.2), and it stays HELD with R4h.
- **The deny-bit budget argument** (Q15): bits per BUDGET and kernel
  CLASS, never per ISA (§8.5).

### R3.2 The r2 panel's findings under delegation

Each finding is **carried** (still binds pcrec, answered in the section
named), **moved inside the kit** (still binds, but as an obligation of
the kit's own design and tests, listed in §8.6), or **dissolved** (its
premise was the price boundary, which no longer exists).

| id | sev | finding (short) | disposition | where, and why |
|---|---|---|---|---|
| P1 | HIGH | the price regime is unspecified and flips verdicts | moved inside the kit | the kit's choices among its arms still face chained vs isolated, hit vs miss. pcrec reads no price, so a regime error can no longer flip a pcrec selection. §8.6 obligation K-1 |
| P2 | MED | the crossover depends on min/median as lo/hi | moved inside the kit | a statistic of the kit's protocol (§8.6 K-2) |
| P3 | HIGH | bilinear corner dominance is a model | dissolved | pcrec has no dominance test. If the kit uses one, it is the kit's model with its own tests (K-1) |
| P4 | MED | "compare on r alone" is false for FIND_PAIR / ALL_PRESENT | moved inside the kit | K-1 |
| P5 / B3 | HIGH | pcrec's rows priced from the kit's own loops (shared source) | dissolved | pcrec's rows are not priced. The guard's "off" arm is pcrec's pre-migration text, pinned byte for byte by pcrec's identity gates (§10.1), and the timing is pcrec's own bench. Neither is computed by the kit |
| B2 | HIGH | `prefix_k.c:65-68` already holds measured machine constants | carried, staged | those constants choose WHICH term the offset-k skip scans and whether to adopt it: a scan PLAN, which D146 puts in the kit. §9.4 stages the move (pcrec's pick travels as a plan hint first), Q29 |
| P6 / B4 | MED | "every arm" vs `any_win`; arm provenance; three more contradictions | dissolved (pcrec) / moved (provenance) | pcrec has no arm notion. Which libc and compiler the kit's data came from is the kit's provenance (K-3) |
| K2 | HIGH | costs depend on the compiler (×2.4, gcc vs clang) | moved inside the kit, plus one spec sentence | the kit keys its data by compiler class and may ladder on compiler macros (K-3). pcrec's spec states that the kit's choices are measured under gcc, pcrec's target compiler (D2), §10.6 |
| P7 / K4 | MED | knobs in disguise: statistic, segment cap, extrapolation, ladder | moved inside the kit | K-2: protocol constants with a decision record in the kit, and a generator that fails rather than truncates |
| P8 | MED | per_hit unpriced; shape-inherited prices; unflagged in-loop sites; STALE granularity | moved inside the kit, plus one pcrec check | the in-loop half binds pcrec: a site's D91 budget is a FIELD of pcrec's delegation table and the request's `MF_P_INLOOP` bit comes only from it (§10.5 C10). The rest is K-1/K-2 |
| K1 / D1 | HIGH | new data moves emitted bytes with no abi event; no stamp | carried | ANY kit change that moves any byte pcrec emits is a pcrec abi event in the same commit, found by D94's grep, with the movers-by-ID census and a stamp on movers (§10.3). In-tree, the kit change and the bump are one commit (§11.1) |
| P9 / C-a / C-b | HIGH | the timed control has no home, no long subjects, no armv8 arm | carried | it is now D146's guard: alpha per mover step on Linux, the batch gate's `memfn-off` bench testee, long subjects, a mover population with a floor, and a directional Mac arm (§10.1, Q31) |
| B1 | HIGH | the arch-blindness regex misses most vocabulary; weak plant | carried | rebuilt: seven vocabulary classes, one positive control each, a plant held out from the regex's source, wider scopes, plus two delegation classes (§10.4 C4) |
| B5 | MED | the other architecture's `#if` arms are never compiled | carried, on both sides | the kit cross-compiles every arm it can emit; pcrec runs `-fsyntax-only` per arm over its own artifacts, with an arm count (§10.5 C9) |
| K3 | MED | `mf_pricelist` ~28 KB on emitter stacks | carried, smaller | the request and result are small (§8.2) and come from pcrec's arena. C10 forbids `mf_*` request/result structs as automatics under `src/` |
| K5 / L1 | MED/LOW | kit text reaches artifacts against `third_party/`'s rule; licence; intrinsic headers | carried | §11.2 and Q26: 0BSD for the whole kit, the `third_party/` sentence updated at extraction, compiler-provided headers named in the spec |
| C-c | MED | the price verifier's midpoints were empty below 64 B | moved inside the kit | K-2 |
| C-d | MED | sabotage rows named timed detectors mech cannot run | carried | deterministic detectors only (§10.7) |
| C-e | MED | no `--check` for the price table; the R4c stub made the row's logic dead code | dissolved (pcrec) / moved (`--check`) | the migration routes real sites through the kit at zero movers, so pcrec's delegation code is never dead (§9.1). The kit's own data needs its own `--check` (K-2) |
| R1 | MED | the native default flip had no ruling designed | carried | `-fno-memfn-native` is ON by default during the SIMD hold, and the flip is its own ruled event (§12.2 R4f, Q28) |
| R2 | MED | R4c′'s trigger vs the handoff's likely removal of those cells | carried | the first mover's trigger is restated after the handoff lands and is measured on the post-handoff build (§12.2 R4d) |
| R3 | LOW | circular R4b/R4c triggers | carried | every step separates its PREREQUISITE (a step) from its TRIGGER (a measured cell or a ruling) (§12.2) |
| P10 / P11 | LOW | published spreads were min..max of 3; "a slow box moves nothing" | dissolved | no spread or scaling claim crosses the boundary |

**Count:** of 23 rows, 11 are carried (B2 staged), 7 move inside the
kit (P8 keeps one pcrec-side check), 3 dissolve outright, and 2 split
(dissolved for pcrec, moved for the kit: P6/B4 and C-e). Every HIGH that
was about MEASUREMENT (P1, P3, P5) leaves pcrec. Every HIGH that was
about the ARTIFACT or the CHECK (K1, P9, B1) stays.

### R3.3 What rev 3 removes from revisions 1 and 2

- §7 entire: the token-priced K0 query, `mf_pricelist`, `mf_dominates`,
  the reference terms `LIBC_*`/`LOOP_*`/`CMP_WORD8`, `memfn/cal/` as
  pcrec-visible data, and checks C2, C3, C7 and C8 as pcrec checks. C1,
  C4, C5 (reshaped) and C6 survive in §10.
- The `kit` ROW with a price predicate (§2.2 rev 2, §7.5), and pcrec's
  per-row price-formula fields.
- §2.5's `fallback` hook and its invariant's reason. The invariant
  itself (one scalar spelling per search) now holds because pcrec has
  NO scalar spelling of a delegated search after its migration step.
- Questions Q16, Q20 and Q23 (dissolved), Q12 (ruled, then superseded
  by D146), and Q19 (replaced by Q31). §13.1 maps every old question.

---

## R2. Revision 2: what changed and why `[rev2]`

**The ruling (Frank, 2026-10-05, on Q12).** He agreed with the K1/K2/K3
split, with one major refinement: *"I'd like pcrec as much as possible to
not know about the architecture details. I don't want pcrec to have
parallel knowledge in its decision tables to e.g. 'use avx2 here' if we
can avoid it. Perhaps it can query the library, given an opaque arch
token, metrics, various measures it can use to determine when to request
code injection."* And: *"That might remove the need for arch sub-panels
then."*

**The agreed shape, designed out in §7.** The kit gains a fourth layer,
**K0, CAPABILITY AND PRICE QUERY**:

- pcrec holds an OPAQUE token, from `--isa` or the fixed default
  `portable` (§7.2). pcrec never branches on it. It only passes it to the
  kit and prints it into a stamp. The C type makes this structural: pcrec
  holds an `mf_token *` with no accessor except its printable name.
- pcrec asks an ARCHITECTURE-NEUTRAL question. The question is an
  operation descriptor (find-in-set, skip-in-set, pinned pair, verify a
  run, all-present) plus the site's proven facts (span bounds, density
  interval, handoff) and the token (§7.3).
- The kit answers with a PRICE LIST. It lists the kernels it can generate
  for that token, each with piecewise-affine costs in one common unit
  (fixed picoseconds per call, picoseconds per byte, picoseconds per hit,
  each with its measured spread), its injected code bytes, and its
  arch-neutral site obligations. Whether a kernel is AVX2, SSE2, NEON or
  SWAR stays inside the kit.
- pcrec's decision table gets ONE arch-blind row, `kit` (§7.5). It
  selects the first kit quote that DOMINATES the price of the table's next
  applicable row over the whole box of the site's proven span and density,
  on every architecture arm, at the pessimistic end of both spreads. pcrec
  prices its own scalar rows in the same unit, from reference terms the
  same calibration run measured. Injection is requested only when that row
  wins.
- The prices are measured calibration tables, one per token, shipped as
  DATA in the kit and generated by a calibration probe through a
  `generate.py`. This is `third_party/`'s "a data source compiles to
  generated tables" rule (§7.7). A token no house box can measure (x86-64
  v4, SVE, SVE2) answers UNPRICED, and an UNPRICED token never selects a
  kit kernel.

**What this removes from pcrec** (§7.9 has the list):

- revision 1's four vector rows (`loopfree`, `vec-verify`, `vec`, `swar`)
  and T6's `vec-masked`. They become one `kit` row per table;
- the `BASE`/`DECLARED(L)` predicate vocabulary (§2.1);
- the vector width `V` that leaked into row 1's predicate;
- the `#if` ladder as a pcrec decision (§2.5). The ladder becomes kit
  text, and the fallback hook stays pcrec's;
- [OPT-SETS]'s `isa` poset, the `isa-route` axis and constraint rows 6-8.
  The `vector` family's four ISA-shaped bits are replaced by three bits
  named for D91's budgets and the kernel class. The "arch sub-panels"
  Frank named are those, and they go.

**What it adds:**

- one opaque value axis (`isa`, the token);
- three deny bits (`-fno-kit-scan`, `-fno-kit-loop`, `-fno-kit-native`),
  where revision 1 had four;
- one pass-through list option (`--kit-deny=`);
- the arch-blindness detector (§7.8 C4). This is a check that `src/`,
  `cli/` and `lib/` name no ISA, which turns Frank's "as much as possible"
  into a red test. Measured at this pin, the tree is ALREADY arch-blind:
  the C4 regex finds exactly ONE hit in `src/`, `cli/` and `lib/`, a
  comment at `src/opt/prefix_k.c:45` citing a glibc AVX2 measurement. So
  the allowlist is born with one entry. K0 is what keeps that number at
  one while kernels arrive.

**What did NOT change.** The table inventory (§1) and the seven sites that
do not slot cleanly (§2.4) still hold. So do the boundary's K1/K2/K3 split
and its hooks (§3.3), the composition model (§4) and the scalar-byte-loop
test reference (§4.5). [MEMFN]'s Linux run (`linux_results.md`) confirmed
T-C on x86 under gcc and clang: a `static const` descriptor through one
header kernel IS the hand kernel. That is the evidence the K2 boundary
rests on, and K0 does not touch it.

**Three findings this revision produced** (each in §7):

1. **No cutoff survives, and none is needed.** The Linux numbers already
   contain a crossover that revision 1 would have had to encode as a
   threshold. A fused SSE2 pass beats two glibc calls up to 64 B and
   loses from about 512 B. Under the dominance rule (§7.5) that crossover
   is a property of the two price lists, so it is never written in pcrec:
   - a proven span of 64 B or less selects the fused kernel;
   - an unproven (rest-of-subject) span does not, because the dominance
     check runs to infinity on the last segment's slope.

   The rule needs no assumed call span W, and W is the term
   `litscan_k82b.md` found decisive and could not source. The rule is
   `sel_cost.md` §3's admission rule ("the sign holds in every regime")
   made exact over a box. Pairwise price differences are bilinear in
   (span, density) on each segment, so checking the box's corners is a
   proof, not a sample.
2. **Density needs no prior at the default.** For the RETURN and ADVANCE
   handoffs, both rows read the same bytes up to the first hit, so the
   comparison is over read length alone (§7.6). Only VERIFY-THEN-CONTINUE
   reads density, and its default is the FULL feasible interval, which
   assumes nothing. A findings bundle may narrow the interval and is never
   required. This keeps K0 inside Frank's K82 ruling: the expected-cost
   model and its rates stay parked.
3. **The default token must be fixed, never detected.** If the default
   were "the build box's architecture", the emitted program would depend
   on the machine that ran `make`. [XARCH] measured 0 movers over 2,925
   rows across two boxes, and `litscan_k82b.md` §1.3 rejected a build-time
   probe on the same ground. So the default is `portable`, a composite
   token whose answer is one quote block per owned baseline ARM (x86-64-v1
   from ubuntubudu, armv8-a from the Mac). The `kit` row must win on every
   arm (§7.6).

---

## 0. Findings first

1. **SIMD slots into pcrec's tables as rows, but into the RIGHT table,
   and the right table does not exist yet.** The inventory (§1) has nine
   entries that touch scanning, verifying or classifying (T1-T9; T7 is a
   primitive, T8 a group of six machine tables). Today every
   L3 table row fuses WHAT is scanned (one byte, a set, an offset set, a
   pinned run) with HOW the scan is spelled (`memchr`, a table walk, two
   leapfrogged `memchr` streams). Adding SIMD as rows of those tables
   would double them: `dfa_pfs[]` already doubles every form for its
   `-bounded` twin, and a vector twin of each would make it four times
   its WHAT count. The clean slot is a NEW nested table, **the scan-form
   table `SCAN_ROWS`** (§2.2). Every L3 emitter asks it "find the first
   position in `[pos, lim)` whose byte is in S". The vector rows, the SWAR
   rows that D122 addendum 3 admits now, and today's scalar spellings are
   all rows of it. This is compare_stack.md P5's "form chosen at compile
   time", built as a table. The in-loop skips (the stay skip, the scan
   edge's run loop, the VM's span scan) are the same table at other SITES,
   in the D139 shape: one table, sites as bits.

2. **Seven sites do not slot cleanly today, each for a stated reason
   (§2.4):**
   - (a) `ofs_test_emit_fn`'s scan arm is an `if`, not a table.
   - (b) the stay skip has no form selection, and its set bypasses the
     class table that D139 made the scan edge use.
   - (c) the scan edge's LOOP form is a named, unbuilt slot. Axis I picks
     the test, not the loop.
   - (d) `vm_emit_span_scan` has one loop text.
   - (e) two readers classify the prefilter by `strcmp` on row NAMES
     (`emit_dfa.c:6417`, `:6450`). A vector row with a new name would
     silently fall out of G1's elision and out of the re-seed density
     price.
   - (f) `emit_req_set_rest` spells k one-needle passes, with no form
     choice.
   - (g) structural, not a defect: **pcrec does not know the target
     architecture when it emits.** Its output is architecture-neutral C.
     So a pcrec-time predicate can only say "a vector form exists at
     every supported architecture's baseline" or "at the DECLARED level"
     (route A, `--isa`). The per-architecture spelling resolves at gcc
     time, inside preprocessor-selected text. That fact draws the
     boundary in item 3.

     **[rev2]** The structural fact stands. What changes is who reads the
     two values. pcrec no longer has a `BASE`/`DECLARED` predicate. It
     passes an opaque token, and the kit decides whether its kernel text
     is a gcc-time ladder (composite token `portable`) or one spelling (a
     declared token). §7.2.

   Each of (a)-(f) is fixed by implement-then-replace (byte-identical)
   when its first non-scalar row lands, never ahead of it (D77).

3. **The boundary that works is a split (option c), drawn where the
   knowledge changes hands (§3).** The kit owns:
   - the per-ISA PRIMITIVES (load, classify, mask, first/last), as
     injectable text selected by predefined macros;
   - the COMPOSITION generator (descriptor in, C text out). It owns the
     loop skeleton, the short path, unrolling, the classifier per set
     shape per ISA, and the fixed reference functions.

   pcrec owns:
   - SELECTION: its tables, predicates over pattern facts, deny flags and
     stamps;
   - the OPERANDS, from its single sources (P2 cube, P3 run, P6 prior,
     minw/maxw);
   - FUSION, through hooks: the verify text at a hit, the DFA reseed and
     view bounds, the scalar fallback. The fallback is always pcrec's own
     next row, so there is never a second scalar spelling of one search
     (D122).

   The kit's internal tables answer only questions pcrec's tables do not
   ask (§3.4), so the result is two layers of one idiom, not two
   selectors. Option (a), a pure generator, is the same split with the
   primitives inlined into its output. Option (b), a header-only library
   with constant descriptors, is right for the stand-alone product and
   wrong as pcrec's only path. Gcc's constant propagation is not a
   guarantee (studies/simd1 §8), and a header the user must have breaks
   self-containment unless pcrec injects it.

   **[rev2]** RULED (Frank, 2026-10-05): the split stands, with a fourth
   kit layer **K0**, the capability-and-price query. pcrec's SELECTION
   shrinks to one arch-blind row per table. That row compares the kit's
   quoted prices against pcrec's own next row in one unit. The kit now
   also owns everything an ISA name appears in: which kernels exist for a
   token, what they cost, the target attribute and route text, the
   loader marker, and the CPU check. pcrec keeps the operands, the hook
   text and the WHAT/WHERE tables. §7.

4. **"Tailored, not fixed" is the composition model, and the fixed library
   falls out of it (§4).** A kernel is a composition of six primitive
   families, chosen by a first-match table keyed on:
   - set shape (which classifier);
   - span bounds (loop-free, one block, or a loop);
   - run/offset (one filter or a pinned pair);
   - density prior (unroll factor, and whether to iterate hits or restart
     per hit);
   - ISA capability.

   F1, F2, F3, F4, F5, F6, F9 and F13 are that composition at GENERIC
   parameters: a run-time operand, an unbounded span, an unknown density,
   the baseline ISA. The independent reference stays the scalar byte loop
   (N-6), NEVER the generic composition. A specialization checked against
   output of its own generator is a control that shares a source with
   what it controls (learnings.md §3, memory
   `pcrec-check-design-lessons`).

5. **Budgets that bind the design before any row is built (§5 Q14-Q16):**
   - **Deny bits:** 45 of the 64 `pcrec_options.flags` bits are taken
     (k82fix's `-fno-req-set-lead` is bit 45). One bit per vector row
     would exhaust them, so the recommendation is one bit per FAMILY plus
     the ISA level as a value option.
   - **Emitted-size caps (D84):** an un-declared build emits a two-arm
     `#if` ladder per vector site, which adds source bytes.
   - **The `abi` ritual:** any change to the kit's text moves emitted
     bytes, so every kit version bump is a pcrec `abi` event (D76/D94).

   **[rev2]** The deny-bit budget shrinks from four family bits to three
   (§7.9, Q15). The emitted-size cost of a ladder is now inside the
   quote's `code_bytes`, so D84's caps and the dial's size gate see it
   without a pcrec rule (Q16). One new event joins the abi ritual: a
   RECALIBRATION. It moves selections without moving any kit text, and it
   is governed by Q20.

---

## 1. The table inventory

Every first-match table in the tree that selects, or sits directly above,
a scan / verify / classify form. "Walk" names the selection function.
Line numbers are main at 8a41efd2 unless marked k82fix.

### 1.1 The walk itself

`DFA_SELECT` (`src/gen/emit_dfa.c:4943`) over `dfa_select` (`:4931`): the
first entry whose `deny & flags` is clear and whose `applies(const DfaSel *)`
holds. `DfaCand` (`:3315`) is `{name, deny, applies}`, and every object
struct begins with one. `DfaSel` (`:3298`) carries `cx`, the machine `d`,
the `UnanchStart`, `forward` and a per-state `st`. Every list ends with
`cand_always`. clskit.c and runcmp.c spell the same idiom with their own
row structs (a predicate TAG plus an exhaustive `switch`), because their
inputs are a set and a run, not a `DfaSel`.

### 1.2 The tables

| # | table | file:line | selects | rows, in order (deny) | predicates read | each row's emitter emits today |
|---|---|---|---|---|---|---|
| T1 | `dfa_pfs[]`, AXIS B | `emit_dfa.c:6304`; walk `dfa_pf_of` `:6323` | the forward scan's CANDIDATE-START skip: what it scans and how | `run-pinned-bounded`, `run-pinned` (`NO_OFFSET_SKIP`\|`NO_RUN_PREFILTER`); `offset-set-bounded`, `offset-set` (`NO_OFFSET_SKIP`); `memchr-bounded`, `memchr`; `byte-class-bounded`, `byte-class`; `none` | `us->kind` (`DFA_PF_MEMCHR` iff `cand.use_memchr`, decided in `unanch_start` `:4150`); `us->views` (the D11 bound); `ofsk.nsel`; the run pin (`pf_run_applies_common` `:5767`) | `pf_emit_memchr` `:5627`: rest-of-subject libc `memchr`, no verify. `pf_emit_bcls` `:5676`: `while (!can_begin_match[s[pos]]) pos++`. The offset/run rows call the file-scope `<p>_ofsskip` (`pf_block_ofs` `:6038` → `ofs_test_emit_fn` `:6143`), and their scan ARM is an `if`: the leapfrog over two `memchr` streams (`ofs_test_emit_pair` `:6102`) where the scan position is a two-member cube, else one `memchr` at k*. Then the `ofsk_emit_verify` chain (`:5990`), whose run term is the run compare (T7). The `-bounded` twins clamp to n−1 |
| T2 | `req_admits[]` (k82fix) | `lane/k82fix:emit_dfa.c:6638`; walk `req_admit` `:6660` | whether the whole-window PRE-CHECK is emitted, and in which shape | `none`; `one-attempt` (G2); `dominated` (G1); `set-leads` (`NO_REQ_SET_LEAD`); `emitted` | the `req_byte`/`req_run`/`req_set` facts; `req_route_one_attempt`; `dfa_cand_scan` (`:6392`) + `req_byte_dominated_by` (G1's density clause reads `cs->memchr_form`); `pcrec_find_pick` | ADMISSION only. The admitted shape is emitted by `pcrec_emit_req_byte_check` (`:1247`): one `memchr` for a byte; the `<p>_reqrun[_whole]` blocks (the same `ofs_test_emit_fn` as T1) for a run; `set-leads` adds the set pick's `memchr` in front; `emit_req_set_rest` (`:1170`) adds one `memchr` per remaining necessary-set member on the no-DFA-scan route |
| T3 | `dfa_edges[]`, AXIS H | `emit_dfa.c:7237`; walk `dfa_edge_of` `:7332` | per STATE: does it emit an [OPT-5] scan edge at all | `scan-edge` (`NO_SCAN_EDGE`); `table-walk` | the pass's own annotation `scan_span` (`edge_applies` `:7232`) | `emit_scan_edge` `:7407`: a peeled guard, then `while (more && TEST) advance;` (unbounded) or the counted `scan_run_length < span` loop. ONE loop form. Its own comment names the SIMD slot as a LOOP form "selected ahead of the scalar loop", unbuilt |
| T4 | `ROWS`, the class-form table | `src/gen/clskit.c:562`; walk `pcrec_clskit_select` `:693` | how ONE byte's membership is spelled, per set, per `--tune` position, per SITE (`CLSS_VM`, `CLSS_SCAN`) | `byte-range`; `byte-fold` (`CLSD_BYTE_FOLD`); `byte-fold-default` (VM only, held D138 Q1); `byte-kit` (`CLSD_BYTE_KIT`, size positions, only if smaller, D139 item 1); `byte-table`; `size-page3`; `speed-page2`; `speed-bitmap1`; `mid-page3`; `kit` | the set alone (one interval, the ASCII fold pair, byte-ness), model bytes, the call count, the `--tune` position, the site | inline `==c` / `(unsigned)(c-lo)<=span` / `(c\|0x20)==x` (`pcrec_clskit_emit_inline`), a kit matcher call, or a table read (`pcrec_clskit_read`). Readers: `vm_cls_test` (`emit_vm.c:1656`) and the scan edge's `scan_test` (`emit_dfa.c:7386`, axis I, D139 item 2) |
| T5 | `TAB_ROWS` | `clskit.c:754`; walk `pcrec_clskit_select_tables` `:777` | the TABLE representation for the classes T4 sent to a table, per artifact | `atom` (VM, `CLSTD_ATOM`); `scan-table` (scan site); `site` | the count of table-read classes, the atom partition's fit | the shared 256-byte byte→atom table plus a 64-bit mask per class; one 256-byte table per edge; or a 32-byte bitmap per class |
| T6 | `pcrec_runcmp_rows` | `src/gen/runcmp.c:64`; walk `rc_row_of` `:195` | the L2 RUN COMPARE (a verify), both engines | `words` (`NO_RUN_OVERLAP`, masked, L ≥ 2); `overlap` (`NO_RUN_OVERLAP`, exact, L ∈ {3, 5-7, 9-15}); `bytes` (masked fallback); `memcmp` (exact fallback) | the run alone (`rc_holds(pred, r)`: masked or not, its length) | memcpy-loaded word compares (`<p>_w<W>(base+o) & w("K")) == w("T")`, joined by `&&`); per-byte `(b & K) == T`; or `!memcmp(base, "t", L)`, which gcc fuses (one load at L ∈ {1,2,4,8}, a vector compare at L ≥ 16) |
| T7 | `pcrec_find_pick` (a primitive, not a table) | `src/core/findings.c:426` | the OPERAND: which candidate byte or cube is rarest | — (argmin over `cube_mass`; NONE answers by cardinality, k82fix (C)) | the byte-rate (static prior or a `--findings` bundle, D83/D123) | nothing; its readers (`pcrec_find_set_pick`, the run's scan member, `req_set_leads_applies`) feed T1/T2's operands |
| T8 | `dfa_reprs`, `dfa_views`, `dfa_seeds`, `dfa_accs`, `dfa_matches`, `dfa_search_starts` | `emit_dfa.c:5270`, `:5388`, `:5462`, `:5552`, `:6857`, `:7072` | the state token, the position views, the entry seed, the accept probe, the match entry, the search start | — | — | the DFA's representation. **Excluded from SIMD:** none of them scans. Membership IS the transition table (compare_stack.md §5's record) |
| T9 | `vm_ctx_forms[]` | `emit_vm.c:8229` | the VM's `\b`/lookaround context test | six truth-function rows | the node's function | a guarded one-position test through T4. **Excluded:** one or two positions, no scan |

### 1.3 The scan sites that have NO table (each a single emitted form today)

| # | site | file:line | what it is in requirements.md's menu | current form |
|---|---|---|---|---|
| N1 | the stay skip, forward and reverse (axis F's direction methods) | `emit_dfa.c:6627` `dir_fwd_skip`, `:6655` `dir_rev_skip` | F5 / F6 `skip_in_set`, IN-LOOP (D91 budget 2) | `while (pos < n && <p>_<m>_stay<K>[s[pos]]) pos++`. The stay set is a raw 256-byte table and is NOT asked through T4, unlike the scan edge since D139 item 2 |
| N2 | the VM span scan (`vm_cursor_rep`'s two arms) | `emit_vm.c:4613` `vm_emit_span_scan` | F5 at stride 1 (a class run); a stride-k sequence otherwise | `while (cur + stride <= lim && it_ < rmax && TEST) cur += stride`, with TEST being T4's spelling per position |
| N3 | `emit_attempt`'s `(?m)^` skip | `emit_dfa.c:8649` | F1, rest of subject | one libc `memchr('\n')`, candidate = hit + 1. Keeps its own form (compare_stack.md §5), provisionally |
| N4 | `emit_req_set_rest` | `emit_dfa.c:1170` | k × F1 presence tests (no current menu item: "all of S present") | a `for` over a `static const` member list, one `memchr` each |
| N5 | the ofsskip scan ARM | `emit_dfa.c:6143` `ofs_test_emit_fn` | F1 at offset k* plus a verify (F9's shape); F2/F3 for the cube (the K82 pair arm) | an `if`: pair arm (two `memchr` streams), else one `memchr` |
| N6 | `vm_rev_emit`'s backward walk | `emit_vm.c` (compare_stack.md §2.3) | F6 reverse, per byte | a per-byte L1 test with `cur--`. Keeps its own form (compare_stack.md §5) |
| N7 | `$_span_match[_caseless]` | `src/enc/enc_byte.c:153/184` | F8 `mismatch`, a run-time operand | a byte loop returning a prefix count. Gated on a cell (compare_stack.md S6) |

---

## 2. Slot-in: where SIMD joins, as rows

### 2.1 The rule this section answers to

A vector form is admissible only as a ROW: `{name, deny, applies,
emitter}`, walked by the table's existing first-match walk, with its name
being what the stamp prints and what `--list-axes` lists. The total
fallback stays last. An ISA fact is a PREDICATE INPUT, never a branch in
an emitter outside the row. That is D122 addendum 2 item 4 ("a SIMD form
later drops in as ONE ROW whose predicate includes the arch capability,
and its deny flag gives it an answer-identity axis for free"), D82, and
memory `pcrec-general-mechanisms-not-special-cases`.

**What "the arch capability" can mean at pcrec time** (finding 2g). pcrec
emits architecture-neutral C, and `Ctx` holds no target. So an ISA
predicate has exactly two readable values:

- `BASE`: a vector form of this composition exists at the baseline of
  EVERY architecture the kit supports (x86-64 SSE2, AArch64 ASIMD). The
  emitted text is then a preprocessor ladder whose `#else` arm is the
  next row's own scalar text (§2.5).
- `DECLARED(L)`: the caller passed `--isa=L` (isa_selection.md §1.2
  route A, designed, not built). The row may then emit only level L's
  spelling, with no ladder.

Route M (a consumer `-march` that raises the predefined macros) needs no
pcrec predicate. The kit's ladder sees the macros at gcc time.

**[rev2] SUPERSEDED.** pcrec reads neither value. The "arch capability"
in D122 addendum 2 item 4's sentence becomes a PRICED kit answer for an
opaque token (§7.2, §7.5). `BASE` is the kit's own behaviour for the
composite token `portable`. `DECLARED(L)` is its behaviour for a declared
token. The rule above still holds word for word: a vector form is
admissible only as a row, the fallback stays last, and no ISA fact
branches an emitter. The difference is that the row's predicate now
reads the kit's prices, not an ISA fact.

### 2.2 The new nested table: `SCAN_ROWS`, the scan-form table (P5's form slot)

**The question it answers.** "Spell the search for the first position `i`
in `[pos, lim)` whose byte is in S (or whose bytes satisfy a pinned
filter), with this handoff at a hit." It does not answer what S is, where
the search runs, or whether it runs at all. Those stay T1/T2/T3's.

**Its sites** (bits, D139's shape): `PF` (the T1 candidate-start skip),
`PRE` (the T2 pre-check's blocks), `OFS` (the ofsskip block's scan arm,
shared by T1's offset/run rows and T2's run blocks, which already share
`ofs_test_emit_fn`), `STAY` (N1), `EDGE` (T3's loop), `VMSPAN` (N2 at
stride 1), and `SETREST` (N4).

**Its input**, a `ScanSpec` (designed):

- **S, as an operand:** one byte; a two-member cube `(K, T)`; a T4
  `ClsChoice` (the set plus its scalar spelling); or a pinned pair (the
  scan byte at k* plus one more filter term at another offset). The
  pinned pair is Study A's and F9's packed pair, with the second position
  chosen by `pcrec_find_pick`.
- polarity: find-in (prefilters) or find-not-in (skips).
- direction.
- **the bound kind:** rest of subject; view-bounded `n − 1` (the D11
  twins); or counted, with `maxw` or the edge's `span`.
- **the site budget:** D91 1, the prefilter, or D91 2, in-loop.
- **the density prior:** `pcrec_find_set_ppm` / `pcrec_dfa_cand_ppm`.
- **the handoff:**
  - RETURN the index (PF, PRE);
  - VERIFY-THEN-CONTINUE, carrying the `ofsk_emit_verify` text with
    `cand` bound (OFS);
  - ADVANCE the cursor variable in place (STAY, EDGE, VMSPAN);
  - ALL-PRESENT (SETREST).
- the prefix placeholder (D143) and the comment tier.

**Its rows (first match).** The order is the design's. Placements marked
OWED are measured placements, not guesses (§6).

| # | row | sites | predicate | deny | emitter |
|---|---|---|---|---|---|
| 1 | `loopfree` | all | the bound is counted and `≤ V`, the kit's short-path width (from `maxw`, a `{0,n}` edge span, or a `W` from [FINDINGS.B4]) AND the kit composes S (§4) | `-fno-vec-scan` | kit K2: the loop-free overlapping-load short path, no loop and no call (RB-4) |
| 2 | `vec-verify` | OFS | the handoff is VERIFY-THEN-CONTINUE AND the kit composes S at `BASE` or `DECLARED` | `-fno-vec-scan` | kit K2 with the on-hit hook: iterate the hit mask's set bits, emit pcrec's verify text for each, and continue the vector loop on failure. That removes k82cost's per-hit re-entry `s`, the "find, verify, restart" cost |
| 3 | `vec` | PF, PRE, SETREST; STAY, EDGE, VMSPAN at `BASE` only unless `DECLARED` (isa_selection.md §2 row 4) | the kit composes S | `-fno-vec-scan` (in-loop sites: `-fno-vec-skip`) | kit K2: the composed scan (§4), with the `#else` arm being the first scalar row below that applies |
| 4 | `libc-memchr` | PF, PRE, OFS, SETREST | S is one byte AND the bound is rest-of-subject. OWED placement against row 3: requirements.md §2.3 row 5 keeps libc on a single rest-of-subject stream unless the Linux `n*` (U-1) says inline matches its long-span `beta` | none (today's default) | today's `memchr(...)` text, byte for byte (`pf_emit_memchr`, the ofsskip memchr arm, the pre-check, N4) |
| 5 | `leapfrog` | OFS, PRE | S is a two-member cube, single-byte scans | none | today's `ofs_test_emit_pair` text |
| 6 | `swar` | all | S is one byte, a cube, or ≤ 3 bytes, with no vector row taken. Portable `uint64_t` SWAR (has-zero-byte), admitted NOW by D122 addendum 3 as an ordinary row (no ISA predicate) | `-fno-swar-scan` | pcrec- or kit-emitted SWAR, P8's subject-end guard (word loads only where `pos + 8 ≤ n`, memcpy loads, a short epilogue) |
| 7 | `table-walk` | PF, STAY, EDGE, VMSPAN | always (the total fallback) | none | today's loop: `can_begin_match` / `stay<K>` / T4's scan test / T4's VM test, byte for byte |

**[rev2] The rows, revision 2.** Rows 1, 2, 3 and 6 above collapse into
ONE arch-blind row. The table becomes:

| # | row | sites | predicate | deny | emitter |
|---|---|---|---|---|---|
| 1 | `kit` | all | `kit_applies` (§7.5): the kit PRICES the query for the token, and its first quote (in the kit's order) whose obligations the site meets DOMINATES the next applicable row's price over the site's proven (span × density) box. It must do so on at least one arm, at the pessimistic end of both spreads. At the size-leaning `--tune` positions the kit's bytes must also not exceed the next row's | `-fno-kit-scan` (budget-1 sites: PF, PRE, OFS, SETREST) / `-fno-kit-loop` (budget-2 sites: STAY, EDGE, VMSPAN). `-fno-kit-native` restricts the quotes to portable-class kernels | `mf_emit` (§7.3) with pcrec's hooks: the verify text, the next row's text as every `#else`, the bound expression, the prefix |
| 2 | `libc-memchr` | PF, PRE, OFS, SETREST | S is one byte AND the bound is rest-of-subject | none | today's text. Price: `LIBC_MEMCHR` (+ `LIBC_RESTART` per hit) |
| 3 | `leapfrog` | OFS, PRE | S is a two-member cube | none | today's `ofs_test_emit_pair`. Price: `LIBC_PAIR` |
| 4 | `table-walk` | PF, STAY, EDGE, VMSPAN | always | none | today's loop. Price: `LOOP_TABLE` or `LOOP_EQ` by T4's spelling |

Revision 1's `loopfree`, `vec-verify`, `vec` and `swar` all survive as KIT
KERNELS. pcrec cannot tell them apart and does not need to. **[rev3]** The
`kit` row's price predicate is withdrawn. Under delegation pcrec keeps
no form ROWS for a delegated site at all: rows 2-4 (`libc-memchr`,
`leapfrog`, `table-walk`) migrate into the kit as its BASELINE arms
(§9), and pcrec's only per-site selection is the profile (§8.5). Row 4's "OWED
placement" against `vec` is gone, because it is a price comparison now.
SWAR's early admission (D122 addendum 3) survives as kernel CLASS: under
the SIMD hold, pcrec's query carries `MF_Q_PORTABLE_ONLY`, a policy flag
that names no architecture (§7.9).

Two notes on the rows (revision 1's numbering):

- **Rows 4, 5 and 7 are today's text.** Promoting the seven sites to ask
  `SCAN_ROWS` moves no byte while rows 1-3 and 6 are denied or absent.
  That is the implement-then-replace step each first non-scalar row
  carries (§6 R4c).
- **Row 6 is the one non-SIMD row.** It is buildable before the SIMD hold
  lifts (D122 addendum 3: "SWAR is fine"). It is also the first honest
  customer of the table, so the table is not built ahead of need (D77). A
  SWAR row needs a measured cell, like any optimization (D119).

### 2.3 Per table: what joins, where, and what its emitter needs

| table | the SIMD (or SWAR) rows that join | position | predicate | deny | what the row's emitter needs | slots cleanly? |
|---|---|---|---|---|---|---|
| T1 `dfa_pfs[]` | **none of its own.** Its rows keep choosing WHAT and WHERE (memchr = one byte, byte-class = the set, offset/run = k-set or pin, and the `-bounded` twins). Each row's emitter asks `SCAN_ROWS` at site `PF` (or `OFS` through the block) for HOW | — | — | — | each emitter builds a `ScanSpec` from what it already holds: `f->cand` (byte or set), `us->views` → the bound kind, `f->ofs` → `OFS` with the verify hook | **yes, once (e) is fixed.** `reseeds` is unchanged: a vector skip over a parked-state set leaves the state parked, the same argument as `byte-class` |
| T2 `req_admits[]` | none (admission is a placement fact; D122 item 2 and P7 keep it the one admission derivation) | — | — | — | — | **yes, with one change:** G1's density clause reads `cs->memchr_form`, which `dfa_cand_scan` sets by `strcmp(pf->c.name, "memchr")` (`:6417`). It must read a property of the SCAN FORM (§2.4 e). The premise "a one-byte scan's per-hit cost" changes under `vec-verify` |
| T3 `dfa_edges[]` | none. Axis H stays "edge or not". The edge's LOOP asks `SCAN_ROWS` at site `EDGE` (the slot its own comment names) | — | — | — | the edge's class set from `scan_choice` (`:7287`), the span (counted or not), the direction's cursor and bound (`f->dir->posv`, `scan_more`), the accept recording, the `ADVANCE` handoff | **no, as built (c)**: the loop text is inline in `emit_scan_edge`. Promote the loop to the table first |
| T4 `ROWS` | **none.** T4 is ONE-POSITION membership and stays scalar. The VECTOR classifier is a different question (16-64 lanes at once) asked of the same set. It belongs to the kit's composition table (§4.3), which T4's set feeds | — | — | — | — | **yes**, as an input. Its `ClsChoice` is the scalar `#else` spelling of a vector row, so one set has one scalar spelling |
| T5 `TAB_ROWS` | none. A vector classifier's constants (nibble tables, range immediates) are the kit's own literals | — | — | — | — | **n/a** |
| T6 `pcrec_runcmp_rows` | **`vec-masked`**: a masked run of L ∈ [16, 2V], one or two overlapping vector loads, `(v & K) == T` as a lane mask, all-ones test | before `words` | masked AND L ≥ 16 AND the kit composes a vector compare at `BASE`/`DECLARED` | `-fno-vec-run` | kit K1's load/and/cmpeq/all-lanes primitives. The caller's P8 guard for L bytes is already emitted | **yes, with a signature change:** `rc_holds(pred, r)` sees only the run. An ISA predicate needs `cx` (`rc_holds(cx, pred, r)`). Exact runs get NO vector row: gcc already lowers constant `memcmp` at L ≥ 16 to a vector compare (D122 addendum: pay for what you use; this record is the reason) |
| T6, **[rev2]** | `vec-masked` is replaced by the arch-blind `kit` row (op VERIFY_RUN, §7.10). Its comparison side is `words`, priced as `ceil(L/8)·CMP_WORD8` | before `words` | `kit_applies` | the site's budget bit | `mf_emit` | **yes**: `rc_holds` still needs `cx`, now for the token and the prices, not for an ISA |
| T7 `pcrec_find_pick` | none (a primitive). The packed-pair operand needs a SECOND pick (the rarest other position, with a distance rule): a new reader, `pcrec_find_pick2`, of the same MASS/PICK kinds | — | — | — | — | **yes** (a reader, not a mechanism; D126 Q4's NONE rule holds inside the primitive) |
| T8, T9 | excluded (§1.2) | — | — | — | — | — |
| N1-N4 | rows of `SCAN_ROWS` at sites `STAY`, `VMSPAN`, `PF`, `SETREST` | — | — | — | as T3's | **no, as built (b), (d), (f)**. N3 stays `libc-memchr` (row 4) with no change |
| N5 | `SCAN_ROWS` site `OFS`: rows 2 (`vec-verify`, which subsumes the K82 pair arm as one fused cube pass, F3), 3, 4, 5, 6 | — | — | — | the verify hook, `maxk`, the guard | **no, as built (a)** |
| N6, N7 | none planned. N6 keeps its own form (compare_stack.md §5). N7's F8 is a run-time operand row of its own when S6's cell exists | — | — | — | — | — |

### 2.4 Where SIMD does NOT slot cleanly, and the fix for each

| # | site | why not | the fix, implement-then-replace, when its first non-scalar row lands |
|---|---|---|---|
| (a) | `ofs_test_emit_fn`'s scan arm (`emit_dfa.c:6143-6185`) | a hard-coded `if (masked scan position) pair-arm else memchr-arm`. The comment explains the ORDER is load-bearing (r2 R2-S2), which is exactly what a row table encodes | the arm becomes `SCAN_ROWS` at site `OFS`. Rows 5 (`leapfrog`) and 4 (`libc-memchr`) are today's two arms, in today's order |
| (b) | the stay skip (`dir_fwd_skip`/`dir_rev_skip`) | no form selection, and the stay set is a raw `stay<K>` table, never asked through T4. That is the same shape D139 item 2 removed from the scan edge ("why can't it use the same structure the table recommends?") | first ask T4 at a scan-type site for the stay set (a D139-shaped cleanup, byte-identical where T4 answers `byte-table`), then ask `SCAN_ROWS` at `STAY`. An unbounded scan edge (`span < 0`) and a stay skip are the SAME loop, "advance while the byte keeps this state", so one site bit may serve both |
| (c) | the scan edge's loop (`emit_scan_edge`) | axis I selects the TEST. The loop is inline text | the loop becomes `SCAN_ROWS` at `EDGE`. The peeled first-iteration guard (the measured t-digits fix) stays the edge's own, around the table's loop |
| (d) | `vm_emit_span_scan` | one text, at any stride | stride 1 asks `SCAN_ROWS` at `VMSPAN`. A stride > 1 keeps its loop (a vector form of a k-periodic sequence is a different composition, unneeded until measured) |
| (e) | `dfa_cand_scan` (`:6417`) and `pcrec_dfa_cand_ppm` (`:6450`) classify T1's selection by `strcmp` on row NAMES | a row added under any other name changes G1's verdict and the re-seed price silently. The same file already holds the better shape: `DfaPf.reseeds` and `run_term` are FIELDS "so a seventh form cannot be added without answering it" | add a `DfaPf` field naming the scan's operand class (`SCAN_BYTE` / `SCAN_SET` / `SCAN_OFS`), and have both readers read it. G1's `memchr_form` premise ("one byte, per-hit restart") becomes a property of the chosen `SCAN_ROWS` row. This fix is owed with the first new T1-adjacent row whatever its kind, SIMD or not |
| (f) | `emit_req_set_rest` (N4) | one form (D82 bound 3: one form gets no table) | a fused ALL-PRESENT kernel (one pass, an OR-accumulated "found" mask per needle, early exit when all are found) is the second form that would earn the site a row. Site `SETREST` |
| (g) | every vector row, structurally | pcrec cannot know the architecture | §2.1 `BASE`/`DECLARED` plus §2.5's ladder. **Not a defect:** it is why the boundary is where §3 puts it |

### 2.5 The scalar fallback inside a ladder is the NEXT ROW

Under `BASE`, a vector row's emitted text is:

```c
#if <PREFIX>_MF_VEC_SSE2 || <PREFIX>_MF_VEC_NEON   /* the kit's capability macros */
    <kit K2 composition for S, at V = 16>
#else
    <the text of the first scalar row of SCAN_ROWS below this one that applies>
#endif
```

The `#else` is NOT the kit's own scalar loop. If it were, an x86 build with
no `__SSE2__` (impossible on x86-64, but the shape holds for an unknown
architecture) would run a second scalar spelling of the same search, which
is D122's one forbidden failure. The kit's own scalar or SWAR forms serve
the kit's stand-alone users and its reference functions. Inside pcrec, the
fallback is pcrec's next row. This requires K2's API to take the fallback
TEXT as a hook (§3.3).

**[rev2]** The ladder's macros, its arms and whether it exists at all are
now the kit's: pcrec passes a token and a kernel per arm (§7.3 `mf_emit`,
a NULL entry meaning "this arm falls back"). The invariant this section
states is kept, and it is now enforced at the API: the only scalar text
inside a kit emission is the `fallback` hook's, which is pcrec's next row.
An arm the kit cannot price is a fallback arm, so a ladder never gains a
scalar spelling of the kit's own.

**[rev3]** The `fallback` hook is withdrawn. After a site's migration
step pcrec has no scalar text to offer, so every `#else` is the kit's own
portable arm, and the invariant (one scalar spelling per search) holds
because the kit holds the only one (§8.3, §9).

### 2.6 Why this is rows, not a parallel mechanism

- **One walk, one idiom:** `SCAN_ROWS` is a `DfaCand` list (or clskit's
  tag-and-switch shape, whichever its inputs fit) walked first-match, total
  fallback last, deny bits in `pcrec_options.flags`, names on `--list-axes`
  ([LIST-TABLES]).
- **One table per question:** WHAT and WHERE (T1/T2/T3), HOW to scan
  (`SCAN_ROWS`), one-position spelling (T4), table storage (T5), verify
  (T6), the vector classifier (the kit's §4.3). No two answer the same
  question. A question asked by two tables would be the parallel mechanism.
- **Answer identity per deny, per architecture:** every vector row is
  speed-only. `make test-axes` with `-fno-vec-scan` and friends must be
  answer-identical on each architecture: the Mac (NEON), the Linux box
  (SSE2; AVX2 under route M), and x86 correctness under Rosetta 2 on the
  Mac (survey.md §1.2 ran SSE4.2/AVX2 there). Arch-specific testing is
  contained by the rows, which is D122 addendum 2 item 4's stated reason.
- **The stamp is the chosen row's name** (D82 rule 2, D46). A new stamp,
  `<PREFIX>_SCAN_FORM` per site class (designed), carries HOW, so the
  existing closed `<PREFIX>_DFA_PREFILTER` value set (WHAT; pcrec-bench's
  adapter enumerates it) does not split. That is the k82fix precedent of
  keeping `<PREFIX>_REQ_WHY`'s four tokens.

**[rev2]** Three of these four points hold unchanged. The changes:

- The answer-identity sweep's per-architecture arms become three deny
  arms per box (`-fno-kit-scan`, `-fno-kit-loop`, `-fno-kit-native`) over
  that box's PRICED tokens, plus option_sets.md §3.5a's compile-only arms
  per token.
- `<PREFIX>_SCAN_FORM` carries the kit's opaque `kernel_id` per arm, and
  it is emitted only where `kit` was selected.
- A new check, C4 (§7.8), keeps the rows arch-blind: no ISA word may
  appear in `src/`, `cli/` or `lib/`.

---

## 3. The boundary: what is the kit's and what is pcrec's

### 3.1 The candidates

The word "kit" means the memory-functions project here, whatever repository
it lives in (Q13).

- **(a) A GENERATOR library.** pcrec calls it at emit time through a C API:
  a descriptor goes in, emitted C text comes out, per ISA. The kit owns
  primitives, composition and spelling. pcrec owns selection and operands.
- **(b) Header-only `always_inline` primitives with CONSTANT descriptors.**
  pcrec's emitted text calls them, for example
  `mf_find_set(s, n, MF_SET_RANGES2('a','z','0','9'))`, and gcc's constant
  propagation does the specialization. The kit is a header. pcrec emits
  calls into it.
- **(c) A split.** The per-ISA primitives are the kit's injectable text, and
  composition is the kit's generator, each in its own layer. pcrec keeps
  selection, operands and FUSION through hooks. The variant the brief names
  ("primitives remote, composition/fusion local") is (c′), with pcrec
  owning composition too.

### 3.2 Evaluation

| criterion | (a) generator | (b) header + constant descriptors | (c) split: K1 primitives + K2 generator in the kit; selection and fusion hooks in pcrec | (c′) primitives remote, composition local |
|---|---|---|---|---|
| **self-contained output** (CLAUDE.md, top) | yes: text is emitted | **only if pcrec INJECTS the header text.** A user `#include` breaks the rule. Injected, it is (a)'s text without (a)'s specialization guarantee | yes. K2's text, plus the K1 subset it uses, is emitted. The runcmp precedent: `<p>_w<W>` helpers are emitted on demand (`pcrec_emit_runcmp_helpers`, `runcmp.c:248`) | yes |
| **D145 licence** | the kit's OUTPUT must carry no notice. The kit needs a generated-output exception of its own (Bison's shape), or a licence in D145's list | the header TEXT is copied into artifacts, so the header itself must be 0BSD / CC0 / Unlicense, or carry an exception | both (a) and (b) apply. Recommend 0BSD for K1 text and the same output exception for K2 (Q14). A memchr translation is Unlicense-derived and clean either way (survey.md §2) | as (c) for K1. Composition is pcrec's own text, already covered by D145 |
| **specialization guarantee** | **guaranteed:** literals are written by the generator (simd1 §8's "fix 1, the plan of record") | **NOT guaranteed.** simd1 §8 measured gcc 15 failing const-prop through a pointer array (half the throughput). Holds only for flat scalar or array descriptors, verified per compiler by objdump (N-8; D82 bound 1) | guaranteed. K2 passes immediates to K1, never a descriptor struct | guaranteed |
| **ISA resolution with no `--isa`** (§2.1) | the generator must emit a `#if` ladder per tier, or pcrec must call it once per tier and wrap the results | **natural:** the header's own `#if __SSE2__ / __ARM_NEON` selects at gcc time | natural. K1 resolves per-ISA spelling by predefined macros at gcc time. K2's composition is ISA-NEUTRAL except where the classifier RANKING differs per ISA (§4.3), and only there does it emit a two-arm ladder | as (c) |
| **testability: exhaustive per primitive** (N-6) | per generated output: possible, over a descriptor population | per primitive: direct, the header is the unit | **per K1 primitive directly, plus per K2 composition** over a descriptor population | per K1. Composition is tested inside pcrec only (answer identity), so it loses the kit's exhaustive length × alignment × position sweep |
| **testability: composition identity vs the reference** | generated vs the scalar byte loop (NOT the generic outputs; finding 4) | constant instantiations vs the scalar loop | as (a). Plus pcrec's answer identity per deny, per architecture (§2.6) | answer identity only. Weaker: the corpus never sweeps alignment or span end |
| **stand-alone value** ("bespoke high-speed memory functions stands on its own") | **high:** a CLI front-end (`memfn-gen 'find any of [a-z0-9_] in span, n ≤ 64'`) emits a tailored header. Nobody has this (survey.md §9 gap 1) | high as a LIBRARY (a better StringZilla: SSE2 tier, fused F2, short path), but a fixed set: the "tailored" half is only as good as const-prop | **highest:** both the library (K1 + reference functions) and the generator (K2 + CLI) | low: the library is a primitives header; the tailoring that is the product's point lives in pcrec |
| **what the bench / oracle can verify** | the oracle: answers only, unchanged (the rows are speed-only). The bench: pcrec cells, with stamps saying which composition ran. The kit needs its own bench (N-7) | same | same, plus the kit's own N-7 bench over its CLI-generated kernels, which is the stand-alone product's evidence | the bench sees pcrec only |
| **churn into pcrec** | every kit release that moves output is a pcrec `abi` event (D76/D94) | every header text change is an `abi` event (injected) | same as (a). Pinned vendor copy (N-10); the bump is deliberate, a ritual and not avoided (memory `pcrec-abi-changes-pre-release`) | primitive changes are `abi` events; composition changes are pcrec's own |
| **fusion with pcrec's verify / reseed / views** | needs hooks: K2 must accept caller text at the hit and the fallback | **hard.** A header function cannot contain the caller's verify unless it takes a callback (an indirect call per hit, or a macro-template, simd1 §8's risk again) | hooks (§3.3) | natural: pcrec writes the loop around primitives |
| **"two implementations of the same search"** (D122) | avoided by §2.5's next-row fallback | **at risk:** the header's scalar fallback is a second scalar spelling inside every artifact | avoided by §2.5 | avoided |

### 3.3 The recommendation: (c), with the hook contract as the uncertain part

**The kit** (one project; its home is Q13):

- **[rev2] K0, the capability-and-price query.** It takes a token and an
  arch-neutral query, and returns a price list: the kernels that exist
  for the token, their measured costs in one unit, their code bytes and
  their site obligations. It also returns the generic reference terms
  pcrec prices its own rows from, and the per-token opaque texts
  (attribute, CPU check, level stamp, loader marker). Its data is the
  calibration tables (§7.7). The full design is §7. **[rev3] Withdrawn by
  D146.** The kit's entry is `mf_emit_site` (§8.2); its measurements are
  internal (§8.6).
- **K1, the primitive layer.** Injectable C text, `static inline
  __attribute__((always_inline))`, every name behind the prefix macro
  (RB-2). It is selected per ISA by predefined macros (RB-3), with every
  wide tier also target-attributed for baseline TUs (RB-10). It has
  capability macros (`MF_VEC_BYTES`, `MF_HAS_LUT16`, `MF_HAS_MOVEMASK`)
  that compositions branch on at gcc time. Its scalar/SWAR fallback is
  for the kit's own users. K1 takes only scalar immediates and pointers,
  never descriptor structs.
- **K2, the composition generator.** A C library with no I/O. Descriptor
  in (§4.1), text out, written against K1's names. It holds the
  composition tables (§4.3-§4.4) as first-match row data with their own
  deny mask, and returns the CHOSEN ROWS' NAMES so a caller can stamp them
  (D46). Its hooks:
  - `on_hit(cand_expr)`: caller text inside the hit iteration;
  - `fallback()`: caller text for the `#else`;
  - `bound`: an expression, not a constant, so pcrec's `lim_` / `n − 1` /
    counted spans pass through;
  - `prefix`: pcrec passes its D143 placeholder `\x01q`, so its
    render-onto-finished-text step names everything.
- **K3, the stand-alone product.** A CLI over K2 that writes a header of
  named, tailored functions from a small spec. The FIXED REFERENCE
  FUNCTIONS (F1-F6, F9, F13 at generic parameters, §4.5) are K3's
  committed output, with direct per-tier names (RB-13) and optional
  out-of-line dispatch (RB-8/A2; legal in the kit's own library, never in
  pcrec's text).
- **The kit's own tests:** N-6 exhaustive per K1 primitive and per K2
  composition over a descriptor population, against the SCALAR BYTE LOOP;
  guard pages; ASan/UBSan; both architectures (Rosetta for x86
  correctness on the Mac, the Linux box for x86 timing). Its N-7 bench.
  N-8 disassembly checks.

**pcrec:**

- the tables (§2): which site gets a vector form, the deny bits, the
  stamps, the `--tune` positions (vector rows are denied at the
  size-leaning positions `-2`/`-1` unless measured smaller, D139 item 1's
  rule);
  **[rev2]** narrowed to ONE arch-blind `kit` row per table. pcrec
  decides WHETHER to ask the kit (the site, its operands, its proven
  facts) and whether the kit's best quote beats pcrec's own next row in
  the common unit. It never decides WHICH kernel or WHICH ISA. The
  `--tune` rule becomes the row's own bytes clause (§7.5);
- **[rev2]** the price FORMULAS of its own scalar rows, over generic
  terms the kit measured (§7.5);
- **[rev2]** the token, held opaque, passed and stamped (§7.2);
- the operands, from the single sources:
  - P2 `pcrec_cls_cube` for cubes;
  - T4's set intervals;
  - P3 for runs and pins;
  - P6 / `pcrec_find_*` for density and the second anchor pick;
  - minw/maxw and the edge span for bounds;
- the hooks' text: `ofsk_emit_verify`, the reseed, view clamps, and the
  next scalar row's text;
- the injection: the K1 subset a K2 output names, emitted once per
  artifact, as runcmp's helpers are;
- the vendored copy: pinned, with PROVENANCE naming the derived artifacts.
  This is the second instance of `third_party/`-derived text reaching an
  artifact, after `utf8_fold_pairs.inc` (third_party/README.md), so the
  README's "almost nothing reaches a generated artifact" sentence gains a
  second row.

**Why (c) and not (a).** They differ in one thing: whether K1 exists as a
separately testable, separately usable layer. Folding it into the generator
loses the kit's library product and its per-primitive exhaustive tests,
and saves nothing, because the generator must still emit the same
primitive text. **Why not (b) as pcrec's path:** specialization is not
guaranteed (simd1 §8), fusion needs callbacks, and the header's scalar
fallback is a second spelling of pcrec's searches. (b) survives as the
kit's LIBRARY face (K1 plus the reference functions), which is where its
stand-alone value is. **Why not (c′):** the composition (unroll, short
path, classifier per set shape) is exactly the "bespoke" knowledge Frank
says stands on its own. Leaving it in pcrec gives the kit nothing to stand
on, and pcrec's composition would be untestable outside answer identity.

**What is honestly uncertain:**

1. **The hook contract is the design's riskiest surface.** Text holes in a
   generator are easy to write and easy to misuse: hygiene of the names
   the hook text may reference, and a hook that reads past the guard the
   composition established. P8's subject-end rule must hold across the
   hole. The first build (§6 R4c) is sized to find out on ONE site (OFS's
   verify hook) before a second customer.
2. **Whether ISA-neutral composition holds for F4/F5.** The classifier
   RANKING differs by ISA (NEON `tbl` at baseline; x86 SSE2 has no
   `pshufb`), so K2 emits a ladder for the classifier only. If unroll or
   short-path choices also differ by ISA (U-8: AVX2's wider vector raises
   the short-path threshold), more of the composition becomes per-tier
   text, and (c) drifts toward (a)'s N-tier output. The size cost of that
   is unmeasured (§5 Q16).
   **[rev2]** This is now the KIT's uncertainty and is priced: a ladder
   or per-tier text shows up as `code_bytes` in the quote (§7.4), and
   linux_results.md Q16 (an AVX2 row keeps the SSE2 16-B tier) is a
   kit-internal composition rule.
3. **gcc-time capability macros are not pcrec-observable.** A stamp cannot
   say which arm compiled unless the artifact computes it from the same
   macros (`isa_selection.md`'s `<PREFIX>_ISA_LEVEL`, RB-12). The stamp
   then names the ROW. The ARM is a preprocessor fact the caller reads
   from the level macro. D46 is satisfied for selection. FORCING an arm is
   the consumer's `-m` flags (route M), not a pcrec flag.
4. **A second repository's churn pre-1.0.** Two-repo coordination costs
   more than it saves until K1's API settles. That is why Q13 recommends
   building the kit in-tree first, as a zero-dependency subtree like
   `analyze/`, and extracting it at its own 0.1.

### 3.4 Why the kit's tables are not a second selector

pcrec's tables ask questions only pcrec can answer:

- is this site worth a vector form at all;
- what is S, from which analysis;
- which budget, which bound, which handoff.

The kit's tables ask questions only a set and an ISA can answer:

- which classifier spells S;
- how many vectors per iteration at this density hint;
- loop-free or loop at this bound.

The rule that keeps them apart is written into the API: K2 receives
FACTS, never site names, and returns a composition or NONE. pcrec never
names a classifier. If pcrec ever wanted to override a classifier, the
override would be a K2 deny bit passed through, never a pcrec-side
re-derivation. **[rev2]** K0 makes this rule two-way. The kit receives
facts and never site names. pcrec receives prices and kernel IDs, and
never ISA names. The override path is `--kit-deny=` and `--kit-force=`,
both opaque pass-throughs. clskit is the in-tree precedent: `TAB_ROWS` (artifact-level)
and `ROWS` (per-set) are nested first-match tables answering different
questions, and the scan edge's axis I asks `ROWS` rather than holding a
mapping of its own (D139 item 2).

**One duplication risk this boundary creates, named with its control.**
The kit must analyse a set's SHAPE for its own users: is it one cube, how
many ranges, are its nibble buckets distinct. pcrec already owns P2
(`pcrec_cube_of`, `src/core/cpset.c`). Two derivations of "is this set one
cube" is compare_stack.md D2's class exactly. The control is an agreement
check, D2's prescribed one: the 256-point exact membership check, run over
every class the corpus produces, K2's verdict against `pcrec_cls_cube`'s.
In pcrec's calls, K2 additionally RECEIVES the cube as a hint, and must
refuse a hint its own analysis contradicts (a loud internal error, never
a silent preference).

---

## 4. The composition model

### 4.1 The descriptor (what K2 receives)

```c
typedef struct {
    /* the operand S */
    int            kind;        /* MF_S_BYTE, MF_S_CUBE, MF_S_SET, MF_S_PAIR */
    unsigned char  byte, K, T;  /* MF_S_BYTE / MF_S_CUBE */
    const uint64_t *set;        /* MF_S_SET: 256-bit membership; intervals beside it */
    int            j1, j2;      /* MF_S_PAIR: two offsets (scan, filter), j2 - j1 = d */
    unsigned char  b1, b2;      /*   and their bytes (or cubes) */
    int            negate;      /* skip (find first NOT in S) */
    int            reverse;
    /* the span */
    long           maxw;        /* -1 unbounded; else a proven bound on n */
    const char    *bound_expr;  /* the caller's bound, text */
    /* the priors */
    unsigned       density_ppm; /* expected hits per million bytes (P6/MASS); 0 = unknown */
    unsigned       run_p99;     /* skip: p99 run length if a findings value exists; 0 = unknown */
    /* the ISA */
    int            isa;         /* MF_ISA_BASE (ladder over every arch's baseline) or a declared level */
    unsigned       deny;        /* the caller's K2 row denies */
    /* hooks */
    void (*on_hit)(void *u, StrBuf *c, const char *cand_expr);   /* NULL: return the index */
    void (*fallback)(void *u, StrBuf *c);                        /* the #else arm's text */
    void *u;
} MfScanDesc;
```

(A sketch. The real API's shape is R4b's to fix. `StrBuf` would be the
kit's own sink type, not pcrec's.)

**[rev2]** Superseded by §7.3. K0's `mf_query` is this descriptor, made
arch-neutral:

- `isa` leaves the struct and becomes the token argument;
- `density_ppm` becomes an interval;
- `maxw` becomes a proven `[span_lo, span_hi]`;
- `run_p99` is dropped until a findings value exists to fill it (D77);
- the hooks move to `mf_hooks`, which K2 receives together with the
  kernel pcrec chose per arm. The price question and the generation call
  share one query, so K2 generates exactly what K0 priced.

### 4.2 The primitive set (K1)

| family | primitives | per-ISA notes (from survey.md §7) |
|---|---|---|
| **P-L load and safe tail** | `vload(p)` (unaligned, memcpy-based); `vload_last(s, n)` (the block ending exactly at `s + n`, overlapped); the sub-vector loads for `n < V`: two overlapping 8-byte words for 8..15, two 4-byte for 4..7, probes for 1..3 (RB-4); never a read outside `s[0..n)` (S-2; no aligned-down over-read, survey.md §0 item 4) | SSE2 `_mm_loadu_si128`; NEON `vld1q_u8`; SWAR `uint64_t` memcpy |
| **P-C classifiers** (a block in, a lane mask vector out) | `eq1(b)`; `eqN(b1..bk)` (OR-chain, k ≤ 3 by default); `cube(K, T)` (`(x & K) == T`, which covers every ASCII case pair at K = 0xDF); `rangeR(lo1, hi1, …)` (R ≤ 4: SSE2 `paddb` + signed `pcmpgtb`, PCRE2's idiom; NEON `vcleq` after a subtract); `lut16(lo_tbl, hi_tbl)` (nibble shufti: NEON `tbl` baseline, x86 SSSE3+ `pshufb`); `bitset32(tbl)` (NEON two `tbl` + `vtst`; x86 truffle at SSSE3+); `not(m)`; `and(m1, m2)` / `or(m1, m2)` (the pinned pair: `cls1(vload(p + j1)) & cls2(vload(p + j2))`, Study A) | the RANKING differs by ISA. That is the one place a composition holds a ladder (§4.3) |
| **P-M mask → position** | `any(m)` (NEON `umaxp` lane 0; x86 `movemask != 0`); `first(m)` (x86 `ctz(movemask)`; NEON `shrn #4` + `ctz >> 2`); `last(m)` (the `clz` forms, for F6); `count(m)` (popcount, F13); `next(m)` (clear lowest: bit iteration for VERIFY-THEN-CONTINUE) | `shrn #4` is settled practice (survey.md §9 item 8) |
| **P-S skeletons** | forward / reverse; the overlapped first block, an aligned middle, the overlapped last block (memchr's shape, no scalar head or tail at n ≥ V); unroll ×U with one OR-reduce per U vectors (RB-7); a size-tiered entry (`n < V` short path, `V ≤ n < U·V` single-vector loop, else unrolled: studies/simd1 §13's haystack tiering per call) | ISA-neutral, written over P-L/P-C/P-M |
| **P-SP loop-free short path** | for a PROVEN bound `maxw ≤ V`: no loop, no call. One or two overlapping loads, classify, mask, first. For a counted run (the scan edge's span): the mask clipped at the bound | the D91 corollary made vector-shaped; requirements.md §0 item 3 measured the scalar byte loop losing from 2-4 B |
| **P-F fusion and handoff** | RETURN (index or `n`); VERIFY-THEN-CONTINUE (for each set bit in hit order: run the `on_hit` text; on its success return `cand`; on all failing continue the vector loop: no re-entry and no rescan); ADVANCE (the cursor variable written in place: skip forms); ALL-PRESENT (OR-accumulate a per-needle "seen" bitmask across blocks, exit when full: N4); COUNT | the hooks are the boundary (§3.3). P8 holds: the hook text sees only `cand` with `cand + maxk < n` already established by the skeleton |

### 4.3 The composition tables (K2's, first match)

**C1, the CLASSIFIER table** (keyed on set shape × ISA capability). The
first applicable row whose capability holds on the arch wins. Under
`MF_ISA_BASE` the composition emits `#if <cap>` / `#else` (next row) only
where the arches' first rows differ.

| # | row | applies | capability | notes |
|---|---|---|---|---|
| 1 | `eq1` | S is one byte | any vector | the F1 shape |
| 2 | `cube` | S is one cube `(K, T)` with ≤ 4 members (a case pair; `[0-3]`-like) | any vector | one AND + one compare: F3; the K82 pair arm in ONE pass |
| 3 | `eqN` | 2 ≤ \|S\| ≤ 3, not one cube | any vector | F2's fused `Two`/`Three` |
| 4 | `range` | S is ≤ R intervals (R = 4 at SSE2 and NEON baseline; PCRE2's `X86_START_BITS_MAX_RANGES`) | any vector | the SSE2-baseline set form (survey.md §9 gap 2) |
| 5 | `lut16` | S ⊆ ASCII, ≤ 8 nibble buckets (shufti) | `MF_HAS_LUT16` (NEON base; x86 SSSE3+) | where x86 SSE2 and NEON first DIFFER: the ladder site |
| 6 | `bitset32` | any S | `MF_HAS_LUT16` | StringZilla's NEON form; truffle on x86 SSSE3+ |
| 7 | NONE | otherwise | — | K2 declines; pcrec's row predicate fails; the scalar row runs (no vector form exists for S on this tier) |

**C2, the SHAPE table** (keyed on span bound × density × handoff × ISA
width V):

| # | row | applies | composition |
|---|---|---|---|
| 1 | `short` | `0 ≤ maxw ≤ V` | P-SP: loop-free |
| 2 | `one-block` | `V < maxw ≤ 2V` | first block + overlapped last block, no loop |
| 3 | `iterate` | handoff is VERIFY-THEN-CONTINUE AND `density_ppm` is HIGH (≥ about one hit per V bytes; the threshold is owed, §6) | ×1 loop, bit-iterate every hit (dense: unrolling only delays the first hit) |
| 4 | `skip-width` | `negate` (a skip) AND `run_p99` known | a vector width whose window covers p99 of runs (simd1 §15's measured rule: predictability first). ×1, no unroll |
| 5 | `unrolled` | `density_ppm` LOW or unknown AND `maxw` unbounded or > 4V | the size-tiered entry: short / ×1 / ×4 OR-reduce (RB-7: matches libc's long-span `beta`) |
| 6 | `loop` | always | ×1 loop with the overlapped last block |

Every C1/C2 row has a K2 deny bit, and K2 reports `C1-row/C2-row` names
(for example `cube/unrolled`) for pcrec's `<PREFIX>_SCAN_FORM` stamp.

### 4.4 What "tailored" buys, case by case (the answer to Frank's earlier question)

| need (a pcrec site) | the fixed-library answer | the tailored composition | why it wins (measured or cited) |
|---|---|---|---|
| K82 pair arm, `(?i)` scan member | two `memchr` streams, leapfrogged (two calls, two passes, overshoot) | `cube` × `iterate`/`unrolled` with the run verify as `on_hit` | requirements.md §0 item 2: fused 0.96-1.46 ns against 3.27 ns at n ≤ 16; 1.6-1.8× at 4 KiB; no per-hit re-entry |
| `(?i)union…` byte-class prefilter over `{u, U}` | a 256-byte table walk, one load per byte | `cube` (K = 0xDF) × `unrolled` | survey.md §0 item 3: NEON `tbl` bitset 6.7-7.6× a table loop; a cube is cheaper still |
| scan edge `[a-z]{0,8}` | a byte loop with the T4 test per byte | `range` × `short` (maxw 8 ≤ V): one load, one classify, `first(not(m))`, clipped at 8 | requirements.md §0 item 3: a short span's form is loop-free |
| VM `[a-z.]+` before `@` (a class run) | the stride-1 span loop | `range`/`lut16` × `skip-width` | simd1 §15: classify + clz, 2-3× over a scalar table loop on mixed run lengths |
| REQ_RUN `/user` in a 1 MiB subject | `memchr('/')` + `memcmp` per hit, restarting | `pair` (the two rarest positions by `pcrec_find_pick2`) × `iterate`, with the run compare as `on_hit` | Study A (simd1 §12): pinned rare-position filters, adopted. The ofsskip and pre-check share one block, so one composition serves both |
| N4: three set members all present | three `memchr` passes | `eqN` × ALL-PRESENT, one pass | requirements.md §2.2 item 2 (k streams cost k F's and k passes) |

### 4.5 The fixed library as the generic-parameter outputs

The kit's reference functions are K2 at generic parameters: S a run-time
operand (no constant folding of needles, so K1 takes a broadcast register),
`maxw = -1`, `density_ppm = 0`, `isa = BASE`, `on_hit = NULL`.

| function | the composition |
|---|---|
| F1 `find_byte` | `eq1` × `unrolled`, RETURN |
| F2 `find_any2/3` | `eqN` × `unrolled`, RETURN |
| F3 `find_cube` | `cube` × `unrolled`, RETURN |
| F4 `find_in_set` | C1 rows 4-6 (a run-time set: `bitset32` on NEON; on SSE2 the scalar bitmap: C1 row 7 is honest here) × `unrolled` |
| F5 `skip_in_set` | F4 with `negate` |
| F6 `rfind_byte`, `rskip_in_set` | F1/F5 with `reverse`, P-M `last` |
| F9 `find_literal`, anchored | `pair` × `iterate`, with the kit's own literal compare as `on_hit` |
| F13 `count_byte` | `eq1` × COUNT (aligned 4× loop, scalar tail, never overlapped: an overlap double-counts) |
| F7 run compare | not a scan: K1's vector compare (T6's `vec-masked` row) |
| F8 `mismatch` | a two-operand variant (`cmpeq(a, b)` negated, `first`); a C1 row over two streams, not built until S6's cell |
| F10 Teddy, F11 UTF-8, F12 find-all | not compositions of this model; their own kernels (survey.md §8) |

**The reference for testing is never this table.** A specialization (say
`cube/short` at maxw 8) is checked against the scalar byte loop, which
shares no source with K2. Checking it against F3 (`cube/unrolled`, the
same generator) would let a K2 defect in `cube` pass both
(learnings.md §3). The generic outputs are the PRODUCT, not the control.

---

## 5. Questions for Frank

**[rev3]** The open questions are now §13 (Q24-Q34); §13.1 maps every
question below to its rev 3 status.

Numbering continues from isa_evaluation.md's Q7-Q11.

12. **Q12, the boundary.** Should §3.3's split be the design of record?
    - The kit owns K1 (per-ISA primitives, injectable text), K2 (the
      composition generator, with its own first-match tables and hooks)
      and K3 (the CLI and fixed reference functions).
    - pcrec owns selection (its tables, plus the new `SCAN_ROWS`),
      operands, fusion text and injection.

    **Recommendation:** yes. It is the only option under which the kit
    stands on its own as BOTH a library and a "bespoke functions"
    generator, pcrec's output stays self-contained and specialized, and
    no search gets a second scalar spelling.

    **[rev2] RULED (Frank, 2026-10-05): yes, with K0.** The kit owns
    K0-K3. pcrec owns selection through ONE arch-blind row per table,
    plus operands, hook text, its own rows' price formulas and the opaque
    token. Linux confirmed the K2 premise (linux_results.md §6.3: T-C's
    descriptor kernel is the hand kernel on x86 under gcc and clang).
    **Recommendation for what remains:** adopt §7 as the design of record
    for K0.
13. **Q13, where the kit lives first.** **Recommendation:** in-tree, as a
    zero-dependency top-level subtree (`memfn/`, on `analyze/`'s
    precedent: it links nothing from `src/`, and `src/` reads it only
    through its public header and API). Extract it to its own repository
    at its 0.1, when K1's API has a second consumer. That respects "don't
    get too caught up with separate project" and keeps the scope mandate
    unextended until then. pcrec's emitter then reads the in-tree copy.
    After extraction it reads a pinned vendor copy under `third_party/`,
    with PROVENANCE naming the derived artifacts.

    **[rev2]** Unchanged, plus the calibration data: `memfn/cal/` in-tree
    (§7.7). After extraction, the vendored copy carries `prices.inc` and
    each arm's PROVENANCE.md. A recalibration then arrives as a vendor
    bump (Q20).
14. **Q14, the kit's licence.** **Recommendation:** K1's injectable text
    under 0BSD, and K2/K3 under MIT with D145's generated-output exception
    (or all of it 0BSD). Either way its text and its output reach users'
    artifacts with no notice, under D145's list. A translated memchr is
    Unlicense-derived and compatible with both.

    **[rev2]** Unchanged. The calibration data never reaches an artifact.
    Only the chosen kernel's text and its opaque `kernel_id` stamp do. So
    the data takes the kit's own licence and needs no output exception.
15. **Q15, the deny-bit budget.** 45 of 64 bits are taken. **Recommendation:**
    - one pcrec bit per FAMILY: `-fno-vec-scan` (`SCAN_ROWS` rows 1-3 at
      PF/PRE/OFS/SETREST), `-fno-vec-skip` (the same rows at the in-loop
      sites, so D91's budget 2 has its own kill switch), `-fno-vec-run`
      (T6's `vec-masked`) and `-fno-swar-scan` (row 6): four bits;
    - K2's internal rows (C1/C2) denied through ONE value option
      (`--memfn-deny=cube,unrolled,…`), not flag bits;
    - the ISA level as the value option `--isa=L` (route A; already
      designed, isa_selection.md Q4).

    D144 item 4 ("every optimization its own deny") is met at the
    granularity the batch-gate triage uses: a family flips, then the
    value option bisects within it.

    **[rev2] Revised: three bits, named for budgets and kernel class,
    never for an ISA.**
    - `-fno-kit-scan` covers the `kit` row at budget-1 sites (PF, PRE,
      OFS, SETREST, and T6 where it verifies for a prefilter).
    - `-fno-kit-loop` covers the `kit` row at budget-2 sites (STAY, EDGE,
      VMSPAN, and T6 inside the match).
    - `-fno-kit-native` limits quotes to portable-class kernels. That is
      SWAR's D122 addendum 3 line and the bench's SIMD-off testee.

    The first two are three-valued (deny/auto/force, option_sets.md
    §2.4a), which gives D46's forceable half. `--kit-deny=` (rev 1's
    `--memfn-deny=`) and `--kit-force=` pass kernel IDs through unparsed.
    `--isa=TOKEN` is the one value axis. Bits used: 46 of 64 at this pin
    (0-45), with k82hand's design taking 46. **Recommendation:** the three
    bits.
16. **Q16, ladders in un-declared builds.** Without `--isa`, a vector row
    emits a two-arm `#if` (vector / pcrec's next scalar row). That adds
    source bytes under D84's caps and the dial's size term. **Recommendation:**
    accept it. The ladder covers only the classifier (C1 row 5's NEON/x86
    split) and the outer vector-or-scalar choice, not whole loops.
    Measure the added bytes over the corpus at R4c (the emitted-size log
    already exists, `[ART-SIZE.1b]`), and make "vector rows only under a
    declared `--isa`" a row predicate if the cost proves material. The
    rows absorb either answer.

    **[rev2] Dissolved.** A ladder's bytes are in the quote's exact
    `code_bytes` (§7.4). So D84's caps, the dial's size-leaning positions
    (the row's bytes clause, §7.5) and the size log all see them with no
    pcrec rule and no `--isa`-only predicate. Linux's one finding for
    this question (an AVX2 row must keep the SSE2 16-B tier, else 8-16 ns
    against 2-4 ns at 16 B) is a K2 composition rule, and it shows up in
    the AVX2 quote's own price. **Recommendation:** close Q16. The
    corpus-bytes measurement at R4c stays, as a census.
17. **Q17, promoting the seven non-table sites (§2.4).** **Recommendation:**
    each site is promoted to ask `SCAN_ROWS` only when its first
    non-scalar row lands, byte-identically (implement-then-replace), never
    as a standalone refactor (D77). Two exceptions, owed now regardless of
    SIMD:
    - §2.4(e), the `strcmp` name readers, is a latent defect against ANY
      new T1 row. Recommend it rides the next T1 change of any kind.
    - §2.4(b)'s first half, the stay set through T4, is D139's own
      argument one site over. Recommend filing it as a `[CLS-TREE]`
      follow-up row.

    **[rev2]** Unchanged. One addition: §2.4(e)'s fix should read the
    chosen `SCAN_ROWS` row's price CLASS (does a hit restart a call?),
    not its name. The `kit` row's per-hit price makes that class a
    property of the quote.

18. **[rev2] Q18, the default token.** Should the default be `portable`,
    fixed, never detected from the build box? Its answer is one quote
    block per owned baseline arm (x86-64-v1, armv8-a), and the kit text
    is a ladder whose `#else` is pcrec's next row. **Recommendation:**
    yes. Detection would make the emitted program depend on the machine
    that ran `make`. [XARCH] measured 0 movers over 2,925 rows on two
    boxes, and `litscan_k82b.md` §1.3 already declined build-time
    calibration on the same ground.
19. **[rev2] Q19, the Mac as the armv8-a calibration box.** D144
    addendum 1 calls Mac timings directional. **Recommendation:** admit
    the Mac as armv8-a's calibration box, under three conditions:
    - calibration's own protocol: N ≥ 5 loops of ≥ 50 ms, min and
      median, the harness's loop subtracted, in a quiet window;
    - pcrec reads only the pessimistic ends of the spreads (kit median
      against reference min), so noise makes the row decline, never
      wrongly select;
    - C7's ratio-invariance check passes on that arm.

    The verdict-making timings of D144 addendum 1 stay Linux-only. A
    calibration is not a verdict: C3 on the Mac would be. Without this
    ruling, armv8-a is UNPRICED and `portable` prices its x86 arm alone.
20. **[rev2] Q20, recalibration governance.** A new calibration run
    moves no kit text and no layout, so it is not an `abi` event. It can
    still move selections. **Recommendation:** a recalibration lands as
    one change containing:
    - the raw transcript;
    - the regenerated `prices.tsv`/`prices.inc` (`generate.py --check`
      green);
    - a SELECTION-DIFF census: every corpus and bench site whose chosen
      row or kernel moves, by ID (the movers-by-ID discipline every
      recent abi landing used);
    - C3 on the movers.

    It is accepted like an alpha (D144). Prices are never hand-edited.
    D103's ruled-diff governance does not apply: it governs a pinned
    policy table, and these are measurements.
21. **[rev2] Q21, the route folded into the token.** **Recommendation:**
    yes, and withdraw the designed `--isa-route` axis. The kit's token
    grammar spells both routes (`x86-64-v3` for route A, `x86-64-v3+cc`
    for route M with the `#error` floor; the spelling is the kit's). This
    removes option_sets.md constraint row 6 with it.
22. **[rev2] Q22, whose libc prices pcrec's libc rows.** `LIBC_*` is the
    calibration box's libc (glibc 2.43 for x86 arms; libSystem for
    armv8-a). A consumer on musl inherits decisions priced on glibc.
    **Recommendation:** accept and document it in `docs/spec/` at R4c. A
    platform-qualified token (`x86-64-v1/musl`) is the general form, to be
    built only for a measured customer (D77).
23. **[rev2] Q23, K0 against the K82 ruling.** Frank parked K82's
    expected-cost model for simplicity. K0 is also a cost comparison, but
    it needs no rates: no call span W, no density prior and no bundle.
    It needs only proven bounds and measured machine terms. The dominance
    rule reads the sign over the whole box, so it can only decline where
    a modelled expectation might have admitted. **Recommendation:** K0
    never requires a findings bundle. A bundle may only NARROW the
    density interval. If K82's model is ever unparked, its `ps` terms
    read `mf_ref` instead of adding `limits.def` rows, so the house
    keeps one calibration source.

---

## 6. Plan-row text for the manager (`[MEMFN]` R1d → R4)

**[rev3]** Both build orders below are superseded by §12.2 (R4a-R4j),
whose plan-row text replaces them.

Paste under `[MEMFN]`. Each step carries its D77 trigger. Steps that touch
pcrec's emission open only under `[OPT-SIMD]`'s sequencing (SIMD last,
D119/D91), except the SWAR row (D122 addendum 3).

> **R1d DELIVERED 2026-10-04 (lane memfnmap): `docs/design/memfn/integration.md`** — the integration map. Nine inventory entries (T1-T9) plus seven table-less scan sites (N1-N7); SIMD joins as rows of ONE new nested scan-form table `SCAN_ROWS` (sites PF/PRE/OFS/STAY/EDGE/VMSPAN/SETREST, D139's shape) rather than as vector twins of every `dfa_pfs[]` row; T6 runcmp gains one `vec-masked` row; T4 ROWS stays scalar and feeds the kit's classifier table. Seven sites do not slot cleanly as built (the ofsskip scan arm's `if`, the stay skip, the scan-edge loop, the VM span scan, two `strcmp`-on-row-name readers, N4's k-memchr loop, and pcrec's architecture-blindness at emit time), each with its implement-then-replace fix. Boundary = (c): kit K1 per-ISA primitives (injectable text) + K2 composition generator (descriptor in, text out, hooks for pcrec's verify and fallback) + K3 CLI/reference functions; pcrec keeps selection, operands, fusion text, injection. Q12-Q17 open to Frank.
> - **R3** (findings to Frank, rulings Q1-Q17): trigger = this delivery. Owed beside it: `probes/linux_run.sh` (U-1, U-8..U-12), the survey's Linux timing.
> - **R4a, kit K1 + reference functions, in-tree `memfn/` (per Q13):** P-L, P-C (`eq1`, `eqN`, `cube`, `range`), P-M and P-S for SSE2 + NEON + scalar/SWAR; F1/F2/F3/F5/F6 as committed K3 output; N-6 exhaustive + guard pages + ASan/UBSan on both architectures (Rosetta for x86 correctness on the Mac); the N-7 bench. **Trigger:** Frank's R3 ruling (the kit stands on its own, so its own trigger is the charter; no pcrec cell is needed for code that changes no emitted byte).
> - **R4b, K2 composition generator + K3 CLI:** C1/C2 tables with deny and row names; the four hooks; the descriptor; the agreement check of K2's cube analysis against `pcrec_cls_cube` (the 256-point exact check, every corpus class). **Trigger:** R4a green on both architectures, plus a named first pcrec customer (R4c).
> - **R4c, the first pcrec row, at site OFS:** promote `ofs_test_emit_fn`'s scan arm to `SCAN_ROWS` (rows 4/5 = today's text, byte-identical, the identity gate), then add `vec-verify` (`cube` × `iterate`/`unrolled`, the run verify as `on_hit`) under `-fno-vec-scan`. Fix §2.4(e) in the same change. abi bump, `docs/spec/` hunk, `<PREFIX>_SCAN_FORM` stamp, sabotage rows (vector row reached; hook guard; fallback arm). **Trigger:** `[OPT-SIMD]` opened (D119 sequencing) AND the K82 pair-arm cells measured on Linux above the D144 addendum-1 noise floor AND U-1's fused-vs-two-call margin holding on x86.
> - **R4c′, the SWAR row (`SCAN_ROWS` row 6), may precede R4c:** a portable SWAR `eq1`/`cube` scan at PF/OFS, admitted now by D122 addendum 3. **Trigger:** a measured cell whose time is in a one-byte or cube scan with short spans (the bench's per-call 6-11 B cells, k82diag §2), alpha-accepted per D144.
> - **R4d, `vec` at site PF (the byte-class prefilter):** C1 rows 2-6 over `can_begin_match`'s set; promote `pf_emit_bcls[_bounded]` to `SCAN_ROWS` first. **Trigger:** the bench class-shape census (U-2, relayed to pcrecdev2) AND a Linux cell whose time is in `pf_emit_bcls` (the WAF `byte-class` cells, compare_stack.md §6.3).
> - **R4e, in-loop skips (sites STAY, EDGE, VMSPAN):** promote the three loops (§2.4 b-d), then `vec`/`loopfree` at `BASE` only (isa_selection.md §2 row 4). **Trigger:** U-3 (an in-loop dispatch probe at a real emitted site, D91 budget 2 re-measured, never inherited) AND a Linux cell dominated by class runs (simd1 §15's shape; `t-digits`-type cells).
> - **R4f, T6 `vec-masked`:** **Trigger:** a census of masked runs with L ≥ 16 at verify sites, plus a cell.
> - **R4g, declared-ISA rows (`DECLARED(L)`):** wide tiers at prefilter sites. **Trigger:** isa_evaluation.md §3.3 L-1/L-2 (a measured level gain on ubuntubudu) and Q4's ruling.
> - **Filed, not scheduled:** the stay set through T4 (a `[CLS-TREE]` follow-up, §2.4 b, D139's argument); N4 ALL-PRESENT (trigger: a cell on the K65 no-DFA-scan route whose time is in `emit_req_set_rest`).


**[rev2] The build order, revision 2.** It replaces R4a-R4g above. The
triggers carry over unless stated. The K0 layer adds two steps (R4a′, and
the stub half of R4c). It turns revision 1's per-family pcrec rows into one
row per table.

> **R1d REVISION 2 DELIVERED 2026-10-05 (lane memfnk0): `docs/design/memfn/integration.md` rev 2** — Frank's Q12 ruling (boundary (c) plus K0) designed out. The kit gains K0, a CAPABILITY-AND-PRICE QUERY (§7): pcrec holds an OPAQUE token (`--isa`, default `portable`, fixed and never detected), asks an arch-neutral query, and gets a price list back (piecewise-affine ps costs with measured spreads, exact code bytes, arch-neutral site needs). pcrec's tables get ONE arch-blind row, `kit`, chosen iff a kit quote DOMINATES the next row's price over the site's proven span × density box on some arm. pcrec prices its own rows from kit-measured generic terms. Calibration is data in `memfn/cal/<arm>/` (raw transcript → `generate.py` → `prices.tsv`), owned per box; x86-64-v4/SVE/SVE2 are UNPRICED. Removes revision 1's four vector rows, `BASE`/`DECLARED`, `V`, the pcrec-side ladder, [OPT-SETS]'s `isa` poset/`isa-route`/constraint rows 6-8 and three of the `vector` family's four bits. Adds three deny bits (`-fno-kit-scan`/`-loop`/`-native`) and the arch-blindness detector C4. Q12 ruled; Q13-Q17 updated; Q18-Q23 new.
> - **R3** (rulings): Q13-Q23. Owed beside it: nothing new on Linux. linux_results.md already answers U-1/U-8..U-12/L-2/L-4/T-C.
> - **R4a, kit K1 + reference functions, in-tree `memfn/`** (unchanged from revision 1, plus the SWAR primitives as a PORTABLE kernel class). **Trigger:** Frank's R3 ruling.
> - **R4a′, K0 + the calibration pipeline** (new): `memfn/k0.h`; `mf_price` over `prices.inc`; `memfn/cal/calibrate.c` + `run_calibrate.sh` + per-arm `generate.py`; the first priced arms `x86-64-v1` (ubuntubudu, through the executor channel) and, on Q19, `armv8-a` (the Mac); C2 (price vs measurement, with the staleness count), C7 and C8 as the kit's own tests. **Trigger:** R4a green. No pcrec cell is needed, because it changes no emitted byte.
> - **R4b, K2 composition generator + K3 CLI** (unchanged), with `mf_emit` taking a kernel per arm and the fallback hook. **Trigger:** R4a′ green on one priced arm, plus a named first pcrec customer.
> - **R4c, pcrec's K0 consumer, byte-identical first:** `--isa=TOKEN` as an opaque value axis (default `portable`), `SCAN_ROWS` promoted at site OFS (rows `libc-memchr`/`leapfrog` = today's text, each with its price-formula field), the `kit` row against a K0 STUB that answers UNPRICED for every token, so ZERO movers is the identity gate. C4 (the arch-blindness detector, with its allowlist counted at birth) and C5 land here, and §2.4(e) is fixed in the same change. No abi event while the stub answers. **Trigger:** R4b green.
> - **R4c′, the first movers: portable-class kernels (SWAR) at OFS/PF under `MF_Q_PORTABLE_ONLY`**: the stub is replaced by the real K0, `-fno-kit-scan`/`-fno-kit-native` exist, and there are an abi bump, `<PREFIX>_SCAN_FORM` on movers, the `docs/spec/` hunk, C3 on the movers, sabotage rows and the selection-diff census. This is the first end-to-end K0 customer, and it is admissible under the SIMD hold (D122 addendum 3). **Trigger:** a measured cell whose time is in a one-byte or cube scan with short proven spans (k82diag §2's 6-11 B cells), alpha-accepted per D144.
> - **R4d, native-class kernels at OFS (`vec-verify`'s successor):** `MF_Q_PORTABLE_ONLY` is lifted for budget-1 sites. **Trigger:** `[OPT-SIMD]` opened (D119 sequencing) AND the K82 pair-arm cells above the D144 addendum-1 floor on Linux. U-1's margin is ANSWERED (fusion wins at ≤ 64 B, loses from ~512 B). Under K0 that is no longer a gate but the prices themselves.
> - **R4e, PF byte-class:** `pf_emit_bcls[_bounded]` promoted to `SCAN_ROWS`. **Trigger:** unchanged (U-2's class-shape census plus a Linux `pf_emit_bcls` cell).
> - **R4f, in-loop sites (STAY, EDGE, VMSPAN) and the in-loop calibration column:** the three loops promoted (§2.4 b-d), `-fno-kit-loop`, and `calibrate.c`'s `MF_Q_INLOOP` column. Until then, in-loop queries answer UNPRICED. **Trigger:** U-3 (an in-loop probe at a real emitted site) AND a Linux cell dominated by class runs.
> - **R4g, T6's `kit` row (VERIFY_RUN):** **Trigger:** unchanged (a census of masked runs with L ≥ 16 at verify sites, plus a cell).
> - **R4h, declared tokens beyond `portable`** (`x86-64-v3`, …: attribute, CPU-check and level-stamp texts from the kit, `rx_info.isa_token`, an abi event). **Trigger:** isa_evaluation.md L-1/L-2. L-2 is answered as "no customer now" (linux_results.md §5), so this stays HELD.
> - **Filed, not scheduled** (unchanged): the stay set through T4; N4 ALL-PRESENT. New: the platform-qualified token (Q22), built for a measured customer only; an emulator CORRECTNESS arm for v4/SVE (never a price).
---

## 7. K0, THE CAPABILITY-AND-PRICE QUERY `[rev2]`

**[rev3] SUPERSEDED ENTIRE by D146 (§R3, §8).** No price, token-priced
quote, dominance test or reference term crosses the boundary any more,
and pcrec does no cost comparison. The section is kept as the record of
the design the r2 panel reviewed. What survives of it: the opacity
principle (§7.1's last paragraph: the kit never learns a site name,
pcrec never an ISA name), the fixed `portable` default (§7.2, HELD with
R4i), the UNOWNED-arm rule as the kit's K-4 (§8.6), and checks C1, C4,
C5 and C6, rebuilt in §10.

### 7.1 The principle: one fact crosses the boundary, and it is a price

Revision 1's boundary already kept classifiers, unrolling and the short
path inside the kit (§3.4). But it left pcrec reading three facts that only
an architecture can answer:

- whether a vector form exists here (`BASE`/`DECLARED`);
- how wide a vector is (`V`, in row 1's predicate);
- whether the vector form is worth it. This was left to "OWED placements"
  in pcrec's row order, which would have become measured thresholds in
  pcrec's tables.

K0 replaces all three with one question and one answer:

| pcrec knows | the kit knows |
|---|---|
| WHAT is scanned (S as a 256-bit set, a pinned pair, a run) and WHERE (the site, its budget, its handoff) | which kernels exist for a token, and for which set shapes |
| the proven span interval and, if any, a density interval | what each kernel costs, per call, per byte and per hit, on the token's calibration box |
| the cost SHAPE of its own scalar rows (one `memchr` stream, two leapfrogged streams, a table walk), as formulas | the measured value of every generic machine term those formulas read (a libc `memchr` call, a table-walk byte step, a restart) |
| the hook text (verify, fallback, bound, prefix) | the target-attribute, route, CPU-check and loader-marker text for a token |
| the decision: one comparison in one unit | nothing about pcrec's sites |

The kit never learns a pcrec site name (§3.4's rule, kept). pcrec never
learns an ISA name. The row that compares them is arch-blind by
construction, because both sides of the comparison come back from the kit
in the same unit.

### 7.2 The token

- **The grammar is the kit's.** pcrec's `--isa=TOKEN` (the `.rxt` `isa`
  config line; `pcrec_options.isa`, a string) is handed to
  `mf_token_parse`. An unknown token is refused with the kit's reason and
  its list (`pcrec --list-isas` prints `mf_tokens()`). pcrec holds the
  result as `const mf_token *`, an incomplete type whose only accessor
  pcrec may call is `mf_token_name()` (for the stamp). It cannot compare
  tokens, and the compiler enforces that.
- **The default is `portable`, fixed, never detected** (§R2 finding 3,
  Q18). `portable` is a COMPOSITE token. Its price list has one ARM per
  owned baseline: `x86-64-v1` (ubuntubudu) and `armv8-a` (the Mac). Its
  kernel text is the kit's gcc-time ladder over those arms. Its `#else`
  is pcrec's next row (§2.5, unchanged in substance). An unknown
  architecture compiles the `#else` and costs exactly the next row.
- **A declared token** (`x86-64-v3`, `armv8-a`, …) has one arm. Its
  kernels are one spelling inside a target-attributed matcher. Revision
  1's ROUTE (target attribute A, or the consumer's `-march` with an
  `#error` floor M, isa_selection.md §1.2.2) is folded into the token:
  `x86-64-v3` is route A, and `x86-64-v3+cc` (spelling Q21's) is route M.
  The kit owns the route's text. pcrec's designed `--isa-route` axis is
  withdrawn.
- **What pcrec does with the token, completely:**
  1. it passes the token to `mf_price` and `mf_emit` (§7.3);
  2. it stamps `<PREFIX>_ISA "<name>"` when the token is not the default
     (D46's "what was asked"; a default artifact is byte-identical);
  3. it injects the kit's opaque per-token text at four fixed places: the
     matcher's attribute (`mf_text_attr`), the `<prefix>_cpu_ok()` body
     (`mf_text_cpu_ok`), the level stamp ladder (`mf_text_level_stamp`)
     and, under `--isa-marker`, the loader note (`mf_text_marker`, or the
     kit's refusal). Each is a byte string pcrec does not parse.

  pcrec never branches on the token. §7.8 C4 checks that.

### 7.3 The API

`memfn/k0.h` (the kit's in-tree header, Q13). The shapes below are the
contract to build at R4a′. The field lists are complete for the
operations of §2.2. Names are PROPOSED.

```c
#define MF_K0_ABI 1                 /* bumped on any layout change below */

typedef struct mf_token mf_token;   /* opaque; pcrec cannot see inside */

/* -- tokens --------------------------------------------------------- */
int          mf_token_parse(const char *spelling, const mf_token **out,
                            char *why, size_t whylen);   /* 0 or MF_ERR_TOKEN */
const char  *mf_token_name(const mf_token *t);           /* stamp text only  */
size_t       mf_tokens(const char **names, size_t cap);  /* --list-isas      */
const mf_token *mf_token_default(void);                  /* "portable"       */

/* -- the question (architecture-neutral) ---------------------------- */
typedef enum {
    MF_OP_FIND_IN,      /* first i in [lo,hi) with s[i] in S                     */
    MF_OP_SKIP_IN,      /* first i in [lo,hi) with s[i] NOT in S                 */
    MF_OP_FIND_PAIR,    /* first i: s[i] in S1 and s[i+delta] in S2              */
    MF_OP_VERIFY_RUN,   /* (s[i+j] & mask[j]) == run[j] for j < len, one place   */
    MF_OP_ALL_PRESENT   /* every one of k sets has a member in [lo,hi)           */
} mf_op;

typedef enum {
    MF_H_RETURN,        /* stop at the first hit; return its index (or the bound) */
    MF_H_VERIFY_NEXT,   /* run the caller's verify per hit; continue on failure   */
    MF_H_ADVANCE,       /* write the cursor in place (skip forms)                 */
    MF_H_ALL_PRESENT    /* OR-accumulate seen sets; stop when all are seen        */
} mf_handoff;

#define MF_SPAN_UNBOUNDED UINT64_MAX
#define MF_PPM_FULL       1000000u   /* density interval default: [0, 1e6] */

typedef struct {
    uint32_t       abi;             /* MF_K0_ABI                                   */
    mf_op          op;
    mf_handoff     handoff;
    uint8_t        reverse;
    uint8_t        set[32];         /* S (FIND_IN/SKIP_IN/FIND_PAIR's S1)          */
    uint8_t        set2[32];        /* FIND_PAIR's S2                               */
    int32_t        delta;           /* FIND_PAIR: S2's offset from S1               */
    const uint8_t *run, *mask;      /* VERIFY_RUN                                   */
    uint32_t       run_len;
    const uint8_t (*sets)[32];      /* ALL_PRESENT: k sets                          */
    uint32_t       nsets;
    uint64_t       span_lo, span_hi;/* PROVEN bytes the operation may read;        */
                                    /*   span_hi = MF_SPAN_UNBOUNDED if none       */
    uint32_t       dens_lo, dens_hi;/* candidates per 1e6 bytes; default 0..FULL   */
    uint32_t       flags;           /* MF_Q_INLOOP (D91 budget 2);                  */
                                    /* MF_Q_PORTABLE_ONLY (no native kernels:      */
                                    /*   D122 add. 3's line, -fno-kit-native)      */
    const char    *deny;            /* --kit-deny's list, passed through unparsed  */
} mf_query;

/* -- the answer: a price list ---------------------------------------- */
typedef struct { int64_t lo, hi; } mf_ps;   /* picoseconds: min and median of N loops */

typedef struct {                    /* cost(r) = at_r0 + per_byte*(r - r0)/1000,    */
    uint64_t r0, r1;                /*   for r in [r0, r1); r1 = MF_SPAN_UNBOUNDED  */
    mf_ps    at_r0;                 /*   on the last segment. at_r0: ps per call    */
    mf_ps    per_byte;              /*   per_byte: fs per byte (ps x 1000), so a    */
} mf_seg;                           /*   0.020 ns/B slope is 20,000, not 20         */

#define MF_MAX_SEG 16
typedef struct {
    mf_ps    per_hit;               /* ps per candidate handled (VERIFY_NEXT only)  */
    uint32_t nseg;
    mf_seg   seg[MF_MAX_SEG];
} mf_curve;

typedef struct {
    char     kernel_id[48];         /* opaque; stamped; passed back to mf_emit      */
    mf_curve cost;
    uint32_t code_bytes;            /* exact source bytes of the injected call site */
    uint32_t helper_bytes;          /* shared text emitted once per artifact        */
    uint32_t needs;                 /* MF_NEED_BOUND_EXPR, MF_NEED_SCRATCH_LOCAL,   */
                                    /* MF_NEED_HELPER_ONCE: arch-neutral site       */
                                    /* obligations pcrec must be able to meet       */
} mf_quote;

#define MF_MAX_QUOTE 8
typedef struct {                    /* one architecture arm of the token           */
    char     arm_id[24];            /* opaque (e.g. a digest); never a branch input */
    int      status;                /* MF_PRICED / MF_UNPRICED / MF_STALE           */
    uint32_t nquote;
    mf_quote quote[MF_MAX_QUOTE];   /* in the KIT's preference order (C1 x C2)      */
    const struct mf_refterms *ref;  /* this arm's generic terms (§7.5)             */
    char     cal_id[24];            /* digest of the calibration rows read          */
} mf_arm;

#define MF_MAX_ARM 4
typedef struct {
    uint32_t abi;
    int      status;                /* MF_PRICED if any arm is; else MF_UNPRICED   */
    uint32_t narm;
    mf_arm   arm[MF_MAX_ARM];
    char     kit_version[16];
} mf_pricelist;

int mf_price(const mf_token *t, const mf_query *q, mf_pricelist *out);

/* the generic terms pcrec's own rows are priced from (§7.5) */
typedef enum {
    MF_REF_LIBC_MEMCHR,   /* one libc memchr call reading r bytes                 */
    MF_REF_LIBC_PAIR,     /* two leapfrogged libc memchr streams (today's pair arm)*/
    MF_REF_LIBC_RESTART,  /* re-entering memchr after a discarded hit             */
    MF_REF_LOOP_TABLE,    /* a byte loop testing a 256-entry table per byte       */
    MF_REF_LOOP_EQ,       /* a byte loop testing == per byte                      */
    MF_REF_CMP_WORD8,     /* one 8-byte masked word compare (runcmp's `words`)     */
    MF_REF_NTERMS
} mf_refterm;
const mf_curve *mf_ref(const struct mf_refterms *r, mf_refterm which);

/* -- generation (K2, unchanged in substance from §3.3) ---------------- */
typedef struct {
    void (*on_hit)(void *u, mf_sink *c, const char *cand_expr);
    void (*fallback)(void *u, mf_sink *c);   /* the next row's text: every #else */
    const char *bound_expr;
    const char *prefix;                      /* pcrec's D143 placeholder          */
    void *u;
} mf_hooks;

int mf_emit(const mf_token *t, const mf_query *q,
            const char *const *kernel_per_arm,   /* NULL entry = fallback on that arm */
            const mf_hooks *h, mf_sink *out, char *names, size_t nameslen);

/* -- per-token opaque text (§7.2 item 3) ----------------------------- */
int mf_text_attr(const mf_token *t, mf_sink *out);
int mf_text_cpu_ok(const mf_token *t, const char *prefix, mf_sink *out);
int mf_text_level_stamp(const mf_token *t, const char *prefix, mf_sink *out);
int mf_text_marker(const mf_token *t, mf_sink *out, char *why, size_t whylen);
```

**Versioning.**

- `MF_K0_ABI` covers the structs' layout and the meaning of every field.
  Every struct carries it first. pcrec checks it at build time
  (`_Static_assert(MF_K0_ABI == PCREC_K0_ABI_EXPECTED)`), because the kit
  is in-tree (Q13). After extraction to a vendored copy, the same assert
  pins the vendored version.
- `kit_version` names the kit's text. Any change to kernel text moves
  emitted bytes, so it is a pcrec `abi` event (D76/D94, unchanged from
  revision 1).
- `cal_id` names the calibration rows an arm's prices came from. A
  recalibration moves no kit text and no layout, but it can move
  SELECTIONS. Its governance is Q20.
- **Staleness is impossible by construction, not by discipline.** Every
  calibration row records the digest of the kernel TEXT it timed. When
  the kit's current text for a kernel differs from that digest, `mf_price`
  marks the arm `MF_STALE` and returns no quote for that kernel. A
  stale arm behaves like an UNPRICED one (§7.6), and C2 (§7.8) counts the
  stale kernels, which must be 0 at a release.

### 7.4 The common unit, and the shape of a price

- **The unit is integer picoseconds per call on the arm's calibration
  box.** It is the unit `litscan_k82b.md` §1.3 proposed for its cost
  terms (`limits.def` rows in `ps`), for the same reasons: integer and
  bit-exact. Revision 1 had no unit at all, because it had no comparison. Slopes are
  carried in femtoseconds per byte, so that `memchr`'s 0.020 ns/B is 20,000
  rather than a rounded 20.
- **The variable is `r`, the bytes the operation reads before it hands
  off.** For RETURN, `r` is the distance to the first hit, capped at the
  bound. For ADVANCE it is the run length. For VERIFY_NEXT it is the whole
  bound, and the hits along it cost `per_hit` each. For ALL_PRESENT it is
  the distance to the last first-occurrence. Both sides of a comparison
  read the same `r`, because both implement the same search with the same
  semantics.
- **The curve is piecewise affine with MEASURED breakpoints.** The
  calibration measures each kernel at a fixed ladder of read lengths:
  every length 1 to 64, then 128, 256, 512, 1 KiB, 4 KiB, 64 KiB and
  1 MiB. Between two measured lengths the price is linear interpolation.
  Beyond the largest, the slope is the one measured between 64 KiB and
  1 MiB. There are no fitted parameters and no smoothing. The dense
  1-64 ladder is there because block quantization makes the cost
  non-affine below twice any vector width (§7.11 item 2). Its breakpoints
  are merged into at most `MF_MAX_SEG` segments by dropping a point only
  when interpolating across it stays inside both neighbours' spreads.
- **Every value is a pair (lo, hi) = (min, median) of N ≥ 5 loops**, each
  loop ≥ 50 ms. That is D144 addendum 1's protocol and the bench's
  Contract 3 reporting. The harness's own loop cost (callcost's `loop`
  row, 0.30 ns on Linux) is measured in the same run and subtracted.
- **`code_bytes` is exact, not modelled.** The kit dry-runs K2 for the
  query and counts the source bytes it would inject (D84's unit). So a
  ladder's bytes, revision 1's Q16 worry, are inside the quote.
- **`needs` is arch-neutral.** It says what the site must provide: a
  bound expression, a scratch local, a once-per-artifact helper. pcrec
  drops any quote whose needs the site cannot meet, without knowing why
  the kernel needs them.

### 7.5 The arch-blind row, and how pcrec prices its own rows

**pcrec's own rows carry PRICE FORMULAS over generic terms.** A row knows
the shape of the text it emits, which is pcrec knowledge, arch-neutral.
It reads the VALUES of the generic machine terms from the same arm's
calibration (`mf_ref`), so both sides of every comparison were measured in
one run on one box.

| `SCAN_ROWS` row (§2.2 `[rev2]`) | handoff | price formula (curves add pointwise) |
|---|---|---|
| `libc-memchr` | RETURN | `LIBC_MEMCHR(r)` |
| `libc-memchr` | VERIFY_NEXT | `LIBC_MEMCHR(W)`, plus `LIBC_RESTART` per hit |
| `leapfrog` | RETURN / VERIFY_NEXT | `LIBC_PAIR(r)`, plus `LIBC_RESTART` per hit (the measured two-stream form, overshoot included: it is what `pair_libc` timed) |
| `table-walk` | RETURN / ADVANCE | `LOOP_TABLE(r)` |
| `table-walk`, T4 spelled `==` or a range | RETURN / ADVANCE | `LOOP_EQ(r)` |
| T6 `words` | (a verify) | `ceil(L/8) * CMP_WORD8` |

A structural check makes the price formula a required FIELD of every row
that can sit below `kit`. This follows `DfaPf.reseeds`' precedent ("so a
seventh form cannot be added without answering it"). A row with no
formula cannot be the comparison's other side, and the build fails rather
than the row being silently skipped.

**The row** (`SCAN_ROWS` row 1, and T6's row before `words`):

```c
/* pcrec side. Reads no ISA fact: every number comes back from the kit. */
static bool kit_applies(const ScanSel *s, KitPick *pick)
{
    const ScanRow *next = scan_next_applicable(s, &ROW_KIT); /* structural walk */
    mf_query q;  scan_query_of(s, &q);       /* operands + proven facts, §7.6    */
    mf_pricelist pl;
    if (mf_price(s->cx->isa, &q, &pl) != MF_PRICED) return false;

    bool any_win = false;
    for (uint32_t a = 0; a < pl.narm; a++) {
        pick->kernel[a] = NULL;                       /* NULL: this arm falls back */
        if (pl.arm[a].status != MF_PRICED) continue;  /* fallback = a tie          */
        mf_curve mine;  next->price(s, pl.arm[a].ref, &mine);
        for (uint32_t k = 0; k < pl.arm[a].nquote; k++) {   /* the KIT's order     */
            const mf_quote *qt = &pl.arm[a].quote[k];
            if (!site_meets(s, qt->needs)) continue;
            if (!mf_dominates(&qt->cost, &mine, &q)) continue;
            pick->kernel[a] = qt->kernel_id;  any_win = true;  break;
        }
    }
    if (!any_win) return false;
    if (tune_size_leaning(s->cx) && kit_bytes(pick) > next->bytes(s))
        return false;                       /* D139 item 1: only if smaller */
    return true;
}
```

**Dominance, exactly.** `mf_dominates(K, N, q)` holds iff three things
are true:

1. **(i)** `K.hi(r, d) <= N.lo(r, d)` at every corner. The corners are the
   points `(r, d)` with `r` in the union of both curves' breakpoints
   inside `[span_lo, span_hi]` plus the two ends, and `d` in
   `{dens_lo, dens_hi}`.
2. **(ii)** If `span_hi` is unbounded, the same inequality also holds for
   the last segment's slope plus `d · per_hit`, at both values of `d`.
3. **(iii)** At least one corner is strict.

The `per_hit` term counts only under VERIFY_NEXT. With
`hits = d · r / 10^6`, the difference `K − N` on any segment has the form
`a + b·r + c·d·r`. That is bilinear, so its maximum over a rectangle is
at a corner, and the corner check is a PROOF over the whole box, not a
sample. The arithmetic is in `__int128`, exact. Test vectors ship with the
function, as `L(x)`'s do (findb4).

**Why this is not a tuned cutoff (D119, D144, the K82 ruling).**

- There is no threshold anywhere in pcrec. Every number is a measured
  machine quantity, regenerated by a pattern-blind, bench-blind probe.
- The verdict reads only the SIGN of a difference, so uniform scaling of
  an arm's prices moves nothing. §7.8 C7 tests that.
- The only modelled step is interpolation between measured lengths, and
  C2 checks it.

**The worked example (Linux, `linux_results.md` §1).** Take the K82 pair
arm (`leapfrog`, RETURN) against a fused two-needle kernel on the
`x86-64-v1` arm. The kernel reads 1.48-3.29 ns up to 64 B. `LIBC_PAIR`
reads 7.08-8.26 ns there. At 4 KiB the kernel reads 157.8 ns and
`LIBC_PAIR` 110.2.

- At an OFS site whose run window proves a span of 64 B or less, the
  kernel dominates and is selected.
- At a rest-of-subject site, (ii) fails on the last segment's slope, so
  the row does not apply and `leapfrog` stays.
- At the same site under a declared `x86-64-v3` token, a quote for an
  AVX2 unrolled body (RB-7) would be priced separately. It wins iff its
  own measured slope beats `LIBC_PAIR`'s.

pcrec reads none of those facts. The crossover revision 1 would have
encoded as "OWED placement" (§2.2 row 4) is a consequence of two price
lists.

### 7.6 The defaults: unpriced tokens, unproven spans, unknown density

| situation | the kit's answer | what pcrec does |
|---|---|---|
| the token's only arm is unowned (`x86-64-v4`, `armv8-a+sve`, `+sve2`) | `MF_UNPRICED`, no quotes | the row does not apply. The artifact is byte-identical to its `-fno-kit-*` twin except the `<PREFIX>_ISA` stamp. An unpriced token is never selected, by construction |
| a composite token with one arm unpriced (e.g. `portable` before Q19's armv8-a ruling) | that arm `MF_UNPRICED`; the others priced | the unpriced arm falls back (its `#else` is the next row, a tie). The row can still apply on the priced arms' wins |
| a kit kernel's text changed since calibration | that arm `MF_STALE` for that kernel | as UNPRICED for that kernel |
| no kit in the tree yet (before R4a′), or a stub K0 | `MF_UNPRICED` for every token | the row never applies, so zero movers. The stub is R4c's implement-then-replace starting point |
| an arm has quotes but none dominates | `MF_PRICED`, quotes returned | that arm falls back. The row applies only if some other arm wins strictly |
| no proven upper bound on the span (rest of subject) | — | `span_hi = MF_SPAN_UNBOUNDED`; dominance must hold on the last segment's slope (§7.5 (ii)) |
| a proven bound (`maxw`, a counted edge's span, the D11 `n − 1` view, a run window) | — | `span_hi` = that bound. A loop-free kernel the kit quotes only when `span_hi` fits it, so pcrec never sees `V` |
| density unknown (the default) | — | `[dens_lo, dens_hi] = [0, MF_PPM_FULL]`. Only VERIFY_NEXT and ALL_PRESENT read it; RETURN and ADVANCE compare on `r` alone (§R2 finding 2) |
| density known from a findings bundle | — | the interval narrows to the bundle's rate bounds. Never required; K82's parked expected-cost model is not a dependency (Q23) |
| an in-loop site (D91 budget 2) | quotes priced from the IN-LOOP calibration (`MF_Q_INLOOP`): the kernel entered hot, back to back, at the site's re-entry pattern | deny bit `-fno-kit-loop`. Until U-3 measures a real emitted in-loop site, the in-loop calibration is unbuilt, so in-loop queries answer UNPRICED |

So the kit's default is **no assumption**: the full density interval, an
unbounded span when nothing is proven, and no price where no house box
measured one.

### 7.7 The calibration data: provenance, format, regeneration, ownership

**Layout** (in-tree under the kit, Q13; `third_party/`'s shape applied to
data derived by MEASURING, as `oracle_store/` applies it to data derived
by RUNNING a library):

```
memfn/cal/
  CLAUDE.md
  calibrate.c          the probe: times K2-EMITTED kernel text and the
                       generic reference forms, per arm, on the box it runs on
  run_calibrate.sh     pinning (taskset on Linux), quiet-box checks (load1
                       before/after, recorded), N >= 5 loops >= 50 ms each
  <arm>/               one directory per ARM (x86-64-v1, x86-64-v3, armv8-a)
    PROVENANCE.md      box, CPU, OS, libc, compiler + flags, governor, date,
                       commit, probe digest, and WHAT DERIVES FROM IT
    raw/<run-id>.txt   the probe transcript, verbatim, with its header
    generate.py        raw -> prices.tsv; interpolation and segment merge only
    prices.tsv         the derived table (table-contract TSV)
  prices.inc           every arm's prices.tsv as C data; generated, committed
```

**`prices.tsv`** has three `#section` blocks (`docs/spec/table_contract.md`):

- `arm`: one row per arm. The columns are `arm  owner_box  status
  cal_id  run_id`, where status is `PRICED`, or `UNPRICED` with a reason.
- `kernels`: one row per (kernel, query class, segment). The columns are
  `kernel_id  text_digest  op  handoff  shape  inloop  r0  r1
  at_r0_lo  at_r0_hi  per_byte_lo  per_byte_hi  per_hit_lo  per_hit_hi`.
  The `shape` column holds the kit's C1 row name. That keeps it opaque to
  pcrec, and it is how the kit maps a query's set onto its rows.
- `reference`: one row per (term, segment), with the same cost columns.

**Regeneration.** `make -C memfn gen-cal` iterates `cal/*/generate.py`
and names no arm (`make gen-tables`' general rule). `generate.py --check`
regenerates into memory and fails on any difference. It runs in the
kit's own `make test`, so a hand-edited `prices.tsv` goes red. The raw
transcript is the only measured artifact. Everything downstream is
derived and checked.

**Ownership** (option_sets.md §3.5a's table, now a CALIBRATION table):

| arm | owner box | runs the calibration | status |
|---|---|---|---|
| `x86-64-v1`, `-v2`, `-v3` | ubuntubudu (Zen 1, glibc 2.43) | the manager, through pcrecdev2's executor channel (heavy Linux runs), on a quiet box | PRICED once measured |
| `x86-64-v4` | none (no AVX-512 box) | — | **UNPRICED** |
| `armv8-a` | the Mac (M1 Max, libSystem) | a lane, in a quiet Mac window | PRICED on Q19's ruling, else UNPRICED |
| `armv8-a+sve`, `+sve2` | none | — | **UNPRICED** |
| `portable` | composite: `x86-64-v1` + `armv8-a` | — | priced per arm |

An emulator (Intel SDE, `qemu-user`) can prove CORRECTNESS for an
unowned arm (option_sets.md R6). It can never price one: emulated time
is not the target's time. So v4/SVE stay UNPRICED until a real box
exists, and an unpriced arm can never select a kernel. That is the safe
direction.

**Relation to D141 ([EST-REGISTRY]).** The kit's `prices.tsv` is an
estimates registry for one domain, built in the shape D141 asks for (a
value, a unit, a kind that is FITTED, and provenance). pcrec gains NO
estimation constant from K0: its side of the comparison is formulas over
kit-supplied terms. D141's census, when scheduled, finds nothing new in
`src/` for this mechanism.

### 7.8 Testability

| # | check | what it proves | shares a source with the calibration? |
|---|---|---|---|
| C1 | every kit kernel against the SCALAR BYTE LOOP, exhaustive per length × alignment × position, guard pages, ASan/UBSan (§4.5, N-6) | answers | no |
| C2 | **price against measurement**: `memfn/cal/verify` times the kernels with its OWN driver, at read lengths the calibration ladder did NOT use (midpoints of every segment). Each measured value must lie inside the quote's (lo, hi), widened by the verifier's own measured spread. It also counts `MF_STALE` kernels (must be 0 at a release) | the interpolation rule and the data's currency | partly: it shares the kernel text and the box, but not the driver, the lengths or the loop code. It is the kit's own check, not the control |
| C3 | **THE CONTROL: decision order end to end.** On the owner box, over the population of every corpus site where `kit` is selected, plus every site where an arm was priced and lost, build each artifact default and with `-fno-kit-*`, and time both with the harness's find-all driver on corpus subjects (D144 add. 1 loops; the floor is base vs base). Where the prices predict a win beyond both spreads, the measured kit arm must not be slower than the deny arm past the floor. Where they predict a loss, the forced arm (`kit-scan=force`, below) must not be faster past the floor | that pcrec selects only where it wins, which is the claim the row makes | **no**: the subjects are different (corpus text, not synthetic spans), the driver is different (generated artifacts through the shipped API, not `calibrate.c`), and so are the code paths (the kernel inside a real matcher with pcrec's hooks, not isolated). It shares only the box, which is unavoidable and named |
| C4 | **arch-blindness detector**: `src/`, `cli/`, `lib/` contain no ISA vocabulary outside a committed allowlist counted at birth (D107's shape), and no `strcmp`/`==` on `mf_token_name(`. A new hit fails. The vocabulary is `grep -rniE '\b(sse[0-9.]*\|ssse3\|avx[0-9a-z]*\|neon\|sve2?\|x86-64-v[1-4]\|armv8[a-z.+-]*\|aarch64\|__x86_64__\|__arm_neon\|__avx2__\|pshufb\|x86_64\|arm64)\b'`. At 68acba37 it finds ONE hit (`src/opt/prefix_k.c:45`, a comment citing glibc's AVX2 `memchr` measurement), so the allowlist is born with one row | Frank's "as much as possible" as a red test | n/a |
| C5 | **unpriced never selects**: the corpus compiled at `--isa=x86-64-v4` and `--isa=armv8-a+sve` carries no `kit` selection, and is byte-identical to `-fno-kit-scan -fno-kit-loop` except the `<PREFIX>_ISA` stamp | §7.6's first row | no |
| C6 | answer identity per deny, per box: `make test-axes` arms for the three bits; option_sets.md §3.5a's compile-only arms per token | correctness under every selection | no |
| C7 | **ratio invariance**: scaling every price in one arm by 2, or by 1/2, flips 0 selections over the corpus census (k82b §1.4's shape) | the decision depends on the SIGN of a difference only, so a uniformly mis-scaled arm (a whole box running slow) moves nothing. A NON-uniform slip (one term in the wrong unit) is not this check's: C2 and C8 catch it, because their measured and fixture numbers stay in the true unit | n/a |
| C8 | the dominance unit test, on the committed Linux numbers as a fixture: the fused pair kernel against `LIBC_PAIR` SELECTS at `span_hi = 64` and does NOT select at `MF_SPAN_UNBOUNDED`. Plus a crossing pair that differs only at an interior breakpoint, which a two-endpoint check would pass | the corner proof, including the interior breakpoints and the slope arm | uses calibration numbers as fixtures by design |

**Forcing (D46's controllability half).** `kit-scan` and `kit-loop` are
three-valued axes (option_sets.md §2.4a): deny, auto and force. Under
force, the row takes the kit's first quote whose `needs` the site meets,
regardless of price. If the kit returns no quote (an UNPRICED token, or
an unsupported shape), the force cannot be honoured. The compile is then
refused, with the kit's reason. That refusal replaces option_sets.md's
constraint row 8 (`forced-row-below-level`) and is arch-blind: pcrec
refuses because the answer was empty, not because it knows a level.
`--kit-force=KERNEL_ID` (opaque, kit-validated) pins one kernel for C3's
loss arm and for the kit's bench.

**Sabotage rows** (ids taken at build, highest S on main + 1):

- one kernel's prices ×0.1 in `prices.inc` (C3 fires; C2 fires);
- an ISA word added to `src/gen/emit_dfa.c` (C4);
- `mf_price` returning PRICED for an unowned arm (C5);
- a kernel's text edited without recalibration, with the staleness
  digest check removed (C2's stale count);
- `mf_dominates` checking only the two ends of the span interval (C8's
  interior-crossing vector);
- one arm's `per_byte` read as ps instead of fs (C2: the verifier's
  measured midpoints leave the quote; C8: the committed fixture's
  selection flips at `span_hi = 64`).

### 7.9 What K0 removes

**From §2 (pcrec's per-site vector rows):**

| revision 1 | revision 2 |
|---|---|
| `SCAN_ROWS` rows 1-3 (`loopfree`, `vec-verify`, `vec`) and row 6 (`swar`) | ONE row, `kit`. The short path, the verify fusion, the vector scan and SWAR are all kit kernels. SWAR is a kernel of the PORTABLE class (`-fno-kit-native` keeps it) |
| row 1's predicate on `V`, the kit's short-path width | gone. The kit quotes a loop-free kernel only when `span_hi` fits it |
| row 4's OWED placement of `libc-memchr` against `vec` | gone. It is a price comparison, decided by data (§7.5's example) |
| the `BASE`/`DECLARED(L)` predicate vocabulary (§2.1) | gone. The token is passed, never read |
| the §2.5 ladder as a pcrec emission | kit text. The `fallback` hook (pcrec's next row) is unchanged |
| T6's `vec-masked` with an `rc_holds(cx, …)` ISA predicate | T6 gains the same `kit` row with `MF_OP_VERIFY_RUN`. `rc_holds` still needs `cx`, for the token and the prices, not for an ISA |
| `<PREFIX>_SCAN_FORM` = a C1/C2 row-name pair | `<PREFIX>_SCAN_FORM` = the kit's opaque `kernel_id` per arm, emitted only where `kit` was selected (movers only, k82hrev Q3's precedent) |

**From [OPT-SETS] (`docs/design/option_sets.md`)**: the "arch
sub-panels".

| option_sets.md item | revision 2 |
|---|---|
| §1.2 vector-row denies: `-fno-vec-scan`, `-fno-vec-skip`, `-fno-vec-run`, `-fno-swar-scan` (four bits) | three bits: `-fno-kit-scan` (D91 budget-1 sites, T6 included where it is a prefilter verify), `-fno-kit-loop` (budget-2 sites), `-fno-kit-native` (portable-class kernels only: D122 addendum 3's line, the bench's SIMD-off testee). They are named for budgets and kernel class, never for an ISA |
| §1.2 `--memfn-deny=cube,unrolled,…` | `--kit-deny=`, the same list, passed through UNPARSED (`mf_query.deny`). pcrec cannot spell a classifier |
| §1.2 / §4.3 the `isa` family: an 8-member POSET pcrec holds | one opaque value axis whose domain is `mf_tokens()`. The order, the chains and the members live in the kit. `--list-sets` lists `isa` members from the kit |
| §1.2 `isa-route` (`--isa-route=macro`) | withdrawn; folded into the token (Q21) |
| §1.2 `-fisa-check=entry`, `-fisa-dispatch=cpu-supports` | the CPU-check text is `mf_text_cpu_ok`. A dispatched kernel (isa_selection.md row 5, H2) is a kit kernel quoted with its measured dispatch term inside its price, under a token that names it. It stays HELD (Q11) |
| §1.2 `--isa-marker` | stays a pcrec boolean (explicit-only, §2.8). Its validity is the kit's answer (`mf_text_marker` refuses with a reason) |
| §2.7 constraint row 6 `isa-route-orphan` | removed (no route axis) |
| §2.7 constraint row 7 `isa-marker-orphan` ("not on the x86 chain") | removed. The kit's refusal replaces it, and pcrec no longer knows what an x86 chain is |
| §2.7 constraint row 8 `forced-row-below-level` | removed. The arch-blind "force with an empty quote list" refusal (§7.8) covers it, for every token |
| §4.2 the `vector` family's four members over four bits | `auto`; `no-simd` = `-fno-kit-native`; `scalar` = `-fno-kit-scan -fno-kit-loop`. A two-bit set at most. option_sets.md §0 item 8's "first consumer is [MEMFN] R4's vector rows" mostly evaporates: trigger 1 (one name over two or more vector-family bits) is met only by `scalar` |
| §4.2's `vector` × `isa` interaction table | gone. Both axes are inputs to one kit query, and the kit's answer is the whole table |
| §3.5's `vector` × `isa` sweep (4 × 8 = 32 corpus runs, floored) | three deny arms × each box's own priced tokens. The compile-only arms per token stay (§3.5a) |
| §3.5a ISA ownership | unchanged in substance, now the calibration ownership table (§7.7) |

**From isa_selection.md §2's first-match table** (pcrec-side ISA
selection): rows 1 (below the knee: baseline), 4 (in-loop: baseline only)
and 6 become price OUTCOMES. A wide kernel that cannot pay on the site's
span loses dominance. Row 3 (declared) is the token. Row 5 (H2 dispatch)
is a kit kernel. Row 2 (libc) is the reference terms. The table moves
into K0 entire. pcrec keeps no ISA selection table.

### 7.10 How pcrec's existing tables change

| table | change under revision 2 |
|---|---|
| T1 `dfa_pfs[]` | none of its own (as revision 1). Its emitters ask `SCAN_ROWS` at PF/OFS. §2.4(e) is still owed: G1's `memchr_form` premise becomes a property of the chosen `SCAN_ROWS` row, and that row may now be `kit` |
| T2 `req_admits[]` | none. G1's density clause must read the SCAN form's per-hit price class, not `strcmp` on a name (§2.4 e) |
| T3 `dfa_edges[]` | none. The edge's loop asks `SCAN_ROWS` at EDGE; ADVANCE handoff, budget 2 |
| T4 `ROWS` | none. The scalar spelling feeds `table-walk` and `LOOP_EQ`/`LOOP_TABLE`'s choice of formula, and S becomes `mf_query.set` |
| T5 `TAB_ROWS` | none |
| T6 `pcrec_runcmp_rows` | gains `kit` (op VERIFY_RUN) before `words`. Its next row's formula is `ceil(L/8)·CMP_WORD8`. Exact runs still get no row (gcc's `memcmp`, revision 1's reason) |
| T7 `pcrec_find_pick` | none. It may supply the density interval, optionally |
| T8, T9 | excluded (as revision 1) |
| `SCAN_ROWS` (new, §2.2) | four rows instead of seven: `kit`, `libc-memchr`, `leapfrog`, `table-walk`. Each non-`kit` row carries a price formula field |
| N1-N7 | as revision 1's §2.3/§2.4, with `kit` in place of rows 1-3 and 6 |
| the dial (`src/core/tune.c`) | two new axes join the pinned table: `kit-scan` and `kit-loop`, `auto` at every position. The size-leaning positions get D139's "only if smaller" through the row's own bytes clause (§7.5), not through a cell |
| `limits.def` | none from K0. If [K82]'s parked model is ever built, its `ps` terms would read `mf_ref` rather than adding rows (Q23) |

### 7.11 What is honestly uncertain

1. **Microbenchmark prices against in-situ cost.** A kernel inside a
   matcher pays alignment, register pressure and the hook's verify. The
   calibration times K2-emitted text inside a generated function, which
   is closer than K1 primitives, but it is not the matcher. C3 is what
   would show a systematic in-situ penalty. If it does, the remedy is an
   in-situ calibration column, never a correction factor.
2. **Interpolation below twice the vector width.** Block quantization
   makes cost a step function there. Hence the dense 1-64 B ladder and
   C2's midpoint samples. A kernel whose curve steps between ladder
   points would fail C2 rather than mis-select silently.
3. **The libc is the calibration box's.** `LIBC_*` prices glibc 2.43 on
   ubuntubudu and libSystem on the Mac. A consumer on musl inherits
   those decisions (Q22).
4. **`portable`'s conjunction.** A composite token needs a win on at
   least one arm, and the losing arms fall back. That is safe, but it
   doubles calibration and makes the ladder's bytes count against every
   arm's size gate.
5. **Compile-time cost.** One `mf_price` per candidate site is table
   lookups plus a dry-run K2 for `code_bytes`. That is unmeasured: R4c
   measures it under D45 before the row ships.
6. **The K82 ruling's spirit.** Frank parked K82's expected-cost model
   for simplicity. K0 is a cost comparison too. It differs in needing no
   rates (no W, no density prior, no bundle), only proven bounds. That
   is argued in §R2 and is Q23's to confirm.

---

## 8. THE DELEGATION CONTRACT `[rev3]`

### 8.1 The principle: a site crosses the boundary, and code comes back

| pcrec knows, and says | the kit knows, and decides |
|---|---|
| WHAT is searched: a predicate over positions (byte sets and masked runs at offsets from a candidate), from pcrec's single sources (P2 cube, T4 sets, P3 runs, the k-set derivation) | HOW: which term to scan and which to verify, the classifier per set shape, unrolling, the loop-free short path, a libc call vs inline vs injected text, the ISA ladder, SWAR vs vector, the always-present scalar arm |
| WHERE and under what PROOF: the site's D91 budget, its bound expressions, its proven span `[span_lo, span_hi]`, anchoring, the read limit | what those proofs buy: a span short enough for a loop-free path, an anchored site needing no loop at all |
| a density HINT per term and per predicate (pcrec's prior, encoding-gated) | what density does to its choice (iterate in place vs restart per hit, unroll factor) |
| the HANDOFF: what happens at a result (return it, advance a cursor in place, run pcrec's verify per candidate and continue on failure, or answer a presence boolean) | how the handoff is fused into its loop |
| the PROFILE asked for (§8.5): `baseline`, `portable` or `native`, and the opaque pass-throughs (`--memfn-deny=`, `--isa=`) | what each profile means in code, and every measurement behind its choices |

Neither side crosses into the other's column. The kit never learns a
pcrec site name or engine (§3.4's rule, kept). pcrec never learns an ISA,
never reads a cost, and never inspects the code it gets back: the text
goes from the kit's sink into pcrec's artifact unread.

### 8.2 The site description (C shapes, versioning)

`memfn/include/memfn.h`, the kit's ONLY public header (§11.1). Names
are PROPOSED; the shapes are the contract R4a builds. Every field is
architecture-neutral.

```c
#define MF_SITE_ABI 1   /* layout and meaning of every struct below           */
#define MF_VOCAB    1   /* the operation vocabulary: op x handoff x term kinds */

typedef enum {
    MF_OP_FIND,         /* first cand in [lo,hi) satisfying the predicate (last, if reverse)  */
    MF_OP_SKIP,         /* first cand in [lo,hi) whose byte is NOT in the one SET term       */
    MF_OP_VERIFY,       /* does the predicate hold at cand == lo (an anchored site)          */
    MF_OP_ALL_PRESENT   /* does EVERY one of npred predicates hold somewhere in [lo,hi)      */
} mf_op;

typedef enum {
    MF_H_RETURN,        /* write the result (or the miss value) to `result`                  */
    MF_H_ADVANCE,       /* move `cursor` in place with pcrec's own step text (skip forms)    */
    MF_H_ON_CAND,       /* per candidate, run pcrec's verify; continue on reject             */
    MF_H_BOOL           /* write 1/0 to `result` (VERIFY, ALL_PRESENT)                       */
} mf_handoff;

typedef enum { MF_T_SET, MF_T_RUN } mf_term_kind;

typedef struct {                    /* one position term, relative to cand          */
    mf_term_kind   kind;
    int32_t        offset;          /* bytes from cand; the term reads s[cand+offset..] */
    uint8_t        set[32];         /* MF_T_SET: 256-bit membership                    */
    uint32_t       table_ref;       /* MF_T_SET: pcrec's table-name hook id, or 0 (§8.3) */
    const uint8_t *run, *mask;      /* MF_T_RUN: (s[cand+offset+j] & mask[j]) == run[j] */
    uint32_t       run_len;
    uint32_t       ppm_lo, ppm_hi;  /* density hint: matches per 1e6 subject bytes;
                                       0..MF_PPM_FULL when unknown (the default)   */
} mf_term;

#define MF_MAX_TERM 8
typedef struct mf_pred {            /* a CONJUNCTION of terms                        */
    uint8_t  nterm;
    mf_term  term[MF_MAX_TERM];
    uint8_t  plan_hint;             /* TRANSITIONAL (§9.4): the term pcrec's model
                                       scans today; 0xFF = none                     */
} mf_pred;

typedef struct {
    uint32_t        abi;            /* MF_SITE_ABI                                   */
    mf_op           op;
    mf_handoff      handoff;
    uint8_t         reverse;
    mf_pred         pred;           /* FIND / SKIP / VERIFY                           */
    uint8_t         npred;          /* ALL_PRESENT                                    */
    const mf_pred  *preds;
    /* pcrec's proven facts */
    uint64_t        span_lo, span_hi;   /* proven bytes in [lo,hi); MF_SPAN_UNBOUNDED  */
    uint32_t        cand_ppm_lo, cand_ppm_hi;  /* the whole predicate's hint           */
    uint8_t         consumer;       /* MF_C_RESULT / MF_C_ENGINE: is a false candidate
                                       handed to a matcher that then rejects it?
                                       named, never priced (§9.4)                     */
    /* policy (§8.5): every bit arch-neutral */
    uint32_t        policy;         /* MF_P_BASELINE | MF_P_PORTABLE_ONLY |
                                       MF_P_INLOOP | MF_P_SIZE_LEANING               */
    const char     *deny;           /* --memfn-deny=, passed through unparsed        */
    const char     *token;          /* --isa=, passed through unparsed; NULL = the
                                       fixed default (§R2 finding 3), HELD (R4h)     */
} mf_site;

typedef struct {
    char     form_id[48];           /* opaque; stamped on movers only (§10.3)         */
    uint32_t helpers;               /* once-per-artifact helpers the text names        */
    uint8_t  moved;                 /* 1 iff the text differs from this site's
                                       BASELINE text (computed by the kit; §10.5 C11) */
} mf_result;

int mf_emit_site(const mf_site *s, const mf_hooks *h, mf_sink *out,
                 mf_result *res, mf_arena *a);          /* 0, or a LOUD internal error */
int mf_emit_helpers(uint32_t helpers, const char *prefix, mf_sink *out);
int mf_vocab_has(mf_op op, mf_handoff h, uint32_t term_kinds); /* compile-time constant */
const char *mf_kit_version(void);                       /* "pcrec-memory-functions X.Y.Z" */
```

> **`[rev4]`** These shapes are EXTENDED by §14.0 (r3 F1-F11): three
> site forms, `end_back`/`empty`, `floor`, REQUIRED/OPTIONAL terms,
> ALL_PRESENT's `ret_pred`, `denies`, and a plan/render split whose
> `mf_plan` reports form tallies, helpers and includes. `plan_hint` is NOT
> transitional (§14.9). `mf_result.form_id` is no longer stamped with a
> kit version (§18).

**Size (K3).** An `mf_site` is about 0.6 KB at `MF_MAX_TERM` 8 (32-byte
sets dominate). `preds` and runs are pointers into pcrec's arena. The kit
allocates nothing on the caller's stack beyond its frame and takes
scratch from `mf_arena`, which pcrec backs with its own arena. C10
(§10.5) forbids an `mf_site` or `mf_result` as an automatic variable
under `src/`.

**Versioning.** Three numbers, three meanings:

- `MF_SITE_ABI` covers layout and field meaning. pcrec asserts it at
  build (`_Static_assert(MF_SITE_ABI == PCREC_MF_SITE_ABI)`). In-tree
  (§11.1) the assert can only fail inside one commit.
- `MF_VOCAB` grows when an operation, handoff or term kind is ADDED
  (§8.4's request path). pcrec's delegation table (§8.5) is checked
  against `mf_vocab_has` at build: a site whose op the kit's vocabulary
  lacks is a build failure, never a silent pcrec fallback.
- `mf_kit_version()` names the kit's TEXT. A kit change that moves any
  byte pcrec emits is a pcrec `abi` event (§10.3). A kit change that
  moves no pcrec byte (a new op nobody requests yet, a K3 CLI feature, a
  test) is not.

**Totality.** For every request inside its vocabulary, the kit MUST
return code. A decline is a kit defect and pcrec fails loudly
(`pcrec_ctx_fail`, the house's internal-error tier). There is no "kit
declined, pcrec spells it itself" path: after a site's migration step
pcrec HAS no spelling of its own (§9), and keeping one would be the
second scalar spelling D122 forbids.

### 8.3 The hook contract

pcrec owns the names, the bounds and the code AROUND a site. It passes
them as TEXT, never as callbacks into the generated program. The kit
renders them into the site's code.

```c
typedef struct {
    /* the subject and its bounds: side-effect-free C expressions */
    const char *s;          /* the subject pointer                                    */
    const char *n;          /* the READ LIMIT: no byte at or past it is ever read        */
    const char *lo, *hi;    /* search start, exclusive end (D11's n-1 views pass here)   */
    /* RETURN / BOOL */
    const char *result;     /* the lvalue written                                       */
    const char *miss;       /* the value written when no cand exists (each site's own:
                               n, hi, -1 …; baseline arms need it byte for byte)         */
    /* ADVANCE */
    const char *cursor;     /* the cursor lvalue                                        */
    const char *step;       /* pcrec's step statement (`pos++`, `pos--`, …)              */
    const char *more;       /* pcrec's continue condition (its direction's scan_more)    */
    /* ON_CAND: pcrec's per-candidate verify */
    void (*on_cand)(void *u, mf_sink *c, const char *cand);
    uint32_t on_cand_reach; /* bytes on_cand reads at or after cand                      */
    /* one-position membership: T4 stays pcrec's */
    const char *(*member)(void *u, uint32_t term, const char *byte_expr);
    const char *(*table_name)(void *u, uint32_t table_ref);
    /* rendering */
    const char *prefix;     /* pcrec's D143 placeholder, rendered after emission         */
    int comment_tier;       /* PCREC_CMT_* passes through                                */
    void *u;
} mf_hooks;
```

**The rules, each with the check that holds it** (§10):

1. **Expressions are pure.** `s`, `n`, `lo`, `hi`, `more` and the member
   text may be evaluated any number of times, in any order. Only `step`
   has an effect. A kit arm that hoists `n` into a local is legal; a pcrec
   hook with a side effect in `hi` is a pcrec defect.
2. **The read guard is the kit's.** The kit never reads `s[k]` for
   `k >= n` or `k < 0`, for any term offset, any vector width, any tail
   (P8's rule, S-2: no aligned-down over-read). When `on_cand` runs, the
   kit has ALREADY established `cand + on_cand_reach <= n`. Held by the
   kit's guard-page tests (§10.2) with synthetic hooks that read exactly
   `on_cand_reach` bytes.
3. **The RETURN contract.** `result` = the LEFTMOST `cand` in `[lo, hi)`
   (the rightmost, if `reverse`) at which every term holds and every term
   read is below `n`, else `miss`. This is litscan_k82h.md §1.1a's
   written gate contract ("leftmost occurrence ≥ `search_from`") made
   the kit's, so the K82 handoff's soundness argument (`lo = max(f,
   c − K)`, that note's §1.2) reads the kit's result unchanged.
   > **`[rev4]`** Restated over REQUIRED and OPTIONAL terms (§14.5,
   > r3 F7): `c` is at most the true leftmost, and every REQUIRED term
   > holds at `c`. Rule 2 gains the expression-form caller guard and the
   > lower `floor` (§14.7).
4. **ON_CAND.** `on_cand`'s text ends in exactly one of two kit-rendered
   tokens, `\x01mfA` (accept) or `\x01mfR` (reject). Accept writes `cand`
   as the result. Reject resumes the search at `cand + 1` (`cand − 1`
   reversed): no candidate is skipped and none is revisited. The hook may
   name only `cand`, the hook expressions above, and pcrec's own locals
   declared OUTSIDE the site. The kit's own locals are block-scoped and
   carry the prefix placeholder, except inside BASELINE arms, which
   reproduce pcrec's pre-migration names exactly and declare them in the
   kit's baseline manifest (§9.2).
5. **ADVANCE.** The kit's loop is `while (more && member(byte at cursor))
   step;` in meaning. The text may differ (a vector body, a counted span),
   but the cursor ends at the first non-member position, or where `more`
   fails, and every `step` effect is the one pcrec gave. A counted span
   (the scan edge's `{0,n}`) is a proven `span_hi`, not a hook.
6. **Membership has ONE owner per granularity.** A ONE-POSITION test of a
   set is T4's (`member`), unchanged: the kit's scalar loop arms call
   back for it, so a set has one scalar spelling in the artifact. A
   MANY-LANE classifier of the same set is the kit's own (§4.3's C1).
   The `set[32]` bits are the truth both must agree with (§10.2's
   agreement check).
7. **Tables stay pcrec's.** A SET term may carry `table_ref`, naming a
   256-byte table pcrec already emits (`can_begin_match`, `stay<K>`,
   `scan<N>`). Baseline arms read it by name. Other arms may ignore it.
   The kit never emits a second copy of a table pcrec emits.
8. **The handoff into the DFA is pcrec's text AFTER the site.** The kit
   returns `c`; pcrec writes `lo = max(search_from, c − K)` and enters
   the engine. Nothing in the kit knows an engine exists. `consumer`
   tells the kit only whether a false candidate costs a later matcher
   anything, so it can weigh verifying harder (§9.4).

**What dissolves.** Revision 1's `fallback` hook (§2.5): the `#else` of
any ladder is the kit's own portable arm, and pcrec, after migration,
has no scalar text to offer. Revision 1's risk item 1 (§3.3, "the hook
contract is the riskiest surface") stands, now with rules 1-5 and their
checks. The first mover (§12.2 R4d) uses only RETURN, so ON_CAND's first
customer is a later step.

### 8.4 Compound work: "this check followed by this check"

D146: when pcrec needs compound work, the kit provides it. Rev 3 gives
compound work three spellings, all inside one request, and one way to
add a fourth.

| pcrec's need | spelled as | what the kit may do with it (its choice) | today's site |
|---|---|---|---|
| **a scan fused with a verify** ("find `c`/`C` at 4 where `SELECT` folds at 0") | ONE `MF_OP_FIND` whose predicate is a conjunction: a SET term and a RUN term at their offsets | scan the rarest term, filter on a second, verify the run from the mask bits, unroll: twins.md T-B's `ffl`, ~7x on the K82 gate | the ofsskip block (`ofs_test_emit_fn`: scan arm + `ofsk_emit_verify` chain + run term), the `<p>_reqrun[_whole]` blocks |
| **a check followed by a check** (presence, in any order) | `MF_OP_ALL_PRESENT` over predicates, in pcrec's ORDER as a hint | run them in order, reorder by density, or one fused pass with a per-predicate "seen" mask (F-ALL-PRESENT, §4.2 P-F) | the REQ_BYTE pre-check then `set-leads`; `emit_req_set_rest`'s k `memchr` passes (N4) |
| **a scan whose candidate pcrec must judge** (a verify the predicate cannot say) | `MF_H_ON_CAND` with pcrec's text | iterate the hit mask in place; never restart a call per hit | none today. It is the shape twins.md T-A's "iterate in place" lever names |
| **a scan handed to the engine** | RETURN, then pcrec's text (rule 8) | — | the K82 handoff |
| **a new composition** (an ORDERED pair: find P1, then P2 at or after P1's result + d; a COUNT; a mismatch over two streams, F8) | a REQUEST through §11.3's ledger, then an `MF_VOCAB` bump | the kit designs, builds and tests it in its own lane; pcrec's site joins the delegation table in the same change as its first use | none: filed when a customer has a measured cell (D77) |

So "this check followed by this check" is never pcrec emitting two kit
calls and gluing them. One site, one request, and the kit owns the
sequencing. It may emit two calls, if that is what wins.

### 8.5 What pcrec still decides, and the two tables it decides with

**Delegability is by SEMANTIC OPERATION, never by cost.** A site is
delegated when its operation is one of the kit's vocabulary and its
migration step has landed (§9). It is never delegated because something
measured faster. Some sites are NEVER delegated, each for a semantic
reason:

| site | delegated? | why |
|---|---|---|
| T1 PF (`memchr`, `byte-class`, `offset-set`, `run-pinned` and their `-bounded` twins) | yes | FIND over a predicate (one byte, a set, or the k-set conjunction) |
| T2 PRE (the REQ_BYTE / REQ_RUN pre-check blocks, `set-leads`) | yes | FIND / ALL_PRESENT |
| OFS (the ofsskip block, N5; shared by T1's offset/run rows and T2's run blocks) | yes | FIND over a conjunction |
| SETREST (N4) | yes | ALL_PRESENT |
| VERIFY and VMRUN (T6 `pcrec_runcmp_rows`: `words`, `overlap`, `bytes`, `memcmp`) | yes, as TWO site bits: VERIFY at budget 1 (the run term of a prefilter or pre-check, `emit_dfa.c:6039`) and VMRUN at budget 2 (inside the VM's match, `emit_vm.c:4483`, `:8628`) | VERIFY of one RUN term at a known position. One emitter, two budgets: runcmp's callers already split that way, which is why rev 2 put T6 under both of its loop and scan bits |
| STAY (N1), EDGE's loop (T3), VMSPAN (N2 at stride 1) | yes, at D91 budget 2 | SKIP with ADVANCE. Only the LOOP; the scan edge's peeled guard, its accept stores and state writes stay pcrec's (§9.3) |
| MLINE (N3, `(?m)^`'s `memchr('\n')`) | yes, last | FIND of one byte. No customer, so it migrates only for uniformity, and only if Q30 says so |
| N6 (`vm_rev_emit`'s backward walk) | not now | a per-byte L1 test with captures in flight; compare_stack.md §5 keeps its form. Filed |
| N7 (`$_span_match[_caseless]`) | no | the encoding seam's residual entry; the encoding owns it (D23). F8 `mismatch` is a later vocabulary item if S6's cell exists |
| VM span at stride > 1 | no | not a byte-set search (§2.4 d) |
| T4 one-position membership | never | one position, not a search; it is the `member` hook's source (§8.3 rule 6) |
| T8 DFA tables, T9 VM context tests, any DFA or VM step | never | the engine, not a memory function |

This is a static table in pcrec (`DELEG_SITES`, sites as bits on D139's
shape), one row per site with its op, handoff, D91 budget and deny bit.
Its op column is checked against `mf_vocab_has` at build (§8.2), and its
budget column against D91's site classification (C10).

**The profile, per site: pcrec's ONE first-match selection** (the house
idiom, memory `pcrec-decisions-as-first-match-tables`):

| # | profile | applies when | policy bits sent | what the kit does |
|---|---|---|---|---|
| 1 | `baseline` | the site's budget deny bit is set: `-fno-memfn-scan` (budget 1: PF, PRE, OFS, SETREST, VERIFY, MLINE) or `-fno-memfn-loop` (budget 2: STAY, EDGE, VMSPAN, VMRUN) | `MF_P_BASELINE` | emits the site's FROZEN pre-migration text: pcrec's own last spelling of this search, byte for byte (§9.2). The guard's "off" arm |
| 2 | `portable` | `-fno-memfn-native` is set. **DEFAULT ON during the SIMD hold** (D91, D119, D122 addendum 3; §12.2 R4f, Q28). **`[rev4]`** Now: axis `memfn-native` is NOT forced (default OFF; enabled by `-fmemfn-native`, D112's shape; §20.2) | `MF_P_PORTABLE_ONLY` | its best text with no architecture-specific code: scalar, SWAR, libc, short-span loop-free forms |
| 3 | `native` | always (**`[rev4]`**: `-fmemfn-native` given, or after R4f's flip) | — | its best text, ISA arms included (a gcc-time `#if` ladder under the fixed default token, or one spelling under a declared token, HELD) |

`MF_P_INLOOP` is set from the site row's budget (D91 budget 2), never
from a per-call decision. `MF_P_SIZE_LEANING` is set at `--tune` -2/-1,
so D139 item 1's "only if smaller" becomes the kit's rule under that bit
(adding it to the dial is a D103 ruled diff at the first mover, Q32).

The profile names a POLICY CLASS, not an architecture: `portable` means
"no text that names an ISA", which is D122 addendum 3's line ("SWAR is
fine"). pcrec cannot tell what the `native` profile emits on any machine,
and does not need to.

### 8.6 What the kit decides, and how (its internal concern, with its own tests)

The kit's choices are first-match tables of its own (§4.3's C1
classifier and C2 shape tables, requirements.md §2.3's binding-form
table, isa_selection.md §2's ISA table, a plan table over a
predicate's terms), each row with a name and a deny that `--memfn-deny=`
reaches. Where its rows are ordered by MEASUREMENT, the measurement is
the kit's data, generated from transcripts by a `generate.py` beside it
(`third_party/`'s rule, applied inside the kit), with its own `--check`.

The r2 panel's measurement findings are now the kit's charter
obligations, carried into the kit's own design note at R4a:

- **K-1, regime and model.** Every measured comparison names its regime
  (chained vs isolated, hit vs miss, density), and a decision must hold
  in every regime its site can be in (P1, P4). Where a choice rests on a
  model (corner dominance, interpolation), the kit's note names it as one
  and tests it with a fixture that would fail if it were wrong (P3).
- **K-2, protocol constants.** The statistic, the length ladder, segment
  caps and extrapolation are constants in a kit decision record. A
  generator FAILS on capacity overflow and never truncates. A verifier
  samples at alignments and hit offsets the calibration held fixed (P2,
  P7, C-c, C-e).
- **K-3, provenance per arm.** Each measured arm names its box, libc,
  compiler class and flags. The kit's data may be keyed by compiler
  class, and its text may ladder on compiler macros (K2, P6/B4).
- **K-4, verdict-grade boxes.** A native arm whose architecture has no
  verdict-grade timing box (D144 addendum 1: Linux, `taskset`, quiet) is
  not SELECTED over the portable arm on that architecture until one
  exists or Frank admits the Mac (Q31). This is the kit's own rule, so
  pcrec still learns no arch fact.
- **K-5, the kit's own timed control.** The kit's selection among its
  arms is checked by its own timed suite against the scalar byte loop
  and the baseline arm, at its cadence. It is not pcrec's guard, which
  is §10.1 and shares no source with it.

None of this reaches pcrec. pcrec's view of all of it is: the code came
back, and its identity gates and bench say what changed.

---

## 9. THE MIGRATION: pcrec's scalar forms become the kit's scalar arms `[rev3]`

### 9.1 The unit, the two commits, and why the kit is live from the first

**The unit of migration is a pcrec EMITTER FUNCTION with every one of its
callers.** No emitter is ever half-delegated, because a form spelled by
the kit at one call site and by pcrec at another is two owners of one
search (D122; memory `pcrec-general-mechanisms-not-special-cases`).
`pcrec_emit_run_compare` has callers in both engines
(`emit_dfa.c:6039`, `emit_vm.c:4483`, `emit_vm.c:8628`), so it moves
with all three.

**Each step is two commits, implement then replace:**

1. **IMPLEMENT.** The kit gains the step's BASELINE arms: a transcription
   of pcrec's text for those emitters, byte for byte, including pcrec's
   local names (each declared in the baseline manifest, §9.2). In this
   commit every PROFILE of those ops answers with the baseline arm,
   because the kit adds no other arm in a migration step. pcrec's
   emitters build the `mf_site` and hooks and call `mf_emit_site`, AND
   still run their own text into a shadow buffer. A SHADOW COMPARATOR
   (an internal check, compiled into this commit only) fails the compile
   loudly if the two differ, on every compile the suite makes.
2. **REPLACE.** pcrec's own text for those emitters and the shadow
   comparator are deleted. pcrec now has no spelling of those searches.

**Zero movers, by construction and by gate.** Because no non-baseline
arm exists yet, the default build emits exactly what it did. That is
what makes the delegation path LIVE at zero movers: unlike revision 2's
R4c stub, whose `kit_applies` logic could never run while every token
answered UNPRICED (r2 C-e), here every delegated site's code really comes
from `mf_emit_site` from the first replace commit on.

### 9.2 The baseline profile: pcrec's last spelling, frozen

The baseline arms are the kit's record of pcrec's pre-migration text,
one per migrated (emitter, op, handoff) shape. `memfn/baseline/
MANIFEST.tsv` lists, per arm: the pcrec function it was transcribed
from, the commit, the local names it declares (`scan_position`,
`scan_run_length`, `rq_i`, `q` …) and the digest of its rendered text
over a fixed request fixture.

- **It is FROZEN.** A baseline arm changes only by a ruled pcrec abi
  event (Q27). It is the guard's "off" arm (§10.1) and D146's
  revisit-when witness ("measured worse than pcrec's pre-migration
  form"), and both need the pre-migration form to stay reachable and
  unchanged.
- **Its independence is by PIN, not by source.** The baseline text
  lives in the kit, but pcrec's identity gates pin it to the bytes pcrec
  emitted at the step's parent commit (§9.3 I2/I3). A kit edit that moves
  a baseline byte turns them red. So the "off" arm is not computed by the
  thing it controls: it is pcrec's own old output, held in place by
  pcrec's own pins.

### 9.3 The identity gates every step passes

| # | gate | what it proves | shares a source with the kit? |
|---|---|---|---|
| I1 | the SHADOW COMPARATOR (§9.1 commit 1), on every compile of `make test` | kit text == pcrec text for every site the suite reaches, every option, both encodings | no: pcrec's original emitter is the other side |
| I2 | **movers by ID**: every corpus and bench pattern emitted at the step's parent and at the step, diffed byte for byte, at the default, at each `-fno-memfn-*` deny, at every `--tune` position and under `-e utf8`. ZERO movers, by ID (the census discipline every recent abi landing used) | the replace commit moved nothing, including on sites the suite's runs never execute | no |
| I3 | the standing identity gates (the four `.c`-artifact gates, recursion's two-comparison gate, the IR-listing baseline) pass with NO re-pin | the same, through the gates mech already sabotages | no |
| I4 | `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c:52`, 60 at 90d396fd) is unchanged in both commits | a migration is not an abi event; a commit that needs one is not a migration | n/a |
| I5 | the EMITTED-FORM RATCHET (C12, §10.5): pcrec's emitters spell no form the delegation table says is delegated. Born counting the emitted-text `memchr(` calls in `emit_dfa.c`: **9** at 90d396fd (lines 1221, 1247, 5679, 5703, 6153, 6157, 6216, 6218, 8762; comment text excluded), 0 in `emit_vm.c` | a replaced emitter cannot quietly come back as a second spelling | no |

### 9.4 The order: customer first (D77), and what each step moves

> **`[rev4]`** M1 is NARROWED to the closure of its triggering site
> class and SEQUENCED after `lane/k82hbuild` merges and K85's re-measure
> (§16, r3 G-F10/G-F11). M5 moves the MODEL, not a hint (§14.9).

A step is taken when a CUSTOMER needs its sites in the kit (the
customer's trigger is in §12.2), never as a stand-alone refactor. That is
revision 1's Q17 rule, kept.

| step | pcrec emitters that move (all callers) | sites | ops / handoffs | §2.4 fix it carries | customer (trigger, §12.2) | `memchr(` ratchet after |
|---|---|---|---|---|---|---|
| **M1** | `ofs_test_emit_fn`, `ofs_test_emit_pair`, `ofsk_emit_verify` (the ofsskip blocks, T1's offset/run rows AND T2's `<p>_reqrun[_whole]`); `pcrec_emit_run_compare` and `pcrec_emit_runcmp_helpers` (runcmp.c entire: `words`, `overlap`, `bytes`, `memcmp`, all three callers); `pcrec_emit_req_byte_check` with `emit_req_set_rest` (REQ_BYTE, `set-leads`, N4) | OFS, PRE, SETREST, VERIFY, VMRUN | FIND over a conjunction (SET + RUN terms), RETURN; ALL_PRESENT, BOOL; VERIFY, BOOL | (a) the ofsskip `if` becomes the kit's plan (its load-bearing ORDER, r2 R2-S2, is the baseline arm's), (f) N4 | R4d: K82's fused scan+verify | 9 → 3 |
| **M2** | `pf_emit_memchr`, `pf_emit_bcls` and their `-bounded` twins | PF | FIND (one byte; a SET with `table_ref` = `can_begin_match`), RETURN | (e) `dfa_cand_scan` (`emit_dfa.c:6454`) and `pcrec_dfa_cand_ppm` (`:6487`) stop classifying by `strcmp` on row names and read a `DfaPf` field. Owed by ANY new T1-adjacent change, so it rides M2 even if M2 were not a kit step | R4g: PF byte-class | 3 → 1 |
| **M3** | `dir_fwd_skip`, `dir_rev_skip`; `emit_scan_edge`'s LOOP (the `while (more && TEST) advance;` and the counted `scan_run_length` loop; the peeled guard, the accept stores and the state writes stay pcrec's); `vm_emit_span_scan` at stride 1 | STAY, EDGE, VMSPAN (D91 budget 2) | SKIP, ADVANCE, with `member` = T4's spelling and `table_ref` = `stay<K>` / `scan<N>` | (b) and (c); (d) at stride 1 | R4h: in-loop | 1 |
| **M4** | `emit_attempt`'s `(?m)^` skip (N3) | MLINE | FIND one byte, RETURN | — | none. Q30 recommends NOT migrating it until one exists: a lone `memchr('\n')` in pcrec is not architecture knowledge | 1 → 0 if taken |
| **M5** | prefix_k's scan-PLAN selection (below) | OFS, PF | the plan moves; the predicate does not | — | the first mover whose best kit plan differs from `plan_hint` (measured) | — |

**The scan edge ("scan-edge?").** Only its LOOP is a memory function.
The peeled first iteration (the measured t-digits fix, `emit_dfa.c`'s
comment at `emit_scan_edge`), the accept-recording stores and the
fall-through state write are the DFA's own transition semantics. They
stay pcrec's text around the kit's ADVANCE site. A counted span (`{0,n}`)
is passed as a proven `span_hi`, not as a hook.

**prefix_k's measured constants (r2 B2), staged as M5.** `src/opt/
prefix_k.c` does two things:

- it DERIVES the necessary `(offset, byte-set)` facts and the pinned run.
  That is pcrec's semantic knowledge, and it stays (PATFACTS' territory);
- it SELECTS among them, with a cost model over `C_MEMCHR` 6, `C_BITMAP`
  116, `C_VERIFY` 250, `C_ENTER` 2000 (`:65-68`), `C_MISPRED` 1500 and
  the 2x materiality bar: which offset to scan, which to verify, and
  whether the skip is adopted over the offset-0 filter at all. Three of
  those constants are box-measured machine terms (`C_MEMCHR` is glibc's
  AVX2 `memchr`, the C4 allowlist's one code hit at `:45`). That is a
  SCAN PLAN, which D146 puts in the kit.

M1 and M2 move the TEXT only. The plan pcrec's model chose travels as
`mf_pred.plan_hint` plus the conjunction it chose, and the baseline arm
honours it byte for byte. M5, its own step with its own trigger, moves
the PLAN: pcrec passes the FULL necessary conjunction (offset 0
included) with per-term density hints and `consumer = MF_C_ENGINE`, and
the kit's plan table chooses. The five constants and the materiality bar
move into that table as the kit's measured data. `C_ENTER` (what a false
candidate costs the engine) becomes the kit's per-`consumer` term,
measured by the kit's timed suite over pcrec-emitted harness artifacts,
which the tight coupling permits. T1's rows still choose WHAT (which
facts form the predicate), so `RX_DFA_PREFILTER`'s closed value set
(which the bench adapter enumerates) does not split. M5 moves selections,
so it is an abi event with a movers census. At M5 the allowlist's last
code hit leaves `src/` (Q29).

### 9.5 The end state

After M1-M3 (and M5), pcrec's emitters build predicates and hooks, and
`src/gen/runcmp.c` is gone. pcrec spells no libc call, no table walk, no
leapfrog and no masked word compare for a delegated site. The
`memchr(` ratchet reads 1 (N3) or 0. The baseline profile holds
everything pcrec used to spell, frozen. The `-fno-memfn-*` bits reach it
from every site.

---

## 10. GUARDS `[rev3]`

Seven guards. G1 is D146's own, independent of the kit. G2 is the
kit's. G3-G7 are pcrec's deterministic checks, and only they carry
sabotage rows (r2 C-d).

### 10.1 G1, D146's guard: pcrec's timing with the kit on vs off

> **`[rev4]`** The population below came from the kit's own `moved`.
> It is replaced by a pcrec-side default-vs-`memfn-off` artifact diff,
> with a declared regime, pooled bins, and a cadence of every memfn abi
> event (§17.2, r3 G-F5/G-F6). armv8 has NO verdict-grade guard (§17.2,
> G-F4).

- **The two arms.** ON is the default profile (`portable` during the
  SIMD hold, `native` after R4f). OFF is `-fno-memfn-scan
  -fno-memfn-loop`, the BASELINE profile: pcrec's own pre-migration
  text, pinned byte for byte (§9.2). Neither arm is computed from the
  kit's data, and the timing is pcrec's own instrument. This is the
  control that shares no source with the kit (D146 "Guard").
- **Alpha, per mover step (D144 item 1).** Every step that adds
  movers (R4d, R4f, R4g, R4h, R4j) times its witness cells ON vs OFF on
  ubuntubudu: `taskset`-pinned, calibrated loops of at least ~50 ms,
  absolute deltas against a base-vs-base floor measured the same way
  (D144 addendum 1). The floor is ON vs ON and OFF vs OFF. A delta inside
  it is NULL.
- **Long subjects and a population (r2 P9, C-a, C-b).** The population
  is EVERY corpus and bench site where `mf_result.moved == 1`, written as
  a manifest by a compile pass and never filtered by an outcome. Its
  subjects are the bench's throughput subjects (at least 1 MiB,
  read-only from pcrec-bench, sha-verified), cut at 16 B, 64 B, 256 B,
  1 KiB, 64 KiB and 1 MiB so the short/long crossover linux_results.md
  found (fusion wins at 64 B and below and loses from about 512 B at
  SSE2 width) is crossed on both sides. Each bin (step, op, length
  decade) that holds a mover needs at least 8 sites, or it prints
  UNREACHED (K35: counted and printed). A mover in an UNREACHED bin is
  reported unverified.
- **Its home.** Alpha: `tests/memfn/guard/run_guard.sh` (opt-in, heavy,
  never in `make test`, run through pcrecdev2's executor channel per
  memory `pcrec-cross-platform-verification`). Batch gate: a pcrec-bench
  TESTEE `pcrec[memfn-off]` beside the default, requested through the
  inbox (D78) at R4d. That request is also option_sets.md §6.1 trigger 3
  (§12.1).
- **The aarch64 arm.** The Mac runs the same script, directional only
  (D144 addendum 1). Since the kit does not select a native arm on an
  architecture without a verdict-grade box (§8.6 K-4), aarch64's ON arm
  under `native` is the portable text until Q31 is ruled. The Mac run is
  then a check that it did not regress, not a verdict that native wins.
- **The verdict.** A mover whose ON arm is slower than OFF past the
  floor is a D146 revisit-when event. It is filed to the kit's request
  ledger (§11.3) as a defect against the kit's choice. While it is open
  the kit's own deny for that arm (`--memfn-deny=`), or pcrec's budget
  bit, is the interim kill switch (D144 item 4).

### 10.2 G2, the kit's own tests (the kit's business; pcrec only requires that they exist and gate the kit)

- **Exhaustive answers per arm** against the SCALAR BYTE LOOP (never
  against another output of the kit's own generator, §4.5): every
  length 0..256 plus the ladder to 1 MiB, every alignment mod 64, the hit
  at every offset in a block and at none, guard pages on both sides, ASan
  and UBSan. Both architectures: natively, Rosetta 2 for x86 correctness
  on the Mac, and ubuntubudu.
- **The baseline arms** against their manifest digests (§9.2), plus a
  `moved` property test: `moved == 0` iff the rendered text equals the
  baseline arm's for the same request (C11 relies on it).
- **The hook contract** (§8.3): synthetic hooks that read exactly
  `on_cand_reach` bytes at a guard page; impure-expression detection by
  rendering each hook expression as a counter-increment macro and
  asserting nothing depends on its evaluation count.
- **The agreement check** (§3.4, kept): the kit's own set-shape analysis
  against `pcrec_cls_cube`'s over every class the corpus produces, by the
  256-point exact membership check, and against T4's `member` spelling
  per set.
- **Cross-target syntax of every arm it can emit** (r2 B5, kit side):
  each arm compiled `-fsyntax-only` per target it names (gcc and clang
  natively, clang `--target=` for the other architecture with its own
  headers).
- **The kit's timed suite** (§8.6 K-5) and its data's `--check` (K-2), at
  the kit's cadence.

`make test` runs the kit's QUICK tier (correctness, a bounded length
range); the exhaustive tier is `make -C memfn test-full`, part of the
batch gate.

### 10.3 G3, the abi ritual for kit versions (r2 K1/D1, carried)

- **Any kit change that moves ANY byte pcrec emits is a pcrec `abi`
  event in the SAME commit**: `PCREC_ARTIFACT_ABI` bumped, every reader
  found by D94's grep, the identity gates re-pinned, a `docs/spec/`
  hunk (D80), and the movers-by-ID census (§9.3 I2's tool) attached.
  In-tree (§11.1) this is one commit by construction. After an
  extraction it is the vendor-bump commit.
- **Detected without trusting the kit**: the standing identity gates
  compare pcrec's output against pinned bytes, so a kit edit that moves
  pcrec bytes with no bump turns them red. The kit's version string is
  not what is checked; the bytes are.
- **`[rev4]` WITHDRAWN, the next bullet.** It contradicts Frank's Q3
  ruling on `litscan_k82h.md` and D81 (r3 G-F1). The stamp now goes on
  EVERY artifact, `none` where no site is delegated, and carries no kit
  version. It is born in its own abi event (§18).
- **The stamp, on movers only** (k82hrev Q3's precedent): an artifact
  with at least one site whose `mf_result.moved == 1` carries
  `<PREFIX>_MEMFN "<kit version>"` and `<PREFIX>_MEMFN_FORMS
  "<form_id>,…"` in site order. An artifact with none carries neither, so
  the zero-mover migration adds no byte. Re-measuring or re-tuning
  inside the kit that moves a selection moves text, so it is covered by
  the same rule. There is no separate "recalibration" event (rev 2's
  Q20 dissolves).
- **`rx_info` is unchanged** until a consumer asks for the kit version in
  the struct (D77).

### 10.4 G4, the arch-blindness detector, rebuilt (C4; r2 B1)

> **`[rev4]`** The plant's "held out" claim is narrowed to what it can
> support, and matching is case-insensitive (§17.5, r3 G-F7).

pcrec carries no architecture knowledge (Q12's refinement, D146). C4
makes that a red test, with the r2 panel's rebuild:

- **Seven vocabulary classes, one pattern each, with explicit
  boundaries** (`\b` fails between `_` and a letter, so `MF_VEC_SSE2`
  slipped past rev 2's regex): (1) ISA names and levels; (2) predefined
  arch macros (`__SSE*__`, `__AVX*__`, `__aarch64__`, `__ARM_NEON*`,
  `__ARM_FEATURE_*`, `__x86_64__`, `_M_X64` …); (3) intrinsics and
  vector types (`_mm*_`, `__m128*`, `vld1q_*`, `vqtbl*`,
  `__builtin_ia32_*` …); (4) intrinsic headers (`*intrin.h`,
  `arm_neon.h`, `arm_sve.h`, `cpuid.h`); (5) targeting (`target("…")`,
  `-march=`, `__builtin_cpu_supports`, `getauxval`, `HWCAP`,
  `hw.optional`, `cpuid`); (6) arch nouns (`x86_64`, `amd64`,
  `aarch64`, `arm64`, `pshufb`, `movemask`, microarchitecture names);
  (7) kit-identity compares: `strcmp`/`strncmp`/`memcmp`/`==` with an
  operand naming `form_id`, `mf_kit_version(` or the `--isa=` token.
- **Two delegation classes, new in rev 3.** (8) pcrec reading kit
  OUTPUT: any `mf_sink` read-back, or a string search over a buffer the
  kit wrote, under `src/`. (9) the include graph: `src/`, `cli/` and
  `lib/` include only `memfn/include/memfn.h` from the kit, never an
  internal kit header (the precedent is `analyze/`'s link-nothing rule,
  inverted).
- **Positive controls, one per class**, planted in a scratch copy and
  required to hit. The plant vocabulary is HELD OUT from the regex's
  source: derived at check time from the compiler's own installation
  (`cc -dM -E` under each owned target, intrinsic names scraped from its
  headers). That list was never chosen by the regex's author
  (learnings.md §3, R8's lesson).
- **A negative control** for the one known false-positive class: hex
  escapes (`\x86` in `.rxt` subjects), excluded by rule.
- **Scopes**: the code of `src/`, `cli/` and `lib/` (allowlist counted at
  birth, D107's shape); the CLAUDE.md files inside them (allowlisted
  rows); `tests/` (its own allowlist, so a NEW test that branches on an
  architecture is visible). `memfn/` is EXEMPT: it is where architecture
  knowledge is supposed to live.
- **Born counts.** An unmerged and superseded lane (`memfnk0r3`)
  measured these classes at b7542fbe: code 1 hit (`src/opt/prefix_k.c:45`,
  "AVX2" in a measurement comment), `src/` docs 1 (`src/gen/CLAUDE.md`,
  "an x86 slot", in the sentence stating the ISA-neutral rule), `tests/`
  15 hits in 10 files (box descriptions, the `R_X86_64_*` relocation
  names `tests/codegen/run_scan_edge_dispatch.sh` parses, a Linux library
  path). C4's build lane re-takes the census and commits it as the
  allowlist; M5 removes the code hit.

### 10.5 G5-G7, pcrec's other deterministic checks

> **`[rev4]`** C5 pins per-ARM digests under `tests/memfn/pins/`
> instead of whole artifacts at the parent (§17.4, r3 F12/G-F8). C9 gains
> a header shim, a native-enabled configuration and a K35 floor (§17.3,
> G-F3). C11 checks the stamp's VALUE on every artifact (§18). C13 (on_cand
> duplicability) and C14 (shape bounds) are new (§14.6, §14.7).

| # | check | what it proves | shares a source with the kit? |
|---|---|---|---|
| C5 | **profile identity**: the corpus at `-fno-memfn-scan -fno-memfn-loop` is byte-identical to the BASELINE pin (the step parent's output); at `-fno-memfn-native` it carries no text the C4 classes 1-4 match (a scan of the EMITTED artifacts, the one place pcrec may grep generated code for vocabulary, because it is checking the kit's promise, not branching on it) | the off arm is what G1 says it is; `portable` is portable | no |
| C6 | answer identity per deny, per box: `make test-axes` arms for the three bits, plus option_sets.md §3.5a's compile-only arms per declared token when R4i builds tokens | correctness under every profile | no |
| C9 | **cross-target syntax, pcrec side** (r2 B5): every corpus artifact with at least one mover, each `#if` arm compiled `-fsyntax-only` per the arm's target (Mac: gcc-16 natively, clang `--target=x86_64-linux-gnu`; ubuntubudu: gcc and clang natively, clang `--target=aarch64-linux-gnu`). The number of arms compiled per artifact is printed and must equal the count the kit reports in `mf_result` (K35). A Rosetta 2 run executes the x86 arm under C6 | the arms no box compiles natively at least parse and type-check, inside real artifacts | no |
| C10 | **site table and stack**: `DELEG_SITES`' budget column matches D91's classification (budget 1: PF, PRE, OFS, SETREST, VERIFY, MLINE; budget 2: STAY, EDGE, VMSPAN, VMRUN); `MF_P_INLOOP` is set only from that column; its op column passes `mf_vocab_has`; no `mf_site`, `mf_pred` or `mf_result` is an automatic variable under `src/` (r2 K3) | an in-loop site cannot ask for an out-of-loop arm; no large request on an emitter stack | n/a (structural) |
| C11 | **stamp census**: the artifacts carrying `<PREFIX>_MEMFN_FORMS` are exactly the movers by ID (§9.3 I2's tool), and every form id is one the kit's `moved` reported | the stamp is on movers and only on movers | partly: `moved` is the kit's, so G2's `moved` property test is the other half |
| C12 | **the emitted-form ratchet** (§9.3 I5): emitted-text `memchr(` calls, table-walk loop texts and runcmp row texts in pcrec's emitters, counted against a committed ceiling that only descends | no replaced form comes back as a second spelling | no |

### 10.6 The spec states the limits (D80)

At R4d's mover, `docs/spec/` gains the kit's contract as a caller sees
it: the `-fno-memfn-*` bits and `--memfn-deny=`, the stamps, the
profile semantics (the baseline is pcrec's pre-migration text), and
three limits. (1) The kit's choices are measured under gcc, pcrec's
target compiler; another compiler gets correct code whose speed was not
the one measured (r2 K2). (2) Where the kit calls libc, its choice was
measured against glibc and libSystem; musl inherits it (rev 2's Q22, now
Q33). (3) Injected intrinsics headers are compiler-provided (r2 L1).

### 10.7 Sabotage rows (deterministic detectors only; ids at build, highest S on main + 1)

> **`[rev4]`** Replaced by §17.6. Every row is mech-runnable from a
> `git archive` (no history), its detector reads pins under `tests/`, and
> each carries `SAB_REACH` (r3 G-F8).

| sabotage | detector |
|---|---|
| one baseline arm edited by one byte | I3 / C5 (the baseline pin) |
| a kit text change that moves a pcrec byte, with no abi bump | the standing identity gates (G3) |
| an ISA word added to `src/gen/emit_dfa.c`, one row per C4 class, drawn from the held-out list | C4 |
| `#include "memfn/src/…"` (an internal kit header) in `src/` | C4 class 9 |
| a `strcmp` on `form_id` in `src/` | C4 class 7 |
| a site's INLOOP bit dropped from `DELEG_SITES` | C10 |
| `moved` forced to 0 on a mover | C11 (the stamp census disagrees with the byte census) |
| a replaced `memchr(` text re-added to an emitter | C12 |
| the kit's guard established one byte short (`cand + reach < n` off by one) | G2's guard-page hook test (the kit's own mech row) |
| a `-fno-memfn-native` arm emitting one intrinsic | C5 |

---

## 11. COUPLING LIKE THE BENCH: home, licence, requests, name `[rev3]`

### 11.1 Where the code lives first: in-tree `memfn/` (recommended, Q25)

> **`[rev4]`** `analyze/` is the INVERSE precedent (a leaf binary that
> links nothing). The kit links INTO libpcrec, so its symbols ship in
> `libpcrec.a`. §20.3 adds the symbol policy and per-file provenance
> (r3 G-F14).

- **A top-level, zero-dependency subtree, on `analyze/`'s precedent**:
  `memfn/` with its own Makefile, tests, CLAUDE.md, LICENSE and README.
  It links nothing from `src/`, `cli/` or `lib/`. pcrec's compiler links
  the kit (it is an emit-time library), and pcrec's sources reach it only
  through `memfn/include/memfn.h` (C4 class 9). Generated artifacts never
  depend on it: what reaches them is TEXT, so self-containment holds.
- **Why in-tree first.** Three reasons, the third decisive:
  1. The API is unsettled until M1 has run; two repositories double the
     cost of every change to it (revision 1's §3.3 item 4, kept).
  2. The scope mandate needs no extension: `memfn/` is inside the pcrec
     repository.
  3. **Atomicity.** A kit change that moves pcrec bytes MUST land with
     its abi bump and re-pins (§10.3). In one repository that is one
     commit and the identity gates see both halves at once. Across two
     it is a vendor bump that can be split, delayed or reverted out of
     step.
- **Extraction** to its own repository `pcrec-memory-functions` happens
  when a second consumer appears (a K3 CLI user, another project) or
  Frank rules it. It needs a SCOPE-MANDATE EXTENSION: the root
  CLAUDE.md's MANDATE names exactly two repositories, and pcrec-bench
  joined it by Frank's ruling (2026-08-17). After extraction pcrec reads
  a pinned vendored copy, `third_party/pcrec-memory-functions-<ver>/`,
  with a PROVENANCE.md naming what derives from it (every delegated site
  of every artifact), and `third_party/README.md`'s "nothing here
  reaches a generated artifact" sentence gains the kit's row beside
  `utf8_fold_pairs.inc` (r2 K5).

### 11.2 Licence (Q26)

The kit's text is injected into users' artifacts, so D145's
consequence binds it: 0BSD, CC0 or Unlicense, or a licence with its own
output exception. **Recommended: 0BSD for the whole kit**, the simplest
licence on D145's list. The planned translation of Rust `memchr`
(Unlicense OR MIT, survey.md) is clean under it. Compiler-provided
intrinsics headers are #included by injected text, never copied into it,
and the spec says so (§10.6).

### 11.3 How pcrec asks for new kit work (Q34)

> **`[rev4]`** One shared file breaks D78's single-writer rule (r3
> G-F13). Two files from day one, with the manager the sole writer of
> requests (§20.1).

**Now (in-tree): a request LEDGER, `memfn/docs/requests.md`.** Numbered
items, never deleted, on D78's shape:

- pcrec's side (the manager, or a pcrec lane through the manager) files
  `R-n`: the customer row, the measured cell that is the D77 trigger, and
  the SEMANTIC operation wanted (a new op, handoff or term kind, or a
  compound shape from §8.4's last row). It never names an ISA or a
  kernel.
- the kit's side (a kit lane) appends `ack:` with its plan, then
  `done:` with the `MF_VOCAB` value that carries it and the kit commit.
- a G1 revisit-when event (§10.1) is filed the same way, as `D-n`
  (defect against a kit choice), with its timing transcript.

It is a FILE rather than messages because kit lanes run asynchronously
and a request must survive a session boundary (memory
`pcrec-lane-hold-lift-artifact`). It is ONE file while both sides share
one repository and one manager. **At extraction** it splits into D78's
pair in the kit's repository (`inbox_from_pcrec.md`, written only by
pcrec's manager; `outbox_to_pcrec.md`, written only by the kit's), single
writer each way, live coordination interprocess. That is exactly the
pcrec-bench arrangement, and the reason for waiting is that until there
are two sessions there is nobody to be the second writer.

**Lanes.** Kit work is ordinary lane work (D86's feature type), briefed
with the scope mandate. A kit lane whose change moves pcrec bytes
carries the pcrec abi ritual in its own delivery (§10.3). The kit's
priorities are pcrec's requests first (it exists to serve them, as the
bench does), its stand-alone K3 product second.

### 11.4 The name

- Project, README, repository-to-be and `mf_kit_version()`'s string:
  **pcrec-memory-functions**.
- Directory `memfn/` (short, and already the design record's name,
  `docs/design/memfn/`). C prefix `mf_` / `MF_`. pcrec's option family
  `memfn`: `-fno-memfn-scan`, `-fno-memfn-loop`, `-fno-memfn-native`,
  `--memfn-deny=`. Revisions 1-2's `kit` flag spellings are withdrawn,
  because "kit" also names D122's compare-stack kit and clskit.
- In prose, "the kit" stays.

---

## 12. option_sets.md, the build order, and the plan-row text `[rev3]`

### 12.1 What rev 3 changes in option_sets.md

| option_sets.md item | revision 3 |
|---|---|
| §1.2 vector-row denies (`-fno-vec-scan`, `-fno-vec-skip`, `-fno-vec-run`, `-fno-swar-scan`); rev 2's `-fno-kit-scan/-loop/-native` | **three bits**: `-fno-memfn-scan` (budget-1 sites to the baseline profile), `-fno-memfn-loop` (budget-2 sites to baseline), `-fno-memfn-native` (the portable profile; DEFAULT ON during the SIMD hold). Named for D91's budgets and a policy class, never an ISA. Bit numbers are taken at landing (the next free; 47-49 if k82hand's bit 46 has landed) |
| §1.2 `--memfn-deny=` | kept, passed through UNPARSED: pcrec cannot spell a kit row |
| §1.2/§4.3 the `isa` family (poset), `isa-route`, `-fisa-check`, `-fisa-dispatch`, `--isa-marker` | as rev 2's cross-note: ONE opaque value axis (`--isa=`, passed through), the route folded into the token, constraint rows 6-8 removed. All of it HELD with R4i |
| §4.2 the `vector` family (`auto` / `simd` / `no-simd` / `scalar`) | **family `memfn`**: `auto` (∅: the defaults), `simd` (`memfn-native := allow`: a caller's opt-in to native arms before the R4f flip; a conflict with a set that denies it is refused by name, as before), `no-simd` (`-fno-memfn-native`), `memfn-off` (`-fno-memfn-scan -fno-memfn-loop`: the D146 guard's off arm and the bench's off testee). `scalar` dissolves: "one byte at a time" is not a profile any more; the nearest thing is `memfn-off`, pcrec's old forms, which already include libc `memchr` |
| §4.2's `vector` × `isa` interaction table | gone: both are inputs of one kit request, and the kit's code is the whole answer |
| §3.5's sweep | three deny arms per box (C6); compile-only arms per declared token only at R4i |
| §6.1 trigger 1 (one name over two or more bits, plus a consumer) | met by `memfn-off` (two bits) the day pcrec-bench takes the `pcrec[memfn-off]` testee (§10.1). That request is ALSO trigger 3. So the first option-sets build is likely this one |
| §6.1 trigger 2's predicted first disagreement (rev 1's Q16: a size position denying `vec-scan`) | dissolves: a size-leaning `--tune` position sends `MF_P_SIZE_LEANING` to the kit (§8.5) rather than denying anything, so no set disagreement arises (Q32) |

The cross-note at the top of option_sets.md is updated in this lane's
delivery to point here.

### 12.2 The build order, revision 3

> **`[rev4]` SUPERSEDED by §22** (r3 G-F10/G-F11/G-F12): R4a-R4j are
> re-derived with the stamp's own event, M1 narrowed and sequenced, and
> R4f's circularity broken.

It replaces rev 2's R4a-R4h. Each step names its PREREQUISITE (a step
that must have landed) separately from its TRIGGER (a measured cell or a
ruling, never a step's mere completion; r2 R3). Nothing that moves an
emitted byte opens before its trigger (D77), and native text stays under
the SIMD hold until R4f (D91, D119).

> **R1d REVISION 3 DELIVERED 2026-10-05 (lane memfndel): `docs/design/memfn/integration.md` rev 3** — D146's DELEGATION model designed out: pcrec describes a SITE (`mf_site`: an op over a conjunctive predicate of byte-set/masked-run terms at offsets, proven span, anchoring, density hints, a policy word) and the kit writes its code through TEXT hooks (subject, read limit, bounds, result, cursor/step, per-candidate verify, T4's one-position spelling, pcrec's table names). pcrec decides only WHICH SITES are delegated (by op type: `DELEG_SITES`) and WHICH PROFILE each gets (first match: `baseline` under `-fno-memfn-scan`/`-loop` = pcrec's frozen pre-migration text, `portable` under `-fno-memfn-native` = default during the SIMD hold, `native`). Compound work = the predicate algebra + ALL_PRESENT + ON_CAND + a request ledger. Migration M1-M5 by customer, each implement (shadow comparator) then replace, zero movers by ID, a `memchr(` ratchet born at 9. Guards: D146's on/off timing (alpha + a `pcrec[memfn-off]` bench testee), the kit's exhaustive tests, the abi ritual for any kit byte move (stamp on movers), C4 rebuilt (7+2 classes, held-out plant), C9 cross-target syntax, C5-C12. In-tree `memfn/` first, 0BSD, name pcrec-memory-functions. r2 findings: 11 carried, 7 moved inside the kit, 3 dissolved, 2 split. Q24-Q34 open.
> - **R3** (rulings): Q24-Q34. Nothing owed on Linux beyond R4b's probe.
> - **R4a, the kit's skeleton in-tree** (`memfn/`): `memfn.h` with `MF_SITE_ABI`/`MF_VOCAB`, `mf_emit_site` over an EMPTY baseline set, K1 primitives and F1/F2/F3/F5/F6 reference functions with G2's exhaustive tests on both architectures, LICENSE (0BSD), CLAUDE.md, `docs/requests.md`. pcrec links it and calls nothing. No emitted byte moves. **Prerequisite:** none. **Trigger:** Frank's Q24/Q25 ruling.
> - **R4b, the first customer's measurement** (probe only, `probes/twins/`): twins.md T-B re-run on Linux ON THE POST-HANDOFF BUILD, with a PORTABLE (SWAR) fused pair-filter variant beside `emit` and the vector `ffl`, on the K82 cells (union-select, userpass, mod-i; gate, sweep, short). **Prerequisite:** none. **Trigger:** the K82 handoff (`lane/k82hbuild`, litscan_k82h.md) merged and alpha-accepted, because the handoff removes the second scan and T-B's twin must be measured against what remains (r2 R2).
> - **R4c, M1: OFS / PRE / SETREST / VERIFY migrate, zero movers** (§9.4): the ofsskip blocks, runcmp entire, the pre-check and N4, implement then replace, I1-I5 green; the three deny bits land (baseline == default, so C5 is live and vacuous-by-identity); `DELEG_SITES`, C4, C10, C12. **Prerequisite:** R4a. **Trigger:** R4b shows the PORTABLE fused form beating `emit` past the D144 floor on at least one K82 cell. If only the vector form wins, M1 waits for R4f's trigger instead.
> - **R4d, the first movers: the kit's portable fused conjunction arm at OFS/PRE**: abi bump, `<PREFIX>_MEMFN[_FORMS]` on movers, the `docs/spec/` hunk with §10.6's limits, C5/C6/C9/C11 live, sabotage §10.7, G1's alpha on the K82 cells; the bench `pcrec[memfn-off]` testee requested (D78 inbox). `MF_P_SIZE_LEANING` on the dial if Q32 rules it. **Prerequisite:** R4c. **Trigger:** R4b's cell (the same measurement: the step that moves bytes is the one it justified).
> - **R4e, ON_CAND's first customer** (a verify the predicate cannot express, iterated in place): **Trigger:** a measured cell where a candidate's verify is not a byte-set/run conjunction and the restart per hit dominates (twins.md T-A's "iterate in place" lever on a real site). Filed until then.
> - **R4f, the native default flip** (`-fno-memfn-native` default OFF): its OWN ruled event (r2 R1, Q28), never a side effect of a kit release. **Prerequisite:** R4d. **Trigger:** `[OPT-SIMD]` opened (D119: SIMD last) AND a Linux alpha where the native arm beats the portable arm past the floor on a mover cell.
> - **R4g, M2: PF migrates, then PF movers** (`pf_emit_memchr`, `pf_emit_bcls`, the `-bounded` twins; §2.4 e's `strcmp` readers fixed in the M2 commit). **Prerequisite:** R4c. **Trigger:** U-2 (the bench class-shape census, relayed to pcrecdev2) AND a Linux cell whose time is in `pf_emit_bcls` (the WAF `byte-class` cells, compare_stack.md §6.3).
> - **R4h, M3: in-loop sites migrate, then in-loop movers** (STAY, the scan edge's loop, VMSPAN at stride 1; `MF_P_INLOOP`). **Prerequisite:** R4c. **Trigger:** U-3 (an in-loop probe at a real emitted site, D91 budget 2 re-measured, never inherited) AND a Linux cell dominated by class runs.
> - **R4i, declared tokens (`--isa=`):** HELD. **Trigger:** isa_evaluation.md L-1/L-2, answered "no customer now" by linux_results.md §5.
> - **R4j, M5: the scan PLAN moves into the kit** (prefix_k's selection and constants; §9.4): an abi event with a movers census; the C4 code hit leaves. **Prerequisite:** R4c (and R4g for PF). **Trigger:** a mover whose kit plan differs from `plan_hint` and whose G1 alpha beats the hinted plan past the floor (Q29).
> - **Filed, not scheduled:** M4 MLINE (Q30); a fused ALL_PRESENT arm for N4 (a cell on the K65 no-DFA-scan route whose time is in `emit_req_set_rest`); an ordered FIND_SEQ op and F8 `mismatch` (each by request with a cell, §11.3); N6; the stay set through T4 (a `[CLS-TREE]` follow-up, §2.4 b); extraction (§11.1).

---

## 13. Questions for Frank `[rev3]`

> **`[rev4]` SUPERSEDED by §23** (Q35-Q44). Q24-Q34 are re-derived
> there; §23.1 maps each.

Renumbered from Q24 (rev 2 ended at Q23; the unmerged price-model draft
`memfnk0r3`'s Q24-Q30 were never delivered and are void). Each has a
recommendation.

24. **Q24, the contract.** Adopt §8 as the design of record: `mf_site`
    (an op over a conjunctive predicate plus proven facts and a policy
    word), the text-hook contract with its eight rules, compound work as
    the predicate algebra plus ALL_PRESENT and ON_CAND, totality (a kit
    decline is a kit defect), and pcrec's two tables (`DELEG_SITES` by op
    type; the profile first-match). **Recommendation:** yes.
25. **Q25, where the kit lives.** In-tree `memfn/`, zero-dependency,
    extracted to `pcrec-memory-functions` when a second consumer appears
    or you rule it (a scope-mandate extension then). **Recommendation:**
    in-tree; the decisive reason is that a kit change and its pcrec abi
    bump must be one commit (§11.1).
26. **Q26, the licence.** **Recommendation:** 0BSD for the whole kit
    (D145's list), replacing rev 1's split recommendation (0BSD for K1,
    MIT plus exception for K2/K3).
27. **Q27, the deny bits and the baseline.** Three bits
    (`-fno-memfn-scan`, `-fno-memfn-loop`, `-fno-memfn-native`), with the
    budget bits selecting the BASELINE profile: pcrec's own pre-migration
    text, held by the kit and FROZEN, changed only by a ruled abi event.
    **Recommendation:** yes, and keep the baseline forever: it is D146's
    guard's off arm and the revisit-when witness, and it costs only the
    text it already is.
28. **Q28, the default during the SIMD hold.** `-fno-memfn-native` is ON
    by default, so the default profile is `portable` (scalar, SWAR, libc,
    loop-free short paths: D122 addendum 3's line). The flip to `native`
    is R4f, its own ruled event. **Recommendation:** yes.
29. **Q29, prefix_k's measured constants (r2 B2).** The k-set
    DERIVATION stays pcrec's; the scan PLAN (which term to scan, which to
    verify, whether to adopt the skip) and its five constants move into
    the kit at R4j, behind a measured trigger. Until then pcrec's pick
    travels as `plan_hint` and the baseline honours it. **Recommendation:**
    yes. Alternative: rule the plan pcrec's forever, which keeps
    box-measured terms (and the C4 allowlist's code hit) in `src/`.
30. **Q30, migrate without a customer?** M4 (the `(?m)^` `memchr('\n')`,
    N3) has no customer. **Recommendation:** no; leave it until one
    exists. A lone libc call in pcrec is not architecture knowledge, and
    the ratchet (C12) keeps it at one.
31. **Q31, the aarch64 verdict box.** D144 addendum 1 makes Mac timings
    directional, and no house aarch64 box gives verdict-grade numbers.
    **Recommendation:** the kit does not SELECT a native arm over its
    portable arm on an architecture with no verdict-grade box (§8.6 K-4),
    so aarch64 runs portable text under `native` until you either admit
    the Mac per cell (quiet window, D144's loop protocol, the kit's own
    timed suite) or a Linux aarch64 box exists. pcrec still learns no
    arch fact: the rule is the kit's.
32. **Q32, the dial.** `--tune` -2/-1 send `MF_P_SIZE_LEANING`, and the
    kit applies D139 item 1's "only if smaller" under it. That changes
    what two pinned positions mean, so it is a D103 ruled diff.
    **Recommendation:** rule it at R4d, with the movers census showing
    what it moves at those positions.
33. **Q33, the libc the kit measured (rev 2's Q22).** Where the kit
    chooses a libc call, it measured glibc and libSystem; musl inherits
    the choice. **Recommendation:** accept and state it in `docs/spec/`
    at R4d (§10.6). A libc-qualified request is the general form, built
    only for a measured customer.
34. **Q34, the request channel.** A numbered ledger in-tree
    (`memfn/docs/requests.md`) now; D78's single-writer inbox/outbox pair
    at extraction. **Recommendation:** yes.

### 13.1 Every earlier question, mapped

| old | status under rev 3 |
|---|---|
| Q12 (the boundary) | RULED (rev 2, with K0), then superseded by D146. K1-K3 survive as the kit's internal layering |
| Q13 (home) | becomes Q25 |
| Q14 (licence) | becomes Q26 |
| Q15 (deny bits) | becomes Q27 |
| Q16 (ladder bytes) | DISSOLVED: code bytes are the kit's concern, and `MF_P_SIZE_LEANING` hands it the dial's intent (Q32) |
| Q17 (promoting the seven sites) | kept as a RULE, not a question: promotion rides a customer (§9.4); §2.4(e) rides M2 regardless; §2.4(b)'s first half stays filed as a `[CLS-TREE]` follow-up |
| Q18 (the fixed `portable` default token) | carried unchanged; HELD with R4i |
| Q19 (the Mac as a calibration box) | replaced by Q31 (no calibration crosses the boundary; the question is now which box gives the kit verdicts) |
| Q20 (recalibration governance) | DISSOLVED: any kit change that moves a pcrec byte is an abi event (§10.3); there is no separate recalibration event |
| Q21 (the route in the token) | carried unchanged; HELD with R4i |
| Q22 (whose libc) | becomes Q33 |
| Q23 (K0 against the K82 ruling) | DISSOLVED: pcrec does no cost comparison at all |
| requirements.md Q1-Q3, isa_selection.md Q4-Q6, isa_evaluation.md Q7-Q11 | unchanged by rev 3, except that every dispatch or ISA choice they discuss (Q5's hybrids, Q4/Q7's levels) is now made INSIDE the kit; pcrec's only ISA surface is the held, opaque `--isa=` |
