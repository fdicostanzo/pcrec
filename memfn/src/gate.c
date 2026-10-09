/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/gate.c — THE ROW-CONTRACT GATE ([MEMFN-ROWCON] N1, enforcing
 * since N3; docs/design/memfn/row_contracts.md §2-§5): the classify
 * functions of fields.def, the gate's per-field rules over a row's
 * `uses`/`serves`, the one text every refusal names its fields with
 * (`gate_describe`), and, under the compile-time switch MF_TRACE, the
 * `MFTRACE` selection records and reach counters
 * (memfn/docs/trace_format.md).
 *
 * The gate answers, for one row at one phase, which fields would make it
 * DECLINE. Per field the phase reads, the first rule that matches:
 *   1. the row USES it and it is UNSTATED:     DECLINE (R1);
 *   2. it is STATED and the row does not SERVE
 *      its class:                               DECLINE (R2);
 *   3. otherwise:                               pass.
 * Since N3 it ENFORCES (row_contracts.md §5). Its callers act on the ONE
 * verdict this file computes: the two selection walks (compose.c
 * `select_arm`, runcmp.c `rc_row_of`) DECLINE a failing row before its
 * predicate and move on, and refuse the site, naming the fields, when no row
 * is left; `mf_use` re-checks the chosen row against the use hooks and
 * refuses a failing use, naming the fields (it cannot re-select: the
 * definition is written).
 *
 * MF_TRACE (off by default) is a scratch-build switch: its records go to
 * stderr and its counters are process-wide, not per-art, so a trace build is
 * neither quiet nor re-entrant. Nothing it writes reaches an artifact.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "kit.h"

/* ---- lexical text shapes ------------------------------------------------- */

/* 1 iff `c` may appear in a C identifier. */
static int ident_char(char c)
{
    return c == '_' || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')
        || (c >= '0' && c <= '9');
}

int kit_is_ident(const char *s)
{
    if (!s || !*s || (*s >= '0' && *s <= '9')) return 0;
    for (; *s; s++)
        if (!ident_char(*s)) return 0;
    return 1;
}

static int is_space(char c)
{
    return c == ' ' || c == '\t' || c == '\n' || c == '\r';
}

/* The text between `s`'s leading and trailing white space: *b and the
 * length. */
static size_t trim(const char *s, const char **b)
{
    while (is_space(*s)) s++;
    size_t n = strlen(s);
    while (n && is_space(s[n - 1])) n--;
    *b = s;
    return n;
}

/* 1 iff `p[0..n)` holds a quote or a comment opener: text whose braces and
 * semicolons a lexical check cannot count, so it is OTHER. */
static int opaque(const char *p, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        if (p[i] == '"' || p[i] == '\'') return 1;
        if (p[i] == '/' && i + 1 < n && (p[i + 1] == '*' || p[i + 1] == '/')) return 1;
    }
    return 0;
}

/* JUMP: `return ...;` or `goto label;`, one statement (its one `;` last, no
 * brace). BRACED: one `{ ... }` block (the opening brace's depth returns to
 * 0 only at the last byte). LOOP_EXIT (Q-R7-3): exactly `break;`, white space
 * inside allowed, nothing else (a `continue;` or a labelled jump is OTHER).
 * Anything else, or text a lexical check cannot count, is OTHER. */
static int stmt_shape(const char *text)
{
    const char *p;
    size_t n = trim(text, &p);
    if (!n || opaque(p, n)) return CL_OTHER;
    if (n >= 6 && !strncmp(p, "break", 5)) {
        size_t i = 5;
        while (i < n && is_space(p[i])) i++;
        if (i + 1 == n && p[i] == ';') return CL_LOOP_EXIT;
    }
    if (p[0] == '{' && p[n - 1] == '}') {
        int depth = 0;
        for (size_t i = 0; i < n; i++) {
            depth += p[i] == '{' ? 1 : p[i] == '}' ? -1 : 0;
            if (depth == 0 && i + 1 < n) return CL_OTHER;
            if (depth < 0) return CL_OTHER;
        }
        return CL_BRACED;
    }
    int ret = n >= 6 && !strncmp(p, "return", 6) && !ident_char(p[6]);
    int jmp = n >= 5 && !strncmp(p, "goto", 4) && is_space(p[4]);
    if (!ret && !jmp) return CL_OTHER;
    for (size_t i = 0; i < n; i++)
        if (p[i] == '{' || p[i] == '}' || (p[i] == ';' && i + 1 < n)) return CL_OTHER;
    return p[n - 1] == ';' ? CL_JUMP : CL_OTHER;
}

/* The ADVANCE hooks' shapes (G3, R4h prep): CONJ, POSTFIX, EXPR_STMT. Each
 * is a LEXICAL check over the trimmed text, conservative by construction:
 * whatever it cannot prove is OTHER. Brackets are ( and [; a brace, a quote
 * or a comment opener is OTHER everywhere (opaque or a block). */

/* 1 iff p[0..n) is bracket-balanced over ( and [, with no brace and no `;`
 * anywhere and no closer before its opener. */
static int balanced(const char *p, size_t n)
{
    int depth = 0;
    for (size_t i = 0; i < n; i++) {
        char c = p[i];
        if (c == '{' || c == '}' || c == ';') return 0;
        if (c == '(' || c == '[') depth++;
        if (c == ')' || c == ']') depth--;
        if (depth < 0) return 0;
    }
    return depth == 0;
}

/* 1 iff the `(` at p[i] (depth 0) follows an identifier character, white
 * space between allowed: a call, or a function-like macro, whose expansion
 * a lexical check cannot see. */
static int is_call(const char *p, size_t i)
{
    while (i && is_space(p[i - 1])) i--;
    return i && ident_char(p[i - 1]);
}

/* CONJ: usable as an `&&` operand with no parentheses. Every top-level
 * operator binds at least as tightly as `&&` (`&&` itself is associative in
 * value and order), so: no top-level `||`, `?`, `:`, `,` or assignment
 * (`=` not in `==`, `!=`, `<=`, `>=`; `<<=`/`>>=` are assignments), no
 * top-level call, and the text neither starts with a binary-only operator
 * nor ends with an operator. */
static int conj_shape(const char *text)
{
    const char *p;
    size_t n = trim(text, &p);
    if (!n || opaque(p, n) || !balanced(p, n)) return CL_OTHER;
    if (strchr("|^<>=/%?:.,", p[0]) || (n >= 2 && p[0] == '&' && p[1] == '&'))
        return CL_OTHER;
    char last = p[n - 1];
    if (!ident_char(last) && last != ')' && last != ']') return CL_OTHER;
    int depth = 0;
    for (size_t i = 0; i < n; i++) {
        char c = p[i];
        if (c == '(' && depth == 0 && is_call(p, i)) return CL_OTHER;
        if (c == '(' || c == '[') { depth++; continue; }
        if (c == ')' || c == ']') { depth--; continue; }
        if (depth) continue;
        if (c == '?' || c == ':' || c == ',') return CL_OTHER;
        if (c == '|' && i + 1 < n && p[i + 1] == '|') return CL_OTHER;
        if (c == '=') {
            if (i + 1 < n && p[i + 1] == '=') { i++; continue; }   /* == */
            char b = i ? p[i - 1] : 0;
            if (b == '!') continue;                                 /* != */
            if ((b == '<' || b == '>') && !(i >= 2 && p[i - 2] == b))
                continue;                                           /* <= >= */
            return CL_OTHER;                                        /* an assignment */
        }
    }
    return CL_CONJ;
}

/* The end of the bracketed group opening at p[i] (( or [), one past its
 * closer, or 0 when it does not close inside p[0..n). */
static size_t group_end(const char *p, size_t n, size_t i)
{
    int depth = 0;
    for (; i < n; i++) {
        if (p[i] == '(' || p[i] == '[') depth++;
        if (p[i] == ')' || p[i] == ']') depth--;
        if (depth == 0) return i + 1;
    }
    return 0;
}

/* POSTFIX: a primary expression (an identifier, or one parenthesized
 * expression), then only `[...]`, `.ident` and `->ident` suffixes, with no
 * white space outside the brackets and no `++`/`--` anywhere: usable as any
 * operator's operand with no parentheses. A call suffix is OTHER (a macro). */
static int postfix_shape(const char *text)
{
    const char *p;
    size_t n = trim(text, &p);
    if (!n || opaque(p, n) || !balanced(p, n)) return CL_OTHER;
    for (size_t i = 0; i + 1 < n; i++)
        if ((p[i] == '+' || p[i] == '-') && p[i + 1] == p[i]) return CL_OTHER;
    size_t i = 0;
    if (p[0] == '(') {
        if (!(i = group_end(p, n, 0))) return CL_OTHER;
    } else if (ident_char(p[0]) && !(p[0] >= '0' && p[0] <= '9')) {
        while (i < n && ident_char(p[i])) i++;
    } else {
        return CL_OTHER;
    }
    while (i < n) {
        if (p[i] == '[') {
            if (!(i = group_end(p, n, i))) return CL_OTHER;
            continue;
        }
        size_t at = p[i] == '.' ? i + 1
                  : p[i] == '-' && i + 1 < n && p[i + 1] == '>' ? i + 2 : 0;
        if (!at || at >= n || !ident_char(p[at]) || (p[at] >= '0' && p[at] <= '9'))
            return CL_OTHER;
        for (i = at; i < n && ident_char(p[i]); i++) {}
    }
    return CL_POSTFIX;
}

/* The C keywords that lead a statement other than an expression statement,
 * or a declaration. */
static const char *const stmt_keywords[] = {
    "if", "else", "for", "while", "do", "switch", "return", "goto", "break",
    "continue", "case", "default", "typedef", "static", "extern", "register",
    "auto", "const", "volatile", "struct", "union", "enum", "void", "char",
    "short", "int", "long", "float", "double", "signed", "unsigned", "_Bool",
    "inline", "__attribute__", "asm", "__asm__", NULL,
};

/* EXPR_STMT: one expression statement, `e` or `e;`: the trimmed text with at
 * most one trailing `;` is non-empty, balanced, holds no other `;`, no
 * brace, no top-level `,`, `?` or `:`, and is not led by a keyword. */
static int expr_stmt_shape(const char *text)
{
    const char *p;
    size_t n = trim(text, &p);
    if (n && p[n - 1] == ';') {
        n--;
        while (n && is_space(p[n - 1])) n--;
    }
    if (!n || opaque(p, n) || !balanced(p, n)) return CL_OTHER;
    size_t w = 0;
    while (w < n && ident_char(p[w])) w++;
    for (unsigned k = 0; w && stmt_keywords[k]; k++)
        if (strlen(stmt_keywords[k]) == w && !strncmp(p, stmt_keywords[k], w))
            return CL_OTHER;
    int depth = 0;
    for (size_t i = 0; i < n; i++) {
        char c = p[i];
        if (c == '(' || c == '[') depth++;
        else if (c == ')' || c == ']') depth--;
        else if (!depth && (c == ',' || c == '?' || c == ':')) return CL_OTHER;
    }
    return CL_EXPR_STMT;
}

/* The MISMATCH fold text's shape (M7, MF_SITE_ABI 7): FOLD_EXPR or FOLD_STMT,
 * else OTHER. Unlike the shapes above it reads THROUGH quoted literals (an
 * ASCII fold compares with 'A' and 'Z'), skipping each one, escapes included,
 * and treats a comment opener as OTHER. Outside the literals the text must
 * hold `@`, be balanced over ( [ { and close no group before opening it.
 * FOLD_EXPR: no `;`, `{` or `}` outside a literal (one expression). FOLD_STMT:
 * its last byte outside white space is `;` or `}` (statements). An
 * unterminated literal is OTHER. */
static int fold_shape(const char *text)
{
    const char *p;
    size_t n = trim(text, &p);
    int depth = 0, at = 0, semi = 0, brace = 0;
    for (size_t i = 0; i < n; i++) {
        char c = p[i];
        if (c == '\'' || c == '"') {
            size_t j = i + 1;
            while (j < n && p[j] != c) j += p[j] == '\\' ? 2 : 1;
            if (j >= n) return CL_OTHER;
            i = j;
            continue;
        }
        if (c == '/' && i + 1 < n && (p[i + 1] == '*' || p[i + 1] == '/')) return CL_OTHER;
        if (c == '@') at = 1;
        if (c == ';') semi = 1;
        if (c == '{' || c == '}') brace = 1;
        if (c == '(' || c == '[' || c == '{') depth++;
        if (c == ')' || c == ']' || c == '}') depth--;
        if (depth < 0) return CL_OTHER;
    }
    if (!n || !at || depth) return CL_OTHER;
    if (!semi && !brace) return CL_FOLD_EXPR;
    return p[n - 1] == ';' || p[n - 1] == '}' ? CL_FOLD_STMT : CL_OTHER;
}

int kit_stmt_shape(const char *text) { return stmt_shape(text); }
int kit_fold_shape(const char *text) { return fold_shape(text); }

/* ---- the classify functions (fields.def's `classify` column) ------------- *
 *
 * Each returns the class of the field's value in `in`, or -1 where the value
 * is UNSTATED (a NULL hook, or no hooks at all). A site field is never
 * unstated; read off a gate_in with no site (the run walk), it is OTHER. */

static int flag01(unsigned v)
{
    return v == 0 ? CL_NO : v == 1 ? CL_YES : CL_OTHER;
}

/* The direction of predicate `p`'s reads: BACK if a term sits below the
 * candidate, NONNEG if none does, OTHER for a malformed term count. */
static int pred_dir(const mf_pred *p)
{
    if (p->nterm == 0 || p->nterm > MF_MAX_TERM) return CL_OTHER;
    for (unsigned t = 0; t < p->nterm; t++)
        if (p->term[t].offset < 0) return CL_BACK;
    return CL_NONNEG;
}

/* 1 iff some SET term of predicate `p` names a table. */
static int pred_tabled(const mf_pred *p)
{
    for (unsigned t = 0; t < p->nterm && t < MF_MAX_TERM; t++)
        if (p->term[t].kind == MF_T_SET && p->term[t].table_ref) return 1;
    return 0;
}

static int cl_form(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    switch (in->s->form) {
    case MF_FORM_EXPR: return CL_EXPR;
    case MF_FORM_STMT: return CL_STMT;
    case MF_FORM_FUNC: return CL_FUNC;
    }
    return CL_OTHER;
}

static int cl_op(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    switch (in->s->op) {
    case MF_OP_FIND:        return CL_FIND;
    case MF_OP_SKIP:        return CL_SKIP;
    case MF_OP_VERIFY:      return CL_VERIFY;
    case MF_OP_ALL_PRESENT: return CL_ALL_PRESENT;
    case MF_OP_MISMATCH:    return CL_MISMATCH;
    }
    return CL_OTHER;
}

static int cl_handoff(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    switch (in->s->handoff) {
    case MF_H_RETURN:  return CL_RETURN;
    case MF_H_ASSIGN:  return CL_ASSIGN;
    case MF_H_ON_MISS: return CL_ON_MISS;
    case MF_H_ADVANCE: return CL_ADVANCE;
    case MF_H_ON_CAND: return CL_ON_CAND;
    case MF_H_BOOL:    return CL_BOOL;
    case MF_H_ON_DIFF: return CL_ON_DIFF;
    }
    return CL_OTHER;
}

static int cl_reverse(const gate_in *in)
{
    return in->s ? flag01(in->s->reverse) : CL_OTHER;
}

static int cl_empty(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    switch (in->s->empty) {
    case MF_EMPTY_MISS:     return CL_E_MISS;
    case MF_EMPTY_NOP:      return CL_E_NOP;
    case MF_EMPTY_EXCLUDED: return CL_E_EXCLUDED;
    case MF_EMPTY_AT_N:     return CL_E_AT_N;
    }
    return CL_OTHER;
}

static int cl_end_back(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    return in->s->end_back == 0 ? CL_ZERO : in->s->end_back == 1 ? CL_ONE : CL_OTHER;
}

static int cl_pred(const gate_in *in)
{
    return in->s ? pred_dir(&in->s->pred) : CL_OTHER;
}

static int cl_preds(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    if (in->s->npred == 0) return CL_NONE;
    if (!in->s->preds) return CL_OTHER;
    int dir = CL_NONNEG;
    for (unsigned i = 0; i < in->s->npred; i++) {
        int d = pred_dir(&in->s->preds[i]);
        if (d == CL_OTHER) return CL_OTHER;
        if (d == CL_BACK) dir = CL_BACK;
    }
    return dir;
}

static int cl_ret_pred(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    if (in->s->ret_pred == MF_NO_PRED) return CL_NONE;
    return in->s->ret_pred < in->s->npred ? CL_PRED : CL_OTHER;
}

static int cl_guard_by_caller(const gate_in *in)
{
    return in->s ? flag01(in->s->guard_by_caller) : CL_OTHER;
}

static int cl_on_miss_leaves(const gate_in *in)
{
    return in->s ? flag01((unsigned)in->s->on_miss_leaves) : CL_OTHER;
}

static int cl_span_hi(const gate_in *in)
{
    return in->s && in->s->span_hi == MF_SPAN_UNBOUNDED ? CL_UNBOUNDED : CL_OTHER;
}

static int cl_denies(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    return in->s->denies == 0 ? CL_NONE
         : in->s->denies == MF_D_RUN_OVERLAP ? CL_RUN_OVERLAP : CL_OTHER;
}

/* A hook ID, like the hooks themselves: 0 is UNSTATED (N3, K-1). It is
 * `site.pred.fn_ref` for every op: a FUNC site's own name (memfn.h). */
static int cl_fn_ref(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    return in->s->pred.fn_ref ? CL_REF : -1;
}

static int cl_table_ref(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    if (pred_tabled(&in->s->pred)) return CL_REF;
    for (unsigned i = 0; in->s->preds && i < in->s->npred; i++)
        if (pred_tabled(&in->s->preds[i])) return CL_REF;
    return CL_NONE;
}

/* A MISMATCH's fold fact (M7): its class there; on any other site it is no
 * field of the site's (site_check refuses a nonzero one), so it reads as
 * unstated and no row need serve it. */
static int cl_fold_kind(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    if (in->s->op != MF_OP_MISMATCH) return -1;
    switch (in->s->fold_kind) {
    case MF_FOLD_NONE:  return CL_F_NONE;
    case MF_FOLD_ASCII: return CL_F_ASCII;
    case MF_FOLD_UCP:   return CL_F_UCP;
    }
    return CL_OTHER;
}

/* ADVANCE's step in positions (RULED Q-R10-2, MF_SITE_ABI 8): ONE, or MANY
 * for a strided site, OTHER for a term count outside 1..MF_MAX_TERM. Off
 * ADVANCE the term count is no step, so it reads as unstated and no row
 * need serve it. */
static int cl_stride(const gate_in *in)
{
    if (!in->s) return CL_OTHER;
    if (in->s->handoff != MF_H_ADVANCE) return -1;
    unsigned w = in->s->pred.nterm;
    return w == 1 ? CL_ONE : w >= 2 && w <= MF_MAX_TERM ? CL_MANY : CL_OTHER;
}

/* `s`, `n`, `lo`: IDENT iff a bare identifier. */
static int ident_or_other(const char *text)
{
    if (!text) return -1;
    return kit_is_ident(text) ? CL_IDENT : CL_OTHER;
}

static int cl_s(const gate_in *in)  { return ident_or_other(in->h ? in->h->s : NULL); }
static int cl_n(const gate_in *in)  { return ident_or_other(in->h ? in->h->n : NULL); }
static int cl_lo(const gate_in *in) { return ident_or_other(in->h ? in->h->lo : NULL); }
static int cl_ref(const gate_in *in)    { return ident_or_other(in->h ? in->h->ref : NULL); }
static int cl_reflen(const gate_in *in) { return ident_or_other(in->h ? in->h->reflen : NULL); }
static int cl_cursor(const gate_in *in) { return ident_or_other(in->h ? in->h->cursor : NULL); }

/* The fold text: its shape, but OTHER wherever the site's fact says there is
 * no fold (fold_kind NONE, which every non-MISMATCH site has): a fold stated
 * against the fact is a value no row serves, so it is refused, naming it. */
static int cl_fold(const gate_in *in)
{
    if (!in->h || !in->h->fold) return -1;
    if (!in->s || in->s->fold_kind == MF_FOLD_NONE) return CL_OTHER;
    return fold_shape(in->h->fold);
}

static int cl_floor(const gate_in *in)
{
    if (!in->h || !in->h->floor) return -1;
    return strcmp(in->h->floor, "0") ? CL_OTHER : CL_ZERO;
}

/* The MF_MISS_N token (memfn.h): defined here, beside its classifier. */
const char mf_miss_n[] = "\x01mfN";

static int cl_miss(const gate_in *in)
{
    if (!in->h || !in->h->miss) return -1;
    if (in->h->miss == MF_MISS_N) return CL_MISS_N;
    return in->h->n && !strcmp(in->h->miss, in->h->n) ? CL_MISS_N : CL_OTHER;
}

static int cl_on_miss(const gate_in *in)
{
    if (!in->h || !in->h->on_miss) return -1;
    return stmt_shape(in->h->on_miss);
}

static int cl_count_by_caller(const gate_in *in)
{
    return in->s ? flag01(in->s->count_by_caller) : CL_OTHER;
}

/* The ADVANCE hooks: their shape class, -1 for unstated. */
static int cl_more(const gate_in *in)
{
    return in->h && in->h->more ? conj_shape(in->h->more) : -1;
}

static int cl_peek(const gate_in *in)
{
    return in->h && in->h->peek ? postfix_shape(in->h->peek) : -1;
}

static int cl_step(const gate_in *in)
{
    return in->h && in->h->step ? expr_stmt_shape(in->h->step) : -1;
}

static int cl_count_start(const gate_in *in)
{
    if (!in->h) return -1;
    return in->h->count_start ? CL_OTHER : CL_ZERO;
}

static int cl_on_cand_reach(const gate_in *in)
{
    if (!in->h) return -1;
    return in->h->on_cand_reach ? CL_OTHER : CL_ZERO;
}

static int cl_comment_tier(const gate_in *in)
{
    return in->h ? CL_OTHER : -1;
}

/* A text or op hook with no shape classes: OTHER iff stated (not NULL).
 * One definition per field, so fields.def's classify column names each. */
#define HOOK_STATED(field) \
    static int cl_##field(const gate_in *in) \
    { return in->h && in->h->field ? CL_OTHER : -1; }
HOOK_STATED(result)
HOOK_STATED(result_decl)
HOOK_STATED(count)
HOOK_STATED(on_cand)
HOOK_STATED(member)
HOOK_STATED(table_name)
HOOK_STATED(fn_name)
HOOK_STATED(note)
HOOK_STATED(note_tag)
HOOK_STATED(indent)
#undef HOOK_STATED

static int cl_run(const gate_in *in)
{
    const mf_term *t = in->t;
    if (!t || t->kind != MF_T_RUN || !t->run || t->run_len == 0) return CL_OTHER;
    if (!t->mask) return CL_EXACT;
    int masked = 0;
    for (uint32_t j = 0; j < t->run_len; j++) {
        if (t->run[j] & ~t->mask[j] & 0xFF) return CL_UNSAT;
        if (t->mask[j] != 0xFF) masked = 1;
    }
    return masked ? CL_MASKED : CL_EXACT;
}

static int cl_run_len(const gate_in *in)
{
    if (!in->t || in->t->run_len == 0) return CL_OTHER;
    return in->t->run_len == 1 ? CL_ONE : CL_MANY;
}

/* ---- the table ----------------------------------------------------------- */

typedef struct {
    const char *name;
    unsigned    phase;
    int       (*classify)(const gate_in *);
    uint64_t    classes;
} field_row;

#define MF_FIELD(name, phase, absent, classify, classes, doc) \
    { #name, phase, classify, classes },
static const field_row fields[FLD_N] = {
#include "fields.def"
};
#undef MF_FIELD


/* The class of field `f` in `in`, closed over the field's set (a classify
 * that returned a class outside it reads OTHER); -1 for unstated. */
static int class_of(unsigned f, const gate_in *in)
{
    int k = fields[f].classify(in);
    if (k >= 0 && !(fields[f].classes >> k & 1)) k = CL_OTHER;
    return k;
}

/* The fields the row USES at `phase` on the site `in` describes: the union
 * of its `uses` entries whose form and handoff hold the site's classes and
 * whose condition, if any, holds (an unstated condition field holds none). */
static uint64_t uses_at(const gate_contract *c, unsigned phase, const gate_in *in)
{
    uint64_t f = 0;
    int form = cl_form(in), handoff = cl_handoff(in);
    for (unsigned i = 0; i < c->nuses; i++) {
        const gate_use *u = &c->uses[i];
        if (!(u->phases & phase) || !(u->forms >> form & 1) || !(u->handoffs >> handoff & 1))
            continue;
        if (u->when_cls) {
            int k = u->when_fld < FLD_N ? class_of(u->when_fld, in) : -1;
            if (k < 0 || !(u->when_cls >> k & 1)) continue;
        }
        f |= u->fields;
    }
    return f;
}

gate_verdict gate_check(const gate_contract *c, unsigned phase, const gate_in *in)
{
    gate_verdict v = { 0, 0 };
    uint64_t uses = uses_at(c, phase, in);
    for (unsigned f = 0; f < FLD_N; f++) {
        if (!(fields[f].phase & phase)) continue;
        int k = class_of(f, in);
        if (k < 0) {
            if (uses >> f & 1) v.r1 |= 1ull << f;
        } else if (!(c->serves[f] >> k & 1)) {
            v.r2 |= 1ull << f;
        }
    }
    return v;
}

/* ---- the refusal text ---------------------------------------------------- */

static const char *const class_names[CL_N] = {
#define MF_CLASS(name, doc) #name,
#include "fields.def"
#undef MF_CLASS
};

/* `f` (R1: used, not stated) and `g` (R2: stated as CLASS, not served), one
 * per field the verdict declines, in fields.def order, comma-joined, into
 * buf[0..n): every gate refusal names its fields with this (ruling (d)). The
 * field names are backquoted, as the kit's other refusals spell a hook. */
void gate_describe(char *buf, size_t n, const gate_verdict *v, const gate_in *in)
{
    size_t at = 0;
    if (n) buf[0] = '\0';
    for (unsigned f = 0; f < FLD_N && at < n; f++) {
        int w = 0;
        const char *sep = at ? ", " : "";
        if (v->r1 >> f & 1)
            w = snprintf(buf + at, n - at, "%s`%s` (R1: used, not stated)", sep,
                         fields[f].name);
        else if (v->r2 >> f & 1)
            w = snprintf(buf + at, n - at, "%s`%s` (R2: stated as %s, not served)", sep,
                         fields[f].name, class_names[class_of(f, in)]);
        if (w > 0) at += (size_t)w;
    }
}

/* ---- MF_TRACE: the records and the reach counters ------------------------ */

#ifdef MF_TRACE

/* Process-wide on purpose (trace builds only): the reach is summed over
 * every art one process renders, and printed once at exit. */
enum { REACH_ROWS = 16 };
static const gate_contract *reach_row[REACH_ROWS];
static unsigned long reach_chosen[REACH_ROWS];
static unsigned long reach_cell[REACH_ROWS][FLD_N][CL_N + 1];   /* CL_N: unstated */
static unsigned long reach_dropped;  /* ENDs whose row found no slot (N4: K35) */
static unsigned trace_arts;
static int reach_armed;

static const char *phase_name(unsigned phase)
{
    return phase == MF_PH_DEFINE ? "define" : phase == MF_PH_USE ? "use" : "run";
}

static const char *deny_name(uint64_t deny)
{
    return deny == MF_D_RUN_OVERLAP ? "MF_D_RUN_OVERLAP" : "MF_D_?";
}

/* `name:R1:UNSTATED` / `name:R2:<class>` for every field the verdict
 * declines, comma-joined; `-` for none. */
static void put_fields(const gate_verdict *v, const gate_in *in)
{
    int any = 0;
    for (unsigned f = 0; f < FLD_N; f++) {
        if (v->r1 >> f & 1)
            fprintf(stderr, "%s%s:R1:UNSTATED", any++ ? "," : "", fields[f].name);
        else if (v->r2 >> f & 1)
            fprintf(stderr, "%s%s:R2:%s", any++ ? "," : "", fields[f].name,
                    class_names[class_of(f, in)]);
    }
    if (!any) fputs("-", stderr);
}

static void reach_print(void)
{
    for (int pass = 0; pass < 2; pass++) {
        for (size_t i = 0;; i++) {
            const gate_contract *c = pass == 0 ? kit_arm_contract(i) : rc_row_contract(i);
            if (!c) break;
            unsigned slot = 0;
            while (slot < REACH_ROWS && reach_row[slot] != c) slot++;
            unsigned long n = slot < REACH_ROWS ? reach_chosen[slot] : 0;
            fprintf(stderr, "MFTRACE REACH table=%s row=%s chosen=%lu\n", c->table, c->row, n);
            if (slot == REACH_ROWS) continue;
            for (unsigned f = 0; f < FLD_N; f++)
                for (unsigned k = 0; k <= CL_N; k++)
                    if (reach_cell[slot][f][k])
                        fprintf(stderr,
                                "MFTRACE REACH table=%s row=%s field=%s class=%s n=%lu\n",
                                c->table, c->row, fields[f].name,
                                k == CL_N ? "UNSTATED" : class_names[k],
                                reach_cell[slot][f][k]);
        }
    }
    /* Always printed: a full registry would otherwise list a chosen row as
       `chosen=0`, a population nobody counted (N4). The census requires 0. */
    fprintf(stderr, "MFTRACE REACH_DROPPED n=%lu\n", reach_dropped);
}

/* The counters' slot for row `c`, registered on first sight; REACH_ROWS
 * when the registry is full (that row then goes uncounted). */
static unsigned reach_slot(const gate_contract *c)
{
    if (!reach_armed) {
        reach_armed = 1;
        atexit(reach_print);
    }
    unsigned slot = 0;
    while (slot < REACH_ROWS && reach_row[slot] && reach_row[slot] != c) slot++;
    if (slot < REACH_ROWS) reach_row[slot] = c;
    return slot;
}

void gate_trace_art(mf_art *art)
{
    art->trace_id = ++trace_arts;
}

static void head(const gate_tctx *t, const char *what)
{
    fprintf(stderr, "MFTRACE %s table=%s art=%u site=", what, t->table, t->art->trace_id);
    if (t->site) fprintf(stderr, "%u", t->site);
    else         fputs("-", stderr);
    fprintf(stderr, " phase=%s", phase_name(t->phase));
}

void gate_trace_sel(const gate_tctx *t)
{
    head(t, "SEL");
    if (t->phase == MF_PH_RUN)
        fprintf(stderr, " run=%s len=%u\n", class_names[class_of(FLD_run, t->in)],
                t->in->t ? (unsigned)t->in->t->run_len : 0u);
    else
        fprintf(stderr, " form=%s op=%s handoff=%s\n", class_names[cl_form(t->in)],
                class_names[cl_op(t->in)], class_names[cl_handoff(t->in)]);
}

void gate_trace_row(const gate_tctx *t, const gate_contract *c, const char *verdict,
                    uint64_t deny, const gate_verdict *v)
{
    head(t, "ROW");
    fprintf(stderr, " row=%s verdict=%s", c->row, verdict);
    if (deny) fprintf(stderr, ":%s", deny_name(deny));
    if (!v) {
        fputs(" gate=-\n", stderr);
        return;
    }
    fprintf(stderr, " gate=%s fields=", v->r1 | v->r2 ? "DECLINED" : "PASS");
    put_fields(v, t->in);
    fputs("\n", stderr);
}

/* ` moved_from=<row>` where the gate moved the selection off row `mc`. */
static void put_moved(const gate_contract *mc)
{
    if (mc) fprintf(stderr, " moved_from=%s", mc->row);
}

void gate_trace_end(const gate_tctx *t, const gate_contract *c, const gate_verdict *v,
                    const gate_contract *mc, const gate_verdict *mv)
{
    head(t, "END");
    if (!c) {
        /* no row serves: the kit refuses, naming `v`'s fields (the last row
           the walk declined, its total fallback) */
        fputs(" chosen=- would_decline=- fields=", stderr);
        if (v) put_fields(v, t->in);
        else   fputs("-", stderr);
        put_moved(mc);
        fputs("\n", stderr);
        return;
    }
    /* would_decline: at define/run, the gate MOVED the selection (the first
       row whose predicate held was declined; its fields are printed), N1's
       WARN quantity measured on the enforcing build; at use, the re-check
       failed and the kit refuses */
    const gate_verdict *w = mc ? mv : v;
    fprintf(stderr, " chosen=%s would_decline=%d fields=", c->row, (w->r1 | w->r2) != 0);
    put_fields(w, t->in);
    put_moved(mc);
    fputs("\n", stderr);

    unsigned slot = reach_slot(c);
    if (slot == REACH_ROWS) {
        reach_dropped++;
        return;
    }
    if (t->phase != MF_PH_USE) reach_chosen[slot]++;   /* a use re-checks, never selects */
    uint64_t uses = uses_at(c, t->phase, t->in);
    for (unsigned f = 0; f < FLD_N; f++) {
        if (!(uses >> f & 1) || !(fields[f].phase & t->phase)) continue;
        int k = class_of(f, t->in);
        reach_cell[slot][f][k < 0 ? CL_N : (unsigned)k]++;
    }
}

#endif /* MF_TRACE */
