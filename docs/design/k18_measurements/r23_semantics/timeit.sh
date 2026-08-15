#!/bin/bash
P='((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,3}((?:[^a]*?|){1,2}?){2,3}){1,2}){2,3}'
cd /tmp/claude-1001/-home-duxevents-pcrec/60beed03-a1ef-4a00-ba48-76e468397d0d/scratchpad/r23/semantics
for b in base a a2 a2fix; do
  s=$(date +%s%N)
  if timeout 900 protos/$b/build/pcrec -p rx -o ct_$b.c -- "$P" >/dev/null 2>ct_$b.log; then
    e=$(date +%s%N); printf "%-6s ok    %8s ms\n" "$b" $(( (e-s)/1000000 ))
  else rc=$?; e=$(date +%s%N); printf "%-6s rc=%-3s %8s ms %s\n" "$b" "$rc" $(( (e-s)/1000000 )) "$(head -c 60 ct_$b.log)"; fi
done
PCREC_K18_STATS=1 timeout 900 protos/a2dup/build/pcrec -p rx -o ct_x.c -- "$P" 2>&1 >/dev/null | head -3
