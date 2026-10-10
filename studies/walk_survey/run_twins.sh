#!/bin/sh
# walk_survey: SCRATCH-TIER timing of the hand-twins that remove one class's
# walk, against today's artifact, answer-identity checked by span checksum.
#   PCREC=build/pcrec BENCHCOPY=build/ws/benchcopy [CPU=7] ./run_twins.sh > results/twin_timing.txt
# K4 landtwin.py (start = the skip loop's landing): \w+ , utf8 . , utf8 \p{L}+
# K3 landtwin.py --fixed (start = end - W): litrun lit-l4 (abcd)
# K5 the folded required-run gate (-fno-req-run-fold as the arm without it):
#    (?i)cat and (?i)error on match-dense lowercase text
# Each line: best of 5 (K5: 3) runs, 3 interleaved repeats.
set -e
cd "$(dirname "$0")"
H=$PWD; W=$H/work/twins; rm -rf "$W"; mkdir -p "$W"
P=${PCREC:?}; B=${BENCHCOPY:?}; CPU=${CPU:-7}
art() {  # id enc extra pattern
    mkdir -p "$W/$1"; "$P" -p rx -e "$2" --features all $3 -o "$W/$1/rx.c" --pattern "$4" 2>/dev/null
}
build() { gcc -O2 -I"$W/$1" fatime.c "$W/$1/$2" -o "$W/$1/$3"; }
art w byte "" '\w+';               python3 landtwin.py "$W/w/rx.c" "$W/w/twin.c"
art dot utf8 "" '.';                python3 landtwin.py "$W/dot/rx.c" "$W/dot/twin.c"
art pl utf8 "" '\p{L}+';            python3 landtwin.py "$W/pl/rx.c" "$W/pl/twin.c"
art l4 byte "" 'abcd';              python3 landtwin.py "$W/l4/rx.c" "$W/l4/twin.c" --fixed 4
for x in w dot pl l4; do build $x rx.c o; build $x twin.c t; done
art cat byte "" '(?i)cat'; art catnf byte -fno-req-run-fold '(?i)cat'
art err byte "" '(?i)error'; art errnf byte -fno-req-run-fold '(?i)error'
for x in cat catnf err errnf; do build $x rx.c o; done
python3 - "$W" <<'PY'
import random, sys
w = sys.argv[1]
open(w + "/cat1m", "wb").write((b"the cat sat on a mat. " * 50000)[:1 << 20])
r = random.Random(7); out = bytearray()
while len(out) < (1 << 20):
    out += b"2026-10-09 12:%02d:%02d host%d svc[%d]: " % (r.randrange(60), r.randrange(60), r.randrange(9), r.randrange(9999))
    out += (b"error: connection reset by peer\n" if r.random() < 0.2 else b"info: request served in %d ms\n" % r.randrange(999))
open(w + "/log1m", "wb").write(bytes(out[:1 << 20]))
PY
echo "# $(date -Is) $(uname -n) load1=$(cut -d' ' -f1 /proc/loadavg) cpu=$CPU gcc -O2; o = today's artifact, t = twin"
for rep in 1 2 3; do
  for v in o t; do
    echo "K4 \\w+     syntax/t-1m      $v $(taskset -c $CPU $W/w/$v $B/bench/syntax/throughput/t-1m.bin findall 5 | cut -f3-)"
    echo "K4 . utf8   utf8/t-1m        $v $(taskset -c $CPU $W/dot/$v $B/bench/utf8/throughput/t-1m.bin findall 5 | cut -f3-)"
    echo "K4 \\p{L}+  utf8/t-1m        $v $(taskset -c $CPU $W/pl/$v $B/bench/utf8/throughput/t-1m.bin findall 5 | cut -f3-)"
    echo "K3 abcd     litrun/mat-l4    $v $(taskset -c $CPU $W/l4/$v $B/bench/litrun/throughput/mat-l4.bin findall 5 | cut -f3-)"
  done
  echo "K5 (?i)cat   syntax/t-1m      fold   $(taskset -c $CPU $W/cat/o $B/bench/syntax/throughput/t-1m.bin findall 3 | cut -f3-)"
  echo "K5 (?i)cat   syntax/t-1m      nofold $(taskset -c $CPU $W/catnf/o $B/bench/syntax/throughput/t-1m.bin findall 3 | cut -f3-)"
  echo "K5 (?i)cat   lowercase 1 MiB  fold   $(taskset -c $CPU $W/cat/o $W/cat1m findall 3 | cut -f3-)"
  echo "K5 (?i)cat   lowercase 1 MiB  nofold $(taskset -c $CPU $W/catnf/o $W/cat1m findall 3 | cut -f3-)"
  echo "K5 (?i)error lowercase log    fold   $(taskset -c $CPU $W/err/o $W/log1m findall 3 | cut -f3-)"
  echo "K5 (?i)error lowercase log    nofold $(taskset -c $CPU $W/errnf/o $W/log1m findall 3 | cut -f3-)"
done
echo "== walk_survey run_twins COMPLETE"
