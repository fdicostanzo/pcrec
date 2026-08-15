#!/bin/bash
cd /tmp/claude-1001/-home-duxevents-pcrec/60beed03-a1ef-4a00-ba48-76e468397d0d/scratchpad/r23/semantics
for P in "$@"; do
  echo "PAT $P"
  for b in base a2; do
    s=$(date +%s%N)
    if timeout 240 protos/$b/build/pcrec -p rx -o tt_$b.c -- "$P" >/dev/null 2>tt_$b.log; then
      e=$(date +%s%N); printf "   %-5s ok    %8s ms\n" "$b" $(( (e-s)/1000000 ))
    else rc=$?; e=$(date +%s%N); printf "   %-5s rc=%-3s %8s ms %s\n" "$b" "$rc" $(( (e-s)/1000000 )) "$(head -c 50 tt_$b.log)"; fi
  done
done
