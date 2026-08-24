# S150 ([DD-14] wave B+C, design SS9.3 S-SR6b) -- `W` INCLUDES THE CUT_MARK FAMILY.
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
# AXIS C IS MEASURED TOO, AND THE FAILURE IS A FALSE MATCH -- six of them.
# `^((?>a(?1)?))a$` matches NOTHING on 10.46 at any length. One mark slot per
# atomic group per EMITTED COPY; the inner activation's mark overwrites the
# outer's, so the outer's `RX_CUT` -- which is an ASSIGNMENT,
# `run->resume_depth = slot_values[slot]` -- becomes a NO-OP.
#
#     W as first written   4 agree,  6 DISAGREE (false matches on "aa".."aaaaaaaa")
#     W + the mark slot   10 agree,  0 DISAGREE
#
# AND THE FALSE-MATCH SET IS EXACTLY THE NON-ATOMIC CONTROL'S LANGUAGE: every
# broken cell equals `^((?:a(?1)?))a$`'s answer. The bug is not "the answer
# differs", it is *the atomic group stopped being atomic* -- a NAMEABLE
# miscompile, which is why the row is a class rather than an instance and why
# `slotfamilies.rxt` carries the non-atomic control beside it.
#
# THE CELL NEEDS AN ATOMIC GROUP LIVE AT TWO DEPTHS. A cell with an atomic
# group the call never re-enters has one activation of the mark and goes
# green.
SAB_ID="S150-w-drops-cutmark"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
# [DD-14 wave B+C] EXPECTED UNDETECTED, and the expectation is CHECKED.
# The sabotage is real and verified applied; this corpus cannot see it
# yet. SAB_DOC_FIGURE above records the measurement and names exactly
# what would have to exist for this row to close. If the matrix ever
# reports NOW DETECTED here, some wave built that witness: re-measure,
# then flip this to DETECTED -- do not delete the row.
SAB_EXPECT=UNDETECTED
SAB_HARNESS_TARGET="tests/recursion/slotfamilies.rxt"
SAB_DESC="W drops the SLOT_CUT_MARK<n> family, so a recursive activation overwrites the outer's mark and the outer's RX_CUT -- an ASSIGNMENT -- becomes a no-op: the atomic group stops being atomic, and the false-match set is exactly the non-atomic control's language"
SAB_DOC_FIGURE="MEASURED (design 5.3b axis C): W as first written gives 4 agree / 6 DISAGREE -- ^((?>a(?1)?))a\$ FALSE-MATCHES \"aa\"..\"aaaaaaaa\", which 10.46 matches at no length. W plus the mark slot is 10/0. || MEASURED UNDETECTED at [DD-14] wave B+C's close: corpus 0fail/47pass, recdiff 0fail/7pass, WITH THE SABOTAGE VERIFIED APPLIED (the artifact for ^((?>a(?1)?))a\$ shows RX_SLOT_CUT_MARK1 gone from the call site's saves) and the answers unchanged -- nomatch at every length 2..8, which is correct. THE FINDING IS ABOUT THE LINKAGE, and it is a divergence from 5.3b's own measurement rather than from the compiler: that axis was measured on a PROTOTYPE with ONE emitted copy of the atomic group entered from both the lexical path and the call, while under CALL_LINKAGE the lexical occurrence and the region are SEPARATE code with SEPARATE mark slots (CUT_MARK0 and CUT_MARK1 in that artifact). The clobber therefore needs two ACTIVATIONS OF THE REGION and an outer cut whose truncation MATTERS -- and the outer cut then reads a LARGER depth, which discards FEWER frames rather than resurrecting a match on these subjects. THE SHIPPED BEHAVIOUR IS UNCHANGED AND CORRECT (the family IS in W); what is owed is a witness that makes the under-cut observable, and until one exists this row certifies less than its text claims."
SAB_COUNT=1
SAB_BEFORE='            vm_w_range(base[i], nstate,
                       vm_slot_mark(&v, snap_before[i].mark),
                       vm_slot_mark(&v, snap_after[i].mark));'
SAB_AFTER='            /* SABOTAGE S150: the CUT_MARK family leaves W */'
