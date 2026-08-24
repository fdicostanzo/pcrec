# S151 ([DD-14] wave B+C, design SS9.3 S-SR6c) -- `W` INCLUDES THE EMPTY_GUARD FAMILY.
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
# ARGUED, NOT MEASURED, AND THE ROW SAYS SO. Design SS5.3b measured two
# families and reasoned about five; this is one of the five, and its prediction
# is stated AS a prediction so a matrix run that scores it UNDETECTED is a
# FINDING about the row rather than about the compiler.
#
# THE ARGUMENT: the guard slot is written at an iteration's ENTRY and read at
# that iteration's END, so two ACTIVATIONS of the same emitted copy share it
# and the outer loop's guard reads the inner's position -- an empty iteration
# admitted, or a legal one refused.
#
# ITS POPULATION IS THE NARROWEST OF THE SEVEN, and that is MEASURED rather
# than assumed: the guard is not emitted for "a nullable body", it is emitted
# for an UNBOUNDED FRAMES-RUNG quantifier with a nullable body. `^(a?){0,5}$`
# allocates NONE while `^(a?)*$` and `^(a?)+$` allocate one each. So a cell
# written with a bounded repeat would go green on a broken compiler, and the
# design says so in terms.
#
# THE DESIGN'S OWN INSTRUCTION, if this row is UNDETECTED: replace the
# prediction with the measured cell, or DROP THE ROW. A row whose signal
# nobody has seen is a row that certifies nothing, and keeping it would be
# worse than not having written it.
SAB_ID="S151-w-drops-emptyguard"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="W drops the SLOT_EMPTY_GUARD<n> family, so two ACTIVATIONS of one unbounded frames-rung quantifier share its empty-iteration guard and the outer loop's guard reads the inner's position"
SAB_DOC_FIGURE="ARGUED, not measured (design 5.3b). PREDICTED: an admitted empty iteration (PCREC_ERR_STEPS) or a refused legal one. THE CELL MUST USE AN UNBOUNDED QUANTIFIER -- MEASURED, a bounded repeat allocates NO guard at all (^(a?){0,5}\$ allocates none while ^(a?)*\$ and ^(a?)+\$ allocate one each), so a {0,5} cell would go green on a broken compiler. quantified.rxt's nullable-callee-under-* cells are the population. If this row scores UNDETECTED the design's own instruction applies: replace the prediction with a measured cell or DROP the row."
SAB_COUNT=1
SAB_BEFORE='            vm_w_range(base[i], nstate,
                       vm_slot_guard(&v, snap_before[i].guard),
                       vm_slot_guard(&v, snap_after[i].guard));'
SAB_AFTER='            /* SABOTAGE S151: the EMPTY_GUARD family leaves W */'
