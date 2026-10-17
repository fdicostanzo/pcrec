#!/bin/bash
# grid2/paranoid.sh -- D166 add. 1.1: the counter-unavailable SUGGESTION. Sourced by slot.sh,
# time2.sh and f2perf2.sh. When user-space counters are not available to this user, each
# script prints, to its log and to its pass's status file, the current
# kernel.perf_event_paranoid (`?` if unreadable), that 2 or lower enables the optional pass,
# what the pass adds, and the two commands; and the skip reaches the provenance
# (`counters skipped:perf_event_paranoid=N` appended to $OUT/provenance.txt).
# THESE SCRIPTS NEVER RUN sysctl OR sudo AND NEVER WRITE UNDER /etc: the commands below are
# TEXT for a person. paranoid_check.sh holds that claim (every line carrying the text is
# marked  #SUGGEST-TEXT  and must be an echo/printf; any other sysctl/sudo/etc mention fails).
#
#   perf_probe            returns 0 when `perf stat` counts cycles:u here; else sets PERF_WHY
#   paranoid_report LOG STATUS    (LOG is the caller's stdout) prints the suggestion to stdout (the caller's log), appends
#                                 it to STATUS, appends the provenance line; idempotent
#   PROVENANCE=FILE       overrides $OUT/provenance.txt (the check's scratch copy)
#   PERF_FORCE_FAIL=1     forces perf_probe to fail (the check's lever; never set in a slot)
paranoid_level() { cat /proc/sys/kernel/perf_event_paranoid 2>/dev/null || echo '?'; }

perf_probe() {
  PERF_WHY=""
  if [ -n "${PERF_FORCE_FAIL:-}" ]; then PERF_WHY="forced to fail (PERF_FORCE_FAIL)"; return 1; fi
  command -v perf > /dev/null || { PERF_WHY="no perf binary on PATH"; return 1; }
  local out
  out=$(perf stat -x, -e cycles:u,instructions:u,branch-misses:u -- true 2>&1) || { PERF_WHY="perf stat denied: $(grep -m1 -iE 'access to|denied|permission' <<<"$out" | cut -c1-100)"; return 1; }
  grep -q 'not supported\|not counted' <<<"$out" && { PERF_WHY="events not counted"; return 1; }
  return 0
}

paranoid_report() {
  local status=${2:-/dev/null} lvl; lvl=$(paranoid_level)
  { echo "counters unavailable: ${PERF_WHY:-unknown}"                                                                         #SUGGEST-TEXT
    echo "kernel.perf_event_paranoid=$lvl"                                                                                    #SUGGEST-TEXT
    echo "SUGGESTION: kernel.perf_event_paranoid of 2 or lower enables the OPTIONAL branch-miss pass (items 6-7 of the slot)"  #SUGGEST-TEXT
    echo "  (user-space cycles, instructions, branches, branch-misses). It adds branch misses per KiB and the predictability"   #SUGGEST-TEXT
    echo "  diagnosis: the ungated corroboration column of the consumer-bound label. Nothing downstream needs it."              #SUGGEST-TEXT
    echo "  one-off:     sudo sysctl kernel.perf_event_paranoid=2"                                                               #SUGGEST-TEXT
    echo "  persistent:  /etc/sysctl.d/99-perf.conf  containing  kernel.perf_event_paranoid = 2"                                #SUGGEST-TEXT
    echo "  (this script never runs sysctl or sudo and never writes under /etc)"                                                #SUGGEST-TEXT
  } | tee -a "$status"
  local prov=${PROVENANCE:-${OUT:+$OUT/provenance.txt}}
  if [ -n "$prov" ] && ! grep -q '^counters skipped:' "$prov" 2>/dev/null; then
    echo "counters skipped:perf_event_paranoid=$lvl" >> "$prov"
  fi
}
