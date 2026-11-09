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
 * size measurement, so the size term measures the artifact it ships.
 *
 * [WINDOW-E1] RP, THE SECOND MARK KIND: pcrec's KNOWLEDGE stamps
 * (`<PREFIX>_FINDINGS` and its `.findings =` initializer; `_MEASURES` joins
 * at [MEASURE-SET] M0) render here too, at THE ONE RENDER POINT of
 * window_contract.md §3.7.3a: after `mf_art_end`, because from B3b on the
 * kit's consulted kinds join the stamp and the kit is then the last reader.
 * The `rx_info` writer marks each line at its byte position, so moving the
 * render here moved no byte. */
#include <stdlib.h>
#include <string.h>

#include "gen/memfn_sites.h"

/* The mark: a placeholder-lead byte that is not the prefix placeholder. */
#define MEMFN_MARK "\x01M\n"
/* The knowledge-stamp marks, one per line they stand for, indexed by
 * `PcrecKsMark`. The letter is not a hex digit, so `\x01` ends where it
 * should. */
static const char *const ks_marks[] = {
    [PCREC_KS_MARK_DEFINE] = "\x01K\n",
    [PCREC_KS_MARK_INIT]   = "\x01k\n",
};

void pcrec_emit_memfn_mark(StrBuf *c)
{
#ifdef PCREC_SIMD_WITNESS
    pcrec_memfn_simd_witness(c);   /* RQ-3's file-scope block, both engines */
#endif
    pcrec_sb_puts(c, MEMFN_MARK);
}

void pcrec_emit_ks_mark(StrBuf *c, PcrecKsMark m)
{
    pcrec_sb_puts(c, ks_marks[m]);
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
 * is one token and never a libc name. The scan runs on MARKED text (the
 * part-layout marks, `\x01L..`, are rendered later): a mark's lead and hex
 * digits read as identifier bytes too, which is harmless because a mark sits
 * after `static ` or on a line of its own, never inside a call name. */
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
    /* [COMPOUND] kept for a compound's union of its parts' forms */
    if (!strcmp(name, "MEMFN_FORMS"))
        s->sb->cx->job->memfn_forms = pcrec_sb_fragf(&s->sb->cx->arena, "%s", value);
}

/* [MEMFN] M1b the UNQUOTED stamp (RULED Q-M1b-2): `RUN_WORDS` is an integer,
 * spelled exactly as pcrec's own run compare stamped it before M1b. */
static void sink_stamp_int(void *u, const char *name, long long value)
{
    StampSink *s = u;
    pcrec_sb_stampf(s->sb, s->upper, name, "%lld", value);
}

/* How many times `mark` occurs in `sb`. */
static size_t mark_count(const StrBuf *sb, const char *mark)
{
    size_t n = 0;
    for (const char *m = sb->p ? strstr(sb->p, mark) : NULL; m; m = strstr(m + 1, mark))
        n++;
    return n;
}

/* Replaces the one `mark` in `sb` with `text`; false if `sb` holds no such
 * mark or more than one. */
static bool splice_mark(StrBuf *sb, const char *mark, const char *text)
{
    const char *m = sb->p ? strstr(sb->p, mark) : NULL;
    if (!m || strstr(m + 1, mark)) return false;
    size_t at = (size_t)(m - sb->p), cut = strlen(mark);
    StrBuf tail = { .cx = sb->cx };
    pcrec_sb_puts(&tail, sb->p + at + cut);
    sb->len = at;
    sb->p[at] = 0;
    pcrec_sb_puts(sb, text);
    pcrec_sb_puts(sb, tail.p ? tail.p : "");
    pcrec_sb_free(&tail);
    return true;
}

/* The queries the compile consulted, for its knowledge stamp (D167
 * addendum 3): this attempt's asks, every earlier attempt's
 * (`Ctx.find_union`) and, on a compound shell, every part's, because the
 * artifact's bytes depend on all of them (§3.7.3a item 4). */
static unsigned ks_consulted(Ctx *cx)
{
    unsigned q = pcrec_find_asked(cx) | (cx->find_union ? *cx->find_union : 0u);
    const PcrecCompShell *sh = cx->job->comp_shell;
    for (int i = 0; sh && i < PCREC_COMP_MAXPARTS; i++)
        if (sh->text[i]) q |= sh->facts[i].find_consulted;
    return q;
}

/* [MEASURE-SET] M0 the `<PREFIX>_MEASURES` value (measure_sets.md §3.5):
 * the set the kit was handed, `id@rev:digest16`, iff a reader CONSULTED it —
 * the kit's `consulted` (R-MS2), on this attempt, any earlier one
 * (`Ctx.meas_union`) or a compound part — and "" otherwise. pcrec has no
 * reader of its own before M4, so the kit's boolean is the whole OR today.
 * Its content was fixed when the set loaded (stamp-on-load). */
static const char *meas_stamp(Ctx *cx)
{
    const mf_measures *ms = cx->job->mf_ms;
    bool consulted = cx->job->meas_consulted || (cx->meas_union && *cx->meas_union);
    const PcrecCompShell *sh = cx->job->comp_shell;
    for (int i = 0; sh && i < PCREC_COMP_MAXPARTS; i++)
        if (sh->text[i]) consulted = consulted || sh->facts[i].meas_consulted;
    if (!consulted) return "";
    if (!ms)
        pcrec_ctx_fail(cx, 0, "internal error: the measurement set was consulted "
                       "but the attempt handed the kit none");
    return pcrec_sb_fragf(&cx->arena, "%s@%u:%s", ms->id, ms->rev, ms->values_digest);
}

/* [WINDOW-E1] RP: renders pcrec's knowledge stamps over the `rx_info`
 * writer's marks in csb, each line's text `pcrec_emit_findings_line`'s and
 * the value `pcrec_find_stamp`'s over `ks_consulted`, read now, after every
 * reader. An artifact
 * that omits `rx_info` (an entry request) holds neither mark; one that has
 * it holds each exactly once, and anything else is an internal error. */
static void ks_stamps_render(Ctx *cx)
{
    StrBuf *c = &cx->job->csb;
    size_t nd = mark_count(c, ks_marks[PCREC_KS_MARK_DEFINE]);
    size_t ni = mark_count(c, ks_marks[PCREC_KS_MARK_INIT]);
    if (nd != ni || nd > 1)
        pcrec_ctx_fail(cx, 0, "internal error: the artifact holds %zu findings "
                       "stamp marks and %zu initializer marks (pcrec_emit_ks_mark)",
                       nd, ni);
    if (!nd) return;
    const char *value = pcrec_find_stamp(cx, ks_consulted(cx));
    const char *meas = meas_stamp(cx);
    for (size_t m = 0; m < sizeof ks_marks / sizeof ks_marks[0]; m++) {
        StrBuf line = { .cx = cx };
        pcrec_emit_findings_line(cx, &line, (PcrecKsMark)m, value);
        pcrec_emit_measures_line(cx, &line, (PcrecKsMark)m, meas);
        (void)splice_mark(c, ks_marks[m], line.p ? line.p : "");
        pcrec_sb_free(&line);
    }
}

/* [XARCH-DEV] U3 renders the target headers over their mark in csb
 * (`pcrec_emit_target_headers_mark`): the text `pcrec_memfn_target_headers`
 * names, read now, after the last emit, from the prologue ahead of the mark
 * and the lines held inside the region (`pcrec_emit_include_line`). The mark
 * sat in its own bracket, so the text takes over its guarded record (both
 * counts and the caps breakdown move by the difference) and no length
 * decision ever read either: a header owed only for a target is beyond the
 * SIMD-off compile. A part carries no mark; any other artifact exactly one.
 * Each held line goes with its mark, whose bracket record goes with it, so
 * the region keeps no `#include`. */
static void target_headers_render(Ctx *cx)
{
    StrBuf *c = &cx->job->csb;
    size_t nm = mark_count(c, PCREC_TARGET_HEADERS_MARK);
    if (nm != (pcrec_is_part(cx) ? 0u : 1u))
        pcrec_ctx_fail(cx, 0, "internal error: the artifact holds %zu target "
                       "header marks (pcrec_emit_target_headers_mark)", nm);
    if (!nm) return;
    const char *held = PCREC_HELD_HEADER_MARK;
    size_t at = (size_t)(strstr(c->p, PCREC_TARGET_HEADERS_MARK) - c->p);
    const char *after = c->p + at + strlen(PCREC_TARGET_HEADERS_MARK);
    /* pass 1: the held lines, in text order */
    StrBuf lines = { .cx = cx };
    size_t nheld = 0;
    for (const char *h = strstr(after, held); h; h = strstr(h + 1, held)) {
        const char *line = h + strlen(held), *eol = strchr(line, '\n');
        if (!eol)
            pcrec_ctx_fail(cx, 0, "internal error: a held header mark ends "
                           "the artifact (pcrec_emit_include_line)");
        pcrec_sb_printf(&lines, "%.*s", (int)(eol + 1 - line), line);
        nheld++;
    }
    const char *text = pcrec_memfn_target_headers(cx, c->p, at, lines.p ? lines.p : "");
    pcrec_sb_free(&lines);
    PcrecEmitSize was = pcrec_emit_size_measure(PCREC_TARGET_HEADERS_MARK,
                                                strlen(PCREC_TARGET_HEADERS_MARK), NULL);
    PcrecEmitSize now = pcrec_emit_size_measure(text, strlen(text), NULL);
    PcrecEmitSize hm = pcrec_emit_size_measure(held, strlen(held), NULL);
    /* pass 2, rebuilt in a fresh buffer, never truncated and re-appended in
     * place: the mark sits near the top, and a truncated csb under a ladder
     * trial's scratch bound would read a length below its own guarded record */
    StrBuf nb = { .cx = cx };
    pcrec_sb_printf(&nb, "%.*s%s", (int)at, c->p, text);
    const char *rest = after;
    for (const char *h; (h = strstr(rest, held)); ) {
        pcrec_sb_printf(&nb, "%.*s", (int)(h - rest), rest);
        rest = strchr(h + strlen(held), '\n') + 1;
    }
    pcrec_sb_puts(&nb, rest);
    free(c->p);
    c->p = nb.p;
    c->len = nb.len;
    c->cap = nb.cap;
    c->simd_guarded += strlen(text) - strlen(PCREC_TARGET_HEADERS_MARK)
                     - nheld * strlen(held);
    c->simd_size.total += now.total - was.total - nheld * hm.total;
    c->simd_size.prose += now.prose - was.prose - nheld * hm.prose;
    c->simd_size.tables += now.tables - was.tables - nheld * hm.tables;
}

/* The finishing pass (see the header). Reads `cx->job->csb` and `hsb`, the
 * finished artifact at the placeholder prefix; writes the three stamp lines
 * over csb's mark. Called once per attempt, after the engine emitter and
 * before anything measures the text. It ENDS the attempt's kit state
 * ([MEMFN] R4c): the art the emitters' sites were rendered through is the
 * one the libc record is noted on, and its end checks every defined site
 * was used (`pcrec_memfn_art_end`). Then, after `mf_art_end`, pcrec's own
 * knowledge stamps render over their marks ([WINDOW-E1] RP, §3.7.3a): the
 * order is libc scan, `mf_stamps`, the kit lines' splice, `mf_art_end`,
 * the knowledge stamps. (The kit lines splice BEFORE `mf_art_end`, so no
 * buffer is held across a call that can refuse; nothing they carry depends
 * on the kit's end.) */
void pcrec_memfn_stamps_render(Ctx *cx)
{
    Job *job = cx->job;
    mf_art *art = pcrec_memfn_art(cx);
    target_headers_render(cx);
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
    /* a spliced part's held marks (`pcrec_emit_include_line`) are bracketed
     * only so no decision reads them; its shell takes them out, so its count
     * leaves them out (none remain in a shell's text by now) */
    size_t held = mark_count(&job->csb, PCREC_HELD_HEADER_MARK) *
                  strlen(PCREC_HELD_HEADER_MARK);
    if (!rc)
        pcrec_sb_stampf(&lines, ss.upper, "SIMD_GUARDED_BYTES", "0x%016llxULL",
                        (unsigned long long)(job->csb.simd_guarded +
                                             job->hsb.simd_guarded - held));
    bool ok = !rc && splice_mark(&job->csb, MEMFN_MARK, lines.p ? lines.p : "");
    pcrec_sb_free(&lines);
    if (rc)
        pcrec_ctx_fail(cx, 0, "internal error: the memfn kit refused the "
                       "artifact's stamps: %s", mf_art_error(art));
    if (!ok)
        pcrec_ctx_fail(cx, 0, "internal error: the artifact holds no single "
                       "memfn stamp mark (pcrec_emit_memfn_mark)");
    /* R17-b' B2 (R-MS6): under the harness lever, the arm-entry counter's
       definitions at the artifact's end, after every use (nothing without it) */
    if (cx->emit_in && cx->emit_in->harness && cx->emit_in->harness->arm_reach) {
        PcrecMfSink ps;
        pcrec_memfn_sink(&ps, &job->csb);
        if (mf_reach_table(art, &ps.s))
            pcrec_ctx_fail(cx, 0, "internal error: the memfn kit refused the arm-entry "
                           "counter's table: %s", mf_art_error(art));
    }
    pcrec_memfn_art_end(cx, art);
    /* §3.3 rule 9's refusal (an underivable kind a kit row consulted) has no
       case before B3b: no routed kit row consults a kind yet */
    ks_stamps_render(cx);
}
