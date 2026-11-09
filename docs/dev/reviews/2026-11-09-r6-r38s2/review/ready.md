# READY — r38s2

## Findings

### READY-1 — the REQ_BYTE STAMP is not rendered by `pcrec_req_pick`; its member comes from `req_run_member`, which K38-2 retires (unnamed reader)
- CONFIRMED (quoted). `src/gen/emit_dfa.c:15830-15832` (build tree 404cff6ea):
  `pcrec_sb_stamp_str(c, g->upper, "REQ_BYTE", pcrec_fact_stamp_req_byte(cx, req_run_member(cx, pcrec_fact_req_run_stated(cx))));`
  and `src/facts/facts.c:919-927` `pcrec_fact_stamp_req_byte(Ctx*, int member)` returns `r->bytes[member]` of the CUT window
  (`r->len >= 2 && r->mask[member] == 0xFF`). The sheet §4.1 row "none -> `<PREFIX>_REQ_BYTE`" says REQ_BYTE "stays pcrec's
  pick: `pcrec_req_pick` ... returns the byte of `pcrec_find_run_scan_index`"; §4.3 retires `ReqRun.idx/bytes/len` and
  `req_run_member`. Neither table names `pcrec_fact_stamp_req_byte` nor the 15831 call site, and the stamp does not go
  through `pcrec_req_pick` at all today. Also: Goal 2's measurable "`pcrec_find_run_scan_index` called only from
  `pcrec_req_pick`" is false of today's tree (its ONLY caller is `pcrec_req_window`, `src/facts/req.c:841`; `pcrec_req_pick`
  reads `run->idx`, req.c:873) — the sheet does not say K38-2 MOVES the call into `pcrec_req_pick`.
  Comment text that states the retiring contract: emit_dfa.c:15845-15847 ("`<PREFIX>_REQ_BYTE` is exactly `bytes[idx]`").
- Severity: maintenance/doc (a K38-2 builder following §4.1 leaves the stamp reading a retired member; compile error,
  not a silent answer change). Effort: text, 2 lines in §4.1/§4.3. Blast: K38-2 pcrec half. Sheet §1 Goal 2, §4.1, §4.3.
- Fix: §4.3 row "`pcrec_fact_stamp_req_byte(cx, member)` + emit_dfa.c:15831 -> render the `req_byte` fact (no member)";
  §4.1/Goal 2 say the scan-index call moves from `pcrec_req_window` into `pcrec_req_pick`.

### READY-2 — C1's skip-half witness `barbaz` on `barbaq barbaz` cannot fail: the near-miss differs at the SCAN position, which the find itself tests
- CONFIRMED (compile). `W/build/pcrec --engine=vm -p rx -o bb.c --pattern 'barbaz'` (review tree 404cff6ea):
  `RX_REQ_RUN "62617262617a@5"`, `RX_REQ_WHY "emitted"`, and the run part is
  `memchr(subject + pos + 5, 122, n - pos - 5)` ... `cand = q - subject - 5` ... `rx_w4(subject + cand) == rx_w4("barb") && rx_w4(subject + cand + 2) == rx_w4("rbaz")`.
  The scan is position 5 (`z`). On `barbaq barbaz` the find never yields candidate 0 (`q` at offset 5 is not `z`), so a
  renderer that drops "the compare of the last claimed position" (position 5, the near-miss's differing position) still
  yields only candidate 7: the plant answers (7,13), equal to libpcre2's (7,13). No difference.
- §2.4 C1 row ("subject built FROM the reply, a near-miss differing at that position: `barbaz` on `barbaq barbaz`, expected
  (7,13), plant (0,6)"). The generic rule also fails whenever the last claimed position IS `scan` (the default prior's
  rarest byte is often the last). Fix: the near-miss differs at the last VERIFIED position that is NOT `scan` (here e.g.
  position 4: `barbbz barbaz` with the planted renderer dropping position 4's compare -> (0,6) vs (7,13)); state "a
  verified position other than `scan`, read from the reply".
- Severity: check (a control that cannot fail; reaches only at the skip's unit, so not a K38-2 blocker). Effort: one
  sentence. Blast: §2.4 C1, §3.4's witness list, §6 P1.

### READY-3 — K38-1's caller check ("`kit_run_member(` called only from `run_decide`") contradicts the two callers the sheet KEEPS
- CONFIRMED (quoted). `kit_run_member` has three callers at 404cff6ea: `memfn/src/presence.c:158` (P3, moves into
  `run_decide`: fine); `memfn/src/window.c:880` `run_member()` (`int exact = r->verify == MF_VERIFY_NO; int bj =
  kit_run_member(d->rate, sets_at, r->set, r->len, exact, NULL).pos;`), which serves BOTH pcrec's fabricated verify-YES
  pre-check site (`req_run_member`) AND `mf_wdecide`'s verify-NO prefilter member that §2.5 keeps as "a second, kept
  decider for a different site"; and `window.c:1498` translate's RQ-2 ranking (`kit_run_member(..., k ? &r : NULL)`, the
  `after` filter, ranking every position), which `run_decide(rates, opts, span) -> (has_scan, scan, ver)` cannot serve.
  Goal 2 and the K38-1 row both say `kit_run_member(` is called ONLY from `run_decide` ("a counted caller check"); built
  as written the check is red on the tree the sheet wants (the §2.5 decider and RQ-2 still call it), or the builder routes
  the prefilter member through `run_decide` (contradicting §2.5's "kept") and must widen `run_decide`'s signature for the
  exact restriction and the ranking.
- Severity: check/design (K38-1 cannot pass its own stated check). Effort: text: name the counted callers
  (`run_decide`; `run_member`'s verify-NO branch, §2.5; translate's ranking, RQ-2) and make the count 3, or say which
  ones move. Blast: §1 Goal 2, §5 K38-1 check column, §2.5. Unchanged by 3.0a (same three call sites at e95cd7aef by
  name; `kit_run_member` count 13 on both trees).

### READY-4 — K38-1's per-reader tie plant on S1095's witness cannot be "counted per reader": it trips pcrec's `req_run_member` agreement error, and the twin-mass reader is tie-blind on that witness
- CONFIRMED (quoted + compile). Witness `-e utf8 abcd`: `RX_REQ_RUN "61626364@3"` on both routes (default `dominated`;
  `--engine=vm` `emitted`, `RX_REQ_HANDOFF "0"`), i.e. an all-tie run resolved rightmost. K38-1 routes "the window
  family's member for pre-check run parts" through `run_decide`; that member is what `req_run_member` asks
  (`emit_dfa.c:1067-1074`: `mf_wdecide(...)` then `if (w.run_member != r->idx) pcrec_ctx_fail(... "the window family's run
  member %d is not the run window's own index %d")`), and K38-1 keeps it (it retires at K38-2). `req_run_member` runs on
  EVERY artifact with a run (the REQ_BYTE/REQ_RUN stamps, `emit_dfa.c:15831`, `:15859`). So a leftmost tie plant in
  `run_decide` makes every tie compile die with that internal error: the plant "fails", but no artifact exists in which
  "layout, part text, twin mass" can each be seen to move. Separately, the twin's mass (`presence.c:205-212`) multiplies
  the masses over `[at, at+len)`, which for a run of <= 8 positions is the whole run whatever the scan: tie-blind on `abcd`.
  Only a run over 8 positions with a tied STRETCH (S1096's `(?i:x)abcdefg(?i:y)` family) can move the twin mass.
- §5 K38-1 "the plant that makes it fail" column. Fix: state the observable (the K38-1 plant is caught by
  `req_run_member`'s agreement check, which K38-1 keeps as its pcrec-side control, PLUS per reader under a run > 8 with a
  tied stretch for the twin mass), or name a second witness for the twin reader. Severity: check. Effort: text.

### READY-5 — committed sabotages K38-2 moves that §5's "existing sabotages" column does not name (S448, S1548, S1700, S280; S1546 suspected)
- CONFIRMED (quoted anchors/reach at 404cff6ea; compiles):
  - **S448** (`src/gen/emit_dfa.c`): `SAB_BEFORE` is exactly `ofs_test_of`'s `t->run_o = w->run_lo; t->run_len = w->run_len;
    t->run_bytes = r->bytes + (w->run_lo - (pin.o - pin.at));` (emit_dfa.c:7421-7423), the lines §4.2 rewrites (the
    run pin reads the WHOLE run, `ReqRun.bytes` retires). Anchor text deleted -> the row errors at REACH_ONLY.
  - **S1548** (`memfn/src/compose.c`, "mf_lever accepts the pres-window lever and sets nothing"): its reach runs
    `pcrec-harness --harness=pres-window ...` and greps `rx_reqrun(subject, subject_length, search_from)`; §4.3 retires
    the lever, the harness bit and the axes arm. Its natural successor is the new `run-tie-left` lever (K38-2a), unnamed.
  - **S1700** (`emit_dfa.c:1597`, `int keep = handoff && req_use_whole(cx) ? nrun - 1 : 0;`): the two-part form
    (`nrun` 2: window + whole) that Q5 retires; its reach greps `RX_REQ_RUN "733a2f2f7777772e@` on
    `(https://www\.(?:acme|hooli)\.(com|de)/[^"?\s]*)` `--engine=vm`, whose whole run is 12 positions
    (`req_whole_run 68747470733a2f2f7777772e`): Q2 moves the stamp to the whole run, so the reach goes red.
  - **S280** (`src/facts/kset.c`): reach greps `RX_REQ_RUN "2f61626364782f75@6/fffffffffffeffff"` on `/abcd[xy]/user`
    `--memfn=no-window-search`, whole run 11 positions (`2f61626364782f75736572/...`): Q2 moves it; and its anchor
    function `pcrec_run_pin` is §4.2's run-pin reader (whole run).
- SUSPECTED: **S1546** (`memfn/src/ofsskip.c` `if (t->kind == MF_T_RUN && x->lead_len) {`, the R-30 LED compare): reach
  greps `memcmp(subject + cand + 1, "bcdefghi", 8) && rx_w8(subject + cand) == rx_w8("abcdefgh")` on
  `(a)(b)...(i)\9` (whole run 9, window `bcdefghi`); the lead is pcrec's cut window inside the whole part, which K38-2
  retires; confirm by asking whether `lead_len` survives `run_decide`'s one extent.
- The sheet says fates are "checked at build with `REACH_ONLY=1`", which would surface S280/S1700 (reach) and S448
  (anchor) at build, but §5 claims each moved sabotage is NAMED with its fate; these five are not. Severity: check/
  maintenance. Effort: 5 rows in §5's K38-2 cell. Blast: K38-2.
- Method: scanned all 1198 `tests/mech/sabotages/S*.sh` `SAB_BEFORE` texts for the retiring names and all reach probes for
  moving stamp literals (REQ_RUN on runs > 8, `reqrun_whole`, `pres-window`).

### READY-6 — in-tree checks and goldens that K38-2 (and K38-1) move, not named in §4.3/§5 (the brief's "every check that compares a golden with its source")
- CONFIRMED (quoted, review tree 404cff6ea). Named by the sheet: `tests/memfn/c10_presence.tsv`, `structural_check.py`
  KNOWN_READERS, `limits_check.sh:161` (PCREC_MAX_REQ_RUN_EMIT is in its list), `run_axes.sh` INTERNAL_ARMS. NOT named:
  1. **[FINDINGS] B2 reader witnesses**: `tests/findings/gen_adversarial.py:27-28` declares reader `c2b` = "RX_REQ_RUN
     before '@' — the emitted 8-byte window" and `c2a` = the '@' index; `tests/findings/witness/witness.tsv:9-10` pins
     `w-c2a github_pat_[0-9]+ 6875625f7061745f@7 / 6769746875625f70@7` and `w-c2b (a|b)+foobarbazquux 7262617a71757578@3 /
     666f6f6261726261@0` (default AND moved values, "a reader that stopped reading the rate is red"), plus the fire bundles
     `fire-c2a`/`fire-c2b` in `tests/findings/adversarial` (the SAME dir C4's all-tie regime reads with `-I`). After Q2
     the part before '@' is the whole run, rate-independent: reader c2b has no rate to read and its witness reds by
     construction; c2a's reader becomes the kit's `scan`. Fate needed (c2b retires with `pcrec_find_run_window_start`;
     c2a re-meant), with the spec rows already in §4.4's findings.md hunk.
  2. **`tests/codegen/run_prechecks.sh`** [4.5]/[4.5b]/[4.5c] (lines 911-933: the 11-byte run's truncation window
     `6875625f7061745f@7`, `"hub_pat_", 8)) return cand;`, "the truncation window rule ... moved") and :1522
     (`7e237e237e237e23@6`); two `reqrun_whole` asserts.
  3. **The R-30 lever's checks**: `tests/memfn/run_presence.sh` section D (`LEVER = "--harness=pres-window"`, `ASK =
     "rx_reqrun_whole(subject, subject_length, search_from)"`, "K35: every witness moves") and
     `tests/compound/run_lever_fence.sh:48-51` (its ALLOW list names run_presence.sh and S1548 for this lever).
  4. **Q5 block-name readers** (`_reqrun_whole`): `tests/codegen/reqcube_check.py:274-291` ("no rx_reqrun_whole block
     carries the search" is a red), `tests/memfn/routing_shape.py:38` FUNC_SUFFIXES, `tests/partlayout/writers.tsv:32` A7
     regex, `tests/memfn/arm_fixtures.c:178`, `memfn/tests/g2/g2_simd_gen.c:568-569` (G2's longest-FUNC-name sizing pin
     `\x01q_reqrun_whole`), `run_dfa_stamps.sh:292`, `run_encoding_checks.sh:644`.
  5. **K38-1**: `tests/memfn/decider_census.tsv:56` (`kit_run_member` "asked by run_member, P3's run scan and translate's
     ranking") and `:69` (`kit_pres_picks:run-window` part row, anchor `kit_pick_takes(&bw,`) both move when P3's window
     moves into `run_decide`; the sheet names only the ADDED `mf_wdecide` row (§2.5).
- §5.1's populations are counted by `emit_sweep` over artifacts; these are the checks whose own expectations must move in
  the same commit (else K38-2's `make test` is red on items 1-4). Severity: maintenance/size (K38-2 is L; this list is
  part of its cost). Effort: a table in §4.3. Blast: K38-2 (items 1-4), K38-1 (item 5).

### READY-7 — pcrec readers of the window-vs-whole landmark choice and of the cut window's TEXT, not in §4.1/§4.3
- CONFIRMED (quoted, 404cff6ea):
  - `req_use_whole` (`emit_dfa.c:8961-8964`, FIRST's row field `.u.use.whole`, declared on the `handoff-attempts` row
    `emit_dfa.c:10441` `{ REQ_USE_HANDOFF, .whole = true, .reenter = true }`) and its readers `req_handoff_k`
    (`:8971-8975`, K = `whole_maxoff` where whole, else `req_landmark_maxoff`), `emit_req_handoff_rest` (`:1172`,
    `whole`/`run` choose the emitted comment "before its whole run / run window / landmark byte" and set
    `Job.req_handoff_vm`, read by `compile.c:1225`), and `req_site_define`'s `keep = handoff && req_use_whole(cx) ? nrun - 1
    : 0` plus its internal error "the handoff keeps the whole run, but the pre-check's parts do not compare it"
    (`:1597-1602`). With one run part (Q5) and K = `whole_maxoff` (Q1) the window-vs-whole distinction these encode is
    gone: the `.whole` column of the FIRST table, `req_handoff_k`'s branch and `keep` either collapse or are re-meant.
    The sheet's §4.3 K row names only `facts.c:318-335`/`req.c`; §4.1 names `emit_req_handoff_rest` only as a reader of
    the assigned `c`. A declared start-table column is involved (memory `pcrec-decisions-as-first-match-tables`), so
    its fate should be stated.
  - `req_note_run` (`:1219-1250`) prints the cut window's LENGTH and BYTES ("every match ... contains the %d bytes \"...\"")
    under `PCREC_CMT_NONESSENTIAL`: a mover on the `-fcomments` arm (emit_sweep's c-default/c-vm `-fcomments` streams)
    on every run over 8 positions; not among §5.1's four populations.
  - `pcrec_fact_stamp_req_run` (`facts.c:911-917`) and the `req_run` listing row (`facts.c:828-830`) take `@` from
    pcrec's `idx`: covered in substance by §4.1/§6 Q7, fine.
  - `pcrec_req_run_masked` (`facts.h:116`) has NO caller at the build tree (grep: definition only): dead, retires with
    the window (trivial).
- Severity: maintenance/size. Effort: 3 rows in §4.3 + "the `-fcomments` arm's run note" in §5.1's population list.

### READY-8 — C4's regime (a) cannot fail its plant, and K38-2a's `run-tie-left` lever cannot show a moved scan before K38-2 (pcrec's agreement check kills the compile)
- CONFIRMED (compile + quoted). (1) All-tie regime: `(cd W && ./build/pcrec -I tests/findings/adversarial
  --analysis=uniform -p rx -o u.c --pattern foobar)` -> `RX_REQ_RUN "666f6f626172@5"` (default prior: `@3`): ties resolve
  RIGHTMOST in pcrec's `pcrec_find_run_scan_index`, and K38-1/K38-2's `run_decide` "REPRODUCES today" (rightmost). So in
  regime (a) alone the kit's `scan` and pcrec's index are EQUAL on every run, and C4's plant ("the stamp fed
  `pcrec_find_run_scan_index`'s index") emits the identical stamp: no red. Only the lever (b) separates them, and the
  lever needs ties, which (a) supplies: the reaching regime is "(b) UNDER (a)", not "(a) and (b)". (The stated reason
  for (a), "default-prior ties fall on the SAME byte", does not bear on an OFFSET check.)
  (2) K38-2a lands BEFORE K38-2 with the lever acting on `run_decide`, which (K38-1) also answers the window family's
  verify-YES member that `req_run_member` cross-checks against pcrec's index (`emit_dfa.c:1071-1074`, `pcrec_ctx_fail`
  "the window family's run member %d is not the run window's own index %d"), called for every artifact's stamps
  (`:15831`, `:15859`). Under `--harness=run-tie-left` at K38-2a every compile of a run with a tie dies with that internal
  error, so plant C's "reach witness ... shows no moved scan offset" can only be read at K38-2 (when `req_run_member`
  retires), or K38-2a must state that the lever's pcrec arm is exercised only in G2 (kit-side) until K38-2.
- §2.4 C4, §5 K38-2a plant C, §5 Order. Severity: check (C4 as worded has a dead regime; K38-2a's plant C has no
  observable at its own unit). Effort: two sentences. Blast: K38-2a, K38-2.
- SUSPECTED, same family: W-K3's G2 form ("admission bit for K in {-32..-1} equals its bit at K 0") only reds the unsigned
  plant on a site whose K-0 bit is 1 (`presence.c:219-221`: at K 0, `landmark = (1e6 * m > 1e6 * h)`; unsigned K -1 gives
  `k*h >= 1e6` -> 0); the row should require rates with `m > h` so the K-0 bit is 1. And C2's "the reply says `ver_len`+1"
  plant at K38-2a has no `mf_class.run` yet (K38-2 adds it): say G2 reads `run_decide`'s return there.

### READY-9 — the five-pick shadow loses pcrec's side on `scan`/`window`/`rwin`/`rwhole`; its witness table and comparator plant are unnamed, and "the records read the reply's extent" makes them self-compare
- CONFIRMED (quoted). `req_pick_shadow` (`emit_dfa.c:11229-11336`) records pcrec's pick against the kit's port:
  `int n = run->whole_len, ps = w->at + req_run_member(cx, w), ks = k.run_scan; ... pick_rec("scan", ps, ks, ...)`;
  `pick_rec("rwin", w->at, kw, ...)`; `pick_rec("rwhole", pw, kwh, ...)`, with `PCREC_PICK_PLANT` hooks. Its witnesses
  `tests/memfn/pres_pick_witnesses.tsv` (28 rows: `scan` 4, `window` 3, `rwin` 1, `rwhole` 2, `landmark` 2, ...) are
  run by `tests/memfn/run_pres_picks.sh` and must "AGREE (the kit's port answers pcrec's own pick)", with pcrec's value
  "written HERE from the pick's documented rule"; S1093 (`emit_dfa.c`, "the five-pick comparator reports agree whatever
  the two answers are") guards the comparator. At K38-2 pcrec has no own scan, window or whole-run keep (§4.3 retires
  `req_run_member`, `ReqRun.idx/at/len`, the K66 part); §4.3 says the `window`/`rwin`/`rwhole` records "read the reply's
  extent", which leaves both columns of each record from ONE source (learnings §3) or one column with nothing to agree
  with. Not named anywhere in the sheet: `pres_pick_witnesses.tsv`, `run_pres_picks.sh`, the `scan` record, S1093.
  The `landmark` record is handled (§3.2, both mass terms on the reply's extent: that one keeps two sources, pcrec's
  margin and the kit's twin).
- Fate options for the sheet to pick: retire `scan`/`window`/`rwin`/`rwhole` records and their witness rows, naming C2
  (text classifier) and C4 (artifact offset) as their successor controls; S1093 stays on the surviving records.
- Severity: check/maintenance. Effort: one §4.3 row + the sabotage cell. Blast: K38-2.

### READY-10 — S1107's fate is filed under K38-1, but `pres_layout_check`'s RUN half is still a live two-source check at K38-1 (it retires only with pcrec's cut at K38-2)
- CONFIRMED (quoted). K38-1 is "NO seam move": pcrec still cuts its own window (`pcrec_req_window`, `req.c:840-852`,
  `pcrec_find_run_window_start`) and states its parts from it (`req_run_tests` -> `ofs_test_run(&t[0], r->bytes, r->mask,
  r->len, m)`, `emit_dfa.c:1101-1106`). `pres_layout_check`'s run half (`compose.c:704-718`) compares those pcrec parts
  with the kit's `pk.run_window`/`pk.run_scan` (`kit_pres_picks`, which K38-1 routes through `run_decide`): "its run part
  is not the WINDOW its presence link verifies". So at K38-1 the RUN half CAN disagree (a `run_decide` stretch or tie
  change against pcrec's unchanged cut), and it is exactly the check that would catch K38-1's own S1096 stretch plant.
  The sheet's §5 K38-1 cell says "S1107 (`pres_layout_check` unchecked): its RUN half can no longer disagree, so
  re-aimed onto the head/rest halves, or retired"; §2.4's own reason for retiring the half ("pcrec lays out no run
  window") is K38-2 content.
- Consequence: retiring/re-aiming S1107 at K38-1 removes a live control one unit early; and (with READY-4) K38-1's
  plants on `run_decide` are observed as this define-time refusal or `req_run_member`'s internal error, not as per-reader
  byte moves. Fix: move S1107's fate to K38-2's cell; at K38-1 name `pres_layout_check`'s run half and `req_run_member`'s
  agreement as the controls that red K38-1's plants.
- Severity: check. Effort: move one clause. Blast: K38-1/K38-2 sabotage cells.

### READY-11 — rev 1's derived run PART ("`need`, `nterm`, ... UNREAD and must be 0") hits two refusals on `preds[]` that §5.1 does not list as moving
- CONFIRMED (quoted, 404cff6ea). `memfn/src/compose.c:466-474` `pred_kinds()`, run by `site_check` over EVERY
  ALL_PRESENT `preds[i]` (`compose.c:843-846`): `if (p->nterm == 0) { *why = "a predicate with no terms (nterm 0)"; ...}`
  and `if (p->need == MF_NEED_UNSTATED) { *why = "predicate need UNSTATED (`need`: 0 is no need, MF_SITE_ABI 13)"; ...}`.
  Sheet §2.1 "True facts, or refused": "On the derived run part the `mf_pred` fields that state a span (`need`, `nterm`,
  `term`, `omin`, `verify`, `nalt`) are UNREAD and must be 0 ... (refused if nonzero)". So the run part pcrec states at
  K38-2 is refused twice by today's kit. §5.1's moving-refusal list says `mf_pred.nterm` "(0 is refused today,
  `memfn.h:667`, Q-G2-10: admitted on the run SPAN, still refused elsewhere)" — the run PART is "elsewhere" — and does
  not list `need` at all (0 is `MF_NEED_UNSTATED`, refused since MF_SITE_ABI 13 as "no silent default").
- Also a contract wrinkle: "`need` 0 on the run part" re-means 0 from "UNSTATED, refused" to "unread here"; D-row
  memory `pcrec-no-silent-defaults` is satisfied only if the refusal text says which preds may carry it (FUNC run part
  with `nalt` 0 and the run span's link tested).
- Fix: §5.1 adds "`mf_pred.nterm` 0 and `need` 0 admitted on the derived run part (a FUNC `preds[]` entry with `nalt` 0
  that `ret_pred`/the run link names), still refused on every other predicate", with the refusal texts. Severity:
  design/doc (K38-2 builder would hit a refusal at first compile; no answer risk). Effort: text. Blast: K38-2, F9.

### READY-12 — doc nits in cites (CONFIRMED, quoted at 404cff6ea / e95cd7aef)
- §2.5 "`pf_window_of`, `ofs_window_of`, `emit_dfa.c:6815-6870`": `pf_window_of` is 6815-6873; `ofs_window_of` is at
  `emit_dfa.c:7592`, outside the range.
- §2.2 "`req_pres_ask` ... called by the admission verdicts in `req_admit` and by `req_site_define`": its callers are
  `req_site_define` (:1554), `req_dominated_applies` (:8640, with the start search's proof), `req_set_leads_applies`
  (:8661), `req_parts_in_whole` (:8866) and `req_pick_shadow` (:11175); not `req_admit` itself. The text should name
  them, since §2.2's "reader that runs before the define asks the same site" rule applies to each.
- Header "every `memfn/src/compose.c` cite below `pres_layout_check`'s head moves by −23 lines" after 3.0a: holds for
  every compose.c cite the sheet makes (697-729 -> 674-706; `pres_layout_check` 688 -> 665, `part_is_run` 665 -> 642,
  verified on e95cd7aef), but 3.0a's compose.c hunks continue past it (`@@ -935 +912,6`, `-1037 +1019,2`, `-1086..1155`),
  so the blanket "every cite below" is false past ~line 912 (no cite lives there today). Say "every cite in
  `pres_layout_check`".
- §2.4 C1 "on the VM route (`--engine=vm`; the default route of `bar(?=baz)` is `dominated`...)": `bar(?=baz)` compiles
  only with `--features all` ("(?=...) requires module 'lookaround'" without it). Spell the flag.
- `pcrec_req_run_masked` (`facts.h:116`) is dead at the build tree (no caller); K38-2 can drop it with the window.

## Answers to the round's questions

### (a) Per unit

| unit | cites at 404cff6ea | after 3.0a (e95cd7aef) | witnesses/plants can fail? | separable | complete? | verdict |
|---|---|---|---|---|---|---|
| K38-1 | hold (compose.c 697-729, presence.c 158/199-222, window.c run_member/translate, kit_run_member) | compose.c −23 holds for every cited line (688->665, 665->642); no cited name renamed; `fd_find` +1 arg (confirmed, 2 call sites); `kit_run_member`/`kit_pres_picks`/`wf_parts_prepare`/`wf_part_site` counts equal | caller check unpassable as written (READY-3); per-reader tie plant trips pcrec's agreement error, twin mass tie-blind on `abcd` (READY-4); S1107 fate one unit early (READY-10) | yes (after 3.0a; 3.0b rebase is a cost) | decider_census rows 56/69 move (READY-6.5) | **ready with listed text fixes** (READY-3, -4, -10, -6 item 5) |
| K38-2a | n/a (new family) | n/a | plant A/B fine; plant C has no observable before K38-2 (READY-8.2); C2's "reply" at K38-2a must be `run_decide`'s return (READY-8, suspected) | yes (after K38-1) | yes | **ready with listed text fixes** (READY-8) |
| K38-2 | hold except READY-12 nits; Q1 movers re-measured (7->2, 6->1, x\w... 7->2), §4.2 run_pin 5/7/6 and Q2's `xabcdefghijkq` stamp re-measured | emit_dfa.c/req.c/facts.c/memfn_sites.c/presence.c/memfn.h untouched by 3.0a | C1 skip half cannot fail (READY-2, skip unit not K38-2); C4 regime (a) dead (READY-8.1); W-L1/W-K1/W-K2 G2+pcrec forms reach (libpcre2: (3,6), (3,6), (4,8)/(6,7)); W-K3 needs K-0 bit 1 (READY-8, suspected) | yes (after K38-2a and 3.0b; 3.0b re-aims S1543, plan_frame R9) | NO: REQ_BYTE stamp path (READY-1), sabotages S448/S1548/S1700/S280 (+S1546) (READY-5), checks/goldens witness.tsv c2a/c2b, run_prechecks 4.5*, run_presence D, lever fence, `_reqrun_whole` readers (READY-6), `req_use_whole`/`req_handoff_k`/`keep`/`-fcomments` note (READY-7), five-pick shadow (READY-9), preds[] `nterm`/`need` refusals (READY-11) | **ready with listed text fixes** — all are listing/text; none reverses a ruling or risks an answer; READY-9 and READY-11 each need one stated choice |
| K38-3 | n/a | n/a | W-K4a/b as rev 1 (aligned-down vs ASan split holds) | rides K38-2 | yes | **ready** |

Overall: **ready with listed text fixes** for K38-2's build go (fix list: READY-1, -5, -6, -7, -8, -9, -11, -12; READY-2 at
the skip unit's brief); K38-1's build go: **ready with listed text fixes** (READY-3, -4, -10, -6 item 5).

### (b) r2 r38s rulings F1-F11 in rev 1

| F | verdict | note |
|---|---|---|
| F1 | RESOLVED | §3.4: SUFFICIENT + OUTPUTS-DETERMINED + whole extent; start `c − omin`; D187 add. 1 gap cited; call mode; P1. (C1's skip-half example is an F7 defect, READY-2) |
| F2 | RESOLVED | §2.2: ask at `req_pres_ask` in src/gen, reply in `mf_class.run`, Job keeps the defined site's reply, `req_whole_run` stays the pattern fact, none state off the link (caller list nit READY-12) |
| F3 | RESOLVED | `has_scan`, invariants, closed input list incl. `levers`, every admitted level/target, C2 containment |
| F4 | PARTLY | Goal scoped, §2.5 census, C4 restricted: done. REQ_BYTE's rule names `pcrec_req_pick` but the stamp is rendered by `pcrec_fact_stamp_req_byte(cx, req_run_member(...))` (READY-1); Goal 2's caller check contradicts §2.5's kept decider and RQ-2 ranking (READY-3) |
| F5 | RESOLVED | §4.4 lists every paragraph r2 named; anchors exist at the build tree (tuning s2-28-p5/p7, s2-29-p4, s2-41-*; match_api s6-3-7-p5/p7/p11, s6-3-1-p5a; facts_listing s4-1-2-p8/p8b; findings.md rows 110-111) |
| F6 | PARTLY | every item r2 enumerated is now listed with a fate (16 `len >= 2` sites verified exactly; MF_T_RUN readers; MFPRES; c10; KNOWN_READERS; limits_check; pres-window; 10 sabotages); the ruled standard "every reader" is not met: READY-1, -5, -6, -7, -9 |
| F7 | PARTLY | W-K2, W-K4a/b, W-L1, W-K1, C2, K38-2a: reaching. C1 skip half (READY-2), C4 regime (a) and K38-2a plant C (READY-8), K38-1's per-reader plant (READY-4) still cannot fail as written |
| F8 | RESOLVED | §5.1 states the pcrec abi event and the D76/D94 ritual; one population missing (`-fcomments` run note, READY-7) |
| F9 | RESOLVED (fix-induced gap) | the two refusals, `member` unread, verify named apart, constants true-or-refused, P3: done. Rev 1's new derived run PART adds two more refusal moves on `preds[]` not listed (READY-11) |
| F10 | RESOLVED | maxoff (trigger D176 Q4), verify NO, least candidate: each stated with why; P2 |
| F11 | RESOLVED | §2.5 exists, Q1 movers correct (re-measured), 1557-1565 holds, −23 holds for the cited lines, constraints split. New nits READY-12 |

## PROBED-AND-HELD

- File:line cites checked at 404cff6ea: 34 (emit_dfa.c 1058-1076, 1555-1556, 1557-1565, 6815-6870 (nit), 7361-7380,
  7419-7423, 7487-7505, 8583-8592, 8869-8872, 11185, 11229-11336, the 10 `len >= 2` lines; facts.c 318/332/581/828/833/
  915, 863; facts.h 65/69/77; kset.c 294-318; findings.c 780-800; compose.c 697-703/704-718/719-729; presence.c 199-222;
  memfn.h 543-545/667/729-741/1147-1149; precheck.c 161; internal.h 177-181; memfn_sites.c 217-219/741-757;
  limits_check.sh 161): 33 hold, 1 nit (READY-12).
- 3.0a: compose.c −23 verified at pres_layout_check/part_is_run; 16 cited names counted on 404cff6ea / 73075a9d1 /
  e95cd7aef (equal except `fd_find` +1 and `mf_wdecide` +1 mention); presence.c identical across bases; 3.0a touches no
  pcrec-side file the sheet cites.
- Sabotages: the 10 named rows' anchors and reach read; all 1198 `SAB_BEFORE` texts scanned for 40 retiring names; 49
  reach probes reading moving stamps triaged (5 new movers, READY-5).
- Compiles: ~45 `build/pcrec` (Q1 movers 6 artifacts, Q2/`xabcdefghijkq`, §4.2 run_pin x3, F2 pair, S280/S1700/S1546
  reaches, S1095 witness x2, barbaz VM, bar(?=baz), all-tie regime x3 + defaults); all sheet-measured values reproduced.
- libpcre2 (ctypes, 8 probes): W-K2 (4,8)/(6,7); W-L1 and W-K1 (3,6); C1 (7,13); (?:ac|ca)xyz NOMATCH; (bar)(?=baz)
  group 1 (0,3); bar\K(?=baz) (3,3); W-L13 shape (3,8)/(6,7): all as the sheet states.
- Spec anchors for §4.4: 12 paragraph ids exist; unlisted ¶8-¶13 of match_api §6.3.7 carry no window text.
- `head_max`, `mf_link.member`, `run_scan`/`run_window`, `PCREC_MAX_REQ_RUN_EMIT`/`MF_PRES_WINDOW` readers grepped
  repo-wide: all named except those in READY-6/-7/-9.
- C10 (`deleg_check`) with a term-less run part: kinds stay a subset of PRE's row; no break (held).
