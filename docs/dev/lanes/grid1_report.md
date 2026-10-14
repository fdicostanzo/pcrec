# grid1 — the joint timing slot for costmodel §F rows F1, F2 and F3, BUILT and CHECKED (not run)

Lane grid1, 2026-10-13, branch `lane/memfn-grid1` (cut from the kit branch
`lane/memfn-r17` at abfece617).

**No timing run.** The lane built and checked the slot and stopped there. The kit
manager launches it later, on a quiet box.

What the lane did:
- **Compiles.** It built `make -j4` in this worktree for the `quad` cell's artifact,
  and the per-arm `gcc` compiles.
- **Checks and counts.** It ran the correctness legs, the plants, and counting
  builds with no clock.
- **Estimates and dry runs.** It ran `--estimate` and a DRY slot with no clock.
- **Nothing in the compiler moved.** Nothing under `src/` or `memfn/src/` changed.
  No pcrec byte moved, and there is no abi event.

Everything the slot produces lives in `worktrees/memfn-slot/grid1/` (`$OUT`) and is
not committed. The scripts and the arm contract are in `docs/dev/lanes/grid1/`; its
`README.md` is the contract.

## Summary

1. **Design.** Three F1 cells, chosen against costmodel's regimes (§1.1):
   - `dig` (PF, 1 term) is the primary cell and runs every axis;
   - `dfa-hat` is the DFA hat (2 terms);
   - `bounded` is the PF run-consuming `[a-z]` set, the dense-prose loser.

   The core axes are landing gap g ∈ {2,4,8,16,32,64,256,∞} × call span
   L ∈ {32, 1 Ki, 64 Ki}, find-all, repeated 64 KiB. The streamed axis is 64 MiB of
   distinct buffers. The full L axis {8,32,128,1 Ki,64 Ki} runs at g ∈ {4,64}, and
   `first` runs at L ∈ {8,32,128}.

   The kit axes:
   - lengths {48,63,64,65,128};
   - g = 64;
   - start alignment {0,7,31} mod 32 on S1/S2/A1/A2;
   - gap shape (regular/uniform/bursty) at g ∈ {8,32}, both repeated and streamed.

   Forms: walk, V1, S1, A1, V3, S3, A3, and **stateless sse2/avx2** (`Sn`/`An`, a new
   `mkvar.py` arm). F3 runs 1-, 2-, 3- and 4-term cells (`dig`, `hex-run`,
   `word-eq`, `quad` = `[0-9A-Fa-f_]+=`) on member-free 64 KiB and 1 MiB subjects
   under 8 widths/forms.
2. **Rows.**
   - F1: 141 groups, **983 timed rows** (+141 A/A rows), 6,325 launches.
   - F3: 8 groups, **64 rows**, 400 launches.
   - F2: 72 (cell, subject, arm) perf cells × 3 launches.
3. **Estimated wall:** F1 75.5 min + F3 4.3 min = **79.9 min**, plus F2. F2 is
   skipped here; on a box where perf is allowed it takes about 1-2 min. The estimate
   uses SEC_REP = 0.65 s per launch and SEC_STREAM = 0.95 s (measured: 0.45-0.97 s
   per launch). Quiet-gate waits are extra. I cut F1's fraction (§2) to get under
   90 min.
4. **The check is GREEN.** 6,287 legs OK and 0 FAIL, including 112 landing-fidelity
   rows. Nothing is excluded or unreached.
   - O = 167: python `re` against each base.
   - R = 1,101 and L = 1,101: arm against base, by answer and by full match list.
   - C = 252: streamed-cursor fingerprints.
   - Deep legs: E 325, N 325, F 91, A 2,925.
   - U = 167 site rows reached; G = 112 landing-fidelity rows.
5. **Plants: 14 of 14 DETECTED.** There is at least one plant per leg: six
   vecspike-shape art plants, two new stateless-arm plants, the driver's cursor,
   the base walk (leg O), an ext arm (leg R), the generator, reach (leg U), and
   landing fidelity (leg G).
6. **F2 skips loudly.** `perf_event_paranoid=4` here, so `perf stat` is denied.
   `f2perf.sh` checks the permission first and writes
   `F2_SKIPPED perf_event_paranoid=4: perf stat denied ...` to the status file. It
   does not try to change the setting.
7. **The arm contract** is implemented, documented (`grid1/README.md`) and proven
   end to end with a worked external set (`grid1/ext_example/`). That run covered
   its own subjects (`gen_subj`), its own cell, a streamed subject, legs R, L and C,
   `--estimate` and a DRY EXT phase. The set was then removed so the slot is clean
   for `slotarms`.
8. **The slot ran end to end in DRY mode.** It covers F1, F3, F2 (skipped, loud),
   EXT none and SLOT_DONE, with 0 answer mismatches over 1,266 launches. The
   stale-check refusal was also exercised.
9. **Three findings changed the design** (§5):
   - With letter filler, the dfa-hat site never saw its landings; leg G caught it.
   - Member-free subjects of `dig`, `word-eq` and `quad` never reach the site (the
     required-byte pre-check answers first), and §F's own F3 subject names have the
     same problem.
   - Streamed buffers repeat their match offsets, so an answer hash cannot show that
     the driver cycles.

**Launch** (after `slotarms` adds its set and the manager re-runs `build.sh --ext`
and `check.sh`):

    setsid nohup bash /home/pcrec/projects/pcrec/worktrees/grid1/docs/dev/lanes/grid1/slot.sh >/dev/null 2>&1 </dev/null &

The status file is `/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid1/slot.status`
(SLOT_START … SLOT_DONE).

## 1. Design

### 1.1 Cells, against costmodel's regimes

| cell | site / terms | why |
|---|---|---|
| `dig` `[0-9]+x` | PF prefilter set find, 1 term (range) | Landing and match separate cleanly. An isolated digit is a landing whose verify fails within 1 byte; `Nx` is a match. It is costmodel's main 1-term cell (β_f measured on it), and it covers all three regimes. Every axis runs here. |
| `dfa-hat` `\b(?:true\|false\|null)\b` | the DFA hat, 2 terms (cube f/n + eq t) | The required hat cell. It is the TUG cell (§A.3) and the 1 MiB miss (§A.4). Its landings are word-initial near hits (` t.`). |
| `bounded` `[a-z]+\b` (`--features all`) | PF, a run-consuming set | The "PF sparse-set" cell the brief asks for. It is the largest ALPHA loss (`prose1m all` +599 µs, DINGHY). A landing is a letter followed by a digit (`\b` fails); a match is a letter followed by a space. L = 8 is its prose regime. |
| F3: `dig`, `hex-run` `[a-f0-9]+`, `word-eq` `[A-Za-z_]+=`, `quad` `[0-9A-Fa-f_]+=` | PF, 1 / 2 / 3 / 4 terms | The per-byte rate β_f by term count on one run. §A.1's 3-term entry is DERIVED and the 4-term entry is missing. `quad` is the one 4-term cover the kit branch emits (probed), built with this worktree's `build/pcrec`. |

`hex-run` was not chosen for F1: every member starts a match, so it can have no
landing. `vm-hat` was not chosen: costmodel §B.2 says a VM-hat use costs about
nothing over the walk and wins at every gap.

### 1.2 Subjects (`grid.py`, declared tables)

- **Landing.** A member byte that does not start a match. It has filler on both
  sides, so the attempt fails within 1-2 bytes: a minimal-verify landing.
- **Match.** A token planted at the end of every L-byte window. L ≥ n means one match
  at the end of the subject; L = none means no match.
- **Landings vs matches.** They are controlled separately: λ = 1/g and α = 1/L.
- **Gap shapes.** `u` is the default: i.i.d. gaps uniform in
  [max(2, g − g/2), g + g/2]. `reg` is exactly g, and g = 2 is always `reg`.
  `burst` is 8 landings 2 bytes apart, then one gap closing the 8g period.
- **Collisions.** A landing that would touch a token or another landing is
  **dropped**. The planted counts are recorded in `subj_facts.tsv`, never assumed.
- **Generator self-check.** python `re` must find exactly the planted matches. A
  member-free subject must hold no member byte and must hold its required byte.
- **Streamed (`-S`).** 1,024 distinct 64 KiB buffers (64 MiB, larger than the 7700X's
  32 MiB L3), each from its own seed. Distinctness is checked by sha256.
- **Placement.** Every buffer is placed 64-aligned + `GRID_OFF`.

There are 134 synthetic subjects (106 repeated, 28 streamed, 1.8 GB), plus the six
real 64 KiB/1 MiB subjects for F2, copied from spike1.

### 1.3 Forms (arms)

- **From the spike's generator.** The arms come from the spike's generator, copied
  into `grid1/mkvar.py` over the R17-b artifacts. These are slot25c ALPHA's `new`
  and `deny` artifacts, and `quad`'s from this worktree.
- **The generator's arms.** `walk` (= `deny`, the base), `V1` (= `new`), `G1`, and
  the derived arms V2, V3, S1-S3, A1-A3.
- **New arm: stateless sse2/avx2** (`v16n`/`v32n` → `Sn`/`An`). It is the W = 64
  block with **no cache**: every use rescans from `lo`.
- **G1 control.** `G1 == V1` assembles identically on all six cells.
- **same_first.** It marks 0 of 18 keep arms. No kept form assembles to its unkept
  twin.

### 1.4 The fractional design and what each block answers

| block | cell | mode | groups | arms | rows | answers (costmodel terms) |
|---|---|---|---|---|---|---|
| D1 core-rep | dig | all | 24 (8 g × L 32/1Ki/64Ki) | 9 | 192 | At fixed L (α), g moves λ (uses per byte): the **warm per-use cost** against the **per-byte rate** (c_warm vs β_t − β_f), so g\* = 18.5 B is bracketed (16/32). At fixed g, L moves α: the **cold per-activation cost** (c_cold, overscan 4.7 B vs 59 B). L = 32 is DINGHY, 1 Ki is TUG (g < 18) or LINER, 64 Ki is one long call. |
| D2 core-stream | dig | all | 12 (g 2/8/32/256 × 3 L) | 9 | 96 | The **fresh-subject term** m: D1's cells with distinct data past L3. |
| D3 span | dig | all | 4 (g 4/64 × L 8/128) | 4 | 12 | §F's full L axis (with D1's 32/1Ki/64Ki) on walk/V1/A1/A3: the c_cold line by width, and the DINGHY/TUG boundary L\* = 64. |
| D4 first | dig | first | 9 (g 2/8/∞ × L 8/32/128) | 6 | 45 | One call of span L with g landings inside it: **C_call vs C_use** (regimefacts §4 gap 1), the single-call dinghy loss (costmodel §B.4). |
| D5 len | dig | first / all | 5 + 5 (n 48/63/64/65/128) | 6 / 9 | 65 | The **sub-block tail** around one W = 64 block (regimefacts §4 gap 2; costmodel §B.4's 40 B rows). Member-free single call, and dense find-all. |
| D6 align | dig | first / all | 9 (3 points × off 0/7/31) | 5 | 36 | The **prologue arms** (S2/A2) against S1/A1 by start alignment: a member-free liner call, a 65-byte call, and a TUG find-all. |
| D7 shape | dig | all | 8 (g 8/32 × reg/burst × rep/stream) | 9 | 64 | Gap **shape** at equal mean, against D1's/D2's `u`. Streamed `reg`/`burst` buffers repeat their landing offsets (only the bytes differ), while streamed `u` varies them. The pair splits the **cache/DRAM** part of "fresh" from the **branch-predictor** part (§5.3). |
| H1 core-rep | dfa-hat | all | 24 | 9 | 192 | D1 for the hat (the TUG cell). |
| H2 core-stream | dfa-hat | all | 8 (g 2/8/32/256 × L 1Ki/64Ki) | 9 | 64 | D2 for the hat at TUG/LINER spans, where its 1 MiB miss lives. |
| H3 span | dfa-hat | all | 4 | 4 | 12 | D3 for the hat. |
| H4 first | dfa-hat | first | 9 | 6 | 45 | D4 for the hat. |
| B1 core-rep | bounded | all | 16 (g 2/8/32/∞ × L 8/32/1Ki/64Ki) | 9 | 128 | The dense run-set loser. L = 8 is its prose regime (a dinghy pass, the +599 µs row). |
| B2 core-stream | bounded | all | 4 (g 2/32 × L 8/1Ki) | 9 | 32 | Fresh data on the dinghy pass. |
| F3 | f3-dig/-hex-run/-word-eq/-quad | first | 8 (4 cells × 64 KiB/1 MiB) | 9 | 64 | **β_f at 1, 2, 3 and 4 terms** per width (SWAR, SSE2, AVX2, ±prologue, stateless) on one run. This replaces §A.1's DERIVED 3-term rate and supplies the missing 4-term rate, which moves §B.2's SWAR crossovers (15.6 → 26 → 65 B). |
| F2 | hex-run/bounded/dfa-hat × prose/docs/code 1m and 64k | all | 18 | 4 | 72 cells | **Branch misses per pass** at 1 MiB against 64 KiB (the learned-predictor control): makes m_fresh a counted term (costmodel §A.4). |

Every cell also gets counters with no clock (`counts.tsv`, 1,268 rows): calls, uses,
cold, cache hit/pass, xcall, skipped, head, blocks and nbuf for every arm, plus the
site's own counters (`site(G1)`). So λ, α and the overscan are read per row, never
assumed.

**Near-hit depth is not an axis.** Every landing is minimal-verify (1-2 bytes; the
hat's is a word-initial ` t.`). The brief's "near hits are the loss mechanism" is
covered as landing density. How long a near hit runs before failing is uncovered;
it is the F8-shaped question.

## 2. Cuts (to fit 60-90 min)

The uncut design, with every block as in §1.4 plus `first` at L = 1 Ki and kept twins
in `first`, was **86.8 min** for F1 + F3. It was cut as follows:

- **Kept twins (V3/S3/A3) are dropped from every `first`-mode block** (D4, D5-sparse,
  H4; 87 launches per round). One call keeps nothing. In `first` the kept artifact
  runs `rx_search`, the same algorithm as its unkept twin, with an unused state
  pointer (costmodel §0.5: "KEEP and the prologue cannot help" a single call). The
  twins do not assemble identically (same_first marks 0 of 18), so the cut is a
  judgment and is labelled.
- **`first` at L = 1 Ki is dropped** (D4, H4; 42 launches per round). D1/H1's
  find-all at L = 1 Ki is 64 calls of span 1 Ki, the same call shape.
- **Already fractional from the start, against §F's "9 forms × 8 g × 3 L × 2 reuse":**
  - streamed runs at g ∈ {2,8,32,256}, not all 8 g;
  - H2 uses L ∈ {1Ki, 64Ki};
  - B1/B2 are reduced as listed;
  - the span axis carries walk/V1/A1/A3 only, as §F states.

Result: **79.9 min** for F1 + F3 (F1 75.5, F3 4.3), plus F2 when perf is allowed.

## 3. Row counts and the estimate

From `OUT=$OUT bash time.sh --estimate`:

    estimate F1  groups=141 rows=983 launches=6325 wall=75.5 min (+ quiet-gate waits)
    estimate F3  groups=8 rows=64 launches=400 wall=4.3 min (+ quiet-gate waits)
    estimate EXT groups=0 rows=0 launches=0 wall=0.0 min (+ quiet-gate waits)
    estimate ALL groups rows=1047 launches=6725 wall=79.9 min

- A row is (cell, subject, mode, arm), A/A excluded.
- Each group launches its base twice per round, for 5 rounds.
- The ext arms that `slotarms` adds will extend this. Re-run `--estimate` after
  `build.sh --ext`; `slot.sh` writes its own ESTIMATE line to the status file.
- The worked ext example (6 groups, 2 arms) estimated 1.1 min.

## 4. The gate: check.sh and plants.sh

`check.sh` runs in 73-81 s. Its last run:

    arms: 77 (cell, arm) pairs, 167 groups, 1268 items, 0 problems
    landing fidelity (G): 112 ok, 0 FAIL
    reach (U): 167 site rows, 0 unreached
    legs OK:   6287   (O 167  R 1101  L 1101  C 252  E 325  N 325  F 91  A 2925)
    legs FAIL: 0
    excluded (cell arm): 0

The legs (definitions in `check.sh`'s header):

| leg | what it checks |
|---|---|
| O | each base against python `re`, independent of pcrec |
| R | each arm's `matches/hash` against its base |
| L | full match lists, per buffer when streamed |
| C | the streamed cursor visits every buffer once, in order (content fingerprints) |
| E, N, F, A | the vecspike deep legs over the generated arms: every-startpos, random startpos, fuzz slices at 64 base offsets, and ASan+UBSan with mkvar's VS_DEBUG re-probe at (OFF, CUT) ∈ {(0,0) (1,1) (13,29) (31,7)} |
| U | the site is reached |
| G | the site's uses equal the planted landings + matches |

Results go to `excluded`, `unreached` and `landing_fidelity`.

`plants.sh` (`plants: ALL DETECTED`, 14 of 14):

| plant | what is broken | detected by |
|---|---|---|
| lowerbound (hex-run V3) | cache test without its lower bound | A |
| overread (dig V3) | tail block one byte late | A (ASan) |
| headoff (dfa-hat V2) | prologue answers one past | E/A |
| lanes16 (hex-run S1) | SSE2 lane shift | E/L |
| lanes32 (dig A3) | AVX2 lane shift, kept form | E/L |
| noaligntest (word-eq A2) | unaligned "aligned" load | E (SIGSEGV) |
| sntail (bounded Sn, new) | stateless tail shift | E |
| anlanes (dfa-hat An, new) | stateless AVX2 lane shift | E |
| drvcycle (gdrv.c) | streamed loop re-times buffer 0, answers unchanged | C (16 FAIL) |
| walktable (dig walk) | base start table drops '7' | O (47 FAIL) |
| extwrong (an ext arm, `run` only) | ext arm answers wrong | R |
| gentoken (grid.py) | a match token that does not match | the planted-count self-check |
| reachgate | a member-free subject lacking `x` | U |
| letterfill | dfa-hat landings in letters | G (uses 128 vs planted 8,188) |

## 5. Findings

1. **The dfa-hat site never landed on its own landings in a letter filler.** The
   first design used letters as filler. There, the site counted exactly 2 uses per
   find-all call at every g (`uses=128` for 64 calls, from g = 2 to g = 256):
   - the hat is the scan the DFA's start state runs;
   - inside a word the DFA walks the letters itself;
   - so a mid-word `t` is consumed by the DFA, not landed by the hat.

   The g axis did nothing for that cell. The filler is now non-word bytes, so a
   landing is a word-initial near hit (the prose case). Leg G now holds every
   find-all row to its planted counts: 112 rows, all within 10%, most exact. A plant
   proves G fires. Without counters on every cell this would have shipped as 192
   meaningless H1 rows.
2. **Member-free subjects never reach the site** for any cell with a required byte
   outside its set: `dig` needs `x`, `word-eq` and `quad` need `=`. The artifact's
   whole-window pre-check answers before the PF scan runs (`uses=0`). This affected
   F3 and D5-sparse; they now carry the required byte in their filler (per-cell
   `REQ`), and leg U lists any site row with `uses=0`.

   §F's F3 subject suggestion, "digits64k, prose1m", does not work for these cells:
   - for `word-eq` neither subject is member-free (`x` and every letter are
     members);
   - for `dig`, a subject without `x` times the pre-check.
3. **Streamed buffers repeat their match offsets** (the L-grid is the same in every
   buffer). For `reg`/`burst` and g = 2 they also repeat their landing offsets;
   only the bytes differ. Two consequences:
   - An answer hash cannot show that the driver cycles: a cursor stuck on buffer 0
     answers identically. Leg C folds content fingerprints instead, and the
     `drvcycle` plant was UNDETECTED by the first, hash-based version of leg C.
   - `-S` rows for `reg`/`burst` isolate cache/DRAM freshness, while `u` streams
     add branch-predictor freshness. D7 pairs them on purpose.
4. **Placement differs from slot25c/spike1.** Their `drv.c` used `malloc`
   (16-aligned heap at 64 KiB, page+16 mmap at 1 MiB). Grid1 places every subject
   64-aligned + `GRID_OFF` (default 0). D6 measures the offset sensitivity directly.
   Do not compare a grid1 absolute ns with a spike1 ns at the same nominal cell
   without that caveat.
5. **No kept form assembles to its unkept twin's `rx_search` in `first` mode**
   (same_first 0 of 18, against the spike, where some did). That is why the
   `first`-mode keep cut is labelled a judgment (§2).

## 6. The arm interface (for lane `slotarms`)

`grid1/README.md` is the contract. In short:

- **Tables.** `arms.tsv` rows are `cell arm role subjects modes`. Rows add up, there
  is exactly one base per cell, and subject tokens are `NAME[@OFF]`.
- **run.** `$OUT/bin/<cell>/<arm>/run SUBJECT first|all` prints
  `matches=N hash=H ns/pass=X` with drv.c's method. `SUBJECT` may be a file, a
  directory or a `*.list` manifest (the streamed case). The binary must honour
  `GRID_OFF` and `GRID_FIXED=N`, which prints `passes`, `cycle` and `cycleexp`.
  Linking `$OUT/lib/gdrv.c` meets all of this.
- **Optional twins.** `cnt` (last stderr line `key=value`, recorded verbatim) and
  `chk` (enables leg L).
- **Ext sets.** `$OUT/ext/<name>/{arms.tsv,build.sh[,gen_subj]}`. `gen_subj` writes
  `$OUT/subj/<name>_*`.
- **Phases.** The EXT phase is for cells whose base an ext set declares. An arm
  joined to an own cell is interleaved in F1/F3.
- **Streamed opt-in.** An arm set opts in by listing a `-S` directory; linking
  `gdrv.c` makes the driver cycle, and leg C checks it.

`grid1/ext_example/` is a worked set: `ex-dig`, pcrec `[0-9]+x` default against
`--memfn=no-pf-terms-mask`, linked with `gdrv.c`, with its own `gen_subj`. Run once
through the whole pipeline, it gave:
- `build.sh --ext` built it;
- the check passed: R 6, L 6, C 4, 0 FAIL;
- `--estimate` showed EXT 6 groups;
- a DRY EXT phase read COMPLETE rows=12.

It was then removed from `$OUT`, and the check re-run clean.

## 7. Launch, status, what is owed

- **Launch:**

      setsid nohup bash /home/pcrec/projects/pcrec/worktrees/grid1/docs/dev/lanes/grid1/slot.sh >/dev/null 2>&1 </dev/null &

  - Defaults: `CPU=14 LAUNCHES=5 LOADMAX=1.5`.
  - It waits up to 30 min for quiet (`START_WAIT`).
  - It refuses if `check.log` is older than any arm table, ext file or binary, or if
    anything is excluded (`ALLOW_EXCLUDED=1` overrides).
- **Status:** `$OUT/slot.status`.
- **Logs:**
  - `$OUT/time_F1.log`, `time_F3.log`, `f2.log`, `time_EXT.log`;
  - raw per-launch values in `$OUT/time/raw_<PHASE>.tsv` and `$OUT/f2/raw.tsv`.
- **Completion lines:** `time.sh: COMPLETE rows=N wall=Ns` per phase, and
  `SLOT_DONE` in the status file. `$OUT/SLOT_DONE` is also touched.
- **Before launching:**
  1. `slotarms` writes `$OUT/ext/<name>/`.
  2. Run `OUT=$OUT bash build.sh --ext`.
  3. Run `OUT=$OUT bash check.sh` (about 80 s; it must end with
     `excluded (cell arm): 0` and `landing fidelity (G): ... 0 FAIL`).
  4. Optionally run `OUT=$OUT bash plants.sh`.
  5. Run `OUT=$OUT bash time.sh --estimate`.
- **F2 needs a ruling.** It runs only if Frank lowers `perf_event_paranoid` (≤ 2 for
  user `:u` events), or if the slot is run under a user allowed to use perf.
  Otherwise the status file says `F2_SKIPPED perf_event_paranoid=4 ...`.
- **Owed:** the timing itself, which is the manager's slot. Nothing else.

## 8. Charter vs committed

| charter item | committed |
|---|---|
| F1 controlled grid: g ∈ {2..∞}, L ∈ {8,32,128,1Ki,64Ki} find-all + `first`, reuse rep/stream 64 MiB, the 9 forms, fractional per §F | §1.4 (D1-D7, H1-H4, B1-B2); fractions and cuts in §2 |
| Cells: at least one PF sparse-set cell and dfa-hat, justified against regimes | `dig` + `bounded` (PF) + `dfa-hat`, §1.1 |
| Landings and matches controlled separately; candidate density ≠ match density | §1.2 (λ = 1/g, α = 1/L planted separately); leg G holds landings to the counters |
| Kit axes: lengths {48,63,64,65,128}; g = 64; alignment {0,7,31} for A2/S2; gap shape | D5, D1/D3 (g = 64), D6, D7; row count §3 |
| F2 perf script, permission-checked, skip loud | `f2perf.sh`; exercised: `F2_SKIPPED perf_event_paranoid=4 ...` |
| F3: 3- and 4-term sparse sets | F3 block (with 1-/2-term controls on the same run); `quad` built by this worktree's compiler |
| Stateless sse2/avx2 arm in mkvar.py, G1 control still holds | `v16n`/`v32n`; G1 == V1 on all 6 cells |
| Arm interface: arms.tsv, run/cnt contract, subjects, gen_subj, ext sets merged by time.sh and built by build.sh, streamed directory/manifest | `README.md`, `arms.py`, `gdrv.c`/`gload.h`; proven by `ext_example/` |
| Harness: interleave, LAUNCHES, taskset, median over launches, per-launch values recorded, LOADMAX gate, counters on every cell, `--estimate`, completion line | `time.sh` (rotated rounds, `raw_<PHASE>.tsv`, quiet gate, `--counts`, `--estimate`, `DRY=1`) |
| slot.sh: F1, F3, F2 (skip-loud), ext; status file; launchable detached | `slot.sh`; DRY end-to-end run SLOT_DONE; refusal exercised |
| Correctness gate: answers = walk's on every subject and mode, plants detected, `excluded` file | `check.sh` (O R L C E N F A U G), `plants.sh` 14/14, `excluded` empty |
| ~60-90 min target; cut and say what | 79.9 min (+F2); cuts in §2 |
| Commit scripts, README, report; CLAUDE.md line; slot dir built and checked | this branch; `docs/dev/lanes/CLAUDE.md` + `grid1/CLAUDE.md`; `$OUT` built, checked, planted |
| No timing run, nothing under src/ or memfn/src/, no byte move | held (counting builds and DRY runs only) |
