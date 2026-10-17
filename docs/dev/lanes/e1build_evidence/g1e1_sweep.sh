#!/usr/bin/env bash
# e1build G1-E1 (window_contract.md rev 3.1 §3.7.7): scripts/emit_sweep.py,
# every stream, REF (the branch point's build) against NEW (the E-1 tree),
# over the arm x analysis product: arms default / -fno-req-byte /
# -fno-req-byte -fno-req-run -fno-prefilter / --engine=vm -fno-req-byte
# -fno-req-run, each at byte and utf8 (`--engine=vm` alone is every run's own
# stream 2); analysis cells none / --analysis weblog / an -I measured user
# bundle `mine` / the `l1none` fixture (utf8 only: it serves utf8 only).
# The analysis cell rides --extra-base and the deny flags --extra, so both
# sides see base+extra on every stream; DIFFER is not this gate
# (--no-differ-floor), movers/asymmetric are.
# usage: g1e1_sweep.sh TREE REF_PCREC NEW_PCREC SCRATCH [JOBS]
set -u
T=$1; REF=$2; NEW=$3; S=$4; J=${5:-4}
mkdir -p "$S/fx"
sed 's/^analysis weblog$/analysis mine/' "$T/src/findings/weblog.rxt" > "$S/fx/mine.rxt"
cat > "$S/fx/l1none.rxt" <<'RXT'
analysis l1none
    cpfreq
        question q
        reader r
        analyzer authored
        encoding utf8
        serves byte-rate when utf8 via encode-latin1
        row U+20AC 7
        provenance
            source authored
            retrieved 2026-09-28
RXT
arms=("default|" "noreqbyte|-fno-req-byte"
      "noreq-pf|-fno-req-byte -fno-req-run -fno-prefilter"
      "noreq-vm|--engine=vm -fno-req-byte -fno-req-run")
cells=("none|" "weblog|--analysis weblog" "mine|-I $S/fx --analysis mine"
       "l1none|-I $S/fx --analysis l1none")
printf 'enc\tarm\tcell\trc\tstreams\tmovers\tasymmetric\n' > "$S/summary.tsv"
for enc in byte utf8; do
  for a in "${arms[@]}"; do
    an=${a%%|*}; af=${a#*|}
    for c in "${cells[@]}"; do
      cn=${c%%|*}; cf=${c#*|}
      [ "$cn" = l1none ] && [ "$enc" = byte ] && continue
      base="$cf"; [ "$enc" = utf8 ] && base="-e utf8 $cf"
      log="$S/es_${enc}_${an}_${cn}.log"
      args=(--ref-bin "$REF" --bin "$NEW" --no-self-check --jobs "$J"
            --out "$S/out_${enc}_${an}_${cn}" --extra-base="$base")
      [ -n "$af" ] && args+=(--extra="$af" --no-differ-floor)
      [ -z "$af" ] && [ -n "$base" ] && args+=(--extra="$base" --extra-base= --no-differ-floor)
      gnutimeout 1800 python3 "$T/scripts/emit_sweep.py" "${args[@]}" > "$log" 2>&1
      rc=$?
      st=$(grep -c '^  population=' "$log")
      mv=$(grep -o 'movers=[0-9]*' "$log" | awk -F= '{s+=$2} END{print s+0}')
      as=$(grep -o 'asymmetric=[0-9]*' "$log" | awk -F= '{s+=$2} END{print s+0}')
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$enc" "$an" "$cn" "$rc" "$st" "$mv" "$as" >> "$S/summary.tsv"
    done
  done
done
echo "== g1e1 sweep COMPLETE"
