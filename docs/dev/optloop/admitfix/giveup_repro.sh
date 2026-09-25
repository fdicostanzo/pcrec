#!/usr/bin/env bash
# [B84] finding 1 reproduced on darwin: email-nested-plus, short-subject-search,
# at b1885a83 and 6ef76820, the bench's forced-VM (`--features all --engine=vm`)
# and auto (`--features all`) configs, over the 75 capability short subjects
# (regenerated from pcrec-bench's gen_subjects.build(), sha256-checked against
# its manifest.tsv) and the three throughput subjects (captext.text, checked
# against manifest_throughput.tsv).  Each artifact is instrumented with ONE
# line after rx_search_run() returns -- g_steps = RX_STEP_BUDGET -
# run.steps_left -- so the driver prints the VM steps each call consumed.
# (The count is only meaningful when rx_search_run initialised the run state;
# where the pre-check returned first it reads 0 or garbage, and the rc says so.)
#
#   SCR=<scratch with b1885a83/ and 6ef76820/ trees built> ./giveup_repro.sh
# Outputs: $SCR/out/<pin>/<cfg>/{run,thr}.txt
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
: "${SCR:?}"; cd "$SCR"
BENCH=/Users/fdicostanzo/pcrec-bench/bench/capability
mkdir -p subj thr
PYTHONDONTWRITEBYTECODE=1 python3 - "$BENCH" <<'PY'
import sys, hashlib, csv
B=sys.argv[1]; sys.path.insert(0,B); sys.path.insert(0,B+"/../..")
import gen_subjects, captext
man={r['id']:r['sha256'] for r in csv.DictReader(open(B+"/manifest.tsv"),delimiter='\t')}
ok=0
for sid,_d,body in gen_subjects.build():
    open("subj/%s.bin"%sid,"wb").write(body); ok+=hashlib.sha256(body).hexdigest()==man[sid]
mt={r['id']:r['sha256'] for r in csv.DictReader(open(B+"/manifest_throughput.tsv"),delimiter='\t')}
okt=0
for sid,n,seed in (("t-64k",64*1024,0xC0FFEE1),("t-256k",256*1024,0xC0FFEE2),("t-1m",1024*1024,0xC0FFEE3)):
    b=captext.text(n,seed); open("thr/%s.bin"%sid,"wb").write(b); okt+=hashlib.sha256(b).hexdigest()==mt.get(sid)
print("short subjects sha-match %d/75, throughput %d/3" % (ok, okt))
PY
P='^([a-zA-Z0-9._%+-]+)+@'
for r in b1885a83 6ef76820; do for c in vm auto; do
  case $c in vm) F="--features all --engine=vm";; auto) F="--features all";; esac
  d=out/$r/$c; mkdir -p $d
  $r/build/pcrec -p rx $F -o $d/enp.c --pattern "$P"
  sed 's/^\(    result = rx_search_run(subject, subject_length, search_from, capture_spans, &run);\)/\1 g_steps = RX_STEP_BUDGET - run.steps_left;/' $d/enp.c > $d/enp_i.c
  gcc-16 -O2 -DARTIFACT="\"$SCR/$d/enp_i.c\"" -o $d/drv "$HERE/steps_driver.c"
  timeout 900 $d/drv subj/*.bin > $d/run.txt
  timeout 60 $d/drv thr/*.bin > $d/thr.txt
  echo "$r $c: $(awk '{print $3}' $d/run.txt | sort | uniq -c | tr -s ' ' | tr '\n' ';')"
done; done
