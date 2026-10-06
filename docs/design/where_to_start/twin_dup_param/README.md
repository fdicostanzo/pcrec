# twin_dup_param — the D77 trigger twin for the reverse-walk candidate row

Lane `revtwin`, 2026-10-06 (D151 item 2). MEASUREMENT ONLY: nothing under `src/`, `cli/`, `lib/`, `tests/`.
Verdict, stated plainly: **the D77 trigger is NOT MET** — the twin does not win the VM cell (it ties it). Details below
and in `../../where_to_start.md` §7.

## What was built

- Pattern `\b(\w+)=[^&]*&(?:[^&]*&)*\1=` = bench `capability/dup-param-detect` (`patterns.rxt:1049`), `pattern.txt`.
- ORIG: main's compiler (this lane's worktree, branch point `5d47db6b`, abi 63, gcc-16 on the Mac) with the pilot's
  generation line `pcrec -p rx --features all` (`GENERATION.txt`: engine vm, ncaps 2, `RX_REQ_BYTE "38"` (`&`),
  `RX_VM_PREFILTER none`, `RX_VM_START_SCAN first-class`). artifact.c sha256 `c910afe4...504d`.
- TWIN `rev` (`rev.r1.patch`, +28 lines in `rx_search_run`, sha256 `3ee071b8...e727`): the reverse-walk row of
  `where_to_start.md` §3/§5.1. After the artifact's own two presence prechecks (memchr `&`, memchr `=`, kept unchanged),
  the start-set seek and attempt loop are replaced by: memchr `=` from `j` (the landmark) -> walk back over the `\w`
  run (the artifact's own `rx_class_bitmap0`) to the candidate start `s` -> ONE `rx_match_anchored` at `s` -> on a
  fail, `j+1` and the next `=`. A run reaching below `search_from` yields no candidate (its `\b` start is below the
  search window; every start inside the run fails `\b`). P = `\b(\w+)` holds no backref/atomic/lookaround and cannot
  consume `=`, so G1 and G2 hold and the candidates are monotone. Give-up posture: the twin runs a subset of the
  original's attempts, so a give-up may become an answer, never the reverse (D151 item 4).
- `null`: the harness's noise control (3 comment lines). `orig2`: recompiled original.

## Identity (before any timing; `identity/`, `iterations.tsv`)

Hardened `artrev identity` (shrunken resources, give-up rule, livelock bound; window-start n/a: no internal prefilter),
libpcre2 sample = Homebrew 10.48 on the Mac (the harness's own oracle; NOT 10.46 — the 10.46 reference was used for the
soundness model re-run, `../model_1046.txt`):

| arm | subjects | result |
|---|---|---|
| rev, plain | t-64k, t-256k, t-1m + corpus 3000 battery/block 16, two match examples | PASS: 14,927 cases, 119,396 transcript lines, 1,475 of 14,924 search cases MATCH in the original, libpcre2 sample 1500/0 disagreements; 13,439 give-up repairs, all 13,439 equal libpcre2's answer |
| rev, `--san` | same | PASS (ASan+UBSan), same counts |
| null, plain / `--san` | same | PASS, 0 repairs |
| rev, plain + `--san` | synthetic dense + sparse | PASS, 2,478 cases, 237 matching; 2,144 repairs all oracle-checked |
| rev, plain | all 75 bench short subjects | PASS, 2,697 cases, 222 matching |
| rev, `--strict-giveup --skip-window` | t-64k | FAIL by design: 1,983 repairs (the twin answers where the original gives up under shrunken budgets). The rule treats the answer as the contract; a caller relying on `PCREC_ERR_STEPS/FRAMES` where the original gave up sees a different answer. D151 item 4 allows exactly this direction. (The `iterations.tsv` row `FAIL` at 11:56:36 is this run.) |

## Subjects

- THR cell = the bench's `throughput` subjects `bench/capability/throughput/t-{64k,256k,1m}.bin`, sha256 verified against
  `manifest_throughput.tsv` (`d2e4f134...`, `3cf7b248...`, `ccbdf7eb...`) — read straight from the bench checkout.
  **None of them contains `&` or `=`** (counted: 0 and 0), so the artifact's own REQ_BYTE precheck returns at memchr speed.
- SRCH cell = the bench's 75 short `search_short` subjects, regenerated read-only into scratch by importing the bench's
  own `gen_subjects.build()` (`scripts/gensubj.py`; the bench's `main()` would write into the bench and was not run);
  all 75 sha256 equal `manifest.tsv` (0 mismatches). Only `br-dup-param` (the single matching subject) and `waf-benign`
  contain `&`.
- dense / sparse: the bench has none for this pattern, and the THR subjects have no match to build them from, so
  `scripts/mkvar.py` makes SYNTHETIC ones from `t-1m.bin` (a 19-byte `\nkey=1&mid=2&key=3\n` record overwritten 255 times
  every 4096 B = dense, once at 3/4 = sparse; same length; sha256 `84307e02...` dense, `43a2b941...` sparse). Generality
  rows only, never part of a cell.

## Timing (ubuntubudu, gcc 15.2.0, Ryzen 5 1600, 11 interleaved rounds, load1 0.08 at start; `timing/`)

Commands: `scripts/timerun.sh 1|2` (`ARTREV_REMOTE_CC=gcc` on the `time` command only; `--remote ubuntubudu --wall 1500`).
Pass 1 (no pads) `001_pass1`, pass 2 (7 pads 16..112 on orig and rev) `002_pass2`; 2 of the 3 allowed runs.

| row | orig | rev | rev vs orig | null dev | verdict |
|---|---|---|---|---|---|
| **THR CELL** (pass 1, median of t64k/t256k/t1m) | 0.0371 ns/B (IQR 0.0008) | 0.0370 (IQR 0.0011) | +0.24% | 0.0001 | **NOISE** |
| t64k / t256k / t1m (pass 2, pads) | 0.0373 / 0.0371 / 0.0383 | 0.0374 / 0.0368 / 0.0209 | -0.13% / +0.76% / +45% | 0.0001 / 0.0002 / 0.0215 | NOISE all (t1m's IQR 0.0184 swamps it; null shows the same 0.0169) |
| **SRCH CELL** (pass 2, median of the 75 bench short subjects) | 1.8385 ns/B (IQR 0.0778) | 1.8819 (IQR 0.0511) | -2.36% (slower) | 0.0039 | **NOISE** (pad-median delta +0.0177 vs threshold 0.0957; paired pads mixed sign) |
| br-dup-param (the one matching bench subject, 11 B) | 8.17 | 10.91 | -33% | 7.23 (!) | NOISE (null deviates 88%: unmeasurable at 11 B) |
| waf-benign (has `&`, passes the prechecks) | 21.49 | 7.69 | +64.2% | 0.28 | WIN (pad-confirmed: pad-median delta +13.84 vs 2.54, all 7 paired pads positive) |
| synthetic dense (255 matches) | 1.106 | 1.085 | +1.9% | 0.090 | NOISE |
| synthetic sparse (1 match at 3/4) | 7.572 | 1.785 | +76.4% | 0.019 | WIN (pass 1 +76.7%; pad-confirmed: delta +5.94 vs spread 0.47, all 7 paired pads positive) |

`orig2` and `null` read NOISE on every row (run valid).

## Reading

The twin is the reverse walk, it is answer-identical, and it WINS where the artifact actually runs its attempt loop
(`waf-benign`, the sparse variant: -64% / -76% time). It does NOT win the bench's VM cell: the cell's subjects never reach
the loop. Since `[OPT-REQBYTE]`/`[OPT-FREQPICK]` the shipped artifact answers the throughput subjects with ONE `memchr('&')`
(0.037 ns/B, the floor `floor-byte` already shows), and the short-subject cell is dominated by per-call cost and the same
precheck (only 2 of 75 subjects pass it). The cycle-1 numbers that made this cell look like a loss (`dup-param-detect`
thr 576x, srch 1.87x, `cycle1_analysis.md:97,117`) predate those batches. Whether a bench subject WITH `&` and `=` and
no match (the case the twin wins) exists is the bench's to add; the twin's win is real and conditional on it.

Mac timings were not taken or used (scratch tier); no clock was read beyond the two ubuntubudu runs.

## Files

`rev.r1.patch` the twin; `GENERATION.txt` pin/abi/compile line; `pattern.txt`; `iterations.tsv` the ledger;
`identity/` transcripts' summaries (plain/san, rev/null); `timing/001_pass1`, `timing/002_pass2` (`summary.txt`, `raw.tsv`);
`scripts/` (`gensubj.py`, `mkvar.py`, `idrun.sh`, `timerun.sh`: scratch paths are this lane's `build-revtwin/`, untracked).
Re-run: build `build/pcrec`; `ARTREV_CC=gcc-16 ARTREV_ROOT=<dir> python3 -B studies/artrev/artrev.py gen dup_param_detect --pcrec build/pcrec --pattern-file pattern.txt --flags="--features all" --prefix rx --pin 5d47db6b`, `twin dup_param_detect rev --patch rev.r1.patch`, then `idrun.sh`/`timerun.sh` (abi 63 pin; a different compiler gives a different artifact sha).
