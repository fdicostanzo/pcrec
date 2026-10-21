/* src/core/measures.c — [MEASURE-SET] M0 the MEASUREMENT SET a compile reads
 * (docs/design/measure_sets.md rev 3 §2, §3; docs/spec/measures.md): the
 * embedded store, the resolution of `--measures NAME|NAME@REV|FILE` (and of
 * nothing, which is the build's default), and the attempt's loaded set.
 *
 * The kind's own parse, checks, views and digest are the row's
 * (src/core/ks_measures.c, libc-only); the stop loop is the knowledge
 * module's (`pcrec_ks_resolve`, src/core/ksrc.c). This file adds what only
 * the library has: the store's pre-parse, the default pointer, and the
 * compile's error channel.
 *
 * THE DEFAULT (§3.4, RULED D166 addendum 2): a compile that names no set
 * reads the `DEFAULTS` row of its class, and at M0 there is one class, `idk`
 * (a compile that declares none), whose row names the LATEST committed set.
 * A build with no default (the stage-0 generator's library) loads nothing.
 *
 * A LOADED SET IS NOT A CONSULTED ONE. Loading fixes WHICH set the stamp
 * would name; the stamp is written only if a reader consulted it (§3.5, the
 * stamp render in src/gen/memfn_stamps.c), so loading moves no byte. */

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "core/ks_measures.h"
#include "core/ksrc.h"

/* One committed set's TEXT, `scripts/embed_text.sh`'s entry shape: the
 * name is `<id>@<rev>`. */
typedef struct {
    const char *name;
    const char *text;
    size_t      len;
} PcrecMeasStoreText;

/* The stage-0 library (the one `scripts/ksgen.c` links to write the
 * pre-parse) carries no store: it parses and never compiles. */
#ifdef PCREC_MEAS_STAGE0
static const PcrecMeasStoreText pcrec_meas_store[1];
static const KsMeasStoreEntry pcrec_meas_store_tbl[1];
static const KsMeasDefault pcrec_meas_defaults[1];
/* Variables, not enumerators: a loop bound that is the constant 0 is a
 * -Wtype-limits warning in this build. */
static const size_t PCREC_MEAS_NSTORE = 0, PCREC_MEAS_NDEFAULTS = 0;
#else
/* `pcrec_meas_store[]`: every committed set's text (make gen-measures). */
#include "measures_store.inc"
/* `pcrec_meas_store_tbl[]` (the same sets pre-parsed by the one reader, in
 * the same order) and `pcrec_meas_defaults[]` (`measure_store/DEFAULTS`). */
#include "measures_table.inc"
static const size_t
    PCREC_MEAS_NSTORE = sizeof pcrec_meas_store_tbl / sizeof *pcrec_meas_store_tbl,
    PCREC_MEAS_NDEFAULTS = sizeof pcrec_meas_defaults / sizeof *pcrec_meas_defaults;
#endif

/* The class every M0 compile is: none declared (§3.4). */
static const char meas_class_idk[] = "idk";

static void *meas_alloc(void *u, size_t n)
{
    return pcrec_arena_alloc(u, n);
}

size_t pcrec_meas_store_count(void)
{
    return PCREC_MEAS_NSTORE;
}

const KsMeasSet *pcrec_meas_store_set(size_t i, const char **text, size_t *len)
{
    if (i >= PCREC_MEAS_NSTORE) return NULL;
    if (text) *text = pcrec_meas_store[i].text;
    if (len) *len = pcrec_meas_store[i].len;
    return pcrec_meas_store_tbl[i].set;
}

const char *pcrec_meas_store_name(size_t i)
{
    return i < PCREC_MEAS_NSTORE ? pcrec_meas_store_tbl[i].name : NULL;
}

/* The store's set `id` at `rev` (0: its latest rev), or NULL. */
static const KsMeasSet *store_find(const char *id, size_t idlen, uint32_t rev)
{
    const KsMeasSet *best = NULL;
    for (size_t i = 0; i < PCREC_MEAS_NSTORE; i++) {
        const KsMeasSet *s = pcrec_meas_store_tbl[i].set;
        if (strlen(s->hdr[KS_MH_ID]) != idlen || memcmp(s->hdr[KS_MH_ID], id, idlen))
            continue;
        if (rev ? s->rev == rev : (!best || s->rev > best->rev)) best = s;
    }
    return best;
}

const char *pcrec_meas_default_for(const KsMeasSet *set)
{
    for (size_t i = 0; i < PCREC_MEAS_NDEFAULTS; i++)
        if (!strcmp(pcrec_meas_defaults[i].id, set->hdr[KS_MH_ID]) &&
            pcrec_meas_defaults[i].rev == set->rev)
            return pcrec_meas_defaults[i].cls;
    return "";
}

/* The resolver's view of the store, for stop S3: a NAME the store defines,
 * at the pinned rev when there is one. */
typedef struct {
    uint32_t rev;
} MeasWalk;

static bool meas_has(void *ctx, KsAt at, const char *name)
{
    const MeasWalk *mw = ctx;
    return at == KS_AT_STORE && store_find(name, strlen(name), mw->rev) != NULL;
}

static int meas_fail(pcrec_error *err, const char *fmt, ...)
    __attribute__((format(printf, 2, 3)));
static int meas_fail(pcrec_error *err, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(err->msg, sizeof err->msg, fmt, ap);
    va_end(ap);
    return -1;
}

/* §3.3's shadow rule, keyed on (id, rev): a set from a file may carry a
 * committed id only as THAT committed set, values and all, so a stamp naming
 * `id@rev` always names what the store holds. */
static int shadow_check(const KsMeasSet *set, const char *where, pcrec_error *err)
{
    const char *id = set->hdr[KS_MH_ID];
    const KsMeasSet *same = store_find(id, strlen(id), set->rev);
    if (same) {
        if (same->digest == set->digest) return 0;
        return meas_fail(err, "%s: %s@%u is a committed measurement set with "
                         "different values; rename the set", where, id, set->rev);
    }
    if (store_find(id, strlen(id), 0))
        return meas_fail(err, "%s: measurement set id '%s' has no committed rev %u; "
                         "rename the set", where, id, set->rev);
    return 0;
}

int pcrec_meas_find(Arena *a, const char *ref, const char *const *dirs,
                    PcrecMeasHit *out, pcrec_error *err)
{
    KsAlloc al = { meas_alloc, a };
    KsErr kerr = { { 0 } };
    size_t nlen, ndirs = 0;
    uint32_t rev;
    memset(out, 0, sizeof *out);
    if (!ref) {
        for (size_t i = 0; i < PCREC_MEAS_NDEFAULTS; i++)
            if (!strcmp(pcrec_meas_defaults[i].cls, meas_class_idk)) {
                const char *id = pcrec_meas_defaults[i].id;
                out->set = store_find(id, strlen(id), pcrec_meas_defaults[i].rev);
                out->stop = "the build's default";
                if (!out->set)
                    return meas_fail(err, "internal error: the default measurement "
                                     "set %s@%u is not in the store", id,
                                     pcrec_meas_defaults[i].rev);
            }
        return 0;
    }
    while (dirs && dirs[ndirs]) ndirs++;
    switch (pcrec_ks_classify_ref(pcrec_ks_measures.flag_classify, true, ref, &nlen, &rev)) {
    case KS_REQ_FILE:
        if (pcrec_ks_meas_read_file(&al, ref, &out->set, &kerr))
            return meas_fail(err, "%s", kerr.msg);
        out->stop = ref;
        return shadow_check(out->set, ref, err);
    case KS_REQ_NAME:
        break;
    case KS_REQ_BAD:
    case KS_REQ_PATH:
        return meas_fail(err, "--measures '%s' is not a set name or a file", ref);
    }
    {
        char *name = pcrec_arena_alloc(a, nlen + 1);
        MeasWalk mw = { rev };
        KsWalk kw = {
            .kind = &pcrec_ks_measures, .dirs = dirs, .ndirs = ndirs,
            .s1 = false, .srcdir = "", .alloc = &al, .ctx = &mw,
            .has = meas_has, .note = NULL, .err = &kerr
        };
        KsHit hit;
        memcpy(name, ref, nlen);
        switch (pcrec_ks_resolve(&kw, KS_REQ_NAME, name, 0, &hit)) {
        case KS_RES_ERROR:
            return meas_fail(err, "%s", kerr.msg);
        case KS_RES_ABSENT:
            if (rev && store_find(name, nlen, 0))
                return meas_fail(err, "measurement set '%s' has no committed rev %u "
                                 "(searched: %s)", name, rev, pcrec_ks_stops_text(&kw));
            pcrec_ks_refuse_unknown(&kw, ref);
            return meas_fail(err, "%s", kerr.msg);
        case KS_RES_FOUND:
            break;
        }
        if (hit.at == KS_AT_STORE) {
            out->set = store_find(name, nlen, rev);
            out->stop = "the built-in store";
            return 0;
        }
        out->set = hit.doc;
        out->stop = hit.path;
        if (rev && out->set->rev != rev)
            return meas_fail(err, "%s carries %s@%u, not %s", hit.path, name,
                             out->set->rev, ref);
        return shadow_check(out->set, hit.path, err);
    }
}

void pcrec_meas_resolve(Ctx *cx)
{
    PcrecMeasHit h;
    pcrec_error e = { 0 };
    KsAlloc al = { meas_alloc, &cx->arena };
    if (pcrec_meas_find(&cx->arena, cx->opt->measures, cx->opt->measures_dirs, &h, &e))
        pcrec_ctx_fail(cx, 0, "%s", e.msg);
    cx->job->meas = h.set;
    cx->job->meas_stamp = h.set ? pcrec_ks_meas_stamp(&al, h.set) : NULL;
}
