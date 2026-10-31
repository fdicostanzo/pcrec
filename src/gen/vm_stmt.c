/* src/gen/vm_stmt.c — the VM matcher body as typed records, their one
 * renderer per kind, and the matcher's frame ([VMREC] (a)).
 *
 * The header (vm_stmt.h) states the module's contract: records are built,
 * each builder renders at once, the body tiles, and the frame is one call.
 * This file is the only place the VM body buffer (`job->vmsb`) is named in
 * src/gen/, and the only place the VM body calls the delegated writers (the
 * memfn kit, the class kit's inline test, the call-site row table, the SIMD
 * witness). Every byte it prints is the byte emit_vm.c printed before the
 * refactor; the identity gate (docs/dev/lanes/vmrec_report.md, E1) is the
 * proof, and a byte that moves is a bug here, never a re-pin. */
#include <string.h>

#include "gen/vm_stmt.h"

/* The body and its tiling clock. `clock` is the uncut length where the last
 * record (or the respell) left the body; `closed` is set by the respell,
 * after which nothing may be built. `gstack` holds the open GUARDs'
 * spellings, innermost last. The records are kept, in order, for a reader of
 * the body (none in stage (a) but the tiling diagnostics). */
struct VmBody {
    Ctx        *cx;
    StrBuf     *b;
    const char *p, *up;
    bool        tracing;
    size_t      clock;
    bool        closed;
    VmGuardSpell gstack[16];
    int         gdepth;
    VmStmt     *rec;
    int         nrec, reccap;
};

static const char *vm_kind_name(VmKind k);

/* ---- fragments ---------------------------------------------------------- */

/* Appends one piece to fragment `f`, growing it in the arena by doubling. */
static VmPiece *vm_frag_push(VmBody *sb, VmFrag *f)
{
    if (f->n == f->cap) {
        int ncap = f->cap ? f->cap * 2 : 4;
        VmPiece *np = pcrec_arena_alloc(&sb->cx->arena, (size_t)ncap * sizeof *np);
        if (f->n) memcpy(np, f->p, (size_t)f->n * sizeof *np);
        f->p = np;
        f->cap = ncap;
    }
    VmPiece *q = &f->p[f->n++];
    memset(q, 0, sizeof *q);
    return q;
}

/* An empty fragment. */
VmFrag pcrec_vm_frag(void)
{
    return (VmFrag){ NULL, 0, 0 };
}

/* Appends pcrec's own text to `f`. */
void pcrec_vm_frag_text(VmBody *sb, VmFrag *f, const char *text)
{
    VmPiece *q = vm_frag_push(sb, f);
    q->k = VP_TEXT;
    q->text = text;
}

/* Appends the class kit's inline membership test of `byte` under `ch`. */
void pcrec_vm_frag_cls(VmBody *sb, VmFrag *f, const ClsChoice *ch, const char *byte)
{
    VmPiece *q = vm_frag_push(sb, f);
    q->k = VP_CLS;
    q->ch = *ch;
    q->text = byte;
}

/* Appends a delegated kit window: site `s` of row `id`, its hooks copied. */
void pcrec_vm_frag_kit(VmBody *sb, VmFrag *f, DelegSite id, const mf_site *s,
                 const mf_hooks *h)
{
    VmPiece *q = vm_frag_push(sb, f);
    q->k = VP_KIT;
    q->id = id;
    q->site = s;
    q->hooks = *h;
}

/* A fragment of one text piece. */
VmFrag pcrec_vm_frag_of(VmBody *sb, const char *text)
{
    VmFrag f = pcrec_vm_frag();
    pcrec_vm_frag_text(sb, &f, text);
    return f;
}

/* Writes one piece into the body: text as itself, the class kit's and the
 * memfn kit's pieces by their own writers, in place. */
static void vm_piece_render(VmBody *sb, const VmPiece *q)
{
    switch (q->k) {
    case VP_TEXT: pcrec_sb_puts(sb->b, q->text); return;
    case VP_CLS:  pcrec_clskit_emit_inline(sb->b, &q->ch, q->text); return;
    case VP_KIT:  pcrec_memfn_emit(sb->cx, q->id, q->site, &q->hooks, sb->b); return;
    }
}

/* Writes a whole fragment, piece by piece. */
static void vm_frag_render(VmBody *sb, const VmFrag *f)
{
    for (int i = 0; i < f->n; i++) vm_piece_render(sb, &f->p[i]);
}

/* ---- targets ------------------------------------------------------------ */

/* A jump to label `lbl`; `ckpt` puts the D183 trail checkpoint on the edge. */
VmTgt pcrec_vm_tgt_label(int lbl, bool ckpt)
{
    return (VmTgt){ VT_LABEL, lbl, ckpt, NULL };
}

/* The jump to the fail label. */
VmTgt pcrec_vm_tgt_fail(void)
{
    return (VmTgt){ VT_FAIL, -1, false, NULL };
}

/* A return of artifact code `<P>_R_<code>`. */
VmTgt pcrec_vm_tgt_return(const char *code)
{
    return (VmTgt){ VT_RETURN, -1, false, code };
}

/* Writes a target as the statement a condition guards. */
static void vm_tgt_render(VmBody *sb, const VmTgt *t)
{
    switch (t->k) {
    case VT_FAIL:
        pcrec_sb_printf(sb->b, "goto %s_fail;", sb->p);
        return;
    case VT_RETURN:
        pcrec_sb_printf(sb->b, "return %s_R_%s;", sb->up, t->code);
        return;
    case VT_LABEL:
        if (t->ckpt)
            pcrec_sb_printf(sb->b, "{ %s_TRAIL_CHECK(); goto %s_L%d; }",
                            sb->up, sb->p, t->lbl);
        else
            pcrec_sb_printf(sb->b, "goto %s_L%d;", sb->p, t->lbl);
        return;
    }
}

/* ---- the renderers, one per kind --------------------------------------- */

/* Refuses a record a renderer was not written for: the kind table named the
 * wrong renderer for `s`'s kind. */
static void vm_renders(VmBody *sb, const VmStmt *s, VmKind k)
{
    if (s->kind != k)
        pcrec_ctx_fail(sb->cx, 0, "internal error: the VM body's %s renderer "
                       "was handed a %s record (the kind table names the "
                       "wrong renderer)", vm_kind_name(k), vm_kind_name(s->kind));
}

/* LABEL: the role as a non-essential line comment, then the label. A role is
 * pcrec's text, and a line break or a trailing backslash in it would carry
 * the next line into the comment. */
static void vm_r_label(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_LABEL);
    const char *role = s->u.label.role;
    if (role && *role) {
        size_t n = strlen(role);
        if (strpbrk(role, "\n\r") || role[n - 1] == '\\')
            pcrec_ctx_fail(sb->cx, 0, "internal error: a VM label's role text "
                           "would not stay inside its line comment");
        pcrec_sb_cmt_open(sb->b, PCREC_CMT_NONESSENTIAL);
        pcrec_sb_printf(sb->b, "// %s\n", role);
        pcrec_sb_cmt_close(sb->b);
    }
    pcrec_sb_printf(sb->b, "%s_L%d: __attribute__((unused));\n", sb->p, s->u.label.lbl);
}

/* CHECKPOINT: the trail checkpoint as a statement. */
static void vm_r_checkpoint(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_CHECKPOINT);
    pcrec_sb_printf(sb->b, "    %s_TRAIL_CHECK();\n", sb->up);
}

/* GOTO: the unconditional jump. */
static void vm_r_goto(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_GOTO);
    pcrec_sb_printf(sb->b, "    goto %s_L%d;\n", sb->p, s->u.go.lbl);
}

/* FAIL: the jump to the fail label. */
static void vm_r_fail(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_FAIL);
    pcrec_sb_printf(sb->b, "    goto %s_fail;\n", sb->p);
}

/* ACCEPT: the jump to the accept label. */
static void vm_r_accept(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_ACCEPT);
    pcrec_sb_printf(sb->b, "    goto %s_accept;\n", sb->p);
}

/* BRANCH: `if (C) T`. */
static void vm_r_branch(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_BRANCH);
    pcrec_sb_puts(sb->b, "    if (");
    vm_frag_render(sb, &s->u.branch.c);
    pcrec_sb_puts(sb->b, ") ");
    vm_tgt_render(sb, &s->u.branch.t);
    pcrec_sb_puts(sb->b, "\n");
}

/* GUARD: the guard's open, in its spelling. */
static void vm_r_guard(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_GUARD);
    pcrec_sb_puts(sb->b, "    if (");
    vm_frag_render(sb, &s->u.guard.c);
    switch (s->u.guard.sp) {
    case VG_BRACED:        pcrec_sb_puts(sb->b, ") {\n"); return;
    case VG_INLINE:        pcrec_sb_puts(sb->b, ")"); return;
    case VG_INLINE_BRACED: pcrec_sb_puts(sb->b, ") {"); return;
    }
}

/* GUARD_END: the close of the innermost open guard. */
static void vm_r_guard_end(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_GUARD_END);
    switch (s->u.guard.sp) {
    case VG_BRACED:        pcrec_sb_puts(sb->b, "    }\n"); return;
    case VG_INLINE:        pcrec_sb_puts(sb->b, "\n"); return;
    case VG_INLINE_BRACED: pcrec_sb_puts(sb->b, " }\n"); return;
    }
}

/* SWITCH: the first-byte switch at depth d and its arms. */
static void vm_r_switch(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_SWITCH);
    const int d = s->u.sw.depth;
    pcrec_sb_printf(sb->b, "    if (scan_position + %d < subject_length) "
                           "switch (subject[scan_position + %d]) {\n", d, d);
    for (int i = 0; i < s->u.sw.ncase; i++)
        pcrec_sb_printf(sb->b, "    case %d: goto %s_L%d;\n",
                        s->u.sw.cases[i].byte, sb->p, s->u.sw.cases[i].lbl);
    pcrec_sb_puts(sb->b, "    }\n");
}

/* PUSH: a resume frame at the label, resuming at the position operand. Under
 * --trace the macro also takes the label id. */
static void vm_r_push(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_PUSH);
    const char *pos = "scan_position";
    if (s->u.push.pos == VPOS_SPAN)
        pos = pcrec_sb_fragf(&sb->cx->arena, "%s_span_cursor", sb->p);
    else if (s->u.push.pos == VPOS_REVDET_PREV)
        pos = pcrec_sb_fragf(&sb->cx->arena, "(size_t)%s_rv%d_prev_position",
                             sb->p, s->u.push.loop);
    const int lbl = s->u.push.lbl;
    if (sb->tracing)
        pcrec_sb_printf(sb->b, "    %s_PUSH(%d, &&%s_L%d, %s);\n",
                        sb->up, lbl, sb->p, lbl, pos);
    else
        pcrec_sb_printf(sb->b, "    %s_PUSH(&&%s_L%d, %s);\n",
                        sb->up, sb->p, lbl, pos);
}

/* The `<P>_SET` line all three trail-write kinds print: the slot through its
 * legend name where the layout names it, by number where it does not. */
static void vm_set_line(VmBody *sb, int slot, const char *name, const char *src)
{
    if (name)
        pcrec_sb_printf(sb->b, "    %s_SET(%s_%s, %s);\n", sb->up, sb->up, name, src);
    else
        pcrec_sb_printf(sb->b, "    %s_SET(%d, %s);\n", sb->up, slot, src);
}

/* The slot's spelling as an expression read: `slot_values[<slot>]`. */
static const char *vm_slot_read(VmBody *sb, int slot, const char *name)
{
    if (name) return pcrec_sb_fragf(&sb->cx->arena, "slot_values[%s_%s]", sb->up, name);
    return pcrec_sb_fragf(&sb->cx->arena, "slot_values[%d]", slot);
}

/* SET: one trailed slot write. */
static void vm_r_set(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_SET);
    vm_set_line(sb, s->u.set.slot, s->u.set.name, s->u.set.src);
}

/* SNAPSHOT: a call site's park of the slot's own value on the trail; the
 * source is the slot itself, derived here, never an operand. */
static void vm_r_snapshot(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_SNAPSHOT);
    vm_set_line(sb, s->u.snap.slot, s->u.snap.name,
                vm_slot_read(sb, s->u.snap.slot, s->u.snap.name));
}

/* RESTORE: a region exit's restore of the caller's value, ordinal j of the
 * activation's parked values. */
static void vm_r_restore(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_RESTORE);
    vm_set_line(sb, s->u.restore.slot, s->u.restore.name,
                pcrec_sb_fragf(&sb->cx->arena,
                               "run->trail[run->resume_stack[run->call_top]"
                               ".trail_mark + %d].saved_value", s->u.restore.j));
}

/* CUT: truncate the resume stack to the depth parked in the slot. */
static void vm_r_cut(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_CUT);
    pcrec_sb_printf(sb->b, "    %s_CUT(%d);\n", sb->up, s->u.cut.slot);
}

/* CUT_LOCAL: the revdet loop's cut, to its own frame mark. */
static void vm_r_cut_local(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_CUT_LOCAL);
    pcrec_sb_printf(sb->b, "    run->resume_depth = %s_rv%d_frame_mark;\n",
                    sb->p, s->u.cut_local.loop);
}

/* CALL: a subroutine call returning to the label. */
static void vm_r_call(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_CALL);
    pcrec_sb_printf(sb->b, "    %s_CALL(&&%s_L%d, scan_position);\n",
                    sb->up, sb->p, s->u.call.ret);
}

/* RETURN: the region exit through the activation's own return label. */
static void vm_r_return(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_RETURN);
    pcrec_sb_printf(sb->b,
        "    {\n"
        "        const size_t %s_call_frame = run->call_top;\n"
        "        if (%s_call_frame >= run->resume_cap) return %s_R_INTERNAL;\n"
        "        run->call_top = run->resume_stack[%s_call_frame].call_top;\n"
        "        goto *run->resume_stack[%s_call_frame].call_ret;\n"
        "    }\n",
        sb->p, sb->p, sb->up, sb->p, sb->p);
}

/* STEP: one step charged, the give-up on an exhausted budget. */
static void vm_r_step(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_STEP);
    pcrec_sb_printf(sb->b, "    if (--run->steps_left < 0) return %s_R_STEPS;\n",
                    sb->up);
}

/* WORK: one work-budget charge. */
static void vm_r_work(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_WORK);
    pcrec_sb_printf(sb->b, "    %s_CHARGE_WORK(%s);\n", sb->up, s->u.work.count);
}

/* CONSUME: a guarded forward step to the label; the wide class's form
 * decodes one character and tests it with the set's kit matcher. */
static void vm_r_consume(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_CONSUME);
    const int lbl = s->u.consume.lbl;
    if (s->u.consume.adv == VADV_WCLS) {
        pcrec_sb_printf(sb->b,
            "    {\n"
            "        unsigned cp_ = 0;\n"
            "        size_t len_;\n"
            "        if (scan_position < subject_length\n"
            "            && (len_ = %s_decode(subject, subject_length, scan_position, &cp_)) != 0\n"
            "            && %s_wcls%d(cp_)) { scan_position += len_; goto %s_L%d; }\n"
            "    }\n",
            sb->p, sb->p, s->u.consume.wi, sb->p, lbl);
        return;
    }
    pcrec_sb_puts(sb->b, "    if (");
    vm_frag_render(sb, &s->u.consume.c);
    if (s->u.consume.adv == VADV_INC)
        pcrec_sb_printf(sb->b, ") { scan_position++; goto %s_L%d; }\n", sb->p, lbl);
    else
        pcrec_sb_printf(sb->b, ") { scan_position += %d; goto %s_L%d; }\n",
                        s->u.consume.k, sb->p, lbl);
}

/* CONSUME_BACK: a guarded backward step of the revdet walk's cursor. */
static void vm_r_consume_back(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_CONSUME_BACK);
    pcrec_sb_puts(sb->b, "    if (");
    vm_frag_render(sb, &s->u.back.c);
    pcrec_sb_printf(sb->b, ") { %s_rv%d_cursor--; goto %s_L%d; }\n",
                    sb->p, s->u.back.loop, sb->p, s->u.back.lbl);
}

/* SPAN: the span cursor's opener. The block declares the iteration count and
 * the folded clamp it needs, starts the cursor and holds the kit's advance;
 * the init-only spelling starts the cursor alone (the lazy rung at rmin 0). */
static void vm_r_span(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_SPAN);
    if (!s->u.span.block) {
        pcrec_sb_printf(sb->b, "    %s_span_cursor = scan_position;\n", sb->p);
        return;
    }
    pcrec_sb_puts(sb->b, "    {\n");
    if (s->u.span.cap >= 0) pcrec_sb_puts(sb->b, "        unsigned long it_ = 0;\n");
    if (s->u.span.clamp)
        pcrec_sb_printf(sb->b, "        const size_t lim_ = %s_PRUNE_CLAMP_SPAN(scan_position, %s, %d);\n",
                        sb->up, s->u.span.clamp, s->u.span.stride);
    pcrec_sb_printf(sb->b, "        %s_span_cursor = scan_position;\n", sb->p);
    vm_piece_render(sb, &s->u.span.kit);
    pcrec_sb_puts(sb->b, "    }\n");
}

/* SPAN_MOVE: a member's write of the span cursor. */
static void vm_r_span_move(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_SPAN_MOVE);
    switch (s->u.span_move.mv) {
    case VSM_SEED:
        pcrec_sb_printf(sb->b, "    %s_span_cursor = scan_position;\n", sb->p);
        return;
    case VSM_BACK:
        pcrec_sb_printf(sb->b, "    %s_span_cursor -= %d;\n", sb->p, s->u.span_move.k);
        return;
    case VSM_FWD:
        pcrec_sb_printf(sb->b, "    %s_span_cursor += %d;\n", sb->p, s->u.span_move.k);
        return;
    }
}

/* SEEK: a write of the subject cursor. */
static void vm_r_seek(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_SEEK);
    switch (s->u.seek.sk) {
    case VSK_SPAN_COMMIT:
        pcrec_sb_printf(sb->b, "    scan_position = %s_span_cursor;\n", sb->p);
        return;
    case VSK_RESTORE:
        pcrec_sb_printf(sb->b, "    scan_position = (size_t)slot_values[%s];\n",
                        s->u.seek.slotx);
        return;
    case VSK_ADVANCE:
        pcrec_sb_printf(sb->b, "    scan_position += %d;\n", s->u.seek.k);
        return;
    case VSK_BACKSTEP:
        pcrec_sb_printf(sb->b, "    scan_position = %s_back_step(subject, "
                               "subject_length, scan_position, %d);\n",
                        sb->p, s->u.seek.k);
        return;
    }
}

/* The local's name as the frame declares it. */
static const char *vm_local_name(VmBody *sb, const VmLocal *x)
{
    Arena *a = &sb->cx->arena;
    switch (x->k) {
    case VL_RV_ITERATION:   return pcrec_sb_fragf(a, "%s_rv%d_iteration", sb->p, x->loop);
    case VL_RV_FRAME_MARK:  return pcrec_sb_fragf(a, "%s_rv%d_frame_mark", sb->p, x->loop);
    case VL_RV_CURSOR:      return pcrec_sb_fragf(a, "%s_rv%d_cursor", sb->p, x->loop);
    case VL_RV_PREV:        return pcrec_sb_fragf(a, "%s_rv%d_prev_position", sb->p, x->loop);
    case VL_RV_GROUPS_SEEN: return pcrec_sb_fragf(a, "%s_rv%d_groups_seen", sb->p, x->loop);
    case VL_GROUP_SEEN:     return pcrec_sb_fragf(a, "%s_revdet_group_seen[%d]", sb->p, x->j);
    case VL_GROUP_SPAN:     return pcrec_sb_fragf(a, "%s_revdet_group_span[%d][%d]",
                                                  sb->p, x->j, x->half);
    }
    return "";
}

/* LSET: a write of an untrailed matcher local, as a statement or inline
 * inside a guard. */
static void vm_r_lset(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_LSET);
    const char *lead = s->u.lset.inl ? " " : "    ";
    const char *tail = s->u.lset.inl ? "" : "\n";
    switch (s->u.lset.op) {
    case VLO_ASSIGN:
        pcrec_sb_printf(sb->b, "%s%s = %s;%s", lead,
                        vm_local_name(sb, &s->u.lset.x), s->u.lset.src, tail);
        return;
    case VLO_INC:
        pcrec_sb_printf(sb->b, "%s%s++;%s", lead, vm_local_name(sb, &s->u.lset.x), tail);
        return;
    case VLO_ZERO:
        pcrec_sb_printf(sb->b, "%s{ int i_; for (i_ = 0; i_ < %d; i_++)"
                               " %s_revdet_group_seen[i_] = 0; }%s",
                        lead, s->u.lset.n, sb->p, tail);
        return;
    }
}

/* BREF: the backreference compare block — the ref selection, the unset
 * test, the seam compare, its work charge, the advance and the jump. */
static void vm_r_bref(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_BREF);
    const VmBrefOps *o = &s->u.bref;
    StrBuf *bb = sb->b;
    const char *fn = pcrec_sb_fragf(&sb->cx->arena, "%s_span_match%s", sb->p,
                                    o->caseless ? "_caseless" : "");
    pcrec_sb_puts(bb, "    {\n        ptrdiff_t ref_start = PCREC_UNSET, "
                "ref_end = PCREC_UNSET, took;\n");
    for (int i = 0; i < o->nrefs; i++) {
        const char *ns = o->ref_start[i];
        const char *ne = o->ref_end[i];
        pcrec_sb_printf(bb,
            "        %sif (slot_values[%s] != PCREC_UNSET) {\n"
            "            ref_start = slot_values[%s];\n"
            "            ref_end   = slot_values[%s];\n"
            "        }%s",
            i ? "else " : "", ns, ns, ne,
            i + 1 == o->nrefs ? "\n" : " ");
    }
    pcrec_sb_cmt_open(bb, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_puts(bb,
        "        /* No PUBLISHED capture on this path. PCRE2 FAILS here;\n"
        "         * it does not match the empty string. */\n");
    pcrec_sb_cmt_close(bb);
    pcrec_sb_printf(bb,
        "        if (ref_start == PCREC_UNSET) goto %s_fail;\n"
        /* [VAR ruling, 2026-09-23] THE REFERENCE SIDE IS A POINTER AND A
         * LENGTH, which is what lets one seam entry serve this construct and
         * a `${name}` variable both. A backreference's bytes are a slice of
         * the subject, so the slice is spelled here rather than the entry
         * being told to index into `s` itself. */
        "        took = %s(subject, subject_length,\n"
        "                  subject + (size_t)ref_start,\n"
        "                  (size_t)(ref_end - ref_start),\n"
        "                  scan_position);\n",
        sb->p, fn);
    if (o->work)
        pcrec_sb_printf(bb, "        %s_CHARGE_WORK(%s);\n", sb->up, o->work);
    pcrec_sb_printf(bb,
        "        if (took < 0) goto %s_fail;\n"
        "        scan_position += (size_t)took;\n"
        "        goto %s_L%d;\n"
        "    }\n",
        sb->p, sb->p, o->lbl);
}

/* VAR: the caller-variable compare block, BREF's with the span source
 * swapped. */
static void vm_r_var(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_VAR);
    const VmVarOps *o = &s->u.var;
    StrBuf *bb = sb->b;
    const char *fn = pcrec_sb_fragf(&sb->cx->arena, "%s_span_match%s", sb->p,
                                    o->caseless ? "_caseless" : "");
    pcrec_sb_printf(bb,
        "    {\n"
        "        ptrdiff_t took;\n"
        "        took = %s(subject, subject_length,\n"
        "                  run->var_value[%d], run->var_length[%d],\n"
        "                  scan_position);\n",
        fn, o->slot, o->slot);
    if (o->work)
        pcrec_sb_printf(bb, "        %s_CHARGE_WORK(%s);\n", sb->up, o->work);
    pcrec_sb_printf(bb,
        "        if (took < 0) goto %s_fail;\n"
        "        scan_position += (size_t)took;\n"
        "        goto %s_L%d;\n"
        "    }\n",
        sb->p, sb->p, o->lbl);
}

/* CALLOUT: the step charge, the callout's context and view, the call, and
 * its edge rows, which the call-site table writes from edges rendered here
 * from the success label (a predicate continues, a consuming callout
 * advances by its result first). */
static void vm_r_callout(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_CALLOUT);
    const VmCalloutOps *o = &s->u.callout;
    StrBuf *b = sb->b;
    const char *p = sb->p;
    Arena *a = &sb->cx->arena;
    if (o->steps)
        pcrec_sb_printf(b, "    if (--run->steps_left < 0) return %s_R_STEPS;\n",
                        sb->up);
    pcrec_sb_printf(b,
        "    {\n"
        "        rx_ctx %s_co_ctx;\n"
        "        const ptrdiff_t %s_co_start = slot_values[0];\n"
        "        ptrdiff_t r;\n"
        "        %s_co_ctx.subject = subject;\n"
        "        %s_co_ctx.len = subject_length;\n"
        "        %s_co_ctx.pos = scan_position;\n",
        p, p, p, p, p);
    const int vn = o->view_n;
    if (vn == 0)
        pcrec_sb_printf(b,
            "        %s_co_ctx.ncap = %d;\n"
            "        %s_co_ctx.caps = (const ptrdiff_t (*)[2])slot_values;\n",
            p, o->ncap, p);
    else {
        /* [INLINE-C] stage 3 THE DEFINITION-SITE VIEW (§1.9): the
         * definition's groups in its own numbering, copied out of the
         * caller's slots at the fire; slot 0 is the attempt start as in
         * the caller's view. */
        pcrec_sb_printf(b,
            "        ptrdiff_t %s_co_view[%d][2];\n"
            "        %s_co_view[0][0] = (ptrdiff_t)ctx->pos;\n"
            "        %s_co_view[0][1] = slot_values[1];\n",
            p, vn, p, p);
        for (int k = 1; k < vn; k++)
            pcrec_sb_printf(b,
                "        %s_co_view[%d][0] = slot_values[%d];\n"
                "        %s_co_view[%d][1] = slot_values[%d];\n",
                p, k, 2 * o->view_map[k],
                p, k, 2 * o->view_map[k] + 1);
        pcrec_sb_printf(b,
            "        %s_co_ctx.ncap = %d;\n"
            "        %s_co_ctx.caps = (const ptrdiff_t (*)[2])%s_co_view;\n",
            p, vn, p, p);
    }
    pcrec_sb_printf(b, "        %s_co_ctx.user = %s;\n", p, o->user);
    if (o->vars)
        pcrec_sb_printf(b,
            "        %s_co_ctx.vars = ctx->vars;\n"
            "        %s_co_ctx.nvars = ctx->nvars;\n", p, p);
    else
        pcrec_sb_printf(b,
            "        %s_co_ctx.vars = NULL;\n"
            "        %s_co_ctx.nvars = 0;\n", p, p);
    pcrec_sb_printf(b,
        "        slot_values[0] = (ptrdiff_t)ctx->pos;\n"
        "        r = %s(&%s_co_ctx);\n"
        "        slot_values[0] = %s_co_start;\n",
        o->callee_sym, p, p);
    const CsEdges edges = {
        .succ = o->pred ? pcrec_sb_fragf(a, "goto %s_L%d;", p, o->lbl)
                        : pcrec_sb_fragf(a, "{ scan_position += (size_t)r; goto %s_L%d; }",
                                         p, o->lbl),
        .fail = pcrec_sb_fragf(a, "goto %s_fail;", p),
        .prop = "return r;",
        .giveup = "{ run->callee_gave_up = 1; return r; }",
    };
    pcrec_callsite_emit(sb->cx, b, "        ", &o->callee, &edges);
    pcrec_sb_puts(b, "    }\n");
}

/* WITNESS: the test build's SIMD witness block (the knee's own bytes). */
static void vm_r_witness(VmBody *sb, const VmStmt *s)
{
    vm_renders(sb, s, VK_WITNESS);
#ifdef PCREC_SIMD_WITNESS
    pcrec_memfn_simd_witness(sb->b);
#endif
}

/* ---- the kind table ------------------------------------------------------ */

/* One row per kind: its name (diagnostics, the record reader) and its ONE
 * renderer. A kind without a row cannot be built (`vm_build`). */
typedef struct {
    VmKind      kind;
    const char *name;
    void      (*render)(VmBody *, const VmStmt *);
} VmKindRow;

static const VmKindRow vm_kind_rows[VK__COUNT] = {
    [VK_LABEL]        = { VK_LABEL,        "label",        vm_r_label },
    [VK_CHECKPOINT]   = { VK_CHECKPOINT,   "checkpoint",   vm_r_checkpoint },
    [VK_GOTO]         = { VK_GOTO,         "goto",         vm_r_goto },
    [VK_FAIL]         = { VK_FAIL,         "fail",         vm_r_fail },
    [VK_ACCEPT]       = { VK_ACCEPT,       "accept",       vm_r_accept },
    [VK_BRANCH]       = { VK_BRANCH,       "branch",       vm_r_branch },
    [VK_GUARD]        = { VK_GUARD,        "guard",        vm_r_guard },
    [VK_GUARD_END]    = { VK_GUARD_END,    "guard-end",    vm_r_guard_end },
    [VK_SWITCH]       = { VK_SWITCH,       "switch",       vm_r_switch },
    [VK_PUSH]         = { VK_PUSH,         "push",         vm_r_push },
    [VK_SET]          = { VK_SET,          "set",          vm_r_set },
    [VK_SNAPSHOT]     = { VK_SNAPSHOT,     "snapshot",     vm_r_snapshot },
    [VK_RESTORE]      = { VK_RESTORE,      "restore",      vm_r_restore },
    [VK_CUT]          = { VK_CUT,          "cut",          vm_r_cut },
    [VK_CUT_LOCAL]    = { VK_CUT_LOCAL,    "cut-local",    vm_r_cut_local },
    [VK_CALL]         = { VK_CALL,         "call",         vm_r_call },
    [VK_RETURN]       = { VK_RETURN,       "return",       vm_r_return },
    [VK_STEP]         = { VK_STEP,         "step",         vm_r_step },
    [VK_WORK]         = { VK_WORK,         "work",         vm_r_work },
    [VK_CONSUME]      = { VK_CONSUME,      "consume",      vm_r_consume },
    [VK_CONSUME_BACK] = { VK_CONSUME_BACK, "consume-back", vm_r_consume_back },
    [VK_SPAN]         = { VK_SPAN,         "span",         vm_r_span },
    [VK_SPAN_MOVE]    = { VK_SPAN_MOVE,    "span-move",    vm_r_span_move },
    [VK_SEEK]         = { VK_SEEK,         "seek",         vm_r_seek },
    [VK_LSET]         = { VK_LSET,         "lset",         vm_r_lset },
    [VK_BREF]         = { VK_BREF,         "bref",         vm_r_bref },
    [VK_VAR]          = { VK_VAR,          "var",          vm_r_var },
    [VK_CALLOUT]      = { VK_CALLOUT,      "callout",      vm_r_callout },
    [VK_WITNESS]      = { VK_WITNESS,      "witness",      vm_r_witness },
};

/* The kind's name, or "?" for a kind with no row. */
static const char *vm_kind_name(VmKind k)
{
    if ((unsigned)k < VK__COUNT && vm_kind_rows[k].name) return vm_kind_rows[k].name;
    return "?";
}

/* ---- building ------------------------------------------------------------ */

/* Opens the body on the Job's VM buffer, which the Job owns so the longjmp
 * cleanup path frees it. */
VmBody *pcrec_vm_stmt_open(Ctx *cx, const char *p, const char *up, bool tracing)
{
    VmBody *sb = pcrec_arena_alloc(&cx->arena, sizeof *sb);
    memset(sb, 0, sizeof *sb);
    sb->cx = cx;
    sb->b = &cx->job->vmsb;
    sb->p = p;
    sb->up = up;
    sb->tracing = tracing;
    sb->clock = pcrec_sb_len_uncut(sb->b);
    return sb;
}

/* Fails the compile when the body is not where the last record left it:
 * something wrote to it outside a renderer. */
static void vm_tile(VmBody *sb, const char *what)
{
    if (pcrec_sb_len_uncut(sb->b) == sb->clock) return;
    pcrec_ctx_fail(sb->cx, 0, "internal error: the VM body changed outside its "
                   "renderers (%zu bytes where the last record, %s #%d, left %zu) "
                   "before %s", pcrec_sb_len_uncut(sb->b),
                   sb->nrec ? vm_kind_name(sb->rec[sb->nrec - 1].kind) : "none",
                   sb->nrec, sb->clock, what);
}

/* THE ONE BUILD STEP every builder ends in: the tiling check, the kind's row,
 * the record appended, and its render into the body, timed by the clock. */
static void vm_build(VmBody *sb, VmStmt *s)
{
    const VmKindRow *row = (unsigned)s->kind < VK__COUNT ? &vm_kind_rows[s->kind] : NULL;
    if (!row || !row->render || row->kind != s->kind)
        pcrec_ctx_fail(sb->cx, 0, "internal error: VM record kind %d is not in "
                       "the kind table, so it has no renderer", (int)s->kind);
    if (sb->closed)
        pcrec_ctx_fail(sb->cx, 0, "internal error: a VM %s record built after the "
                       "body was closed by the class re-spelling", row->name);
    vm_tile(sb, row->name);
    if (sb->nrec == sb->reccap) {
        int ncap = sb->reccap ? sb->reccap * 2 : 256;
        VmStmt *nr = pcrec_arena_alloc(&sb->cx->arena, (size_t)ncap * sizeof *nr);
        if (sb->nrec) memcpy(nr, sb->rec, (size_t)sb->nrec * sizeof *nr);
        sb->rec = nr;
        sb->reccap = ncap;
    }
    VmStmt *r = &sb->rec[sb->nrec++];
    *r = *s;
    r->at = pcrec_sb_len_uncut(sb->b);
    r->tat = sb->b->len;
    row->render(sb, r);
    r->end = pcrec_sb_len_uncut(sb->b);
    r->tend = sb->b->len;
    sb->clock = r->end;
}

/* A zeroed record of kind `k`. */
static VmStmt vm_rec(VmKind k)
{
    VmStmt s;
    memset(&s, 0, sizeof s);
    s.kind = k;
    return s;
}

void pcrec_vm_b_label(VmBody *sb, int lbl, const char *role)
{
    VmStmt s = vm_rec(VK_LABEL);
    s.u.label.lbl = lbl;
    s.u.label.role = role;
    vm_build(sb, &s);
}

void pcrec_vm_b_checkpoint(VmBody *sb)
{
    VmStmt s = vm_rec(VK_CHECKPOINT);
    vm_build(sb, &s);
}

void pcrec_vm_b_goto(VmBody *sb, int lbl)
{
    VmStmt s = vm_rec(VK_GOTO);
    s.u.go.lbl = lbl;
    vm_build(sb, &s);
}

void pcrec_vm_b_fail(VmBody *sb)
{
    VmStmt s = vm_rec(VK_FAIL);
    vm_build(sb, &s);
}

void pcrec_vm_b_accept(VmBody *sb)
{
    VmStmt s = vm_rec(VK_ACCEPT);
    vm_build(sb, &s);
}

void pcrec_vm_b_branch(VmBody *sb, VmFrag c, VmTgt t)
{
    VmStmt s = vm_rec(VK_BRANCH);
    s.u.branch.c = c;
    s.u.branch.t = t;
    vm_build(sb, &s);
}

/* Opens a guard; the spelling is pushed so its close must name it. */
void pcrec_vm_b_guard(VmBody *sb, VmGuardSpell sp, VmFrag c)
{
    if (sb->gdepth == (int)(sizeof sb->gstack / sizeof sb->gstack[0]))
        pcrec_ctx_fail(sb->cx, 0, "internal error: VM guards nested too deep");
    VmStmt s = vm_rec(VK_GUARD);
    s.u.guard.c = c;
    s.u.guard.sp = sp;
    vm_build(sb, &s);
    sb->gstack[sb->gdepth++] = sp;
}

/* Closes the innermost guard, refusing a close in another spelling or with
 * no guard open. */
void pcrec_vm_b_guard_end(VmBody *sb, VmGuardSpell sp)
{
    if (sb->gdepth == 0 || sb->gstack[sb->gdepth - 1] != sp)
        pcrec_ctx_fail(sb->cx, 0, "internal error: a VM guard's close does not "
                       "match the guard it closes");
    VmStmt s = vm_rec(VK_GUARD_END);
    s.u.guard.sp = sp;
    vm_build(sb, &s);
    sb->gdepth--;
}

void pcrec_vm_b_switch(VmBody *sb, int depth, const VmCase *cases, int ncase)
{
    VmStmt s = vm_rec(VK_SWITCH);
    s.u.sw.depth = depth;
    s.u.sw.cases = cases;
    s.u.sw.ncase = ncase;
    vm_build(sb, &s);
}

void pcrec_vm_b_push(VmBody *sb, int lbl, VmPosKind pos, int loop)
{
    VmStmt s = vm_rec(VK_PUSH);
    s.u.push.lbl = lbl;
    s.u.push.pos = pos;
    s.u.push.loop = loop;
    vm_build(sb, &s);
}

/* A SET whose source is the slot's own value is a call site's park, which is
 * a SNAPSHOT (review r8 SOUND-7): refused here, so the two cannot be
 * confused. */
void pcrec_vm_b_set(VmBody *sb, int slot, const char *name, const char *src)
{
    if (strcmp(src, vm_slot_read(sb, slot, name)) == 0)
        pcrec_ctx_fail(sb->cx, 0, "internal error: a VM SET of slot %d copies "
                       "the slot onto itself; a self-copy is a SNAPSHOT", slot);
    VmStmt s = vm_rec(VK_SET);
    s.u.set.slot = slot;
    s.u.set.name = name;
    s.u.set.src = src;
    vm_build(sb, &s);
}

void pcrec_vm_b_snapshot(VmBody *sb, int slot, const char *name)
{
    VmStmt s = vm_rec(VK_SNAPSHOT);
    s.u.snap.slot = slot;
    s.u.snap.name = name;
    vm_build(sb, &s);
}

void pcrec_vm_b_restore(VmBody *sb, int slot, const char *name, int j)
{
    VmStmt s = vm_rec(VK_RESTORE);
    s.u.restore.slot = slot;
    s.u.restore.name = name;
    s.u.restore.j = j;
    vm_build(sb, &s);
}

void pcrec_vm_b_cut(VmBody *sb, int slot)
{
    VmStmt s = vm_rec(VK_CUT);
    s.u.cut.slot = slot;
    vm_build(sb, &s);
}

void pcrec_vm_b_cut_local(VmBody *sb, int loop)
{
    VmStmt s = vm_rec(VK_CUT_LOCAL);
    s.u.cut_local.loop = loop;
    vm_build(sb, &s);
}

void pcrec_vm_b_call(VmBody *sb, int ret)
{
    VmStmt s = vm_rec(VK_CALL);
    s.u.call.ret = ret;
    vm_build(sb, &s);
}

void pcrec_vm_b_return(VmBody *sb)
{
    VmStmt s = vm_rec(VK_RETURN);
    vm_build(sb, &s);
}

static void vm_b_step(VmBody *sb)
{
    VmStmt s = vm_rec(VK_STEP);
    vm_build(sb, &s);
}

void pcrec_vm_b_work(VmBody *sb, const char *count)
{
    VmStmt s = vm_rec(VK_WORK);
    s.u.work.count = count;
    vm_build(sb, &s);
}

void pcrec_vm_b_consume(VmBody *sb, VmFrag c, VmAdv adv, int k, int lbl)
{
    VmStmt s = vm_rec(VK_CONSUME);
    s.u.consume.c = c;
    s.u.consume.adv = adv;
    s.u.consume.k = k;
    s.u.consume.lbl = lbl;
    vm_build(sb, &s);
}

void pcrec_vm_b_consume_wcls(VmBody *sb, int wi, int lbl)
{
    VmStmt s = vm_rec(VK_CONSUME);
    s.u.consume.adv = VADV_WCLS;
    s.u.consume.wi = wi;
    s.u.consume.lbl = lbl;
    vm_build(sb, &s);
}

void pcrec_vm_b_consume_back(VmBody *sb, int loop, VmFrag c, int lbl)
{
    VmStmt s = vm_rec(VK_CONSUME_BACK);
    s.u.back.loop = loop;
    s.u.back.c = c;
    s.u.back.lbl = lbl;
    vm_build(sb, &s);
}

void pcrec_vm_b_span(VmBody *sb, int cap, const char *clamp, int stride,
               DelegSite id, const mf_site *site, const mf_hooks *h)
{
    VmStmt s = vm_rec(VK_SPAN);
    s.u.span.block = true;
    s.u.span.cap = cap;
    s.u.span.clamp = clamp;
    s.u.span.stride = stride;
    s.u.span.kit.k = VP_KIT;
    s.u.span.kit.id = id;
    s.u.span.kit.site = site;
    s.u.span.kit.hooks = *h;
    vm_build(sb, &s);
}

void pcrec_vm_b_span_init(VmBody *sb)
{
    VmStmt s = vm_rec(VK_SPAN);
    s.u.span.block = false;
    s.u.span.cap = -1;
    vm_build(sb, &s);
}

void pcrec_vm_b_span_move(VmBody *sb, VmSpanMove mv, int k)
{
    VmStmt s = vm_rec(VK_SPAN_MOVE);
    s.u.span_move.mv = mv;
    s.u.span_move.k = k;
    vm_build(sb, &s);
}

void pcrec_vm_b_seek(VmBody *sb, VmSeek sk, const char *slotx, int k)
{
    VmStmt s = vm_rec(VK_SEEK);
    s.u.seek.sk = sk;
    s.u.seek.slotx = slotx;
    s.u.seek.k = k;
    vm_build(sb, &s);
}

void pcrec_vm_b_lset(VmBody *sb, VmLocal x, VmLsetOp op, const char *src, int n,
               bool inl)
{
    VmStmt s = vm_rec(VK_LSET);
    s.u.lset.x = x;
    s.u.lset.op = op;
    s.u.lset.src = src;
    s.u.lset.n = n;
    s.u.lset.inl = inl;
    vm_build(sb, &s);
}

void pcrec_vm_b_bref(VmBody *sb, const VmBrefOps *o)
{
    VmStmt s = vm_rec(VK_BREF);
    s.u.bref = *o;
    vm_build(sb, &s);
}

void pcrec_vm_b_var(VmBody *sb, const VmVarOps *o)
{
    VmStmt s = vm_rec(VK_VAR);
    s.u.var = *o;
    vm_build(sb, &s);
}

void pcrec_vm_b_callout(VmBody *sb, const VmCalloutOps *o)
{
    VmStmt s = vm_rec(VK_CALLOUT);
    s.u.callout = *o;
    vm_build(sb, &s);
}

void pcrec_vm_b_witness(VmBody *sb)
{
    VmStmt s = vm_rec(VK_WITNESS);
    vm_build(sb, &s);
}

/* ---- the body's other readers ------------------------------------------ */

size_t pcrec_vm_stmt_program_bytes(const VmBody *sb)
{
    return pcrec_sb_len_decide(sb->b);
}

const char *pcrec_vm_stmt_text(const VmBody *sb)
{
    return sb->b->p ? sb->b->p : "";
}

/* [OPT-CLSPACK] the class-table re-spelling, moved verbatim from emit_vm.c's
 * `vm_cls_respell`: two passes over the same matches, the first sizing the
 * output, the second writing it; then the body is rewritten whole. The one
 * post-render rewrite of the body, declared: it runs after the last record,
 * on a body that tiles, and it closes the body. */
void pcrec_vm_stmt_respell(VmBody *sb, const char *needle, const char *const *from,
                     const char *const *to, int n)
{
    StrBuf *b = sb->b;
    vm_tile(sb, "the class re-spelling");
    char *out = NULL;
    size_t olen = 0;
    for (int pass = 0; pass < 2; pass++) {
        const char *q = b->p ? b->p : "", *hit;
        size_t o = 0;
        while ((hit = strstr(q, needle)) != NULL) {
            int r = 0;
            while (r < n && strncmp(hit, from[r], strlen(from[r])) != 0) r++;
            if (r == n)
                pcrec_ctx_fail(sb->cx, 0, "internal error: a class table read in "
                               "the VM program was not recorded, so the table "
                               "selection cannot re-spell it");
            size_t pre = (size_t)(hit - q), tl = strlen(to[r]);
            if (pass) { memcpy(out + o, q, pre); memcpy(out + o + pre, to[r], tl); }
            o += pre + tl;
            q = hit + strlen(from[r]);
        }
        size_t rest = strlen(q);
        if (pass) { memcpy(out + o, q, rest + 1); break; }
        olen = o + rest;
        out = pcrec_arena_alloc(&sb->cx->arena, olen + 1);
    }
    b->len = 0;
    if (b->p) b->p[0] = 0;
    pcrec_sb_puts(b, out);
    sb->clock = pcrec_sb_len_uncut(b);
    sb->closed = true;
}

/* ---- the frame ------------------------------------------------------------ */

/* The frame's own tiling: every row of the matcher's span is written through
 * FR_ROW, which first checks that the artifact buffer is where the previous
 * row left it, so a print added between rows is an internal error. */
typedef struct {
    Ctx    *cx;
    StrBuf *c;
    size_t  end;
} VmFrameW;

static void vm_fr_tile(VmFrameW *fw)
{
    if (pcrec_sb_len_uncut(fw->c) != fw->end)
        pcrec_ctx_fail(fw->cx, 0, "internal error: the VM matcher's span was "
                       "written outside its frame rows");
}
#define FR_ROW(fw, stmt) \
    do { vm_fr_tile(fw); stmt; (fw)->end = pcrec_sb_len_uncut((fw)->c); } while (0)

/* [FINDALL-NEXT] `<prefix>__match_notempty`, the find-all iterator's retry
 * matcher (findall_iter.md §3.3): `<prefix>_match_anchored`'s text,
 * written just above at `matcher_at`, again under its own name with one
 * line more at its accept label (`guard_at`): a match whose REPORTED span is
 * empty at `ctx->pos` is rejected and the program backtracks to its next
 * alternative, exactly as PCRE2's NOTEMPTY_ATSTART retry does. The reported
 * span is `[start, scan_position)` with `ctx->pos <= start <= scan_position`
 * (`start` is the `\K` slot where one was crossed), so it is empty AT
 * `ctx->pos` exactly when `scan_position == ctx->pos`; an empty span a `\K`
 * moved past `ctx->pos` (`ab\K`) is a match.
 *
 * A COPY, NOT A FLAG: a guard on a run-state flag in the one matcher costs
 * every search and match entry a load and a test at each accept, and
 * reshapes the out-of-line matcher (measured +10-14% on nullable
 * patterns); the program's computed goto keeps gcc from
 * inlining or cloning it, so only a second text keeps the entries' code
 * unchanged. Scaffold (§6.4): no length decision reads it. Written where the
 * retry table's winner needs it (`PCREC_ITER_NEEDS_GUARDED`), above the
 * `#undef`s, while the program's macros are defined. Moved from emit_vm.c's
 * `vm_emit_guarded_matcher`; its text is a byte copy of the rendered span,
 * so it follows the renderers. */
static void vm_fr_guarded_copy(VmBody *sb, VmFrameW *fw, size_t matcher_at,
                               size_t guard_at)
{
    StrBuf *c = fw->c;
    const char *name = pcrec_sb_fragf(&sb->cx->arena, "%s_match_anchored(", sb->p);
    const char *at = strstr(c->p + matcher_at, name);
    if (!at || (size_t)(at - c->p) > guard_at)
        pcrec_ctx_fail(sb->cx, 0, "internal error: the guarded matcher's source has "
                       "no `_match_anchored` head (src/gen/emit_vm.c)");
    const size_t name_at = (size_t)(at - c->p), end_at = c->len;
    const char *copy = pcrec_sb_fragf(&sb->cx->arena,
        "%.*s%s__match_notempty(%.*s"
        "    if (scan_position == ctx->pos) goto %s_fail;\n"
        "%.*s",
        (int)(name_at - matcher_at), c->p + matcher_at, sb->p,
        (int)(guard_at - name_at - strlen(name)), c->p + name_at + strlen(name),
        sb->p, (int)(end_at - guard_at), c->p + guard_at);
    FR_ROW(fw, (pcrec_sb_scaffold_open(c), pcrec_sb_puts(c, copy),
                pcrec_sb_scaffold_close(c)));
}

/* Writes `<prefix>_match_anchored`, the program, into `c`: its head and
 * declarations, the jump to L0, the body, the accept label and its return,
 * and the fail block (the pop-and-resume dispatch where the program pushes).
 * Moved from emit_vm.c's `vm_emit_search_body` (the text and its comments are
 * that function's); `f` carries every fact it reads. */
void pcrec_vm_stmt_frame(VmBody *sb, StrBuf *c, const VmFrame *f)
{
    const char *p = sb->p, *up = sb->up;
    VmFrameW fw = { sb->cx, c, pcrec_sb_len_uncut(c) };
    if (!sb->closed) vm_tile(sb, "the frame");
    if (sb->gdepth)
        pcrec_ctx_fail(sb->cx, 0, "internal error: the VM body ends inside a guard");
    const size_t matcher_at = c->len;   /* [FINDALL-NEXT] the guarded copy's source */
    FR_ROW(&fw, pcrec_sb_printf(c,
        "static %sptrdiff_t %s_match_anchored(const rx_ctx *ctx, %s_run_state *run%s%s)\n"
        "{\n"
        "    const unsigned char *const subject = ctx->subject;\n"
        "    const size_t subject_length = ctx->len;\n"
        "    size_t scan_position = ctx->pos;\n"
        "    ptrdiff_t *const slot_values = run->slot_values;\n",
        /* [CC-DIFF] STEP 2: `ai_body`, not `ai` — THIS is the function the
         * size term prices, and the SHARED rung keeps exactly one copy of it
         * while every thin helper above still inlines. */
        f->ai_body, p, p, f->mrl_param, f->gst_param));
    /* [K134] the trail checkpoints' trigger, a local so the check is one
     * compare against a register, started at the run's floor
     * (vm_emit_trail_compact). */
    if (f->trail_gc)
        FR_ROW(&fw, pcrec_sb_printf(c, "    size_t %s_trail_gc_at = %s_trail_gc_start(run);\n", p, p));
    if (f->span_cursor)
        FR_ROW(&fw, pcrec_sb_printf(c, "    size_t %s_span_cursor = 0;   /* the span-loop cursor (engine_m4.md 2.5):\n"
                     "                             a plain local, UNTRAILED, whose save\n"
                     "                             point is a resume frame */\n",
                  p));
    /* [ENG-BREP] the reverse-deterministic rung's working locals. All UNTRAILED
     * and all read only where they are provably live: `it`/`mk` inside the
     * forward scan, `c`/`prev`/`ns` inside one commit's own backward walk. What
     * has to survive a backtrack lives in slot_values (the three slots per loop) or in
     * the resume frame's recorded position, which is where the retreat target
     * rides.
     *
     * The capture-recovery arrays are SHARED across every revdet loop in the
     * program and sized by the widest body, because a walk's results are
     * published into slot_values before control leaves the loop that ran it — nothing
     * here outlives its own commit. */
    for (int i = 0; i < f->nrev_total; i++)
        FR_ROW(&fw, pcrec_sb_printf(c,
            /* [M6-READ] These suffixes MUST match the ones the use sites
             * NAMES (M6-READ): `cursor` is the walk cursor; `groups_seen`
             * is the count the walk has witnessed, tested against the group
             * count at the wstep label (`if (groups_seen >= ng)`);
             * `revdet_group_span[j][2]` is the span the backward walk
             * recovered for group j and `revdet_group_seen[j]` whether it has
             * been witnessed. Read off THIS file's own emission sites (the
             * `ga`/`gs`/`ns` locals and the "no group to witness" note),
             * which is where the rung's vocabulary actually lives.
             *
             * These suffixes MUST match the ones the use sites
             * compose with `%s_<suffix>` from the `rv` base -- they are the
             * same variable, spelled in two places. The rename moved the uses
             * and left the declarations, and a revdet artifact stopped
             * compiling; the two-artifact altcls differential caught it. */
            "    size_t %s_rv%d_cursor = 0; unsigned long %s_rv%d_iteration = 0;\n"
            "    size_t %s_rv%d_frame_mark = 0; ptrdiff_t %s_rv%d_prev_position = -1;\n"
            "    int %s_rv%d_groups_seen = 0;\n",
            p, i, p, i, p, i, p, i, p, i));
    if (f->nrev_total && f->nrevcaps) {
        FR_ROW(&fw, pcrec_sb_printf(c, "    ptrdiff_t %s_revdet_group_span[%d][2] = {{0}};\n", p, f->nrevcaps));
        FR_ROW(&fw, pcrec_sb_printf(c, "    unsigned char %s_revdet_group_seen[%d] = {0};\n", p, f->nrevcaps));
    }
    FR_ROW(&fw, pcrec_sb_puts(c, "    (void)subject; (void)subject_length; (void)slot_values;\n"));
    /* Four of the five per-loop locals are used only by shapes that do not
     * always occur — the walk cursor and `prev` exist only when a walk is
     * emitted, the seen-counter only when the body has groups, and (found by
     * [CC-CLANG]'s CLANGGEN sweep, not by inspection) `iteration` only where
     * a READER exists for it: the rmax-bound test at the scan head fires iff
     * `rmax >= 0` and the rmin tests at the commit/short labels fire iff
     * `rmin > 0`, so a bare unbounded `X*` (rmin 0, rmax -1) writes it
     * (reset, incremented every iteration) and never reads it at all —
     * gcc's `-Wunused-but-set-variable` does not catch a write-only local
     * reached through `x++` (measured: gcc accepts `((?<a>a)|(?<b>b))*`
     * clean at -Wall -Wextra -Werror), clang's does. `mk` (`frame_mark`) is
     * the only one of the five genuinely used by every shape — the cut it
     * feeds runs on every commit, rmin or rmax notwithstanding — and is
     * deliberately not listed, so a future shape that stops using it still
     * gets caught. The generated matcher is built -Wall -Wextra -Werror;
     * `--no-captures` on a possessified rung loop is the combination that
     * has none of the first three, and it failed -Wunused-variable before
     * this line existed. */
    for (int i = 0; i < f->nrev_total; i++)
        FR_ROW(&fw, pcrec_sb_printf(c, "    (void)%s_rv%d_cursor; (void)%s_rv%d_prev_position;"
                     " (void)%s_rv%d_groups_seen; (void)%s_rv%d_iteration;\n",
                  p, i, p, i, p, i, p, i));
    if (f->tracing)
        FR_ROW(&fw, pcrec_sb_printf(c, "    fprintf(stderr, \"[%s] enter at scan_position %%zu of %%zu\\n\","
                     " scan_position, subject_length);\n", p));
    FR_ROW(&fw, pcrec_sb_printf(c, "    goto %s_L0;\n\n", p));
    FR_ROW(&fw, pcrec_sb_splice(c, sb->b));   /* [MEMFN] RQ-3: the program's guarded record with it */
    /* The three trace lines. Built here rather than inline so the untraced
     * artifact's text is the SAME format string with three empty inserts —
     * one emitted shape, not two, for the same reason the traced macros above
     * keep the untraced order of operations: a debug build that took a
     * different path would be a tool that lies. */
    /* [M6-READ] Widened: the renamed emitted locals (pos -> scan_position,
     * w -> run, b_ -> frame_index) made every one of these trace strings
     * longer, and snprintf TRUNCATES rather than failing. gcc's
     * -Wformat-truncation caught two of the three; the third is widened with
     * them because a silently cut trace line is a debugging tool that lies. */
    /* Three more of the JUDGED shape above: an UNTRACED artifact's bytes are
     * identical because each insert is simply empty, which is what
     * run_vm_identity.sh's gate cares about and what a debug flag has no
     * business changing. The old comment below says so in those words. */
    const char *accept_tr = "", *fail_tr = "", *exhaust_tr = "";
    Arena *a = &sb->cx->arena;
    if (f->tracing) {
        /* [M6.2 wave E] ON A `\K` ARTIFACT THIS LINE SAYS BOTH SPANS, because
         * on such an artifact they are different and one of them alone is
         * misleading. `[ctx->pos, pos)` is what the PROGRAM consumed, which is
         * what a trace of the program should say; the REPORTED span starts at
         * the last crossed `\K`, and a reader watching `(?:a\K)*ab` retreat
         * would otherwise see "ACCEPT [0,4)" and the caller print "2 4" with
         * nothing connecting them. Emitted only where a `\K` exists, so a
         * `\K`-free traced artifact keeps its line byte for byte. */
        if (f->kreset)
            accept_tr = pcrec_sb_fragf(a,
                     "    fprintf(stderr, \"[%s] ACCEPT consumed [%%zu,%%zu)"
                     " reported [%%td,%%zu)\\n\", ctx->pos, scan_position,"
                     " slot_values[0] != PCREC_UNSET ? slot_values[0] : (ptrdiff_t)ctx->pos,"
                     " scan_position);\n", p);
        else
            accept_tr = pcrec_sb_fragf(a,
                     "    fprintf(stderr, \"[%s] ACCEPT [%%zu,%%zu)\\n\","
                     " ctx->pos, scan_position);\n", p);
        fail_tr = pcrec_sb_fragf(a,
                 "    fprintf(stderr, \"[%s] backtrack: %%zu frame(subject), trail %%zu\\n\","
                 " run->resume_depth, run->trail_depth);\n", p);
        /* A separate guarded statement rather than a brace around the
         * existing one: that keeps the UNTRACED artifact's bytes identical
         * (the insert is simply empty), which is what run_vm_identity.sh's
         * gate cares about and what a debug flag has no business changing. */
        exhaust_tr = pcrec_sb_fragf(a,
                 "    if (run->resume_depth == 0)\n"
                 "        fprintf(stderr, \"[%s] FAIL: resume stack empty\\n\");\n",
                 p);
    }
    /* `has_push` is derived ABOVE, beside the `<PREFIX>_VM_FRAMELESS` stamp
     * it is also read by — one derivation, two readers of the same bool
     * ([OPT-VMFL] STEP 0 §4.2). */
    /* [CC-CLANG] The fail label's own comment claims "THE ONLY ... INDIRECT
     * JUMP", which is exactly untrue on a FRAMELESS program (has_push
     * false, below): there is no `goto *` left in that case at all. The
     * comment is selected on the same predicate that omits the dispatch,
     * rather than left to describe a jump the artifact no longer contains. */
    FR_ROW(&fw, pcrec_sb_printf(c, "\n%s_accept: __attribute__((unused));\n", p));
    FR_ROW(&fw, (pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL),
    pcrec_sb_puts(c,
        "    /* 3.1: leftmost-first is FIRST COMPLETE MATCH WINS, not compare\n"
        "     * candidates. The VM returns here immediately and the capture\n"
        "     * slots at this instant are the answer -- no candidate comparison,\n"
        "     * no longest-wins, no second pass. The caller's capture_spans array is\n"
        "     * filled by the ENTRY, not here (3.4). */\n"),
    pcrec_sb_cmt_close(c)));
    const size_t guard_at = c->len;   /* where the guarded copy's accept test goes */
    FR_ROW(&fw, pcrec_sb_printf(c,
        "%s"
        "    return (ptrdiff_t)(scan_position - ctx->pos);\n"
        "\n%s_fail: __attribute__((unused));\n",
        accept_tr, p));
    FR_ROW(&fw, (pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL),
    pcrec_sb_puts(c,
        f->has_push
          ? "    /* THE ONLY BACKTRACKER AND THE ONLY INDIRECT JUMP.\n"
            "     * A step is one backtrack resumption (4.2), counted at exactly\n"
            "     * this place -- so forward progress is FREE (a linear match over\n"
            "     * 100 MB costs zero steps), the steps_left is subject-length-\n"
            "     * independent, and the counter measures precisely the thing it is\n"
            "     * meant to bound. D22: DD-2 is ROBUSTNESS, not a security\n"
            "     * boundary, and it must not be traded against execution speed. */\n"
          : "    /* [CC-CLANG] THE ONLY BACKTRACKER, AND THIS PROGRAM PUSHES\n"
            "     * NO RESUME FRAME AT ALL (no RX_PUSH site, no linked\n"
            "     * subroutine call anywhere in the tree) -- so there is no\n"
            "     * indirect jump here, and the pop-and-resume dispatch below\n"
            "     * is omitted rather than emitted dead. A step is one\n"
            "     * backtrack resumption (4.2), counted at exactly this place\n"
            "     * -- forward progress is FREE, the steps_left is subject-\n"
            "     * length-independent, and the counter measures precisely the\n"
            "     * thing it is meant to bound. D22: DD-2 is ROBUSTNESS, not a\n"
            "     * security boundary, and it must not be traded against\n"
            "     * execution speed. */\n"),
    pcrec_sb_cmt_close(c)));
    FR_ROW(&fw, pcrec_sb_printf(c,
        "%s%s%s",
        fail_tr, exhaust_tr,
        /* [CC-CLANG] `has_push` false means `run->resume_depth` can never
         * leave 0, so the guard on the return is not merely redundant but
         * actively wrong to emit AS a guard: an `if` with no covering `else`
         * leaves the compiler unable to see that every path returns, and
         * both gcc and clang reject the resulting fall-off-the-end with
         * `-Wreturn-type` under this project's own default `-Werror`
         * GENCFLAGS. The honest text is the unconditional return the proof
         * already licenses, not a conditional one dressed as always-true. */
        f->has_push ? "    if (run->resume_depth == 0) return -1;\n"
                    : "    return -1;\n"));
    /* [CC-CLANG] The budget decrement below is reachable only past the
     * return just emitted, so on a frameless artifact (has_push false) it
     * would be unreachable dead code -- omitted for the same reason the
     * pop-and-resume block is, not merely to silence a warning. */
    if (f->has_budget && f->has_push)
        FR_ROW(&fw, pcrec_sb_printf(c, "    if (--run->steps_left < 0) return %s_R_STEPS;\n", up));
    if (!f->has_push) {
        /* [CC-CLANG] `has_push` is false: no `RX_PUSH` and no linked
         * subroutine call exists anywhere in this program, so the
         * unconditional return just emitted always fires and the
         * pop-and-resume block that would otherwise follow is unreachable —
         * omitted rather than emitted dead, and taking the one indirect jump
         * this file's own header counts (the fail label) down to none. */
        FR_ROW(&fw, pcrec_sb_puts(c, "}\n\n"));
    } else {
        const char *pop_tr = "";
        if (f->tracing)
            pop_tr = pcrec_sb_fragf(a,
                     "        fprintf(stderr, \"[%s] pop   #%%zu resume L%%d at"
                     " scan_position %%zu (rewind trail %%zu -> %%zu)\\n\",\n"
                     "                frame_index, run->resume_stack[frame_index].id, scan_position, run->trail_depth,"
                     " run->resume_stack[frame_index].trail_mark);\n", p);
        FR_ROW(&fw, pcrec_sb_printf(c,
            "    {\n"
            "        const size_t frame_index = --run->resume_depth;\n"
            "        scan_position = run->resume_stack[frame_index].resume_position;\n"
            "%s"
            "%s", pop_tr,
            /* [DD-14 wave B+C] §5.5's ONE ADDED LINE, and it restores WHICH
             * ACTIVATION IS CURRENT — exactly as the line above it restores
             * `scan_position` and the loop below it rewinds the trail.
             *
             * IT RUNS FOR EVERY FRAME AND NEEDS NO BRANCH, which is what a
             * call frame's `resume_label` being the fail label itself buys
             * (see `RX_CALL`): the fail label needs no knowledge of frame
             * kinds, so this is a line rather than a test.
             *
             * §5.5's DRAWN CELL IS WHY IT IS NOT OPTIONAL, and this lane
             * REPRODUCED it before adding the line: on `^(a(?1)?b)$` / "aaabbb"
             * the retreat pops the innermost call frame and then an ordinary
             * alternation frame INSIDE the enclosing activation, and without
             * this restore `call_top` still names the POPPED call frame — so
             * the enclosing activation's return reads `trail_mark` one level
             * too deep and restores the wrong values. Measured on the traced
             * artifact: group 1 came back (2,5) where it must be (1,5), one
             * level off at every depth, and the whole match was lost.
             *
             * THE DESIGN CALLS THIS "the fail label's TWO lines" (§5.1/§5.5).
             * Under D71.1 the second — `call_depth = resume_stack[..].call_mark`
             * — does not exist in the default artifact at all, because the
             * recursion-depth COUNTER moved to a diagnostic generation axis
             * and calls consume ordinary frames. S-SR2 names THIS line, which
             * §9.3 already records as the one whose deletion changes answers;
             * S-SR2a, the other line's row, moves to that axis with it.
             *
             * EMITTED ONLY ON A CALL-BEARING ARTIFACT — §9.1's byte-identity
             * claim, held by construction rather than by a filtered diff. */
            f->has_linked_calls
              ? "        run->call_top = run->resume_stack[frame_index]"
                ".call_top;\n"
              : ""));
        FR_ROW(&fw, pcrec_sb_puts(c,
            "        while (run->trail_depth > run->resume_stack[frame_index].trail_mark) {\n"
            "            run->trail_depth--;\n"
            "            slot_values[run->trail[run->trail_depth].slot_index] = run->trail[run->trail_depth].saved_value;\n"
            "        }\n"
            "        goto *run->resume_stack[frame_index].resume_label;\n"
            "    }\n"
            "}\n\n"));
    }
    if (f->guarded_copy) vm_fr_guarded_copy(sb, &fw, matcher_at, guard_at);
    vm_fr_tile(&fw);
}
