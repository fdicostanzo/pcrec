# Decision-families survey — raw stamp-led inventory (lane decsurvey, 2026-10-06)

Verbatim text of lane decsurvey's handback, delivered as a message (its own
"handback failed: spawner gone"); it wrote no file. It is the SEED for the full
survey (`docs/design/decision_families_survey.md`, lane decsurvey2), not the
deliverable: stamp-led, no ranked evaluation rows, latent inconsistencies named
but not probed with concrete inputs. Abbreviations: ED=src/gen/emit_dfa.c,
EV=src/gen/emit_vm.c, § = docs/spec/tuning.md, M = docs/spec/match_api.md §6.3.
T = table-driven, C = code (if/ternary/switch), N = number.

## Inventory (stamp | values | T/C/N | write site | spec)

- ENGINE_SEL | selected, forced, declined-nullable-default, overflowed-dfa, overflowed-prefilter, collapsed-prefilter, declined-nullable, size-cap-retry | C: 8-arm ternary esel_of src/opt/select_engine.c:943; switch ED:396; write ED:424 | M4375
- ENGINE_WHY | prose, VM only | C | EV:11183 | §2.11
- REQ_WHY | emitted, none, one-attempt, dominated | T req_admits[] ED:7249 (5 rows) but via switch req_why_name ED:7288 (set-leads+emitted -> "emitted") | ED:10194 | §2.29
- REQ_HANDOFF | K / none | T req_uses ED:7364 + code ED:7389 | ED:10203 | §2.41
- VM_START_SCAN | first-class, none | T dfa_pfs, ED:6939 | ED:10210 | §2.42
- DFA_PREFILTER | run-pinned(-bounded), offset-set(-bounded), first-memchr-bounded, first-class(-bounded), memchr(-bounded), byte-class(-bounded), none | MIXED: T dfa_pfs ED:6863; ATTEMPT is code ED:10393 | ED:10507 | M4600
- DFA_SCAN | unanchored/attempt/empty | C ED:10379 | ED:10506
- DFA_TABLE | premultiplied, indexed, mixed, none | MIXED T dfa_reprs ED:5499, mixed/none code ED:4383 | ED:10519 | §2.13
- DFA_SCAN_EDGE | none, range, fold, bitmap, kit, mixed | MIXED: gate T dfa_edges ED:8067; value=clskit test name ED:8151; rollup code ED:4432-4471 | ED:10533 | M4650, §2.18/2.22/2.33/2.37
- DFA_START | pinned, reverse-pass | T ED:7894 | ED:10541 | §2.19
- DFA_MATCH | unwrapped, search-filter | T ED:7678 | ED:10571 | §2.15
- VM_RESEED | exact, clamped, anchored, adaptive-dense, adaptive.. | T pcrec_reseed_rows EV~11011 (pred switch EV:11082) | EV:11332 | §2.35
- VM_PREFILTER hybrid/none C EV:11222; VM_PREFILTER_WHY C EV:11230; VM_PREFILTER_LANG exact/count-collapsed C EV:11255
- VM_PREFILTER_LANG_WHY | forced, exact, no counted repeat, nullable collapsed language (unreachable), dfa overflow retry exact nfa N, size cap retry exact N > cap | C: ternary compile.c:1864 -> enum -> switch | EV:11285-11325 | §2.17
- UNROLL_K_WHY | default, option, denied, size-model, size-model-declined, cap-rescue, capacity-declined | C ternary compile.c:1977 | EV:11402 | §2.16
- VM_ENTRY_SHAPE | auto, plain, shared, forward, inline | C if-chain vm_plan_entry EV:10798-10970 | EV:11560 | §2.21
- VM_START | anchored/gstart/unanchored | fact renderer startanch.c:161 | EV:11558
- VM_PRUNE_CEILING none/prefilter-window/subject-end C ternary EV:11642; STARTPOS_GUARD align/guarded/permissive C ED:10053; UTF_CHECK inert/whole/off C ED:10065; TUNE T tune.c ED:10211.
- Fact stamps (facts.c renderer): END_WINDOW ED:10114, REQ_BYTE ED:10140, REQ_RUN ED:10167 (+"/mask" suffix §2.39), DFA_PREFILTER_OFFSETS ED:10516.
- NUMBER: ALTCLS_*, DFA_UNIFORM_FOLDS, MAX_EMIT_*, VM_CALL_*, UNROLL_K, VM_ROOT_MINW, VM_FRAMELESS, VM_ALT_ISLANDS, VM_CLS_*, VM_LIT_RUNS, VM_PROGRAM_BYTES, VM_RUNGS/STRATS/PRUNES (bitmasks), NSLOTS, budgets, FAST_*, RUN_WORDS runcmp.c:276, FINDINGS, NCAPS/NVARS (EV:11384-11714, ED:456-2236).
- Dispersed (code, not table): ENGINE_SEL, UNROLL_K_WHY, VM_PREFILTER_LANG_WHY, VM_ENTRY_SHAPE, VM_PREFILTER(_LANG), STARTPOS_GUARD, UTF_CHECK, VM_PRUNE_CEILING, plus ATTEMPT/empty special-casing in DFA_SCAN/PREFILTER/TABLE/SCAN_EDGE.

## Findings

- **Form+reason mixed:** REQ_WHY ("emitted" is a form; none/one-attempt/dominated are reasons; two rows share "emitted"; "none" conflates found-nothing with -fno-req-byte; ED comment says four answers, table has five rows). ENGINE_SEL (routes vs outcomes; declined-nullable-default sounds like fallback but isn't). VM_PREFILTER_LANG_WHY (sources, vacuity, numeric rung strings, one unreachable value). DFA_SCAN_EDGE "none" has 4 causes. DFA_MATCH "search-filter" = cand_always row hiding 5 populations (M4658), only size-cap one visible in ENGINE_SEL. DFA_START "reverse-pass" same shape (M4701). UNROLL_K_WHY: spec §2.16 says SEVEN values; compile.c comment ~1970 says SIX; ladder has 7 arms.
- **Two altitudes:** REQ_RUN serves req-run (§2.28) and req-run-fold (§2.39, "/mask" suffix, no own stamp). DFA_SCAN_EDGE serves scan-edge, view-edge (§2.37 "No stamp of its own"), cls-fold, cls-kit; "none" cannot name the denying axis. ENGINE_SEL/ENGINE_WHY/VM_PREFILTER_WHY. VM_START_SCAN and DFA_PREFILTER first-*-bounded = one start-set axis (§2.42), two stamps. REQ_WHY "dominated" reads dfa_pfs scan byte; req-use calls req-admit. ATTEMPT/empty tested by hand at ED:4383, 4455, 10379, 10393.
- **Fallback prose vs code:** dfa_matches "search-filter" and dfa_search_starts "reverse-pass" are cand_always; ATTEMPT/empty causes come from dfa_scan_name upstream, not the table. req-admit "emitted" row comment "always (fallback)" vs spec "artifact emits a pre-check". ENGINE_SEL "selected" is a mid-ladder arm (!dfa_disabled), spec calls it the common case; spec table order differs from arm order.
- **Spec ladders, code not table:** §2.21 (EV:10798 if-chain, may_attr/may_fwd); §2.11 (AND over analyses[] + ternary); §2.5/§2.17 drop/collapse ladder (compile_driver); §2.16 (compile.c:1977); M4375 (esel_of ternary); §2.23/§2.36 (ED:10053/10065); §2.25/§2.4 VM_PRUNE_CEILING. VM_RESEED is a table but predicates dispatch by switch.
- **Same predicate, different words:**
  - one start position: §2.29 G2 (start_max 0/search_from; VM_START anchored|gstart + linearity), §2.42 line 3528 ("unanchored (start_anchor)... anchored or \G runs one attempt"), §2.35 VM_RESEED "anchored" row, match_api.md:2326, DFA_PREFILTER none (§2.29). All the start_anchor fact.
  - "$/\Z/\z view or word context": M4613-4618, tuning.md:2846, §2.18 line 1629, §2.19/M4701 (1664), §2.26 line 2387, §2.42 "SEEDED" (3559; match_api.md:2323).
  - unanchored/not nullable/<256 members: §2.42 lines 3528-3530 (VM) and 3571 (DFA hat, plus T=S proper subset of E); nullable wording also §2.17 and §2.23 line 2172.
  - DFA scan in front: §2.29 G1/K65/K66, §2.42, M "artifact CONTAINS a DFA scan"; code predicate once, pcrec_artifact_has_dfa_scan ED:383.
  - attempt is linear (§2.29: exact hybrid or frameless) never a named predicate.
  - ATTEMPT-or-empty listed as a cause in each of DFA_START/TABLE/SCAN_EDGE/PREFILTER/MATCH spec rows.
- **Suggested order:** ENGINE_SEL; UNROLL_K_WHY + VM_PREFILTER_LANG_WHY; VM_ENTRY_SHAPE; small ternaries; shared predicates (one-start-position, view/word-context, ATTEMPT-or-empty).
