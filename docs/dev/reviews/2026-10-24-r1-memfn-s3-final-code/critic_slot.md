# critic_slot — SLOT TRACING / rulings / goals / previous findings / standing questions (opus)

Round memfn-s3-final, code mode. SUBJECT cc4f54eb2 (lane/memfn-s3pair), BASE 0d3765c87. Review tree
worktrees/crit-memfn-s3-final (read only). Compilers: /tmp/claude-1001/crit-memfn-s3-final/{subj,base}/pcrec.
Probe helper: slot/probe.sh (compiles one pattern on both, prints scan/prefilter/forms and find calls).
No make, no suites, no timing. Reads/byte arguments use the kit's own cost table (plan_cost.def), not clocks.

## Disclosures
- Lens exception used: read docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md, 2026-10-23-r2-memfn-s3-c1-code.md
  and the r2 sibling dir's crit-memfn-s3-c1-slot.md (the previous slot lens), as allowed.
- Auto-injected on Read: the review tree's CLAUDE.md, docs/CLAUDE.md, docs/design/CLAUDE.md,
  docs/design/memfn/CLAUDE.md, memfn/CLAUDE.md, memfn/src/CLAUDE.md (orientation only).
- `git log` subject lines only. No denied file opened.

## Findings (written incrementally)

### SLOT-1  A REPORT site's stop is A-mass (rarity alone), so a 3+-member rare stop takes a byte walk where DEF ran memchr on a one-byte position; the family's own priced row (A-model) is not asked
- status: CONFIRMED (emitted text; no timing). `probe.sh '[xqz]ab'`: SUBJECT `RX_DFA_SCAN "cover"`, find =
  `while (c < n && !((s[c]==113 || s[c]==120 || s[c]==122))) c++` then `memcmp(s+c+1,"ab",2)`; BASE
  `"run-pinned"`, `memchr(subject + pos + 2, 98, ...)` in the offset-skip function. Same shape:
  `ab[xqz]` (BASE `offset-set`, memchr 'b'), `e[xqz]e` (memchr 'e'), `the[jqz]` (run-pinned, memchr 'h').
  Controls that hold: `v[0-9]\.[0-9]`, `x[0-9]{2}` (one-byte stop, memchr both arms); class-only windows
  (`[A-Z]{2}[0-9]{4}`, `\b[A-Z]{3}\b`) walk on both arms.
- severity: speed      - effort: M      - blast radius: every `cover` artifact whose least-mass core
  position has 3+ members while some core position is one byte (the corpus count is a census, not run here:
  >50 compiles).
- where: memfn/src/window.c:546 `a_mass_choose` (mass only); finder.c R7w (the 3+-member pick is WALK);
  design §2.1 A-mass row, Goals "Non-goals" (pricing the stop by its find method, `[MEMFN-PAIRSTOP]`).
- detail: by the kit's own cost table a walk is `C_BITMAP` 116 (1/100 c/B) against `C_MEMCHR` 6: the rule
  that chose the stop ignores a 19x difference the same file prices one table above (A-model's domain IS
  the method restriction: "one-member positions, the scan moves as a singleton, MEASURED", window_site.md
  §2.1). R2-1 widened PAIR to any two bytes, which closes the 2-member door only; the 3+-member door is the
  same class (r1 C8, r2 R2-8). The Goals section makes pricing a NON-goal while Goal 2 (not slower than DEF)
  outranks every goal below it: Goal 2's check is only the §6 cells and the 24-row sample, so this loss
  passes the bar by not being sampled. Either the non-goal must be argued against Goal 2 (with the census
  count), or the stop's domain needs the method (see GENERAL FORM).

### SLOT-2  Goal 3's "rows carry their own actions (no `if` on which row held outside the walk)" is met by Table D only; S3's new code branches on Table E's and B-renderer's row ids at 7 sites
- status: CONFIRMED (reading; grep at BASE vs SUBJECT)
- severity: maintenance (design: the goal is stated as checkable by review)   - effort: S-M
- blast radius: window.c only; every future E or B row
- where: window.c:1839, 1843, 1848, 1850 (`r == E_FIND`, `r == E_GENERIC` in wf_prepare);
  1771, 2611, 2644 (`bren == B_FN` in wf_find_prepare / wf_find_expr / wf_find_define); 2619
  (`bren == B_PAIR` declares B-pair's state in wf_find_expr). Pre-existing (BASE, S2): 808 and 681
  (`wf_arows[..].ct == &ct_a_model`: C-model and MARGIN ask which A row held, by contract identity), 1013-1022
  (`mr == M_MARGIN`/`M_PARKED`: Table M's choice applied outside its rows).
- detail: R2-7's fix moved Table D's actions into `wf_drows[]` (`finds`, `prepare`, `path`) and `wf_d_text[]`,
  and the design's Goal 3 now states the rule for EVERY table ("a table's rows carry their own actions").
  B's renderers keep the text in a parallel `wf_b_text[]` with B-fn's entry NULL and B-fn special-cased in
  three functions; B-pair's state is declared by an id test; Table E's prepare/path/plan-vs-legacy hand-off
  is an `if` chain on the E row index. The general form is D's: each row a struct with `prepare`, `head`/
  `expr`, `define`, `state` and `path` members (B-fn's `expr` = wf_find_fn, `define` = ofs_fn_define_at; E's
  `prepare` = wf_find_prepare / NULL, `hands` = plan or legacy). Deletes 7 id tests and the NULL slot.

### SLOT-3  Goal 3's "each method one renderer" is met for PAIR alone: S3's B-memchr and B-walk are a third copy of the one-byte memchr stream and a second copy of the set walk
- status: CONFIRMED (reading)
- severity: maintenance      - effort: M      - blast radius: pffind.c, ofsskip.c, window.c (every memchr/walk FIND)
- where: window.c:2428-2459 (`wf_b_search`/`wf_b_memchr`, `wf_b_walk`, added by S3); ofsskip.c:296-315
  (`memchr_body`, fn-memchr: one stream at offset k); pffind.c:259-293 (`pf_memchr_use`, incl. the
  below-candidate `+ k` of pf_memchr_back, which is B-memchr's d* < 0 case) and 297-319 (`pf_walk_use`).
- detail: R2-6 made `ofs_pair_text` the ONE two-stream text (fn-pair's body and B-pair), and the design now
  states the rule generally (Goal 3: "each method one renderer"; §2.2 names the pair only). The one-stream
  `memchr` is the same method in three renderers, each with its own offset/stale/miss spelling (pf_memchr's
  `+ k` for a back stop, fn-memchr's `- k`, B-memchr's `- d` / `+ -d` plus raise), and the set walk two
  (pf_walk over pcrec's table only; B-walk C-table or C-own). B-memchr is the third member of a family of
  three, the guide's unification trigger ("propose unification at ~3 members"). General form: `ofs_pair`'s
  shape with one byte (an `ofs_stream` struct: subject, n, at, len, k, cand, miss, layout), its readers
  the three memchr sites; a walk twin over a membership callback. Trigger: the next edit of any of the
  three, or the SIMD-everywhere unlock in GENERAL FORM below.

### SLOT-4  PAIR's widening to "any two bytes" sends COMMON two-byte stops to two memchr streams, with no cost constant and its refutation unmeasured; DEF never ran PAIR on these
- status: SUSPECTED (emitted text confirmed; the speed claim needs one timing cell: a common-pair stop under
  the 650 harness, e.g. `[st][hr]` or `[et][hr]e` on English `real` text, routed vs `--memfn=no-wf-find`)
- severity: speed      - effort: S (the cell) / M (a pair cost row)
- blast radius: every `cover` artifact whose stop is a two-byte set of mass below `HORS_MIN` (14.6%) and
  above what a memchr stream amortizes, or whose window D-hors declines (one position, or last offset < 0)
- where: finder.c:302-311 (PAIR row: `FB_UNMEASURED_DEFAULT`, refutation "a measured cell where the walk
  beats two memchr streams on a cube stop"); window_site.md §2.2 PAIR row; Frank's "Widen two pair s3 now".
- detail: `probe.sh '[st][hr]'`: SUBJECT two memchr streams on `h` and `r` (each roughly 5-6% of English
  bytes); BASE `"byte-class"`. `[et][hr]e`: SUBJECT PAIR on {h,r}; BASE memchr on `e` at offset 2 via
  offset-skip. Before R2-1 the pair form served only caseless cubes inside a run (fn-pair's measured home:
  rare letters' two cases). The widening's stated reason is the method's NEED ("two leapfrogging streams
  need exactly two bytes"), which is a soundness fact, not a speed fact: each stream is a libc call per hit,
  so a dense pair pays one call every ~10 bytes where the walk (C_BITMAP) pays a flat 1.16 c/B. The row's own
  refutation names a cube stop; the population it now serves is not cubes. Consequence of the ruling: PAIR
  should carry a mass ceiling (or the walk a floor) the way D-hors carries HORS_MIN, measured, or the bar's
  sample must hold a common-pair row. Not an answer issue (differential below holds).

### SLOT-5  kit_proof.md, the `cover` design of record, still says B1 lands the pcrec FACT deny `-fno-kit-proof` and lists `kit-proof` in `--list-axes`; S3 (= B1) built neither and revised nothing
- status: CONFIRMED (reading)
- severity: doc (design)      - effort: S
- blast radius: kit_proof.md §2.2, §7, the fam-M6 / con-staging rows; emit_dfa.c and known.c comments citing
  "§7's B1 row"
- where: docs/design/kit_proof.md:128, 192, 225, 414-437, 665-666; SUBJECT diff touches no kit_proof.md
  (git diff --stat over docs/design shows window_site.md only); emit_dfa.c `cand_rows[]` cover row comment
  ("a pcrec FACT deny `-fno-kit-proof` is filed under [IFACE-PUSH]"); known.c:365-368.
- detail: the code agrees with D174's first application (bit 57 filed by behaviour under [IFACE-PUSH]), so
  the ruling holds; the design note does not record it (docs/design/CLAUDE.md: a build that refutes a note
  revises it deliberately). CONSEQUENCE worth stating in the revision: the `cover` LOCATE row now has NO
  pcrec-side identity of its own. Its only off switch is the kit's E-find deny, which also moves any native
  window site E-find renders (registry.md §6 `wf-find`: "any other window search takes a plain byte loop"),
  and C13's `refused` detail conflates "denied" with "the kit cannot render this stop" (r2 F5's
  unrenderable pick, R2-8's below-candidate pair): `KITPROOF`'s why cannot tell a deny from a decline.

### SLOT-6  Stale orientation text after R2-1: PAIR still described as a "cube stop" asked with its "stretch", and REPORT as held by "every FIND row (KD_ALL)"
- status: CONFIRMED (reading)
- severity: doc      - effort: S      - blast radius: the next editor of finder.c / Table B
- where: memfn/src/CLAUDE.md:15 ("PAIR added ... a window site's cube stop"; "`fd_find`: the window site, the
  stop's set, offset and stretch"); finder.c:33 ("PAIR, the two-stream find of a window site's cube stop");
  finder.c:412-413 (`kind_cl`: "every FIND row's kinds hold it since D172 S3 (KD_ALL)": KD_ALL excludes
  REPORT; only D1, D1c, D1w, PAIR, R7w hold it, through KD_STOP / D1c's explicit kind, finder.c:127-144);
  finder.c:314 (PAIR's refutation names "a cube stop"); docs/design/memfn/CLAUDE.md:64 and window.c:9 cite
  window_site.md as rev 3.2 with no mention that the code implements the rev 3.3 DRAFT (see Q2 (a)).
- detail: SF_STRETCH_CUBE retired (finder.c:104), `fd_stop` carries set and offset only (kit.h). The
  `kind_cl` comment states the opposite of the KD_ALL/KD_STOP split three screens up.

### SLOT-7  The Goals' strict ranking ("when two conflict, the higher wins") is contradicted by the subject's own ruled trades: hex8 is Goal 4 beating Goal 2, and SLOT-1's non-goal is Goal 3 beating Goal 2
- status: CONFIRMED (reading: window_site.md Goals vs §6 and §2.1)
- severity: design (doc)      - effort: S      - blast radius: every later S3-family acceptance read against these goals
- where: window_site.md:24-45 (Goals, Non-goals) vs §6 (hex8-bounded throughput/dense 1.531 capped at 1.551,
  "accepted for the 2-6x wins", the kit's judgement call under D172's addendum) and §2.1/Non-goals ("Table A
  ranks by mass alone and Table B finds whatever A chose").
- detail: Goal 2 reads "not slower than DEF beyond the floor ... the named caps excepted". A cap is the
  mechanism by which a LOWER goal wins: hex8 is slower than DEF on dense input BECAUSE D-hors buys Goal 4's
  hex8 wins, and the cap admits it; nothing in the goals says which wins qualify for a cap, so Goal 2 is
  unfalsifiable against Goal 4 (any loss can be capped). Likewise SLOT-1: keeping Table A mass-only is Goal 3
  ("one table per slot", B "finds whatever A chose") taking precedence over Goal 2 on every 3+-member-stop
  artifact the sample does not hold. Suggested wording: Goal 2 admits a cap only where a NAMED Goal-4 win on
  the same pattern exceeds it (hex8's 2-6x), ruled by the owner; and Goal 2's population is stated (the
  sample's strata) with the classes outside it listed as unmeasured (SLOT-1, SLOT-4, R2-2's same-set
  windows), so a reader can see where the ranking was never tested.

### SLOT-8  On B-fn sites the stop's find is decided by TWO tables: the FIND slot picks PAIR, then fn_rows[]'s BODY slot re-decides fn-pair vs fn-memchr from the scan's mask; design §2.7 says these FOLD into D1/PAIR, the code keeps both
- status: CONFIRMED (reading)
- severity: maintenance (design: Goal 3 "Table B IS the finder's FIND slot; no private copy of it")
- effort: M      - blast radius: every B-fn (caseless-literal) `cover` artifact and every native offset-skip site
- where: window.c:1672-1683 (`b_fn_holds`: pick PAIR, then `ofs_fn_scan` hi >= 0 and `ofs_fn_serves`, a
  quiet BODY walk); ofsskip.c:212-215, 861-921 (BODY rows fn-pair, fn-memchr under one FN_BODY_SERVES,
  first match on the scan's mask); window_site.md §2.7 row "ofsskip fn-memchr / fn-pair / vrun PREFIX |
  FOLD: ... + D1 / PAIR / vrun".
- detail: the two tables agree by construction today (PAIR requires two members; B-fn requires the stop in a
  RUN term, whose positions are one-member or cube, so the BODY sees a cube and takes fn-pair), but nothing
  states or checks the agreement: a future FIND row (say a priced pair row, SLOT-4) or a BODY row (a new
  one-stream form) moves one decision without the other, and B-fn would render the BODY's pick under the
  FIND slot's trace name (`WPATH fd=PAIR`, which also does not say B-fn vs B-pair: r2 F4, still open). The
  fold the design records (§2.7) is the general form: fn_rows' BODY slot becomes a renderer list keyed on the
  FIND slot's pick, as `wf_brows` already is for E-find, and fd_route's native offset-skip ask reads the
  same FIND rows. Trigger: the next row added to either table. Until then a self-check (every B-fn plan:
  BODY pick == the FIND pick's form) would make the agreement a stated fact.

### SLOT-9  The two new caller-facing deny names `wf-find` / `wf-hors` are family letters plus a method name, coined 2026-10-23, after D174 (2026-10-22) bound new names to behaviour
- status: CONFIRMED (reading; `git log -S'"wf-hors"'` dates the name to bc675b020, 2026-10-23)
- severity: doc (contract: a caller types and reads these; D80/D174)      - effort: S before landing, M after
- blast radius: `--memfn=` spellings, `--list-axes`, registry.md §6 rows, tuning.md §2.43¶3d,
  match_api.md §6.3.4 `"cover"` row, tests/axes/memfn_arm.py, G2 plants S1422/S1423, emit_sweep pins
- where: memfn/src/options.def:504-513; window.c:1356-1358 (`WF_FIND_ID`, `WF_HORS_ID`).
- detail: D174: a caller-facing name names "the BEHAVIOUR a caller sees or turns off, never an internal
  module or mechanism ('kit', 'memfn', 'proof', family letters, lane or row ids)". `wf` is the window
  FAMILY's letters and `hors` is Horspool, the mechanism D-hors implements; the descs were reworded by
  behaviour (r1 C15) but the names were not. D174's "S3's two deny rows stay under `--memfn=`" keeps the
  NAMESPACE, it does not exempt the row names (it is "not retroactive" only for names shipped before
  2026-10-22). r2 F7 raised this; R2-5's disposition fixed the prose only. Behaviour names in the descs'
  own words would be e.g. `window-search` and `common-byte-skip`. Cheapest now: nothing has shipped.

## Q1. SLOT TRACING (each slot to the table window_site.md rev 3.3 names)

| slot | design names | code at SUBJECT | verdict |
|---|---|---|---|
| A stop | §2.1 A-parked/A-model/A-mass/floor + MARGIN, kit_tables | `wf_atable` (A-empty, A-parked, A-model, A-mass, A-floor), `wf_mtable` (M-one, MARGIN, M-parked) on kit_walk | matches; Table M's choice and C-model's/MARGIN's "which A row held" are applied outside the walk (SLOT-2, pre-existing). On REPORT only A-mass/A-floor are reachable (no entry); A-mass is method-blind (SLOT-1) |
| B find (decision) | §2.2: IS the finder's FIND slot, asked about the stop | `fd_find` over `fd_rows` FIND: facts from `set_facts` (SPAN0/ONE/TWO_MEMBER/CONTEXT_STOP), SEEK_ROLE, WINDOW_STOP, need REQUIRED, layer OFF | one table, no private copy, EXCEPT on B-fn plans, where fn_rows' BODY slot re-decides (SLOT-8). Unreachable on REPORT: R8, R3a, R3b, R4, R1, R2 (KD_ALL excludes REPORT), D1w only under `no-fd-d1`; D1c only for a one-byte stop below the candidate (`(?<=Q)ab` reaches it) |
| B renderers | §2.2 `wf_brows`: B-fn, B-pair, B-memchr, B-walk | `wf_brows[]` (row list, first match on the pick) + parallel `wf_b_text[]`; B-fn special-cased in 3 functions | matches the list; actions not row-carried (SLOT-2); renderer choice untraced (`WPATH fd=` names the FIND row; r2 F4); an unbuilt pick declines silently (r2 F5) |
| C verify plan | §2.3 steps 1-7 | `wf_crows[]` + `c_plan` | matches (C-pin on REPORT = verify-YES R whole, path `mass+pin`, as §2.7 says) |
| D resume | §2.5 kit_table, rows carry actions, D-hors `whi >= 0` | `wf_dtable` + `wf_drows[]` (`finds`, `prepare`, `path`) + `wf_d_text[]` (head/next/define) | matches rev 3.3, incl. R2-9's conjunct; reachable only inside E-find (r1 C6 still open) |
| E frame | §2.6 E-func, E-stmt, E-find, E-generic | `wf_etable` (same order, E-find deny `wf-find`) | matches; E's actions are `r == E_FIND` tests (SLOT-2); E-legacy/E-generic keyed on the REPORT label (r1 C5) |
| E-find text | §2.6 + §2.2 + §2.5 | `wf_find_expr` / `_define` / `_use` over `wf_frame`, `wf_open`, `wf_cand`, `wf_close`, `wf_test_to` | shares the floor's frame (C9 holds); B-memchr and B-walk are new copies of the stream/walk methods (SLOT-3) |
| pcrec `cover` row | kit_proof.md §1.1, §7 B1; match_api §6.3.4 | `locate_cover_applies` = `pcrec_cover()->why == NULL`; the lever no longer gates it | matches the S3 ruling; kit_proof.md's B1 deny/listing not revised (SLOT-5) |
| `cover_conj[]` | kit_proof.md §1.1 C1..C14 | known.c:376 table, first failing row is `why` | one table, read in order; C8 reads `pcrec_fact_span_stated` on every build (spec hunk facts_listing §4.1¶2 matches) |
| C13's ask | "the REPORT description has a row that serves it" | `cc_served`: `mf_ask` on `pcrec_cover_site`; refusal -> `report-served/refused` | matches; one detail for deny and decline (SLOT-5) |

Third members found: B-memchr (third one-stream memchr renderer, SLOT-3); fn_rows BODY as a second
decider of the FIND slot's question (SLOT-8). Duplicated: none else. Narrowed: PAIR's stop must be at or past
the candidate (by design, R2-8). Unreachable: listed above.

## Q2. RULINGS: agreement and CONSEQUENCES

- **(a) window_site.md rev 3.3 DRAFT vs rev 3.2 of record.** The code implements rev 3.3 (E-find, fd_find's
  question, PAIR any-two, wf_brows, Table D kit_table, D-hors's `whi >= 0`) and the spec hunks (registry
  `wf-find`/`wf-hors`, tuning ¶3d, match_api `"cover"`) commit callers to it. AGREES with rev 3.3; DISAGREES
  with rev 3.2 (which has no E-find row, PAIR only as "today's scope", Table D a declared list).
  CONSEQUENCE: landing this merges a contract whose design is "NOT YET ACCEPTED"; the manager's acceptance of
  rev 3.3 is a precondition of the merge, not a follow-up. Index lines still read rev 3.2 (SLOT-6).
- **(b) D172** (one window site; REPORT = verify everything; stop choice the kit's as tables). AGREES:
  RPT, `kit_report_exact`, SF_PROOF_EXACT, the R-26.6 preview and `mf_preview` are gone (finder.c, kit.h,
  memfn_sites.c); REPORT is the window site through E-find. CONSEQUENCE: REPORT's stop is A-mass, the
  family's method-blind row, while the RESEED alternative keeps prefix_k's priced A-model: the family has
  two stop rules and REPORT got the cheaper-to-state one (SLOT-1).
- **(c) D146** (delegation; guard = pcrec's timings kit on vs off; revisit when kit code measures worse than
  pcrec's pre-migration form). AGREES in shape (C13 asks; the kit owns the method). CONSEQUENCE: SLOT-1 and
  SLOT-4 are D146's revisit trigger in waiting; its guard is the mover sample, so the sample must hold those
  shapes or the trigger cannot fire.
- **(d) D147** (each layer best on its own; both layers reported). AGREES for the scalar layer's bar.
  CONSEQUENCE: B-pair carries no SIMD row, so on `\b(?i:foobar)\b` the SIMD-on layer is now WORSE than its
  own previous best (BASE `vrun@w32+w16`, SUBJECT `"none"`, probe below): D147's "the SIMD layer must be the
  best it can be" is knowingly unmet there; §6 books it as a SIMD-thread finding (r2 R2-3, PLAN). The
  emit_sweep `-fmemfn-simd` pins were raised back to 22/15 (>= main's 20/15), so the count no longer shows it.
- **(e) D155** (floor rule; no `#if` in bodies). AGREES: B-fn reuses the offset-skip function's file-scope
  rungs (D155's seam), B-pair/B-memchr/B-walk have none. `(?i)foobar -fmemfn-simd` keeps `vrun@w32+w16`.
- **(f) D157** (facts only). AGREES: `fd_stop` is set + offset; C13 states the REPORT description; nothing
  pcrec sends names a kit row. The registry `wf-find` row describes the kit's methods to callers, which is
  D80 behaviour text, not a D157 breach.
- **(g) D174** (behaviour names). PROSE AGREES (registry, tuning, `--list-axes` descs). NAMES DISAGREE
  (SLOT-9).
- **(h) PAIR widened to "any two bytes" (Frank 2026-10-23).** AGREES: SF_TWO_MEMBER for any two-member set at
  offset >= 0, SF_STRETCH_CUBE retired, ONE renderer `ofs_pair_text` (fn-pair and B-pair). CONSEQUENCES: (1)
  common pairs now take two libc streams, unmeasured, the row's refutation still phrased for cubes (SLOT-4);
  (2) a non-cube pair never reaches B-fn, so it never gets SIMD (by §2.2's non-goal `[MEMFN-PAIRSIMD]`);
  (3) a 3+-member stop still walks (SLOT-1): the widening stopped at the method's arity, not at the loss's
  cause (the method-blind stop).
- **(i) S3-internal rulings re-checked:** FIND asked at the OFF variant (agrees, §2.2 bullet 3); KD_ALL
  revert / KD_STOP (agrees, §2.2 bullet 4; `kind_cl`'s comment wrong, SLOT-6); `table_ref` UNSTATED on a
  window site (agrees; gate.c `cl_table_ref` returns -1 when `nalt`); a 2+-member stop below the candidate
  declines (agrees, verified `(?<=[Qq])ab` -> `"unanchored"` on both arms); OFF arm = pre-S3 default
  (VERIFIED, 54 + 6 compiles byte-identical but for the abi digits, PROBED-AND-HELD).

## Q3. GOALS (rev 3.3's ranked 1-4)

- **Goal 1 (answers exact)** is served first: the OFF arm identity holds (54/54), the differential below is
  clean, G2 carries plants for every S3 row (S1422-S1429, S1540) and E-find reach floors.
- **Goal 2 (not slower than DEF)** is served on the cells it names and lost, unmeasured, where a lower goal
  or a non-goal chose: SLOT-1 (Goal 3's "B finds whatever A chose" over Goal 2; 3+-member stops walk where
  DEF memchr'd), SLOT-4 (the PAIR widening, an unmeasured default, over Goal 2 on common pairs), hex8 (Goal
  4 over Goal 2, capped; SLOT-7 on why the ranking text does not admit it), R2-2's same-set windows (MEASURE
  in 588, result not visible to this lens).
- **Goal 3 (simple)** is half-met: one table per slot except B-fn (SLOT-8); one renderer per method for the
  pair only (SLOT-3); rows carry actions in D only (SLOT-2).
- **Goal 4 (speed wins)**: hex8 via D-hors, caseless literals via B-fn/B-pair. Nothing here contradicts it.

## Q4. PREVIOUS FINDINGS at SUBJECT

### r1 (2026-10-23-r1-memfn-s3-code.md)

| id | r1 disposition | status at SUBJECT | cite |
|---|---|---|---|
| C1 | FIX | FIXED: Table B returns the deciding row's pick, E-find renders D1/D1c/D1w/PAIR/R7w | finder.c:925-950 `fd_find`; window.c:1693-1712 `wf_brows` |
| C2 | PROCESS | FIXED at the pin level: emit_sweep `-fmemfn-simd` c-default 22 (byte) / 15 (utf8), main 20/15; the B-pair SIMD loss stays as R2-3 | scripts/emit_sweep.py:506, 537 |
| C3 | FIX | FIXED: the stop's own facts, need REQUIRED, layer OFF ruled; KD_ALL restored on R8..R2 and PRES, KD_STOP on D1/D1w/PAIR/R7w | finder.c:127-128, 212-237 |
| C4 | DOC | DONE as DRAFT only: rev 3.3 §2.6 records E-find, not accepted (Q2 a) | window_site.md:12-20, 333 |
| C5 | FILE | OPEN: `e_legacy_holds`, `e_generic_holds`, the refusal text and `select_arm` key on `site_kind == REPORT` | window.c:1392, 1420, 1827; compose.c:280 |
| C6 | FILE | OPEN: D-hors reachable only inside E-find | window.c:1718-1744 |
| C7 | FIX | FIXED: `wf_dtable` kit_table, contracts, deny `wf-hors`, path `+hors`, actions row-carried (R2-7) | window.c:1594-1649, 2588-2599 |
| C8 | FOLD | OPEN: stop priced by mass only; consequence SLOT-1 | window.c:546-564 |
| C9 | FIX | FIXED: `wf_frame`, `wf_open`/`wf_cand`/`wf_close`, `wf_test_to` shared | window.c:2182-2294 |
| C10 | GATE | PARTLY: the sample is in the bar (§6 rev 3.3); G2 gained dense, caseless (one high-byte cube) and two-byte streams; widening G2 windows toward the ~13 admission cap not seen | g2_win_gen.c diff; window_site.md:591-597 |
| C11 | FIX | NOT VERIFIABLE by this lens (its code is under s3_evidence, denied) | — |
| C12 | NOTED | OPEN as noted (run-skip resume to ideas.md; not read) | — |
| C13 | FIX | FIXED: S1425-S1429 plus S1540 (R2-6's shared renderer) | memfn/tests/run_g2_win.sh:116-137 |
| C14 | FIX | FIXED for E-find (`fx->holds`, no cast); `b_fn_holds` still WRITES its translation (`translate(..., b->fn)`) from inside a predicate, harmlessly (read only when B-fn wins) | window.c:1405-1409, 1672-1683 |
| C15 | FIX | PARTLY: `--list-axes` descs and spec prose by behaviour; the names are not (SLOT-9) | options.def:504-513 |
| C16 | FILE | OPEN (filed): `--harness=kit-proof` parsed, "INERT", read only by the KITPROOF trace | cli/main.c:1217-1219; internal.h:172-180 |
| C17 | FIX where touched | MOSTLY: `WF_FIND_ID`/`WF_HORS_ID`, `WF_WHY_MAX` labelled, libc off on Horspool text, `fd_find_form` gone; `"wf-find"`/`"wf-hors"` still spelled separately in options.def; find_groups on the query path is now justified in place (the class reads the count) | window.c:1356-1358, 1477-1481, 1791 |

### r2 (2026-10-23-r2-memfn-s3-c1-code.md)

| id | r2 disposition | status at SUBJECT | cite |
|---|---|---|---|
| R2-1 | ASK FRANK -> widen PAIR | FIXED for two-byte stops (`ab(?=[Qq])`: two memchr streams on q/Q); the 3+-member class remains (SLOT-1) and the widened scope is unmeasured on common pairs (SLOT-4) | finder.c:301-314 (PAIR row), set_facts |
| R2-2 | MEASURE in 588 | OPEN in code (no change to same-set windows); the reading is outside this lens's inputs | — |
| R2-3 | PLAN | OPEN as planned: `\b(?i:foobar)\b -fmemfn-simd` SUBJECT `"none"`, BASE `vrun@w32+w16` | probe in PROBED-AND-HELD |
| R2-4 | FIX-NOW | FIXED: tests/axes/memfn_arm.py classifies `wf-find`/`wf-hors` (DIFFER) | tests/axes/memfn_arm.py:116-130 |
| R2-5 | FIX-NOW | FIXED for prose (registry §6, tuning ¶3d name no E-find/D-hors/HORS_MIN); names open (SLOT-9) | registry.md §6 rows; tuning.md §2.43¶3d |
| R2-6 | FIX-NOW | FIXED: `ofs_pair_text`, one renderer for fn-pair and B-pair (plant S1540); the one-byte stream is not unified (SLOT-3) | ofsskip.c:245-259; window.c:2465-2480 |
| R2-7 | FIX-NOW | FIXED for Table D (actions in `wf_drows`/`wf_d_text`, no const cast, `WF_HORS_ID`, header of `wf_b_search` corrected); the same rule unmet for E and B (SLOT-2) | window.c:1628-1649, 2426-2432 |
| R2-8 | PLAN | OPEN as planned: `(?<=[Qq])ab` is `"unanchored"` on both arms | probe |
| R2-9 | DOC | FIXED: §2.5 and registry `wf-hors` state the last offset >= 0 | window_site.md:315; registry.md `wf-hors` row |
| R2-10 | DOC | FIXED (DRAFT): Goals added; ranking contradicted by ruled trades (SLOT-7) | window_site.md:24-45 |
| R2-11 | NOTED | unchanged (by the ruled bar) | window_site.md:594-597 |
| R2-12 | PLAN | OPEN (no high-byte/utf8 timing class in this subject's code) | — |
| R2-13 | NOTED | the pins carry "r2 re-pin" notes with the old values; job 606's reading not visible here | scripts/emit_sweep.py:506, 537 |
| R2-14 | NOTED | unchanged | — |

### r2 slot-lens findings the consolidated table did not carry (crit-memfn-s3-c1-slot.md)

| id | status at SUBJECT | cite |
|---|---|---|
| F4 renderer untraced; `wf_brows[].row/.basis`, `wf_drows[].basis` unread | OPEN: `WPATH ... fd=` prints `wf_plan_brow` = the FIND row id; no reader of `.row`/`.basis` | compose.c:1100-1108; window.c:2700-2703 |
| F5 an unrenderable pick declines silently (fd_route refuses loudly) | OPEN: no self-check that every L_OFF FIND pick has a `wf_brows` row | window.c:1752-1754; finder.c:898-902 |
| F10 D1c keyed on kinds DFA_ATTEMPT/REPORT as well as the fact | OPEN (agrees with §2.2's text) | finder.c:219 |
| F11 R7w's `table_ref REF` need serves pf_walk, B-walk relies on UNSTATED | OPEN (comment now says so) | finder.c:229-237 |
| F12 PAIR's pcrec-side reach floor a placeholder | OPEN: `fd PAIR PLACEHOLDER PLACEHOLDER`; G2's `pair:316 fn:48` floors count it | tests/memfn/row_floors.tsv:112; run_g2_win.sh:78 |

## Q5. STANDING QUESTIONS

### SIBLING OF A FAMILY
1. **"Find the next byte of set S at offset d from c"** has three homes: pffind.c (pf_memchr, pf_memchr_back,
   pf_walk), ofsskip.c's BODY (fn-memchr, fn-pair) and window.c's B-memchr / B-pair / B-walk. Only the pair
   is one text now (`ofs_pair_text`). SLOT-3.
2. **Deciders of that find**: fd_rows' FIND slot (native through `fd_route`, window through `fd_find`), fn_rows'
   BODY slot, vrun's PREFIX slot. The first two answer the same question for B-fn sites. SLOT-8.
3. **Stop choosers**: A-model (prefix_k, priced by `plan_cost.def`, domain = one-member positions), A-mass
   (mass only, REPORT and parts), pcrec's `pcrec_find_run_rank` (the parts' tie source), and D-hors's
   HORS_MIN (a threshold standing in for a cost comparison at the resume). Four rules where one priced choice
   would do. SLOT-1, SLOT-4.
4. **REPORT-label keys**: `e_legacy_holds`, `e_generic_holds`, wf_prepare's refusal text, compose.c
   `select_arm`, D1c's kind list. One frame fact ("the candidate is the answer") would replace five keys
   (r1 C5, r2 F10).
5. **Row actions outside the walk**: Table D carries them; Tables M, E and B's renderers test row ids
   (SLOT-2). A kit_table convention (an action struct per row) is the shared form.

### GENERAL FORM + UNLOCKS (each with its trigger)
- **E-find IS the general window search**; E-func/E-stmt + `translate()`/`legacy_ok` are its zero-mover
  special case. Unlock: route every FIND window site through E-find, retire the translation (window.c
  ~1178-1351) and, behind it, pffind's FIND arms; D-hors then serves native sites (r1 C6). Trigger: an
  emit_sweep arm forcing E-find on native sites, answer-identical, plus G1 no-loss at both layers; or S1's
  native D-hors count > 0.
- **One priced stop × method choice**: A-model's argmin extended from "one-member positions, C_MEMCHR" to
  every core position with a per-method scan cost (C_MEMCHR, a measured C_PAIR, C_BITMAP for the walk, the
  Horspool resume's expected shift). Unlock: SLOT-1 (3+-member walk) and SLOT-4 (dense pairs) and R2-8 (an
  unfindable below-candidate pair) dissolve into prices; HORS_MIN becomes a comparison, not a fitted
  threshold; A-mass retires. Trigger: the census count of `cover` artifacts whose least-mass core position
  has 3+ members while a one-byte core position exists (SLOT-1), plus one timing cell from each of SLOT-1
  and SLOT-4. (The Non-goals file it as `[MEMFN-PAIRSTOP]`.)
- **One stream primitive** (`ofs_pair` generalized to one or two bytes, layout parameters) with the SIMD
  PREFIX rows over the primitive, not over fn-pair's body. Unlock: SIMD for B-pair and B-memchr in every
  frame (closes R2-3 without a new kernel for cubes), deletes two memchr copies, and makes B-fn's
  translatability test unnecessary. Trigger: the SIMD thread judges R2-3, or the next edit of any memchr copy.
- **BODY slot as a renderer list keyed on the FIND pick** (SLOT-8). Unlock: one decision per slot for
  native offset-skip sites too. Trigger: the next row added to fd_rows FIND or fn_rows BODY.

## PROBED-AND-HELD
- **OFF arm = the pre-S3 default but for abi digits**: 18 patterns x {default, `-fmemfn-simd`,
  `--engine=vm`} = 54 compiles, SUBJECT `--memfn=no-wf-find,no-wf-hors` vs BASE, byte-identical after
  85->84 normalisation; plus 6 patterns (hex8, `[a-z]{16}`, `[aeiou]{3}`, ...) with `--memfn=no-wf-find`
  alone, identical. 0 differences.
- **Answers**: 10 slot-relevant patterns (D1c `(?<=Q)ab`, PAIR `ab(?=[Qq])` and `a[xy]b`, B-walk
  `[xqz]ab`, D-hors `\b[0-9a-f]{8}\b` and `[0-9a-f]{3}(?=[0-9a-f])`, lookbehind+class `(?<=a)[0-9a-f]{8}`,
  `(?<=x)[xy]z`, declined `(?<=[Qq])ab`, `(?<=[0-9a-f])[0-9a-f]{4}`) x 400 random subjects x every
  `search_from` = 93,210 rx_search calls against libpcre2-8, 0 differences.
- **Slot reach by probe**: D1 memchr (`x[0-9]{2}`, `v[0-9]\.[0-9]`), D1c with the raise (`(?<=Q)ab`), B-pair
  (`ab(?=[Qq])`, `[st][hr]`, `\b(?i:foobar)\b`), B-fn with vrun under `-fmemfn-simd` (`(?i)foobar`), B-walk
  (`[xqz]ab`), D-hors (`\b[0-9a-f]{8}\b`, `[aeiou]{3}`), cover declined for a two-byte stop below the
  candidate (`(?<=[Qq])ab`, both arms `"offset-set-bounded"`).
- **By reading**: PAIR is unreachable from native routes (SF_WINDOW_STOP only in `fd_find`; `fd_route` maps
  FF_PAIR to no arm); `cl_table_ref` reads UNSTATED on a window site; B-fn and fn_rows' BODY agree by
  construction (SLOT-8); D-hors's probe stays inside the bound (`whi >= 0`, bound `C + chi`) and the lower
  half stays in the test's first conjunct, the shift being sound regardless; the OFF arm needs no D-hors
  deny (D-hors only inside E-find); RPT/`kit_report_exact`/`mf_preview` fully retired (no reader left).
- **Compiles**: about 190 single-pattern compiles in total (the OFF-arm batch was 108 compiles, over
  COMMON's ~50 per batch guidance; disclosed), no runs beyond the differential drivers, no timing.
