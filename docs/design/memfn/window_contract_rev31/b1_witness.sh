#!/usr/bin/env bash
# wcfix: panel r4's B1 witness and M2's probe, reproduced on a pcrec binary.
# usage: b1_witness.sh PCREC SCRATCH     (writes fixtures under SCRATCH only)
set -u
P=$1; S=$2; mkdir -p "$S/L1" "$S/M2"
cat > "$S/L1/l1none.rxt" <<'RXT'
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
run() {
    out=$("$P" -p rx -e utf8 -I "$S/L1" --analysis l1none "$@" -o - 2>&1); rc=$?
    v=$(printf '%s\n' "$out" | grep -m1 -o '#define RX_FINDINGS .*\|counts nothing via [a-z0-9-]*')
    printf 'rc=%s\t%s\t%s\n' "$rc" "$*" "$v"
}
echo "== B1: -e utf8 -I L1 --analysis l1none"
run --pattern 'abc'
run --pattern 'caf.'
run --pattern '^abc' -fno-req-byte
run --pattern '^abc' -fno-req-byte -fno-req-run -fno-prefilter
run --pattern 'caf.' --engine=vm -fno-req-byte -fno-req-run
echo "== M2: a byte-identical user copy of the store's default.rxt"
cp "$(dirname "$0")/../../../../src/findings/default.rxt" "$S/M2/"
printf 'store default:  %s\n' "$("$P" -p rx --pattern abc -o - | grep -m1 'define RX_FINDINGS')"
printf 'user -I copy:   %s\n' "$("$P" -p rx -I "$S/M2" --analysis default --pattern abc -o - | grep -m1 'define RX_FINDINGS')"
"$P" --list-analysis default -I "$S/M2" | awk -F'\t' '/^#section chain/{s=1;print;next} /^#section/{s=0} s'
