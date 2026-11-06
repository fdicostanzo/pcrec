/* docs/dev/lanes/r33_sim/probe.c -- R-33's SITE PROBE (a study; never built by make).
 *
 * Linked into a scratch copy of the traced pcrec (MF_TRACE + PCREC_CAND_TRACE) with
 *   -Wl,--wrap=pcrec_mf_define,--wrap=pcrec_mf_emit,--wrap=pcrec_mf_art_begin
 * (build.sh), so NO file under src/ or memfn/src/ changes. For every site pcrec
 * hands the kit it writes one stderr line `R33 {json}` AFTER the kit's define returns
 * (so the kit's MFTRACE records for that define come before it, and pcrec's own
 * MFROUTED line right after it): the site's stated facts (frame, the predicate's
 * terms, the window alternatives and their spans) and, for a window site and for
 * each window-stating FUNC part, TODAY's phase-1 decision through the public query
 * mf_wdecide (stop, stop set, plan, path). At each art's begin it writes the art's
 * byte-rate table once (`R33RATE`), the table every kit mass reads. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "memfn.h"

int  __real_pcrec_mf_define(mf_art *, const mf_site *, const mf_hooks *, mf_sink *,
                            uint32_t *);
int  __real_pcrec_mf_emit(mf_art *, const mf_site *, const mf_hooks *, mf_sink *,
                          mf_sink *, mf_result *);
mf_art *__real_pcrec_mf_art_begin(mf_arena *, const char *, uint32_t, uint64_t,
                                  const mf_measures *, const mf_analysis *);

static unsigned n_art;
static const mf_art *arts[64];

static unsigned art_no(const mf_art *a)
{
    for (unsigned i = 0; i < n_art && i < 64; i++)
        if (arts[i] == a) return i + 1;
    return 0;
}

mf_art *__wrap_pcrec_mf_art_begin(mf_arena *ar, const char *prefix, uint32_t policy,
                                  uint64_t denies, const mf_measures *ms,
                                  const mf_analysis *an)
{
    mf_art *a = __real_pcrec_mf_art_begin(ar, prefix, policy, denies, ms, an);
    if (n_art < 64) arts[n_art] = a;
    n_art++;
    const uint32_t *rate = NULL;
    int present = -1;
    unsigned long long digest = 0;
    for (uint16_t i = 0; an && an->kinds && i < an->nkinds; i++)
        if (an->kinds[i].tag && !strcmp(an->kinds[i].tag, "byte-rate")) {
            present = an->kinds[i].present;
            digest = (unsigned long long)an->kinds[i].digest; /* mf_akind lost prov at unit 1g (MF_SITE_ABI 22) */
            if (present == MF_KIND_PRESENT) rate = an->kinds[i].payload;
        }
    fprintf(stderr, "R33RATE art=%u present=%d digest=%016llx rate=", n_art, present, digest);
    if (rate)
        for (int b = 0; b < 256; b++) fprintf(stderr, "%s%u", b ? "," : "", rate[b]);
    else
        fputs("none", stderr);
    fputc('\n', stderr);
    return a;
}

static void hex(FILE *f, const uint8_t *p, size_t n)
{
    fputc('"', f);
    for (size_t i = 0; i < n; i++) fprintf(f, "%02x", p[i]);
    fputc('"', f);
}

static void alts_json(FILE *f, unsigned nalt, const mf_walt *alts, unsigned wfloor)
{
    fprintf(f, "\"wfloor\":%u,\"alts\":[", wfloor);
    for (unsigned a = 0; a < nalt; a++) {
        fprintf(f, "%s{\"entry\":%u,\"spans\":[", a ? "," : "", alts[a].entry);
        for (unsigned i = 0; i < alts[a].nspan; i++) {
            const mf_wspan *w = &alts[a].spans[i];
            fprintf(f, "%s{\"start\":%d,\"len\":%u,\"verify\":%u,\"core\":%u,\"core_lo\":%u,"
                       "\"core_len\":%u,\"sets\":[",
                    i ? "," : "", (int)w->start, w->len, w->verify, w->core, w->core_lo,
                    w->core_len);
            for (unsigned j = 0; j < w->len; j++) {
                if (j) fputc(',', f);
                hex(f, w->set[j], 32);
            }
            fputs("]}", f);
        }
        fputs("]}", f);
    }
    fputc(']', f);
}

static void wr_json(FILE *f, const mf_art *art, const mf_site *s)
{
    mf_wreply r;
    memset(&r, 0, sizeof r);
    int rc = pcrec_mf_wdecide(art, s, &r);
    fprintf(f, "\"wr\":{\"rc\":%d", rc);
    if (!rc) {
        fprintf(f, ",\"alt\":%u,\"reseed\":%u,\"has_stop\":%u,\"stop\":%d,\"stop_set\":",
                r.alt, r.reseed, r.has_stop, (int)r.stop);
        hex(f, r.stop_set, 32);
        fputs(",\"plan\":[", f);
        for (unsigned i = 0; i < r.nplan; i++)
            fprintf(f, "%s[%d,%u]", i ? "," : "", (int)r.plan[i], r.plan_term[i]);
        fprintf(f, "],\"pinned\":%u,\"run_stated\":%u,\"run_member\":%d,\"run_lo\":%d,"
                   "\"run_len\":%u,\"path\":\"%s\"",
                r.pinned, r.run_stated, (int)r.run_member, (int)r.run_lo, r.run_len, r.path);
    }
    fputc('}', f);
}

static void pred_json(FILE *f, const mf_pred *p)
{
    fprintf(f, "{\"fn_ref\":%u,\"nterm\":%u,\"terms\":[", p->fn_ref, p->nterm);
    for (unsigned i = 0; i < p->nterm && i < MF_MAX_TERM; i++) {
        const mf_term *t = &p->term[i];
        fprintf(f, "%s{\"kind\":%d,\"offset\":%d,\"need\":%d", i ? "," : "", t->kind,
                (int)t->offset, t->need);
        if (t->kind == MF_T_SET) { fputs(",\"set\":", f); hex(f, t->set, 32); }
        if (t->kind == MF_T_RUN && t->run) {
            fputs(",\"run\":", f);
            hex(f, t->run, t->run_len);
            if (t->mask) { fputs(",\"mask\":", f); hex(f, t->mask, t->run_len); }
        }
        fputc('}', f);
    }
    fputs("]", f);
    if (p->nalt) { fputc(',', f); alts_json(f, p->nalt, p->alts, p->wfloor); }
    fputc('}', f);
}

static void site_line(const char *via, int rc, uint32_t handle, mf_art *art,
                      const mf_site *s)
{
    FILE *f = stderr;
    fprintf(f, "R33 {\"via\":\"%s\",\"rc\":%d,\"art\":%u,\"site\":%u,\"form\":%d,\"op\":%d,"
               "\"handoff\":%d,\"site_kind\":%u,\"policy\":%u,\"span_hi\":%llu,\"npspan\":%u,"
               "\"pred\":",
            via, rc, art_no(art), handle, s->form, s->op, s->handoff, s->site_kind, s->policy,
            (unsigned long long)s->span_hi, s->npspan);
    pred_json(f, &s->pred);
    fputs(",\"preds\":[", f);
    for (unsigned i = 0; i < s->npred && s->preds; i++) {
        if (i) fputc(',', f);
        const mf_pred *p = &s->preds[i];
        if (p->nalt) {
            /* a FUNC part's own window statement: today's decision through the
               same query, on a FIND/FUNC/RETURN site carrying only the part's facts */
            mf_site t;
            memset(&t, 0, sizeof t);
            t.abi = s->abi; t.form = MF_FORM_FUNC; t.op = MF_OP_FIND; t.handoff = MF_H_RETURN;
            t.pred.fn_ref = p->fn_ref; t.pred.plan_hint = MF_NO_PRED;
            t.span_hi = MF_SPAN_UNBOUNDED; t.policy = s->policy; t.denies = s->denies;
            t.opts = s->opts; t.body = s->body; t.site_kind = s->site_kind;
            t.ret_pred = MF_NO_PRED;
            t.nalt = p->nalt; t.alts = p->alts; t.wfloor = p->wfloor;
            fputs("{\"part\":", f);
            pred_json(f, p);
            fputc(',', f);
            wr_json(f, art, &t);
            fputc('}', f);
        } else {
            pred_json(f, p);
        }
    }
    fputc(']', f);
    if (s->nalt) {
        fputc(',', f);
        alts_json(f, s->nalt, s->alts, s->wfloor);
        fputc(',', f);
        wr_json(f, art, s);
    }
    fputs("}\n", f);
}

int __wrap_pcrec_mf_define(mf_art *art, const mf_site *s, const mf_hooks *h, mf_sink *sk,
                           uint32_t *handle)
{
    int rc = __real_pcrec_mf_define(art, s, h, sk, handle);
    site_line("define", rc, handle ? *handle : 0, art, s);
    return rc;
}

int __wrap_pcrec_mf_emit(mf_art *art, const mf_site *s, const mf_hooks *h, mf_sink *body,
                         mf_sink *fs, mf_result *res)
{
    int rc = __real_pcrec_mf_emit(art, s, h, body, fs, res);
    site_line("emit", rc, 0, art, s);
    return rc;
}
