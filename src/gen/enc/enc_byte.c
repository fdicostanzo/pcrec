/* The BYTE encoding backend ([M5-SEAM], D58; PCREC_ENC_BYTE).
 *
 * One byte is one character. Every residual entry below is therefore the
 * identity shape, which is exactly what makes this backend the seam's
 * bring-up member: it embeds the same entry points a UTF-8 backend will
 * embed, so a caller's loop is written once and compiles unchanged when the
 * pattern is later compiled for another encoding.
 *
 * This file is TEXT, not emitter code (see enc.h): `$` stands for the
 * artifact's own --prefix and is the only character substituted. Keep the
 * emitted text ASCII-only, like every other string this compiler emits — the
 * artifact is source someone else's toolchain compiles. */
#include "gen/enc/enc.h"

/* The declaration block: emitted into the .h of a split artifact, and into
 * the .c of a self-contained one — the same placement the four entry-point
 * declarations get, because a residual entry IS a caller-facing entry point.
 *
 * The contract comment lives HERE rather than in the emitter, so that adding
 * a residual entry to a future backend cannot land a declaration whose
 * contract nobody wrote. */
static const char decls_byte[] =
"/* $_next_pos -- the ENCODING RESIDUAL entry (pcrec DD-12/D58).\n"
" *\n"
" * Returns the smallest position STRICTLY GREATER than pos that is a\n"
" * CHARACTER BOUNDARY of this artifact's encoding, counting every position\n"
" * >= n as a boundary. So the result is in (pos, n] whenever pos < n, and is\n"
" * pos + 1 whenever pos >= n -- which is what lets a find-all loop advance\n"
" * past a zero-length match and still terminate (see pcrec's\n"
" * docs/spec/match_api.md S3.1, which writes that loop out).\n"
" *\n"
" * This entry is the ONE place an artifact's byte-vs-character distinction\n"
" * lives. It reads s only at offsets in [pos, n), so the (s == NULL, n == 0)\n"
" * subject $_search accepts is legal here too, and it is never called from\n"
" * this artifact's own engine: it is caller-facing residue, not hot-path\n"
" * code.\n"
" *\n"
" * THIS artifact was compiled for the `byte` encoding, where one byte is one\n"
" * character. An artifact compiled for another encoding exports this same\n"
" * entry with that encoding's body and no caller loop changes. */\n"
"size_t $_next_pos(const unsigned char *s, size_t n, size_t pos);\n";

/* The definition block: .c only. `(void)s; (void)n;` because generated code
 * is built -Wall -Wextra -Werror and this backend genuinely reads neither —
 * not dereferencing s is a REQUIREMENT here, not an accident of the identity
 * body: the search entry's own contract admits s == NULL when n == 0. */
static const char defs_byte[] =
"/* byte encoding: one byte is one character, so the next boundary after pos\n"
" * is pos + 1 and the subject is never read. */\n"
"size_t $_next_pos(const unsigned char *s, size_t n, size_t pos)\n"
"{\n"
"    (void)s; (void)n;\n"
"    return pos + 1;\n"
"}\n";

/* ---- entry 2 and 3: the BACKREFERENCE COMPARE ([M6.5.2], D58 scope item 3)
 *
 * A backreference compares SUBJECT TEXT against SUBJECT TEXT. Every other
 * construct pcrec compiles is a 256-bit bitmap or a position predicate, which
 * is why caselessness folds away at parse time (D23) — there is no bitmap to
 * widen here, because the operand is text nobody has seen at compile time. So
 * the fold has to happen at MATCH time, in the one place an encoding is
 * allowed to differ: this residual.
 *
 * TWO ENTRIES, NOT ONE WITH A FLAG. D18/D23's rule is that an option compiles
 * away — "the generated code has no flag, no branch and no tolower()" — and
 * D23 MEASURED the alternative (a runtime fold indirection) costing 26% on a
 * pattern containing no letters at all. The emitter picks the entry at emit
 * time from `Ast.u.bref.caseless`, so the caseless artifact pays for the fold and the
 * case-sensitive one pays nothing.
 *
 * THE RETURN IS A LENGTH, AND THE SIGN CARRIES A SECOND FACT. Under this
 * backend the compare cannot change length, so `took` is always
 * `ref_end - ref_start` on success — but the signature is designed for the
 * backend that does not exist yet, where it is NOT: `(?i)^(ss)\1$` on
 * "ss\xdf" is no match in an 8-bit build and a UTF-8 build has to answer the
 * sharp-s family differently, with one captured character folding to two and
 * the consumed length no longer equalling the captured one. Returning a length
 * is what lets that backend give a different answer WITHOUT THE SHARED EMITTER
 * CHANGING A CHARACTER — it never computes a length, it only adds the one it
 * is given. That is DD-12 (7) working as designed rather than being worked
 * around.
 *
 * On FAILURE the value is negative and `-(r) - 1` is the number of subject
 * bytes that DID compare equal. That is not decoration: `(a*)\1` over a long
 * subject fails the compare after O(n) byte comparisons, and those are work
 * the fail label never sees — the exact definition of a WORK UNIT (D47's
 * second addendum). A bare `-1` sentinel could not carry the number, which is
 * R32 E4: the first draft recommended charging the compared prefix and its own
 * signature could not express it. `-(r) - 1` rather than `-r` so that a
 * zero-length prefix is representable, keeping the ordinary "no match, nothing
 * compared" case at -1.
 *
 * THE FOLD IS SPELLED ARITHMETICALLY AND IS TIED TO pcrec's OWN, over all
 * 65,536 byte pairs, by tests/backrefs/fold_agreement_check.c against
 * `pcrec_ascii_fold` (src/core/fold.c) — which is also what `cls_casefold`
 * derives its class widening from. Two spellings of one fact with a MECHANISM
 * between them, not a comment (R32 E8; sabotage row S116). A `tolower()`
 * here would be a DEFECT rather than a shortcut: it is locale-dependent at the
 * CALLER's run time, in a locale pcrec does not control, and an artifact whose
 * answers change with `setlocale` is not the self-contained matcher APPROACH
 * promises.
 *
 * ENGINE-CALLABLE, unlike `next_pos`, and the seam's check reads that off the
 * row rather than from a list of its own — see `engine_callable` in enc.h. */
static const char decls_bref[] =
"/* $_bref_match -- the ENCODING RESIDUAL entry for a CASE-SENSITIVE\n"
" * backreference compare (pcrec DD-12/D58).\n"
" *\n"
" * PRECONDITION: ref_start <= ref_end <= n. The caller passes a PUBLISHED\n"
" * capture pair, and a published pair is ordered BY CONSTRUCTION -- the start\n"
" * was recorded before the group's body ran and the end after it.\n"
" *\n"
" * RETURNS, and the sign carries two different facts:\n"
" *     >= 0   the number of SUBJECT bytes consumed at `at`. This need not\n"
" *            equal ref_end - ref_start: under an encoding whose case\n"
" *            folding is not length-preserving it may differ, which is why\n"
" *            this entry returns a length rather than a bool.\n"
" *     <  0   no match, and -(result) - 1 is the number of subject bytes\n"
" *            that DID compare equal before the mismatch (0 when the very\n"
" *            first unit differs, or when fewer than the needed bytes\n"
" *            remain). That prefix is the WORK the compare actually did and\n"
" *            is what the caller charges against its work budget.\n"
" *\n"
" * Reads s only at offsets in [ref_start, ref_end) and [at, n).\n"
" *\n"
" * THIS artifact was compiled for the `byte` encoding, where one byte is one\n"
" * character and the compare is length-preserving. An artifact compiled for\n"
" * another encoding exports this same entry with that encoding's body. */\n"
"ptrdiff_t $_bref_match(const unsigned char *s, size_t n,\n"
"                       size_t ref_start, size_t ref_end, size_t at);\n";

static const char defs_bref[] =
"/* byte encoding: one byte is one character, so the compare is a memcmp with\n"
" * a prefix count. */\n"
"ptrdiff_t $_bref_match(const unsigned char *s, size_t n,\n"
"                       size_t ref_start, size_t ref_end, size_t at)\n"
"{\n"
"    size_t need = ref_end - ref_start;\n"
"    size_t i;\n"
"    for (i = 0; i < need; i++) {\n"
"        if (at + i >= n || s[at + i] != s[ref_start + i])\n"
"            return -(ptrdiff_t)i - 1;\n"
"    }\n"
"    return (ptrdiff_t)need;\n"
"}\n";

static const char decls_bref_ci[] =
"/* $_bref_match_caseless -- the ENCODING RESIDUAL entry for a CASELESS\n"
" * backreference compare (pcrec DD-12/D58): $_bref_match, folding case.\n"
" *\n"
" * Same contract, same return protocol. THIS artifact folds the 52 ASCII\n"
" * letters and nothing else, which is what an 8-bit non-UTF match does: in\n"
" * the C locale bytes >= 0x80 have no case, so folding them would be a guess\n"
" * about a locale the caller owns and pcrec does not. */\n"
"ptrdiff_t $_bref_match_caseless(const unsigned char *s, size_t n,\n"
"                                size_t ref_start, size_t ref_end, size_t at);\n";

static const char defs_bref_ci[] =
"/* The fold is spelled arithmetically and covers exactly A-Z <-> a-z. No\n"
" * tolower(): that is locale-dependent at YOUR run time, and this matcher's\n"
" * answers must not change with setlocale(). */\n"
"ptrdiff_t $_bref_match_caseless(const unsigned char *s, size_t n,\n"
"                                size_t ref_start, size_t ref_end, size_t at)\n"
"{\n"
"    size_t need = ref_end - ref_start;\n"
"    size_t i;\n"
"    for (i = 0; i < need; i++) {\n"
"        unsigned char x, y;\n"
"        if (at + i >= n) return -(ptrdiff_t)i - 1;\n"
"        x = s[at + i];\n"
"        y = s[ref_start + i];\n"
"        if (x >= 'A' && x <= 'Z') x = (unsigned char)(x + 32);\n"
"        if (y >= 'A' && y <= 'Z') y = (unsigned char)(y + 32);\n"
"        if (x != y) return -(ptrdiff_t)i - 1;\n"
"    }\n"
"    return (ptrdiff_t)need;\n"
"}\n";

/* ---- entry 4: the LOOKBEHIND BACK-STEP ([M6.6.2] wave D, D58 scope item 3;
 * lookaround_design.md §4)
 *
 * A lookbehind runs its body FORWARD from a position `k` characters before
 * the assertion's entry (§3.4/§3.5: pcrec's reverse machine is a DFA over the
 * capture-erased pattern and cannot carry a body with captures, backrefs or
 * nested lookaround in it). "`k` characters before" is the ONE step in that
 * shape whose answer depends on the encoding, so it is the one that lives
 * here. The [M6.6] plan row states the rule in its own text: *a seam entry,
 * never raw `pos - k` byte arithmetic in shared emitter code* — which is
 * correct today and silently wrong under a UTF-8 backend. Sabotage row S133
 * inlines it, and the fixture-declared per-site count in tests/codegen's
 * [M5-SEAM] check is its ONLY possible detector, because inlining changes no
 * answer under THIS backend.
 *
 * THE RETURN PROTOCOL DIVERGES FROM ENTRY 2's, DELIBERATELY. `$_bref_match`
 * returns a signed length whose sign carries a second fact — the compared
 * prefix, which the caller charges. A back-step's failure carries no second
 * fact: "fewer than k characters precede pos" is one bit, and the WORK the
 * entry did is `k`, which the CALLER ALREADY KNOWS AT COMPILE TIME and
 * charges with a literal (§3.7). A sentinel is therefore the honest encoding,
 * and `(size_t)-1` cannot collide with a legal position, because a legal
 * position is <= n and a subject of SIZE_MAX bytes is not representable.
 *
 * WHY `s` AND `n` ARE PARAMETERS when this backend ignores both and the entry
 * reads only below `pos`: a UTF-8 backend walking back over continuation
 * bytes must reject a MALFORMED sequence, which is a failure mode the byte
 * backend cannot have and needs the subject's bounds to detect. Adding a
 * parameter later is an ABI break the seam exists to avoid. The
 * unused-parameter cast is `$_next_pos`'s own, for `$_next_pos`'s own reason.
 *
 * ENGINE-CALLABLE, like the two compares and unlike `next_pos`: a back-step
 * has no automaton representation whatsoever, so forbidding the call from an
 * engine body would forbid the construct. */
static const char decls_back_step[] =
"/* $_back_step -- the ENCODING RESIDUAL entry for a LOOKBEHIND BACK-STEP\n"
" * (pcrec DD-12/D58).\n"
" *\n"
" * Returns the position exactly `k` CHARACTERS before `pos`, or\n"
" * $_BACK_STEP_NONE when fewer than k characters precede pos.\n"
" *\n"
" * Reads s only at offsets in [0, pos), so the (s == NULL, n == 0) subject\n"
" * $_search accepts is legal here too.\n"
" *\n"
" * THIS artifact was compiled for the `byte` encoding, where one byte is one\n"
" * character, so the answer is pos - k and the subject is never read. An\n"
" * artifact compiled for another encoding exports this same entry with that\n"
" * encoding's body and no engine code changes. */\n"
"size_t $_back_step(const unsigned char *s, size_t n, size_t pos, size_t k);\n"
"#define $_BACK_STEP_NONE ((size_t)-1)\n";

static const char defs_back_step[] =
"/* byte encoding: one byte is one character, so k characters before pos is\n"
" * pos - k and the subject is never read. */\n"
"size_t $_back_step(const unsigned char *s, size_t n, size_t pos, size_t k)\n"
"{\n"
"    (void)s; (void)n;\n"
"    return k > pos ? $_BACK_STEP_NONE : pos - k;\n"
"}\n";

static const PcrecEncEntry entries_byte[] = {
    { PCREC_ENCE_NEXT_POS,      false, decls_byte,    defs_byte    },
    { PCREC_ENCE_BREF,          true,  decls_bref,    defs_bref    },
    { PCREC_ENCE_BREF_CASELESS, true,  decls_bref_ci, defs_bref_ci },
    { PCREC_ENCE_BACK_STEP,     true,  decls_back_step, defs_back_step },
    { 0, false, NULL, NULL }
};

/* [K49] THE UNANCHORED RETRY ADVANCE (enc.h's `advance` field). One byte is
 * one character here, so EVERY position is a character boundary and the next
 * one after `pos` is `pos + 1` — which is the text the emitter hard-coded
 * before this field existed, reproduced here character for character. That is
 * the whole of this backend's stake in K49: the byte artifact does not move.
 *
 * No comment rides into the artifact. A `byte` artifact's advance is the
 * obvious one, and a comment explaining why it is obvious would be new
 * emitted scaffolding on the path D76's identity gate pins. */
static const char advance_byte[] =
"@P++;\n";

/* [K50] WHERE A MATCH MAY BEGIN. Under this backend one byte is one
 * character, so EVERY position is a character boundary and there is no
 * restriction to express: both fields are NULL.
 *
 * That is not a stub. `NULL` is the value both consumers read as "contribute
 * nothing" — `nfa_wrap_unanchored` builds the pre-K50 two-state wrap with no
 * gate node, and the emitters emit no guard text — so every byte artifact
 * that existed before K50 is byte-identical to the one this compiler emits
 * now, and the identity gate proves it rather than the comment claiming it.
 * A backend that wrote out the tautology instead (`start_cls` = all 256 bits,
 * `start_guard` = "1") would be honest and would move every artifact in the
 * tree for nothing, which is what enc.h's field comment means by NULL being
 * the answer rather than a default. */

const PcrecEnc pcrec_enc_backend_byte = {
    /* [M5.0] `max_cp` is `0xFF`: this backend's repertoire IS the byte range,
     * so complementing within it is the `~bits[i]` loop the parser used to
     * write by hand (enc.h's field comment, utf8_design.md §2.7.1). */
    PCREC_ENC_BYTE, "byte", 0xFFu, entries_byte, advance_byte,
    NULL, NULL   /* [K50] start_cls / start_guard: every position is a start */
};
