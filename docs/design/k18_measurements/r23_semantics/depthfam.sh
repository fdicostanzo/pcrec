#!/bin/bash
cd /tmp/claude-1001/-home-duxevents-pcrec/60beed03-a1ef-4a00-ba48-76e468397d0d/scratchpad/r23/semantics
printf "%-8s %-46s %-10s %-10s %s\n" "k" "pattern" "base_ms" "a2_ms" "a2 counters(rev)"
for k in 2 3 4 5 6 7 8; do
  P="((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,$k}(){2,3}){1,2}){2,3}"
  s=$(date +%s%N); timeout 300 protos/base/build/pcrec -p rx -o d_b.c -- "$P" >/dev/null 2>&1; rb=$?; e=$(date +%s%N); tb=$(( (e-s)/1000000 ))
  s=$(date +%s%N); timeout 300 protos/a2/build/pcrec  -p rx -o d_a.c -- "$P" >/dev/null 2>&1; ra=$?; e=$(date +%s%N); ta=$(( (e-s)/1000000 ))
  c=$(PCREC_K18_STATS=1 timeout 300 protos/a2dup/build/pcrec -p rx -o d_c.c -- "$P" 2>&1 >/dev/null | tail -1 | grep -o "redirects=[0-9]* nonstacktop=[0-9]* maxdepth=[0-9]* ctxs=[0-9]*")
  printf "%-8s %-46s %-10s %-10s %s\n" "$k" "${P:0:44}" "${tb}(rc$rb)" "${ta}(rc$ra)" "$c"
done
