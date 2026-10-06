# ARTREV A09 — loglines_level_context — review (rvA09)

Pattern `\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b`,
pin 57db5152 (abi 62), gcc-16 -O2, hybrid: DFA prefilter over the count-collapsed
language, then a backtracking VM attempt at the window start. Losing cell (~x3.8).

**No timing was run** (brief: suite lock held, load above the gate). Every lead is
"scratch timing owed". Effects are ranked from work counts. I took the counts with an
instrumented scratch copy (`tools/mkcount.py`, `tools/count_drv.c`), plus a reading of the asm.

## 1. What the artifact does, as read

- `rx_search` → `rx_search_run`:
  1. A `memchr(subject+from, 'e')` presence check (`e` is the required byte; every keyword has one).
  2. `rx_prefilter` runs an unanchored forward DFA (44 states, 29 classes, premultiplied
     `unsigned short` table) to the first accept. It then runs a reverse DFA back from the accept
     to find the window start.
  3. `rx_match_anchored` (VM) runs at the start. If it fails, `attempt+1` and the prefilter runs
     again from there. The window end is ignored ("cut-bearing artifact").
- The forward DFA, dumped with `tools/dfa_dump.py`:
  - States 0 and 29 are the "searching" component. 0 is after `\W`, 29 is inside a word.
  - 58..377 are the level-literal prefixes. 319 means a whole level was just read.
  - 406/435 are the after-level `[^\n]*` component, with the same 0/29 shape.
  - 464..1247 are keyword prefixes. 1044 means a whole keyword was just read; on `\W` it
    accepts and the next state is dead. `\n` sends every after-level state back to 0.
- The VM tests `\b`, then the level (switch on the first byte, 2/4-byte compares). It tests
  `\b` again, then runs the lazy `.{0,200}?` with **one resume frame per position**: push,
  try `\b`+keyword, fail, pop, step. Captures are trailed (`RX_SET` of slot 2 for the
  200-count). Run counters (`resume_depth`, `trail_depth`, `steps_left`, `work_left`) live in
  `run->` memory.

### Which subjects set the cell

| per MiB (find-all) | fail | syslog | hit |
|---|---|---|---|
| matches | 0 | 0 | 193 |
| level words (`\bLEVEL\b`) | 0 | 0 | 386 |
| forward DFA steps | 1,000,308 | 1,010,568 | 992,955 |
| state-0 skip-loop bytes | 48k | 38k | 55k |
| reverse DFA steps | 0 | 0 | 12.4k |
| VM lazy positions | 0 | 0 | 8.1k |

All twelve subjects pay the same thing: **one DFA step per byte**. The state-0 skip almost
never fires, because a word byte takes 0 to 29 and the next `\W` takes it back. So the skip
only covers runs of two or more non-word bytes.

The step loop (asm `L11`/`L15`/`L5`) is about 20 instructions per byte. Its loop-carried
chain is state → `add` → `ldrh`, roughly 5-6 cycles per byte, latency-bound. The VM and the
reverse pass are about 2% of the hit group's work under the original.

Once the scan is fixed, fail and syslog become the cheap groups and hit the expensive one.
Positions 6-7 of the sorted twelve then fall in the slower of fail/syslog (syslog: 2.8k vs
2.0k memchr calls per MiB). **So only the scan leads (L1/L2) can move the cell.** L3-L5 are
hit-group and generality leads.

## 2. Leads

All six are sealed. All six PASS identity plain and `--san` on the final set: 413 supplied
subjects (12 throughput + 112 search + 289 edge) plus the 3000-case battery and the libpcre2
sample. Two scratch differentials (section 4) back them up.

### L1 — skip the searching component with two literal memchr streams (algorithmic) — r2 sealed

- **Observation.** {0,29} is left only by C/E/F read in state 0, meaning position 0 or after
  a `\W` byte. It reaches 319 only through a whole literal. Nothing accepts in between.
- **r1.** Three memchr streams (C/E/F), with a predecessor test. That leaves 4.7k/8.9k/24k
  DFA steps per MiB, but scans 3 MiB per MiB with 5.4k/4.4k/7.5k calls.
- **r2 (sealed).** Two streams on rare bytes: `O` (ERROR+3) and `T` (FATAL+2, CRIT+3). Each
  hit is verified by compares and the `\W` predecessor test. Each stream caches its next
  verified start across the call. The DFA is then entered in state 0 at that start. Result:
  2 MiB scanned; 2.0k (fail) / 2.8k (syslog) / 6.6k (hit) calls per MiB; zero DFA steps on
  fail/syslog.
- **Why `O`/`T`.** These are the cheapest cover on these subjects. `R`+`L` is worse on syslog
  (R = 5,008/MiB). No byte is common to all three literals. This is a measured byte-frequency
  choice; the idea of picking the rarest byte came from the rvA01 notebook entry.
- **Expected effect.** At least 10x on the prefilter. Scratch timing owed.
- **Controls that FAIL:**
  - `ctlnb` (r1 with no word-start test).
  - `ctlnof` (F stream ignored).
  - `ctlnb2` (r2 FATAL with no word-start test). Only an A09 edge subject catches it.
  - `ctlbnd` (r2's `x+3<=n` bound dropped). It PASSES plain and FAILS only under ASan. It needed
    edge subjects that end in a truncated literal (`...FAT`), because the identity driver
    mallocs subjects to exact size.

### L2 — the same skip, pure scalar (algorithmic)

- **The twin.** A 256-byte table loop over {C,E,F} with the predecessor test. No memchr.
- **Effect.** 1.0M DFA steps per MiB drop to 4.7k/8.9k. The loop body is 7 instructions per
  byte with no state chain. Estimate about 3x on the prefilter.
- **Why it exists.** It splits L1's gain into "component skip" and "memchr". It is also the
  form an emitter can produce with no new kernel.

### L3 — skip the after-level component {406,435} (algorithmic)

- **Observation.** The emitted `stay14` loop covers 406's self-loop only.
- **The twin.** The exit table is {`\n`,d,r,t,u}. At an exit byte, the predecessor decides
  whether the state is 406 or 435.
- **Effect.** Hit only: about 14k DFA steps per MiB removed (L6's residual is 5.9k).
- **Control.** `ctlL3` (word-start test dropped) FAILS.

### L4 — the hybrid re-proves the DFA's answer (redundant-work) — r3 sealed

- **r1.** The window start is the last position where the DFA was in 319, minus the literal
  length (4 if `s[p-1]=='T'`, else 5). That replaces the reverse pass. The after-level region
  is entered only from 319 and left only by `\n` or death.
- **r2.** Skip the VM when the window is provably its answer. The test: the keyword (found by
  suffix match at the window end) starts at most 200 bytes after the level end. The guards:
  `steps_left > 256` and `work_left > 2048`, since one attempt spends at most 201 steps and
  1,021 work units.
  - **r2 PASSED harness identity but was WRONG.** With `_in` buffers of 0 frames or 0 trail,
    the original gives up with `PCREC_ERR_FRAMES` (-3). r2 returned the match instead: 284k
    differences in my capacity differential. The harness shim only ever passes the stamped
    default buffers, so harness identity cannot see this.
- **r3 (sealed).** Adds `trail_depth < trail_cap && resume_depth < resume_cap` to the fast
  path's guard. 0 differences.
- **Effect.** On hit, 12.4k reverse steps and 193 VM attempts per MiB go to 0.
- **Controls:**
  - `ctlL4` (CRIT start one late) FAILS.
  - `ctlL4e` (one early) FAILS only by the identity driver's 900 s timeout. An early start
    livelocks `rx_search_run`: the prefilter from s returns s-1, the VM fails, it moves to s,
    and the cycle repeats. My window differential flags it at once (43,843 start differences).
  - `ctlgap` (bound 201) PASSED until I added exact-gap edge subjects (gaps 199-202 for every
    level×keyword pair). It FAILS now.

### L5 — frameless lazy step (control-flow)

- **The twin.** Drop `RX_PUSH(&&rx_L16)`. Keep the capacity check and the per-position
  `--steps_left` in the original order. Point the 10 keyword-failure `goto rx_fail` at
  `rx_L16`.
- **Checks.** Exact under the budget/capacity differential: 6 budget pairs × 4 buffer shapes.
- **Effect.** About 45 → 25 instructions per lazy position. Moot under L4 r3, which keeps
  only VM attempts that fail or whose gap does not fit, so it matters only for those.

### L6 — combination L1 r2 + L3 + L4 r3 + L5, for the confirmer

- **Residual per MiB.** fail: 2.0k memchr calls. syslog: 2.8k. hit: 6.6k memchr calls plus
  5.9k DFA steps.
- **Rebasing.** L4's first hunk needed a hand rebase onto L1's declarations. The other patches
  applied cleanly.

**Expected order on the cell (subjects that set the median):** L6 ≈ L1 ≫ L2 ≫ L3 = L4 = L5 = null.
**On hit:** L6 > L1 > L4 > L2 > L5 ≈ L3.

## 3. Rejected / not carried

- **Drop or replace the `'e'` presence memchr.** Negligible: it finds an `e` within about 15
  bytes, once per search call (193/MiB on hit).
- **A single memchr stream.** No byte is common to ERROR, FATAL and CRIT.
- **`R`+`L` streams.** Syslog has R = 5,008/MiB, so this is worse than `O`+`T`.
- **Tightening the per-step DFA loop** (the accept-by-class load each step, the
  re-materialized `@PAGEOFF` adds, the 406 compare in the loop head). After L1 the loop does
  not run on the median's subjects, and before L1 it is latency-bound on `ldrh`. This agrees
  with rvA01.
- **SWAR or word-at-a-time scanning of the component.** Excluded by the rules.
- **Localizing the run counters in the VM** (rvA07a's L6). Real, but the VM is about 2% of
  the original hit work and about 0% under L4 r3.
- **Find-all restart cost** (`rx_run_state_init`, buffer bind, re-priming two streams per
  call). About 193 calls/MiB; negligible.
- **Using the uncut window end as a VM bound.** Unsound in general (the artifact says so).
  L4 r2/r3 instead checks the count explicitly.

## 4. Identity method and harness notes

- **Supplied subjects.** The 12 throughput and 112 search subjects, plus 289 A09 edge
  subjects. The edge subjects come from `edge_subjects/gen_edge.py` (seed 9, deterministic):
  token soup from literal fragments, truncated literals at the subject end, and exact
  `.{0,200}` gaps of 199..202.
- **Battery.** 3000 cases at block 16, with `--match-example 'ERROR x timeout'` and
  `'CRIT timed out'`.
- **Window differential** (`tools/pfdiff_*`). Compares `rx_prefilter`'s return and window
  START, orig vs twin, at every `search_from` (step 7 on large files), under ASan/UBSan. This
  is strictly stronger than answer identity for prefilter twins. A start that is too early is
  invisible to answers (the VM retries) and shows up only as work or a livelock.
- **Budget/capacity differential** (`tools/budget_*`). Orig and twin are rebuilt with
  `RX_STEP_BUDGET`/`RX_WORK_BUDGET` shrunk (7..500M, 3..1e9). They are compared through
  `_search_in`/`_match_in` with 0/1 frames × 0/1 trail and through `_search`.
- **Harness gap, for the manager.** The identity shim never exercises `_in` with
  smaller-than-default buffers or small budgets. That is how L4 r2 passed while wrong.
- **Ledger.** 6/6 leads; revisions L1 2, L2 1, L3 1, L4 3, L5 1, L6 1; 0 timing runs.
  The 8 controls are uncounted.

## 5. Disclosure (injected context)

- **Project CLAUDE.md.** I read its scope mandate and the D27 blindness rationale. Its
  emphasis on "general mechanisms, not special cases" may have nudged me to frame L1-L3 as
  "skip a strongly connected searching component" rather than "add a memchr for this
  pattern". Its D26/compat text did not bear on the leads.
- **Memory index.** The entries on "suspect tuning constants" (label unmeasured defaults)
  and "decisions as first-match tables" shaped how I labelled the `O`/`T` byte choice and the
  fast-path guard constants. The constants 256 and 2048 are derived bounds (201 steps;
  5+201·5+11 = 1,021 work units), rounded up. `O`/`T` are measured on these subjects only.
- **Nothing in the injected text named this artifact, its emitter, or any of these leads.**
