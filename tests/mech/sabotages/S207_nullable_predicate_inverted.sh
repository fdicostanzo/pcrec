# S207 (S-OPT41-2) — [OPT-4.1] THE NULLABILITY PREDICATE INVERTED: THE RESCUE
# IS REFUSED ON EVERY PATTERN IT WAS BUILT FOR, AND KEPT ON EVERY PATTERN IT
# WAS BUILT TO AVOID.
#
# WHY THE PAIR EXISTS. S206 removes the predicate; this one turns it round.
# They are not two spellings of one plant, because the two failures have
# OPPOSITE costs and only one instrument sees each. S206 is a SLOWDOWN with
# every answer right (the bench's 1.2-9.9x); this is a LOST OPTIMISATION with
# every answer right — the [OPT-4] rescue that pcrec-bench measured at 2.2-4.6x
# on five of its ten labelled points, and at x4.60 on `level-context`, simply
# stops happening. A check written for one direction alone passes the other,
# which is this directory's founding lesson stated one predicate over.
#
# WHAT IT BREAKS. `pcrec_minw(root) == 0` becomes `!= 0`, so a pattern is
# called nullable exactly when it is not. `\b(?:ERROR|FATAL|CRIT)\b...` — the
# [SEL-1] witness, minimum width 12 — is declared nullable and its rescue is
# declined, so the artifact falls back to the pre-[OPT-4] `overflowed-dfa` VM
# with no prefilter at all; `(a|b){1,30000}` loses the size rung's collapsed
# prefilter; and every genuinely nullable pattern KEEPS the useless one.
#
# **THE CORPUS CANNOT SEE EITHER HALF**, for the reason S206's header states
# in full: the prefilter is a FILTER (match_api.md §6.3 H1/H2/H3), so its
# presence, its absence and its language are all answer-identical. The corpus
# arm below is EXPECTED to read `0fail`.
#
# **WHAT SEES IT, AND WHY THE NON-NULLABLE TWIN IS THE ROW THAT MATTERS.**
# `pfcollapse` §6 is the detector this plant is written against: the `sel1`
# witness must still stamp `RX_VM_PREFILTER "hybrid"` / `"count-collapsed"`
# and `RX_ENGINE_SEL "collapsed-prefilter"`, and under the inversion it reads
# `"none"` / `declined-nullable`. §2's five `count-collapsed` witnesses fail
# beside it on the force axis, and `resource`'s NON-nullable size-rung cell
# (`(a|b){1,30000}`, one character from its nullable twin) fails on the size
# rung. §6b and the nullable resource cell go red too — an inversion is loud
# in both directions — but they are S206's detectors, not this row's, and a
# reader must not take their redness as evidence that the twin was checked.
SAB_ID="S207-nullable-predicate-inverted"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="pfcollapse resource harness"
SAB_HARNESS_TARGET="tests/base/bounded_repeats.rxt"
SAB_DESC="[OPT-4.1]'s nullability predicate is inverted, so the count-collapsed rescue is DECLINED on exactly the patterns pcrec-bench measured it winning 2.2-4.6x on and KEPT on the three it measured it losing 1.2-9.9x on. Answer-identical everywhere: the prefilter is a filter, so neither its loss nor its uselessness moves a single cell of the corpus"
SAB_DOC_FIGURE="PENDING PHASE 2 (lane opt41 coded this row under an execution hold; the canonical run belongs beside the [OPT-4.1] merge). EXPECTED: pfcollapse red on §6's sel1 rows, §2's six count-collapsed witnesses and §7b's collapsed-prefilter witness (plus §6b and the exact-nullable rows, which are S206's detectors reddening incidentally); resource red on BOTH size-rung cells; corpus 0fail/N pass."
SAB_REACH='"$PCREC" --features all -p rx -o - -- "\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b"'
SAB_REACH_EXPECT="collapsed-prefilter
count-collapsed"
SAB_REACH_POP="tests/codegen/run_prefilter_collapse.sh|^lang_witness count-collapsed|6
tests/codegen/run_prefilter_collapse.sh|\[sel1\]|8
tests/resource/run_resource_tests.sh|^size_rung_cell |2"
SAB_COUNT=1
SAB_BEFORE='        fit.prefilter_lang_nullable = pcrec_minw(root) == 0;'
SAB_AFTER='        fit.prefilter_lang_nullable = pcrec_minw(root) != 0;   /* SABOTAGE S207 */'
