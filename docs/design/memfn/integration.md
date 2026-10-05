# memory-functions: R1d, THE INTEGRATION MAP AND THE COMPOSITION MODEL

Owner row: `[MEMFN]` (docs/dev/plan.md), step R1d. Lane `memfnmap`,
2026-10-04, written from main at 8a41efd2 (abi 59), reading `lane/k82fix`
(abi 60, unmerged) for `req_admits[]`. DESIGN ONLY: nothing under `src/`,
`cli/`, `lib/` or `tests/` changes, and no emitted byte moves (D91). Every
table row, stamp, option and emitted text below is DESIGNED, not built.
Building any of it is an `abi` event plus a `docs/spec/` hunk (D76/D94,
D80), behind the trigger its plan step names (§6).

Frank (2026-10-04): *"Don't get too caught up with 'separate project'. We
need to integrate. We use decision tables to organize variants. SIMD
variants might slot into those tables cleanly if given the chance. What
does that mean? Separate projects may mean a product that can be used to
generate the code selected in the decision tables. Or if that doesn't
work, some things are in the remote project and some are local. That
said, a project that allows you to create bespoke high-speed memory
functions stands on its own."* And earlier: is there benefit in
constructing functions TAILORED to the need rather than a fixed set?

Inputs: `requirements.md` (R1: F1-F13, B1a/B1b/B2/B3, RB-*, N-*),
`isa_selection.md` (R1b), `isa_evaluation.md` (R1c), `survey.md` (R2),
`docs/design/compare_stack.md` (the L0-L4 layers, §2's site inventory),
D82 (the form slot), D91 (scalar first, two budgets), D119, D122 and its
addenda 2-3 (every form choice a `DFA_SELECT`-style row; SIMD later = one
row; SWAR admitted now), D139 (one class-form table, sites as bits), D144
item 4 (every optimization its own deny), D145 (generated-output licence
exception), and the tables themselves (§1).

---

## 0. Findings first

1. **SIMD slots into pcrec's tables as rows, but into the RIGHT table,
   and two of those tables do not exist yet.** pcrec has nine first-match
   tables that touch scanning, verifying or classifying (§1). Today every
   L3 table row fuses WHAT is scanned (one byte, a set, an offset set, a
   pinned run) with HOW the scan is spelled (`memchr`, a table walk, two
   leapfrogged `memchr` streams). Adding SIMD as rows of those tables
   would double them: `dfa_pfs[]` already doubles every form for its
   `-bounded` twin, and a vector twin of each would make it four times
   its WHAT count. The clean slot is a NEW nested table, **the scan-form
   table `SCAN_ROWS`** (§2.2). Every L3 emitter asks it "find the first
   position in `[pos, lim)` whose byte is in S". The vector rows, the SWAR
   rows that D122 addendum 3 admits now, and today's scalar spellings are
   all rows of it. This is compare_stack.md P5's "form chosen at compile
   time", built as a table. The in-loop skips (the stay skip, the scan
   edge's run loop, the VM's span scan) are the same table at other SITES,
   in the D139 shape: one table, sites as bits.

2. **Seven sites do not slot cleanly today, each for a stated reason
   (§2.4):**
   - (a) `ofs_test_emit_fn`'s scan arm is an `if`, not a table.
   - (b) the stay skip has no form selection, and its set bypasses the
     class table that D139 made the scan edge use.
   - (c) the scan edge's LOOP form is a named, unbuilt slot. Axis I picks
     the test, not the loop.
   - (d) `vm_emit_span_scan` has one loop text.
   - (e) two readers classify the prefilter by `strcmp` on row NAMES
     (`emit_dfa.c:6417`, `:6450`). A vector row with a new name would
     silently fall out of G1's elision and out of the re-seed density
     price.
   - (f) `emit_req_set_rest` spells k one-needle passes, with no form
     choice.
   - (g) structural, not a defect: **pcrec does not know the target
     architecture when it emits.** Its output is architecture-neutral C.
     So a pcrec-time predicate can only say "a vector form exists at
     every supported architecture's baseline" or "at the DECLARED level"
     (route A, `--isa`). The per-architecture spelling resolves at gcc
     time, inside preprocessor-selected text. That fact draws the
     boundary in item 3.

   Each of (a)-(f) is fixed by implement-then-replace (byte-identical)
   when its first non-scalar row lands, never ahead of it (D77).

3. **The boundary that works is a split (option c), drawn where the
   knowledge changes hands (§3).** The kit owns:
   - the per-ISA PRIMITIVES (load, classify, mask, first/last), as
     injectable text selected by predefined macros;
   - the COMPOSITION generator (descriptor in, C text out). It owns the
     loop skeleton, the short path, unrolling, the classifier per set
     shape per ISA, and the fixed reference functions.

   pcrec owns:
   - SELECTION: its tables, predicates over pattern facts, deny flags and
     stamps;
   - the OPERANDS, from its single sources (P2 cube, P3 run, P6 prior,
     minw/maxw);
   - FUSION, through hooks: the verify text at a hit, the DFA reseed and
     view bounds, the scalar fallback. The fallback is always pcrec's own
     next row, so there is never a second scalar spelling of one search
     (D122).

   The kit's internal tables answer only questions pcrec's tables do not
   ask (§3.4), so the result is two layers of one idiom, not two
   selectors. Option (a), a pure generator, is the same split with the
   primitives inlined into its output. Option (b), a header-only library
   with constant descriptors, is right for the stand-alone product and
   wrong as pcrec's only path. Gcc's constant propagation is not a
   guarantee (studies/simd1 §8), and a header the user must have breaks
   self-containment unless pcrec injects it.

4. **"Tailored, not fixed" is the composition model, and the fixed library
   falls out of it (§4).** A kernel is a composition of six primitive
   families, chosen by a first-match table keyed on:
   - set shape (which classifier);
   - span bounds (loop-free, one block, or a loop);
   - run/offset (one filter or a pinned pair);
   - density prior (unroll factor, and whether to iterate hits or restart
     per hit);
   - ISA capability.

   F1, F2, F3, F4, F5, F6, F9 and F13 are that composition at GENERIC
   parameters: a run-time operand, an unbounded span, an unknown density,
   the baseline ISA. The independent reference stays the scalar byte loop
   (N-6), NEVER the generic composition. A specialization checked against
   output of its own generator is a control that shares a source with
   what it controls (learnings.md §3, memory
   `pcrec-check-design-lessons`).

5. **Budgets that bind the design before any row is built (§5 Q14-Q16):**
   - **Deny bits:** 45 of the 64 `pcrec_options.flags` bits are taken
     (k82fix's `-fno-req-set-lead` is bit 45). One bit per vector row
     would exhaust them, so the recommendation is one bit per FAMILY plus
     the ISA level as a value option.
   - **Emitted-size caps (D84):** an un-declared build emits a two-arm
     `#if` ladder per vector site, which adds source bytes.
   - **The `abi` ritual:** any change to the kit's text moves emitted
     bytes, so every kit version bump is a pcrec `abi` event (D76/D94).

---

## 1. The table inventory

Every first-match table in the tree that selects, or sits directly above,
a scan / verify / classify form. "Walk" names the selection function.
Line numbers are main at 8a41efd2 unless marked k82fix.

### 1.1 The walk itself

`DFA_SELECT` (`src/gen/emit_dfa.c:4943`) over `dfa_select` (`:4931`): the
first entry whose `deny & flags` is clear and whose `applies(const DfaSel *)`
holds. `DfaCand` (`:3315`) is `{name, deny, applies}`, and every object
struct begins with one. `DfaSel` (`:3298`) carries `cx`, the machine `d`,
the `UnanchStart`, `forward` and a per-state `st`. Every list ends with
`cand_always`. clskit.c and runcmp.c spell the same idiom with their own
row structs (a predicate TAG plus an exhaustive `switch`), because their
inputs are a set and a run, not a `DfaSel`.

### 1.2 The tables

| # | table | file:line | selects | rows, in order (deny) | predicates read | each row's emitter emits today |
|---|---|---|---|---|---|---|
| T1 | `dfa_pfs[]`, AXIS B | `emit_dfa.c:6304`; walk `dfa_pf_of` `:6323` | the forward scan's CANDIDATE-START skip: what it scans and how | `run-pinned-bounded`, `run-pinned` (`NO_OFFSET_SKIP`\|`NO_RUN_PREFILTER`); `offset-set-bounded`, `offset-set` (`NO_OFFSET_SKIP`); `memchr-bounded`, `memchr`; `byte-class-bounded`, `byte-class`; `none` | `us->kind` (`DFA_PF_MEMCHR` iff `cand.use_memchr`, decided in `unanch_start` `:4150`); `us->views` (the D11 bound); `ofsk.nsel`; the run pin (`pf_run_applies_common` `:5767`) | `pf_emit_memchr` `:5627`: rest-of-subject libc `memchr`, no verify. `pf_emit_bcls` `:5676`: `while (!can_begin_match[s[pos]]) pos++`. The offset/run rows call the file-scope `<p>_ofsskip` (`pf_block_ofs` `:6038` → `ofs_test_emit_fn` `:6143`), and their scan ARM is an `if`: the leapfrog over two `memchr` streams (`ofs_test_emit_pair` `:6102`) where the scan position is a two-member cube, else one `memchr` at k*. Then the `ofsk_emit_verify` chain (`:5990`), whose run term is the run compare (T7). The `-bounded` twins clamp to n−1 |
| T2 | `req_admits[]` (k82fix) | `lane/k82fix:emit_dfa.c:6638`; walk `req_admit` `:6660` | whether the whole-window PRE-CHECK is emitted, and in which shape | `none`; `one-attempt` (G2); `dominated` (G1); `set-leads` (`NO_REQ_SET_LEAD`); `emitted` | the `req_byte`/`req_run`/`req_set` facts; `req_route_one_attempt`; `dfa_cand_scan` (`:6392`) + `req_byte_dominated_by` (G1's density clause reads `cs->memchr_form`); `pcrec_find_pick` | ADMISSION only. The admitted shape is emitted by `pcrec_emit_req_byte_check` (`:1247`): one `memchr` for a byte; the `<p>_reqrun[_whole]` blocks (the same `ofs_test_emit_fn` as T1) for a run; `set-leads` adds the set pick's `memchr` in front; `emit_req_set_rest` (`:1170`) adds one `memchr` per remaining necessary-set member on the no-DFA-scan route |
| T3 | `dfa_edges[]`, AXIS H | `emit_dfa.c:7237`; walk `dfa_edge_of` `:7333` | per STATE: does it emit an [OPT-5] scan edge at all | `scan-edge` (`NO_SCAN_EDGE`); `table-walk` | the pass's own annotation `scan_span` (`edge_applies` `:7232`) | `emit_scan_edge` `:7407`: a peeled guard, then `while (more && TEST) advance;` (unbounded) or the counted `scan_run_length < span` loop. ONE loop form. Its own comment names the SIMD slot as a LOOP form "selected ahead of the scalar loop", unbuilt |
| T4 | `ROWS`, the class-form table | `src/gen/clskit.c:562`; walk `pcrec_clskit_select` `:693` | how ONE byte's membership is spelled, per set, per `--tune` position, per SITE (`CLSS_VM`, `CLSS_SCAN`) | `byte-range`; `byte-fold` (`CLSD_BYTE_FOLD`); `byte-fold-default` (VM only, held D138 Q1); `byte-kit` (`CLSD_BYTE_KIT`, size positions, only if smaller, D139 item 1); `byte-table`; `size-page3`; `speed-page2`; `speed-bitmap1`; `mid-page3`; `kit` | the set alone (one interval, the ASCII fold pair, byte-ness), model bytes, the call count, the `--tune` position, the site | inline `==c` / `(unsigned)(c-lo)<=span` / `(c\|0x20)==x` (`pcrec_clskit_emit_inline`), a kit matcher call, or a table read (`pcrec_clskit_read`). Readers: `vm_cls_test` (`emit_vm.c:1656`) and the scan edge's `scan_test` (`emit_dfa.c:7386`, axis I, D139 item 2) |
| T5 | `TAB_ROWS` | `clskit.c:754`; walk `pcrec_clskit_select_tables` `:777` | the TABLE representation for the classes T4 sent to a table, per artifact | `atom` (VM, `CLSTD_ATOM`); `scan-table` (scan site); `site` | the count of table-read classes, the atom partition's fit | the shared 256-byte byte→atom table plus a 64-bit mask per class; one 256-byte table per edge; or a 32-byte bitmap per class |
| T6 | `pcrec_runcmp_rows` | `src/gen/runcmp.c:64`; walk `rc_row_of` `:195` | the L2 RUN COMPARE (a verify), both engines | `words` (`NO_RUN_OVERLAP`, masked, L ≥ 2); `overlap` (`NO_RUN_OVERLAP`, exact, L ∈ {3, 5-7, 9-15}); `bytes` (masked fallback); `memcmp` (exact fallback) | the run alone (`rc_holds(pred, r)`: masked or not, its length) | memcpy-loaded word compares (`<p>_w<W>(base+o) & w("K")) == w("T")`, joined by `&&`); per-byte `(b & K) == T`; or `!memcmp(base, "t", L)`, which gcc fuses (one load at L ∈ {1,2,4,8}, a vector compare at L ≥ 16) |
| T7 | `pcrec_find_pick` (a primitive, not a table) | `src/core/findings.c:426` | the OPERAND: which candidate byte or cube is rarest | — (argmin over `cube_mass`; NONE answers by cardinality, k82fix (C)) | the byte-rate (static prior or a `--findings` bundle, D83/D123) | nothing; its readers (`pcrec_find_set_pick`, the run's scan member, `req_set_leads_applies`) feed T1/T2's operands |
| T8 | `dfa_reprs`, `dfa_views`, `dfa_seeds`, `dfa_accs`, `dfa_matches`, `dfa_search_starts` | `emit_dfa.c:5270`, `:5388`, `:5462`, `:5552`, `:6857`, `:7072` | the state token, the position views, the entry seed, the accept probe, the match entry, the search start | — | — | the DFA's representation. **Excluded from SIMD:** none of them scans. Membership IS the transition table (compare_stack.md §5's record) |
| T9 | `vm_ctx_forms[]` | `emit_vm.c:8229` | the VM's `\b`/lookaround context test | six truth-function rows | the node's function | a guarded one-position test through T4. **Excluded:** one or two positions, no scan |

### 1.3 The scan sites that have NO table (each a single emitted form today)

| # | site | file:line | what it is in requirements.md's menu | current form |
|---|---|---|---|---|
| N1 | the stay skip, forward and reverse (axis F's direction methods) | `emit_dfa.c:6627` `dir_fwd_skip`, `:6655` `dir_rev_skip` | F5 / F6 `skip_in_set`, IN-LOOP (D91 budget 2) | `while (pos < n && <p>_<m>_stay<K>[s[pos]]) pos++`. The stay set is a raw 256-byte table and is NOT asked through T4, unlike the scan edge since D139 item 2 |
| N2 | the VM span scan (`vm_cursor_rep`'s two arms) | `emit_vm.c:4613` `vm_emit_span_scan` | F5 at stride 1 (a class run); a stride-k sequence otherwise | `while (cur + stride <= lim && it_ < rmax && TEST) cur += stride`, with TEST being T4's spelling per position |
| N3 | `emit_attempt`'s `(?m)^` skip | `emit_dfa.c:8649` | F1, rest of subject | one libc `memchr('\n')`, candidate = hit + 1. Keeps its own form (compare_stack.md §5), provisionally |
| N4 | `emit_req_set_rest` | `emit_dfa.c:1170` | k × F1 presence tests (no current menu item: "all of S present") | a `for` over a `static const` member list, one `memchr` each |
| N5 | the ofsskip scan ARM | `emit_dfa.c:6143` `ofs_test_emit_fn` | F1 at offset k* plus a verify (F9's shape); F2/F3 for the cube (the K82 pair arm) | an `if`: pair arm (two `memchr` streams), else one `memchr` |
| N6 | `vm_rev_emit`'s backward walk | `emit_vm.c` (compare_stack.md §2.3) | F6 reverse, per byte | a per-byte L1 test with `cur--`. Keeps its own form (compare_stack.md §5) |
| N7 | `$_span_match[_caseless]` | `src/enc/enc_byte.c:153/184` | F8 `mismatch`, a run-time operand | a byte loop returning a prefix count. Gated on a cell (compare_stack.md S6) |

---

## 2. Slot-in: where SIMD joins, as rows

### 2.1 The rule this section answers to

A vector form is admissible only as a ROW: `{name, deny, applies,
emitter}`, walked by the table's existing first-match walk, with its name
being what the stamp prints and what `--list-axes` lists. The total
fallback stays last. An ISA fact is a PREDICATE INPUT, never a branch in
an emitter outside the row. That is D122 addendum 2 item 4 ("a SIMD form
later drops in as ONE ROW whose predicate includes the arch capability,
and its deny flag gives it an answer-identity axis for free"), D82, and
memory `pcrec-general-mechanisms-not-special-cases`.

**What "the arch capability" can mean at pcrec time** (finding 2g). pcrec
emits architecture-neutral C, and `Ctx` holds no target. So an ISA
predicate has exactly two readable values:

- `BASE`: a vector form of this composition exists at the baseline of
  EVERY architecture the kit supports (x86-64 SSE2, AArch64 ASIMD). The
  emitted text is then a preprocessor ladder whose `#else` arm is the
  next row's own scalar text (§2.5).
- `DECLARED(L)`: the caller passed `--isa=L` (isa_selection.md §1.2
  route A, designed, not built). The row may then emit only level L's
  spelling, with no ladder.

Route M (a consumer `-march` that raises the predefined macros) needs no
pcrec predicate. The kit's ladder sees the macros at gcc time.

### 2.2 The new nested table: `SCAN_ROWS`, the scan-form table (P5's form slot)

**The question it answers.** "Spell the search for the first position `i`
in `[pos, lim)` whose byte is in S (or whose bytes satisfy a pinned
filter), with this handoff at a hit." It does not answer what S is, where
the search runs, or whether it runs at all. Those stay T1/T2/T3's.

**Its sites** (bits, D139's shape): `PF` (the T1 candidate-start skip),
`PRE` (the T2 pre-check's blocks), `OFS` (the ofsskip block's scan arm,
shared by T1's offset/run rows and T2's run blocks, which already share
`ofs_test_emit_fn`), `STAY` (N1), `EDGE` (T3's loop), `VMSPAN` (N2 at
stride 1), and `SETREST` (N4).

**Its input**, a `ScanSpec` (designed):

- **S, as an operand:** one byte; a two-member cube `(K, T)`; a T4
  `ClsChoice` (the set plus its scalar spelling); or a pinned pair (the
  scan byte at k* plus one more filter term at another offset). The
  pinned pair is Study A's and F9's packed pair, with the second position
  chosen by `pcrec_find_pick`.
- polarity: find-in (prefilters) or find-not-in (skips).
- direction.
- **the bound kind:** rest of subject; view-bounded `n − 1` (the D11
  twins); or counted, with `maxw` or the edge's `span`.
- **the site budget:** D91 1, the prefilter, or D91 2, in-loop.
- **the density prior:** `pcrec_find_set_ppm` / `pcrec_dfa_cand_ppm`.
- **the handoff:**
  - RETURN the index (PF, PRE);
  - VERIFY-THEN-CONTINUE, carrying the `ofsk_emit_verify` text with
    `cand` bound (OFS);
  - ADVANCE the cursor variable in place (STAY, EDGE, VMSPAN);
  - ALL-PRESENT (SETREST).
- the prefix placeholder (D143) and the comment tier.

**Its rows (first match).** The order is the design's. Placements marked
OWED are measured placements, not guesses (§6).

| # | row | sites | predicate | deny | emitter |
|---|---|---|---|---|---|
| 1 | `loopfree` | all | the bound is counted and `≤ V`, the kit's short-path width (from `maxw`, a `{0,n}` edge span, or a `W` from [FINDINGS.B4]) AND the kit composes S (§4) | `-fno-vec-scan` | kit K2: the loop-free overlapping-load short path, no loop and no call (RB-4) |
| 2 | `vec-verify` | OFS | the handoff is VERIFY-THEN-CONTINUE AND the kit composes S at `BASE` or `DECLARED` | `-fno-vec-scan` | kit K2 with the on-hit hook: iterate the hit mask's set bits, emit pcrec's verify text for each, and continue the vector loop on failure. That removes k82cost's per-hit re-entry `s`, the "find, verify, restart" cost |
| 3 | `vec` | PF, PRE, SETREST; STAY, EDGE, VMSPAN at `BASE` only unless `DECLARED` (isa_selection.md §2 row 4) | the kit composes S | `-fno-vec-scan` (in-loop sites: `-fno-vec-skip`) | kit K2: the composed scan (§4), with the `#else` arm being the first scalar row below that applies |
| 4 | `libc-memchr` | PF, PRE, OFS, SETREST | S is one byte AND the bound is rest-of-subject. OWED placement against row 3: requirements.md §2.3 row 5 keeps libc on a single rest-of-subject stream unless the Linux `n*` (U-1) says inline matches its long-span `beta` | none (today's default) | today's `memchr(...)` text, byte for byte (`pf_emit_memchr`, the ofsskip memchr arm, the pre-check, N4) |
| 5 | `leapfrog` | OFS, PRE | S is a two-member cube, single-byte scans | none | today's `ofs_test_emit_pair` text |
| 6 | `swar` | all | S is one byte, a cube, or ≤ 3 bytes, with no vector row taken. Portable `uint64_t` SWAR (has-zero-byte), admitted NOW by D122 addendum 3 as an ordinary row (no ISA predicate) | `-fno-swar-scan` | pcrec- or kit-emitted SWAR, P8's subject-end guard (word loads only where `pos + 8 ≤ n`, memcpy loads, a short epilogue) |
| 7 | `table-walk` | PF, STAY, EDGE, VMSPAN | always (the total fallback) | none | today's loop: `can_begin_match` / `stay<K>` / T4's scan test / T4's VM test, byte for byte |

Two notes on the rows:

- **Rows 4, 5 and 7 are today's text.** Promoting the seven sites to ask
  `SCAN_ROWS` moves no byte while rows 1-3 and 6 are denied or absent.
  That is the implement-then-replace step each first non-scalar row
  carries (§6 R4c).
- **Row 6 is the one non-SIMD row.** It is buildable before the SIMD hold
  lifts (D122 addendum 3: "SWAR is fine"). It is also the first honest
  customer of the table, so the table is not built ahead of need (D77). A
  SWAR row needs a measured cell, like any optimization (D119).

### 2.3 Per table: what joins, where, and what its emitter needs

| table | the SIMD (or SWAR) rows that join | position | predicate | deny | what the row's emitter needs | slots cleanly? |
|---|---|---|---|---|---|---|
| T1 `dfa_pfs[]` | **none of its own.** Its rows keep choosing WHAT and WHERE (memchr = one byte, byte-class = the set, offset/run = k-set or pin, and the `-bounded` twins). Each row's emitter asks `SCAN_ROWS` at site `PF` (or `OFS` through the block) for HOW | — | — | — | each emitter builds a `ScanSpec` from what it already holds: `f->cand` (byte or set), `us->views` → the bound kind, `f->ofs` → `OFS` with the verify hook | **yes, once (e) is fixed.** `reseeds` is unchanged: a vector skip over a parked-state set leaves the state parked, the same argument as `byte-class` |
| T2 `req_admits[]` | none (admission is a placement fact; D122 item 2 and P7 keep it the one admission derivation) | — | — | — | — | **yes, with one change:** G1's density clause reads `cs->memchr_form`, which `dfa_cand_scan` sets by `strcmp(pf->c.name, "memchr")` (`:6417`). It must read a property of the SCAN FORM (§2.4 e). The premise "a one-byte scan's per-hit cost" changes under `vec-verify` |
| T3 `dfa_edges[]` | none. Axis H stays "edge or not". The edge's LOOP asks `SCAN_ROWS` at site `EDGE` (the slot its own comment names) | — | — | — | the edge's class set from `scan_choice` (`:7287`), the span (counted or not), the direction's cursor and bound (`f->dir->posv`, `scan_more`), the accept recording, the `ADVANCE` handoff | **no, as built (c)**: the loop text is inline in `emit_scan_edge`. Promote the loop to the table first |
| T4 `ROWS` | **none.** T4 is ONE-POSITION membership and stays scalar. The VECTOR classifier is a different question (16-64 lanes at once) asked of the same set. It belongs to the kit's composition table (§4.3), which T4's set feeds | — | — | — | — | **yes**, as an input. Its `ClsChoice` is the scalar `#else` spelling of a vector row, so one set has one scalar spelling |
| T5 `TAB_ROWS` | none. A vector classifier's constants (nibble tables, range immediates) are the kit's own literals | — | — | — | — | **n/a** |
| T6 `pcrec_runcmp_rows` | **`vec-masked`**: a masked run of L ∈ [16, 2V], one or two overlapping vector loads, `(v & K) == T` as a lane mask, all-ones test | before `words` | masked AND L ≥ 16 AND the kit composes a vector compare at `BASE`/`DECLARED` | `-fno-vec-run` | kit K1's load/and/cmpeq/all-lanes primitives. The caller's P8 guard for L bytes is already emitted | **yes, with a signature change:** `rc_holds(pred, r)` sees only the run. An ISA predicate needs `cx` (`rc_holds(cx, pred, r)`). Exact runs get NO vector row: gcc already lowers constant `memcmp` at L ≥ 16 to a vector compare (D122 addendum: pay for what you use; this record is the reason) |
| T7 `pcrec_find_pick` | none (a primitive). The packed-pair operand needs a SECOND pick (the rarest other position, with a distance rule): a new reader, `pcrec_find_pick2`, of the same MASS/PICK kinds | — | — | — | — | **yes** (a reader, not a mechanism; D126 Q4's NONE rule holds inside the primitive) |
| T8, T9 | excluded (§1.2) | — | — | — | — | — |
| N1-N4 | rows of `SCAN_ROWS` at sites `STAY`, `VMSPAN`, `PF`, `SETREST` | — | — | — | as T3's | **no, as built (b), (d), (f)**. N3 stays `libc-memchr` (row 4) with no change |
| N5 | `SCAN_ROWS` site `OFS`: rows 2 (`vec-verify`, which subsumes the K82 pair arm as one fused cube pass, F3), 3, 4, 5, 6 | — | — | — | the verify hook, `maxk`, the guard | **no, as built (a)** |
| N6, N7 | none planned. N6 keeps its own form (compare_stack.md §5). N7's F8 is a run-time operand row of its own when S6's cell exists | — | — | — | — | — |

### 2.4 Where SIMD does NOT slot cleanly, and the fix for each

| # | site | why not | the fix, implement-then-replace, when its first non-scalar row lands |
|---|---|---|---|
| (a) | `ofs_test_emit_fn`'s scan arm (`emit_dfa.c:6143-6185`) | a hard-coded `if (masked scan position) pair-arm else memchr-arm`. The comment explains the ORDER is load-bearing (r2 R2-S2), which is exactly what a row table encodes | the arm becomes `SCAN_ROWS` at site `OFS`. Rows 5 (`leapfrog`) and 4 (`libc-memchr`) are today's two arms, in today's order |
| (b) | the stay skip (`dir_fwd_skip`/`dir_rev_skip`) | no form selection, and the stay set is a raw `stay<K>` table, never asked through T4. That is the same shape D139 item 2 removed from the scan edge ("why can't it use the same structure the table recommends?") | first ask T4 at a scan-type site for the stay set (a D139-shaped cleanup, byte-identical where T4 answers `byte-table`), then ask `SCAN_ROWS` at `STAY`. An unbounded scan edge (`span < 0`) and a stay skip are the SAME loop, "advance while the byte keeps this state", so one site bit may serve both |
| (c) | the scan edge's loop (`emit_scan_edge`) | axis I selects the TEST. The loop is inline text | the loop becomes `SCAN_ROWS` at `EDGE`. The peeled first-iteration guard (the measured t-digits fix) stays the edge's own, around the table's loop |
| (d) | `vm_emit_span_scan` | one text, at any stride | stride 1 asks `SCAN_ROWS` at `VMSPAN`. A stride > 1 keeps its loop (a vector form of a k-periodic sequence is a different composition, unneeded until measured) |
| (e) | `dfa_cand_scan` (`:6417`) and `pcrec_dfa_cand_ppm` (`:6450`) classify T1's selection by `strcmp` on row NAMES | a row added under any other name changes G1's verdict and the re-seed price silently. The same file already holds the better shape: `DfaPf.reseeds` and `run_term` are FIELDS "so a seventh form cannot be added without answering it" | add a `DfaPf` field naming the scan's operand class (`SCAN_BYTE` / `SCAN_SET` / `SCAN_OFS`), and have both readers read it. G1's `memchr_form` premise ("one byte, per-hit restart") becomes a property of the chosen `SCAN_ROWS` row. This fix is owed with the first new T1-adjacent row whatever its kind, SIMD or not |
| (f) | `emit_req_set_rest` (N4) | one form (D82 bound 3: one form gets no table) | a fused ALL-PRESENT kernel (one pass, an OR-accumulated "found" mask per needle, early exit when all are found) is the second form that would earn the site a row. Site `SETREST` |
| (g) | every vector row, structurally | pcrec cannot know the architecture | §2.1 `BASE`/`DECLARED` plus §2.5's ladder. **Not a defect:** it is why the boundary is where §3 puts it |

### 2.5 The scalar fallback inside a ladder is the NEXT ROW

Under `BASE`, a vector row's emitted text is:

```c
#if <PREFIX>_MF_VEC_SSE2 || <PREFIX>_MF_VEC_NEON   /* the kit's capability macros */
    <kit K2 composition for S, at V = 16>
#else
    <the text of the first scalar row of SCAN_ROWS below this one that applies>
#endif
```

The `#else` is NOT the kit's own scalar loop. If it were, an x86 build with
no `__SSE2__` (impossible on x86-64, but the shape holds for an unknown
architecture) would run a second scalar spelling of the same search, which
is D122's one forbidden failure. The kit's own scalar or SWAR forms serve
the kit's stand-alone users and its reference functions. Inside pcrec, the
fallback is pcrec's next row. This requires K2's API to take the fallback
TEXT as a hook (§3.3).

### 2.6 Why this is rows, not a parallel mechanism

- **One walk, one idiom:** `SCAN_ROWS` is a `DfaCand` list (or clskit's
  tag-and-switch shape, whichever its inputs fit) walked first-match, total
  fallback last, deny bits in `pcrec_options.flags`, names on `--list-axes`
  ([LIST-TABLES]).
- **One table per question:** WHAT and WHERE (T1/T2/T3), HOW to scan
  (`SCAN_ROWS`), one-position spelling (T4), table storage (T5), verify
  (T6), the vector classifier (the kit's §4.3). No two answer the same
  question. A question asked by two tables would be the parallel mechanism.
- **Answer identity per deny, per architecture:** every vector row is
  speed-only. `make test-axes` with `-fno-vec-scan` and friends must be
  answer-identical on each architecture: the Mac (NEON), the Linux box
  (SSE2; AVX2 under route M), and x86 correctness under Rosetta 2 on the
  Mac (survey.md §1.2 ran SSE4.2/AVX2 there). Arch-specific testing is
  contained by the rows, which is D122 addendum 2 item 4's stated reason.
- **The stamp is the chosen row's name** (D82 rule 2, D46). A new stamp,
  `<PREFIX>_SCAN_FORM` per site class (designed), carries HOW, so the
  existing closed `<PREFIX>_DFA_PREFILTER` value set (WHAT; pcrec-bench's
  adapter enumerates it) does not split. That is the k82fix precedent of
  keeping `<PREFIX>_REQ_WHY`'s four tokens.
