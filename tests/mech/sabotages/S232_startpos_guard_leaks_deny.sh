# S232 — [K50] THE CALLER-STARTPOS GUARD IGNORES ITS OWN DENY FLAG.
#
# `-fno-startpos-guard` is the one axis in `docs/spec/tuning.md` that is NOT
# answer-identity-preserving: it selects between two RULED semantics for a
# mid-character caller `startpos` (refuse with `PCREC_ERR_STARTPOS`, or answer
# the automaton's own answer, `utf8_design.md` 2.6.1.1). Drop the flag test
# and the permissive arm stops existing — the deny build refuses exactly where
# the default build does, and 2.6.1.1's oracle-validated cells are gone rather
# than moved.
#
# THE FAILURE IS SILENT IN THE DIRECTION THAT MATTERS. The DEFAULT arm is
# still correct, so every corpus cell, every identity gate and the whole
# `harness` suite stay green; what is lost is a semantics the design ruled and
# a caller can ask for. An axis whose deny arm quietly stopped working would
# read as "no divergence" to any check that only compares the default build
# against an oracle.
#
# WHAT SEES IT: `tests/utf8/run_startbnd_diff.sh`'s per-pattern TEXT check,
# which reads the deny artifact for a `return PCREC_ERR_STARTPOS;` BEFORE
# anything is run. That ordering is deliberate and is why the row is caught at
# all 10 witnesses rather than at some: the driver's own LEAKED-INTO-THE-DENY-
# ARM bucket can only see a leak that FIRES, and a guard emitted with a
# tautological condition would slip past it.
SAB_ID="S232-startpos-guard-leaks-deny"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="startbnd"
SAB_DESC="the emitted caller-startpos guard stops reading PCREC_NO_STARTPOS_GUARD, so -fno-startpos-guard emits the guard anyway and the ruled permissive semantics (utf8_design.md 2.6.1.1) has no build that carries it"
SAB_DOC_FIGURE="docs/spec/tuning.md 2.23; docs/spec/match_api.md 3.1's -fno-startpos-guard bullet; lib/pcrec.h's PCREC_NO_STARTPOS_GUARD comment"
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx -e utf8 --features lookaround -o - -- "(?<!.)" | grep -o "return PCREC_ERR_STARTPOS;" | head -1'
SAB_REACH_EXPECT='return PCREC_ERR_STARTPOS;'
SAB_BEFORE='    if (cx->opt->flags & PCREC_NO_STARTPOS_GUARD) return buf;'
SAB_AFTER='    /* SABOTAGE S232: the deny flag is not read. */'
