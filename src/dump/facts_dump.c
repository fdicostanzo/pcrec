/* src/dump/facts_dump.c — [PATFACTS] `--emit-facts`: THE PATTERN-FACTS
 * RECORD AS A LISTING (docs/design/patfacts/design.md §11, ruled Q8-Q10;
 * the format contract is docs/spec/facts_listing.md).
 *
 * ONE PRINTER, NEVER A RECOMPUTATION (design §11.3). Every `facts` row is
 * read off the FINAL attempt's `Job.pf` — the memo the passes read — through
 * `facts.h` alone: the value by the fact's own renderer (the one the
 * artifact's stamps use, so a stamp and a row cannot disagree), and the
 * status, `why` and `used` bit exactly as the accessor STORED them. This file
 * calls no derivation and includes no private header; it is not an owner, so
 * `tests/codegen/run_facts_checks.sh` fails if it ever does.
 *
 * THE DECISIONS SECTION IS THE ARTIFACT'S OWN STAMP BLOCK (design §11.2,
 * §11.5, r1 A12). Route and emission decisions stay out of the record (D124)
 * and are inspectable anyway: this file reads the value `#define`s straight
 * off the final attempt's finished `.c` buffer, the artifact itself, so
 * nothing re-asks `req_admit` or `DFA_SELECT` to fill it. The "range" the
 * design names is the whole buffer: stamps sit in two blocks around the
 * `#include` lines and, on a VM artifact, beside the slot legend. A row is an
 * OBJECT-like `#define` whose name is `<PREFIX>_…` or `PCREC_FEATURE_…`; the
 * FUNCTION-like ones (`_TIER_NOTE`, `_CHARGE_WORK`, `_PRUNE_*`, `_TRAIL`,
 * `_SET`, `_PUSH`, `_CUT`, `_CALL` — code, not stamps) are excluded by their
 * `(`, and the check that compares this section with the emitted file
 * excludes them by NAME, so a new function-like macro is a check failure
 * rather than a silent omission.
 *
 * It sits in `dump/`, above the driver: the driver reaches it only through
 * the `PcrecFactsHook` it is handed, and names no symbol here. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
#include "enc/enc.h"

/* The two sections' rows, accumulated across one compile per encoding. */
typedef struct {
    StrBuf facts;
    StrBuf dec;
} FactsRows;

/* `facts.def`'s own name, epoch, kind and owner columns, by row. */
static const char *const fd_name[PF_NFACTS] = {
#define PF_FACT(ID, name, epoch, kind, deny, owner, depends) [PF_##ID] = name,
#include "facts/facts.def"
};
static const int fd_epoch[PF_NFACTS] = {
#define PF_FACT(ID, name, epoch, kind, deny, owner, depends) [PF_##ID] = (epoch),
#include "facts/facts.def"
};
static const PfKind fd_kind[PF_NFACTS] = {
#define PF_FACT(ID, name, epoch, kind, deny, owner, depends) [PF_##ID] = kind,
#include "facts/facts.def"
};
static const char *const fd_owner[PF_NFACTS] = {
#define PF_FACT(ID, name, epoch, kind, deny, owner, depends) [PF_##ID] = owner,
#include "facts/facts.def"
};

/* The CLI spelling of deny bit `bit`, off `src/core/axes.def` — the one
 * table the parser accepts it from, so a `why` token and the flag a caller
 * types cannot drift. A bit with no row prints as hex rather than vanishing. */
static const char *fd_deny_flag(Ctx *cx, uint64_t bit)
{
    /* The `!= 0` for axes_dump.c's reason: most of the macro column is enum
     * constants, which gcc reads as a likely mistake in a boolean context. */
#define PCREC_AXIS(dm, df, fm, ff, defst)                         \
    if ((uint64_t)(dm) != 0 && (uint64_t)(dm) == bit) return df;
#include "core/axes.def"
    return pcrec_sb_fragf(&cx->arena, "0x%llx", (unsigned long long)bit);
}

/* The CLOSED `status` vocabulary (facts_listing.md). An unasked fact never
 * reaches here — the force loop asked it — so it reads `absent` too. */
static const char *fd_status(const PfWhy *w)
{
    switch ((PfStatus)w->status) {
    case PF_ST_DERIVED:  return "derived";
    case PF_ST_DENIED:   return "denied";
    case PF_ST_DECLINED: return "declined";
    case PF_ST_ABSENT:
    case PF_ST_UNASKED:  return "absent";
    }
    return "absent";
}

/* The `why` token: `deny:<flag>`, `decline:<reason>`, `rate:<source>`, or
 * empty for a plain derivation. The token grammar is the contract; a reason's
 * NAME is advisory (facts_listing.md). */
static const char *fd_why(Ctx *cx, const PfWhy *w, const char *enc)
{
    switch ((PfWhyCode)w->code) {
    case PF_WHY_NONE:             return "";
    case PF_WHY_DENY:
        return pcrec_sb_fragf(&cx->arena, "deny:%s", fd_deny_flag(cx, w->deny));
    case PF_WHY_ENC_MULTIBYTE:    return "decline:enc-multibyte";
    case PF_WHY_NOT_END_ANCHORED: return "decline:not-end-anchored";
    case PF_WHY_GSTART:           return "decline:gstart";
    case PF_WHY_UNBOUNDED:        return "decline:unbounded";
    case PF_WHY_RATE_BUILTIN:     return "rate:builtin-prior";
    case PF_WHY_RATE_NONE:
        return pcrec_sb_fragf(&cx->arena, "rate:none(%s)->rightmost", enc);
    case PF_WHY_FORCE_FAILED:     return "decline:force-failed";
    }
    return "";
}

/* One `decisions` row per value stamp in the finished artifact `a[0..n)`. */
static void fd_decisions(Ctx *cx, FactsRows *r, const char *enc,
                         const char *a, size_t n)
{
    const char *up = pcrec_sb_upper(&cx->arena, cx->opt->prefix);
    size_t upl = strlen(up), i = 0;
    while (i < n) {
        size_t e = i, ns, ne, vs;
        while (e < n && a[e] != '\n') e++;
        if (e - i > 8 && !strncmp(a + i, "#define ", 8)) {
            ns = ne = i + 8;
            while (ne < e && a[ne] != ' ' && a[ne] != '\t' && a[ne] != '(') ne++;
            if (ne < e && a[ne] != '(' &&
                ((ne - ns > upl && !strncmp(a + ns, up, upl) && a[ns + upl] == '_') ||
                 (ne - ns > 14 && !strncmp(a + ns, "PCREC_FEATURE_", 14)))) {
                const char *cells[3];
                vs = ne;
                while (vs < e && (a[vs] == ' ' || a[vs] == '\t')) vs++;
                cells[0] = enc;
                cells[1] = pcrec_sb_fragf(&cx->arena, "%.*s", (int)(ne - ns), a + ns);
                cells[2] = pcrec_sb_fragf(&cx->arena, "%.*s", (int)(e - vs), a + vs);
                pcrec_sb_row(&r->dec, cells, 3);
            }
        }
        i = e + 1;
    }
}

/* THE HOOK the driver calls once, on the final attempt's success path, after
 * the force loop (src/core/compile.c's `facts_force`). */
static void fd_hook(Ctx *cx, const char *artifact, size_t len, void *ud)
{
    FactsRows *r = ud;
    const PatFacts *pf = &cx->job->pf;
    const PcrecEnc *e = pcrec_enc_by_id(cx->opt->encoding);
    const char *enc = e ? e->name : "?";
    for (int f = 0; f < PF_NFACTS; f++) {
        const char *cells[9];
        cells[0] = enc;
        cells[1] = fd_name[f];
        cells[2] = "pattern";
        cells[3] = pcrec_sb_fragf(&cx->arena, "E%d", fd_epoch[f]);
        cells[4] = fd_status(&pf->why[f]);
        cells[5] = (pf->used >> f) & 1u ? "yes" : "no";
        /* An ABSENT fact has no value to render: its memo was never
         * written, and printing the zeroed memo would claim an answer. */
        cells[6] = pf->why[f].status == PF_ST_ABSENT ||
                   pf->why[f].status == PF_ST_UNASKED
                 ? "" : pcrec_fact_render(cx, (PfFactId)f);
        cells[7] = fd_why(cx, &pf->why[f], enc);
        cells[8] = pcrec_sb_fragf(&cx->arena, "%s; owner %s",
                                  fd_kind[f] == PF_CORE ? "core" : "derived",
                                  fd_owner[f]);
        pcrec_sb_row(&r->facts, cells, 9);
    }
    fd_decisions(cx, r, enc, artifact, len);
}

char *pcrec_emit_facts(const char *pattern, const pcrec_options *opt,
                       const int *encs, int nenc, pcrec_error *err)
{
    FactsRows r;
    pcrec_options defo;
    StrBuf s = { 0 };
    int own;

    memset(&r, 0, sizeof r);
    pcrec_default_options(&defo);
    if (opt) defo = *opt;
    /* A paired header would move the ABI block's stamps out of the `.c` the
     * decisions section reads; `pcrec_emit_ir`'s own rule. */
    defo.header_name = NULL;
    own = defo.encoding;
    if (nenc <= 0) { encs = &own; nenc = 1; }

    for (int i = 0; i < nenc; i++) {
        pcrec_options o = defo;
        pcrec_output out;
        o.encoding = encs[i];
        if (pcrec_compile_driver(pattern, &o, &out, err, NULL, NULL, NULL,
                                 fd_hook, &r) != 0) {
            pcrec_sb_free(&r.facts);
            pcrec_sb_free(&r.dec);
            return NULL;
        }
        pcrec_output_free(&out);
    }

    pcrec_sb_puts(&s,
        "# pcrec --emit-facts: the pattern-facts record of the compile(s) below,\n"
        "# one per encoding (docs/spec/facts_listing.md). A DEBUG listing: the\n"
        "# section and column names and the status/used/why vocabularies are\n"
        "# promised; the fact names, reasons and notes are advisory.\n"
        "#section facts\n"
        "# One row per record fact, in facts.def order. `used` is yes when a pass\n"
        "# asked for the fact while the artifact was built, no when only this\n"
        "# listing asked (after the artifact was complete).\n"
        "#encoding\tfact\tgrain\tepoch\tstatus\tused\tvalue\twhy\tnote\n");
    if (r.facts.p) pcrec_sb_puts(&s, r.facts.p);
    pcrec_sb_puts(&s,
        "#section decisions\n"
        "# The artifact's own value stamps, read off the emitted C as written:\n"
        "# the route and emission DECISIONS the record does not hold (D124).\n"
        "#encoding\tstamp\tvalue\n");
    if (r.dec.p) pcrec_sb_puts(&s, r.dec.p);
    pcrec_sb_free(&r.facts);
    pcrec_sb_free(&r.dec);
    return pcrec_sb_take(&s);
}
