/* shim.c -- [ARTREV] the one TU every arm is compiled through.
 *
 * Same shape as pcrec-bench's testees/pcrec/shim.c: it #includes the arm's
 * artifact.c (found via -I<armdir>) and exports flat <stddef.h>-typed art_*
 * wrappers, so the drivers never re-declare pcrec's ABI.  Built with the ONE
 * fixed command line `$CC -O2 -fPIC -I<armdir> -DARTREV_PFX=<p> -DARTREV_PFXU=<P>
 * [-DARTREV_HAVE_IN=1] shim.c <driver>.c`.  Every exported call shape of
 * docs/spec/match_api.md is wrapped: <p>_search(_in), _match(_in),
 * _match_caps(_in), _next_pos, _valid_upto.  ARTREV_HAVE_IN is set by `gen`
 * from the artifact's own header (does it publish <P>_BUFFER_ALIGN, i.e. the
 * `_in` entries exist; a DFA artifact gets a NULL descriptor).
 */
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "artifact.c"

#define ART_CAT2(a, b) a##b
#define ART_CAT(a, b) ART_CAT2(a, b)
#define P(x)  ART_CAT(ARTREV_PFX, x)
#define PU(x) ART_CAT(ARTREV_PFXU, x)

typedef P(_ctx) art_ctx_t;
typedef P(_buffers) art_buffers_t;

int art_ncaps(void) { return (int)PU(_NCAPS); }
int art_have_in(void)
{
#ifdef ARTREV_HAVE_IN
    return 1;
#else
    return 0;
#endif
}

int art_search(const unsigned char *s, size_t n, size_t pos, ptrdiff_t (*caps)[2])
{ return P(_search)(s, n, pos, caps); }

static void art_ctx(art_ctx_t *c, const unsigned char *s, size_t n, size_t pos)
{
    memset(c, 0, sizeof *c);
    c->subject = s;
    c->len = n;
    c->pos = pos;
}

ptrdiff_t art_match(const unsigned char *s, size_t n, size_t pos)
{ art_ctx_t c; art_ctx(&c, s, n, pos); return P(_match)(&c); }

ptrdiff_t art_match_caps(const unsigned char *s, size_t n, size_t pos, ptrdiff_t (*caps)[2])
{ art_ctx_t c; art_ctx(&c, s, n, pos); return P(_match_caps)(&c, caps); }

size_t art_next_pos(const unsigned char *s, size_t n, size_t pos)
{ return P(_next_pos)(s, n, pos); }

size_t art_valid_upto(const unsigned char *s, size_t n, size_t pos)
{ return P(_valid_upto)(s, n, pos); }

#ifdef ARTREV_HAVE_IN
/* The stamped default capacities, in caller storage (match_api.md 10).  The
 * shrunken-resource identity mode (identity.py) overrides the COUNTS through
 * art_set_bufs: the storage stays at the stamped size, only nframes/ntrail the
 * entry is told about shrink (0 and 1 are the cases a frame- or trail-dropping
 * twin can get wrong -- lane rvA09, 2026-10-06). */
static art_buffers_t art_bufs;
static void *art_fr, *art_tr;
static long art_nf = -1, art_nt = -1;
void art_set_bufs(long nframes, long ntrail) { art_nf = nframes; art_nt = ntrail; }
static art_buffers_t *art_get_buffers(void)
{
    if (PU(_RESUME_FRAME_SIZE) == 0) return NULL;   /* a DFA artifact takes no buffers (match_api 10.4) */
    if (!art_fr) {
        if (posix_memalign(&art_fr, 64, (size_t)PU(_RESUME_FRAMES) * PU(_RESUME_FRAME_SIZE) + 64) ||
            posix_memalign(&art_tr, 64, (size_t)PU(_TRAIL_FRAMES) * PU(_TRAIL_FRAME_SIZE) + 64))
            abort();
        art_bufs.frames = art_fr;  art_bufs.nframes = PU(_RESUME_FRAMES);
        art_bufs.trail = art_tr;   art_bufs.ntrail = PU(_TRAIL_FRAMES);
    }
    art_bufs.nframes = art_nf >= 0 ? (size_t)art_nf : PU(_RESUME_FRAMES);
    art_bufs.ntrail  = art_nt >= 0 ? (size_t)art_nt : PU(_TRAIL_FRAMES);
    return &art_bufs;
}
int art_search_in(const unsigned char *s, size_t n, size_t pos, ptrdiff_t (*caps)[2])
{ return P(_search_in)(s, n, pos, caps, art_get_buffers()); }
ptrdiff_t art_match_in(const unsigned char *s, size_t n, size_t pos)
{ art_ctx_t c; art_ctx(&c, s, n, pos); return P(_match_in)(&c, art_get_buffers()); }
ptrdiff_t art_match_caps_in(const unsigned char *s, size_t n, size_t pos, ptrdiff_t (*caps)[2])
{ art_ctx_t c; art_ctx(&c, s, n, pos); return P(_match_caps_in)(&c, caps, art_get_buffers()); }
#else
void art_set_bufs(long nframes, long ntrail) { (void)nframes; (void)ntrail; }
int art_search_in(const unsigned char *s, size_t n, size_t pos, ptrdiff_t (*caps)[2])
{ (void)s; (void)n; (void)pos; (void)caps; return -1000; }
ptrdiff_t art_match_in(const unsigned char *s, size_t n, size_t pos)
{ (void)s; (void)n; (void)pos; return -1000; }
ptrdiff_t art_match_caps_in(const unsigned char *s, size_t n, size_t pos, ptrdiff_t (*caps)[2])
{ (void)s; (void)n; (void)pos; (void)caps; return -1000; }
#endif

#ifdef ARTREV_HAVE_PF
/* The internal prefilter a hybrid artifact searches through (window-start
 * differential, driver_pf.c): returns what rx_prefilter returns, window[0] the
 * start it proposes.  Only compiled when identity.py found a `static int
 * <p>_prefilter(` in the pinned artifact. */
int art_pf(const unsigned char *s, size_t n, size_t pos, ptrdiff_t (*w)[2])
{ return P(_prefilter)(s, n, pos, w); }
#endif
