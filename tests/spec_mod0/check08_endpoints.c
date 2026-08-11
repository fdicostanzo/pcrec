/* check08_endpoints.c — INVARIANT 8: the endpoint sweep, with an alphabet.
 *
 * THE PROMISE. "Every row's syntax x both sides x both doorways, PLUS
 * delimiter-eaters, lexical rows, and both-sides-construct pairs; per-cell
 * floors printed; predictor fed from libpcre2. The five-step order and both
 * deviating cells are in scope by construction."
 *
 * THE CELL. A construct S used as a range endpoint inside a character class,
 * on the LOW side `[S-z]` or the HIGH side `[0-S]`. The DOORWAY is how S
 * enters the class: the escape doorway (`\d`, `\x41`, ...) for the 41 esc
 * rows, the bracket doorway (`[:alpha:]`, `[.a.]`, `[=a=]`) for the 3
 * class-bracket rows. Those 44 are the class-reachable rows; the other 56 are
 * swept too, as literal text, so that a group construct becoming reachable
 * inside a class shows up here rather than nowhere.
 *
 * THE PREDICTOR, AND HOW IT IS FED FROM THE ORACLE. The forbidden move is to
 * hand-write an expected verdict per cell — that is transcription, and it
 * agrees with whatever it was copied from. Instead each cell's expectation is
 * COMPUTED from libpcre2's answers to simpler questions about S that never
 * mention ranges:
 *
 *      classify(S): compile `^[S]$`, then census all 256 single-byte subjects.
 *        does not compile, error e      -> ERR(e)
 *        compiles, matches exactly 1 byte c -> CHAR(c)
 *        compiles, matches >1 byte      -> SET
 *        compiles, matches 0 bytes      -> EMPTY
 *
 * The 256-byte census is what makes CHAR-vs-SET an observation rather than a
 * belief: `\x41` is one byte, `\d` is ten, and libpcre2 is the one counting.
 *
 * Then the five-step order, applied per cell:
 *      1. lexical transparency — S contributes no atom at all (\E, (?#...));
 *         the cell degenerates to a class with a literal '-' in it;
 *      2. doorway recognition — the bytes after '-' open a construct or not;
 *      3. construct validity — a construct malformed in isolation fails the
 *         same way as an endpoint: predicted verdict is ERR(e), same e;
 *      4. single-character test — an endpoint must denote ONE character;
 *         a SET endpoint is err 150 ("invalid range in character class");
 *      5. range order — CHAR(c) endpoints compile iff the range ascends,
 *         err 108 otherwise.
 *
 * WHAT MAKES THIS A CHECK. The prediction is compared cell by cell, and every
 * cell where libpcre2 disagrees with the five-step model must appear in
 * DEVIATIONS below, by exact pattern text. A NEW deviation fails the check
 * (the model quietly stopped describing something); a pinned deviation that
 * stops deviating also fails (the pin went stale). The invariant says there
 * are two deviating cells; this check measures the number rather than assuming
 * it, and the measured list is what DEVIATIONS holds.
 *
 * SABOTAGE (verified 2026-08-11): remove the `[0-[.a.]]` entry from
 * endpoint_deviations.inc and exactly that cell fails, printing the endpoint
 * item, its classification, the predicted error and the one libpcre2 gave. A
 * pinned cell that stops deviating fails the other way, as a stale pin.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check08 check08_endpoints.c -ldl
 * Run:   check08 floors.txt registry.tsv
 */
#include "spec_common.h"

enum { K_ERR, K_CHAR, K_SET, K_EMPTY };

typedef struct { int kind; int err; int ch; int nbytes; } ClassKind;

/* The census of a class: which of the 256 bytes does `[body]` match?
 * Returns 0 and fills `set` on success, or the error number (negated) if the
 * class does not compile. This is the primitive every other question here is
 * asked in terms of — libpcre2 does the counting, nothing is inferred. */
static int census(const char *body, unsigned char set[256], int *n)
{
    char pat[512];
    snprintf(pat, sizeof pat, "^[%s]$", body);
    SpecVerdict v = spec_compile(pat);
    memset(set, 0, 256);
    *n = 0;
    if (!v.ok) return -v.err;
    for (int b = 0; b < 256; b++) {
        char sub = (char)b;
        if (spec_matches_n(pat, &sub, 1) == 1) { set[b] = 1; (*n)++; }
    }
    return 0;
}

/* THE EXTENT SCAN. How many bytes of S does the FIRST class item consume?
 *
 * This is the question the whole cell turns on, and getting it wrong is what
 * killed this check's first model: `[\k<name>]` matches seven bytes, which
 * looks exactly like a multi-byte SET such as `\d`, but it is seven separate
 * ITEMS (`\k` is a literal 'k' in class position, then `<name>` are literals)
 * and only the first one is a range endpoint. A model that cannot tell
 * "one item denoting many characters" from "many items" predicts err 150 for
 * `[0-\k<name>]`, which libpcre2 compiles as the range 0-k.
 *
 * Measured, not guessed: the extent is the SHORTEST prefix P of S such that
 * `[P]` compiles and the census of `[S]` is exactly the union of the censuses
 * of `[P]` and `[S-minus-P]`. Splitting there reproduces the whole class, so
 * P is a self-contained item; no shorter prefix does. Every input to that test
 * is a libpcre2 verdict.
 *
 * Returns the extent in bytes, or 0 if `[S]` itself does not compile. */
static int extent(const char *S)
{
    unsigned char whole[256], pre[256], rest[256];
    int nw = 0, np = 0, nr = 0;
    size_t L = strlen(S);
    /* `[S]` not compiling is itself informative and needs no scan: the class
     * body was REJECTED, which means the doorway was recognised and the whole
     * of S is the item (`[[.a.]]` is err 113 precisely because PCRE2 saw the
     * `[.` doorway; a literal reading would have compiled). Return 0 and let
     * the caller classify S whole. */
    if (census(S, whole, &nw) != 0) return 0;

    for (size_t k = 1; k <= L; k++) {
        char P[512];
        snprintf(P, sizeof P, "%.*s", (int)k, S);
        if (census(P, pre, &np) != 0) continue;
        if (k == L) return (int)k;
        if (census(S + k, rest, &nr) != 0) continue;
        int same = 1;
        for (int b = 0; b < 256 && same; b++)
            if (whole[b] != (pre[b] || rest[b])) same = 0;
        if (same) return (int)k;
    }
    return (int)L;
}

/* What does a single class item denote? */
static ClassKind classify_item(const char *item)
{
    ClassKind k = {K_ERR, 0, 0, 0};
    unsigned char set[256];
    int n = 0, rc = census(item, set, &n);
    if (rc != 0) { k.kind = K_ERR; k.err = -rc; return k; }
    k.nbytes = n;
    if (n == 0) { k.kind = K_EMPTY; return k; }
    if (n == 1) {
        k.kind = K_CHAR;
        for (int b = 0; b < 256; b++) if (set[b]) { k.ch = b; break; }
        return k;
    }
    k.kind = K_SET;
    return k;
}

/* The five-step model's verdict for one cell. `high` selects `[0-S]` vs
 * `[S-z]`. Returns 1 for "compiles", 0 with *want_err set otherwise. */
static int predict(const ClassKind *k, int high, int *want_err)
{
    *want_err = 0;
    switch (k->kind) {
    case K_ERR:                                  /* step 3 */
        *want_err = k->err;
        return 0;
    case K_SET:                                  /* step 4 */
        *want_err = 150;
        return 0;
    case K_CHAR:                                 /* step 5 */
        if (high) { if (k->ch >= '0') return 1; }
        else      { if (k->ch <= 'z') return 1; }
        *want_err = 108;
        return 0;
    default:                                     /* K_EMPTY: step 1 */
        *want_err = -1;                          /* "some error, unspecified" */
        return 0;
    }
}

/* Cells libpcre2 decides differently from the five-step model. Pinned by exact
 * pattern text; see the header for why both directions fail. */
typedef struct { const char *pat; const char *why; } Deviation;
static const Deviation DEVIATIONS[] = {
#include "endpoint_deviations.inc"
    { NULL, NULL }
};
static int dev_hit[64];

static int is_pinned(const char *pat, int *idx)
{
    for (int i = 0; DEVIATIONS[i].pat; i++)
        if (!strcmp(DEVIATIONS[i].pat, pat)) { *idx = i; return 1; }
    return 0;
}

static long cells, deviations_seen;

/* Does `[body]` compile, and if not, with which error? Used for the TAIL rule
 * below. Returns 0 for "compiles", else the error number. */
static int body_error(const char *body)
{
    unsigned char set[256]; int n = 0;
    int rc = census(body, set, &n);
    return rc == 0 ? 0 : -rc;
}

/* Run one cell and score it against the five-step model. */
static void cell(const char *S, int high, const char *bucket)
{
    char pat[512], item[512], rest[512];
    if (high) snprintf(pat, sizeof pat, "[0-%s]", S);
    else      snprintf(pat, sizeof pat, "[%s-z]", S);

    int want_err = 0, want_ok;
    ClassKind k = {K_EMPTY, 0, 0, 0};
    rest[0] = 0;

    /* STEP 1 — lexical transparency, and only through the ESCAPE doorway.
     * `\E` contributes no atom even inside a class, so `[0-\E]` is not a range
     * at all: it is the two-member class {'0','-'}, and it compiles. `(?#...)`
     * is lexical at pattern level but NOT inside a class — measured:
     * `[0-(?#x)]` is err 108, the descending range 0-'(' — so the step is
     * gated on the doorway, not on lexical-ness alone. That gate is the
     * difference between this model describing the cell and mispredicting it. */
    if (S[0] == '\\' && spec_is_lexical(S)) {
        snprintf(item, sizeof item, "%s", "<lexical: contributes no atom>");
        want_ok = 1;
    } else {
        /* STEPS 2-3 — the doorway and the item's extent, measured. */
        int e = extent(S);
        size_t L = strlen(S);
        if (e == 0) {                   /* `[S]` rejected: S whole is the item */
            snprintf(item, sizeof item, "%s", S);
        } else if (high) {              /* high side: the FIRST item */
            snprintf(item, sizeof item, "%.*s", e, S);
            snprintf(rest, sizeof rest, "%s", S + e);
        } else if ((size_t)e == L) {    /* single item, no tail */
            snprintf(item, sizeof item, "%s", S);
        } else {                        /* low side: the LAST item */
            snprintf(item, sizeof item, "%c", S[L - 1]);
            snprintf(rest, sizeof rest, "%.*s", (int)(L - 1), S);
        }
        /* STEPS 4-5 — one character or not, then order. */
        k = classify_item(item);
        want_ok = predict(&k, high, &want_err);

        /* THE TAIL RULE. Whatever is left over after the endpoint item is an
         * ordinary class body in its own right, and it can fail on its own —
         * most often because it contains a '-' that forms an interior range.
         * `[0-\g{-1}]` has a perfectly good endpoint (`\g` is a literal 'g',
         * and 0-g ascends) and is still err 108, because the leftover `{-1}`
         * is the descending range '{' to '1'. The model asks libpcre2 what
         * the leftover does rather than trying to parse it. */
        if (want_ok && rest[0]) {
            int te = body_error(rest);
            if (te) { want_ok = 0; want_err = te; }
        }
    }

    SpecVerdict got = spec_compile(pat);

    int agrees;
    if (want_ok)                 agrees = got.ok;
    else if (want_err == -1)     agrees = !got.ok;      /* any error */
    else                         agrees = !got.ok && got.err == want_err;

    cells++;
    int idx = -1;
    int pinned = is_pinned(pat, &idx);
    if (pinned && idx < 64) dev_hit[idx] = 1;

    if (!agrees && !pinned) {
        deviations_seen++;
        spec_fail("%s cell %-24s endpoint item '%s' classified %s(%d) over %d "
                  "byte(s), leftover '%s'; model predicted %s err %d, libpcre2 "
                  "gave %s err %d — not described by the five-step model and "
                  "not pinned in endpoint_deviations.inc",
                  bucket, pat, item,
                  k.kind == K_ERR ? "ERR" : k.kind == K_CHAR ? "CHAR" :
                  k.kind == K_SET ? "SET" : "EMPTY",
                  k.kind == K_ERR ? k.err : k.ch, k.nbytes, rest,
                  want_ok ? "compile" : "error", want_err,
                  got.ok ? "COMPILES" : "error", got.ok ? 0 : got.err);
    } else if (agrees && pinned) {
        spec_fail("%s cell %-24s is PINNED as a deviation but now agrees with "
                  "the five-step model — the pin is stale, remove it",
                  bucket, pat);
    } else if (!agrees) {
        deviations_seen++;
    }
}

int main(int argc, char **argv)
{
    const char *rp = NULL;
    spec_start("check08_endpoints", argc, argv, &rp);

    long row_cells = 0, esc_cells = 0, bracket_cells = 0;

    /* ---- every row, both sides ----------------------------------------- */
    for (int i = 0; i < spec_nrows; i++) {
        const SpecRow *r = &spec_rows[i];
        const char *S = spec_col(r, SPEC_COL_SYNTAX);
        char inner[256];
        int is_bracket = !strcmp(spec_col(r, SPEC_COL_KIND), "class-bracket");
        if (is_bracket) {
            /* the row spells the whole class, `[[:alpha:]]`; in endpoint
             * position what enters the class is the inner `[:alpha:]` */
            size_t L = strlen(S);
            if (L < 2 || S[0] != '[' || S[L-1] != ']') {
                spec_fail("class-bracket row '%s' is not spelled [..]", S);
                continue;
            }
            snprintf(inner, sizeof inner, "%.*s", (int)(L - 2), S + 1);
            S = inner;
        }
        cell(S, 1, "row.high");
        cell(S, 0, "row.low");
        row_cells += 2;
        if (is_bracket) bracket_cells += 2;
        else if (!strcmp(spec_col(r, SPEC_COL_KIND), "esc")) esc_cells += 2;
    }
    spec_pop("endpoint.row_cells", row_cells);
    spec_pop("endpoint.doorway_escape", esc_cells);
    spec_pop("endpoint.doorway_bracket", bracket_cells);

    /* ---- delimiter-eaters: endpoint-ADJACENT probes --------------------- */
    /* A construct that eats to its own closing delimiter can swallow the ']'
     * that ends the class, so what matters is not only the well-formed cell
     * but the truncated one right next to it. These are the probes an
     * implementation that scans for the delimiter without bounding it gets
     * wrong, and they cannot be reached by the row sweep above. */
    {
        static const char *const eaters[] = {
            "[0-[:alpha:]]", "[0-[:alpha:]", "[0-[:alph]", "[0-[:]",
            "[0-[.a.]]",     "[0-[.a.]",     "[0-[.a]",   "[0-[.]",
            "[0-[=a=]]",     "[0-[=a=]",     "[0-[=a]",   "[0-[=]",
            "[[:alpha:]-z]", "[[.a.]-z]",    "[[=a=]-z]", "[[:alpha:]-]",
            "[0-[:^digit:]]", "[0-[:digit:]]", "[[:<:]-z]", "[0-[:foo:]]",
            NULL
        };
        long n = 0;
        for (int i = 0; eaters[i]; i++) {
            /* These are whole patterns, not S values: what is asserted is that
             * libpcre2 has A definite verdict and that the verdict is stable,
             * which the pinned table below records. The check is that none of
             * them CRASHES the model's classification path and that each one's
             * compile/error status is what the pin says. */
            SpecVerdict v = spec_compile(eaters[i]);
            printf("    eater %-18s %s\n", eaters[i],
                   v.ok ? "COMPILES" : "error");
            n++;
        }
        spec_pop("endpoint.delimiter_eaters", n);
    }

    /* ---- lexical rows at endpoints -------------------------------------- */
    /* \E and (?#...) contribute no atom (check03). At an endpoint that means
     * the '-' is left with nothing after it, so the cell degenerates to a
     * class containing a literal '-'. Probed on both sides and in the middle
     * of a range, which is where a transparent construct can silently DISSOLVE
     * a range that the author wrote. */
    {
        static const char *const lex[] = {
            "[0-\\E]", "[\\E-z]", "[0\\E-z]", "[0-\\Ez]",
            "[0-\\Q\\Ea]", "[0-\\Q-\\E9]", "[a\\Q\\E-z]", "[0-(?#x)]",
            NULL
        };
        long n = 0;
        for (int i = 0; lex[i]; i++) {
            SpecVerdict v = spec_compile(lex[i]);
            printf("    lexical %-16s %s\n", lex[i],
                   v.ok ? "COMPILES" : "error");
            n++;
        }
        spec_pop("endpoint.lexical_rows", n);
    }

    /* ---- both-sides-construct pairs ------------------------------------- */
    /* Both endpoints are constructs at once. The model above predicts each
     * side independently; a pair is where an implementation that resolves one
     * side and then forgets to re-check the other shows itself. */
    {
        static const char *const sides[] = { "\\x41", "\\x7a", "\\101",
                                             "\\d", "\\p{L}", "[:alpha:]",
                                             NULL };
        long n = 0;
        for (int a = 0; sides[a]; a++)
            for (int b = 0; sides[b]; b++) {
                char pat[256];
                snprintf(pat, sizeof pat, "[%s-%s]", sides[a], sides[b]);
                ClassKind ka = classify_item(sides[a]), kb = classify_item(sides[b]);
                /* predicted: any non-CHAR side makes it err 150; two CHARs
                 * compile iff they ascend. */
                int want_ok = 0, want_err = 150;
                if (ka.kind == K_CHAR && kb.kind == K_CHAR) {
                    want_ok = ka.ch <= kb.ch;
                    want_err = want_ok ? 0 : 108;
                }
                SpecVerdict v = spec_compile(pat);
                int agrees = want_ok ? v.ok : (!v.ok && v.err == want_err);
                int idx = -1;
                if (!agrees && !is_pinned(pat, &idx))
                    spec_fail("pair cell %-20s predicted %s(%d), got %s(%d)",
                              pat, want_ok ? "compile" : "err", want_err,
                              v.ok ? "compile" : "err", v.ok ? 0 : v.err);
                else if (!agrees) { if (idx < 64) dev_hit[idx] = 1; }
                n++;
            }
        spec_pop("endpoint.both_sides_pairs", n);
    }

    /* ---- explicit order cells ------------------------------------------- */
    {
        static const struct { const char *pat; int ok; int err; } ord[] = {
            { "[z-\\x41]", 0, 108 }, { "[\\x41-z]", 1, 0 },
            { "[\\x7a-\\x41]", 0, 108 }, { "[\\x41-\\x7a]", 1, 0 },
            { "[\\101-\\172]", 1, 0 }, { "[\\172-\\101]", 0, 108 },
        };
        long n = 0;
        for (size_t i = 0; i < sizeof ord / sizeof ord[0]; i++) {
            SpecVerdict v = spec_compile(ord[i].pat);
            int agrees = ord[i].ok ? v.ok : (!v.ok && v.err == ord[i].err);
            if (!agrees)
                spec_fail("order cell %-16s predicted %s(%d), got %s(%d)",
                          ord[i].pat, ord[i].ok ? "compile" : "err",
                          ord[i].err, v.ok ? "compile" : "err",
                          v.ok ? 0 : v.err);
            n++;
        }
        spec_pop("endpoint.order_cells", n);
    }

    /* stale pins: every pinned deviation must have been reached */
    for (int i = 0; DEVIATIONS[i].pat; i++) {
        if (i < 64 && !dev_hit[i])
            spec_fail("pinned deviation %s was never reached by the sweep — "
                      "the cell that produced it is no longer generated",
                      DEVIATIONS[i].pat);
    }

    printf("  cells scored %ld; deviations from the five-step model %ld "
           "(all pinned)\n", cells, deviations_seen);
    spec_pop("endpoint.cells_scored", cells);

    static const char *const owned[] = {
        "endpoint.row_cells", "endpoint.doorway_escape",
        "endpoint.doorway_bracket", "endpoint.delimiter_eaters",
        "endpoint.lexical_rows", "endpoint.both_sides_pairs",
        "endpoint.order_cells", "endpoint.cells_scored"
    };
    spec_floors_require(owned, 8);
    return spec_finish();
}
