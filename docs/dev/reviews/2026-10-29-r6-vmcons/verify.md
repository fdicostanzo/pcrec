# Verifier `verify` — critic round vmcons (design re-review), 2026-10-29

Scope: re-check of the CONFIRMED findings in soundness/findings.md and seam/findings.md. Subject read
only from subject_vmcons_report.md (snapshot of bf9a5bb8d). Base compiler B =
worktrees/crit-vmcons/build/pcrec (06aa5ab87). All my artifacts: verify/w/. My own copies of the
critics' drivers (drv.c, drvv.c, reviewed) and libpcre2 oracle p2.c (reviewed; compiled by me,
`gcc -O1 p2.c -lpcre2-8`). Generated matchers built with `verify/bld.sh` (gcc -O1, `-include` the
artifact header) and run under `scripts/watchdog -s 20 -m 1g`. Every twin below was made by ME by
applying the edit to MY OWN re-emission, then compared to the critic's diff. No make, no suite, no
denied file opened. SEAM-6 and S-4 skipped (SUSPECTED, per brief).

## S-1

**Verdict: HOLDS.**

- Re-emitted: `$B -p rx --features all --engine=vm -o w/s1.c --pattern '^(?:(?:(a)b)*c){2}$'`;
  `diff` against soundness/w/s1.c and s1.h: identical. Default flags (no `--engine`) also emit
  `RX_ENGINE "vm"` (w/s1d.c:20), so the witness is on the default VM route.
- Base text (w/s1.c:252-257 and :286-290): both cursor rungs print
  `if ((ptrdiff_t)rx_span_cursor >= slot_values[N] + 2) { RX_SET(G1_START..); RX_SET(G1_END..); }`.
  The `--emit-ir` listing records L8 and L13 as `push` then two unconditional `set` rows, no branch.
  emitter sites confirmed: src/gen/emit_vm.c:5044, :5195 (span rung guards), :5854, :5934,
  :5941, :5953 (revdet guards) are all `if (...) {` printfs, none a `goto`.
- Rule as written: Stage -1's VE_BRANCH is recorded by `vm_jump` for "every conditional
  `goto <p>_L`"; these guards contain no goto, so nothing records them; the completeness check
  counts `slot_values[` reads, `goto <p>_L`, `_PUSH(`, `_CUT(`/`resume_depth =`, `return` — none
  counts an `if (` opener. So the analysis sees L13's SETs as the SET row's "kill s"; after L8's
  SETs every path (L7, L5, L11, L13; and the L14 resume path back into L13) reaches L13's kill
  before ACCEPT reads slots 2,3, so V3 DELETEs both L8 SETs. I re-derived this independently; it
  is the reading a Stage -1-literal builder takes. A builder who treats the `if` as an implicit
  branch would be safe, but the text gives no such instruction (it names `goto` explicitly).
- Twin: `sed '255,256d' w/s1.c > w/s1t.c` — the same two-line deletion as the critic's
  s1t.diff (the critic left a comment line; otherwise identical).
- Run (base w/s1b, twin w/s1tw, libpcre2 p2), subjects abcc ababcc abcabc cc abcababc:
  - `abcc`: base 1:0,1 / twin 1:-1,-1 / libpcre2 1:0,1
  - `ababcc`: base 1:2,3 / twin 1:-1,-1 / libpcre2 1:2,3
  - `abcabc` 1:3,4, `cc` 1:-1,-1, `abcababc` 1:5,6: all three agree; group 0 spans agree everywhere.
- Gate claim: plausible, not re-swept (I did not redo the 6,245-pattern scan). A simple grep of
  tests/**/*.rxt for a `)*...){n>=2}` shape returned nothing. Magnitude as stated by the critic
  (answer, DOC) is right; the scope is every guarded write the analysis models as a must-write.

## S-2

**Verdict: HOLDS** (both witnesses).

- Re-emitted: `$B -p rx --features vars -o w/v1.c --pattern '^(a)${v}c'` and
  `... -o w/v2.c --pattern '^(?:${v}x|by)z'`. Against the critic's soundness/w/v1.c, v2.c (and .h)
  the only difference is `RX_ENGINE_SEL "selected"` vs `"forced"` (the critic added
  `--engine=vm`); the matcher text is identical, and the default route is VM (`RX_ENGINE "vm"`).
- Base emitter confirmed: `vm_var` (src/gen/emit_vm.c:8896-8941) prints
  `if (took < 0) goto <p>_fail; scan_position += took; goto <p>_L<next>;` and records only
  `vm_ev(VE_FAIL)` then `vm_ev(VE_GOTO, next)` (:8938-8939), plus the work note from
  `vm_work_at`. The listing shows `L3 label / note / fail / goto L6` (and `L4 ... fail / goto L7`
  for witness B).
- Rule as written: the FAIL row's successors are "the unwind (modelled by the PUSH edges)" and
  its FIRST+ is "nothing"; Stage -1 adds VE_BREF for `vm_bref` but no event for the variable
  compare; the completeness check counts `goto <p>_L` (1 = the one GOTO event) and does not count
  `goto <p>_fail`, so it is green. Hence (A) after L2/L5's SETs the only path ends at FAIL: V3
  DELETEs both; (B) FIRST+(arm 1) = {} (E false), FIRST+(arm 2) = {b}; D2 admits ("some byte class
  drops a continuation") and emits `switch: 'b' -> L5, default fail`. I derived both
  independently; they match the critic's diffs. No other reading of the text as written routes
  the variable's success edge; a builder would have to invent a row.
- Twins (mine): `sed '231d;225d' v1.c > v1t.c`; v2t.c replaces L2's `RX_PUSH(&&rx_L6..); goto rx_L4;`
  with `if (scan_position < subject_length) switch (subject[scan_position]) { case 98: goto rx_L5; default: break; } goto rx_fail;`.
  Same edits as soundness/w/v1t.diff, v2t.diff (comment lines aside). Built with drvv.c (var v from env V).
- Observed (base / twin / libpcre2 with the quotemeta splice):
  - A, v="b": `abc` 1:0,1 / **1:-1,-1** / 1:0,1; `ac` nomatch in all three.
  - B, v="a": `axz` match 0,3 / **nomatch** / match 0,3; `bxz` nomatch all; `byz` 0,3 all.
  - B, v="b": `bxz` match 0,3 / **nomatch** / match 0,3; `axz` nomatch all; `byz` 0,3 all.
- Gate claim spot-checked: tests/vars/basic.rxt:62 `^(${a}|${b})$` exists, emits on the VM route
  by default with one push; under the rule both arms have F = {} so D2's switch fails `cat`/`dog`
  — stage 2b would go red. The V3 form has no corpus cell by my grep either. Critic's scope and
  severity stand; I did not verify the CALLOUT aside (not claimed CONFIRMED).

## S-3

**Verdict: HOLDS** under the reading the design evidently intends (NOTE = no effect, ASSERT =
BRANCH); see the reading note below, which applies to S-1, S-2 and S-5 too.

- Re-emitted with `--features all` (lookaround is not in the default feature set; the critic's
  "default flags" means default engine choice with `--features all` — its artifacts stamp
  `PCREC_FEATURE_SET "all"`): `$B -p rx --features all -o w/lb2.c --pattern '^x(?:a|(?<=x|yz))w'`
  and `... -o w/na.c --pattern '^(*napla:x(?:a|))xb'`. Both identical (.c and .h) to the
  critic's soundness/w/lb2.*, na.*. Route: VM (`RX_ENGINE "vm"`, selected).
- Base text confirmed (w/lb2.c): the width-2 lookbehind branch is
  `scan_position = rx_back_step(subject, subject_length, scan_position, 2);` (listing: `note`)
  followed by FORWARD `consume 'y'`, `consume 'z'`; the width-1 branch the same with 'x'; the
  success path restores `scan_position = (size_t)slot_values[RX_SLOT_LOOK_POS0]` (listing:
  `note`) after the CUT. In w/na.c the napla's empty arm reaches L4's
  `scan_position = (size_t)slot_values[RX_SLOT_LOOK_POS0]` with no CUT, then `consume 'x'`.
  The design's CLASSB row ("the backward consuming test (lookbehind)") is indeed not the base's
  lookbehind shape.
- Rule derivation (mine): lb2 arm 2 = SET, SET (trailed: non-effect), GOTO, ASSERT (fork),
  PUSH L12 (fork), back-step NOTEs, CLASS 'x' / via L12 CLASS 'y': F = {x, y}; arm 1 F = {a};
  D2 admits on 'w'. na arm 2 = GOTO, the restore NOTE, CLASS 'x': F = {x}; arm 1 F = {a}. Same
  as the critic's diffs.
- Twins (mine, same edits as lb2t.diff / nat.diff): L3's / L6's `RX_PUSH; goto` replaced by
  the per-byte switch with default fail.
- Observed (base / twin / libpcre2):
  - lb2: `xw` match 0,2 / **nomatch** / match 0,2; `xaw` 0,3 all; `xxw`, `yzw`, `xyzw` nomatch all.
  - na: `xb` match 0,2 / **nomatch** / match 0,2; `xab`, `xxb`, `ab` nomatch all.
- Gate claim spot-checked: tests/lookaround/lookbehind.rxt:211-215 `(?<=a)b|(?<=bc)d` with
  `m "bcd" 2 3` exists; it is VM-forced and arm 2 is the back-step form (listing shows the
  2-character back-step), arm 1 the width-1 ASSERT form; under the rule both arms have F = {b},
  so byte 'd' drops both and the cell would go red at 2b. Agreed: the corpus is the backstop,
  not the proof.
- **Reading note (applies to S-1, S-2, S-3, S-5).** Every witness contains events the verdict
  table has no row for (ASSERT for `^`, NOTE for MRL/back-step/restore, RUNG/STRAT records):
  S-7's point, which I confirm below. Read STRICTLY, "unrecognised refuses the matcher
  function" would refuse every one of these witnesses (safe, no answer change) — and would
  also refuse every anchored matcher, so the build would do nothing on them, contradicting the
  design's own W1-W18 cells and measurements (whole-artifact refusal was measured, with
  verdicts firing on `^`-anchored patterns). The only reading under which the design does what
  it claims is ASSERT = BRANCH and residual NOTE = no effect, and under that reading the answer
  changes are real. So the findings HOLD as defects of the design text; their trigger is the
  under-specified NOTE/ASSERT rows plus the missing events.

## S-5

**Verdict: HOLDS as the critic scoped it** — the doc gap (the span row has no producer and no
class carrier) is certain; the answer change is real for a builder who follows Stage -1's event
list, and does not arise for one who invents the missing span event. Severity: answer under one
of two readings, doc under both.

- Re-emitted: `$B -p rx -o w/gs.c --pattern '^(?:[ab]+b|y)(z)'`, `... -o w/lz.c --pattern '^(?:.*?x|y)(z)'`.
  Against soundness/w/gs.*, lz.*: only the `PCREC_FEATURE_SET`/`_MODULES` stamp lines differ (the
  critic used `--features all`); matcher text identical. Route VM.
- Base text confirmed: greedy span = raw `{ ... while (... class ...) rx_span_cursor += 1; }` block
  at L4 (w/gs.c), listing `L4 label / set / note / note / goto L8`; lazy extend = raw
  `if (!(... rx_class_bitmap0 ...)) goto rx_fail; rx_span_cursor += 1;` at L9 (w/lz.c), listing
  `L9 label / goto L8`. VE_RUNG (emit_vm.c:285, produced at :3700) carries the label and the rung
  KIND, no class; it is a side-table record, not a program-trace event (:10028-10037).
- Text: the table has a `span (cursor rung)` row ("F ∪= class, continue as zero iterations"), but
  Stage -1's event table lists no span event and nothing that carries the class; the completeness
  check counts no `while`/class test on `span_cursor`. So the row has no producer.
- Rule derivation (mine, the Stage -1-literal reading): arm 1 passes SET slot4 (trailed:
  non-effect), the span-cursor writes (dead at L6 and at the retreat/extend labels' MAYFRAMES:
  non-effect), the PUSH fork (loops back to L8), and stops at the continuation's CLASS: F = {b}
  (greedy) / {x} (lazy); arm 2 F = {y}. Same as gst.diff / lzt.diff.
- Twins (mine, identical edits): L2's `RX_PUSH(&&rx_L6..); goto rx_L4;` -> switch, default fail.
- Observed (base / twin / libpcre2):
  - greedy: `abz` 0:0,3 1:2,3 / **nomatch** / = base; `aabz` 0:0,4 1:3,4 / **nomatch** / = base;
    `bbz`, `bz`, `yz`, `aaz` agree in all three.
  - lazy: `axz` 0:0,3 1:2,3 / **nomatch** / = base; `aaxz` 0:0,4 1:3,4 / **nomatch** / = base;
    `xz`, `yz` agree.
- Gate claim (greedy likely caught, lazy less so): not re-swept; plausible.

## S-6

**Verdict: HOLDS** (as a sabotage / doc gap: the text omits the offset rule; the wrong reading
moves captures; the right reading holds).

- Re-emitted: `$B -p rx --features all --engine=vm -fno-splice-calls -o w/c1.c --pattern '^(x(?>a(?1)?b)y)$'`;
  identical (.c and .h) to soundness/w/c1.*. Base: two call sites (L14 -> R_c1 = L17, L26 ->
  R_c2 = L29), snapshot `RX_SET(START/END/CUT_MARK1/PENDING, slot_values[same])` after each
  RX_CALL, the shared exit L3 restoring `trail[resume_stack[call_top].trail_mark + 0..3]`
  positionally (w/c1.c:358-362).
- Text: `grep -n -i 'ordinal|positional|offset|trail_mark'` over the snapshot finds only V1's
  "(K36 positional storage)", the C-move's "positional reads run after the exit's capacity
  guard", the keying sentence and the C-move deny row. Nothing says which offset a KEPT restore
  reads once V1 drops snapshot entries. Confirmed omission. W18's sabotage list (PENDING read
  dropped; CUT mark read dropped; `\K` slot 0 in W) has no offset row. Confirmed.
- K_c re-derived (mine): after L17, L13 'b' -> L11 CUT reads MARK0 -> L9 'y' -> L7 reads PENDING,
  kills START/END; MARK1 unread; the surviving frame L15 leads to the same path; so K_c1 =
  {PENDING}. After L29: L23 CUT(5) reads MARK1, L19 reads PENDING and kills START/END, then the
  region RETURN forks to every R_c, which kill W under the stock-restore model: K_c2 = {MARK1,
  PENDING}. Agrees with the critic.
- Twins: I applied the critic's c1n.diff and c1x.diff with `patch` to MY re-emission (identical
  base) and read the result: C-move (restores at each R_c via `rx_ret_frame`, recorded at the
  exit after the capacity guard), V1/V2 narrowing; c1n reads kept ordinals (+0; +0/+1), c1x the
  original ordinals (+3; +2/+3). This is what the C-move + V1/V2 rows yield under each reading.
- Observed (base / c1n / c1x / libpcre2), 7 subjects:
  - `xaxabyby`: 1:0,8 / 1:0,8 / **1:-1,8** / 1:0,8
  - `xaxaxabybyby`: 1:0,12 / 1:0,12 / **1:2,12** / 1:0,12
  - `xaby` 1:0,4 all four; `xay`, `xaxaby`, `xab`, `xaxabyb` nomatch all four.
- Severity: doc (answer if built on the original-ordinal reading), as the critic says. Which
  reading a builder takes: an emitter that loops over W(g) and simply skips deleted slots keeps
  the loop index (the original ordinal) unless told otherwise, so the wrong reading is a natural
  one.

## SEAM-5

**Verdict: HOLDS.**

- Re-emitted: `$B -p rx --engine=vm --features recursion -o w/spec/spec.c --pattern '^(a(?1)?b)$'`;
  byte-identical to seam/w/stock/spec.c and seam/w/spec.c.
- Twin: `patch` of seam/w/spec_full/twin.diff onto my re-emission gives a file identical to
  seam/w/spec_full/spec.c. I re-derived each edit from the snapshot's rows:
  - C-move: restore of PENDING at R_c1 (L13) through `rx_ret_frame`, recorded at the exit after
    the capacity guard; kept ordinal +0;
  - round A iter 1: K_c1 = {PENDING} (L7 reads PENDING, kills START/END); K_c2 = {PENDING} (L15
    reads it); V3 deletes L15's START/END (L3 RETURN forks to every R_c, which kill W(g) in the
    stock-restore model);
  - round A iter 2: with L15's read gone, K_c2 = {} (V1/V2 drop c2's entries) and L2's PENDING
    write is dead (V3);
  - round B: V5 untrails L4 PENDING and L7 START/END (dead at the attempt entry, at L11 and at
    L19's continuation);
  - walk 3: no `_SET` between L2 and the inner `goto rx_L2`, so `vm_jump_closes_trail_cycle`
    places no checkpoint there; `nset` = 2 KEEP sites -> `margin = 2` (was 15). The exit L3's
    checkpoint stays.
  This is the rule as written; I found no other reading of these rows that differs here.
- Observed (default entry `rx_search`; base / twin / libpcre2), subjects a^n b^n:
  - n = 1, 2, 5, 763: identical in all three (763 -> 0:0,1526 1:0,1526);
  - n = 764: **-3 (FRAMES)** / 0:0,1528 1:0,1528 / same as twin;
  - n = 1000: -3 / 0:0,2000 1:0,2000 / same as twin; n = 1024: -3 / 0:0,2048 / same;
  - n = 1025, 1100: -3 / -3 / libpcre2 answers;
  - a^5 b^5 x and `ab`: identical; a^764 b^764 x: -3 / nomatch / nomatch (also a give-up -> answer move).
  No new give-up, no capture difference where both answer: the twin is a G1-legal give-up ->
  answer move, matching libpcre2.
- Gate facts confirmed:
  - tests/recursion/framebuffer.rxt:41 `gu frames` (subject length 1528) in the default-entry
    block (lines 31-41, comment: "this give-up is the shipped behaviour") — that is cell 1. The
    design's census (snapshot lines 91 and 721) names "framebuffer.rxt cells 2-4" only.
  - tests/recursion/d27/sr_depth.rxt:58 (len 1528) and :59 (len 2000) are `gu frames` on the same
    pattern and move under the twin; :60 (len 4000, n = 2000) stays FRAMES. sr_depth is named in
    the census (as a file), so (a) is about card 0a, not a missing reader.
  - Card 0a (snapshot line 648) states "0 failed; a red is a design defect: stop and report" —
    the harness compares to the `gu frames` expectations, so these cells go red by design.
  - tests/axes/run_axes.sh:648-678 (`GIVEUP1_ALLOWANCE`, a per-key manifest) and :1508-1512
    (every GIVEUP1 case fails unless its exact `<flags>|<file:line>` key is named). The existing
    `-fno-req-byte|tests/recursion/d27/sr_depth.rxt:*` rows are at :83, :157-161, :179-183 (other
    patterns of the same file), not at :58-59; the critic's "same file, re-triage" is correct,
    its row line range in run_axes.sh is approximate.
- Correction: none to the substance. Note the design's own Measurements already report the twins
  answering ~3,800 stock give-up cells, so the author knew moves happen; the defect is that the
  STEP 0 card and stage gates are written as plain equality and do not carry them.

## S-8

**Verdict: HOLDS** (check adequacy, latent answer; the factual premise is exact).

- Re-emitted the critic's artifact: `$B -p rx --features all --engine=vm -fno-splice-calls -o w/t2.c --pattern '^(b)(?1)'`
  — identical to soundness/w/t2.c.
- Base lines (w/t2.c): `#define RX_CHARGE_WORK` :98 (reads/writes `run->work_left` :101-102),
  `RX_TRAIL` :106 (`run->trail_depth`, :107-110), `RX_SET` :112, `RX_PUSH` :115
  (`run->resume_depth`, `run->trail_depth`, `run->call_top`, :116-121), `RX_CUT` :123
  (`run->resume_depth =` :124), `RX_CALL` :127 (:128-135), `RX_TRAIL_CHECK` :172; the matcher
  `rx_match_anchored` starts at :230; `#undef RX_TRAIL/RX_SET/RX_PUSH` at :303-305. All are
  FILE-scope `#define`s textually outside the matcher function. Count: 44 cursor-field
  occurrences of `run->(trail_depth|resume_depth|call_top|work_left|steps_left)` in the file,
  12 of them inside the function's text (:230-302).
- Snapshot sentences: R "That covers macro text, primitive value text ..." (line 323); the guard
  "no `run->(resume_depth|trail_depth|call_top|steps_left|work_left)` occurs in a matcher function
  outside the write-back and reload brackets" (lines 414-416); sabotages W3's value text, the
  steps_left write-back, the compaction reload (417-419) — none plants a macro body.
- So a guard implemented as a grep over the function's text cannot see an unlocalised macro
  body. "Occurs in a matcher function" could be read as "after preprocessing", which would be
  adequate, but the text does not say so and its three sabotages would not distinguish the two
  implementations. Correction: none; the critic's fix (run the guard on the preprocessed function,
  add a macro-body sabotage) is the right shape.

## SEAM-1

**Verdict: HOLDS (premise)**; the keying failure itself stays SUSPECTED, as the critic labels it
(no keying code exists to run).

- Re-emitted: `$B -p rx --engine=vm --features recursion -fno-splice-calls -o w/ck2/spec.c --pattern '^(?:(?1)y)*(a|b)$'`;
  identical to seam/w/ck2/spec.c.
- Base text (w/ck2/spec.c): L4 `RX_PUSH(&&rx_L8..)`, L6 `RX_CALL(&&rx_L10..)` then the three
  snapshot `RX_SET`s (START, END, PENDING) and `goto rx_L2`; L10 -> L9 'y' -> L7
  `RX_TRAIL_CHECK(); goto rx_L4;`. No other `_SET` lies between the `rx_L4:` label and that
  back-goto in the text.
- Mechanism confirmed in src/gen/emit_vm.c: `vm_jump_closes_trail_cycle` (:3510) is
  `lbl_nset[id] && lbl_nset[id] <= v->nset` with `lbl_nset[id] = nset + 1` set when the label is
  written (:3480); `vm_goto` (:3527) emits a checkpoint iff it is true, and
  `vm_trail_check_text` (:3491) logs an event (VE_NOTE today) for each. The snapshot says walk 3's
  `vm_set` counts KEEP sites only (line 352). So the L7 checkpoint exists only because of L6's
  snapshot SETs: confirmed.
- Rule derivation (mine): live-after(R_c = L10): L9 -> L7 -> L4 -> {PUSH L8 whose path L8 -> L5
  writes PENDING before L13 reads it and kills START/END; CALL at L6 reading K_c itself}. Least
  fixpoint K_c = {}; V2 deletes all three restores and V1 all three snapshot entries. In walk 3
  `nset` does not advance between L4 and L7, so the checkpoint and its event vanish, and every
  later event (L8/L5 SET, L13's SETs, the region's L2/L15 SETs, the exit) has a walk-3 ordinal one
  lower (plus the deleted sites' own events) than its walk-2 ordinal.
- Snapshot sentences (lines 341-346): "keyed by site id: the ordinal of the site's event in the
  walk that decided it ... D's new chain labels are allocated after every walk-1 label" and the
  all-KEEP byte-identity keying check. Both confirmed as quoted; an all-KEEP table moves no event,
  so the check cannot fail on an ordinal shift. "Ordinal of the site's event" does not say whether
  it counts all events, sites of one kind, or deleted sites — any of the safe schemes the critic
  lists is compatible with the text, which is why the failure is only SUSPECTED. Overlaps S-4
  (skipped per brief).

## SEAM-2

**Verdict: HOLDS** (design/doc inconsistency; soundness not at stake, as the critic says).

- Rounds re-applied by hand to two real emissions (mine, identical to the critic's):
  - w/ck2/spec.c (`^(?:(?1)y)*(a|b)$`, linked): A1 iteration 1 — stock-restore model (every R_c
    kills W): L15's `START := PENDING` / `END := pos` are dead (next stop is the RETURN at L3,
    then the kill at R_c); K_c = {} so V1/V2 delete the snapshot/restore entries. L2's
    `PENDING := pos` is still LIVE in iteration 1, because ordinary liveness counts L15's
    `START := PENDING` as a read of PENDING whether or not START is dead. A2: no copy. Iteration 2:
    L15's read is gone, so L2's write is dead -> DELETE. Iteration 3: no change. Round A needs 2
    productive iterations.
  - w/spec/spec.c (`^(a(?1)?b)$`, SEAM-5's specimen): the same shape — iteration 1 deletes L15's
    START/END and c1/c2's START/END entries (K = {PENDING}); iteration 2 empties K_c2 and deletes
    L2's PENDING write. 2 productive iterations. (I did not redo the critic's 3-iteration pp case.)
- Snapshot text, quoted: Summary "One pipeline: each pass reads a REAL emission" (line 31);
  "Each pass reads the events of a real emission, never a predicted one" (333); verdict table
  "decided in ROUNDS, each round on the program it rewrites" (272-273); "Round A, repeated until
  nothing changes" (287); "at most three emission walks per VM artifact" (368); card 0i "the
  walks' upper bound is 3x the emission share" (656); Q3 "An in-memory rewrite ... is a second
  description of what the emitter would write, which is the failure the listing's design forbids"
  (801-803).
- Contradiction confirmed: iteration 2 reads "walk 2 minus iteration 1's deletions", which no
  walk emits. Either the rounds are an in-memory rewrite of walk 2's event list (then lines 31/333
  are false for every round after the first, and Q3's choice is already made for the slot-flow
  verdicts), or every round re-emits (then "at most three walks" and 0i's 3x bound are wrong,
  the walk count being unbounded by the text). Mitigation the critic also notes: a deletion mask
  over walk 2's events is a faithful model (DELETE emits nothing; SETU is slot-neutral) except for
  checkpoint events, which are slot-neutral too (SEAM-1) — so the honest restatement costs nothing.

## SEAM-4

**Verdict: HOLDS**, with one magnitude correction (the census point is weaker than stated).

- "`PCREC_MAX_VM_RESUME_POINTS` is defined nowhere": confirmed. `grep -rn 'define PCREC_MAX_VM_RESUME'`
  over the whole review tree finds nothing. The name appears only in comments/messages:
  src/gen/emit_vm.c:9813 (the `resume-points` row's comment), tests/codegen/run_ir_listing.sh:436
  and :474, tests/mech/sabotages/S305_lit_run_slot_walk_overskips.sh:10, and one more the critic
  did not list, tests/vm/run_vm_tests.sh:250 ("that 128-point cap"). src/core/limits.h:196-203
  records the 128-point total cap as a measured-and-rejected first draft (the cap that exists is
  on REPLICATION, e.g. the max-replicas limit and `PCREC_MAX_VM_REPLICATION_PRODUCT`, not on total
  resume points).
- `v->npush` readers: every code occurrence in src/gen/*.c is a pre-pass increment (:3040-3416)
  except one read, the listing row at emit_vm.c:9816; the other mentions (:8049-8066, :10955,
  :11034) are comments saying it is deliberately NOT consulted. Confirmed: one consumer.
- run_ir_listing.sh:465-480: `ir_rp` (listing row) vs `c_rp` (emitted `RX_PUSH(&&rx_L` sites);
  `ir_rp < c_rp` is a hard FAIL. S305: `SAB_SUITES="irlisting"`, its SAB_DOC_FIGURE records
  "DETECTED by run_ir_listing.sh's resume-points under-count check". I did not run the matrix, so
  "detected ONLY by that assertion" rests on S305's own record; it is the only detector it names.
- W7b: `$B -p rx --engine=vm --emit-ir --pattern '[abd]x|[acd]y|[bcd]z'` -> `resume-points 2`,
  `islands 0` (reproduced). With D's 5 sites the two branches follow exactly as the critic says:
  (a) row stays pre-pass -> 2 < 5 -> run_ir_listing.sh FAILs on every artifact where D adds
  pushes; (b) row = final walk's count (the snapshot's choice, line 349) -> the assertion compares
  the final walk with its own text, and S305's planted pre-pass under-count changes nothing
  observable -> S305 UNDETECTED.
- Snapshot: "the push-site total and the resume-point cap" (89, 347-350), W7b "the cap reads it"
  (478) — the cap the design says the final walk feeds does not exist. Confirmed.
- Correction: the census named in landing 2 is "Readers found by grep, plus these named ones"
  (720); a grep for `resume-points` does hit run_ir_listing.sh and S305 (S305:12 contains the
  token). So the readers would likely be FOUND; what the design lacks is the DECISION (keep the
  pre-pass row with its own D-free comparison, or retire S305 by name). Severity doc +
  check-integrity, as stated. The `vm_reseed_cal[has_push]` aside was not verified.

## SEAM-7

**Verdict: HOLDS** (speed + doc; every cited base fact checked).

- `fit_rungs[]` is at src/core/compile.c:1268. Order of the rows I read: forcing, nomem,
  size-term-trial, sel1-collapse, sel1-drop, drop-compound, drop-end-mark, **unroll-rescue**
  (:1330, `.applies = NULL`, `.retries = 0`), prefilter-collapse (:1334, retries 1),
  drop-anchored, drop-premul (note "measured ~1.27x"), **drop-handoff** (note "measured up to
  ~2.5x"), **drop-prefilter** (note "measured up to ~4x slower"), refuse.
- `COMPILE_MAX_ATTEMPTS` is a hand formula (compile.c:672) held equal to `fit_attempt_bound()`
  (:1455) by `fit_check(... == COMPILE_MAX_ATTEMPTS ...)` at :1769-1770: a new retrying row moves
  it. Confirmed.
- docs/spec/limits.md 8.4¶2 (line 310): "The order is by measured cost, cheapest first ...
  row 1 runs inside every VM attempt, so before any retry". 8.4¶3 (316): `--size-cap=refuse`
  "denies every row of this table marked degrading, which is all eight". 8.4¶4 (318): the
  "smallest artifact" refusal promise. src/core/CLAUDE.md:14: "A new contributor rung on the VM
  side forces a MEASURED order (D77)". All quoted as the critic says.
- Snapshot (lines 364-367): "an over-cap artifact climbs a new `fit_rungs[]` rung,
  'drop-dispatch' (re-emit without D, i.e. skip walk 2), before the refusal ... No size factor
  exists to tune." The position relative to unroll-rescue / drop-handoff / drop-prefilter is not
  stated; "before the refusal" admits every order. Confirmed.
- Consequence: since unroll-rescue acts inside every VM attempt, D's growth (the design's own
  +9-10 %) is first absorbed by a smaller unroll K; if drop-dispatch is placed after drop-handoff
  or drop-prefilter, a ~2.5x/~4x measured loss is spent to keep a tens-of-percent dispatch gain.
  That conflicts with 8.4¶2's cheapest-first contract; the 8.4¶4 "smallest artifact" promise
  holds for any order. The critic's reading is correct; magnitude is a judgment on unmeasured
  costs (no run possible), so "speed" severity stands as a risk, not a measured loss.

## S-7 and SEAM-3

**Verdict: S-7 HOLDS. SEAM-3 HOLDS** (as a contradiction between two of the design's sentences;
its answer-level consequence is latent, and S-1/S-2/S-3/S-5 are its concrete instances today).

S-7 (missing rows):
- The statement-kind table (snapshot lines 221-246) has rows LABEL, SET, snapshot entry,
  restore, READ, PUSH, CALL, RETURN, GOTO, BRANCH, CLASS/LIT/WCLASS, span, SWITCH+CASEs, CLASSB,
  BREF, CUT, CHECKPOINT, WORK, LSET/LREAD, CALLOUT, ACCEPT, FAIL, attempt entry, unrecognised.
  None for ASSERT, NOTE, ISLAND, RUNG, STRAT, PRUNE — all six are in the snapshot's own kind list
  (line 161-163) and all six have producers at the base (`vm_ev(.., VE_X` counts in
  src/gen/emit_vm.c: ASSERT 4, NOTE 20, ISLAND 1, RUNG 1, STRAT 1, PRUNE 1; the enum comment
  calling VE_ISLAND "reserved: no producer" at :285 is stale too). RUNG/STRAT/PRUNE write no C
  and are filtered out of the program listing (:10028-10035), so "no effect" is true for them;
  ASSERT is a conditional jump (`if (...) goto <p>_L` — a `goto <p>_L`, so under Stage -1 it may
  become VE_BRANCH, but the text does not say ASSERT is retired).
- NOTE is where cursor moves hide: emit_vm.c:7174 (`scan_position = <p>_back_step(...)`),
  :7488 (`scan_position = (size_t)slot_values[..]`, lookaround restore), :5873 (revdet lazy
  commit) are printfs whose only event is a NOTE (confirmed on w/lb2.c and w/na.c in S-3).
  Stage -1 converts only the work and checkpoint NOTEs (VE_WORK, VE_CHECKPOINT).
- Strict reading refuses every matcher with `^` or any residual NOTE (the build does nothing on
  them); the evident reading (NOTE = no effect) is unsound today (S-3). Confirmed as stated.

SEAM-3 (compile-time completeness):
- Quoted and confirmed: "Each proof's only premise about its input is that the input is
  COMPLETELY modelled. Stage -1 and its completeness check provide that, and the unrecognised row
  refuses the function otherwise." (398-400); "an invisible read is not 'unrecognised', so no
  refuse row can catch it" (173-174); "The completeness check ... For every corpus artifact"
  (194-196); the proof framing "Soundness then composes by transitivity: each pass is proven against the
  program it actually reads" (36-37).
- V0 fires on an event of unknown kind only; a statement printed with no event (the four shapes
  of S-1/S-2/S-3/S-5 are live examples at the base) is neither unknown nor counted at compile
  time. The completeness check is a corpus test, so outside the corpus' emitter-path coverage
  the premise is coverage, not proof. Confirmed.
- Base facts: `pcrec_sb_printf(` occurs 178 times and `vm_ev(` 55 times in emit_vm.c at
  06aa5ab87 (the design's 182/54 was at 75ac19837 with a different count method; same order of
  magnitude). `vm_cls_reads` (:1771) does strstr-count the emitted text for a decision today, so
  the critic's in-compiler count has precedent. Fix shape is the critic's judgment; plausible.

## VERIFY COMPLETE

S-1: HOLDS (answer; base, twin and libpcre2 re-run by me: abcc/ababcc group 1 lost)
S-2: HOLDS (answer; both witnesses reproduce; vars basic.rxt:62 would catch the D form)
S-3: HOLDS (answer, under the only reading where the build acts: NOTE = no effect, ASSERT = BRANCH)
S-5: HOLDS as scoped (doc gap certain; answer change under the Stage -1-literal reading)
S-6: HOLDS (doc/sabotage; original-ordinal twin moves group 1, kept-ordinal twin = base = libpcre2)
S-8: HOLDS (macros are file-scope, outside the function text the guard greps)
SEAM-1: HOLDS (premise; the keying failure itself stays SUSPECTED)
SEAM-2: HOLDS (round A needs 2 productive iterations on two real programs; contradicts "real emission"/Q3 or "at most three walks")
SEAM-4: HOLDS (no such cap defined; npush has one reader; S305 detector moves); correction: a grep census would find the readers, the gap is the decision
SEAM-5: HOLDS (twin answers n = 764..1024 = libpcre2 where stock gives FRAMES; framebuffer.rxt:41 cell 1 not in the census; card 0a red by design)
SEAM-7: HOLDS (ladder position unstated; base facts exact; speed impact is a risk, unmeasured)
S-7 and SEAM-3: HOLDS (six kinds without rows; compile-time completeness is corpus-only)
