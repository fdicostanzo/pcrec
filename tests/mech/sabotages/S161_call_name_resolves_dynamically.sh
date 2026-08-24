# S161 ([DD-14] wave B+C, design SS9.3 S-SR14) -- A CALL BY NAME TO A
# DUPLICATED NAME TAKES THE FIRST DECLARATION, STATICALLY.
#
# THE CELL THAT SEPARATES TWO CONSTRUCTS SHARING ONE NAME, MEASURED on 10.46
# under `PCRE2_DUPNAMES`. The rows that decide it make the FIRST declaration
# UNSET, which the naive rows cannot:
#
#     ^(?:(?<a>x)|q)(?<a>y)(?&a)$   a CALL       "qyx" (0,3)   "qyy" nomatch
#     ^(?:(?<a>x)|q)(?<a>y)\k<a>$   a REFERENCE  "qyx" nomatch "qyy" (0,3)
#
# **A call by name runs the FIRST DECLARATION's PATTERN, statically, whether or
# not that group is set. A backreference by name reads the first SET member of
# the run, dynamically.** Two different resolutions of one name, in one pass.
#
# AND A CALL DOES NOT RETRY INTO THE LATER MEMBERS:
# `^(?<a>x)(q)(?<a>y)(?&a)z$` matches "xqyxz" and NOT "xqyyz".
#
# THE RULE IS UNIFORM ACROSS ALL FOUR BY-NAME SPELLINGS, which the design's
# first version measured for `(?&name)` alone: `(?&a)`, `(?P>a)`, `\g<a>` and
# `\g'a'` all match "qyx" and all refuse "qyy". So the resolver applies ONE
# rule at ONE site and there is no per-spelling arm to get wrong -- which is
# what makes this a single-line sabotage.
#
# THE DESIGN CONSEQUENCE IS WHY `A_CALL` DOES NOT REUSE `A_BREF`'s `refs[]`.
# That field is a SET "even when it has one element, deliberately", because a
# by-name REFERENCE resolves at MATCH time over a run. A call resolves at PARSE
# time to ONE NUMBER. Reusing the field would make one field mean two things
# and would invite an emitter to write the else-if chain the other construct
# needs.
#
# THE SABOTAGE IS ONE COMPARISON OPERATOR, which is the smallest edit that
# expresses "resolve like `A_BREF`": the run is walked and the LAST member
# wins instead of the first. The declaration order is the group NUMBER order
# (PCRE2 numbers by opening paren), so `<` and `>` are exactly first and last.
SAB_ID="S161-call-name-dynamic"
SAB_FILE="src/parse/mod_backrefs.c"
SAB_SUITES="harness recursion registry"
SAB_HARNESS_TARGET="tests/recursion/dupnames.rxt"
SAB_DESC="the resolver's PEND_CALL name rule takes the LAST declaration of a duplicated name instead of the FIRST, so a call by name runs a different group's pattern than 10.46 does"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR14, from 3.4(c)'s MEASURED discriminator): ^(?J)(?:(?<a>x)|q)(?<a>y)(?&a)\$ on \"qyx\" goes from (0,3) to nomatch, and on \"qyy\" from nomatch to (0,3) -- i.e. it starts answering like the BACKREFERENCE, which is the construct 3.4(c) exists to separate it from. The cell needs features recursion,named-groups,modifiers,backrefs (the (?J) letter is module backrefs')."
SAB_COUNT=1
SAB_BEFORE='                    if (first == 0 || gp->number < first) first = gp->number;'
SAB_AFTER='                    if (first == 0 || gp->number > first) first = gp->number;   /* SABOTAGE S161 */'
