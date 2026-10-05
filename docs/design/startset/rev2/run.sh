#!/usr/bin/env bash
# [START-SET] rev 2 reproductions (startset.md rev 2 §4.1a / §6.2).  From the
# repo root after `make`:  W=<scratch dir> docs/design/startset/rev2/run.sh
# Writes docs/design/startset/rev2/out/{witnesses.tsv,sweep.tsv,sweep_summary.txt,control.txt}.
# Needs gcc-16 and libpcre2-8 under $PCRE2 (default /opt/homebrew: LOCAL 10.48, not the 10.46 reference).
set -eu
R=docs/design/startset/rev2; C=docs/design/startset/census.tsv
export PCREC="$PWD/build/pcrec" W="${W:?scratch dir}"
mkdir -p "$W"
gcc-16 -O1 -std=gnu11 -Ilib -Isrc -o "$W/fs_plant" "$R/fs_probe_plant.c" build/libpcrec.a
# 1. the six witnesses at the critic's alphabets (ssc-sound F1's table)
w() { ALPHA="$1" MAXLEN=7 W="$W/wit" python3 "$R/sweep.py" "$C" "$W/wit_$2.tsv" "${@:3}"; }
mkdir -p "$W/wit"
w 61,7a,77,78    1 matrix.rxt:1064 matrix.rxt:2597
w 61,62,7a,77,78 2 matrix.rxt:1122 matrix.rxt:2662
w 61,62,63,64    3 lookbehind.rxt:212
w 61,62,0a,78    4 ctxnode.rxt:400
{ echo "# [START-SET] rev 2: the six r4 sound-F1 witnesses at the critic's alphabets, maxlen 7"; head -1 "$W/wit_1.tsv"; for i in 1 2 3 4; do tail -n +2 "$W/wit_$i.tsv"; done; } > "$R/out/witnesses.tsv"
# 2. the seeded-machine sweep (every seeded byte-class row; per-row alphabet)
mkdir -p "$W/sweep"; W="$W/sweep" python3 "$R/sweep.py" "$C" "$R/out/sweep.tsv"
python3 "$R/summarize.py" "$R/out/witnesses.tsv" "$R/out/sweep.tsv" > "$R/out/sweep_summary.txt"
# 3. the fact's control on every machine, with planted WALK defects
mkdir -p "$W/ctl"; FSPLANT="$W/fs_plant" W="$W/ctl" python3 "$R/control.py" "$C" "$R/out/control.txt"
# 4. the start-byte oracle on the VM hat (auto, then --engine=vm; the second is ~15 min on the M1)
mkdir -p "$W/vmo"; W="$W/vmo" python3 "$R/vmoracle.py" "$C" "$R/out/vmoracle_auto.tsv" auto | tee "$R/out/vmoracle_auto.txt"
mkdir -p "$W/vmo2"; W="$W/vmo2" python3 "$R/vmoracle.py" "$C" "$R/out/vmoracle_vm.tsv" vm | tee "$R/out/vmoracle_vm.txt"
