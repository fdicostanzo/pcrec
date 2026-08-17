# S57 — [ENG-BREP counter-K] A RESUME LABEL MADE TO READ AN UNTRAILED LOOP
# LOCAL, across a trip boundary.
#
# Counter-K makes slot and local SHARING ACROSS TRIPS load-bearing in a way
# replication never did: ONE emitted body copy is re-entered at every iteration,
# so any per-loop local inside that body is reused where replication gave each
# copy its own. That is safe today only because of an invariant stated in
# exactly one comment (`src/gen/emit_vm.c`, the cursor rung's retreat note) — a
# resume label reads only TRAILED slots or `pos`, never an untrailed local.
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
SAB_ID="S57-counter-trip-local"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="counterkdiff"
SAB_DESC="the nested cursor rung's low-water slot becomes an untrailed store, so an outer counter trip resumes reading a value a later inner iteration wrote"
SAB_DOC_FIGURE="docs/design/counterk_impl/counterk_design.md §8.4 (S57 and the invariant it attacks)"
SAB_COUNT=1
SAB_BEFORE='        vm_set(v, low, "(ptrdiff_t)pos",
               "span-loop low-water mark (loop entry pos)");'
SAB_AFTER='        sb_printf(v->b, "    stv[%d] = (ptrdiff_t)pos;\n", low);  /* SABOTAGE S57 */'
