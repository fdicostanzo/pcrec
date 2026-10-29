# crit-trailgc lens SLOT: slot-tracing + ruling check

Subject 801ad1214, BASE b05ccfc0b. Scratch scripts: slots/backscan.py (text-order back-jump scanner, independent of the branch checker), slots/sweep.py, slots/gen.py.

Verdict: (a), (b), (c) HOLD on everything the emitter produces today (no counterexample in ~47.7k artifacts). They hold by convention plus a check that sees 11 artifacts, not by construction: the rule is applied to 2 jump primitives; ~29 raw `goto <p>_L<n>` printf sites and the resume (push) edge are outside it. No answer- or reach-level counterexample found.

## Findings

### SLOT-1: the cycle rule is enforced on 2 of ~31 jump-writing sites; the rest rely on a check that sees 11 artifacts
- status: CONFIRMED (structural; no live counterexample)
- severity: design (latent reach; no answer risk, since compaction never raises depth)
- effort: small; blast radius: none in emitted bytes for the structural fix (no site triggers today)
- location: src/gen/emit_vm.c `vm_jump_closes_trail_cycle`/`vm_goto`/`vm_jump` (3484-3522); raw `goto %s_L%d` printf sites at 3880, 4649, 4658, 4666, 5522, 5603, 5611, 5791, 5893, 5902, 6087, 6293, 6528, 7131, 8596, 8606, 8612, 8616, 8620, 8624, 8862, 8923, 8971, 9110/9111, 9158, 9176, 9190, 9224
- The `vm_emit_trail_compact` comment says the back edge crossing each write "carries a checkpoint". True only for `vm_goto`/`vm_jump`/region return. Two edge kinds can go back in the text without one: (i) any raw conditional goto above, should one ever target an already-written label (today all go forward; vm_star's guard was the one backward case and the branch converted it); (ii) a resume edge `<P>_PUSH(&&L)` with L written BEFORE the push and a `_SET` between: the cycle L -> SET -> PUSH -> fail -> resume L keeps the SET's entry below the mark every turn and passes no goto. Claim (c) ("a resume adds no growth of its own") is literally true but the cycle argument silently assumes no such push exists.
- The branch's tests/vm/trail_checkpoints.py models both kinds correctly, but make test runs it only on run_trail_compact.sh's 11 witnesses; its corpus mode (TRAIL_CORPUS=1) is wired into no make target, battery stage or mech arm (grep scripts/, Makefile, tests/). D183's "Revisit when" trigger therefore has no regular watcher.
- Probe: corpus x 9 flag sets + 4,000 random shapes x 3: 0 checker failures, 0 unguarded backward gotos spanning a `_SET(`, 0 back-resumes, 0 `_SET(` in C loops. A corpus sweep is ~17 s here (docstring says "minutes").
- fix: (1, general) route every label-jump text through `vm_jump`, and make `vm_push` refuse (internal error) a resume label already written with a SET since -- the proof then holds as written for every edge kind; (2, control) wire the corpus mode into make test-vm or the battery (~17 s).

### SLOT-2: abi 91 -> 93 without the identity gate's (B) re-pin (D76/D94 ritual incomplete)
- status: CONFIRMED by reading (gate not run, per the read-only brief)
- severity: maintenance (battery `recidentity` stage red by construction at SUBJECT)
- effort: one line + self-pin comment; blast radius: the battery's last stage
- location: tests/codegen/run_recursion_identity.sh:1285 `FILEPIN=...:-02229045e`; `git cat-file -p 02229045e:src/gen/emit_dfa.c` = `PCREC_ARTIFACT_ABI 91`, subject emits 93, so lines 1383-1393 fail "the emitted scaffolding changed: bump abi ... and re-pin comparison (B) ... in the same change (D76)". The branch does not touch the file; every prior lane self-pinned (comment block 1270-1284). Not in `make test` (D136), so a normal-tier run will not show it. If 93 is renumbered at landing, S693, codegen ABI_EXPECT and the changelog paragraph move again.

### SLOT-3: Vm slot table: `emitted_set` duplicates `nset > 0`; `ncheck` has two writers and the checkpoint text two spellers; `lbl_nset` re-derives the event log; checkpoints missing from --emit-ir
- status: CONFIRMED (reading + one run)
- severity: maintenance
- effort: small; blast radius: emit_vm.c only (listing op addition would touch ir_listing.md §3.4)
- location: emit_vm.c 532, 547-557, 3469-3478, 3488-3489, 3508-3510, 3578-3579

| slot | written by | read by | job(s) | duplicate of |
|---|---|---|---|---|
| `nset` | vm_set | vm_jump_closes_trail_cycle; vm_emit_trail_compact | TWO: program-order clock AND margin | `emitted_set` == `nset > 0` (set in the same lines 3578-3579); count of `VE_SET` events |
| `lbl_nset[]`/`lbl_cap` | vm_lbl | vm_jump_closes_trail_cycle | SETs written before each label | derivable from the always-on `ev` log (VE_LABEL, VE_SET); third arena grow-by-doubling array (ev, tabrd, lbl_nset) |
| `ncheck` | vm_trail_check AND vm_jump | vm_emit_trail_compact, prologue | only `!= 0` read | two incrementers; `%s_TRAIL_CHECK();` spelled at 3488 and 3510 -- breaks the file's "one primitive writes bytes and count in the same call" discipline (cf. vm_work_at) |

- `nset`'s two jobs coincide today; the cost is that limits.md §4's caller-observable `4n + 17` depends on the artifact-wide site count: any future SET site anywhere in the specimen's program moves the documented boundary.
- Family: third per-label record in emit_vm.c (`ev`, `rgn_lbl`/`rgn_exit`, `lbl_nset`).
- Checkpoints write no `vm_ev`, so `--emit-ir`'s `program` section (ir_listing.md §3.4, "the straight-line trace of what executes") omits them: `(a|aa)+b` has 1 `_TRAIL_CHECK();` in C, 0 in --emit-ir. vm_ev's header: "One call per emitted primitive writes both artifacts".
- fix: vm_jump calls a shared helper that writes text + count; derive/drop `emitted_set`; optionally a `checkpoint` op (vocabulary append-only, §3.4¶2).

### SLOT-4: margin is the whole site count, not the checkpoint-free path the checker already computes; check verdict (2) is tautological
- status: CONFIRMED
- severity: design (reach) / maintenance (check)
- effort: deferred (D77); blast radius: margin value in every checkpointed artifact (abi event)
- location: emit_vm.c vm_emit_trail_compact (`margin = v->nset`); trail_checkpoints.py verdict (2)
- cscan: margin 255 vs heaviest checkpoint-free path 61; specimen 15 vs 10. At default cap 3,072 cscan's floor is 2,817 where 3,011 is sound; the quarter rule stops ~194 kept entries sooner. No effect on the fast tier (both > cap/2).
- Verdict (2) "heaviest path <= margin" cannot fail while (1) passes: margin is the sum of all weights and an acyclic path visits each site once. It only controls nset == count of `_SET(` lines (learnings §3: shares a source with what it controls).
- Trigger to build: a pattern giving up on trail with spare frames where site count >> path bound; then compute the longest checkpoint-free SET path in the emitter (DAG pass over the event log once checkpoints are events) and (2) becomes a real control.

### SLOT-5: ruling check: unlabelled `cap / 2` floor bound; `cold` unmeasured; D183 states no ranked goals
- status: CONFIRMED (reading)
- severity: doc
- effort: a sentence each; blast radius: docs only
- location: vm_emit_trail_compact comment + emitted `margin < cap / 2 ? margin : cap / 2`; attr_text.c A5; decisions.md D183
- The quarter is labelled ("a choice, not a measurement", with the O(1) derivation): meets architecture.md "Tuning constants are suspect". The HALF ("never on a trail less than half full", "(at least cap / 2)") has no measurement, derivation or label in the comment, D183 or limits.md §4 paragraph 3 (lane/trailgc), and it decides the fast tier (cscan margin 255 > 56/2). Note the floor's stated purpose ("the next stretch still fits after a compaction there") holds only when margin <= cap/2.
- `noinline` on the floor is labelled MEASURED with regime -- meets the rule. `cold` (PCREC_ATTR_COLD, which also carries noinline; the enum name says only cold) is argued, not measured: minor.
- D183 decides "under the brief's rule" without stating it; no ranked goals appear in D183, K134 or the abi entry, so the ruling cannot be checked against its own goals from the record. Implied order (answers unchanged > flat cscan answers > never-full cost > bounded work) is served in that order; the cost goal is measured on two subject families only (my one extra probe agrees, below).

### SLOT-6: general form + unlocks (standing question)
- status: SUSPECTED (proposal)
- severity: design
- effort: n/a until a trigger fires
- General form: a BACK-EDGE SAFEPOINT primitive. The emitter knows at emission time every edge that can close a cycle (vm_goto/vm_jump to a written label, call return; after SLOT-1 nothing else), so `TRAIL_CHECK` generalises to one placed, checked site per loop turn for any amortised runtime bookkeeping, off the hot primitives; trail_checkpoints.py is already the generic "every weighted cycle passes a safepoint" check (change only the weight predicate). Unlocks + triggers: (1) growable caller-supplied trail (grow at a safepoint instead of giving up at the write) -- trigger: a pattern still giving up on trail with frames to spare after K134; (2) cancellation/deadline polling -- trigger: a user request for interruptible matching; (3) dead-frame compaction of the resume stack (TRAIL-SEG's frame twin) -- trigger: a FRAMES give-up on provably dead frames; (4) work-charge placement for loops the fail label never sees (vm_work's hand-placed sites, its revdet miss) -- trigger: another missed-charge finding.

## PROBED-AND-HELD

- Trail writes outside vm_set: none. `_SET(` text only at emit_vm.c 3572/3574; `_TRAIL(` only inside the SET macro definitions (12233/12267); no other src/gen emitter writes either. Region restores, splice parks/restores, counters, guards, cut/look marks all go through vm_set. Cursor, revdet locals, MRL clamp, gst are C locals or resume-depth values; `rv*_frame_mark` holds resume_depth, so compaction cannot stale it.
- Trail positions stored outside resume_stack[].trail_mark: none (every emitted trail_depth/trail_mark text grepped). The CALL macro records the mark before the |W| parks, so the parks are the first entries of the call frame's segment: kept, stay at mark+j.
- Text order == emission order: `v->b` assigned once (10337); only rewrite is vm_cls_respell (in place, no reorder); vm_lbl is the only label writer (3467); regions emitted after the main body into the same buffer (calls forward, returns checkpointed); vm_emit_trail_compact runs after the program is complete (12893), so nset/ncheck are final; the guarded matcher copy duplicates the prologue local too.
- Claim (c): the fail label rewinds to the popped frame's mark (13354-13356); depth after a resume <= depth at the last checkpoint and the next stretch is a checkpoint-free path. Compaction never raises depth at any program point vs the plain trail, so no give-up comes earlier than BASE; the fast tier at the half floor only gives up where the plain trail would.
- Sweeps (sweep.py = branch checker + independent backscan.py): corpus 4,984 lines (4,531 VM compiles; 691-1,040 with a checkpoint per set) x 9 flag sets {default; -fno-possessify -fno-revdet -fno-atomic-discharge -fno-splice-calls -fno-alt-island; -fno-counter -fno-length-prune; --unroll=1; --unroll=2; --trace; --vm-entry-shape=1; --no-captures; -e utf8 -i} = 40,779 artifacts; random shapes (gen.py seed 1: captures, lazy/possessive/counted repeats, lookarounds, backrefs, (?1)/(?&n), conditionals, \K) 4,000 x 3 flag sets = 6,921 compiled. 0 failures of any kind. Worst heaviest path == margin (251/251) on a deep non-looping nest, as expected.
- Never-full cost outside D183's two families: `(a|aa)+b`, a^1000 b, 2,000 searches, perf stat instructions:u on cpu 7: BASE 523.4M, SUBJECT 521.8M (1 checkpoint). No cost visible.
- vm_star's vm_jump conversion: the one conditional backward goto in the tree, now covered; vm_jump evaluates before the enclosing printf, so ncheck is consistent.
- `(?:(a)b)*+c` emits 0 checkpoints (cursor rung: SETs in an `if` after the C while): correct.
- abi provisional 93 (92 reserved for kit S3) recorded in abi_changelog.md; S693 re-pinned to 93/91: consistent apart from SLOT-2.
