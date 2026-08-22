/* cut_proto.c — PROTOTYPE. NOT pcrec output, NOT compiled by pcrec's make.
 *
 * [M6.4.1] §3 (the VM lowering of an UNCONDITIONAL cut). The design claims
 * that `vm_cut`'s no-trail-rewind invariant survives being used for a cut that
 * possessify's §2.2 proof does NOT license — i.e. for a cut that really does
 * delete reachable matches. The claim is STRUCTURAL (it is an argument about
 * frames and trail marks, src/gen/emit_vm.c:4773-4793 and :5071-5079), and an
 * argument about pointer bookkeeping is exactly the kind of claim that should
 * be RUN before it is believed.
 *
 * So this file hand-lowers five atomic patterns into the emitted VM's OWN
 * vocabulary and runs them. The machinery below — RX_TRAIL / RX_SET / RX_PUSH
 * / RX_CUT, the run state, and the fail label with its trail unwind — is
 * COPIED VERBATIM from an artifact `build/pcrec -p rx -o q.c '(?:(a)|bc){1,3}d'`
 * emitted at the commit in this file's archived header, so a divergence
 * between this prototype and the real emitter is a divergence in the LOWERING
 * (which is what is under test) and not in the substrate.
 *
 * WHAT IS HAND-WRITTEN AND THEREFORE WHAT THIS CANNOT PROVE: the lowering
 * itself. If the module's real lowering differs from the shape below, this
 * probe says nothing about it. It is evidence that the SHAPE the design
 * proposes computes PCRE2's answers, not evidence that anybody implemented
 * that shape. That is why every claim it supports is marked PROTOTYPE.
 *
 * The oracle is libpcre2 (checked by the .sh driver that runs this), and the
 * expectations compiled in below are only a self-check so a broken build is
 * not reported as a passing one.
 *
 * Build: cc -O2 -Wall -Wextra -std=gnu11 -o cut_proto cut_proto.c
 */
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define RX_UNSET  (-1)
#define RX_NSLOTS 12
#define RX_RESUME_FRAMES 64
#define RX_TRAIL_FRAMES  64
#define RX_R_FRAMES (-3)

typedef struct { void *resume_label; size_t resume_position; unsigned trail_mark; } rx_frame;
typedef struct { unsigned slot_index; ptrdiff_t saved_value; } rx_trail_entry;
typedef struct {
    ptrdiff_t slot_values[RX_NSLOTS];
    rx_frame  resume_stack[RX_RESUME_FRAMES];
    rx_trail_entry trail[RX_TRAIL_FRAMES];
    unsigned resume_depth, trail_depth;
} rx_run_state;

/* --- VERBATIM from an emitted artifact (see the header comment) ---------- */
#define RX_TRAIL(slot_) do {                                  \
        if (run->trail_depth >= RX_TRAIL_FRAMES) return RX_R_FRAMES;    \
        run->trail[run->trail_depth].slot_index = (unsigned)(slot_);               \
        run->trail[run->trail_depth].saved_value = slot_values[(slot_)];                       \
        run->trail_depth++;                                             \
    } while (0)
#define RX_SET(slot_, v_) do {                                \
        RX_TRAIL(slot_); slot_values[(slot_)] = (v_);                 \
    } while (0)
#define RX_PUSH(lbl_, p_) do {                                \
        if (run->resume_depth >= RX_RESUME_FRAMES) return RX_R_FRAMES;       \
        run->resume_stack[run->resume_depth].resume_label = (lbl_);                             \
        run->resume_stack[run->resume_depth].resume_position = (p_);                             \
        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth;                          \
        run->resume_depth++;                                             \
    } while (0)
#ifndef CUT_REWINDS_TRAIL
#define RX_CUT(slot_) do {                                   \
        run->resume_depth = (unsigned)slot_values[(slot_)];                      \
    } while (0)
#else
/* ---- THE SABOTAGE ARM (R31 C6) ------------------------------------------
 * `vm_cut`'s comment says the cut "IT DOES NOT TOUCH THE TRAIL, and must
 * not". This arm makes it touch the trail, in the most natural WRONG way: it
 * undoes everything the frames it is discarding would have undone, by
 * rewinding to the trail mark of the FIRST DISCARDED frame.
 *
 * It exists because C6 found that this probe's "non-vacuous" column measures
 * the WRONG AXIS. Cut-vs-uncut and trail-rewind-vs-not are different
 * questions: under this sabotage exactly the rows the probe labelled VACUOUS
 * go red, and all nine it advertised as non-vacuous stay green. A suite whose
 * only discrimination column is cut-vs-uncut cannot see CUT-INV at all.
 *
 * The driver builds BOTH arms every run and reports, per row, which axis that
 * row discriminates — so the two columns are measured rather than asserted. */
#define RX_CUT(slot_) do {                                   \
        unsigned m_ = (unsigned)slot_values[(slot_)];                            \
        if (m_ < run->resume_depth) {                                            \
            unsigned tm_ = run->resume_stack[m_].trail_mark;                     \
            while (run->trail_depth > tm_) {                                     \
                run->trail_depth--;                                              \
                slot_values[run->trail[run->trail_depth].slot_index] =           \
                    run->trail[run->trail_depth].saved_value;                    \
            }                                                                    \
        }                                                                        \
        run->resume_depth = m_;                                                  \
    } while (0)
#endif
/* ------------------------------------------------------------------------ */

static void rx_init(rx_run_state *run)
{
    int i;
    for (i = 0; i < RX_NSLOTS; i++) run->slot_values[i] = RX_UNSET;
    run->resume_depth = 0; run->trail_depth = 0;
}

/* The fail label's body, spelled once as a macro so all five lowerings share
 * the emitter's exact unwind rather than five hand-copies that could drift. */
#define RX_FAIL_BODY()                                                        \
    if (run->resume_depth == 0) return -1;                                    \
    {                                                                         \
        const unsigned fi = --run->resume_depth;                              \
        scan_position = run->resume_stack[fi].resume_position;                \
        while (run->trail_depth > run->resume_stack[fi].trail_mark) {         \
            run->trail_depth--;                                               \
            slot_values[run->trail[run->trail_depth].slot_index] =            \
                run->trail[run->trail_depth].saved_value;                     \
        }                                                                     \
        goto *run->resume_stack[fi].resume_label;                             \
    }

enum { S_MARK = 0, S_MARK2 = 1, S_G1S = 2, S_G1E = 3, S_G2S = 4, S_G2E = 5,
       S_G3S = 6, S_G3E = 7 };

#define AT(k) (scan_position + (k) < subject_length)
#define B(k)  (subject[scan_position + (k)])

/* ---- P1: (?>a|ab)c ------------------------------------------------------ */
static ptrdiff_t p1(const unsigned char *subject, size_t subject_length,
                    size_t start, rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
    RX_SET(S_MARK, (ptrdiff_t)run->resume_depth);   /* mark BEFORE any push */
    RX_PUSH(&&L_alt2, scan_position);
    if (AT(0) && B(0) == 'a') { scan_position += 1; goto L_cut; }
    goto rx_fail;
L_alt2:
    if (AT(1) && B(0) == 'a' && B(1) == 'b') { scan_position += 2; goto L_cut; }
    goto rx_fail;
L_cut:
    RX_CUT(S_MARK);
    if (AT(0) && B(0) == 'c') { scan_position += 1; return (ptrdiff_t)scan_position; }
    goto rx_fail;
rx_fail: __attribute__((unused));
    RX_FAIL_BODY()
}

/* ---- P2: ((?>(a)|ab))c|(abc)  — THE OUTER-FAILURE CELL ------------------
 * The cut discards the inner alternation frame WITHOUT rewinding the trail.
 * The outer alternation's frame sits BELOW the mark and carries a trail mark
 * from before the body ran, so popping it must still undo groups 1 and 2. */
static ptrdiff_t p2(const unsigned char *subject, size_t subject_length,
                    size_t start, rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
    RX_PUSH(&&L_outer2, scan_position);
    RX_SET(S_G1S, (ptrdiff_t)scan_position);
    RX_SET(S_MARK, (ptrdiff_t)run->resume_depth);
    RX_PUSH(&&L_inner2, scan_position);
    if (AT(0) && B(0) == 'a') {
        RX_SET(S_G2S, (ptrdiff_t)scan_position);
        scan_position += 1;
        RX_SET(S_G2E, (ptrdiff_t)scan_position);
        goto L_incut;
    }
    goto rx_fail;
L_inner2:
    if (AT(1) && B(0) == 'a' && B(1) == 'b') { scan_position += 2; goto L_incut; }
    goto rx_fail;
L_incut:
    RX_CUT(S_MARK);
    RX_SET(S_G1E, (ptrdiff_t)scan_position);
    if (AT(0) && B(0) == 'c') { scan_position += 1; return (ptrdiff_t)scan_position; }
    goto rx_fail;
L_outer2:
    RX_SET(S_G3S, (ptrdiff_t)scan_position);
    if (AT(2) && B(0) == 'a' && B(1) == 'b' && B(2) == 'c') {
        scan_position += 3;
        RX_SET(S_G3E, (ptrdiff_t)scan_position);
        return (ptrdiff_t)scan_position;
    }
    goto rx_fail;
rx_fail: __attribute__((unused));
    RX_FAIL_BODY()
}

/* ---- P3: (?>(a)|ab)  — capture RETAINED across the cut on success ------- */
static ptrdiff_t p3(const unsigned char *subject, size_t subject_length,
                    size_t start, rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
    RX_SET(S_MARK, (ptrdiff_t)run->resume_depth);
    RX_PUSH(&&L_alt2, scan_position);
    if (AT(0) && B(0) == 'a') {
        RX_SET(S_G1S, (ptrdiff_t)scan_position);
        scan_position += 1;
        RX_SET(S_G1E, (ptrdiff_t)scan_position);
        goto L_cut;
    }
    goto rx_fail;
L_alt2:
    if (AT(1) && B(0) == 'a' && B(1) == 'b') { scan_position += 2; goto L_cut; }
    goto rx_fail;
L_cut:
    RX_CUT(S_MARK);
    return (ptrdiff_t)scan_position;
rx_fail: __attribute__((unused));
    RX_FAIL_BODY()
}

/* ---- P4: (?>(a)x|ab) — capture ABANDONED inside the body, before the cut -
 * The undo here is ORDINARY backtracking (the body's own frame), which runs
 * BEFORE the cut. If the cut were moved earlier this cell would be wrong. */
static ptrdiff_t p4(const unsigned char *subject, size_t subject_length,
                    size_t start, rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
    RX_SET(S_MARK, (ptrdiff_t)run->resume_depth);
    RX_PUSH(&&L_alt2, scan_position);
    if (AT(0) && B(0) == 'a') {
        RX_SET(S_G1S, (ptrdiff_t)scan_position);
        scan_position += 1;
        RX_SET(S_G1E, (ptrdiff_t)scan_position);
        if (AT(0) && B(0) == 'x') { scan_position += 1; goto L_cut; }
    }
    goto rx_fail;
L_alt2:
    if (AT(1) && B(0) == 'a' && B(1) == 'b') { scan_position += 2; goto L_cut; }
    goto rx_fail;
L_cut:
    RX_CUT(S_MARK);
    return (ptrdiff_t)scan_position;
rx_fail: __attribute__((unused));
    RX_FAIL_BODY()
}

/* ---- P5: (?>a|ab)c|abcd — the CEILING cell, lowered ---------------------
 * The atomic answer ends at 4; the UNCUT twin's answer ends at 3. A prefilter
 * window end of 3 used as an MRL ceiling would prune this match away. This
 * lowering carries no MRL, so it reports the TRUE answer — which is the number
 * probe_uncut_superset.py's R3a violations are measured against. */
static ptrdiff_t p5(const unsigned char *subject, size_t subject_length,
                    size_t start, rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
    RX_PUSH(&&L_outer2, scan_position);
    RX_SET(S_MARK, (ptrdiff_t)run->resume_depth);
    RX_PUSH(&&L_alt2, scan_position);
    if (AT(0) && B(0) == 'a') { scan_position += 1; goto L_cut; }
    goto rx_fail;
L_alt2:
    if (AT(1) && B(0) == 'a' && B(1) == 'b') { scan_position += 2; goto L_cut; }
    goto rx_fail;
L_cut:
    RX_CUT(S_MARK);
    if (AT(0) && B(0) == 'c') { scan_position += 1; return (ptrdiff_t)scan_position; }
    goto rx_fail;
L_outer2:
    if (AT(3) && B(0) == 'a' && B(1) == 'b' && B(2) == 'c' && B(3) == 'd') {
        scan_position += 4; return (ptrdiff_t)scan_position;
    }
    goto rx_fail;
rx_fail: __attribute__((unused));
    RX_FAIL_BODY()
}

typedef ptrdiff_t (*matchfn)(const unsigned char *, size_t, size_t, rx_run_state *);

/* Naive leftmost search: every start position, in order. NOT the emitted
 * search loop -- deliberately, so this probe measures the LOWERING and not the
 * prefilter (which is §4's separate question and probe_uncut_superset.py's). */
static int search(matchfn f, const char *subj, size_t *sp, size_t *ep,
                  ptrdiff_t caps[3][2])
{
    rx_run_state run;
    size_t n = strlen(subj);
    size_t st;
    for (st = 0; st <= n; st++) {
        ptrdiff_t r;
        rx_init(&run);
        r = f((const unsigned char *)subj, n, st, &run);
        if (r == RX_R_FRAMES) return -2;
        if (r >= 0) {
            *sp = st; *ep = (size_t)r;
            caps[0][0] = run.slot_values[S_G1S]; caps[0][1] = run.slot_values[S_G1E];
            caps[1][0] = run.slot_values[S_G2S]; caps[1][1] = run.slot_values[S_G2E];
            caps[2][0] = run.slot_values[S_G3S]; caps[2][1] = run.slot_values[S_G3E];
            return 1;
        }
    }
    return 0;
}

struct row { const char *pat; matchfn f; const char *subj; int ncap; };

static const struct row ROWS[] = {
    { "(?>a|ab)c",           p1, "abc",   0 },
    { "(?>a|ab)c",           p1, "xabc",  0 },
    { "(?>a|ab)c",           p1, "abcabc",0 },
    { "(?>a|ab)c",           p1, "aabc",  0 },
    { "((?>(a)|ab))c|(abc)", p2, "abc",   3 },
    { "((?>(a)|ab))c|(abc)", p2, "xabc",  3 },
    { "((?>(a)|ab))c|(abc)", p2, "abd",   3 },
    { "(?>(a)|ab)",          p3, "ab",    1 },
    { "(?>(a)|ab)",          p3, "b",     1 },
    { "(?>(a)x|ab)",         p4, "ab",    1 },
    { "(?>(a)x|ab)",         p4, "ax",    1 },
    { "(?>a|ab)c|abcd",      p5, "abcd",  0 },
    { "(?>a|ab)c|abcd",      p5, "xxabcd",0 },
    { "(?>a|ab)c|abcd",      p5, "abc",   0 },
    /* R31 C6: rows added BECAUSE they discriminate the TRAIL invariant rather
     * than the cut. Each writes a capture inside the atomic body on the path
     * the cut commits to, so a cut that rewound the trail would lose it. */
    { "(?>(a)|ab)",          p3, "a",     1 },
    { "(?>(a)x|ab)",         p4, "axb",   1 },
    { "((?>(a)|ab))c|(abc)", p2, "abcx",  3 },
};

int main(void)
{
    size_t i;
    puts("# PROTOTYPE: hand-lowered atomic patterns on the emitted VM's own");
    puts("# frame/trail machinery. Columns: pattern, subject, span, groups.");
    puts("# The .sh driver checks every row against libpcre2.");
    puts("");
    for (i = 0; i < sizeof ROWS / sizeof ROWS[0]; i++) {
        size_t s = 0, e = 0;
        ptrdiff_t caps[3][2] = {{RX_UNSET,RX_UNSET},{RX_UNSET,RX_UNSET},{RX_UNSET,RX_UNSET}};
        int r = search(ROWS[i].f, ROWS[i].subj, &s, &e, caps);
        printf("PROTO\t%s\t%s\t", ROWS[i].pat, ROWS[i].subj);
        if (r == -2)      printf("giveup");
        else if (r == 0)  printf("nomatch");
        else {
            int g;
            printf("(%zu,%zu)", s, e);
            for (g = 0; g < ROWS[i].ncap; g++) {
                if (caps[g][0] < 0 || caps[g][1] < 0) printf(" -");
                else printf(" (%td,%td)", caps[g][0], caps[g][1]);
            }
        }
        printf("\n");
    }
    return 0;
}
