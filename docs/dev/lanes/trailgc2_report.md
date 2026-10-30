# Lane trailgc2: K134 trail compaction at checkpoints (option 4), and the remaining gap to pcre2-jit

Lane trailgc2 (opus), 2026-10-29, on `lane/trailgc` (worktree
`worktrees/trailgc`, base b05ccfc0b), resuming `docs/dev/lanes/trailgc_report.md`.
Build go: Frank, 2026-10-29. Scratch is under
`/var/tmp/pcrec-pcrec/scratch/trailgc2/`. The bench checkout was only read.

## Summary

- **Option 4 is taken (D183).** The compaction runs at checkpoints on the VM
  program's backward jumps and region returns, never at the trail write. It
  covers everything option 1 covered, and more:

  | | base | option 1 | option 4 |
  |---|---|---|---|
  | flat cscan subjects, default arm | FRAMES | answer | answer |
  | `^(a(?1)?b)$`, largest default n | 342 | 512 | **763** |
  | cscan nest-brace, deepest default answer | 49 | 80 | **85** |
  | idents-1m instructions (never-full path) | 188.58 M | 209.84 M (+11.3 %) | 191.67 M (**+1.6 %**) |
  | nest-paren-32k | 30.74 M | 32.38 M (+5.3 %) | 31.07 M (**+1.1 %**) |
  | splice-1m | 46.76 M | 52.76 M (+12.8 %) | 47.76 M (**+2.1 %**) |

  All answers equal libpcre2 10.46's.
- **Soundness.** Every cycle of the emitted program passes a checkpoint. A
  run between two checkpoints executes each trail-write site at most once, so
  the artifact's site count M bounds the growth there. The floor is
  `cap - min(M, cap/2)`. A single stretch longer than the room left still gives
  up at the write, exactly as before; it never gives a wrong answer. CUT-INV
  and the K36 call snapshot hold: the compaction keeps order and moves each
  frame's mark down with its entries. A checker reads the emitted C and
  verifies the property. It found one real miss during the build (the
  empty-iteration guard's conditional back-jump), now fixed.
- **Built and checked locally.** The emitter, a new `make test-vm` section, K134
  cells in `cscan.rxt` (base gives up on 10 cases, libpcre2 and option 4
  answer), seven sabotage rows S1790-S1796 (every one detected by hand, including
  the backward-goto and return checkpoints), the specimen re-aims, spec hunks,
  and abi 91 -> 93. The full suite and mech are OWED: queued jobs
  690-trailgc-test and 691-trailgc-mech.
- **Remaining gap to pcre2-jit**, in cycles per call (box loaded; read the
  instruction ratios beside them):

  | subject | cycles ratio | instr ratio |
  |---|---|---|
  | idents-1m | x2.7 | x2.3 |
  | nest-paren-32k | x6.5 | x3.0 |
  | nest-brace-100k | x4.4 | x3.2 |
  | splice-1m | x2.6 | x2.0 |
  | comment-5m | x2.1 | x2.6 |
  | js-1m | x4.8 | x4.5 |

  The trail is 35-73 % of pcrec's cycles. On flat input that is candidate B's.
  On the calling members (nest-brace, js) more than half the trail is the call
  snapshot and restore, which is candidate C's. After the no-trail twin,
  nest-paren is still x4.0, which is D (serial alternation). Depth: the default
  arms reach 85 vs 176 levels (nest-brace) and 19 vs 150 (JSON arrays). The
  large arms reach 1,062,545 vs 909,088 levels (nest-brace) and 220,857 vs
  666,665 (JSON).

## Premise test

I confirmed it on this box. The base build (b05ccfc0b) gives `rc=-3`
(`PCREC_ERR_FRAMES`) on the default arm for idents-1m, comment-5m, splice-1m,
nest-paren-32k and nest-paren-100k. The old option-1 build
(`scratch/trailgc/new/drv`) answers idents-1m with `rc=1`, span 0..1000007.
libpcre2 10.46 (interp and JIT) answers every flat subject (lane trailgc's
premise test; re-checked here with `gap/p2`, JIT spans 0..1000007, 0..65547,
0..1000009, 0..5000011). The old report's option-2 prototype numbers (idents
+2.2 %, nest-paren +1.1 %) are its own measurements; option 2 was not rebuilt.

## Option 4 design

**Where the checkpoints go** (`src/gen/emit_vm.c`):

- **Backward jumps.** `vm_goto` writes `<PREFIX>_TRAIL_CHECK();` before a jump
  to a label that is already written, when a `<PREFIX>_SET` has been written
  since that label (`vm_jump_closes_trail_cycle`: the label records the SET
  count at its definition). `vm_jump` is the same rule for sites that write
  their own `goto` inside a condition (the empty-iteration guard's `!=`
  back-jump): `{ <PREFIX>_TRAIL_CHECK(); goto L; }`.
- **Region returns.** `vm_region` writes a checkpoint after the callee's
  restores and before the indirect `goto *call_ret`. A chain of returns writes
  restores once per level and passes no backward jump, so it needs its own.
- **Call entries need no checkpoint of their own.** Recursion always jumps back
  to an earlier label, so the backward-jump rule already covers the call.

**Why every unbounded growth passes one.** The program is a linear text with
jumps. Any cycle in it must contain an edge that goes back in the text: a
backward `goto`, a return to a call's return label, or a resume after
backtrack. A trail write on a cycle lies inside the range of some backward
edge of that cycle. The emitter puts a checkpoint on every backward goto whose
range contains a SET, and on every return. A resume after backtrack restores
the depth its push saw, so it adds no growth. So no cycle that writes the
trail can avoid a checkpoint. Between two consecutive checkpoints each SET site
runs at most once. The growth is then at most M entries, where M = `v->nset`,
the artifact's SET-site count, emitted as `margin` in the floor function.

**The trigger (rule E, after six variants; see Measurements).**

- `<p>_trail_gc_floor(cap) = cap - min(M, cap/2)`. It is a `noinline`
  function. That is MEASURED, not principled: inlined, gcc moved the matcher's
  register allocation and the checkpoints cost 3.8 % instead of 1.1-2.1 %.
- `<PREFIX>_TRAIL_CHECK()`: `if (trail_depth > gc_at) gc_at = compact(run)`.
  `gc_at` is a matcher-local variable initialised from the floor. As a
  run-state field it cost 8-20 more instructions per check.
- `compact` returns the floor again if `w + cap/4 <= floor`. Otherwise it
  returns `(size_t)-1`, and the attempt stops compacting. A compaction then
  frees at least a quarter of the capacity's worth of writes before the next
  one, so the work is at most four entry visits per trail write.
- Nothing gives up earlier than today. The stock
  `if (depth >= cap) return R_FRAMES` stays at the write. If a stretch longer
  than the room left arrives, it gives up there, as it always did.

**Invariants.**

- CUT-INV holds: compaction rewinds nothing and changes no slot.
- K36's positional call-return read `trail[resume_stack[call_top].trail_mark + j]`
  still holds. The compaction keeps entry order and moves each live frame's
  mark to its new segment start. A call frame's parked values are the oldest
  entries of their segment, so they are kept, in order, at `mark + j`.
- The fast tier still escalates once on a long flat subject (checked). Its
  kept trail cannot leave a quarter free, so it stops compacting and gives up
  to the deep tier.

## Measurements

Method: `perf stat -e instructions:u`, per call = (11 calls - 1 call) / 10,
`_in` with NF=64 and NT=10M, so the trail never fills on these subjects. The
builds are gcc -O2, and also -fPIC as the bench builds; -fPIC gives the same
numbers. The pattern is `scratch/trailgc/cscan.pat` (cscan.rxt's decoded
pattern).

| variant | idents-1m | nest-paren-32k | splice-1m |
|---|---|---|---|
| base | 188.58 M | 30.74 M | 46.76 M |
| option 1 (at the write) | 209.84 M | 32.38 M | 52.76 M |
| option 4, checkpoints compiled out | 188.58 M | 30.74 M | 46.76 M |
| option 4, trigger in the run state | +4.4 % | | |
| option 4, matcher-local trigger, floor inlined | 195.84 M | 31.92 M | 48.09 M |
| **option 4 as built (noinline floor)** | **191.67 M (+1.6 %)** | **31.07 M (+1.1 %)** | **47.76 M (+2.1 %)** |

Cycles (minimum of 5, box loaded by kit job 622, noisy): base 59.71 / 9.55 /
13.96 M, option 1 61.53 / 11.59 / 15.56 M, option 4 (inlined floor) 58.71 /
8.87 / 13.95 M, option 4 as built 58.06 / 10.27 / 13.61 M. None of these
differ from base by more than the run-to-run noise. Checkpoints executed per
call: about 1.0 M (idents), 65.5 k (nest-paren), 333 k (splice).

**Trigger rules tried** (nest-brace default depth; the specimen's default n
in brackets where measured):

| rule | nest-brace |
|---|---|
| doubling trigger max(floor, 2w) | 75 |
| option 1's success rule (2w < cap), then off | 75 |
| margin set by hand to 31 | 79 |
| geometric retry | 120, but the per-write work is unbounded, rejected |
| 2M guard | 104, unbounded on a fast-tier artifact, rejected |
| 3cap/4 room | 91, per-write cost 2x E's |
| **E: floor + quarter room** | **85 (specimen 763)** |

Measured stretch: the largest trail growth between two checkpoints is 31 on
the cscan subjects. The checker's static heaviest path is 61, against a margin
of 255 on cscan, and 10 against 15 on the specimen.

## Decision

**Option 4.** The rule was: take option 4 if it covers everything option 1
covers (all flat cscan subjects answer, the specimen reaches the same n,
nest-brace is no worse) at no more than about 3 % instructions on the
never-full path. It does all of that:

- all flat subjects answer;
- the specimen reaches 763 (option 1: 512);
- nest-brace reaches 85 (option 1: 80);
- the cost is +1.1-2.1 %.

The specimen and nest-brace go further than under option 1 because the
quarter-room rule needs less free room than option 1's half-capacity rule.
Recorded as D183.

## What was built

- `src/gen/emit_vm.c`: `vm_trail_check`, `vm_jump_closes_trail_cycle`,
  `vm_jump` (the conditional back-jump form), the checkpoint in `vm_goto` and
  `vm_region`, and the SET-site count and per-label SET count in `Vm`.
  `vm_emit_trail_compact` emits `<p>_trail_gc_floor`, `<p>_trail_compact` and
  `<PREFIX>_TRAIL_CHECK`, only when the program has a checkpoint. The
  matcher's prologue declares `<p>_trail_gc_at`. The trail write is stock.
  The header comment states the argument above.
- `src/gen/attr_text.c` and `src/core/internal.h`: `PCREC_ATTR_COLD` and the
  `noinline` reader rows.
- Spec:
  - `docs/spec/limits.md` §4: ¶1 763/764, ¶2 `4n + 17`, a new ¶3 on the
    compaction; §5¶6 1,526 bytes.
  - `docs/spec/match_api.md` §10.1¶1 and §10.6¶2-3: the 64 MB table
    re-measured. Frames now bind at 838,860 levels, and the ceiling is
    `min(nframes / 2, (ntrail - 17) / 4)`.
  - `docs/spec/tuning.md` §2.11¶2.
  - `docs/guide/tuning-and-limits.md` (its two numbers).
- K134 is FIXED on lane/trailgc, pending merge (`docs/dev/known_issues.md`).
- D183 added (`docs/dev/decisions.md`).
- R2:
  - Comments fixed in `S155`, `S179`, `S180` and
    `tests/codegen/run_tiered_entry.sh`.
  - `docs/design/frame_buffer_design.md` gets a dated note. Its measured rows
    are its own record from before K134.
  - Also dated records, left as they are: `docs/design/two_tier_entry.md`
    (n=342, 8.982), `docs/design/sr_d27_extract.md` (342/343),
    `docs/design/subroutines_design.md` §3324 and
    `docs/design/artifact_size_term.md` (684 B).
  - `limits.md` §8a's `.subject_ceiling` table (512/341) is the frames-derived
    DECLARED stamp. It is unchanged by this work: the measured reach is now
    763, above the declared 512.

## Tests and sabotage

- **`tests/vm/run_trail_compact.sh`** (new; in `make test-vm`; mech arm
  `trailcompact`), with `trail_compact_driver.c` and `trail_checkpoints.py`. It
  has 11 witnesses: four long cscan subjects, the specimen, and possessive,
  atomic, nested-possessive, backreference, greedy and empty-guard loops. For
  each it checks:
  1. **The emitted-C check.** No trail-writing cycle without a checkpoint, the
     heaviest checkpoint-free path is at most the margin, and there is no SET
     inside a C loop.
  2. **Answers at every trail capacity.** Every rung from 1 up to the plain
     high-water either gives up or equals the large-buffer answer, captures
     included.
  3. **Reach.** The eight `compacts` witnesses must answer below their plain
     high-water. Only a compaction can do that, so a witness that stops
     reaching it fails.
  4. **The documented boundary.** n=200: 816 gives up, 817 answers.
  5. **The fast tier.** It escalates exactly once and answers.

  Population line: 11 witnesses, 8 compacting, 2 probes. Result 34/0 locally.
  `TRAIL_CORPUS=1` adds the corpus-wide emitted-C check, which runs in job 690.
  Samples run by hand on 45 patterns each from captures/, recursion/ and
  lookaround/ were clean. The heaviest path was 19/22, 61/255 and 5/5.
- **K134 cells in `tests/recursion/cscan.rxt`** (generator `gen_cscan.py`,
  oracle libpcre2 10.46 through the committed ctypes binding): identifiers
  x350, splices x700, parentheses 300 deep, 60 mixed statements, braces 60
  deep. The base pcrec fails 10 of the 145 cases and option 4 fails none.
- **Specimen re-aims** (helper commit 11da0ff07): `framebuffer.rxt`,
  `d27/sr_depth.rxt` + `sr_gen.py`, `fb_exact_driver.c` (`trail_for = 4n + 17`,
  n >= 7), `fb_mmap_driver.c` + `run_frame_buffer.sh` (838,860/838,861),
  `ts4_driver.c` + `run_stackdepth_tests.sh` (763, 1,526 B).
- **Sabotage rows**, each planted by hand in a scratch copy and run against
  `run_trail_compact.sh`; all DETECTED:

  | row | plant | failed / passed |
  |---|---|---|
  | S1790 | keep a slot's newer entries, drop the oldest | 6 / 24 (answers change) |
  | S1791 | the seen map is never cleared per segment | 3 / 28 (380 mismatches on the specimen) |
  | S1792 | frame marks not moved | 2 / 32 |
  | S1793 | no quarter rule | 2 / 32 (the 816 probe answers; the fast tier never escalates) |
  | **S1794** | **no checkpoint on backward gotos** | 17 / 17 (emitted-C check + answers) |
  | **S1795** | **no checkpoint on returns** | 4 / 30 (emitted-C check on the specimen) |
  | S1796 | no checkpoint on the conditional back-jump | 2 / 32 (emitted-C check) |

  The mech run of these rows plus S693 is job 691.

## Movers and abi

- **abi 91 -> 93**, provisional; 92 is the kit's S3. Every reader found by
  grep was updated:
  - `PCREC_ARTIFACT_ABI` in `emit_dfa.c`;
  - `match_api.md`: the guard block, rx_info row 1, 6¶17;
  - `S693`;
  - the codegen `ABI_EXPECT` and its transition string;
  - `abi_changelog.md`, with a new entry naming the moved bytes.
- **Mover census**: `docs/dev/lanes/trailgc2/movers.py`. It masks the abi and
  the `_VM_PROGRAM_BYTES` value. A moved cell must be class `checkpoints`: the
  working text minus the floor/compact/macro block, the `TRAIL_CHECK();`
  lines, the `gc_at` declaration and the guarded-jump braces equals the
  reference. A smoke run on 7 patterns gave 13 identical, 22 checkpoints and 0
  unexpected. The full census runs in job 690.
- What moves: VM artifacts whose program writes a slot inside a loop or a
  called region. DFA artifacts move only the abi digits.

## Remaining gap to pcre2-jit

Method follows l9look. Both engines read the same pattern files, the bench's
`cscan-onig.rx` and `wild-json-validate-onig.rx`.

- pcrec: `_in` with NF=4M, NT=64M (`gap/cscan`, `gap/json`).
- pcre2-jit: libpcre2 10.46, `pcre2_jit_stack_create(32K, 1 GiB)` with a
  1 GiB heap limit (R1: the bench's `pcre2-jit-deep`; scratch `gap/p2.c`,
  mode `jg`).
- Per call = (11 - 1) / 10. Cycles are the minimum of 8 runs over two passes,
  at box load 16-27 (kit job 622 and the queue). Instructions are stable.
- No-trail twin: `RX_SET` without `RX_TRAIL`. It is an upper bound on trail
  cost and is not a correct matcher on nest-brace.
- Call entries: a counting twin. Its snapshot entries equal its restore
  entries.

| subject | pcrec cyc | jit cyc | ratio | instr ratio | trail share | call entries of the trail | no-trail vs jit |
|---|---|---|---|---|---|---|---|
| idents-1m | 64.9 M | 23.7 M | x2.74 | x2.33 | 56 % | 0 % | x1.21 |
| nest-paren-32k | 11.6 M | 1.77 M | x6.5 | x3.00 | 38 % | 0 % | x4.0 |
| nest-brace-100k | 82.6 M | 18.9 M | x4.4 | x3.23 | 63 % | 55 % (1.9 M calls) | x1.63 (cost only) |
| splice-1m | 16.8 M | 6.41 M | x2.62 | x2.02 | 73 % | 0 % | x0.72 |
| comment-5m | 57.3 M | 27.1 M | x2.11 | x2.55 | 35 % | 0 % | x1.38 |
| js-1m | 114 M | 23.9 M | x4.77 | x4.45 | 64 % | 65 % (6.3 M calls) | x1.72 |

Attribution:

- **B (frameless-region write coalescing).** It covers the whole trail share on
  idents (56 %), splice (73 %) and comment (35 %). On nest-brace and js it
  covers the part that is not call snapshot (about 28 % and 22 % of cycles,
  estimated by entry count). It is the largest single term. Without the trail,
  splice is faster than JIT and idents is within x1.21.
- **C (call snapshot narrowed by liveness).** At most the call entries' share
  of the trail: about 35 % of cycles on nest-brace and 42 % on js. This is an
  upper bound and an estimate, since it assumes trail cost is proportional to
  entries. C also binds the default depth (below).
- **D (first-set alternation dispatch).** It is the residual on nest-paren:
  x4.0 after the no-trail twin, with 11 pushes and 9 failing branches per byte
  (l9look's count). It is likely part of the x1.4-1.7 residuals on comment,
  nest-brace and js. That share is not separated here.
- **New: none found.** The checkpoints themselves cost +1-2 % instructions and
  no measurable cycles.
- **Not engine cost.** js-1m's bench x21.9 is mostly first touch of the
  `_in` storage in a single timed call (l9look). This method keeps buffers
  resident and does not see it.

Depth limits:

| arm | pcrec | pcre2-jit |
|---|---|---|
| default, cscan nest-brace levels | **85** (base 49) | **176** (default JIT stack) |
| default, JSON array nesting `[[..1..]]` | **19** (base 17) | **150** |
| large: pcrec `_in` 512 MiB frames + 512 MiB trail vs jit-deep 1 GiB, nest-brace | **1,062,545** | **909,088** |
| large, JSON array nesting | **220,857** | **666,665** |

On the default arms, the depth still binds on the call snapshot width:

- 19 slots per call on cscan, about 33 on JSON;
- each snapshot plus its restore costs about 2 x W trail entries per level,
  which compaction cannot drop while the call frame is live.

That is candidate C. The large-arm JSON gap has the same cause.

## Measurement card

| card | command (scratch `/var/tmp/pcrec-pcrec/scratch/trailgc2/`) | reads |
|---|---|---|
| never-full instructions | `mk.sh DIR PCREC`, then `perfcall.sh DIR/drv SUBJ` | idents-1m, nest-paren-32k, splice-1m |
| specimen boundary | `mint N...` (bisects minimal trail per n with frames = 2n) | 4n + 17 |
| default depth | `gap/depth.sh pd 4096`; `gap/jdepth.sh pd 100000`; JIT `jd` | 85 / 19; 176 / 150 |
| large depth | `NF=13421772 NT=33554432 gap/depth.sh pl 8000000`; `gap/depth.sh jg 8000000` (same for jdepth) | 1,062,545 / 909,088; 220,857 / 666,665 |
| gap rates | `gap/rate.sh` (stock, no-trail twin, jit-deep; min of 5 cycles) | the table above |
| call entries | `gap/{cscan,json}_cnt/drv SUBJ r` (NF=4194304 NT=67108864 REPS=1) | trail writes / return restores |
| 64 MB reservation | `fbm/fb 763 100000 400000 838860 838861` | match_api §10.6 table |
| checks | `bash tests/vm/run_trail_compact.sh`; `TRAIL_CORPUS=1` for the corpus | 34/0 |

## STATE AT HANDOFF

- Branch `lane/trailgc` holds option 4 complete, with WIP commits through this
  report. Nothing is merged to main.
- Local results:
  - `run_trail_compact.sh` 34/0;
  - the cscan.rxt harness 145/0;
  - the k18 witness 24/0;
  - all seven sabotage rows DETECTED by hand.
- A local section run (`scratch/trailgc2/sections.sh`, under `boxlock run`)
  covers test-codegen, registry, rxtsource, vm, recursion, frame-buffer,
  stackdepth and the tests/recursion harness. It waits for the box behind the
  queue. I left it running; its log is `scratch/trailgc2/sections.log`. It is
  not a verdict this lane read.
- The helper lane validated its re-aims (11da0ff07): the framebuffer.rxt and
  sr_depth.rxt harness passed 88/0, `make test-frame-buffer` (ASan) 7/0, and
  `make test-stackdepth` 39/0. It did not run sr_gen.py; the spans were
  hand-checked against libpcre2 10.46.
- OWED: trailgc-test trailgc-mech.
  - Job `690-trailgc-test`: build, strict, mover census, `TRAIL_CORPUS=1`
    checkpoint sweep, full `make test`.
  - Job `691-trailgc-mech`: S1790-S1796 + S693.
  - Both are queued and run before 16:00 today if they reach the front.
    Otherwise their `--ready` holds them to 2026-10-30T13:30.
- Gap measurement: done. The cycles were taken under load (16-27). A
  quiet-box re-run of `gap/rate.sh` would firm up the cycle ratios. The
  instruction ratios do not need it.
- For the manager: abi 93 is provisional, so renumber at landing if the kit's
  92 lands differently. Candidates B, C and D are not built.
