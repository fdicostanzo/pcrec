/* The UTF-8 encoding backend ([M5.0] stage 2; PCREC_ENC_UTF8).
 *
 * The seam's SECOND backend, and therefore the third-encoding recipe's first
 * real test (enc.h's header; D58's revisit clause): one new file HERE, one
 * `extern` in enc.h, one row in enc.c's table — nothing in src/core, src/gen
 * outside this directory, cli/ or lib/ is touched by this backend existing.
 *
 * A character is ONE TO FOUR BYTES here, so unlike enc_byte.c none of these
 * bodies is the identity — and the contract comments each declaration block
 * carries are the byte backend's, verbatim where the contract is unchanged,
 * because the whole point of the seam is that a caller's loop compiles
 * against either backend's text without an edit.
 *
 * WELL-FORMEDNESS: the design's ruling (utf8_design.md §2.6, ASK 1 RULED
 * 2026-09-04) is that an ill-formed byte sequence MATCHES NOTHING — no
 * validation pass, no error return. The forward automaton delivers that by
 * construction (an ill-formed sequence has no path, §2.3); the two entries
 * here that walk bytes themselves (`next_pos`, `back_step`) deliver their own
 * halves of it, and `back_step`'s is the subtle one — see its block.
 *
 * This file is TEXT, not emitter code (see enc.h): `$` stands for the
 * artifact's own --prefix and is the only character substituted. Keep the
 * emitted text ASCII-only — the artifact is source someone else's toolchain
 * compiles. */
#include "gen/enc/enc.h"

/* ---- entry 1: next_pos -------------------------------------------------- */

static const char u8_decls_next_pos[] =
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
" * THIS artifact was compiled for the `utf8` encoding: a boundary is any\n"
" * position not holding a continuation byte (0x80-0xBF). On ill-formed\n"
" * input every non-continuation byte still counts as a boundary, which is\n"
" * the self-synchronizing reading and never loops or reads out of range. */\n"
"size_t $_next_pos(const unsigned char *s, size_t n, size_t pos);\n";

static const char u8_defs_next_pos[] =
"/* utf8 encoding: skip forward over continuation bytes. A well-formed\n"
" * character's continuations are at most 3, but the loop is bounded by n\n"
" * rather than by 4 so that ill-formed input degrades to \"next\n"
" * non-continuation byte\" instead of to a mid-garbage position. */\n"
"size_t $_next_pos(const unsigned char *s, size_t n, size_t pos)\n"
"{\n"
"    size_t i = pos + 1;\n"
"    while (i < n && (s[i] & 0xC0) == 0x80) i++;\n"
"    return i;\n"
"}\n";

/* ---- entries 2 and 3: the backreference compares ------------------------
 *
 * CASE-SENSITIVE: a plain byte compare. UTF-8 is a prefix code and injective,
 * so equal code-point sequences and equal byte sequences are the same fact —
 * utf8_design.md §5.3 calls this [FORM-CHAR] object (3) `utf8-exact`, and the
 * body below is enc_byte.c's LITERALLY UNCHANGED, which is that section's own
 * claim made checkable (diff the two strings).
 *
 * CASELESS: the fold this artifact's classes were widened by is pcrec's
 * ASCII fold and nothing else — the non-ASCII simple-fold closure is [M5.0]
 * stage 4's, landing with the vendored CaseFolding.txt, and a compare that
 * folded MORE than the classes do would make `(?i)(k)\1` and `(?i)[k]\x{212A}`
 * disagree about what caselessness means inside one artifact. An ASCII fold
 * is 1:1, single-byte and never touches a lead or continuation byte, so the
 * per-character walk and the per-byte walk are the same function here; the
 * byte-wise spelling below is that fact, not a shortcut. Stage 4 replaces
 * this body with the table-driven per-character walk (design §4.6) and the
 * LENGTH-return protocol is what lets it do so without the shared emitter
 * changing a character: `^(k)\1$` on "k" + U+212A measures MATCH(0,4) on
 * 10.46 — one byte captured, three consumed — which is the cell that
 * vindicated the protocol (design §5.3). */

static const char u8_decls_bref[] =
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
" * THIS artifact was compiled for the `utf8` encoding. UTF-8 is a prefix\n"
" * code, so equal byte sequences and equal character sequences are one\n"
" * fact and the exact compare is byte-wise. */\n"
"ptrdiff_t $_bref_match(const unsigned char *s, size_t n,\n"
"                       size_t ref_start, size_t ref_end, size_t at);\n";

static const char u8_defs_bref[] =
"/* utf8 encoding: the exact compare is a byte compare (UTF-8 is a prefix\n"
" * code -- equal characters and equal bytes are the same fact). */\n"
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

static const char u8_decls_bref_ci[] =
"/* $_bref_match_caseless -- the ENCODING RESIDUAL entry for a CASELESS\n"
" * backreference compare (pcrec DD-12/D58): $_bref_match, folding case.\n"
" *\n"
" * Same contract, same return protocol. THIS artifact folds the 52 ASCII\n"
" * letters and nothing else -- the same fold its character classes were\n"
" * widened by, so one artifact carries one definition of caselessness.\n"
" * (pcrec's non-ASCII simple fold is a later milestone stage; an ASCII\n"
" * fold is 1:1 and single-byte, so the per-character walk and this\n"
" * per-byte one are the same function.) */\n"
"ptrdiff_t $_bref_match_caseless(const unsigned char *s, size_t n,\n"
"                                size_t ref_start, size_t ref_end, size_t at);\n";

static const char u8_defs_bref_ci[] =
"/* The fold is spelled arithmetically and covers exactly A-Z <-> a-z. No\n"
" * tolower(): that is locale-dependent at YOUR run time, and this matcher's\n"
" * answers must not change with setlocale(). Bytes >= 0x80 are lead or\n"
" * continuation bytes of characters this artifact's fold does not touch. */\n"
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

/* ---- entry 4: the lookbehind back-step ----------------------------------
 *
 * THE BODY IS utf8_design.md §5.2.1's REPAIRED ONE, r54 E4, and the line the
 * first design draft did not have is marked below. The defect it repairs:
 * a walk that skips continuation bytes without checking that the lead byte
 * DECLARES the length of the run it walked answers "one character back = 0"
 * on `C2 80 80` (a two-byte lead followed by TWO continuations), the forward
 * body then consumes the well-formed `C2 80` and ends one byte past where it
 * started, and the lookbehind end-check fires — which on a NEGATIVE
 * lookbehind is RX_R_INTERNAL, below PCREC_ERR_FLOOR, and a composed call
 * site TRAPS on a subject §2.6 promises will merely not match. Reachable on
 * a WELL-FORMED subject too, through a caller-supplied mid-character
 * `startpos` (§2.6.1.1).
 *
 * THE INVARIANT THE LENGTH TEST BUYS (§5.2.1): if back_step returns q, then
 * s[q..pos) decomposes into exactly k length-consistent UTF-8 runs, so a
 * k-character body started at q ends at pos ON EVERY INPUT — the end-check's
 * redundancy argument becomes unconditional and RX_R_INTERNAL unreachable
 * from this construct. It is deliberately a LENGTH test and not a validity
 * test: a full validator here would be a second UTF-8 decoder beside the
 * automaton, two definitions of well-formedness that could drift, and the
 * invariant does not need one (an overlong run is length-consistent, and the
 * forward automaton has no accepting path over it — the body fails, the
 * end-check is never reached). */

static const char u8_decls_back_step[] =
"/* $_back_step -- the ENCODING RESIDUAL entry for a LOOKBEHIND BACK-STEP\n"
" * (pcrec DD-12/D58).\n"
" *\n"
" * Returns the position exactly `k` CHARACTERS before `pos`, or\n"
" * $_BACK_STEP_NONE when fewer than k characters precede pos.\n"
" *\n"
" * Reads s only at offsets in [0, pos), so the (s == NULL, n == 0) subject\n"
" * $_search accepts is legal here too.\n"
" *\n"
" * THIS artifact was compiled for the `utf8` encoding: the walk skips back\n"
" * over continuation bytes and VALIDATES each stepped-over run against its\n"
" * lead byte's declared length. A malformed run answers $_BACK_STEP_NONE\n"
" * (\"no such position\"), never a position inside or beyond it -- pcrec's\n"
" * ill-formed-input rule is that such a subject matches nothing. */\n"
"size_t $_back_step(const unsigned char *s, size_t n, size_t pos, size_t k);\n"
"#define $_BACK_STEP_NONE ((size_t)-1)\n";

static const char u8_defs_back_step[] =
"/* utf8 encoding: walk back one length-validated character run per step. */\n"
"size_t $_back_step(const unsigned char *s, size_t n, size_t pos, size_t k)\n"
"{\n"
"    (void)n;                 /* reads only below pos, as the contract says */\n"
"    while (k--) {\n"
"        size_t end = pos;    /* one past the character being stepped over */\n"
"        size_t want;\n"
"        unsigned char lead;\n"
"\n"
"        if (pos == 0) return $_BACK_STEP_NONE;\n"
"        /* At most 3 continuation bytes may precede a lead byte. Stopping\n"
"         * at 3 is not a guard against long runs -- it is the encoding: a\n"
"         * 5-byte form is not UTF-8, so a 4th continuation means the run is\n"
"         * malformed and the length test below rejects it anyway. */\n"
"        do { pos--; } while (pos > 0 && (s[pos] & 0xC0) == 0x80\n"
"                             && end - pos < 4);\n"
"\n"
"        lead = s[pos];\n"
"        if      (lead < 0x80)            want = 1;\n"
"        else if ((lead & 0xE0) == 0xC0)  want = 2;\n"
"        else if ((lead & 0xF0) == 0xE0)  want = 3;\n"
"        else if ((lead & 0xF8) == 0xF0)  want = 4;\n"
"        else return $_BACK_STEP_NONE;  /* a continuation byte, or 0xF8+ */\n"
"\n"
"        /* THE LINE THE FIRST DESIGN DRAFT DID NOT HAVE (pcrec r54 E4).\n"
"         * The lead byte must DECLARE exactly the run this loop walked.\n"
"         * Without it a `C2 80 80` run answers \"one character back = 0\",\n"
"         * the forward body consumes the well-formed `C2 80` and ends at 1\n"
"         * past where it started, and the lookbehind end-check -- whose\n"
"         * redundancy proof assumes back_step and the forward parse agree\n"
"         * -- fires. On a NEGATIVE lookbehind that is a below-the-floor\n"
"         * internal-error return, and a composed call site traps. */\n"
"        if (want != end - pos) return $_BACK_STEP_NONE;\n"
"    }\n"
"    return pos;\n"
"}\n";

static const PcrecEncEntry entries_utf8[] = {
    { PCREC_ENCE_NEXT_POS,      false, u8_decls_next_pos,  u8_defs_next_pos  },
    { PCREC_ENCE_BREF,          true,  u8_decls_bref,      u8_defs_bref      },
    { PCREC_ENCE_BREF_CASELESS, true,  u8_decls_bref_ci,   u8_defs_bref_ci   },
    { PCREC_ENCE_BACK_STEP,     true,  u8_decls_back_step, u8_defs_back_step },
    { 0, false, NULL, NULL }
};

/* [K49] THE UNANCHORED RETRY ADVANCE (enc.h's `advance` field), and it is this
 * backend's own `next_pos` rule written as an inline step because DD-12 (7)
 * forbids an engine body calling the entry.
 *
 * A position is a character boundary under UTF-8 iff its byte is not a
 * CONTINUATION byte — `0` and `n` counting as boundaries — so "the next
 * boundary strictly after pos" is one step plus a skip over continuations.
 * The skip is bounded by `n` rather than by 3 for `next_pos`'s own reason: an
 * ill-formed run then degrades to "the next non-continuation byte" instead of
 * to a position inside the garbage, and, per utf8_design.md §2.6(c), an
 * ill-formed byte must remain something a search can advance PAST — matches
 * after a bad byte are found, matches through it are not. */
static const char advance_utf8[] =
"/* [K49] The retry advance is this ENCODING's step, not `+ 1`: an\n"
" * unanchored search may only ever try LATER CHARACTER BOUNDARIES as\n"
" * match starts, or it can report a position inside a character. A\n"
" * boundary here is any position whose byte is not a continuation\n"
" * byte, so the step is one forward and then over the continuations. */\n"
"@P++;\n"
"while (@P < @N\n"
"       && (@S[@P] & 0xC0) == 0x80) @P++;\n";

const PcrecEnc pcrec_enc_backend_utf8 = {
    /* `max_cp` is Unicode's maximum: the complement universe `[^x]` means
     * under this encoding (enc.h's field comment, utf8_design.md §2.7.1). */
    PCREC_ENC_UTF8, "utf8", 0x10FFFFu, entries_utf8, advance_utf8
};
