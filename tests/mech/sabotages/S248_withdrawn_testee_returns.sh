# S248 — [DD-13b.W23.5] R-B's own detector, aimed at itself: a WITHDRAWN
# production RETURNING.
#
# `src/parse/rxt_schema.def` gains a `PCREC_RXT_SCHEMA(CONFIG, "testee",
# ...)` row — reviving the `config`-body `testee` roster directive D99
# withdrew (item N-42). This is the exact shape the withdrawal-absence
# check's three-arm landing bar (`w23_impl.md` §4.3) exists to catch:
# a withdrawn keyword becoming an ACTIVE production again, spelled
# EXACTLY as the check's own parser arm looks for it (a quoted token in
# the schema table).
#
# MEASURED (this row's own construction, `tests/rxtsource/
# run_rxtsource_tests.sh`'s withdrawal-absence checks): under the plant
# the PARSER ARM alone goes red —
#   "withdrawal-absence, parser arm: 1 hit(s) —
#    src/parse/rxt_schema.def:167: PCREC_RXT_SCHEMA(CONFIG, \"testee\", ...)"
# — while the DATA ARM stays green (no `.rxt`/`.rxtin` file in the tree
# WRITES `testee` at a config-body first-token position, plant or no
# plant — the row existing is not the same as anyone using it) and the
# SELF-CHECK stays green (it exercises the aux-subtree narrowing on two
# scratch files that never touch `rxt_schema.def` at all). Three
# independent arms see three independent things, which is the point of
# building three rather than one.
SAB_ID="S248-withdrawn-testee-returns"
SAB_FILE="src/parse/rxt_schema.def"
SAB_SUITES="rxtsource"
SAB_DESC="a config-body 'testee' schema row returns after D99 withdrew it — the PARSER ARM of the withdrawal-absence check (w23_impl.md §4.3 arm b) goes red naming the row; the data arm and the aux-subtree self-check are unaffected"
SAB_DOC_FIGURE="docs/dev/decisions.md D99 (item 2, N-42); docs/design/dd13_format/w23_impl.md §4.3"
SAB_COUNT=1
# REACH: the row rests on `testee` being ABSENT from the CONFIG scope on
# the clean tree — `--list-schema` must show no `config testee` row —
# and on the fixed 5-token PARSER ARM grep in
# tests/rxtsource/run_rxtsource_tests.sh reaching src/parse/rxt_schema.def
# unconditionally (it always runs, not gated on any corpus population).
SAB_REACH='"$PCREC" --list-schema | awk -F"\t" "\$1 == \"config\" && \$2 == \"testee\" { n++ } END { print n+0 }"'
SAB_REACH_EXPECT='0'
SAB_BEFORE='PCREC_RXT_SCHEMA(CONFIG, "analysis", LIST,  0, NONE, REPEAT,      "", FORMAT, PCREC, 23)'
SAB_AFTER='PCREC_RXT_SCHEMA(CONFIG, "analysis", LIST,  0, NONE, REPEAT,      "", FORMAT, PCREC, 23)
/* SABOTAGE S248: a withdrawn production returns. */
PCREC_RXT_SCHEMA(CONFIG, "testee",   TOKEN, 0, NONE, AT_MOST_ONE, "", FORMAT, PCREC, 1)'
