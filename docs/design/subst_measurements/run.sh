#!/usr/bin/env bash
# subst phase-A probe (replace_design.md §R2): compile nine artifacts with the
# given pcrec, link the independent-element glue against them and libpcre2-8,
# and compare every cell with pcre2_substitute. Usage: run.sh PCREC OUTDIR
set -eu
B=$1 O=$2 H=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$O"
c(){ "$B" -p "$1" -o "$O/$1.c" --features named-groups,assertions,classes,lookaround --pattern "$2"; }
c ast 'a*'; c alt '(a)|(b)'; c ab '(a+)b'; c ymd '(?<y>\d+)-(?<m>\d+)'; c mdy '(?<m>\d+)/(?<y>\d+)'
c ea '|a'; c xy 'x*|y'; c kr 'ab\K'; c lb '(?<=(a))b'
gcc -O2 -Wall -Wextra -std=gnu11 -I"$O" -o "$O/glue" "$H/glue.c" "$O"/{ast,alt,ab,ymd,mdy,ea,xy,kr,lb}.c -lpcre2-8
"$O/glue"
