#!/bin/bash
# plant.sh SID : copy the worktree's sources, plant SID, build, run run_trail_compact.sh
S=/var/tmp/pcrec-pcrec/scratch/trailgc3; W=/home/pcrec/projects/pcrec/worktrees/trailgc
id=$1; f=$(ls $W/tests/mech/sabotages/${id}_*.sh); d=$S/sab/$id; rm -rf $d; mkdir -p $d
tar -C $W --exclude=./build --exclude=./build-asan --exclude=./build-ubsan --exclude=./.git -cf - . | tar -C $d -xf -
python3 - "$f" "$d" <<'PY'
import sys,subprocess
f,d=sys.argv[1],sys.argv[2]
env=subprocess.run(['bash','-c','. "%s"; printf "%%s\\0%%s\\0%%s" "$SAB_FILE" "$SAB_BEFORE" "$SAB_AFTER"'%f],capture_output=True).stdout.decode().split('\0')
p=d+'/'+env[0]; s=open(p).read(); assert s.count(env[1])==1,(env[1],s.count(env[1])); open(p,'w').write(s.replace(env[1],env[2]))
PY
make -C $d -j8 >$d/build.log 2>&1 || { echo "$id BUILD FAILED"; exit 1; }
(cd $d && TMPDIR=/var/tmp/pcrec-pcrec TRAIL_CORPUS=${TRAIL_CORPUS:-0} gnutimeout 900 bash tests/vm/run_trail_compact.sh > $d/tc.log 2>&1)
echo "$id: $(command grep -E '^checks (passed|failed)' $d/tc.log | tr '\n' ' ')"; command grep FAIL $d/tc.log | head -4 | cut -c1-200
