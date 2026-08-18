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

const PcrecEnc pcrec_enc_backend_byte = {
    PCREC_ENC_BYTE, "byte", decls_byte, defs_byte
};
