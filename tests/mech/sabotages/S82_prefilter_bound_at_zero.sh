# S82 — [M6.2 WAVE D] D63's CANDIDATE-START PREFILTER BOUNDED AT 0 INSTEAD OF
# AT `startpos`.
#
# THIS IS A LOST MATCH, NOT A SLOW PATTERN, and it is the one place where
# `\G`'s start-state family and wave C's scan avoidance actually meet.
#
# ENG_ATTEMPT's candidate-start prefilter (D63, wave C) skips whole attempts
# whose seeded start state would be dead. Its candidate set is derived by
# `cand_from_live_seeds` from `Dfa.s1u[]` — the states an attempt at
# `start > startpos` enters. Wave D adds a SECOND family, `Dfa.s1g[]`, for the
# one attempt where `start == startpos`, and the derivation never looked at
# it. So wave C's `start > 0` bound is exactly one attempt too wide the moment
# both mechanisms are live in one pattern:
#
#     (?m)^a|\Gb   on "xb" at startpos 1
#         libpcre2:            (1, 2)
#         shipped pcrec:       (1, 2)
#         with `start > 0`:    NO MATCH
#
# because the candidate set is the newline definition (only the `(?m)^a`
# branch's seed is live in `s1u[]`), `s[startpos - 1]` is `x`, and the memchr
# advance jumps the attempt at `startpos` — the only attempt where the `\Gb`
# branch could ever have run.
#
# THE FIX IS A STRENGTHENING RATHER THAN A SECOND CONDITION, which is why the
# sabotage is a one-token revert: `start > startpos` implies `start > 0`, so
# the shipped guard is the wave-C guard with a tighter lower bound, and every
# position the skip then passes over is one the derivation's domain covers.
#
# WHY THE `\G`-ONLY POPULATION CANNOT SEE IT, and this is the row's real
# content: a FULLY-`\G` pattern emits no prefilter at all (`attempt_cand`'s
# own anchored early-out fires, since every `s1u[]` is dead), and a `(?m)`-only
# pattern has no `s1g[]` to enter. The defect lives exactly in the
# INTERSECTION, which is a population neither wave's corpus had until this one
# added it. tests/assertions/gpos.rxt section 5 carries the cell, and
# run_gstart_diff.sh's `partial` class sweeps it.
SAB_ID="S82-prefilter-bound-at-zero"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness gstartdiff"
SAB_HARNESS_TARGET="tests/assertions/gpos.rxt"
SAB_DESC="D63's ENG_ATTEMPT prefilter is bounded at 'start > 0' (wave C's value) instead of 'start > startpos', so a pattern with BOTH a (?m)^ branch and a \\G branch skips the one attempt the \\G branch needs ('(?m)^a|\\Gb' on \"xb\" at startpos 1 loses its match)"
SAB_DOC_FIGURE="tests/assertions/gpos.rxt section 5's (?m)^a|\\Gb block goes red, and run_gstart_diff.sh's §2 sweep diverges from libpcre2"
SAB_COUNT=1
SAB_BEFORE='                  gseed ? "startpos" : "0",'
SAB_AFTER='                  "0",   /* SABOTAGE S82 */'
