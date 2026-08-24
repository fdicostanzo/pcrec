# S167 ([DD-14] wave D, design §4.2/§9.3 S-SR15) -- `\g<0>` / `\g'0'` MUST
# RESOLVE TO THE ROOT, ANCHORS INCLUDED, NOT "GROUP 0 DOES NOT EXIST".
#
# THE CELL THIS ROW DEFENDS, MEASURED (design §2.4): `^(a\g<0>?b)$` on
# "aabb" is NOMATCH -- `\g<0>` re-runs the WHOLE PATTERN, `^`/`$` included, so
# the inner `^` fails at offset 1 -- while the UNANCHORED form
# `(a\g<0>?b)` on "aabb" is (0,4), because with the anchors gone the call
# reaches depth 2. Both cells are carried in `whole.rxt` and `leadingzero.rxt`
# and BOTH are needed: an anchored-only assertion cannot tell "resolves to the
# root" from "refuses to resolve at all", since a construct that has stopped
# compiling ALSO answers nomatch on the anchored cell (a `perr` block, not a
# silent miscompile) and only the unanchored MATCH exposes the difference.
#
# THE MECHANISM. `pcrec_call_node` (src/parse/mod_recursion.c, wave D) is what
# `pcrec_brport_g`'s `<`/`'` arms (src/parse/mod_backrefs.c) call to turn a
# parsed `\g` body into an `A_CALL`: an ABSOLUTE zero (no sign, no name) is
# the ROOT and gets `target = 0` directly with NO `PendingRef` queued; every
# other value queues one and lets the end-of-parse resolver settle it against
# `1 <= n <= ncap`. Read `bool root = false;` for the line below and `\g<0>`
# stops being special-cased: `number == 0` reaches the ORDINARY resolver path
# (`mod_backrefs.c`'s `pcrec_bref_resolve`, the `PEND_CALL` numeric rule),
# which answers exactly what a reference to non-existent group 0 answers --
# "refers to capture group 0, but this pattern has N" -- and `(a\g<0>?b)`
# REFUSES TO COMPILE instead of matching "aabb". Design §9.3's own row names
# this exact wrong reading and its alternative ("a resolver that targets the
# group-1 body passes") -- this sabotage is the first of the two, the one a
# reader most naturally reaches for by analogy with `A_BREF`'s "0 is always
# out of range" rule, which is precisely the analogy `subroutines_design.md`
# §4.1(b) exists to refuse.
#
# WHAT IS NOT TOUCHED: `(?R)`/`(?0)`/`(?00)` resolve to the root through
# `pcrec_rcport_num`'s OWN, SEPARATE `rc_node(cx, rw, at, true, 0, ...)` call
# (mod_recursion.c) -- this sabotage's one-line edit is inside
# `pcrec_call_node` alone, so the `(?` doorway's zero family is UNAFFECTED and
# only the `\g` doorway's is broken. That is deliberate: it is what makes this
# the sharpest single-line expression of "the two doorways must agree about
# what zero means" (design §4.2's "NOT A NEW PORT" ruling) rather than a
# broader break that would also fire `leadingzero.rxt`'s `(?01)`/`(?00)` cells
# and muddy which doorway the row is really about.
SAB_ID="S167-g-zero-not-root"
SAB_FILE="src/parse/mod_recursion.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="pcrec_call_node's root computation is forced false, so an absolute \\g<0>/\\g'0'/\\g<00>/\\g'00' queues an ordinary PendingRef with number 0 instead of resolving to the AST root, and the resolver's plain 1<=n<=ncap check then refuses it as a nonexistent group"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR15, from 2.4's MEASURED anchored/unanchored pair): ^(a\\g<0>?b)\$ on \"aabb\" stays nomatch either way (a refusal and a correct root resolution both answer nomatch anchored), but (a\\g<0>?b) UNANCHORED on \"aabb\" goes from (0,4) to a compile REFUSAL naming capture group 0 -- the cell that separates \"resolved to the root\" from \"failed to resolve at all\". Needs features recursion. whole.rxt and leadingzero.rxt both carry the unanchored/anchored pair for all four zero spellings (\\g<0>, \\g'0', \\g<00>, \\g'00')."
SAB_COUNT=1
SAB_BEFORE='    bool root = !is_relative && !name && number == 0;'
SAB_AFTER='    bool root = false;   /* SABOTAGE S167 */'
