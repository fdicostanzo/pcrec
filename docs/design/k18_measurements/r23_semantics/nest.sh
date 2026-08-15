#!/bin/bash
cd /tmp/claude-1001/-home-duxevents-pcrec/60beed03-a1ef-4a00-ba48-76e468397d0d/scratchpad/r23/semantics
mknest() { local d=$1 p="a*"; for ((i=0;i<d;i++)); do p="(?:$p)*"; done; echo "$p"; }
printf "%-6s %-10s %-10s %-10s %s\n" "depth" "base" "A2" "A2FIX" "A2 counters"
for d in 16 32 64 100 200 250; do
  P=$(mknest $d)
  for b in base a2 a2fix; do
    s=$(date +%s%N); timeout 300 protos/$b/build/pcrec -p rx -o n_$b.c -- "$P" >/dev/null 2>&1; rc=$?; e=$(date +%s%N)
    eval "t_$b=$(( (e-s)/1000000 ))ms(rc$rc)"
  done
  c=$(PCREC_K18_STATS=1 timeout 300 protos/a2dup/build/pcrec -p rx -o n_c.c -- "$P" 2>&1 >/dev/null | tail -1 | grep -o "redirects=[0-9]* nonstacktop=[0-9]* maxdepth=[0-9]* ctxs=[0-9]*")
  printf "%-6s %-10s %-10s %-10s %s\n" "$d" "$t_base" "$t_a2" "$t_a2fix" "$c"
done
