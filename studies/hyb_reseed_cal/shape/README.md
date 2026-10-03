# Re-running the shape probes

SCRATCH TIER. Work in a scratch directory (never the repo, never /tmp on a
shared box); `$REPO` is the pcrec checkout, `$BENCH` a pcrec-bench checkout
(read only).

```sh
python3 $REPO/studies/hyb_reseed_cal/shape/regen_bench_subjects.py \
    $BENCH/bench/syntax .                      # -> subj/ (42), thr/ (3)
python3 $REPO/studies/hyb_reseed_cal/subjects.py cal   # lka_*, synth-*
cp $REPO/studies/hyb_reseed_cal/shape/{sdrv.c,rr.sh,mkbound.py,mkb3.py} .
# one cell: shipped (a) and deny (d)
P=$REPO/build/pcrec
$P -p rx --features all            -o possq.a.c --pattern 'a?+a'
$P -p rx --features all -fno-hyb-reseed -o possq.d.c --pattern 'a?+a'
for v in a d; do gcc-16 -O2 -include possq.$v.h -o possq.$v sdrv.c possq.$v.c; done
./rr.sh possq s 20000 subj/*.bin              # short search
./rr.sh possq f 20 thr/t-64k.bin thr/t-256k.bin   # find-all
# a form variant against the same deny:
python3 mkbound.py possq.a.c possq.f1.c f1
gcc-16 -O2 -include possq.a.h -o possq.xf1.a sdrv.c possq.f1.c; cp possq.d possq.xf1.d
./rr.sh possq.xf1 f 20 thr/t-64k.bin thr/t-256k.bin
```

The cells of `results/`: possq `a?+a`, lkapos `item(?= done)`, lkaneg
`item(?! done)`, lkaverb `item(*pla: done)`, lkanon `(?*item)item`, atalt
`(?>a|ab)c` (byte), lbvar `(?<=a|é)x` (`-e utf8`).

The counts table: add `n_att++`/`n_fail++`/`n_seed++` at the attempt, the
reset and the re-seed's prefilter call of a copy of the artifact, declare the
three counters, and link `cnt.c` (`./x.cnt s subj/*.bin`, `./x.cnt f FILE`).

On Linux pin every launch (`taskset -c N`) and read `xcall.md` §6 for the
alpha protocol; these Mac numbers are directional only.
