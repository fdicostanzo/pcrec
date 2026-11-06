# ready — memfn-span-cards-r11

Lens: readiness — S2c, S2d, S2e of span_cards.md rev 1.1 (ef2f130fc) against build tree main 6f1b40f75.

## Findings

### READY-1 CONFIRMED — the loader refuses every delta row's `inputs`; no unit changes it (S2e cannot load its own set)
- Severity: blocker for S2e (the set cannot be written); completeness. Effort: small code (loader + ks_ref.py
  + mfixtures rows + a §7 row) but it is a FORMAT change that must be assigned to a unit. Blast radius: S2c's
  spec hunk, S2e's assembly step 2, S2a's format-2 parse (the natural home).
- Design: §2.4 (:262, :276), §3.4 step 2 (:591), §3.8 step 1 (:787) put each `delta` row's base ARM name
  (`base.walk`, `base.null.<cls>`, `base.fail.<kind>.<entry>`) in the MEASURED row's `inputs`; §4.4 (:940)
  amends only the SPEC text `measures.md` §2.2¶3, at S2c.
- Code at 6f1b40f75, `src/core/ks_measures.c:466-481` (check_rows): `if (!computed) return mfail(...,
  "key '%s': a %s row names inputs", ...)` — a `measured` row with non-`-` inputs is refused; and even on a
  computed row each input must be `is_row_key` or `is_cell_id` (:396-415, the `cell` id column), so an ARM
  name (a value of the `arm` column) is refused there too. `measures.md` §2.2¶3 at 6f1b40f75 ("only a
  `derived` or `fitted` row names inputs") and §7's row ("an input that is neither a row nor a cell") agree.
- Repro (reading): §3.8 step 2 runs `pcrec --list-measurements draft.tsv`; the first `find_hit` row (status
  `measured`, `inputs base.walk`) reaches ks_measures.c:469 and the listing is refused. No unit's content
  (S2a §4.5 code list, S2c's spec-only hunk, S2e) names a loader / ks_ref.py / mfixtures / §7 change for
  measured-row inputs or arm-name resolution (`grep -n inputs` over the design: 14 hits, none names the loader).
- Also D80: S2c lands a §2.2¶3 contract sentence whose code is in no unit — spec and loader disagree from S2c on.
- Fix (text): S2a (the format-2 unit) gains: on a FORMAT-2 set, a `measured` row whose card's `lengths` is
  `delta ...` names exactly one input, which must be an `arm` value of this set's cells (not a cell id);
  ks_ref.py the same; a §7 row; mfixtures rows (an arm input accepted on a delta row; refused on a `slope`
  row; an unknown arm refused); a sabotage row. The §2.2¶3 hunk then moves to S2a (spec with code), which
  also makes S2c's "parse `lengths` on format-2 cards" a loader fact, not only the recompute's. Note the
  LOADER must then read the card's `lengths` grammar (today `lengths` is free provenance text), so S2a needs
  the estimator-grammar parse too, or the rule keys on the card name — the design must pick one.

### READY-2 CONFIRMED — check C's card-guard population is 17, not 12 ("every card table")
- Severity: doc / check-floor (a pin at 12 is wrong; an equality pin would be red in the correct build).
  Effort: one number + tree_drill.py C reading every card table. Blast radius: S2c witness, §2.4.
- §2.4 (:288-292) puts the guard "in the card-table walk (:337-343), over every card table and every `ver`" —
  and finder_check.py:333-343 at 6f1b40f75 does walk every `memfn/data/cards/*.tsv` — but the population is
  taken from `kit-grid.tsv` only ("kit-grid.tsv's 9 cards", §9 S2c "12 with a `kit:form.` dep after
  kit-grid@3"). `tree_drill.py` C (:72-76) reads only kit-grid.tsv.
- Repro: `git show 6f1b40f75:memfn/data/cards/kit-kernels.tsv`: 5 cards with `kit:form.` deps (beta, f,
  saving, xover, gstar; all `form` first); kit-synthetic.tsv 0 (deps `-`). Population at the tree 9 + 5 = 14,
  after kit-grid@3 17. Observed text 12, expected 17 (or narrow the guard to kit-grid.tsv and say so).
- Fix (text): §2.4 and §9 S2c: 14 at the tree, 17 after kit-grid@3, floored at 17; tree_drill.py C to count
  over every card table, as the guard reads.

### READY-3 CONFIRMED — S2e's cell-less embed turns three existing STORE checks (and two sabotage detectors) red in the correct build; none is listed
- Severity: blocker for S2e's `make test` witness; completeness (§3.8 "No embed reader needs the cells").
  Effort: re-aim three checks + two S-row detectors + their spec wording. Blast radius: S2e.
- `tests/knowledge/run_measures_tests.sh` at 6f1b40f75, STORE section, for EVERY `measure_store/*/*/set.tsv`:
  (i) :52-57 R4 `LM --list-measurements="$id@$rev"` (a NAME, resolved from the EMBED, no `-I`) `cmp`'d with
  the committed file; (ii) :58-64 R5 the NAME's `--view=decoded` against `ks_ref.py decode "$f"` (the FILE,
  with its `cells`); (iii) :104 the embedded text (`meas_store_check.c` OUTDIR/<name>.text) `cmp`'d
  with the committed file. Under §3.8's rule (the embed omits `cells`, and "`--list-measurements=NAME`
  resolved from the embed prints ... an EMPTY `cells` section") all three differ for zen4-grid3 (1,008 cells
  in the file, 0 in the embed): red in the CORRECT build.
- Detectors that move with them: S1241 (embedded text one byte short; detector "meas_store_check.c's text =
  file compare", i.e. (iii)) and S1232 (canonical writer drops cells; detector includes "R4 on the store",
  i.e. (i)). The design lists S1241 only as "anchors re-read" (§8.2 DEFAULTS row) and S1232 only at S2a; their
  DETECTORS change at S2e, which is an intent re-verification, not an anchor re-read.
- §3.8's reader list ("`memfn_measures`, the listing, `meas_store_check.c` (pre vs fresh, both cell-less),
  `--measures=NAME` stamps") misses run_measures_tests.sh's STORE R4/R5/text compares; and
  `tests/knowledge/CLAUDE.md` (STORE description) and measures.md §6¶2's last sentence ("Every committed set
  file equals its own canonical view") need the FILE-vs-NAME distinction stated.
- Interaction with READY-1: if the fix makes the loader resolve a delta row's input against this set's cell
  ARMS, the cell-less embedded text no longer parses (`meas_store_check.c` :70-75 "does not parse"; every
  NAME compile refused). The input rule must be "an arm of the set's cells when cells are present", or the
  embed must keep the base cells, or the base must not be an `inputs` reference — one decision, both units.
- Also the design doc: measure_sets.md §8.3 (:1457-1471) "Embedded = committed" ("compares each embedded text
  with `set.tsv` byte for byte") is amended by the cell-less rule and is not in §10.2's measure_sets rows.
- Fix (text): S2e's package lists the three STORE compares re-aimed (R4/R5 on `--list-measurements=FILE`
  for the cells, plus NAME's view = FILE's view with `cells` emptied; embedded text = file minus section
  `cells`, computed by the runner), S1241's and S1232's detectors re-verified (intent), and the CLAUDE.md /
  §6¶2 wording.

### READY-4 CONFIRMED — the embedded TEXT is written by `scripts/embed_text.sh`, not ksgen; S2e's package and sabotage (v) name only ksgen, and (v) names no check
- Severity: completeness (S2e) / witness. Effort: text. Blast radius: S2e.
- Makefile:358-362 at 6f1b40f75 (`gen-%`): the text step is `$(KS_ENV_$*) sh scripts/embed_text.sh
  $(KS_TEXT_$*) $(KS_TEXTSRCS_$*)` and only the pre-parse is `ksgen`. embed_text.sh:2 "embeds each FILE's
  bytes, unmodified" — a POSIX-sh/od encoder shared with the findings store (:31-39, EMBED_KIND). §3.8 "The
  embed" ("built (`make gen-measures`, `scripts/ksgen.c`) ... WITHOUT section `cells`, text and pre-parse
  alike") and §8.2's built-in-sets row ("`scripts/ksgen.c` omitting `cells`") miss embed_text.sh, whose
  "unmodified" contract (and its header comment, scripts/CLAUDE.md's entry, measure_sets.md:605's text-step
  sentence) changes, or which needs a cell-stripping step before it.
- Sabotage (v) "ksgen embeds the `cells` section": the TEXT half of the plant would be in embed_text.sh
  (or the strip step), not ksgen; and its detector ("`file_cells` ... and the embedded view's empty `cells`
  disagree, and the pre-parse's cell table is non-empty where the rule says none") names no check file or
  assertion. Today's checks would not see it: meas_store_check.c compares pre vs fresh of the SAME embedded
  text (both carry the cells if both were planted), and READY-3's re-aimed text compare decides the rest.
  Also unstated: where `file_cells` comes from (the embed has no cells; ksgen must record the FILE's count).
- Fix (text): S2e names embed_text.sh (or a strip step) in the package; (v) splits into (v1) the text step
  keeps cells -> the re-aimed "embedded text = file minus `cells`" compare (run_measures_tests.sh) and (v2)
  the pre-parse keeps cells -> a named assertion that every embedded set's pre-parse has 0 cells and the
  listing's `file_cells` equals the FILE's cell count by awk; state that ksgen writes `file_cells` from the file.

### READY-5 CONFIRMED (text) — S2c's slot sabotages (j), (j2), (k), (l) have no runner; the placement "assertion" is a re-draw filter with no bound; (l)'s gate is count-only
- Severity: witness (S2c). Effort: text. Blast radius: S2c.
- §9 "Sabotage ids are the kit's, taken ... from the top of the free range" (S-rows: tests/mech/sabotages/,
  highest S1856 at 6f1b40f75). An S-row is run by `tests/mech/run_sabotage_matrix.sh`, which runs only the
  suites of its closed SAB_SUITES vocabulary (:177ff). The detectors of (j), (j2), (k), (l) — the `nm`
  placement assertions, the cell-text hash check, the answer gate — run only in the slot harness's
  `--dry-run`, which no suite runs ("never built by make", §3.1). So as S-rows they cannot score DETECTED.
  Precedent for a slot-local sabotage runner exists (docs/design/memfn/r17b_prime/b3a/sabotage/run_skb3a.sh,
  e8min/sabotage.py); the design must name it (a `slot/sabotage.sh` that plants, runs `--dry-run`, expects
  the refusal) or say these rows are not S-rows.
- (j)/(j2): §3.2 "a draw failing either is re-drawn (seeded, deterministic)". Under plant (j) (pads ignore
  the launch) or (j2) (twin forced to its arm's phase) every re-draw fails the same way: unless the re-draw
  loop is BOUNDED and refuses after K attempts, the plant hangs the dry run instead of "refuses". State the
  bound (and that exhausting it refuses).
- (l): the answer gate compares COUNTS ("find-all count ... against the generator's planted count"). A plant
  that returns each hit shifted (pos+1) keeps the count; name the planted wrong find (e.g. libc searching
  another byte: count 0 vs E), or gate on a position checksum (sum of found positions), which costs nothing.
- (o) holds but by a crash: `finder_check.py` digest() (:313-324) does `int(r["value_e6"])`, so a format-2
  draft with any `null` row raises ValueError before the digest compare; still red, not the stated reason.
- Also doc: §3.1's table and §3.8 step 2 spell `pcrec --list-measurements FILE` / `... draft.tsv`; cli/main.c
  :1567-1573 takes the set only as `--list-measurements=X` (the bare flag is the index; `draft.tsv` is then a
  stray argument). Spell `--list-measurements=draft.tsv`.

### READY-6 CONFIRMED (text/design) — the recompute "reads ONLY the set file" but its floor and `partial` need three inputs outside it
- Severity: check (Goal 3) / design. Effort: text + one format decision. Blast radius: S2c's spec text, S2e's check.
- §3.4 (:570) "The recompute reads ONLY the set file: header, cards, rows (their `inputs`) and cells" vs §3.5
  (:672-676) "The one recorded input the recompute takes as given is the run summary's list of groups that
  never ran ... in PROVENANCE.md" — a prose file, with no machine format stated.
- Goal 2's floor (§1, §3.5) needs more than that list: "for each census (form, cls), at least one
  `verify_cmp` row" and "every `enter.<kind>.NONE` row" need the CENSUS population (census0.out, not in the
  set); "pair unless J1 (b) holds pair out" needs J1's verdict (`slot/j1/verdict`, explicitly NOT in the set,
  §3.6). A never-ran group's keys are not recoverable from a group name. So the "exact" recompute of the
  floor and of `partial` (Goal 3) cannot be written from the set alone.
- And the floor is the KIT's card-set property (row-1 keys, forms, census), but §3.5 is to be measures.md's
  new spec section, whose format "reads no owner's vocabulary" (§2.3¶2): the floor's key list does not belong
  in measures.md.
- Fix: name every input outside the set (never-ran groups WITH their keys, J1's verdict, the census key
  list), give each a machine-readable home and format (e.g. a `#`-free TSV beside set.tsv covered by
  PROVENANCE's sha, or a `floor` file in span_cards/slot/), amend :570, and home the floor's key list with
  the kit (card table or slot), leaving measures.md §3.5 the generic "a set's declared floor" rule.

### READY-7 CONFIRMED (text) — S2d's committed outputs have no owning unit
- Severity: maintenance/separability. Effort: text. Blast radius: S2d, S2e.
- S2d is "— (a measurement)" with no commit; S2e's content does not name them. Unowned: `span_cards/slot/
  j1/verdict` and `j1_cells.tsv` (§3.6, "J1's evidence home"); the `ofsskip.c` comment UNMEASURED -> MEASURED
  under (a)/(c) (§3.6; §8.2's row gives it package "none" and NO unit); the per-round transcript's location +
  sha (§3.8 PROVENANCE); the plan-row filing under (b). Fix: S2d (or S2e) lists them as its commit.

### READY-8 CONFIRMED (design/doc) — "rows carry no deps" leaves zen4-grid3 with no form-hash record, contradicting measure_sets §2.4/§7.2 and this design's own staleness claims
- Severity: maintenance (permanent: a committed rev never changes, measures.md §8¶1). Fix-induced (CHECKC).
- §2.4 (:296) "Every zen4-grid3 row's `deps` column is `-` ... only the cards carry deps" — and a card's
  deps are TEMPLATES (`kit:form.<form>`), not hashes. measure_sets.md at 6f1b40f75 §2.4 (:632-634) "A row's
  `deps` column holds `;`-joined items `owner:dep-id=hash`, written by the producer from the card's `deps`
  declaration", staleness defined on them (:663-668); §7.2 (:1228-1230) "The checker refuses a row ... whose
  `deps` lacks a card dep". Neither amendment is in §10.2 (which lists §7.2's `lengths`/`aa_rule` only).
- The design still claims staleness through the hash: §3.6 ("their form hash moves with the literal"),
  §11 Q3 ("A PAIR width retune stales the PAIR cards through their form hash"). With no recorded hash in
  the set, no future staleness implementation can see a PAIR retune for zen4-grid3@1, ever.
- Fix: record `kit:form.<id>=<hash>` in each form-bearing row's deps (the producer has it: the cell-text
  check computes it), so check C's measure_store pass reads the RECORDED hash (sharper than resolving the
  token); or keep `-` and amend measure_sets §2.4/§7.2 (§10.2 rows) and withdraw the §3.6/§11 staleness claims.

### READY-9 CONFIRMED (doc) — separability: S2a is NOT independent until S2e
- §9 LOCK: "S2a is independent until S2e". But S2c's spec hunks (§4.4: new §3.4's `events` column, §2.2¶5
  "a format-2 set carries in `cells`...", the §2.2¶3 format-2 `inputs` rule) describe format 2, which S2a
  introduces (§2.1¶1a, §2.2¶1a); landed before S2a they cite a format the spec does not define, and S2c's
  plant (o) needs a format-2 file. The paragraph's own revert sentence admits the coupling. With READY-1's
  loader change in S2a, the edge is hard. Fix: "S2a -> S2c (spec), S2b -> S2c -> S2d -> S2e".

### READY-10 CONFIRMED (doc) — libpcrec's growth "reported (artifact_size_log.tsv's neighbour figure)": that file holds no libpcrec figure
- `docs/dev/artifact_size_log.tsv` at 6f1b40f75 is a per-PATTERN emitted-artifact size log (columns pattern,
  engine, rungs, prefilter, size_bytes, ...). Fix: S2e reports `size -t build/libpcrec.a` and `size -A
  build/obj/core/measures.o` base vs head (tree_drill.py D's own method) in its report.

## PROBED-AND-HELD

- Build tree = design tree for every cited code/data path: `git diff --stat 6f1b40f75 ef2f130fc --
  tests/memfn/finder_check.py src/core/ks_measures.c memfn/src/formhash.c memfn/data/cards/kit-grid.tsv
  docs/spec/measures.md docs/design/measure_sets.md measure_store tests/knowledge scripts/ksgen.c
  memfn/src/kit.h` is empty.
- Cites that HOLD at 6f1b40f75 (file:line): formhash.c:19-31 (normalization), :237-277 (`canon`, walk `[0-9]`
  by table, libc `x`, `on_miss "return 0;"`), :291 (`mf_art_begin(..., MF_P_PORTABLE_ONLY, ...)`); kit.h:
  546-555 (`fd_stop.renders_pair`; kit.h is memfn/src/kit.h), finder.c:656; ofsskip.c:275-279
  (`ofs_pair_decl`, `wa = 128, wb = 128`) and :267-272 ("its TIME is an UNMEASURED DEFAULT"); finder_check.py
  :313-324 (format-1 digest), :337-343 (card walk), :395-399 (key loop, form-first test), :343-374;
  measures.md has §2.2¶1-¶4 and no §3.4/§3.5 (so "new" holds), §5¶6, §6¶1-¶2, §8¶1-¶3 as quoted;
  measure_sets.md §1.4 (:381), §1.5 (:414, "Cells no row reads are not committed" :431), §1.7 (:500), §7.1-
  §7.4 (:1176-:1294), §3.6 (:878), sizing sentence (:626-628), §9.3/§8.4 (emit_sweep data mode); emit_sweep
  DATA_KINDS = ("analysis", "limits") (:2783) and "joins at M1" (:2766, :2895); docs/dev/lanes/m0build/census.py
  exists; movers/0001.tsv's shape is as §5 describes (header keys seq/class/old/new/code_commit/population/
  movers, `#section movers` `artifact moved first_difference`); index.tsv columns incl. `supersedes`,
  `status`; DEFAULTS `idk zen4-grid1@1`; DEFAULTS.log row 1 as quoted; S1228/S1229/S1237/S1241/S1245/S1246
  exist and S1229's SAB_BEFORE is `{ "idk", "zen4-grid1", 1u },` in measures_table.inc;
  run_measures_tests.sh:75 is a floor `>= 1` and :77-94 the DEFAULTS/default_for/DEFAULTS.log check;
  650-covertime-slot's `--ready` (load1 < 2.0, two samples >= 55 s), BOILERPLATE:236 (quiet only at start);
  boxqueue `--ready` 77 = never, `expect NAME=N lines=ERE`; r17b_prime.md:2040/:2059/:2061/:2063;
  regime_eval.md exists. 6f1b40f75's tests/mech/sabotages top id S1856.
- kit-grid.tsv at 6f1b40f75: 10 cards, 9 with a `kit:form.` dep, all `form` first (tree_drill.py C,
  re-run on the buildtree export: same). kit-kernels.tsv 5 more (READY-2); kit-synthetic.tsv 0.
- tree_drill.py on the buildtree: A rows 49 / form-bearing 40 (find_byte 4 + find_hit 20 + verify_cmp 16);
  B 195 points, 21.6 min timed, 1,008 set cells; D 23,788 B grid1 embed, ~15.8 KB grid3 cell-less — all as
  §2.5/§3.7/§3.8 quote.
- drill.py (1)/(2) re-run: every §3.5 table row reproduces (clean 60000/92; bimodal non-unit 2034
  REFUSED; A/A +600 -> 604 PASS, +2000 -> 2001 REFUSED; delta mixed/negative null, clean priced; drift
  0.03 % / 3.0 % refused / 2.0 % < 4.96 % kept; end to end 147 cells, unit exactly 10^6, libc 63298).
- Sabotage rows that CAN fail as written (named check sees the plant, correct build green): (m) pairwise
  distinct (with walk-set folded into walk by design when equal); (n) guard in the card walk sees a
  kit-grid@3 card with `kit:form.` dep and non-`form` first dim (the existing 13-column check passes it);
  (o) red (by crash on null rows, READY-5); (p) the recompute recomputes noise_e6 exactly (isqrt_rn, rhafz
  integers) so +1 is seen, provided the recompute does not stop at the stale digest first (also red: still
  DETECTED); (u) the measure_store pass resolving a renamed token to no hash (`form` dict from
  arm_fixtures `--hash`, finder_check.py:252) — needs the new ids added to arm_fixtures.c hash_mode's `ids[]`
  (:1652) and check_hash's resolve list, which "R-MS3's two fixtures per new id" implies; say so.
- (q) partly: an edited cell is always seen by run_measures_tests.sh's file-sha compare (:66-72), but the
  recompute sees it only if the cell moves a median/trim/isqrt result — name the planted cell (e.g. the
  unit's median-launch 1 Mi walk cell, which moves W and every row).
- r5 fixes for S2c-S2e present in the text: CELLS-1 (a)-(e) (events column, `round med`, `J<j>.<name>`,
  one base rule, launch = (job, l)); CELLS-2 (domain, refused cells kept, J1 home, never-ran input — but see
  READY-6); CELLS-3 (grammar without placeholder, `bimodal-test`, §7.2 + column comment at S2c — but see
  READY-1, fix-induced); CHECKC (guard in the card walk, measure_store pass — see READY-2, READY-8);
  HASH (one renderer, cell hash = site text); TWIN (linked addresses, not object bytes); PLACE (per-launch
  draw, fixed `ctl`, placement screen, HELD); DRIFT (proxy argued, power stated); Z (re-drilled with aa,
  one event); FLOOR (paired aa_D, FRG dropped); CENSUS (movers.py named, 0002 shape); EMBED (main's ruling
  (d) applied — see READY-3/4, fix-induced); GOAL2 (floor, REFUSED not PARTIAL); J1-WIN (J2p, 77 under
  (b)); LOCK (stated — see READY-9); J3 (counts reproduce); INDEX (supersedes empty, both current); D149
  labels (pad range, "3 of 4", factor 3, margin 2, "5 of 8").
- docs/spec/cli.md §2.9a defers columns to measures.md §6 (no hunk needed for `file_cells`).
- The `--list-measurements` index reader run_measures_tests.sh:84 reads `default_for` POSITIONALLY ($8):
  `file_cells` must be APPENDED after `source` (state the position in the §6¶1 hunk).

## Per-unit verdicts

| unit | verdict | what must change first |
|---|---|---|
| S2c | **ready with listed text fixes** | READY-2 (population 17), READY-5 (slot-sabotage runner, bounded re-draw, (l)'s plant, `--list-measurements=`), READY-9 (S2a -> S2c), and READY-1's decision for its §2.2¶3 hunk (move it to S2a with the loader code, or drop it if the base moves out of `inputs`); arm_fixtures `ids[]` named (PROBED (u)) |
| S2d | **ready with listed text fixes** | READY-7 (its commit: j1 evidence, ofsskip.c comment, transcript sha, (b) filing). Its own jobs, populations, window and quiet handling hold; it times S2c's harness, so it waits for S2c's fixes |
| S2e | **NOT READY** | READY-1 (the set cannot load: measured rows may not name inputs, arms are not cells), READY-3 (cell-less embed reds three STORE checks + S1241/S1232 detectors in the correct build), READY-4 (embed_text.sh, (v)'s check), READY-6 (recompute inputs outside the set; floor's home), READY-8 (no hash recorded; contradicts measure_sets §2.4/§7.2 and §3.6/§11), READY-10 |

**Round verdict: NOT READY.** S2c and S2d are ready once their text fixes land, but READY-1 is a format
decision (S2a's loader, S2c's spec hunk, S2e's set, and the cell-less embed all meet in it), so a rev 1.2
must settle it before S2c's spec hunk is written. Two of the S2e blockers (READY-1, READY-3) are
fix-induced by rev 1.1's CELLS-3 and EMBED fixes; READY-8 by CHECKC.

## Standing questions

**SIBLING OF A FAMILY.**
- **The mover census (`slot/movers.py`) IS a third member.** Members: `docs/dev/lanes/m0build/census.py`
  (0001), `scripts/emit_sweep.py --data KIND OLD NEW` (analysis, limits), and now `span_cards/slot/movers.py`,
  "a copy of m0build's census method". measure_sets.md §9.3/§8.4 (Frank 2026-10-14) homes the DEFAULTS
  transition census as emit_sweep's `measures` data kind. The design's D77 argument ("its first use is M1's")
  does not hold: S2e IS a DEFAULTS transition, the use §8.4 names. r5 CENSUS's ruling accepted either
  option, so this is not a defect, but the general-mechanism rule favours building `--data measures` at S2e
  (two arms: OLD vs NEW default and the forced `--measures=` pair) and deleting the copy. Recommendation:
  build it; else a §12 row with trigger "the next DEFAULTS transition" (row 1's).
- **The slot harness**: the 4th-5th hand-built slot harness (650, grid1, grid2, b3a/e8min, span_cards) —
  FAM-B is filed; its trigger "a second harness that needs placement" is too narrow for a family already
  past three: make it "the next slot harness written".
- **The recompute check**: a 4th python reader of set files (ks_ref.py, finder_check.py's read_sections +
  digest, memfn/data/sets/generate.py's digest, now the recompute). Independence is required from the SLOT
  harness, not from ks_ref.py: the recompute should import ks_ref.py's parser (one pcrec-side spec reader)
  rather than a fifth parse.
- **The placement draw**: first member (no other harness draws per-launch pads); FAM-B covers it.
- **Check C's card guard**: an extension of the existing card walk (one loop), not a new family; it IS the
  measure_sets §7.2 "row off its card / deps lacks a card dep" checker's first piece — see READY-8.

**GENERAL FORM + UNLOCKS (with triggers).**
1. **The base as a cell reference, not a row input** (READY-1's general form): a format-2 `cells` row may
   name the arm it is the base OF (or the card names a base-arm column), so rows never carry arm names and
   the loader's input rule is unchanged. Unlocks: no loader exception, the cell-less embed stays parseable.
   Trigger: rev 1.2's READY-1 decision.
2. **A machine-readable run record inside the set** (READY-6): a `run` section (never-ran groups with their
   keys, the floor's declared keys, J1-type gate verdicts), hashed by the file sha. Unlocks: "the recompute
   reads only the set" becomes true; M3 writes the same section. Trigger: rev 1.2 (Goal 3).
3. **Recorded form hashes in row deps** (READY-8): `kit:form.<id>=<hash>`; unlocks measure_sets §2.4's
   staleness for every kit set and lets check C's pass compare the recorded hash, not only resolve a token.
   Trigger: the first staleness implementation or the first PAIR retune ((b)), whichever first — but the
   choice is permanent for zen4-grid3@1, so decide at S2e.
4. **`emit_sweep --data measures`** (above). Trigger: S2e (now) or row 1's flip.
5. §12.1 (estimators as registry derivations) would ALSO absorb READY-1 (a `delta` row as `arm-minus-base`
   over cell ids), but collides with §4.3 (derived rows carry `-` noise): its trigger should add "a measured
   row whose value is a derivation over cells needing its own noise".
