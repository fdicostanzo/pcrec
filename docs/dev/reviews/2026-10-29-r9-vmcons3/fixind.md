# Critic fix-induced (fixind), round vmcons3 (design short re-check), 2026-10-29

Subject: docs/dev/lanes/vmcons3_report.md @ 62980551b (rev 3). Review tree worktrees/crit-vmcons3.
Question: what do rev 3's OWN changes newly break, leave unstated, or leave unproven.

## Findings

Probe artifacts (all in this dir): `p1.c` (`^(?:(?1)b)*(a)$`, `--features all --engine=vm -fno-splice-calls`),
`p2.c` (`^(?:abq|cdq|ce)*?z`, `--features all --engine=vm -fcomments`), `c5b.c` (`^(?:.*?x|y)(z)`,
`--features all -fcomments`). B = worktrees/crit-vmcons3/build/pcrec. 4 compiles in total (one refused for
missing `--features`), no gcc runs. emit_vm.c line numbers are the review tree's.

### FIX-1 SOUND-7 split SNAPSHOT/RESTORE out of SET; every "SET record" counter is left stated over SET only
- CONFIRMED (structural, with a witness). Severity: design, with a give-up hazard in (c) (G1 sentence 2).
  Effort S (wording). Blast radius: every linked-call artifact. Blocks (c)'s gates K2/K4; for (a) it is an
  implementation note that E1 catches.
- Today one primitive, `vm_set` (emit_vm.c:3579-3593), does all of these for the call snapshots
  (8222-8225) and the region restores (8471-8477): `emitted_set = true`, `nset++` and `VE_SET`. `nset`
  drives D183's checkpoint placement (`lbl_nset`, 3480; `vm_jump_closes_trail_cycle`, 3510-3513) and
  the printed `margin` (12886). `emitted_set` drives `touches_storage`/`may_fwd` (11061), so it sets the
  entry shape and FRAMELESS.
- Rev 3 makes SNAPSHOT and RESTORE separate kinds with their own builders. It then defines its
  counters over "SET records":
  - K2: "`nset` counts SET records whatever their verdict";
  - K4: "the `margin` constant equals the number of KEEP ... SET records of walk 3";
  - the "counters that steer emission" row says `nset`, `emitted_set`... "move into the builders",
    without saying which builders.
- Witness `p1.c`. The loop's back edge `RX_TRAIL_CHECK(); goto rx_L4;` (p1.c:281-282) exists ONLY because
  of the three SNAPSHOT lines 271-273: they are the only trail writes between `rx_L4:` (265) and the jump.
  `margin = 12` (p1.c:162) counts the 3 snapshots and the 3 restores (311-313) plus 6 ordinary SETs.
- Read literally:
  - In (a), a `vm_snapshot`/`vm_restore` that does not bump `nset` drops that checkpoint and prints
    `margin = 6`. E1 turns red, so (a) is safe if E1 reaches linked calls (it does: recursion corpus).
  - In (c), K4 as written is either red on every linked-call artifact (stock's margin includes them),
    or, if the build is made to agree with K4, the margin undercounts by 2|W| per call site and the
    back-edge checkpoints of call-only loops vanish.
  - K3 lets CHECKPOINT records "vanish freely" and K2 runs pinned, so the only control left is the
    4-shape ntrail sweep. The result: the trail fills between checkpoints, a new FRAMES give-up at a
    stamped capacity.
- Fix: name the population once, as "trail-write records" = SET, SNAPSHOT and RESTORE with verdict KEEP
  (UNTRAIL and DELETE excluded). Use it in `nset`, `emitted_set`, K2's pin, K4 and the listing's `set` op.
  The kind table's "writes" column already says "trail only" for SNAPSHOT; RESTORE's says only `s`, so
  add "(trailed)".

### FIX-2 K2's "exact" diff still omits derived lines (r8 FIX-2's own lesson)
- CONFIRMED (structural). Severity: design (K2 goes red on a correct build, or is weakened ad hoc at
  build time). Effort S. Blocks (c) 2a only.
- Every DELETE or UNTRAIL changes the body's decided length:
  - `en->program_bytes = pcrec_sb_len_decide(&job->vmsb)` (emit_vm.c:10962);
  - which is stamped as `<PREFIX>_VM_PROGRAM_BYTES` (11710);
  - and compared against the entry knee (11097: `program_bytes <= term`, giving FORWARD/INLINE against
    SHARED/PLAIN).
- A DELETE of the artifact's last trailed write flips `emitted_set`, so `touches_storage`/`may_fwd`
  flip too (11061-11065).
- So on a frameless artifact that sits near the knee, or whose last SET is k, `{k: DELETE}` changes:
  - the stamp line;
  - `RX_VM_ENTRY_SHAPE`;
  - the frame's ENTRY/DECL records (the frame is a record kind in rev 3's table);
  - the listing's verdict-count row.
- K2 says "every other record's kind, operands and rendered bytes unchanged", and in C only "k's bytes
  ... and again in the notempty copy". `pin-nset` pins `nset` alone.
- Rev 3's own "What the final walk owns" lists FRAMELESS and `RX_VM_PROGRAM_BYTES` as walk-3
  products, so the author knows they move. They are just not in K2's enumeration.
- Fix: either the pin lever pins every walk-2 size and storage decision (`nset`, `program_bytes`,
  `emitted_set`; call it `pin-walk2-decisions`), or K2's allowed diff enumerates the stamp, entry-shape
  and frame-record lines.
- To the question "is K2 still testing the shipped configuration?": no, by design. Pinned, it tests
  walk 2's placement under walk 3's verdicts, which never ships. Shipped placement is covered only by
  K4 (the margin constant, not placement) and the 4-shape ntrail sweep. FIX-1 is the concrete way that
  gap bites.

### FIX-3 SOUND-1's own record has a byte-identical twin kind, so E1 cannot check it
- CONFIRMED. Severity: design/maintenance (speed in (c); no answer change found). Effort S. Should be
  fixed before (a)'s go, because (a) is where the typing is fixed.
- The design's central claim ("Why kind can no longer be wrong"): "If it calls the wrong one, the
  program it emits is a different program. For (a) that is a red identity diff."
- That is false for SPAN "init only" against LSET assign on `<p>_span_cursor`:
  - render_check.py's templates `('SPAN','init_only')` and `('LSET','assign')` both print
    `    %s_span_cursor = scan_position;\n` (render_check.log rows `lazy0` 5159 and `resume` 5221);
  - in `c5b.c` lines 435 (the rmin = 0 opener) and 445 (the extend label's re-init) are the same bytes.
- Neither E1 nor RT can tell them apart: RT's reader sees identical text, and the M-table has no row
  for this pair.
- Same class elsewhere:
  - SNAPSHOT against SET with source SLOT(s) (covered by the new refusal);
  - RESTORE against SET whose source is built from `run->` read pieces (NOT refused). R1-R4 accept
    it. It is caught only in (c), by the S-6 assertion (the kept-restore list misses it).
- Consequences:
  - 5159 built as LSET means C5b's PUSH `SPAN(id)` and SEEK `SPAN_COMMIT(id)` have no opener, so they
    are OPAQUE and D declines silently. That is a speed loss, seen only at (c) 2b's C5b sabotage.
  - 5221 built as an opener only widens F (held: safe).
- Fix:
  - enumerate the byte-identical (kind, spelling) pairs mechanically (a script over the 47 templates);
  - give each pair a discriminator: a refusal, or a CEN count such as "members whose span or island id
    has no opener record" = 0, which (a)'s E5 can carry;
  - add M16 "SPAN init-only built as LSET".

### FIX-4 R4 and the class-read post-pass: the lexer's registry does not exist yet, and its text is rewritten after lexing
- CONFIRMED (structural). Severity: design. Effort M. Blocks (a) as written, because (a) builds the
  lexer and gates E5 on it.
- (i) **Ordering.** Builder step 5 lexes each fragment "at once", during the walk. R4 reads "the
  registry the prologue's helper writers fill". All three writers run after the walk:
  - `pcrec_emit_prologue` (emit_vm.c:14554);
  - the class atom and kit helpers (13076-13088), written after `vm_cls_tables` (14529);
  - the kit's word-load helpers, which are written by `mf_flush_helpers` at prologue time
    (memfn/include/memfn.h:1346-1352: an EXPR site "only records them").
  So at lex time the registry is empty. Every `rx_w2`/class read refuses (E5 red), or the build
  quietly invents a second, walk-time list.
- (ii) **Respell.** `vm_cls_respell` (1726-1764) runs after the walk.
  - It re-spells table reads, `(rx_class_bitmapN[(X) >> 3] >> ((X) & 7)) & 1` becoming
    `rx_class_atomN(X)` (different length), then `b->len = 0; pcrec_sb_puts(b, out)`.
  - That stales every record's `at`/`end` and every lexed window, and the shipped body is not the
    lexed body.
  - Rev 3 says tiling catches "a truncation (`b->len = 0`)", yet moves this one truncation into
    vm_stmt.c verbatim "after the tiling check". The exception is real, and unstated as one.
- (iii) **Census domain.** `kit_census.sh` lexes the FINAL `.c` (compile, then `kit_census.py`). So the
  lesson "the first run refused `rx_class_atom<N>`, therefore R4 must read the registry" was learned
  in a text domain the in-compiler lexer never sees.
  - At render the window holds `rx_class_bitmapN` (c5b.c:446 shows the pre-respell form), and the
    final artifact need not define that name at all (13079-13088 write atoms instead).
  - E5 "0 refusals" therefore has no prototype evidence for its actual domain.
- Fix, pick one and state it:
  - (1) R4 reads a walk-time registry built from the interned class pool and the art's recorded
    helpers, plus a control that it equals the prologue's emitted definitions; and respell is declared
    a table-to-table name substitution in CLS pieces (re-lex the respelled windows, or re-render them);
  - (2) the class read form becomes a CLS-piece operand, rendered after the pool is final (a deferred
    render: see FIX-12's general form);
  - (3) defer the lexer to (c) (FIX-6).

### FIX-5 R4's purity column for kit helpers crosses the D146/D147 boundary, unfiled
- CONFIRMED (structural). Severity: design (kit boundary). Effort S to file, M to build. Blocks (a)
  only if the lexer stays in (a).
- The kit's API gives no helper names and no effect facts. `mf_result` carries form_id, handle,
  reads_table, includes and cls; helpers are written by `mf_flush_helpers` straight into a sink.
- So the registry's kit rows can only be one of two things:
  - a pcrec-typed list of the kit's helper spellings. That is the prototype's `PURE_HELPERS` (`w2`,
    `w4`, `w8`) and `PURE_PATTERNS` (`mf_[a-z0-9_]+`, `ofs*`), which is exactly "a list someone types"
    (rev 3's own reason for R4). It also presumes the kit's text (D157; memory
    `pcrec-kit-facts-not-methods`);
  - or a new kit-contract fact ("helpers used, each with its effect class"). That is an `MF_SITE_ABI`
    change and a `memfn/docs/requests.md` row, and it is not in rev 3's cost.
- When the kit adds a helper (a `_w16`, a SIMD helper), the window refuses, V0 follows (silent, speed
  only) and CEN goes red. Rev 3 says a kit-window refusal "also files a kit request", but the defect
  would be pcrec's own table.
- Purity is DECLARED, not derived. Nothing checks a row's "PURE" against the helper's definition.
- Fix: file the request (facts only: name and "reads only its arguments" per helper), and derive the
  rows from it. Until then, document that kit-window R4 refusals are triaged against pcrec's table first.

### FIX-6 Cost and D77: (a) builds the lexer and registry ahead of their reader
- Severity: cost/process. Effort: negative (it shrinks (a)).
- Rev 3: "In (a) nothing reads it: the census counts it." The lexer (~200 lines of C), the helper
  registry with purity, FL and CEN have no consumer until (c)'s V0.
- D77 (memory `pcrec-build-under-measurement`) says to build them with their reader.
- Moving them to (c) 2a:
  - takes FIX-4 and FIX-5 off (a)'s go;
  - brings (a) back toward rev 2's M (96 sites, tiling, renderers, frame entry, RT, E1);
  - keeps (a)'s proof where it is strongest, the two-compiler byte diff.
- Against D153: no other in-flight remodel touches emit_vm.c besides trailgc, which lands first.
  `[SPAN-HELPERS]` is `not-started` and is callout-side. So one lane is credible for the slimmer (a).
  With the lexer, the registry and four new standing checks it is at the top of L.
- E1's size is unstated: about 2,568 lines x 2 engines x (1 + 3 + 45 axes.def arms + the memfn rows)
  x 2 compilers, about 0.5 M compiles plus listings. The queue job should be sized before the go.

### FIX-7 E1's population misses three emitter-reaching axes
- CONFIRMED (structural). Severity: test coverage. Effort S. Blocks (a)'s evidence plan (cheap to add).
- (1) **The kit's own arms.** E1 names "every deny/force arm `make test-axes` sweeps
  (`src/core/axes.def`)". `pcrec --list-axes` also has a `#section memfn` of `--memfn=no-NAME` rows
  (14 today). memfn/CLAUDE.md calls `--list-axes` "the ONE enumeration point".
  - Kit windows are the one place rev 3 still lexes, and kit arms are what change their text.
- (2) **.rxt SOURCE compiles** (tests/definitions `*.rxtin`, tests/rxtsource, examples/makefile;
  multi-target `-o DIR`). Composition-only emitter paths live there: the DELIVER SETs (emit_vm.c:8400-8407;
  `deliver_n` is filled only by `rxt_compose.c:1111-1114`) and flat/site imports. "Every corpus
  `pattern`/`pattern-esc` line" never reaches them.
- (3) **A maximal (60-byte) prefix.** That is K38's bug class, fixed-size buffers that truncate at long
  prefixes, and new renderer code is where it would re-enter.
  - `run_longprefix_sweep.sh`/`run_prefix_invariance.sh` run in E3, but against the new compiler's
    own invariance, not against the parent.
- Not missing: libpcrec API compiles against the CLI. The harness compiles through the library, and the
  CLI goes through the same `pcrec_compile`. Retries (ladder trials, abort_over) re-run from a fresh Job
  (compile.c:2362), so they are covered by whatever E1 compiles.

### FIX-8 E4/E5 are zero-count gates produced by (a)'s own code (a control sharing its source)
- SUSPECTED (check design). Severity: check design. Effort S.
- E4 "0 internal errors" and E5 "0 refusals" pass trivially on any builder path where tiling or the lexer
  is not wired.
- E7's M12/M13 seed tiling on two paths. FL tests the lexer function, not its invocation from every
  delegated renderer.
- K35 (a population nobody counts): CEN should print windows lexed per class and compare them with an
  independent count. Two candidates: delegated-site emissions from the kit's own stamps or site
  manifest, or the prototype's 49 windows on its 37 compiles.

### FIX-9 The RESTORE row's renderer text is wrong at its stated position R_c
- CONFIRMED (structural). Severity: doc for (c) 2c (that gate's identity check would catch it). Effort S.
- The kind table gives RESTORE "(at R_c, ordinal j)" and the renderer
  `run->trail[run->resume_stack[run->call_top].trail_mark + j]`, "today's bytes".
- Today's bytes are only right at the REGION exit, before the return. At R_c the region has already
  done `run->call_top = run->resume_stack[frame].call_top; goto *...` (emit_vm.c:8503-8509, the `call_top` pop at 8507).
- Rev 1's C-move reads `<p>_ret_frame`. So the RESTORE kind needs a spelling operand (region exit
  against R_c), and `<p>_ret_frame` needs a VmLocal and an R3 scope entry.
- In (a) every RESTORE sits at the region exit and serves every caller. Its "site" for the ordinal
  operand is the region, not a call c, so V1/V2's "at R_c" pairing is defined only after the C-move.
  Say so.

### FIX-10 Sibling fields left unstated by the fixes
- Severity: doc. Effort S. None blocks (a) alone.
- `group` on the island root LABEL, `opens(ISLAND id, F, nullable)`:
  - the legacy VE_ISLAND event rev 3 says the LABEL renderer emits carries `entry`, `nbr` and a role
    with nodes, depth, try sites, pushes and size estimates (emit_vm.c:4620-4630);
  - these are not operands, so either the record carries them or VE_ISLAND stays a `vm_note`.
- `deleg` on SPAN: the init-only spelling must carry none. It calls no kit, and DELEG/VMSPAN site
  counts must not move.
- `local` and the span cursor:
  - `<p>_span_cursor` is an LSET target (render_check's `resume`, `retreat`, `extend` at 5221/5225/5232)
    AND SPAN's write;
  - LSET's FIRST+ applies the non-effect rule to its untrailed write, but SPAN's row ("continue iff
    min = 0") does not;
  - it holds only because the span cursor is written before it is read on every path from a resume
    label (each `again` label re-inits it at 5221). That invariant should be stated, because the local
    is shared by every rung.
- `at`/`end`: stale after respell (FIX-4).
- `role`: "printed only as a COMMENT piece by the LABEL renderer". But PUSH, SET, WORK and NOTE events
  also carry listing roles (vm_ev's role argument). State that `role` is the listing text for every
  kind and is printed as C only by LABEL.

### FIX-11 Tail: siblings of existing families
- Severity: design (forest-for-trees lens). No block.
- **Text readers of emitted C.** With rev 3 there would be four or more:
  - the in-compiler fragment lexer;
  - RT's `vmgraph.py`;
  - ST's static scan;
  - (b)'s R guard over the preprocessed matcher;
  - plus the existing greps (`run_ir_listing.sh`, the recursion-identity canonicalizers, `vm_cls_reads`'
    strstr, the respell's strstr).
  - The test-side readers (RT, ST, the R guard) should share ONE C tokenizer. The in-compiler lexer
    must stay separate from them, because it is what they control.
- **Name tables.**
  - R2's label set, R3's scope list (the DECL facts, plus RUNSTATE after R) and R4's helper registry
    are three tables over the artifact's declared names.
  - Today's siblings: the stamp registry (`stamp_kinds.c`), DELEG_SITES, the kit's pending-helper
    record and the prologue's `pl.bufs`.
  - That is a third or later member, so propose one artifact symbol table: name, kind (label, param,
    local, run-state, helper, table) and effect class, filled by the writer that declares the name.

### FIX-12 Tail: the general form, and its unlocks with triggers
- Severity: design (unlock lens). No block.
- **General form.** Rev 3 builds a typed low-level IR of the matcher (statement records, one renderer
  per kind) but still renders at once. The general form is RECORD-THEN-RENDER: build every record,
  settle the pool, verdicts and dispatch on records, then render once.
- Unlocks:
  - (u-a) The respell post-pass and its tiling exception disappear: the CLS piece renders its final
    read form. Trigger: FIX-4 is answered by option (2).
  - (u-b) (c)'s three walks become one emission plus record rewrites. Trigger: card 0i shows emission
    as a material share of compile time.
  - (u-c) Size attribution per kind and a structural program-bytes model replace the length knee.
    Trigger: the next knee miss (the 4,096-byte twelve-class witness is one). This is r8's u3.
  - (u-d) The DFA emitter on the same record primitive (u4).
  - (u-e) The artifact symbol table of FIX-11 lets R2-R4, prefix-collision refusal across `.rxt`
    targets and dead-helper elimination read one table. Trigger: R's RUNSTATE class is the second
    reader.

## PROBED-AND-HELD

- **SOUND-2, the island opener on the root LABEL.**
  - The root takes the caller's `entry` (emit_vm.c:4568). Every path into it, whether a goto, a loop
    back edge or a PUSH resume to a lazy loop's body entry, passes the LABEL record itself, so "opened
    on this path" holds by construction.
  - Islands are flat literal alternations (`vm_isl_build`), so they cannot nest.
  - Non-root node labels and candidate-chain labels are reached only from inside the island: gotos from
    nodes, plus the chain's own PUSH resumes (4746-4760), which inherit O through the PUSH edge.
  - Probe p2.c: the lazy island loop came out possessified, but the root `rx_L5` is entered by
    `goto rx_L5` only.
  - Held. Sites checked: vm_isl_emit, vm_isl_die and vm_alt.
- **SOUND-1, continue iff min = 0.**
  - FIRST+ for the rmin = 0 lazy rung is class ∪ FIRST(continuation), which is correct.
  - For the greedy and possessive block with rmin = 0 it is the same, and with rmin ≥ 1 it is class
    only, also correct.
  - Sequential rungs share `<p>_span_cursor`: a PUSH stores the cursor's VALUE, and every `again`
    label re-initialises the local from `scan_position` (5221). So no member reads another rung's
    value. Held, with the stated-invariant note in FIX-10.
  - D183 (`nset`/`lbl_nset`) and the listing are unaffected: SPAN is no SET and has no event.
- **SOUND-7, the self-copy refusal.**
  - All 32 `vm_set` sites read: the only exact self-copy is vm_call's snapshot (8223).
  - The others are not self-copies:
    - DELIVER targets are fresh slots above `ncap` (rxt_compose.c:1083-1084);
    - the splice park and restore use distinct slot families (8343, 8416);
    - counters are `slot + K`;
    - the pending-to-start copy (8703) has a different source slot.
  - No other site would newly internal-error.
- **Restore ordinals.** D183 compaction keeps the call snapshots at `mark + j` ("THE CALL SNAPSHOT
  STAYS WHERE THE RETURN READS IT", 12798-12802). Deleting some snapshots under V1 still leaves the kept
  ones as the first distinct-slot entries of the segment, so compaction and the renumbered `j` agree.
- **Event order of nested checkpoints.** `vm_jump` has one call site (6601), one argument per printf.
  No unspecified evaluation order to preserve.
- **Ladder trials and abort_over.** Each attempt `calloc`s a fresh Job (compile.c:2362) and re-walks,
  so a record stream cannot outlive a longjmp into the next attempt (provided it lives in the Job or
  arena).
- **D80.** limits.md §3.3.5 and §7 promise nothing about compile time or memory, and the new internal
  errors fire only on emitter bugs. No spec hunk is owed for (a).
- **The FIX-3 premise.** c5b.c:435 against 445 are byte-identical (checked).
- **The FIX-1 premise.** p1.c:271-282 and 162 (checked).
- **Counts.** 4 compiles, 0 gcc, 0 driver runs. 32 `vm_set` sites and 7 `vm_push_at` sites read. I
  opened no denied files.

## STATE AT HANDOFF

- STATE: complete.
- OWED: none.
- No answer-level finding was confirmed, so no libpcre2 twin was needed. FIX-1's give-up hazard is
  stated as a consequence of the K4 wording, not as a measured move.
