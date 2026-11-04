# S57 — [ENG-BREP counter-K] A RESUME LABEL MADE TO READ AN UNTRAILED LOOP
# LOCAL, across a trip boundary.
#
# Counter-K makes slot and local SHARING ACROSS TRIPS load-bearing in a way
# replication never did: ONE emitted body copy is re-entered at every iteration,
# so any per-loop local inside that body is reused where replication gave each
# copy its own. That is safe today only because of an invariant stated in
# exactly one comment (`src/gen/emit_vm.c`, the cursor rung's retreat note) — a
# resume label reads only TRAILED slots or `scan_position`, never an untrailed local.
#
# Counter-K does not introduce the invariant; it makes it carry weight it has
# not carried before, and an invariant with no check is a sentence [R25 E16].
#
# THE WITNESS IS A NESTED LOOP: a cursor rung INSIDE a counter loop at
# NOPT > K — `(x(?:ab){2,4}){0,12}c` and `(x(?:ab){2,4}){0,17}c` in
# patterns.txt. That is the only shape where an untrailed inner local is read
# across an OUTER trip boundary; a flat counter loop cannot express it, which is
# why the stride axis is not merely about §7.4's division.
#
# The sabotage removes the trailing from the inner cursor rung's low-water slot,
# turning it into exactly the untrailed local the invariant forbids.
# RE-AIMED 2026-11-04 (lane mechtri3): the vmrec record-first refactor (3bc599c92) removed v->b, so
# the old direct pcrec_sb_printf no longer builds. The plant is now a PAIR: the emit_vm.c site marks its
# source with a leading \x01, and vm_r_set (src/gen/vm_stmt.c) prints a marked source as a plain
# slot_values[] store instead of the trailed SET. Same defect: the value is written, the old one is not trailed.
SAB_ID="S57-counter-trip-local"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="counterkdiff"
SAB_DESC="the nested cursor rung's low-water slot becomes an untrailed store, so an outer counter trip resumes reading a value a later inner iteration wrote"
SAB_DOC_FIGURE="docs/design/counterk_impl/counterk_design.md §8.4 (S57 and the invariant it attacks)"
SAB_COUNT=1
SAB_BEFORE='        vm_set(v, low, "(ptrdiff_t)scan_position",
               "span-loop low-water mark (loop entry scan_position)");'
SAB_AFTER='        vm_set(v, low, "\x01(ptrdiff_t)scan_position",   /* SABOTAGE S57 */
               "span-loop low-water mark (loop entry scan_position)");'
SAB_FILE2="src/gen/vm_stmt.c"
SAB_BEFORE2='    vm_renders(sb, s, VK_SET);
    vm_set_line(sb, s->u.set.slot, s->u.set.name, s->u.set.src);'
SAB_AFTER2='    vm_renders(sb, s, VK_SET);
    if (s->u.set.src[0] == '\''\x01'\'') {   /* SABOTAGE untrailed */
        pcrec_sb_printf(sb->b, "    slot_values[%d] = %s;\n", s->u.set.slot, s->u.set.src + 1);
        return;
    }
    vm_set_line(sb, s->u.set.slot, s->u.set.name, s->u.set.src);'
SAB_COUNT2=1
