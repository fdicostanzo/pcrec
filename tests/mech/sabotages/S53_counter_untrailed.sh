# S53 — [ENG-BREP counter-K] THE COUNTER SLOT MADE UNTRAILED.
#
# The iteration counter is a TRAILED `stv` slot, and §2.2 is the argument for
# why it cannot be a plain local: one emitted body copy is re-entered at every
# iteration, so a resume into a body-internal choice point must find the counter
# at the value that iteration had. A plain store leaves the LAST value written,
# which is the value of whatever iteration ran most recently — not the one being
# resumed into.
#
# THIS IS THE RUNG'S CENTRAL CORRECTNESS CLAIM, and it is worth having a row
# rather than a paragraph: the note's own first draft proposed an untrailed
# local as a "saving" for the possessive arm, and R25 E5 showed it was a
# mandatory-phase MISCOMPILE. The saving was withdrawn; this row is what keeps
# it withdrawn.
#
# The witness must have a body with an INTERNAL CHOICE POINT — a body with none
# never resumes inside itself and cannot see the difference. `((a)|ab){0,12}c`
# and its siblings in patterns.txt are exactly that, and they select the counter
# rung at the default K (12 > 8), which R25 E2 makes a requirement rather than a
# hope: a witness that does not select the strategy tests the rung below it.
# RE-AIMED 2026-11-04 (lane mechtri3): the vmrec record-first refactor (3bc599c92) removed v->b, so
# the old direct pcrec_sb_printf no longer builds. The plant is now a PAIR: the emit_vm.c site marks its
# source with a leading \x02, and vm_r_set (src/gen/vm_stmt.c) prints a marked source as a plain
# slot_values[] store instead of the trailed SET. Same defect: the value is written, the old one is not trailed.
# MARKER CHANGED 2026-11-04 (lane mechfix1): the first re-aim marked the source with \x01, which is
# PCREC_PREFIX_LEAD (the prefix placeholder every vm_rolef text starts with), so vm_r_set's untrailed
# branch fired on EVERY prefixed source and printed an unrewritten `q_...` name. \x02 is unused.
SAB_ID="S53-counter-untrailed"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="counterkdiff"
SAB_DESC="the counter's per-trip increment becomes a plain untrailed store, so a resume into a body choice point reads the wrong iteration count"
SAB_DOC_FIGURE="docs/design/counterk_impl/counterk_design.md §2.2"
#
# RE-AIMED 2026-09-18 (lane w2b, [REVW.2] wave 2 stage 3). The trip increment's value text was a `char val[64]`
# and is now an inline `vm_rolef` fragment, so the anchored `vm_set` call
# carries the value expression instead of a variable name and wraps onto a
# second line. The plant is unchanged in substance: the SAME value text goes
# out through a plain untrailed store instead of through `vm_set`, which is
# what this row tests -- so the AFTER now spells the value expression where it
# used to spell `val`.
# The PLANT and its INTENT are UNCHANGED; the row was re-driven SOLO after the
# re-aim rather than assumed (see docs/dev/lanes/w2b_report.md).
SAB_COUNT=1
SAB_BEFORE='            vm_set(v, ctr, vm_rolef(v, "slot_values[%d] + %d", ctr, K),
                   "counter rung: += K, once per TRIP");'
SAB_AFTER='            vm_set(v, ctr, vm_rolef(v, "\x02slot_values[%d] + %d", ctr, K),   /* SABOTAGE S53 */
                   "counter rung: += K, once per TRIP");'
SAB_FILE2="src/gen/vm_stmt.c"
SAB_BEFORE2='    vm_renders(sb, s, VK_SET);
    vm_set_line(sb, s->u.set.slot, s->u.set.name, s->u.set.src);'
SAB_AFTER2='    vm_renders(sb, s, VK_SET);
    if (s->u.set.src[0] == '\''\x02'\'') {   /* SABOTAGE untrailed */
        pcrec_sb_printf(sb->b, "    slot_values[%d] = %s;\n", s->u.set.slot, s->u.set.src + 1);
        return;
    }
    vm_set_line(sb, s->u.set.slot, s->u.set.name, s->u.set.src);'
SAB_COUNT2=1
