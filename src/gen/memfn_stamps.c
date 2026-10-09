/* src/gen/memfn_stamps.c — [MEMFN] R4a′: the kit's every-artifact stamps,
 * `<PREFIX>_RUN_WORDS` (M1b), `<PREFIX>_MEMFN_FORMS` and `<PREFIX>_MEMFN_LIBC`
 * (docs/design/memfn/integration.md §R4.3.3, §R4.8, §18; D147 addendum 10,
 * Q53/Q55; docs/spec/match_api.md §6.3), and pcrec's own line after them,
 * `<PREFIX>_SIMD_GUARDED_BYTES` ([MEMFN] RQ-3, D155 addendum 2).
 *
 * THE KIT WRITES THE LINES; pcrec owns WHERE they go and the libc inventory
 * of the text pcrec spelled. Both engines write a one-line MARK where the
 * stamps belong (`pcrec_emit_memfn_mark`, after the engine body). The
 * driver, once the artifact is finished, scans the whole text for libc
 * calls, notes each through `mf_art_note_libc`, has `mf_stamps` render the
 * three lines through a sink onto `pcrec_sb_stampf` (RUN_WORDS, unquoted)
 * and `pcrec_sb_stamp_str` (the other two), and splices them over the mark
 * (`pcrec_memfn_stamps_render`).
 *
 * WHY A FINISHING PASS AND NOT A NOTE AT EVERY EMITTER THAT SPELLS A CALL.
 * The record is a WHOLE-ARTIFACT inventory (Q53): the search code, the
 * variable resolver's `strlen`, `--emit-main`'s `printf`, the trace macros'
 * `fprintf`. A note per spelling site is a second spelling of each, and a
 * new site that forgets it is silently missing from the record; the pass
 * reads what was actually written, the prefix render's own reason
 * (core/internal.h [K79]). Its one blind spot is a libc function missing
 * from `libc_names` below: C11 (tests/memfn/run_libc_census.sh), whose names
 * come from the compiled object, reports it.
 *
 * WHY THE MARK IS A PLACEHOLDER-LEAD BYTE. A mark the pass failed to replace
 * then fails `pcrec_sb_render_prefix` loudly as a stray lead byte, so it can
 * never reach a caller as text. The pass runs on every attempt, before the
 * size measurement, so the size term measures the artifact it ships. */
#include <string.h>

#include "gen/memfn_sites.h"

/* The mark: a placeholder-lead byte that is not the prefix placeholder. */
#define MEMFN_MARK "\x01M\n"

void pcrec_emit_memfn_mark(StrBuf *c)
{
#ifdef PCREC_SIMD_WITNESS
    pcrec_memfn_simd_witness(c);   /* RQ-3's file-scope block, both engines */
#endif
    pcrec_sb_puts(c, MEMFN_MARK);
}

/* The C library's functions, by the headers that declare them: C17
 * <string.h>, <stdio.h>, <stdlib.h>, <ctype.h>, and the POSIX/GNU string
 * functions a search form may call. A name here is RECOGNISED, not
 * recorded: only a call the text makes is noted. `memchr` is not here
 * ([MEMFN] M7 rider): since M4 no pcrec text spells a `memchr(` call (every
 * one is a kit row's, and the kit notes it as it renders, mf_art_note_libc),
 * so the entry recognised nothing (S513's equivalence, slot11). */
static const char *const libc_names[] = {
    /* <string.h> */
    "memcmp", "memcpy", "memmove", "memset", "strcat", "strchr",
    "strcmp", "strcoll", "strcpy", "strcspn", "strerror", "strlen", "strncat",
    "strncmp", "strncpy", "strpbrk", "strrchr", "strspn", "strstr", "strtok",
    "strxfrm",
    /* POSIX / GNU string functions */
    "bcmp", "bcopy", "bzero", "memmem", "mempcpy", "memrchr", "rawmemchr",
    "stpcpy", "stpncpy", "strcasecmp", "strchrnul", "strdup", "strncasecmp",
    "strndup", "strnlen", "strsep", "strtok_r",
    /* <stdio.h> */
    "clearerr", "dprintf", "fclose", "feof", "ferror", "fflush", "fgetc",
    "fgetpos", "fgets", "fileno", "fopen", "fprintf", "fputc", "fputs",
    "fread", "freopen", "fscanf", "fseek", "fsetpos", "ftell", "fwrite",
    "getc", "getchar", "getline", "perror", "printf", "putc", "putchar",
    "puts", "remove", "rename", "rewind", "scanf", "setbuf", "setvbuf",
    "snprintf", "sprintf", "sscanf", "tmpfile", "tmpnam", "ungetc",
    "vfprintf", "vfscanf", "vprintf", "vscanf", "vsnprintf", "vsprintf",
    "vsscanf",
    /* <stdlib.h> */
    "_Exit", "abort", "abs", "aligned_alloc", "at_quick_exit", "atexit",
    "atof", "atoi", "atol", "atoll", "bsearch", "calloc", "div", "exit",
    "free", "getenv", "labs", "ldiv", "llabs", "lldiv", "malloc", "mblen",
    "mbstowcs", "mbtowc", "qsort", "quick_exit", "rand", "realloc", "srand",
    "strtod", "strtof", "strtol", "strtold", "strtoll", "strtoul",
    "strtoull", "system", "wcstombs", "wctomb",
    /* <ctype.h> */
    "isalnum", "isalpha", "isblank", "iscntrl", "isdigit", "isgraph",
    "islower", "isprint", "ispunct", "isspace", "isupper", "isxdigit",
    "tolower", "toupper",
};

static bool is_libc_name(const char *s, size_t n)
{
    for (size_t i = 0; i < sizeof libc_names / sizeof libc_names[0]; i++)
        if (strlen(libc_names[i]) == n && !memcmp(libc_names[i], s, n))
            return true;
    return false;
}

/* The prefix placeholder's lead counts as an identifier byte, so `\x01q_x`
 * is one token and never a libc name. */
static bool ident_byte(unsigned char b)
{
    return b == '_' || b == PCREC_PREFIX_LEAD || (b >= '0' && b <= '9') ||
           ((b | 0x20) >= 'a' && (b | 0x20) <= 'z');
}

/* Index one past the string or character literal opening at `t[i]`. */
static size_t skip_literal(const char *t, size_t n, size_t i)
{
    char q = t[i++];
    while (i < n && t[i] != q) i += t[i] == '\\' ? 2 : 1;
    return i < n ? i + 1 : n;
}

/* Index one past the comment opening at `t[i]` (`/` then `*` or `/`). */
static size_t skip_comment(const char *t, size_t n, size_t i)
{
    if (t[i + 1] == '/') {
        while (i < n && t[i] != '\n') i++;
        return i;
    }
    for (i += 2; i + 1 < n; i++)
        if (t[i] == '*' && t[i + 1] == '/') return i + 2;
    return n;
}

static size_t skip_space(const char *t, size_t n, size_t i)
{
    while (i < n && (t[i] == ' ' || t[i] == '\t' || t[i] == '\n' ||
                     t[i] == '\\'))
        i++;
    return i;
}

/* THE RECORD'S ONE EXCLUSION (Q53): a `memcpy` whose length argument is an
 * integer literal of 1-8 is a register load, not a call. `t[i]` is the
 * call's `(`. A length the text spells any other way (a `sizeof`, a macro)
 * counts as a call; C11 reports the disagreement if the compile folds it. */
static bool memcpy_is_idiom(const char *t, size_t n, size_t i)
{
    int depth = 0, arg = 0;
    size_t len_at = 0, len_end = 0;
    for (i++; i < n; i++) {
        char ch = t[i];
        if (ch == '"' || ch == '\'') { i = skip_literal(t, n, i) - 1; continue; }
        if (ch == '(' || ch == '[' || ch == '{') depth++;
        else if ((ch == ')' || ch == ']' || ch == '}') && depth) depth--;
        else if (ch == ')') { if (arg == 2) len_end = i; break; }
        else if (ch == ',' && !depth && ++arg == 2) len_at = i + 1;
    }
    if (arg != 2 || !len_end) return false;
    len_at = skip_space(t, len_end, len_at);
    unsigned long v = 0;
    size_t d = len_at;
    while (d < len_end && t[d] >= '0' && t[d] <= '9') v = v * 10 + (unsigned)(t[d++] - '0');
    if (d == len_at) return false;
    while (d < len_end && strchr("uUlL", t[d])) d++;
    return skip_space(t, len_end, d) == len_end && v >= 1 && v <= 8;
}

/* Notes every libc function `t` calls: an identifier from `libc_names` in
 * call position (next token `(`, not a member after `.`/`->`), outside
 * comments and literals. Returns mf_art_note_libc's first failure. */
static int scan_libc_calls(mf_art *art, const char *t, size_t n)
{
    size_t i = 0;
    while (i < n) {
        char ch = t[i];
        if (ch == '/' && i + 1 < n && (t[i + 1] == '*' || t[i + 1] == '/')) {
            i = skip_comment(t, n, i);
            continue;
        }
        if (ch == '"' || ch == '\'') { i = skip_literal(t, n, i); continue; }
        if (!ident_byte((unsigned char)ch) || (ch >= '0' && ch <= '9')) {
            i++;
            continue;
        }
        size_t at = i;
        while (i < n && ident_byte((unsigned char)t[i])) i++;
        size_t paren = skip_space(t, n, i);
        if (paren >= n || t[paren] != '(' || !is_libc_name(t + at, i - at))
            continue;
        size_t b = at;
        while (b && (t[b - 1] == ' ' || t[b - 1] == '\t')) b--;
        if (b && (t[b - 1] == '.' || (t[b - 1] == '>' && b > 1 && t[b - 2] == '-')))
            continue;
        if (i - at == 6 && !memcmp(t + at, "memcpy", 6) && memcpy_is_idiom(t, n, paren))
            continue;
        char name[16];
        memcpy(name, t + at, i - at);
        name[i - at] = 0;
        if (mf_art_note_libc(art, name)) return -1;
    }
    return 0;
}

/* ---- the kit's view of pcrec's buffers ----------------------------------- */

typedef struct { StrBuf *sb; const char *upper; } StampSink;

static void sink_stamp(void *u, const char *name, const char *value)
{
    StampSink *s = u;
    pcrec_sb_stamp_str(s->sb, s->upper, name, value);
}

/* [MEMFN] M1b the UNQUOTED stamp (RULED Q-M1b-2): `RUN_WORDS` is an integer,
 * spelled exactly as pcrec's own run compare stamped it before M1b. */
static void sink_stamp_int(void *u, const char *name, long long value)
{
    StampSink *s = u;
    pcrec_sb_stampf(s->sb, s->upper, name, "%lld", value);
}

/* Replaces the one mark in `sb` with `text`; false if `sb` holds no mark or
 * more than one. */
static bool splice_mark(StrBuf *sb, const char *text)
{
    const char *m = sb->p ? strstr(sb->p, MEMFN_MARK) : NULL;
    if (!m || strstr(m + 1, MEMFN_MARK)) return false;
    size_t at = (size_t)(m - sb->p), cut = sizeof MEMFN_MARK - 1;
    StrBuf tail = { .cx = sb->cx };
    pcrec_sb_puts(&tail, sb->p + at + cut);
    sb->len = at;
    sb->p[at] = 0;
    pcrec_sb_puts(sb, text);
    pcrec_sb_puts(sb, tail.p ? tail.p : "");
    pcrec_sb_free(&tail);
    return true;
}

uint32_t pcrec_memfn_policy(uint64_t flags)
{
    return pcrec_axis_on(flags, PCREC_NO_MEMFN_SIMD, PCREC_FORCE_MEMFN_SIMD)
               ? 0u : MF_P_PORTABLE_ONLY;
}

/* The finishing pass (see the header). Reads `cx->job->csb` and `hsb`, the
 * finished artifact at the placeholder prefix; writes the three stamp lines
 * over csb's mark. Called once per attempt, after the engine emitter and
 * before anything measures the text. It ENDS the attempt's kit state
 * ([MEMFN] R4c): the art the emitters' sites were rendered through is the
 * one the libc record is noted on, and its end checks every defined site
 * was used (`pcrec_memfn_art_end`). */
void pcrec_memfn_stamps_render(Ctx *cx)
{
    Job *job = cx->job;
    mf_art *art = pcrec_memfn_art(cx);
    StrBuf lines = { .cx = cx };
    StampSink ss = { &lines, pcrec_sb_upper(&cx->arena, cx->opt->prefix) };
    mf_sink sink = { .u = &ss, .stamp = sink_stamp,
                     .stamp_int = sink_stamp_int };
    int rc = scan_libc_calls(art, job->csb.p ? job->csb.p : "", job->csb.len) ||
             scan_libc_calls(art, job->hsb.p ? job->hsb.p : "", job->hsb.len) ||
             mf_stamps(art, &sink);
    /* [MEMFN] RQ-3 (D155 addendum 2, "Reported"): pcrec's own line after the
     * kit's three, the artifact's CPU-guarded byte count in the decision
     * view's unit (uncut, so the comment axis cannot move it, and at the
     * prefix placeholder, so `-p` cannot). Every length decision subtracts
     * these bytes; this line is where the real size stays visible. Read from
     * the two finished buffers' records, which carry every spliced scratch
     * buffer's (pcrec_sb_splice).
     *
     * FIXED-WIDTH HEX, and the width is the point: this line is itself
     * emitted code the size decisions measure (it renders before the
     * measurement), so a decimal value would make the line one byte longer
     * per digit and leak the guarded count into every cap, knee and quoted
     * figure. Measured, not argued: the first build's witness moved
     * `--warn-emit-bytes`' quoted sizes by 6 bytes ("1620166" vs "0"). */
    if (!rc)
        pcrec_sb_stampf(&lines, ss.upper, "SIMD_GUARDED_BYTES", "0x%016llxULL",
                        (unsigned long long)(job->csb.simd_guarded +
                                             job->hsb.simd_guarded));
    bool ok = !rc && splice_mark(&job->csb, lines.p ? lines.p : "");
    pcrec_sb_free(&lines);
    if (rc)
        pcrec_ctx_fail(cx, 0, "internal error: the memfn kit refused the "
                       "artifact's stamps: %s", mf_art_error(art));
    if (!ok)
        pcrec_ctx_fail(cx, 0, "internal error: the artifact holds no single "
                       "memfn stamp mark (pcrec_emit_memfn_mark)");
    pcrec_memfn_art_end(cx, art);
}
