# S152 ([DD-14] wave B+C, design SS9.3 S-SR6d) -- `W` INCLUDES THE RUNG (SPAN_LOW / REVDET / COUNTER) FAMILY.
#
# THE ROW THIS DESIGN HAD REFUTED TWICE, and this file is one of the five it
# was split into. `W` is the ACTIVATION-PRIVATE RESTORE SET: every slot
# instance the emitted callee region can write, saved at the call and put back
# at the return. The first version of the design restored the captures
# REACHABLE FROM the callee's body; the second restored the capture SLOTS; and
# R34's C2 panel refuted the second with TWO EXECUTED PROTOTYPES showing SIX
# MORE FAMILIES missing.
#
# WHY EVERY FAMILY, in one sentence: each is written at a construct's ENTRY
# and read at that construct's EXIT, and two ACTIVATIONS of one construct are
# NESTED rather than sequential -- so the inner activation's write is still in
# the slot when the outer activation reads it. That sentence is true of all
# seven families and is the reason the rule is "every family" rather than a
# list somebody curated.
#
# FIVE ROWS AND NOT ONE, deliberately. A single row deleting the whole builder
# would prove the RULE and nothing about any PARTICULAR family; each of these
# deletes exactly one family's slot range from `W` and leaves the other six.
#
# ARGUED, NOT MEASURED, like S151 -- and THREE families in one row rather than
# three rows, because they are one claim: rung state is per EMITTED COPY, and
# a call re-enters a copy rather than running a second one.
#
# THE ARGUMENT IS ALREADY IN THIS TREE, one construct over.
# `counterk_design.md` RULED the iteration counter a TRAILED slot rather than a
# C local, and its stated reason is "a body-internal frame from iteration 1
# resumes reading a stale local". A nested ACTIVATION is that argument with a
# second index: same copy, same slot, two live readers.
#
# TWO SITES, and they are two because the builder writes the three ranges in
# two adjacent statements -- SPAN_LOW alone, then REVDET and COUNTER together.
# Splitting them across `SAB_FILE`/`SAB_FILE2` is what lets `replace.py` keep
# `SAB_COUNT=1` honest at both.
#
# WHICH RUNG A BODY GETS IS A COMPILE-TIME CHOICE THIS ROW CANNOT FIX, which
# design SS9.3 records: the cell has to be written against the LANDED rung
# selection rather than against a rung the design picked.
SAB_ID="S152-w-drops-rungs"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="W drops the three RUNG families (SPAN_LOW, REVDET, COUNTER), so a callee containing a quantifier called at two depths shares its rung state across activations -- counterk_design's own reason for making the counter TRAILED, with a second index"
SAB_DOC_FIGURE="ARGUED, not measured (design 5.3b). counterk_design.md's OWN reason for making the counter a TRAILED slot rather than a local -- \"a body-internal frame from iteration 1 resumes reading a stale local\" -- is this argument with a second index. The detector is a callee containing an {n,m} loop called at two depths; WHICH RUNG that body gets is a compile-time choice this row cannot fix, so the cell is written against the LANDED rung selection and quantified.rxt is the population."
SAB_COUNT=1
SAB_BEFORE='            vm_w_range(base[i], nstate,
                       vm_slot_low(&v, snap_before[i].low),
                       vm_slot_low(&v, snap_after[i].low));'
SAB_AFTER='            /* SABOTAGE S152: the SPAN_LOW family leaves W (and so do
             * REVDET and COUNTER, at the second site) */'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='            vm_w_range(base[i], nstate,
                       vm_slot_rev(&v, snap_before[i].rev, 0),
                       vm_slot_rev(&v, snap_after[i].rev, 0));
            vm_w_range(base[i], nstate,
                       vm_slot_ctr(&v, snap_before[i].ctr),
                       vm_slot_ctr(&v, snap_after[i].ctr));'
SAB_AFTER2='            /* SABOTAGE S152 (second site): REVDET and COUNTER too */'
