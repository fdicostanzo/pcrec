/* tests/mrl/cwmax_check.c — [M6.6.2 wave A; re-aimed at [M5.0] stage 2] the
 * CHARACTER width pair `pcrec_cwmin`/`pcrec_cwmax` against the corpus.
 *
 * BORN `maxw_check.c`, sweeping the BYTE pair; when stage 2 re-aimed the cwmax
 * chain into characters (utf8_design.md §5.6.2 — `pcrec_cwmax` retired, its
 * fixpoint became `cwmax`) this instrument moved with its subject, unchanged
 * in spirit.
 *
 * **THAT RE-AIM RESTED ON A PREMISE THAT EXPIRED, AND THIS IS THE REPAIR
 * (2026-09-05, lane k49fix).** The sentence here used to read: *"under the
 * `byte` encoding this file parses with, one character is one byte, so every
 * number below is what the byte sweep measured."* True when it was written and
 * FALSE the moment `tests/utf8/` merged. That corpus's blocks carry
 * `encoding utf8`, their oracle spans are BYTE offsets into subjects holding
 * MULTI-BYTE characters, and CHECK 2 was comparing those bytes against a
 * CHARACTER quantity — so `[^a]` matching one 2-byte character read as "span 2
 * EXCEEDS cwmax=1" on 21 cells. **The unit mismatch was in THIS FILE, not in
 * the analysis**: verified cell by cell before the repair, every one of those
 * 21 spans is exactly ONE character (or one character against a `{1,2}`'s
 * cwmax of 2), so cwmax was right in characters throughout and no
 * under-estimate exists in this population. An under-estimate would have been
 * an ENGINE bug in the silent direction (the lookaround fixed-width rule reads
 * this number) and is what the repair had to rule out before touching the
 * check.
 *
 * THE RULE NOW, and both halves are needed or the comparison still mixes
 * units:
 *
 *   - **A block is parsed under ITS OWN encoding.** `pcrec_options.encoding`
 *     comes from the block's `encoding` directive, so cwmax is computed on the
 *     AST the block MEANS. Under `byte` a literal `[EUR]` is a class of three
 *     BYTES; under `utf8` it is one CHARACTER. The two are different languages
 *     and only one of them is the block's.
 *   - **The oracle span is measured in the same unit.** Under `utf8` the span
 *     is counted in CHARACTERS — non-continuation bytes in
 *     `subject[start..end)` — and under `byte` it stays the byte count it
 *     always was, unchanged to the line.
 *
 * THE CHARACTER COUNT SHARES NO SOURCE WITH WHAT IT CHECKS (learnings §3).
 * It is a one-line predicate over the subject's own bytes — `(b & 0xC0) !=
 * 0x80` — and never asks pcrec, `next_pos`, the lowering or any decoder. That
 * is deliberate: this file exists to check an ANALYSIS from outside, and a
 * span counted by the compiler's own notion of a character boundary would make
 * CHECK 2 a comparison of pcrec against itself.
 *
 * `pcrec_cwmax` is an ANALYSIS, so its errors are silent by construction: it
 * has no output of its own, and until the lookaround module's fixed-width rule
 * consumes it (`lookaround_design.md` §2.5) nothing in the artifact changes
 * when it is wrong. That is `src/opt/mrl.c`'s own stated reason for existing
 * as a separate file with its own corpus, one function later.
 *
 * TWO CHECKS, AND THEY CONSTRAIN cwmax FROM OPPOSITE SIDES. This matters more
 * than the count of patterns: a check that only bounds cwmax from BELOW is
 * passed by `return PCREC_W_UNBOUNDED;` — the exact degenerate implementation
 * that would make the fixed-width rule reject everything — and a check that
 * only bounds it from ABOVE is passed by `return 0;`, the degenerate one that
 * makes the rule accept everything. Neither degenerate survives both.
 *
 *   CHECK 1 (the lower side, from pcrec) — `cwmax(n) >= cwmin(n)` at EVERY NODE
 *   of every pattern in the corpus, not just at the root. Per-node because the
 *   two functions recurse differently (cwmin takes a `min` at A_ALT, cwmax a
 *   `max`; cwmin multiplies by `rmin`, cwmax by `rmax`), so a subtree can
 *   violate the invariant while the root's numbers still look ordered.
 *
 *   CHECK 2 (the upper side, from the ORACLE) — for every `m`/`ms` expectation
 *   in the corpus, `end - start <= cwmax(root)`. The spans in the `.rxt` files
 *   are oracle-verified against python `re` (docs/testing.md), so this is the
 *   one side of cwmax that is checked against something that is NOT pcrec: a
 *   cwmax below the truth is a span the corpus already knows about. That is
 *   also the direction that miscompiles — an under-estimate makes a
 *   variable-width lookbehind branch look fixed.
 *
 * WHY CHECK 2 DOES NOT ALSO ASSERT `end - start >= cwmin(root)`: `\K` makes it
 * false. The reported span STARTS at the `\K`, so it is a SUBSET of what the
 * match consumed and can be shorter than the minimum width — `a\Kb` on "ab"
 * reports (1,2) with cwmin 2. The `<=` direction survives `\K` untouched for
 * the same reason (a subset is no wider), which is why one half is asserted
 * unconditionally and the other is not asserted at all.
 *
 * THE CORPUS IS READ, NOT TRANSCRIBED. The `.rxt` files are given on the
 * command line (run_mrl_tests.sh passes every one in tests/), and this file
 * re-implements only the three directives it needs — `pattern`, `features`,
 * `m`/`ms` — following tests/harness/run.sh's grammar. It DOES NOT COMPILE
 * anything: it parses to an AST and calls the two analyses directly, which is
 * the only way to see a per-node number at all.
 *
 * SKIPPING IS COUNTED AND PRINTED, NEVER SILENT (pcre2_check.c's rule). A
 * pattern the parser refuses under its block's own feature set is a legitimate
 * skip — `perr` blocks are most of them — but a corpus that quietly shrank to
 * nothing would otherwise pass. The totals are printed and the pattern count
 * is asserted against a floor.
 *
 * PROVE THE CHECK IS LIVE. PCREC_CWMAX_SABOTAGE corrupts what the check reads
 * — `zero` clamps cwmax to 0 (the "accept everything" degenerate), `unbounded`
 * pins it to PCREC_W_UNBOUNDED (the "reject everything" one), `swap` returns
 * cwmin. Each must make this binary FAIL, and run_mrl_tests.sh requires it.
 * `unbounded` must be caught by CHECK 1's own strictness rather than by the
 * inequality, so CHECK 1 additionally requires that cwmax is not unbounded
 * everywhere: the corpus contains bounded patterns and it must say so.
 *
 * PROVE THE DECODE IS LIVE TOO, and in BOTH directions — a character count
 * that is never exercised is dead code that makes the mismatch above
 * un-reproducible, and it would pass silently. Two floors, both asserted:
 *
 *   (i)  the `utf8` block population must be NONZERO. A corpus that lost
 *        tests/utf8/, or a reader that stopped seeing `encoding` lines, would
 *        otherwise leave this whole path unentered and green.
 *   (ii) at least one COMPARED span's byte length must EXCEED its character
 *        count. (i) alone is satisfied by a `utf8` corpus of ASCII-only
 *        subjects, where the two counts coincide and the decode proves
 *        nothing. This is the floor that fails if someone "simplifies" the
 *        character count back into a byte count.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>

#include "core/internal.h"
#include "gen/enc/enc.h"   /* pcrec_enc_by_name — the encoding namespace's one table */

/* ---- the sabotage channel (see the header) --------------------------------- */

enum { SAB_NONE = 0, SAB_ZERO, SAB_UNBOUNDED, SAB_SWAP };
static int sabotage;

static long long cwmax_of(const Ast *a)
{
    switch (sabotage) {
    case SAB_ZERO:      return 0;
    case SAB_UNBOUNDED: return PCREC_W_UNBOUNDED;
    case SAB_SWAP:      return pcrec_cwmin(a);
    default:            return pcrec_cwmax(a);
    }
}

/* ---- counters -------------------------------------------------------------- */

static long n_files, n_blocks, n_parsed, n_skipped, n_nodes, n_spans;
static long n_bounded_nodes;      /* nodes whose cwmax is NOT unbounded */
static long n_viol_order, n_viol_span;
static long n_neg;
/* [2026-09-05] the encoding-aware half's own population, so it cannot be dead
 * code that passes silently — see the header's two floors. */
static long n_utf8_blocks, n_utf8_spans, n_multibyte_spans, n_undecodable;

static void viol_order(const char *file, int line, const char *pat,
                       long long mn, long long mx, int kind)
{
    if (n_viol_order < 20)
        fprintf(stderr, "FAIL %s:%d: cwmax < cwmin at a node (kind %d): "
                "cwmin=%lld cwmax=%lld  pattern '%s'\n",
                file, line, kind, mn, mx, pat);
    n_viol_order++;
}

/* ---- the per-node sweep ----------------------------------------------------
 *
 * An EXPLICIT WORKLIST rather than recursion, for src/ir/nfa.c's R-2 reason:
 * a left-leaning A_CAT spine and an A_CAP chain are as long as the PATTERN,
 * not as deep as its nesting, and a driver that blows its stack on a long
 * literal would be reporting the wrong thing. */
typedef struct { const Ast **v; size_t n, cap; } Stack;

static void push(Stack *s, const Ast *a)
{
    if (!a) return;
    if (s->n == s->cap) {
        s->cap = s->cap ? s->cap * 2 : 64;
        s->v = realloc(s->v, s->cap * sizeof *s->v);
        if (!s->v) { fprintf(stderr, "FAIL: out of memory\n"); exit(2); }
    }
    s->v[s->n++] = a;
}

static void sweep(const Ast *root, const char *file, int line, const char *pat)
{
    Stack s = { NULL, 0, 0 };
    push(&s, root);
    while (s.n) {
        const Ast *a = s.v[--s.n];
        long long mn = pcrec_cwmin(a), mx = cwmax_of(a);
        n_nodes++;
        if (mn < 0 || mx < 0) {
            if (n_neg < 20)
                fprintf(stderr, "FAIL %s:%d: negative width (cwmin=%lld cwmax=%lld) "
                        "pattern '%s'\n", file, line, mn, mx, pat);
            n_neg++;
        }
        if (mx < mn) viol_order(file, line, pat, mn, mx, (int)a->k);
        if (mx < PCREC_W_UNBOUNDED) n_bounded_nodes++;
        push(&s, a->l);
        push(&s, a->r);
    }
    free(s.v);
}

/* ---- parsing one pattern ---------------------------------------------------
 *
 * branch_count_check.c's recipe: a hand-built Ctx, `pcrec_parse_mods_init`
 * because ParseMods is incomplete outside src/parse/, and `setjmp` for the
 * refusal path. The arena is freed either way. Returns NULL when pcrec
 * refuses the pattern under the feature set currently installed. */
static Ast *parse_one(const char *pat, bool caseless, int encoding,
                      Ctx *cx, pcrec_options *defo)
{
    memset(cx, 0, sizeof(*cx));
    pcrec_default_options(defo);
    if (caseless) defo->flags |= PCREC_CASELESS;
    /* [2026-09-05] The block's OWN encoding, so cwmax is computed on the AST
     * the block means. The parser's literal reader is per-encoding
     * (`pcrec_pat_char`, src/opt/lower_enc.c), so this is what makes a literal
     * multi-byte character in the pattern text ONE class rather than a
     * concatenation of byte classes. The lowering is deliberately NOT run —
     * this file never compiles — which is exactly what keeps the AST at the
     * CHARACTER tier the cwmax pair is defined on. */
    defo->encoding = encoding;
    cx->pat = pat;
    cx->patlen = strlen(pat);
    cx->opt = defo;
    cx->job = calloc(1, sizeof(Job));
    if (!cx->job) { fprintf(stderr, "FAIL: out of memory\n"); exit(2); }
    cx->arena.cx = cx;

    Ast *root = NULL;
    if (setjmp(cx->jb) == 0) {
        pcrec_parse_mods_init(cx);
        root = pcrec_parse_info(cx, NULL);
    }
    return root;   /* caller frees the arena and the job */
}

static void release(Ctx *cx)
{
    arena_free(&cx->arena);
    free(cx->job);
}

/* ---- the .rxt reader ------------------------------------------------------- */

/* A truncating copy. `snprintf("%s")` says the same thing but makes gcc warn
 * about a truncation this file WANTS (an over-long directive is a corpus bug,
 * not a reason to overrun a buffer). */
static void copy_bounded(char *dst, size_t cap, const char *src)
{
    size_t n = strlen(src);
    if (n >= cap) n = cap - 1;
    memcpy(dst, src, n);
    dst[n] = 0;
}

static void trim_nl(char *s)
{
    size_t n = strlen(s);
    while (n && (s[n - 1] == '\n' || s[n - 1] == '\r')) s[--n] = 0;
}

/* The subject's escape grammar, transcribed from tests/harness/verify_rxt.py's
 * `decode_subject` (the harness's own reader): `\"` `\\` `\n` `\t` `\r` `\f`
 * `\v` `\xHH`, anything else literal. Decoding into `dst` (a byte buffer, NOT
 * a string — a subject may legally contain NUL) and returning its length, or
 * -1 on a malformed escape.
 *
 * THIS FILE DID NOT USED TO DECODE AT ALL, and the comment that stood here
 * said why: *"the offsets in an .rxt file are already DECODED byte offsets."*
 * Still true, and no longer sufficient — a CHARACTER count needs the bytes
 * those offsets point at, not just the offsets. */
static long decode_subject(const char *s, size_t len, unsigned char *dst, size_t cap)
{
    size_t i = 0, n = 0;
    while (i < len) {
        if (n >= cap) return -1;
        if (s[i] != '\\') { dst[n++] = (unsigned char)s[i++]; continue; }
        if (i + 1 >= len) return -1;
        switch (s[i + 1]) {
        case '"':  dst[n++] = '"';  i += 2; break;
        case '\\': dst[n++] = '\\'; i += 2; break;
        case 'n':  dst[n++] = '\n'; i += 2; break;
        case 't':  dst[n++] = '\t'; i += 2; break;
        case 'r':  dst[n++] = '\r'; i += 2; break;
        case 'f':  dst[n++] = '\f'; i += 2; break;
        case 'v':  dst[n++] = '\v'; i += 2; break;
        case 'x': {
            if (i + 3 >= len) return -1;
            char h[3] = { s[i + 2], s[i + 3], 0 };
            char *e;
            long v = strtol(h, &e, 16);
            if (*e || v < 0 || v > 0xFF) return -1;
            dst[n++] = (unsigned char)v; i += 4;
            break;
        }
        default: return -1;
        }
    }
    return (long)n;
}

/* The CHARACTER count of `b[start..end)`, and it is one predicate: a UTF-8
 * character boundary is any position whose byte is not a continuation byte
 * (`(b & 0xC0) == 0x80`), so the count is the number of NON-continuation bytes
 * in the range. Shares no source with pcrec — see the header. An ill-formed
 * run degrades to "one character per non-continuation byte", which is the same
 * self-synchronizing reading `next_pos` uses and never over-counts a
 * well-formed one. */
static long char_width(const unsigned char *b, long n, long start, long end)
{
    if (start < 0) start = 0;
    if (end > n) end = n;
    long w = 0;
    for (long i = start; i < end; i++)
        if ((b[i] & 0xC0) != 0x80) w++;
    return w;
}

/* `m "subject" START END` / `ms "subject" START END STARTPOS`. Returns the two
 * offsets AND both widths of the span — bytes as before, plus characters — so
 * `block_run` can pick the unit its block's encoding calls for. The block's
 * `encoding` line may legally follow the `m` lines, so BOTH are always
 * computed and the choice is made once the block is complete. */
static bool span_of(const char *line, long *wbytes, long *wchars)
{
    const char *p = line;
    if (strncmp(p, "ms ", 3) == 0) p += 3;
    else if (strncmp(p, "m ", 2) == 0) p += 2;
    else return false;
    while (*p == ' ' || *p == '\t') p++;
    if (*p != '"') return false;
    /* the LAST quote on the line closes the subject: subjects may contain an
     * escaped quote, and the trailing fields are all numeric. */
    const char *q = strrchr(p, '"');
    if (!q || q == p) return false;
    const char *body = p + 1;              /* first byte inside the quotes */
    size_t bodylen = (size_t)(q - body);
    q++;
    char *endp;
    long a = strtol(q, &endp, 10);
    if (endp == q) return false;
    const char *r = endp;
    long b = strtol(r, &endp, 10);
    if (endp == r) return false;

    *wbytes = b - a;
    static unsigned char subj[65536];
    long slen = decode_subject(body, bodylen, subj, sizeof subj);
    /* A subject this file cannot decode falls back to the byte width, which is
     * the PRE-repair behaviour and is never smaller than the character width —
     * so the fallback can only make CHECK 2 stricter, never let a violation
     * through. Counted and printed rather than silent. */
    if (slen < 0) { *wchars = -1; return true; }
    *wchars = char_width(subj, slen, a, b);
    return true;
}

/* ONE BLOCK, BUFFERED. The parse happens at the END of the block rather than
 * at the `pattern` line, because run.sh's grammar puts `features` and `flags`
 * AFTER it and both change what the pattern parses to. Buffering also means a
 * block with no `m` line at all — a `perr` block, or one that is all `n`
 * expectations — still gets its tree swept, which is most of the corpus's
 * zero-width and refusal shapes. */
typedef struct {
    char  pat[65536];
    char  feats[512];
    bool  caseless;
    int   encoding;              /* PCREC_ENC_*, from the block's own directive */
    int   patline;
    long *sp_bytes, *sp_chars;   /* both widths; the encoding picks one */
    int  *sp_line;
    size_t nsp, capsp;
} Block;

static void block_span(Block *b, long wbytes, long wchars, int line)
{
    if (b->nsp == b->capsp) {
        b->capsp = b->capsp ? b->capsp * 2 : 16;
        b->sp_bytes = realloc(b->sp_bytes, b->capsp * sizeof *b->sp_bytes);
        b->sp_chars = realloc(b->sp_chars, b->capsp * sizeof *b->sp_chars);
        b->sp_line  = realloc(b->sp_line,  b->capsp * sizeof *b->sp_line);
        if (!b->sp_bytes || !b->sp_chars || !b->sp_line) {
            fprintf(stderr, "FAIL: out of memory\n"); exit(2);
        }
    }
    b->sp_bytes[b->nsp] = wbytes;
    b->sp_chars[b->nsp] = wchars;   /* -1 when the subject would not decode */
    b->sp_line[b->nsp]  = line;
    b->nsp++;
}

static void block_run(Block *b, const char *path, const char *default_features)
{
    char err[256];
    const char *spec = b->feats[0] ? b->feats : default_features;
    if (pcrec_enabled_set_spec(spec, err, sizeof err) != 0) {
        fprintf(stderr, "FAIL %s:%d: bad features spec '%s': %s\n",
                path, b->patline, spec, err);
        n_viol_order++;
        return;
    }

    Ctx cx; pcrec_options defo;
    Ast *root = parse_one(b->pat, b->caseless, b->encoding, &cx, &defo);
    if (!root) { n_skipped++; release(&cx); return; }
    n_parsed++;

    sweep(root, path, b->patline, b->pat);

    const bool chars = (b->encoding != PCREC_ENC_BYTE);
    if (chars) n_utf8_blocks++;

    long long mx = cwmax_of(root);
    for (size_t i = 0; i < b->nsp; i++) {
        long wb = b->sp_bytes[i], wc = b->sp_chars[i];
        long w;
        const char *unit;
        if (chars && wc >= 0) { w = wc; unit = "characters"; n_utf8_spans++; if (wb > wc) n_multibyte_spans++; }
        else if (chars)       { w = wb; unit = "bytes (UNDECODABLE subject)"; n_undecodable++; }
        else                  { w = wb; unit = "bytes"; }
        n_spans++;
        if (w > mx) {
            if (n_viol_span < 20)
                fprintf(stderr, "FAIL %s:%d: ORACLE span %ld %s EXCEEDS cwmax=%lld "
                        "for pattern '%s'\n", path, b->sp_line[i], w, unit, mx, b->pat);
            n_viol_span++;
        }
    }
    release(&cx);
}

static void block_reset(Block *b)
{
    b->nsp = 0; b->feats[0] = 0; b->caseless = false;
    b->encoding = PCREC_ENC_BYTE;   /* run.sh's own default for a block with no directive */
}

static void do_file(const char *path, const char *default_features)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "FAIL: cannot open %s\n", path); n_viol_order++; return; }
    n_files++;

    static char line[65536];
    Block b;
    memset(&b, 0, sizeof b);
    b.encoding = PCREC_ENC_BYTE;
    bool have = false;
    int lineno = 0;

    while (fgets(line, sizeof line, f)) {
        lineno++;
        trim_nl(line);
        if (line[0] == '#' || line[0] == 0) continue;

        if (strncmp(line, "pattern ", 8) == 0) {
            if (have) block_run(&b, path, default_features);
            block_reset(&b);
            copy_bounded(b.pat, sizeof b.pat, line + 8);
            b.patline = lineno;
            n_blocks++;
            have = true;
            continue;
        }
        if (!have) continue;

        if (strncmp(line, "features ", 9) == 0) {
            copy_bounded(b.feats, sizeof b.feats, line + 9);
            continue;
        }
        if (strncmp(line, "flags ", 6) == 0) {
            if (strchr(line + 6, 'i')) b.caseless = true;
            continue;
        }
        if (strncmp(line, "encoding ", 9) == 0) {
            /* Resolved through the SEAM's own registry rather than by
             * comparing the string here, so this file cannot drift from
             * `src/gen/enc/enc.c`'s spelling of an encoding's name — the
             * single-namespace rule ([SR-10]) that table owns. An unknown
             * name is a corpus bug and is reported, not defaulted. */
            const PcrecEnc *e = pcrec_enc_by_name(line + 9);
            if (!e) {
                fprintf(stderr, "FAIL %s:%d: unknown encoding '%s'\n",
                        path, lineno, line + 9);
                n_viol_order++;
            } else {
                b.encoding = e->id;
            }
            continue;
        }

        long wb, wc;
        if (span_of(line, &wb, &wc)) block_span(&b, wb, wc, lineno);
    }
    if (have) block_run(&b, path, default_features);

    free(b.sp_bytes); free(b.sp_chars); free(b.sp_line);
    fclose(f);
}

/* ---- main ------------------------------------------------------------------ */

int main(int argc, char **argv)
{
    const char *sab = getenv("PCREC_CWMAX_SABOTAGE");
    if (sab && *sab) {
        if      (!strcmp(sab, "zero"))      sabotage = SAB_ZERO;
        else if (!strcmp(sab, "unbounded")) sabotage = SAB_UNBOUNDED;
        else if (!strcmp(sab, "swap"))      sabotage = SAB_SWAP;
        else { fprintf(stderr, "unknown PCREC_CWMAX_SABOTAGE '%s'\n", sab); return 2; }
        printf("  (SABOTAGE '%s' installed — this run MUST fail)\n", sab);
    }

    if (argc < 2) {
        fprintf(stderr, "usage: %s FILE.rxt...\n", argv[0]);
        return 2;
    }

    printf("=== [M6.6.2 wave A / M5.0 s2] pcrec_cwmax over the .rxt corpus ===\n");

    /* the fallback for a block with no `features` line: exactly what the CLI
     * installs when no --features flag is given (D37's mapping point). */
    const char *deflt = PCREC_DEFAULT_FEATURES;

    for (int i = 1; i < argc; i++) do_file(argv[i], deflt);

    printf("  files                     : %ld\n", n_files);
    printf("  pattern blocks seen       : %ld\n", n_blocks);
    printf("  patterns parsed           : %ld\n", n_parsed);
    printf("  patterns skipped (refused): %ld\n", n_skipped);
    printf("  AST nodes swept           : %ld\n", n_nodes);
    printf("    of which cwmax is BOUNDED: %ld\n", n_bounded_nodes);
    printf("  oracle spans checked      : %ld\n", n_spans);
    printf("    utf8 blocks / spans      : %ld / %ld\n", n_utf8_blocks, n_utf8_spans);
    printf("    of those, spans whose BYTE width exceeds their CHARACTER width: %ld\n",
           n_multibyte_spans);
    printf("    undecodable subjects (fell back to bytes): %ld\n", n_undecodable);
    printf("  CHECK 1 violations (cwmax < cwmin)      : %ld\n", n_viol_order);
    printf("  CHECK 2 violations (span > cwmax)      : %ld\n", n_viol_span);
    printf("  negative widths                       : %ld\n", n_neg);

    int bad = 0;
    if (n_viol_order || n_viol_span || n_neg) bad = 1;

    /* the corpus must not have quietly shrunk. The floors are well below the
     * measured numbers on purpose — they catch a reader that broke, not a
     * corpus that grew or shrank by a file. */
    if (n_parsed < 500) {
        fprintf(stderr, "FAIL: only %ld patterns parsed — the corpus reader is broken\n",
                n_parsed);
        bad = 1;
    }
    if (n_nodes < 2000) {
        fprintf(stderr, "FAIL: only %ld nodes swept — the sweep is not walking\n", n_nodes);
        bad = 1;
    }
    if (n_spans < 2000) {
        fprintf(stderr, "FAIL: only %ld oracle spans checked — CHECK 2 is not running\n",
                n_spans);
        bad = 1;
    }
    /* and cwmax must actually be BOUNDED somewhere: `return PCREC_W_UNBOUNDED;`
     * satisfies both inequalities and is useless. */
    if (n_bounded_nodes * 2 < n_nodes) {
        fprintf(stderr, "FAIL: only %ld of %ld nodes have a BOUNDED cwmax — cwmax is "
                "degenerate (everything unbounded passes both inequalities)\n",
                n_bounded_nodes, n_nodes);
        bad = 1;
    }
    /* [2026-09-05] THE ENCODING-AWARE HALF'S OWN TWO FLOORS (see the header).
     * (i) the population exists at all. */
    if (n_utf8_blocks == 0) {
        fprintf(stderr, "FAIL: ZERO utf8 blocks seen — the `encoding` directive reader "
                "is not working, or the utf8 corpus is gone; either way CHECK 2's "
                "character path is dead code and this run certifies nothing about it\n");
        bad = 1;
    }
    /* (ii) and the two units actually DIFFER somewhere, or the character count
     * is indistinguishable from the byte count it replaced. */
    if (n_multibyte_spans == 0) {
        fprintf(stderr, "FAIL: NO compared span has a byte width exceeding its character "
                "width — every utf8 span checked was ASCII, so the character count is "
                "untested and CHECK 2 would read identically with the pre-repair byte "
                "comparison\n");
        bad = 1;
    }
    /* An undecodable subject is a corpus bug rather than a check bug, and the
     * fallback is sound (bytes >= characters, so CHECK 2 only gets stricter) —
     * but it must never be SILENT. */
    if (n_undecodable) {
        fprintf(stderr, "FAIL: %ld utf8 span(s) had a subject this reader could not "
                "decode and fell back to the byte width — the escape grammar here has "
                "drifted from tests/harness/verify_rxt.py's\n", n_undecodable);
        bad = 1;
    }

    printf("%s\n", bad ? "=== cwmax check FAILED ===" : "=== cwmax check PASSED ===");
    return bad;
}
