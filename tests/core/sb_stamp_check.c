/* tests/core/sb_stamp_check.c — [REVW.2] wave 2, EP2 step 10 / lens 1 X8:
 * THE STAMP PRIMITIVE'S OWN PROPERTY.
 *
 * WHAT THIS CHECK IS AND IS NOT FOR, stated first because it differs from
 * `sb_fragf_check.c`'s argument and the difference matters. `pcrec_sb_fragf`'s
 * promise is invisible to every answer-level check in this tree — the corpus
 * runs at the two-byte prefix `rx`, where nothing truncates. THE STAMP
 * PRIMITIVE IS NOT IN THAT POSITION. Every byte it writes lands in the
 * emitted `.c`, so the four byte-identity gates and the full-corpus emit-diff
 * DO see a defect in it, immediately and on thousands of artifacts. Saying so
 * is the point: a check whose justification is borrowed from its neighbour is
 * a check nobody can size.
 *
 * WHAT IT ADDS, then, is TWO things the gates cannot give:
 *
 *   (a) WHICH PROPERTY BROKE. A gate says "artifact differs at byte 4,117".
 *       The sub-checks below say "the separator space is gone" or "the name
 *       field is right-justified" — which is the difference between a
 *       five-minute fix and a bisect.
 *
 *   (b) THE PARAMETER SPACE THE CORPUS DOES NOT REACH. The shipped call sites
 *       use exactly two padding widths (9 and 24) and one prefix length (2,
 *       `rx`). This file sweeps widths 0..64 against every name length in the
 *       same range — including the `namew < strlen(name)` case, where a
 *       hand-rolled padding loop and printf's own field width agree only by
 *       accident — and builds one stamp at PCREC_MAX_PREFIX_LEN, the longest
 *       `-p` the CLI accepts and the K38 boundary the corpus never produces.
 *
 * THE ORACLE IS `snprintf` INTO AN OVERSIZED BUFFER, `sb_fragf_check.c`'s
 * choice and `branch_count_check.c`'s rule: a different mechanism (caller-
 * sized stack storage, one call) reaching the same answer, not a
 * transcription of the subject's body.
 *
 * FAILING-DIRECTION STORY (coding_guide.md §5 item 5), run before this file
 * was committed; transcripts in `docs/dev/lanes/w2x_report.md`. Four plants
 * into `sb_stampv`, and THEY DO NOT BEHAVE ALIKE:
 *
 *   PLANT 1 — the separator space deleted. Sub-checks 1, 2, 3, 4 and 5 RED
 *             (512/512 and 4160/4160 rows); 6 GREEN, correctly — the line is
 *             still one newline-terminated line, it is the wrong one.
 *   PLANT 2 — `%-*s` written `%*s` (name field right-justified). ONLY
 *             sub-checks 2 and 5 RED, and sub-check 2 on exactly the 2016
 *             rows whose width exceeds their name length. SUB-CHECK 1 STAYS
 *             GREEN, because at width 0 the two spellings are identical —
 *             which is precisely why the sweep has to carry the width, and
 *             why 30 of the 37 shipped call sites could not have caught it.
 *   PLANT 3 — the trailing newline dropped. Sub-checks 1-6 ALL RED.
 *   PLANT 4 — `pcrec_sb_stamp_str` emitting `%s` instead of `\"%s\"`. Sub-check 4
 *             RED and NOTHING ELSE, which is the sub-check's whole reason for
 *             existing separately: the quoting is the one part of the stamp
 *             line that belongs to one of the three entry points and not to
 *             the shared body.
 *
 * COST: one process, no `pcrec` and no `gcc` invocation per case —
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

/* A detached buffer — `.cx` NULL — is `syntax_dump.c`'s own shape and the
 * right one here: this check has no `Ctx` to diagnose into. */
static StrBuf SB;

/* Drain SB into a caller buffer and reset it, so each sub-check reads exactly
 * the bytes its own call produced. */
static void take(char *out, size_t cap)
{
    size_t n = SB.len < cap - 1 ? SB.len : cap - 1;
    memcpy(out, SB.p ? SB.p : "", n);
    out[n] = 0;
    SB.len = 0;
    if (SB.p) SB.p[0] = 0;
}

int main(void)
{
    /* ---- 1. THE UNPADDED LINE agrees with an independent formatter, over a
     * NAME-LENGTH sweep that runs far past any stamp name the emitters use
     * (the longest today is 21 bytes, `VM_PREFILTER_LANG_WHY`). */
    {
        int bad_rows = 0, rows = 0;
        char got[4096], ref[4096];
        for (int len = 1; len <= 512; len++) {
            char *nm = malloc((size_t)len + 1);
            if (!nm) { bad("1: out of memory building the sweep input"); break; }
            for (int i = 0; i < len; i++) nm[i] = (char)('A' + (i % 26));
            nm[len] = 0;
            sb_stampf(&SB, "RX", nm, "%d", len);
            take(got, sizeof got);
            int rn = snprintf(ref, sizeof ref, "#define RX_%s %d\n", nm, len);
            rows++;
            if (rn < 0 || (size_t)rn >= sizeof ref) {
                bad("1: the REFERENCE snprintf truncated; its buffer is too small for this sweep");
                free(nm);
                break;
            }
            if (strcmp(got, ref) != 0) bad_rows++;
            free(nm);
        }
        if (rows == 0)          bad("1: the name-length sweep ran zero rows");
        else if (bad_rows != 0) { char m[160]; snprintf(m, sizeof m, "1: %d of %d unpadded rows disagree with snprintf", bad_rows, rows); bad(m); }
        else { char m[192]; snprintf(m, sizeof m, "1: all %d unpadded rows (name lengths 1..512) agree with an independent snprintf", rows); ok(m); }
    }

    /* ---- 2. THE PADDED LINE, over the FULL width x name-length cross
     * product 0..64, which is where the shipped call sites reach exactly two
     * cells (width 9 for the `_R_*` family, width 24 for the slot table). The
     * cells with `namew <= strlen(name)` are the ones that matter most: a
     * padding loop and a printf field width agree on them only if the loop
     * was written to clamp, and `_R_INTERNAL` is a shipped instance. */
    {
        int bad_rows = 0, rows = 0, shorter = 0;
        char got[512], ref[512], nm[80];
        for (int w = 0; w <= 64; w++) {
            for (int len = 1; len <= 64; len++) {
                for (int i = 0; i < len; i++) nm[i] = (char)('a' + (i % 26));
                nm[len] = 0;
                pcrec_sb_stampwf(&SB, "RX", nm, w, "%s", "V");
                take(got, sizeof got);
                snprintf(ref, sizeof ref, "#define RX_%-*s %s\n", w, nm, "V");
                rows++;
                if (w > len) shorter++;
                if (strcmp(got, ref) != 0) bad_rows++;
            }
        }
        if (rows == 0)          bad("2: the width x length cross product ran zero rows");
        else if (shorter == 0)  bad("2: no row in the sweep actually PADS (width never exceeds the name) — the sweep cannot see a padding defect");
        else if (bad_rows != 0) { char m[160]; snprintf(m, sizeof m, "2: %d of %d padded rows disagree with snprintf", bad_rows, rows); bad(m); }
        else { char m[224]; snprintf(m, sizeof m, "2: all %d width(0..64) x name-length(1..64) rows agree with snprintf, %d of them actually padding", rows, shorter); ok(m); }
    }

    /* ---- 3. THE FOUR SHIPPED VALUE SPELLINGS, byte for byte. A stamp's
     * value is EMITTED C: the radix and the integer suffix are tokens the
     * artifact's own compiler reads, not renderings of a number. These are
     * the exact formats `emit_vm.c` uses, and they are the argument against
     * the typed `sb_stamp_int` lens 1 proposed. */
    {
        struct { const char *name, *fmt, *want; } row[] = {
            { "VM_RUNGS",          "0x%xu",  "#define RX_VM_RUNGS 0x1fu\n" },
            { "VM_ROOT_MINW",      "%lluULL","#define RX_VM_ROOT_MINW 31ULL\n" },
            { "STEP_BUDGET",       "%lldLL", "#define RX_STEP_BUDGET 31LL\n" },
            { "R_STEPS",           "((ptrdiff_t)PCREC_ERR_STEPS)",
                                             "#define RX_R_STEPS ((ptrdiff_t)PCREC_ERR_STEPS)\n" },
        };
        int n = (int)(sizeof row / sizeof row[0]), bad_rows = 0;
        char got[256];
        for (int i = 0; i < n; i++) {
            if (i == 0)      sb_stampf(&SB, "RX", row[i].name, row[i].fmt, 31u);
            else if (i == 1) sb_stampf(&SB, "RX", row[i].name, row[i].fmt, (unsigned long long)31);
            else if (i == 2) sb_stampf(&SB, "RX", row[i].name, row[i].fmt, (long long)31);
            else             sb_stampf(&SB, "RX", row[i].name, "%s", "((ptrdiff_t)PCREC_ERR_STEPS)");
            take(got, sizeof got);
            if (strcmp(got, row[i].want) != 0) {
                char m[320];
                snprintf(m, sizeof m, "3: value spelling %s produced <%s>, wanted <%s>", row[i].name, got, row[i].want);
                bad(m);
                bad_rows++;
            }
        }
        if (!bad_rows) { char m[160]; snprintf(m, sizeof m, "3: all %d shipped value spellings (hex+u, ULL, LL, a raw C expression) are byte-exact", n); ok(m); }
    }

    /* ---- 4. THE STRING STAMP OWNS ITS QUOTING — the one property that
     * belongs to one entry point rather than to the shared body. */
    {
        char got[256];
        pcrec_sb_stamp_str(&SB, "RX", "VM_PREFILTER", "hybrid");
        take(got, sizeof got);
        if (strcmp(got, "#define RX_VM_PREFILTER \"hybrid\"\n") != 0) {
            char m[320];
            snprintf(m, sizeof m, "4: pcrec_sb_stamp_str produced <%s>, wanted the QUOTED form", got);
            bad(m);
        } else {
            /* An empty value must still produce a well-formed `""`, because a
             * stamp with a bare nothing after it is a different macro. */
            pcrec_sb_stamp_str(&SB, "RX", "EMPTY", "");
            take(got, sizeof got);
            if (strcmp(got, "#define RX_EMPTY \"\"\n") != 0)
                bad("4: pcrec_sb_stamp_str on an EMPTY value did not produce a quoted empty string");
            else
                ok("4: pcrec_sb_stamp_str quotes its value, including the empty one");
        }
    }

    /* ---- 5. THE K38 BOUNDARY. A stamp whose `<UPPER>` is a full
     * PCREC_MAX_PREFIX_LEN prefix — the longest `-p` the CLI accepts, the
     * length the corpus never runs at and the one the recorded miscompile
     * happened at. The primitive holds no fixed buffer, so completeness here
     * is the property; a result at or below the largest retired scratch size
     * would prove nothing and is reported as a failure of the CHECK. */
    {
        char pfx[PCREC_MAX_PREFIX_LEN + 1];
        memset(pfx, 'P', sizeof pfx - 1);
        pfx[sizeof pfx - 1] = 0;
        char got[1024], ref[1024];
        /* The value is `_VM_PREFILTER_LANG_WHY`'s own longest REAL spelling:
         * emit_vm.c's PFLW_SIZECAP arm formats two `unsigned long long`s, so
         * this is that arm at both of its maxima, not a value padded to clear
         * the bar below. */
        const char *maxval = "size cap retry, exact 18446744073709551615 > 18446744073709551615";
        pcrec_sb_stampwf(&SB, pfx, "VM_PREFILTER_LANG_WHY", 24, "\"%s\"", maxval);
        take(got, sizeof got);
        snprintf(ref, sizeof ref, "#define %s_%-*s \"%s\"\n", pfx, 24,
                 "VM_PREFILTER_LANG_WHY", maxval);
        if (strcmp(got, ref) != 0)       bad("5: a max-prefix stamp line does not match its reference — the K38 shape");
        else if (strlen(got) <= 160)     bad("5: the max-prefix witness is <= 160 bytes, so it clears no retired scratch size; widen it");
        else { char m[224]; snprintf(m, sizeof m, "5: a %zu-byte stamp line built from a %d-byte prefix is complete (past 160, the largest retired fixed size)", strlen(got), PCREC_MAX_PREFIX_LEN); ok(m); }
    }

    /* ---- 6. THE LINE IS ONE LINE. Exactly one newline, at the end, and no
     * stray NUL or TAB — the framing property every artifact's `#define`
     * block depends on and the one a `\n\n` in the wrong place would break
     * silently for a reader diffing artifacts. */
    {
        char got[512];
        int nl = 0, bad_rows = 0;
        for (int w = 0; w <= 32; w += 8) {
            pcrec_sb_stampwf(&SB, "RX", "NAME", w, "%d", w);
            take(got, sizeof got);
            size_t L = strlen(got);
            nl = 0;
            for (size_t i = 0; i < L; i++) if (got[i] == '\n') nl++;
            if (nl != 1 || L == 0 || got[L - 1] != '\n') bad_rows++;
            if (strchr(got, '\t')) bad_rows++;
        }
        if (bad_rows) bad("6: a stamp line is not exactly one newline-terminated line");
        else          ok("6: every stamp line carries exactly one newline, at its end, and no TAB");
    }

    pcrec_sb_free(&SB);
    printf(fails ? "\nsb_stamp_check: %d sub-check(s) FAILED\n" : "\nsb_stamp_check: all sub-checks passed (%d failures)\n", fails);
    return fails ? 1 : 0;
}
