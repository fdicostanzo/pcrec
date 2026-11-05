# crit-memfn-sp1e — LENS SEAM (manifesto principle 9; span_pick.md §The designer/emitter split)

Subject 9de5b5638 (lane/memfn-sp1e) vs base 20fb73159. Read-only; probes with
tr-subject/tr-base MF_TRACE pcrec, `-p rx --features all`, default arm/regime
unless stated. Scratch: /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1e/SEAM/out/<tag>/{x.c,err}.
No denylisted file was opened.

The question: can what crosses from "decide" to "render" be written to text
and read back by another process that renders the same C? Short answer: YES
for the E-find plan modulo stage-1-sanctioned crossings (listed under NOTED),
and 1e makes the crossing SMALLER (Table D's `drow` field and its parallel
text table are gone; one renderer index `bren` now carries find + resume +
file-scope text). The gaps are in the RECORD (trace) and in the SHAPE of the
T-FIND question, not in the bytes.

## FINDINGS

### SEAM-1 — the renderer row (third member of the 1e triple) is in no trace record; B-fn vs B-pair have EQUAL records and DIFFERENT C — CONFIRMED
- severity: doc/design (trace sufficiency); effort XS; blast radius: every
  E-find site whose method row is PAIR (trace readers: reach_equal, rows_check,
  any future plan-in/C-out golden keyed by the triple).
- where: memfn/src/compose.c:1140-1146 (FDROUTE/WPATH writers print
  `row->ct->row` = `E-find` and `row->id` = `window-search`, never
  `wf_brows[w->bren].row`); memfn/docs/trace_format.md (as changed, FDROUTE
  paragraph: "its pick is E-find's to render: B-fn, B-pair, B-memchr, B-walk,
  and since span_pick 1e B-hors" — names the renderer rows but no record
  carries which one rendered).
- repro (2 compiles):
  `tr-subject/pcrec -p rx --features all -o out/p11/x.c --pattern '(?i)qzx'`
  `tr-subject/pcrec -p rx --features all -o out/p42/x.c --pattern '(?i)qzx\b'`
  `grep -E 'table=(fd|wfE)|FDROUTE|WPATH' err | grep -v REACH | md5sum` is
  IDENTICAL (1b1d5b05…) for both: wfE END chosen=E-find; fd ROW D-hors
  PRED_FALSE, D1/D1c/D1w PRED_FALSE, PAIR CHOSEN; `FDROUTE row=PAIR
  arm=E-find`; `WPATH path=mass+pin arm=window-search fd=PAIR`.
  Emitted C differs in METHOD: p11 renders B-fn (`rx_mf1_ofsskip`,
  `rx_mf1_ofsskip__body`), p42 renders B-pair (inline two-stream leapfrog,
  `rx_mf1_ha/hb/wa/wb`). The only trace difference is an INDIRECT one: p11
  carries two `table=fn` selections (fn-pair BODY, PREFIX none) at the same
  site AFTER the WPATH line — the render-time fn_rows walk (ofs_fn_define_at),
  not a statement of the renderer row. Base (tr-base, 2 compiles) has the same
  gap (records equal, md5 b98613fb…), so it is NOT new — but 1e is the unit
  that declares the text keyed by (frame row, method row, renderer row), and
  the record holds only two of the three.
- reconstruction recipe today (undocumented): frame = wfE END (or composer:
  no wfE / E-stmt); method = FDROUTE row (pick is a function of the row:
  fd_pick_of ignores q); renderer = composer: FDROUTE arm (distinct ct rows
  pf_memchr / pf_memchr_bounded / pf_memchr_back / pf_walk / pf_walk_bounded,
  so the composer's triple IS recoverable); E-find: D-hors -> B-hors (also
  path `+hors`), D1/D1c -> B-memchr, D1w/R7w -> B-walk, PAIR -> B-fn iff a
  define-phase `table=fn` selection follows for the site, else B-pair.
- fix (XS, trace-only, no byte): print the renderer row on FDROUTE (e.g.
  `ren=B-fn`; composer: the arm, already there) and document it in
  trace_format.md; or state the inference recipe there. The plan-in/C-out
  golden the design names for the emitting face needs `bren` as an input.

### SEAM-2 — the composer's T-FIND walk now writes a D-hors ROW it can never answer: "not applicable to this asker" and "asked, false" print the same line — CONFIRMED
- severity: doc/design (trace semantics; new in 1e); effort XS-S; blast
  radius: every composer FIND define record (`table=fd`, phase=define), and
  under `--memfn=no-window-skip` every one of them prints `D-hors
  verdict=DENIED` too.
- where: memfn/src/finder.c:257 (D-hors first in fd_rows, no asker fact),
  :646-679 (fd_find's composer branch never calls hors_facts, so
  SF_HORS_WINDOW/DENSE are never set; `wf` NULL so `core` is UNSTATED and the
  use_none contract PASSes).
- repro (4 compiles): `--pattern 'abc'` and `--pattern 'a+b'` on tr-base and
  tr-subject. Subject adds, at the COMPOSER's site (a+b site 2, frame E-stmt,
  arm pf_memchr): `ROW table=fd … row=D-hors verdict=PRED_FALSE gate=PASS
  fields=-`. The window asker's record at abc site 1 (frame E-find) is the
  SAME four lines (SEL form=STMT op=FIND handoff=ASSIGN; ROW D-hors
  PRED_FALSE gate=PASS; ROW D1 CHOSEN; END chosen=D1). Different renderers
  (pf_memchr vs E-find's B-memchr); the asker is recoverable only from the
  frame (wfE END / FDROUTE arm), not from the fd record.
- why it matters on this lens: PAIR's asker-dependence is a STATED fact
  (SF_ASKER_PAIR, PRED_FALSE for the composer by the fact); HORS's is an
  ABSENT one (the composer states no window). See SEAM-3. A reader replaying
  the fd record cannot tell a sparse-window window site from a composer site.
- fix: either (a) let the asker fact cover HORS (SEAM-3), so the composer's
  D-hors ROW is PRED_FALSE for a stated reason, or (b) document in
  trace_format.md that since 1e every composer FIND record carries a D-hors
  ROW that is structurally false; (b) is XS.

### SEAM-3 — the asker fact is one bit ("renders PAIR") but TWO picks are the window family's alone (PAIR and HORS); HORS's asker-dependence is carried by the composer stating no window — CONFIRMED by reading, latent (no mover today)
- severity: design; effort S; blast radius: the day a composer asker states
  a window (unit 3.0, "the plan takes the frame", or a kit request that has
  the composer state window facts), D-hors can hold for it, fd_renderer
  (compose.c:276-293) has no HORS row, and select_arm REFUSES the site (LOUD,
  `no row serves this site (the finder row D-hors's routed pick)`), never a
  silent mis-render.
- where: compose.c:266-269 comment ("PAIR and HORS: the window family's
  alone"); finder.c:105 SF_ASKER_PAIR only; kit.h fd_stop comment ("THE ASKER
  FACT `renders_pair`").
- design reading: span_pick.md §The tables T-FIND names the asker fact as
  "the asker renders PAIR", so the subject follows the letter; the SEAM point
  is that the asker fact is really "the set of picks this asker has renderer
  rows for" (compose.c fd_renderers: LIBC, LIBC_BACK, WALK; window.c wf_brows:
  PAIR, LIBC, LIBC_BACK, WALK, HORS). Serialised, the T-FIND question should
  carry that set (or the renderer table's id) rather than one pick's bit;
  then PAIR and HORS are filtered by one mechanism and SEAM-2's D-hors ROW is
  false for a stated reason. Proposed as a 3.0 input, not a 1e defect.

### SEAM-4 — "one walk", but two question shapes: the composer's T-FIND question is derived from the mf_site inside the finder; only the window asker STATES its question (fd_stop) — CONFIRMED by reading; stage-1 acceptable, NOTED for 3.0
- severity: design; effort S-M; blast radius: the planner->emitter split
  (manifesto principle 9): a T-FIND question written to text today has two
  record kinds.
- where: finder.c:646-679. `st == NULL` (composer): find_facts reads the
  site's term[0] (SET or RUN), need from the span, scope from fd_scope; `st`
  non-NULL (window): set_facts(st->set, st->off), need REQUIRED, hors_facts,
  `renders_pair`, gate facts via `st->wf`. `renders_pair` is hard-coded 1 at
  the only window call (window.c:1844) and is implied 0 by `st == NULL`, so
  the asker fact is exactly `st != NULL`: it carries no information the
  branch does not already carry.
- why it is not a 1e defect: the design asks for ONE walk (done: one
  kit_walk over fd_table) and the asker fact (done); the question's shape is
  not specified, and the asker fact is a named exception until unit 3.0.
- suggestion: have select_arm state an fd_stop too (set/run of term 0, its
  offset, its need, renders_pair 0), so fd_find has one question builder and
  the record of a T-FIND question is one shape; a RUN span 0 needs a field
  fd_stop lacks (run_len 1 -> one member).

## NOTED (stage-1-sanctioned or pre-existing crossings; not defects)

Decide -> render crossing in E-find's plan (`struct wf_plan`, window.c:1247-1281):
- DATA (serialisable as is): off[], set[][32], core[], table[] (offer ids),
  ncore, clo/chi, hy_set/hy, wfloor, reads_table, stop_ix, stop_alone, grp[],
  nrun, hl, sh[256], libc, includes, bren.
- POINTERS: `row` (arm identity; serialisable as its id), `brow` (const char*
  into fd_rows[].id; serialisable), `fsite` (B-fn's translated mf_site,
  WRITTEN BY A PREDICATE: b_fn_holds calls translate() into fx->fn, window.c
  :1782-1784 — pre-existing at base :1848), `runs` (mf_pred*, built at define).
  All serialisable given an mf_site/mf_pred encoding.
- DEAD field: `w->pick` is written (window.c:1868) and never read; B-memchr
  renders LIBC vs LIBC_BACK from the stop offset's sign, coherent with D1/D1c's
  facts by construction. Pre-existing (base :1937, same).
- 1e SIMPLIFIES the crossing: `drow` and `wf_d_text` are gone; `bren` indexes
  one text table (wf_b_text: head, next, define) plus wf_b_find. Residual
  inline renderer dispatch outside the table: `if (w->bren == B_FN)` and
  `if (w->bren == B_PAIR)` (pair-state declarations) in wf_find_expr
  (window.c:2727, :2735) and wf_find_define (:2764) — keyed on the renderer
  row's identity, so not a re-derivation; a `decl` column would make the
  table whole (maintenance, XS, optional).
Re-derivations at render time (all pre-existing, sanctioned):
- B-fn's text re-walks fn_rows BODY and PREFIX (ofs_fn_define_at -> fn_select
  x2, ofsskip.c:672-675) under the render hooks, after b_fn_holds already
  asked BODY quietly (ofs_fn_serves) to choose B-fn: named exception
  "fn_rows BODY/PREFIX". The PREFIX rung (SIMD) is decided only here.
- E-stmt / E-func: T-FRAME's legacy predicate asks select_arm quietly
  (kit_legacy_serves, window.c:1564, includes the composer's T-FIND walk);
  mf_define then re-asks select_arm non-quietly on the translated site
  (compose.c:1075) for the arm: the frame row does not carry its method or
  renderer row. Sanctioned (T-FRAME text-time; compose arms[] named exception).
- wf_find_decide runs twice per E-find define (quiet in Table E's predicate,
  non-quiet in wf_prepare for the record); same inputs, same answer.
Pointers/callbacks/state into T-FIND (decide side, text-time until 3.0):
- fd_stop gained `rate` (the RAW handed table; D-hors's mass via kit_mass),
  `wf` (pointer to the window family's gate facts; its only consumer is
  D-hors's contract `core` CORED, which SF_HORS_WINDOW already implies) and
  `renders_pair`. All serialisable as values/classes. HORS_MIN reading the
  NONE row's uniform mass is the R2 named exception.
- frame callbacks at render: hooks `table_name`, `fn_name` (pcrec's), and the
  art-level first-use state (`art->includes`, mf_art_note_libc, runcmp's
  wused/wemitted, simd_inc): the design's [rev5 C3] order-dependence.
Target-language assumptions crossing back into the reply: wf_brows[].libc
("its text calls memchr") sets w->libc/includes, which reach mf_class
(wf_plan_class) — an emitter fact in the reply; B-hors adds libc 0, same as
base's no-row case. Pre-existing.
MF_CLASS_V 7 -> 8: pres_row/pres_led are POSITIONAL indices into the finder
row listing, so a FIND row inserted ahead of the PRES rows moves them (1a, 1f,
now 1e); ruled by the design (§Staging), noted as a seam whose value is an
index rather than a row id.

## PROBED-AND-HELD

- Composer triple recoverable from the trace: fd END (method) + FDROUTE arm
  (renderer; five distinct ct rows) — held on 'a+b' (site 1 parked, site 2
  E-stmt -> pf_memchr), 'abc' window E-find.
- E-find triple recoverable except PAIR's B-fn/B-pair (SEAM-1): D-hors sites
  print `FDROUTE row=D-hors arm=E-find` and `WPATH path=mass+hors fd=D-hors`
  ('[0-9a-f]{8}'); D1 sites (9 patterns), PAIR sites (21 patterns: 7 B-fn,
  14 B-pair) as expected.
- Method row -> pick is a function (fd_pick_of ignores q): no equal-row,
  different-pick pair exists.
- Asker fact equal-record pairs: composer (a+b site 2) vs window (abc site 1)
  give identical fd records; the asker is recoverable from the frame row (wfE
  END / FDROUTE arm), so the triple is not ambiguous — the fd record alone is
  (SEAM-2).
- fd_find's composer path keeps fd_route's refusals: out-of-scope -> no row;
  UNSTATED need -> `?need`, refused by select_arm (fd_renderer(UNSTATED) NULL).
- fd_renderers' `end_back -1` wildcard on LIBC_BACK: a non-zero end_back
  reaches pf_memchr_back's gate (end_back ZERO) and is refused, as base's switch.
- Base vs subject fd/wfD/FDROUTE records on 'abc', 'a+b', '(?m)^foo$': only
  the documented moves (wfD SEL/ROW/END gone; a D-hors ROW added to every fd
  FIND walk, composer included).
- pcrec compiles: 43 (of 250; counted by the probe wrapper).
