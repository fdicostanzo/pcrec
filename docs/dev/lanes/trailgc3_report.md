# Lane trailgc3: code review 2026-10-29-r2 applied to the K134 trail compaction

Lane trailgc3 (opus), 2026-10-29, on lane/trailgc (from 801ad1214). Review:
docs/dev/reviews/2026-10-29-r2-trailgc.md and its MANAGER RULINGS. Commits:
f18317611 (src: F1, F5, F9), fcd0c4925 (checks, S1797-S1799; THE LAST SRC
COMMIT and the identity FILEPIN), e730f4f88 (docs, plan rows, guide rule,
re-pins), 75ac19837 (tests/vm/CLAUDE.md), then this report. abi stays 93,
provisional. Evidence: docs/dev/lanes/trailgc3/ (the measurement driver and
script, the F3 tables at -O2 and -O3, the sabotage plant log, the mover census).

## Summary

- **F1 fixed.** One compaction now visits the segments of at most `cap` live
  frames, the topmost; older frames' entries stay as they are. Review witness
  (`_in`, 1M frames, trail 64): HEAD 2.37 s here (review 3.31 s), doubled input
  9.29 s; now 0.00 s and 0.01 s. The bound in D183, limits.md §4¶3 and the
  emitter comment is now at most 12 visits per trail write plus
  `4 * NSLOTS / cap` map bytes. The old "4 visits" counted the trail and not
  the frames.
- **F5 fixed.** The page-sized fast tier never compacts: each fast-tier entry
  sets the run state's new `trail_gc_floor` to never. Its FRAMES give-up
  escalates, and the deep tier compacts. On the tiered default entry, cscan
  19-byte segments went +15.1 % to +0.84 %, and `^(a(?1)?b)$` n=100 went
  +19.5 % to +3.7 %.
- **F3: two non-cscan shapes are still above the ~3 % bar.** These are the
  recursion specimen and a recursive-parens matcher, at +3.6-4.0 % on both
  entries. HEAD had the same cost under `_in`, so the fixes did not add it. It
  is Frank's call (see "Question for Frank" below).
- **F4: no.** The fix keeps every checkpoint, so it does not drop checkpoints on
  loops that can never compact. Filed as [TRAIL-CKPT-PRUNE].
- **F2:** the specimen's `4n + 17` is unchanged and still monotone.
  - I tried a re-arming stop rule once (`max(floor, w + cap/4)`). It still left
    holes and moved the specimen boundary (n = 200 needed 803), so the latch
    stays.
  - Doc: limits.md §4¶3. Mechanism: [TRAIL-REARM].
  - The commit message of f18317611 says "re-arming trigger". That attempt was
    reverted before fcd0c4925.
- **Checks:**
  - run_trail_compact.sh: 38 checks, 0 failed locally.
  - S1790-S1799: all ten detected when planted by hand.
  - The full runs are queued and OWED (see the last section).

## Disposition table

| id | ruling | done | where |
|---|---|---|---|
| F1 | FIX-NOW | bounded walk (top `cap` frames); bound corrected to 12 visits/write + map bytes | emit_vm.c vm_emit_trail_compact; D183; limits §4¶3; witness `frames-bound`, `partial-walk`; S1797, S1799 |
| F2 | doc + PLAN | doc sentence (non-monotone below the plain high-water; `4n + 17` measured monotone n = 7..1,200); one re-arm tried and reverted | limits §4¶3; [TRAIL-REARM] |
| F3 | re-measure, to Frank if > 3 % | both entries, table below; spec and parens are above 3 % | this report; D183 "Cost"; K134 |
| F4 | say, else PLAN | not dropped | [TRAIL-CKPT-PRUNE] |
| F5 | FIX-NOW | fast tier never compacts (run-state floor, set to never on each fast-tier entry) | emit_comb.c fwd_own; emit_iter.c; S1798; every witness must escalate exactly once |
| F6 | FIX-NOW | FILEPIN `fcd0c4925` (self-pin; the manager re-pins to the merge) | tests/codegen/run_recursion_identity.sh; run OWED in job 690 |
| F7 | FIX-NOW | the corpus checkpoint check runs by default in test-vm (`TRAIL_CORPUS=0` skips it; about 10 s) | tests/vm/run_trail_compact.sh |
| F8 | FIX-NOW | verdict (2) reworded as the `nset == _SET(` count control | tests/vm/trail_checkpoints.py |
| F9 | FIX-NOW | one writer `vm_trail_check_text` (both spellings), and a `vm_ev` note: `--emit-ir` now lists `note trail checkpoint: ...` | emit_vm.c; S1796 re-anchored |
| F10 | FIX-NOW | the rung ladder always ends at the high-water; answered >= 1 per witness | trail_compact_driver.c next_rung; run_trail_compact.sh |
| F11 | FIX-NOW | each rung mallocs exactly `nt` entries | trail_compact_driver.c run_exact |
| F12 | PLAN | not built | [TRAIL-GC-COUNT] |
| F13 | PLAN | three rows added (S1797-S1799); the rest is filed | [TRAIL-MECH-COVER] |
| F14 | NOTED + PLAN | filed | [TRAIL-BOUND-SCALE] |
| F15 | FIX-NOW | both annotations now say 763/764, `4n + 17`, 1,528 B | docs/pcre2_compliance.md |
| F16 | FIX-NOW | the nset comment names `margin` in `<prefix>_trail_gc_floor` | emit_vm.c Vm |
| F17 | FIX-NOW | cap/2 is DERIVED (it pays for the first compaction's `cap` frame visits); the quarter is a CHOICE; noinline on `_trail_gc_start` is MEASURED; `cold` is ARGUED; D183 has ranked goals and the rule restated | emit_vm.c; attr_text.c; D183 |
| F18 | DOC | abi changelog clause: text, frames, run-state member (see below) | docs/dev/history/abi_changelog.md |
| F19 | NOTED (manager) | nothing to do here | — |
| LATCH HOOK | NOTED | filed | [LATCH-HOOK] |
| SAFEPOINT | BOONIES row | filed with four unlocks and their triggers | [VM-SAFEPOINT] |
| process | guide rule | "A VM capacity change is measured through both entries" | docs/dev/guide/architecture.md |

## F1 bounded compaction

- **Premise reproduced.** Witness `(?:a|ab)*(?:(\w+)=(\d+);)*+end` on 'a'×100k +
  'k=1;'×100k + 'end', `_in`, 1M frames, trail 64:
  - HEAD 801ad1214: 2.37 s. Doubled input: 9.29 s, so quadratic.
  - BASE b05ccfc0b: FRAMES at once.
  - Fixed: 0.00 s and 0.01 s, the same answer as the 4M-trail run.
- **Fix.** The walk starts at frame `max(0, top - cap)`. The read and write
  cursors start at that frame's predecessor's mark. Frames below it, and their
  entries, are untouched.
- **Why answers are kept:**
  - TRAIL-SEG only ever drops an entry whose slot already has an older entry in
    the same segment.
  - Narrowing the window leaves some dups in the trail. It never drops an entry
    it should keep.
  - CUT-INV and the K36 call snapshot read only the marks the walk rewrites
    consistently.
  - The `partial-walk` witness checks the case where frames exceed `cap`
    (`^(a)(?:a|ab)*(?:(c)(d)?)*+a{60}(?:cd)+$` on 'a'×501 + 'cd'×300).
    Planting S1799 (reading from 0) gives 98 capture mismatches there.
- **Bound:**
  - A compaction reads at most `cap` entries, clears its byte map through at
    most `cap` kept ones, and moves at most `cap` marks.
  - The first compaction of an attempt follows more than `cap/2` writes. Each
    later one follows more than `cap/4` writes, because of the quarter rule.
  - So for `cap >= 4` it is at most 12 visits per write, plus a map of NSLOTS
    bytes per compaction.
- **Coverage kept.** The specimen boundary stays `4n + 17` (n = 7 → 45,
  200 → 817, 763 → 3,069, 764 → 3,073, 1,000 → 4,017). All cscan witnesses
  answer.
- **Register allocation.** Starting the matcher's trigger from a plain load of
  the run-state floor cost cscan seg5 `_in` +4.1 %. The noinline accessor
  `<prefix>_trail_gc_start` gets +0.93 %, the same as HEAD. noipa and by-value
  variants were no better.

## F5 tiered entry

- Each fast-tier entry (`fwd_own`, own forwards and the iterator's) writes
  `run.trail_gc_floor = (size_t)-1;` after its bind. Its FRAMES give-up then
  reaches the deep tier unchanged, and the deep tier compacts.
- run_trail_compact.sh section 3 requires every witness to escalate exactly
  once (12 witnesses). S1798 (fast-tier compaction left on) makes 3 witnesses
  escalate 0 times.

DEFAULT tiered entry (`rx_search`/`_next`, mode 1), gcc 15 -O2, `instructions:u`,
min of 3. BASE = b05ccfc0b, HEAD = 801ad1214, NEW = this lane:

| shape | HEAD | NEW |
|---|---|---|
| cscan 19-byte segments (seg5) | +15.10 % | +0.84 % |
| cscan seg20 | +4.56 % | +0.75 % |
| `^(a(?1)?b)$` n = 100 | +19.51 % | +3.66 % |
| poss500 `(?:(a)(b)?)*+x` (the fast tier compacted instead of escalating) | +23.67 % | +3.18 % (escalates) |

## F3 re-measure

| shape | tiered default (mode 1) | `_in`, big buffers (mode 0) | HEAD tiered / `_in` |
|---|---|---|---|
| cscan seg5 (19 B) | +0.84 % | +0.93 % | +15.10 / +0.93 |
| cscan seg20 | +0.75 % | +0.76 % | +4.56 / +0.87 |
| cscan seg80 | not comparable (BASE gives up; NEW answers) | +0.70 % | — / +0.83 |
| `^(a(?1)?b)$` n = 100 | **+3.66 %** | **+3.77 %** | +19.51 / +3.70 |
| `(\((?:[^()]++\|(?1))*\))` find-all | **+3.56 %** | **+4.01 %** | +3.80 / +3.82 |
| `(\w+)(?:,(\w+))*;` find-all | +1.55 % | +1.71 % | +0.84 / +0.84 |

- At -O3 (f3_O3.txt):
  - cscan: +0.7-0.9 %.
  - spec: +3.7 / +3.8 %.
  - parens: +3.4 / +3.9 %.
  - csv: **+4.2 / +4.3 %** (HEAD +3.5 / +3.5 %).
- The csv shape is +0.7-0.9 points above HEAD on both builds. That is the price
  of reading the floor from the run state, needed by F5. One bounded effort
  went to it (noinline accessor, noipa, by-value), so I accept it.
- Mechanism (review EMIT-1): the cold call's rejoin at a short loop's latch
  evicts the trail depth from its register.

**Question for Frank:**

- **The question.** Two non-cscan shapes cost about 3.6-4.0 % more
  instructions when the trail never fills, a little over your ~3 % bar:
  - the recursion specimen;
  - a recursive balanced-parentheses matcher.

  The short comma-capture loop is 1.6-1.7 % at -O2 but 4.2-4.3 % at -O3. The
  scanner shapes K134 was filed for are under 1 %.
- **The forces:**
  - The fix itself changes no answer.
  - It is what makes the cscan subjects answer at all.
  - The cost sits on short loops whose checkpoint can almost never fire.
- **My leaning:**
  - Land it as is.
  - Treat the 0.6-1.0 point overshoot as accepted for now.
  - Start [TRAIL-CKPT-PRUNE] when a bench cell or user pattern shows the cost.
    That row removes the checkpoint from loops that push their own resume
    frame every turn, which is where this cost lives.
- **The alternative.** Hold the landing until that row is built. It needs its
  own proof and a checker change, about one lane.

## Checks and pins

- tests/vm/run_trail_compact.sh: 13 witnesses (9 compacting, 2 boundary probes,
  1 bounded-work run, 12 escalating exactly once) plus the corpus checkpoint
  sweep. Locally: 38 checks, 0 failed.
- Sabotage rows. Each was planted by hand and then removed; the log is
  trailgc3/plants.log:

  | row | what it plants | detected by |
  |---|---|---|
  | S1790 | — | 9 failed |
  | S1791 | — | 4 failed |
  | S1792 | — | 3 failed |
  | S1793 | quarter stop off; re-anchored | 1 failed (the specimen's 816 probe) |
  | S1794 | — | 21 failed |
  | S1795 | — | 4 failed |
  | S1796 | checkpoint not written; re-anchored | 2 failed (cycle check) |
  | S1797 | NEW: walk from frame 0 | `frames-bound` timeout |
  | S1798 | NEW: fast tier compacts | 4 failed |
  | S1799 | NEW: read cursor from 0 | `partial-walk` 98 mismatches |

  Field validation passes for all 11 rows (with S693).
- Identity gate (B): FILEPIN `fcd0c4925`, the lane's last src commit. The
  manager re-pins it to the merge commit. The run is OWED in job 690.
- Stack frames, by `gcc -fstack-usage` and test-stackdepth (5/5 locally):
  - The run-state member `trail_gc_floor` moves the specimen's numbers by
    16-32 B:
    - entry frame: 3,184 → 3,200 B;
    - deep: 131,216 → 131,232 B;
    - deep path: 134,400 → 134,432 B;
    - a 128 KB thread is short by 3,328 → 3,360 B.
  - `_in` stays 144 B.
  - Re-pinned in limits.md §5¶2-¶4, match_api.md §5.3¶7 and §10.9¶10,
    lib/pcrec.h and the run_stackdepth_tests.sh comment.
  - The review's F18 note said these were unchanged. That was before F5 added
    the member.
- Mover census: docs/dev/lanes/trailgc3/movers.py, trailgc2's census with the
  new admitted lines (the run-state member, its bind and fast-tier lines, the
  start accessor). It classifies a base vs new artifact as `checkpoints`. The
  corpus run is OWED in job 690.

## Docs

- D183 rewritten in place (amendment noted in its title):
  - ranked goals;
  - the decision rule restated;
  - the F1 walk limit and the F5 fast tier;
  - the measured cost on both entries;
  - the work bound with both arrays, and the old "four visits" named and
    corrected;
  - labelled constants;
  - consequences (the run-state member, the frame moves, non-monotone reach);
  - one new revisit trigger.
- docs/spec/limits.md:
  - §4¶3: the work bound in plain words, the fast tier never compacts, and the
    non-monotone sentence.
  - §5¶2-¶4: frame numbers.
- docs/spec/match_api.md §5.3¶7 and §10.9¶10: frame numbers.
- lib/pcrec.h: the frame sentence.
- docs/pcre2_compliance.md (F15): both hand annotations.
- docs/dev/history/abi_changelog.md (F18): the added functions and member, plus
  size and stack.
- docs/dev/known_issues.md K134: the fixed text, the bound, the cost on both
  entries, S1790-S1799.
- docs/dev/plan.md, Backlog:
  - [TRAIL-CKPT-PRUNE]
  - [TRAIL-REARM]
  - [TRAIL-GC-COUNT]
  - [TRAIL-MECH-COVER]
  - [TRAIL-BOUND-SCALE]
  - [LATCH-HOOK]
- docs/dev/plan.md, Boonies: [VM-SAFEPOINT]. plan_lint: 0 violations.
- docs/dev/guide/architecture.md: the both-entries measurement rule.
- tests/vm/CLAUDE.md and the mech matrix's trailcompact vocabulary.

## Validation

- Locally:
  - run_trail_compact.sh 38/0.
  - test-stackdepth 5/5.
  - plan_lint 0.
  - the pre-commit staged checks green.
  - the ten sabotage plants as above.
  - the mover classifier checked on a base vs new artifact (`checkpoints`).
  - F3 at -O2 and -O3.
- Not run here (the box was held by queue job 680; heavy runs go through the
  queue):
  - make strict;
  - make test;
  - the corpus mover census;
  - the identity gate;
  - the mech matrix.

## STATE AT HANDOFF

- Branch lane/trailgc, clean apart from the manager's untracked
  trailgc3_deliver.txt. The last src commit is fcd0c4925.
- OWED, queued 2026-10-29 ~12:35 (owner trailgc):
  - **690-trailgc-test** (key trailgc-test): build, make strict, mover census
    (unexpected = 0), run_trail_compact.sh with the corpus sweep, the identity
    gate (B) at fcd0c4925, then make test through perfrun. Cap 3 h.
  - **691-trailgc-mech** (key trailgc-mech): mech S1790-S1799 + S693, 11 rows.
    Cap 4 h.
- Both jobs' `--ready` answers ready only before 17:30 (test) or 17:00 (mech)
  today, else from 2026-10-30T13:30, so neither starts in the 19:00-00:00
  bench window. The cancelled pre-review 690/691-trailgc jobs are already in
  done/ as cancelled. Ahead of them are 680-ic3-test (running), 681-ic3-mech
  and 690-p910-census.
- For the manager:
  - F3's question for Frank (above).
  - Re-pin FILEPIN to the merge commit at landing.
  - abi 93 stays provisional in landing order (F19).

## Triage 2026-10-29 (tgctri)

Job 690-trailgc-test ended RED (rc=1, wall 3153 s). Verdict read from make's
`*** [Makefile:N: test-X] Error` lines: ten sections red (registry,
prefilter, vm, codegen, cpset-structure, rxtsource, memfn-arch,
fallback-table, startset, partlayout) plus the identity gate `ident`.
strict, the mover census (unexpected 0) and the trail compaction check with
the corpus sweep (39 checks) were GREEN. The job's `ident ran=2 declared=0
OVER` was not a declaration bug: the captured number is the gate's own exit
status (`ident: DONE rc=2`), so the OVER was the failure itself.

No failure moved an ANSWER. Every one is a stale pin, a stale hand-written
reader or a missing manifest row for the new emitted text; the lane's own
mover census already classed every moved cell as `checkpoints`.

| failure | cause | fix |
|---|---|---|
| registry: compliance annotation drift | commit e730f4f88 edited the F15 prose in `docs/pcre2_compliance.md` but not its store | same text in `docs/pcre2_compliance_annotations.txt` |
| prefilter T2 SIZECAP, fallback-table seq-pfclow/pfcbcat/pfcd2/att-scpfc | the checkpoint adds a FIXED 1,815 B of code to every artifact carrying one (same +1,815 on three unrelated lowsize witnesses, e.g. sc 31293 -> 33108 on `(?:a\K){2,}b`), pushing the 30,000 B lowsize witnesses over the cap | lowsize/trlowsize/trlowboth cap 30,000 -> 31,815 in both scripts (restores each witness's margin exactly); expected rows unchanged |
| codegen run_size_term: rescue took K=2 | same +1,815 on every rung (K=4 32,801 -> 34,616) against the 33,200 cap | cap 33,200 -> 35,015 (K=6 ~39,697 and K=3 ~35,501 still do not fit, K=4 fits with ~400 B headroom) |
| vm ir-listing BYTE-NEUTRALITY (5 baselines) | each listing gains the `trail checkpoint` note row(s) and the events count | re-captured (CAPTURE_IR_BASELINE=1); diff is only `events` and the note rows |
| codegen facts-decisions | `RX_TRAIL_CHECK` is a caller macro, not a decision stamp | added to the MACHINERY list |
| codegen K37 / TT-9 | `tests/vm/run_trail_compact.sh` ran the compiler and the checker unbounded and was in neither sanitizer list | `$TIMEOUT_BIN` on both calls; added to `tests/lib/san_scripts.txt` (it takes GENCFLAGS) |
| codegen SABANCHOR | S38's anchor `gslot, v->p, top);` became `gslot, vm_jump(v, top));` | S38 BEFORE/AFTER re-derived from the live source |
| cpset-structure manifest | `(a(?1)?b)` EMITTED_BYTES 41,450 -> 43,357 (only sample artifact with a checkpoint) | re-recorded after reading the diff (one row) |
| rxtsource census (+10 lines) and memfn-arch | the K134 long-flat cscan cell for 350 identifiers spelled `x86_...`, an arch noun (C4 class 6); census moved by cscan's 5 new cells x 2 lines | generator identifiers `x%d_%d` -> `v%d_%d` (same length, regenerated, libpcre2-verified, only that line differs); C3/CENSUS/RUNSH pins +10 |
| startset vm-movers | framebuffer.rxt grew 8 lines: the `(a\|aa)+b` block moved 94 -> 102 | both manifests re-keyed |
| partlayout attribute census | `P_trail_compact` (cold, noinline) and `P_trail_gc_start` (noinline) unlisted | two K134 rows in `tests/partlayout/writers.tsv` |
| ident (A) 496 + 312 unrecorded region differences, bref-rename census 248 vs 413 | program regions now contain `RX_TRAIL_CHECK();` statements and `{ RX_TRAIL_CHECK(); goto rx_LN; }` blocks, which no deny axis removes, so every deny-restores excuse and the rename bucket missed | `trail_check_canon` in `prog_region()` (the seventh exception's two-sided shape): strips exactly those two spellings from every extracted region; other spellings still land in rdiff; non-vacuity floor TRAILCHK_TOTAL >= 1; comparison (B) still pins the whole file at FILEPIN |

Local re-validation (the box was held by queue jobs, so the heavy scripts were
NOT run by this triage; the re-queued job is their validation): rerun and
GREEN here: registry, cpset-structure, rxtsource, memfn-arch, facts-checks,
partlayout, ir-listing (164 checks), the S38 anchor check (1076 sabotages, all
resolve). By direct compile: the three lowsize sequences now read
`prefilter-collapse@size`, `drop-prefilter@size` and `prefilter-collapse@size >
drop-prefilter@size > drop-handoff@size`; the SIZECAP prefilter reads
`yes-collapsed`; the rescue takes K=4 (`cap-rescue`) at cap 35,015; the ident
canonicalizer, applied to the 18 listed REGION DIFFERS patterns and 300 bench
patterns on `--engine=vm`, reproduces the base (b05ccfc0b) region exactly with
no `RX_TRAIL_CHECK` left. OWED to the re-queued 690-trailgc-test: fallback-table,
prefilter, codegen (K37/TT-9/size_term), startset, vm and the identity gate as
whole scripts. Not touched, to flag: `scripts/emit_sweep.py`'s `lowsize`/`lowboth`
variants and `run_size_term.sh`'s K100 cell still use the 30,000 B cap (not part
of the failing set; re-measure if the sweep or that cell reads red).

## Landing 2026-10-29 (landtgc)

- Merge `ebcc10aa1` (lane/trailgc ffd1f578e into main at abi 92), landed as abi 93. Conflicts: abi_changelog (both entries kept, 93 current, S3's 92 now "was"), plan.md and the lanes history index (both sides kept), emit_dfa.c, match_api.md (3 spots), run_codegen_tests.sh (ABI_EXPECT=93, both history clauses), S693 (93), cpset_structure comments, recursion_identity (comments), rxtsource census pins (summed: LINES/RUNSH_LINES 75523, C3_SKIP 52780, C3_VERIFIABLE 25046; FILES/BLOCKS = main's ic3 values).
- Re-pin: `86356a960` moves the (B) FILEPIN to `ebcc10aa1`; (A) untouched ([RECID-A] stays red until lane/recida lands).
- `make` and `make strict`: clean.
- Ledger: major line added (counter 31).
- Not moved, noted: `scripts/emit_sweep.py` lowsize/lowboth and `run_size_term.sh` K100 cell use a deliberately lowered `PCREC_MAX_VM_EMIT_CODE_BYTES=30000` (a test knob, not the trail cap); re-measure only if they read red.
- plan.md: no trail row existed to change; the lane's seven rows merged as not-started.
- OWED (not pushed): detached chain `/var/tmp/pcrec-pcrec/scratch/landtgc/chain.log` runs test-codegen, test-registry, test-rxtsource, test-recursion-identity (logs beside it, `<suite>.log`), waiting on the box queue. Expected: chain ends `== ALL DONE`, each `rc=0` except test-recursion-identity, whose only red is identity (A) with the [RECID-A] counts 167/382/167/111 (bucket ~330) and (B) zero-diff. STOP RULE: any answer difference, a (B) diff, or another red means do not push.
