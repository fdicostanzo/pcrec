# Verifier: critic round vmcons2 (design short re-check), 2026-10-29

Verifier (opus). Subject: docs/dev/lanes/vmcons2_report.md @ 2227faf5a (snapshot
subject_vmcons2_report.md). Review tree: worktrees/crit-vmcons2 (main ffb9254cb + lane/trailgc
ffd1f578e), `B=worktrees/crit-vmcons2/build/pcrec`. Every artifact below was RE-EMITTED by me into
`/var/tmp/pcrec-pcrec/scratch/crit-vmcons2/verify/w/` (`V=` below) and every twin rebuilt from my
emission. Own drivers: `V/vd.c` (pcrec, `rx_search`, rc + every span), `V/vp2.c` (libpcre2-8, rc +
every span, -1 = unset), `V/vrun.sh` (one gcc -O1, run under scripts/watchdog). No critic artifact
was compiled or run. Written incrementally, one section per finding id.

## SOUND-1

**Verdict: HOLDS** (answer, under a reading the text permits but does not force; the cell-reach
half holds unconditionally).

- Code (review tree `src/gen/emit_vm.c:5155-5159`): `if (a->u.rep.rmin > 0) { vm_emit_span_scan(...);
  vm_span_reach(...); } else pcrec_sb_printf(b, "    %s_span_cursor = scan_position;\n", v->p);`.
  So the lazy rung at rmin = 0 prints no span block. The design's own survey types 5159 as `LSET`
  (`vmcons2_evidence/site_kinds.tsv`: "5159 vm_cursor_rep LSET NONE span_cursor = scan_position"),
  and SPAN has 1 site (the scan block). Re-emitted `V/c5b.c` (`$B -p rx -o V/c5b.c --features all
  --pattern '^(?:.*?x|y)(z)'`): arm 1 is `RX_SET(RX_SLOT_SPAN_LOW0,..); rx_span_cursor =
  scan_position; goto rx_L8; rx_L8: if (RX_PRUNE_TOO_SHORT(rx_span_cursor, 2)) goto rx_fail;
  RX_PUSH(&&rx_L9, rx_span_cursor); scan_position = rx_span_cursor; goto rx_L7;` - no `{` block.
  Control: the rmin >= 1 sibling `^(?:[ab]{2,}?b|y)(z)` (`V/c5c.c`) does print the scan block.
- Design text: kind table PUSH row "pos = cursor: fork; pos = span cursor of the open SPAN: continue,
  no fork; any other pos: OPAQUE"; S-5 disposition "A span-cursor PUSH and the span's SPAN_COMMIT
  are members: no fork, continue"; S-3 disposition "OPAQUE at every SEEK except a SPAN_COMMIT of the
  span in progress". Nothing defines "the open SPAN" / "span in progress" (no open/close rule).
- Reading applied (the critic's): the PUSH whose pos operand is the span-cursor local is a member
  (S-5's wording keys on "span-cursor PUSH"), and the following `scan_position = rx_span_cursor`
  (5214, typed SEEK SPAN_COMMIT by the survey) continues. Walk: SET (trailed, non-effect), LSET
  (non-effect: `rx_span_cursor` is rewritten at L9 before any read on the resume path), BRANCH_FAIL
  (continue), PUSH (member: continue, no fork into L9), SPAN_COMMIT (continue), CONSUME `x`: F(arm 1)
  = {x}; F(arm 2) = {y}. D2 admits. The text does NOT force this: the design's operand list ("group
  id (span or island)") would let a builder key membership on a span id, and no span id exists here,
  so the PUSH would fall to "any other pos: OPAQUE" (safe). The text does not forbid it either: a
  pos-typed operand ("span cursor") cannot tell which rung's span it belongs to, since every rung
  uses the one local `<p>_span_cursor`.
- Twin (`V/c5b_twin.c`, my edit from my emission): at rx_L2, `RX_PUSH(&&rx_L6, scan_position); goto
  rx_L4;` replaced by `if (scan_position >= subject_length) goto rx_fail; switch
  (subject[scan_position]) { case 120: goto rx_L4; case 121: goto rx_L5; default: goto rx_fail; }`
  (D2: one candidate per class, so no push).
- Run (`V/vrun.sh`, subjects axz aaxz xz yz bz):

  | subject | base | twin | libpcre2 |
  |---|---|---|---|
  | axz | 1 0:0,3 1:2,3 | **0** | 1 0:0,3 1:2,3 |
  | aaxz | 1 0:0,4 1:3,4 | **0** | 1 0:0,4 1:3,4 |
  | xz | 1 0:0,2 1:1,2 | same | same |
  | yz | 1 0:0,2 1:1,2 | same | same |
  | bz | 0 | 0 | 0 |

- Cell reach: C5b ("lazy SPAN", sabotage "as C5a" = SPAN row contributes nothing) reaches no SPAN
  record at all, so that sabotage cannot turn it red under either reading. HOLDS.
- Fix direction the critic gives (membership by span id carried as an operand, no SPAN of that id
  on the path -> OPAQUE; a rmin >= 1 lazy cell for the SPAN row) is consistent with the evidence.

## SOUND-2

**Verdict: PARTLY.** The structural half HOLDS unconditionally (the ISLAND opener is a record no CFG
path reaches). The answer half HOLDS only under one of two readings the design text gives, and the
design's own kind table gives the other one. Its twin reproduces exactly.

- Code (`emit_vm.c:4614-4636`): at `x == 0`, `vm_ev(v, VE_ISLAND, entry, ...)` is written and THEN
  `vm_lbl(v, n->lbl, ...)`. The design's merge rule ("Byte identity of (a)": a legacy `vm_ev` that is
  not merged "stays an annotation record at its original position") and the kind table (ISLAND is an
  annotation, "(print nothing)") put the opener BEFORE the root's LABEL record. A GOTO's successor is
  "L" (the LABEL record), and the record before the opener is the previous arm's unconditional
  `goto rx_fail` (FAIL: path ends). So no successor edge reaches it. Re-emitted `V/isl5.c`
  (`--features all -fno-altcls-factor`, `^(?:\d+y|(?:ab|abc|abcd|abcde))(z)`, `RX_VM_ALT_ISLANDS 1`):
  arm 2 at rx_L5 starts `if (... !memcmp(subject + scan_position, "ab", 2)) goto rx_L8; goto
  rx_fail;`. This is a single-child root, with no SWITCH that could route through "inside an ISLAND
  group: see ISLAND". Listing `V/isl5.ir`: the previous arm's `fail`, then `L5 label`. The opener
  record precedes that label.
- The two readings for the island ADVANCE (`scan_position += k`, `emit_vm.c:4716`, typed SEEK in
  site_kinds.tsv):
  - Rule 3 (prose): "goes OPAQUE at every other cursor move: ... ADVANCE outside an island". The
    summary adds "a member of a declared group (SPAN, ISLAND)", and the operand list carries a
    "group id (span or island)". Read with the operand, the ADVANCE is a member, so FIRST+
    continues.
  - The kind table row "SEEK RESTORE s / BACKSTEP k / ADVANCE k ... FIRST+ OPAQUE", together with
    the S-3 disposition "FIRST+ is OPAQUE at every SEEK except a SPAN_COMMIT of the span in
    progress", has no island exemption. The table's preamble says "nothing else decides".
  - The text therefore contradicts itself. The critic took the rule-3/operand reading. The table
    reading is safe: F(arm 2) goes OPAQUE, and D declines.
  - The critic said the safe reading leaves rule 3's exemption as dead code. That understates it:
    the table never had that exemption.
- Under the critic's reading, F(arm 2) is built as follows:
  - Peeks: BRANCH, fork both. The false side is FAIL.
  - WORK: continue.
  - PUSH at scan_position: fork.
  - ADVANCE: member, continue.
  - SET: trailed.
  - CONSUME `z`.
  - Result: F(arm 2) = {z}, against F(arm 1) = [0-9], so D2 admits.
- Twin `V/isl5_twin.c`: rx_L2's `RX_PUSH(&&rx_L6, scan_position); goto rx_L4;` is replaced by `if
  (scan_position >= subject_length) goto rx_fail; switch (subject[scan_position]) { case 48 ... 57:
  goto rx_L4; case 122: goto rx_L5; default: goto rx_fail; }`.

  | subject | base | twin | libpcre2 |
  |---|---|---|---|
  | abz | 1 0:0,3 1:2,3 | **0** | = base |
  | abcz | 1 0:0,4 1:3,4 | **0** | = base |
  | abcdez | 1 0:0,6 1:5,6 | **0** | = base |
  | 12yz | 1 0:0,4 1:3,4 | same | = base |
  | zz, az | 0 | 0 | 0 |

- Also holds: no cell exercises ISLAND's FIRST+ row. The cell table has C5a/C5b for SPAN, and D1 is
  "the island's own rules".
- What the fix must do: put the opener on the path, and resolve the rule-3 versus kind-table
  contradiction in ONE place: membership requires the opener to have been met on the path.

## SOUND-6

**Verdict: HOLDS.** This is a mechanism gap, not a rule-as-written answer move. The consequence
twin reproduces.

- Typing: the design types both sites correctly. In `site_kinds.tsv`, 5018 is `BRANCH_FAIL`
  ("recorded as VE_NOTE (fewer than rmin iterations)") and 3889 is `BRANCH|BRANCH_FAIL`. The kind
  table and rule 2 handle a correctly typed BRANCH_FAIL. So the build as written moves no answer
  here. The finding is that the guarantee that should catch a MIS-typing (the r6 S-2 class) cannot
  see it.
- Signature table, quoted rows:
  - `goto <p>_fail` "1 if the record has an unwind edge, else 0";
  - `goto <p>_L` "the label edges the record lists";
  - `scan_position =`, `+=`, `++`;
  - `slot_values[`;
  - `run->`;
  - the six macros;
  - brace balance.

  No row counts `if (`, `case ` or `else`. FAIL and BRANCH_FAIL both have an unwind edge, so the
  signature is 1 for each.
- Re-emitted `V/mt.c` (`$B -p rx -o V/mt.c --features all --pattern '^(a)b+c'`, engine vm,
  `RX_VM_FRAMELESS 1`, no `RX_PUSH`):
  - `if ((ptrdiff_t)rx_span_cursor < (ptrdiff_t)scan_position + 1) goto rx_fail;` (from
    `emit_vm.c:5018`);
  - `if (RX_PRUNE_TOO_SHORT(rx_span_cursor, 1)) goto rx_fail;` (`vm_mrl_test`, `emit_vm.c:3889-3891`).

  Each has 1 `goto rx_fail`, 0 `goto rx_L`, no `slot_values[`, no `scan_position =`/`+=`/`++`, no
  `run->`, no macro of the six, and brace balance 0. That is exactly FAIL's signature, so typed FAIL
  they raise no mismatch and no V0.
- Consequence, under the rows as written once the site is typed FAIL:
  - FAIL means "path ends", so ACCEPT is unreachable after the rung.
  - The program has no PUSH, so no resume edge reads the slots.
  - Both group-1 SETs are dead, and V3 deletes them.
- Twin `V/mt_twin.c` deletes the two `RX_SET(RX_SLOT_GROUP1_*)` lines:

  | subject | base | twin | libpcre2 |
  |---|---|---|---|
  | abbc | 1 0:0,4 1:0,1 | 1 0:0,4 **1:-1,-1** | = base |
  | abc | 1 0:0,3 1:0,1 | 1 0:0,3 **1:-1,-1** | = base |
  | ac, xabc | 0 | 0 | 0 |

- The same blindness covers BRANCH vs GOTO and CASE vs GOTO: each prints one `goto <p>_L` in both
  typings. The island's compares are VE_GOTO today (site_kinds 4657/4669/4678 "recorded as
  unconditional VE_GOTO"). Sabotage (ii) as designed (the back-step as LSET) is detected only through
  the cursor token, so the sabotage set does not cover this class. Overlap: FIX-6 (the alphabet
  cannot see local writes / `&&` edges) is the same root, a chosen token list; see FIX-6.

## SOUND-7

**Verdict: HOLDS.** It sits between the two classes: the design declares the kind (row "snapshot
entry j of call c ... V1") but gives it NO print site, so the slip comes from the design's own
survey typing, and no check would catch it. It is caught only at the answer level, by C6.

- Code (`emit_vm.c:8222-8225`): `vm_call` writes each snapshot entry as `vm_set(v,
  a->u.call.save[j], vm_slot_ref(v, a->u.call.save[j]), "park this activation's value on the trail
  (a trailed SELF-write)")`. `vm_set` (`emit_vm.c:3579-3592`) prints through its two `pcrec_sb_printf`
  lines, 3584 and 3586, which are the same lines every capture SET uses.
- Design text: survey "one each: SET (two spellings)". `site_kinds.tsv` has "3584 vm_set SET OPGAP"
  and "3586 vm_set SET OPGAP", and no row anywhere is typed snapshot. The kind table has the snapshot
  row (V1, "Never COPY, never UNTRAIL") and the SET row ("gen s == t iff e is `slot[t]`"; V3 DEAD, V4
  COPY). The `vm_stmt` operand list has no snapshot or "call site" operand. The signature cannot
  separate the two: both print one `<P>_SET(` and one `slot_values[`. The role text is the only
  difference, and SLOTS-5 forbids it as an input.
- Rule as written with the survey's typing: each entry is `SET s <- slot[s]`, so "s == source" holds
  trivially on every path, and V4 deletes it (or V3 does first, where s is dead after). V1's first
  match never applies because no record has the snapshot kind.
- Re-emitted `V/c6.c` (`--features all --engine=vm -fno-splice-calls`, `^(x(?>a(?1)?b)y)$`): two
  `RX_CALL`s, each followed by four self-copies, eight in all
  (`RX_SET(RX_SLOT_GROUP1_START, slot_values[RX_SLOT_GROUP1_START]);` etc., lines 287-290 and
  335-338). Twin `V/c6_twin.c` deletes all eight:

  | subject | base | twin | libpcre2 |
  |---|---|---|---|
  | xaby | 1 0:0,4 1:0,4 | same | = base |
  | xaxabyby | 1 0:0,8 1:0,8 | 1 0:0,8 **1:-1,8** | = base |
  | xaxaxabybyby | 1 0:0,12 1:0,12 | 1 0:0,12 **1:2,12** | = base |
  | xay, xaxaby | 0 | 0 | 0 |

  These match the critic's numbers and r6's S-6 twin.
- Not an escape: C6 (gate 2d) compares answers, so it would be red. Its NAMED sabotage, though, is
  "original ordinals", not this slip, and the S-6 codegen assertion compares kept SNAPSHOT lists
  that would then be empty. The fix needs both: a kind source at `vm_call` (an operand or a
  `vm_snapshot` writer) named in the survey, and a "self-copy is never COPY" clause.

## SOUND-3 (= FIX-3)

**Verdict: HOLDS.** It is structural and latent in production today. The test-level red is SUSPECTED
from the arithmetic; I did not run it, because running suites is barred. One check covers both
SOUND-3 and FIX-3.

- Design text:
  - "Delegated writers write fragments": "That buffer is Job-owned ... and carries the body's comment
    setting (`pcrec_sb_comments`, set beside `vmsb`'s in compile.c). So kit comments strip
    identically."
  - Hazard table: "comment-tier stripping in fragments | the fragment buffer is set by the same
    `pcrec_sb_comments` call as `vmsb`".
  - Nothing else is said about the buffer's records. The survey also counts the "`PCREC_SIMD_WITNESS`
    block (test build only) | 1 | 1 | no record" without saying which writer prints it once
    `emit_vm.c` cannot name the body.
- Review tree:
  - `src/core/internal.h:376-436`: StrBuf carries `cmt_dropped` ("every LENGTH-BASED DECISION
    reads `pcrec_sb_len_uncut` ... that is emitted CODE moving over a comment switch, which is the
    one thing this axis promises never to do"), `simd_open/simd_at/simd_guarded/simd_size`,
    `layout_bytes`, `scaf_*` and `abort_over`.
  - `src/core/sb.c` has `pcrec_sb_len_decide` = `len_uncut - simd_guarded - layout_bytes -
    scaf_guarded`. `pcrec_sb_splice` carries simd/scaf/layout, and its own comment says
    "`cmt_dropped` is deliberately NOT carried".
  - `emit_vm.c:10962` reads `en->program_bytes = pcrec_sb_len_decide(&job->vmsb);`.
  - `src/core/compile.c:3205-3218` checks the balance over `{ &csb, &hsb, &vmsb, &scr_test }`
    only.
  - `compile.c:2357-2366` states the rule that every Job StrBuf gets `.cx` (L8-F1), and
    `compile.c:2427-2446` holds the `abort_over` arming ("a buffer the caps count is a buffer the
    trial's bound covers").
- Witness path (FIX-3), checked in code:
  - `emit_vm.c:10373-10377` writes `v->b = &job->vmsb;` and then `#ifdef PCREC_SIMD_WITNESS
    pcrec_memfn_simd_witness(v->b);`.
  - `memfn_sites.c:345-366` writes a SIMD bracket around a NONESSENTIAL comment, "so the bracket
    counts muted bytes".
  - If those bytes reach the body via a fragment plus `pcrec_sb_splice`:
    - the body's `simd_guarded` gains the muted bytes (uncut unit), but its `cmt_dropped` does not;
    - so `len_decide(vmsb)` comes out short by the muted bytes at the default `-fno-comments`;
    - so the `RX_VM_PROGRAM_BYTES` stamp moves, and the witness check (`tests/memfn/run_simd_guarded.sh`
      header: "every length DECISION (the VM entry-shape knee and VM_PROGRAM_BYTES ...) reads the
      SIMD-off length") would go red.
  - The arithmetic holds. The red is SUSPECTED; I did not run it.
- The FIX-3 addendum (mid-line bracket) HOLDS as a hazard.
  - `sb.c:206-213`: `pcrec_sb_simd_open` refuses "a bracket opened mid-line" by reading the byte
    before it in the SAME buffer.
  - The run compare is printed mid-line (`vm_lit`, `emit_vm.c:8980-8984`: `"if (scan_position + %d
    <= subject_length && "`, then `vm_run_compare(v, v->b, ...)`).
  - A fresh fragment buffer starts with `len == 0`, so the check passes. The splice re-checks
    nothing about line position.
  - This is latent: there is no SIMD form at a VM run site today.
- Soundness's probe ("no VM body site writes a kit comment region or SIMD bracket at the base") is
  consistent with the code: the kit's writers (`memfn/src/runcmp.c:472` cmt_open,
  `ofsskip.c:559-599` simd_open) are reached on whatever sink they are handed.
- Severity: maintenance/design. The production direction is an emitted-code move across
  `-fno-comments` or `-fmemfn-simd` once a kit row prints a comment or a bracket at a VM site.

## SOUND-4 (~ FIX-5)

**Verdict: HOLDS** on all six items. Items (i) and (vi) depend on which text the counter reads, and
the design states neither. Every item fails toward V0, so no answer moves. Item (i) moves emitted
CODE across the comment axis.

- Design text: "The primitive counts these tokens in the text it prints (fragments included) with
  `strstr` loops". The rows:
  - "`goto <p>_fail` | 1 if the record has an unwind edge, else 0";
  - "`return` | the record's give-up/abort/return exits";
  - "`run->` assignments, `--run->` | the declared run-state writes";
  - "brace balance | 0, except +1 for GUARD/SWITCH openers, -1 for their ends";
  - the S-1 disposition: "Single-line guarded writes (`if (c) x = y;`) record GUARD, the statement
    and GUARD_END with no printed brace".
- (i) `return` in comment text.
  - `vm_lbl` (`emit_vm.c:3464-3468`) prints `// %s` inside a NONESSENTIAL comment region.
  - The roles come from `emit_vm.c:8227` ("the call returned; continue here") and 8469 ("the callee
    region for %s returns").
  - Re-emitted with `-fcomments`, each matcher has `return` inside comment lines:
    - `V/lbc.c` (`^x(?<!ab|c)y(a+)\1`): two "... a disagreement returns HARD" lines, plus "The VM
      returns here immediately";
    - `V/c6c.c` (`^(x(?>a(?1)?b)y)$ -fno-splice-calls`) and `V/k2ac.c` (`^(?:(?1)y)*(a|b)$`):
      "// the call returned; continue here", "// the callee region for a capture group returns".
  - Default `V/k2a.c` has 0 comment lines in the matcher.
  - So whether the function is V0 depends on `-fcomments` if the count reads the written bytes, and
    every linked-call program is V0 if it reads pre-mute text. The first moves D and the verdicts
    across the comment axis (`internal.h:379-392` "the one thing this axis promises never to do").
- (ii) BREF prints two `goto <p>_fail`. Re-emitted `V/bref.c` (`^(a)\1$ --engine=vm`) has `if
  (ref_start == PCREC_UNSET) goto rx_fail;` and `if (took < 0) goto rx_fail;` in one compound (the
  emitter at `emit_vm.c:8847-8875`, two `vm_ev(VE_FAIL)`). That is 2 against the row's "1". It also
  has three `slot_values[` for two slots, which is ambiguous against "reads recorded".
- (iii) `run->` reads cannot be told from writes by `strstr`.
  - VAR reads `run->var_value[%d], run->var_length[%d]` (`emit_vm.c:8921`).
  - The callout give-up edge prints `{ run->callee_gave_up = 1; return r; }` (`emit_vm.c:9151`).
  - The UNWIND text holds `if (run->resume_depth == 0)`, also a read.
- (iv) Brace-free single-line GUARDs. Re-emitted `V/brace.c` (`^\{(a|"x\}")*\}$ --engine=vm`) has
  `if (!rx_revdet_group_seen[0]) rx_revdet_group_span[0][1] = (ptrdiff_t)rx_rv0_cursor;` and `if
  (rx_rv0_prev_position < 0) rx_rv0_prev_position = (ptrdiff_t)rx_rv0_cursor;`. Each counts 0 against
  the brace row's +1 (GUARD) and -1 (END).
- (v) Exits hidden in macro bodies.
  - `V/bref.c` defines `RX_CHARGE_WORK` with `if (run->work_left < 0) return RX_R_WORK;`, and the
    WORK row lists "exit (R_WORK)". So its text shows 0 `return` against 1.
  - `RX_SET` (via `RX_TRAIL`), `RX_PUSH` and `RX_CALL` return `RX_R_FRAMES`, but their rows list no
    exit. So the rows are inconsistent unless "return" means declared text tokens, not edges.
- (vi) Trace. `emit_vm.c:13295-13305`: under `--trace` the accept line reads `slot_values[0]` (when
  `\K` exists) and the backtrack line reads `run->resume_depth, run->trail_depth`. The frame rows
  declare no reads, so the function is V0 only when traced.

## FIX-5

**Verdict: HOLDS** on items 1-4 and 6-7. Item 5 is PARTLY: the text admits a reading in which it
does not occur.

- 1 = SOUND-4 (i); the same artifacts were checked.
- 2: `scan_position =` is a prefix of `scan_position ==`.
  - `V/bref.c` has `if (scan_position == 0) goto rx_L2;` and `if (scan_position == subject_length
    || ...)`; every `^`/`$` VM artifact has such a line.
  - The design's cursor row ("`scan_position =`, `+=`, `++`") would count each as a cursor write on
    a BRANCH (0).
  - The same applies to `run->` against `if (run->resume_depth == 0)`.
- 3: the frame rows carry tokens and the design leaves their counts unstated.
  - The fail label in every artifact holds two `return`, `--run->`, `scan_position = run->...`,
    `slot_values[`, `goto *` and a brace block.
  - The kind table's frame row has reads "—", exits unlisted, and no signature.
  - The token table does name UNWIND for `goto *` and `run->`, so the claim is "partly declared,
    partly not", not "no signature".
- 4: the embedded checkpoint.
  - `emit_vm.c:3516-3524` (`vm_jump`) returns `{ <TRAIL_CHECK> goto L; }`, used as a BRANCH's
    target text at 6600-6601.
  - Re-emitted `V/ej.c` (`(a|)*b --engine=vm`) has `if ((ptrdiff_t)scan_position !=
    slot_values[4]) { RX_TRAIL_CHECK(); goto rx_L0; }`.
  - The BRANCH row owns no `_TRAIL_CHECK(`, and CHECKPOINT is a separate kind. So it is a mismatch
    unless an operand is added.
- 5: verdict-dependent text.
  - Step 4 "unless the verdict is DELETE, print"; step 5 "count the text's tokens". If "the text" is
    the formatted text, which is computed whether printed or not, a tombstone counts the SET's own
    tokens and matches.
  - A SETU retag prints `RX_SETU(`, which does not contain `RX_SET(`. `strstr` needs `(` right after
    `SET`.
  - So: the retag half HOLDS; the tombstone half holds only under the printed-bytes reading.
- 6 = SOUND-4 (iv).
- 7 = SOUND-4 (ii).
- Legacy-column note: `vm_work_at` (`emit_vm.c:3650-3656`) returns before its `VE_NOTE` when
  `!v->has_budget`, so BREF's legacy op list is conditional. HOLDS.
- Direction: every item is safe for answers. Each makes (a)'s "card 0m: 0 mismatches, 0 V0" red on
  today's corpus/flags (items 2 and 7 on every `^` and every backreference pattern).

## SOUND-5 (~ FIX-4 items 4 and 5)

**Verdict: HOLDS.** The counts hold, and so do both mismatches.

- Counts I re-derived:
  - `grep -c '\bvm_ev(' src/gen/emit_vm.c` = 55, which is the definition at 841 plus **54 calls**.
  - `vmcons2_evidence/body_print_sites.tsv` has **132** rows.
  - `site_kinds.tsv` has 132 rows minus FRAG 34 (30 fragments + 4 span-block lines), COMMENT 6 and
    POSTPASS 1, which leaves **91** sites.
  - Of those, BRANCH 20 + `BRANCH|BRANCH_FAIL` 1 = 21, BRANCH_FAIL 9, LSET 15, SEEK 6, GUARD/END 6/6,
    as the design states.
  - The 4 delegated writer calls are at `emit_vm.c:1688`, 4555, 4839 and 9153, and the SIMD
    witness at 10376.
  - I did not re-derive the 23 frame calls or the 31 raw `slot_values[` formats independently; I
    rely on the critic's function-aware scan there.
- Mismatch 1. Design guard 2: "outside `vm_stmt.c`, `vmsb` appears only in compile.c's two lines".
  `src/core/compile.c` names `vmsb` on FIVE code lines:
  - 308 `pcrec_sb_free(&cx->job->vmsb);`
  - 2365 `cx.job->vmsb.cx = ...`
  - 2385 `pcrec_sb_comments(&cx.job->vmsb, cmt);`
  - 2435 `cx.job->vmsb.abort_over = st_bound;`
  - 3206 the balance-check array

  Lines 2428 and 2440 are comments. Outside compile.c, `vmsb` also appears in `internal.h:3528`
  (`StrBuf vmsb;`, plus comments at 383, 3530, 3533) and in `limits.def:282` (a comment), and in
  `emit_vm.c` at 10373 and 10962 plus comments. The design also writes "src/compile.c"; the file is
  `src/core/compile.c`. As written, the guard is red on day one, or gets rewritten ad hoc.
- Mismatch 2. The design's line "The body text is then exposed READ-ONLY: `vm_stmt_body_text()`
  for `vm_cls_reads` and `pcrec_sb_len_decide`" is wrong for len_decide. `pcrec_sb_len_decide(const
  StrBuf *)` (`src/core/sb.c:303-310`) reads `cmt_dropped` (via `len_uncut`), `simd_guarded`,
  `layout_bytes` and `scaf_guarded` along with the open-bracket state. Text cannot supply these. The
  frame's `pcrec_sb_splice(c, v->b)` (`emit_vm.c:13270`) also needs the StrBuf. So vm_stmt.c must
  export `len_decide` and `splice_into` entry points, or the grep guard's "no `StrBuf *` getter"
  breaks.

## FIX-4

**Verdict: HOLDS** on all five items and the addendum. The design's "by construction" holds only
for the `Vm.b` field. It is not a compile error for any other route to the body.

- 1. The kit calls stay in emit_vm.c with a `StrBuf *`:
  - `pcrec_memfn_emit(v->cx, DELEG_VMRUN, s, &h, b)` (4555) and `(..., id, s, &h, b)` (4839);
  - `pcrec_clskit_emit_inline(b, ...)` (1688);
  - `pcrec_callsite_emit(cx, b, ...)` (9153).

  The design says "No kit change: the hook signatures already take a `StrBuf *`" and "handed the
  primitive's fragment buffer". Then either emit_vm.c holds a `StrBuf *` to the fragment, which guard
  (2)'s "no `StrBuf *` getter in `vm_stmt.h`" forbids, or the calls and their site builders move
  into vm_stmt.c. The design states neither. HOLDS.
- 2. `vm_cls_test` (1685), `vm_run_compare(Vm *, StrBuf *b, ...)` (4545) and `vm_ctx_side` (8542,
  per the critic) print into a caller-chosen `StrBuf *`. Guard (2)'s third bullet names only the
  three kit entry points. HOLDS (all three signatures read: `vm_cls_test(Vm *v, StrBuf *b, ...)`
  1685, `vm_run_compare` 4545, `vm_ctx_side(Vm *v, StrBuf *b, ...)` 8542).
- 3. The frame is written into csb. `vm_emit_search_body` (from 12948; `StrBuf *c = &job->csb`)
  prints the head and locals, splices the body (`pcrec_sb_splice(c, v->b)`, 13270), then the
  accept/fail text. `grep -c 'pcrec_sb_[a-z_]*(c,'` gives 221 calls on `c` in emit_vm.c. A raw print
  into csb inside the matcher span is therefore not a compile error. The design's "frame writers
  move into vm_stmt.c" is convention, not structure. HOLDS.
- 4 and 5: see SOUND-5.
- Addendum. `Job` is a complete type in `src/core/internal.h` (vmsb at 3528), and emit_vm.c
  includes `core/internal.h` (line 62). It already reaches Job buffers through the context:
  `&v->cx->job->scr_test` (4933), `&cx->job->scr_desc` (9697, 10006, 10015), `&v->cx->job->csb`
  (12729 and seven more), `&job->vmsb` (10373, 10962). So `pcrec_sb_printf(&v->cx->job->vmsb, ...)`
  still compiles once `Vm.b` is opaque. "A raw `pcrec_sb_printf(v->b, ...)` is a compile error" is
  literally true, but only for that one spelling. The backstop is the grep, whose `vmsb` line list
  is wrong (item 5). HOLDS.

## FIX-1

**Verdict: HOLDS.** It is structural and safe for answers. Gate (a)'s "card 0m: 0 mismatches, 0 V0"
is red by design on a corpus pattern.

- Design text:
  - "brace balance | 0, except +1 for GUARD/SWITCH openers, -1 for their ends";
  - "Kit text is free to contain `if`/`while`/its own locals but no token above beyond its row's
    declaration";
  - "counts these tokens in the text it prints ... with `strstr` loops" ("a count, not a parser");
  - gate (a): "card 0m (census: 0 mismatches, 0 V0)".
- Witness:
  - I decoded `tests/recursion/cscan.rxt:20` (`pattern-esc`) myself with the format's seven escapes
    plus `\xHH`. The result is byte-identical to the critic's `cscan.pat`.
  - Compiled: `$B -p rx --features recursion,named-groups,conditionals,modifiers,classes,atomic-groups,lookaround,assertions
    -o V/cscan.c --pattern "$(cat V/cscan.pat)"`. Engine "vm", matcher `rx_match_anchored` from
    line 416.
  - Line 433, one CONSUME(LIT) statement:
    `if (scan_position + 3 <= subject_length && rx_w2(subject + scan_position) == rx_w2("(\?") &&
    rx_w2(subject + scan_position + 1) == rx_w2("\?{")) { scan_position += 3; goto rx_L5; }`
  - `strstr` counts 2 `{` (one inside `"\?{"`) and 1 `}`, so the balance is +1 against CONSUME's 0.
    That is a mismatch, and the function goes V0.
- Second witness:
  - Re-emitted `V/brace.c` (`^\{(a|"x\}")*\}$ --engine=vm`).
  - Line 44 is a BRANCH:
    `... rx_w2("x}") && rx_w2(subject + scan_position + 2) == rx_w2("}\"")) goto rx_L19;`
  - Its balance is -2 against 0.
- The text comes from the kit run compare (`vm_run_compare` -> `pcrec_memfn_emit(DELEG_VMRUN, ...)`,
  `emit_vm.c:4545-4556`). So what the user writes in the pattern decides V0, and with it D and the
  verdicts in (c).
- Direction: V0 (safe). The defect is the gate (red at landing) and the pressure to tune the alphabet.
  The fix is to count outside string and char literals and comments.

## FIX-2

**Verdict: HOLDS**, including both addenda.

- Design text:
  - "Checkpoint placement and the D183 margin follow walk 3's `nset` (KEEP sites only) with no
    second mechanism";
  - K2: "`{k: DELETE}` (and ... `{k: UNTRAIL}`) changes EXACTLY the line(s) of record k in the C and
    its record's op in the listing";
  - K2a: "walk 3 drops it [the rx_L7 checkpoint]".
- Code:
  - `vm_set` does `v->nset++` (`emit_vm.c:3591`), and `vm_lbl` stamps `lbl_nset[id] = v->nset + 1`
    (3480).
  - `vm_jump_closes_trail_cycle` compares `lbl_nset[id] <= v->nset` (3512).
  - The margin is printed into `<p>_trail_gc_floor` as `"    const size_t margin = %lld;\n"` with
    `v->nset` (12880-12886).
- Re-emitted `V/k2a.c` (`--features all --engine=vm -fno-splice-calls`, `^(?:(?1)y)*(a|b)$`):
  - 12 `RX_SET(` sites (13 lines with `RX_SET(`, minus the macro definition);
  - line 161 `const size_t margin = 12;`;
  - `RX_TRAIL_CHECK();` at 280 and 313.
- Consequence: any one-entry DELETE (or UNTRAIL, if "KEEP sites only" counts trail writes) makes
  walk 3's nset 11, so line 161 changes too. That is a second changed line which is not record k's,
  so K2 as written is red on a correct build.
- Addendum 1:
  - The restores in `V/k2a.c` read `run->trail[run->resume_stack[run->call_top].trail_mark +
    0/1/2].saved_value` (lines 310-312). They pair with the three snapshot SETs at 270-272.
  - Under the S-6 sentence ("a kept restore reads its snapshot at its ordinal among the KEPT
    entries of its own site"), a one-entry DELETE of snapshot START re-numbers `+1`/`+2` to
    `+0`/`+1`. That is three changed lines for one record. K2 is "for every SET site k", and snapshot
    entries are SET-printed sites.
- Addendum 2:
  - `vm_emit_guarded_matcher` (`emit_vm.c:12727-12750`) writes a second full text copy of the matcher
    when `PCREC_ITER_NEEDS_GUARDED`.
  - So a one-entry change appears twice. "The line(s) of record k" must be defined over both copies.
- Embedded checkpoint (the critic's third shape): `vm_jump`'s `{ RX_TRAIL_CHECK(); goto L; }`
  (`emit_vm.c:3516-3524`; seen in `V/ej.c`) is BRANCH text. A placement change there alters a BRANCH
  line elsewhere.

## FIX-6 (~ SOUND-6)

**Verdict: HOLDS** for the structural blindness, the CALL-successor point and the R addendum. Holds
PARTLY for the `&&` miscount, which depends on whether a PUSH's resume label is a "label edge". There
is no answer witness; the unsafe direction is argued, not shown.

- Design text, the token table: `goto <p>_L`, `goto <p>_fail`, `goto *`, `return`, `slot_values[`,
  `scan_position =`/`+=`/`++`, `run->`, the six macros and braces. It has no token for a local
  (`<p>_span_cursor`, `<p>_rv<i>_*`, `<p>_revdet_group_*`) and none for `&&<p>_L`. Other lines:
  - non-effect rule: "The live clause binds locals (LSET)";
  - sabotage (ii): "the back-step printed as an LSET: the census red".
- Locals:
  - Every LSET text has zero signature tokens, for example `rx_span_cursor = scan_position;`
    (5159), `rx_span_cursor -= 1;` (5225), and `rx_rv0_prev_position = ...` in `V/brace.c`. So an
    LSET recorded as COMMENT (or any zero-signature kind) passes with 0 = 0.
  - The LSET and COMMENT rows differ in FIRST+ ("continue iff non-effect" against "continue") and
    in writes. A non-dead local write mistyped as COMMENT would therefore slip D's live clause.
  - That is the unsafe direction, in principle. The design's sabotage (ii) is detected only
    through the CURSOR token in `scan_position = rx_back_step(...)`, which is the alphabet point.
- `&&` edges:
  - `vm_push_at` prints `RX_PUSH(&&rx_L%d, pos)` (`emit_vm.c:3555-3561`) and `vm_call` prints
    `RX_CALL(&&rx_L%d, scan_position)` (8217); neither contains `goto rx_L`.
  - The PUSH row's successors are "next, L". If "label edges the record lists" includes L, the
    count is 0 against 1 on every PUSH and CALL, so V0 everywhere.
  - If it means only goto-edges, nothing is wrong. The text does not say which.
- CALL successor:
  - Re-emitted `V/k2a.c` 269-273: `RX_CALL(&&rx_L10, scan_position);`, three snapshot `RX_SET`s,
    then `goto rx_L2;`.
  - The callee edge is a separate GOTO after the snapshot entries, so the CALL row's "callee entry"
    successor is wrong as printed. The snapshot row's "next" already assumes this order. HOLDS.
- R addendum (design text):
  - The (b) gate says "no `run->(resume_depth|trail_depth|call_top|steps_left|work_left)` outside
    the write-back and reload brackets". After R, `run->resume_depth = %s_frame_mark;` (CUT_LOCAL,
    `emit_vm.c:5849`, 5990) and `--run->steps_left` (STEP, 9087) are spelled on locals. The `run->`
    token that tells them apart from an LSET is gone.
  - A cut mistyped as LSET then passes, and FIRST+ would "continue iff non-effect" through a cut
    instead of going OPAQUE.
  - (b)'s cost row says "R's change list is the rows whose text reads `run->`" and omits the
    signature re-declaration. HOLDS.
- Overlap with SOUND-6: one root, a chosen token alphabet that cannot see a mis-typing class.
  SOUND-6 is the conditional class (with a consequence twin); FIX-6 is the locals and `&&` class.

## FIX-7

**Verdict: HOLDS** on the design text. 0k's prototype half stays SUSPECTED; the critic could not
read rev 1's prototypes and neither did I (denylist).

- 0n:
  - Design: "the prototypes' graph builder ported to read (a)'s RECORDS ... then the full rule set
    run both ways over the corpus | every verdict and every D admission identical in both; a
    disagreement is an input gap in the records: stop and report", and standing question 2: "card
    0n's text-vs-record agreement is a second implementation over a DIFFERENT input".
  - The builder is rev 1's text prototype (F12: "the text checker becomes card 0n's text
    prototype"). r6's headline lists S-1, S-2, S-3 and S-5 as answer twins of that model, so the
    model is wrong in exactly those rows.
  - Either the text side keeps rev 1's rows, and a correct record stream disagrees on C1-C5 and the
    card blames the records, or it is revised to rev 2's rows, and both sides share one author's
    model.
  - The design says neither. Its triage is one-directional ("an input gap in the records"). HOLDS.
- 0m red by design: see FIX-1 and FIX-5, both verified above.
- 0k and G1:
  - The 0k card is "the full twin against stock, `_search_in` at ntrail 1..600", run in STEP 0 "on
    the prototypes". The stage gates 2a-2e (snapshot table) contain no ntrail sweep on the BUILT
    compiler. So the restated G1 give-up clause is checked only on prototypes. HOLDS.
  - `tests/recursion/framebuffer.rxt:25-41` documents the stamped default "2048/3072" for
    `^(a(?1)?b)$` (n = 764 needs "3,073 trail entries (of 3,072)"). So 1..600 does not reach the
    stamped trail capacity of that family. HOLDS.
  - G1's sentence 1 ("never ... at the stamped capacities") and sentence 2 ("Inside D183's gap band,
    a give-up at a given `ntrail` may move, in both directions") conflict wherever a stamped capacity
    lies in a pattern's gap band. The text states no precedence. HOLDS as a text gap. I did not
    construct a pattern whose stamped capacity is in its band.

## FIX-8

**Verdict: HOLDS.**

- Design: EXPECTED-MOVES "A moved cell NOT on the list is red; a listed cell that does not move is
  red too (the list is a manifest, never a count)", "checked against libpcre2 like card 0e"; "one
  `GIVEUP1_ALLOWANCE` row per moved cell per arm: the deny flag's arm, and the internal arm".
- No executor is named. `tests/vm/expected_moves.tsv` has no reader in the design after STEP 0:
  0e is a STEP 0 card, the stage gates run at landing, and no make-test section, script or mech row
  is named. `grep -rl expected_moves tests/ Makefile` in the review tree is empty, as expected for
  an unbuilt design. No libpcre2-absent rule is given either.
- Direction-blind lookup:
  - `tests/axes/run_axes.sh:1507-1518` reads `while IFS=$'\t' read -r cls key btrc bout atrc aout;
    ... _allowed="${GIVEUP1_ALLOWANCE[$flags|$relkey]:-}"`. The key is flags|file:line; `btrc` and
    `atrc` (which side gave up) are not consulted.
  - So a row written for "the arm gives up" also excuses "the default gives up", which is the
    build's new give-up that G1 forbids.
  - The header (648-656) defines GIVEUP1 as "exactly one side gives up". I found no
    listed-but-not-firing check: the grep of `GIVEUP1` in run_axes.sh shows only the lookup and the
    count line 1597.
- Per-arm rows that can never fire. This is inferred from the design's own mechanism split:
  - A D-moved cell (W6) does not move back under `--harness=keep-slot-writes`, because D stays on.
  - A slot-flow-moved cell (framebuffer cell 1) does not move back under the D deny.
  - So "per moved cell per arm" writes rows for arms that cannot produce the GIVEUP1. This holds
    for any cell moved by exactly one mechanism.

## FIX-9

**Verdict: HOLDS** as a design-text gap. The first example's reach is SUSPECTED.

- Design text:
  - V0 row: "KEEP (every site); D declines";
  - "From (c) on, a mismatch's effect is all-KEEP plus D declining";
  - walk table: walk 2 is skipped only when "D found no site, or D is denied", and walk 3 only on
    "no verdict, or the lever is on".
  - Nothing says what happens when a signature mismatch is first found in walk 2 (D already
    emitted) or in walk 3 (verdicts already applied). "D declines" is then no longer possible
    without a re-emission the walk bound does not count.
- (i) D2 says "every case goto through `vm_jump`". `vm_jump` returns `{ RX_TRAIL_CHECK(); goto L; }`
  when the jump closes a trail cycle (`emit_vm.c:3516-3524`; the shape is seen in `V/ej.c`). A CASE
  carrying it breaks the CASE signature (FIX-5 item 4), and walk 1 has no CASE.
  - Whether a D2 case target is ever an already-written label is SUSPECTED: arms are normally
    emitted after the switch. The design's own "(D183's cycle theorem)" suggests it can happen.
- (ii) The verdict-dependent text (FIX-5 item 5, the SETU retag) exists only in walk 3.
- The fix shape (walk-2 V0 re-emits walk 1; walk-3 checks verdict-aware, and a walk-3 mismatch is
  an internal error) is reasonable.

## FIX-10

**Verdict: HOLDS** (headers checked only, as briefed). All four family members exist:

1. `src/gen/emit_vm.c:3444-3447`: "THE FIVE PRIMITIVES. Every one of them writes C *and* records
   the listing event ... there is no other way to emit a label." The critic's aside "seven by now,
   3624-3631" is not at those lines: they hold the work-charge table. That is a minor citation slip.
2. `src/gen/stamp_kinds.c:4-6, 24-25`: "Every stamp the emitters write through the stamp
   primitives ... classified by WHAT IT IS A FACT ABOUT ... does not classify is an INTERNAL ERROR
   on a compound's shell".
3. `src/gen/callsite_rows.c:1-14`: "THE ROW ORDER IS THE EMITTED ORDER, first match".
4. `src/core/internal.h:450-455`: "The gate sits in `pcrec_sb_putc`/`pcrec_sb_puts`/
   `pcrec_sb_vprintf` ... so it cannot be bypassed by a helper", with the balance check at
   `src/core/compile.c:3205-3218`.

The general form and its unlocks were not judged, as briefed.

## Summary of verdicts

| id | verdict | class | note |
|---|---|---|---|
| SOUND-1 | HOLDS | answer, under a permitted reading (the PUSH row's "span cursor of the open SPAN") + cell reach | twin axz/aaxz NOMATCH; libpcre2 = base |
| SOUND-2 | PARTLY | opener off-path HOLDS; answer only under rule 3's island exemption, which the kind table's ADVANCE row ("OPAQUE") contradicts | twin abz/abcz/abcdez NOMATCH; libpcre2 = base |
| SOUND-3 = FIX-3 | HOLDS | structural, latent; witness-test red SUSPECTED (arithmetic) | |
| SOUND-4 ~ FIX-5 | HOLDS | structural; (i) moves code across `-fcomments` | FIX-5 item 5 PARTLY (tombstone half reading-dependent) |
| SOUND-5 ~ FIX-4 (4, 5) | HOLDS | doc/maintenance | five compile.c code lines, len_decide needs records |
| SOUND-6 ~ FIX-6 | HOLDS | mechanism gap (sites typed right in the design; the signature cannot catch a conditional fail typed FAIL) | consequence twin 1:-1,-1; libpcre2 = base |
| SOUND-7 | HOLDS | kind declared but given no print site; the survey types it SET; the signature cannot tell | twin 1:-1,8 / 1:2,12; caught by C6 answers (and likely the S-6 assertion) |
| FIX-1 | HOLDS | structural (gate 0m red by design) | cscan.rxt:20 line 433, brace +1 |
| FIX-2 | HOLDS | design (K2 red by design) | margin 12 line; S-6 renumbering; notempty copy |
| FIX-4 | HOLDS | design (structural claim is grep-only) | Job complete type, csb frame |
| FIX-6 | HOLDS (the `&&` miscount PARTLY) | design | no witness for the unsafe direction |
| FIX-7 | HOLDS (0k prototype half SUSPECTED) | design text | |
| FIX-8 | HOLDS | maintenance/design | run_axes.sh:1507-1518 direction-blind |
| FIX-9 | HOLDS (example (i)'s reach SUSPECTED) | design text | |
| FIX-10 | HOLDS (headers only) | | "seven by now, 3624-3631" citation slip |

Overlaps, each covered by one check: SOUND-3 = FIX-3; SOUND-4 ~ FIX-5 (comments/return, BREF's two
fails and the single-line GUARD found by both); SOUND-5 mismatch 1 = FIX-4 item 5, mismatch 2 =
FIX-4 item 4; SOUND-6 ~ FIX-6 (one root: the chosen token alphabet).

Not found by either critic, from my own reading of the design: SOUND-2's safe reading is not "dead
code" as soundness says. It is what the declared kind table already states (ADVANCE: OPAQUE; S-3:
"OPAQUE at every SEEK except a SPAN_COMMIT"). So the defect is that rule 3 and the summary contradict
the table, not that the table is unsafe.

## PROBED-AND-HELD

- Box use, all single and light: about 17 `build/pcrec` emissions (one refused: `--pattern-esc`
  wants a file), 9 gcc builds (the libpcre2 driver plus 4 bases and 4 twins), all before 15:10. No
  `make`, no suite.
- Answer twins rebuilt from my own emissions:
  - c5b: 5 subjects;
  - isl5: 6 subjects;
  - mt: 4 subjects;
  - c6: 5 subjects.

  Every base equals libpcre2 on every subject and span. Every twin moves exactly the spans the
  critics reported.
- Control: lazy rmin >= 1 (`^(?:[ab]{2,}?b|y)(z)`) prints the span block, so the SOUND-1 fix's
  replacement cell reaches a SPAN.
- Artifacts: `V/` = `/var/tmp/pcrec-pcrec/scratch/crit-vmcons2/verify/w/`, holding c5b.c, c5b_twin.c,
  c5c.c, isl5.c, isl5_twin.c, isl5.ir, mt.c, mt_twin.c, c6.c, c6_twin.c, lbc.c, c6c.c, k2ac.c, k2a.c,
  bref.c, brace.c, cscan.pat, cscan.c, ej.c, vd.c, vp2.c, vrun.sh.
- Denylist: no denied file was opened. I read the evidence dir's TSVs with shell tools, so no
  directory CLAUDE.md was injected. I read the r6 review's headings and rulings, which are allowed.

## STATE AT HANDOFF

- STATE: complete
- OWED: none

VERIFY COMPLETE
