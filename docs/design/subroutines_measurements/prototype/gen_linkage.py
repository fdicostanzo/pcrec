"""[DD-14] §6 PROTOTYPE -- the three LINKAGES for an addressable body.

Charter addition (i): a called group's body exists at its LEXICAL position
AND as a call target. Rule once-emitted-with-two-linkages vs
lexical-occurrence-as-call, MEASURED.

This generator writes three hand-written matchers for ONE pattern family, in
pcrec's own emitted idiom (computed goto, an explicit resume array, a trail of
slot writes, RX_SET/RX_PUSH/RX_CUT spelled exactly as src/gen/emit_vm.c
spells them), differing ONLY in how the shared body is reached:

  SPLICE  every occurrence -- lexical and called -- gets its own copy of the
          body. k+1 copies. No call machinery at all. This is what
          lookaround_design.md §6.4 calls the disciplined splice, and it is
          the shape [M6.6.2]'s vm_look already emits.

  HYBRID  the LEXICAL occurrence is spliced; the CALLS share one further copy
          reached through the call linkage. 2 copies. The lexical path pays
          nothing; a call pays a push and an indirect jump.

  CALL    ONE copy, reached through the call linkage by EVERY occurrence, the
          lexical one included. 1 copy. Every path pays the linkage.

A FOURTH variant, INLINE-TO-DEPTH-K, is generated for the RECURSIVE family
only, because that is the shape the plan row rules out by name ("NOT inline
expansion to depth K -- K19/K22 already paid for that lesson") and a ruling
with no number behind it is an assertion.

NOTE ON WHAT COLLAPSES. The charter names the alternative to CALL as
"once-emitted-with-two-linkages: the lexical occurrence falls through to a
shared body whose exit dispatches on 'was I called?'". Writing it out shows
it is not a third design: the exit's dispatch needs a per-ACTIVATION answer,
and the only per-activation channel is the call stack itself -- so the
fall-through path must push its own continuation, which IS the call linkage.
The genuine three-way choice is SPLICE / HYBRID / CALL above, and HYBRID is
what "two linkages" means once it is made to work. §6.1 states this.

Usage:  python3 gen_linkage.py <variant> <ncalls> [depth] > out.c
        variant in splice|hybrid|call|inlineK ; family chosen by variant
"""
import sys

# ---- the body: `[a-z]+` with a capture, i.e. a group with a real choice
# point, so the linkage is not being measured against a body with no frames.
HEAD = r'''
/* [DD-14] PROTOTYPE -- NOT emitted by pcrec, hand-written in its idiom.
 * Slot map:  0/1 whole, 2/3 group1, 4 call-stack height mark (unused in
 * SPLICE), 5.. per-call saved capture cells. */
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define RX_NSLOTS        8
#define RX_RESUME_FRAMES 2048
#define RX_TRAIL_FRAMES  4096
#define RX_CALL_FRAMES   256
#define PCREC_UNSET      ((ptrdiff_t)-1)
#define RX_R_FRAMES      ((ptrdiff_t)-3)
#define RX_R_CALLS       ((ptrdiff_t)-5)     /* the new typed give-up */

typedef struct {
    ptrdiff_t slot_values[RX_NSLOTS];
    struct { const void *resume_label; size_t resume_position;
             unsigned trail_mark; unsigned call_mark; }
             resume_stack[RX_RESUME_FRAMES];
    struct { unsigned slot_index; ptrdiff_t saved_value; }
             trail[RX_TRAIL_FRAMES];
    const void *call_stack[RX_CALL_FRAMES];
    unsigned resume_depth, trail_depth, call_depth;
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
        run->resume_stack[run->resume_depth].call_mark = run->call_depth;   \
        run->resume_depth++;                                            \
    } while (0)
#define RX_CALL(ret_) do {                                              \
        if (run->call_depth >= RX_CALL_FRAMES) return RX_R_CALLS;       \
        run->call_stack[run->call_depth++] = (ret_);                    \
    } while (0)

static ptrdiff_t rx_match_anchored(const unsigned char *subject,
                                   size_t subject_length, size_t start,
                                   rx_run_state *run)
{
    ptrdiff_t *slot_values = run->slot_values;
    size_t scan_position = start;
'''

TAIL = r'''
rx_accept: __attribute__((unused));
    RX_SET(1, (ptrdiff_t)scan_position);
    return (ptrdiff_t)(scan_position - start);

rx_fail: __attribute__((unused));
    if (run->resume_depth == 0) return -1;
    {
        const unsigned frame_index = --run->resume_depth;
        scan_position = run->resume_stack[frame_index].resume_position;
        while (run->trail_depth > run->resume_stack[frame_index].trail_mark) {
            run->trail_depth--;
            slot_values[run->trail[run->trail_depth].slot_index] =
                run->trail[run->trail_depth].saved_value;
        }
        run->call_depth = run->resume_stack[frame_index].call_mark;
        goto *run->resume_stack[frame_index].resume_label;
    }
}

int rx_search(const unsigned char *s, size_t n, size_t startpos,
              ptrdiff_t (*caps)[2])
{
    static rx_run_state run_storage;
    rx_run_state *run = &run_storage;
    size_t at = startpos;
    for (;;) {
        int i;
        for (i = 0; i < RX_NSLOTS; i++) run->slot_values[i] = PCREC_UNSET;
        run->resume_depth = run->trail_depth = run->call_depth = 0;
        {
            ptrdiff_t r = rx_match_anchored(s, n, at, run);
            if (r == RX_R_FRAMES || r == RX_R_CALLS) return (int)r;
            if (r >= 0) {
                if (caps) { caps[0][0] = (ptrdiff_t)at;
                            caps[0][1] = (ptrdiff_t)at + r;
                            caps[1][0] = run->slot_values[2];
                            caps[1][1] = run->slot_values[3]; }
                return 1;
            }
        }
        if (at >= n) return 0;
        at++;
    }
}

int main(int argc, char **argv)
{
    /* Two modes: `-1 SUBJECT` prints the answer once (correctness), and the
     * default runs the built-in corpus REPS times (throughput). */
    static const char *corpus[] = {
        SUBJECTS
    };
    /* THE LEXICAL-ONLY CORPUS: subjects on which the match dies inside or
     * just after the FIRST (lexical) occurrence and never reaches a call
     * site. This is the corpus on which HYBRID's whole claim lives -- it
     * should track SPLICE exactly and beat CALL. */
    static const char *lexonly[] = {
        "abc!", "hello!", "z!", "abcdefghij!", "!", "ABC", "abcdefgh!x"
    };
    const char **use = corpus;
    size_t nuse = sizeof corpus / sizeof corpus[0];
    long reps; long i; size_t k; long hits = 0;
    if (argc > 1 && strcmp(argv[1], "-lex") == 0) {
        use = lexonly; nuse = sizeof lexonly / sizeof lexonly[0];
        argv++; argc--;
    }
    reps = (argc > 1) ? atol(argv[1]) : 200000;
    if (argc > 2 && strcmp(argv[1], "-1") == 0) {
        ptrdiff_t c[2][2] = {{-1,-1},{-1,-1}};
        int r = rx_search((const unsigned char *)argv[2], strlen(argv[2]),
                          0, c);
        printf("%d %td %td %td %td\n", r, c[0][0], c[0][1], c[1][0], c[1][1]);
        return 0;
    }
    for (i = 0; i < reps; i++)
        for (k = 0; k < nuse; k++)
            hits += (rx_search((const unsigned char *)use[k],
                               strlen(use[k]), 0, NULL) == 1);
    printf("hits %ld\n", hits);
    return 0;
}
'''


def body(lbl, ok_label, sid):
    """`([a-z]+)` -- a capture around a greedy plus with a real choice point.
    `sid` disambiguates label names between copies."""
    return r'''
rx_%(s)s_enter: __attribute__((unused));
    RX_SET(2, (ptrdiff_t)scan_position);
    if (!(scan_position < subject_length
          && subject[scan_position] >= 'a' && subject[scan_position] <= 'z'))
        goto rx_fail;
    scan_position++;
    goto rx_%(s)s_loop;
rx_%(s)s_loop: __attribute__((unused));
    if (scan_position < subject_length
        && subject[scan_position] >= 'a' && subject[scan_position] <= 'z') {
        RX_PUSH(&&rx_%(s)s_stop, scan_position);
        scan_position++;
        goto rx_%(s)s_loop;
    }
    goto rx_%(s)s_stop;
rx_%(s)s_stop: __attribute__((unused));
    RX_SET(3, (ptrdiff_t)scan_position);
    goto %(ok)s;
''' % {"s": sid, "ok": ok_label}


def lit(ch, nxt, sid):
    return r'''
rx_%(s)s: __attribute__((unused));
    if (!(scan_position < subject_length
          && subject[scan_position] == '%(c)s')) goto rx_fail;
    scan_position++;
    goto %(n)s;
''' % {"s": sid, "c": ch, "n": nxt}


def gen(variant, ncalls):
    """The family: `^([a-z]+)` then ncalls repetitions of `.<the same body>`,
    then `$`. One LEXICAL occurrence and `ncalls` call sites."""
    out = [HEAD]
    out.append("    RX_SET(0, (ptrdiff_t)scan_position);\n")
    out.append("    if (scan_position != 0) goto rx_fail;   /* ^ */\n")

    first = "rx_d0" if ncalls else "rx_end"

    if variant == "splice":
        out.append("    goto rx_b0_enter;\n")
        out.append(body("b0", first, "b0"))
        for i in range(ncalls):
            out.append(lit(".", "rx_b%d_enter" % (i + 1), "d%d" % i))
            out.append(body("b%d" % (i + 1),
                            ("rx_d%d" % (i + 1)) if i + 1 < ncalls
                            else "rx_end", "b%d" % (i + 1)))
        out.append("\nrx_end: __attribute__((unused));\n"
                   "    if (scan_position != subject_length) goto rx_fail;\n"
                   "    goto rx_accept;\n")

    elif variant == "hybrid":
        # lexical occurrence SPLICED; the calls share one further copy. At
        # k == 0 there is no call site, so no shared copy is emitted and the
        # variant IS the splice -- which is the point of the k=0 baseline row.
        out.append("    goto rx_b0_enter;\n")
        out.append(body("b0", first, "b0"))
        for i in range(ncalls):
            nxt = ("rx_d%d" % (i + 1)) if i + 1 < ncalls else "rx_end"
            out.append(lit(".", "rx_c%d" % i, "d%d" % i))
            out.append("\nrx_c%d: __attribute__((unused));\n"
                       "    RX_CALL(&&rx_r%d);\n"
                       "    goto rx_shared_enter;\n"
                       "rx_r%d: __attribute__((unused));\n"
                       "    goto %s;\n" % (i, i, i, nxt))
        if ncalls:
            out.append(body("shared", "rx_ret", "shared"))
            out.append("\nrx_ret: __attribute__((unused));\n"
                       "    goto *run->call_stack[--run->call_depth];\n")
        out.append("\nrx_end: __attribute__((unused));\n"
                   "    if (scan_position != subject_length) goto rx_fail;\n"
                   "    goto rx_accept;\n")

    elif variant == "call":
        # EVERY occurrence, lexical included, goes through the linkage.
        out.append("    RX_CALL(&&rx_rL);\n    goto rx_shared_enter;\n")
        out.append("rx_rL: __attribute__((unused));\n    goto %s;\n" % first)
        for i in range(ncalls):
            nxt = ("rx_d%d" % (i + 1)) if i + 1 < ncalls else "rx_end"
            out.append(lit(".", "rx_c%d" % i, "d%d" % i))
            out.append("\nrx_c%d: __attribute__((unused));\n"
                       "    RX_CALL(&&rx_r%d);\n"
                       "    goto rx_shared_enter;\n"
                       "rx_r%d: __attribute__((unused));\n"
                       "    goto %s;\n" % (i, i, i, nxt))
        out.append(body("shared", "rx_ret", "shared"))
        out.append("\nrx_ret: __attribute__((unused));\n"
                   "    goto *run->call_stack[--run->call_depth];\n")
        out.append("\nrx_end: __attribute__((unused));\n"
                   "    if (scan_position != subject_length) goto rx_fail;\n"
                   "    goto rx_accept;\n")
    else:
        raise SystemExit("bad variant %r" % variant)

    subs = ",\n        ".join(
        '"%s"' % ".".join(w for _ in range(ncalls + 1))
        for w in ["abc", "hello", "z", "abcdefghij"])
    subs += ",\n        " + ",\n        ".join(
        '"%s"' % s for s in ["abc.def", "no-match-here", "a.b.c.d.e.f"])
    out.append(TAIL.replace("SUBJECTS", subs))
    return "".join(out)


if __name__ == "__main__":
    v = sys.argv[1]
    n = int(sys.argv[2])
    sys.stdout.write(gen(v, n))
