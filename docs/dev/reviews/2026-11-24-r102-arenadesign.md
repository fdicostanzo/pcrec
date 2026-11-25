# Review r102 arenadesign: [ARENA-SCOPES] design (design mode, before the build go)

DRAFT by the coordinator, 2026-11-24. Dispositions are PROPOSED; the manager rules them.

## Subject
- `docs/design/arena_scopes.md` at b8308584a (lane/arenadesign), STATUS PROPOSED. Design tree T = 79a7ca279; the build would
  land on main F = 88bb21d73 (review tree built there, `nice make -j2`). `git diff 79a7ca279 88bb21d73 -- src cli lib
  memfn/src tests` is empty.
- Requirements: ACCEPTED arch note `docs/design/arena_scopes_arch.md` (D-1..D-12), r100/r101 RULED, r96 (GENFORM-8/9,
  COST-1/2), D203, D109, D191 adds. 1-2, K155, K163, src/core/CLAUDE.md, docs/dev/guide/ (architecture.md, coding.md); the
  owner's words of 2026-11-24 (quoted in the launch prompt).
- FREEZE DRIFT: main moved to 23238e972 during the round (dev journal only); decisions.md and plan.md unchanged.
- No committed evidence (the design ran no probe), so nothing was re-run before briefing.

## Verdict
NOT READY for a build go. Nothing here challenges the choice of shape (B) in principle, and every finding can be fixed
in the design text. But six findings show the release rules, as written, can free memory that is still in use, strand
memory, or fail to catch what they claim to (B1-B3, B7, B10, and B11's hook placement), and three gates cannot be met as
worded (B5, B11, B15). D-1's 4-vs-6 count, which decides the mechanism, does not survive re-scoring (B9). Recommendation:
a revision lane on these findings, then a light re-check round (fix-induced and readiness lenses) before the go.

## Lenses as run
| lens | model | question | why chosen | raw findings |
|---|---|---|---|---|
| premise | opus | are the design's "the existing X already does Y" sentences and counts true, and does D-1's A=4 vs B=6 survive? | launcher; a new mechanism (lens table: premise) | 7 |
| simulate | opus | hand-run L1-L5, the registering order, release, unwind and the closed check over every recovery point, including a nested part compile (K163) | launcher; a rule over real code paths (simulate; soundness-style hand execution) | 10 |
| costpeak | opus | records are on the heap: is arena peak really unchanged, what does a record cost per scope, and is G5 sound? | launcher; a measured quantity and a gate (measurement; complexity) | 5 |
| unlocks | opus | the general form beyond memory kinds, siblings, and unlocks with triggers (carries both standing questions) | launcher; the "critics propose unlocks" lens | 8 |
| conform | sonnet | does the design answer the ACCEPTED note and the RULED reviews, and is each build unit ready (cites, witnesses that can fail, STOPs)? | rulings relied on + the last check before a build go (ruling check; readiness) | 12 |

42 raw findings, consolidated to 32 (B1-B32). Verification was done inline by the coordinator: every CONFIRMED item is a
quote claim or a hand-run over the design's own text. 0 REFUTED (`review/verify.md`).

## Findings and proposed dispositions
Severity: memory = a strand, a leak or a use-after-free on some path; design = a decision or gate that is wrong or cannot
be met; doc = wording.

### Release rules and the registry (memory)
- **B1 (SIM-1, SIM-2) FIX-NOW, memory.** L1's check (`s->depth != a->depth`) does not catch a stale close once another
  scope has opened at the same depth. Because `Scope.mark` points to a record that can be reused through `spare`, the
  stale close releases an entry the ENCLOSING scope still owns (hand-run in the simulate file). `pcrec_scope_free` can
  also unlink the record a nested scope uses as its mark, and then the nested close runs past its own entries. The table
  row claims "double close" is caught. Fix: a mark record that each scope owns (a no-op kind, never on `spare` while the
  scope is open, its depth checked at close), with `pcrec_scope_free` allowed only on entries of the innermost scope.
- **B2 (SIM-3) FIX-NOW, memory/answer.** A record reused from `spare` keeps its previous kind's state. `pcrec_sb_free`
  resets only `p`/`len`/`cap` (sb.c), so `ar`, `cmt_*`, `layout_bytes` and the rest survive. A STRBUF record reused as an
  ARENA entry would release a garbage `head`. Fix: step (1) zeroes the taken record and sets its kind; `pcrec_scope_sb`
  then sets only `.cx`. This matches today's `StrBuf o = { .cx = cx }`, which G1 needs.
- **B3 (SIM-4) FIX-NOW, memory.** `pcrec_scope_check_closed` "before the success `job_cleanup`" comes after compile.c's
  takes have already moved `out_c`/`out_h`/`out_ir` into `out` (:3739-3744). If the check refuses, those strings are
  stranded, and sabotage row (5) would then go red for the wrong reason. Fix: run the check before the first take.
- **B7 (SIM-8, UNL-1, PREMISE-6, COSTPEAK-1) FIX-NOW, memory/design.** The base level is left unspecified. `owned` stays
  `AOwn` (arena-allocated, its own walk) beside the heap `LEnt` records, so "kept as the registry's BASE level (same
  release walk)" is false as written. Two readings follow. (1) If hold records are heap, as "records are heap" says, then
  the release text frees no `owned` record (a leak per hold). (2) If they stay arena records, step (1)'s malloc is not the
  hold's step. Separately, G2a's "attempt-arena high-water IDENTICAL; a favourable move is reported, not kept" is false
  at F4 (the K163 copy leaves the outer arena, compile.c:3735) and at R2 if the record moves. Read literally, that rule
  would reject a D203 bug fix. Fix: one record type and one walk, with the base level as the registry's bottom (UNL-1's
  form). Name where the hold's record lives. State G2a per unit, with the exact expected byte move at R2 and F4.
- **B10 (CONFORM-2) FIX-NOW, design.** Sabotage row (2) ("drop the release in `pcrec_scope_close`") cannot go red. The
  same attempt's `pcrec_arena_free` releases the entries, so LSan, ASan and alloc_check all stay green, and `make asan` is
  not part of `make test` anyway. Fix: `pcrec_scope_close` asserts `a->top == s->mark` after its walk, or
  `check_closed` also requires an empty `top`.
- **B14 (COSTPEAK-3) FIX-NOW, memory.** Step (3), "make the resource (... the StrBuf's first growth / the child's first
  block)", reads as making these EAGERLY, but today they are lazy. A child arena built eagerly takes a 64 KB block on
  clskit's empty path. Fix: STRBUF and ARENA entries start zeroed and grow on first use. Only HEAP needs steps 1-4.

### The K163 check and F4 (design)
- **B4 (SIM-5, UNL-6) FIX-NOW, design.** The lent count sits at two allocation sites, `pcrec_arena_alloc` and
  `sb_grow`. Other uses of the error channel bypass it: sb.c:228 `sb_simd_fail`, :473 `pcrec_sb_take`, :793 render_prefix.
  So do the design's own heap record takes. "0 after F4" therefore does not prove K163's class closed (D203; a population
  nobody counts). Fix: one channel accessor that every refusal path and every registering call goes through, and count
  there.
- **B5 (SIM-6) FIX-NOW, design.** After F4, a failure of the inner copy is ABSORBED: rc -1 makes `a4_parts_dfa` decline,
  and the compile succeeds with the plain artifact. It is not "diagnosed at the INNER point". W6's exact pin (`504, 982,
  0`) moves. Fix: F4's gate reads "nothing stranded; absorbed by the by-design fallback; W6 re-pinned in the same unit
  (D110)", and names the answer under OOM moving from a refusal to the plain artifact.
- **B6 (SIM-7, SIM-9) FIX-NOW, memory/doc.** F4 does not state its order. If the lent refusal comes before `c_src` is
  stored in its hold, that refusal strands `c_src`. "No longjmp there" can be read as "a failed allocation returns
  without storage". Fix: state the order (reserve holds, set lent, `part_compile`, clear lent, store, test the count), and
  state that the count never changes the allocation.
- **B16 (CONFORM-1) FIX-NOW, design.** `Ctx.lent` is a new Ctx field with writers in three files, but D-7 says "not a new
  Ctx field", and register row 6a's corollary (one writer, named readers) is not met. Fix: one owning accessor in arena.c
  (it pairs with B4), plus the field's writer/reader line.
- **B18 (CONFORM-5) FIX-NOW, doc/design.** F4 is a D203 bug fix, but the design does not carry D203's four items (class,
  the house rule it breaks, the sibling grep count, the class-level fix shape). It is also sized and ordered like a plan
  unit. K163 is SUSPECTED, so if the pre-F4 lent count reads 0 that must be a STOP, not a pass.
- **B24 (CONFORM-12) DOC.** U8 (the enclosing attempt owns the inner teardown) fired with this design, and K163 asks the
  design to choose between that and an outer-owned holder. The design takes the holder without saying it weighed U8. R2
  also reaches beyond A-ENTRY's "only the facts copy's lifetime" in `walk_part` without saying so.

### D-1, the deciding count (design)
- **B8 (PREMISE-2, UNL-2) FIX-NOW, design.** S4's "(B) CAN, 33 lines, keyed on the FIELD" relies on an entry kind the
  kind table lacks. HEAP holds the pointer VALUE, which goes stale after realloc (nfa.c:172, dfa.c:1591) and after the
  by-value swap (compile.c:587-591). It needs a FIELD row (`void **`). It also needs the Job registered before its fields,
  because `free(cx->job)` comes before `pcrec_arena_free` today. A by-address `owned` slot would give (A) the same
  capability, so "only shape that can delete anything at S4" is false.
- **B9 (PREMISE-3, PREMISE-1, COSTPEAK-4, PREMISE-4) FIX-NOW, design.** Re-scored, D-1's 4-vs-6 is a tie, 6/6. The (A)
  column scores a narrower (A) than the accepted note's, which lets heap blocks join through `Arena.owned`. With the
  StrBuf inside an owned record (the design's own STRBUF trick), S10 and S12 delete under (A) with no copy. S13's (A) cell
  is also wrong: `keyseen` is allocated once per call, before the refinement loop (minimize.c:132, :148, :151), not per
  pass, so it is not retained n times. Separately, (A)'s YES cells omit the 64 KB `ABLOCK_MIN` floor per child arena. The
  premise lens's view is that (B) probably still wins, but on cost and form: no 64 KB floor, early release, arena bytes
  left alone. Fix: re-score with the note's (A), and decide on the stated tiebreaker.

### Gates, witnesses and units (design/readiness)
- **B11 (CONFORM-3) FIX-NOW, design.** T1/W7 has no price. W4 alone makes about 33k arena allocations (callgrind), against
  the about 162 mallocs that test-alloc's roughly 60 s budget covers today. T1's `pcrec_arena_alloc` hook also breaks
  alloc_inject.h's rule "NOTHING UNDER `src/`, `cli/` OR `lib/` IS EDITED". The design does not say whether W7 shares the
  malloc counter, which would move every exact pin. Sabotage (1)'s only detector depends on W7. Fix: state the sampling
  (for example, only allocations while a scope entry is live), the counter, the floor, the budget, where the hook lives,
  and a STOP.
- **B12 (COSTPEAK-2) FIX-NOW, design.** By default massif records a peak only to within 1% (`--peak-inaccuracy`), so a
  +1% band is at the tool's noise. The predicted rise (at most about 2.2 KB) is about 34x below that band on a 7.6 MB
  peak. Fix: pin `--peak-inaccuracy=0.0` (and heap-admin), gate on the predicted delta, and keep +1% only as R-3's
  backstop. One SUSPECTED sub-item: the spare list pins small chunks in the brk heap, which massif cannot see.
- **B13 (COSTPEAK-5) FIX-NOW, speed/design.** Summed over the corpus, G5's +1% is dominated by the heavy compiles, so a
  per-compile regression goes unseen. The cost estimate itself holds: about 0.05% measured on two patterns, and nothing
  superlinear. Fix: gate per pattern (max or p95 ratio under callgrind), and put the sb_grow lent check after the
  capacity early return.
- **B15 (CONFORM-6) FIX-NOW, readiness.** No arena high-water counter exists in the tree, and G2a's has no unit to build
  it. Massif has no script. C0(b)'s three families and the k155fix2 witnesses are not named, and the G1 sweep is not
  named (`scripts/emit_sweep.py`). Units R1..F5 have no STOP (D191 add. 1(b)).
- **B19 (CONFORM-7) FIX-NOW, readiness.** "ALLOW rows 5 to 0" leaves out the rows the registry itself needs: the record
  malloc, and the StrBuf/Arena inside a record (scratch_builder_check.py:82-85 is the same family). Without them the
  scanner goes red at F1. Fix: "net -5, +k (named)". The `shape:NAME` feature is left with no user after F3.
- **B20 (CONFORM-8) FIX-NOW, doc.** The builder house rule changes (coding.md 1.6 and src/core/CLAUDE.md: builders
  "must be arena-backed"; minimize and scanedge are the "named exceptions"). D-12 says src/core/CLAUDE.md is "unchanged",
  and no unit carries the hunk.
- **B22 (CONFORM-10) FIX-NOW, readiness.** Witness reach is deferred to C0 with no fallback. S11, S12 and S14 have no
  filed stranding, so no check goes red-then-green at F2 or F3, and the clskit kit did not appear in 3 single-compile
  profiles. Fix: name S11/S12 beside clskit in C0(c), and list a client with no witness as SINGLE-CONTROL.
- **B28 (UNL-7) FIX-NOW, design (small).** D-11's check sits in the shared callback (src/gen/memfn_sites.c:70), whose only
  binder (:211) passes the attempt arena by construction. So the check can fire only under its own sabotage row, and it
  also blocks a later scope-child `mf_arena` for the kit's scratch (S27). Fix: move the check to the art binder. The
  design's path `memfn_sites.c` is under src/gen/.

### Doc and register
- **B17 (CONFORM-4) DOC.** The design re-words P6's event ("a field added to `Arena`" becomes "a field whose zero is not
  valid") and declines RM-3 without saying that is what it does. `child` is set by arena.c only, a writer rule that is
  never stated.
- **B21 (CONFORM-9) DOC.** The manager list drops items r100/r101 sent as PLAN: S27's trace, the [ARENA-REGROW] row
  update, P5, and the kit wording of D-11.
- **B23 (CONFORM-11) DOC.** D-10's three-kinds sentence leaves out `DfaMemo.arena` (Ctx-bound, freed by hand). R1 can
  only write an interim sentence, because `child`/`top` arrive at F1.
- **B25 (UNL-3) DOC.** L5's reason ("keeps the release order a single list") is false: the ARENA row's release is
  `pcrec_arena_free`, which already walks the child's registry. L5 blocks the owner's "special areas" form (marks inside
  a bump area), and a helper reached from both arenas (clskit.c `intern_records`). Fix: correct the reason, keep L5 for
  now, and name the trigger for lifting it.
- **B26 (UNL-4) DOC.** D-5's "a fix that is one call" holds only for StrBuf builders. The array members of S19
  (dfa.c `arena_regrow`, possessify.c `fq_push`) need a `pcrec_scope_realloc`. dfa.c's R1 R-3a rule ("scratch is
  arena-owned so longjmp cannot leak") is a family member D-1 does not count.
- **B29 (UNL-8, UNL-2) DOC.** Unlock table: a generic release signature (`release(void *storage)`) and a base level that is
  the registry's bottom are cheap in F1 and expensive later. They are needed by U4/P4's FIELD and RUN rows and by U6. The
  design should state them now, or say why not.
- **B30 (PREMISE-5) DOC.** `pcrec_count_groups` owns no Job (compile.c:3870-3912), so "the two recovery points that own a
  Job" should read "one".
- **B31 (PREMISE-7) DOC.** G4/D-1/D-8 counts are given with no command. Re-derived, all hold: 25 + 37 frees, 27 + 6, 5
  ALLOW rows, 2 known_stranded, 462 calls, 33 writers.

### PLAN / NOTED
- **B27 (UNL-5) PLAN.** GENFORM-9's "no second non-memory member" does not count the trace build's arrival restores: the
  `pcrec_cand_eval_reset` at the very handler top where D-4 adds the unwind, and 6 `pcrec_cand_trace_quiet` brackets that
  a longjmp skips. Whether trace-only members count toward GENFORM-9 is the manager's call. Feed the count to U6.
- **B32 (SIM-10) NOTED.** Pre-existing: two test drivers (cpset_model_check.c, varexp_check.c) run a Ctx with no recovery
  point. No scope client is reachable from them. The "six test-tier points" count holds; the grep also matches
  proof_run.c's sigsetjmp, which is unrelated.

Counts: FIX-NOW 21 (B1-B16, B18, B19, B20, B22, B28); DOC 9 (B17, B21, B23, B24, B25, B26, B29, B30, B31); PLAN 1 (B27);
NOTED 1 (B32); REJECTED 0.

## PROBED-AND-HELD (consolidated)
- All 11 recovery points (5 src setjmps; 6 test) end in `pcrec_arena_free` on their Ctx. FIT_FORCE_NEXT is the one
  arrival that resumes, and no STRBUF client is live in the force loop (facts_force comes after layout and stamps).
- The real nesting depth in the first build is 1: no client calls another while its scope is open. `keyseen` is always
  the top record, so popping it is O(1).
- No HEAP table in minimize.c or scanedge.c is `realloc`'d, so HEAP records keyed on the value hold for the first-build
  clients.
- A StrBuf inside its record follows `sb_grow`'s realloc (sb.c:65-66). D-6's "both sides heap" holds (no `.ar` write on
  a Job StrBuf).
- After F4, the inner compile writes nothing through the outer arena except the one pointer store into the hold (checked
  across all 11 `Arena *` struct fields).
- Peak: at most 10 live records (scanedge) at about 224 B each, so 2.2 KB; the design's "under 4 KB" holds, and about
  4.5 KB for a 2-part compound. On the measured probe, the massif peak sits before any scope client runs.
- Cost: measured on 2 patterns, the lent check is about 0.04-0.05% of instructions; nothing is superlinear in a size the
  user controls.
- D-1..D-12 are all answered (12/12). D-6 explains why it does not build r96's by-`.ar` form. Every sabotage id the
  design cites exists.
- FILE* sites: no second member (14 `fclose` lines in 5 files, ordered safely). The goto-out ladders restore state, not
  memory (counted under B27).

## Which lens caught what
premise: B8, B9 (lead), B7 (part), B30, B31. simulate: B1, B2, B3, B4, B5, B6, B7 (lead), B32. costpeak: B7 (part), B9
(part), B12, B13, B14. unlocks: B4 (part), B7 (part), B8 (part), B25, B26, B27, B28, B29. conform: B10, B11, B15-B24.
The most productive lens was simulate (the answer-level and memory holes in the rules). B7 was reached by four lenses from
four sides.

## Recommendations
- A D27 spec-first test author is NOT recommended: the subject is internal, with no caller-facing contract (no spec hunk,
  D80).
- Next round: after the revision, fix-induced plus readiness (one per build unit). Simulate re-runs B1-B3 and B6 over the
  revised text.

## Lessons for the guide (proposed)
- Premise lens: when a design picks between named shapes by a COUNT, re-score the rival using the ACCEPTED note's
  definition, not the design's restatement (B9).
- Simulate lens: a registry whose marks are record pointers and whose records are reused gets a STALE-HANDLE drill
  (close, reopen at the same depth, then close the stale handle) and a FREE-THE-MARK drill (B1).
- COMMON template: findings go under `## Findings`, above `## PROBED-AND-HELD` (one critic appended all 12 under the held
  heading).

## RULED (manager, 2026-11-24)

- Every PROPOSED disposition ACCEPTED as written: FIX-NOW 21, DOC 9, PLAN 1, NOTED 1. A FRESH design lane (arenadesign2)
  writes rev 2 on lane/arenadesign; there is no fix-in-place by the rev-1 author.
- B9: rev 2 re-scores D-1 with the ACCEPTED note's definition of shape (A) and states the deciding reason as found. If
  (B) wins on cost and not on count, the design says so; a mechanism choice that flips goes back to the manager
  before the build go.
- B27 (PLAN): the trace build's arrival restores as GENFORM-9's possible second non-memory member go into
  [ARENA-SCOPES]'s refs as an unlock, with its trigger. They are not built in this design.
- Next: a fix-induced plus readiness round (one or two critics, next free review number), then the owner's build go.
- Lessons 1 and 2 ACCEPTED into the pcrec-critic lens table (premise: re-score a rival by the accepted definition;
  simulate: stale-handle and free-the-mark drills for any registry with reused records). Lesson 3 ACCEPTED (COMMON
  template wording).
