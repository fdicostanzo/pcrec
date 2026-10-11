#!/bin/bash
# check_twins.sh — build every lrdfa hand-twin from the shipped artifacts and
# check its ANSWERS (every span, find-all) against its base artifact AND
# libpcre2 10.46 (p2spans) on the set's throughput + short subjects (+ the waf
# match.bin for capability, whose throughput subjects hold zero matches).
# No timing. Env: L (scratch: art/, tw/, bench/, match/), REPO (pcrec checkout
# whose build/pcrec compiled art/). Prints one verdict line per (twin, subject
# group) and exits 1 on any difference.
set -u
L=${L:?}; REPO=${REPO:?}; H=$(cd "$(dirname "$0")" && pwd)
W=$REPO/docs/dev/optloop/waf; WS=$REPO/studies/walk_survey
A=$L/art; T=$L/tw; B=$L/bench/bench; P=$REPO/build/pcrec
export TMPDIR=$L
mkdir -p $T
gcc -O2 -o $L/p2spans $H/p2spans.c -lpcre2-8 || exit 2
esc() { python3 -c '
import sys
b=open(sys.argv[1],"rb").read().rstrip(b"\n"); o=[]
for c in b:
    o.append("\\\\" if c==0x5c else "\\\"" if c==0x22 else chr(c) if 0x20<=c<0x7f else "\\x%02x"%c)
print("\""+"".join(o)+"\"",end="")' "$1"; }
spans() {   # spans OUTBIN SRC.c HDR.h  — link waf/spans.c against an artifact
    local d=$(mktemp -d); cp "$3" $d/art.h
    gcc -O2 -I$d -I"$(dirname "$2")" -I$A -o "$1" $W/spans.c "$2" ${4:-} || return 1; rm -rf $d; }
rc=0
check() {   # check NAME SET PATTERN_FILE BASE.c TWIN.c [extra twin objects]
    local name=$1 set=$2 pf=$3 base=$4 twin=$5; shift 5
    spans $T/$name.base "$base" "${base%.c}.h" || { echo "BUILD-FAIL base $name"; rc=1; return; }
    spans $T/$name.twin "$twin" "${TWIN_H:-${base%.c}.h}" "$*" || { echo "BUILD-FAIL twin $name"; rc=1; return; }
    local subs="$B/$set/throughput/*.bin $B/$set/subjects/*"; [ $set = capability ] && subs="$subs $L/match/match.bin"
    local nsub=0 same=0 diff=0 orc=0 m=0
    for s in $subs; do
        nsub=$((nsub+1))
        $T/$name.base "$s" > $T/b.out; $T/$name.twin "$s" > $T/t.out; $L/p2spans "$pf" "$s" > $T/o.out
        if cmp -s $T/b.out $T/t.out && cmp -s $T/t.out $T/o.out; then same=$((same+1)); m=$((m+$(tail -1 $T/o.out | cut -d= -f2)))
        else diff=$((diff+1)); echo "  DIFF $name $(basename $s): base $(tail -1 $T/b.out) twin $(tail -1 $T/t.out) p2 $(tail -1 $T/o.out)"; fi
    done
    [ $diff = 0 ] && echo "SAME   $name: $same/$nsub subjects, $m matches (base = twin = libpcre2 10.46, span for span)" || { echo "DIFF   $name: $diff of $nsub"; rc=1; }
}
# 1. plainloop (per-step / skip dispatch): the DFA steps every byte
for c in capability:hex8-bounded capability:wild-waf-crs-942140-dbnames capability:wild-codegrammar-json-constant; do
    s=${c%%:*}; p=${c#*:}; python3 $W/mk_twin.py plainloop $A/${s}__$p.c $T/${s}__${p}__plain.c >/dev/null
    check ${p}__plain $s $B/$s/patterns/$p.rx $A/${s}__$p.c $T/${s}__${p}__plain.c
done
# 1b. the existing deny arm -fno-start-set (no DFA hat) — a compiler arm, not a hand edit
for c in capability:hex8-bounded capability:wild-waf-crs-942140-dbnames capability:wild-codegrammar-json-constant; do
    s=${c%%:*}; p=${c#*:}; $P --features all -fno-start-set -p rx -o $T/${s}__${p}__nostart.c --pattern-esc --pattern "$(esc $B/$s/patterns/$p.rx)" 2>/dev/null
    check ${p}__nostart $s $B/$s/patterns/$p.rx $A/${s}__$p.c $T/${s}__${p}__nostart.c
done
# 2. union-select: the caseless run pre-check scanning another member (pick rate)
u=capability__wild-waf-crs-942270-union-select; up=$B/capability/patterns/wild-waf-crs-942270-union-select.rx
$P --features all -fno-req-run -p rx -o $T/${u}__norun.c --pattern-esc --pattern "$(esc $up)" 2>/dev/null
for v in "select c" "from m" "from f" "union u"; do set -- $v
    python3 $W/mk_twin.py ciprecheck $T/${u}__norun.c $T/${u}__$1_$2.c $1 $2 >/dev/null
    TWIN_H=$T/${u}__norun.h check union-select__$1_$2 capability $up $A/$u.c $T/${u}__$1_$2.c; unset TWIN_H
done
# 3. K101 bounded streams (mod-i, mod-r)
for p in mod-i mod-r; do python3 $H/mk_twin_dfa.py k101 $A/syntax__$p.c $T/syntax__${p}__k101.c >/dev/null
    check ${p}__k101 syntax $B/syntax/patterns/$p.rx $A/syntax__$p.c $T/syntax__${p}__k101.c; done
# 4. email-owasp: G2-off whole-window '@' pre-check
e=capability__wild-validator-email-owasp
python3 $H/mk_twin_dfa.py precheck $A/$e.c $T/${e}__precheck.c 64 >/dev/null
check email-owasp__precheck capability $B/capability/patterns/wild-validator-email-owasp.rx $A/$e.c $T/${e}__precheck.c
python3 $H/mk_twin_dfa.py deferpre $A/$e.c $T/${e}__deferpre.c 64 64 >/dev/null
check email-owasp__deferpre capability $B/capability/patterns/wild-validator-email-owasp.rx $A/$e.c $T/${e}__deferpre.c
# 5. landing start (K4 / [START-LANDING-EXC]): line-80, cls-atleast-4096
for p in line-80 cls-atleast-4096; do
    if python3 $WS/landtwin.py $A/bounded__$p.c $T/bounded__${p}__land.c 2>$T/land.err; then
        check ${p}__land bounded $B/bounded/patterns/$p.rx $A/bounded__$p.c $T/bounded__${p}__land.c
    else echo "NOT-TWINNABLE ${p}__land: $(cat $T/land.err)"; fi; done
# 6. concat-sqli: [OPT-ATTEMPT-SPLIT] exact twin
c=capability__wild-waf-crs-942360-concat-sqli; cp=$B/capability/patterns/wild-waf-crs-942360-concat-sqli.rx
python3 $H/mk_split.py $cp $T/split >/dev/null
for x in u a; do $P --features all -p s$x -o $T/split/s$x.c --pattern-esc --pattern "$(esc $T/split/$x.rx)" 2>/dev/null; done
TWIN_H=$H/split_rx.h check concat-sqli__split capability $cp $A/$c.c $H/split_rx.c $T/split/su.c $T/split/sa.c; unset TWIN_H
# 7. high-byte-run: SWAR high-bit skip
python3 $H/mk_twin_dfa.py hiskip $A/capability__high-byte-run.c $T/capability__high-byte-run__hiskip.c >/dev/null
check high-byte-run__hiskip capability $B/capability/patterns/high-byte-run.rx $A/capability__high-byte-run.c $T/capability__high-byte-run__hiskip.c
# 8. failing-direction control: a planted k101 (rare stream never searched) MUST differ
python3 $H/mk_twin_dfa.py k101plant $A/syntax__mod-i.c $T/syntax__mod-i__plant.c >/dev/null
prc=$rc; check mod-i__k101PLANT syntax $B/syntax/patterns/mod-i.rx $A/syntax__mod-i.c $T/syntax__mod-i__plant.c
if [ $rc = $prc ]; then echo "CONTROL FAILED: the planted twin read SAME"; rc=1; else echo "CONTROL OK: the planted twin is caught"; rc=$prc; fi
exit $rc
