# The window family split: window.c and the position primitives into small files, once

DESIGN rev 2.1, lane wsplitd3, 2026-11-24 (rev 2: lane wsplitd2; rev 1: lane wsplitd; same day).
Not a build go.
Architecture: `memfn/docs/arch_review_2026-11.md` (ACCEPTED rev 4): ARV-9 (the split), ARV-16 (the
primitives' home), ARV-5 (the set family) and ARV-7's text-buffer leaf, as one unit. This note
makes the choices that review left to the design step: §8 H1 (the cut and every section's home),
H2 (the primitives' home), H3 (the set family) and H8's placement half (where the public entries
live).

**Read §R2.1 first, then §R2.** Rev 2.1 answers review r98
(`docs/dev/reviews/2026-11-24-r98-memfn-winsplit2.md`), every FIX-NOW (R1-R13) and DOC (R14-R26)
item, under its RULING: every gate arm's BASE run is green on the box it is listed for (§8.4 holds
the runs), binders.py's per-commit population keeps each peel's rows with a floor (drilled, §7.8),
and `kit_run_set`/`kit_run_at` move to kit_pos.c (R13, the kit manager's choice). Rev 2 answers review r95 (`docs/dev/reviews/2026-11-24-r95-memfn-winsplit.md`)
item by item, applies its RULING (O1-O7 as recommended) and carries the round's lesson 1: the cut is
no longer a name census only, it is ASSEMBLED into the actual files by a committed assembler and
every assembled file is compiled (`gcc-16 -fsyntax-only`, with and without `MF_TRACE`), §11.

**Base.** B = `a0742283a` (lane/memfn-wsplit). Its code equals rev 1's T `a0f13ad83`
(`git diff --stat a0f13ad83 a0742283a -- memfn/src memfn/include tests memfn/tests Makefile`: empty),
so every `window.c:N` cite below reads the same at both. [rev2.1] Rev 2.1's runs are at B' =
`79388197d` (the branch tip this lane was cut from), whose code equals B (`git diff --stat
a0742283a 79388197d -- memfn/src memfn/include tests memfn/tests Makefile scripts`: empty); the
gate base runs (§8.4) are on a `git archive` of B' built with gcc-16 on the Mac, with
lane/memfn-plantcheck's runners (C0, `838deefe2`, tests/scripts code-equal to the design's cite
`8bd727eab`) overlaid where a gate needs them. Commands run from the repo root at B, with
`D=docs/design/memfn/window_split`, `W=memfn/src`, and `S=$PCREC_TMPDIR/scratch/<lane>` the scratch
dir the assembler writes (`S/asm`, never `memfn/src`).

**Numbers convention.** Every count names its command and says CENSUS (the whole population, exact)
or FLOOR. The instruments are committed in `window_split/` (own CLAUDE.md).

## §R2.1 — what rev 2.1 changes, by review id (r98)

| r98 id | disposition | where |
|---|---|---|
| R1 G1's `make strict` red on the Mac | FIXED: on the Mac G1 = `syncheck.sh` (the strict compile) + `make CC=gcc-16 test-memfn-rows test-memfn-finder test-memfn-link` as their own command; `make strict` is Linux's; every arm's base run green, recorded | §8.2, §8.3, §8.4 |
| R2 G3's Mac row, plant split by box | FIXED: Mac G3 = `run_g2_win.sh --plants`, `run_proof.sh` + `--plants`, `run_g2.sh --quick`; run_g2_pres's 7 plants, g2_vspan and the g2v/simdfloor mech rows are Linux's, named; the non-existent run_g2.sh modes dropped | §8.2, §8.3 |
| R3 binders.py's per-commit population | FIXED (instrument): population = B's eight files + every file the unit creates; floors 187/75/49/67/4; CC from the environment; DRILLED | §7, §7.8 |
| R4 U24 is not content-free | FIXED: U24 = the `git mv` + S3252, census `decide`, PROVENANCE row, CLAUDE.md entry | §8.1 |
| R5 U3's short list | FIXED: every unit's re-point list derived by `repoint.py` from binders.py; U3's 10 rows listed | §8.1 |
| R6 U4: head comment, S3285 | FIXED | §8.1 |
| R7 U1's purity anchor | FIXED: the anchor per commit range; the include clause dropped | §7.4 |
| R8 census APPEND plants | FIXED: the append target found by content, asserted present; rev 1's sentence restored | §7.2 |
| R9 F1 too late | FIXED: F1 in C0b | §8.1, §13 |
| R10 PROVENANCE row per new file | FIXED | §7.6 |
| R11 G2 arm 3's reach floor | FIXED: `w32reach.py`, floors from its base run | §8.2, §8.4 |
| R12 G4 removals, G7 readers | FIXED: G4 +82 / -3 by name; G7's readers named | §8.2 |
| R13 `kit_run_set` | MOVED (ruled): `kit_run_set`, `kit_run_at` to kit_pos.c at U3; `kit_wspan_at` stays | §3, §6.2, cut.spec |
| R14 §10 forbids U2b | FIXED | §10 |
| R15 rows_check plants | DOC + instrument: both window_ren.c, U13; binders.py counts them | §7.6 |
| R16 cites | DOC | §3, §4.4, §6.1, §6.6 |
| R17 reader census | DOC: strict regex, 48; compose.c/presence.c populations; 0 binders in the moved compose/presence text | §7.7 |
| R18 kit.h exception's reason | DOC | §4.3 |
| R19 Goal 1's crossing objects | DOC: 4 objects, all Table E payload; tables.py's initializer blind spot | §1, §4.4, §13.1 |
| R20 A5 wording | DOC | §5 |
| R21 O1's cause | DOC | §R2 W1, §12 |
| R22 ARV-7's other half | DOC + PLAN (main's) | §1, §6.4, §13 |
| R23 kitgraph's spec | DOC: the empty spec spelled; blind spot stated | §6.4, §6.5, §13.1 |
| R24 presence <-> compose | DOC | §1, §6.5 |
| R25 S1427's two re-spells | DOC | §7.3, §7.5 |
| R26 ren_find's comment | FIXED in edits.spec (the comment names its two exceptions) | §5 A4 |

## §R2 — what rev 2 changes, by review id

| r95 id | disposition | where |
|---|---|---|
| W1 frame's grain (O1) | APPLIED: frame / ren split; the {frame, ren} SCC goes with the CUT (`wf_tables_check` homed in frame; [rev2.1] R21: the pure move already has no file cycle), and O1 + A5's per-table checks remove table crossings (13 -> 2) | §3, §5 O1, §12 |
| W2 kit_pick.c's names | FIXED: two-file reading (CONFIRMED by the kit manager); `kit_mass`, `kit_run_member` to kit_pos.c; `sets_at` family-private; [rev2.1] `kit_run_set`, `kit_run_at` to kit_pos.c (r98 R13) | §6.2 |
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
(§12); W8 PLAN (main's), W11 NOTED. The two-file reading of §6.2 is CONFIRMED by the kit manager.

Review r98's RULING (kit manager, rev 2.1): every FIX-NOW (R1-R13) and DOC (R14-R26) item; R1/R2's
rule (every gate arm's base run GREEN on its listed box before it is used; the Mac runs the strict
compile through syncheck.sh and the named make targets as their own command, `make strict` is
Linux's; §8.3 names what runs where, plant by plant); R3's binders.py fix drilled with one re-keyed
broken AFTER; R13: `kit_run_set` and `kit_run_at` MOVE to kit_pos.c within the two-file reading
(D204 moves the primitives ONCE, so no second move is owed), `kit_wspan_at` stays with presence;
plan.md line cites rewritten to tags (PL14). The re-check after rev 2.1 is LIGHT (§8 at the base on
the Mac, and R3's drill). No build go: the owner gives it after that re-check.

## 1. GOALS

Ranked; each measurable.

1. **One table, one file, and only the searchers public** (ruling 2). Measure: `tables.py` (W36's
   one population: every file-scope table or object of the family, and every family function body
   that names one outside the file defining it). At the pure move (`assemble.py --pure`) 13 of 30
   are named in another file's function bodies; at the tip 2: `wf_find_arm` and `wf_floor_arm`, the
   arm objects, which are not searched tables (§4.4). [rev2.1] R19: with the two contracts
   `wf_find_ct`/`wf_floor_ct`, which Table E's INITIALIZER names (a population tables.py does not
   count, §13.1), 4 objects cross, all Table E row payload (2 arms, 2 contracts), 0 searched tables.
   Comparison: tip <= 2 by tables.py, each named, and the 4 by name.
2. **Split once, final grain** (ruling 1). 22 new `.c` files of 81-428 lines and the private header
   `window.h` (561 lines) replace window.c (4,672), take `kit_mass`, `kit_run_member`, [rev2.1]
   `kit_run_set` and `kit_run_at`, and take compose.c's text buffer (C0b). Measure: R-48's diff (NEON V) touches no family file except
   `window_vform.c`, plus at most one line of `window.h` (§9).
3. **Answer- and byte-identical at every commit.** Measure: §8's gates per commit against the
   unit's base.
4. **No file cycle inside the family, and presence.c calls down only INTO THE FAMILY.** Measure:
   `kitgraph.py` over the assembled tip (EMPTY spec, §6.5) with every kit file but the family and
   presence.c dropped prints no CYCLE (§6.5; held at the tip). [rev2.1] R24: outside the family
   presence.c still has two B-era pair loops, presence.c <-> finder.c and presence.c <-> compose.c
   (`kit_presence_check` / `kit_pres_run`), named in §6.5, not this unit's.
5. **Every binding check still binds, re-aimed in the commit that moves its text.** Measure:
   `binders.py` over the assembled tip finds every binder's text exactly once (mech 187 sites,
   G2 75 plants, purity 49, census 67 (57 of window/presence/compose.c, rev 2's population, + 10 of
   finder/generic/ofsskip.c, [rev2.1]), rows_check 4 edits; all OK, §7), and every re-pointed
   SAB_AFTER and plant TO compiles in its new file (§7.5); per commit the same populations, never
   below their floors (§7.8).

Non-goals: no behaviour change; no new form; no NEON V design (§9 places it); `formhash.c`/
`k1_ref.c` untouched (R-1); the layer order's TEXT (ARV-7/H8's other half, [rev2.1] R22: the
register row ARV-7 files) untouched beyond C0b's leaf;
no re-cite of docs' `window.c:N` cites (§13 F6).

The three standing questions (docs/design/CLAUDE.md):

- (1) Measurement regime: none applies. Compile-time moves only; byte identity of every emitted
  artifact is the speed proof. The one quantity the split can move is the kit's own stack frames
  (cross-file calls stop inlining): measured by G6, which owes a base run (§8.2).
- (2) Independent control: `scripts/emit_sweep.py` compares the base binary's emitted bytes with
  each commit's over the corpus, a source the split does not touch; G2/G3 check the family against
  `k1_ref.c`, outside the family (R-1). The assembler's compile evidence has its own control: the
  same files assembled WITHOUT the edits fail (38 of 82, §11.2), and B's own tree passes (40/40).
  [rev2.1] Every gate's own control is its BASE run on its listed box, green (§8.4), and binders.py's
  per-commit selection has a drilled fail direction (§7.8).
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
contract comment); [rev2.1] R13: `kit_run_set` takes presence.c :84-91 and `kit_run_at` :112-118
(each with its leading blank line; kit_run_at's comment). `window.h <-` lines name the text the
header takes (types, the family's vocabulary, the family comment). `-` lines are window.c lines
no new file keeps as they stand: the SPDX/Provenance/title head :1-7 and the includes :66-71
(each new file's prologue replaces them, R5), and [rev2.1] R16: :132-139, `kit_tie_member_key`
and its comment, which is NOT deleted: an edits.spec block re-places it verbatim in presence.c as
a static beside `member_key`, its one caller (§6.2); the TIE comment O3 rewrites is kit.h's.
Every window.c line is homed exactly once (assembler rule R1, §11.1; `window.c` keeps 0 lines).

Tip numbers: `python3 -I $D/assemble.py . $S/asm` prints each file's lines and exports; PUBLIC =
names in kit.h or memfn.h (CENSUS of the `#define X MF_NS(..)` lines naming a definition of the
file); FAMILY = names in window.h; STATIC = file-static functions/tables/objects.

| file | from (B) | lines | PUBLIC | FAMILY | STATIC | holds |
|---|---|---|---|---|---|---|
| `kit_pos.c` | window.c :231-284, :937-962; presence.c :56-91, :112-118 | 143 | 12 | 0 | 0 | the position questions: the set family (`kit_pos_in count shape two full first class_of spelled`), `kit_run_member`, `kit_mass`, [rev2.1] `kit_run_set`, `kit_run_at` |
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
| `window_ren.c` | :2193-2563, :2607-2648, :2877-2887 | 418 | 5 | 5 | 16 | THE TRIPLE: the renderer tables with `ren_find`, Table S, the support table, `wf_renders`, `wf_arm_pick`, `wf_find_decide`; O1's two, A4 |
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

Sums (CENSUS from the table): 22 new `.c` files; PUBLIC 44 names (of which new to kit.h: the 6 set
family names and the 2 TIE predicates, §4.3; `kit_run_set`/`kit_run_at` keep their kit.h names,
moved with their definitions); FAMILY 76. Lines 81-428; 4,763 lines in the 22 files (each file's
new prologue included, R5; rev 2: 4,745, + 15 for R13's two functions, + 3 for R26's comment in
ren; `assemble.py` at B', rev 2.1's specs). presence.c keeps 334 lines at the tip. No file keeps
the name `window.c` (O4).

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

kit.h keeps only names with a caller outside the family, plus ONE stated exception, [rev2.1] R18
with its reasons as they hold name by name (callers at the assembled tip, `grep -l -w NAME
$S/asm/memfn/src/*.c`): `kit_pos_in`, `kit_pos_count`, `kit_pos_first` HAVE non-family callers (U2b
makes them so: compose, finder, ofsskip, precheck, presence, pffind, generic); `kit_pos_shape`,
`kit_pos_two`, `kit_pos_full` are family-only today and are kit.h's by H3's one-family-one-header
choice (the set family is declared once, beside `kit_pos_class_of`/`kit_pos_spelled`, which C15
sees); the TIE predicates `kit_tie_exchanges`/`kit_tie_reseeds` are family-only (stop, margin), and
are kit.h's for a structural reason: they are defined in `kit_pick.c`, which is not a family file
and includes kit.h only, so window.h cannot carry them without kit_pick.c joining the family's
header (which would make the TIE table's file depend on the window family it serves). Changes (CENSUS: `diff` of the sorted `#define X MF_NS` names, B vs tip):
+6 (`kit_pos_in count shape two full first`), +2 (`kit_tie_exchanges`, `kit_tie_reseeds`), -2
(`kit_tie_takes`, now static; `kit_tie_member_key`, moved static to presence.c beside `member_key`,
its one caller), -3 (`wf_find_arm`, `wf_floor_arm` to window.h: no non-family file names them;
`wf_part_site` static in parts). `wf_support_rows` stays (test caller `arm_fixtures.c`). 134 -> 137
names (`grep -c -E '^#define +[A-Za-z_0-9]+ +MF_NS\('` of kit.h at B' and in `$S/asm`; R13 moves no
kit.h name).

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
is the one population, measured the same way at both ends. [rev2.1] R19: two more objects cross
that tables.py cannot see, `wf_find_ct` and `wf_floor_ct` (the E-find and floor contracts, B
window.c :1865's forward declaration, defined in find/floor, `@export`ed in window_h.in): Table E's
INITIALIZER in frame names them, and tables.py counts function bodies only (§13.1). Same kind as
the arms (Table E's row payload, O7's reading), so the rule does not reach them either: 4 objects
cross, all Table E payload, 0 searched tables.

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
3559-3573`). presence.c's interface is OUTSIDE this cut (W34): it declares `run_modes[]` (B :223,
[rev2.1] R16: rev 2's :192 was the assembled tip's line; a first-match table the one-line grep
missed) and 9 public names that do not all search it; its own
split under ruling 2 is a later unit, trigger: the next presence.c table row or the kit's stage-2
architecture review's refactor list ([KIT-ARCH-STEP]), whichever comes first.

**STOP RULE check.** No file needs a second mechanism for the interface rule: every searched table
is static in its file at the tip, and the four crossing objects are Table E payload (above). The
rule does not fire.

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
  comment (an index read cannot go through `ren_find` and stay byte-identical). [rev2.1] R26:
  `ren_find`'s own comment is corrected too (edits.spec `@@ window_ren.c A4 (r98 R26)`): it names
  its two stated exceptions, `wf_legacy_stream` (one named row by index) and `wf_arm_pick` (a match
  by arm identity, B's text), so "THE ONE ACCESSOR" no longer reads as unqualified.
- **O1** (window_ren.c). `const char *wf_ren_pieces(struct wf_plan *w, wf_frame_row f, const
  ren_fused_row *fu, fd_form search)`: a MOVE of `wf_plan_site`'s piece selection (Table S, skeleton,
  and stream/check under `ST_ONE && !fu`), returning Table S's `why`; `wf_plan_site` keeps the
  refusal text and asks `wf_frame_name` itself (pure; order-free). `const char *wf_ren_check(void)`:
  a MOVE of `wf_tables_check`'s `ren_search` and `ren_fused` loops.
- **A5** (window_span.c). `int wf_span_render(wf_rc *rc, kb *t, const struct wf_stretch *st)` and
  `int wf_span_define(wf_rc *rc, const struct wf_stretch *st, mf_sink *out)`: wrappers of the row's
  `render`/`define` calls. [rev2.1] R20: the callers' `if (..) return -1;` exist at B and are kept;
  `wf_span_render` is a pure wrapper, and `wf_span_define` MERGES the caller's `define` NULL test
  into itself (`return define && define(..)`); the one ADDED statement of A5 is in frame's
  `wf_tables_check` (`if ((e = wf_span_check())) return e;`, value-equal: each sub-check returns
  its first refusal or NULL in B's loop order). `const char *wf_span_check(void)`: a MOVE of wfS's part of `wf_tables_check` (:2587-2595
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
   finder.c `popcount256` (its count, and :938-939's least-member loop -> `kit_pos_first`,
   `kit_pos_in`; [rev2.1] R16: rev 2's :940 is the `covered` test that reads its result);
   ofsskip.c `set_count`/`set_first`; precheck.c `only_byte`/`single_byte`'s reads; presence.c
   `set_first_member` and `one_member` (callers -> `kit_pos_count(X) == 1`); compose.c's two counts,
   `part_is_byte`'s membership and `span_byte`; pffind.c `set_size` (count + first member);
   generic.c `kit_set_test` (:110-111, membership); `kit_mass`'s own open read. Kept byte for byte:
   S452's anchor (finder.c `if (m == 1)`) and S804's (precheck.c `return n == 1;`). Excluded by R-1,
   named: `formhash.c:493`, `k1_ref.c`.
2. **H2, the final file(s)** (W2). The two-file reading, CONFIRMED by the kit manager: D204's
   "their final file" is read as one file PER QUESTION FAMILY, because ruling 2 puts a table with
   its searchers and nothing else:
   - `kit_pos.c` = the position questions: the set family, `kit_run_member`, `kit_mass` (the
     final file that takes `kit_mass`, so presence.c and the planner both call DOWN into it) and
     [rev2.1] `kit_run_set` with its reader `kit_run_at` (r98 R13, below);
   - `kit_pick.c` = the TIE table and its searchers only (`kit_pick_takes` and the predicates
     public, `kit_tie_takes` static).
   Placed by rule: `kit_tie_member_key` -> presence.c, static (its one caller, `member_key`; S1094
   re-points there); `sets_at` stays family-private in verify (all its callers are family files,
   so no kit.h name; not renamed: S3006 needs no re-spell); `meet_at` stays stop's (static,
   Table A's callback).
   [rev2.1] R13 (the kit manager's choice, ruled): rev 2 kept `kit_run_set` and `kit_run_at` in
   presence.c on two false premises (r98 FIXIND-11): `kit_run_set` converts a RUN TERM's position
   (an `mf_term`'s `run`/`mask`; kit.h: "the kit's ONE run-position-to-set conversion") and reads no
   presence span record, and [SP1D-KITSPLIT-SEAMS] holds no seam fact for it (that row's status now
   holds seam facts only; its primitives half, which named `kit_run_set`, is the half D204
   overtook). Both MOVE to kit_pos.c at U3 with `kit_mass` (B presence.c :84-91, :112-118; their
   kit.h declarations and names unchanged; no binder quotes either, `binders.py`: 0 rows), so the
   primitives move ONCE, as D204 says, and no second move is owed. `kit_run_at` is the
   `kit_pos_at` reader of a RUN term (no caller in memfn/src today; a public kit.h name, kept).
   `kit_wspan_at` STAYS in presence.c on a true reason: it reads `mf_wspan`'s `set[j]`, a presence
   span record. Effect: compose.c's call of `kit_run_set` now goes DOWN into kit_pos.c, so compose.c
   -> presence.c is `kit_pres_run` alone at the tip (§6.5).
3. **W9, the general form.** `kit_<family>.c` is the general form for a kit-wide question family
   that more than one kit area asks: `kit_pos.c`, `kit_pick.c`, `kit_kb.c`. Unlocks: [SP1D-ARGMIN]'s
   argmin goes to `kit_pick.c` on its own trigger (its next argmin site); a new position question
   (NEON V's lane masks, if they need a set query) joins `kit_pos.c`.
4. **W4, ARV-7's order.** C0b moves ARV-7's text-buffer leaf (`kit_kb.c <- compose.c 27-115`, B-s3)
   before the split, so the plan rows' "ARV-7 before or with it" holds. Effect, measured on the
   assembled tip: `kit_kb.c` is in no cycle ([rev2.1] R23, the spec spelled: `: > $S/empty.spec;
   python3 -I $D/kitgraph.py $S/asm/memfn/src $S/empty.spec` prints one SCC of 24 files that does
   not contain `kit_kb.c` or `kit_pos.c`; the spec must be EMPTY over an assembled tree, §13.1);
   the remaining full-kit SCC runs through compose.c's services (`kit_walk`, `fd_find`, ...), which
   is ARV-7/H8's layer-order register row and not this unit.
   [rev2.1] R22, ARV-7's two halves: the arch note's ARV-7 row is "the text buffer's own leaf file
   (a pure move); the layer order filed as a row with its known violations". C0b does the LEAF
   half, so [ARV-7-TEXTBUF-LEAF]'s leaf is DONE at C0b; its other half, the declared layer order of
   memfn/src as a register row with its known violations, is NOT this unit's and stays open with
   its own trigger, for main to rule (PLAN, §13). The row's range `compose.c :29-108` is stale:
   it cuts `kit_out` mid-function (B :108-114); C0b's 27-115 (the `kb` header to before "the
   selection table") is the whole leaf.
5. **W5, the cycles exactly.** With every kit file but the family (kit_kb.c, kit_pos.c,
   kit_pick.c included) and presence.c dropped (`DROP="<the 16 others>" python3 -I $D/kitgraph.py
   $S/asm/memfn/src $S/empty.spec`; rev 2's "17" counted kit_kb.c among the dropped, which gives
   the same result): no CYCLE. The family and presence.c form a DAG; the presence <-> window pair
   edge is gone. With compose.c and gate.c dropped instead (`DROP="compose.c gate.c"`), one SCC of
   15 remains (CENSUS, same spec): its loops are presence.c <-> finder.c (`fd_pres_run` /
   `kit_pres_*`, a B-era pair outside the family) and finder.c <-> window_ren.c (`wf_renders` /
   `fd_find`). [rev2.1] R24: with nothing dropped, presence.c <-> compose.c is a second B-era pair
   outside the family (`presence.c -> compose.c: kit_presence_check`, `compose.c -> presence.c:
   kit_pres_run`; R13 took `kit_run_set` off the second edge); neither pair is this unit's, and
   Goal 4's "calls down only" is stated INTO THE FAMILY. The second is the H1 OUTCOME, not ARV-7's: `wf_renders`
   is `ren_search`'s searcher, so ruling 2 puts it in ren, and `fd_find` is T-FIND's one walk, which
   `wf_find_decide` asks; the arch note's A8 gives finder <-> frame to H1. Reason it stays: breaking
   it needs `fd_find` to take the renderable set as a stated fact rather than asking for it, a
   behaviour change outside a move unit. Trigger: the first unit that changes T-FIND's asker
   interface (the plan_frame line's successor), or H8's layer-order row, whichever lands first.
6. **W6, H8's placement half.** `mf_pres_ports` (memfn.h; presence.c B :283, [rev2.1] R16: rev 2's
   :252 was the tip's line) stays in presence.c: it is
   presence's pure query over the presence spans, read by pcrec's trace build; presence.c's split
   is the later unit of §4.4. `mf_wdecide` is window_ask.c's; `wf_check` window_check.c's.

## 7. The binding checks that move

`binders.py ROOT TREE [RUNNERS_ROOT] [--compile]` is the re-aim table: for every binder KEYED to a
file of the unit's population, where its text is in TREE (OK file, STALE, AMBIGUOUS), after the
unit's own re-spellings (its RENAMES/LITERAL table, `OK*`), and with `--compile` whether the
binder's AFTER/TO compiles in its new file. Its control is B itself: run with TREE = ROOT it must
find every binder in its present file.

[rev2.1] R3, the population: rev 2 selected rows keyed to B's eight file names only, so run per
commit (ROOT = TREE = the commit) a row the commit had just re-keyed to its new file LEFT the
population, and the report exited 0 at any size. The population is now B's eight edited files
PLUS every file the unit creates (cut.spec's left-hand sides, read by the script), for mech rows,
G2 plants (`*.c@@` and `*.h@@`), census rows (any of those keys) and rows_check.py's PLANTS (R15);
a re-keyed row stays in at every commit. Each population has a FLOOR, its size at B (mech 187, G2
75, purity 49, census 67, rows 4); a population below its floor is red (`POPULATION N BELOW FLOOR
F`) whatever its rows read. `CC` comes from the environment only (gcc-16 on the Mac, gcc on Linux;
`--compile` without it is an error). Drilled, §7.8.

Results (CENSUS; `$S/binders_*.txt`, rev 2.1's binders.py at B'):

| population | rows | at B (TREE = B, runners of B) | at B (runners of C0) | tip (runners of C0 `838deefe2`, `--compile`) |
|---|---|---|---|---|
| mech sites (SAB_BEFORE, SAB_BEFORE2) | 187 in 177 files | 187 OK | 187 OK | 187 OK (3 `OK*`); compile 186 PASS + 1 SKIP(header) |
| G2 plants (run_g2_win, run_g2_pres, run_proof) | 75 | 71 OK, 4 STALE | 75 OK | 75 OK; 75 PASS |
| purity `old` texts | 49 (of 53 rows; 4 are `-`) | 49 OK | 49 OK | 49 OK (1 `OK*`) |
| decider census rows | 67 (57 window/presence/compose.c + 10 finder/generic/ofsskip.c) | 67 OK | 67 OK | 67 OK |
| rows_check.py PLANTS edits (R15) | 4 (S2983 x2, S2988 window.c; S2984 finder.c) | 4 OK | 4 OK | 4 OK; 3 plants PASS |

The 4 STALE are S1423, S3092 (window.c) and S3064, S1224 (compose.c): stale AT B, so the split
inherits them; lane/memfn-plantcheck re-aims all four (FUW-12), which is C0. Re-keyed by the split
(moved to a new file): mech 59 sites in 58 files (window.c; S1094 among them, to presence.c); G2 41; purity 49; census 50;
rows 3 (all window_ren.c). Total 202 re-points, listed per unit by `python3 -I $D/repoint.py
$S/binders_tip_cc.txt` (§8.1).
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
F2 (rev 1, [rev2.1] R8 restated exactly): the census's self-checks name window.c by text in two
kinds. (a) The three `plant()` rows (`kit_pick_takes(&best, p->mass`, `kit_pick_takes(&b, c.v`
keyed window.c, and presence.c's `kit_pick_takes(&bw, wm`) READ their file and copy a loop; at the
tip they fail with FileNotFoundError (measured): U1 keys each by content, the one file holding its
anchor (window.c until the move: `&best` -> window_stop.c at U23, `&b, c.v` -> kit_pos.c at U3).
(b) The three C2 bypass plants and the S2985 renderer-list plant APPEND with `open(.., "a")`: on
a tree without window.c mode "a" CREATES window.c, the stray filter (`startswith("window.c:")`)
reads the planted lines and the checks pass on a file the unit deleted; at rev 2's tip only (a)'s
crash masked this. They quote no text, so U1 names their APPEND TARGET by content: the one file
holding `static const ren_search_row ren_search[] = {` (window.c until U13, window_ren.c from
U13; S2985's lines name `ren_search`, so the target is the file they would really live in),
ASSERTS it exists and is unique before `open(.., "a")` (else the check is red: "append target
missing"), and filters strays by that file's name. U1 FAILS IF THAT FILE DOES NOT EXIST (rev 1's
sentence, restored). §10 forbids the census's self-plants creating a file.

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
[SABANCHOR]'s plant pass (its floor 81) counts through the same applier. The executing gates are
G3's `--plants` runs at the tip, [rev2.1] R2: on the Mac `run_g2_win.sh --plants` (33 re-aimed
plants) and `run_proof.sh --plants` (1); on Linux only `run_g2_pres.sh --plants` (7), §8.2/§8.3.

Re-spelled plants (`OK*`, the FROM changes): S1402 (O3), S1405, S1428, S3106 (H3), S1410 (H3
`full`). TO-only: S1427 ([rev2.1] R25: its TO calls `count` AND `in_set`, re-spelled
`kit_pos_count` AND `kit_pos_in`; with `count` alone it still fails, `implicit declaration of
function 'in_set'` (r98 READY-4, planted); unre-spelled it FAILS to compile in window_find.c, the
fail direction of §7.5; binders.py's RENAMES carries both).

### 7.4 Purity (W24)

`run_purity_reach.sh` reads `window.c` for its population and inserts the NEVER functions before
`wf_arows[]`. U1, on the unsplit tree: the population greps the FAMILY LIST (`window*.c kit_pick.c
kit_pos.c`) with "exactly once across the list"; each row's plant and NEVER insertion go into the
file that holds the row's `old` text (tip homes, `binders.py`: ren 26, verify 12, stop 4, frame 4,
margin 3), and the link line excludes THAT file's object, not `window.o`. [rev2.1] R7, the NEVER
anchor per commit range (the NEVER bodies need `wf_x`/`wf_dec` declared above them and must
precede the row's `new` text): while the row's text is in window.c (U1-U22; no purity row's text
stays with decide, so window.c holds none from U23), the line before `static const wf_arow
wf_arows[] = {` in window.c, as today; once the row's file is peeled, the line after that file's
prologue `#include "window.h"` (R5 writes it into every window_*.c; the types are window.h's from
U4). Rev 2's "the NEVER functions include window.h" is DROPPED: window.h does not exist before
U4, and the prologue already includes it. `purity_rows.tsv` row MARGIN is re-spelled by O3. `run_finder.sh`'s
`purity_plant` (rows a-mass and m-parked) is re-aimed by content in U1 (`make test-memfn-finder`
runs it, G1).

### 7.5 Re-spell lists and the AFTER/TO compile probe (W25, W26)

The re-spell lists, derived (not hand-listed) by `binders.py`'s table (H3's renames; O3's and A2's
expressions):

- mech: S1417 (O3; SAB_BEFORE and SAB_AFTER), S3106, S3525 (H3);
- G2: S1402, S1405, S1410, S1428, S3106, and S1427 TO-only (`count` and `in_set`, §7.3);
- purity: MARGIN (O3).
- Not re-spelled, checked: S3006 (`sets_at` is not renamed), S452 and S804 (U2b keeps both anchor
  lines byte for byte), S3250 (calls `reply_of`, in window.h).

W26's correction: a non-compiling sabotage is a loud BUILD-FAILED anomaly in mech, not a kill; the
real gap is that nothing compiles a re-pointed AFTER before the next full mech run. The probe
(`CC=gcc-16 binders.py . $S/asm <plantcheck runners> --compile`): each SAB_AFTER (with the row's
other site when both are in one file) and each plant's TO set (all edits of one plant label
together) applied to its NEW file alone and `-fsyntax-only`-ed: mech 186 PASS + 1 header (S3285,
probed through its 19 includers: 19 PASS); G2 75 PASS; [rev2.1] rows_check 3 plants PASS. At B:
the same, all PASS (control of the probe's setup; its fail directions are S1427 above and §7.8's
drill).

### 7.6 The rest

- **rows_check.py** plants S2983 (two edits) and S2988, keyed window.c at B: [rev2.1] R15, ALL
  THREE texts are in `window_ren.c` at the tip (rev 2's "window_frame.c" was wrong); re-keyed in
  U13 (ren). They have their own (before, after) applier, outside tests/lib/plants.py, so neither
  `--plant-check` nor [SABANCHOR]'s plant pass sees them; rev 2.1's binders.py counts them (its
  `rows` population, floor 4 with finder.c's S2984) and compiles each plant's edits in its new
  file, per commit; `make test-memfn-rows` (G1) executes them.
- **C15/C16, PROVENANCE.** `run_link_checks.sh` (`make test-memfn-link`): every new external symbol
  `pcrec_mf_*`; every new file's SPDX and Provenance lines (assembler R5 writes them). [rev2.1] R10:
  C16 holds memfn/PROVENANCE.md file for file both ways (`no row in PROVENANCE.md` / `a PROVENANCE.md
  row names a file that does not exist`), so EVERY new file gets its own row IN THE COMMIT THAT
  CREATES IT: kit_kb.c at C0b, kit_pos.c at U2, kit_pick.c at U3, window.h at U4, each peel's file
  at its peel, window_decide.c at U24 (row 54 re-keyed, below). The artifact-text column per file:
  kit_pos.c inherits presence.c's row 53 "no artifact text" (position questions only), as do
  kit_pick.c and the decision/plan files (cands, check, stop, margin, verify, decide, plan, frame,
  ask, parts); kit_kb.c (the buffer every renderer writes through) and floor, find, text, test,
  span, vform, efind, ren, legacy carry artifact text (the renderers and their text kit). Row
  54's A-model/C-model transcription clause moves to window_stop.c's and window_verify.c's rows at
  U23/U21 (`files.spec`'s `prov` lines), the rest "kit original"; row 53 (presence.c) notes
  `kit_mass`'s, `kit_run_set`'s and `kit_run_at`'s move at U3; compose.c's row notes `kit_kb.c` at
  C0b. C16 checks that each row exists, not its artifact-text cell: the cell is the builder's
  reading of the file's own text (row 54 today: artifact text on a "window-family" art only, the
  floor row's byte loop; the legacy rows' text is theirs).
- **Makefile.** KITHDRS gains `memfn/src/window.h`; `KITSRCS` is a wildcard; no Makefile line names
  window.c (`grep -n 'window\.c' Makefile`: 0).

### 7.7 File-name readers (W30)

Not binding (re-read, re-worded in the commit that moves the text they describe). [rev2.1] R17,
the census with the file name as a token: `git grep -l -E 'window\.c([^a-zA-Z0-9_]|$)' -- tests
memfn scripts Makefile ':!tests/mech/sabotages/'` at B': 48 files, of which 2 are append-only
records (memfn/docs/journal.md, memfn/docs/responses.md: never re-worded), so 46 readers (CENSUS of
that spelling; a reader spelling it differently, e.g. run_purity_reach.sh's `window.o`, is missed,
so a FLOOR of readers). Rev 2's 50 used the substring `window\.c` and counted `scripts/gestalt` and
`scripts/statusline.sh`, whose only match is jq's `.context_window.…` path: not readers, dropped.
They include r95's six (run_decide_check.c's comments, run_pres_picks.sh, tests/memfn/CLAUDE.md,
memfn/tests/NOTES.md, kit.h/memfn.h/.def comments). C0b's and U3's moves out of compose.c and
presence.c have reader populations of their own, same command with `compose\.c` / `presence\.c`:
32 and 18 files (FLOORS, same caveat; e.g. the arch note's ARV-7 row naming `compose.c :29-108`,
memfn/src/CLAUDE.md's compose.c and presence.c entries, mass_check.c :4 naming kit_run_member's
home). 0 binders quote text in compose.c 27-115 or presence.c 56-91/112-118 (binders.py at the
tip: no row re-keyed to kit_kb.c; kit_pos.c's rows are window.c's), so those moves are prose-only.
The assembled tip does NOT carry the re-words: its kit.h still says `kit_mass` is presence.c's and
names window.c in 40-odd comments (`grep -n 'window\.c' $S/asm/memfn/src/kit.h`); the build
re-words them in the moving commit, the assembler re-words no comment.

### 7.8 binders.py's per-commit population, drilled (r98 R3)

The drill (lane scratch `$S/drill`: the assembled tip's `memfn/` with a copy of B''s `tests/mech`
and `tests/memfn`, ROOT = TREE = that tree, i.e. a commit AFTER a peel re-keyed its row; runners
of C0), on mech S3535 (window.c :4459-4468's w32 stamp line, which the vform peel U6 moves):

| case | S3535's row | binders.py (rev 2.1) | rev 2's binders.py, same tree |
|---|---|---|---|
| (a) control | SAB_FILE re-keyed `memfn/src/window_vform.c`, AFTER intact | rc 0; `S3535 ... OK window_vform.c ... PASS`; `binders: mech 187 rows, 187 OK, 0 bad, floor 187` | - |
| (b) the drill | re-keyed, AFTER broken (`stamp = w64_undeclared;`, does not compile) | **rc 1**; `S3535 ... OK window_vform.c ... FAIL ...: In function ...`; `binders: mech 187 rows, 186 OK, 1 bad, floor 187` | rc 0; `binders: mech 186 rows, 186 OK, 0 bad` (the row LEFT the population: r98's defect, reproduced) |
| (d) floor | SAB_FILE re-keyed to a file outside the population (`memfn/src/levels.c`) | **rc 1**; `binders: mech POPULATION 186 BELOW FLOOR 187 (rows left the selection)` | - |

Commands: `CC=gcc-16 python3 -I $D/binders.py $S/drill $S/drill $S/pc --compile` ((a), (b); rev
2's file is `git show 6b60976ad~1:docs/design/memfn/window_split/binders.py`), and the same without
`--compile` for (d). So the per-commit arm fails on a re-keyed broken AFTER and on a shrinking
population, which rev 2's could not.

## 8. Commit order and gates

### 8.1 Order (W20)

Every commit is byte-identical to the base and green on its own. [rev2.1] R5: each unit's
RE-POINT LIST (the binders whose text it moves to another file) is DERIVED, never hand-listed:
`python3 -I $D/repoint.py $S/binders_tip_cc.txt` (the binders.py run over the assembled tip)
prints `UNIT FILE POP ID` per row, CENSUS: 202 rows in 19 units (U3 10, U4 1, U6 6, U7 7, U10 6,
U11 11, U12 5, U13 47, U14 7, U15 5, U16 12, U17 25, U18 2, U19 4, U20 8, U21 18, U22 9, U23 17,
U24 2; U8 floor and U9 test move none). The lists below name the non-peel units' rows; a peel's
are its file's rows in that output.

- **C0 (outside the unit):** lane/memfn-plantcheck lands (FUW-12: S1423, S3092, S1224, S3064
  re-aimed; the one applier; `--plant-check`).
- **C0b:** [rev2.1] R9: FIRST F1 (memfn/src/CLAUDE.md, 12,277 B of its 12,288 B limit, moves
  window.c's detail to memfn/NOTES.md, so this and every later commit can add its file's line);
  then ARV-7's leaf, `kit_kb.c <- compose.c 27-115` (W4), with kit_kb.c's PROVENANCE row and
  compose.c's row's note (R10). No binder quotes the moved text (0 rows, §7.7).
- **U1 checks first, on the unsplit tree:** purity's family list and per-file insertion with the
  anchor per commit range (W24, §7.4), `purity_plant`, decider census self-plants keyed by content
  and their APPEND target found by content and asserted present (F2, §7.2). Green at B with the
  list {window.c}.
- **U2 ARV-5:** `kit_pos.c` born with the set family and `kit_pos_first` (its PROVENANCE row and
  CLAUDE.md line); window.c's callers re-spelled (S3106, S3525; plants S1405, S1410, S1427 (`count`
  and `in_set`), S1428, S3106). **U2b:** the other files' copies (§6.1). No binder changes FILE here.
- **U3 ARV-16:** `kit_pos.c` takes `kit_run_member`, `kit_mass`, [rev2.1] `kit_run_set` and
  `kit_run_at` (R13); `kit_pick.c` born (TIE + O3, its PROVENANCE row); `kit_tie_member_key` to
  presence.c; S1417, S1402, purity MARGIN re-spelled; census U3 row (§7.2). [rev2.1] R5, re-pointed
  here (repoint.py's U3 rows): mech S1094 (presence.c), mech S3106 (kit_pos.c); plants S1403
  (kit_pick.c), S3106 (kit_pos.c); census `kit_pick_takes`, `kit_tie_takes`, `wf_tie_to`, `wf_ties`
  (kit_pick.c), `kit_run_member` (kit_pos.c), `kit_tie_member_key` (presence.c).
- **U4 window.h born:** the shared types and the vocabulary (W3), `#include`d by window.c; KITHDRS;
  C16 (its PROVENANCE row); the two arms' declarations leave kit.h, `wf_part_site` static (W13).
  [rev2.1] R6: moving :8-65 (the family comment, whose `*/` is :65) leaves window.c's :1-7 head
  comment unclosed (probed in r98: it comments out the includes), so U4 adds one ` */` line after
  :7 (U23 replaces that head); and U4 re-points mech S3285 to window.h (its anchor `enum {
  WF_SPAN_HEAD = 64 };` is B :1493, inside the `window.h <-` item 1493-1494). Separability held
  (r98: B + H3's renames + all 351 header lines moved compiles, both defines).
- **U5 the accessors in place** (A2, A3, A4, O1, A5, R26's comment), still in one file; census U5
  row. No binder changes file.
- **U6..U23, the peel, 18 commits, one file each, emitter end first:** vform, find, floor, test,
  text, span, efind, ren, frame, legacy, parts, ask, plan, check, cands, verify, margin, stop. Each
  moves its ranges, drops `static` from the names that cross IN EITHER DIRECTION between the new
  file and the remainder and declares them in window.h, deletes the moved names' forward
  declarations (R4), and re-points its repoint.py rows (mech, G2, purity, census, rows_check), its
  file's PROVENANCE row and CLAUDE.md line. U13 (ren) carries rows_check's S2983/S2988 (§7.6).
  U23 (stop) also replaces window.c's head with window_decide.c's prologue.
- **U24:** [rev2.1] R4: `git mv memfn/src/window.c memfn/src/window_decide.c` (the file's content
  100 % unchanged, so `git log --follow` keeps the decider's history) PLUS, in the same commit, the
  residue's binders no peel re-points (repoint.py's U24 rows: mech S3252's SAB_FILE, census row
  `decide`), PROVENANCE row 54's file cell (`src/window.c` -> `src/window_decide.c`; C16 holds the
  table file for file both ways, so a bare rename is red), and memfn/src/CLAUDE.md's entry. Rename
  detection is per file, so the other files' edits do not cost the 100 % similarity.

19 family `.c` files + window.h = 20 new family files; with kit_pos.c, kit_pick.c, kit_kb.c, 23.

### 8.2 Gates

[rev2.1] R1/R2, the rule (r98 RULING): a gate arm is used only on a box where its BASE run is
GREEN; §8.4 records each Mac arm's command and last line at the base. An arm red at the base cannot
fail, so it is not listed for that box.

- **G1, per commit** (W21, W27), each its own command (no arm stops another):
  1. the strict compile: on the Mac `bash $D/syncheck.sh $C gcc-16` over a scratch copy of the
     commit's `memfn/` (`C=$S/c; rm -rf $C; mkdir -p $C; cp -R memfn $C/`; syncheck copies the
     drivers into its OUT, so never the tree itself): KITFLAGS + `make strict`'s `-Wshadow -Werror`
     + `-Wmissing-prototypes`, plain and `-DMF_TRACE`, + the four white-box drivers. On Linux the
     same with `gcc`, and `make strict`. [rev2.1] R1: `make strict` is LINUX's only: its recipe
     ends with `memfn/tests/check_targets.sh || exit 1`, which exits 1 on aarch64 whatever the
     compiler, so on the Mac it is red at every commit, base included, and (without `-k`) runs no
     target after it;
  2. `make CC=gcc-16 test-memfn-rows test-memfn-finder test-memfn-link` (Linux: plain `make`);
  3. [SABANCHOR] `python3 scripts/m6read_check_sab_anchors.py`;
  4. `python3 tests/memfn/decider_census.py --root .` (test-memfn-rows runs it too);
  5. `bash tests/memfn/run_purity_reach.sh`;
  6. each runner's `--plant-check` (C0): `memfn/tests/run_g2_win.sh`, `memfn/tests/run_g2_pres.sh`,
     `tests/memfn/run_proof.sh`, `tests/memfn/run_wreply.sh` (static: no build, any host);
  7. `python3 -I $D/unused.py memfn/src <the family files + every edited file>` (syntax-only does
     not report an unused static);
  8. `CC=gcc-16 python3 -I $D/binders.py . . --compile` (Linux `CC=gcc`): the W26 probe, every
     population at or above its floor (§7, §7.8), seconds to minutes.
- **G2, byte identity per commit:** `scripts/emit_sweep.py --ref <the unit's base> --tree-rev
  <commit>` (W28: `--ref` the base the unit is cut from, not T), three arms: default;
  `--extra=-fmemfn-simd=x86-64` (vrun@w16; DIFFER_PINS' pinned arm); and
  `--extra=-fmemfn-simd=x86-64-v3 --no-differ-floor` (an unpinned arm, WAIVED by that flag), which
  renders the V form's w32 level block (window_vform.c, B :4459-4468, mech S3535's code); identity
  over it is a real gate on the Mac (r98 READY-2: emit_sweep's target set-aside masks none of 3
  planted w32 changes). [rev2.1] R11, the arm's REACH COUNTER, which the waived floor cannot be:
  `python3 -I $D/w32reach.py build/pcrec . --floor=byte=N,utf8=M` counts the corpus patterns
  (emit_sweep's distinct-pattern population) whose arm-3 artifact holds `span-vector@w32`, per
  base, and is red below its floor; N and M are its BASE run's counts (§8.4), pinned in this note
  (the pin site: the gate's command line, no scripts/ edit). **Where it runs (W28):** emit_sweep
  and w32reach emit text only, and an explicit-family arm reads the same on every host ([XARCH-DEV]
  U3: "the cells read the same on every host"), so all three arms and the counter run on the Mac.
  Compiling or RUNNING the emitted x86-64-v3 code is G3's and is Linux's.
- **G3, at the tip** (the gates that EXECUTE re-aimed plants, W22), [rev2.1] R2, by box:
  - the Mac: `memfn/tests/run_g2_win.sh --plants` (its plant path builds the planted kit and runs
    `one_run` only: no target loop, no `v_section`, host-independent; EXECUTES its 33 re-aimed
    plants S1400-S1428, S1543, S2986-S2991, S3040, S3041, S3084-S3096, S3116-S3118, read per
    plant); `tests/memfn/run_proof.sh` and `run_proof.sh --plants` (S1419, re-keyed
    window_check.c); `memfn/tests/run_g2.sh --quick` (no plants; run_g2.sh has no
    `-fmemfn-simd` arm and no `--plant`/`--plants`/`--plant-check` mode, so rev 2's "with and
    without `-fmemfn-simd` ... each also `--plants`" is DROPPED for it);
  - Linux only: `run_g2_win.sh` plain (it runs `v_section`, i.e. `memfn/tests/g2_vspan.py both`,
    which is red on a host that cannot run x86-64-v3 text: "a skip is not a pass"; so on the Mac
    plain `run_g2_win.sh` is red at the base and is not listed); `memfn/tests/run_g2_pres.sh` plain
    and `--plants`, which EXECUTES its 7 re-aimed plants (S3012 stop; S3047, S3110, S3112, S3125,
    S3126 parts; S3106 kit_pos) (on the Mac its `host_has` accepts x86-64, whose text does not
    compile on arm64, and its x86-only plants S3099/S3101/S3102 can never read RED there, so its
    rc is red at the base: not a Mac gate); `run_g2.sh` (full); and the mech rows whose detection
    only Linux suites execute, run as mech rows (not REACH_ONLY) at the tip: S3525 (re-spelled
    `in_set`), S3526 (SAB_SUITES `g2v`, REACH `-fmemfn-simd=x86-64-v3`) and S3515, S3530,
    S3532-S3536 (`simdfloor` at x86-64-v3).
- **G4, symbols at the tip:** `make test-memfn-link` (run_link_checks.sh: C15, C16) and
  `nm -g` of every kit object (or `build/libpcrec.a`), defined `pcrec_mf_*` symbols, diffed
  against the base's: [rev2.1] R12, BOTH directions pinned by name: +82 (the 74 new window.h
  externals, the 2 arms already external now declared there, + the 8 new kit.h names: the 6 set
  family names and the 2 TIE predicates) and -3 (`pcrec_mf_kit_tie_takes`,
  `pcrec_mf_kit_tie_member_key`, `pcrec_mf_wf_part_site`, made static); r98 measured B 178 ->
  tip 257 over every memfn/src object; R13 moves two externals between files and changes no name.
- **G5, at the tip, Linux:** REACH_ONLY mech over the re-pointed rows, then `make test` (a
  boxqueue job). [rev2.1] Stated: G5 is NOT a Mac gate in this unit: `make test` measures ~100-105
  minutes on the Mac (docs/testing.md), so its base run is not taken here, and an arm with no
  base run on a box is not listed for it (R1's rule).
- **G6:** `-fstack-usage` (run_link_checks.sh's R-28 recipe, which `make test-memfn-link` runs: no
  kit frame over its cap, population floor) at the base AND the tip: no frame over 4 KB, and every
  frame that grew past 3 KB from its base value named in the delivery. The base run is G1 arm 2's
  test-memfn-link at the base (§8.4); the per-frame comparison reads its `su` files.
- **G7, stamps unchanged:** [rev2.1] R12, each arm with its reader: `MF_SITE_ABI`, `MF_CLASS_V`,
  `MF_VOCAB` = memfn/include/memfn.h's three `#define`s, equal at base and tip (`grep -E '^#define
  (MF_SITE_ABI|MF_CLASS_V|MF_VOCAB) ' memfn/include/memfn.h`, diffed; memfn.h's other edits are
  comments only, `git diff BASE -- memfn/include/memfn.h`); the `_MEMFN_FORMS`/`_MEMFN_LIBC` stamps
  by `make test-memfn-stamps` (run_libc_census.sh, which reads none of the three defines); pcrec's
  abi by G2 (every artifact's first line).

### 8.3 By box (W29), plant by plant

| gate | the Mac (aarch64, gcc-16; the Mac suite lock, not boxqueue) | Linux (x86, boxqueue) |
|---|---|---|
| G1 | arms 1 (syncheck.sh) and 2-8, every commit; NOT `make strict` | `make strict` + arms 1-8, every commit |
| G2 | all three arms + w32reach.py (text only) | yes |
| G3 | `run_g2_win.sh --plants` (33 plants), `run_proof.sh` + `--plants` (S1419), `run_g2.sh --quick` | REQUIRED: plain `run_g2_win.sh` (with g2_vspan), `run_g2_pres.sh` + `--plants` (its 7 plants), `run_g2.sh`, `g2_vspan.py`, mech S3525/S3526 (g2v) and S3515/S3530/S3532-S3536 (simdfloor) executed |
| G4, G6, G7 | yes | yes |
| G5 | not listed (no base run: ~100 min) | REQUIRED at the tip |

`scripts/boxqueue` needs flock and /proc (Linux); on the Mac heavy stages take the Mac suite lock.
The Linux arms are OWED by the build lane at the tip, not run by this design lane (its brief: the
Linux arms are recorded as Linux-owed, not run).

### 8.4 The base runs on the Mac (r98 R1/R2's rule)

@BASERUNS@

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

- Change a statement, its order or a constant beyond §5's stated accessor shapes and [rev2.1] R14
  §6.1's U2b re-spells (O6 put them inside the unit: loops -> `kit_pos_*` calls in 7 non-family
  files, value-equal, ofsskip.c's `set_count` int -> unsigned at its 5 sites stated); a commit with
  an emit_sweep difference is reverted, not re-pinned.
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
| **total** | **`syncheck: 82 PASS, 0 FAIL (gcc-16)`** ([rev2.1] re-run with rev 2.1's specs, R13's cut and R26's edit included: the same 82/82) |
| control: B's own tree (`memfn/src` copied) | `40 PASS, 0 FAIL` (18 files x 2 + 4; [rev2.1] the same at B' and on the base archive, §8.4) |
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
| O1 frame's grain | SPLIT: `window_frame.c` 277 + `window_ren.c` 418 (rev 1: one 737-line file) | pure move 86 statics / 40 types (family census, §4.2); [rev2.1] R21: r95's {frame, ren} SCC (through `wf_erows` when `wf_tables_check` sat in ren) goes with the CUT: rev 2's cut homes `wf_tables_check` in frame, and the PURE move already has no file cycle (`census.py memfn/src <family spec> --calls`: FILE CYCLES empty, no edits applied); what O1 + A5's per-table form (`wf_ren_pieces`, `wf_ren_check`, `wf_span_check`) removes is table CROSSINGS: frame's direct reads of `ren_search`, `ren_fused`, `ren_skel`, `ren_stream`, `ren_check`, `wf_srows`, `wf_spanrows` (Goal 1's 13 -> 2). At the tip frame -> ren 3 calls (`wf_find_decide`, `wf_ren_pieces`, `wf_ren_check`), ren -> frame 0 (`kitgraph.py`, empty spec) |
| O2 planner's grain | separate: stop 254, margin 98, verify 314, decide 135 | A2's 3 + A3's 1 names |
| O3 TIE's shape | two predicates, enum private | kit.h +2 -2 |
| O4 the name window.c | no file keeps it; U24 renames the remainder | r95 W31: keeping it saves at most 24 of ~150 binders; rev 1's "halves" withdrawn |
| O5 MARGIN | own file, 98 lines | A3 |
| O6 U2b | inside, widened (§6.1) | 7 other files edited, all compile (§11) |
| O7 find -> frame names | kept: they are row payload (actions); find's FAMILY names 16 | - |

## 13. Findings and records

- F1 (W35) `memfn/src/CLAUDE.md` is 12,277 B against 12,288: the file list for 22 files moves
  window.c's detail to `memfn/NOTES.md` (there is no notes file in memfn/src: C16), [rev2.1] R9:
  in C0b, FIRST (C0b, U2 and U3 each add a kit file before U4, and any one-line entry breaks the
  limit: the pre-commit hook's `--staged` row and `make test-claudemd-size`).
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
- [rev2.1] R22 (PLAN, main's): [ARV-7-TEXTBUF-LEAF] reads, after C0b: the leaf DONE at C0b
  (range 27-115, not the row's stale :29-108); the register-row half (the declared layer order of
  memfn/src with its known violations) OPEN, with its own trigger for main to rule. Recorded only;
  this lane edits no plan row.
- [rev2.1] OPEN CHOICES: none raised by rev 2.1's base runs (§8.4).

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
  [rev2.1] R19: it counts FUNCTION BODIES only, so an object named in another file's table
  INITIALIZER is invisible to it: `wf_find_ct`/`wf_floor_ct` in Table E's rows (§4.4, by name).
- [rev2.1] R23: `kitgraph.py` reads every static of a file named on a spec line's right side as
  visible across the split, so over an ASSEMBLED tree a per-file spec (`F <- F 1-99999`) invents
  edges between same-named statics and parameters (r98: a 28-file SCC holding kit_kb.c through
  `kit_kb.c -> generic.c: need`); over an assembled tree give it an EMPTY spec (§6.4, §6.5).
- [rev2.1] `binders.py`'s population is keyed by FILE NAME (B's eight + the unit's new files); a
  binder keyed to some other file is outside it by construction, and its floors are B's sizes, so a
  NEW binder row in the population raises N above the floor without moving the floor.
- `binders.py`'s compile probe compiles the planted file alone; a header plant is probed through
  its includers by hand (S3285).
