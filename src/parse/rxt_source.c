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
#include <errno.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#include "pcrec.h"
#include "core/internal.h"

/* [LIM-1] (D90, 2026-08-30) THE FOUR CAPS THIS HEAD PARSER HAS ALWAYS HAD
 * (docs/spec/limits.md §3.5) but never NAMED — the survey that built
 * src/core/limits.def found them as bare buffer-size literals
 * (`char name[128]`, an inline `64`) rather than as a table row anywhere.
 * Generated here, the single derivation `pcrec --list-limits` dumps and
 * limits.md §3.5 is checked against — values unchanged: 127-byte identifier
 * caps (a 128-byte buffer, one NUL) and a 64-deep `from` nest. */
#define PCREC_LIMIT_RXT_SOURCE(name, value, unit, kind, override, anchor, desc, default_name) \
    enum { name = (value) };
#include "core/limits.def"
#undef PCREC_LIMIT_RXT_SOURCE

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
    { "export",         1 },
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
    __attribute__((format(printf, 3, 4)));

static int rxt_fail(RxtP *p, size_t line, const char *fmt, ...)
{
    /* The prefix is written FIRST and the body straight after it, rather
     * than formatting the body into a scratch buffer and splicing the two.
     * The splice needs a scratch as large as the destination, so gcc's
     * -Wformat-truncation is right to say the result may not fit — and
     * `make strict` is -Werror. Composing in place has nothing to warn
     * about, allocates nothing, and truncates in the one direction that
     * keeps the file and line (which is what a reader acts on) rather
     * than losing them to a long sentence. */
    char *out = p->err->msg;
    size_t cap = sizeof p->err->msg;
    int n = snprintf(out, cap, "%s:%zu: ", p->path, line);
    size_t at = (n < 0) ? 0 : (size_t)n;
    if (at > cap - 1) at = cap - 1;
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(out + at, cap - at, fmt, ap);
    va_end(ap);
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

/* THE SAME VALUE AS line_value, TRAILING WHITESPACE REMOVED, for the
 * kinds whose value is a TOKEN or a LIST rather than rest-of-line.
 *
 * This exists because the OTHER parser accepts what this one would
 * otherwise refuse. run.sh's directive arms all end `[[:space:]]*$`, so
 * `flags i` and `flags i ` are one value there; without this they would
 * be two here, and the two `.rxt` parsers would disagree about a line
 * neither design document distinguishes. MEASURED: 0 corpus directive
 * lines carry trailing whitespace, so the disagreement is unreachable
 * today — which is exactly why it is worth fixing now rather than
 * leaving the two parsers to agree by luck of the corpus (three corpus
 * files DO carry trailing whitespace on other lines, where it is data).
 *
 * Returns an arena copy: once anything is trimmed off the end, the value
 * is no longer a suffix of the line. */
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

/* [DD-13b.W1.3] A DEFINITION NAME IS NOT AN IDENTIFIER, AND THAT IS THE
 * MANAGER'S RULING (2026-09-03, `dd13b syntax is the manager's`), taken on
 * the bench's O-13 §4(a): of the bench's pattern ids, all but a handful
 * carry a `-` (`cls-upto-64`, `ctx-lazy-256`, `w-512`), so requiring an
 * identifier here would mean every set that ever became an `.rxt` source
 * had to carry a name map beside it — a second place a pattern's identity
 * is written, which is the shape this project refuses everywhere else.
 *
 * SO A BLOCK'S `name`, AND A `target` ROW'S DEFINITION REFERENCE, ADMIT
 * `-` AND `.` AFTER THE FIRST BYTE. The first byte stays `[A-Za-z_]`
 * because the MAPPED name (below) must be a C identifier and no mapping
 * can repair a leading digit or `-`.
 *
 * IT DOES NOT WIDEN A GROUP NAME, and the boundary is worth stating where
 * a reader meets the rule: a block's `name` lives in the FILE namespace
 * (w1_impl DECIDED (7)), never in the pattern's group namespace, so
 * `(?&some-id)` is still refused by PCRE2's own name grammar
 * (`pcrec_group_name_scan`, mod_recursion.c) and D26 makes that PCRE2's
 * rule rather than one this format may widen. A `-`/`.` definition is
 * therefore BUILDABLE as a target and NOT CALLABLE from a pattern —
 * exactly what a bench set needs, since its patterns never call each
 * other, and exactly what a library meant to be composed must avoid.
 *
 * THREE PARSERS READ THIS GRAMMAR AND THEY MOVE TOGETHER (D94's rule
 * applied to a grammar rather than to a number): leg A is here, leg B is
 * `tests/harness/run.sh`'s `^name[[:space:]]+(...)` arm, leg C is
 * `tests/harness/verify_rxt.py`'s `NAME_RE`. C1's three-parser
 * differential is what makes them agree; a fourth reader cannot be added
 * quietly. */
static int defname_ok(const char *s)
{
    if (!*s) return 0;
    if (!isalpha((unsigned char)*s) && *s != '_') return 0;
    for (const char *p = s + 1; *p; p++)
        if (!isalnum((unsigned char)*p) && *p != '_' && *p != '-' && *p != '.')
            return 0;
    return 1;
}

/* THE SAME RULE, over a BOUNDED span rather than a NUL-terminated string
 * (r46sem finding 8): `config_list_ok` used to copy each element into a
 * fixed `char save[128]` before calling `ident_ok` on it, so an element
 * over 127 bytes silently returned "invalid list" with no diagnostic that
 * named the cap. Checking the span directly needs no buffer, no copy, and
 * no cap at all — an identifier inside a config list has no length limit
 * of its own, only the ones `config`/`target`'s own names have (see
 * `parse_config`/`parse_target` below, and docs/spec/limits.md). */
static int ident_ok_n(const char *s, size_t n)
{
    if (!n) return 0;
    if (!isalpha((unsigned char)s[0]) && s[0] != '_') return 0;
    for (size_t i = 1; i < n; i++)
        if (!isalnum((unsigned char)s[i]) && s[i] != '_') return 0;
    return 1;
}

/* [DD-13b.W1.3] THE NAME -> PREFIX MAPPING, and it has ONE HOME because
 * the collision refusal is stated OVER it: `-` and `.` become `_`, every
 * other byte is copied. A second copy of this loop would be a second
 * answer to "do these two names collide", which is the whole question the
 * refusal exists to answer.
 *
 * It is total on every name `defname_ok` admits, and it is NOT injective —
 * `a-b` and `a.b` both map to `a_b`. That is not a defect to design away
 * (a mapping that never collided would have to mangle the name a reader
 * wrote); it is the reason the refusal exists, and the reason the
 * diagnostic names BOTH definitions rather than only the prefix they
 * share. Writes into `dst`, which must hold `strlen(name) + 1`. */
void pcrec_rxt_prefix_from_name(const char *name, char *dst, size_t dstsz)
{
    size_t j = 0;
    for (const char *q = name; *q && j + 1 < dstsz; q++)
        dst[j++] = (*q == '-' || *q == '.') ? '_' : *q;
    dst[j] = 0;
}

/* `config-list` = ident { "," [ws] ident } — accepted as written, stored
 * as written (the dump is AS-WRITTEN, §1.8), but VALIDATED here so a
 * malformed list is refused at the declaration rather than at whatever
 * later pass first tries to walk it.
 *
 * [DD-13b.W1.1 r46sem finding 2] A TAB ANYWHERE IN THE LIST IS REFUSED,
 * never accepted as a separator. `skip_ws` (below) treats space and tab
 * identically, because it has to for the ordinary "a, b" case between
 * items — so without this a list value could carry a literal tab through
 * to columns 13/14 of `--list-source`'s TSV UNESCAPED (they are not among
 * the three escaped columns, §1.8), splitting the row and shifting every
 * later field. Ruled: a tab inside a comma list is never what an author
 * means, so the construct refuses rather than the dump growing a fourth
 * escaped column for two fields that should never need one. */
static int config_list_ok(const char *s)
{
    if (!*s) return 0;
    if (strchr(s, '\t')) return 0;
    for (;;) {
        s = skip_ws(s);
        const char *start = s;
        while (*s && *s != ',' && !isspace((unsigned char)*s)) s++;
        if (s == start) return 0;
        if (!ident_ok_n(start, (size_t)(s - start))) return 0;
        s = skip_ws(s);
        if (!*s) return 1;
        if (*s != ',') return 0;
        s++;
    }
}

/* THE SAME TRAILING-WHITESPACE RULE `value_trimmed` GIVES A TOKEN VALUE
 * (r46sem finding 21), for a raw span that is not itself a `line_value`
 * call — `with`/`from`'s list text, which is a SUBSTRING of the
 * declaration line rather than "everything after the keyword". Without
 * this, `target t = d with a, b  ` (two trailing spaces) stored the
 * spaces into column 13 of the dump, and two files differing only in
 * trailing whitespace on this line produced different TSV bytes — exactly
 * what the C1 byte-for-byte differential exists to notice. */
static const char *rtrim_ws(Arena *a, const char *s)
{
    size_t n = strlen(s);
    while (n && (s[n - 1] == ' ' || s[n - 1] == '\t')) n--;
    return arena_strndup(a, s, n);
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
    /* [DD-13b.W1.1 r46sem finding 23] A DIRECTORY MUST BE REFUSED BY
     * NAME, not silently read as an empty file. On Linux `fopen(dir,
     * "rb")` SUCCEEDS and `fseek`/`ftell` succeed too (a directory has a
     * size), so without this check `fread` returns 0 (EISDIR, previously
     * unchecked), `slurp_lines` reports zero lines, and
     * `pcrec_rxt_source_parse` returns a valid EMPTY `RxtSource` —
     * `pcrec --list-source tests/` printed the header and exited 0. That
     * is the same "an empty successful dump reads as success" shape
     * `--min-files` closes one directory over (r45chk N1), here one level
     * lower. `stat` before `fopen` gives a diagnostic that names the
     * actual problem, rather than relying on `fread`'s EISDIR behaviour
     * (which sets the stream's error indicator on this platform but is
     * not a portable guarantee to lean on for the primary check). */
    struct stat st;
    if (stat(p->path, &st) != 0)
        return rxt_fail(p, 0, "cannot stat .rxt source file");
    if (!S_ISREG(st.st_mode))
        return rxt_fail(p, 0,
                        "not a regular file (a directory or special file "
                        "cannot be a .rxt source)");
    FILE *f = fopen(p->path, "rb");
    if (!f)
        return rxt_fail(p, 0, "cannot open .rxt source file");
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return rxt_fail(p, 0, "cannot seek .rxt source file"); }
    long sz = ftell(f);
    if (sz < 0) { fclose(f); return rxt_fail(p, 0, "cannot size .rxt source file"); }
    rewind(f);
    char *buf = arena_alloc(p->arena, (size_t)sz + 2);
    size_t got = fread(buf, 1, (size_t)sz, f);
    if (ferror(f)) { fclose(f); return rxt_fail(p, 0, "error reading .rxt source file"); }
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
    /* [DD-13b.W1.1 r46sem finding 10, RULED by the manager 2026-08-30] A
     * BLANK LINE ENDS THE CONTINUATION — for a block scalar exactly as it
     * already did for a `config` body (`parse_config`'s own `if
     * (!line_indented(nx)) break;`, unchanged): the body IS the indented
     * continuation, a blank line is not indented, so it terminates like
     * any other non-indented line. This used to stop at the first
     * NON-indented, NON-blank line, treating an INTERIOR blank line as
     * part of the value (only trailing blanks were trimmed) — a second,
     * disagreeing answer to the same question format_design.md calls
     * "the same rule". A directive after the blank line belongs to the
     * FILE, not to whatever the blank line's continuation would have
     * been. */
    size_t start = *i + 1;
    size_t end = start;
    while (end < L->n && line_indented(L->v[end]))
        end++;
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
        /* [DD-13b.W1.1 r46sem finding 3] ONLY `i` IS DEFINED
         * (docs/spec/rxt_format.md, tests/harness/run.sh's own arm) — this
         * leg used to accept any run of letters, which made a corpus block
         * `flags xmz` dump `flags=xmz` here while leg B hard-errors it,
         * the exact "three parsers, three answers, on a line the spec
         * rules" class this step's remedy targets. */
        if (!*v) return rxt_fail(p, line, "'flags' needs its letters");
        if (strcmp(v, "i") != 0)
            return rxt_fail(p, line,
                            "unknown flag letter(s) '%s' (only 'i' is "
                            "defined)", v);
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
        /* [DD-13b.W1.1 r46sem finding 4, RULED] ONLY `vm` FOR W1.1 — the
         * smaller change; `dfa` arrives when a test needs it (D77). This
         * leg used to accept `dfa` while leg B (`tests/harness/run.sh`)
         * already refused it, which is a D80 defect on its face: the two
         * parsers disagreed about a directive the format's own spec
         * paragraph (docs/spec/rxt_format.md) already ruled in `vm`'s
         * favor — only the `--list-source` COLUMN TABLE contradicted it,
         * fixed in the same change as this. */
        if (strcmp(v, "vm"))
            return rxt_fail(p, line,
                            "unknown 'engine' value '%s' (only vm is "
                            "defined)", v);
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
        /* [DD-13b.W1.1 r46sem finding 12] LEG B's ALPHABET IS `[0-9]+`
         * with no sign and no leading space; this leg used to accept a
         * leading `+` (strtol's own grammar) AND silently clamp an
         * overflowing value to LONG_MAX with `errno` never checked, so
         * `budget steps=99999999999999999999` reported
         * `9223372036854775807` in the dump with no diagnostic at all.
         * Requiring the FIRST byte to be a bare digit closes the sign/
         * leading-whitespace gap in one test (strtol's own whitespace
         * skip and its `+`/`-` prefix are both non-digit first bytes);
         * checking `errno == ERANGE` closes the overflow. */
        if (!isdigit((unsigned char)*num))
            return rxt_fail(p, line,
                            "'budget' wants a non-negative integer with no "
                            "sign or leading space (got '%s')", num);
        errno = 0;
        char *end = NULL;
        long n = strtol(num, &end, 10);
        if (!end || *end || end == num || n < 0 || errno == ERANGE)
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
    char name[RXT_CONFIG_NAME_MAX + 1];
    const char *e = v;
    while (*e && !isspace((unsigned char)*e)) e++;
    size_t nlen = (size_t)(e - v);
    if (!nlen)
        return rxt_fail(p, line, "'config' needs a name");
    /* [DD-13b.W1.1 r46sem finding 8] A DISTINCT DIAGNOSTIC NAMING THE CAP.
     * This used to fall into the SAME "needs a name" message a genuinely
     * missing name gets — which tells an author with a too-long name a
     * FALSE thing about their line (it has a name; it is too long), worse
     * than no message at all. docs/spec/limits.md carries the 128-byte
     * identifier cap this and the two `target` fields below share. */
    if (nlen >= sizeof name)
        return rxt_fail(p, line,
                        "'config' name is too long (%zu bytes, max %zu)",
                        nlen, sizeof name - 1);
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
        r->from_list = rtrim_ws(p->arena, list);
    }

    /* duplicate config names are a tier-2 refusal naming BOTH sites
     * (w1_impl §1.3) — a namespace collision the author can only fix if
     * they are told where the other one is. */
    for (size_t k = 0; k + 1 < src->nrows; k++)
        if (src->rows[k].kind == RXT_DECL_CONFIG &&
            !strcmp(src->rows[k].name, name))
            return rxt_fail(p, line,
                            "duplicate config name '%s' (already declared "
                            "on line %zu)", name, src->rows[k].line);

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
        if (!kw) {
            /* [DD-13b.W1.1 r46sem finding 11] `line_blank_or_comment`
             * tests the RAW first byte for '#' (above), so it can never
             * fire here — `body` is always indented (the caller already
             * checked `line_indented(nx)`), so its first byte after
             * `skip_ws` is never a space. An indented `# note` therefore
             * reaches this catch-all and, without this arm, is reported
             * as "'#' is not a config-block directive" — spec-conformant
             * (a `#` anywhere but column 1 is data) but confusing in the
             * one region where indentation is structural. Named rather
             * than fixed: the grammar decision (allow a column-1-relative
             * comment inside a head continuation) is left open (sem10's
             * sibling), but the diagnostic at least says what happened. */
            if (*body == '#')
                return rxt_fail(p, bline,
                                "a comment must start in column 1 (this '#' "
                                "is indented, and indentation inside a "
                                "'config' body is continuation, not "
                                "commentary — format_design.md's lexical "
                                "rule)");
            return unknown_token(p, bline, body, "config-block");
        }
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
    char prefix[RXT_TARGET_PREFIX_MAX + 1];
    const char *pe = eq;
    while (pe > v && isspace((unsigned char)pe[-1])) pe--;
    size_t plen = (size_t)(pe - v);
    /* [DD-13b.W1.3] `target = <definition>` — THE PREFIX OMITTED MEANS
     * "derive it from the definition name". It is the exporter's form: a
     * bench set's ids carry `-`, a C prefix cannot, and writing the
     * mapping out by hand 33 times is 33 chances to write it differently
     * once. An EMPTY left side is now this shorthand and no longer the
     * "needs a prefix" refusal; a left side that is present is checked
     * exactly as before, so nothing an author already wrote changes
     * meaning.
     *
     * It does not repeal format_design §2.7's "every other file builds
     * nothing unless it says so": this IS the file saying so. A `name`d
     * block alone still declares a definition and builds nothing. */
    int derived = (plen == 0);
    if (!derived) {
        /* [DD-13b.W1.1 r46sem finding 8] see parse_config's twin above: a
         * distinct diagnostic naming the cap, not the "needs a prefix"
         * message a genuinely missing prefix gets. */
        if (plen >= sizeof prefix)
            return rxt_fail(p, line,
                            "'target' prefix is too long (%zu bytes, max %zu)",
                            plen, sizeof prefix - 1);
        memcpy(prefix, v, plen); prefix[plen] = 0;
        if (!ident_ok(prefix))
            return rxt_fail(p, line,
                            "'target' prefix '%s' is not an identifier (it "
                            "becomes the generated symbols' prefix)", prefix);
    }

    const char *rest = skip_ws(eq + 1);
    char def[RXT_TARGET_DEF_MAX + 1];
    const char *de = rest;
    while (*de && !isspace((unsigned char)*de)) de++;
    size_t dlen = (size_t)(de - rest);
    if (!dlen)
        return rxt_fail(p, line,
                        "'target %s =' needs a definition name", prefix);
    /* [DD-13b.W1.1 r46sem finding 8] see the two twins above. */
    if (dlen >= sizeof def)
        return rxt_fail(p, line,
                        "'target %s =' definition name is too long (%zu "
                        "bytes, max %zu)", prefix, dlen, sizeof def - 1);
    memcpy(def, rest, dlen); def[dlen] = 0;
    /* [DD-13b.W1.3] `defname_ok`: a target names a DEFINITION, which is a
     * file-namespace name and may carry `-`/`.`. The PREFIX above stays an
     * identifier — it is what the emitted symbols are built from. */
    if (!defname_ok(def))
        return rxt_fail(p, line,
                        "'target %s' definition name '%s' is not a definition "
                        "name (a letter or '_' then letters, digits, '_', '-' "
                        "or '.')",
                        derived ? "=" : prefix, def);
    if (derived) {
        pcrec_rxt_prefix_from_name(def, prefix, sizeof prefix);
        if (!ident_ok(prefix))
            return rxt_fail(p, line,
                            "'target = %s' cannot derive a prefix: '%s' is not "
                            "an identifier even with '-' and '.' mapped to "
                            "'_'", def, prefix);
    }

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
        r->with_list = rtrim_ws(p->arena, list);
    }

    /* [DD-13b.W1.3] THE COLLISION REFUSAL, and the mapping made it reachable
     * from two DIFFERENT names. `a-b` and `a.b` are distinct definitions and
     * both map to `a_b`; before the mapping the only way to collide was to
     * write one prefix twice, so naming the prefix alone was a complete
     * answer. It is not any more — a reader shown only `a_b` cannot tell
     * which two of their names produced it — so the diagnostic names BOTH
     * definitions when they differ, and keeps the old sentence when they do
     * not. Two shapes, one check, because they are one collision.
     *
     * MEASURED (2026-09-03, over every `patterns` directory under
     * `/home/duxevents/pcrec-bench/bench`): across the bench's 90 ids the mapping
     * produces exactly one collision, `floor`, and it is CROSS-SET (each of
     * the four sets carries its own `floor.rx`) — so no single-set export
     * collides, and the refusal fires exactly where sets are merged, which
     * is where it should. */
    for (size_t k = 0; k + 1 < src->nrows; k++)
        if (src->rows[k].kind == RXT_DECL_TARGET &&
            !strcmp(src->rows[k].name, prefix)) {
            if (strcmp(src->rows[k].value, def) != 0)
                return rxt_fail(p, line,
                                "definitions '%s' and '%s' (line %zu) both map "
                                "to target prefix '%s'; a name's '-'/'.' "
                                "become '_', so give one an explicit prefix",
                                def, src->rows[k].value, src->rows[k].line,
                                prefix);
            return rxt_fail(p, line,
                            "duplicate target prefix '%s' (already declared "
                            "on line %zu)", prefix, src->rows[k].line);
        }
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
        for (size_t k = d; k < depth && at + 1 < sizeof members; k++) {
            int w = snprintf(members + at, sizeof members - at, "%s -> ",
                             stack[k]->name);
            /* snprintf returns what it WOULD have written; letting that
             * past `at` would make the next `sizeof members - at` wrap to
             * an enormous size_t and hand snprintf a bogus bound. */
            if (w < 0) break;
            at += (size_t)w;
            if (at >= sizeof members) { at = sizeof members - 1; break; }
        }
        snprintf(members + at, sizeof members - at, "%s", r->name);
        return rxt_fail(p, r->line,
                        "'config %s from' is a cycle: %s", r->name, members);
    }
    if (depth >= RXT_FROM_NEST_MAX)
        return rxt_fail(p, r->line,
                        "'config %s from' nests more than %d deep",
                        r->name, RXT_FROM_NEST_MAX);
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
            rxt_fail(&p, line, "%s",
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
                /* THE SEPARATOR IS A SPACE, NOT "whitespace", and that is
                 * agreement with the other parser rather than pedantry:
                 * run.sh's arm is `^pattern\ (.*)$` — a LITERAL space —
                 * so `pattern<TAB>abc` is a hard error there. Accepting
                 * it here would make the two parsers disagree about a
                 * line, which is exactly what the differential exists to
                 * find, and it would find it in a file somebody wrote
                 * rather than in this comment. MEASURED: 0 of the 3,265
                 * pattern lines use a tab separator. */
                const char *after = l + tok_len(l);
                if (*after != ' ') {
                    rxt_fail(&p, line,
                             "'pattern' wants a single space before its "
                             "regex (the pattern text is rest-of-line "
                             "verbatim from there, so the separator cannot "
                             "be part of it)");
                    goto fail;
                }
                after++;
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
                 * <store>. Both are RECORDED here and neither is opened:
                 * this parser touches no filesystem at all, which is what
                 * keeps `--list-source` a pure function of the file's
                 * bytes. [DD-13b.W1.2]'s `pcrec_rxt_source_resolve` is
                 * where the "local" form's path is RESOLVED (existence
                 * only, against the source's own directory and the
                 * --lib-path list) and where the <store> form is refused as
                 * not in this build; a library's CONTENTS are the
                 * composer's, and the store SCAN is [LIB]'s. */
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
                             "ENDED at the first 'pattern' line (line %zu); "
                             "nothing file-level may appear after it",
                             hk->kw, src->first_pattern_line);
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
                /* [DD-13b.W1.3] `defname_ok`, not `ident_ok`: see that
                 * function's header for the ruling and for the one
                 * boundary it draws (buildable as a target, not callable
                 * from a pattern). */
                if (!defname_ok(v)) {
                    rxt_fail(&p, line,
                             "'name' wants a definition name — a letter or "
                             "'_' then letters, digits, '_', '-' or '.' "
                             "(got '%s')", v);
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
                                 "duplicate block name '%s' (already named on "
                                 "line %zu)", v, src->rows[k].line);
                        goto fail;
                    }
                block->name = arena_strdup(&src->arena, v);
                continue;
            }
            if (tok_is(l, "export")) {
                /* [DD-13b.W1.3, D89 addendum point 2] THE LIBRARY'S OWN
                 * INTERFACE, DECLARED. Frank: "for library use, the library
                 * explicitly provides the names it intends to export."
                 * Delivery stopped being "every named group" — the default
                 * is now NOTHING exported, and a definition says what it
                 * offers.
                 *
                 * THE `config-list` SHAPE, because `with`/`use`/`from`
                 * already use it and a fourth list syntax would be a fourth
                 * thing to get wrong. `config_list_ok` is the SAME validator
                 * those three run, so a tab or a malformed element is
                 * refused here in the words it is refused there.
                 *
                 * WHAT IS *NOT* CHECKED HERE: whether the definition
                 * actually declares a group by each name. That is a question
                 * about the PATTERN, and this parser does not parse
                 * patterns — the composer answers it at bind time, where the
                 * sub-parse's own `named_groups` list is in hand, and
                 * refuses naming both the export and the definition. Asking
                 * it here would need a second regex parser in the head
                 * reader, which is the one thing the seam ruling forbids. */
                const char *v = value_trimmed(&p, l);
                if (!config_list_ok(v)) {
                    rxt_fail(&p, line,
                             "'export' wants a comma-separated list of "
                             "group names (got '%s')", v);
                    goto fail;
                }
                if (block->exports) {
                    rxt_fail(&p, line,
                             "a block has one 'export' line; this one already "
                             "declared '%s'", block->exports);
                    goto fail;
                }
                block->exports = rtrim_ws(&src->arena, v);
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
                /* [DD-13b.W1.1 r46sem finding 14] COMPARE THE TRIMMED
                 * VALUE, not the exact one — ruled: a `|` with trailing
                 * whitespace is nobody's intended literal, so `description
                 * | ` (one trailing space) is refused as the block-scalar
                 * spelling exactly like bare `description |`, matching
                 * `tests/harness/verify_rxt.py`'s `v.strip() == '|'`
                 * (which already trims). Before this fix the exact
                 * `strcmp` let the trailing-space form fall through and be
                 * accepted as the literal text `"| "` — the one place leg
                 * C was STRICTER than legs A/B rather than in step with
                 * them. */
                size_t vlen = strlen(v);
                while (vlen && (v[vlen - 1] == ' ' || v[vlen - 1] == '\t'))
                    vlen--;
                if (vlen == 1 && v[0] == '|') {
                    rxt_fail(&p, line,
                             "a pattern block's 'description' takes the "
                             "one-line form only: the '|' block scalar is "
                             "continuation, and a pattern block's lines are "
                             "not indented (the head is where '|' belongs)");
                    goto fail;
                }
                /* [DD-13b.W1.1 r46sem finding 13] AN EMPTY DESCRIPTION IS
                 * ACCEPTED, matching legs B and C — `description ` (one
                 * trailing space, no text) used to hard-error here while
                 * both other parsers accept it with an empty value. There
                 * is nothing wrong with a block declaring it has no
                 * description text; "needs its text" was never true of
                 * this line, only of one with nothing after the keyword
                 * at all — which does not reach this arm (see
                 * `vocab_find`'s tokenizer above). */
                block->description = arena_strdup(&src->arena, v);
                continue;
            }
            if (parse_setting(&p, block, line, l, 1) != 0) goto fail;
        }
    }

    /* the `from` cycle check, once every config is known — a `from` may
     * name a config declared later in the file, so this cannot run inline */
    {
        RxtRow *stack[RXT_FROM_NEST_MAX];
        for (size_t i = 0; i < src->nrows; i++)
            if (src->rows[i].kind == RXT_DECL_CONFIG &&
                config_walk(&p, src, &src->rows[i], stack, 0) != 0)
                goto fail;
    }

    /* [DD-13b.W1.1 r46sem finding 7] `target … with c1,c2` NAMES A LIST
     * OF CONFIGS THAT MUST EXIST, and docs/spec/rxt_format.md has always
     * said so ("config composition and the with/from cascades are
     * VALIDATED") — only `from`'s cycle walk above actually did it.
     * `parse_target` checks `with_list` for SYNTAX only (`config_list_ok`)
     * and stores it; nothing ever resolved the names against the file's
     * declared configs, so `target t = d with nosuch` parsed clean. Run as
     * a WHOLE-FILE pass, like the `from` cycle check just above, because a
     * `with` may name a config declared LATER in the file. */
    for (size_t i = 0; i < src->nrows; i++) {
        RxtRow *r = &src->rows[i];
        if (r->kind != RXT_DECL_TARGET || !r->with_list) continue;
        const char *s = r->with_list;
        while (*s) {
            s = skip_ws(s);
            const char *start = s;
            while (*s && *s != ',' && !isspace((unsigned char)*s)) s++;
            if (!config_by_name(src, start, (size_t)(s - start))) {
                rxt_fail(&p, r->line,
                         "'target %s with' names '%.*s', which is not a "
                         "config declared in this file", r->name,
                         (int)(s - start), start);
                goto fail;
            }
            s = skip_ws(s);
            if (*s == ',') s++;
        }
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
    /* [DD-13b.W1.3] the `lib` closure's other files, freed before this one:
     * they were parsed into their own `RxtSource`s (each with its own arena)
     * by `pcrec_rxt_source_resolve`, and the definition set points INTO
     * their arenas. Recursion depth is the `lib` chain's, which the visited
     * set bounds at the number of distinct files. */
    for (size_t i = 0; i < src->nkids; i++) pcrec_rxt_source_free(src->kids[i]);
    free(src->kids);
    arena_free(&src->arena);
    free(src);
}

/* ------------------------------------------- [DD-13b.W1.2] RESOLUTION ----
 *
 * Everything above this line reports the file AS WRITTEN. Everything below
 * answers the three questions `--source` has to answer before it can call
 * `pcrec_compile` even once: which artifacts, from which block, under which
 * settings. `--list-source` never reaches any of it, which is what keeps
 * that dump comparable against run.sh's and verify_rxt.py's own parses —
 * resolution is a third thing only pcrec does, so a resolved dump would
 * compare pcrec's resolver against no counterpart (w1_impl §1.8).
 *
 * NO FILE IS OPENED HERE EXCEPT TO SAY WHETHER IT EXISTS. A `lib` row's
 * path is resolved (does it name a readable file, in the source's own
 * directory or in one of the `--lib-path` entries) because §1.3's refusal
 * table demands a diagnostic naming the path and the list searched. Its
 * CONTENT is never read: pulling definitions out of a library is the
 * composer's, i.e. W1.3's, and [LIB]'s store scan is [LIB]'s.
 */

/* ---- the small list walk both `with` and `from` are spelled in ---- */

typedef struct { const char *s; const char *e; } RxtItem;

/* Yields the next comma-separated item of `*cur`, trimmed, or 0 at the end.
 * `config_list_ok` has already validated the spelling at parse time, so
 * this walk has no grammar of its own to get wrong. */
static int list_next(const char **cur, RxtItem *out)
{
    const char *s = skip_ws(*cur);
    if (!*s) return 0;
    const char *e = s;
    while (*e && *e != ',' && !isspace((unsigned char)*e)) e++;
    out->s = s; out->e = e;
    s = skip_ws(e);
    if (*s == ',') s++;
    *cur = s;
    return e > out->s;
}

/* ---- the settings accumulator ----
 *
 * ONE STRUCT FOR BOTH COMPOSITION LEVELS, which is what stops the two
 * mechanisms §1.5 separates from being written twice. `cfg_merge` is the
 * flat LATER-WINS rule, and it is the only rule `from` and `with` use; the
 * PER-KIND table (features UNION, everything else more-specific-wins) is
 * applied exactly once, at the block, by `resolve_one` below. */
typedef struct {
    const char *flags, *features, *encoding, *engine;
    int         features_only;
    long        budget_steps, budget_frames;
    const char *pcrec_raw;
} RxtSet;

static void set_init(RxtSet *s)
{
    memset(s, 0, sizeof *s);
    s->budget_steps = -1;
    s->budget_frames = -1;
}

/* `a` then `b`, later wins — except `pcrec`, which ACCUMULATES.
 *
 * The exception is not an inconsistency: every other config line is a
 * SETTING and a later one replaces an earlier one, while `pcrec <raw>` is
 * a line kind that may legitimately appear more than once and whose
 * later-wins is the CLI option parser's own, applied to the joined text.
 * Joining is therefore how "later wins" is spelled for that kind, not an
 * escape from it. */
static void cfg_merge(Arena *a, RxtSet *dst, const RxtSet *add)
{
    if (add->flags)     dst->flags = add->flags;
    if (add->features)  dst->features = add->features;
    if (add->encoding)  dst->encoding = add->encoding;
    if (add->engine)    dst->engine = add->engine;
    if (add->budget_steps  >= 0) dst->budget_steps  = add->budget_steps;
    if (add->budget_frames >= 0) dst->budget_frames = add->budget_frames;
    if (add->pcrec_raw) {
        if (!dst->pcrec_raw) dst->pcrec_raw = add->pcrec_raw;
        else {
            size_t n = strlen(dst->pcrec_raw) + 1 + strlen(add->pcrec_raw) + 1;
            char *j = arena_alloc(a, n);
            snprintf(j, n, "%s %s", dst->pcrec_raw, add->pcrec_raw);
            dst->pcrec_raw = j;
        }
    }
}

static void set_from_row(RxtSet *s, const RxtRow *r)
{
    set_init(s);
    s->flags = r->flags;
    s->features = r->features;
    s->features_only = r->features_only;
    s->encoding = r->encoding;
    s->engine = r->engine;
    s->budget_steps = r->budget_steps;
    s->budget_frames = r->budget_frames;
    s->pcrec_raw = r->pcrec_raw;
}

/* A config MATERIALISES ONCE, and `seen` is what makes that true rather
 * than nearly true (§1.5: "`config c from a, b` materialises ONCE at
 * parse"). Without it a DIAMOND double-counts: `target t with dev,
 * release` where `release from dev` expands `dev` twice, and while every
 * ordinary setting is idempotent under later-wins, `pcrec <raw>`
 * ACCUMULATES — so the joined flag text would carry `dev`'s line twice.
 * That is harmless for every flag pcrec has today (each is last-wins) and
 * would stop being harmless the day one is not, which is the wrong thing
 * to leave resting on the flag set's current shape.
 *
 * `seen` spans ONE target's whole `with` composition, not one `from`
 * chain, because the diamond's two arms come from different list members.
 * ORDER is unaffected: skipping an already-materialised config removes a
 * REPEAT, and a repeat under later-wins contributes only what the first
 * visit already did.
 *
 * The cycle and the every-name-exists checks both ran at parse time
 * (`config_walk`), so this walk needs neither — which is the point of
 * doing them there: the reachability question is asked once, by the pass
 * that can name the cycle's members. `seen` therefore terminates a
 * diamond, never a cycle. */
typedef struct { RxtRow **v; size_t n, cap; } RxtSeen;

static int seen_add(Arena *a, RxtSeen *s, RxtRow *r)
{
    for (size_t i = 0; i < s->n; i++) if (s->v[i] == r) return 0;
    if (s->n == s->cap) {
        size_t cap = s->cap ? s->cap * 2 : 8;
        RxtRow **v = arena_alloc(a, cap * sizeof *v);
        for (size_t i = 0; i < s->n; i++) v[i] = s->v[i];
        s->v = v; s->cap = cap;
    }
    s->v[s->n++] = r;
    return 1;
}

static void cfg_effective(RxtSource *src, RxtRow *r, RxtSeen *seen, RxtSet *out)
{
    set_init(out);
    if (!seen_add(&src->arena, seen, r)) return;   /* already materialised */
    if (r->from_list) {
        const char *cur = r->from_list;
        RxtItem it;
        while (list_next(&cur, &it)) {
            RxtRow *dep = config_by_name(src, it.s, (size_t)(it.e - it.s));
            if (!dep) continue;          /* parse already refused this */
            RxtSet sub;
            cfg_effective(src, dep, seen, &sub);
            cfg_merge(&src->arena, out, &sub);
        }
    }
    RxtSet own;
    set_from_row(&own, r);
    cfg_merge(&src->arena, out, &own);
}

/* ---- `lib` path resolution ---- */

static int path_is_file(const char *p)
{
    struct stat st;
    return stat(p, &st) == 0 && S_ISREG(st.st_mode);
}

/* `src->path`'s own directory, arena-owned, "" when it has none. A `lib`
 * reference is relative to THE FILE THAT WROTE IT, not to the process's
 * working directory — a source file that names its library is portable
 * only under that rule, and `--lib-path` is the caller's addition to it
 * rather than its replacement. */
static const char *source_dir(RxtSource *src)
{
    const char *slash = strrchr(src->path, '/');
    if (!slash) return "";
    size_t n = (size_t)(slash - src->path) + 1;   /* keep the '/' */
    char *d = arena_alloc(&src->arena, n + 1);
    memcpy(d, src->path, n);
    d[n] = 0;
    return d;
}

static char *join_path(Arena *a, const char *dir, const char *rest)
{
    size_t nd = strlen(dir);
    int need_slash = nd && dir[nd - 1] != '/';
    size_t n = nd + (size_t)need_slash + strlen(rest) + 1;
    char *p = arena_alloc(a, n);
    snprintf(p, n, "%s%s%s", dir, need_slash ? "/" : "", rest);
    return p;
}

/* Renders the search chain for a diagnostic: the source's own directory
 * first, then every `--lib-path` in order. It is built from the SAME list
 * the search walks, so a message can never name a path the search skipped.
 *
 * THE SOURCE'S OWN DIRECTORY IS NAMED, NOT SPELLED, and that is a size fix
 * rather than a style one. Every diagnostic that carries this chain also
 * carries `rxt_fail`'s `<path>:<line>: ` prefix — so printing the
 * directory's full text here put the SOURCE PATH IN THE MESSAGE TWICE,
 * once as the prefix the reader is already looking at and once inside the
 * chain. On a 256-byte `pcrec_error.msg` that redundancy is what pushed
 * the no-such-definition refusal over the buffer at the very path length
 * its own fixture runs at (263 bytes, MEASURED by the class check one
 * directory over). Saying "the source's own directory" costs 28 bytes
 * whatever the path is, tells the reader the same thing, and reads better.
 * The `--lib-path` entries ARE spelled: those the reader has not been told
 * anywhere else. */
static const char *lib_chain_text(Arena *a, const char *own,
                                  const char *const *dirs, size_t ndirs)
{
    (void)own;
    StrBuf sb = { 0 };
    sb_puts(&sb, "the source's own directory");
    for (size_t i = 0; i < ndirs; i++) sb_printf(&sb, ", '%s'", dirs[i]);
    if (!ndirs) sb_puts(&sb, " (no --lib-path)");
    char *heap = sb_take(&sb);
    size_t n = strlen(heap) + 1;
    char *out = arena_alloc(a, n);
    memcpy(out, heap, n);
    free(heap);
    return out;
}

/* ---- [DD-13b.W1.3] THE `flags` LETTER MAPPING, with ONE home -----------
 *
 * `flags i` means the same thing on a `config` line, on a pattern block and
 * on a DEFINITION, so the letter -> bit mapping is one function and not one
 * loop per caller. It moved here rather than staying in `cli/main.c` because
 * this file is where a definition's letters are read, and a mapping with two
 * homes is the D24 shape one tier down: a letter added to the CLI's loop and
 * not to the composer's would make a library mean one thing when built as a
 * target and another when bound into a caller. */
int pcrec_rxt_flags_from_letters(const char *letters, unsigned long long *out,
                                 char *bad)
{
    unsigned long long f = 0;
    if (letters) {
        for (const char *c = letters; *c; c++) {
            if (*c == 'i') f |= (unsigned long long)PCREC_CASELESS;
            else { if (bad) *bad = *c; return -1; }
        }
    }
    *out = f;
    return 0;
}

/* ---- [DD-13b.W1.3] THE DEFINITION CLOSURE ------------------------------
 *
 * W1.2 resolved a `lib` reference as far as EXISTENCE and deliberately read
 * nothing: a library's CONTENTS were "the composer's, W1.3". This is that.
 *
 * THE WALK IS A FIXPOINT WITH A VISITED SET KEYED ON THE RESOLVED PATH, and
 * both halves of that matter. Keyed on the RESOLVED path so a diamond — two
 * files each `lib`-ing a third — reads the third once and its definitions
 * are one set of definitions rather than two with colliding names; a visited
 * SET so a cycle terminates, which format_design §2.5 makes legal (a library
 * may reasonably `lib` a file that `lib`s it back, and refusing that would
 * be a rule about file layout rather than about meaning).
 *
 * ORDER IS `lib` DECLARATION ORDER, DEPTH FIRST, WITH THIS FILE'S OWN BLOCKS
 * FIRST. It is a stated order rather than an emergent one because a
 * DUPLICATE NAME refusal names the two files it found, and "which one was
 * found first" must be a property of the source text and not of a traversal
 * anyone could change.
 *
 * A DUPLICATE DEFINITION NAME ACROSS THE CLOSURE IS A REFUSAL. K42 records
 * the residual — colliding names have no external oracle — but that is about
 * names the FORMAT cannot see; this one it can, and refusing it here is what
 * keeps the residual from growing. Within ONE file the parser already
 * refuses it (`duplicate block name`); this is the same rule one scope out,
 * and its diagnostic names both files because the two lines are in different
 * ones.
 */
typedef struct {
    RxtP               *p;        /* diagnostics, re-pathed per file      */
    RxtSource          *root;     /* owns the arena and the kid list      */
    const char *const  *dirs;
    size_t              ndirs;
    const char        **seen;     /* resolved paths already read          */
    size_t              nseen, seencap;
    RxtDef             *defs;
    size_t              ndefs, defcap;
} RxtClosure;

/* The `"path"` form's search, EXACTLY as the existence check walks it: the
 * naming file's own directory, then each `--lib-path` in order. Returns the
 * resolved path (arena-owned) or NULL. */
static const char *lib_resolve(RxtClosure *cl, const char *own,
                               const char *ref)
{
    if (ref[0] == '/') return path_is_file(ref) ? ref : NULL;
    const char *cand = join_path(&cl->root->arena, own, ref);
    if (path_is_file(cand)) return cand;
    for (size_t d = 0; d < cl->ndirs; d++) {
        cand = join_path(&cl->root->arena, cl->dirs[d], ref);
        if (path_is_file(cand)) return cand;
    }
    return NULL;
}

static int closure_seen(RxtClosure *cl, const char *path)
{
    for (size_t i = 0; i < cl->nseen; i++)
        if (!strcmp(cl->seen[i], path)) return 1;
    return 0;
}

static int closure_walk(RxtClosure *cl, RxtSource *s, const char *respath);

/* A `lib` row's reference, unquoted; NULL when the row is a store
 * reference (which is refused by the caller, in its own words). */
static const char *lib_ref_text(Arena *a, const char *value)
{
    size_t rl = strlen(value);
    if (rl >= 2 && value[0] == '"' && value[rl - 1] == '"')
        return arena_strndup(a, value + 1, rl - 2);
    return value;
}

static int closure_walk(RxtClosure *cl, RxtSource *s, const char *respath)
{
    if (closure_seen(cl, respath)) return 0;
    if (cl->nseen == cl->seencap) {
        size_t nc = cl->seencap ? cl->seencap * 2 : 8;
        const char **nv = arena_alloc(&cl->root->arena, nc * sizeof *nv);
        for (size_t i = 0; i < cl->nseen; i++) nv[i] = cl->seen[i];
        cl->seen = nv; cl->seencap = nc;
    }
    cl->seen[cl->nseen++] = respath;

    RxtP fp = *cl->p;
    fp.path = s->path;

    /* This file's own named blocks, in file order. */
    for (size_t i = 0; i < s->nrows; i++) {
        const RxtRow *r = &s->rows[i];
        if (r->kind != RXT_DECL_PATTERN || !r->name) continue;
        for (size_t k = 0; k < cl->ndefs; k++)
            if (!strcmp(cl->defs[k].name, r->name))
                return rxt_fail(&fp, r->line,
                                "definition '%s' is declared twice in the lib "
                                "closure: also at %s:%zu",
                                r->name, cl->defs[k].file, cl->defs[k].line);
        unsigned long long f = 0;
        char badc = 0;
        if (pcrec_rxt_flags_from_letters(r->flags, &f, &badc) != 0)
            return rxt_fail(&fp, r->line,
                            "unknown flag letter '%c' in `flags %s` on "
                            "definition '%s'", badc, r->flags, r->name);
        if (cl->ndefs == cl->defcap) {
            size_t nc = cl->defcap ? cl->defcap * 2 : 8;
            RxtDef *nv = arena_alloc(&cl->root->arena, nc * sizeof *nv);
            for (size_t k = 0; k < cl->ndefs; k++) nv[k] = cl->defs[k];
            cl->defs = nv; cl->defcap = nc;
        }
        RxtDef *d = &cl->defs[cl->ndefs++];
        d->name = r->name;
        d->pattern = r->value;
        d->flags = f;
        d->encoding = r->encoding;
        d->exports = r->exports;
        d->file = s->path;
        d->line = r->line;
    }

    /* Then its `lib` rows, in declaration order, depth first. */
    const char *own = source_dir(s);
    for (size_t i = 0; i < s->nrows; i++) {
        const RxtRow *r = &s->rows[i];
        if (r->kind != RXT_DECL_LIB || !r->value) continue;
        if (r->value[0] == '<') continue;      /* refused by the caller */
        const char *ref = lib_ref_text(&cl->root->arena, r->value);
        const char *rp = lib_resolve(cl, own, ref);
        if (!rp) continue;                     /* refused by the caller */
        if (closure_seen(cl, rp)) continue;
        pcrec_error kerr = { 0 };
        RxtSource *kid = pcrec_rxt_source_parse(rp, &kerr);
        if (!kid)
            return rxt_fail(&fp, r->line,
                            "'lib %s' does not parse: %s", r->value, kerr.msg);
        if (cl->root->nkids == cl->root->kidcap) {
            size_t nc = cl->root->kidcap ? cl->root->kidcap * 2 : 4;
            RxtSource **nv = realloc(cl->root->kids, nc * sizeof *nv);
            if (!nv) { pcrec_rxt_source_free(kid);
                       return rxt_fail(&fp, r->line, "out of memory reading "
                                       "'lib %s'", r->value); }
            cl->root->kids = nv; cl->root->kidcap = nc;
        }
        cl->root->kids[cl->root->nkids++] = kid;
        if (closure_walk(cl, kid, rp) != 0) return -1;
    }
    return 0;
}

/* ---- the entry ---- */

int pcrec_rxt_source_resolve(RxtSource *src,
                             const char *const *libdirs, size_t nlib,
                             RxtTarget **out, size_t *nout,
                             pcrec_error *err)
{
    RxtP p = { .path = src->path, .arena = &src->arena, .err = err, .failed = 0 };
    *out = NULL;
    *nout = 0;

    const char *own = source_dir(src);
    const char *chain = lib_chain_text(&src->arena, own, libdirs, nlib);

    /* (1) Every `lib` reference must name a file that EXISTS. Its contents
     * are not read — see this section's header. */
    for (size_t i = 0; i < src->nrows; i++) {
        const RxtRow *r = &src->rows[i];
        if (r->kind != RXT_DECL_LIB || !r->value) continue;
        const char *ref = r->value;
        size_t rl = strlen(ref);
        /* THE TWO SPELLINGS ARE TWO DIFFERENT MECHANISMS, and only one of
         * them is a path. `<store-name>` names a library STORE, whose scan
         * is [LIB]'s row; treating it as a filename would be a silently
         * wrong search that reports "no readable file" for a reference that
         * was never meant to be one. It is refused as REAL AND NOT IN THIS
         * BUILD — the same tier the head grammar gives a wave-2 keyword,
         * and for the same reason (DECIDED (1)). */
        if (rl >= 2 && ref[0] == '<')
            return rxt_fail(&p, r->line,
                            "'lib %s' is a library-STORE reference, which is "
                            "NOT IN THIS BUILD (the store scan arrives with "
                            "[LIB]; the spelling is real, not a typo). The "
                            "\"path\" form resolves today", ref);
        /* a quoted path-ref keeps its quotes in `value` (AS WRITTEN); the
         * reference itself is what is between them. */
        if (rl >= 2 && ref[0] == '"' && ref[rl - 1] == '"') {
            char *unq = arena_alloc(&src->arena, rl - 1);
            memcpy(unq, ref + 1, rl - 2);
            unq[rl - 2] = 0;
            ref = unq;
        }
        int found = 0;
        if (ref[0] == '/') found = path_is_file(ref);
        else {
            found = path_is_file(join_path(&src->arena, own, ref));
            for (size_t d = 0; !found && d < nlib; d++)
                found = path_is_file(join_path(&src->arena, libdirs[d], ref));
        }
        if (!found)
            return rxt_fail(&p, r->line,
                            "'lib %s' names no readable file; searched %s",
                            r->value, chain);
    }

    /* (1b) [DD-13b.W1.3] THE DEFINITION CLOSURE. Built ONCE per source and
     * shared by every target, because it is a property of the FILE. It runs
     * AFTER the existence loop above so a missing or store-shaped `lib`
     * keeps its own diagnostic — the closure walk skips exactly those two
     * cases, which is why they are refused before it rather than inside it.
     *
     * NEVER NULL. A file with no named block anywhere in its closure gets an
     * EMPTY set rather than a NULL one, so the composer has one thing to
     * test and every `--source` build takes the same path. */
    RxtDefs *defs = arena_alloc(&src->arena, sizeof *defs);
    {
        RxtClosure cl = { .p = &p, .root = src, .dirs = libdirs, .ndirs = nlib };
        if (closure_walk(&cl, src, src->path) != 0) return -1;
        defs->v = cl.defs;
        defs->n = cl.ndefs;
    }

    /* (2) WHICH ARTIFACTS. */
    size_t ntarget = 0, npattern = 0;
    const RxtRow *lone = NULL;
    for (size_t i = 0; i < src->nrows; i++) {
        if (src->rows[i].kind == RXT_DECL_TARGET) ntarget++;
        else if (src->rows[i].kind == RXT_DECL_PATTERN) {
            npattern++;
            lone = &src->rows[i];
        }
    }

    if (!ntarget) {
        /* THE COMPATIBILITY DEFAULT (Frank, format_design §6.4): no
         * `target` and exactly ONE UNNAMED block means `target rx`, so a
         * file that is a single pattern with expectations — which is what
         * every one of the corpus's 179 files is — builds the artifact it
         * always did without declaring anything.
         *
         * ANYTHING ELSE WITH NO `target` BUILDS NOTHING, and that is not an
         * error: a library ships nothing by itself (format_design §6.1).
         * Zero targets, exit 0, no diagnostic. Two observables, never
         * confused — a file that CANNOT be built refuses, a file that
         * declares nothing to build is silent. */
        if (npattern == 1 && !lone->name) {
            RxtTarget *t = arena_alloc(&src->arena, sizeof *t);
            memset(t, 0, sizeof *t);
            t->prefix = "rx";
            t->name = "rx";
            t->pattern = lone->value;
            t->line = lone->line;
            t->block_line = lone->line;
            t->flags = lone->flags;
            t->features = lone->features;
            t->features_only = lone->features_only;
            t->encoding = lone->encoding;
            t->engine = lone->engine;
            t->budget_steps = lone->budget_steps;
            t->budget_frames = lone->budget_frames;
            t->pcrec_raw = NULL;
            t->defs = defs;
            *out = t;
            *nout = 1;
        }
        return 0;
    }

    RxtTarget *ts = arena_alloc(&src->arena, ntarget * sizeof *ts);
    size_t n = 0;

    for (size_t i = 0; i < src->nrows; i++) {
        RxtRow *tr = &src->rows[i];
        if (tr->kind != RXT_DECL_TARGET) continue;

        /* (3) FROM WHICH BLOCK. A definition name is a block's `name`, in
         * the FILE namespace (DECIDED (7)). W1.2 has no composer and reads
         * no `lib` file, so a name this file does not declare is refused
         * naming the name AND the chain that was searched — the caller can
         * then tell "I misspelled it" from "it lives in a library and this
         * build cannot reach into one yet". */
        const RxtRow *blk = NULL;
        for (size_t k = 0; k < src->nrows; k++) {
            if (src->rows[k].kind != RXT_DECL_PATTERN) continue;
            if (src->rows[k].name && !strcmp(src->rows[k].name, tr->value)) {
                blk = &src->rows[k];
                break;
            }
        }
        /* CONTRACT FIRST, PROSE LAST, AND THAT ORDER IS THE WHOLE POINT.
         * §1.3's table requires this refusal to name the definition AND the
         * `lib` chain searched, and `pcrec_error.msg` is a FIXED 256 bytes
         * that already holds a path and a line number. The first version of
         * this message spent its budget repeating the name three times and
         * on a sentence about [DD-13b.W1.3], and put the chain LAST — so the
         * chain was cut off at EVERY path length tried, including a 20-byte
         * one. It therefore never met the contract it was written for, on
         * any input, and the truncation hid that rather than announcing it.
         * `rxt_fail`'s documented rule is that truncation keeps the file and
         * line, i.e. it eats the TAIL: so whatever the contract requires
         * must come before whatever merely helps. */
        if (!blk)
            return rxt_fail(&p, tr->line,
                            "'target %s' names no definition '%s': no pattern "
                            "block here has that name; searched %s (a lib's "
                            "definitions need the composer, W1.3)",
                            tr->name, tr->value, chain);

        /* (4) UNDER WHICH SETTINGS — the two mechanisms, in order. */
        RxtSet s;
        set_init(&s);
        if (tr->with_list) {
            /* ONE `seen` for the whole `with` list — see cfg_effective. */
            RxtSeen seen = { NULL, 0, 0 };
            const char *cur = tr->with_list;
            RxtItem it;
            while (list_next(&cur, &it)) {
                RxtRow *cr = config_by_name(src, it.s, (size_t)(it.e - it.s));
                if (!cr) continue;       /* parse already refused this */
                RxtSet eff;
                cfg_effective(src, cr, &seen, &eff);
                cfg_merge(&src->arena, &s, &eff);
            }
        }

        RxtTarget *t = &ts[n++];
        memset(t, 0, sizeof *t);
        t->prefix = tr->name;
        /* Frank's §6.3 rule, and the ONE place it is spelled: the block's
         * `name`, or the prefix when the block is unnamed. A target that
         * reaches here always came from a NAMED block (it named one), so
         * the fallback covers the implicit target above and any future
         * caller; either way `name` is never NULL. */
        t->name = blk->name ? blk->name : tr->name;
        t->pattern = blk->value;
        t->line = tr->line;
        t->block_line = blk->line;
        t->pcrec_raw = s.pcrec_raw;
        t->defs = defs;

        /* THE PER-KIND TABLE (§1.5), applied exactly once. */
        t->features_only = blk->features_only;
        if (blk->features_only || !s.features) {
            t->features = blk->features;
        } else if (!blk->features) {
            t->features = s.features;
        } else {
            /* UNION, spelled as the comma-join `--features` already reads.
             * No vocabulary is restated here: a join that is not a legal
             * spec (`all`, `none` and the frozen set names are whole-spec
             * words, not list members) is refused by
             * `pcrec_enabled_set_spec` in its own words, and the CLI adds
             * the one sentence that names the way forward — `features
             * only` on the block. Duplicating that vocabulary here to
             * pre-empt the message would be a second home for it. */
            size_t sz = strlen(s.features) + 1 + strlen(blk->features) + 1;
            char *j = arena_alloc(&src->arena, sz);
            snprintf(j, sz, "%s,%s", s.features, blk->features);
            t->features = j;
        }
        t->flags    = blk->flags    ? blk->flags    : s.flags;
        t->encoding = blk->encoding ? blk->encoding : s.encoding;
        t->engine   = blk->engine   ? blk->engine   : s.engine;
        t->budget_steps  = blk->budget_steps  >= 0 ? blk->budget_steps
                                                   : s.budget_steps;
        t->budget_frames = blk->budget_frames >= 0 ? blk->budget_frames
                                                   : s.budget_frames;
    }

    *out = ts;
    *nout = n;
    return 0;
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
    /* [DD-13b.W1.3] APPENDED, never inserted — `docs/spec/table_contract.md`
     * and this dump's own rule: a consumer's positional read of columns 1-15
     * must survive. */
    "export",
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
        sb_putc(&sb, '\t');
        if (r->exports) sb_puts(&sb, r->exports);               /* 16 export */
        sb_putc(&sb, '\n');
    }
    return sb_take(&sb);
}
