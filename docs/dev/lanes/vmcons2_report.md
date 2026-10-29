# Lane vmcons2: ONE design for the VM trail and dispatch build, rev 2 (the analysis input complete by construction)

Lane vmcons2 (opus), 2026-10-29. Design and measurement only (no build go): nothing under
`src/`, `cli/`, `lib/` or `memfn/` changed. Worktree `worktrees/vmcons2`, branch
`lane/vmcons2` off main 7596d4881. This document REPLACES rev 1 (`vmcons_report.md`) for the
build. It applies review `docs/dev/reviews/2026-10-29-r6-vmcons.md` (cited `[r6 S-n]`,
`[r6 SEAM-n]`) and its MANAGER RULINGS, the ROOT-CAUSE RULING first. Rev 1's dispositions of
review r3 (`[r3 Fn]`) stand unless a row below supersedes them. Rulings file
`vmcons2_rulings.md`: empty at handoff.

Base code: lane/trailgc 06aa5ab87 (D183), the tree review r6 read. The survey reads its
`src/gen/emit_vm.c` three-way merged with main's one emitter change since the merge base
(95832f09c, [INLINE-C] stage 3's definition-site callout view), so it describes the text the
build will edit. Probes ran on a scratch build of lane/trailgc (`git archive`, `make`).
Evidence: `docs/dev/lanes/vmcons2_evidence/` (scripts, the classified site table, logs);
scratch `/var/tmp/pcrec-pcrec/scratch/vmcons2/`.

## Summary

- **Premise test: reproduced.** Review r6's S-2 witness `^(a)${v}c` (v = `b`) on `abc`.
  - The listing records the variable compare as `label / note / fail / goto L6`. Rev 1's FAIL
    row ("successors: the unwind") ends every path there, so the SETs of slots 2 and 3 have no
    read after them, and V3 deletes both.
  - Stock and libpcre2 give 1:0,1; the rule-as-written twin gives 1:-1,-1.
  - Evidence: `vmcons2_evidence/premise.sh`, `premise.log`. `[r6 S-2]`
- **Printing is recording (the new Stage -1).** Every statement a matcher's emitter prints goes
  through ONE recording primitive, `vm_stmt`. Only that primitive can write the matcher body
  buffer: it lives in its own file, and `emit_vm.c` holds only an opaque handle.
  - Every statement kind is a row of ONE declared table: an event with its reads, writes, edges
    and cursor effect, or a declared no-effect form.
  - Each record carries a token signature that the primitive checks against the text it
    prints. This is a count, not a parser.
  - A statement whose kind has no modelled row, or whose text breaks its signature, makes the
    function unanalysable (V0): every verdict is KEEP and D declines.
  - The corpus token-count check becomes a STRUCTURAL check: no write to a matcher body
    outside the primitive. A compile error enforces it, and a grep guard backs it.
  - This one rule covers r6's S-1, S-2, S-3, S-5 and S-7 and any shape not yet found.
    `[r6 S-7, SEAM-3; ROOT-CAUSE RULING]`
- **The survey: feasible and byte-identical** (STOP RULE not triggered).
  - Inside the walk, `emit_vm.c` writes the body through **132 print calls**. They form **91
    statement sites**. The other 41 calls are 30 fragments of a statement, 6 comment calls,
    4 span-block lines and 1 post-pass.
  - Of the 91 sites: **21** already record a correct typed event, **4** record one with missing
    operands, **20** record the wrong kind (mostly NOTE standing for a branch, a cursor move or
    a cut), and **46** record nothing.
  - Outside that: 23 print calls write the matcher's fixed frame (prologue, accept, fail
    label); 4 calls hand the body buffer to delegated writers (the kit's span and run sites,
    the class-kit inline test, the callout call-site rows); 1 post-pass rewrites class reads.
  - Every one of these is a `pcrec_sb_*` call on the body buffer, or a writer that is handed
    it. Each can print the same bytes through the primitive. So the refactor (a) is a pure
    refactor: C artifact and listing byte-identical, no abi bump. It is proven by a
    two-compiler diff over the corpus plus the structural check, and lands FIRST and alone.
- **Today's gap, measured** (24 witness artifacts, `census.tsv`):
  - unrecorded statements: 207 `goto <p>_fail` against 146 FAIL events; 79 slot reads, none
    recorded; 136 cursor writes, 103 local writes, 280 `if (` openers and 48 block openers,
    none recorded as such;
  - recorded exactly: SET, PUSH, CUT and CALL, which already go through primitives.
- **The kind table answers r6's answer findings with one general rule each:**
  - GUARD is a statement with a skip edge, so a guarded SET is a may-write by the graph, not by
    a clause `[r6 S-1]`;
  - a conditional fail is BRANCH_FAIL, and VAR/BREF are compound consumes with both edges
    `[r6 S-2]`;
  - every cursor assignment is a typed SEEK, and FIRST+ is position-blind only up to the first
    cursor move that is not a forward consume or a member of a declared group (SPAN, ISLAND)
    `[r6 S-3, S-5]`;
  - SPAN and ISLAND are group openers carrying their first-byte class `[r6 S-5]`.
- **Verdict identity** is `sid = (node, instance, site line, k)`, assigned inside the primitive
  BEFORE the verdict lookup.
  - So a deleted or retagged statement still consumes its id, a vanished checkpoint shifts
    nothing, and D's own statements carry D's site lines.
  - Three checks; the second and third can fail on a keying slip:
    - K1: all-KEEP byte identity (necessary, vacuous for keying);
    - K2: one-entry maps change exactly one site;
    - K3: walk 3's sids equal walk 2's, minus checkpoints.
  - The ordinal keying of rev 1 is the sabotage, with named cells. `[r6 S-4, SEAM-1]`
- **Rest of r6, as ruled:**
  - S-6: kept-ordinal restore sentence, codegen assertion, cell;
  - S-8: R's guard on the PREPROCESSED matcher, plus a macro sabotage;
  - SEAM-2: rounds stated as an in-memory fixpoint over walk 2's records, with the faithfulness
    invariant checked by K3; Q3 dissolves;
  - SEAM-4: phantom cap dropped; `npush` kept, compared against the D-free push count; S305
    stays detected;
  - SEAM-5: EXPECTED-MOVES for STEP 0's 0a and the stage gates, GIVEUP1 rows, framebuffer.rxt
    cell 1 and sr_depth.rxt:58-59 in the census;
  - SEAM-6 and SEAM-7: DOC and STEP 0 cards;
  - SEAM-G1/G2: DOC and PLAN.
- **Build plan:**
  - (a) printing-is-recording refactor: byte-identical, no abi event, lands first and alone;
  - (b) R, abi event 1;
  - (c) the analysis build (walks, D stage 1, C-move, verdicts, the full listing), abi event 2.
  - STEP 0 runs between (a) and (c)'s build go. Its new card 0n checks that the analysis rules
    give the same verdicts on (a)'s real RECORDS as on the text, over the corpus.
- **Flags** (Frank's F11 ruling; memory `pcrec-flag-follows-caller-effect`):
  - one public deny for D;
  - the slot-flow verdicts on the `--harness` lever;
  - R and both refactors (a, the C-move): none.

## Disposition table

One row per review r6 finding (and its recommendations and lessons). "Where" is this
document's section.

| id | ruled | disposition here | where |
|---|---|---|---|
| S-1 | FIX-NOW | GUARD/GUARD_END are statement kinds. The GUARD has two successors: the block, and the statement after its GUARD_END (the skip edge). A SET inside is a may-write by the graph: the meet at the join keeps the skip path's facts, so no special clause exists. Single-line guarded writes (`if (c) x = y;`) record GUARD, the statement and GUARD_END with no printed brace. Witness cell C1; sabotage: no skip edge. | Printing is recording; The statement-kind table; Test cells |
| S-2 | FIX-NOW | VAR and BREF are compound consume rows: successors next-label AND the unwind, FIRST+ OPAQUE, reads (BREF: 2g, 2g+1; VAR: caller variables, constant). FAIL ends a path only for an unconditional `goto <p>_fail`; every conditional one is BRANCH_FAIL. The signature counts `goto <p>_fail` per statement. The CALLOUT row's edges are explicit (succ, fail, give-up), so its "next" no longer means the next event. Cells C2a-C2c. | The statement-kind table; Test cells |
| S-3 | FIX-NOW | Every `scan_position` assignment that is not a forward consume is a SEEK record (RESTORE from a slot, BACKSTEP, ADVANCE, SPAN_COMMIT). FIRST+ is OPAQUE at every SEEK except a SPAN_COMMIT of the span in progress. A lookbehind is a BACKSTEP followed by FORWARD consumes, and the CLASSB row's description is corrected (CONSUME_BACK is the revdet walk's local cursor only). Cells C3a, C3b. | The statement-kind table; Test cells |
| S-4 | FIX-NOW (= SEAM-1) | Stable statement identity `sid = (node, instance, site line, k)`, assigned before the verdict lookup. Checks K1-K3; K2 and K3 can fail. Sabotage: rev 1's ordinal keying. Cells K2a, K2b. | Verdict identity across walks |
| S-5 | FIX-NOW | SPAN is a group opener carrying (class of the first stride byte, min, stride, span id). FIRST+: F ∪= class, then continue along the zero-iteration path iff min = 0. A span-cursor PUSH and the span's SPAN_COMMIT are members: no fork, continue. Cells C5a, C5b. | The statement-kind table; Test cells |
| S-6 | FIX-NOW | V2 row: a kept restore reads its snapshot at its ordinal among the KEPT entries of its own site. Codegen assertion: at each call site, the snapshot SET list and the restore list are the same slot sequence. Cell C6; sabotage: original ordinals. | The statement-kind table; Test cells |
| S-7 (+ SEAM-3) | FIX-NOW | The root-cause rule: one writer (`vm_stmt`), one declared kind table with a row for every kind (the six r6 named included), V0 on an unmodelled kind or a signature mismatch at compile time, every compile. NOTE becomes an annotation that has no text argument, so it prints no C by construction. The corpus check becomes structural, plus a corpus census of zero mismatches. | Printing is recording |
| S-8 | FIX-NOW | R's guard runs on the PREPROCESSED matcher (`gcc -E` of the artifact, the matcher function cut out after expansion), so the seven `RX_*` macro bodies are read. Sabotage: one macro left on `run->trail_depth`. | Gates and STEP 0 (stage (b) gate); Test cells |
| SEAM-1 | FIX-NOW (= S-4) | As S-4. The CHECKPOINT premise `^(?:(?1)y)*(a\|b)$` is cell K2a. | Verdict identity across walks |
| SEAM-2 | FIX-NOW | Walks 1-3 are emissions. The rounds are a fixpoint over walk 2's record list. Invariant: DELETE is a tombstone (no effect in any column, prints nothing), SETU is a retag (writes s, trail no), and CHECKPOINT records are slot-neutral. K3 checks that walk 3's records equal the fixpoint's list modulo checkpoints. Q3 dissolves: only D, which ADDS statements, needs its own emission. | Verdict identity across walks |
| SEAM-3 | FIX-NOW (with S-7) | As S-7. The compile-time count is the per-statement signature inside the primitive, on the `vm_cls_reads` precedent (a count, not a graph). | Printing is recording |
| SEAM-4 | FIX-NOW | The phantom "resume-point cap" is dropped. `npush` stays the pre-pass count in the listing's `resume-points` row. run_ir_listing.sh's under-count assertion compares it with the push count of the D-denied compile, which differs from walk 1 in no PUSH. S305 stays DETECTED. Readers named: run_ir_listing.sh (the resume-points block), S305, `vm_reseed_cal[has_push]` with [OPT-HYB-RESEED]'s calibration check, and tests/vm/run_vm_tests.sh's comment (DOC). | Verdict identity across walks; Gates and STEP 0 |
| SEAM-5 | FIX-NOW | An EXPECTED-MOVES list (cell, stock give-up, build answer, libpcre2 answer) for 0a, checked like 0e. Stage gates read "equal except the listed GIVEUP1 cells, each libpcre2-checked". `GIVEUP1_ALLOWANCE` rows per arm (the deny flag and the internal arm). The existing `-fno-req-byte\|sr_depth.rxt` rows are re-triaged. framebuffer.rxt cell 1 and sr_depth.rxt:58-59 join the census. | Gates and STEP 0 |
| SEAM-6 | DOC + PLAN | G1's give-up clause restated: no new give-up at the stamped capacities, nor at any `ntrail` at or above the plain trail's need. Inside D183's gap band a give-up may move, as limits §4 paragraph 3 already allows. STEP 0 card 0k: ntrail sweeps on np, pp and an oscillating-kept-set shape. | Gates and STEP 0 |
| SEAM-7 | PLAN + DOC | STEP 0 card 0l measures D-off against unroll-K-down, handoff-off and prefilter-off on near-cap artifacts. Leaning: `drop-dispatch` is the FIRST retrying VM rung, and the unroll trial sees D's bytes. Census: `COMPILE_MAX_ATTEMPTS`/`fit_tables_selfcheck`, limits §8.4¶3's count, §8.5's stamp and note rows, `--size-cap=refuse`, the `src/core/axes.def` row. | Gates and STEP 0; Cost |
| SEAM-G1 | DOC | [OPT-ALTCLS] stage-2 prefix factoring joins the first-consumed-byte family. It runs first, so D sees factored alternations. K_c and `vm_build_region_saves`' W are named together: W is the upper bound, and V2 narrows it per site. `_VM_DISPATCH_SITES` takes the activity-count stamp registry shape. | The statement-kind table; Cost |
| SEAM-G2 | PLAN | General form: "emission parameterised by a verdict map keyed by stable sids", with the rounds as its in-memory fixpoint. Unlocks (a)-(d) filed with r6's triggers. (e) is BUILT here: an unmodelled kind declines, so the table can grow one row at a time. | Verdict identity across walks; Cost |
| Rec. D27 author | ACCEPTED | A spec-first author for (c), briefed with G1's promise and the give-up direction. | Gates and STEP 0 |
| Rec. print-site probe | ACCEPTED | Done here as the survey (`site_kinds.tsv`). After (a) the probe becomes the census card 0m. | Printing is recording; Gates and STEP 0 |
| Lessons 1-3 | for the manager | They are the manager's to add to the guide (`docs/dev/guide/critics.md` is outside this design). This design applies all three: statements counted, not chosen tokens; a non-identity map pinned; expected moves in every gate. | — |

**r3 rows carried from rev 1.** F2, F3, F5, F6, F8, F9, F10, F11, F13, F14, F15, F16, F18,
F19, F21-F27, F29-F37 and SLOTS-5 stand as rev 1 disposed them; their text is restated below
where the build needs it. Superseded:

- **F1 and F17** (the analysis input, one table): by "Printing is recording" and the kind
  table.
- **F4**: by the rounds statement under SEAM-2.
- **F7**: "the resume-point cap" is struck (SEAM-4).
- **F12**: the checker gate rule stands, and the text checker becomes card 0n's text
  prototype.
- **F20**: by SEAM-G2's general form.

## Printing is recording

### The survey

Method: `vmcons2_evidence/sites.py` and `calls.py` list every `pcrec_sb_*` and `vm_ev` call
in the merged `emit_vm.c` with its enclosing function and target buffer. Every call writing
the body buffer (`v->b`, its aliases `b`/`bb`, or the scratch `t` that is spliced in) is
classified by hand in `site_kinds.tsv`: one row per print call, with the rev 2 kind and
today's status.

**Who writes a matcher body.** The matcher function is three pieces:

- the frame, written straight into the artifact by `vm_emit_search_body`;
- the walk's body, written into the Job-owned scratch buffer `job->vmsb` and spliced in;
- the `__match_notempty` copy, a text copy of the first two made by
  `vm_emit_guarded_matcher`.

Callee regions are inside the same function (computed goto). Callout code runs in a separate
function that receives `ctx` only. The `RX_*` macros are file-scope definitions.

| writer | calls | statement sites | today |
|---|---|---|---|
| walk prints in `emit_vm.c` (32 functions) | 132 | 91 | 21 OK, 4 operands missing, 20 wrong kind, 46 none |
| ...of which fragments of a statement (condition text, block tails) | 30 | — | part of their statement |
| ...of which comment calls (role line, the bref comment) | 6 | — | no effect |
| ...of which the span block's inner lines | 4 | — | part of SPAN |
| ...of which post-pass (`vm_cls_respell`) | 1 | — | value text only |
| frame prints in `vm_emit_search_body` (prologue locals, `goto L0`, accept, fail label) | 23 | 23 | no records |
| delegated writers handed the body (`pcrec_memfn_emit` x2, `pcrec_clskit_emit_inline` via `vm_cls_test`, `pcrec_callsite_emit`) | 4 | inside SPAN, CONSUME(LIT), island BRANCH, CONSUME/BRANCH tests, CALLOUT | no records |
| `vm_emit_guarded_matcher` (the notempty copy) | 3 | 1 added guard | no record |
| `PCREC_SIMD_WITNESS` block (test build only) | 1 | 1 | no record |
| `vm_ev` calls | 54 | — | most sit next to their print and merge into it; the rest become annotations (RUNG, STRAT, PRUNE, NOTE) |

**The 91 walk statement sites by rev 2 kind** (counts of sites):

- branches: BRANCH 21 (the MRL test is a BRANCH or a BRANCH_FAIL by its target), BRANCH_FAIL 9, BRANCH_ABORT 1;
- guards: GUARD 6, GUARD_END 6;
- local writes: LSET 15;
- cursor writes: SEEK 6;
- consumes: CONSUME 3, CONSUME_BACK 1, SPAN 1, BREF 1, VAR 1;
- calls: CALLOUT 1, STEP 1;
- island: SWITCH, CASE and SWITCH_END 1 each;
- one each: SET (two spellings), PUSH (two spellings), LABEL, GOTO, FAIL, CUT, CUT_LOCAL (2),
  CALL, RETURN, CHECKPOINT, WORK, ACCEPT.

Sites with the wrong kind today:

- **as VE_NOTE:** the trail checkpoint, the work charge, the MRL test, the span reach and rmin
  tests, the counter trip and bound, the empty-iteration rule, every lookbehind guard and
  end-check, the back-step, the lookaround cursor restore, the revdet cut and lazy commit;
- **as unconditional VE_GOTO:** the island's three compare forms (conditional);
- **as unconditional VE_FAIL:** the BREF and VAR conditional fails.

The 46 with nothing are the guards, the local writes, the span's own tests and moves, the
revdet walk's statements, the island advance and switch, and the callout's step charge.

Slot reads hide in value text: 31 format strings outside the one read primitive `vm_slot_ref`
spell `slot_values[` (SET sources, branch conditions, the CUT work count, the callout view).
`vm_rolef` builds 22 C fragments, not role strings (gotos, slot reads, cursor expressions).

**Today's gap on emitted artifacts** (`census.py`, 24 witness artifacts, 48 compiles at the
base; per-artifact rows in `census.tsv`). Totals:

| token in the body text | count | matching events in the listing | gap |
|---|---|---|---|
| `RX_SET(` / `RX_PUSH(` / `RX_CUT(` / `RX_CALL(` | 112 / 57 / 5 / 4 | set 112 / push 57 / cut 5 / call 4 | none: they already go through primitives |
| `goto <p>_fail;` | 207 | fail 146 | 61 conditional fails unrecorded or recorded as unconditional |
| `slot_values[` (reads and raw writes) | 79 | none | every read unrecorded |
| `scan_position` writes | 136 | consume 118 (forward consumes only) | seeks, span commits, island advances, bref/var advances |
| span/revdet local writes | 103 | none | every local write |
| `if (` | 280 | assert 27 | guards and branches |
| block openers `{` at line end | 48 | none | guards, scopes |

### The primitive (one writer)

**`vm_stmt`** (new file `src/gen/vm_stmt.c`, its header private to `src/gen/`) is the ONLY
function that appends to a matcher body. Its call carries:

- the statement's KIND (an enum value indexing the declared table);
- its typed operands: target label(s), slot written, local written, cursor effect, group id
  (span or island);
- its role text;
- the C text, as a format and arguments.

It does five things, in this order:

1. assign the statement's sid (Verdict identity across walks);
2. consult the verdict map for that sid (walk 3 only; walks 1-2 and every compile without
   verdicts pass KEEP);
3. append ONE record to the stream (the existing `VEvent` array, grown to carry the new
   operands, the read list, the sid and a tombstone flag);
4. unless the verdict is DELETE, print the text into the body;
5. count the text's tokens against the record's signature (below).

**Reads are recorded where their text is made.**

- `vm_slot_read(v, slot)` and `vm_local_read(v, local)` return the `slot_values[...]` or local
  text AND append the slot or local to the pending read list. The next `vm_stmt` moves that
  list into its record.
- The 31 raw `slot_values[` formats and `vm_slot_ref`/`vm_slot_expr`'s 10 callers move onto
  these.
- A fragment built but never printed would leave stale pending reads on the next statement.
  That is the safe direction: an extra read only keeps a write alive.

**Compound statements.**

- A block whose effect is one thing is ONE statement, its inner lines printed through the
  primitive's fragment interface: SPAN with the kit's advance; BREF, VAR and CALLOUT blocks;
  the WCLASS decode block; the region RETURN; the island SWITCH with its CASEs.
- A block holding ordinary statements is a GUARD pair, so those statements stay separate
  records: the guarded capture publishes, the revdet retreat and extend pushes, the revdet
  group publish, the rmin low-water set.
- `vm_work_at` gets a fragment form for the work charge inside BREF and VAR. The charge is then
  a declared part of those rows, not a separate record.

**Delegated writers write fragments.**

- `pcrec_memfn_emit` (kit span and run sites), `pcrec_clskit_emit_inline` and
  `pcrec_callsite_emit` are handed the primitive's fragment buffer, never the body.
- That buffer is Job-owned (for the longjmp cleanup, like `scr_test`) and carries the body's
  comment setting (`pcrec_sb_comments`, set beside `vmsb`'s in compile.c). So kit comments
  strip identically.
- No kit change: the hook signatures already take a `StrBuf *`.

**The frame and the post-passes are declared writers in the same file.**

- The prologue's declarations and initialisers (DECL), `goto <p>_L0` (ENTRY), the accept
  return (ACCEPT_RETURN), the fail label's pop/rewind/dispatch (UNWIND) and the `--trace`
  lines (TRACE) are printed by `vm_stmt_frame_*` functions in `vm_stmt.c` as records of their
  own kinds.
- `vm_cls_respell` (value-text table reads) and the notempty copy (`vm_emit_guarded_matcher`
  plus one NOTEMPTY_GUARD record) move into `vm_stmt.c` as its two declared post-passes.
- The body text is then exposed READ-ONLY: `vm_stmt_body_text()` for `vm_cls_reads` and
  `pcrec_sb_len_decide`.

**Annotations print nothing by construction.** `vm_note(v, kind, role)` for NOTE, RUNG, STRAT,
PRUNE and ISLAND takes no format and cannot reach the buffer. A note that today accompanies a
printed statement becomes that statement's role. `[r6 S-7]`

### The per-statement signature (the compile-time completeness count)

Every row of the kind table declares its TOKEN SIGNATURE as a function of the record's
operands. The primitive counts these tokens in the text it prints (fragments included) with
`strstr` loops, on the `vm_cls_reads` precedent:

| token | must equal |
|---|---|
| `goto <p>_L` | the label edges the record lists |
| `goto <p>_fail` | 1 if the record has an unwind edge, else 0 |
| `goto *` | 1 for RETURN and UNWIND, else 0 |
| `return` | the record's give-up/abort/return exits |
| `slot_values[` | reads + raw slot writes recorded |
| `scan_position =`, `+=`, `++` | the record's cursor effect (0, 1 move) |
| `run->` assignments, `--run->` | the declared run-state writes (CUT_LOCAL, STEP, RETURN, UNWIND) |
| `<P>_SET(` `_PUSH(` `_CUT(` `_CALL(` `_TRAIL_CHECK(` `_CHARGE_WORK(` | 1 for the kind that owns the macro (or a compound that declares it), else 0 |
| brace balance | 0, except +1 for GUARD/SWITCH openers, -1 for their ends |

A mismatch, or a record whose kind row is UNMODELLED, marks the matcher function V0. That runs
on every compile, not on the corpus. Kit text is free to contain `if`/`while`/its own locals
but no token above beyond its row's declaration. So a kit text change that adds a goto or a
cursor write turns its artifact V0, not wrong. `[r6 SEAM-3]`

In (a) nothing reads V0 (no analysis exists yet), so a mismatch changes no output. The
test-only harness option `--harness=stmt-records` prints the full record stream with sids and
a per-function census line (statements, records, mismatches, V0). The corpus check asserts
zero mismatches and zero V0. From (c) on, a mismatch's effect is all-KEEP plus D declining:
correct, slower, and visible in the listing.

### The structural check (replacing the token-count corpus check)

`tests/codegen/run_stmt_writer.sh` (new; light, no compiles):

1. **By construction:** `emit_vm.c` cannot name the body buffer. `Vm` holds an opaque
   `VmStmt *`. The `StrBuf` lives in `vm_stmt.c`, and `job->vmsb` is referenced only there
   and in compile.c's allocation and cleanup. A raw `pcrec_sb_printf(v->b, ...)` is a compile
   error.
2. **The grep guard**, so nobody re-exposes the buffer:
   - no `StrBuf *` getter in `vm_stmt.h`;
   - outside `vm_stmt.c`, `vmsb` appears only in compile.c's two lines;
   - `pcrec_memfn_emit`, `pcrec_clskit_emit_inline` and `pcrec_callsite_emit` are called from
     `emit_vm.c` only with the fragment buffer.
3. **Sabotages** (one row each in the mech table):
   - (i) a getter added and one raw print through it: check (2) red;
   - (ii) one statement re-typed (the back-step printed as an LSET): the census red, with
     `site=` naming it;
   - (iii) one read printed as raw text instead of `vm_slot_read`: the census red (the
     `slot_values[` count exceeds the recorded reads).

The corpus census (card 0m, then a `make test` section) tests the signature check rather than
standing in for it. `[r6 S-7, SEAM-3]`

### Byte identity of (a)

**Why it is a pure refactor.**

- Every new call prints the same format with the same arguments at the same program point; it
  only also records. Fragments concatenate to the same bytes. The fragment buffer for
  delegated writers carries the same comment mode.
- Counters that steer emission move unchanged: `nset` and `lbl_nset` (checkpoint placement,
  D183), `nwork`, `nclamp`, `ncheck`, `emitted_push`, `has_push`.
- The listing stays identical through the kind table's LEGACY column: the op a record
  renders as in (a) ("none" for a statement that had no event).
- Each legacy `vm_ev` either merges into the adjacent primitive call (no other event between
  them) or stays an annotation record at its original position. So the listing's row order
  and its `events` count are unchanged.

**What proves it.**

- A one-time two-compiler diff over every corpus `pattern` line, with its own flags, at both
  prefixes, default engine and `--engine=vm`, `-e utf8` where labelled. Compared: C artifact
  and `--emit-ir` byte for byte. This is §5.4's precedent: landing evidence in the commit and
  the lane report, under `scripts/boxlock`.
- `run_recursion_identity.sh`'s FILEPIN stays put (no abi bump).
- The structural check and the census are green with sabotages (i)-(iii) detected.

**Hazards, each with its guard.**

| hazard | guard |
|---|---|
| comment-tier stripping in fragments | the fragment buffer is set by the same `pcrec_sb_comments` call as `vmsb` |
| event reordering in the listing | the merge rule above; the listing is in the identity diff |
| a fragment printed twice or dropped | the identity diff |
| longjmp cleanup of the new buffer | Job-owned, freed beside `scr_test` in compile.c |

### Feasibility (STOP RULE)

Feasible, and byte-identical. Every writer of a matcher body is either a `pcrec_sb_*` call on
the body buffer, or a pcrec-side adapter (in `src/gen/`) that takes a `StrBuf *`. No writer
needs a second description of the program, and none needs a kit change.

The only judgement calls are which multi-line blocks are ONE statement (compound) and which are
a GUARD pair. The table below fixes each one by its effect: a block holding a SET, PUSH or
branch to a label is a GUARD pair, so those stay separate records.

## The statement-kind table

ONE table, `vm_stmt_rows[]`, indexed by kind. Each analysis reads its own column; nothing else
decides. A kind added before its columns are written carries UNMODELLED and makes its function
V0.

Notation:

- `s` is a slot and `L` a label;
- R are the record's recorded reads, W(g) the slots region g can write (minus 0/1), and R_c
  the return label of call site c;
- ncap = the pattern's groups + 1;
- "unwind" is the fail label (modelled by the PUSH edges);
- "exit" is a return out of the matcher (give-up or abort), which reads no slot.

| kind (sites) | successors | reads | writes | copies (must) | MAYFRAMES | FIRST+ | verdict site | legacy op in (a) |
|---|---|---|---|---|---|---|---|---|
| LABEL | next | — | — | meet of preds | join of preds | continue | — | label |
| COMMENT | (no-effect form) | — | — | — | — | continue | — | none |
| GOTO L | L | — | — | — | — | continue at L | — | goto |
| FAIL (unconditional `goto <p>_fail` only) | unwind | — | — | — | — | path ends | — | fail |
| BRANCH L (21: tests, asserts, island compares, guards' cousins) | L, next | R | — | — | — | fork both (a peek moves no cursor) | — | assert / goto / note / none |
| BRANCH_FAIL (9: conditional fails) | next, unwind | R | — | — | — | continue at next | — | note / none |
| BRANCH_ABORT (lookbehind negative end-check) | next, exit | R | — | — | — | continue at next | — | note |
| GUARD / GUARD_END (6 pairs + 3 single-line) | GUARD: the block AND the statement after its GUARD_END; END: next | R (GUARD) | — | — (the join does the meet) | — | fork both | — | none |
| SWITCH d / CASE c→L / SWITCH_END (island) | every CASE target and the statement after SWITCH_END | subject | — | — | — | inside an ISLAND group: see ISLAND | — | none / goto / none |
| PUSH L, pos | next, L (resumes at pos) | live-in(L) ∪ R | frames | L inherits the pusher's facts | adds L | pos = cursor: fork; pos = span cursor of the open SPAN: continue, no fork; any other pos: OPAQUE | D: by site kind | push |
| SET s ← e | next | R | s (trailed) | kill s; gen s == t iff e is `slot[t]` | pass | continue iff non-effect (rev 1's rule) | DEAD, COPY, UNTRAIL | set |
| snapshot entry j of call c | next | none | trail only | none | pass | continue | V1 | set |
| restore of s at R_c (C-move) | next | trail | s | kill s | pass | continue | V2 | set |
| CUT mark | next | mark slot | frames discarded | unchanged | unchanged | OPAQUE | — | cut |
| CUT_LOCAL (revdet cut) | next | the frame-mark local | frames discarded | unchanged | unchanged | OPAQUE | — | note / none |
| CALL c (region g, return R_c) | callee entry | W(g) ∩ live-after(R_c) | — | none after | pass | continue into the callee | — | call |
| RETURN (region exit, a compound block) | every R_c of the region, exit (capacity guard) | live-in of every R_c | call_top | none at any R_c | pass | fork to every R_c | — | return |
| CHECKPOINT | next | — | trail only (compaction) | — | — | continue | — (carries a sid, never a verdict) | note |
| WORK (count) | next, exit (R_WORK) | R | work counter | — | — | continue | — | note |
| STEP (callout's step charge) | next, exit (R_STEPS) | — | steps counter | — | — | continue | — | none |
| CONSUME class / lit / wclass (forward, on `scan_position`) | target on match, else next | subject | cursor (forward) | — | — | F ∪= the first byte's class; stop | — | consume |
| CONSUME_BACK (revdet walk, on the walk cursor local) | target, next | subject, the local | the local | — | — | OPAQUE | — | consume |
| SPAN (group opener: first-byte class, min, stride, span id; compound with the kit advance) | next | subject | the span cursor local | — | — | F ∪= class; continue iff min = 0 (the zero-iteration path) | — | none |
| SEEK SPAN_COMMIT (span id) | next | the span local | cursor | — | — | continue (identity on the zero-iteration path) | — | none |
| SEEK RESTORE s / BACKSTEP k / ADVANCE k | next (BACKSTEP: + unwind via its BRANCH_FAIL) | R | cursor | — | — | OPAQUE | — | note / none |
| LSET x (15) | next | R | local x (untrailed) | — | — | continue iff non-effect (rev 1's rule) | never | none |
| BREF g.. (compound) | target, unwind | 2g, 2g+1 for each ref; work count | cursor (unknown amount) | — | — | OPAQUE | — | fail, note, fail, goto (legacy) |
| VAR v (compound) | target, unwind | caller variables (constant) | cursor (unknown amount) | — | — | OPAQUE | — | note, fail, goto (legacy) |
| CALLOUT site (compound) | target (succ), unwind (fail), exit (prop, give-up) | `slot_values[0 .. 2*ncap-1]` whatever `--no-captures` says, and the caller's vars `[r3 F8]` (the definition-site view's slots are a subset; read the whole range) | slot 0 transiently (saved and restored: net none); `run->callee_gave_up` on the give-up exit | kill all | pass | OPAQUE | — | callout, fail, goto (legacy) |
| ACCEPT | accept | slots `0 .. 2*NCAPS-1` (slot 0 carries `\K`) | — | — | — | F = all, E = true | — | accept |
| frame: DECL / ENTRY / ACCEPT_RETURN / UNWIND / TRACE | ENTRY: the attempt entry (L0); UNWIND: the PUSH edges | — | DECL: locals at entry | entry: no facts | entry: {} | — | — | none |
| NOTEMPTY_GUARD (the notempty copy's accept test) | accept, unwind | — | — | — | — | (F = all) | — | none |
| annotations: NOTE / RUNG / STRAT / PRUNE / ISLAND (group opener: island first-byte set, nullable flag) | (print nothing) | — | — | — | — | ISLAND: F ∪= its first-byte set; continue iff nullable | — | as today |
| UNMODELLED (any kind without columns) | — | — | — | — | — | — | — | **the function is V0: every verdict KEEP, D declines** |

**Three general rules the rows encode.**

1. **A guard is an edge, not a clause.** The skip edge makes every guarded statement
   conditional in every column at once. The guarded SET in r6's S-1 is a kill on its own path
   and a pass on the skip path, and the meet at the join gives a may-write. COPY's "gen" from a
   guarded SET does not survive the meet. Liveness keeps the slot live through the skip
   path. `[r6 S-1]`
2. **A path ends only where the text ends it.** FAIL is the unconditional `goto <p>_fail` and
   nothing else. Every conditional fail is BRANCH_FAIL, and compound consumes list both edges.
   The signature makes a mismatch V0. `[r6 S-2]`
3. **FIRST+ is position-blind only while the cursor has not moved.** It continues through
   statements that leave the cursor alone. It stops with a class at a forward consume, a SPAN
   or an ISLAND. It goes OPAQUE at every other cursor move: SEEK RESTORE (lookaround success,
   revdet lazy commit), BACKSTEP (lookbehind of width 2 or more), ADVANCE outside an island,
   BREF, VAR, CALLOUT and CONSUME_BACK. Width-1 lookbehinds emit a peek BRANCH and stay
   transparent, as r6 probed. `[r6 S-3, S-5]`

**FIRST+'s own column** (rev 1, unchanged): program altitude, follows calls, every cut
OPAQUE. It is the first-consumed-byte family's program-altitude member, beside START SET,
possessify `first_of`, the island's admission, the start table's `cand_rows[]` and
**[OPT-ALTCLS] stage-2 prefix factoring**, which is D2 at AST altitude restricted to a shared
literal first byte. ALTCLS runs first, so D sees factored alternations. `[r6 SEAM-G1]` The
PATH split (EFFECT / UNSEEN) stays filed `[r3 F19a]`.

**The non-effect rule** (rev 1, unchanged): a write before a dropped continuation's first
byte is a non-effect iff its variable is TRAILED, or the variable is dead at every resume label
its failure can reach. Otherwise the continuation is OPAQUE. D runs on walk 1, where every
slot write is trailed. The live clause binds locals (LSET), and card 0h measures what it
declines.

**D's admission table** (rev 1, unchanged; first match per choice point; reads PUSH's site-kind
enum, never role text `[r3 SLOTS-5]`):

| row | site kind | admit when | emit |
|---|---|---|---|
| D1 | flat alternation the island admits | the island's own rules | island trie (unchanged) |
| D2 | alternation chain, n >= 2 | some byte class drops a continuation | SWITCH to per-class chains, original order, a push only between candidates; every case goto through `vm_jump` (D183's cycle theorem) |
| D3 | optional, loop iteration (stage 2, FILED) | — | the stock chain |
| D4 | rung retreat, lookaround, possessive exit, anything else | — | the stock chain |

**The slot-flow verdict table** (per SET site, first match, decided in ROUNDS):

| row | site | verdict | round | emitted |
|---|---|---|---|---|
| V0 | the matcher function holds an UNMODELLED kind or a signature mismatch | KEEP (every site); D declines | — | `<P>_SET` |
| V1 | snapshot entry of s at call c | DELETE iff V2 deletes the restore of s at R_c; else KEEP. Never COPY, never UNTRAIL (positional storage). | A (with its restore) | nothing / `<P>_SET` |
| V2 | restore of s at R_c | DELETE iff s ∉ K_c = W(g) ∩ live-after(R_c); else KEEP. **A kept restore reads its snapshot at its ordinal among the KEPT entries of its own site.** `[r6 S-6]` | A | nothing / the restore |
| V3 | s is dead after the site | DELETE (DEAD) | A1 | nothing |
| V4 | s == source on every path (must) | DELETE (COPY) | A2 | nothing |
| V5 | s is dead at the attempt entry and at every L in MAYFRAMES(site) | UNTRAIL | B | `<P>_SETU` (a plain store) |
| V6 | otherwise | KEEP | — | `<P>_SET` |

- **K_c and W.** `vm_build_region_saves`' W is the AST-altitude upper bound; V2 narrows it per
  call site. A change to W's rule is reviewed against V1/V2. Both readers are named in the
  build's guide entry. `[r6 SEAM-G1]`
- **The S-6 codegen assertion.** At each call site, the list of snapshot SETs kept by V1 and
  the list of restores kept by V2 are the same slot sequence. Checked on walk 3's records.

**The rounds** (rev 1's order, now stated as what they are `[r6 SEAM-2]`). They run IN MEMORY
on walk 2's record list:

1. **Round A, repeated until nothing changes:**
   - A1: liveness, then every DEAD verdict (V2, V3, and V1 through V2) as tombstones;
   - A2: available copies on that list, then every COPY verdict as tombstones.
2. **Round B, once:** liveness and MAYFRAMES recomputed, then every UNTRAIL verdict as a retag.
3. **Nothing after round B** carries a fact across a resume edge (TRAIL-EQ-LIVE; rev 1's F4
   argument stands).

The invariant that makes the in-memory model faithful:

- a tombstone prints nothing and has no effect in any column;
- a SETU retag changes only "writes trail";
- CHECKPOINT records are slot-neutral, so whether walk 3 re-emits a checkpoint changes no
  column.

Measured on real programs, round A takes 2 productive iterations on `^(?:(?1)y)*(a|b)$` and 3 on
the possessive nest (r6's seam lens). Each productive iteration tombstones at least one record,
so the count is bounded by the SET records.

**C in the one table** (rev 1, unchanged): liveness uses the stock-restore model in every round
(every R_c kills all of W(g); the CALL reads W(g) ∩ live-after(R_c); snapshot entries read
nothing). That is one monotone pass, and K_c is read off it.

## Verdict identity across walks

**The walks** (rev 1, with the rounds moved in memory):

| walk | emits | read by | skipped when |
|---|---|---|---|
| 1 | the stock program (R and C-move rendering included) | D's FIRST+ (every slot write trailed: full TRAIL-EQ) | never |
| 2 | walk 1 with D's map | the slot-flow rounds, in memory | D found no site, or D is denied (walk 2 = walk 1) |
| 3 | walk 2 with the slot-flow map: the FINAL C, records and listing | every derived fact | no verdict, or the lever is on (walk 3 = walk 2) |

At most three emissions per VM artifact. The rounds cost analysis time, not emissions. Card 0i
measures the emission share of compile time.

**The statement identity** `[r6 S-4, SEAM-1]`:
`sid = (node, instance, line, k)`, where:

- `node` is the emitting AST node's pre-order index;
- `instance` counts how many times that node's emission has begun in this walk: replicas,
  region against lexical copies, splice instances and lookbehind branches each get their own;
- `line` is `__LINE__` of the `vm_stmt` call site, passed by the `VM_STMT` macro. It is
  stable within one compiler binary, which is the only scope a verdict map lives in;
- `k` counts earlier records with the same (node, instance, line), so loops at one call site
  (the cursor rung's capture SETs) stay distinct.

Why it survives the walks:

- **Walk 1 to walk 2.** D changes only the statements of the choice point it dispatches. They
  are emitted by D's own call sites (new lines), and the arm bodies are emitted once each as
  before. So every node's emission count and order are unchanged. D's own map is keyed by the
  A_ALT node's (node, instance).
- **Walk 2 to walk 3.** The primitive assigns the sid BEFORE it consults the map, so a DELETE
  consumes its id and leaves a tombstone record. A vanished checkpoint has a sid that no verdict
  names, and nothing is an ordinal, so nothing shifts.

**What the final walk owns** (rev 1, corrected `[r6 SEAM-4]`):

- **The push-site total** (`[abd]x|[acd]y|[bcd]z`: 5 sites against stock's 2). "The
  resume-point cap" is STRUCK: no such cap exists (`PCREC_MAX_VM_RESUME_POINTS` is defined
  nowhere, and `src/core/limits.h:196-203` records it as a rejected draft).
- **The listing's `resume-points` row** stays the PRE-PASS count (`npush`), its meaning
  unchanged. run_ir_listing.sh's `pre-pass >= emitted` assertion reads the push count of the
  D-denied compile (`-fno-<dispatch>`). Verdicts never add or remove a PUSH, so that count is
  walk 1's. The extra compile happens only where the default listing shows dispatch sites.
  S305 stays DETECTED through the same assertion.
- **Checkpoint placement and the D183 margin** follow walk 3's `nset` (KEEP sites only) with
  no second mechanism (D183 addendum `[r3 F18a]`).
- **FRAMELESS, ENTRY_SHAPE, the entry rung and `vm_reseed_cal[has_push]`.** The last flips
  when D makes a program frameless, and [OPT-HYB-RESEED]'s calibration check reads it.
- **The stamps, `RX_VM_PROGRAM_BYTES`, the listing and the notempty copy.**
- **Capacities keep the AST pre-pass in this build.** That is the safe over-charge; stamp
  shrink is filed `[r3 F7]`.

**The checks** (stage (c)'s gate 2a; the levers are test-only):

| check | what it asserts | can it fail on a keying slip? |
|---|---|---|
| K1 all-KEEP | walk 3 with an all-KEEP map (`--harness=keep-slot-writes`) and walk 2 with an empty D map (`-fno-<dispatch>`) emit byte-identical C and records to their input walk | no (necessary only) |
| K2 one-entry maps | for the corpus' first N VM artifacts and every SET site k (capped per artifact), `--harness=verdicts=FILE` with `{k: DELETE}` (and, for a site under a SPAN or GUARD, `{k: UNTRAIL}`) changes EXACTLY the line(s) of record k in the C and its record's op in the listing. With `--harness=stmt-records` every record carries its sid, so the diff is located by sid, not by position. | yes |
| K3 cross-walk sids | every walk-3 record's sid exists in walk 2 with the same kind and operands. The only differences: tombstones where the map says DELETE, retags where it says UNTRAIL, and CHECKPOINT records free to vanish. The rounds' final in-memory list re-rendered equals walk 3's records modulo checkpoints (SEAM-2's invariant). | yes |

**Sabotages** (mech rows, each with a named cell):

- **SAB-ORD:** rev 1's keying, the ordinal of the event in the deciding walk.
  - K2a: `^(?:(?1)y)*(a|b)$` with `--features all --engine=vm -fno-splice-calls`. The `rx_L7`
    checkpoint exists only because of the snapshot SETs that V1/V2 delete, so walk 3 drops it
    and every later ordinal shifts by one. K2 and K3 red.
  - Stock answers on `a ayb aybyb ayayb` are 1:0,1 / 1:2,3 / 1:4,5 / 1:4,5, equal to
    libpcre2's (`cells.log`).
- **SAB-SKIP:** a DELETE does not advance `k`.
  - K2b: `^(?:(a)(b))*c$` with `--features all --engine=vm` (a cursor rung with two capture
    groups: four SETs from two call sites inside one loop, reach checked).
  - `{(group 1 close): DELETE}` must change only that line. Under the sabotage, the next
    SET's k shifts. K2 red.

## Gates and STEP 0

**G1, restated** `[r6 SEAM-5, SEAM-6]`:

- Answers are identical to stock wherever stock answers, captures included.
- **Never a new give-up** at the stamped capacities, nor at any `ntrail` at or above the plain
  trail's need. Inside D183's gap band, a give-up at a given `ntrail` may move, in both
  directions, as limits §4 paragraph 3 already allows between capacities.
- Where stock gives up (FRAMES, WORK, STEPS), the build may answer, and that answer is
  libpcre2's (one-way toward answers; limits §1, §7). Left recursion may move from FRAMES to an
  answer inside pattern_language §9 paragraph 4a.

**The other goals** (rev 1, unchanged; ranked):

- **G2:** the recursive and scanner members' instructions per call at or below pcre2-jit's;
  cycles confirmed at landing under the quiet gate.
- **G3:** flat VM patterns, led by the backreference family.
- **G4:** default-arm depth at or above jit's on nest-brace (176) and JSON (150).
- **G5:** storage for one-shot callers.
- **Non-goals** as rev 1: default capacities and stamp shrink; comment-5m below jit; D stage
  2; packed entries and narrow frames; the DFA route, the island's own rows, the kit.

**EXPECTED-MOVES.** One committed list, `tests/vm/expected_moves.tsv`. Each row holds:
cell (`file:line`), flags, stock give-up kind, build answer, libpcre2 answer, the stage that
moves it, and the reason. It starts with:

- `tests/recursion/framebuffer.rxt` cell 1 (the `gu frames` at n = 764, lines 35-41;
  `[r6 SEAM-5b]`);
- `tests/recursion/d27/sr_depth.rxt:58-59` (len 1528 and 2000);
- W6's four left-recursion cells;
- every cell STEP 0's 0a finds moving.

Every row is checked against libpcre2 like card 0e. A moved cell NOT on the list is red; a
listed cell that does not move is red too (the list is a manifest, never a count).

**The stage gates, restated:**

- "corpus answers equal `-fno-<dispatch>`" (stage 2b) and "equal `--harness=keep-slot-writes`"
  (2d/2e) read **equal, except the EXPECTED-MOVES cells**.
- `tests/axes/run_axes.sh` gets one `GIVEUP1_ALLOWANCE` row per moved cell per arm: the deny
  flag's arm, and the internal arm `INTERNAL_ARMS` sweeps.
- The existing `-fno-req-byte|tests/recursion/d27/sr_depth.rxt:*` rows are re-triaged once the
  default's answers move. `[r6 SEAM-5c]`

**Stage gates by landing:**

| landing | gate |
|---|---|
| (a) printing is recording | the two-compiler identity diff over the corpus (C and listing byte-identical); `run_stmt_writer.sh` green with sabotages (i)-(iii) detected; card 0m (census: 0 mismatches, 0 V0); `run_recursion_identity.sh` unchanged (FILEPIN unmoved) |
| (b) R | answer identity on the corpus; the R guard over the PREPROCESSED matcher (`gcc -E`, the matcher function cut out after expansion, so the seven `RX_*` macro bodies are read): no `run->(resume_depth\|trail_depth\|call_top\|steps_left\|work_left)` outside the write-back and reload brackets; sabotages W3, the steps_left write-back, the compaction reload, and **SAB-MACRO: `RX_TRAIL` left on `run->trail_depth`** `[r6 S-8]` |
| (c) 2a walks, no verdicts | K1 byte identity; K2, K3 with SAB-ORD and SAB-SKIP detected |
| (c) 2b D stage 1 | corpus answers equal `-fno-<dispatch>` except EXPECTED-MOVES; W6 moves; W7a, W7b; W10-W13, W17; cells C2b, C2c, C3a, C3b, C5a, C5b; the size rung |
| (c) 2c C-move | identity; K36's witnesses |
| (c) 2d round A | corpus answers equal `--harness=keep-slot-writes` except EXPECTED-MOVES; W2, W8, W18; C1, C2a, C6 with the S-6 assertion |
| (c) 2e round B | as 2d; W14-W16; W4's sabotage row (REACH gap noted) |

**A D27 spec-first author** for (c), briefed with G1 as restated and the give-up direction (r6
recommendation).

**STEP 0.** ONE job before (c)'s build go, AFTER (a) lands. It is queued by the manager
outside 19:00-00:00, heavy (over 50 compiles), on the prototypes in walk order (D first).
`$E` = `docs/dev/lanes/vmcons_evidence` (rev 1's scripts), `$E2` = `docs/dev/lanes/vmcons2_evidence`,
`$S` = the STEP 0 lane's scratch, `$PC` = the (a) build's `build/pcrec`.

| # | card | command | gate / output |
|---|---|---|---|
| 0a | corpus twin identity, full stack | `scripts/boxlock run --label vmcons-step0-ident -- env CC=$S/ccwrap.sh VMCONS_CHAIN="altd:ALkf vmopt_tg:BCdU variants:R" PCREC=$PC bash tests/harness/run.sh` (every `.rxt`); again with `RXTFLAGS="-fno-splice-calls --engine=vm"` | 0 failed, **except the EXPECTED-MOVES cells**, each libpcre2-checked; a moved cell not listed is a design defect: stop and report `[r6 SEAM-5a]` |
| 0b | census, one pass | rev 1's 0b (merged `census.py`, all 79 bench texts, `-e utf8` where labelled) | as rev 1, plus V0 functions by cause (UNMODELLED kind or signature mismatch) |
| 0c | gap cycles and ablations | rev 1's 0c, in a bench quiet-gate window | G2 in cycles; D stage 2's trigger |
| 0d | R at -O3 and on the default arm | rev 1's 0d | `[r3 F26]` |
| 0e | give-up-to-answer cells against libpcre2 | rev 1's 0e | every answer equals libpcre2's; the list feeds EXPECTED-MOVES |
| 0f | sabotage table on the prototypes | rev 1's 0f, plus the r6 rows (no skip edge, VAR fail unconditional, SEEK transparent, SPAN contributes nothing, original-ordinal restore) on cells C1-C6 | every row DETECTED |
| 0g | U through the recursion harness | rev 1's 0g | 0 failed |
| 0h | locals under D's non-effect rule | rev 1's 0h | the sites the exact rule declines |
| 0i | emission share of compile time | rev 1's 0i | the walks' bound is 3x the emission share; the rounds' analysis time is reported separately |
| 0j | S180 witness | rev 1's 0j | `[r3 F9]` |
| 0k | trail give-up monotonicity | the full twin against stock, `_search_in` at ntrail 1..600, on `^(\((?:[^()]\|(?1))*\))$`, the possessive nest `^(\((?:[^()]++\|(?1))*+\))$` (atomic-groups), and one shape whose kept set oscillates (cold call sites whose snapshots V1/V2 empty) | report every cell where stock answers and the twin gives up: inside the gap band, a DOC row; at or above the plain trail's need, a design defect `[r6 SEAM-6]` |
| 0l | drop-dispatch rung position | on 0b's near-cap VM artifacts: size and instructions for D-off against unroll-K-down, handoff-off and prefilter-off | the measured order for `fit_rungs[]` (limits §8.4¶2 cheapest-first; D77) `[r6 SEAM-7]` |
| 0m | statement census | `scripts/boxlock run --label vmcons-step0-census2 -- bash $E2/stmt_census.sh` (to be written with (a): every corpus pattern through `build/pcrec-harness --harness=stmt-records`) | 0 mismatches, 0 V0 over the corpus (r6 recommendation 2) |
| 0n | record/text agreement | the prototypes' graph builder ported to read (a)'s RECORDS (`--harness=stmt-records`) instead of the text, then the full rule set run both ways over the corpus | every verdict and every D admission identical in both; a disagreement is an input gap in the records: stop and report. It is the evidence r6 said the text-only identity runs are not (`[r6 S-7]`'s note on the prototypes). |

Missing glue, written in STEP 0's lane, scratch only: rev 1's list, plus the record reader
(0n), the r6 sabotage flags (0f) and the ntrail driver (0k).

## Test cells

Every cell is an `.rxt` line in the build's own corpus file (`tests/vm/opt_witness.rxt`, new
in (c)), run by `bash tests/harness/run.sh tests/vm/opt_witness.rxt`. Its sabotage row runs as
`bash tests/mech/run_sabotage_matrix.sh S<id>` with ids from the range the brief of (c) names.
Expected answers below are stock's at the base, checked equal to libpcre2's in
`vmcons2_evidence/cells.log`. Run `S=<scratch> PCREC=<base pcrec> bash
docs/dev/lanes/vmcons2_evidence/cells.sh`, which needs `drv.c`, `drvv.c` and `p2.c` in `$S/w`.

**New in rev 2 (review r6):**

| cell | rule row guarded | pattern, flags, subject | expected (stock = libpcre2) | sabotage that must turn it red |
|---|---|---|---|---|
| C1 | GUARD skip edge `[r6 S-1]` | `^(?:(?:(a)b)*c){2}$`, `--features all`, `abcc` / `ababcc` / `abcabc` / `cc` | 1:0,1 / 1:2,3 / 1:3,4 / 1:-1,-1 | GUARD without the skip edge (V3 deletes L8's SETs: twin 1:-1,-1) |
| C2a | VAR row, conditional fail `[r6 S-2]` | `^(a)${v}c`, `--features all`, v = `b`, `abc` | 0:0,3 1:0,1 (premise twin: 1:-1,-1) | VAR's fail edge unconditional (rev 1's FAIL row) |
| C2b | VAR is FIRST+ OPAQUE (D) | `^(?:${v}x\|by)z`, v = `a`: `axz`, `byz`, `bxz` | match 0,3 / match 0,3 / nomatch | VAR's FIRST+ "nothing" (D drops arm 1) |
| C2c | same, other binding | `^(?:${v}x\|by)z`, v = `b`: `bxz`, `byz`, `axz` | match 0,3 / match 0,3 / nomatch | as C2b |
| C3a | BACKSTEP is OPAQUE `[r6 S-3]` | `^x(?:a\|(?<=x\|yz))w`, `--features all`, `xw` / `xaw` / `xxw` / `yzw` | 0,2 / 0,3 / nomatch / nomatch | SEEK BACKSTEP "continue" in FIRST+ |
| C3b | RESTORE is OPAQUE | `^(*napla:x(?:a\|))xb`, `--features all`, `xb` / `xab` | 0,2 / nomatch | SEEK RESTORE "continue" |
| C5a | SPAN contributes its class `[r6 S-5]` | `^(?:[ab]+b\|y)(z)`, `--features all`, `abz` / `aabz` / `bbz` / `yz` | 0:0,3 1:2,3 / 0:0,4 1:3,4 / 0:0,3 1:2,3 / 0:0,2 1:1,2 | SPAN row contributes nothing |
| C5b | lazy SPAN | `^(?:.*?x\|y)(z)`, `--features all`, `axz` / `aaxz` / `xz` / `yz` | 0:0,3 1:2,3 / 0:0,4 1:3,4 / 0:0,2 1:1,2 / 0:0,2 1:1,2 | as C5a |
| C6 | kept-ordinal restore `[r6 S-6]` | `^(x(?>a(?1)?b)y)$`, `--features all --engine=vm -fno-splice-calls`, `xaby` / `xaxabyby` / `xaxaxabybyby` / `xay` / `xaxaby` | 1:0,4 / 1:0,8 / 1:0,12 / nomatch / nomatch | restores keep ORIGINAL ordinals (r6 twin: 1:-1,8 and 1:2,12); the S-6 codegen assertion must fire too |
| K2a | sid survives a vanished checkpoint `[r6 SEAM-1]` | `^(?:(?1)y)*(a\|b)$`, `--features all --engine=vm -fno-splice-calls`, `a` / `ayb` / `aybyb` / `ayayb` | 1:0,1 / 1:2,3 / 1:4,5 / 1:4,5 | SAB-ORD: K2/K3 red (the cell answers stay as a control) |
| K2b | sid survives a DELETE in a loop | `^(?:(a)(b))*c$`, `--features all --engine=vm`, `c` / `abc` / `ababc` | 1,2 unset / 1:0,1 2:1,2 / 1:2,3 2:3,4 | SAB-SKIP: K2 red |
| RM | R reads macro bodies `[r6 S-8]` | any linked-call artifact, e.g. `^(a(?1)?b)$` `--engine=vm -fno-splice-calls` | the preprocessed guard | SAB-MACRO: `RX_TRAIL` left on `run->trail_depth` |
| ST-i..iii | one writer `[r6 S-7, SEAM-3]` | no pattern: source and corpus | `run_stmt_writer.sh` green; census 0 | sabotages (i) getter + raw print, (ii) mistyped kind, (iii) raw read text |

**Carried from rev 1** (commands and base answers in rev 1's table and its `witness.log`):

| cell | rule | pattern, flags, subject | base |
|---|---|---|---|
| W1 | slot reads | `^(?:(?:[bB]\|[cC]d)(\w))+by$`, `bxby` / `bxcdzby` / `BqBqby` | 1:1,2 / 1:4,5 / 1:3,4 |
| W2 | CALL reads W ∩ live-after | `^(b)(?1)`, `--engine=vm -fno-splice-calls`, `bb` | 0:0,2 1:0,1 |
| W3 | R covers value text | `^(?:(?>ab\|a)c\|abd)`, `--engine=vm`, `abd` | 0,3 |
| W4 | round order | no producer today | REACH gap |
| W5 | V0 refuses the function | a planted UNMODELLED kind before a dispatched arm | (now also ST-ii) |
| W6 | D on left recursion | `(?:a\|(?R))+` on `b`, `ab`, `ba`; `^(a\|(?1)b)` on `x`, `b` | FRAMES; must MOVE (EXPECTED-MOVES) |
| W7a | FRAMELESS iff | `a(?:\dx\|[a-z]y)c`, `--engine=vm` | FRAMELESS 1 after D |
| W7b | push total from the final walk | `[abd]x\|[acd]y\|[bcd]z`, `--engine=vm` | 5 sites; `resume-points` stays the pre-pass 2; the D-denied compile has 2 pushes (SEAM-4) |
| W8 | callout ncap | `(a)(?:(b)\|c)(?C\`c: return RX_CAP_SET(2) ? RX_FAIL : RX_PASS;\`)d`, `--allow-code=c --no-captures`, `abd` / `acd` | nomatch / match |
| W9 | S180 detector | 0j | — |
| W10-W13, W17 | D commit opacity, lookaround cut, order, nullable arms, callout/caseless/UTF-8 | rev 1's patterns | stock |
| W14-W16 | U: live counter, entry liveness, MAYFRAMES | `(?:a\|ab){300}+c`; `a\|(b)c` on `bxa`; `(ab\|a)+ab` on `aaba` | stock |
| W18 | VB's B/C witnesses | rev 1's four patterns | stock |

## Cost

**(a) printing is recording**: size M, one lane, refactor class.

| item | sites |
|---|---|
| new `src/gen/vm_stmt.c` + private header | the primitive, the kind table (about 35 rows x 9 columns), sid assignment, the signature counter, the fragment buffer, the frame writers, the two post-passes, `vm_note`; about 300-400 lines |
| `emit_vm.c` walk prints rewritten as `VM_STMT` calls | 132 calls, 91 statement sites, in 32 functions |
| `vm_ev` calls folded or turned into `vm_note` | 54 |
| raw `slot_values[` formats moved onto `vm_slot_read`, plus `vm_slot_ref`/`vm_slot_expr` callers | 31 + 10 |
| C-text `vm_rolef` fragments audited (gotos, reads, cursor expressions) | 22 |
| frame prints moved into `vm_stmt.c` | 23 |
| delegated-writer calls given the fragment buffer | 4 |
| harness option `--harness=stmt-records` | one bitfield, one CLI arm, the lever-fence allowlist |
| checks | `run_stmt_writer.sh` + 3 sabotages; the census script (0m) |
| docs | `src/gen/CLAUDE.md` (the new file), the guide's emission-primitive entry, D-number for printing-is-recording, `ir_listing.md` unchanged (listing identical) |

- **Risk: low.** It is mechanical, and byte identity over the corpus is the gate, so a slip
  shows as a diff before landing.
- **Calibration.** D183's +213 source lines / +861 test and spec lines suggest roughly
  +450/-250 in `src/gen` and +300 in tests and docs.
- **Compile-time cost.** Records stay the same order as today's events (the census: 1,223
  body lines against 1,389 events over 24 artifacts). The signature count is a handful of `strstr`
  calls per statement, nothing beside the gcc step. Card 0i measures it in passing.

**(b) R**: size S-M, one lane, abi event 1 (every VM artifact's matcher text moves).

- R becomes cheaper on top of (a): every cursor access is already a typed record (CUT_LOCAL,
  STEP, WORK, frame UNWIND), so R's change list is the rows whose text reads `run->`.
- Obligations as rev 1's landing 1: mover census, limits §5 stack numbers re-measured,
  match_api §10.9¶10 if it moves, the bench null band spent once.

**(c) the analysis build**: size L, two to three lanes (rev 1's landing 2). Additions in rev
2:

- the listing hunk: full records with sids and the new ops, ir_listing §3.2 and §3.4, the
  header sentence becoming true;
- K2, K3 and their levers;
- EXPECTED-MOVES and the GIVEUP1 rows;
- the drop-dispatch rung at 0l's measured position, with its census: `COMPILE_MAX_ATTEMPTS`
  and `fit_tables_selfcheck`, limits §8.4¶3's count, §8.5's stamp and note rows,
  `--size-cap=refuse`, the `src/core/axes.def` row `[r6 SEAM-7]`;
- the SEAM-4 readers;
- framebuffer.rxt cell 1.

The rest of rev 1's landing-2 obligations stand:

- the one spec pass: limits §4, §5¶6, §6, §7, §8.4/§8.5; match_api §6.3.8¶10-12, §10.1¶1,
  §10.2¶4, §10.6¶2-3; tuning §2.11¶2, §2.20, §2.21¶3 and a D section; ir_listing §3.1;
  pattern_language §9 paragraph 4a;
- the named readers: S179, S180, `run_frame_buffer.sh`, `fb_mmap_driver.c`, framebuffer.rxt
  cells 1-4, `fb_exact_driver.c`, `sr_depth`, `ts4`, `rx_info`, and the bench
  `program_sha256` null band;
- the D183 addendum;
- [ART-TRAIL-ELIDE] closed in;
- [ENG-ISL-S2] conditional on 0b;
- `tests/vm/vmgraph.py` as the one text-graph module, now with a record reader beside it
  (0n).

**Flags** (Frank's F11 ruling, R1):

| change | public flag | test lever | stamp |
|---|---|---|---|
| (a) printing is recording | none | `--harness=stmt-records` (diagnostic only) | none |
| (b) R | none | none | none; proven by identity and the preprocessed guard |
| C-move | none | none | none; identity and K36's witnesses |
| D | ONE deny flag (working name `-fno-first-byte-dispatch`, final spelling per D174); never a force (unsound) | — | `<PREFIX>_VM_DISPATCH_SITES`, registry shape of the activity-count stamps `[r6 SEAM-G1]` |
| slot-flow verdicts | none | `--harness=keep-slot-writes` (all-KEEP; `INTERNAL_ARMS`) and `--harness=verdicts=FILE` (K2's one-entry maps; the `--harness=measures=FILE` precedent) | listing ops and a verdict-count row |

Flag bits: D's deny takes one. 5 remain with the filed bit-57 candidate, 6 without it. The
[IFACE-PUSH] hard trigger (<= 4) is not reached.

**Filed, not built** (D77 triggers):

- D stage 2 (0c);
- stamped capacity shrink (SEAM-G2a);
- per-cycle margins (G2b; trigger: an `_in` caller at small `ntrail` binding on the margin);
- a generic "drop verdict class X" rung (G2c; trigger: a second growing pass);
- a static measured-admission input (G2d; trigger: a 0c cell where FIRST+ admits a slower
  dispatch);
- AD's unlocks, F20(b)/(d)/(e), F19(a), TG's packed entries.

**Questions for Frank**:

1. **How many landings?** (a) must land alone: it is the only stage provable by plain byte
   identity, and every later proof reads its records.
   - The question left is whether R (b) and the analysis build (c) land separately.
   - Forces are as in rev 1: two version bumps and the bench's "same program" noise band spent
     twice, against one large merge.
   - Leaning: separate, for the same reason as rev 1, and because (b) is now small.
2. **Build only the alternation half of the dispatch (stage 1) now?** Unchanged from rev 1;
   leaning yes.
3. **Rev 1's walks-versus-in-memory question** is no longer a question.
   - The verdict rounds are in memory by the faithfulness invariant (SEAM-2).
   - D stays a real emission because it adds statements.
   - The answers are identical either way, so per memory `pcrec-answer-free-choices-are-mine`
     it is the manager's call, not Frank's.

**Measurements carried** (rev 1, instructions per call; not re-run here):

- The full stack R+B+C+U+D gives:
  - nest-paren 3.87 against jit 10.35;
  - nest-brace 15.31 against 50.40;
  - js 38.43 against 58.58;
  - idents 53.78 against 82.09;
  - splice 18.42 against 23.66;
  - comment-5m 101.96 against 86.50.
- D stage 1 depths are 1022 and 340. C ablated, the depth falls to 119 and 21.
- These came from TEXT prototypes. As r6 noted, their identity runs are not evidence for the
  record-based build, and card 0n closes that gap.

**Standing questions (docs/design/CLAUDE.md).**

1. **Measurement regime: relevant.** It is rev 1's: warm, resident, the 7700X, gcc 15.2 -O2,
   instructions; cycles in 0c under the quiet gate. This lane measured no rate.
2. **Independent control: relevant.** Stock-vs-build answers, the oracle `.rxt` expectations
   and libpcre2 for moved give-ups, as in rev 1. NEW: card 0n's text-vs-record agreement is a
   second implementation over a DIFFERENT input, and the D27 author for (c) is the control that
   does not share the author's alphabet.
3. **What moves on regeneration: relevant.**
   - (a): nothing. The C artifact and the listing are byte-identical, and the FILEPIN is
     unmoved.
   - (b): every VM artifact's matcher text.
   - (c): rev 1's landing-2 list plus the listing's full-record hunk.

## STATE AT HANDOFF

- STATE: complete (design and measurement, as briefed; no build).
- Rulings file `docs/dev/lanes/vmcons2_rulings.md`: empty when read before each commit and
  before this report. Last entry applied: none.
- Premise test: CONFIRMED. S-2's witness under rev 1's rule as written moves group 1 from 0,1
  to -1,-1; stock and libpcre2 give 0,1 (`premise.log`).
- STOP RULE: not triggered. Routing every printed statement through one primitive is
  feasible and byte-identical (Printing is recording, "Feasibility").
- OWED: none. STEP 0 is the build's pre-go job after (a) lands. Its cards 0m and 0n need
  (a)'s records, so they cannot run before then.
- Box use, all single-process and all ended by 14:30, nowhere near the 19:00-00:00 window:
  - one scratch build of lane/trailgc;
  - 48 census compiles;
  - 11 witness cells (11 compiles, 11 gcc builds, libpcre2 runs);
  - the premise twin.
- Evidence (`docs/dev/lanes/vmcons2_evidence/`):
  - `premise.sh`, `premise.log`;
  - `cells.sh`, `cells.log`;
  - `sites.py`, `calls.py`, `body_print_sites.tsv` (the 132 calls);
  - `site_kinds.tsv` (each call's rev 2 kind and today's status);
  - `census.py`, `census_pats.tsv`, `census.tsv`.
- Scratch: `/var/tmp/pcrec-pcrec/scratch/vmcons2/` (the base build, the merged emitter text,
  artifacts).
- Next: a short re-check of this document. Per the r6 rulings that is the soundness lens with
  its print-site enumeration, plus fix-induced. The build go for (a) follows only from it.
