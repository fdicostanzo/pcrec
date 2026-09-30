# [CLS-TREE] — THE DESIGN NOTE: a class matcher as one node, a kit predicate, and a shared byte automaton

Lane `clsdes88` (opus), branch `lane/clsdes88`, on `main` at `73590d19`,
2026-09-28. **Design only**: nothing under `src/`, `tests/`, `docs/spec/`.
The plan row is `docs/dev/plan.md` [CLS-TREE] (UNPARKED 2026-09-28), and this
note answers the eight things the row and the lane brief ask it to DECIDE
(§1-§8). A light D6 panel reviewed it; findings and dispositions are in
`docs/dev/reviews/2026-09-28-r1-cls-tree-design.md`, and the fixes are made
inline, marked **[r1 ID]**. Panel verdict: no BLOCKER; four MUST-FIX/SHOULD
measurement fixes and two SHOULD notes applied; the decode/automaton
ill-formed agreement and the splice's priority safety were verified against
the source by the semantics critic.

**Status: PROPOSED.** Frank rules §8. **S0's calibration LANDED 2026-09-29
(lane clsfit): §1.7** — the per-probe model fits (member r +0.98 all arms,
kit orderings 30/36 held out), the whole-set `page3w` beats every kit
policy, and the λ re-proposal is a first-match table with three programs
(§1.7.5, PROPOSED; its diff is in `docs/dev/lanes/clsfit_report.md`). Every cell this note proposes for the
`--tune` table is a PROPOSAL under D103 (the table is a pinned contract, and
a measurement landing never moves a cell by itself).

**Sources, and what each is.** Every number below names its file. There are
four kinds, and they are not interchangeable:

| tag | what | where | citable for |
|---|---|---|---|
| **[S]** | the study (lane clstudy, 2026-09-11), Mac, gcc-16, exhaustive verification | `docs/dev/cls_tree_study.md`, `studies/cls_tree_study/results/{sweep_*,baseline,crosscheck_*,proptest}.tsv` | sizes, compile time, answer identity |
| **[T]** | the ns/char membership arm, **ubuntubudu**, gcc, load1 0.10, 11 interleaved rounds, checksummed (2026-09-11, I-65 rider) | `studies/cls_tree_study/results/bench_ubuntubudu_20260911.tsv` (2,641 rows); analysed by `timefit.py` → `results/timefit_20260928.txt` | **timing** — the only citable timing in this note |
| **[N]** | new, this lane, Mac, **box-independent** (byte counts, automaton sizes, exhaustive answer checks; no timing) | `studies/cls_tree_study/results/{whole_k53,whole_uprops,automaton_k53}.tsv`, produced by `verify_whole.py`/`automaton.py` | sizes, state counts, answer identity |
| **[P]** | a probe of the shipped compiler, `build/pcrec` at `73590d19` (abi 44), `--features all -e utf8` | quoted inline with the command | what pcrec emits today |

Darwin timing appears nowhere (Frank, 2026-09-11). The Mac-run bench smoke in
§7 checked ANSWERS only and its times were discarded.

---

## 0. The decisions, in one table

| # | question (row item) | DECISION | rests on |
|---|---|---|---|
| **CT-1** | kit members | the study's seven (`ALL RANGES CUBES MASK64 BITMAP PAGE64 BSEARCH`), `CUBES` at tier 1 only, **plus WHOLE-SET sections for the table members** (a section may span the whole set; today `MAXK = 64` forbids it) | [S] §2, §6.1; [T]; [N] §1.3 |
| **CT-2** | the sectioning DP | kept, exact over contiguous partitions, O(n·64) + O(k) whole-set candidates — **but its speed term is REPLACED**: the study's `λ·Σops` sums op counts over all sections, which is a code-size proxy; [T] shows it predicts nothing about ns/char (r = −0.00, pairwise 17/36 on member subjects). The replacement prices a PER-PROBE time, calibrated on ubuntubudu (§7 b) | [T] via `timefit.py`; §1.2 |
| **CT-3** | λ → `--tune` | all five positions are the SAME DP with different pinned λ; whole-set tables are ordinary candidates, so +2's extreme-speed forms arrive by the DP choosing them, not by a +2 special case. The pinned constants 4/16/16/64/256 (opt_dial_design.md §4) were derived from the refuted term and **are re-proposed after calibration, as a ruled diff** | D103; §1.4 |
| **CT-4** | how a class becomes ONE node | a new AST kind (`A_WCLASS`, name the implementer's) produced by `pcrec_lower_enc` for every class whose encoding automaton is deeper than one code unit; it carries the code-point set AND today's lowered byte alternation as a child during implement-then-replace. **Not a flag on `A_CLASS`**: 49 `case A_CLASS` arms + 6 comparisons read "a class is bytes" after lowering, and `vm_cls` would silently intern the first 32 bytes of a code-point set (r54 E1) | [P] grep; `src/core/compile.c:1479-1523`; §2.1 |
| **CT-5** | VM instruction shape | `len = $_decode(s, n, pos, &cp)` then the set's kit predicate `$_clsN(cp)`; a NEW encoding-seam entry `PCREC_ENCE_DECODE`, `engine_callable`, **`static inline`**, whose body IS stage 4's `$_span_ci_decode` (ill-formed ⇒ 0, the automaton's exact ill-formed set), which then retires into it. Byte backend: no row (depth-1 classes never decode) | `src/enc/enc_utf8.c:187-214`; DD-12 (7); §2.2 |
| **CT-6** | byte-DFA seam | **two pieces, staged separately**: (ii-a) the class's MINIMAL byte automaton per direction, spliced as its NFA fragment (fan-out on entry **827 → 30 forward, 827 → 65 reverse** for `\p{L}`) — the class's compile-time share of K67; (ii-b) the DFA-side CONSUMING ISLAND (decode + kit inside the DFA walk) is **not designed here**: it is [ENG-ISL]'s splice and [UCP] §D's mechanism, and this note fixes only its interface (the kit predicate is the island's test). (ii-a) does NOT shrink DFA tables: the minimal automaton is 299 states and so is today's forward DFA | [N] `automaton_k53.tsv`; [P]; §3 |
| **CT-7** | caseless | folded at CONSTRUCTION (stage 4's per-contribution rule, `cls_casefold` via `PcrecEnc.fold`); the kit receives the folded set and never learns it was caseless (Constraint 1). No runtime fold anywhere | [S] §4.3, §7; §4 |
| **CT-8** | retirements | K55's `--engine=vm` refusal (and every captured wide class, e.g. `(\p{L})`, refused today); `vm_cls_shape`/`-fno-cls-fold` (the kit's one-cube `CUBES` is its general form, 8 corpus classes vs 4); [OPT-CLSPACK] (the byte tier needs no tables at all); K67's class share. **STAYS**: [K53-SELRETRY] (the DFA route keeps its ~200 KB tables until the island) | §5 |
| **CT-9** | staging | S0 (measure) → S1 (kit in `src/`, no artifact moves) → S2 (byte tier, VM; abi) → S3 (`A_WCLASS`, byte-identical refactor) → S4 (VM decode+kit; abi; the UCP prerequisite) → S5 (minimal-automaton splice; gated on [OPT-CLOSURE-CTX] + a K67 re-measure). Island: not staged here | §6 |

---

## 1. The kit, the sectioning DP, and the dial

### 1.1 Members: the study's seven, kept

The study's verdict stands and is not re-litigated: **the answer is the kit,
not a pick from it** — no single representation wins any real code-point
set; `\p{L}` at the middle policy is 27 sections of four forms ([S] §4). The
members and their preconditions are [S] §2's table. Two things from the study
carry into the design as decisions rather than observations:

- **`CUBES` ships at tier 1 only** (the O(k) `cube_of` single-cube test). The
  exact Quine-McCluskey tier costs 4.9× discovery time for 0.36% fewer probe
  ops on 10 of 126 sectionings ([S] §6.1). Re-openable on [UTF-RW]'s
  population, which may carry many-interval byte classes this corpus lacks
  ([S] §9).
- **The kit takes a bare interval list and nothing else** (Constitutional
  Constraint 1). It is what lets `cube_of` rediscover the ASCII fold (`{S,s}`
  → `(c|0x20)=='s'`) and three case-blind cubes today's classifier cannot see
  ([S] §4.3), and it is what makes the composition identity
  `kit(A∪B) ≡ kit(A)||kit(B)` a law the implementation can be tested against
  (438 cells × 1,114,112 code points, 0 mismatches, [S] §7). **An
  implementation that adds a provenance or "hint" argument retires that test
  silently** (studies/cls_tree_study/CLAUDE.md, "two invariants"); S1's review
  checks the signature.

### 1.2 The DP's speed term was never a time model, and the timing run shows it

The study's objective is

```
best[j] = min over i of  best[i] + rodata(i..j) + text(i..j) + λ·ops(i..j)
```

and `ops(i..j)` is the section's leaf op count (`section.py` `offer(...)`,
plus `DISP_OPS = 1.0` per section). Summed over the partition, `Σ ops` is the
op count of the WHOLE matcher's code. A single probe runs the dispatch path
and ONE leaf. So the term the dial has been pricing is a second code-size
measure, not a per-probe cost. `kit.py`'s own header said as much — "`ops` (a
MODEL weight used only to steer the sectioning search) ... the emitted matcher
is compiled and TIMED, and the model's job is only to generate candidates for
the measurement to rank" — and the ranking by timing was then never done: the
Mac refused ([S] §11), the ubuntubudu run landed 2026-09-11, and nobody read it
against the model. `opt_dial_design.md` §4 pinned λ from the ops column in the
meantime.

**[T], read by `timefit.py` (`results/timefit_20260928.txt`), 12 K53 sets ×
3 policies (λ = 0, 16, 256):**

| regime | r(ns, model ops) | ρ | fewer model ops ⇒ faster, within a set | geomean vs flat bsearch: `bitmap1` / λ0 / λ16 / λ256 |
|---|---:|---:|---:|---|
| member | **−0.00** | +0.13 | **17 / 36** | **0.109** / 0.416 / 0.499 / 0.417 |
| mixed | +0.07 | +0.17 | 20 / 36 | 0.147 / 0.461 / 0.514 / 0.439 |
| full | +0.16 | +0.25 | 24 / 36 | 0.159 / 0.429 / 0.469 / 0.401 |
| ascii | −0.02 | +0.01 | 15 / 36 | 0.190 / 0.300 / 0.303 / 0.306 |

Three readings, each from the table and nothing else:

1. **The kit is 1.9-3.3× faster than [CLS-TREE]'s own seed** (the flat binary
   search, `refbs`) at every policy and regime. The kit is worth building.
2. **Among kit policies the model ranks nothing.** On uniformly random
   members, "fewer model ops is faster" holds 17 times in 36, a coin toss.
   `\p{L}` itself: λ0 has 206 model ops and 10.2 ns/char, λ16 has 108 ops and
   11.4 ns ([T] medians; ops from `results/sweep_k53.tsv`). So the five pinned
   λ constants select among matchers with the same speed.
3. **The one arm that is much faster has NO dispatch tree.** `bitmap1` — one
   bitmap over the whole span, one bound test and one load — is 3.8× faster
   than the fastest kit policy and 4.6× faster than the middle on member
   subjects (geomean 0.109 vs 0.416 and 0.499 of `refbs`)
   and never slower than the kit in any regime. The dispatch tree's
   data-dependent branches are the cost on random subjects; the leaves are
   not. (The `ascii` regime makes the point from the other side: every probe
   takes the same dispatch path, the branches predict, and the kit closes to
   within 11-17% of `bitmap1` — `\p{L}` λ0 5.88, λ16 6.10, λ256 6.22 vs
   5.31 ns, [T] **[r1 ALT-1]**. `bitmap1` itself
   pays a mispredicted BOUND branch there, cp < 65 or not.)

**[r1 MEAS-2] One noisy cell, disclosed and bounded.** `^C` on member
subjects is BIMODAL in [T]: rounds {0,6,7,8,9} read high and the other six
low, in lockstep across all five arms (`bitmap1` 1.60 vs 13.30 ns) — an
environmental effect on that one run, not arm behaviour; no other cell
varies >2×. The medians land in the low cluster. Dropping `^C` entirely
(11 sets) leaves every reading standing: member r = +0.06, pairwise 16/33,
geomean `bitmap1` 0.113 / λ0 0.409 / λ16 0.467 of `refbs` (mixed 18/33,
full 21/33, ascii 14/33). b1 re-measures it.

**Decision CT-2.** The DP stays (its byte model is verified to ~3%, [S] §5.2;
its search is exact; its compile time is 25.86 ms worst, [S] §6). Its speed
term is replaced by a **modelled per-probe time**:

```
T(partition) = t_bound + t_disp(m) + Σ_s p_s · t_leaf(form_s)
```

with `m` the section count, `t_disp` the dispatch tree's cost (a function of
depth ≈ log2 m and of branch predictability), `p_s` the probability a probe
lands in section `s`, and `t_leaf` per form (dependent loads counted
separately from ALU ops, the study's `OP_DEP_LOAD` distinction). Two things
about this form are decided here and two are left to the calibration:

- **Decided: it is per probe.** Whatever the calibration finds, the objective
  never again sums leaf costs over sections unweighted.
- **Decided: `p_s` is a DECLARED distribution, uniform over the set's
  members.** The compiler cannot know the subject, and "member" is the regime
  where the matcher's answer matters most (a match continues the walk). The
  study named the alternative — a frequency-weighted tree — and its
  dependency, a code-point frequency model from [UTF-RW] ([S] §9). Uniform
  over members is the one choice that needs no data.
- **Left to calibration: `t_disp(m)`'s shape and each form's `t_leaf`.** They
  are fitted from `make bench2` on ubuntubudu (§7 b1), which adds the
  whole-set arms and a `runs` regime (text-like: the dispatch branches
  predict). **The DP's exactness survives only if `t_disp` is additive per
  section** (the study's `DISP_OPS` form). If the fit says it is logarithmic
  in `m`, the DP gains a section-count dimension (`best[j][m]`, O(n·64·M)); at
  M ≈ 40 that multiplies 25.86 ms by ~40, about 1 s on the worst set, which
  would re-open [S] §6's D77 cache verdict. That is a measured consequence to
  weigh at S0, not a reason to pick a form now.

### 1.3 Whole-set tables: the forms `MAXK = 64` made unreachable

`section.py` caps a section at 64 intervals "to make the DP O(n·64)" and the
study names the cap as never swept ([S] §9). The cap has a consequence the
study did not draw out: **no sectioning of a 677-931-interval set can be ONE
section**, so the fastest measured arm (`bitmap1`) and PCRE2's own lookup
shape (a staged table over the whole set) are outside the search space. At
λ = ∞ the DP builds `\p{L}` as 11 `BITMAP` sections behind a dispatch tree
([S] §5.2), which is the worst of both.

This lane built two whole-set forms (`studies/cls_tree_study/wholeset.py`),
both branch-free after one bound test, both taking a bare interval list, and
verified them exhaustively on all 1,114,112 code points against the study's
independent reference ([N] `verify_whole.py`): **0 mismatches on the 12 K53
sets**, and on all 312 `uprops` sets (`results/whole_uprops.tsv`).

**[N] `results/whole_k53.tsv`, object bytes (`.text + .rodata`, the study's
unit), set to the right of the study's own policies ([S] `sweep_k53.tsv`) and
today's emitted DFA ([S] `baseline.tsv` at `13b56a12`; `\p{Xwd}` re-baselined
at `13b7c202`, `ucp_study.md` §E):**

| set | kit λ0 | kit λ16 (mid) | kit λ256 | **page3w** (3-stage) | page2w (2-stage) | `bitmap1` | today, DFA |
|---|---:|---:|---:|---:|---:|---:|---:|
| `\p{L}` | 4,318 | 4,359 | 5,850 | **4,249** | 8,666 | 25,710 | 227,409 |
| `\P{L}` | 4,242 | 4,395 | 6,305 | **5,128** | 37,044 | 139,264 | — |
| `\p{C}` | 4,586 | 4,667 | 6,530 | **5,480** | 37,140 | 139,264 | 228,957 |
| `\p{Cn}` | 4,538 | 4,580 | 6,409 | **5,472** | 37,100 | 139,153 | 211,305 |
| `\p{Xan}` | 4,625 | 4,959 | 7,561 | **4,641** | 8,898 | 25,712 | 267,541 |
| `\p{Xwd}` | 4,947 | 5,326 | 6,866 | **5,545** | 31,300 | 114,744 | 294,153 → **197,685** |
| `\P{Xwd}` | 4,958 | 5,292 | 7,643 | **5,728** | 37,420 | 139,264 | — |
| `\p{Unknown}` | 4,506 | 4,684 | 6,369 | **5,432** | 37,092 | 139,153 | 215,055 |

(`bitmap1` is rodata only, `⌈span/8⌉`; its `.text` is ~60 B. The `—` cells
were not in the study's baseline.)

**The three-stage table costs about the kit's middle in bytes** (−6% to
+20% across the eight rows, and SMALLER than λ16 on `\p{L}` and `\p{Xan}`),
with no dispatch tree at all: `top[cp>>10] → a deduplicated block of 16 page
indices → a deduplicated 64-bit leaf`, three dependent loads. Its speed is
UNMEASURED — it is the headline arm of §7 b1. If it lands near `bitmap1`, it
dominates every multi-section kit matcher for the huge sets on both axes, and
the multi-section DP becomes the SIZE end's mechanism only. The design is
built so that outcome needs no redesign:

**Decision CT-1 (the whole-set half).** The DP offers, in addition to its
contiguous ≤ 64-interval sections, ONE extra candidate: the whole set as a
single section, for each table member (`BITMAP`, `PAGE64`, and a three-stage
`PAGE` if §7 b1 admits it). Pricing stays O(k): `BITMAP` is `⌈span/8⌉`,
`PAGE64`'s distinct-leaf count is already O(k) ([S] §6), and a three-stage
table's distinct-block count is O(k) by the same argument (only blocks an
interval starts or ends in can be partial). No table is materialized unless
chosen. **This is not a special case**: a whole-set section is a section; the
cap was a search bound, not a statement about the answer.

**Population-wide ([N] `results/whole_uprops.tsv`, all 312 sets, 0
mismatches):** `page3w` totals **114,609** object bytes against the kit's
85,613 at λ16 and 84,106 at λ0 ([S] `sweep_uprops.tsv`). The whole excess is
in the SMALL sets, where the kit emits a few compares and no table: over the
28 sets with ≥ 46 intervals `page3w` is **59,991** against the kit's 58,038
(+3.4%). **[r1 MEAS-1]** (first draft: 58,466 / +2.6% — a name-keyed sum
that double-counted one of two same-named sets). That is the DP's job, not a problem — offered as a candidate, a
whole-set table is chosen only where it pays.

**[r1 ALT-3] How the whole-set candidate enters the DP.** `section.py`'s
recurrence reaches a section only through its ≤ 64-interval window, so a
whole-set section cannot be a PART of a larger partition; it is compared at
`best[n]` as a one-section alternative. S1 may generalise this (a table
section over any contiguous run, priced in O(k)); the first build offers the
whole set only, which is exactly the population §1.3's numbers measure.

`page3w`'s stage width (TS = 10) was chosen as the size-minimum of TS ∈ {10,
12, 14} on the K53 twelve (4.2-5.6 KB at 10, 5.8-6.8 KB at 12, 8.3-9.8 KB at
14, rodata only — [N] `results/page3_ts_k53.tsv`, `python3 wholeset.py k53`;
committed at **[r1 MEAS-4]**, the first draft cited an uncommitted sweep). A general three-stage member
would let the DP pick TS per set; that is S1's implementer's choice under the
same O(k) pricing, and it is not a new member.

### 1.4 λ → `--tune`

**What is pinned today.** `opt_dial_design.md` §4: −2 → λ 4, −1 → 16,
0 → 16, +1 → 64, +2 → 256, derived by the rubric from the study's ops
column. `src/core/tune.c:86-98` records +2 as "IDENTICAL TO +1 ON EVERY CELL"
until "lambda is implemented (`[CLS-TREE]`)". And Frank's +2 direction
(2026-09-16, the plan row): the extreme-speed forms — "full-table/huge-bitmap
class membership ... its few huge bitmaps at 5.6x size for 6 probe ops notch"
— are **+2's intended content**, priced as a real λ position with its measured
rate, not excluded by the rubric's `Z₂ = 2.0` budget.

**What [T] changes.** Every one of the five constants picks among matchers the
timing cannot tell apart (§1.2 reading 2). They are pinned to a term that is
a size proxy, so at today's constants the dial's speed positions buy BYTES,
not speed: on `\p{L}`, member subjects, λ256 costs +34% bytes over λ16 and
runs 10.23 vs 11.42 ns — while λ0, the SIZE end, runs 10.18 ([T] medians).

**Decision CT-3.**

1. **One mechanism, five constants.** Every position runs the same DP (CT-2's
   objective, CT-1's candidates) with its own pinned λ. No position names a
   form. +2's extreme-speed content arrives because at +2's λ the DP chooses
   the whole-set bitmap where it is the fastest measured form — which is
   Frank's direction reached by the general mechanism, not a +2 special case.
2. **The five constants are RE-PROPOSED after S0's calibration, as one ruled
   diff to `opt_dial_design.md` §4 and `tuning.md`'s λ row** (D103 point 1:
   a measurement landing never moves a cell by itself; D103 addendum: the
   rubric proposes, placement is art). Until then the λ row stays
   "reservation", as `tuning.md` has it.
3. **The +2 rate is stated now, from [T] and [N], so the ruling has it:**
   `bitmap1` is **3.8-4.6× faster than the kit on member subjects** (geomean
   over the twelve sets, against the fastest and the middle policy, [T]); on
   `\p{L}` it costs **5.9× the middle's bytes** (25,710 vs 4,359); on `\P{L}` the bytes are 32× (139,264 vs 4,395), because the
   complement's span is all of Unicode. Against TODAY's emitted DFA for the
   same set, `bitmap1` is still 1.5-10.4× SMALLER (`\p{Cn}` 139,153 vs
   211,305; `\p{Xan}` 25,712 vs 267,541; [S] `baseline.tsv`). If `page3w` times near `bitmap1`, +2's rate collapses
   and the proposal will say so.

### 1.5 The byte tier

Every one of the 41 distinct byte classes in the shipped corpus (2-4
intervals each, 319 sites) compiles at the middle policy to **1,584 B of
`.text` and zero `.rodata`**, 82 sections (69 `ALL`, 8 `CUBES`, 5 `MASK64`),
246/246 exhaustively verified ([S] §4.4) — against a 32-byte bitmap table per
bitmap-class site today. At the byte tier the policies agree ([S] §5.3 item
5): no table appears at any λ, so the dial is invariant there in practice and
the calibration question of §1.2 does not arise.

Its TIMING is not in [T] (a code-point membership loop), and the one byte-tier
timing on file points the other way at noise level: the bench's abi-23 AFTER
measured `cls-fold` slower on its single witness (ci-256 forced-VM ×1.027
search / ×1.045 thr / ×1.095 match vs a 1.34% floor; plan.md [FORM-CHAR2]).
That is the byte tier's owed measurement (§7 b2).

### 1.6 Where it lives, and what it costs to compile

One module (`src/gen/clskit.c`, the name is the implementer's), a pure
function from a code-point set and a λ to (a) the chosen sectioning and (b)
its emitted C text, called once per DISTINCT set per artifact (sites share one
`static inline int $_clsN(unsigned cp)`). It reads λ from the tune table and
nothing else (D82: one decision point). Compile time is [S] §6's: 25.86 ms on
the worst set, per distinct set, less than a fifth of the 144 ms `build/pcrec`
already spent compiling `\p{Xwd}` at `13b56a12`. **No per-artifact limit is
added**: nothing measured needs one (D77). The trigger that would: a pattern
with hundreds of distinct large classes ([S] §6's own qualification), which
no corpus or bench pattern is known to be.

### 1.7 S0 calibration results (lane clsfit, 2026-09-29)

**Status: MEASURED; the λ re-proposal in §1.7.5 is PROPOSED** (D129 Q1:
one ruled diff; the manager takes it to Frank). Nothing under `src/`,
`tests/` or `docs/spec/` moves here.

**Sources.** Three new ubuntubudu files, copied verbatim from pcrec-bench
branch `scratch/clstree-s0` (each carries a `# provenance:` first line), and
one analysis:

| tag | what | where |
|---|---|---|
| **[T2]** | `make bench2`: 12 K53 sets × 5 regimes × 7 arms × 11 interleaved rounds, gcc 15.2.0, pcrec pin `dd3be4e4` (archive form), load1 0.02, 4,620 rows, no `ANSWER MISMATCH` (bench `81f0982`, outbox O-76) | `studies/cls_tree_study/results/bench2_ubuntubudu_20260929.tsv`, column `ns_per_char` (medians over rounds) |
| **[C2]** | the isolated `^C`/member re-run, 41 rounds, load1 0.21 (bench `d6e0106`) | `results/capC_isolated_ubuntubudu_20260929.tsv` |
| **[B2]** | `make bench2-bytes` ([OPT-CLSPACK]), N = 4/16/32, load1 0.46 (the fixed gate waited once, at 0.54) (bench `81f0982`) | `results/bench2_bytes_ubuntubudu_20260929.tsv`, column `ns_per_call` |
| **[F]** | `timefit_s0.py` (analysis only; runs anywhere) | `results/timefit_s0_20260929.txt` — every number below not cited to another file is read from it |

#### 1.7.1 The per-probe model fits; the old term still does not

**Method.** `timefit_s0.py` REPLAYS every timed arm probe by probe over the
harness's own subject stream: `bench.py`'s xorshift generator reproduced bit
for bit, and **verified** by regenerating all 2^20 probes of every (set,
regime) and matching the harness's own `hits` + positional `chk` columns
(60/60 streams, [F] line 1). The 09-11 run [T] used the identical streams
(48/48 `refbs` hits+chk equal), so the replay applies to it exactly. Each
probe is costed in four counted quantities: conditional branches, their
MISPREDICTS under a 2-bit counter per static branch site, loads, and
dependent loads. One OLS over all 420 (set, regime, arm) medians of [T2] —
the kit's three policies, the flat bsearch and the three whole-set tables
under one model — gives

```
ns/char = 2.095 + 3.892·mispredicts + 0.189·branches − 0.090·loads + 0.095·deploads
```

**The old term, re-read on the fresh run** ([F] "OLD term"; timefit.py's
statistics): member r(ns, `model_ops`) = **+0.08**, fewer-ops-is-faster
**19/36**; mixed +0.06, 20/36; full +0.11, 22/36; ascii −0.04, 12/36; runs
+0.43, 32/36. The 09-11 refutation replicates in every random regime. Only
on `runs`, where the dispatch branches predict, does an op count track time.

**The new model** ([F] "FIT"; LOSO = leave-one-SET-out, refitted twelve
times):

| regime | all 7 arms r (LOSO) | ρ | kit 3 policies r | kit pairwise (LOSO) | all-arm pairwise |
|---|---:|---:|---:|---:|---:|
| member | **+0.98** (+0.98) | +0.96 | +0.90 | **30/36** (30/36) | 236/252 |
| mixed | +0.98 (+0.98) | +0.97 | +0.88 | 27/36 (27/36) | 232/252 |
| full | +0.98 (+0.98) | +0.98 | +0.92 | 29/36 (29/36) | 231/252 |
| ascii | +0.97 (+0.97) | +0.94 | +0.96 | 6/24 (14/24) | 191/216 |
| runs | +0.96 (+0.96) | +0.96 | +0.80 | 29/36 (28/36) | 236/252 |

Without `^C` (11 sets, refitted: 2.088 + 4.081·mis + 0.170·br − 0.075·ld +
0.071·dep): member all-arm r +0.98, kit r +0.89, kit pairwise 27/33; every
other r within 0.01 of the 12-set fit. **Held out — [T2]'s coefficients, unrefitted, on
the 09-11 run [T]** ([F] "TRANSFER"): member kit pairwise **30/36** (the old
term: 17/36), all-arm r +0.92 (+0.97 without `^C`); mixed 29/36, r +0.98;
full 31/36, r +0.98; ascii 10/24, r +0.97.

Four readings:

1. **Yes: the refitted model predicts measured time where λ·Σops did not.**
   Member-subject kit orderings go from a coin toss (17/36 on [T], 19/36 on
   [T2]) to 30/36 on both, and r from −0.00 to +0.90 over the kit's
   policies (+0.98 over all arms), out of sample on a run it never saw.
2. **Per-probe time is branch MISPREDICTS**: 3.9 ns each, plus 0.19 ns per
   predicted branch. Loads are free to within ±0.1 ns in this
   throughput-bound loop (each table arm's load chain is fixed, so those two
   coefficients are not separately determined). §1.2 reading 3 — the
   dispatch tree's data-dependent branches are the cost — is now a fitted
   model, not an inference.
3. **Its limits, stated.** (a) The `ascii` kit ordering (6/24): there the
   three policies sit within 0.5 ns of each other and several at the floor;
   the model has nothing to resolve. (b) It does not resolve one TABLE
   against another: `page3w` measures 1.20-1.37× `page2w` on member
   subjects (0.35-0.63 ns), the model gives it one extra dependent load,
   0.095 ns. It ranks trees against tables, not tables against tables.
4. **CT-2's additivity question is answered "no", and §1.7.4 shows it no
   longer matters.** A probe's mispredicts depend on the branch biases along
   its whole path, a property of the tree's shape, not of one section; an
   exact DP carrying this T would need tree-shape state.

**`^C` [r1 MEAS-2] — closed.** [C2]: 41 rounds, max/min ≤ 1.13 on every arm
(`bitmap1` 1.78-1.80, λ0 10.95-11.12), medians within 3% of [T2]'s 11-round
cell. The 09-11 bimodality (`bitmap1` 1.60 vs 13.30) did not recur in 52
rounds over two sessions: an environmental effect on that one run. Every
reading above holds with and without `^C`.

#### 1.7.2 Whole-set tables vs the kit, per regime (the +2 rate question)

Geomean over the twelve sets of each arm's median ns/char, as a fraction of
the flat bsearch `refbs` ([F] "geo/refbs" rows; [T2]):

| regime | `bitmap1` | `page2w` | `page3w` | λ0 | λ16 | λ256 |
|---|---:|---:|---:|---:|---:|---:|
| member | 0.116 | 0.115 | **0.145** | 0.417 | 0.457 | 0.383 |
| mixed | 0.147 | 0.145 | 0.171 | 0.453 | 0.506 | 0.434 |
| full | 0.160 | 0.159 | 0.183 | 0.421 | 0.465 | 0.402 |
| ascii | 0.211 | 0.211 | 0.236 | 0.283 | 0.284 | 0.290 |
| runs | 0.163 | 0.162 | 0.209 | 0.390 | 0.381 | 0.307 |

The harness floor is 1.69 ns (the fastest cell in [T2]): the per-probe
indirect call through the arm table, the loop and the bound test, paid by
every arm. `bitmap1` and `page2w` sit on it.

1. **`page3w` comes close to `bitmap1`**: on member subjects 1.20-1.31×
   `bitmap1` (2.13-2.32 vs 1.77-1.86 ns; 0.44-0.63 ns above the floor),
   0.99-1.54× across the other regimes (the 1.54 is `runs` `^L`). It is **1.26-4.50×
   faster than the FASTEST kit policy on member subjects** and faster in
   **57 of 60** set×regime cells; one ties at the floor (`ascii`
   `Unknown`, every arm but `refbs` at 1.77) and two go to the kit, both within 0.25 ns
   (`ascii` `Cn` λ256 1.77 vs 1.92; `runs` `^L` λ256 2.49 vs 2.74) ([F]
   "best-kit/page3w" column).
2. **`page2w` times at `bitmap1` in every cell** (member 1.69-1.79 vs
   1.77-1.86) and is 2.9-3.8× smaller (8,666-37,420 vs 25,770-139,324 B;
   [N] `whole_k53.tsv` `page2w_obj`; `bitmap1` = its exact rodata + 60 B).
   `bitmap1` is dominated on both axes on all twelve sets.
3. **The +2 rate (§1.4 point 3), restated from measurement.** `page3w`
   costs 1.01-1.23× the kit's size-minimal bytes (`K`, λ = 4, [S]
   `sweep_k53.tsv` `total`); `page2w` costs 1.9-7.2× `page3w`'s bytes for
   1.20-1.37× member speed. Against TODAY's pinned middle (kit λ16), `page3w`
   is **3.2× faster** on member subjects (geomean 7.04 → 2.23 ns) for
   **+11% bytes** (4,735 → 5,250 B geomean) ([F] "row cost"). So +2's
   content is `page2w`, not `bitmap1`: the same speed at a third of the
   bytes. The +2 step over the middle is real but small — 0.35-0.63 ns a
   probe in a loop whose floor is 1.69.
4. **`runs`** (text-like): the kit closes but does not catch up (best kit
   policy 0.91-1.87× `page3w`, geomean λ256 0.307 vs `page3w` 0.209 of
   `refbs`). λ256 buys 21% over λ0 here (0.307 vs 0.390), the one regime
   where the kit's policies separate by more than noise.

#### 1.7.3 [OPT-CLSPACK]: bitmap vs kit vs shared atom table ([B2])

Median ns/call over 11 rounds [min-max]; `n_atoms` 5 / 16 / 29:

| N | `refbs` | `bitmap` | `kit` (λ16) | `atom` |
|---:|---:|---:|---:|---:|
| 4 | 12.22 | 2.070 [2.069-2.084] | 9.69 [9.68-9.74] | 2.070 [2.069-2.077] |
| 16 | 17.03 | 2.070 [2.069-2.076] | 11.50 [11.49-11.52] | 2.070 [2.068-2.074] |
| 32 | 17.68 | 2.070 [2.069-2.090] | 12.18 [12.17-12.19] | 2.070 [2.069-2.093] |

1. **`atom` vs `bitmap`: a tie at the harness floor**, identical medians at
   every N and overlapping ranges. The loop is throughput-bound (independent
   iterations), so it cannot see the atom's second dependent load; STEP 0's
   24% atom-over-bit-array win (a latency-shaped VM hand twin,
   `form_char_step0.md`) is neither reproduced nor refuted.
2. **`kit` reads 4.7-5.9× slower, and the number is NOT the kit's test.**
   `bench_bytes.py` reaches site i's kit test through a per-site FUNCTION
   POINTER (`kit_fns[site]`), a data-dependent indirect call on random sites;
   `bitmap` and `atom` reach site i by indexing DATA (`bm_tabs[site]`,
   `atom_masks[site]`), with no control transfer. The gap is that dispatch
   difference plus the kit's own branches on random bytes, and this data
   cannot separate them. **Fixed shape, this lane:** `bench_bytes.py
   --dispatch switch` gives every arm the same `switch (site)` with site
   i's test inlined in case i — the shape a VM with one instruction per
   class site has. Mac smoke: answers only, 24 rows, 0 mismatches; not
   timed (Darwin timing is never citable).
3. **Bytes** (box-independent; first N classes of `byteclasses.tsv`, the
   same N [B2] timed): `bitmap` 32N rodata = 128 / 512 / 1,024 B; `atom`
   256 + 8N = 288 / 384 / 512 B; `kit` 0 rodata, `.text` 128 / 596 / 1,276 B
   ([S] `sweep_byteclasses.tsv` λ16 `total`, arm64 model; the two table arms'
   per-site test code is not counted). `atom` beats `bitmap` above N = 10.7
   (the row's own "~10"), and beats the kit's `.text` at N = 16 and 32.
   D129 Q5's premise that the kit's byte tier answers the size question
   holds for `.rodata` only; counted as `.text + .rodata`, the atom table is
   the smaller form at N ≥ 16 on this population.

**Recommendation: keep [OPT-CLSPACK] open, as a SIZE-PRIORITIZED row, and
settle its default status with one re-run.** Frank's own filing rule ("if it
impacts performance, limit to scenarios where we are prioritizing space")
decides it once the time comparison that matters (atom vs the kit, since S2
replaces bitmaps with the kit) exists. Proposed first-match rows for a byte
class site, stated now so the re-run's outcome picks one without new
argument: at `−2`/`−1`, (1) `atom` if the artifact has ≥ 11 byte-class sites
and ≤ 64 atoms, (2) the kit; at `0`..`+2`, (1) `atom` under the same
condition **only if** the `--dispatch switch` re-run times it ≤ the kit at
N = 16 and 32 beyond the round range, (2) the kit. The re-run is `make -C
studies/cls_tree_study bench2-bytes CC=gcc` with `--dispatch switch` added
(about a minute of box time; §7 b).

#### 1.7.4 The dial: the DP against a first-match table (Frank's option-2 trigger)

[F] "DIAL" evaluates the DP's objective `min bytes + λ·T̂` over every
candidate — the kit at λ = 4/0/16/256, `page3w`, `page2w`, `bitmap1` — with
T̂ the fitted member-subject time, on the twelve timed sets:

| λ (bytes per ns) | 0 | 250 | 500 … 100,000 | 1,000,000 |
|---|---|---|---|---|
| DP picks | `K` ×12 | `K` ×6, `page3w` ×6 | **`page3w` ×12** | `page3w` ×10, `page2w` ×2 |

and the first-match rows of §1.7.5 pick `K` ×12 at `−2`/`−1`, `page3w` ×12
at `0`/`+1`, `page2w` ×12 at `+2`. So:

- **The DP reproduces the table at `−2` and `0`, and never picks a
  multi-section kit sectioning at any λ > 4.** λ256 is DOMINATED by
  `page3w` on both axes on all twelve sets (1.17-1.63× its bytes, slower in
  every member cell); λ16 is larger than `K` and the slowest kit policy on
  member subjects in 8 of 12 sets. λ256 does buy time over λ0 (up to 31% on
  member subjects, 21% geomean on `runs`), but `page3w` buys 1.26-4.50× for
  1-23% more bytes than `K`, so a price of time high enough to pay for a
  λ256 sectioning pays for `page3w` first.
- **At `+2` the DP is worse than the table.** The model does not resolve
  `page2w` against `page3w` (§1.7.1 reading 3b), so even at 10⁶ B/ns it
  takes `page2w` on 2 of 12 sets; the first-match row, written on the
  MEASURED ordering, takes it on 12.
- **So on these numbers the DP with a time term is no better than a greedy
  first-match rule, and worse at one position. That is Frank's option-2
  trigger, stated.** The DP keeps one job: the optimizer INSIDE the `K`
  row, a size minimizer over contiguous partitions whose byte model is
  verified to ~3% ([S] §5.2). CT-2's per-probe model stays too, as the
  RUBRIC's instrument for arguing placements (it is what shows λ > 4 buys
  nothing), not as a term the compiler evaluates.

**Row cost** ([F] "row cost", geomean over the twelve; `K` is untimed at
λ = 4 and read at λ0's time):

| row | bytes | member | mixed | full | ascii | runs |
|---|---:|---:|---:|---:|---:|---:|
| today's pinned `0`/`−1` (kit λ16) | 4,735 | 7.04 | 8.03 | 6.65 | 3.30 | 4.15 |
| today's pinned `+2` (kit λ256) | 6,767 | 5.89 | 6.89 | 5.76 | 3.37 | 3.34 |
| proposed `−2`/`−1` (`K`) | 4,493 | 6.41 | 7.18 | 6.03 | 3.29 | 4.25 |
| proposed `0`/`+1` (`page3w`) | 5,250 | **2.23** | 2.70 | 2.62 | 2.74 | 2.27 |
| proposed `+2` (`page2w`) | 27,948 | 1.77 | 2.30 | 2.27 | 2.45 | 1.77 |

**Population-wide (312 `uprops` sets, bytes only — no set outside K53 was
timed; [F] "POPULATION", `K` = kit λ0, the size end `sweep_uprops.tsv`
has):** with the 16-section gate the middle row sends **9/312** sets to
`page3w` and totals 85,381 B (−0.3% vs the kit λ16 total of 85,613 B); the
`+2` row totals 219,973 B (2.57×). Without the gate (any `K` with ≥ 2
sections) it would send 52 sets and total +0.6%; the gate costs no bytes
either way, and it exists because below 16 sections nothing is timed.

#### 1.7.5 The λ re-proposal — PROPOSED

The one diff to `docs/design/opt_dial_design.md` §4 and `docs/spec/tuning.md`'s
λ row is verbatim in `docs/dev/lanes/clsfit_report.md` (it applies cleanly to
`main` at `608bd094`; NOT applied here). Its table:

| position | the class matcher — first match wins | kit λ |
|---|---|---:|
| `−2` | the smaller of {`K`, `P3`} | 4 |
| `−1` | = `−2` | 4 |
| `0` | (1) `P3` if `K` has ≥ 16 sections and bytes(`P3`) ≤ 1.26 × bytes(`K`); (2) `K` | 4 |
| `+1` | = `0` | 4 |
| `+2` | (1) where `0` chose `P3`: the smaller of {`P2`, `B1`}; (2) as `0` | 4 |

**Three distinct programs, not five** — the class row collapses the way
bench O-74 found `--tune` collapsing per route. What it changes in this
note, if ruled: CT-2's DP keeps its exact size search and drops its speed
term (§1.7.4); CT-3's "five pinned λ" become one kit constant and this
table; CT-1's whole-set candidates are rows, not DP sections (§1.3 [r1
ALT-3]'s one-section-alternative entry is exactly a row's argmin).
Placements Frank may move (D103 addendum, "placement is art"): `z_mid`
(1.26; at 1.20 six of the twelve fall back to `K`), the 16-section gate (a
placement at the bottom of the timed range; `K` has 16-22 sections at λ = 4
on the twelve), and whether `+1` should take `P2` where it is ≤ 2× `P3`
(`L`, `Xan`).

---

## 2. The VM instruction shape

### 2.1 The node (CT-4)

Today `pcrec_lower_enc` rewrites every non-ASCII class, in place, into
`A_CAT(A_EMPTY, A_ALT(...))` of byte-range chains (`src/opt/lower_enc.c:309-
360`), before BOTH the NFA builder and the VM emitter, because "those are the
two consumers that can only express BYTES" (`src/core/compile.c:1479-1485`).
After that line every `A_CLASS` is a byte class, and the tree relies on it:
**145 mentions of `A_CLASS` under `src/`, 49 `case A_CLASS` arms and 6
`==`/`!=` comparisons, across 19 files** ([P] grep at `73590d19`) — PATFACTS'
necessary sets, the prefilter, possessify, the start-anchor and end-window
derivations, `vm_cls`'s 32-byte interning. A code-point set reaching `vm_cls`
compiles to a silent miscompile (r54 E1, quoted at compile.c:1482).

**So the one node is a NEW kind, not a flag.** `pcrec_lower_enc` replaces a
class whose encoding automaton is deeper than one code unit with an
`A_WCLASS` node carrying:

- the code-point set (sorted, disjoint, non-adjacent — cpset's invariant), and
- **during implement-then-replace, today's lowered alternation as a child**,
  built by the unchanged `u8_box`/`u8_ranges`.

The depth-1 test is not new: it is `lower_class_utf8`'s existing ASCII
identity fast path (`hi <= 0x7F` → untouched, lower_enc.c:311-314), which
under the byte encoding is every class. The rule reads the ENCODING'S answer,
so DD-12 (7)'s "no encoding conditionals" holds: the byte backend never makes
the node because no byte class is deeper than one unit.

**The readers are enumerated by the compiler, not by memory.** The coding
guide's no-`default:` exhaustive-switch rule (coding_guide.md §1.3) makes
`-Wswitch` fire at each of the 49 `case A_CLASS` switches that does not handle
the new kind; the 6 comparisons are found by grep. At S3 every reader walks the
child — byte-identical artifacts by construction — and later stages move
readers off the child one at a time; the child is deleted when no reader walks
it. (The splice-in-place invariant compile.c:1497-1508 states holds: the new
node replaces a leaf, and leaves are not group roots.)

### 2.2 The test (CT-5)

At a VM class site whose operand is an `A_WCLASS`:

```c
/* shape, not final text */
if (pos >= n) goto fail;
len = $_decode(subject, n, pos, &cp);
if (len == 0 || !$_cls3(cp)) goto fail;
pos += len;
```

and the same pair inside the possessified span loops and counted-class loops
(`while (pos < n && (len = $_decode(...)) && $_cls3(cp)) pos += len;`).

- **`$_decode` is a new encoding-seam entry, `PCREC_ENCE_DECODE`.**
  `engine_callable` (an engine body calls it — the `PCREC_ENCE_SPAN`
  precedent, `src/enc/enc.h`), in the artifact's mask only when a decode site exists.
- **Its body is stage 4's `$_span_ci_decode`, verbatim** (enc_utf8.c:187-214):
  1-4 bytes, returns 0 on a truncated sequence, a bad continuation, an
  overlong form, a surrogate or a value above U+10FFFF. The comment there
  already states the property this design needs: "the ill-formed set is
  exactly the automaton's (overlong forms, surrogates and code points above
  U+10FFFF are excluded from every lowered class), so a subject this compare
  rejects is one no other part of the artifact would have matched either."
  **One decoder, not two**: `SPAN_CASELESS`'s private copy retires into the
  entry, and `SPAN_CASELESS` in the mask implies `DECODE` in the mask. That
  implication is a new seam fact (an entry depending on an entry) and is a
  D58 event, recorded against D58 as its revisit clause asks.
- **`static inline`, not exported.** The existing entries are exported only
  because an always-emitted unused `static` fails the harness's `-Werror`
  build (`src/enc/enc.h`, the entries-table header comment); a masked-in-only-when-called entry has no such problem,
  and an exported function is interposable under `-fPIC`, so gcc will not
  inline it into a shared-object build ([CC-DIFF] STEP 0's finding is gcc
  stopping at exactly such call boundaries). The class predicate is
  `static inline` for the same reason.
- **The byte backend has no `DECODE` row.** A depth-1 class never decodes
  (CT-4), and a backend under which the entry is never needed has no row —
  `PCREC_ENCE_VAR_VALID`'s precedent (`src/enc/enc.h`).

**Surrogates.** A complemented set (`\P{L}`, `[^a]`) includes
U+D800-U+DFFF, because cpset complements within `[0, max_cp]`. The decoder
never yields them, so the kit's answer there is unreachable. Treating the gap
as a don't-care would let the DP merge across it (fewer intervals); it is NOT
done, because nothing measured says it pays and it would make the kit's input
something other than the set (Constraint 1). Named, D77.

**Backward reads.** The VM's `\b` reads `subject[scan_position-1]` as a byte
(emit_vm.c:7908). That is ASCII `\w`'s correct semantics today and is not
touched. UCP's `\b` needs "decode the character ENDING here": `back_step`
(PCREC_ENCE_BACK_STEP) plus `$_decode` plus the kit (§9).

### 2.3 What the VM gains, measured

| pattern (`-e utf8`) | today, VM | with the kit (S4) |
|---|---|---|
| `\P{Unknown}` `--engine=vm` | REFUSED: 689,367 B code > 500,000 (K55) | one `static inline` matcher, 4.5-6.7 KB object across policies ([S] `sweep_k53.tsv`, `^Unknown(Zzzz)`) |
| `\p{Xwd}` | REFUSED: 576,063 B code (`ucp_study.md` §E) | 4.9-6.9 KB ([S]) |
| `(\p{Xwd})` — captures route to the VM | REFUSED: 579,674 B (`ucp_study.md` §E) | as above: **any captured UCP `\w` becomes buildable** |
| `(\p{L})` | REFUSED: "1187962 bytes of emitted C source (limit 1000000)" ([P]: `build/pcrec -p rx --features all -e utf8 -o out.c --pattern '(\p{L})'`) | 4.2-5.9 KB ([N] page3w 4,249; [S] 4,318-5,850) |

The per-character COST in the VM loop is not measured anywhere: [T] is a
membership loop behind an indirect call. It is S4's own acceptance
measurement (§7 b3).

---

## 3. The byte-DFA / hybrid seam

### 3.1 What the DFA's bytes are, and why piece (ii-a) does not shrink them

[P] `\p{L}` under `-e utf8`: the emitted forward table is
`rx_forward_next_state[29900]` and the reverse `rx_reverse_next_state[45300]`
— **299 × 100 and 453 × 100** (states × byte classes), plus per-cell
`is_accepting` arrays of the same length; the artifact ships at
`RX_ENGINE_SEL "size-cap-retry"` (the anchored machine dropped, K53's ladder).

[N] `automaton_k53.tsv`: the **minimal forward automaton of `\p{L}`'s UTF-8
encodings is exactly 299 states**, and the minimal REVERSE one exactly **453**
— the emitted DFAs' own state counts. Subset construction plus minimization
already finds the class's minimal automaton. The table is big because a
byte-level DFA for a wide class needs ~100 byte classes and hundreds of states
at once; no NFA-side restructuring changes the minimal DFA. **So the
prefix/suffix-shared automaton buys COMPILE TIME and nothing else.** Shrinking
the DFA route's artifact is the island's job (§3.4).

### 3.2 Piece (ii-a): splice the class's minimal automaton (CT-6)

K67's class share is the fan-out an epsilon-closure walks when it ENTERS the
class: under `\p{L}+`, every loop-boundary DFA state re-offers every branch
head, and 92% of closure visits take the ~466 ns loop-context memo path
(K67; [OPT-CLOSURE-CTX]). [N] `automaton_k53.tsv`, `\p{L}`:

| NFA fragment for the class | states | class edges | **entered by (closure fan-out)** |
|---|---:|---:|---:|
| today: flat alternation of `u8_box` chains (this lane's transcription) | 2,799 class nodes | — | **827** branch heads |
| minimal forward automaton, set-labelled edges | 299 | 627 | **30** |
| minimal reverse automaton, exact over bytes | 453 | 4,497 | **65** |
| (reversed forward automaton, for contrast; `revfwd_root_fanout` column, added **[r1 MEAS-3]**) | 299 | 627 | 270 |

(The transcription's 2,799 class nodes differ by 3% from K67's instrumented
2,711 forward NFA states; the gap is not explained here, and the fan-out
comparison does not depend on it. Across the K53 twelve the forward fan-out
is 21-32 and the reverse 64-65, against 809-1,118 flat branches.)

**The splice.** The encoding row gains one function: *given a code-point set
and a direction, return the minimal byte automaton of its encodings*. It is
built from the same `u8_box` decomposition that ships today, hash-consed
bottom-up (forward), or built over the reversed member encodings (reverse;
the reversed forward automaton is 4× wider on entry, the table's last row). The
NFA builder expands an `A_WCLASS` into that automaton — one entry state, one
exit, set-labelled class edges. The byte backend's automaton is one class
state, which is exactly what the NFA builds for a byte class today, so the NFA
builder has one code path (DD-12 (7)).

**Its boundary with the siblings, stated so neither is absorbed:**

- **[OPT-CLOSURE-CTX]** makes the loop-context closure path cheap, or
  unnecessary for a loop whose body cannot match empty — for every pattern.
  Its fix (1), if it holds, takes K67's witness "from ~26 s to well under 1 s"
  on its own (plan.md [OPT-CLOSURE-CTX]).
- **[OPT-RETRY-REUSE]** removes the ×3 ladder rebuild (77.49 s → 26.32 s on
  K67's witness), for every pattern that takes the ladder.
- **This piece** divides the per-entry fan-out by 27 (forward) and 13
  (reverse), for wide classes only.

The three multiply. **Decision: S5 is built AFTER [OPT-CLOSURE-CTX], and only
if K67's witness re-measured on that tree still shows the class fan-out as a
material share** (D77). If [OPT-CLOSURE-CTX]'s fix (1) already brings
`\p{L}+` under a second, a 13-27× cut to the remainder is a small absolute
number, and S5's cost — below — may not pay.

**S5's identity question is not byte identity.** A different NFA gives a
different raw DFA; minimization then gives the same minimal machine, but the
emitted state NUMBERING follows raw creation order
(`dfa_online_minimization_study.md` §1, `minimize.c:161`). So S5's gate is
DFA ISOMORPHISM over the corpus + bench (tables equal under a state
permutation), and every artifact whose numbering moves is an `abi`-visible
byte change. How many move is §7 a3's measurement, taken before S5 is
chartered.

### 3.3 The hybrid's prefilter

A VM-hybrid artifact's DFA prefilter is built from the NFA and so reads the
same fragment. At S4 the VM stops reading the byte child; the prefilter keeps
it (and at S5 moves to the minimal automaton with every other NFA reader). No
separate decision.

### 3.4 Piece (ii-b): the island — interface only

A byte-wise DFA cannot run a decode-and-test mid-state; the way a wide class
stops costing hundreds of KB on the DFA route is to leave the DFA for one
character — decode, test with the kit, resume at the class's exit state or
die. That is `ucp_study.md` §D.4's observation: "[CLS-TREE]'s DFA side and
[UCP]'s predicate island need the same splice", and it is [ENG-ISL]'s framing
("islands of VM in DFA", its scan edge being the first instance). **This note
does not design the island.** It fixes the two things the island will need
from here:

1. **The island's test is the kit predicate and the decode entry, unchanged**
   — `len = $_decode(...); ok = len && $_clsN(cp)`. Nothing about the kit is
   VM-specific.
2. **The class is one node until the NFA builder**, so an island-aware
   builder can choose, per `A_WCLASS`, between the S5 automaton and an island
   edge, without re-lowering.

**Trigger (D77):** the island is built when either [UCP]'s design takes its
predicate-island route, or a bench cell measures the DFA route of a wide class
as a cost the VM route (S4) does not fix. Which island lands first builds the
splice and the other reuses it (`ucp_study.md` §F Q5).

---

## 4. Caseless composition (CT-7)

The fold happens at CONSTRUCTION, per contribution, through
`PcrecEnc.fold` (`cls_casefold`; `src/enc/enc.h`'s `fold` field: "byte folds exactly the 52
ASCII letters and MUST NOT fold 0xE9 to 0xC9 ... utf8 folds U+00E9 to
U+00C9"). The class node — `A_CLASS` or `A_WCLASS` — holds the folded set, and
the kit tests it. There is no runtime fold anywhere in a class test; D23
measured a runtime fold indirection at 26% on a pattern with no letters.

This is also why the kit's `CUBES` finds the fold without being told: the
folded set `{S,s}` IS a one-cube set ([S] §4.3). And it is why the one
UCP × caseless trap `ucp_study.md` §B.3 found — `(?i)[[:lower:]]` must NOT
fold under UCP while `(?i)\p{Ll}` must — is a construction-time rule that the
kit cannot break or fix: the kit receives whichever set construction built.
[UCP]'s design owns that rule.

The caseless BACKREFERENCE compare (`$_span_match_caseless`) is not a class
and keeps its runtime fold; it only shares the decoder (§2.2).

---

## 5. What it retires, and what stays (CT-8)

| item | today | after | stage |
|---|---|---|---|
| **K55** — `\P{Unknown}` under `--engine=vm` | refused (689,367 B > 500,000); `tests/axes/run_axes.sh`'s `REFUSAL_PATTERN["--engine=vm"]` entry documents it | compiles; the `--engine=vm` entry is DELETED (the `-fno-size-term` entry with the same substring stays — K45's witness). A refusal-set move is an identity break (`opt_dial_design.md` §6.2) and is recorded as one | S4 |
| captured wide classes (`(\p{L})`, `(\p{Xwd})`, any `(\w)` under a future UCP) | refused (§2.3) | compile on the VM | S4 |
| `vm_cls_shape` + `-fno-cls-fold` + `RX_VM_CLS_FOLDS` | the ASCII-pair fold classifier (4 of the corpus's 8 one-cube classes) | retired into the kit's `CUBES` (all 8) — Frank ruled it subsumed 2026-09-11; the flag's fate is Q2 | S2 |
| [OPT-CLSPACK] (N byte classes' 32N bytes of bitmaps) | not started | **proposed CLOSE as answered**: the kit's byte tier emits zero `.rodata` for all 41 corpus classes ([S] §4.4); nothing is left to pack. Re-opens if [UTF-RW] brings table-bearing byte classes | S2 |
| [FORM-CHAR2] (i)/(ii) | chartered as calibration inputs | stay calibration inputs (§7 b2); no standalone ruling (Frank, 2026-09-11) | S0/S2 |
| K67 — the class's share | 827-branch fan-out per closure entry | 30 / 65 | S5, gated |
| **K53 known_fail rows** | **already gone**: [K53-SELRETRY] moved the 16 blocks back into `tests/utf8/` on 2026-09-10 (known_fail/CLAUDE.md) | nothing further to retire | — |
| **[K53-SELRETRY]** (the drop ladder) | the DFA route of `\p{L}` etc. ships at `size-cap-retry` | **STAYS.** S1-S5 do not shrink the DFA route (§3.1); only the island does. It is also selection-layer correctness independent of classes (its population is 8 altwide literal alternations, K53 entry) | — |
| the size caps themselves | — | unchanged | — |

---

## 6. Staging (CT-9)

Each stage is one lane, merges alone, and states its abi event. "Identity"
below means the house gates (the four `.c` byte-identity gates, the recursion
identity gate's two pins, `run_ir_listing.sh`'s `irsb` arm — coding_guide.md
§3.1-3.3), **with readers of the abi number found by grep at the time**
(D94) — never from this list.

| stage | what | answer checks | identity / abi | sabotage rows (numbered from main's highest S-id at the time) |
|---|---|---|---|---|
| **S0** | measure: §7 a1-a3 (Mac) and b1 (ubuntubudu); fit CT-2's per-probe model; re-propose the five λ constants as ONE ruled diff | — | none | — |
| **S1** | the kit in `src/`: DP + forms + C emitter + the whole-set candidates; **no emitter calls it yet** | a new `tests/clskit/` differential: every set of the 312 `uprops` + the 41 byte classes + the proptest compositions, the EMITTED C compiled and compared to a reference on all 1,114,112 code points (the study's own shape, now against `src/`); a C-vs-study cross-check of sectionings (the study's `crosscheck.py` found two bugs this way, [S] §8) | no artifact moves; no abi | a leaf off by one at a section seam; `cube_of` accepting a non-cube; a whole-set page table with one leaf dedup collision — each must be DETECTED by the differential |
| **S2** | the byte tier on the VM: `vm_cls_test`'s bitmap/range/fold shapes replaced by the kit's byte forms; `vm_cls_shape` retired; the scan edge's axis-I class bodies re-pointed at the same emitter **as a separate commit/abi event** (DFA artifacts move) | whole-corpus answer identity default vs the kit-deny axis (Q2) in `make test-axes`; PC-4 live oracle; `tests/base/cls_fold.rxt`'s 58 cells | **abi bump** (every VM artifact with a class site moves; 319 sites / 41 sets in the corpus); the recursion gate's FOLD deny-axis IFF and `FOLD_PATTERNS` manifest re-pinned; form-census floors re-measured | the kit's byte form widened by one byte (the unsound direction — S228's shape for the fold) |
| **S3** | `A_WCLASS` + every reader walking the byte child | — | **BYTE-IDENTICAL over the corpus + bench, every encoding × features triple** ([K53-SELRETRY]'s 3,348/3,348 method); no abi | a reader that walks the SET instead of the child (the r54 E1 shape) must fail loudly, not miscompile |
| **S4** | VM decode + kit for `A_WCLASS`; `PCREC_ENCE_DECODE`; `SPAN_CASELESS` onto it; λ read from `--tune`; K55's axes entry deleted | `tests/utf8/`'s `\p` corpora ([STORE] 387/387, PC-4) under `--engine=vm` AND default; a new ill-formed matrix: every class kind × {truncated, overlong, surrogate, >U+10FFFF, stray continuation} × both engines, expected "no match" — the DFA's answer is the oracle and must agree; `make test-axes` over all five `--tune` positions (answer identity) | **abi bump** (VM artifacts with wide classes; `SPAN_CASELESS` artifacts' text); the refusal set shrinks — recorded as the identity break it is | `$_decode` accepting an overlong 2-byte form (`C0 80`); accepting a surrogate (`ED A0 80`); the depth-1 test mis-routing an ASCII class to decode (answer-neutral — must be caught by a structural codegen check, not by answers) |
| **S5** | minimal-automaton splice, **gated** (§3.2) | as S4, both engines | **DFA isomorphism** over corpus + bench (not byte identity); abi bump iff any artifact's numbering moves (§7 a3 says how many) | the automaton builder dropping one box; merging two states whose suffix sets differ |

**The ritual's price, stated once.** S2, S4 and (probably) S5 are abi events:
bump `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c:51`), the change log in
`docs/spec/match_api.md` §6, every reader found by grep, `make test-codegen`,
then registry + codegen + rxtsource suites (the D94 addendum's "suites that
count"). S2 also moves `docs/spec/tuning.md` §2.22 and `match_api.md` §6.3
(the fold stamp and flag), and S4 moves `tuning.md`'s λ row from
"reservation" to its pinned cells, `limits.md` if any refusal text changes,
and the encoding-seam spec for the new entry — all D80, in the same change.
Pre-1.0, these are deliberate and permitted (memory
`pcrec-abi-changes-pre-release`).

### 6.1 S4 build plan (lane s4build, 2026-09-29)

Written before the build, from `lane/land3` (U2 + S3 + K67, abi 46). It
states what S4 builds and which rulings it reads. It is not a new design.

**The instruction (§2.2, as ruled).** At `vm_emit_node`'s `A_WCLASS` arm, on
the kit route, the VM emits one test for the whole class:

```c
if (scan_position < subject_length
    && (len_ = <p>_decode(subject, subject_length, scan_position, &cp_)) != 0
    && <p>_wclsN(cp_)) { scan_position += len_; goto next; }
goto fail;
```

`<p>_wclsN` is `pcrec_clskit_emit_kit`/`_emit_whole`'s `static inline` matcher.
There is one per DISTINCT set per artifact, interned the way `vm_cls` interns
byte bitmaps, and emitted beside the class bitmaps ahead of the program. Its
form is `pcrec_clskit_select` at `cx->opt->tune`, which is D131's ruled
first-match table read unchanged. `vm_cost` and `vm_count_slots` answer the
kit route as they answer `A_CLASS` (no frame, slot or trail). `vm_emit`
already charges the wrapper one node (D-4). The listing gains one event,
`VE_WCLASS`, whose row names the set, the form and the row that chose it.

**The decode seam (§2.2).**
- `PCREC_ENCE_DECODE` is a new entry: `engine_callable`, and a row in
  `entries_utf8[]` only. The byte backend has no row, and a backend with no row
  keeps the byte child (`pcrec_enc_has_entry`, the `VAR_VALID` precedent). So
  the kit route needs no encoding test.
- Its body is stage 4's `$_span_ci_decode`, verbatim, renamed `$_decode`. It
  rejects exactly the automaton's ill-formed set: truncated, stray
  continuation, overlong, surrogate, and anything above U+10FFFF.
- `SPAN_CASELESS`'s private copy retires into the entry. Its utf8 body calls
  `$_decode`.
- **Two seam columns, both recorded as D58 events:**
  - `requires`: a mask of entries this entry's body calls. The utf8
    `SPAN_CASELESS` row requires `DECODE`. Both emit functions close the mask
    over it. `varmvp` built this column and deleted it for want of a customer
    (D77). This is the customer.
  - `inline_def`: the definition is `static inline`, has no declaration (so
    nothing reaches the public `.h`), and is emitted ahead of the engine
    bodies rather than in the epilogue. §2.2 says why an exported decoder
    would not inline under `-fPIC`.
- The epilogue emits the non-inline entries. `vm_emit_search_body` emits the
  inline ones before the class tables.

**Which `A_WCLASS` sites switch to the kit.** The rule is a RULE, not a
list: an `A_WCLASS` that reaches `vm_emit_node` takes the kit, unless
`-fno-cls-kit` is given or the backend has no `DECODE` row. Every site that
consumes the node's BYTE CHILD before `vm_emit_node` sees it keeps doing
that, unchanged:

| site | route | why |
|---|---|---|
| forward class test (`vm_emit_node`), incl. inside star / opt-chain / counter / possessive loops, lookbehind bodies, atomic bodies, call regions | **kit** | the loop rungs emit the body through `vm_emit`, so the loop's per-iteration test becomes the kit test |
| literal run (`pcrec_lit_run`, S2a/F5) | byte child | a run of ≥ 3 known bytes is one `memcmp`; decoding it would be slower |
| alternation island (`vm_isl_words`) | byte child | a literal trie over bytes, e.g. `café\|naïve` |
| cursor rung (`vm_det_seq`, `vm_cap_offsets`) | byte child | a deterministic fixed-stride child (`(é)+`, `é{3}`) keeps its stride scan; a child with a choice point (`\p{L}`) has no stride and falls to the frames rung, whose body is the kit test |
| revdet backward walk | never reached | loud (`pcrec_wcls_misplaced`), as at S3 |
| NFA builder, DFA, VM hybrid prefilter, anchored machine | byte child | §3.3 and D129 Q4: the DFA side changes only with the [UCP] island |

**The selection rows (D131, D131 addendum 1).** `ClsSelectIn.tune` is
`cx->opt->tune`. `ClsSelectIn.deny` is 0: no row deny is mapped to a public
flag. Answer identity ACROSS forms is what `tests/clskit/`'s exhaustive
differential proves. Answer identity across positions is `make test-axes`
over the five `--tune` positions. Answer identity kit-vs-no-kit is
`-fno-cls-kit`.

Consequence: **`+2` stops being identical to `+1`** where `0` chose `P3`.
`tune.c`'s "declared vacuous" comment and `tuning.md`'s `+2` note name that
become-reachable condition ("the day λ is implemented"). Both change in the
same commit, and so does `run_tune_dial.sh` §3c's `+2 == +1` assertion.

**`-fno-cls-kit` (D129 Q2's deny, first built here).**
- It means "every `A_WCLASS` on the VM emits its byte child", i.e. today's
  forms.
- It gets a `PCREC_BIT`, an `axes.def` row, a `--list-axes` row, a
  `tuning.md` §2 entry, and joins `rx_info.flags`' strategy-denial mask.
- S2 later widens its meaning to the byte tier. `-fno-cls-fold` stays until
  S2 (it governs `A_CLASS`, which S4 does not touch).

**The activity stamp.** `<PREFIX>_VM_CLS_KIT` is the number of distinct kit
matchers the artifact emits. It is a D81 VM-only activity count.

**cwmax / cwmin — the D-2 ruling.** `A_WCLASS` answers **1 CHARACTER** in both
`pcrec_cwmax` and `pcrec_cwmin`, the same as `A_CLASS`: a class is one
character by definition. The byte child's answer (its encoded length) was a
unit error kept at S3 for byte identity. Measured, it moves nothing:
- Every reader that runs after `pcrec_lower_enc` (where the kind exists) asks
  only zero-vs-nonzero. That is `startanch.c`'s `== 0` and `endwin.c`'s
  `!= 0`.
- The one reader that uses the value, `endwin.c`'s window, declines under any
  multi-byte encoding first (`e->start_cls`).
- `mod_lookaround.c` and `callgraph.c` run before the lowering, so they never
  see the kind.

`pcrec_minw` (a BYTE width, the MRL prune's unit) keeps walking the child,
because the child's minimum encoded length is exactly the bytes a kit test
consumes at least.

**What this retires, and what it does not.**
- **K55** stops refusing. `\P{Unknown}` under `--engine=vm` compiles, and
  `run_axes.sh`'s `REFUSAL_PATTERN["--engine=vm"]` entry is deleted. Every
  wide class under `--engine=vm` (the K53 twelve) stops refusing on code
  bytes.
- Captured wide classes (`(\p{L})`, `(\p{Xwd})`) stop refusing as far as the
  VM PROGRAM is concerned. Whether the default route's hybrid then fits
  depends on its byte PREFILTER, which S4 does not shrink (§3.3). That
  population is MEASURED at build and reported. It is not assumed.
- The refusal set shrinks. That is recorded as the identity break it is
  (`opt_dial_design.md` §6.2), with the population listed by pattern.
- **Not retired here:**
  - [UCP] U1's by-name refusals of wide UCP sets and UCP `\b` under utf8.
    Lifting those is U4's (`ucp_design.md` §6, D130 item 3).
  - [K53-SELRETRY]'s drop ladder, which the DFA route keeps (§5).

**abi.** This is one abi event, 46 → 47 at this lane's base; the manager
serializes the number at merge. VM artifacts with a wide class move, and so do
utf8 caseless-backreference artifacts (the decoder's name and placement). The
D76/D94 ritual applies, with readers found by grep.



### (a) The Mac can do these (box-independent: counts, bytes, answers)

- **a1. `page3w`/`page2w` over all 312 sets** — DONE by this lane
  (`results/whole_uprops.tsv`: 312 sets exhaustive, 0 mismatches; totals in
  §1.3). **DONE, lane clss0 (S0)**: the same for the 41 byte classes
  (`results/whole_byteclasses.tsv`, 0/41 mismatches; `compare_whole_kit.py`
  → `results/whole_vs_kit_byteclasses.tsv`). CONFIRMED, not merely expected:
  WHOLE-WINS=0 / TIE=13 / kit-wins=28 against the size-minimal kit answer —
  no byte class in the corpus population has a whole-set object strictly
  smaller than the kit's own answer, so a byte-tier whole-set DP candidate
  would win nothing on size there.
- **a2. The `A_CLASS` reader census, classified**: for each of the 49 arms and
  6 comparisons, "reads bytes / reads the set / structural only" — and for
  every "reads bytes" site, what `A_WCLASS` must answer (width, count,
  first-unit set), spelled out before S3 merges: `-Wswitch` forces every site
  to be TOUCHED, not to be RIGHT **[r1 SEM-1]**. **RE-HOMED: this is S3's
  first act, not an S0 measurement** (staging table, §6) — it sizes S3/S4 and
  needs `A_WCLASS` to already exist as a target to classify readers against,
  which S0 has no reason to build. Dropped from this list so S0's owed count
  reads honestly against what S0 actually charters.
- **a3. S5's renumbering population** — **WITHDRAWN (D129 Q4): S5 (the
  minimal-automaton splice) is DROPPED.** Frank: "why use a DFA to do a
  lookup? what about binary search?" — the splice shrinks no artifact (the
  emitted DFAs are already minimal, 299/453 states) and buys compile time
  only; the island ([UCP]'s mechanism) is what shrinks the DFA route and
  removes the class's K67 share. No renumbering population is ever needed.
- **a4. After [OPT-CLOSURE-CTX] lands: K67's witness re-timed** — compile
  time is a single-process CPU measurement and the Mac's direction is honest
  for a 77 s vs 1 s question; the citable number runs on ubuntubudu with b1.
  (No longer gated on S5's abi question, per D129 Q4 above — [OPT-CLOSURE-CTX]
  is its only remaining trigger.)
- **a5. The [FORM-CHAR2] (i) asm-counting half** — **DONE, lane clss0 (S0)**:
  per-site instruction counts (`gcc -O2 -S`, `results/asm_count_byteclasses.tsv`,
  `asm_count.py`), extended from the one hand-picked fold-vs-bitmap witness to
  every kit byte form the emitter can build (`ALL`/`RANGES`/`CUBES`/`MASK64`)
  vs `BITMAP` (today's shape), over all 41 corpus byte classes. Mean
  instruction counts (arm64/Mach-O, this run — instruction COUNTS are the
  portable comparison, not mnemonic text): `MASK64` 7.40 (n=15, never a
  branch), `RANGES` 9.12 (n=41), `CUBES` 11.63 (n=19, up to 23 on a 4-cube
  cover), `BITMAP` 12.37 (n=41, always one load). `ALL` fits no class in this
  population (no byte class is a single contiguous run).

### (b) The timing arm — ubuntubudu only, relayed to the pcrecdev2 executor

**b1, the CLSPACK arm and the isolated `^C` re-run are DONE** (pcrec-bench
`scratch/clstree-s0` `81f0982` + `d6e0106`, O-76; read in §1.7). **One
re-run is OWED**, about a minute of box time: the CLSPACK arm with every
arm on the same dispatch shape (§1.7.3 reading 2),
`CC=gcc gnutimeout 600 python3 studies/cls_tree_study/bench_bytes.py
--ns 4,16,32 --lam 16 --rounds 11 --dispatch switch --out
bench2_bytes_switch.tsv` (expected 132 data rows; its header line names
`dispatch=switch`). The brief below is the record of what ran.

**b1 is ready to run today, and lane clss0 (S0) adds two more items that ride
the SAME executor session: the [OPT-CLSPACK] timing arm (D129 item 5,
`bench_bytes.py`/`make bench2-bytes`) and the isolated `^C`/member re-run
[r1 MEAS-2] asked for.** Below is the exact-command brief, for the manager to
relay verbatim — the pcrecdev2 executor is sonnet and does nothing
judgment-shaped, so every command is copy-paste exact and assumes an
extracted `git archive` copy of pcrec at the commit the manager names.

**FIXED 2026-09-29 (lane clsgate), after this brief's first two runs both
returned REFUSED** (pcrec-bench branch `scratch/clstree-s0`, `0d7392c`:
attempt 1 REFUSING mid-run at load1 0.61 after 3 of 12 sets, attempt 2 at
load1 0.52 after 10 of 12 sets, the SECOND attempt with nothing else of ours
running on the box). Diagnosis: the harness's own gate was tripping on the
harness's own work — `bench2` compiles a fresh binary per set (bitmap +
three kit policies + the wholeset `page2w`/`page3w` arms) and then runs it
once per regime, back to back with no idle gap, and the old gate checked
load1 only once per SET. A 1-minute load average is an exponential moving
average with a ~1-minute time constant; sustained single-core CPU work with
no cooldown drives it toward 1.0 regardless of anything else on the box —
attempt 2's own trajectory (pre-wait 0.07 → refusal at 0.52 after 10 sets,
nothing else running) is exactly that curve, not external contention. Fixed
in `studies/cls_tree_study/loadgate.py` (`wait_for_quiet`, shared by
`bench.py` and `bench_bytes.py`): the 0.5 threshold is UNCHANGED, but a
build phase now compiles every arm for every unit before any timing starts,
and the gate is checked immediately before EACH timed unit (one
set×regime run, not one whole set) and POLLS for quiet — logging every
reading — for up to `--max-load-wait` seconds (default 600 = 10 min)
before refusing. A self-inflicted reading decays within a poll cycle or two
once the harness is idle waiting on the gate; only genuine, sustained
external contention reaches the bound, and that case still refuses with its
load readings, same as before. See `loadgate.py`'s header for the full
diagnosis and `docs/dev/lanes/clsgate_report.md` for the fix's own
correctness smoke (Mac, `--max-load 99`).

Also fixed at the same time: the executor's pcrec copy is a `git archive`
extraction, not a worktree checkout — confirmed by pcrecdev1 (O-73) that no
`~/pcrec` worktree exists on that box, and the pin is recorded from the
archive command itself, never from a `git log` run inside the extracted
tree (which has no `.git`).

> **pcrecdev2 — [CLS-TREE] S0 timing session (read-only study run; writes
> ONLY `studies/cls_tree_study/results/bench2.tsv`,
> `studies/cls_tree_study/results/bench2_bytes.tsv`,
> `studies/cls_tree_study/results/capC_isolated.tsv`, and
> `studies/cls_tree_study/build/`).**
> Box: ubuntubudu. The harness polls for a quiet box before each timed unit
> (up to 10 minutes) rather than refusing instantly; a bound-exceeded
> refusal is still a result — report it with its load readings, do not
> loosen `--max-load`. Tree: pcrec at `<COMMIT the manager names>` (at or
> after the merge of `lane/clsgate`; nothing in `src/` is read for b1/the
> isolated re-run — the study reads `src/parse/uprops_tables.inc` and its own
> committed `results/byteclasses.tsv` only. `bench2-bytes` needs no
> `build/pcrec` either — same committed-input rule).
> ```
> mkdir -p /var/tmp/clstree_s0/pcrec
> git -C ~/pcrec archive <COMMIT> | tar -x -C /var/tmp/clstree_s0/pcrec
> echo "pin: <COMMIT>"                                     # record the pin from THIS command, not git log
> cd /var/tmp/clstree_s0/pcrec
> gcc --version | head -1                                 # record the compiler
> mkdir -p build/clstree_s0
>
> # --- b1: kit/whole-set ns/char, the committed 2026-09-11 arm set + whole-set tables ---
> gnutimeout 7200 make -C studies/cls_tree_study bench2 CC=gcc \
>     > build/clstree_s0/b1_bench2.log 2>&1
> tail -5 build/clstree_s0/b1_bench2.log
> wc -l studies/cls_tree_study/results/bench2.tsv
> head -1 studies/cls_tree_study/results/bench2.tsv        # load1_at_start
>
> # --- CLSPACK: N=4/16/32 live byte-class sites, bitmap vs kit vs shared atom table ---
> gnutimeout 1800 make -C studies/cls_tree_study bench2-bytes CC=gcc \
>     > build/clstree_s0/clspack_bench2_bytes.log 2>&1
> tail -5 build/clstree_s0/clspack_bench2_bytes.log
> wc -l studies/cls_tree_study/results/bench2_bytes.tsv
> head -1 studies/cls_tree_study/results/bench2_bytes.tsv  # load1_at_start
>
> # --- isolated ^C/member re-run [r1 MEAS-2]: the one bimodal cell, alone, more rounds ---
> CC=gcc gnutimeout 600 python3 studies/cls_tree_study/bench.py \
>     --population k53 --sets '^C' --regimes member --lams 0,16,256 \
>     --rounds 41 --out capC_isolated.tsv \
>     > build/clstree_s0/measc_isolated.log 2>&1
> tail -5 build/clstree_s0/measc_isolated.log
> wc -l studies/cls_tree_study/results/capC_isolated.tsv
>
> echo "CLS-TREE-S0-TIMING DONE"
> ```
> Expected row counts (fewer only if a build/run fails — a `BUILD FAIL` or
> `RUN FAIL` line is a finding, report it verbatim; any `ANSWER MISMATCH` line
> aborts that command's run and is a finding):
>   - `bench2.tsv`: 4,620 data rows (12 sets × 5 regimes × 7 arms × 11 rounds).
>   - `bench2_bytes.tsv`: 132 data rows (3 N values {4,16,32} × 4 arms
>     {refbs,bitmap,kit,atom} × 11 rounds); also report the `n_atoms` column's
>     three values (expect small integers well under 64 — a refusal naming
>     ">64 atoms" is itself the finding, not a crash).
>   - `capC_isolated.tsv`: 205 data rows (1 set × 1 regime × 5 arms {refbs,
>     bitmap1, lam0, lam16, lam256} × 41 rounds).
> The `CLS-TREE-S0-TIMING DONE` line is the done-trailer — its absence means
> the session did not reach the end (report whichever log's `tail` is last).
> Return all three TSVs (commit on a scratch branch or scp back) plus the
> `build/clstree_s0/*.log` files, the recorded pin/compiler, and the three
> `load1_at_start` readings. Wall time: b1 is dominated by 60 set×regime runs
> of 7 arms × 11 rounds × 1 M probes (the 2026-09-11 run of 5 arms × 4
> regimes fitted inside the I-65 session); `bench2-bytes` is 3 builds × 11
> rounds × 4 arms × 2^20 probes, small (well under b1's); the isolated
> re-run is 1 build × 41 rounds × 5 arms × 2^20 probes, also small. **Expected
> wall time, gate-quiet case**: a few minutes total — Mac gcc-16 measured
> ~0.25 s/set to build every arm (including the wholeset ones) and ~2.2 s/set
> to run all five regimes, so twelve sets is on the order of 30 s of real
> compute even before any ubuntubudu-vs-Mac speed difference; the fixed
> gate's own overhead when the box is already quiet is one `os.getloadavg()`
> call per timed unit, not a sleep. The two added commands' own timeouts
> (1800 s, 600 s) and b1's 7200 s stay generous relative to that, covering
> both a slower box and the gate's bounded wait (up to 10 min per timed unit,
> reached only under genuine external contention — in which case the
> `gnutimeout` firing first and the gate's own bounded refusal are both
> legitimate outcomes to report, not harness failures).

What b1 answers: `page3w`/`page2w` vs `bitmap1` vs the kit's three policies,
under the four old regimes and the new `runs` regime (text-like runs of 1-32
code points within one 256-code-point block). That is CT-2's calibration data
and CT-3's re-proposal input. What the CLSPACK arm answers: D129 item 5 —
whether the shared atom table's measured .text/.rodata win at N=16
(`studies/form_char_twins`, STEP 0) also holds ns/call against both the kit's
own inline tests and today's bit array, at N=4/16/32. What the isolated
re-run answers: whether `^C`'s bimodal member-subject timing (`bitmap1` 1.60
vs 13.30 ns in the 2026-09-11 run, in lockstep across every arm — an
environmental effect, not arm behaviour, [r1 MEAS-2]) recurs under the same
harness on a fresh session, at 4x the round count.

**b2. The byte tier, in the VM loop** — after S2 lands, through pcrec-bench,
not the study harness: the ci-256 witness and the csv/loglines class-heavy
cells at the S2 pin vs its parent, forced-VM and auto. This is [FORM-CHAR2]'s
timing half and the bench's abi-23 AFTER precedent (plan.md [FORM-CHAR2]).
It rides a bench window (memory `pcrec-bench-status`), relayed as an inbox
item when S2 merges.

**b3. The code-point tier, in the VM loop** — after S4 lands: the bench's
utf8 subbench cells that use `\p{...}` or would under UCP, forced-VM vs auto
at S4's pin, plus K55's `\P{Unknown}` (newly buildable, so a first sample, not
a comparison). This is where the membership-loop numbers of b1 meet the
decode and the VM's own loop; nothing in this note licenses an end-to-end
claim before it.

---

## 8. Questions for Frank, each with a recommendation

**Q1. Re-propose the five λ constants after S0's calibration, as one ruled
diff — and until then, is the λ row still "reservation"?**
*Recommend YES to both.* The pinned 4/16/16/64/256 select among matchers the
timing cannot tell apart ([T]: 17/36 on member subjects, §1.2), because the
term they price is a code-size proxy. Keeping them would ship a dial whose
speed positions buy bytes. D103 says a recalibration is "evidence for a NEW
proposal ... re-ratified as its own diff", which is this.

**Q2. `-fno-cls-fold` at S2: retire it, or keep it as the deny flag for the
`CUBES` member?** *Recommend: retire it, and add ONE kit-level deny
(`-fno-cls-kit`) whose meaning is "emit today's class forms".* The fold is one
cube among the kit's forms; a per-member deny set would grow with the kit, and
the axis `make test-axes` needs is kit-vs-no-kit (the answer-identity
control). Pre-1.0 flag removal is a spec change, not a compatibility break
(`pcrec-abi-changes-pre-release`). `RX_VM_CLS_FOLDS` is replaced by one
activity stamp the implementer names (a count of kit-emitted class sites,
D81's VM-only activity family).

**Q3. The +2 position: is "the same DP at a high λ, with whole-set tables as
candidates" the right reading of the 2026-09-16 direction?** *Recommend YES.*
It delivers the huge-bitmap forms at +2 (3.8× faster than the kit's middle,
5.9-32× its bytes, still smaller than today's DFA tables; §1.4) without a
+2-only mechanism, and if `page3w` times near `bitmap1`, +2 then honestly
costs almost nothing extra and the note will say so rather than invent a
difference.

**Q4. S5 (the minimal-automaton splice) gated behind [OPT-CLOSURE-CTX] and a
K67 re-measure — or built with the rest, per "hit everything class related
at the same time"?** *Recommend GATED.* The splice cuts closure fan-out 13-27×
but does not shrink any artifact (§3.1), its gate is isomorphism rather than
byte identity, and [OPT-CLOSURE-CTX] may make its target small first. The
DESIGN is done together (this note); only the BUILD waits on its measurement
(D77).

**Q5. Close [OPT-CLSPACK] as answered by the kit's byte tier?** *Recommend
YES.* Its premise is 32N bytes of per-class bitmaps; the kit emits zero
`.rodata` for every class in the corpus ([S] §4.4). A table-bearing byte class
from [UTF-RW] would re-open it with a population.

**Q6. The island ([ENG-ISL]/[UCP]) — confirm it is out of this row's staging,
with only its interface fixed here.** *Recommend YES.* It is the one piece
that shrinks the DFA route, and it is also UCP's `\b` mechanism; designing it
twice, once per customer, is the parallel-mechanism shape the general-
mechanisms rule forbids. Its trigger is in §3.4.

**Q7. Order against [UCP].** *Recommend S0 → S1 → S3 → S4 before S2,* if UCP
is the next customer: S4 is what makes `\p{Xwd}`-sized classes buildable on
the VM (UCP's hard prerequisite, `ucp_study.md` §E), and S2's byte tier is
independent and can follow. If UCP is not scheduled, S2 first is the smaller,
corpus-wide change.

---

## 9. What [UCP] can build on

In `ucp_study.md` §F's terms:

- **Option (b), partial UCP** (`\d`→`\p{Nd}`, `\s`→`\p{Xsp}`, small POSIX)
  needs nothing from here: those sets are affordable today (3-19 KB DFA,
  `ucp_study.md` §E).
- **Option (c)'s VM half** — `\w`, `[:alpha:]`, `[:alnum:]` as `\p{Xwd}`-,
  `\p{L}`-, `\p{Xan}`-sized sets, and every CAPTURED form of them — is
  unbuildable today and **buildable at S4**: one kit matcher per distinct set,
  for `\p{Xwd}` 5.5 KB as a whole-set three-stage table ([N]) or 4.9-6.9 KB
  across the kit's policies ([S]), behind `$_decode`.
- **Option (c)'s `\b`** needs a word test on the character BEFORE and AFTER a
  position. S4 supplies both halves' parts — `$_decode` forward, `back_step`
  + `$_decode` backward, and the kit predicate for `\p{Xwd}` — but not the
  DFA-side mechanism (the predicate island, `ucp_study.md` §D.2), which is the
  §3.4 island and is triggered by UCP's own design.
- **The `[:lower:]` caseless trap** (§4) is construction-time and UCP's; the
  kit neither helps nor hurts.
- **Status of the `\b` parts [r1 SEM-2]**: `back_step(k=1)` is verified to
  return the start of the character ending at `pos` (enc_utf8.c), but the
  COMPOSITION `back_step + decode + kit` against PCRE2's UCP `\b` is asserted
  here, not measured; UCP's design owes that differential.
- **What UCP must not assume**: that the DFA route's `\w` becomes small. It
  does not until the island (§3.1).

---

## Appendix A. Reproduction

All in `studies/cls_tree_study/` (its `README.md` and `CLAUDE.md`):

| number | command | output |
|---|---|---|
| §1.2's table | `python3 timefit.py` | `results/timefit_20260928.txt` |
| §1.3's whole-set columns (K53) | `CC=gcc-16 python3 verify_whole.py k53` | `results/whole_k53.tsv` |
| a1 (312 sets) | `CC=gcc-16 python3 verify_whole.py uprops` | `results/whole_uprops.tsv` |
| §3's automaton sizes | `python3 automaton.py k53 --exact-rev` | `results/automaton_k53.tsv` |
| b1 | `make bench2 CC=gcc` (ubuntubudu only) | `results/bench2.tsv` |

The Mac smoke of `bench2`'s generator (3 sets × 3 regimes, `--max-load 99`,
1 round, output discarded) confirmed that every new arm's hit count and
positional checksum equal the reference arm's in every cell; its times were
not read.

### §1.7 addendum — the fair-dispatch CLSPACK re-run (I-121 / bench O-77, 2026-09-29; manager)

`results/bench2_bytes_switch_ubuntubudu_20260929.tsv` (132/132 rows, `--dispatch switch`, pcrec cdd8607d). Medians are in ns/call, over 11 rounds each.

| N live sites | bitmap | atom | kit (λ16) | refbs |
|---|---:|---:|---:|---:|
| 4 | 7.59 | 7.61 | 8.57 | 12.33 |
| 16 | 10.66 | 9.64 | 12.38 | 16.55 |
| 32 | 10.96 | 11.38 | 12.99 | 18.55 |

With the dispatch confound removed, **the kit's byte tier is the SLOWEST of the three table-free/table forms at every N**: +13% / +16% / +19% against the bitmap. The instruction-count win (§7 a5) does not become a time win. The atom table and the bitmap are within noise of each other; N=16's spread is max/min ≈ 1.26 on both. The atom table is smaller than per-site bitmaps from N ≈ 11. Consequences, owed to Frank as rulings:
1. **S2** (the byte tier on the VM) as designed, which replaces bitmaps with kit forms by default, would be a measured SPEED REGRESSION. The kit's byte forms belong at the size-leaning `--tune` positions only.
2. **[OPT-CLSPACK]**'s condition "default only if atom ≤ kit" is met at every N. Against the bitmap, the atom table is a size win at no measured time cost for N ≥ ~11. That makes it a candidate for the byte tier's default table form above that N.
