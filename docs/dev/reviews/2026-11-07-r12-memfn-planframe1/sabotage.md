# SAB — memfn-planframe1
## Findings
### SAB-1 — row (D) is SAME for the natural spelling of "a second renderer list" (CONFIRMED by code reading)
Severity: maintenance/design (Goal 4's witness does not witness Goal 4). Effort: S. Blast: Goal 4 only.
§5 3.0a row (D); `tests/memfn/decider_census.py` :50-61 at a678d0a4e.
The backstop greps raw text for LIVE = `kit_walk(`, `< best`, `tie_takes`, `TIE_`, `pick_takes(` and the BYPASS
argmin spellings. Today's renderer lists are spelled with NONE of them: `fd_renderer` (`compose.c` :283-290) is a
`for` loop comparing `fd_renderers[i].pick == pick`; Table B's walk (`window.c` :1850-1851) is
`for (...) if (wf_brows[fx->bren].holds(&bx)) break;`. The census header itself says (:39-41) "What it cannot
see: a decider spelled in no BACKSTOP shape". So a planted second renderer list copied from either of today's
lists (the natural plant, and the natural regression) is GREEN; row (D) goes red only if the planter spells it
with `kit_walk(`, which `decider_census.py`'s own plant() self-test (:233-294) already proves. Classification:
SAME (check stays green) for a pick-keyed loop; red only for a kit_walk twin.
Fix: make every renderer lookup (search, stream, check, fused) go through ONE named accessor (e.g. a
`kit_render_row(` / per-table lookup function) and add that spelling plus `.pick ==` / `->pick ==` (and the
`.holds(` walk idiom) as LIVE/BYPASS shapes with HITS re-pinned; plant (D) as a copy of `fd_renderer`'s loop in an
unlisted function. General form: the census lists the renderer tables as members AND the backstop learns the
row-table walk idiom; trigger is this unit (it adds three such tables).

### SAB-2 — rows (B)/(C) are LOUD only while `select_arm`'s routed refusal survives, which §2.4 calls unreachable (CONFIRMED reach, SUSPECTED regression path)
Severity: design (witness depends on code the design invites deleting). Effort: S (one sentence + keep the
branch). Blast: rows B, C. §2.4 ("becomes unreachable by construction"), §5 rows B/C; `compose.c` :312-319,
`finder.c` :555-574, :656, `emit_dfa.c` :7096-7098/:8352-8354 at a678d0a4e.
Reach holds: a composer FIND site over a two-member set at offset 0 gets SF_SPAN0|SF_TWO_MEMBER (`set_facts`
:556-558); D1/D1w need SF_ONE_MEMBER, so with the renderability gate gone PAIR (facts SF_SPAN0|SF_TWO_MEMBER once
SF_ASKER_PAIR is deleted) decides; `fd_renderer` has no PAIR row, and `select_arm` returns NULL with `*row` set
(`if (rid) { ... return NULL; }`, :314-319: "no fall-back to the walk below"). pcrec's ask then hits
`pcrec_ctx_fail` ("the memfn kit refuses ... site"), so the compile is refused: LOUD. G2's composer sets include
case pairs/small sets (`g2_gen.c` :2935), and pcrec's byte-class PF rows state multi-member sets, so both
populations reach it.
The catch: the LOUD outcome lives entirely in that `if (rid)` refusal branch. §2.4 says the composer's refusal of
an unrenderable routed pick "becomes unreachable by construction". A build that deletes it as dead code, or
rewrites the lookup so an unmatched pick falls through to `kit_walk` (the walk below), turns (C) into SAME bytes:
the walk renders pf_walk/pf_walk_bounded, exactly R7w's text, so emit_sweep is identical too. And (B)'s plant is
underspecified: "the composer frame declared to render PAIR" means adding a (composer, PAIR) search renderer row,
and that row must name an arm. With arm NULL it is (C)'s refusal; with an existing arm (say pf_walk_arm) the
composer renders the walk under row id PAIR, bytes SAME, and only `mf_result.row` moves.
Fix: §2.4 states that `select_arm`'s routed refusal is KEPT as the observation point of (B)/(C) and is not
removed as unreachable; (B)'s plant names its row's arm as NULL/absent and asserts the refusal text; (C) asserts
the refusal message (rc != 0 AND message names PAIR), not just "corpus compile red".

### SAB-3 — row (A) goes red only if `wf_plan_brow` keeps returning T-FIND's row; §2.4 says rev 1 changes it to the renderer row / fused id, which would turn the CORRECT build red (CONFIRMED by code reading)
Severity: answer-of-the-check (green build red) / doc. Effort: S. Blast: row A, Goal 1's "check C stale 0",
`arm_fixtures --hash`. §2.4 reader table (formhash row), §2.6.4, §5 row A; `formhash.c` :287 (entry `pair`, row
"PAIR"), :466-469, :511; `window.c` :1866 (`w->brow = fx->brow`), :2817-2820 at a678d0a4e.
Today `wf_plan_brow` returns `w->brow`, T-FIND's deciding row id ("PAIR"), and `fh_render` refuses the id when
`strcmp(*row, e->row)` differs (:511). Under (A) the pair instance's stop loses PAIR from E-find's renderable set,
T-FIND walks on to R7w, `*row` = "R7w" != "PAIR", the id is refused: red, as the design says (LOUD in the check;
in the product it is a SILENT-MOVE: B-pair stops go to B-walk). But §2.4's formhash row says `[rev1]` the
accessor "returns the composed search renderer row, or B-fn's fused id". Built as written, the correct build's
pair instance returns "B-pair" (or the fused id), the entry still says "PAIR", and `pair` is refused at HEAD:
Goal 1's hash identity and check C fail in the green build, and (A) can no longer be told from correct. Either
the parenthetical is wrong (keep `wf_plan_brow` = T-FIND row, add a separate accessor for the renderer row, as
`wf_plan_bren` already is at :2824-2827) or the entry's `row` column must change in the same commit, and then
(A)'s red must be re-argued.
Side effect worth one line in §2.4: the renderable set is defined from the SEARCH renderer table only, so B-fn
(a fused row, matched first) is reachable only because B-pair's (E-find, PAIR) row exists. (A) therefore also
silently retires every fn-pair offset-skip site under E-find (caught by emit_sweep and G2's fn:48 floor, so not
a hole today), and a later unit that deletes B-pair once every PAIR is fused would silently kill B-fn. State the
rule: a fused row's pick counts toward the renderable set, or name the dependency.

### SAB-4 — the agreement checks (Goal 2, row E) compare the plan function with itself unless the define side is read from the define's OWN record; the design does not say which (SUSPECTED)
Severity: design (a control sharing a source with what it controls, learnings §3). Effort: S to state, M to
build. Blast: Goal 2 entirely, rows E and F. §4.1 ("Both `wf_prepare` ... and `mf_wdecide` read it"), §5 row E;
`window.c` :1191-1215 (`reply_of`, today used only by `mf_wdecide`), `compose.c` :1180-1186 (rule 2's re-ask
compares `ask_sel`'s class with `r->cls`, the define's stored class).
3.0a makes ONE internal plan function the source of both the define's selection and the reply's frame part.
The kit's MF_TRACE agreement then "re-asks with the define's site, hooks and call; every field compared". If
the define-side operand is built by calling `reply_of` (or the plan function) on the define's decision, which is
the cheapest spelling, then (E)'s plant in `reply_of` moves both operands identically: SAME, agreement green.
(E) is red only if the define-side values come from what the define actually USED: the site_rec's arm id /
`wplan->row` (Table E row), `wplan->brow` (T-FIND row), the stream renderer row the text was written with, and
the fused row (`wplan->bren == B_FN`, or the composer arm's id). The existing rule-2 check is the right
precedent precisely because `r->cls` is what the define stored, not a re-computation.
Fix: §5 3.0b states the define-side operand of the agreement is read from the site record the define kept
(`site_rec` / `wf_plan` members, `mf_defined`), never via `reply_of` or the plan function, and (E) adds a
second plant inside the PLAN FUNCTION's frame part (e.g. Table E row reported as E-generic while E-func
renders) to show that a plan-function fault that does not move text is still red there; if it is SAME, say so
and name the check that owns it (emit_sweep owns only text-moving faults).

### SAB-5 — Goal 2's G2 floors (each frame row >= 1, each produced stream >= 1) cannot see a wrong stream on one frame, and floors of 1 are K35-weak (CONFIRMED by reasoning over the tables)
Severity: design (check adequacy). Effort: S. Blast: Goal 2's tally, `stream` on every frame. §1 Goal 2, §5 3.0b
witness; `run_g2_win.sh` :82 (EFIND_FLOORS, measured-less-~10% floors), `g2_win_gen.c` :998 (`ef_hors` counted
from the TEXT, `strstr(ft, "_sh[256]")`).
SHIFT is produced by one frame only (E-find via D-hors); ONESHOT by E-find, E-generic and the composer frames. The
per-stream floors are AGGREGATE: a plant giving E-generic's sites SHIFT (or NONE), or E-func's NONE, keeps
ONESHOT >= 1 (E-find still has hundreds) and SHIFT >= 1 (D-hors still has ~110+). The floor of 1 also lets a plant
that misroutes all but one site of a frame pass; G2's own convention (:66-82) is measured-less-10%.
Plant that shows it: Table S's S-oneshot row reads "no search -> SHIFT" (E-generic only). Stream renderer has
no (E-generic, SHIFT) row, so if the floor's text is looked up the compile refuses (LOUD); if the reply's
`stream` is filled from Table S but the floor's text is written without consulting it (today's
`wf_floor_expr` hard-wires `resume_next`, :2314-2327), it is SAME for bytes and green on every Goal 2 floor.
Fix: tally (frame_row, stream) CELLS, floor each produced cell at its measured count less ~10%, and assert the
cells the tables cannot produce are 0 (SHIFT outside E-find; anything but ONESHOT on E-generic and the composer
frames; MASK everywhere). Cross-check each reply's stream against the text independently, as `ef_hors` already
does: `stream == SHIFT` iff the site's text holds `_sh[256]`. The MASK-0 assertion has no live witness
either (Table S cannot produce MASK, so 0 is structural): plant `reply_of` writing MASK for one frame and show
the tally reads the field.

### SAB-6 — on E-find, `fused` (B-fn vs B-pair) and `method` have no independent observer; no listed plant would catch them wrong (CONFIRMED by code reading)
Severity: design (the one distinction rev 0 named, §2.3 "B-fn has `fused` set and B-pair has it empty"). Effort: S.
Blast: row 1's reader of the triple. §2.3, §5 3.0b (G2 "holds the reply's frame part to `mf_defined` (`form_id` =
`fused` on E-func/E-stmt, `row` = `method` where the composer routes)"); `compose.c` :1303-1318 (`mf_defined`:
`form_id` is `r->arm->id`, "window-search" on every E-find site; `row` is `r->fd_row`).
`mf_defined` exposes neither E-find's T-FIND row nor whether B-fn rendered, so G2's hold covers E-func/E-stmt
only. On E-find the reply's `fused` and `method` are held only by the agreement check (SAB-4: same source) and
by Goal 5's resolution check, which accepts any listed id or "". Plants that stay GREEN on every listed check:
(i) `fused` left "" on B-fn (or set to the offset-skip form id on B-pair): both values resolve; SAME bytes.
(ii) E-find's `method` reported as "R7w" for a PAIR stop: "R7w" resolves in `mf_finder_rows`; SAME bytes.
(iii) `frame_row` swapped E-find <-> E-generic on REPORT sites: both resolve.
Row (J) is red only where `fused` is non-empty (E-func/E-stmt arms, B-fn): on E-find's other rows the plant writes
`method` = "" (the `fused` value), and "" passes a resolve-or-empty rule; on E-generic both are "" (SAME). No id
is both a finder row and a form id, so (J) cannot hide by coincidence.
Fix: G2 classifies each E-find site's TEXT, as its census already does (libc/walk/hors/pair/fn at :998 and
neighbours), and asserts per site: `fused != ""` iff the text calls `<prefix>_mf<h>_ofsskip`; `method` agrees
with the text class (PAIR iff two `memchr` streams, D-hors iff `_sh[256]`, D1/D1c iff one memchr, R7w/D1w iff a
walk); `frame_row` = E-find iff `mf_defined.form_id` is "window-search", E-generic iff "wf-floor". The resolution
check also asserts emptiness exactly: `method == ""` iff no T-FIND row decided (E-generic, BODY-decided E-func),
`fused == ""` iff the frame composes. Plant each of (i)-(iii).

### SAB-7 — row (M)'s pin is independent of the table for ONE row only; the ruling's text does not state the other rows it is said to pin (CONFIRMED against the ruling text in COMMON)
Severity: design (independence claim overstated). Effort: S. Blast: support table MASK/SHIFT cells. §1 Goal 4
("a pin written from the ruling's text"), §5 3.0a (pin = "memchr ONESHOT only; D-hors SHIFT only; PAIR and WALK
ONESHOT only"), row (M).
Frank's 2026-11-07 text says "libc memchr is one-shot only" and names SHIFT as a third stream. It does not say
D-hors is SHIFT only, nor that PAIR or WALK are ONESHOT only; those rows are the kit manager's/lane's reading,
the same author and the same commit as the support table. So the pin is independent for LIBC (and LIBC_BACK, by
"memchr") only; for WALK, PAIR and HORS it shares a source with what it controls. That matters exactly for the
cells no byte witness sees: every MASK cell (no frame has a MASK renderer, so admitting MASK for WALK or PAIR moves
no byte, no G2 count and no reply). (M) is planted on LIBC, the one row with an independent source, so it
proves the mechanism but not the claim. HORS/ONESHOT-type cells are fine: admitting ONESHOT for HORS flips Table S
to S-oneshot, which moves bytes (emit_sweep red; the `_sh[` control red).
The italic rows (vector block search, SWAR) are in the support table text but have no pin row and no T-FIND row;
if they are built as code rows they are D77 rows ahead of need with no witness; if prose, say so.
Fix: label each pin row with its source (ruling text vs derived basis: "a byte loop stops at one position",
"two memchr streams restart at c + 1"); for derived rows, the independent witness is a basis test, e.g. a
fixture that the WALK/PAIR renderers hold no block state across a rejection (their text has no mask variable).
Or narrow Goal 4's claim to "the LIBC row equals the ruling; the rest equal their stated basis".

### SAB-8 — rows (L)'s floor half and (N) are SAME unless the floor's text is looked up in the stream renderer table and a missing row refuses; §2.6.4 leaves `wf_floor_expr` hard-wiring `resume_next` (SUSPECTED)
Severity: design (witness reach). Effort: S. Blast: rows L, N; E-generic's stream. §2.6.2 (S-oneshot lists
"E-find, E-generic"), §2.6.4 floor row ("`resume_next` (`wf_floor_expr` :2314-2327)"), §5 rows L, N.
Today `wf_floor_expr` calls the resume spelling directly. If 3.0a refactors only E-find's loop to compose from
the tables (the zero-mover minimum, and what §2.6.4's per-row table suggests), then deleting the (E-generic,
ONESHOT) row (N) or changing S-oneshot's text (L) does not reach the floor: N is SAME (no refusal, no byte), and
L reaches E-find's sites only (still red via G2 answers, so L survives on E-find). N's stated red ("every floor
site is refused") requires (1) the floor's NEXT text to come from the stream renderer row Table S's pick selects,
and (2) a failed lookup to refuse. If L is reached on the floor too, `C += 2` in `wf_floor_expr` skips
candidates and G2's floor answers go red (the floor has ~110+ G2 sites, PATH_FLOORS floor:110). Classification
if built as stated: N LOUD, L SILENT-MOVE caught by answers; if the floor is not table-driven: N SAME, L
SILENT-MOVE on E-find only.
Fix: §2.6 states that every composing frame, E-generic included, takes its NEXT text from the stream renderer
row Table S's pick names, and that a (frame, stream) with no row refuses (rule 2 of §2.5.4). Add a reach line to
(N): G2 control "a DFA_SCAN site under no-window-search renders on the floor" (:689-690) is the one that turns red.

### SAB-9 — row (H) proves `pur_diff` compares `stream` only; `framed`, `frame_row`, `method`, `fused` can be left out of `pur_diff` and the control print with every listed check green (CONFIRMED by code reading)
Severity: design (check adequacy). Effort: S. Blast: Goal 3 for four of the five new members. §1 Goal 3 ("compares
every new field"), §5 row H; `arm_fixtures.c` :2204-2220 (`pur_diff`, field by field), :2312-2335 (control print,
field by field), `run_finder.sh` :144-178 (`purity_plant`: RED + control moved).
`pur_diff` is a hand-listed field-by-field compare, and the control print is a second hand list. (H) plants only
`stream`, so it proves only that `stream` is in both lists. An impure `fused` or `frame_row` (keyed on
`art->nsites`), with `pur_diff` lacking that field, is SAME on purity (green) and SAME on bytes.
Fix (general form, preferred): `reply_of` already `memset`s the reply (:1194), so `pur_diff` can be a `memcmp`
of the whole `mf_wreply` (with a named-field diagnostic only after a mismatch), and the control print a hex
dump of the struct; then one plant covers every member present and future. Otherwise add one `purity_plant`
per new member (four more lines in `run_finder.sh`). Trigger: this unit (it adds five members; the next unit
adds more).

### SAB-10 — `mf_wcall`'s values have no plant: UNSTATED's refusal, NONE's zero frame part and EMIT's DEFINE|USE gate are each unwitnessed (CONFIRMED: no listed row reaches them)
Severity: design (no-silent-default rule unwitnessed). Effort: S. Blast: §2.2. §2.2, §5 3.0b rows E-J.
None of (E)-(J) varies `call`. Plants that stay green on every listed check:
(i) UNSTATED treated as NONE (a presumed value, memory `pcrec-no-silent-defaults`): every caller states a value,
so no listed check calls with 0. (ii) NONE answers a frame part (`framed` 1): ASK-2's caller ignores the frame
part and pcrec reads none of it (§4.2). (iii) EMIT walking Table E under DEFINE only: identical to DEFINE on
every site whose hooks serve every use-time field, which is every fixture listed (the corpus's OFS ask is
DEFINE; G2 asks in the frame each site is defined, but the design does not say any G2 site is defined by
`mf_emit` with a row the use hooks fail).
Fix: three fixtures in `arm_fixtures`: call 0 -> -1; call NONE -> `framed` 0, ids "", `stream` NONE (a
`memcmp` against a zeroed frame part); EMIT on a site where `mf_emit` and `mf_define` select different rows
(the gate's DEFINE|USE declining a row, `compose.c` :255-258's case) answers `mf_emit`'s. Plant each.

### SAB-11 — the counting hook sees only the callbacks the fixture states; today's purity hooks state four of the six (CONFIRMED at `arm_fixtures.c` :2236-2237)
Severity: design (minor). Effort: S. Blast: Goal 3's "0 callback calls" for `member`, `on_cand`. §1 Goal 3, row G.
`pur_define`'s hooks state `fn_name`, `table_name`, `note`, `note_tag` (no `member`, no `on_cand`). A kit that
reads a hook only where it is stated (the norm: stated-ness is a fact the plan reads) never calls an unstated
one, so a plan that calls `member` or `on_cand` is invisible to a counting hook over these hooks. (G) is reached
(it plants `table_name`, which is stated): LOUD in the check. But Goal 3 lists six callbacks.
Fix: the framed asks' `def` in the counting fixture states all six callbacks (each a counter), and the plant
list gains one row per callback, or one parametrised plant over the six.

## PROBED-AND-HELD
- (A) reach: `formhash.c` :287 entry `pair` (row "PAIR"), :450-473 builds an E-find REPORT window site over `{X,x}`;
  `*row = wf_plan_brow()` = T-FIND's row (`window.c` :1866, :2817-2820); a plant removing PAIR from E-find's set
  gives "R7w", refused at :511. LOUD in the check while the accessor keeps today's meaning (see SAB-3).
- (C) reach and refusal: composer two-member sets reach PAIR once the gate is gone (`finder.c` :556-558, rows
  :280-294); `select_arm` refuses with no fall-back (`compose.c` :314-319); pcrec turns the refusal into
  `pcrec_ctx_fail` (`emit_dfa.c` :7096-7098, :8352-8354). LOUD (SAB-2 names the condition).
- (K): G2 counts hors from the TEXT (`g2_win_gen.c` :998 `strstr(ft, "_sh[256]")`), independent of the plan, floor
  hors:110 (`run_g2_win.sh` :82); the control at :692-694 renders a dense REPORT window and requires `_sh[`. Under
  (K) either T-FIND moves to D1/PAIR/R7w or E-find declines to the floor; both remove `_sh[`: red twice. In the
  product a SILENT-MOVE. HOLDS.
- (H): `purity_plant` (`run_finder.sh` :144-174) requires the planted --purity RED and the --purity-control print
  to DIFFER from the unplanted build's; the unrated half of the purity sites has no HORS (no rates, no
  SF_HORS_DENSE, `finder.c` :638-644), so correct = ONESHOT and the plant's SHIFT after one define moves the print
  once the print carries `stream`. HOLDS for `stream` (SAB-9 for the other members).
- (J): no finder row id equals a form id (`finder.c` row ids vs `formhash.c`/FORM_FLOORS ids), so method-from-fused
  cannot coincide; red wherever `fused` is non-empty (E-func/E-stmt arms, B-fn), SAME where both are "" (SAB-6).
- (F): ASK-3's suites are trace builds (`run_cand_oracle.sh` :87-91 builds `-DPCREC_CAND_TRACE`;
  `run_fallback_table.sh` :143-147); a STMT/ASSIGN frame selects E-stmt, not E-func, so `frame_row`/`fused` differ
  at every `ofs_site_define`: LOUD where reached, and (F) itself is the reach proof. HOLDS.
- (G): `pur_define`'s hooks state `table_name` (`arm_fixtures.c` :2236), so a plant calling it is counted: HOLDS
  (SAB-11 for `member`/`on_cand`).
- (I): G2's existing control (`g2_win_gen.c` :677-678) already shows a REPORT site under `no-window-search` answering
  -1 at ask and define; the framed-ask fixture mirrors it. HOLDS.
- (L) on E-find: `C += 2` skips candidates; G2's 3.3M answer calls vs `g2_win_ref.c` go red. HOLDS (floor half: SAB-8).
- (M): no byte, count or reply moves (no MASK renderer), so the pin is the only witness, and it is red for LIBC.
  HOLDS for LIBC (SAB-7 for the other rows).
- Support cell "ONESHOT admitted for HORS": Table S then picks S-oneshot for D-hors, bytes move (emit_sweep red,
  `_sh[` control red). Caught without the pin.
- Cases reasoned: 14 sabotage rows, 5 goal checks (G2 per-frame/per-stream floors, MASK 0, reply-id resolution,
  counting hook, support pin); code read at a678d0a4e in compose.c, finder.c, window.c, formhash.c,
  arm_fixtures.c, decider_census.py, run_finder.sh, run_g2_win.sh, g2_win_gen.c, emit_dfa.c, the two ASK-4 suites.
  No compiles were needed.
