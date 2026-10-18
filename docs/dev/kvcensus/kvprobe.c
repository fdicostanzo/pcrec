/* docs/dev/kvcensus/kvprobe.c — the kvcensus SITE PROBE (measurement only).
 *
 * Linked into a copy of the CLI with GNU ld's --wrap, so NOTHING under src/
 * changes: every site pcrec hands the kit (pcrec_memfn_define /
 * pcrec_memfn_emit, the two doors in src/gen/memfn_sites.c) is recorded as
 * one tab-separated `SITE` line, then passed on unchanged. The kit's
 * define-time query (mf_ask, pure by contract) is asked for the same site
 * and hooks so the line also carries what the kit proves TODAY (`proven0`,
 * `proven_prev`, `exists`). Output goes to the file named by KV_OUT
 * (appended); unset, the probe is silent and the compile is untouched.
 *
 *   gcc -O2 -std=gnu11 -Ilib -Isrc -o build/kv/pcrec-kv cli/main.c \
 *       docs/dev/kvcensus/kvprobe.c build/libpcrec.a \
 *       -Wl,--wrap=pcrec_memfn_define -Wl,--wrap=pcrec_memfn_emit
 *
 * Fields: SITE door art_seq id op form handoff site_kind reverse end_back
 *         pred_need window_stated move_back overshoot pred_terms
 *         npred preds npspan pspans head_max ask_rc exists proven0 proven_prev
 * A term list is `;`-joined `kind:offset:need:payload`, payload the 32-byte
 * set in hex (SET) or `run_hex/mask_hex` (RUN, mask `-` when exact). A pred
 * list is `|`-joined `need{terms}`.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen/memfn_sites.h"

uint32_t __real_pcrec_memfn_define(Ctx *cx, DelegSite id, const mf_site *s,
                                   const mf_hooks *h, StrBuf *file);
void __real_pcrec_memfn_emit(Ctx *cx, DelegSite id, const mf_site *s,
                             const mf_hooks *h, StrBuf *body);

static const char *op_name(mf_op o)
{
    switch (o) {
    case MF_OP_FIND: return "FIND";
    case MF_OP_SKIP: return "SKIP";
    case MF_OP_VERIFY: return "VERIFY";
    case MF_OP_ALL_PRESENT: return "ALL_PRESENT";
    default: return "OTHER";
    }
}

static const char *kind_name(unsigned k)
{
    static const char *const n[] = { "UNSTATED", "DFA_SCAN", "DFA_HAT", "HYB_PF",
                                     "VM_ATTEMPT", "DFA_ATTEMPT" };
    return k < sizeof n / sizeof n[0] ? n[k] : "?";
}

static const char *need_name(mf_need n)
{
    return n == MF_REQUIRED ? "R" : n == MF_OPTIONAL ? "O" : "U";
}

static void hex(FILE *f, const uint8_t *p, size_t n)
{
    for (size_t i = 0; i < n; i++) fprintf(f, "%02x", p[i]);
}

static void terms(FILE *f, const mf_pred *p)
{
    for (unsigned i = 0; i < p->nterm && i < MF_MAX_TERM; i++) {
        const mf_term *t = &p->term[i];
        if (i) fputc(';', f);
        fprintf(f, "%s:%d:%s:", t->kind == MF_T_SET ? "S" : t->kind == MF_T_RUN ? "R" : "F",
                (int)t->offset, need_name(t->need));
        if (t->kind == MF_T_SET) hex(f, t->set, 32);
        else if (t->kind == MF_T_RUN && t->run) {
            hex(f, t->run, t->run_len);
            fputc('/', f);
            if (t->mask) hex(f, t->mask, t->run_len); else fputc('-', f);
        }
    }
    if (!p->nterm) fputc('-', f);
}

static void preds(FILE *f, const mf_pred *ps, unsigned n)
{
    for (unsigned i = 0; i < n; i++) {
        if (i) fputc('|', f);
        fprintf(f, "%s{", need_name(ps[i].need));
        terms(f, &ps[i]);
        fputc('}', f);
    }
    if (!n) fputc('-', f);
}

static void record(Ctx *cx, const char *door, DelegSite id, const mf_site *s,
                   const mf_hooks *h)
{
    static const mf_art *last;
    static unsigned seq;
    const char *path = getenv("KV_OUT");
    if (!path) return;
    FILE *f = fopen(path, "a");
    if (!f) return;
    mf_art *art = pcrec_memfn_art(cx);
    if (art != last) { last = art; seq++; }
    mf_class cls;
    memset(&cls, 0, sizeof cls);
    int rc = mf_ask(art, s, h, &cls);
    fprintf(f, "SITE\t%s\t%u\t%s\t%s\t%d\t%d\t%s\t%u\t%u\t%s\t%u\t%d\t%u\t",
            door, seq, pcrec_deleg_sites[id].id, op_name(s->op), (int)s->form,
            (int)s->handoff, kind_name(s->site_kind), s->reverse, s->end_back,
            need_name(s->pred.need), s->pred.window_stated, (int)s->pred.move_back,
            (unsigned)s->pred.overshoot);
    terms(f, &s->pred);
    fprintf(f, "\t%u\t", s->npred);
    preds(f, s->preds, s->npred);
    fprintf(f, "\t%u\t", s->npspan);
    preds(f, s->pspans, s->npspan);
    fprintf(f, "\t%llu\t%d\t%u\t", (unsigned long long)s->head_max, rc, cls.exists);
    hex(f, cls.proven0, 32);
    fputc('\t', f);
    hex(f, cls.proven_prev, 32);
    fputc('\n', f);
    fclose(f);
}

uint32_t __wrap_pcrec_memfn_define(Ctx *cx, DelegSite id, const mf_site *s,
                                   const mf_hooks *h, StrBuf *file)
{
    record(cx, "define", id, s, h);
    return __real_pcrec_memfn_define(cx, id, s, h, file);
}

void __wrap_pcrec_memfn_emit(Ctx *cx, DelegSite id, const mf_site *s,
                             const mf_hooks *h, StrBuf *body)
{
    record(cx, "emit", id, s, h);
    __real_pcrec_memfn_emit(cx, id, s, h, body);
}
