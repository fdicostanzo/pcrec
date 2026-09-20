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

/* ---------------------------------------------- THE STRUCTURE LAYER
 *
 * [DD-13b.W23.1] THE THREE FLAT KEYWORD TABLES ARE GONE. Until this step
 * the format's rules lived HERE, in control flow: `head_vocab`,
 * `config_vocab` and `block_vocab` said which token was legal where, and a
 * chain of `tok_is()` arms below remembered each kind's own cardinality,
 * its own continuation rule and its own idea of what might be indented
 * under it. The ruling (format_design §2.25, Frank's consequence 3) is that
 * those rules are DECLARED and VALIDATED, so the tables are now
 * `src/parse/rxt_schema.def` and this file WALKS them. Nothing here decides
 * what is legal; it decides what a legal line MEANS.
 *
 * THE LAYER A READER WITH NO KEYWORD TABLE SEES (format_design §1.2.1) is
 * four line classes (S0), one attachment rule (S1), one grouping rule (S2)
 * and one opaque-region rule (S3), parameterized by exactly THREE schema
 * columns — the block-opener set, the `value`+`children` prose PAIR, and
 * `children: tree`, the OPEN SUBTREE. Every one of those is a
 * `--list-schema` query, so a generic reader FETCHES the parameters rather
 * than hard-coding them, and this parser reads them from the same table.
 */

typedef enum { LC_BLANK, LC_WS, LC_COMMENT, LC_CONTENT } RxtLineClass;

/* S0 — THE FOUR LINE CLASSES, and the narrow definitions matter:
 *
 *   BLANK is the EMPTY line and nothing else. It closes attachment.
 *   WHITESPACE-ONLY is INERT — no indent is read off it, it attaches to
 *     nothing and nothing attaches to it, no first token is dispatched. A
 *     reader steps over it. (Inside an S3 region it is BYTES like every
 *     other line there, which is what makes it the format's only paragraph
 *     break.) Writing BLANK as "empty or whitespace-only" would have made
 *     every whitespace-only line close attachments and end prose regions,
 *     which all three legs measurably do not do.
 *   A COMMENT is `#` in COLUMN 1. A `#` anywhere else is data. It closes
 *     attachment exactly as a blank does — one rule a reader can remember,
 *     rather than a carve-out.
 *   Everything else is CONTENT, and its INDENT is its count of leading
 *     SPACES. A leading TAB does not open an indent: the caller refuses it
 *     BY NAME (§1.6.1a narrowing (4), TAKEN — a tab inside a VALUE is
 *     still data).
 */
static RxtLineClass line_class(const char *s, size_t *indent)
{
    if (!*s)       { *indent = 0; return LC_BLANK; }
    if (*s == '#') { *indent = 0; return LC_COMMENT; }
    size_t i = 0;
    while (s[i] == ' ') i++;
    *indent = i;
    const char *q = s + i;
    while (*q == ' ' || *q == '\t') q++;
    if (!*q) return LC_WS;
    return LC_CONTENT;
}

/* ONE FRAME PER OPEN ATTACHMENT LEVEL. S1 already required a stack — a
 * reader must know which enclosing level a lesser indent closes back to,
 * which is the one piece of state this layer has always carried — so the
 * OPEN SUBTREE (parameter 3) costs one BIT per frame and no lookahead.
 *
 * `scope` is the scope of the lines AT this level and `base` is what it was
 * before a group opened here: S2 switches a FILE level to BLOCK at the
 * first `pattern`, and the head boundary is exactly that switch, so the two
 * have to be kept apart or a second `pattern` could not re-open a group.
 * `seen` is the cardinality bookkeeping, one entry per schema row holding
 * the line of that kind's first occurrence AT THIS LEVEL IN THIS GROUP —
 * which is why a new group clears it and a new frame allocates a fresh one. */
typedef struct {
    size_t          indent;
    RxtSchemaScope  scope;
    RxtSchemaScope  base;
    /* [DD-13b.W23.3] the scope this frame was opened FROM. It is the one
     * reserved field name a `required-if`/`forbidden-if` condition may
     * name (`parent == block`), which is how ONE `provenance` record
     * serves two parents instead of being two records that rhyme
     * (format_design §2.14, §2.26 item 10). */
    RxtSchemaScope  parent;
    int             tree;     /* inside an OPEN SUBTREE: no dispatch at all */
    RxtRow         *row;      /* the RxtRow this level's lines write into */
    size_t         *seen;
    /* [DD-13b.W23.3] the VALUE of each kind's first occurrence at this
     * level, parallel to `seen`, because a constraint condition names a
     * SIBLING and siblings arrive in any order — `url` may precede the
     * `source authored` that forbids it. So the conditions are evaluated
     * when the frame CLOSES and never at the line, which is also the only
     * point at which `required` can be answered at all. */
    const char    **val;
    /* [DD-13b.W23.3] `unique-by`'s accumulated key tuples for this level,
     * one entry per row that carries the constraint. Not a `seen` column:
     * `seen` answers "has this KIND appeared" and `unique-by` answers "has
     * this KEY appeared", and a kind whose cardinality is `repeat` has as
     * many keys as it has lines. */
    const char    **ukey;
    size_t         *uline;
    size_t          nukey, ukeycap;
    /* [DD-13b.W23.4] TWO USES, kept in one pair of fields rather than four
     * because they never both apply to the same frame. For a PROVENANCE or
     * VARIANT frame: `open_line` is the sub-block's OWN opener line (the
     * `provenance`/`variant <testee>` line itself, which `f->row->line` —
     * the OWNING block's line — cannot give); `open_value` is the opener's
     * own scalar (a variant's `testee`, NULL for `provenance`, which takes
     * none). For a TREE frame (an `ext` body): the same two name the
     * OPENER ROW's identity for `#section aux`'s `parent_line` (§2.24's
     * normative fact (a), "the opener line ... IS the block's identity") —
     * `open_line` doubles as this level's own `parent_line` and
     * `open_value` is unused there (`consumer` below carries the value a
     * tree frame needs instead, since it is inherited by every descendant
     * rather than read once at the opener). */
    size_t          open_line;
    const char     *open_value;
    /* [DD-13b.W23.4] TREE-FRAME-ONLY: the `ext` body's own accounting,
     * meaningless (and unset) when `tree` is false. `depth` is this
     * level's distance from the `ext` opener (1 for the opener's direct
     * children); `consumer` is the `ext <consumer>` token, inherited
     * unchanged by every descendant frame so a nested line needs no walk
     * back to its root to report it. */
    size_t          depth;
    const char     *consumer;
} RxtFrame;

/* ------------------------------------------------------------ the parser */

/* [DD-13b.W23.3] A FILE-DECLARED CLOSED SET (`vocabulary <key> <v…>`,
 * format_design §2.15). It is NOT a second mechanism beside the schema: a
 * `closed` constraint whose selector has no FORMAT-declared members reads
 * its set from here, so "what values may this key take" has one answer from
 * one walk regardless of who declared it. A key with no line here keeps
 * FREE-VOCABULARY behaviour exactly, which is what makes the production
 * purely additive. */
typedef struct RxtVocab {
    const char      *key;
    const char      *members;   /* space-separated, as accumulated */
    size_t           line;
    struct RxtVocab *next;
} RxtVocab;

typedef struct {
    const char *path;
    Arena *arena;
    pcrec_error *err;
    int failed;
    RxtVocab   *vocab;
} RxtP;

/* Every diagnostic from this file goes through here, so every one of them
 * carries the FILE and the LINE. `pcrec_error.pos` is a PATTERN offset
 * everywhere else in the tree and there is no pattern here, so it is left
 * 0 and the location lives in the text — a file:line is what a `.rxt`
 * author can act on, and inventing a byte offset into a file for a field
 * whose every other reader means "offset into the pattern" would be a
 * second meaning for one field. */
/* [DD-13b.W23.1] THE DIAGNOSTIC CLASS — WHICH RULE WAS VIOLATED, as a
 * machine-read TAG beside the D26-free wording.
 *
 * WHY A TAG AND NOT A SENTENCE. The three-leg differential compares legs
 * A, B and C on every refusal, and leg B refuses EVERY unrecognised line
 * by catch-all fall-through with one sentence — so a VERDICT-only
 * comparison reads "all three legs refuse" for a rule leg B has never
 * heard of, and the one live check on the `all-readers` column would be
 * satisfiable by accident on a population of one message. The class is
 * what gives the differential a RULE to compare instead of an exit code.
 *
 * D26 IS UNTOUCHED AND THE BOUNDARY IS EXACT: the class is a tag a CHECK
 * reads, the sentence beside it is for a human, and D26 governs wording.
 * The tag's POSITION is stable and its SET is closed; `docs/spec/cli.md`
 * states both as the CLI's output contract, which is where it belongs —
 * a machine-parseable stderr field is the CLI's promise and not the
 * format's grammar.
 *
 * FOUR CLASSES, and each names a LAYER rather than a symptom:
 *   structure-attachment  S0/S1/S2/S3 — where a line attaches, or may not
 *   unknown-token-in-scope  the kind has no schema row in this scope, or
 *                           has one whose wave is above this build's
 *   schema-constraint     a declared rule over lines: cardinality, a
 *                         closed set, a uniqueness or resolution rule
 *   value-shape           the line attached and is legal here; its VALUE
 *                         does not parse
 */
typedef enum {
    RXTD_STRUCTURE,
    RXTD_UNKNOWN_TOKEN,
    RXTD_SCHEMA_CONSTRAINT,
    RXTD_VALUE_SHAPE
} RxtDiagClass;

static const char *rxt_diag_class_name(RxtDiagClass c)
{
    switch (c) {
        case RXTD_STRUCTURE:          return "structure-attachment";
        case RXTD_UNKNOWN_TOKEN:      return "unknown-token-in-scope";
        case RXTD_SCHEMA_CONSTRAINT:  return "schema-constraint";
        case RXTD_VALUE_SHAPE:        return "value-shape";
    }
    return "?";
}

static int rxt_fail(RxtP *p, RxtDiagClass cls, size_t line,
                    const char *fmt, ...)
    __attribute__((format(printf, 4, 5)));

static int rxt_fail(RxtP *p, RxtDiagClass cls, size_t line,
                    const char *fmt, ...)
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
    /* THE TAG LEADS, which is the whole of "a stable, machine-parseable
     * position": a reader takes the bracketed word at the front and stops
     * caring about the rest, and the file:line an author acts on is still
     * the next thing they see. */
    int n = snprintf(out, cap, "[%s] %s:%zu: ",
                     rxt_diag_class_name(cls), p->path, line);
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
 * rule rather than one this format may widen.
 *
 * **[DD-13b.W23.3, D100] A `-`/`.` DEFINITION IS NOW CALLABLE — THROUGH ITS
 * DERIVED IDENTIFIER, AND THE OLD BOUNDARY IS REPEALED.** This comment
 * used to end "…therefore BUILDABLE as a target and NOT CALLABLE from a
 * pattern", recorded as a feature: a library meant to be composed simply
 * avoided the wide spelling. §2.22 measured that unusable — every id in
 * all five pcrec-bench sets is a hyphenated slug, so the regime-membership
 * mechanism the format owes them had no spelling at all — and D100 accepts
 * the loss of the deliberately-non-callable declaration. `(?&cls_upto_64)`
 * reaches `name cls-upto-64` because `rxt_compose.c`'s lookup maps every
 * definition's name through `pcrec_rxt_prefix_from_name` below and compares
 * THAT; the SPELLING `(?&cls-upto-64)` is still refused, by PCRE2's own
 * grammar, which is the half D26 keeps. Two definitions whose mapped names
 * collide make a call to the shared identifier a refusal naming both — see
 * `rxt_compose.c`'s `def_by_name`, where the rule and its narrowing live.
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
        return rxt_fail(p, RXTD_VALUE_SHAPE, 0, "cannot stat .rxt source file");
    if (!S_ISREG(st.st_mode))
        return rxt_fail(p, RXTD_VALUE_SHAPE, 0,
                        "not a regular file (a directory or special file "
                        "cannot be a .rxt source)");
    FILE *f = fopen(p->path, "rb");
    if (!f)
        return rxt_fail(p, RXTD_VALUE_SHAPE, 0, "cannot open .rxt source file");
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return rxt_fail(p, RXTD_VALUE_SHAPE, 0, "cannot seek .rxt source file"); }
    long sz = ftell(f);
    if (sz < 0) { fclose(f); return rxt_fail(p, RXTD_VALUE_SHAPE, 0, "cannot size .rxt source file"); }
    rewind(f);
    char *buf = arena_alloc(p->arena, (size_t)sz + 2);
    size_t got = fread(buf, 1, (size_t)sz, f);
    if (ferror(f)) { fclose(f); return rxt_fail(p, RXTD_VALUE_SHAPE, 0, "error reading .rxt source file"); }
    fclose(f);
    buf[got] = 0;

    /* [RXTNUL] A NUL BYTE ANYWHERE IN THE FILE IS REFUSED BY NAME, BEFORE
     * THE FILE IS SPLIT INTO LINES. Below this point every production
     * reads a NUL-terminated C string handed out of `v[]`, so without
     * this scan a NUL mid-line silently truncates whatever value it
     * falls inside — `pattern ab<NUL>cd` parsed as `ab`, exit 0, no
     * diagnostic (the bench's own M1 measurement,
     * docs/design/dd13_format/bench_rxt_needs_v1.md §1.9/§2.7, ranked
     * this refusal ABOVE `pattern-esc` itself: "a missing capability is
     * a known limit, a silent truncation is a trap"). The format is
     * line-oriented text and NUL has no representation in any production
     * today — the scan costs one pass over bytes already in hand, and it
     * runs BEFORE the line split rather than being caught line by line,
     * because a per-line strlen() would already have thrown the true
     * length away. A future `pattern-esc` escape production would carry
     * a NUL as a DECODED escape value, never as a raw file byte, so this
     * refusal does not narrow that grammar. */
    for (size_t i = 0; i < got; i++) {
        if (buf[i] != 0) continue;
        size_t line = 1;
        for (size_t j = 0; j < i; j++) if (buf[j] == '\n') line++;
        return rxt_fail(p, RXTD_VALUE_SHAPE, line, "embedded NUL byte in .rxt source file");
    }

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

/* S3 — AN OPAQUE REGION (format_design §1.2.1). Reads the region a
 * prose-region-opening line introduces; `*i` enters at the opener and
 * leaves at the last line of the region, so the caller's loop `++` lands
 * on the first line after it.
 *
 * THE EXTENT IS STRUCTURAL AND IS THE ONLY STRUCTURAL FACT ABOUT THE
 * REGION: it runs from the next line up to, and not including, the FIRST
 * of a CONTENT line whose indent is <= the opener's, a BLANK line, or a
 * COMMENT line. A whitespace-only line ends nothing and is bytes. Every
 * line inside is BYTES — S0 does not classify it for dispatch, S1 does not
 * attach it, S2 does not test it — so a reader can find a region's end
 * without tokenising a single line inside it, which is the falsifiable
 * form of the rule.
 *
 * THE COMMENT AND BLANK BOUNDARIES ARE LOAD-BEARING rather than tidy: the
 * transparent reading (a comment is skipped and the region continues) can
 * produce an opener with TWO DISJOINT prose regions, a shape the
 * single-extent rule cannot express at all.
 *
 * THE DEDENT IS A BYTE COUNT, WHICH IS WHY A SHALLOWER LINE MUST BE
 * REFUSED RATHER THAN SILENTLY STRIPPED (K57, docs/dev/known_issues.md,
 * FIXED). The dedent depth is set by the FIRST continuation line; every
 * later line in the region is stripped by that same byte count, which is
 * only safe when the byte count being removed is entirely whitespace. A
 * CONTENT line whose own leading whitespace run is SHORTER than that
 * depth would have real bytes deleted — the design (format_design.md
 * §1.2.1 S3 / §1.2.5's `prose-value`) states the region's EXTENT but
 * deliberately leaves this decode case to the implementer ("the choice is
 * the implementer's"), and the manager's standing ruling for this shape
 * (a value the decode cannot represent) is REFUSAL BY NAME, class
 * `value-shape` — never silent loss, never silent reinterpretation. A
 * WHITESPACE-ONLY line is exempt: format_design.md §1.2.5's paragraph
 * break decodes to an empty line whatever its own width, and this fix
 * must not narrow that. `prose_dedent.rxtin` used to assert the byte-loss
 * value with K57 named beside it and now asserts this refusal instead. */
static int read_prose_region(RxtP *p, RxtLines *L, size_t *i,
                             size_t opener_indent, const char **out)
{
    size_t start = *i + 1;
    size_t end = start;
    while (end < L->n) {
        size_t ind = 0;
        RxtLineClass c = line_class(L->v[end], &ind);
        if (c == LC_BLANK || c == LC_COMMENT) break;
        if (c == LC_CONTENT && ind <= opener_indent) break;
        end++;                       /* CONTENT deeper than the opener, or WS */
    }
    if (end == start)
        return rxt_fail(p, RXTD_STRUCTURE, *i + 1,
                        "block scalar '|' has no indented continuation lines "
                        "(a '|' value is the indented lines below it)");

    size_t indent = 0;
    while (L->v[start][indent] == ' ' || L->v[start][indent] == '\t') indent++;

    /* K57's fix: any CONTENT line (one with a non-whitespace byte) whose
     * own leading whitespace run is shorter than `indent` cannot be
     * dedented by a byte count without deleting content. Checked as its
     * own pass, before any stripping, so a refused file never even
     * partially decodes. */
    for (size_t k = start; k < end; k++) {
        const char *ln = L->v[k];
        size_t lw = 0;
        while (ln[lw] == ' ' || ln[lw] == '\t') lw++;
        if (!ln[lw]) continue;        /* whitespace-only: the paragraph break */
        if (lw < indent)
            return rxt_fail(p, RXTD_VALUE_SHAPE, k + 1,
                            "block scalar '|' continuation is indented %zu, "
                            "less than the block's own indent %zu set by line "
                            "%zu -- dedenting would delete content",
                            lw, indent, start + 1);
    }

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

/* A PROSE VALUE, and the TRIGGER IS PARAMETERIZED — which is the whole of
 * what makes S3 a declared device rather than a value rule this file
 * remembers. A region opens only when ALL THREE hold: the line's KIND is
 * prose-region-opening (`value: prose` AND `children: prose`, read as a
 * PAIR off the schema), its value with trailing spaces and tabs TRIMMED is
 * exactly the single byte `|`, and it is not inside an OPEN SUBTREE.
 *
 * Without the FIRST condition `pattern |` — a legal pattern, the
 * alternation of two empties — becomes a refusal. Without the SECOND,
 * `description | ` (one trailing space) is a literal where all three legs
 * make it the block form. Without the THIRD, an aux body's `separator |`
 * swallows its own siblings.
 *
 * The one-line form stores the value AS WRITTEN, untrimmed: `description`
 * is a rest-of-line production and its trailing space is data. Only the
 * `|` TEST trims. */
static int prose_value(RxtP *p, RxtLines *L, size_t *i,
                       const RxtSchemaRow *row, size_t indent, int in_tree,
                       const char **out)
{
    /* THE INDENT IS SUBTRACTED FIRST, and it is load-bearing rather than
     * tidy: `tok_len` stops at the first whitespace byte, so on an INDENTED
     * line it measures ZERO and `line_value` hands back the whole line
     * including its kind. Every W1 caller sat at indent 0 and could not
     * see it; a `variant`'s `note |` sits at indent 2 and the region would
     * silently not open, leaving its own continuation to reach S1 as an
     * orphan ([DD-13b.W23.3]). */
    const char *v = line_value(L->v[*i] + indent);
    size_t n = strlen(v);
    while (n && (v[n - 1] == ' ' || v[n - 1] == '\t')) n--;
    if (!in_tree && pcrec_rxt_schema_prose_region(row) && n == 1 && v[0] == '|')
        return read_prose_region(p, L, i, indent, out);
    *out = arena_strdup(p->arena, v);
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
        if (!*v) return rxt_fail(p, RXTD_VALUE_SHAPE, line, "'flags' needs its letters");
        if (strcmp(v, "i") != 0)
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
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
        if (!*v) return rxt_fail(p, RXTD_VALUE_SHAPE, line, "'features' needs a module list");
        for (const char *q = v; *q; q++)
            if (!isalnum((unsigned char)*q) && *q != ',' && *q != '_' &&
                *q != '-')
                return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                                "'features' takes a comma-separated module "
                                "list (got '%s')", v);
        r->features = arena_strdup(p->arena, v);
        return 0;
    }
    if (tok_is(l, "encoding")) {
        if (!ident_ok(v))
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
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
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "unknown 'engine' value '%s' (only vm is "
                            "defined)", v);
        r->engine = arena_strdup(p->arena, v);
        return 0;
    }
    /* [OPT-DIAL] `tune <position>` — the speed-vs-size dial, in the
     * IDENTICAL vocabulary the CLI's `--tune=` takes (D93's own framing:
     * a config block's directives are the format's named axes). Both
     * spellings on equal terms, and the ORDINAL is legal here with no `=`
     * problem to solve — the `=` form is a command-line requirement about
     * argv, not a property of the value.
     *
     * VALIDATED HERE BY THE ONE PARSER (`src/core/tune.c`), never by a
     * second list of five tokens: a token set spelled twice is a token set
     * that will one day be spelled differently. The value is kept AS
     * WRITTEN so `--list-source` reports the author's own spelling. */
    if (tok_is(l, "tune")) {
        int pos = 0;
        if (pcrec_tune_parse(v, &pos) != 0)
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "'tune' wants -2..2 or one of min-size, size, "
                            "balanced, speed, max-speed (got '%s')", v);
        r->tune = arena_strdup(p->arena, v);
        return 0;
    }
    if (tok_is(l, "budget")) {
        long *slot = NULL;
        const char *num = NULL;
        if (!strncmp(v, "steps=", 6))       { slot = &r->budget_steps;  num = v + 6; }
        else if (!strncmp(v, "frames=", 7)) { slot = &r->budget_frames; num = v + 7; }
        else
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
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
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "'budget' wants a non-negative integer with no "
                            "sign or leading space (got '%s')", num);
        errno = 0;
        char *end = NULL;
        long n = strtol(num, &end, 10);
        if (!end || *end || end == num || n < 0 || errno == ERANGE)
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "'budget' wants a non-negative integer (got '%s')",
                            num);
        *slot = n;
        return 0;
    }
    return rxt_fail(p, RXTD_VALUE_SHAPE, line, "internal: '%s' is not a settings line", l);
}

/* WAVE REFUSAL, RE-BASED ON THE SCHEMA'S `wave` COLUMN. The keyword is
 * REAL and in the spec; what it is not is built. Saying "unknown" here
 * sends a reader hunting a typo in a word they just read in the format
 * design — K14's shape, and MEASURED on the pre-W23 binary, where
 * `vocabulary` read "not a file-level directive".
 *
 * The LIST of such keywords is now DERIVED rather than hand-kept: a row
 * whose `wave` exceeds `PCREC_RXT_WAVE_BUILT` refuses here, so a withdrawn
 * production cannot be forgotten in a hand-kept list because there is no
 * hand-kept list. */
static int refuse_wave(RxtP *p, size_t line, const RxtSchemaRow *row,
                       RxtSchemaScope scope)
{
    if (row->wave == PCREC_RXT_WAVE_RESERVED)
        return rxt_fail(p, RXTD_UNKNOWN_TOKEN, line,
                        "'%s' is a RESERVED %s keyword: the format owns the "
                        "word and no build parses it (the keyword is real, "
                        "not a typo)",
                        row->kind, pcrec_rxt_scope_context(scope));
    return rxt_fail(p, RXTD_UNKNOWN_TOKEN, line,
                    "'%s' is a wave-%d %s declaration and is NOT IN THIS "
                    "BUILD (this pcrec implements wave %d of the .rxt format; "
                    "the keyword is real, not a typo)",
                    row->kind, row->wave, pcrec_rxt_scope_context(scope),
                    PCREC_RXT_WAVE_BUILT);
}

static int unknown_token(RxtP *p, size_t line, const char *l,
                         RxtSchemaScope scope)
{
    size_t n = tok_len(l);
    return rxt_fail(p, RXTD_UNKNOWN_TOKEN, line, "'%.*s' is not a %s directive",
                    (int)n, l, pcrec_rxt_scope_context(scope));
}

/* CARDINALITY, ENFORCED GENERICALLY FROM THE COLUMN. Six settings kinds
 * silently LAST-WON on the pre-W23 binary while a seventh in the same
 * family refused, so any value the schema writes is a compatibility
 * decision and writing none was the worst of the three available outcomes
 * (§2.25.2's ruled table; corpus + bench population of every refusal: 0).
 * ONE refusal site, so the six cannot acquire six wordings. */
static int refuse_cardinality(RxtP *p, size_t line, const RxtSchemaRow *row,
                              RxtSchemaScope scope, size_t first)
{
    return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, line, "a %s has one '%s' (already given on line %zu)",
                    pcrec_rxt_scope_noun(scope), row->kind, first);
}

/* ---- [DD-13b.W23.3] THE SCHEMA'S OTHER TWO COLUMNS, ENFORCED ----------
 *
 * W23.1 landed the table and enforced `cardinality` generically from its
 * column; `value` and `constraints` were DECLARED and nothing read them,
 * which the `.def`'s own header said rather than implying otherwise. This
 * is the half that reads them, and it is generic for the same reason the
 * cardinality site is: fourteen productions arrive in one step, and
 * fourteen hand-written refusals would be fourteen wordings for four rules.
 *
 * WHAT IS CHECKED WHERE, and the split is forced rather than chosen:
 *   - `value` at the LINE. A shape is a property of the line's own text.
 *   - `constraints` at the FRAME CLOSE, because every condition names a
 *     SIBLING and siblings arrive in any order — `url` may precede the
 *     `source authored` that forbids it — and because `required` cannot be
 *     answered before the last line of the scope has been read.
 *   - `unique-by` at the LINE, because it is the one constraint whose
 *     subject is a line rather than a scope, and refusing at the SECOND
 *     occurrence is what lets the diagnostic name both.
 */

/* THE VALUE SHAPE, CHECKED GENERICALLY AND HONESTLY.
 *
 * It asserts what is UNIFORM across every row carrying a shape and nothing
 * more: `none` takes no value, `int` takes digits, every other shape takes
 * a non-empty value — except `prose`, whose empty form is legal and shipped
 * (a block `description` with a trailing space and no text, the r46
 * finding-13 cell). The PRECISE grammar of a `token`, a `list` or a
 * `qualified-line` stays with the production that owns it, and that is a
 * boundary rather than a shortcut: `lib "a path"` is a `token` row whose
 * value carries a space, so a generic no-whitespace test would refuse a
 * shipped spelling. A check that over-claims is worse here than one that
 * under-claims, because `--list-schema` publishes the column and a reader
 * would act on it. */
static int check_value_shape(RxtP *p, const RxtSchemaRow *row, size_t line,
                             const char *v)
{
    switch (row->value) {
        case RXT_VAL_NONE:
            if (*v)
                return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                                "'%s' takes no value (got '%s')", row->kind, v);
            return 0;
        case RXT_VAL_INT:
            if (!*v || !isdigit((unsigned char)*v))
                return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                                "'%s' wants a non-negative integer (got '%s')",
                                row->kind, v);
            for (const char *q = v; *q; q++)
                if (!isdigit((unsigned char)*q))
                    return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                                    "'%s' wants a non-negative integer (got "
                                    "'%s')", row->kind, v);
            return 0;
        case RXT_VAL_PROSE:
        case RXT_VAL_RAW:
        case RXT_VAL_CASE:
            return 0;
        case RXT_VAL_TOKEN:
        case RXT_VAL_LINE:
        case RXT_VAL_LIST:
        case RXT_VAL_PAIR:
        case RXT_VAL_SUBJECT:
        case RXT_VAL_QUALIFIED:
            if (!*v)
                return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                                "'%s' needs a value (its shape is '%s')",
                                row->kind, pcrec_rxt_value_name(row->value));
            return 0;
    }
    return 0;
}

/* Is `needle` (length `nlen`) one of `set`'s space-separated words? */
static int word_in_set(const char *set, const char *needle, size_t nlen)
{
    const char *s = set;
    while (*s) {
        while (*s == ' ') s++;
        const char *w = s;
        while (*s && *s != ' ') s++;
        if ((size_t)(s - w) == nlen && !strncmp(w, needle, nlen)) return 1;
    }
    return 0;
}

static const RxtVocab *vocab_lookup(const RxtP *p, const char *key, size_t klen)
{
    for (const RxtVocab *v = p->vocab; v; v = v->next)
        if (strlen(v->key) == klen && !strncmp(v->key, key, klen)) return v;
    return NULL;
}

/* `closed`'s membership test for ONE (selector, value) pair. The FORMAT
 * members come from the clause's own remaining words; with none, the set is
 * whatever a `vocabulary <selector>` line declared, and with no such line
 * the key is FREE — §2.15's compatibility rule, which is what keeps this
 * production purely additive. */
static int closed_check(RxtP *p, size_t line, const char *kind,
                        const char *sel, size_t sellen,
                        const char *fmt_members,
                        const char *val, size_t vlen)
{
    if (*fmt_members) {
        if (word_in_set(fmt_members, val, vlen)) return 0;
        return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, line,
                        "'%s' value '%.*s' is not in the closed set for "
                        "'%.*s' (declared here: %s)",
                        kind, (int)vlen, val, (int)sellen, sel, fmt_members);
    }
    const RxtVocab *vo = vocab_lookup(p, sel, sellen);
    if (!vo) return 0;            /* free vocabulary — §2.15's own rule */
    if (word_in_set(vo->members, val, vlen)) return 0;
    return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, line,
                    "'%s' value '%.*s' is not in the '%.*s' vocabulary "
                    "declared on line %zu (%s)",
                    kind, (int)vlen, val, (int)sellen, sel, vo->line,
                    vo->members);
}

/* `closed` over a whole row's value, in the two forms the `.def` header
 * declares: a per-ROW selector, and `per-key` for a LIST of `key=value`
 * items whose OWN key selects the set. A `qualified-line`'s value is
 * checked at its QUALIFIER, because a qualified line's first component is
 * what the shape exists to name. */
static int closed_apply(RxtP *p, const RxtSchemaRow *row, size_t line,
                        const char *arg, size_t arglen, const char *v)
{
    const char *sel = arg;
    size_t sellen = 0;
    while (sellen < arglen && arg[sellen] != ' ') sellen++;
    const char *members = arg + sellen;
    while (*members == ' ' && (size_t)(members - arg) < arglen) members++;
    size_t mlen = arglen - (size_t)(members - arg);
    char mbuf[128];
    if (mlen >= sizeof mbuf) mlen = sizeof mbuf - 1;
    memcpy(mbuf, members, mlen);
    mbuf[mlen] = 0;

    if (sellen == 7 && !strncmp(sel, "per-key", 7)) {
        /* each `key=value` item carries its own set */
        const char *q = v;
        while (*q) {
            while (*q == ' ' || *q == ',' || *q == '\t') q++;
            if (!*q) break;
            const char *item = q;
            while (*q && *q != ' ' && *q != ',' && *q != '\t') q++;
            const char *eq = memchr(item, '=', (size_t)(q - item));
            if (!eq) continue;    /* a BARE label is keyless, never checked */
            if (closed_check(p, line, row->kind, item, (size_t)(eq - item),
                             "", eq + 1, (size_t)(q - eq - 1)) != 0)
                return -1;
        }
        return 0;
    }

    const char *val = v;
    size_t vlen = strlen(v);
    if (row->value == RXT_VAL_QUALIFIED) {
        /* A qualified line's QUALIFIER is its first token, space-
         * delimited — `under <convention> <case-line>`, §2.17's own
         * production. There is no colon in the spelling; the first
         * version of this read stopped at one and would have taken a
         * colon inside a SUBJECT as the qualifier's end. */
        vlen = 0;
        while (val[vlen] && val[vlen] != ' ' && val[vlen] != '\t') vlen++;
    }
    return closed_check(p, line, row->kind, sel, sellen, mbuf, val, vlen);
}

/* `under`'s KEY TUPLE — the ONE named parser-code exception §2.25.3
 * records, and its reason is that three of the four components
 * (convention, subject, kind, startpos) live INSIDE the value rather than
 * on lines of their own. `value: qualified-line` already means this parser
 * decomposes the value, so the components are in hand at the site that has
 * them; a declared extractor would be a second description of a
 * decomposition performed anyway. A SECOND `qualified-line` production with
 * a different key is D77's trigger to make it declarative.
 *
 * The tuple is rendered as ONE string with a separator no component can
 * contain, so the comparison is a `strcmp` and the refusal can print it. */
static const char *under_key(Arena *a, const char *v)
{
    /* `under <convention> <case-line>` — SPACE-SEPARATED, no colon
     * (format_design §2.17's own production, and the spelling both
     * harness legs implement: leg B's arm has no colon and leg C REFUSES
     * the colon form by name). The first token is the qualifier and the
     * rest of the line is an UNCHANGED `m`/`n`/`ms`/`ns`/`mc` line.
     *
     * The first version of this function read the convention with
     * `strchr(v, ':')`, which on the real spelling found no colon, left
     * the convention EMPTY and slid the whole tuple one component left —
     * so two `under` lines differing only in SUBJECT or in STARTPOS were
     * refused as duplicates while the refusing fixture still went red for
     * an unrelated reason. Found by the spec lane MEASURING the
     * production against all three legs rather than reading it.
     *
     * The tuple takes the convention, the case kind, the startpos when
     * written, and the quoted subject; everything after the subject is
     * the EXPECTATION, which is the thing two `under` lines are allowed
     * to disagree about only by being two different keys. */
    const char *conv = v;
    size_t convlen = 0;
    while (conv[convlen] && conv[convlen] != ' ' && conv[convlen] != '\t')
        convlen++;
    const char *rest = skip_ws(conv + convlen);

    const char *kind = rest;
    size_t kindlen = 0;
    while (kind[kindlen] && kind[kindlen] != ' ' && kind[kindlen] != '\t')
        kindlen++;
    const char *q = skip_ws(kind + kindlen);
    const char *sp = q;
    size_t splen = 0;
    while (isdigit((unsigned char)sp[splen])) splen++;
    if (splen) q = skip_ws(sp + splen);
    const char *subj = q;
    size_t subjlen = 0;
    if (*subj == '"') {
        subjlen = 1;
        while (subj[subjlen]) {
            if (subj[subjlen] == '\\' && subj[subjlen + 1]) { subjlen += 2; continue; }
            if (subj[subjlen] == '"') { subjlen++; break; }
            subjlen++;
        }
    } else {
        while (subj[subjlen] && subj[subjlen] != ' ' && subj[subjlen] != '\t')
            subjlen++;
    }

    size_t n = convlen + kindlen + splen + subjlen + 8;
    char *out = arena_alloc(a, n);
    snprintf(out, n, "%.*s\x01%.*s\x01%.*s\x01%.*s",
             (int)convlen, conv, (int)kindlen, kind,
             (int)splen, sp, (int)subjlen, subj);
    return out;
}

/* ---- the condition grammar `<field> <op> [value]` ---------------------
 *
 * ONE reader for `required-if` and `forbidden-if`, because they share the
 * grammar and differ only in which OUTCOME the condition governs — which is
 * exactly why they are two kinds and not one kind with a negated operator
 * (§2.25.3). `parent` is the one reserved field name; every other field
 * names a SIBLING ROW in this scope. */
static int cond_holds(const RxtFrame *f, const RxtSchemaRow *rowbase,
                      size_t nrows, const char *arg, size_t arglen)
{
    const char *fld = arg;
    size_t fldlen = 0;
    while (fldlen < arglen && fld[fldlen] != ' ') fldlen++;
    const char *op = fld + fldlen;
    while ((size_t)(op - arg) < arglen && *op == ' ') op++;
    size_t oplen = 0;
    while ((size_t)(op - arg) + oplen < arglen && op[oplen] != ' ') oplen++;
    const char *want = op + oplen;
    while ((size_t)(want - arg) < arglen && *want == ' ') want++;
    size_t wantlen = arglen - (size_t)(want - arg);

    const char *have = NULL;
    if (fldlen == 6 && !strncmp(fld, "parent", 6)) {
        have = pcrec_rxt_scope_name(f->parent);
    } else {
        for (size_t i = 0; i < nrows; i++) {
            if (rowbase[i].scope != f->scope) continue;
            if (strlen(rowbase[i].kind) != fldlen ||
                strncmp(rowbase[i].kind, fld, fldlen)) continue;
            if (f->seen[i]) have = f->val[i] ? f->val[i] : "";
            break;
        }
    }

    if (oplen == 7 && !strncmp(op, "present", 7)) return have != NULL;
    if (!have) return 0;          /* an absent field satisfies no comparison */
    int eq = strlen(have) == wantlen && !strncmp(have, want, wantlen);
    if (oplen == 2 && !strncmp(op, "==", 2)) return eq;
    if (oplen == 2 && !strncmp(op, "!=", 2)) return !eq;
    return 0;
}

/* EVERY CONSTRAINT THAT RANGES OVER A SCOPE, EVALUATED WHEN THE SCOPE
 * CLOSES. `close_line` is the line that closed it (or the last line of the
 * file), which is where a MISSING-line refusal has to point: there is no
 * offending line to blame, so it blames the record. */
static int frame_constraints(RxtP *p, const RxtFrame *f,
                             const RxtSchemaRow *rowbase, size_t nrows,
                             size_t close_line)
{
    for (size_t i = 0; i < nrows; i++) {
        const RxtSchemaRow *row = &rowbase[i];
        if (row->scope != f->scope || !*row->constraints) continue;
        const char *cur = row->constraints;
        RxtConstraintKind k;
        const char *arg;
        size_t arglen;
        int rc;
        while ((rc = pcrec_rxt_constraint_next(&cur, &k, &arg, &arglen)) != 0) {
            if (rc < 0)
                return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, close_line,
                                "internal: '%s' carries a constraint clause "
                                "naming no known kind", row->kind);
            switch (k) {
                case RXT_C_REQUIRED:
                    if (!f->seen[i])
                        return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, close_line,
                                        "a %s needs a '%s' line",
                                        pcrec_rxt_scope_noun(f->scope),
                                        row->kind);
                    break;
                case RXT_C_REQUIRED_IF:
                    if (!f->seen[i] && cond_holds(f, rowbase, nrows, arg, arglen))
                        return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, close_line,
                                        "a %s must carry '%s' when %.*s",
                                        pcrec_rxt_scope_noun(f->scope),
                                        row->kind, (int)arglen, arg);
                    break;
                case RXT_C_FORBIDDEN_IF:
                    if (f->seen[i] && cond_holds(f, rowbase, nrows, arg, arglen))
                        return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, f->seen[i],
                                        "a %s may not carry '%s' when %.*s",
                                        pcrec_rxt_scope_noun(f->scope),
                                        row->kind, (int)arglen, arg);
                    break;
                case RXT_C_EXACTLY_ONE_OF: {
                    /* Evaluated ONCE per clause and not once per member row:
                     * every member carries the same clause, so counting from
                     * the clause's own word list keeps one answer. */
                    size_t have = 0, first = 0;
                    const char *s = arg;
                    while ((size_t)(s - arg) < arglen) {
                        while ((size_t)(s - arg) < arglen && *s == ' ') s++;
                        const char *w = s;
                        while ((size_t)(s - arg) < arglen && *s != ' ') s++;
                        size_t wlen = (size_t)(s - w);
                        if (!wlen) break;
                        for (size_t j = 0; j < nrows; j++) {
                            if (rowbase[j].scope != f->scope) continue;
                            if (strlen(rowbase[j].kind) != wlen ||
                                strncmp(rowbase[j].kind, w, wlen)) continue;
                            if (f->seen[j]) { have++; if (!first) first = j + 1; }
                            break;
                        }
                    }
                    if (i + 1 != first && have) break;   /* one report only */
                    if (have != 1)
                        return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, close_line,
                                        "a %s needs exactly one of %.*s (it "
                                        "has %zu)",
                                        pcrec_rxt_scope_noun(f->scope),
                                        (int)arglen, arg, have);
                    break;
                }
                case RXT_C_CLOSED:
                case RXT_C_UNIQUE_BY:
                case RXT_C_FUNCTIONAL_BINDING:
                case RXT_C_NKINDS:
                    break;        /* per-LINE constraints; see line_constraints */
            }
        }
    }
    return 0;
}

/* The two constraints whose subject is a LINE. `closed` could be evaluated
 * at the close with the others and deliberately is not: its refusal names an
 * offending VALUE, and a value has a line. */
static int line_constraints(RxtP *p, RxtFrame *f, const RxtSchemaRow *row,
                            size_t line, const char *v)
{
    const char *cur = row->constraints;
    RxtConstraintKind k;
    const char *arg;
    size_t arglen;
    int rc;
    while ((rc = pcrec_rxt_constraint_next(&cur, &k, &arg, &arglen)) != 0) {
        if (rc < 0)
            return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, line,
                            "internal: '%s' carries a constraint clause "
                            "naming no known kind", row->kind);
        if (k == RXT_C_CLOSED) {
            if (closed_apply(p, row, line, arg, arglen, v) != 0) return -1;
            continue;
        }
        if (k != RXT_C_UNIQUE_BY) continue;

        const char *key;
        if (arglen == 9 && !strncmp(arg, "under-key", 9)) {
            key = under_key(p->arena, v);
        } else if (arglen == 10 && !strncmp(arg, "first-word", 10)) {
            size_t n = 0;
            while (v[n] && v[n] != ' ' && v[n] != '\t') n++;
            key = arena_strndup(p->arena, v, n);
        } else {
            key = v;              /* `value` — the whole trimmed value */
        }
        /* The stored key is PREFIXED with the row's own kind, so two rows
         * carrying `unique-by` in one scope cannot collide with each
         * other's keys — a uniqueness rule is per row, not per scope. */
        size_t need = strlen(row->kind) + 1 + strlen(key) + 1;
        char *full = arena_alloc(p->arena, need);
        snprintf(full, need, "%s\x01%s", row->kind, key);

        for (size_t i = 0; i < f->nukey; i++)
            if (!strcmp(f->ukey[i], full))
                return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, line,
                                "duplicate '%s': its %.*s repeats one already "
                                "given on line %zu", row->kind,
                                (int)arglen, arg, f->uline[i]);
        if (f->nukey == f->ukeycap) {
            size_t nc = f->ukeycap ? f->ukeycap * 2 : 8;
            const char **nk = arena_alloc(p->arena, nc * sizeof *nk);
            size_t *nl = arena_alloc(p->arena, nc * sizeof *nl);
            if (f->nukey) {
                memcpy(nk, f->ukey, f->nukey * sizeof *nk);
                memcpy(nl, f->uline, f->nukey * sizeof *nl);
            }
            f->ukey = nk; f->uline = nl; f->ukeycap = nc;
        }
        f->ukey[f->nukey] = full;
        f->uline[f->nukey] = line;
        f->nukey++;
    }
    return 0;
}

/* ---- [DD-13b.W23.4] the four `#section` record pushes -----------------
 *
 * Each mirrors `row_push`'s own growable-array shape exactly (arena-owned,
 * doubling capacity), so there is one pattern for "a section array that
 * grows" rather than four independently-invented ones. */

static RxtProv *prov_push(Arena *a, RxtSource *src)
{
    if (src->nprovs == src->provcap) {
        size_t cap = src->provcap ? src->provcap * 2 : 8;
        RxtProv *nv = arena_alloc(a, cap * sizeof *nv);
        if (src->nprovs) memcpy(nv, src->provs, src->nprovs * sizeof *nv);
        src->provs = nv;
        src->provcap = cap;
    }
    RxtProv *r = &src->provs[src->nprovs++];
    memset(r, 0, sizeof *r);
    return r;
}

static RxtVariant *variant_push(Arena *a, RxtSource *src)
{
    if (src->nvariants == src->variantcap) {
        size_t cap = src->variantcap ? src->variantcap * 2 : 8;
        RxtVariant *nv = arena_alloc(a, cap * sizeof *nv);
        if (src->nvariants) memcpy(nv, src->variants, src->nvariants * sizeof *nv);
        src->variants = nv;
        src->variantcap = cap;
    }
    RxtVariant *r = &src->variants[src->nvariants++];
    memset(r, 0, sizeof *r);
    return r;
}

static RxtCase *case_push(Arena *a, RxtSource *src)
{
    if (src->ncases == src->casecap) {
        size_t cap = src->casecap ? src->casecap * 2 : 32;
        RxtCase *nv = arena_alloc(a, cap * sizeof *nv);
        if (src->ncases) memcpy(nv, src->cases, src->ncases * sizeof *nv);
        src->cases = nv;
        src->casecap = cap;
    }
    RxtCase *r = &src->cases[src->ncases++];
    memset(r, 0, sizeof *r);
    return r;
}

static RxtAux *aux_push(Arena *a, RxtSource *src)
{
    if (src->nauxes == src->auxcap) {
        size_t cap = src->auxcap ? src->auxcap * 2 : 16;
        RxtAux *nv = arena_alloc(a, cap * sizeof *nv);
        if (src->nauxes) memcpy(nv, src->auxes, src->nauxes * sizeof *nv);
        src->auxes = nv;
        src->auxcap = cap;
    }
    RxtAux *r = &src->auxes[src->nauxes++];
    memset(r, 0, sizeof *r);
    return r;
}

/* [DD-13b.W23.4] reads a PROVENANCE or VARIANT frame's own value for
 * `name`, the same (scope, kind-name) match `cond_holds` above already
 * does for a constraint's own field reference — one lookup shape, two
 * customers, so the two cannot read a field differently. Returns NULL for
 * a field never seen; `f->val[i]` itself is never NULL once `f->seen[i]`
 * is set (empty string is the "seen but blank" case, PROSE's own empty
 * form). */
static const char *frame_field(const RxtFrame *f, const RxtSchemaRow *rowbase,
                               size_t nrows, const char *name)
{
    size_t nlen = strlen(name);
    for (size_t i = 0; i < nrows; i++) {
        if (rowbase[i].scope != f->scope) continue;
        if (strlen(rowbase[i].kind) != nlen || strncmp(rowbase[i].kind, name, nlen))
            continue;
        return f->seen[i] ? (f->val[i] ? f->val[i] : "") : NULL;
    }
    return NULL;
}

/* [DD-13b.W23.4] a closing PROVENANCE or VARIANT frame becomes ONE
 * `#section` row — called from `RXT_CLOSE_FRAME` after `frame_constraints`
 * has already passed, so a record missing a `required` field never reaches
 * here at all. A no-op for every other scope (CONFIG/DATA/FILE frames close
 * through the same macro and carry nothing to report). */
static void close_section_frame(Arena *a, RxtSource *src,
                                const RxtSchemaRow *rowbase, size_t nrows,
                                const RxtFrame *f)
{
    if (f->scope == RXT_SCOPE_PROVENANCE) {
        RxtProv *r = prov_push(a, src);
        r->line = f->open_line;
        r->block_line = f->row ? f->row->line : 0;
        r->block_name = f->row ? f->row->name : NULL;
        r->source        = frame_field(f, rowbase, nrows, "source");
        r->url           = frame_field(f, rowbase, nrows, "url");
        r->ref           = frame_field(f, rowbase, nrows, "ref");
        r->retrieved     = frame_field(f, rowbase, nrows, "retrieved");
        r->license       = frame_field(f, rowbase, nrows, "license");
        r->license_note  = frame_field(f, rowbase, nrows, "license-note");
        r->fidelity      = frame_field(f, rowbase, nrows, "fidelity");
        r->adaptation    = frame_field(f, rowbase, nrows, "adaptation");
        r->attribution   = frame_field(f, rowbase, nrows, "attribution");
        r->bytes         = frame_field(f, rowbase, nrows, "bytes");
        r->sha256        = frame_field(f, rowbase, nrows, "sha256");
    } else if (f->scope == RXT_SCOPE_VARIANT) {
        RxtVariant *r = variant_push(a, src);
        r->line = f->open_line;
        r->block_line = f->row ? f->row->line : 0;
        r->block_name = f->row ? f->row->name : NULL;
        r->testee = f->open_value;
        r->kind        = frame_field(f, rowbase, nrows, "kind");
        r->text        = frame_field(f, rowbase, nrows, "text");
        r->groups      = frame_field(f, rowbase, nrows, "groups");
        r->note        = frame_field(f, rowbase, nrows, "note");
        r->unsupported = frame_field(f, rowbase, nrows, "unsupported");
    }
}

/* [DD-13b.W23.4] is `kind` one of the eight real CASE-kind spellings? An
 * `under` line's wrapped case-line is free text until this says so — the
 * schema has already routed us here on the OUTER `under` row alone, so
 * nothing has checked that its tail actually names a real kind. */
static int is_case_kind(const char *kind)
{
    static const char *const k[] = {
        "m", "n", "ms", "ns", "mc", "gu", "g", "gp"
    };
    for (size_t i = 0; i < sizeof k / sizeof *k; i++)
        if (!strcmp(kind, k[i])) return 1;
    return 0;
}

/* [DD-13b.W23.4] parses a CASE-kind line's BODY (everything after the kind
 * word) into `c`. Best-effort and STRUCTURAL only — see `RxtCase`'s own
 * comment: a shape this does not recognise leaves the corresponding field
 * NULL rather than raising anything. `rest` points at (or past) the
 * separating whitespace right after the kind word. */
static void parse_case_body(const char *rest, const char *kind, RxtCase *c,
                            Arena *a)
{
    const char *s = skip_ws(rest);

    /* `ms`/`ns` carry an explicit startpos BEFORE the subject; `m`/`n`/`mc`/
     * `gu` are all "search from byte offset 0" (rxt_format.md's own words
     * for each), so their startpos is the implicit constant. `g`/`gp` have
     * no startpos of their own — see the field's comment in internal.h. */
    if (!strcmp(kind, "ms") || !strcmp(kind, "ns")) {
        const char *w = s;
        while (isdigit((unsigned char)*s)) s++;
        if (s > w) c->startpos = arena_strndup(a, w, (size_t)(s - w));
        s = skip_ws(s);
    } else if (!strcmp(kind, "m") || !strcmp(kind, "n") || !strcmp(kind, "mc") ||
              !strcmp(kind, "gu")) {
        c->startpos = "0";
    }

    /* `gu`'s own code word precedes ITS subject; every other subject-
     * bearing kind's subject comes first (there is nothing before it). */
    if (!strcmp(kind, "gu")) {
        const char *w = s;
        while (*s && !isspace((unsigned char)*s)) s++;
        if (s > w) c->giveup = arena_strndup(a, w, (size_t)(s - w));
        s = skip_ws(s);
    }

    /* `g`/`gp` carry NO subject at all — they attach to a preceding `m`/
     * `ms` case and read a `<slot>` in the subject's place, below. */
    int has_subject = strcmp(kind, "g") && strcmp(kind, "gp");
    if (has_subject) {
        if (*s == '@') {
            /* `@file:"path"` — the ONE spelling `docs/spec/rxt_format.md`'s
             * "Named subjects" section defines; anything else past '@' is
             * left unrecognised (subject/subject_form stay NULL) rather
             * than guessed at. */
            static const char pfx[] = "@file:";
            size_t plen = sizeof pfx - 1;
            if (!strncmp(s, pfx, plen) && s[plen] == '"') {
                c->subject_form = "file";
                const char *q = s + plen + 1;
                const char *qs = q;
                while (*q && *q != '"') { if (*q == '\\' && q[1]) q++; q++; }
                c->subject = arena_strndup(a, qs, (size_t)(q - qs));
                s = *q ? q + 1 : q;
            } else {
                while (*s && !isspace((unsigned char)*s)) s++;
            }
        } else if (*s == '"') {
            /* the quoted text, INCLUDING its quotes, AS WRITTEN — `lib`'s
             * own "recorded, never decoded" convention one production
             * over: the escapes inside are the format's, not a second
             * vocabulary this parser must understand to report the field. */
            c->subject_form = "inline";
            const char *qs = s;
            const char *q = s + 1;
            while (*q && *q != '"') { if (*q == '\\' && q[1]) q++; q++; }
            if (*q == '"') q++;
            c->subject = arena_strndup(a, qs, (size_t)(q - qs));
            s = q;
        }
        s = skip_ws(s);
        /* `[as <id>] [sha256 <hex64>]`, independently optional, `as`
         * before `sha256` when both are written. */
        if (!strncmp(s, "as", 2) && isspace((unsigned char)s[2])) {
            s = skip_ws(s + 2);
            const char *w = s;
            while (*s && !isspace((unsigned char)*s)) s++;
            c->subject_id = arena_strndup(a, w, (size_t)(s - w));
            s = skip_ws(s);
        }
        if (!strncmp(s, "sha256", 6) &&
            (isspace((unsigned char)s[6]) || !s[6])) {
            s = skip_ws(s + 6);
            const char *w = s;
            while (*s && !isspace((unsigned char)*s)) s++;
            c->sha256 = arena_strndup(a, w, (size_t)(s - w));
            s = skip_ws(s);
        }
    }

    /* the KIND-SPECIFIC TAIL. */
    if (!strcmp(kind, "m") || !strcmp(kind, "ms")) {
        const char *w = s;
        while (isdigit((unsigned char)*s)) s++;
        if (s > w) c->start = arena_strndup(a, w, (size_t)(s - w));
        s = skip_ws(s);
        w = s;
        while (isdigit((unsigned char)*s)) s++;
        if (s > w) c->end = arena_strndup(a, w, (size_t)(s - w));
    } else if (!strcmp(kind, "mc")) {
        const char *w = s;
        while (isdigit((unsigned char)*s)) s++;
        if (s > w) c->count = arena_strndup(a, w, (size_t)(s - w));
    } else if (!strcmp(kind, "g") || !strcmp(kind, "gp")) {
        const char *w = s;
        while (isdigit((unsigned char)*s)) s++;
        if (s > w) c->slot = arena_strndup(a, w, (size_t)(s - w));
        s = skip_ws(s);
        w = s;
        if (*s == '-') s++;
        while (isdigit((unsigned char)*s)) s++;
        if (s > w) c->start = arena_strndup(a, w, (size_t)(s - w));
        s = skip_ws(s);
        w = s;
        if (*s == '-') s++;
        while (isdigit((unsigned char)*s)) s++;
        if (s > w) c->end = arena_strndup(a, w, (size_t)(s - w));
    }
    /* `n`/`ns`/`gu` have no further tail. */
}

/* ---- [DD-13b.W23.3] a WRAPPED one-line value (`children: prose` on a row
 * whose own `value` is NOT prose) ---------------------------------------
 *
 * S1's attachment says the indented lines under such a row ARE that line's
 * value; S3's `|` region is the form that applies when the value shape is
 * PROSE too. `vocabulary` is the one row in this build where the two differ
 * — a long closed set wraps (§2.15) — so the join is a SPACE and each
 * continuation line is trimmed, because the value is a LIST of words and a
 * newline inside one would make a member nobody can write.
 *
 * The EXTENT is `read_prose_region`'s, deliberately shared rather than
 * re-derived: two spellings of "where does a continuation end" is exactly
 * the drift S3 was declared to remove. */
static int read_wrapped_value(RxtP *p, RxtLines *L, size_t *i,
                              size_t opener_indent, const char *first,
                              const char **out)
{
    size_t end = *i + 1;
    while (end < L->n) {
        size_t ind = 0;
        RxtLineClass c = line_class(L->v[end], &ind);
        if (c == LC_BLANK || c == LC_COMMENT) break;
        if (c == LC_CONTENT && ind <= opener_indent) break;
        end++;
    }
    if (end == *i + 1) { *out = first; return 0; }

    size_t total = strlen(first) + 1;
    for (size_t k = *i + 1; k < end; k++) total += strlen(L->v[k]) + 1;
    char *buf = arena_alloc(p->arena, total + 1);
    size_t at = strlen(first);
    memcpy(buf, first, at);
    for (size_t k = *i + 1; k < end; k++) {
        const char *ln = skip_ws(L->v[k]);
        size_t len = strlen(ln);
        while (len && (ln[len - 1] == ' ' || ln[len - 1] == '\t')) len--;
        if (!len) continue;
        buf[at++] = ' ';
        memcpy(buf + at, ln, len);
        at += len;
    }
    buf[at] = 0;
    *out = buf;
    *i = end - 1;                     /* caller's loop does the ++ */
    return 0;
}

/* `oracle <engine-ref>[/<version>]` (§2.9, widened at W23 from a bare
 * engine name). pcrec KNOWS no oracles, so this validates the SHAPE and
 * resolves nothing: an engine ref is an identifier and a version is a
 * dotted/hyphenated run after a single `/`. Naming an oracle pcrec cannot
 * reach is a labelled skip in the harness, never a refusal here. */
static int oracle_ref_ok(RxtP *p, size_t line, const char *v)
{
    /* `oracle none <reason>` is the SECOND spelling (§2.9), and it is not
     * an engine-ref at all: it declares a counted, PRINTED skip and
     * carries the reason as rest-of-line prose. R-RXT-7's obligation
     * rides it (an exclusion still owes an upstream_issues entry), which
     * is why the reason is required rather than optional — a skip with
     * no stated reason is the silent pass the production exists to
     * replace. */
    if (!strncmp(v, "none", 4) && (v[4] == ' ' || v[4] == '\t')) {
        if (!*skip_ws(v + 4))
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "'oracle none' needs a reason (the skip is "
                            "counted and PRINTED, and an exclusion owes an "
                            "upstream_issues.md entry)");
        return 0;
    }
    if (!strcmp(v, "none"))
        return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                        "'oracle none' needs a reason after it");
    const char *slash = strchr(v, '/');
    /* THE ENGINE HALF IS A `defname`, NOT AN `ident`, for the reason
     * `variant`'s testee name is: real engine names are hyphenated slugs
     * (`pcre2-dfa`, `pcre2-interp`), and a grammar that admits a testee
     * called `pcre2-dfa` while refusing an ORACLE called `pcre2-dfa`
     * would be two answers to one question. pcrec resolves neither. */
    size_t nlen = slash ? (size_t)(slash - v) : strlen(v);
    char *nm = arena_strndup(p->arena, v, nlen);
    if (!defname_ok(nm))
        return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                        "'oracle' wants an engine reference, optionally "
                        "'/<version>' (got '%s')", v);
    if (!slash) return 0;
    if (!slash[1])
        return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                        "'oracle %s' has a '/' with no version after it", v);
    for (const char *q = slash + 1; *q; q++)
        if (!isalnum((unsigned char)*q) && *q != '.' && *q != '-' && *q != '_')
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "'oracle' version '%s' wants letters, digits, "
                            "'.', '-' or '_'", slash + 1);
    return 0;
}

/* A `tag` LIST: each item is a BARE LABEL or a `key=value` with NO
 * WHITESPACE in either half (§2.15, and r58 R3 which REMOVED the quoted
 * `tag-prose` alternative — a tag value is one word, and a sentence lives
 * in `variant note` where its own production is). A bare label is KEYLESS
 * and therefore never vocabulary-checked; `closed per-key` above says so by
 * skipping items with no `=`. */
static int tag_list_ok(RxtP *p, size_t line, const char *v)
{
    const char *q = v;
    size_t nitem = 0;
    while (*q) {
        while (*q == ' ' || *q == '\t' || *q == ',') q++;
        if (!*q) break;
        const char *item = q;
        while (*q && *q != ' ' && *q != '\t' && *q != ',') q++;
        size_t len = (size_t)(q - item);
        const char *eq = memchr(item, '=', len);
        size_t klen = eq ? (size_t)(eq - item) : len;
        if (!ident_ok_n(item, klen))
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "'tag' item '%.*s' is not a label or "
                            "key=value (a key is a letter or '_' then "
                            "letters, digits or '_')", (int)len, item);
        if (eq && eq + 1 == item + len)
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "'tag' item '%.*s' has a '=' with no value",
                            (int)len, item);
        nitem++;
    }
    if (!nitem)
        return rxt_fail(p, RXTD_VALUE_SHAPE, line, "'tag' needs at least one "
                        "label or key=value item");
    return 0;
}

/* ---- [DD-13b.W23.3] `pattern-esc`'s DECODER, and it is pcrec's ONCE ----
 *
 * The format's OWN subject escape vocabulary and no second vocabulary
 * (format_design §2.19; `docs/spec/rxt_format.md`'s escape table). The
 * `--pattern-esc` CLI flag routes an operand through THIS function, so the
 * CLI, `--source` and `--list-source` decode identically by construction
 * rather than by three tables that agree today.
 *
 * `\x00` IS REFUSED BY NAME AND THE NAME IS K9. `pcrec_compile` takes no
 * pattern length, so a NUL-bearing pattern would compile as its prefix and
 * report success — the same silent-wrong-artifact trap the whole-file NUL
 * refusal closes for a `pattern` line. Expressing a NUL pattern is a KNOWN
 * LIMIT with a named owner and a stated lifting trigger, not a silence. */
int pcrec_rxt_decode_escaped(const char *v, Arena *a, const char **out,
                             char *err, size_t errsz)
{
    size_t n = strlen(v);
    if (n < 2 || v[0] != '"' || v[n - 1] != '"') {
        snprintf(err, errsz, "an escaped pattern is double-quoted text "
                 "(got '%s')", v);
        return -1;
    }
    const char *s = v + 1;
    size_t len = n - 2;
    char *buf = arena_alloc(a, len + 1);
    size_t at = 0;
    for (size_t i = 0; i < len; i++) {
        if (s[i] != '\\') {
            if (s[i] == '"') {
                snprintf(err, errsz, "an unescaped '\"' ends the quoted text "
                         "(write \\\" for a literal quote)");
                return -1;
            }
            buf[at++] = s[i];
            continue;
        }
        if (i + 1 >= len) {
            snprintf(err, errsz, "a trailing backslash escapes nothing");
            return -1;
        }
        char c = s[++i];
        switch (c) {
            case '"':  buf[at++] = '"';  break;
            case '\\': buf[at++] = '\\'; break;
            case 'n':  buf[at++] = '\n'; break;
            case 't':  buf[at++] = '\t'; break;
            case 'r':  buf[at++] = '\r'; break;
            case 'f':  buf[at++] = '\f'; break;
            case 'v':  buf[at++] = '\v'; break;
            case 'x': {
                if (i + 2 >= len || !isxdigit((unsigned char)s[i + 1]) ||
                    !isxdigit((unsigned char)s[i + 2])) {
                    snprintf(err, errsz, "'\\x' wants exactly two hex digits");
                    return -1;
                }
                char hx[3] = { s[i + 1], s[i + 2], 0 };
                long b = strtol(hx, NULL, 16);
                i += 2;
                if (b == 0) {
                    snprintf(err, errsz,
                             "'\\x00' is refused (K9): the compile entry takes "
                             "no pattern length, so a NUL-bearing pattern "
                             "compiles as its prefix and reports success. "
                             "Lifts with rx_info.pattern_len");
                    return -1;
                }
                buf[at++] = (char)b;
                break;
            }
            default:
                snprintf(err, errsz, "unknown escape '\\%c' (the vocabulary is "
                         "\\\" \\\\ \\n \\t \\r \\f \\v \\xHH)", c);
                return -1;
        }
    }
    buf[at] = 0;
    *out = buf;
    return 0;
}

/* `config <name> [from a,b]` and its indented body. */
static int parse_config(RxtP *p, RxtSource *src, RxtLines *L, size_t *i,
                        RxtRow **out)
{
    size_t line = *i + 1;
    const char *v = line_value(L->v[*i]);
    char name[RXT_CONFIG_NAME_MAX + 1];
    const char *e = v;
    while (*e && !isspace((unsigned char)*e)) e++;
    size_t nlen = (size_t)(e - v);
    if (!nlen)
        return rxt_fail(p, RXTD_VALUE_SHAPE, line, "'config' needs a name");
    /* [DD-13b.W1.1 r46sem finding 8] A DISTINCT DIAGNOSTIC NAMING THE CAP.
     * This used to fall into the SAME "needs a name" message a genuinely
     * missing name gets — which tells an author with a too-long name a
     * FALSE thing about their line (it has a name; it is too long), worse
     * than no message at all. docs/spec/limits.md carries the 128-byte
     * identifier cap this and the two `target` fields below share. */
    if (nlen >= sizeof name)
        return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                        "'config' name is too long (%zu bytes, max %zu)",
                        nlen, sizeof name - 1);
    memcpy(name, v, nlen); name[nlen] = 0;
    if (!ident_ok(name))
        return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                        "'config' name '%s' is not an identifier", name);

    RxtRow *r = row_push(p, src, RXT_DECL_CONFIG, line);
    r->name = arena_strdup(p->arena, name);

    const char *rest = skip_ws(e);
    if (*rest) {
        if (strncmp(rest, "from", 4) || !isspace((unsigned char)rest[4]))
            return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, line,
                            "'config %s' takes only 'from <list>' after its "
                            "name (got '%s')", name, rest);
        const char *list = skip_ws(rest + 4);
        if (!config_list_ok(list))
            return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, line,
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
            return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, line,
                            "duplicate config name '%s' (already declared "
                            "on line %zu)", name, src->rows[k].line);

    /* THE BODY IS NO LONGER READ HERE. Until W23.1 this function
     * consumed its own indented continuation, with its own idea of what a
     * body line may be and its own vocabulary table; now S1 ATTACHES those
     * lines and the schema says which are legal in the `config` scope. The
     * function's job shrank to the HEADER, which is what "the schema
     * decides where structure begins and ends" costs a production that
     * used to decide for itself. `*i` is left ON the header line. */
    *out = r;
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
        return rxt_fail(p, RXTD_VALUE_SHAPE, line,
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
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "'target' prefix is too long (%zu bytes, max %zu)",
                            plen, sizeof prefix - 1);
        memcpy(prefix, v, plen); prefix[plen] = 0;
        if (!ident_ok(prefix))
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "'target' prefix '%s' is not an identifier (it "
                            "becomes the generated symbols' prefix)", prefix);
    }

    const char *rest = skip_ws(eq + 1);
    char def[RXT_TARGET_DEF_MAX + 1];
    const char *de = rest;
    while (*de && !isspace((unsigned char)*de)) de++;
    size_t dlen = (size_t)(de - rest);
    if (!dlen)
        return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                        "'target %s =' needs a definition name", prefix);
    /* [DD-13b.W1.1 r46sem finding 8] see the two twins above. */
    if (dlen >= sizeof def)
        return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                        "'target %s =' definition name is too long (%zu "
                        "bytes, max %zu)", prefix, dlen, sizeof def - 1);
    memcpy(def, rest, dlen); def[dlen] = 0;
    /* [DD-13b.W1.3] `defname_ok`: a target names a DEFINITION, which is a
     * file-namespace name and may carry `-`/`.`. The PREFIX above stays an
     * identifier — it is what the emitted symbols are built from. */
    if (!defname_ok(def))
        return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                        "'target %s' definition name '%s' is not a definition "
                        "name (a letter or '_' then letters, digits, '_', '-' "
                        "or '.')",
                        derived ? "=" : prefix, def);
    if (derived) {
        pcrec_rxt_prefix_from_name(def, prefix, sizeof prefix);
        if (!ident_ok(prefix))
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
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
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
                            "'target %s' takes only 'with <list>' after the "
                            "definition (got '%s')", prefix, tail);
        const char *list = skip_ws(tail + 4);
        if (!config_list_ok(list))
            return rxt_fail(p, RXTD_VALUE_SHAPE, line,
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
                return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, line,
                                "definitions '%s' and '%s' (line %zu) both map "
                                "to target prefix '%s'; a name's '-'/'.' "
                                "become '_', so give one an explicit prefix",
                                def, src->rows[k].value, src->rows[k].line,
                                prefix);
            return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, line,
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
        return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, r->line,
                        "'config %s from' is a cycle: %s", r->name, members);
    }
    if (depth >= RXT_FROM_NEST_MAX)
        return rxt_fail(p, RXTD_SCHEMA_CONSTRAINT, r->line,
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
            return rxt_fail(p, RXTD_VALUE_SHAPE, r->line,
                            "'config %s from' names '%.*s', which is not a "
                            "config declared in this file", r->name,
                            (int)(s - start), start);
        if (config_walk(p, src, dep, stack, depth + 1) != 0) return -1;
        s = skip_ws(s);
        if (*s == ',') s++;
    }
    return 0;
}

/* [DD-13b.W23.3a] Forward declarations: `include`'s resolution runs INSIDE
 * `pcrec_rxt_source_parse` below (§1.10.2 rule 2 — resolution must be
 * visible to `--list-source`, which never calls `pcrec_rxt_source_resolve`),
 * but the three helpers it needs are defined further down, in `lib`'s own
 * "path resolution" section, where they have lived since W1.2. Moving them
 * would be a bigger diff for no reason; declaring them here is the smaller
 * one. */
static int path_is_file(const char *p);
static const char *source_dir(RxtSource *src);
static char *join_path(Arena *a, const char *dir, const char *rest);

/* ------------------------------------------------------------- the entry */

/* Reads `path` and returns its `.rxt` HEAD as written — every `lib`/
 * `name`/`target`/`config` row plus every pattern block, in file order —
 * or NULL with `err` filled. Touches no OTHER filesystem path (no `lib`
 * resolution, no composition): that is `pcrec_rxt_source_resolve`'s job,
 * kept separate so `--list-source`'s dump stays a pure function of this
 * one file's bytes. Runs before any `Ctx` exists, so every error is
 * RETURNED rather than raised through `ctx_fail` — see the file header for
 * why. The structure layer (S0-S3, the attachment stack `st` below) is the
 * dispatch; `rxt_schema.def`'s rows say what is legal where. */
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

    /* THE ATTACHMENT STACK, arena-backed and grown rather than capped. S1
     * already required one — a reader must know which enclosing level a
     * lesser indent closes back to — so the OPEN SUBTREE marks one frame
     * and adds no memory the layer did not already carry. It needs no
     * limit of its own: each level costs at least one more leading space,
     * so the depth is bounded by the line it is reached on. */
    RxtFrame *st = NULL;
    size_t ndepth = 0, depthcap = 0;
    size_t nrows = pcrec_rxt_schema_nrows();
    const RxtSchemaRow *rowbase = pcrec_rxt_schema_rows(NULL);

#define RXT_PUSH_FRAME(IND, SCOPE, BASE, TREE, ROW)                        \
    do {                                                                   \
        if (ndepth == depthcap) {                                          \
            size_t nc = depthcap ? depthcap * 2 : 8;                       \
            RxtFrame *nv = arena_alloc(&src->arena, nc * sizeof *nv);      \
            if (ndepth) memcpy(nv, st, ndepth * sizeof *nv);               \
            st = nv; depthcap = nc;                                        \
        }                                                                  \
        memset(&st[ndepth], 0, sizeof st[ndepth]);                         \
        st[ndepth].indent = (IND);                                         \
        st[ndepth].scope  = (SCOPE);                                       \
        st[ndepth].base   = (BASE);                                        \
        st[ndepth].parent = ndepth ? st[ndepth - 1].scope                  \
                                   : RXT_SCOPE_NSCOPES;                    \
        st[ndepth].tree   = (TREE);                                        \
        st[ndepth].row    = (ROW);                                         \
        st[ndepth].seen   = arena_alloc(&src->arena, nrows * sizeof(size_t)); \
        st[ndepth].val    = arena_alloc(&src->arena, nrows * sizeof(char *)); \
        ndepth++;                                                          \
    } while (0)

/* A frame CLOSES when a lesser indent pops it, when a new group replaces
 * its contents, when a BLANK line or a COMMENT closes every attachment
 * (S0), and at end of file — FOUR sites, one helper, because the
 * scope-ranging constraints have to be answered at every one of them or a
 * record missing a `required` line at the foot of a file goes unreported.
 *
 * [O-29 FIX, 2026-09-16] The blank/comment site is the one this comment
 * used to leave out, and the omission was not editorial: the code itself
 * skipped the macro there, closing every open frame with a raw `ndepth =
 * 1` reset instead of calling it. S0's own rule ("a BLANK and a COMMENT
 * each close every open attachment") is silent about WHAT closing an
 * attachment costs — `frame_constraints` re-checked, and for a
 * PROVENANCE/VARIANT frame, `close_section_frame` pushing its
 * `#section` row — and a bare `ndepth = 1` pays neither. A provenance or
 * variant sub-block that is the last content before a blank line or a
 * comment (which is how two `pattern` blocks are ordinarily separated)
 * closed silently, exit 0, its record never pushed — pcrec-bench's O-29.
 * The fix is not a fifth mechanism: it is this same macro, called in a
 * loop exactly like the dedent-pop and EOF sites already do. */
#define RXT_CLOSE_FRAME(F, LINE)                                            \
    do {                                                                    \
        if (!(F)->tree) {                                                   \
            if (frame_constraints(&p, (F), rowbase, nrows, (LINE)) != 0)    \
                goto fail;                                                  \
            close_section_frame(&src->arena, src, rowbase, nrows, (F));    \
        }                                                                   \
    } while (0)

    RXT_PUSH_FRAME(0, RXT_SCOPE_FILE, RXT_SCOPE_FILE, 0, NULL);

    /* the immediately preceding CONTENT line, which is the only line a
     * deeper one may attach to (S1) */
    size_t last_indent = 0;
    int last_was_content = 0;
    const RxtSchemaRow *last_row = NULL;
    RxtRow *last_rxtrow = NULL;
    /* [DD-13b.W23.4] the most recently DISPATCHED row's own line and value
     * — refreshed on every schema-dispatched line (below), so whichever
     * row a following indented line attaches under, these two are ITS
     * opener's own facts, never a stale earlier one's. `cur_route` is the
     * `frames-buffer=` route live for the CURRENT pattern block, reset at
     * every new block; `last_aux_line` is the line of the most recently
     * emitted `#section aux` row, which an aux tree's own deeper push
     * reads as its `parent_line` (see the S1 tree-continuation site). */
    size_t last_row_line = 0;
    const char *last_row_value = NULL;
    const char *cur_route = "default";
    size_t last_aux_line = 0;

    for (size_t i = 0; i < L.n; i++) {
        const char *l = L.v[i];
        size_t line = i + 1;
        size_t indent = 0;
        RxtLineClass lc = line_class(l, &indent);

        /* S0: a WHITESPACE-ONLY line is INERT, a BLANK and a COMMENT each
         * close every open attachment and return to indent 0.
         *
         * [O-29 FIX] "close every open attachment" is RXT_CLOSE_FRAME's
         * fourth site (see its own comment above), not a bare depth
         * reset: every frame between here and the file level is popped
         * through the SAME macro the dedent-pop while loop and the EOF
         * loop use, top-down, so a PROVENANCE/VARIANT frame still open
         * at a blank line or a comment gets its `constraints` checked
         * and its `#section` row pushed exactly as it would at any
         * other closing site. */
        if (lc == LC_WS) continue;
        if (lc == LC_BLANK || lc == LC_COMMENT) {
            while (ndepth > 1) {
                RXT_CLOSE_FRAME(&st[ndepth - 1], line);
                ndepth--;
            }
            last_was_content = 0;
            last_row = NULL;
            last_rxtrow = NULL;
            continue;
        }

        /* §1.6.1a narrowing (4), TAKEN: indentation is SPACES. A tab in
         * the indentation region is refused BY NAME rather than silently
         * counted, because the two spellings have no agreed depth and a
         * file mixing them has no defined tree under any depth rule. A tab
         * inside a VALUE is still data and is untouched. */
        if (l[indent] == '\t') {
            rxt_fail(&p, RXTD_STRUCTURE, line,
                     "indentation is spaces; this line is indented with a "
                     "TAB (a tab inside a value is still data, but a tab "
                     "in the indentation has no agreed depth)");
            goto fail;
        }

        /* ---- S1: ATTACHMENT ---- */
        if (last_was_content && indent > last_indent) {
            /* a CHILD of the line above. What may be indented under a
             * kind is the `children` column and nothing else. */
            if (st[ndepth - 1].tree) {
                /* [DD-13b.W23.4] a DEEPER tree level — this frame's own
                 * `#section aux` accounting is inherited from the frame
                 * that was just open (now `st[ndepth - 2]`, the push
                 * below having not yet run): `parent_line` is the line of
                 * the aux row most recently emitted (which is exactly the
                 * row this new, deeper level attaches under — S1's own
                 * invariant), `depth` and `consumer` descend from the
                 * parent frame unchanged. */
                size_t pdepth = st[ndepth - 1].depth;
                const char *pconsumer = st[ndepth - 1].consumer;
                RXT_PUSH_FRAME(indent, RXT_SCOPE_NSCOPES, RXT_SCOPE_NSCOPES,
                               1, NULL);
                st[ndepth - 1].depth = pdepth + 1;
                st[ndepth - 1].open_line = last_aux_line;
                st[ndepth - 1].consumer = pconsumer;
            } else if (last_row && pcrec_rxt_schema_open_subtree(last_row)) {
                /* [DD-13b.W23.4] the FIRST tree level, opened directly off
                 * an `ext` line: `open_line`/`consumer` come from that
                 * line's own facts, captured when it was dispatched
                 * (`last_row_line`/`last_row_value`), not from this
                 * child's. */
                RXT_PUSH_FRAME(indent, RXT_SCOPE_NSCOPES, RXT_SCOPE_NSCOPES,
                               1, last_rxtrow);
                st[ndepth - 1].depth = 1;
                st[ndepth - 1].open_line = last_row_line;
                st[ndepth - 1].consumer = last_row_value;
            } else {
                RxtSchemaScope cs = pcrec_rxt_schema_child_scope(last_row);
                if (cs == RXT_SCOPE_NSCOPES) {
                    if (last_row)
                        rxt_fail(&p, RXTD_STRUCTURE, line,
                                 "indented line continues nothing ('%s' "
                                 "takes no continuation)", last_row->kind);
                    else
                        rxt_fail(&p, RXTD_STRUCTURE, line,
                                 "indented line continues nothing (the "
                                 "declaration above it takes no "
                                 "continuation)");
                    goto fail;
                }
                RXT_PUSH_FRAME(indent, cs, cs, 0, last_rxtrow);
                /* [DD-13b.W23.4] a PROVENANCE or VARIANT sub-block: its
                 * own opener line/value, for `close_section_frame` to
                 * report as `line`/`testee` once the frame closes. A
                 * no-op cost for CONFIG/DATA child frames, which read
                 * neither field. */
                st[ndepth - 1].open_line = last_row_line;
                st[ndepth - 1].open_value = last_row_value;
            }
        } else {
            while (ndepth > 1 && indent < st[ndepth - 1].indent) {
                RXT_CLOSE_FRAME(&st[ndepth - 1], line);
                ndepth--;
            }
            if (indent != st[ndepth - 1].indent) {
                /* [DD-13b.W23.3] THIS BRANCH HELD THREE DIFFERENT MISTAKES
                 * UNDER ONE SENTENCE, and splitting them is the finding
                 * rather than the tidying. "Indented line continues
                 * nothing (the declaration above it takes no
                 * continuation)" is TRUE of the case one arm up — a
                 * deeper indent under a childless kind — and false here
                 * in two distinct ways:
                 *
                 *   (a) NOTHING IS OPEN. A blank line, a column-1 comment
                 *       or the start of the file closes every attachment,
                 *       so there is no declaration above to take or
                 *       refuse a continuation. Legs B and C have said so
                 *       in their own words since W23.2; leg A did not.
                 *   (b) A RAGGED DEDENT — the line closes back to a depth
                 *       NOBODY OPENED, shallower than the level it left
                 *       and deeper than the one below it. Inside an OPEN
                 *       SUBTREE, where no kind takes or refuses
                 *       continuation at all, the shared sentence named a
                 *       rule the subtree does not have.
                 *
                 * The repairs differ (delete the indent; match an
                 * enclosing depth), which is the test for whether two
                 * refusals want one sentence or two. */
                if (!last_was_content)
                    rxt_fail(&p, RXTD_STRUCTURE, line,
                             "this line is indented and nothing above it is "
                             "open to attach it to (a blank line, a comment "
                             "or the start of the file closes every "
                             "attachment)");
                else
                    rxt_fail(&p, RXTD_STRUCTURE, line,
                             "this line is indented %zu, which closes back "
                             "to a depth nothing opened (the enclosing level "
                             "is indented %zu); indentation must return to a "
                             "depth already open",
                             indent, st[ndepth - 1].indent);
                goto fail;
            }
        }

        RxtFrame *f = &st[ndepth - 1];
        last_indent = indent;
        last_was_content = 1;
        last_row = NULL;
        last_rxtrow = f->row;

        /* Inside an OPEN SUBTREE nothing is dispatched: S2's opener set is
         * empty there, S3 never opens there, no schema row exists for any
         * line below the opener, and the unknown-token rule is VACUOUS
         * rather than excepted. pcrec parses the structure, dumps it
         * faithfully, and interprets nothing.
         *
         * [DD-13b.W23.4] "DUMPS IT FAITHFULLY" IS THIS. `#section aux`'s
         * three normative facts (format_design §2.24 at 3.4.1): the key
         * is the line's first token, the value is everything after the
         * separating whitespace VERBATIM to end of line (empty for a bare
         * key — the same rest-of-line reading `line_value` already gives
         * `pattern`/`description`), and row order is source order, which
         * falls out for free from pushing one row per line as it is read. */
        if (f->tree) {
            const char *tok = l + indent;
            size_t klen = 0;
            while (tok[klen] && !isspace((unsigned char)tok[klen])) klen++;
            RxtAux *ar = aux_push(&src->arena, src);
            ar->line = line;
            ar->block_line = block ? block->line : 0;
            ar->block_name = block ? block->name : NULL;
            ar->consumer = f->consumer;
            ar->depth = f->depth;
            ar->key = arena_strndup(&src->arena, tok, klen);
            /* rest-of-line VERBATIM past the key and its separating
             * whitespace — `tok_len`'s '=' special case (for
             * `frames-buffer=`) does not apply to an aux key, which is
             * free text pcrec resolves against nothing, so the value is
             * read off `klen` directly rather than through `line_value`. */
            ar->value = arena_strdup(&src->arena, skip_ws(tok + klen));
            ar->parent_line = f->open_line;
            last_aux_line = line;
            continue;
        }

        const char *tok = l + indent;
        size_t tlen = tok_len(tok);

        /* ---- S2: GROUPING. The opener set is a scope-free query. ---- */
        const RxtSchemaRow *row = NULL;
        const RxtSchemaRow *op = pcrec_rxt_schema_opener(tok, tlen);
        RxtSchemaScope gscope = pcrec_rxt_schema_group_scope(f->base);
        if (op && gscope != RXT_SCOPE_NSCOPES) {
            if (op->wave > PCREC_RXT_WAVE_BUILT) {
                refuse_wave(&p, line, op, f->scope);
                goto fail;
            }
            /* A NEW GROUP REPLACES THIS LEVEL'S CONTENTS, so the previous
             * group's scope-ranging constraints are answered HERE — the
             * third of RXT_CLOSE_FRAME's three sites, and the one a reader
             * misses, because nothing is popped. */
            if (f->scope == gscope) RXT_CLOSE_FRAME(f, line);
            f->scope = gscope;
            f->parent = f->base;
            memset(f->seen, 0, nrows * sizeof *f->seen);
            memset(f->val, 0, nrows * sizeof *f->val);
            f->nukey = 0;
            row = op;
        } else {
            row = pcrec_rxt_schema_row(f->scope, tok, tlen);
        }

        if (!row) {
            /* An indented `#` is a structure error naming the RULE, not
             * "'#' is not a directive": indentation is what makes the
             * difference, and a reader in the one region where it is
             * structural needs to be told which rule they met. */
            if (*tok == '#') {
                rxt_fail(&p, RXTD_STRUCTURE, line,
                         "a comment must start in column 1 (this '#' is "
                         "indented, and indentation inside a '%s' body is "
                         "continuation, not commentary — "
                         "format_design.md's lexical rule)",
                         pcrec_rxt_scope_name(f->scope));
                goto fail;
            }
            /* THE HEAD BOUNDARY, named. A head keyword down here is not an
             * unknown token — it is a real declaration in the wrong place,
             * and the reader needs to be told about the boundary rather
             * than about their spelling. */
            if (f->base == RXT_SCOPE_FILE && f->scope != RXT_SCOPE_FILE &&
                pcrec_rxt_schema_row(RXT_SCOPE_FILE, tok, tlen)) {
                rxt_fail(&p, RXTD_STRUCTURE, line,
                         "'%.*s' is a file-level declaration and the head "
                         "ENDED at the first 'pattern' line (line %zu); "
                         "nothing file-level may appear after it",
                         (int)tlen, tok, src->first_pattern_line);
                goto fail;
            }
            unknown_token(&p, line, tok, f->scope);
            goto fail;
        }

        if (row->wave > PCREC_RXT_WAVE_BUILT) {
            refuse_wave(&p, line, row, f->scope);
            goto fail;
        }

        /* ---- CARDINALITY, from the column ---- */
        size_t ridx = (size_t)(row - rowbase);
        if (row->cardinality == RXT_CARD_AT_MOST_ONE && f->seen[ridx]) {
            refuse_cardinality(&p, line, row, f->scope, f->seen[ridx]);
            goto fail;
        }
        if (!f->seen[ridx]) f->seen[ridx] = line;
        last_row = row;

        /* ---- [DD-13b.W23.3] THE `value` AND `constraints` COLUMNS ----
         *
         * Read here, once, for every kind in every scope — the same
         * placement `cardinality` already has, and for the same reason: a
         * per-production copy of this would be fourteen wordings for four
         * rules. A row whose value is REST-OF-LINE (`pattern`, `pcrec`,
         * `description`) keeps every byte; everything else is compared
         * TRIMMED, because run.sh's arms all end `[[:space:]]*$` and two
         * parsers disagreeing about a trailing space is the class W1.1
         * closed once already. */
        {
            const char *sv = (row->value == RXT_VAL_RAW ||
                              row->value == RXT_VAL_PROSE ||
                              row->value == RXT_VAL_CASE)
                                 ? line_value(tok)
                                 : value_trimmed(&p, tok);
            if (check_value_shape(&p, row, line, sv) != 0) goto fail;
            if (!f->val[ridx]) f->val[ridx] = sv;
            if (*row->constraints &&
                line_constraints(&p, f, row, line, sv) != 0) goto fail;
            /* [DD-13b.W23.4] THIS row's own line/value, for a following
             * indented line to capture as ITS opener's facts (a
             * `provenance`/`variant`/`ext` sub-block's own `line`/
             * `testee`/`consumer`) if it turns out to open one. Refreshed
             * on every dispatched row, so it is always the immediately
             * preceding one's, never stale. */
            last_row_line = line;
            last_row_value = sv;
        }

        /* ---- the VALUE, which is the only thing left for code ---- */
        if (f->scope == RXT_SCOPE_FILE) {
            if (row == pcrec_rxt_schema_row(RXT_SCOPE_FILE, "config", 6)) {
                RxtRow *cr = NULL;
                if (parse_config(&p, src, &L, &i, &cr) != 0) goto fail;
                last_rxtrow = cr;
                continue;
            }
            if (tok_is(tok, "target")) {
                if (parse_target(&p, src, &L, &i) != 0) goto fail;
                continue;
            }
            if (tok_is(tok, "lib")) {
                const char *v = value_trimmed(&p, tok);
                /* a `path-ref` is C's own two spellings: "local" or
                 * <store>. Both are RECORDED here and neither is opened:
                 * this parser touches no filesystem at all, which is what
                 * keeps `--list-source` a pure function of the file's
                 * bytes. */
                size_t n = strlen(v);
                if (n < 2 || !((v[0] == '"' && v[n - 1] == '"') ||
                               (v[0] == '<' && v[n - 1] == '>'))) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                             "'lib' wants a path reference, either \"local\" "
                             "or <store-name> (got '%s')", v);
                    goto fail;
                }
                RxtRow *r = row_push(&p, src, RXT_DECL_LIB, line);
                r->value = arena_strdup(&src->arena, v);
                last_rxtrow = r;
                continue;
            }
            if (tok_is(tok, "description")) {
                const char *text = NULL;
                if (prose_value(&p, &L, &i, row, indent, 0, &text) != 0)
                    goto fail;
                RxtRow *r = row_push(&p, src, RXT_DECL_DESCRIPTION, line);
                r->value = text;
                last_rxtrow = r;
                continue;
            }
            /* ---- [DD-13b.W23.3] THE HEAD DECLARATIONS ----
             *
             * Every one of them is RECOGNISED, value-checked and DROPPED:
             * §2.2's boundary for this step is that new productions parse
             * and are not yet REPORTED, so none of them pushes an `RxtRow`
             * and the dump's shape is untouched until W23.4. The single
             * exception is `vocabulary`, which is remembered because a
             * `closed` constraint one scope down has to read it. */
            if (tok_is(tok, "include")) {
                /* A PATH, in `lib`'s own quoted spelling and no other, so
                 * the format has ONE way to write a path (docs/spec/
                 * rxt_format.md's own `include` row: `<store>` is refused
                 * by value shape, unlike `lib`).
                 *
                 * [DD-13b.W23.3a] UNLIKE EVERY OTHER HEAD DECLARATION IN
                 * THIS BLOCK, this one IS resolved here, against the
                 * filesystem, at PARSE time. §1.10.2 rule 2 is why:
                 * `--list-source` is the ONLY call legs B and C ever make
                 * over an `include` line (they never parse the keyword
                 * itself), so a resolution that only `--source`'s later
                 * `pcrec_rxt_source_resolve` could see would leave them
                 * nothing to read. This row therefore breaks the
                 * "`--list-source` is a pure function of the file's bytes"
                 * property `lib` keeps — a departure §1.10.2 argues for
                 * directly, since an include path has TWO counterparts
                 * (all three legs must resolve it) where a `lib`/definition
                 * resolution has none. */
                const char *v = value_trimmed(&p, tok);
                size_t n = strlen(v);
                if (n < 3 || v[0] != '"' || v[n - 1] != '"') {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                             "'include' wants a double-quoted path (got '%s')",
                             v);
                    goto fail;
                }
                const char *ref = arena_strndup(&src->arena, v + 1, n - 2);
                const char *cand = ref[0] == '/'
                    ? ref
                    : join_path(&src->arena, source_dir(src), ref);
                if (!path_is_file(cand)) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                             "'include %s' names no readable file (looked "
                             "for %s)", v, cand);
                    goto fail;
                }
                /* `realpath(3)` with a NULL buffer (POSIX.1-2008): it
                 * mallocs the result, so a caller with no `PATH_MAX`
                 * opinion never has to guess one. Freed right after the
                 * arena copy — the SAME malloc/free-beside-an-arena shape
                 * `closure_walk`'s own `realloc`d kid array already uses a
                 * few hundred lines down. */
                char *realp = realpath(cand, NULL);
                if (!realp) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                             "'include %s' could not be resolved: %s", v,
                             strerror(errno));
                    goto fail;
                }
                const char *rp = arena_strdup(&src->arena, realp);
                free(realp);
                /* A second `include` of the SAME resolved real path is a
                 * refusal naming BOTH sites (`format_design.md` §2.5) — the
                 * closure-wide rule's own slice that ONE file's own parse
                 * can decide without walking anything else (two DIFFERENT
                 * spellings inside this file that resolve to the SAME real
                 * path). The transitive, cross-file half of the rule is
                 * legs B and C's, over the closures they walk. */
                for (size_t k = 0; k < src->nrows; k++) {
                    if (src->rows[k].kind != RXT_DECL_INCLUDE) continue;
                    if (strcmp(src->rows[k].name, rp) != 0) continue;
                    rxt_fail(&p, RXTD_SCHEMA_CONSTRAINT, line,
                             "'include %s' names the same file as line "
                             "%zu's 'include %s'", v, src->rows[k].line,
                             src->rows[k].value);
                    goto fail;
                }
                RxtRow *r = row_push(&p, src, RXT_DECL_INCLUDE, line);
                r->value = arena_strdup(&src->arena, v);
                r->name = rp;
                last_rxtrow = r;
                continue;
            }
            if (tok_is(tok, "vocabulary")) {
                const char *v = NULL;
                if (read_wrapped_value(&p, &L, &i, indent,
                                       value_trimmed(&p, tok), &v) != 0)
                    goto fail;
                size_t klen = 0;
                while (v[klen] && v[klen] != ' ') klen++;
                if (!ident_ok_n(v, klen)) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                             "'vocabulary' wants a key then its values (got "
                             "'%s')", v);
                    goto fail;
                }
                RxtVocab *vo = arena_alloc(&src->arena, sizeof *vo);
                vo->key = arena_strndup(&src->arena, v, klen);
                vo->members = arena_strdup(&src->arena, skip_ws(v + klen));
                vo->line = line;
                vo->next = p.vocab;
                p.vocab = vo;
                if (!*vo->members) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                             "'vocabulary %s' declares no values (a closed set "
                             "with no members can never be satisfied)",
                             vo->key);
                    goto fail;
                }
                /* [DD-13b.W23.4] name=key, value=the escaped member list
                 * (format_design §2.24's own words for this row). */
                {
                    RxtRow *r = row_push(&p, src, RXT_DECL_VOCABULARY, line);
                    r->name = vo->key;
                    r->value = vo->members;
                }
                continue;
            }
            if (tok_is(tok, "oracle")) {
                const char *v = value_trimmed(&p, tok);
                if (oracle_ref_ok(&p, line, v) != 0) goto fail;
                row_push(&p, src, RXT_DECL_ORACLE, line)->value = v;
                continue;
            }
            if (tok_is(tok, "tag")) {
                const char *v = value_trimmed(&p, tok);
                if (tag_list_ok(&p, line, v) != 0) goto fail;
                row_push(&p, src, RXT_DECL_TAG, line)->value = v;
                continue;
            }
            if (tok_is(tok, "use")) {
                const char *v = value_trimmed(&p, tok);
                if (!config_list_ok(v)) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                             "'use' wants a comma-separated config list (got "
                             "'%s')", v);
                    goto fail;
                }
                row_push(&p, src, RXT_DECL_USE, line)->value = v;
                continue;
            }
            if (tok_is(tok, "freq") || tok_is(tok, "ext")) {
                /* A `freq` block is named by a `defname`; an `ext` block is
                 * named by its CONSUMER, which pcrec resolves against
                 * nothing at all (§2.27: the consumer namespace is free).
                 * The two share this arm because the only thing leg A does
                 * with either name is check that it is a name. */
                const char *v = value_trimmed(&p, tok);
                if (!defname_ok(v)) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                             "'%.*s' wants a name — a letter or '_' then "
                             "letters, digits, '_', '-' or '.' (got '%s')",
                             (int)tlen, tok, v);
                    goto fail;
                }
                /* [DD-13b.W23.4] THE OPENER ROW, unconditionally — an
                 * `ext` block with no children still identifies itself
                 * (format_design §2.24 at 3.4.1, normative fact (a)): "the
                 * opener line ... IS the block's identity". `freq` is not
                 * an aux production and gets no row here. */
                if (tok_is(tok, "ext")) {
                    RxtAux *ar = aux_push(&src->arena, src);
                    ar->line = line;
                    ar->consumer = v;
                    ar->key = "ext";
                    ar->value = v;
                }
                continue;
            }
            unknown_token(&p, line, tok, f->scope);
            goto fail;
        }

        if (f->scope == RXT_SCOPE_CONFIG) {
            if (tok_is(tok, "analysis")) {
                /* names a `freq` data block; resolution is §2.10's and is
                 * not this step's — the value shape is all leg A asks. */
                continue;
            }
            RxtRow *cr = f->row;
            if (tok_is(tok, "pcrec")) {
                const char *raw = line_value(tok);
                if (!*raw) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line, "'pcrec' needs at least one flag");
                    goto fail;
                }
                /* ACCUMULATE, and it JOINS rather than replacing — the
                 * same rule `cfg_merge` already applies ACROSS configs,
                 * applied within one body so there is one answer to "what
                 * does a second `pcrec` line mean" instead of two. */
                if (cr->pcrec_raw) {
                    size_t n = strlen(cr->pcrec_raw) + 1 + strlen(raw) + 1;
                    char *j = arena_alloc(&src->arena, n);
                    snprintf(j, n, "%s %s", cr->pcrec_raw, raw);
                    cr->pcrec_raw = j;
                } else {
                    cr->pcrec_raw = arena_strdup(&src->arena, raw);
                }
                continue;
            }
            if (parse_setting(&p, cr, line, tok, 0) != 0) goto fail;
            continue;
        }

        /* ---- [DD-13b.W23.3] THE SUB-BLOCK SCOPES ----
         *
         * `provenance`, `variant` and the `freq` data block's bodies are
         * fully described by their rows: a value SHAPE, a cardinality, and
         * the constraints already applied above. There is nothing left for
         * per-kind code to do, which is the schema's whole claim tested on
         * its largest population — three scopes and twenty-one kinds
         * reached by one arm.
         *
         * A PROSE-VALUED attribute still opens its S3 region here, because
         * the region's EXTENT is structural and has to be consumed or its
         * lines reach S1 as orphans. That is the one thing a value shape
         * cannot do by being declared. */
        if (f->scope == RXT_SCOPE_PROVENANCE || f->scope == RXT_SCOPE_VARIANT ||
            f->scope == RXT_SCOPE_DATA) {
            if (pcrec_rxt_schema_prose_region(row)) {
                const char *text = NULL;
                if (prose_value(&p, &L, &i, row, indent, 0, &text) != 0)
                    goto fail;
                f->val[ridx] = text;
            }
            continue;
        }

        /* ---- BLOCK scope ---- */
        if (op) {
            if (!src->first_pattern_line) src->first_pattern_line = line;
            block = row_push(&p, src, RXT_DECL_PATTERN, line);
            f->row = block;
            last_rxtrow = block;
            /* [DD-13b.W23.4] a fresh block starts at the DEFAULT route,
             * exactly as `docs/spec/rxt_format.md`'s own words for
             * `frames-buffer=` say ("also the initial state"). */
            cur_route = "default";
            /* REST-OF-LINE, VERBATIM. `pattern` is the one production
             * whose value keeps every byte to the end of the line — no
             * trimming, no quoting, no escaping. Three corpus blocks carry
             * a literal TAB here and in all three the tab IS the thing
             * under test, which is why the dump escapes this column rather
             * than the parser normalising it.
             *
             * THE SEPARATOR IS A SPACE, NOT "whitespace", and that is
             * agreement with the other parser rather than pedantry:
             * run.sh's arm is `^pattern\ (.*)$` — a LITERAL space — so
             * `pattern<TAB>abc` is a hard error there. */
            const char *after = tok + tlen;
            if (*after != ' ') {
                rxt_fail(&p, RXTD_STRUCTURE, line,
                         "'%.*s' wants a single space before its regex "
                         "(the pattern text is rest-of-line verbatim from "
                         "there, so the separator cannot be part of it)",
                         (int)tlen, tok);
                goto fail;
            }
            if (tok_is(tok, "pattern-esc")) {
                /* [DD-13b.W23.3] THE SECOND BLOCK OPENER. Its value is the
                 * DECODED bytes, by pcrec's one decoder — so a block reads
                 * identically downstream however it was spelled, and
                 * `--list-source` reports the decoded text (re-escaped in
                 * the same vocabulary, a byte-exact round trip by
                 * construction). [DD-13b.W23.4] THE `esc` COLUMN now marks
                 * which spelling was used — non-NULL exactly when this
                 * block opened with `pattern-esc`. */
                block->esc = "1";
                char msg[192];
                const char *dec = NULL;
                if (pcrec_rxt_decode_escaped(value_trimmed(&p, tok),
                                             &src->arena, &dec,
                                             msg, sizeof msg) != 0) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line, "'pattern-esc': %s",
                             msg);
                    goto fail;
                }
                block->value = dec;
            } else {
                block->value = arena_strdup(&src->arena, after + 1);
            }
            continue;
        }

        if (!block) {
            /* a block-scope line with no block above it cannot happen:
             * the scope only becomes BLOCK when an opener switched it. */
            rxt_fail(&p, RXTD_VALUE_SHAPE, line, "internal: block-scope line with no block");
            goto fail;
        }
        last_rxtrow = block;

        /* The EXPECTATION kinds are recognised, RECORDED for the dump, and
         * never SCORED. A `.rxt` expectation is the harness's business:
         * this parser reads a file to find its definitions and targets,
         * and a compiler that started scoring `m` lines would be a second
         * harness — recording is `--list-source`'s own job (§2.24), not a
         * step toward scoring. */
        if (tok_is(tok, "perr")) continue;
        if (tok_is(tok, "frames-buffer=")) {
            /* [DD-13b.W23.4] POSITIONAL, not block-scoped (rxt_format.md's
             * own words): the route named here governs every CASE row
             * below it until the next such line or the block's end —
             * `cur_route` is reset to "default" at every new block. */
            cur_route = f->val[ridx] ? f->val[ridx] : "default";
            continue;
        }
        if (row->value == RXT_VAL_CASE) {
            RxtCase *c = case_push(&src->arena, src);
            c->line = line;
            c->block_line = block->line;
            c->block_name = block->name;
            c->kind = row->kind;
            c->route = cur_route;
            parse_case_body(tok + tlen, row->kind, c, &src->arena);
            continue;
        }

        /* ---- [DD-13b.W23.3] THE BLOCK-SCOPED W23 LINES ----
         *
         * `provenance`, `variant` and `ext` are SUB-BLOCK OPENERS and need
         * no arm at all beyond their value: the `children` column routes
         * their bodies and the rows above do the rest. `mc` is an
         * expectation kind and was consumed by the `RXT_VAL_CASE` skip.
         * What is left is three one-line value rules. */
        if (tok_is(tok, "tag")) {
            const char *v = value_trimmed(&p, tok);
            if (tag_list_ok(&p, line, v) != 0) goto fail;
            /* [DD-13b.W23.4] ACCUMULATE, comma-joined in source order —
             * `tag`'s own cardinality is REPEAT, so the dump's `tags`
             * column has to serve every line the same way `pcrec_raw`'s
             * space-join already serves several `pcrec` lines. */
            if (block->tags) {
                size_t n = strlen(block->tags) + 1 + strlen(v) + 1;
                char *j = arena_alloc(&src->arena, n);
                snprintf(j, n, "%s,%s", block->tags, v);
                block->tags = j;
            } else {
                block->tags = v;
            }
            continue;
        }
        if (tok_is(tok, "oracle")) {
            const char *v = value_trimmed(&p, tok);
            if (oracle_ref_ok(&p, line, v) != 0) goto fail;
            block->oracle = v;
            continue;
        }
        if (tok_is(tok, "under")) {
            /* The SCORING of a second correct answer is the consumer's
             * (§2.17) and the harness's counted-skip is legs B and C's.
             * Leg A's whole interest is the KEY TUPLE, which `unique-by`
             * has already taken above, and the CONVENTION, which `closed`
             * has already checked against a `vocabulary convention` line
             * if the file declared one.
             *
             * [DD-13b.W23.4] AND THE WRAPPED CASE LINE, for the dump: the
             * schema routed us here on the OUTER `under` row alone, so
             * nothing yet has read `<case-line>`'s own kind — `is_case_kind`
             * is the check that stops a malformed tail from being
             * misparsed as some real kind's fields. */
            const char *rest = line_value(tok);
            const char *w = rest;
            while (*w && !isspace((unsigned char)*w)) w++;
            const char *conv = arena_strndup(&src->arena, rest,
                                             (size_t)(w - rest));
            const char *ib = skip_ws(w);
            size_t klen = 0;
            while (ib[klen] && !isspace((unsigned char)ib[klen])) klen++;
            char ikind[8];
            if (klen < sizeof ikind) {
                memcpy(ikind, ib, klen);
                ikind[klen] = 0;
                if (is_case_kind(ikind)) {
                    RxtCase *c = case_push(&src->arena, src);
                    c->line = line;
                    c->block_line = block->line;
                    c->block_name = block->name;
                    c->kind = arena_strdup(&src->arena, ikind);
                    c->under = conv;
                    c->route = cur_route;
                    parse_case_body(skip_ws(ib + klen), c->kind, c, &src->arena);
                }
            }
            continue;
        }
        if (tok_is(tok, "provenance") || tok_is(tok, "variant") ||
            tok_is(tok, "ext")) {
            if (tok_is(tok, "variant")) {
                const char *v = value_trimmed(&p, tok);
                /* §2.23's 3.4 ruling: a testee name is a FREE IDENTIFIER
                 * validated as a name and as UNIQUE within its block (the
                 * `unique-by value` row above) AND AGAINST NOTHING ELSE.
                 * With `config … testee` withdrawn there is no roster in
                 * the format to resolve against, and pcrec does not know
                 * what engines exist — a deliberate non-check, which the
                 * absence of a `closed` clause on the row states where a
                 * reader can fetch it. */
                if (!defname_ok(v)) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                             "'variant' wants a testee name — a letter or "
                             "'_' then letters, digits, '_', '-' or '.' "
                             "(got '%s')", v);
                    goto fail;
                }
            } else if (tok_is(tok, "ext")) {
                const char *v = value_trimmed(&p, tok);
                if (!defname_ok(v)) {
                    rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                             "'ext' wants a consumer name — a letter or '_' "
                             "then letters, digits, '_', '-' or '.' (got "
                             "'%s')", v);
                    goto fail;
                }
                /* [DD-13b.W23.4] THE OPENER ROW, unconditionally — see the
                 * FILE-scope arm's identical comment. */
                RxtAux *ar = aux_push(&src->arena, src);
                ar->line = line;
                ar->block_line = block->line;
                ar->block_name = block->name;
                ar->consumer = v;
                ar->key = "ext";
                ar->value = v;
            }
            continue;
        }

        if (tok_is(tok, "name")) {
            const char *v = value_trimmed(&p, tok);
            /* [DD-13b.W1.3] `defname_ok`, not `ident_ok`: see that
             * function's header for the ruling. **[DD-13b.W23.3, D100] the
             * boundary that header used to draw is REPEALED** — a `-`/`.`
             * definition is callable through its DERIVED identifier
             * (`rxt_compose.c`'s `def_by_name`), so this line no longer
             * decides whether the block can be called, only what it may be
             * called. */
            if (!defname_ok(v)) {
                rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                         "'name' wants a definition name — a letter or '_' "
                         "then letters, digits, '_', '-' or '.' (got '%s')",
                         v);
                goto fail;
            }
            /* A BLOCK'S `name` IS IN THE FILE NAMESPACE (w1_impl DECIDED
             * (7)) — not in the pattern's group namespace — so this
             * collision check is against other blocks and nothing else. */
            for (size_t k = 0; k < src->nrows; k++)
                if (src->rows[k].kind == RXT_DECL_PATTERN &&
                    &src->rows[k] != block && src->rows[k].name &&
                    !strcmp(src->rows[k].name, v)) {
                    rxt_fail(&p, RXTD_SCHEMA_CONSTRAINT, line,
                             "duplicate block name '%s' (already named on "
                             "line %zu)", v, src->rows[k].line);
                    goto fail;
                }
            block->name = arena_strdup(&src->arena, v);
            continue;
        }
        if (tok_is(tok, "export")) {
            /* [DD-13b.W1.3, D89 addendum point 2] THE LIBRARY'S OWN
             * INTERFACE, DECLARED, in the `config-list` shape `with`/`use`/
             * `from` already use. WHAT IS NOT CHECKED HERE: whether the
             * definition declares a group by each name — that is a question
             * about the PATTERN, answered by the composer at bind time. */
            const char *v = value_trimmed(&p, tok);
            if (!config_list_ok(v)) {
                rxt_fail(&p, RXTD_VALUE_SHAPE, line,
                         "'export' wants a comma-separated list of group "
                         "names (got '%s')", v);
                goto fail;
            }
            block->exports = rtrim_ws(&src->arena, v);
            continue;
        }
        if (tok_is(tok, "description")) {
            /* A BLOCK'S `description` TAKES THE FULL PROSE VALUE SINCE
             * W23.1, INCLUDING THE `|` REGION — the widening §1.2.5 rules
             * and SW16 names in the spec. Until the two layers were split,
             * "a pattern block's lines are NOT indented" was a LEXICAL rule
             * that contradicted the prose production; under S1 there is one
             * attachment rule everywhere and a prose region's extent is
             * S3's, so the contradiction dissolves rather than being
             * arbitrated. An EMPTY description is accepted, matching legs B
             * and C. */
            const char *text = NULL;
            if (prose_value(&p, &L, &i, row, indent, 0, &text) != 0)
                goto fail;
            block->description = text;
            continue;
        }
        if (parse_setting(&p, block, line, tok, 1) != 0) goto fail;
    }

    /* END OF FILE CLOSES EVERY OPEN FRAME (RXT_CLOSE_FRAME's third site).
     * Without this a `provenance` record missing its `source` at the foot
     * of a file is never reported, which is the failure mode a `required`
     * constraint exists to prevent and the one a reader would assume is
     * covered. */
    for (size_t d = ndepth; d > 0; d--)
        RXT_CLOSE_FRAME(&st[d - 1], L.n);
#undef RXT_CLOSE_FRAME
#undef RXT_PUSH_FRAME

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
                rxt_fail(&p, RXTD_VALUE_SHAPE, r->line,
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
    pcrec_arena_free(&src->arena);
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
    const char *flags, *features, *encoding, *engine, *tune;
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
    if (add->tune)      dst->tune = add->tune;
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
    s->tune = r->tune;
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
    char *heap = pcrec_sb_take(&sb);
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

/* Loads and walks `s` (already resolved to `respath`) into `cl`'s LIBRARY
 * CLOSURE: records `s` as a kid of `cl->root`, records every readable `lib`
 * reference `s` names, and recurses into each — a fixpoint over the
 * `lib`-reaches-`lib` graph, keyed on the RESOLVED PATH so a diamond is
 * read once and a cycle terminates (`closure_seen`). Returns nonzero on the
 * first unreadable/malformed child, which `err` already names. */
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
                /* THE WORST CASE OF THE FOUR: TWO full paths under one
                 * `pcrec_error.msg`, `rxt_fail`'s own `<path>:<line>: `
                 * prefix (this file) plus `cl->defs[k].file:line` (the
                 * OTHER file) in the body — both grow with `TMPDIR`, so
                 * this is the only one of the four paying the TMPDIR tax
                 * TWICE and needs the tightest prose. "'%s' dup: %s:%zu"
                 * is the two locations and nothing else; "is declared
                 * twice in the lib closure" (the original wording) was
                 * measured truncating the SECOND path's own extension on
                 * this box's own TMPDIR, which is what W1.3's
                 * `compose_dup_definition.rxt` needle exists to catch. */
                return rxt_fail(&fp, RXTD_SCHEMA_CONSTRAINT, r->line,
                                "'%s' dup: %s:%zu",
                                r->name, cl->defs[k].file, cl->defs[k].line);
        unsigned long long f = 0;
        char badc = 0;
        if (pcrec_rxt_flags_from_letters(r->flags, &f, &badc) != 0)
            return rxt_fail(&fp, RXTD_VALUE_SHAPE, r->line,
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
            return rxt_fail(&fp, RXTD_VALUE_SHAPE, r->line,
                            "'lib %s' does not parse: %s", r->value, kerr.msg);
        if (cl->root->nkids == cl->root->kidcap) {
            size_t nc = cl->root->kidcap ? cl->root->kidcap * 2 : 4;
            RxtSource **nv = realloc(cl->root->kids, nc * sizeof *nv);
            if (!nv) { pcrec_rxt_source_free(kid);
                       return rxt_fail(&fp, RXTD_VALUE_SHAPE, r->line, "out of memory reading "
                                       "'lib %s'", r->value); }
            cl->root->kids = nv; cl->root->kidcap = nc;
        }
        cl->root->kids[cl->root->nkids++] = kid;
        if (closure_walk(cl, kid, rp) != 0) return -1;
    }
    return 0;
}

/* ---- the entry ---- */

/* Answers the three questions `--source` must answer before it can call
 * `pcrec_compile` even once: WHICH artifacts (every `target` row, or the
 * implicit `target rx` for a file with no head and exactly one unnamed
 * block), FROM WHICH block (a definition name resolved in the FILE
 * namespace, walking the `lib` closure `closure_walk` builds), and UNDER
 * WHICH SETTINGS (`with`/`from`'s flat later-wins merge, applied once per
 * block). Fills `*out`/`*nout` with the resolved `RxtTarget` array, or
 * returns nonzero with `err` naming the first unresolvable reference. */
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
         * and for the same reason (DECIDED (1)).
         *
         * TRIMMED to fit `pcrec_error.msg`'s 256-byte cap under a long
         * `TMPDIR` (macOS default ~49 bytes): the explanatory clauses
         * ("the spelling is real, not a typo", "The \"path\" form resolves
         * today") are not part of what a caller needs to ACT — the store
         * name and the two contract needles ("NOT IN THIS BUILD", "[LIB]")
         * are. */
        if (rl >= 2 && ref[0] == '<')
            return rxt_fail(&p, RXTD_VALUE_SHAPE, r->line,
                            "'lib %s' is a STORE reference: NOT IN THIS "
                            "BUILD (see [LIB]); use a \"path\" instead", ref);
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
            return rxt_fail(&p, RXTD_VALUE_SHAPE, r->line,
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
            t->tune = lone->tune;
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
         * must come before whatever merely helps.
         *
         * STILL NOT ENOUGH on a long `TMPDIR` (macOS's per-user default is
         * ~49 bytes, against Linux's flat `/tmp`): the reworded prose above
         * was measured landing this refusal AT the 263-byte class-check
         * limit on this box, still occasionally shedding its own tail. The
         * words this trims (three of them: "names", "no pattern block here
         * has that name", "(a lib's definitions need the composer,
         * W1.3)") are commentary the contract does not require — §1.3 asks
         * for the definition name and the chain searched, not for the
         * shape of "pattern block" or a pointer to this milestone. */
        if (!blk)
            return rxt_fail(&p, RXTD_VALUE_SHAPE, tr->line,
                            "'target %s' -> no definition '%s'; searched %s",
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
        t->tune     = blk->tune     ? blk->tune     : s.tune;
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
 * swallows.
 *
 * [REVW.1] wave 1: THE ESCAPE ITSELF IS `sb_field` (src/core/sb.c) NOW.
 * It moved verbatim, one directory up, so the `.rxt` format's subject
 * vocabulary and `--explain`'s frame-only one share their `\xNN` tail
 * instead of spelling it twice. This file's call sites say `sb_field`
 * directly rather than through a forwarder: a one-line forwarder would be
 * a second name for one function, and the reader wants to see WHICH
 * vocabulary a column is escaped in. */

static const char *kind_name(RxtDeclKind k)
{
    switch (k) {
    case RXT_DECL_LIB:         return "lib";
    case RXT_DECL_TARGET:      return "target";
    case RXT_DECL_CONFIG:      return "config";
    case RXT_DECL_DESCRIPTION: return "description";
    case RXT_DECL_PATTERN:     return "pattern";
    case RXT_DECL_INCLUDE:     return "include";
    case RXT_DECL_VOCABULARY:  return "vocabulary";
    case RXT_DECL_ORACLE:      return "oracle";
    case RXT_DECL_TAG:         return "tag";
    case RXT_DECL_USE:         return "use";
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
    /* [DD-13b.W23.4] THREE MORE, same rule: append-only, positions 1-16
     * unchanged (format_design §2.24). */
    "tags", "oracle", "esc",
    /* [OPT-DIAL] APPENDED, same append-only rule: positions 1-19 unchanged,
     * so every positional reader of the earlier columns survives. */
    "tune",
};
#define RXT_NCOLS (sizeof rxt_columns / sizeof *rxt_columns)

/* [DD-13b.W23.4] one `#section` block: the NAME line, the header comment
 * (the same shape `schema_dump.c`'s own two sections use), then rows. The
 * header parameter is the PRE-BUILT `"#col1\tcol2\t...\n"` line so every
 * section writes it identically rather than five variations on one loop. */
static void section_open(StrBuf *sb, const char *name, const char *header)
{
    sb_printf(sb, "#section %s\n", name);
    sb_puts(sb, header);
}

size_t pcrec_rxt_source_ncols(void) { return RXT_NCOLS; }

/* Renders `--list-source`'s TSV: one row per head declaration and per
 * pattern block, in file order, plus the `#section` blocks
 * (`provenance`/`variants`/`cases`/`aux`) `src`'s own row scan already
 * accumulated. AS WRITTEN, never resolved — matches `pcrec_rxt_source_
 * parse`'s own promise so the two cannot silently disagree about what the
 * file says. Returns a malloc'd string the caller frees. The header comment
 * embedded in the output IS the contract (docs/spec/table_contract.md);
 * changing a column here is a `docs/spec/` change in the same commit (D80). */
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
        "# Empty field = none.\n"
        "#\n"
        "# [DD-13b.W23.4] Column 5's `pattern` now means TWO things,\n"
        "# disambiguated by column 19 (`esc`): for a `pattern` block it is\n"
        "# the line's bytes verbatim; for `pattern-esc` it is the DECODED\n"
        "# bytes, re-escaped in this same vocabulary. Both deliver the same\n"
        "# bytes; `esc` says which spelling wrote them.\n"
        "#\n"
        "# FOUR `#section` BLOCKS follow the main table, unconditionally\n"
        "# WHEN NON-EMPTY, never interleaved with it: `provenance`,\n"
        "# `variants`, `cases` (one row per `m`/`n`/`ms`/`ns`/`mc`/`gu`/`g`/\n"
        "# `gp` line, `under`-wrapped ones included), `aux` (one row per\n"
        "# LINE of an `ext` tree, the opener included at depth 0 — its\n"
        "# contents are dumped faithfully and interpreted by nothing here,\n"
        "# format_design.md §2.27). No section row's field 1 (always the\n"
        "# integer `line`) can equal a main-table `kind` token.\n");

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
        sb_field(&sb, is_pat ? r->description : r->value);   /*  4 value */
        sb_putc(&sb, '\t');
        if (is_pat) sb_field(&sb, r->value);                 /*  5 pattern */
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
        if (is_cfg) sb_field(&sb, r->pcrec_raw);             /* 15 pcrec */
        sb_putc(&sb, '\t');
        if (r->exports) sb_puts(&sb, r->exports);               /* 16 export */
        sb_putc(&sb, '\t');
        if (r->tags) sb_puts(&sb, r->tags);                     /* 17 tags */
        sb_putc(&sb, '\t');
        if (r->oracle) sb_puts(&sb, r->oracle);                 /* 18 oracle */
        sb_putc(&sb, '\t');
        if (r->esc) sb_puts(&sb, r->esc);                       /* 19 esc */
        sb_putc(&sb, '\t');
        if (r->tune) sb_puts(&sb, r->tune);                     /* 20 tune */
        sb_putc(&sb, '\n');
    }

    /* [DD-13b.W23.4] THE FOUR `#section` BLOCKS, unconditionally when
     * non-empty, ALWAYS AFTER the main table and never interleaved with it
     * (format_design §2.24; DECIDED (5), w23_impl §1.5 — R2's "first
     * `pattern` row is the body boundary" invariant depends on it). A file
     * using no W23 production emits NO `#section` line at all, so its
     * stream differs from a pre-W23 one only in the header row's three
     * appended columns. */
    if (src->nprovs) {
        section_open(&sb, "provenance",
            "#line\tblock_line\tblock_name\tsource\turl\tref\tretrieved"
            "\tlicense\tlicense-note\tfidelity\tadaptation\tattribution"
            "\tbytes\tsha256\n");
        for (size_t i = 0; i < src->nprovs; i++) {
            const RxtProv *r = &src->provs[i];
            sb_printf(&sb, "%zu\t%zu\t", r->line, r->block_line);
            if (r->block_name) sb_puts(&sb, r->block_name);
            sb_putc(&sb, '\t');
            if (r->source) sb_puts(&sb, r->source);
            sb_putc(&sb, '\t');
            if (r->url) sb_puts(&sb, r->url);
            sb_putc(&sb, '\t');
            if (r->ref) sb_puts(&sb, r->ref);
            sb_putc(&sb, '\t');
            if (r->retrieved) sb_puts(&sb, r->retrieved);
            sb_putc(&sb, '\t');
            if (r->license) sb_puts(&sb, r->license);
            sb_putc(&sb, '\t');
            if (r->license_note) sb_field(&sb, r->license_note);
            sb_putc(&sb, '\t');
            if (r->fidelity) sb_puts(&sb, r->fidelity);
            sb_putc(&sb, '\t');
            if (r->adaptation) sb_field(&sb, r->adaptation);
            sb_putc(&sb, '\t');
            if (r->attribution) sb_field(&sb, r->attribution);
            sb_putc(&sb, '\t');
            if (r->bytes) sb_puts(&sb, r->bytes);
            sb_putc(&sb, '\t');
            if (r->sha256) sb_puts(&sb, r->sha256);
            sb_putc(&sb, '\n');
        }
    }

    if (src->nvariants) {
        section_open(&sb, "variants",
            "#line\tblock_line\tblock_name\ttestee\tkind\ttext\tgroups"
            "\tnote\tunsupported\n");
        for (size_t i = 0; i < src->nvariants; i++) {
            const RxtVariant *r = &src->variants[i];
            sb_printf(&sb, "%zu\t%zu\t", r->line, r->block_line);
            if (r->block_name) sb_puts(&sb, r->block_name);
            sb_putc(&sb, '\t');
            if (r->testee) sb_puts(&sb, r->testee);
            sb_putc(&sb, '\t');
            if (r->kind) sb_puts(&sb, r->kind);
            sb_putc(&sb, '\t');
            if (r->text) sb_field(&sb, r->text);
            sb_putc(&sb, '\t');
            if (r->groups) sb_puts(&sb, r->groups);
            sb_putc(&sb, '\t');
            if (r->note) sb_field(&sb, r->note);
            sb_putc(&sb, '\t');
            if (r->unsupported) sb_field(&sb, r->unsupported);
            sb_putc(&sb, '\n');
        }
    }

    if (src->ncases) {
        section_open(&sb, "cases",
            "#line\tblock_line\tblock_name\tkind\tunder\tstartpos"
            "\tsubject_form\tsubject\tsubject_id\tsha256\tstart\tend"
            "\tcount\tgiveup\tslot\troute\n");
        for (size_t i = 0; i < src->ncases; i++) {
            const RxtCase *r = &src->cases[i];
            sb_printf(&sb, "%zu\t%zu\t", r->line, r->block_line);
            if (r->block_name) sb_puts(&sb, r->block_name);
            sb_putc(&sb, '\t');
            sb_puts(&sb, r->kind);
            sb_putc(&sb, '\t');
            if (r->under) sb_puts(&sb, r->under);
            sb_putc(&sb, '\t');
            if (r->startpos) sb_puts(&sb, r->startpos);
            sb_putc(&sb, '\t');
            if (r->subject_form) sb_puts(&sb, r->subject_form);
            sb_putc(&sb, '\t');
            if (r->subject) sb_field(&sb, r->subject);
            sb_putc(&sb, '\t');
            if (r->subject_id) sb_puts(&sb, r->subject_id);
            sb_putc(&sb, '\t');
            if (r->sha256) sb_puts(&sb, r->sha256);
            sb_putc(&sb, '\t');
            if (r->start) sb_puts(&sb, r->start);
            sb_putc(&sb, '\t');
            if (r->end) sb_puts(&sb, r->end);
            sb_putc(&sb, '\t');
            if (r->count) sb_puts(&sb, r->count);
            sb_putc(&sb, '\t');
            if (r->giveup) sb_puts(&sb, r->giveup);
            sb_putc(&sb, '\t');
            if (r->slot) sb_puts(&sb, r->slot);
            sb_putc(&sb, '\t');
            sb_puts(&sb, r->route);
            sb_putc(&sb, '\n');
        }
    }

    if (src->nauxes) {
        section_open(&sb, "aux",
            "#line\tblock_line\tblock_name\tconsumer\tdepth\tkey\tvalue"
            "\tparent_line\n");
        for (size_t i = 0; i < src->nauxes; i++) {
            const RxtAux *r = &src->auxes[i];
            sb_printf(&sb, "%zu\t", r->line);
            if (r->block_line) sb_printf(&sb, "%zu", r->block_line);
            sb_putc(&sb, '\t');
            if (r->block_name) sb_puts(&sb, r->block_name);
            sb_putc(&sb, '\t');
            if (r->consumer) sb_puts(&sb, r->consumer);
            sb_printf(&sb, "\t%zu\t", r->depth);
            sb_puts(&sb, r->key);
            sb_putc(&sb, '\t');
            sb_field(&sb, r->value);
            sb_putc(&sb, '\t');
            if (r->parent_line) sb_printf(&sb, "%zu", r->parent_line);
            sb_putc(&sb, '\n');
        }
    }

    return pcrec_sb_take(&sb);
}
