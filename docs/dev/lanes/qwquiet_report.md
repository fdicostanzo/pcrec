# qwquiet report

Premise confirmed: scripts/queuewatch and scripts/watchrun tree_cpu summed /proc stat fields 13+14 (utime+stime) of LIVE
processes only, so a job whose work runs in short-lived forked children (mech) showed no movement.

Fix: both tree_cpu awk sums now add fields 15+16 (cutime+cstime, reaped children, which accumulate into each living
ancestor). CPU only, no file-growth signal: a hung job (sleep, blocked read, no children) still reads quiet; a job writing
only to its own build/tmp is covered by the CPU of the writers. No state-format change (signature is the same field list).

Tests (scripts/tests/queuewatch.test): busy fork-loop with silent log stays NOT quiet; silent sleeper goes QUIET once;
PLANT of the old live-only sum turns the busy case red. Green: queuewatch 21/21, queuewatch_ci 5/5, watchrun 21/21,
monitor_preflight 7/7. Note the plant case is probabilistic by design (a sample may catch a live child); it passed twice.

STATE AT HANDOFF: committed on lane/qwquiet, not merged. Rulings file empty (no entries applied).
