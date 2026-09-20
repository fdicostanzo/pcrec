/* tests/core/sb_fragf_check.c — [REVW.2] wave 2 stage 3: THE FRAGMENT
 * PRIMITIVE'S OWN PROPERTY, checked below any emitted artifact.
 *
 * WHAT `pcrec_sb_fragf` PROMISES, and why the promise needs a check of its own.
 * `lens10_emission_kit_charter.md` item 1 defines it as formatted text in
 * arena-owned storage "sized EXACTLY to the result", so that "truncation is
 * impossible BY CONSTRUCTION rather than by a per-site size argument." Stage
 * 3 then deletes ~90 hand-sized `char NAME[N]` scratch buffers across both
 * emitters and routes their text through this one function. That makes this
 * function the single point where the K38 class — a derived identifier run
 * off the end of a fixed buffer, emitted as a sentence that stops mid-word —
 * is now either impossible or universal.
 *
 * AND NO ANSWER-LEVEL CHECK CAN SEE THE DIFFERENCE BETWEEN THOSE TWO STATES
 * at the shipped `-p rx` prefix. `lens10`'s own §4.1 measurement is that no
 * fragment provably truncates today at a 60-byte prefix, with the tightest
 * margin in the tree at 9 bytes; every corpus test runs at `rx`, two bytes.
 * So an off-by-one here — `arena_alloc(a, n)` instead of `n + 1`, the one
 * mistake this shape invites — would pass the whole suite while silently
 * dropping the LAST BYTE of every fragment long enough to matter. That is
 * what this file is for, and it is why the length sweep below runs out to
 * lengths no pattern in the corpus produces.
 *
 * THE ORACLE IS `snprintf` INTO AN OVERSIZED BUFFER — a different mechanism
 * (caller-sized stack storage) reaching the same answer, not a transcription
 * of `pcrec_sb_fragf`'s body. `branch_count_check.c`'s rule: different algorithm,
 * different code, different failure modes. The one thing both share is the
 * platform's `vsnprintf`, which is the subject's own dependency and not
 * something this check could avoid without writing a formatter.
 *
 * FAILING-DIRECTION STORY (coding_guide.md §5 item 5), run before this file
 * was committed, transcripts in `docs/dev/lanes/w2b_report.md`. TWO plants
 * were tried and they do NOT behave alike, which is worth more than the
 * check itself:
 *
 *   PLANT B — `vsnprintf(out, n, ...)` instead of `n + 1`, i.e. the SIZE
 *   ARGUMENT wrong. Sub-checks 1, 2, 4, 5 and 6 all go RED (4,001 of 4,001
 *   sweep rows disagree; 512 of 513 results short by one). This is the plant
 *   this check is a detector for.
 *
 *   PLANT A — `arena_alloc(a, n)` instead of `n + 1`, i.e. the ALLOCATION
 *   one byte short. THIS CHECK STAYS GREEN, and so does AddressSanitizer.
 *   MEASURED, not reasoned: `arena_alloc` rounds every request up to 16 bytes
 *   and zeroes the slice, so the terminator lands in already-zero storage the
 *   next `arena_alloc` will zero again; and ASan sees only the arena's own
 *   64 KiB block `malloc`, never the intra-block slice bounds, so a one-byte
 *   overrun inside a block is invisible to it BY CONSTRUCTION. A standalone
 *   `-fsanitize=address` probe over lengths 0..599 reported "content correct
 *   at every length" against both the repaired and the plant-A build.
 *
 * So: `pcrec_sb_fragf`'s no-truncation promise is enforced by the SIZE ARGUMENT,
 * and the exactness of the allocation itself is not observable from outside
 * this tree's instruments at all. Stated here rather than left implied,
 * because the natural reading of "sized exactly to the result" is that both
 * halves are checked and only one of them is.
 *
 * COST: one process, no `pcrec` invocation, no `gcc` invocation per case —
 * `unit_cc.sh`'s shape budget.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
#include "core/limits.h"

static int fails = 0;
static void ok(const char *what)  { printf("PASS: %s\n", what); }
static void bad(const char *what) { printf("FAIL: %s\n", what); fails++; }

/* A detached arena — `.cx` NULL — is exactly what `syntax_dump.c`'s probe
 * buffers already use, and is the right shape here: this check has no `Ctx`
 * to diagnose into, and the allocation sizes below are all small enough that
 * a failure would be a genuine out-of-memory rather than a routed refusal. */
static Arena AR;

int main(void)
{
    /* ---- 1. AGREEMENT WITH AN INDEPENDENT FORMATTER, over a length sweep
     * that crosses every fixed size the retired buffers used (32, 64, 80, 96,
     * 160) and runs well past PCREC_MAX_EMIT_NAME_LEN. */
    {
        int bad_rows = 0, rows = 0;
        char ref[8192];
        for (int len = 0; len <= 4000; len++) {
            char *fill = malloc((size_t)len + 1);
            if (!fill) { bad("1: out of memory building the sweep input"); break; }
            for (int i = 0; i < len; i++) fill[i] = (char)('a' + (i % 26));
            fill[len] = 0;
            int rn = snprintf(ref, sizeof ref, "rx_%s_end", fill);
            const char *got = pcrec_sb_fragf(&AR, "rx_%s_end", fill);
            rows++;
            if (rn < 0 || (size_t)rn >= sizeof ref) {
                /* the oracle's own buffer must never be the binding
                 * constraint, or this check would be comparing two
                 * truncations and calling them equal */
                bad("1: the REFERENCE snprintf truncated; its buffer is too small for this sweep");
                free(fill);
                break;
            }
            if (strcmp(ref, got) != 0) bad_rows++;
            free(fill);
        }
        if (rows == 0)          bad("1: the length sweep ran zero rows");
        else if (bad_rows != 0) { char m[128]; snprintf(m, sizeof m, "1: %d of %d sweep rows disagree with snprintf", bad_rows, rows); bad(m); }
        else { char m[128]; snprintf(m, sizeof m, "1: all %d sweep rows (formatted lengths 9..4009) agree with an independent snprintf", rows); ok(m); }
    }

    /* ---- 2. THE LENGTH IS EXACT, which is the off-by-one's own detector.
     * `strlen` of the result must equal what `vsnprintf` MEASURED, for every
     * length — an allocation of `n` rather than `n + 1` leaves every nonempty
     * result one byte short and check 1 would catch it too, but this one says
     * WHICH property broke. */
    {
        int short_rows = 0, rows = 0;
        for (int len = 0; len <= 512; len++) {
            char *fill = malloc((size_t)len + 1);
            if (!fill) { bad("2: out of memory"); break; }
            memset(fill, 'x', (size_t)len);
            fill[len] = 0;
            const char *got = pcrec_sb_fragf(&AR, "%s", fill);
            rows++;
            if (strlen(got) != (size_t)len) short_rows++;
            free(fill);
        }
        if (rows == 0)            bad("2: the exact-length sweep ran zero rows");
        else if (short_rows != 0) { char m[160]; snprintf(m, sizeof m, "2: %d of %d results are not their formatted length — the allocation is off by one", short_rows, rows); bad(m); }
        else { char m[160]; snprintf(m, sizeof m, "2: all %d results (lengths 0..511) carry their FULL formatted length", rows); ok(m); }
    }

    /* ---- 3. THE EMPTY RESULT is a valid, NUL-terminated string and not a
     * NULL — because a call site hands this straight to `%s`. */
    {
        const char *e = pcrec_sb_fragf(&AR, "%s", "");
        if (!e)            bad("3: an empty format returned NULL; a call site would pass it to %s");
        else if (*e != 0)  bad("3: an empty format did not return an empty string");
        else               ok("3: an empty result is a real, NUL-terminated empty string, never NULL");
    }

    /* ---- 4. THE K38 WITNESS, at the legal boundary. A `<prefix>_<suffix>`
     * built from a prefix of exactly PCREC_MAX_PREFIX_LEN bytes — the longest
     * `-p` the CLI accepts — is the shape that truncated in the recorded
     * incident and the shape the corpus (which runs at `rx`) never produces.
     * The result must be complete and must be allowed to exceed any of the
     * fixed sizes the retired buffers used. */
    {
        char pfx[PCREC_MAX_PREFIX_LEN + 1];
        memset(pfx, 'p', sizeof pfx - 1);
        pfx[sizeof pfx - 1] = 0;
#define K38_FMT "%s_slot_values[%d] = (ptrdiff_t) (%s_scan_position - %s_saved_%d)"
        const char *n = pcrec_sb_fragf(&AR, K38_FMT, pfx, 12, pfx, pfx, 34);
        char ref[1024];
        snprintf(ref, sizeof ref, K38_FMT, pfx, 12, pfx, pfx, 34);
#undef K38_FMT
        /* 160 is `vm_rolef`'s own `char buf[160]`, the LARGEST fixed size any
         * retired buffer used and the one lens 10 records as TRUNCATING
         * ANYWAY. A witness at or below it would prove nothing this check
         * needs proved, so falling under it is a failure of the CHECK and is
         * reported as one rather than passing quietly. */
        if (strcmp(n, ref) != 0)          bad("4: a max-prefix derived identifier does not match its reference — the K38 shape");
        else if (strlen(n) <= 160)        bad("4: the max-prefix witness is <= 160 bytes, so it does not clear the largest retired buffer; widen it");
        else { char m[192]; snprintf(m, sizeof m, "4: a %zu-byte identifier derived from a %d-byte prefix is complete (past vm_rolef's 160, the largest retired fixed size)", strlen(n), PCREC_MAX_PREFIX_LEN); ok(m); }
    }

    /* ---- 5. INDEPENDENT STORAGE. Two fragments built one after the other do
     * not alias, and the FIRST is still intact after the second is built.
     * This is the property that distinguishes an arena fragment from the
     * stack buffer it replaces: the emitters hand a fragment to an `pcrec_sb_printf`
     * far below the site that built it, and a reused buffer would have been
     * overwritten by then. A 64 KiB run crosses the arena's own block
     * boundary (ABLOCK_MIN), so the check also covers the case where the
     * second allocation moves to a fresh block. */
    {
        const char *first = pcrec_sb_fragf(&AR, "FIRST-%d", 1);
        char big[400];
        memset(big, 'z', sizeof big - 1);
        big[sizeof big - 1] = 0;
        int overlaps = 0;
        for (int i = 0; i < 400; i++) {
            const char *later = pcrec_sb_fragf(&AR, "%s-%d", big, i);
            if (later == first) overlaps++;
        }
        if (overlaps)                       bad("5: a later fragment was handed the SAME storage as an earlier one");
        else if (strcmp(first, "FIRST-1"))  bad("5: an earlier fragment was clobbered by later allocations — it is not independent storage");
        else                                ok("5: an earlier fragment survives 400 later ones intact, across an arena block boundary, with no aliasing");
    }

    /* ---- 6. CONVERSIONS THE CALL SITES ACTUALLY USE, including `%%` (which
     * makes the measured length differ from the format's own length) and a
     * `%lld`, the emitters' width for every counter and budget. */
    {
        const char *g = pcrec_sb_fragf(&AR, "%s_%d%% of %lld [%c]", "rx", 50, (long long)1 << 40, 'q');
        char ref[256];
        snprintf(ref, sizeof ref, "%s_%d%% of %lld [%c]", "rx", 50, (long long)1 << 40, 'q');
        if (strcmp(g, ref) != 0) bad("6: a mixed-conversion format disagrees with snprintf");
        else                     ok("6: %s/%d/%%/%lld/%c in one format agree with snprintf");
    }

    pcrec_arena_free(&AR);
    printf(fails ? "\nsb_fragf_check: %d sub-check(s) FAILED\n" : "\nsb_fragf_check: all sub-checks passed (%d failures)\n", fails);
    return fails ? 1 : 0;
}
