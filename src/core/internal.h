/* Internal shared definitions for the pcrec compiler. Not installed. */
#ifndef PCREC_INTERNAL_H
#define PCREC_INTERNAL_H

#include <setjmp.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "pcrec.h"
/* Every number that decides what pcrec accepts, rejects or promises, with its
 * provenance — ours, PCRE2 syntax, or a PCRE2 internal (D26). */
#include "core/limits.h"

/* [M4.7b/K7] The compile context, named early so the two allocators below can
 * carry a back-pointer to it. THAT back-pointer is the whole mechanism behind
 * K7's second half: pcrec is a LIBRARY, and an allocator that calls abort() on
 * a failed malloc kills the caller's process — the worst failure on K7's list,
 * and the one a caller who set a memory limit was specifically trying to avoid.
 * With a Ctx in reach, every allocation failure on the compile path becomes an
 * ordinary ctx_fail (longjmp to compile_driver's setjmp, job_cleanup, return
 * -1 with a diagnostic) instead. See ctx_nomem() below. */
typedef struct Ctx Ctx;

/* [M6.2 wave A] The scoped inline-option state, INCOMPLETE ON PURPOSE — see
 * `Ctx.mods` and src/parse/parse_mods.h. */
typedef struct ParseMods ParseMods;

/* ---- arena allocator (all AST/IR memory; freed wholesale) ---- */

typedef struct ABlock {
    struct ABlock *next;
    size_t used, cap;
    char mem[];
} ABlock;

/* `cx` is the owning compile, or NULL for an arena with no error channel to
 * report through (there are none today; every Arena is a Ctx's own). */
typedef struct { ABlock *head; Ctx *cx; } Arena;

void *arena_alloc(Arena *a, size_t sz);   /* zeroed, 16-aligned */
void  arena_free(Arena *a);

/* ---- growable string buffer (codegen output) ---- */

/* `cx` is the owning compile, or NULL — and unlike Arena, NULL is a REAL case
 * here: src/parse/syntax_dump.c builds `--features`/syntax-query text in bare
 * `StrBuf sb = {0}` locals that belong to no compile and have no pcrec_error to
 * fill, so an allocation failure there has nowhere to be reported and keeps the
 * abort. Attaching a Ctx is what upgrades a buffer from "abort" to "diagnose". */
/* [ART-SIZE] `abort_over` is the SIZE TERM's early-abort bound (D84;
 * docs/design/artifact_size_term.md §2.2c), and it is a COST guard, never a
 * cap decision. Nonzero only during a LADDER attempt: the ladder is measuring
 * what K produces, and without a bound the worst rung writes tens of MB before
 * anyone learns it is the worst (measured: a 6-deep `{17}` tower emits 35.5 MB
 * at K=6 while K=1 answers in 42,619). When `len` passes it the attempt
 * `ctx_fail`s, the driver records that K as out, and the next K starts with a
 * fresh arena. The DEFAULT and FINAL attempts leave it 0 and always run to
 * completion, because their figures are what a refusal quotes. */
typedef struct { char *p; size_t len, cap; Ctx *cx; size_t abort_over; } StrBuf;

void  sb_putc(StrBuf *sb, char c);
void  sb_puts(StrBuf *sb, const char *s);
void  sb_printf(StrBuf *sb, const char *fmt, ...)
      __attribute__((format(printf, 2, 3)));
char *sb_take(StrBuf *sb);                /* transfer ownership, resets sb */
void  sb_free(StrBuf *sb);

/* ---- AST ---- */

/* [M6.4.2 / SR-8] Forward declaration: `Ast.reg` (below) points at the
 * registry row whose producer built the node. The full definition is far
 * down this file; the AST only ever holds the pointer. */
typedef struct RegRow RegRow;

typedef enum {
    A_CLASS,   /* byte class (literals normalized to singleton classes) */
    A_CAT,     /* l r */
    A_ALT,     /* l | r  (l is preferred branch) */
    A_REP,     /* l{rmin,rmax}, rmax == -1 for unbounded; greedy flag */
    A_EMPTY,   /* matches empty string */
    A_BOL,     /* ^ and \A : start of subject */
    A_EOL,     /* $ and \Z : end of subject or before a final \n */
    /* [M6.2 wave A] `\z` — end of subject, FULL STOP. A distinct KIND rather
     * than a flag on A_EOL, and the two spellings are not interchangeable
     * here: D62's principle is that node KINDS encode STRUCTURE and node
     * FIELDS encode PARSE-RESOLVED MODIFIER STATE. `\z` is not a modifier
     * variant of `$` — no option turns one into the other, `\Z` really IS
     * A_EOL (an exact alias, assertions_design.md §3.2), and the position
     * sets differ permanently: `$`/`\Z` hold at `n` AND at `n-1` before a
     * final newline, `\z` only at `n`. So it is structure, it gets a kind,
     * and mrl.c:18-24's exhaustive-switch-no-default rule earns its keep:
     * adding this member is a compile error at every analysis that must
     * decide about it. */
    A_END,
    /* [M6.2 wave B] `\b` and `\B` — the WORD BOUNDARY assertions. Two kinds
     * rather than one kind plus a negation flag, on the same D62 principle
     * `\z` was ruled by: `\B` is not `\b` under a modifier, it is the
     * complementary position set, and no option turns one into the other.
     *
     * They are the module's first CONTEXT assertions: unlike `\A`/`\Z`/`\z`,
     * whose truth is a function of the position alone, these read the byte on
     * EACH SIDE of the position. That is what costs an alphabet refinement
     * (assertions_design.md §3.4), a bit of DFA state identity (§3.5) and a
     * class-indexed accept (§3.6) — see src/ir/dfa.c. */
    A_WORDB,
    A_NWORDB,
    /* [M6.2 wave D] `\G` — the FIRST MATCHING POSITION, i.e. the `startpos`
     * the match call was given (`docs/spec/match_api.md` §3.1;
     * assertions_design.md §4). A third kind on D62's principle, and the
     * cleanest instance of it in the module: `\G` is not `\A` under an
     * option, it is a test against a RUNTIME value where `\A`'s is the
     * compile-time constant 0. The two coincide only when `startpos == 0`,
     * which is why a pattern that confuses them passes every test written at
     * the default startpos — the whole reason this module's corpus carries
     * `ms`/`ns` cells.
     *
     * Zero-width and NOT REPEATABLE, measured against libpcre2 10.46 by this
     * wave: `\G*` `\G+` `\G?` `\G{2}` `a\G*` are all error 109 and `(\G)*`
     * compiles to (0,0) — `\A`/`\z`/`\b`'s shape exactly, so this kind joins
     * parse.c's existing rejection and group-wrap sites rather than earning a
     * rule of its own. `[\G]` is error 107, so the row keeps
     * RF_CLASS_INVALID.
     *
     * `Ast.u.anch.multiline` is meaningless here and is never read: `\G` is an
     * absolute position test like `\A`/`\z`, unaffected by every option. */
    A_GSTART,
    /* [M6.2 wave E] `\K` — RESET THE REPORTED START of the match to here
     * (assertions_design.md §6). The module's last construct, and the only
     * one that is not an assertion at all: every other kind in this block
     * answers a QUESTION about the position and can fail; this one always
     * succeeds, consumes nothing, and has a SIDE EFFECT.
     *
     * THAT IS WHY IT IS VM-ONLY, and the reason is narrower than the phrase
     * "the DFA cannot do it" suggests (R30 E7). The reported start it writes
     * is a property of the WINNING PATH, and pcrec's DFA state is a
     * priority-ordered SET of NFA states which does not carry the path. A
     * tagged DFA (Laurikari) recovers exactly such positions with registers
     * on transitions; pcrec's is not one and this wave does not propose
     * making it one, so the door is closed BY CHOICE and is recorded as such
     * rather than as a theorem. `src/parse/registry.c`'s row has said
     * `VM_ONLY` since before there was a producer; `src/opt/select_engine.c`
     * is where that finally has teeth.
     *
     * ITS EFFECT ON THE LANGUAGE IS NOTHING, and that is load-bearing twice
     * over: `src/ir/nfa.c` lowers it to N_EPS, so the capture-erased
     * prefilter DFA built for `a\Kb` is the machine `ab` builds, and the
     * prefilter's span start — the PRE-`\K` start — is exactly what the
     * hybrid needs to bound the search with (§6.3 rule 1).
     *
     * Zero-width and NOT REPEATABLE, measured against libpcre2 10.46 by this
     * wave: `\K*` `\K+` `\K?` `\K{2}` `a\K*` are all error 109 and `(\K)*`
     * compiles to (0,0) — `\A`/`\z`/`\b`/`\G`'s shape exactly, so this kind
     * joins `pcrec_is_bare_anchor` rather than earning a rule of its own.
     * `[\K]` is error 107, so the registry row keeps RF_CLASS_INVALID.
     *
     * `Ast.u.anch.multiline` is meaningless here and is never read. */
    A_KRESET,
    /* [M4.5b] capturing group `(l)`, group number in `capno`.
     *
     * D31 ruled the group erasure STAYS, on a MEASURED compile-time cost, and
     * engine_m4.md §11.3 records that the VM nonetheless needs SOME node to
     * know where to emit a capture write. Both hold at once because this node
     * is BORN ONLY WHEN CAPTURES ARE REQUESTED (`Ctx.want_caps`, i.e. neither
     * --no-captures nor a capture-free pattern) and because every consumer
     * other than the VM emitter treats it as TRANSPARENT — see ast_bare() in
     * src/ir/nfa.c. So:
     *   - a capture-free pattern's AST is byte-identical to D31's, always;
     *   - `--no-captures` reproduces D31's AST for ANY pattern;
     *   - the prefilter NFA/DFA built for a capture pattern is the SAME
     *     machine the capture-ERASED pattern builds (engine_m4.md §6.1's
     *     STRUCTURAL erasure half, preserved by construction rather than by a
     *     second lowering — §11.3's "two lowerings from one parse" mitigation,
     *     obtained without copying the tree).
     * That is also what makes §5.4's byte-identity gate hold by construction
     * instead of by inspection. */
    A_CAP,
    /* [M6.4.2] `(?>X)` — the ATOMIC GROUP, and the possessive quantifier
     * suffixes `X*+ X++ X?+ X{n,m}+`, which parse to `A_ATOMIC(A_REP(X))`
     * (PCRE2's own definition; atomic_groups_design.md §3.2 RULE 1, measured
     * on 18 spelling pairs / 47 cells including 28 whose iteration can end in
     * two places).
     *
     * A KIND AND NOT A FIELD, on D62's own principle — node KINDS encode
     * STRUCTURE, node FIELDS encode parse-resolved MODIFIER STATE. Atomicity
     * is not a modifier: it changes the LANGUAGE (`(?>a*)a` matches nothing
     * where `a*a` matches), it changes the BACKTRACKING (choice points that
     * would have been retried are discarded), and it BRACKETS a body. Two
     * further supports, both measured by the design lane:
     *
     *   - `src/opt/revdet.c:226`'s `rd_node` CLEARS `Ast.u.rep.possessive` on the
     *     reversed copy the emitter walks, so a module that stored its
     *     semantics in that field would have them silently deleted on a
     *     revdet-approved body (design §6.5). A kind survives the copy.
     *   - adding an `AKind` produces FIFTEEN `-Wswitch` diagnostics across six
     *     files, each one a pass that must say what it does with an atomic
     *     group; adding a struct FIELD produces zero
     *     (`assertions_measurements/probes/probe_wswitch_alarm.sh`, re-run).
     *
     * IT IS A CUT, and the cut is the whole semantics: at the moment the body
     * first succeeds, every choice point the body created is discarded, so the
     * group can never be re-run with a different answer. The VM already had
     * that operation — `vm_cut`, built for [ENG-BREP]'s possessification — and
     * this kind needs no new VM primitive, because the no-trail-rewind
     * invariant `vm_cut` relies on is INDEPENDENT of the §2.2 proof that
     * licenses today's cuts (design §3.1, CUT-INV).
     *
     * `l` is the body; `r` is unused. `Ast.u.rep.possessive` is NEVER written for
     * this construct (design §3.2 RULE 2): that field keeps its meaning as
     * possessify's deniable optimisation mark, so `-fno-possessify` cannot
     * become a miscompiler and a copy constructor cannot delete a language
     * feature. The emitter's "is this A_REP under an atomic lift" question is
     * THREADED context (`vm_cuts(a, under_atomic)`), never a stored flag —
     * D67's corollary, because a flag describing a parent the free discharge
     * deleted goes stale.
     *
     * VM-ONLY, per its registry row's mask, and the `engines`/`reg` stamp
     * below is how that reaches src/opt/select_engine.c. A DFA cannot
     * implement it: subset construction keeps every alternative alive, which
     * is exactly the NON-atomic semantics, so `src/ir/nfa.c` lowers the body
     * TRANSPARENTLY and the capture-erased prefilter answers for the UNCUT
     * language — a strict superset. That is sound for the prefilter's
     * rejection and its span START and NOT for its span END, which is why
     * `src/gen/emit_vm.c`'s MRL ceiling is switched off on a cut-bearing
     * artifact (design §4, 114 measured cells of silent match loss without
     * it). The full cut construction (Berglund et al.) is CHARTERED for the
     * `[ENG-CUT]` plan row, not built. */
    A_ATOMIC,
    /* [M6.5.2] A BACKREFERENCE — `\1`, `\g{-1}`, `\k<name>`, `(?P=name)`.
     * Compare the subject at the cursor against the text some earlier group
     * captured, AT THIS INSTANT of the backtracking state
     * (docs/design/backrefs_design.md §3).
     *
     * A KIND AND NOT A FLAG ON `A_CLASS`, on D62's own principle: node KINDS
     * encode STRUCTURE. Everything else pcrec compiles is a 256-bit bitmap or
     * a position predicate; a backreference is neither. It consumes a VARIABLE
     * number of bytes decided at MATCH time, which no `A_CLASS` can express,
     * and it is the reason this module needs a new emitted operation and the
     * encoding seam's SECOND residual entry (design §4).
     *
     * `refs`/`nrefs`/`caseless` below are its payload; `l` and `r` are unused.
     *
     * ITS MINIMUM WIDTH IS 0 and `src/opt/mrl.c` already said so before this
     * kind existed ("Lookaround, backreferences and `(*ATOMIC)` have no
     * producers today; when they gain one, each contributes 0 here until
     * someone measures otherwise"). A referenced group can publish an EMPTY
     * capture, so 0 is exact rather than conservative — and `vm_nullable` must
     * answer TRUE for the same reason, or a nullable quantifier body loses its
     * empty-iteration guard and the artifact hangs (design §3.2 property 5).
     *
     * VM-ONLY, per the twelve registry rows that produce it, and the
     * `engines`/`reg` stamp above is how that reaches
     * `src/opt/select_engine.c`. A DFA cannot implement it at all: a
     * backreference is not a regular construct, and the capture-erased
     * approximation APPROACH §2 names is not even a sound SUPERSET once the
     * referenced group holds an assertion or an atomic/possessive operator
     * (design §7.2, measured). That is why a backref-bearing pattern gets NO
     * prefilter — `EngineFit.prefilter` is forced false — rather than a
     * filtered one. */
    A_BREF,
    /* [M6.6.2] `(?=X)` `(?!X)` `(?<=X)` `(?<!X)` and their non-atomic
     * spellings `(?*X)` `(?<*X)` `(*napla:X)` `(*naplb:X)` — A LOOKAROUND:
     * run the body as a SUB-MATCH, keep the VERDICT and throw the POSITION
     * away (docs/design/lookaround_design.md §3.1).
     *
     * ONE KIND AND NOT FOUR (or eight), design §3.1(a). The measured argument
     * for a kind over a flag is `assertions_design.md`'s — a new AKind
     * enumerator raises a build diagnostic where a struct field raises none —
     * and that argument says AT LEAST one kind, not four. Four would put three
     * of them at the mercy of a `case` written for the first, which is the
     * failure the alarm exists to prevent, one level in. So: one kind, and
     * D62's own principle governs the rest — node KINDS encode structure, node
     * FIELDS encode parse-resolved state. The measured budget for THIS
     * enumerator was taken before it was added: 23 `-Wswitch` sites in 10
     * files ([M6.6.2] wave A's dummy-enumerator run, which counted 24 with
     * `pcrec_maxw`'s own new arm included).
     *
     * `l` is the body; `r` is unused. The payload is `u.look` below, and D62
     * control 3's obligation comes WITH those fields: an analysis that
     * pattern-matches `case A_LOOK:` and does not read `.neg` reproduces
     * possessify.c's pre-D62 bug and no compiler diagnostic will say so.
     * Design §9.3 makes that three sabotage rows rather than a comment.
     *
     * ITS MINIMUM AND MAXIMUM WIDTH ARE BOTH 0, and 0 BECAUSE IT WAS CHECKED
     * rather than because it was inherited (design §3.1(d)). A LOOKAHEAD
     * inspects bytes ahead of the cursor and consumes none; a LOOKBEHIND's
     * bytes are BEHIND the cursor, and `pcrec_minw`/`pcrec_maxw` count bytes
     * still to be CONSUMED. `vm_nullable` must answer TRUE for the same fact,
     * or a quantified lookaround loses its empty-iteration guard — and design
     * §2.6 measured that quantified lookaround SHIPS (all fourteen forms
     * compile in both oracles, and the empty-iteration cells terminate).
     *
     * VM-ONLY, per the six registry rows that produce it, and the
     * `engines`/`reg` stamp below is how that reaches
     * `src/opt/select_engine.c`. A DFA cannot implement it today: `src/ir/nfa.c`
     * lowers it to an EPSILON, i.e. the prefilter is built from the
     * lookaround-ERASED pattern, which is a sound SUPERSET (design §5.3:
     * L(P) is a subset of L(erase(P)) at every position) — sound for the
     * prefilter's rejection and its span START, and NOT for its span END,
     * which is why the MRL window ceiling is dropped on a lookaround-bearing
     * artifact exactly as it is on a cut-bearing one (design §5.6). The
     * general DFA construction is CHARTERED as `[ENG-LOOK]`, not built, and
     * design §5.7 records Frank's ruling that NO one-character fold ships
     * anywhere in the meantime. */
    A_LOOK,
    /* [DD-14] `(?1)` `(?+2)` `(?-1)` `(?0)` `(?R)` `(?&name)` `(?P>name)`
     * `\g<1>` `\g'1'` `\g<name>` — A SUBROUTINE CALL: run another group's
     * pattern here, and put the capture state back on the way out
     * (docs/design/subroutines_design.md §4.1).
     *
     * ONE KIND FOR ALL TEN SPELLINGS (design §4.1(a)). The spelling is not a
     * semantic difference: §2.1's discriminator — does the construct RE-RUN
     * the group's pattern, or compare against the TEXT it captured — is the
     * same for all ten, §2.3's relative forms compute to an absolute number
     * inside the port, and §2.4's zero family is just `target == 0`.
     * `Ast.reg` (above) already carries the producing `RegRow` for the
     * diagnostics and for D65, so the spelling is recoverable without a
     * field of its own.
     *
     * IT IS NOT A_BREF, AND THE FIELD THAT WOULD HAVE BEEN SHARED IS THE
     * TELL. `A_BREF.u.bref.refs[]` is a SET because a *reference* to a
     * duplicated name resolves at MATCH time to the first member that is
     * set; a CALL to a duplicated name runs the FIRST DECLARATION,
     * statically, and never retries into the run (design §3.4(c),
     * MEASURED on 10.46). Reusing `refs[]` here would make one field mean
     * two things and would invite an emitter to write the else-if chain
     * `backrefs_design.md` §8.3 designed for the other construct.
     *
     * `l` AND `r` ARE BOTH UNUSED. The callee is NOT a child: it is
     * `u.call.body`, a pointer to a subtree that lives at its own lexical
     * position elsewhere in the same tree. THAT MAKES IT THE AST'S FIRST
     * `Ast*` -> `Ast*` BACK EDGE, and design §4.4 states the rule every
     * walker in this compiler now lives under:
     *
     *     A WHOLE-TREE PREDICATE MUST NOT FOLLOW `.body`.
     *
     * It already visits the callee at the callee's own lexical position, so
     * following the edge is REDUNDANT as well as NON-TERMINATING — on
     * `(a(?1))` a bare `const Ast *` walker with no visited set recurses for
     * ever and HANGS THE COMPILER, which no answer-comparison test can
     * detect because there is no answer. A SUBTREE-RELATIVE analysis, one
     * whose answer for a call genuinely is the callee's, goes through
     * `src/opt/callgraph.c`'s memoised SCC fixpoint instead (§4.4a).
     *
     * ITS MINIMUM WIDTH IS THE CALLEE'S, and that is a FIXPOINT, not a
     * recursion: design §4.4b's Kleene iteration from infinity downward over
     * the SCC condensation, with `minw == infinity` meaning "this callee
     * matches nothing", which is a LEGAL compile (`^(a(?1)b)$` compiles on
     * 10.46 and matches nothing). `vm_nullable` is the same shape with cycle
     * bottom `false` (§2.6), and both live in `callgraph.c` because a bare
     * `const Ast *` signature cannot express a fixpoint.
     *
     * A CALL TARGET MUST JOIN THE MARKED SET (design §4.3): a call names a
     * group exactly as a reference does, so `pcrec_bref_mark` marks
     * `u.call.target` or `--no-captures` deletes group 1's `A_CAP` out from
     * under `(a)(?1)`. The mark is NOT transitive and needs no fixpoint —
     * a call from inside group 1 to group 3 is an `A_CALL` NODE IN THE TREE,
     * so the whole-tree walk reaches it wherever it sits.
     *
     * VM-ONLY (design §8.1). A DFA cannot implement it: a subroutine call is
     * not a regular construct once it is recursive, and `src/ir/nfa.c`'s
     * capture-erased approximation is NOT even a sound superset here
     * (§8.2), which is why a call-bearing pattern gets NO prefilter rather
     * than a filtered one — wave E's one line in `src/opt/select_engine.c`.
     * Wave G revisits `nfa.c` with §8.3's bounded approximation.
     *
     * D62 CONTROL 3'S OBLIGATION COMES WITH THE PAYLOAD (`u.call` below):
     * an analysis that pattern-matches `case A_CALL:` and does not read
     * `.body` treats a call as an OPAQUE ZERO-WIDTH ATOM — which is SOUND
     * for a decline and WRONG for a descent. Design §9.3 makes that three
     * sabotage rows rather than a comment. */
    A_CALL
} AKind;

/* [DD-14] HOW AN `A_CALL`'s CALLEE REACHES THE ARTIFACT (design §6.2/§6.3).
 * DECIDED BY `src/opt/callgraph.c` FROM THE SCC CONDENSATION, never by the
 * parser: the parser does not have the graph, and "is the target in a cycle"
 * is the eligibility question.
 *
 * The two are NOT two spellings of one lowering — design §6.1 measured that
 * "emit the body once with two linkages" collapses when it is written out —
 * so a pattern may carry both, node by node, and §9.2's SPLICE-vs-LINKAGE
 * `A == B` control over the whole corpus is what holds them to one language. */
typedef enum {
    /* INLINE THE CALLEE'S SUBTREE AT THE CALL SITE. Only legal when the
     * target is NOT in a cycle with this call (a spliced recursive call is
     * an infinite emitter) and the size budget allows it. Wave G. */
    CALL_SPLICE,
    /* EMIT THE CALLEE ONCE AS AN ADDRESSABLE REGION AND JUMP TO IT, with the
     * return label in the RESUME FRAME (§5.1: the frame IS the call record —
     * §5.2 derives, and §5.9's prototype REPRODUCES, the clobber bug a
     * separate `call_stack[]` array has). The default and the only linkage
     * that can express recursion. Wave B+C. */
    CALL_LINKAGE
} CallLink;

typedef struct Ast Ast;
struct Ast {
    /* ---- COMMON FIELDS ----------------------------------------------------
     *
     * [D70] Everything here is read or written for structurally UNRELATED
     * kinds, measured by the migration survey (src/core/CLAUDE.md, "The D70
     * ownership survey"). A field belongs here only because the survey put it
     * here; the default home for anything per-kind is the union below. */
    AKind    k;
    Ast     *l, *r;

    /* NOT A REPEATABLE ITEM (R20/SPEC-1). PCRE2 error 109's other half: a
     * quantifier after this node is an error rather than a repetition of it.
     * It cannot be derived from `k`, which is the whole reason it is a field
     * — a bare option run produces A_EMPTY, and A_EMPTY is ORDINARILY
     * quantifiable (`()*` and `(a|)*` both compile in libpcre2, measured).
     * The arena zeroes, so every node that does not say otherwise is
     * repeatable, which is the safe default.
     *
     * WHY IT IS NOT "produces no atom": the genuinely-lexical constructs
     * produce no atom either and are TRANSPARENT — libpcre2 compiles
     * `a\Q\E*` and `a(?#c)*`, letting the quantifier reach back to the `a`.
     * A bare option run does not: `a(?i)*` is err 109 at the quantifier.
     * That measured boundary is what this flag marks, and both sides of it
     * are pinned in tests/reject/.
     *
     * [D70] CROSS-KIND, so it stays common. It is WRITTEN on A_EMPTY (a bare
     * option run, src/parse/mod_modifiers.c) and PROPAGATED onto A_CAP and
     * A_ATOMIC from their bodies (src/parse/parse.c, mod_named_groups.c,
     * mod_atomic_groups.c), and it is READ off an atom of ANY kind by
     * src/parse/parse.c's quantifier check. No union member could hold it. */
    bool     not_repeatable;

    /* [M6.4.2 / SR-8, D67] THE PRODUCING ROW — the registry row whose port
     * built this node, or NULL for every node the BASE grammar built.
     *
     * D67's shape is "every AST node produced by an RS_MODULE row carries its
     * row's `engines` mask, STAMPED BY THE PRODUCER at construction", and this
     * is that stamp spelled as a POINTER TO THE ROW rather than as a copy of
     * the mask, for the reason this whole registry exists (D24): a copied mask
     * is a SECOND HOME for a registry fact, and the two can drift. The row is
     * also where `why`'s TEXT has to come from — D67 says `why_pos`/`why` come
     * from "the first DFA-excluding node's ROW" — so a mask alone would have
     * needed a second stamp beside it anyway. `pcrec_ast_engines()` below is
     * the one reader, and it is the only thing that may interpret this field.
     *
     * NULL MEANS ANY_ENGINE, which is D67 contract note 2's requirement that a
     * FORGOTTEN STAMP FAIL IN THE UNSOUND DIRECTION: the arena zeroes, so a
     * producer that forgets to stamp yields a node claiming both engines, and
     * what catches that is the generic tripwire in
     * tests/registry/registry_check.c (every VM_ONLY row with a producer must
     * refuse `--engine=dfa` by name), not a lucky default.
     *
     * A DISCHARGE MUST NOT LET ITS OUTPUT INHERIT THE DISCHARGED NODE'S STAMP
     * (D67 contract note 3): the discharged node is not copied, its
     * replacement's NEW nodes are born NULL/ANY_ENGINE, and nodes copied from
     * the body keep their own stamps — copying a `\K` must keep forcing. The
     * free discharge (src/opt/atomic.c) is deletion-shaped and satisfies this
     * trivially; `[ENG-CUT]` inherits the rule. Sabotage row S97. */
    const RegRow *reg;

    /* ---- [D70] THE PER-KIND PAYLOAD UNION ---------------------------------
     *
     * D70 (Frank, 2026-08-23): the per-kind fields — existing AND new — live
     * in a TAGGED UNION of per-kind payload structs, keyed by `k` above.
     * `n->u.rep.rmin` carries its ownership in its name, and the accretion of
     * one more top-level field per new module stops here.
     *
     * THE RULE, and it is the decision's operative clause: NO MODULE MAY ADD A
     * NEW TOP-LEVEL PER-KIND FIELD. A new kind adds a union MEMBER. A field
     * joins the common block above only when a survey MEASURES it cross-kind,
     * and the survey is recorded (src/core/CLAUDE.md) so the next author
     * inherits the measurement rather than repeating the guess.
     *
     * IT IS NOT A CHECKING MECHANISM. C does not police union member access:
     * reading `u.rep.rmin` on an A_CLASS node compiles, and hands you class
     * bitmap bytes. The union buys READING and CONTAINMENT, not enforcement,
     * so D62's discipline governs exactly as before — parse-resolved state,
     * per-field comments, per-field sabotage rows.
     *
     * THE DISCIPLINE THE UNION ADDS, and it is the one rule a writer must
     * carry: A WRITER MAY TOUCH `u.<payload>` ONLY UNDER A KIND CHECK THAT
     * OWNS IT, and a GENERIC COPY OR SANITISE HELPER — one that runs for
     * kinds it does not enumerate — MUST GUARD rather than write
     * unconditionally. The reason is measured rather than stylistic: the D70
     * migration survey found exactly two unconditional per-kind writes on
     * generic paths, and both are now kind-guarded.
     *
     *   - `src/opt/revdet.c`'s `rd_node` cleared A_REP's `revbody`/
     *     `possessive` on EVERY kind it copies. Through `u.rep` that lands on
     *     `u.cls.bits` — `possessive` at `+49` is bitmap byte 9 (`0x48`-`0x4F`)
     *     and `revbody` at `+56..+63` is bitmap bytes 16-23 (`0x80`-`0xBF`) —
     *     so a reversed A_CLASS node loses those bytes. MEASURED on the
     *     unguarded build: the backward walk's class tests become an all-zero
     *     bitmap and the LAST ITERATION'S CAPTURES come back UNSET
     *     (`((H)|I){3}J` on "HHHJ" reports groups unset where both oracles
     *     give (2,3)(2,3)), with the whole-match span unchanged — which is
     *     why only a capture-aware check sees it.
     *   - `src/parse/mod_assertions.c`'s multiline pin ran for all eight of
     *     that port's kinds, harmless only because five of them have no
     *     payload YET.
     *
     * Before the union both writes were merely DEAD; after it, the first is a
     * clobber and the second is a clobber waiting for its payload.
     *
     * THE ARENA ZEROES THE WHOLE ALLOCATION, union included, so every "the
     * arena zeroes, so ..." argument in the comments below still holds
     * verbatim: a node nothing wrote reads as all-zero through whichever
     * member its kind selects. */
    union {
        /* A_CLASS: 256-bit membership bitmap. `cls_set`/`cls_has` below take
         * the array, so they are unchanged by D70. */
        struct { uint8_t bits[32]; } cls;

        /* A_REP: `l{rmin,rmax}`, rmax == -1 for unbounded. */
        struct {
            int         rmin, rmax;
            bool        greedy;
            /* [ENG-BREP] POSSESSIFIED (A_REP only). Set by src/opt/possessify.c when
             * the eng_brep_design.md §2.2 rule proves that no retreat into this loop
             * can ever produce a match the PREFERRED path does not, so the emitter
             * owes it no resume frames and no giveback.
             *
             * IT IS AN ANNOTATION, NOT A SPELLING. `a{2,4}` and a possessified
             * `a{2,4}` match the same strings by construction — that is the whole
             * claim — so every consumer other than src/gen/emit_vm.c ignores this
             * field, exactly as they ignore A_CAP. In particular src/ir/nfa.c lowers
             * A_REP by replication regardless (§2.8), which is why the prefilter DFA
             * is unchanged and why possessification is a run-time and emitted-size
             * win rather than a compiler-time one.
             *
             * The arena zeroes, so a node nothing analysed keeps its machinery — the
             * sound default, and the reason `-fno-possessify` is byte-identity-safe:
             * denying the pass leaves every node in the state it was born in. */
            bool        possessive;
            /* [ENG-BREP] REVERSE-DETERMINISTIC (A_REP only). Set by src/opt/revdet.c to
             * the body's REVERSED AST when engine_m4.md §2.5's rung applies, and left
             * NULL otherwise — so this one field is BOTH the verdict and the artifact
             * the emitter needs, and the three sites that must agree about the rung
             * (vm_cost_rep, vm_count_slots, vm_rep) read one field instead of each
             * re-deciding. Ast.u.rep.possessive's precedent, one rung down.
             *
             * The reversed body is what the emitted backward walk matches: it recovers
             * the previous iteration boundary for a retreat and, per §3.4's corrected
             * derivation, the LAST iteration's captures. Reversal is A_CAT children
             * swapped, recursively; every other node kind reverses to itself.
             *
             * Same annotation-not-a-spelling rule as `possessive`: it changes the
             * emitted machinery and never what the quantifier matches, so every
             * consumer other than src/gen/emit_vm.c ignores it. The arena zeroes, so a
             * node nothing analysed keeps its machinery, which is what makes
             * `-fno-revdet` byte-identity-safe. */
            const Ast  *revbody;
        } rep;

        /* A_CAP: 1-based capturing group number. */
        struct { int no; } cap;

        /* A_BOL and A_EOL — a CLOSED FAMILY sharing one meaning, so they share
         * one payload rather than getting a member each (D70's family rule).
         * src/parse/mod_assertions.c also pins this member false on A_END,
         * A_WORDB, A_NWORDB, A_GSTART and A_KRESET; those kinds have no payload
         * of their own, so that write aliases nothing and is read back
         * nowhere — see the survey in src/core/CLAUDE.md. */
        struct {
            /* [M6.2 wave A] MULTILINE, resolved AT PARSE TIME (A_BOL / A_EOL only).
             * D62: node fields encode parse-resolved modifier state, exactly as
             * `greedy` above encodes `(?U)`'s — set from the scoped `(?m)` state in
             * force AT THE `^`/`$` ITSELF, never re-derived downstream.
             *
             * ANY ANALYSIS THAT EXEMPTS OR SPECIAL-CASES `$` (or `^`) MUST CONSULT
             * THIS FIELD. That sentence is D62's control 3 and it is load-bearing,
             * not decoration: src/opt/possessify.c exempts `$` from the follow-set
             * widening on an upward-closure argument that COLLAPSES PER LINE under
             * `(?m)`, and before this field existed that analysis read the parser's
             * END-OF-PATTERN option state — so `(?m:a{0,4}$)` and `(?m)a{0,4}$(?-m)`
             * would each have exempted a multiline `$` and lost a match
             * (assertions_design.md §8.1.1, two measured miscompile cells). A new
             * analysis that pattern-matches `case A_EOL:` and does not read
             * `.multiline` reproduces exactly that bug, and no compiler diagnostic
             * will tell you: that residual is D62's accepted cost, and this comment
             * is the thing that covers it.
             *
             * [M6.2 wave C] THE FIELD IS LIVE, and D62 control 3's obligation was
             * DISCHARGED BY INSPECTION over every AST-walking analysis, with the
             * verdict recorded here rather than in five places nobody re-reads. §8.3
             * names four sites as the residual the flag spelling cannot cover — the
             * `Ast.k` switches carrying a `default:` arm, `src/gen/emit_vm.c` x3 and
             * `src/opt/revdet.c` x1 — and the inspection is that NONE of them needs
             * the flag, for one reason with three shapes:
             *
             *   - `vm_det_seq` (emit_vm.c) DECLINES on the kind: a `$` of either
             *     spelling is zero-width, so "scan ahead by stride" is wrong for
             *     both, and its `default: return 0` is right without reading a field.
             *   - `vm_cap_offsets` and `vm_rev_emit` (emit_vm.c) are UNREACHABLE for
             *     either spelling: both run only on bodies `vm_det_seq` and
             *     `src/opt/revdet.c`'s `rd_shape` already approved, and `rd_shape`
             *     declines every `A_BOL`/`A_EOL`.
             *   - `pcrec_revdet_first` (revdet.c) WIDENS to all bytes, the sound
             *     direction, which makes the disjointness test fail and the
             *     quantifier keep its machinery.
             *
             * THE PATTERN WORTH CARRYING FORWARD: an analysis is at risk exactly when
             * it treats `$` as TRANSPARENT — reasoning about WHERE it is true and
             * concluding it may be skipped over. Every one of these four treats it as
             * OPAQUE (decline, widen, or unreachable), and opacity is multiline-blind
             * by construction. `src/opt/possessify.c` was the one transparent
             * consumer in the tree and is the one this field exists for.
             *
             * The arena zeroes, so a node nothing set is non-multiline. */
            bool multiline;
        } anch;

        /* A_BREF: the backreference payload. */
        struct {
            /* [M6.5.2] A_BREF ONLY — the CANDIDATE GROUP NUMBERS, ascending, and how
             * many. Filled by the END-OF-PARSE resolution pass (design §5.3), which is
             * the one site that knows both the whole-pattern group count and every
             * declaration of a duplicated name.
             *
             * A SET EVEN WHEN IT HAS ONE ELEMENT, deliberately. A reference to a
             * DUPLICATED name (`(?J)`, design §8) resolves at MATCH time against a run
             * of groups whose numbers are not contiguous — `(?J)(?<a>x)(q)(?<a>y)`
             * gives the name `a` the numbers 1 and 3 — so the emitted shape is an
             * else-if chain over the run in ascending number, taking the first member
             * that is SET. Carrying the set uniformly means `nrefs == 1` is the SAME
             * emitted code path with the chain length at one, rather than a second,
             * rarer, less-tested path.
             *
             * `Ast.u.cap.no` is NOT reused for this: on an `A_CAP` it means "this node IS
             * group k", a different fact, and overloading it would make two facts
             * compete for one field. */
            const int  *refs;
            int         nrefs;
            /* [M6.5.2] A_BREF ONLY — is the compare CASELESS? D62's principle again:
             * node FIELDS encode PARSE-RESOLVED MODIFIER STATE, set from the scoped
             * `(?i)` state in force AT THE BACKREFERENCE, never re-derived downstream.
             *
             * MEASURED (backrefs_design.md §4, axis B): the caselessness is the option
             * in force at the REFERENCE, not at the group. `^(a)(?i:\1)$` matches
             * "aA"; `^(?i:(a))\1$` does not; `^((?i)a)\1$` does not.
             *
             * IT CANNOT FOLD AWAY AT PARSE TIME the way `Ast.u.anch.multiline`'s sibling
             * `cx->mods->caseless` does for a class (D23): there is no bitmap to widen,
             * because the operand is subject text not known until the match runs. So
             * this field selects WHICH residual seam entry the emitter calls
             * (`$_bref_match` or `$_bref_match_caseless`) — two entries chosen at emit
             * time, never one entry with a runtime flag, which is D18/D23's rule that
             * an option compiles away.
             *
             * ANY ANALYSIS THAT PATTERN-MATCHES `case A_BREF:` AND DOES NOT READ THIS
             * FIELD reproduces src/opt/possessify.c's pre-D62 bug, and no compiler
             * diagnostic will say so — D62 control 3's accepted residual, covered here
             * and by sabotage row S106. */
            bool        caseless;
        } bref;

        /* [M6.6.2] A_LOOK: the lookaround payload — THREE FLAGS AND A WIDTH
         * TABLE, i.e. FIVE parse-resolved fields (design §3.1(a')). Every one
         * of them is D62 state: resolved by the parse hook at the position
         * that knows, never re-derived downstream.
         *
         * D70 IS WHY THIS IS A UNION MEMBER AND NOT FIVE MORE TOP-LEVEL
         * FIELDS, and design §3.1's own sketch (which wrote them as
         * `look_behind`, `look_neg`, ...) is superseded in SPELLING and not in
         * content. In particular `int look_widths[]` was sketched as a
         * FLEXIBLE ARRAY MEMBER and is an arena `const int *` here: a flexible
         * array cannot live in a union, cannot be preceded by another member,
         * and would make `sizeof(Ast)` a lie for the zeroing arena that
         * allocates every node at one fixed size. */
        struct {
            /* DIRECTION — false = lookahead, true = lookbehind.
             * WRITTEN by the parse hook (src/parse/mod_lookaround.c, wave
             * B+C for the three `(?=`-side tails, wave D for the three `<`
             * tails). READ by `vm_look` (src/gen/emit_vm.c) and by nothing
             * else — the whole one-reader argument §3.1(a) rests on. Sabotage
             * row S-LA15 ignores it and emits the lookahead shape for a
             * lookbehind. */
            bool        behind;
            /* POLARITY — true = the body must FAIL for the assertion to hold.
             * WRITTEN by the parse hook, READ by `vm_look`. Sabotage row
             * S-LA14 ignores it, and every negative cell goes red. This is the
             * field D62 control 3 names: `case A_LOOK:` without `.neg` is
             * possessify.c's pre-D62 bug in a new construct. */
            bool        neg;
            /* ATOMICITY — true for `(?=` `(?!` `(?<=` `(?<!`, false for
             * `(?*` `(?<*` `(*napla:` `(*naplb:`. It is the whole difference
             * between the two families (design §2.2): the atomic forms commit
             * to the body's FIRST success, the non-atomic ones can be
             * re-entered. WRITTEN by the parse hook, READ by `vm_look`, which
             * emits the shape MINUS the cut when it is false (§3.6).
             * Sabotage row S-LA16 ignores it and always emits the cut. */
            bool        atomic;
            /* THE WIDTH TABLE — the fixed width of each TOP-LEVEL branch of
             * the body, in branch order, for a LOOKBEHIND; NULL for a
             * lookahead. Arena-allocated (see the D70 note above).
             *
             * COMPUTED AT PARSE TIME AND STORED, design §3.1(c), for the
             * reason `Ast.u.bref.caseless` is: the REFUSAL in §2.5 has to
             * happen in the module's parse hook — a body pcrec will not
             * compile must be rejected with a pattern OFFSET, not discovered
             * by the emitter — and once the hook has computed the widths,
             * recomputing them downstream is a second derivation that can
             * disagree with the first. `pcrec_maxw`/`pcrec_minw` (src/opt/mrl.c)
             * are what the hook computes them WITH: a branch qualifies exactly
             * when `minw == maxw`, which is also why an under-estimating
             * `pcrec_maxw` is a silent miscompile rather than a lost
             * optimisation. WRITTEN by the parse hook (wave D), READ by §3.4's
             * emitted back-step. Sabotage row S-LA11.
             *
             * [DD-14.LB] `NULL` ON A LOOKBEHIND MEANS **PENDING**, and that is
             * this field's one extra state rather than a second field. The
             * hook cannot compute the table when the body carries an `A_CALL`
             * — `pcrec_maxw`'s `A_CALL` arm answers `PCREC_W_UNBOUNDED` there
             * because the callee is not bound until `pcrec_callgraph_build`
             * runs over the FINAL tree — so it records the assertion instead
             * (`at` below) and `pcrec_postresolve` (src/opt/postresolve.c)
             * fills this in or refuses. THE THREE STATES ARE DISJOINT AND
             * EXHAUSTIVE: `!behind` -> NULL and `nbranch == 0` (a lookahead
             * has no width rule); `behind && widths` -> resolved; `behind &&
             * !widths` -> pending, `nbranch` already correct. `vm_look_behind`
             * ctx_fails on the pending shape, which is what makes a DELETED
             * post-resolution pass a loud internal error rather than a NULL
             * dereference (sabotage row S-LB1). */
            const int  *widths;
            /* how many entries `widths` holds — the body's top-level branch
             * count, which is `AltInfo.nbr` (PARSE-1) for the body parse.
             * WRITTEN and READ with `widths`; the two are one fact — EXCEPT
             * in the pending state above, where the hook knows the branch
             * count (the parse just produced it) and not the widths, which is
             * exactly why the deferred pass needs nothing but this node. */
            int         nbranch;
            /* [DD-14.LB] THE ASSERTION'S OWN PATTERN OFFSET — the `at` the
             * parse hook was dispatched on, i.e. the offset of the construct's
             * opening `(`. WRITTEN by the parse hook for EVERY A_LOOK, READ by
             * `pcrec_lookaround_fix_widths` when it refuses a body whose width
             * could only be decided after the call graph existed.
             *
             * IT EXISTS BECAUSE `Ast` CARRIES NO POSITION OF ANY KIND
             * (PARSE-1's own note), and a deferred refusal with no offset
             * would be the tier-2 regression D26 forbids: the hook's own
             * refusals for call-FREE bodies point at the assertion, and the
             * deferred one must point at the same byte or the two timings
             * would be observably different diagnostics for one rule. It is
             * written UNCONDITIONALLY rather than only when pending, because
             * "the offset this construct was parsed at" is a fact about every
             * lookaround and a conditionally-valid field is a field a later
             * reader gets wrong. */
            size_t      at;
        } look;

        /* [DD-14] A_CALL: the subroutine-call payload — ONE RESOLVED TARGET,
         * ONE SHARED BODY, ONE LINKAGE AND ONE SLOT WRITE SET (design §4.1).
         * The first two are D62 parse-resolved state; the last three are
         * DERIVED ANALYSIS, and design §4.1(d) is explicit that the split is
         * deliberate — `save`/`nsave`/`link` are a fixpoint over the call
         * graph and the parser does not have the graph, so they belong where
         * possessify's and mrl's results belong, not in the parse hook.
         *
         * NOTHING PRODUCES AN `A_CALL` YET. Wave A2 lands the kind and the
         * walker arms with NO producer; the parse hook, the resolver and
         * `src/opt/callgraph.c` are wave B+C's. Every field below therefore
         * names the wave that will first WRITE it, and the arena zeroes, so a
         * node nothing wrote reads `target == 0`, `body == NULL`,
         * `link == CALL_SPLICE`, `nsave == 0`, `save == NULL`. */
        struct {
            /* THE GROUP NUMBER TO RUN. `0` IS NOT "unset": it is THE ROOT —
             * `(?R)`, `(?0)`, `\g<0>`, `\g'0'` — and design §2.4 MEASURED
             * that the root INCLUDES THE ANCHORS (`^(a(?R)?b)$` on "aabb"
             * matches, `\A`/`\z` inside a callee re-assert at the same
             * absolute positions, §3.4(e2)), so this is deliberately a
             * NUMBER and not a pointer to an `A_CAP`.
             *
             * AN INT AND NOT A SET, and that is the field that distinguishes
             * this construct from `A_BREF` (design §4.1(b)): §3.4(c) MEASURED
             * that a call by NAME to a `(?J)` duplicated name runs the FIRST
             * DECLARATION, statically, and does not retry into the run, while
             * a REFERENCE to the same name resolves at match time against the
             * whole run. One number, resolved once.
             *
             * WRITTEN by the end-of-parse resolution pass (wave B+C's
             * `PEND_CALL` rule in `pcrec_bref_resolve`, design §4.2) — the one
             * site that knows both the final group count and every
             * declaration of a duplicated name. The four ports
             * (`pcrec_rcport_num`/`_rel`/`_name` in `src/parse/mod_recursion.c`
             * and `pcrec_brport_g`'s `<`/`'` arms, wave D) only record a
             * `PendingRef`; relatives are already absolute by then, and
             * `(?+0)`/`(?-0)` are the port's own error 126.
             * READ by `pcrec_bref_mark` (`src/opt/atomic.c`, §4.3 — the ONE
             * reader that exists in this wave), by `src/opt/callgraph.c` and
             * by `vm_emit`'s `RX_CALL` site. */
            int         target;
            /* THE RESOLVED CALLEE SUBTREE. SHARED, NEVER OWNED — it is the
             * same `Ast *` that hangs at the callee's own lexical position
             * in this tree, so it is NEVER deep-copied and NEVER freed
             * through this pointer, and a generic copy helper that FOLLOWS
             * it duplicates the callee (src/core/CLAUDE.md's D70 survey
             * records what each one does).
             *
             * THIS POINTER IS THE AST'S FIRST BACK EDGE and design §4.4's
             * rule governs every reader: A WHOLE-TREE PREDICATE MUST NOT
             * FOLLOW IT — it would recurse for ever on `(a(?1))` and hang the
             * compiler, and it is redundant anyway because the callee is
             * visited at its own lexical position. A SUBTREE-RELATIVE
             * analysis goes through `src/opt/callgraph.c`'s memoised SCC
             * fixpoint. The arms in this wave are where that rule was applied
             * site by site.
             *
             * RESOLVED ONCE AND STORED, `A_BREF.u.bref.refs`'s rule
             * (§4.1(c)): four independent derivations of "which subtree does
             * this call run" would be four chances to disagree.
             * WRITTEN by the same end-of-parse pass as `target` (wave B+C).
             * READ by `callgraph.c`, `vm_nullable`, `vm_cost`,
             * `vm_count_slots`, `vm_emit` and — ONLY once
             * `lookaround_design.md` §11 wave A has built it, P13 measured it
             * has not — `pcrec_maxw`. */
            const Ast  *body;
            /* HOW THE CALLEE REACHES THE ARTIFACT — `CALL_SPLICE` (inline the
             * subtree here) or `CALL_LINKAGE` (jump to one emitted region and
             * return). WRITTEN by `src/opt/callgraph.c` from the SCC
             * condensation and a size budget (design §6.3), NEVER by the
             * parser, which does not have the graph. READ by `vm_emit`, and
             * by `src/ir/nfa.c` in wave G (a SPLICEABLE call has an exact
             * finite lowering; a recursive one does not, §8.3).
             * The arena zeroes to `CALL_SPLICE`, which is the WRONG default
             * in the unsound direction for a recursive callee — so wave B+C
             * sets this for EVERY node before the emitter runs, and wave G's
             * eligibility rule is what may downgrade it. */
            CallLink    link;
            /* |W| — HOW MANY SLOTS THE RETURN RESTORES, and `save` is the
             * ascending list of their INDICES. W is the CALLEE REGION's SLOT
             * WRITE SET: EVERY slot family any node in the callee's
             * transitive body can write, NOT just the captures. Design
             * §5.3a's rule, and it is the row this design has had REFUTED
             * TWICE — the capture-only version lost `SLOT_GROUP<n>_PENDING`
             * (two LOST MATCHES) and `SLOT_CUT_MARK<n>` (six FALSE MATCHES,
             * §5.3b) — so "the captures" is the answer that is measured
             * WRONG, not merely incomplete.
             *
             * SLOTS 0 AND 1 ARE EXCLUDED BY CONSTRUCTION: §3.4(b) MEASURED
             * that `\K` is NOT restored by a return, so the pair of indices
             * that carry it must survive the restore.
             *
             * THE INDICES ARE THE CALLEE REGION'S OWN (design §4.4c). W
             * derived from the LEXICAL occurrence names the LEXICAL copy's
             * slots, and under `CALL_LINKAGE` the emitted callee region's are
             * different numbers — a restore written against the wrong indices
             * is §5.3b's axis-C miscompile arriving by a second route.
             * Counted PER EMITTED INSTANCE (§5.7).
             *
             * WRITTEN by `src/opt/callgraph.c`'s `W` fixpoint (wave B+C).
             * Arena-allocated, ascending. READ by `vm_emit`'s save/restore
             * emission and charged by `vm_cost` as `2*nsave` of trail. */
            int         nsave;
            const int  *save;
            /* [DD-14 wave B+C] THE THREE DERIVED FACTS A BARE `const Ast *`
             * WALKER CANNOT COMPUTE, cached ON THE NODE rather than in a memo
             * the walker would need a context to reach.
             *
             * WHY ON THE NODE. `pcrec_minw` (src/opt/mrl.c) and `vm_nullable`
             * (src/gen/emit_vm.c) are bare `const Ast *` walkers with no `Ctx`
             * parameter, so "read callgraph.c's memo" has exactly two
             * spellings: change every call site's signature, or put the memo
             * in a FILE-STATIC — and a file-static is a mutable global, which
             * [TS-1]/[TS-3] test against directly (two threads compiling
             * different patterns at once). The node is the one place both
             * walkers already have in hand and that is private to one compile.
             *
             * EVERY ONE IS WRITTEN SO THE ARENA'S ZERO IS THE SOUND ANSWER,
             * because a walker may legitimately run BEFORE the fixpoint does
             * (`pcrec_minw` is called from src/opt/possessify.c, which runs
             * inside `pcrec_select_engine`, before the graph exists):
             *
             *   `minw`        0 — the least width this callee can consume.
             *                 Zero is `pcrec_minw`'s own SAFE direction (an
             *                 under-estimate prunes less and can never delete
             *                 a live position), so an un-run fixpoint costs
             *                 pruning and never a match.
             *   `nonnullable` false — i.e. "assume NULLABLE". The polarity is
             *                 INVERTED for exactly this reason, and it is the
             *                 whole content of the field's name: `vm_nullable`
             *                 answering true is what EMITS the empty-iteration
             *                 guard, so `false` keeps the guard and a wrong
             *                 answer costs a redundant guard, while the other
             *                 polarity's zero would DROP the guard and hang
             *                 the emitted matcher on `(?&g)*` with a nullable
             *                 callee (§2.6).
             *   `nsave`/`save` 0/NULL — restore nothing, which is a
             *                 miscompile, and is why they are NOT arena-zero
             *                 safe and why `pcrec_emit_vm` fills them for
             *                 every node before it emits a byte.
             *
             * `maxw` WAS DELIBERATELY ABSENT UNTIL [DD-14.LB], and the
             * paragraph that argued for its absence is kept here because the
             * half of it that was right is still right. `pcrec_maxw`'s safe
             * direction is the OPPOSITE of `minw`'s, so a plain `long long
             * maxw` whose arena zero is `0` would be its SILENT MISCOMPILE —
             * an under-estimated maximum lets a variable-width branch through
             * the lookbehind rule as fixed, which on a NEGATIVE lookbehind is
             * a false match. That is why the pair below is TWO fields and not
             * one: `maxw_known` is the arena-zero-safe half, exactly as
             * `nonnullable`'s inverted polarity is, and `pcrec_maxw`'s arm
             * reads `maxw` ONLY through it.
             *
             * WHAT CHANGED IS THE "no customer" HALF. The customer is module
             * `lookaround`'s fixed-width rule, and the timing objection this
             * paragraph used to raise — "it would need a writer that runs
             * before the parse-time lookbehind width rule, which the call
             * graph cannot" — is answered by moving the CONSUMER rather than
             * the writer: `pcrec_postresolve` (src/opt/postresolve.c) re-asks
             * the width question after `pcrec_callgraph_build`, so the memo is
             * read where it exists. See `pcrec_postresolve`'s declaration and
             * docs/design/subroutines_design.md §3.4(d)'s 2026-08-24
             * amendment.
             *
             *   `maxw`       the callee's greatest width, VALID ONLY when
             *                `maxw_known`. `PCREC_W_UNBOUNDED` is a legal
             *                value and is the fixpoint's answer for every
             *                callee in a cycle and every callee that can
             *                reach one.
             *   `maxw_known` false — i.e. "answer PCREC_W_UNBOUNDED". The
             *                arena's zero is the SOUND direction for this
             *                pair for the reason above, and it is the answer
             *                `pcrec_maxw` gave for every call before this
             *                field existed, so a walker that legitimately
             *                runs before the fixpoint (the parse hook itself)
             *                sees exactly the old behaviour.
             *
             * WRITTEN by `src/opt/callgraph.c`'s two fixpoints (`minw`,
             * `maxw`/`maxw_known`) and by `src/gen/emit_vm.c` (`nonnullable`,
             * whose recurrence is `vm_nullable` and lives there; `save`/
             * `nsave`, whose SLOT INDICES are the emitter's own layout and
             * exist nowhere else). */
            long long   minw;
            long long   maxw;
            bool        maxw_known;
            bool        nonnullable;
        } call;
    } u;
};

static inline void cls_set(uint8_t *b, unsigned c)      { b[c >> 3] |= (uint8_t)(1u << (c & 7)); }
static inline bool cls_has(const uint8_t *b, unsigned c){ return (b[c >> 3] >> (c & 7)) & 1u; }

/* ---- NFA (priority Thompson) ---- */

typedef enum {
    N_CLASS,   /* consume one byte in cls, goto t1 */
    N_SPLIT,   /* epsilon: try t1 first (higher priority), then t2 */
    N_EPS,     /* epsilon: goto t1 */
    N_BOT,     /* assert start of subject, goto t1 */
    N_EOL,     /* assert end-of-subject or before-final-\n, goto t1 */
    N_END,     /* [M6.2 wave A] assert end-of-subject (`\z`), goto t1 —
                * strictly stronger than N_EOL, which is why it is its own
                * state kind and its own closure bit rather than a variant */
    /* [M6.2 wave C] `(?m)^` and `(?m)$`, goto t1. SEPARATE KINDS from N_BOT
     * and N_EOL, and that is not the same question D62 answered: D62 rules
     * that the AST spells multiline as a FIELD, because `Ast.k` encodes
     * STRUCTURE and a modifier is parse-resolved state. By the time lowering
     * has run the modifier is no longer state — it has been resolved into a
     * DIFFERENT ASSERTION, whose truth condition is a different expression
     * over different inputs (N_EOL is a position test; N_EOL_M reads a BYTE).
     * That is exactly the structural difference NKind exists to carry, and
     * it is the same argument N_END already won one line up.
     *
     * Their operands, in the vocabulary src/ir/dfa.c's Clo uses:
     *   N_BOT_M  — start of subject, or the byte to the LEFT is a newline;
     *   N_EOL_M  — end of subject, or the byte to the RIGHT is a newline.
     * `\A`/`\Z` never lower to these: their nodes pin multiline false at the
     * parser (src/parse/mod_assertions.c), which is what makes them aliases
     * of the NON-multiline `^`/`$` under `(?m)` too, as PCRE2 has them. */
    N_BOT_M,
    N_EOL_M,
    /* [M6.2 wave B] `\b` / `\B`, goto t1. The FIRST assertions in this
     * machine whose truth is not a function of the position alone: both read
     * the byte on either side of it. src/ir/dfa.c's closure evaluates them
     * from TWO bits — the word-ness of the byte the walk already consumed
     * (carried in the DFA state's identity) and the word-ness of the byte it
     * is about to consume (a per-class parameter). The test is SYMMETRIC in
     * those two bits, which is exactly why one closure serves the forward and
     * the reverse machine with no notion of direction anywhere in it. */
    N_WORDB,
    N_NWORDB,
    /* [M6.2 wave D] `\G`, goto t1. An ABSOLUTE POSITION TEST like N_BOT — it
     * reads no byte and needs no class axis — but against a value that is not
     * known until the match call: `pos == startpos` where N_BOT is `pos == 0`.
     *
     * In src/ir/dfa.c that makes it a THIRD closure bit beside `bot_ok` and
     * `eol_ok`/`end_ok`, and a SECOND family of interior start states
     * (`Dfa.s1g[]`), because "this attempt begins at `startpos`" is a
     * start-state property exactly as "this attempt begins at offset 0" is.
     * It never survives a consumed byte — after one transition `pos >
     * startpos` unconditionally — so the worklist closes every successor with
     * the bit clear and mid-pattern `\G` (`a\Gb`) dies in the closure with no
     * special case (assertions_design.md §4.2). */
    N_GSTART,
    N_ACCEPT
} NKind;

typedef struct {
    NKind   k;
    uint8_t cls[32];
    int     t1, t2;
    uint8_t loop;        /* star/plus loop-entry split */
    uint8_t exit_is_t2;  /* which edge leaves the loop (greedy: t2) */
} NState;

typedef struct {
    NState *st;
    int     n, cap;
    int     start;
    /* [OPT-K] THE ANCHORED START — the state a match's OWN first byte is read
     * from, as opposed to `start`, which for an ENG_UNANCH machine is the
     * lowest-priority self-loop `nfa_wrap_unanchored` puts in front of it.
     *
     * IT IS A FIELD AND NOT A SHAPE TEST. `docs/design/offset_k_skip.md` §3
     * needs to walk the pattern's own prefix, and the alternative — "the start
     * is a SPLIT whose t2 is an all-bytes N_CLASS looping back to it" — is a
     * second statement of `nfa_wrap_unanchored`'s construction that a change
     * to the wrap would silently invalidate. `pcrec_build_nfa` sets it equal
     * to `start`, so an UNWRAPPED machine (ENG_ATTEMPT's, and the reverse
     * machine) answers correctly without anyone having to remember to. */
    int     anch_start;
} Nfa;

/* ---- [OPT-K] the offset-k prefix analysis (src/opt/prefix_k.c) ---- */

/* How far past offset 0 the walk looks. It is a WALK bound and not a tuning
 * knob: past ~two dozen bytes a fixed-width prefix is vanishingly rare and
 * the frontier has almost always either accepted or fanned out. The k-SET
 * cap below is the one that bounds emitted work.
 *
 * How many (offset, byte-set) tests one skip may carry — the k-set cap. Four
 * is the note's §4.6: the third and fourth verify are already below the
 * model's noise on every corpus pattern, and each one is emitted text and a
 * branch on the candidate path.
 *
 * [LIM-1] (D90, 2026-08-30): both generated from src/core/limits.def, the
 * single derivation `pcrec --list-limits` dumps — values unchanged (24, 4). */
#define PCREC_LIMIT_INTERNAL_H(name, value, unit, kind, override, anchor, desc, default_name) \
    enum { name = (value) };
#include "core/limits.def"
#undef PCREC_LIMIT_INTERNAL_H
/* MEASURED (make strict): gcc's enum-widening extension picks an UNSIGNED
 * underlying type for PCREC_MINW_MAX's enumerator (1LL << 40 exceeds
 * UINT_MAX, and gcc's "smallest sufficient type" rule prefers unsigned for
 * a non-negative value out of int range) — every comparison and arithmetic
 * use across this tree (mrl.c, callgraph.c, emit_vm.c) assumes `long long`,
 * so `-Wsign-compare` fires at all eleven of them. One correction, at
 * generation, rather than a cast repeated at every use site: rebinding the
 * name to a cast of itself is standard C's self-referential-macro rule
 * (C11 6.10.3.4) — the inner occurrence is not re-expanded, so it resolves
 * to the ENUM CONSTANT the include above just declared, cast once. The
 * 2^40 value is still spelled exactly once, in limits.def; this is a TYPE
 * fix, not a second numeric source. PCREC_W_UNBOUNDED (below) is unaffected
 * by construction — it is already only ever a macro alias of this name. */
#define PCREC_MINW_MAX ((long long)PCREC_MINW_MAX)

typedef struct {
    int      k;          /* the offset, in bytes from the candidate start */
    uint8_t  set[256];   /* the bytes a match may carry there */
    int      count;      /* how many */
    int      byte;       /* the single value when count == 1 */
    unsigned ppm;        /* the prior's mass on `set`, parts per million */
} PrefixK;

typedef struct {
    int      nwalk;                   /* offsets proved: k[0..nwalk-1] */
    PrefixK  k[PCREC_PREFIX_K_MAX];
    /* THE SELECTION. `nsel == 0` means "no offset-k skip" — the artifact
     * keeps exactly the offset-0 filter it had before this row. */
    int      nsel;
    int      sel[PCREC_OFSK_MAX_SET]; /* indices into k[], ASCENDING by offset */
    int      scan;                    /* index into sel[]: the memchr offset */
    int      maxk;                    /* k[sel[nsel-1]].k */
    unsigned rate_ppm;                /* predicted candidate rate, selected */
    unsigned base_ppm;                /* ... and under the offset-0 filter alone */
} PrefixKSets;

/* `k0` is the offset-0 byte set the DFA derivation already owns
 * (src/gen/emit_dfa.c's `cand_from_escapes`); this function never re-derives
 * it. See docs/design/offset_k_skip.md §3. */
void pcrec_prefix_ksets(Ctx *cx, const Nfa *nfa, const uint8_t k0[256],
                        PrefixKSets *o);
unsigned pcrec_byte_freq_ppm(int b);
unsigned pcrec_byte_freq_total_ppm(void);

/* ---- DFA (priority subset construction) ---- */

/* [M6.2 wave C] THE CLASS AXIS IS THREE-VALUED, and this enum is it.
 *
 * Wave B gave the closure one class-axis bit — "the byte about to be consumed
 * is a word character" — because `\b` was the only assertion that read it.
 * `(?m)$` reads a DIFFERENT property of that same byte ("it is a newline"), so
 * the axis stops being a bool and becomes a partition of the alphabet:
 *
 *   UPC_PLAIN  neither a word character nor a newline
 *   UPC_WORD   a word character
 *   UPC_NL     a newline (the D64 definition, `pcrec_cls_newline`)
 *
 * THE THREE ARE DISJOINT AND EXHAUSTIVE because a newline is not a word
 * character; there is no fourth combination to represent. src/ir/dfa.c's
 * `eqclasses` refines the byte-equivalence partition by whichever of the two
 * sets the machine actually needs, so every byte of a class has the same
 * answer and `upc_of_class` is exact rather than a sample.
 *
 * THE SAME THREE VALUES INDEX THE OTHER SIDE. The byte the walk has already
 * CONSUMED carries the same partition — `\b` reads its word-ness and `(?m)^`
 * reads its newline-ness — but that side is carried in the state IDENTITY
 * (§3.5's mechanism), so it indexes the START states (`Dfa.s1u`) rather than
 * a per-state array. One enum, two uses, and the symmetry is real: the
 * forward and reverse machines swap which side is which, which is what
 * make_state's `reverse` mapping is for. */
enum { UPC_PLAIN = 0, UPC_WORD = 1, UPC_NL = 2, UPC_N = 3 };


/* One closure of a pre-set under one class-axis context. */
typedef struct {
    int     *list;     /* priority-ordered N_CLASS state ids (arena) */
    int      nlist;
    uint8_t  accept;   /* match ends here */
} DView;

typedef struct {
    /* [M6.2 wave B, generalized in wave C] THE CLASS VIEWS — the SAME pre-set
     * closed once per class-axis context (assertions_design.md §3.5/§3.6).
     * `up[UPC_PLAIN]` is the base view every pre-wave site meant by "the
     * state's list" and "the state's accept bit".
     *
     * They are SECOND LISTS rather than second interned states, and that is
     * the one structural choice worth understanding before editing anything:
     *
     *   - `eolvar`/`endvar` are POSITION views: they apply at two positions
     *     out of n, so an indirection through a per-state table costs nothing
     *     and an interned variant state is the natural spelling.
     *   - a class view is decided by the byte at EVERY position, and the
     *     class of that byte is already in a register for the transition
     *     lookup. Interning it as a variant state would put a second table
     *     read on the hot path for a choice the transition row can BAKE IN.
     *
     * So `tr[c]` is built from `up[upc_of_class(c)]`, and the only thing left
     * over is the ACCEPT bit — which is why §3.6's class-indexed accept table
     * exists and nothing else does. Every view's accept equals
     * `up[UPC_PLAIN].accept` on every state of a machine with no `\b` and no
     * `(?m)$` (there is no N_WORDB/N_EOL_M to gate, so the closures
     * coincide), so that table is not emitted and the artifact does not move.
     *
     * The OTHER half of the context — the class of the byte already CONSUMED
     * — is not a field at all. It is carried implicitly: two pre-sets that
     * differ in it close differently wherever it matters, so they intern
     * apart, and where it does not matter they intern together, which is the
     * merge a separate field would have to forbid. */
    DView    up[UPC_N];
    int      eolvar;   /* EOL-variant state (the eol_ok=true closure of the same
                          pre-set: correctly priority-pruned accept + threads),
                          used at EOL positions; -1 = identical to this state */
    /* [M6.2 wave A] END-variant state: the (eol_ok, end_ok) = (T,T) closure,
     * used at `pos == n` only. -1 means "IDENTICAL TO THE EOL VIEW" — NOT
     * "identical to this state", and the difference is the whole of R30 E3.
     * The chain a consumer must walk is therefore two links:
     *     view(st, pos == n) = endvar >= 0 ? endvar
     *                        : eolvar >= 0 ? eolvar : st
     * Canonicalizing against the base instead would make every eol-differing
     * state of every `$`-bearing pattern intern a live endvar, and a
     * `\z`-free pattern's artifact would stop being byte-identical — the
     * exact opposite of the zero-regression property this convention buys.
     * tests/codegen/run_endvar_identity.sh is the check that says so. */
    int      endvar;
    int     *tr;       /* [ncls] target dfa state or -1 = dead (arena) */
} DState;

typedef struct {
    DState  *st;       /* heap (realloc'd) */
    int      n, cap;
    int      ncls;     /* number of byte equivalence classes */
    uint8_t  clsmap[256];
    uint8_t  rep[256]; /* representative byte per class id */
    int      s0;       /* start state where there is no context byte at all */
    /* [M6.2 wave B, generalized in wave C] MECHANISM 4's seed
     * (assertions_design.md §3.8): the INTERIOR start states, one per
     * class-axis context of the byte the walk has already passed —
     * `s[startpos-1]` for the forward machine, `s[end]` for the reverse one.
     * `s1u[UPC_PLAIN]` is what the pre-wave code called `s1`.
     *
     * `s0` covers "there is no such byte" (start of subject for the forward
     * machine, end of subject for the reverse one), which is neither a word
     * character nor a newline, so `s0` needs no twins of its own.
     *
     * All three are the same state whenever the machine carries no assertion
     * that reads the consumed byte, because the closures then coincide and
     * intern together — which is what keeps every existing artifact's start
     * dispatch a compile-time constant. */
    int      s1u[UPC_N];
    /* [M6.2 wave D] `\G`'s own interior start states: the SAME class-axis
     * family as `s1u[]`, closed with the `\G` bit SET (assertions_design.md
     * §4.2). The three reachable start states of that section's table are
     * therefore `s0` (`start == 0`, which implies `start == startpos` since
     * an attempt loop never runs below `startpos`), `s1g[]`
     * (`start == startpos > 0`) and `s1u[]` (`start > startpos`).
     *
     * Equal to `s1u[]` entry for entry on every machine with no N_GSTART —
     * the bit gates nothing there, so `pcrec_build_dfa` does not even close
     * the extra views and assigns the same interned ids. That is what keeps
     * every pre-wave artifact's start dispatch and `start_max` string
     * unmoved, by construction rather than by a flag test in the emitter. */
    int      s1g[UPC_N];
    /* True when this machine was built with a CLASS AXIS at all — i.e. its
     * NFA carries an N_WORDB/N_NWORDB (`\b`'s word-ness) or an N_BOT_M/
     * N_EOL_M (`(?m)`'s newline-ness). It is the flag every emitter site that
     * must choose between the pre-wave text and the class-indexed text reads,
     * and it is derived from the NFA rather than from any state's contents so
     * the two emitters cannot disagree about which shape they are in.
     *
     * Named `wordctx` through wave B, when `\b` was the only customer. */
    bool     clsctx;
    int      maxstates;/* engine-dependent cap (R1 A-3): table-mode machines
                          afford far more states than computed-goto ones */
    /* [ENG-ABS] IS THIS MACHINE OPTIONAL, i.e. may the compile continue
     * without it? False on every machine the ENGINE needs — the forward and
     * reverse pair, ENG_ATTEMPT's single machine — and true only on the
     * anchored MATCH-HERE machine, which is a FORM the emitter may or may not
     * select (docs/design/anchored_match_unwrapped.md §5.2).
     *
     * It is read at exactly one place: `intern`'s two "pattern too complex"
     * sites, where an optional machine RECORDS the overflow and returns
     * instead of `ctx_fail`ing. That keeps `[SEL-1]`'s own record and both
     * diagnostics character-for-character unchanged, and it is why a pattern
     * that compiles today cannot start failing because an optional machine
     * did not fit. */
    bool     optional;
    /* [ENG-ABS] Set by `intern` when an OPTIONAL machine hit a cap. The
     * machine is then partially built and must not be emitted; the emitter's
     * axis-G candidate reads this (through `Job.anchored_ok`) and selects the
     * search-and-filter fallback. Never set on a mandatory machine — that
     * path still `ctx_fail`s. */
    bool     overflowed;
    int     *tab;      /* hash table (heap) */
    size_t   tabcap;
} Dfa;


/* ---- compile context ---- */

/* engine selection (D7): assertion-free patterns use the O(n) unanchored
 * forward + reverse-DFA engine with table-driven emission; patterns with
 * ^/$ stay on the per-start attempt engine (computed goto) for now */
enum { PCREC_ENG_ATTEMPT, PCREC_ENG_UNANCH };

/* [M4.5b] engine_m4.md §5.1: selection's answer, computed by a PASS
 * (src/opt/select_engine.c) rather than by compile.c's old inline `if`.
 * `engines` uses the registry's own ENGM_* vocabulary (§5.1), which is what
 * makes SR-8 a consumption rather than a new schema. */
typedef struct {
    unsigned    engines;    /* ENGM_* mask: which engines CAN compile this */
    unsigned    chosen;     /* exactly one ENGM_* bit */
    const char *why;        /* the forcing construct, for the stamp and F7 */
    size_t      why_pos;    /* pattern offset of it */
    bool        prefilter;  /* §6: is a DFA prefilter emitted alongside */

    /* [OPT-4] WHICH LANGUAGE THAT PREFILTER WAS BUILT FROM (K39;
     * docs/design/prefilter_count_independence.md). False = the pattern's own
     * (exact) language; true = the COUNT-COLLAPSED superset, every `A_REP`
     * with `rmin > 1 || rmax > 1` lowered as `X{min(m,1),}`.
     *
     * IT IS NOT SET BY `pcrec_select_engine`, and that is the one thing to
     * know about this field's home. Every other member here is a decision
     * selection can make from the AST alone; this one is decided by MEASURING
     * the exact machine (`src/core/compile.c`'s build gate compares `Nfa.n`
     * — historically against a state budget, now only for the stamp), because
     * a prediction of
     * that number would be a second statement of `compile_ast`'s own `A_REP`
     * lowering and the two can drift (D24). It rides on `EngineFit` rather
     * than on `Job` so that the emitter reads the prefilter's KIND and its
     * LANGUAGE off one struct, in one place — `<PREFIX>_VM_PREFILTER` and
     * `<PREFIX>_VM_PREFILTER_LANG` are two readers of one derivation (D81).
     *
     * ITS CONSUMERS ARE THREE AND THEY MUST AGREE: the stamp, the `--emit-ir`
     * listing's `; prefilter` line, and `Vm.mrl_win` — where it joins
     * `pcrec_has_atomic`/`pcrec_has_lookaround` as a third reason the span END
     * is not an upper bound. R31 E3's finding applies unchanged: the lines
     * that BUILD the ceiling read `mrl_win` itself, so flipping this field
     * cannot leave a stamp disagreeing with a live clamp. */
    bool        prefilter_collapsed;

    /* [OPT-4.1] IS THE PREFILTER'S LANGUAGE NULLABLE — can it match the empty
     * string? Written ONCE at `src/opt/select_engine.c`'s fit site as
     * `pcrec_minw(root) == 0` and read by the two sites that can decline the
     * count-collapsed rescue (D81: one derivation, N readers; the predicate is
     * `src/opt/mrl.c`'s existing width analysis, never a second walk).
     *
     * WHY THE COLLAPSED LANGUAGE'S NULLABILITY IS THE EXACT PATTERN'S.
     * The collapse rewrites `X{m,n}` as `X{min(m,1),}`, and `min(m,1) == 0`
     * iff `m == 0`, so an `A_REP` is nullable on exactly the same condition
     * before and after; concatenation and alternation combine 0-ness
     * identically. One walk therefore answers for both languages, which is why
     * this field is not "collapsed_lang_nullable".
     *
     * WHY `pcrec_minw` IS THE RIGHT WALK AND NOT AN APPROXIMATION OF ONE. It
     * already answers for the PREFILTER's lowering rather than for the
     * pattern's semantics: `A_CAP`/`A_ATOMIC` are transparent (as `src/ir/
     * nfa.c` lowers them), `A_LOOK` is 0 (as the prefilter lowers it — to
     * epsilon), and `A_CALL` reads the callgraph fixpoint, which
     * `src/core/compile.c` has already run by the time selection asks. Its
     * documented direction is UNDER-estimation, so `minw == 0` may claim
     * nullable where the true language is not — and that direction is the safe
     * one here: declining a rescue costs a filter, never an answer.
     *
     * WHAT IT DECIDES (the measured need, pcrec-bench O-10 item 3 at pin
     * 96e44c2). A nullable prefilter language admits a zero-length match at
     * EVERY position, so the filter can never dismiss one: the artifact pays a
     * scan whose every answer is "maybe". Measured there at 1.2-9.9x SLOWER
     * than the same pattern with no prefilter at all (`[a-z]{0,32768}`: search
     * x3.57, throughput 1.880 -> 6.899 ns/B). The same fact is visible inside
     * the artifact from the other end — a nullable language's start state
     * ACCEPTS, so `src/gen/emit_dfa.c`'s `unanch_start` can select no
     * candidate-byte skip and the inlined scan stamps `<PREFIX>_DFA_PREFILTER
     * "none"` — which is a genuine second derivation of this predicate and not
     * a restatement of it. */
    bool        prefilter_lang_nullable;

    /* [OPT-4.1] AND THE DECISION IT DROVE: a collapse RUNG asked for the
     * count-collapsed prefilter and nullability declined it, so this artifact
     * has NO prefilter. False on every other path, including the two rungs
     * when the language is not nullable, and including a pattern that simply
     * has no prefilter for one of the older reasons (a backreference, a linked
     * call, `-fno-prefilter`).
     *
     * IT IS A SEPARATE FIELD FROM THE PREDICATE ABOVE because they answer
     * different questions and three readers need the second one: the `_ENGINE_
     * SEL` ladder (which stamps `"declined-nullable"` on the [SEL-1] rung),
     * the `--emit-ir` listing's `; prefilter` line (which would otherwise name
     * a FLAG the caller did not pass), and the `fit.prefilter` clause that
     * makes the decision. A pattern can be nullable and keep an exact
     * prefilter all day; that is the default and it is not this field. */
    bool        prefilter_declined_nullable;

    /* [OPT-4.1] IS THERE A COLLAPSIBLE `A_REP` AT ALL — an `rmin > 1` or
     * `rmax > 1` the collapse would CHANGE? `pcrec_has_collapsible_rep(root)`
     * (src/opt/atomic.c), derived ONCE at `src/opt/select_engine.c`'s fit site
     * and read by BOTH conjuncts that need it: this pass's
     * `prefilter_declined_nullable` and `src/core/compile.c`'s `pfc_wanted`.
     *
     * IT IS A FIELD RATHER THAN TWO CALLS BECAUSE THE TWO SITES MUST NOT BE
     * ABLE TO DISAGREE, and they DID: the decline shipped without this
     * conjunct while the build gate had it (r47sel finding 1). A nullable
     * pattern that overflows the [SEL-1] cap with NO collapsible repeat then
     * stamped `_ENGINE_SEL "declined-nullable"` — a rescue REFUSED — when the
     * collapsed lowering IS the exact one and there was never a distinct
     * rescue to refuse. `match_api.md`'s own value table warns against exactly
     * that inversion, and the comparative bench buckets on this macro. */
    bool        prefilter_has_collapsible_rep;

    /* [OPT-4] WHY THAT LANGUAGE (D81's `_WHY`; `<PREFIX>_VM_PREFILTER_LANG_WHY`).
     *
     * FRANK'S RULING B (2026-08-29): the DEFAULT builds the EXACT prefilter and
     * the collapsed language is only ever a LADDER ATTEMPT — taken when the
     * exact machine cannot be built or its artifact cannot be shipped, never
     * because a state count crossed a knee. So every collapsing value below
     * names the ATTEMPT that took it, and there is no budget value left to
     * name: `PCREC_PREFILTER_EXACT_NFA_STATES` is gone.
     *
     *   PFLW_EXACT    the pattern's own language. The default outcome.
     *   PFLW_NO_REP   no collapsible `A_REP`, so the collapsed lowering IS the
     *                 exact one. Kept distinct from PFLW_EXACT because it is
     *                 the state `-fprefilter-collapse` is HONOURED but vacuous
     *                 in, and a caller who passed the flag and got `exact`
     *                 needs to know which of the two happened.
     *   PFLW_NULLABLE [OPT-4.1] there WAS something to collapse and the
     *                 collapse was DECLINED, because the collapsed language is
     *                 nullable and a nullable filter can never dismiss a
     *                 position. Kept distinct from both values above for
     *                 PFLW_NO_REP's own reason: a caller who passed
     *                 `-fprefilter-collapse` and got `exact` needs to know
     *                 that the flag reached a POLICY, not a vacuity.
     *                 Reachable only where a prefilter still exists to stamp,
     *                 i.e. under `-fprefilter-collapse`; on a RUNG the decline
     *                 leaves no prefilter and therefore no macro at all (that
     *                 outcome is `_ENGINE_SEL "declined-nullable"`).
     *   PFLW_FORCED   `-fprefilter-collapse`: collapse wherever a collapsible
     *                 repeat exists. The only route to literal
     *                 count-INDEPENDENCE now.
     *   PFLW_SEL1     the [SEL-1] rung: a DFA build overflowed a STATE cap and
     *                 the collapsed language is what stands between this
     *                 pattern and no prefilter at all.
     *   PFLW_SIZECAP  the size rung: the EXACT artifact was refused by an
     *                 emitted-size cap, and the collapsed prefilter is what
     *                 makes it shippable. Frank's ruling B in one value.
     *
     * `prefilter_lang_why >= PFLW_FORCED` iff `prefilter_collapsed`, and it is
     * STRUCTURAL rather than agreed: `src/core/compile.c`'s ladder branches on
     * the decision it just made, not on a re-walk of the conjuncts.
     *
     * THERE IS NO `denied` VALUE, and its absence is a measurement rather than
     * an oversight. Under ruling B `-fno-prefilter-collapse` denies the two
     * ATTEMPTS; on a pattern whose exact build succeeds it changes nothing (so
     * the honest stamp is whatever the default stamps — the byte-for-byte
     * recovery rule), and on a pattern that needed an attempt it turns a
     * compile into a REFUSAL or a prefilter into none, neither of which leaves
     * an artifact carrying this macro. A value no witness can reach is a value
     * that should not exist (the manager's "keep them witness-driven").
     *
     * `prefilter_nfa_states` is the EXACT forward NFA's size, MEASURED (D24),
     * recorded on every path. It is no longer compared against anything — the
     * knee is gone — but PFLW_SEL1 reports it, because the scale of the machine
     * the collapse avoided is the fact a reader of that value wants. */
    unsigned    prefilter_nfa_states;
    unsigned char prefilter_lang_why;

    /* [OPT-4] the emitted size that triggered PFLW_SIZECAP, and the cap it
     * exceeded, carried so the stamp can quote the comparison that caused the
     * retry. Zero on every other path. */
    unsigned long long prefilter_sizecap_bytes;
    unsigned long long prefilter_sizecap_limit;

    /* [OPT-4] HOW THIS ARTIFACT GOT ITS ENGINE, as a CLOSED VALUE SET
     * (`<PREFIX>_ENGINE_SEL`, D81; bench O-8's ask).
     *
     * WHY IT EXISTS BESIDE `why`, WHICH ALREADY SAYS SOMETHING. `why` is
     * PROSE — "capture group at pattern offset 18", "dfa overflowed: >32000
     * states at pattern offset 0" — written to be read by a person. A
     * CONSUMER cannot bucket on it: telling "auto picked the VM" from "auto
     * FELL BACK to the VM" means substring-matching English, and the
     * comparative bench had to. This is the same decision as a token.
     *
     * ONE DERIVATION, TWO READERS (D81): both come off this struct, written
     * once at `src/opt/select_engine.c`'s single `cx->job->fit = fit` site
     * from the driver's own attempt record.
     *
     * SEVEN VALUES since [LIM-1] (was six) — `ESEL_SIZE_CAP_RETRY` joined
     * at D90's fold-in — and the last five are all "fell back" with
     * different outcomes — which is exactly the distinction `why` cannot
     * carry. */
    unsigned char engine_sel;
} EngineFit;

/* [OPT-4] `EngineFit.engine_sel` — `<PREFIX>_ENGINE_SEL`'s closed value set.
 * Ordered so `>= ESEL_OVERFLOWED_DFA && <= ESEL_DECLINED_NULLABLE` reads "a
 * DFA build overflowed a STATE cap and this compile fell back", which is the
 * bucket the bench actually wants. [LIM-1] (2026-08-30) added
 * `ESEL_SIZE_CAP_RETRY` OUTSIDE that range on purpose — its own cap is the
 * emitted-SIZE one (`compile_driver`'s CR_SIZECAP rung), not a DFA state
 * cap, so folding it into the contiguous range above would make the
 * existing range test lie about what overflowed. A consumer wanting
 * "any fallback occurred, of any kind" now tests `>= ESEL_OVERFLOWED_DFA`
 * (unbounded above, since this is the last value); one wanting
 * specifically "a DFA state cap overflowed" needs the bounded range. */
enum {
    ESEL_FORCED               = 0,  /* the caller named --engine=vm/dfa */
    ESEL_SELECTED             = 1,  /* auto chose on the AST; nothing overflowed */
    /* everything from here is a FALLBACK after a DFA build overflowed a cap */
    ESEL_OVERFLOWED_DFA       = 2,  /* the DFA was to be the ENGINE; no prefilter survives */
    ESEL_OVERFLOWED_PREFILTER = 3,  /* the VM was already chosen; its prefilter was dropped */
    ESEL_COLLAPSED_PREFILTER  = 4,  /* [SEL-1]'s rung: a prefilter SURVIVED, count-collapsed */
    /* [OPT-4.1] a [SEL-1] OR [OPT-4] SIZE rung OFFERED and DECLINED: the
     * collapsed language is nullable, so the rescue would have shipped a
     * filter that can never dismiss. No prefilter survives — the artifact is
     * the pre-rung one — and this value is the difference between "the
     * collapsed machine overflowed/refused too" (ESEL_OVERFLOWED_DFA /
     * ESEL_SIZE_CAP_RETRY's own absence) and "the collapse was refused on
     * purpose". [LIM-1] (2026-08-30) WIDENED ITS REACH: it used to be
     * reachable ONLY from the [SEL-1] rung ("the SIZE rung's own decline
     * stays `selected`" was this comment's own claim, and it was WRONG the
     * moment the SIZE rung's own outcome got a value of its own below — a
     * SIZE-rung nullable decline was silently indistinguishable from an
     * ordinary `selected` compile, exactly the K35 shape this whole macro
     * exists to prevent). Both rungs' declines now read this value. */
    ESEL_DECLINED_NULLABLE    = 5,
    /* [LIM-1] (D90, 2026-08-30) THE SIZE RUNG'S OWN SUCCESS, FOLDED IN FROM
     * [LIM-1]'s brief. Before this value existed, a [OPT-4] SIZE-rung
     * rescue that SURVIVED (the collapsed prefilter shipped) stamped
     * `"selected"` — indistinguishable from an ordinary compile that never
     * hit any cap at all, so a consumer bucketing on this macro alone (the
     * bench's own O-10 use) could not tell "this artifact is smaller only
     * because the emitted-size cap forced a retry" from "nothing unusual
     * happened". `docs/spec/limits.md` §3.3's own [OPT-4] section already
     * named the gap without a fix: "the SIZE rung's own decline is not this
     * value... the route stays `selected`" was true of the DECLINE only,
     * and was silently ALSO being read as true of the rung's SUCCESS,
     * which this value corrects. Reachable ONLY from `collapse_reason ==
     * CR_SIZECAP` (src/core/compile.c) with a prefilter that survived —
     * tests/resource's `(a|b){1,30000}` cell is the standing witness. */
    ESEL_SIZE_CAP_RETRY       = 6
};

/* [OPT-4] `EngineFit.prefilter_lang_why`. Ordered so that everything from
 * `PFLW_FORCED` up is a collapsing outcome: see the invariant stated above. */
enum {
    PFLW_EXACT    = 0,
    PFLW_NO_REP   = 1,
    /* [OPT-4.1] a NON-collapsing outcome, so it sits BELOW the boundary: the
     * collapse was asked for and refused. Placing it above `PFLW_FORCED`
     * would break the `>= PFLW_FORCED iff prefilter_collapsed` invariant the
     * emitter's cross-check rides on. */
    PFLW_NULLABLE = 2,
    /* everything from here collapses */
    PFLW_FORCED   = 3,
    PFLW_SEL1     = 4,
    PFLW_SIZECAP  = 5
};

/* [OPT-4] `Ctx.collapse_reason` — WHICH ladder attempt asked for the collapsed
 * prefilter on this pass. `CR_NONE` on the default attempt and on every
 * attempt that is not a collapse retry. Maps 1:1 onto the two `PFLW_*` rung
 * values, which is the point: the driver decides, the stamp reports. */
enum {
    CR_NONE    = 0,
    CR_SEL1    = 1,   /* a DFA state cap overflowed ([SEL-1]'s rung) */
    CR_SIZECAP = 2    /* an emitted-size cap refused the exact artifact */
};
typedef struct {
    /* heap-held so longjmp cleanup sees consistent pointers */
    Nfa    nfa;      /* forward NFA (unanchored-wrapped for ENG_UNANCH) */
    Nfa    rnfa;     /* reversed-pattern NFA (ENG_UNANCH only) */
    Dfa    dfa;      /* forward DFA */
    Dfa    rdfa;     /* reverse DFA, non-pruning (ENG_UNANCH only) */
    /* [ENG-ABS] THE MATCH-HERE MACHINE (ENG_UNANCH only): the SAME subset
     * construction over the SAME `nfa`, rooted at `nfa.anch_start` — the
     * pattern's own first state, which `nfa_wrap_unanchored` deliberately
     * leaves addressable — so it is the forward machine WITHOUT the
     * start-anywhere self-loop. `<prefix>_match` runs it from `ctx->pos` and
     * needs no reverse pass, because the start is the question rather than an
     * answer. docs/design/anchored_match_unwrapped.md §2/§3. */
    Dfa    adfa;
    /* [ENG-ABS] Did that machine BUILD, on an artifact whose `_match` this
     * emitter writes? The emitter's axis-G `unwrapped` candidate is exactly
     * this predicate; false selects the search-and-filter fallback. */
    bool   anchored_ok;
    int    engine;   /* PCREC_ENG_*: which DFA SHAPE (unanch/attempt) */
    EngineFit fit;   /* [M4.5b] which ENGINE (dfa/vm), and why */
    /* [OPT-ALTCLS] D46 stamp source, filled by src/opt/altcls.c BEFORE
     * select_engine/emission ever run (docs/dev/plan.md's interaction note:
     * the pass runs before possessify/MRL/counter). Counts, not booleans,
     * for the same reason RX_VM_RUNGS is a mask rather than a scalar: a
     * pattern can carry more than one mergeable/factorable alternation and a
     * boolean would collapse that. Read by BOTH emitters (this pass touches
     * the AST before either engine is built, unlike possessify/revdet's
     * VM-only marks), so the stamp macro lives in the SHARED prologue
     * (pcrec_emit_prologue), not in emit_vm.c alone. Zero under
     * `-fno-altcls-merge`/`-fno-altcls-factor` by construction: the deny
     * checks sit at the top of the functions that would otherwise increment
     * these, so a denied build's stamp is indistinguishable from "nothing to
     * merge/factor here" — the same "no trace" rule possessify's denial
     * follows. */
    int    altcls_merges;    /* stage 1: alternation runs folded into one class */
    int    altcls_factored;  /* stage 2: alternation runs prefix-factored */
    /* [M6.5.2] WHICH ENCODING RESIDUAL ENTRIES THIS ARTIFACT NEEDS — an OR of
     * PCREC_ENCE_* (src/gen/enc/enc.h). `PCREC_ENCE_NEXT_POS` is always in it
     * (docs/spec/match_api.md §3.1 promises that entry unconditionally); the
     * two backreference entries are added by the VM emitter as it emits them,
     * so the mask is DISCOVERED BY EMITTING rather than predicted by a second
     * walk — the same discipline the class pool and the cursor local already
     * follow, and the reason the prologue is written after the program body.
     *
     * A backref-free artifact therefore carries exactly the residual text it
     * always did, which is what makes §11.3's byte-identity gate hold for the
     * seam as well as for the engine. */
    unsigned enc_mask;
    StrBuf csb, hsb;
    /* [M4.5b] the VM emitter's scratch buffer for the matcher's BODY. It is
     * Job-owned rather than a local in pcrec_emit_vm for one reason: the body
     * must be produced BEFORE the text that precedes it (the class pool, the
     * cursor local, RX_NSTATE are all discovered by emitting), and any
     * ctx_fail during that emission longjmps out — a stack-local StrBuf would
     * leak its heap buffer on exactly the path the sanitizer battery checks. */
    StrBuf vmsb;
    /* [M4.5c] the emitted-program LISTING (DD-8, engine_m4.md S10), filled
     * only when Ctx.want_ir is set. Job-owned for vmsb's reason. */
    StrBuf irsb;
    /* [ART-SIZE] the VM emitter's two SCRATCH buffers, Job-owned for vmsb's
     * reason and found the same way: r42's S3 fix armed `vmsb`'s early abort,
     * so a size-term ladder trial now longjmps out from INSIDE the emission —
     * and the union battery's LeakSanitizer axis caught the two function-local
     * StrBufs that were live at that moment (the span-loop's inline test text
     * and a class description in the listing), 2 x 256 B on the R1 witness.
     * A scratch buffer is RESET (len = 0) at each use and never freed by its
     * user; `job_cleanup` frees both on every path. */
    StrBuf scr_test, scr_desc;
    /* [M4.7b/K7] Strings taken out of the three buffers above and not yet
     * handed to the caller — Job-owned for exactly that window, so an
     * allocation failure between two takes frees rather than strands them.
     * NULL at every other moment; see compile_driver's tail. */
    char *out_c, *out_h, *out_ir;
    /* [ART-SIZE] The emitted VM node count this run produced — `Vm.nlabel`,
     * published here at the end of `pcrec_emit_vm` because the size term's
     * ladder needs it and `Vm` is emitter-local. It is the SAME number
     * `--emit-ir`'s "program N labels" line prints, so the two cannot drift.
     * 0 on a DFA artifact, which has no VM nodes. */
    int vm_emitted_nodes;
    /* [ART-SIZE] The rung bitmask this run emitted (`Vm.rungs`, the same value
     * `<PREFIX>_VM_RUNGS` stamps). The size term reads ONE bit of it: the
     * COUNTER rung's. `K` is the counter rung's chunking factor and affects
     * NOTHING else, so a pattern whose artifact never took that rung cannot
     * change size at any K, and running the ladder on it is provably wasted
     * work. Bit 4 (0x10) — kept in step with emit_vm.c's `vm_rung_bit[]` by
     * the same contract `<PREFIX>_VM_RUNGS`'s own block states. */
    unsigned vm_rungs;
    /* [ART-SIZE] THE ARTIFACT'S DECLARED CAPACITY, published for the size
     * term's ladder the same way and for a sharper reason than the two above.
     * These are the exact values `rx_info`'s `.frame_capacity` and
     * `.subject_ceiling` carry (D44.1: what the artifact ENFORCES, learnable
     * without triggering PCREC_ERR_FRAMES), captured per attempt.
     *
     * MEASURED, and this is why the fields exist: `K` is answer-identical in
     * the LANGUAGE and NOT in the DEPTH an artifact reaches. `^(a(?1)?b)$`
     * stamps `subject_ceiling` 512 at the default K and 341 at K=1 — a
     * smaller K raises the per-iteration frame need, so the same default
     * budgets carry a shorter subject. A compiler-chosen K that turns a
     * MATCH into a frames give-up is an answer change no flag asked for, so
     * `size_term_choose` treats a rung that would LOWER either number as not
     * a candidate at all (docs/design/artifact_size_term.md §3.3a). An
     * explicit `--unroll=K` may still lower it: that is the caller's own
     * choice, and `docs/spec/limits.md` says so.
     *
     * Sentinels are the emitter's: `frame_capacity` -1 = unbounded,
     * `subject_ceiling` 0 = unset/not applicable. BOTH mean "no bound" and
     * therefore compare as +infinity, never as zero — a rung that declares a
     * ceiling where the default declared none has LOWERED it. */
    long long vm_frame_capacity;
    long long vm_subject_ceiling;
} Job;

/* [M6.3] module `named-groups` — see Ctx.named_groups below for the full
 * rationale. Arena-owned: `name` is a NUL-terminated copy made at
 * declaration time, and the node itself is never freed individually. */
typedef struct NamedGroup {
    const char         *name;
    int                 number;   /* the group's capture number, 1-based */
    struct NamedGroup  *next;
} NamedGroup;

/* [M6.5.2] module `backrefs` — ONE PENDING REFERENCE, recorded by whichever
 * spelling produced it and resolved once at END OF PARSE
 * (docs/design/backrefs_design.md §5.3).
 *
 * WHY DEFERRED AT ALL. PCRE2's rule 2 makes `\1`..`\9`'s VALIDITY a
 * whole-pattern question — `\1(a)` compiles, the group is AFTER the escape —
 * and the relative and by-name forms need the final count and the complete set
 * of declarations too (`\g{+1}(a)` is legal; a duplicated name's run is not
 * complete until the pattern ends). One deferred list gives three properties
 * at once: forward references (§3.5) are legal BY CONSTRUCTION rather than by
 * an exception, there is exactly ONE site that decides what "group k exists"
 * means so the numeric, relative and by-name spellings cannot disagree, and
 * the dupnames run resolution (§8.3) happens where every declaration is
 * already known.
 *
 * RULE 3 IS THE EXCEPTION AND MUST STAY ONE: the backref-vs-OCTAL decision for
 * a multi-digit run beginning 1-7 is made AT the escape from `Ctx.ncap`'s
 * count SO FAR, because deferring it would let a later group retroactively
 * turn an octal literal into a backreference. `\10(a)..(j)` is the measured
 * boundary — octal 010, not a reference to group 10.
 *
 * Arena-owned and threaded like `NamedGroup`; `name` is an arena copy. */
/* [DD-14 wave B+C] WHICH RULE THE RESOLVER APPLIES (subroutines_design.md
 * §4.2). ONE LIST AND ONE PASS, not a second list beside it: the pass's whole
 * justification is that it is the ONE site that knows both the final group
 * count and every declaration of a duplicated name, and that is as true of a
 * subroutine call as of a backreference.
 *
 * THE TWO RULES DIFFER IN THE NAME ARM AND NOWHERE ELSE:
 *
 *   PEND_BREF  by number: that group. by NAME: the whole RUN of groups with
 *              that name, ascending — the emitted chain picks the first SET
 *              member at MATCH time (§8.3 of backrefs_design.md).
 *   PEND_CALL  by number: that group, one number. by NAME: the FIRST
 *              DECLARATION with that name, STATICALLY, whether or not it is
 *              set, and a call never retries into the later members —
 *              MEASURED on 10.46 across all four by-name call spellings
 *              (subroutines_design.md §3.4(c)): under DUPNAMES,
 *              `^(?:(?<a>x)|q)(?<a>y)(?&a)$` matches "qyx" and refuses "qyy",
 *              while the `\k<a>` REFERENCE does the opposite.
 *
 * THE ZERO CASE IS NOT A THIRD DIFFERENCE. `(?R)`/`(?0)`/`(?00)` target the
 * AST ROOT, which always exists, so the port answers them itself and queues
 * NOTHING — see `src/parse/mod_recursion.c`'s header. A number that reaches
 * this list is therefore out of range at 0 for BOTH kinds, which is what keeps
 * `(a)(?-2)` (a relative offset computing to zero) an error-115 rather than a
 * silent `(?R)`. */
typedef enum { PEND_BREF, PEND_CALL } PendKind;

typedef struct PendingRef {
    Ast                *node;    /* the A_BREF whose `refs` this fills in, or
                                  * the A_CALL whose `target`/`body` it does */
    PendKind            kind;
    /* An absolute group number, read only when `name` is NULL. It may be ZERO
     * OR NEGATIVE: `\g{-1}` at a count of zero computes 0, and whether a
     * number names a group is the ONE question this list defers. Splitting
     * that check between the port and the resolver would be the second home
     * §5.3 exists to prevent — and it was a real defect, not a hypothetical:
     * it made the `\g` row's own `syntax` refuse at the port, so D65's
     * built-status column called a construct this module BUILDS `unbuilt`. */
    int                 number;
    const char         *name;    /* NULL selects `number`; else resolve this */
    size_t              at;      /* pattern offset the diagnostic points at */
    const char         *what;    /* the spelling, for that diagnostic */
    struct PendingRef  *next;
} PendingRef;

struct Ctx {
    Arena                arena;
    const char          *pat;
    size_t               patlen;
    size_t               pos;      /* parser cursor */
    int                  depth;    /* parser group-nesting depth (bounded) */
    /* [M4-QUOTING] module `quoting`'s lexer-mode flag (design's own words,
     * RF_LEXICAL's comment above: "a TOKENIZER MODE, not an atom"). True
     * from a NON-EMPTY `\Q` through its `\E` (or true end of pattern, the
     * unterminated case) -- an EMPTY `\Q\E` never sets it, because it is
     * fully transparent and never reaches p_atom/p_class at all (xskip/
     * cls_skip dissolve it before either is called; see parse.c). While
     * true, p_atom and p_class's main loop read raw bytes literally instead
     * of dispatching through the ordinary switch/registry doorway -- the
     * ONLY state this flag changes. `cat_ends`/`xskip`/`cls_skip` are the
     * three places that must close it on `\E` (or true end) BEFORE deciding
     * whether a cat/class item boundary has been reached; see their own
     * comments in parse.c for why the close has to happen there and not
     * inside the quoted-byte reader itself. */
    bool                 in_quote;
    /* SCOPED PARSE STATE (PARSE-1; widened to a struct at MOD-0.5c, the
     * D31-note's "expect a struct, not more bools"). Seeded at parse entry
     * and saved/restored around every BODY-CARRYING group, because that is
     * where PCRE2 restores it: measured 17/17 against libpcre2 10.46,
     * `(?i)` set anywhere inside a group stays in force to the end of THAT
     * group — it leaks across sibling alternation branches, `(a(?i)b|c)d`
     * matching `Cd` — and is restored at the immediately-enclosing `)`, not
     * the outermost one. A top-level `(?i)` is never restored. A BARE option
     * run `(?i)` deliberately escapes its own paren pair's restore — it is an
     * option-setting construct spelled with parens, not a group with a body —
     * which is why the save/restore lives on p_group_body's body-parsing
     * tail, not unconditionally in p_group (the placement IS the scope rule).
     *
     * `opt` is const and caller-owned, so it CANNOT hold this: a module doing
     * D29's "set parse state, parse body, restore" has nothing to set.
     * Module `modifiers`' port (mod_modifiers.c) is the only writer.
     *
     * [M6.2 wave A] IT IS AN OPAQUE POINTER, AND THAT IS THE POINT
     * (assertions_design.md §8.2/§8.6, D62). The invariant is: *scoped
     * modifier state is resolved AT PARSE TIME, onto the node; no post-parse
     * pass reads it.* That was a sentence someone had to remember, and the
     * one pass that forgot — src/opt/possessify.c, reading
     * `cx->mods.multiline` at verdict time, i.e. the parser's END-OF-PATTERN
     * state — was a shipped miscompile waiting for `(?m)` to be accepted.
     * `ParseMods` is now defined ONLY in `src/parse/parse_mods.h`, so this
     * member is an INCOMPLETE TYPE everywhere else: a future analysis in
     * src/opt/, src/ir/, src/gen/ or cli/ that tries to consult it does not
     * produce a subtly wrong verdict, it fails to compile. The enforcement is
     * what stops the invariant decaying; a future `(?X)` modifier physically
     * cannot be consulted after the parse.
     *
     * NULL until `pcrec_parse_mods_init` runs. Every Ctx that can reach a
     * parser or a doorway port calls it — see that function. */
    /* [ART-SIZE] What the size term decided, set by compile_driver before the
     * FINAL emission and read by the stamp block (D81: a selection fact is
     * stamped whether or not it fired, so `size_term_why` is never NULL on a
     * VM artifact). It is computed in the DRIVER and not in the emitter
     * because only the driver has seen the whole ladder — an emitter run knows
     * its own K and nothing about the alternatives it was chosen over. */
    const char          *size_term_why;
    ParseMods           *mods;
    /* THE RUNNING CAPTURE COUNT (MOD-0.1, design §18.1 as Frank resolved
     * it: there is NO scanner). Incremented at p_group_body's capturing-`(`
     * hook — group numbers are assigned by opening-paren order, so the
     * count AT a point in the parse is what PCRE2's multi-digit
     * octal-vs-backref rule consults (`\12` is a backreference iff the
     * RUNNING count >= 12, else octal; the TOTAL is irrelevant there). The
     * count at END of parse is the whole-pattern total, which is what
     * validates `\1`..`\9` — deferred resolution: module `backrefs` records
     * pending references and checks them against the final value, and its
     * pending list lands WITH that module (a list nothing can write is
     * unexercised structure, D33 §9.3 / D24's recorded loss — the judgment
     * is in the 2026-08-11 journal entry). Today the count feeds
     * `--count-groups`, the external channel tests/spec_mod0/check02
     * compares against libpcre2's CAPTURECOUNT and err-115 boundary. */
    unsigned             ncap;
    /* [M4.5b] Does this compile want capture OFFSETS out of the matcher?
     * engine_m4.md §5.3: the selection input is the requested OUTPUT, not the
     * presence of a `(`. Seeded from PCREC_NO_CAPTURES at compile entry and
     * read at exactly one place, p_group_body's capturing-`(` hook, which is
     * what makes "--no-captures reproduces today's AST" true by construction
     * rather than by a later erasure pass. Cleared for pcrec_count_groups and
     * the syntax-query surfaces, which never emit. */
    bool                 want_caps;
    /* [M4.5c] Produce the emitted-program listing alongside the artifact
     * (DD-8's `--emit-ir`). A QUERY, not a generation axis: it changes what
     * pcrec REPORTS, never a byte of what it emits — which is why it lives on
     * Ctx rather than in pcrec_options, and why the listing is rendered from
     * the emitter's own event stream instead of from a second walk. */
    bool                 want_ir;
    /* [ENG-BREP] the possessification pass's own census, set by
     * pcrec_possessify on every call (SET, not accumulated, so the fixpoint's
     * second round reports the final state rather than double-counting).
     * `poss_total` counts A_REP nodes in the SOURCE tree, which is the only
     * quantifier population comparable with eng_brep_design.md §2.6's — the
     * emitter's rung marks count a replicated body's copies once EACH, so a
     * census read off those measures replication as much as it measures
     * quantifiers. Reported in --emit-ir's header; nothing else reads it. */
    int                  poss_marked, poss_total;
    /* Pattern offset of the FIRST capturing `(`, or SIZE_MAX if none — the
     * engine_why stamp's `why_pos` (§5.5). */
    size_t               first_cap_pos;
    /* [M6.2 wave E] Pattern offset of the FIRST `\K`, or SIZE_MAX if none.
     *
     * IT IS THE DIAGNOSTIC'S SOURCE AND NOT THE VERDICT'S, deliberately.
     * `forces_kreset` (src/opt/select_engine.c) answers "does this AST carry
     * an A_KRESET" by WALKING THE TREE, because that is the honest question —
     * the reported start is path-dependent exactly when such a node exists,
     * and a parse-time counter would keep saying VM after a future rewrite
     * deleted the node. This field only supplies the `engine_why` stamp's
     * offset, which the AST has no room for (no node carries a source
     * position). It is read ONLY when the walk already found a node, so it
     * cannot be stale in the direction that matters. */
    /* [M6.4.2 / SR-8, D67] Pattern offset of the FIRST construct whose
     * registry row EXCLUDES the DFA, or SIZE_MAX if none.
     *
     * IT REPLACES `first_kreset_pos` AND `first_atomic_pos`, which is the
     * retirement D67 asks for: with the consultation generic, a per-construct
     * position field would be a per-construct home for a fact the ONE stamp
     * call already has in hand. `pcrec_ast_stamp` is that call and the only
     * writer, so the offset and the `Ast.reg` it belongs to are recorded in
     * the same statement.
     *
     * IT IS THE DIAGNOSTIC'S SOURCE AND NOT THE VERDICT'S, exactly as
     * `first_kreset_pos` was. `forces_registry` (src/opt/select_engine.c)
     * answers "does this POST-DISCHARGE tree carry a DFA-excluding node" by
     * WALKING, because that is the honest question and because the free
     * discharge DELETES nodes a parse-time counter would keep counting. This
     * field only supplies the `engine_why` stamp's offset, which no AST node
     * carries. It is read ONLY on the path where the walk already found a
     * node, so it cannot be stale in the direction that matters; on a tree
     * where a rewrite deleted SOME but not all of them, the offset and the
     * `why` TEXT (which comes from the surviving node's own row) can name
     * different occurrences — D26 tier-3 wording, not a verdict. */
    size_t               first_vmonly_pos;
    /* [M4.7b/K7] Running total of NFA-state-list ELEMENTS interned by the
     * subset construction, across every machine this compile builds (forward
     * and reverse are charged to one budget because they are both live at
     * once). This is the compile's dominant memory term and the one nothing
     * bounded — see PCREC_MAX_SUBSET_ELEMS in limits.h for the growth law and
     * the number. Charged in src/ir/dfa.c's intern(). */
    long long            subset_elems;
    /* [SEL-1] (2026-08-28) `auto`'s DFA-cap-overflow contract (plan row
     * [SEL-1]): a `--engine=auto` compile whose DFA build overflows a cap
     * falls back to the VM instead of refusing, and an auto-selected
     * prefilter whose DFA overflows is dropped. The FORCE forms
     * (`--engine=dfa`, `-fprefilter`) stay do-or-die, unchanged.
     *
     * THE GENERAL MECHANISM: the DFA build reports "over budget" as a
     * RESULT the selector's existing fixpoint consumes, not as a special
     * case at the `ctx_fail` site. There is exactly one recovery point in
     * this compiler (`compile_driver`'s single `setjmp`), so the fallback is
     * a ONE-SHOT RETRY of the whole pipeline rather than a second recovery
     * point wrapped around the DFA build — `src/core/compile.c`'s retry
     * loop is the only place that decides to retry, and
     * `src/opt/select_engine.c`'s `forces_dfa_overflow` is the only place
     * that reads these fields.
     *
     * `dfa_overflowed` and `dfa_overflow_why` are WRITTEN by the two
     * "pattern too complex" `ctx_fail` sites in src/ir/dfa.c, immediately
     * before the `longjmp` — plain fields on `Ctx` rather than arena text,
     * because the retry decision runs in `compile_driver` AFTER
     * `job_cleanup`'s `arena_free` has already run on the failed attempt.
     * `dfa_disabled` is the retry's own INPUT, seeded true only on the
     * second (and last) pass compile_driver runs after an eligible
     * overflow: `forces_dfa_overflow` treats it exactly like a VM_ONLY
     * registry row (excludes ENGM_DFA from the very fixpoint
     * `forces_captures`/`forces_registry` already drive), and the prefilter
     * derivation drops the prefilter under it too — a retry's own DFA build
     * would be the IDENTICAL construction that just overflowed, so
     * attempting it again would cost a second refused build the plan row's
     * cost bound (at most one refused build dearer than `--engine=vm`)
     * forbids. See PCREC_DFA_OVERFLOW_WHY_LEN (limits.h) for the buffer's
     * sizing. */
    bool                 dfa_disabled;

    /* [OPT-4] WHY THIS ATTEMPT IS BUILDING THE COLLAPSED PREFILTER, or
     * `CR_NONE` if it is not. Ruling B's whole selector: the collapse is never
     * chosen by measuring the pattern, only by an ATTEMPT the driver decides to
     * make after something has already failed.
     *
     * ONE FIELD RATHER THAN A BOOL PER RUNG, because the two rungs differ only
     * in what failed and what the stamp should say, and a second bool would be
     * a second thing to keep in step with the first. `compile_driver` sets it;
     * the build gate reads it as "force the collapse"; the `_LANG_WHY`
     * derivation reads it for the reason. */
    unsigned char        collapse_reason;   /* CR_* */

    /* [OPT-4] set at the emitted-size cap's own `ctx_fail` sites, immediately
     * before the refusal, so `compile_driver` can tell a size refusal from
     * every other `ctx_fail` that arrives at the same `setjmp`. This is
     * `dfa_overflowed`'s shape exactly, and for the same reason: there is ONE
     * recovery point in this compiler, so a rung that wants to act on a
     * particular failure has to label it where it happens. */
    bool                 size_cap_refused;
    unsigned long long   size_cap_bytes;    /* what the artifact measured */
    unsigned long long   size_cap_limit;    /* what it exceeded */

    /* [OPT-4] ON THE ATTEMPT THAT OVERFLOWED, was the DFA to be the ENGINE?
     * Seeded by `compile_driver` alongside `dfa_disabled` and meaningful only
     * when that is true. It is the one fact separating
     * `ESEL_OVERFLOWED_DFA` from `ESEL_OVERFLOWED_PREFILTER`, and it cannot be
     * recovered on the retry: by then the DFA is excluded from selection
     * outright, so every fallback attempt reports `chosen == ENGM_VM` whatever
     * the first attempt wanted. Recorded where it is still true, carried like
     * `dfa_overflow_why` and for the same reason. */
    bool                 dfa_was_engine;
    bool                 dfa_overflowed;
    char                 dfa_overflow_why[PCREC_DFA_OVERFLOW_WHY_LEN];
    /* [DD-14 wave B+C] THE CALL GRAPH, or NULL for a call-free pattern.
     * Built by `pcrec_callgraph_build` (src/opt/callgraph.c) AFTER every
     * rewriting pass and before emission — see that function's declaration for
     * why the position is load-bearing rather than convenient. Arena-owned and
     * opaque: its readers are the emitter and nothing else. */
    struct CallGraph    *callgraph;
    /* [M6.3] module `named-groups`: every DECLARED (name, group-number)
     * pair, threaded as an arena-allocated singly linked list in
     * declaration (opening-paren) order — `named_groups` is the head,
     * `n_named_groups` its length. This is a LEXICAL fact about the
     * pattern text, the same tier `ncap`/`ngroups` already are (recorded
     * whether or not `want_caps` is set — a --no-captures build still
     * knows a group's NAME, it simply delivers no caps[] slot for it), so
     * it is populated unconditionally by the module's parser port
     * (src/parse/mod_named_groups.c) and left NULL/0 by every pattern with
     * no named group. src/gen/emit_dfa.c's emit_info_def reads it once, at
     * the end of parse, to build the SORTED `rx_group_entry` array
     * docs/spec/match_api.md §6 promises (sort key: strcmp on the name —
     * PCRE2's own PCRE2_INFO_NAMETABLE is sorted exactly this way,
     * measured directly in tests/probes/probe_named_groups.c, which is
     * this decision's evidence). */
    NamedGroup          *named_groups;
    unsigned             n_named_groups;
    /* [M6.5.2] module `backrefs`: every reference this pattern made, in
     * REVERSE declaration order (prepended, like `named_groups` above), and
     * how many. Resolved in one pass by `pcrec_bref_resolve` at the end of
     * `pcrec_parse_info`. NULL/0 for every pattern with no backreference,
     * which is what makes the whole mechanism cost a backref-free compile
     * nothing. */
    PendingRef          *pending_refs;
    unsigned             n_pending_refs;
    jmp_buf              jb;
    pcrec_error         *err;
    const pcrec_options *opt;
    Job                 *job;
};

/* [M6.2 wave A] `Ctx.mods`' type is DELIBERATELY INCOMPLETE HERE (§8.6): the
 * definition lives in src/parse/parse_mods.h and nothing outside src/parse/
 * includes it, so "no post-parse pass reads cx->mods" is a compile error
 * rather than a review finding. Seed it before any parse or doorway call. */
void pcrec_parse_mods_init(Ctx *cx);         /* src/parse/parse.c */

/* PARSE-1: what `p_alt` reports about the alternation it just parsed.
 *
 * WHY THIS IS A STRUCT AND NOT AN `int`. The measured requirement is a branch
 * COUNT — conditionals are error 127 above 2 top-level branches and
 * `(?(DEFINE)` is error 154 above 1 — but `ctx_fail(cx, pos, ...)` takes a
 * POSITION as a required argument, so a module cannot RAISE that error with a
 * count alone. D26 puts pinning pcrec's own offsets against pcrec's own
 * convention in tier 2; only chasing PCRE2's specific number is tier 3. And a
 * per-branch position is not recoverable after the fact: `Ast` has no position
 * field of any kind, so a design that leaves the AST alone forecloses it
 * unless `p_alt` reports it. One `size_t` at the site that already touches
 * `cx->pos` costs the same as the count.
 *
 * `nbr` counts TOP-LEVEL branches, so it is 1 for an alternation-free body and
 * never 0. `last_bar` is the offset of the LAST `|` p_alt consumed, or
 * SIZE_MAX when there was none — the offending separator for a
 * "too many branches" diagnostic. */
typedef struct {
    int    nbr;
    size_t last_bar;
} AltInfo;

void ctx_fail(Ctx *cx, size_t pos, const char *fmt, ...)
     __attribute__((noreturn, format(printf, 3, 4)));

/* [M4.7b/K7] The ONE diagnostic for a failed allocation on the compile path,
 * so every such site reads the same and none of them has to invent wording.
 * It is ONE message on purpose: naming which internal table could not grow
 * would tell a caller nothing they can act on, and the two things they CAN do
 * — shrink the pattern, or raise the limit — are the same whichever it was.
 *
 * `pos` is 0 (whole-pattern) at every site: an allocation failure is a property
 * of the pattern's total cost, not of a byte in it. */
void ctx_nomem(Ctx *cx) __attribute__((noreturn));

/* ---- syntax construct registry (D24 / SR-1) ----
 *
 * ONE declarative home per non-base construct. Before this table a single
 * construct's identity lived in up to five places (esc_modules[],
 * esc_char_value's switch, the (?X ternary chain, tests/reject/, the
 * compliance report); `\v` shipped wrong because the first two disagreed ten
 * lines apart with nothing enforcing that they agree.
 *
 * The table describes constructs OUTSIDE the base tier only. Base syntax
 * (literals, `.`, classes, quantifiers, `|`, `(...)`, `^`, `$`, and the plain
 * character escapes \n \t \r \f \a \e \xHH) stays in parse.c and never
 * consults the registry. MEASURED 2026-08-10 (R6): that makes the base tier
 * CHEAP, not lookup-free — `[abc]` costs one lookup at the class-bracket
 * doorway and three for a typical class-heavy pattern, while `(?:` costs zero
 * because parse.c answers it before the registry. SR-5 must guard the measured
 * property, not the claimed one.
 *
 * Rows are pure `static const` data. A runtime-mutable registry is rejected
 * because it would be file-scope mutable state in the compiler, which D19's
 * "usable FROM threads" property forbids. Note what actually guards that:
 * D19's COMPILER-side property is audited by hand, NOT mechanized — TS-1 scans
 * emitted output only and would not notice a mutable global added here.
 *
 * Per-compile SELECTION of flavour and feature mask is the DESIGN (D24), not
 * the present tense: pcrec_options carries no flavour or enablement field, and
 * nothing outside tests/registry/ reads the feature/flavour/engine columns. */

typedef enum {
    RK_ESC,           /* doorway 1: after '\'             — one byte decides */
    RK_GROUP,         /* doorway 2: after '(?'            — one byte decides */
    RK_VERB,          /* doorway 3: after '(*'            — a NAME decides   */
    RK_CLASSBRACKET,  /* doorway 4: after '[' in a class  — one byte decides */
    /* [M6.4.2] NOT A DOORWAY — the one kind in this enum that no lookup on
     * the parse path ever consults, and that is deliberate rather than an
     * omission.
     *
     * The possessive quantifier suffixes (`a*+` `a++` `a?+` `a{n,m}+`) are
     * QUANTIFIER SUFFIXES, not atoms: they are recognised by `p_rep` in
     * src/parse/parse.c, after `try_quant` has already accepted the
     * quantifier. This file's header records the exemption and its reason —
     * inventing a doorway for them would cost the BASE tier a registry lookup
     * on every quantifier — and that reason is preserved exactly: no doorway
     * consults this kind, `pcrec_registry_find` is never called with it, and
     * the parse path is byte-for-byte what it was.
     *
     * THE ROWS EXIST FOR THE DUMP. Without them `--list-syntax` and the
     * generated index in docs/pcre2_compliance.md would say `(?>...)` is BUILT
     * and say NOTHING AT ALL about `*+ ++ ?+ {n,m}+`, so a reader could not
     * tell "not implemented" from "not in the table" — a D26 tier-2
     * (RECOGNITION) discoverability defect. `registry.c` already carries the
     * precedent for a row that "exists so the table is complete for the dump"
     * (`(?:`, which the base grammar answers before the registry is reached).
     *
     * WHAT IT COSTS, because a fifth kind raises NO `-Wswitch` alarm — every
     * `RegKind` switch in the tree carries a `default:`, MEASURED at 28 files
     * offered / 28 clean / 0 diagnostics
     * (atomic_groups_measurements/probes/probe_rk_alarm.sh). The exposure is
     * therefore the hardcoded kind ARRAYS and the enumerations-by-CALL, which
     * no compiler and, before [M6.4.2], no check could see. All of them are
     * enumerated in atomic_groups_design.md §7.4 (eleven sites), and
     * `tests/registry/registry_check.c`'s per-kind check now reads the
     * `--list-syntax` OUTPUT — the only formulation that can see an omission
     * from one of those arrays at all, since iterating RK_COUNT over
     * registry.c would share a source with what it checks. */
    RK_QUANTSUFFIX,
    /* [DD-11.1] manager ruling, 2026-08-29: `RK_QUANTSUFFIX`'s own precedent
     * ("NOT A DOORWAY" — see its own comment above), applied a second time.
     * `^`, `$` and the plain capturing group `(...)` are base grammar with
     * NO doorway at all — parsed directly in `p_atom`/`p_group_body`,
     * unlike the literal escapes (which route through the real `\`
     * doorway even when answered before reaching the registry) — so they
     * had NO `RegRow` home to attach `RegRow.definitions` (D85) to. Named
     * `RK_BARE` rather than `RK_ANCHOR`: `(...)` is not an anchor, and the
     * kind is for "a base-grammar construct with no doorway" generally,
     * not for anchors specifically. Same discipline as `RK_QUANTSUFFIX`:
     * `pcrec_registry_find`/`arbitrate` are NEVER called with it, the rows
     * exist for the DUMP and for D85's definitions machinery, and every
     * site enumerating `RegKind`s explicitly needs a new arm — grep
     * `RK_QUANTSUFFIX` across the tree for the site list this addition
     * used to find them all (docs/design/atomic_groups_design.md §7.4 is
     * the precedent's own worked example of what "every site" means). */
    RK_BARE,
    RK_COUNT
} RegKind;

/* Which module owns the construct. A mask, not an index: `(?<` is genuinely
 * two constructs sharing one byte (lookbehind and named group). */
enum {
    FEAT_CLASSES       = 1u << 0,
    FEAT_ASSERTIONS    = 1u << 1,
    FEAT_BACKREFS      = 1u << 2,
    FEAT_UNICODE_PROPS = 1u << 3,
    FEAT_QUOTING       = 1u << 4,
    FEAT_MISC          = 1u << 5,
    FEAT_LOOKAROUND    = 1u << 6,
    FEAT_NAMED_GROUPS  = 1u << 7,
    FEAT_ATOMIC_GROUPS = 1u << 8,
    FEAT_COMMENTS      = 1u << 9,
    FEAT_CALLOUTS      = 1u << 10,
    FEAT_BRANCH_RESET  = 1u << 11,
    FEAT_CONDITIONALS  = 1u << 12,
    FEAT_RECURSION     = 1u << 13,
    FEAT_MODIFIERS     = 1u << 14,
    FEAT_VERBS         = 1u << 15,
    /* MOD-0.3a (2026-08-12): `(?[...])` split out of `classes` the day the
     * classes producers began — an enabled module must never still refuse a
     * construct while naming itself, and set-operation classes are real
     * work `classes` does not contain. The registry row's own comment had
     * reserved this call for whoever implemented the doorway. */
    FEAT_EXTENDED_CLASSES = 1u << 16
};

/* Flavour: which construct a byte MEANS. Exactly one today, by design — D18's
 * earn-its-axis rule applied to the front end. SR-7 adds the rest; the column
 * exists now so a second flavour REBINDS A ROW instead of adding a branch
 * inside a handler. */
enum { FLAV_PCRE2 = 1u << 0 };

/* Engine capability: which engine the construct can LOWER to. NOT a parsing
 * question — `\1` parses fine and simply cannot become a DFA. NOTHING CONSUMES
 * THIS COLUMN YET; it turns on at SR-8, when M4's VM gives the parser a second
 * engine to choose between. Until then the values are recorded DESIGN INTENT,
 * not measured behaviour, and no test may assert on them beyond well-formedness. */
enum {
    ENGM_DFA = 1u << 0,   /* the shipped DFA engines (ENG_UNANCH, ENG_ATTEMPT) */
    ENGM_VM  = 1u << 1    /* the backtracking VM (M4, not built) */
};

typedef enum {
    RS_BASE,      /* implemented today, by the base grammar */
    RS_MODULE,    /* known and unimplemented; `module` names what would implement
                     it. A complete, tested outcome — not a stub */
    RS_REJECTED   /* PCRE2 rejects it too, so agreement IS compliance and there
                     is no module to name (POSIX collating elements) */
} RegStatus;

/* D65 (2026-08-21, ratifying docs/design/registry_built_status_memo.md): a
 * THIRD axis, orthogonal to RegStatus (is this base grammar?) and Roadmap
 * (will a module ever implement it?) — has the OWNING module's producer
 * actually landed for THIS construct. Deliberately not a fourth RegRow
 * field: `pcrec_construct_built_status()` (src/parse/syntax_dump.c) DERIVES
 * it, per row, by driving the row's own `syntax` through a gate-forced-open
 * doorway call — the same reason ext.c's UNBUILT macro comment gives for
 * not adding "a second built column somebody would have to keep in sync
 * with the ports". PCREC_BUILT_NA is the answer for RS_BASE/RS_REJECTED
 * rows (the question does not arise); PCREC_BUILT_DEFECT is a row whose
 * own well-formed `syntax` produced neither a clean answer nor the
 * enabled-but-unbuilt refusal shape — a registry defect, never a status,
 * which tests/registry/registry_check.c asserts never happens rather than
 * silently rendering. */
typedef enum {
    PCREC_BUILT_NA = 0,
    PCREC_BUILT_YES,
    PCREC_BUILT_NO,
    PCREC_BUILT_DEFECT
} PcrecBuiltStatus;

/* The stable substring both ext.c's UNBUILT macro (which renders it) and
 * pcrec_construct_built_status (which recognises it) key on, so a reworded
 * refusal cannot silently stop being classified — one define, not two
 * copies of the sentence (D65's memo, "Risks and the check-design
 * question"). */
#define PCREC_UNBUILT_MARKER "is enabled but"

/* Which diagnostic the construct produces. Kept as data so SR-2's dispatch is
 * a mechanical substitution and byte-identity is provable. */
typedef enum {
    RD_NONE,          /* compiles; no diagnostic */
    RD_MODULE,        /* the doorway's template + `module` */
    RD_MODULE_OCTAL,  /* atom form only: "\N (backreference/octal) requires ..." */
    RD_FIXED          /* `msg`, verbatim */
} RegDiag;

/* K14 / D34 item 1 (design §17.2): a fact about pcrec's ROADMAP, orthogonal to
 * `status` (which is a fact about PCRE2). "requires module 'X'" renders ONLY
 * for ROADMAP_PLANNED; a ROADMAP_NEVER construct is real, refused, and names
 * NO module — these are exactly the constructs docs/pcre2_compliance.md marks
 * OUT-OF-SCOPE, and compliance_section.py asserts prose <=> column in BOTH
 * directions so the survey stays the independent home that caught K14 (the
 * one-source direction is CHECKED, not generated — R14/C2-F8).
 *
 * Zero is deliberately NOT a legal published value: it means "unset" on a
 * row registry_check requires to carry one, and "inherit the row's value" on
 * a VerbName. The legal pairings (registry_check enforces them): RS_BASE
 * rows carry ROADMAP_NONE (the question does not arise for supported
 * syntax); RS_MODULE rows carry PLANNED or NEVER; RS_REJECTED rows carry
 * NEVER (PCRE2 rejects it too, so there is nothing a module could ever
 * implement — the pairing is required, not a choice). */
typedef enum {
    ROADMAP_NONE = 0,
    ROADMAP_PLANNED,
    ROADMAP_NEVER
} Roadmap;

/* MOD-0.1 slice 2 (design §18.3 as ruled, plus SPEC-MOD0's findings A and C):
 * is the construct a legal quantifier target? Populated FROM libpcre2
 * (`a<syntax>*` per row — the sweep is /var-reproducible via
 * tests/spec_mod0/check10, whose oracle recomputes every verdict on every
 * run), never reasoned from documentation.
 *
 *   QF_YES      `a<syntax>*` compiles and the `*` quantifies the construct
 *   QF_NO       err 109 — a real construct that is not a quantifier target
 *               (-family assertions, (?C), bare option-settings... ) OR a
 *               construct PCRE2 rejects outright, whose quantified form
 *               cannot compile either
 *   QF_FORM     the row's FAMILY spans both verdicts and the row cannot say:
 *               option-run rows resolve bare-vs-`:body` in the producer, and
 *               the verb row resolves PER NAME (QV_* below) — `a(*ACCEPT)*`
 *               compiles while `a(*FAIL)*` is 109 with identical table forms
 *               (SPEC-MOD0 finding C)
 *   QF_LEXICAL  quantifying the syntax creates NO quantifier for the
 *               construct at all: `\E`/`(?#)` are transparent (the `*` binds
 *               the PRECEDING atom) and `\Q` literalises it (`a\Q*` compiles
 *               but the star is a literal — SPEC-MOD0 finding A: a bare
 *               "yes" there would be false)
 *   QF_NONE     unset; legal only on RS_BASE rows */
typedef enum {
    QF_NONE = 0,
    QF_YES,
    QF_NO,
    QF_FORM,
    QF_LEXICAL
} QuantFact;

/* The verb row's per-name resolution of QF_FORM. QV_NOT_ASKABLE: the
 * unquantified form itself does not compile (start-of-pattern-only options
 * away from position 0 have no askable cell), which is a THIRD outcome, not
 * a "no" — folding it into no would be wrong (SPEC-MOD0's sweep: 18 yes /
 * 6 no / 26 not-askable over the 50 names). */
typedef enum {
    QV_NOT_ASKABLE = 0,
    QV_YES,
    QV_NO
} QuantVerb;

enum {
    /* RF_CLASS_BASE (1u << 0) RETIRED at MOD-0.3d: "inside a class this
     * byte is BASE syntax" became the row's own BASE class port (ExtPort
     * .base + SCALAR/FN data — one home, and the value is oracle-tied by
     * check_class_ports where the flag was a bare assertion). The bit is
     * left unassigned so an old build's dump and a new one cannot alias. */

    /* A DELIMITER-PAIR construct: the selector byte opens it only when the
     * matching `<sel>]` appears later in the pattern, and the character class's
     * OWN opening bracket can serve as its `[`. Both halves are true of exactly
     * the POSIX collating rows and false of `[:...:]`, which is why one flag
     * carries them: `[.a.]` is an error at offset 0 while `[:alpha:]` is an
     * ordinary five-character class, and `[[.]` compiles because nothing closes
     * the pair. Measured against libpcre2 10.46, not inferred. If a third row
     * ever needs one half without the other, split the flag — the two
     * behaviours coincide here, they are not the same statement. */
    RF_CLASS_DELIM = 1u << 1,

    /* The text between the delimiters is a NAME from a known set, and a name
     * outside it is NOT this construct — PCRE2 says "unknown POSIX class name"
     * rather than routing it anywhere. Exactly one row carries this today
     * (`[[:alpha:]]`), and it is the class-bracket doorway's half of the same
     * over-promise Q1 removed at `(*`: without it pcrec answered "requires
     * module 'classes'" for all 12531 candidate names where libpcre2 has 14,
     * so its answer did not depend on the name at all (R8/C4-7). */
    RF_CLASS_NAMED = 1u << 2,

    /* PCRE2 forbids this construct INSIDE a character class, permanently — no
     * option, no version, no future in which `[\A]` means anything (error 107,
     * or 71 for `\N`). So the in-class doorway must NOT name a module for it:
     * module `assertions` will implement `\A`, and will never implement
     * `\A`-in-a-class, because that is not a construct. Same defect as
     * `(*NOTAVERB)` and `[[:foo:]]`, at the third doorway (R9/SPEC-classes-F1).
     *
     * Distinct from a BASE class port, which says the byte is BASE syntax in a class
     * and the doorway is never entered (`[\b]` is backspace). This says the
     * doorway IS entered and the answer is a refusal that promises nothing. */
    RF_CLASS_INVALID = 1u << 3,

    /* RF_OPTION_RUN (1u << 4) RETIRED at MOD-0.5b: it told ext.c "validate the
     * whole run before trusting this row" for the twelve GROUP_OPT rows. Since
     * MOD-0.2's recogniser+rank arbitration already asks each row a row-local
     * question and falls through to the kind's catch-all when a row declines,
     * the same fact now lives in the row's own `recognise` field —
     * pcrec_registry_option_run_recognise (src/parse/mod_modifiers.c), whose
     * own comment records why it is a MARKER rather than the check itself,
     * and see ext.c for where the real check moved (not far: the same call,
     * gated on identity instead of a bit). The bit is left unassigned so an
     * old build's dump and a new one cannot alias — the RF_CLASS_BASE
     * precedent above. */

    /* The LEXICAL row kind (MOD-0.1 slice 4, design §13.3): the construct is
     * a TOKENIZER MODE, not an atom — `\Q...\E` turns raw bytes into literal
     * character tokens, `\E` alone is the measured no-op, `(?#...)` is a
     * lexer discard. When built, it is built in the lexer; a LEXICAL row
     * has NO class port and NO AST port ever — not "not yet", by design,
     * since the mode transition IS the producer — and it gates like any
     * producer: disabled -> terminal at the token with the row's existing
     * vocabulary.
     *
     * [M4-QUOTING] TWO OF THE THREE ROWS ARE BUILT NOW, and this paragraph's
     * old claim ("this flag changes no behaviour today") is true only of
     * the third. `\Q`/`\E` (module `quoting`) are built in exactly the shape
     * this paragraph describes: `esc_atom`'s own quote-mode dispatch and the
     * `xskip`/`cls_skip`/`cat_ends` boundary-transparency extensions
     * (src/parse/parse.c), gated on `pcrec_feature_enabled(FEAT_QUOTING)`
     * with the module disabled reproducing the pre-landing refusal
     * byte-for-byte. `(?#...)` (module `comments`) remains exactly as
     * described — refusing with its exact string, RF_LEXICAL changing no
     * behaviour for that one row until it lands the same way.
     *
     * MEMBERSHIP IS MEASURED, not asserted: §13.3(d)'s criterion is the same
     * fact the `quant` column carries as QF_LEXICAL, so registry_check
     * requires RF_LEXICAL <=> QF_LEXICAL in both directions and a fourth
     * lexical construct is FOUND (by check10's sweep) rather than assumed
     * away. NOT base grammar: base is never refused and never toggleable;
     * these rows are both (`--without=quoting` must refuse `\Q`). */
    RF_LEXICAL = 1u << 5,

    /* [M6.6.2 wave F / D71 item 3] AN INDEX ROW: it describes a SPELLING for
     * the index layer and is NEVER elected by `pcrec_registry_arbitrate`. The
     * one place that skips it is the arbitration loop itself (registry.c), so
     * a row carrying this bit cannot reach any doorway's dispatch by any path.
     *
     * WHY THE BIT EXISTS AT ALL, because "just do not add such a row" was the
     * alternative and D71 item 3 is the ruling that rejected it: the dispatch
     * and the index answer DIFFERENT QUESTIONS ("which row fires" vs "what
     * does PCRE2's surface look like") and were conflated by row=construct.
     * The twelve `(*` alpha lookaround spellings are the first population
     * where the two genuinely part: they are real, distinct PCRE2 spellings a
     * user writes and the compliance index owes a line for, and NONE of them
     * is selected by a byte — the `(*` doorway dispatches on a NAME through
     * mod_verbs.c's VerbName tables (D25/Q1), so an alpha row has no
     * byte-keyed dispatch identity to keep. R6 stands for every other row.
     *
     * `tail` ON SUCH A ROW IS ITS NAME, and that is the literal reading of
     * the field's own contract ("the bytes that must FOLLOW `sel` for this
     * row to apply") at a doorway whose selector is REG_SEL_ANY: after `(*`,
     * the bytes that must follow for `(*pla:a)`'s row to apply really are
     * `pla`. It is how mod_verbs.c's `pcrec_registry_verb_name_row` finds the
     * row for a scanned name, and it is NOT read by the lookup path (the
     * default recogniser never runs for a row arbitration skips).
     *
     * registry_check asserts BOTH halves: every RF_INDEX row has a `tail` and
     * a `family`, and no (kind, sel, text) arbitration anywhere returns one. */
    RF_INDEX = 1u << 6
};

#define REG_SEL_ANY (-1)      /* catch-all row; last row for its kind */

/* src/parse/ext.c — the four doorways out of the base grammar (SR-2). Each is
 * called only after parse.c's own switch has declined, so a base-tier pattern
 * reaches none of them.
 *
 * THE CLAIM IS RETURNED, NOT RAISED (MOD-0.1, D33 §5 — the load-bearing
 * change). A doorway's terminal answer used to be a `ctx_fail`, which longjmps
 * past the caller; the three `noreturn` attributes that stood here were
 * today's truth and the design's obstacle, because a caller that never sees
 * the claim can never override it — the endpoint rule (D33 §6, K12) needs to
 * see "something claimed" BEFORE the construct's own diagnostic fires. So a
 * doorway now RETURNS an ExtResult and the caller passes it to
 * pcrec_ext_finish, the ONE epilogue that renders a refusal (one epilogue, so
 * D33 §8's "two missing doorway epilogues" cannot be missing). This also
 * retires K11's undefined behaviour: both escape call sites invoked a
 * value-flow through `noreturn` declarations, and a returning doorway
 * corrupted or crashed depending on register allocation; under the value
 * contract the flow is defined C at every site.
 *
 * THE PRODUCING VALUES EXIST SINCE MOD-0.3b AND NOTHING CONSTRUCTS THEM
 * YET: slice 1 lands the vocabulary and the port DATA unwired, so
 * EXT_SCALAR / EXT_MEMBERS / EXT_NODE are unreachable until the classes
 * producers wire in (slices 2-3), and pcrec_ext_finish's wall reports any
 * premature arrival as an internal error. D33 §9.3's obligation — every
 * EXT_* outcome carries a probe that is false the day before — is
 * discharged AT WIRING by the tests/classes/ corpus pins, written first and
 * watched failing (the FIX-3 pattern); until then the exercisable subset is
 * still refusals only, which byte-identity asserts. The call sites in
 * parse.c end in a loud internal-error wall after the epilogue, so a
 * producing port must extend the handling VISIBLY there rather than being
 * silently discarded (the PARSE-1 fallthrough defect, made structurally
 * impossible).
 *
 * "Returns normally" carries NO meaning on its own — the meaning is in the
 * VALUE, which is what keeps the two doorway contracts distinct (the concern
 * parse.c's PARSE-1 note records): the class-bracket doorway declines with
 * EXT_NOT_MINE and the cursor unchanged; the `(?` doorway can never decline
 * (its catch-all is REJECTED), so EXT_NOT_MINE from it is a registry defect
 * the wall reports. */
typedef enum {
    EXT_NOT_MINE = 0,   /* no construct here; cursor unchanged; caller
                           carries on. Only the class-bracket doorway can
                           produce it today. */
    EXT_REFUSAL,        /* a claim that terminates the compile: `msg`/`at`
                           carry the diagnostic, formatted AT CLAIM TIME so it
                           outlives the handler (D33 §5's representability
                           requirement), fired by pcrec_ext_finish. */
    /* The PRODUCING claims (D33 §5's full vocabulary, landed MOD-0.3b,
     * unconstructable until the classes producers wire in): */
    EXT_SCALAR,         /* one code point in `scalar` — the ONLY shape legal
                           as a range endpoint (D33 §6). `\b` in a class. */
    EXT_MEMBERS,        /* a byte-set the caller ORs into the class under
                           construction: `node` is an A_CLASS whose cls[]
                           holds the members. `[\d]`, `[[:alpha:]]`. */
    EXT_NODE            /* a finished subtree the caller splices in at atom
                           position: `\d` outside a class. */
} ExtWhat;

/* THE ASK CONTRACT (MOD-0.1, design §15/§18.2 as Frank ruled it): a doorway
 * is asked at one of three `want` levels, and there is NO `may` capability
 * axis — the fifth-session ruling collapsed it, with the revisit trigger
 * recorded: a terminal answer REQUIRED to depend on a full sub-parse while
 * its module is disabled reintroduces the axis.
 *
 *     WANT_CLAIM     is this yours, and what shape (consumer: arbitration)
 *     WANT_VERDICT   the right terminal answer, whatever it costs
 *     WANT_RESULT    the produced set/node
 *
 * THE CURSOR RULE, the load-bearing line: cx->pos moves ONLY under
 * WANT_RESULT. Below RESULT a doorway may inspect the pattern without limit
 * — the verb-name scan, the option run and the delimiter-pair scan are all
 * bounded row-local reads VERDICT is entitled to — but must leave cx->pos
 * byte-identical, and VERDICT never recurses into the pattern grammar.
 * tests/spec_mod0's check06 measures this over every registry row through
 * the CLI probe channel (`--probe-ask`), which reports the real cursor
 * before and after a single doorway call.
 *
 * THE GATE (§5.4/§15) demotes `want` by exactly one step — RESULT ->
 * VERDICT — for a row whose module is not enabled, and FLOORS at VERDICT: a
 * disabled module still owes its diagnostic, so nothing ever demotes to
 * CLAIM (silence where a message is owed). The enabled set is EMPTY today,
 * so every ask from parse.c (always WANT_RESULT — the real parse wants the
 * construct) is answered at VERDICT, which is why ExtResult's vocabulary is
 * all refusals. ext.c's demotion is unconditional for exactly that reason;
 * the enabled-set slice replaces it with the membership test (check07's
 * subject), and `pcrec_ext_class_pair_opens` below is the one ask that
 * bypasses `want` — it IS the CLAIM-shaped question as a predicate. */
typedef enum { WANT_CLAIM = 0, WANT_VERDICT, WANT_RESULT } ExtWant;

typedef struct RegRow RegRow;

typedef struct {
    ExtWhat what;
    size_t  at;         /* EXT_REFUSAL: offset the diagnostic points at */
    char    msg[256];   /* EXT_REFUSAL: the exact text; 256 matches
                           pcrec_error.msg, so deferring the format cannot
                           truncate differently than ctx_fail did */

    /* §16.3(e)'s verdict-shape payload, exercisable subset (the K12 endpoint
     * slice). TRUE only on a refusal for a construct pcrec can CERTIFY is
     * SET-shaped and PCRE2-accepted for EVERY form that reaches the row: the
     * ten char-type escapes (the construct IS its selector byte — syntax
     * "\X"; the measured class_expect covers all forms) and the bracket
     * doorway's KNOWN POSIX names (the 14-name table validated the body).
     * The range logic overrides such a refusal with PCRE2's verdict —
     * "invalid range in character class", err-150's analogue — at an
     * endpoint (§16's step 4). Body-dependent rows (\p, \N{U+}, ...) are
     * NEVER marked: pcrec cannot certify 150 for an arbitrary body
     * ([0-\p{Foo}] is PCRE2 147, not 150), so their module promise stands —
     * the deliberate boundary pinned in tests/reject/ and recorded in the
     * 2026-08-11 journal entry. */
    bool    ep_set_certain;
    /* class-bracket claims only: offset just past the construct's closing
     * "X]" — where a low endpoint's range dash would sit. */
    size_t  end;
    /* The level the ask was actually ANSWERED at, after the gate — the §5.4
     * demotion made observable (the probe channel prints it; nothing on the
     * compile path reads it, which byte-identity asserts). WANT_RESULT here
     * means THE GATE WAS OPEN — the row's module is in the enabled set
     * (slice 9); on a refusal it distinguishes "gate open, port missing"
     * (D33's NULL-port refusal) from "gate closed" (verdict-level demotion).
     * With the default empty enabled set it is never `result`, which cli
     * case10 pins. A decline is a claim-level answer (zero-init). */
    ExtWant answered_at;

    /* Production payloads (MOD-0.3b; read only for the matching `what`,
     * zero/NULL otherwise — designated initializers leave them so): */
    int     scalar;     /* EXT_SCALAR: the code point */
    Ast    *node;       /* EXT_MEMBERS: A_CLASS whose cls[] the caller ORs in;
                           EXT_NODE: the subtree the caller splices */

    /* THE ELECTED ROW (MOD-0.7 slice 2) — which row the doorway DISPATCHED
     * on. Nothing on the compile path reads it; `--explain` does, and cli
     * case11 asserts it per row.
     *
     * THE CONTRACT IS A BICONDITIONAL: **NULL if and only if the doorway
     * answered WITHOUT a row.** R20/MOD07-4 found the reverse direction false
     * in two of the three cases this comment already named, because both
     * failing paths STAMP AT LOOKUP and then answer somewhere the lookup's
     * result plays no part:
     *
     *   unknown escape              the lookup found nothing. NULL, always.
     *   class-bracket, no row       the lookup found nothing. NULL, always.
     *   class-bracket, pair never   a row WAS found and the delimiter scan
     *     closes                    then rejected it. Cleared at the DECLINE.
     *   `(?` at end of pattern      c2 == -1 aliases REG_SEL_ANY, so the
     *                               catch-all is found by an accident of the
     *                               sentinel and the branch walks past it.
     *                               Cleared in that branch.
     *
     * A path that answers without consulting the row must clear the stamp
     * where it answers, not rely on the lookup having failed. The two that
     * did not made `--explain` assert elections that never happened.
     *
     * IT IS NOT "THE ROW THAT WROTE THE MESSAGE", and the distinction is
     * measured rather than pedantic: for `(?iZ)` the elected row is the `i`
     * GROUP_OPT row while the text is the catch-all row's, because the
     * option-run grammar rejected the run (ext.c's option-run branch). Both
     * facts are true and `--explain` prints them as two fields.
     *
     * WHY IT EXISTS AT ALL, with the number: 13 registry rows share their
     * rendered atom diagnostic with a sibling in the same bucket (10 of the
     * `(?-N)` family, 3 of the `(?<` lookarounds), so a check comparing TEXT
     * — which is what registry_check's check_table_to_parser does — cannot
     * tell which of them answered. Identity can. See docs/design/design_notes_mod07.md
     * §5.3.
     *
     * STAMPED IN EXACTLY ONE PLACE PER DOORWAY: each public `pcrec_ext_*`
     * is a thin wrapper that calls the answering body with an out-parameter
     * and writes this field on the single return. A return added inside a
     * doorway later cannot forget it. */
    const RegRow *row;
} ExtResult;

/* A row's PRODUCING PORTS (design Part II §4/§14; D33 §5). One per position
 * — `aport` answers atom position, `cport` answers class position — because
 * the two positions of one construct genuinely differ in PCRE2 (\12 at 12
 * groups: backref at atom, octal in class — §14.1's measured table). The
 * KIND is the single home of "can this row produce here":
 *
 *   PORT_NONE    atom: the row refuses with its own diagnostic, exactly as
 *                every row does today.
 *                class: PERMANENTLY INVALID at class position — NULL's one
 *                meaning (§14.3, R14-verified mode-invariant). When the
 *                RF_CLASS_* flags retire (slice 3) this replaces them.
 *   PORT_SCALAR  one code point, as DATA: `\b` -> 0x08 (base scalar), and
 *                the literal fallbacks `\g \k \8 \9` -> their own letters
 *                (§14.3 — the K13 semantics, produced instead of asserted).
 *   PORT_SET     a 256-bit membership bitmap, as DATA (32 bytes): the ten
 *                char-type escapes and the POSIX names. Bitmaps are
 *                GENERATED from libpcre2 censuses, never hand-typed, and
 *                PC-4 re-measures them against the live oracle (the PC-3
 *                pattern; a libpcre2 version bump is a re-measurement
 *                event, D26 addendum).
 *   PORT_FN      a bounded row-local scan for shapes data cannot carry (the
 *                octal re-read `[\12]`, the POSIX name lookup): §18.2's
 *                VERDICT legality — may read its own body, never recurses
 *                into the pattern grammar. Signature is provisional until
 *                its first caller wires in (slice 2/3); the FIELD exists now
 *                so every macro initialises the whole port once.
 *
 * Ports are DATA about production; they carry no diagnostic and no module
 * fact (those stay on the row — R11/M5's rule that a handler must not be a
 * second home for tier-2 facts). */
typedef enum { PORT_NONE = 0, PORT_SCALAR, PORT_SET, PORT_FN } PortKind;

/* (`typedef struct RegRow RegRow;` moved ABOVE ExtResult at MOD-0.7 slice 2 —
 * ExtResult.row needs the name, and ExtResult is defined first.) */
typedef ExtResult (*ExtPortFn)(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from);

typedef struct {
    PortKind             kind;
    /* MOD-0.3d: TRUE for a port whose semantics are PCRE2 BASE FACTS the
     * gate must never touch — `\b`-in-class is backspace and `[\12]` is
     * octal WHATEVER is enabled (§14.3: "\b's class port is base (never
     * gated) and its AST port is 'assertions'" — the per-port feature
     * split that makes the C5 miscompile unrepresentable). A module's own
     * producing ports carry false and answer only through an open gate. */
    bool                 base;
    int                  scalar;  /* PORT_SCALAR: the code point.
                                     PORT_SET: the NEGATE flag — nonzero
                                     means the produced set is the exact
                                     256-bit complement of `set` (\D \S \W
                                     \H \V, and \N's not-newline). Only
                                     POSITIVE tables are stored; the
                                     complement law is asserted by the
                                     emitting probe for every pair. */
    const unsigned char *set;     /* PORT_SET: 32 bytes, bit b of set[b>>3] */
    ExtPortFn            fn;      /* PORT_FN */
} ExtPort;

#define NO_PORT { PORT_NONE, false, 0, NULL, NULL }

/* module `classes` (MOD-0.3c) — src/parse/mod_classes.c. The tables are
 * GENERATED from libpcre2 censuses by tests/probes/probe_cls_bits.c
 * (--emit writes src/parse/cls_bits.inc; the provenance header names the
 * version); PC-4 re-measures produced sets against the live oracle. */
extern const unsigned char pcrec_cls_digit_esc[32], pcrec_cls_space_esc[32],
    pcrec_cls_word_esc[32], pcrec_cls_hspace[32], pcrec_cls_vspace[32],
    pcrec_cls_newline[32],
    pcrec_cls_px_alnum[32], pcrec_cls_px_alpha[32], pcrec_cls_px_ascii[32],
    pcrec_cls_px_blank[32], pcrec_cls_px_cntrl[32], pcrec_cls_px_digit[32],
    pcrec_cls_px_graph[32], pcrec_cls_px_lower[32], pcrec_cls_px_print[32],
    pcrec_cls_px_punct[32], pcrec_cls_px_space[32], pcrec_cls_px_upper[32],
    pcrec_cls_px_word[32],  pcrec_cls_px_xdigit[32];
/* Which class-axis context does byte class `c` carry? Declared here rather
 * than in src/ir/dfa.c because BOTH emitters ask it — the accept table, the
 * seed table and ENG_ATTEMPT's per-state arms all have to agree with the
 * subset construction about which view a class selects, and a second copy of
 * this two-line rule is exactly the drift this project keeps recording.
 *
 * Well-defined ONLY because `eqclasses` refined the partition by whichever of
 * the two sets the machine needs: every byte of a class then has the same
 * answer, so reading it off the class's representative byte is exact rather
 * than a sample. A machine that skipped a refinement never asks the
 * corresponding question — with no N_WORDB nothing distinguishes UPC_WORD
 * from UPC_PLAIN, and this answer is then consumed only as an index into
 * views that are all the same list. */
static inline int upc_of_class(const Dfa *d, int c)
{
    if (cls_has(pcrec_cls_word_esc, d->rep[c])) return UPC_WORD;
    if (cls_has(pcrec_cls_newline,  d->rep[c])) return UPC_NL;
    return UPC_PLAIN;
}

/* The GENERATED name->bits map for the POSIX named classes: emitted by
 * probe_cls_bits.c --emit as part of cls_bits.inc, so the PAIRING of a
 * name to its table is the same artifact as the measurement that produced
 * the table — never a hand-written line (R16's lower/upper swap lived in
 * exactly such a line; this deletes the species). posix_names[] in
 * registry.c stays the separate home of EXISTENCE and ATTRIBUTION (does
 * PCRE2 have the name; whose module is it), which PC-3 measures — two
 * different questions, two homes, one check tying their name sets. */
typedef struct {
    const char          *name;
    const unsigned char *bits;
} PcrecClsNamed;
extern const PcrecClsNamed pcrec_cls_posix_map[];
extern const size_t        pcrec_cls_posix_map_n;

/* The POSIX named-class producer (the `:` row's PORT_FN). */
ExtResult pcrec_clsport_posix(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from);
/* module `assertions` ([M6.2] wave A) — src/parse/mod_assertions.c. ONE atom
 * port for `\A`/`\Z`/`\z`, dispatching on the elected row's own `sel`.
 * `\b` `\B` `\G` `\K` and `(?m)` are recognised by the same module and have
 * NO producer yet: with the module enabled they refuse by their own name
 * through ext.c's UNBUILT epilogue, never as "requires module 'assertions'"
 * (which would be a lie once it is enabled) and never as unknown. */
ExtResult pcrec_asrtport_atom(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from);
/* The octal class producer (MOD-0.3d) — the `\0`..`\7` rows' BASE PORT_FN,
 * in parse.c: base grammar's own rule migrated to the seam (FIX-3's measured
 * semantics — selector digit + up to two more octal digits, <= \377, PCRE2
 * err 151 above with the ran-out offset). */
ExtResult pcrec_clsport_octal(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from);
/* src/parse/parse.c — build an A_CLASS from a 32-byte membership bitmap,
 * applying the caseless fold BEFORE the optional negation (the OS-1/D23
 * order rule: both orders produce case-closed sets and only behaviour can
 * tell them apart — see cls_casefold's comment). The ONE constructor every
 * set-producing port uses, so the fold rule cannot be forgotten per site. */
Ast *pcrec_ast_node(Ctx *cx, AKind k);   /* bare-kind ctor for module TUs */
/* [M6.4.2 / SR-8, D67] THE STAMP, and the ONE call that applies it.
 *
 * A module's producer calls this on every node it creates, with the row it was
 * dispatched on and the pattern offset it blames. Two things happen in one
 * statement, which is why it is a function and not an assignment: `Ast.reg` is
 * set (so `pcrec_ast_engines` can consult the row's `engines` mask, and so
 * `select_engine.c` can name the construct), and — for a row that EXCLUDES the
 * DFA — `Ctx.first_vmonly_pos` records the offset, first-wins. Doing both here
 * is what stops the offset and the row from being recorded at different
 * moments and drifting.
 *
 * A PRODUCER THAT FORGETS TO CALL IT yields nodes claiming BOTH engines, which
 * is the UNSOUND direction on purpose (D67 contract note 2). What catches that
 * is `tests/registry/registry_check.c`'s generic tripwire — every VM_ONLY row
 * with a producer must refuse `--engine=dfa` BY NAME — not a lucky default. */
void pcrec_ast_stamp(Ctx *cx, Ast *a, const RegRow *rw, size_t at);
/* [M6.2 wave D] The BARE ANCHOR rule, one home, four readers (parse.c's
 * quantifier rejection and group wrap, mod_modifiers.c's `(?i:...)` port,
 * mod_named_groups.c's declaring port). See src/parse/parse.c for the
 * measured rule and for the drift that made it one function. */
bool pcrec_is_bare_anchor(const Ast *a);
Ast *pcrec_wrap_bare_anchor(Ctx *cx, Ast *body);
Ast *pcrec_ast_class_from_bits(Ctx *cx, const unsigned char bits[32],
                               bool negate);
/* [M6.5.2] One byte as an atom, with the caseless fold applied — the same
 * one-constructor rule as the line above, for module TUs that produce a
 * CHARACTER rather than a set (module `backrefs`' octal readings). */
Ast *pcrec_ast_char(Ctx *cx, unsigned c);

/* [M6.5.2] THE ASCII CASE-FOLD PARTITION AS ONE OBJECT — src/core/fold.c,
 * where the full account lives. `pcrec_ascii_fold[c]` is c's case PARTNER, or
 * c itself when it has none. `cls_casefold` derives its class widening from
 * it, and `tests/backrefs/fold_agreement_check.c` asserts the SHIPPED
 * `$_bref_match_caseless` residual entry induces the identical partition over
 * all 65,536 byte pairs. Two spellings of one fact, with a mechanism between
 * them instead of a comment (R32 E8; sabotage row S116). */
extern const unsigned char pcrec_ascii_fold[256];

/* [DD-11.1] THE REPLACEMENT/DEFINITION TABLE (D85, docs/design/
 * definitions_table.md, r43-revised). For a row whose construct stands for
 * another construct expressible in CORE syntax (D85's own words) under some
 * option scope, `RegRow.definitions` (below) points at a small `static
 * const` array of `RegDef` rows: an ORDERED list, first-applicable-wins,
 * terminated by `DEFK_END` rather than carrying a parallel count (the
 * `family` field's own precedent: one new fact on the row, not a second
 * home for its size). NULL for the ~100 rows with nothing to say — the
 * D82-bound-3 shape `family` already has.
 *
 * THE PREDICATE IS A TAG, NOT A STORED CALLABLE (manager ruling, r43,
 * folding K1/K2/K3/K9 of docs/dev/reviews/2026-08-29-r43-dd11-definitions.md).
 * A stored `bool (*)(const Ctx *)` was measured NOT to close the gap it was
 * meant to (K1: `Ctx.mods` already compiles as an opaque pointer everywhere,
 * so there was no type hazard to avoid) and to WEAKEN containment instead
 * (K2: a stored callable is reachable from any TU holding a `Ctx *`, which
 * is every TU downstream of `src/parse` — the deref lives in the CALLEE, not
 * in the type). `DefTag` is a CLOSED ENUM evaluated by exactly ONE
 * exhaustive no-default `switch` in `src/parse/definitions.c`
 * (`pcrec_def_tag_applies`, `mrl.c`'s discipline: a new tag with no arm is a
 * compile error) — containment by CONSTRUCTION, checked by a grep (K2's
 * fix) rather than asserted by a type that did not enforce it. */
typedef enum {
    DEF_ALWAYS,          /* the row's only entry, or its unconditional tail */
    DEF_MULTILINE,       /* cx->mods->multiline true at the construct */
    DEF_NOCAP,           /* cx->mods->nocap true at the construct */
    DEF_UCP,             /* Unicode class semantics active — NO PRODUCER YET
                          * (module unicode-props has no \w-shaped producer);
                          * the evaluator answers false unconditionally until
                          * one exists, which is sound (the row falls through
                          * to its DEF_ALWAYS entry, today's byte behaviour) */
    DEF_ENCODING_UTF8,   /* --encoding=utf8 — NO PRODUCER YET ([DD-12]/[M5]);
                          * same false-until-built shape as DEF_UCP */
    DEF_NEWLINE_CONV,    /* a non-LF newline convention is active — NO
                          * PRODUCER YET (D64, parked); same shape */
    DEF_LIB_NAME_BOUND   /* [LIB]/[DD-13b]: the name is bound in the
                          * compile's definitions/library input — NO
                          * PRODUCER YET; same shape */
} DefTag;

/* DEFK_END terminates a `definitions` array (no parallel count, see above).
 * DEFK_STR is a bodyless construct's core-syntax TEXT, parsed and spliced at
 * the occurrence — the SAME convention `RegRow.syntax` already uses ("a
 * pattern that PROBES this construct" is itself a valid pcrec pattern), so
 * `--list-definitions` prints it verbatim. DEFK_BUILDER is an OPERAND-taking
 * construct (the possessive suffix, `(?n)`) whose definition needs the
 * caller's own AST subtree spliced in, which no string convention here
 * expresses without inventing a placeholder syntax nothing else uses.
 *
 * DEF_IDENTITY (manager ruling, 2026-08-29, folding the identity question):
 * the row's own PRIMITIVE form — "already core", no substitution — is an
 * EXPLICIT entry, never the ABSENCE of one. D85's own text calls the
 * identity "the last row [that] always applies", which makes it a ROW by
 * the note's own reading; the alternative (`pcrec_def_resolve` returning
 * NULL as the identity signal) is ABSENCE-AS-DISCRIMINATOR, the exact
 * hazard [DD-13]'s stamp design already ruled out (a missing entry reads
 * identically to a forgotten one). No `str`, no `builder` — there is
 * nothing to splice, the occurrence's own shipped lowering IS the
 * definition. `--list-definitions` prints `applies=identity` FROM THIS
 * KIND, never by inference. Carries `tag == DEF_ALWAYS` (it is always the
 * unconditional TAIL of its list) so `pcrec_def_resolve`'s ordinary
 * first-applicable-wins walk needs no special case for it.
 *
 * DEFK_TEXTFN (manager ruling, 2026-08-29, folding the operand-
 * parameterized question): the GENERAL shape for "a binding parameterized
 * by text at the occurrence" — `\cX`, bare `\x`/`\x{}`, `\o{}`, octal/`\0`,
 * `\N{U+}` today; [DD-13b]'s [LIB] name-bound rows reuse it later
 * (parameterized by the name), which is why it is a third KIND and not a
 * one-off. `str` here is not a splice-ready core-syntax string (there is
 * no such fixed string when the operand varies) — it is a human-readable
 * TEMPLATE for `--list-definitions`'s `definition` column (e.g. `\cX ≡
 * \x{X ^ 0x40}`). `textfn` is the actual definition: given the operand
 * text at the occurrence, it returns the core AST — and it MUST call the
 * EXISTING decoder (`esc_char_value` and friends, src/parse/parse.c/
 * pcrec_esc_char_value_export below) rather than re-implement the
 * decoding, so there is exactly one decode site regardless of how many
 * `DefKind`s can reach it. [DD-11.3]'s self-oracle samples `textfn` over a
 * representative operand set per row (all 256 for `\x`, letters/
 * punctuation for `\c`, boundary code points for `\N{U+}`, the octal edge
 * cases) rather than a single string, since no ONE operand could stand for
 * the row the way a fixed `DEFK_STR` value does. */
typedef enum { DEFK_END, DEFK_STR, DEFK_BUILDER, DEF_IDENTITY, DEFK_TEXTFN, DEFK_ROW } DefKind;

/* A DEFK_BUILDER's `builder` takes the body the construct would otherwise
 * wrap or number, and returns the CORE-syntax equivalent — e.g. the
 * possessive suffix's `body` is the already-built `A_REP` node and the
 * builder wraps it in `A_ATOMIC`; `(?n)`'s `body` is the group's inner AST
 * and the builder is the IDENTITY (no `A_CAP` wrapper — `(?:X)` never gets
 * one either — NOTE this is `pcrec_def_build_identity`, an ordinary
 * DEFK_BUILDER function operating on a BODY, unrelated to the `DEF_IDENTITY`
 * KIND above, which marks a whole RegDef entry with no body at all; the
 * `(?n)`-scoped capturing-group row carries BOTH, in the same list, for
 * its two different option states). [DD-11.5] is what would call these for
 * REAL lowering; today they exist so the structural check
 * (`pcrec_ast_all_core`) can invoke one in isolation and confirm its
 * OUTPUT is core-set vocabulary.
 *
 * A DEFK_BUILDER's `str` is a TEMPLATE (manager ruling, r43-second-round,
 * 2026-08-29), exactly as DEFK_TEXTFN's already is below — one placeholder
 * convention, `X` for the operand (the quantifier bounds spelled as in the
 * construct: `X{n,m}+ ≡ (?>X{n,m})`) — so `--list-definitions` stops
 * printing the fixed literal `<builder>` for these rows, which said nothing
 * about what the builder DOES. [DD-11.3]'s self-oracle INSTANTIATES the
 * template over a small body set (`a`, `(a)`, `[ab]`, `a|b`, `\d+`) to
 * produce a real Pattern B and compares BEHAVIOUR against the builder's own
 * output (and against libpcre2) — a builder that drifts from its stated
 * template shows up as a disagreeing cell, never as an AST-equality
 * assertion (D77: no measured need for AST-structural-equality
 * infrastructure this tree does not otherwise have). The template is the
 * builder's STATED CONTRACT; the builder function stays the production
 * mechanism — one fact, two readers (dump, self-oracle), same as `str`'s
 * other two duties below. */
typedef Ast *(*DefBuilderFn)(Ctx *cx, Ast *body);

/* A DEFK_TEXTFN's `textfn` takes the operand TEXT at the occurrence
 * (`operand`/`len`, NOT NUL-terminated — pattern text never is) and the
 * live `Ctx` (needed to build an AST node, `pcrec_ast_node`/`pcrec_ast_char`
 * and friends all take one), and returns the core AST. It is a pure
 * function of (operand, cx) — no scanning, no cursor movement, since the
 * occurrence has already been scanned by the time a definition is asked
 * for (structural-check/self-oracle callers hand it a slice they chose,
 * never a live parse position). */
typedef Ast *(*DefTextFn)(const char *operand, size_t len, Ctx *cx);

/* DEFK_ROW (manager ruling, r43-second-round, 2026-08-29): an entry that
 * CHAINS to ANOTHER ROW's own resolution rather than restating a fact that
 * row already carries — "an alias row defines to the row it aliases, never
 * to the alias's own expansion; one fact, one row." `str` holds the target
 * row's `syntax` (never the target's OWN definition text) — `family`'s own
 * reference-by-syntax-string idiom (`mod_lookaround.c`'s `la_kind`),
 * generalised past ONE `RegKind` via `pcrec_registry_row_by_syntax`
 * (registry.c), since a chain may cross kinds (`$`, RK_BARE, chains to
 * `\Z`, RK_ESC — `family` itself never needs to, so it stayed
 * single-kind). `pcrec_def_resolve` (definitions.c) does not return a
 * DEFK_ROW entry to its caller: it WALKS THROUGH it, recursively resolving
 * the target row under the SAME `Ctx` — this is D85's "expandable" table
 * property made concrete, and it is why `$`'s non-multiline fact
 * (`(?=\n?\z)`) lives in exactly one row (`\Z`'s) even though two
 * constructs alias it. A row named by a DEFK_ROW entry that does not exist,
 * or whose own resolution loops back here, is a registry DEFECT — resolved
 * by `pcrec_registry_row_by_syntax` returning NULL / by a depth bound, both
 * asserted loudly by the resolver, never silently — exactly `la_kind`'s
 * own dangling-reference contract, one level over. */

typedef struct RegDef {
    DefKind      kind;
    DefTag       tag;      /* meaningless when kind == DEFK_END */
    const char  *str;      /* DEFK_STR: the definition itself.
                            * DEFK_TEXTFN, DEFK_BUILDER: a human-readable
                            * TEMPLATE for the dump, never spliced or
                            * parsed (DEFK_BUILDER's own comment above has
                            * the placeholder convention).
                            * DEFK_ROW: the TARGET row's `syntax` — a
                            * reference, never the target's own definition
                            * text (its comment above has the chaining
                            * rule). NULL otherwise (DEF_IDENTITY,
                            * DEFK_END). */
    DefBuilderFn builder;  /* DEFK_BUILDER only */
    DefTextFn    textfn;   /* DEFK_TEXTFN only */
    /* DEFK_STR only, optional (NULL everywhere else): for a row whose
     * ENTRIES are keyed by an OPERAND (a name) rather than by an
     * option-scope tag -- the 14-name POSIX class family is today's only
     * user (r43-third-round follow-up, team-lead ruling 2026-08-29) -- the
     * entry's own name text ("alpha", "digit", ...). `pcrec_def_resolve`'s
     * ordinary first-applicable-wins walk cannot select a NAMED entry
     * (there is no DefTag for "alpha" vs "digit"), so this field exists
     * for the TWO callers that need to pick a SPECIFIC entry rather than
     * the walk's first answer: `--list-definitions` prints
     * `[[:alpha:]] ≡ [A-Za-z]` per entry instead of the row's fixed
     * `syntax` example, and [DD-11.3]'s self-oracle instantiates the row's
     * real construct with the name (`[[:%s:]]`) to get 14 real cells
     * instead of a first-wins skip. Appended at the END of the struct so
     * every existing positional initializer in registry.c still COMPILES
     * with this field defaulting to NULL (C's aggregate-init zero-fill
     * rule) — but `-Wextra`'s `-Wmissing-field-initializers` still flags
     * every 5-field literal, so `make strict` DID need every one updated
     * to a trailing `, NULL` (a mechanical pass, 46 lines, no field values
     * changed) — a lesson for the next field added here: "compiles" and
     * "compiles clean under strict" are different claims. */
    const char  *operand;
} RegDef;

/* src/parse/definitions.c */
bool pcrec_def_tag_applies(DefTag tag, const Ctx *cx);
const RegDef *pcrec_def_resolve(const Ctx *cx, const RegRow *rw);
const char *pcrec_def_tag_name(DefTag tag);
bool pcrec_ast_is_core(AKind k);
bool pcrec_ast_all_core(const Ast *a);
Ast *pcrec_def_build_atomic(Ctx *cx, Ast *body);     /* the possessive family */
Ast *pcrec_def_build_identity(Ctx *cx, Ast *body);   /* (?n) */
/* DEFK_TEXTFN implementations — each calls the existing base-tier decoder
 * rather than re-decoding; src/parse/definitions.c's own header names the
 * one call site each reaches. */
Ast *pcrec_def_text_cx(const char *operand, size_t len, Ctx *cx);      /* \cX */
Ast *pcrec_def_text_hex(const char *operand, size_t len, Ctx *cx);     /* \xHH, \x{HHHH} */
Ast *pcrec_def_text_octal(const char *operand, size_t len, Ctx *cx);   /* \o{OOO}, \NNN, \0 */
Ast *pcrec_def_text_unicode(const char *operand, size_t len, Ctx *cx); /* \N{U+HHHH} */

/* Field groups are ordered identity / ownership / selection / outcome / doc.
 * `feature` and `module` are ADJACENT on purpose: they are two halves of one
 * fact, and registry.c's M_* macros emit them as a pair so a row cannot carry
 * a feature bit that disagrees with the module name it prints. */

struct RegRow {
    RegKind     kind;
    int         sel;       /* the deciding byte, or REG_SEL_ANY */
    /* The bytes that must FOLLOW `sel` for this row to apply, or NULL for "any"
     * (SR-9, docs/design/design_registry_selectors.md §7). Since MOD-0.2 the lookup
     * engine never interprets this field: it is the PARAMETER of
     * pcrec_recognise_tail_default — a row's recogniser answers when its tail
     * is a prefix of the text, and `rank` (below) elects among answering rows,
     * which is what makes a tailed row beat the same byte's tail-less fallback
     * and `\N{U+` beat `\N{`. SR-9's longest-tail-wins produced identical
     * answers over the whole probe space (261,193-probe scaffold + a
     * 5,247-comparison behavioural differential) and was retired.
     *
     * WHY A SECOND KEY RATHER THAN A STRING SELECTOR (§2, which R6 rejected with
     * measurements): one byte still decides the DOORWAY, and only a handful of
     * constructs need more. Making every selector a string would turn the
     * base-tier class lookup from 3 rows into ~31 and silently narrow the
     * 255-byte sweep; this keeps both exactly as they were.
     *
     * IT IS A LITERAL PREFIX, NOT A PATTERN. `(?-` followed by a digit is a
     * relative subroutine call and followed by a letter is an option setting,
     * so that construct needs ten rows ("0".."9") rather than one "\d" — which
     * is deliberate: a tail nobody has to interpret cannot be interpreted
     * wrongly, and the ten-row digit family is a shape this table already has
     * twice (`(?0)`..`(?9)` and `\0`..`\9`). */
    const char *tail;
    const char *syntax;    /* how it is written — also a valid probe pattern,
                              which is what lets the conformance test cover new
                              rows without being edited */

    unsigned    feature;   /* FEAT_* mask; 0 for RS_BASE/RS_REJECTED */
    const char *module;    /* module name AS IT APPEARS IN DIAGNOSTICS, or NULL */

    unsigned    flavours;  /* FLAV_* mask */
    unsigned    engines;   /* ENGM_* mask — design intent, unconsumed today.
                              [M4.7a] SR-8: consultation deliberately NOT
                              built ahead of a producer (D18/OS-0/D53); the
                              tripwire in tests/registry/registry_check.c
                              (check_engine_capability_tripwire) asserts
                              every VM_ONLY-masked RS_MODULE row has no
                              wired producer, so wiring the first one fails
                              loudly and names SR-8 as the thing to build
                              first. */

    RegStatus   status;
    RegDiag     diag;
    const char *msg;       /* RD_FIXED only, else NULL */
    /* The diagnostic when the CLASS'S OWN bracket is the opener (`[:alpha:]`
     * rather than `[[:alpha:]]`). NULL — every row but one — means the row
     * behaves identically in both positions.
     *
     * It exists because ONE row's outcome genuinely changes KIND with position,
     * measured against libpcre2 10.46: `[[:alpha:]]` is a POSIX class PCRE2
     * SUPPORTS, so pcrec owes "requires module 'classes'"; `[:alpha:]` is an
     * error PCRE2 will never accept, so promising a module there is a lie no
     * module can make true. The two collating rows do NOT need it — `[.a.]`
     * and `[[.a.]]` are both error 113, same text, both positions.
     *
     * This is a TIER 2 distinction under D26 (is a module promised?), not a
     * tier 3 one (what does the sentence say), which is why one extra field
     * buys it and a fifth doorway kind is not needed. */
    const char *open_msg;
    unsigned    flags;     /* RF_* */

    const char *note;      /* one-line PCRE2 semantics (SR-3/SR-4 render this) */

    /* LAST on purpose: every macro-built row initialises these explicitly,
     * and a longhand row that forgets one gets the zero value, which
     * registry_check flags on any non-base row rather than silently reading
     * as a claim. */
    Roadmap     roadmap;
    QuantFact   quant;

    /* MOD-0.1 slice 3 (design §14.4 as R14-corrected): the row's
     * CLASS-POSITION EXPECTATION — what `[<syntax>]` does under libpcre2,
     * two-valued and libpcre2-observable:
     *
     *   "err N"      the class does not compile; N is PCRE2's error number
     *   "char 0xNN"  it compiles and denotes exactly this one byte
     *   "set N"      it compiles and denotes N of the 256 byte values
     *
     * Populated FROM libpcre2 (tests/probes/probe_class_expect.c, 8-bit,
     * options = 0), cross-validated against the independent SPEC-MOD0
     * measurement, and re-verified against a live oracle run by
     * tests/spec_mod0/check04 — never reasoned from documentation.
     *
     * NULL on the 56 group/verb rows, and ONLY there: `(` inside a class is
     * an ordinary member, so those constructs cannot reach a class position
     * and a value would be an invented fact (§4.4's objection). The 41 esc
     * and 3 class-bracket rows must each carry one; registry_check enforces
     * both directions and the vocabulary. */
    const char *class_expect;

    /* MOD-0.2 (design §2.2 as adopted at D32 §§2-4, kept by Part II §14.4):
     * row SELECTION is recogniser + rank, not tail interpretation. Both
     * fields sit after the explicitly-initialised block and are ZERO-
     * DEFAULTED on purpose: 78 rows are alone in their bucket, and a
     * meaningful rank there would be an invented fact (D32 §3 — rank only
     * means anything between clashing recognisers).
     *
     * `rank` is a LOCAL TIEBREAK inside one (kind, sel) bucket, in three
     * tiers:
     *
     *     0   the bucket's fallback, and every row that never clashes
     *    25   a tailed row — beats the fallback; the single-byte tails
     *         within one bucket are mutually exclusive, so equal rank
     *         among them can never produce two ANSWERS
     *    70   the longer half of the table's one prefix-related tail pair
     *         (`\N{U+` over `\N{`) — the only place two tailed
     *         recognisers both answer
     *
     * The VALUES are arbitrary; only the ordering within a clashing set is
     * a fact. (R11 recovered D30's 0/25/40/70 draft mapping; the 40 tier is
     * deliberately not reproduced — `\N{` clashes only with the fallback
     * below it and `\N{U+` above it, so the tailed tier serves it.) Do not
     * add a global rank sweep as a permanent check: R11/M3 measured one
     * redundant with the per-row syntax check in all 5,632 probes. The
     * defect rank CAN carry — two answering rows at the winning rank — is
     * detected at dispatch (pcrec_registry_arbitrate) and floored as
     * exercised by registry_check's arbitration-liveness counter.
     *
     * `recognise` answers "is the text at the tail position my construct's
     * proper form?" — POSITIVE and LOCAL (D32 §2): it recognises its own
     * form and knows nothing about sibling rows (the bare `\N` row
     * answering "always" is CORRECT; elimination is rank's job). NULL
     * means pcrec_recognise_tail_default with this row's `tail` as its
     * parameter — after MOD-0.2 that default is the ONLY reader of `tail`
     * on the lookup path ("tail survives only as the parameter of a
     * tail_default recogniser"). The signature deliberately receives the
     * row's tail and NOTHING ELSE of the row (R11/M5): a recogniser that
     * could read its row would be a second, uncheckable home for tier-2
     * facts like the module name. */
    int  rank;
    bool (*recognise)(const char *at, size_t avail, const char *tail);

    /* MOD-0.3b: the two producing ports (full doc on ExtPort above). Every
     * macro initialises BOTH explicitly — -Wextra's missing-field-initializers
     * is the enforcement, the same property MOD-0.2 measured for rank and
     * recognise. Unwired in slice 1: nothing on the compile path reads them
     * until the classes producers land, which byte-identity asserts. */
    ExtPort aport;   /* atom position */
    ExtPort cport;   /* class position */

    /* [M6.6.2 wave F] D71 ITEM 3's `family` FIELD — THE INDEX LAYER's ONLY
     * NEW FACT, and it is deliberately a bare string rather than a table.
     *
     * WHAT IT HOLDS: the FAMILY's CANONICAL SYNTAX — the spelling the index
     * prints for the whole group. NULL means "this row is its own family",
     * which is every row but the twelve alpha spellings today, and the index
     * renders such a row exactly as it always has.
     *
     * WHY THE CANONICAL SYNTAX IS ITSELF THE GROUPING KEY. The alternative
     * was a family NAME plus a separate `RegFamily` table carrying the
     * canonical syntax and the resolver rule, and that table would be a
     * SECOND HOME for a string the rows already hold (D24). Members of a
     * family are the rows whose `family` compares equal; the family's
     * canonical syntax IS that key; and the resolver rule — how a member
     * resolves to the family's construct — is the member row's own `note`,
     * which every row already carries and which registry_check requires to be
     * non-empty. So the field adds one fact and stores it once.
     *
     * FOR A FAMILY WHOSE CANONICAL SPELLING IS ALSO A MEMBER (this wave's
     * six: `(?=...)` is both the family key and the syntax of the primary
     * row), the primary keeps `family == NULL` and the ALIASES point at its
     * `syntax`. That is not two homes for the same string: the primary owns
     * the string, and an alias holds a REFERENCE to it that
     * `tests/registry/registry_check.c` resolves and fails loudly on if it
     * dangles. src/parse/mod_lookaround.c's `la_kind` resolves the very same
     * reference to reach the primary's three `u.look` flags, so the alias
     * cannot disagree with its primary about what it means.
     *
     * FOR A FAMILY WITH NO SUCH MEMBER — recursion's `(?1)`..`(?9)`, whose
     * index line D71 spells `(?N)` and which is no row's own syntax — the key
     * is simply a family-level spelling and every member carries it,
     * including the one an unwary reader would call the "first". That is the
     * shape the next customer joins in: give all ten digit rows
     * `family = "(?N)"` and `\g<1>`/`\g'1'` theirs, change nothing else, and
     * the index collapses them with `built` ANDed across the members. Their
     * dispatch identity — ten byte-keyed rows, R6 — is untouched, which is
     * what D71 item 3 means by "rows keep their byte-keyed dispatch identity".
     *
     * LAST IN THE STRUCT, after the ports, for the reason the roadmap/quant
     * block gives one field group up: every macro in registry.c initialises
     * it explicitly, so a macro that forgot it is a -Wextra
     * missing-field-initializer rather than a silent NULL that reads as a
     * claim ("this row is its own family") nobody wrote. */
    const char *family;

    /* [DD-11.1] D85's replacement/definition table, NULL for a row with
     * nothing to say (same shape and same reason as `family` above — see
     * the type comment before `struct RegRow` for the placement rationale
     * and the r43 predicate-representation ruling). LAST for the identical
     * -Wextra reason `family` states. */
    const RegDef *definitions;
};

/* [M6.4.2 / SR-8] The engines mask a node contributes to the pattern-wide AND.
 * ONE reader of `Ast.reg`, so "an unstamped node claims both engines" is
 * written once rather than at every consultation site. */
static inline unsigned pcrec_ast_engines(const Ast *a)
{
    return a->reg ? a->reg->engines : (ENGM_DFA | ENGM_VM);
}

/* src/parse/registry.c */
const RegRow *pcrec_registry(RegKind k, size_t *n);
/* [DD-11.1] the CROSS-KIND syntax lookup a `DEFK_ROW` chain resolves through
 * (below) — `family`'s own resolution idiom (mod_lookaround.c's `la_kind`),
 * generalised past ONE `RegKind`: `family` only ever names another `RK_GROUP`
 * row, but a chain may cross kinds (`$`, `RK_BARE`, chains to `\Z`, `RK_ESC`).
 * Matches `syntax` by exact string equality across every kind `RK_COUNT`
 * enumerates; NULL means no such row (a dangling reference — the caller's
 * job to fail loudly on, exactly as `la_kind`'s own NULL does). */
const RegRow *pcrec_registry_row_by_syntax(const char *syntax);
/* `at` points at the byte AFTER the doorway's selector byte and `avail` is how
 * many bytes remain there, so a row's `tail` can be compared without the caller
 * knowing any row exists. Passing avail = 0 asks the tail-less question and is
 * what a truncated pattern supplies — a row whose tail cannot fit does not
 * match, which is why `(?P` at end-of-pattern falls to the bare-`P` row rather
 * than reading past the end. */
const RegRow *pcrec_registry_find(RegKind k, int sel, const char *at, size_t avail);
/* The default recogniser (MOD-0.2): answers when `tail` is a prefix of
 * at[0..avail), and always when the row has no tail (the bucket's fallback —
 * D32 §2's "positive and local"). A NULL `at` is the tail-less question
 * exactly as it was under SR-9. */
bool pcrec_recognise_tail_default(const char *at, size_t avail, const char *tail);
/* Does this row's recogniser answer for the text? The engine's own dispatch
 * predicate, exposed so checks count answers with the same code the
 * arbitration runs — one source, no drift (R15). */
bool pcrec_registry_row_answers(const RegRow *r, const char *at, size_t avail);
/* The MOD-0.2 engine behind pcrec_registry_find: every sel-matching row's
 * recogniser runs, the highest-ranked ANSWERING row wins, and two answers at
 * the WINNING rank set *ambiguous — the D32 §2 defect, which the escape and
 * group doorways report as an internal error rather than resolving silently.
 * `ambiguous` may be NULL for callers that only want the row. */
const RegRow *pcrec_registry_arbitrate(RegKind k, int sel, const char *at,
                                       size_t avail, bool *ambiguous);

/* src/parse/mod_modifiers.c — module `modifiers` (MOD-0.5b), moved out of
 * registry.c WITH the measured grammar block that establishes it (the
 * probes-and-code-together rule; see the file's own header for why). */
/* Is `at[0..avail)` a valid PCRE2 inline option run — the text starting at the
 * byte after `(?`, up to and including its `)` or `:` terminator? The grammar
 * is measured against libpcre2; see mod_modifiers.c. */
bool pcrec_registry_option_run_ok(const char *at, size_t avail);
/* The twelve GROUP_OPT rows' `recognise` field (retires RF_OPTION_RUN). A
 * MARKER, not the check itself — always answers true, identically to the
 * tail-less default — so ext.c can key off `r->recognise == this pointer`
 * instead of a flag; see its own comment for why it does not run
 * pcrec_registry_option_run_ok directly. */
bool pcrec_registry_option_run_recognise(const char *at, size_t avail,
                                         const char *tail);
/* The twelve GROUP_OPT rows' atom-port producer (MOD-0.5c): parses the
 * validated run at `from` (the SELECTOR byte — the run includes it),
 * applies the per-letter deltas to cx->mods or refuses per letter, and for
 * the `:` terminator parses the body through pcrec_parse_body under the
 * new state. Returns EXT_NODE with `end` past the construct's `)`; the
 * cursor is returned UNMOVED (check06). Only called at a post-gate
 * WANT_RESULT on a run pcrec_registry_option_run_ok accepted — which
 * includes the RECOGNISED-MALFORMED runs (the err-194 shapes) this port
 * exists to diagnose. */
ExtResult pcrec_modport_optrun(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from);

/* src/parse/mod_named_groups.c — module `named-groups` ([M6.3]). The FIRST
 * producer wired onto a registry row whose `engines` mask had excluded
 * ENGM_DFA (tests/registry/registry_check.c's check_engine_capability
 * tripwire is tuned to that event) — resolved by RECLASSIFYING the three
 * declaring rows' `engines` to ANY_ENGINE rather than by building SR-8's
 * general lowering-time consultation: a named group's AST is an ordinary
 * A_CAP node, indistinguishable from a plain numbered group's, so the
 * EXISTING generic capture-forcing rule (src/opt/select_engine.c's
 * `forces_captures`: ENGM_VM whenever `cx->want_caps && cx->ncap > 0`)
 * already forces the VM whenever this construct actually delivers a
 * capture slot, and a `--no-captures` build compiles it on the DFA exactly
 * as it would a plain group. See docs/dev/decisions.md's [M6.3] entry. */
ExtResult pcrec_ngport_declare(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from);

/* src/parse/mod_atomic_groups.c — module `atomic-groups` ([M6.4.2]). The
 * `(?>...)` group port: parses the body and returns an A_ATOMIC node STAMPED
 * with the row (SR-8/D67, `Ast.reg`). It is the SECOND VM_ONLY producer, and
 * the one the engine-capability tripwire was written to fire for a second time
 * and then be replaced by — see src/opt/select_engine.c's generic
 * `forces_registry` analysis, which is SR-8 as D55 specified it.
 *
 * The possessive SUFFIXES share this module and this node kind but NOT this
 * port: `X q+` desugars to `A_ATOMIC(A_REP(X))` at src/parse/parse.c's own
 * quantifier site, which is where the `+` is recognised. Their registry rows
 * (RK_QUANTSUFFIX) exist for the DUMP and are what parse.c stamps FROM, so the
 * mask and the `why` text still have exactly one home. */
ExtResult pcrec_agport_atomic(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from);
/* The RK_QUANTSUFFIX row for a quantifier spelled by its own selector byte
 * (`*`, `+`, `?` or `{`), for parse.c's desugaring to stamp from. NULL is a
 * registry defect and the caller says so rather than shipping an unstamped
 * node — src/parse/mod_atomic_groups.c. */
const RegRow *pcrec_atomic_suffix_row(int quant_byte);

/* [M6.6.2] src/parse/mod_lookaround.c — module `lookaround`. THE ONE PORT ALL
 * SIX ROWS DISPATCH THROUGH (design §8.1): `(?=...)` `(?!...)` `(?*...)` and
 * the three `(?<` tails `=` `!` `*`. It returns an `A_LOOK` node whose three
 * `u.look` flags it resolves from the row's own `sel`/`tail` — the six
 * constructs differ in NOTHING ELSE — stamped with the row (SR-8/D67).
 *
 * ONE PORT AND NOT SIX, because a second one would be a second place the
 * `<`-tail split is decided; and that split is exactly how D65's `built`
 * column moves in two waves rather than one. At [M6.6.2] wave B+C the port
 * ACCEPTS the three lookahead tails and DECLINES the three `<` tails at
 * `WANT_RESULT` (the "gate open, port missing" refusal
 * `pcrec_construct_built_status` reads), so three rows read `built` and three
 * read `unbuilt`; wave D deletes the decline when the back-step seam entry
 * lands. See the file's header for what wave D changes and what it does not.
 *
 * IT ALSO OWNS §2.7's `\K` CHECK — an `A_KRESET` anywhere in a lookaround
 * body is a parse-time refusal, recursively through nested groups and nested
 * lookarounds, matching libpcre2's default (err 199). */
ExtResult pcrec_laport_group(Ctx *cx, const RegRow *rw, ExtWant want,
                             size_t at, size_t from);

/* [DD-14.LB] MODULE `lookaround`'s HALF OF THE DEFERRED WIDTH RE-CHECK — the
 * §2.5 fixed-width rule, asked a SECOND TIME, at a second TIMING.
 *
 * THE RULE STAYS IN THE MODULE AND THE TIMING LIVES IN THE PASS. That split
 * is the whole point of these two declarations: `pcrec_postresolve` knows
 * WHEN the graph exists and in what ORDER to visit, and knows nothing about
 * lookbehind widths; this file's implementation knows the width rule and its
 * three refusal sentences, and knows nothing about the call graph. A pass
 * that inlined the rule would be a SECOND derivation of "is this branch
 * fixed-width" for the hook's to disagree with — the failure `u.look.widths`
 * is stored to prevent one level down.
 *
 * `_pending` answers "did the hook defer this node": true exactly for an
 * `A_LOOK` that is a lookbehind whose `widths` is still NULL. `_fix_widths`
 * resolves such a node — filling `u.look.widths` — or refuses via `ctx_fail`
 * at `u.look.at` with the hook's own wording, BYTE FOR BYTE (the doorway
 * epilogue `pcrec_ext_finish` is itself `ctx_fail(cx, at, "%s", msg)`, so the
 * two paths render identically by construction and not by transcription). It
 * is a no-op on any node `_pending` declines, so a future second caller
 * cannot use it to re-derive an already-resolved table. */
bool pcrec_lookaround_width_pending(const Ast *a);
void pcrec_lookaround_fix_widths(Ctx *cx, Ast *a);

/* [M6.5.2] src/parse/mod_named_groups.c — THE GROUP-NAME GRAMMAR, one home.
 *
 * Scans a subpattern name at `p[i..n)`: a leading ASCII letter or `_`, then
 * letters, digits and `_`, at most PCREC_MAX_GROUP_NAME bytes. Returns the
 * length (0 on a name that does not start), and sets `*why` to a
 * pcrec-authored diagnostic when the scan fails.
 *
 * IT IS SHARED BECAUSE IT IS ONE PCRE2 FACT WITH FOUR READERS. The declaring
 * port owns it, and module `backrefs`' three by-name reference spellings
 * (`\k<n>` `\k'n'` `\k{n}`, `\g{n}`, `(?P=n)`) must agree with it EXACTLY —
 * a reference whose name grammar is narrower than the declaration's cannot
 * name a group that exists, and one that is wider accepts a spelling PCRE2
 * refuses. That is the drift `pcrec_is_bare_anchor` was made one function for,
 * one construct later. */
size_t pcrec_group_name_scan(const char *p, size_t n, size_t i,
                             const char **why);

/* [M6.5.2] src/parse/mod_backrefs.c — module `backrefs`, the four producing
 * ports and the end-of-parse resolution pass. Design:
 * docs/design/backrefs_design.md, panel-approved at R32.
 *
 * FOUR PORTS, ONE NODE KIND. `pcrec_brport_digit` is the ten digit rows'
 * atom-position producer and owns PCRE2's octal disambiguation (§5) — it is
 * the ONLY one that can produce something OTHER than an `A_BREF`, because
 * rules 1 and 3 make `\0` and a re-read multi-digit run an ordinary character.
 * The other three are pure reference producers. Every one of them RECORDS a
 * pending reference rather than resolving it (see `PendingRef`). */
ExtResult pcrec_brport_digit(Ctx *cx, const RegRow *rw, ExtWant want,
                             size_t at, size_t from);
ExtResult pcrec_brport_g(Ctx *cx, const RegRow *rw, ExtWant want,
                         size_t at, size_t from);
ExtResult pcrec_brport_k(Ctx *cx, const RegRow *rw, ExtWant want,
                         size_t at, size_t from);
ExtResult pcrec_brport_pname(Ctx *cx, const RegRow *rw, ExtWant want,
                             size_t at, size_t from);

/* [DD-14 wave B+C] src/parse/mod_recursion.c — module `recursion`, the three
 * SUBROUTINE-CALL ports at the `(?` doorway. Design:
 * docs/design/subroutines_design.md §4.2's port table.
 *
 *   pcrec_rcport_num   `(?1)`..`(?9)` and their multi-digit continuations,
 *                      `(?0)`, `(?R)` — and §2.4a's LEADING-ZERO rule, which
 *                      is why this port re-reads the whole digit run from the
 *                      selector byte instead of trusting `rw->sel`.
 *   pcrec_rcport_rel   `(?+N)`, `(?-N)`, with the leading-zero and
 *                      relative-zero rules.
 *   pcrec_rcport_name  `(?&name)`, `(?P>name)`.
 *
 * The FOURTH doorway of §4.2's table — `\g<...>` / `\g'...'` — had no port
 * through wave B+C: those two rows carried `NO_PORT` and refused through
 * ext.c's ENABLED-BUT-UNBUILT epilogue, which is what kept their D65 `built`
 * column honest until wave D. mod_recursion.c's closing note records why the
 * brief's "one decline branch in pcrec_brport_g" turned out to be unreachable
 * code, and what wave D wired instead: both rows' `aport` now points at
 * `pcrec_brport_g` itself (src/parse/mod_backrefs.c), which gained `<`/`'`
 * arms that call back into `pcrec_call_node`/`pcrec_call_by_name` below. */
ExtResult pcrec_rcport_num(Ctx *cx, const RegRow *rw, ExtWant want,
                           size_t at, size_t from);
ExtResult pcrec_rcport_rel(Ctx *cx, const RegRow *rw, ExtWant want,
                           size_t at, size_t from);
/*   pcrec_rcport_define  `(?(DEFINE)...)` — D71 item 4. NOT a call: it is the
 *                        DEFINITION half, lowered as the `{0}`-callee shape
 *                        (an `A_REP` with rmin == rmax == 0 over the body,
 *                        the node `(?:BODY){0}` already produces), so no
 *                        pass below the parser gained a line for it. Its row
 *                        is tailed `DEFINE)` on the `(?(` doorway and is the
 *                        one row in this module that is NOT VM_ONLY — see
 *                        the port's own header for the measurement. */
ExtResult pcrec_rcport_define(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from);
ExtResult pcrec_rcport_name(Ctx *cx, const RegRow *rw, ExtWant want,
                            size_t at, size_t from);
/* [DD-14 wave D] Exported so `pcrec_brport_g`'s `<`/`'` arms (module
 * `backrefs`, the shared `\g` doorway, P3) build a PEND_CALL through this
 * file's own root/queue rule and FIRST-DECLARATION name rule instead of a
 * second copy of either. See mod_recursion.c's closing note. */
Ast *pcrec_call_node(Ctx *cx, const RegRow *rw, size_t at, bool is_relative,
                     int number, const char *name, const char *what);
ExtResult pcrec_call_by_name(Ctx *cx, const RegRow *rw, ExtWant want,
                             size_t at, const char *body, size_t blen,
                             size_t end, const char *what);

/* THE END-OF-PARSE PASS (§5.3), called from `pcrec_parse_info` and nowhere
 * else. Two jobs, in this order:
 *
 *   1. RESOLVE every pending reference against the final group count and the
 *      complete set of name declarations, filling each `A_BREF`'s `refs`
 *      array; a reference to a group that does not exist raises pcrec's own
 *      error-115-class diagnostic at the recorded offset.
 *   2. Under `--no-captures` ONLY, DELETE the `A_CAP` wrapper of every group
 *      no reference names, and return the possibly-new root.
 *
 * WHY (2) IS A DELETION AND NOT A CONSTRUCTION. Under `--no-captures` the
 * pre-[M6.5] parser built no `A_CAP` at all (`parse.c`'s capturing-`(` hook),
 * so a backreference had nothing to read — measured by R32 E6, which is why
 * §6.3 rules that a REFERENCED group keeps its internal slots and reports
 * none. Deciding at the `(` which groups will be referenced needs a lexical
 * pre-scan the project ruled out (`Ctx.ncap`'s comment: "the pre-scan is
 * dead"), and a forward reference makes the question unanswerable there in
 * principle. So the parser now builds the wrapper for every numbered group and
 * this pass removes the ones nothing reads. For a pattern with NO
 * backreference that deletes ALL of them, so the tree — and therefore the
 * emitted C — is what it has always been, BY CONSTRUCTION rather than by
 * inspection. That identity is what `tests/codegen/run_backref_identity.sh`
 * gates, `--no-captures` arm included. */
Ast *pcrec_bref_resolve(Ctx *cx, Ast *root);

/* Does this tree carry a backreference? Read by src/opt/select_engine.c, which
 * forces `EngineFit.prefilter` OFF for such a pattern (§7.1): the
 * backref-ERASED approximation a prefilter DFA would be built from is not a
 * sound superset once the referenced group holds an assertion or an
 * atomic/possessive operator, and even where it IS a superset its leftmost
 * SPAN differs from the true one on a large fraction of subjects — measured,
 * §7.2 — so the exact anchored window `engine_m4.md` §6.1's hybrid needs
 * cannot be had. src/opt/atomic.c, beside the other two tree predicates. */
bool pcrec_has_bref(const Ast *a);

/* THE MARKED SET (§3.2.4): `mark[g]` becomes true for every group number some
 * `A_BREF` in this tree can resolve to — the UNION of every node's `refs`,
 * which for a by-name reference over a duplicated name is EVERY member of the
 * run and not merely the member a given match resolves to (R32 re-check E13:
 * §8.3's chain reads them all at match time, so an unmarked member would be
 * read under write-on-traverse and re-admit E1 through it).
 *
 * A marked group is the one that pays for publish-at-close — a third slot and
 * a third trailed write per traverse — and an unmarked one emits exactly the
 * two writes it always did. `mark` has `ncap + 1` entries and the caller
 * zeroes it. src/opt/atomic.c. */
void pcrec_bref_mark(const Ast *a, bool *mark, int nmark);

/* [DD-14] Does this tree carry a SUBROUTINE CALL? `pcrec_has_bref`'s sibling,
 * in the same file and for the same reason (subroutines_design.md §4.3).
 *
 * IT DOES NOT FOLLOW `Ast.u.call.body` — design §4.4's rule for every
 * whole-tree predicate: the callee is visited at its own lexical position
 * anyway, and following the back edge would not terminate on `(a(?1))`.
 *
 * NO CALL SITE IN THIS WAVE. Its consumer is wave E's one line in
 * src/opt/select_engine.c, which forces `EngineFit.prefilter` OFF for a
 * call-bearing pattern (design §8.2: erasure is NOT a superset here, and §8.3
 * measured 21x-350x for the alternative). Declared and defined now because
 * wave A2 is the wave that owns the tree predicates; wired when there is a
 * producer that can make it answer anything but false. */
bool pcrec_has_call(const Ast *a);
/* [DD-14 wave G] `pcrec_has_call`'s narrowing: is there a call that is still a
 * JUMP? Reads `u.call.link`, so it is meaningful only AFTER
 * `pcrec_callgraph_build` — a SPLICED call has an exact finite lowering and is
 * neither structurally VM-only (§8.1) nor a bar to the prefilter (§8.2/§8.3);
 * a LINKED one is both. See src/opt/atomic.c for the full argument. */
bool pcrec_has_linked_call(const Ast *a);
/* [DD-14 wave G] Can any emitted code WRITE a capture slot? `A_REP{0,0}` emits
 * nothing and a subroutine call is capture-transparent (design §3.1), so a
 * group reached only through those can never leave a visible capture — it is
 * still COUNTED and still reported UNSET, exactly as PCRE2 reports it, but it
 * does not need the capture-recording engine. src/opt/select_engine.c's
 * `forces_captures` is the consumer; src/opt/atomic.c has the argument. */
bool pcrec_has_live_capture(const Ast *a);

/* [DD-14 wave B+C] THE CALL GRAPH (src/opt/callgraph.c). Opaque and
 * arena-owned; `cx->callgraph` is NULL for a call-free pattern, which is what
 * keeps such a pattern's compile byte-identical to what it was before this
 * module.
 *
 * WHERE IT RUNS IS LOAD-BEARING, NOT CONVENIENT. It must run AFTER every pass
 * that REBUILDS a node — `pcrec_altcls` (which allocates a fresh `A_CAP` over
 * a merged class) and `pcrec_discharge_atomic` (which splices an `A_ATOMIC`
 * out) — because it is the only writer of `Ast.u.call.body`, and a `.body`
 * captured before those passes names a subtree that is no longer in the tree.
 * Under `CALL_LINKAGE` that would emit the callee REGION from the stale
 * subtree and the LEXICAL occurrence from the new one: two programs for one
 * group, with §4.4c's slot indices and §5.3's `W` computed over whichever was
 * handed over. Wave A2 found the hazard (commit 513de65); the file's own
 * header carries the full argument and the two witnesses. It must equally run
 * BEFORE emission, since the emitter reads `.body`, `link` and `minw`.
 *
 * IT DOES FOUR THINGS: binds `.body` for every call from the FINAL tree; sets
 * `link = CALL_LINKAGE` on every node (§6.3 — the arena's `CALL_SPLICE` is
 * the wrong default in the unsound direction, a spliced recursive call being
 * an infinite emitter); runs §4.4b's `minw` Kleene fixpoint; and runs
 * [DD-14.LB]'s `maxw` fixpoint, its MIRROR IN EVERY SENSE INCLUDING THE ONE
 * THAT MATTERS (it descends from `PCREC_W_UNBOUNDED` where `minw` descends
 * from `PCREC_MINW_MAX`, because over-estimating is `pcrec_maxw`'s free
 * direction and under-estimating is its miscompile).
 *
 * IT ASKS NO MODULE'S QUESTION. Wave B+C's draft re-asked module
 * `lookaround`'s §2.7 `\K` refusal here, and MEASUREMENT deleted the check
 * (PCRE2's `\K` rule is LEXICAL — see this file's own standing note, and
 * `tests/recursion/kreset.rxt`). The graph-needing checks that DID survive
 * live in `pcrec_postresolve` below, which is a separate pass so that
 * "build the graph" and "enforce somebody's rule with it" stay separate
 * jobs. */
void pcrec_callgraph_build(Ctx *cx, Ast *root);

/* [DD-14.LB] THE POST-RESOLUTION CHECKS — src/opt/postresolve.c. The pass for
 * every rule that (a) must refuse a pattern AT A PATTERN OFFSET and (b) cannot
 * be decided until the call graph exists.
 *
 * IT IS A GENERAL MECHANISM WITH ONE CUSTOMER TODAY, not a fold of that
 * customer. The shape it generalises is a TIMING gap, and the gap is
 * structural rather than incidental: a module's parse hook is the only place
 * in this compiler that holds a pattern offset, and `Ast` carries no position
 * of any kind (PARSE-1), so a rule that needs the graph has nowhere to raise
 * its diagnostic from — unless the hook RECORDS the offset on the node and a
 * later pass reads it back. Every future rule of that shape (§6.3's splice
 * eligibility, a variable-length lookbehind follow-on, a call inside a
 * construct some module has not met yet) is the same three moves, so the
 * pass owns the WALK and the ORDER and each module owns its own RULE.
 *
 * ORDER IS PART OF THE CONTRACT: it visits the recorded constructs in
 * ASCENDING PATTERN OFFSET, so a pattern with two offending lookbehinds
 * refuses at the FIRST, which is what the parse hook would have done and what
 * every other diagnostic in this compiler does. A walk order would have
 * reported whichever the tree spine reached first, which for a left-nested
 * `A_CAT` is the LAST one written.
 *
 * IT RUNS AFTER `pcrec_callgraph_build` AND BEFORE THE MACHINE BUILDS, and it
 * is a NO-OP for a call-free pattern (`cx->callgraph == NULL` and nothing was
 * ever recorded), which is what keeps such a pattern's compile byte-identical
 * to what it was before module `recursion` existed. */
void pcrec_postresolve(Ctx *cx, Ast *root);

/* The graph's readers, for `src/gen/emit_vm.c`, which owns the two fixpoints
 * whose RECURRENCE lives in the emitter — `vm_nullable`'s (a `static` there,
 * and a second copy would be a second answer to "can this match empty") and
 * `W`'s (a set of SLOT INDICES, which exist nowhere but the emitter's own
 * layout). Targets are ASCENDING and `0` means THE ROOT. */
int         pcrec_callgraph_ntargets(const struct CallGraph *cg);
int         pcrec_callgraph_target(const struct CallGraph *cg, int i);
const Ast  *pcrec_callgraph_body(const struct CallGraph *cg, int i);
int         pcrec_callgraph_index(const struct CallGraph *cg, int target);
/* Can region `i` reach region `j` through any chain of calls? TRANSITIVE, so
 * `reaches(i, i)` is exactly "target i is in a cycle" — §6.3's splice
 * eligibility question (wave G) and §4.4b's cycle test in one relation. */
bool        pcrec_callgraph_reaches(const struct CallGraph *cg, int i, int j);
/* [DD-14 wave G] Does every call site naming target `i` SPLICE (design §6.3)?
 * The per-node answer is `Ast.u.call.link`; this is the same fact addressed by
 * region index, which is what the emitter needs to decide whether to emit a
 * SHARED REGION for `i` at all — a target with no linked site has no region,
 * no entry label, no exit label and no second `goto *`. */
bool        pcrec_callgraph_spliced(const struct CallGraph *cg, int i);

/* src/parse/mod_uprops.c — module `unicode-props` (MOD-0.6 phase 2). No
 * producer: `\p`/`\P` always REFUSE, but with a REFINED, load-bearing-offset
 * split between "malformed shape" and "well-formed, unrecognised name" —
 * see the file's own header for the full account, docs/design/design_notes_mod06.md
 * for the design, and D33 §9's obligation this discharges (an EXT_* outcome
 * exists here only in the sense that the refusal text/offset changed;
 * SCALAR/MEMBERS/NODE remain unreachable for this module until a producer
 * lands, exactly as MOD-0.3b's own comment on ExtWhat describes). */
/* The `\p`/`\P` rows' `recognise` field — a MARKER, not the check itself
 * (mirrors pcrec_registry_option_run_recognise): both rows are alone in
 * their bucket, so this always answers true, identically to the tail-less
 * default. Its only purpose is POINTER IDENTITY: ext.c keys off
 * `r->recognise == pcrec_registry_uprops_recognise` to hand off to
 * pcrec_modport_uprops instead of the generic RD_MODULE fallback text. */
bool pcrec_registry_uprops_recognise(const char *at, size_t avail,
                                     const char *tail);
/* The \p/\P body scanner (see mod_uprops.c's header for the full algorithm
 * and its measured basis). Called DIRECTLY from pcrec_ext_escape — not
 * through r->aport/r->cport, which stay NO_PORT on both rows this phase —
 * keyed on the recogniser marker above. Always returns EXT_REFUSAL. */
ExtResult pcrec_modport_uprops(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from);

/* ---- doorway 3's NAME tables (Q1) --------------------------------------
 *
 * The other three doorways are decided by a BYTE and a RegRow can carry the
 * whole answer. `(*` is decided by a NAME, and until Q1 pcrec had no name
 * table at all: one catch-all row answered "requires module 'verbs'" for every
 * name, including names PCRE2 does not have. That was a live over-promise —
 * `(*NOTAVERB)` was told a module would implement it — and it made an external
 * name differential impossible, because pcrec's answer did not depend on the
 * name. See docs/dev/decisions.md D25.
 *
 * THESE ARE NOT RegRows, deliberately. A RegRow names a module, a feature bit,
 * an engine mask and a diagnostic template; fifty verb rows would repeat one
 * module fifty times and carry fifty hand-written notes nobody has measured —
 * the fiction SR-1 refused to write. A VerbName answers exactly one question,
 * "does PCRE2 have this name and in which forms", and EVERY BIT OF IT IS
 * VERIFIED against libpcre2 by tests/registry/pcre2_check.c (PC-3). Nothing
 * here is asserted; it is all recorded measurement.
 *
 * PCRE2 keeps TWO tables and picks between them by the CASE of the name's
 * first byte, with a different "not recognized" error for each. Measured
 * against libpcre2 10.46 with options = 0 (no PCRE2_UTF, no PCRE2_UCP):
 * `(*accept)` is error 195 and `(*Accept)` is error 160. */
enum {
    VF_BARE     = 1u << 0,  /* (*NAME)                                       */
    VF_ARG      = 1u << 1,  /* (*NAME:arg) with a non-empty arg              */
    VF_EMPTYARG = 1u << 2,  /* (*NAME:)                                      */
    VF_EQNUM    = 1u << 3,  /* (*NAME=digits), at least one digit            */

    /* The argument is a SUBPATTERN, not a name run, so the doorway does not
       require a `)` to be present: `(*pla:x` is PCRE2 error 114 "missing
       closing parenthesis" (the name WAS recognised) while `(*ACCEPT:x` is
       error 160 (it was not). One bit, two measured behaviours. */
    VF_GROUPARG = 1u << 4,

    /* Valid only at the very start of the pattern: `a(*CR)` is error 160.
       PCRE2 allows a RUN of these (`(*UTF)(*CR)` compiles); pcrec's rule is
       offset 0 exactly — see pcrec_ext_verb for why that is currently
       equivalent and what would change it. */
    VF_ATSTART  = 1u << 5
};

typedef struct {
    const char *name;      /* exact, case-sensitive                          */
    unsigned    forms;     /* VF_* mask: the forms libpcre2 ACCEPTS          */

    /* A form outside `forms` normally produces the table's generic "not
       recognized" message, because that is what PCRE2 produces. `(*MARK)` and
       `(*MARK:)` are the measured exception (error 166), so the row carries
       its own message and the mask of forms it applies to. Both NULL/0 for
       every other name. */
    unsigned    own_forms;
    const char *own_msg;

    /* ROADMAP_NONE = inherit the RK_VERB row's value (PLANNED — module
     * `verbs`). Set explicitly on the names the compliance survey marks
     * OUT-OF-SCOPE; disposition is a PER-NAME fact because RK_VERB is one
     * row for ~50 names spanning both values (design §17.2, R14/C2-F5:
     * `(*COMMIT)` is NEVER while `(*pla:...)` is a lookaround in verb
     * spelling). */
    Roadmap     roadmap;

    /* Meaningful only through the RK_VERB row's QF_FORM (see QuantFact). */
    QuantVerb   quant;
} VerbName;

typedef struct {
    const char     *unknown_msg;  /* PCRE2's wording for a name not in `rows` */
    const VerbName *rows;
    size_t          n;
} VerbTable;

/* Defined in src/parse/mod_verbs.c since MOD-0.4 (the migration test), moved
 * WITH the verb_upper/verb_lower/verb_tables data and their measurement
 * provenance comments — was src/parse/registry.c until this move. */

/* The table PCRE2 would consult for a name whose first byte is `first`. Never
 * NULL: every byte selects one of the two. */
const VerbTable *pcrec_registry_verb_table(int first);
/* Exact lookup within that table, or NULL. */
const VerbName  *pcrec_registry_verb_find(const VerbTable *t,
                                          const char *name, size_t len);
/* Iteration for tests and for --list-verbs; `which` is 0 (the upper table) or
 * 1 (the lower one), matching the order docs and dumps present them in. */
const VerbTable *pcrec_registry_verb_tables(int which);
/* [M6.6.2 wave F] THE NAME's OWN ROW, or NULL when the name has none — which
 * is every verb except the twelve `(*` alpha lookaround spellings, and NULL
 * is what makes the `(*` doorway row the default (design §8.2's "everything
 * else inherits").
 *
 * DESIGN §8.2 ASKED FOR AN OPTIONAL MODULE/FEATURE PAIR ON THE VerbName; this
 * is that recommendation in the form ASK 3's own ruling made available. Frank
 * ruled YES to a REGISTRY ROW for each of the twelve, and a row already
 * carries the module and the feature AS A CHECKED PAIR (registry.c's `M_*`
 * macros exist so a row cannot print one module while carrying another
 * module's bit). Copying that pair onto the VerbName as well would be a
 * second home for it (D24) needing a mechanism to keep the two equal, so the
 * name resolves to the ROW instead — which is strictly more than the pair,
 * since the row also carries the port, the syntax, the engines mask and the
 * roadmap the doorway now reads. Defined in registry.c beside the rows,
 * because it reads `tail` AS A NAME and only those rows license that reading. */
const RegRow *pcrec_registry_verb_name_row(const char *name, size_t len);
/* PCRE2's cap on a verb NAME and the complaint past it — shared by both
 * tables, so it is not a VerbTable field. Returns the message; sets *max. */
const char *pcrec_registry_verb_name_limit(size_t *max);

/* The POSIX class-bracket NAME table, for RF_CLASS_NAMED rows — a THIRD
 * schema beside RegRow and VerbName, on D25's reasoning: a POSIX name answers
 * "does PCRE2 have this name" plus, since MOD-0.3a, WHOSE construct it is —
 * because two of the sixteen are not character classes at all. `[[:<:]]` and
 * `[[:>:]]` are zero-width word-boundary assertions, so their honest module
 * is `assertions` (the module `\b`'s own row carries), not the doorway's
 * `classes`; the split is data here, never a special case at a call site. */
typedef struct {
    const char *name;              /* case-sensitive; exactly one spelling */
    bool        whole_class_only;  /* legal ONLY as the class's entire content:
                                      `[[:<:]]` compiles, `[x[:<:]]`,
                                      `[^[:<:]]`, `[[:<:]a]` do not (R9/C3-4);
                                      also unnegatable — `[[:^<:]]` is err 130 */
    unsigned    feature;           /* FEAT_* of the module that will produce it */
    const char *module;            /* that module's name, for diagnostics */
} PosixName;

/* `name` may carry a leading `^` (`[[:^alpha:]]` is a real construct; a
 * whole-class-only name never negates). Returns true if PCRE2 has it;
 * `pcrec_registry_posix_unknown_msg` is what to say when not. */
bool        pcrec_registry_posix_known(const char *name, size_t len);
bool        pcrec_registry_posix_whole_class_only(const char *name, size_t len);
const char *pcrec_registry_posix_unknown_msg(void);
/* Exact lookup (no `^` handling — strip it first), or NULL. */
const PosixName *pcrec_registry_posix_find(const char *name, size_t len);
/* Iteration, for tests and --list-verbs' sibling checks. */
const PosixName *pcrec_registry_posix_names(size_t *n);

/* src/parse/ext.c — the four doorways out of the base grammar (SR-2). The
 * doorway VOCABULARY (ExtWhat / ExtWant / ExtResult and its contract doc)
 * moved above RegRow when MOD-0.3b embedded ports in rows — the dependency
 * inverted; the doorway FUNCTIONS stay here, except `pcrec_ext_verb` (MOD-0.4,
 * the migration test): it moved to src/parse/mod_verbs.c WITH the `(*`
 * doorway's VerbName tables and accessors, keeping this file's exact
 * signature — parse.c's call site did not change. See mod_verbs.c's header
 * for why the move needed no new port/recognise wiring. */

/* THE SHARED GATE and THE SHARED REFUSAL EPILOGUE MACRO, below, are the two
 * pieces of doorway machinery `pcrec_ext_verb` still needs after MOD-0.4's
 * move — promoted from `static`/file-local so mod_verbs.c can call/use them
 * too, with exactly one definition each (ext.c keeps the definitions; the
 * full rationale comments live there, not duplicated here). */
/* Demotes RESULT to VERDICT for a row whose module is not enabled, floors at
 * VERDICT. See ext.c's own comment on the definition for the full ASK-contract
 * rationale. */
ExtWant pcrec_ext_gate(const RegRow *r, ExtWant want);

/* Format a refusal at claim time and return it — relies on the enclosing
 * doorway naming its gated ask level `want`, exactly as ext.c's comment on
 * REFUSE's original site documents. Needs <stdio.h> in the includer for
 * snprintf; every TU that invokes it already carries that include. */
#define REFUSE(atpos, ...) do {                                              \
        ExtResult res_ = { .what = EXT_REFUSAL, .at = (atpos), .msg = "",    \
                           .answered_at = want };                            \
        snprintf(res_.msg, sizeof res_.msg, __VA_ARGS__);                    \
        return res_;                                                         \
    } while (0)
/* THE ENABLED-BUT-UNBUILT REFUSAL, promoted out of ext.c at [M6.6.2] when a
 * SECOND consumer arrived (src/parse/mod_lookaround.c's wave B+C tail
 * decline) — `pcrec_ext_gate`'s move at MOD-0.4, one construct later, and for
 * that move's reason: one definition rather than a second copy of the
 * sentence. The full rationale for the DIAGNOSTIC lives at ext.c's arm and is
 * deliberately not duplicated here.
 *
 * IT READS `r` FROM THE ENCLOSING SCOPE, exactly as `REFUSE` reads `want`, and
 * that convention is the price of both macros being macros: the includer must
 * name the dispatching `const RegRow *` `r`. `PCREC_UNBUILT_MARKER` is inside
 * the format on purpose — it is the substring `pcrec_construct_built_status`
 * keys on to recognise this shape from outside (D65), so a reword that lost it
 * would silently stop a construct being classified `unbuilt`. */
#define UNBUILT(pos, fmt, ...) \
    REFUSE((pos), "module '%s' " PCREC_UNBUILT_MARKER " " fmt \
           " is not implemented yet", r->module, ##__VA_ARGS__)
/* A row whose diag value does not belong to its kind is a registry defect,
 * not a pattern error — see REFUSE above; the wording is deliberately not a
 * "requires module" diagnostic since nothing a caller writes can produce it. */
#define BAD_ROW(at, what) \
    REFUSE((at), "internal error: malformed registry row for " what)

/* The ONE epilogue: renders a refusal via ctx_fail (byte-identical to the
 * pre-epilogue diagnostics — same format results, same offsets), returns
 * normally on EXT_NOT_MINE. Every doorway call in parse.c is followed by
 * exactly this call. */
void pcrec_ext_finish(Ctx *cx, const ExtResult *r);

ExtResult pcrec_ext_escape(Ctx *cx, ExtWant want, int c, bool in_class,
                           size_t at);
ExtResult pcrec_ext_group(Ctx *cx, ExtWant want, int c2, size_t at);
ExtResult pcrec_ext_verb(Ctx *cx, ExtWant want, size_t at);
/* The one doorway that can DECLINE: `[` is an ordinary class member most of
 * the time, so EXT_NOT_MINE means "no construct here" and the caller carries
 * on with member parsing. (Its R5-era history — a bool return no path could
 * make true, then `void` — is resolved by the value contract: the decline is
 * IN the value now, and a future "consumed, carry on" outcome extends
 * ExtWhat where both call sites' walls force it to be handled.)
 *
 * `at_content_start` says the construct begins at the FIRST byte of the class's
 * content — no member before it and no `^`. It exists for `[[:<:]]` and
 * `[[:>:]]`, which libpcre2 recognises ONLY as a class's entire content
 * (R9/C3-4); every other POSIX name works in any position. */
ExtResult pcrec_ext_class_bracket(Ctx *cx, ExtWant want, int c2, size_t at,
                                  size_t from, bool at_class_open,
                                  bool at_content_start);

/* True when a `[X...X]` construct really opens at `from` with delimiter `c2` —
 * K4's scan as a predicate, for callers that must ASK rather than diagnose.
 * Used by the range-endpoint check: PCRE2 makes `[0-[:digit:]]` error 150, and
 * pcrec used to read the `[` as a literal and emit a matcher (R9/SPEC-FA).
 * Lives in scans.c since slice 9. */
bool pcrec_ext_class_pair_opens(Ctx *cx, int c2, size_t from);

/* src/parse/scans.c — the ALWAYS-LIVE extent scans (design §12; slice 9).
 * Pure over (pat, patlen) on purpose, named per check01's discovery
 * convention, and their TU must never link the enabled-set symbols below —
 * the linker is the check's oracle. */
bool   pcrec_class_delim_extent_scan(const char *pat, size_t patlen, int c2,
                                     size_t from, size_t *close_at);
/* True iff `at` points at a `{` whose body is quantifier-SHAPED by
 * try_quant's grammar (values unchecked — err-104/105 bodies are shaped).
 * Two load-bearing callers by design: try_quant's pre-test and the `\N{`
 * row's recogniser. See the scan's own comment. */
bool   pcrec_brace_quant_shape(const char *at, size_t avail);
size_t pcrec_verb_name_extent_scan(const char *pat, size_t patlen,
                                   size_t nstart);

/* src/parse/enabled.c — the enabled feature set (slice 9): one home,
 * process-wide, written once by the CLI's --features before any compile.
 * NOT a pcrec_options field (D20 keeps the core API's option surface
 * scalar); promote a library channel later if a caller wants one. */
bool     pcrec_feature_enabled(unsigned featmask);
unsigned pcrec_enabled_mask(void);
int      pcrec_enabled_set_spec(const char *spec, char *err, size_t errsz);
/* D37 (docs/dev/decisions.md): the currently-installed set's own NAME
 * ("std1", "all", "none", or "explicit" for a hand-written module list)
 * and its EXPANDED module list (comma-separated, rendered from the mask —
 * never NULL, "" when nothing is enabled). Filled by pcrec_enabled_set_spec
 * at spec-parse time; src/gen reads both at emission time to stamp the
 * artifact (D37's reproducibility promise). Returned strings point at
 * static storage — do not free. */
const char *pcrec_enabled_set_label(void);
const char *pcrec_enabled_set_modules(void);
/* D37's bare-default MAPPING POINT: the one place "no --features flag"
 * resolves to a named value from --features' own vocabulary. Stays "none"
 * through [STD1] phase A on purpose — see enabled.c's own comment on this
 * constant before changing it. */
extern const char *const PCREC_DEFAULT_FEATURES;

/* ---- [DD-13b.W1] the `.rxt` SOURCE file (src/parse/rxt_source.c) -------
 *
 * THE ONE HEAD PARSER's types. `--source` must resolve `lib`/`name`/
 * `target`/`config` before it can compile anything, so pcrec reads the
 * file's HEAD; the harness keeps its own BODY parsers and is TOLD where
 * the body starts (`--list-source`'s `line` column). See
 * docs/design/dd13_format/w1_impl.md §1.1 for the seam ruling and §1.8
 * for the dump's contract, docs/spec/rxt_format.md for the format.
 *
 * ONE ROW TYPE. A `lib`, a `target`, a `config` and a `pattern` block are
 * each (kind, name, value, settings, a list), and the dump prints them in
 * FILE ORDER — which separate per-kind arrays cannot express without a
 * further structure to interleave them. So one discriminated row, in file
 * order, and typed lookup is a filter over it. W1.2's target BUILD and
 * W1.3's composer are what would earn a definition-shaped record with
 * fields a row has no place for; D77 says that is when to add one. */
typedef enum {
    RXT_DECL_LIB,          /* `lib "path"` / `lib <store>`   — value      */
    RXT_DECL_TARGET,       /* `target p = def [with c,...]`  — name/value */
    RXT_DECL_CONFIG,       /* `config c [from a,b]` + body   — name       */
    RXT_DECL_DESCRIPTION,  /* file-level `description`       — value      */
    RXT_DECL_PATTERN       /* a pattern BLOCK                — value=text */
} RxtDeclKind;

typedef struct {
    RxtDeclKind kind;
    size_t      line;         /* 1-based line of the declaration/block    */
    const char *name;         /* target prefix / config name / block name */
    const char *value;        /* lib path-ref, target definition, prose,
                               * or — on a pattern row — the pattern text
                               * REST-OF-LINE VERBATIM (it may hold a TAB) */
    const char *description;  /* a pattern block's own `description`      */
    const char *flags;        /* `flags` letters                          */
    const char *features;     /* `features` module list                   */
    int         features_only;/* the block wrote `features only` (M14)    */
    const char *encoding;
    const char *engine;       /* "vm" | "dfa"                             */
    long        budget_steps; /* -1 when unset — 0 is a legal budget      */
    long        budget_frames;
    const char *with_list;    /* target's `with` config list, as written  */
    const char *from_list;    /* config's `from` config list, as written  */
    const char *pcrec_raw;    /* config's `pcrec` raw flag text           */
} RxtRow;

typedef struct {
    const char *path;
    RxtRow     *rows;
    size_t      nrows, rowcap;
    /* THE SEAM'S ONE NUMBER: the 1-based line of the FIRST `pattern` row,
     * which is where the head ends and run.sh starts its own per-line
     * loop. 0 means the file has no pattern block at all — a legal shape
     * (a pure library file), and DISTINCT from a failed call, which
     * returns NULL and a diagnostic instead. */
    size_t      first_pattern_line;
    Arena       arena;
} RxtSource;

/* Parses `path`. NULL on failure with `err` filled — every diagnostic
 * names the FILE, the LINE and the CONSTRUCT. Free with the call below. */
RxtSource *pcrec_rxt_source_parse(const char *path, pcrec_error *err);
void       pcrec_rxt_source_free(RxtSource *src);
/* `--list-source`: the file AS WRITTEN, one row per declaration and per
 * block, in file order, under docs/spec/table_contract.md. Caller frees. */
char      *pcrec_rxt_source_tsv(const RxtSource *src);
/* The dump's column count, so a checker asserts the header's own width
 * against the producer rather than against a literal it maintains by
 * hand (the D65 incident's lesson, table_contract.md's History). */
size_t     pcrec_rxt_source_ncols(void);

/* src/parse/syntax_dump.c — rendering the registry as text (SR-3). Both
 * renderers return a malloc'd string the caller frees; `flavours` of 0 means
 * "no filter". These are INTERNAL on purpose: the CLI and the test suite are
 * the only consumers today, and promoting one function into lib/pcrec.h later
 * is easy in a way that un-promoting it is not. */
char *pcrec_syntax_tsv(unsigned flavours);
/* [DD-11.2] `--list-definitions`, the fifth registry surface (D85,
 * docs/design/definitions_table.md §5). Walks the same rows
 * `pcrec_syntax_tsv` does, through the same rendering helpers
 * (src/parse/syntax_dump.c), so the two dumps join on `kind`/`selector`/
 * `syntax` by construction. Takes `--flavour` exactly like `pcrec_syntax_
 * tsv` (r43 K6: an unfiltered dump would print a definition for a
 * construct `--list-syntax --flavour=X` says does not exist). */
char *pcrec_definitions_tsv(unsigned flavours);
/* D65: the built-status derivation `pcrec_syntax_tsv`'s new column reads,
 * and the same function tests/registry/registry_check.c's defect assertion
 * calls directly — one derivation, two callers, so neither can drift from
 * the other (the shape SR-4's dump/doc pairing already uses). Mutates the
 * process-global enabled set TEMPORARILY (src/parse/enabled.c) to force
 * `r`'s own module open regardless of what the process's real --features
 * installed, and restores it exactly before returning — see the function's
 * own comment for why that is safe and how the restore is exact. */
PcrecBuiltStatus pcrec_construct_built_status(const RegRow *r);
/* `--list-verbs`: the Q1 name tables, which are not RegRows and so cannot
 * appear in the TSV above. Caller frees. */
char *pcrec_syntax_verbs(void);
/* [M6.6.2 wave F] `--list-families`: D71 item 3's INDEX LAYER — one line per
 * family (the rows sharing a key; a row's key is its `family` if set and its
 * own `syntax` otherwise), with `built` ANDed over the members. A SECOND dump
 * for `--list-verbs`' reason: `--list-syntax` is per-ROW and its consumers
 * depend on that (the reject table probes every row's own `syntax`), so the
 * grouping gets its own view rather than collapsing theirs. Caller frees. */
char *pcrec_syntax_families(void);

/* [CHK-2] `--list-axes` — THE OPTIMIZATION-AXIS REGISTRY'S FOURTH SURFACE
 * (docs/spec/registry.md). One row per (axis, candidate); `name` is the
 * candidate's stamp value where it has one, `deny` the `cx->opt->flags` bit
 * (or 0) that removes it from the emitter's own selection walk. Populated by
 * walking the SAME `DfaCand`-headed arrays `src/gen/emit_dfa.c`'s
 * `dfa_select` walks — never a hand-copied restatement of their names and
 * bits (docs/dev/learnings.md §3) — so a candidate added to one of those six
 * lists appears in the dump with no edit to the walker. `cap` bounds `out`;
 * returns the number written (never more than `cap`). */
typedef struct { const char *name; unsigned deny; } PcrecAxisCand;
size_t pcrec_dfa_axis_table_cands(PcrecAxisCand *out, size_t cap);      /* axis A */
size_t pcrec_dfa_axis_prefilter_cands(PcrecAxisCand *out, size_t cap);  /* axis B */
size_t pcrec_dfa_axis_view_cands(PcrecAxisCand *out, size_t cap);       /* axis C */
size_t pcrec_dfa_axis_seed_cands(PcrecAxisCand *out, size_t cap);       /* axis D */
size_t pcrec_dfa_axis_accept_cands(PcrecAxisCand *out, size_t cap);     /* axis E */
size_t pcrec_dfa_axis_direction_cands(PcrecAxisCand *out, size_t cap);  /* axis F */
size_t pcrec_dfa_axis_match_cands(PcrecAxisCand *out, size_t cap);      /* axis G */
/* `src/parse/axes_dump.c` — renders the seven DFA layer-1 axes above plus the
 * VM/engine-selection axes (bits 4-14, and the coarse `--engine=` axis) as
 * one TSV, `docs/spec/table_contract.md`'s wire format. Caller frees. */
char *pcrec_axes_tsv(void);

/* [LIM-1] `src/parse/limits_dump.c` — renders src/core/limits.def, the
 * numeric-limits table (D90), as one TSV, table_contract.md's wire format
 * (the SIXTH surface). Caller frees. */
char *pcrec_limits_tsv(void);

/* NULL when no construct matches the query. */
/* `--explain QUERY` (SR-3, rewritten at MOD-0.7). NULL when the query reaches
 * no doorway AND no row looks like it — the CLI turns that into exit 1 with
 * its own message. Otherwise the answer, and `*ndissent` (may be NULL) is how
 * many displayed rows FAILED the election/promise/attribution clauses: a
 * defect surfaced, which the CLI reports as exit 3, distinct from exit 1's
 * "your query could not be answered". See syntax_dump.c's own header for the
 * format and for what these clauses can and cannot dissent on.
 *
 * `err` (may be NULL, zeroed on entry) is the R20/MOD07-1 channel and it
 * DISAMBIGUATES THE NULL: empty `err->msg` is "no construct matches" as
 * before; a filled one is a doorway that RAISED — an enabled module port ran
 * a real parse of the query text and that parse failed. Both are exit 1 at
 * the CLI, with different sentences, because "your query could not be
 * answered" is not what happened in the second. */
char *pcrec_syntax_explain(const char *query, unsigned flavours, int *ndissent,
                           pcrec_error *err);
unsigned pcrec_flavour_by_name(const char *name);
/* MOD-0.1 (§18.2): the probe channel behind `pcrec --probe-ask` — one
 * doorway call for `construct` at ask level `want_name` ("claim" /
 * "verdict" / "result"), placed exactly as parse.c would place it, reporting
 * the REAL Ctx cursor before and after. Returns a malloc'd TSV line the
 * caller frees, or NULL when the want name is unknown or the text reaches no
 * doorway. check06 (the cursor rule) compares over this surface.
 *
 * `err` as for `pcrec_syntax_explain` above: zeroed on entry, and a filled
 * `err->msg` on a NULL return is the R20/MOD07-1 case — an enabled port
 * raised rather than the caller asking a bad question. */
char *pcrec_probe_ask(const char *want_name, const char *construct,
                      pcrec_error *err);

/* ---- stage entry points ---- */

int pcrec_hexval(int c);   /* src/parse/parse.c — the one hex-digit decode site */
Ast *pcrec_parse(Ctx *cx);                          /* src/parse/parse.c */
Ast *pcrec_parse_info(Ctx *cx, AltInfo *info);      /* PARSE-1; info may be NULL */
/* src/core/compile.c — parse-only: the running capture count's end-of-parse
 * value (§18.1; the CLI's --count-groups channel), or -1 with `err` filled
 * on the same refusal pcrec_compile would give. Internal, like the dumps. */
int pcrec_count_groups(const char *pattern, pcrec_error *err);
/* src/core/compile.c — [M4.5c] DD-8's `--emit-ir`: compile as usual but return
 * the VM program LISTING instead of the C. malloc'd, caller frees; NULL with
 * `err` filled on any refusal, including the honest one for a pattern that
 * does not compile to the VM at all. Internal, like the syntax dumps: the CLI
 * and the test suite are its only consumers. */
char *pcrec_emit_ir(const char *pattern, const pcrec_options *opt,
                    pcrec_error *err);
/* PARSE-1: the MODULE CALLBACK. Parses a nested body and stops AT its
 * terminator without consuming it — the caller consumes its own `)` and owns
 * its own unterminated-construct diagnostic. Do NOT hand a module
 * pcrec_parse_info instead: that one requires end-of-pattern and ctx_fails on
 * `)`. info may be NULL. */
Ast *pcrec_parse_body(Ctx *cx, AltInfo *info);
/* [OPT-4] `collapse` builds the COUNT-COLLAPSED language — every counted
 * repeat lowered as `X{min(m,1),}` — and is true ONLY where this machine's
 * sole customer is the VM hybrid's prefilter (docs/design/
 * prefilter_count_independence.md §3). It also RESETS `nfa->n`, so the same
 * `Nfa` can be measured exact and then rebuilt collapsed in place. */
void pcrec_build_nfa(Ctx *cx, Ast *root, Nfa *nfa,  /* src/ir/nfa.c */
                     bool reverse, bool collapse);
void nfa_wrap_unanchored(Ctx *cx, Nfa *nfa);        /* lowest-priority start self-loop */
bool nfa_has_asserts(const Nfa *nfa);
bool nfa_has_bot(const Nfa *nfa);   /* ^ present: still needs ENG_ATTEMPT */
/* [ENG-ABS] `root` and `optional` are PARAMETERS rather than a second
 * construction. `root` used to be `nfa->start` implicitly; every call site now
 * states which start state its machine is rooted at, which is the whole of
 * what makes the anchored MATCH-HERE machine a parameter of this function and
 * not a copy of it. `optional` is documented on `Dfa.optional`. */
void pcrec_build_dfa(Ctx *cx, Nfa *nfa, Dfa *dfa,   /* src/ir/dfa.c */
                     bool prune, bool reverse, int maxstates,
                     int root, bool optional);

/* [ENG-ABS] What `intern` returns to an OPTIONAL machine that has overflowed:
 * the value `DState.tr[]` already carries for "dead", so a partially built
 * optional machine is well-formed rather than corrupt on the way out. */
enum { PCREC_DFA_DEAD = -1 };
void pcrec_minimize_dfa(Ctx *cx, Dfa *dfa);         /* src/opt/minimize.c */
void pcrec_emit_dfa(Ctx *cx);                       /* src/gen/emit_dfa.c -> job->csb/hsb */

/* ---- [OPT-ALTCLS] alternation->class normalization (docs/dev/plan.md) ---- */

/* Runs immediately after parse and before EVERYTHING downstream (engine
 * selection, possessify/revdet/mrl, both machine builds, both emitters) --
 * the plan row's interaction note: post-merge/post-factor shapes must be
 * what those analyses see, not the alternation spelling. Returns the
 * (possibly rewritten) root; the original tree is never mutated in place,
 * matching select_engine.c's `discharge` hook shape, because stage 1/2 both
 * change tree SHAPE rather than annotate existing nodes. Self-gated on
 * PCREC_NO_ALTCLS_MERGE/PCREC_NO_ALTCLS_FACTOR (cx->opt->flags), so a denied
 * build's cx->job->altcls_merges/altcls_factored stay at 0 -- the same
 * "no trace" rule possessify.c's -fno-possessify follows. */
Ast *pcrec_altcls(Ctx *cx, Ast *root);               /* src/opt/altcls.c */

/* ---- [M4.5b] the VM engine (docs/design/engine_m4.md) ---- */

/* engine_m4.md §5.1: per-pattern engine selection as a PASS, run after parse
 * and before machine construction. Fills cx->job->fit, and ctx_fails with the
 * §5.6/D44.6 refusal when --engine conflicts with what the pattern needs. */
void pcrec_select_engine(Ctx *cx, Ast *root);        /* src/opt/select_engine.c */

/* ---- [ENG-BREP] possessification (docs/design/eng_brep_design.md §2) ---- */

/* The §2.2 rule as a pass: mark every A_REP for which no retreat into the loop
 * can produce a match the preferred path does not. A REWRITE, not an analysis
 * that returns a verdict (§2.8) — it does not observe that the loop needs no
 * frames, it MAKES the quantifier one that needs none, by setting Ast.u.rep.possessive
 * for src/gen/emit_vm.c to act on.
 *
 * Returns the number of quantifiers it newly marked, which is what makes it
 * MONOTONE and lets a caller drive it to a fixpoint: a second call over the
 * same tree marks nothing and returns 0.
 *
 * Runs only for a VM artifact and only when the pass is allowed — see the call
 * site in pcrec_select_engine, which owns both conditions. */
int  pcrec_possessify(Ctx *cx, Ast *root);           /* src/opt/possessify.c */

/* §2.2's "X admits a unique iteration" — (U1) one-unambiguous, (U2)
 * prefix-free, and non-nullable, decided on the body's position (Glushkov)
 * automaton — exported from possessify.c because the REVERSE-DETERMINISTIC rung
 * needs the identical predicate on the identical construction and a second
 * implementation of a rule that carries three measured refutations is the
 * worst possible place for this project to keep two sources of truth.
 *
 * `pcrec_uniq_scratch` arena-allocates the position state ONCE per pass; the
 * struct is deliberately opaque here because its only property a caller needs
 * is that it is reusable. `*why` names the failing condition
 * ("nullable-body", "ambiguous-body", "not-prefix-free", "model-error") or
 * "unique-iteration" on success. */
void *pcrec_uniq_scratch(Ctx *cx);                   /* src/opt/possessify.c */
bool  pcrec_uniq_iteration(void *scratch, const Ast *body, const char **why);

/* [M6.4.2] §2.2's verdict as a QUERY rather than as a MARK — the callable
 * verdict atomic_groups_design.md §5.3 (E7) asks for, and the whole reason the
 * free discharge could be narrowed to a shape that is buildable today.
 *
 * It runs THE SAME WALK `pcrec_possessify` runs — same FOLLOW accumulation,
 * same enclosing-loop term, same four conjuncts, the same lines of code — and
 * calls `fn(user, rep)` once for every `A_REP` whose verdict is POSITIVE,
 * WITHOUT writing `Ast.u.rep.possessive`. A second implementation of §2.2 is the one
 * thing this file must never grow (every conjunct in it is a measured
 * refutation of a simpler rule somebody believed), so the discharge asks
 * possessify rather than re-deriving anything.
 *
 * ONE PASS IS EXACT, not an approximation of the fixpoint `run_possessify`
 * drives: the fixpoint exists because `pcrec_possessify` reports how many
 * quantifiers it NEWLY marked and a caller wants that to reach zero, but the
 * verdict itself reads no `possessive` field anywhere (P9), so round two marks
 * nothing new and this survey sees exactly what the fixpoint would. */
void  pcrec_poss_survey(Ctx *cx, Ast *root,
                        void (*fn)(void *user, Ast *rep), void *user);

/* ---- [M6.4.2] module `atomic-groups`: the free discharge (design §5.3) --- */

/* Delete every `A_ATOMIC` whose cut is PROVABLY A NO-OP, splicing its body
 * back in, and return the (possibly new) root.
 *
 * THE CONDITION IS POSSESSIFY'S OWN §2.2 VERDICT, unchanged, and the reason
 * that is exactly right rather than merely convenient: the verdict's entire
 * content is "no retreat into this loop can produce a match the preferred path
 * does not", which is precisely "the cut deletes nothing". Ships for the
 * `A_ATOMIC(A_REP(X))` arm ONLY — the possessive spellings — because that is
 * the arm with evidence (0 violations over 532 positive-verdict patterns,
 * atomic_groups_measurements/out/free_discharge.txt); the plain-group `(?>X)`
 * arm is DEFERRED at zero measured cells (design §5.3's E7 ruling) and needs a
 * callable (U1)/(U2) predicate over an arbitrary subtree, which is strictly
 * more than the A_REP verdict above.
 *
 * RUN FROM THE TOP OF `pcrec_select_engine`, BEFORE the analysis loop, and NOT
 * from the `EngineAnalysis.discharge` socket — see that file for the three
 * reasons, one of which is that the socket's fixpoint never CALLS a registered
 * hook today. NOT gated by `-fno-possessify` either: the discharge is
 * semantics-preserving by its own verdict, and gating it would make an
 * optimisation flag change which ENGINE a pattern gets.
 *
 * D67 contract note 3 holds by construction: this is a DELETION, so the nodes
 * that survive are the body's own and keep their own stamps, and no new node
 * is born to inherit the discharged one's. */
Ast *pcrec_discharge_atomic(Ctx *cx, Ast *root);      /* src/opt/atomic.c */

/* Does this tree carry an A_ATOMIC — i.e. a cut that survived the discharge?
 *
 * READ AT EMISSION, and it is H3's whole predicate. The capture-erased
 * prefilter is built from the UNCUT language (src/ir/nfa.c lowers an atomic
 * body transparently, which is the only sound choice for a subset
 * construction), so the prefilter's window END is NOT an upper bound on the
 * cut match's end — MEASURED at 122 refuting cells and 114 cells of live
 * silent match loss on the emitted prefilter (design §4.3). Its span START and
 * its REJECTION stay sound, so the fix is to drop the MRL ceiling only. */
bool pcrec_has_atomic(const Ast *a);                  /* src/opt/atomic.c */

/* [M6.6.2] Does this tree carry an `A_LOOK`? `pcrec_has_atomic`'s TWIN, and
 * declared beside it because it is read in the same expression, at the same
 * point, for the same reason.
 *
 * ASKED OF THE POST-DISCHARGE TREE (design §5.6(4)). The prefilter is built
 * from the lookaround-ERASED pattern (src/ir/nfa.c lowers an A_LOOK to an
 * epsilon, the only sound choice for a subset construction), so its window END
 * is NOT an upper bound on the real match's end — the identical hazard the
 * cut has, arriving through a different door. Its span START and its REJECTION
 * stay sound (L(P) is a subset of L(erase(P)) at every position, design §5.3),
 * so the fix is again to drop the MRL ceiling only.
 *
 * FLAT, not shaped: design §5.6 names the narrower "a lookaround inside an
 * alternation" predicate and rejects it — a second analysis with no
 * independent check, against a silent match loss if it is wrong anywhere. */
bool pcrec_has_lookaround(const Ast *a);              /* src/opt/atomic.c */

/* [OPT-4] Does this tree carry an `A_REP` the count-collapse would CHANGE —
 * one with `rmin > 1 || rmax > 1` (docs/design/prefilter_count_independence.md
 * §3)? The third member of the family above, and declared beside them because
 * it is the same question asked for the same consumer: which counted repeats
 * make the prefilter's machine scale with a number the filter does not need.
 *
 * IT IS THE COLLAPSE'S OWN GUARD, SPELLED ONCE. `compile.c`'s build gate reads
 * it to decide whether rebuilding is worth an NFA, and `emit_vm.c` never asks
 * it at all — the artifact reports what was BUILT (`job->fit.prefilter_lang`),
 * not what could have been, so there is no second derivation to disagree.
 *
 * It is ASKED OF THE POST-DISCHARGE TREE like its two neighbours, and for a
 * sharper reason than symmetry: possessification rewrites `A_REP` nodes, and a
 * predicate answering about the pre-pass tree could name a repeat the builder
 * no longer sees. */
bool pcrec_has_collapsible_rep(const Ast *a);         /* src/opt/atomic.c */

/* Does any node in `a` carry `row` as its SR-8 producing stamp — i.e. did that
 * row's producer actually build something here?
 *
 * D65's built-status derivation reads this for a row that reaches NO DOORWAY
 * (RK_QUANTSUFFIX), where `doorway_route`/`doorway_call`'s `ExtResult` is not
 * available to classify on. It is the stamp itself and not a second fact, so
 * it cannot disagree with the producer; and it is what makes the derivation's
 * DEFECT verdict reachable — a row whose `syntax` does not exercise its own
 * construct parses cleanly and stamps nothing. */
bool pcrec_ast_stamped_by(const Ast *a, const RegRow *row);  /* src/opt/atomic.c */

/* ---- [ENG-BREP] the reverse-deterministic rung (engine_m4.md §2.5) ---- */

/* Mark every A_REP whose consumed run decomposes into iterations UNIQUELY and
 * RECOVERABLY FROM THE RIGHT, by setting Ast.u.rep.revbody to the body's reversed
 * AST. The emitter then owes it ONE body copy instead of `rmax` of them.
 *
 * Not monotone in possessify's sense and not a fixpoint: the verdict depends
 * only on the body's own shape and its nesting, so one walk decides every
 * quantifier. Returns how many it marked, for the census line.
 *
 * Runs only for a VM artifact and only when the rung is allowed — same call
 * site and same reasoning as pcrec_possessify. */
int  pcrec_revdet(Ctx *cx, Ast *root);               /* src/opt/revdet.c */

/* The set of bytes a node can BEGIN with, over the restricted tree the rung
 * admits (non-nullable, assertion-free), exported so that the emitted backward
 * walk's byte dispatch and the analysis's own check that the dispatch is
 * well-defined read ONE computation. `out` is a 32-byte class bitmap. */
void pcrec_revdet_first(const Ast *a, uint8_t *out);  /* src/opt/revdet.c */

/* ---- [M4.6d] MINIMUM-REMAINING-LENGTH pruning (k23_design.md §4.3) ---- */

/* The least number of subject bytes any match of `a` can consume. The VM
 * emitter threads it down its own walk as a FOLLOW-MIN accumulator and turns
 * the sum into a compile-time constant per program point: a position with
 * fewer bytes left than that constant has no accepting continuation and is
 * cut before a choice point is pushed for it.
 *
 * UNDER-ESTIMATING IS ALWAYS SAFE (it prunes less); over-estimating deletes
 * real matches, silently. src/opt/mrl.c says which cases take which direction
 * and why its switch has no live default arm. */
long long pcrec_minw(const Ast *a);                  /* src/opt/mrl.c */

/* The SATURATION ceiling every minimum-width arithmetic pins itself to. Shared
 * because the emitter's own accumulator has to hold the same ceiling the
 * analysis does — two different ceilings would let a long concatenation of
 * saturated subtrees overflow past the one that was supposed to prevent it.
 * Far above any addressable subject on purpose: a saturated bound reads as
 * "doomed", which at 2^40 remaining bytes it is.
 *
 * [LIM-1] (D90): generated earlier in this file (PCREC_PREFIX_K_MAX's own
 * limits.def include, home INTERNAL_H) — value unchanged, (1LL << 40). */

/* [M6.6.2 wave A] The MAXIMUM number of subject bytes any match of `a` can
 * consume — `pcrec_minw`'s twin, and its DIRECTION IS THE OPPOSITE ONE.
 *
 * `pcrec_minw` may UNDER-estimate for free (a bound below the truth prunes
 * less). `pcrec_maxw` may OVER-estimate for free, and under-estimating is the
 * silent-miscompile direction: its first consumer is the lookaround module's
 * FIXED-WIDTH rule (`lookaround_design.md` §2.5 — a lookbehind branch is
 * admitted only when `minw == maxw`), so a maxw below the truth admits a
 * VARIABLE-width branch as fixed and the emitted back-step steps the wrong
 * distance. Every conservative arm in src/opt/mrl.c's `pcrec_maxw` therefore
 * rounds UP, and `PCREC_W_UNBOUNDED` is where rounding up runs out.
 *
 * `maxw(a) >= minw(a)` for every node of every tree, and that is checked
 * rather than asserted: tests/mrl/maxw_check.c sweeps it over every node of
 * every pattern in the whole `.rxt` corpus. */
long long pcrec_maxw(const Ast *a);                  /* src/opt/mrl.c */

/* "This node's maximum width has no static bound" — an unbounded quantifier,
 * a backreference, or any arithmetic that ran off the top.
 *
 * IT IS DELIBERATELY THE SAME VALUE AS `PCREC_MINW_MAX`, and the reason is
 * that it must COMPOSE with `mrl_sat_add`/`mrl_sat_mul` rather than need a
 * check at every arm:
 *
 *   - `mrl_sat_add(UNBOUNDED, anything)` saturates, so unbounded ABSORBS
 *     through a concatenation, which is what "unbounded" has to do;
 *   - `mrl_sat_mul(UNBOUNDED, 0)` is 0, so an unbounded repeat of a
 *     ZERO-WIDTH body is correctly 0 (`(?:\b)*` consumes nothing however many
 *     times it runs) instead of being needlessly widened;
 *   - `mrl_sat_mul(UNBOUNDED, k>0)` saturates, so a bounded repeat of an
 *     unbounded body stays unbounded.
 *
 * The cost of sharing the value is that a SATURATED-but-finite maxw is
 * indistinguishable from a genuinely unbounded one. That is maxw's SAFE
 * direction (it reads as "no static bound", the conservative answer) and it
 * is why the sharing is written down here rather than discovered later.
 * A consumer asks `w >= PCREC_W_UNBOUNDED`, never `w == `. */
#define PCREC_W_UNBOUNDED PCREC_MINW_MAX

/* engine_m4.md §2: the backtracking VM as emitted specialized C. Emits the
 * whole artifact (prologue, ABI types, the DFA prefilter pair when the fit
 * says so, the VM itself, and the four entry points). */
/* [DD-14 wave B+C] `root` LOST ITS `const`, and the reason is one field.
 * `Ast.u.call.nonnullable` is the graph fixpoint whose RECURRENCE
 * (`vm_nullable`) is `static` to the emitter — see src/opt/callgraph.c's
 * header for why the two fixpoints split across two files — so the emitter is
 * the pass that WRITES it, and `save`/`nsave` are written there too because
 * their values are SLOT INDICES that exist nowhere else. Dropping the
 * qualifier is preferred to casting it away at the write site: a cast is a
 * claim a reader has to check, and the tree is this compile's own arena. */
void pcrec_emit_vm(Ctx *cx, Ast *root);              /* src/gen/emit_vm.c */

/* src/gen/emit_dfa.c, exported for emit_vm.c: the shared artifact-prologue
 * and entry-point emitters. `pcrec_emit_dfa_engine` emits ONE engine function
 * body (the same forward+reverse or attempt code pcrec_emit_dfa emits) under
 * a caller-chosen name and storage class, which is how the VM's hybrid gets
 * its prefilter without a second copy of that emitter (§6.1, §2.8's "reused
 * unchanged" table). */
typedef struct {
    const char *searchfn, *matchfn, *matchcapsfn, *infoname;
    char        upper[80];
} GenNames;
void pcrec_gen_names(Ctx *cx, GenNames *g);
void pcrec_emit_abi_types(StrBuf *sb);
/* [DD-13] `<PREFIX>_ENGINE`, the D46 family's UNCONDITIONAL selection fact:
 * one emitter for both engines so the two can never spell it differently
 * (src/gen/emit_dfa.c's own header on it; docs/spec/match_api.md §6.3's
 * (a)/(b) split). `engine` is "vm" or "dfa". */
void pcrec_emit_engine_stamp(StrBuf *sb, const char *upper, const char *engine,
                             const char *sel);
const char *pcrec_engine_sel_name(Ctx *cx);
/* [DD-13c] `<PREFIX>_DFA_SCAN` + `<PREFIX>_DFA_PREFILTER`, the DFA scan's own
 * two selection facts, emitted from ONE place for the TWO artifact kinds that
 * CONTAIN a DFA scan: a DFA artifact, and a VM HYBRID (`fit.prefilter`), whose
 * inlined `static <prefix>_prefilter` IS this emitter's scan. Values come from
 * the same `unanch_start`/`attempt_cand` derivations the loop is emitted from
 * (src/gen/emit_dfa.c's own header on it; docs/spec/match_api.md §6.3's (a)).
 * MUST NOT be called on a non-hybrid VM artifact: there is no DFA there, and
 * `job->engine`/`job->dfa` were never set (src/core/compile.c builds the pair
 * only when `fit.chosen == ENGM_DFA || fit.prefilter`). */
void pcrec_emit_dfa_scan_stamps(Ctx *cx, StrBuf *sb, const char *upper);
/* [DD-13c] Does this artifact CONTAIN a DFA scan? src/core/compile.c's own
 * `fit.chosen == ENGM_DFA || fit.prefilter` condition, spelled once: it is what
 * makes `job->dfa`/`job->engine` exist, so it is the guard every reader of them
 * outside the DFA emitter must ask. True on a DFA artifact and on a VM HYBRID,
 * false on a non-hybrid VM artifact. */
bool pcrec_artifact_has_dfa_scan(Ctx *cx);
void pcrec_emit_c_string_literal(StrBuf *sb, const char *s, size_t len);

/* [DD-14.FB] (D71 item 2, docs/spec/match_api.md §10.4) THE CALLER-BUFFER
 * SIZING SURFACE, as five facts the emitter that knows the run state's layout
 * hands to the two places that PUBLISH them -- the artifact's header (five
 * macros) and `rx_info` (four fields). It is a struct rather than five
 * parameters because both consumers take all of them and a positional list of
 * five integers is the shape a later edit silently transposes.
 *
 * A DFA ARTIFACT PASSES THE INERT SHAPE and the surface is still emitted:
 * spec §10.4 rules the whole surface present on every artifact, with the four
 * SIZING facts reading 0 (that engine has no resume stack to size) and the
 * alignment reading 1 (every pointer satisfies it) -- a deliberate departure
 * from §6.3's VM-only rule for capacity macros, because these five are what a
 * caller needs in order to CALL the artifact and engine selection is not the
 * caller's choice. `pcrec_bufsurface_inert()` is that shape, spelled once. */
typedef struct {
    long long resume_frames;      /* stamped DEFAULT capacity, in frames */
    long long trail_frames;       /* stamped DEFAULT capacity, in entries */
    int       resume_frame_size;  /* bytes per resume frame, THIS artifact */
    int       trail_frame_size;   /* bytes per trail entry, THIS artifact */
    int       align;              /* bytes; the alignment BOTH regions need */
} BufSurface;
BufSurface pcrec_bufsurface_inert(void);

void pcrec_emit_prologue(Ctx *cx, const GenNames *g, int ncaps,
                         const BufSurface *bs);
void pcrec_emit_dfa_engine(Ctx *cx, const char *fn, const char *storage);
/* [M5-SEAM] the per-encoding residual DEFINITIONS (src/gen/enc/); the
 * matching declarations ride pcrec_emit_prologue. */
void pcrec_emit_residual(Ctx *cx);
void pcrec_emit_info(Ctx *cx, const GenNames *g, int engine, const char *why,
                     long long budget, long long work, long long frames,
                     long long ceiling, const BufSurface *bs);
void pcrec_emit_main(Ctx *cx, const GenNames *g);

#endif /* PCREC_INTERNAL_H */
