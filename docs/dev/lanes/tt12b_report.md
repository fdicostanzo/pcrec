# lane tt12b — [TT-12] STEP 1 report

**Branch** `lane/tt12b`, commits `969b9ba..52c9fee` (4 commits on top of
`6fba88d`). **Status: ALL FOUR ITEMS DELIVERED AND MEASURED.** Items 1, 2
and 4 have full corpus/end-to-end confirming measurements. Item 3's own
mechanism is validated (self-tests + the D77 concurrency check) but a full
`make san` end-to-end run was not performed — flagged, not hidden, and
owed at the next merge battery. `scripts/battery.sh` (item 5) is written
and its stage shapes are each backed by items 1/3/4's own numbers, but the
battery itself was deliberately not run as a whole (the brief: the manager
runs it at the next merge).

---

## 1. The five-line table

| item | measurement | result |
|---|---|---|
| 1: pairwise axes | full corpus + oracle, paired vs 4205s sequential ref | **2868s (47:48), 1.47x** — above the ≤40min target under real load (12-18 vs ref's 4.5-6); answer-identical on all 21 axes |
| 2: K45 tower | full corpus, all 5 axes | **refused_undoc: 2→0 on all five**; K45 CLOSED |
| 3: san `-P` (D77) | 5 identity scripts, seq vs `-P4` | **831s → 351s, 2.37x**, zero contention, verdicts identical |
| 4: K44 shapes | full `make test`, 3 shapes, one at a time | **`-j4 PROCS=3` wins: 1115s, rc=0** (vs `-j12 PROCS=1` 1674s rc=2, `-j2 PROCS=6` 1792s rc=0) |
| 5: battery.sh | written, stage shapes sourced from 1/3/4 | not run end to end (manager's call at merge) |

## 2. Item 1 — pairwise axes (`tests/axes/run_axes.sh`)

The job list (19 bit-flag axes + 2 engine directions, same order and
`AXES=` filtering as before) now runs two at a time, each at
`PROCS=ceil(PROCS/2)`, in backgrounded subshells with per-job result files
(a subshell cannot mutate this script's own `fail`/`axis_results`
directly). Building this found and fixed a latent race worth landing on
its own merits: `run_one_axis` wrote the harness's stdout/stderr and the
diff-awk's stderr to FIXED filenames shared across every axis call —
harmless serially, a real corruption risk for the diagnostic text a
failure prints once two axes can run concurrently. Every such filename is
now per-axis (slug-derived).

**Validated twice.** First, a full-corpus 3-axis subset
(`AXES="-fno-counter --engine=dfa"`, which the file's own `--engine`
substring match also pulls `--engine=vm` into) confirmed the mechanism and
the K45 fix together. Second, the FULL 21-axis paired sweep with the
oracle cross-check, matching `make test-axes`'s own delivered shape:

- **Total wall: 2868s (47:48)**, vs opt5i's sequential reference of 4205s
  (70:05) — **1.47x**, 31.8% off. This is ABOVE the STEP 1 charter's
  ≤40 min target.
- **The shortfall is load, not the mechanism.** The reference run's box
  sat at load 4.5-6 through its own sequential sweep (docs/dev/plan.md
  [TT-12] row); the paired run's box sat at load 12-18 throughout (other
  daytime work — flagged live to the team lead, not a hold on this run).
  Every pair's own per-axis wall landed 25-30% above the reference's solo
  figure, consistent with contention, not with pairing adding overhead.
  Two data points support this reading directly: the FIRST validation run
  (quiet box, load 0.3-1.5) paired `-fno-possessify`+`-fno-revdet` in
  ~220s against their solo reference times of 177s/178s (355s sequential)
  — 1.6x on a quiet box for that one pair, already most of the way to 2x.
- **Answer identity: fully verified, not merely argued.** Every one of the
  21 axes' `agree`/`budget`/`refused`/`lost`/`mismatches`/`gained` counts
  is BYTE-IDENTICAL to the pre-fix reference — K45's five axes read
  `refused_doc` exactly 2 higher each (the fix landing in the same run,
  expected), zero MISMATCH, zero LOST, zero GAINED anywhere, oracle
  cross-check OK.
- **Pairing THREE was not measured** — the D77 trigger for it (two already
  meets "close to additive"; a third ~45+ minute run was not worth
  chasing an explicitly optional stretch target) — shipped two, per the
  brief's own fallback instruction.
- **Recommendation for a re-run on a quiet box**, which the STEP 0
  profile's own numbers suggest would land closer to or under 40 min:
  not performed here, box availability didn't offer a clean window this
  session.

## 3. Item 2 — K45's `tests/size/size_term.rxt` tower documented

Five `REFUSAL_PATTERN` entries added/extended, one per axis, each verified
against the SHIPPED diagnostic text before being written (never guessed):

| axis | what it actually hits |
|---|---|
| `-fno-counter` | a SECOND diagnostic shape of the same replication cap ("nested bounded repeats would replicate a body N times" vs the single-level "would replicate its body" the entry already matched) |
| `-fprefilter` | the general NFA construction cap — forcing a prefilter needs the NFA/DFA build the block's `engine vm` directive was written to skip |
| `--engine=dfa` | the SAME NFA construction cap, same reason |
| `-fno-altcls-merge` | the VM emitted-node cap (had NO entry at all before) |
| `-fno-size-term` | the emitted-code-bytes cap (had NO entry at all before) |

No `REFUSAL_FLOOR` added for the two new entries — a floor asserts a
MEASURED corpus-wide population (K35) and the only measurement behind
them is this one file's two cells. Verified live, full corpus (twice, in
both validation runs above): `refused_undoc=0` on all five, everything
else byte-identical. `docs/dev/known_issues.md` K45 is marked FIXED.

## 4. Item 3 — san's 34-script loop through a bounded job pool

`tests/lib/run_san_group.sh` (new): a FIFO-throttled job pool
(`SAN_PROCS`, default 4), buffered per-script output replayed in argument
order (nothing interleaves mid-line), `-- san: SCRIPT --` markers
preserved, a lost/crashed worker scored a HARD FAILURE. Deliberately NOT
`tests/lib/run_group.sh` — that script's own header says its `GROUP_PROCS`
is a real throttle only at exactly 1; every existing 2-3-script call site
launches its whole group unthrottled above that, which would oversubscribe
san's 34-script list (several already internally parallel at
`PROCS=nproc`) the same way K44 does. Applied [TT-8]'s own mech fix
(`INNER_PROCS = ncpu/PROCS`) to the identical shape: the four PROCS-aware
scripts among the 34 now get `PROCS=ceil(nproc/SAN_PROCS)` rather than the
old blanket `PROCS=nproc`, so they can't double-stack with pool siblings.

**D77 pre-measurement** (the trigger STEP 0 named before wiring anything):
the five whole-corpus identity scripts, sequential vs `-P4`, same tree,
box load 1.4-4 (quiet-ish, dropping over the run's own window).
**Sequential: 831s (13:51). Concurrent: 351s — 2.37x.** No shared-resource
contention — every script's own wall time was flat to slightly FASTER
concurrently, and every verdict tail was byte-for-byte identical between
the two runs.

**What was NOT done**: a full `make san` end-to-end run under the new
wiring (measured ~46 min at the old serial shape; expect meaningfully
less, unmeasured). `run_san_group.sh`'s own mechanics (job-pool
throttling, the PROCS override, ordinary-nonzero and signal-killed-worker
attribution) were verified with disposable dummy scripts outside the
worktree, not committed, not a substitute for the real end-to-end run.
Owed at the next merge/close battery.

## 5. Item 4 — K44's test-stage PROCS shapes

| shape | wall | rc | counterk.rxt:1807 | resource `[a-z]{0,30000}` CPU cap |
|---|---|---|---|---|
| `-j12 PROCS=1` | 1674s (27:54) | 2 (FAIL) | green | **RED** — exceeded 45s CPU |
| `-j4 PROCS=3` | 1115s (18:35) | 0 (PASS) | green | green |
| `-j2 PROCS=6` | 1792s (29:52) | 0 (PASS) | green | green |

All three ran the full 31/31 sections (`test_trailer.sh`'s own count — no
section silently dropped, K44's own cited failure mode for `-j12`
non-`-k` runs; these were all `-k` so that specific hazard didn't apply,
but the check ran anyway). **`-j4 PROCS=3` wins outright — fastest AND
only clean run**, not a speed/cleanliness trade-off. Recorded in
`docs/dev/known_issues.md` K44 with the table and ruling; `scripts/
battery.sh`'s test stage defaults to it.

**Measurement caveat, disclosed live to the team lead during the run**:
pcrec-bench (`worktrees/b34repin`) started its own `make check` at 10:07,
overlapping the tail of shape (a) and the first half of shape (b) — two
heavy jobs on the box from different repos/sessions, outside this lane's
control. The RELATIVE comparison between the three shapes still holds
(the same confound, roughly, touched (a) and (b) but not (c), and (b) won
on both speed and cleanliness anyway — contamination would if anything
have hurt (b), not helped it), but none of the three absolute wall times
should be read as quiet-box numbers.

## 6. Item 5 — `scripts/battery.sh`

Six stages (`test → strict → axes → san → lint → mech`), detached under
`setsid` with a PID file, one log per stage plus a `trailer.log` with
stage START/END/rc lines and a final `== BATTERY DONE rc=` line. Every
stage's shape besides `axes` (new per Frank's 2026-09-03 ruling) is
sourced from this lane's own measurements rather than carried over from
the manager's ad-hoc `battery_v4.sh` unchanged: `TEST_MAKE_J=4
TEST_PROCS=3` (item 4), `MECH_PROCS=6` ([TT-8], already established —
`battery_v4.sh` was contradicting it at `PROCS=4`), `SAN_PROCS=4`
(item 3), `AXES_PROCS` feeding `run_axes.sh`'s own pairing (item 1). The
detach/PID-file/function-injection mechanism was self-tested with dummy
stage commands (verified real-time). **Not run as a whole** — per the
brief, the manager runs the full battery at the next merge; a first full
run is the confirming measurement this row still owes for the combined
chain's own wall time and green/red shape.

## 7. What was not done, and why

- **Pairing THREE axes** — not measured; two already meets the "close to
  additive" bar, and the brief listed three as an explicitly optional
  stretch ("if pairing THREE is still additive, say so ... but ship two").
- **A quiet-box re-run of the full pairwise sweep** — the confirming
  measurement for whether ≤40 min is reachable outside today's daytime
  contention. Not performed; box availability didn't offer a second clean
  window this session.
- **A full `make san` end-to-end run under the new `-P` wiring** — the
  mechanism is validated (self-tests, D77) but not exercised at full
  scale. Owed at the next merge battery.
- **Running `scripts/battery.sh` itself** — explicitly the manager's job
  per the brief, at the next merge.
- **`docs/dev/plan.md`'s `[TT-12]` row** was left untouched — the manager
  updates plan.md at merge per this project's own convention; this report
  and `docs/dev/lanes/tt12b_log.md` carry the lane's own record.

## 8. Files touched

- `tests/axes/run_axes.sh` — pairing + K45's REFUSAL_PATTERN entries + the
  per-axis filename race fix.
- `tests/axes/CLAUDE.md` — pairing mechanism + K45 documentation.
- `tests/lib/run_san_group.sh` (new) — the bounded job pool.
- `tests/lib/CLAUDE.md` — its entry.
- `Makefile` — `san:` target rewired to `run_san_group.sh`.
- `scripts/battery.sh` (new) — battery_v5.
- `scripts/CLAUDE.md` — its entry.
- `docs/dev/known_issues.md` — K44 and K45 entries updated/closed.
- `docs/testing.md` — item 1/3 runtime sections, `battery_v5`'s shape in
  "Battery integration".
- `docs/dev/lanes/tt12b_log.md`, `docs/dev/lanes/tt12b_report.md` (this
  file) — the lane's own record.

Commit range: `969b9ba..52c9fee` (4 commits on `lane/tt12b`, off `6fba88d`).
`make strict` clean at every commit point it was checked (start, after
item 1+2, after item 4).
