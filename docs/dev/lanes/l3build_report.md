# Lane l3build: span_arms L3's five remodel commits

Lane l3build (opus), 2026-11-20. Branch `lane/l3build`, cut from main `cfa0c2b1a` (L1 landed, the L3
census merged). Design of record: `docs/design/span_arms.md` rev 3.3, §14.4 "L3 — BACK", "Remodel
commits, in order", with §14.3 D-4, D-6, D-7, D-8. The FEATURE is not built here.

## Summary

- **The five remodel commits are on the branch**, in the design's order, each its own commit:
  - RM-2 `f52b6d6aa`;
  - RM-3 `c921cf980`;
  - RM-5 `9bd570b16`;
  - RM-4 `f9c3c88b0`;
  - remodel 5 (`rn_cmp`) `f15dc9876`.
- **Each is byte-identical by construction**, and a light smoke shows it. 61 handoff and lookbehind
  patterns were compiled per commit against the base binary: 366 comparisons each (the .c under byte and
  utf8 on both engines, plus `--emit-facts`), and 0 differ. RM-5 adds 7 lookbehind patterns (42 more
  comparisons), also 0 differ.
- **`make strict` is clean** at every commit.
- **Ten sabotage rows were re-anchored or re-aimed.** Each row's plant was applied to the tip in a
  scratch tree, the tree rebuilt, and the row's witness pattern recompiled. Every plant compiles, and
  the output moves on its witness, except S901, which is UNREACHED as declared. The rows are S463, S467,
  S1957, S3075, S470, S809, S901, S453 and S474.
- **The gate verdicts are OWED as box-queue jobs** (Validation queued): five identity sweeps, the
  trace build, two mech jobs and `make test`.
- **No stop.** At this base the design's text held for every commit.
- **`src/gen/emit_vm.c` is not touched.**

## Remodel commits

1. **RM-2, `f52b6d6aa` (D-7): K's three states.**
   - **The type.** `src/facts/facts.h` gains `PfBound`: the states `PF_OFF_NONE`, `PF_OFF_BOUNDED` and
     `PF_OFF_UNBOUNDED`, plus a signed `long long v`. In the unbounded state `v` keeps the saturated
     number, so every printed byte is today's.
   - **The helpers.** `pcrec_bound_none()` and `pcrec_bound_of(off)` (facts.c: unbounded at or above
     `PCREC_W_UNBOUNDED`, value kept). The two predicates are `pcrec_bound_stated` ("is K stated") and
     `pcrec_bound_bounded` ("is K stated and bounded").
   - **The fact.** `req_landmark_maxoff` and `pcrec_fact_req_landmark_maxoff` are `PfBound`. The −1
     sentinel is retired at the reset, the derivation, `req_landmark_k` (`head < 0`) and the printer.
     The derivation's "why unbounded" test is `stated && !bounded`.
   - **The emitters.** `req_handoff_k` and `req_landmark_k` return `PfBound`. The whole-run branch is
     `pcrec_bound_of(whole_maxoff)`. The hand tests now ask `pcrec_bound_bounded`:
     - `req_handoff_applies`;
     - the stamp;
     - the entry's unbounded branch;
     - `emit_req_landmark_move`'s early return;
     - `pcrec_emit_req_attempt_reentry`'s comment choice.
   - **`head_max`.** `req_site_define` maps the unbounded state onto `MF_HEAD_MAX_UNBOUNDED` at its one
     writer.
   - **The admission.** `req_landmark_admits` still takes K's value (`.v`). Its two callers reach it only
     where K is stated, and a NONE value of 0 prices the same as −1 did (`max(K, 0)`).
   - **Not touched** (the note's "NOT in RM-2"):
     - `req_handoff_entry_applies`'s `k >= 0 && k < PCREC_W_UNBOUNDED` on the whole-run K, whose `k >= 0`
       conjunct L3's feature deletes;
     - `req_handoff_unbounded_applies`.
   - **Re-anchored:**
     - S463: the entry's value line `long long k = kb.v;` plus the next comment.
     - S467: `if (!pcrec_bound_bounded(k)) return false;`. The plant keeps only `stated`.
     - S1957: the stamp's bounded test.
     - S3075: the re-entry's value line plus the re-ask printf, its two-line site.
2. **RM-3, `c921cf980` (D-8): one emitter of the move arithmetic.**
   - **The emitter.** `emit_req_move_open(c, ind, hit, pos, target, K)` prints
     `if (hit - pos > K) {` and its assignment one level in. Where `target` IS `hit`, the entry's case, it
     prints `target -= K` (nothing at K = 0). Otherwise, the re-entry's case, it prints `target = hit - K`
     (`target = hit` at K = 0).
   - **Stays in the callers:** the entry's `k > 0 || round.len > 0` guard and its `else`, the re-entry's
     reseed splice, both unbounded branches, the re-ask block, both `ROUNDUP` calls and the
     `req_handoff_vm` write (S1711).
   - **The premise.** "Cannot underflow" moved from `emit_req_handoff_rest`'s header into the one
     emitter's.
   - **Re-aimed:**
     - S470 keys on the emitter's in-place branch (`in_place ? "...1 || ..." : ...`), so it fires at the
       entry only.
     - S809 keys on the assign branch (`0LL`), so it fires at the re-entry only.
     - Per-caller detection survives, as D-8 states.
3. **RM-5, `9bd570b16`: `lb_max`'s read accessor.** `pcrec_lb_max(const Ctx *)` sits in
   `src/core/internal.h` beside `pcrec_lb_raise`. The `_VALID_LB` stamp reads it. Re-anchored: S901 (its
   plant and its UNREACHED declaration unchanged). `run_assertions_tests.sh`'s `VALID_LB` reads the
   emitted stamp, which is unchanged.
4. **RM-4, `f9c3c88b0` (D-6): `pcrec_run_scan_index(rate, run, lo, hi)`.**
   - **Where.** Defined in `src/facts/req.c` beside `pcrec_req_pick` and declared in `facts.h`.
   - **What.** It is pcrec's own pick over `run->pos[lo..hi)`, returned as a run index.
   - **The callers.** `pcrec_req_pick` and the trace shadow `req_set_leads_own` (emit_dfa.c) both call it
     over `[0, whole_len)`.
   - **An empty stretch** (`lo >= hi`) answers −1 and never asks the primitive over zero positions. This
     is D-6's empty-extent refusal. No caller reaches it today: both guard `whole_len >= 2`. It is now the
     site of the W-L17..19 plant the feature names.
   - **Untouched.** `rn_scan_mass`'s whole-`RbRun` call is not one of D-6's two callers, so it was left
     alone.
   - **Re-anchored:** S453.
   - **Checks.** `tests/findings/structural_check.py` passes S1-S4 at the commit, run by hand. Its S1
     still reaches `pcrec_req_pick`.
5. **Remodel 5, `f15dc9876` (D-4): the comparator `rn_cmp`.**
   - **The split.** `rn_better`'s `RB_ROW_SCAN` moved into `rn_cmp(w, const RbRun *a, const RbRun *b)`,
     which returns the sign. `rn_better` is `rn_cmp(...) >= 0 ? a : b`.
   - **Not yet a caller.** TOP still calls `rn_better`. Calling `rn_cmp` is the feature's.
   - **Re-aimed:** S474. Its anchor line `    RB_ROW_SCAN(i, w, rn_choice_rows,` is unchanged and
     unique, but the plant now answers a sign over pointers
     (`return a->off < PCREC_W_UNBOUNDED ? 1 : -1;`).
   - **Checked:** S1930's row line is unmoved.

## Identity per commit

**The light smoke,** done by hand. It used `l3build_evidence/cmp.sh`, `pats.txt` (61 patterns: the
handoff.rxt and handoff_vm.rxt patterns and the binding rows' witnesses) and `lb.txt` (7 lookbehind
patterns). The reference is the base `cfa0c2b1a` build in `$PCREC_TMPDIR/scratch/l3build/trees/base`.

| commit | comparisons | differ |
|---|---|---|
| RM-2 | 366 | 0 |
| RM-3 | 366 | 0 |
| RM-5 | 42 (lb.txt) | 0 |
| RM-4 | 366 | 0 |
| remodel 5 | 366 | 0 |

**The gate itself is OWED, one box-queue job per commit.** Each job:
- builds the commit's tree from `git archive` into `$PCREC_TMPDIR/scratch/l3build/trees/<tag>`;
- runs `scripts/emit_sweep.py` from that SUBJECT tree (its population), with `--ref-bin` the base
  binary, over every stream (.c, emit-ir, composition, dumps, facts) plus
  `sae1_evidence/bench_patterns.txt`;
- takes its verdict from `sae1_evidence/ident_check.py` against an EMPTY census, never from
  emit_sweep's rc.

The pass line is `== ident_check COMPLETE: 0 unexplained`. RM-4's third gate, the trace build, is its
own job (`tests/memfn/run_pres_picks.sh` over the RM-4 tree).

## Binding checks

**The anchor map.** `l3build_evidence/anchors.py` counts every sabotage row's `SAB_BEFORE`, as a
whole-file substring (`replace.py`'s own rule), in every file the commits touch:
- `src/gen/emit_dfa.c`, `src/facts/facts.c`, `facts.h`, `req.c`, `kset.c`;
- `src/core/internal.h` and `findings.c`.

It counts at the base and after each commit, 264 rows. It reads every row in those files, not only the
listed ranges, so it has no first-line limit.

**Rows whose count moved,** each re-aimed in its own commit:

| commit | rows |
|---|---|
| RM-2 | S463, S467, S1957, S3075 |
| RM-3 | S470, S809 |
| RM-5 | S901 |
| RM-4 | S453 |
| remodel 5 | S474 (its plant no longer compiled in `rn_cmp`) |

After the re-aims, every row in those files matches once. The exceptions are S283 and S284, which match
twice both at the base and at the tip (pre-existing, unrelated).

**Plant probes** (`l3build_evidence/plantprobe.sh`, on a scratch export of the tip). Each re-aimed
plant was applied through `tests/mech/lib/replace.py`, the tree rebuilt, and the row's witness compiled
clean and planted:

| row | witness | result |
|---|---|---|
| S463 | `(?m)^x{2,5}(?i:cat)` | output moves |
| S467 | `a.*?(?i:select)` | output moves |
| S1957 | `a+xyz` on the VM | output moves |
| S3075 | `a+xyz` on the VM | output moves |
| S470 | `(?m)^x{2,5}(?i:cat)` | output moves |
| S809 | the ipv4 byte-landmark pattern | output moves |
| S453 | `(?i:select)\d+x` | output moves |
| S474 | `ab.*xyzw`, facts | output moves |
| S901 | `^(?<=xy)a\|b$` | unchanged, UNREACHED as declared |

Every plant compiled. The DETECTED verdicts are the mech jobs' (OWED).

**S467's plant changes shape.** It used to hand off at K = 2^40, so the subtraction never fired. Now
the unbounded state takes the entry's no-move branch, and the DFA route stamps `REQ_HANDOFF
"unbounded"`. run_prechecks [5.12c] reads exactly that (only the VM attempt loop may stamp unbounded),
so the row should still read DETECTED. The mech job confirms it.

**The rest of the binding list** is unmoved: S476, S529, S811, S1707, S1712, S1711, S1955, S471, S813,
S814, S1701, S280, S461 and S1930. It is queued as its own mech job.

**Other checks:**
- `tests/codegen/run_prechecks.sh` and `tests/findings/e1_object_check.py` run inside `make test`.
- `structural_check.py` was also run by hand at RM-4 and passed.

## Validation queued

All nine jobs have owner `l3build` and prio 200. The scripts are in
`$PCREC_TMPDIR/scratch/l3build/jobs/`, generated by `l3build_evidence/mkjobs.py`. The outputs are under
`$PCREC_TMPDIR/scratch/l3build/`.

| key | what | pass line or verdict |
|---|---|---|
| `l3build-trace-rm4` | RM-4's trace build, run_pres_picks.sh over the RM-4 tree | the check's rc (`checks failed: 0`) |
| `l3build-ident-rm2` | RM-2's identity gate (`ident-rm2/`) | `== ident_check COMPLETE: 0 unexplained` |
| `l3build-ident-rm3` | RM-3's identity gate | the same |
| `l3build-ident-rm5` | RM-5's identity gate | the same |
| `l3build-ident-rm4` | RM-4's identity gate | the same |
| `l3build-ident-cmp` | remodel 5's identity gate | the same |
| `l3build-mech-reaimed` | S463 S467 S1957 S3075 S470 S809 S453 S474 S901 | each DETECTED (S901 UNREACHED as declared) |
| `l3build-mech-bound` | S476 S529 S811 S1707 S1712 S1711 S1955 S471 S813 S814 S1701 S280 S461 S1930 | each at its declared expectation |
| `l3build-test` | full `make test` via perfrun on the worktree | no `*** [... test-X] Error` line |

The mech jobs and `make test` run IN the worktree, so nothing may be edited there while they run.

## Findings and notes for the feature lane

1. **The whole-run branch of `req_handoff_k`** states `pcrec_bound_of(whole_maxoff)` whatever
   `whole_len` is. That keeps today's value: a `whole_len < 2` run reads as bounded 0, not none. Whether
   `req_use_whole` can hold with no stated run was not measured. The feature's deletion of the `k >= 0`
   conjunct in `req_handoff_entry_applies` (§5.4 A8) is the place to state that run's none.
2. **`PfBound`'s NONE value is 0** and means nothing. `req_landmark_admits` reads `.v` from callers that
   reach it only with K stated. The feature's signed K reaches the same reader. Its `max(K, 0)` is
   already the design's "a landmark at or before the attempt start costs no step back".
3. **`emit_req_move_open` takes K as a bounded value of either sign,** but today's text assumes
   `K >= 0`. Its header says so ("K is bounded and >= 0"). The D-8 K < 0 row (`hit += B`, the clamp, the
   per-row guard `k != 0 || round.len > 0`) is the feature's edit there and in the two callers.
4. **The register** (`docs/dev/guide/architecture.md`) is not edited. The rows that ride with these
   commits are left for the manager at landing:
   - P2 (RM-2 for K);
   - P3 (RM-3);
   - P4 (RM-4);
   - 6a (`lb_max` only, RM-5).
5. **No new stack frame of size;** the stackdepth check is in `make test`.

## STATE AT HANDOFF

- **Commits on `lane/l3build`** (base `cfa0c2b1a`):
  - `f52b6d6aa` RM-2;
  - `c921cf980` RM-3;
  - `9bd570b16` RM-5;
  - `f9c3c88b0` RM-4;
  - `f15dc9876` remodel 5;
  - this report's commit, with `l3build_evidence/` (anchors.py, mkjobs.py, cmp.sh, plantprobe.sh,
    pats.txt, lb.txt).
- **Rulings file:** `l3build_rulings.md` is empty, so no ruling was applied. Last entry applied: none.
- **Stopped at:** nothing. All five commits are built.
- **Owed:** none (as the deliver file declares). The nine box-queue jobs under Validation queued are this
  lane's gate runs, listed for the manager to read.
- **Not run by this lane:** `make test-axes` and the D27 and witness work, which belong to the feature.
