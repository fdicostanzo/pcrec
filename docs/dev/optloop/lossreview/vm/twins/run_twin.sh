#!/bin/bash
# run_twin.sh NAME SET/PATTERN KIND SPEC
#   KIND transform  SPEC = twin.py transform list (applied to today's artifact)
#   KIND flags      SPEC = extra pcrec flags for the twin (the deny/axis twin)
#   KIND pattern    SPEC = the rewritten pattern text for the twin
# Builds base (today, --features all) and twin as the bench builds them
# (gcc -O2 -fPIC -shared), links the answer driver (fadrv.c) and the timing
# driver (fatime.c) against each, ANSWER-CHECKS twin vs base over the set's
# throughput AND short subjects plus extra_subjects.py's discriminating ones
# (per-subject find-all match count + span checksum), and writes
# $LR/twins/NAME/time.sh: the interleaved timing command for a quiet slot
# (NOT run here). Env: LR, PCREC, BENCHCOPY.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
: "${LR:?}" "${PCREC:?}" "${BENCHCOPY:?}"
name=$1 sp=$2 kind=$3 spec=$4
set_=${sp%/*}; pat=${sp#*/}
D=$LR/twins/$name; rm -rf "$D"; mkdir -p "$D/base" "$D/twin"
P="$(cat "$BENCHCOPY/bench/$set_/patterns/$pat.rx")"
"$PCREC" --features all -o "$D/base/rx.c" --pattern "$P"
case $kind in
  transform) cp "$D/base/rx.h" "$D/twin/rx.h"
             python3 "$HERE/twin.py" "$D/base/rx.c" "$D/twin/rx.c" "$spec" ;;
  flags)     "$PCREC" --features all $spec -o "$D/twin/rx.c" --pattern "$P" ;;
  pattern)   "$PCREC" --features all -o "$D/twin/rx.c" --pattern "$spec" ;;
  *) echo "bad kind $kind"; exit 2 ;;
esac
SUBJ=$(ls "$BENCHCOPY/bench/$set_/throughput/"*.bin)
SHORT=$(ls "$BENCHCOPY/bench/$set_/subjects/"*.bin 2>/dev/null || true)
python3 "$HERE/extra_subjects.py" "$sp" "$D/extra" >/dev/null
EXTRA=$(ls "$D/extra/"*.bin 2>/dev/null || true)
for v in base twin; do
  ( cd "$D/$v"
    gcc -O2 -fPIC -shared -o librx.so rx.c
    gcc -O2 -I. -o fadrv "$HERE/../fadrv.c" -L. -lrx -Wl,-rpath,"$D/$v"
    gcc -O2 -I. -o fatime "$HERE/fatime.c" -L. -lrx -Wl,-rpath,"$D/$v"
    taskset -c 12-15 gnutimeout 900 ./fadrv $SUBJ $SHORT $EXTRA | sed -e "s#$BENCHCOPY/##" -e "s#$D/##" > answers.txt )
done
if cmp -s "$D/base/answers.txt" "$D/twin/answers.txt"; then
  echo "ANSWERS IDENTICAL ($name): $(grep -c . "$D/base/answers.txt") subjects, $(awk -F'\t' '{split($4,a,"=");m+=a[2]} END{print m}' "$D/base/answers.txt") matches"
else
  echo "ANSWERS DIFFER ($name)"; diff "$D/base/answers.txt" "$D/twin/answers.txt" | head; exit 1
fi
cat > "$D/time.sh" <<EOT
#!/bin/bash
# QUIET SLOT ONLY (scratch tier): 9 interleaved rounds, base then twin, pinned.
for r in 1 2 3 4 5 6 7 8 9; do
  for v in base twin; do echo "== \$v round \$r"; taskset -c 14 "$D/\$v/fatime" 5 $SUBJ | tail -1; done
done
EOT
chmod +x "$D/time.sh"
