/* src/gen/enc — the ENCODING BACKENDS ([M5-SEAM], D58; DD-12 (7)/(8)).
 *
 * DD-12 (7) forbids encoding conditionals anywhere: no "if utf do x else y"
 * in the compiler, in the emitter, or in the emitted artifact. Encodings are
 * SEALED BACKENDS, and the only "switch" is WHICH backend's text an artifact
 * embedded. This header is that seam's whole interface.
 *
 * WHAT A BACKEND IS. One `PcrecEnc` row: an id, the one spelling of its name
 * (the CLI value, the diagnostics, and any future stamp all read THIS string
 * — [SR-10]'s single-namespace rule for the half this row owns), and the two
 * blocks of RESIDUAL TEXT it contributes to every artifact compiled under it:
 * the declarations (emitted into the .h when the artifact is split, into the
 * .c when it is self-contained) and the definitions (.c only). A member whose
 * `decls` is NULL is a NAME pcrec knows and an encoding it cannot yet
 * compile; `pcrec_enc_ready()` is that test, and the refusal reads the row's
 * own `name` rather than a hand-written literal.
 *
 * WHY TEXT AND NOT A CALLBACK. The residual is emitted verbatim except for
 * the artifact's `--prefix`, so a backend is a string and a backend author
 * writes C, not emitter code. `$` is the prefix placeholder and the ONLY
 * character `pcrec_enc_emit_text` treats specially; residual text must
 * therefore contain no other `$`.
 *
 * THE THIRD-ENCODING RECIPE (DD-12 (7)'s own derailment test). Adding an
 * encoding backend is: one new `enc_<name>.c` in this directory, plus its
 * `extern` below and its row in `enc.c`'s table. Both of those are files in
 * THIS directory. Nothing in src/core, src/gen, cli/ or lib/ is touched, and
 * if a future backend ever needs one of them touched, that is the design-stop
 * signal DD-12 names rather than a patch to write. */
#ifndef PCREC_GEN_ENC_H
#define PCREC_GEN_ENC_H

#include "core/internal.h"   /* StrBuf */

/* [M6.5.2] THE SEAM'S ENTRIES ARE A TABLE, one row per residual entry, and
 * this is D58's own revisit clause being honoured: *"M5's UTF-8 backend lands
 * — the second consumer is the seam's validation event; ANY INTERFACE CHANGE
 * IT FORCES GETS RECORDED AGAINST THIS ENTRY."* The second consumer arrived
 * early (a caseless backreference compare, backrefs_design.md §4) and it
 * forces one.
 *
 * WHY THE TWO TEXT BLOBS COULD NOT SIMPLY GROW. Until now a backend was two
 * strings emitted UNCONDITIONALLY into every artifact. With three entries that
 * means every artifact — including one with no backreference in it — grows two
 * exported functions of dead code. They cannot be `static` (an unused `static`
 * fails the harness's `-Werror` generated-code build, which is why `next_pos`
 * is exported), so they would be LINKED dead weight in every artifact pcrec
 * has ever emitted. A per-entry mask is what keeps the cost where the
 * construct is.
 *
 * THE ROAD NOT TAKEN: two more string fields (`bref_decls`/`bref_defs`).
 * Simpler, and it does not generalise — lookbehind's back-step ([M6.6]) is the
 * next residual entry D58 already names, and it would need a third pair.
 *
 * `engine_callable` IS THE OTHER HALF, and it is a fact about the ENTRY rather
 * than about any artifact. DD-12 (7) forbids the matching machinery from
 * depending on the encoding, and `tests/codegen/run_codegen_tests.sh`'s
 * [M5-SEAM] check enforces it by asserting a residual name appears nowhere
 * inside a file-scope function body. That is exactly right for `next_pos` —
 * unanchoredness is the automaton's own self-loop, so there is no external
 * advance for an engine to route through, and an engine that DID route through
 * it would match identically under the byte backend and change the hot path's
 * shape under any other. It is exactly WRONG for a backreference compare,
 * which has no automaton representation whatsoever: forbidding the call
 * forbids the construct. So the entry declares which it is, the check reads
 * the declaration, and the population it applies to is the one the FIXTURE
 * TABLE names rather than one derived from the artifact under test. */
typedef struct {
    unsigned    id;              /* PCREC_ENCE_* below */
    bool        engine_callable; /* may an engine body call it? */
    const char *decls;           /* residual declarations, `$` = prefix */
    const char *defs;            /* residual definitions, `$` = prefix */
} PcrecEncEntry;

/* The entry ids, which are also the bits of the per-artifact MASK. */
enum {
    /* Always in the mask: docs/spec/match_api.md §3.1 promises it
     * unconditionally and tests/codegen's K27 fixture calls it directly. */
    PCREC_ENCE_NEXT_POS       = 1u << 0,
    /* In the mask only when the artifact contains a backreference of that
     * caselessness — two entries rather than one with a flag, because D18/D23
     * say an option compiles away and D23 MEASURED a runtime fold indirection
     * costing 26% on a pattern with no letters in it. */
    PCREC_ENCE_BREF           = 1u << 1,
    PCREC_ENCE_BREF_CASELESS  = 1u << 2,
    /* [M6.6.2 wave D] In the mask only when the artifact contains a
     * LOOKBEHIND. D58 named this entry before it existed — see the "ROAD NOT
     * TAKEN" paragraph above, which predicted it by name as the reason the
     * entries table is a table — and lookaround_design.md §4.3 makes the
     * prediction falsifiable: ONE enumerator, ONE row in `entries_byte[]`,
     * and the `A_LOOK` arm ORs the bit when `u.look.behind`. No field is
     * added to `PcrecEncEntry`, no signature changes, `pcrec_enc_ready` is
     * untouched, both emit functions are untouched, and the third-encoding
     * recipe in this header is unchanged. */
    PCREC_ENCE_BACK_STEP      = 1u << 3
};

typedef struct {
    int         id;      /* PCREC_ENC_* (lib/pcrec.h) */
    const char *name;    /* the ONE spelling: CLI value and diagnostics */
    /* [M5.0] THE COMPLEMENT UNIVERSE — the greatest code point this encoding
     * has, and the ONE question that reads it is "what does `[^x]` mean here"
     * (docs/design/utf8_design.md §2.7.1/§2.7.2, D58's addendum).
     *
     * IT IS NOT A CODE-UNIT WIDTH AND NOT A VALIDITY PREDICATE. `byte` reads
     * `0xFF` because a byte encoding's repertoire is exactly `0..0xFF`, so
     * `negate(S) = [0, 0xFF] \ S` is the SAME FUNCTION as the `~bits[i]` loop
     * it replaces — which is what makes stage 1's byte-identity gate an
     * argument rather than a hope. `utf8` reads `0x10FFFF`.
     *
     * IT IS THIS FIELD, AND NOT THE ENTRIES TABLE, THAT MAKES [M5.0] A D58
     * SEAM EVENT. The design's §5 opened "the seam needs no interface change"
     * and r54 E2 retracted it: the entries table above is untouched by the
     * second backend (four residual bodies under their existing signatures),
     * and `PcrecEnc` itself gains this one scalar. Recorded rather than
     * quietly added, because D58's revisit clause asks for exactly that.
     *
     * A FUTURE CODEPAGE BACKEND WILL NOT FIT IT (§5.7.3, R-ASKS-3(b)): a
     * codepage's repertoire is 256 code points SCATTERED across Unicode, so no
     * maximum describes it and the field becomes the contiguous-repertoire
     * special case of "what set does a complement complement within". That is
     * D77-recorded with its trigger, not built for. */
    unsigned    max_cp;
    /* The backend's entries, terminated by a row with `decls == NULL`. An
     * EMPTY table (or none) is a NAME pcrec knows and an encoding it cannot
     * yet compile; `pcrec_enc_ready()` is that test, and the refusal reads the
     * row's own `name` rather than a hand-written literal. */
    const PcrecEncEntry *entries;
    /* [K49] THE UNANCHORED RETRY ADVANCE — the statements an emitted engine
     * runs to move a failed attempt's START position to the next position the
     * search is allowed to try.
     *
     * IT IS A THIRD KIND OF CONTRIBUTION, and saying why is the point. The
     * entries above are FUNCTIONS a caller (or, where `engine_callable`, an
     * engine) calls. This is INLINE TEXT spliced into an engine body, and it
     * has to be, for two independent reasons that happen to agree:
     *
     *   - `next_pos` computes exactly this position and carries
     *     `engine_callable = false`. DD-12 (7), the [M5-SEAM] codegen check
     *     and sabotage row S68 all forbid an engine body calling it.
     *   - Even if they did not, a call would MOVE THE BYTE ARTIFACT. The byte
     *     advance is `pos++` and must stay `pos++`, byte for byte, or the
     *     identity gate is a re-pin rather than a proof.
     *
     * WHAT K49 REFUTED, and why the field exists at all. `docs/design/
     * utf8_design.md` §5.5 ASSERTED that a byte-granular retry "cannot produce
     * a wrong answer" under UTF-8 because a mid-character start "has no path".
     * That holds for a POSITIVE pattern only, and §2.6.1 of the same document
     * had already recorded the inversion: a NEGATIVE assertion succeeds
     * exactly where a body has no path, so a mid-character retry answers, and
     * answers with a reported position inside a character. K49's witness is
     * `(?<!.)` at a boundary startpos over `CE B1 CE B2` reporting `(3,3)`.
     *
     * THE RULE THIS TEXT SPELLS, one backend at a time: an unanchored search
     * may only ever try LATER CHARACTER BOUNDARIES of its own encoding as
     * match starts. Under `byte` every position is a boundary, so the step is
     * `pos++` and this backend contributes what the emitter used to hard-code.
     *
     * SUBSTITUTION. Three tokens, and `$` is NOT one of them (an advance names
     * no artifact symbol): `@P` the position variable, `@S` the subject
     * variable, `@N` the subject-length variable. A line's own leading spaces
     * are RELATIVE indentation; `pcrec_enc_advance` prefixes every line with
     * the caller's base indent, so one backend text serves call sites at
     * different depths.
     *
     * IT DUPLICATES `next_pos`'s RULE IN A SECOND SPELLING, deliberately and
     * with the same guard the fold already has. `enc_byte.c`'s caseless
     * compare and `cls_casefold` are two spellings of one fold, tied by
     * `tests/backrefs/fold_agreement_check.c`; this text and this backend's
     * `next_pos` are two spellings of one boundary rule, tied by
     * `tests/codegen/run_encoding_checks.sh`'s advance-agreement check, which
     * reads BOTH out of an artifact pcrec actually emitted. A backend that
     * changes one and not the other fails there rather than in a corpus cell
     * nobody wrote. */
    const char *advance;
    /* [K50] WHERE A MATCH MAY BEGIN — the same boundary rule as `advance` and
     * `next_pos`, asked as a PREDICATE instead of as a step, because the two
     * consumers that need it cannot use a step.
     *
     * K49 fixed the VM's retry loop by asking the encoding how to MOVE a
     * failed attempt's start. K50 is the other half of the same rule and the
     * other two "try the next start" mechanisms:
     *
     *   - `src/ir/nfa.c`'s `nfa_wrap_unanchored` self-loop, which is not a
     *     loop the emitter can see at all — it is an AUTOMATON, and the
     *     positions it "generates" are wherever its lowest-priority split
     *     enters the pattern. Gating that split needs the boundary rule as a
     *     BYTE SET, evaluated inside the subset construction.
     *   - `src/gen/emit_dfa.c`'s `ENG_ATTEMPT` start loop, which cannot take
     *     the `advance` text without moving every byte artifact: its step is
     *     the `start++` of a `for` header, and replacing a header increment
     *     with a trailing statement is exactly the emitted-scaffolding move
     *     D76 makes an abi event. A `continue` guard at the top of the body
     *     is additive — a backend with no restriction contributes nothing and
     *     the byte artifact does not move.
     *
     * TWO FIELDS FOR ONE RULE, which is this seam's existing bargain rather
     * than a new one. `advance` and `next_pos` are already two spellings of
     * the boundary rule (see `advance`'s own comment), tied by
     * `tests/codegen/run_encoding_checks.sh`'s advance-agreement check
     * because a backend that changes one and not the other must fail at a
     * check and not in a corpus cell. These two join that arrangement: the
     * check now reads FOUR spellings out of one emitted artifact and requires
     * all four to agree over an exhaustive byte alphabet.
     *
     * WHY NOT DERIVE THE TEXT FROM THE SET. The emitter does own a general
     * class-test renderer (`vm_cls_test`), and for utf8's start set — every
     * byte except the 64 continuation bytes — it selects the BITMAP shape,
     * because the set is the complement of a range and `VmClsShape` has no
     * complement-of-range member. That would put a 32-byte table and a
     * shift-and-mask in an entry guard whose whole promise is O(1) and free,
     * and adding the missing shape moves bytes on every artifact that has a
     * class of that form ([FORM-CHAR] territory, its own gate-bearing
     * change). Measured, not assumed — and recorded here so the next reader
     * does not re-derive it.
     *
     * BOTH ARE OPTIONAL AND `NULL` MEANS "NO RESTRICTION": every position of
     * every subject is a character boundary. That is `byte`'s answer, it is
     * what makes the IR build no gate node and the emitters emit no guard,
     * and it is therefore what keeps every byte artifact byte-identical
     * across this change BY CONSTRUCTION rather than by a comparison.
     *
     * `start_cls` is a 32-byte class in the same 256-bit representation the
     * AST, the NFA and the DFA all use, so nothing has to agree with a second
     * encoding of "which bytes".
     *
     * THE DISJOINTNESS THIS SET OWES, checked and not assumed. The subset
     * construction carries the boundary property on its CLASS AXIS
     * (`UPC_NOSTART`, core/internal.h), which is a PARTITION — so a byte that
     * is not a character start must be neither a word byte nor a newline. UTF-8
     * satisfies this (continuation bytes are 0x80..0xBF; both other sets are
     * ASCII). A future backend that does not is refused at
     * `pcrec_enc_start_cls_ok()` with an internal error naming this comment,
     * rather than silently classifying a non-start byte as a word byte and
     * re-opening K50. */
    const unsigned char *start_cls;
    /* The same predicate as C text, true when `@P` is a position a match may
     * begin at. Substitution is `advance`'s, minus the indentation rule: this
     * is ONE EXPRESSION, spliced into an `if`, never a statement list. */
    const char *start_guard;
} PcrecEnc;

/* The registry. Lookup is total over the namespace and returns NULL for a
 * value that is not a member at all. */
const PcrecEnc *pcrec_enc_by_id(int id);
const PcrecEnc *pcrec_enc_by_name(const char *name);
/* Render every member's name, comma-separated, into a CALLER-owned buffer —
 * no static scratch, because pcrec_compile() is called concurrently (TS-3)
 * and a lazily-filled shared buffer would be a data race in a diagnostic. */
void pcrec_enc_names(char *buf, size_t cap);

/* True when this member has a backend to embed. [M6.5.2]: "has a non-empty
 * entries array", where it used to read `decls != NULL` — the field the
 * entries table removed. R32 E11 found this: the readiness predicate is a
 * THIRD site the interface change touches, not the two emit functions alone,
 * and the `-e utf8` refusal path reads it. */
static inline int pcrec_enc_ready(const PcrecEnc *e)
{
    return e && e->entries && e->entries[0].decls;
}

/* Emit the declarations / definitions of every entry the artifact needs.
 * `mask` is an OR of PCREC_ENCE_*; an entry not in it contributes nothing, so
 * an artifact with no backreference is byte-identical to what it was before
 * the second and third entries existed. */
void pcrec_enc_emit_decls(StrBuf *sb, const PcrecEnc *e, unsigned mask,
                          const char *prefix);
void pcrec_enc_emit_defs(StrBuf *sb, const PcrecEnc *e, unsigned mask,
                         const char *prefix);
/* Is this entry callable from an engine body? Answered from the BACKEND's own
 * row, so a future backend's entry declares its own status rather than
 * inheriting one from a list somewhere else. False for an id no backend
 * carries. */
bool pcrec_enc_entry_engine_callable(const PcrecEnc *e, unsigned id);

/* Copy `text` into `sb`, replacing every `$` with `prefix`. */
void pcrec_enc_emit_text(StrBuf *sb, const char *text, const char *prefix);

/* [K49] Render this backend's `advance` text into a CALLER-owned buffer, with
 * `@P`/`@S`/`@N` replaced by the three variable names and every line prefixed
 * by `indent`. A caller-owned buffer for `pcrec_enc_names`' reason (TS-3:
 * `pcrec_compile()` is called concurrently, so no static scratch) and because
 * the one call site splices the result into an `sb_printf` beside its
 * siblings. Truncation is not silently tolerated: the function returns false
 * when the text did not fit, and the caller raises an internal error rather
 * than emitting a half-written advance. */
bool pcrec_enc_advance(const PcrecEnc *e, char *buf, size_t cap,
                       const char *indent, const char *posvar,
                       const char *subjvar, const char *lenvar);

/* [K50] Render this backend's `start_guard` EXPRESSION into a caller-owned
 * buffer, with `@P`/`@S`/`@N` replaced. Returns false when the backend has no
 * restriction (`start_guard == NULL`) — which is not an error and is the
 * common case: the caller emits nothing. Truncation IS an error and is
 * reported the same way `pcrec_enc_advance` reports it, through
 * `*truncated`, so the two outcomes a `false` covers stay distinguishable. */
bool pcrec_enc_start_guard(const PcrecEnc *e, char *buf, size_t cap,
                           const char *posvar, const char *subjvar,
                           const char *lenvar, bool *truncated);

/* [K50] The disjointness `start_cls` owes the DFA's class axis (see the
 * field's comment): a byte that is not a character start must be neither a
 * word byte nor a newline, because `UPC_NOSTART` is a member of a PARTITION.
 * True when the backend has no restriction at all. */
bool pcrec_enc_start_cls_ok(const PcrecEnc *e);

/* The backends themselves, one file each. */
extern const PcrecEnc pcrec_enc_backend_byte;   /* enc_byte.c */
extern const PcrecEnc pcrec_enc_backend_utf8;   /* enc_utf8.c, [M5.0] stage 2 */

#endif /* PCREC_GEN_ENC_H */
