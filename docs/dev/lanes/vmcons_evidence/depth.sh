#!/bin/bash
# depth.sh K MODE ARM HI : largest nesting that answers. K cscan (nest-brace '(?{ {{..x;..}} })') | json ('[[..1..]]'); ARM pd (default) | pl (_in, NF/NT env)
V=/var/tmp/pcrec-pcrec/scratch/vmbc; k=$1; m=$2; arm=$3; d=/var/tmp/pcrec-pcrec/scratch/vmcons/b/${k}_$m/drv
ok() { local n=$1 f=$V/subj/$k$1.bin
  if [ ! -f $f ]; then
    if [ $k = cscan ]; then python3 -I -c "import sys;n=int(sys.argv[1]);sys.stdout.write('(?{ '+'{'*n+' x; '+'}'*n+' })')" $n > $f
    else python3 -I -c "import sys;n=int(sys.argv[1]);sys.stdout.write('['*n+'1'+']'*n)" $n > $f; fi
  fi
  case $arm in
    pd) gnutimeout 60 $d $f d | command grep -q 'default rc=1' ;;
    pl) REPS=1 gnutimeout 300 $d $f r | command grep -q 'r rc=1' ;;
  esac; }
lo=1; hi=$4; ok $lo || { echo 0; exit; }; ok $hi && { echo ">=$hi"; exit; }
while [ $((hi-lo)) -gt 1 ]; do x=$(((lo+hi)/2)); if ok $x; then lo=$x; else hi=$x; fi; done; echo $lo
