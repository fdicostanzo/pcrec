# critic_house.md -- memfn-s3-final, lens HOUSE (function/file level vs coding.md, style.md, addenda/kit.md)

Read-only; no compiles run (findings are from reading SUBJECT cc4f54eb2 in the review tree and the
diff 0d3765c87..cc4f54eb2). Paths below are under the review tree. memfn/src/ = M/.

### HOUSE-1  `pcrec_fact_span` is dead after the subject removed its one caller
- status: CONFIRMED (repro: `grep -rn 'pcrec_fact_span\b' src tests lib cli tools analyze` -> only the decl facts.h:529 and the def facts.c:616; BASE had the caller in known.c cc_exact's `pcrec_kit_proof_routed(...) ? pcrec_fact_span : pcrec_fact_span_stated`)
- severity: maintenance
- effort: S      - blast radius: src/facts (one function, one decl); the `used`-record semantics it carried are then unreachable
- where: src/facts/facts.c:616, src/facts/facts.h:529 (caller removed at src/gen/known.c:~258)
- detail: the retirement of the kit-proof lever left the recording variant of the span fact with no reader; the
  non-recording `_stated` twin is now the only one. The new known.c comment ("`used` stays the passes' record,
  facts_listing.md 4.1p2") keeps explaining a distinction the tree no longer exercises. Delete the function (or
  say why it stays) in the same change that retired its only use (coding.md 4.2 "editing is as important as writing").

### HOUSE-2  The kit-proof lever is left inert, with a comment saying so, instead of retired
- status: CONFIRMED (cli/main.c:1217-1219, src/core/internal.h:172-180 and 3900-3907, src/gen/known.c:~432)
- severity: maintenance
- effort: S-M      - blast radius: cli flag, PcrecHarnessOptions bit, KITPROOF trace field `routed=`, tests/kitproof, tests/memfn/site_census.py
- where: src/core/internal.h:172 ("INERT since D172 S3 ... Its retirement is filed (docs/dev/lanes/s3_report.md)"), :3901, cli/main.c:1217
- detail: `--harness=kit-proof` now changes no byte; `pcrec_kit_proof_routed` is read only to print `routed=%d` in
  a trace record. The tree keeps a flag, a bit, an accessor and a record column that cannot change anything, and
  three comments narrate the history ("through S2 it routed...", "inert since", "survives only as the spelling its
  callers still pass"). coding.md 4.2: history goes to docs with a pointer; a comment should say what the code does.
  The pointer given is a lane report (docs/dev/lanes/s3_report.md), not a durable doc and not a plan row.
  Either retire (callers: tests/kitproof/run_cover.sh:55, reach.sh:18, site_census.py:80) or state in ONE sentence
  what the lever still does. A flag whose only effect is a trace column is a latent "knob that does nothing".

### HOUSE-3  fd_find duplicates fd_route's fd_x setup and decide call
- status: CONFIRMED
- severity: maintenance
- effort: S      - blast radius: finder.c only
- where: memfn/src/finder.c:866-905 (fd_route) vs 925-950 (fd_find)
- detail: both functions do `fd_x q; memset; q.art; q.handle; q.site; q.pred_ix=-1; q.ff.kind=kind_cl(...);
  q.ff.layer=CL_L_OFF; q.ff.need; gate_in in={...,&q.ff,NULL}; gate_tctx tc={art,"fd",handle,MF_PH_DEFINE,&in,1,quiet,0};
  fd_decide(&q, FD_FIND, &tc, &d)`. The shared piece is "decide slot FIND for a prepared fd_x under hooks": a
  `static void fd_find_decide(fd_x *q, const mf_hooks *def, int quiet, fd_decision *d)` would hold the
  gate_in/tctx/decide triple and the fd_x init could be one `fd_x_init(&q, art, handle, site)`. S3 already did the
  right thing for the facts (set_facts / seek_facts were extracted so find_facts and fd_find share them); the
  decision half was not. A third caller (B4/B8 dispatch) would copy it again.

### HOUSE-4  Predicates that write state: b_fn_holds (new), e_legacy_holds (extended contract)
- status: CONFIRMED
- severity: maintenance
- effort: S-M      - blast radius: window.c Table B and E walks
- where: memfn/src/window.c:1672 (b_fn_holds calls `translate(b->d, b->w, 0, b->fn)` filling b->fn, the caller's storage); 1388 (e_legacy_holds, `translate(..., e->L)`)
- detail: a `holds` function is a predicate (the walk may ask it any number of times, in any order, quietly or traced);
  these two fill the plan's translated site as a side effect and the winner's later prepare reads that storage
  (`fx->fn->site` becomes `w->fsite`, wf_prepare re-translates L after the walk for the legacy case). The Table D
  predicates the same diff adds are correct: wf_dx is computed BEFORE the walk "the predicates only read" (window.c ~1620).
  e_legacy_holds is pre-existing and wf_prepare knows ("translate(d, w, eb, L)" is repeated after the walk), so the
  honest shape is: compute the translation (or its "serves" bit) before the walk into a wf_bx/wf_ex field, predicates read.
  b_fn_holds is the new instance and repeats the pre-existing sin. It also calls ofs_fn_serves (a full BODY walk of
  fn_table, gate-traced if quiet were 0) from inside another walk: a walk nested in a predicate.

### HOUSE-5  REPORT is keyed in predicate code, not in the contract rows the gate already reads
- status: CONFIRMED (code reading); severity as design-lite
- severity: maintenance
- effort: S      - blast radius: Table E rows (3), wf_prepare's refusal text
- where: memfn/src/window.c:1392 (e_legacy_holds `site_kind == MF_SK_REPORT`), :1417-1420 (e_generic_holds returns `site_kind != MF_SK_REPORT`), :1822-1830 (wf_prepare reconstructs "this was REPORT" with `!(v.r1 | v.r2)`)
- detail: `FLD_site_kind` is a contract column (WF_SERVES_REST sets it MF_ANY; finder.c's rows use KD_STOP exactly for this).
  The E rows' contracts could say `[FLD_site_kind] = ~CM(REPORT)` (E-func, E-stmt, E-generic) and the gate would
  decline, name the field in gate_describe, and need no predicate; E-generic's holds would then be the old `e_true`
  that the subject deleted, and wf_prepare's special REPORT message would fall out of the gate's description. As
  written, a consumer-kind rule lives in three places that must agree (two predicates + one message). Same family
  as memory `pcrec-general-mechanisms-not-special-cases`; the finder half of this diff did it the table way (KD_STOP, ct_*).

### HOUSE-6  The "is a window site" test is spelled three ways, one of them different
- status: CONFIRMED (spelling differs); whether the difference is a defect is SUSPECTED
- severity: maintenance
- effort: S      - blast radius: gate.c, compose.c, window.c
- where: memfn/src/gate.c:476 (`in->s->nalt || in->s->alts`, NEW in this diff), memfn/src/compose.c:941 (`!nalt && !alts && !wfloor`), window.c part_states (`p->nalt || p->alts || p->wfloor`)
- detail: three hand-written copies of one predicate; the new gate.c one omits `wfloor`, the other two include it. A
  site stating only `wfloor` (wf_check would refuse it, but gate classification runs on whatever site the host
  states) is "window" to the composer and "term site" to cl_table_ref. Name one helper (`site_states_window(const
  mf_site *)` in kit.h beside wf_check) and use it at all three. To confirm as a defect: a site with wfloor set and
  nalt==0 through mf_ask.

### HOUSE-7  d_hors_head ignores its `bound` parameter and re-derives the bound's text
- status: CONFIRMED
- severity: maintenance
- effort: S      - blast radius: window.c D-hors only (emitted bytes: `C + 0 >= N` becomes `C >= N` is NOT byte-identical, so this is an abi event if changed)
- where: memfn/src/window.c:2538-2552 (`(void)bound;` then `kb_printf(b, "if (%s + %d >= %s) break; ", rc->C, w->chi, rc->N)`)
- detail: coding.md 2.3 "use the file's own declared helper": wf_bound() already builds the loop bound; wf_find_expr
  computes it and hands it to every head as `bound`. D-one uses it (`if (!(%s)) break;`), D-hors takes the parameter
  only to (void) it and prints a second, differently-spelled spelling of the same bound (`C + chi >= N`, so chi==0
  prints `C + 0 >= N`). Either drop the parameter from the head signature (d_one_head is the only user) or use it.
  Same shape in wf_find_expr: `(void)want_value;` with a comment saying "always wanted" -- the expr callback
  signature is dictated by wf_frame, which is fine, but then the parameter is documented nowhere in its header.

### HOUSE-8  Comments narrate history in code, CLAUDE.md and enums (coding.md 4.2, style.md "Comments and headers")
- status: CONFIRMED
- severity: maintenance
- effort: S      - blast radius: comments only (no emitted byte)
- where (examples, all added or reworded by the subject):
  - memfn/src/finder.c:109-110 `1u << 12 was SF_PROOF_EXACT ... 1u << 13 was SF_STRETCH_CUBE, PAIR's scope before code review r2 R2-1` (tombstones for enum bits no code reads)
  - finder.c:74-77 ("the listing printed A3 as "RUN" from D2's retirement to D172 S3"), :26-36 header ("joined at the S3 code review (C1)"), :249, :856-862
  - memfn/include/memfn.h:1391-1396 (the whole `mf_preview` prototype slot is a RETIRED tombstone), :502 (still says "through commit 5 an art previewed it, mf_preview(art, "window-family")", naming an entry that no longer exists)
  - memfn/src/fields.def:~157 "RPT, the row that read it, retired at D172 S3"; plan_cost.def "landed at S3"
  - src/core/internal.h:172-180, 3898-3905 (HOUSE-2); src/gen/emit_dfa.c:4842-4846 "(the OFF arm: `composite`, the default before S3)"
  - memfn/src/window.c header lines 12-16 ("Since S2 commit 6 ... through commit 5 an art had to preview")
  - memfn/src/CLAUDE.md:15 and :21 (an orientation file listing "ids reserved ... PAIR added at the S3 code review's C1", "`mf_preview` is retired (D172 S3)")
- detail: the guide's rule is "invariants and why-not-the-alternative in code, history in docs with a pointer".
  Dead enum bits and a retired entry are best handled by deleting (git records them) or one line in
  memfn/docs/finder_history.md (which finder.c's own header already names as the log). Several of these cite
  review ids (C1, R2-1, R2-6, r1 C7, R2-7) that mean nothing without the denied review files; a reader of the
  code cannot follow them. Not a correctness issue; bulk of the comment-quality debt of this change.

### HOUSE-9  Stale/contradictory function headers introduced or left by the subject
- status: CONFIRMED
- severity: doc
- effort: S      - blast radius: comments
- where and detail:
  - memfn/src/window.c:2698-2703 `wf_plan_brow`: header says "E-find's Table B renderer row for the plan" but it returns `w->brow`, the FIND-slot row that DECIDED the stop (e.g. "D1", "PAIR"); the renderer row is `wf_brows[w->bren].row` ("B-memchr"...). kit.h:833 says the deciding-row meaning, so header and kit.h contradict. The struct field is also named `brow` while wf_brows[].row is the renderer's -- two things "B row".
  - memfn/src/CLAUDE.md:15 "`fd_find`: the window site, the stop's set, offset and stretch": `fd_stop` is {set, off}; the stretch left with r2 R2-1.
  - src/gen/emit_dfa.c:7540 `window_reply_ask` "Asked wherever the art previews the family (the default)": no art previews anything since S2 c6/S3.
  - memfn/src/window.c:2661-2665 `wf_floor_applies` is documented as "the family rows' applicability" and installed on BOTH wf_floor_arm and wf_find_arm; the name says floor.
  - kit.h:455-458 the reflowed wf_prepare header leaves a ragged "*legacy NULL; on a / row reproducing" line break mid-sentence.

### HOUSE-10  B-memchr renders memchr-and-store a third time (pffind.c, precheck.c, window.c)
- status: SUSPECTED (confirm: diff the three emitted shapes for LIBC with equal d on a STMT site; they differ only in frame)
- severity: maintenance
- effort: M      - blast radius: pffind.c pf_memchr_use (~253), precheck.c:230, window.c:2428-2447 (wf_b_search/wf_b_memchr)
- detail: the S3 r2 R2-6 fix correctly extracted `ofs_pair_text` for the PAIR leapfrog (kit.h:411, one renderer, two
  customers). B-memchr is the same situation for the FF_LIBC / FF_LIBC_BACK picks: pffind.c's pf_memchr /
  pf_memchr_back render exactly these picks for fd_route sites (`const void *q = memchr(s + lo, b, n - lo)` + store, the `q`
  local, the bounded variant, the k-below variant) and window.c re-writes the text with its own bound/raise handling.
  addenda/kit.md "One table per slot ... extend the table and call it" is about the FIND decision, which the diff now
  does through fd_find; the RENDERER of the same pick is still per-site-family. At least name the shared text
  function (memchr statement at `P`, length `N - P`, optional offset k) the way ofs_pair_text was.

### HOUSE-11  ofs_pair is a 13-string layout struct (altitude)
- status: SUSPECTED (judgment)
- severity: maintenance
- effort: M      - blast radius: ofsskip.c:245-262, window.c:2465-2478, pair_body
- where: memfn/src/kit.h:414-425 (`ofs_pair`), memfn/src/ofsskip.c:245
- detail: the extraction is right, but the parameter object mixes policy (names: subject, n, ha, hb, fresh, q, cand, miss)
  with byte-level layout (`ind`, `in2`, `nl`) so the callers pass `"        ", "    ", "\n"` and `"", "", " "`; a
  caller that wants a third layout has to know that `nl` is both the line end and the join. Layout strings
  in a data struct are the "emitted-text rules" hazard (anchor columns): the fn-pair callers' indent is now data in a
  struct 8 lines from where it is rendered. Acceptable as is for two customers; a `layout` enum {LINES, ONE_LINE}
  (two fields, owned by ofs_pair_text) would take the knowledge out of the callers. Also the single-line form emits
  `{ const void *...` with a leading double-space risk when in2 and ind are both "" (inspect the emitted text).

### HOUSE-12  Parallel row tables for one row (wf_drows/wf_d_text, wf_brows/wf_b_text), and a pick->row loop
- status: CONFIRMED (shape); design relevance left to the slot critic
- severity: maintenance
- effort: S-M    - blast radius: window.c Tables B and D
- where: memfn/src/window.c:938-953 (wf_drows), :2590-2597 (wf_d_text, index-coupled by `_Static_assert` only), :1693-1706 (wf_brows) and :2484-2488 (wf_b_text), :1667-1691 (b_*_holds), :1740-1744 (the first-match loop `for (fx->bren = 0; ...)`)
- detail: each row's data is split in two arrays in two places 600-1000 lines apart, joined by array index and a
  static assert (it is a good assert; the shape is still two edits per row). The Table B renderer loop is hand-written
  `for` over `.holds`, not the kit_table walk the neighbouring tables use, so Table B alone has no contract, no deny
  and no trace; and three of its four `holds` are one-line `pick == X` tests, i.e. the table is a pick-indexed
  map written as a first-match list. coding.md 4 question 3 (code-driven vs data-driven) both ways: a function-pointer
  field in wf_brows (and a forward declaration) removes the index coupling; a `[FF_x] = B_row` lookup removes the loop.

### HOUSE-13  Smaller duplications and constants
- status: CONFIRMED (each)
- severity: maintenance
- effort: S
- where and detail:
  - memfn/src/window.c:184 `two()` enumerates a set's members exactly as `shape()` (170) does and `count()` (161) / finder.c `popcount256` (pre-existing twin) count them; wf_b_memchr calls `shape`, wf_b_pair calls `two`. One `set_members(set, m, max)` would serve both.
  - memfn/src/finder.c:799 `set_facts` now sets SF_TWO_MEMBER for every FIND site with a two-member set, though only PAIR reads it and only under SF_WINDOW_STOP: harmless but the fact is computed for a route (fd_route) that has no row reading it (K35 shape: a populated field nobody counts).
  - memfn/src/plan_cost.def HORS_MIN 145822: a threshold "the geometric middle" of two samples (one winning cell), labelled PROVISIONAL with the evidence: label is present, so this is held, not a finding against the label; noted because memory `pcrec-suspect-tuning-constants` makes it suspect and the row's `box` column names one machine.
  - window.c `enum { WF_WHY_MAX = 320 }`: labelled UNMEASURED DEFAULT with its basis: held.
  - window.c wf_floor_define / wf_floor_use hard-code `5` parameters (pre-existing) next to the new E-find code that does not: not the subject's.

### HOUSE-14  wf_find_decide runs twice per define and its quiet flag is half-honoured
- status: SUSPECTED (confirm: MFTRACE output for one cover site shows Table D / FDROUTE records once; and count ofs_fn_serves calls)
- severity: maintenance
- effort: S      - blast radius: window.c wf_prepare 1795-1850
- where: memfn/src/window.c:1812 (`wf_find_decide(art, d, w, def, 1, fx)` always), :1838 (`if (r == E_FIND && !quiet && wf_find_decide(..., 0, fx))`)
- detail: the setup is computed quietly before Table E, then recomputed with quiet 0 only to get the trace and reach count.
  Every window site pays the quiet setup (fd_find, Table D walk, and for PAIR a translate plus ofs_fn_serves) even
  when a legacy row will win, and the E-find winner pays it twice. The comment "the define records E-find's selection"
  is accurate but the design is "run the decision twice to write one trace line". One decision with the trace flag
  taken from the *later* knowledge (record only if r == E_FIND) cannot work because the trace precedes the walk; hence
  better to separate the decision (pure, once) from the trace record (print from fx, once). Related to HOUSE-4.

## PROBED-AND-HELD
- Emitted text: the subject's only new emitted comment (d_hors_define, window.c ~2573) goes through the sink's
  cmt_open/cmt_close with fixed text (no pattern-derived byte), so the `*/` escaping rule (coding.md 3.2) is not engaged. HELD.
- Anchor columns / sabotage-anchor columns (coding.md 3.4): ofsskip.c's pair_body now builds the loop text via ofs_pair_text
  with indent strings "        "/"    ": checked the indents match the pre-change literals (8 and 4 spaces; lines 546-549); no
  re-indentation of anything in emit_dfa.c beyond the `.list` rows. HELD (not run; reading only).
- abi event: PCREC_ARTIFACT_ABI 84 -> 85 at emit_dfa.c:55 in the same diff as the byte-moving kit rows. HELD.
- `fd_route` signature loses `gphases`; every caller (compose.c select_arm, ask_sel) updated; no stale `kit_report_exact`, `fd_preview_step`,
  `fd_row_decides`, `art->preview`, `fd_nested_walk`, `FF_PROOF`, `SF_PROOF_EXACT` references remain anywhere in memfn/ or src/ (grep, 0 hits other than comments listed in HOUSE-8). HELD.
- Side effects in the new Table D predicates (d_hors_holds, d_one_holds) and e_find_holds: pure reads of precomputed state. HELD.
- Tables walked as tables: Tables A, M, D, E on kit_table/kit_walk; PAIR added to fd_rows[] as a row with a contract (ct_pair),
  KD_STOP masks, not an if in fd_find. HELD (modulo HOUSE-5, HOUSE-12).
- Prices fixed-point (addenda/kit.md): the diff adds no float; HORS_MIN is an integer ppm. HELD.
- Spec travels with the change: not my lens (spec hunks present in docs/spec per COMMON); not re-checked.
- Opened accidentally from the denylist: none. (window.c's own header cites docs/dev/lanes/wsc1_report.md; not opened.)
- Not covered: nothing was compiled or run (COMMON bars suites); all CONFIRMED statuses are reading/grep-level.
