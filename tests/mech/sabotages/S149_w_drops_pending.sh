# S149 ([DD-14] wave B+C, design SS9.3 S-SR6a) -- `W` INCLUDES THE PENDING FAMILY.
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
# AXIS P IS MEASURED, NOT ARGUED, and the failure is a LOST MATCH (two of
# them). `^(a(?1)?b)\1$`: the backreference MARKS group 1, so it lowers
# publish-at-close -- the open position goes to a PENDING slot and the pair is
# published together at the close. The inner activation overwrites the outer's
# pending value, so the outer publishes the wrong start.
#
#     W as first written (captures only)   11 agree,  2 DISAGREE
#     W + the pending slot                 13 agree,  0 DISAGREE
#
# THE CELL NEEDS A GROUP A BACKREFERENCE NAMES, and design SS9.3 says so: an
# unmarked group is not marked, the family is never allocated, and the row
# would go GREEN on a broken compiler. `slotfamilies.rxt` is that file and it
# declares `features recursion,backrefs`.
#
# AND THIS MODULE WIDENS THE MARKED SET, which is worth knowing before reading
# the population. `pcrec_bref_mark` marks CALL TARGETS too (design SS4.3, so
# `--no-captures` cannot delete a called group), and `Vm.pend_of` is built
# from that same mark set -- so EVERY CALLED GROUP now lowers publish-at-close
# whether or not a backreference names it. That is sound (publish-at-close was
# measured at 0 divergences over 5,808 cells) and it makes this family's
# population the whole module rather than the backref half of it.
SAB_ID="S149-w-drops-pending"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/slotfamilies.rxt"
SAB_DESC="W drops the SLOT_GROUP<n>_PENDING family, so a recursive activation overwrites the outer activation's publish-at-close start and the outer level publishes the wrong span -- a LOST MATCH, measured 11/2"
SAB_DOC_FIGURE="MEASURED (design 5.3b axis P): W as first written gives 11 agree / 2 DISAGREE -- ^(a(?1)?b)\\1\$ on \"aabbaabb\" and \"aaabbbaaabbb\" answer NOMATCH where 10.46 answers (0,8) g1=(0,4) and (0,12) g1=(0,6). W plus the pending slot is 13/0."
SAB_COUNT=1
SAB_BEFORE='                if (vm_marked(v, g)) {
                    int ps = vm_slot_pend(v, g);
                    if (ps >= 0 && ps < nstate) w[ps] = true;
                }'
SAB_AFTER='                /* SABOTAGE S149: the PENDING family leaves W */'
