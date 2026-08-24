/* [DD-14] PROTOTYPE -- the §5 call mechanism, hand-written in pcrec's emitted
 * idiom and run against libpcre2.
 *
 * NOT emitted by pcrec and NOT a change to src/. Three matchers, written the
 * way §5 says the emitter should write them, so that the design's central
 * claims are executed rather than argued:
 *
 *   P1  ^((a)(?1)?(b))$    -- per-level capture save/restore across a
 *                             RECURSIVE call, at depth 1..N, with the
 *                             lexical occurrence SPLICED and the call site
 *                             taking the LINKAGE (§6.3's ruling, built)
 *   P2  ^(?(DEFINE)(?<g>a|ab))(?&g)c$
 *                          -- §3.2's atomicity discriminator and §5.5's
 *                             drawn cell: the follow fails after the callee's
 *                             FIRST success and must retreat INTO the
 *                             returned call
 *   P3  ^(a|(?1)a)$        -- §3.3's cell: n-1 nested recursions ALL ENTERED
 *                             AT OFFSET 0, which must MATCH "a"*n
 *   P4  ^(?(DEFINE)(?<g>x|xy))(?&g)(?&g)y$
 *                          -- §5.2's clobber sequence: call A, A returns,
 *                             call B, B fails, retreat into A's callee, A
 *                             returns AGAIN. A separate call_stack[] array
 *                             indexed by depth gets the WRONG return label
 *                             here; a call-as-a-frame does not.
 *
 * Everything below the matchers is §5 verbatim: the frame carries `call_ret`
 * and `call_top`; RX_CALL pushes a frame whose resume_label is rx_fail;
 * RX_RETURN does NOT pop; the fail label restores call_top and call_depth;
 * the capture save/restore is |W| trailed SELF-writes after the push and |W|
 * trailed restores read back at trail_mark + j.
 */
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define RX_NSLOTS        8
#define RX_RESUME_FRAMES 4096
#define RX_TRAIL_FRAMES  65536
#define RX_CALL_DEPTH    1024
#define PCREC_UNSET      ((ptrdiff_t)-1)
#define RX_R_FRAMES      ((ptrdiff_t)-3)
#define RX_R_RECURSE     ((ptrdiff_t)-5)     /* §5.6's new typed give-up */
#define CALL_TOP_NONE    ((unsigned)-1)

typedef struct {
    ptrdiff_t slot_values[RX_NSLOTS];
    struct { const void *resume_label; size_t resume_position;
             unsigned trail_mark;
             const void *call_ret;    /* §5.1: NULL on an ordinary frame */
             unsigned call_top;       /* the activation in force at push */
             unsigned call_mark; }    /* call_depth in force at push */
             resume_stack[RX_RESUME_FRAMES];
    struct { unsigned slot_index; ptrdiff_t saved_value; }
             trail[RX_TRAIL_FRAMES];
#ifdef BROKEN_ARRAY
    /* §5.2's REJECTED design, built so the bug is MEASURED rather than
     * derived: a separate stack of return labels indexed by call depth,
     * POPPED at the return, with each frame restoring only the DEPTH. */
    const void *call_stack[RX_CALL_DEPTH];
#endif
    unsigned resume_depth, trail_depth, call_top, call_depth;
} rx_run_state;

#define RX_TRAIL(slot_) do {                                            \
        if (run->trail_depth >= RX_TRAIL_FRAMES) return RX_R_FRAMES;    \
        run->trail[run->trail_depth].slot_index = (unsigned)(slot_);    \
        run->trail[run->trail_depth].saved_value = slot_values[(slot_)];\
        run->trail_depth++;                                             \
    } while (0)
#define RX_SET(slot_, v_) do {                                          \
        RX_TRAIL(slot_); slot_values[(slot_)] = (v_);                   \
    } while (0)
#define RX_PUSH(lbl_, p_) do {                                          \
        if (run->resume_depth >= RX_RESUME_FRAMES) return RX_R_FRAMES;  \
        run->resume_stack[run->resume_depth].resume_label = (lbl_);     \
        run->resume_stack[run->resume_depth].resume_position = (p_);    \
        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth; \
        run->resume_stack[run->resume_depth].call_ret = NULL;           \
        run->resume_stack[run->resume_depth].call_top = run->call_top;  \
        run->resume_stack[run->resume_depth].call_mark = run->call_depth; \
        run->resume_depth++;                                            \
    } while (0)
/* §5.1: a CALL IS A FRAME. resume_label is rx_fail, so the fail label needs
 * no knowledge of frame kinds -- one added line serves both. */
#ifndef BROKEN_ARRAY
#define RX_CALL(ret_, p_) do {                                          \
        if (run->resume_depth >= RX_RESUME_FRAMES) return RX_R_FRAMES;  \
        if (run->call_depth  >= RX_CALL_DEPTH)     return RX_R_RECURSE; \
        run->resume_stack[run->resume_depth].resume_label = &&rx_fail;  \
        run->resume_stack[run->resume_depth].resume_position = (p_);    \
        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth; \
        run->resume_stack[run->resume_depth].call_ret = (ret_);         \
        run->resume_stack[run->resume_depth].call_top = run->call_top;  \
        run->resume_stack[run->resume_depth].call_mark = run->call_depth; \
        run->call_top = run->resume_depth;                              \
        run->resume_depth++;  run->call_depth++;                        \
    } while (0)
#else
/* §5.2's REJECTED design. The call frame still exists (so trail_mark and the
 * save block are identical and the two variants differ in ONE thing only:
 * where the return label lives and when it is popped). */
#define RX_CALL(ret_, p_) do {                                          \
        if (run->resume_depth >= RX_RESUME_FRAMES) return RX_R_FRAMES;  \
        if (run->call_depth  >= RX_CALL_DEPTH)     return RX_R_RECURSE; \
        run->resume_stack[run->resume_depth].resume_label = &&rx_fail;  \
        run->resume_stack[run->resume_depth].resume_position = (p_);    \
        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth; \
        run->resume_stack[run->resume_depth].call_ret = NULL;           \
        run->resume_stack[run->resume_depth].call_top = run->call_top;  \
        run->resume_stack[run->resume_depth].call_mark = run->call_depth; \
        run->call_top = run->resume_depth;                              \
        run->call_stack[run->call_depth] = (ret_);                      \
        run->resume_depth++;  run->call_depth++;                        \
    } while (0)
#endif
/* §5.1: the return does NOT pop -- §3.2 measured the call is backtrackable,
 * so the callee's frames AND its return label must survive the return. */
#ifndef BROKEN_ARRAY
#define RX_RETURN do {                                                  \
        const unsigned t_ = run->call_top;                              \
        run->call_top   = run->resume_stack[t_].call_top;               \
        run->call_depth = run->resume_stack[t_].call_mark;              \
        goto *run->resume_stack[t_].call_ret;                           \
    } while (0)
#else
#define RX_RETURN do {                                                  \
        const unsigned t_ = run->call_top;                              \
        run->call_top   = run->resume_stack[t_].call_top;               \
        run->call_depth = run->resume_stack[t_].call_mark;              \
        goto *run->call_stack[run->call_depth];                         \
    } while (0)
#endif
/* §5.3: |W| trailed SELF-writes after the push; the restore reads them back
 * at trail_mark + j. W(g) includes g's OWN slots -- see the design's §5.3,
 * which this prototype corrected. */
#define RX_SAVE_1(a_)  do { RX_SET((a_), slot_values[(a_)]); } while (0)
#define RX_REST(j_, s_) do {                                            \
        RX_SET((s_), run->trail[run->resume_stack[run->call_top].trail_mark \
                                + (j_)].saved_value);                   \
    } while (0)

/* ---- P1: ^((a)(?1)?(b))$ -----------------------------------------------
 * slots: 0/1 whole, 2/3 g1, 4/5 g2, 6/7 g3.  W(1) = {2,3,4,5,6,7}, six slots.
 * The LEXICAL occurrence of group 1 is spliced (§6.3); the recursive call
 * site inside it, and the one inside the shared copy, take the linkage. */
static ptrdiff_t p1(const unsigned char *subject, size_t subject_length,
                    size_t start, rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
    if (scan_position != 0) goto rx_fail;            /* ^ */
    RX_SET(0, (ptrdiff_t)scan_position);

/* --- the LEXICAL copy of group 1's body, emitted as it always was --- */
    RX_SET(2, (ptrdiff_t)scan_position);             /* g1 start */
    RX_SET(4, (ptrdiff_t)scan_position);             /* g2 start */
    if (!(scan_position < subject_length && subject[scan_position] == 'a'))
        goto rx_fail;
    scan_position++;
    RX_SET(5, (ptrdiff_t)scan_position);             /* g2 end */
    RX_PUSH(&&lex_skip, scan_position);              /* (?1)? greedy */
    RX_CALL(&&lex_ret, scan_position);
    RX_SAVE_1(2); RX_SAVE_1(3); RX_SAVE_1(4);
    RX_SAVE_1(5); RX_SAVE_1(6); RX_SAVE_1(7);
    goto shd_entry;
lex_ret: __attribute__((unused));
    goto lex_after;
lex_skip: __attribute__((unused));
    goto lex_after;
lex_after: __attribute__((unused));
    RX_SET(6, (ptrdiff_t)scan_position);             /* g3 start */
    if (!(scan_position < subject_length && subject[scan_position] == 'b'))
        goto rx_fail;
    scan_position++;
    RX_SET(7, (ptrdiff_t)scan_position);             /* g3 end */
    RX_SET(3, (ptrdiff_t)scan_position);             /* g1 end */
    if (scan_position != subject_length) goto rx_fail;   /* $ */
    goto rx_accept;

/* --- the SHARED copy: the call target --- */
shd_entry: __attribute__((unused));
    RX_SET(2, (ptrdiff_t)scan_position);
    RX_SET(4, (ptrdiff_t)scan_position);
    if (!(scan_position < subject_length && subject[scan_position] == 'a'))
        goto rx_fail;
    scan_position++;
    RX_SET(5, (ptrdiff_t)scan_position);
    RX_PUSH(&&shd_skip, scan_position);
    RX_CALL(&&shd_ret, scan_position);
    RX_SAVE_1(2); RX_SAVE_1(3); RX_SAVE_1(4);
    RX_SAVE_1(5); RX_SAVE_1(6); RX_SAVE_1(7);
    goto shd_entry;
shd_ret: __attribute__((unused));
    goto shd_after;
shd_skip: __attribute__((unused));
    goto shd_after;
shd_after: __attribute__((unused));
    RX_SET(6, (ptrdiff_t)scan_position);
    if (!(scan_position < subject_length && subject[scan_position] == 'b'))
        goto rx_fail;
    scan_position++;
    RX_SET(7, (ptrdiff_t)scan_position);
    RX_SET(3, (ptrdiff_t)scan_position);
    /* §5.3: the RETURN restores W, then goto* the frame's return label. */
    RX_REST(0, 2); RX_REST(1, 3); RX_REST(2, 4);
    RX_REST(3, 5); RX_REST(4, 6); RX_REST(5, 7);
    RX_RETURN;

rx_accept: __attribute__((unused));
    RX_SET(1, (ptrdiff_t)scan_position);
    return (ptrdiff_t)(scan_position - start);
rx_fail: __attribute__((unused));
    if (run->resume_depth == 0) return -1;
    {
        const unsigned fi = --run->resume_depth;
        scan_position = run->resume_stack[fi].resume_position;
        while (run->trail_depth > run->resume_stack[fi].trail_mark) {
            run->trail_depth--;
            slot_values[run->trail[run->trail_depth].slot_index] =
                run->trail[run->trail_depth].saved_value;
        }
        run->call_top   = run->resume_stack[fi].call_top;    /* §5.1's ONE */
        run->call_depth = run->resume_stack[fi].call_mark;   /*  added line */
        goto *run->resume_stack[fi].resume_label;
    }
}

/* ---- P2: ^(?(DEFINE)(?<g>a|ab))(?&g)c$ ---------------------------------
 * The callee is reachable ONLY by the call, so the only alternation frame in
 * existence belongs to the CALL. W(g) = {2,3} (group g itself). */
static ptrdiff_t p2(const unsigned char *subject, size_t subject_length,
                    size_t start, rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
    if (scan_position != 0) goto rx_fail;
    RX_SET(0, (ptrdiff_t)scan_position);
    RX_CALL(&&ret0, scan_position);
    RX_SAVE_1(2); RX_SAVE_1(3);
    goto g_entry;
ret0: __attribute__((unused));
    if (!(scan_position < subject_length && subject[scan_position] == 'c'))
        goto rx_fail;
    scan_position++;
    if (scan_position != subject_length) goto rx_fail;
    goto rx_accept;

g_entry: __attribute__((unused));
    RX_SET(2, (ptrdiff_t)scan_position);
    RX_PUSH(&&g_alt2, scan_position);
    if (!(scan_position < subject_length && subject[scan_position] == 'a'))
        goto rx_fail;
    scan_position++;
    goto g_close;
g_alt2: __attribute__((unused));
    if (!(scan_position + 1 < subject_length
          && subject[scan_position] == 'a' && subject[scan_position+1] == 'b'))
        goto rx_fail;
    scan_position += 2;
    goto g_close;
g_close: __attribute__((unused));
    RX_SET(3, (ptrdiff_t)scan_position);
    RX_REST(0, 2); RX_REST(1, 3);
    RX_RETURN;

rx_accept: __attribute__((unused));
    RX_SET(1, (ptrdiff_t)scan_position);
    return (ptrdiff_t)(scan_position - start);
rx_fail: __attribute__((unused));
    if (run->resume_depth == 0) return -1;
    {
        const unsigned fi = --run->resume_depth;
        scan_position = run->resume_stack[fi].resume_position;
        while (run->trail_depth > run->resume_stack[fi].trail_mark) {
            run->trail_depth--;
            slot_values[run->trail[run->trail_depth].slot_index] =
                run->trail[run->trail_depth].saved_value;
        }
        run->call_top   = run->resume_stack[fi].call_top;
        run->call_depth = run->resume_stack[fi].call_mark;
        goto *run->resume_stack[fi].resume_label;
    }
}

/* ---- P3: ^(a|(?1)a)$ ---------------------------------------------------
 * §3.3's cell. Group 1 is BOTH lexical and a call target; the recursion is
 * LEFT-recursive on the second branch and every level is entered at offset 0.
 * W(1) = {2,3}. */
static ptrdiff_t p3(const unsigned char *subject, size_t subject_length,
                    size_t start, rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
    if (scan_position != 0) goto rx_fail;
    RX_SET(0, (ptrdiff_t)scan_position);
    /* lexical occurrence, spliced */
    RX_SET(2, (ptrdiff_t)scan_position);
    RX_PUSH(&&lex_alt2, scan_position);
    if (!(scan_position < subject_length && subject[scan_position] == 'a'))
        goto rx_fail;
    scan_position++;
    goto lex_close;
lex_alt2: __attribute__((unused));
    RX_CALL(&&lex_callret, scan_position);
    RX_SAVE_1(2); RX_SAVE_1(3);
    goto shd_entry;
lex_callret: __attribute__((unused));
    if (!(scan_position < subject_length && subject[scan_position] == 'a'))
        goto rx_fail;
    scan_position++;
    goto lex_close;
lex_close: __attribute__((unused));
    RX_SET(3, (ptrdiff_t)scan_position);
    if (scan_position != subject_length) goto rx_fail;
    goto rx_accept;

shd_entry: __attribute__((unused));
    RX_SET(2, (ptrdiff_t)scan_position);
    RX_PUSH(&&shd_alt2, scan_position);
    if (!(scan_position < subject_length && subject[scan_position] == 'a'))
        goto rx_fail;
    scan_position++;
    goto shd_close;
shd_alt2: __attribute__((unused));
    RX_CALL(&&shd_callret, scan_position);
    RX_SAVE_1(2); RX_SAVE_1(3);
    goto shd_entry;
shd_callret: __attribute__((unused));
    if (!(scan_position < subject_length && subject[scan_position] == 'a'))
        goto rx_fail;
    scan_position++;
    goto shd_close;
shd_close: __attribute__((unused));
    RX_SET(3, (ptrdiff_t)scan_position);
    RX_REST(0, 2); RX_REST(1, 3);
    RX_RETURN;

rx_accept: __attribute__((unused));
    RX_SET(1, (ptrdiff_t)scan_position);
    return (ptrdiff_t)(scan_position - start);
rx_fail: __attribute__((unused));
    if (run->resume_depth == 0) return -1;
    {
        const unsigned fi = --run->resume_depth;
        scan_position = run->resume_stack[fi].resume_position;
        while (run->trail_depth > run->resume_stack[fi].trail_mark) {
            run->trail_depth--;
            slot_values[run->trail[run->trail_depth].slot_index] =
                run->trail[run->trail_depth].saved_value;
        }
        run->call_top   = run->resume_stack[fi].call_top;
        run->call_depth = run->resume_stack[fi].call_mark;
        goto *run->resume_stack[fi].resume_label;
    }
}

/* ---- P4: ^(?(DEFINE)(?<g>x|xy))(?&g)(?&g)y$ ----------------------------
 * §5.2's CLOBBER SEQUENCE, built. Two sequential calls to one shared body.
 * With a separate call_stack[] indexed by depth, the second call overwrites
 * the first call's return label and the retreat into the first callee returns
 * to the WRONG continuation. */
static ptrdiff_t p4(const unsigned char *subject, size_t subject_length,
                    size_t start, rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
    if (scan_position != 0) goto rx_fail;
    RX_SET(0, (ptrdiff_t)scan_position);
    RX_CALL(&&retA, scan_position);
    RX_SAVE_1(2); RX_SAVE_1(3);
    goto g_entry;
retA: __attribute__((unused));
    RX_CALL(&&retB, scan_position);
    RX_SAVE_1(2); RX_SAVE_1(3);
    goto g_entry;
retB: __attribute__((unused));
    if (!(scan_position < subject_length && subject[scan_position] == 'y'))
        goto rx_fail;
    scan_position++;
    if (scan_position != subject_length) goto rx_fail;
    goto rx_accept;

g_entry: __attribute__((unused));
    RX_SET(2, (ptrdiff_t)scan_position);
    RX_PUSH(&&g_alt2, scan_position);
    if (!(scan_position < subject_length && subject[scan_position] == 'x'))
        goto rx_fail;
    scan_position++;
    goto g_close;
g_alt2: __attribute__((unused));
    if (!(scan_position + 1 < subject_length
          && subject[scan_position] == 'x' && subject[scan_position+1] == 'y'))
        goto rx_fail;
    scan_position += 2;
    goto g_close;
g_close: __attribute__((unused));
    RX_SET(3, (ptrdiff_t)scan_position);
    RX_REST(0, 2); RX_REST(1, 3);
    RX_RETURN;

rx_accept: __attribute__((unused));
    RX_SET(1, (ptrdiff_t)scan_position);
    return (ptrdiff_t)(scan_position - start);
rx_fail: __attribute__((unused));
    if (run->resume_depth == 0) return -1;
    {
        const unsigned fi = --run->resume_depth;
        scan_position = run->resume_stack[fi].resume_position;
        while (run->trail_depth > run->resume_stack[fi].trail_mark) {
            run->trail_depth--;
            slot_values[run->trail[run->trail_depth].slot_index] =
                run->trail[run->trail_depth].saved_value;
        }
        run->call_top   = run->resume_stack[fi].call_top;
        run->call_depth = run->resume_stack[fi].call_mark;
        goto *run->resume_stack[fi].resume_label;
    }
}

typedef ptrdiff_t (*matcher)(const unsigned char *, size_t, size_t,
                             rx_run_state *);
static matcher matchers[] = { p1, p2, p3, p4 };
static const int ncaps[] = { 3, 1, 1, 1 };

int main(int argc, char **argv)
{
    static rx_run_state run_storage;
    rx_run_state *run = &run_storage;
    int which; const char *subj; size_t n; int i; ptrdiff_t r;
    if (argc < 3) { fprintf(stderr, "usage: callproto N SUBJECT\n"); return 2; }
    which = atoi(argv[1]);
    subj = argv[2];
    n = strlen(subj);
    if (which < 0 || which > 3) { fprintf(stderr, "bad matcher\n"); return 2; }
    for (i = 0; i < RX_NSLOTS; i++) run->slot_values[i] = PCREC_UNSET;
    run->resume_depth = run->trail_depth = run->call_depth = 0;
    run->call_top = CALL_TOP_NONE;
    r = matchers[which](
            (const unsigned char *)subj, n, 0, run);
    if (r == RX_R_RECURSE) { printf("recurse\n"); return 0; }
    if (r == RX_R_FRAMES)  { printf("frames\n");  return 0; }
    if (r < 0)             { printf("nomatch\n"); return 0; }
    printf("match %td %td", run->slot_values[0], run->slot_values[1]);
    for (i = 1; i <= ncaps[which]; i++)
        printf(" %td %td", run->slot_values[2*i], run->slot_values[2*i+1]);
    printf("\n");
    return 0;
}
