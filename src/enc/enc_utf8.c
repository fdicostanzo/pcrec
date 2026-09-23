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
#include "enc/enc.h"

/* ---- entry 1: next_pos -------------------------------------------------- */

static const char u8_decls_next_pos_doc[] =
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
" * the self-synchronizing reading and never loops or reads out of range. */\n";

static const char u8_decls_next_pos[] =
"size_t $_next_pos(const unsigned char *s, size_t n, size_t pos);\n";

static const char u8_defs_next_pos_doc[] =
"/* utf8 encoding: skip forward over continuation bytes. A well-formed\n"
" * character's continuations are at most 3, but the loop is bounded by n\n"
" * rather than by 4 so that ill-formed input degrades to \"next\n"
" * non-continuation byte\" instead of to a mid-garbage position. */\n";

static const char u8_defs_next_pos[] =
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

static const char u8_decls_bref_doc[] =
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
" * fact and the exact compare is byte-wise. */\n";

static const char u8_decls_bref[] =
"ptrdiff_t $_bref_match(const unsigned char *s, size_t n,\n"
"                       size_t ref_start, size_t ref_end, size_t at);\n";

static const char u8_defs_bref_doc[] =
"/* utf8 encoding: the exact compare is a byte compare (UTF-8 is a prefix\n"
" * code -- equal characters and equal bytes are the same fact). */\n";

static const char u8_defs_bref[] =
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

static const char u8_decls_bref_ci_doc[] =
"/* $_bref_match_caseless -- the ENCODING RESIDUAL entry for a CASELESS\n"
" * backreference compare (pcrec DD-12/D58): $_bref_match, folding case.\n"
" *\n"
" * Same contract, same return protocol. THIS artifact folds by Unicode\n"
" * DEFAULT SIMPLE case folding -- the same relation its character classes\n"
" * were widened by, so one artifact carries one definition of caselessness.\n"
" *\n"
" * THE RETURN IS A LENGTH AND HERE IS WHERE THAT PAYS. A fold partner may\n"
" * encode to a different number of bytes, so the subject bytes consumed need\n"
" * not equal ref_end - ref_start: `^(k)\\1$` on \"k\" + U+212A (KELVIN) is a\n"
" * match of length 4 -- one byte captured, three consumed. */\n";

static const char u8_decls_bref_ci[] =
"ptrdiff_t $_bref_match_caseless(const unsigned char *s, size_t n,\n"
"                                size_t ref_start, size_t ref_end, size_t at);\n";

static const char u8_defs_bref_ci_doc[] =
"/* THE SIMPLE CASE-FOLD MAP, sorted by source code point: {from, to}, where\n"
" * `to` is that code point's canonical fold representative. Two characters\n"
" * are caselessly equal exactly when their representatives are equal, so a\n"
" * representative is all a compare needs and only the non-identity entries\n"
" * are here. A direct-indexed 0x110000-entry map would be ~4.4 MB.\n"
" *\n"
" * GENERATED from the Unicode Character Database's CaseFolding.txt, `C` and\n"
" * `S` status lines only (simple folding). Full folding is 1:n and would not\n"
" * fit a character-to-character compare; pcrec's reference oracle implements\n"
" * none of it. */\n";

static const char u8_defs_bref_ci[] =
"static const unsigned $_bref_ci_fold_pairs[][2] =\n"
/* The brace is on its own line so ONE brace-matching walk serves both a
 * function body and this initializer -- `tests/codegen/run_encoding_
 * checks.sh`'s DD12a(i) excision, which must treat this table as part of
 * the residual entry it belongs to. */
"{\n"
#include "utf8_fold_pairs.inc"
"};\n"
"\n"
"static unsigned $_bref_ci_fold(unsigned c)\n"
"{\n"
"    size_t lo = 0;\n"
"    size_t hi = sizeof $_bref_ci_fold_pairs / sizeof $_bref_ci_fold_pairs[0];\n"
"    while (lo < hi) {\n"
"        size_t mid = lo + (hi - lo) / 2;\n"
"        if ($_bref_ci_fold_pairs[mid][0] < c) lo = mid + 1;\n"
"        else if ($_bref_ci_fold_pairs[mid][0] > c) hi = mid;\n"
"        else return $_bref_ci_fold_pairs[mid][1];\n"
"    }\n"
"    return c;\n"
"}\n"
"\n"
"/* Decode the character at s[p], bounded by `end`. Returns its length in\n"
" * bytes, or 0 when the sequence is truncated or ILL-FORMED -- and the\n"
" * ill-formed set is exactly the automaton's (overlong forms, surrogates and\n"
" * code points above U+10FFFF are excluded from every lowered class), so a\n"
" * subject this compare rejects is one no other part of the artifact would\n"
" * have matched either. This matcher's rule is that ill-formed input matches\n"
" * nothing, never that it is an error. */\n"
"static size_t $_bref_ci_decode(const unsigned char *s, size_t end, size_t p,\n"
"                               unsigned *cp)\n"
"{\n"
"    unsigned char b = s[p];\n"
"    size_t len, i;\n"
"    unsigned v, floor;\n"
"    if (b < 0x80u)               { *cp = b; return 1; }\n"
"    else if ((b & 0xE0u) == 0xC0u) { len = 2; v = b & 0x1Fu; floor = 0x80u; }\n"
"    else if ((b & 0xF0u) == 0xE0u) { len = 3; v = b & 0x0Fu; floor = 0x800u; }\n"
"    else if ((b & 0xF8u) == 0xF0u) { len = 4; v = b & 0x07u; floor = 0x10000u; }\n"
"    else return 0;\n"
"    if (p + len > end) return 0;\n"
"    for (i = 1; i < len; i++) {\n"
"        if ((s[p + i] & 0xC0u) != 0x80u) return 0;\n"
"        v = (v << 6) | (unsigned)(s[p + i] & 0x3Fu);\n"
"    }\n"
"    if (v < floor || v > 0x10FFFFu || (v >= 0xD800u && v <= 0xDFFFu)) return 0;\n"
"    *cp = v;\n"
"    return len;\n"
"}\n"
"\n"
"/* The walk is per CHARACTER on BOTH sides and the two cursors advance\n"
" * independently, which is the whole difference from the exact compare: the\n"
" * reference's character and the subject's may be different byte lengths.\n"
" * The prefix reported on failure is the SUBJECT bytes that did compare\n"
" * equal, because that is the work this call actually did. */\n"
"ptrdiff_t $_bref_match_caseless(const unsigned char *s, size_t n,\n"
"                                size_t ref_start, size_t ref_end, size_t at)\n"
"{\n"
"    size_t i = ref_start, j = at;\n"
"    while (i < ref_end) {\n"
"        unsigned x = 0, y = 0;\n"
"        size_t lx = $_bref_ci_decode(s, ref_end, i, &x);\n"
"        size_t ly = (j < n) ? $_bref_ci_decode(s, n, j, &y) : 0;\n"
"        if (lx == 0 || ly == 0 ||\n"
"            $_bref_ci_fold(x) != $_bref_ci_fold(y))\n"
"            return -(ptrdiff_t)(j - at) - 1;\n"
"        i += lx;\n"
"        j += ly;\n"
"    }\n"
"    return (ptrdiff_t)(j - at);\n"
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

static const char u8_decls_back_step_doc[] =
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
" * ill-formed-input rule is that such a subject matches nothing. */\n";

static const char u8_decls_back_step[] =
"size_t $_back_step(const unsigned char *s, size_t n, size_t pos, size_t k);\n"
"#define $_BACK_STEP_NONE ((size_t)-1)\n";

static const char u8_defs_back_step_doc[] =
"/* utf8 encoding: walk back one length-validated character run per step. */\n";

static const char u8_defs_back_step[] =
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

/* ---- entries 5 and 6: the CALLER-VARIABLE COMPARE ([VAR], D58 scope item 3)
 *
 * `variables_pattern.md` §1.3, the utf8 half. The EXACT compare is a byte
 * compare for the same reason the exact backreference compare is (UTF-8 is a
 * prefix code, so equal bytes and equal characters are one fact) and the
 * CASELESS one is the decode-and-fold walk, with the reference cursor reading
 * the caller's buffer instead of the subject.
 *
 * THE CASELESS ROW DECLARES `requires = PCREC_ENCE_BREF_CASELESS`, and that
 * column exists for exactly this. The fold map is 1,484 pairs and the decoder
 * is thirty lines; both already ship as `$_bref_ci_fold_pairs` /
 * `$_bref_ci_fold` / `$_bref_ci_decode` inside the caseless backreference
 * entry's own text. Carrying a second copy here would double a table in any
 * artifact that used both; renaming them into a shared entry would move the
 * emitted bytes of every caseless-backreference artifact that has ever been
 * built. Declaring the dependency does neither: a caseless-variable artifact
 * additionally carries `$_bref_match_caseless` itself, which is one exported
 * function it never calls (`next_pos`'s own shape, and enc.h's paragraph on
 * why a residual cannot be `static`).
 *
 * THE VALUE IS KNOWN WELL-FORMED BEFORE EITHER BODY RUNS. The entry wrapper
 * validates it once per call (`variables_common.md` §2.1's refusal, which
 * cannot live in a two-valued return space), so the decoder below can assume
 * of `v` exactly what the backreference decoder assumes of a captured span:
 * that the automaton would have accepted it. What it may NOT assume of `s` is
 * anything at all, which is why the subject side still checks. */
static const char u8_decls_var_doc[] =
"/* $_var_match -- the ENCODING RESIDUAL entry for a CASE-SENSITIVE compare\n"
" * against a CALLER-SUPPLIED value (pcrec [VAR]).\n"
" *\n"
" * PRECONDITION: v points at vlen readable bytes, and (under this encoding)\n"
" * they are well-formed UTF-8. The entry wrapper checks both before the\n"
" * match begins -- a value that is not well-formed is a REFUSED CALL, not a\n"
" * silent nomatch, and this entry's two-valued return has no room to say so.\n"
" *\n"
" * RETURNS, exactly as $_bref_match does:\n"
" *     >= 0   the number of SUBJECT bytes consumed at `at`; under a\n"
" *            length-changing fold this need not equal vlen.\n"
" *     <  0   no match, and -(result) - 1 is the number of subject bytes\n"
" *            that DID compare equal -- the work this call did.\n"
" *\n"
" * THE VALUE'S BYTES ARE MATCHED AS THEMSELVES, never parsed as pattern\n"
" * syntax, under any flag (variables_common.md section 4.2).\n"
" *\n"
" * THIS artifact was compiled for the `utf8` encoding. UTF-8 is a prefix\n"
" * code, so equal byte sequences and equal character sequences are one fact\n"
" * and the exact compare is byte-wise. */\n";

static const char u8_decls_var[] =
"ptrdiff_t $_var_match(const unsigned char *s, size_t n,\n"
"                      const unsigned char *v, size_t vlen, size_t at);\n";

static const char u8_defs_var_doc[] =
"/* utf8 encoding: the exact compare is a byte compare (UTF-8 is a prefix\n"
" * code -- equal characters and equal bytes are the same fact). */\n";

static const char u8_defs_var[] =
"ptrdiff_t $_var_match(const unsigned char *s, size_t n,\n"
"                      const unsigned char *v, size_t vlen, size_t at)\n"
"{\n"
"    size_t i;\n"
"    for (i = 0; i < vlen; i++) {\n"
"        if (at + i >= n || s[at + i] != v[i])\n"
"            return -(ptrdiff_t)i - 1;\n"
"    }\n"
"    return (ptrdiff_t)vlen;\n"
"}\n";

static const char u8_decls_var_ci_doc[] =
"/* $_var_match_caseless -- the ENCODING RESIDUAL entry for a CASELESS\n"
" * compare against a caller-supplied value (pcrec [VAR]): $_var_match,\n"
" * folding case.\n"
" *\n"
" * Same contract, same return protocol. THIS artifact folds by Unicode\n"
" * DEFAULT SIMPLE case folding -- the same relation its character classes\n"
" * were widened by, so one artifact carries one definition of caselessness.\n"
" *\n"
" * THE RETURN IS A LENGTH AND HERE IS WHERE THAT PAYS. A fold partner may\n"
" * encode to a different number of bytes, so the subject bytes consumed need\n"
" * not equal vlen: a value of \"k\" matches U+212A (KELVIN) in three subject\n"
" * bytes against one value byte.\n"
" *\n"
" * THE VALUE IS NOT PRE-FOLDED, and under this encoding it could not be: a\n"
" * fold can change byte length, so a pre-folded value's length would no\n"
" * longer correspond to the subject bytes it should consume -- the same fact\n"
" * that makes this entry return a length rather than a bool.\n"
" *\n"
" * It shares $_bref_match_caseless's fold map and decoder rather than\n"
" * carrying a second copy of either. */\n";

static const char u8_decls_var_ci[] =
"ptrdiff_t $_var_match_caseless(const unsigned char *s, size_t n,\n"
"                               const unsigned char *v, size_t vlen,\n"
"                               size_t at);\n";

static const char u8_defs_var_ci_doc[] =
"/* The walk is per CHARACTER on BOTH sides and the two cursors advance\n"
" * independently -- the value's character and the subject's may be different\n"
" * byte lengths. The prefix reported on failure is the SUBJECT bytes that\n"
" * did compare equal, because that is the work this call actually did. */\n";

static const char u8_defs_var_ci[] =
"ptrdiff_t $_var_match_caseless(const unsigned char *s, size_t n,\n"
"                               const unsigned char *v, size_t vlen,\n"
"                               size_t at)\n"
"{\n"
"    size_t i = 0, j = at;\n"
"    while (i < vlen) {\n"
"        unsigned x = 0, y = 0;\n"
"        size_t lx = $_bref_ci_decode(v, vlen, i, &x);\n"
"        size_t ly = (j < n) ? $_bref_ci_decode(s, n, j, &y) : 0;\n"
"        if (lx == 0 || ly == 0 ||\n"
"            $_bref_ci_fold(x) != $_bref_ci_fold(y))\n"
"            return -(ptrdiff_t)(j - at) - 1;\n"
"        i += lx;\n"
"        j += ly;\n"
"    }\n"
"    return (ptrdiff_t)(j - at);\n"
"}\n";

/* ---- entry 7: the VALUE VALIDITY PREDICATE ([VAR], variables_common.md §2.1)
 *
 * A caller-supplied value that is not well-formed UTF-8 is a REFUSED CALL
 * under this encoding, not a silent nomatch — the opposite of the rule for a
 * SUBJECT, whose ill-formed bytes correctly match nothing because the
 * automaton was built over well-formed classes and the reference span a
 * backreference compares came out of that automaton. A value came from the
 * caller and has passed through nothing.
 *
 * SO THE CHECK IS THE ENTRY WRAPPER'S, once per call per resolved expansion,
 * and it is a SEPARATE ENTRY rather than a line inside the compare for the
 * reason the D6 panel's MECH-M4 states: the compare's return space is
 * two-valued by sign and has no room for "refuse" without breaking the
 * protocol `$_bref_match` already fixed.
 *
 * THE BACKEND'S HAVING A ROW HERE IS WHAT TURNS THE CHECK ON. `entries_byte[]`
 * has none, because every byte string is a valid `byte` string, and the
 * emitter then emits nothing — no encoding conditional anywhere (DD-12 (7)).
 *
 * IT IS ITS OWN DECODER AND DELIBERATELY NOT `$_bref_ci_decode`'s. That one
 * ships only in a CASELESS artifact, and validity is asked of every variable
 * whatever its caselessness; depending on it would make an exact-compare
 * artifact drag in a 1,484-pair fold table to answer a question about byte
 * shapes. The two agree on what well-formed means — same lead-byte families,
 * same overlong floors, same surrogate and U+10FFFF exclusions, which are the
 * automaton's own — and that agreement is the thing to preserve if either
 * moves. */
static const char u8_decls_var_valid_doc[] =
"/* $_var_valid -- is a caller-supplied value well-formed under this\n"
" * artifact's encoding? (pcrec [VAR], variables_common.md section 2.1.)\n"
" *\n"
" * Called ONCE PER CALL per resolved variable, before the match begins. A\n"
" * false answer is a REFUSED CALL (PCREC_ERR_UNSET_VAR), never a nomatch:\n"
" * the caller handed this matcher bytes it cannot interpret, which is a\n"
" * different thing from a subject that simply does not match. */\n";

static const char u8_decls_var_valid[] =
"int $_var_valid(const unsigned char *v, size_t vlen);\n";

static const char u8_defs_var_valid_doc[] =
"/* Well-formed means exactly what the automaton's own lowered classes mean:\n"
" * the four lead-byte families, the right number of continuation bytes, no\n"
" * overlong form, no surrogate, nothing above U+10FFFF. */\n";

static const char u8_defs_var_valid[] =
"int $_var_valid(const unsigned char *v, size_t vlen)\n"
"{\n"
"    size_t p = 0;\n"
"    while (p < vlen) {\n"
"        unsigned char b = v[p];\n"
"        size_t len, i;\n"
"        unsigned c, floor;\n"
"        if (b < 0x80u)                 { p += 1; continue; }\n"
"        else if ((b & 0xE0u) == 0xC0u) { len = 2; c = b & 0x1Fu; floor = 0x80u; }\n"
"        else if ((b & 0xF0u) == 0xE0u) { len = 3; c = b & 0x0Fu; floor = 0x800u; }\n"
"        else if ((b & 0xF8u) == 0xF0u) { len = 4; c = b & 0x07u; floor = 0x10000u; }\n"
"        else return 0;\n"
"        if (p + len > vlen) return 0;\n"
"        for (i = 1; i < len; i++) {\n"
"            if ((v[p + i] & 0xC0u) != 0x80u) return 0;\n"
"            c = (c << 6) | (unsigned)(v[p + i] & 0x3Fu);\n"
"        }\n"
"        if (c < floor || c > 0x10FFFFu || (c >= 0xD800u && c <= 0xDFFFu))\n"
"            return 0;\n"
"        p += len;\n"
"    }\n"
"    return 1;\n"
"}\n";

static const PcrecEncEntry entries_utf8[] = {
    { PCREC_ENCE_NEXT_POS,      false, 0,
      u8_decls_next_pos_doc,  u8_decls_next_pos,
      u8_defs_next_pos_doc,   u8_defs_next_pos  },
    { PCREC_ENCE_BREF,          true,  0,
      u8_decls_bref_doc,      u8_decls_bref,
      u8_defs_bref_doc,       u8_defs_bref      },
    { PCREC_ENCE_BREF_CASELESS, true,  0,
      u8_decls_bref_ci_doc,   u8_decls_bref_ci,
      u8_defs_bref_ci_doc,    u8_defs_bref_ci   },
    { PCREC_ENCE_BACK_STEP,     true,  0,
      u8_decls_back_step_doc, u8_decls_back_step,
      u8_defs_back_step_doc,  u8_defs_back_step },
    { PCREC_ENCE_VAR,           true,  0,
      u8_decls_var_doc,       u8_decls_var,
      u8_defs_var_doc,        u8_defs_var       },
    /* [VAR] THE ONE ROW THE `requires` COLUMN EXISTS FOR: this body calls
     * `$_bref_ci_decode`/`$_bref_ci_fold`, which the caseless backreference
     * entry's own text defines. See that entry's header for why sharing
     * beats both alternatives. */
    { PCREC_ENCE_VAR_CASELESS,  true,  PCREC_ENCE_BREF_CASELESS,
      u8_decls_var_ci_doc,    u8_decls_var_ci,
      u8_defs_var_ci_doc,     u8_defs_var_ci    },
    /* [VAR] NOT engine-callable: the entry wrapper's once-per-call
     * resolution calls it, never an engine body — `next_pos`'s own status,
     * and the [M5-SEAM] check's rule applies to it on the same terms. */
    { PCREC_ENCE_VAR_VALID,     false, 0,
      u8_decls_var_valid_doc, u8_decls_var_valid,
      u8_defs_var_valid_doc,  u8_defs_var_valid },
    { 0, false, 0, NULL, NULL, NULL, NULL }
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

/* [K50] WHERE A MATCH MAY BEGIN — the two spellings enc.h's `start_cls` and
 * `start_guard` document, and they are the SAME predicate `next_pos` and the
 * `advance` above already implement: a position is a character boundary iff it
 * is the end of the subject or its byte is not a continuation byte.
 *
 * THE SET IS "NOT A CONTINUATION BYTE", NOT "A VALID LEAD BYTE", and the
 * difference is utf8_design.md §2.6(c) rather than sloppiness. An ill-formed
 * byte — 0xFE, 0xFF, an overlong lead, a lead whose continuations are missing
 * — is a POSITION A SEARCH MAY START AT, because §2.6(c)'s ruled semantics
 * require matches after an ill-formed byte to be found (`a` on `FF 63` gives
 * `(1,2)`). K50's fix gates where attempts BEGIN; it does not make the search
 * refuse to walk past garbage, and a lead-byte set would have done the latter.
 * The bytes excluded are exactly 0x80..0xBF.
 *
 * THE PARTITION PRECONDITION enc.h states is satisfied and is worth checking
 * by eye as well as by `pcrec_enc_start_cls_ok`: 0x80..0xBF holds no word byte
 * and no newline, both of which are ASCII. */
static const unsigned char start_cls_utf8[32] = {
    /* 0x00..0x7F: every ASCII byte starts a character */
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    /* 0x80..0xBF: the continuation bytes — the ONLY positions excluded */
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    /* 0xC0..0xFF: leads, and the ill-formed bytes §2.6(c) keeps startable */
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF
};

/* The same rule as an expression, and the two clauses in front of the byte
 * test are each there for a stated reason rather than for safety.
 *
 * `@P >= @N` SO THE SUBJECT IS NEVER READ AT `@N`: match_api.md §3.1 promises
 * the matcher never reads `s[n]`, and the end of the subject is a character
 * boundary.
 *
 * `@P == 0` BECAUSE OFFSET 0 IS ALWAYS A VALID START, AND THAT IS A RULING
 * ABOUT ILL-FORMED INPUT RATHER THAN AN EXEMPTION. The byte test is LOCAL —
 * "is this a continuation byte" — which is exactly what libpcre2 asks under
 * `PCRE2_UTF`, but libpcre2 asks it only AFTER a whole-subject validation pass
 * has already rejected an ill-formed subject (§2.6(b)). pcrec has no such
 * pass: Frank's ASK 1 ruling is that an ill-formed sequence MATCHES NOTHING,
 * with "no validation pass, no error return". So this guard sees subjects
 * libpcre2's would never reach, and on a subject that BEGINS with a
 * continuation byte the local test alone refuses offset 0 — turning
 * "ill-formed input matches nothing" into "ill-formed input is an error",
 * which is that ruling inverted.
 *
 * Two independent reasons agree. A caller naming offset 0 cannot have pointed
 * INSIDE a character, because none precedes it, so it is not the caller error
 * this guard exists to catch. And MEASURED: without the clause, 21
 * oracle-verified cells across `tests/utf8/axis01`, `axis03` and `axis09` stop
 * answering and return `PCREC_ERR_STARTPOS` — `a` on the one-byte subject
 * `\x80` among them. Those cells ARE §2.6's ruled semantics, and what found it
 * was wiring this axis into `make test-axes`.
 *
 * It costs the guard nothing anywhere else: `ENG_ATTEMPT`'s use of this same
 * text is already gated on `start > search_from`, so `@P == 0` cannot be true
 * there, and the IR gate is a different mechanism that never sees position 0
 * (the ungated split is the one the caller's own position enters). */
static const char start_guard_utf8[] =
    "@P == 0 || @P >= @N || (@S[@P] & 0xC0) != 0x80";

const PcrecEnc pcrec_enc_backend_utf8 = {
    /* `max_cp` is Unicode's maximum: the complement universe `[^x]` means
     * under this encoding (enc.h's field comment, utf8_design.md §2.7.1). */
    /* [M5.0 stage 4] the fold is Unicode DEFAULT SIMPLE case folding — the
     * relation `CaseFolding.txt`'s `C` and `S` lines define, which §4.1
     * MEASURED to be the whole of libpcre2 10.46's caseless behaviour under
     * `PCRE2_UTF` (0 of 11 one-to-many cells match). The residual caseless
     * compare below folds through the SAME data, generated in the same run. */
    PCREC_ENC_UTF8, "utf8", 0x10FFFFu, &pcrec_fold_ucd_simple,
    entries_utf8, advance_utf8,
    start_cls_utf8, start_guard_utf8
};
