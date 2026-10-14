# summarize.py over census_bench/sites.tsv (pcrec caf64716, 2026-10-11)
patterns=367 compiles=734 failed=47 (bench tree d359564f-era checkout at /home/pcrec/projects/pcrec-bench, read-only)
| stream | role | sites | bounded | byte | pair-cube | pair-adj | pair-other | small-k<=2 | small-k3 | small-k4+ | range>2 | cube>2 | wide-r2 | wide-r3-4 | wide-r5+ | wide-k<=4 | ANY k<=4 cubes | ANY <=2 ranges |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| default | dfa-hat | 16 | 16 | 0 | 0 | 0 | 0 | 1 | 7 | 0 | 4 | 0 | 2 | 0 | 2 | 0 | 10 | 7 |
| default | dfa-pf | 102 | 3 | 0 | 7 | 2 | 0 | 3 | 2 | 7 | 36 | 3 | 17 | 13 | 12 | 0 | 43 | 66 |
| default | vm-hat | 17 | 0 | 8 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 7 | 0 | 0 | 10 | 10 |
| vm | vm-hat | 285 | 0 | 136 | 13 | 3 | 1 | 5 | 9 | 8 | 46 | 3 | 26 | 22 | 13 | 2 | 204 | 231 |
