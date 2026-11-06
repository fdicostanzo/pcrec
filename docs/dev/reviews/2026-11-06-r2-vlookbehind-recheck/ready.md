# crit-vlb3 lens READY — is rev 3 ready for the stage-1 build go?

Subject: frozen copy `R/subject_vlookbehind.md` (rev 3, febde6edd). Code read in the review tree
`worktrees/crit-vlb3` (e20dee230). Line numbers: `S:n` = frozen subject, `file:n` = review tree.

## Findings

### READY-1 — the bounded step breaks DD12a(i) and the advance-agreement claim is false
CONFIRMED (by reading; a `range` lookbehind cannot be compiled today). Severity: maintenance
(a gate goes red at landing) + doc. Effort: S (design text) + S/M (the build's harness hunk).
Blast radius: every ASCII corpus pattern that stage 1 flips to compiled (24 distinct), plus the
`residlbrange` fixture under `-e utf8`.
- S:1275-1278 (§5.6) says `run_encoding_checks.sh`'s advance-agreement check "is unaffected ...
  A `range` fixture under `-e utf8` gives it a second site to read"; S:1534-1537 (§7) says the
  UTF-8 twin "also gives the advance-agreement check ... the bounded step to read, and it is W14's
  byte-step detector".
- The check reads ONE site only: it compiles the witness `a*` and extracts the lines after the
  retry loop's guard `if (attempt_position >= subject_length) return 0;`
  (tests/codegen/run_encoding_checks.sh:2128-2142). A lookbehind fixture is never compiled by it
  and its step is never extracted. So the check gives W14's byte-step sabotage NO detector.
- Worse, DD12a(i) (run_encoding_checks.sh:330-420, 1546-1866) compares each ASCII corpus pattern's
  `byte` and `utf8` artifacts as TEXT. It excises only NAMED encoding-owned regions: the four
  residual entries, "(2) the [K49] unanchored retry advance, the one splice DD-12 (7) admits into
  shared emitter code" (anchored on that same guard line, :362-369), `.encoding`, K50's guard,
  and the encoding-keyed selections. A `VSK_STEP_CHAR` splice is `scan_position++;` under byte and
  the three-line skip loop (plus its comment, READY-2) under utf8 (enc_byte.c:379, enc_utf8.c:542-550).
  It is in no named region. So every flipped ASCII lookbehind with a `range` branch becomes a
  DIVERGE_STRICT pair, and `make test`'s codegen section goes red.
- Owed text (name it in §5.6 / §7 / §6 gate 5): (a) a sixth named region in DD12a(i) for the
  lookbehind step, with its own counter and floor (and its asymmetry rule: present on both sides);
  (b) either a second extraction in the advance-agreement check (anchored on the step's own
  emitted text) or delete the "second site" and "W14's byte-step detector" claims and name another
  detector; (c) the two "one splice" statements that become false: the DD12a(i) header item (2)
  and emit_vm.c's K49 comment at :13340-13346 ("This loop is an EXTERNAL advance ... the one thing
  ... does not exist"); and enc.h:355-360's field contract ("the statements an emitted engine runs to
  move a failed attempt's START position"), which is wider than the `@N` comment §5.6 widens.

### READY-2 — the `advance` text carries a K49 comment that is false at the new site, under -fno-comments too
CONFIRMED. Severity: doc (emitted C text) + maintenance. Effort: S. Blast radius: every UTF-8
artifact with a `range` branch.
- The utf8 `advance` text begins with a five-line C comment: "The retry advance is this ENCODING's
  step ... an unanchored search may only ever try LATER CHARACTER BOUNDARIES as match starts"
  (enc_utf8.c:542-547). Rendered by `pcrec_enc_advance`, it is emitted VERBATIM. Measured: `a*`,
  `--engine=vm -e utf8 -fno-comments`, still emits the `[K49]` comment (R/ready/adv.c:307-311).
  enc.h's own D112 note says `advance` "ships ... all code" (doc half NULL), which this contradicts.
- §5.6 (S:1276) treats the step as "the text is the same and only a token's substitution
  differs". Spliced into the lookbehind loop, the comment describes a match-start retry inside a
  candidate loop, and survives `-fno-comments`. G4's "the encoding's step adds two more lines"
  (S:212) is three code lines plus five comment lines.
- Owed text: split `advance` into its D112 pair (doc, code) in the same change, so the lookbehind
  site renders the code half and its own role text; or state that the K49 comment rides along and
  why. Either way the build's `range` texts list (§5.1b, S:812-815) names it.

### READY-3 — S-U4's re-aim cell `(?<=a)x` never reaches the width rule
CONFIRMED. Severity: doc (a witness re-aim on a cell that cannot carry it). Effort: XS.
- §7 (S:1538-1543): "After stage 1, `(?<=a)x` becomes `range` [1,4] ... It is re-aimed at gate
  3's classification control: the judgment 'fixed width 1' becomes 'width 1..4'".
- A one-character body is a T3 CONTEXT NODE, built BEFORE any width rule: mod_lookaround.c:524-533
  ("T3 FIRST ... No width rule is asked of it"), ctxnode.c's header, and the [UCP] U2 note in
  run_codegen_tests.sh:1506-1511. Measured: `--emit-ir` of `(?<=a)x` has no lookbehind label at
  all; `(?<=ab)x` has "lookbehind branch 1 of 1, fixed width 2". So under the S-U4 sabotage
  `(?<=a)x` still compiles, as A_CTX, and no "width 1..4" judgment exists to read.
- Owed text: re-aim on a body of two or more characters, e.g. `(?<=ab)x` ("fixed width 2" becomes
  "width 2..8"). The row's own `SAB_DESC`/header ("`(?<=a)x` included", S-U4 :17-20, :24) is
  already stale today for the same reason, so the figure update owes that line too.

### READY-4 — gate 1's named harness has no UTF-8 mode, let alone PCRE2_MATCH_INVALID_UTF
CONFIRMED. Severity: design/doc (a gate names an instrument that cannot run a third of its cells).
Effort: S (name the instrument) / M (build it). Blast radius: gate 1's UTF-8 and ill-formed cells,
W6, W11(b), W13, W14's UTF cells, W15.
- Gate 1 (S:1320-1347) is "run by `tests/lookaround/run_lookaround_diff.sh`" and its cell set
  includes "byte and UTF-8" and ill-formed subjects compared "under `PCRE2_MATCH_INVALID_UTF`".
- That script and its shared oracle `tests/backrefs/bref_oracle.py` contain no encoding option:
  no `-e`, no `utf`, no compile or match flags (grep, 0 hits in either). §7 (S:1548-1551) says only
  "the harness that runs them needs that option".
- The tree already has INVALID_UTF-capable instruments (`tests/lib/p2probe.c`,
  `tests/utf8/run_startbnd_diff.sh`, `tests/utf8/gen_*_illformed.py`). Owed text: gate 1 names
  which instrument carries the UTF-8 and ill-formed cells (an extension of `bref_oracle.py` with
  a flags column, or a tests/utf8 section), and the population counts (K35) per mode.

### READY-5 — `VL_LB_COUNT`'s declaration has no sizing pass named
CONFIRMED (by reading). Severity: maintenance (a build lane will find it; the r6 process rule
"trace new storage to the pass that SIZES it" applies to locals too). Effort: XS.
- §5.6 (S:1249): "`<p>_lb<n>_count`, declared by the frame as the `rv` locals are". The `rv`
  locals are declared from `VmFrame.nrev_total` (vm_stmt.c:1203-1222, vm_stmt.h:304-318), with a
  `(void)` row for the ones that may be unused (vm_stmt.c:1247-1250, the -Wunused rule). `VmLocal`
  is `{k, loop, j, half}` and `vm_local_name` has one arm per member (vm_stmt.c:473-482).
- Unstated: the `VmFrame` field and who counts it; what `<n>` indexes (lookbehind site, or site ×
  branch); and that ONE artifact-wide local suffices (K_i is dead before the first push and the
  write-to-read window is straight-line, so no nested evaluation can interleave), which would make
  the frame row a single `size_t` and remove the count.
- Owed text: one bullet in §5.6 naming the frame field (or the single shared local) and the
  `vm_local_name` arm.

### READY-6 — the per-slot `low` legend collides with `vm_slot_name`'s no-parallel-list rule
CONFIRMED (by reading). Severity: design (house rule) / maintenance. Effort: S.
- Ruling 8 owes per-slot legend and listing text. §5.1b (S:749-751) proposes "One owner record per
  `low` index (span loop or lookbehind branch)" so the legend can say `SLOT_LB_LO<i>`.
- `vm_slot_name`'s header (emit_vm.c:1004-1010): "The classification is the SAME arithmetic
  vm_slot_guard/low/mark/rev/ctr use above, read backwards. It is deliberately not a second table
  ... a parallel list would be a second source of truth about it -- which is how a slot two live
  loops share gets emitted". An owner record per index is that list.
- Two forms obey the rule, and the design should pick one: (a) an ARITHMETIC sub-block: lookbehind
  lows after the span lows inside the family (`base_low + nspanlow_total + i`), counted apart in
  `vm_count_slots_look`, so the name and the `holds` text are read off the index as today; or
  (b) the `mark` family's precedent: one generic name and one `holds` text that covers both owners
  (`vm_listing_slots(..., "mark", ..., "a possessified loop's ... or an atomic group's")`,
  emit_vm.c:9832-9835). (b) cannot rename `SLOT_SPAN_LOW` without moving today's bytes (G2), so (a)
  is the one that delivers ruling 8's per-slot text. (a) also changes the "Only the TOTAL has to
  agree" sentence (S:742): the two sub-totals must each agree.

### READY-7 — the "160-byte `vm_rolef` limit" no longer exists
CONFIRMED. Severity: doc. Effort: XS.
- §5.1b (S:812-815): "The 160-byte `vm_rolef` limit and its truncation note apply to each".
  `vm_rolef` is arena-owned and unbounded (emit_vm.c:885-894 over `pcrec_sb_fragfv`, sb.c:611-624,
  which measures then allocates). The 160-byte note survives only as a STALE comment in
  `vm_look_behind_branch` (emit_vm.c:7125-7129), a reader the `range` row's text-1 rewrite touches.
- Owed text: delete the claim; list the stale comment among the texts that move.

### READY-8 — ruling 7's [VMREC] member list has no named home
CONFIRMED. Severity: doc. Effort: XS.
- Ruling 7: new members do not wait for [VMREC], "but [VMREC] must list them". §5.6 (S:1237-1259)
  says (b)/(c) "must model" the shape and that (c)'s declared-effects rule "takes one row each",
  but names no file. At the freeze the [VMREC] row (plan.md (plan row, at the freeze)) has no long-form body under
  `docs/design/plan_row_bodies/`, and no docs/design file lists `VmSeek`/`VmLocalKind` members.
- Owed text: §5.6 names where the list lands in the build commit (the [VMREC] row's refs line, or
  a new `plan_row_bodies/VMREC.md`) with the three entries (`VSK_STEP_CHAR`, `VL_LB_COUNT`, the
  `VSK_BACKSTEP` local operand) and their declared effects. §13 Q5 is then marked ANSWERED (ruling
  7) and Q6 ANSWERED (ruling 8), with §5.1b's "recommended" made "ruled".

### READY-9 — W12(a) fails for a reason the row does not state (K134's compaction)
SUSPECTED (fragility; the witness does fail today, traced). Severity: doc (witness argument).
Effort: XS.
- W12 (S:1479): "(a) Nine candidates: 2 + 9 live entries against a capacity of 5". Under the
  "LO_i written at L_try_i" sabotage the SET sits inside the cycle, so `L_adv_i`'s `goto L_try_i`
  carries a K134 checkpoint (emit_vm.c:3511-3535), and `<prefix>_trail_compact` DROPS later
  same-slot entries within a segment (emit_vm.c:12650-12668). Hand trace at capacity 5 (floor
  `5 - min(nset, 2) = 3`): the second candidate's checkpoint compacts LO,LO → one entry (depth 4 →
  3), then returns "never" because `3 + 5/4 > 3`; the fourth candidate's body write then hits
  `RX_R_FRAMES`. So the sabotage is red, but only because the trigger stops after one round.
- A K134 trigger change (re-arming was tried, lane trailgc3, per that header) would turn the
  witness GREEN under the sabotage. Owed text: state the mechanism (or choose a sabotage whose
  extra entries are distinct slots), and confirm W12(a) red at build.

## PROBED-AND-HELD

- Code cites in rev 3's delta, read in the review tree: `VmSeek` = {SPAN_COMMIT, RESTORE, ADVANCE,
  BACKSTEP} and `vm_r_seek` renders BACKSTEP with a literal `%d` (vm_stmt.h:131-136,
  vm_stmt.c:450-469) — so a local operand IS new; `VmLocalKind` 7 members (vm_stmt.h:141-149);
  `VK_LSET`/`VLO_ASSIGN`; `VK_WORK` takes a text count (vm_stmt.h:218, vm_stmt.c:372) so
  `RX_CHARGE_WORK(K_i)` needs no new operand; `RX_CHARGE_WORK` charges only `> 0` (emit_vm.c:12135-
  12141); `VPOS_CURSOR`/`VPOS_SPAN`; `vm_cursor_rep`'s header quote verbatim (emit_vm.c:4876-4883);
  the `low` layout comment (:947-953), `vm_slot_low`, `nlow`/`nlow_total`, `SLOT_SPAN_LOW`
  (:1042), the listing's `low` row and its "no cursor rung" note (:9828-9831), `VmSnap.low` and
  `vm_w_range` (:7566, :7802-7804); `vm_count_slots_look`'s `npush` arithmetic (:3038-3055);
  `vm_cost_look`'s `+1+nbranch` / `+2` (:2858-2864); `vm_plan_capacities` and the 3072 clamp
  (:8026-8044); `vm_look_behind` allocates `bl/bodl/endl` in one up-front loop (:7404-7408); the
  branch prologue order guard, push, work, BACKSTEP, sentinel (:7148-7206); `vm_jump_closes_trail_cycle`
  reads `lbl_nset` against `nset`, and only SET/SNAPSHOT/RESTORE bump `nset` (:3511-3535, :3576-
  3581) — so `L_far_i`'s retry jump (VSK_RESTORE seek + LSET) gets no checkpoint, as §5.1b says.
- The 14 new or re-aimed witness answers, re-probed on Oracle B (libpcre2 10.46): W6, W11(b), W12(a)
  and (b), W13 ×2, W14 ×4 (`\G` from 0/1/2, UTF `\G`), W15 ×2, W16 ×2 — all equal to §7's figures.
- `low` family through a callee's save set and splices: per-copy families include `low`
  (emit_vm.c:7789-7820), so `LO_i` inherits the call/splice save discipline span lows already
  have; this is a point FOR ruling 8, not against.
- W12(b) traced: the correct term sizes capacity 6; the sabotaged constant sizes 4; branch 1's body
  write meets `depth >= cap` with four distinct-slot entries live (mark, POS, LO_0, LO_1), which
  compaction cannot drop. Red as claimed.
- r6 RULING block vs §16b/§16c: V1 (term re-derived, explicit), V3 (arm deleted, rule kept), V4
  (deleted with its object, re-asked as Q6, now ruling 8) are SUPERSEDED in the open, each with a
  §16c row; V2, V5-V17 unchanged in rev 3's text. The "fix-induced traces storage to the sizing
  pass" process rule was applied to the trail (§5.5 items 1-5); its one miss is the local
  (READY-5). No r6 disposition found silently reversed.
- Stale-term sweep of rev 3 (D_i, SLOT_COUNTER, counter slot, `hi−lo+1`, growable, "8 lines"):
  every hit past the revision blocks is marked history or rev-2 cost text (§13 Q1(B)).
- GOALS: §0 still ranks G1-G5 with a measurable each; rev 3 serves them in order (G1 answers by the
  same candidate list; G2 by ruling A; G3 by one loop; G4 tightened to `2·hi − lo` and O(1) trail).
  Two goal texts are stale but harmless: G2's "must be closed before the build go" (closed), and
  G4's "two more lines" (READY-2).
- SIBLING OF A FAMILY. (1) The cursor-rung lookbehind loop is the SECOND member of "frame-carried
  candidate cursor + once-per-entry trailed bound" (`vm_cursor_rep` first); arev row 3 (rev 1 line
  259, §16c item 3) would be the third. The pick-up list already says row 3 shares `L_try/L_body/
  L_end`; unify into one emitter primitive when that third member is built (trigger: A-REV S3).
  (2) `VSK_STEP_CHAR` is the second caller of the `advance` text (after the K49 retry), and the
  third encoding-step spelling beside `$_back_step` and `next_pos`. Not one mechanism yet: they are
  different seam channels (entry vs inline text) on purpose (DD-12 (7)); READY-1 is the cost of
  the second inline caller. (3) `VL_LB_COUNT` and the far retry are single-member; no family.
- GENERAL FORM + UNLOCKS. The shape is "enumerate a position interval [far, near] by a
  frame-carried cursor, bound tested against one trailed slot, step = the encoding's character
  step bounded by the cursor". Unlocks, each with its trigger: (a) a raised or caller-set 255 cap
  costs no storage (trail independent of `hi`) — trigger: [IFACE-PUSH]'s `max_varlookbehind`
  candidate; then `back_step_upto` (§5.5) once the `(hi−lo)²/2` corner is measured; (b) stage-2
  references whose width is known only at run time take the same two run-time counts — trigger:
  a corpus/bench pattern needing it (none today); (c) arev row 3's candidate source as a second
  producer of the same cursor loop — trigger: A-REV S3 build; (d) [LB-EXIST] unbounded lookbehind
  with `far` from an automaton filter instead of `hi` — trigger: "a real pattern needs it".

Per-unit verdicts (stage 1):
- U1 width rule, both limits, `limits.def` rows, §10 pattern_language/limits §3.11: READY
  (rev 3 delta does not touch it; separable: the 65535 ceiling can land alone).
- U2 the loop and the emission table (§5.1, §5.1a, §5.1b): READY WITH TEXT FIXES (READY-6, -7).
- U3 record vocabulary and the seam (§5.6): READY WITH TEXT FIXES (READY-1, -2, -5, -8).
- U4 budgets and trail (§5.5): READY (term derived from every write; cites hold).
- U5 gates and witnesses (§6, §7): READY WITH TEXT FIXES (READY-1, -3, -4, -9).
- U6 spec hunks (§10, incl. limits §3.1 and the decision entry): READY.
- U7 [DD-14.LB] reversal and D27 material: READY (unchanged from rev 2).

Overall verdict: **READY WITH LISTED TEXT FIXES** (READY-1..9; READY-1 and READY-4 name
harness work the build owes, which the design must list, not redesign).
