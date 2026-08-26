/*
 * ts4_driver.c — [TS-4] / [DD-14.FB], the matcher's own 128 KB-thread case.
 *
 * WHAT THIS IS ABOUT, AND WHY IT IS NOT [TS-2]'s QUESTION. [TS-2] and [TS-3]
 * ask whether concurrent calls RACE. This asks something disjoint: whether ONE
 * call FITS. A generated matcher's run state is a local of whichever entry the
 * caller called, so an artifact whose resume stack and trail are sized for
 * depth carries that storage on the C stack — and docs/dev/plan.md's [TS-4]
 * row names the ceiling it has to fit under, musl's default 128 KB thread
 * stack. plan.md's [TS-4] and [DD-10] rows are both about the COMPILER's own
 * recursion (compile_ast, clo_visit); this is the second, disjoint instance of
 * the same concern, in the EMITTED matcher, and design §3 of
 * docs/design/frame_buffer_design.md MEASURES it live rather than prospective.
 *
 * THE TWO ARMS.
 *
 *   default   `<prefix>_search` on a 128 KB thread. On a call-bearing,
 *             depth-unbounded artifact this OVERFLOWS THE THREAD STACK and the
 *             process dies of SIGSEGV. That is K33 (docs/dev/known_issues.md),
 *             it is a live defect against a shipped promise — spec §5.3's
 *             concurrency contract — and D73 keeps the stamped default that
 *             causes it, so this arm is EXPECTED to die until that ruling
 *             changes. The runner scores it as a pinned known state, not as a
 *             pass; if it ever stops dying, the runner FAILS, because the
 *             record is then out of date.
 *
 *   buffered  `<prefix>_search_in` with the same subject on the same 128 KB
 *             thread, storage supplied from the HEAP. This must return a
 *             match. It is the remedy, and it is the reason the default arm's
 *             death is a documented limitation rather than an open wound.
 *
 * The subject is a^n b^n at the n this artifact's stamped capacity supports
 * (MEASURED: 342, a 684-byte subject), so the default arm dies on a subject
 * it would otherwise MATCH — the failure is the stack, not the pattern.
 *
 * Prints one line to stdout and exits 0 on a clean run; a stack overflow kills
 * the process before any line is printed, which is what the runner reads.
 */
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

#define TS4_STACK_BYTES (128 * 1024)   /* musl's default thread stack size */
#define TS4_N 342                      /* the stamped default's largest match */
/* [OPT-1] the shallow arm's depth: the smallest subject the pattern matches at
 * all, and the one spec §5.3 used to name as still faulting. */
#define TS4_SHALLOW_N 1

/* The caller-supplied regions, on the HEAP — the point of the buffered arm is
 * that this storage is NOT on the 128 KB stack. Sized in frames/entries from
 * the artifact's own macros, generously above what depth 342 needs (686 frames
 * and 3,073 trail entries, MEASURED). */
#define TS4_FRAMES 65536
#define TS4_TRAIL  262144

struct arg {
    const unsigned char *subject;
    size_t               len;
    int                  buffered;
    void                *frames;
    void                *trail;
    int                  rc;
};

static void *ts4_body(void *p)
{
    struct arg *a = p;
    ptrdiff_t caps[RX_NCAPS][2];
    if (!a->buffered) {
        a->rc = rx_search(a->subject, a->len, 0, caps);
    } else {
        rx_buffers b;
        b.frames = a->frames; b.nframes = TS4_FRAMES;
        b.trail  = a->trail;  b.ntrail  = TS4_TRAIL;
        a->rc = rx_search_in(a->subject, a->len, 0, caps, &b);
    }
    return NULL;
}

int main(int argc, char **argv)
{
    pthread_attr_t attr;
    pthread_t th;
    struct arg a;
    unsigned char *s;
    size_t n = TS4_N;

    if (argc != 2 || (strcmp(argv[1], "default") != 0
                   && strcmp(argv[1], "buffered") != 0
                   && strcmp(argv[1], "shallow") != 0)) {
        fprintf(stderr, "usage: %s default|buffered|shallow\n", argc > 0 ? argv[0] : "ts4");
        return 2;
    }
    /* [OPT-1] the shallow arm differs from `default` in the SUBJECT and in
     * nothing else: same entry, same thread, same artifact. */
    if (strcmp(argv[1], "shallow") == 0) n = TS4_SHALLOW_N;

    s = malloc(2 * n + 1);
    if (!s) { fprintf(stderr, "ts4: out of memory\n"); return 2; }
    memset(s, 'a', n); memset(s + n, 'b', n); s[2 * n] = 0;

    a.subject = s; a.len = 2 * n; a.rc = -99;
    a.buffered = strcmp(argv[1], "buffered") == 0;
    a.frames = NULL; a.trail = NULL;
    if (a.buffered) {
        if (RX_RESUME_FRAME_SIZE == 0 || RX_TRAIL_FRAME_SIZE == 0) {
            fprintf(stderr, "ts4: this artifact reports no resume stack to size"
                            " — the buffered arm needs a VM artifact\n");
            free(s);
            return 2;
        }
        a.frames = malloc((size_t)TS4_FRAMES * (size_t)RX_RESUME_FRAME_SIZE);
        a.trail  = malloc((size_t)TS4_TRAIL  * (size_t)RX_TRAIL_FRAME_SIZE);
        if (!a.frames || !a.trail) {
            fprintf(stderr, "ts4: out of memory for the caller buffers\n");
            free(a.frames); free(a.trail); free(s);
            return 2;
        }
    }

    if (pthread_attr_init(&attr) != 0) { fprintf(stderr, "ts4: attr_init\n"); return 2; }
    if (pthread_attr_setstacksize(&attr, TS4_STACK_BYTES) != 0) {
        fprintf(stderr, "ts4: setstacksize(%d) refused\n", TS4_STACK_BYTES);
        return 2;
    }
    if (pthread_create(&th, &attr, ts4_body, &a) != 0) {
        fprintf(stderr, "ts4: pthread_create\n");
        return 2;
    }
    pthread_join(th, NULL);
    pthread_attr_destroy(&attr);

    printf("%s rc=%d n=%zu stack=%d\n", argv[1], a.rc, n, TS4_STACK_BYTES);
    free(a.frames); free(a.trail); free(s);
    return 0;
}
