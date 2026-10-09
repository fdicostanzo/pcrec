#!/bin/bash
# [OPT-REVEND] the whole twin record, in order: the identity sweep, the two
# sabotage controls (each MUST show twin_diff > 0), the timing block, then
# form B's identity sweep and timing.
#   PCREC=build/pcrec ./run_all.sh   -> results/{check,control_*,timing}.txt
set -u
HERE=$(cd "$(dirname "$0")" && pwd); R=$HERE/results; mkdir -p "$R"
"$HERE/run_check.sh" > "$R/check.txt" 2>&1; echo "== check rc=$?" >> "$R/check.txt"
for c in noeol firstseed; do
    TWIN_SABOTAGE=$c PATTERNS=$HERE/controls.tsv "$HERE/run_check.sh" > "$R/control_$c.txt" 2>&1
    echo "== control $c rc=$? (rc=1 expected: the control must fail)" >> "$R/control_$c.txt"
done
{ echo "# $(date -Is) $(uname -n) gcc $(gcc -dumpfullversion) cpu: $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2)"
  echo "# governor: $(cat /sys/devices/system/cpu/cpu7/cpufreq/scaling_governor 2>/dev/null)"
  for rep in 1 2 3; do echo "## repeat $rep"; "$HERE/run_timing.sh" 7; done; } > "$R/timing.txt" 2>&1
TWIN_FORM=lower "$HERE/run_check.sh" > "$R/check_lower.txt" 2>&1; echo "== check (form B) rc=$?" >> "$R/check_lower.txt"
{ for rep in 1 2 3; do echo "## repeat $rep (form B)"; TWIN_FORM=lower "$HERE/run_timing.sh" 7; done; } > "$R/timing_lower.txt" 2>&1
echo "== run_all COMPLETE $(date -Is)" >> "$R/timing.txt"
