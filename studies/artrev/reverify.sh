#!/usr/bin/env bash
# reverify.sh -- [ARTREV] re-run the HARDENED identity (default + shrunk resources + window start)
# over a set of sealed twin patches, in a scratch ARTREV_ROOT, and print one verdict row per twin.
#
#   reverify.sh OUTDIR ARTIFACT_SRC_DIR NAME PATCHDIR[,PATCHDIR...] "SUBJECT_ARGS" "IDENTITY_ARGS" [--san]
#
# ARTIFACT_SRC_DIR  a build-artrev/<NAME>/ holding the pinned artifact.c/.h + meta.json + arms/orig
#                   (a reviewer cell's, or a regenerated one); copied, never modified.
# PATCHDIR          directories of NAME.rN.patch files (the sealed twins; `ctl*` ones are controls).
# Every patch is applied as an UNCOUNTED control arm (`twin --patch --control`), so the bounds ledger
# of the real artifact is untouched.  Output: OUTDIR/verdicts.tsv  (arm, mode, status, first line of why).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$1; SRC=$2; NAME=$3; PDIRS=$4; SUBJ=$5; IDARGS=$6; SAN=${7:-}
export ARTREV_CC=${ARTREV_CC:-gcc-16}
export ARTREV_ROOT=$OUT/root
export ARTREV_HOST_ROOT=${ARTREV_HOST_ROOT:-$(git -C "$HERE" rev-parse --git-common-dir | sed 's#/\.git$##')}
A="python3 -B $HERE/artrev.py"
rm -rf "$OUT/root"; mkdir -p "$OUT/root/$NAME/arms" "$OUT/logs"
for f in artifact.c artifact.h artifact.s meta.json GENERATION.txt pattern.bin; do cp "$SRC/$f" "$OUT/root/$NAME/" 2>/dev/null; done
cp -R "$SRC/arms/orig" "$SRC/arms/orig2" "$OUT/root/$NAME/arms/"; rm -rf "$OUT"/root/$NAME/arms/*/build
$A twin $NAME null --null >/dev/null
printf 'arm\tmode\tstatus\twhy\n' > "$OUT/verdicts.tsv"
for pd in ${PDIRS//,/ }; do
  for p in "$pd"/*.patch; do
    b=$(basename "$p" .patch); arm=$(echo "$b" | tr '.' '_'); [ "$b" = null.r1 ] && continue
    if ! $A twin $NAME "$arm" --patch "$p" --control > "$OUT/logs/$arm.twin.log" 2>&1; then
      printf '%s\t-\tNOAPPLY\t%s\n' "$arm" "$(tail -1 "$OUT/logs/$arm.twin.log" | cut -c1-160)" >> "$OUT/verdicts.tsv"; continue; fi
    for mode in plain $SAN; do
      extra=""; [ "$mode" = san ] && extra="--san"
      # shellcheck disable=SC2086
      eval "$A identity $NAME $arm $SUBJ $IDARGS $extra" > "$OUT/logs/$arm.$mode.log" 2>&1
      rc=$?
      st=$(grep -m1 '^IDENTITY' "$OUT/logs/$arm.$mode.log" | awk '{print $2}'); [ -z "$st" ] && st="ERROR(rc=$rc)"
      why=$(grep -m1 -E 'GIVE-UP RULE VIOLATED|FIRST DIFFERENCE|REPAIR DISAGREES|window start: .*start differences [1-9]|FAILED|LIVELOCK' "$OUT/logs/$arm.$mode.log" | cut -c1-160)
      printf '%s\t%s\t%s\t%s\n' "$arm" "$mode" "$st" "$why" >> "$OUT/verdicts.tsv"
    done
  done
done
cat "$OUT/verdicts.tsv"
