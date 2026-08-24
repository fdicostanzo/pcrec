# S121 ([M6.6.2] wave 0, D70) — THE REVERSAL COPY CONSTRUCTOR WRITES A PER-KIND
# FIELD WITHOUT CHECKING THE KIND.
#
# THE HAZARD D70's TAGGED UNION CREATED, and the reason the union's own comment
# calls itself "not a checking mechanism". `rd_node` is the copy constructor for
# EVERY kind `rd_reverse` handles — A_CLASS, A_EMPTY, the six position
# predicates, A_CAP, A_REP, A_CAT, A_ALT, plus that function's tail fallthrough
# — and it clears two A_REP-only fields on the copy. Before the union those
# writes were simply DEAD for every other kind. After it they are writes
# THROUGH `u.rep` onto whatever payload the node actually owns.
#
# THE ARITHMETIC, measured at the wave: the union sits at offset +40 and
# `u.cls.bits` spans +40..+71, so
#     u.rep.possessive @ +49      -> class bitmap BYTE 9      -> 0x48-0x4F (H-O)
#     u.rep.revbody    @ +56..+63 -> class bitmap BYTES 16-23 -> 0x80-0xBF
# On a reversed A_CLASS node the clear therefore ZEROES the body's membership
# for those ranges. The emitted backward walk's class tests become an ALL-ZERO
# `rx_class_bitmap[32]`, can never be taken, and the LAST ITERATION'S CAPTURES
# — the thing `Ast.u.rep.revbody` exists to recover — come back UNSET.
#
# WHY IT NEEDS ITS OWN CORPUS FILE, and this is the row's real lesson. THE
# WHOLE-MATCH SPAN IS UNCHANGED in every case; only capture slots move. And
# when this guard was written, all 44 corpus patterns that took the
# reverse-deterministic rung were spelled in LOWERCASE ASCII — not one had a
# bit in either clobbered range — so the wave's own four-axis byte-identity
# gate reported ZERO differences with the guard removed. The corpus could not
# express the bug. `tests/rungselect/revdet_highbytes.rxt` was written to close
# exactly that, which is why this row targets it: its `g` lines are the
# detector, and an `m`-only corpus would score this sabotage UNDETECTED while
# looking like coverage.
#
# THE GENERAL RULE this row guards, stated at the union in src/core/internal.h:
# a writer may touch `u.<payload>` only under a kind check that owns it, and a
# generic copy or sanitise helper MUST guard rather than write unconditionally.
SAB_ID="S121-revdet-node-unguarded"
SAB_FILE="src/opt/revdet.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/rungselect/revdet_highbytes.rxt"
SAB_DESC="rd_node's clear of the A_REP-only revbody/possessive loses its kind guard, so the reversal copy constructor writes through u.rep on every kind it copies. On a reversed A_CLASS node that zeroes u.cls.bits bytes 9 and 16-23 (H-O and 0x80-0xBF), the backward walk's class tests become an all-zero bitmap, and the last iteration's captures come back UNSET with the match span unchanged"
SAB_DOC_FIGURE="PREDICTED: corpus RED on tests/rungselect/revdet_highbytes.rxt — 61 of its 127 cases fail under the unguarded build, 0 under the guarded one (measured by hand at the wave). Canonical figure owed from run_sabotage_matrix.sh S121."
SAB_COUNT=1
SAB_BEFORE='    if (n->k == A_REP) {
        n->u.rep.revbody = NULL;
        n->u.rep.possessive = false;
    }
    return n;'
SAB_AFTER='    /* SABOTAGE S121: the guard removed — a naive D70 port */
    n->u.rep.revbody = NULL;
    n->u.rep.possessive = false;
    return n;'
