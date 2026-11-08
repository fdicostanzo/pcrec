#!/bin/bash
# usage: or.sh PATTERN SUBJECT START... ; prints one line
pat=$1; subj=$2; shift 2; hx(){ printf '%s' "$1" | od -An -tx1 -v | tr -d ' \n'; }
args=(); for s in "$@"; do args+=("$s:$(hx "$subj")"); done
printf '%s on %s from %s: ' "$pat" "$subj" "$*"; ${P2PROBE:-p2probe} "" "$(hx "$pat")" "${args[@]}" | tail -n +2 | tr '\n' '/'; echo
