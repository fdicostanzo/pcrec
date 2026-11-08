# Review 2026-11-07 r13 — memfn-planframe2 (design re-check): plan_frame.md rev 2.1, span_pick unit 3.0

DRAFT by the round's coordinator. Dispositions are PROPOSED; the kit manager rules them (R-35). This is the
LAST RE-CHECK before 3.0a's build (narrow round: readiness + fix-induced). The round number r13 is the
coordinator's guess at the next free number; the launcher assigns it.

## Subject

- `docs/design/memfn/plan_frame.md` rev 2.1 at **778d63147** (branch lane/memfn-u30d; the launcher's
  reference f53d50de4 adds only lane-report commits on top). Units 3.0a (kit-only) and 3.0b (seam + pcrec asks).
- Build tree: main **a678d0a4e** (unchanged through the round). Review tree built there once (`nice make -j2`, rc 0).
- Rulings frozen at main a678d0a4e (decisions.md 6fc4b6912, plan.md c90d33f54). Re-diffed at the critics'
  return and at hand-back: **no FREEZE DRIFT**.
- **FREEZE NOTES (records).** (1) The owner's composition ruling (Frank 2026-11-07: "Candidate search and
  candidate validation are two different primitive pieces that are composed"; "Yes" to "Adopt search, stream,
  check as composed pieces?"; yes to row 1 waiting for an inline one-member finder) still has no record on main:
  no D-entry (grep "primitive pieces" in decisions.md/plan.md is empty). Its only record is the kit's denied
  ledger; it was quoted verbatim to critics in COMMON. (2) Plan row RUNG-LIST (the Q13 ruling's "file the rung
  list as a PLAN row") is PROPOSED in the design's §7 for main to file; it is not on main yet. Neither changes
  a finding below; both are main's filing to do.
- Prior review r12 (`docs/dev/reviews/2026-11-07-r12-memfn-planframe1.md`, its rulings and its Q13 ruling) was
  an input.

## Lenses as run

| lens (id) | model | its one question | why chosen |
|---|---|---|---|
| readiness, unit 3.0a (READY-A) | opus | can 3.0a be built literally at a678d0a4e (cites, readers, separability, loaders over new row shapes), and can each 3.0a witness / sabotage row go red? | the lens table's "LAST re-check before a build go" row; split per unit to keep the brief narrow |
| readiness, unit 3.0b (READY-B) | opus | the same for 3.0b, plus the MF_SITE_ABI reader census and whether a D27 author could test from §2.2-§2.3 alone | same row; 3.0b is the seam event and the D27 cell's input |
| fix-induced (FIXIND) | opus | does each rev 2 / rev 2.1 fix add a read, row, field or check that breaks something (siblings, pairs of fixes on one check, populations), and did the Q13 removal leave debris? Plus the two standing questions | the lens table's re-check row |
| verifier | sonnet | re-derive 18 groups of CONFIRMED / SUSPECTED claims | skill §6 |

No third lens: the profile is a re-check of a revised design; both re-check rows cover it.

## Which lens caught what

- Unit 3.0a's buildability (census, REACH, pins, sabotage observation points): READY-A; FIXIND found the
  census strays (R4), the ST-many contradiction (R3) and the unread frame-part outputs (R8) independently.
- The seam's stored-record agreement and the D27 cell's inputs: READY-B.
- Defects the fixes themselves introduced (plan_test's stop, a zero-key G2 claim, the floor's render order,
  the impossible-cell contradiction, debris of the Q13 removal): FIXIND.

Overlaps: R2 = READY-B-6 + FIXIND-2 + FIXIND-3. R3 = READY-A-4 + FIXIND-6. R4 = READY-A-1 + FIXIND-8.
R7 = READY-A-5 + FIXIND-12. R8 = READY-A-9 + FIXIND-13. R19 = READY-B-8 + FIXIND-10. R22 = READY-B-10 + FIXIND-1.
R5 and R6 (READY-A-3, READY-B-1) are the same REACH-population gap seen from the two units.

## Findings, with PROPOSED dispositions

[V: ...] is the verifier's verdict (verify.md, V-n).

### Blocking 3.0b: rulings needed before MF_SITE_ABI freezes

- **R1** (READY-B-4) [V-8: HOLDS]. F29's fix says the kit agreement compares EVERY reply field (memcmp) against
  a reply "built from what the define STORED, never through reply_of or the plan function". At a678d0a4e
  nothing stored can supply the decision group: `site_rec` (`kit.h` :239-270) and `struct wf_plan` (`window.c`
  :1242-1274) carry no `alt`, `reseed`, stop/stop_set, `plan_term[]`, `pinned` or `run_*`; `wf_dec` is arena
  scratch; on E-func and E-stmt `wplan` is NULL (`window.c` :1947-1949), and E-func is the one site pcrec frames.
  A builder must add an unlisted record or take the forbidden shortcut. **FIX-NOW, kit manager rules the shape.**
  Recommendation: narrow. The FRAME part is compared against the stored record (what F29 and row E2 are about),
  with a per-frame field map in §4.1 (E-func: `frame_row` from `wplan == NULL` plus the legacy site's form,
  `search` from the stored BODY row, ...). The decision group is compared by re-deriving through `decide`, with
  its independent control named: the purity harness and ASK-3 (as rule 2's re-ask re-runs `select_arm`). The
  alternative (a stored decision copy in `site_rec`) costs a record nothing reads but the check.
- **R2** (READY-B-6, FIXIND-2, FIXIND-3) [V-9, V-10: HOLDS]. F12's `plan_test` does not cover the position it
  most matters for, and its TABLE condition is mis-stated. (a) C-stop removes the stop's offset from `plan[]`
  (`window.c` :1080-1081), but the stop's test kind is still chosen by `w->table[stop_ix]` (B-walk's find,
  :2553 -> :2159-2166; D-hors's probe :2652). Two asks differing only in `table_name` stated-ness, where only the
  stop is offered a table, render different text and get EQUAL replies: r12 F12's failure, on the stop. Row AB's
  "table text iff TABLE" is then red on a correct build. (b) TABLE needs the site's own offer as well as the hook
  (`offer_at`, :1281-1290, :1314), and `w->table[]` is indexed over the sorted plan-plus-stop offsets, not over
  `plan[]`. (c) The text marker `tbl[` appears in no G2 text (G2 spells `g2w_t<id>_<ref>`, `g2_win_gen.c` :569-574):
  the TABLE side of the class has zero keys. **FIX-NOW (seam shape, before 3.0b).** Recommendation: a separate
  `stop_test` member beside `plan_test[]` (keeps `plan[]`'s alignment), TABLE defined as "hook stated AND the
  covering span offers this set", the define side matched by OFFSET, and the G2 marker named as the hook's
  own spelling. Row AB's population includes a stop below a TABLE position and a stated hook with no offer.

### Blocking 3.0a: text fixes (no scope change)

- **R3** (READY-A-4, FIXIND-6) [V-4: HOLDS]. F9's rule says ST-many REFUSES, but the renderable set it feeds is a
  0/1 predicate in `fd_holds` (`finder.c` :498-511), a DECLINE inside `kit_walk`. Built literally, ST-many
  silently falls to the next T-FIND row (PAIR -> R7w, B-walk): the unmeasured choice change (D186) the refusal
  exists to stop. Sabotage (R)'s "every B-pair site is refused" does not happen. **FIX-NOW.** The gate holds on
  ST-one or ST-many; ST-many refuses afterwards with a named refusal (as `?need` does, `finder.c` :659-668);
  (R) asserts that refusal.
- **R4** (READY-A-1, FIXIND-8) [V-1: HOLDS]. F28's backstop shapes `.pick ==`, `->pick ==`, `].holds(` hit 9
  lines outside every census member at base: the Table A/M/E/fn_rows `kit_walk` adapters (`ofsskip.c` :440,
  `window.c` :726, :791, :1625), Table C's walk (:1102) and the four `b_*_holds` (:1785-1792). Check B is red on
  any stray, whatever HITS says. `].holds(` is the idiom of every declared table, not of renderer lists.
  **FIX-NOW.** Narrow the shapes to the renderer tables' names (or list the adapters as members with an
  `answers` value); state the expected HITS and MEMBER_COUNT after 3.0a.
- **R5** (READY-A-3) [V-3: HOLDS, stronger]. "REACH equality with the B rows' reach counted under the search
  renderer rows and S-restart/S-shift" counts nothing: `reach_print` covers only arms, runcmp, fn and fd
  (`gate.c` :882-908); Table B is an open loop (`window.c` :1850-1851). If 3.0a's new tables print REACH,
  `reach_equal.py` :237-240 is red on every new row and has no "new row" declaration. **FIX-NOW.** One sentence:
  the new tables print no REACH in 3.0a (they are plain first-match arrays like Table B), or reach_equal gains
  a declared `--new` set.
- **R7** (READY-A-5, FIXIND-12) [not separately verified; by reading]. The support pin
  `tests/memfn/stream_support.tsv` has no named reader, column set, or way to read the kit's table (C data). Row
  (M) is red only through that comparison, since no 3.0 frame renders MASK. The derived rows' "basis witnesses"
  need a per-site search, which is a 3.0b member. **FIX-NOW.** One paragraph: the reader (e.g. a rows_check
  section), the columns, how the kit table is printed (an `arm_fixtures` mode), the LIBC/LIBC_BACK SOURCE cells
  quoting the ruling verbatim (cell vs table, never table vs table), and the basis witnesses named as landing-time
  (emit_sweep over base text) or moved to 3.0b.
- **R8** (READY-A-9, FIXIND-13) [by reading]. 3.0a's plan function computes `fused`, `plan_test`, the reply
  ids, E-func's `search` (the new `fn_rows` pick column) and takes an allocator, but nothing in 3.0a reads them
  and no 3.0a row plants them (Y-AC are 3.0b's). 3.0a would ship computed-but-unread fields (D77,
  `pcrec-no-silent-defaults`). **FIX-NOW.** Move those outputs, the pick column and the allocator to 3.0b beside
  their readers; 3.0a's plan function keeps what the define renders. This also keeps 3.0a's "lands and reverts
  alone" exact.
- **R9** (READY-A-2) [V-2: HOLDS]. Sabotage S686's SAB_BEFORE is the two `fn_rows` BODY lines verbatim
  (`ofsskip.c` :419-420); adding the pick column breaks its anchor (setup failure, not DETECTED). G2's in-script
  plants S1423, S1427, S1428 and S1543 anchor on lines the split restructures. **FIX-NOW (XS).** Name the re-aims.
  (If R8 moves the pick column to 3.0b, S686's re-aim moves with it.)
- **R10** (READY-A-6) [V-5: HOLDS]. `rows_check.py` reads `renderer_rows.tsv` with exactly 5 columns
  (:756, :157-158) and accepts frames E-find/composer only (:765); FDROUTE prints no frame (`compose.c`
  :1153-1156), so the re-keyed frame column is checked against nothing. **FIX-NOW (XS).** Say where FUSED goes
  (a 6th column, `read_tsv(..., 6)`), and either FDROUTE prints `frame=` (trace_format.md moves) or the frame
  column is stated as documentation.
- **R11** (READY-A-8) [by reading]. (B) and (C) "assert the refusal names PAIR", but the mech runner has no
  "failing log must contain X" field, and SAB_REACH runs on the clean tree. **FIX-NOW (XS).** Name the host: an
  invariant ("no compile's refusal names a T-FIND row") in a named suite over a named population (e.g. G2's
  composer two-member sets, `foo|bar\d`), or a mech field.
- **R15** (FIXIND-9) [V-12: HOLDS]. F3's skeleton gives the floor "in order" `wf_open; wf_cand; for (...)`, but
  `wf_floor_expr` renders the TEST first (`window.c` :2320) and then `wf_open` with flags from `rc->used` (:2321).
  A skeleton writer that renders in text order drops `wf_open`'s parameters (emit_sweep catches it).
  **FIX-NOW (XS).** The skeleton row states render order apart from text order, or `wf_open`'s flags become a
  fact of the check row.

### 3.0b text fixes (before 3.0b's build)

- **R6** (READY-B-1) [V-6: HOLDS]. `purity_rows.tsv` "gains the Table E, B, S and skeleton rows", but
  `run_purity_reach.sh` :27-37 takes its population from `window.c` by three patterns (`WF_CT_A(`, `WF_CT_M(`,
  `{ N, "C-`) and plants by rebuilding `window.c` only. New ids are red against the population, or `+`-exempt
  (K35). **FIX-NOW.** Name the new population patterns and the files the new tables live in (or extend the
  plant path); list the script and `tests/memfn/CLAUDE.md` :43 in §3.
- **R16** (READY-B-3) [V-7: HOLDS]. Sabotage (I) "a framed ask walks Table E without the art's denies" is a no-op:
  Table E's walk already passes deny 0 (`window.c` :1917; `wf_etable` deny NULL), and `window-search` arrives through
  the site's `opts` (`compose.c` :170-171). **FIX-NOW.** Plant "walks Table E with the site's `opts` cleared";
  §2.2 names the mechanism (site `opts`); optionally a T-FIND-deny fixture (`--memfn=no-fd-d1`).
- **R17** (READY-B-5) [(a) SUSPECTED, (b) by reading]. (a) Row F's plant (ASK-1 states STMT/ASSIGN) may be
  refused at phase 1 (`emit_dfa.c` :7610-7613) rather than reach ASK-3, so "the suite is red" proves nothing about
  ASK-3. **FIX-NOW (XS):** F asserts the failure text names ASK-3's invariant. (b) Goal 2 describes ASK-3 as reading
  the stored record; it compares phase-1 against a re-ask (both through the plan function). **DOC:** say the
  two checks are a chain (kit: re-ask == stored; ASK-3: phase-1 == re-ask).
- **R18** (READY-B-7) [by reading]. A D27 author with §2.2-§2.3 alone lacks: `call` outside the enum; `def` NULL
  under DEFINE/EMIT and garbage under NONE; `*out` on -1 (zeroed?, which ASK-3 relies on); the list of "frame
  fields" NONE ignores and the refusals DEFINE/EMIT add (given only as code cites); an observable oracle per
  frame-part member (the text classes are in §5, not §2.3). **FIX-NOW.** State items 1-4 as contract lines and
  move §5's text-class mapping into §2.3 as each value's observable meaning.
- **R19** (READY-B-8, FIXIND-10) [V-13: HOLDS]. "The two agreement checks green on the corpus and on G2 (both
  layers)": G2's window generator is MF_P_PORTABLE_ONLY throughout (`g2_win_gen.c` :639 ... :1042), and
  `g2_simd_gen.c` states no window facts, so at the SIMD layer the agreement and Goal 5's MASK-0 have zero keys.
  The corpus carrier of the MF_TRACE agreement is not named (`make test` builds the kit without MF_TRACE; the only
  corpus MF_TRACE run is `reach_equal.py`). (The gap statement itself holds: `foo[Xx]bar` is `"none"` OFF and
  `"vrun@w32+w16"` under `-fmemfn-simd`.) **FIX-NOW (doc).** Say "G2 (OFF layer only)"; name the corpus carrier
  (e.g. `reach_equal.py --arms` including `-fmemfn-simd`, a boxqueue job) or state the SIMD agreement unchecked
  under RUNG-LIST's trigger.
- **R21** (READY-B-11, READY-B-12) [V-16 B-11 HOLDS; V-14 HOLDS]. Row AD's same-class-different-text fixture,
  built on the purity harness's 11 FUNC/RETURN sites asked through DEFINE, varies nothing (no text hook stated;
  window uses read text hooks at USE only, `window.c` :2838-2846). And `cl_miss` (`gate.c` :651-656) compares
  `miss`'s text with `n`'s, so the round-trip projection "per hook, stated-ness and class" misses a cross-hook
  relation; renaming `n` alone legitimately moves the class (a false red). **FIX-NOW.** AD's population is
  STMT/ASSIGN and STMT/ON_MISS sites under EMIT with every text hook stated, renamed relation-preservingly, plus
  one case where breaking the relation DOES move the class; §2.2 names the `miss`/`n` relation.
- **R26** (FIXIND-7) [V-11: HOLDS statically; G2 cell census not run]. G2's impossible cells say "anything but
  RESTART on E-stmt", but §2.3's own rule gives (E-stmt, NONE) for every non-PF composer arm (`fused` ARM), and
  G2 renders `generic` on STMT sites (`run_g2_win.sh` :66 floors generic:380). Two rules answer one cell; the
  tally would be red on a correct build. **FIX-NOW (XS).** E-stmt allows RESTART (PF arm) or NONE (ARM); cross-check
  NONE iff `fused` ARM.
- **R27** (FIXIND-11) [V-15: HOLDS]. F32 makes `pur_diff` a whole-reply `memcmp`, but §2.3 also has the harness
  assert that a NONE ask and a framed ask "answer equal decision fields": those replies differ in the frame part
  by construction. **FIX-NOW (XS).** Name the second comparator, `memcmp(a, b, offsetof(mf_wreply, framed))` (the
  frame part is appended last and `reply_of` memsets).
- **R25** (FIXIND-5) [V-17: HOLDS]. `mf_wsearch`'s VECTOR value and the support table's VECTOR row were rev 2's,
  for `rung[]`. With the rung list gone nothing produces VECTOR, no T-FIND row picks it, and it has no basis
  witness or sabotage cell. F8's ruling kept MASK declared; no ruling keeps VECTOR. **FIX-NOW (D77 trim, kit
  manager's call).** Recommendation: carry VECTOR and its support row to §2.5.5's NOTE / RUNG-LIST; or keep them
  with a basis witness and a Goal 5 "VECTOR count 0".

### Doc and record fixes

- **R12** (READY-A-10) [by reading]. "Split first, then the renderable set" leaves Table S and the support table
  in neither commit, though §2.6.0 has the split read Table S. **DOC:** commit 1 = §2.5.2-§2.5.3 + §2.6 (asker
  fact untouched); commit 2 = §2.4; each commit's sabotage rows listed.
- **R13** (READY-A-11). (L)'s reach excludes B-fn sites; (N) needs §2.6.2 to declare two rows with one text.
  **DOC.**
- **R14** (READY-A-7). Reader-list gaps for retired names: `units_inventory.md` :56/:111, `window_site.md`
  :272/:340/:342, `tests/memfn/CLAUDE.md` :37, `memfn/src/CLAUDE.md` :26, comments in `window.c`, `compose.c`
  :1151, `rows_check.py` :103, `decider_census.py` :74. Two `_Static_assert`s on Table B's sizes (`window.c`
  :2708-2711) retire with the split and need successors. **DOC.**
- **R22** (READY-B-10, FIXIND-1). 3.0b lists 18 sabotage rows, not 17 (rev 2 never counted E2): the note has 30,
  3.0b's range is S2994-S3011. **DOC** (three places).
- **R23** (READY-B-2) [V-18: HOLDS]. `docs/dev/lanes/r33_sim/probe.c` :94 calls `pcrec_mf_wdecide` with three
  arguments and is built by kit box-queue jobs; §3 should name it (edit, or "study, left to break"). **DOC.**
- **R24** (FIXIND-4). Q13 debris: "the `fn_rows` fact columns" (plural) in four places though one column remains;
  "top-level"/"no level" wording that only meant something beside `rung[]`; the offset-skip arm's declared
  RESTART has no named home column. **DOC.**
- **R28** (FIXIND-14). RUNG-LIST's trigger, quoted from the Q13 ruling, says "or the first MASK producer lands";
  read literally it is met today (vrun takes set lanes lowest first, `vrun.c` :317-329, and `foo[Xx]bar
  -fmemfn-simd` runs it). **DOC (kit manager restates his trigger):** "the first MASK stream RENDERER ROW lands".

### Noted

- **R20** (READY-B-9) [V-16: mechanism NOT SUPPORTED]. The suspected decline of framed E-func/E-stmt asks under
  six stated callbacks does not occur: every composer and window contract has `FLD_member`/`FLD_on_cand` =
  MF_ANY. **NOTED.** A reached-ask control (rc 0, `framed` 1 per frame beside the 0-call count) is cheap hygiene;
  the build lane may add it.
- **Standing questions (FIXIND).** (1) "Does this frame accept this piece" now has a rule for the search (the
  renderable set) and one for the stream (Table S); the check becomes the third member at the second check
  renderer row (vrun's TRIM). General form: one intersection rule over the three pieces, with ST-one / ST-none /
  ST-many as its first-match rows (it also dissolves R3). Trigger: the second check renderer row or the
  finder's MASK row. (2) The five per-frame renderer tables are siblings of `arms[]` and `fn_rows`: one renderer
  table keyed (frame, piece kind, value). Trigger: vrun's re-expression (Q9). (3) The reply's "not described"
  residues (ARM's `plan_test` NONE, the D-hors PROVES residue, the SIMD gap, `search` NONE on ARM) form a family:
  a per-piece COVERAGE fact (DESCRIBED / NONE / UNDESCRIBED). Trigger: the first reader that must tell "absent"
  from "unreported" (row 1's first record or RUNG-LIST); cheapest at 3.0b's one MF_SITE_ABI event if ever wanted.
  **PLAN** rows for (1) and (3) with those triggers; (2) NOTED.

## Readiness (per unit)

- **3.0a: ready with listed text fixes.** Every cite holds at a678d0a4e (about 85 checked across the critics).
  Before the build: R3 (ST-many: the kit manager picks the refusal point), R4, R5, R7, R8 (move the unread
  outputs to 3.0b), R9, R10, R11, R15; docs R12-R14 in the same pass. None changes the unit's scope; R3 and R8
  are small rulings, the rest is a sentence or a paragraph each.
- **3.0b: not ready.** R1 (the agreement's define side has no stored decision group; a shape the kit manager
  must rule) and R2 (`plan_test` misses the stop; a seam-shape change before MF_SITE_ABI freezes). Once those
  two are ruled, 3.0b is ready with the listed text fixes R6, R16-R19, R21, R25-R27 and the doc fixes R22-R24, R28.
- **Overall: not ready** as a whole; **3.0a may start** once its listed text fixes are in rev 2.2. No new
  re-check round is needed for 3.0a's fixes if the kit manager reads the diff; recommend a one-critic readiness
  look at 3.0b's R1/R2 text before 3.0b's build.

The D27 spec-first author for 3.0b (accepted in r12) stands; R18 lists what its inputs still lack.

## PROBED-AND-HELD (consolidated; case counts in each critic file)

- About 85 cites at a678d0a4e across `finder.c`, `window.c`, `compose.c`, `ofsskip.c`, `formhash.c`, `kit.h`,
  `memfn.h`, `emit_dfa.c`, `g2_win_gen.c`, `run_g2_win.sh`, `run_finder.sh`, `rows_check.py`, `decider_census.tsv`:
  all hold within a line or two.
- The four per-row branches F2 named are the only `== B_*` tests in `window.c` (:1868, :2723, :2731, :2760).
- §3's symbolic MF_SITE_ABI readers: 24 code lines, equal to the design's list (0 missing, 0 extra); no
  docs/spec or docs/guide hit (D80 not triggered). The `mf_wdecide` caller list is complete except R23.
- ASK-1..ASK-5 are facts and checks only (D157); every ASK-1 value equals `ofs_site_define`'s.
- Rows (A), (K), (N), (P), (Q) reach and go red at base (witness compiles: `foo|bar\d`, `..`,
  `(?:(?!a)z|w)`, `--memfn=no-fd-d1 abcdef`). Rows S, T, U, X, Y, Z, AA, AC, G, H reach their named checks.
- The D-hors split's recomposed string is byte-equal; B-pair's declaration is followed by a space the
  loop-state slot must carry (build detail).
- Rev 2.1's removal: every remaining mention of `nrung`/`rung[]`/`mf_wrung`/`mf_wcheck`/`fs`/sink/W/AE is
  history or the RUNG-LIST row (8 lines); except R22/R24.
- The stated SIMD gap holds and agrees with Goal 5 (2 compiles); the stored BODY row stays fn-pair under
  `-fmemfn-simd`, so the gap does not redden the agreement.
- F1, F2, F4, F5, F7, F27 and F29's E-stmt half (`fd_pick_of` + `fd_renderers` map the stored arm to its pick)
  are correctly applied.
- Stating all six callbacks moves no selection (MF_ANY everywhere; V-16).

## By-id completeness

READY-A-1..11 -> R4, R9, R5, R3, R7, R10, R14, R11, R8, R12, R13. READY-B-1..12 -> R6, R23, R16, R1, R17, R2,
R18, R19, R20, R22, R21, R21. FIXIND-1..14 -> R22, R2, R2, R24, R25, R3, R26, R4, R15, R19, R27, R7, R8, R28;
standing questions -> Noted. All 37 raw findings map to R1-R28; none dropped.

## Lessons for the guide (proposed)

- A fix that turns a CHECK's spelling into a backstop SHAPE (F28) must run the shape over the build tree and list
  its stray hits: the house idiom `].holds(` belongs to every table, not to the family being fenced (R4).
- A fix that says "refuse" inside a predicate that can only decline (R3) is a two-rules finding by construction:
  re-check names where the refusal is raised.
- A "compare against what the define STORED" fix must list the stored member for each compared field (R1).
- When a revision removes a mechanism (Q13), grep for the values that only existed to fill it (VECTOR, R25), not
  only for its names.

## Files

Critic texts, `verify.md`, COMMON and the verifier brief: `review/` beside this file.

## Rulings (kit manager, 2026-11-07)

- Every PROPOSED FIX-NOW is ACCEPTED: R1-R11, R15-R19, R21, R25-R27. DOC items are accepted as proposed (R12-R14, R22-R24, R28). R20 is NOTED.
- R1, the shape: NARROW, as recommended. The FRAME part is compared against the stored record, with a per-frame field map in §4.1. The decision group is compared by re-deriving through `decide`, with its independent control named: the purity harness and ASK-3. There is no stored decision copy in `site_rec`: a record nothing reads but the check is not built.
- R2, the shape: a separate `stop_test` member beside `plan_test[]`, as recommended. TABLE = "hook stated AND the covering span offers this set"; the define side is matched by OFFSET; the G2 marker is the hook's own spelling. Row AB's population includes a stop below a TABLE position and a stated hook with no offer.
- R28: the trigger is restated as "row 1 compares a SIMD-on cell, or the first MASK stream RENDERER ROW lands".
- Readiness: after rev 2.2 applies these, 3.0a may build without another round, once the kit manager checks the by-id table. 3.0b gets its D27 author at its build, as r12 ruled.
- Process change (one readiness critic per build unit): ACCEPTED for the critic skill.

## Rulings on rev 2.2's Q14 and Q15 (kit manager, 2026-11-07, at 11b522809)

- Q14: ACCEPTED as recommended. Keep the offer fact, and add sabotage row AF (3.0b becomes 19 rows).
- Q15: FDROUTE prints `frame=`, and reach_equal.py under `-fmemfn-simd` carries the SIMD-layer agreement: both ACCEPTED. `r33_sim/probe.c` "left to break" is REJECTED. Kit census jobs build it (`r33_sim/build.sh`, called by the S2f census job and its successors), so a break reddens the census instrument after 3.0b. Lane files stay frozen after merge, so 3.0b adds a successor probe beside the census instrument under `docs/design/memfn/span_pick/`, built by its own `build.sh` with the new `mf_wdecide` signature, and points the census jobs at it. The 3.0b build lane carries this; 3.0a is unaffected.
- 3.0a: GO. The by-id table is complete (27 rows; R20 noted). Build under R-35's stage 2-3 GO.
