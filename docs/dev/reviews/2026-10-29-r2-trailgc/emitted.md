# Critic lens EMIT (emitted-vs-replaced), round trailgc, 2026-10-29

SUBJECT 801ad1214 (review tree worktrees/crit-trailgc/build/pcrec), BASE b05ccfc0b
(built at /var/tmp/pcrec-pcrec/scratch/crit-trailgc/base/build/pcrec). Scratch:
/var/tmp/pcrec-pcrec/scratch/crit-trailgc/emitted/ (gen.sh, perf/build.sh, perf/drv.c,
perf/perf.sh, perf/perf1.txt). Driver = find-all through `rx_search_in` with 1M frames /
4M trail (mode 0), or the stamped default `rx_search` (mode 1), or a given trail cap (mode 2).
perf: `perf stat -x, -e instructions:u,cycles:u -r 5 taskset -c 7`, gcc 15, box load ~5
(cycles are noisy; instruction counts are exact and repeat to 0.00%).

## Findings

### EMIT-1: the checkpoint's hot-path cost exceeds D183's +1.1-2.1 % on two of six loop-heavy VM patterns (up to +3.8 %), because the cold call's rejoin un-registers `trail_depth` for the whole loop
- status: CONFIRMED
- repro: `perf/build.sh NAME pat PATTERN` (base + subject, -O2/-O3), then `perf/perf.sh`.
  Instructions:u, never-full (no compaction runs; BASE answers at the same buffers, answers identical):

  | pattern / subject | O2 delta | O3 delta |
  |---|---|---|
  | cscan / idents 300 KB | +1.10 % | +1.00 % |
  | cscan / mixed C tokens 300 KB | +0.93 % | +0.77 % |
  | cscan / nest-paren 32k | +1.07 % | +0.85 % |
  | cscan / nest-brace 2k | +0.76 % | +0.58 % |
  | `(?:(\w+)=(\d+);)*end` / 100k pairs | +0.44 % | +0.44 % |
  | same, `*+` | +0.43 % | +0.44 % |
  | `(foo\|bar\|baz)+x` / 4000 x 30 words | +1.59 % | +1.59 % |
  | `(\w+)(?:,(\w+))*;` / 10000 rows x 20 | +0.84 % | **+3.46 %** |
  | `(\((?:[^()]++\|(?1))*\))` / 30000 x `(a(b(c)d)e)` | **+3.82 %** | **+3.48 %** |

  cscan sits inside the claim; the two bold rows do not. Mechanism, read off
  `gcc -O3 -S` of the csv artifact (perf/csv/{base,subj}/ma3.s): BASE keeps
  `run->trail_depth` in `%r10` across the `(?:,(\w+))*` loop (`addq $2, %r10`); SUBJECT
  reloads it at the loop head (`.L81: ... movq 88(%rsi), %r11`) because the cold path
  (`rx_trail_compact(run)`, which writes `run->trail_depth`) rejoins at the latch, and the
  frame store turns into an SSE pair build (`movq %rcx,%xmm0; movq %r11,%xmm1;
  punpcklqdq; movups`). The checkpoint itself is 2 instructions (`cmpq %r11,%rdi; jb
  .L102`), the loop body grows ~25 -> ~31 instructions: ~7.5 instructions per iteration
  measured (453 M / 300 reps / 10000 rows / 20 iterations). This is the SAME
  reload-at-merge-point mechanism D183's Why rejects for option 1, moved from every write
  to every latch; it is cheap where the loop body is long (cscan) and not where it is a
  few dozen instructions. matcher text grows 212 vs 188 asm instructions. Cycles (3
  interleaved rounds, -r 5, box load ~5): csv O3 -0.6 / +4.3 / +3.2 %, parens O2 +4.1 /
  +10.9 / -3.3 %: noisy, but not contradicting the instruction delta.
- severity: speed
- effort: small-to-medium. Options: (a) state the per-latch cost honestly in D183 / limits
  §4 (a range per loop-body size, not +1.1-2.1 %); (b) skip the checkpoint where it can never
  compact (EMIT-2), which removes it from exactly these short loops.
- blast radius: every VM artifact with a checkpoint (any trail-writing loop or a region
  return): `rx_match_anchored` of csv-like / recursive-paren-like patterns.
- location: src/gen/emit_vm.c vm_emit_trail_compact (the `cold, noinline` call that rejoins);
  docs/dev/decisions.md D183 (Decision, "+1.1-2.1 %").

### EMIT-2: checkpoints land on hot loops where compaction can never drop an entry (a frame per turn, each slot written once per turn; a once-only guarded SET)
- status: CONFIRMED (placement and cost); the "never drops" claim is argued from TRAIL-SEG, not run.
- repro: `build/pcrec --features all -o g.c --pattern '(\w+)(?:,(\w+))*;'`: the loop
  `rx_L2: RX_PUSH(&&rx_L8,..); ... RX_SET(G2_START); ... RX_SET(G2_END); rx_L7: RX_TRAIL_CHECK(); goto rx_L2;`
  pushes a resume frame on EVERY turn before its two writes, so every turn's writes sit in
  their own segment with distinct slots: TRAIL-SEG keeps all of them, the compaction can
  only return `(size_t)-1`, and the frame stack grows in lockstep. Likewise
  `(foo|bar|baz)+x`: the revdet scan latch `rx_L5: ... if (rx_rv0_iteration == 1UL) { RX_SET(REVDET0_LOW,..) } RX_TRAIL_CHECK(); goto rx_L3;`
  carries a checkpoint on every turn for a write that runs once per attempt
  (`vm_jump_closes_trail_cycle` counts SET SITES in program text, so a guarded
  first-iteration SET counts). These two are the +0.84/+3.46 % and +1.59 % rows of EMIT-1.
  Also `(?:(\w+)=(\d+);)*end` (non-possessive, frame per turn) gets one.
  docs/spec/limits.md §4 paragraph 3 (lane/trailgc) (on the branch) already says it: "A pattern whose every pass
  pushes its own resume frame keeps every entry and gains nothing." The emitter still pays
  a checkpoint on every turn of exactly those loops.
- severity: speed / design
- effort: medium. The general form: a cycle whose every turn pushes a frame that is not cut
  inside the turn (net `resume_depth` growth > 0 per turn) and writes each slot at most once
  per turn cannot leave a droppable entry, because each turn's writes form their own
  segment; such a back-edge needs no checkpoint (a cut AFTER the loop merges segments, but
  then the loop no longer turns, and any enclosing loop carries its own checkpoint). This is
  a fact the emitter has at `vm_goto` time only if it tracks pushes like it tracks `nset`
  (a `npush` clock next to `nset`), so it is the same mechanism, not a special case. The
  once-only guarded SET is a narrower case (`vm_set` under `iteration == 1`). Unlock: the
  short frame-per-turn loops are where EMIT-1's excess lives, so this would likely bring
  the measured range back inside D183's claim.
- blast radius: VM artifacts with non-possessive capture loops (the common case).
- location: src/gen/emit_vm.c `vm_jump_closes_trail_cycle` / `vm_goto`.

### EMIT-3: a compaction visits every live frame, so D183's "at most four entry visits per trail write" fails when live frames exceed the trail capacity; the extra work is charged to no budget
- status: CONFIRMED
- repro: pattern `(?:a|ab)*(?:(\w+)=(\d+);)*+end` (first loop pushes 1-2 frames per `a` and
  writes nothing; the possessive loop's writes all fall in the top segment), subject
  `'a'*100000 + 'k=1;'*100000 + 'end'`, `rx_search_in` with nframes = 2^20 and ntrail = T
  (`perf/frm/{base,subj}/drv2 perf/frm.txt 1 2 T`):

  | T | BASE | SUBJECT |
  |---|---|---|
  | 64 | FRAMES, 0.00 s | match, **3.54 s** |
  | 256 | FRAMES, 0.00 s | match, 0.50 s |
  | 4096 | FRAMES, 0.00 s | match, 0.03 s |
  | 4194304 | match, 0.00 s | match, 0.00 s |

  Doubling both halves (`frm2.txt`, 200k + 200k, T=64): 10.12 s, i.e. ~quadratic. Each
  compaction walks `f = 0..resume_depth` (100k frames) to reclaim ~T/2 entries. Answers are
  right; the cost is the frame walk. `docs/spec/limits.md` §3.1¶2 charges "a frame
  discarded at a cut" to the work budget, but this walk charges nothing, so neither budget
  stops it (§7¶3 does disclaim a total-time bound).
- severity: speed / design (doc: D183 Why and the vm_emit_trail_compact comment claim the
  four-visits bound; the function comment does say "the trail plus the live frames").
- effort: small: either (a) bound the trigger by frames too (e.g. the quarter rule counts
  `resume_depth` as visits: keep the floor only if `cap/4 >= (w + resume_depth)/4`-style
  amortization, or stop when `resume_depth > cap`), or (b) start the walk at the lowest
  frame whose mark is above the last compaction's kept prefix (frames below an untouched
  prefix cannot change), or (c) charge the walk to RX_CHARGE_WORK. (b) is the general one:
  it makes the work proportional to what changed.
- blast radius: callers of the `_in` entries (and iterators with buffers) whose nframes far
  exceeds ntrail; NOT the stamped defaults I saw (fast 62/93 or 2/6 frames/trail, deep
  2048/3072: frames <= trail there, so the bound holds within ~2x).
- location: src/gen/emit_vm.c vm_emit_trail_compact (the `for (f = 0; f <= run->resume_depth; f++)`
  loop and the `w + run->trail_cap / 4 <= gc_floor` rule); D183 Why ("caps the work at four
  entry visits per trail write").

### EMIT-4: on the DEFAULT tiered entry, cscan's small inputs pay +15 % instructions: compaction runs inside the fast tier's doomed attempt and lets it run further before it escalates anyway
- status: CONFIRMED
- repro: cscan artifact (perf/cscan/{base,subj}), default `rx_search` (driver mode 1), short
  random C segments built by the python block in this lens's history (perf/seg{5,20}.txt;
  seg5 is `(?{ x = = if 1; })`, 19 bytes). `perf stat -e instructions:u,cycles:u -r 3 taskset -c 7`:

  | subject | BASE instr | SUBJECT instr | delta | cycles delta |
  |---|---|---|---|---|
  | seg5, 80000 reps | 739.6 M | 851.3 M | **+15.1 %** | +14.1 % |
  | seg20, 20000 reps | 711.2 M | 743.6 M | **+4.6 %** | +6.6 % |
  | seg5 via `rx_search_in` (1M frames, 4M trail) | 1464.9 M | 1478.5 M | +0.93 % | |

  Both sides escalate exactly once per call (driver built with `-DRX_TEST_TIER_HOOK`,
  perf/cscan/*/drvh: `esc 1` on both): cscan's fast tier (`RX_FAST_FRAMES 37`,
  `RX_FAST_TRAIL 56`) never answers even a 19-byte segment. With margin 255 > 56/2 the
  floor is 28, so SUBJECT compacts inside the fast attempt (`rx_trail_compact` is 4.95 % of
  samples). Which limit binds, measured with `rx_search_in` at the fast tier's sizes
  (perf/cscan/*/drvm, 10000 calls on seg5): trail 56 / frames 37 -> FRAMES on both sides,
  BASE 1824 instr/call, SUBJECT 3153 instr/call; trail 1,000,000 / frames 37 -> both ANSWER
  (7355 vs 7423 instr/call). So the TRAIL is the binding limit, the compaction cannot rescue
  it (it compacts, cannot keep a quarter free, stops, and the trail fills at the write as
  before), and the ~1330 instructions per call it spends first are pure waste before the
  same escalation. The never-full measurements behind D183 (and limits §3.2¶4's "wasted
  fast attempt") do not see this, because they bind large buffers. `parens`, `csv`, `fbb`
  on the default entry show the same delta as on `_in` (+3.8/+0.84/+1.59 %): it bites where
  the fast tier escalates anyway.
- severity: speed
- effort: small. Candidate general forms: (a) when `margin >= cap/2` (one checkpoint-free
  stretch can use the whole headroom, cscan 255 vs 56) the floor rule promises nothing, so
  start the trigger at `(size_t)-1`; or (b) the fast tier binds no trigger and escalation
  does the job (one mechanism fewer in the fast tier). Control: seg5/seg20 on the default
  entry, plus the trailgc2 fast-tier escalation check, which (b) would change.
- blast radius: default-entry calls on patterns whose fast tier escalates (recursive /
  frame-heavy patterns like cscan) on short subjects, which is the cscan dog-food use
  (inline_c.md 2.3 scans one short segment per call).
- location: src/gen/emit_vm.c vm_emit_search_body (`_trail_gc_at` init from
  `_trail_gc_floor(run->trail_cap)` regardless of tier) and vm_emit_trail_compact's floor
  rule `cap - min(margin, cap/2)`.

### EMIT-5: the checkpoint is invisible to the emitter's own walk: no `vm_ev` event, so `--emit-ir` is byte-identical BASE vs SUBJECT and `--trace` prints no compaction
- status: CONFIRMED
- repro: `diff <(BASE --features all --engine=vm --emit-ir --pattern '(\w+)(?:,(\w+))*;') <(SUBJECT ... same)`
  -> identical (also for `(\((?:[^()]++|(?1))*\))`), while the C gains `RX_TRAIL_CHECK();`
  at the latch / return. A `--trace` artifact of `(?:(\w+)=(\d+);)*+end` runs and prints
  push/set/cut lines but nothing when a compaction moves `trail_depth` and every live
  frame's `trail_mark`, so a trace reader sees the `(trail N)` numbers jump with no cause.
  Its siblings record themselves: `vm_work_at` (emit_vm.c:3636) does `nwork++` AND
  `vm_ev(v, VE_NOTE, ...)`; `vm_trail_check` (emit_vm.c:3488) and `vm_jump`'s inline form
  (emit_vm.c:3504-3511) do `ncheck++` only.
- severity: maintenance / doc (ir_listing.md promises the listing is the emitter's own walk
  "so it cannot drift from the code it describes"; the checkpoint is now code it does not
  describe).
- effort: small: one `vm_ev(v, VE_NOTE, 0, 0, "trail checkpoint")` in vm_trail_check and in
  vm_jump's checkpoint branch (an IR-listing change, not an artifact byte change), and one
  `--trace` line in `_trail_compact` under the trace axis.
- blast radius: --emit-ir readers, any event-based check, --trace users debugging a
  give-up.
- location: src/gen/emit_vm.c:3488 (vm_trail_check), :3504 (vm_jump), vm_emit_trail_compact.

### EMIT-6: the trail capacity is no longer monotone: a cscan run answers at trail 199 and gives up at 200 (and at 615-617 between answers at 614 and 618), because one compaction at a transient peak switches compaction OFF for the rest of the attempt
- status: CONFIRMED
- repro: cscan artifact, `rx_search_in` with 1,048,576 frames and trail T
  (perf/cscan/subj/drvm SUBJECT-FILE 1 2 T 1048576), answer vs the large-buffer reference:
  - seg20 (`perf/seg20.txt`, ~80 bytes): T 180-184 give up, **185-199 answer, 200 gives up**, 201-700 answer.
  - seg80: 609-614 answer, **615-617 give up**, 618-1500 answer.
  - seg300: 837-841 answer, **842-848 give up**, 849-865 answer, **866-869 give up**, 870-1500 answer.
  BASE gives up at every one of these T (its first answer for seg80 is between 3000 and
  6000), so no answer is lost against BASE: the claim "only moves the give-up later" holds
  pointwise. What breaks is monotonicity in the capacity. Cause, from an instrumented copy
  (perf/inst/, an fprintf in `_trail_compact`): at T=199 the compactions keep 38, 39, then
  60 entries and go OFF only late, after which the remainder fits; at T=200 the checkpoints
  fire at other moments, the third compaction lands on a momentary peak of live entries
  (w=51 > floor 100 - q 50) and returns `(size_t)-1`, and the attempt then grows the trail
  unchecked although the live set shrinks again as frames pop. The OFF is decided by one
  sample of a quantity that goes up and down.
- severity: design / doc. limits.md §4¶2 publishes a single threshold ("needs exactly
  `4n + 17` trail entries; one entry fewer returns PCREC_ERR_FRAMES"), which reads as
  monotone; for the specimen it may be, but §4 paragraph 3 (lane/trailgc) states the general rule with no caveat,
  and a caller who sizes `ntrail` by bisection over a workload can land in a hole.
- effort: small-to-medium. General form: make OFF not sticky, e.g. re-arm the trigger at
  `w + cap/4` or at the floor whenever a backtrack has lowered `trail_depth` below the last
  kept `w` (the fail label already moves `trail_depth`; one compare there), or re-arm at
  `max(floor, 2 * w)`-style geometric spacing, which keeps the O(1)-per-write argument
  (each compaction is paid by w fresh writes) without a permanent off switch. Either way,
  state in §4 paragraph 3 (lane/trailgc) that reach in T is not monotone if it stays.
- blast radius: callers of the `_in` entries choosing a trail size; the default tiers are
  single points so they are not affected by non-monotonicity as such.
- location: src/gen/emit_vm.c vm_emit_trail_compact (`return w + run->trail_cap / 4 <=
  gc_floor ? gc_floor : (size_t)-1;` and the `_TRAIL_CHECK` macro's assignment);
  docs/spec/limits.md §4 paragraph 3 (lane/trailgc).

### EMIT-7: every checkpointed artifact grows by ~0.6-1.0 KB of text (+3 to +10 % on small artifacts)
- status: CONFIRMED
- repro: `size` of the driver linked with each artifact (perf/build.sh prints it), text bytes BASE -> SUBJECT:
  kv 10960 -> 11532 (O2, +5.2 %), fbb 9848 -> 10484 (+6.5 %), csv 10600 -> 11208 (+5.7 %),
  parens 10476 -> 11508 (+9.9 %), cscan 30532 -> 31448 (+3.0 %); -O3 similar
  (+540 to +1176 bytes). The fixed part is `_trail_gc_floor` + `_trail_compact` (two
  out-of-line functions per artifact, cold section for the second); the per-site part is
  a compare + the cold-section call block per checkpoint.
- severity: size (low)
- effort: none needed if accepted; note it in the abi changelog entry, which today speaks
  only of byte identity for checkpoint-free artifacts.
- blast radius: VM artifacts with a checkpoint (58 of 136 in this lens's spread).
- location: src/gen/emit_vm.c vm_emit_trail_compact.

### EMIT-8: "sibling of a family": the checkpoint is the fourth member of the count-then-gate family and the third per-loop-turn emitted check, and the only one placed by a structural rule
- status: CONFIRMED (sites read); the unification is a proposal.
- The COUNT-THEN-GATE family (a counter bumped by the site emitter, read at scaffold time to
  decide what the prologue/entry declares): `nclamp` (emit_vm.c:3881, vm_mrl_test) gates
  `mrl_param`; `ngst` (:9223) gates `gst_param`; `nwork` (:3641, vm_work_at) with
  `has_budget` gates `_CHARGE_WORK`; NEW `ncheck` (:3489 vm_trail_check, :3509 vm_jump)
  gates `_trail_gc_at` and the two functions (:13111-13115, beside the
  `v->nclamp > 0 ? pl->mrl_param` / `v->ngst > 0 ? pl->gst_param` arguments). `ncheck` is
  bumped in TWO places that each print their own spelling of the checkpoint (the
  statement form at :3487 and the inline `{ X_TRAIL_CHECK(); goto L; }` at :3510), where
  `vm_work_at` threads an indent through ONE writer precisely to avoid that (its own comment,
  :3629-3635: "the alternative is a second printf at that site, and then nwork and the
  listing's NOTE event would count charges the artifact does not make"). Same lesson; the
  checkpoint should take the indent/inline argument through one writer and one `vm_ev`
  (EMIT-5).
- The PER-LOOP-TURN emitted checks: the revdet scan latch's work charge (emit_vm.c:5834,
  `vm_work(... resume_depth - frame_mark ...)`, emitted in the same latch block that now
  ends `RX_TRAIL_CHECK(); goto rx_L3;` in `(foo|bar|baz)+x`); the counter rung's once-per-trip
  MRL prune (vm_mrl_test at :6125, "ONCE PER TRIP"); and the checkpoint. The first two are
  placed by the construct's emitter, the checkpoint by a structural rule in `vm_goto` /
  `vm_jump` (a backward edge over a `_SET`). The per-backtrack budget checks are a different
  family (fail label `steps_left`, :13297; callout's `--steps_left`, :9075; `_PUSH`/`_TRAIL`
  capacity give-ups in the macros) and are not siblings.
- Proposal (not urgent, one structural member today): the backward-edge branch in
  `vm_goto`/`vm_jump` is now a LATCH HOOK; a future per-turn check (or the revdet work charge,
  if it were ever generalised) belongs there as a declared row, not as a fourth
  construct-local spelling. The `npush` clock EMIT-2 needs would live beside `nset` there.
- severity: maintenance / design
- location: as cited.

## PROBED-AND-HELD

- **Byte identity apart from the abi digits (abi changelog claim).** 136 artifact pairs
  (30 + 13 + 22 patterns x byte/utf8, `--engine=auto` and `--engine=vm`, `--features all`,
  plus 3 callout artifacts without `--emit-main`): plain literals, alternations, bounded
  repeats, lookahead/lookbehind (positive/negative, in loops), backrefs and named backrefs,
  atomic and possessive groups, recursion `(?R)`/`(?1)`, callouts, utf8, case-folding. 78
  have no checkpoint and ALL 78 are byte-identical after normalising `(abi 91|93)` and
  `.abi = 91|93,`; every one of the 136 headers differs only in the abi digits. In the 58
  with a checkpoint, the only removed lines are `RX_VM_PROGRAM_BYTES` (58x) and the vm_star
  empty-guard line (3x, rewritten through `vm_jump`); everything else is additive (the two
  functions, the macro, the `_trail_gc_at` local, `RX_TRAIL_CHECK();` lines). Zero
  "no checkpoint but differs" cases.
- **Checkpoint placement, missing side.** `tests/vm/trail_checkpoints.py` (run as a plain
  script on MY generated files only) over 153 SUBJECT artifacts: rc 0, every artifact passes
  (no checkpoint-free SCC with a `_SET`, heaviest path <= margin). I also read every raw
  `goto %s_L%d` printf in emit_vm.c (32 sites): all target `next`/forward labels or
  fail paths; the conditional back-jumps go through `vm_jump`.
- **Hot-path shape.** gcc -O2 and -O3 asm of the csv and cscan matchers: the checkpoint is
  `cmp; jb` to a `.text.unlikely` block (`rx_match_anchored.cold`) that spills five
  registers around `call rx_trail_compact` only there; `cold, noinline` work as intended.
  The per-attempt `call rx_trail_gc_floor` is sunk by gcc past the early-fail tests:
  `(?:(\d+),)+;` over 500k failing digit attempts and `(?:(\w+)=(\d+);)+end` over 100k
  failing pairs: instructions BASE vs SUBJECT equal to within 300 of 342 M / 2.7 M.
- **Answers.** All perf workloads (9 pattern/subject pairs, -O2/-O3, `_in` and default
  entries) give identical counts and capture checksums BASE vs SUBJECT wherever BASE
  answers; SUBJECT additionally answers cscan idents-1m / mix-1m and several default-entry
  cases where BASE returns FRAMES.
- **Degenerate capacities under ASan+UBSan** (`-fsanitize=address,undefined`): 6
  pattern/subject pairs (kv, kv possessive, csv, recursive parens, cscan x2) x trail caps
  0..70, 97, 255, 256, 257, 511, 513, 1023 x frames 1, 3, 37, 1,048,576 = 1872 runs: 369
  answer exactly the reference, 1503 give up with FRAMES, 0 mismatches, 0 sanitizer
  reports. cap 0/1 (floor = cap, never compacts), cap < 4 (`cap/4 == 0`), odd caps, cap <
  2 x margin (cscan margin 255) all behave; `(size_t)-1` never fires.
- **Large NSLOTS.** `(?:(\w+)=(\d+);)*+end|(x){800 groups}` (NSLOTS 1609, 410 KB of code):
  `seen[1609]` on the stack; trail 64 costs 46.0 M instructions vs 26.8 M at 1 M (no
  compaction) for 20k pairs: the per-compaction memset is visible but bounded; answers
  identical at 64/1024/1 M.
- **Margin vs real checkpoint-free maximum.** The checker reports cscan's heaviest
  checkpoint-free path 61 against margin 255 (the whole-program `_SET` site count); csv 4/4,
  kv 6/6, fbb 4/5, wide-NSLOTS 1600/1607. Conservative only; it moves cscan's deep-tier
  floor from a possible 3011 to 2817 and forces the half-capacity floor in its fast tier
  (relevant to EMIT-4, not a finding on its own).
- **Sticky OFF across a backtrack, the simple shape.** `(?:(\w+)=(\d+);)*x|(?:(\w+)[=:](\d+);)*+end`
  (branch 1 fills the trail then fails) over 3000 + 20000 pairs, caps 14000..26000 by 500
  and 18000..18500 by 25: no hole; SUBJECT answers from 18025 up, BASE only at 1 M. (The
  hole exists, but on cscan's own shape: EMIT-6.)
- **Default-entry cost outside cscan.** parens/csv/fbb on `rx_search` (tiered): same deltas
  as on `_in` (+3.8 / +0.84 / +1.59 %); EMIT-4 is specific to a fast tier that escalates.
- **--trace artifact** compiles and runs with checkpoints (only the missing trace line,
  EMIT-5).
