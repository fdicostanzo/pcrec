# S173 — [DD-14 wave G] THE SPLICE LEAVES THROUGH THE CALLER'S CONTINUATION.
#
# S-SR18's TWIN, for the linkage S-SR18 does not cover. Design §6.3 rules that
# wave G "may share the BODY but NEVER the EXIT", and §3.5 is why it is a RULE
# and not an optimisation: a call reaches the GROUP, not the group's LEXICAL
# OCCURRENCE, so the callee must leave through ITS OWN exit — MEASURED on
# 10.46, `^ab(?<=(ab))(?1)$` matches "abab", `^(?!(z|zy))x(?1)c$` matches
# "xzyc" and `^(?>(a|ab))z(?1)c$` matches "azabc", and an emitter that let the
# callee fall out through the occurrence's continuation gets all three wrong.
#
# THE SPLICE HAS ITS OWN VERSION OF THE SAME MISTAKE, and it is the one a
# reader will propose as an obvious saving: emit the inlined body straight to
# the CALL SITE'S continuation and skip the exit label. That is not merely a
# lost label — the exit is where §3.1's RESTORE lives, so skipping it makes the
# splice CAPTURE-OPAQUE where the measurement says a call is CAPTURE-TRANSPARENT
# ("the capture state after the call is exactly the state before it, whatever
# the call did", `out/captures.txt` C2, read off the LIVE ovector through a
# `pcre2_set_callout` callback).
#
# THE DETECTOR MUST BE A `g` LINE, and this is the row where that is not a
# style note: the sabotaged matcher answers the same SPAN on almost every cell,
# because a leaked capture changes what group 1 reports and not where the match
# is. `captures.rxt`'s cells are the population, and design §5.3's own prototype
# was refuted at exactly this shape — "a wrong span on a correct match, which no
# `m`/`n` expectation catches and only a `g` line does".
SAB_ID="S173-splice-shares-exit"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/captures.rxt"
SAB_DESC="vm_splice emits the inlined callee body straight to the CALL SITE's continuation instead of to its own exit label, so the |W| trailed restores that follow the exit are never reached. The splice becomes capture-OPAQUE where design 3.1 MEASURED a call to be capture-TRANSPARENT: the callee's writes to the shared capture pairs survive the return."
SAB_DOC_FIGURE="PREDICTED: captures.rxt goes RED on its group-span lines while most of its m/n spans stay right -- a leaked capture moves what group 1 reports, not where the match is. run_recursion_diff.sh's SS3 sweep (span AND every group span, 1632 cells) and its SS5 A == B section both go red, and SS5's failure names the SPLICE arm specifically, since the LINKAGE arm still restores. Canonical figure owed from run_sabotage_matrix.sh S173."
SAB_COUNT=1
SAB_BEFORE='    vm_emit(v, body_lbl, a->u.call.body, done_lbl);'
SAB_AFTER='    vm_emit(v, body_lbl, a->u.call.body, next);   /* SABOTAGE S173 */'
