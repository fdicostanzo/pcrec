# r27b: job 581, the follow-up timing of the REPORT window-search forms (MEASUREMENT ONLY)

Lane r27b, 2026-10-21. Branch `lane/memfn-r27b`, cut from the kit branch `lane/memfn-b4scope`. Brief: job 581
(`581-kit-r27-follow`), Frank's GO of 2026-10-21. Nothing under `memfn/src`, `src/`, `cli/`, `lib/` or `tests/`
changed. Job 580's files (`docs/dev/lanes/r27_evidence/`) are untouched; the new instruments are in
`docs/dev/lanes/r27b_evidence/`. The job was DRY-RUN and QUEUED here, never timed by the lane.

**State: the timing run is OWED.** Job id `581-kit-r27-follow`. Completion line `== r27b COMPLETE rows=N launches=5`
(N is about 2000: 8 cells x 3 regimes x 3 classes x 5 launches x 8 to 9 arms). The queue run dir is
`worktrees/.boxqueue/{running,done,failed}/<TS>-581-kit-r27-follow/` (its `job.log` is the log). The table is
`build/r27b/job/r27b_table.md` in the r27b worktree, the raw rows `r27b_results.tsv` and the population counts
`pop.tsv` beside it. A red differential ends the job with `== r27b DIFFERENTIAL RED` (rc 3) and no timing.

## 1. What the job measures

Same harness as 580: the 650 harness (`docs/design/kit_proof/measure/`, unchanged), 8 cells, regimes throughput /
search_short / match, classes real / none / dense, 5 launches, T = 20 ms per sample, N = 9 samples, one pinned core
(cpu 7, sibling 15), gcc 15.2 -O2, no -march, the SAME compilers as 580 (copied into `build/r27b/bin/`, sha256
`pcrec` ffe4f86e..., `pcrec-harness` 84d3d346...). Scalar layer only; SIMD is not read and its verdict is
pcrec-bench's (D144 addendum 4). The kit names no memfn profile (D147), and the table header says so.

| arm | cells | what |
|---|---|---|
| DEF, COV, AA | all 8 | the 650 harness's own (default build; `cover` routed; A/A of DEF) |
| PRO, SHF | all 8 | 580's text, rendered by the same code (the renders were compared byte for byte with 580's) |
| PRO2 | all 8 | a byte-identical recompile of PRO (`cmp` in the build stage): the A/A pair for the new text |
| HRS | all 8 | Horspool over sets (below) |
| PRR | year4, hex8-bounded | PRO with the RIGHTMOST tie for the stop (year4 @3, hex8-bounded @7) |
| PRF | lit-l8, foobar, file-ext-order | PRO's text as a `noinline` function (`rx_mf1_find`), as the default build's ofsskip FUNC is |

**HRS.** Per window at c (the window is the span-0 positions 0..K-1; the loop ends when c + K > n): read the byte b at
the window's LAST position; if b is not in S[K-1], advance c by `sh[b]`; otherwise test the other span-0 positions and
the ctx items (the same `&&` chain as PRO, a literal as one memcmp of its first K-1 bytes) and, on failure, also
advance by `sh[b]`. `sh[b]` is the least t in 1..K-1 with b in S[K-1-t], else K; S[j] is the intersection of every
term tested at offset j, so each skipped position c + u (u < sh[b]) would need b in S[K-1-u], which it is not. ctx
items sit outside 0..K-1 and only narrow the set, so the shift stays sound. The table is a 256-byte `static const` in
the statement expression. No read leaves [0, n): the last byte is read only after c + K <= n holds; ctx items keep
their own bound and absent rule (the text is the generic row's, copied from 580).

## 2. Every arm's rendered text, one cell (year4; PRF on foobar)

The text replaces only the generic row's loop inside the statement expression (the operands and the miss value are
the kit's). Stop = least default byte-rate mass, a tie to the leftmost (PRO).

PRO (and PRO2, identical):

```c
for (;;) { while (rx_mf1_c + 0 < rx_mf1_n && !(rx_mf1_s[rx_mf1_c] >= 48 && rx_mf1_s[rx_mf1_c] <= 57)) rx_mf1_c++; if (rx_mf1_c + 4 > rx_mf1_n) break; if ((rx_mf1_s[rx_mf1_c + 1] >= 48 && rx_mf1_s[rx_mf1_c + 1] <= 57) && (rx_mf1_s[rx_mf1_c + 2] >= 48 && rx_mf1_s[rx_mf1_c + 2] <= 57) && (rx_mf1_s[rx_mf1_c + 3] >= 48 && rx_mf1_s[rx_mf1_c + 3] <= 57)) { rx_mf1_f = 1; break; } rx_mf1_c++; }
```

PRR (rightmost tie, stop at offset 3, the other three positions tested):

```c
for (;;) { while (rx_mf1_c + 3 < rx_mf1_n && !(rx_mf1_s[rx_mf1_c + 3] >= 48 && rx_mf1_s[rx_mf1_c + 3] <= 57)) rx_mf1_c++; if (rx_mf1_c + 4 > rx_mf1_n) break; if ((rx_mf1_s[rx_mf1_c] >= 48 && rx_mf1_s[rx_mf1_c] <= 57) && (rx_mf1_s[rx_mf1_c + 1] >= 48 && rx_mf1_s[rx_mf1_c + 1] <= 57) && (rx_mf1_s[rx_mf1_c + 2] >= 48 && rx_mf1_s[rx_mf1_c + 2] <= 57)) { rx_mf1_f = 1; break; } rx_mf1_c++; }
```

SHF (each test its own branch, the failure shift of 580):

```c
for (;;) { while (rx_mf1_c + 0 < rx_mf1_n && !(rx_mf1_s[rx_mf1_c] >= 48 && rx_mf1_s[rx_mf1_c] <= 57)) rx_mf1_c++; if (rx_mf1_c + 4 > rx_mf1_n) break; if (!((rx_mf1_s[rx_mf1_c + 1] >= 48 && rx_mf1_s[rx_mf1_c + 1] <= 57))) { rx_mf1_c += 2; continue; } if (!((rx_mf1_s[rx_mf1_c + 2] >= 48 && rx_mf1_s[rx_mf1_c + 2] <= 57))) { rx_mf1_c += 3; continue; } if (!((rx_mf1_s[rx_mf1_c + 3] >= 48 && rx_mf1_s[rx_mf1_c + 3] <= 57))) { rx_mf1_c += 4; continue; } rx_mf1_f = 1; break; }
```

HRS (the table elided to its shape: 1 for a digit, 4 otherwise):

```c
static const unsigned char rx_mf1_sh[256] = {...256 entries...}; for (;;) { unsigned char rx_mf1_b; if (rx_mf1_c + 4 > rx_mf1_n) break; rx_mf1_b = rx_mf1_s[rx_mf1_c + 3]; if (!((rx_mf1_b >= 48 && rx_mf1_b <= 57))) { rx_mf1_c += rx_mf1_sh[rx_mf1_b]; continue; } if ((rx_mf1_s[rx_mf1_c] >= 48 && rx_mf1_s[rx_mf1_c] <= 57) && (rx_mf1_s[rx_mf1_c + 1] >= 48 && rx_mf1_s[rx_mf1_c + 1] <= 57) && (rx_mf1_s[rx_mf1_c + 2] >= 48 && rx_mf1_s[rx_mf1_c + 2] <= 57)) { rx_mf1_f = 1; break; } rx_mf1_c += rx_mf1_sh[rx_mf1_b]; }
```

PRF on foobar (the search is a separate function; the call replaces the statement expression):

```c
static __attribute__((noinline)) size_t rx_mf1_find(const unsigned char *subject, size_t subject_length, size_t scan_position)
{
    return ({ const unsigned char *rx_mf1_s = (const unsigned char *)(subject); size_t rx_mf1_n = subject_length; size_t rx_mf1_lo = scan_position; size_t rx_mf1_c = rx_mf1_lo; int rx_mf1_f = 0; for (;;) { { const void *rx_mf1_q = rx_mf1_c + 3 < rx_mf1_n ? memchr(rx_mf1_s + rx_mf1_c + 3, 98, rx_mf1_n - rx_mf1_c - 3) : 0; if (!rx_mf1_q) break; rx_mf1_c = (size_t)((const unsigned char *)rx_mf1_q - rx_mf1_s) - 3; } if (rx_mf1_c + 6 > rx_mf1_n) break; if (!memcmp(rx_mf1_s + rx_mf1_c, "foobar", 6)) { rx_mf1_f = 1; break; } rx_mf1_c++; } rx_mf1_f ? rx_mf1_c : (subject_length); });
}
    scan_position = rx_mf1_find(subject, subject_length, scan_position);
```

## 3. The differential stage (no clock, runs FIRST, aborts the job if red)

`diff_581.py` writes, per cell, 2000 deterministic subjects (seeded from the cell id) of length 0..40 over an alphabet of
the cell's stop, set and ctx bytes plus a few others (space, `x`, newline, 0xE9). Half are pure random strings; half
plant an instance of the cell's match or a near-miss (a byte replaced, dropped, or the text cut short) in filler, and
half of those are cut so the planted text may END the subject. Python `re` (`python3 -I`, bytes) gives
`search(subject, lo)` for EVERY lo in 0..n: 318k to 368k checks per cell and sentinel phase set. The independent control shares no source with
pcrec.

`ddrv.c` calls each arm's `rx_search(subject, n, lo)` for every lo and compares (start, end), for EVERY arm of the cell
(DEF, COV, AA, PRO, PRO2, SHF, HRS, PRR, PRF), in two buffer modes:
- **sentinel:** the subject sits in the middle of a buffer with 64 sentinel bytes on EACH side. The sentinel is a per-cell
  tile that satisfies the cell's terms (`abcdefgh`, `foobar`, `.tar`, `cat `, `done\n`, digits, `a1`, `abcdef01 `), rotated
  through every phase of the tile, so a term read one byte past either end sees a byte that completes a match and shows as a
  wrong answer.
- **exact-size under ASan+UBSan** (`-DEXACT`, when libasan is present; it is on this box): the subject is a `malloc` block
  of exactly n bytes with no neighbours, so any over-read faults.

Validation of the stage itself (plants, in the scratchpad, not committed): an HRS bound changed from `c + 8 > n` to
`c + 7 > n` on lit-l8 goes RED in both modes (154 sentinel mismatches; an ASan heap-buffer-overflow). Smoke result on all
8 cells (the dry-run uses two; all 8 were run once by hand): 0 mismatches in every arm.
Also gated as 580 did: the 650 answer gate (DEF COV AA) and the same gate for every proto arm on the full subjects, 72 per arm.

## 4. The reading's improvements

- The table header names the layer (scalar only; SIMD is pcrec-bench's) and the memfn profile (none named, D147), the
  compilers' sha, L, T, N.
- Table A carries the ratio to DEF with its reading letter (F, S, -), DEF's absolute ns/pass and ns/byte, and the floor
  of PRO in relative, ns/pass and ns/byte terms; Table B carries every arm's absolute ns/pass / ns/byte; the pair
  columns (X/PRO with PRO2/PRO as the A/A floor) are in Table A.
- The `match` regime is flagged by the same SLOWER test, in its own list per arm.
- Per launch the log prints `load1`, the pinned CPU's and its SMT sibling's `cpu_busy`; the end prints both again and a
  final `load1` line.

## 5. Population counts and the PREDICTOR

`pop_581.py` (run by the job, output `pop.tsv`, printed in the table file). Per cell and subject class, over the
throughput subject (the bytes the timing reads), at every window position:
- stop hits per KiB (the PRO stop, which the script checks is the cell's stop);
- the fraction of stops where the verify chain fails;
- the measured mean survival: the chain tests PASSED before the first failure (a full pass counts every test).

PREDICTED, beside them: **pcrec's default byte-rate prior (`tests/findings/default_ppm.tsv`) summed per set as
`memfn/src/presence.c` `set_mass` does** (cap 1e6 ppm), class-independent. Stop mass and hits per KiB = 1024 x the stop's
mass; survival = sum over j >= 1 of the product of the masses of the first j chain tests (the chain is the other span-0
positions ascending, then the ctx items, each by its set's mass); fail fraction = 1 minus the product of all of them. One
column is 581's addition beside the brief's: the expected HRS advance per window under the prior, the sum over b of
rate[b] x sh[b].

`read_581.py` then labels each cell WIN / LOSE / TIE for SHF and for HRS against PRO (six non-match rows per cell, the
pair-FASTER minus pair-SLOWER count, the floor from PRO2/PRO), and finds for each predictor the best threshold rule
'WIN iff value >= t' (or <=). It prints the contradicting cells and the no-rule baseline (the minority count), so a rule
counts only if it beats the baseline. A degenerate case (all decided cells alike) is printed as TRIVIAL. Cells that
contradict the best rule are listed by name; nothing is smoothed. The prediction values were computed here (no timing):
the stop masses are 0.99 to 28.4 percent, the predicted survival 0.016 (foobar) to 0.81 (word-digit), and the expected HRS
advance 1.19 (word-digit) to 7.2 (lit-l8); the measured side is in `pop.tsv` after the run.

## 6. Where everything is

| item | path |
|---|---|
| instruments | `docs/dev/lanes/r27b_evidence/`: `proto_bodies_581.py`, `ddrv.c`, `diff_581.py`, `pop_581.py`, `measure_581.sh`, `read_581.py`, `581-kit-r27-follow` (the queue job) |
| job | `581-kit-r27-follow`, cap 3000 s, quiet gate as 580 (`--ready`), `idle-ok`, expect `^== r27b COMPLETE` |
| log | the queue run dir's `job.log` (under `worktrees/.boxqueue/*/<TS>-581-kit-r27-follow/`) |
| table, rows, populations | `build/r27b/job/r27b_table.md`, `r27b_results.tsv`, `pop.tsv` (r27b worktree, gitignored) |
| completion line | `== r27b COMPLETE rows=N launches=5` |

## 7. Not done, on purpose

No timing was run by the lane; the readings of section 4 and the predictor separation of section 5 wait for the job.
The panel's M5/U6 questions (E4 as a gated body row; whether HRS replaces it) are answered by that table, not here.
