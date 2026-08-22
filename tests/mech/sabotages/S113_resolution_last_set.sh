# S113 (design row S-BR10) — §8.3's RESOLUTION TAKES THE LAST SET MEMBER.
#
# THE SECOND of the four candidate rules, and the one that "walk the run and
# keep the last one you saw set" produces naturally.
#
# THE CELL THAT KILLS IT, and it is exactly one:
# `(?J)^(?<a>x)(?<a>y)\k<a>$` matches "xyx" and NOT "xyy". BOTH members are
# set there, so every rule that picks *a* set member agrees on which cells
# COMPILE and disagrees only on which text the reference compares. Under this
# sabotage "xyy" matches and "xyx" does not — the exact inversion.
#
# IT IS ALSO WHAT THE REFLECTION TABLE WOULD ENCODE without §8.2's number
# tiebreak (sabotage S118): the caller algorithm in `docs/spec/match_api.md`
# §6 walks BACK to the run's first row and FORWARD to the first participating
# one, so a table emitted in descending number selects the highest-numbered
# participant. Two independent routes to the same wrong rule, which is why
# both have rows.
SAB_ID="S113-resolution-last-set"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="dupnamesdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/dupnames.rxt"
SAB_DESC="The emitted chain over a duplicated name's run drops its `else`, so every set member overwrites the previous one and resolution becomes \"LAST set\" instead of \"first set\". (?J)^(?<a>x)(?<a>y)\\k<a>\$ then matches \"xyy\" and not \"xyx\" -- the exact inversion of the measured answer"
SAB_DOC_FIGURE="PREDICTED: dupnamesdiff RED; the corpus RED on exactly the \"xyx\"/\"xyy\" cell of dupnames.rxt. Canonical figure owed from run_sabotage_matrix.sh S113."
SAB_COUNT=1
SAB_BEFORE='                i ? "else " : "", ns, ns, ne,'
SAB_AFTER='                "", ns, ns, ne,   /* SABOTAGE S113: no else, last wins */'
