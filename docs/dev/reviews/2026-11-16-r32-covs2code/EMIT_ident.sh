#!/bin/bash
# ident.sh PATS FLAGS... : base vs subject at the given flags; prints per pattern
D=/var/tmp/pcrec-pcrec/scratch/crit-covs2code/EMIT
PB=/var/tmp/pcrec-pcrec/scratch/crit-covs2code/base/build/pcrec
PS=/home/pcrec/projects/pcrec/worktrees/crit-covs2code/build/pcrec
pats=$1; shift; tag=$(echo "$*" | tr -c 'a-z0-9\n' _); mkdir -p $D/id/b $D/id/s
i=0
while IFS= read -r pat; do i=$((i+1))
  for t in b s; do P=$PB; [ $t = s ] && P=$PS
    nice timeout 120 $P -p rx "$@" -o $D/id/$t/a.c --pattern "$pat" > $D/id/$t.err 2>&1; echo $? > $D/id/$t.rc
    [ -f $D/id/$t/a.c ] && cat $D/id/$t/a.c $D/id/$t/a.h 2>/dev/null | sed -E '/[aA][bB][iI]/s/\b10[89]\b/ABI/g' > $D/id/$t.n || : > $D/id/$t.n
    rm -f $D/id/$t/a.c $D/id/$t/a.h
  done
  hdr=$(head -1 $D/id/s.n | cut -c1-90)
  r=$(grep -o 'RX_DFA_SCAN "[a-z-]*"' $D/id/s.n | head -1)
  if cmp -s $D/id/b.n $D/id/s.n && cmp -s $D/id/b.rc $D/id/s.rc && cmp -s $D/id/b.err $D/id/s.err; then st=SAME; else st=DIFF; cp $D/id/b.n $D/id/DIFF_${tag}_$i.b; cp $D/id/s.n $D/id/DIFF_${tag}_$i.s; fi
  echo "$st [$*] #$i rc=$(cat $D/id/s.rc) $r :: $pat"
done < "$pats"
