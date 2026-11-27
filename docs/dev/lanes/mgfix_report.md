# mgfix report

## Fix
Implemented in two places, both in `tests/core/memgate/`. `memgate.py` `drv_argv` runs every `mg_instr` under `setarch $(uname -m) -R` (ADDR_NO_RANDOMIZE). I chose the Python wrapper because it needs no re-exec and no rebuild of the sides, and it is testable from the command line. `mg_drv.c -DMG_INSTR` also checks `personality()` and exits 3 if the flag is missing, so a direct run cannot silently count with ASLR on.
`mg_peak` needs no wrapper: it counts REQUESTED bytes, so no address enters. An A/A run over 1,500 compiles (two directories, same binary) gave every delta +0 and VERDICT WITHIN at bound 0. `gdrv` is the growth driver, not an instruction count.
Second defect found while reading how T1's noise read was done: `memgate.py` keys results by side directory, so `A == B` (the same directory twice) overwrites the first run with the second, and every ratio is 1 by construction. This is why T1's "noise 0 over 7,402" saw no jitter: it was vacuous for peak as well as instr. `main` now refuses A == B; the header and CLAUDE.md say the noise read needs a second directory of the same binaries.
Control: `test_verdicts.py` asserts that the `mg_instr` command is `setarch ... -R` and that `mg_peak` is run directly (14/14 pass). A manual check showed that `mg_instr` run directly exits 3.

## Noise read
Base `cd17dea82` against a copy of itself (`instr`, 4,500 corpus compiles, `--jobs 2`, scratch `/var/tmp/pcrec-pcrec/scratch/mgfix/`):
- ASLR ON (old command line): ratio min 0.9791, p95 1.00019, max 1.02196; max |delta| 20,770 instructions; 3 OVER-BAND (corpus/263, 2741, 1826), VERDICT STOP. The five flagged compiles ranged 0.996..1.0084.
- ASLR OFF (new): ratio min 0.99999, p95 1.00000, max 1.00001; max |delta| 246 (on a large compile); VERDICT WITHIN. The five flagged compiles (3372, 4394, 2743, 3326, 4406) agree within 1 instruction (2743: 92,995 vs 92,994, the rest identical), so the STOP RULE did not fire.
G5's bands (1.01 / 1.02) are unchanged; the measured noise is recorded beside them in `docs/design/arena_scopes.md` G5.

## Gates
- `python3 -I tests/core/memgate/test_verdicts.py`: ok 14/14.
- A/A runs above. Pre-existing `-Wuse-after-free` warning in `mg_drv.c` (`pcrec_inject_realloc_at`) is untouched.
- OWED: queue job `200-mgfix-mg` (`make memgate MEMGATE_BASE=cd17dea82 MEMGATE_BOUND=112` on this worktree), lanecheck key `mgfix-mg`.

## STATE AT HANDOFF
Rulings file: empty. Branch lane/mgfix committed. OWED: mgfix-mg (the full memgate gate on F2+F6 plus the r105 fixes).
