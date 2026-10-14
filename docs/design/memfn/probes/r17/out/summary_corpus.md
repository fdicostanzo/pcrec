# summarize.py over census/sites.tsv (pcrec caf64716, 2026-10-11)
patterns=4542 compiles=9084 failed=755
| stream | role | sites | bounded | byte | pair-cube | pair-adj | pair-other | small-k<=2 | small-k3 | small-k4+ | range>2 | cube>2 | wide-r2 | wide-r3-4 | wide-r5+ | wide-k<=4 | ANY k<=4 cubes | ANY <=2 ranges |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| default | dfa-hat | 39 | 39 | 0 | 13 | 6 | 12 | 2 | 1 | 0 | 2 | 0 | 3 | 0 | 0 | 1 | 37 | 37 |
| default | dfa-pf | 772 | 210 | 0 | 49 | 93 | 94 | 7 | 32 | 34 | 135 | 4 | 109 | 150 | 65 | 14 | 420 | 522 |
| default | vm-hat | 225 | 0 | 97 | 12 | 21 | 23 | 1 | 3 | 0 | 5 | 2 | 4 | 41 | 16 | 0 | 159 | 167 |
| vm | vm-hat | 2974 | 0 | 1571 | 157 | 246 | 176 | 42 | 47 | 45 | 217 | 6 | 171 | 208 | 88 | 22 | 2472 | 2626 |
