# armread/ -- inputs and script for armread_report.md
- `raw_EXT.tsv`, `time_EXT.log`: copies of the kit's slot timing (memfn-slot/grid1/time/raw_EXT.tsv, time_EXT.log; Zen 4, 2026-10-13/14).
- `counters.tsv`: the `cnt` twin rows (calls/matches/bytes) from `time_EXT.log`.
- `fit.py` (`python3 -I fit.py raw_EXT.tsv > fit.out`): per-engine C_call / c_byte / C_match fits, residuals, crossovers. `fit.out` is its output.
