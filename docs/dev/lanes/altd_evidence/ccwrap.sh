#!/bin/bash
# ccwrap.sh ARGS... : gcc, but every generated matcher .c is first rewritten by altd.py with NO listing
# (-m AL, every scan_position choice point eligible, ALTD_RULE=all, ALTD_FOLLOW=1): the soundness-maximal twin
A=/var/tmp/pcrec-pcrec/scratch/altd; W=/home/pcrec/projects/pcrec/worktrees/trailgc; args=(); inc=()
for a in "$@"; do case "$a" in -I*) inc+=("$a");; esac; done
for a in "$@"; do
  if [[ "$a" == *.c ]] && [ -f "$a" ] && command grep -q 'RX_PUSH(&&\|_PUSH(&&' "$a" && command grep -q '__attribute__((unused));' "$a"; then
    if ALTD_RULE=all ALTD_FOLLOW=1 ALTD_CFLAGS="-I$W/lib -I$(dirname "$a") ${inc[*]}" python3 -I $A/tools/altd.py -m AL "$a" - "$a.altd.c" 2>>"${ALTD_LOG:-$A/altd_corpus.log}"; then
      args+=("$a.altd.c")
    else echo "REFUSED $a" >> "${ALTD_LOG:-$A/altd_corpus.log}"; args+=("$a"); fi
  else args+=("$a"); fi
done
exec gcc "${args[@]}"
