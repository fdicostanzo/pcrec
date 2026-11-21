# Emitter-to-driver flow-back: fields, size gates, ladder (read-only survey, 2026-11-17)

All paths under /home/pcrec/projects/pcrec. Line numbers are of the current tree. The roadmap's own
numbers are stale: roadmap.md:529 says `Job` ends `:3669` and `req_handoff_vm` is `:3460`; today `Job` ends
src/core/internal.h:3818 and `req_handoff_vm` is internal.h:3569.

## 0. A caveat on "14"

docs/design/stream/roadmap.md:529 and approach.md:204,380 say "14 emitter-written Job fields (r3-B7, verified)".
The list of 14 is NOT FOUND in either file (r3-B7 appears only as a finding id, roadmap.md:524,545; the review
file itself was not located by grep of docs/design/stream and src/core). So the table below is MY enumeration of
every `Job` field (internal.h:3538-3818) that an emitter (src/gen/*) writes. It has 17 rows if each name is its
own row (14 if region_placed/region_open, entry_exported/entry_static/entry_body/entry_comb and tbl_n/tbl_out
are each counted as one family: 1 req_handoff_vm, 2 vm_islands, 3 enc_mask, 4 code_block_lines,
5 vm_emitted_nodes, 6 vm_rungs, 7 vm_frame_capacity, 8 vm_subject_ceiling, 9 vm_frameless, 10 region_*,
11 string_h, 12 entry_* family, 13 tbl_n/tbl_out, 14 anchored_ok is NOT emitter-written, see below). INFERRED
that this matches the review's 14; it cannot be confirmed. Fields the DRIVER writes (fit.*, revend_*, anchored_ok
at compile.c:425, lm_built, machines_final) are out of scope here.

## 1. The fields

Legend: kind T = fact about emitted text; P = fact about plan/regex computable before emitting; H = target
machine/C compiler; O = other. "DECIDES" = the driver acts on it; "REPORTS" = stamp/listing only.
"read by driver" is the question; emitter-internal readers are listed but do not flow back.

| # | field (decl) | written by | read by | meaning | kind | use |
|---|---|---|---|---|---|---|
| 1 | req_handoff_vm (internal.h:3569) | gen/emit_dfa.c:1098 `emit_req_handoff_rest`; gen/emit_dfa.c:7896 `pf_emit_handoff` | core/compile.c:1229 `fit_handoff_applies` (the `drop-handoff` rung's applies) | the attempt printed a VM-side required-run handoff row | T (printed a row). Its cause is a plan choice (the candidate route, `cand_finish_of(cx) == CAND_ROUTE_VM`, emit_dfa.c:7896) INFERRED P-derivable | DECIDES (re-plan: gates rung 11) |
| 2 | vm_islands (3573) | gen/emit_vm.c:11843 `vm_emit_stamps` (`if (v->nislands > 0)`) | core/compile.c:1145 `fit_islands_applies` (`drop-islands`) | the attempt printed an alternation island | T; cause is the island build decision `vm_isl_build` (plan-level, before emission, emit_vm.c:4551-4564) | DECIDES |
| 3 | vm_emitted_nodes (3685) | gen/emit_vm.c:14425 `vm_emit_epilogue` (`= v->nlabel`) | core/compile.c:3446,3498,3538,3545 (size-term ladder record, `size_term_choose`) | count of VM nodes (labels) emitted; same number as `--emit-ir` "program N labels" | T (a count of printed things) | DECIDES (picks unroll K; also a consistency compare at :3538) |
| 4 | vm_rungs (3693) | emit_vm.c:14426 | compile.c:3486 (`& 0x10u`, counter-rung gate for running the size-term ladder) | bitmask of VM rungs the artifact took | P: rungs are chosen in the pre-pass `vm_count_slots` (emit_vm.c:~10860-10880 region) INFERRED | DECIDES (whether the ladder runs) |
| 5 | vm_frame_capacity (3715) | emit_vm.c:14432 | compile.c:3447,3499 -> `size_term_choose` | frame capacity the artifact declares (= `rx_info.frame_capacity`) | P (a declared capacity computed from plan and K) | DECIDES (a K that would lower it is not a candidate) |
| 6 | vm_subject_ceiling (3716) | emit_vm.c:14433 | compile.c:3448,3500 -> `size_term_choose` | subject ceiling the artifact declares | P, as 5 | DECIDES |
| 7 | region_placed, region_open (3747) | gen/memfn_targets.c:288 `pcrec_emit_target_open`; :300 close | same file :230,:272,:298; core/compile.c:3407 (end-of-attempt balance check) | the CPU-target `#pragma`-style region was written / is open | T (bracket balance of printed text) | driver read is an invariant check that REFUSES (`pcrec_ctx_fail` "internal error"); not a re-plan |
| 8 | code_block_lines (3636) | gen/emit_code.c:501 `pcrec_emit_code_block` | dump/facts_dump.c:137 | lines in the inline-code block | T | REPORTS (facts dump) |
| 9 | enc_mask (3647) | emit_dfa.c:17091-17120 `pcrec_emit_dfa`; emit_vm.c:7651,7660,9120,9181,9388,10968 (on the `Vm` copy) | emit_dfa.c:3543-3649 (prologue writers) only | which encoding helper entries the text needs, "DISCOVERED BY EMITTING" (comment internal.h:3638) | T | emitter-internal; the driver does not read it |
| 10 | vm_frameless (3725) | emit_vm.c:11208 `vm_plan_entry` (`= !v->has_push`) | emit_dfa.c:8683 `req_route_one_attempt` | VM program never pushes a frame | P (plan fact, published for the prologue's reader) | emitter-internal |
| 11 | string_h (3788) | emit_dfa.c:16668 `pcrec_emit_prologue` | gen/memfn_sites.c:1012 `pcrec_memfn_art_end` | the prologue declared `<string.h>` | T | emitter-internal; invariant refusal ("internal error") |
| 12 | entry_shaped / entry_exported / entry_static / entry_body / entry_comb (3793-3794, ~3800) | gen/entries.c:414-421 `pcrec_entry_shape` | gen/entries.c, gen/part_layout.c:353,433,442, gen/emit_iter.c:59 | the linkage and combinator shape of each entry | P (from the entry-row tables) | emitter-internal; the driver does not read them |
| 13 | tbl_n, tbl_out (3817) | gen/tblpool.c | gen/tblpool.c:79-91 | pooled file-scope tables asked / emitted | T | emitter-internal; `pcrec_tbl_done` refuses an unemitted table |

Not emitter-written but in the same struct and the same flow: `anchored_ok` (3558) is written by the DRIVER
(compile.c:425) and read by driver and emitters; the emitters read driver-written `fit.*`, `revend_*`.
Two further flow-backs are NOT `Job` fields but `Ctx` flags set at the failure site and read by the ladder:
`cx->dfa_overflowed` (compile.c:1526, set by the DFA build) and `cx->size_cap_refused` (compile.c:3565, set by the
driver itself right after it MEASURES the emitted text). Also not fields: the measured `emit_code` / `emit_tot`
(compile.c:3426-3428, `pcrec_sb_size_decide` on `csb`+`hsb`).

Reading of the roadmap sentence: the ladder reads ONE of them by name (`req_handoff_vm`, compile.c:1229), but
the rung applicability tests also read `vm_islands` (compile.c:1145), and the size-term ladder reads four more
(vm_emitted_nodes, vm_rungs, vm_frame_capacity, vm_subject_ceiling; compile.c:3446-3500). So "reads one" is
true of `fit_rungs[]` applicability tests only if vm_islands is counted as added since (the roadmap predates
the K139 `drop-islands` row, compile.c:1487; INFERRED).

## 2. The size gates

### 2a. Limits measured on EMITTED CODE / TEXT length (src/core/limits.def)

| limit (limits.def line) | default | where checked | on trip |
|---|---|---|---|
| PCREC_MAX_VM_EMIT_CODE_BYTES (188) | 500000 | core/compile.c:3558-3574 (`emit_code > cap_code`, after the whole text is built and stamped, compile.c:3426-3441) | sets `size_cap_refused` (3565) then `pcrec_ctx_fail` "pattern too large: %zu bytes of emitted code" (3568); the failure longjmps to the one recovery point, where `fit_labels` (1522-1528) turns it into label FIT_L_SIZE and the SIZE-CAP LADDER (rows 5-14 of `fit_rungs[]`, compile.c:1370-1493) runs; a hard refusal only at the last row `refuse` (compile.c:1493). Comment compile.c:3547-3553: "THE CAPS REFUSE HERE, and only here". |
| PCREC_MAX_EMIT_BYTES (195) | 1000000 | same, compile.c:3575 (`emit_tot > cap_tot`) | the same route and message ("bytes of emitted C source") |
| PCREC_DEFAULT_WARN_EMIT_BYTES (194) | 250000 | compile.c:3625 | advisory warning only, never refuses (limits.def:194) |
| PCREC_SIZE_TERM_THRESHOLD (196) | 120000 | compile.c:2349 (threshold), run decision near :3470-3500 | gates whether the unroll-K size-term ladder runs at all; on CODE bytes ("the emitted CODE size did not exceed PCREC_SIZE_TERM_THRESHOLD", compile.c:1673); not a refusal |
| PCREC_SIZE_TERM_BAR (197) | 75 percent | `size_term_choose`, compile.c:~2654 | selection knee: K is taken only if it saves 25 percent of bytes |
| VM_INLINE_CHAIN_MAX_BYTES (388) | 4096 | gen/emit_vm.c:11309-11315 (`en->program_bytes <= term`) | selection: VM entry shape INLINE/FORWARD below it, SHARED/PLAIN above; no refusal. `program_bytes` = `pcrec_vm_stmt_program_bytes` = `pcrec_sb_len_decide` of the body text (gen/vm_stmt.c:1070-1073) |
| VM_ISL_BYTES_PER_NODE (271), VM_ISL_BYTES_PER_CHAIN_NODE (272), VM_ISL_SIZE_FACTOR (273) | 180, 98, 2 | gen/emit_vm.c:4551-4564 (`vm_isl_*`), :4596-4608 and :10869-10872 (the 0.9 x PCREC_MAX_VM_EMIT_CODE_BYTES guard) | selection: an island that would estimate over the chain by the factor, or past 0.9 of the code cap while the chain fits, DECLINES (no refusal). These are PLAN-unit estimates OF emitted bytes (see 2c) |
| VM_ISL_MAX_BYTES (254) | 262144 | vm_isl enumeration | "total literal bytes across every enumerated word": measured on PATTERN literal bytes (plan unit), declines the island |
| PCREC_STARTPOS_GUARD_TEXT_MAX (396) | 1024 bytes | not examined | an emitted guard text length cap; not found where checked (not read) |

Per docs/spec/limits.md section 8 (its section 8; 8.4 "The size-cap ladder and
`--size-cap=refuse`") and the `--max-emit-code-bytes` / `--max-emit-bytes` per-compile raise-only flags
(compile.c:2542-2544, 3436-3441).

### 2b. Limits already in PLAN units (all in limits.def)

states: PCREC_MAX_NFA_STATES 161, PCREC_MAX_DFA_STATES_GOTO 162, PCREC_MAX_DFA_STATES_TABLE 163,
PCREC_ANCHORED_MAX_STATES 186, PCREC_MARK_PRIO_MAX_STATES 187, PCREC_MIN_SCAN_CHAIN 397;
entries/elements: PCREC_MAX_TABLE_ENTRIES 164, PCREC_MAX_SUBSET_ELEMS 165, PCREC_MAX_AUTO_DFA_ELEMS 166;
nodes: PCREC_MAX_VM_NODES 167, PCREC_MAX_VM_REPLICATION_PRODUCT 169, PCREC_MAX_SPLICE_NODES 184,
PCREC_MAX_SPLICE_TOTAL 185; copies: PCREC_MAX_VM_REPEAT_COPIES 168 (checked emit_vm.c:10881, "before a single
byte of the matcher is written", a hard refusal "pattern too large: a bounded repeat would replicate its body");
positions: PCREC_MAX_POSSESS_POSITIONS 171, PCREC_MAX_REQ_RUN_POS_SET 410; frames: VM_DEFAULT_RESUME_FRAMES 209,
VM_DEFAULT_TRAIL_FRAMES 210, VM_MAX_AUTO_* 211-212 (run-time capacities); steps/work: VM_DEFAULT_STEP_BUDGET 207,
VM_DEFAULT_WORK_BUDGET 208; counts/levels: PCREC_MAX_REPEAT 175, PCREC_MAX_GROUP_DEPTH 176, VM_ISL_MIN_BRANCHES
230-231, VM_ISL_MAX_WORDS 253, VM_ISL_MAX_DEPTH 255, PCREC_MAX_ALTNF_WORK 411 (units), PCREC_MAX_FIND_CPFREQ_ROWS 190.
Ops/rows: no limit named in "ops" units found; "rows" appears only as PCREC_MAX_FIND_CPFREQ_ROWS (not a code-size
gate).

### 2c. Is there a plan-level predictor of each emitted-length gate TODAY?

- PCREC_MAX_VM_EMIT_CODE_BYTES / PCREC_MAX_EMIT_BYTES (hard-ish caps): NO exact predictor. Partial, all INFERRED
  as imprecise: (i) the island estimate `(nnd + trysites) x VM_ISL_BYTES_PER_NODE` and the chain estimate
  `chain_nodes x VM_ISL_BYTES_PER_CHAIN_NODE` (emit_vm.c:4551-4559), documented as within about 10 percent on
  cross-product shapes and about 48 percent over on short-word sets (emit_vm.c comment before :4572); they cover
  alternation islands only; (ii) the VM replication pre-pass `v->maxcopies` and `nlabel`-type counts
  (emit_vm.c:10881; `vm_count_slots`/`vm_cost_rep` named at emit_vm.c:594, 1017) check replication and
  PCREC_MAX_VM_NODES before emission but are not converted to bytes; (iii) `Job.vm_emitted_nodes` is a node count
  but is published only AT THE END of emission (emit_vm.c:14425). `VmBody.nrec` (gen/vm_stmt.c:30-31, typed
  statement records) exists but is a count of records already recorded during body emission, i.e. post-body, not
  a pre-emission quantity; no code was found that reads `nrec` to predict size (grep of the field's readers not
  exhaustive).
- VM_INLINE_CHAIN_MAX_BYTES: reads `program_bytes`, the text length of the body already emitted (emit_vm.c:11315);
  no plan-level predictor, the decision is made on the emitted text.
- PCREC_SIZE_TERM_THRESHOLD: read against emitted code bytes of the default-K attempt (compile.c:3470 region);
  the counter-rung gate is the only plan-ish proxy (vm_rungs bit 0x10, compile.c:3486).
- A window position count as predictor: not found.

## 3. The ladder (src/core/compile.c `fit_rungs[]`, 1331-1493; src/opt/select_engine.c has no ladder of its own)

grep "ladder" in src/opt/select_engine.c gives only a pointer to compile.c's retry-ladder comment (:95) and the
bounded-repeat ladder (:531, :574, unrelated: VM counter unroll rungs). Rows in walk order (compile.c:1331+),
"on" = the arrival label set (FIT_L_*, compile.c:925, `fit_labels` 1522-1528):

| # | rung | trigger on arrival | applies test, and what the test reads |
|---|---|---|---|
| 0 | forcing | FIT_L_FORCING (job->pf.forcing) | fit_always. An emission-time fact (a forced ask failed) |
| 1 | nomem | FIT_L_NOMEM (cx->failed_nomem) | fit_always; propagates |
| 2 | size-term-trial | OVERFLOW/SIZE/OTHER | `fit_trial_applies`: `st_phase == ST_LADDER` (driver state); a size-term trial's failure means "this K is out" |
| 3 | sel1-collapse | FIT_L_OVERFLOW (`cx->dfa_overflowed`, set when the DFA BUILD overflows; machines are built before emission, so a plan-level build result) | `fit_sel1_collapse_applies` (compile.c:1312): auto engine, no `-fprefilter`, not `island_route`, `!dfa_disabled`, `fit_collapse_can_help` (plan) |
| 4 | sel1-drop | OVERFLOW | `fit_sel1_drop_applies`: eligible and (`!dfa_disabled` or collapse_reason == CR_SEL1); driver state only |
| 5 | drop-compound | SIZE | `s->comp_assembled` = `job->comp_shell != NULL` at the refusal (compile.c:3563); learned at emission/assembly |
| 6 | drop-end-mark | SIZE | `fit_end_mark_applies` (1117-ish): `job->revend_form == RF_TAGGED && !end_mark_dropped`; driver-written, plan-level |
| 7 | unroll-rescue | SIZE | no `applies` (NULL); acts on the size-term record (vm_emitted_nodes/code from the ladder trials) |
| 8 | prefilter-collapse | SIZE | `fit_collapse_applies` (1063): `fit.chosen != ENGM_DFA`, `fit.prefilter`, not already collapsed, `fit_collapse_can_help`; plan-level (driver `fit`) |
| 9 | drop-landmark-walk | SIZE | `fit_lmwalk_applies`: `lm_built` and `pcrec_cand_lmwalk_member`; driver machine state |
| 10 | drop-anchored | SIZE | `fit_anchored_applies`: `anchored_ok` and `pcrec_cand_drop_anchored_shrinks`; driver state |
| 11 | drop-premul | SIZE | `fit_premul_applies`: `fit.chosen == ENGM_DFA`, flag test; plan-level |
| 12 | drop-handoff | SIZE | `fit_handoff_applies`: `Job.req_handoff_vm` (EMITTER-WRITTEN) |
| 13 | drop-prefilter | SIZE | `fit_prefilter_applies`: `fit.chosen != ENGM_DFA`, `fit.prefilter`, flag; plan-level |
| 14 | drop-islands | SIZE | `fit_islands_applies`: `Job.vm_islands` (EMITTER-WRITTEN) |
| 15 | refuse | all labels | fit_always; hard error |

Also: "forced" loop and the two [SEL-1]/[OPT-4] DFA-overflow rungs (compile.c:1270-1310 comment). Every size rung
(5-14) is triggered by one fact: the measured emitted text length exceeded a cap (`cx.size_cap_refused`,
compile.c:3565). Which rung is chosen is then decided mostly by plan/driver state (rows 6, 8-11, 13), with two
rows (12, 14) deciding by an emitter-written text fact, and row 5 by whether a compound was assembled.

## 4. Closing paragraph (facts only)

Of the things that flow back from emission to the driver and decide something, I count nine: the measured emitted
text length (emit_code/emit_tot, compile.c:3426-3428), `req_handoff_vm`, `vm_islands`, `vm_emitted_nodes` and
`region_open` (an internal-error check) are kind T (5); `vm_rungs`, `vm_frame_capacity`, `vm_subject_ceiling`
and the DFA-overflow flag `cx->dfa_overflowed` are kind P (4); H: 0; O: 0. (The count excludes `Ctx.size_cap_refused`,
which the driver sets itself from the T measurement, and the emitter-internal fields enc_mask, vm_frameless,
string_h, entry_*, tbl_*, which never reach the driver; code_block_lines only reports.) Of the T items, the
plan-level predictors today are: for `vm_islands`, yes (the island build decision `vm_isl_build` and the
estimate `(nodes + try sites) x 180`, emit_vm.c:4551-4564); for `req_handoff_vm`, INFERRED yes (the candidate route,
emit_dfa.c:7896); for `vm_emitted_nodes`, only partial pre-passes (`vm_count_slots`/`vm_cost_rep`, emit_vm.c:594,
1017); for the measured emitted length, no exact predictor, only the island and chain byte estimates (alternations
only) and no use of `VmBody.nrec` found; `region_open` is an invariant, not a size. No code-length gate has been
converted to an op-count gate today: both PCREC_MAX_* emitted-length caps are checked on text after emission
(compile.c:3558, 3575); the pre-emission gates already in plan units are PCREC_MAX_VM_NODES and
PCREC_MAX_VM_REPEAT_COPIES (emit_vm.c:10881).
