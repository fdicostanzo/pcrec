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

typedef struct {
    int         id;      /* PCREC_ENC_* (lib/pcrec.h) */
    const char *name;    /* the ONE spelling: CLI value and diagnostics */
    const char *decls;   /* residual declarations, `$` = prefix; NULL = not
                            implemented yet (the name exists, the backend
                            does not) */
    const char *defs;    /* residual definitions, `$` = prefix */
} PcrecEnc;

/* The registry. Lookup is total over the namespace and returns NULL for a
 * value that is not a member at all. */
const PcrecEnc *pcrec_enc_by_id(int id);
const PcrecEnc *pcrec_enc_by_name(const char *name);
/* Render every member's name, comma-separated, into a CALLER-owned buffer —
 * no static scratch, because pcrec_compile() is called concurrently (TS-3)
 * and a lazily-filled shared buffer would be a data race in a diagnostic. */
void pcrec_enc_names(char *buf, size_t cap);

/* True when this member has a backend to embed (`decls != NULL`). */
static inline int pcrec_enc_ready(const PcrecEnc *e) { return e && e->decls; }

/* Copy `text` into `sb`, replacing every `$` with `prefix`. */
void pcrec_enc_emit_text(StrBuf *sb, const char *text, const char *prefix);

/* The backends themselves, one file each. */
extern const PcrecEnc pcrec_enc_backend_byte;   /* enc_byte.c */

#endif /* PCREC_GEN_ENC_H */
