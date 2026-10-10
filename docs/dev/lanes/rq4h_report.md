# rq4h — the RQ-4 tier-U timing harness and slot20 (lane rq4h, 2026-10-10)

Branch `lane/rq4h`, cut from the kit branch `lane/memfn-rq4` (= main
a2f66450, R-13 included). Built only. The timing slot itself is NOT run: the
kit manager launches it on main's GO. Nothing under `src/`, `cli/`, `lib/` or
`tests/` changed, so there is no abi event and no pin moves.

## 1. Summary (resume from here)

- **Harness** in `docs/design/memfn/probes/rq4/`:
  - `cells.tsv`: 51 cells (§2).
  - `rq4_drv.c`: the timing driver, linked against each pcrec-emitted
    artifact. It times the public `rx_search` and match_api §3.1.3's find-all
    loop over it.
  - `rq4.py`: the runner (emit, facts, build, check, time).
  - `rq4_table.py`: the reading.
  - Own `CLAUDE.md`; an entry in `probes/CLAUDE.md`.
- **Slot script**: `worktrees/memfn-slot/slot20/run.sh` (outside git).
  - Detached launch:
    `setsid nohup bash /home/pcrec/projects/pcrec/worktrees/memfn-slot/slot20/run.sh > /dev/null 2>&1 < /dev/null & disown`
  - The script redirects its own output into `slot20/run.log`.
  - It follows the slot18/19 shape: a START line with the tip, a stage line
    per step with its rc, a trap that writes `verdict.txt` and `FAILED`, and
    `SLOT20_DONE` plus `DONE` at the end.
  - It refuses to run over stale outputs.
  - The reading is `slot20/table.md`.
- **Estimated slot wall: about 75 min.** The ceiling is 3 h (§5).
- **Dry run done** (§6). It wrote only `slot20/dryrun/`; the slot's real
  output paths are untouched. Its numbers are NOT readings.
- **Facts confirmed** on all 51 cells, at 0.2 ms loops in scratch (not
  readings):
  - **Live arm.** At `-march=x86-64` every vrun arm's live dispatcher arm is
    w16; at `-march=x86-64-v3` it is w32. OFF is scalar everywhere.
  - **Answers.** The three arms answer identically on every subject (3,960
    answer rows).

## 2. The cells (`cells.tsv`) and why each is there

Every artifact is `pcrec -p rx --features all [--engine=vm] ARM -o
art/<cell>/<ARM>/rx.c --pattern P`. This is the same `--features all` that
emit_sweep and alpha_k82.sh use, and every arm has the same basename, so a
byte compare is a text compare.

| ids | class | pattern(s) | why |
|---|---|---|---|
| us | R1 | `(?i)union.*?select.*?from` (cap) | R-1 cell; a vrun mover at default (KA `C`, load +4; KB `L`, load +2) |
| up | R1 | userpass (bench `wild-secrets-username-password-pair`) | R-1 cell; **renders NO vrun today** (FORMS `none`), so it is a null cell |
| mi | R1 | `(?i)cat` (syn) | R-1 cell; a vrun mover (KA `C`@0, KB `A`@1) |
| cn | R1 | `it\Nm` (syn) | R-1 cell; exact, `fn-memchr`, **no vrun**, so a null cell |
| m01-m19 (18) | MOVER | slot18's default-engine movers | the corpus's vrun movers. `slot18_simd_mover_ids.txt`'s 87 rows give 20 distinct default patterns, and two of those ARE `mi`/`us`, so they are not repeated |
| v01-v19 (19) | MOVER | slot18's vm-engine movers | 19 distinct `--engine=vm` patterns |
| kb | KB | `(?i)cat`, KA's byte injected | KB's case: KA's byte is COMMON in the subject and the run is rare (see the next paragraph) |
| sp | SPARSE | `(?i)azqb` | §R4.9.7.1's sparse-pick `fn-pair` cell. Both picks are rare letters (KA `Z`@1, KB `Q`@2), which is glibc's best regime |
| n01-n08 | NULL | `xyzzy`, `\d+xyzzy`, `(?i)\d+ab/cd`, `(?i)x/1234` (auto), `[a-z]*select[a-z]*`; vm `xyzzy`, `(a\|b)+xyzzy`, `(?i)\d+ab/cd` | non-vrun controls from the same site classes (§R4.9.7.1's `fn-memchr` witnesses). Their three arms are byte-identical |

**How the KB cell's subject is built.** It injects `V | (~M & random)` at a
1/8 share of filler bytes. `(V, M)` is KA's scanned byte and mask, read from
the DEFAULT artifact's w16 helper. The filler is then sanitized again.

**Null population.** The null cells are 10: up, cn and n01-n08. They are
read from byte identity, not from the class column.
- **No vrun cell has DEFAULT ≡ KBDENY** (rankuse gives every corpus mover a
  KB). So the D−K null band is measured on non-vrun text: same-text arm pairs
  in the same run and binaries set. That is the floor rule's population, but
  it is not vrun text.

**Witnesses.** Each witness is a string the pattern matches, planted to make
hits. The check stage refuses a planted subject with 0 hits.

## 3. Regimes (K-1 names; integration.md §R4.9.5 item 7)

| label | class | what |
|---|---|---|
| `gate/tail-64k`, `gate/tail-1m` | THROUGHPUT, isolated | one `rx_search` from 0; the filler's only hit is at the END, so the scan crosses the whole subject (hit-sparse extreme) |
| `sweep/sparse-64k`, `sweep/sparse-1m` | THROUGHPUT, chained | §3.1.3 find-all, a hit every ~16 KiB (gaps uniform in [8, 24) KiB) |
| `sweep/dense-64k`, `sweep/dense-1m` | THROUGHPUT, chained | find-all, a hit every ~256 B |
| `pc16`, `pc64`, `pc256`, `pc1024` | PER-CALL | one call from 0 on each of up to 256 consecutive chunks of `sparse-64k` (the span ladder) |
| `short75` | PER-CALL | the capability set's 75 short subjects (bench, sha-checked) |
| `space8` .. `space256` | DENSITY | find-all over 64 KiB with the witness planted every S bytes. S ≤ the witness length is skipped (userpass keeps 64-256) |
| `bench/<set>-t-64k\|t-1m/{gate,sweep}` | BENCH | R-1's own bench subjects (`cap` for us/up, `syn` for mi/cn) |

**Filler.** The filler is pseudo-English: the driver's word list, with 1/16
capitalized, punctuation, and a newline about every 70 columns. It is
deterministic from (spec, witness, seed), so the three arms time the same
bytes. Every accidental match is killed before planting: rx_search finds
each match and its last byte becomes `#`. Each row prints the subject's
FNV-1a hash and the find-all answer, and the table refuses a verdict on a
row whose arms disagree (ANSWER-MISMATCH).

**Statistic** (§R4.9.5 item 8, R-1's `UNMEASURED DEFAULT:`s):
- Each reading is one process. It calibrates until a loop takes at least
  50 ms (min-ms), then takes the min of 3 such loops.
- There are 3 launches. The median is taken over launches, and the spread
  over launches is reported.

**Interleaving** (item 4). For each (launch, level, cell, regime) the three
arms run back to back. Their order rotates by `(launch + cell + regime) mod
3`, so each arm takes each position.

**Pinning.** Every reading runs under `taskset -c 12-15` (`--cpus`, default
12-15). The SMT siblings are read from `thread_siblings_list` (4,5,6,7 on
this box). Each reading records:
- the siblings' busy% from `/proc/stat` deltas;
- the CPUs' mean `scaling_cur_freq`;
- load1.

**Load wait.** Before each launch the slot waits, for at most 600 s, until
load1 < 1.5. This is not the spec's 0.5, because the run's own process counts
toward load1.

**Header** (item 1): CPU model and class (`zen4`, sub-class U-dev), governor,
boost, glibc, gcc, the pcrec tip, the kit (in-tree), the levels, the arms,
the loops and load1.

**Arms and levels** (item 4):
- The arms:
  - DEFAULT is `-fmemfn-simd`.
  - KBDENY is `-fmemfn-simd --memfn=no-vrun-kb`.
  - OFF is `-fno-memfn-simd`.
- The levels:
  - `v1` is `-O2 -march=x86-64 -mtune=generic`.
  - `v3` is `-O2 -march=x86-64-v3 -mtune=generic`. `-mtune=generic` is added
    per item 4's recipe rule; the brief wrote v3 without it.
- Each (cell, arm, level) is its own binary.
- **Live arm.** The facts stage preprocesses each artifact at the level
  (`gcc -E -P`) and reads which helper call survives in the dispatcher: a
  call to `__w32(` means w32, `__w16(` means w16, neither means scalar. A
  vrun arm that is not w16 at v1 / w32 at v3, or a non-vrun arm that is not
  scalar, is a FAIL.

## 4. How the null band is computed (`rq4_table.py`)

For each pair:
- D−K is `DEFAULT − KBDENY` (the KB question; + means KB costs).
- ON−OFF is `DEFAULT − OFF` (SIMD-on vs SIMD-off, D147; + means SIMD costs).

For each (regime, level), the null cells are those whose two artifacts in
that pair are byte-identical (`meta.tsv` id_DK / id_DO). Each null cell's
delta is computed exactly as a mover's is, from medians over launches.
- **FLOOR** is the maximum |delta| over those null cells (`UNMEASURED
  DEFAULT:` the maximum, until the null distribution supports a quantile;
  §R4.9.5 item 5).
- **Unit by class.** THROUGHPUT, DENSITY and BENCH deltas are relative (% of
  the second arm). PER-CALL deltas are absolute ns.
- **Verdict.**
  - LOSS if delta > +floor.
  - WIN if delta < −floor.
  - NULL otherwise.
  - NO-BAND if the regime has no null cell.
  - `null-cell` on the null cells themselves.
- **Discard rule.** Readings whose siblings were busier than `--sib-max`
  (`UNMEASURED DEFAULT:` 5%, item 2) are dropped before the median. The table
  prints kept/dropped counts per arm.
- **Multiple comparisons.** The summary counts comparisons per pair (item 8)
  and lists every LOSS past the floor.

**Limitations to read beside the numbers:**
- **(a)** The PER-CALL band is an absolute-ns maximum over null cells of
  different magnitudes.
- **(b)** The bench regimes' null population is only up and cn, the two R-1
  null cells.
- **(c)** The D−K band is non-vrun text (§2).

## 5. Estimated slot wall time

Planned readings: 3 launches × 2 levels × 872 (cell, regime) pairs × 3 arms
= **15,696**. Measured per reading at 50 ms loops on this box: **0.24-0.29 s**
(`/usr/bin/time` on six regime/subject shapes, 11:40). On top of that:
- emit, facts, build and check: 41 s for all 51 cells (smoke2);
- subjects: about 5 s;
- `make -j16`: seconds.

**Estimate: about 75 min.** Add up to 30 min if the load wait holds at each of
the 3 launches. The rq4 step's `gnutimeout` is 3 h.

**The slot needs** cores 12-15 AND their siblings 4-7 quiet. Otherwise the 5%
sibling-busy rule discards readings (the dry run, on a busy box, dropped 3 of
12). Re-rendering with `rq4_table.py slot20/run --sib-max 100` shows
everything, labelled by the cut it used.

## 6. Dry-run transcript (TINY; NOT a reading)

`RQ4_MODE=tiny bash .../slot20/run.sh` writes only `slot20/dryrun/`. It ran
2026-10-10 11:41:22 → 11:41:27 (5 s), tip 1388626a, with cells mi and n01,
regime `gate/tail-64k`, 1 launch and 5 ms loops. The null cell is included
so that the table's band path runs. `slot20/dryrun/run.log`:

```
START 2026-10-10T11:41:22-04:00 mode tiny tip 1388626a tree /home/pcrec/projects/pcrec/worktrees/rq4h cpus 12-15
BUILD rc=0
SUBJECTS rc=0 :: subjects: -> /home/pcrec/projects/pcrec/worktrees/memfn-slot/slot20/dryrun/subjects, sha256 mismatches 0
RQ4 rc=0 wall=1s :: RQ4-RUN COMPLETE /home/pcrec/projects/pcrec/worktrees/memfn-slot/slot20/dryrun/run fails=0 readings=12 wall=0s
TABLE rc=0 :: /home/pcrec/projects/pcrec/worktrees/memfn-slot/slot20/dryrun/table.md
SLOT20_DONE 2026-10-10T11:41:27-04:00
```

`rq4.log` stages: `STAGE emit rc=0 cells=2 artifacts=6`, `STAGE facts rc=0`,
`STAGE build rc=0 binaries=12`, `STAGE check rc=0 answers=12`, `STAGE time
rc=0 readings=12`. The table read `Readings kept / dropped (sibling busy >
5.0%): DEFAULT 2/2, KBDENY 3/1, OFF 4/0` (load1 3.97: the box was busy). So
the discard rule visibly fired, and the affected rows read NO-DATA.

Other runs, all in scratch (`$CLAUDE_JOB_DIR/tmp/rq4h/`) and none of them
readings:

| when (2026-10-10) | run | result |
|---|---|---|
| 11:38:02, 1 s | `rq4.py --tiny` | 12 readings, fails=0 |
| 11:38, ~5 s | `subjects_r4b.py` into scratch | 0 sha256 mismatches; the pcrec-bench checkout was unchanged before and after (`git status` empty) |
| 11:39:55 → 11:40:07 | smoke over 10 cells at 1 ms loops, every regime incl. bench and short75 | 1,086 readings, fails=0. This exercised every regime path (gate/sweep/pc/short/space/bench) and the KB injection |
| 11:40:32, 41 s | smoke2 over all 51 cells at 0.2 ms | 5,232 readings, fails=0; every live arm as expected; 3,960 answer rows equal across arms |
| 11:41:33 → 11:41:39 | the slot script launched DETACHED (`setsid nohup … & disown`) on a scratch copy | DONE |
| right after | a second run over the same output | `FAIL stale outputs …`, as designed |

## 7. Charter vs delivered

| charter item | delivered |
|---|---|
| Arms DEFAULT / KB-DENY / OFF, interleaved, both layers reported | yes: three arms per reading group in rotated order. The table reports D−K and ON−OFF (OFF = SIMD-off, the others SIMD-on) |
| Levels `-O2 -march=x86-64 -mtune=generic` and `-O2 -march=x86-64-v3`; live arm confirmed from the emitted dispatcher | yes, with `-mtune=generic` on both (§R4.9.5 item 4). The live arm is read per (cell, arm, level) from the preprocessed artifact, and a mismatch FAILs |
| The four R-1 cells as pcrec renders them | yes: us, up, mi, cn from the bench patterns with `--features all`. up and cn render no vrun today and serve as null cells |
| The corpus's vrun movers, deduped | yes: 39 distinct (pattern, engine) cells, two of them being mi/us |
| (a) KA's byte common, run rare | yes: `kb`, with KA's byte injected at 1/8 |
| (b) sparse-pick `fn-pair` cell | yes: `sp`, `(?i)azqb` (KA `Z`, KB `Q`) |
| Regimes: 64 KiB and 1 MiB, hit-sparse and hit-dense; span ladder; spacing ladder 8..256 B | yes (§3). Plus short75 and R-1's bench subjects |
| Measure the public search entry on the emitted artifact, not a hand copy | yes: `rx_search` / `rx_next_pos` linked from the artifact. No FUNC is copied |
| tb_r4b.c's calibration: loops ≥ ~50 ms, interleaved, repetitions, median with spread | yes: the same tmeasure shape, 3 loops, 3 launches, median plus spread |
| `taskset`, cpu list a parameter, default 12-15 | yes: `--cpus` / `RQ4_CPUS`. The spec's one-logical-CPU rule is NOT applied, because the brief named a list. Siblings are recorded and gated |
| Raw TSV per reading; a table script with three arms, D−K and ON−OFF with null bands and a sign verdict; regime and CPU class named | yes: `raw.tsv`, `rq4_table.py`, header `cpu_class zen4` |
| Under probes/rq4/ with CLAUDE.md, probes/CLAUDE.md updated, house header style | yes. The neighbours carry no SPDX line, only a descriptive header comment, and that style is followed |
| slot20/run.sh: START with tip, stage lines with rc, trap → verdict.txt + FAILED, DONE; detached; wall time stated; outputs under slot20/ | yes (§1, §5); the detached launch was tested on a copy |
| Dry run, labelled, times recorded | yes (§6) |
| Forbidden runs avoided | yes: no full timing, make test, test-axes, emit_sweep, G2 or mech. Only `make -j4`/`-j16` light builds and single pcrec compiles |

## 8. Commits

- `1388626a`: the WIP harness (cells, driver, runner, table).
- The final commit: the KA/KB extraction by register name (exact KB has no
  `mb`), the CLAUDE.md files, and this report.
