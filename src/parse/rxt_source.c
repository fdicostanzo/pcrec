/* src/parse/rxt_source.c — [DD-13b.W1.1] the `.rxt` SOURCE parser.
 *
 * THE ONE HEAD PARSER. Design: docs/design/dd13_format/w1_impl.md §1.1's
 * seam ruling and §1.8's output contract; the grammar is
 * docs/design/dd13_format/format_design.md §1.2/§1.3, W1 row of §1.4.
 * Contract: docs/spec/rxt_format.md.
 *
 * WHY THIS FILE EXISTS AT ALL. `--source` must resolve `lib`/`name`/
 * `target`/`config` before it can compile anything, so pcrec needs a
 * reader for the file's HEAD. The tree already has two `.rxt` parsers,
 * both the harness's (tests/harness/run.sh's bash arm chain and
 * tests/harness/verify_rxt.py's `parse_rxt`), and both parse the BODY.
 * The manager's seam ruling keeps it that way: this file owns the HEAD
 * and the whole-file resolution and is the ONLY implementation of it;
 * run.sh gains no head arms and is TOLD the body boundary through
 * `--list-source`'s `line` column. The BODY therefore has three readers
 * on purpose — that duplication is the control C1 compares — and the
 * HEAD has exactly one, which is why §3.1 says plainly that the head has
 * no differential control and names what covers it instead.
 *
 * WHAT W1.1 BUILDS HERE, and what it does not. The head grammar, the
 * body's DIRECTIVE lines, the four W1 head declarations, the three
 * lexical contexts W1 has (head, config body, pattern block), block
 * scalars, `config`'s cascade and its `from` cycle check, and `target`
 * PARSING. It does NOT build: the composer, `target`'s BUILD path,
 * `--emit-composed`, or any `rx_info` change (w1_impl §7.3). A `lib`
 * path is recorded, never opened — [LIB]'s store scan is [LIB]'s.
 *
 * ONE ROW TYPE, NOT FOUR. The note's F2 names `RxtDef`/`RxtTarget`/
 * `RxtConfig` beside `RxtSource`. Every one of them is (kind, name,
 * value, settings, a list) and W1.1 has no consumer that tells them
 * apart — the dump prints them in FILE ORDER, which four arrays cannot
 * express without a fifth structure to interleave them. So there is one
 * `RxtRow` with a kind discriminator, in file order, and typed lookup is
 * a filter over it. That is the general mechanism the house rule asks
 * for rather than four parallel ones (memory
 * `pcrec-general-mechanisms-not-special-cases`); the moment W1.2's
 * target BUILD or W1.3's composer needs a definition-shaped record with
 * fields a row has no place for, it gets one, and D77 says that is when.
 *
 * NO Ctx, SO NO ctx_fail. This parser runs BEFORE any compile (the CLI
 * calls it with no pattern in hand), so there is no `Ctx` to longjmp out
 * of and no arena owner to clean up. Errors are returned, not thrown,
 * and every one of them names the FILE, the LINE and the CONSTRUCT
 * (w1_impl §1.3). The arena is this object's own and dies with it.
 */

#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "pcrec.h"
#include "core/internal.h"

/* ---------------------------------------------------------------- lexer */

/* A line's first whitespace-delimited token IS its kind (format_design
 * §1.2). `frames-buffer=` is the one kind whose spelling runs into its
 * value with no space, so the token ends at '=' as well as at space —
 * exactly how run.sh's own `^frames-buffer=(.*)$` arm reads it. */
static size_t tok_len(const char *s)
{
    size_t i = 0;
    while (s[i] && !isspace((unsigned char)s[i]) && s[i] != '=') i++;
    /* keep the '=' as part of the token for the one kind that has it, so
     * "frames-buffer" and "frames-buffer=" are not two spellings of one
     * thing in the vocabulary tables below. */
    if (s[i] == '=') i++;
    return i;
}

static int tok_is(const char *s, const char *want)
{
    size_t n = tok_len(s);
    return strlen(want) == n && !strncmp(s, want, n);
}

static const char *skip_ws(const char *s)
{
    while (*s == ' ' || *s == '\t') s++;
    return s;
}

/* the value of a `<kind> <value>` line: everything after the kind token
 * and the whitespace behind it. REST-OF-LINE, so trailing bytes are KEPT
 * — `pattern` and `description` are both rest-of-line productions
 * (format_design §1.3), and a pattern's trailing space is data. */
static const char *line_value(const char *line)
{
    return skip_ws(line + tok_len(line));
}

/* THE SAME VALUE, TRAILING WHITESPACE REMOVED, for the kinds whose value
 * is a TOKEN or a LIST rather than rest-of-line.
 *
 * This exists because the other parser accepts what this one would
 * otherwise refuse. run.sh's directive arms all end `[[:space:]]*$`, so
 * `flags i` and `flags i ` are one value there; without this they would
 * be two here, and the two `.rxt` parsers would disagree about a line
 * neither design document distinguishes. MEASURED: 0 corpus directive
 * lines carry trailing whitespace, so the disagreement is unreachable
 * today — which is exactly why it is worth fixing now rather than
 * leaving the parsers to agree by luck of the corpus (three corpus files
 * DO carry trailing whitespace on other lines, where it is data).
 *
 * Returns an arena copy; the value is not a suffix of the line once
 * anything has been trimmed off its end. */
static const char *value_trimmed(RxtP *p, const char *line);

static int line_indented(const char *s)
{
    return *s == ' ' || *s == '\t';
}

static int line_blank_or_comment(const char *s)
{
    const char *p = s;
    while (*p == ' ' || *p == '\t') p++;
    return *p == '\0' || *s == '#';
}

/* ------------------------------------------------------- the vocabularies
 *
 * THREE CONTEXTS, EACH A CLOSED VOCABULARY (format_design §1.2). A first
 * token unknown IN ITS CONTEXT is a hard error that NAMES the context —
 * "nothing is a keyword everywhere". A token that is real but belongs to
 * a later wave is refused as NOT IN THIS BUILD, never as unknown
 * (w1_impl DECIDED (1)): sending a reader hunting a typo in a word that
 * is in the spec is K14's shape.
 *
 * These tables are also the 32-keyword census's subject (§3.1's F12):
 * the census asserts that no corpus line's first token is any of these
 * NEW words, which is what makes appending arms to run.sh safe. */
typedef struct { const char *kw; int wave; } RxtKeyword;

/* head — file-level declarations (format_design §1.3's decl-line, plus
 * the two head block kinds `config` and `freq`). */
static const RxtKeyword head_vocab[] = {
    { "lib",         1 }, { "target",  1 }, { "description", 1 },
    { "config",      1 },
    { "include",     2 }, { "tag",     2 }, { "freq",        2 },
    { "use",         3 }, { "oracle",  3 },
};

/* config body — the indented lines under a `config <name>` line. */
static const RxtKeyword config_vocab[] = {
    { "pcrec",    1 }, { "flags",  1 }, { "features", 1 },
    { "encoding", 1 }, { "engine", 1 }, { "budget",   1 },
    { "analysis", 2 },
    { "testee",   3 }, { "option", 3 },
};

/* pattern block — today's thirteen line kinds plus W1's three. The
 * expectation kinds are listed because this parser must RECOGNISE them
 * to refuse an unknown neighbour; it reads none of their values (a
 * `.rxt` expectation is the harness's business, never the compiler's). */
static const RxtKeyword block_vocab[] = {
    { "pattern",        1 },
    { "flags",          1 }, { "features", 1 }, { "engine",  1 },
    { "budget",         1 }, { "frames-buffer=", 1 },
    { "perr",           1 }, { "m",        1 }, { "n",       1 },
    { "ms",             1 }, { "ns",       1 }, { "g",       1 },
    { "gp",             1 }, { "gu",       1 },
    { "name",           1 }, { "description", 1 }, { "encoding", 1 },
    { "tag",            2 }, { "mc",       2 },
    { "oracle",         3 }, { "variant",  3 },
};

static const RxtKeyword *vocab_find(const RxtKeyword *v, size_t n,
                                    const char *line)
{
    for (size_t i = 0; i < n; i++)
        if (tok_is(line, v[i].kw)) return &v[i];
    return NULL;
}

/* ------------------------------------------------------------ the parser */

typedef struct {
    const char *path;
    Arena *arena;
    pcrec_error *err;
    int failed;
} RxtP;

/* Every diagnostic from this file goes through here, so every one of them
 * carries the FILE and the LINE. `pcrec_error.pos` is a PATTERN offset
 * everywhere else in the tree and there is no pattern here, so it is left
 * 0 and the location lives in the text — a file:line is what a `.rxt`
 * author can act on, and inventing a byte offset into a file for a field
 * whose every other reader means "offset into the pattern" would be a
 * second meaning for one field. */
static int rxt_fail(RxtP *p, size_t line, const char *fmt, ...)
{
    va_list ap;
    char body[256];
    va_start(ap, fmt);
    vsnprintf(body, sizeof body, fmt, ap);
    va_end(ap);
    snprintf(p->err->msg, sizeof p->err->msg, "%s:%zu: %s",
             p->path, line, body);
    p->err->pos = 0;
    p->err->input = PCREC_ERR_INPUT_PATTERN;
    p->failed = 1;
    return -1;
}

static char *arena_strndup(Arena *a, const char *s, size_t n)
{
    char *d = arena_alloc(a, n + 1);
    memcpy(d, s, n);
    d[n] = 0;
    return d;
}

static char *arena_strdup(Arena *a, const char *s)
{
    return arena_strndup(a, s, strlen(s));
}

static const char *value_trimmed(RxtP *p, const char *line)
{
    const char *v = line_value(line);
    size_t n = strlen(v);
    while (n && (v[n - 1] == ' ' || v[n - 1] == '\t')) n--;
    return arena_strndup(p->arena, v, n);
}

/* an `ident` is a PCRE2 group name AND a C identifier (format_design
 * §1.3's terminal) — one rule, so a name that can be a group cannot fail
 * to be a struct member later. */
static int ident_ok(const char *s)
{
    if (!*s) return 0;
    if (!isalpha((unsigned char)*s) && *s != '_') return 0;
    for (const char *p = s + 1; *p; p++)
        if (!isalnum((unsigned char)*p) && *p != '_') return 0;
    return 1;
}

/* `config-list` = ident { "," [ws] ident } — accepted as written, stored
 * as written (the dump is AS-WRITTEN, §1.8), but VALIDATED here so a
 * malformed list is refused at the declaration rather than at whatever
 * later pass first tries to walk it. */
static int config_list_ok(const char *s)
{
    if (!*s) return 0;
    for (;;) {
        s = skip_ws(s);
        const char *start = s;
        while (*s && *s != ',' && !isspace((unsigned char)*s)) s++;
        if (s == start) return 0;
        char save[128];
        size_t n = (size_t)(s - start);
        if (n >= sizeof save) return 0;
        memcpy(save, start, n);
        save[n] = 0;
        if (!ident_ok(save)) return 0;
        s = skip_ws(s);
        if (!*s) return 1;
        if (*s != ',') return 0;
        s++;
    }
}

/* -------------------------------------------------------- file slurping */

/* The file is read whole and split into NUL-terminated lines, because
 * every production here needs to look at the NEXT line (indentation is
 * continuation, §1.2) and a line-at-a-time reader would need a pushback
 * of its own. `\r\n` is trimmed to `\n`: a `.rxt` file edited on Windows
 * must not make every value end in an invisible byte. */
typedef struct { char **v; size_t n; } RxtLines;

static int slurp_lines(RxtP *p, RxtLines *out)
{
    FILE *f = fopen(p->path, "rb");
    if (!f)
        return rxt_fail(p, 0, "cannot open .rxt source file");
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return rxt_fail(p, 0, "cannot seek .rxt source file"); }
    long sz = ftell(f);
    if (sz < 0) { fclose(f); return rxt_fail(p, 0, "cannot size .rxt source file"); }
    rewind(f);
    char *buf = arena_alloc(p->arena, (size_t)sz + 2);
    size_t got = fread(buf, 1, (size_t)sz, f);
    fclose(f);
    buf[got] = 0;

    /* count lines first, then fill — one pass each, no realloc dance */
    size_t nl = 0;
    for (size_t i = 0; i < got; i++) if (buf[i] == '\n') nl++;
    if (got && buf[got - 1] != '\n') nl++;
    char **v = arena_alloc(p->arena, (nl + 1) * sizeof *v);

    size_t k = 0;
    char *s = buf;
    for (size_t i = 0; i <= got; i++) {
        if (i == got) {
            if (s < buf + got) v[k++] = s;
            break;
        }
        if (buf[i] == '\n') {
            buf[i] = 0;
            if (i > 0 && buf[i - 1] == '\r') buf[i - 1] = 0;
            v[k++] = s;
            s = buf + i + 1;
        }
    }
    out->v = v;
    out->n = k;
    return 0;
}

/* ------------------------------------------------------- the productions */

static RxtRow *row_push(RxtP *p, RxtSource *src, RxtDeclKind kind, size_t line)
{
    if (src->nrows == src->rowcap) {
        size_t cap = src->rowcap ? src->rowcap * 2 : 16;
        RxtRow *nv = arena_alloc(p->arena, cap * sizeof *nv);
        if (src->nrows) memcpy(nv, src->rows, src->nrows * sizeof *nv);
        src->rows = nv;
        src->rowcap = cap;
    }
    RxtRow *r = &src->rows[src->nrows++];
    memset(r, 0, sizeof *r);
    r->kind = kind;
    r->line = line;
    r->budget_steps = -1;
    r->budget_frames = -1;
    return r;
}

/* A PROSE VALUE: the one-line form, or the block scalar (`|` then
 * indented lines). The exception is a property of the VALUE production,
 * not of `description` (format_design §1.2), so it lives here and a
 * second prose field would inherit it rather than invent it.
 *
 * The block scalar's indentation rule is YAML's: the FIRST continuation
 * line's indent is the block's, and that many leading bytes are stripped
 * from every line, so relative indentation inside the prose survives.
 * `*i` enters at the `|` line and leaves at the first line that is not
 * part of the value. */
static int parse_prose(RxtP *p, RxtLines *L, size_t *i, const char *val,
                       const char **out)
{
    if (strcmp(val, "|") != 0) {
        *out = arena_strdup(p->arena, val);
        return 0;
    }
    size_t start = *i + 1;
    size_t end = start;
    while (end < L->n && (line_indented(L->v[end]) ||
                          L->v[end][0] == '\0'))
        end++;
    /* trailing blank lines belong to whatever follows, not to the value */
    while (end > start && L->v[end - 1][0] == '\0') end--;
    if (end == start)
        return rxt_fail(p, *i + 1,
                        "block scalar '|' has no indented continuation lines "
                        "(a '|' value is the indented lines below it)");

    size_t indent = 0;
    while (L->v[start][indent] == ' ' || L->v[start][indent] == '\t') indent++;

    size_t total = 0;
    for (size_t k = start; k < end; k++) {
        size_t len = strlen(L->v[k]);
        total += (len > indent ? len - indent : 0) + 1;
    }
    char *buf = arena_alloc(p->arena, total + 1);
    size_t at = 0;
    for (size_t k = start; k < end; k++) {
        const char *ln = L->v[k];
        size_t len = strlen(ln);
        size_t skip = len < indent ? len : indent;
        memcpy(buf + at, ln + skip, len - skip);
        at += len - skip;
        buf[at++] = '\n';
    }
    if (at) at--;                     /* no trailing newline on the value */
    buf[at] = 0;
    *out = buf;
    *i = end - 1;                     /* caller's loop does the ++ */
    return 0;
}

/* A SETTINGS LINE — `flags`/`features`/`encoding`/`engine`/`budget`.
 * ONE implementation, used by both the `config` body and a pattern
 * block, because they are the same production in format_design §1.3
 * (`config-line`'s five middle rows are annotated "as a pattern
 * block's"). Two implementations would be two chances to disagree about
 * what `budget frames=` means. `features only` is accepted only where
 * `allow_only` says so — it is a BLOCK line (M14), not a config one. */
static int parse_setting(RxtP *p, RxtRow *r, size_t line, const char *l,
                         int allow_only)
{
    const char *v = value_trimmed(p, l);

    if (tok_is(l, "flags")) {
        if (!*v) return rxt_fail(p, line, "'flags' needs its letters");
        for (const char *q = v; *q; q++)
            if (!isalpha((unsigned char)*q))
                return rxt_fail(p, line,
                                "'flags' takes letters only (got '%s')", v);
        r->flags = arena_strdup(p->arena, v);
        return 0;
    }
    if (tok_is(l, "features")) {
        if (allow_only) {
            /* `features only <list>` (M14): the list REPLACES rather than
             * unions with the config's. Parsed here so the dump's
             * `features_only` column is a fact about the line and not a
             * guess a later resolver makes. */
            if (!strncmp(v, "only", 4) &&
                (v[4] == ' ' || v[4] == '\t')) {
                r->features_only = 1;
                v = skip_ws(v + 4);
            }
        }
        if (!*v) return rxt_fail(p, line, "'features' needs a module list");
        for (const char *q = v; *q; q++)
            if (!isalnum((unsigned char)*q) && *q != ',' && *q != '_' &&
                *q != '-')
                return rxt_fail(p, line,
                                "'features' takes a comma-separated module "
                                "list (got '%s')", v);
        r->features = arena_strdup(p->arena, v);
        return 0;
    }
    if (tok_is(l, "encoding")) {
        if (!ident_ok(v))
            return rxt_fail(p, line,
                            "'encoding' needs an encoding name (got '%s')", v);
        r->encoding = arena_strdup(p->arena, v);
        return 0;
    }
    if (tok_is(l, "engine")) {
        if (strcmp(v, "vm") && strcmp(v, "dfa"))
            return rxt_fail(p, line,
                            "unknown 'engine' value '%s' (want vm or dfa)", v);
        r->engine = arena_strdup(p->arena, v);
        return 0;
    }
    if (tok_is(l, "budget")) {
        long *slot = NULL;
        const char *num = NULL;
        if (!strncmp(v, "steps=", 6))       { slot = &r->budget_steps;  num = v + 6; }
        else if (!strncmp(v, "frames=", 7)) { slot = &r->budget_frames; num = v + 7; }
        else
            return rxt_fail(p, line,
                            "unknown 'budget' spec '%s' (want steps=<n> or "
                            "frames=<n>)", v);
        char *end = NULL;
        long n = strtol(num, &end, 10);
        if (!end || *end || end == num || n < 0)
            return rxt_fail(p, line,
                            "'budget' wants a non-negative integer (got '%s')",
                            num);
        *slot = n;
        return 0;
    }
    return rxt_fail(p, line, "internal: '%s' is not a settings line", l);
}

/* WAVE REFUSAL — the DECIDED (1) shape. The keyword is REAL and in the
 * spec; what it is not is built. Saying "unknown" here sends a reader
 * hunting a typo in a word they just read in the format design. */
static int refuse_wave(RxtP *p, size_t line, const RxtKeyword *kw,
                       const char *ctx)
{
    return rxt_fail(p, line,
                    "'%s' is a wave-%d %s declaration and is NOT IN THIS "
                    "BUILD (this pcrec implements wave 1 of the .rxt format; "
                    "the keyword is real, not a typo)",
                    kw->kw, kw->wave, ctx);
}

static int unknown_token(RxtP *p, size_t line, const char *l, const char *ctx)
{
    size_t n = tok_len(l);
    return rxt_fail(p, line, "'%.*s' is not a %s directive",
                    (int)n, l, ctx);
}

/* `config <name> [from a,b]` and its indented body. */
static int parse_config(RxtP *p, RxtSource *src, RxtLines *L, size_t *i)
{
    size_t line = *i + 1;
    const char *v = line_value(L->v[*i]);
    char name[128];
    const char *e = v;
    while (*e && !isspace((unsigned char)*e)) e++;
    size_t nlen = (size_t)(e - v);
    if (!nlen || nlen >= sizeof name)
        return rxt_fail(p, line, "'config' needs a name");
    memcpy(name, v, nlen); name[nlen] = 0;
    if (!ident_ok(name))
        return rxt_fail(p, line,
                        "'config' name '%s' is not an identifier", name);

    RxtRow *r = row_push(p, src, RXT_DECL_CONFIG, line);
    r->name = arena_strdup(p->arena, name);

    const char *rest = skip_ws(e);
    if (*rest) {
        if (strncmp(rest, "from", 4) || !isspace((unsigned char)rest[4]))
            return rxt_fail(p, line,
                            "'config %s' takes only 'from <list>' after its "
                            "name (got '%s')", name, rest);
        const char *list = skip_ws(rest + 4);
        if (!config_list_ok(list))
            return rxt_fail(p, line,
                            "'config %s from' needs a comma-separated config "
                            "list (got '%s')", name, list);
        r->from_list = arena_strdup(p->arena, list);
    }

    /* duplicate config names are a tier-2 refusal naming BOTH sites
     * (w1_impl §1.3) — a namespace collision the author can only fix if
     * they are told where the other one is. */
    for (size_t k = 0; k + 1 < src->nrows; k++)
        if (src->rows[k].kind == RXT_DECL_CONFIG &&
            !strcmp(src->rows[k].name, name))
            return rxt_fail(p, line,
                            "duplicate config name '%s' (already declared at "
                            "%s:%zu)", name, p->path, src->rows[k].line);

    /* the body: indented lines, closed vocabulary, own context */
    while (*i + 1 < L->n) {
        const char *nx = L->v[*i + 1];
        if (!line_indented(nx)) break;
        (*i)++;
        if (line_blank_or_comment(nx)) continue;
        const char *body = skip_ws(nx);
        size_t bline = *i + 1;
        const RxtKeyword *kw = vocab_find(config_vocab,
                                          sizeof config_vocab / sizeof *config_vocab,
                                          body);
        if (!kw) return unknown_token(p, bline, body, "config-block");
        if (kw->wave > 1) return refuse_wave(p, bline, kw, "config-block");
        if (tok_is(body, "pcrec")) {
            const char *raw = line_value(body);
            if (!*raw)
                return rxt_fail(p, bline, "'pcrec' needs at least one flag");
            r->pcrec_raw = arena_strdup(p->arena, raw);
            continue;
        }
        if (parse_setting(p, r, bline, body, 0) != 0) return -1;
    }
    return 0;
}

/* `target <prefix> = <definition> [with c1,c2]`. PARSED, never built:
 * W1.1 resolves no definition and emits no artifact (§7.3). The
 * definition name is checked to be an identifier and nothing more —
 * "no such definition" is W1.2's refusal, because W1.1 has no definition
 * set to search. */
static int parse_target(RxtP *p, RxtSource *src, RxtLines *L, size_t *i)
{
    size_t line = *i + 1;
    const char *v = line_value(L->v[*i]);
    const char *eq = strchr(v, '=');
    if (!eq)
        return rxt_fail(p, line,
                        "'target' wants '<prefix> = <definition>' (no '=' on "
                        "the line)");
    char prefix[128];
    const char *pe = eq;
    while (pe > v && isspace((unsigned char)pe[-1])) pe--;
    size_t plen = (size_t)(pe - v);
    if (!plen || plen >= sizeof prefix)
        return rxt_fail(p, line, "'target' needs a prefix before the '='");
    memcpy(prefix, v, plen); prefix[plen] = 0;
    if (!ident_ok(prefix))
        return rxt_fail(p, line,
                        "'target' prefix '%s' is not an identifier (it becomes "
                        "the generated symbols' prefix)", prefix);

    const char *rest = skip_ws(eq + 1);
    char def[128];
    const char *de = rest;
    while (*de && !isspace((unsigned char)*de)) de++;
    size_t dlen = (size_t)(de - rest);
    if (!dlen || dlen >= sizeof def)
        return rxt_fail(p, line,
                        "'target %s =' needs a definition name", prefix);
    memcpy(def, rest, dlen); def[dlen] = 0;
    if (!ident_ok(def))
        return rxt_fail(p, line,
                        "'target %s' definition name '%s' is not an "
                        "identifier", prefix, def);

    RxtRow *r = row_push(p, src, RXT_DECL_TARGET, line);
    r->name = arena_strdup(p->arena, prefix);
    r->value = arena_strdup(p->arena, def);

    const char *tail = skip_ws(de);
    if (*tail) {
        if (strncmp(tail, "with", 4) || !isspace((unsigned char)tail[4]))
            return rxt_fail(p, line,
                            "'target %s' takes only 'with <list>' after the "
                            "definition (got '%s')", prefix, tail);
        const char *list = skip_ws(tail + 4);
        if (!config_list_ok(list))
            return rxt_fail(p, line,
                            "'target %s with' needs a comma-separated config "
                            "list (got '%s')", prefix, list);
        r->with_list = arena_strdup(p->arena, list);
    }

    for (size_t k = 0; k + 1 < src->nrows; k++)
        if (src->rows[k].kind == RXT_DECL_TARGET &&
            !strcmp(src->rows[k].name, prefix))
            return rxt_fail(p, line,
                            "duplicate target prefix '%s' (already declared at "
                            "%s:%zu)", prefix, p->path, src->rows[k].line);
    return 0;
}

/* A `config … from` CYCLE is the visited set of the expansion walk, not a
 * separate pass (w1_impl §1.5). W1.1 does not materialise the composition
 * (the dump is AS-WRITTEN), so what runs here is the walk's REACHABILITY
 * half alone: every named config exists, and no chain returns to its
 * start. The refusal names the cycle's members, per §1.3's table. */
static RxtRow *config_by_name(RxtSource *src, const char *name, size_t len)
{
    for (size_t i = 0; i < src->nrows; i++)
        if (src->rows[i].kind == RXT_DECL_CONFIG &&
            strlen(src->rows[i].name) == len &&
            !strncmp(src->rows[i].name, name, len))
            return &src->rows[i];
    return NULL;
}

static int config_walk(RxtP *p, RxtSource *src, RxtRow *r,
                       RxtRow **stack, size_t depth)
{
    for (size_t d = 0; d < depth; d++) {
        if (stack[d] != r) continue;
        /* name every member from the point the cycle closes */
        char members[512];
        size_t at = 0;
        for (size_t k = d; k < depth; k++)
            at += (size_t)snprintf(members + at, sizeof members - at, "%s -> ",
                                   stack[k]->name);
        snprintf(members + at, sizeof members - at, "%s", r->name);
        return rxt_fail(p, r->line,
                        "'config %s from' is a cycle: %s", r->name, members);
    }
    if (depth >= 64)
        return rxt_fail(p, r->line,
                        "'config %s from' nests more than 64 deep", r->name);
    stack[depth] = r;
    if (!r->from_list) return 0;
    const char *s = r->from_list;
    while (*s) {
        s = skip_ws(s);
        const char *start = s;
        while (*s && *s != ',' && !isspace((unsigned char)*s)) s++;
        RxtRow *dep = config_by_name(src, start, (size_t)(s - start));
        if (!dep)
            return rxt_fail(p, r->line,
                            "'config %s from' names '%.*s', which is not a "
                            "config declared in this file", r->name,
                            (int)(s - start), start);
        if (config_walk(p, src, dep, stack, depth + 1) != 0) return -1;
        s = skip_ws(s);
        if (*s == ',') s++;
    }
    return 0;
}

/* ------------------------------------------------------------- the entry */

RxtSource *pcrec_rxt_source_parse(const char *path, pcrec_error *err)
{
    if (err) { err->msg[0] = 0; err->pos = 0; }
    pcrec_error local;
    if (!err) { err = &local; err->msg[0] = 0; err->pos = 0; }

    RxtSource *src = calloc(1, sizeof *src);
    if (!src) return NULL;
    src->arena.cx = NULL;

    RxtP p = { .path = path, .arena = &src->arena, .err = err, .failed = 0 };
    RxtLines L = { 0 };
    if (slurp_lines(&p, &L) != 0) { pcrec_rxt_source_free(src); return NULL; }
    src->path = arena_strdup(&src->arena, path);

    RxtRow *block = NULL;             /* the open pattern block, if any */
    int in_body = 0;

    for (size_t i = 0; i < L.n; i++) {
        const char *l = L.v[i];
        size_t line = i + 1;
        if (line_blank_or_comment(l)) continue;

        /* INDENTATION IS CONTINUATION IN THE HEAD ONLY (format_design
         * §1.2), and every head construct that HAS continuation lines
         * consumes them itself, above. So an indented line reaching here
         * continues nothing — and in the body it is the asymmetry the
         * format states outright, which is worth saying rather than
         * letting it fall into "unknown token". MEASURED, 0 corpus lines
         * begin with whitespace (w1_impl §5), so no existing file can
         * reach either arm. */
        if (line_indented(l)) {
            rxt_fail(&p, line,
                     in_body ? "a pattern block's lines are NOT indented "
                               "(indentation is continuation in the head "
                               "only)"
                             : "indented line continues nothing (the "
                               "declaration above it takes no continuation)");
            pcrec_rxt_source_free(src);
            return NULL;
        }

        if (tok_is(l, "pattern")) {
            in_body = 1;
            if (!src->first_pattern_line) src->first_pattern_line = line;
            block = row_push(&p, src, RXT_DECL_PATTERN, line);
            /* REST-OF-LINE, VERBATIM. `pattern` is the one production
             * whose value keeps every byte to the end of the line — no
             * trimming, no quoting, no escaping (rxt_format.md). Three
             * corpus blocks carry a literal TAB here and in all three the
             * tab IS the thing under test, which is why the dump escapes
             * this column rather than the parser normalising it. */
            {
                const char *after = l + tok_len(l);
                if (*after == ' ' || *after == '\t') after++;
                block->value = arena_strdup(&src->arena, after);
            }
            continue;
        }

        if (!in_body) {
            /* ---- HEAD ---- */
            const RxtKeyword *kw = vocab_find(head_vocab,
                                              sizeof head_vocab / sizeof *head_vocab,
                                              l);
            if (!kw) { unknown_token(&p, line, l, "file-level"); goto fail; }
            if (kw->wave > 1) { refuse_wave(&p, line, kw, "file-level"); goto fail; }

            if (tok_is(l, "config")) {
                if (parse_config(&p, src, &L, &i) != 0) goto fail;
                continue;
            }
            if (tok_is(l, "target")) {
                if (parse_target(&p, src, &L, &i) != 0) goto fail;
                continue;
            }
            if (tok_is(l, "lib")) {
                const char *v = value_trimmed(&p, l);
                /* a `path-ref` is C's own two spellings: "local" or
                 * <store>. The path is RECORDED, never opened — resolving
                 * it against a --lib-path list is [LIB]'s store scan. */
                size_t n = strlen(v);
                if (n < 2 || !((v[0] == '"' && v[n - 1] == '"') ||
                               (v[0] == '<' && v[n - 1] == '>'))) {
                    rxt_fail(&p, line,
                             "'lib' wants a path reference, either \"local\" "
                             "or <store-name> (got '%s')", v);
                    goto fail;
                }
                RxtRow *r = row_push(&p, src, RXT_DECL_LIB, line);
                r->value = arena_strdup(&src->arena, v);
                continue;
            }
            if (tok_is(l, "description")) {
                const char *text = NULL;
                if (parse_prose(&p, &L, &i, line_value(l), &text) != 0) goto fail;
                RxtRow *r = row_push(&p, src, RXT_DECL_DESCRIPTION, line);
                r->value = text;
                continue;
            }
            unknown_token(&p, line, l, "file-level");
            goto fail;
        }

        /* ---- BODY: a pattern block's directive lines ---- */
        {
            const RxtKeyword *kw = vocab_find(block_vocab,
                                              sizeof block_vocab / sizeof *block_vocab,
                                              l);
            if (!kw) {
                /* THE HEAD BOUNDARY, named. A head keyword down here is
                 * not an unknown token — it is a real declaration in the
                 * wrong place, and the reader needs to be told about the
                 * boundary rather than about their spelling (§1.3). */
                const RxtKeyword *hk = vocab_find(head_vocab,
                                                  sizeof head_vocab / sizeof *head_vocab,
                                                  l);
                if (hk)
                    rxt_fail(&p, line,
                             "'%s' is a file-level declaration and the head "
                             "ENDED at the first 'pattern' line (%s:%zu); "
                             "nothing file-level may appear after it",
                             hk->kw, p.path, src->first_pattern_line);
                else
                    unknown_token(&p, line, l, "pattern-block");
                goto fail;
            }
            if (kw->wave > 1) { refuse_wave(&p, line, kw, "pattern-block"); goto fail; }

            /* The EXPECTATION kinds are recognised and skipped whole. A
             * `.rxt` expectation is the harness's business: this parser
             * reads a file to find its definitions and targets, and a
             * compiler that started scoring `m` lines would be a second
             * harness. */
            if (tok_is(l, "m") || tok_is(l, "n") || tok_is(l, "ms") ||
                tok_is(l, "ns") || tok_is(l, "g") || tok_is(l, "gp") ||
                tok_is(l, "gu") || tok_is(l, "perr") ||
                tok_is(l, "frames-buffer="))
                continue;

            if (tok_is(l, "name")) {
                const char *v = value_trimmed(&p, l);
                if (!ident_ok(v)) {
                    rxt_fail(&p, line,
                             "'name' wants an identifier (got '%s')", v);
                    goto fail;
                }
                /* A BLOCK'S `name` IS IN THE FILE NAMESPACE (w1_impl
                 * DECIDED (7), the manager's ruling on r45sem S3) — not
                 * in the pattern's group namespace — so this collision
                 * check is against other blocks and nothing else. */
                for (size_t k = 0; k < src->nrows; k++)
                    if (src->rows[k].kind == RXT_DECL_PATTERN &&
                        &src->rows[k] != block && src->rows[k].name &&
                        !strcmp(src->rows[k].name, v)) {
                        rxt_fail(&p, line,
                                 "duplicate block name '%s' (already named at "
                                 "%s:%zu)", v, p.path, src->rows[k].line);
                        goto fail;
                    }
                block->name = arena_strdup(&src->arena, v);
                continue;
            }
            if (tok_is(l, "description")) {
                /* THE ONE-LINE FORM ONLY, IN A BLOCK. format_design §1.3
                 * gives a block-line `description` the same `prose-value`
                 * the head's takes, which includes the `|` block scalar —
                 * but §1.2's lexical rule says a PATTERN BLOCK's lines are
                 * NOT indented, and a block scalar is defined as indented
                 * continuation. The two cannot both hold in the body, and
                 * the body's rule is the one 3,265 blocks depend on
                 * (R-COMPAT-1), so it wins: `|` is a HEAD form.
                 *
                 * This also keeps the seam honest. run.sh's per-line loop
                 * has no continuation mechanism, and giving the body one
                 * would put head-shaped parsing back into the harness —
                 * the exact thing §1.1's ruling removed. MEASURED free: 0
                 * corpus lines are indented and 0 blocks carry a
                 * `description`, so no existing file can reach either
                 * reading. Raised for the manager rather than settled
                 * silently; see the lane report. */
                const char *v = line_value(l);
                if (!strcmp(v, "|")) {
                    rxt_fail(&p, line,
                             "a pattern block's 'description' takes the "
                             "one-line form only: the '|' block scalar is "
                             "continuation, and a pattern block's lines are "
                             "not indented (the head is where '|' belongs)");
                    goto fail;
                }
                if (!*v) {
                    rxt_fail(&p, line, "'description' needs its text");
                    goto fail;
                }
                block->description = arena_strdup(&src->arena, v);
                continue;
            }
            if (parse_setting(&p, block, line, l, 1) != 0) goto fail;
        }
    }

    /* the `from` cycle check, once every config is known — a `from` may
     * name a config declared later in the file, so this cannot run inline */
    {
        RxtRow *stack[64];
        for (size_t i = 0; i < src->nrows; i++)
            if (src->rows[i].kind == RXT_DECL_CONFIG &&
                config_walk(&p, src, &src->rows[i], stack, 0) != 0)
                goto fail;
    }

    /* A FILE WITH A HEAD AND NO `pattern` BLOCKS IS LEGAL (the grammar
     * permits it, and a pure library file is exactly that shape). It is
     * not an error here, and `first_pattern_line` stays 0 — which is the
     * value run.sh reads as "no body", distinct from a failed call. */
    return src;

fail:
    pcrec_rxt_source_free(src);
    return NULL;
}

void pcrec_rxt_source_free(RxtSource *src)
{
    if (!src) return;
    arena_free(&src->arena);
    free(src);
}

/* ------------------------------------------------- `--list-source`'s TSV */

/* THE RXT-ESCAPE, on columns 4, 5 and 15 (w1_impl §1.8, RULED). The
 * vocabulary is the `.rxt` format's OWN subject escape — `\t \n \r \\
 * \xNN` — already specified in docs/spec/rxt_format.md, already
 * implemented by tests/harness/driver.c's decode(), and already what a
 * `.rxt` author knows. No second decoder is invented for the differential
 * to drift across.
 *
 * IT IS BUILT BEFORE THE CHECK THAT WOULD SILENTLY PASS WITHOUT IT
 * (§7.1 item 2): three corpus blocks carry a literal TAB in the pattern
 * text, and in all three the tab is the thing under test. Emitted raw the
 * field splits and every later column shifts on exactly those rows — a
 * three-row-in-3,265 corruption, which is the size of finding a summary
 * swallows. */
static void put_escaped(StrBuf *sb, const char *s)
{
    if (!s) return;
    for (const unsigned char *q = (const unsigned char *)s; *q; q++) {
        switch (*q) {
        case '\\': sb_puts(sb, "\\\\"); break;
        case '\t': sb_puts(sb, "\\t");  break;
        case '\n': sb_puts(sb, "\\n");  break;
        case '\r': sb_puts(sb, "\\r");  break;
        default:
            /* every other byte that cannot survive a TSV line, by number.
             * Printable bytes and UTF-8 continuation bytes pass through:
             * the escape exists to protect the FRAMING, not to transcode
             * the content. */
            if (*q < 0x20 || *q == 0x7f) sb_printf(sb, "\\x%02x", *q);
            else sb_putc(sb, (char)*q);
            break;
        }
    }
}

static const char *kind_name(RxtDeclKind k)
{
    switch (k) {
    case RXT_DECL_LIB:         return "lib";
    case RXT_DECL_TARGET:      return "target";
    case RXT_DECL_CONFIG:      return "config";
    case RXT_DECL_DESCRIPTION: return "description";
    case RXT_DECL_PATTERN:     return "pattern";
    }
    return "?";
}

/* THE 15 COLUMNS of w1_impl §1.8, in order, append-only under
 * docs/spec/table_contract.md. Kept as a table rather than as fifteen
 * sb_puts calls in the header string so the HEADER and the ROW WRITER
 * cannot disagree about how many there are — the contract's HEADER
 * TRUTHFULNESS check compares them, and a check whose two sides come
 * from one list is the only version of it that means anything. */
static const char *const rxt_columns[] = {
    "kind", "line", "name", "value", "pattern", "flags", "features",
    "features_only", "encoding", "engine", "budget_steps", "budget_frames",
    "with", "from", "pcrec",
};
#define RXT_NCOLS (sizeof rxt_columns / sizeof *rxt_columns)

size_t pcrec_rxt_source_ncols(void) { return RXT_NCOLS; }

char *pcrec_rxt_source_tsv(const RxtSource *src)
{
    StrBuf sb = { 0 };

    sb_puts(&sb,
        "# pcrec --list-source: the .rxt SOURCE file AS WRITTEN (DD-13b W1).\n"
        "# One row per head declaration and per pattern block, in FILE ORDER.\n"
        "# `kind` is the DECLARATION NAME. There is no head/body column: the\n"
        "# head ends at the first `pattern` row, so a head row is exactly one\n"
        "# preceding it — a property of the ORDER, which is what the parse\n"
        "# differential compares.\n"
        "# AS-WRITTEN, never resolved: `config` composition and the `with`/\n"
        "# `from` cascades are validated but NOT applied here, because a\n"
        "# resolved dump would compare pcrec's resolver against no\n"
        "# counterpart. `--list-source --resolved` is named and unbuilt.\n"
        "# Columns 4 (`value`), 5 (`pattern`) and 15 (`pcrec`) are escaped in\n"
        "# the .rxt format's own subject-escape vocabulary (\\t \\n \\r \\\\ \\xNN):\n"
        "# a `pattern` line is rest-of-line verbatim and may contain a TAB.\n"
        "# Empty field = none. Sectionless: `#section` arrives with W2's\n"
        "# `freq` data block, whose `row <offset> <16 counts>` cannot be a\n"
        "# column here under any reading.\n");

    sb_putc(&sb, '#');
    for (size_t c = 0; c < RXT_NCOLS; c++) {
        if (c) sb_putc(&sb, '\t');
        sb_puts(&sb, rxt_columns[c]);
    }
    sb_putc(&sb, '\n');

    for (size_t i = 0; i < src->nrows; i++) {
        const RxtRow *r = &src->rows[i];
        int is_pat = r->kind == RXT_DECL_PATTERN;
        int is_cfg = r->kind == RXT_DECL_CONFIG;

        sb_puts(&sb, kind_name(r->kind));                       /*  1 kind */
        sb_printf(&sb, "\t%zu", r->line);                       /*  2 line */
        sb_putc(&sb, '\t');
        if (r->name) sb_puts(&sb, r->name);                     /*  3 name */
        sb_putc(&sb, '\t');
        /* `value` carries the lib's path-ref, the target's definition
         * name, and a description's text — the three kinds whose payload
         * is one scalar. A block's own `description` rides column 4 too,
         * on the block's row, because a second description column would
         * be a second home for one fact. */
        put_escaped(&sb, is_pat ? r->description : r->value);   /*  4 value */
        sb_putc(&sb, '\t');
        if (is_pat) put_escaped(&sb, r->value);                 /*  5 pattern */
        sb_putc(&sb, '\t');
        if (r->flags) sb_puts(&sb, r->flags);                   /*  6 flags */
        sb_putc(&sb, '\t');
        if (r->features) sb_puts(&sb, r->features);             /*  7 features */
        sb_putc(&sb, '\t');
        if (r->features_only) sb_putc(&sb, '1');                /*  8 features_only */
        sb_putc(&sb, '\t');
        if (r->encoding) sb_puts(&sb, r->encoding);             /*  9 encoding */
        sb_putc(&sb, '\t');
        if (r->engine) sb_puts(&sb, r->engine);                 /* 10 engine */
        sb_putc(&sb, '\t');
        if (r->budget_steps >= 0) sb_printf(&sb, "%ld", r->budget_steps);
        sb_putc(&sb, '\t');                                     /* 11 */
        if (r->budget_frames >= 0) sb_printf(&sb, "%ld", r->budget_frames);
        sb_putc(&sb, '\t');                                     /* 12 */
        if (r->with_list) sb_puts(&sb, r->with_list);           /* 13 with */
        sb_putc(&sb, '\t');
        if (r->from_list) sb_puts(&sb, r->from_list);           /* 14 from */
        sb_putc(&sb, '\t');
        if (is_cfg) put_escaped(&sb, r->pcrec_raw);             /* 15 pcrec */
        sb_putc(&sb, '\n');
    }
    return sb_take(&sb);
}
