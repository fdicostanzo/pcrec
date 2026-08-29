# r40 — D6 critic panel on the [ART-SIZE] STEP 2 DESIGN NOTE (docs/design/artifact_size_term.md at lane/artsize3 abb2a1f), before any code

Three read-only critics, no make: critic-arch (sonnet; mechanism fit +
process obligations — REPORTED), critic-model (sonnet; the size model,
the gcc curve, the threshold gap, the lever pricing, the pinned
populations — pending), critic-sem (opus; identity of K, the cap on the
auto path, the non-deniable cap, the stamps — pending). Panel opened
2026-08-28 ~22:5x EDT, forty-fourth session. The lane is HELD; the code
phase opens on the panel's dispositions.

## critic-arch — findings and triage

| # | severity | finding | disposition |
|---|---|---|---|
| AR1 | MISSING-OBLIGATION | D80 spec-hunk list incomplete: `docs/spec/cli.md:218-224` hand-enumerates every `-fno-` axis through `-fno-offset-skip`; the note names only tuning.md, limits.md, match_api.md §6 | ACCEPTED → landing bar: `-fno-size-term` added there in the same change |
| AR2 | MISSING-OBLIGATION | the two new macros (`_UNROLL_K` / `_UNROLL_K_WHY`, §7.1) have no home in match_api.md §6.3's per-mechanism bullets (`match_api.md:1659-1720`, where `_DFA_SCAN`/`_DFA_PREFILTER` live) | ACCEPTED → landing bar: a §6.3 bullet on the `_DFA_SCAN` precedent, VM-artifact-scoped |
| AR3 | GAP | §6.2's K sweep is a hand-written one-off; `--unroll` is a VALUE axis and [CHK-2] (c) "test-axes-from-dump" is NOT built — this note is the consumer (c) waits for and does not say so; `axes_dump.c` has no kind=value support | ACCEPTED → the note states it: the K-sweep check ships now as the gate; `--unroll` is registered as a value axis when [CHK-2] (c) is built, and this row is its named trigger (D77) |
| AR4 | GAP | the note never states what K selection does to [ART-SIZE.1b]'s tripwire (MAX 1,400,000 B / 8.0 s) and size log | ACCEPTED → one sentence + the post-change `size_diff` as a delivery number: headroom grows, pin unaffected |
| AR5 | HOLDS | the brief's worry that a lone deny flag breaks the registry's shape is wrong: 12 of 13 predicate bits are deny-only (tuning.md §2.6-§2.9, §2.12-§2.14); only the prefilter pair (bits 8/9) is deny+force | no action; bit 17 deny-only is the norm |
| AR6 | HOLDS | abi 9→10 four sites verified live (`run_codegen_tests.sh:2683` ABI_EXPECT=9; `match_api.md:159,1521`; FILEPIN in run_recursion_identity.sh) | no action |
| AR7 | HOLDS | §6.2/§9 scope the control correctly: `.o` byte-identical, source differs by exactly the two stamp lines (r39 A1 internalised) | no action |
| AR8 | HOLDS | K selection is a genuine SELECTION over N(K) — argmin over a ladder, D82's candidate-list shape — ahead of [ENG-FORM] reaching VM axes | no action |
| AR9 (Q2/Q4) | RULING | D45 is explicitly compile-budget-scoped; the two-mechanism split is the correct reading of it; Q4 (`a{1,25000}`-shaped shipped size) is real but outside the row's mandate as chartered | to Frank (surfaced 22:5x); a shipped-size instrument would be a new row, not this note's gap |
| AR10 (Q3) | ESCALATE | the 131,072 collision is STRONGER than the note says: `limits.h:172,240` — `PCREC_MAX_VM_REPLICATION_PRODUCT` is a literal ALIAS of `PCREC_MAX_VM_NODES = 131072` | ACCEPTED → take the note's own costless fix: threshold 120,000 (same tail gap) |
| AR11 | NIT | §7.2 cites tuning.md §2.13 as the deny-only precedent; §2.14 (`-fno-offset-skip`, bit 16) is the closer one | ACCEPTED |
| AR12 | HOLDS | refusal via `ctx_fail(v->cx, 0, …)` joins the existing "pattern too large" family (`compile.c:14`: the 2nd param is a source pos, every existing site passes 0); D26 discharged | no action |
| AR13 | N/A | `docs/guide/` does not exist ([GUIDE-1] not started) | nothing owed |

## critic-model — findings and triage

Reproduced from the note's archived data (`docs/design/artsize_impl/
{corpus_sizes,ksweep,gccfit}.tsv`) and the lane's scratch, and RAN the
built compiler on both K41 fuzz-gate witnesses. Scripts in the session
scratchpad `r40-model/`.

| # | severity | finding | disposition |
|---|---|---|---|
| F1 | **REFUTED-CLAIM — changes the design** | K41's OPEN second witness (`docs/dev/known_issues.md` K41, the 1,250,766 B pattern that "compiles inside the budget today", 7.8 CPU-s against a 10 s budget): the model predicts **118,240 B**; actual comment-excluded size is **1,214,333 B** — 10.3× under. CAUSE: the pattern's VM HYBRID prefilter emits ~3,111 `static const void *const rx_targets_N[11]` computed-goto jump tables; `measure.py`'s `TABLE_DECL_RE`/`TABLE_OPEN_RE` cannot cross the `*` in `void *const`, so E stays 320, and its `LABEL_RE` matches only `rx_L<N>:` where this form uses `rx_sN:`, so N stays 552. So B̂(K=8) < the 131,072 threshold ("term does not run") on a pattern 9.3× the threshold; N=552/105 is far under the 2,000-node cap; K=1 saves 8.7 % anyway. NEITHER mechanism engages on a real, already-pinned oversize pattern. **1,262 of 2,487 corpus patterns use the hybrid prefilter** — not a rare path; the corpus just never blows it up | **SEND BACK**: (1) the instrument counts every table form (pointer tables included) and every label form, verified against the two K41 witnesses by hand count; (2) the hybrid's jump-table entries are a MEASURED term of the model (their gcc cost per entry measured like §4.2's), refit, error re-reported including on both witnesses; (3) the K rule, threshold and cap re-evaluated so that BOTH K41 witnesses are classified correctly — the cap must bind on PREDICTED gcc COST over all terms (or the note states, with the number, the population a node-only cap misses and why it is acceptable); (4) the population-nobody-counted lesson goes in the note and the check-design memory: the classifier's own regexes were the uncounted population. The size log's per-pattern figure ([ART-SIZE.1b], byte-exact `size_count.sh`) is the control the instrument must agree with |
| F2 | WRONG-NUMBER | §4.2's gcc log-log residual range "−20 % … +18 %" omits the three `alt` mixed points (alt500/2047/4000, E = 8,544-64,544, not node-decorrelated); on the 20-point population that produces the fit the range is **−43.3 % … +18.3 %** (fit itself reproduced exactly: 0.000542 · N^1.2687, crossings 2305/1929) | ACCEPTED → state the full population and range |
| F3 | WRONG-NUMBER (unit) | "0.0009 µs per table entry" is **0.905 µs/entry** (Δcpu 0.21 s / ΔE 232,000) — a ms/µs slip; the ≈5,930× node/entry ratio is consistent with the corrected unit | ACCEPTED |
| F4 | WRONG-NUMBER (minor) | §2.4 "DFA only … max 35.29 %" is the 4th-worst row; the DFA max is 35.35 % (`a\bb`) = the global max | ACCEPTED |
| F5 | GAP (provenance) | the committed `probes/fit.py` is a single-intercept OLS and cannot produce the note's two-intercept S(vm)/S(dfa) fit; the quoted coefficients came from an un-archived interactive run (the critic re-derived them by dummy-variable joint OLS on table ENTRIES, matching `model.json` to 10+ digits) | ACCEPTED → commit the script that produces the numbers |
| F6 | GAP | `vm_count_slots` (~emit_vm.c:2314) accumulates slot categories, not a node/label count; `nlabel` looks like an emission-time counter — N(K) pre-emission is asserted, not demonstrated | ACCEPTED → the revision names the actual pre-emission source of N(K) (a counting walk, or a dry emission) and its cost |
| F7 | not attacked | §5's three levers — the classifier is not archived, no data file to check | ACCEPTED → archive the lever classifier + its TSV (same fix as F5) |
| HOLDS | reproduced exactly | model coefficients and full error distribution (2.35/12.40/18.21/35.35 %); the non-monotone K curve; the 15/15 ranking; the 7-pattern ratio table and the empty materiality gap; the threshold gap (1.6434×, 7 of 2,487); the cap headroom (corpus max N = 1,471; untouched max exactly 445) | the corpus-scoped analysis is precise; the design fails OUTSIDE the corpus (F1) |

## critic-sem — findings and triage

Read-only; compiler `worktrees/artsize3/build/pcrec` (abi 9); gcc -O1 on
artifacts under ~600 KB; both K41 witnesses emitted verbatim; scratch
`r40-sem/`.

| # | severity | finding | disposition |
|---|---|---|---|
| S1 | **GAP — blocks §11's code phase** | §2.2/§4.3/§11.2: N(K) "already computed, exact" by `vm_count_slots` at the `v.unroll_k` site (:7461). FALSE: `vm_count_slots` (:2314) returns void, counts SLOTS (nctr/nmark/nguard/…) + `maxcopies`, not nodes; `Vm.nodes` (:433) is bumped only by `vm_charge` (:692-696) DURING emission (:2304 says so verbatim; limits.h:218-220 repeats it); `v.nlabel` is emission-time; the pre-pass MUTATES `v` and can `ctx_fail` on the replication product (:2610), so a 6-rung ladder cannot call it six times; and it runs at :7655, ~200 lines after :7461, behind region/splice/callgraph setup | ACCEPTED (= critic-model F6): the revision names the NEW node-counting pre-pass (re-runnable per rung, mirroring every rung decision — the three-way-agreement hazard `vm_count_slots`' own header warns about) or a dry emission, with its cost, and moves the selection to a site where the count exists; §11 budgets it as the largest piece of the code phase |
| S2 | **CONTRACT-CHANGE** | §6.1 "step/work budgets charged — per iteration", §0.9 "every K is answer-identical": REFUTED on the give-up surface. `((a)|ab){12}c` on "ab"×12: minimum `--step-budget` that completes K=1: 89, K=2: 89, K=3: 97, K=4: 98, K=6: 107, K=8: 110 (rung 0x10 at every K — chunking, via the once-per-trip MRL guard :4245-4260); minimum `--backtrack-frames` K=1 → 39, K=8 → 28 (descending K RAISES the frame need 39 %); `RX_TRAIL_FRAMES` in the emitted header 51/52/53/54/56/62 for K=8/6/4/3/2/1 — a macro match_api.md:1083 names as caller-read. Default-budget ANSWERS are identical (checked) | ACCEPTED: §6.1's identity claim narrows to match results + captures, explicitly excluding the give-up/capacity surface; the K-sweep gate is specified to compare answers under DEFAULT budgets and to exclude `budget`/`gu` cells by construction (stated, not discovered); a D80 hunk records that the size term may change a tuned caller's budget verdict (limits.md) |
| S3 | GAP | §6.1 "rung selection runs before K is consulted": FALSE — `vm_counter_fits` (:1034-1036) reads `v->unroll_k` (`rmin >= K || (rmax-rmin) >= K`). `((a)|ab){3}c`: rung 0x10 at K=1,2,3 → 0x2 at K=4,8 (RX_NSLOTS 7→6, RX_FAST_TRAIL 17→13). Reaches the corpus: `^(?R){0,2}$` (tests/recursion/d27/sr_depth.rxt:180, quantified.rxt) flips 0x2→0x10 between K=3 and K=2; its `gu frames` answer holds at all five K. §3.1's "identical on every subject" is a population artifact (every subject's counts ≫ 8) | ACCEPTED: §6.1 says rung answer-identity is gated TODAY by `make test-axes`' PCREC_NO_COUNTER bit; structural check 4 handles the no-counter-rung case (copy count = `count`, K inert) |
| S4 | GAP | §3.1a's "15/15" cannot fail: E is constant in K on every subject (built from the AST) and S(engine) is constant, so argmin_K B̂ ≡ argmin_K N(K) for any positive node coefficient — it validates that N ranks bytes, not the model | ACCEPTED: the ladder is specified as `argmin N(K)` — exact, no model; the fitted model stays load-bearing only for the threshold gate and the materiality bar, said explicitly |
| S5 | **CONTRACT-CHANGE — design-changing** | §4.3 "it cannot ship an uncompilable artifact … step 1 has already taken the smallest K": FALSE whenever the materiality bar DECLINES — step 1 then keeps K_opt. The bar is in BYTES, the cap in NODES. K41 witness 2 measured: K=1 1,127,561 B / N=105 … K=8 1,250,819 B / N=552 — ratio 0.9014 > 0.75 → DECLINES despite an 81 % node reduction. A shape with that ratio and N(K=8) > 2,000 is REFUSED although a ladder K exists under the cap (not landed as a witness — N=1,960 / 2,449 reached on nested variants; the arithmetic does not need it). N is also NON-MONOTONE in K in nodes (2,449/2,469/1,334/1,635/498/262 for K=8/6/4/3/2/1) | ACCEPTED: the cap re-runs the ladder (bar bypassed) before refusing — "refuse only if no K on the ladder is under the cap"; the cap is applied at the ladder-chosen K, never a greedily-descended one |
| S6 | CONTRACT-CHANGE (small) | both K41 witnesses under AUTO today: w1 2,004,464 B / N=7,467 / vm; w2 1,250,821 B / N=552 / vm. Under the rule: w1 above threshold, ratio ~0.05 → K=1 → 105,248 B / N=313 — leaves the fuzz gate's oversize bucket; w2 declines (S5) — stays. Neither refused; nothing that compiles today stops. **The pinned K41 bucket moves 2 → 1**, and known_issues.md K41 documents only "0 = closure" | ACCEPTED: K41 gains its hunk in this change (w1 fixed by the K rule; w2 table/prefilter-dominated, out of the row's reach — [OPT-4]'s mechanism); fuzz gate re-pinned at 1 with the reading; w2 is the PINNED counter-example to §10 Q4 |
| S7 | GAP (D80) | limits.md §7 "What is not limited today" states compile TIME is not a compiler-side contract; the cap makes it one, in the units that predict it | ACCEPTED → that sentence is the named spec hunk |
| S8 | NIT (r39 A1's class) | `.abi = 9,` sits in the emitted BODY of every artifact (line 863 of a VM artifact), DFA included: the bump moves every artifact by +1 byte; §8 "0 on DFA artifacts" and §9 rows 3/5 are wrong; §6.2 control 3 already says "stamp and `abi` lines" | ACCEPTED → §8/§9 agree with §6.2 |
| S9 | NIT (D81) | `_UNROLL_K_WHY` ∈ {default, size-model, option} has four reachable states behind "default" (denied / never ran / ran-and-declined / tied) — a check cannot tell "did not bind" from "ran and declined" | ACCEPTED → values `denied` / `default` / `size-model` / `size-model-declined` / `option` (or a second stamp carrying the ladder's argmin) |
| S10 | NIT | the ladder guard `K_c <= K_opt` is unreachable (K_opt is always 8 when the ladder runs) | ACCEPTED → drop or mark defensive |
| S11 | ASK | "0 of 2,487 refused" measured on the default axis only; N depends on more than (AST, K) (`-fno-length-prune` moves N 121→117 on `((a)|ab){12}c`); forced-VM table patterns are tiny (N = 2, 2, 2, 6) — low risk | ACCEPTED → re-measure under `--engine=vm` and each deny flag (emit only, no gcc; watchdog, PROCS≤4) |
| S12 | HOLDS | a mispredicted threshold cannot flip on today's corpus (worst error above 50 KB is 6.91 % vs 33 %/24 % clearance; the tail UNDER-predicts → a missed saving, never a wrong selection); K=1 is always legal for the counter rung (`vm_counter_fits` at K=1 true for every quantifier reaching it); descending K shrinks the K22 replication-product walk | no action |

**Open Q2 — critic-sem's recommendation: NOT deniable, but OVERRIDABLE
UPWARD.** The deny flag must never reach the cap (the note's argument is
right about a deny flag). But "not deniable" and "not overridable" are
different rulings, and every other resource limit in the project has a
per-compile override (`--step-budget`, `--work-budget`,
`--backtrack-frames=N` raising a compiled-in capacity; limits.md §3);
this would be the first without one, and its whole cost falls on the
caller's own gcc on their own box. On the [SEL-1] fallback path — the
one the note expects to reach the cap — "change the pattern" is not
available to a caller whose pattern came from a config file.
Recommended: `--max-emit-nodes=N` (+ option field), RAISE-ONLY,
hard-ceilinged by `PCREC_MAX_VM_NODES` (131,072), the effective value
STAMPED as a selection fact. Manager concurs; to Frank.

## Manager's disposition — REVISION REQUIRED before code

Sent back to lane artsize3 (2026-08-28 ~23:0x) with every ACCEPTED row
above as the revision bar. What changes the design: F1 (the instrument
was blind to the hybrid's jump tables — the model and both mechanisms
miss a pinned oversize pattern), S1 (no pre-emission node count exists),
S2 (K is caller-observable on the give-up surface — a D80 hunk, and the
new gate must be specified around it), S5 (the cap re-runs the ladder
before refusing), S4 (the ladder is argmin N). Rulings for Frank: Q2
(override shape), Q4 (witness 2 is the pinned shipped-size
counter-example). The lane HOLDS the code phase until the revision is
re-read by the manager; a focused re-check by critic-sem on S1/S2/S5
follows if the revision's mechanism moves.

## critic-sem — FOCUSED RE-CHECK of the revised note (6808bdd; the mechanism moved to DRY EMISSION over the ladder)

CLOSED: S2 (narrowing exact, table reproduced, D80 hunk named), S3
(nothing assumes rung-before-K — each trial re-runs `vm_counter_fits`
at its own K), S4 (`argmin N`, model confined to threshold + bar), S5
(bar-bypassed ladder re-run; cap applied at the ladder-chosen K), S8,
S9 (one value short — R5). S1 closed-with-caveat: dry emission is the
right answer and the counting-pre-pass refutation is correct, but it is
not yet a MECHANISM (R1, R3).

| # | severity | finding | disposition |
|---|---|---|---|
| R1 | **BLOCKER (contract change)** | §2.2/§3.3 "a trial that `ctx_fail`s is discarded … can never turn a pattern that refuses today into one that compiles": a trial CANNOT be discarded — `ctx_fail` (compile.c:14-28) ends in `longjmp(cx->jb,1)` and internal.h:1469-1475 states the rule: ONE recovery point (`compile_driver`'s single `setjmp`), fallback = a one-shot retry of the whole pipeline ([SEL-1] paid exactly that a day ago). A trial's failure unwinds past the ladder, `arena_free`s, and returns THAT trial's diagnostic. MEASURED, in the direction the note does not guard: `(?:(?:(?:(?:(?:(?:a\|b){41}){41}){41}){41}){41}){41}` with `--engine=vm`: **K=8 COMPILES (N=118,098), K=6 REFUSES** ("VM exceeds 131072 emitted nodes") — under LADDER=[8,6,…] a pattern that compiles today refuses after the change, citing a limit its artifact never reached at a K the user never asked for | ACCEPTED → design work the note must carry: the emitter's size guards RETURN an over-budget RESULT when a `trial` flag is set (internal.h:1469's own prescribed shape — never a second `setjmp`); the ladder consumes the result; a trial's refusal is never the compile's answer; the K=8-compiles/K=6-refuses witness becomes a test cell |
| R2 | **GAP** | the ladder's cost is bounded by its WORST rung, and K=6 is routinely the worst (`vm_counter_copies`' mandatory `K + m%K` term is non-monotone: m=16 → 8 copies at K=8, 10 at K=6). Measured: a 5-deep `{17}` tower K=8 **1.74 MB** / K=6 **3.12 MB**; 6-deep **16.2 MB** / **35.5 MB** — the ladder emits a 35 MB buffer to learn K=6 is bad, and the post-emission cap protects gcc, never pcrec's own time/memory; all trials allocate from one never-freed arena. "2.84 s worst in the project" is true of the corpus, not of the mechanism | ACCEPTED → an EARLY ABORT inside a trial once the scratch buffer passes the (code-bytes or total) cap — the buffer is already measured; with R1's result-returning guards this is the same mechanism; cost table re-measured on a worst-rung pattern; per-trial arena reclaim or a stated bound |
| R3 | GAP | `pcrec_emit_vm` mutates the shared AST (:5691 `a->u.call.nonnullable`; :5726-5727 `a->u.call.save`/`.nsave` = pointers into THAT run's arena, K-dependent) and `job->enc_mask`; repeated emission is currently BENIGN only because every publisher precedes its readers within a run (`vm_publish_nonnull` :7582/7593 < `vm_count_slots` :7655; `vm_publish_saves` :7915 < `vm_cost` :2277 / `vm_splice` :5920) — a property nothing states and nothing checks (:1181 relies on the arena reading FALSE for an unpublished annotation — true on run 1 only) | ACCEPTED → the note states the invariant "every annotation the emitter writes is re-published by the same run before any reader consumes it", the code phase asserts it, and a sabotage (move `vm_publish_saves` after `vm_cost`) must turn §6.2 control 4 red |
| R4 | CONTRACT-CHANGE (from the ruling) | with the D45 cap on CODE bytes (outside table initializers) at 500,000: `a{1,31000}` = 1,369,177 B total but **12,851 code bytes** → ADMITTED by the code cap (§4.3 said refused); K41 witness 2 = **1,248,680 code bytes** (its 3,111 prefilter states are computed-goto CODE, `RX_DFA_TABLE "none"`) → refused at every K; §4.3's three derivations (the fuzz gate's 1,000,000 raw, the corpus gap, tripwire independence) rest on RAW bytes and must be re-derived on code bytes; `--emit-main`'s appended `main()` is code the user never ships — define the quantity without it | ACCEPTED with the manager's clarification: the TOTAL-bytes cap (1,000,000, exact) STAYS beside the code cap — `a{1,31000}` is refused by IT (Frank's Q4: "a large byte count makes it unusable"), so Q4 is answered by the two-cap set, not reopened; (i) and (iii) stand |
| R5 | NIT | §4.4 step 4 (cap rescue) takes a K after the bar declined it — stamps `size-model`/`-declined`, neither true | ACCEPTED → sixth value `cap-rescue` |
| R6 | NIT | the give-up surface has NO gate after S2's exclusion | ACCEPTED → on excluded cells compare the give-up CODE where both K give up; the check records the excluded population's size |

Fix order (critic): R1, R2, R4, R3, R5, R6. Manager: agreed; R1+R2 are
ONE mechanism (result-returning size guards under a trial flag, with
the buffer-size abort as the first such guard).
