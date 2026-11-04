# FIXIND (crit-stream3): fix-induced re-check of approach.md rev 3

Lens: FIXIND. Subject: subject/approach.md (rev 3). Review tree: worktrees/crit-stream3 (main 3f777330e).
Git reads only for part C (no compiles were needed for parts A/C; see PROBED-AND-HELD for the compile count).
Diffs saved here: m1.diff (02229045e src/), m2.diff (00c97769e src/), m3.diff (002810cac src/), m4.diff
(main...1cd8d220b src/ lib/ Makefile memfn/ cli/), m4_dfa.diff (its emit_dfa.c part).

## Findings

### FIXIND-1 (CONFIRMED; design; INDUCED (D1)): the p1build replay omits a HAND-SCHEMA change, so by §2.2's own cross-part list it is a contract event, not a pass
- §2.4 row 3 says p1build PASSES after X-0..X-5 (IF the walk renders as existing kinds), and lists `CandSel` as a P2 touch.
- `git diff -U0 main...1cd8d220b -- src/gen/emit_dfa.c` (m4_dfa.diff): `CandSel.point` (bool) is REPLACED by
  `unsigned char asker` with a new enum `CAND_ASK_UNSTATED/BODY/CALLER/SEED` and `CAND_ASKER()`; a new struct
  `CandGive { hand; asker; }`; `CandLocate.fin` (CT_* bits) is REPLACED by `CandGive gives[4]`; `CandFinish`
  gains `at_askers` "set on every row with an `AT` take cell (0 is UNSTATED, which the self-check refuses)".
  Existing LOCATE rows are rewritten (`.gives = { { CAND_HAND_NOMATCH, CAND_ASK_BODY } }` etc., m4_dfa.diff
  lines ~202-244), and `cand_takes` now reads `r->u.finish.at_askers & CAND_ASKER(s->asker)`.
- That is a new DIMENSION of the `AT` hand (who asks it), i.e. "a new ... hand type (P2 + P3 + P6)" by §2.2's own
  list, and it edits every existing FINISH row with an AT take cell and every LOCATE row. §4.1's hand map (C6's fix)
  has no asker either: the `pos` value `AT` cannot say "a per-seed point request" vs "the caller's".
- Also missing from the row: a FOURTH machine. `CAND_ML = 1u << 5` joins the path-member enum (internal.h hunk
  @-9206), `dfa_member_machines(..., const Dfa *out[4])` (was 3), and `dfa_table_name`, `dfa_scan_edge_name`,
  `dfa_uniform_folds` widen `mach[3]` to `mach[4]` (P3 name/fold writers).
- Consequence: 2-of-3-pass becomes at most 1-of-3 (02229045e, itself qualified by FIXIND-3). Fix: classify p1build
  as a cross-part event (hand type + machine), or name a split that makes the asker an existing `pos` field.
- Severity design; effort small (text); blast radius §0 F1 row, §2.4, §11.3 P-d's criterion. Subject §2.4, §4.1.

### FIXIND-2 (CONFIRMED; design; INDUCED (D1)): p1build touches P5 (the pipeline driver) and the machine build, which no split X-0..X-5 removes
- §2.3 gives `compile.c`'s "pipeline driver and its entries" to P5. p1build's compile.c hunks (m4.diff) are not
  only the ladder: `job_cleanup` frees `job->lmnfa.st/lmdfa.st/lmdfa.tab` (@-305); a new `lmwalk_build(cx, root)`
  calls `pcrec_build_nfa(... &job->lmnfa ...)` and `revend_build_one(...)` (@-533) and is CALLED from
  `compile_driver` "once the three machines are final" (@-3104). internal.h adds `Job.lmnfa`, `lmdfa`, `lm_built`,
  `lm_root` and `Ctx.lmwalk`.
- §2.4's table lists only "a ladder rung" for compile.c and "Ctx/Job fields" for internal.h. X-2/X-3 address the
  ladder and emitter-to-driver flags; none addresses "a row needs a machine built by the driver". In the end state
  the row's machine is `AUTO(M, rev, ...)`'s operand: someone must build M, and today that is P5's driver.
- Residual touch no split removes: P5 (driver build + cleanup) and P1/P3 (machine lifetime). Name an X-6
  ("machines are requested by the plan and built by one builder keyed by the record") or classify as cross-part.
- Severity design; effort small (text); §2.2 X table, §2.4 row 3.

### FIXIND-3 (CONFIRMED; design; INDUCED (D1)): 02229045e is not "two rows over existing hands": it also WIDENS an existing row to a new route, so check (b) fails on it in any end state
- m1.diff, `pf_handoff_applies`: the line `if (!s->forward || cand_finish_of(cx) == CAND_ROUTE_VM) return false;`
  is removed; NEXT's EXISTING `handoff` row's `.desc` changes to "forward scan of the caller-facing body OR OF A VM
  HYBRID'S INLINED PREFILTER"; `emit_unanchored` gains `if (pcrec_req_site_in_prefilter(cx)) ...` and the VM search
  body skips its own blocks then. So VM hybrids (which the two NEW rows never admit: they require
  `!pcrec_artifact_has_dfa_scan`) change their output through an OLD row.
- §2.2 check (b): "the stream listing of every corpus pattern the row does not admit is byte-identical". The hybrid
  patterns move, so (b) fails for 02229045e as one change; it passes only if split into "new rows" + "existing row
  widened" (the latter is not an F1 change at all). §2.4 says (b) "was NOT replayed"; this one is readable from the
  diff alone.
- Also in the same diff: `CandUse` (the req-use row record) gains FIELDS `whole` and `reenter` (m1.diff @-5605),
  read by the renderer (`pcrec_emit_req_attempt_reentry` emits only where `reenter`); an existing invariant trap is
  deleted from `vm_emit_search_body` ("internal error: the [K82] handoff reached a VM route with no prefilter");
  internal.h adds `Ctx.req_handoff_dropped` (driver -> row, not emitter -> driver: X-3 names only the latter
  direction) and two cross-emitter prototypes (`pcrec_req_site_in_prefilter`, `pcrec_emit_req_attempt_reentry`).
  The table lists none of these.
- Severity design; effort small; §2.4 row 1.

### FIXIND-4 (CONFIRMED; design; INDUCED (D1)): 00c97769e's cross-part classification is right for a reason the table does not give; its listed cause understates it
- §2.4 row 2: cross-part "correctly so: a new IR fact (P1 + P2)", and "its P3 share disappears IF FIND's renderer
  takes the landmark as an operand".
- m2.diff also shows: (i) `CandNode` gains `uint64_t under[CAND_NSLOTS], by[CAND_NSLOTS]` (@-8397): "A READ MADE
  UNDER DENY BITS ... let one cycle in the slot graph be acyclic in the rows". That is the WORLD mechanism itself,
  i.e. a new read-declaration field of the card-read graph: "a new backward card field is a P6 change" (§2.2);
  (ii) `VERIFIER`'s accepted hand widens from `CT_CAND` to `CT_CAND | CT_LOWER` (@-8493): an existing part's
  `accepts` changes (a seam contract change); (iii) a new scan-form enum value `PF_SCAN_LANDMARK` (@-5105) "a lower
  bound K bytes before a hit, never a candidate start, so no reader may price it as a candidate byte or set" (a new
  operand of the scan kind, a P3 event by the control-case rule); (iv) `cand_rows_selfcheck` rewritten.
- So even with no new IR fact, 00c97769e would not pass. The conclusion (cross-part) holds; the "its P3 share
  disappears IF ..." sentence does not (iii is a renderer operand), and §4.2 rule 2's claim that the world
  mechanism is "today's" should cite that it was born in this very change as a P6-class event.
- Severity doc/design; effort small; §2.4 row 2, §4.2 rule 2.

### FIXIND-5 (CONFIRMED; design; NEW): the control case invokes a cross-part rule §2.2 does not contain
- §2.4: "002810cac ... is a contract event by the cross-part list (a new operand of a kind is a P3 change)". §2.2's
  extended list is: a new kind, exit or hand type; a new kit operation; a new IR fact; a new kit-site id; a new
  backward card field. "A new operand of a kind" is not on it.
- And git: 002810cac touches `src/opt/scanedge.c` (105 lines) and `src/ir/dfa.c` (P1 by §2.3: `src/opt/*` except
  select_engine.c/derive.c), `src/gen/known.c` (P2), `emit_dfa.c`, `internal.h`. By the map its P1 share is the
  shape analysis. But §5.1 names `scanedge.c` and `vm_det_seq`/`vm_cursor_fits` as the TWO shape analyses the stream
  unifies, and §2.3 maps the first to P1 and the second to P2: one fact, two parts.
- Fix: add "a new operand of an existing kind (P2 + P3 + P6)" to §2.2's list; map scanedge.c with
  vm_cursor_fits (both P2, or both P1).
- Severity design; effort small; §2.2, §2.3, §2.4 control row.

### FIXIND-6 (CONFIRMED; design; INDUCED (D1)): X-2 as described is not sufficient: a rung is more than a row field
- §2.2 X-2: "a row FIELD declares whether, and in which order, the size cap may drop the row; the ladder walks the
  table's declared fields". 02229045e's and p1build's ladder hunks (m1.diff, m4.diff, compile.c) each also edit:
  `COMPILE_MAX_ATTEMPTS` (a global retry budget summed over rungs: 02229045e "+ 1" and "4 *" ("a FOURTH ladder run,
  since it restarts the size term"), p1build "+ 1"); the `FitAct` enum; `fit_act_verb`; the driver's `switch`
  (`case FIT_DROP_END_MARK: case FIT_DROP_HANDOFF: case FIT_DROP_LANDMARK_WALK:`); and `fit_seq_legal[]`, which is a
  PAIRWISE legality relation naming OTHER rungs (02229045e adds 6 pairs incl. `{FIT_DROP_PREFILTER, FIT_DROP_HANDOFF}`
  AND `{FIT_DROP_HANDOFF, FIT_DROP_PREFILTER}`, i.e. no total order; p1build adds 2).
- A per-row "order" field cannot express a two-way legal pair, the size-term restart, or the retry budget; each new
  droppable row would still edit the ladder's global state. Also each rung carries caller-visible text
  (`.note`, printed by `size_drop_note`; `.cells` = `ESEL_SIZE_CAP_RETRY` stamps), whose home after X-2 is unstated.
- Fix: X-2's end state must also derive the retry budget and the legal sequence from the row fields (or concede a
  rung-table append as a declared S shape).
- Severity design; effort medium; §2.2 X-2, §4.2 `size`.

### FIXIND-7 (CONFIRMED; doc; INDUCED (D2/D1)): X-3's and §4.2 `size`'s "14 emitter-written Job fields read by the ladder" does not reproduce
- The ladder's `applies` predicates (compile.c, all `fit_*_applies`, printed in full): they read `job->fit.chosen`,
  `fit.prefilter`, `fit.prefilter_collapsed` (driver/selection outputs), `job->revend_form` (written by the driver,
  compile.c:550/555), `job->anchored_ok` (driver, compile.c:419; the emitter only saves/restores it for a
  counterfactual, emit_dfa.c:11667-11669), `cx->end_mark_dropped`, and ONE emitter-written field,
  `job->req_handoff_vm`. The emitters write ~20 Job fields (`grep` of `cx->job->X =` in src/gen/*.c), almost all
  read elsewhere (entries, stamps, memfn forms), not by the ladder.
- "14" equals the rung count; the field count looks copied from it. X-3's scope is then one field plus whatever
  p1build adds (`lm_built`, written by the DRIVER's `lmwalk_build`), so X-3 is smaller than claimed, but the
  driver-written selection outputs (`fit.*`, `revend_form`) are a second channel X-3 does not name.
- Severity doc; effort trivial; §2.2 X-3, §4.2 `size` row.

### FIXIND-8 (CONFIRMED; design; INDUCED (D1)): X-4 leaves a second per-site key: the find-table ids and their rendered names
- p1build adds `DELEG_SITE(LMHIT, ...)` AND, in `memfn_sites.h`, `PCREC_FIND_LANDMARK` ("`<p>_landmark_bytes`
  ([LANDWALK]'s LMHIT)") plus an entry in `find_table_tag[]` (emit_dfa.c hunk @-6688). X-4 re-keys only the DELEG id
  by (operation, row); the `PCREC_FIND_*` table enum (`PCREC_FIND_NTABLE`) and `find_table_tag[]` (which spell
  emitted identifiers) stay per site, so a new row over FIND still appends there. Also touched:
  `tests/memfn/site_manifest.tsv`, `c4_allowlist.tsv`, `run_deleg_sites.sh`, `run_site_manifest.sh` (per-site pins
  X-5 does not cover: they are keyed by site, not strategy).
- Severity design; effort small; §2.2 X-4, X-5.

### FIXIND-9 (CONFIRMED; design; INDUCED (D1)): S3 "the abi line" is one of at least four abi readers every replayed change touched; X-1 moves only the constant
- All four changes (incl. the control) edit `tests/mech/sabotages/S693_abi_not_bumped.sh` (`SAB_BEFORE`/`SAB_AFTER`
  hold the number), `tests/codegen/run_recursion_identity.sh` (`FILEPIN` re-pinned at every abi move) and
  `docs/dev/history/abi_changelog.md`. CLAUDE.md's own row: "The site list is EVERY READER OF THE NUMBER, FOUND BY
  GREP". §2.2's S3 names only `PCREC_ARTIFACT_ABI`. After X-1 these readers still move with every byte-moving row.
- Either S3 lists the abi event's grep-found reader set as its declared shape, or check (a) fails on all three.
- Severity design; effort trivial; §2.2 S3, X-1.

### FIXIND-10 (CONFIRMED; design; NEW): check (a) as stated fails every real change on files the map does not cover
- §2.2 (a): "`git diff --stat` touches only files the map (§2.3) gives to P2, plus S's registries". The map covers
  src/, cli/, lib/, `docs/spec/*`, `Makefile`. Every replayed change also touches files with no part: per-directory
  `CLAUDE.md`/`NOTES.md` (a house Convention requires it: `tests/litscan/CLAUDE.md`, `tests/memfn/CLAUDE.md`,
  `src/gen/CLAUDE.md`, `src/facts/CLAUDE.md`, `lib/CLAUDE.md`), `docs/dev/plan.md`, `docs/dev/history/*`, lane
  reports, `docs/design/startset/s1/census_s1.py` (00c97769e and p1build), `scripts/emit_sweep.py` (00c97769e;
  named in the table but in no S), `tests/lib/san_excluded.txt` (p1build), and shared test runners
  (`tests/axes/run_axes.sh`, `tests/registry/run_registry_tests.sh` with its axes-coverage count 236 -> 242).
- Fix: declare an exempt set (docs/dev/**, per-dir CLAUDE.md/NOTES.md) and put shared counts into S4 by name.
- Severity design (the check cannot pass as written); effort trivial; §2.2.

### FIXIND-11 (CONFIRMED; doc; NEW): S5 "a new P2 file: one build line in Makefile" is the wrong shape
- `Makefile:117-121`: `LIBSRCS := $(wildcard src/core/*.c) ... $(wildcard src/gen/*.c) ...`: a new src file needs NO
  build line. p1build's Makefile hunk (`git diff main...1cd8d220b -- Makefile`) is a TEST registration
  (`'bash tests/codegen/run_landmark_walk.sh'` in `test-codegen`, plus a comment). S5's real shape is "a test-runner
  line", a test touch (S4), not a build line.
- Severity doc; effort trivial; §2.2 S5, §2.4 row 3 "the `Makefile` line (S5)".

### FIXIND-12 (CONFIRMED; doc; NEW): p1build's abi move is 93 -> 95, not 92 -> 95
- `git show 1cd8d220b:src/gen/emit_dfa.c | sed -n 55p` = `#define PCREC_ARTIFACT_ABI 95`; at the merge base
  5796317e9 (and main 3f777330e) line 55 is `93`. m4_dfa.diff's first hunk: `-93 +95`.
- Severity doc; effort trivial; §2.4 row 3.

### FIXIND-13 (CONFIRMED; design; INDUCED (B1)): the "report and position shift" folds two facts with opposite uses; `\G` is a POSITIVE admission fact today
- §4.1 item 2: "\K moves the reported start; \G pins the start position ... a consumer that does not apply it
  declines. Today that is lmwalk g1's two kind tests". Readers of `\G` in the review tree that USE it to admit:
  `cand_rows[]` BOUND rows `attempt-gstart` and `vm-gstart` (emit_dfa.c:10503-10517, predicates
  `cand_bound_gstart_*_applies` at :10108/:10115, `.map = CM_ONE`, listed as `vm-anchor-bound 2 gstart`), the seed
  table `%s_gstart_seed_state` (emit_dfa.c:14471, :14709); `cover_conj[]` C3 `no-gstart` (known.c:377, :186) is a
  decline. Kind tests of `A_GSTART`/`A_KRESET` also sit in src/facts (req.c:701-702, startset.c:139-140, endwin.c,
  startanch.c, widths.c), src/opt (possessify, revdet, mrl, atomic, callout, derive), emit_vm.c (19 lines).
- So "today that is lmwalk g1's two kind tests" names one consumer of ~20 files; and a single "shift" fact whose
  consumer card says "applies it or declines" cannot carry `\G`'s BOUND = ONE use. Sibling fact unstated: the start
  constraint (`\G`: start == startpos) vs the report shift (`\K`).
- Fix: two P1 facts beside `Nfa.erased` (a start pin, read positively by BOUND and seeding; a report shift, read by
  every consumer that reports a start); quote both reader sets.
- Severity design; effort small; §4.1 typing rule item 2, §6.0 superset owners.

### FIXIND-14 (CONFIRMED; design; INDUCED (B1)): the `Nfa.erased` reader trace misses three readers, two of which change behaviour when row G's BREF/VAR/CALL bit is added
- §4.1 lists readers `pcrec_vm_prefilter_window` (emit_vm.c:3774-3777), `pcrec_cand_lang_exact` -> `cand_project`
  (emit_dfa.c:13647-13651), lmwalk `g1`. `grep -n 'erased' src/*/*.c` adds:
  (a) `src/facts/kset.c:833` `if (nfa->erased) return PF_WHY_ERASED;` in `pcrec_span_walk` (a P1 reader; printed
  by `--emit-facts` as `decline:erased-nfa`, src/dump/facts_dump.c:115). Today a backref has NO machine
  (nfa.c:980-996 and `frag_row` at :585-603: "a row with ANY text and NO erase bit (a backreference, a variable)
  ... the same loud internal error"), so row G's arm creates a NEW machine population; kset's decline on it is
  correct, but the reader is unlisted, and the arm also changes `frag_row`'s KTEXT_ANY rule (`if (!row.erase)
  break;`): kindrow.def's A_BREF/A_VAR rows gain an erase bit, which every `pcrec_ast_row(a).erase` reader sees.
  (b) `src/gen/emit_vm.c:11311`: the `RX_VM_PREFILTER_LANG` stamp reads ONLY `NFA_ERASED_COUNT` ("atomic and
  lookaround erasures stamp "exact" here: F-13, a vocabulary mover filed for a later abi"). A BREF superset window
  would stamp "exact". This also means §4.1's evidence "today's exact windows for `a\Kb` and `\Ga(x)`
  (`RX_VM_PREFILTER_LANG "exact"`) are right" cites a stamp that says "exact" for LOOK/ATOMIC supersets too: it is
  not a witness of exactness (the argument holds via kindrow.def:64-66, not via the stamp).
  (c) `emit_vm.c:10442` `v->mrl_win = pcrec_cand_lang_exact(cx)` (MRL window), and the trace-build compare at
  emit_dfa.c:12034 (prints L/A/C letters only); and on p1build `compile.c:554` `job->lmnfa.erased == 0` (the ML build
  gate).
- Severity design ((b) moves a caller stamp's meaning when the arm lands; (a) a kind-row column change); effort
  small; §4.1, §6.0.

### FIXIND-15 (CONFIRMED; design; INDUCED (D2, C4)): "each rung is a new WORLD (the deny bits)" is false for the ladder; its world is an 8-cell record plus fired flags the table's `under`/`by` cannot express
- §4.2 D2 paragraph: "It fits rule 2 because each rung is a new WORLD (the deny bits)". The ladder's cross-attempt
  state is `FitSets` (compile.c:895-923): `dd`, `cr`, `sdr`, `flags_or` (the ONLY deny-bit cell), `carry` (measured
  figures copied forward because `job_cleanup` frees them), `latch`, `restart`, `comp`; plus `fit_fired` turned into
  `Ctx` flags at compile.c:2338-2343 (`anchored_dropped`, `end_mark_dropped`, `req_handoff_dropped`). Of today's 14
  rungs, `drop-handoff` has `.deny = 0` and works through `cx->req_handoff_dropped`, which `pf_handoff_applies` and
  the attempt rows read directly (m1.diff); `drop-end-mark`, `drop-anchored`, `drop-premul`, `drop-prefilter` also
  have `.deny = 0`. Only p1build's `drop-landmark-walk` uses a deny bit (`flags_or = PCREC_NO_LANDMARK_WALK`).
- So the acyclicity argument ("acyclic over (part, world) states, `fit_seq_legal[]` keeps the sequence monotone")
  holds only if the WORLD record is defined to include those cells and flags; rule 2's `under`/`by` vocabulary
  (deny bits) cannot name `req_handoff_dropped`. And `carry` is a backward fact (the failed attempt's measured size)
  that the `size` card field does not state as carried ACROSS worlds.
- Fix: define the world record (the deny bits AND the dropped-row set AND the carried figures) once; X-2's row field
  then writes "this row is dropped" into it. See Part B (the world family).
- Severity design; effort small (text); §4.2 `size` and the D2 paragraph, §2.2 X-2.

### FIXIND-16 (CONFIRMED; design; INDUCED (C7)): the FIXED marks are mis-homed: row G's cell drops three of today's CG_FIXED rows, and row 7 cites them as its own
- §6.2: row G give-up "—"; row 7 "FIXED (today's `handoff` rows, `CG_FIXED`)". Today's CG_FIXED rows
  (`grep -n '.contract = CG_FIXED' src/gen/emit_dfa.c`): `handoff` (:10285), `handoff-attempts` (:10294),
  `handoff-attempts-entry` (:10300): req-use rows handing `CT_LOWER`, i.e. row G's gates; and RETRY's `exact`
  (:10451), `clamped` (:10459), `retry-anchored` (:10467) on the VM route (`hyb-reseed`), which are the hybrid
  window's retry, i.e. row 7's. The enum comment (emit_dfa.c:9823-9828) names exactly these two families.
- Read as written, a stream built from §6.2 loses FIXED on the three handoff gates (row G "—"), which the
  [GIVEUP-DIFF] direction control then no longer holds to "never move". Also note: `CandRow.contract` has NO code
  reader today (`grep '\->contract\|\.contract\b'` finds only the comment at :9823), so the card's "FIXED give-up
  mark" is a declared fact for an instrument, not a backward channel any neighbour reads: counting it among F4's
  "eight channels" overstates the channel count by one.
- Fix: row G "FIXED on the req-use handoff gates (K82 Q10), — elsewhere"; row 7 "FIXED (RETRY's exact/clamped/
  retry-anchored)".
- Severity design (give-up surface); effort trivial; §6.2, §4.2, §0 F4.

### FIXIND-17 (CONFIRMED; design; INDUCED (C1)): "[LANDWALK-PRES] ... One row edit in P2 (F1)" contradicts the subject's own map
- §4.3: FIND asks the kit with the continuation's fixed span and the walk reads FIND's `proves`: "One row edit in P2
  (F1) through a declared read (F4)". FIND's site description is `find_site` / the `DELEG_SITE(LMHIT, MF_OP_FIND,
  DELEG_H(MF_H_ASSIGN), MF_TK_SET, ...)` row (p1build `memfn_sites.def`), and §2.3 gives `memfn_sites.def` and "each
  site description (`req_site_define`, `find_site`)" to the P3/P4 SEAM, not P2. Asking LMHIT with a span changes
  that site's description (a set-find becomes a set-plus-span find), so by §2.2/§2.3 it is at least a P2 + seam
  change, and a kit-site-shape change until X-4 (and possibly a kit operation event, P4) if the kit must test the
  span. The walk's skip of a hit whose +1 byte fails is also new walk text (`emit_landmark_walk`, P3) unless the kit
  does it.
- Fix: state the closure's real change set ("P2 + the site description; a kit event if the span is a new
  `mf_site` term"), or route it through X-4's end state explicitly.
- Severity design (an F1 claim); effort trivial; §4.3, §6.2 row 5.

### FIXIND-18 (CONFIRMED; doc; INDUCED (B2)): §5.3's "Its spec readers" list is hand-enumerated and incomplete
- §5.3 lists `match_api.md §6.3.3`, `tuning.md §3.1¶2`, `cli.md §1.11¶1`. `grep -n 'RX_ENGINE' docs/spec/*.md` adds
  readers whose WORDING is keyed on the engine value: `match_api.md` [6.3.1¶6] (":1926", "`#if`ing on `RX_ENGINE` is
  safe on every artifact; `#if`ing on a (b) macro such as `RX_VM_RUNGS` or a budget macro does not compile against a
  DFA artifact": the stamp SCOPE rule, which §5.3's budget-gate sentence must keep), [6.3.4¶2] (:2117), [6.3.4¶13]
  (:2260, `_DFA_MATCH` "Defined on exactly the artifacts whose `RX_ENGINE` is "dfa""), and `tuning.md` [2.44¶2]
  (:989, "ENGINE-SELECTING"). Same shape as D94's lesson ("a hand-enumerated list missed a fifth reader"): say "found
  by grep at the change", as §8 now does for the re-key list.
- Severity doc; effort trivial; §5.3.

### FIXIND-19 (CONFIRMED; design; NOT FIXED (C2) / NEW): the card omits two declared, checked `CandNode` facts, and its population claim understates `accepts`
- `CandNode` (emit_dfa.c, `typedef struct CandNode`; table at :9930) carries per NODE (all 13): `accepts` ("CT_* this
  node takes from a predecessor"), `asks`, `succ` (the hand graph), `reads`/`under`/`by`/`kask`/`kfields`, and
  `raise, rank, entry`: "THE PROGRESS CLASS of each RE-ENTERING successor edge ... `raise`: the edge strictly
  raises ... `rank`: a RELOCATE to the route's fallback LOCATE row, whose rank exceeds the handing row's", with a check
  ("`raise` edges acyclic, and every `rank` edge's inequality").
- §4.2 Population (C2's fix) says `accepts`' precursor is `CandRow.take`, "FINISH and RECOVER only". The node-level
  `accepts` exists for every slot. More important: the progress class is the plan-time proof that a re-entering hand
  terminates (today's backward edge), and the card has no field for it; §4.1's `reentry` carries only the run-time
  FLOOR. F4's "every backward plan-time fact today's tree carries ... has a home in the card" therefore misses it
  (nine channels, not eight), and `succ` (the producer-side graph) is the unstated sibling of `reads`.
- Fix: add a `progress` card field (raise / rank / entry per re-entering edge) and cite `CandNode.accepts`/`succ`.
- Severity design (F4); effort small; §4.2, §4.1 `reentry`, §0 F4.

### FIXIND-20 (CONFIRMED; doc; NEW): §2.3's map leaves files unmapped and puts the hand types in the wrong file
- Unmapped in the review tree: `src/parse/ks_analysis.c`, `src/parse/ks_lib.c` (excluded from P1 as "the
  knowledge-source rows (`ks_*.c`)" and given to no other row: P2's inputs list only `src/core/{ks_measures.*,
  ksrc*}`), and `src/gen/known.h` (only `known.c` is mapped). Every other src/ file is covered (checked by listing
  all eight src/ dirs).
- The seam's TYPES live in `emit_dfa.c`, not `internal.h`: the `CT_*` enum and `CAND_HAND_*` aliases
  (emit_dfa.c:9786-9812), `CandSel` (the asker on p1build), `CandNode`, `CandRow`'s `take`/`hands`. §2.3 gives P6
  only `callsite_rows.*` and "`internal.h`: the shared seam types", and lists `emit_dfa.c`'s straddle as "P2, P3, the
  seam [P3/P4], the abi number": the P6 share of emit_dfa.c is missing, which is why FIXIND-1's hand-schema change
  could be filed under P2.
- Line counts HOLD (16,008 + 14,201 + 3,722 + 9,342 = 43,273; internal.h 9,342).
- Severity doc; effort trivial; §2.3.

### FIXIND-21 (SUSPECTED; design; NEW): check (b) and X-5 key on the listing's `row`; today a row's listed POSITION renumbers when a row is inserted
- 02229045e changes an EXISTING row's listing entry: `.list = { [CAND_ROUTE_DFA] = { "req-use", 2,
  "scan-from-startpos" } }` -> `{ "req-use", 4, ... }` (m1.diff @-10083), because two rows were inserted above it.
  If the stream listing (or X-5's pin key) carries the ordinal, every pattern admitted by a row below the insertion
  moves, and check (b) fails for patterns the new row does not admit. Confirm: the listing's `row` field must be the
  row's NAME (as `.c` names are), never its ordinal; §2.2/§4.1 say only "its admitting `row`".
- Severity design; effort trivial; §2.2 (b), X-5, §4.1.

### FIXIND-22 (CONFIRMED; doc; NEW): small cite slips
- §0.1 lists five `mf_site_kind` values at memfn.h:414-415; the enum there has six (`MF_SK_REPORT` too; §8 has it).
- §2.4 row 3 "`emit_landmark_walk` (+149 lines)": the function is 117 lines in the diff (m4_dfa.diff from
  `+static void emit_landmark_walk` to its closing brace), plus a 45-line `DfaDir` hunk (`landmark`/`lmverify`
  directions, @-9384) the table does not list (two new P3 direction objects).
- Severity doc; effort trivial.

## Part B: standing questions

### B-1 Sibling of a family: rev 3's "re-plan over worlds" makes the ladder the FOURTH spelling of a counterfactual world (CONFIRMED by grep)
1. the start table's read worlds: `CandNode.under[]`/`by[]` deny bits (born at 00c97769e, FIXIND-4);
2. the ladder's cross-attempt state: `FitSets` cells + `fit_fired` -> `Ctx.*_dropped` flags (FIXIND-15);
3. lmwalk's counterfactual NEXT read, `pcrec_cand_lmwalk_next_cf` (p1build emit_dfa.c:11867-11882) behind
   `lm_next_read` ([SEL-WORLD]);
4. `pcrec_cand_drop_anchored_shrinks` (emit_dfa.c:11663-11671): save `Job.anchored_ok`, set false, re-derive the
   path, restore: a world made by mutating a Job field.
- General form: one WORLD record (deny bits + dropped-row set + carried figures) and one primitive "evaluate slot S
  under world W", read by the table's `under`/`by`, the counterfactual reads and the ladder. Unlocks: X-2 reduces to
  "row field `droppable` + writes W"; the C10 "one read table"'s `world` target becomes concrete; the `anchored_ok`
  toggle (a mutation-based counterfactual, the riskiest spelling) is retired. Trigger: X-2's build, or the next
  conjunct that needs a counterfactual (whichever first). Per memory, this is the "notice at three, propose
  unification" case; it is at four.

### B-2 Sibling: a second order vocabulary for droppable rows
- X-2's "a row FIELD declares ... in which order" would sit beside `fit_seq_legal[]`'s pairwise legality (FIXIND-6)
  and the `fit_rungs[]` array order (compile.c:954: "`fit_rungs[]`, which carries the order"): two order sources
  for one ladder. General form: the legal sequence derived from the row fields (a partial order), not declared
  pairwise. Trigger: X-2.

### B-3 Sibling: the hand's ASKER makes a third hand vocabulary
- Today: `CT_*` masks + `CAND_HAND_*` aliases (+ `CandSel.point`); rev 3 adds §4.1's per-coordinate `pos`; p1build adds
  the asker (FIXIND-1). General form: `pos` carries (coordinate type, asker) and the CT/CAND_HAND masks become its
  rendering; trigger: P-c (the first seam record), which must carry p1build's asker to stay byte-identical.

### B-4 General form of the F1 split list (unlock)
- X-1..X-5 are each "a per-row/per-site global registry becomes keyed by the row's own record". The general form is
  one rule: every registry a row appends to is keyed by `row` NAME and derived from the row table (ladder, kit-site
  table, find-table ids, pins, abi readers). Unlock: check (a) then needs no satellite list beyond "the row table +
  its own files". Trigger: the second of X-1..X-5 to be built (two instances justify the rule).

## PROBED-AND-HELD

- Part C git reads: 4 merges/branches diffed (02229045e, 00c97769e, 002810cac, main...1cd8d220b), every src/ hunk
  header read; 02229045e's 61 files, 00c97769e's 84, 002810cac's 31, p1build's 88 (non-lane) checked against the
  table's columns. HELD: the named P2 functions of all three rows exist in the hunks (`req_handoff_applies`,
  `req_use`, `req_landmark_admits`, `pf_handoff_applies`, `req_reentered`, `cand_nodes[]`, `cand_rows[]`;
  `cand_rows_selfcheck`, `cand_read`; `locate_landmark_walk_applies`, `cand_takes`, `cand_finish_sel`/`_ask`,
  `cand_locate_hands`); the P3 functions (`emit_req_handoff_rest`, `pf_emit_handoff`, `emit_unanchored`,
  `vm_emit_search_body` 5 hunks, `pcrec_emit_req_byte_check`, `pf_emit_ofs_bounded`, `dfa_member_machines`); seam
  hunks (`req_site_define` 3 and 5 hunks); the facts files of 00c97769e (facts.c/.def/.h, facts_derive.h, req.c);
  the abi moves 90->91, 74->75, 86->87 (control); lever bit 57 + axes.def row; the population-pin counts (startset
  3/5/3, codegen 5/13/15, memfn 3/4, registry 2, 15 new sabotages, 21 mech files).
- §2.3 counts: 43,273 / 16,008 / 14,201 / 9,342 exact; `fit_rungs[]` at compile.c:1268 with 14 named rungs; 11
  `DELEG_SITE` rows; `PCREC_ARTIFACT_ABI` at emit_dfa.c:55 (93) and its four in-file readers.
- Cited file:lines checked, holding: emit_vm.c:3774-3777, 8096-8110 (D49 gate, WORK sites), 13021-13025;
  emit_dfa.c:1415-1426, 1437-1452, 5674-5695 (contract/hands/needs/take), 8010-8027, 9786-9831, 9930, 11278-11287,
  13647-13651, 14554; internal.h:2413-2435 (the `Nfa.erased` definition quoted by §4.1 is verbatim);
  kindrow.def:64-66; memfn.h:767-770; memfn_sites.def:15-18; memfn_sites.h:308-316; dfa.c:1555-1557;
  callsite_rows.c:1-14. 
- B1's home check: `Nfa.erased`'s definition (language widening only) fits the language-superset fact; `\K`/`\G`
  stay out (kindrow.def A_GSTART/A_KRESET erase 0); readers that read the whole word (prefilter window,
  cand_lang_exact, kset span walk, lmwalk g1, lmwalk_build) are unaffected while no bit is added: HELD for today.
- B2's fix (exclude ACCEPT; D49's one budget gate) matches emit_vm.c:8096-8110 exactly: HELD.
- B4's re-sort of row 5 against all ten `lmwalk_conj[]` rows (p1build lmwalk.c:276-287): HELD (7 sound, 2 profit,
  1 fit; `finisher-dfa` at lmwalk.c:124-127; `g1` = gstart, kreset, then `erased == 0`, lmwalk.c:181-185).
- C4's wording ("acyclic over (part, world) states") matches `table-read-cycle`'s per-(slot, deny-bits) walk for the
  start table: HELD (the ladder half is FIXIND-15).
- §14.1: every one of the 36 crit-stream2 ids (A1-A8, B1-B4, C1-C12, D1-D7, E1-E5) has text in its claimed section (read in full: §0-§13); the
  substantive gaps are the induced ones above, not missing fixes.
- Compiles: 0 (git reads and greps only).

## Summary
- Part C: the F1 replay's table under-reports what each change touched. p1build changes the hand schema (the asker)
  and adds a fourth machine built by the P5 driver (FIXIND-1, -2). 02229045e also widens an existing row, so check (b)
  fails on it (FIXIND-3). 00c97769e is cross-part for more reasons than the one given (FIXIND-4).
- The splits are not sufficient as written. X-2 misses the retry budget and the pairwise order (-6); X-3's count is
  wrong (-7); X-4 misses the find-table ids (-8); S3 misses the abi readers (-9); check (a) has no exempt set (-10).
- Fix-induced: the FIXED marks are mis-homed (-16), the ladder's worlds are not deny bits (-15), the shift fact folds
  `\G`'s positive use (-13), the erased trace misses a stamp reader (-14). Part B: the world family has 4 spellings.
