# Review 2026-11-06 r3 — vlookbehind rev 4 (design, LAST re-check before the stage-1 build)

**Subject.** docs/design/vlookbehind.md REVISION 4 at 2ef0d1818; build tree main 80341284e (review
tree built there). Scope: rev 4's new machinery only (the `$_fwd_step` seam entry; DD12a(i) region
(1) from `pcrec_enc_entry_symbols` + `tests/codegen/enc_entry_list.c`; K49 via
`PCREC_ENC_BOUNDARY_ENTRIES`; the entry-shape knee; the -fno-comments doc pair; W13/W14/W-low
detectors; the U1-U9 build-unit table). §5.1's loop not re-litigated.
**Freeze drift:** none. Cited code unchanged 2ef0d1818..80341284e (both critics); decisions.md,
plan.md and the subject unchanged 80341284e..45f18903a (main at hand-back).

**Verdict (proposed): READY WITH LISTED TEXT FIXES.** No answer-level or speed-level finding. The
fwd_step mechanism itself holds: bit 8 free, no existing byte moves, engine_callable distinction
sound, the knee reads body bytes only (2628 under both encodings), -fno-comments strips the doc pair,
utf8 body == next_pos == bounded advance on 100.9M swept cells. The findings are all in the CHECKS
the design derives (DD12a(i) rule (b)/(a) on the UCP substitute entry) and in the unit table's
completeness (unlisted exact guards, oracle encoding, misnamed functions, owed items unassigned).

## RULING (manager, 2026-11-06)

Verdict accepted: READY WITH LISTED TEXT FIXES; no answer- or speed-level finding; the seam entry holds (100.9M swept cells). Every PROPOSED disposition is ACCEPTED (FIX-NOW FIXIND-1..4, READY-1..9; DOC FIXIND-5/6, READY-10/11). No further round: the fixes are applied by the stage-1 BUILD lane as its first commit (a tagged r3-1106 erratum pass on vlookbehind.md), and the build-side items (guards 7->9, the UCP witness for the derived floor, the S133/S134 anchor re-cut, the ctypes oracle's UTF/INVALID_UTF modes and compile context, the owed items assigned to units) become build-unit work. Frank's build go (2026-11-06) stands. Process change adopted: every DELIVER block carries `nonempty: Findings; PROBED-AND-HELD` so lanecheck cannot pass an empty template (critic skill §5).

## Lenses as run
| lens | model | question | why chosen |
|---|---|---|---|
| fix-induced (+ an exhaustive equivalence sweep in place of a soundness lens) | opus | what does each rev-4 addition (entry, symbol function, mask, operands, plants) read/add in today's code? | re-check of a revised design; items (1)-(4) re-spell, do not change, the step, so soundness was folded in as a sweep |
| readiness | opus | per unit U1-U9: cites hold, witness can fail, separable, complete? overall verdict | last re-check before a build go |
| verifier | sonnet | re-run every CONFIRMED finding that changes the design | skill §6 |
Standing questions (sibling, general form + unlocks): both lenses.

## Findings (consolidated; PROPOSED dispositions)
| id | lens(es) | sev | verify | finding | proposed | reason |
|---|---|---|---|---|---|---|
| FIXIND-1 | fixind | design | HOLDS | DD12a(i)'s derived rule (b) keys presence by ENTRY, but byte's SPAN_CASELESS_UCP defines the same symbols as SPAN_CASELESS (a substitute, enc.h:230-233); on `(*UCP)(?i)(a+)\1` byte={UCP}, utf8={SPAN_CASELESS,DECODE} and SPAN_CASELESS's one-sided presence is not admitted -> red as written. Pre-existing half: SIG_RE does not excise `unsigned char` heads (rev 4's head matcher repairs that) | FIX-NOW (text) | key rule (b) by symbol set, or have the reader print a `stands-for` column (UCP -> SPAN_CASELESS) that rule (b) reads |
| FIXIND-2 | fixind | check | HOLDS | rule (a)'s derived floor needs every listed entry reached; SPAN_CASELESS_UCP is reached only by block 718 of 4,843, outside the default 250-block slice; no explicit witness reaches it -> red on every default run | FIX-NOW (text) | add a `(*UCP)(?i)(a)\1x`-shape witness to item 4's explicit list |
| FIXIND-3 + READY-2 | both | maintenance | HOLDS (guard is run_codegen_tests.sh:1599, not 1606) | exact `resid_backdecl -ne 7` goes to 9 with residlbrange + twin, its header "one per top-level branch" breaks; fwd_step lacks its own exact guard (the :1126 precedent); tests/partlayout/writers.tsv:29 A4 class map lacks fwd_step (latent: frozen population, no range cell); run_partlayout.py:538 sec_seam regex and the c1 -fPIC nm arm (7 fixtures) do not cover fwd_step | FIX-NOW (text) | list each in U6 with its edit |
| FIXIND-4 | fixind | build | SUSPECTED, not verified | `size_t <p>_lb_count;` is the only uninitialised frame local; -Wmaybe-uninitialized risk under -Werror harness builds | FIX-NOW (text) | `= 0`, the span_cursor/rv precedent; costless |
| FIXIND-5 | fixind | maintenance | not verified | W-low's plant is a 4-5-site edit; mech rows carry at most 2 | DOC | say it is a scratch-tree one-off, or use the 1-edit equivalent (vm_set_line renders an untrailed write for SLOT_LB_LO*) |
| FIXIND-6 | fixind | design | HOLDS (fact) | `pcrec_enc_entry_symbols` restates enc.c:156-157's UCP side-emission condition: "beside" is not "derived" | DOC now, PLAN the general form | state the condition is shared via one predicate both call; general per-row side-emission hook as a filed row |
| READY-1 | ready | maintenance | HOLDS | S133's SAB_BEFORE is a 6-line block (seek + note + sentinel branch to tgt_fail); S134 anchors the branch; range's sentinel goes to L_n_i with a different note, so "one shared line, SAB_COUNT=1 unchanged" is false | FIX-NOW (text) | U8 lists re-cutting S133/S134 SAB_BEFORE/AFTER and SAB_DOC_FIGUREs |
| READY-3 | ready | check | HOLDS (path is docs/design/eng_brep_measurements/probes/pcre2_ctypes.py:141-142) | the ctypes binding encodes str patterns latin-1: `(?<=é\|bc)x` under PCRE2_UTF fails to compile -> every non-ASCII UTF cell exits 2; no PCRE2_MATCH_INVALID_UTF constant, no compile context (gate 3's max_varlookbehind=0 control unaskable through it) | FIX-NOW (text) | U6 owes the utf-8 encode (utfcheck_arm.py:48 precedent), the constant, and a compile-context call or a named other route for gate 3; tests/backrefs/CLAUDE.md in readers |
| READY-4 | ready | completeness | not verified (list) | owed items in no unit: W-low asan + --work-budget confirmation; gate 3 accept-set/classification harness; gate 4 budget cell; DD12a(i) re-validation plants; W-low codegen detector; K49 member floor | FIX-NOW (text) | assign each to a unit |
| READY-5 | ready | doc | HOLDS | gate 6 says `make test-codegen`; run_encoding_checks.sh runs under `make test-encoding-checks` (Makefile:835-837) | FIX-NOW (text) | one word |
| READY-6 | ready | doc | HOLDS | totals step is in `vm_plan` (emit_vm.c:10600); VmFrame built in `vm_emit_search_body` (:13056); back_step mask OR is in `vm_look_behind` (:7397), not vm_look / pcrec_emit_vm | FIX-NOW (text) | correct names in §5.1b, §5.6, U3-U5 |
| READY-7 | ready | completeness | HOLDS | U1 omits the stored widths representation (`const int *widths`, internal.h:1858, comment :1834-1870) and its readers (la_lb_raise mod_lookaround.c:395, fix_widths/hook :427-633, emit_vm.c:7122, vm_count_slots_look, vm_cost_look); LA_MSG_MAX comment unassigned | FIX-NOW (text) | add to U1's readers |
| READY-8 | ready | completeness | PARTLY | flipped refused.rxt cells (:104/220/228) move run_lookaround_diff.sh:270's exact NPO=69 guard; S136's DOC_FIGURE moves | FIX-NOW (text) | list in U7 |
| READY-9 | ready | doc | HOLDS | docs/design/stream/arev.md:341 "today's four" VmSeek members; K49 header run_encoding_checks.sh:2098-2105 "spelled TWICE", "linked next_pos" | FIX-NOW (text) | add to U4/U6 readers |
| READY-10 | ready | check | SUSPECTED | if the utf8 fwd_step row is built from next_pos's text/macro or calls it, K49's tie compares a source with itself (learnings §3) | DOC | state the row is its own literal |
| READY-11 | ready | check | SUSPECTED | no witness for a vm_slot_lblow off-by-one/collision; no S150-S153 twin for the lblow range | DOC | §5.1b states it answer-neutral and why, or names a witness |

## PROBED-AND-HELD (selected; full lists in review/)
fixind: next free bit 1u<<8; no mask number read anywhere; every entry loop gated by the mask; back_step only in lookbehind artifacts (22 probe artifacts); engine_callable readers are three id-specific consults; knee stamp 2628 both encodings incl. -fno-comments; doc pair under PCREC_CMT_NONESSENTIAL; symbol rule over 13 rows = SIG_RE names minus span_ci_decode exactly; span_ci_decode removal safe; K49 #include route works; sweep 278,327 + 100,860,160 cells 0 disagreements, 0 out-of-range reads; VmSeek/VmLocalKind switches have no default (missing arm warns); six b_seek sites unaffected; W13/W14(i)/(ii) detectors read their sites. Note for the build: inline rows' `decls` must be "" (NULL is the table sentinel). ready: VK_SEEK/LSET read only by renderers; sentinel count holds for range; sigs_of matches fwd_step; --work-budget/VALIDATE_ONLY/REACH_ONLY exist.

## By-id completeness
FIXIND-1..6, READY-1..11: every id above has a disposition. Verified: FIXIND-1,2,3,6, READY-1,2,3,5,6,7,9 HOLD; READY-8 PARTLY; FIXIND-4/5, READY-4/10/11 not verified (suspected or list items, text-only).

## Recommended
A D27 spec-first author for stage 0 stays recommended (§9). Standing questions: both lenses name the boundary-rule family (next_pos, advance, fwd_step; plus K50's start predicates) as one declared per-backend boundary predicate, NOT for stage 1; trigger a third backend or an edit to one spelling. General form: every check's hand list of seam names from the reader (SIG_RE, TWINNED, sigs_of, writers.tsv A4, sec_seam, c1 nm list, enc_entry_name/enc_is_twinned); trigger: the next entry or backend.

## Lessons for the guide (proposed)
1. lanecheck passed a findings file holding only its headings and "(in progress)": COMMON's DELIVER blocks should set `nonempty: Findings; PROBED-AND-HELD`.
2. A derived check over a seam must be drilled on the seam's SUBSTITUTE rows (an entry "in the mask instead of" another): keying by entry vs symbol diverges exactly there (FIXIND-1).
