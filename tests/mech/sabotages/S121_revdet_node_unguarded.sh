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
# THE ARITHMETIC AS IT WAS AT [M6.6.2], and it describes a layout that no
# longer exists — read the [M5.0] block below for the current one. The union
# sat at offset +40 and `u.cls.bits` spanned +40..+71, so
#     u.rep.possessive @ +49      -> class bitmap BYTE 9      -> 0x48-0x4F (H-O)
#     u.rep.revbody    @ +56..+63 -> class bitmap BYTES 16-23 -> 0x80-0xBF
# On a reversed A_CLASS node the clear therefore ZEROED the body's membership
# for those ranges. The emitted backward walk's class tests became an ALL-ZERO
# `rx_class_bitmap[32]`, could never be taken, and the LAST ITERATION'S
# CAPTURES — the thing `Ast.u.rep.revbody` exists to recover — came back UNSET.
#
# ============================================================================
# [M5.0 STAGE 1] THIS ROW IS NOW **UNREACHED**, AND THAT IS THE HONEST VERDICT
# ============================================================================
#
# The interval-payload refactor shrank `u.cls` from 32 bytes to 16
# (`{const PcrecCpRange *iv; int n;}`), and the clobber went LATENT rather
# than away. Re-derived with `offsetof` on the built tree:
#
#     u.cls now spans +40..+55   (iv +40..+47, n +48..+51, 4 bytes padding)
#     u.rep.possessive @ +49  ->  BYTE 1 OF `n`
#     u.rep.revbody    @ +56..+63 -> OUTSIDE `u.cls` ENTIRELY
#
# `rd_node` CLEARS — it writes zeros — and under `--encoding=byte` a class
# holds at most 128 disjoint non-adjacent intervals, so `n <= 128 < 256` and
# byte 1 of `n` is ALREADY ZERO on every artifact this backend can produce.
# The unguarded write is a no-op.
#
# MEASURED at [M5.0] stage 1, with the guard removed: **all 2,845 distinct
# corpus patterns compile BYTE-IDENTICALLY**, and this row's own detector file
# — written specifically to express this clobber, because an all-lowercase
# corpus could not — reports **7/7 identical**. There is nothing left for the
# harness target to see.
#
# **SO THE ROW DECLARES ITS REACH RATHER THAN SCORING GREEN OVER A NO-OP.**
# That is [MECH-REACH]'s whole purpose and the S70/S155 failure it was built
# to retire: a row that goes on scoring while certifying nothing is worse than
# an absent one, because it reads like coverage. Manager ruling R2
# (docs/dev/lanes/utf8s1_rulings.md), 2026-09-04.
#
# **THE GUARD STAYS AND THE ROW STAYS**, because both go LIVE again at stage 3.
# `\p{L}` is ~770 intervals, so `n > 255` becomes ordinary the moment module
# `unicode-props` lands — and then clearing byte 1 of `n` turns `n = 256` into
# `n = 0`, the EMPTY class, which is a LOST MATCH rather than a corrupted one.
# The guard is correct for a reason that is about `k` and never about offsets,
# which is exactly why it survived a re-layout that erased its symptom.
#
# THE TWO REACH DECLARATIONS BELOW ARE THE TWO THINGS THAT MUST BOTH BE TRUE
# for this row to detect anything again, and they are declared separately
# because they can arrive separately:
#   (1) the COMPILER must be able to build a class with `n >= 256` at all,
#       i.e. `\p{...}` must compile — stage 3's landing;
#   (2) this row's own DETECTOR FILE must contain such a pattern on the
#       reverse-deterministic rung, or the harness target will still see
#       nothing even once (1) holds.
# Whoever lands stage 3 owes (2) in the same change, and the `NOW REACHED`
# direction of `SAB_EXPECT` is what will say so.
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
SAB_DOC_FIGURE="HISTORICAL (pre-[M5.0]): corpus RED on tests/rungselect/revdet_highbytes.rxt — 61 of its 127 cases fail under the unguarded build, 0 under the guarded one (measured by hand at the [M6.6.2] wave). THAT FIGURE NO LONGER REPRODUCES: at [M5.0] stage 1 the unguarded build is byte-identical on all 7 of that file's patterns and on all 2,845 corpus patterns, which is why this row now declares UNREACHED. A new canonical figure is owed from run_sabotage_matrix.sh S121 at stage 3, once the reach declarations above start holding."
# (1) CAN THE COMPILER PRODUCE THE POPULATION AT ALL? `\p{L}` is the smallest
# construct whose class carries more than 255 intervals. Today it refuses with
# "requires module 'unicode-props'", so the emitted pattern comment never
# appears and this probe FAILS — which is the UNREACHED verdict, correctly.
# The day stage 3 lands it compiles, this matches, and the row wakes up.
SAB_REACH='"$PCREC" --features all -p rx -o - -- "\p{L}"'
SAB_REACH_EXPECT="/* Generated by pcrec. Pattern: \p{L} */"
# (2) DOES THIS ROW'S OWN DETECTOR CARRY SUCH A PATTERN? The harness target is
# what would go red, so a live compiler with no `\p` pattern in this file
# still detects nothing. Keyed on the file rather than on the corpus at large,
# because a `\p` pattern elsewhere does not put one on the revdet rung here.
SAB_REACH_POP='tests/rungselect/revdet_highbytes.rxt|^pattern .*\\p\{|1'
# EXPECTED UNREACHED, with the reason, so the matrix reports the row as
# honestly dormant rather than as a failure — and so the runner's own reverse
# check (`NOW REACHED`) fires the day either declaration above starts holding.
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON="[M5.0 stage 1] the 16-byte u.cls put u.rep.possessive over byte 1 of the interval COUNT, which is provably zero under --encoding=byte (n <= 128), so the unguarded clear is a no-op: 2,845/2,845 corpus patterns and 7/7 of this row's own detector file compile byte-identically with the guard removed. The guard is still correct and goes LIVE at stage 3, where \p{L}'s ~770 intervals make n > 255 ordinary and a cleared byte turns n=256 into the EMPTY class (a lost match). Re-derivation: src/core/CLAUDE.md, [M5.0 stage 1] section; ruling R2."
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
