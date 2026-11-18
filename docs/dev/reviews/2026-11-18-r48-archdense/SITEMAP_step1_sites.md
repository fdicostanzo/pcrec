# my_sites.md (STEP 1, derived from requirements only, before opening the note)
Vocabulary from req row, tuning 2.41, R-30, R-41: handoff-attempts / -entry / -unbounded, handoff-reentry (pf), req-use table,
REQ_HANDOFF stamp, landmark_position, attempt_position, PCREC_W_UNBOUNDED / MF_HEAD_MAX_UNBOUNDED / head_max, drop-handoff
(DROP_HANDOFF, req_handoff_vm, req_handoff_dropped), PCREC_NO_REQ_HANDOFF (-fno-req-handoff, D195/FLAG-DEMOTE), rx_reqrun(_whole), req_landmark_maxoff.
Cmd base: git -C /home/pcrec/projects/pcrec grep -n -E 'handoff[-_]attempts|REQ_HANDOFF|drop-handoff|DROP_HANDOFF|NO_REQ_HANDOFF' 57fcb5737 -- src lib memfn/src memfn/include ; also 'landmark_position', 'emit_req_landmark_move', 'MF_HEAD_MAX_UNBOUNDED'

| site | found by | my class |
|---|---|---|
| emit_dfa.c emit_req_landmark_move (7919) the one text of re-entry move, 2 consumers | grep emit_req_landmark_move | SHARED / the site to change (where "last occurrence" compare replaces re-ask) |
| emit_dfa.c pcrec_emit_req_attempt_reentry (7955) VM attempt-loop re-entry | grep pcrec_emit_req_attempt_reentry | WIDEN/ROW consumer; called from emit_vm.c:13971 |
| emit_dfa.c pf_emit_handoff (7895) DFA forward-scan reentry | grep landmark_position | AS-IS or consumer of the shared move |
| emit_dfa.c emit_req_handoff_rest (1083) entry declare of landmark_position | grep landmark_position | the entry; NEW state (blocked look-ahead window / last-occ var) declared here |
| emit_dfa.c emit_req_reentry_use (1758) the pre-check re-ask text, .result="landmark_position" | grep landmark_position | the site that issues the (second) kit ask: NEW-SEAM (kit request R-n) |
| emit_dfa.c req_site_define / req_reentered (9338) / REQ_ON_MISS site description, memfn_sites.c (head_max 1640-1644) | grep head_max | NEW-SEAM: kit site facts (the ask's fact set; MF_SITE_ABI) |
| emit_dfa.c cand row table req-use rows 10710-10740 (handoff, handoff-attempts, -entry, -unbounded) + pf row handoff-reentry 10797 | grep handoff-attempts | ROW (rows reworded/merged; this is the decision table) |
| emit_dfa.c predicates req_handoff_applies/vm_run/entry/attempts/unbounded (8981-9112), pf_handoff_applies 9309 | grep req_handoff_ | ROW predicates (CHAIN: conjunct chain) |
| emit_dfa.c req_handoff_k (9154), req_handoff_stamp (9355), stamp REQ_HANDOFF (16605), cand slot name 12770 | grep REQ_HANDOFF | SHARED (K question) / stamp |
| emit_dfa.c 10287/10316/10356 .under/.by NO_REQ_HANDOFF in cand_select calls (9238) | grep NO_REQ_HANDOFF | flag site (D195 demotion of the flag) |
| emit_dfa.c req_handoff_assert_body 13709/14011, 14017 `landmark_position = search_from` | grep landmark_position | AS-IS/checks (structural assert) |
| emit_dfa.c 15067-15097 LANDWALK landmark_position walk (landmark_position++ loop) | grep landmark_position | SIBLING/SHARED: the existing last-occurrence walk row (drop-landmark-walk), same variable name |
| emit_vm.c 13832-13971 attempt loop entry + call to reentry; start-seek | read | consumer |
| compile.c drop-handoff rung 1215-1229, 1455, 1909-1922, 2462, 2675 ; internal.h req_handoff_vm 3569, req_handoff_dropped 4230 | grep drop-handoff | ROW (fit ladder) + Job/Ctx fields: must follow any new state |
| axes.def:235, lib/pcrec.h:1116 (bit 46), axes_dump.c:789, stamp_kinds.c:55 | grep NO_REQ_HANDOFF | flag/axis/stamp (D195 FLAG-DEMOTE: deny public->lever) |
| memfn/include/memfn.h head_max, MF_HEAD_MAX_UNBOUNDED (322), MF_SITE_ABI 29 | grep | kit seam (R-41) |
| memfn/src/presence.c:363-375, precheck.c:4, compose.c head_max | grep head_max | kit side of ask |
| src/gen/memfn_sites.c (head_max) | grep head_max | site builder |
| docs/spec/tuning.md 2.41 (p8b,p8c,p9,p9a), match_api.md (REQ_HANDOFF x10), limits.md 8.4, facts_listing.md, findings.md, lib/pcrec.h doc | grep REQ_HANDOFF docs/spec | spec hunks (D80) |
| tests: tests/codegen/run_prechecks.sh (32 REQ_HANDOFF, 5.12l grep of text shape landmark_position < attempt_position), run_dfa_stamps.sh:287, run_encoding_checks.sh:807-813, run_fallback_table.sh, run_recursion_identity.sh, tests/axes/run_axes.sh, tests/ci/measured_axes.tsv, tests/registry, tests/resource, tests/memfn/run_handoff_reach.sh, site_manifest.tsv, c10_presence.tsv, tests/litscan/*, startset/ | grep | text-shape pins that bind emitted text (abi event) |
| mech sabotages S1700-S1714, S1955-57, S3074-77, S463, S467, S473, S808/809, S844, S3119 | grep | binding checks |
| scripts/emit_sweep.py (4 REQ_HANDOFF) | grep | reader of stamp |
| kit: memfn/docs/requests.md R-30/R-41, responses.md | read | ledger |
| plan rows FLAG-DEMOTE, LANDWALK, REQRUN-VM, REQ-HANDOFF-L1 | grep plan | ride-along |

## STEP 2 additions from the note's VOCABULARY (note lines 54-70) [ADDED]
- CandUse.whole / CandUse.reenter, REQ_USE_HANDOFF (payload of req-use rows) [ADDED]
- RETRY slot's `adaptive-dense` row [ADDED]
- handoff_position emitted local [ADDED]
- pcrec_fact_req_whole_run(...)->whole_maxoff [ADDED]
- mf_site.ret_pred, mf_hooks.n/.lo, on_miss, on_miss_leaves, MF_H_ASSIGN [ADDED]
- zero-hit nouns: page size / stream chunk, match_api.md 5.2p6 "no streaming window state" [ADDED]
