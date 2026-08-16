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
    PCREC_MAX_POSSESS_POSITIONS = 256
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
