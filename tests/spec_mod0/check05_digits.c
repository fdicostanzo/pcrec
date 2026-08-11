/* check05_digits.c — INVARIANT 5: the digit rules, all three clauses.
 *
 * THE PROMISE. "Single digits \1..\9 never fall back to octal; runs beginning
 * 8/9 are backreferences at any length and any count; octal fallback re-reads
 * at most three octal digits and overflow is err 151. Oracle: libpcre2 over a
 * generated digit-run x count grid."
 *
 * PREDICTOR, stated before the run. Write a probe as
 *      ^ (a){B}  \RUN  (a){A} $        with T = B + A groups in total.
 *
 *   CLAUSE 1 — single digits. For d in 1..9, \d is a BACKREFERENCE in every
 *     cell of the grid, with no octal cell anywhere:
 *        T >= d  -> compiles, and libpcre2's BACKREFMAX is d;
 *        T <  d  -> err 115, and NOT a successful compile.
 *     The failure direction that matters is the second one: an implementation
 *     that fell back to octal would COMPILE \1 with no groups (as chr(1)),
 *     so "compiles when it must not" is what the grid hunts, and every T < d
 *     cell is one of those probes.
 *
 *   CLAUSE 2 — runs beginning 8 or 9. For a run n whose first digit is 8 or 9,
 *     at ANY length and ANY count, n is a backreference decided by the TOTAL
 *     count (forward groups included), never octal — which it could not be
 *     anyway, 8 and 9 not being octal digits:
 *        T >= n  -> compiles, BACKREFMAX == n;
 *        T <  n  -> err 115.
 *     Probed at the boundary (T = n-1 and T = n) so each run contributes a
 *     cell on each side of its own threshold, and with the groups placed
 *     before, after, and split, so "any count" means placement too.
 *
 *   CLAUSE 3 — octal fallback. For a run n whose first digit is 1..7 with
 *     B < n (the running count does not reach it), the escape is OCTAL, and:
 *        (a) at most THREE octal digits are consumed, the rest are literal
 *            text: \1234 is chr(0123) then '4';
 *        (b) a three-digit value above \377 is err 151 in 8-bit mode;
 *        (c) overflow is decided by the THREE DIGITS ACTUALLY READ, not by the
 *            whole run. So a longer run overflows exactly when its first three
 *            octal digits do: \1000 is chr(0100) then '0' and compiles, while
 *            \7777 is err 151 because the three digits read are 777.
 *
 * PREDICTOR CORRECTION, and the run that forced it. Clause 3(c) as first
 * written here said the opposite — that a longer run "cannot overflow", so
 * \7777 would be chr(0377) followed by a literal '7'. libpcre2 returned err
 * 151. The rule reads three digits and THEN range-checks them; it does not
 * shorten the read to keep the value in range. The corrected form above is
 * what the cells below assert, and \7777 is now an overflow cell. Recorded
 * rather than quietly edited, because the wrong version is the intuitive one
 * and the next reader will arrive holding it.
 *
 * HOW BACKREF-NESS IS READ. From libpcre2's own PCRE2_INFO_BACKREFMAX, not
 * inferred from matching — the oracle answers the question the claim is about.
 * The INFO constants are sanity-checked in spec_start() before any cell runs;
 * a wrong constant reads some other field and agrees with everything.
 * Octal-ness is read the other way, by MATCHING the byte the octal value
 * denotes, because BACKREFMAX cannot distinguish "octal" from "no reference".
 *
 * SABOTAGE (verified 2026-08-11): flip the backreference threshold from
 * `T >= n` to `T > n` and 86 cells fail across the single-digit and 8/9 grids,
 * each naming its B, A and the error libpcre2 gave. Changing an expected octal
 * byte string fails that cell alone; asserting err 152 instead of 151 fails
 * all 12 overflow cells.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check05 check05_digits.c -ldl
 * Run:   check05 floors.txt
 */
#include "spec_common.h"

/* ^ (a){B} \run (a){A} $ */
static char *build(int B, const char *run, int A)
{
    static char buf[80000];
    size_t k = 0;
    buf[k++] = '^';
    for (int i = 0; i < B; i++) { memcpy(buf + k, "(a)", 3); k += 3; }
    buf[k++] = '\\';
    memcpy(buf + k, run, strlen(run)); k += strlen(run);
    for (int i = 0; i < A; i++) { memcpy(buf + k, "(a)", 3); k += 3; }
    buf[k++] = '$'; buf[k] = 0;
    return buf;
}

/* One backreference cell: predicted compile-vs-115 and predicted BACKREFMAX. */
static long cell_backref(int B, const char *run, int A, const char *bucket)
{
    int n = atoi(run), T = B + A;
    const char *pat = build(B, run, A);
    SpecVerdict v = spec_compile(pat);
    int want = (T >= n);

    if (!v.ok) {
        if (want)
            spec_fail("%s \\%s B=%d A=%d: predicted compile (T=%d >= %d), "
                      "got err %d", bucket, run, B, A, T, n, v.err);
        else if (v.err != 115)
            spec_fail("%s \\%s B=%d A=%d: predicted err 115 (T=%d < %d), "
                      "got err %d", bucket, run, B, A, T, n, v.err);
        return 1;
    }
    if (!want) {
        spec_fail("%s \\%s B=%d A=%d: predicted err 115 (T=%d < %d) but it "
                  "COMPILED — this is the octal-fallback direction the clause "
                  "forbids", bucket, run, B, A, T, n);
        return 1;
    }
    int bm = spec_backrefmax(pat);
    if (bm != n)
        spec_fail("%s \\%s B=%d A=%d: compiled but BACKREFMAX is %d, not %d — "
                  "libpcre2 did not read it as a backreference",
                  bucket, run, B, A, bm, n);
    return 1;
}

/* One octal cell: the pattern must compile, and must MATCH the byte string the
 * octal reading denotes — which is what distinguishes octal from a reference
 * that merely happens to compile. */
static long cell_octal(const char *run, const char *want_bytes, size_t want_len)
{
    char pat[64];
    snprintf(pat, sizeof pat, "^\\%s$", run);
    SpecVerdict v = spec_compile(pat);
    if (!v.ok) {
        spec_fail("octal \\%s: predicted compile, got err %d", run, v.err);
        return 1;
    }
    if (spec_matches_n(pat, want_bytes, want_len) != 1) {
        spec_fail("octal \\%s: compiled but does not match the byte string the "
                  "octal reading denotes — the digit run was consumed "
                  "differently than predicted", run);
    }
    return 1;
}

int main(int argc, char **argv)
{
    spec_start("check05_digits", argc, argv, NULL);
    long c1 = 0, c2 = 0, c89 = 0, c3 = 0, cov = 0;

    /* ---- CLAUSE 1: single digits \1..\9, full B x A grid ---------------- */
    for (int d = 1; d <= 9; d++) {
        char run[2] = { (char)('0' + d), 0 };
        for (int B = 0; B <= 9; B++)
            for (int A = 0; A <= 9; A++)
                c1 += cell_backref(B, run, A, "single");
    }
    /* \0 is the control: it IS octal always, at every count. If this cell ever
     * starts behaving like \1..\9, clause 1's "never falls back" has lost its
     * contrast and the grid above would still pass. */
    for (int B = 0; B <= 3; B++) {
        const char *pat = build(B, "0", 0);
        SpecVerdict v = spec_compile(pat);
        c1++;
        if (!v.ok) spec_fail("control \\0 B=%d: predicted compile (octal NUL), "
                             "got err %d", B, v.err);
        else if (spec_backrefmax(pat) != 0)
            spec_fail("control \\0 B=%d: BACKREFMAX nonzero — \\0 became a "
                      "reference, so clause 1's contrast is gone", B);
    }

    /* ---- CLAUSE 2: runs beginning 8/9, any length, any count ----------- */
    {
        static const char *const runs89[] = {
            "8", "9", "81", "89", "98", "99", "812", "899", "900", "989",
            NULL
        };
        for (int i = 0; runs89[i]; i++) {
            int n = atoi(runs89[i]);
            /* the run's own threshold, from both sides */
            c89 += cell_backref(0, runs89[i], n, "89.after");
            c89 += cell_backref(0, runs89[i], n - 1, "89.after");
            c89 += cell_backref(n, runs89[i], 0, "89.before");
            c89 += cell_backref(n - 1, runs89[i], 0, "89.before");
            /* split placement: same total, groups on both sides */
            c89 += cell_backref(n / 2, runs89[i], n - n / 2, "89.split");
            c89 += cell_backref(n / 2, runs89[i], n - n / 2 - 1, "89.split");
        }
        /* "any count" also means far from the threshold, not only at it */
        for (int A = 0; A <= 20; A++) c89 += cell_backref(0, "8", A, "89.grid");
        for (int A = 0; A <= 20; A++) c89 += cell_backref(0, "9", A, "89.grid");
        for (int B = 0; B <= 20; B++) c89 += cell_backref(B, "89", 0, "89.grid");
    }

    /* ---- CLAUSE 2b: leading 1..7 is decided by the RUNNING count -------- */
    /* The contrast that makes clause 2 mean something: a leading-1..7 run with
     * groups only AFTER it is octal, where the same shape with a leading 8 is
     * a backreference. Without this the "8/9 is different" claim is untested. */
    /* Swept as a grid rather than asserted on one example: for each run n, walk
     * B from 0 to n keeping the TOTAL fixed at n. Every cell has enough groups
     * in the pattern for a backreference to be valid, so the only thing that
     * can decide the cell is WHERE they are — which is exactly the running-vs-
     * total question. Predicted: backref iff B >= n, octal otherwise. */
    {
        static const char *const runs17[] = { "10", "11", "12", "13", "14",
                                              "15", "16", "17", "21", "34",
                                              "70", NULL };
        for (int i = 0; runs17[i]; i++) {
            int n = atoi(runs17[i]);
            for (int B = 0; B <= n; B++) {
                int A = n - B;
                const char *pat = build(B, runs17[i], A);
                SpecVerdict v = spec_compile(pat);
                c2++;
                if (!v.ok) {
                    spec_fail("running-count \\%s B=%d A=%d: predicted compile "
                              "(as %s), got err %d", runs17[i], B, A,
                              B >= n ? "backref" : "octal", v.err);
                    continue;
                }
                int bm = spec_backrefmax(pat);
                if (B >= n && bm != n)
                    spec_fail("running-count \\%s B=%d A=%d: predicted backref "
                              "%d, BACKREFMAX is %d", runs17[i], B, A, n, bm);
                if (B < n && bm != 0)
                    spec_fail("running-count \\%s B=%d A=%d: predicted OCTAL "
                              "(only %d groups precede it), but BACKREFMAX is "
                              "%d — the TOTAL count decided it, and clause 2's "
                              "8/9 exception then has no contrast",
                              runs17[i], B, A, B, bm);
            }
        }
    }

    /* ---- CLAUSE 3: octal fallback, at most three digits, overflow 151 --- */
    c3 += cell_octal("101", "A", sizeof "A" - 1);         /* 0101 = 65 = 'A' */
    c3 += cell_octal("1234", "S4", sizeof "S4" - 1);       /* 0123 = 'S', then literal '4' */
    c3 += cell_octal("12345", "S45", sizeof "S45" - 1);
    c3 += cell_octal("1000", "@0", sizeof "@0" - 1);       /* 0100 = '@', then literal '0' */
    c3 += cell_octal("1001", "@1", sizeof "@1" - 1);
    c3 += cell_octal("10000", "@00", sizeof "@00" - 1);     /* still three digits, then two */
    c3 += cell_octal("012", "\012", sizeof "\012" - 1);      /* \0 form: three digits incl. the 0 */
    c3 += cell_octal("0123", "\0123", sizeof "\0123" - 1);    /* ...then literal '3' */
    c3 += cell_octal("01234", "\012" "34", 3);
    c3 += cell_octal("00", "\0", sizeof "\0" - 1);         /* short runs stop at the run's end */
    c3 += cell_octal("000", "\0", sizeof "\0" - 1);
    c3 += cell_octal("0000", "\0" "0", 2);
    c3 += cell_octal("377", "\377", sizeof "\377" - 1);      /* the top of the range */
    c3 += cell_octal("376", "\376", sizeof "\376" - 1);
    c3 += cell_octal("40", " ", sizeof " " - 1);          /* 040 = 32 = space: two digits */
    c3 += cell_octal("101", "A", sizeof "A" - 1);
    c3 += cell_octal("1017", "A7", sizeof "A7" - 1);
    c3 += cell_octal("176", "~", sizeof "~" - 1);
    c3 += cell_octal("1760", "~0", sizeof "~0" - 1);
    /* Every leading digit 1..7 reaches octal fallback, not just some: one
     * three-digit cell per leading digit that stays inside \377. */
    c3 += cell_octal("100", "@", sizeof "@" - 1);
    c3 += cell_octal("200", "\200", sizeof "\200" - 1);
    c3 += cell_octal("300", "\300", sizeof "\300" - 1);
    c3 += cell_octal("240", "\240", sizeof "\240" - 1);
    c3 += cell_octal("340", "\340", sizeof "\340" - 1);

    /* overflow: the three digits READ are above \377, at any run length.
     * The long runs here are the cells that killed the first predictor. */
    {
        static const char *const over[] = { "400", "401", "500", "600",
                                            "700", "777", "477", "677",
                                            "7777", "4000", "40000", "7770",
                                            NULL };
        for (int i = 0; over[i]; i++) {
            char pat[32];
            snprintf(pat, sizeof pat, "^\\%s$", over[i]);
            SpecVerdict v = spec_compile(pat);
            cov++;
            if (v.ok)
                spec_fail("overflow \\%s: predicted err 151, but it COMPILED",
                          over[i]);
            else if (v.err != 151)
                spec_fail("overflow \\%s: predicted err 151, got err %d",
                          over[i], v.err);
        }
    }

    spec_pop("digits.single_cells", c1);
    spec_pop("digits.run_cells", c2);
    spec_pop("digits.leading89_cells", c89);
    spec_pop("digits.octal_fallback_cells", c3);
    spec_pop("digits.overflow_cells", cov);

    static const char *const owned[] = {
        "digits.single_cells", "digits.run_cells", "digits.leading89_cells",
        "digits.octal_fallback_cells", "digits.overflow_cells"
    };
    spec_floors_require(owned, 5);
    return spec_finish();
}
