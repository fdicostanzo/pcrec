#!/usr/bin/env bash
# minwb.sh ENVSPEC PATTERN SUBJECT -> minimum --work-budget giving a non-"work" answer
envs="$1"; pat="$2"; subj="$3"; lo=1; hi=2000000
for wb in $hi; do env $envs ./pcrec_shim -p rx --engine=vm --fno-step-budget --work-budget=$wb --emit-main -o mw.c --pattern "$pat" 2>/dev/null; done
while [ $lo -lt $hi ]; do mid=$(( (lo+hi)/2 )); env $envs ./pcrec_shim -p rx --engine=vm --work-budget=$mid --emit-main -o mw.c --pattern "$pat" && gcc-16 -w -O1 -o mw mw.c; r=$(./mw "$subj"); if [ "$r" = work ]; then lo=$((mid+1)); else hi=$mid; fi; done; echo "$lo $(./mw "$subj")"
