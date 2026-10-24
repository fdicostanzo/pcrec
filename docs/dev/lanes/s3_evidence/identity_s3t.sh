#!/usr/bin/env bash
# docs/dev/lanes/s3_evidence/identity_s3t.sh -- lane s3 trailing checks, item 3(c): the four
# DD12a(i) strict-identity pairs (of 237) that differed in job 606 (`\b` twice, `\B`,
# `(?i)\bcat\b`), byte vs utf8, on BOTH main c3ea619c3's compiler and the S3 build, abi digits
# mapped back (84 -> 83). Prints per pattern: whether main's byte/utf8 diff equals the S3
# build's (a pre-existing pair), each S3-build hunk, and for the cover pattern the window
# statement token by token (split at `;`).
#     bash identity_s3t.sh MAIN_PCREC S3_PCREC OUTDIR
set -u
M=$1 N=$2 O=$3
mkdir -p "$O"
nrm() { sed 's/abi 84/abi 83/;s/!= 84/!= 83/;s/_ABI_H 84/_ABI_H 83/;s/\.abi = 84/.abi = 83/'; }
i=0
for P in '\b' '\B' '(?i)\bcat\b'; do
    i=$((i + 1))
    for b in main s3; do
        x=$M; [ "$b" = s3 ] && x=$N
        for e in byte utf8; do
            "$x" --features all -p rx -e "$e" -o - --pattern "$P" | nrm > "$O/p$i.$b.$e.c"
        done
        diff "$O/p$i.$b.byte.c" "$O/p$i.$b.utf8.c" > "$O/p$i.$b.diff"
    done
    same=no; cmp -s "$O/p$i.main.diff" "$O/p$i.s3.diff" && same=yes
    echo "== [$P] byte/utf8 diff: main $(wc -l < "$O/p$i.main.diff") lines, S3 $(wc -l < "$O/p$i.s3.diff") lines; identical on both compilers: $same; S3 hunks: $(grep -c '^[0-9]' "$O/p$i.s3.diff")"
    if [ "$same" = no ]; then
        cut -c1-200 "$O/p$i.s3.diff"
        echo "-- the window statement (scan_position = ({ ... })), byte vs utf8, split at ';':"
        grep '^    scan_position = ({' "$O/p$i.s3.byte.c" | tr ';' '\n' > "$O/p$i.wb"
        grep '^    scan_position = ({' "$O/p$i.s3.utf8.c" | tr ';' '\n' > "$O/p$i.wu"
        diff "$O/p$i.wb" "$O/p$i.wu"
        echo "-- stamps the window is held to:"; grep -h '^#define RX_REQ_RUN ' "$O/p$i.s3.byte.c" "$O/p$i.s3.utf8.c"
    fi
done
echo "== identity_s3t COMPLETE"
