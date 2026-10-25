# NOTES — history, lessons and rationale for this directory

Not auto-injected. CLAUDE.md is the orientation guide; text moved here verbatim from it (2026-10-22, size limit) lives below.

## DFA emitter organization: layers, derivation readers, hazards, wave gates

- Layer 1: the form is a VALUE. Per axis with >= 2 real forms there is a `static const` list in PREFERENCE order, first applicable wins: A `dfa_reprs`, B prefilter (`cand_rows[]` NEXT rows via `cand_select`), C `dfa_views`, D `dfa_seeds`, E `dfa_accs`, F `dfa_dir_forward`/`_reverse`, G `dfa_matches` (entry form, ENG-ABS), H/I scan edge (OPT-5), J start-pinned search. Rules: (1) every list's LAST entry always applies (`cand_always`); (2) the chosen object's `c.name` IS the stamp value (never re-derive a stamp from a predicate); (3) a `-fno-*` deny is the object's `c.deny` field, a FILTER on the list, never a clause in the emitter body; (4) only axes with >= 2 real forms get a list (facts stay booleans, D75 addendum). A new candidate needs no edit to the read-only axis accessors (`pcrec_dfa_axis_*_cands`, used by `--list-axes`).
- Layer 2: the emitted state is an OPAQUE TOKEN (typedef + accessors per machine at file scope via `repr->emit_token`); `emit_scan_loop` and `emit_machine_tables` are written once and called with forward and reverse `DfaForm`. A new table representation = one `dfa_reprs` entry + one `emit_token`. `<M>_row` MUST NOT be hoisted (a divide under pre-multiplied tables). Emitted state constants are scaled at EMIT time by `repr->cell_of`.
- ONE derivation, N readers (never restate a condition at a second site): `attempt_cand`, `unanch_start`, `dfa_engine_is_empty`, `dfa_match_of`, `req_admit`, `dfa_search_start_of`, `vm_marked`, `vm_cursor_fits`, `vm_cuts`/`vm_lifts`, `under_atomic` (threaded, never stored). The start-decision table is `cand_rows[]` ([START-TABLE], `docs/design/start_table.md`, D148): readers ask `cand_select`/`cand_read` (a slot's predicate asks another slot's row, never restates it), `CandNode.reads[]`/`kask` declare every read; `tests/codegen/run_cand_rows.sh` and `run_cand_oracle.sh` check.
- `emit_unanchored` handles EOL and non-EOL machines in ONE function (M2.12: a forked `$` copy lost the prefilter/skip loops). Under EOL every skip is bounded at n-1 and scan avoidance runs BEFORE the accept/EOL evaluation (D11). `views = eol || endv` is what every former `eol` site reads. `emit_view_select` is one branch that reproduces the old string (byte-identity discipline); `endvar == -1` = same as EOL view. The start dispatch order is load-bearing (`start == 0`, then `== startpos`, then above). `pick_skip_states` declines states whose accept varies by class. The `last_accept_position == (size_t)-1` gate is load-bearing. A reference knob for an identity gate goes at the emitter AND at the analysis action (`#ifndef` in `src/ir/dfa.c`) - a knob inside the sabotaged source cancels (wave D finding).
- Cost/soundness hazards: `vm_cost` must charge every trailed write (`A_ATOMIC` mark, `\K` one trail entry per emitted `\K`) or the artifact refuses subjects it can match; `A_CAP` publish-at-close for groups some `A_BREF` names (suppression covers both halves of the pending+pair publication); an atomic group's follow is zeroed at the BOUNDARY (`vm_atomic`) and restored after the cut; `vm_cut` is reused unchanged; the lookaround/callee follow is scoped to 0; slots 0 and 1 are never members of a call's `W`; `call_top` is on every frame and both reset functions set `call_top = CALL_TOP_NONE`; the callee region has its OWN exit; the `goto *` is written out inline per region; all call bytes gated on `Vm.has_calls`; `<prefix>_search_in` delegates to the un-suffixed entries never the reverse ([DD-14.FB]).
- Wave knobs/gates: `tests/codegen/run_endvar_identity.sh` (S69), `run_wordctx_identity.sh` (S71), `run_mlinectx_identity.sh` (S76), `run_gstart_identity.sh` (S83), `[M6.2-WORDB]`/`[M6.2-KRESET]`/`[DD-14-RECURSION]` blocks in `run_codegen_tests.sh`, `tests/assertions/run_mline_diff.sh`/`run_kreset_diff.sh`, `tests/codegen/run_dfa_stamps.sh` (stamp == loop), `run_vm_identity.sh` (DFA-only output byte-identical to pre-VM), `run_object_neutrality.sh`, `run_vm_frameless.sh`, `run_dfa_uniform_fold.sh`, `tests/utfcheck/`, `tests/kitproof/`, `tests/partlayout/`, `tests/compound/`.
- Stamp-scope rule: a stamp belongs to the mechanism it names, not the artifact kind that usually carries it (a hybrid stamps the scan it inlines through `pcrec_emit_dfa_scan_stamps`, gated on `fit.prefilter` only; `pcrec_artifact_has_dfa_scan`). `rx_info` mirror fields call the same derivations as the macros.
- `--emit-ir` is table-contract TSV ([DD-8], D106/D108; contract `docs/spec/ir_listing.md`, read before changing it): named `#section` blocks, cells literal or arena fragments, an empty population is a ROW with empty cells, never a `#` remark.
- `emit_state_legend` allocates from the arena; after a change run the witnesses in D105 notes (`x[0-9]{500}y`, `(?i)a{2,40}Z`, `((a)|b){0,4000}c`, `[a-z]{0,16384}`).
- Entry linkage is decided in `entries.c` only (EXPORTED / STATIC / OMITTED, derived edges from `entry_rows[]`); a request it cannot honour is an internal error. Attribute text comes only from `attr_text.c` (`pcrec_attr_text`). Part layout decisions only in `part_layout.c`'s declared first-match tables.

## Emitted text: discovered-by-emitting facts, masked flags, noclone

- Emission is DISCOVERED-BY-EMITTING for some facts (`Job.enc_mask`, class pool, cursor local, `has_push`): the prologue is written AFTER the program body; `job->enc_mask` is copied before use per the timing rule in `enc/CLAUDE.md`.
- Strategy-denial and force-pair flags are masked out of `rx_info.flags` (`emit_info_def`; mask DERIVED from `src/core/axes.def` minus the `kept` set, [FLAGBITS]): an axis that changes no answer must not make behaviorally identical artifacts differ; the activity record is `<PREFIX>_VM_STRATS` etc.
- `<prefix>_search` carries `__attribute__((noclone))` ([K24]): do NOT delete as decoration or replace with `hot`/`cold`; the lever must live in emitted text. One site serves both engines (`emit_search_head`). Reasoning: docs/dev/known_issues.md K24, docs/design/k24bisect_impl/k24_fix_note.md.

## [FINDALL-NEXT] lane iterland: additions carried from lane/itertri (verbatim)

- **emit_iter.c** — [FINDALL-NEXT] I1 + I4: the find-all iterator's text (`<prefix>_next`, `<prefix>_next_n`, the one body `<p>__one` both inline, its bind/step parts, the shared block's `rx_iter`, and setters); the section below.


## [FINDALL-NEXT] I1 — the find-all iterator (lane i1build, 2026-10-21; abi 82 -> 83)

`docs/design/findall_iter.md` rev 3 as cut by the I1 rulings (§12 there);
`docs/spec/match_api.md` §3.8 is the contract.

- **emit_iter.c** (new) writes the iterator: the shared block's `rx_iter`,
  its states and setters (`pcrec_emit_iter_abi_types`), the header's
  `<prefix>_iter_buffers` and `_next` declaration, and the iterator's text
  (`pcrec_emit_iterate`, the `iterate` combinator of `entry_rows[]`):
  `<p>__bind_checks` (the caller-position prologue `<prefix>_search` runs,
  via `pcrec_emit_startpos_guard`, run once at bind), `<p>__enter` (the state
  machine and the setters' normalization), `<p>__step` (the retry, the
  search, PCRE2's advance; commits only on a match), the VM's
  `<p>__step_own` (the storage binding `<prefix>_search` makes, tiered or
  frameless) and `<prefix>_next`. The engine emitters supply the search body
  `<p>__find` and the retry `<p>__retry` and say the step's shape
  (`PcrecIterText`).
- **The split** (iterfix2: only where it buys something). Where the search
  entry's caller-position prologue writes anything
  (`pcrec_startpos_prologue_on`: a UTF check, or an encoding start guard
  that is on) and an iterator is requested, emit_dfa.c's `<prefix>_search`
  is a wrapper (`pcrec_emit_search_wrapper`) over `<p>__find`, which
  `emit_search_head` writes as an EF_BODY row (entries.c);
  `find_body_shared` makes it `noinline` on the attempt route's label-table
  body and `always_inline` elsewhere; emit_vm.c's search loop is `<p>__find`
  and `<searchfn>_run` is the range test then the guard over it
  (`vm_emit_search_run_prologue`). Elsewhere nothing splits: the entries
  are their pre-iterator text (EMIT-1: instruction-identical) and the step
  calls the search entry itself.
- **The retry** is THE RETRY TABLE (emit_iter.c): the first row that applies
  names the stamp value and what the build needs (`PCREC_ITER_NEEDS_*`;
  compile.c builds `Job.nedfa` only on NEEDS_NEDFA). DFA:
  `pcrec_emit_dfa_retry` is one anchored attempt of `Job.nedfa` at `q`
  (`dfa_dir_anchored` with `^`/`\A` false past 0, through
  `dfa_start_from_context`). VM: `vm_emit_retry` runs
  `<p>__match_notempty`, a textual copy of the matcher
  (`vm_emit_guarded_matcher`) whose accept carries
  `if (scan_position == ctx->pos) goto <p>_fail;`, so no existing entry
  carries the guard.
- **The residual twins** (src/enc/enc.c): every out-of-line residual entry
  is a static `<p>__<name>`; the exported name is a one-line forwarder.
  Every reference writes the twin's second `_` through
  `pcrec_enc_twin_mark`, a scaffold byte, so a renamed call is the length it
  was. Checked by tests/codegen/run_residual_twins.sh (no PLT call in a
  -fPIC object).
- **THE SCAFFOLD BRACKET** (`pcrec_sb_scaffold_open`/`_close`/`_putc`,
  src/core/sb.c): every byte of the iterator, the split's new heads and the
  twins' forwarders is excluded from every length decision, the RQ-3 SIMD
  bracket's rules with its own count. Measured on a sample of DFA, VM,
  hybrid, utf8, `-futf-check`, var-bearing and compound artifacts: the
  counted size moves only where the DFA notempty root is built (a machine,
  counted like one) and by one byte on a compound shell's `__next_pos`
  reference. A new iterator line goes inside the bracket.
- **`rx_info.next`** (`emit_info_def`) points at `<prefix>_next`; `rx_nextfn`
  is declared on the tag `struct rx_iter` ahead of `struct rx_info`.

## [FINDALL-NEXT] I4 — `<prefix>_next_n` (lane i2build, 2026-10-21; abi 83 -> 84)

`docs/design/findall_iter_i2.md` rev 2; `docs/spec/match_api.md` §3.8.1-§3.8.2.

- **One body, two controllers** (emit_iter.c `emit_one`, `emit_controllers`):
  I1's `_next` body is the static `always_inline` `<p>__one`; `_next` is
  `return <p>__one(...)` and `_next_n` a loop of it up to `k`. Each is its
  own `PcrecEntry` (NEXT, NEXT_N; iterfix2) with its own linkage; NEXT_N's
  parts include NEXT (a NULL `capture_spans` goes through
  `<p>__one_local` -> `_next`), so `.next` is set wherever `.next_n` is.
- **The shared block** gains `rx_nextnfn` (beside `rx_nextfn`, emit_dfa.c)
  (scaffold). `RX_FOREACH` was dropped before landing (D175).
- **`_next`'s OBJECT is not I1's** (the TU gains a second caller of the shared
  statics); its body TEXT is, checked by `tests/findall/run_one_body.sh`
  (ruling R1, `docs/dev/lanes/i2build_report.md`).
- **Lane iteropt (2026-10-22, folded into abi 84):** a NULL `capture_spans`
  goes to the `noinline` `<p>__one_local`, the one function owning the
  NCAPS-pair stack buffer, so neither controller carries the
  `-fstack-protector-strong` canary; `rx_iter_init` writes every field, so
  `<p>__enter` stores only the header (plus the bind checks) and is
  `static inline`. `docs/dev/lanes/iteropt_report.md` has the instruction
  counts.
- **Lane iteropt2 (2026-10-22, folded into abi 84): the cursor.** `<p>__step`
  and `<p>__one` take the subject, `*lop` and (with the retry) `*flp` instead
  of `rx_iter` fields (`cursor_params`/`cursor_args`); `<p>__one` no longer
  binds. `<p>__one_call` (`_next`'s body, also `<p>__one_local`'s) binds and
  passes the iterator's own `&it->lo`/`&it->flags`; `_next_n` binds once,
  holds `s`/`n`/`lo`/`flags` in locals across its loop and stores them once.
  `run_one_body.sh` was re-pinned to this `<p>__one`.
  `docs/dev/lanes/iteropt2_report.md` has the instruction counts.


## [M4-SUBST] emit_subst.c — the subst artifact (lanes substb2/substext; moved here by lane substland, 2026-10-24)

[M4-SUBST] the subst artifact (`docs/spec/subst_api.md`): the prefix-independent subst types block (`PCREC_SUBST_H`: codes, flags, pieces, the map, the record, the `static inline` check and context setup), the per-template element `<prefix>_render` writing pieces, `<prefix>_subst_info` and its stamps; and the SUPPORT UNIT (`pcrec_emit_support`, `pcrec --emit-support`: `pcrec_subst_group_run`, the by-name helper, `pcrec_subst_flatten`, `pcrec_subst_replace_all`, `pcrec_subst_case_utf8` over the generated case map, abi-suffixed names, the FNV-1a content id over its own text). Module subst-extended: conditionals (padded pieces), and the CASE REGION (`<prefix>_region`/`_match`, a sizing then a writing pass) whose state tables come from the declared rule table `case_rules` (§2¶13). Changing the subst block's or the support unit's text is NOT an rx abi event (neither is ever in an rx artifact) but their `#error` guard ties them to `PCREC_RX_ABI_H`.
