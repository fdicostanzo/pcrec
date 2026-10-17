# memfn/src/ — the kit's sources

Built into `libpcrec.a` by pcrec's Makefile (`KITSRCS`, compiled with
`KITFLAGS`: no `-Ilib`/`-Isrc`, so nothing here can include pcrec). Every
file includes its headers by relative path. From R4c pcrec's emitters render
two sites through the kit (src/gen/memfn_sites.c, DELEG_SITES): the
offset-skip block and the pre-check composite, by the scalar arms below;
from M1b, a third, the VM's literal-run compare (VMRUN, runcmp.c); from
R4g (M2), a fourth, the prefilter find (PF, pffind.c).

- **kit.h** — the INTERNAL header: `kb` (growable text over the caller's
  `mf_arena`), the `mf_art` struct and its per-site records, the arm
  interface K2 selects over (an arm writes STRAIGHT TO THE SINK, in order,
  so a hook that writes and the sink's comment gate act at the point the arm
  reaches them), the sink writers (`kit_out`, `kit_flush`) and the
  offset-skip function's shared renderer (`ofs_fn_*`; since R4e'.0
  `ofs_fn_define` takes the calling site's handle), the shared walk's table
  descriptor `kit_table` and `kit_walk` (R4e'.0), and the row
  contracts' types (`gate_contract`: `uses` per site kind and phase,
  `serves` per field; `CL_*`/`FLD_*` from fields.def) and the MF_TRACE
  record calls. Never included outside this directory.
- **compose.c** — K2, the composer (R17-b′ B3a adds `kit_presence_check`, the PRESENCE-statement rules, inside `site_check`): THE KIT'S ONE SELECTION WALK,
  `kit_walk` (R4e'.0, integration.md §R4.9.2.3: per row of the asked slot,
  in table order, the deny, the gate, the row's predicate; first match; a
  slot holding no row is no selection and records nothing), which the arms
  (`select_arm`), the run compare (`rc_row_of`) and `fn_rows[]`
  (`fn_select`) all call; `mf_art`, the define/use split
  (`mf_define`/`mf_use`/`mf_emit`/`mf_call`; handles checked at use and at
  `mf_art_end`), the vocabulary rules every site must pass (`site_check`,
  `pred_kinds`: out-of-enum fields and every shape integration.md §R4.7
  rules outside the vocabulary are REFUSED loudly; since lane rankuse
  `rank_ok` refuses a position ranking that is not distinct positions of
  the RUN term `plan_hint` names, or longer than it or MF_RANK_MAX) and their table
  (`mf_vocab_has`), the FIRST-MATCH arm table (`ofsskip`, `precheck`,
  `precheck_assign`, `precheck_assign_byte` (one renderer, three rows:
  N3's split by handoff, and R-15's by what ret_pred names),
  `runcmp`, the five PF rows (`pf_memchr`, `pf_memchr_bounded`, `pf_walk`,
  `pf_walk_bounded`: R4g; `pf_memchr_back`: M4 prep), `mismatch_inplace`
  (M7 prep), then the generic row; each arm's `ct` is its contract, which
  the gate reads before the arm's predicate and, since [MEMFN-ROWCON] N3,
  ENFORCES: a failing row is declined and the walk moves on, a site no row
  serves is refused naming the fields, and `mf_use` re-checks the chosen
  arm against the use hooks and refuses a use it does not serve), the
  art's one `denies` value (a site
  whose `denies` differ is refused, Q-M1b-1), the `mf_includes` query, and
  the stamps: `mf_art_note_libc` (the libc record's writer, a sorted
  distinct name list on the art; every arm that renders a libc call notes
  it at the render, beside its `includes` bit: `memchr` in `ofs_fn_define`,
  `precheck_use` and `pf_memchr_use`, `memcmp` in `run_cmp_render`; the word-load helper's
  constant `memcpy` is the record's exclusion and is not noted) and `mf_stamps` (M1b: `RUN_WORDS`, the run
  compare's words count, through `sink->stamp_int`; R4a′: `MEMFN_FORMS
  "none"`, constant until R4f, then `MEMFN_LIBC`, the noted names
  comma-joined or `none`, through `sink->stamp`).
  Since R4e' batch 1 (R-13) the walk's DENY also reads the site's
  `--memfn=` string (`no-<row>`, through a table's `opt` accessor and
  options.c's `kit_opt_denied`), `kit_ask` asks ONE named row the same
  questions (a PREFIX row's rungs), and an OPTIONAL slot that chooses none
  traces `chosen=none`, not a refusal's `-` (`gate_tctx.optional`).
- **generic.c** — THE GENERIC SCALAR ROW (integration.md §14.6): the last
  row of every selection table, rendering every site the vocabulary
  describes as a plain byte loop (GNU C statement expressions for EXPR; a
  `static inline` definition plus calls for FUNC; STMT ASSIGN, ON_MISS,
  ON_CAND and ADVANCE). It tests every term, honours `floor`, `n`,
  `end_back` and the empty outcome on every op (VERIFY tests its range
  too; an empty range, `lo > n` included, reads nothing: §R4.7 F1), and
  uses pcrec's `member` hook for a set when one is given. No tuning constant (D149).
  **Since [MEMFN] R4h (M3, lane r4h, 2026-10-08) its `stmt_advance` is
  pcrec's in-loop skip text**: DELEG_SITES rows STAY (`dir_fwd_skip`/
  `dir_rev_skip`), EDGE (`emit_scan_edge`, both loops) and VMSPAN
  (`vm_emit_span_scan` at stride 1) render through it at zero movers (the
  frozen target, tests/memfn/pins/r4h_target/). pcrec passes every hook as
  text (`more`/`peek`/`step`/`cursor`, its own opaque `member`, and the
  caller-owned `count` with `count_by_caller` 1 on the counted edge and the
  VM's `it_`). Sabotage rows S214 (the scan edge's cap, `count_start` 1)
  and S616 (the VM span's `it_` cap, `count_start` 0) are anchored on its
  cap line, each scoped by that site fact.
- **ofsskip.c** — a SCALAR ARM, born at R4c (integration.md §15.1;
  transcribed from pcrec's `ofs_test_emit_fn` and friends): THE OFFSET-SKIP
  FUNCTION, a `static inline size_t` returning the leftmost position whose
  every term holds (one `memchr` stream on the scanned term, or the PAIR
  leapfrog on a two-member cube), its offset legend comment and its call.
  `ofsskip_arm` is the offset-skip site (FIND/FUNC/RETURN); `ofs_fn_*` also
  render the pre-check's run blocks. **Since R4e'.0 (lane r4e0,
  2026-10-09; integration.md §R4.9.2.1, the seam) the function's body is a
  first-match table, `fn_rows[]`**, with a SLOT column: BODY (`fn-pair`, the
  pair leapfrog where the scanned position is a two-member cube, above
  `fn-memchr`, the slot's floor) and PREFIX (born EMPTY: the guarded
  per-level helpers SIMD rows will add, D155; an empty slot renders zero
  bytes). `ofs_fn_define` is the seam: the BODY walk, then the PREFIX walk
  handed the BODY row, then the text. **Since R4e'.0b (lane r4e0b,
  2026-10-09; D155 item 6, integration.md §R4.9.2.5/§R4.9.2.6, pcrec abi
  68 -> 69) the text is routed**: the BODY loop under the helper
  `<fn>__body` (`fn_head`, the head every piece shares), then the PREFIX
  row's helpers, then `<fn>` itself, the SELECTOR (`fn_selector`), whose
  whole body is one call `return <fn>__body(subject, n, pos[, tables]);`.
  A PREFIX row's levels become `#if` arms above that call, which is then
  the `#else` arm's line byte for byte; the PREFIX walk is handed the
  helper's name (`fn_in.body_fn`), its last fall-through. No options.def
  row: the routing is the floor shape D155 ordered, measured once against
  its parent (its G1 census), not an arm with an OFF. Both BODY rows are today's inline `b >= 0` branch moved
  text-for-text, scalar and undeniable (no options.def row); each carries
  a contract (`fn_pair_ct`/`fn_memchr_ct`, the body's own fields: `denies`,
  `table_ref`, no `floor`). Trace table `fn`. Its `miss` (stated as `n`) and `floor`
  (none) edge is its CONTRACT's since N3: the ad hoc define and call tests
  (lane m1bfix's K96 fix) are deleted, the gate does both.
  **Since R4e' batch 1 (lane r13, R-13) the PREFIX slot holds the SIMD
  rows** (`vrun-w16`; `vrun-w32` above it): a PREFIX row carries an
  `mf_formdecl` (kit.h) and its predicate is `prefix_holds` over it (walk
  tests 3-5 of §R4.9.2.3: REACH, OVER, APPLIES, plus "the define sink offers
  the bracket ops"); its deny is its options.def name (`fn_opt`, walk test
  1). The seam re-asks the chosen row's NAMED rungs with `kit_ask`, writes
  one guarded block per rendered rung in ascending level order
  (`fn_level_block`: `#if <guard>`, the level's `#include` once per art,
  `fn_head`, the row's body, `#endif`), each bracketed by the sink's
  `simd_open`/`simd_close`, then the selector with its `#if`/`#elif`/`#else`
  chain (the chain's guarded part and its `#endif` bracketed, the `#else`
  call not), and records the FUNC's MEMFN_FORMS token on the art
  (`fn_note_form`).
- **vrun.c** — THE FIRST SIMD ROWS (R4e' batch 1, R-13; integration.md
  §R4.9.7): `vrun-w16` (and `vrun-w32`), the fused run scan R-1 timed as
  `ffl`, without its lead: a broadcast compare of the scanned cube position
  over VW candidates, the BODY's own run compare (runcmp.c) as the in-block
  verify, an overlapped final block, and an entry test falling through by
  the derived reach VW + T. Each row is an `mf_formdecl` (its options.def
  deny, level, `over` = `fn-pair`, named rungs, instruction classes, reach,
  `guarded_max`, APPLIES, render) and a contract (`vrun_*_ct`: the BODY's
  serves plus `policy` NONE|SIZE). The module comment carries the
  over-read argument and every constant's D149 label. Since lane rankuse
  (2026-10-09, D157) the candidate mask ANDs a SECOND position, KB, the
  first position of pcrec's rarity ranking (`mf_pred.rank_*`) other than KA
  (`vrun_kb`; none where the ranking states no other), denied by
  `--memfn=no-vrun-kb`; no distance rule beyond KB != KA (derived). Since
  lane r16b (R-16, D147 addendum 16, RULED) KB is read at w32 ONLY: the
  level's `npos` in vrun.c's per-level table `ops_of[]` (1 at w16, 2 at
  w32), so the w16 helper, standalone or as the w32 helper's rung, filters
  on KA alone; the deny still drops KB at every level. Since lane
  r14b (R-14, D147 addendum 15) each candidate's verify skips the
  positions the mask tested (`vrun_proven`; runcmp.c's
  `run_cmp_render_trim`), and a run the mask covers whole is returned with
  no verify; the deny `--memfn=no-vrun-trim` verifies the whole run.
  Since lane r14p (the R-14 follow-up) the MAIN path verifies a run of 3
  or 5-7 bytes by ONE padded word (runcmp.c's `run_cmp_render_pad`, its
  locals by `run_cmp_pad_decl`), its main guard holding the E = P - L bytes
  that word reads past the run (`vrun_pad`; the margin argument is the
  module comment's PADDED VERIFY); the final block keeps the trimmed
  compare; the deny `--memfn=no-vrun-pad` is the r14b text.
- **levels.def**, **levels.c** — the kit's ISA LEVELS (R4e' batch 1):
  `MF_LEVEL(token, family, guard, header, vw, test_march, forbid, stamp)`,
  the one place a level's guard string, intrinsics header, width and stamp
  token are spelled; `mf_levels()` (memfn.h, for the tests) and
  `kit_level()` over it.
- **precheck.c** — a SCALAR ARM, born at R4c (§15.3-§15.5; transcribed from
  pcrec's `emit_req_*`): THE PRE-CHECK COMPOSITE (ALL_PRESENT, ON_MISS or
  ASSIGN): the one-byte gate, each run's call (its offset-skip function and
  run-search comment at file scope), the set rest's table loop; pcrec's
  notes at pcrec's places. ONE renderer as TWO rows since N3,
  `precheck_arm` (ON_MISS) and `precheck_assign_arm` (ASSIGN), both form id
  `precheck`: an ON_MISS site never reads `miss`, an ASSIGN site tests the
  run call's result against `n`, so the rows serve different `miss` classes
  (and each predicate tests its own handoff). R-15 (lane r15b) adds the
  third row, `precheck_assign_byte_arm`: an ASSIGN site whose ret_pred is
  part 0, ONE REQUIRED byte (the `byte_landmark` predicate; the parts
  themselves are `precheck_parts`, shared), its position KEPT by one
  `memchr` behind the empty test in a statement expression (`landmark`;
  local `<prefix>_mf<handle>_q`), `n` on a miss, then pcrec's `on_miss`. It
  is the kit's first SCALAR row with a deny of its own (`opt`
  "precheck-assign-byte"); denied, the generic row renders the site. pcrec
  states the shape only from [REQ-HANDOFF-L1], so on main it renders
  nothing (reach `pending-site:REQ-HANDOFF-L1`).
- **runcmp.c** — a SCALAR ARM, born at M1b (integration.md §15.6, §R4.8;
  transcribed from pcrec's `src/gen/runcmp.c`): THE RUN COMPARE, one
  first-match row table (`words`, `overlap`, `bytes`, `memcmp`; the first
  two denied by `MF_D_RUN_OVERLAP`, read through the table's `deny`
  accessor by `kit_walk` since R4e'.0) and its writers. `run_cmp_render` is the
  RUN term of the offset-skip function's verify chain and the body of
  `runcmp_arm` (VERIFY/EXPR/BOOL behind the caller's guard: pcrec's VM
  literal runs); `run_cmp_prepare` declares a FUNC definition's word-load
  helpers ahead of it; `run_cmp_render_trim` (R-14) is the same row's text
  less positions the caller tested (vrun.c's verify) and `run_cmp_trim_none`
  says whether anything is left; `mf_flush_helpers` writes the pending ones (the art
  records the widths used/declared and the words count `mf_stamps` writes
  as `RUN_WORDS`); `mf_run_rows` is the rows' accessor (`--list-axes`).
  The overlap lengths and the width rule are DERIVED (D149).
- **pffind.c** — a SCALAR ARM, born at R4g (M2; integration.md §15.7;
  transcribed from pcrec's `pcrec_emit_find` and the memchr forms' NULL
  test and store): THE PREFILTER FIND, one FIND / STMT / ASSIGN statement
  over one SET term at offset 0 moving a scan position to the next byte a
  match can begin with. TWO renderers as FOUR rows (N3's split, by
  `end_back`): `pf_memchr_arm` / `pf_memchr_bounded_arm` (a one-byte set:
  `memchr`, then on the unbounded row pcrec's `on_miss` on a NULL hit, which
  must leave, and the store; on the bounded row one store of the hit or
  pcrec's `miss`, `n - 1`), form id `pf_memchr`; `pf_walk_arm` /
  `pf_walk_bounded_arm` (a set pcrec names by table: the in-place walk
  `while (lo < n && !T[s[lo]]) lo++;`, `result` IS `lo`, miss the range's
  end), form id `pf_walk`. The guards around the statement stay pcrec's
  (the memchr rows' empty range is EXCLUDED; the walk's NOP). Since R17-b′ B2 (KW-3) the rows ALSO serve pcrec's new shape and write those guards themselves: the memchr's `if (lo >= n) on_miss` (empty MISS), the bounded memchr's `if (lo + 1 < n) { ... }` block (empty NOP), the walk's post-test (empty MISS, a leaving on_miss), and on the two bounded rows the `moved` hook under `if (result > skip_from)` (`moved_open`/`moved_close`, one statement: `one_stmt`); a memchr row serves a one-member set whether or not a table is offered (PR-1). M4 prep (R-7)
  added a FIFTH row, `pf_memchr_back_arm` (form id `pf_memchr`, the same
  renderer): MLINE's `(?m)^` skip, its one-byte term at offset -1 (the
  candidate's predecessor), `floor` the text of `lo`, `empty` AT_N
  (Q-R7-2), `on_miss` JUMP/BRACED or LOOP_EXIT (`break;`, Q-R7-3), and the
  store adds the 1 back; its range is read-bounded (Q-R7-1). No tuning
  constant (D149).
- **mismatch.c** — F8, THE MISMATCH, born at M7 prep (R-8, MF_VOCAB 3;
  integration.md §15.8; transcribed from pcrec's encoding seam,
  `src/enc/enc_byte.c`/`enc_utf8.c`'s span-compare loops): the compare
  LOOP of the subject from `lo` against a run-time reference span, a STMT
  site inside pcrec's own residual function (RULED Q-R8-2: the signature,
  the full-match return and the meaning of a difference stay pcrec's).
  ONE renderer (`mm_render`) as TWO rows (RULED Q-R8-9): the generic row
  renders the exact and FOLD_EXPR shapes (one `if` per byte, the fold text
  pasted around each operand), `mismatch_inplace_arm` the FOLD_STMT shape
  (two byte temps, `x`/`y` unless a hook names one, the fold statements
  pasted per temp, the subject-end test and the compare as two exits).
  ON_DIFF: the loop index IS `result`, so k is written before `on_miss`
  runs. Operands are pasted raw when identifiers, parenthesized otherwise;
  `on_miss` raw when JUMP/BRACED, braced otherwise, never LOOP_EXIT (its
  own loop encloses it). No tuning constant (D149).
- **k1_ref.c** — K1's REFERENCE functions (`mf_ref_*`): one obviously-
  correct byte loop per primitive (F1 find_byte, F2 find_any2/3, F4
  find_in_set, F5 skip_in_set, F9 find_literal, F7 run_verify, F8
  mismatch since M7 prep). G2's
  oracle side; never artifact text.
- **fields.def** — THE FIELD TABLE of the row contracts ([MEMFN-ROWCON]
  N1, docs/design/memfn/row_contracts.md §2), two X-macros: `MF_CLASS(name,
  doc)` (the value classes, OTHER in every set) and `MF_FIELD(name, phase,
  absent, classify, classes, doc)` (every site/hook/run-term field a row
  reads: where the gate reads it, what an absent value is, including the
  written per-kind OBLIGATION exemptions, its classify function and its
  closed class set, with the text-shape classes IDENT / JUMP / BRACED and,
  since R4h prep, the ADVANCE hooks' CONJ (`more`), POSTFIX (`peek`) and
  EXPR_STMT (`step`); and `count_by_caller`, the caller-owned counter
  (MF_SITE_ABI 5, OBLIG); since M4 prep (MF_SITE_ABI 6) `empty`'s E_AT_N
  (Q-R7-2) and `on_miss`'s LOOP_EXIT (`break;`, Q-R7-3); since M7 prep
  (MF_SITE_ABI 7) the MISMATCH's `fold_kind` (F_NONE/F_ASCII/F_UCP, read on
  a MISMATCH site only) and `fold`'s FOLD_EXPR/FOLD_STMT (a lexical check
  that reads through quoted literals; OTHER where fold_kind is NONE), and
  the `ref`/`reflen` hooks; since M6 prep (MF_SITE_ABI 8) `stride` (ADVANCE's
  W = pred.nterm, ONE/MANY, read on an ADVANCE site only; at MANY the
  generic row USES `s` and `cursor`, a conditional `uses` entry) and the
  `cursor` hook (IDENT/OTHER);
  `miss`'s MISS_N is the `MF_MISS_N` token or the text of `n`). Since N3
  `fn_ref` is a hook ID (0 UNSTATED, so a FUNC site stating 0 is refused,
  K-1) rather than an OBLIG exemption, and `s`/`n`/`lo` are read at define
  as well as use (ruling F1).
- **gate.c** — THE ROW-CONTRACT GATE (`stmt_shape` classes `break;` as
  LOOP_EXIT since M4 prep) (its `uses` entries may be CONDITIONAL
  since R4h prep: `GATE_WHEN(cls, field)` applies an entry only where a site
  field has that class, so `count_by_caller` YES makes `count` a use; kit.h
  `gate_use`): also DEFINES the exported `MF_MISS_N`
  sentinel (`mf_miss_n`, memfn.h; `kit.h`'s `kit_miss(h)` resolves it to the
  `n` hook's text, and every reader of `miss` goes through that). fields.def's classify functions
  (`kit_is_ident`, the one lexical identifier check, lives here, beside
  the ADVANCE hooks' `conj_shape`/`postfix_shape`/`expr_stmt_shape` and the
  MISMATCH fold's `fold_shape`; `kit_stmt_shape`/`kit_fold_shape` export
  two of them to a renderer that pastes the text), the
  per-field rules (R1 used-and-unstated, R2 stated-and-not-served) as
  `gate_check`, ENFORCED since N3 at define, use and the run walk (the
  callers decline a failing row, or refuse), `gate_describe` (the text
  every gate refusal names its fields with: backquoted name, rule, class),
  and under the compile-time switch `MF_TRACE` (off by default) the
  `MFTRACE` stderr records and reach counters (format:
  `../docs/trace_format.md`; since N4 the exit lines end with
  `REACH_DROPPED n=N`, the selections a full counter registry could not
  hold (32 rows since R4e'.0, over the three tables), so an undercount is visible rather than silent; a trace build also asks a declined row's
  predicate, so `would_decline` still means "the gate moved this
  selection"). Each
  row's `uses`/`serves`, with a citation per declaration, sits at the end of
  that row's own file (ofsskip.c, precheck.c, runcmp.c, pffind.c, mismatch.c,
  generic.c).
- **fields.def / gate.c, the `policy` field (R4e' batch 1, R-13,
  §R4.9.2.3 [r9 F-3])** — the site's MF_P_* word is a stated BIT-SET field:
  each set bit is its class (PORTABLE, INLOOP, SIZE; NONE for none) and a
  row must serve every one (gate.c `class_set_of`). Every scalar contract
  serves MF_ANY; the SIMD rows serve NONE|SIZE, so -fno-memfn-simd and an
  in-loop site DECLINE them with no new verdict.
- **options.def** — the kit's option registry, an X-macro
  `MF_OPT(name, kind, budget, layer, doc)` (D147 addendum 9). Born empty;
  its first rows are R4e' batch 1's SIMD denies (`vrun-w16`, `vrun-w32`),
  then `vrun-kb` (lane rankuse: the vrun rows' second filter position, an
  option of a form rather than a row of a table), `vrun-trim` (lane
  r14b: their trimmed verify, the same kind of option) and `vrun-pad`
  (lane r14p: their padded main-path verify, likewise); the first SCALAR
  row is `precheck-assign-byte` (lane r15b, R-15: the precheck renderer's
  kept-landmark row, `MF_B_ANY`, live at both SIMD settings), denied
  through the arm's `opt` and `arm_table`'s accessor (compose.c `arm_opt`).
  Each byte-moving kit change adds its own deny row (`--memfn=no-NAME`) in
  the same commit and raises the floor in `docs/spec/registry.md` §6. See
  `../CLAUDE.md` "The kit's option namespace".
- **options.c** — `mf_options()` and `mf_opts_check()` over options.def:
  what `--list-axes` prints and what `--memfn=` accepts are one table; and
  `kit_opt_denied()` (R-13), the walk's read of a site's `no-<name>`.

- **R17-a, the zero-mover seam (lane r17a, MF_SITE_ABI 11; setfind.md rev
  2.3 §11.1)** — across these files, no byte any row writes moved:
  `compose.c` gains `window_check` (the last of `site_check`'s rules: a
  forward FIND states W0 `window_stated` 1, every other site and preds[]
  entry 0; W1/W2 only under W0; back = move_back - d_min not negative;
  `decl_point` 0/1), the storage point's protocol (`mf_locals`: refused where
  `decl_point` is 0, a second time ("placed twice"), or with an `s`/`n` text
  other than the define's, which `mf_define` copies into the site record;
  `mf_use` refuses a decl_point site before its `mf_locals`; `mf_art_end`
  refuses "never placed" and "placed, never read" before "never used") and
  `mf_defined` (the define's form id, `reads_table` = the row's column and a
  tabled SET term, `includes` = the row's column). `kit.h` gains
  `kit_window_site`/`kit_d_min`, the site record's `def_s`/`def_n`/`placed`,
  two arm columns appended last (`reads_table`: the PF walk rows, ofsskip and
  the three precheck rows; `includes`: every row that can write a libc call)
  and `MF_SERVES_WINDOW_TODAY`, which every contract (the arms' and
  `fn_rows[]`') includes: W0 YES, W1 D_MIN, W2 ZERO, W4 any. `fields.def`
  gains the class D_MIN and the fields `window_stated`, `move_back`,
  `overshoot` (read on a forward FIND under W0 only, unstated elsewhere) and
  `decl_point` (OBLIG, every site); `gate.c` their classifiers. No row keeps
  storage yet: `mf_locals` writes nothing (R17-b's stateful row is the
  first).

- **finder.c** — THE FINDER TABLE (R17-b′ B1, lane fdb1;
  `docs/design/memfn/r17b_prime.md` rev 3 §1, §2.5): `fd_rows[]`, 19 rows
  (FIND: R0, R5, R8, R3a, R3b, R4, R1, R2, D1, D1c, D1w, D2, R7, R7w; PRES:
  P0, P2, P3, P4, P9) as a `kit_table` over `kit_walk`, each with its
  `needs`, its facts, at most two comparators over measurement-set keys
  (templates `<shape>`/`<liner>`/`<kind>`/`<t>`, expanded per site), its pick
  or chain link, mandatory `basis`/`evidence`/`refuted_by`, its routing step
  and its `routed` bit (0 on every row at B1) and its contract (`FD_CT`).
  A key ABSENT from the set does not hold (never read as 0; S917). `fd_decide`
  walks the terminal rows and the residual N intervals with the PAY RULE
  (`fd_pay`, `mf_finder_pay`: T1 strict, T2/T3 ties pass; operand keys
  PROVISIONAL). `fd_shadow` is the define's shadow call: under MF_TRACE it
  prints `MFTRACE FD` records (phase `shadow`, never counted as chosen) per
  slot and layer and writes NOTHING to any sink. `mf_finder_rows` is the
  R-MS4 listing into caller-owned storage. No artifact text.
  **R17-b′ B2 (lane fdb2):** D1, D1c and D1w are ROUTED (and so locked);
  `fd_route` is the routed decision `compose.c`'s `select_arm` asks first
  (OFF variant, the site's stated kind): a routed pick renders through its
  arm (LIBC `pf_memchr[_bounded]`, LIBC_BACK `pf_memchr_back`, WALK
  `pf_walk[_bounded]`), asked on its own and REFUSED if it declines; else the
  arms walk. `mf_result.row` reports the deciding row, `MFTRACE FDROUTE` its
  trace record. R0/R7's null floor is `kit.eps.streamed.slope` (rev 3 [C4]).
  `compose.c` also carries R-MS6's arm-entry counter (`mf_reach`,
  `mf_reach_table`; a counter statement at each routed site's use, only on
  an art the host asked).
- **terms.c** — R17-b's cover search (`mf_set_terms`, lane memfn-r17),
  ported search only: the finder reads a set site's cover SHAPE
  (`r<R>e<E>c<C>`). Its renderers land at B4.
- **presence.c** — KW-8's PORTS (R17-b′ B3a, lane b3a): `mf_pres_ports`
  re-derives pcrec's five priced picks over a site's STATED presence spans
  (`pspans`, `head_max`) and the analysis object's `byte-rate` payload
  (cardinality masses under PRIOR_NONE): the set pick, the run's scan index
  and window start, set-leads, G1 (byte dominated) and the landmark
  admission. Read by pcrec's `-DPCREC_CAND_TRACE` build only (the MFPICK
  comparator in `src/gen/emit_dfa.c`); no row reads it. Plants SK-B3A-2..7.
- **formhash.c** — `mf_form_hash`/`mf_form_hash_text` (R-MS3): a form's
  normalized-text identity (comments dropped, whitespace collapsed,
  non-kept identifiers renamed, FNV-1a-64) over canonical instances
  rendered through the kit itself (`walk`, `libc`; other forms from their
  build step, -1 before). Allocates its scratch arena with `malloc`: a
  listing entry, never reached by a compile.
- **B1 across the other files** — `fields.def` gains twelve classes (the
  class space is FULL at 64: the next class needs a wider mask) and the
  fields `body` (site), `site_kind`/`layer`/`need` (the finder walk's facts,
  from `gate_in.fd`) and `start` (hook); `gate.c` their classifiers and the
  `shadow` trace phase; `compose.c` the QUERY (`mf_ask`/`ask_sel`: the walk
  `mf_define` would take, no state written; `kit_class` the class of an
  arm on a site), the set's checks (`measures_check`: `kit.` keys only,
  values in bound, no duplicate) and `consulted`, `site_check`'s `body`
  rule (PARAM refused until B8; an UNSTATED body refused since R-23, MF_SITE_ABI 14), and under MF_TRACE the define's re-ask
  (class must equal; `exists=0` must prove all bytes); `arms` gain a `libc`
  column (the class's `libc_free`).

The scalar arms are the LIVE scalar layer (D147): improvable kit code, each
change with its own `--memfn=no-NAME` row and, where it moves a byte,
pcrec's abi event and `tests/memfn/pins/arms.tsv` re-pin in the same commit.
Their provenance lines read `pcrec <commit> (relicensed 0BSD by its author, D145 addendum 1)`
(R-4 Q1, ruled by Frank 2026-10-06). Planned, not here yet: the other migrated
sites' arms (M1b on), SIMD forms (R4e′, rendered only under
`-fmemfn-simd`), K3 support. Rules: external symbols through `MF_NS`
(`pcrec_mf_*`; C15), everything else `static`; an SPDX line and a
provenance header on every file, with its row in `../PROVENANCE.md` (C16);
nothing included from pcrec's `src/`/`cli/`/`lib/`.
