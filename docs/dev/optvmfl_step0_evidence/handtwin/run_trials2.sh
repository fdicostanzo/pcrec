#!/bin/bash
set -u
D=/tmp/claude-1001/-home-duxevents-pcrec/dcce9a31-e3ae-41e3-8913-a4a918af3f32/scratchpad/vmfl0/handtwin
B=/home/duxevents/pcrec-bench/bench/bounded
cd "$D"

run5() {
    local bin="$1" regime="$2" subj="$3" repeats="$4"
    for i in 1 2 3 4 5; do
        ld=$(uptime | grep -oP 'load average: \K[0-9.]+')
        out=$("./$bin" "$regime" "$subj" "$repeats")
        echo "$bin $regime $(basename "$subj") trial$i load=$ld $out"
    done
}

echo "== ctx findall ctx_large2 (5000) =="
run5 ctx-lazy-256_orig_time findall ctx_large2.bin 5000
run5 ctx-lazy-256_twin_time findall ctx_large2.bin 5000

echo "== nest2-64 match d-01024 (2000000) =="
run5 nest2-64_orig_time match "$B/subjects/d-01024.bin" 2000000
run5 nest2-64_twin_time match "$B/subjects/d-01024.bin" 2000000

echo "== nest2-64 findall t-digits-016k (100000) =="
run5 nest2-64_orig_time findall "$B/throughput/t-digits-016k.bin" 100000
run5 nest2-64_twin_time findall "$B/throughput/t-digits-016k.bin" 100000
