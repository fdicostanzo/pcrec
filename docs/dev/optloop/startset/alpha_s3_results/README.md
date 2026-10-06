# START-SET stage 3 (the DFA hat) — Linux alpha, raw results (lane alphas3, 2026-10-06)

Read: `docs/dev/lanes/alphas3_report.md`. Everything here is the box's own output,
fetched verbatim; nothing was edited after the run.

## Pin, box, protocol

- BASE `5d47db6b` (main before the hat, abi 63), NEW `8148e034` (the stage-3 merge, abi 64),
  DENY = NEW `-fno-start-set` (bit 47). Built from `git archive` tarballs of the two
  commits (copied over, so the box repo got no ref and no worktree).
- ubuntubudu (Ryzen 5 1600), gcc 15.2.0-16ubuntu1, glibc 2.43 (`ldd` 2.43-2ubuntu2.4),
  scalar layer only, governor schedutil / boost=1, `taskset -c 2`, 5 launches x 5
  passes round-robin across the arms, a cell is the median of the per-launch medians,
  load1 < 0.5 gated before every cell/subject. Pre-run: load1 0.06, `df -h /` 13 GB free.
- Box work dir `/home/duxevents/pcrec/scratch_lx/alphas3` (gitignored `scratch_lx`),
  removed afterwards. Last box run ended 2026-10-06T17:26:18Z (`chain2.log` `ALL2_DONE`).
- Subjects: `alpha_s3.sh build` regenerates the bench's throughput subjects read-only with
  the bench's own generators; all 24 SHA lines read OK (`out.build.log`).

## Files

| file | what |
|---|---|
| `out.build.log`, `out.check.log` | `alpha_s3.sh build` / `check` (check: `rc=0`; answers identical on base/new/deny, W/C program-structure checks pass) |
| `out.time1.log`, `out.time2.log` | `alpha_s3.sh time`, run 1 and the time-only reproducibility pass (run 2); the driver's own columns and verdicts |
| `main_cells.md` | the two runs side by side (`summarize.py main`) |
| `out.g1classify.log`, `out.g1build.log`, `out.g1check.log`, `g1_movers.tsv` | the Q3/Q4 extension (`../alpha_s3_g1.py`): the 89 manifest movers compiled on NEW and DENY, 30 classified `G1 emitted->dominated`; built (5 arms for the 30, 3 for the rest); answers checked (`g1 check: rc=0`) |
| `out.g1time1.log`, `out.g1time2.log` | the extension's two timing passes: every mover x its throughput subjects (174 rows each) |
| `all_movers.md` | those two side by side (`summarize.py g1`) |
| `q3_per_mover.md` | the per-mover G1 table: base / new (elided) / `-fno-req-byte` / keep (hat + pre-check), `new - keep` in ns/B and ns/call, the program-identical null |
| `out.density.log` | per mover and subject: the hat's set T, and d_T = the fraction of subject bytes in T |
| `out.short1.log`, `out.short2.log` | SYNTHETIC short-call probe (`../alpha_s3_short.py`), two passes: the K90 comparison |
| `chain.log`, `chain2.log`, `run_chain.sh`, `run_chain2.sh` | the detached chains (stamps, rc's) |
| `summarize.py` | renders the markdown tables from the logs |

## Arms of the extension (`alpha_s3_g1.py`)

`base`, `new`, `deny` as in `alpha_s3.sh`; `noreq` = NEW `-fno-req-byte` (D148 addendum 4's
named arm); `keep` = a scratch build of NEW with ONE line patched
(`req_dominated_applies` returns false in `src/gen/emit_dfa.c`), i.e. the hat AND the pre-check.
No flag produces `keep` (the `dominated` row is undeniable), so the ruling's "with the pre-check"
is the twin; `noreq` is kept as the ruled arm and as a program-identical null (on a G1 mover the
elided form has no pre-check, so `new` and `noreq` are the same program: `.text` byte-identical
on all 30, column `textsame`).

## Reading cautions

- The driver's per-cell floor is one sample of |deny - base|; where the cell sits on the
  `memchr` floor (0.0167 ns/B) it is ~0.00001 and a 0.4% effect reads REGRESSION. Every
  such cell is converted to ns per call in the report and read against a call-sized scale.
- Corpus movers (tests/...) carry no throughput subject of their own; they are timed on the
  bench's capability prose (`cap:t-64k`, `cap:t-1m`), a SCRATCH-tier population.
