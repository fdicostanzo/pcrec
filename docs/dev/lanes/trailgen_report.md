# Lane trailgen: VM-wide trail census and a review of the trail's structure

Lane trailgen (opus), 2026-10-29. Design and measurement only (no build go): nothing under
`src/`, `cli/`, `lib/` or `memfn/` changed. Worktree `worktrees/trailgen`, branch
`lane/trailgen` at lane/trailgc 801ad1214 (main + D183, not yet landed). Every twin is a
mechanical text rewrite of lane/trailgc's emitted C, built in scratch
`/var/tmp/pcrec-pcrec/scratch/trailgen/`; the generators, drivers and raw tables are copied
to `docs/dev/lanes/trailgen_evidence/`. Read only: main's `vmbc_report.md` and
`vmbc_evidence/`, the bench checkout (its store records, patterns and subjects).

## Summary

- **The premise holds only for the recursive members.** On the bench's own VM patterns
  that are not cscan/JSON, vmbc's B (delete writes whose new value is dead) removes
  **0.4 % of trail entries** and 0.1 % of instructions. vmbc's flat subjects (idents,
  splice, comment) are flat INPUTS to a recursive, call-bearing pattern, so they do not
  speak for flat patterns. B is not the general VM win.
- **The general VM win is a sibling rule of B, found by this census: UNDO-DEAD.** A
  trail entry exists only so that an unwind can put the OLD value back. If that old value
  is dead everywhere an unwind can deliver it (at the resume label of every frame that may
  be live at the write, and at the next attempt's entry), the write still happens but
  records no entry. Over the 41 non-recursive bench artifacts in the sample it removes
  **87.8 % of trail entries** (16.09 M -> 1.96 M) and **21.7 % of summed instructions**,
  against a no-trail upper bound of 26.4 %. Per artifact: `bak-2` (`(\w)(\w)\2\1`)
  -64 % instructions and -63 % cycles, `phone-palindrome-6` -51 % / -47 %, the three
  `bak-*` -30 % / -20 %, `mod-j-uc` -15 % / -11 %. It answers identically on every
  sampled artifact and witness.
- **UNDO-DEAD is [ART-TRAIL-ELIDE] in general form.** vmbc folded that row into B as
  "subsumed". The census says it is not: B deletes writes, and these writes are live (a
  backreference or accept reads them). The row belongs in the same analysis, as a third
  verdict.
- **The second general finding is about how the trail is driven, not what it holds:
  REGISTER-RESIDENT CURSORS (R).** When the matcher is a separate function (large and
  call-bearing artifacts), gcc keeps `trail_depth`, `resume_depth`, `call_top` and the
  budgets in memory. It reloads and stores them around every slot store, because
  `slot_values` lives inside the same run struct and may alias them (checked in the
  assembly). Matcher locals, written back at every exit, remove that:
  - stock: -8 % to -18 % instructions and -15 % to -33 % cycles on the six gap subjects;
  - on top of B+C: another -8 % to -20 % instructions (idents 79.6 M, now below
    pcre2-jit's 82.1 M);
  - answer-identical by construction (5,460 cells, 0 differences, same give-ups);
  - zero effect on small artifacts whose matcher is inlined (gcc already does it there).
- **Packed 8-byte trail entries (P): measured, not now.** They halve one-shot page
  faults on stock (js-1m 82.9 k -> 48.5 k) but add instructions (+1 % to +10 %). After
  B+C the trail is too small to matter (js-1m 15.7 k -> 14.8 k).
- **Proposal: one coherent trail cleanup, one build, three stages.**
  1. Stage 0, R: cursors as locals.
  2. Stage 1, SLOT-FLOW write verdicts: DELETE (vmbc's DEAD and COPY), UNTRAIL (new),
     KEEP, from one liveness pass plus one forward "frames that may be live" pass.
  3. Stage 2, vmbc's C: the call restore moves to each call site.

  It replaces vmbc's two-stage B+C plan, with the same base (D183) and the same single
  abi event. Questions for Frank below.
- **Not covered:** the corpus. The box lock refused at 11:25 (queue jobs ready). The
  bench sample is 50 of 79 distinct VM patterns, by a declared rule. The corpus census
  is the build's STEP 0 (card below).

## Premise test

**Partly confirmed.** The table in `trailgc2_report.md` does show trail shares of
35-73 % on idents, splice and comment, and vmbc's twins reproduce them: stock idents
191.67 M instructions, B+C 91.73 M. But those three subjects run the cscan pattern, which
has 20 spliced and 2 linked calls. The trail entries B removes there are the splice's
park-and-restore writes, so B's win is a recursion-machinery win even on flat input.

Over the bench's other VM patterns (table below):

- B+C changes the summed instructions by **-0.1 %** (flat) and **-1.8 %** (recursive).
- B's DEAD rule fires on 7 of 46 artifacts (38 of 276 SET sites), and mostly on the
  `rec-*` family.

So, per the brief's STOP RULE: **B removes little outside recursion.** The census then
asked what the trail cost on flat patterns IS. The answer is UNDO-DEAD:

- It fires on 43 of 46 artifacts (149 of 276 sites).
- 16 of the 25 trail-writing artifacts push no frame at all on their subject. They write
  captures that only `<prefix>_reset_for_next_attempt` ever unwinds, and the next attempt
  overwrites them before reading them.
- The other 9 push frames, but the slot is dead at every resume label.

Frank's bet ("a general VM benefit, not only recursion") holds for the trail cleanup as a
whole, but through UNDO-DEAD and R, not through B.

## Census

**Method.**

- **Population.** For each bench subbench, the newest auto-caps pcrec record in
  `pcrec-bench/store/records/` gives each pattern's engine (`bench_vm.py`). 86 VM rows,
  79 distinct texts. `unusual/` is not in the store; vmbc's census covers its 25.
- **Declared sample** (the 50-compile cap):
  - all 5 `subst` VM cases, on `acc-small`. It is regenerated from
    `bench/subst/logsim.py` and its sha256 equals the manifest's
    7f972454...b1ad77e0.
  - the first 45 of the other 74 distinct patterns, ordered by sha256 of the pattern
    text (`sample.tsv`). The 29 not sampled are listed in `notsampled.tsv`.
- **Per pattern.** One emit (lane/trailgc's pcrec, `-p rx --features all`) and seven
  gcc builds: stock, counting, R, no-trail, B+C (vmbc's `vmopt.py -m BCd`), B+C
  counting, B+C+R. A second pass, with no new emit, adds B+C+U (`vmopt_tg.py -m BCdU`),
  its counting twin, and B+C+U+R.
- **The driver** `gdrv.c` is the throughput regime: every non-overlapping match over the
  bench's largest timed subject for that pattern, default arm.
- **Instructions** are `instructions:u` per pass, (REPS=3 - REPS=1)/2.
- **Identity** compares match count, a checksum over every capture span, and the give-up
  code with stock.
- **Skipped (4).**
  - 3 `bounded/cls-*` now route to the DFA at this pin. The bench record (an older pcrec)
    says VM.
  - `utf8/asr-lb-class` is refused under byte encoding. The census emits without
    `-e utf8`, so the 3 sampled `utf8/` patterns ran as byte patterns: a known
    deviation from the bench.
- R did not build on 2 artifacts that have a second matcher function
  (`<prefix>__match_notempty`). The prototype localises only `<prefix>_match_anchored`.

**Trail-writing artifacts** (21 flat and 4 recursive of 46; the other 21 write no trail on
their subject). Columns:

- **trail/B**: trail entries per subject byte.
- **share**: the no-trail twin's saving, an upper bound on the trail's cost.
- **B+C**, **U on top**, **R**, **all**: instruction change per pass. "U on top" is
  against B+C; the others are against stock, and "all" is B+C+U+R.

| artifact | rec | SET / B-dead / U | trail/B stock -> all | share | B+C | U on top | R | all |
|---|---|---|---|---|---|---|---|---|
| syntax/bak-2 `(\w)(\w)\2\1` | no | 6 / 0 / 6 | 4.17 -> 0 | 64 % | 0 | **-64.4 %** | -0.8 % | **-64.4 %** |
| capability/phone-palindrome-6 | no | 9 / 0 / 9 | 0.79 -> 0 | 51 % | 0 | **-51.4 %** | +0.5 % | **-50.6 %** |
| syntax/bak-1, bak-py, bak-g-rel | no | 3 / 0 / 3 | 2.22 -> 0 | 30 % | 0 | **-29.7 %** | 0 | **-29.7 %** |
| syntax/mod-j-uc | no | 6 / 0 / 2 | 2.97 -> 1.49 | 32 % | 0 | **-14.7 %** | +0.9 % | -11.4 % |
| utf8/asr-lb-varwidth | no | 2 / 0 / 2 | 0.002 -> 0 | 12 % | 0 | -11.8 % | +3.0 % | -6.8 % |
| capability/wild-semdiv-empty-alt-repeat | no | 3 / 0 / 0 | 0.37 -> 0.37 | 9 % | 0 | 0 | 0 | 0 |
| subst/5-mask-ipv4 | no | 10 / 4 / 6 | 0.045 -> 0 | 5 % | -1.6 % | -3.3 % | +0.5 % | -4.0 % |
| subst/4-reorder | no | 6 / 0 / 6 | 0.027 -> 0 | 3 % | 0 | -2.8 % | 0 | -2.8 % |
| capability/wild-logparse-quotedstring-grok | no | 16 / 0 / 10 | 0.017 -> 0.006 | 3 % | 0 | -1.3 % | -0.6 % | -1.7 % |
| syntax/lkb-neg | no | 2 / 0 / 2 | 0.005 -> 0 | 2 % | 0 | -1.9 % | +1.7 % | -0.6 % |
| subst/7-url-tld-fix | no | 15 / 0 / 11 | 0.003 -> 0.001 | 2 % | 0 | -1.0 % | -0.9 % | -1.8 % |
| capability/wild-logparse-base10num-grok | no | 1 / 0 / 1 | 0.047 -> 0 | 2 % | 0 | -1.6 % | +0.4 % | -1.1 % |
| syntax/lka-pos, lka-verb, lka-nonatomic | no | 2 / 0 / 2 | <=0.005 -> 0 | <=1 % | 0 | +1.6 % / +1.6 % / -1.4 % | 0 | +1.6 % / +1.6 % / -1.4 % |
| syntax/grp-named, grp-named-quote, subst/2-rare, 6-upper | no | 2 / 0 / 2 | <=0.011 -> 0 | 0 | 0 | -0.2 % / -0.2 % / 0 / 0 | 0 | about 0 |
| syntax/rec-back, rec-g-angle, rec-py | yes | 12 / 9 / 3 | 0.069 -> 0 | 3 % | -1.8 % | -1.1 % | 0 | -2.9 % |
| syntax/rec-1 (gives up FRAMES on t-1m, every twin identically) | yes | 15 / 3 / 3 | 0.001 -> 0 | 7 % | -5.0 % | -0.3 % | -9.5 % | **-17.5 %** |

Totals:

| group | artifacts (trail-writing) | instructions/pass | no-trail bound | B+C | B+C+U | R | B+C+U+R | trail entries stock -> B+C+U |
|---|---|---|---|---|---|---|---|---|
| flat | 41 (21) | 803.9 M | -26.4 % | -0.1 % | **-21.7 %** | +0.2 % | **-20.8 %** | 16,094,053 -> 1,960,073 (-87.8 %) |
| recursive | 5 (4) | 29.2 M | -2.9 % | -1.8 % | -2.9 % | 0 | -2.9 % | 219,121 -> 51 |
| vmbc's six gap subjects (cscan, JSON) | 2 artifacts | below | | | | | | |

- **Cycles** on the largest movers: min of 5, box load 5.7, gdrv REPS (3-1)/2.

  | artifact | stock -> B+C+U |
  |---|---|
  | bak-2 | 22.37 -> 8.34 M (-63 %) |
  | phone-palindrome-6 | 5.05 -> 2.70 M (-47 %) |
  | bak-py | 22.10 -> 17.79 M (-20 %) |
  | mod-j-uc | 41.00 -> 36.63 M (-11 %) |
- **Small changes are within noise.** The +1.6 % to +3 % rows (lka-pos, lka-verb,
  asr-lb-varwidth) are code-layout moves on artifacts doing 0.1-1 M instructions per
  pass. R's +/-2 % on inlined artifacts is the same.
- **Trail entries per push** are at most 4 on every pushing artifact (cscan nest-paren:
  9 per byte against 11 pushes per byte). This is the number behind the copy-on-push
  verdict below.

**The six gap subjects**, instructions per call (M), lane/trailgc's `drv.c` `r` mode,
vmbc's method:

| subject | stock | R | B+C | B+C+R | B+C+U | B+C+U+R | pcre2-jit (vmbc) |
|---|---|---|---|---|---|---|---|
| idents-1m | 191.67 | 165.25 | 91.73 | **79.63** | 90.39 | **78.67** | 82.09 |
| nest-brace-100k | 162.72 | 133.92 | 91.02 | **72.72** | 90.42 | 72.72 | 50.40 |
| splice-1m | 47.76 | 42.76 | 20.42 | 18.76 | 20.42 | 18.76 | 23.66 |
| js-1m | 260.71 | 225.81 | 72.63 | **65.02** | 72.63 | 65.02 | 58.58 |
| nest-paren-32k | 31.07 | 25.43 | 25.04 | **20.12** | 24.97 | 20.05 | 10.35 |
| comment-5m | 220.97 | 202.97 | 133.47 | 132.97 | 128.47 | 129.97 | 86.50 |

Cycles, min of 5 at box load 6.6-6.9 (noisy; read the instruction column for decisions):

| subject | stock | R | P | B+C | B+C+R | B+C+R+P | jit (vmbc, load 3.5) |
|---|---|---|---|---|---|---|---|
| idents-1m | 57.34 | 44.92 | 54.32 | 24.34 | **20.50** | 19.69 | 18.30 |
| nest-brace-100k | 77.70 | 56.07 | 45.89 | 23.83 | **20.33** | 19.15 | 12.67 |
| splice-1m | 12.73 | 10.59 | 11.62 | 3.71 | 3.38 | 3.38 | 4.62 |
| js-1m | 97.82 | 83.37 | 83.11 | 24.74 | **20.96** | 21.86 | 16.86 |
| nest-paren-32k | 10.35 | 6.94 | 8.34 | 6.33 | 5.75 | 5.42 | 1.77 |
| comment-5m | 43.87 | 35.69 | 41.20 | 27.28 | 25.70 | 25.32 | 17.89 |

**Identity.**

- R, P and RP against stock: `ident_tg.py` (vmbc's checker, retargeted) gave 5,460 cells,
  **0 differences, and give-ups in exactly the same cells**.
- B+C+R, B+C+RP and B+C+U(+R) gave 0 differences. They also answer 484-747 cells where
  stock gives up, which is B+C's capacity gain.
- The 46 census artifacts: every twin equal to stock.
- Trap witnesses (`traps.py`): 16 patterns, 492 cells, 0 differences. These are vmbc's
  six plus captures under alternation, loops, lookahead and backreferences.
- An earlier R build had a bug: the prototype missed rewriting `RX_TRAIL_CHECK`. The
  checker caught it as give-ups where stock answered (34 cells), and it was fixed before
  any number above.

## Trail structure today

From lane/trailgc's emitted C (`emit_vm.c`), `docs/spec/limits.md` §3.2, §4, §5 and
`docs/spec/match_api.md` §10.

- **Entry.** `{ unsigned slot_index; ptrdiff_t saved_value; }`: 16 bytes, 4 of them
  padding. `<PREFIX>_TRAIL_FRAME_SIZE` stamps it, the artifact asserts it, and it is
  private layout. match_api §10.4¶1 publishes the arithmetic only.
- **Write** (`<PREFIX>_TRAIL` inside `<PREFIX>_SET`):
  1. capacity check (`return R_FRAMES`);
  2. store the slot index and the old value;
  3. increment `run->trail_depth`.

  Every `SET` writes an entry. That is P7: the old value is saved unconditionally.
- **Frames** (the resume stack) are a separate array:
  - 24 B call-free (`resume_label`, `resume_position`, `trail_mark`);
  - 40 B call-bearing (adds `call_ret`, `call_top`).

  A frame's `trail_mark` is the trail depth at its push. **Segments are implicit:**
  segment i is `[frame[i].mark, frame[i+1].mark)`. There is no segment header.
- **Restore** (`<prefix>_fail`): pop the frame, then walk the trail backward from the top
  to its mark, restoring each slot. Several entries for one slot restore newest first,
  so the oldest wins. The attempt reset (`<prefix>_reset_for_next_attempt`) is the same
  walk down to 0, run between start positions.
- **CUT** sets `resume_depth` back to a saved mark and never rewinds the trail (CUT-INV).
  So the cut segments merge into the parent's segment.
- **TRAIL-SEG** (K134): inside one segment, only the oldest entry per slot can ever be
  restored. **D183** compacts to that at checkpoints:
  - placement: backward gotos that close a trail-writing cycle, and region returns;
  - floor: `cap - min(M, cap/2)`;
  - stop rule: stops for the attempt when it cannot free a quarter;
  - it moves the frame marks down with their entries.
- **Calls** (K36):
  - `<PREFIX>_CALL` pushes a frame whose resume is `fail`.
  - It snapshots W(g) as self-writes, which are the first entries of that frame's
    segment.
  - The region exit restores W(g) by positional reads `trail[frame[call_top].mark + j]`.
  - Compaction keeps those first entries in order, so the positional read survives.
- **Storage and capacity** (limits §3.2, §5; match_api §10):
  - two caller buffers (frames, trail) in the `_in` descriptor, each with its own
    capacity;
  - the default entries run a page-budgeted fast tier first, then a 2,048-frame,
    3,072-entry run struct on the C stack (131 KB deep path for the specimen, K33);
  - statically bounded artifacts get exact stamped capacities (`bak-2`: 1 frame,
    7 entries).
  - A full trail gives `PCREC_ERR_FRAMES`, the same code as full frames.
- **The run state** (`<prefix>_run_state`) holds `slot_values[NSLOTS]`, the two
  buffer bases and capacities, both depths, `call_top` and the two budgets. The matcher
  takes `run` by pointer and sets `slot_values = run->slot_values`.

## Structure review

Each candidate is ranked by measured effect, then soundness risk, then spec cost.

| # | candidate | measured / estimated effect | soundness risk | spec cost | verdict |
|---|---|---|---|---|---|
| 1 | **UNDO-DEAD**: no trail entry when the old value is dead at every unwind target | flat bench: -87.8 % entries, -21.7 % instructions, up to -64 %; gap subjects 0 to -3.7 % on top of B+C | **medium**: an untrailed write is R25 E5's failure class. Controlled by the push edge (vmbc's TRAIL-EQ) and two planted sabotages, both detected (below) | stamped `TRAIL_FRAMES` shrink where the cost model learns it (limits §3.2 stamps, `rx_info.trail_frames`); [ART-TRAIL-ELIDE] named "the trail FRAMES give-up goes" | **build** (stage 1) |
| 2 | **R: cursors as matcher locals** (`trail_depth`, `resume_depth`, `call_top`, budgets, bases, caps), written back at every return and around the compaction call | gap subjects -8 to -18 % instructions stock, -8 to -20 % on B+C; 0 on inlined (small) artifacts | **low**: same values, same order of every observable store; 0 differences in 5,460 cells | none (private); abi bump only | **build** (stage 0) |
| 3 | B: DEAD + COPY (vmbc) | gap subjects -40 to -72 % with C; flat bench -0.1 % | medium (vmbc's analysis) | vmbc's | build (stage 1, as vmbc designed) |
| 4 | C: call restore per site (vmbc) | the depth and js/nest-brace wins | medium (vmbc's) | vmbc's | build (stage 2) |
| 5 | **P: 8-byte packed entry** `(value << 16) \| slot` | one-shot page faults -41 to -50 % on stock, only -5 to -42 % on small counts after B+C; instructions +1 to +10 % stock, about 0 after B+C+R | low; needs slot < 65,536 (static) and \|value\| < 2^47 (a subject-length bound to state) | `TRAIL_FRAME_SIZE` 16 -> 8, limits §5's stack numbers, match_api §10.4's example, §10.6's table; private layout, so callers recompile, no source change | **not now**: file a row; decide together with the default trail capacity (vmbc question 3) |
| 6 | per-slot epoch / generation marks instead of entries (skip the entry when the slot is already saved in this segment) | runtime twin of vmbc's rule (iii), measured at **zero** on top of B+C. Cannot see cut-merge growth (each possessive pass has a new epoch), which is exactly K134 | low | none | **reject**; D183 stays the runtime answer |
| 7 | copy-on-push (pcre2's interpreter style: each frame copies the capture vector) | every pushing artifact here has at most 4 entries per push, against NSLOTS 2-83 words copied per push (cscan nest-paren: 11 pushes per byte x 83 slots against 9 entries per byte) | low | frame size becomes NSLOTS-dependent | **reject**: the undo log is the right shape, more so after U and B |
| 8 | one interleaved frame-and-trail stack (implicit marks) | saves one 8 B field per frame; compaction must move frames | medium | **high**: the two-buffer `_in` descriptor (match_api §10.2) and both capacities change | **reject** |
| 9 | narrower frames (32-bit `trail_mark` and `call_top`, `call_ret` off the uniform frame): 40 -> 32 or 24 B | unmeasured. After B+C, frames ARE the storage (js-1m: 64 B per subject byte, mostly frames) | low | `RESUME_FRAME_SIZE` stamps; a frame-count bound below 2^32 to state | **file**, trigger: the post-B+C one-shot regime still bound by frame bytes |

**What pcre2 does.** No pcre2 source is on the box (searched with `find /`, nothing
downloaded), so this is general knowledge, not a reading:

- The 10.30+ interpreter uses heap frames that each carry the whole ovector, copied at
  every backtrack point (row 7's shape).
- The JIT saves a capture pair onto its own stack when it enters the capturing bracket,
  and restores it in that bracket's backtrack code. The slot is implicit in the code, so
  no slot index is stored.

pcrec's trail plus the per-write static verdicts (U, B) is the AOT analogue of the JIT's
static save. The remaining difference is the generic restore loop against restore code
generated per bracket. After R that loop is tight (the measured R gains are mostly that
loop and the push path).

**Why R works only on big artifacts.** The aliasing lives in the matcher's own stores:

- `slot_values[i] = ...` with a variable `i` (every unwind) or through
  `run->trail[...].saved_value` (type `ptrdiff_t`, which may alias `size_t`);
- so gcc reloads `run->trail_depth` (offset 704 on cscan) and stores it back on every
  iteration of the unwind loop and every SET.

When the matcher is inlined into `<prefix>_search`, the run struct is a local whose
fields gcc can disambiguate, and R changes nothing. This is the sharper number
`frame_buffer_design.md` §6 said a lane should count instructions for. trailgc2 already
measured the same effect for `gc_at` (8-20 instructions per check as a run field).

## Proposed general cleanup

**One analysis, one declared table, three verdicts per write, plus two mechanical
changes.**

> **SLOT-FLOW** (vmbc's flow graph: fall-through, gotos, `PUSH(L) -> L`, region exit ->
> return labels). It computes slot liveness (least fixpoint) and one forward may-analysis,
> MAYFRAMES(p): the resume labels of frames that may be live at p.
>
> - `PUSH(L)` adds L.
> - The resume edge carries the pusher's set without L.
> - CUT keeps the set (an over-approximation, sound).
>
> Each `SET(s, e)` site gets the first matching verdict:
>
> | row | condition | verdict | emitted |
> |---|---|---|---|
> | 1 | the site is a call snapshot (K36 positional storage) | KEEP | `<PREFIX>_SET` |
> | 2 | `s` is dead after the site | DELETE | nothing (vmbc DEAD) |
> | 3 | `s == source` provably on every path | DELETE | nothing (vmbc COPY) |
> | 4 | `s` is dead at the attempt entry and at every L in MAYFRAMES(site) | UNTRAIL | `<PREFIX>_SETU` (a plain store) |
> | 5 | otherwise | KEEP | `<PREFIX>_SET` |
>
> vmbc's rule table (its reads and writes per statement, row 11's refuse-to-optimise
> default, row 7's code-site rule) is unchanged and feeds both passes. C stays vmbc's
> rule, in the stock-restore model.

**Why UNTRAIL is sound.** It is the same induction as vmbc's TRAIL-EQ argument:

- The invariant "every LIVE slot holds the stock run's value" survives an untrailed
  write. Between the write and an unwind to a frame F, the stock run restores `s`. The
  twin does not, but `s` is dead at F's resume label (row 4), so no read sees the
  difference.
- The attempt reset is an unwind to "no frame", whose target is the matcher's entry.
- Frames pushed AFTER the write save post-write values, which the twin also holds.
- CUT only removes frames, so MAYFRAMES over-approximates.
- Linked calls are covered: the snapshot is row 1, and return labels are flow edges.

**Controls, run here.**

- **Sabotage, entry liveness dropped** (`TG_SAB_ENTRY`): witness `a|(b)c` on `bxa`.
  Stock gives g1 -1,-1; the sabotaged twin gives a stale 0,1. DETECTED.
- **Sabotage, MAYFRAMES dropped** (`TG_SAB_FRAMES`): witness `(ab|a)+ab` on `aaba`,
  found by exhausting {a,b}^2..9. Stock gives g1 0,1; the sabotage gives 1,2. DETECTED.
  Over all 1,020 of those subjects, the sabotage differs from stock on 610 and the
  correct U twin on 0.
- **R25 E5** (`(?:a|bc){3}+`): U leaves its counter trailed (live at the resume label).

**The two mechanical changes.**

- **R:**
  - every matcher function that expands the VM macros keeps the trail and resume
    cursors, their bases and capacities, `call_top` and the budgets as locals;
  - `return` sites write the five mutable ones back;
  - the cold compaction call is bracketed by write-back and reload;
  - a call that passes `run` (none today; [INLINE-C] code sites may add one) is
    bracketed the same way.
- **D183 follow-through** (vmbc's prune): a checkpoint is placed only where a still-
  TRAILED write closes the cycle, and the margin counts trailed sites. U makes this
  matter more: `bak-2` has no trailed site left, so it needs no checkpoint and no
  compaction code at all.

**What it subsumes.**

- [ART-TRAIL-ELIDE] is row 4, in general form (frames may be live). Correct vmbc's
  "subsumed by B" note.
- vmbc's rule (iii) stays dropped (measured zero; and runtime epochs, review row 6, are
  rejected for the same reason).

**General mechanisms, not special cases.** There is no recursion-only clause and no
frameless-only clause. Row 4's "no frame live" case is just MAYFRAMES = {}. One table
and one analysis decide every write. It does have three rows over one fact (liveness);
the forest-for-the-trees lens is satisfied, because the table is the unification.

**The cost model.** `vm_cost` charges a trail entry per `vm_set`. To shrink the stamped
capacities, the verdict must exist before sizing: run SLOT-FLOW on the emitted program
first, then size. Leaving the charge as it is is SAFE (over-charge; S87's guard is
against UNDER-charge) and keeps the stamps. Recommendation: stamps follow the verdicts in
the same build; this is the spec hunk [ART-TRAIL-ELIDE] already named.

**Standing questions (docs/design/CLAUDE.md).**

1. **Measurement regime (relevant).**
   - Warm throughput, resident buffers, one box (7700X, gcc 15.2 -O2).
   - Instruction counts decide. Cycles were taken at load 5.7-6.9 and only confirm
     direction.
   - The one-shot regime (page faults) is measured for P.
   - No verdict flips between regimes.
2. **Independent control (relevant).**
   - The twins are judged by running both binaries (stock pcrec's answers), never by the
     analysis.
   - `vmopt_tg.py` reads emitted TEXT, so it shares no source with a future emitter
     analysis. It becomes the build's independent verdict checker: every DELETE and
     UNTRAIL the build emits must be justified by the text analysis.
   - Population: `census_tg.py` reports skips and refusals.
3. **What moves on regeneration (relevant).**
   - Every VM artifact's prologue and macros (R).
   - The SET -> SETU lines, deleted SETs, the moved restores, the checkpoint lines and
     the margin constant.
   - The stamped trail capacities (rows 2-4 change the sizing).
   - The `--emit-ir` program listing (S10), which must show the verdicts.
   - All of it is one abi event with a mover census.

## Interaction with B+C and D

- **B+C (vmbc).** This proposal keeps vmbc's design whole. It adds one table row (4) and
  one forward pass, and puts both in the same stage as B, because they read the same
  liveness.
  - U on top of B+C is small on the gap subjects (idents -1.5 %, comment -3.7 %) and
    carries the flat bench (-21.7 %).
  - R is independent of B+C, and it compounds with it: B+C+R reaches idents 79.6 M,
    below pcre2-jit's 82.1 M. B+C makes the trail small; R makes what remains, and the
    push and fail paths, cheap.
  - vmbc's two internal stages become three: R, then the write verdicts, then C. That is
    still one build and one abi bump.
- **D (first-byte alternation dispatch, lane altd, in design).**
  - D cuts pushes per byte, the dominant cost left on nest-paren (B+C+R still 20.1 M
    against jit's 10.35 M). R cuts the cost per push. They compound and do not overlap.
  - For SLOT-FLOW, D's dispatch is a new statement. vmbc's row 11 refuses to optimise
    anything unrecognised, so D landing first or second is sound either way. Whichever
    lands second adds the dispatch's row: its successors are the arms, and a dispatch
    that pushes on behalf of an arm adds that arm's resume label to MAYFRAMES.
  - Neither changes the other's verdicts. Fewer pushes means fewer MAYFRAMES entries,
    so D can only widen U.
  - Ordering: no constraint from this side.

## Measurement cards

All commands are under `/var/tmp/pcrec-pcrec/scratch/trailgen/`, with copies in
`docs/dev/lanes/trailgen_evidence/`. The stock C is lane/trailgc's emitted
`scratch/trailgc2/gap/{cscan,json}/rx.c`; the B+C C is vmbc's `scratch/vmbc/b/*_BCd/`.

| card | command | reads | result |
|---|---|---|---|
| bench VM population | `python3 -I bench_vm.py STORE BENCH > bench_vm.tsv` | engine per pattern from the newest auto-caps record | 86 rows, 79 distinct |
| census (declared sample) | `python3 -I census_tg.py sample.tsv census.tsv`, then `census_u.py census.tsv census_u.tsv`, then `analyse.py` | trail/byte, push/byte, no-trail bound, B+C / U / R instructions, identity | `census.tsv`, `census_u.tsv` |
| twins | `mkv.sh SRCDIR OUTDIR MODE [gdrv.c]`; MODE in `stock cnt R P RP notrail` (and `+cnt`) | — | — |
| gap rates | `NOCYC=1 MODES="..." rate.sh` (instructions), `rate.sh` (min-of-5 cycles) | per call, (11-1)/10 | `rate_instr.txt`, `rate_cyc.txt` |
| identity, gap twins | `MODES="R P RP BCd_R BCdU_stock ..." python3 -I ident_tg.py {cscan\|json}` | 0 differences | `ident_summary.txt` |
| traps | `python3 -I traps.py` | 16 patterns, 492 cells | `traps.log` |
| sabotage controls | `python3 -I sab.py` (entry), `sab3.py` + the {a,b}^2..9 sweep (frames) | stale capture reported | in this report |
| one-shot | `REPS=1 NF=4194304 NT=67108864 perf stat -e page-faults:u,task-clock tw/K_M/drv SUBJ r` | first-touch pages | in this report |
| **corpus STEP 0 (not run: box lock refused at 11:25)** | `scripts/boxlock run --label trailgen-census -- python3 -I census_tg.py` over the `--list-source` corpus (one row per distinct VM pattern, its `.rxt` subjects as input), then `census_u.py` | flat/recursive totals for the corpus | — |
| **corpus twin identity (build STEP 0b)** | vmbc's `ccwrap.sh` with `VMOPT_MODE=BCdU` pointed at `vmopt_tg.py`, plus `variants.py R`, over `make test-corpus` (and `RXTFLAGS="-fno-splice-calls --engine=vm"`) | every `.rxt` expectation | — |

Not a find/scan/skip/verify method, so the measurement script's method cards do not
apply. The gap card (`rate.sh` against jit) and the census card are the ones to re-run
at landing.

## Build plan

One build, three stages. Each stage is checked for answer identity before the next.
It lands after [INLINE-C] (the one-build gate, plus row 7's code-site contract) and
after lane/trailgc merges.

0. **STEP 0 (measure before code).**
   - The corpus census and corpus twin identity above.
   - The 29 unsampled bench patterns (`notsampled.tsv`).
   - The `utf8/` family with `-e utf8`.
1. **Stage 0, R.**
   - Change the emitter's macro text and every matcher prologue and exit.
   - Card: the gap rates, expected -8 to -18 % instructions; 0 on inlined artifacts.
   - Checks: identity sweep; a sabotage that drops one write-back (e.g. `steps_left` at
     the step give-up) must be caught by a budget witness; one that skips the reload
     after compaction must be caught by `run_trail_compact.sh`.
2. **Stage 1, SLOT-FLOW verdicts.**
   - vmbc's B stage plus row 4, with checkpoint pruning and the margin.
   - The cost model sizes from the verdicts.
   - Independent checker: `vmopt_tg.py` (text) re-derives every DELETE and UNTRAIL.
   - Sabotage rows: vmbc's list, plus the two above (entry liveness, MAYFRAMES), plus
     R25 E5.
   - Card: the census (flat -21.7 %, entries -87.8 %) and the gap subjects.
3. **Stage 2, C** (vmbc's stage 2, unchanged).
4. **Landing.**
   - One abi bump and the mover census.
   - Spec re-pins: vmbc's list (limits §4, §5¶6, match_api §10.1¶1, §10.6, tuning
     §2.11¶2, the guide) plus limits §3.2's stamped capacities for statically bounded
     artifacts.
   - Close [ART-TRAIL-ELIDE] into this row.

**File, not build:**

- P (packed entries): trigger, the default trail capacity question.
- Narrow frames: trigger, the post-B+C one-shot regime still bound by frame bytes.

## Questions for Frank

1. **Should the trail cleanup decide three things about each slot write, not two?**
   - **Problem.** vmbc's B deletes a write when nobody reads the NEW value. On the
     bench's ordinary (non-recursive) patterns that almost never happens: a capture is
     read by a backreference or by the final answer. So B helps only the recursive
     scanners.
   - **What the census found.** The cost on ordinary patterns is the RECORDING of the
     OLD value, so that a backtrack can put it back. That old value is usually
     worthless: nothing reads it before it is overwritten again. Skipping the record:
     - `(\w)(\w)\2\1` runs 63 % faster;
     - a phone-palindrome pattern 47 % faster;
     - 21.7 % fewer instructions over the 41 ordinary bench patterns sampled.
   - **Forces.**
     - It is the same analysis B needs, so it adds one table row and one small pass.
     - The risk is real: an unrecorded write is exactly the kind of bug R25 E5 was. The
       design's guard (the backtrack edges in the analysis) caught both sabotages I
       planted.
     - It also shrinks the trail capacity stamped on small patterns, which shows in
       `rx_info`.
   - **Leaning.** Yes: put it in the same build and stage as B, and fold
     [ART-TRAIL-ELIDE] into it.
2. **Should the register fix go first, inside the same build?**
   - **What it is.** The generated matcher keeps its stack-depth counters in memory and
     reloads them around every capture store, because the compiler cannot prove they
     are separate. Keeping them in local variables cuts 8-18 % of instructions on the
     big recursive scanners (15-33 % of cycles), and changes nothing on small patterns.
   - **Forces.** It is the smallest and safest change here, and it touches every VM
     artifact's text (so a version bump either way).
   - **Leaning.** Stage 0 of the same build: one version bump, and it makes every later
     stage's measurement cleaner. If you would rather see something small land soon
     after [INLINE-C], it can also ship alone; nothing depends on the other stages.
3. **Packed 8-byte trail entries: wait?**
   - **What they give.** Half the trail memory: on today's code, one-shot page faults
     -41 to -50 %. After B+C the trail is nearly empty, so that gain mostly disappears,
     and they cost a little in instructions.
   - **Leaning.** File a row and decide it together with vmbc's question about
     shrinking the default trail.

## STATE AT HANDOFF

- STATE: complete (design and measurement, as briefed; no build).
- Rulings file `docs/dev/lanes/trailgen_rulings.md`: empty at every read (start, before
  each commit, before this report). Last entry applied: none.
- OWED: none.
  - The corpus census was NOT run. The box lock yielded to ready queue jobs 680, 681 and
    690 at 11:25, and the brief says not to queue and wait. It is the build's STEP 0,
    with commands in Measurement cards.
- Box use:
  - one declared 50-pattern sample (single process: 50 emits plus gcc builds; the
    first pass's 18 emits were reused after a prototype fix, not repeated);
  - 16 trap compiles and 3 sabotage compiles;
  - single-process rate runs.
  - No timing window was running (job 622 is a correctness run, no quiet gate). Load was
    5-7 from that job. Nothing ran after 19:00.
- Evidence: `docs/dev/lanes/trailgen_evidence/` (generators, drivers, checkers, raw
  tables); full scratch in `/var/tmp/pcrec-pcrec/scratch/trailgen/` (twins under `tw/`
  and `cs/`).
- Not done: R for artifacts with a second matcher function (prototype limit, 2 of 46);
  B+C+U on the 11 callout bench artifacts (vmopt refuses them; row 7).
