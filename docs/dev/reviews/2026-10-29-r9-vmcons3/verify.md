# VERIFY — critic round vmcons3 (opus verifier), 2026-10-29

Started 15:37. Inputs: sound/sound.md (SOUND-1..8), fixind/fixind.md (FIX-1..12). Review tree
worktrees/crit-vmcons3 (B=build/pcrec). Every answer-level twin rebuilt from MY OWN emission; scratch
under verify/. Critic artifacts read but not trusted. No denied file opened (unless noted below).

## SOUND-3 — HOLDS (answer-level, rule-as-written twin for (c); no stock answer moves)

- Ran: `$B -p rx --features all -o verify/c8.c --pattern '^(a)b+c'` (my emission). The kit span window
  (pcrec_memfn_emit VMSPAN, emit_vm.c:4836-4839) is c8.c:268-271. Twin `verify/c8_twin.c`
  (diff `verify/c8_twin.diff`): the while condition gains
  `&& (__builtin_memset(slot_values + 2, 0xff, 2 * sizeof *slot_values) != 0)`.
- Lexer as written (my copy of the evidence frag_lex.py, scope = subject, subject_length,
  scan_position, slot_values, run, ctx, rx_span_cursor, rx_window_end; output rx_span_cursor):
  the twin window lexes CLEAN.
- Runs (drv.c, gcc -O1, watchdog): base `abbc` 0:0,4 1:0,1; `abc` 0:0,3 1:0,1; `ac` nomatch.
  Twin `abbc` 0:0,4 **1:-1,-1**; `abc` 0:0,3 **1:-1,-1**; `ac` nomatch. libpcre2 (p2.c, my build):
  `abbc` 1:0,1; `abc` 1:0,1; `ac` nomatch = base.
- ARGUMENT: the reading is the one the text admits. Design §"The lexer" R3 defines "read" purely by
  token shape (not followed by an assignment op/`++`/`--`, not preceded by `++`/`--`, not under unary
  `&`); `slot_values` followed by `+` is a read. R4 covers only `<p>_`/`<P>_` names, so
  `__builtin_memset` is outside every rule; R1's noreturn list does not name it. The supporting
  sentence "it cannot be passed an address of matcher state" is false: `slot_values` is itself a
  pointer (`ptrdiff_t *const slot_values = run->slot_values;`, c8.c:247). Also confirmed: the
  registry's "PURE" `decode` has an out-parameter (`$_decode(..., unsigned *cp)`,
  src/enc/enc_utf8.c:234-235). Did not re-run the critic's 15-row r3holes list; the one twin plus
  the decode signature suffice for the class.
- Blocks (c)'s V0 claim; for (a) only FL's coverage (no current kit text has the shape).

## SOUND-6 — PARTLY (the twin HOLDS; the argument is weaker than stated: the design text points at the first byte in rule 3, but the row itself does not)

- Ran: `$B -p rx -o verify/s6.c --pattern '^(?:((?:ab)+)c|bd)'` (default engine; VM program; the span
  is the VMSTRIDE block `subject[rx_span_cursor + 0] == 97 && subject[rx_span_cursor + 1] == 98`,
  s6.c alt 1 at rx_L7). My twin is a DIFFERENT D shape from the critic's (theirs fails the whole
  alternation unless the byte is `b`): a per-alternative skip at rx_L2,
  `if (!(scan_position < subject_length && subject[scan_position] == 98)) goto rx_L5;` before the
  fork's PUSH (F(alt 1) = {b} under the "class = seq[stride-1]" reading). Diff `verify/s6_twin.diff`.
- Observed (drv.c): base `abc` 0:0,3 1:0,2; `ababc` 0:0,5 1:0,4; `bd` 0:0,2 1:-1,-1; `abd` nomatch.
  Twin `abc` **nomatch**; `ababc` **nomatch**; `bd` and `abd` unchanged. libpcre2 = base on all 4.
- ARGUMENT: the SPAN row (snapshot line 287) reads "SPAN (opens id: class, min, stride) ... F ∪= class";
  rev 2's row (vmcons2_report.md:411) said "first-byte class". The stride operand travels beside
  "class", and the emitter holds the class as a per-position SEQUENCE (`vm_span_advance`'s
  `seq[0..stride-1]`, emit_vm.c:4784-4791), so "class" for a stride-k span is genuinely ambiguous in
  the row. BUT rule 3's third bullet (snapshot "Continuing after an opener can only ADD bytes to F
  (the opener already added the group's first-byte set)") states the intent: first-byte. So a careful
  builder would read seq[0]; the finding is a row-text regression whose unsafe reading moves answers,
  not a rule that forces the wrong reading. The broader claim (non-printing operands — ids, F,
  nullable, first-byte class, PUSH site kind — have no E1/RT detector) is correct by construction of
  the checks: they read text, and these operands do not print. Fix as the critic says (restore
  "first-byte (`seq[0]`)"; derive F from the rendered operand). Blocks (c) 2b, not (a).

## SOUND-8 — HOLDS (answer-level, rule-as-written twin for (c) 2c/2d; no stock answer moves)

- Ran: `$B -p rx --features all --engine=vm -fno-splice-calls -o verify/c6.c --pattern '^(x(?>a(?1)?b)y)$'`.
  My emission has two CALL sites (snapshots c6.c:287-290 and 335-338) and ONE restore block at the
  region exit `rx_L3` (360-363, ordinals +0..+3), shared by both callers.
- Delete map (V1/V2 by hand, the union over the two sites since the restores are shared): GROUP1_START
  and GROUP1_END are written at rx_L7/rx_L19 before any read after either return label, so their
  RESTOREs and both sites' SNAPSHOTs go; CUT_MARK1 (read by `RX_CUT(5)`/the WORK charge after rx_L25)
  and GROUP1_PENDING (read at L7/L19) are kept. Twins: `c6_twin_renum.c` (kept restores at +0, +1;
  `c6_renum.diff`) and `c6_twin_origord.c` (same deletions, kept restores at the ORIGINAL +2, +3;
  `c6_origord.diff`). In both, the kept SNAPSHOT slot sequence = the kept RESTORE slot sequence =
  [CUT_MARK1, PENDING].
- Observed (drv.c): base and renum identical: `xaby` 1:0,4; `xaxabyby` 1:0,8; `xaxaxabybyby` 1:0,12;
  `xay`, `xaxaby` nomatch. origord: `xaxabyby` **1:-1,8**; `xaxaxabybyby` **1:-1,12**. libpcre2 = base.
- ARGUMENT: the design states S-6 two ways. Snapshot line 342: "the kept SNAPSHOT list and the kept
  RESTORE list are the same slot sequence" — origord passes it. Disposition FIX-2 (line 143: "whose
  ordinal operand equals the rank among kept snapshots (enumerated, and the S-6 assertion checks it)")
  and cell C6 (line 670: "restores keep ORIGINAL ordinals (the S-6 assertion fires)") assume a form
  that checks ordinals. So the cell's sabotage claim is false under line 342's statement. The RESTORE
  row (277, "j = rank among the KEPT snapshots of its site") could be read as derived by the renderer
  (then the mis-typing is impossible), but V2 (336) calls it "a renderer operand", i.e. passed; the
  critic's fix (derive j at render time, state S-6 once) is right. Also note (supports FIX-9): in
  today's emission the restores serve every caller, so "rank among the kept snapshots of ITS SITE"
  is only well defined after the C-move.

## SOUND-1 / FIX-3 — HOLDS (structural; no answer)

- Review tree src/gen/emit_vm.c:5159 `pcrec_sb_printf(b, "    %s_span_cursor = scan_position;\n", v->p);`
  (the rmin = 0 lazy arm's `else`) and emit_vm.c:5221 the same format string verbatim (the `again`
  label, retreat/extend resume). Evidence render_check.log rows 27 `lazy0 SPAN init_only 5159 MATCH`
  and 31 `resume LSET assign 5221 MATCH`; render_check.py:82/86 type them as different kinds.
- Design §"Why kind can no longer be wrong" (snapshot 219-221): "If it calls the wrong one, the
  program it emits is a different program. For (a) that is a red identity diff." False for this pair:
  same bytes, different kinds. M6 ("`VmLocal` excludes the cursor") does not save it — the excluded
  cursor is `scan_position`; `<p>_span_cursor` is an LSET target by render_check's own typing.
  M-table M1-M15 has no row for SPAN-init-only vs LSET. I did not re-run the critics' 47-template
  cross-collision scan; the pair itself is quoted above. Severity design/check; blocks nothing in (a)'s
  bytes, but the fix (a discriminator not read from text, e.g. "member with no opener" count) belongs
  in (a), where the typing is fixed.

## SOUND-4 — HOLDS (structural), one citation off by ~25-30 lines

- Macro exits (my c6.c prologue): `RX_TRAIL` line 131 `if (run->trail_depth >= run->trail_cap) return
  RX_R_FRAMES;` (RX_SET at 136 expands RX_TRAIL); `RX_PUSH` 140 and `RX_CALL` 152 `if (run->resume_depth
  >= run->resume_cap) return RX_R_FRAMES;`. Kind table rows (snapshot 274-280): SET "next", SNAPSHOT
  "next", RESTORE "next", PUSH "next, L", CALL "next (the SNAPSHOT records; ...)": no FRAMES exit.
  WORK (283) and STEP (284) do list their exit. M10 (690): "the macro is printed only by its kind's
  renderer, whose row lists the macro's exits" — false for SET/PUSH/CALL (and SNAPSHOT/RESTORE, which
  render through `<P>_SET`).
- CALLOUT cursor write: emit_vm.c:9082 `const bool pred = !a->u.callout.consume;` and 9146-9148
  `.succ = pred ? ... : vm_rolef(v, "{ scan_position += (size_t)r; goto %s_L%d; }", ...)` (the critic
  cited 9055 / 9141-9143; the facts are right, the lines are 9082 / 9146-9148). CALLOUT row (294)
  writes column: "slot 0 transiently (net none); `run->callee_gave_up` on the give-up exit" — no cursor.
  Today's columns are safe (FIRST+ OPAQUE at CALLOUT; an exit ends a path), as the critic says.
  Blocks (b)/(c) consumers of these columns, not (a).

## SOUND-2 — HOLDS (check domain; the "dead" part is true for the prototype and for the literal `<p>` reading; a lexer that keys on `v->p` and treats the lead byte as an identifier char would work, but the design does not say so)

- Review tree: src/core/internal.h:742-743 `#define PCREC_PREFIX_LEAD '\x01'` / `#define
  PCREC_PREFIX_PLACEHOLDER "\x01q"`; src/core/compile.c:2020-2021 `user_prefix = defo.prefix;
  defo.prefix = PCREC_PREFIX_PLACEHOLDER;` ("THE EMITTERS SEE THE PLACEHOLDER, NEVER THE CALLER'S
  PREFIX"); emit_vm.c:10374 `v->p = cx->opt->prefix;`; the rewrite is compile.c:3489-3497
  (`pcrec_sb_render_prefix` on csb/hsb/irsb at `facts_force`, "after every decision").
- Is the lexer necessarily run before the rewrite? YES as designed: builder step 5 (snapshot ~line 202)
  "Render it at once into the body ... then lex its fragment windows", and from (c) its refusal must
  set V0 during the walks, which all precede `facts_force`. So the lexer's domain is placeholder text.
- Probe (no compile; my `verify/ph.py` over my copy of frag_lex.py, `verify/ph.log`): four windows
  (label `&&L3`, unknown helper, prefixed-local write, `PUSH(&&L9,...)` macro). Final spelling `rx_`:
  all 4 REFUSED. Render-time spelling (`\x01q_`/`\x01Q_`), with p = `rx` or p = `\x01q`: all 4 CLEAN.
- The census (kit_census.sh lines 13-19) compiles to `.c` and lexes the FINAL file, so its 49/0/12
  never touched render-time text — confirmed by reading the script.
- Design text: §"The lexer" names `<p>_`/`<P>_` and never the placeholder. Unsafe direction (CLEAN
  instead of REFUSED). Fix: state the domain as render-time text with the placeholder as one
  identifier lead (or lex a rendered view); spell FL rows and CEN in that domain. Blocks (a)'s E5/FL
  as written (vacuous), and (c)'s V0.

## SOUND-5 — HOLDS (structural; check domain)

- Review tree emit_vm.c:1726-1764 `vm_cls_respell`: two strstr passes build `out`, then
  `b->len = 0; if (b->p) b->p[0] = 0; pcrec_sb_puts(b, out);` (1761-1763) — a truncate-and-regrow
  of the whole body. Called at 1830 (`if (respell) vm_cls_respell(v);`) from `vm_cls_tables`
  (def 1794), itself called at 14529, after the program is emitted. During the walk every table read
  is written in the SITE form (`vm_cls_read(v, VCR_SITE, ...)` at 1691 → `<p>_class_bitmap<ci>`,
  1648-1650); respell substitutes the ATOM/KIT form (1651-1656), a different length.
- Probe (1 compile): `$B -p rx --engine=vm -o verify/rs.c --pattern
  '[ac][bd][ce][df][eg][fh][gi][hj][ik][jl][km][ln]x'`: final text has 12 `rx_class_atomN(subject...)`
  reads and 0 `rx_class_bitmapN[` reads (e.g. rs.c:256). So the shipped CLS bytes are not what any
  renderer printed at record time, and every later record's `at`/`end` is stale against the final
  body. I did not re-run the gdb render-time dump; the code path above is unambiguous.
- Design: line 233-235 "A truncation (`b->len = 0`) is caught too", vs line 249 / 403-404
  "`vm_stmt_respell()` ... moved verbatim ... after the walk and after the tiling check" — the one
  truncation in the tree is exempted, unstated as an exception. E6 (line 428) "every record of E1's
  default population: 0 disagreements" does not say whether RT reads pre- or post-respell text.
- Nesting: BREF/VAR call `vm_work_at` mid-skeleton (emit_vm.c:8868, 8929); the design states the SID
  rule for a nested CHECKPOINT (536-538) but builder step 1's tiling assertion ("the previous record's
  `end`") has no rule while an enclosing record is open. Same-length overwrite: tiling compares
  lengths only (233-235), so "by any route" is over-claimed; agree with "appends and truncations".
- Blocks (a)'s E6 (domain unstated) and the "text is rendered from the record" claim for respelled
  CLS pieces; no answers.

## SOUND-7 — HOLDS (re-ran the slice on my own emissions)

- Ran: my `verify/c8.c` (default) and `$B -p rx --features all -fcomments -o verify/c8cmt.c --pattern
  '^(a)b+c'`; `python3 -I verify/slice.py verify/c8.c verify/c8cmt.c` (`verify/slice.log`, my script).
  The comment-stripped -fcomments body equals the default body (True), so the -fcomments offsets ARE
  the default body's uncut offsets. LABEL roles are muted NONESSENTIAL comments
  (`vm_lbl`: `pcrec_sb_cmt_open(v->b, PCREC_CMT_NONESSENTIAL); pcrec_sb_printf(v->b, "// %s\n", role);`)
  and muted bytes count in `cmt_dropped` (sb.c:383; `pcrec_sb_len_uncut` = len + cmt_dropped, sb.c:192).
- Observed: kit window text offsets in the default body [539, 678); uncut offsets [655, 794) (116 muted
  bytes before it). `[655, 794)` of the written default body = `cursor += 1; } } RX_CHARGE_WORK(...);
  if ((ptrdiff_t)rx_span_c` → lexer: `R4 unknown helper RX_CHARGE_WORK; R4 unknown helper rx_span_c`;
  the true window: CLEAN. Matches the critic's [655, 793) up to my regex taking one more byte.
- Design: Summary/record section ("Every record stores the body's uncut length (bytes plus muted
  comment bytes)") vs §"The lexer" ("C tokens of the fragment window `[at, end)` of the body") and
  "The domain is the same at every comment setting". Inconsistent as written. One-sentence fix (store
  text offsets too). Blocks (a)'s E5 as written.

## FIX-1 — HOLDS (structural, with my own witness)

- Review tree emit_vm.c:3579-3593 `vm_set`: prints `<P>_SET(...)`, then `v->emitted_set = true;
  v->nset++; vm_ev(v, VE_SET, ...)`. Snapshots call it (8222-8225, `vm_set(v, a->u.call.save[j],
  vm_slot_ref(...))`), region restores call it (8471-8477, `trail_mark + %d`). Readers: `lbl_nset[id] =
  v->nset + 1` (3480) and `vm_jump_closes_trail_cycle` (3510-3513: `lbl_nset[id] <= v->nset`); the
  margin print `const size_t margin = %lld;` with `v->nset` (12880-12886); `touches_storage =
  v->has_push || v->emitted_set` and `may_fwd = !touches_storage && ...` (11061-11065).
- Witness (1 compile): `$B -p rx --features all --engine=vm -fno-splice-calls -o verify/p1.c --pattern
  '^(?:(?1)b)*(a)$'`. Matcher: `rx_L4:` ... `RX_CALL(&&rx_L10, ...)` + three snapshots
  (body lines 19-22) ... `rx_L7: RX_TRAIL_CHECK(); goto rx_L4;` (30-31). In emission order the only
  `RX_SET`s between label rx_L4 and that back jump are the three snapshots (the callee region rx_L2..
  rx_L3 is emitted after), so the checkpoint exists only because snapshots bump `nset`. `margin = 12`
  (p1.c:162) = 3 snapshots + 3 restores + 6 ordinary SETs (counted).
- Design K2 (snapshot 555: "`nset` counts SET records whatever their verdict") and K4 (557: "equals the
  number of KEEP ... SET records of walk 3"); the counters row (412) says `nset`/`emitted_set` "move into
  the builders" without naming SNAPSHOT/RESTORE. Taken literally with SNAPSHOT/RESTORE as separate kinds,
  K4 is red on stock linked-call artifacts or, if the build obeys it, undercounts. Fix as the critic
  says (one population: trail-write records). Severity design; E1 protects (a).

## FIX-2 — HOLDS (structural); stronger than stated

- emit_vm.c:10962 `en->program_bytes = pcrec_sb_len_decide(&job->vmsb);`; 11710-11711
  `pcrec_sb_stampf(c, v->up, "VM_PROGRAM_BYTES", ...)`; 11097-11100 `if ((long long)en->program_bytes
  <= term) shape = may_fwd ? FORWARD : INLINE; else ... SHARED : PLAIN`; `may_fwd` reads
  `emitted_set` (11061-11065).
- Design K2 (555): "changes EXACTLY record k ... In the C, k's bytes change in the matcher and again
  in the notempty copy". `--harness=pin-nset` pins `nset` only. Design 545-548 lists FRAMELESS and
  `RX_VM_PROGRAM_BYTES` as walk-3 products.
- Stronger: every `{k: DELETE}` removes bytes, so the `<P>_VM_PROGRAM_BYTES` stamp line moves on EVERY
  one-entry DELETE map, not only near the knee; K2's C clause as written is red on any correct build.
  (Not compiled; follows from 10962/11710.) Blocks (c) 2a only.
- Side observation (supports FIX-9/SOUND-8): K2's pair entry `{(SNAPSHOT j of c, RESTORE j at R_c)}`
  assumes per-site restores; today the restore block is ONE per region, shared by every call site
  (my c6.c: two call sites, one restore block at rx_L3), so deleting "RESTORE j at R_c" for one c
  deletes it for all callers until the C-move exists.

## FIX-4 — HOLDS (structural)

- (i) Order, emit_vm.c: the walk, then `vm_cls_tables(&v);` (14529), `vm_plan_reseed`, the entry
  shape, then `pcrec_emit_prologue(cx, &g, v.ncaps, &pl.bufs, v.nlitrun > 0);` (14554),
  `vm_emit_stamps`, `vm_emit_storage` (the class tables, e.g. 13093 `static const unsigned char
  %s_class_bitmap%d[32]`). memfn/include/memfn.h:1346-1352: `mf_flush_helpers` "Writes, at file scope,
  every helper the art's rendered text has used ... an EXPR site only records them, so the caller
  flushes at a file-scope point ... (pcrec: its prologue". Design R4 (snapshot ~483-487): "The registry
  is the table the prologue's helper writers fill". So at step-5 lex time that table is empty; the
  build needs a second, walk-time list the design does not name.
- (ii) Respell: verified under SOUND-5 (1761-1763 truncate-regrow, after the walk, exempted from
  tiling at 403-404). (iii) Census domain: verified under SOUND-2 (kit_census.sh lexes the final `.c`).

## FIX-5 — HOLDS (structural)

- memfn/include/memfn.h:1144-1170 `mf_result`: `form_id[48]` (opaque), `handle`, `moved`, `reads_table`,
  `includes`, `cls`, `row[8]`. No helper names, no effect facts (the critic's field list omits `moved`
  and `row`; neither carries helper facts). Helpers reach the text only through `mf_flush_helpers`
  into a sink. So R4's purity rows for kit helpers are either a pcrec-typed list (the prototype's
  `PURE_HELPERS`/`PURE_PATTERNS`, frag_lex.py:43-48) or a new kit-contract fact. The D157/process
  framing is judgment; the structural fact holds.

## FIX-7 — PARTLY ((1) and (2) HOLD; (3) REFUTED)

- (1) `$B --list-axes` (`verify/axes.txt`): `#section memfn` at line 201, 14 `--memfn=no-NAME` rows,
  its own header saying "NOT pcrec axes" (memfn/src/options.def). E1 (snapshot 423) names "every
  deny/force arm `make test-axes` sweeps (`src/core/axes.def`)", which does not include these.
  HOLDS.
- (2) `deliver_n` is written in src/ only at src/parse/rxt_compose.c:1112; emit_vm.c:8400 loops on it
  (DELIVER SETs). E1's population is "every corpus `pattern`/`pattern-esc` line", which never runs
  composition. HOLDS.
- (3) The 60-byte prefix: REFUTED as a risk to (a)'s renderers. The emitters never see the user prefix:
  compile.c:2020-2021 sets `defo.prefix = PCREC_PREFIX_PLACEHOLDER` ("every length measured below ...
  is then the text at a canonical prefix length") and the real prefix is written only at
  `facts_force` (3489-3497), so new renderer code always prints the 2-byte placeholder; a fixed buffer
  in a renderer cannot see prefix length. (Part mode adds `__<role>`, also fixed per part.) E1's "both
  prefixes" suffices for the K38 class at renderer level.

## FIX-9 — HOLDS (structural)

- emit_vm.c:8502-8509: the region exit prints `const size_t <p>_call_frame = run->call_top;` ...
  `run->call_top = run->resume_stack[<p>_call_frame].call_top;` then `goto *...call_ret;`. The
  restores (8471-8477) precede it and read `run->resume_stack[run->call_top].trail_mark + j`, correct
  only BEFORE the pop. At R_c (after the indirect jump) `run->call_top` is the parent activation's, so
  the RESTORE row's renderer (snapshot 277, "(at R_c, ordinal j)", today's bytes) prints the wrong
  frame's trail mark there. The design says nothing about a `<p>_ret_frame` local or a spelling
  operand. Affects (c) 2c only.

## FIX-6, FIX-8, FIX-10, FIX-11, FIX-12 — not verified (judgment, per brief); cited-line sanity

- FIX-10: emit_vm.c:4620 `vm_ev(v, VE_ISLAND, entry, t->nbr, ...` and 5225/5232 span-cursor LSETs
  match. FIX-11: src/gen/stamp_kinds.c exists. fixind's HELD rows: compile.c:2362 `cx.job = calloc(1,
  sizeof(Job));` and rxt_compose.c:1084 `int slot = (int)cx->ncap + 1;` match. FIX-6/8/12 cite no
  lines needing checks. No wrong citation found.

## Summary of verdicts

| id | verdict | note |
|---|---|---|
| SOUND-1 / FIX-3 | HOLDS | 5159 and 5221 same format string, different kinds |
| SOUND-2 | HOLDS | render-time text is placeholder-spelled; lexer runs before the rewrite by design; my probe: 4/4 CLEAN render-time vs 4/4 REFUSED final |
| SOUND-3 | HOLDS | my twin: `abbc`/`abc` group 1 → -1,-1 (base and libpcre2 0,1); window lexes CLEAN |
| SOUND-4 | HOLDS | macro FRAMES exits + CALLOUT cursor write not in rows; CALLOUT lines are 9082/9146-9148, not 9055/9141-9143 |
| SOUND-5 | HOLDS | truncate-regrow after the walk; 12 atom reads in final text |
| SOUND-6 | PARTLY | twin moves answers (my per-alt dispatch: `abc`, `ababc` → nomatch), but rule 3 says "first-byte set", so the bad reading is admitted by the row only |
| SOUND-7 | HOLDS | 116 muted bytes; uncut [655,794) mis-slices the written body |
| SOUND-8 | HOLDS | my origord twin: 1:-1,8 / 1:-1,12; slot-sequence S-6 passes it; C6 cell's "S-6 fires" claim false under line 342 |
| FIX-1 | HOLDS | p1.c back-edge checkpoint exists only for snapshots; margin 12 |
| FIX-2 | HOLDS (stronger) | the PROGRAM_BYTES stamp moves on every DELETE map |
| FIX-4 | HOLDS | prologue/kit helper writers run after the walk |
| FIX-5 | HOLDS | mf_result carries no helper names/effects |
| FIX-7 | PARTLY | memfn arms and DELIVER (compose-only) hold; 60-byte prefix REFUTED (emitters see the placeholder) |
| FIX-9 | HOLDS | call_top popped before the indirect return |

No stock answer moves anywhere; every answer-level result is a rule-as-written twin for (c).
For (a)'s go: SOUND-2, SOUND-5, SOUND-7 (E5/E6/FL domains), FIX-1 (counter population), FIX-4 (registry
timing) and FIX-7 (1)(2) (E1 population) are the text fixes that bear on (a).

Budget: 6 pcrec compiles, 8 gcc builds (14 total), every matcher run under scripts/watchdog. No make,
no suites, no denied file opened. Read (not trusted) the critics' sound/stride/s_twin.diff and
sound/uncut/slice.py for method only; every result above is from my own emissions in verify/.

## STATE AT HANDOFF

STATE: complete
OWED: none

VERIFY COMPLETE
