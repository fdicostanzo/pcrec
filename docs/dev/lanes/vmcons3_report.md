# Lane vmcons3: ONE design for the VM trail and dispatch build, rev 3 (the record is the source, the text is rendered from it)

Lane vmcons3 (opus), 2026-10-29. Design and measurement only (no build go): nothing under
`src/`, `cli/`, `lib/` or `memfn/` changed. Worktree `worktrees/vmcons3`, branch
`lane/vmcons3`, rebased onto main 26804bd46. This document REPLACES rev 2
(`vmcons2_report.md`) for the build. It applies review
`docs/dev/reviews/2026-10-29-r8-vmcons2.md` (cited `[r8 SOUND-n]`, `[r8 FIX-n]`) and its
MANAGER RULINGS, the ROOT-CAUSE RULING's second pass first. The r6 and r3 rulings, and
rev 2's dispositions of r6 (`[r6 S-n]`, `[r6 SEAM-n]`) and of r3 (`[r3 Fn]`), stand unless a
row below supersedes them. Rulings file `vmcons3_rulings.md`: empty at every read.

**Base code.** Main 26804bd46 with lane/trailgc ffd1f578e's `src/` diff applied (it lands
first). This is the tree review r8 read: its `emit_vm.c` line numbers are r8's, and every
`emit_vm.c:N` below is this tree's. The only rejected hunk is emit_dfa.c's abi line, which
has nothing to do with the design. Probes ran on a scratch build of it.

- Scratch: `/var/tmp/pcrec-pcrec/scratch/vmcons3/` (`merged/` is the tree and its build).
- Evidence: `docs/dev/lanes/vmcons3_evidence/` (scripts, logs, the call table).

## Summary

- **Premise test: reproduced** (`premise.sh`, `premise.log`).
  - r8 SOUND-6's witness is `^(a)b+c` (`--features all`). Rev 2's token signature, applied as
    written by `sig_rev2.py`, counts the possessive rung's two conditional fails
    (`if ((ptrdiff_t)rx_span_cursor < (ptrdiff_t)scan_position + 1) goto rx_fail;` and
    `if (RX_PRUNE_TOO_SHORT(rx_span_cursor, 1)) goto rx_fail;`).
  - Each statement's count vector is identical when typed FAIL and when typed BRANCH_FAIL:
    MATCH both ways, so no mismatch and no V0.
  - Under FAIL, V3 deletes both of group 1's SETs. The twin gives `1:-1,-1` on `abbc` and
    `abc`; base and libpcre2 give `1:0,1`.
- **The inversion** `[r8 ROOT-CAUSE RULING, second pass]`. Each emitter site BUILDS a typed
  record (kind plus typed operands). Each kind has ONE renderer that prints it, and the
  builder renders at once, so printing is rendering.
  - A kind that is not in the table has no builder, so it cannot be built.
  - The control text of a statement (its gotos, its returns, its labels, its braces, the
    cursor and slot writes it performs) is printed only by its kind's renderer, from the
    record's operands. So a record cannot disagree with its text about its kind, its edges
    or its writes.
  - The token signature is DROPPED, for the core kinds and for the compound kinds
    (BREF, VAR, CALLOUT, RETURN, WCLASS) alike.
- **Value fragments are the only free text.** A fragment is a condition, a SET source, a work
  count, a clamp, a declaration value or delegated kit text.
  - pcrec's fragments are typed piece lists. A literal piece must be a C string literal at
    the call site (the builder's macro enforces it); slot, local and run-state reads are
    typed read pieces (they record the read); class reads are class pieces; a nested
    fragment is a sub-piece. No piece builder takes a label, a target or a statement, so no
    builder can produce a goto or a return.
  - The kit's text cannot be typed. It is written IN PLACE into the body by the renderer, and
    then lexed by a fragment lexer with four rules drawn from C's own classes and the
    artifact's own declaration lists: no control transfer out, no label name, no write to a
    matcher-scope name except the record's declared output, and no unknown helper. A refusal
    makes the function V0. The lexer skips comments and string/char literals.
- **One writer, made structural by a TILING invariant** `[r8 FIX-4]`. Every record stores the
  body's uncut length (bytes plus muted comment bytes) where it starts and where it ends.
  Each builder asserts that the body has not grown since the last record ended.
  - So a write that reaches the body by any route is an internal error at the next record:
    `&v->cx->job->vmsb`, a comment-tier print under `-fno-comments`, a helper handed the
    buffer.
  - The matcher's span in the artifact is written by ONE vm_stmt.c call (frame, body splice,
    accept, fail block, notempty copy) and tiles itself the same way.
  - No getter and no grep is the guarantee. A static scan stays as an early warning.
- **No new buffer** `[r8 SOUND-3 = FIX-3]`. The kit writes into the body buffer itself, at the
  renderer's position. So every decision record the body carries survives with the bytes:
  `cmt_dropped`, the SIMD, scaffold and layout records, `.cx`, `abort_over`, the
  end-of-compile balance check and the SIMD mid-line refusal. None is copied.
- **Byte identity of (a): feasible; STOP RULE not triggered.**
  - `render_check.py` joins every body statement's print calls in emission order and matches
    each against its renderer's template: 98 statement spellings in 47 (kind, spelling)
    templates, 130 of the 132 body print calls (the other two are a class-read piece and the
    respell post-pass).
  - Result: all 98 MATCH, and every fragment group is control-free and write-free. The 7
    compound spellings are fixed skeletons moved verbatim. The 27 frame and copy calls are
    moved verbatim into one vm_stmt.c entry.
  - The evidence plan (two compilers, every corpus pattern line and every bench text, every
    axis including `-fcomments`, `-fmemfn-simd`, `--trace` and the listing) is in "Renderers
    and byte identity".
- **The fragment lexer has a prototype and a census** (`frag_lex.py`, `kit_census.sh`, 37
  compiles).
  - 49 kit windows in 16 shapes, 0 refused. That covers the span advance and the run compare,
    the `-fmemfn-simd` and `-fcomments` arms, UTF-8, and cscan.rxt:20 with FIX-1's
    `rx_w2("\?{")`.
  - 12 sabotage rows are detected, one per mis-typing class. The 4 controls stay clean:
    pattern bytes in a literal `[r8 FIX-1]`, `return` in a comment `[r8 FIX-5]`, `==` as a
    read, and the span's declared output.
  - The FIRST run refused 4 windows: the prototype's hand-written helper list lacked the
    class kit's `rx_class_atom<N>`. That is the reason rule R4 must read the artifact's own
    helper registry (a declared table), never a list someone types.
- **The answer fixes** (each with a named cell checked against libpcre2, `cells.sh`,
  `cells.log`):
  - `[r8 SOUND-1]`: the rmin = 0 lazy rung's cursor init IS a SPAN record ("init only"
    spelling, same bytes). Membership is by span-id OPERAND, and a member whose opener was not
    met on the path is OPAQUE. Cells C5b and C5c.
  - `[r8 SOUND-2]`: the island opener is an operand of the root LABEL record, so it is on
    every path into the island. One table statement covers the island exemption. Cells C7a
    (one-child root, `-fno-altcls-factor`) and C7b (SWITCH root, default flags).
  - `[r8 SOUND-7]`: SNAPSHOT and RESTORE are kinds with their own builders. `vm_set`
    refuses a self-copy source, and V4 never matches a self-copy. Cell C6.
- **Verdicts are rendered.** A DELETE renders nothing (a tombstone record) and UNTRAIL renders
  `<P>_SETU`, so a walk-3 "mismatch" no longer exists `[r8 FIX-5 item 5, FIX-9]`.
  - V0 has one source: a refused fragment.
  - In walk 1 it declines D and every verdict. In walk 2 the walk is discarded and walk 1's
    records are reused (still at most 3 emissions). In walk 3 it is an internal error.
- **K2 is exact** `[r8 FIX-2]`.
  - K2 runs under a pin lever (`--harness=pin-nset`) that freezes D183's placement counter at
    walk 2's value, and it compares RECORD streams.
  - Snapshot/restore entries are pair entries, with their renumbering enumerated. A lone
    snapshot DELETE is refused.
  - K4 checks the KEEP-only margin separately.
- **The rest of r8 as ruled:**
  - FIX-7: card 0n becomes a STANDING renderer round-trip check with two-way triage; the
    ntrail sweep moves onto the built compiler in gates 2d/2e; G1's precedence is stated.
  - FIX-8: EXPECTED-MOVES gets its executor and direction-keyed GIVEUP1 lookups.
  - FIX-9: V0 by walk.
  - FIX-10: PLAN for u2-u5 (u1 is this design) and the citation fix.
- **Cost, honestly.** (a) grows from rev 2's M to L.
  - A new `src/gen/vm_stmt.c` of about 1,300 lines, about 350 of them moved.
  - In emit_vm.c: 96 statement sites, 54 `vm_ev`, 41 slot spellings, 22 C-text fragments,
    4 delegated calls and 27 frame/copy calls touched.
  - About 500 lines of checks.
  - It stays one lane, refactor class, byte-identical, with no abi bump, landing first and
    alone.
- **Flags** (memory `pcrec-flag-follows-caller-effect`):
  - (a) and R get none.
  - D gets one public deny.
  - The slot-flow verdicts get test-only levers: `keep-slot-writes`, `verdicts=FILE` and the
    new `pin-nset`.

## Disposition table

One row per review r8 finding (plus its residue, lessons and process change). "Where" names
this document's section.

| id | ruled | disposition here | where |
|---|---|---|---|
| SOUND-1 | FIX-NOW | The rmin = 0 lazy rung's `<p>_span_cursor = scan_position;` (`emit_vm.c:5159`) becomes a SPAN record with the spelling "init only" (min 0, the body class, a span id), so the bytes are unchanged. PUSH's position is a typed operand `SPAN(id)`. A member (`PUSH pos=SPAN(id)`, `SEEK SPAN_COMMIT(id)`) continues iff the opener of `id` was met on this path, else it is OPAQUE. Ids are per record, never the shared local, so two rungs cannot be confused. C5b stays the rmin = 0 cell (sabotage: "span-cursor PUSH with no SPAN opener on the path = member"). C5c `^(?:[ab]{2,}?b\|y)(z)` covers the block spelling (sabotage: "SPAN contributes nothing"). | The kind table; Test cells |
| SOUND-2 | FIX-NOW | The island opener (first-byte set, nullable) is an OPERAND of the island root's LABEL record (`opens = ISLAND(id, F, nullable)`), so every path into the island passes it. Legacy events stay in order (VE_ISLAND, then VE_LABEL). ONE table statement covers the exemption: an island ADVANCE, compare or SWITCH carries `member(id)` and continues iff `id` was opened on this path, else OPAQUE. Rule 3 now reads the table, so the table and the prose no longer contradict. Cells C7a (one-child root) and C7b (SWITCH root, reachable with default flags). Sabotage: "ISLAND contributes nothing", plus "member without opener = continue". | The kind table; Test cells |
| SOUND-3 (= FIX-3) | FIX-NOW | No fragment buffer exists. The kit writes into the body buffer in place, from inside the renderer, so `cmt_dropped`, the SIMD, scaffold and layout records, `.cx`, `abort_over`, the balance check and the mid-line refusal are the body's own. (a)'s gate adds `run_simd_guarded.sh` and full `-fcomments` and `-fmemfn-simd` passes to the identity diff. | Value fragments; Renderers and byte identity |
| SOUND-4 | FIX-NOW (signature rewrite) | Dropped with the signature. Core and compound kinds are rendered, never counted. The fragment lexer's text domain is stated: comments and string/char literals are skipped, so `-fcomments`, `--trace` and pattern bytes change no verdict. BREF's two fails and three reads are the BREF renderer's own text, read from its operands. `run->` is never counted: a write to run state is a renderer's, and in a fragment it refuses (R3). | Value fragments |
| SOUND-5 | FIX-NOW (with FIX-4) | The counts are re-derived (`calls3.py`, `calls.tsv`): 132 body calls (the same set), plus 24 frame calls (r8 counted 23, up to the fail block's opening; the 24th is the pop block's last puts at 13436) and 3 copy calls. `vmsb` is not hidden. Tiling makes a raw write an internal error by any route. vm_stmt.c exports `vm_stmt_program_bytes()` (the `pcrec_sb_len_decide` of the body) and a `const char *` view for `vm_cls_reads`; the splice is inside the frame entry. The static scan is written against today's five compile.c lines. | The record is the source |
| SOUND-6 | FIX-NOW (signature rewrite) | Impossible by construction. FAIL's builder has no condition operand, and a conditional fail can only be built as a BRANCH with target FAIL. A site that drops its condition changes the program's text, so (a)'s identity diff turns red, and after (a) the record is true to the program. Cell C8 `^(a)b+c`, plus mis-typing row M1. | The record is the source; Test cells |
| SOUND-7 | FIX-NOW | SNAPSHOT (`vm_snapshot(v, slot)`, no source operand) and RESTORE (`vm_restore(v, slot, j)`) are kinds with their own builders, called from `vm_call` and `vm_region`. Their renderers print today's `<P>_SET(...)` bytes. `vm_set` refuses a source that is exactly SLOT(target) (internal error: "a self-copy is a SNAPSHOT"), and V4 never matches a self-copy. Cell C6. Sabotage: "snapshot built as SET" (the refusal fires; with the refusal removed, V4's self-copy clause still keeps it). | The kind table; Test cells |
| FIX-1 | FIX-NOW (signature rewrite) | No count reaches a literal: pattern bytes in `rx_w2("...")` are one opaque token. cscan.rxt:20 and `^\{(a\|"x\}")*\}$` are census cells (both CLEAN in `kit_census.log`). | Value fragments |
| FIX-2 | FIX-NOW | K2's exact allowed diff: compared on RECORD streams under `--harness=pin-nset`, where `nset` counts SET records whatever their verdict, so the margin and every checkpoint stay walk 2's. A one-entry map changes only record k (a tombstone or retag). Snapshot/restore maps are PAIR entries, and the only other moved records are that call site's later restores, whose ordinal operand equals the rank among kept snapshots (enumerated, and the S-6 assertion checks it). A lone snapshot DELETE is refused by the map loader. In C, the same change shows twice where the notempty copy exists (the copy is a byte copy of the rendered span). K4, new, checks the KEEP-only margin without the pin. | Verdict identity across walks |
| FIX-3 | FIX-NOW | As SOUND-3. | Value fragments |
| FIX-4 | FIX-NOW | The tiling invariant (above) is the structural guarantee. The kit, clskit and callsite calls move INTO renderers: a record carries the kit-site handle (`mf_site *`, hooks, DelegSite id) or the callsite callee as an operand, so emit_vm.c never holds a body `StrBuf *`. The frame, the splice, the notempty copy and the respell post-pass are one vm_stmt.c entry each. Sabotage rows: a raw `pcrec_sb_puts(&v->cx->job->vmsb, ...)`; the same under `-fno-comments` as a comment-tier write; a raw csb print added inside the frame entry. | The record is the source; Test cells |
| FIX-5 | FIX-NOW (signature rewrite) | Every item dissolves: (1) comments are skipped by the lexer and not counted anywhere else; (2) `==` is a read (lexer token, R3); (3) frame rows are rendered; (4) the embedded checkpoint is a nested CHECKPOINT record built by BRANCH's `jump` target; (5) verdicts are rendered; (6) brace-free GUARDs are the GUARD spelling `inline`; (7) BREF's two fails are its renderer's. The legacy op list is whatever the renderer emits, `[note]` included when `has_budget`. | The record is the source; Renderers and byte identity |
| FIX-6 | FIX-NOW (signature rewrite) | A local write in a fragment refuses: R3 covers every matcher-scope name from the frame's declaration list, not chosen tokens. LSET's target is a `VmLocal` enum that excludes the cursor and the run-state fields, so a SEEK or CUT_LOCAL cannot be built as an LSET (compile error). `&&L` is printed only by the PUSH and CALL renderers. CALL's successor is `next` (the SNAPSHOT records), and the callee edge is the following GOTO record. After R, the run-state fields join the scope list as class RUNSTATE, writable only by their renderers, so R needs no re-declared signature. Mirror sabotage: an LSET folded into a fragment (DETECTED in the census rows). | Value fragments; The kind table |
| FIX-7 | FIX-NOW | 0n becomes the STANDING renderer round-trip check: an independent text reader recovers kind, edges, reads and writes from each rendered record, with two-way triage. 0m becomes the fragment census (refusals by class, 0). The ntrail sweep moves onto the BUILT compiler in gates 2d/2e, at the stamped boundary. G1: sentence 1 (no new give-up at a stamped capacity) governs where a stamped capacity lies inside a gap band. | Gates, EXPECTED-MOVES and STEP 0 |
| FIX-8 | FIX-NOW | Executor `tests/vm/run_expected_moves.sh` (section `test-vm-moves`), with direction and arm columns. It checks the committed libpcre2 column always and live libpcre2 when present (SKIP loud). It is red on a listed non-move. Unlisted moves stay `run_axes.sh`'s UNALLOWED GIVEUP1 red. For listed cells, run_axes' lookup reads the manifest's arm AND direction instead of a direction-blind GIVEUP1 row. A row goes only on the arm that moves the cell. | Gates, EXPECTED-MOVES and STEP 0 |
| FIX-9 | FIX-NOW | V0 has one source, a refused fragment. Walk 1: D declines and verdicts are all KEEP. Walk 2: the walk is discarded, the rounds run on walk 1's records and walk 3 applies them with D off (at most 3 emissions). Walk 3: impossible (verdicts change no fragment), so an internal error. | Verdict identity across walks |
| FIX-10 | PLAN (u2-u5) | u1 is this design. u2-u5 are filed with r8's triggers. Citation corrected: the comment at `emit_vm.c:3444` names FIVE primitives; the SIXTH (`vm_rung_mark`, 3685) and the SEVENTH (the work charge, 3611) are named in their own comments. | Cost |
| residue: `ir_listing.md` "resume-point cap" | DOC | In (c)'s spec pass, with `run_ir_listing.sh`'s failure text. | Cost |
| residue: lever-fence ALLOW entries | DOC | Every new `--harness=` lever and every script that names one gets an ALLOW entry: `stmt-records`, `keep-slot-writes`, `verdicts=FILE`, `pin-nset`; K2, K3, K4, the census and the round-trip scripts. | Cost |
| residue: `<PREFIX>_VM_DISPATCH_SITES` | DOC | A `stamp_kinds.c` row in (c). | Cost |
| Lessons 1-5 | for the manager | Applied here: the kind is rendered, not counted (1); the lexer's text domain is stated (2); K2 enumerates its derived lines (3); no new buffer joins the family (4); openers are on the path (5). | — |
| Process change (a mis-typed record per kind class) | ACCEPTED | The mis-typing table M1-M15, each row naming what makes it impossible or what catches it, and its cell. | Test cells |

**Rows carried.** Every rev 2 row for r6 stands except where this table supersedes it: S-1
(the GUARD is now rendered), S-2, S-3, S-5 (by SOUND-1/2), S-6, S-7 + SEAM-3 (signature
dropped; one writer by tiling), S-8, S-4/SEAM-1, SEAM-2, SEAM-4, SEAM-5 (by FIX-8), SEAM-6
(by FIX-7), SEAM-7, SEAM-G1, SEAM-G2. Rev 2's r3 carry list stands.

## The record is the source

### The record and its builders

A matcher body is a stream of records, `VmStmt`, owned by `src/gen/vm_stmt.c` (its header is
private to `src/gen/`). A record holds:

| field | meaning |
|---|---|
| `kind` | a row of `vm_kind_rows[]`, the ONE declared table (below) |
| `sid` | `(node, instance, line, k)`, as rev 2 (Verdict identity across walks) |
| `spelling` | the renderer's layout variant (indent, braced or inline, traced, block or init-only). It changes bytes, never a column |
| `tgt` | BRANCH, GOTO, CONSUME: `LABEL(id, ckpt)` (`ckpt` = D183's placement rule applies, as `vm_jump` today, or a declared-forward plain goto), `FAIL`, `ABORT(code)`, `ACCEPT` |
| `slot`, `j` | SET, SNAPSHOT, RESTORE, CUT, SEEK RESTORE: the slot. RESTORE: the ordinal |
| `local` | LSET, CONSUME_BACK, CUT_LOCAL: a `VmLocal` (an enum over the frame's declared locals; the cursor and run state are not members) |
| `pos` | PUSH: `CURSOR`, `SPAN(id)` or `REVDET_PREV(rv)` |
| `group` | `opens(id)` on SPAN and on an island root LABEL; `member(id)` on its members |
| `frag[]` | value fragments (typed piece lists): condition, source, count, clamp |
| `reads` | filled from the fragments' typed read pieces, and by compound renderers from their operands |
| `deleg` | the kit-site handle (`mf_site *`, hooks, DelegSite id), the callsite callee and edges, or the clskit class |
| `at`, `end` | the body's uncut length before and after the record (tiling) |
| `verdict` | walk 3: KEEP, DELETE (tombstone) or UNTRAIL (retag) |
| `role` | the listing's text. A role is printed only as a COMMENT piece by the LABEL renderer, never as code |

**One builder per kind**, each a macro passing `__LINE__`: `VM_LABEL`, `VM_GOTO`, `VM_FAIL`,
`VM_BRANCH`, `VM_GUARD`/`VM_GUARD_END`, `VM_SWITCH` (holding its case list), `VM_PUSH`,
`VM_SET`, `VM_SNAPSHOT`, `VM_RESTORE`, `VM_CUT`, `VM_CUT_LOCAL`, `VM_CALL`, `VM_RETURN`,
`VM_CHECKPOINT`, `VM_WORK`, `VM_STEP`, `VM_CONSUME`, `VM_CONSUME_BACK`, `VM_SPAN`, `VM_SEEK`,
`VM_LSET`, `VM_BREF`, `VM_VAR`, `VM_CALLOUT`, `VM_ACCEPT`, `VM_WITNESS` (the test-only SIMD
witness block), and `vm_note` (annotation kinds: NOTE, RUNG, STRAT, PRUNE, which print
nothing).

A builder does five things, in order:

1. **Tiling check.** Assert that the body's uncut length equals the previous record's `end`.
   Otherwise it is an internal error naming the previous record's sid and the current line.
2. **Sid.** Assign the sid, before any verdict lookup.
3. **Verdict.** Consult the verdict map (walk 3 only; otherwise KEEP).
4. **Append** the record.
5. **Render** it at once into the body (`at`/`end` set around the render), then **lex** its
   fragment windows (Value fragments).

There is no "print" left in emit_vm.c's walk: a site builds, and the builder renders.

### Why kind can no longer be wrong

The control text of a statement, meaning its jump, its exit, its label reference, its block
braces and its write to the cursor, a slot, a local or run state, is printed by the renderer
of its kind from the record's operands, and by nothing else. So:

- the text's successors are the record's successors;
- the text's writes are the record's writes (renderer-owned writes are read off the kind
  row, fragment writes are refused);
- the text's reads are the record's reads (typed read pieces record them, and compound
  renderers read them off their operands).

The only judgement a site makes is WHICH builder it calls. If it calls the wrong one, the
program it emits is a different program. For (a) that is a red identity diff. For any later
build the record is the true description of the program that was emitted. There is nothing
to count.

### The one writer, structurally `[r8 FIX-4, SOUND-5]`

- **Tiling** (above). It runs on every compile and checks lengths, not names. So it catches
  a raw write however the pointer was obtained:
  - through `&v->cx->job->vmsb` (Job stays a complete type, and the buffer stays Job-owned
    for the longjmp cleanup, exactly as today);
  - through a helper that was handed it;
  - as a comment-tier write under `-fno-comments` (the uncut length counts muted bytes).

  A truncation (`b->len = 0`) is caught too.
- **The frame is one call.** `vm_stmt_frame(v, &facts)` writes the matcher's whole span in
  the artifact buffer in one call:
  - the head and declarations, `goto <p>_L0`, the body splice, the accept label and its
    return, the fail block;
  - then the notempty copy (a post-pass).

  `facts` carries `has_push`, `tracing`, `nkreset`, `has_linked_calls`, `has_budget`,
  `ncheck`, the rung bits, `nrev_total`, `nrevcaps`, the MRL and `\G` parameter
  declarations, and `ai_body`. No emit_vm.c code runs while the span is half written, and
  the entry checks at its end that the span's length equals the sum of its frame records
  plus the spliced body.
- **Exports.** These are the only ways the rest of the emitter sees the body:
  - `vm_stmt_program_bytes()` is `pcrec_sb_len_decide` of the body, for the entry-shape knee
    and the `RX_VM_PROGRAM_BYTES` stamp;
  - `vm_stmt_text()` is a `const char *` view, for `vm_cls_reads`;
  - `vm_stmt_respell()` is the class-read post-pass, moved verbatim.
- **Static scan, an early warning only** (`tests/codegen/run_stmt_writer.sh`). Outside
  vm_stmt.c, `src/gen/` names `vmsb` nowhere. `src/core/compile.c` names it on its five
  lines today (308 free, 2365 `.cx`, 2385 comments, 2435 `abort_over`, 3206 the balance
  list), plus the Job declaration in `internal.h` and the comment in `limits.def`.
  `pcrec_memfn_emit`, `pcrec_clskit_emit_inline` and `pcrec_callsite_emit` are called from
  vm_stmt.c only. Every `VM_LIT` argument in emit_vm.c lexes clean under R1-R2.

### The kind table and the analysis rules

ONE table, `vm_kind_rows[]`. Every analysis reads its own column, the renderer column says
what prints, and nothing else decides. Notation as in rev 2: `s` is a slot, `L` a label, R
the record's reads, W(g) the slots region g can write, R_c the return label of call site c,
"unwind" the fail label, "exit" a return out of the matcher. A row whose analysis columns are
not yet written is UNMODELLED. Its function is V0, so the table can grow a row at a time.

| kind | renderer (spellings) | successors | reads | writes | copies (must) | MAYFRAMES | FIRST+ | verdict | legacy events |
|---|---|---|---|---|---|---|---|---|---|
| LABEL | `[// role]` + `<p>_L<n>: __attribute__((unused));` (role, bare) | next | — | — | meet of preds | join of preds | continue; if `opens(ISLAND id, F, nullable)`: F ∪= F_isl, open `id`, continue iff nullable | — | [island], label |
| COMMENT piece | `// text` under the comment gate (only inside LABEL and the BREF compound) | — | — | — | — | — | — | — | — |
| GOTO | `goto <p>_L<n>;`, preceded by a nested CHECKPOINT when `ckpt` places one | L | — | — | — | — | continue at L | — | [note], goto |
| FAIL | `goto <p>_fail;` (no operand: it cannot be conditional) | unwind | — | — | — | — | path ends | — | fail |
| BRANCH | `if (C) T` where T renders `tgt`: `goto <p>_fail;` / `goto <p>_L<n>;` / `{ <P>_TRAIL_CHECK(); goto <p>_L<n>; }` (nested CHECKPOINT) / `return <P>_R_<code>;` | tgt, next | R(C) | — | — | — | fork both (C peeks, moves nothing); a `member(id)` BRANCH (island compare): continue iff `id` open, else OPAQUE | — | as today per site (assert, goto, note, none) |
| GUARD / GUARD_END | `if (C) {` … `}` (braced); `if (C) ` + ONE inline record (inline); `if (C) { ` + inline records + ` }` (inline braced) | GUARD: the block AND the record after its GUARD_END; END: next | R(C) | — | — (the join meets) | — | fork both | — | none |
| SWITCH (case list) | `if (scan_position + d < subject_length) switch (subject[scan_position + d]) {` + `case b: goto <p>_L<n>;`… + `}` | every case label, next | subject | — | — | — | `member(id)`: continue to every case iff `id` open, else OPAQUE | — | goto per case |
| PUSH | `<P>_PUSH([n, ]&&<p>_L<n>, POS);` POS renders `pos` | next, L (resumes at pos) | live-in(L) ∪ R | frames | L inherits the pusher's facts | adds L | pos CURSOR: fork; pos SPAN(id): continue iff `id` open, else OPAQUE; REVDET_PREV: OPAQUE | D: by site kind | push |
| SET | `<P>_SET(<slot>, SRC);` | next | R(SRC) | s (trailed) | kill s; gen s == t iff SRC is exactly SLOT(t), t ≠ s (a self-copy is refused by the builder) | pass | continue iff non-effect (rev 1's rule) | V3, V4, V5 | set |
| SNAPSHOT (call c, entry j) | `<P>_SET(<slot>, slot_values[<slot>]);` (the source is derived, there is no operand) | next | none | trail only (positional) | none | pass | continue | V1 | set |
| RESTORE (at R_c, ordinal j) | `<P>_SET(<slot>, run->trail[run->resume_stack[run->call_top].trail_mark + j].saved_value);` (j = rank among the KEPT snapshots of its site) | next | trail | s | kill s | pass | continue | V2 | set |
| CUT | `[WORK]` + `<P>_CUT(<slot>);` | next | mark slot | frames discarded | unchanged | unchanged | OPAQUE | — | [note], cut |
| CUT_LOCAL | `run->resume_depth = <p>_rv<i>_frame_mark;` | next | the mark local | frames discarded | unchanged | unchanged | OPAQUE | — | note / none |
| CALL c | `<P>_CALL(&&<p>_L<R_c>, scan_position);` | next (the SNAPSHOT records; the callee edge is the following GOTO) | W(g) ∩ live-after(R_c) | call frame | none after | pass | continue | — | call |
| RETURN | the fixed region-exit block (`emit_vm.c:8503`) | every R_c of the region, exit (capacity guard) | live-in of every R_c | call_top | none at any R_c | pass | fork to every R_c | — | return |
| CHECKPOINT (standalone, or nested in GOTO/BRANCH) | `<P>_TRAIL_CHECK();` | next | — | trail only (compaction) | — | — | continue | — (a sid, never a verdict) | note |
| WORK | `<indent><P>_CHARGE_WORK(N);` | next, exit (R_WORK, the macro's) | R(N) | work counter | — | — | continue | — | note |
| STEP | `if (--run->steps_left < 0) return <P>_R_STEPS;` | next, exit (R_STEPS) | — | steps counter | — | — | continue | — | none |
| CONSUME (class, lit, wclass) | `if (C) { ADV; goto <p>_L<n>; }`, with ADV `scan_position++` / `scan_position += k`; wclass: its fixed decode block | target, next | subject | cursor (forward) | — | — | F ∪= the first byte's class; stop | — | consume |
| CONSUME_BACK | `if (C) { <p>_rv<i>_cursor--; goto <p>_L<n>; }` | target, next | subject, the local | the local | — | — | OPAQUE | — | consume |
| SPAN (opens id: class, min, stride) | block: `{` [`it_`] [`lim_`] `<p>_span_cursor = scan_position;` KIT `}`; init only (rmin = 0 lazy): `<p>_span_cursor = scan_position;` | next | subject | the span cursor | — | — | F ∪= class; open `id`; continue iff min = 0 | — | none |
| SEEK SPAN_COMMIT (member id) | `scan_position = <p>_span_cursor;` | next | the span cursor | cursor | — | — | continue iff `id` open, else OPAQUE | — | none |
| SEEK ADVANCE k (member island id) | `scan_position += k;` | next | — | cursor | — | — | continue iff `id` open, else OPAQUE | — | none |
| SEEK RESTORE s / BACKSTEP k | `scan_position = (size_t)slot_values[s];` / `scan_position = <p>_back_step(subject, subject_length, scan_position, k);` | next | s / — | cursor | — | — | OPAQUE | — | note / none |
| LSET x | `x = SRC;` / `x++;` / `x += k;` / `x -= k;` / `{ int i_; for (…) x[i_] = 0; }`; indented, or inline inside a GUARD | next | R(SRC) | local x (untrailed) | — | — | continue iff non-effect (rev 1's rule) | never | none |
| BREF (refs, caseless) | the fixed block `emit_vm.c:8829-8875`: per-ref selection, its comment, `goto <p>_fail` twice, nested WORK, advance, `goto L` | target, unwind | 2g, 2g+1 per ref; the work count | cursor (unknown amount) | — | — | OPAQUE | — | fail, [note], fail, goto |
| VAR (slot, caseless) | the fixed block `emit_vm.c:8917-8936` | target, unwind | caller variables (constant) | cursor (unknown amount) | — | — | OPAQUE | — | [note], fail, goto |
| CALLOUT (site, view, binding) | the fixed block `emit_vm.c:9089-9154`; its edge rows are printed by `pcrec_callsite_emit` called FROM the renderer, with edge text rendered from typed targets | the row table's applicable actions: SUCCESS → target, FAIL → unwind, PROPAGATE/GIVEUP → exit, TRAP → abort (no successor) | `slot_values[0 .. 2*ncap-1]`, the caller's vars | slot 0 transiently (net none); `run->callee_gave_up` on the give-up exit | kill all | pass | OPAQUE | — | callout, fail, goto |
| ACCEPT | `goto <p>_accept;` | accept | slots `0 .. 2*NCAPS-1` | — | — | — | F = all, E = true | — | accept |
| frame (one entry): DECL / ENTRY / BODY / ACCEPT_RETURN / UNWIND / TRACE | today's text, moved | ENTRY: L0; UNWIND: the PUSH edges | per row, from the facts | DECL: locals at entry | entry: no facts | entry: {} | — | — | none |
| NOTEMPTY_GUARD (the copy's accept test) | `if (scan_position == ctx->pos) goto <p>_fail;` (in the copy) | accept, unwind | — | — | — | — | (F = all) | — | none |
| WITNESS (test build only) | the kit's SIMD witness block | next | — | — | — | — | continue | — | none |
| annotations: NOTE / RUNG / STRAT / PRUNE | (print nothing) | — | — | — | — | — | continue | — | as today |

**The rules the rows encode** (rev 2's three, corrected):

1. **A guard is an edge, not a clause** (unchanged, `[r6 S-1]`). The inline spellings print
   no brace and are the same row.
2. **A path ends only where the text ends it.** That holds by construction now: only FAIL,
   ACCEPT, RETURN, the frame's UNWIND and a TRAP row end a path, and each one's renderer
   prints the unconditional form.
3. **FIRST+ and group membership** `[r8 SOUND-1, SOUND-2]`. FIRST+ walks paths carrying the
   set O of group ids OPENED on that path. A record carrying `opens(id)` (SPAN, or an island
   root LABEL) applies its own row and adds `id` to O. A record carrying `member(id)`
   continues iff `id` ∈ O, and is OPAQUE otherwise. Every other cursor move is OPAQUE:
   SEEK RESTORE, BACKSTEP, BREF, VAR, CALLOUT and CONSUME_BACK.
   - O is part of the walk state (visited keyed by record and O), so it stays finite.
   - Ids are per record, so two rungs that share the one `<p>_span_cursor` local are told
     apart.
   - Continuing after an opener can only ADD bytes to F (the opener already added the
     group's first-byte set). That is the safe direction for D.
   - Width-1 lookbehinds are peeks (BRANCH), as r6 and r8 probed.

**Unchanged from rev 2** (restated where the build needs it):

- FIRST+'s column: program altitude, follows calls, every cut OPAQUE. The family includes
  [OPT-ALTCLS] stage 2 `[r6 SEAM-G1]`.
- The non-effect rule.
- D's admission table D1-D4: it reads PUSH's site-kind enum, never role text `[r3 SLOTS-5]`.
- The rounds (A repeated, B once, in memory on walk 2's records, with the faithfulness
  invariant `[r6 SEAM-2]`).
- "C in the one table".

The slot-flow table:

| row | site | verdict | round | rendered |
|---|---|---|---|---|
| V0 | the function holds a refused fragment or an UNMODELLED row | KEEP everywhere; D declines | — | `<P>_SET` |
| V1 | SNAPSHOT of s at call c | DELETE iff V2 deletes the RESTORE of s at R_c; else KEEP. Never COPY, never UNTRAIL | A | nothing / `<P>_SET` |
| V2 | RESTORE of s at R_c | DELETE iff s ∉ K_c = W(g) ∩ live-after(R_c); else KEEP. A kept restore's ordinal is its rank among the KEPT snapshots of its site (a renderer operand) `[r6 S-6]` | A | nothing / the restore |
| V3 | SET: s dead after the site | DELETE | A1 | nothing |
| V4 | SET: s == SRC on every path, and SRC is not SLOT(s) | DELETE (COPY) | A2 | nothing |
| V5 | SET: s dead at the attempt entry and at every L in MAYFRAMES | UNTRAIL | B | `<P>_SETU` |
| V6 | otherwise | KEEP | — | `<P>_SET` |

K_c and W, and the S-6 codegen assertion (at each call site, the kept SNAPSHOT list and the
kept RESTORE list are the same slot sequence, checked on walk 3's records), are as rev 2.

## Renderers and byte identity

### Every site maps to one renderer (`render_check.py`, `render_check.log`)

`calls3.py` lists every print call that writes the body (`v->b` and its aliases `b`, `bb`, `t`)
or the matcher's span in the artifact, with its FULL format text (`calls.tsv`, 159 rows: 132
body, 24 frame, 3 copy). `render_check.py` then does three things:

- it groups the 132 body calls into statements in emission order, with a marker for each
  delegated or non-literal piece (the class test, a kit window, a context side, the
  callsite rows, a nested WORK);
- it expands the six `%s` arguments that are themselves C text today (`vm_trail_check_text`,
  the two ternary literal arguments) into what their typed operand renders;
- it matches each statement against its (kind, spelling) TEMPLATE, a regular expression of
  the renderer's fixed text with operand slots.

Results:

| item | count |
|---|---|
| statement spellings checked | 98 (91 template, 7 compound verbatim) |
| distinct (kind, spelling) renderers | 47 |
| body calls covered | 130 of 132 (+ `vm_cls_test`'s class-read puts, a CLS piece; + `vm_cls_respell`, the post-pass) |
| MATCH | 98 of 98 |
| fragment groups lexed | every condition, source, count and clamp: 0 control tokens, 0 writes |
| literal state reads inside fragments (become typed read pieces) | 16 statements with `slot_values[`, 2 with `run->` |

By kind: BRANCH 33 spellings, LSET 11, GUARD/GUARD_END 6 + 6, SEEK 6, SPAN 3, GUARD+LSET
inline 3, CONSUME 3, FRAGMENT 3, and one or two each for the rest.

What makes a template a proof of byte identity: a renderer prints its template's fixed text
with the site's operands in the slots. The operands are the same values today's calls pass:
the prefix, label ids, slot spellings (`vm_slot_expr`), local names, integers, class reads
(`vm_cls_read` or the clskit inline text), kit windows (the kit, called with the same
arguments into the same buffer at the same point) and target texts. So it prints the same
bytes.

The script checks the TEXT side. The OPERAND side (that each operand is passed today's
value) is what the identity diff proves.

**Spelling operands, not new kinds.** A site's text variants are layout operands of one kind:

- the traced PUSH;
- named and numbered SET slots;
- the WORK indent;
- inline and braced GUARDs;
- the block and init-only SPAN;
- `neg` and the side of a context row;
- a ref's `else` prefix and its trailing separator in BREF;
- the caller and definition-site views in CALLOUT.

Each is decided where today's code decides it, so no new decision exists.

**Moved verbatim** (code motion into vm_stmt.c, with no template needed):

- the frame (24 calls);
- the notempty copy (3 calls; its text is a byte copy of the rendered span, so it follows
  the renderers);
- `vm_cls_respell` (the same strstr pass over the body, after the walk and after the tiling
  check);
- the compound skeletons of RETURN, BREF, VAR, CALLOUT and WCLASS.

**What else must hold, and why it does:**

| hazard | why (a) is unchanged |
|---|---|
| the listing | each renderer emits today's legacy events, in today's order: LABEL emits VE_ISLAND then VE_LABEL; BREF emits fail, [note], fail, goto; GOTO emits the nested checkpoint's note before its goto. `vm_note` annotations stay at their positions. The listing reads events, not text interleaving |
| counters that steer emission | `nset` and `lbl_nset` (D183 placement), `ncheck`, `nwork`, `nclamp`, `emitted_push`, `emitted_set`, `has_push` and `nlitrun` move into the builders at the same program points. No decision reads the body's length mid-walk (r8 HELD) |
| the comment axis | COMMENT pieces go through the same `pcrec_sb_cmt_open`/`close` gate into the body. The kit's comments land in the body itself |
| SIMD, scaffold, layout | the kit writes into the body in place, so the bracket records and the mid-line check see the body's own last byte |
| class-read side effects | `vm_cls_note_read` runs once per CLS piece BUILD, as today (once per `vm_cls_test` call). Rendering a members fragment twice (into the kit's input and into 5230's condition) notes nothing new, exactly as today's string reuse |
| kit side effects | `pcrec_memfn_emit` is called once per record render, with the same site and hooks, as today's one call. (c)'s three walks are rev 2's concern, unchanged |
| the post-pass | it runs after the walk, on the same text |

### The evidence plan for (a) (it lands alone, with no abi bump)

| # | evidence | population | gate |
|---|---|---|---|
| E1 | two-compiler identity diff: (a)'s parent against (a), C artifact AND `--emit-ir` listing, byte for byte | every corpus `pattern`/`pattern-esc` line (2,568 distinct by `emit_vm.c`'s own count) with its own flags and features; default engine and `--engine=vm`; both prefixes; `-e utf8` where labelled; then the same population under `-fcomments`, under `-fmemfn-simd`, under `--trace`, and under every deny/force arm `make test-axes` sweeps (`src/core/axes.def`); plus every bench text (pcrec-bench, read-only) with its flags | 0 differing files. A heavy queue job outside 19:00-00:00. The landing commit and the lane report carry it (§5.4's precedent) |
| E2 | `make test-memfn-guarded` (run_simd_guarded.sh) | the witness build | green: `RX_VM_PROGRAM_BYTES` and the knee are unchanged |
| E3 | `make test` (async, as always), `make strict`, `make test-codegen`, `run_recursion_identity.sh` | — | green; FILEPIN unmoved; abi unchanged |
| E4 | tiling (internal error on any foreign write) | every compile in E1-E3 | 0 internal errors |
| E5 | fragment census (`--harness=stmt-records`: refusals by class) | E1's whole population | 0 refusals, 0 UNMODELLED |
| E6 | renderer round-trip (Test cells: RT) | every record of E1's default population | 0 disagreements |
| E7 | sabotage rows M1-M15 (Test cells) | their cells | every row DETECTED or refused as stated |

The E1 driver is written with (a) (scratch only; rev 2's identity-diff precedent). This lane
ran none of E1-E7: they need (a).

## Value fragments

### What a fragment is

A fragment is the only free text inside a statement. Its classes are the condition of a
BRANCH, GUARD, CONSUME or SWITCH; the source of a SET or LSET; the count of a WORK; the clamp
of a SPAN; the declaration values of the frame; and the delegated windows. Each class says,
by its builder or by the lexer, why it cannot carry control.

| class | builder | why it cannot hold control or a write | refusal |
|---|---|---|---|
| pcrec condition, source, count, clamp | `VmFrag` pieces: `VM_LIT(f, "…")` (the macro concatenates `"" s ""`, so only a string LITERAL compiles), `vm_frag_int`, `vm_frag_prefix`/`_up`, `vm_frag_slot(s)`, `vm_frag_local(l)`, `vm_frag_runstate(field)` (a read), `vm_frag_cls(ci, byte)`, `vm_frag_op(binop)` (one of C's non-assigning binary operators), `vm_frag_ident(name)` (checked `[A-Za-z_][A-Za-z0-9_]*`, not a label, not a scope name), `vm_frag_sub(f)` | no piece builder takes a label, a target, a statement or a free string. A control or write token could only be spelled inside a `VM_LIT` literal in emit_vm.c's source, which the static scan lexes and the runtime lexer refuses | static scan red (test time); V0 at compile (c); census count (a) |
| clskit inline class test (CLS piece) | pcrec's class kit, `pcrec_clskit_emit_inline`, called by the CLS piece's renderer | a pure membership expression over the byte operand | lexed (R1-R4) |
| kit span advance (SPAN's KIT window) | `pcrec_memfn_emit` at VMSPAN/VMSTRIDE, called by the SPAN renderer into the body | the kit's text is not typed: only the lexer stands here. Declared output: `<p>_span_cursor` (SPAN's write column) | lexed (R1-R4) → V0 |
| kit run compare (BRANCH and CONSUME KIT windows) | `vm_run_compare` → the kit, called by the renderer | as above; no outputs | lexed → V0 |
| callsite rows (CALLOUT) | NOT a fragment: `callsite_rows.c` is pcrec's own declared row table, and its edge texts are rendered from typed targets by the CALLOUT renderer. The record's edges are read from the same table (`pcrec_callsite_actions(f)`, a new byte-neutral export: the applicable rows' action column) | rows generate text and edges together (r8 FIX-10's member 3) | — |
| comment text (COMMENT piece) | the LABEL and BREF renderers | inside `//` under the comment gate. The renderer refuses text holding `\n` or `\r` or ending in `\` (a line splice would swallow the next line) | internal error (roles are pcrec's text) |
| frame declaration values (`ai_body`, the MRL and `\G` parameters) | moved verbatim with the frame | the frame's own facts | — |
| the SIMD witness block | the kit's test-only witness, called by WITNESS's renderer | test build only; a no-effect row | lexed |

### The lexer (rules and text domain)

**Text domain.** C tokens of the fragment window `[at, end)` of the body, outside comments
and outside string and char literals: a literal's bytes, which carry PATTERN bytes, are one
opaque token. Preprocessor lines are lexed in every arm.

The domain is the same at every comment setting and under `--trace` (trace text lives in
frame records, not fragments). So V0 cannot move with an axis that promises not to move code
`[r8 FIX-5 (1), SOUND-4 (i), (vi)]`.

**The rules.** They come from C's own classes and the artifact's own declaration lists. None
of them is a list chosen to identify a kind.

- **R1 control.** No `goto`, `return`, `setjmp`/`longjmp`, and no noreturn call (`abort`,
  `exit`, `_Exit`, `quick_exit`, `__builtin_trap`, `__builtin_unreachable`). No `#define`,
  `#undef`, `#include` or `#line`.
  - `break`, `continue` and `switch` are allowed: no loop or switch of the matcher body
    encloses a fragment, so C itself confines them (a top-level `break` is a compile error).
- **R2 labels.** No identifier naming a matcher label (`<p>_L<n>`, `<p>_fail`,
  `<p>_accept`). Every label reference is a renderer's. That also makes `&&label` and
  computed goto impossible.
- **R3 writes.** A matcher-scope identifier may only be READ. The scope is the frame's
  parameters plus its DECL record's locals, from the same facts that render them, after R
  the run-state locals included.
  - Read means: never followed (after any `[..]`, `.f` or `->f` chain) by an assignment
    operator or `++`/`--`, never preceded by `++`/`--`, and never the operand of unary `&`.
  - Exception: the class's declared outputs.
  - Calls are then harmless. A helper can see only what it is passed, and it cannot be
    passed an address of matcher state.
- **R4 names.** Every `<p>_`/`<P>_` identifier is a scope name or a helper the artifact
  defines with a PURE row in the helper registry. The registry is the table the prologue's
  helper writers fill (class bitmaps and atoms, `w2/4/8`, `decode`, `back_step`,
  `span_match*`, `wcls*`, the PRUNE macros, the kit's helpers), with a purity column. An
  unknown name refuses.

**The prototype** (`frag_lex.py`, `kit_census.py`; `kit_census.log`).

- 37 compiles (`census_pats.tsv` plus cscan.rxt:20) gave 49 kit windows in 16 shapes. They
  cover the span advance, the clamped and capped forms, the run compare (`rx_w2`/`memcmp`)
  and its brace and `"x}"` literals, UTF-8, `-fcomments` and `-fmemfn-simd` (no VM body
  site has a SIMD form today, as r8 found).
- 0 refused, 12 sabotages detected, 4 controls clean.
- The first run (`kit_census_run1.log`) refused the four `rx_class_atom<N>` windows of the
  cscan artifact. The prototype's hand list lacked that helper family, which the class kit
  writes into the prologue.
  - The refusal is the safe direction (V0: all KEEP, D declines), so a missing row costs
    speed, never answers.
  - It is also why R4 reads the registry the prologue's writers fill, and not a list
    someone types.

**What a refusal does.**

- In (a) nothing reads it: the census counts it (E5, 0 expected).
- From (c) on it makes the function V0 (Verdict identity across walks, FIX-9).
- A refusal in a pcrec piece is also a static-scan red at test time. One in a kit window
  also files a kit request (the kit's row contract: `memfn/docs/requests.md`, single-writer
  main; memory `pcrec-requests-are-mine-to-file`).

**FIX-3's buffer facts, one by one.**

- `cmt_dropped`: the kit's muted bytes are muted in the body.
- SIMD, scaffold and layout: the kit's brackets open and close in the body (balance-checked
  at compile end, as today's `vmsb` is).
- `.cx`: the body's.
- `abort_over`: the body's (a ladder trial's bound covers the kit's bytes, as today).
- The mid-line refusal: `pcrec_sb_simd_open` looks at the body's own last byte. In an
  expression window (the run compare) that byte is mid-line, so a SIMD bracket there is
  still refused, exactly as today.

## Verdict identity across walks

**The walks** (rev 2's, with V0 by walk) `[r8 FIX-9]`:

| walk | renders | read by | V0 found here |
|---|---|---|---|
| 1 | the stock program (R and the C-move rendering included) | D's FIRST+ (every slot write trailed) | D declines (walk 2 = walk 1), every verdict KEEP (walk 3 = walk 1): 1 emission |
| 2 | walk 1 with D's map (D adds SWITCH, PUSH and GOTO records; their only fragment is the renderer's fixed dispatch subject) | the rounds, in memory | walk 2 is discarded; the rounds run on walk 1's records and walk 3 applies them with D off: still at most 3 emissions |
| 3 | walk 2 with the slot-flow map: the final C, records and listing | every derived fact | impossible: verdicts change no fragment (a tombstone renders nothing, a retag renders `<P>_SETU`), so a refusal here is an internal error |

**The statement identity** is rev 2's `sid = (node, instance, line, k)`. `line` is the builder
macro's `__LINE__`. Two additions:

- A nested CHECKPOINT (GOTO's or BRANCH's `jump` target) is its own record, with the
  enclosing builder's line and its own `k`, so it can vanish in walk 3 without shifting the
  enclosing record's sid.
- SNAPSHOT and RESTORE have their own builder lines, so V1 and V2 sites are keyed apart from
  SETs at the same call site.

Why it survives the walks is as rev 2 (r8 HELD both legs, with the note that a helper reused
by D carries the helper's line, which is harmless because D's map keys on the A_ALT node).

**What the final walk owns**: rev 2's list (the push total, the listing's pre-pass
`resume-points` row with the D-denied comparison, D183 placement and margin from walk 3's
KEEP SETs, FRAMELESS and the reseed calibration bit, the stamps, `RX_VM_PROGRAM_BYTES`, the
listing, the notempty copy).

**The checks** (stage (c)'s gate 2a; levers test-only):

| check | what it asserts | can it fail on a keying slip? |
|---|---|---|
| K1 all-KEEP | walk 3 under `--harness=keep-slot-writes`, and walk 2 under `-fno-<dispatch>`, render byte-identical C and records to their input walk | no (necessary only) |
| K2 one-entry maps `[r8 FIX-2]` | Under `--harness=pin-nset` (D183's `nset` counts SET records whatever their verdict, so walk 3's margin and every standalone and nested checkpoint equal walk 2's), for the first N VM artifacts and every SET site k (capped per artifact): `{k: DELETE}`, and `{k: UNTRAIL}` under a SPAN or GUARD, changes EXACTLY record k in the record stream (`--harness=stmt-records`): a tombstone or a retag, with every other record's kind, operands and rendered bytes unchanged. In the C, k's bytes change in the matcher and again in the notempty copy where it exists. Snapshot sites take PAIR entries `{(SNAPSHOT j of c, RESTORE j at R_c): DELETE}`; the allowed extra moves are that site's later RESTOREs, whose `j` operand drops by one (enumerated, not exempted). A lone SNAPSHOT entry is refused by the map loader | yes |
| K3 cross-walk sids | every walk-3 record's sid exists in walk 2 with the same kind and operands; the differences are tombstones (DELETE), retags (UNTRAIL), renumbered RESTORE ordinals, and CHECKPOINT records (standalone or nested) free to vanish. The rounds' final in-memory list re-rendered equals walk 3's records modulo checkpoints | yes |
| K4 KEEP-only margin (new) | without the pin, the `margin` constant `vm_emit_trail_compact` prints equals the number of KEEP (not DELETE, not UNTRAIL) SET records of walk 3; checkpoint give-ups are swept on the build (gates 2d/2e) | yes (a margin from walk 2 is red) |

**Sabotages:**

- SAB-ORD (rev 1's ordinal keying) on cell K2a: K2 and K3 red.
- SAB-SKIP (a DELETE does not advance `k`) on cell K2b: K2 red.
- SAB-PIN (pin-nset ignored) on K2a: K2 red on the margin record. This shows K2's exactness
  depends on the pin, as stated.

## Gates, EXPECTED-MOVES and STEP 0

**G1, restated** `[r6 SEAM-5, SEAM-6; r8 FIX-7]`:

- Answers are identical to stock wherever stock answers, captures included.
- Never a new give-up at a STAMPED capacity. Where a stamped capacity lies inside a
  pattern's D183 gap band, this sentence governs.
- At an unstamped `ntrail` at or above the plain trail's need, never a new give-up either.
- Below that, inside the gap band, a give-up may move in both directions (limits §4
  paragraph 3).
- Where stock gives up (FRAMES, WORK, STEPS), the build may answer, and that answer is
  libpcre2's.

The other goals (G2-G5) and the non-goals are rev 2's.

**EXPECTED-MOVES** `[r8 FIX-8]`. The manifest is `tests/vm/expected_moves.tsv`, one row per
cell per arm that moves it, with columns:

- cell (`file:line`) and flags;
- the arm: D's deny flag, or `--harness=keep-slot-writes`;
- the stock give-up kind;
- the libpcre2 answer;
- the stage and the reason.

Its rows start as rev 2's: framebuffer.rxt cell 1, sr_depth.rxt:58-59, W6's four, and 0a's
finds, each on the ONE arm that moves it (D-caused on D's arm; slot-flow on the
keep-slot-writes arm).

- **Executor.** `tests/vm/run_expected_moves.sh`, a `make test` section `test-vm-moves`. Per
  row, it requires all three of:
  - the default build answers the libpcre2 column;
  - the row's arm gives up with the listed kind;
  - live libpcre2 equals the column, when libpcre2 is present (a loud SKIP when it is
    absent, on PC-3's precedent; the committed column is still checked).

  A listed row that does not move is red. The manifest is a list, never a count.
- **Unlisted moves.** They stay `run_axes.sh`'s UNALLOWED GIVEUP1 red (AXIS FAIL). For a cell
  in the manifest, run_axes' allowance lookup reads the manifest row: it is allowed only on
  the row's arm and only in the row's direction (default answers, arm gives up). So the
  build's NEW give-up (the other direction) stays red. No direction-blind `GIVEUP1_ALLOWANCE`
  row is written for these cells. The existing `-fno-req-byte|…sr_depth.rxt:*` rows are
  re-triaged when the default's answers move `[r6 SEAM-5c]`.

**Stage gates by landing:**

| landing | gate |
|---|---|
| (a) the record is the source | E1-E7 above |
| (b) R | answer identity on the corpus; R's guard on the PREPROCESSED matcher (rev 2, `[r6 S-8]`); sabotages W3, the steps_left write-back, the compaction reload, SAB-MACRO; the run-state fields join the scope list as RUNSTATE (R3) with the census still 0 |
| (c) 2a walks, no verdicts | K1; K2, K3, K4 with SAB-ORD, SAB-SKIP and SAB-PIN detected |
| (c) 2b D stage 1 | corpus answers equal `-fno-<dispatch>` except EXPECTED-MOVES (`test-vm-moves` green); W6 moves; W7a, W7b; W10-W13, W17; cells C2b, C2c, C3a, C3b, C5a, C5b, C5c, C7a, C7b; the size rung |
| (c) 2c C-move | identity; K36's witnesses; C6 with the S-6 assertion |
| (c) 2d round A | corpus answers equal `--harness=keep-slot-writes` except EXPECTED-MOVES; W2, W8, W18; C1, C2a, C6, C8; the BUILD's ntrail sweep (below) |
| (c) 2e round B | as 2d; W14-W16; W4's sabotage row (REACH gap noted) |

**The ntrail sweep on the build** (gates 2d and 2e) `[r8 FIX-7]`: `_search_in` at every
ntrail from 1 to the pattern's stamped capacity + 64, build against stock, on:

- `^(\((?:[^()]|(?1))*\))$`;
- the possessive nest `^(\((?:[^()]++|(?1))*+\))$`;
- an oscillating-kept-set shape;
- framebuffer.rxt's pattern, around its stamped 3072.

Red on a new give-up at a stamped capacity, or at or above the plain trail's need. A move
inside the gap band is listed, not red.

**A D27 spec-first author** for (c), as rev 2.

**STEP 0** (one heavy job after (a) lands, before (c)'s build go; outside 19:00-00:00):

- Cards 0a-0j and 0l are as rev 2.
- 0k moves onto the build (above). It is replaced in STEP 0 by a prototype-side smoke run of
  the same shapes, reported as evidence only.
- **0m (restated)**: the fragment census (E5) over the corpus and bench, with every axis. Its
  output is refusals by class and rule, and UNMODELLED rows. Gate: 0.
- **0n (restated)** `[r8 FIX-7]`: the renderer ROUND-TRIP becomes a STANDING check (Test
  cells: RT), not a one-shot card.
  - Its reader (`tests/vm/vmgraph.py`, revised to rev 3's rows) parses each record's
    rendered bytes into kind, successors, writes and reads, and compares them with the
    record's row.
  - A disagreement is triaged both ways: a renderer bug or a reader bug, neither presumed
    right.
  - It is the one place an independent implementation reads the text. What it controls is
    the renderers, the only trusted base left.

## Test cells

Every cell is an `.rxt` line in the build's corpus file (`tests/vm/opt_witness.rxt`, new in
(c)), run by `bash tests/harness/run.sh tests/vm/opt_witness.rxt`. Its sabotage runs as
`bash tests/mech/run_sabotage_matrix.sh S<id>`, with ids from the range the build brief
names (this lane was given none).

Expected answers are base answers equal to libpcre2 10.46. For rev 3's new cells, run
`S=<scratch> PCREC=<merged build/pcrec> bash docs/dev/lanes/vmcons3_evidence/cells.sh`
(`cells.log`). The carried cells are in rev 2's `cells.log`.

**New in rev 3 (review r8):**

| cell | rule row guarded | pattern, flags, subjects | expected (= libpcre2) | sabotage that must turn it red |
|---|---|---|---|---|
| C5b | SPAN init-only opener; member by id `[r8 SOUND-1]` | `^(?:.*?x\|y)(z)`, `--features all`: `axz` / `aaxz` / `xz` / `yz` | 0:0,3 1:2,3 / 0:0,4 1:3,4 / 0:0,2 1:1,2 / 0:0,2 1:1,2 | "a span-cursor PUSH with no SPAN opener on the path is a member" (r8's twin: `axz`, `aaxz` NOMATCH) |
| C5c | SPAN block spelling (lazy, rmin ≥ 1) | `^(?:[ab]{2,}?b\|y)(z)`, `--features all`: `abbz` / `aabz` / `abz` / `ababz` / `yz` | 0:0,4 1:3,4 / 0:0,4 1:3,4 / nomatch / 0:0,5 1:4,5 / 0:0,2 1:1,2 | "SPAN contributes nothing" |
| C7a | island opener on the root LABEL `[r8 SOUND-2]` | `^(?:\d+y\|(?:ab\|abc\|abcd\|abcde))(z)`, `--features all -fno-altcls-factor` (one-child root): `abz` / `abcz` / `abcdez` / `12yz` | 0:0,3 1:2,3 / 0:0,4 1:3,4 / 0:0,6 1:5,6 / 0:0,4 1:3,4 | "ISLAND contributes nothing"; "a member without its opener continues" (r8's twin: the first three NOMATCH) |
| C7b | island opener, SWITCH root | `^(?:\d+y\|(?:ab\|abc\|cd\|cde))(z)`, `--features all` (default flags; `RX_VM_ALT_ISLANDS 1`, root `switch`): `abz` / `abcz` / `cdz` / `cdez` / `12yz` / `xz` | 0:0,3 1:2,3 / 0:0,4 1:3,4 / 0:0,3 1:2,3 / 0:0,4 1:3,4 / 0:0,4 1:3,4 / nomatch | as C7a |
| C6 | SNAPSHOT kind; kept-ordinal restore `[r8 SOUND-7; r6 S-6]` | `^(x(?>a(?1)?b)y)$`, `--features all --engine=vm -fno-splice-calls`: `xaby` / `xaxabyby` / `xaxaxabybyby` / `xay` / `xaxaby` | 1:0,4 / 1:0,8 / 1:0,12 / nomatch / nomatch | "snapshot built as SET" (the builder's refusal fires; with it removed, V4's self-copy clause still keeps it, so the twin needs both removed: 1:-1,8 / 1:2,12); "restores keep ORIGINAL ordinals" (the S-6 assertion fires) |
| C8 | FAIL has no condition `[r8 SOUND-6]` | `^(a)b+c`, `--features all`: `abbc` / `abc` / `ac` | 0:0,4 1:0,1 / 0:0,3 1:0,1 / nomatch | mis-typing row M1 (the premise twin: 1:-1,-1) |

**Carried from rev 2** (unchanged, commands in rev 2's Test cells): C1, C2a, C2b, C2c, C3a,
C3b, C5a, K2a, K2b, RM, W1-W18.

**The mis-typing table** (the r8 process change: one MIS-TYPED record per kind class, and what
makes it impossible or catches it). Each row is a check of (a) or (c) as noted.

| # | mis-typed record | what makes it impossible, or what catches it | cell / check |
|---|---|---|---|
| M1 | a conditional fail typed FAIL (r8 SOUND-6) | FAIL's builder has no condition operand. Dropping the condition changes the program (identity red in (a)); the record is then true | C8; E1; renderer round-trip unit row "FAIL" |
| M2 | a conditional jump typed GOTO | the same, for GOTO | E1; round-trip |
| M3 | a CASE as a standalone GOTO | no CASE builder exists: SWITCH holds its case list | compile error |
| M4 | an LSET typed COMMENT (r8 FIX-6's mirror) | a COMMENT piece prints inside `//` (no code). The comment-class check refuses `\n`, `\r` and a trailing `\` (no escape from the comment) | sabotage "role ending in `\`": internal error |
| M5 | a local write folded into a fragment | R3 (the frame's scope list) | `run_frag_lex.sh` row "local write" (prototype: DETECTED) |
| M6 | a cursor write as an LSET | `VmLocal` excludes the cursor: compile error. In a fragment: R3 | compile; lexer row "cursor write" (DETECTED) |
| M7 | a SNAPSHOT as a SET (r8 SOUND-7) | `vm_set` refuses a self-copy source; V4 excludes self-copies | C6 sabotage |
| M8 | a CUT_LOCAL as an LSET | `VmLocal` excludes run state; after R the fields are RUNSTATE (renderer-only) | compile; lexer row "run-state write" (DETECTED) |
| M9 | a checkpoint hidden in a BRANCH's text | only the `jump` target renders one, as a nested CHECKPOINT record | round-trip; K3 |
| M10 | an exit hidden in a macro (WORK, SET, PUSH, CALL) | the macro is printed only by its kind's renderer, whose row lists the macro's exits | round-trip |
| M11 | a goto, label or `return` in kit text (r8 FIX-1's class) | R1, R2 → V0 | lexer rows "goto", "return", "label name" (DETECTED) |
| M12 | a raw print into the body (r8 FIX-4) | tiling → internal error, by any route | sabotage "`pcrec_sb_puts(&v->cx->job->vmsb, ";")`" and "the same as a comment-tier write under `-fno-comments`" |
| M13 | a raw csb print inside the matcher span | the frame is one vm_stmt.c call, and it tiles itself | sabotage "a raw csb print added inside `vm_stmt_frame`" |
| M14 | a renderer printing a target its record does not hold | the round-trip's independent reader | sabotage "BRANCH renders `goto L(n+1)`" |
| M15 | an unknown helper with an effect called from a fragment | R4 (the helper registry's purity column) | lexer row "unknown helper" (DETECTED) |

**New standing checks** (each a `make test` section unless noted):

| check | what it runs | red on |
|---|---|---|
| ST `tests/codegen/run_stmt_writer.sh` (light) | the static scan; sabotages M12, M13 and the comment row M4 | any |
| FL `tests/vm/run_frag_lex.sh` (light) | the C lexer's own rows: the 12 refusal rows and 4 clean controls of `kit_census.py`, ported | a row not as stated |
| RT `tests/vm/run_render_roundtrip.sh` | (1) unit: every (kind, spelling) rendered with sample operands and read back; (2) corpus: every record of a fixed sample of VM artifacts (the witness file plus 200 corpus lines, ≤ 50 compiles per run or under the box lock) | any disagreement (triaged both ways) |
| CEN (census, card 0m then a section) | `--harness=stmt-records` census over the corpus: refusals by class and rule, UNMODELLED | any refusal or UNMODELLED |
| test-vm-moves | EXPECTED-MOVES (above) | a listed non-move; an answer not equal to the libpcre2 column |

## Cost

**(a) the record is the source**: size L (rev 2 said M), one lane, refactor class,
byte-identical, no abi event, lands first and alone.

| item | sites |
|---|---|
| new `src/gen/vm_stmt.c` + private header | the record type; `vm_kind_rows[]` (about 35 rows × 10 columns); 28 renderer functions for the 47 (kind, spelling) templates; the builders; about 11 piece builders; the fragment lexer (about 200 lines of C); tiling; the helper registry's purity table; the frame entry, the notempty copy and the respell post-pass (moved, about 350 lines); the `stmt-records` dump. About 1,300 lines in all |
| `emit_vm.c` statement sites rewritten as builder calls | 96 statement entries (98 spellings), covering 130 print calls in 32 functions |
| `vm_ev` calls folded into renderers or turned into `vm_note` | 54 |
| raw `slot_values[` formats → SLOT pieces, plus `vm_slot_ref`/`vm_slot_expr` callers | 31 + 10 |
| `vm_rolef` C-text fragments → typed operands or pieces (gotos → targets, reads → read pieces, cursor expressions → pos operands) | 22 |
| delegated calls moved into renderers (kit span, kit run, clskit inline, callsite) | 4 call sites, plus the site-handle operands |
| frame and copy calls moved | 24 + 3 |
| `callsite_rows.c` | one export, `pcrec_callsite_actions` (byte-neutral) |
| the SIMD witness | one WITNESS record |
| checks | ST, FL, RT, CEN; the E1 identity driver (scratch, evidence only) |
| docs | `src/gen/CLAUDE.md` (the new file); the guide's emission-primitive entry (the "five primitives" doctrine becomes "one builder per kind"); a D number for "the record is the source"; `ir_listing.md` unchanged (the listing is identical) |

- **Calibration.** About +1,300 / -650 in `src/gen` (about 350 of each side is code motion),
  and about +500 in tests and docs.
- **Risk: low to medium.** It is mechanical, and E1 is a byte gate, so a slip shows as a diff
  before landing. The new risk is a renderer bug in a spelling the corpus does not reach. RT's
  unit half renders every spelling.
- **Compile-time cost.** One record per statement (about 1,200 per artifact over rev 2's 24
  witnesses), a length compare per builder, and the lexer over fragment bytes only (a fraction
  of the body). Card 0i measures it in passing.

**(b) R**: size S-M, as rev 2. It is cheaper on top of (a): every run-state write is a
renderer's (CUT_LOCAL, STEP, WORK, RETURN, the frame's UNWIND), so R's change list is those
renderers plus the scope list's RUNSTATE class. No signature needs re-declaring (r8 FIX-6's
addendum dissolves).

**(c) the analysis build**: size L, two to three lanes, as rev 2. Additions in rev 3:

- the group-membership walk state (O);
- the SNAPSHOT/RESTORE rows;
- K4 and `pin-nset`;
- `test-vm-moves` and the direction-keyed lookup in `run_axes.sh`;
- the build's ntrail sweep.

**Flags** (memory `pcrec-flag-follows-caller-effect`; Frank's F11 ruling):

| change | public flag | test lever | stamp |
|---|---|---|---|
| (a) the record is the source | none (a refactor, proven at landing) | `--harness=stmt-records` (diagnostic only) | none |
| (b) R | none | none | none |
| C-move | none | none | none |
| D | ONE deny flag (working name `-fno-first-byte-dispatch`; final spelling per D174); never a force | — | `<PREFIX>_VM_DISPATCH_SITES` (a `stamp_kinds.c` row) |
| slot-flow verdicts | none | `--harness=keep-slot-writes`, `--harness=verdicts=FILE`, `--harness=pin-nset` (K2 only) | listing ops and a verdict-count row |

Flag bits: D's deny takes one, leaving 5 (with the filed bit-57 candidate). The [IFACE-PUSH]
hard trigger (≤ 4) is not reached.

**Filed, not built** (D77 triggers):

- **FIX-10's unlocks**, with r8's triggers:
  - u2: R's guard on records;
  - u3: size attribution per kind;
  - u4: the DFA emitter on the same primitive;
  - u5: stamps as records.
- **Rev 2's filed list**: D stage 2; stamped capacity shrink; per-cycle margins; a generic
  drop-verdict rung; a static measured-admission input; AD's unlocks; F20(b)/(d)/(e); F19(a);
  TG's packed entries.
- **NEW: a "declared-forward" check.** Do a plain-goto target's `ckpt = never` sites ever
  jump backward over a SET? Trigger: a D183 give-up that a checkpoint would have prevented.
  Today's sites print bare gotos where `vm_jump` is not used, and this design keeps that
  choice as an operand rather than re-deciding it.

**Questions for Frank** (carried from rev 2, unchanged, in plain words):

1. **Should the build land as three pieces or two?** The refactor (a) must land alone, and
   whether R and the analysis build land separately is open. Leaning: separately.
2. **Should only the alternation half of the dispatch be built now?** Leaning: yes.

The (a) cost growth is the manager's call (an answer-free choice).

**Standing questions (docs/design/CLAUDE.md).**

1. **Measurement regime: relevant, unchanged from rev 2** (warm, resident, the 7700X, gcc
   15.2 -O2, instructions; cycles in 0c under the quiet gate). This lane measured no rate.
2. **Independent control: relevant.**
   - Stock against the build, the oracle `.rxt` expectations, and libpcre2 for the moved
     give-ups.
   - NEW: the renderer round-trip, a second implementation (Python, text side) of the kind
     table's columns, now the control of the one trusted base (the renderers). The D27
     author for (c) is the control that does not share this author's alphabet.
   - For (a), the identity diff is the control: two compilers, one of which predates the
     design.
3. **What moves on regeneration: relevant.** (a): nothing; C, listing and FILEPIN are
   unmoved. (b): every VM artifact's matcher text. (c): rev 2's list.

## STATE AT HANDOFF

- STATE: complete (design and measurement, as briefed; no build).
- Rulings file `docs/dev/lanes/vmcons3_rulings.md`: empty when read at start, before each
  commit and before this report. Last entry applied: none.
- **Premise test: CONFIRMED.** r8 SOUND-6's conditional fails pass rev 2's signature typed as
  FAIL (count vectors equal). The twin moves group 1 to -1,-1 on `abbc` and `abc`; base and
  libpcre2 give 0,1 (`premise.log`).
- **STOP RULE: not triggered.** Every body statement class matches a renderer template (98 of
  98), the compounds and the frame move verbatim, and the kit writes in place. No class needs
  text the record cannot carry.
- OWED: none. E1-E7 need (a)'s build, so they are (a)'s landing gate, not this lane's runs.
- Box use, all single-process and light, all before 15:20 (the queue's make test was running;
  no timing job):
  - two scratch builds (lane/trailgc; main plus the trailgc diff);
  - 37 census compiles;
  - 7 cell compiles with their gcc builds and libpcre2 runs;
  - the premise twin;
  - a few probe compiles.
- Evidence (`docs/dev/lanes/vmcons3_evidence/`):
  - `premise.sh`, `sig_rev2.py`, `premise.log`;
  - `cells.sh`, `cells.log`;
  - `calls3.py`, `calls.tsv` (159 calls with full formats);
  - `render_check.py`, `render_check.log`;
  - `frag_lex.py`, `kit_census.py`, `kit_census.sh`, `census_pats.tsv`, `cscan.pat`,
    `kit_census.log`, `kit_census_run1.log` (the first run's helper-registry refusal);
  - `drv.c` and `p2.c` (r8's drivers, copied), `run.sh`.
- Scratch: `/var/tmp/pcrec-pcrec/scratch/vmcons3/` (`merged/` holds the tree and build;
  `premise/`, `cells/`, `census/`, `w/`).
- Next: a short re-check (soundness with the enumeration clause and the mis-typed-record
  probe, plus fix-induced). Then the build go for (a).
