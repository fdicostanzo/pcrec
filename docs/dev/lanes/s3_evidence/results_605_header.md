# job 588 (lane s3): D172 S3's acceptance, window_site.md rev 3.2 §6

- the bar: the SCALAR layer (`-fno-memfn-simd`, the default); the SIMD-on layer (`-fmemfn-simd`) REPORTED, each cell against SIMD-on DEF; the official SIMD verdict stays pcrec-bench's (D144 addendum 4)
- one compiler (the S3 build, pcrec 8d53dc29df1a); arms by flags (measure_588.sh header); gcc -O2, no -march, one pinned core (cpu 7, sibling 15), gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0
- L=5 launches, T=20000000 ns per sample, N=9 samples (job 581's calibration)
