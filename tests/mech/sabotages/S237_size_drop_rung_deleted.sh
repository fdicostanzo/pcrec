# S237 — [K53-SELRETRY] THE OPTIONAL-CONTRIBUTOR DROP RUNG NEVER FIRES.
#
# `compile_driver`'s retry loop drops the OPTIONAL anchored machine and
# re-emits when an emitted-size cap has refused an artifact carrying one
# (`docs/spec/limits.md` §8, "The optional-contributor drop"). Make its
# eligibility test constantly false and the rung stops existing: patterns that
# compile today go back to REFUSING, which is K53 restored.
#
# THE FAILURE IS A REFUSAL, WHICH SOUNDS LOUD AND IS NOT. The population is
# small, it is entirely outside the default axes most checks sweep at (the six
# `\p` names need `-e utf8` AND `--features unicode-props`; the eight corpus
# members are wide literal alternations from a `.rxtin` FIXTURE, not a `.rxt`
# corpus file), and a refusal is the state this tree spent four days regarding
# as normal for exactly these patterns. Nothing that compares ANSWERS can see
# it: a pattern that does not compile has no answers to disagree about.
#
# WHAT SEES IT: `tests/codegen/run_anchored_match.sh` §6a (the rung driven
# directly through a `-DPCREC_MAX_EMIT_BYTES=20000` reference compiler — three
# witnesses that must produce artifacts rather than diagnostics) and §5's
# size-drop FLOOR, which is the corpus-population half and is why that pin is
# a floor rather than the ceiling its overflow neighbour carries. The `utf8`
# corpus arm sees it too, as sixteen pattern-compile failures.
SAB_ID="S237-size-drop-rung-deleted"
SAB_FILE="src/core/compile.c"
SAB_SUITES="anchoredmatch"
SAB_DESC="compile_driver's optional-contributor drop rung is never eligible, so an emitted-size cap refuses artifacts that fit once the OPTIONAL anchored machine is dropped — the K53 defect restored (an optional machine deciding what pcrec accepts)"
SAB_DOC_FIGURE="docs/spec/limits.md 8's 'The optional-contributor drop'; docs/design/anchored_match_unwrapped.md 5.2a; docs/dev/known_issues.md K53"
SAB_COUNT=1
# REACH: does a pattern EXIST that this rung rescues? Read as the stamp the
# rung is the only writer of, on the row's own headline witness. If `\p{L}`
# under utf8 ever stops taking the rung — because a class-emission change made
# it fit unaided ([CLS-TREE]), or because the caps moved — this row is
# certifying nothing and says so rather than scoring.
SAB_REACH='"$PCREC" --features unicode-props -e utf8 -p rx -o - -- "\p{L}" | grep -o "size-cap-retry" | head -1'
SAB_REACH_EXPECT='size-cap-retry'
SAB_BEFORE='                cx.size_cap_refused &&
                size_drop_rung < SDR_MAX &&
                cx.job && cx.job->anchored_ok;'
SAB_AFTER='                false;   /* SABOTAGE S237: the rung is never offered. */'
