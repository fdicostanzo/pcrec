# RD/readiness findings — critic round altnf2 (rev 1 re-check), lens: build readiness

Subject: docs/design/alt_normal_form.md rev 1 @ f7fd1a759; cites checked at the
BUILD tree 569c57d3a (review tree worktrees/crit-altnf2). Prefix RDY.

## Findings

### RDY-1 — §3.6's "-Wswitch-complete, a missed reader is a compile error" is false for three of the listed readers
CONFIRMED (code reading). Severity: speed/size (silent decline -> byte movers), doc. Effort: one sentence + brief line. Blast: stage 2a.
§3.6 says adding `KTEXT_UNIT` is safe because "the row is `-Wswitch`-complete, so a missed reader is a compile error".
At 569c57d3a the TEXT column readers are: switches in `src/facts/req.c:581`, `src/opt/mrl.c:486`, `src/facts/startset.c:82`,
`src/ir/nfa.c:596-610` (these would WARN under -Wswitch; only `make strict` makes it an error, -Werror is not the default),
and EQUALITY tests `pcrec_ast_row(a).text == KTEXT_ZERO` at `src/opt/possessify.c:446`, `:501`, `:924`, which no switch
diagnostic covers: an unedited possessify site would silently send `A_EMPTY` to `first_of`/`break`/decline and move BYTE
artifacts (possessify marks), contradicting stage 2a's predicted-mover list. The compile-error guarantee that does exist
(`tests/core/kindrow_check.sh`, internal.h's -Werror=switch) is over AKind rows, not KindText values.
Fix: §3.6 drops the -Wswitch claim, lists the three `==` sites as REQUIRED edits (or requires them rewritten as switches), and
stage 2a's gate includes `make strict` plus a byte emit-diff over possessify readers (zero movers outside the run).
Also unlisted in the §3.6 reader list: `src/core/internal.h:2505` (the A_CALLOUT `consume` override that writes `.text`),
`docs/design/inline_c.md` §1.8's column table (values `zero/own/any`, a design-spec reader), and
`tests/core/kindrow_check.sh` (row census) plus mech sabotages that plant TEXT values
(`tests/mech/sabotages/S1639_kindrow_var_text_zero.sh`, `S1653_callout_consume_read_empty.sh`): each must be re-read when a
fourth value appears.

### RDY-2 — Gate B0's population as spelled is not byte-only: `emit_sweep.py --bases byte` is ignored in plain `--ref` mode
CONFIRMED (code reading, scripts/emit_sweep.py at 569c57d3a). Severity: maintenance/doc (the REQUIRED gate cannot be run green as written). Effort: rewrite the population line. Blast: stage 1.
§5 stage 1 Gate B0: "`scripts/emit_sweep.py --ref BASE --bases byte` (its pinned streams ...) ... Empty emit diff".
`--bases` is read only by `--variant` (`run_variants`, :3400) and `--data` (:2903) modes; in plain `--ref` mode it is parsed and
validated (:3227-3229) and otherwise unused. The plain streams compile every `.rxt` pattern with its own directives (utf8 files
included), the composition stream compiles every `.rxt/.rxtin`, and the facts stream is hard-wired
`--emit-facts=byte,utf8` (:1076). Stage 1 moves utf8 artifacts by design, so the named population is red by construction, or
the build lane must invent the byte filter the note claims exists.
Fix: name a runnable byte-only population (e.g. `--variant` with a no-op variant at `--bases byte`, or `--patterns-file` of the
byte corpus lines with `--no-corpus`, or a stated post-filter on the movers by encoding), and state the utf8-ASCII clause's
population the same way. Must also count refusals per K35 as the note asks (`(*UTF)` under byte).

### RDY-3 — Stage 1 has an unlisted CHOICE mover: the VM quantifier rung flips (frames -> cursor) because `vm_det_seq` stops declining a merged class
CONFIRMED (code reading + 3 compiles). Severity: speed (an unlisted choice cell under D186) + design (a reader of the lowered child missing from §2.1/§3.3). Effort: one predicted-mover line, one census gate line, one §2.1 row. Blast: stage 1, every utf8 VM compile with a quantified multi-box class.
`src/gen/emit_vm.c:1885-1928` `vm_det_seq` descends `A_WCLASS` into its byte child (`:1891`) and declines `A_ALT` and `A_EMPTY` (`:1924`), so today every sealed multi-box class under a quantifier declines the cursor rung (`vm_cursor_fits`). Stage 1's sibling merge turns e.g. `(?i)é` (`c3 a9|c3 89`) into `c3[a9 89]`, a deterministic 2-byte stride.
Repro (review tree): `pcrec -e utf8 --engine=vm -fno-cls-kit -p rx -o c1.c --pattern '(?i)xé+y'` -> `RX_VM_RUNGS 0x4u` (frames-unbounded), program 3319 bytes; same at the default cls-kit axis -> `0x4u`; the stage-1 tree spelled `pcrec -e byte --engine=vm --pattern 'x(?:\xc3[\xa9\x89])+y'` -> `RX_VM_RUNGS 0x1u` (cursor), 1078 bytes.
§5 stage 1 "Kind" names only the derived scan PICK flips as choice cells, and Gate U4's VM census is islands only. The rung is chosen per A_REP; a rung flip is a choice cell (D186) needing its own listing and per-regime evidence (the cursor rung is called "a strict improvement" in the source comment `:1870-1873`, which is a claim, not a measurement).
Fix: add "VM rung flips (`RX_VM_RUNGS`) on quantified multi-box classes" to stage 1's predicted movers and choice cells; add an `RX_VM_RUNGS` base-vs-stage census beside the island census in U4 (same axes); add `vm_det_seq`/`vm_cursor_fits` to §2.1's reader table. Also stage 2b moves the same reader at code-point level (a factored `ab[xyz]` alternation becomes a det stride) and should list it.

### RDY-4 — §4.7 cites "D168 add. 3" for "the ruled reading keys the abi on emitted text"; D168 addendum 3 is the `\A`/`\z` fold
CONFIRMED (frozen decisions.md @569c57d3a :9846). Severity: doc. Effort: one cite. Blast: §4.7.
D168 addendum 3 is "`\A`/`\z` fold at both layers, staged" (ctx_span.md Q7); it carries "P2e is a second abi event" but rules nothing about what keys the abi. The ruled readings that do are D76 (scaffolding as a whole), match_api.md §6¶17-¶19 (which the sentence already cites) and D94 (readers of the number). Fix: cite D76/§6¶17 instead, or the exact ruling the lane meant.

### RDY-5 — Stage 2b's reader list is incomplete: two existing PUBLIC deny flags, their spec text and stamps change meaning; §11 proposes a new flag instead
CONFIRMED (grep at 569c57d3a). Severity: doc/contract (D80) + maintenance. Effort: a reader list and a decision line. Blast: stage 2b.
Stage 2b names only "`tests/altcls/` and its stamps". Readers of what it changes (altcls's two stages):
- `docs/spec/tuning.md` §2.6 `-fno-altcls-merge` (bit 10) ¶1 "merging a maximal run of single-character alternation branches into one class" and §2.7 `-fno-altcls-factor` (bit 11) ¶1 "prefix-factoring a maximal run of branches that share a literal first byte": both become false once the owner merges equal-width siblings and factors on fixed-width keys and suffixes; table rows `tuning.md:117-118`, `:1214`; `lib/pcrec.h:229` `PCREC_NO_ALTCLS_FACTOR`; `src/core/axes.def` rows.
- stamps `<PREFIX>_ALTCLS_MERGES` / `_ALTCLS_FACTORED` (`src/gen/emit_dfa.c:471`, `:3214`; `src/gen/stamp_kinds.c:47`) and the island activity count tied to them (`src/gen/emit_vm.c:572`).
- tests: `tests/altcls/run_altcls_tests.sh`, `run_altdiff.sh`, `tests/island/run_island_tests.sh`, `tests/axes/run_axes.sh`, `tests/codegen/run_form_census.sh`, `tests/recursion/run_specimen_identity.sh`; mech `S66_altcls_merge_drops_union.sh`, `S67_altcls_flags_mask.sh`.
§11 says 2b gets a public deny "spelled at build" without saying whether the two existing flags are re-specified (deny the owner's merge rule / factoring rules) or a third bit is added. Fix: stage 2b re-specifies the existing two flags (no new bit), lists the spec hunks (tuning §2.6/§2.7, the stamp definitions) and the test/mech readers above.

### RDY-6 — Stage 2p: the new core fact's contract readers are unlisted, and "2p goes alone" is not separable as written
CONFIRMED (readers, by grep) / SUSPECTED (separability, by reading §3.4-§3.5 against §5). Severity: doc/contract + design. Effort: text. Blast: stage 2p.
(a) A new `PF_FACT` row is read by `tests/codegen/run_facts_checks.sh` check 3 (one listing row per `facts.def` row per encoding) and check 4 (every deny flag's `deny:<flag>` set must equal `docs/spec/tuning.md`'s hand-written "Facts emptied" line: a run-derived fact emptied by `-fno-req-run`/`PCREC_NO_REQ_RUN` and `-fno-req-run-fold` must be ADDED to those lines or check 4 goes red), and by `docs/spec/facts_listing.md` §4.1.2 (one paragraph per fact; "the format and its vocabularies are promised", ¶1¶1), a D80 spec hunk in the same change. The note says only "`--emit-facts` names are advisory". The piece-group bound is a new `limits.def` row (provenance tier, `INTERNAL_H`), whose value the census sets: name that the census runs BEFORE the row lands (no silent default).
(b) §5 stage 2a: "If the census lists no bench cell, stage 2a waits (D77) and 2p goes alone." But 2p's width groups need the equal-width hull merge at ALT (`(?i)с` = `d1 81|d0 a1|e1 b2 83`: its width-2 group is two branches differing at two positions, which stage 1 cannot merge, so the width-12 москва piece's `[d0 d1][81 a1]` comes only from an ALT hull merge), and §3.5's ALT row assigns "one width" to 2a, "several" to 2p. The москва piece was measured by spelling the hull as a byte CLASS, which does not exercise the ALT arm. Fix: state that 2p alone builds the equal-width hull merge inside the group list while the single run stays today's (2a's row 1 then reads it), so 2p does not depend on 2a.

### RDY-7 — The public deny levers left "at build" (§10, §11) would cross Frank's flag-bit hard trigger; a build lane cannot allocate them
CONFIRMED (lib/pcrec.h at 569c57d3a; frozen plan.md [IFACE-PUSH]). Severity: design (blocks unit start). Effort: one §13 question or one decision line. Blast: stages 1, 2a, 3 (and 2b, RDY-5).
`PCREC_BIT(n)` in use: 0-54, 56, 57 (57 of 64; free 55, 58-63 = 7). [IFACE-PUSH]'s HARD TRIGGER (Frank 2026-10-10): "the push opens when <= 4 flag bits remain". §11 gives public denies to stages 1, 2a, 2b and 3: four new bits leave 3, so the third new bit trips the trigger ([FLAG-ACCESS] first, per the owner's standing rule). The note never mentions the bit budget, and §10 leaves "whether each stage's deny lever is public" to the build. Fix: decide in the note (e.g. stage 2b re-uses bits 10/11 per RDY-5; stage 1's lever public, 2a/3 test-only until their choice evidence shows a loss) or put the bit budget to Frank as a §13 question before the stage-1 go.

### RDY-8 — Existing mech sabotage rows anchored on the exact text each stage rewrites are not listed ([MECH-REACH])
CONFIRMED (grep of `tests/mech/sabotages/` SAB_FILE/SAB_BEFORE). Severity: maintenance (a row whose anchor vanishes stops reaching its site; a rewritten site loses its sabotage coverage). Effort: one list per stage. Blast: all stages.
The §5 preamble demands REACH only "for every new mech row". Rows whose `SAB_BEFORE` is the text a stage edits:
stage 1: `S366_wclass_island_default.sh` (anchor `case A_WCLASS: return vm_isl_words(v, a->l, out, depth, budget);`, the arm stage 1 changes to carry the inside-a-wide-class reading); `lower_enc.c` rows `S302`, `S303`, `S-U3`, `S-U7`, `S-U8` (re-check each anchor against the seal deletion and the owner call);
stage 2a: `S268_req_run_alt_overclaim.sh` (anchor `o.head = rn_common_head(w, l.head, r.head);` inside `rr_alt`, which 2a replaces by a row table), plus the KIND_ROW plants `S1638`-`S1641`, `S1653` (a fourth TEXT value);
stage 2b: `S66_altcls_merge_drops_union.sh`, `S67_altcls_flags_mask.sh` (altcls's merge code, which becomes the owner);
stage 3: `S451_req_hull_keeps_left.sh` (anchor the `rn_hull_mask` call that stage 3 merges into one position constructor).
Fix: each stage's brief lists the rows it re-anchors (or retires with a replacement), with REACH re-run, beside the new S-rows.

### RDY-9 — Every unit is externally blocked on span_pick 1e, and §4.2's reader list should be re-checked at 1e's landing
CONFIRMED (git log of the build tree: 1d landed `39e7b20c5`; 1e not landed; frozen plan [RUN-POS-SET] trigger "the build waits for span_pick unit 1e's landing"). Severity: doc. Effort: one sentence. Blast: all stages.
This is the note's own rule (§4.7), so not a defect; but 1e rewrites the window walk ("T-FIND as ONE walk... arms/fd_find text become renderers", span_pick.md §rows 1e/U3) in `emit_dfa.c`, where most of §4.2's reader audit rows live (`req_handoff_*`, `pf_window_of`, `req_site_define`, `emit_req_handoff_rest`, `req_part_window`). Fix: §4.7 adds "the stage-1 brief re-greps §4.2's reader list and §2.3's ledger lines at 1e's landing commit" (the ledger already drifted base: cites say 7ffbd4deb; they hold at 569c57d3a, but not necessarily after 1e).

## Per-unit verdict (the lens's question)

| unit | (a) cites hold @569c57d3a | (b) gates/witnesses runnable and can fail | (c) separable | (d) readers complete | verdict |
|---|---|---|---|---|---|
| stage 1 | YES (seal `lower_enc.c:369-384`, `emit_vm.c:4079/4091/4093/4099-4110`, `limits.def:411`, flags `-fno-cls-kit`, stamp `RX_VM_ALT_ISLANDS`, `L2 label empty`/`RX_VM_PROGRAM_BYTES 1502ULL` all reproduce); D168 add. 3 mis-cited (RDY-4) | B0's population is not byte-only as spelled (RDY-2); U1's model and U3's per-machine counter are build deliverables (specified enough to write); U2's chain is folds.py -> foldsweep.py -> a keep predicate the note does not name (rpsurvey's "8+width", minor); S-a/S-b/S-i/K123 reach (S-i island 1 measured; K123 matches today with `--features all`) | YES, after 1e (RDY-9); abi ritual complete per §4.7 | NO: VM rung reader (RDY-3), mech anchors (RDY-8) | ready with listed text fixes (RDY-2, RDY-3, RDY-4, RDY-7, RDY-8) |
| stage 2a | YES (`req.c:470` + comment `:464-469`, `:549`, `:344`, `:538`, `:698` fallthrough to `rb_row_into` `:579`, `kindrow.def:61`, `endwin.c:301`) | S-c reaches via the run-pinned prefilter (`RX_REQ_WHY "dominated"`, `RX_DFA_PREFILTER "run-pinned"`, memcmp "xyab"), S-g reaches (`RX_REQ_RUN "616278@2"`, needs `--features all`); the census model is to be written | gated by its own census (D77) BEFORE a build go: a measurement lane, not a build lane, is the next step (§13 q3) | NO: possessify `==` sites and the false -Wswitch claim (RDY-1), mech anchors (RDY-8) | not ready for BUILD (by design: census first); text fixes RDY-1, RDY-8 |
| stage 2p | n/a (new code); москва figures by spelling | the piece-list gate needs an independent model (to write); S-p is a FACT witness, stated | SUSPECTED not separable from 2a as worded (RDY-6b) | NO: facts checks 3/4, facts_listing spec, limits row (RDY-6a) | ready with listed text fixes (RDY-6) |
| stage 2b | YES (`altcls.c:180/210/260/312`) | S-d/S-k answer witnesses vs libpcre2 (premise.out); census to write | YES after 1e; A-ISL overlap listed | NO: public flags/spec/stamps/tests (RDY-5), rung reader (RDY-3 tail), mech (RDY-8) | ready with listed text fixes (RDY-5, RDY-7, RDY-8) |
| stage 3 | YES (`rn_hull_mask`, `pcrec_cube_of`, `pcrec_cls_cube`, `pcrec_memfn_wpos_cube` -> 256-bit `mf_wspan.set`) | S-e is bound-3 only (stated); S-f fails at either bound per the note | NO by design (O3): rides with [POS-ONE-DETECTOR], which has no design note and whose D187 "Later" waits for the kit split | partial: kit-side readers via the seam already take sets (holds) | not ready (blocked by O3 dependency, as the note intends) |

Goals lens: G1 (`make test`, `make test-axes`, PC-3) and G5 (per-machine `_next_state` counts, U3) are checkable as stated; G2 is checkable only once RDY-2 (B0 population) and RDY-3 (rung choice cells) are fixed; G3's ledger is a reviewer check (the cited lines hold); G4's "766 exactly" is checkable (U2, shapes2.py reproduces 24+489+253) but "about 898 after 2a" and the 2p piece claim are inferred until their censuses run. Stage order serves the ranking: stage 1 (G4/G5 with G1/G2 gates) -> 2a (G4, census-gated) -> 2p (G4 as a fact) -> 2b (G3) -> 3 (G4); 2b serves G3 before the remaining G4 of stage 3, which is consistent with O3.

§10/§13 blockers to starting a unit: the deny-lever/flag-bit question (RDY-7) blocks stage 1 and 2b briefs; §13 q3 (count first) blocks a stage 2a BUILD lane but not its census lane; §13 q2 only stage 3; the owner's file name, piece-fact name and group-bound value do not block (build/census decides). Everything else in §10 is outside the five units.

OVERALL: **ready with listed text fixes** for stage 1, 2p and 2b (RDY-1..RDY-9; none needs a redesign), stage 2a ready for its census lane only, stage 3 not ready by design (O3).

## PROBED-AND-HELD

- Every function the note names exists at 569c57d3a (52 names grepped across src/, lib/, memfn/src): all present; `req_landmark_maxoff` is the fact name (`pcrec_fact_req_landmark_maxoff`), not a function: fine.
- §2.3 ledger lines at 569c57d3a: `lower_enc.c:369-384` (seal + comment, K123 text) HOLD; `altcls.c:180/210/260/312` HOLD; `req.c:344/470/549/698` HOLD (`:698` `case A_EMPTY` falls through to `rb_row_into`, `:582` `KTEXT_ZERO -> rb_assert_into`); `endwin.c:301` (`a->r->k == A_EMPTY` skip) HOLD; `emit_vm.c:4093` HOLD; `limits.def:411` HOLD with the quoted RULED text; `req.c:464-469` comment reads as §2.2 (1) says.
- §3.6's other `ZERO` readers `nfa.c:598`, `mrl.c:487`, `startset.c:83`, `possessify.c:446/501/924` exist at those lines (only the -Wswitch claim fails, RDY-1).
- `match_api.md` §6¶18 (moved table = bump cause) and ¶19 (byte-exact whole-file within one abi) say what §4.7 says; current abi 95; changelog `docs/dev/history/abi_changelog.md` has [OPT-REQRUN-ENC] 37->38 and R-30 93->94 entries.
- Flags/stamps/targets exist with these spellings: `-fno-cls-kit`, `-fno-req-run-fold`, `-fno-altcls-merge`, `-fno-altcls-factor`, `--engine=vm`, `--emit-facts`, `RX_VM_ALT_ISLANDS`, `RX_ALTCLS_FACTORED`, Makefile `test-codegen`, `test-axes`, `test-registry`, `test-rxtsource`; `tests/altcls/` exists.
- `scripts/emit_sweep.py` has `--ref`, `--bases`, `--patterns-file`, `--no-corpus` (RDY-2 is about `--bases` semantics, not existence); bench has 392 `bench/*/patterns/*.rx`, 76 under `bench/utf8`.
- shapes2.py over UCD 16.0.0 reproduces 24 ascii + 489 + 253 (= 766) of 1454 classes, 37 mixed, 132 superset/allcube<=2 (0 compiles).
- Witness baselines (12 compiles total, 3 linked runs): S-i `RX_VM_ALT_ISLANDS 1`; seal VM `L2 label empty`, `RX_VM_PROGRAM_BYTES 1502ULL`; S-c run `78796162@0`, reached by the run-pinned prefilter (`memcmp "xyab"`, offsets `0*,1,2,3`; its REACH line should name `RX_DFA_PREFILTER_OFFSETS`, not the req pre-check, which is "dominated"); S-g `616278@2` (needs `--features all`); `(?i)xyzk` utf8 `58595a` (21 bits) as S-f says; `abcd()efgh`/`abcd(?:|)efgh` 4-position run; `(?:ab|aB)xy` 3 positions; `abcd(?:ab|Abyz)` keeps 2 affix positions (SLOT-4 premise); K123 `(?<=[a\x{3b1}])x` on `αx` matches (2,3).
- The kit seam already carries 256-bit sets (`mf_wspan.set`, `pcrec_memfn_wpos_bits`), so stage 3's set positions need no new seam field (D187 consistent).
- Compiles run by this lens: 15 single-pattern compiles, 3 gcc builds, 0 suites.

END OF FINDINGS
