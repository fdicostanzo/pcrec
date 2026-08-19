# S77 — [M6.2 wave C] D62's CONTROL 2, and it is PERMANENT: the flag's reader
# turned off.
#
# D62 rules that multiline-`$` is a parse-resolved FIELD on the `A_EOL` node
# rather than a distinct node kind, and it accepts a named residual for that
# choice: a new node KIND cannot be silently ignored (mrl.c:18-24's
# exhaustive-switch rule makes it a build failure at 15 of 19 sites), while a
# new FIELD warns nowhere. Three controls replace the compile alarm, and this
# row is the second of them — "a PERMANENT sabotage row flipping the flag's
# reader off — must go red".
#
# THE READER is `first_of`'s `A_EOL` arm in src/opt/possessify.c. With
# `a->multiline` consulted, a multiline `$` in a quantifier's FOLLOW widens
# FOLLOW to all bytes and the quantifier is NOT possessified. With the read
# turned off, every `$` takes the transparent arm — which is precisely the
# shipped pre-cure behaviour, and precisely the miscompile: the retreat into
# the quantifier is the only route to the match, and possessification removes
# it.
#
# WHAT GOES RED, and it is a LOST MATCH rather than a wrong span:
# `(?m)[^c]{1,3}$` on "a\nc" is (0,1) and becomes NO MATCH AT ALL. That cell
# is §8.7's recommended guard for exactly this reason — it cannot pass by
# accident on an off-by-one — and the scoped spellings `(?m:[^c]{1,3}$)` and
# `(?m)[^c]{1,3}$(?-m)` go red beside it, which the pre-cure code got wrong
# for a SECOND reason (a verdict-time read of the parser's end-of-pattern
# state) that the field spelling closes by construction.
#
# NOTE WHAT STAYS GREEN: every non-multiline cell in tests/assertions/gate.rxt.
# The exemption is correct there and must keep firing; a sabotage that turned
# both directions red would be describing a switch, not a gate.
SAB_ID="S77-first-of-ignores-multiline"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness assertions"
SAB_HARNESS_TARGET="tests/assertions/multiline.rxt"
SAB_DESC="possessify's first_of stops reading Ast.multiline, so a multiline \$ in a quantifier's follow is treated as transparent and the quantifier is possessified — D62's accepted residual made live: '(?m)[^c]{1,3}\$' on \"a\\nc\" loses its match entirely, in the scoped spellings too"
SAB_DOC_FIGURE="tests/assertions/multiline.rxt: the D47.5 gate cells (section 4) and the scoped cells (section 5) go red; tests/assertions/gate.rxt's non-multiline cells stay green"
SAB_COUNT=1
SAB_BEFORE='        if (a->multiline) {'
SAB_AFTER='        if (0) {   /* SABOTAGE S77 */'
