# S164 ([DD-14] wave B+C, design SS4.4c, SS9.3 S-SR19) -- THE SLOT LAYOUT
# COUNTS EVERY EMITTED REGION, INCLUDING ONE DEFINED INSIDE `X{0}`.
#
# **THE SITE WHOSE FIRST ANSWER WAS WRONG**, and design SS4.4a is emphatic about
# it: site (6) said LEXICAL ONLY, and the consequence is an OUT-OF-BOUNDS SLOT
# WRITE -- K27's class, in a matcher someone else compiles. `vm_count_slots`'
# own header names the failure: "a lift this pre-pass cannot see runs
# `vm_slot_mark(v, v->nmark++)` past `RX_NSLOTS`."
#
# THREE FACTS MAKE A LEXICAL COUNT WRONG, and the first is the one no reasoning
# from the tree finds:
#
#   1. `X{0}` EMITS NOTHING AND COUNTS NOTHING -- `vm_count_slots` returns at
#      its `rmin == 0 && rmax == 0` guard -- AND A CALLEE CAN LIVE THERE. That
#      is the classic pre-DEFINE idiom, MEASURED matching on 10.46 for plain,
#      recursive, atomic and rung-bearing callees. MEASURED in-pcrec:
#      `^((?>a)){1}b$` allocates 2 cut marks and `^((?>a)){0}b$` allocates NONE.
#   2. THE CALLEE REGION IS EMITTED SEPARATELY from the lexical occurrence
#      (SS6.3), so it needs its OWN instances. "Double-counting" is the CORRECT
#      count here, not a bug to avoid.
#   3. `u.call.save` LISTS SLOT INDICES, and the two regions' indices DIFFER. A
#      restore written against the wrong indices is SS5.3b's axis-C miscompile
#      arriving by a second route.
#
# THE CELL MUST CARRY A RUNG-BEARING OR ATOMIC CALLEE and SS4.4c says so: a
# callee with only CAPTURE slots allocates from a family `{0}` does NOT prune,
# so a plain `{0}` cell goes GREEN on a broken layout.
# `^(?:((?>a|ab))){0}(?1)z$` is the shape and `zerodef.rxt` is written on it,
# with the plain row kept beside it as the control a naive fix would pass
# vacuously.
#
# `asan` IS ASSIGNED AS WELL AS `harness`, because the two see different
# things: under ASan the failure is a REPORT naming the write, and without it
# the write lands in whatever follows `slot_values` and the corpus sees
# silent corruption -- which may or may not change an answer on the subjects
# anyone chose.
SAB_ID="S164-region-slots-uncounted"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
# [DD-14 wave B+C] EXPECTED UNDETECTED, and the expectation is CHECKED.
# The sabotage is real and verified applied; this corpus cannot see it
# yet. SAB_DOC_FIGURE above records the measurement and names exactly
# what would have to exist for this row to close. If the matrix ever
# reports NOW DETECTED here, some wave built that witness: re-measure,
# then flip this to DETECTED -- do not delete the row.
SAB_EXPECT=DETECTED
SAB_HARNESS_TARGET="tests/recursion/slotfamilies.rxt"
SAB_DESC="vm_count_slots is not run per emitted callee region, so a callee's own slot instances are never counted and the emitter assigns past RX_NSLOTS -- an OUT-OF-BOUNDS WRITE in emitted code, K27's class"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR19): an OUT-OF-BOUNDS SLOT WRITE, K27's class, which vm_count_slots' own header names ('a lift this pre-pass cannot see runs vm_slot_mark(v, v->nmark++) past RX_NSLOTS'). THE CELL MUST CARRY A RUNG-BEARING OR ATOMIC CALLEE UNDER {0} -- ^(?:((?>a|ab))){0}(?1)z\$ -- because a callee with only CAPTURE slots allocates from a family {0} does not prune and the row goes green. zerodef.rxt is written on exactly that requirement. Under ASan the failure is a REPORT; without it, silent corruption, which is why the asan suite is assigned as well. || MEASURED UNDETECTED: corpus 0fail/23pass on zerodef.rxt, recdiff 0fail/7pass. The sabotage does NOT produce an out-of-bounds write on this population, it produces a SLOT COLLISION: with the region's cut mark uncounted, \`vm_slot_mark(v, 0)\` and \`vm_slot_pend(v, 1)\` both resolve to slot 4 on ^(?:((?>a|ab))){0}(?1)z\\$ (RX_NSLOTS 6 -> 5), so a resume depth and a publish-at-close position share a cell -- and the two cells this file carries do not read the collided values on a path that changes their answer. The \`asan\` suite the design assigns DOES NOT EXIST as a mech arm, so the memory-safety half was never scored here either. THE SHIPPED LAYOUT IS CORRECT (RX_NSLOTS 6, the region counted); what is owed is a cell whose collided slots are both live on one path. || [DD-14 wave G, 2026-08-24] RE-MEASURED AND FLIPPED TO DETECTED on a CYCLIC callee: see the transcript in this file's header. The 'MEASURED UNDETECTED' paragraph above is the record of the OLD target (an acyclic callee, which wave G splices, so no region is emitted and the sabotage is a no-op there) and is kept as the reason the cell had to move."
SAB_COUNT=1
# [DD-14 wave G, 2026-08-24] RE-ANCHORED ON THE TWO LINES THAT DO THE WORK,
# because the loop around them gained a `rgn_emit[i]` guard and a comment. The
# smaller anchor is also the better one: it names the region COUNT and nothing
# about the loop that drives it.
#
# **AND WAVE G MOVED THIS ROW'S POPULATION OUT FROM UNDER IT — SO THE CELL WAS
# RE-POINTED AT A CYCLIC CALLEE AND THE ROW FLIPPED TO DETECTED (manager
# ruling, 2026-08-24).** The old target `zerodef.rxt` argues from
# `^(?:((?>a|ab))){0}(?1)z$`, which names an ACYCLIC callee: §6.3 now SPLICES
# it, no region is emitted, `rgn_emit[i]` is false and the sabotage is a NO-OP
# on that pattern rather than the undetected slot COLLISION the paragraph below
# measured. **A row whose population has moved out from under it measures
# nothing, and expected-UNDETECTED is the reading that hides that.**
#
# THE FIX IS A CELL WHOSE CALLEE IS IN A CYCLE, because in-a-cycle is exactly
# what forces the LINKAGE, and the linkage is exactly what emits a REGION for
# this pass to count. `tests/recursion/slotfamilies.rxt` carries one:
# `^(?:(?<g>(?=a)a(?&g)?b)){0}(?&g)$` — `g` calls itself, so a region is
# emitted, and the region's body carries a LOOKAROUND, whose two slot families
# are per EMITTED COPY and therefore exist only in the region's own count.
#
# **THE TRANSCRIPT OF THE FLIP** (sabotage applied to a `git archive HEAD` tree,
# both compilers run on the same pattern):
#
#     shipped     RX_NSLOTS 7   with RX_SLOT_LOOK_MARK0 = 5, RX_SLOT_LOOK_POS0 = 6
#     sabotaged   RX_NSLOTS 5   both LOOK slots GONE, and the two `RX_SET`s that
#                               wrote them gone with them
#     tests/recursion/slotfamilies.rxt  45 passed / 2 FAILED
#     the named cell: `^(?:(?<g>(?=a)a(?&g)?b)){0}(?&g)$` on "aaabbb"
#                     expected `match 0 6`, got `nomatch`  -- A LOST MATCH
#     the OLD target, same sabotage:    zerodef.rxt 33 passed / 0 failed
#
# The last line is the pair that names the failure: the row is green on the
# population it used to have and red on the one it should have had all along.
# The SPLICE side of the same claim is S177, which is detected separately.
SAB_BEFORE='            if (v.rgn_emit[i])
                vm_count_slots(&v, pcrec_callgraph_body(v.cg, i), 1, false);'
SAB_AFTER='            /* SABOTAGE S164: the region'"'"'s own slots are never counted */'
