# job 588 (lane s3): D172 S3's acceptance, window_site.md rev 3.2 §6

- the bar: the SCALAR layer (`-fno-memfn-simd`, the default); the SIMD-on layer (`-fmemfn-simd`) REPORTED, each cell against SIMD-on DEF; the official SIMD verdict stays pcrec-bench's (D144 addendum 4)
- one compiler (the S3 build, pcrec 8d53dc29df1a); arms by flags (measure_588.sh header); gcc -O2, no -march, one pinned core (cpu 7, sibling 15), gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0
- L=5 launches, T=20000000 ns per sample, N=9 samples (job 581's calibration)

## Table: the bar (SCALAR) and the SIMD-on reading

| cell | regime | class | DEF ns/pass | RTE/DEF | floor(581) | cap | verdict | RT2/RTE (A/A) | RTEs/DEFs (SIMD-on) | SIMD-on reading | G1 wf-find (RTE/DEF) | G1 wf-find SIMD (RTEs/DEFs) | G1 wf-hors (RTE/NOH) | G1 wf-hors SIMD (RTEs/NOHs) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lit-l8 | throughput | real | 65685 | 0.952 | 0.020 |  | PASS | 0.999 | 0.951 | within | 0.952 | 0.951 | same text | same text |
| lit-l8 | throughput | none | 62062 | 0.995 | 0.020 |  | PASS | 1.003 | 0.991 | within | 0.995 | 0.991 | same text | same text |
| lit-l8 | throughput | dense | 1867544 | 0.267 | 0.020 |  | PASS | 1.001 | 0.267 | within | 0.267 | 0.267 | same text | same text |
| lit-l8 | search_short | real | 9260 | 0.838 | 0.020 |  | PASS | 1.000 | 0.856 | within | 0.838 | 0.856 | same text | same text |
| lit-l8 | search_short | none | 8426 | 0.980 | 0.020 |  | PASS | 0.999 | 0.961 | within | 0.980 | 0.961 | same text | same text |
| lit-l8 | search_short | dense | 11756 | 0.268 | 0.020 |  | PASS | 0.970 | 0.269 | within | 0.268 | 0.269 | same text | same text |
| lit-l8 | match | real | 3290 | 1.002 | 0.020 |  | PASS | 1.000 | 1.003 | within | 1.002 | 1.003 | same text | same text |
| lit-l8 | match | none | 2195 | 1.011 | 0.020 |  | PASS | 0.999 | 1.009 | within | 1.011 | 1.009 | same text | same text |
| lit-l8 | match | dense | 7196 | 1.017 | 0.020 |  | PASS | 0.989 | 1.004 | within | 1.017 | 1.004 | same text | same text |
| year4 | throughput | real | 542612 | 0.870 | 0.020 |  | PASS | 1.000 | 0.867 | within | 0.870 | 0.867 | same text | same text |
| year4 | throughput | none | 410255 | 0.911 | 0.020 |  | PASS | 0.997 | 0.912 | within | 0.911 | 0.912 | same text | same text |
| year4 | throughput | dense | 1599100 | 0.669 | 0.020 |  | PASS | 1.002 | 0.672 | within | 0.669 | 0.672 | same text | same text |
| year4 | search_short | real | 16131 | 0.910 | 0.035 |  | PASS | 1.000 | 0.899 | within | 0.910 | 0.899 | same text | same text |
| year4 | search_short | none | 27301 | 0.959 | 0.050 |  | PASS | 1.011 | 0.949 | within | 0.959 | 0.949 | same text | same text |
| year4 | search_short | dense | 5095 | 0.478 | 0.027 |  | PASS | 0.975 | 0.465 | within | 0.478 | 0.465 | same text | same text |
| year4 | match | real | 2095 | 1.000 | 0.020 |  | PASS | 1.001 | 1.001 | within | 1.000 | 1.001 | same text | same text |
| year4 | match | none | 1650 | 1.001 | 0.020 |  | PASS | 1.000 | 1.000 | within | 1.001 | 1.000 | same text | same text |
| year4 | match | dense | 2975 | 0.998 | 0.020 |  | PASS | 1.000 | 1.000 | within | 0.998 | 1.000 | same text | same text |
| file-ext-order | throughput | real | 206829 | 0.921 | 0.020 |  | PASS | 1.005 | 0.921 | within | 0.921 | 0.921 | same text | same text |
| file-ext-order | throughput | none | 180756 | 1.003 | 0.020 |  | PASS | 1.001 | 1.004 | within | 1.003 | 1.004 | same text | same text |
| file-ext-order | throughput | dense | 778410 | 0.519 | 0.020 |  | PASS | 0.999 | 0.518 | within | 0.519 | 0.518 | same text | same text |
| file-ext-order | search_short | real | 13850 | 0.803 | 0.020 |  | PASS | 1.000 | 0.803 | within | 0.803 | 0.803 | same text | same text |
| file-ext-order | search_short | none | 12998 | 1.032 | 0.020 | 1.053 | PASS | 1.000 | 1.031 | within | 1.032 | 1.031 | same text | same text |
| file-ext-order | search_short | dense | 13530 | 0.242 | 0.020 |  | PASS | 1.002 | 0.229 | within | 0.242 | 0.229 | same text | same text |
| file-ext-order | match | real | 2595 | 1.050 | 0.020 | 1.059 | PASS | 0.999 | 1.034 | within | 1.050 | 1.034 | same text | same text |
| file-ext-order | match | none | 2236 | 1.067 | 0.020 | 1.085 | PASS | 1.000 | 1.066 | within | 1.067 | 1.066 | same text | same text |
| file-ext-order | match | dense | 4130 | 1.001 | 0.020 |  | PASS | 0.998 | 0.998 | within | 1.001 | 0.998 | same text | same text |
| hex8-bounded | throughput | real | 2504144 | 0.398 | 0.020 |  | PASS | 1.000 | 0.397 | within | 0.398 | 0.397 | 0.466 | 0.466 |
| hex8-bounded | throughput | none | 2391736 | 0.396 | 0.020 |  | PASS | 0.998 | 0.394 | within | 0.396 | 0.394 | 0.440 | 0.439 |
| hex8-bounded | throughput | dense | 1514549 | 1.543 | 0.020 | 1.551 | PASS | 0.994 | 1.538 | within | 1.543 | 1.538 | 1.122 | 1.129 |
| hex8-bounded | search_short | real | 38295 | 0.525 | 0.020 |  | PASS | 1.000 | 0.526 | within | 0.525 | 0.526 | 0.416 | 0.417 |
| hex8-bounded | search_short | none | 168032 | 0.173 | 0.023 |  | PASS | 1.000 | 0.172 | within | 0.173 | 0.172 | 0.164 | 0.164 |
| hex8-bounded | search_short | dense | 10469 | 0.962 | 0.020 | 1.159 | PASS | 1.009 | 0.959 | within | 0.962 | 0.959 | 1.054 | 1.053 |
| hex8-bounded | match | real | 3939 | 1.002 | 0.020 |  | PASS | 1.002 | 0.993 | within | 1.002 | 0.993 | 0.997 | 1.000 |
| hex8-bounded | match | none | 2922 | 1.001 | 0.020 |  | PASS | 0.999 | 0.998 | within | 1.001 | 0.998 | 0.997 | 0.998 |
| hex8-bounded | match | dense | 7109 | 0.999 | 0.020 |  | PASS | 1.003 | 0.997 | within | 0.999 | 0.997 | 1.002 | 1.000 |
| foobar | throughput | real | 67903 | 0.960 | 0.020 |  | PASS | 0.996 | 0.961 | within | 0.960 | 0.961 | same text | same text |
| foobar | throughput | none | 64639 | 1.013 | 0.020 |  | PASS | 0.995 | 1.004 | within | 1.013 | 1.004 | same text | same text |
| foobar | throughput | dense | 2062373 | 0.308 | 0.020 |  | PASS | 1.000 | 0.308 | within | 0.308 | 0.308 | same text | same text |
| foobar | search_short | real | 8147 | 0.891 | 0.020 |  | PASS | 0.998 | 0.889 | within | 0.891 | 0.889 | same text | same text |
| foobar | search_short | none | 8405 | 0.977 | 0.020 |  | PASS | 1.000 | 0.976 | within | 0.977 | 0.976 | same text | same text |
| foobar | search_short | dense | 9958 | 0.299 | 0.020 |  | PASS | 0.999 | 0.299 | within | 0.299 | 0.299 | same text | same text |
| foobar | match | real | 2836 | 1.032 | 0.020 |  | FAIL | 1.001 | 1.033 | SLOWER | 1.032 | 1.033 | same text | same text |
| foobar | match | none | 2439 | 1.000 | 0.020 |  | PASS | 0.999 | 1.000 | within | 1.000 | 1.000 | same text | same text |
| foobar | match | dense | 4576 | 1.006 | 0.020 |  | PASS | 0.996 | 0.997 | within | 1.006 | 0.997 | same text | same text |
| cat-bounded | throughput | real | 436417 | 0.690 | 0.020 |  | PASS | 1.002 | 0.693 | within | 0.690 | 0.693 | same text | same text |
| cat-bounded | throughput | none | 471636 | 0.589 | 0.020 |  | PASS | 1.009 | 0.588 | within | 0.589 | 0.588 | same text | same text |
| cat-bounded | throughput | dense | 3551143 | 0.293 | 0.020 |  | PASS | 1.000 | 0.292 | within | 0.293 | 0.292 | same text | same text |
| cat-bounded | search_short | real | 14281 | 0.716 | 0.020 |  | PASS | 0.997 | 0.714 | within | 0.716 | 0.714 | same text | same text |
| cat-bounded | search_short | none | 18784 | 0.713 | 0.020 |  | PASS | 0.999 | 0.717 | within | 0.713 | 0.717 | same text | same text |
| cat-bounded | search_short | dense | 9529 | 0.393 | 0.020 |  | PASS | 1.001 | 0.393 | within | 0.393 | 0.393 | same text | same text |
| cat-bounded | match | real | 2938 | 1.001 | 0.020 |  | PASS | 1.000 | 1.000 | within | 1.001 | 1.000 | same text | same text |
| cat-bounded | match | none | 2605 | 1.000 | 0.020 |  | PASS | 0.999 | 1.000 | within | 1.000 | 1.000 | same text | same text |
| cat-bounded | match | dense | 3969 | 0.976 | 0.025 |  | PASS | 0.992 | 0.968 | within | 0.976 | 0.968 | same text | same text |
| done-eol | throughput | real | 641169 | 0.685 | 0.020 |  | PASS | 1.005 | 0.685 | within | 0.685 | 0.685 | same text | same text |
| done-eol | throughput | none | 586349 | 0.670 | 0.020 |  | PASS | 0.999 | 0.669 | within | 0.670 | 0.669 | same text | same text |
| done-eol | throughput | dense | 1116773 | 0.326 | 0.020 |  | PASS | 0.987 | 0.326 | within | 0.326 | 0.326 | same text | same text |
| done-eol | search_short | real | 25243 | 0.571 | 0.046 |  | PASS | 0.999 | 0.571 | within | 0.571 | 0.571 | same text | same text |
| done-eol | search_short | none | 34718 | 0.597 | 0.020 |  | PASS | 0.978 | 0.586 | within | 0.597 | 0.586 | same text | same text |
| done-eol | search_short | dense | 11260 | 0.275 | 0.049 |  | PASS | 1.001 | 0.275 | within | 0.275 | 0.275 | same text | same text |
| done-eol | match | real | 2973 | 1.003 | 0.020 |  | PASS | 1.006 | 1.006 | within | 1.003 | 1.006 | same text | same text |
| done-eol | match | none | 2451 | 1.000 | 0.020 |  | PASS | 0.999 | 1.000 | within | 1.000 | 1.000 | same text | same text |
| done-eol | match | dense | 4351 | 0.994 | 0.030 |  | PASS | 1.039 | 1.026 | within | 0.994 | 1.026 | same text | same text |
| word-digit | throughput | real | 2324618 | 0.274 | 0.020 |  | PASS | 1.000 | 0.274 | within | 0.274 | 0.274 | same text | same text |
| word-digit | throughput | none | 2277232 | 0.256 | 0.020 |  | PASS | 1.000 | 0.256 | within | 0.256 | 0.256 | same text | same text |
| word-digit | throughput | dense | 2676728 | 0.655 | 0.020 |  | PASS | 0.980 | 0.629 | within | 0.655 | 0.629 | same text | same text |
| word-digit | search_short | real | 86941 | 0.361 | 0.020 |  | PASS | 1.000 | 0.364 | within | 0.361 | 0.364 | same text | same text |
| word-digit | search_short | none | 189039 | 0.307 | 0.020 |  | PASS | 0.999 | 0.307 | within | 0.307 | 0.307 | same text | same text |
| word-digit | search_short | dense | 4294 | 0.441 | 0.020 |  | PASS | 0.998 | 0.440 | within | 0.441 | 0.440 | same text | same text |
| word-digit | match | real | 2646 | 0.985 | 0.020 |  | PASS | 0.998 | 0.981 | within | 0.985 | 0.981 | same text | same text |
| word-digit | match | none | 2527 | 0.984 | 0.020 |  | PASS | 1.000 | 0.985 | within | 0.984 | 0.985 | same text | same text |
| word-digit | match | dense | 2972 | 0.997 | 0.020 |  | PASS | 1.001 | 1.001 | within | 0.997 | 1.001 | same text | same text |

## The five named cells (§6), each capped at 581's ratio plus its floor

- hex8-bounded throughput/dense: RTE/DEF 1.543, cap 1.551: within
- hex8-bounded search_short/dense: RTE/DEF 0.962, cap 1.159: within
- file-ext-order search_short/none: RTE/DEF 1.032, cap 1.053: within
- file-ext-order match/real: RTE/DEF 1.050, cap 1.059: within
- file-ext-order match/none: RTE/DEF 1.067, cap 1.085: within

## G1 alpha summary (pcrec's timing vs its own deny; < 1: the row is faster)

- wf-find, scalar: 72 cells, geometric mean 0.686, min 0.173, max 1.543
- wf-find, SIMD-on: 72 cells, geometric mean 0.684, min 0.172, max 1.538
- wf-hors, scalar: 9 cells, geometric mean 0.634, min 0.164, max 1.122
- wf-hors, SIMD-on: 9 cells, geometric mean 0.634, min 0.164, max 1.129

## Mover sample (not the §6 bar)

Other cover movers (sample_588.tsv, pick_588.py's stratified pick), each DEF vs routed at both layers; floor = this run's A/A in the regime; FINDINGS for the manager, never the bar.

| row | stratum | pattern | regime | class | DEF ns/pass | RTE/DEF | floor | reading | RTEs/DEFs (SIMD) | SIMD reading |
|---|---|---|---|---|---|---|---|---|---|---|
| smp01 | LIBC/one/norun | `\\\|` | throughput | real | 16038 | 0.764 | 0.020 | within | 0.764 | within |
| smp01 | LIBC/one/norun | `\\\|` | throughput | none | 7547 | 0.996 | 0.020 | within | 0.996 | within |
| smp01 | LIBC/one/norun | `\\\|` | throughput | random | 96366 | 0.630 | 0.020 | within | 0.630 | within |
| smp01 | LIBC/one/norun | `\\\|` | search_short | real | 5023 | 0.866 | 0.030 | within | 0.866 | within |
| smp01 | LIBC/one/norun | `\\\|` | search_short | none | 4649 | 0.952 | 0.030 | within | 0.952 | within |
| smp01 | LIBC/one/norun | `\\\|` | search_short | random | 5350 | 0.829 | 0.030 | within | 0.829 | within |
| smp02 | LIBC/one/run | `ABCDEFGH` | throughput | real | 23942 | 0.537 | 0.020 | within | 0.537 | within |
| smp02 | LIBC/one/run | `ABCDEFGH` | throughput | none | 7486 | 1.001 | 0.020 | within | 1.001 | within |
| smp02 | LIBC/one/run | `ABCDEFGH` | throughput | random | 48184 | 0.994 | 0.020 | within | 0.994 | within |
| smp02 | LIBC/one/run | `ABCDEFGH` | search_short | real | 6237 | 0.736 | 0.030 | within | 0.736 | within |
| smp02 | LIBC/one/run | `ABCDEFGH` | search_short | none | 4660 | 1.000 | 0.030 | within | 1.000 | within |
| smp02 | LIBC/one/run | `ABCDEFGH` | search_short | random | 7665 | 0.971 | 0.030 | within | 0.971 | within |
| smp03 | WALK/hors/norun | `[^abc]{2,4}?` | throughput | real | 2417625 | 0.689 | 0.020 | within | 0.689 | within |
| smp03 | WALK/hors/norun | `[^abc]{2,4}?` | throughput | random | 2280637 | 0.676 | 0.020 | within | 0.676 | within |
| smp03 | WALK/hors/norun | `[^abc]{2,4}?` | search_short | real | 3475 | 0.551 | 0.030 | within | 0.551 | within |
| smp03 | WALK/hors/norun | `[^abc]{2,4}?` | search_short | random | 3447 | 0.533 | 0.030 | within | 0.533 | within |
| smp04 | WALK/one/norun | `[a[:b]` | throughput | real | 842764 | 0.836 | 0.020 | within | 0.836 | within |
| smp04 | WALK/one/norun | `[a[:b]` | throughput | random | 600050 | 4.464 | 0.020 | SLOWER | 4.464 | SLOWER |
| smp04 | WALK/one/norun | `[a[:b]` | search_short | real | 5048 | 0.806 | 0.030 | within | 0.806 | within |
| smp04 | WALK/one/norun | `[a[:b]` | search_short | random | 7354 | 1.951 | 0.030 | SLOWER | 1.951 | SLOWER |
| smp05 | WALK/one/run | `(?:(?i:abs)\|(?i:ab)S)` | throughput | real | 3429799 | 0.106 | 0.020 | within | 9.547 | SLOWER |
| smp05 | WALK/one/run | `(?:(?i:abs)\|(?i:ab)S)` | throughput | none | 70412 | 4.908 | 0.020 | SLOWER | 11.843 | SLOWER |
| smp05 | WALK/one/run | `(?:(?i:abs)\|(?i:ab)S)` | throughput | random | 184675 | 2.268 | 0.020 | SLOWER | 12.290 | SLOWER |
| smp05 | WALK/one/run | `(?:(?i:abs)\|(?i:ab)S)` | search_short | real | 11074 | 1.653 | 0.030 | SLOWER | 2.916 | SLOWER |
| smp05 | WALK/one/run | `(?:(?i:abs)\|(?i:ab)S)` | search_short | none | 11107 | 2.292 | 0.030 | SLOWER | 4.007 | SLOWER |
| smp05 | WALK/one/run | `(?:(?i:abs)\|(?i:ab)S)` | search_short | random | 14658 | 1.934 | 0.030 | SLOWER | 4.078 | SLOWER |
| smp06 | LIBC/one/norun | `z(?!a)` | throughput | real | 16091 | 0.792 | 0.020 | within | 0.792 | within |
| smp06 | LIBC/one/norun | `z(?!a)` | throughput | none | 7616 | 0.993 | 0.020 | within | 0.993 | within |
| smp06 | LIBC/one/norun | `z(?!a)` | throughput | random | 95659 | 0.673 | 0.020 | within | 0.673 | within |
| smp06 | LIBC/one/norun | `z(?!a)` | search_short | real | 5090 | 0.859 | 0.030 | within | 0.859 | within |
| smp06 | LIBC/one/norun | `z(?!a)` | search_short | none | 4706 | 0.896 | 0.030 | within | 0.896 | within |
| smp06 | LIBC/one/norun | `z(?!a)` | search_short | random | 5286 | 0.864 | 0.030 | within | 0.864 | within |
| smp07 | LIBC/one/run | `z(?:ab){3,}?` | throughput | real | 41672 | 0.301 | 0.020 | within | 0.301 | within |
| smp07 | LIBC/one/run | `z(?:ab){3,}?` | throughput | none | 7482 | 1.008 | 0.020 | within | 1.008 | within |
| smp07 | LIBC/one/run | `z(?:ab){3,}?` | throughput | random | 50298 | 0.923 | 0.020 | within | 0.923 | within |
| smp07 | LIBC/one/run | `z(?:ab){3,}?` | search_short | real | 9906 | 0.447 | 0.030 | within | 0.447 | within |
| smp07 | LIBC/one/run | `z(?:ab){3,}?` | search_short | none | 4436 | 0.953 | 0.030 | within | 0.953 | within |
| smp07 | LIBC/one/run | `z(?:ab){3,}?` | search_short | random | 8380 | 0.875 | 0.030 | within | 0.875 | within |
| smp08 | WALK/hors/norun | `\\b\\w*?\\B\\w` | throughput | real | 2473017 | 0.860 | 0.020 | within | 0.860 | within |
| smp08 | WALK/hors/norun | `\\b\\w*?\\B\\w` | throughput | random | 3405487 | 1.139 | 0.020 | SLOWER | 1.139 | SLOWER |
| smp08 | WALK/hors/norun | `\\b\\w*?\\B\\w` | search_short | real | 4599 | 0.535 | 0.030 | within | 0.535 | within |
| smp08 | WALK/hors/norun | `\\b\\w*?\\B\\w` | search_short | random | 5730 | 0.665 | 0.030 | within | 0.665 | within |
| smp09 | WALK/one/norun | `(?:(?!a)z\|w)` | throughput | real | 487653 | 1.157 | 0.020 | SLOWER | 1.157 | SLOWER |
| smp09 | WALK/one/norun | `(?:(?!a)z\|w)` | throughput | random | 395703 | 1.317 | 0.020 | SLOWER | 1.317 | SLOWER |
| smp09 | WALK/one/norun | `(?:(?!a)z\|w)` | search_short | real | 8586 | 1.253 | 0.030 | SLOWER | 1.253 | SLOWER |
| smp09 | WALK/one/norun | `(?:(?!a)z\|w)` | search_short | random | 12090 | 1.413 | 0.030 | SLOWER | 1.413 | SLOWER |
| smp10 | WALK/one/run | `(?i)foobar` | throughput | real | 3724515 | 0.149 | 0.020 | within | 12.784 | SLOWER |
| smp10 | WALK/one/run | `(?i)foobar` | throughput | none | 74928 | 7.352 | 0.020 | SLOWER | 18.215 | SLOWER |
| smp10 | WALK/one/run | `(?i)foobar` | throughput | random | 182135 | 3.276 | 0.020 | SLOWER | 17.643 | SLOWER |
| smp10 | WALK/one/run | `(?i)foobar` | search_short | real | 11743 | 2.567 | 0.030 | SLOWER | 4.430 | SLOWER |
| smp10 | WALK/one/run | `(?i)foobar` | search_short | none | 11234 | 3.936 | 0.030 | SLOWER | 7.277 | SLOWER |
| smp10 | WALK/one/run | `(?i)foobar` | search_short | random | 14306 | 3.201 | 0.030 | SLOWER | 6.998 | SLOWER |
| smp11 | LIBC/one/norun | `(?x)a#` | throughput | real | 575395 | 0.562 | 0.020 | within | 0.562 | within |
| smp11 | LIBC/one/norun | `(?x)a#` | throughput | random | 94908 | 0.602 | 0.020 | within | 0.602 | within |
| smp11 | LIBC/one/norun | `(?x)a#` | search_short | real | 4772 | 0.716 | 0.030 | within | 0.716 | within |
| smp11 | LIBC/one/norun | `(?x)a#` | search_short | random | 5237 | 0.832 | 0.030 | within | 0.832 | within |
| smp12 | LIBC/one/run | `.{3}cat` | throughput | real | 87769 | 0.880 | 0.020 | within | 0.880 | within |
| smp12 | LIBC/one/run | `.{3}cat` | throughput | none | 71338 | 1.016 | 0.020 | within | 1.016 | within |
| smp12 | LIBC/one/run | `.{3}cat` | throughput | random | 49315 | 1.017 | 0.020 | within | 1.017 | within |
| smp12 | LIBC/one/run | `.{3}cat` | search_short | real | 9108 | 0.892 | 0.030 | within | 0.892 | within |
| smp12 | LIBC/one/run | `.{3}cat` | search_short | none | 9332 | 0.983 | 0.030 | within | 0.983 | within |
| smp12 | LIBC/one/run | `.{3}cat` | search_short | random | 7557 | 0.995 | 0.030 | within | 0.995 | within |
| smp13 | WALK/hors/norun | `...` | throughput | real | 1527216 | 0.632 | 0.020 | within | 0.632 | within |
| smp13 | WALK/hors/norun | `...` | throughput | random | 1436615 | 0.667 | 0.020 | within | 0.667 | within |
| smp13 | WALK/hors/norun | `...` | search_short | real | 3533 | 0.431 | 0.030 | within | 0.431 | within |
| smp13 | WALK/hors/norun | `...` | search_short | random | 3495 | 0.417 | 0.030 | within | 0.417 | within |
| smp14 | WALK/one/norun | `[a-]` | throughput | real | 749744 | 1.017 | 0.020 | within | 1.017 | within |
| smp14 | WALK/one/norun | `[a-]` | throughput | random | 428316 | 1.216 | 0.020 | SLOWER | 1.216 | SLOWER |
| smp14 | WALK/one/norun | `[a-]` | search_short | real | 5507 | 1.244 | 0.030 | SLOWER | 1.244 | SLOWER |
| smp14 | WALK/one/norun | `[a-]` | search_short | random | 10649 | 1.611 | 0.030 | SLOWER | 1.611 | SLOWER |
| smp15 | WALK/one/run | `(?i)abc` | throughput | real | 3642379 | 0.105 | 0.020 | within | 9.907 | SLOWER |
| smp15 | WALK/one/run | `(?i)abc` | throughput | none | 71358 | 5.127 | 0.020 | SLOWER | 12.492 | SLOWER |
| smp15 | WALK/one/run | `(?i)abc` | throughput | random | 179968 | 2.319 | 0.020 | SLOWER | 12.302 | SLOWER |
| smp15 | WALK/one/run | `(?i)abc` | search_short | real | 11006 | 1.711 | 0.030 | SLOWER | 2.990 | SLOWER |
| smp15 | WALK/one/run | `(?i)abc` | search_short | none | 11167 | 2.372 | 0.030 | SLOWER | 4.172 | SLOWER |
| smp15 | WALK/one/run | `(?i)abc` | search_short | random | 14175 | 1.905 | 0.030 | SLOWER | 3.883 | SLOWER |
| smp16 | LIBC/one/norun | `(?<!a)c` | throughput | real | 225376 | 0.652 | 0.020 | within | 0.652 | within |
| smp16 | LIBC/one/norun | `(?<!a)c` | throughput | random | 109464 | 0.579 | 0.020 | within | 0.579 | within |
| smp16 | LIBC/one/norun | `(?<!a)c` | search_short | real | 6119 | 0.802 | 0.030 | within | 0.802 | within |
| smp16 | LIBC/one/norun | `(?<!a)c` | search_short | random | 5974 | 0.783 | 0.030 | within | 0.783 | within |
| smp17 | LIBC/one/run | `a{ , }` | throughput | real | 24344 | 0.526 | 0.020 | within | 0.526 | within |
| smp17 | LIBC/one/run | `a{ , }` | throughput | none | 7583 | 0.999 | 0.020 | within | 0.999 | within |
| smp17 | LIBC/one/run | `a{ , }` | throughput | random | 48511 | 1.009 | 0.020 | within | 1.009 | within |
| smp17 | LIBC/one/run | `a{ , }` | search_short | real | 5837 | 0.691 | 0.030 | within | 0.691 | within |
| smp17 | LIBC/one/run | `a{ , }` | search_short | none | 4068 | 1.003 | 0.030 | within | 1.003 | within |
| smp17 | LIBC/one/run | `a{ , }` | search_short | random | 6884 | 1.028 | 0.030 | within | 1.028 | within |
| smp18 | WALK/hors/norun | `..` | throughput | real | 1847718 | 0.861 | 0.020 | within | 0.861 | within |
| smp18 | WALK/hors/norun | `..` | throughput | random | 1831850 | 0.818 | 0.020 | within | 0.818 | within |
| smp18 | WALK/hors/norun | `..` | search_short | real | 2836 | 0.635 | 0.030 | within | 0.635 | within |
| smp18 | WALK/hors/norun | `..` | search_short | random | 2825 | 0.568 | 0.030 | within | 0.568 | within |
| smp19 | WALK/one/norun | `[[:]` | throughput | real | 210270 | 1.891 | 0.020 | SLOWER | 1.891 | SLOWER |
| smp19 | WALK/one/norun | `[[:]` | throughput | none | 201337 | 1.461 | 0.020 | SLOWER | 1.461 | SLOWER |
| smp19 | WALK/one/norun | `[[:]` | throughput | random | 416404 | 1.251 | 0.020 | SLOWER | 1.251 | SLOWER |
| smp19 | WALK/one/norun | `[[:]` | search_short | real | 18849 | 1.659 | 0.030 | SLOWER | 1.659 | SLOWER |
| smp19 | WALK/one/norun | `[[:]` | search_short | none | 22606 | 1.346 | 0.030 | SLOWER | 1.346 | SLOWER |
| smp19 | WALK/one/norun | `[[:]` | search_short | random | 10239 | 1.626 | 0.030 | SLOWER | 1.626 | SLOWER |
| smp20 | WALK/one/run | `(?i)x/1234` | throughput | real | 22252 | 10.263 | 0.020 | SLOWER | 10.263 | SLOWER |
| smp20 | WALK/one/run | `(?i)x/1234` | throughput | none | 7565 | 29.071 | 0.020 | SLOWER | 29.071 | SLOWER |
| smp20 | WALK/one/run | `(?i)x/1234` | throughput | random | 46863 | 8.913 | 0.020 | SLOWER | 8.913 | SLOWER |
| smp20 | WALK/one/run | `(?i)x/1234` | search_short | real | 5708 | 3.160 | 0.030 | SLOWER | 3.160 | SLOWER |
| smp20 | WALK/one/run | `(?i)x/1234` | search_short | none | 4442 | 5.933 | 0.030 | SLOWER | 5.933 | SLOWER |
| smp20 | WALK/one/run | `(?i)x/1234` | search_short | random | 7527 | 3.673 | 0.030 | SLOWER | 3.673 | SLOWER |
| smp21 | LIBC/one/norun | `:` | throughput | real | 16055 | 0.773 | 0.020 | within | 0.773 | within |
| smp21 | LIBC/one/norun | `:` | throughput | none | 7549 | 1.002 | 0.020 | within | 1.002 | within |
| smp21 | LIBC/one/norun | `:` | throughput | random | 95996 | 0.630 | 0.020 | within | 0.630 | within |
| smp21 | LIBC/one/norun | `:` | search_short | real | 5309 | 0.846 | 0.030 | within | 0.846 | within |
| smp21 | LIBC/one/norun | `:` | search_short | none | 4616 | 0.949 | 0.030 | within | 0.949 | within |
| smp21 | LIBC/one/norun | `:` | search_short | random | 5432 | 0.803 | 0.030 | within | 0.803 | within |
| smp22 | LIBC/one/run | `a{2,2}c` | throughput | real | 81874 | 0.927 | 0.020 | within | 0.927 | within |
| smp22 | LIBC/one/run | `a{2,2}c` | throughput | none | 72140 | 0.987 | 0.020 | within | 0.987 | within |
| smp22 | LIBC/one/run | `a{2,2}c` | throughput | random | 48688 | 0.991 | 0.020 | within | 0.991 | within |
| smp22 | LIBC/one/run | `a{2,2}c` | search_short | real | 8014 | 0.927 | 0.030 | within | 0.927 | within |
| smp22 | LIBC/one/run | `a{2,2}c` | search_short | none | 8703 | 0.972 | 0.030 | within | 0.972 | within |
| smp22 | LIBC/one/run | `a{2,2}c` | search_short | random | 7515 | 0.972 | 0.030 | within | 0.972 | within |
| smp23 | WALK/hors/norun | `\\w\\B\\w` | throughput | real | 2907755 | 0.634 | 0.020 | within | 0.634 | within |
| smp23 | WALK/hors/norun | `\\w\\B\\w` | throughput | random | 3485801 | 0.859 | 0.020 | within | 0.859 | within |
| smp23 | WALK/hors/norun | `\\w\\B\\w` | search_short | real | 4214 | 0.540 | 0.030 | within | 0.540 | within |
| smp23 | WALK/hors/norun | `\\w\\B\\w` | search_short | random | 5219 | 0.668 | 0.030 | within | 0.668 | within |
| smp24 | WALK/one/norun | `[:a]` | throughput | real | 754284 | 0.994 | 0.020 | within | 0.994 | within |
| smp24 | WALK/one/norun | `[:a]` | throughput | random | 416950 | 1.249 | 0.020 | SLOWER | 1.249 | SLOWER |
| smp24 | WALK/one/norun | `[:a]` | search_short | real | 5469 | 1.224 | 0.030 | SLOWER | 1.224 | SLOWER |
| smp24 | WALK/one/norun | `[:a]` | search_short | random | 10426 | 1.623 | 0.030 | SLOWER | 1.623 | SLOWER |

- sample, scalar RTE/DEF: 122 rows over 24 patterns, geometric mean 1.074, min 0.105, max 29.071
- sample SLOWER beyond floor, scalar: smp04 throughput/random 4.464; smp04 search_short/random 1.951; smp05 throughput/none 4.908; smp05 throughput/random 2.268; smp05 search_short/real 1.653; smp05 search_short/none 2.292; smp05 search_short/random 1.934; smp08 throughput/random 1.139; smp09 throughput/real 1.157; smp09 throughput/random 1.317; smp09 search_short/real 1.253; smp09 search_short/random 1.413; smp10 throughput/none 7.352; smp10 throughput/random 3.276; smp10 search_short/real 2.567; smp10 search_short/none 3.936; smp10 search_short/random 3.201; smp14 throughput/random 1.216; smp14 search_short/real 1.244; smp14 search_short/random 1.611; smp15 throughput/none 5.127; smp15 throughput/random 2.319; smp15 search_short/real 1.711; smp15 search_short/none 2.372; smp15 search_short/random 1.905; smp19 throughput/real 1.891; smp19 throughput/none 1.461; smp19 throughput/random 1.251; smp19 search_short/real 1.659; smp19 search_short/none 1.346; smp19 search_short/random 1.626; smp20 throughput/real 10.263; smp20 throughput/none 29.071; smp20 throughput/random 8.913; smp20 search_short/real 3.160; smp20 search_short/none 5.933; smp20 search_short/random 3.673; smp24 throughput/random 1.249; smp24 search_short/real 1.224; smp24 search_short/random 1.623
- sample SLOWER beyond floor, SIMD layer: smp04 throughput/random 4.464; smp04 search_short/random 1.951; smp05 throughput/real 9.547; smp05 throughput/none 11.843; smp05 throughput/random 12.290; smp05 search_short/real 2.916; smp05 search_short/none 4.007; smp05 search_short/random 4.078; smp08 throughput/random 1.139; smp09 throughput/real 1.157; smp09 throughput/random 1.317; smp09 search_short/real 1.253; smp09 search_short/random 1.413; smp10 throughput/real 12.784; smp10 throughput/none 18.215; smp10 throughput/random 17.643; smp10 search_short/real 4.430; smp10 search_short/none 7.277; smp10 search_short/random 6.998; smp14 throughput/random 1.216; smp14 search_short/real 1.244; smp14 search_short/random 1.611; smp15 throughput/real 9.907; smp15 throughput/none 12.492; smp15 throughput/random 12.302; smp15 search_short/real 2.990; smp15 search_short/none 4.172; smp15 search_short/random 3.883; smp19 throughput/real 1.891; smp19 throughput/none 1.461; smp19 throughput/random 1.251; smp19 search_short/real 1.659; smp19 search_short/none 1.346; smp19 search_short/random 1.626; smp20 throughput/real 10.263; smp20 throughput/none 29.071; smp20 throughput/random 8.913; smp20 search_short/real 3.160; smp20 search_short/none 5.933; smp20 search_short/random 3.673; smp24 throughput/random 1.249; smp24 search_short/real 1.224; smp24 search_short/random 1.623

## D-hors admission (E[sh]) (not the §6 bar)

D-hors sites (esh_588.tsv, pick_esh_588.py's pick stratified by E[sh], the expected shift per probe under the default byte-rate prior), D-hors (RTE) vs D-one (NOH, `--memfn=no-wf-hors`) at both layers; alpha = wf-hors's G1 ratio (< 1: D-hors faster); floor = this run's A/A in the regime; where a site's SIMD-layer text equals its scalar text (a cover artifact carries no SIMD form) the arm was built and timed once and the SIMD alpha IS the scalar one; FINDINGS for the manager and Frank, never the bar, no default moves.

| site | pattern | E[sh] | max(sh) | stop mass ppm | regime | class | NOH ns/pass | alpha scalar (RTE/NOH) | floor | reading | alpha SIMD (RTEs/NOHs) | SIMD reading |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| esh01 | `(?s)[0-9a-f].[0-9a-f]` | 1.000 | 1 | 284434 | throughput | real | 1643296 | 1.699 | 0.020 | SLOWER | 1.699 | SLOWER |
| esh01 | `(?s)[0-9a-f].[0-9a-f]` | 1.000 | 1 | 284434 | throughput | random | 1195872 | 2.117 | 0.020 | SLOWER | 2.117 | SLOWER |
| esh01 | `(?s)[0-9a-f].[0-9a-f]` | 1.000 | 1 | 284434 | search_short | real | 11259 | 2.093 | 0.030 | SLOWER | 2.093 | SLOWER |
| esh01 | `(?s)[0-9a-f].[0-9a-f]` | 1.000 | 1 | 284434 | search_short | random | 18850 | 2.733 | 0.030 | SLOWER | 2.733 | SLOWER |
| esh02 | `(?s)[^a]..` | 1.000 | 1 | 945837 | throughput | real | 975837 | 1.001 | 0.020 | within | 1.001 | within |
| esh02 | `(?s)[^a]..` | 1.000 | 1 | 945837 | throughput | random | 927256 | 1.003 | 0.020 | within | 1.003 | within |
| esh02 | `(?s)[^a]..` | 1.000 | 1 | 945837 | search_short | real | 1257 | 1.005 | 0.030 | within | 1.005 | within |
| esh02 | `(?s)[^a]..` | 1.000 | 1 | 945837 | search_short | random | 1436 | 0.900 | 0.030 | FASTER | 0.900 | FASTER |
| esh03 | `[aeiou]..[aeiou]` | 1.030 | 4 | 252788 | throughput | real | 2975529 | 0.955 | 0.020 | FASTER | 0.955 | FASTER |
| esh03 | `[aeiou]..[aeiou]` | 1.030 | 4 | 252788 | throughput | random | 1324384 | 2.153 | 0.020 | SLOWER | 2.153 | SLOWER |
| esh03 | `[aeiou]..[aeiou]` | 1.030 | 4 | 252788 | search_short | real | 12940 | 1.237 | 0.030 | SLOWER | 1.237 | SLOWER |
| esh03 | `[aeiou]..[aeiou]` | 1.030 | 4 | 252788 | search_short | random | 48260 | 3.821 | 0.030 | SLOWER | 3.821 | SLOWER |
| esh04 | `\\b\\w*?\\B\\w` | 1.193 | 2 | 807006 | throughput | real | 2182780 | 0.974 | 0.020 | FASTER | 0.974 | FASTER |
| esh04 | `\\b\\w*?\\B\\w` | 1.193 | 2 | 807006 | throughput | random | 4425405 | 0.873 | 0.020 | FASTER | 0.873 | FASTER |
| esh04 | `\\b\\w*?\\B\\w` | 1.193 | 2 | 807006 | search_short | real | 2598 | 0.934 | 0.030 | FASTER | 0.934 | FASTER |
| esh04 | `\\b\\w*?\\B\\w` | 1.193 | 2 | 807006 | search_short | random | 4676 | 0.823 | 0.030 | FASTER | 0.823 | FASTER |
| esh05 | `\\w{5}` | 1.772 | 5 | 807006 | throughput | real | 1691774 | 0.883 | 0.020 | FASTER | 0.883 | FASTER |
| esh05 | `\\w{5}` | 1.772 | 5 | 807006 | throughput | random | 3389767 | 0.713 | 0.020 | FASTER | 0.713 | FASTER |
| esh05 | `\\w{5}` | 1.772 | 5 | 807006 | search_short | real | 11398 | 0.785 | 0.030 | FASTER | 0.785 | FASTER |
| esh05 | `\\w{5}` | 1.772 | 5 | 807006 | search_short | random | 21712 | 0.589 | 0.030 | FASTER | 0.589 | FASTER |
| esh06 | `[a-z][a-z0-9]{3}` | 1.785 | 4 | 663413 | throughput | real | 1417011 | 0.968 | 0.020 | FASTER | 0.968 | FASTER |
| esh06 | `[a-z][a-z0-9]{3}` | 1.785 | 4 | 663413 | throughput | random | 1726216 | 0.825 | 0.020 | FASTER | 0.825 | FASTER |
| esh06 | `[a-z][a-z0-9]{3}` | 1.785 | 4 | 663413 | search_short | real | 3612 | 0.980 | 0.030 | within | 0.980 | within |
| esh06 | `[a-z][a-z0-9]{3}` | 1.785 | 4 | 663413 | search_short | random | 30836 | 0.991 | 0.030 | within | 0.991 | within |
| esh07 | `[a-z]{6}` | 2.683 | 6 | 663413 | throughput | real | 1335739 | 1.035 | 0.020 | SLOWER | 1.035 | SLOWER |
| esh07 | `[a-z]{6}` | 2.683 | 6 | 663413 | throughput | random | 1523924 | 0.465 | 0.020 | FASTER | 0.465 | FASTER |
| esh07 | `[a-z]{6}` | 2.683 | 6 | 663413 | search_short | real | 14880 | 1.100 | 0.030 | SLOWER | 1.100 | SLOWER |
| esh07 | `[a-z]{6}` | 2.683 | 6 | 663413 | search_short | random | 99724 | 0.252 | 0.030 | FASTER | 0.252 | FASTER |
| esh08 | `[0-9a-f]{4}` | 3.147 | 4 | 284434 | throughput | real | 1684027 | 0.595 | 0.020 | FASTER | 0.595 | FASTER |
| esh08 | `[0-9a-f]{4}` | 3.147 | 4 | 284434 | throughput | random | 1254074 | 0.637 | 0.020 | FASTER | 0.637 | FASTER |
| esh08 | `[0-9a-f]{4}` | 3.147 | 4 | 284434 | search_short | real | 75451 | 0.402 | 0.030 | FASTER | 0.402 | FASTER |
| esh08 | `[0-9a-f]{4}` | 3.147 | 4 | 284434 | search_short | random | 86001 | 0.452 | 0.030 | FASTER | 0.452 | FASTER |
| esh09 | `[0-9a-f]{5}` | 3.862 | 5 | 284434 | throughput | real | 1687755 | 0.524 | 0.020 | FASTER | 0.524 | FASTER |
| esh09 | `[0-9a-f]{5}` | 3.862 | 5 | 284434 | throughput | none | 1591709 | 0.509 | 0.020 | FASTER | 0.509 | FASTER |
| esh09 | `[0-9a-f]{5}` | 3.862 | 5 | 284434 | throughput | random | 1255682 | 0.516 | 0.020 | FASTER | 0.516 | FASTER |
| esh09 | `[0-9a-f]{5}` | 3.862 | 5 | 284434 | search_short | real | 93066 | 0.286 | 0.030 | FASTER | 0.286 | FASTER |
| esh09 | `[0-9a-f]{5}` | 3.862 | 5 | 284434 | search_short | none | 115774 | 0.292 | 0.030 | FASTER | 0.292 | FASTER |
| esh09 | `[0-9a-f]{5}` | 3.862 | 5 | 284434 | search_short | random | 89505 | 0.337 | 0.030 | FASTER | 0.337 | FASTER |
| esh10 | `[0-9a-f]{6}` | 4.578 | 6 | 284434 | throughput | real | 1659135 | 0.458 | 0.020 | FASTER | 0.458 | FASTER |
| esh10 | `[0-9a-f]{6}` | 4.578 | 6 | 284434 | throughput | none | 1596247 | 0.431 | 0.020 | FASTER | 0.431 | FASTER |
| esh10 | `[0-9a-f]{6}` | 4.578 | 6 | 284434 | throughput | random | 1253749 | 0.430 | 0.020 | FASTER | 0.430 | FASTER |
| esh10 | `[0-9a-f]{6}` | 4.578 | 6 | 284434 | search_short | real | 94164 | 0.232 | 0.030 | FASTER | 0.232 | FASTER |
| esh10 | `[0-9a-f]{6}` | 4.578 | 6 | 284434 | search_short | none | 122743 | 0.221 | 0.030 | FASTER | 0.221 | FASTER |
| esh10 | `[0-9a-f]{6}` | 4.578 | 6 | 284434 | search_short | random | 92944 | 0.256 | 0.030 | FASTER | 0.256 | FASTER |
| esh11 | `[0-9a-f]{7}` | 5.293 | 7 | 284434 | throughput | real | 1664087 | 0.401 | 0.020 | FASTER | 0.401 | FASTER |
| esh11 | `[0-9a-f]{7}` | 5.293 | 7 | 284434 | throughput | none | 1599380 | 0.367 | 0.020 | FASTER | 0.367 | FASTER |
| esh11 | `[0-9a-f]{7}` | 5.293 | 7 | 284434 | throughput | random | 1262567 | 0.366 | 0.020 | FASTER | 0.366 | FASTER |
| esh11 | `[0-9a-f]{7}` | 5.293 | 7 | 284434 | search_short | real | 91221 | 0.202 | 0.030 | FASTER | 0.202 | FASTER |
| esh11 | `[0-9a-f]{7}` | 5.293 | 7 | 284434 | search_short | none | 122588 | 0.182 | 0.030 | FASTER | 0.182 | FASTER |
| esh11 | `[0-9a-f]{7}` | 5.293 | 7 | 284434 | search_short | random | 93591 | 0.211 | 0.030 | FASTER | 0.211 | FASTER |
| esh12 | `[0-9a-f]{8}` | 6.009 | 8 | 284434 | throughput | real | 1664139 | 0.348 | 0.020 | FASTER | 0.348 | FASTER |
| esh12 | `[0-9a-f]{8}` | 6.009 | 8 | 284434 | throughput | none | 1600715 | 0.316 | 0.020 | FASTER | 0.316 | FASTER |
| esh12 | `[0-9a-f]{8}` | 6.009 | 8 | 284434 | throughput | random | 1253899 | 0.317 | 0.020 | FASTER | 0.317 | FASTER |
| esh12 | `[0-9a-f]{8}` | 6.009 | 8 | 284434 | search_short | real | 88325 | 0.180 | 0.030 | FASTER | 0.180 | FASTER |
| esh12 | `[0-9a-f]{8}` | 6.009 | 8 | 284434 | search_short | none | 120749 | 0.153 | 0.030 | FASTER | 0.153 | FASTER |
| esh12 | `[0-9a-f]{8}` | 6.009 | 8 | 284434 | search_short | random | 92068 | 0.176 | 0.030 | FASTER | 0.176 | FASTER |

### alpha sorted by E[sh] (geometric mean over regimes and classes; counts of SLOWER/FASTER cells)

| E[sh] | site | pattern | max(sh) | stop mass ppm | scalar alpha gmean [min, max] | scalar SLOWER/FASTER | SIMD alpha gmean [min, max] | SIMD SLOWER/FASTER |
|---|---|---|---|---|---|---|---|---|
| 1.000 | esh01 | `(?s)[0-9a-f].[0-9a-f]` | 1 | 284434 | 2.130 [1.699, 2.733] | 4/0 of 4 | 2.130 [1.699, 2.733] | 4/0 of 4 |
| 1.000 | esh02 | `(?s)[^a]..` | 1 | 945837 | 0.976 [0.900, 1.005] | 0/1 of 4 | 0.976 [0.900, 1.005] | 0/1 of 4 |
| 1.030 | esh03 | `[aeiou]..[aeiou]` | 4 | 252788 | 1.766 [0.955, 3.821] | 3/1 of 4 | 1.766 [0.955, 3.821] | 3/1 of 4 |
| 1.193 | esh04 | `\\b\\w*?\\B\\w` | 2 | 807006 | 0.899 [0.823, 0.974] | 0/4 of 4 | 0.899 [0.823, 0.974] | 0/4 of 4 |
| 1.772 | esh05 | `\\w{5}` | 5 | 807006 | 0.735 [0.589, 0.883] | 0/4 of 4 | 0.735 [0.589, 0.883] | 0/4 of 4 |
| 1.785 | esh06 | `[a-z][a-z0-9]{3}` | 4 | 663413 | 0.938 [0.825, 0.991] | 0/2 of 4 | 0.938 [0.825, 0.991] | 0/2 of 4 |
| 2.683 | esh07 | `[a-z]{6}` | 6 | 663413 | 0.605 [0.252, 1.100] | 2/2 of 4 | 0.605 [0.252, 1.100] | 2/2 of 4 |
| 3.147 | esh08 | `[0-9a-f]{4}` | 4 | 284434 | 0.512 [0.402, 0.637] | 0/4 of 4 | 0.512 [0.402, 0.637] | 0/4 of 4 |
| 3.862 | esh09 | `[0-9a-f]{5}` | 5 | 284434 | 0.396 [0.286, 0.524] | 0/6 of 6 | 0.396 [0.286, 0.524] | 0/6 of 6 |
| 4.578 | esh10 | `[0-9a-f]{6}` | 6 | 284434 | 0.322 [0.221, 0.458] | 0/6 of 6 | 0.322 [0.221, 0.458] | 0/6 of 6 |
| 5.293 | esh11 | `[0-9a-f]{7}` | 7 | 284434 | 0.273 [0.182, 0.401] | 0/6 of 6 | 0.273 [0.182, 0.401] | 0/6 of 6 |
| 6.009 | esh12 | `[0-9a-f]{8}` | 8 | 284434 | 0.235 [0.153, 0.348] | 0/6 of 6 | 0.235 [0.153, 0.348] | 0/6 of 6 |

- E[sh] reading: 12 sites live of 12 in esh.tsv (findings only; no part of the bar)

SIMD-on reading (reported, not the bar): SLOWER: foobar match/real 1.033 > 1.020
== s3t BAR FAIL: 72 cells read on the scalar layer; FAILING: foobar match/real 1.032 > 1.020
