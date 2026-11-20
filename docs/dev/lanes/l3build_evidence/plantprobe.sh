#!/usr/bin/env bash
# plantprobe.sh ID ARGS...: apply sabotage ID in the plant tree, rebuild, compare `pcrec ARGS` output planted vs clean
S=/var/tmp/pcrec-pcrec/scratch/l3build; P=$S/plant; id=$1; shift
f=$(ls $P/tests/mech/sabotages/${id}_*.sh); eval "$(bash -c '. "$1" >/dev/null 2>&1; declare -p SAB_FILE SAB_BEFORE SAB_AFTER SAB_COUNT' _ "$f")"
printf '%s' "$SAB_BEFORE" > $S/b.txt; printf '%s' "$SAB_AFTER" > $S/a.txt
clean=$($P/build/pcrec "$@" 2>&1 | md5sum)
cp "$P/$SAB_FILE" $S/orig.save
python3 $P/tests/mech/lib/replace.py "$P/$SAB_FILE" $S/b.txt $S/a.txt "${SAB_COUNT:-1}" || { echo "$id: REPLACE FAILED"; exit 1; }
if timeout 600 make -C $P -j8 >$S/plant.build.log 2>&1; then
  planted=$($P/build/pcrec "$@" 2>&1 | md5sum)
  [ "$clean" != "$planted" ] && echo "$id: plant compiles; output MOVES on: $*" || echo "$id: plant compiles; output unchanged on: $*"
else echo "$id: PLANT BUILD FAILED"; grep -m3 error $S/plant.build.log; fi
cp $S/orig.save "$P/$SAB_FILE"; touch "$P/$SAB_FILE"
