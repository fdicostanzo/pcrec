/* sha256.h -- one-shot SHA-256 (FIPS 180-4), zero dependencies.
 *
 * pcrec-analyze's provenance digest ("sha256 HEX" on --digest-only, the
 * `provenance sha256` line on a whole-file scan) is a straight SHA-256 of
 * the input bytes -- nothing pcrec-specific. `analyze/` is a SEPARATE
 * zero-dependency binary (design.md §10.1's end-state row) and does not
 * link libpcrec, so this is its own small implementation rather than a
 * reach into src/.
 */
#ifndef PCREC_ANALYZE_SHA256_H
#define PCREC_ANALYZE_SHA256_H

#include <stddef.h>

/* Writes the 64 lowercase hex digits + NUL into out (out must hold >= 65
 * bytes). One-shot: the whole buffer is hashed in a single call, which is
 * sufficient here since every caller already holds its input fully in
 * memory (design.md §10.3's "one-pass" claim is about the COUNTERS; a
 * digest over an in-memory buffer needs no separate streaming state). */
void pcrec_analyze_sha256_hex(const unsigned char *data, size_t len, char out[65]);

#endif
