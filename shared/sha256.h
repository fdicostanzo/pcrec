/* sha256.h -- one-shot SHA-256 (FIPS 180-4), zero dependencies.
 *
 * The tree's ONE SHA-256 (docs/design/inline_c.md §5.5). Two binaries
 * compile it separately and neither links the other: `build/pcrec-analyze`
 * (the provenance digest of an exemplar file, "sha256 HEX") and `libpcrec`
 * (an `include`/`lib` line's `sha256 <hex64>` pin, checked over the bytes
 * the `.rxt` reader parses). A leaf: it includes nothing of pcrec's, so
 * analyze/'s independence from src/ holds and src/ never reaches into
 * analyze/. Its control is the NIST vectors plus `sha256sum`, never the
 * other binary.
 */
#ifndef PCREC_SHARED_SHA256_H
#define PCREC_SHARED_SHA256_H

#include <stddef.h>

/* Writes the 64 lowercase hex digits + NUL into out (out must hold >= 65
 * bytes). One-shot: the whole buffer is hashed in a single call, which is
 * sufficient here since every caller already holds its input fully in
 * memory (design.md §10.3's "one-pass" claim is about the COUNTERS; a
 * digest over an in-memory buffer needs no separate streaming state). */
void pcrec_sha256_hex(const unsigned char *data, size_t len, char out[65]);

#endif
