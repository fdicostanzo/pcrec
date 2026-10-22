#!/bin/sh
# Builds the artifacts the hand-written API drivers use, then each driver
# under ASan+UBSan (and t_threads also under TSan), and runs them.
# usage: api/build.sh [PCREC]   (default: $PCREC, else the tree's build/pcrec)
# substfix (adoption): paths, the timeout binary and the compiler from the
# environment ($OUT is required).
# substb2: the R4 interface -- the support unit is emitted once ($O/support.h,
# each driver defines PCREC_SUPPORT_IMPLEMENTATION in t.h), and unset handling
# is the run-time RX_SUBST_STRICT flag, so no artifact is compiled with
# --unset=.
set -u
D=$(cd "$(dirname "$0")" && pwd)
P=${1:-${PCREC:-$D/../../../../build/pcrec}}
O=${OUT:?OUT must name a scratch directory}
mkdir -p "$O"
T="${TIMEOUT_BIN:-timeout} 60"
gcc() { command "${CC:-gcc}" "$@"; }
rx() { pfx=$1; shift; $T "$P" --features all -p "$pfx" -o "$O/$pfx.c" "$@" || echo "RX-FAIL $pfx"; }
sb() { pfx=$1; shift; $T "$P" -p "$pfx" -o "$O/$pfx.c" "$@" || echo "SUBST-FAIL $pfx"; }

rx ra --pattern '(a)(b)?'
rx rb --pattern '(x)(y)'
rx rn --pattern '(?<n>a)(?<m>b)?(c)?'
rx rd --pattern '(?J)(?<n>a)|(?<n>b)'
rx rk --pattern 'a\Kb'
rx rs --engine=vm --step-budget=1000 --pattern '(.*a){12}'
rx rx1 --engine=vm --step-budget=1000 --pattern 'x|(.*a){12}'
rx ru -e utf8 --pattern 'x*'
rx ru2 -e utf8 --pattern '.'
rx rnc --no-captures --pattern '(a)'
rx rv --pattern 'a'
rx rz --pattern 'zz(?<zz>q)'
rx rg --pattern 'a'
rx rgg --pattern '\Ga'
rx rlb --pattern '(?<=a)b'
rx rck -e utf8 -futf-check --pattern '.'
rx ral -e utf8 -fstartpos-guard=align --pattern '.'
sb s1 --subst '[$1]'
sb s2 --subst '<$0>'
sb sn --subst '$3${zz}$1'
sb snm --subst '[$n|$m|$1]'
sb sv --subst '[${!v}|${!w}|${!v}]'
sb sve --subst '[${!v}|${!w}]'
sb se1 --subst '[$1|$2]'
sb s0 --subst '$0'
sb sall --subst '$n$2$0${n}$1$n${m}$0$2'
printf 'a\000$1\000b' > "$O/snul.tpl"; sb snul --subst-file "$O/snul.tpl"
sb snone --subst 'lit'
sb sdn --subst '<$n>'
$T "$P" --emit-support -o "$O/support.h" || echo "SUBST-FAIL support"

SAN="-fsanitize=address,undefined -fno-sanitize-recover=undefined -g -O1 -std=gnu11"
fail=0
for c in "$O"/r*.c "$O"/s*.c; do
  b=$(basename "$c" .c)
  $T gcc $SAN -c -I "$O" -o "$O/$b.o" "$c" || { echo "CC-FAIL $b"; fail=1; }
done
for t in t_bind t_element t_glue t_vars t_shape t_iter t_threads t_utf; do
  $T gcc $SAN -I "$O" -o "$O/$t" "$D/$t.c" "$O"/r*.o "$O"/s*.o -lpthread || { echo "BUILD-FAIL $t"; fail=1; continue; }
  ASAN_OPTIONS=detect_leaks=1 $T "$O/$t" > "$O/$t.log" 2>&1; rc=$?
  echo "== $t exit $rc: $(grep -c '^PASS' "$O/$t.log") pass, $(grep -c '^FAIL' "$O/$t.log") fail"
  grep -E '^FAIL|runtime error|Sanitizer' "$O/$t.log"
done
# threads: ASan build and TSan build (TSan objects are separate)
mkdir -p "$O/tsan"
for c in "$O"/ra.c "$O"/s1.c; do b=$(basename "$c" .c); $T gcc -fsanitize=thread -g -O1 -c -I "$O" -o "$O/tsan/$b.o" "$c"; done
$T gcc -fsanitize=thread -g -O1 -I "$O" -o "$O/t_threads_tsan" "$D/t_threads.c" "$O/tsan/ra.o" "$O/tsan/s1.o" -lpthread \
  && { $T "$O/t_threads_tsan" > "$O/t_threads_tsan.log" 2>&1; echo "== t_threads(tsan) exit $?: $(grep -c '^PASS' "$O/t_threads_tsan.log") pass"; grep -E '^FAIL|WARNING' "$O/t_threads_tsan.log"; }
exit $fail
