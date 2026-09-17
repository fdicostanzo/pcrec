# S252 — [K59-PREMUL] THE PREMULTIPLIED-TABLE DROP RUNG NEVER FIRES.
#
# `compile_driver`'s retry loop drops the premultiplied DFA transition table
# and re-emits when an emitted-size cap has refused a DFA-engine artifact
# that still carries one — the drop ladder's SECOND rung
# (`docs/spec/limits.md` §8, "The optional-contributor drop";
# `docs/dev/known_issues.md` K59, FIXED). Make its eligibility test
# constantly false and the rung stops existing: `--tune=min-size` alone
# (or a caller's own explicit `-fno-premul-table`) is once again the ONLY
# way to reach K59's own witness, and every other dial position — and every
# other DFA-engine artifact this rung alone could rescue — goes back to
# REFUSING.
#
# THE FAILURE IS A REFUSAL, WHICH SOUNDS LOUD AND IS NOT (S237's own
# reasoning, one rung over). The population is entirely outside the default
# axes most checks sweep at (K59's witness needs `-e utf8 --features
# unicode-props`), and it is small enough that a refusal at those specific
# axes reads as ordinary rather than alarming. Nothing that compares
# ANSWERS can see it: a pattern that does not compile has no answers to
# disagree about.
#
# WHAT SEES IT: `tests/codegen/run_tune_dial.sh` §6, which drives K59's own
# filed witness through all five `--tune` positions and requires every one
# to COMPILE — with the ladder's own drop-rung STAMPS (`RX_ENGINE_SEL
# "size-cap-retry"`, `RX_DFA_TABLE` off `"premultiplied"`) asserted at the
# four positions whose rescue depends on this rung.
SAB_ID="S252-premul-drop-rung-deleted"
SAB_FILE="src/core/compile.c"
SAB_SUITES="tunedial"
SAB_DESC="compile_driver's premultiplied-table drop rung (K59's own fix) is never eligible, so an emitted-size cap refuses a DFA-engine artifact that fits once the premultiplied transition table is dropped -- the K59 defect restored at every --tune position but the caller's own explicit -2/-fno-premul-table"
SAB_DOC_FIGURE="docs/spec/limits.md 8's 'The optional-contributor drop'; docs/dev/known_issues.md K59; tests/codegen/run_tune_dial.sh section 6"
SAB_COUNT=1
# REACH: does the K59 witness still compile at a position where ONLY this
# rung rescues it (balanced -- the artifact that is refused at balanced
# before either rung, and rescued by BOTH rungs together after)? Read as
# the RX_ENGINE_SEL stamp the rung is a co-writer of.
SAB_REACH='"$PCREC" --features unicode-props -e utf8 -p rx -o - -- "[^\p{C}\p{M}\p{P}]" | grep -o "size-cap-retry" | head -1'
SAB_REACH_EXPECT='size-cap-retry'
SAB_BEFORE='            const bool premul_eligible =
                cx.size_cap_refused &&
                size_drop_rung < SDR_NO_PREMUL &&
                cx.job && cx.job->fit.chosen == ENGM_DFA &&
                !(defo.flags & PCREC_NO_PREMUL_TABLE);'
SAB_AFTER='            const bool premul_eligible =
                false;   /* SABOTAGE S252: the rung is never offered. */'
