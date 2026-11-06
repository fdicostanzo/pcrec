# READY critic: arev2

Question: if the owner gave a build go for S3 (the proof step) and its prerequisites S1 and S1M,
with vlookbehind stage 1 (`range`, rev 3) landing first, could a build lane start each unit from
this text? Subject: `docs/design/stream/arev.md` rev 1 at 0f7d79795; build tree e20dee230 (review
tree `worktrees/crit-arev2`, HEAD verified e20dee230d09a5). `git diff --stat fd1a32021 e20dee230 --
src tests scripts` is EMPTY, so no code anchor moved between rev 1's anchor commit and the build
tree.

## Findings

### READY-1 — The client's own row has two owner texts that disagree; rev 3 adopted none of arev's five proposals (CONFIRMED; design/answer; blocks S3)
- arev §3.1 "This is the client's own row": the `!has_bot` conjunct and its order, `lang = same`
  instead of "exact", the per-branch verdict, the cursor spelling, and two prerequisites read
  differently are "PROPOSALS to the client's owner document, which is vlookbehind's to change".
- vlookbehind rev 3 (e20dee230), written later, keeps the OLD row. §5.4 (vlb3 lines 1087-1135)
  says "Exactness is read from `Nfa.erased == 0`". It has no `has_bot` (grep: 0 hits in the whole
  file). Its prerequisites still list `[LANDWALK-VM]` (line 1130). Its trigger is still D77, "a
  measured cell where the lookbehind's candidate tries dominate", although the owner ruled a PROOF
  step with no trigger. §6 line 1454 says "Stage 3 (HELD): `reverse-dfa` ... witnesses WD1-WD6".
- The two witness lists share ids but not cells. vlb3 §7 "Stage 3's witnesses": WD1 =
  `(?<=(?>a|ab)b)x`, WD2 = W10's cell, WD3 = W1's, WD4 = W5's gap cell, WD5 = W7's. arev §3.1 has
  WD1 = `(?<=(?>ab|a)b{1,2})x`, WD2 = `(?<=(a{1,2})|(aa{1,2}))c`, WD3 = `(?<=(a{1,2}))b`, WD4 =
  `(?<*(a{1,2}))b\1c`. arev also adds WD-G, WD-A, WD-B and WD8. Rev 3 has none of these.
- rev 3 §16c's 11-item pick-up list runs only vlookbehind → arev. Nothing carries arev → vlookbehind.
- Failure: a lane given "build S3" opens the client's owner document and finds an admission
  without the F1/F2 screen (`\G` gives a SUBSET machine; `^` gives an internal-error refusal),
  which is the review's answer-level miscompile.
- Fix: the manager rules which document owns the row's admission, witnesses, prerequisites and
  trigger. Either vlookbehind rev 4 takes proposals (1)-(5) and arev's WD list, or both notes say
  arev §3.1 supersedes vlb §5.4/§7 stage 3.
- Effort S (text). Blast: S3, vlookbehind stage 3.

### READY-2 — arev rev 1 still builds against rev 2's loop: the 11 pickups are not applied (CONFIRMED; doc/answer)
- rev 3 §16c lists 11 pickups at arev line numbers. All of them stand in rev 1.
- Line 401 still says "NOT YET RULED".
- Lines 422-430 and the reader table's brackets still carry the rev-2 spelling.
- The charge is `k + (candidates − 1)` (line 462). The one-way give-up argument is per candidate
  (pickup 4: it must be restated on TOTALS, since the cursor shape charges per step).
- The finisher contract cites "rev 2 §5.1" (pickup 3: row 3 SHARES rev 3's `L_try_i`/`L_body_i`/
  `L_end_i`, which are not merely the same shape).
- The trail column is unresolved: is the term "2 + varying branches" or per row (pickup 5)? Its
  reader, `vm_cost_look` (emit_vm.c:2858, W12's sabotage site), is not in any reader list.
- W-trail's cell (pickup 10) needs a superset machine with at least four confirm-failing accepts.
- Readiness consequence: rows 2 and 3 emit into rev 3's label set, and the row-3 sketch (arev
  lines 405-418) has no `L_end_i`. A lane cannot write row 3 from it without re-deriving rev 3.
- Fix: apply pickups 1-11 (a rev 2 of arev). Effort S.

### READY-3 — `R19 does not rise ([ROWCONJ]'s conjunct type)`: that type does not exist; [ROWCONJ] is not started (CONFIRMED; maintenance; S3 ratchet)
- arev §4.1, the S3 ratchet cell: "R19 ... do not rise (... [ROWCONJ]'s conjunct type for (a)-(e))".
- At e20dee230, `grep -rn RowConj src` finds nothing. plan.md line 844: `[ROWCONJ] STATE:not-started`.
  The roadmap §5 R19 recipe counts "private conjunct structs among `CompConj`, `CoverConj`,
  `RevendFormRow`, `lmwalk_conj[]`'s, minus 1" = 3.
- Rows 2-3's five conjuncts need a conjunct list. Without [ROWCONJ], that list is a fifth private
  struct (R19 3 → 4, a rejected step under the ratchet rule) or a borrowed one.
- Fix: list [ROWCONJ] as an S3 prerequisite, or state R19 +1 with its deletion. Effort S (text);
  M if [ROWCONJ] is built first.

### READY-4 — [GIVEUP-DIFF] as specified cannot see this row, and the row's lever is not chosen (CONFIRMED; design; blocks S3's gate)
- [GIVEUP-DIFF] (plan.md line 850; locate_finish.md lines 479-503) is "three additions to `make
  test-axes`' GIVEUP1 relation". GIVEUP1 compiles the corpus "default vs each DENY". Its direction
  rule reads "the row's classification", the derived `(row, route)` posture of a LOCATE row
  (`.giveup`, `CG_FIXED`). Its trigger names only "locate_finish L3, L4 or L5 or [LANDWALK-VM]".
- The lookbehind row is not a LOCATE row and has no `.giveup` classification column.
- arev §3.1: "The lever is test-only unless a regime can be slower after narrowing". A test-only
  lever is not a `make test-axes` deny axis, so GIVEUP1 has nothing to compare. No "test-only
  lever" mechanism exists in src/ or docs/spec/: every force/deny lever is a `PCREC_NO_*` /
  `PCREC_FORCE_*` flag.
- The same unnamed lever is what §3.1's gate means by "the row forced on and with it denied", and
  what the size-cap rung would set (READY-6).
- Missing for a lane:
  - the lever's spelling: a public `-fno-…`, which costs a flag bit (see [IFACE-PUSH]/[FLAG-ACCESS]),
    or a named test-only mechanism;
  - where the row's ONE_WAY classification is declared;
  - the constructed ONE_WAY witness, which locate_finish item 3 requires "per ONE_WAY row" and
    arev does not name.
- Fix: the manager rules the lever. Add the row to [GIVEUP-DIFF]'s trigger and scope. Name the
  witness: a budget cell where `range` gives up and row 3 answers, for example W12(a)'s shape under
  `--work-budget`. Effort S (text) + M (axes).

### READY-5 — The per-part oracle is wrong for every `superset` part, and partial for `same` (CONFIRMED; design; G3/F3)
- arev §0 G3 and §3.1 "Per-part oracle": the part's answer is "the smallest `s ≥ bound` such that
  libpcre2 matches `B` anchored at `s` ending exactly at `from`".
- (a) For `lang = superset` this is not the part's contract. arev's own counter-example (§3.1
  STOP RULE) says the erased machine of `(?>ab|a)b{1,2}` "accepts at 0" on `abx`, where libpcre2
  finds nothing (probe: `(?:(?>ab|a)b{1,2})` on `ab` → nomatch). The correct part sits AT 0
  while the oracle says −1, so the oracle fails a correct part by design.
- The superset contract is one-sided: every true start is returned, and the answer is ≤ the
  true one. So the oracle must check containment, not equality.
- (b) "comparing `ovector[1]`" tests only the PRIORITY end. Probe: `a|ab` on `ab` → [0-1]. For a
  one-branch `B = (?:a|ab)`, `from = 2`, a correct part answers 0, while the ovector oracle says no
  start ends at 2.
- Only the callout form (force a backtrack unless the position is `from`) is an oracle.
- Fix: state the oracle per `lang` value (`same`: equality, via the callout form; `superset`: the
  true start set ⊆ the part's accepts). Drop "comparing `ovector[1]`". Effort S (text).

### READY-6 — The size-cap rung: its readers are not listed, and its deny column needs the lever of READY-4 (CONFIRMED; maintenance/doc)
- arev §2.4: "a size-cap RUNG in `fit_rungs[]`, in H-LADDER's declared append shape". H-LADDER's
  shape (roadmap) covers `fit_rungs[]`, `FitAct`, `fit_seq_legal[]`, `COMPILE_MAX_ATTEMPTS`, the
  driver case and the note. The rung has readers outside that shape, all at e20dee230:
  - `docs/spec/limits.md` §8.4's rung table (rows 0a and 2a), whose last column names each rung's
    public flag (`-fno-landmark-walk (the whole form)`). A rung with a test-only lever has no
    entry for that column;
  - `docs/spec/tuning.md` ¶2.15p4 / ¶2.54p5 (the rung order sentences);
  - `tests/codegen/run_fallback_table.sh` (its `fseq`/`frec` rows under the `trlowsize` build,
    lines 327-400);
  - `tests/mech/sabotages/S238_size_drop_unstamped.sh` (enumerates the rungs that stamp
    `size-cap-retry`), plus a twin of `S1826_lmwalk_rung_unattributed.sh`;
  - `src/dump/axes_dump.c:961` (it lists `fit_rungs`).
- S1M is said to "declare" the rung's shape and S3 to build it. Neither unit names a witness
  that can fail for the rung, such as a `trlowsize` cell where the lookbehind's machines push the
  artifact over the cap.
- Fix: list these readers and the witness, and put the rung in ONE unit. Effort S.

### READY-7 — S1M "moves EVERY machine" but omits two and lists one reader of about 110 (CONFIRMED; maintenance)
- arev §2.4 and S1M: "`dfa`, `rdfa`, `adfa`, the lowered set, `lmdfa`, and the lookbehind's". The
  `Job` struct (internal.h lines 3436-3505) also holds:
  - `nedfa`, the MANDATORY [FINDALL-NEXT] retry machine (16 references, in compile.c and
    emit_dfa.c). Its walk is `pcrec_emit_dfa_retry`'s run-time `DfaDir` copy, which S1 folds;
  - `xprio`, `mark_prio`'s probe.
- Readers by grep: `job->dfa` 45, `->rdfa` 19, `->adfa` 24, `->lmdfa` 8, `->xrdfa` 7, `->xdfa` 4.
  They sit in compile.c, emit_dfa.c, emit_vm.c, lmwalk.c, known.c and internal.h. arev names only
  `dfa_member_machines` (and its fixed `out[4]`).
- Fix: name `nedfa`/`xprio` (in or out, with the reason), and give the reader set as a grep recipe.
  Effort S (text). Blast: S1M's cost is likely above "M".

### READY-8 — Not every witness can fail in the deny build, though §3.1 says "every cell can fail in both builds" (CONFIRMED in a byte model; doc/check)
- arev §3.1: "in the row's deny build the same cell runs `range` and is red under stage 1's own
  plants".
- The vlbrev3 `model.py` (`range` evaluator) was copied into `ready/m/`. Six of stage 1's §7
  plants were added (W1 shortest-first, W2 no end-check, W3 no body backtrack, W5 non-atomic cut,
  W11a no restore, W16 nearest never tried; script `ready/plants.py`, cells `ready/cells.txt`).
  18 arev byte cells were run.
- Reached by no modelled plant:
  - WD1 rev 1 pair (`(?<=(?>ab|a)b{1,2})x` / `(?<!…)` on `abx`);
  - WD-A positive (`(?<=^a{1,2})b`). The negative twin is reachable by W4's hard return, by hand
    trace;
  - WD-B control (`cx`);
  - both WD6 cells;
  - `(?<=a{1,2}\b)x` / `(?<=a{1,2}\b)-` of WD8.
- Reached: WD1 rev 0 cells (W2), WD-B (W11a), WD2/WD3 (W1), WD4 (W2, W5, W16), WD8 `$` (W2),
  W-restore (W11a). WD-G is W14's own cell.
- Plants not modelled: W4, W6-W10, W12-W15 (UTF/cap/startpos/trail). None of them targets an
  atomic or context body.
- These cells are reverse-machine hazards. In the deny build they are green by construction,
  which is fine, but the claim is false.
- W-UTF has NO plant at all (each of the other witnesses names one).
- In the DEFAULT build every cell reaches its named plant by hand trace (13 checked; see HELD).
- Fix: per cell, name the deny-build plant, or mark it "row-only (deny build: control)". Give
  W-UTF a plant (for example the part accepting mid-character). Effort S.

### READY-9 — [VMREC]: S3 lists stage (c) but not (b), which plan.md orders before it (CONFIRMED; doc)
- plan.md line 239 [VMREC]: "next: (b) the analysis-free R stage on the records; (c) the analysis
  build, stage 2a first ..., after a soundness round on its lexer section and a D27 spec-first
  author".
- arev's S3 prerequisite reads "[VMREC]'s ANALYSIS stage (c)". (b), the soundness round and
  (c)'s own D27 author are all ahead of it. S3's real start is behind three [VMREC] units.
- Fix: write the chain. Effort S.

### READY-10 — No unit builds the record's text form, yet the F3/F4 checks need it (CONFIRMED; design)
- §0 G3 (golden check: record in, text out) and §0 F4 ("the record written as text and read back
  renders the same bytes") need a record WRITER and READER.
- §3.1 says only "reads the record through a test-only hook under `tests/`". In §4.1, S1's "what"
  column (the record) and S3's "what" (part + `VK_AUTO` + rows 2-3) contain neither the text
  form nor the hook. The per-part oracle is marked "INFERRED: not built".
- S3's gate column names "the golden check, the per-part oracle" but no unit owns them.
- §4.1's S3 gate also omits two of §0's checkable forms: G2's grep ("`const char *` fields that
  hold C") and F4's round trip. S1's gate omits G2's grep too, though G2 says "after S1".
- Separability: the golden check, the oracle and the round trip are each a separable test lane
  once the record type and the part renderer's API are frozen. That freeze is a field list, not a
  C struct (§9 leaves names and layout to the build lane), so it is a lane-ordering dependency.
- Fix: put the text writer/reader, the hook and the oracle in named units (S1 for the writer and
  round trip; S3 for the part oracle). Add G2's grep and F4's round trip to the S1 and S3 gate
  cells. Effort S (text); M to build.

### READY-11 — The ratchet rows S1/S3 credit do not exist in the roadmap yet (CONFIRMED; doc)
- roadmap §5 at de551e514 stops at R27. There is no R28/R28'. R03 and R10 still have their OLD
  recipes (`src/opt/revdet.c` present; `emit_landmark_walk` present).
- S1's "R28' 5 → 0" and S3's "R28', R03', R10' do not rise" cite recipes that only arev §4.3
  proposes ("the manager restates roadmap §5").
- Fix: the manager's restatement is a prerequisite of S1's gate. List it. Effort S.

### READY-12 — S1's sabotage reader set is wider than its five re-aims (SUSPECTED; maintenance)
- S1 folds the `DfaDir` objects, the two literal printers and the form derivation inside
  emit_dfa.c. 183 sabotages anchor `SAB_FILE=src/gen/emit_dfa.c`. 36 of them name an S1-touched
  token in their text (for example `S72_reverse_skip_blind_sfound.sh`'s anchor, which spans
  `stay_advance(f, K, f->dir->scan_more)`; S73; S82, whose anchor `gseed ? "search_from" : "0"`
  is a floor literal).
- S1's gate lists "five sabotage re-aims" (S74, S1825, S1827, S759, S760).
- To confirm: diff an S1 build against `tests/mech`'s anchor check (`SAB_COUNT` mismatches).
- Fix: phrase the gate as "the sabotage matrix's anchor check: 0 missing anchors; the five named
  rows also DETECTED". Effort S.

### READY-13 — Small text gaps a lane would trip on (CONFIRMED; doc)
- (a) The part's declared read effect "reads `subject[bound − 1 .. from]`" reads `subject[-1]` at
  `bound = 0` and `subject[n]` at `from = n`. It must be clipped to `[0, subject_length)` with the
  absent-context rule (S74), or the effect set is wrong for [VMREC] (c)'s analysis.
- (b) Row 3's `RX_CHARGE_WORK(scan_position < POS)` is a run-time expression. `VK_WORK`'s operand
  is a C string (`pcrec_vm_b_work(VmBody *, const char *count)`, vm_stmt.c line 933). Under
  [VMREC] (c) ("every analysed operand is printed by its renderer or carried as a record field")
  it needs a typed operand. That is a new MEMBER, so it does not wait, but it is unlisted.
- (c) The D27 author has no extract named. vlookbehind names `vlb_d27_extract.md` for stage 1;
  S3's promise has none.
- (d) "Bytes: ... byte-identical (the comparator)" names no instrument. vlookbehind gate 2 uses
  `tests/codegen/run_recursion_identity.sh`; §0 uses `scripts/emit_sweep.py`. Pick one.
- (e) vlookbehind §10 says stage 3 owes "a `tuning.md` §2 section for the row and ITS STAMP". arev
  owes a lever hunk and no stamp. Say which, and whether the stamp rides [IFACE-PUSH].

### READY-14 — Standing Q1: a sibling family the note misses, the in-body CALL to a file-scope function (CONFIRMED; design)
- §2.3 calls `VK_AUTO` "[VMREC] (c)'s r9 rule for kit windows ... applied to a SECOND opaque
  kind". It says rev 0's precedent is called "by the COMBINATOR level, not from the body".
- An in-body call to a file-scope function already exists: `VK_CALLOUT` (vm_stmt.c:710).
  `pcrec_emit_code_protos` (emit_code.c:142, called at emit_vm.c:14187 "before the function whose
  call sites name them") emits each code segment's prototype and binding before the VM function.
  The site calls `<binding>.fn(&ctx)`, and "gcc sees the definition, so the call is direct and
  inlinable".
- So the family is kit windows (opaque, declared effects), callout/code segments (a file-scope
  function with a slot before the matcher) and `VK_AUTO`. `VK_AUTO` is the THIRD member, which is
  past the "unify at the third" threshold.
- Consequence: the part's "own slot before the matcher function" has a precedent slot. It should
  be the same slot mechanism, not a new stream-level one, or argue why not. The effect-set field
  should be one declaration shared by the three.
- Other families the note does not name:
  - (b) automata built per site and run inside a VM body: revdet's reversed AST (structural),
    ENG-ISL's trie (`vm_isl_build`, R04, roadmap A-ISL), and now the lookbehind's table machine.
    arev lists A-ISL only as an unlock;
  - (c) the machine-language fact read after the build: `lang` (new), `RX_VM_PREFILTER_LANG`
    (exact / count-collapsed), `RX_VM_RESEED` exact/superset (locate_finish C10's classifier), and
    the landmark walk's `lmnfa.erased == 0` gate (compile.c:554). That is four readers of one fact
    family, and A-FACTS' "superset record" is its home. arev names only the stamp, as a name clash;
  - (d) row exits selected by a fact: `revend_forms[]` (form by fact), W3's AT/LOWER finisher by
    erasure, and rows 2-3's exit by `lang`. That is three members of a "first-match row whose exit
    is a recorded fact" family.
- Effort S (text). This changes S3's part-slot design.

## PROBED-AND-HELD

- **Code anchors (i).** 40 symbols grepped at e20dee230. All are present at the cited files, and
  the 26 line anchors checked by `sed` match. The list: `emit_scan_loop` :13244,
  `emit_reverse_block` :13409 (its callers :13625/:14317/:14489), `unanch_scan` :13495,
  `emit_rev_end` :14229, `emit_rev_end_one_seed`/`_tagged` (:14054/:14116 direct calls),
  `emit_landmark_walk`, `dfa_dir_landmark`/`lmverify`, `dir_rev_bound_accept` :9297,
  `dir_rev_skip` :9249, `pcrec_emit_dfa_retry` :14700 copy, `dfa_form_derive` :12962,
  `dfa_member_machines` :4916, `CT_LOWER` :9882, `CAND_HAND_AT` :9901, the `.u.locate.emit`
  :10354, `RX_VM_PREFILTER_LANG` :11311, `vm_charge` :932, `Rev` :5500, `vm_revdet_rep` :5705,
  `VL_GROUP_SEEN` vm_stmt.c:482, `revend_build_one` compile.c:454, `lmwalk_build` :547,
  `revend_choose_form` :568, the `fit_rungs` rows :1360/:1402, `pcrec_nfa_has_bot` nfa.c:1342,
  nfa.c:704 `N_GSTART`, dfa.c:1028 `gst_ok`, dfa.c:1583 `DFA_INVARIANT`, lmwalk.c:181 `gstart`,
  emit_comb.c:576, `VK_WORK`, `VSK_RESTORE`, `VPOS_REVDET_PREV`, `FitSets`. One cosmetic drift:
  `kindrow.def` is `src/core/kindrow.def` (the note gives no directory).
- **No code drift** between fd1a32021 and e20dee230: `git diff --stat` over src/tests/scripts is
  empty.
- **Gate harness exists:** `tests/lookaround/run_lookaround_diff.sh` (four sections today: the
  pcre2-only sweep, atomicity, follow-scoping, engine arms; `make test-lookaround`). The
  variable-lookbehind section is stage 1's (vlb3 gate 1), so the S3 gate's harness exists once
  stage 1 lands. The force/deny arm does not (READY-4).
- **Sabotage witnesses exist:** S74, S1825, S1827, S759, S760, S50, S51, S52, S94, S160 (10 of 10
  under tests/mech/sabotages, with their `SAB_FILE`s as the note implies).
- **Plan rows exist:** [GIVEUP-DIFF] l.850, [VMREC] l.239, [LB-EXIST] l.1710, [ROWCONJ] l.844
  (not started, READY-3), [IFACE-PUSH] l.1270, [REVBLOCK-VIEW] l.403, [ENG-LOOK] l.540, [STREAM]
  l.1678, [VLOOKBEHIND] l.685, [DEC-RUNG] l.1536. The LANDWALK-* rows are sub-rows (`  - [TAG]`):
  ALLACC l.289, WINDOW l.295, FOLD l.301, FWD l.307, VM l.313.
- **Default-build reach (ii, first half):** all 13 of these reach their named plant by hand trace
  in the default build: WD1, WD-G, WD-A (a compile refusal), WD-B, WD2, WD3, WD4 (nomatch with
  no re-walk), WD5, WD6 (vlb3's own note: only `baax` discriminates), WD8, W-restore (branch 2's
  one-length from scan_position 0 → nomatch). W-UTF has no plant (READY-8).
- **Ruling check:**
  - S3 adds exactly one new VM KIND (`VK_AUTO`), and it is listed as waiting for [VMREC] (c).
  - The part is a new stream-level unit inside S3, so it waits with it. READY-14 argues it should
    reuse the code-protos slot.
  - New MEMBERS that do not wait: a `VmLocalKind` for the call's result local, `VK_WORK`'s typed
    operand (READY-13b), a `FitAct` for the rung, plus rev 3's own `VSK_STEP_CHAR` and local
    operand.
  - S1's record and S1M's machine table are not VM records, so they do not wait.
  - S2 is consistent with "revdet's step = a representation". Its loop is left to S5's family.
  - Consequence for S3's order: S1 → S1M can run now (ride-along). vlookbehind stage 1 lands
    independently. S3 is gated by [VMREC] (b) → soundness round → D27 → (c) (READY-9), by
    [GIVEUP-DIFF] with the lever ruling (READY-4), and by [ROWCONJ] or an R19 exception
    (READY-3).
- **Separability (iii):**
  - S1 then S1M: sequential, each one lane.
  - S3's part placement + `VK_AUTO` + rows 2-3: ONE unit. With no client, no witness can fail for
    the call alone (byte-identical, unused).
  - The size-cap rung: separable after S1M + S3's machines exist.
  - [GIVEUP-DIFF]: a separable test-side lane once the lever is ruled.
  - The per-part oracle and the golden check: separable test lanes once the record field list and
    the part signature freeze (READY-10).
  - The D27 author: separable, needs an extract (READY-13c).
  - The gate harness extension: rides stage 1.
- **Owner criteria F1-F3 checkability:**
  - Gate answers: checkable by `run_lookaround_diff.sh` once the lever exists.
  - "Nothing slower": a timing artifact over the four regimes (no script named; acceptable as a
    window job).
  - F1: the diff classification is a lane-report artifact (roadmap §7 item 5), not a command. Its
    ratchet half needs READY-11.
  - F2: a grep, which is checkable but in no gate cell (READY-10).
  - F3: the golden check and oracle are not built (READY-10), and the oracle's definition is
    wrong for superset (READY-5).
  - F4's round trip is in no gate.
- **Standing Q2, the general form + unlocks.** The proof step is an instance of a CONTRACTED PART
  CALLED FROM A HOST PROGRAM. The part is any compiled component with typed position inputs,
  typed hands out and a declared effect set. The call is a record in the host's stream, and the
  part has an oracle on its own contract. Unlocks, each with a trigger:
  - (1) Lookahead-as-check, a forward `AUTO EXISTS` on capture-free regular lookaheads in a VM
    body (roadmap §4 row 12). Trigger: a bench or corpus cell where a capture-free lookahead
    body's VM run is ≥ X% of the evaluation (measured per position).
  - (2) One call record for callouts, kit windows and `VK_AUTO`, with one effect-set declaration
    (READY-14). Trigger: [VMREC] (c)'s analysis needs the third opaque kind's effects, which
    holds the day S3 lands (count of opaque in-body call kinds = 3).
  - (3) The anchored verify and atomic regular bodies as forward parts in the VM
    ([LANDWALK-VM]). Trigger: its own measured cell (the dup-param x1.33-1.45).
  - (4) Per-part oracles for every contracted part (landmark walk, prefilter window). Trigger: the
    second part with a contract lands, or a part bug found only end-to-end.
  - (5) [LB-EXIST]'s unbounded lookbehind via the same call. Trigger: its plan row's (a real
    pattern).
- **Model sanity:** the copied `range` evaluator with no plant reproduces libpcre2 on all 18 cells
  (the arev / premise.out answers: e.g. WD2 [3-4,1-3], WD4 [2-5,1-2], W-restore [2-3]).

## Verdict

**NOT READY.** S1 is ready with text fixes (READY-11, READY-12, READY-10's G2 grep). S1M is
ready with text fixes (READY-7, READY-6's rung placement). S3 is not ready:
- its client's owner document contradicts it (READY-1);
- it is written against rev 2's loop (READY-2);
- its gate's lever and [GIVEUP-DIFF] coverage are unruled (READY-4);
- its F3 oracle is mis-defined and unowned (READY-5, READY-10);
- its ratchet claim depends on an unbuilt type (READY-3).
All are fixable in text plus three manager rulings: the row's owner document, the lever, and
[ROWCONJ] before S3 or an R19 exception.
