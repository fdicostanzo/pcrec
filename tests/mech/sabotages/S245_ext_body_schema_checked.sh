# S245 — [DD-13b.W23.3] S-R6: AN `ext` BODY BECOMES SCHEMA-CHECKED.
#
# Both `ext` rows (file scope and block scope) flip `children` from
# `tree` to a NAMED SCOPE — `provenance`, a real scope with real rows —
# so the OPEN SUBTREE (structure-layer parameter 3, r58 ruling R1) stops
# existing and every line of every aux body is dispatched against a
# vocabulary.
#
# THREE DETECTORS, AND THE THIRD ARRIVED FOR FREE AT REVISION 3.4.1.
#
#   1. `aux_arbitrary_keys.rxtin` — leg A REFUSES what it must accept.
#      This is aux being NARROWED: a consumer's own key space is not
#      pcrec's, and the production's entire promise is that pcrec parses
#      the structure and interprets nothing.
#   2. `aux_deep_tree.rxtin` — aux being INTERPRETED. Its body's keys are
#      deliberately real format keywords (`pattern`, `config`, `m`,
#      `provenance`, `variant`) three levels deep; under the plant they
#      are dispatched, and the graduation rule's failure mode becomes a
#      check rather than a sentence.
#   3. `aux_literal_pipe.rxtin` — the STRUCTURAL axis. Because `children`
#      IS parameter 3, the same flip RE-ARMS S2 and S3 inside the
#      subtree, so a trimmed bare `|` opens a prose region and swallows
#      its own siblings. A plant on a semantic column that also moves a
#      structural one is worth naming: it is why the parameter reads
#      `children` rather than taking a column of its own.
#
# The SUITE is `rxtsource` for all three; the corpus has no `ext` line
# and cannot acquire one, which is the honest reason this row's
# population lives entirely in fixtures.
SAB_ID="S245-ext-body-schema-checked"
SAB_FILE="src/parse/rxt_schema.def"
SAB_SUITES="rxtsource"
SAB_DESC="both 'ext' rows' children column moves from tree to a named scope, so an aux body is dispatched against a vocabulary instead of being parsed structurally and left uninterpreted — aux NARROWED at one fixture and INTERPRETED at another"
SAB_DOC_FIGURE="docs/design/dd13_format/format_design.md §2.27 (the AUX production), §1.2.1 parameter 3; w23_impl.md §3.5 S-R6"
SAB_COUNT=1
# REACH: the row rests on `ext` declaring `children: tree` at BOTH
# scopes on the clean tree. Two rows, one value — the query prints both,
# so a single flip is visible as a changed population rather than as a
# changed string.
SAB_REACH='"$PCREC" --list-schema | awk -F"\t" "\$2 == \"ext\" { print \$5 }" | sort -u'
SAB_REACH_EXPECT='tree'
SAB_BEFORE='PCREC_RXT_SCHEMA(FILE, "ext",         TOKEN, 0, TREE,       REPEAT,      "", FORMAT, PCREC,      23)'
SAB_AFTER='/* SABOTAGE S245 (1 of 2): the file-scope ext body becomes schema-checked. */
PCREC_RXT_SCHEMA(FILE, "ext",         TOKEN, 0, PROVENANCE, REPEAT,      "", FORMAT, PCREC,      23)'
SAB_FILE2="src/parse/rxt_schema.def"
SAB_BEFORE2='PCREC_RXT_SCHEMA(BLOCK, "ext",        TOKEN,     0, TREE,       REPEAT,      "",                     FORMAT, PCREC, 23)'
SAB_AFTER2='/* SABOTAGE S245 (2 of 2): the block-scope ext body too. */
PCREC_RXT_SCHEMA(BLOCK, "ext",        TOKEN,     0, PROVENANCE, REPEAT,      "",                     FORMAT, PCREC, 23)'
SAB_COUNT2=1
