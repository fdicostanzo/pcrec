# r39 — D6 critic panel on the [OPT-K] DESIGN NOTE (docs/design/offset_k_skip.md at lane/optk d13f5be), before the emitter side

Three read-only critics, no make: critic-sem (opus; semantics + answer
identity — REPORT PENDING at the time of this skeleton), critic-cost
(sonnet; cost model + numbers — transcribed prefix_k.c's model_cost into
python, reproduced §4.7's 20/372/6,037 ppm exactly, then substituted
MEASURED byte frequencies over bench/loglines 163,048 B / 112 subjects
and bench/email 42,653 B / 85), critic-arch (sonnet; architecture fit +
process obligations — verified against the lane's LIVE uncommitted
emitter, which already existed point-for-point during the review).

VERDICTS SO FAR. arch: the design fits — a genuine SELECTION over
[ENG-FORM]'s candidate lists (dfa_pfs[] gains two entries at the head,
the five k=0 forms unchanged byte-for-byte, emit_scan_loop untouched,
one new `emit_block` slot on the existing DfaPf); `Nfa.anch_start` in
the IR layer, set once in pcrec_build_nfa, is the right home; D83's
hook (static table, findings file named-not-built) and the D66 answer
(A_LOOK lowers to N_EPS on this NFA — nfa.c:621 — so the walk cannot
see a lookbehind's bytes today) both hold. cost: NO WRONG-SELECTION
found on any population tried (real loglines/email frequencies, an
adversarial dense-UUID subject with `-` at 10.8 %, hex32-id stays
declined at 0.82-1.25×); what fails is the note's arithmetic hygiene.

## Findings and triage

| # | lens | severity | finding | disposition |
|---|---|---|---|---|
| A1 | arch | MISSING-OBLIGATION (confirmed) | §5.1/§6.2 claim the `-fno-offset-skip` build is BYTE-IDENTICAL to the pre-row compiler's output; false by D81 (selection facts are stamped unconditionally — `_DFA_PREFILTER_OFFSETS "none"` on every abi-9 DFA artifact). Foreseeable at design time; already corrected in the lane's uncommitted tree | ACCEPTED → optk: the note of record says "differs by exactly one stamp line" and states what the control proves (answer identity + loop objdump equality) |
| A2 | arch | MISSING-OBLIGATION (in progress) | structural check `tests/codegen/run_offset_skip.sh`, the tests/mech sabotage row, and abi site 4 (run_recursion_identity.sh FILEPIN re-pin) not yet in the tree; sites 1-3 landed live | ACCEPTED → landing bar, before delivery |
| A3 | arch | LAYERING nit | prefix_k.c `wclose` and dfa.c `clo_walk` are two hand-maintained exhaustive NKind switches (different semantics — sound over-approximation vs exact context-parametrized closure — so NOT a parallel mechanism), nothing keeps them in sync on a new NKind | ACCEPTED → a line in the note naming the pairing; a shared NKind-count guard if cheap |
| A4 | arch | nit | walk-termination-on-accept re-derives a min-width-adjacent fact mrl.c's pcrec_minw computes over the AST for the VM | NO ACTION (different representation, different consumer) |
| C1 | cost | MODEL | three inconsistent "predicted gain" numbers for the same rows: §4.5 19×/31×/3,600×; §4.7's ratio column is a candidate-MASS ratio (40,350×/201×/134×); model_cost(base)/model_cost(new) — what the materiality check tests — is 192×/38×/23× (static table) | ACCEPTED → one formula; relabel §4.7's column; §4.5 and §7 quote the model_cost ratio |
| C2 | cost | MODEL | the static prior is 3-12× off on the load-bearing bytes vs real log text (digits 265,848 ppm measured vs 74,760; `-` 17,927 vs 4,984; `t` 27,200 vs 60,061); selection survives (78×/25×/44× with the measured table) but §4.3's sensitivity grid never sweeps the PRIOR | ACCEPTED → add the prior sweep (measured-loglines table as a SECOND prior, sensitivity only; the shipped table stays static per D83/learnings §3) |
| C3 | cost | MODEL | C_ENTER = 10.7 cycles (measured, opt3) × "~2 bytes a false start survives" (uncited) is labelled MEASURED | ACCEPTED → measure false-start survival on the three exercising patterns or drop the label and state the band |
| C4 | cost | DESIGN | for `\b`-prefixed patterns the walk computes S[0] (stack-frame: literal `a`, 33 K ppm) and discards it; the offset-0 verify keeps only the 63-byte escape set. §5.4 needs the escape set for termination, but a tighter ADDITIONAL k=0 verify is one more (k, set) member | ACCEPTED as a question → optk evaluates under the model; include if material, else record why |
| P1 | cost | PLAN | §7.1 names no number to hold the timing run against — a 5× real gain on a 23× prediction would pass every stated check | ACCEPTED → state the model_cost prediction per exercising row (static and measured prior) with a tolerance before measuring |
| P2 | cost | PLAN | load discipline inherited by reference only; the box carries lanes today (load1 1.06-1.66 observed during the review) | ACCEPTED → restate in §7.1 (idle box, taskset, load1 per row) |
| P3 | cost | PLAN | no artifact-size estimate for the accessor block + stamps; abi 7 overshot its own +5 KB estimate 6× | ACCEPTED → one-line estimate before the bump, checked after |
| C5 | cost | nit | C_VERIFY (250) honestly unmeasured; the per-candidate bounds check is not in the model | NOTED (rare path) |
| — | cost | unverified | §4.3's 1,352-pattern C_ENTER sweep counts (11/33/120 changing k-set) — plausible, not reproducible without make | NOTED |

Sent to optk as change requests 2026-08-28 ~13:5x (message id 2e57c580).
critic-sem's findings are appended below when they arrive.

## critic-sem (opus; semantics + answer identity) — VERDICT: the emitter must NOT be written from the note as-is

Evidence: scratchpad/critic-sem/ (t1.c/t1_optk.c, h2.c/h2_optk.c, census_all.py). The k≥1
walk is CONFIRMED sound (attacked with unequal-width alternation, optional/{0,n}, lazy,
nested groups, case folding, \b/^/lookaround at and before k, empty-width atoms, dotall,
negated classes, UTF-8, backrefs, calls, atomic groups, counter replication — held every
time; erased constructs cannot shift later offsets, closed upstream at nfa.c:816/830;
the walk reads the same NFA the DFA is built from; `cand = hit − k*` cannot underflow so
the plan row's "clamp" is unnecessary; overlapping candidates/resume/find-all O(n) all
confirmed; full-alphabet k=0 unreachable; \G and (?m)^ compile "attempt", never reach the
reseed). REFUSAL-NEEDED: none.

| # | severity | finding | disposition |
|---|---|---|---|
| S1 | **MISCOMPILE** (demonstrated, both engines) | the offset-0 member of the k-set reuses `cand_from_escapes` (bytes that move the machine off `fs` — the SCAN role; §2.1 says "not because a match can begin there") as a VERIFY that refuses a start. On a SEEDED machine (every \b/\B pattern; 3 of the 4 §4.7 beneficiaries) the reseed lands in `s1u[word]`, where a byte that fails \b from fs STARTS a match. Witness `\b\.[0-9]{4}Z` (main c60679b: DFA, byte-class-bounded, can_begin_match = the 63 word bytes, '.' = 0); the rule selects it at 288×; §5.2's form transcribed into the artifact: "ab.1234Z" (2,8) → nomatch, "x.9999Z" (1,7) → nomatch, oracle = baseline; VM hybrid `\b\.([0-9]{4})Z` the same. §5.5 is no net: the forward pass never spawns the thread. Real shapes exposed: `\b:[0-9]{2}:[0-9]{2}`, `\b\.[0-9]{3}Z`, `\b-[0-9]{4}-`. NO EXISTING GATE SEES IT (test-axes compares two builds that agree; corpus lacks the shape). Corpus census: 30 non-\b patterns whose set misses match-start bytes are SAFE (unseeded: δ(s0,b)=s0 everywhere) | ACCEPTED, BLOCKING → optk: split offset 0 by ROLE — scan keeps `us.cand.set`, the verify uses the walk's own frontier[0] (already computed at prefix_k.c:337, overwritten at :317); restate §3.2 over the whole conjunction; §6.1 as a four-step argument naming the state each step is about; oracle-verified .rxt witnesses + a sabotage row that swaps the verify table for can_begin_match |
| S-D1 | DESIGN | §4.7/§4.3/§4.5 all computed against the wrong offset-0 mass (807,006 ppm is the role-A quantity); uuid's/stack-frame's verify mass drops ~3× under the fix; declines UNDECIDED | ACCEPTED → re-run against the corrected mass |
| S-D2 | DESIGN | §5.6's stated reason (EOL/END views) does not cover the \b rows — the bounded form is selected by `wctx`; what carries them is `!start_acc`'s s1u OR (emit_dfa.c:2153-2156), the one place that already reasons over every seeded start — and it is the reason that would have caught S1 | ACCEPTED → rewrite §5.6 on it |
| S-D3 | DESIGN | "greedy is exact" unproven: verify_cost is non-monotone in p (peaks at 0.5); code is fine (decreasing gains) | ACCEPTED → claim a decreasing-gains greedy |
| S-D4 | DESIGN | the no-`default:` NKind switch alarm is `make strict`'s only (-Werror not default); 12/12 handled today | ACCEPTED → say so or add a structural check |
| S-D5 | DESIGN | model_cost's integer arithmetic zeroes the C_ENTER term below ~500 ppm — the model is cost-blind among the selective candidates §4.7 advertises | ACCEPTED → scale or state |
| S-D6 | DESIGN | five stop conditions, not four: an empty S[j] means the pattern cannot match — [OPT-5]'s degenerate case, thrown away | ACCEPTED → list it; exploit or say why not |
| S-N1..3 | NIT | negative-k scan pointer guard (§10); `ofsk_emit_verify`'s `1` fallback → assert; `_OFFSETS` sibling stamp absent at 891b672 | ACCEPTED (N3 since added; structural check must read the artifact's k-set) |

Sent to optk as a BLOCKING change request (message 2026-08-28 ~14:0x). The lesson for
learnings.md / the check-design memory: a set derived for one ROLE (skip a parked run)
reused for another (refuse a start) — the identity gate compared two builds that shared
the wrong set and agreed; only an ORACLE-verified witness of the exposed shape can see it.
