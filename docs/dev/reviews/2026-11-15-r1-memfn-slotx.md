# Review 2026-11-15 r1 memfn-slotx — the slot harness's slotx pieces (code, light round)

DRAFT by the round coordinator: dispositions are PROPOSED; the kit manager rules them.

## Subject

- SUBJECT `f13a5935618da4867b7c1e22a3484b30db108962` (lane/memfn-slotx), BASE
  `1840f4e81e1b81331d35137c84ebda0ddf6744cb` = merge-base with lane/memfn-mfind (the branch is cut from mfind,
  not main). Reviewed: BASE..SUBJECT only, lane report/deliver and kit journal/responses/wake denied.
- What it is: the slot timing harness's pieces for kit-grid@6 (the mfind cards): the `reject` dim of
  find_hit@6 (gen.c plants rejected hits, drv.c reads them off the bytes, run.py's REJECT-RATE check), the
  arm's TARGET REGION frame (`arm_fixtures --frame`/`--target-facts`, `mf_form_includes`, link.py `framed()`,
  the ISA check, cell_text.tsv `target`/`target_isa`), ver-6 planning (`card_of`, J6B/J6H, `UNPLANNED6`),
  est.py's split by ver (`draft_split`, `zen4-grid6`, window-only pricing, record.py `WINDOWS`), eight sabotage
  rows S3160-S3167; kit edits: formhash.c's mfind-*/fn-memchr run `x` -> `xy`, kit-grid.tsv find_hit@6
  respelled in place.
- Rulings frozen at main `1b75dba61` (decisions.md `cb375f912`, plan.md `41b65ea00`). Re-diffed at critic
  return and at hand-back: main moved (77a8743e1) but neither ruling file changed; the subject did not move.
  FREEZE DRIFT: none.
- Review tree built once unlocked (`nice make -j2`); BASE built from a `git archive` export in the round dir;
  run kit = fixture binaries for both trees + a side-by-side driver (`COMMON.md`). The box was held by a
  queue job throughout; critics ran nice, one dry run at a time.

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| harness fidelity (FID) | opus | is the thing TIMED the thing GATED, KEYED and RECORDED, for (a) the reject dim end to end and (b) the target-region frame vs what pcrec emits | the subject is measurement-harness code adding a regime dim and a compile frame |
| check adequacy (CHK) | opus | can each new/changed check fail on its named defect: (a) the 8 rows alone, (b) a different defect of the same class, deleted/invented table lines | 8 new sabotage rows (> 5: opus) + new ISA, REJECT-RATE, key-dims and split checks |
| ruling check + slot tracing (RUL), with goals and both standing questions | opus | do the edits outside the slot's scripts keep their rulings and pins; does each new piece have one home | an in-place edit of an append-only card row; kit entry-table and kit.h edits; new frame mechanism |
| verifier | sonnet | re-check every CONFIRMED finding that would change code or design | skill §6.2 |

Which lens caught what: the ISA check's AVX-512 blindness was found INDEPENDENTLY by FID and CHK (F1); every
sabotage-row weakness (F3-F6) came from CHK's per-row and variant plants; every ruling/naming/home finding
(F7-F11) from RUL. FID's end-to-end trace of the reject chain found nothing wrong.

## Findings (consolidated) with PROPOSED dispositions

| id | lenses | verdict | severity | finding | PROPOSED | reason |
|---|---|---|---|---|---|---|
| F1 | FID-1, CHK-1 | HOLDS (EVEX half; `k*` half not re-run by the verifier, CHK's own repro stands) | answer (harness record) | link.py `ISA_NEEDS`/`isa_needs` classify by mnemonic + register name: EVEX AVX-512VL code on ymm/xmm reads as avx2/avx and `k*` mask instructions match no row, so a w32 cell keyed `x86-64-v3` compiled at `-march=x86-64-v4` (or with an avx512vl pragma) PASSES with `avx,avx2,bmi,bmi2`; on the Zen 4 timing box such code runs, so a cell would time AVX-512 code recorded as v3. The owed mfind-w64 arm will be judged by this table. | FIX-NOW | small; the check exists exactly for this over-reach. Classify by encoding (0x62 EVEX prefix => avx512f(+vl); est.py already decodes VEX/EVEX), add a `k\S*` row and `%[xy]mm(1[6-9]\|2[0-9]\|3[01])`; one sabotage row compiling a v3-keyed TU with an avx512vl pragma |
| F2 | CHK-2 | HOLDS (t2-under-every-deletion part not re-run) | answer-low / maintenance | A DELETED `ISA_NEEDS` line is silent (`avx` deleted: w16 VEX code passes under x86-64; `bmi2` deleted: fn-memchr's `shrx` passes under generic; `avx2` deleted: target_isa silently records `avx,bmi,bmi2`), and the table has no row for features targets.def enables for x86-64-v3 (fma, f16c, sse3, cx16, ...). No check ties the table to the targets' feature lists. | FIX-NOW | small: derive the features the table must cover from `--target-facts` of every planned target and refuse a feature with no row (the declared-map deleted/invented-line drill) |
| F3 | CHK-3 | HOLDS | maintenance (false DETECTED risk) | sabotage.sh's control runs only `dry control J2` + the est self-test (sabotage.sh:157-167), but t1/t2 score on J6B, r1/r2/k1 on J6H, v2/d1 on `plan report`: "control green first" does not hold for 7 rows; a regression of the UNPLANTED J6B/J6H/plan would score them DETECTED with no plant reaching anything. Today all are green unplanted (CHK ran them). | FIX-NOW | small: run the control for each job the selected rows name (J6H's ~9 min only when r1/r2/k1 are selected) |
| F4 | CHK-4 | HOLDS | answer-low (unwitnessed refusal) | Row v1's want (sabotage.sh:300) matches the self-test's WRONG line, which goes WRONG from the self-test's own predicate even with draft_split's per-set check DISABLED; the `DRAFT-VER MISMATCH` refusal (the only guard on the real writer path) is witnessed by no row. | FIX-NOW | trivial: want `\[slotx\] the draft split[^\t]*\t\(DRAFT-VER MISMATCH` (the planted run prints it) |
| F5 | CHK-5 | HOLDS | answer (ver-6 draft rows) | write_draft's per-ver row selection (est.py:906 `vrows = split.get(v, [])`) is reached by no self-test case or row: planting "every ver-6 row also into zen4-grid3" leaves selftest at 54 cases, 0 wrong. v1 names the writer's outcome but plants only inside draft_split. | FIX-NOW | small: an MF case that runs write_draft on the mfcard synth and reads back each `.vN` file's row keys |
| F6 | FID-2 | PARTLY | design | The cell identity (cell-text hash over the FILE+BODY spans, mf_form_hash/_cls, the draft row's `deps`) folds site TEXT only, never the instance's target token; link.py's target comparison reads one entry field twice (a control sharing its source). The verifier notes the target feeds the renderer (formhash.c:451 `mf_art_target`), so a target edit USUALLY moves the text; the identity is target-blind only where the text is target-independent. | FOLD INTO F8 | the target's home in the set identity is F8's ruling; if the ruling is per-target sets, the class carries it; otherwise add a target dep/cross-check per form across jobs in est.cell_texts |
| F7 | RUL-1 | HOLDS | design / doc | kit-grid.tsv respells the committed find_hit@6 row in place (adds `reject`), against measure_sets.md §7.2 (line 1244 at main freeze: "a committed (owner, quantity, ver) row never changes"). On substance the "before any merge or timing" argument HOLDS (row only on the mfind/slotx chain, no set/record/pin reads its dims, mfind's jobs superseded), but the rule says COMMITTED and the row is committed and pushed; the carve-out lives only in the card file comment and cards/CLAUDE.md, not at the rule's home; mfind_report.md:185 still states the old dims. | DOC (main's ruling) | ask main for the general-form sentence in §7.2 ("binds from the row's first merge to main or first set/record under it; before that a row is a draft of its lane chain") — RUL's leaning, over a ver-7 row that would leave a dead never-measured ver-6 card; plus a one-line "respelled by slotx" note for the mfind report |
| F8 | RUL-2 | HOLDS | design (ruling conflict), answer-adjacent | est.py:913 writes `class x86_64/zen4` for every ver, including zen4-grid6, whose rows mix generic, x86-64-region and x86-64-v3-region (AVX2) cells; per span_cards.md §2.7 (D188 + add. 1) `class` IS the set's target identity inside the digest, "a set is one target", and a several-target set's spelling is the format event reserved to [XARCH-DEV]'s J6 design. The per-row target sits only in free-text `source`/`compiler`. | FIX-NOW (interim) + main ruling | interim: the ver-6 draft REFUSES while a set would mix targets (no draft is due before a window anyway); then main rules (i) one set per declared target from the one run (split by (ver, target), the general form of draft_split; needs no new format; RUL's leaning) or (ii) the multi-target format event |
| F9 | RUL-3 | HOLDS | doc / maintenance | Job names J6B/J6H reuse span_cards.md's "J6" (unit S2g, vrun SIMD, HELD: :488, §2.7 heading :756, §9, Non-goals); no line says J6 now also names the mfind window. A later S2g J6 and these would share a prefix in records and STATES. | FIX-NOW | trivial now (no record holds the names yet), costly after the first window: rename (e.g. JMB/JMH) or one §2.7/§9 sentence — the manager picks the spelling |
| F10 | RUL-4 | HOLDS | maintenance / doc | The frame (`--frame` + link.py `framed()`) omits the family `#error` guard pcrec writes (memfn_targets.c:177-181) and the three g2 generators write, while both comments say "as pcrec places it". No codegen effect. It is also the FIFTH hand restatement of match_api.md §6.3.10¶15's placement order (memfn_targets.c, g2_mfind_gen.c, g2_any_gen.c, g2_pres_gen.c, now this), every spelling single-sourced from kit tables but the ORDER restated each time. | FIX-NOW (guard) + PLAN (family) | the guard is a fourth `--frame` part (small) and makes the comment true; unification = one kit entry `mf_frame_c(target, inc)` -> {guard, headers, region open/close}, trigger: the next ¶15 placement change or a sixth host (past the ~3-member point) |
| F11 | RUL-5 | read | maintenance (low) | card_of / draft_split / WINDOWS / FLOOR's ver column each have one home (card_of is the general form of the per-quantity lookup it replaces). The growing piece: each card ver adding a dim adds a named Arm field + twin() argument + DIM_FIELD lambda (`back` @4, `reject` @6; second member). | NOTED | general form: Arm carrying a `dims` dict keyed by DIM_FIELD names; trigger: the next card dim |

## Standing questions (RUL lens)

- **Sibling of a family**: the host frame writers (F10, fifth member: propose unification); the ISA census
  (run_targets.sh §3b objdump counts and link.py isa_check: second member; the kit already declares each SIMD
  row's instruction classes, MFIND_INSN/VRUN_INSN, a better source than a mnemonic regex, trigger the third
  member: S2g's vrun cells or a non-x86 box); per-ver tables (one home each; the window<->ver relation is implicit
  across WINDOWS and SETS, low); per-dim Arm fields (F11).
- **General form + unlocks**: a timed cell is (site text, host frame, subject regime), each read from its
  owner's table, so a new form is timed by an entry + a card, not a harness piece. Unlocks: S2g with no new
  frame/ISA work (trigger: main releases S2g); per-target sets from one run (F8 option i; trigger: the first
  ver-6 draft); the w64 arm as a formhash entry under an AVX-512 target (trigger: an AVX-512 row filed; not
  filed); `reject` as a per-stream-piece dim under D190 (trigger: plan_frame unit 3.0 / [PIECE-ACCEPT-RULE]
  pricing streams); a kit `mf_frame_c` (F10).
- **Goals (span_cards.md §1, in order)**: Goal 1 (moves nothing a caller sees) SERVED — 48 build/pcrec outputs
  (8 patterns incl. ones reaching the offset-skip/memchr site x 3 flag sets x plain/--emit-main) byte-identical
  BASE vs SUBJECT; the fixture render (124 files), `--query`, `--gate`, `--finder-rows` identical; only the four
  formhash entries' hashes/texts move and no file pins them (0 grep hits for all 8 old/new hashes). Goal 2
  SERVED for kit-grid@6. Goal 3 (self-checking set) AT RISK via F8. Goal 4 SERVED.

## PROBED-AND-HELD (summary; full lists in the critic texts)

- FID: the reject-50 chain end to end (key -> Arm -> tab.c -> gen.c seeded plant identical for gate and timed
  pools -> `_time`/`_gate` sharing `step()` -> round check); a real J6H dry run (172 arms x 7 launches, rc 0) whose
  `reject` lines equal subjects x E x R/100 exactly; key swaps (KEY-ARM or reject_check); identical records with
  different cells (keys distinct per form/gap/reject); card_of on every J6B/J6H key; the frame vs
  `build/pcrec-harness --harness=mfind -fmemfn-simd={x86-64,x86-64-v3}`: same headers, identical pragma text,
  region closed at TU end (only the guard differs: F10); 43 cell_text rows per form.
- CHK: 8/8 rows DETECTED alone, control green first each time; unplanted J6B (36 s) and J6H (9 min) dry runs
  rc 0; REJECT-RATE variants off by one hit, table 49-for-50, and a no-token bypass: 3/3 LOUD; DIM_FIELD deleted
  LOUD, invented SAME (harmless); card_of last-card and ver-6 deps dropped: 2/2 LOUD; window filter removed LOUD
  (by traceback, not a case line); `m6read_check_sab_anchors.py`: rc 0, 1299 sabotages, 1353 anchors.
- RUL: find_hit@6 readers (0 sets, 0 records, finder_check counts unchanged); formhash readers (arms.tsv,
  rows.tsv, row_floors.tsv, finder_check FORM_IDS/FORM_INSTANCE_FLOOR, rename/edit fixtures, FIXTURE_FLOOR): no
  pinned value moves; mf_form_includes reads the same `mf_includes(art)` pcrec reads (no second table); est
  selftest 54 cases 0 wrong; D190 like-for-like preserved (all four forms moved to `xy` together).

## By-id completeness

FID-1 -> F1; FID-2 -> F6; CHK-1 -> F1; CHK-2 -> F2; CHK-3 -> F3; CHK-4 -> F4; CHK-5 -> F5; RUL-1 -> F7;
RUL-2 -> F8; RUL-3 -> F9; RUL-4 -> F10; RUL-5 -> F11. Verifier: every item HOLDS except FID-2 PARTLY; two
sub-claims not re-run (F1's `k*` half, F2's t2-under-every-deletion) — the critics' own repros stand.

## Lessons for the guide (proposed)

1. **An ISA/feature check over disassembly classifies by ENCODING, not by mnemonic or register name** (F1: EVEX
   code on ymm/xmm reads as AVX2 by name); and its feature table is held to the targets' declared feature lists
   (F2). Candidate text for critics.md lessons and coding.md's check notes.
2. **A sabotage row's control runs the job the row scores on** (F3); a row's want names the CHECK's refusal
   text, not a self-test predicate that goes WRONG independently of the check (F4). Candidate text for the
   check-adequacy lens: "for each row, re-run it with the named check disabled: it must go MISSED".

Critic texts, the verifier's file and COMMON are in `2026-11-15-r1-memfn-slotx/` beside this draft (one
`plan.md:NN` cite in ruling.md respelled to the row tag for PL14).

## RULED (kit manager, 2026-11-15 03:00)

- F1 FIX-NOW as proposed: classify by ENCODING (EVEX 0x62 => avx512f(+vl)), a `k*` mask row and the high register names (xmm/ymm16-31, zmm).
- F2 FIX-NOW as proposed: the features the table must cover come from `--target-facts` of every planned target; refuse a feature with no row.
- F3 FIX-NOW: the sabotage control runs every job the rows score on (J6B, J6H, plan report), green first.
- F4 FIX-NOW: v1's want names the DRAFT-VER MISMATCH refusal text.
- F5 FIX-NOW: a self-test case runs write_draft on the mfcard synth and reads each ver's rows; plant the cross-ver leak and require WRONG.
- F6 FOLLOWS F8: if main rules per-target sets, the class carries the target and F6 closes. Otherwise a target dep/cross-check per form goes into est.cell_texts.
- F7 TO MAIN: the general-form sentence for measure_sets §7.2 (a row binds from its first merge to main or its first set/record; before that it is a draft of its lane chain), plus a one-line "respelled by slotx" note in the mfind report.
- F8 INTERIM FIX-NOW: the ver-6 draft REFUSES while a set would mix targets. TO MAIN: the kit leans to (i), one set per declared target from the one run, split by (ver, target), with no new format.
- F9 FIX-NOW: rename J6B/J6H to JMB/JMH, everywhere they appear (jobs, plan, sabotage rows, docs).
- F10 FIX-NOW the guard as the fourth `--frame` part. Unification (`mf_frame_c`) is FILED with a trigger: the next ¶15 placement change or a sixth host.
- F11 NOTED (the general form, an Arm `dims` dict, trigger: the third dim).
- Lessons 1-2: accepted as proposals for the guide (main's file); relayed.
