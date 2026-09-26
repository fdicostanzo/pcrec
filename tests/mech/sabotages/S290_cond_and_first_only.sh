# S290 — [FINDINGS] B0: a `required-if` condition's ` and ` CONJUNCTION is
# read as its FIRST conjunct only.
#
# `src/parse/rxt_source.c`'s `cond_holds` returns after evaluating the first
# `<field> <op> [value]` conjunct. The provenance rows B0 rewrote then read
# `required-if parent == data` (and `parent == block` for `url`/`ref`) —
# the pre-B0 rule — so an AUTHORED data block is again told it owes
# `bytes`/`sha256` it cannot have (findings design §0.10's defect,
# reinstated). The plant is the conjunction mechanism alone; every row
# and clause string is untouched.
#
# DETECTOR: tests/rxtsource's `[FINDINGS] B0` section — the accepting
# fixture `analysis_bundle_accept.rxtin`'s `plain` bundle carries an
# authored provenance with no `bytes`, so the accept assertion goes red.
SAB_ID="S290-cond-and-first-only"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="rxtsource"
SAB_DESC="the required-if/forbidden-if ' and ' conjunction evaluates only its first conjunct, so an authored data block is told it owes bytes/sha256 again (findings design 0.10 reinstated)"
SAB_DOC_FIGURE="docs/design/findings/design.md §0.10, §3.1 (PROVENANCE rows); docs/spec/rxt_format.md's constraints clause spellings"
SAB_COUNT=1
# REACH: the rows must still spell a conjunction on the clean tree, or the
# plant has nothing to truncate.
SAB_REACH='"$PCREC" --list-schema | awk -F"\t" "\$1 == \"provenance\" && \$2 == \"bytes\" { print \$7 }"'
SAB_REACH_EXPECT='required-if parent == data and source != authored'
SAB_BEFORE='        if (!cut) return 1;'
SAB_AFTER='        return 1;   /* SABOTAGE S290: later conjuncts ignored */'
