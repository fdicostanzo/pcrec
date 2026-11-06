# crit-vlb3 lens fixind (fix-induced): findings

## Findings

### FIXIND-1 — the in-body `advance` splice turns DD12a(i)'s hot-loop identity red on every `range` pattern; §5.6 names the wrong check
CONFIRMED (by reading the check; no run). Severity: maintenance/design (a gate goes red at build, or is
weakened ad hoc). Effort: small (a named region + its counter + floor + witness, and a §5.6/§7 hunk).
Blast radius: every corpus pattern with a varying lookbehind, both encodings.
Design: §5.6 notes on `VSK_STEP_CHAR` (frozen copy l.1265-1277), §5.1a ("not an entry"), §0 G4 l.210-212
("the encoding's step adds two more lines").
Code: `tests/codegen/run_encoding_checks.sh` l.329-372 (DD12a(i) header), l.491 `GUARD_RE`, l.1304-1315
(excise), l.1527 (witnesses), l.2136-2141 (K49 awk extraction); `src/enc/enc_utf8.c` l.544-551
(`advance_utf8`), `src/enc/enc_byte.c` l.379-380; `src/gen/CLAUDE.md` l.27.
- DD12a(i) re-emits every corpus `.rxt` pattern under `byte` and `utf8` and requires the two texts to be
  IDENTICAL after excising a CLOSED list of encoding-owned regions. Region (2) is "the [K49] unanchored
  retry advance, THE ONE SPLICE DD-12 (7) admits into shared emitter code outside the entries table",
  found ONLY by `GUARD_RE` (`if (attempt_position >= subject_length|attempt_max) return 0;`).
- `VSK_STEP_CHAR` adds a SECOND splice of the same text inside the VM body, where no `GUARD_RE` line
  precedes it. Under `byte` it renders `scan_position++;`; under `utf8` a 5-line K49 comment plus
  `scan_position++; while (scan_position < (size_t)slot_values[...] && ...) scan_position++;`. Unexcised,
  so every stage-1 `range` pattern in the corpus is a DD12a(i) mismatch (the check's own sabotage
  validation (d) plants exactly this shape of text "outside every named region" and expects red).
- §5.6 instead says the K49 advance-agreement check "is unaffected ... A `range` fixture under `-e utf8`
  gives it a second site to read". It does not: that check extracts ONE site with an awk anchored on the
  retry loop's guard line of the `a*` witness (l.2136-2141); a `range` fixture is never read by it.
- Probe (review tree, `nice -n 19`): `(?<=a|bc)x` compiled `-p rx --emit-main` under `byte` and
  `-e utf8`; the `rx_match_anchored` function text of the two artifacts is IDENTICAL (`diff` empty),
  both calling `rx_back_step` twice. That identity is what DD12a(i) pins, and `VSK_STEP_CHAR` is the
  first record that would make the matcher body itself differ by encoding.
- So the addition lands on two unnamed readers: DD12a(i)'s region list (needs a region (6), its counter,
  a floor and a `range` witness in l.1527's list, and the asymmetry rule (b) for it), and the
  "one splice" sentences (DD12a header, src/gen/CLAUDE.md l.27 "The VM's unanchored retry advance comes
  from `PcrecEnc.advance`", enc.h's "the one call site splices ..." l.614-616).
- A third reader, a DECISION: the VM body's length feeds the entry-shape knee
  (`pcrec_vm_stmt_program_bytes` -> `pcrec_sb_len_decide`, uncut, comments included; emit_vm.c
  l.10874, l.11009 against `VM_INLINE_CHAIN_MAX_BYTES` 4,096). Today the advance lives in the search
  loop, OUTSIDE `VmBody`, so the body's length is encoding-independent. Spliced into the body, the
  utf8 text (about 420 bytes with its comment, measured from enc_utf8.c l.544-551 substituted, against
  17 for `scan_position++;`) makes the length, and so the entry rung, differ by encoding for the same
  ASCII pattern near the knee: an encoding-dependent emitter decision, which DD-12 (7) and DD12a(i)
  exist to exclude. The fix shape is small (measure the step's text out of the decision, as SIMD
  and layout text already are, or render a comment-free step), but the design must name it.
- Side fact: the utf8 text carries its own comment ("The retry advance is this ENCODING's step ... an
  unanchored search may only ever try LATER CHARACTER BOUNDARIES as match starts"), which is FALSE at a
  lookbehind step and rides into the artifact unconditionally (not under `-fcomments`). G4's "two more
  lines" is seven. Either the comment moves out of the backend text into the retry-loop caller, or the
  lookbehind site states it; both are encoding-seam edits the design does not list.

### FIXIND-2 — `VL_LB_COUNT`'s declaration has no sizing pass: no `VmFrame` field, no counter, no `<n>`
CONFIRMED (by reading; the gap is in the design text, the build would hit it as a compile error
"undeclared identifier" or invent the plumbing). Severity: maintenance (a build-time surprise, and a
second spelling of a local's name). Effort: small. Blast radius: every `range` artifact.
Design: §5.6 table row `K_i`'s writes (frozen l.1249: "`<p>_lb<n>_count`, declared by the frame as the
`rv` locals are"); §5.1b second table, column "matcher locals" (l.713), the only column of that table
that names NO pass.
Code: `src/gen/vm_stmt.h` l.276-290 (`VmFrame`), `src/gen/vm_stmt.c` l.1187-1250 (the frame's local
declarations), l.473-487 (`vm_local_name`), `src/gen/emit_vm.c` l.13056-13074 (the frame's producer),
l.10606-10617 (`nrev_total` from the count pass).
- Locals are not declared by any generic mechanism. The frame writes each family from its own
  `VmFrame` field: `span_cursor` (a rung bit), `nrev_total` (the count pass's `nrev`, one
  declaration line per loop index, plus the `(void)` suppression line), `nrevcaps` (sized by the
  widest body). "Declared by the frame as the `rv` locals are" therefore implies: a new `VmFrame`
  field, its producer in `pcrec_emit_vm` (from which count?), a declaration row in
  `pcrec_vm_stmt_frame`, and the numbering scheme `<n>` that both the declaration and
  `vm_local_name` read. The design states none of the four, and the §5.1b reader table names a pass
  for every column except this one.
- `VmLocal` is `{k, loop, j, half}`; which field carries `<n>` is unstated (a sibling field left
  unstated, read by `vm_local_name`'s new arm).
- The local's NAME is spelled in more places than the record: `K_i = min(hi - lo, scan_position)`
  and `K_i - 1` are `VK_LSET` `src` STRINGS, and the far charge is a `VK_WORK` `count` STRING (§5.6
  "the local's name"), all built in emit_vm.c, which cannot call `vm_local_name` (static in
  vm_stmt.c). That is the declaration/use split the frame's own [M6-READ] comment records as a past
  break ("The rename moved the uses and left the declarations, and a revdet artifact stopped
  compiling").
- A simpler shape the design's own facts license: `K_i` is "written and read only between `L_b_i` and
  the first push, which is straight-line code with no choice point or call" (§5.1). So no two
  `K` values are ever live at once, in any nesting, recursion or splice: ONE program-wide local
  (declared iff the artifact has a `range` branch, a `bool` in `VmFrame`, like `span_cursor`) is
  sufficient, and the `<n>` numbering, its counter and the per-branch declarations disappear. Either
  way, the design should name the pass.

### FIXIND-3 — the new operand and members leave their builder, [VMREC]'s list and two sabotage anchors unstated
CONFIRMED (by reading). Severity: maintenance/doc. Effort: small (three sentences in §5.6/§6/§7).
Blast radius: the build lane's first compile and the mech sabotage matrix.
Design: §5.6 table (frozen l.1251, l.1255) and notes (l.1259-1263); §6 stage-1 scope (l.1288-1316);
§7 S133/S134 notes (l.1522-1536). Ruling 7 (COMMON): members do not wait for [VMREC], "but [VMREC]
must list them".
Code: `src/gen/vm_stmt.h` l.252 (`struct { VmSeek sk; const char *slotx; int k; } seek;`), l.274
(`pcrec_vm_b_seek(sb, sk, slotx, k)`), `src/gen/vm_stmt.c` l.450-469 (`vm_r_seek`, a switch with no
default), `tests/mech/sabotages/S123_look_no_cursor_restore.sh` l.34-35, `S133_backstep_inlined.sh`
l.40-41; plan row [VMREC] at e20dee230 (plan.md l.239-245).
- **The local count operand.** "The seek record gains an optional typed `VmLocal`" names the field
  but not its siblings: how "absent" is spelled (a flag, or a sentinel `VmLocalKind`), which of
  `k`/the local the renderer reads for `VSK_BACKSTEP` (today `%d` of `k`), and whether the builder
  is widened (six call sites move) or a second builder is added. The choice matters to two readers
  that match builder TEXT: S133's `SAB_BEFORE` is the exact line
  `pcrec_vm_b_seek(v->sb, VSK_BACKSTEP, NULL, k);` with `SAB_COUNT=1`; a widened signature breaks the
  anchor (the row stops applying), a new `range` site written in the same spelling makes the count 2.
- **S123** is not named by §7 at all: its anchor is `            pcrec_vm_b_seek(v->sb, VSK_RESTORE, sl, 0);`
  (vm_look's restore), `SAB_COUNT=1`. The `range` row adds two `VSK_RESTORE` sites (`L_n_i` from
  `POS`, the far retry from `LO_i`); one written with the same local name and indent turns S123's
  count to 2. §7 should say the new sites are spelled so that S123 keeps exactly its one site, or
  re-count it.
- **[VMREC]'s list.** Ruling 7 makes listing the two members and the operand a condition. [VMREC]'s
  row (and its refs) carries no member list today, and §6 stage 1's scope does not include writing
  one; §5.6 only says "(c)'s declared-effects rule takes one row each". The build lane needs to know
  WHERE the list lives (the row's (c) rulings line, a long-form body, or the design §5.6 table as
  the cited home) or the condition is unowned.
- **Effects completeness of `VL_LB_COUNT`.** §5.6 gives its effect as "an untrailed local", but the
  local is also READ through opaque strings: the `VK_LSET` `src` texts (`min(hi - lo, scan_position)`,
  `K_i - 1`) and the `VK_WORK` `count` text. [VMREC] (c)'s ruling at the freeze is "every analysed
  operand is printed by its renderer or carried as a record field". The new `VSK_BACKSTEP` operand
  honours it; these three reads do not. Existing `rv` locals have the same shape, so this is a note
  for the [VMREC] list, not a blocker.

### FIXIND-4 — W-low's sabotage is spelled in a form the record vocabulary cannot build
CONFIRMED (by reading). Severity: doc (a sabotage row a build lane cannot plant as written).
Effort: one sentence. Blast radius: §7's W-low row only.
Design: §7 W-low (frozen l.1484: "`LO_i` written untrailed (`VK_LSET`)"); §3 host row (l.338).
Code: `src/gen/vm_stmt.h` l.137-149: "An untrailed matcher LOCAL an LSET may write. The span cursor,
the subject cursor and run state are not members ... so an LSET cannot be built on them"; the
`lset` operand is a `VmLocal` (a closed enum of locals), never a slot index.
- A `VK_LSET` cannot target a slot, so "`LO_i` written by `VK_LSET`" is not a mutation of the
  emitter; it is a vocabulary extension. The plantable wrong spelling is "`LO_i` held in an untrailed
  LOCAL (a second `VmLocalKind` member beside `VL_LB_COUNT`)", which is also the natural mistake (it
  is exactly how `K_i` is held). The codegen check ("`LO_i`'s write is a `RX_SET` of the
  `SLOT_LB_LO<i>` slot") then fails on that plant. Re-spell the row so its plant and its check read
  the same thing (learnings §3: a control whose plant cannot be built never fails).

## PROBED-AND-HELD

- **Trail term vs every write (r6's lesson).** Traced each write of the `range` sketch to its sizing
  pass in the review tree: `LO_i` (`vm_set` -> `vm_set_counted`, emit_vm.c l.3574-3592: `nset++`,
  VE_SET) is the loop's only trailed write; `K_i` (`VK_LSET`) and the two `VSK_RESTORE` seeks are not
  trail writes. The term `2 + (range branches)` added to `vm_cost_look` (l.2858-2864) covers the
  peak (exhausted branches' `LO` stay live, body max on top). The call arm's `2 * |W|` (l.10640)
  picks `LO_i` up through the region counter ranges (`VmSnap.low`, l.7566-7579, l.7802-7804) with no
  new code, provided `vm_count_slots_look` counts it (the design says it does). HELD.
- **Slot sizing.** `nstate` (l.10631-10634) and every base (`vm_slot_mark`/`rev`/`ctr`/pending/look,
  l.958-990, l.1134-1223) are sums of family totals read from the count pass, so adding to `nlow` in
  both passes keeps them consistent; replicated copies are walked per copy by the count pass
  (l.3160 `for copies vm_count_slots`), matching per-emission allocation. HELD.
- **K134 checkpoint rule.** `vm_jump_closes_trail_cycle` (l.3511-3514) reads `lbl_nset`/`nset`, and
  only SET/SNAPSHOT/RESTORE records count (l.3571-3581): the far retry's `goto L_far_i` gets none,
  `L_adv_i`'s `goto L_try_i` gets one iff the body has a SET-family write. The margin
  (`vm_emit_trail_compact`, l.12757 `margin = nset`) counts `LO_i`'s site automatically. HELD.
- **Push count / frames.** `vm_count_slots_look`'s `nbranch - 1` (l.3053) -> one per non-last
  `one-length` plus one per `range` is stated; at most one lookbehind-owned retry frame is live at a
  time, so `vm_cost_look`'s `1 + nbranch` stays a bound. HELD.
- **Seam facts.** `$_back_step` (enc_utf8.c l.303-341): `k == 0` returns `pos` (never the sentinel);
  `size_t k` in both encodings, so a local count is in range; the sentinel is monotone in `k`
  (re-read, and the evidence's port in `candidates.py` matches the emitted text line for line).
  `advance_utf8` reads `@S[@P]` only under `@P < @N`, so `@N` = the cursor is in range. HELD.
- **[M5-SEAM] per-site counts.** `calls_in_bodies` counts call tokens, so the local-count back-step is
  counted like the literal one, and the sentinel rule ("one sentinel compare per back-step call")
  holds for the `range` row's two (`==` and `!=`). `ctxnode.c` (`lang_charset`) admits only bodies of
  exactly one character, so no `range` branch is diverted to a context node and the `residlbrange`
  fixture stays a lookbehind. HELD.
- **Dangling deleted terms.** Grepped the frozen copy for `D_i`, `SLOT_COUNTER`, `Σ_range`,
  `hi_i − lo_i + 1`, `growable`, per-candidate: every remaining occurrence is marked history (rev 2,
  §16/§16b tables, the struck rewrite list "Those four rewrites were the counter shape's", the arev
  pick-up list). One residual: §5.1b l.666-667 ("at `lo == hi` it has today's order and pushes at
  the cursor") describes rev 1's sketch, which rev 3's rewrite 3 contradicts; it reads as current.
  Doc-only, not filed separately.
- **The low family's contract**, quoted (emit_vm.c l.947-953): "what a span loop cannot recover from
  its own resume frame is where the loop STARTED ... written once per loop ENTRY ... O(1) trail per
  entry". `LO_i` is the walk's bound, written once per evaluation, trailed: fits, with the comment
  widening §5.1b lists. The legend/listing readers (`vm_slot_name` l.1042, `vm_listing_slots`
  l.9828-9831, `VmStamp.nlow` l.14068) are all named by §5.1b. HELD.
- **Today's lookbehind trail constant**: not re-measured (rev 2's premise.out); the cost function
  text (l.2858-2864) says `trail += 2`. Consistent.

## Questions for a pcre2-reader

None: every fact this lens needed is pcrec code.
