#!/bin/bash
# grid2/paranoid_check.sh -- the check for D166 add. 1.1's counter-unavailable SUGGESTION
# (r17b_prime.md §5.4: "the text appears when the probe is forced to fail; the skip reaches
# the provenance; no sysctl/sudo in the scripts"). Usage:  OUT=<a built slot dir> bash paranoid_check.sh
# It writes only under $OUT/tmp/paranoid_check/.
#   A  forced probe failure (PERF_FORCE_FAIL=1) through time.sh --paranoid, slot.sh
#      (PARANOID_ONLY=1) and f2perf.sh end to end: each prints the current
#      kernel.perf_event_paranoid, "2 or lower enables", what the pass adds, both commands;
#   B  the skip reaches the provenance: `counters skipped:perf_event_paranoid=N` in $OUT/provenance.txt;
#      f2perf.sh also writes F2_SKIPPED to its status file;
#   C  the positive control: the probe NOT forced prints no suggestion (when counters work here);
#   D  no script runs sysctl or sudo or writes under /etc: every non-comment line of every
#      grid2/*.sh is scanned; the suggestion's own text lines carry the marker  #SUGGEST-TEXT
#      and must be echo/printf lines;
#   E  failing direction: the scan is run on copies with a planted `sysctl -w`, a planted
#      `sudo`, a planted write under /etc, and a marker on a non-echo line: each must be caught.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:?set OUT to a built slot directory}
W=$OUT/tmp/paranoid_check; rm -rf "$W"; mkdir -p "$W"
export PROVENANCE=$W/provenance.txt PARANOID_STATUS=$W/paranoid.status   # the check never touches the slot's own provenance
fails=0; passes=0
ok()  { passes=$((passes + 1)); echo "ok   $*"; }
bad() { fails=$((fails + 1)); echo "FAIL $*"; }
need() {   # label file phrase...
  local lab=$1 f=$2; shift 2
  for p in "$@"; do grep -qF -- "$p" "$f" && ok "$lab: has '$p'" || bad "$lab: missing '$p' in $f"; done
}
PHRASES=("counters unavailable" "kernel.perf_event_paranoid=" "2 or lower enables" "branch-miss" "predictability" "one-off:" "persistent:")
CMD1="sudo sysctl kernel.perf_event_paranoid=2"; CMD2="/etc/sysctl.d/99-perf.conf"

# ---- A, B: forced failure
PERF_FORCE_FAIL=1 OUT=$OUT PHASE=F1 PASS_STATUS=$W/time.status bash "$HERE/time.sh" --paranoid > "$W/time.out" 2>&1
need "time.sh log" "$W/time.out" "${PHRASES[@]}" "$CMD1" "$CMD2"
need "time.sh status" "$W/time.status" "${PHRASES[@]}" "$CMD1" "$CMD2"
PERF_FORCE_FAIL=1 PARANOID_ONLY=1 bash "$HERE/slot.sh" "$OUT" > "$W/slot.out" 2>&1
need "slot.sh log" "$W/slot.out" "${PHRASES[@]}" "$CMD1" "$CMD2"
need "slot.sh status" "$W/paranoid.status" "${PHRASES[@]}"
PERF_FORCE_FAIL=1 STATUS=$W/f2.status bash "$HERE/f2perf.sh" > "$W/f2.out" 2>&1
need "f2perf.sh log" "$W/f2.out" "f2perf: SKIPPED" "${PHRASES[@]}" "$CMD1" "$CMD2"
need "f2perf.sh status" "$W/f2.status" "F2_SKIPPED" "${PHRASES[@]}"
lvl=$(cat /proc/sys/kernel/perf_event_paranoid 2>/dev/null || echo '?')
need "provenance" "$W/provenance.txt" "counters skipped:perf_event_paranoid=$lvl"
grep -qF "kernel.perf_event_paranoid=$lvl" "$W/time.out" && ok "the printed level is the current one ($lvl)" || bad "printed level is not $lvl"

# ---- C: the positive control
if PERF_FORCE_FAIL= bash -c ". '$HERE/paranoid.sh'; perf_probe"; then
  OUT=$OUT PHASE=F1 PASS_STATUS=$W/time2.status bash "$HERE/time.sh" --paranoid > "$W/time2.out" 2>&1
  grep -q 'SUGGESTION' "$W/time2.out" && bad "suggestion printed although counters work" || ok "no suggestion when counters work"
else
  echo "note: counters are unavailable on this box, so the positive control (C) is skipped"
fi

# ---- D, E: no sysctl / sudo / write under /etc in any script
scan() {   # dir -> number of violations; prints them
  local d=$1 n=0 f l
  local w1="sys" w2="ctl" s1="su" s2="do" e1="/et" e2="c/"
  for f in "$d"/*.sh; do
    [ "$(basename "$f")" = paranoid_check.sh ] && continue
    while IFS= read -r l; do
      [[ "$l" =~ ^[[:space:]]*# ]] && continue
      if [[ "$l" == *'#SUGGEST-TEXT' ]]; then
        [[ "$l" =~ ^[[:space:]]*(\{[[:space:]]*)?(echo|printf)[[:space:]] ]] || { echo "marker on a non-echo line: $f: $l"; n=$((n + 1)); }
        continue
      fi
      if [[ "$l" == *"$w1$w2"* || "$l" == *"$s1$s2"* || "$l" == *"$e1$e2"* ]]; then echo "forbidden mention: $f: $l"; n=$((n + 1)); fi
    done < "$f"
  done
  return "$n"
}
scan "$HERE" > "$W/scan.out"; n=$?
[ "$n" = 0 ] && ok "no sysctl/sudo/etc mention outside the marked suggestion text (all grid2/*.sh)" || { bad "scan of the real scripts found $n"; cat "$W/scan.out"; }
plant() {   # name  sed-expression-or-append  -> scan a copy of the scripts with the plant
  local nm=$1 line=$2
  rm -rf "$W/p"; mkdir -p "$W/p"; cp "$HERE"/*.sh "$W/p/"
  printf '%s\n' "$line" >> "$W/p/slot.sh"
  scan "$W/p" > "$W/p.out"; local k=$?
  [ "$k" -gt 0 ] && ok "plant '$nm' caught ($k)" || bad "plant '$nm' NOT caught"
}
plant "sysctl -w" "sys""ctl -w kernel.perf_event_paranoid=2"
plant "sudo" "su""do true"
plant "write under etc" "echo 1 > /et""c/sys""ctl.d/x.conf"
plant "marker on a non-echo line" "true #SUGGEST-TEXT"
echo "paranoid_check: passed=$passes failed=$fails"
[ "$fails" = 0 ]
