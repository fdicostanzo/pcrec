# Lane trailgc: K134 trail compaction (STOPPED at the hot-path bar)

Lane trailgc (opus), 2026-10-29, worktree `worktrees/trailgc`, branch
`lane/trailgc` off main b05ccfc0b. Build go quoted in the brief (Frank
2026-10-29). Scratch: `/var/tmp/pcrec-pcrec/scratch/trailgc/`.

## Summary

STATE: stopped, under the brief's STOP RULE. The brief's bar is "0 hot-path
instructions on the non-full path". The brief's design (compaction called from
`<PREFIX>_TRAIL` when the trail is full) does not meet that bar when it is
measured.

- **The fix works.** TRAIL-SEG compaction with a derived hysteresis rule is
  built in the emitter (commit 6cc3ec09d). Every flat subject that gave up now
  answers on the default arm, and the answers equal libpcre2 10.46's:
  idents-1m, comment-5m, splice-1m, nest-paren-32k, nest-paren-100k.
- **It is not free.** Measured with `perf stat instructions:u`, per call, on a
  run whose trail never fills (`_in` with a 10M-entry trail):

  | subject | base instructions | at-full build | change |
  |---|---|---|---|
  | idents-1m | 188.6 M | 209.8 M | +11.3 % |
  | nest-paren-32k | 30.7 M | 32.4 M | +5.3 % |
  | splice-1m | 46.8 M | 52.8 M | +12.8 % |

  In cycles (minimum of 7, box loaded) this is about +4 % on idents, +3 % on
  splice, and noise on nest-paren.
- **The cause is structural, not the compaction code.** In the base artifact,
  gcc keeps `trail_depth` and the trail base pointer in registers across a run
  of `RX_SET`s and addresses the entries at constant offsets. A cold path that
  can change `trail_depth` and then REJOIN the hot path makes every `RX_SET` a
  merge point. gcc then reloads the depth and rebuilds the address at every
  site, and it spills the trail pointer. Three variants were tried and none
  removes this: `__builtin_expect`, an always-inline compaction, and a
  register-light call returning the new depth (+10.5 %). Any design that
  compacts at a trail write and continues has this cost.
- **A ruling is needed on which cost to take.** The three options are in
  Design below. My leaning is option 1 (compact when full, at the trail write,
  as built), with the bar restated as "no change in what gives up or answers,
  and +5-13 % instructions on trail-heavy matching". Option 2 is cheaper but
  partial. Option 3 is truly zero but doubles the matcher's text.

## Premise test

Confirmed at HEAD b05ccfc0b. I compiled `tests/recursion/cscan.rxt` with
`build/pcrec -p rx` and used l9look's driver (scratch `drv.c`). The default arm
`rx_search` returns `rc=-3` (`PCREC_ERR_FRAMES`) on idents-1m, comment-5m,
splice-1m, nest-paren-32k and nest-brace-128. It answers literal-100k.

libpcre2 10.46 answers all five at default limits (scratch `p2.py`, interp and
JIT): idents 0..1000007, comment 0..5000011, splice 0..1000009, nest-paren-32k
0..65547 and nest-brace-128 0..267. The bench's `cscan.rx` is byte-identical to
cscan.rxt's decoded pattern.

## Design

**TRAIL-SEG, as l9look stated it.** The live frames' `trail_mark`s partition
the trail. An unwind to a live frame restores the entries above its mark
newest-first, so the oldest entry per slot is the value that survives. Inside
one segment, every later entry for a slot that the segment already holds is
never read back, so dropping it changes no answer.

The compaction keeps each segment's entries in order, moves every live frame's
mark down with them, rewinds nothing, and changes no slot value. CUT-INV
holds.

**The K36 positional read is kept.** A call frame's |W| parked entries are the
first entries of its segment, and each names a distinct slot. So each one is
the oldest for its slot and is kept, at `mark + j` after the mark moves. A
return whose restore triggers a compaction reads the mark after the
compaction, because `<PREFIX>_SET` evaluates its value after `<PREFIX>_TRAIL`.
The call frame is live while its activation is: the stock positional read
already depends on that.

**The hysteresis is an amortization bound, not a tuned number.** A compaction
succeeds only if it leaves more than half the capacity free. When it fails,
the run gives up exactly as a full trail did before. It reads the whole trail,
and at least half a trail of fresh writes comes before the next compaction.
So each trail write pays for at most two entry visits: the doubling argument.

Any constant fraction is O(1) per write. The fraction k sets the usable share
of the capacity for live state (1 - 1/k) against a worst-case cost of k entry
visits per write. One half is the textbook point and was not tuned. Without
hysteresis, the l9look twin compacted 607,662 times on one call. With it, the
fast tier gives up and escalates instead.

The rule is never worse than no compaction, because it runs only where the
stock artifact gave up. It is not monotone in capacity in general: a trail at
least twice as large always reaches at least as far, and one between 1x and 2x
is not guaranteed to.

**Where the call sits: the three options.**

1. **At the trail write, when full (built; the brief's design).** General: it
   covers every source of garbage, including duplicates written inside one
   segment with no cut. The cost is +5-13 % instructions on the non-full path
   (table above).
2. **At `RX_CUT`, past a geometric threshold.** This is prototyped in scratch
   `vcut/`. A cut is where segments merge, which is where K134's garbage comes
   from. The check is `if (trail_depth > trail_gc_at) compact`, where
   `trail_gc_at = max(cap/2, 2*kept)`, also amortized O(1). The trail write
   keeps its stock `return FRAMES`.
   - Cost: +2.2 % instructions on idents and +1.1 % on nest-paren. That is 13
     cut sites against 256 set sites in cscan.
   - It answers all of K134's flat subjects. nest-brace reaches 77 levels.
   - It is partial. Garbage written with no cut (the `^(a(?1)?b)$` specimen,
     for example) is never compacted, and that specimen stays at n=342.
   - It also changes the trigger from "when full" to "past a threshold".
3. **A second matcher text with the compacting macro**, entered only after a
   plain run gives up with a trail-full code. This is the
   `vm_emit_guarded_matcher` text-copy precedent. gcc does not clone or
   inline the computed-goto matcher, so a flag cannot do it.
   - It is truly zero on the plain path.
   - The cost is about twice the matcher's C text and compile time for every
     artifact whose trail is unbounded. A trail-full run also re-runs from
     scratch, but the wasted plain run dies when its trail fills, so it is
     short.
   - The size caps (limits.md §8), the size term and the emitted-byte pins all
     move.

Under option 1 the bar could be met for patterns that cannot need compaction.
Artifacts whose trail cost is statically bounded (sized exactly by `vm_cost`)
could keep the stock macro. That does not help cscan-like patterns, which are
the ones the fix exists for.

## What was built

All of this is on `lane/trailgc` and is option 1.

- 6cc3ec09d: the emitter work in `src/gen/emit_vm.c`, `src/gen/attr_text.c`
  and `src/core/internal.h`.
  - `vm_emit_trail_compact` writes `static __attribute__((cold, noinline)) int
    <prefix>_trail_compact(<prefix>_run_state *run)`. It is emitted only when
    the artifact writes the trail (`emitted_set`).
  - The byte map has `<PREFIX>_NSLOTS` bytes on the stack. It is cleared
    through the entries just kept, so the cost is the trail plus the live
    frames, never frames x slots.
  - The function returns `w < trail_cap - w`.
  - Both `<PREFIX>_TRAIL` forms (plain and traced) now read `if (trail_depth >=
    trail_cap && !<prefix>_trail_compact(run)) return <PREFIX>_R_FRAMES;`.
  - `PCREC_ATTR_COLD` is a new [ATTR-TABLE] row (`cold`, `"__attribute__((cold,
    noinline)) "`, reader A5).
- 2nd WIP commit: the `^(a(?1)?b)$` specimen cells were re-aimed from 342/343
  to 512/513.
  - `tests/recursion/framebuffer.rxt`: cells 1-6. Cell 2 is now
    `frames-buffer=2048,8192`, and it still detects a swap because 8192,2048
    gives up (measured).
  - `tests/recursion/d27/sr_depth.rxt` and `sr_gen.py`: CEIL 512/513, and the
    500 cell moved to 1000. The cells were placed by hand with an in-file
    note, the way K34's were. The spans are libpcre2 10.46's on this box.
- e0eac8363: `tests/recursion/fb_exact_driver.c`.
  - The trail is now `6n - 3`, the compaction's own boundary: L(n) = 3n - 2
    live entries, and success needs 2L < T. It was measured exact at n = 1, 2,
    3, 10, 100, 342, 343, 510-514, 1000 and 699,051.
  - The default depths are now 510-514.
- e0eac8363: `fb_mmap_driver.c` and `run_frame_buffer.sh`.
  - The ceiling moved from 466k-470k to 699,000/699,100. It is predicted as
    `(ntrail + 3) / 6 = 699,051`, and measured exactly there.
  - The 342 row is now 512, and its check reads the §10.1 boundary.
- e0eac8363: `tests/thread/ts4_driver.c` and `run_stackdepth_tests.sh`.
  `TS4_N` is now 512, the new largest default match. The text 684 B became
  1,024 B.

Measured with option 1 (scratch builds):

| subject or specimen | base | option 1 |
|---|---|---|
| cscan flat subjects, default arm | FRAMES | answer = libpcre2 |
| cscan nest-brace, deepest default answer | 49 levels | 80 levels (the twin's any-progress rule: ~122) |
| `^(a(?1)?b)$`, largest default n | 342 | 512 (the trail still binds; frames would allow 1,024) |
| `^(a(?1)?b)$`, trail needed at n | ~9n | exactly 6n - 3 |

## Invoked checks run so far (targeted, option 1)

- `tests/harness/run.sh tests/recursion` (PROCS=4): before the re-aims, 2101
  pass and 5 fail. The 5 were exactly the moved specimen cells (sr_depth 50/51,
  framebuffer 34/55/80). After the re-aims, framebuffer.rxt and sr_depth.rxt
  pass 88/0. The whole directory was not re-run after the re-aims.
- `make test-stackdepth` (before the TS-4 re-aim): green. The entry frame stays
  3,184 B and the deep path 134,400 B, unchanged.
- `make test-frame-buffer` (opt-in, ASan): 7 pass, 0 fail after the re-aims,
  including the exact-fit arm under `-fsanitize=address,undefined`.

## Invariants kept

- **CUT-INV.** The compaction never rewinds the trail and never writes a slot.
  It only drops entries that no unwind restores, and moves marks.
- **The K36 positional read.** The argument is in Design. The specimen and
  every recursion corpus cell pass with compaction forced at the default
  capacities. The planned tiny-capacity sweep and sabotage row S1790 below were
  meant to witness it.
- **Tier identity (limits.md §3.2¶3).** A fast-tier success implies a
  deep-tier success, because the deep capacity is at least twice the fast one.

## Tests and sabotage

Not built: the lane stopped first. The plan, which holds for option 1:

- **Corpus.** Add K134 cells to `gen_cscan.py`, oracle libpcre2 plus the rule
  expectation. Five flat subjects of 0.2-2.8 KB give up on the base default
  arm and answer with compaction (built in scratch `k134/`):
  - idents: base trail hw 25,540
  - splice: 6,390
  - parens: 5,517
  - mixed realistic code: 21,041
  - braces80: 4,917

  Then repeat them under `frames-buffer=64,128` (minimum trail 60-107), so the
  `_in` arm compacts constantly. comment needs about 18 KB to exceed 3,072 on
  the default arm, so it goes only under the tiny route.
- **A tiny-capacity identity check** (`run_trail_compact.sh`, a driver on
  `_in`). Every cscan cell plus synthesized subjects run at trail caps {16 ..
  256} against a huge-buffer reference on the same artifact, capture arrays
  compared with memcmp. Two counted populations: the runs that answered below
  the stock trail high-water, measured by canary; and the specimen boundary
  `6n-3` answers and `6n-4` gives up.
- **The hysteresis witness.** The `-DRX_TEST_TIER_HOOK` count: idents (live
  about 45 > 28) must escalate exactly once. With hysteresis removed, the fast
  tier thrashes and never escalates.
- **Sabotage rows (S1790-S1794 planned):**
  - S1790 keeps the newest entry (overwrites the kept entry's value). This
    also corrupts a call snapshot.
  - S1791 does not clear the byte map between segments, so it crosses a live
    frame.
  - S1792 does not move the frame marks.
  - S1793 removes the hysteresis (`w < cap`).
  - S1794 never compacts.

## Movers and abi

The abi bump is NOT done; it would follow the ruling. Emitted bytes move on
every artifact that writes the trail: the `_TRAIL` macro, plus one function.
Readers found by test so far are all re-aimed in this branch:
- framebuffer.rxt and d27/sr_depth.rxt
- fb_exact, fb_mmap and run_frame_buffer.sh
- ts4_driver and run_stackdepth_tests

Readers still owed under option 1:
- docs/spec/limits.md §3.2 (a new paragraph on what the trail capacity bounds),
  §4¶1-2 (512/513; about 3 live and 6 needed per level) and §5¶6 (684 B became
  1,024 B)
- docs/spec/match_api.md §10.1¶1 (684/686 became 1,024/1,026) and §10.6¶2-3
  (the table and the 699,051 ceiling)
- docs/spec/tuning.md §2.11¶2 (nine trail entries per level)
- the stale comments in sabotage rows S155, S179 and S180 (686/3,081)
- the abi grep ritual and `make test-codegen`/registry/rxtsource
- the rxtsource census, startset manifests and axes allowances once cscan.rxt
  grows

## Measurement card

| card | value | how |
|---|---|---|
| non-full-path instructions, idents-1m | 188.6 M base → 209.8 M (+11.3 %) | `perf stat instructions:u`, (11 calls - 1 call)/10, `_in` NF=64 NT=10M |
| non-full-path instructions, nest-paren-32k | 30.7 M → 32.4 M (+5.3 %) | same |
| non-full-path instructions, splice-1m | 46.8 M → 52.8 M (+12.8 %) | same |
| non-full-path cycles, min of 7 | idents 54.0 → 56.1 M; splice 13.0 → 13.4 M; nest-paren 9.46 → 9.30 M | same, cycles:u, box under a queue job |
| option 2 (at-cut) instructions | idents 192.7 M (+2.2 %), nest-paren 31.1 M (+1.1 %) | scratch `vcut/`, NT=100M so no compaction fires |
| variants of option 1 | `__builtin_expect` +11.3 %; always-inline 226.4 M (+20 %); call returning depth +10.5 % | scratch `vexp/`, `vinl/`, `vret/` |

## Filed rows

- **[TRAIL-COST-BOUND]** (new, not built). `vm_cost` charges a possessive
  loop's trail per ITERATION, because a cut does not rewind it. With
  compaction, the live trail of such a loop is bounded by NSLOTS x (frames +
  1), so the static sizing could stop classing such loops as unbounded. That
  is an opt row; its trigger is a measured artifact whose trail sizing moves a
  verdict.
- **Candidate B ([ART-TRAIL-ELIDE])** is the overlap. Write coalescing removes
  the writes whose merge cost option 1 adds, and it shrinks what any option
  must compact. If B lands first, option 1's measured overhead shrinks with
  it. Not built here, per the brief.
- **K36's hoist** is still open (`vm_region`'s guard after the reads). Not
  touched: this lane does not edit that region.

## STATE AT HANDOFF

- STATE: stopped (STOP RULE: the measured hot-path cost contradicts the brief's
  "0 hot-path instructions" bar). A ruling is needed: option 1, 2 or 3, or a
  restated bar.
- Rulings file `docs/dev/lanes/trailgc_rulings.md`: empty at every read
  (start, before each commit, before this report). Last entry applied: none.
- Branch HEAD: option 1 built, plus the specimen re-aims (WIP commits).
  Uncommitted: none.
- Owed runs: NOT queued (trailgc-test and trailgc-mech). The build is held
  pending the ruling, and queuing a full suite on a design that may change
  would waste a box slot.
- Resume plan for a fresh agent: read this report; apply the ruling; for
  option 1, do "Tests and sabotage" and then "Movers and abi", then queue
  690-trailgc-test and 691-trailgc-mech. The scratch prototypes and
  measurement helpers in `/var/tmp/pcrec-pcrec/scratch/trailgc/` are:
  - `build.sh`, `drv.c`, `maxdepth.sh`, `maxab.sh`, `p2one.py`
  - `base/`, `new/`, `vcut/`, `vret/`, `vexp/`, `vinl/`
  - `k134/` subjects
  - `basetree/`, a b05ccfc0b build
