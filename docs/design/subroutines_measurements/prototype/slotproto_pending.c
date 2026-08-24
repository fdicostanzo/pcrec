/* [DD-14] §5.3 — ADOPTED FROM THE R34 C2 PANEL, NOT REWRITTEN.
 *
 * This file arrived as the C2 critic's refutation prototype for §5.3 and is
 * kept AS THE CRITIC WROTE IT, for the reason docs/design/CLAUDE.md records
 * about `probes/simvm.py` one lane over: a lane that rewrites the instrument
 * which refuted it cannot be trusted not to soften it. The lane re-BUILT both
 * binaries from this source and re-ran the comparison before editing §5.3;
 * `../probes/probe_slotfamilies.py` is that re-run, and it is the lane's own
 * work. Only this header block is the lane's.
 *
 * WHAT IT REFUTED: §5.3's first version defined the return's restore set W
 * over CAPTURE SLOTS ONLY, on the reasoning (inherited from
 * lookaround_design.md §6.4(2)) that every other slot family is
 * "re-initialised at its own entry label on every entry". That is true of
 * SEQUENTIAL re-entry and false of RECURSIVE re-entry, where an inner
 * activation's write to a lexically-outer construct's slot is still live when
 * the outer activation reads it. §5.3 now states the GENERAL rule.
 *
 */
/* LENS-2 refutation prototype for [DD-14] §5.3 / §12 P-2.
 *
 * Pattern: ^(a(?1)?b)\1$      (libpcre2 10.46: "aabbaabb" -> (0,8) g1=(0,4))
 *
 * Group 1 is MARKED (a backreference names it), so pcrec's REAL emitter
 * (src/gen/emit_vm.c, [M6.5.2] vm_slot_pend / the A_CAP arm at :4531-4566)
 * lowers it PUBLISH-AT-CLOSE: the opening position goes to a non-capture
 * SLOT_GROUP1_PENDING slot, and the (start,end) pair is published together
 * at the closing position.
 *
 * §5.3 defines the return's restore set W over CAPTURE slots only.  This
 * file is §5.3 verbatim (W = {2,3}) plus the real emitter's publish-at-close,
 * built two ways:
 *      default              -- W = {2,3}, exactly what §5.3 says
 *      -DW_INCLUDES_PENDING -- W = {2,3,4}, the pending slot added
 * The two builds differ in ONE thing only: whether the pending slot is
 * saved at the call and restored at the return.
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
#define RX_R_RECURSE     ((ptrdiff_t)-5)
#define CALL_TOP_NONE    ((unsigned)-1)

#define SLOT_G1_PENDING 4

typedef struct {
    ptrdiff_t slot_values[RX_NSLOTS];
    struct { const void *resume_label; size_t resume_position;
             unsigned trail_mark; const void *call_ret;
             unsigned call_top; unsigned call_mark; }
             resume_stack[RX_RESUME_FRAMES];
    struct { unsigned slot_index; ptrdiff_t saved_value; }
             trail[RX_TRAIL_FRAMES];
    unsigned resume_depth, trail_depth, call_top, call_depth;
} rx_run_state;

#define RX_TRAIL(slot_) do {                                            \
        if (run->trail_depth >= RX_TRAIL_FRAMES) return RX_R_FRAMES;    \
        run->trail[run->trail_depth].slot_index = (unsigned)(slot_);    \
        run->trail[run->trail_depth].saved_value = slot_values[(slot_)];\
        run->trail_depth++;                                             \
    } while (0)
#define RX_SET(slot_, v_) do { RX_TRAIL(slot_); slot_values[(slot_)] = (v_); } while (0)
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
#define RX_RETURN do {                                                  \
        const unsigned t_ = run->call_top;                              \
        run->call_top   = run->resume_stack[t_].call_top;               \
        run->call_depth = run->resume_stack[t_].call_mark;              \
        goto *run->resume_stack[t_].call_ret;                           \
    } while (0)
#define RX_SAVE_1(a_)  do { RX_SET((a_), slot_values[(a_)]); } while (0)
#define RX_REST(j_, s_) do {                                            \
        RX_SET((s_), run->trail[run->resume_stack[run->call_top].trail_mark \
                                + (j_)].saved_value);                   \
    } while (0)

/* §5.3's W for group 1 = {2,3}.  W_INCLUDES_PENDING adds slot 4. */
#ifdef W_INCLUDES_PENDING
#  define SAVE_W  do { RX_SAVE_1(2); RX_SAVE_1(3); RX_SAVE_1(SLOT_G1_PENDING); } while (0)
#  define REST_W  do { RX_REST(0,2); RX_REST(1,3); RX_REST(2,SLOT_G1_PENDING); } while (0)
#else
#  define SAVE_W  do { RX_SAVE_1(2); RX_SAVE_1(3); } while (0)
#  define REST_W  do { RX_REST(0,2); RX_REST(1,3); } while (0)
#endif

static ptrdiff_t m(const unsigned char *subject, size_t subject_length,
                   size_t start, rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
    if (scan_position != 0) goto rx_fail;              /* ^ */
    RX_SET(0, (ptrdiff_t)scan_position);

/* ---- the LEXICAL copy of group 1 (spliced, §6.3) ---- */
    RX_SET(SLOT_G1_PENDING, (ptrdiff_t)scan_position); /* g1 open, PENDING */
    if (!(scan_position < subject_length && subject[scan_position] == 'a'))
        goto rx_fail;
    scan_position++;
    RX_PUSH(&&lex_skip, scan_position);                /* (?1)? greedy */
    RX_CALL(&&lex_ret, scan_position);
    SAVE_W;
    goto shd_entry;
lex_ret: __attribute__((unused));
lex_skip: __attribute__((unused));
    if (!(scan_position < subject_length && subject[scan_position] == 'b'))
        goto rx_fail;
    scan_position++;
    /* g1 CLOSES: the pair is published together */
    RX_SET(2, slot_values[SLOT_G1_PENDING]);
    RX_SET(3, (ptrdiff_t)scan_position);
    /* \1 */
    {
        ptrdiff_t rs = slot_values[2], re = slot_values[3];
        size_t n;
        if (rs == PCREC_UNSET) goto rx_fail;
        n = (size_t)(re - rs);
        if (scan_position + n > subject_length) goto rx_fail;
        if (n && memcmp(subject + scan_position, subject + rs, n) != 0)
            goto rx_fail;
        scan_position += n;
    }
    if (scan_position != subject_length) goto rx_fail; /* $ */
    goto rx_accept;

/* ---- the SHARED copy: the call target (group 1's body) ---- */
shd_entry: __attribute__((unused));
    RX_SET(SLOT_G1_PENDING, (ptrdiff_t)scan_position);
    if (!(scan_position < subject_length && subject[scan_position] == 'a'))
        goto rx_fail;
    scan_position++;
    RX_PUSH(&&shd_skip, scan_position);
    RX_CALL(&&shd_ret, scan_position);
    SAVE_W;
    goto shd_entry;
shd_ret: __attribute__((unused));
shd_skip: __attribute__((unused));
    if (!(scan_position < subject_length && subject[scan_position] == 'b'))
        goto rx_fail;
    scan_position++;
    RX_SET(2, slot_values[SLOT_G1_PENDING]);
    RX_SET(3, (ptrdiff_t)scan_position);
    REST_W;
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

int main(int argc, char **argv)
{
    static rx_run_state run_storage;
    rx_run_state *run = &run_storage;
    const char *subj; size_t n; int i; ptrdiff_t r;
    if (argc < 2) { fprintf(stderr, "usage: pendproto SUBJECT\n"); return 2; }
    subj = argv[1]; n = strlen(subj);
    for (i = 0; i < RX_NSLOTS; i++) run->slot_values[i] = PCREC_UNSET;
    run->resume_depth = run->trail_depth = run->call_depth = 0;
    run->call_top = CALL_TOP_NONE;
    r = m((const unsigned char *)subj, n, 0, run);
    if (r == RX_R_RECURSE) { printf("recurse\n"); return 0; }
    if (r == RX_R_FRAMES)  { printf("frames\n");  return 0; }
    if (r < 0)             { printf("nomatch\n"); return 0; }
    printf("match %td %td %td %td\n", run->slot_values[0], run->slot_values[1],
           run->slot_values[2], run->slot_values[3]);
    return 0;
}
