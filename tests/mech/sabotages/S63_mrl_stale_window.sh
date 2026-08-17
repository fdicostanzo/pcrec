# S63 — [M4.6d] THE PREFILTER WINDOW LEFT STALE ACROSS THE start++ RETRY.
#
# D51 ruling 2 (b), removed. The MRL ceiling on the search entry is
# `min(n, win[0][1])` — the prefilter's match-END window — and the window is
# per-ATTEMPT. `rx_search`'s retry loop advances `start` without it; the
# emitter therefore recomputes the window there, which is the ruling's second
# branch and the one this build took.
#
# THE DIRECTION OF ERROR IS THE DANGEROUS ONE, which is the whole reason the
# ruling made this a hard gate rather than a note. The prefilter's forward scan
# terminates on a dead transition, so `win[0][1]` is the last accepting END
# BEFORE that break: on a subject holding a second, later match the carried
# window is too SMALL. A too-small ceiling makes `minrest` bind harder than it
# should and can cut a position an accepting continuation needed — matches
# deleted, not merely pruning forgone. Every other conservative choice in this
# design errs the safe way; this one does not.
#
# WHAT CATCHES IT IS A STRUCTURAL CHECK, NOT A SUBJECT SWEEP, and that is
# honest rather than a shortcut. A structural argument says the retry cannot
# fire at all on the prefilter path (the prefilter is the capture-erased
# machine, so a match it reported at `win[0][0]` is one the VM must find), and
# the critic who raised this could not make the loop fire in 99 trials —
# 0-firings-in-N is explicitly not a discharge, and it is also why no
# differential population reliably reaches the state. So
# `tests/mrl/run_mrl_tests.sh` asserts the RECOMPUTE EXISTS in the emitted C:
# two prefilter call sites, one of them at `start`. This row is what proves
# that assertion can go red.
SAB_ID="S63-mrl-stale-window"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="mrl"
SAB_DESC="the start++ retry stops recomputing the prefilter window, carrying an attempt's match-end ceiling into the next attempt: too SMALL, the direction that deletes real matches"
SAB_DOC_FIGURE="tests/mrl/run_mrl_tests.sh, ruling 2 (b); k23_design.md §9.1, §14.4"
SAB_COUNT=1
SAB_BEFORE='    if (v.nclamp > 0 && prefn)
        snprintf(retry_win, sizeof retry_win,'
SAB_AFTER='    if (0 && prefn)  /* SABOTAGE S63 */
        snprintf(retry_win, sizeof retry_win,'
