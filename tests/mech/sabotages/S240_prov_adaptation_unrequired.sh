# S240 — [DD-13b.W23.3] S-R2: `provenance`'s `adaptation` STOPS BEING
# REQUIRED when the record's fidelity is not `verbatim`.
#
# `src/parse/rxt_schema.def`'s PROVENANCE `adaptation` row loses its
# `required-if fidelity != verbatim` clause. Nothing else moves: the row
# still exists, still takes a prose value, still holds its cardinality,
# and every other provenance rule is untouched. What is gone is the one
# DECLARED conditional in the table — format_design §2.14 rule 3, the
# conditional Frank's ruling names by example.
#
# WHY THE PLANT IS AN ERASURE AND NOT A FLIP. A wrong CONDITION (say
# `fidelity == verbatim`) would refuse the verbatim record too, and then
# BOTH halves of the fixture pair go red — which proves something broke
# and not that this rule is the thing checking. Deleting the clause
# leaves the accept half green and turns exactly one cell red, which is
# the discriminating shape.
#
# THE ROW IS RE-HOMED TO THIS REPO AND THAT IS ITS OWN DECISION (r57
# S-M3). The bench's acceptance checks C5/C6 test this same rule in
# pcrec-bench, so a row whose only detector lived there would score
# UNDETECTED in `make mech` and be RIGHT to — a row's detector must live
# in THIS repo's matrix. `tests/rxtsource/fixtures/prov_adapted_no_
# adaptation.rxtin` and its accept control are the pcrec-side pair that
# makes the rule checkable here.
#
# LEG A ONLY, by the schema's own column: every `provenance` row reads
# `validated_by: pcrec`, and legs B and C CONSUME a provenance body
# without reading it. That is why this row's suite is `rxtsource` and
# not the corpus — there is no three-leg assertion for it to break.
SAB_ID="S240-prov-adaptation-unrequired"
SAB_FILE="src/parse/rxt_schema.def"
SAB_SUITES="rxtsource"
SAB_DESC="the provenance 'adaptation' row loses its required-if clause, so a record declaring fidelity 'adapted' with no adaptation text is accepted — the one declared conditional in the schema, deleted"
SAB_DOC_FIGURE="docs/design/dd13_format/format_design.md §2.14 rule 3, §2.25.3 (required-if); w23_impl.md §3.5 S-R2"
SAB_COUNT=1
# REACH: the row rests on `adaptation` still carrying a `required-if`
# clause on the clean tree. If a later wave moves the rule into parser
# code the clause disappears and this plant becomes a no-op — which the
# runner must report as UNREACHED rather than as DETECTED-by-luck.
SAB_REACH='"$PCREC" --list-schema | awk -F"\t" "\$1 == \"provenance\" && \$2 == \"adaptation\" { print \$7 }"'
SAB_REACH_EXPECT='required-if fidelity != verbatim'
SAB_BEFORE='PCREC_RXT_SCHEMA(PROVENANCE, "adaptation",   PROSE, 0, PROSE, AT_MOST_ONE, "required-if fidelity != verbatim",                      FORMAT, PCREC, 23)'
SAB_AFTER='/* SABOTAGE S240: the required-if clause is deleted. */
PCREC_RXT_SCHEMA(PROVENANCE, "adaptation",   PROSE, 0, PROSE, AT_MOST_ONE, "",                      FORMAT, PCREC, 23)'
