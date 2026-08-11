/* check04_class_position.c — INVARIANT 4: class-position expectation, external.
 *
 * THE PROMISE. "For the 44 class-reachable rows (41 esc + 3 class-bracket):
 * the two-valued expectation column (compile-as-what / error N) matches
 * libpcre2 on the row's class probe SET (including endpoint-adjacent probes
 * for delimiter-eaters). Populations printed per bucket with a ratcheting
 * floor; the 56 group/verb rows carry no value."
 *
 * WHAT A ROW'S CLASS-POSITION EXPECTATION IS. Two-valued: either the construct
 * COMPILES inside a class and denotes something (one character, or a set of
 * n), or it is an ERROR with a specific number. Nothing else. This check
 * measures that value for each of the 44 class-reachable rows and pins it in
 * class_expectations.inc; a row whose value moves fails, in either direction.
 *
 * WHY A PROBE SET AND NOT ONE PROBE. `[S]` alone cannot distinguish a
 * construct from a coincidence. The failure mode this hunts is a construct
 * whose class-position reading depends on what is NEXT to it — the escape that
 * silently falls back to a literal when it is not alone, or the delimiter-eater
 * that swallows a neighbour. So each row is probed in a set of positions and
 * the readings must COHERE:
 *
 *      bare        [S]           the reference reading
 *      before      [S~]          a literal '~' after it
 *      after       [~S]          a literal '~' before it
 *      negated     [^S]          must be the exact complement of bare
 *      in-a-class  [a-fS]        alongside a range
 *
 * Coherence is asserted as arithmetic on the CENSUSES, all of them libpcre2's:
 * census([S~]) must be census([S]) + {'~'}, census([~S]) the same, and
 * census([^S]) must be the exact 256-bit complement of census([S]). A
 * construct that reads differently with a neighbour breaks one of those
 * equations and is named.
 *
 * WHY '~' IS THE NEIGHBOUR. It must be absent from every row's syntax, so it
 * cannot collide with the construct's own text, AND outside every class-type
 * construct's set, or the arithmetic goes vacuous exactly where it matters:
 * with 'q' as the neighbour, `[[:alpha:]q]` has the same census as
 * `[[:alpha:]]` — q is already a letter — so the equation holds no matter what
 * the construct did. '~' (0x7e) is in none of \d \s \w \h \v or
 * [:alpha:], and in no row's spelling.
 *
 * ENDPOINT-ADJACENT PROBES FOR THE DELIMITER-EATERS. `[:alpha:]`, `[.a.]` and
 * `[=a=]` scan forward for their own closing delimiter, so the probes that
 * matter are the ones where that delimiter is missing or early — where an
 * unbounded scan runs off the end of the class and takes the `]` with it.
 * Those probes cannot be built by the pattern above (they are deliberately
 * truncated), so they are a separate bucket with its own floor.
 *
 * THE 56 GROUP/VERB ROWS. They carry no class-position value: `(` inside a
 * class is an ordinary character. The check asserts that too, once the column
 * exists — a group row with a class-position expectation would be a claim that
 * the construct is reachable there, and it is not.
 *
 * SABOTAGE (verified 2026-08-11): corrupt one entry in class_expectations.inc
 * (`\d` from "set 10" to "set 11") and exactly that row fails, naming both the
 * pinned and the measured value. Changing the neighbour from '~' to 'a' makes
 * the rows whose syntax contains an 'a' (`[.a.]`, `[=a=]`, `\N{name}`) unable
 * to distinguish their own text from the neighbour; changing it to 'q' makes
 * the `[:alpha:]` row's arithmetic vacuous, which is why it is neither.
 *
 * AWAITED SURFACE. `pcrec --list-syntax` has no class-position expectation
 * column: its 12 columns are kind selector syntax module feature flavours
 * engines status diag flags expect note, and `expect` holds diagnostic TEXT
 * for the rows that reject, not a two-valued class-position verdict. The
 * oracle half — all 44 rows, all probe sets, the census arithmetic, the pinned
 * table — runs now.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check04 check04_class_position.c -ldl
 * Run:   check04 floors.txt registry.tsv [--emit-pins]
 */
#include "spec_common.h"

/* census of `[body]`: 0 and the set on success, else the error number. */
static int census(const char *body, unsigned char set[256], int *n)
{
    char pat[512];
    snprintf(pat, sizeof pat, "^[%s]$", body);
    SpecVerdict v = spec_compile(pat);
    memset(set, 0, 256);
    *n = 0;
    if (!v.ok) return v.err;
    for (int b = 0; b < 256; b++) {
        char sub = (char)b;
        if (spec_matches_n(pat, &sub, 1) == 1) { set[b] = 1; (*n)++; }
    }
    return 0;
}

/* The two-valued expectation, rendered as a short stable string:
 *   "err N"        the class does not compile
 *   "char 0xNN"    it compiles and denotes exactly one character
 *   "set N"        it compiles and denotes N characters                    */
static void expectation(const char *S, char *out, size_t sz)
{
    unsigned char set[256]; int n = 0;
    int e = census(S, set, &n);
    if (e) { snprintf(out, sz, "err %d", e); return; }
    if (n == 1) {
        for (int b = 0; b < 256; b++)
            if (set[b]) { snprintf(out, sz, "char 0x%02x", b); return; }
    }
    snprintf(out, sz, "set %d", n);
}

/* Emit one pin as C source. Backslashes must be doubled: every escape row's
 * syntax starts with one, and an unescaped `\d` in a C string literal is a
 * different (and warned-about) thing entirely. */
static void emit_pin(const char *S, const char *got)
{
    printf("{ \"");
    for (const char *p = S; *p; p++) {
        if (*p == '\\' || *p == '"') putchar('\\');
        putchar(*p);
    }
    printf("\", \"%s\" },\n", got);
}

typedef struct { const char *syntax; const char *expect; } Pin;
static const Pin PINS[] = {
#include "class_expectations.inc"
    { NULL, NULL }
};

static const char *pinned_for(const char *S)
{
    for (int i = 0; PINS[i].syntax; i++)
        if (!strcmp(PINS[i].syntax, S)) return PINS[i].expect;
    return NULL;
}

int main(int argc, char **argv)
{
    const char *rp = NULL;
    spec_start("check04_class_position", argc, argv, &rp);
    int emit = (argc > 3 && !strcmp(argv[3], "--emit-pins"));

    long esc_rows = 0, bracket_rows = 0, probe_cells = 0, adj_cells = 0;
    long noclass_rows = 0;

    for (int i = 0; i < spec_nrows; i++) {
        const SpecRow *r = &spec_rows[i];
        const char *kind = spec_col(r, SPEC_COL_KIND);
        const char *S = spec_col(r, SPEC_COL_SYNTAX);
        int is_esc = !strcmp(kind, "esc");
        int is_bracket = !strcmp(kind, "class-bracket");
        char inner[256];

        if (!is_esc && !is_bracket) { noclass_rows++; continue; }
        if (is_bracket) {
            size_t L = strlen(S);
            snprintf(inner, sizeof inner, "%.*s", (int)(L - 2), S + 1);
            S = inner;
            bracket_rows++;
        } else esc_rows++;

        char got[64];
        expectation(S, got, sizeof got);
        if (emit) { emit_pin(S, got); continue; }

        const char *pin = pinned_for(S);
        if (!pin)
            spec_fail("row '%s' has no pinned class-position expectation — "
                      "add it to class_expectations.inc (regenerate with "
                      "--emit-pins); an unpinned row is unchecked", S);
        else if (strcmp(pin, got))
            spec_fail("row '%s': pinned class-position expectation is '%s', "
                      "libpcre2 now says '%s'", S, pin, got);

        /* ---- the probe set, and the census arithmetic ------------------- */
        unsigned char bare[256], with[256]; int nb = 0, nw = 0;
        int ebare = census(S, bare, &nb);
        probe_cells++;
        if (ebare) {
            char probe[512];
            /* A LEXICAL construct contributes no atom, so `[S]` is the EMPTY
             * class — err 106, and about the class, not the construct. Its
             * coherence claim is the opposite one: `[Sq]` must be exactly
             * `[q]`, because the construct vanished. Without this branch \E
             * looks like a construct that reads differently beside a
             * neighbour, which is the reverse of what it is. */
            if (spec_is_lexical(S)) {
                unsigned char justq[256]; int nq = 0;
                census("~", justq, &nq);
                const char *lforms[] = { "%s~", "~%s", NULL };
                for (int f = 0; lforms[f]; f++) {
                    snprintf(probe, sizeof probe, lforms[f], S);
                    int e2 = census(probe, with, &nw);
                    probe_cells++;
                    if (e2) {
                        spec_fail("lexical row '%s': `[%s]` is err %d, but a "
                                  "construct that contributes no atom should "
                                  "leave `[~]` behind", S, probe, e2);
                        continue;
                    }
                    for (int b = 0; b < 256; b++)
                        if (with[b] != justq[b]) {
                            spec_fail("lexical row '%s': `[%s]` is not "
                                      "identical to `[~]` at byte 0x%02x — it "
                                      "did not vanish", S, probe, b);
                            break;
                        }
                }
                continue;
            }
            /* an erroring construct must error the same way with a neighbour:
             * the error is the construct's, not the class's */
            const char *forms[] = { "%s~", "~%s", "a-f%s", NULL };
            for (int f = 0; forms[f]; f++) {
                snprintf(probe, sizeof probe, forms[f], S);
                int e2 = census(probe, with, &nw);
                probe_cells++;
                if (e2 == 0)
                    spec_fail("row '%s' is 'err %d' alone but `[%s]` COMPILES "
                              "— the construct's class-position reading depends "
                              "on its neighbours", S, ebare, probe);
            }
            continue;
        }

        {
            char probe[512];
            /* [Sq] and [qS] must be exactly bare + {'q'} */
            const char *forms[] = { "%s~", "~%s", NULL };
            for (int f = 0; forms[f]; f++) {
                snprintf(probe, sizeof probe, forms[f], S);
                int e2 = census(probe, with, &nw);
                probe_cells++;
                if (e2) {
                    spec_fail("row '%s' compiles alone but `[%s]` is err %d",
                              S, probe, e2);
                    continue;
                }
                for (int b = 0; b < 256; b++) {
                    int want = bare[b] || b == '~';
                    if (with[b] != want) {
                        spec_fail("row '%s': `[%s]` differs from `[%s]` plus "
                                  "'q' at byte 0x%02x — the construct reads "
                                  "differently next to a neighbour",
                                  S, probe, S, b);
                        break;
                    }
                }
            }
            /* [^S] must be the exact complement of [S] */
            snprintf(probe, sizeof probe, "^%s", S);
            int e3 = census(probe, with, &nw);
            probe_cells++;
            if (e3) {
                spec_fail("row '%s' compiles but its negation `[%s]` is err %d",
                          S, probe, e3);
            } else {
                for (int b = 0; b < 256; b++)
                    if (with[b] == bare[b]) {
                        spec_fail("row '%s': `[^%s]` is not the complement of "
                                  "`[%s]` at byte 0x%02x", S, S, S, b);
                        break;
                    }
            }
        }
    }

    /* ---- endpoint-adjacent probes for the delimiter-eaters -------------- */
    {
        static const char *const adj[] = {
            "[:alpha:", "[:alpha", "[:", "[:]", "[:alpha:]~", "~[:alpha:]",
            "[.a.", "[.a", "[.", "[.]", "[.a.]~", "~[.a.]",
            "[=a=", "[=a", "[=", "[=]", "[=a=]~", "~[=a=]",
            "[:^digit:]", "[:<:]", "[:foo:]", "[:al:pha:]",
            NULL };
        for (int i = 0; adj[i]; i++) {
            unsigned char set[256]; int n = 0;
            int e = census(adj[i], set, &n);
            adj_cells++;
            /* The assertion is not "this must error": it is that libpcre2 has
             * a DEFINITE, stable verdict, pinned like every other row. A probe
             * whose verdict is unpinned is unchecked. */
            char got[64];
            if (e) snprintf(got, sizeof got, "err %d", e);
            else if (n == 1) {
                for (int b = 0; b < 256; b++)
                    if (set[b]) { snprintf(got, sizeof got, "char 0x%02x", b); break; }
            } else snprintf(got, sizeof got, "set %d", n);
            if (emit) { emit_pin(adj[i], got); continue; }
            const char *pin = pinned_for(adj[i]);
            if (!pin)
                spec_fail("endpoint-adjacent probe `[%s]` has no pin — measured "
                          "'%s'; add it to class_expectations.inc", adj[i], got);
            else if (strcmp(pin, got))
                spec_fail("endpoint-adjacent probe `[%s]`: pinned '%s', "
                          "libpcre2 now says '%s'", adj[i], pin, got);
        }
    }

    if (emit) return 0;

    printf("  class-reachable rows: %ld esc + %ld bracket = %ld; "
           "rows carrying no class value: %ld\n",
           esc_rows, bracket_rows, esc_rows + bracket_rows, noclass_rows);
    spec_pop("class.esc_rows", esc_rows);
    spec_pop("class.bracket_rows", bracket_rows);
    spec_pop("class.probe_cells", probe_cells);
    spec_pop("class.adjacent_cells", adj_cells);
    spec_pop("class.noclass_rows", noclass_rows);

    static const char *const owned[] = {
        "class.esc_rows", "class.bracket_rows", "class.probe_cells",
        "class.adjacent_cells", "class.noclass_rows"
    };
    spec_floors_require(owned, 5);
    if (spec_fails) return spec_finish();

    return spec_await(
        "a two-valued class-position expectation column in `pcrec "
        "--list-syntax` (compile-as-what / error N)",
        "this check looks for a column named `class_expect` in the dump's "
        "header. For each of the 44 class-reachable rows it must equal the "
        "measured value pinned in class_expectations.inc, in the same "
        "vocabulary ('err N' / 'char 0xNN' / 'set N'); for the 56 group and "
        "verb rows it must be EMPTY, since those constructs are not reachable "
        "inside a class at all. The `expect` column that exists today is "
        "diagnostic TEXT for rejecting rows and is not this");
}
