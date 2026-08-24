# S153 ([DD-14] wave B+C, design SS9.3 S-SR6e) -- `W` INCLUDES THE LOOKAROUND (LOOK_MARK / LOOK_POS) FAMILY.
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
# ARGUED, AND THE DESIGN'S OWN FIRST VERSION PREDICTED THE OPPOSITE. SS12 P-2
# named exactly these two families as candidates and argued they were SAFE,
# "because each is re-initialised at its own entry label on every entry". That
# prediction is WITHDRAWN, and the sentence that withdraws it is the most
# transferable line in SS5.3a:
#
#     The re-initialisation is not the question; the OVERWRITE is.
#     A slot re-initialised at entry has been overwritten FOR ITS CALLER.
#
# THE FAMILY THE DESIGN COULD NOT MEASURE, because `[M6.6.2]` had not landed
# when it was written -- so SS9.3 recorded the row as "NOT LANDABLE UNTIL
# `[M6.6.2]` DOES" and asked this wave to either land it or say why not. It
# lands: module `lookaround` ships, both slot families exist, and
# `inlookaround.rxt` carries calls inside a lookahead and inside an atomic
# group.
#
# WHAT ITS POPULATION DOES NOT YET CONTAIN is a RECURSIVE call inside a
# lookaround with the assertion live at two depths, which is the shape SS12 P-2
# predicts fails. The cells that exist are calls inside assertions rather than
# assertions inside recursions, so a matrix run scoring this UNDETECTED is a
# finding about the POPULATION and the row should gain such a cell rather than
# be dropped.
SAB_ID="S153-w-drops-look"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/inlookaround.rxt"
SAB_DESC="W drops the SLOT_LOOK_MARK / SLOT_LOOK_POS families, so a recursive call INSIDE a lookaround shares the assertion's cut mark and saved cursor across activations"
SAB_DOC_FIGURE="ARGUED (design 5.3b), and the design's OWN FIRST VERSION PREDICTED THESE TWO WERE SAFE -- 12 P-2 named SLOT_LOOK_MARK/_POS as candidates and argued they were fine \"because each is re-initialised at its own entry label on every entry\". THAT PREDICTION IS WITHDRAWN: the re-initialisation is not the question, the OVERWRITE is. A slot re-initialised at entry has already been overwritten for its caller."
SAB_COUNT=1
SAB_BEFORE='            vm_w_range(base[i], nstate,
                       vm_slot_lookmark(&v, snap_before[i].lookmark),
                       vm_slot_lookmark(&v, snap_after[i].lookmark));
            vm_w_range(base[i], nstate,
                       vm_slot_lookpos(&v, snap_before[i].lookpos),
                       vm_slot_lookpos(&v, snap_after[i].lookpos));'
SAB_AFTER='            /* SABOTAGE S153: the two LOOKAROUND families leave W */'
