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
    PCREC_MAX_TABLE_ENTRIES    = 2000000  /* states*ncls bound (~12 MB source) */
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
