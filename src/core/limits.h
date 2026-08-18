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

    /* M2.8 raised this from 20000. It is a MEMORY backstop (48 B/state, two
     * machines, so ~12.6 MB), not the real ceiling: the DFA caps below are
     * grounded in emitter cost (R1 A-3) and now bind first across the
     * realistic keyword range — 6000-word lists compile, 10000-word lists
     * fail on the DFA cap with its actionable "VM engine arrives in M4".
     * Stack depth is no longer a constraint here: clo_visit's tail edges are
     * iterative (verified at -O0 on a 1,000,000-branch alternation). */
    PCREC_MAX_NFA_STATES       = 131072,
    PCREC_MAX_DFA_STATES_GOTO  = 10000,   /* computed-goto attempt engine */
    PCREC_MAX_DFA_STATES_TABLE = 32000,   /* table engine; must fit in short */
    PCREC_MAX_TABLE_ENTRIES    = 2000000, /* states*ncls bound (~12 MB source) */

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
     * narrowing and not only a rescue: exact repeats above roughly `a{9800}`.
     * Those cost 63 s and 154 s at n=20000 and n=30000 today — D45's own
     * standard says a compile needing that much is a failure rather than a slow
     * box — and the refusal is the EXISTING "too complex for the DFA engine"
     * family pointing at the VM, not a new tier (D26). The boundary for this
     * family already existed at 65535, set by the state cap; this moves it, it
     * does not invent it.
     *
     * Same revisit-when as every other budget here: if a LEGITIMATE pattern is
     * measured needing more, raise it WITH the measurement recorded. Note that
     * raising it buys memory quadratically in the repeat count, not linearly. */
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
    PCREC_MAX_GROUP_DEPTH = 250
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
    PCREC_UPROP_NAME_MAX = 48
};

#endif /* PCREC_LIMITS_H */
