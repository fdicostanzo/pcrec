# job 581 (lane r27b): window-search arms, SCALAR layer only

- layer: SCALAR (portable C, `-fno-memfn-simd`, the kit's default OFF); SIMD is NOT read here and its verdict is pcrec-bench's (D144 addendum 4)
- memfn profile: none named by the kit (D147: there is no portable/native/baseline profile); arms are hand-rendered REPORT text over the harness build (`pcrec-harness --harness=kit-proof`), gcc -O2, no -march, one pinned core (cpu 7, sibling 15), gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0
- compilers: pcrec ffe4f86e0800, pcrec-harness 84d3d346bfb4 (the 580 build)
- L=5 launches, T=20000000 ns per sample, N=9 samples

## Table A: ratio to DEF (and the reading F=FASTER S=SLOWER -=NULL) ; floor in absolute terms

| cell | regime | class | DEF ns/pass | DEF ns/B | floor(PRO) rel | floor(PRO) ns/pass | floor(PRO) ns/B | COV/DEF | AA/DEF | PRO/DEF | PRO2/DEF | SHF/DEF | HRS/DEF | PRR/DEF | PRF/DEF | HRS/PRO | SHF/PRO | PRR/PRO | PRF/PRO | PRO2/PRO (A/A) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lit-l8 | throughput | real | 66290 | 0.0632 | 0.020 | 1325.8 | 0.0013 | 9.854S | 0.996- | 0.947F | 0.946F | 0.947F | 4.418S |  | 0.932F | 4.665S | 1.000- |  | 0.984- | 0.999 |
| lit-l8 | throughput | none | 62382 | 0.0595 | 0.020 | 1247.6 | 0.0012 | 10.488S | 1.001- | 0.998- | 0.999- | 0.996- | 4.725S |  | 0.974F | 4.733S | 0.997- |  | 0.975F | 1.001 |
| lit-l8 | throughput | dense | 1882643 | 1.7954 | 0.020 | 37652.9 | 0.0359 | 0.289F | 0.999- | 0.266F | 0.266F | 0.262F | 0.165F |  | 0.323F | 0.621F | 0.987- |  | 1.214S | 1.001 |
| lit-l8 | search_short | real | 9177 | 0.0911 | 0.020 | 185.5 | 0.0018 | 3.867S | 1.016- | 0.854F | 0.853F | 0.832F | 1.097S |  | 0.932F | 1.284S | 0.974F |  | 1.091S | 0.999 |
| lit-l8 | search_short | none | 8679 | 0.0895 | 0.020 | 173.6 | 0.0018 | 6.147S | 1.002- | 0.958F | 0.959F | 0.960F | 1.362S |  | 1.034S | 1.421S | 1.002- |  | 1.079S | 1.001 |
| lit-l8 | search_short | dense | 11809 | 0.1185 | 0.020 | 236.2 | 0.0024 | 0.332F | 1.000- | 0.269F | 0.269F | 0.269F | 0.158F |  | 0.368F | 0.587F | 0.999- |  | 1.368S | 1.001 |
| lit-l8 | match | real | 3325 | 0.0333 | 0.020 | 66.5 | 0.0007 | 0.999- | 0.998- | 0.999- | 1.002- | 0.998- | 0.998- |  | 1.003- | 0.999- | 1.000- |  | 1.004- | 1.003 |
| lit-l8 | match | none | 2211 | 0.0224 | 0.020 | 44.2 | 0.0004 | 1.000- | 0.999- | 1.008- | 1.008- | 1.017- | 1.000- |  | 1.008- | 0.992- | 1.009- |  | 1.000- | 1.000 |
| lit-l8 | match | dense | 7240 | 0.0739 | 0.020 | 144.8 | 0.0015 | 1.001- | 1.006- | 1.002- | 1.001- | 1.009- | 0.999- |  | 1.001- | 0.997- | 1.007- |  | 0.998- | 0.999 |
| year4 | throughput | real | 547073 | 0.5217 | 0.020 | 10941.5 | 0.0104 | 1.214S | 1.003- | 0.870F | 0.867F | 1.117S | 1.183S | 1.225S |  | 1.360S | 1.284S | 1.408S |  | 0.997 |
| year4 | throughput | none | 414554 | 0.3953 | 0.020 | 8291.1 | 0.0079 | 1.324S | 1.000- | 0.907F | 0.909F | 1.264S | 1.336S | 1.427S |  | 1.472S | 1.394S | 1.573S |  | 1.002 |
| year4 | throughput | dense | 1606188 | 1.5318 | 0.020 | 32123.8 | 0.0306 | 0.740F | 0.999- | 0.694F | 0.693F | 0.673F | 0.698F | 0.697F |  | 1.005- | 0.970F | 1.005- |  | 0.997 |
| year4 | search_short | real | 16226 | 0.1662 | 0.035 | 565.1 | 0.0058 | 1.421S | 1.016- | 0.909F | 0.910F | 1.359S | 1.092S | 1.379S |  | 1.201S | 1.495S | 1.517S |  | 1.001 |
| year4 | search_short | none | 27536 | 0.2787 | 0.050 | 1371.8 | 0.0139 | 1.733S | 0.998- | 0.960- | 0.956- | 1.500S | 1.170S | 1.565S |  | 1.219S | 1.563S | 1.631S |  | 0.996 |
| year4 | search_short | dense | 5121 | 0.0534 | 0.027 | 140.8 | 0.0015 | 0.510F | 1.000- | 0.467F | 0.468F | 0.485F | 0.466F | 0.474F |  | 0.998- | 1.038S | 1.016- |  | 1.003 |
| year4 | match | real | 2107 | 0.0210 | 0.020 | 42.1 | 0.0004 | 0.954F | 1.000- | 1.001- | 1.001- | 0.954F | 0.971F | 1.114S |  | 0.970F | 0.953F | 1.112S |  | 1.000 |
| year4 | match | none | 1659 | 0.0171 | 0.020 | 33.2 | 0.0003 | 0.993- | 1.003- | 1.002- | 1.004- | 0.995- | 0.994- | 1.111S |  | 0.993- | 0.993- | 1.110S |  | 1.002 |
| year4 | match | dense | 2994 | 0.0306 | 0.020 | 59.9 | 0.0006 | 0.985- | 1.000- | 1.000- | 0.999- | 0.983- | 0.997- | 1.055S |  | 0.998- | 0.984- | 1.055S |  | 0.999 |
| file-ext-order | throughput | real | 207791 | 0.1982 | 0.020 | 4155.8 | 0.0040 | 3.733S | 1.000- | 0.927F | 0.921F | 0.941F | 2.856S |  | 0.924F | 3.080S | 1.015- |  | 0.996- | 0.993 |
| file-ext-order | throughput | none | 181899 | 0.1735 | 0.020 | 3638.0 | 0.0035 | 4.126S | 1.000- | 1.003- | 1.001- | 1.013- | 3.207S |  | 1.001- | 3.198S | 1.010- |  | 0.999- | 0.999 |
| file-ext-order | throughput | dense | 784224 | 0.7479 | 0.020 | 15684.5 | 0.0150 | 0.951F | 1.000- | 0.518F | 0.517F | 0.506F | 0.914F |  | 0.541F | 1.763S | 0.976F |  | 1.044S | 0.997 |
| file-ext-order | search_short | real | 13936 | 0.1393 | 0.020 | 278.7 | 0.0028 | 2.836S | 1.004- | 0.803F | 0.805F | 0.807F | 1.645S |  | 0.858F | 2.049S | 1.005- |  | 1.069S | 1.004 |
| file-ext-order | search_short | none | 13113 | 0.1318 | 0.020 | 262.3 | 0.0026 | 5.060S | 0.999- | 1.033S | 1.036S | 1.121S | 2.418S |  | 1.094S | 2.342S | 1.085S |  | 1.060S | 1.003 |
| file-ext-order | search_short | dense | 13610 | 0.1397 | 0.020 | 272.2 | 0.0028 | 0.368F | 1.002- | 0.242F | 0.229F | 0.229F | 0.227F |  | 0.290F | 0.935F | 0.943- |  | 1.198S | 0.943 |
| file-ext-order | match | real | 2625 | 0.0266 | 0.020 | 52.5 | 0.0005 | 0.992- | 0.995- | 1.039S | 1.044S | 0.998- | 0.998- |  | 0.996- | 0.960F | 0.961F |  | 0.958F | 1.004 |
| file-ext-order | match | none | 2254 | 0.0227 | 0.020 | 45.1 | 0.0005 | 0.986- | 0.997- | 1.065S | 1.064S | 1.000- | 0.985- |  | 0.999- | 0.925F | 0.939F |  | 0.938F | 0.999 |
| file-ext-order | match | dense | 4152 | 0.0428 | 0.020 | 83.0 | 0.0009 | 1.005- | 1.008- | 1.004- | 1.003- | 1.002- | 0.999- |  | 1.001- | 0.994- | 0.998- |  | 0.996- | 0.998 |
| hex8-bounded | throughput | real | 2550160 | 2.4320 | 0.020 | 51003.2 | 0.0486 | 0.890F | 0.994- | 0.931F | 0.930F | 0.803F | 0.458F | 1.030S |  | 0.493F | 0.863F | 1.107S |  | 1.000 |
| hex8-bounded | throughput | none | 2405029 | 2.2936 | 0.020 | 48100.6 | 0.0459 | 0.927F | 1.003- | 1.021S | 1.023S | 0.821F | 0.490F | 1.145S |  | 0.480F | 0.805F | 1.121S |  | 1.003 |
| hex8-bounded | throughput | dense | 1523007 | 1.4525 | 0.020 | 30558.4 | 0.0291 | 1.322S | 1.001- | 1.412S | 1.394S | 1.378S | 1.531S | 1.472S |  | 1.084S | 0.975F | 1.042S |  | 0.987 |
| hex8-bounded | search_short | real | 38436 | 0.3975 | 0.020 | 768.7 | 0.0079 | 1.560S | 1.002- | 1.422S | 1.423S | 1.079- | 0.523F | 1.402S |  | 0.368F | 0.759F | 0.986- |  | 1.001 |
| hex8-bounded | search_short | none | 170553 | 1.7287 | 0.023 | 3968.3 | 0.0402 | 1.303S | 0.986- | 1.064S | 1.052S | 0.734F | 0.173F | 1.219S |  | 0.163F | 0.690F | 1.146S |  | 0.989 |
| hex8-bounded | search_short | dense | 10517 | 0.1082 | 0.020 | 210.3 | 0.0022 | 1.184S | 0.999- | 1.132S | 1.133S | 0.698F | 1.139S | 1.363S |  | 1.006- | 0.616F | 1.203S |  | 1.001 |
| hex8-bounded | match | real | 3961 | 0.0403 | 0.020 | 79.2 | 0.0008 | 1.008- | 1.005- | 0.999- | 1.010- | 0.999- | 1.011- | 0.998- |  | 1.012- | 1.000- | 0.999- |  | 1.011 |
| hex8-bounded | match | none | 2948 | 0.0305 | 0.020 | 59.0 | 0.0006 | 0.999- | 0.999- | 0.998- | 0.999- | 1.005- | 0.998- | 0.998- |  | 1.000- | 1.007- | 1.000- |  | 1.001 |
| hex8-bounded | match | dense | 7169 | 0.0710 | 0.020 | 143.4 | 0.0014 | 0.997- | 0.998- | 0.994- | 1.022- | 0.995- | 0.997- | 0.997- |  | 1.003- | 1.001- | 1.003- |  | 1.029 |
| foobar | throughput | real | 67967 | 0.0648 | 0.020 | 1359.3 | 0.0013 | 7.545S | 0.998- | 0.965F | 0.965F | 0.960F | 5.552S |  | 0.957F | 5.756S | 0.995- |  | 0.992- | 1.001 |
| foobar | throughput | none | 65143 | 0.0621 | 0.020 | 1302.9 | 0.0012 | 7.806S | 1.001- | 1.011- | 1.009- | 1.000- | 6.542S |  | 0.996- | 6.472S | 0.989- |  | 0.985- | 0.998 |
| foobar | throughput | dense | 2077184 | 1.9810 | 0.020 | 41543.7 | 0.0396 | 0.320F | 1.000- | 0.302F | 0.302F | 0.305F | 0.199F |  | 0.343F | 0.658F | 1.009- |  | 1.137S | 1.001 |
| foobar | search_short | real | 8186 | 0.0838 | 0.020 | 163.7 | 0.0017 | 4.004S | 0.999- | 0.918F | 0.919F | 0.933F | 1.645S |  | 1.013- | 1.791S | 1.016- |  | 1.103S | 1.000 |
| foobar | search_short | none | 8473 | 0.0865 | 0.020 | 169.5 | 0.0017 | 5.206S | 0.998- | 1.002- | 1.001- | 1.029S | 2.030S |  | 1.089S | 2.026S | 1.027S |  | 1.087S | 0.999 |
| foobar | search_short | dense | 10008 | 0.1023 | 0.020 | 200.2 | 0.0020 | 0.317F | 1.004- | 0.318F | 0.318F | 0.302F | 0.202F |  | 0.395F | 0.636F | 0.950F |  | 1.242S | 0.999 |
| foobar | match | real | 2872 | 0.0295 | 0.020 | 57.4 | 0.0006 | 0.979F | 0.994- | 0.972F | 0.972F | 0.997- | 1.043S |  | 1.045S | 1.074S | 1.026S |  | 1.075S | 1.000 |
| foobar | match | none | 2451 | 0.0244 | 0.020 | 49.0 | 0.0005 | 0.932F | 0.999- | 0.929F | 0.927F | 1.002- | 0.997- |  | 0.997- | 1.073S | 1.079S |  | 1.073S | 0.998 |
| foobar | match | dense | 4602 | 0.0470 | 0.020 | 92.0 | 0.0009 | 1.001- | 1.000- | 1.007- | 1.024S | 0.997- | 1.037S |  | 1.034S | 1.030S | 0.990- |  | 1.027S | 1.017 |
| cat-bounded | throughput | real | 439574 | 0.4192 | 0.020 | 8791.5 | 0.0084 | 1.348S | 0.999- | 0.645F | 0.648F | 0.655F | 1.885S |  |  | 2.921S | 1.015- |  |  | 1.004 |
| cat-bounded | throughput | none | 474488 | 0.4525 | 0.020 | 9489.8 | 0.0091 | 1.217S | 1.003- | 0.559F | 0.564F | 0.571F | 1.699S |  |  | 3.040S | 1.021- |  |  | 1.008 |
| cat-bounded | throughput | dense | 3572661 | 3.4072 | 0.020 | 71453.2 | 0.0681 | 0.408F | 1.000- | 0.295F | 0.295F | 0.291F | 0.192F |  |  | 0.651F | 0.985- |  |  | 0.999 |
| cat-bounded | search_short | real | 14422 | 0.1478 | 0.020 | 288.4 | 0.0030 | 2.074S | 1.008- | 0.673F | 0.671F | 0.691F | 1.993S |  |  | 2.959S | 1.025S |  |  | 0.997 |
| cat-bounded | search_short | none | 18890 | 0.1915 | 0.020 | 377.8 | 0.0038 | 2.495S | 1.000- | 0.652F | 0.653F | 0.669F | 2.256S |  |  | 3.457S | 1.026S |  |  | 1.002 |
| cat-bounded | search_short | dense | 9590 | 0.0981 | 0.020 | 191.8 | 0.0020 | 0.340F | 0.995- | 0.404F | 0.402F | 0.400F | 0.255F |  |  | 0.633F | 0.991- |  |  | 0.996 |
| cat-bounded | match | real | 2963 | 0.0299 | 0.020 | 59.3 | 0.0006 | 1.001- | 1.000- | 0.999- | 0.999- | 0.997- | 1.002- |  |  | 1.004- | 0.998- |  |  | 1.000 |
| cat-bounded | match | none | 2623 | 0.0270 | 0.020 | 52.5 | 0.0005 | 1.002- | 1.001- | 0.998- | 0.998- | 0.999- | 1.001- |  |  | 1.002- | 1.001- |  |  | 1.000 |
| cat-bounded | match | dense | 4033 | 0.0415 | 0.025 | 101.0 | 0.0010 | 1.026S | 1.003- | 0.969F | 0.965F | 0.945F | 1.022- |  |  | 1.055S | 0.975F |  |  | 0.996 |
| done-eol | throughput | real | 646926 | 0.6170 | 0.020 | 12938.5 | 0.0123 | 1.270S | 1.000- | 0.686F | 0.688F | 0.705F | 1.119S |  |  | 1.632S | 1.029S |  |  | 1.003 |
| done-eol | throughput | none | 592014 | 0.5646 | 0.020 | 11840.3 | 0.0113 | 1.328S | 0.999- | 0.668F | 0.666F | 0.700F | 1.168S |  |  | 1.747S | 1.047S |  |  | 0.997 |
| done-eol | throughput | dense | 1122656 | 1.0706 | 0.020 | 22453.1 | 0.0214 | 0.472F | 1.001- | 0.325F | 0.325F | 0.327F | 0.442F |  |  | 1.361S | 1.007- |  |  | 1.001 |
| done-eol | search_short | real | 25392 | 0.2564 | 0.046 | 1155.7 | 0.0117 | 1.218S | 1.002- | 0.572F | 0.572F | 0.572F | 0.758F |  |  | 1.326S | 1.000- |  |  | 1.001 |
| done-eol | search_short | none | 35026 | 0.3520 | 0.020 | 700.5 | 0.0070 | 1.955S | 1.001- | 0.589F | 0.584F | 0.604F | 0.873F |  |  | 1.483S | 1.026S |  |  | 0.993 |
| done-eol | search_short | dense | 11330 | 0.1158 | 0.049 | 558.2 | 0.0057 | 0.349F | 1.005- | 0.291F | 0.291F | 0.276F | 0.243F |  |  | 0.834F | 0.948- |  |  | 1.000 |
| done-eol | match | real | 3007 | 0.0308 | 0.020 | 60.1 | 0.0006 | 1.005- | 0.997- | 0.998- | 0.997- | 1.001- | 0.994- |  |  | 0.997- | 1.003- |  |  | 0.999 |
| done-eol | match | none | 2465 | 0.0254 | 0.020 | 49.3 | 0.0005 | 1.001- | 0.999- | 1.000- | 0.999- | 1.001- | 0.999- |  |  | 1.000- | 1.001- |  |  | 1.000 |
| done-eol | match | dense | 4435 | 0.0454 | 0.030 | 134.5 | 0.0014 | 1.018- | 0.997- | 0.975- | 0.993- | 1.008- | 1.018- |  |  | 1.044S | 1.034S |  |  | 1.019 |
| word-digit | throughput | real | 2336742 | 2.2285 | 0.020 | 46734.8 | 0.0446 | 0.679F | 0.999- | 0.196F | 0.195F | 0.197F | 0.688F |  |  | 3.501S | 1.001- |  |  | 0.995 |
| word-digit | throughput | none | 2283836 | 2.1780 | 0.020 | 45676.7 | 0.0436 | 0.677F | 1.001- | 0.172F | 0.173F | 0.173F | 0.680F |  |  | 3.940S | 1.005- |  |  | 1.000 |
| word-digit | throughput | dense | 2692165 | 2.5674 | 0.020 | 53843.3 | 0.0513 | 0.708F | 1.001- | 0.672F | 0.674F | 0.688F | 0.685F |  |  | 1.019- | 1.024S |  |  | 1.004 |
| word-digit | search_short | real | 86894 | 0.8854 | 0.020 | 1737.9 | 0.0177 | 0.823F | 1.006- | 0.259F | 0.259F | 0.260F | 0.797F |  |  | 3.081S | 1.007- |  |  | 1.000 |
| word-digit | search_short | none | 189811 | 1.9416 | 0.020 | 3796.2 | 0.0388 | 0.735F | 1.000- | 0.214F | 0.214F | 0.217F | 0.763F |  |  | 3.559S | 1.011- |  |  | 1.000 |
| word-digit | search_short | dense | 4326 | 0.0431 | 0.020 | 86.5 | 0.0009 | 0.579F | 1.001- | 0.482F | 0.486F | 0.529F | 0.456F |  |  | 0.946F | 1.098S |  |  | 1.008 |
| word-digit | match | real | 2663 | 0.0270 | 0.020 | 53.3 | 0.0005 | 0.981- | 1.002- | 0.998- | 0.997- | 1.000- | 1.000- |  |  | 1.002- | 1.002- |  |  | 0.999 |
| word-digit | match | none | 2544 | 0.0263 | 0.020 | 50.9 | 0.0005 | 0.981- | 1.000- | 0.986- | 0.991- | 0.998- | 0.987- |  |  | 1.001- | 1.013- |  |  | 1.005 |
| word-digit | match | dense | 2986 | 0.0308 | 0.020 | 59.7 | 0.0006 | 0.999- | 1.001- | 1.000- | 0.999- | 1.003- | 1.006- |  |  | 1.006- | 1.003- |  |  | 0.999 |

## Table B: absolute, ns/pass / ns per byte (median of the launches)

| cell | regime | class | DEF | COV | AA | PRO | PRO2 | SHF | HRS | PRR | PRF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lit-l8 | throughput | real | 66290 / 0.0632 | 653236 / 0.6230 | 65997 / 0.0629 | 62782 / 0.0599 | 62728 / 0.0598 | 62775 / 0.0599 | 292889 / 0.2793 |  | 61752 / 0.0589 |
| lit-l8 | throughput | none | 62382 / 0.0595 | 654254 / 0.6239 | 62425 / 0.0595 | 62278 / 0.0594 | 62312 / 0.0594 | 62121 / 0.0592 | 294784 / 0.2811 |  | 60752 / 0.0579 |
| lit-l8 | throughput | dense | 1882643 / 1.7954 | 544256 / 0.5190 | 1881000 / 1.7939 | 500723 / 0.4775 | 501209 / 0.4780 | 494073 / 0.4712 | 310776 / 0.2964 |  | 607951 / 0.5798 |
| lit-l8 | search_short | real | 9177 / 0.0911 | 35486 / 0.3521 | 9326 / 0.0925 | 7840 / 0.0778 | 7829 / 0.0777 | 7632 / 0.0757 | 10063 / 0.0999 |  | 8550 / 0.0848 |
| lit-l8 | search_short | none | 8679 / 0.0895 | 53346 / 0.5500 | 8698 / 0.0897 | 8316 / 0.0857 | 8326 / 0.0859 | 8331 / 0.0859 | 11819 / 0.1219 |  | 8973 / 0.0925 |
| lit-l8 | search_short | dense | 11809 / 0.1185 | 3919 / 0.0393 | 11807 / 0.1185 | 3176 / 0.0319 | 3178 / 0.0319 | 3174 / 0.0319 | 1865 / 0.0187 |  | 4346 / 0.0436 |
| lit-l8 | match | real | 3325 / 0.0333 | 3322 / 0.0332 | 3317 / 0.0332 | 3320 / 0.0332 | 3330 / 0.0333 | 3319 / 0.0332 | 3318 / 0.0332 |  | 3334 / 0.0334 |
| lit-l8 | match | none | 2211 / 0.0224 | 2212 / 0.0224 | 2208 / 0.0224 | 2230 / 0.0226 | 2229 / 0.0226 | 2249 / 0.0228 | 2211 / 0.0224 |  | 2230 / 0.0226 |
| lit-l8 | match | dense | 7240 / 0.0739 | 7248 / 0.0740 | 7284 / 0.0744 | 7256 / 0.0741 | 7248 / 0.0740 | 7308 / 0.0746 | 7236 / 0.0739 |  | 7245 / 0.0740 |
| year4 | throughput | real | 547073 / 0.5217 | 664276 / 0.6335 | 548525 / 0.5231 | 475891 / 0.4538 | 474252 / 0.4523 | 611181 / 0.5829 | 647341 / 0.6174 | 670252 / 0.6392 |  |
| year4 | throughput | none | 414554 / 0.3953 | 548872 / 0.5234 | 414529 / 0.3953 | 376123 / 0.3587 | 376704 / 0.3593 | 524201 / 0.4999 | 553643 / 0.5280 | 591689 / 0.5643 |  |
| year4 | throughput | dense | 1606188 / 1.5318 | 1188840 / 1.1338 | 1605217 / 1.5309 | 1115203 / 1.0635 | 1112296 / 1.0608 | 1081580 / 1.0315 | 1120947 / 1.0690 | 1120225 / 1.0683 |  |
| year4 | search_short | real | 16226 / 0.1662 | 23052 / 0.2361 | 16478 / 0.1688 | 14748 / 0.1511 | 14763 / 0.1512 | 22046 / 0.2258 | 17719 / 0.1815 | 22377 / 0.2292 |  |
| year4 | search_short | none | 27536 / 0.2787 | 47717 / 0.4829 | 27474 / 0.2780 | 26428 / 0.2674 | 26321 / 0.2664 | 41313 / 0.4181 | 32228 / 0.3261 | 43093 / 0.4361 |  |
| year4 | search_short | dense | 5121 / 0.0534 | 2614 / 0.0273 | 5120 / 0.0534 | 2391 / 0.0250 | 2399 / 0.0250 | 2483 / 0.0259 | 2386 / 0.0249 | 2429 / 0.0253 |  |
| year4 | match | real | 2107 / 0.0210 | 2010 / 0.0200 | 2107 / 0.0210 | 2110 / 0.0210 | 2110 / 0.0210 | 2011 / 0.0200 | 2047 / 0.0204 | 2347 / 0.0234 |  |
| year4 | match | none | 1659 / 0.0171 | 1648 / 0.0170 | 1665 / 0.0171 | 1662 / 0.0171 | 1665 / 0.0171 | 1651 / 0.0170 | 1650 / 0.0170 | 1844 / 0.0190 |  |
| year4 | match | dense | 2994 / 0.0306 | 2949 / 0.0301 | 2994 / 0.0306 | 2993 / 0.0306 | 2991 / 0.0305 | 2944 / 0.0301 | 2987 / 0.0305 | 3159 / 0.0323 |  |
| file-ext-order | throughput | real | 207791 / 0.1982 | 775773 / 0.7398 | 207777 / 0.1982 | 192668 / 0.1837 | 191375 / 0.1825 | 195526 / 0.1865 | 593368 / 0.5659 |  | 191969 / 0.1831 |
| file-ext-order | throughput | none | 181899 / 0.1735 | 750454 / 0.7157 | 181816 / 0.1734 | 182395 / 0.1739 | 182149 / 0.1737 | 184227 / 0.1757 | 583339 / 0.5563 |  | 182145 / 0.1737 |
| file-ext-order | throughput | dense | 784224 / 0.7479 | 745604 / 0.7111 | 784369 / 0.7480 | 406571 / 0.3877 | 405550 / 0.3868 | 396884 / 0.3785 | 716610 / 0.6834 |  | 424367 / 0.4047 |
| file-ext-order | search_short | real | 13936 / 0.1393 | 39520 / 0.3949 | 13994 / 0.1398 | 11184 / 0.1118 | 11225 / 0.1122 | 11246 / 0.1124 | 22922 / 0.2290 |  | 11961 / 0.1195 |
| file-ext-order | search_short | none | 13113 / 0.1318 | 66359 / 0.6668 | 13102 / 0.1317 | 13540 / 0.1360 | 13587 / 0.1365 | 14697 / 0.1477 | 31710 / 0.3186 |  | 14353 / 0.1442 |
| file-ext-order | search_short | dense | 13610 / 0.1397 | 5014 / 0.0515 | 13643 / 0.1401 | 3298 / 0.0339 | 3111 / 0.0319 | 3110 / 0.0319 | 3084 / 0.0317 |  | 3951 / 0.0406 |
| file-ext-order | match | real | 2625 / 0.0266 | 2603 / 0.0264 | 2612 / 0.0265 | 2728 / 0.0276 | 2739 / 0.0278 | 2620 / 0.0266 | 2619 / 0.0265 |  | 2614 / 0.0265 |
| file-ext-order | match | none | 2254 / 0.0227 | 2223 / 0.0224 | 2247 / 0.0226 | 2400 / 0.0242 | 2398 / 0.0242 | 2254 / 0.0227 | 2220 / 0.0224 |  | 2252 / 0.0227 |
| file-ext-order | match | dense | 4152 / 0.0428 | 4174 / 0.0430 | 4185 / 0.0431 | 4170 / 0.0430 | 4163 / 0.0429 | 4162 / 0.0429 | 4146 / 0.0427 |  | 4155 / 0.0428 |
| hex8-bounded | throughput | real | 2550160 / 2.4320 | 2269941 / 2.1648 | 2534184 / 2.4168 | 2373111 / 2.2632 | 2371960 / 2.2621 | 2048129 / 1.9532 | 1169167 / 1.1150 | 2626251 / 2.5046 |  |
| hex8-bounded | throughput | none | 2405029 / 2.2936 | 2229206 / 2.1259 | 2412747 / 2.3010 | 2455092 / 2.3414 | 2461386 / 2.3474 | 1975626 / 1.8841 | 1177743 / 1.1232 | 2753194 / 2.6257 |  |
| hex8-bounded | throughput | dense | 1523007 / 1.4525 | 2013491 / 1.9202 | 1524508 / 1.4539 | 2151161 / 2.0515 | 2123035 / 2.0247 | 2098284 / 2.0011 | 2332304 / 2.2243 | 2241564 / 2.1377 |  |
| hex8-bounded | search_short | real | 38436 / 0.3975 | 59966 / 0.6201 | 38497 / 0.3981 | 54648 / 0.5652 | 54696 / 0.5656 | 41462 / 0.4288 | 20102 / 0.2079 | 53900 / 0.5574 |  |
| hex8-bounded | search_short | none | 170553 / 1.7287 | 222151 / 2.2516 | 168088 / 1.7037 | 181432 / 1.8389 | 179382 / 1.8181 | 125189 / 1.2689 | 29529 / 0.2993 | 207982 / 2.1080 |  |
| hex8-bounded | search_short | dense | 10517 / 0.1082 | 12449 / 0.1280 | 10506 / 0.1080 | 11910 / 0.1225 | 11918 / 0.1226 | 7337 / 0.0754 | 11978 / 0.1232 | 14331 / 0.1474 |  |
| hex8-bounded | match | real | 3961 / 0.0403 | 3993 / 0.0406 | 3979 / 0.0404 | 3957 / 0.0402 | 4000 / 0.0407 | 3958 / 0.0402 | 4004 / 0.0407 | 3954 / 0.0402 |  |
| hex8-bounded | match | none | 2948 / 0.0305 | 2946 / 0.0305 | 2946 / 0.0305 | 2941 / 0.0304 | 2945 / 0.0305 | 2963 / 0.0307 | 2942 / 0.0304 | 2942 / 0.0304 |  |
| hex8-bounded | match | dense | 7169 / 0.0710 | 7145 / 0.0708 | 7156 / 0.0709 | 7125 / 0.0706 | 7328 / 0.0726 | 7134 / 0.0707 | 7148 / 0.0708 | 7146 / 0.0708 |  |
| foobar | throughput | real | 67967 / 0.0648 | 512834 / 0.4891 | 67817 / 0.0647 | 65556 / 0.0625 | 65606 / 0.0626 | 65251 / 0.0622 | 377373 / 0.3599 |  | 65041 / 0.0620 |
| foobar | throughput | none | 65143 / 0.0621 | 508483 / 0.4849 | 65237 / 0.0622 | 65854 / 0.0628 | 65748 / 0.0627 | 65123 / 0.0621 | 426177 / 0.4064 |  | 64851 / 0.0618 |
| foobar | throughput | dense | 2077184 / 1.9810 | 663919 / 0.6332 | 2076219 / 1.9800 | 627157 / 0.5981 | 627777 / 0.5987 | 632650 / 0.6033 | 412471 / 0.3934 |  | 713287 / 0.6802 |
| foobar | search_short | real | 8186 / 0.0838 | 32779 / 0.3355 | 8177 / 0.0837 | 7517 / 0.0769 | 7520 / 0.0770 | 7638 / 0.0782 | 13465 / 0.1378 |  | 8293 / 0.0849 |
| foobar | search_short | none | 8473 / 0.0865 | 44109 / 0.4501 | 8453 / 0.0863 | 8488 / 0.0866 | 8482 / 0.0866 | 8715 / 0.0889 | 17197 / 0.1755 |  | 9226 / 0.0942 |
| foobar | search_short | dense | 10008 / 0.1023 | 3177 / 0.0325 | 10045 / 0.1027 | 3186 / 0.0326 | 3184 / 0.0325 | 3025 / 0.0309 | 2026 / 0.0207 |  | 3957 / 0.0404 |
| foobar | match | real | 2872 / 0.0295 | 2813 / 0.0289 | 2855 / 0.0293 | 2791 / 0.0286 | 2791 / 0.0286 | 2863 / 0.0294 | 2997 / 0.0307 |  | 3002 / 0.0308 |
| foobar | match | none | 2451 / 0.0244 | 2285 / 0.0228 | 2449 / 0.0244 | 2276 / 0.0227 | 2271 / 0.0227 | 2455 / 0.0245 | 2443 / 0.0244 |  | 2443 / 0.0244 |
| foobar | match | dense | 4602 / 0.0470 | 4609 / 0.0471 | 4601 / 0.0470 | 4634 / 0.0473 | 4713 / 0.0481 | 4589 / 0.0469 | 4772 / 0.0487 |  | 4758 / 0.0486 |
| cat-bounded | throughput | real | 439574 / 0.4192 | 592366 / 0.5649 | 439030 / 0.4187 | 283682 / 0.2705 | 284721 / 0.2715 | 287925 / 0.2746 | 828548 / 0.7902 |  |  |
| cat-bounded | throughput | none | 474488 / 0.4525 | 577318 / 0.5506 | 475871 / 0.4538 | 265182 / 0.2529 | 267394 / 0.2550 | 270828 / 0.2583 | 806281 / 0.7689 |  |  |
| cat-bounded | throughput | dense | 3572661 / 3.4072 | 1457709 / 1.3902 | 3572232 / 3.4067 | 1054798 / 1.0059 | 1053994 / 1.0052 | 1038646 / 0.9905 | 686934 / 0.6551 |  |  |
| cat-bounded | search_short | real | 14422 / 0.1478 | 29907 / 0.3065 | 14536 / 0.1490 | 9711 / 0.0995 | 9679 / 0.0992 | 9959 / 0.1021 | 28738 / 0.2946 |  |  |
| cat-bounded | search_short | none | 18890 / 0.1915 | 47129 / 0.4778 | 18895 / 0.1916 | 12324 / 0.1249 | 12344 / 0.1251 | 12645 / 0.1282 | 42605 / 0.4319 |  |  |
| cat-bounded | search_short | dense | 9590 / 0.0981 | 3261 / 0.0334 | 9542 / 0.0976 | 3873 / 0.0396 | 3858 / 0.0395 | 3839 / 0.0393 | 2450 / 0.0251 |  |  |
| cat-bounded | match | real | 2963 / 0.0299 | 2966 / 0.0300 | 2963 / 0.0300 | 2959 / 0.0299 | 2960 / 0.0299 | 2955 / 0.0299 | 2970 / 0.0300 |  |  |
| cat-bounded | match | none | 2623 / 0.0270 | 2628 / 0.0270 | 2626 / 0.0270 | 2618 / 0.0269 | 2618 / 0.0269 | 2621 / 0.0270 | 2625 / 0.0270 |  |  |
| cat-bounded | match | dense | 4033 / 0.0415 | 4137 / 0.0426 | 4046 / 0.0416 | 3907 / 0.0402 | 3892 / 0.0401 | 3811 / 0.0392 | 4121 / 0.0424 |  |  |
| done-eol | throughput | real | 646926 / 0.6170 | 821620 / 0.7836 | 647008 / 0.6170 | 443552 / 0.4230 | 445019 / 0.4244 | 456403 / 0.4353 | 723709 / 0.6902 |  |  |
| done-eol | throughput | none | 592014 / 0.5646 | 786085 / 0.7497 | 591216 / 0.5638 | 395675 / 0.3773 | 394401 / 0.3761 | 414439 / 0.3952 | 691324 / 0.6593 |  |  |
| done-eol | throughput | dense | 1122656 / 1.0706 | 529478 / 0.5049 | 1123447 / 1.0714 | 364672 / 0.3478 | 364941 / 0.3480 | 367296 / 0.3503 | 496148 / 0.4732 |  |  |
| done-eol | search_short | real | 25392 / 0.2564 | 30929 / 0.3124 | 25454 / 0.2571 | 14515 / 0.1466 | 14528 / 0.1467 | 14513 / 0.1466 | 19242 / 0.1943 |  |  |
| done-eol | search_short | none | 35026 / 0.3520 | 68459 / 0.6879 | 35065 / 0.3524 | 20615 / 0.2072 | 20472 / 0.2057 | 21142 / 0.2124 | 30575 / 0.3072 |  |  |
| done-eol | search_short | dense | 11330 / 0.1158 | 3959 / 0.0405 | 11392 / 0.1164 | 3301 / 0.0337 | 3301 / 0.0337 | 3128 / 0.0320 | 2751 / 0.0281 |  |  |
| done-eol | match | real | 3007 / 0.0308 | 3022 / 0.0310 | 2999 / 0.0307 | 3000 / 0.0307 | 2997 / 0.0307 | 3008 / 0.0308 | 2989 / 0.0306 |  |  |
| done-eol | match | none | 2465 / 0.0254 | 2467 / 0.0255 | 2464 / 0.0254 | 2464 / 0.0254 | 2463 / 0.0254 | 2467 / 0.0255 | 2463 / 0.0254 |  |  |
| done-eol | match | dense | 4435 / 0.0454 | 4516 / 0.0462 | 4420 / 0.0452 | 4323 / 0.0443 | 4405 / 0.0451 | 4469 / 0.0457 | 4514 / 0.0462 |  |  |
| word-digit | throughput | real | 2336742 / 2.2285 | 1586438 / 1.5129 | 2335171 / 2.2270 | 458976 / 0.4377 | 456743 / 0.4356 | 459432 / 0.4381 | 1606848 / 1.5324 |  |  |
| word-digit | throughput | none | 2283836 / 2.1780 | 1546199 / 1.4746 | 2285510 / 2.1796 | 393955 / 0.3757 | 394096 / 0.3758 | 395946 / 0.3776 | 1552371 / 1.4805 |  |  |
| word-digit | throughput | dense | 2692165 / 2.5674 | 1906344 / 1.8180 | 2693529 / 2.5687 | 1808099 / 1.7243 | 1815683 / 1.7316 | 1852005 / 1.7662 | 1843227 / 1.7578 |  |  |
| word-digit | search_short | real | 86894 / 0.8854 | 71482 / 0.7284 | 87405 / 0.8906 | 22484 / 0.2291 | 22495 / 0.2292 | 22635 / 0.2306 | 69270 / 0.7058 |  |  |
| word-digit | search_short | none | 189811 / 1.9416 | 139566 / 1.4276 | 189756 / 1.9410 | 40702 / 0.4163 | 40702 / 0.4163 | 41140 / 0.4208 | 144845 / 1.4816 |  |  |
| word-digit | search_short | dense | 4326 / 0.0431 | 2506 / 0.0250 | 4329 / 0.0431 | 2084 / 0.0208 | 2102 / 0.0209 | 2289 / 0.0228 | 1972 / 0.0196 |  |  |
| word-digit | match | real | 2663 / 0.0270 | 2612 / 0.0265 | 2667 / 0.0271 | 2657 / 0.0270 | 2655 / 0.0270 | 2663 / 0.0270 | 2663 / 0.0270 |  |  |
| word-digit | match | none | 2544 / 0.0263 | 2497 / 0.0258 | 2543 / 0.0263 | 2508 / 0.0259 | 2521 / 0.0261 | 2539 / 0.0262 | 2510 / 0.0259 |  |  |
| word-digit | match | dense | 2986 / 0.0308 | 2985 / 0.0308 | 2990 / 0.0308 | 2986 / 0.0308 | 2983 / 0.0308 | 2995 / 0.0309 | 3004 / 0.0310 |  |  |

## R-27.1's bar per arm (non-match: real/none vs DEF SLOWER, dense vs COV slower)

PRO: 6 miss(es)
- file-ext-order/search_short/none PRO/DEF 1.033
- hex8-bounded/throughput/none PRO/DEF 1.021
- hex8-bounded/throughput/dense PRO/COV 1.068
- hex8-bounded/search_short/real PRO/DEF 1.422
- hex8-bounded/search_short/none PRO/DEF 1.064
- cat-bounded/search_short/dense PRO/COV 1.188
SHF: 8 miss(es)
- year4/throughput/real SHF/DEF 1.117
- year4/throughput/none SHF/DEF 1.264
- year4/search_short/real SHF/DEF 1.359
- year4/search_short/none SHF/DEF 1.500
- file-ext-order/search_short/none SHF/DEF 1.121
- hex8-bounded/throughput/dense SHF/COV 1.042
- foobar/search_short/none SHF/DEF 1.029
- cat-bounded/search_short/dense SHF/COV 1.177
HRS: 23 miss(es)
- lit-l8/throughput/real HRS/DEF 4.418
- lit-l8/throughput/none HRS/DEF 4.725
- lit-l8/search_short/real HRS/DEF 1.097
- lit-l8/search_short/none HRS/DEF 1.362
- year4/throughput/real HRS/DEF 1.183
- year4/throughput/none HRS/DEF 1.336
- year4/search_short/real HRS/DEF 1.092
- year4/search_short/none HRS/DEF 1.170
- file-ext-order/throughput/real HRS/DEF 2.856
- file-ext-order/throughput/none HRS/DEF 3.207
- file-ext-order/search_short/real HRS/DEF 1.645
- file-ext-order/search_short/none HRS/DEF 2.418
- hex8-bounded/throughput/dense HRS/COV 1.158
- foobar/throughput/real HRS/DEF 5.552
- foobar/throughput/none HRS/DEF 6.542
- foobar/search_short/real HRS/DEF 1.645
- foobar/search_short/none HRS/DEF 2.030
- cat-bounded/throughput/real HRS/DEF 1.885
- cat-bounded/throughput/none HRS/DEF 1.699
- cat-bounded/search_short/real HRS/DEF 1.993
- cat-bounded/search_short/none HRS/DEF 2.256
- done-eol/throughput/real HRS/DEF 1.119
- done-eol/throughput/none HRS/DEF 1.168
PRR: 10 miss(es)
- year4/throughput/real PRR/DEF 1.225
- year4/throughput/none PRR/DEF 1.427
- year4/search_short/real PRR/DEF 1.379
- year4/search_short/none PRR/DEF 1.565
- hex8-bounded/throughput/real PRR/DEF 1.030
- hex8-bounded/throughput/none PRR/DEF 1.145
- hex8-bounded/throughput/dense PRR/COV 1.113
- hex8-bounded/search_short/real PRR/DEF 1.402
- hex8-bounded/search_short/none PRR/DEF 1.219
- hex8-bounded/search_short/dense PRR/COV 1.151
PRF: 7 miss(es)
- lit-l8/throughput/dense PRF/COV 1.117
- lit-l8/search_short/none PRF/DEF 1.034
- lit-l8/search_short/dense PRF/COV 1.109
- file-ext-order/search_short/none PRF/DEF 1.094
- foobar/throughput/dense PRF/COV 1.074
- foobar/search_short/none PRF/DEF 1.089
- foobar/search_short/dense PRF/COV 1.245

## match regime flagged by the SLOWER test (T9; any class, vs DEF)

PRO: 2 SLOWER
- file-ext-order/match/real PRO/DEF 1.039
- file-ext-order/match/none PRO/DEF 1.065
SHF: 0 SLOWER
HRS: 2 SLOWER
- foobar/match/real HRS/DEF 1.043
- foobar/match/dense HRS/DEF 1.037
PRR: 3 SLOWER
- year4/match/real PRR/DEF 1.114
- year4/match/none PRR/DEF 1.111
- year4/match/dense PRR/DEF 1.055
PRF: 2 SLOWER
- foobar/match/real PRF/DEF 1.045
- foobar/match/dense PRF/DEF 1.034

## Population counts (measured, per cell and subject class) against the PREDICTOR

Predictor: pcrec's default byte-rate prior (tests/findings/default_ppm.tsv) summed per set as memfn/src/presence.c set_mass does; class-independent. Survival = positions (chain tests) passed before the first failure.

| cell | class | K | stop@ | stop hits/KiB (pred) | verify-fail frac (pred) | mean survival (pred) | pred HRS advance |
|---|---|---|---|---|---|---|---|
| lit-l8 | real | 8 | 1 | 14.74 (10.12) | 0.9834 (1.0000) | 0.618 (0.0552) | 7.155 |
| lit-l8 | none | 8 | 1 | 14.66 (10.12) | 1.0000 (1.0000) | 0.605 (0.0552) | 7.155 |
| lit-l8 | dense | 8 | 1 | 110.71 (10.12) | 0.0000 (1.0000) | 7.000 (0.0552) | 7.155 |
| foobar | real | 6 | 3 | 15.24 (10.12) | 0.9821 (1.0000) | 0.301 (0.0156) | 5.525 |
| foobar | none | 6 | 3 | 15.36 (10.12) | 1.0000 (1.0000) | 0.235 (0.0156) | 5.525 |
| foobar | dense | 6 | 3 | 141.27 (10.12) | 0.0000 (1.0000) | 5.000 (0.0156) | 5.525 |
| file-ext-order | real | 4 | 0 | 51.66 (10.21) | 0.9611 (0.9999) | 0.654 (0.0634) | 3.707 |
| file-ext-order | none | 4 | 0 | 50.88 (10.21) | 1.0000 (0.9999) | 0.572 (0.0634) | 3.707 |
| file-ext-order | dense | 4 | 0 | 74.94 (10.21) | 0.3992 (0.9999) | 1.802 (0.0634) | 3.707 |
| cat-bounded | real | 3 | 0 | 25.80 (18.88) | 0.8746 (0.9999) | 1.158 (0.0582) | 2.873 |
| cat-bounded | none | 3 | 0 | 25.32 (18.88) | 1.0000 (0.9999) | 0.932 (0.0582) | 2.873 |
| cat-bounded | dense | 3 | 0 | 219.45 (18.88) | 0.0000 (0.9999) | 4.000 (0.0582) | 2.873 |
| done-eol | real | 4 | 0 | 70.71 (28.84) | 0.9313 (1.0000) | 1.353 (0.0524) | 3.738 |
| done-eol | none | 4 | 0 | 69.83 (28.84) | 1.0000 (1.0000) | 1.168 (0.0524) | 3.738 |
| done-eol | dense | 4 | 0 | 74.19 (28.84) | 0.0823 (1.0000) | 3.692 (0.0524) | 3.738 |
| year4 | real | 4 | 0 | 78.10 (76.55) | 0.8335 (0.9996) | 1.159 (0.0808) | 3.776 |
| year4 | none | 4 | 0 | 40.52 (76.55) | 1.0000 (0.9996) | 0.665 (0.0808) | 3.776 |
| year4 | dense | 4 | 0 | 895.98 (76.55) | 0.4286 (0.9996) | 2.143 (0.0808) | 3.776 |
| word-digit | real | 2 | 1 | 15.44 (76.55) | 0.0000 (0.1930) | 1.000 (0.8070) | 1.193 |
| word-digit | none | 2 | 1 | 0.00 (76.55) | 0.0000 (0.1930) | 0.000 (0.8070) | 1.193 |
| word-digit | dense | 2 | 1 | 426.79 (76.55) | 0.0000 (0.1930) | 1.000 (0.8070) | 1.193 |
| hex8-bounded | real | 8 | 0 | 332.99 (291.26) | 0.9862 (1.0000) | 1.396 (0.3975) | 6.009 |
| hex8-bounded | none | 8 | 0 | 333.18 (291.26) | 1.0000 (1.0000) | 1.383 (0.3975) | 6.009 |
| hex8-bounded | dense | 8 | 0 | 910.22 (291.26) | 0.8750 (1.0000) | 3.750 (0.3975) | 6.009 |

### Which cells do SHF and HRS win or lose (against PRO; six non-match rows per cell)

net = (rows pair-FASTER) - (rows pair-SLOWER) against PRO, pair floor from PRO2/PRO; vsDEF is the same count of the arm's own reading against DEF.

| cell | pred survival | pred stop mass ppm | pred HRS advance | SHF F/S vs PRO | HRS F/S vs PRO | PRR F/S | PRF F/S | SHF F/S vs DEF | HRS F/S vs DEF |
|---|---|---|---|---|---|---|---|---|---|
| lit-l8 | 0.0552 | 9886 | 7.155 | 1/0 WIN | 2/4 LOSE |  | 1/4 | 5/0 | 2/4 |
| year4 | 0.0808 | 74760 | 3.776 | 1/5 LOSE | 0/4 LOSE | 0/4 |  | 2/4 | 2/4 |
| file-ext-order | 0.0634 | 9969 | 3.707 | 1/1 TIE | 1/5 LOSE |  | 0/4 | 4/1 | 2/4 |
| hex8-bounded | 0.3975 | 284434 | 6.009 | 6/0 WIN | 4/1 WIN | 0/5 |  | 4/1 | 4/2 |
| foobar | 0.0156 | 9886 | 5.525 | 1/1 TIE | 2/4 LOSE |  | 0/4 | 4/1 | 2/4 |
| cat-bounded | 0.0582 | 18442 | 2.873 | 0/2 LOSE | 2/4 LOSE |  |  | 6/0 | 2/4 |
| done-eol | 0.0524 | 28161 | 3.738 | 0/3 LOSE | 1/5 LOSE |  |  | 6/0 | 4/2 |
| word-digit | 0.8070 | 74760 | 1.193 | 0/2 LOSE | 1/4 LOSE |  |  | 6/0 | 6/0 |

### Separation by a static rule from the masses (honest count of the contradicting cells)

- SHF by pred survival: best threshold rule 'WIN iff value <= 0.0552' leaves 2 of 6 decided cells contradicting: done-eol, hex8-bounded  [no-rule baseline: 2 contradicting; a rule only counts if it beats this]
- SHF by pred stop mass: best threshold rule 'WIN iff value <= 9886' leaves 1 of 6 decided cells contradicting: hex8-bounded  [no-rule baseline: 2 contradicting; a rule only counts if it beats this]
- SHF by pred HRS advance: best threshold rule 'WIN iff value >= 6.009' leaves 0 of 6 decided cells contradicting  [no-rule baseline: 2 contradicting; a rule only counts if it beats this]
- SHF by pred fail frac: best threshold rule 'WIN iff value >= 1' leaves 1 of 6 decided cells contradicting: done-eol  [no-rule baseline: 2 contradicting; a rule only counts if it beats this]
  decided: lit-l8=WIN, year4=LOSE, file-ext-order=TIE, hex8-bounded=WIN, foobar=TIE, cat-bounded=LOSE, done-eol=LOSE, word-digit=LOSE
- HRS by pred survival: best threshold rule 'WIN iff value >= 0.3975' leaves 1 of 8 decided cells contradicting: word-digit  [no-rule baseline: 1 contradicting; a rule only counts if it beats this]
- HRS by pred stop mass: best threshold rule 'WIN iff value >= 2.844e+05' leaves 0 of 8 decided cells contradicting  [no-rule baseline: 1 contradicting; a rule only counts if it beats this]
- HRS by pred HRS advance: best threshold rule 'WIN iff value >= 6.009' leaves 1 of 8 decided cells contradicting: lit-l8  [no-rule baseline: 1 contradicting; a rule only counts if it beats this]
- HRS by pred fail frac: best threshold rule 'WIN iff value >= 2' leaves 1 of 8 decided cells contradicting: hex8-bounded  [no-rule baseline: 1 contradicting; a rule only counts if it beats this]
  decided: lit-l8=LOSE, year4=LOSE, file-ext-order=LOSE, hex8-bounded=WIN, foobar=LOSE, cat-bounded=LOSE, done-eol=LOSE, word-digit=LOSE
