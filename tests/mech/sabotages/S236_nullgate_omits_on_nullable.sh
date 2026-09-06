# S236 — [K50-NULLGATE] THE GATE IS OMITTED ON A NULLABLE PATTERN, i.e. the
# narrowing over-firing.
#
# [K50-NULLGATE] builds the boundary gate iff `pcrec_startgate_needed` — the
# pattern can match EMPTY — because a match that CONSUMES a byte already begins
# on a byte the backend's `start_cls` admits. The predicate's SAFE direction is
# over-reporting nullable (an unnecessary gate costs throughput); the UNSAFE
# direction is the one this row plants: a predicate that says "not needed" for
# a pattern that can accept without consuming re-opens K50 for exactly the
# family K50's own witness belongs to.
#
# WHY IT IS ITS OWN ROW AND NOT A SECOND HUNK OF S234. S234 deletes the gate
# for EVERY pattern; this one deletes it only where the predicate is consulted,
# which is the [K50-NULLGATE] mechanism specifically. They also fail through
# DIFFERENT detectors: S234 is caught by answers (the startbnd differential and
# the corpus cells), while this one is caught FIRST by the compiler itself.
#
# WHAT SEES IT, and the ordering is the point. `cstart_check_omission`
# (src/ir/nfa.c) walks the epsilon+assertion closure of the pattern's own start
# at the omission site and refuses when an N_ACCEPT is reachable without
# consuming — so a nullable pattern does not MISCOMPILE under this sabotage, it
# fails to compile at all, with the internal error naming the disagreement
# between the AST-level predicate and the machine. That is the invariant doing
# its job: two independent derivations (`pcrec_minw` over `Ast`, the closure
# walk over `NState`) meeting at the site that would otherwise commit the
# defect. The answer-level detectors behind it stay armed for the case where
# the invariant is ALSO removed.
#
# MEASURED at the landing, with the predicate forced to `false`: `\B`, `a*` and
# `(?:a||b)` are each REFUSED under `-e utf8` with
# "[K50-NULLGATE] omitted the character-boundary gate on a pattern that can
# ACCEPT without consuming", while `b|c` compiles unchanged — the invariant
# discriminates on exactly the property the predicate is about, rather than
# firing on everything.
SAB_ID="S236-nullgate-omits-on-nullable"
SAB_FILE="src/core/internal.h"
SAB_SUITES="startbnd harness"
SAB_HARNESS_TARGET="tests/utf8/axis11_startpos_boundary.rxt"
SAB_DESC="pcrec_startgate_needed always answers 'the gate is not needed', so [K50-NULLGATE] omits the character-boundary gate on NULLABLE patterns too — the narrowing's unsafe direction, which re-opens K50 for the family its own witness belongs to"
SAB_DOC_FIGURE="docs/dev/known_issues.md K50; docs/dev/lanes/k50bnd_report.md 10.2 and 10.6"
SAB_COUNT=1
# REACH: can the compiler still build a machine for a nullable pattern under an
# encoding that restricts start positions at all? If `\B` stops compiling under
# -e utf8, or the utf8 backend stops restricting, this row's site is no longer
# reachable and it must score UNREACHED rather than go on certifying.
SAB_REACH='"$PCREC" -p rx -e utf8 --features assertions -o - -- "\\B" | grep -o "STARTPOS_GUARD" | head -1'
SAB_REACH_EXPECT='STARTPOS_GUARD'
SAB_BEFORE='    return cx->job->fit.lang_nullable;'
SAB_AFTER='    (void)cx; return false;   /* SABOTAGE S236 */'
