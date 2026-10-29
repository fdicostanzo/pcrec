/* src/gen/vm_stmt.h — the VM matcher body as typed RECORDS ([VMREC] (a);
 * docs/dev/lanes/vmcons3_report.md rev 3, vmrec_report.md rev 3.1).
 *
 * PRIVATE TO src/gen/: emit_vm.c is its one includer. Every statement of the
 * VM matcher's body is BUILT as a record (a kind and its typed operands), and
 * each kind has ONE renderer, which prints it at once into the body. The
 * control text of a statement (its gotos, returns, labels, braces, and its
 * writes to the cursor, a slot, a local or run state) is printed only by its
 * kind's renderer, from the record's operands; the only free text is a VALUE
 * FRAGMENT (a condition, a source, a count, a clamp), which carries no
 * control. A kind that is not in the kind table has no renderer, so it cannot
 * be built.
 *
 * ONE WRITER, BY TILING. The body buffer is reachable only through this
 * module: every builder checks that the body's uncut length (written plus
 * comment-muted bytes) is where the previous record ended, so a write that
 * reached the body by any other route (a raw print, a helper handed the
 * buffer, a comment-tier print under `-fno-comments`, a truncation) is an
 * internal error at the next record. Lengths, not names: an append or a
 * truncation is caught, a same-length overwrite is not. The matcher's span in
 * the artifact is written by ONE call, `vm_stmt_frame`, which tiles its own
 * rows the same way.
 *
 * NO ANALYSIS LIVES HERE. Records carry no verdicts, no read sets and no
 * statement ids; stage (c) adds those (review r9's FIX-6). The listing's
 * events and the counters that steer emission stay with emit_vm.c's
 * primitives, at the program points they always had. */
#ifndef PCREC_VM_STMT_H
#define PCREC_VM_STMT_H

#include "core/internal.h"
#include "gen/callsite_rows.h"
#include "gen/clskit.h"
#include "gen/memfn_sites.h"

/* THE KINDS. One row each in `vm_kind_rows[]` (vm_stmt.c), which names the
 * kind's renderer; the table is the only place a kind is made printable. */
typedef enum {
    VK_LABEL,        /* `[// role]` + `<p>_L<n>:` */
    VK_CHECKPOINT,   /* `<P>_TRAIL_CHECK();` as a statement */
    VK_GOTO,         /* `goto <p>_L<n>;` */
    VK_FAIL,         /* `goto <p>_fail;` (no condition operand) */
    VK_ACCEPT,       /* `goto <p>_accept;` */
    VK_BRANCH,       /* `if (C) T`, T rendered from the target */
    VK_GUARD,        /* `if (C) {` / `if (C)` (inline) / `if (C) {` (inline braced) */
    VK_GUARD_END,    /* its close, in the open GUARD's spelling */
    VK_SWITCH,       /* the first-byte switch with its case list */
    VK_PUSH,         /* `<P>_PUSH([n, ]&&<p>_L<n>, POS);` */
    VK_SET,          /* `<P>_SET(<slot>, SRC);` */
    VK_SNAPSHOT,     /* a call site's park: `<P>_SET(<slot>, slot_values[<slot>]);` */
    VK_RESTORE,      /* a region exit's restore of ordinal j */
    VK_CUT,          /* `<P>_CUT(<slot>);` */
    VK_CUT_LOCAL,    /* `run->resume_depth = <p>_rv<i>_frame_mark;` */
    VK_CALL,         /* `<P>_CALL(&&<p>_L<ret>, scan_position);` */
    VK_RETURN,       /* the region-exit block */
    VK_STEP,         /* `if (--run->steps_left < 0) return <P>_R_STEPS;` */
    VK_WORK,         /* `<P>_CHARGE_WORK(N);` */
    VK_CONSUME,      /* `if (C) { ADV; goto <p>_L<n>; }`; the wide class's block */
    VK_CONSUME_BACK, /* `if (C) { <p>_rv<i>_cursor--; goto <p>_L<n>; }` */
    VK_SPAN,         /* the span cursor's opener: the scan block, or init only */
    VK_SPAN_MOVE,    /* a span-cursor member: re-seed, retreat, extend */
    VK_SEEK,         /* a cursor write: span commit, slot restore, advance, back-step */
    VK_LSET,         /* a write to an untrailed matcher local */
    VK_BREF,         /* the backreference compare block */
    VK_VAR,          /* the caller-variable compare block */
    VK_CALLOUT,      /* the callout block, its edge rows through callsite_rows.c */
    VK_WITNESS,      /* the test build's SIMD witness block */
    VK__COUNT
} VmKind;

/* A VALUE FRAGMENT: a piece list. TEXT is pcrec's own text; CLS is the class
 * kit's inline membership test of one byte expression, written by the
 * renderer; KIT is a delegated kit window, written IN PLACE into the body by
 * the renderer (so the SIMD, scaffold and comment records it makes are the
 * body's own). No piece takes a label, a target or a statement. */
typedef enum { VP_TEXT, VP_CLS, VP_KIT } VmPieceKind;
typedef struct {
    VmPieceKind    k;
    const char    *text;   /* TEXT: the text; CLS: the byte expression */
    ClsChoice      ch;     /* CLS */
    DelegSite      id;     /* KIT */
    const mf_site *site;   /* KIT: arena-owned */
    mf_hooks       hooks;  /* KIT */
} VmPiece;
typedef struct {
    VmPiece *p;
    int      n, cap;
} VmFrag;

/* A jump's target: a label (`ckpt`: the D183 placement put a trail
 * checkpoint on this edge, rendered as `{ <P>_TRAIL_CHECK(); goto L; }`),
 * the fail label, or a return of the artifact code `<P>_R_<code>`. */
typedef enum { VT_LABEL, VT_FAIL, VT_RETURN } VmTgtKind;
typedef struct {
    VmTgtKind   k;
    int         lbl;
    bool        ckpt;
    const char *code;
} VmTgt;

/* GUARD and GUARD_END spellings; a GUARD_END closes the innermost open GUARD
 * and must name its spelling. */
typedef enum {
    VG_BRACED,        /* `    if (C) {\n` ... `    }\n` */
    VG_INLINE,        /* `    if (C)` + one inline record + `\n` */
    VG_INLINE_BRACED  /* `    if (C) {` + inline records + ` }\n` */
} VmGuardSpell;

/* PUSH's resume position. */
typedef enum {
    VPOS_CURSOR,       /* scan_position */
    VPOS_SPAN,         /* the span cursor */
    VPOS_REVDET_PREV   /* the revdet loop's previous boundary */
} VmPosKind;

/* CONSUME's advance. */
typedef enum {
    VADV_INC,    /* `scan_position++;` */
    VADV_BY,     /* `scan_position += k;` */
    VADV_WCLS    /* the wide class's decode block (its own condition) */
} VmAdv;

/* SPAN_MOVE: a span-cursor member's write. */
typedef enum {
    VSM_SEED,    /* `<p>_span_cursor = scan_position;` (resumed from the frame) */
    VSM_BACK,    /* `<p>_span_cursor -= k;` */
    VSM_FWD      /* `<p>_span_cursor += k;` */
} VmSpanMove;

/* SEEK: a cursor write. */
typedef enum {
    VSK_SPAN_COMMIT,  /* `scan_position = <p>_span_cursor;` */
    VSK_RESTORE,      /* `scan_position = (size_t)slot_values[<slot>];` */
    VSK_ADVANCE,      /* `scan_position += k;` */
    VSK_BACKSTEP      /* the encoding seam's back-step by k */
} VmSeek;

/* An untrailed matcher LOCAL an LSET may write. The span cursor, the subject
 * cursor and run state are not members (they are written only by their own
 * kinds), so an LSET cannot be built on them. */
typedef enum {
    VL_RV_ITERATION,     /* <p>_rv<loop>_iteration */
    VL_RV_FRAME_MARK,    /* <p>_rv<loop>_frame_mark */
    VL_RV_CURSOR,        /* <p>_rv<loop>_cursor */
    VL_RV_PREV,          /* <p>_rv<loop>_prev_position */
    VL_RV_GROUPS_SEEN,   /* <p>_rv<loop>_groups_seen */
    VL_GROUP_SEEN,       /* <p>_revdet_group_seen[j] */
    VL_GROUP_SPAN        /* <p>_revdet_group_span[j][half] */
} VmLocalKind;
typedef struct {
    VmLocalKind k;
    int         loop, j, half;
} VmLocal;
typedef enum {
    VLO_ASSIGN,   /* `x = SRC;` */
    VLO_INC,      /* `x++;` */
    VLO_ZERO      /* the seen array, all n cleared (the `{ int i_; ... }` block) */
} VmLsetOp;

/* One first-byte switch arm. */
typedef struct { int byte, lbl; } VmCase;

/* BREF's operands: per ref, its two slot expressions; the seam compare's
 * caselessness (which names the entry); the work charge's count, or NULL
 * where the artifact has no budget; the success label. */
typedef struct {
    const char *const *ref_start;
    const char *const *ref_end;
    int                nrefs;
    bool               caseless;
    const char        *work;
    int                lbl;
} VmBrefOps;

/* VAR's operands: the variable's slot, caselessness, the work charge's count
 * (or NULL) and the success label. */
typedef struct {
    int         slot;
    bool        caseless;
    const char *work;
    int         lbl;
} VmVarOps;

/* CALLOUT's operands: the step charge, the binding, the view (0: the
 * caller's slots; else the definition-site map), the caller variables,
 * the predicate/consume choice, the success label and the call-site row
 * table's callee description. */
typedef struct {
    bool        steps;
    const char *callee_sym;
    const char *user;
    int         ncap;
    int         view_n;
    const int  *view_map;
    bool        vars;
    bool        pred;
    int         lbl;
    CsCallee    callee;
} VmCalloutOps;

/* THE RECORD. `kind` selects the operand member; `at`/`end` are the body's
 * uncut length around the render (the tiling clock), `tat`/`tend` its
 * written length (text offsets, for a reader of the render-time text). */
typedef struct {
    VmKind kind;
    union {
        struct { int lbl; const char *role; } label;
        struct { int lbl; } go;
        struct { VmFrag c; VmTgt t; } branch;
        struct { VmFrag c; VmGuardSpell sp; } guard;
        struct { int depth; const VmCase *cases; int ncase; } sw;
        struct { int lbl; VmPosKind pos; int loop; } push;
        struct { int slot; const char *name; const char *src; } set;
        struct { int slot; const char *name; } snap;
        struct { int slot; const char *name; int j; } restore;
        struct { int slot; } cut;
        struct { int loop; } cut_local;
        struct { int ret; } call;
        struct { const char *count; } work;
        struct { VmFrag c; VmAdv adv; int k, lbl, wi; } consume;
        struct { VmFrag c; int loop, lbl; } back;
        struct { bool block; int cap, stride; const char *clamp; VmPiece kit; } span;
        struct { VmSpanMove mv; int k; } span_move;
        struct { VmSeek sk; const char *slotx; int k; } seek;
        struct { VmLocal x; VmLsetOp op; const char *src; int n; bool inl; } lset;
        VmBrefOps    bref;
        VmVarOps     var;
        VmCalloutOps callout;
    } u;
    size_t at, end, tat, tend;
} VmStmt;

typedef struct VmBody VmBody;

/* Opens the body for one VM program: `job->vmsb`, the compile's prefix
 * spellings and the --trace axis. */
VmBody *vm_stmt_open(Ctx *cx, const char *p, const char *up, bool tracing);

/* ---- fragments ---------------------------------------------------------- */
VmFrag  vm_frag(void);
void    vm_frag_text(VmBody *sb, VmFrag *f, const char *text);
void    vm_frag_cls(VmBody *sb, VmFrag *f, const ClsChoice *ch, const char *byte);
void    vm_frag_kit(VmBody *sb, VmFrag *f, DelegSite id, const mf_site *s,
                    const mf_hooks *h);
VmFrag  vm_frag_of(VmBody *sb, const char *text);

/* ---- targets ------------------------------------------------------------ */
VmTgt   vm_tgt_label(int lbl, bool ckpt);
VmTgt   vm_tgt_fail(void);
VmTgt   vm_tgt_return(const char *code);

/* ---- the builders, one per kind ------------------------------------------ */
void vm_b_label(VmBody *sb, int lbl, const char *role);
void vm_b_checkpoint(VmBody *sb);
void vm_b_goto(VmBody *sb, int lbl);
void vm_b_fail(VmBody *sb);
void vm_b_accept(VmBody *sb);
void vm_b_branch(VmBody *sb, VmFrag c, VmTgt t);
void vm_b_guard(VmBody *sb, VmGuardSpell sp, VmFrag c);
void vm_b_guard_end(VmBody *sb, VmGuardSpell sp);
void vm_b_switch(VmBody *sb, int depth, const VmCase *cases, int ncase);
void vm_b_push(VmBody *sb, int lbl, VmPosKind pos, int loop);
void vm_b_set(VmBody *sb, int slot, const char *name, const char *src);
void vm_b_snapshot(VmBody *sb, int slot, const char *name);
void vm_b_restore(VmBody *sb, int slot, const char *name, int j);
void vm_b_cut(VmBody *sb, int slot);
void vm_b_cut_local(VmBody *sb, int loop);
void vm_b_call(VmBody *sb, int ret);
void vm_b_return(VmBody *sb);
void vm_b_step(VmBody *sb);
void vm_b_work(VmBody *sb, const char *count);
void vm_b_consume(VmBody *sb, VmFrag c, VmAdv adv, int k, int lbl);
void vm_b_consume_wcls(VmBody *sb, int wi, int lbl);
void vm_b_consume_back(VmBody *sb, int loop, VmFrag c, int lbl);
void vm_b_span(VmBody *sb, int cap, const char *clamp, int stride,
               DelegSite id, const mf_site *s, const mf_hooks *h);
void vm_b_span_init(VmBody *sb);
void vm_b_span_move(VmBody *sb, VmSpanMove mv, int k);
void vm_b_seek(VmBody *sb, VmSeek sk, const char *slotx, int k);
void vm_b_lset(VmBody *sb, VmLocal x, VmLsetOp op, const char *src, int n,
               bool inl);
void vm_b_bref(VmBody *sb, const VmBrefOps *o);
void vm_b_var(VmBody *sb, const VmVarOps *o);
void vm_b_callout(VmBody *sb, const VmCalloutOps *o);
void vm_b_witness(VmBody *sb);

/* ---- the body's other readers ----------------------------------------- */

/* The body's length for a DECISION (`pcrec_sb_len_decide`): the entry-shape
 * knee and the `<PREFIX>_VM_PROGRAM_BYTES` stamp. */
size_t      vm_stmt_program_bytes(const VmBody *sb);
/* The body's text, read-only (the class pass counts its table reads). */
const char *vm_stmt_text(const VmBody *sb);

/* THE ONE POST-RENDER REWRITE: re-spells every `from[i]` in the body as
 * `to[i]` (the class-table selection), after the walk. It CLOSES the body:
 * no record can be built after it, and the frame splices exactly what it
 * left. `needle` is the opening every recorded read starts with; a match of
 * it that is no recorded read is an internal error. */
void vm_stmt_respell(VmBody *sb, const char *needle, const char *const *from,
                     const char *const *to, int n);

/* THE MATCHER'S FRAME: what the one call needs to write the whole span (head
 * and declarations, the entry jump, the body splice, the accept label and
 * return, the fail block) and, where the retry table asks for it, the
 * not-empty copy of that span. */
typedef struct {
    const char *ai_body;     /* the matcher's linkage attribute text */
    const char *mrl_param;   /* the MRL ceiling parameter, or "" */
    const char *gst_param;   /* the `\G` parameter, or "" */
    bool trail_gc;           /* the program has trail checkpoints */
    bool span_cursor;        /* the cursor rung is present */
    int  nrev_total;         /* revdet loops */
    int  nrevcaps;           /* the widest revdet body's group count */
    bool tracing;
    bool kreset;             /* the program writes `\K` */
    bool has_push;
    bool has_budget;
    bool has_linked_calls;
    bool guarded_copy;       /* write `<p>__match_notempty` too */
} VmFrame;

/* Writes the matcher's whole span into the artifact buffer `c` in one call,
 * the body spliced in; the body must be closed (`vm_stmt_respell`) or end on
 * a record. */
void vm_stmt_frame(VmBody *sb, StrBuf *c, const VmFrame *f);

#endif
