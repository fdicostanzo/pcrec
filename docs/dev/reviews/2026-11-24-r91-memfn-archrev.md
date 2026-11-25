# Review r91 memfn-archrev (arch): the kit's architecture review note (R-49)

DRAFT by the coordinator, 2026-11-24. Dispositions are PROPOSED; the kit manager rules them.

## RULING (kit manager, 2026-11-24)

- Every disposition is ruled AS PROPOSED. F1-F20 are FIX-NOW, for a FRESH architect lane (archrev2, opus) on lane/memfn-arch, briefed from this review. Its note revision answers each F-id.
- F14's RUL-13 (is Q36 extraction still the trigger, or does the 11-04 manifesto supersede it?) is PLAN. It goes to main as a question, and the fix lane writes ARV-14's trigger as "Q36 extraction, or its successor as ruled".
- F21 is DOC. It goes to main with ARV-4's drift list (the [KIT-ARCH-STEP] row: "three stages" lists two).
- Re-check: a light arch round on the revision, covering ARV-9, ARV-10, ARV-12 and §8 (plus any ARV the revision re-sizes). The review number comes from main.
- Proposed process changes 1-4 (process.md) are NOT applied here. The critic and architect skills and the tools/ home are shared with main, so they go to main as proposals in responses.md.
- The critic texts' line cites into plan.md were rewritten to `plan.md [row by tag]` (plan_lint PL14).

## Subject

- Note: `memfn/docs/arch_review_2026-11.md` at 30abd87065b4173baaac596b5bfacf4606b7120f (lane/memfn-arch; tip at
  freeze c86feec23, which adds only a journal line after 4564d2752).
- Tree reviewed: T = a0f13ad83a2432f14341831ba4d1ff68964b79d9. main at freeze and at hand-back: e11c5f4ef. T and main
  differ only in memfn/docs ledgers and BOILERPLATE.md, so no cited site moved.
- Requirements: R-49 (memfn/docs/requests.md at the subject commit) and the owner's kit-arch-step ruling
  (docs/design/plan_row_bodies/KIT-ARCH-STEP.md).
- Rulings frozen at main e11c5f4ef. decisions.md, plan.md and docs/dev/guide are unchanged at hand-back: NO FREEZE DRIFT.
- FREEZE NOTE: the owner's standing kit memories that R-49 names are not readable on this box. Critics relied on R-49's
  wording and the records that quote them.

## Lenses as run

| lens | model | question | why chosen | time |
|---|---|---|---|---|
| aggregation (+ goals, + the two standing questions) | opus | per suggestion and section: chains, second mechanisms, private copies classed AS-IS or omitted; is each ARV's class/size/gate right; goals' CHECK lines; sibling of a family; general form + unlocks | always in arch mode | ~10 min |
| site-map completeness | sonnet | own site list from R-49 first, then a diff against the note's; does each §10 command print its claim | always | ~6 min |
| register | sonnet | every matching register row cited, with a verdict against its Ride-along triggers line; rows the note should have proposed | always | ~3 min |
| first-unit identity | opus | ARV-2/3/5-12 called answer-identical: real gate, separability, smuggled movers; binding checks found through the anchor map | the note lists answer-identical units | ~10 min |
| ruling check | opus | each ruling and owner quote, word for word against its record; uncited rulings; the owner question `window-file-split`; R-49's exclusions | the note cites rulings and asks one owner question | ~8 min |

Kit: `kit/anchor_map.py` and `.tsv` (266 sabotage anchor hits under memfn/, each with its enclosing function).

## Verdict

There are NO answer-level or speed-level findings. The note proposes no code, and every code claim it makes is
about structure. The findings are design and doc findings about the suggestions' scope, size, gate and records.
The note's backbone holds: 44 of 44 inline file:line cites and 33 of 38 §10 commands hold at T, and 18 of 22 owner
quotes are word-for-word. But the biggest suggestion (ARV-9) and the three seam suggestions (ARV-10, ARV-11 and
ARV-12) are mis-sized or mis-scoped, and the owner question is posed inverted. **Not ready for the owner summary
until it is revised.** A fresh architect should fix it, followed by a light re-check of ARV-9, ARV-10, ARV-12 and §8.

## Findings (consolidated), with PROPOSED dispositions

| id | finding | lenses (ids) | severity | proposed |
|---|---|---|---|---|
| F1 | **ARV-9's split leaves about 1,240 window.c lines in no file.** Unplaced: :1376-1775 (beyond plan_of/translate), :2840-3538 (THE FRAMED ASK, including `mf_wdecide` :3109, which is the plan call pcrec reads, and THE PARTS) and :4511-4672 (`wf_plan_class` and the five accessors). `translate` is called from FRAME and from the framed ask. Static names cross every boundary (TEXT->FRAME 26, PLAN->FRAME 10, ...), so the split needs a private header with about 60 de-staticized names. That contradicts §8's "adds no API and no seam" and A3's "opaque outside window.c" | SITE-3, AGG-5, FU-1 | design | FIX-NOW |
| F2 | **ARV-9 does not delete the presence<->window cycle it claims to delete.** window.c also calls `kit_byte_rate`, `kit_run_opts_of`, `kit_pres_run` and `kit_pres_run_span`. C-9's name list is a floor that was read as a census. presence.c's `kit_pres_picks` still calls `kit_pick_takes` in the PLAN file. Deleting the cycle means moving most of presence.c ([SP1D-KITSPLIT-SEAMS]'s shared primitives file). A8 (the finder<->presence cycle, plus finder<->FRAME at window.c:2630 / finder.c `wf_renders`) has no suggestion, row or leave-it | AGG-5, FU-2, AGG-10 | design | FIX-NOW |
| F3 | **ARV-9 is not "M, no-mover pure move".** Checks that bind by file name must change in the same commit. Concretely: about 47 window.c sabotage rows plus S1095 and S1096 must re-point SAB_FILE, or [SABANCHOR] goes red; `tests/memfn/run_purity_reach.sh` greps ONE file for both PLAN and FRAME rows and plants only into window.c, so it needs a multi-file redesign; the decider census needs about 21 re-keys plus its hard-coded presence.c plant; G2's `window.c@@`/`presence.c@@` plants (41 + 8) and rows_check S2983/S2988 move; and C15/C16, PROVENANCE rows and Makefile KITHDRS change. Re-size the unit and list its binding checks | FU-3 | size | FIX-NOW |
| F4 | **The text half calls the planner half's private set statics** (`shape` :4104, `two` :4134, `in_set` :4400). A1/A2's "the split already holds inside the file" is true of state, not of code. A pure move must either copy them (a private copy) or wait for ARV-5. State the order | AGG-6 | design | FIX-NOW |
| F5 | **The owner question `window-file-split` is posed unfairly.** (a) Its polarity is inverted: "is it INSIDE 'do not split now'?" is followed by the leaning "yes, allowed". (b) The D201 add. 2 "code organization" analogy drops "If that's true" and the kit's recorded caveat, and it was about emitted code, not source layout. (c) RECORDS omit D185's 2026-11-17 addendum (a planner/emitter module split as the example), the 11-04 manifesto's cross-tree end state, and ARCH-STEP's "sympathetic looking back". (d) Triggers (b) and (c) fire on ARV-9 itself, and "the kit split" is the manifesto split (see [POS-ONE-DETECTOR]). (e) Register row 9 ("a standalone move is churn") is the precedent and is not cited. (f) The EXAMPLE presumes NEON V's placement (R-49 excludes that) | RUL-2, RUL-3, RUL-4, RUL-5, RUL-14, REG-4 | design | FIX-NOW |
| F6 | **ARV-5 undercounts and would add a second mechanism.** The 256-bit popcount is spelled 8 times (the note says 2: `popcount256`, `one_member`, `single_byte` and 3 inline). "Is it ONE member?" already has a declared accessor, `kit_pos_class_of` (kit.h:451), which the note never names. The general form is to widen the `kit_pos_*` family, not to add kit.h `only`. k1_ref.c is G2's ORACLE and must be excluded, or G2 grades the primitive against itself. Sabotage rows S3106 and S3525 and two G2 plants anchor on the helpers. "8 helpers + 13 reads" double-counts 6 helper bodies | AGG-1, SITE-1, FU-4, FU-5 | design | FIX-NOW |
| F7 | **ARV-10 is larger than "S-M, kit".** `mf_site.denies` is also a contract-gate field (fields.def:228 plus its class, `cl_denies`, 10 FLD_denies contract cells in 9 files, and `rc_deny`). There are more deny channels: the levers, and options read inside predicates. An options.def row makes a user-visible `--memfn=` spelling and a registry §6 row, which contradicts registry.md §6¶7 ("born with the change that moves an emitted byte"), so it needs a spec amendment under D80. pcrec's build breaks unless memfn_sites.c changes in the SAME commit. It amends ruled Q-M1b-1 (integration.md) without citing it. [FLAG-DEMOTE]/D195 and register rows 3 and 15 rewrite the same `deny_map`. It is an MF_SITE_ABI event, not a pcrec abi event | AGG-3, FU-8, RUL-7, REG-1 | design | FIX-NOW |
| F8 | **ARV-12 re-proposes an item that is already filed.** The filing is window_site.md:517-523, with its own triggers "the next G2 site-builder regeneration, or a renderer change", and that change may already have fired. The direction is ruled by D162 add. 3; the note cites the earlier D157 instead. The field list omits `end_back`, `span_class` and `need`. G2 and the tests/memfn fixtures WRITE these fields through the public struct, so the unit rewrites its own independent control. That makes it an M-L unit with a harness re-cut. The emitting half is a LAYER seam (D185 add. 11-17), not a module seam | RUL-6, AGG-9, FU-7, RUL-11 | design/size | FIX-NOW |
| F9 | **ARV-11 and ARV-6 are two parts of one per-level emission family.** The other parts are choosing the level, opening the block plus includes, and the selector. There is a fourth spelling table, `mfind_simd` (vrun.c:548). The V form composes by prefix and keys by (level, width): it emits its 128-bit block under LV_X86_W32. ARV-11 is the third application of D146 add. 1's facts/C-spellings split (levels_c), so name the form. Dropping `LV_X86_W32` from the V renderer needs a form->level admission fact, which is NEON V's design (a smuggled feature piece). The note also pre-decides a layout. The vany selector row S2996 must be re-aimed, and targets_check.c reads vany text | AGG-4, AGG-12, SITE-7, FU-12, FU-11 | design | FIX-NOW |
| F10 | **ARV-8 is not a "re-pin".** Table S (`wf_srows`, walked privately at window.c:2529, a refusal verdict) and the `wf_support` keyed scan are omitted (B2, §0's count, B-s6). A hand array of 8 tables is the same chain spelled another way; the general form is registration on walk, and the 4 per-table `*_row_contract` enumerators go. Readers that go RED: run_g2.sh `rows_zero`, rows_check.py A (about 20 new rows.tsv lines; wfA/wfM write no text, so C has no form), and reach_equal.py. `FLOOR_ROWS` (a >= floor) does not. It amends plan_frame R5 / r13 V-3's recorded REACH scope without citing it | AGG-2, AGG-7, FU-6, RUL-8 | size/design | FIX-NOW |
| F11 | **ARV-7's declared layer order is violated on day one.** gate.c (a proposed leaf) calls UP into compose, runcmp, ofsskip and finder (gate.c:911-913, :750). File it as a carve-out or a row, not "S, pure move + doc". The compose.c :29-108 move itself holds (0 anchors, 0 census members) | AGG-7 | design | FIX-NOW |
| F12 | **ARV-1 files second mechanisms as noted deviations.** Several of the 11 EXC rows are whole tables or span several sites (`select_arm`/arms[], `fn_rows` BODY as a second T-FIND, `ren_fused`, the U6 shadow, the generic per-byte RUN chain). Judgement (e) excludes those ("never a second mechanism"). They are also the largest goal-1 strains, and §2/§3 do not list them. Split the rows by kind: implement-then-replace rows for some, noted rows for the one-site ones. State the register row's kind and status columns and its single home | AGG-8, REG-8(i) | design | FIX-NOW |
| F13 | **ARV-3 mislabels production entries as harness-only.** `mf_pres_ports` (emit_dfa.c:11692), `mf_finder_rows` (memfn_sites.c:906) and `mf_reach`/`mf_lever` are called by pcrec's compile/CLI path. ARV-3's list also omits `mf_ref_*` and `mf_kernel_find_any` | FU-9, AGG-11 | doc | FIX-NOW |
| F14 | **ARV-14 needs a noted-deviation row and a family.** It goes against "Product first, harness minimal" with no noted-deviation row. formhash.c has two siblings with no product caller: k1_ref.c (G2's oracle linked into the library it checks; the note's reason does not apply to it) and vany.c. Q36 extraction may be superseded by the 11-04 manifesto as the trigger (SUSPECTED) | REG-6, AGG-11, RUL-13 | doc/design | FIX-NOW (row and family); RUL-13 PLAN (manager checks Q36's currency) |
| F15 | **ARV-2's claims are wrong.** memfn/src and memfn/tests CLAUDE.md are already UNDER the 12,288-byte limit (11 and 25 bytes of headroom), and ARV-2 edits neither. The history home is memfn/include/NOTES.md, not memfn/NOTES.md. The move shifts about 75-78 live `memfn.h:N` cites, including the WHEREs ARV-4 re-pins, so state the order or cite by symbol | FU-10, SITE-5, AGG-13 | doc | FIX-NOW |
| F16 | **The register coverage is incomplete.** Rows 3, 14, 15 and 19 match touched sites but are not cited. A-PLAN, A-KIND and H-SITES are disposed against their Prerequisites, not their "Ride-along triggers" lines (A-PLAN's "any R-n that changes how a site is chosen" and H-SITES' "new [OPT-SIMD] sites" fit NEON V). Row 7b is NOT drift (:334-341 is still the body with its `strstr`). Row 10 owns the kit span widening that D-s5 re-proposes. ARV-5/6/7/8/10 have fired or named events but no register row, so a NEON V planner grepping the register finds only ARV-11. Name R-48 in ARV-11's event | REG-1..REG-9, SITE-6(c) | design/doc | FIX-NOW |
| F17 | **No hand-off list.** The architect skill's self-check is "no layout outside 'What the design step must decide'". The note has no such section, yet it fixes layouts: ARV-9's file ranges, ARV-5's kit.h home, ARV-11's key, ARV-10's field, ARV-12's record. Add the list and hand those choices on | AGG-10 | doc (method) | FIX-NOW |
| F18 | **Sites missed.** (a) Four G2 runners spell their own thread pool and subprocess helper beside `parpool.py` (SITE-4). (b) `wf_plan_class` is a sixth plan accessor (SITE-6b). (c) SUSPECTED: no rows for the seam's reply channels `mf_class`/`mf_rows`/`mf_wreply`/`mf_hooks`, which are where [SEAM-READER-CENSUS] applies (SITE-8). (d) SUSPECTED: no row for the Table E legacy bridge, `kit_legacy_serves`/`kit_legacy_arm` (SITE-9) | SITE-4, SITE-6, SITE-8, SITE-9 | maintenance/doc | FIX-NOW (a, b); the architect classes c and d |
| F19 | **Count, command and citation slips.** B1 says "8 calls over 7 tables" (it is 9 over 8). C-20c's pattern does not show B10's counts. The "single set" quote is cited to span_pick.md, but its record is journal.md:2976 / responses.md:3073. "keep the instrument" is the guide's rule, not D77's, and it applies after a MEASURED NO, so ARV-15 needs another ground. The addenda/kit.md quote drops "MEASUREMENT". [SP1D-ARGMIN]'s trigger is half-quoted | SITE-2, SITE-6(a), RUL-1, RUL-9, RUL-12(a,b) | doc | FIX-NOW |
| F20 | **ARV-13 omits [LAYOUT-DRAW].** That filed row names cards.py's layout pools, so splitting cards.py fires it | RUL-10 | maintenance | FIX-NOW |
| F21 | **[KIT-ARCH-STEP] plan row drift.** The row says "three stages" but lists two | RUL-12(c) | doc | DOC (the manager's, with ARV-4) |

## PROBED-AND-HELD (summary; the full lists are in the critic files)

- Inline cites: 44 of 44 hold. §10 commands: 33 of 38 print their claim (C-7a, C-16, C-19b, C-20c and C-34 do not).
- Owner quotes: 22 checked. 18 are word-for-word (some truncated); 4 slip (F5 b, F19).
- A1 (the planner writes no text, 0 lines), A3 (struct wf_plan behind accessors; compose.c reads it only through them) and B1 (8 `kit_table`s on one walk) hold. B4 (2 selector writers), B5 (2 `ops_of`, scope aside), B7 (the targets facts/C split), B10 (D155 add. 3 composable pieces) and B11 (5 equality sites) hold. A6 (5 argmins; the sixth-member trigger has not fired) and A10 (`consulted` is read with no writer) hold.
- ARV-2/3 "no abi event" holds: no check reads the memfn.h changelog or entry order (6 text readers checked).
- ARV-7's compose.c :29-108 move holds (0 anchors, 0 census members, 0 G2 plants).
- ARV-6 "vany text reaches no artifact" holds. ARV-8 "artifact-identical" holds (MF_TRACE only).
- ARV-10 and ARV-12 are MF_SITE_ABI events and NOT pcrec abi events: this holds (no emitted byte moves).
- Register drift: row 10 and A-KIND hold. Row 7b does not (F16). No noted-deviation row names a kit file: holds.
- The 72-member census with 11 EXC rows holds. D203 "not applicable" holds. "No other question" holds: each ARV's direction is ruled.
- R-49's exclusions hold except for F5 (f). The KIT-ARCH-STEP sequence holds.

## By-id completeness

AGG-1..13 -> F6, F10, F7, F9, F1/F2, F4, F10/F11, F12, F8, F17/F2, F13/F14, F9, F15.
SITE-1..9 -> F6, F19, F1, F18, F15, F19/F18/F16, F9, F18, F18.
REG-1..9 -> F7, F16, F16, F5/F16, F16, F14, F16, F12/F16, F16.
FU-1..12 -> F1, F2, F3, F6, F6, F10, F8, F7, F13, F15, F9, F9.
RUL-1..14 -> F19, F5, F5, F5, F5, F8, F7, F10, F19, F20, F8, F19/F21, F14, F5.
Every critic id maps to a consolidated finding. No finding went to a verifier agent: every CONFIRMED item is a grep or quote claim, and the coordinator re-ran a sample inline (see process.md).

## Lessons for the guide (proposed)

- An arch review of SECTIONS (not one feature) should name the suggestion each first-unit claim belongs to, and its gate. In this round, three lenses each re-derived ARV-9's ranges and two each derived its cycle. Assign size/gate to first-unit identity alone.
- A note's count command built from a NAME LIST (C-9, C-19b, C-16) is a floor, and it was read as a census four times. The architect skill's self-check should ask, for each count, "what spelling does this regex miss?" The critic-side twin already exists.
