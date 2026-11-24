# The window family split: window.c and the position primitives into small files, once

DESIGN rev 2, lane wsplitd2, 2026-11-24 (rev 1: lane wsplitd, same day). Not a build go.
Architecture: `memfn/docs/arch_review_2026-11.md` (ACCEPTED rev 4): ARV-9 (the split), ARV-16 (the
primitives' home), ARV-5 (the set family) and ARV-7's text-buffer leaf, as one unit. This note
makes the choices that review left to the design step: §8 H1 (the cut and every section's home),
H2 (the primitives' home), H3 (the set family) and H8's placement half (where the public entries
live).

**Read §R2 first.** Rev 2 answers review r95 (`docs/dev/reviews/2026-11-24-r95-memfn-winsplit.md`)
item by item, applies its RULING (O1-O7 as recommended) and carries the round's lesson 1: the cut is
no longer a name census only, it is ASSEMBLED into the actual files by a committed assembler and
every assembled file is compiled (`gcc-16 -fsyntax-only`, with and without `MF_TRACE`), §11.

**Base.** B = `a0742283a` (lane/memfn-wsplit). Its code equals rev 1's T `a0f13ad83`
(`git diff --stat a0f13ad83 a0742283a -- memfn/src memfn/include tests memfn/tests Makefile`: empty),
so every `window.c:N` cite below reads the same at both. Commands run from the repo root at B, with
`D=docs/design/memfn/window_split`, `W=memfn/src`, and `S=$PCREC_TMPDIR/scratch/<lane>` the scratch
dir the assembler writes (`S/asm`, never `memfn/src`).

**Numbers convention.** Every count names its command and says CENSUS (the whole population, exact)
or FLOOR. The instruments are committed in `window_split/` (own CLAUDE.md).

## §R2 — what rev 2 changes, by review id

| r95 id | disposition | where |
|---|---|---|
| W1 frame's grain (O1) | APPLIED: frame / ren split; the {frame, ren} SCC removed by per-table checks | §3, §5 O1, §12 |
| W2 kit_pick.c's names | FIXED: two-file reading stated for main to confirm; `kit_mass`, `kit_run_member` to kit_pos.c; `sets_at` family-private; `kit_run_set` ruled | §6.2 |
| W3 family vocabulary in stop | FIXED: window.h's shared section; `use_nothing` a `static const` there | §4.1 |
| W4 ARV-7's order | FIXED: C0b, ARV-7's text-buffer leaf `kit_kb.c`, before the split | §6.4, §8 |
| W5 finder <-> family loop | FIXED: stated as the H1 outcome, with its reason and trigger | §6.5 |
| W6 H8 placement half | FIXED: `mf_pres_ports` placed (presence.c, outside the cut) | §6.6 |
| W7 D204 attribution and limits | FIXED | §0 |
| W8 [IR-FORM] member (4) | PLAN, main's: recorded only | §13 |
| W9 general form, unlocks | FIXED: `kit_<family>.c` | §6.3 |
| W10 "only one" | FIXED: `kit_pos_count(s) == 1`, one spelling | §6.1 |
| W11 A4 beside ren_find | NOTED: recorded as a noted deviation, in the code comment | §5 A4 |
| W12 U2b population | FIXED: widened list; R-1 exclusions named | §6.1 |
| W13 kit.h names | FIXED: §10's rule with the H3/TIE exception; three names leave kit.h | §4.3 |
| W14 V block widths | DOC: they live in window.h | §9 |
| W15 complete header types | FIXED: window.h derived by assembly and compiled | §4, §11 |
| W16 forward declarations | FIXED: assembler rule R4; every prototype homed | §11.1 |
| W17 range boundaries | FIXED in cut.spec | §3 |
| W18 `run_member` | FIXED: not renamed; a census blind spot | §4.2, §13 |
| W19 accessors not all moves | FIXED: each one's kind and signature | §5 |
| W20 commit counts | FIXED | §8.1 |
| W21 missing prototypes, MF_TRACE | FIXED: G1 carries `-Wmissing-prototypes` and an `MF_TRACE` pass | §8.2 |
| W22 no gate executes a plant | FIXED: static apply check per commit, `--plants` at the tip; dependency on lane/memfn-plantcheck stated | §7.3, §8.2 |
| W23 decider census counts | FIXED: per-commit pins, counted from the assembled tip | §7.2 |
| W24 purity NEVER anchor | FIXED in U1 | §7.4 |
| W25 re-spell lists | FIXED: derived by `binders.py`'s re-spell table | §7.5 |
| W26 SAB_AFTER compile claim | FIXED: probed, 186 + 1 + 75 | §7.5, §11 |
| W27 G1's scope | FIXED | §8.2 |
| W28 V w32 block arm | FIXED: x86-64-v3 arm; runs on the Mac (text emission) | §8.2 |
| W29 gates by box | FIXED | §8.3 |
| W30 file-name readers | DOC: 50 files, CENSUS | §7.7 |
| W31 O4 | DOC: the unsupported "halves" claim withdrawn | §12 |
| W32 instrument blind spots | FIXED/STATED beside each number | §13.1 |
| W33 published numbers | DOC: re-measured | §2, §7, §13 |
| W34 §4 cells | DOC | §4.4, §6.6 |
| W35 F1's NOTES.md | DOC: memfn/NOTES.md | §13 F1 |
| W36 Goal 1's population | FIXED: one instrument, both ends | §1, §4.4 |
| W37 evidence outside the subject | DOC: `spec_v4` and `fields.py` numbers dropped | §13 F4 |

## §0 — Rulings applied

The owner's rulings, D204 (2026-11-24, verbatim):

1. "Split: how do you plan to split? If you anticipate this file growing, splitting out once rather
   then multiple times would be best. I'd rather have many small concisely defined files than larger
   sprawling ones"
2. "Split: yes on trigger but once you do split, make it count. Consider where reasonable the
   interface of the file. If there is a table and functions that search it specifically, they belong
   together in that file. Then the public names are just those functions."

Main's accepted readings (D204; rev 1 wrongly called them the kit manager's): the split lands at
NEON V's trigger (R-48), BEFORE NEON V; the primitives move ONCE, to their final file, with
`kit_mass`; the file-interface rule is general. D204's limits, kept: [IR-FORM] member (4) is
overtaken for window.c at this trigger only; its "emitter-shaped SIMD forms" clause stays and binds
§9; the [SP1D-KITSPLIT-SEAMS] seam-facts half stays. Main's R-1: `formhash.c` and `k1_ref.c` are not
this unit.

Review r95's RULING (kit manager): every FIX-NOW and DOC item in this revision; O1-O7 as recommended
(§12); W8 PLAN (main's), W11 NOTED.

## 1. GOALS

Ranked; each measurable.

1. **One table, one file, and only the searchers public** (ruling 2). Measure: `tables.py` (W36's
   one population: every file-scope table or object of the family, and every family function body
   that names one outside the file defining it). At the pure move (`assemble.py --pure`) 13 of 30
   are named in another file's function bodies; at the tip 2: `wf_find_arm` and `wf_floor_arm`, the
   arm objects, which are not searched tables (§4.4). Comparison: tip <= 2, and each of the 2 named.
2. **Split once, final grain** (ruling 1). 22 new `.c` files of 81-428 lines and the private header
   `window.h` (561 lines) replace window.c (4,672), take `kit_mass` and `kit_run_member`, and take
   compose.c's text buffer (C0b). Measure: R-48's diff (NEON V) touches no family file except
   `window_vform.c`, plus at most one line of `window.h` (§9).
3. **Answer- and byte-identical at every commit.** Measure: §8's gates per commit against the
   unit's base.
4. **No file cycle inside the family, and presence.c calls down only.** Measure: `kitgraph.py` over
   the assembled tip with every kit file but the family and presence.c dropped prints no CYCLE
   (§6.5; held at the tip).
5. **Every binding check still binds, re-aimed in the commit that moves its text.** Measure:
   `binders.py` over the assembled tip finds every binder's text exactly once (mech 187 sites,
   G2 75 plants, purity 49, census 57; all OK, §7), and every re-pointed SAB_AFTER and plant TO
   compiles in its new file (§7.5).

Non-goals: no behaviour change; no new form; no NEON V design (§9 places it); `formhash.c`/
`k1_ref.c` untouched (R-1); the layer order's TEXT (H8's other half) untouched beyond C0b's leaf;
no re-cite of docs' `window.c:N` cites (§13 F6).

The three standing questions (docs/design/CLAUDE.md):

- (1) Measurement regime: none applies. Compile-time moves only; byte identity of every emitted
  artifact is the speed proof. The one quantity the split can move is the kit's own stack frames
  (cross-file calls stop inlining): measured by G6, which owes a base run (§8.2).
- (2) Independent control: `scripts/emit_sweep.py` compares the base binary's emitted bytes with
  each commit's over the corpus, a source the split does not touch; G2/G3 check the family against
  `k1_ref.c`, outside the family (R-1). The assembler's compile evidence has its own control: the
  same files assembled WITHOUT the edits fail (38 of 82, §11.2), and B's own tree passes (40/40).
- (3) Regenerated data: none (no `data/*`, `.def` row or measured set is regenerated).

## 2. Premise and today

- `wc -l memfn/src/window.c` = 4672 (CENSUS).
- At B the kit's file graph (`python3 -I $D/kitgraph.py $W <(echo 'window.c <- window.c 1-4672')`,
  function bodies) has one SCC of 9 files: compose, finder, gate, generic, mismatch, ofsskip,
  presence, runcmp, window (CENSUS). Its edges into window.c include presence.c -> window.c
  (`kit_pick_takes kit_pos_spelled kit_run_member kit_tie_member_key`), mismatch.c (`shape`),
  ofsskip.c (`count`), finder.c (`wf_renders`). Rev 1's "SCC of 6" was with compose.c and gate.c
  dropped; kitgraph reads locals and parameters as calls (W32), which r95 found adds 2 false edges
  there; no conclusion below rests on that run.
- `window.c:N` cites in the tree: 819 in 186 files (`git grep -c -E 'window\.c:[0-9]+' | awk`
  summed, CENSUS at B; rev 1's 784/179 matched no tree, W33).

## 3. The file list

The cut is `$D/cut.spec` (rev 2; census-readable, `NEW <- SRC a-b ...`), with W17's boundaries
corrected: ask ends at :2876 (`wstream_of` whole), text at :3879, floor starts at :3880 (its
comment), efind takes :2649, vform :4321, floor :4608, `kit_mass` takes presence.c :56-83 (its
contract comment). `window.h <-` lines name the text the header takes (types, the family's
vocabulary, the family comment). `-` lines are dropped heads (window.c's SPDX/Provenance/title,
:1-7, :66-71; the old TIE comment :132-139, rewritten by O3). Every window.c line is homed exactly
once (assembler rule R1, §11.1; `window.c` keeps 0 lines).

Tip numbers: `python3 -I $D/assemble.py . $S/asm` prints each file's lines and exports; PUBLIC =
names in kit.h or memfn.h (CENSUS of the `#define X MF_NS(..)` lines naming a definition of the
file); FAMILY = names in window.h; STATIC = file-static functions/tables/objects.

| file | from (B) | lines | PUBLIC | FAMILY | STATIC | holds |
|---|---|---|---|---|---|---|
| `kit_pos.c` | window.c :231-284, :937-962; presence.c :56-83 | 128 | 10 | 0 | 0 | the position questions: the set family (`kit_pos_in count shape two full first class_of spelled`), `kit_run_member`, `kit_mass` |
| `kit_pick.c` | window.c :78-131, :140-151 | 83 | 3 | 0 | 2 | the TIE table `wf_ties` and its searchers: `kit_pick_takes`, `kit_tie_exchanges`, `kit_tie_reseeds`; `kit_tie_takes` static |
| `kit_kb.c` | compose.c :27-115 | 100 | 8 | 0 | 1 | ARV-7's text-buffer leaf (`kb_*`, `kit_out`, `kit_fail`, `kit_flush`, `kit_sink_ok`) |
| `window_cands.c` | :152-230, :285-459 | 188 | 0 | 6 | 7 | the candidate list (`cands`, `rd_set`, `rd_core`, `wf_extent`, `run_role`, `pinned_yes`) |
| `window_check.c` | :460-580 | 133 | 1 | 0 | 2 | the statement rules (`wf_check`) |
| `window_stop.c` | :72-77, :581-836 | 254 | 0 | 3 | 22 | the cost table, Table A with its rows and walk; A2 |
| `window_margin.c` | :837-901 | 98 | 0 | 1 | 12 | Table M, `m_margin_holds`, `m_pair`; A3 (O5) |
| `window_verify.c` | :902-936, :963-1229 | 314 | 0 | 4 | 23 | Table C and `c_plan` |
| `window_decide.c` | :1230-1374 | 135 | 0 | 3 | 1 | THE DECISION: walks A, M, C through their searchers |
| `window_plan.c` | :1375-1555, :4511-4607 | 216 | 7 | 2 | 0 | THE PLAN (`offer_at`), `plan_of`, the `wf_plan_*` accessors (O2) |
| `window_legacy.c` | :1556-1775 | 221 | 0 | 4 | 0 | the legacy rows' helpers |
| `window_frame.c` | :1776-1892, :2564-2606, :2691-2839 | 277 | 3 | 1 | 12 | Table E (T-FRAME) and its searchers, `wf_plan_site`, `wf_prepare`, `wf_tables_check` (O1) |
| `window_ren.c` | :2193-2563, :2607-2648, :2877-2887 | 415 | 5 | 5 | 16 | THE TRIPLE: the renderer tables with `ren_find`, Table S, the support table, `wf_renders`, `wf_arm_pick`, `wf_find_decide`; O1's two, A4 |
| `window_span.c` | :1893-2065, :3706-3730 | 227 | 0 | 4 | 23 | the span form table (wfS) and its searchers; A5 |
| `window_efind.c` | :2066-2192, :2649-2690, :4083-4089 | 191 | 0 | 5 | 5 | E-find's plan |
| `window_ask.c` | :2840-2876, :2888-3266 | 428 | 2 | 0 | 15 | THE FRAMED ASK: `mf_wdecide` (memfn.h), `wf_agree` (MF_TRACE) |
| `window_parts.c` | :3267-3538 | 286 | 3 | 0 | 4 | THE PARTS (`wf_part_site` now static, W13) |
| `window_text.c` | :3539-3705, :3731-3766, :3847-3879, :3897-3965 | 302 | 0 | 15 | 3 | `wf_rc`'s primitives and the H form |
| `window_test.c` | :3779-3846 | 81 | 0 | 2 | 2 | the candidate test text |
| `window_floor.c` | :3880-3896, :3966-4035, :4608-4641 | 133 | 0 | 3 | 4 | THE FLOOR ROW's text and contract, `wf_floor_arm` |
| `window_find.c` | :4036-4082, :4090-4320, :4471-4510, :4642-4672 | 360 | 0 | 16 | 7 | E-FIND's text and contract, `wf_find_arm` |
| `window_vform.c` | :3767-3778, :4321-4470 | 175 | 0 | 2 | 6 | the V form and its level block (§9) |
| `window.h` | the `window.h <-` lines | 561 | - | 76 | - | the family's private header (§4) |

Sums (CENSUS from the table): 22 new `.c` files; PUBLIC 42 names (of which new to kit.h: the 6 set
family names and the 2 TIE predicates, §4.3); FAMILY 76. Lines 81-428; 4,745 lines in the 22 files
(each file's new prologue included, R5). No file keeps the name `window.c` (O4).

## 4. The private header and the owner's rule

### 4.1 window.h

`memfn/src/window.h` is assembled (R3, R5): SPDX/Provenance head, the family comment (:8-65), the
guard `MF_WINDOW_H` and `#include "kit.h"`, then the moved types in source order (`@TYPES@`), then
one section of declarations per defining file (`@DECLS@`), then the two arms. It joins Makefile
KITHDRS (a hand list; KITSRCS is a wildcard), carries C16's lines and a PROVENANCE row, and every
name is spelled `#define name MF_NS(name)` (C15). Only family files include it.

W15 made the header's content a COMPILE question, not a name count: the five renderer row types,
`ren_key` and the `wf_rc` body are complete in it (30 dereference lines in efind, ask, floor, find,
plan need them), and the `-fsyntax-only` of every includer is the binding check (§11). Composition
(`python3 -I $D/ents.py $S/asm/memfn/src/window.h`, CENSUS of top-level entities): 76 MF_NS names
with their 72 prototypes and 4 extern objects, 13 typedefs, 3 structs, 7 enumerator groups, 14 other
macros, and 1 table: `use_nothing`.

W3, the family vocabulary: the row contracts' vocabulary (:757-790, :792: `WF_SERVES_*`, `NU`,
`use_nothing`) is not Table A's, so it is window.h's shared section, not stop's. `use_nothing` is a
`static const` array in the header: `NU()` takes its `sizeof`, which an `extern` declaration cannot
give (r95 RDCODE-4), and the alternatives (a bound stated twice, or a copy per user) state its
length in two places. Each includer gets its own copy of a one-row read-only array; no code compares use-list
addresses (CENSUS: `grep -n -E '(==|!=) *&?use_|->uses *(==|!=)' memfn/src/*.[ch]`: 0), and its
only readers are contract initializers (`WF_CT_A(.., use_nothing, ..)` twice in stop, `NU(use_nothing)`
in span). `use_entry` stays in stop (its only user).

### 4.2 Crossing names, pure move and tip

- Pure move, family only (`python3 -I $D/census.py $W <family spec> --calls`, the cut.spec with the
  header, sink, kit_kb and presence lines removed; CENSUS of code text): 86 statics, 40
  types/macros/enumerators and 10 kit.h names cross; no file cycle over calls. (Rev 1: 79/34/19,
  at a coarser cut and before W17.)
- Tip (`census.py` over the assembled files, one `F <- F 1-99999` line each): 1 static crosses,
  `run_member`, and it is the W18 false positive (`WR_M(run_member)` names `mf_wreply`'s member in
  a macro argument); 0 types; the rest are window.h/kit.h names.
- `run_member` is NOT renamed (W18: rev 1's `wf_run_member` rename is withdrawn); its real use is a
  member, and MF_NS does not apply to members. The other rev 1 collision worry (`count`, `shape`,
  `full` as members) is gone with H3's renames (`kit_pos_*`), and syntax-only compile of every
  includer is the check (§11).

### 4.3 kit.h (W13)

kit.h keeps only names with a caller outside the family, plus ONE stated exception: the set family
(`kit_pos_*`, H3) and the TIE predicates are kit-wide VOCABULARY (ARV-5 names other kit files as
their users; U2b makes them so: compose, finder, ofsskip, precheck, presence, pffind, generic call
`kit_pos_*` at the tip). Changes (CENSUS: `diff` of the sorted `#define X MF_NS` names, B vs tip):
+6 (`kit_pos_in count shape two full first`), +2 (`kit_tie_exchanges`, `kit_tie_reseeds`), -2
(`kit_tie_takes`, now static; `kit_tie_member_key`, moved static to presence.c beside `member_key`,
its one caller), -3 (`wf_find_arm`, `wf_floor_arm` to window.h: no non-family file names them;
`wf_part_site` static in parts). `wf_support_rows` stays (test caller `arm_fixtures.c`). 134 -> 137
names.

### 4.4 The owner's rule, table by table (W36, W34)

`tables.py DIR FILES..` (CENSUS: every file-scope `table`/`obj` entity of the files, static or not,
and every function body naming one outside its defining file; comments, strings and members
blanked):

- pure move (`cd $S/pure/memfn/src && python3 -I $D/tables.py . window_*.c kit_pos.c kit_pick.c
  window.h`): 30 declared, 13 named elsewhere: `ren_check ren_fused ren_search ren_skel ren_stream
  wf_arows wf_atable wf_find_arm wf_floor_arm wf_mtable wf_spanrows wf_srows wf_ties`;
- tip (same command in `$S/asm`): 30 declared, 2 named elsewhere: `wf_find_arm` (in `wf_agree`,
  `wf_find_prepare`, `wf_plan_bren`, `wf_plan_brow`) and `wf_floor_arm` (in `plan_of`).

The two are ARM OBJECTS (`const arm`), Table E's actions, read by address (`p->arm == &wf_find_arm`
identity tests and the plan's arm field), not tables searched; the rule's "table and the functions
that search it" does not reach them, and an accessor per identity test would be a second mechanism
for one comparison. They are declared in window.h (W13). Rev 1's "11 tables" counted any use; this
is the one population, measured the same way at both ends.

The tables and their homes at the tip (r95 W34 corrections folded in):

| table | home | searchers (function bodies) |
|---|---|---|
| `wf_ties` (TIE) | kit_pick.c | `kit_tie_takes`, `kit_tie_exchanges`, `kit_tie_reseeds` |
| `wf_arows`, `wf_atable` (A) | window_stop.c | `a_ct`, `a_holds`, `wf_a_choose`, `wf_a_path`, `wf_a_is_model` |
| `wf_mrows`, `wf_mtable` (M) | window_margin.c | `m_ct`, `m_holds`, `wf_m_choose` |
| `wf_crows` (C) | window_verify.c | `c_plan` |
| `wf_erows`, `wf_etable` (E) | window_frame.c | `e_ct`/`e_holds`/`e_opt`, `wf_plan_site`, `wf_tables_check` |
| `ren_skel/search/stream/check/fused`, `wf_srows` (S), `wf_support` | window_ren.c | `ren_find`, `table_s`, `wf_ren_pieces`, `wf_ren_check`, `wf_renders`, `wf_stmt_row`, `wf_stream_refusal`, `wf_support_rows`, `wf_arm_pick`, `wf_find_decide`, `wf_legacy_stream` |
| `wf_spanrows`, `wf_spantable` (wfS) | window_span.c | `s_ct/s_holds/s_opt`, `wf_stretches`, `wf_span_render`, `wf_span_define`, `wf_span_check` |
| `wf_wsearch` | window_ask.c (W34: `wsearch_of` is ask's, not find's) | `wsearch_of` |
| `nop_decl_rows`, `wr_members` (MF_TRACE) | window_ask.c | `emit_use_refused`, `wr_first_diff` |
| `wf_param_decl` | window_floor.c | `wf_floor_define` |
| use lists | beside their contracts | their contracts only |
| `use_nothing` | window.h (shared vocabulary, §4.1) | none (data in contracts) |

`wf_rc`'s typedef is frame's text at B and its body text's (W34); both go to window.h (`window.h <-
3559-3573`). presence.c's interface is OUTSIDE this cut (W34): it declares `run_modes[]` (:192, a
first-match table the one-line grep missed) and 9 public names that do not all search it; its own
split under ruling 2 is a later unit, trigger: the next presence.c table row or the kit's stage-2
architecture review's refactor list ([KIT-ARCH-STEP]), whichever comes first.

**STOP RULE check.** No file needs a second mechanism for the interface rule: every searched table
is static in its file at the tip, and the two crossing objects are arms (above). The rule does not
fire.

## 5. The accessors (W19: which are moves)

All in `edits.spec` (the assembler applies them; each block's FROM is found exactly once, R7).
Byte identity is claimed for every one (same values, same order of observable effects); G2 is the
proof, the assembled compile the precondition.

- **O3 the TIE predicates** (kit_pick.c, kit.h). NEW one-line reads: `int kit_tie_exchanges(int r)
  { return wf_ties[r].to == TIE_EXCHANGE; }`, `int kit_tie_reseeds(int r) { return wf_ties[r].to ==
  TIE_RESEED; }`; the enum stays private. Call sites: stop's C-model `if (kit_tie_exchanges(T_CMODEL))`,
  margin's `kit_tie_reseeds(T_MARGIN)`. kit.h's "NOT through it" TIE comment is rewritten. Replaces
  rev 1's A1 `kit_tie_rule`.
- **A2** (window_stop.c). `void wf_a_choose(const mf_art *art, const mf_site *s, int quiet, wf_dec *d,
  unsigned ai)`: a MOVE of decide's Table A walk and choose lines. `const char *wf_a_path(size_t
  arow)` and `int wf_a_is_model(size_t arow)`: NEW one-line reads replacing the expressions
  `wf_arows[..].path` (decide's snprintf) and `wf_arows[..].ct == &ct_a_model` (verify's
  `c_model_holds`, margin's `m_margin_holds`).
- **A3** (window_margin.c). `void wf_m_choose(wf_dec *d, const gate_in *in, const gate_tctx *tc)`: a
  MOVE of Table M's walk and its MARGIN/PARKED branch with `m_pair`. decide keeps `f`, `in` and
  `tc` (r95: `trace_cands` reads `tc`) and passes `&in, &tc`.
- **A4** (window_ren.c). `unsigned wf_legacy_stream(wf_frame_row f)`: `f == E_FUNC ?
  ren_fused[RF_FN].stream : ren_stream[RS_CALLER].k.keys`. NOT a move: it MERGES the 4 read pairs
  of `wf_frame_of` and `wf_agree` into one function; those sites become
  `wstream_of(wf_legacy_stream(E_FUNC/E_STMT))` (lines disappear; HITS moves, §7.2). W11, NOTED: it
  reads the tables by index beside "THE ONE ACCESSOR" `ren_find`, a deviation recorded in its own
  comment (an index read cannot go through `ren_find` and stay byte-identical).
- **O1** (window_ren.c). `const char *wf_ren_pieces(struct wf_plan *w, wf_frame_row f, const
  ren_fused_row *fu, fd_form search)`: a MOVE of `wf_plan_site`'s piece selection (Table S, skeleton,
  and stream/check under `ST_ONE && !fu`), returning Table S's `why`; `wf_plan_site` keeps the
  refusal text and asks `wf_frame_name` itself (pure; order-free). `const char *wf_ren_check(void)`:
  a MOVE of `wf_tables_check`'s `ren_search` and `ren_fused` loops.
- **A5** (window_span.c). `int wf_span_render(wf_rc *rc, kb *t, const struct wf_stretch *st)` and
  `int wf_span_define(wf_rc *rc, const struct wf_stretch *st, mf_sink *out)`: wrappers of the row's
  `render`/`define` calls; each ADDS return propagation at its caller (`if (wf_span_render(..))
  return -1;`). `const char *wf_span_check(void)`: a MOVE of wfS's part of `wf_tables_check` (:2587-2595
  at B: the two loops and the last-row check, including `render == wf_span_v`).
- After O1 + A5, `wf_tables_check` (frame) is the E loop, then `wf_span_check()`, then
  `wf_ren_check()`: B's order (E, wfS, ren_search, ren_fused) kept.
- `wf_plan_bren` stays in plan (W15: `wf_plan_frame` also reads `w->skel->k.id`, so moving it buys
  nothing; the row types are complete in window.h anyway).

## 6. The primitives (H2, H3), the leaf and the cycles

1. **H3, the set family** (`kit_pos.c`, kit.h prototypes, one copy, C15 sees it). Names:
   `kit_pos_in count shape two full first`, with the existing `kit_pos_class_of` and
   `kit_pos_spelled`. W10: "only one" is spelled `kit_pos_count(s) == 1`, one spelling everywhere;
   rev 1's `kit_pos_class_of(..) == KIT_POS_ONE` claim is withdrawn. `kit_pos_first(s)` (least
   member, or -1) is born for U2b's callers.
   **U2b, inside the unit (O6), widened per W12** (each copy deleted, its callers re-spelled):
   finder.c `popcount256` (its count, and :940's first-member loop -> `kit_pos_first`, `kit_pos_in`);
   ofsskip.c `set_count`/`set_first`; precheck.c `only_byte`/`single_byte`'s reads; presence.c
   `set_first_member` and `one_member` (callers -> `kit_pos_count(X) == 1`); compose.c's two counts,
   `part_is_byte`'s membership and `span_byte`; pffind.c `set_size` (count + first member);
   generic.c `kit_set_test` (:110-111, membership); `kit_mass`'s own open read. Kept byte for byte:
   S452's anchor (finder.c `if (m == 1)`) and S804's (precheck.c `return n == 1;`). Excluded by R-1,
   named: `formhash.c:493`, `k1_ref.c`.
2. **H2, the final file(s)** (W2). The two-file reading, for main to confirm: D204's "their final
   file" is read as one file PER QUESTION FAMILY, because ruling 2 puts a table with its searchers
   and nothing else:
   - `kit_pos.c` = the position questions: the set family, `kit_run_member` and `kit_mass` (the
     final file that takes `kit_mass`, so presence.c and the planner both call DOWN into it);
   - `kit_pick.c` = the TIE table and its searchers only (`kit_pick_takes` and the predicates
     public, `kit_tie_takes` static).
   Placed by rule: `kit_tie_member_key` -> presence.c, static (its one caller, `member_key`; S1094
   re-points there); `sets_at` stays family-private in verify (all its callers are family files,
   so no kit.h name; not renamed: S3006 needs no re-spell); `kit_run_set`, `kit_run_at`,
   `kit_wspan_at` stay in presence.c (readers of presence's span records, which presence.c owns;
   [SP1D-KITSPLIT-SEAMS]'s seam fact for `kit_run_set` stays as written); `meet_at` stays stop's
   (static, Table A's callback). If main reads "final file" as ONE file, the cost is the TIE table
   sharing a file with non-searchers (`kit_mass`, the set family): ruling 2 against D204's word,
   main's to weigh.
3. **W9, the general form.** `kit_<family>.c` is the general form for a kit-wide question family
   that more than one kit area asks: `kit_pos.c`, `kit_pick.c`, `kit_kb.c`. Unlocks: [SP1D-ARGMIN]'s
   argmin goes to `kit_pick.c` on its own trigger (its next argmin site); a new position question
   (NEON V's lane masks, if they need a set query) joins `kit_pos.c`.
4. **W4, ARV-7's order.** C0b moves ARV-7's text-buffer leaf (`kit_kb.c <- compose.c 27-115`, B-s3)
   before the split, so the plan rows' "ARV-7 before or with it" holds. Effect, measured on the
   assembled tip: `kit_kb.c` is in no cycle (`python3 -I $D/kitgraph.py $S/asm/memfn/src <tip spec>`
   prints one SCC of 24 files that does not contain `kit_kb.c`); the remaining full-kit SCC runs
   through compose.c's services (`kit_walk`, `fd_find`, ...), which is H8's layer-order register row
   and not this unit.
5. **W5, the cycles exactly.** With every kit file but the family and presence.c dropped
   (`DROP=<the 17 others> python3 -I $D/kitgraph.py $S/asm/memfn/src <tip spec>`): no CYCLE. The
   family and presence.c form a DAG; the presence <-> window pair edge is gone. With compose.c and
   gate.c dropped instead, one SCC of 15 remains (CENSUS, same run): its loops are presence.c <->
   finder.c (`fd_pres_run` / `kit_pres_*`, a B-era pair outside the family) and finder.c <->
   window_ren.c (`wf_renders` / `fd_find`). The second is the H1 OUTCOME, not ARV-7's: `wf_renders`
   is `ren_search`'s searcher, so ruling 2 puts it in ren, and `fd_find` is T-FIND's one walk, which
   `wf_find_decide` asks; the arch note's A8 gives finder <-> frame to H1. Reason it stays: breaking
   it needs `fd_find` to take the renderable set as a stated fact rather than asking for it, a
   behaviour change outside a move unit. Trigger: the first unit that changes T-FIND's asker
   interface (the plan_frame line's successor), or H8's layer-order row, whichever lands first.
6. **W6, H8's placement half.** `mf_pres_ports` (memfn.h; presence.c :252) stays in presence.c: it is
   presence's pure query over the presence spans, read by pcrec's trace build; presence.c's split
   is the later unit of §4.4. `mf_wdecide` is window_ask.c's; `wf_check` window_check.c's.

## 7. The binding checks that move

`binders.py ROOT TREE [RUNNERS_ROOT] [--compile]` is the re-aim table: for every binder that quotes
text in a file the unit changes, where that text is in TREE (OK file, STALE, AMBIGUOUS), after the
unit's own re-spellings (its RENAMES/LITERAL table, `OK*`), and with `--compile` whether the
binder's AFTER/TO compiles in its new file. Its control is B itself: run with TREE = ROOT it must
find every binder in its present file.

Results (CENSUS; `$S/binders_*.txt`):

| population | rows | at B (TREE = B, runners of B) | tip (runners of B) | tip (runners of lane/memfn-plantcheck 8bd727eab) |
|---|---|---|---|---|
| mech sites (SAB_BEFORE, SAB_BEFORE2) | 187 in 177 files | 187 OK | 187 OK (3 `OK*`) | 187 OK |
| G2 plants (run_g2_win, run_g2_pres, run_proof) | 75 | 71 OK, 4 STALE | 71 OK (5 `OK*`), 4 STALE | 75 OK |
| purity `old` texts | 49 (of 53 rows; 4 are `-`) | 49 OK | 49 OK (1 `OK*`) | 49 OK |
| decider census rows (window/presence/compose.c) | 57 | 57 OK | 57 OK | 57 OK |

The 4 STALE are S1423, S3092 (window.c) and S3064, S1224 (compose.c): stale AT B, so the split
inherits them; lane/memfn-plantcheck re-aims all four (FUW-12), which is C0. Re-keyed by the split
(moved to a new file): mech 59 sites in 58 files (window.c; S1094 among them, to presence.c); G2 41; purity 49; census 50.
`run_wreply.sh`'s plants name only `src/gen/emit_dfa.c` (CENSUS: `grep -n '@@'`), none in the unit.

### 7.1 Mech sabotage rows

By new file (`binders_tip_cc.txt`, the moved window.c sites): ask 16, span 9, parts 7, vform 6,
text 4, legacy 3, verify 2, ren 2, find 2, and 1 each stop, margin, efind, decide, check, kit_pos,
window.h (S3285), presence.c (S1094). S3285's anchor (`WF_SPAN_HEAD`) is in window.h: a header
sabotage builds into every includer; probed: planted, all 19 family files compile (§11). [SABANCHOR]
(`scripts/m6read_check_sab_anchors.py`) is the per-commit check of SAB_FILE.

### 7.2 Decider census (W23)

Per-commit edits of `tests/memfn/decider_census.tsv` and the pins in `decider_census.py`, counted
from the assembled tip (the tip map is `python3 -I $D/rekey.py . $S/binders_tip_cc.txt`, run
`decider_census.py --root . --src $S/asm/memfn/src --map MAP --no-plants` with the pins below:
97 checks passed, 0 failed; with B's pins it fails exactly the two pin checks):

| commit | map edit | MEMBER_COUNT | HITS (where the backstop lines go) |
|---|---|---|---|
| B | - | 72 | 68 |
| U3 | `kit_tie_exchanges`, `kit_tie_reseeds` rows added; kit.h's `kit_tie_takes` prototype row deleted (O3 makes it static); `kit_tie_member_key` re-keyed presence.c; TIE rows re-keyed kit_pick.c | 73 | 66 (O3: kit.h -2, stop -1, margin -1, kit_pick +2) |
| U5 | rows for `wf_a_choose`, `wf_m_choose`, `wf_legacy_stream`, `wf_ren_pieces` (fn) and `wf_ren_check` (excluded) | 78 | 62 (A2/A3 0: decide -2, stop +1, margin +1; A4 -3: ask -4, ren +1; O1+A5 -1: frame -7, ren +6) |
| each peel | its rows re-keyed to its file | unchanged | unchanged |

The HITS deltas are per edit block (`edits.spec`'s FROM vs TO lines holding a BACKSTOP shape;
sum -6 = 62 - 68, CENSUS). `RUN_CALLERS` names functions, unchanged (the tip run's D section holds).
F2 (rev 1): the census's self-check plants name window.c by text and append to it; at the tip they
fail with FileNotFoundError (measured), so U1 re-aims them by content to the file holding the text.

### 7.3 G2 plants (W22)

How the build reads plants at the tip: each plant is `FILE@@FROM@@TO` under the runner's dialect,
FILE a path under the copied `memfn/src`. On lane/memfn-plantcheck the runners apply through ONE
applier, `tests/lib/plants.py` (`apply`/`check`; statuses OK/STALE/AMBIGUOUS/MISSING FILE/NO
SPEC/ORPHAN), whose FILE is any name (no window.c in its code), and `--plant-check` counts without
building. So at the tip a plant keyed `window_margin.c@@...` is read the same way as today's
`window.c@@...`; rev 1's `plants.py` (this directory's, window.c/presence.c regex) is superseded by
`binders.py` for the design and by the branch's applier for the build.

Dependency, stated: **the build depends on lane/memfn-plantcheck landing first** (C0). Without it,
(a) 4 plants are stale at B and one stale plant ends a `--plants` run, (b) there is no per-commit
static plant check: the runners' private heredocs apply only in `--plant`/`--plants` modes, which no
gate runs. With it, G1 runs each runner's `--plant-check` per commit (seconds) and
[SABANCHOR]'s plant pass (its floor 81) counts through the same applier. The executing gate is G3's
three `--plants` runs at the tip (a box job, §8.3).

Re-spelled plants (`OK*`, the FROM changes): S1402 (O3), S1405, S1428, S3106 (H3), S1410 (H3
`full`). TO-only: S1427 (its TO calls `count`: re-spelled `kit_pos_count`; unre-spelled it FAILS to
compile in window_find.c, measured in an earlier probe run, the fail direction of §7.5).

### 7.4 Purity (W24)

`run_purity_reach.sh` reads `window.c` for its population and inserts the NEVER functions before
`wf_arows[]`. U1, on the unsplit tree: the population greps the FAMILY LIST (`window*.c kit_pick.c
kit_pos.c`) with "exactly once across the list"; each row's plant and NEVER insertion go into the
file that holds the row's `old` text (tip homes, `binders.py`: ren 26, verify 12, stop 4, frame 4,
margin 3), and the link line excludes THAT file's object, not `window.o`. The NEVER functions
include window.h. `purity_rows.tsv` row MARGIN is re-spelled by O3. `run_finder.sh`'s
`purity_plant` (rows a-mass and m-parked) is re-aimed by content in U1 (`make test-memfn-finder`
runs it, G1).

### 7.5 Re-spell lists and the AFTER/TO compile probe (W25, W26)

The re-spell lists, derived (not hand-listed) by `binders.py`'s table (H3's renames; O3's and A2's
expressions):

- mech: S1417 (O3; SAB_BEFORE and SAB_AFTER), S3106, S3525 (H3);
- G2: S1402, S1405, S1410, S1428, S3106, and S1427 TO-only (§7.3);
- purity: MARGIN (O3).
- Not re-spelled, checked: S3006 (`sets_at` is not renamed), S452 and S804 (U2b keeps both anchor
  lines byte for byte), S3250 (calls `reply_of`, in window.h).

W26's correction: a non-compiling sabotage is a loud BUILD-FAILED anomaly in mech, not a kill; the
real gap is that nothing compiles a re-pointed AFTER before the next full mech run. The probe
(`binders.py . $S/asm <plantcheck runners> --compile`): each SAB_AFTER (with the row's other site
when both are in one file) and each plant's TO set (all edits of one plant label together) applied
to its NEW file alone and `gcc-16 -fsyntax-only`-ed: mech 186 PASS + 1 header (S3285, probed through
its 19 includers: 19 PASS); G2 75 PASS. At B: the same, all PASS (control of the probe's setup; its
fail direction is S1427 above).

### 7.6 The rest

- **rows_check.py** plants S2983/S2988 (frame at B): their text is in `window_ren.c` / `window_frame.c`
  at the tip; re-aimed by content in the peel that moves it.
- **C15/C16, PROVENANCE.** `run_link_checks.sh` (`make test-memfn-link`): every new external symbol
  `pcrec_mf_*`; every new file's SPDX and Provenance lines (assembler R5 writes them). PROVENANCE row
  54 (window.c: A-model/C-model transcribe `prefix_k`) splits into window_stop.c's and
  window_verify.c's rows (`files.spec`'s `prov` lines), the rest "kit original"; row 53 (presence.c)
  notes `kit_mass`'s move; compose.c's row notes `kit_kb.c`.
- **Makefile.** KITHDRS gains `memfn/src/window.h`; `KITSRCS` is a wildcard; no Makefile line names
  window.c (`grep -n 'window\.c' Makefile`: 0).

### 7.7 File-name readers (W30)

Not binding (re-read, re-worded in the commit that moves the text they describe): `git grep -l
'window\.c' -- tests memfn scripts Makefile`, outside `tests/mech/sabotages/`: 50 files (CENSUS of
that spelling; a reader spelling it differently is missed, so a FLOOR of readers). They include r95's
six (run_decide_check.c's comments, run_pres_picks.sh, tests/memfn/CLAUDE.md, memfn/tests/NOTES.md,
kit.h/memfn.h/.def comments), `scripts/gestalt` and `scripts/statusline.sh`.

## 8. Commit order and gates

### 8.1 Order (W20)

Every commit is byte-identical to the base and green on its own.

- **C0 (outside the unit):** lane/memfn-plantcheck lands (FUW-12: S1423, S3092, S1224, S3064
  re-aimed; the one applier; `--plant-check`).
- **C0b:** ARV-7's leaf, `kit_kb.c <- compose.c 27-115` (W4).
- **U1 checks first, on the unsplit tree:** purity's family list and per-file insertion (W24),
  `purity_plant`, decider census self-plants by content (F2). Green at B with the list {window.c}.
- **U2 ARV-5:** `kit_pos.c` born with the set family and `kit_pos_first`; window.c's callers
  re-spelled (S3106, S3525; plants S1405, S1410, S1427, S1428, S3106). **U2b:** the other files'
  copies (§6.1).
- **U3 ARV-16:** `kit_pos.c` takes `kit_run_member` and `kit_mass`; `kit_pick.c` born (TIE + O3);
  `kit_tie_member_key` to presence.c (S1094; S1417, S1402, purity MARGIN re-spelled; census U3 row).
- **U4 window.h born:** the shared types and the vocabulary (W3), `#include`d by window.c; KITHDRS;
  C16; the two arms' declarations leave kit.h, `wf_part_site` static (W13).
- **U5 the accessors in place** (A2, A3, A4, O1, A5), still in one file; census U5 row.
- **U6..U23, the peel, 18 commits, one file each, emitter end first:** vform, find, floor, test,
  text, span, efind, ren, frame, legacy, parts, ask, plan, check, cands, verify, margin, stop. Each
  moves its ranges, drops `static` from the names that cross IN EITHER DIRECTION between the new
  file and the remainder and declares them in window.h, deletes the moved names' forward
  declarations (R4), and re-points its own mech rows, census rows, plants, rows_check plants and
  PROVENANCE row. U23 (stop) also replaces window.c's head with window_decide.c's prologue.
- **U24:** `git mv memfn/src/window.c memfn/src/window_decide.c`, no content change (a 100 %
  rename, so `git log --follow` keeps the decider's history; W20's threshold problem is avoided by
  not mixing the rename with a peel).

19 family `.c` files + window.h = 20 new family files; with kit_pos.c, kit_pick.c, kit_kb.c, 23.

### 8.2 Gates

- **G1, per commit** (W21, W27): `make CC=gcc-16 strict test-memfn-rows test-memfn-finder
  test-memfn-link` on the Mac (`CC=gcc-16` spelled: bare gcc there is Apple clang); [SABANCHOR];
  decider_census.py; run_purity_reach.sh; each runner's `--plant-check` (C0); `syncheck.sh` over the
  commit's tree (the strict flags plus `-Wmissing-prototypes`, and a `-DMF_TRACE` pass strict never
  compiles; write-free) and `unused.py` over the family (syntax-only does not report an unused
  static); `binders.py --compile` (the W26 probe; seconds).
- **G2, byte identity per commit:** `scripts/emit_sweep.py --ref <the unit's base> --tree-rev
  <commit>` (W28: `--ref` the base the unit is cut from, not T), three arms: default;
  `--extra=-fmemfn-simd=x86-64` (vrun@w16); and `--extra=-fmemfn-simd=x86-64-v3 --no-differ-floor`,
  which renders the V form's w32 level block (window_vform.c, B :4459-4468, mech S3535's code).
  The third arm's reach floor: the count of corpus patterns whose emitted text holds the w32 level
  stamp at the base, measured by the gate's first run on the base and pinned; a commit's run below
  it is red. **Where it runs (W28):** emit_sweep emits text only, and an explicit-family arm reads
  the same on every host ([XARCH-DEV] U3: "the cells read the same on every host"), so all three
  arms run on this aarch64 Mac; nothing in G2 is owed on Linux. Compiling or RUNNING the emitted
  x86-64-v3 code is G3's and is Linux's.
- **G3, at the tip:** `memfn/tests/run_g2.sh` (with and without `-fmemfn-simd`), `run_g2_win.sh`,
  `run_g2_pres.sh`, `tests/memfn/run_proof.sh`, each also `--plants` (the gate that EXECUTES the
  re-aimed plants, W22), and `memfn/tests/g2_vspan.py`.
- **G4, symbols at the tip:** `run_link_checks.sh` (C15, C16) and `nm -g build/libpcrec.a` diffed
  against the base's: the additions are exactly the new kit.h/window.h names under `pcrec_mf_`.
- **G5:** REACH_ONLY mech over the re-pointed rows, then `make test` at the tip.
- **G6:** `-fstack-usage` (run_link_checks.sh's recipe) at the base AND the tip: no frame over 4 KB,
  and every frame that grew past 3 KB from its base value named in the delivery. The base run is
  owed (W29: rev 1 had no baseline; this lane runs no compile).
- **G7, stamps unchanged:** `MF_SITE_ABI`, `MF_CLASS_V`, `MF_VOCAB`, pcrec's abi, the
  `_MEMFN_FORMS`/`_MEMFN_LIBC` stamps (`make test-memfn-stamps`).

### 8.3 By box (W29)

| gate | the Mac (aarch64, gcc-16; the Mac suite lock, not boxqueue) | Linux (x86, boxqueue) |
|---|---|---|
| G1 | yes, every commit | yes |
| G2 | yes, all three arms (text only) | yes |
| G3 | `run_g2*.sh`, `run_proof.sh` and their `--plants` at ONE SIMD layer only (the host renders no x86 SIMD row); `g2_vspan.py` is red by construction here and is NOT run (a SKIP would read as a pass) | REQUIRED: both layers, `g2_vspan.py` |
| G4, G6, G7 | yes | yes |
| G5 | `make test` yes; mech yes | yes |

`scripts/boxqueue` needs flock and /proc (Linux); on the Mac heavy stages take the Mac suite lock.
The r95 FREEZE NOTE's `targets-check` warning on aarch64 predates the unit and does not touch G2's
explicit-family arms; it is why G3's x86 half is Linux's.

## 9. Anticipated growth: NEON V's places (designs nothing of NEON V)

- The V form's text and its level admission block (B :4459-4468; mech S3535) are `window_vform.c`.
  NEON V's text lands there and nowhere else in the family.
- W14: the block widths `WF_VBLK_MIN/MAX` are in window.h (read by vform's renderer and span's two
  `_Static_assert`s, so neither file owns them); a NEON width is one window.h line, inside Goal 2's
  "at most one header line". D204's binding clause applies here: [IR-FORM]'s "emitter-shaped SIMD
  forms" — NEON V adds a form row, not a new family file.
- ARV-11's per-level C-spelling table (H4) is a `.def` beside `targets_c.def`, compiled into
  `levels.c`: static there, its lookup the only public name (ruling 2); vform and vrun.c call it.

## 10. What the build must not do

- Change a statement, its order or a constant beyond §5's stated accessor shapes; a commit with an
  emit_sweep difference is reverted, not re-pinned.
- Copy a `kit_walk(` or a table read: §7.2's HITS are exact.
- Re-point a binder in a later commit than the one moving its text; leave a binder naming window.c
  after U24; let the census's self-plants create a file.
- Add a name to window.h no other family file uses, or to kit.h no outside file uses — except the
  stated kit-wide vocabulary (§4.3).
- Touch `formhash.c`, `k1_ref.c` (R-1), the layer order's text beyond C0b, or any NEON V row.
- Re-cite docs' `window.c:N` line cites (§13 F6).

## 11. Assembler evidence (r95 lesson 1)

### 11.1 The assembler

`assemble.py ROOT OUT [--pure]` reads `cut.spec`, `files.spec` (titles, provenance), `window_h.in`
(the header template and its `@export`/`@new` list) and `edits.spec` (renames and FROM/TO blocks),
and writes `OUT/memfn/{src,include}` as the tree at the unit's tip, window.c removed. It refuses an
OUT inside the repo's `memfn/src`. Its rules: R1 every source line to exactly one file (a
`window.h <-` item wins over a file range; `-` drops); R2 `ent:NAME` takes the entity and its
comment; R3 an `@export` loses `static` and window.h gets `#define N MF_NS(N)` plus a declaration
cut from the definition (a function's head to its body's `{`, `;`; an object `extern` + its
declarator); R4 a static forward declaration of an exported name is deleted, one of a non-exported
name moves to its definition's file (W16: e.g. `plan_ix`'s); R5 each file's prologue (SPDX,
Provenance, title, the std includes, kit.h, window.h for window_*); R6 code-token renames (comments
and strings untouched, members skipped); R7 edit blocks, each FROM exactly once. `--pure` skips the
edits and accessors (the controls below).

### 11.2 The compile, every file, both defines

Command: `TMPDIR=$S/tmp python3 -I $D/assemble.py . $S/asm && bash $D/syncheck.sh $S/asm gcc-16`
(gcc-16 = Homebrew GCC 16.2.0). Flags: `-O2 -g -Wall -Wextra -std=gnu11 -Wshadow -Werror
-Wmissing-prototypes -fsyntax-only`, every `OUT/memfn/src/*.c`, plain and `-DMF_TRACE`; then the four
white-box drivers that include kit.h (`tests/memfn/arm_fixtures.c`, `mass_check.c`,
`proven_check.c`, `run_decide_check.c`) with KITFLAGS against the assembled kit.h.

| run | result |
|---|---|
| tip, plain | 39/39 PASS (the 22 new files and the 17 others, edited ones included) |
| tip, `-DMF_TRACE` | 39/39 PASS |
| tip, the 4 drivers | 4/4 PASS |
| **total** | **`syncheck: 82 PASS, 0 FAIL (gcc-16)`** |
| control: B's own tree (`memfn/src` copied) | `40 PASS, 0 FAIL` (18 files x 2 + 4) |
| control: `--pure` (the cut without edits.spec) | `44 PASS, 38 FAIL`: all 19 family files fail, both defines (no guard/include edit, no accessors) |
| `unused.py` over the family + every edited file, tip | 0 UNUSED (B's window.c/presence.c/compose.c: 0) |
| S3285 planted in the tip's window.h | 19/19 family files compile |

Iterations: rev 2's cut reached 82/82 after fixing, in order, an edit FROM that R3 had already
de-`static`ed, single-line ranges, and the unused statics syntax-only does not report (hence
`unused.py`). What the assembly does NOT prove: each intermediate commit's tree (U2-U23) compiles;
that is G1's per commit, with the same `syncheck.sh`.

## 12. Open choices: as ruled (r95 RULING), with numbers

| O | applied | numbers |
|---|---|---|
| O1 frame's grain | SPLIT: `window_frame.c` 277 + `window_ren.c` 415 (rev 1: one 737-line file) | pure move 86 statics / 40 types (family census, §4.2); r95's {frame, ren} SCC through `wf_erows` in `wf_tables_check` removed by A5's per-table form (`wf_span_check`, `wf_ren_check`): frame -> ren 3 calls (`wf_find_decide`, `wf_ren_pieces`, `wf_ren_check`), ren -> frame 0 (`kitgraph.py`, tip) |
| O2 planner's grain | separate: stop 254, margin 98, verify 314, decide 135 | A2's 3 + A3's 1 names |
| O3 TIE's shape | two predicates, enum private | kit.h +2 -2 |
| O4 the name window.c | no file keeps it; U24 renames the remainder | r95 W31: keeping it saves at most 24 of ~150 binders; rev 1's "halves" withdrawn |
| O5 MARGIN | own file, 98 lines | A3 |
| O6 U2b | inside, widened (§6.1) | 7 other files edited, all compile (§11) |
| O7 find -> frame names | kept: they are row payload (actions); find's FAMILY names 16 | - |

## 13. Findings and records

- F1 (W35) `memfn/src/CLAUDE.md` is 12,277 B against 12,288: the file list for 22 files moves
  window.c's detail to `memfn/NOTES.md` (there is no notes file in memfn/src: C16), in U4.
- F2 decider census self-plants (§7.2).
- F3 four stale plants at B (S1423, S3092, S1224, S3064): C0.
- F4 (W37) rev 1's "six `struct wf_plan` fields with two writers" rested on an uncommitted
  `fields.py`; withdrawn from this note, the question left for a committed instrument. Rev 1's O1
  numbers from `spec_v4` are replaced by the committed cut (§12). C-39's 10 names: r95 re-derived
  them (HOLDS); not restated.
- F5 the finder loops survive (§6.5).
- F6 819 `window.c:N` cites in 186 files go stale by line (§2), as every refactor's do (H11).
- F7 no `__FILE__`/`__LINE__`/`__func__` in `memfn/src`: no file name can reach an artifact.
- W8 (PLAN, main's): append the D204 pointer to [IR-FORM] member (4). Recorded only.

### 13.1 Instrument blind spots (W32), beside the numbers they touch

- `census.py`/`kitgraph.py` read a macro argument as a use (`WR_M(run_member)`: §4.2's 1 tip
  static) and kitgraph reads locals/params as calls (§2's B SCC may hold false edges; the tip DAG
  claim of §6.5 has no edge to be false about).
- Name counts cannot see type completeness (dereference, `sizeof`), prototypes (blanked) or comment
  boundaries: these are now the assembler's and the compiler's (§11), which is why §4's header is
  derived, not counted.
- `ents.py` takes the first entity's owner per range and drops `typedef enum` enumerators: no tip
  number in this note is an `ents.py` enumerator count except window.h's composition (§4.1).
- `tables.py` blanks members after `.`/`->`, so a table reached only through a struct field is not
  a crossing; at the tip no table is held in a field outside its file (the arms are by address).
- `binders.py`'s compile probe compiles the planted file alone; a header plant is probed through
  its includers by hand (S3285).
