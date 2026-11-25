#!/usr/bin/env bash
# retab.sh CENSUSDIR: re-tabulate pres_reach_census.sh's work directory, *.n0 artifacts excluded
S="$1"
for d in "$S"/S*; do id=$(basename "$d"); moved=0 files=0
  for f in $(cd "$S/clean" && ls -d */g2p_sites.c *.log tr.*.err | grep -v '^build.log$' | grep -v '\.n0'); do
    files=$((files+1)); cmp -s "$S/clean/$f" "$d/$f" || moved=$((moved+1)); done
  c0=""; cmp -s "$S/clean/c0/census0.py" "$d/c0/census0.py" || c0=" (edits the @c0 census copy only)"
  if [ "$moved" = 0 ]; then echo "REACH $id UNREACHED-BY-GENERATOR (0 of $files artifacts moved)$c0"; else echo "REACH $id moved $moved of $files artifacts$c0"; fi
done
