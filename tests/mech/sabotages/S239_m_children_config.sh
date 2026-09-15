# S239 — [DD-13b.W23.2] S-R1: `m`'s SCHEMA ROW STOPS DECLARING
# `children: none`, AND ONLY THE THREE-LEG DIFFERENTIAL SEES IT MOVE.
#
# `src/parse/rxt_schema.def`'s block `m` row is flipped from `children:
# none` to `children: config` — a real, existing scope with real rows
# (`pcrec`, `flags`, `features`, `encoding`, `engine`, `budget`,
# `analysis`). This is deliberately NOT a nonsense value: the point is
# that leg A's WALK still works end to end, it just answers a DIFFERENT
# QUESTION about an indented line under `m` than legs B and C do.
#
# MEASURED (this row's own construction, `tests/rxtsource/fixtures/
# indent_under_m.rxtin`): leg A now answers
# `[unknown-token-in-scope] ...: 'n' is not a config-block directive`
# (the indented `n "b"` line is dispatched into CONFIG scope, where `n`
# has no row) where the clean tree answers
# `[structure-attachment] ...: indented line continues nothing ('m'
# takes no continuation)`. Legs B and C are unaware of the schema and
# keep answering structure-attachment — their own fixed attachment logic
# never consults `rxt_schema.def`'s `children` column at all (by design,
# format_design.md §2.25.5: "the schema table is leg A's, deliberately").
#
# So NEITHER a single-leg read of leg A (still refuses) NOR a
# verdict-only three-leg compare (all three still refuse) sees this row
# move at all — the class CHANGED, the exit code did not. W23-S2's own
# class-comparison rewrite of `check_refusal_all3`
# (`tests/rxtsource/run_rxtsource_tests.sh`) is the one instrument built
# to see it: `indent-under-m`'s check asserts class structure-attachment
# on ALL THREE legs independently, and under this plant leg A's own
# needle match (`[structure-attachment]`, folded into `check_refusal`'s
# needle list by `check_refusal_all3`) fails first.
SAB_ID="S239-m-children-config"
SAB_FILE="src/parse/rxt_schema.def"
SAB_SUITES="rxtsource"
SAB_DESC="the block 'm' schema row's children column moves from none to config, so leg A answers a different diagnostic CLASS for an indented line under 'm' than legs B and C do — invisible to a verdict-only differential"
SAB_DOC_FIGURE="docs/design/dd13_format/format_design.md §2.25.5 (the schema table is leg A's, deliberately); w23_impl.md §3.1 W23-S2"
SAB_COUNT=1
# REACH: the row rests on `m` still being a real BLOCK-scope kind with
# `children: none` on the clean tree, and on `indent_under_m.rxtin`
# reaching that exact site.
SAB_REACH='"$PCREC" --list-schema | awk -F"\t" "\$1 == \"block\" && \$2 == \"m\" { print \$5 }"'
SAB_REACH_EXPECT='none'
SAB_BEFORE='PCREC_RXT_SCHEMA(BLOCK, "m",              CASE,  0, NONE,  REPEAT,      "", FORMAT, NONE,        1)'
SAB_AFTER='/* SABOTAGE S239: children moves from none to config. */
PCREC_RXT_SCHEMA(BLOCK, "m",              CASE,  0, CONFIG,  REPEAT,      "", FORMAT, NONE,        1)'
