#!/bin/bash
# [OPT-VMFL] STEP 0 (b): 5 trials each, orig vs twin, match + findall regimes.
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

echo "== csv5 match f-csv-5 (20000000) =="
run5 csv5_orig_time match "$B/subjects/f-csv-5.bin" 20000000
run5 csv5_twin_time match "$B/subjects/f-csv-5.bin" 20000000

echo "== csv5 findall csv5_large (2000) =="
run5 csv5_orig_time findall csv5_large.bin 2000
run5 csv5_twin_time findall csv5_large.bin 2000

echo "== ctx match l-00 (5000000) =="
run5 ctx-lazy-256_orig_time match "$B/subjects/l-00.bin" 5000000
run5 ctx-lazy-256_twin_time match "$B/subjects/l-00.bin" 5000000

echo "== ctx match l-03 worst case (500000) =="
run5 ctx-lazy-256_orig_time match "$B/subjects/l-03.bin" 500000
run5 ctx-lazy-256_twin_time match "$B/subjects/l-03.bin" 500000

echo "== ctx findall ctx_large (500) =="
run5 ctx-lazy-256_orig_time findall ctx_large.bin 500
run5 ctx-lazy-256_twin_time findall ctx_large.bin 500

echo "== nest2-64 match d-01024 (2000000) =="
run5 nest2-64_orig_time match "$B/subjects/d-01024.bin" 2000000
run5 nest2-64_twin_time match "$B/subjects/d-01024.bin" 2000000

echo "== nest2-64 findall t-digits-016k (100000) =="
run5 nest2-64_orig_time findall "$B/throughput/t-digits-016k.bin" 100000
run5 nest2-64_twin_time findall "$B/throughput/t-digits-016k.bin" 100000
