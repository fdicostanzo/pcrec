/* tests/core/memgate/mg_drv.c — memgate's per-compile driver ([ARENA-SCOPES] T1).
 *
 * Reads lines "RAISE\tFEATURES\tENGINE\tPATFILE" on stdin, runs one
 * `pcrec_compile` per line, prints one result line per input line.
 *
 * -DMG_PEAK (linked against an alloc_inject.h build, with
 *   -Wl,--wrap=pcrec_arena_alloc -Wl,--wrap=pcrec_arena_free):
 *   "PEAK RC LIVE_AFTER ATT_HW OTH_HW UPEAK" where PEAK is the compile's peak
 *   live heap in REQUESTED bytes (the size each live block the library holds
 *   was asked for, kept per pointer), UPEAK the same peak read by
 *   malloc_usable_size (INFORMATIONAL: it moves with the allocator's rounding
 *   and mmap/brk choice under a different heap history, lane arenabuild2's
 *   ruling R-2), and the arena BLOCK bytes, in REQUESTED block size, split BY
 *   ARENA IDENTITY: ATT_HW is the high-water of
 *   the block bytes held by attempt arenas (an Arena that is its Ctx's own
 *   `&cx->arena`), OTH_HW the same for every other arena (the memo, clskit's,
 *   a scope's child). A new block is seen as `a->head` moving across one
 *   `pcrec_arena_alloc` call; an arena's bytes are dropped when it reaches
 *   `pcrec_arena_free` through the wrap. A call made from inside arena.o is
 *   not wrapped (GNU ld wraps undefined references only), so a child arena
 *   released by arena.c's own registry walk stays counted in OTH: OTH is
 *   informational, ATT is the gate (design G2a).
 * -DMG_INSTR (linked against the plain -O2 library): "INSTR RC" where INSTR
 *   is the user-mode instruction count (perf_event_open, exclude_kernel)
 *   around the one `pcrec_compile` call. Needs ADDR_NO_RANDOMIZE (the count
 *   moves ~2% with the layout): exits 3 without it.
 *
 * Deterministic by construction (no wall clock; instr under ASLR off); memgate.py's noise read runs
 * a side against a SECOND directory of the same binaries to prove it. */
#include <malloc.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "pcrec.h"

#ifdef MG_PEAK
#include "core/internal.h"

static long long live, peak, ulive, upeak;

/* The requested size of every live library block, keyed by its address
 * (open addressing, linear probing, backward-shift deletion; this file is
 * not injected, so its own malloc is the real one). */
static struct { void *p; size_t n; } *sz_tab;
static size_t sz_cap, sz_used;

static size_t sz_home(const void *p) { return ((uintptr_t)p >> 4) * 0x9E3779B97F4A7C15ull & (sz_cap - 1); }

static void sz_put(void *p, size_t n);
static void sz_grow(void)
{
    size_t oc = sz_cap;
    __typeof__(sz_tab) ot = sz_tab;
    sz_cap = oc ? oc * 2 : 1 << 16;
    sz_tab = calloc(sz_cap, sizeof *sz_tab);
    if (!sz_tab) { perror("memgate"); exit(2); }
    sz_used = 0;
    for (size_t i = 0; i < oc; i++)
        if (ot[i].p) sz_put(ot[i].p, ot[i].n);
    free(ot);
}
static void sz_put(void *p, size_t n)
{
    if ((sz_used + 1) * 2 > sz_cap) sz_grow();
    size_t h = sz_home(p);
    while (sz_tab[h].p && sz_tab[h].p != p) h = (h + 1) & (sz_cap - 1);
    if (!sz_tab[h].p) sz_used++;
    sz_tab[h].p = p;
    sz_tab[h].n = n;
}
/* Removes `p`, returning its requested size (0 if unknown). */
static size_t sz_take(void *p)
{
    if (!sz_cap) return 0;
    size_t h = sz_home(p);
    while (sz_tab[h].p && sz_tab[h].p != p) h = (h + 1) & (sz_cap - 1);
    if (!sz_tab[h].p) return 0;
    size_t n = sz_tab[h].n;
    sz_used--;
    for (size_t i = h, j = h;;) {   /* backward-shift deletion */
        sz_tab[i].p = NULL;
        for (;;) {
            j = (j + 1) & (sz_cap - 1);
            if (!sz_tab[j].p) return n;
            size_t k = sz_home(sz_tab[j].p);
            if (i <= j ? (i < k && k <= j) : (i < k || k <= j)) continue;
            break;
        }
        sz_tab[i] = sz_tab[j];
        i = j;
    }
}

/* Counts a block of `n` requested bytes the library now holds and raises
 * both peaks. */
static void *add(void *p, size_t n)
{
    if (p) {
        sz_put(p, n);
        live += (long long)n;
        if (live > peak) peak = live;
        ulive += (long long)malloc_usable_size(p);
        if (ulive > upeak) upeak = ulive;
    }
    return p;
}
/* Uncounts a block the library is giving back. */
static void drop(void *p)
{
    if (!p) return;
    live -= (long long)sz_take(p);
    ulive -= (long long)malloc_usable_size(p);
}
void *pcrec_inject_malloc_at(size_t n, const char *f, int l) { (void)f; (void)l; return add(malloc(n), n); }
void *pcrec_inject_calloc_at(size_t a, size_t b, const char *f, int l) { (void)f; (void)l; return add(calloc(a, b), a * b); }
void *pcrec_inject_realloc_at(void *p, size_t n, const char *f, int l)
{
    (void)f; (void)l;
    long long o = p ? (long long)malloc_usable_size(p) : 0;
    void *q = realloc(p, n);
    if (q) {
        if (p) { live -= (long long)sz_take(p); ulive -= o; }
        add(q, n);
    }
    return q;
}
char *pcrec_inject_strdup_at(const char *s, const char *f, int l) { (void)f; (void)l; return add(strdup(s), strlen(s) + 1); }
void pcrec_inject_free_at(void *p, const char *f, int l)
{
    (void)f; (void)l;
    drop(p);
    free(p);
}

/* The per-arena block bytes, keyed by the Arena's address (open addressing;
 * a compile holds a handful of arenas at once). */
#define MG_NARENA 4096
static struct { const Arena *a; long long bytes; bool att; } tab[MG_NARENA];
static long long att_live, att_hw, oth_live, oth_hw;

/* The table slot for `a`, claimed on first sight. */
static size_t slot(const Arena *a)
{
    size_t h = ((uintptr_t)a >> 4) % MG_NARENA;
    size_t probes = 0;
    while (tab[h].a && tab[h].a != a) {
        if (++probes >= MG_NARENA) {   /* a full table would probe forever (r104 MEMGATE-6) */
            fprintf(stderr, "mg_drv: more than %d distinct Arena addresses in one compile; raise MG_NARENA\n", MG_NARENA);
            abort();
        }
        h = (h + 1) % MG_NARENA;
    }
    tab[h].a = a;
    return h;
}

void *__real_pcrec_arena_alloc(Arena *a, size_t sz);
void __real_pcrec_arena_free(Arena *a);

/* Allocates through the real arena and charges a newly opened block to the
 * arena's class (attempt or other). */
void *__wrap_pcrec_arena_alloc(Arena *a, size_t sz)
{
    ABlock *h0 = a->head;
    void *p = __real_pcrec_arena_alloc(a, sz);
    if (a->head != h0) {
        size_t s = slot(a);
        tab[s].att = a->cx && a == &a->cx->arena;
        long long n = (long long)(sizeof(ABlock) + a->head->cap);   /* the block the arena requested (R-2) */
        tab[s].bytes += n;
        if (tab[s].att) { att_live += n; if (att_live > att_hw) att_hw = att_live; }
        else { oth_live += n; if (oth_live > oth_hw) oth_hw = oth_live; }
    }
    return p;
}

/* Drops the arena's charged block bytes, then frees it for real. */
void __wrap_pcrec_arena_free(Arena *a)
{
    size_t s = slot(a);
    if (tab[s].att) att_live -= tab[s].bytes;
    else oth_live -= tab[s].bytes;
    tab[s].bytes = 0;
    __real_pcrec_arena_free(a);
}
#endif

#ifdef MG_INSTR
#include <linux/perf_event.h>
#include <sys/personality.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

/* A user-mode instruction counter on this thread, disabled until armed. */
static int instr_fd(void)
{
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof pe);
    pe.type = PERF_TYPE_HARDWARE;
    pe.size = sizeof pe;
    pe.config = PERF_COUNT_HW_INSTRUCTIONS;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;
    int fd = (int)syscall(SYS_perf_event_open, &pe, 0, -1, -1, 0);
    if (fd < 0) { perror("perf_event_open"); exit(2); }
    return fd;
}
#endif

/* The whole file at `path`, NUL-terminated (the pattern bytes). */
static char *slurp(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *s = malloc((size_t)n + 1);
    if (!s || fread(s, 1, (size_t)n, f) != (size_t)n) { fclose(f); free(s); return NULL; }
    s[n] = 0;
    fclose(f);
    return s;
}

int main(void)
{
    char line[8192];
#ifdef MG_INSTR
    /* The count depends on the address-space layout: memgate.py starts this under `setarch -R`; refuse otherwise. */
    int pers = personality(0xffffffff);
    if (pers < 0 || !(pers & ADDR_NO_RANDOMIZE)) {
        fprintf(stderr, "mg_instr: ASLR is on; run under `setarch $(uname -m) -R`\n");
        return 3;
    }
    int fd = instr_fd();
#endif
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = 0;
        char *raise = strtok(line, "\t"), *feat = strtok(NULL, "\t");
        char *eng = strtok(NULL, "\t"), *pf = strtok(NULL, "\t");
        if (!pf) { printf("BADLINE\n"); fflush(stdout); continue; }
        char *pat = slurp(pf);
        if (!pat) { printf("NOPAT\n"); fflush(stdout); continue; }
        pcrec_options o;
        pcrec_default_options(&o);
        o.features = strcmp(feat, "-") ? feat : NULL;
        o.engine = atoi(eng);
        if (atoi(raise)) { o.max_emit_code_bytes = UINT64_MAX / 2; o.max_emit_bytes = UINT64_MAX / 2; }
        pcrec_output out;
        memset(&out, 0, sizeof out);
        pcrec_error err;
        memset(&err, 0, sizeof err);
#ifdef MG_PEAK
        live = peak = ulive = upeak = 0;
        if (sz_cap) memset(sz_tab, 0, sz_cap * sizeof *sz_tab);
        sz_used = 0;
        att_live = att_hw = oth_live = oth_hw = 0;
        memset(tab, 0, sizeof tab);
        int rc = pcrec_compile(pat, &o, &out, &err);
        if (rc == 0) pcrec_output_free(&out);
        printf("%lld %d %lld %lld %lld %lld\n", peak, rc, live, att_hw, oth_hw, upeak);
#else
        ioctl(fd, PERF_EVENT_IOC_RESET, 0);
        ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);
        int rc = pcrec_compile(pat, &o, &out, &err);
        ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);
        long long n = 0;
        if (read(fd, &n, sizeof n) != (ssize_t)sizeof n) n = -1;
        if (rc == 0) pcrec_output_free(&out);
        printf("%lld %d\n", n, rc);
#endif
        fflush(stdout);
        free(pat);
    }
    return 0;
}
