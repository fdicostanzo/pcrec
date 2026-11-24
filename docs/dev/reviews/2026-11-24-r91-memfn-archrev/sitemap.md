# CRITIC sitemap: memfn-archrev (r91)

## Findings

### SITE-1 (CONFIRMED; maintenance; S) section B, B8 / ARV-5: the set-COUNT primitive is spelled 8 times, the note names 2
B8 says "count" is spelled twice (window.c:233 `count`, ofsskip.c:64 `set_count`) and C-19b is the command for it. C-19b's name list
(`count|in_set|set_count|span_byte|part_is_byte`) cannot see the others. Repro (R/tree/memfn/src): `grep -nE '__builtin_popcount' *.c`.
Observed count-of-a-256-set loops: finder.c:583 `popcount256` (+ inline :927), compose.c:705 and :775 (both inline), precheck.c:66
(inside `single_byte`, :61), presence.c:194 (`one_member`, :191), ofsskip.c:67, window.c:236. That is 8 spellings in 6 files, 3 of them
under helper names C-19b does not list (`popcount256`, `single_byte`, `one_member`), 3 inline. The first-member row (5 spellings) holds
(compose.c:813, finder.c:939, ofsskip.c:75, precheck.c:56 `only_byte`, presence.c:98). ARV-5's "deletes 8 local helpers and ~13 reads"
needs the list: the 13 reads of C-19a (13 lines, 10 files, held) include the BODIES of the helpers (window.c:231, k1_ref.c:17,
compose.c:806/813), so "8 helpers + 13 reads" double counts. Class: SHARED (note has it); the row is undercounted. Radius: ARV-5 scope.

### SITE-2 (CONFIRMED; doc; XS) section B, B1: "8 calls over 7 tables" is 9 calls over 8 tables
B1 row: "ONE walk, 8 calls over 7 tables (arms, fd, fn x2, runcmp, wfA, wfM, wfE, wfS)". C-7a at T prints 9 call sites
(compose.c:303, finder.c:577, ofsskip.c:555 and :580, runcmp.c:219, window.c:1300, :1310, :2055, :2734; the compose.c:193 and kit.h:1363 hits
are definition and prototype); C-7c prints 8 tables (1+1+1+1+4). The row's own list names 8 tables, and §0 says "8 declared first-match
tables", B-s4 says "(all 8)". kit_ask (3 calls) holds. Fix the row's counts.

### SITE-3 (CONFIRMED; design/doc; S) section A, A1/A2 and ARV-9 (A-s2) + the proposed register row: window.c :2860-3539 has no row and is placed in no file
A1 covers :152-1375 (planner), A2 :3539-4510 (text). A-s2 and the §6 register row split the file as `:78-1375` / `:1776-2860` / `:3539-4510`
(plus "plan_of/translate", which live at :1496 and :1670, so :1375-1776 goes with the plan). The span :2860-3539 (about 680 lines) is
in none of the three ranges and has no site row anywhere. C-2's own output puts `THE FRAMED ASK (plan_frame.md 2.2-2.3, unit 3.0b)` at
:2840 and `THE PARTS` at :3267. That span holds the kit's PUBLIC plan entries: `mf_wdecide` :3109 (the plan call §5 D8 says pcrec reads),
`wdecide_framed` :3055, `framed_refused` :3043, `reply_frame` :2981, `wf_frame_of` :2932, `wf_agree` :3193, `wf_has_parts`/`wf_part_site`/
`wf_parts_check`/`wf_parts_prepare` :3294-3493, `run_part_terms` :3384. Neither A1-A12 nor the register row says whether they are PLAN,
FRAME or TEXT, yet they are the production face of the seam and the first thing a "no-mover pure move" has to place. The "byte identity,
pure move" claim cannot be checked for a split whose ranges leave a fifth of the file out. Class: NEW-SEAM-adjacent (needs a ROW per
function group, and a home). Radius: ARV-9, owner question `window-file-split`.

### SITE-4 (CONFIRMED; maintenance; S) section C: the "shared pool parpool.py" has one importer; four G2 runners spell their own pool and subprocess helper
§4 intro says "The shared pool is `parpool.py`" and C7 classes the G2 runners AS-IS. Repro: `grep -lE 'parpool' memfn/tests/*.py memfn/tests/span_forms/*.py`
gives parpool.py and cards.py only (cards.py:5072 loads it by path). `grep -nE 'ThreadPoolExecutor' memfn/tests/*.py`: run_g2_simd.py:424,
run_g2_any.py:346 and :396, g2_vspan.py:696, and run_g2_mfind.py (3 pool hits). parpool.py's own header: "ONE ordered process pool for the kit's long
test runners" (owner ruling 2026-11-23, "reviewed for parallelism"). The subprocess helper is spelled per runner: `sh(cmd, timeout)` at
run_g2_mfind.py:214, run_g2_any.py:133, run_g2_simd.py:246; `run(argv, timeout)` at g2_vspan.py:134. Four spellings of "run a command with a
timeout", four pools, beside a rule-5-style "one question, one primitive" the note applies elsewhere (B5, B8). Class: SHARED (no row, no
suggestion; the §4 "Already filed" list names `mutb.py under parpool` only). Not asking for a build: a C row or a "leave it, trigger" line.

### SITE-5 (CONFIRMED; doc; XS) section D, D2 and D-s1 (ARV-2): the CLAUDE.md size claim does not follow from the command or the action
D2 says memfn/src and memfn/tests CLAUDE.md "sit at 12,277 and 12,263 bytes against the 12 KB limit"; D-s1 says moving the memfn.h changelog and
include/CLAUDE.md's history "brings memfn/src and memfn/tests CLAUDE.md back under the limit with room". C-27 prints 11539/12277/12263 as claimed.
But scripts/check_claudemd_size.sh:24 sets the limit at 12288 (1 KB = 1024), so both files are ALREADY under (by 11 and 25 bytes): "back under"
is wrong, and the files at risk are not the file D-s1 edits. Moving include/ history cannot change src/ or tests/ CLAUDE.md sizes. No suggestion
trims those two files. State what the headroom is (11 and 25 bytes) and either add the trim for those two files or drop the sentence.

### SITE-6 (CONFIRMED; doc; XS) section B, B10 and section A, A3: commands that do not print the claim they are attached to
(a) B10 "vrun.c -> ofsskip.c (3), runcmp.c (6); window.c -> ofsskip.c (7); precheck.c -> ofsskip.c (4)", command C-20c. C-20c's pattern lists only
`ofs_fn_(call|define|scan|applies|fall|fits)` and `run_cmp_render`. Observed: vrun.c prints 2 ofsskip symbols and 3 run_cmp_render* lines (+2
comment lines); window.c prints 2 ofs_fn lines and 1 run_cmp_render line. The counts DO hold as distinct symbols under a wider pattern
(`ofs_[a-z_]+\(|kit_selector\(` and `run_cmp[a-z_]*\(`: vrun 3 ofsskip and 6 runcmp; window 7 ofsskip; precheck 4), so the claim is true but C-20c
does not show it. Replace with the wider pattern.
(b) A3 lists five accessors; C-5's regex also prints `wf_plan_class` (window.c:4517, called from compose.c) and static `wf_plan_site` (:2721).
`wf_plan_class` is a sixth public function that takes a plan; A3 omits it.
(c) §6 "searched with C-34": C-34 prints register rows 3, 7b, 10 and 14 (grep for memfn|kit|mf_). The §6 table has 7b, 10 and 12. Row 12
does not match C-34's pattern (so it was found another way), and rows 3 (event "after S1 and kit K38-2") and 14 ("starts when kit K38-2 lands", done)
match but are not mentioned. Row 19 (one first-row walker; the note's B2 cites it) is also not printed by C-34. Say how rows 12 and 19 were found
and dispose of rows 3 and 14 in one line.

### SITE-7 (CONFIRMED; design; S) section B, B5/B6 and ARV-11 (B-s5): a fourth per-level table, `mfind_simd`, is outside the "3 spellings"
B5 counts 3 spellings of per-level vector vocabulary (vany ops_of :96, vrun ops_of :182, window.c:4395-4396) found by C-16 (`ops_of\[MF_NLEVEL\]`).
vrun.c:548-551 declares `mfind_simd[MF_NLEVEL]` (struct `mfind_lv` :536-543: lanes `vw`, mask shift, `mtype`, `ctz`, `ones`), keyed by
`LV_X86_W16`/`W32`, plus `mfind_swar`. It is a per-level C-spelling table (the mask's C type, the count-trailing-zeros builtin, the all-ones
constant) that a non-x86 level (NEON: 64-bit mask via `vshrn`, different ctz/ones) must also fill, and ARV-11's "one per-level spelling table"
would have to absorb it, else the B-s5 delete count ("2 of 3 spelling tables") is wrong (it is 2 of 4, or ARV-11 leaves one standing). The
regex missed it because the array is not named `ops_of`. The 22 `LV_X86_*` lines of C-17 do include :549-550 (vrun 14, held), so B6's count
is right and B5's is not. Class: SHARED (same row as B5).

### SITE-8 (SUSPECTED; design; S) section D: no row for the REPLY channels or the hooks (R-49: "the C text and stamps you return")
§5's intro names the seam's return side: `mf_sink`, `mf_class` (`MF_CLASS_V` 11), `mf_wreply`, the counted `mf_rows`, and the callbacks `mf_hooks`
(pcrec -> kit state: ref/fold/start/moved/run_cmp). D1-D10 cover: header size (D1), changelog (D2), `mf_site` span fields (D3), deny (D4), renderer
interface in `mf_pred` (D5), consumer kinds (D6), stamps (D7), plan callers (D8), a stray pcrec static (D9), the ritual (D10). No row gives the
CLASS of `mf_class`/`mf_rows`/`mf_wreply` (a reply struct pcrec reads field by field at emit_dfa.c, known.c, memfn_sites.c: `grep -rlE
'\bmf_class\b|mf_wreply|mf_rows' src` lists known.c, memfn_sites.c, emit_dfa.c, memfn_sites.h, known.h) or of `mf_hooks`. These are where
[SEAM-READER-CENSUS] ("every mf_* seam member has a kit reader or a listed trigger") actually applies, and the note makes that row the
event for D4/D5 without classing the sites it would count. Confirm by a grep of readers per `mf_class` field against memfn.h's field list.

### SITE-9 (SUSPECTED; design; S) section B: the window-to-arm bridge (Table E legacy rows) has no row
B intro names `kit_legacy_arm`/`wf_stmt_row`/`wf_ren_arm` as the path by which a window plan reaches an arm, and D5 covers the `mf_pred` fields it
fills. The bridge itself, `THE SPAN FORMS` + `TABLE E's legacy rows: the plan as today's row's site` (window.c:1463-1776; `translate` :1670,
`kit_legacy_serves` compose.c:311, `kit_legacy_arm` :326), is the one place where the planner's output is turned back into an old-field site and
dispatched through `select_arm`. It is the strain behind ARV-12 (D5) and it is a CHAIN (arm-by-arm legacy test), yet B1-B11 have no row. Not
checked further: whether `kit_legacy_serves` is a first-match walk over `arms` (it calls the same `arm_table`) or a second chain.

## PROBED-AND-HELD
- Commands checked at T: all of C-1 .. C-37 and C-28b (38 commands). Held as claimed (print what the note says): C-1 (6 sizes), C-2 (wf_plan at
  window.c:1391, kit.h:1183), C-3 (0), C-4 (0), C-6 (doc ref), C-7b (3 kit_ask), C-7c (1+1+1+1+4), C-7d, C-8 (5 argmins + 1 double call at
  :956-958), C-9 (all seven symbol counts and both edge directions), C-10 (72, 11), C-11 (12 rows; FL_KEY only at definition and listing;
  consulted read :1598, no writer), C-12 (9, 2 keys), C-13 (9), C-14 (4-way hand list), C-15, C-16, C-17 (22 lines: vany 2, vrun 14, window 6),
  C-18, C-19a (13 lines, 10 files), C-21a/b/c/d (1; 15; 5 equality sites; memfn_sites.c:42), C-22, C-23 (6543, 163), C-24 (no src/cli/lib
  file), C-25 (7 runners), C-26a (48), C-27 (238; 11539/12277/12263), C-28 (11 fields), C-29, C-30 (4 kit + 3 pcrec files), C-31, C-32 (9:
  emit_dfa 8, known 1; mf_ask 4, wdecide 3, pres_ports 1), C-33 (emit_dfa.c:1395), C-35, C-36 (:308), C-37a (0), C-37b (finder.c:977), C-28b
  (targets.c only). Not held or not showing the claim: C-7a (SITE-2), C-19b (SITE-1), C-20c and C-34 (SITE-6), C-16 (SITE-7).
- 44 inline file:line cites checked against R/tree line text (decide 1274, :1300, :1310, cands :419, kit_pick_takes :147, mf_wdecide :3109,
  wf_plan_site :2721, kit_byte_rate/kit_mass/kit_run_set/kit_run_decide at presence.c:47/75/85/245, fd_find :689, cmp_eval :526, fd_lookup :481,
  key_expand :447, ren_find :2231, select_arm :265, arms :135 (12 arms), fn_rows :496, rows :108, reach_print :907, kit_selector :643, :4465,
  vany_selector :189, kit_walk :193, mf_stamps :1733, measures_check :1017, consulted :1598, translate :1670, memfn.h :537 and :513-514, :308,
  formhash :320/:369, deny walk compose.c:171-172, window.c:473-476 and :3046): 44 of 44 held.
- Plan-row drift claims: [SP1E-RENDERER-TABLE] asker fact has 0 hits (held), but note that the five renderer tables are still FIVE tables
  (ren_skel/search/stream/check/fused, window.c:2306-2447), against the row's text "ONE renderer table keyed by (frame, pick, layer)"; "looks
  done" is true of the asker fact only (git log --grep gives no landing commit by tag; only 6dc54e383, a report citation). [KN-CARRIERLESS]:
  0 KN_ bits, needs_names "PEAIMN" remains, no commit by tag (half done: held). [SP1D-ARGMIN]: 5 argmins, no sixth member (held; trigger
  "stage 3 row 1 or a sixth", the note quotes only the second half); [SP1D-KITSPLIT-SEAMS]: still not-started, window.c holds kit_pick_takes
  and kit_run_member while presence.c holds kit_mass (held); [KIT-POLICY-TABLE], [FH-INTRIN], [PICK-IDIOM], [SEAM-READER-CENSUS],
  [MEMFN-UNBOUNDED-SPANS]: all STATE:not-started with no landing commit by tag, consistent with the note.
- Own-list sites that the note has: the 8 kit_tables, 12 arms, 12 fd rows, 15 options, 9 costs, 5 first-member spellings, deny channels (B11/D4),
  parpool/cards.py, formhash entries/shapes, the DELEG callers in emit_dfa.c/known.c.

CRITIC COMPLETE
