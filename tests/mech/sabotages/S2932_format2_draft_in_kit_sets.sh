#!/usr/bin/env bash
# S2932 -- span_pick stage 2 unit S2c, sabotage (o) (docs/design/memfn/span_cards.md §3.8, §9's S2c row;
# lane memfn-s2c). A FORMAT-2 DRAFT SET PLACED IN memfn/data/sets/.
#
# Plant: synthetic-all-walk.tsv's header becomes a format-2 draft's: `format 2` and its values_digest
# the format-2 one (5c77acf469930b8b, tests/knowledge/ks_ref.py digest of the edited file), rows unchanged
# (their noise `-`).
# Detector: tests/memfn/finder_check.py check C (arm memfnfinder): its own format-1 digest (pcrec-meas-1,
# written from measures.md §3.3) of the file mismatches the header (generate.py --check also refuses the
# edited generated file). span_cards §9 NOTES: a draft with a `null` row may be red earlier, by a
# ValueError at int(r["value_e6"]): red, not by the stated reason.
SAB_ID="S2932-format2-draft-in-kit-sets"
SAB_FILE="memfn/data/sets/synthetic-all-walk.tsv"
SAB_SUITES="memfnfinder"
SAB_DESC='a format-2 draft set placed in memfn/data/sets/, which holds format-1 sets only'
SAB_DOC_FIGURE='MEASURED by lane memfn-s2c (sub-lane fh) planted and reverted by hand; exact re-run: bash tests/mech/run_sabotage_matrix.sh S2932.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='format	1
id	synthetic-all-walk
rev	1
class	x86_64-avx2/zen4
isa	x86-64-v3 avx2 sse4.2 popcnt bmi2
tier	synthetic
composite	0
members	
unit_key	kit.beta.WALK.DFA_SCAN.r1e0c0
method	kit-synthetic@2
run	-
box	-
compiler	-
code_commit	-
counters	skipped:not-taken
partial	0
rows	83
values_digest	b3ea024ae0fe2fbb'
SAB_AFTER='format	2
id	synthetic-all-walk
rev	1
class	x86_64-avx2/zen4
isa	x86-64-v3 avx2 sse4.2 popcnt bmi2
tier	synthetic
composite	0
members	
unit_key	kit.beta.WALK.DFA_SCAN.r1e0c0
method	kit-synthetic@2
run	-
box	-
compiler	-
code_commit	-
counters	skipped:not-taken
partial	0
rows	83
values_digest	5c77acf469930b8b'
