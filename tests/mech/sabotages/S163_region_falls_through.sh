# S163 ([DD-14] wave B+C, design SS3.5/SS5.4/SS6.3, SS9.3 S-SR18) -- THE CALLEE
# REGION HAS ITS OWN EXIT.
#
# THE CONSTRUCT FAMILY THE DESIGN DID NOT HAVE, and the sharpest finding of
# R34's C1 round: **a call reaches the GROUP, not the group's LEXICAL
# OCCURRENCE**, and the obvious emitter miscompiles every cell of it. MEASURED
# on 10.46, each row with a wrapper-isolating control:
#
#   W1  ^ab(?<=(ab))(?1)$        "abab" (0,4)  the callee must leave through
#                                             ITS OWN exit, not the lookbehind's
#                                             end-check-cut-and-restore
#   W2  ^(?!(z|zy))x(?1)c$       "xzyc" (0,4)  it must RETRY inside a region
#                                             whose lexical home is CUT on the
#                                             assertion's own success
#   W3  ^(?>(a|ab))z(?1)c$       "azabc" (0,5) it must GIVE BACK `a` and take
#                                             `ab`, though its lexical home is
#                                             ATOMIC
#   Z0  ^(?:(?<g>a|ab)){0}(?&g)c$ "abc" (0,3)  ...and there is no lexical
#                                             emission to fall out of at all
#
# IT IS AN EXIT ROW AND NOT AN ENTRY ROW, which R34's V-6 corrected in the
# design itself. An earlier version said a jump into the group's body would
# inherit the lookbehind's BACK-STEP; that is INVERTED. `lookaround_design.md`
# puts the wrapper's machinery at `L_entry` and in `L_b_i` (BEFORE `L_body_i`),
# so a jump to the GROUP's own entry label -- which lives INSIDE the branch
# body -- lands AFTER the back-step. The entry is fine. **The EXIT is where it
# breaks**, and that is both sharper and more general: falling out of the body
# reaches the assertion's end-check against a saved position that is
# meaningless for a call, then its cut and position restore.
#
# SO SS6.3's SPLIT IS A RULE AND NOT AN OPTIMISATION. SS6.1's collapse argument
# says the exit needs a per-ACTIVATION answer, and the only per-activation
# channel is the call record -- so a shared body cannot leave through the
# lexical occurrence's continuation, whatever wrapper that continuation has.
# **Wave G may share the BODY; it may never share the EXIT.**
SAB_ID="S163-region-falls-through"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/inlookaround.rxt"
SAB_DESC="the callee region is emitted into the LEXICAL occurrence's continuation instead of its own exit, so a call to a group whose lexical home is a lookbehind, a negative lookahead or an atomic group inherits that wrapper's end-check, verdict or cut"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR18): ^(?>(a|ab))z(?1)c\$ on \"azabc\" goes from (0,5) to nomatch -- the atomic exit's RX_CUT discards the choice points the retry needs. The row carries ALL THREE WRAPPERS (W1's lookbehind end-check-and-restore, W2's negative-assertion cut, W3's atomic cut) because they are three different exits and an emitter can get one right and the others wrong. It is an EXIT row, NOT an entry row -- R34 V-6 found the design's first version sabotaging the back-step, which a call never reaches."
SAB_COUNT=1
SAB_BEFORE='    vm_emit_fd(v, v->rgn_lbl[i], body, v->rgn_exit[i], 0, NULL);
    vm_lbl(v, v->rgn_exit[i],'
SAB_AFTER='    /* SABOTAGE S163: the region leaves through the lexical continuation */
    vm_emit_fd(v, v->rgn_lbl[i], body, v->nlabel - 1, 0, NULL);
    vm_lbl(v, v->rgn_exit[i],'
