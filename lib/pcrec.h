/* pcrec — PCRE-to-C regex compiler: public library API.
 * Compile a pattern to specialized C source; the generated code has no
 * dependency on this library. */
#ifndef PCREC_H
#define PCREC_H

#include <stddef.h>

enum {
    PCREC_ENC_ASCII = 0,   /* byte semantics, 8-bit clean */
    PCREC_ENC_UTF8  = 1    /* not yet implemented (module 'utf8', M5) */
};

typedef struct {
    const char *prefix;      /* C identifier prefix for generated symbols; default "rx" */
    int         encoding;    /* PCREC_ENC_* */
    int         caseless;    /* nonzero: match case-insensitively (ASCII letters
                                only — Unicode folding is module 'utf8', M5).
                                Compiled AWAY into the automaton's byte classes:
                                the generated code carries no flag, no branch and
                                no case conversion, and its entry point has the
                                same signature either way (D18). That zero-cost
                                claim is scoped to the ASCII tier's constructs:
                                backreferences under (?i) (module 'backrefs', and
                                the M4 VM before them) compare captured SUBJECT
                                text at run time and are where it gets
                                re-examined (D23). */
    int         emit_main;   /* nonzero: append a standalone main() to the .c */
    const char *header_name; /* name used in the generated #include "...";
                                NULL = self-contained .c (declarations inlined,
                                h_src not produced) */
} pcrec_options;

typedef struct {
    char   msg[256];  /* human-readable diagnostic */
    size_t pos;       /* byte offset into the pattern, when applicable */
} pcrec_error;

typedef struct {
    char *c_src;      /* malloc'd; free with pcrec_output_free */
    char *h_src;      /* malloc'd or NULL when options.header_name == NULL */
} pcrec_output;

void pcrec_default_options(pcrec_options *opt);

/* Returns 0 on success (out filled), -1 on failure (err filled if non-NULL). */
int pcrec_compile(const char *pattern, const pcrec_options *opt,
                  pcrec_output *out, pcrec_error *err);

/* Generated searcher contract: <prefix>_search(s, n, startpos, m) searches
 * s[startpos..n) and returns 1 with *m filled (byte offsets, end exclusive)
 * or 0. startpos > n returns 0. `^` anchors to absolute offset 0 regardless
 * of startpos. m may be NULL. s may be NULL only when n == 0.
 *
 * The one-shot form above is the WHOLE generated contract today. The
 * streaming interface APPROACH.md §6 specifies (<prefix>_stream_init/feed/
 * end) is not emitted yet: it arrives with milestone M3, whose design gate
 * (docs/plan.md, M3.0) owns reconciling that contract with the two-pass
 * engine before any streaming code is written. */

void pcrec_output_free(pcrec_output *out);

#endif /* PCREC_H */
