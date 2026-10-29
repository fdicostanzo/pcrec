#!/usr/bin/env bash
# p1build speed cells: walk (lane build) vs main (main's build/pcrec), find-all,
# instructions:u + cycles:u per pass (p1dsg's drv.c), REPS interleaved passes.
# BASE=deny compares against the lane build's own `-fno-landmark-walk` artifact
# (byte-identical to main's but for the abi number, checked on 5b at authoring)
# instead of main's binary, which moves with every merge.
set -u
S=${PCREC_TMPDIR:-/var/tmp/pcrec-$USER}/scratch/p1build/speed; mkdir -p $S
DRV=/home/pcrec/projects/pcrec/worktrees/p1build/docs/dev/lanes/p1dsg_evidence/drv.c
LW=/home/pcrec/projects/pcrec/worktrees/p1build/build/pcrec
MAIN=/home/pcrec/projects/pcrec/build/pcrec
MAINF=()
[ "${BASE:-main}" = deny ] && { MAIN=$LW; MAINF=(-fno-landmark-walk); }
REPS=${REPS:-5}
cell() {   # cell NAME ENC PATTERN SUBJECT
    local name=$1 enc=$2 pat=$3 subj=$4 e=()
    [ "$enc" = u ] && e=(-e utf8)
    for side in lw main; do
        local bin=$LW f=(); [ $side = main ] && { bin=$MAIN; f=("${MAINF[@]}"); }
        mkdir -p $S/$name/$side
        gnutimeout 60 $bin --features all "${e[@]}" "${f[@]}" -p rx -o $S/$name/$side/rx.c --pattern "$pat" || { echo "$name $side compile failed"; return; }
        gcc -O2 -DART=\"rx.c\" -I $S/$name/$side -o $S/$name/$side/drv $DRV || { echo "$name $side cc failed"; return; }
    done
    local scan; scan=$(sed -n 's/^#define RX_DFA_SCAN "\(.*\)"$/\1/p' $S/$name/lw/rx.c)
    : > $S/$name/lw.out; : > $S/$name/main.out
    for r in $(seq $REPS); do
        $S/$name/lw/drv $subj 1 >> $S/$name/lw.out
        $S/$name/main/drv $subj 1 >> $S/$name/main.out
    done
    python3 -I - "$name" "$scan" $S/$name/lw.out $S/$name/main.out <<'PY'
import sys,re,statistics as st
name,scan,a,b=sys.argv[1:]
def rd(p):
    rows=[dict(re.findall(r'(\w+)=(\S+)',l)) for l in open(p)]
    return rows
A=rd(a);B=rd(b)
same = all(x['res']==y['res'] and x['hash']==y['hash'] for x,y in zip(A,B))
ia=st.median(int(x['instr']) for x in A); ib=st.median(int(x['instr']) for x in B)
ca=st.median(int(x['cycles']) for x in A); cb=st.median(int(x['cycles']) for x in B)
print(f"{name}\tscan={scan}\tres={A[0]['res']}\tanswers={'same' if same else 'DIFFER'}\tinstr lw={ia:,.0f} main={ib:,.0f} x{ib/ia:.2f}\tcycles lw={ca:,.0f} main={cb:,.0f} x{cb/ca:.2f}")
PY
}
SUB=/var/tmp/pcrec-pcrec/scratch/p1dsg/subj
TP=/home/pcrec/projects/pcrec-bench/bench/syntax/throughput
EMAIL='[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
cell 5b-accmain b "$EMAIL" $SUB/acc-main.log
cell 5b-accsmall b "$EMAIL" $SUB/acc-small.log
cell 5b-fzme-N1 b "$EMAIL" $SUB/fz-me.log
cell 5b-qs200k b "$EMAIL" $SUB/qs-200k.log
cell qntplus-t1m b 'a+b' $TP/t-1m.bin
cell qntplus-t256k b 'a+b' $TP/t-256k.bin
cell lw-az-accsmall b '[a-z]+@x' $SUB/acc-small.log
