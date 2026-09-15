/*
 * driver.c — runs a single generated matcher against one subject string.
 *
 * Usage: t <subject> [startpos] [route] [mode]
 *   <subject> is the inner text of a .rxt `m`/`n`/`ms`/`ns` line's
 *   double-quoted subject, with surrounding quotes already stripped by
 *   run.sh but its escapes (\" \\ \n \t \r \f \v \xHH) still encoded as
 *   literal backslash sequences — this program decodes them.
 *
 *   [DD-13b.W23.3, H15/H6] AN `@`-PREFIXED SUBJECT NAMES A FILE, and its
 *   bytes are taken BYTE-EXACT: no escape decoding, no NUL handling, no
 *   encoding assumption, no trailing-newline rule. `@path` is the whole
 *   argument and the rest of it is the path. That is what makes
 *   `format_design.md` §2.18's `@file:"path"` subject real rather than
 *   approximated — a subject carrying a NUL and invalid UTF-8 reaches the
 *   matcher as the file holds it, which no escape vocabulary routed
 *   through argv could express (argv cannot carry a NUL at all).
 *
 *   THE PREFIX IS A MARKER AND THEREFORE A COLLISION, and run.sh closes it
 *   on the OTHER side: a literal quoted subject whose first byte is `@`
 *   is staged with that byte written `\x40`, which this decoder already
 *   produces as `@`. Three corpus subjects begin with `@` (MEASURED), so
 *   the collision is live rather than theoretical, and the escape is
 *   byte-exact rather than a special case here.
 *
 *   [mode] ([DD-13b.W23.3], H7) selects WHAT IS ASKED, and defaults to the
 *   single-search question every existing invocation asks:
 *     "one" (or absent)  one `<prefix>_search` from [startpos]; the
 *                        match/nomatch/give-up protocol below, unchanged.
 *     "count"            `docs/spec/match_api.md` §3.1's FIND-ALL LOOP,
 *                        printing `count <n>`. This is the `mc` line's
 *                        question (format_design §2.21) and the loop is
 *                        §3.1's, transcribed — the empty-match advance
 *                        goes through the artifact's own
 *                        `<prefix>_next_pos` residual, never a literal
 *                        `+ 1` and never the bench's `max(end, pos+1)`,
 *                        which double-counts an empty match found beyond
 *                        the scan position.
 *   [startpos] is an optional non-negative decimal integer passed as
 *   rx_search's startpos argument; if omitted, startpos defaults to 0
 *   (the `m`/`n` directives always mean startpos 0; `ms`/`ns` pass it
 *   explicitly — see docs/testing.md).
 *   [route] ([DD-14.FB], run.sh's `frames-buffer=` directive) names WHICH
 *   ENTRY runs the case, and it is the only thing it changes — the same
 *   subject, the same startpos, the same printed protocol:
 *     "default" (or absent)  rx_search
 *     "null"                 rx_search_in(..., NULL). Spec §10.3 defines
 *                            this to be EXACTLY the call above, so a corpus
 *                            run through this route must agree with a
 *                            default run cell for cell — which is what makes
 *                            it a control rather than a variant.
 *     "<frames>,<trail>"     rx_search_in with two malloc'd regions of those
 *     "<n>"                  CAPACITIES (a single number means both). The
 *                            two are separate on purpose: the trail binds
 *                            first at the stamped defaults (design §4's 4.49
 *                            trail entries per frame), and a route that
 *                            could only set them equal could not tell a
 *                            correct build from one that swapped them.
 *   The buffers are malloc'd, which satisfies RX_BUFFER_ALIGN by definition,
 *   and freed before this program returns; nothing reads them back. On a DFA
 *   artifact every route answers identically, because that engine's `_in`
 *   entries ignore the descriptor (spec §10.4).
 *
 * Prints exactly one line to stdout:
 *   "match %td %td [%td %td ...]\n"
 *                       (rx_search found a match: caps[0][0], caps[0][1] —
 *                        the whole-match span, [M4.4]/D44.2's caps-array
 *                        search signature — followed by caps[k][0]/caps[k][1]
 *                        for every k in [1, RX_NCAPS), [M4.5a]: today
 *                        RX_NCAPS is always 1 on a DFA-compiled artifact, so
 *                        the line is exactly "match %td %td\n" as before —
 *                        this is a superset, not a reshape. A .rxt `g`/`gp`
 *                        capture-expectation line picks its slot's pair out
 *                        of these fields by position; see docs/testing.md)
 *   "nomatch\n"         (rx_search found no match) — exits 0
 *   "count %zu\n"       ([DD-13b.W23.3], mode `count` only) the number of
 *                        matches §3.1's find-all loop reports — exits 0. A
 *                        give-up anywhere in the loop is NOT a count: it
 *                        prints its own word and exits 3 exactly as the
 *                        single-search path does, because a partial count
 *                        reported as a count is a wrong answer where a
 *                        give-up is a named outcome.
 *   "steps\n" / "frames\n" / "work\n" / "recurse\n"
 *                       ([K21-class fix, 2026-08-15; [DD-14] wave A,
 *                        2026-08-24, named the fourth code] rx_search found
 *                        neither: it GAVE UP, VM-artifact budget exhaustion,
 *                        and exits 3, not 0 — see the discrimination at the
 *                        call site below for why this is its own outcome,
 *                        never folded into "match" or "nomatch". Each typed
 *                        give-up code prints its own word — a code this
 *                        driver cannot name is mislabelled evidence, which
 *                        is exactly what a two-way `steps`-or-else compare
 *                        did to every non-STEPS code before this fix.
 *                        `recurse` (`PCREC_ERR_RECURSE`) is reserved with
 *                        no producer yet (D71 item 1), so no artifact prints
 *                        it today; it is named here anyway so a future
 *                        producer needs no driver change.)
 *   "internal\n"        ([DD-14] wave A commit 2, D71 item 1) rx_search
 *                        returned PCREC_ERR_INTERNAL, BELOW the give-up
 *                        floor and NOT a give-up: the artifact caught its
 *                        OWN analysis/emission inconsistency (module
 *                        'lookaround''s negative-polarity lookbehind
 *                        end-check is the one producer today). Still exits
 *                        3 like the four codes above -- this driver has no
 *                        third outcome shape to give it -- but run.sh's
 *                        `gu` directive (docs/testing.md) refuses to let
 *                        any corpus block EXPECT "internal": nothing may
 *                        plan for the artifact catching its own bug.
 * On a malformed escape in argv[1] or a malformed [startpos], prints a
 * message to stderr and exits 2.
 * EXIT 4 ([DD-14.FB]) is its own outcome and belongs to the anchored-entry
 * CROSS-CHECK below: on any route other than `default` the driver also runs
 * <prefix>_match_in and <prefix>_match_caps_in against their un-suffixed
 * siblings on the same ctx, and a disagreement exits 4 with the two values on
 * stderr. Distinct from 2 (this driver's own usage/input error) and from 3 (a
 * give-up) so run.sh can name it: see that cross-check's own comment for the
 * one divergence it permits.
 */

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

/* [DD-13b.W1.2] H11 — THE PREFIX IS A `-D`, NOT A HARD-CODED NAME.
 *
 * A `.rxt` source declares `target <prefix> = <definition>`, and each
 * target's artifact carries its own symbol prefix. This driver has to link
 * against whichever one it is handed, so the prefix became a compile-time
 * macro. `w1_impl.md` DECIDED (3) picks this over a generated shim: a shim
 * would put a second code generator inside the harness, whose output
 * nobody reviews.
 *
 * THE DEFAULT IS `rx`, SO EVERY EXISTING INVOCATION IS UNCHANGED. The
 * ordinary per-block path compiles with `-p rx` and passes no `-D` at all,
 * which is what keeps all 179 corpus files on a byte-identical build line.
 *
 * TWO MACROS AND NOT ONE, because C cannot case-convert a token: an
 * artifact's identifiers are `<prefix>_*` and its macros are `<PREFIX>_*`.
 * run.sh derives BOTH from one value, which is where their agreement
 * lives — and a mismatched pair cannot pass silently, because every use of
 * each names something the artifact either declares or does not, so a
 * wrong half is a compile error rather than a wrong answer.
 *
 * `rx_ctx` is NOT among them. It is one of the fixed-literal ABI types
 * (docs/spec/match_api.md §1/§2), unprefixed on every artifact on purpose,
 * so that differently-prefixed matchers compose in one TU. Prefixing it
 * here would be this driver inventing a rule the ABI does not have. */
#ifndef RXT_PREFIX
#define RXT_PREFIX  rx
#endif
#ifndef RXT_UPREFIX
#define RXT_UPREFIX RX
#endif
#define RXT_PASTE_(a, b) a##b
#define RXT_PASTE(a, b)  RXT_PASTE_(a, b)
/* `<prefix>_suffix` and `<PREFIX>_SUFFIX`. The pasted token is rescanned,
 * so RXMAC(_NCAPS) reaches the artifact's own `#define` and can be used
 * where a constant expression is required — an array bound, below. */
#define RXFN(suffix)  RXT_PASTE(RXT_PREFIX, suffix)
#define RXMAC(suffix) RXT_PASTE(RXT_UPREFIX, suffix)

static int hexval(unsigned char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/*
 * Decode escapes from src into a freshly malloc'd buffer. *out_len is set
 * to the decoded length (tracked explicitly; the buffer may contain \0
 * bytes, so it must never be measured with strlen). Returns the buffer,
 * or NULL on a malformed escape (message already printed to stderr).
 */
static unsigned char *decode(const char *src, size_t *out_len) {
    size_t srclen = strlen(src);
    /* Decoded output is never longer than the source. */
    unsigned char *buf = malloc(srclen > 0 ? srclen : 1);
    if (!buf) {
        fprintf(stderr, "driver: out of memory\n");
        return NULL;
    }

    size_t n = 0;
    for (size_t i = 0; i < srclen; i++) {
        unsigned char c = (unsigned char)src[i];
        if (c != '\\') {
            buf[n++] = c;
            continue;
        }
        i++;
        if (i >= srclen) {
            fprintf(stderr, "driver: trailing backslash in subject\n");
            free(buf);
            return NULL;
        }
        unsigned char e = (unsigned char)src[i];
        switch (e) {
            case '"':  buf[n++] = '"';  break;
            case '\\': buf[n++] = '\\'; break;
            case 'n':  buf[n++] = '\n'; break;
            case 't':  buf[n++] = '\t'; break;
            case 'r':  buf[n++] = '\r'; break;
            case 'f':  buf[n++] = '\f'; break;
            case 'v':  buf[n++] = '\v'; break;
            case 'x': {
                if (i + 2 >= srclen) {
                    fprintf(stderr, "driver: incomplete \\x escape\n");
                    free(buf);
                    return NULL;
                }
                int hi = hexval((unsigned char)src[i + 1]);
                int lo = hexval((unsigned char)src[i + 2]);
                if (hi < 0 || lo < 0) {
                    fprintf(stderr, "driver: invalid \\x escape\n");
                    free(buf);
                    return NULL;
                }
                buf[n++] = (unsigned char)((hi << 4) | lo);
                i += 2;
                break;
            }
            default:
                fprintf(stderr, "driver: invalid escape '\\%c'\n", e);
                free(buf);
                return NULL;
        }
    }

    *out_len = n;
    return buf;
}

/*
 * [DD-13b.W23.3, H15/H6] Read a whole file into a freshly malloc'd buffer,
 * BYTE-EXACT. *out_len is the file's length; the buffer may hold NULs and
 * ill-formed UTF-8 and neither is interpreted. Returns the buffer, or NULL
 * with a message already printed to stderr.
 *
 * NO `\n` RULE OF ANY KIND — not stripped, not required, not added. A
 * subject file IS its bytes (`format_design.md` §2.18: "The bytes are taken
 * BYTE-EXACT from the file"), and a driver that trimmed a trailing newline
 * would make every subject's own length a property of this program rather
 * than of the file, which is the one thing `sha256` exists to pin.
 *
 * An EMPTY file is a legitimate empty subject, so a 0-byte read is not an
 * error; `malloc(1)` keeps the pointer non-NULL, matching `decode`'s own
 * handling of an empty argument.
 */
static unsigned char *read_subject_file(const char *path, size_t *out_len) {
    FILE *f = fopen(path, "rb");
    size_t cap, n;
    unsigned char *buf;

    if (!f) {
        fprintf(stderr, "driver: cannot open subject file '%s'\n", path);
        return NULL;
    }
    cap = 4096; n = 0;
    buf = malloc(cap);
    if (!buf) {
        fprintf(stderr, "driver: out of memory\n");
        fclose(f);
        return NULL;
    }
    for (;;) {
        size_t got = fread(buf + n, 1, cap - n, f);
        n += got;
        if (n < cap) break;                 /* short read: EOF or error */
        {
            unsigned char *nb = realloc(buf, cap * 2);
            if (!nb) {
                fprintf(stderr, "driver: out of memory reading '%s'\n", path);
                free(buf); fclose(f);
                return NULL;
            }
            buf = nb; cap *= 2;
        }
    }
    if (ferror(f)) {
        fprintf(stderr, "driver: read error on subject file '%s'\n", path);
        free(buf); fclose(f);
        return NULL;
    }
    fclose(f);
    *out_len = n;
    return buf;
}

/*
 * Parse a startpos argument: must be all decimal digits (at least one),
 * fitting in a size_t. Returns 0 on success with *out set, -1 on a
 * malformed argument (message already printed to stderr).
 */
static int parse_startpos(const char *s, size_t *out) {
    if (!s || !*s) {
        fprintf(stderr, "driver: empty startpos argument\n");
        return -1;
    }
    size_t v = 0;
    for (const char *q = s; *q; q++) {
        if (*q < '0' || *q > '9') {
            fprintf(stderr, "driver: invalid startpos argument '%s'\n", s);
            return -1;
        }
        v = v * 10 + (size_t)(*q - '0');
    }
    *out = v;
    return 0;
}

/*
 * Parse a [route] argument into a call plan. Returns 0 on success, -1 on a
 * malformed route (message already printed to stderr).
 *
 * *use_in says whether to call rx_search_in at all; *have_buffers whether to
 * pass a descriptor rather than NULL. The two are separate because
 * "rx_search_in with NULL" is a THIRD thing from both other routes and is the
 * one the delegation's own control needs.
 */
static int parse_route(const char *s, int *use_in, int *have_buffers,
                       size_t *nframes, size_t *ntrail) {
    const char *comma;
    char *end;
    unsigned long long a, b;

    *use_in = 0; *have_buffers = 0; *nframes = 0; *ntrail = 0;
    if (!s || !*s || strcmp(s, "default") == 0) return 0;
    if (strcmp(s, "null") == 0) { *use_in = 1; return 0; }

    errno = 0;
    a = strtoull(s, &end, 10);
    if (end == s || errno != 0 || (*end != 0 && *end != ',') || a == 0) {
        fprintf(stderr, "driver: invalid route '%s' (want default|null|<n>|<frames>,<trail>)\n", s);
        return -1;
    }
    comma = end;
    if (*comma == 0) { b = a; }
    else {
        const char *t = comma + 1;
        errno = 0;
        b = strtoull(t, &end, 10);
        if (end == t || errno != 0 || *end != 0 || b == 0) {
            fprintf(stderr, "driver: invalid route '%s' (trail capacity)\n", s);
            return -1;
        }
    }
    *use_in = 1; *have_buffers = 1;
    *nframes = (size_t)a; *ntrail = (size_t)b;
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2 || argc > 5) {
        fprintf(stderr, "usage: %s <subject> [startpos] [route] [mode]\n", argc > 0 ? argv[0] : "t");
        return 2;
    }

    size_t startpos = 0;
    if (argc >= 3 && parse_startpos(argv[2], &startpos) != 0) return 2;

    int use_in = 0, have_buffers = 0;
    size_t nframes = 0, ntrail = 0;
    if (argc >= 4 && parse_route(argv[3], &use_in, &have_buffers, &nframes, &ntrail) != 0)
        return 2;

    /* [DD-13b.W23.3] the MODE, a CLOSED set of two — an unknown mode is a
     * usage error rather than a silent fall back to `one`, because falling
     * back would make a mis-spelled `count` answer the wrong question and
     * pass. */
    int mode_count = 0;
    if (argc >= 5) {
        if (strcmp(argv[4], "count") == 0)    mode_count = 1;
        else if (strcmp(argv[4], "one") != 0) {
            fprintf(stderr, "driver: invalid mode '%s' (want one|count)\n", argv[4]);
            return 2;
        }
    }

    /* [DD-13b.W23.3, H15] `@path` names a FILE whose bytes are the subject,
     * byte-exact; anything else is the escaped inline form. */
    size_t len = 0;
    unsigned char *buf = argv[1][0] == '@' ? read_subject_file(argv[1] + 1, &len)
                                           : decode(argv[1], &len);
    if (!buf) return 2;

    /* [DD-13b.W23.3, H7] THE FIND-ALL LOOP, which is the `mc` line's whole
     * question. It is `docs/spec/match_api.md` §3.1's loop TRANSCRIBED —
     * the same transcription `tests/encseam/findall_driver.c` carries, and
     * deliberately so: if the two ever differ, one of them has stopped
     * meaning what the spec says. The advance off an EMPTY match goes
     * through the artifact's own `<prefix>_next_pos` residual and off the
     * MATCH'S OWN START (`caps[0][0]`), never off the loop variable — an
     * empty match can be found at a position later than the one searched
     * from, which is exactly where the bench's `pos = max(end, pos+1)`
     * formula double-counts it (`(?=a)` on `"xax"` is 1, not 2;
     * format_design §2.21's measured table).
     *
     * A non-default route is not offered here and the reason is stated
     * rather than assumed: `mc` asks about the artifact's ANSWER, and the
     * `_in` entries answer the same question through different storage —
     * a find-all count is not the place that distinction is observable,
     * and run.sh keeps an `mc`-bearing block off the routed path. */
    if (mode_count) {
        ptrdiff_t fa[RXMAC(_NCAPS)][2];
        size_t p = startpos, nmatch = 0;
        while (p <= len) {
            int r = RXFN(_search)(buf, len, p, fa);
            if (r != 1) {
                if (r < 0) {
                    const char *w = r == PCREC_ERR_STEPS    ? "steps"
                                  : r == PCREC_ERR_FRAMES   ? "frames"
                                  : r == PCREC_ERR_WORK     ? "work"
                                  : r == PCREC_ERR_RECURSE  ? "recurse"
                                  : r == PCREC_ERR_INTERNAL ? "internal"
                                  : NULL;
                    if (w) printf("%s\n", w);
                    else printf("giveup %d\n", r);
                    free(buf);
                    return 3;
                }
                break;                      /* 0 = done */
            }
            nmatch++;
            p = (fa[0][1] > fa[0][0])
                  ? (size_t)fa[0][1]
                  : RXFN(_next_pos)(buf, len, (size_t)fa[0][0]);
        }
        printf("count %zu\n", nmatch);
        free(buf);
        return 0;
    }

    /* [DD-14.FB] The caller-supplied regions, when the route asks for them.
     * Sized in BYTES from the artifact's own RX_*_FRAME_SIZE macros, which is
     * the arithmetic spec §10.4 publishes them for -- if those macros were
     * stamped from the wrong struct (sabotage row S-FB6) this is the
     * allocation that comes out short, and the artifact's own _Static_assert
     * catches it one step earlier still. On a DFA artifact the sizes are 0
     * and the route degenerates to a NULL descriptor, which that engine
     * ignores anyway. */
    void *frames_mem = NULL, *trail_mem = NULL;
    if (have_buffers) {
        if (RXMAC(_RESUME_FRAME_SIZE) == 0 || RXMAC(_TRAIL_FRAME_SIZE) == 0) {
            have_buffers = 0;   /* an inert (DFA) artifact: nothing to size */
        } else {
            frames_mem = malloc(nframes * (size_t)RXMAC(_RESUME_FRAME_SIZE));
            trail_mem  = malloc(ntrail  * (size_t)RXMAC(_TRAIL_FRAME_SIZE));
            if (!frames_mem || !trail_mem) {
                fprintf(stderr, "driver: out of memory for a %zu-frame / %zu-entry buffer\n",
                        nframes, ntrail);
                free(frames_mem); free(trail_mem); free(buf);
                return 2;
            }
        }
    }

    /* [K21-class fix, 2026-08-15] `rx_search`'s return is THREE-valued (1
     * match, 0 no-match, a negative give-up sentinel — PCREC_ERR_STEPS/
     * PCREC_ERR_FRAMES ([ABI-NS]/D60: unprefixed since [ABI-NS]; the
     * per-prefix RX_ERR_* spellings this comment used to name were deleted,
     * no alias) — when a VM artifact exhausts its step budget or
     * backtrack-frame capacity; a DFA artifact never returns the
     * sentinels). Testing the result with `if (found)` is C-truthy on a
     * negative return too, so the ORIGINAL version of this driver took the
     * match branch on a give-up and printed `caps`, which the give-up path
     * never writes — uninitialized stack reported as a confident match.
     * This is one instance of a recorded SHAPE, not a one-off: the same
     * truthy-check-on-three-valued-return bug has now been found and fixed
     * at three other sites reading this same API —
     * tests/fuzz/fuzz_driver.c (the fuzzfix arc, discriminates found==1/
     * found==0/PCREC_ERR_STEPS/PCREC_ERR_FRAMES explicitly), and
     * src/gen/emit_dfa.c's `pcrec_emit_main` (docs/dev/known_issues.md K21,
     * the CLI's `--emit-main` generated main()). A FOURTH site,
     * tests/registry/pc4_driver.c, has the identical `if (rx_search(...))`
     * shape TODAY and is NOT yet fixed — flagged for the manager rather
     * than silently patched here, since PC-4 is a different subsystem with
     * its own sabotage battery outside this fix's scope. Any new driver
     * against this API should discriminate explicitly, the way this one
     * now does, rather than add a fifth instance of the shape.
     *
     * Exit code 3 mirrors `pcrec_emit_main`'s choice, for the same reason:
     * distinct from a normal run (0) and this driver's own usage/malformed-
     * input exit (2), and it lets run.sh treat a give-up as its own HARD
     * harness-level failure (never compared against a `match`/`nomatch`
     * expectation) the same way it already treats a crash or a timeout. */
    ptrdiff_t caps[RXMAC(_NCAPS)][2];
    RXFN(_buffers) rxb;
    const RXFN(_buffers) *bufp = NULL;
    int found;
    rxb.frames = frames_mem; rxb.nframes = nframes;
    rxb.trail  = trail_mem;  rxb.ntrail  = ntrail;
    if (have_buffers) bufp = &rxb;
    if (!use_in) {
        found = RXFN(_search)(buf, len, startpos, caps);
    } else {
        found = RXFN(_search_in)(buf, len, startpos, caps, bufp);
    }

    /*
     * [DD-14.FB] THE OTHER TWO `_in` ENTRIES, CROSS-CHECKED ON EVERY ROUTED
     * CASE — because without this they had NO behavioural coverage anywhere in
     * the tree. `<prefix>_search_in` is the entry every cell, every driver and
     * every measurement drives; `<prefix>_match_in` and
     * `<prefix>_match_caps_in` were built, declared, structurally checked and
     * never once RUN. Three entries shipped and one was exercised.
     *
     * IT IS A CROSS-CHECK, NOT A SECOND ANSWER, and that distinction is what
     * makes it free of new expectations. The `.rxt` `m`/`n` vocabulary means a
     * SEARCH (leftmost-first from `startpos`); the two anchored entries answer
     * a different question (match AT `ctx->pos`), so routing an `m` line
     * through them would change what the corpus means. Instead each anchored
     * entry is compared against ITS OWN un-suffixed sibling on the same ctx,
     * which is the property §10.2 states — "each `_in` entry is its
     * un-suffixed sibling in every respect, plus one argument naming where the
     * working storage lives" — and needs no oracle of its own.
     *
     * THE ONE PERMITTED DIVERGENCE IS A GIVE-UP ON EITHER SIDE, and getting
     * that wrong is how this check introduced itself: the first version
     * allowed the difference only DOWNWARD (a smaller caller buffer turning a
     * match into `PCREC_ERR_FRAMES`, which the corpus's `frames-buffer=
     * 512,400000` cell exists to produce) and it went RED on a correct build,
     * on the `1024,8192` cell — where the `_in` entry MATCHES a subject its
     * un-suffixed sibling refuses. That direction is the whole feature.
     *
     * So the rule is symmetric in the give-up and strict everywhere else: when
     * a buffer is supplied, the two answers may differ if EITHER is a give-up,
     * because the caller's capacity is simply not the stamped one. If NEITHER
     * is a give-up they must agree exactly — same length, same capture spans —
     * and a give-up code that differs from its sibling's while both gave up is
     * a divergence too. On the `null` route NO divergence at all is permitted:
     * §10.3 defines that call to BE the un-suffixed one, so `have_buffers` is
     * false and the exemption does not apply.
     */
    if (use_in) {
        rx_ctx ctx;
        ptrdiff_t caps_plain[RXMAC(_NCAPS)][2] = {{0}},
                  caps_in[RXMAC(_NCAPS)][2] = {{0}};
        ptrdiff_t m_plain, m_in, c_plain, c_in;
        int k, bad = 0;
        ctx.subject = buf; ctx.len = len; ctx.pos = startpos;
        ctx.ncap = 0; ctx.caps = NULL; ctx.user = NULL;

        m_plain = RXFN(_match)(&ctx);
        m_in    = RXFN(_match_in)(&ctx, bufp);
        c_plain = RXFN(_match_caps)(&ctx, caps_plain);
        c_in    = RXFN(_match_caps_in)(&ctx, caps_in, bufp);

        /* Differing is permitted only when a buffer was supplied AND at
         * least one of the two answers is a give-up (< -1). Either direction:
         * a smaller buffer refuses what the default matches, a larger one
         * matches what the default refuses. */
        if (m_in != m_plain && !(have_buffers && (m_in < -1 || m_plain < -1))) {
            fprintf(stderr, "driver: rx_match_in disagrees with rx_match"
                            " (%td vs %td) at startpos %zu -- neither is a give-up,"
                            " so the caller's capacity cannot explain it\n",
                    m_in, m_plain, startpos);
            bad = 1;
        }
        if (c_in != c_plain && !(have_buffers && (c_in < -1 || c_plain < -1))) {
            fprintf(stderr, "driver: rx_match_caps_in disagrees with rx_match_caps"
                            " (%td vs %td) at startpos %zu -- neither is a give-up,"
                            " so the caller's capacity cannot explain it\n",
                    c_in, c_plain, startpos);
            bad = 1;
        }
        if (c_in == c_plain && c_plain >= 0) {
            for (k = 0; k < RXMAC(_NCAPS); k++) {
                if (caps_in[k][0] != caps_plain[k][0] || caps_in[k][1] != caps_plain[k][1]) {
                    fprintf(stderr, "driver: rx_match_caps_in slot %d disagrees"
                                    " (%td,%td) vs (%td,%td)\n", k,
                            caps_in[k][0], caps_in[k][1],
                            caps_plain[k][0], caps_plain[k][1]);
                    bad = 1;
                }
            }
        }
        if (bad) { free(frames_mem); free(trail_mem); free(buf); return 4; }
    }

    free(frames_mem); free(trail_mem);
    if (found == 1) {
        printf("match");
        for (int k = 0; k < RXMAC(_NCAPS); k++) {
            printf(" %td %td", caps[k][0], caps[k][1]);
        }
        printf("\n");
    } else if (found == 0) {
        printf("nomatch\n");
    } else {
        /* [DD-14 wave A, 2026-08-24] EVERY typed give-up code gets its own
         * word — the pre-fix line named exactly two of the (now four)
         * codes and folded every other one into "frames", which is
         * mislabelled evidence: a WORK give-up printed as a frame-capacity
         * failure would send a reader chasing the wrong bound, precisely
         * DD-2's "different failures, different diagnoses" complaint,
         * reached from inside this driver rather than from generated
         * --emit-main code (src/gen/emit_dfa.c's `pcrec_emit_main` fixed
         * the identical shape at [ENG-BREP counter-K]). A code this
         * fallthrough cannot name still prints its numeric value rather
         * than guessing.
         *
         * [DD-14 wave A commit 2] "internal" (PCREC_ERR_INTERNAL, BELOW
         * the give-up floor) is named too, even though it is NOT a
         * give-up — it is the artifact's own analysis/emission
         * inconsistency check firing (module 'lookaround''s
         * negative-polarity lookbehind end-check is the one producer
         * today). It still exits 3 like every other negative return this
         * driver cannot turn into a match/nomatch line, but run.sh's `gu`
         * directive (docs/testing.md) refuses to let any corpus block
         * EXPECT it: nothing may plan for the artifact catching its own
         * bug, that is what sabotage rows are for. */
        const char *word = found == PCREC_ERR_STEPS    ? "steps"
                          : found == PCREC_ERR_FRAMES   ? "frames"
                          : found == PCREC_ERR_WORK     ? "work"
                          : found == PCREC_ERR_RECURSE  ? "recurse"
                          : found == PCREC_ERR_INTERNAL ? "internal"
                          : NULL;
        if (word) printf("%s\n", word);
        else printf("giveup %d\n", found);
        free(buf);
        return 3;
    }

    free(buf);
    return 0;
}
