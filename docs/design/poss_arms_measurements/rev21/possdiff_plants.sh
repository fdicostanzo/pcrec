#!/usr/bin/env bash
# Runs possdiff_exh.sh over every rev-2 pattern file: once with the arms as
# designed (must agree everywhere, reach complete), once per sabotage plant
# (each must be DETECTED: a divergence, on its own witness), and the C-1
# route-flip witnesses on the DEFAULT route.  rev 2.1: + SAB_TEXTPOS (N1);
# SAB_LAZY is now a sabotage ROW (N2), no longer a control.  Writes one log per run into
# $OUT and prints a verdict table.  PROTO = the rev-2 prototype binary.
set -u
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUT="${OUT:?}"; mkdir -p "$OUT"
FILES="$HERE/pd_arms.txt $HERE/pd_utf8.txt $HERE/pd_utf8i.txt $HERE/pd_ucp.txt $HERE/pd_i.txt"
AB="PROTO_ARM_A=1 PROTO_ARM_B=1"
run() {  # name, env, extra args...
    n="$1"; e="$2"; shift 2
    ARMS_ENV="$e" "$HERE/possdiff_exh.sh" "$@" > "$OUT/$n.log" 2>&1
    echo "$n	rc=$?	$(tail -1 "$OUT/$n.log")"
}
# shellcheck disable=SC2086
run arms "$AB" --reach "$HERE/pd_reach.tsv" $FILES
for pl in SAB_M0 SAB_FIRSTPOL SAB_MIXED SAB_NOFOLD SAB_FIRSTMEM SAB_NONNULL A1_NOCC SAB_LAZY SAB_TEXTPOS SAB_NORECGUARD; do
    # shellcheck disable=SC2086
    run "plant_$pl" "$AB PROTO_$pl=1" $FILES
done
printf '# features: all\n\\w++\\b\n(?>\\w+)\\b\nx(?>\\w+)\\b\n\\d++(?![\\d.])\n[a-z]++(?=@)\n(?>[a-z]+)(?=@)\n' > "$OUT/routeflip.txt"
ENGA=default run routeflip_default "$AB" "$OUT/routeflip.txt"
