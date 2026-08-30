/* src/core/limits.h — every number in this compiler that encodes a POLICY.
 *
 * WHY ONE HOME. A bare `250` in parse.c and a bare `60` in compile.c look alike
 * and are not alike: one reproduces a PCRE2 boundary and the other is a choice
 * we made and may change on a Tuesday. A reader cannot tell which is which, and
 * neither can a reviewer deciding whether a divergence matters. The value of
 * this file is the PROVENANCE, not the collection — the sections are the point.
 *
 * WHAT BELONGS HERE, and the rule is deliberately narrow so this does not
 * become a junk drawer: a number belongs here if changing it changes what pcrec
 * ACCEPTS, REJECTS or PROMISES. Structural constants do not (256 byte values,
 * a 32-byte class bitmap, an arena block size, a growth factor), and neither do
 * local algorithmic bounds whose correctness argument lives beside them —
 * `TRIE_MAX_RDEPTH` and `MAX_GROUPS` stay in src/ir/nfa.c on purpose, with
 * their proofs. Moving those here would separate a bound from the reason it is
 * sound, which is worse than scattering.
 *
 * THE THREE SECTIONS ARE D26's TIERS. That decision says pcrec aims at
 * FUNCTIONAL compatibility with PCRE2, not bit-exact compatibility with one
 * installed build of a moving target — fully aligned at the core, less effort
 * the further out, and least of all for constructs pcrec will never implement.
 * Which section a number sits in tells you what to do when a PCRE2 upgrade
 * disagrees with it:
 *
 *   OURS              nothing to do. PCRE2 has no opinion.
 *   PCRE2 SYNTAX      investigate. The language changed under us and a pattern
 *                     someone writes now behaves differently. This is core.
 *   PCRE2 INTERNALS   record it and move on. These are artifacts of how PCRE2
 *                     is built, not of what the language means, and pcrec's
 *                     values are MINIMUMS we honour, not contracts we owe. */

#ifndef PCREC_LIMITS_H
#define PCREC_LIMITS_H

/* ---- OURS — engineering choices, free to tune -------------------------- */
enum {
    /* Generated-symbol prefix (`-p`). A C identifier bound, nothing more. */
    PCREC_MAX_PREFIX_LEN = 60,

    /* K38 (2026-08-26): the size EVERY fixed buffer that holds an EMITTED
     * identifier or C sub-expression built from the `-p` prefix must use.
     * Before this, each site in src/gen/emit_vm.c (and emit_dfa.c's own
     * shape) hand-picked a buffer size for its own short suffix on a short
     * prefix; snprintf does not fail on overflow, it TRUNCATES, so a real
     * 60-char prefix (the documented maximum, accepted by cli/main.c's
     * `valid_prefix` and promised by docs/spec/cli.md §1) met a family of
     * buffers sized for "rx" and produced uncompilable C — a MISCOMPILE, not
     * a give-up, invisible to every corpus artifact because they all use the
     * 2-char "rx" prefix. Reproduced and enumerated with a real 60-char
     * prefix run through gcc (see tests/cli/run_cli_tests.sh case3): the
     * worst observed content is a slot expression, `<prefix>_<slot-name>` at
     * up to 60 + 1 + 47 = 108 bytes. This constant is PCREC_MAX_PREFIX_LEN
     * plus generous headroom over that worst case, plus NUL, so ONE size
     * answers "how big" at every such site instead of a fresh per-site guess
     * that reopens K38 the next time a suffix grows (the frames_sentinel fix
     * earlier the same day made exactly that hand-picked mistake once more,
     * which is why this is a shared constant now rather than another
     * PCREC_MAX_PREFIX_LEN + <n> literal). Buffers sized from it only GROW
     * relative to their old hand-picked sizes, so every artifact this
     * compiler already emitted for an in-range prefix is byte-identical. */
    PCREC_MAX_EMIT_NAME_LEN = PCREC_MAX_PREFIX_LEN + 96,

    /* [SEL-1] (2026-08-28) The fixed size of `Ctx.dfa_overflow_why` — the
     * DFA-cap-overflow reason `pcrec_select_engine`'s `forces_dfa_overflow`
     * row reports as `RX_ENGINE_WHY` on an `--engine=auto` compile that
     * retried after its DFA build overflowed. A plain array on `Ctx`, not an
     * arena string: it must survive `job_cleanup`'s `arena_free`, since
     * `compile.c`'s retry decision reads it AFTER the failed attempt's arena
     * is gone. Sized for the longer of the two "pattern too complex"
     * ctx_fail sites' own texts (src/ir/dfa.c) — "dfa overflowed: subset
     * construction exceeds 48000000 state-set elements (K7)" is 76 bytes —
     * plus headroom, the same margin-over-worst-case shape K38 above uses. */
    PCREC_DFA_OVERFLOW_WHY_LEN = 96,

    /* M2.8 raised this from 20000. It is a MEMORY backstop (48 B/state, two
     * machines, so ~12.6 MB), not the real ceiling: the DFA caps below are
     * grounded in emitter cost (R1 A-3) and now bind first across the
     * realistic keyword range — 6000-word lists compile, 10000-word lists
     * fail on the DFA cap with its actionable "try --engine=vm".
     * Stack depth is no longer a constraint here: clo_visit's tail edges are
     * iterative (verified at -O0 on a 1,000,000-branch alternation). */
    PCREC_MAX_NFA_STATES       = 131072,
    PCREC_MAX_DFA_STATES_GOTO  = 10000,   /* computed-goto attempt engine */
    PCREC_MAX_DFA_STATES_TABLE = 32000,   /* table engine; must fit in short */
    PCREC_MAX_TABLE_ENTRIES    = 2000000, /* states*ncls bound (~12 MB source) */

    /* [OPT-4] `PCREC_PREFILTER_EXACT_NFA_STATES` WAS HERE AND IS GONE (Frank's
     * ruling B, 2026-08-29). It was the knee that chose the count-collapsed
     * prefilter by measuring the exact NFA, and the measurement that removed it
     * is in docs/design/prefilter_count_independence.md §10: the collapse buys
     * bytes with match-time and step-budget costs, so it now acts only where
     * the exact artifact CANNOT SHIP — the [SEL-1] state-cap rung and the
     * emitted-size-cap rung, both in `compile_driver`'s ladder — never because
     * a state count crossed a threshold. `-fprefilter-collapse` is the route to
     * the old behaviour and more. NOTHING REPLACES IT: there is deliberately no
     * new constant here, because the caps below are now the only quantity that
     * decides, which is the whole of ruling B. */

    /* [M4.7b] K7's SECOND half: how many NFA-state-list ELEMENTS the priority
     * subset construction may intern, summed over every machine one compile
     * builds (forward and reverse are charged together because both are live
     * at once).
     *
     * WHY THE STATE-COUNT CAPS ABOVE CANNOT DO THIS. They bound how many DFA
     * states exist; the construction's memory is the sum of those states' SET
     * SIZES, and the two come apart by a whole factor. Unanchored `a{n}` is the
     * clean example: the start self-loop means that after k bytes every chain
     * position 0..k is live, so the machine has n+1 states whose sets average
     * n/2 — n+1 against the cap, n^2/2 in memory. MEASURED: `a{10000}` interns
     * 50,025,000 elements for 216 MB, `a{20000}` 200,050,000 for 845 MB and
     * 63 s, `a{30000}` 1.87 GB and 154 s — all of them COMPILING, none of them
     * within sight of the 32000-state cap. `a{65535}` did reach that cap, but
     * only after 2.1 GB, because the cap is consulted per state and the memory
     * is spent per element.
     *
     * THE NUMBER IS THE TEST CORPUS'S MEASURED MAXIMUM, DOUBLED. The most
     * expensive pattern in tests/ is `((a)|bc){0,4000}d` at 24,050,003
     * elements (285 MB before this lane's nfa.c fix, 111 MB after; the element
     * count is the same either way, which is the point of counting elements
     * rather than bytes) — counterk.rxt's "endgame count", deliberately built
     * one body over D45's own case to prove [ENG-BREP]'s counter rung lifted
     * the replication bound, so it is an extreme by construction rather than
     * by accident. Doubling it is the headroom; nothing a person writes is
     * near it.
     *
     * WHAT IT COSTS AT THE CEILING, MEASURED at the boundary rather than
     * extrapolated from a rate: ~216 MB and 0.9 s for the worst refusal
     * (`a{65535}`), ~175 MB and 3.9 s for the most expensive compile that
     * still fits (`a{9000}`, and `[a-zA-Z0-9_.-]{9000}` and `[^\n]{9000}`
     * land within 100 KB of it, so the cost is set by the element count and
     * not by the alphabet). Bytes-per-element sits at 4.3-4.6 across every
     * shape probed, which is why one element count bounds every one of them.
     *
     * WHAT IT REFUSES THAT USED TO COMPILE, stated plainly because it is a
     * narrowing and not only a rescue: exact repeats above `a{9795}` (bisected;
     * `a{9795}` compiles, `a{9796}` refuses). Those cost 63 s and 154 s at
     * n=20000 and n=30000 today — D45's own
     * standard says a compile needing that much is a failure rather than a slow
     * box — and the refusal is the EXISTING "too complex for the DFA engine"
     * family pointing at the VM, not a new tier (D26). The boundary for this
     * family already existed at 65535, set by the state cap; this moves it, it
     * does not invent it.
     *
     * THE LEVER THAT BUYS THAT BEHAVIOUR BACK, WITH ITS PRICE, so a vendored
     * user who needs the old boundary does not have to rediscover the cost.
     * Raise this number; each step below is MEASURED on the project box with
     * the budget removed, which for this family IS the pre-[M4.7b] compiler
     * (the nfa.c fix does not touch exact repeats):
     *
     *   205,000,000   restores `a{20000}`   —  845 MB, 63-99 s
     *   460,000,000   restores `a{30000}`   — 1.87 GB, 109 s
     *   ~500,000,000  restores everything this family ever had: above roughly
     *                 this the budget stops binding and the 32000-state cap
     *                 takes over, which is where `a{65535}` refuses — at
     *                 2.1 GB. There is nothing to buy beyond that point.
     *
     * Those seconds are the reason for the default, not a footnote to it: a
     * 63-109 s compile is what D45 calls a failure rather than a slow box.
     *
     * Same revisit-when as every other budget here: if a LEGITIMATE pattern is
     * measured needing more, raise it WITH the measurement recorded. Note that
     * raising it buys repeat count only as its SQUARE ROOT — the table above
     * is 2.2x the number for 1.5x the reach — because the cost is quadratic in
     * the repeat count, not linear. */
    PCREC_MAX_SUBSET_ELEMS     = 48000000,

    /* [M4.5b] The VM emitter's own size backstop, and the reason it needs one
     * separate from the NFA cap above: a bounded repeat REPLICATES its body
     * (docs/design/engine_m4.md §3.3's RULED reading — `X{m,n}` is m mandatory
     * copies plus n-m optional ones, with no counter and no suppression test),
     * so `(a|b){0,10000}` emits ten thousand copies of the body's labels. The
     * NFA cap normally binds first, because the NFA replicates the same way —
     * but `--engine=vm` skips machine construction entirely (§5.6: the
     * prefilter is OFF in that mode, so there is no NFA to cap), which is
     * exactly the invocation where nothing else would stop it.
     *
     * The number is the NFA cap's, deliberately: the two count comparable
     * things (one emitted node per label, one NFA state per position) and a
     * pattern that fits one should not surprise a reader by failing the
     * other. It is NOT grounded in gcc compile time the way the DFA caps are
     * (R1 A-3), because §2.1's whole point is that VM code size is linear in
     * the expanded node count where DFA state counts are exponential —
     * measuring where the VM's gcc cliff actually sits is ASK-7, unowned. */
    PCREC_MAX_VM_NODES         = 131072,

    /* [M4.5c fix] The SECOND VM size bound, and the one D45's consequence 1
     * asks for: how many times a bounded repeat may REPLICATE a body that
     * contains a choice point.
     *
     * PCREC_MAX_VM_NODES above is not enough, which D45 records as a defect:
     * it refused `(a|b){0,65535}` and let `((a)|b){0,4000}c` emit 3.5 MB that
     * pegged cc1 for 100+ minutes.
     *
     * WHY THIS CAP IS ON REPLICATION AND NOT ON TOTAL SIZE. gcc's cost is
     * superlinear in the emitted program, so a naive reading caps total size —
     * and a first draft of this did, at 128 total backtrack resume points.
     * MEASURED, that refuses the wrong patterns: a 200-branch capture-bearing
     * keyword alternation has 199 resume points and compiles in 0.50 s at -O2
     * (100 branches measured), because its size is PROPORTIONATE to what the
     * author wrote. `((a)|b){0,4000}c` is sixteen characters and 3.5 MB. The
     * defect is DISPROPORTION, not size, and only replication produces it.
     *
     * THE NUMBER (project box, 2026-08-15; the full curves are in
     * docs/testing.md's battery section):
     *
     *   ((a)|b){0,N}c    bytes    -O1     -O2     ubsan -O1
     *      N =  64       65 KB   0.50 s  1.40 s     2.30 s   <- the cap
     *      N = 128      120 KB   0.90 s  4.61 s     6.11 s
     *      N = 400      355 KB   3.50 s 51.54 s    49.94 s
     *
     * D45's plain budget is 5 s. At 64 copies the worst allowed artifact costs
     * 1.40 s at -O2 (28% of it) and 2.30 s under UBSan (4% of the 60 s
     * sanitizer budget); 128 copies would sit at 92% of the plain budget,
     * which is not a margin.
     *
     * A body with NO choice point does not replicate at all — it compiles to a
     * span loop (engine_m4.md S2.5's cursor rung) — so `a{0,65535}` and
     * `(?:ab){0,9999}` are unaffected, and the diagnostic can name the one
     * construct that reaches this cap without guessing. */
    PCREC_MAX_VM_REPEAT_COPIES = 64,

    /* [K22] The THIRD VM size bound, and the one the other two structurally
     * cannot provide: how many times a body may be replicated in TOTAL along a
     * chain of NESTED bounded repeats.
     *
     * WHY NEITHER OF THE TWO ABOVE COVERS IT. `PCREC_MAX_VM_REPEAT_COPIES`
     * bounds ONE quantifier's own factor, and nesting MULTIPLIES factors that
     * are individually tiny: a depth-40 tower of `{0,2}` has a maximum factor
     * of 2 and replicates the innermost body 2^40 times.
     * `PCREC_MAX_VM_NODES` would catch it, and does — but it is charged DURING
     * emission, while `vm_count_slots` must walk the same copy tree BEFORE a
     * byte is emitted, so the walk itself is the Theta(2^d) work nobody
     * bounded. K22: depth 30 refused in 11.8 s and depth 35 hung with no
     * diagnostic, on a 320-character pattern (docs/dev/known_issues.md K22,
     * docs/design/possessify_impl/k22_repro.txt).
     *
     * IT IS THE NODE CAP'S OWN VALUE, and that is a structural identity rather
     * than a coincidence worth tuning separately. Every replicated copy of a
     * body costs at least one `vm_charge` (one `vm_emit` call per copy), so
     * the total replication product is a LOWER BOUND on the emitted node
     * count. Refusing above `PCREC_MAX_VM_NODES` therefore refuses only
     * patterns `PCREC_MAX_VM_NODES` was going to refuse anyway — the guard
     * moves the refusal EARLIER, never wider, so it cannot cost a pattern that
     * compiles today. MEASURED on the K22 tower: depth 16 (product 65,536)
     * compiles before and after; depth 17 (product 131,072, exactly at this
     * limit) still reaches the node cap in 0.7 s; depth 18 and up now refuse
     * in ~0.1 s where depth 35 used to hang.
     *
     * The REAL fix is [ENG-BREP]'s counter-K rung, which stops replicating for
     * exactly these shapes. This is the interim guard that makes the failure
     * honest in the meantime. */
    PCREC_MAX_VM_REPLICATION_PRODUCT = PCREC_MAX_VM_NODES,

    /* [ENG-BREP] K, the COUNTER rung's unroll factor (D47.2; counter-K design
     * note §4.1). One body copy per K iterations plus an iteration counter,
     * replacing the full replication the two caps above exist to bound.
     *
     * WHY IT BELONGS IN THIS FILE, where VM_DEFAULT_WORK_BUDGET deliberately
     * does not: changing K changes what pcrec ACCEPTS. The emitted copy count
     * for a bounded repeat is a function of K, so K and the caps above jointly
     * decide which patterns compile and which are refused — this file's own
     * inclusion rule, met exactly. A runtime give-up budget meets none of it
     * and lives beside its siblings in the emitter.
     *
     * THE VALUE IS MEASURED, on two curves that agree (eng_brep_design.md
     * §4.4): gcc -O2 compile time is quadratic in emitted copies, and the
     * throughput advantage of unrolling is exhausted by K ~= 16. 8 sits below
     * the knee on both.
     *
     * ONE PER ARTIFACT, and that is RULED rather than chosen (D47 ADDENDUM,
     * holding eng_brep_design.md §4.5 strictly): K does not vary per
     * quantifier in v1. The downward clamp that would have varied it — the
     * thing that actually fixes small-count nesting towers — moved whole to
     * plan row [ENG-CLAMP]. So a pattern mixing `{0,3}` and `{0,4000}` unrolls
     * both by 8, and the first replicates either way. */
    PCREC_DEFAULT_UNROLL_K = 8,

    /* [ENG-BREP] How many byte-consuming POSITIONS a quantifier body may have
     * before src/opt/possessify.c gives up on it. It bounds the position
     * (Glushkov) automaton the §2.2 unique-iteration test is decided on: the
     * analysis carries one byte set and one follow-union per position, and
     * the pairwise-disjointness sweep is quadratic in them.
     *
     * It changes what pcrec PROMISES only in the direction that is always
     * safe. Exceeding it DECLINES — the quantifier keeps its backtracking
     * machinery and matches exactly as it does today — so raising or lowering
     * this number can change how fast an artifact runs and can never change
     * what it matches. 256 because that is also the width of the position
     * SET representation (one bit per position in the same 32-byte shape as a
     * class bitmap), so the two limits are one number rather than two that
     * could drift; a body with more than 256 literal positions is not a
     * bounded repeat anybody is waiting on. */
    PCREC_MAX_POSSESS_POSITIONS = 256,

    /* [ENG-BREP] How many CAPTURING GROUPS a quantifier body may contain before
     * src/opt/revdet.c declines the reverse-deterministic rung.
     *
     * It is a bound on EMITTED LOCALS, not on analysis: the rung recovers the
     * last iteration's captures by a backward walk that accumulates one span
     * pair and one seen-flag per body group before publishing them, and those
     * live in the matcher's frame. Same number and same reason as the cursor
     * rung's own `VM_MAX_BODY_CAPS` (src/gen/emit_vm.c), which bounds the same
     * kind of table for the same failure: a group the table could not hold
     * would never be written and would report UNSET on a match it participated
     * in — a silent wrong span, which is the one outcome D26 refuses outright.
     *
     * Like every other decision in that pass, exceeding it DECLINES: the
     * quantifier keeps the machinery it has today and matches exactly what it
     * matches today, so this number can change how fast an artifact runs and
     * can never change what it answers. */
    PCREC_MAX_REVDET_BODY_GROUPS = 64,

    /* [OPT-ALTCLS] stage 2 (src/opt/altcls.c): how many times prefix
     * factoring may RECURSE into a group that just SPLIT (branches that
     * shared a literal prefix diverging on the next byte), before it stops
     * factoring that subtree further.
     *
     * It is NOT a bound on the shared-prefix LENGTH — extending a prefix
     * while every branch in the group keeps agreeing is an ITERATIVE loop
     * (D10/DD-10/R1 R-2's discipline: a long common literal run, like a
     * quantifier body or a flat concatenation elsewhere in this tree, is a
     * PATTERN-LENGTH-shaped input and must not cost a stack frame per byte).
     * This bound is on SPLIT depth only — how many times one group's
     * branches fork into two-or-more literal-byte sub-groups that each get
     * factored again — which is shaped by branch COUNT, not by any single
     * branch's length, and is the one axis the iterative loop cannot absorb
     * because each split is a genuinely different recursive subproblem.
     *
     * Exceeding it DECLINES the remaining sub-groups (they stay spelled as
     * alternation, unfactored) rather than refusing the compile — the same
     * safe-fallback shape every other cap in this file uses: this number can
     * change how much of a deeply-forking branch set gets factored and can
     * never change what the pattern matches. 64 mirrors
     * `PCREC_MAX_REVDET_BODY_GROUPS` above: a branch set that keeps forking
     * new literal-prefix sub-groups 64 levels deep is not a keyword list
     * anybody is waiting on. */
    PCREC_MAX_ALTCLS_FACTOR_DEPTH = 64
};

/* ---- PCRE2 SYNTAX — exact, and part of the language -------------------- *
 *
 * These two decide whether a pattern a person writes is legal. Both MEASURED
 * against libpcre2 10.46 rather than read from documentation, 2026-08-10:
 * changing either makes pcrec accept or reject patterns PCRE2 does not. */
enum {
    /* `a{65535}` compiles; `a{65536}` is PCRE2 error 105, "number too big in
     * {} quantifier". This is the ceiling FIX-1's K5 was about. Note python
     * `re` does NOT agree — its ceiling is 4294967294 — so the corpus oracle
     * cannot check this one and tests/reject/ owns it. */
    PCREC_MAX_REPEAT = 65535,

    /* 250 nested groups compile; 251 is PCRE2 error 119, "parentheses are too
     * deeply nested", and pcrec agrees exactly. parse.c called this a
     * "PCRE2-like" cap, which undersold it — it is PCRE2's number, measured.
     * It also bounds parser and AST recursion depth (R1 review R-1), so it is
     * load-bearing for more than compatibility. */
    PCREC_MAX_GROUP_DEPTH = 250,

    /* [M6.3] a named group's name: 128 bytes compile, 129 is PCRE2 error
     * 148, "subpattern name is too long (maximum 128 code units)" — swept
     * 1..2000 bytes of an otherwise-valid name against libpcre2 10.46
     * (tests/probes/probe_named_groups.c), so this is a measured wall, not
     * an assumed carry-over of PCRE1's older 32-byte MAX_NAME_SIZE. */
    PCREC_MAX_GROUP_NAME = 128
};

/* ---- PCRE2 INTERNALS — minimums we honour, not contracts we owe -------- *
 *
 * Both of these are artifacts of how libpcre2 10.46 is BUILT, not statements
 * about what a regex means, and both govern constructs pcrec rejects today and
 * may never implement. They are here so that a future reader can see they are
 * the cheap tier rather than the core one, and so that a PCRE2 upgrade moving
 * them is a note in the journal rather than a bug. Do not spend on making them
 * exact again; see D26. */
enum {
    /* A verb name of 128 bytes is PCRE2's ordinary "not recognized"; 129 is
     * error 148, "subpattern name is too long (maximum 128 code units)".
     * Measured over every length 1..319 in both name tables (R8/C2-9): exactly
     * two transitions in 638 probes, both at 129, and table-independent. */
    PCREC_VERB_NAME_MAX = 128,

    /* `(*LIMIT_MATCH=N)` and friends. PCRE2 refuses while ACCUMULATING, one
     * digit before its uint32_t counter would overflow, so the boundary is
     * 4294967290 rather than 4294967295 — reject once the running value would
     * exceed UINT32_MAX/10 - 1. Leading zeros never move the accumulator, so
     * `=00000000000000000001` compiles: this is a MAGNITUDE rule, not a length
     * one. Swept to exhaustion over 209 digit strings x 4 names (R8/C2-9).
     *
     * docs/pcre2_compliance.md marks `(*LIMIT_*)` OUT-OF-SCOPE and has since the
     * 2026-08-09 survey: they bound a BACKTRACKING search, pcrec is O(n) by
     * construction, and D22 removes the adversarial-input motivation. So this
     * is a tier-4 construct reproduced to a tier-1 standard — exactly the
     * over-investment D26 exists to stop. It stays because it is already built
     * and passing, not because it earned its keep. */
    PCREC_VERB_LIMIT_ACC_MAX = 429496728,

    /* `\p{...}`/`\P{...}` property names. libpcre2 10.46 normalises the
     * body WHILE SCANNING (space/tab/hyphen/underscore insignificant, ASCII
     * case folded) and counts only SIGNIFICANT characters: 48 compiles or
     * refuses as an unknown name (error 147); 49 is "malformed \P or \p
     * sequence" (error 146), blamed at the scan position immediately after
     * the 49th significant character — NOT at the end of the body, which is
     * how tests/probes/probe_uprops.c proved the count is of significant
     * characters rather than of total body bytes (a body padded with
     * insignificant filler past 100,000 bytes still compiles when it has
     * one significant character). R10 disposition 5 named 48 before this was
     * measured; the probe confirmed it exactly, so this is not a corrected
     * number, only a verified one. Not a contract pcrec owes — an artifact
     * of libpcre2's own build, MOD-0.6's `mod_uprops.c`. */
    PCREC_UPROP_NAME_MAX = 48,

    /* [DD-14 wave G] THE SPLICE SIZE BUDGET, design §6.3 condition 3.
     *
     * A call site whose callee is not in a cycle is emitted INLINE unless the
     * expansion is too big; these are "too big". Both are counted in AST
     * NODES over the callee's region, with a spliced NESTED call contributing
     * its own expansion (`src/opt/callgraph.c`'s `cg_expansion`), so the
     * number a nested chain is judged on is the size it will actually reach.
     *
     * WHY AST NODES AND NOT EMITTED ONES, which is the measurement that would
     * really bound the artifact. Eligibility has to be decided BEFORE the
     * emitter runs, because `src/opt/select_engine.c` reads the linkage to
     * answer "is this pattern VM-only" and "may it carry a prefilter" — a
     * spliced call has an exact finite lowering and a linked one does not
     * (§8.1, §8.3). The emitter's own `Cost` and `vm_charge` numbers do not
     * exist yet at that point, and asking for them would be a second slot
     * census, so this budget is over the one size that IS available. The
     * relationship is not linear — a bounded repeat replicates its body — so
     * PCREC_MAX_VM_NODES remains the hard backstop and this is the knob that
     * keeps ordinary patterns far away from it.
     *
     * WHY A BUDGET AT ALL, given the splice is faster on every row of §6.2's
     * table: the same table measures SPLICE at 298.6 bytes per call site
     * against CALL's 80.1, and that slope is per site — `k` sites to one big
     * callee is `k` copies. The budget is where "faster" stops paying for
     * "bigger", and it is a PERFORMANCE knob in both directions: a declined
     * site is still correct, it just takes the linkage, loses the prefilter
     * and forces the VM.
     *
     * THE NUMBERS. 512 nodes is roughly two of the RFC 5322 email specimen's
     * whole factored patterns, and every callee in that specimen expands to
     * under 20 (docs/design/subroutines_measurements/email_specimen), so the
     * realistic factoring population sits two orders of magnitude below the
     * per-site cap. 8192 total added nodes is 1/16 of PCREC_MAX_VM_NODES,
     * which leaves the replication factor an order of magnitude of room
     * before the backstop is the thing that answers. Neither is measured
     * against a population that exists, because §8.4 measured that population
     * EMPTY; they are stated here so the next reader tunes a number rather
     * than rediscovering a rule. */
    PCREC_MAX_SPLICE_NODES = 512,
    PCREC_MAX_SPLICE_TOTAL = 8192,

    /* [ART-SIZE] THE TWO EMITTED-SIZE CAPS (D84 and its addenda;
     * docs/design/artifact_size_term.md §4). D45's consequence 1 has asked
     * for a compiler-side size bound since 2026-08-15 — "the compile-time
     * bound is the harness-side guard, the size bound is the compiler-side
     * one, and they are different obligations" — and this is it.
     *
     * BOTH ARE IN BYTES OF EMITTED C SOURCE, COMMENT-EXCLUDED
     * (tests/lib/size_count.sh's definition, the quantity
     * docs/dev/artifact_size_log.tsv already logs). The `.o` a user links is
     * ~17 % of that at r = 0.99 (the census's §5), so the numbers below are
     * ~85 KB and ~170 KB of object code — quoted because a limit should read
     * in the unit a user ships.
     *
     * BOTH ARE EMERGENCY FAILSAFES, NOT TUNED THRESHOLDS (D84 addendum 3,
     * Frank: "we can adjust the number but it's really more of an emergency
     * failsafe than a tuning"). A failsafe is judged by whether it fires on
     * the right SHAPES, so centring one in its measured gap is NOT an
     * improvement and the asymmetry below is not a defect: a proposal to move
     * either needs a shape it fires or fails to fire on, not a better ratio.
     * What a failsafe does owe is that nothing legitimate hits it silently —
     * which is the refusal text, docs/spec/limits.md's "Handling an oversized
     * artifact" section, and the ten-axis zero-refusal sweep, not a number.
     *
     * NEITHER IS DENIABLE and BOTH ARE OVERRIDABLE UPWARD (D84 ruling 1):
     * `-fno-size-term` denies the K SELECTION and never reaches a cap — a
     * safety refusal a flag turns off is not one — while
     * `--max-emit-code-bytes=N` / `--max-emit-bytes=N` raise them, and the
     * place a real build does that is the pattern-source file's `config`
     * block, per target, beside the pattern (D84 addendum 3).
     *
     * WHY TWO CAPS AND NOT ONE. They bound different things because the size
     * a user ships and the cost gcc pays are different quantities, MEASURED:
     * a data-table entry costs gcc 0.905 us, a computed-goto jump-table entry
     * 8.7 us, and a VM node 5.37 ms — a node is ~5,930x a table entry. So
     * `a{1,31000}` is a 1,367,865-byte artifact that gcc compiles in 0.34 s
     * (cheap to compile, too large to ship: the TOTAL cap refuses it, the
     * CODE cap does not), while K41's second fuzz witness is 1,220,606 bytes
     * of which 670,650 are CODE and costs gcc 66.92 s at -O2 (both refuse
     * it). One cap would have to get one of those two answers wrong. */

    /* CODE bytes: comment-excluded emitted bytes OUTSIDE table initializers.
     * D45's half. Counted exactly by the emitter as it writes — never
     * modelled, because a refusal must not inherit a fit's error.
     *
     * THE NUMBER (Frank, D84 addendum 2: "then 500k is fine"). It sits in a
     * MEASURED EMPTY BAND: every artifact at or below 283,080 code bytes (the
     * whole 2,487-pattern corpus, worst case) compiles in <= 71 % of D45's
     * 10 s budget, and the next measured artifact up is the K41 witness at
     * 670,650 code bytes and 669 % of it. 500,000 is 1.77x above the first
     * and 1.34x below the second.
     *
     * WHAT IT DOES NOT BOUND, stated because a cap that oversells itself is
     * worse than one that does not: gcc's cost is NOT a function of any count
     * the compiler can produce, and the two K41 witnesses invert the ordering
     * (670,650 code bytes at 66.92 s against 1,718,425 at 55.13 s) because
     * witness 2's prefilter is one function carrying a 3,108-way computed-goto
     * CFG. This is a measured SEPARATION with the cap in an empty band — the
     * shape PCREC_MAX_VM_REPEAT_COPIES above was derived with — not a
     * compile-cost oracle, and the population it cannot speak for is code
     * bytes in (283 KB, 671 KB), empty today. */

    /* TOTAL bytes: the whole comment-excluded artifact. Frank's Q4 half
     * (D84 ruling 2) — "a large byte count makes the artifact unusable" — a
     * concern in its own right and NOT a proxy for compile time. An EXACT
     * post-emission check, refusing before the file is written, with no model
     * on this axis at all (D84 addendum): a fixed number and a loud refusal,
     * so the outcome is predictable by construction rather than by prediction.
     *
     * THE NUMBER. The corpus's largest artifact is 651,412 bytes and the next
     * measured artifact up is `a{1,25000}` at 1,103,865 — a 1.69x gap.
     * 1,000,000 is also what tests/fuzz/fuzz.py's K41_OVERSIZE_BYTES already
     * calls oversize, so the compiler now agrees with its own fuzz gate;
     * that threshold counts RAW `.c` bytes (comments included), so THIS cap
     * is the stricter of the two and an artifact it admits is always one the
     * gate admits. It stays BELOW tests/size/check_size_tripwire.sh's
     * 1,400,000 B pin, so the tripwire remains an INDEPENDENT backstop rather
     * than sharing a constant with the thing it checks. */

    /* [ART-SIZE] The K SELECTION's trigger: the emitted size above which the
     * size term evaluates the unroll ladder at all. Same unit as the caps.
     *
     * It sits in the corpus tail's widest multiplicative gap (1.64x, between
     * 98,596 and 162,034 bytes), so no ordinary emitter or corpus movement
     * flips a pattern across it, and it leaves the term a measured no-op on
     * 2,480 of the corpus's 2,487 compiling patterns (99.72 %).
     *
     * NOT 131,072, which the first draft chose and which would have been a
     * third name for PCREC_MAX_VM_NODES's value — and worse, for
     * PCREC_MAX_VM_REPLICATION_PRODUCT, which is a literal ALIAS of it above.
     * A number that means three unrelated things in two files is how a reader
     * infers a shared derivation that does not exist. */
};

/* [ENG-ABS] THE ANCHORED MATCH-HERE MACHINE'S OWN STATE CEILING, and it is
 * LOWER than the cap every other table machine is built under
 * (docs/design/anchored_match_unwrapped.md §5.2, §8.2).
 *
 * WHY IT IS ITS OWN NUMBER, added at the r41 close (finding S1). The anchored
 * machine is OPTIONAL — an entry point's form, not an engine's requirement —
 * so a pattern whose anchored machine would be enormous should DECLINE the
 * form rather than pay for it, and under `PCREC_MAX_DFA_STATES_TABLE` it did
 * not: r41 measured **+46 % of pcrec's own COMPILE CPU** on `tests/resource`'s
 * giant-repeat shapes (`[a-z]{0,30000}` 23.4 s -> 37.5 s), taking that suite's
 * 45 s `K7_CPU` headroom from 21.6 s to 7.5 s, and pushed one artifact to
 * 1,984,382 B — over `[ART-SIZE.1b]`'s 1,400,000 B pin, and invisible to the
 * tripwire because those shapes live in a bash array rather than in the size
 * log. Both are the SAME fact: the optional machine was charged the mandatory
 * machines' budget.
 *
 * WHERE 4,096 COMES FROM — measured, not chosen, and RE-derived once when the
 * first measurement turned out to be over the wrong population.
 *
 * Over the corpus compiled CAPTURES-ON (825 artifacts select the form) the
 * anchored machine is min 1 / median 2 / p99 67 / max 2,001 (`a{1,2000}`).
 * Over the corpus compiled `--no-captures` — the LARGER population, because a
 * capture-bearing pattern is VM-selected captures-on and never builds an
 * anchored machine at all — 1,213 artifacts select it, median 3, p99 196, and
 * **three exceed 4,096**: `((a)|ab){0,4000}c`, `((a)|ab){4000}c` and
 * `((a)|bc){0,4000}d`, all of `tests/counterk/counterk.rxt`'s 4000-count
 * family. `tests/resource`'s DFA-routed shapes are 20,001, 25,001 and 30,001.
 *
 * So 4,096 is **2.05x the captures-on maximum**, above 1,210 of the 1,213
 * `--no-captures` selectors, and **4.9x below the smallest resource shape**.
 * The three it excludes are 4000-count torture shapes whose `<prefix>_match`
 * no caller optimises for, and excluding them is what keeps the ceiling low
 * enough to be worth having — raising it past them would put it within 1.2x
 * of the resource shapes it exists to exclude.
 *
 * **"NO CORPUS ARTIFACT LOSES THE FORM" WAS THE FIRST DERIVATION'S CLAIM AND
 * IT IS FALSE**; three do. The error was measuring one compile mode and
 * generalising to the tree, and it was caught by
 * `tests/anchored/run_anchored_diff.sh`'s compared population moving 1,213 ->
 * 1,210 rather than by re-reading the derivation.
 *
 * IT IS A CEILING ON STATES, and it inherits `PCREC_MAX_TABLE_ENTRIES`'
 * narrowing for free because `pcrec_build_dfa` applies that to whatever
 * `maxstates` it is handed — so a wide-alphabet anchored machine is bounded
 * by ENTRIES exactly as the mandatory pair is, through the same two lines.
 * That is why this is one more argument to the existing mechanism rather than
 * a second cap beside it.
 *
 * CROSSING IT REFUSES NOTHING. `Dfa.optional` makes the two `intern()` cap
 * sites RECORD and return instead of `ctx_fail`ing, so the compile continues,
 * the artifact keeps the search-and-filter form of its anchored entry and
 * STAMPS that (`<PREFIX>_DFA_MATCH "search-filter"`). The set of patterns
 * pcrec accepts is unchanged in either direction — `docs/spec/limits.md`
 * states that as the second, narrower exception on the three DFA ceilings.
 *
 * IT IS ALSO THE OVERFLOW ARM'S OWN WITNESS SUPPLY. Before this ceiling the
 * arm had ZERO reachable population (the shared caps are hit by the mandatory
 * machines first) and could only be driven by the `-D` override below;
 * `tests/codegen/run_anchored_match.sh` §4a now brackets the ceiling from
 * both sides and compiles one of the three IN-CORPUS overflow patterns, and
 * §4b keeps the override as the control that the arm behaves the same way at
 * a cap no shape reaches.
 *
 * OVERRIDABLE FOR EXACTLY ONE CONSUMER. `run_anchored_match.sh` §4 builds a
 * reference compiler with this lowered to 6 so the arm is exercised on small,
 * fast patterns as well as on the four heavy ones — the same shape and the
 * same single consumer as `-DPCREC_NO_TRIE` and `-DPCREC_NO_ENDVAR`
 * (`src/ir/dfa.c`'s header states the rule); never overridden in a shipped
 * build.
 *
 * IT IS AT THE ACTION. The value is read at the one `pcrec_build_dfa` call
 * that builds the optional machine, not at a flag some other edit could
 * cancel — the placement lesson of the [M6.2] repair slice. */
#ifndef PCREC_ANCHORED_MAX_STATES
#define PCREC_ANCHORED_MAX_STATES 4096
#endif

/* [ART-SIZE] THE TWO EMITTED-SIZE CAPS AND THE SIZE TERM'S THRESHOLD, as
 * `#ifndef`-overridable MACROS rather than enum members.
 *
 * WHY OVERRIDABLE AT BUILD TIME, when the CLI overrides are raise-only.
 * `cap-rescue` — the path where the materiality bar declines a K and a cap
 * takes it anyway — has a NATURAL POPULATION OF ZERO: reaching it needs a
 * pattern whose byte ratio exceeds the bar while some ladder K drops its CODE
 * under the cap, and on replication-dominated patterns bytes and code move
 * together, so a ratio above the bar keeps code above the cap. Five candidate
 * shapes were probed and none reached it. Because the CLI overrides are
 * RAISE-ONLY (deliberately: a raise-only flag cannot be used to manufacture a
 * refusal on someone else's build), the path cannot be forced from outside
 * either — which would leave a shipped branch no test can drive.
 *
 * So the structural check builds a REFERENCE COMPILER with a cap lowered at
 * pcrec's own compile time and drives the branch through it. That is not a new
 * surface: it is [ENG-ABS]'s precedent one lane over, whose overflow arm has
 * the same empty natural population and whose check builds a reference
 * compiler with `-DPCREC_ANCHORED_MAX_STATES=6`.
 *
 * A BUILD-TIME `-D`, NEVER A CLI VALUE. The distinction is the whole point:
 * lowering a cap has to be something a person does to a compiler they built
 * for a test, not something a caller can do to a compile, so the raise-only
 * rule stays true for every user of a shipped pcrec.
 *
 * THE ONE NON-DEFAULT CONSUMER of these three macros is
 * `tests/codegen/run_size_term.sh`. If a second appears, it wants a comment
 * here saying why.
 *
 * MEASURED, so the next reader does not have to re-derive it: with
 * `-DPCREC_MAX_VM_EMIT_CODE_BYTES=40000`, `((a)|ab){0,2047}c` reaches
 * `cap-rescue` — its materiality bar declines K=1 (byte ratio 0.922) and the
 * lowered code cap then takes it anyway. That is the witness the check drives.
 *
 * Units, derivations and the failsafe framing: see the block above and
 * docs/design/artifact_size_term.md §4. */
#ifndef PCREC_MAX_VM_EMIT_CODE_BYTES
#define PCREC_MAX_VM_EMIT_CODE_BYTES 500000
#endif
#ifndef PCREC_MAX_EMIT_BYTES
#define PCREC_MAX_EMIT_BYTES 1000000
#endif
#ifndef PCREC_SIZE_TERM_THRESHOLD
#define PCREC_SIZE_TERM_THRESHOLD 120000
#endif

#endif /* PCREC_LIMITS_H */
