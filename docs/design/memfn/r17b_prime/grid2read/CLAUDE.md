# docs/design/memfn/r17b_prime/grid2read/ — the reading of the zen4-grid2 timing slot

Lane grid2read (2026-10-16), ANALYSIS ONLY: no timing, no build, no `make`. The slot is
`worktrees/memfn-slot/grid2/` (method `kit-grid@2`, Zen 4 7700X, CPU 14, compiler
`lane/memfn-r17` c90d65e53, abi 77). The report is `docs/dev/lanes/grid2read_report.md`;
it cites sections of `analysis.txt` as "an. N.M".

| file | role |
|---|---|
| `grid2read.py` | the whole reading. `python3 -I grid2read.py [OUT] > analysis.txt` (OUT defaults to the slot directory; also rewrites `keys.tsv`). `--check` verifies `SHA256SUMS` and stops on a mismatch; `--sums` regenerates it. Prints the NULL rule, the contamination and load accounting, the eps tokens, beta/saving/F tables, the V1 staircase, the find-all fits and g*, the predictability diagnosis, the dispatch charges and the pay rule, the one-byte arms, the trigger probe, and the §9.3 predictions. |
| `grload2.py` | loaders: the raw launch files cut into VISITS (a requeue is a second visit of one key, never merged), the contamination window (as epoch seconds), counters and subject facts. |
| `analysis.txt` | the full output the report cites. |
| `keys.tsv` | the PROPOSED `kit-grid@2` rows the reading yields, in the shipped finder's own key spellings (`kit.delta.<alt>.<pick>.<kind>.n<N>`, `kit.cdisp_call.<kind>.<layer>.<nforms>`, ...), each with unit, value, layer, floor and a confidence label. NOT a measurement set (no digest, no deps). |
| `SHA256SUMS` | sha256 of the 18 slot files read, paths relative to OUT. |

The window is `WIN` in `grload2.py`: 2026-10-16 19:38:11 .. 19:39:30 EDT. A launch is stamped after it
ends and lasts <= ~1 s, so a visit overlaps iff a stamp is >= the window start and (stamp - 1 s) <= its end.
A visit with ANY launch row at load1 > 1.5 (the harness's LOADMAX) outside the window is LOAD-SUSPECT: excluded
from the noise statistics and the fits, and used for a constant only where the report says so.

Run with `python3 -I`; read-only against the slot directory; writes only `keys.tsv`/`SHA256SUMS` here.
