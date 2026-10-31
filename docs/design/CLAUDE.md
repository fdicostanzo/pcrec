# docs/design/ — living design documents

Documents that describe a design AND the process/learning of building it
(panel-outcome blocks and refutations recorded inline rather than edited
away). Living: revised as the design is reviewed and built, unlike
docs/dev/'s append-only or historical records. Each note's status (PROPOSED /
PANELED / RULED / BUILT / SUPERSEDED) is in its own header; read a note's
PANEL OUTCOME / "REVISION n" / "§R" block before any section.

## Standing questions every design note answers (Frank, 2026-10-05)

**Every design note opens with GOALS** (Frank, 2026-10-23): 3-5 goals, each
with who benefits and a measurable form (comparison + margin), a priority
order for conflicts, and non-goals. Rule and example:
`docs/dev/guide/architecture.md`. Not retroactive: a note gains the section
at its next revision.

A design that introduces a MEASURED quantity, a CHECK or a DATA file answers
each of these in its own short section. First say whether the question is
RELEVANT; if not, say why in one line.

1. **The measurement regime.** For every number read or produced: the regime
   (latency vs throughput, hit vs miss, dependent vs independent calls, which
   box, compiler, libc) and whether a different regime would flip a decision.
2. **The independent control.** For every check or selection: what it is
   checked AGAINST, with proof the expectation does not share a source with
   the subject (`docs/dev/learnings.md` §3). Also who counts the population
   (K35) and whether each sabotage witness reaches its site ([MECH-REACH]).
3. **What moves when the data is regenerated.** For every table, calibration,
   stamp or generated file: which emitted bytes, pins or selections move on
   regeneration/re-measurement, and whether that is an abi event (D76/D94:
   readers found by grep, the byte-count reader class included) and a spec
   change (D80).

## Standing rules

- Update this file when files are added/removed or their roles change.
- A design document's own revision is its own change (D80): when a build
  meets and refutes a note, record it first in the lane report
  (`docs/dev/lanes/<lane>_report.md`) and edit the note in a separate,
  deliberate revision; mark corrections inline with the panel/round tag.
- `*_d27_extract.md` files (`la_d27_extract.md`, `sr_d27_extract.md`,
  `utf8_d27_extract.md`) are the D27 blinded author's extracts of a design
  note: regenerate ONLY by re-cutting from the source; never edit them
  independently of it.
- `*_impl/` and `*_measurements/` directories are kept separate from the
  design lane's directory on purpose (design-lane numbers come from
  prototypes, build-lane numbers from the shipped compiler); never merge or
  confuse them. Instruments read pcrec only where their own CLAUDE.md says so.
- Adopted critic instruments (e.g. `assertions`/`subroutines` probes,
  `simvm.py`) are kept AS THE CRITIC WROTE THEM; do not soften them.
- A rename must preserve the PROPERTIES names carry (greppable families a
  test asserts an absence through), not just readability (`m6read_samples/`).
- A bounded gate over a sorted corpus (`head -n N`) is a fixed fixture, not a
  population; an instrument needs a way to FAIL.
- A note's abi bump is "the next number at landing", never a literal.
- `studies/` lane work tied to a note (e.g. `studies/alt_dispatch/`,
  `studies/pf_know/`, `studies/hyb_reseed_cal/`) is never built by pcrec's make.
- Every subdirectory has its own CLAUDE.md; follow it.

## Files and subdirectories (one line each; status in the note's header)

Option sets, selection, cost
- `option_sets.md` — [OPT-SETS] named bundles of options (rev 2 applies panel r1); `option_sets_measurements/` — its cross-source probes.
- `sel_cost.md` — [SEL-COST] step 1 / [SEL-SIZE] (refuted); admission rule for compile-time selection terms; `sel_cost/` — census and drivers.
- `opt_dial_inventory.md` — [OPT-DIAL] step 0 inventory; `opt_dial_design.md` — [OPT-DIAL] step 1 design (paneled r60, revised, governance ruling).
- `regime_tables.md` — search-form selection by regime (draft rev 0).
- `prior_cost_unify.md` — [PRIOR-COST-UNIFY] one priced scan decision; `prior_cost_unify/` — instruments.
- `measure_sets.md` — [MEASURE-SET] measurement-set format/store/loading (rev 3); store lives in `measure_store/`.
- `decision_families_survey.md` — survey of if/else decision families; `decision_families/` — raw stamp inventory and `decfb0/` census.
- `dec_fallback.md` — [DEC-FALLBACK] one fallback ladder; `dec_fallback/` — edit set, anchor map, reach prototype.

Memory functions, kit, compound, iterator
- `memfn/` — [MEMFN] design record (requirements, ISA selection, survey, integration revisions through 4.9, twins, Linux results, later r17 notes); own CLAUDE.md; revision history in `memfn/CLAUDE.md`.
- `compound.md` — [COMPOUND] compound artifact (rev 2.2), first client [MATCH-SPLIT]; `compound/` — twin; `compound_callout_alignment.md` — compound/callout seams (D163 add. 5); `compound_entries.md` — every entry as a compound controller; `compound_entries/` — probes.
- `inline_c_requirements.md` — [INLINE-C] REQUIREMENTS (not a design, no build go): user C inside pattern `(?C{...})` and template `${{ }}`/`${( )}`; use cases and draft tests, R-P/R-T/R-S rows, post-match predicate analysis, prior art, trust gate, open questions (lane inlinecreq, rev 0).
- `inline_c.md` — [INLINE-C] DESIGN, pattern side (PROPOSED rev 1, lane inlinecrev1, after panel r1): one `A_CALLOUT` node for `(?C`/`(?{`, one call-site emitter and the shared return table, firing classes + `once`, generated segment functions, `verify` as a D156 FINISH row, the `--allow-code` + `sha256` pin trust gate, stages 0/1a/1b/2-5.
- `match_split_requirements.md` — [MATCH-SPLIT] requirements; `match_split_pinonly.md` — SUPERSEDED (D163) by `compound.md`.
- `findall_iter.md` — [FINDALL-NEXT] find-all iterator; `findall_iter/` — probes.
- `kit_proof.md` — [KIT-VERIFY] U1 report without an engine; `kit_proof/` — evidence.
- `ctx_span.md` — [DD-11.5] span-context producer, `A_BOL`/`A_EOL` into `A_CTX` (D168); `ctx_span/` — evidence.
- `artifact_manager.md` — [ART-MGR] many-artifact catalog/loader direction document.

Search, start, scan and engine optimization notes
- `xcall.md` — [OPT-HYB-RESEED-XCALL]; `hyb_reseed.md` — [OPT-HYB-RESEED] (built).
- `pf_know.md` — [PF-KNOW] what a prefilter proves to the VM.
- `startset.md` + `startset/`, `where_to_start.md` + `where_to_start/`, `start_table.md` + `start_table/`, `start_landing.md`, `locate_finish.md` (D156), `revend.md` ([OPT-REVEND]), `endmark.md` + `endmark/` (D164) — the start/locate/finish family.
- `litscan_s1.md`, `litscan_s4.md`, `litscan_k82b.md`, `litscan_k82h.md`, `compare_stack.md` — [OPT-LITSCAN] notes and the compare-stack coordination map.
- `reqbyte_freq_pick.md`, `reqpos_2b.md` — [OPTLOOP.2] cycle-2 notes.
- `premultiplied_dfa_table.md` [OPT-3], `offset_k_skip.md` [OPT-K], `artifact_size_term.md` [ART-SIZE] (+ `artsize_impl/`), `prefilter_count_independence.md` [OPT-4] (+ `opt4_impl/`), `opt5_step2_twopass.md` [OPT-5], `two_tier_entry.md` [OPT-1] step 2, `emitter_form.md` [ENG-FORM] (D82).
- `alt_dispatch_study.md` — [ENG-ISL.S0] alternation-dispatch study (`studies/alt_dispatch/`).
- `emit_backends_notes.md` — FORWARD NOTES only (Frank 2026-10-30, nothing scheduled): record-level cleanups, other code targets, a bytecode VM, a matcher IR with backend libraries, memfn on the backend side.
- `cls_tree_design.md` — [CLS-TREE]; `poss_arms.md` — [ART-POSS-ARMS] (+ `poss_arms_measurements/`); `altcls_pinned_impl/` — [OPT-ALTCLS] pinned instrument.
- `c3_three_way.md` — C3 tier narrowing (built); `tt4m_harness_batching.md` — [TT-4M] step 2b.

Engines, bounded repeat, budgets
- `engine_m4.md` — [M4.2] backtracking-VM design; `match_api_m4.md` — [M4.1] match-API freeze; `subst_template_design.md` — [M4-SUBST]; `design_callout_abi.md` — callout ABI (D38, paneled R21).
- `k18_memo_design.md` + `k18_measurements/`; `eng_brep_design.md` + `eng_brep_measurements/`, `possessify_impl/`, `rungselect_impl/`, `counterk_impl/` — [ENG-BREP] lanes.
- `anchored_match_unwrapped.md` — [ENG-ABS] second mechanism (unwrapped forward DFA).
- `k23_impl/` (K23 / MRL design), `mrl_impl/` ([M4.6d]), `m46a_impl/` (budget calibration), `k24bisect_impl/` (K24), `m46e_impl/` ([M4.6e]).

Modules (design notes with `*_measurements/` siblings)
- `extension_design.md` — module/extension architecture (D34; Part II is the redesign of record); `design_notes_mod06.md` (`unicode-props`), `design_notes_mod07.md` (`--explain`).
- `assertions_design.md` + `assertions_measurements/`; `atomic_groups_design.md` + `atomic_groups_measurements/`; `backrefs_design.md` + `backrefs_measurements/`; `lookaround_design.md` + `lookaround_measurements/` + `la_d27_extract.md`; `subroutines_design.md` + `subroutines_measurements/` + `sr_d27_extract.md`; `frame_buffer_design.md` (D71 item 2).
- `data_plan.md` — [DATA-PLAN] large data paid only where used, shared where repeated: pcrec's own UCD tables (A) and Unicode data in matchers (B) (PROPOSED); `data_plan/` — its instruments.
- `uprop_more.md` — [UPROP-MORE] `\p{}` binary properties + Bidi_Class (PCRE2 catch-up) and Block/Age (extension) design (PROPOSED).
- `utf8_design.md` + `utf8_measurements/` + `utf8_d27_extract.md` ([M5.0]); `ucp_design.md` + `ucp_measurements/` ([UCP]); `utf_valid_design.md` + `utf_valid_evidence/` ([UTF-VALID], D133); `encoding_data_layout.md`.
- `definitions_table.md` — [DD-11]; `dd13_format/` — [DD-13] file format; `findings/` — [FINDINGS] (D83); `patfacts/` — [PATFACTS] (D120); `oracle_interface.md` — oracle interface/answer store.
- `variables_common.md`, `variables_pattern.md`, `replace_design.md`, `variables_roadmap.md` — [VAR] design set (paneled r1, revised; pattern half landed 2026-09-23).
- `subst_api_r4_draft.md` — [M4-SUBST] the DRAFT `docs/spec/subst_api.md` was generated from for `replace_design.md` §R4 (lane substb2); RETIRED to a pointer (review 2026-10-24 r1, IFACE-9): the spec is the contract. `subst_measurements/` — the §R2 glue probe and the §R4.13 `subst-extended` probes against libpcre2.
- `design_registry_selectors.md` — SR-9 selectors (superseded by R6); `registry_built_status_memo.md` — registry built-status memo.
- `m6read_samples/` — [M6-READ] approved sample commented artifacts (style of record).
- `plan_row_bodies/` — verbatim long-form text of plan.md rows moved out by [PLAN-LINT] step 2; the plan.md row is the status of record.

## Pointers

- `APPROACH.md`, `docs/dev/decisions.md` (D-ids cited per note), `docs/dev/plan.md` rows, `docs/dev/reviews/` (panel files), `docs/dev/lanes/` (lane reports), `docs/spec/` (the contract, D80), `docs/dev/learnings.md` §3, `memfn/CLAUDE.md`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design.md
- `findall_iter_i2.md` (+ r1 panel) — [FINDALL-NEXT] I4 `_next_n` and `RX_FOREACH` design; entry text in NOTES.md.
