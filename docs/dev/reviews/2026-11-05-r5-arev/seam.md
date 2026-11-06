# crit-seam findings (seam-round-trip lens, manifesto principle 9), arev rev 0

Subject: R/subject_arev.md (§ cited), review tree worktrees/crit-arev (main f15f30f25). Paths below
are relative to the review tree unless absolute. The question: can §2.1's operand record and §2.3's
VM-record host be written to text, read back by another process, and rendered to the same bytes?
Short answer: NO, not as specified. The record omits the renderer's real input (DfaForm and the
choices made while deriving it), several fields hold C text, one field is a method choice, the W2
column collapses four forms with different answers, and the VK_AUTO renderer has an undeclared
second output channel. Details follow.

## Findings

### SEAM-1 — the renderer does not read RevWalk; it reads a DfaForm full of pointers and choices the record never names
- CONFIRMED (code). Severity: design. Effort: M (S1's design must say which form facts the record
  carries). Blast radius: every table-repr instance (W1-W3, L). §2.1 ("Every field is a fact the
  planner states; the renderer reads them"), §2.3, S1.
- `emit_reverse_block(StrBuf *c, const DfaForm *rev, ...)` (src/gen/emit_dfa.c:13409) renders from
  `DfaForm` (emit_dfa.c ~5880-5975): `Ctx *cx`, `const Dfa *d`, `const DfaDir *dir` (with function
  pointers `emit_skip`, `emit_bound_accept`), `const DfaRepr *repr`, `const DfaView *view`,
  `const DfaSeed *seed`, `const DfaAcc *acc` (`emit_tail` fn pointer), `const CandRow *pf`
  (`emit_block`/`emit_define`), `const UnanchStart *us`, plus `skip[]`, `scan[]`, `tr_fold`,
  `acc_fold`, `entry_set/entry_head/entry_dead`, `accv`.
- Those are filled by `dfa_form_derive` (emit_dfa.c:12962) from inputs OUTSIDE RevWalk:
  `uint64_t flags = cx->opt->flags;` and `.route = cand_route_of(cx), .ss = pcrec_fact_start_set(cx)`,
  then four CHOICES: `f->repr = DFA_SELECT(DfaRepr, dfa_reprs, &s, flags); f->view = ...;
  f->seed = ...; f->acc = ...` (each skips rows by `cand->deny`, emit_dfa.c `dfa_select`), the
  UnanchStart's `views/viewsel/eol` (which W2 rewrites: `if (formw) rus.eol = rus.endv =
  rus.viewsel = rus.views = false;`), and the caller's post-derivation overrides
  (`if (formw) rev.seed = &dfa_seeds[1];`, emit_rev_end).
- So rendering = f(RevWalk, deny flags, route, start-set fact, UnanchStart, caller overrides). A
  process holding only a written RevWalk cannot reproduce the bytes; it would have to re-run
  `dfa_form_derive` against a Ctx it does not have.
- Fix direction: decide which side owns the form. Either the record carries the form's SELECTED
  rows as tokens (repr/view/seed/acc row names, the skip and scan-edge state lists, the two folds,
  the entry facts), declared as plan outputs; or the record names the renderer's frame inputs
  (flags word, route, view facts) as declared fields. Either way §2.1 needs those rows. The second
  keeps choices on the render side, which roadmap §0a's "emit is a pure function of the plan" argues
  against.

### SEAM-2 — W2 is four walks, not one column; equal records under §2.1, different bytes, and one rendering would give a wrong answer
- CONFIRMED (code + run + oracle). Severity: answer (for any renderer that trusts the record) and
  doc. Effort: S-M. Blast radius: every `rev-end` artifact (`$`/`\Z`-pinned on the DFA route). §1
  table W2, §1 "What they already share", §2.1 W2 column, §5 moving-seed loops.
- Code: `revend_forms[]` (emit_dfa.c ~13838-13848) is a first-match table of five rows (`denied`,
  `one-seed`, `tagged`, `two-seed`, `overflow`) that picks the walk's FORM. Only the two-seed forms
  reach `emit_reverse_block(c, &rev, "revend", "continue;")` (emit_dfa.c:14317).
  `emit_rev_end_one_seed` and `emit_rev_end_tagged` call `emit_scan_loop(c, rev)` directly
  (emit_dfa.c:14054, 14116) with `rev->dead = "break;"`, `rev->entry_set = true`, and the seed STATE
  resolved at compile time (`revend_seed_state(d, -1)`, `%s_reverse_state reverse_state = %d;`).
  The one-seed form also patches the result after the walk (`zero_at_n`: "a zero-length match at n
  is probed where the n-1 walk finds none"). §1's "W1-W3 ... ALREADY share one renderer,
  `emit_reverse_block`" is false for two of W2's forms. They share `emit_scan_loop` only.
- Equal records, different bytes (run): `a+b$` at default takes `one-seed` ("REVERSE FROM THE END,
  ONE SEED", 0 `reverse_view` lines, emitted C md5 34e014d7). Under `-fno-rev-end-onewalk` it takes
  the two-seed walk (7 `reverse_view` lines, md5 bddbd309). Under §2.1's W2 column both are
  {machine R, seed `n` / `n − 1`, floor `search_from`, exit farthest, tags none, dead `continue;`,
  names `revend`, host inline}. The record is equal and the bytes differ.
- Equal records, different ANSWER: `a\n?$` on "a\n". libpcre2 10.46 gives [0-2] (probe
  R/seam/p2.c). pcrec two-seed (`-fno-rev-end-onewalk`) gives `match 0 2`. The one-seed spelling of
  the same record seeds only `n − 1` when the last byte is `\n` and reports
  `match_end_position = subject_length - 1`, so (0,1) (read from emit_rev_end_one_seed's text; that
  row is not admitted here because `nl_last` is true, which is exactly the fact the record lacks).
  The missing fields are the seed stream's COMBINATION rule (walk every seed and keep the min start
  plus a tie bit, versus choose one seed by the last byte plus the empty-at-n probe) and the fact
  that admits it (`nl_last`, `Job.revend_nl_last`). §5's "the `seed` operand is a POSITION STREAM"
  does not cover a stream whose element is chosen by a subject byte, or a seed that is a STATE
  rather than a position.
- Fix: W2 gets one record per form (or a form field that names the `revend_forms[]` row and its
  facts), and `seed` admits {position stream with combine = min / choose-by-byte; compile-time seed
  state}. The `revend_forms[]` row table is already the declared choice. The record should cite it,
  not flatten it.

### SEAM-3 — `dead` merges two hands, its W1 value is wrong, and every value is a C statement
- CONFIRMED (code). Severity: design (F2 falsifier, principle 9) + doc. Effort: S. Blast radius:
  every instance. §2.1 `dead` row, §2.2 hand types, §5 LOCATE × FINISH.
- §2.1 defines `dead` as "the hand on a dead seed or no accept". In the code these are two
  different hands, written in different places:
  - dead ENTRY is `DfaForm.dead` (`dead_skip`, emit_dfa.c:13409-13415);
  - NO ACCEPT is text the caller writes after the block:
    - W1: `if (match_start_position == (size_t)-1) return 0;` (emit_dfa.c:13626);
    - W3: `{ landmark_position++; continue; }` as dead_skip (:14490) and again as the no-accept
      line (:14491);
    - W2 one-seed: `break;` as dead and `return 0;` as no-accept (:14062).
- So §2.1's W1 cell "NULL (seed is live)" is right for the dead entry and wrong for no accept,
  which is `return 0;`.
- Every value of the field is TARGET TEXT: `continue;`, `break;`, `{ landmark_position++;
  continue; }`, W4's int label. The manifesto (F2, falsifier column) says "a record still carries
  target text" fails flexibility. Principle 9 says no "assumptions about the other side's language".
- The success hand is also a naming convention, not a declared type. The walk writes
  `match_start_position` (the DfaDir's `recv`), and "none" is the sentinel `(size_t)-1` that each
  caller tests.
- Fix: the record declares a hand set {DEAD_ENTRY, NO_ACCEPT, ACCEPT(position[, tag])}, each mapped
  to a target (a label, or FINISH's hand: NOMATCH, AT, LOWER, SPAN, or "next seed"). The record
  holds no statement text. The renderer spells the C. §5's proposal ("FINISH's hand types are the
  kind's hand types") is the right vocabulary, and §2.1 should use it.

### SEAM-4 — `seed` and `floor` are C expressions and variable names, split between the record and the caller's text
- CONFIRMED (code). Severity: design. Effort: S-M. Blast radius: every instance. §2.1 `seed`,
  `floor`, `names`; §2.5 G2.
- The seed position is not given to the block. The CALLER declares it, in C, before calling:
  - W1 `size_t match_end_position = last_accept_position;` (:13620-ish);
  - W3 `size_t match_end_position = landmark_position + 1;` (:14486-ish).
- The seed's right context is DfaDir strings that hard-code that variable name:
  `"match_end_position < subject_length", "subject[match_end_position]"` (dfa_dir_reverse,
  :9360ff; repeated in dfa_dir_landmark).
- The floor is hard-coded in four DfaDir strings (`at_bound` "rewind_position <= search_from",
  `scan_more` "rewind_position > search_from", plus the bound accept). W4's floor is the C
  expression `(size_t)slot_values[%d]` and its seed the local `<p>_rv<i>_cursor`
  (`vm_rolef(v, "%s_rv%d_cursor", ...)`, emit_vm.c ~5735).
- §2.1's L column ("`max(0, cursor − W)`", "VM cursor") is an expression too. W is "hi characters
  times the encoding's widest character", which builds encoding arithmetic into the operand.
- Round trip: a reader would get C fragments that only parse against the writer's local
  declarations (`search_from`, `landmark_position`, `slot_values`). A second target cannot read
  them.
- Fix: `seed` and `floor` become typed position REFERENCES ({subject start, search start, the
  forward accept, a hit-stream element + k, a VM slot id, the VM cursor, a constant}, plus a
  declared width bound for L), and context is a fact the renderer derives. §3.3 (a) moves the floor
  "from a string constant into an operand". It should also say the operand is not a string.

### SEAM-5 — W4's `charge` cell names a compile-time node counter; the backward walk has no run-time charge
- CONFIRMED (code). Severity: doc + design (G10). Effort: S. Blast radius: W4 and the G10 claim.
  §2.1 `charge` (W4: "per step, as today (`vm_charge`)"), §2.5 G10.
- `vm_charge` (emit_vm.c:932) is the COMPILE-TIME emitted-node budget:
  `if (++v->nodes > PCREC_MAX_VM_NODES) pcrec_ctx_fail(... "pattern too large ...")`.
- `vm_rev_emit` (emit_vm.c:5521) calls it once per emitted node and builds no `VK_WORK` and no
  `VK_STEP` record. The only run-time work charge on the revdet rung is the scan cut's `vm_work`
  ("frames discarded by the revdet scan cut", ~5800).
- So W4's walk charges NOTHING per step at run time. The cell conflates two different facts, a
  compile-time size budget and a run-time give-up budget, and G10's "declared operand" has no
  existing instance.
- For the seam this matters because [GIVEUP-DIFF] direction reasoning (§3.1, D158) reads this field.
  Fix: split it into `size_charge` (compile-time, render side) and `work_charge` (run-time, per
  walk or per byte), and correct W4's value to "none at run time".

### SEAM-6 — `Rev` has dead fields, and the group sinks are artifact-shared mutable storage that §3.2 maps into `tags`
- CONFIRMED (code + grep). Severity: maintenance + design. Effort: S. Blast radius: W4 (S2). §3.2
  "the group sinks = `tags`", §1 "W4 has its own operand record".
- Dead-field pair (required construction): `R.ga = ga; R.ns = ns;` are written (emit_vm.c:5913) and
  never read. `grep -n 'R->ga\|R->ns'` finds only comments. Two W4 instances whose `Rev` differ
  only in `ga`/`ns` render identical bytes.
- `R->gs` IS read (`"!%s[%d]", R->gs, j`, :5572/:5582). The same name is ALSO spelled independently
  by `vm_local_name` (`VL_GROUP_SEEN: "%s_revdet_group_seen[%d]"`, vm_stmt.c:482). So one fact has
  two spellings. Moving `Rev` onto RevWalk as S2 proposes would copy two dead fields and one
  duplicated name into the shared record.
- The sinks are NOT per instance. `VL_GROUP_SPAN`/`VL_GROUP_SEEN` are indexed by `j` only, not by
  `loop` (vm_stmt.c:482-484). The frame declares ONE array per artifact, sized by the widest body:
  `ptrdiff_t %s_revdet_group_span[%d][2]`, `nrevcaps` (vm_stmt.c:1224-1226). Every revdet walk in
  an artifact writes the same storage. Each walk's VLO_ZERO and publish order is what keeps that
  sound.
- `names` (`rv<i>`) does not cover that storage, so a record read back by another process has no
  way to know that two instances share a buffer. That is shared mutable state across the seam.
- Fix: S2 drops `ga`/`ns`, derives `gs` from the VmLocal, and declares the group sink as an
  artifact-scope resource with the instance's reset and publish obligations.

### SEAM-7 — `exit` (and, under a function host, the local `names`) are fields nobody reads
- CONFIRMED for W4 (code); SUSPECTED for the L host (not built). Severity: design. Effort: S.
  §2.1 `exit`, `names`; §2.3 reason 1.
- Dead-field pair 2: `vm_rev_emit` takes no exit operand. It always renders one reversed body
  succeeding to `next` (its signature is `(Vm *v, int entry, const Ast *a, int next, const Rev
  *R)`). A W4 record with `exit = farthest` would render the same bytes as one with `first`. The
  field is unchecked, so a wrong value is silently ignored, not refused.
- The table renderer has the converse gap: `emit_scan_loop` records only the smallest accept, so
  `exit = first` on `repr = table` has no renderer today. That is new work in S3, not a re-labelling.
- §2.3 reason 1 says that under the function host "the renderer's local names stay RECOVER's
  inside each function". So for `host = vm-record` the state, position and result parts of `names`
  are unread. Only the function and table stems matter. Two L records differing only in those parts
  would render the same bytes.
- Fix: declare the admissible (repr × exit × host) cells as a table. The renderer refuses a cell
  outside it (loud), and `names` is split into the parts each host reads.

### SEAM-8 — `repr` is a method choice presented as a fact, and its `machine` is a pointer graph the renderer re-analyses
- CONFIRMED (text + code). Severity: design (§2.1's own invariant; D186; the D157 principle). Effort:
  S (design text). Blast radius: S2, S3, every later representation row. §2.1 `repr`, §2.5 G8, §5
  "Representation rows", §6.
- Fact or method? arev itself treats it as a CHOICE:
  - §5: "A TDFA-style group tag on table machines would let W4 change representation; HELD,
    trigger: a measurement showing a table walk faster than the structural one". A row that moves on
    a measurement is a D186 choice row.
  - §5 also lists three candidates (table, structural, [LANDWALK-FOLD]'s constants) "as one
    representation axis of the kind", with D161 add. 17's tiers "its rows by prefix shape".
  - The FACTS are what admit each row: revdet's forward and reverse unique iteration and
    prefix-freeness (`Ast.u.rep.revbody != NULL`); the table machine built, under cap, with its
    erasures.
  - Putting the chosen row into a record that §2.1 says holds only "facts the planner states"
    smuggles a method in.
- D157's letter is pcrec→kit (rarity as facts, the kit picks the method), so it is not violated
  literally. But the manifesto's 2026-11-04 addendum moves the kit's emitting face into the back
  end, so the same boundary now runs between planner and back end, and a back end handed `repr`
  has been told how.
- Name collision: `DfaForm.repr` is already the `DfaRepr` table-LAYOUT axis, itself a
  `DFA_SELECT` choice (SEAM-1). §2.1's `repr` row says "`DfaRepr` rows inside", so two choices at
  two levels share one word.
- `machine` under `structural` is `Ast.u.rep.revbody`, a pointer graph. `vm_rev_emit` also
  re-derives facts from it at render time: `pcrec_revdet_first(v->cx, br[j], f)` (emit_vm.c:5639)
  computes each branch's first set, and `vm_cls(v, ...)` interns class tables into the Vm's shared
  table. Both are shared mutable state and analysis on the render side of the seam.
- Fix: `repr` becomes the OUTPUT of a declared representation row table (row, admitting facts,
  lever), recorded as a selection like `revend_forms[]`, not as a fact. The structural machine is
  carried as serialisable IR (the reversed body as text or IR, plus its first sets as stated
  facts). Rename one of the two `repr`s.

### SEAM-9 — a machine reference changes meaning when the driver swaps machines, and the build request leaves out the parameters that set the language
- CONFIRMED (code). Severity: design (answer-bearing for L). Effort: S-M. Blast radius: S3's
  machine table; W2. §2.4, §2.1 `machine`, §3.1 row 1.
- Mutable identity:
  - `revend_choose_form` swaps the lowered machines INTO the plain slots under `tagged`:
    `td = job->rdfa; job->rdfa = job->xrdfa; job->xrdfa = td;` (src/core/compile.c:589, with
    nfa/rnfa/dfa/adfa beside it).
  - §1's "`Job.rdfa`, or the lowered `Job.xrdfa`" is therefore resolved by an in-place swap.
    `emit_rev_end` always reads `job->rdfa`, which holds whichever machine was swapped in.
  - A (site, role) reference written before `revend_choose_form` (driver line 3162) names the
    other machine after it. So the table's entries must be immutable once built, and a form
    decision must ADD an entry, never swap.
- Incomplete build request:
  - §2.4 makes `exact` / `collapsed` the build request. But the builder's real parameters are
    `revend_build_one(cx, nfa, d, prune, reverse, cap, root, forward)` (compile.c:454), and
    `pcrec_build_dfa`'s `prune` CHANGES THE LANGUAGE: "With prune on, lower-priority threads are
    cut" (src/ir/dfa.c:982-987).
  - A pruned machine's accepts are not the branch's language, so `erased == 0` alone does not
    license §3.1 row 1 (`exist`, answer).
  - The request must carry {direction, root (start / anch_start), prune, cap, count policy}, and
    the entry must record {built, overflowed, erased bits, prune}. The exactness fact `exist` reads
    is `erased == 0 AND !prune AND built`.
- Where exactness lives today:
  - exactness is on the NFA (`Nfa.erased`, internal.h:2427), not the DFA the walk reads;
  - `lmwalk_build` uses it as a BUILD GATE (`if (job->lmnfa.erased == 0 && revend_build_one(...))`,
    compile.c:554), so W3 never records a non-exact machine at all;
  - the size-cap fall-back flows back as `job->lm_built` / `revend_fit` booleans.
  - §2.4's "the realized `Nfa.erased` is recorded with the entry" is the right move. It should list
    every one of these as the entry's declared result fields.

### SEAM-10 — VK_AUTO's renderer would write outside the body; the hybrid "precedent" is not a record; no call signature
- CONFIRMED (code) for the constraints; the design gap is in the text. Severity: design. Effort:
  M. Blast radius: S3 (G5). §2.3 (proposal, reasons 2 and 3), §2.5 G5/G6.
- D182 and the module header (src/gen/vm_stmt.h:1-26) fix ONE writer by tiling: every record's
  renderer prints into the body buffer (`sb->b = &cx->job->vmsb`, vm_stmt.c:730), and a write that
  reached the body any other way is an internal error.
- §2.3 has VK_AUTO's renderer emit "a call to a per-instance `static` function defined at file
  scope" with "tables and accessors at file scope under the instance stem". That is a record whose
  rendering ALSO writes outside the body: a second output channel no record kind has today. It
  also depends on an implicit ORDER, because the function must be defined in `csb` before the
  matcher function that `pcrec_vm_stmt_frame` (emit_vm.c:13074) splices the body into.
- Reason 2's precedent does not carry over. `pcrec_emit_dfa_engine` is called by the COMBINATOR
  layer (src/gen/emit_comb.c:576, 580) as a separate entry part, not from inside a VM record.
  vlookbehind rev 1 §4 G5 says so too ("It is outside the matcher body").
- The record names no signature: the parameters (subject, length, seed, floor), the result type,
  the "none" value, and for `gate`/`exist` whether the function returns a position or a
  decided/passed code. Reason 3's declared effects ("reads `subject[floor − 1 .. seed]`, writes one
  result") are the right content, but they are prose. Principle 9 needs them as fields.
- Fix: make the file-scope walk a PART (a stream-level record with its own stem, emitted in its own
  slot before the matcher, like the hybrid's part), and VK_AUTO an in-body CALL record that names
  that part, its argument references (SEAM-4), its result hands (SEAM-3) and its effect set. Then
  each record has one renderer and one output, and the order is the stream's declared part order.

### SEAM-11 — one `names` stem is really two: table stems are per machine × direction and shared; label stems are per walk
- CONFIRMED (code). Severity: design. Effort: S. Blast radius: S1, S3. §2.1 `names`, §2.3 reason 1,
  §3.3 (a).
- Table and accessor names come from `f->dir->c.name`: e.g. `"%s_%s_%s, ", f->p,
  f->dir->c.name, tag` (emit_dfa.c:6040), `emit_machine_tables` `m = f->dir->c.name` (:13110).
- Labels come from `f->lbl`, which `emit_reverse_block` overrides per instance:
  `emit_reverse_block(c, &rev, "revend", "continue;")` writes labels `revend*` over tables named
  `<p>_reverse_*`.
- In `emit_rev_end`'s relocate arm, the rev-end walk and the composite's RECOVER pass are two WALKS
  over one machine and one set of tables. The tables are emitted once (`emit_machine_tables(c,
  &rev)`), and `emit_rev_end_tagged` copies the form (`DfaForm rel = *rev;`) so the composite reads
  the same tables untagged.
- A record with one stem per instance must therefore either emit the tables again (new bytes, and a
  duplicate-symbol risk at file scope) or rely on knowing that a sibling instance already did. That
  is an implicit cross-record dependency.
- Fix: tables belong to the machine-table ENTRY (§2.4), emitted once per (machine, direction). A walk
  instance REFERENCES the entry and carries only its label stem.

### SEAM-12 — the facts that flow back (tag encoding, tie bit, empty-at-n probe, reach) are consumer conventions, not declared fields
- CONFIRMED (code). Severity: design / doc. Effort: S. Blast radius: W1-W3, S1. §2.2 "report a
  tagged end", §2.1 `tags`, §5.
- The `distance` tag comes back as an `unsigned` BIT SET (bit k = distance k, k ≤ 7 by
  `pcrec_nfa_mark_distances(..., 7)`, compile.c). Consumers decode it by convention:
  `__builtin_ctz(revend_dist)` for the end, `revend_dist & (revend_dist - 1)` for the TIE
  (emit_rev_end_tagged; W1 `match_end_position -= (size_t)__builtin_ctz(%s)`, :13630).
  §2.1 says only "`distance`". The encoding, its width bound and the tie fact are part of the hand
  type.
- The one-seed form's `zero_at_n` patch (SEAM-2) is a result produced OUTSIDE the walk.
- W3's reach guard reads `lmwalk_reach`, which the FINISHER writes (the farthest byte the last
  verify read) and the NEXT walk's decision reads. That is a fact flowing from FINISH back to
  LOCATE that §2.1/§2.3's finisher contract does not mention.
- Exactness and the size-cap fall-back for L ARE declared (§2.4 and §3.1, "an overflow is the row's
  decline"). The walk's result for `first` (position versus "yes/no") is declared only as prose in
  §2.2's "hand (seam type)" column.
- Fix: a hand-type table with encodings ({position, sentinel}, {position, distance set ≤ 7 bits,
  tie = popcount > 1}, {yes/no}, {decided/passed}) and the host-loop state each instance owns
  (reach, seed cursor). The fields are then declared, not conventional.

## PROBED-AND-HELD

- Cited anchors exist at the cited lines in the review tree (13 checked):
  - `Rev` :5500, `vm_rev_emit` :5521, `vm_revdet_rep` :5705 (emit_vm.c);
  - `VK_CONSUME_BACK` vm_stmt.h:59, `vm_r_consume_back` vm_stmt.c:403;
  - `dfa_member_machines` :4916 (four machines: F, R, A, ML), `struct DfaDir` :5787,
    `dfa_dir_reverse` :9360, `dfa_dir_landmark` :9442, `dfa_dir_lmverify` :9460,
    `emit_scan_loop` :13244, `emit_reverse_block` :13409, `emit_landmark_walk` :14398,
    `emit_rev_end` :14229 (emit_dfa.c);
  - `revend_build_one` compile.c:454, `lmwalk_build` :547, `CAND_ML` internal.h:9285,
    `lmwalk_conj[]` lmwalk.c:276.
- `emit_reverse_block` "only sets the form's `lbl` and `dead` and calls `emit_scan_loop`" (§1):
  holds (emit_dfa.c:13409-13416). Only the claim of WHO calls it fails (SEAM-2).
- `dfa_dir_landmark` repeats `dfa_dir_reverse`'s direction strings: holds for every behavioural
  string (seed_cond, seed_byte, at_bound, peek, consume, advance, skip/bound fns, scan_more,
  scan_back). It differs in c.name, title, label, statev, viewv, ind, bind, tbl_hdr and
  acc_meaning, which §3.3 (a) lists as becoming operands. Held.
- The overflow decline is declared and restored as §2.4 says (`revend_build_one` saves and restores
  `dfa_overflowed` and `dfa_overflow_why`, returns false on `d->overflowed`; `lmwalk_build` restores
  `subset_elems`). Held.
- The L client's exactness is read from a recorded fact, not the kind (§3.1). Held in design: the
  fact exists (`Nfa.erased`, set by every widening arm, nfa.c:599/603/848/955, reset per build at
  :1072/:1089). It is incomplete only by SEAM-9's prune parameter.
- `VK_CONSUME_BACK`'s operands are a pure record (a fragment, the loop number, a label). It renders
  `<p>_rv<i>_cursor--` from the loop id, not from text. This record kind survives a round trip
  (modulo the VP_CLS class-table interning, which the post-render respell closes, D182). Held.
- The finisher stays the host's, chosen by FINISH rows (§2.3): holds for W2/W3. Both assert their
  FINISH rows (`cand_finish_ask(...)->u.finish.act != ...` -> `pcrec_ctx_fail`), as §3.3 says
  these asserts "become seam type checks".
- Runs: 10 single-pattern `build/pcrec` compiles (form discovery over 5 patterns; `a+b$` and `a\n?$` with and without `-fno-rev-end-onewalk`; one `--emit-main`), 2 gcc builds (one matcher, one libpcre2 probe), 3 libpcre2 probes. No make, no suites.
