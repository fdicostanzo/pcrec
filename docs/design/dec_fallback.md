# One fallback ladder — refactor B ([DEC-FALLBACK]): the row contract, the inventory, the no-mover refactor

**DESIGN NOTE, PROPOSED, panel-addressed, REVISION 2, nothing built.**
Revision 1: lane `decfbdes`, 2026-10-08, main `31a9ae4c` (abi 68). Revision 2:
lane `decfbrev2`, 2026-10-08, main `42ab7c25`. `src/` is identical between the
two pins, so every rev-1 `file:line` citation still holds. Nothing under
`src/`, `cli/`, `lib/` or `tests/` changes in either lane. The instruments
and their committed output are in `dec_fallback/` (own CLAUDE.md). Rulings
are Frank's; §11 lists the questions still open, each with a recommendation.

The shape copies refactor A (`start_table.md` rev 2.1): the edit set and its
instruments, the no-mover gates, a commit plan with derived sabotage re-aims,
and the lessons of A's build (`../dev/lanes/stc5_report.md`, `stc5b_report.md`,
`stc67_report.md` §4).

**The contract, as ruled.**
- Today's tokens are kept; B is a pure no-mover (D151 addendum 2, item 1).
- B comes after A. Its STEP 0 census ran after C7 (lane decfb0).
- B absorbs `start_table.md` Q8, the prefilter admission ternary.
- The movers are later, separate rows, never folded in. Revision 2 moves one
  more out: the §4.1 waste fix is the new row [DEC-COLLAPSE-WASTE] (§5.1).

**Read before writing.**
- `decision_families_survey.md` §3.1, §4.1, §4.5, §4.6.
- `../dev/lanes/decfb0_report.md` and `decision_families/decfb0/results.md`
  (the STEP 0 census).
- `../dev/reviews/2026-10-08-r-decfallback-panel.md` (the panel this
  revision answers) and `dec_fallback/reach/out/` (its measured evidence).
- `../dev/lanes/nullanch1_report.md` §1 (the `empty_admits` fact, F1).
- `sel_cost.md` §4.
- D151 and its addenda, D152, D153.
- `../spec/limits.md` §8 ("The size-cap ladder").
- The table sites in `src/core/compile.c`, `src/opt/select_engine.c`,
  `src/gen/emit_vm.c`, `src/gen/emit_dfa.c` and `src/dump/axes_dump.c` at
  this pin.

---

## R. Panel disposition (revision 2)

Every finding of the light D6 panel (critB2 checks/instruments, critB1
soundness; `../dev/reviews/2026-10-08-r-decfallback-panel.md`) is ACCEPTED,
and the manager's dispositions there are binding. "Fixed" means the note now
says the corrected thing. "Measured" means the revision's row-reach prototype
(`dec_fallback/reach/`, §4.3a) supplied the count. "Designed" means a B0/B1
deliverable now specified here and not built in this lane.

| finding | resolution | where |
|---|---|---|
| critB2 **B1** (T2 listing has no byte gate where its rows fire: stream 3 is `--engine=vm`) | designed, and a HARD GATE for B4 (manager ruling): a B0 stream `emit-ir-auto` (stdout AND rc, refusals included, every variant, arms `-fno-prefilter`/`-fprefilter`/`-fno-prefilter-collapse`, a floor per listing TOKEN per variant); plus hand-written `check_ir_value` rows in `tests/prefilter/run_prefilter_tests.sh` for EVERY T2 row and scope, 18 rows with their witnesses listed. Measured: the T2 listing cell equals `--emit-ir`'s value on every final VM attempt over 60 variant × arm runs (0 mismatches). Found while building the prototype: `--emit-ir` ignores `--pattern-esc` (F-B5), so the stream must hand decoded bytes | §4.2 B0 items 2 and 6, §4.3 item 2, §4.3a, §10 F-B5 |
| critB2 **M1** (refusals not compared) | designed: the rev-1 `notes` stream becomes stream 7, the FULL stderr and rc of every compile, refusals compared byte for byte (the exhaustion diagnostic and which cap is named included), with a refusal floor per variant | §4.2 B0 item 3 |
| critB2 **M2** (population mismatch) | designed: every floor is re-measured in emit_sweep's OWN population per variant, each with an `-e utf8` base; the attempt histogram runs in its own driver over decfb0's population and is compared PARENT vs CHILD, never as pinned absolute counts; decfb0's tables are pinned only once, for the B1 cross-record. The prototype's counts (decfb0's population) are stated as indicative, not as pins | §4.2 B0 items 4-5, §4.3 item 4 |
| critB2 **M3** (no per-row reach instrument) | designed (B1: `row_reach` from the trace) and PROTOTYPED now (probes in a scratch copy): every T1-T4 row and cell has a witness or an UNREACHED entry with its argument and an alternative witness. A fifth variant `lowthr` gives `capacity-declined` a population; arms `-fno-prefilter` and `--tune=min-size` are added; `make alloc` joins B3's gate | §4.2 B0/B1, §4.3a |
| critB2 **M4** (sabotage: no T3/T4 plants; T2 rows 5-7; `on` mask; `sets` cells; T1 row 2) | fixed: 34 planned rows covering every table, the `on` mask, every `sets` cell (latch, carry, restart, flags_or, dd, CR, SDR) and row 0, each with its witness and expected detector; `run_fallback_table.sh` joins `TEST_SECTIONS` and gets mech arm `fallbacktable` | §4.4 |
| critB2 **M5** (trace needs instrument changes) | designed: `trace_diff.py` gains a per-slot order (`fallback` ORDERED, the rest SET); the `fallback` record carries the POST-ROW state tuple (dd, CR, SDR, flags_or, carry, latch, restart); `--variant` composes with `--trace` per variant against that variant's parent trace | §4.2 B0 item 7, B1 |
| critB2 **M6** (reader census undercounts; hand FIELDS) | fixed, BUILT: `state_readers.sh` now DERIVES its member list from the declarations (`EngineFit`; the driver locals and `cx.` members the recovery point names, `pf.forcing` among them; the Ctx members seeded from them; the four enums' values from their enum blocks), each source fail-closed on an empty extraction. 408 lines at `42ab7c25` (rev 1: 164), in six classes | §2.1, `dec_fallback/state_readers.sh` |
| critB2 **M7** (retiring the registry legs) | fixed per the manager's ruling: both legs (`axes_registry_check.sh:755`, `:782`) retire AT B5, in the commit that deletes `cx.size_term_why =`, with the PASS re-pin, and ONLY behind the new observed-stamp leg in `run_fallback_table.sh` (every one of the 8 `ENGINE_SEL` and 7 `UNROLL_K_WHY` values observed on a witness and held to `match_api.md` §6.3's hand-written sets, K35 floors), which lands at B0 and must be green from B0 | §4.2 B5, §4.5 |
| critB2 m1 (the histogram shares setjmp/rung sites; no trial/other split; no state) | answered: stated as the histogram's limits; the B1 cross-record compares the post-row state tuple, which the histogram cannot see, and the prototype already splits the trial row from `other` (`trial` probe) | §4.3 item 4, §9.2 |
| critB2 m2 (RE-RUN set hand-derived) | designed: B0 gives `call_graph.py` a `--family fallback` root/seed set (the walk, T2-T4, `esel_of`; seeds = the derived members), so `sabotage_anchors.py`'s `rerun_at` is computed per B commit; owner resolution stays a hard error (1 pre-existing unresolved site, S571, outside the family). The 11 re-aims re-derived on `42ab7c25` with the rev-2 edit set: unchanged | §4.2 B0 item 9, §4.4 |
| critB2 m3 (`degrading` vs `fof` contradicts `limits.md` §8 / `run_resource_tests.sh:1338`) | fixed: `degrading` = "costs run time to fit or recover"; `fof` = "inside `--fast-or-fail`'s reach". B2, the commit that adds the [SEL-1] rows to the table, carries a wording hunk to `limits.md` §8 and that comment (no behaviour moves) | §1.2, §4.2 B2, §4.6 |
| critB2 m4 (self-check compares hand vs hand) | fixed: stated; the independent half is a trace-build assertion that observed attempts ≤ the bound (measured: max 9 of 25 over every run) | §1.8, §1.9 |
| critB2 m5 (`has_var` invariants are an argument) | fixed: stated as a corpus argument plus a structural argument, not a proof; now also MEASURED (1,104 `has_var` admissions, 0 with a rung or `dd`) and asserted in the trace build | §1.4, §1.9 |
| critB1 **MAJOR-1** (§4.1's split is incomplete: nullable ∧ ¬empty_admits wastes an attempt) | fixed, and MOVED OUT OF B (manager ruling): the three-way split (pfc_rep; nullable ∧ ¬empty_admits; empty_admits) is measured per variant and filed as [DEC-COLLAPSE-WASTE] with both candidate forms. T2r5 and T3r3 are listed as two derivations of one question | §5.1, §7, `docs/dev/plan.md` |
| critB1 **MAJOR-2** (fix (a) moves `VM_PREFILTER_WHY`'s byte figure) | fixed: recorded on [DEC-COLLAPSE-WASTE] as a stamp-VALUE mover whose D76/D94 status is ruled when it is built. B keeps every attempt and every stamp value | §5.1 |
| critB1 **MAJOR-3** (the `pf.forcing` arm is a fifth arrival) | fixed (manager ruling): a `forcing` LABEL and a T1 row 0 ahead of `nomem`, so the table is total over every arrival; `pf.forcing` is in the derived census; its witness is a designed alloc-injector cell over `pcrec_emit_facts` (no corpus compile reaches it) | §1.1, §1.2, §4.3a, §4.4 |
| critB1 m1 (row 2 fires many times; "at most once" false) | fixed: rows 0 and 2 repeat, rows 1 and 3-9 fire at most once, row 10 ends the compile; the trace build asserts it (measured: no at-most-once row fired twice in any compile) | §1.3, §1.9 |
| critB1 m2 (§1.7's "no size row after a [SEL-1] row" argued wrongly) | fixed by MECHANISM, not by argument: `prefilter-collapse`'s `off` cell becomes PASS and the attribution walk goes BACK through the fired rows to the first non-PASS cell, which reproduces today's token on the m2 sequence too. The sequence stays unpopulated (it needs F-B3's state, 0 in every run) and is listed as legal in §1.9 | §1.2, §1.7, §1.9 |
| critB1 m3 (`fit_fired`/`fit_last` must be volatile; the anchored machine's own fallback) | fixed: the fired record is `volatile` driver state (`fit_seq[]`/`fit_nseq`, plus `fit_fired`); the anchored machine's overflow → search-filter fallback (`compile.c:356-372`) is declared an unhosted sibling | §1.3, §7 |
| manager: Q1, Q2, Q4(b) | RULED by Frank 2026-10-08 (all as recommended) | §11 |
| manager: Q3, Q5, Q6, Q7 | taken as recommended; Q5 reframed by MAJOR-1/2 and moved to [DEC-COLLAPSE-WASTE] | §11 |
| manager: Q8 | done (this panel) | §11 |

---

## 0. Answers first

1. **What B builds.** Four first-match tables, plus one attribution walk that
   READS them. B adds no new decision.
   - **T1 `fit_rungs[]`**, the ONE fallback ladder. It is today's six size-cap
     rows plus five new ones: `forcing` (the `--emit-facts` force loop's
     arrival, rev 2), `nomem` (K60's propagation), `size-term-trial`
     ([ART-SIZE]'s "this K is out"), `sel1-collapse` and `sel1-drop` ([SEL-1]).
     - Rows are keyed by the ARRIVAL LABEL SET (`forcing | nomem | overflow |
       size | other`, §1.1) in an `on` column.
     - Each row carries its state writes as data (`sets`) and its tokens as
       cells.
     - The forcing test, the K60 test, the trial catch, the
       `ovf_eligible`/`retry_collapse`/`retry_drop` block
       (`compile.c:1179-1307`) and the `cx.size_cap_refused ? fit_select :
       refuse` dispatch (`:1316-1319`) become one walk.
   - **T2 `pf_admits[]`**, the prefilter admission: Q8, the 4-clause ternary
     at `select_engine.c:879-886`. It is merged with its SECOND derivation,
     the `--emit-ir` "prefilter" reason chain (`emit_vm.c:9443-9541`). The
     verdict cell is the ternary's answer and the listing cells are the
     chain's tokens. The two orders differ today (§2.2), and the merged order
     reproduces both (MEASURED, §4.3a).
   - **T3 `pflw_rows[]`**, the collapse build gate (`compile.c:1806-1873`)
     with its `VM_PREFILTER_LANG_WHY` reason, written from one row (D81's
     "decision and reason together", as a table).
   - **T4 `st_whys[]`**, the 7-arm `UNROLL_K_WHY` ternary (`compile.c:1977-1984`).
   - **The attribution walk** replaces `esel_of`'s 8-arm ternary
     (`select_engine.c:960-994`). In order:
     1. `forced`;
     2. else the admission row's ESEL cell;
     3. else, walking the FIRED attributing ladder rows from the latest back,
        the first cell that is not PASS, keyed on whether the final prefilter
        survived (rev 2: a backward walk, §1.7);
     4. else `selected`.

     `VM_PREFILTER_WHY` (`emit_vm.c:11264`) and the three drop notes
     (`compile.c:2239-2254`) read the fired rows' cells.
2. **No mover: tokens, attempts and listing are all held.**
   - **Tokens.** Every value of `ENGINE_SEL`, `UNROLL_K_WHY`, `VM_PREFILTER`,
     `VM_PREFILTER_LANG`, `VM_PREFILTER_LANG_WHY` and `VM_PREFILTER_WHY`
     (`match_api.md` §6.3) is unchanged. So are the `--emit-ir` prefilter
     tokens and prose, and every stderr line and exit code.
   - **Attempts.** The attempt COUNT and ORDER are unchanged, including every
     wasted attempt. `COMPILE_MAX_ATTEMPTS` keeps the value 25. The hand
     formula is kept and is now CHECKED against the table (§1.8).
   - **Listing.** `--list-axes` is byte-identical through B6. B7 is the one
     declared listing commit, as C7 was.
   - **Measured ahead of the build.** The rev-2 prototype computes T2, T3 and
     the attribution walk from this note's row lists alone and compares them
     with today's probes, stamps and listing over decfb0's population × 5
     limit variants × 14 flag arms: 0 mismatches (§4.3a). That is a check of
     the TABLES' content, not of B's code, which does not exist yet.
3. **F1 is PRESERVED byte for byte** (Frank's ruling).
   - Nine corpus `^${v…}$` rows stamp `declined-nullable-default` although
     `has_var` is what turns their prefilter off.
   - Today that lives in a `has_var ? nullable : empty_admits` ternary inside
     `lang_nullable_declinable` (`select_engine.c:855-857`). In B it is one
     visible ROW of T2 (`var-nullable`, §1.4), the ternary is gone, and the
     row is the F1 holder.
   - F1's fix is a separate later mover row. B makes it a one-row deletion
     plus one listing cell (§5.2).
4. **The §4.1 fix is NOT in B, and revision 2 files it.** critB1 split the
   wasted collapse attempts three ways, and the manager ruled the fix out of
   B into [DEC-COLLAPSE-WASTE] (§5.1):
   - (i) a rung offered to a pattern with no collapsible repeat (the missing
     `pfc_rep` conjunct, survey §4.1);
   - (ii) a rung offered to a nullable, NOT `empty_admits` pattern, whose
     gate then declines the collapse, so the machine that just failed is
     rebuilt and fails again (critB1 MAJOR-1; live at shipped limits:
     `^(?:(?:a|b)*a(?:a|b){20})?$`, and `-e utf8 ^(\p{Xwd}{1,3})?$`);
   - (iii) the `empty_admits` decline, which is [OPT-4.1]'s DESIGNED outcome
     and not waste.
5. **§4.5 and §4.6 under B** (§6).
   - §4.5 (`--emit-ir` names `-fno-prefilter` for a [PF-DROP] artifact) is
     PRESERVED. In B it is one cell: the `forced-off` admission row's listing
     cell is shared by the caller's bit and [PF-DROP]'s OR'd bit.
   - §4.6 (`engine-route` listed order ≠ evaluated order) is fixed with ZERO
     artifact movers. It does move `--list-axes`, so it is B7's declared
     listing commit: one swap of two listed orders, `kind` `predicate` →
     `list`, and two corrected descs.
6. **New findings** (§10).
   - **F-B1.** The `--emit-ir` chain has no `has_var` arm. A non-nullable
     `${…}` pattern compiled under `auto` lists
     `no-engine-vm  --engine=vm -- …`, a flag the caller never passed
     (PROBED, `a${v}b`). It is §4.5's sibling and is preserved.
   - **F-B2.** The `declined-nullable-default` listing desc ("auto (or forced
     --engine=vm plus -fprefilter)") is FALSE: that invocation stamps
     `forced` and builds a hybrid (PROBED).
   - **F-B3.** `collapsed-prefilter` would be stamped when the [SEL-1]
     collapse retry kept an UNcollapsed prefilter. Population 0 in every one
     of revision 2's 60 runs, and §10 gives the argument for why.
   - **F-B4.** Both failure labels can be set on one arrival only through the
     optional anchored machine, which restores the flag. T1's label-set walk
     reproduces today's precedence either way.
   - **F-B5 (rev 2, probed).** `--pattern-esc` is IGNORED by `--emit-ir` and
     `--emit-facts`: both branches return before the decode at
     `cli/main.c:2359`, so the listing describes the raw escaped text, not
     the pattern the `.c` compile builds. A pre-existing CLI defect outside B;
     every B0 listing stream must hand DECODED bytes.
7. **Siblings** (§7). Hosted in B: the ladder, [SEL-1], the force loop's
   arrival, K60's propagation, the size-term trial catch, the admission (Q8
   and the listing chain), the collapse gate and PFLW, `UNROLL_K_WHY`,
   `ENGINE_SEL`, `VM_PREFILTER_WHY`, and the notes. Declared NOT hosted, with
   reasons:
   - the auto engine choice ([SEL-COST]'s `sel_auto_rows[]`, D124);
   - `forces_dfa_overflow`;
   - the do-or-die request refusals ([OPT-SETS]' constraint table);
   - `size_term_choose`'s argmin (an optimizer inside one row);
   - the `--tune` flag ORs;
   - the anchored machine's own overflow fallback (rev 2);
   - the start table.
8. **[SEL-COST] §4 and `--fast-or-fail`** (§8).
   - [SEL-COST]'s post-build rows land as a sixth arrival label (`cost`) with
     their own T1 rows.
   - `--fast-or-fail`'s reach becomes a visible per-row column, `fof`. It is
     true on the five size rows and false on the [SEL-1] rows, today's scope
     exactly.

---

## 1. The row contract

### 1.1 The arrival label set

An arrival is one `longjmp` to `compile_driver`'s recovery point
(`compile.c:1167`'s catch branch). Today it carries three flags plus one
phase flag, read in a fixed order (`:1179`, `:1203`, `:1229`, `:1277`,
`:1316`). B names them once:

| label | set by | meaning |
|---|---|---|
| `forcing` | `pcrec_facts_force_all` (`src/facts/facts.c:430`, cleared `:442`), read as `cx.job->pf.forcing` | the failure happened inside `--emit-facts`' force loop, AFTER the attempt's artifact and stamps were complete (rev 2, critB1 MAJOR-3) |
| `nomem` | `pcrec_ctx_nomem` (`compile.c:52`) | a genuine allocation failure (K60) |
| `overflow` | `src/ir/dfa.c:203,1248,1315,1330` | a DFA state, context or work cap declined a machine |
| `size` | `compile.c:2157` | an emitted-size cap refused the artifact |
| `other` | every other `pcrec_ctx_fail` | a refusal no rung can rescue |

`labels = (forcing ? FORCING : 0) | (nomem ? NOMEM : 0) | (dfa_overflowed ?
OVERFLOW : 0) | (size_cap_refused ? SIZE : 0)`, and `OTHER` when none is set.
- **`forcing` co-occurs with the others.** An allocation failure inside the
  force loop sets both `forcing` and `nomem`. Today the forcing test comes
  first and ABSORBS it (the listing never refuses a compile that succeeded,
  `patfacts/design.md` §11.4). Row 0 precedes row 1 for that reason; a
  `nomem` row at the top would propagate where today the arm absorbs, a
  stream-7 and CLI mover.
- **Both `overflow` and `size` can only be set together through an optional
  machine.** The one optional machine, the anchored match-here DFA, saves and
  restores `dfa_overflowed` (`compile.c:356-370`), so no shipped arrival
  carries both.
- The walk is defined on the SET anyway, so its precedence is today's code
  order whatever the set (F-B4, §10).
- The `overflow` label carries one ATTRIBUTE, `dfa_overflow_is_budget` (the
  [LIM-2] N1 budget note). It is an attribute and not a row: the note prints
  for either [SEL-1] row (§1.3).

### 1.2 T1 `fit_rungs[]`: the columns

Today's columns stay: `name`, `deny`, `degrading`, `applies`, `act`. B adds:

| column | type | meaning | no silent default |
|---|---|---|---|
| `on` | label mask | the arrival labels the row is asked on | every row states it |
| `fof` | bool | the row is inside `--fast-or-fail`'s reach: the switch denies it when `degrading` | stated on every row; `false` on the [SEL-1] rows is today's scope, not a default |
| `sets` | struct | the cross-attempt state the row writes: `dfa_disabled` (SET/KEEP), `collapse_reason` (a `CR_*` value/KEEP), `size_drop_rung` (an `SDR_*` value/KEEP), `flags_or` (bits), `restart_term`, `carry` (`overflow_why`, `size_cap_*`), `latch` (`dfa_was_engine`/`budget_fallback`, first overflow only) | KEEP is a named token, never 0-means-keep |
| `esel` | pair `{kept, off}` | the `ENGINE_SEL` this row attributes when the FINAL prefilter survived (`kept`) or did not (`off`); `ESEL_PASS` = this row attributes nothing in that case, and the walk goes on BACK to the previous fired row (§1.7) | `ESEL_PASS` is named |
| `pflw` | `PFLW_*` / `PFLW_PASS` | the `VM_PREFILTER_LANG_WHY` value this row makes when the collapse it set builds | named |
| `pfwhy` | format / NONE | `VM_PREFILTER_WHY`'s text | named |
| `ukw` | token / PASS | `UNROLL_K_WHY` contribution (only `unroll-rescue` → `cap-rescue`) | named |
| `note` | `{what, cost}` / NONE | the stderr drop note | named |
| `retries` | 0/1 | attempts this row adds when it fires (feeds §1.8) | stated |
| `repeat` | `once` / `many` / `final` | how often the row may fire in one compile: `once` (rows 1, 3-9), `many` (rows 0 and 2), `final` (row 10, the compile ends) | stated; asserted in the trace build (§1.9) |

**`degrading` and `fof` are two questions** (critB2 m3). `degrading` = "this
row costs run time to make the artifact fit or recover". `fof` = "this row is
inside `--fast-or-fail`'s reach", and the switch denies a row only when both
hold. Rows 3-4 are degrading (a [SEL-1] retry ships a VM with a collapsed or
no prefilter) and outside the reach, which is today's scope (`cli.md:414`
calls the switch "a size POLICY"). `limits.md` §8 ("denies every row the
table marks degrading — today all five") and the comment at
`run_resource_tests.sh:1338` were written when the table held only size rows.
B2, the commit that adds rows 3-4, corrects both to "every size-cap row the
table marks degrading" (a wording hunk, no behaviour, §4.6).

**Rows, in walk order:**

| # | row | on | applies (verbatim from today) | deny | degr. | fof | sets | esel {kept, off} | pflw | note | repeat |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | `forcing` | forcing | always (`:1179`) | — | no | no | FORCE_NEXT (record the forced fact `absent`/`decline:force-failed`, clear `err`, resume the force loop at the next fact, `:1180-1182`) | PASS | PASS | — | many (≤ `PF_NFACTS`) |
| 1 | `nomem` | nomem | always (`:1203`) | — | no | no | PROPAGATE (refuse, keep the diagnostic) | PASS | PASS | — | once |
| 2 | `size-term-trial` | overflow, size, other | `st_phase == ST_LADDER` (`:1229`) | — | no | no | TERM_NEXT (`:1230-1247`) | PASS | PASS | — | many (≤ N per run, ≤ 3 runs) |
| 3 | `sel1-collapse` | overflow | `engine == AUTO && !FORCE_PREFILTER && !dfa_disabled` (`:1277-1282`) | `NO_PREFILTER_COLLAPSE` | yes | **no** | dd=SET, CR_SEL1, carry `overflow_why`, latch | {`collapsed-prefilter`, ROLE} | `PFLW_SEL1` | — | once |
| 4 | `sel1-drop` | overflow | `engine == AUTO && !FORCE_PREFILTER && (!dfa_disabled ∥ CR == CR_SEL1)` (`:1283-1284`) | — | yes | **no** | dd=SET, CR_NONE, carry, latch | {ROLE, ROLE} | PASS | — | once |
| 5 | `unroll-rescue` | size | NULL (chosen inside `size_term_choose`) | — | yes | yes | — | PASS | PASS | — | once |
| 6 | `prefilter-collapse` | size | `fit_collapse_applies` (`:683`) | `NO_PREFILTER_COLLAPSE` | yes | yes | CR_SIZECAP, carry `size_cap_*`, restart | {`size-cap-retry`, **PASS**} | `PFLW_SIZECAP` | — | once |
| 7 | `drop-anchored` | size | `fit_anchored_applies` | — | yes | yes | SDR_NO_ANCHORED | {`size-cap-retry`, `size-cap-retry`} | PASS | anchored | once |
| 8 | `drop-premul` | size | `fit_premul_applies` | — | yes | yes | SDR_NO_PREMUL, `flags_or` NO_PREMUL_TABLE | same | PASS | premul | once |
| 9 | `drop-prefilter` | size | `fit_prefilter_applies` | — | yes | yes | SDR_NO_PREFILTER, `flags_or` NO_PREFILTER, carry, restart | same | PASS | prefilter (+ `pfwhy`) | once |
| 10 | `refuse` | every label | always | — | no | no | REFUSE | PASS | PASS | — | final |

ROLE is ONE cell with two spellings, keyed on the latched `dfa_was_engine`:
`overflowed-dfa` when the DFA was to be the engine, `overflowed-prefilter`
otherwise. This is `esel_of` arms 8/9 as data.

**Why each cell is today's behaviour.**
- **Row 0.** Today's first test (`:1179`), ahead of K60's. The forced ask
  runs after every stamp is written, so the row writes no ladder state and
  attributes nothing.
- **Rows 3-4.** The block offers collapse when it is eligible, and drop
  otherwise or after a failed collapse. `retry_collapse ? CR_SEL1 : CR_NONE`
  (`:1299`) makes row 3 win where both apply. Denying row 3
  (`-fno-prefilter-collapse`) makes it transparent and row 4 fires on the
  first overflow, which is `retry_drop`'s `!dfa_disabled` disjunct.
- **Row 4's `kept` cell is ROLE.** A surviving prefilter after `sel1-drop` is
  impossible: CR_NONE plus `dfa_disabled` drops it (`select_engine.c:880`).
  So the cell's spelling is unobservable, and the trace build asserts the
  impossibility (§1.9; measured: 1,303 compiles end on `sel1-drop`, 0 with a
  prefilter).
- **Row 6's `off` cell is PASS (rev 2).** Rev 1 wrote `selected`, which is
  today's arm 6 when no other ladder row fired. It is wrong when a [SEL-1]
  row fired first (critB1 m2): today stamps ROLE there. PASS sends the walk
  back to the earlier row, which gives `selected` when there is none and ROLE
  when it was `sel1-collapse` (§1.7).
- **Rows 7-9 stamp `size-cap-retry` whatever the prefilter.** That is arm 5,
  which has no `fit->prefilter` conjunct (note D).

### 1.3 The walk and the state

`fit_walk(sel, labels)` walks T1 in order. A row is asked only when `on &
labels`. It is skipped when `applies` is NULL, when its `deny & flags` is set,
or when `degrading && fof && (flags & PCREC_FAST_OR_FAIL)`. The first row
whose `applies` holds fires. Row 10 applies to every label, so the walk is
total over every arrival (row 0 included: critB1 MAJOR-3).

The `sets` cell is applied by ONE generic action routine. Today's switch at
`:1321-1474` keeps only the cases whose action is code: FORCE_NEXT,
PROPAGATE, TERM_NEXT, REFUSE. The rest are data.

**The cross-attempt state is UNCHANGED in name and meaning**: `dfa_disabled`,
`collapse_reason`, `size_drop_rung`, `dfa_was_engine`, `budget_fallback`,
`size_cap_*`, `overflow_why`, `st_*`. What changes is WHO writes it: only the
row's `sets` cell does. It is still read where it is read today: every
`applies` predicate, `select_engine.c`'s admission (T2), `build_anchored_dfa`
(`:354`) and `forces_dfa_overflow` (`select_engine.c:392`).

**The fired record** (critB1 m1/m3):
- **`fit_seq[]` / `fit_nseq`**, the ORDERED list of fired ATTRIBUTING rows
  (rows 3, 4, 6-9; each fires at most once, so six entries suffice). The
  attribution walk reads it backwards (§1.7). An order is needed, not a
  bitmask: table order is not firing order once a size row can precede a
  [SEL-1] row (§1.7's sequence list).
- **`fit_fired`**, a bitmask of every `once` row fired. The notes read it in
  table order, which is today's `dropped_*` order; the three `dropped_*`
  booleans retire. The trace build asserts no `once` bit is set twice.
- All three are `volatile` driver locals beside `dfa_disabled`
  (`compile.c:897-927`), for the same `-Wclobbered` reason: they are written
  between `setjmp` and `longjmp`.

None of them is an artifact byte. The walk reads them through the attempt's
`Ctx` as `collapse_reason` is read today (`:1062`).

**Why the state survives.** Replacing `CR_*`/`SDR_*` by row pointers would
re-aim every row and check that names them (§4.4). It would also break A's
rule that a reader reads a row's PAYLOAD, never its identity
(`dfa_search_is_pinned`, start_table.md [r2 sound-m2]). The state values ARE
the payload: a row writes `CR_SEL1`, and readers test `CR_SEL1` (§11 Q6,
taken).

### 1.4 T2 `pf_admits[]`: the prefilter admission (Q8)

**Two derivations today.**
- The VERDICT is `select_engine.c:879-886`: the first clause (`has_bref ∥
  has_call ∥ has_var ∥ (dd && CR ≠ SEL1) ∥ dn ∥ dnd`) → off, then
  `force_on` → on, then `force_off` → off, then `would_prefilter`.
- The LISTING's reason is `emit_vm.c:9443-9541`: verdict on → `yes` /
  `yes-collapsed`; then `has_bref`, `has_call`, `dn`, `dnd`, `dd`, the
  `NO_PREFILTER` flag, else `no-engine-vm`.
- They test the same facts in DIFFERENT orders, and the listing chain has no
  `has_var` arm.

**The merged table.** Every row's verdict equals the ternary's and every row's
listing token equals the chain's, on every input (argued per row below;
MEASURED by the prototype, §4.3a; checked by B2's oracle and by the B0
`emit-ir-auto` stream and `check_ir_value` rows from then on):

| # | row | predicate | verdict | listing value (DD-8 token) | ESEL cell (scope) | scopes reached |
|---|---|---|---|---|---|---|
| 1 | `backref` | `has_bref` | off | `no-backreference` | — | NONE |
| 2 | `linked-call` | `has_call` | off | `no-linked-call` | — | NONE |
| 3 | `var-nullable` **[F1 holder]** | `CR == NONE && !dd && would_prefilter && has_var && nullable && !force_on` | off | `no-nullable-exact` | `declined-nullable-default` | NONE |
| 4 | `nullable-exact` | `CR == NONE && !dd && would_prefilter && empty_admits && !force_on` | off | `no-nullable-exact` | `declined-nullable-default` | NONE |
| 5 | `nullable-collapsed` | `CR ≠ NONE && empty_admits && collapsible_rep && !force_on` | off | `no-nullable-collapsed` | `declined-nullable` | SEL1 (SIZECAP UNREACHED, §4.3a) |
| 6 | `overflow-drop` | `dd && (CR ≠ SEL1 ∥ force_off)` | off | `no-dfa-overflow` (+ `overflow_why`) | — | NONE, SEL1 (SIZECAP UNREACHED) |
| 7 | `forced-on` | `force_on` | on | `yes` / `yes-collapsed` | — | NONE, SIZECAP |
| 8 | `forced-off` | `force_off` | off | `no-fno-prefilter` (§4.5, preserved) | — | NONE, SIZECAP |
| 9 | `var` | `has_var` | off | `no-engine-vm` (F-B1, preserved) | — | NONE |
| 10 | `default` | always | `would_prefilter` | `yes` / `yes-collapsed` if on, else `no-engine-vm` | — | on: NONE, SEL1, SIZECAP; off: NONE |

**Why it equals both derivations.**
- **Rows 1-2.** `lang_nullable_declinable` carries `!has_bref && !has_call`,
  so rows 3-5 exclude them, and their order against 3-5 is free.
- **Rows 3-5 are today's two flags** `prefilter_declined_nullable_default`
  (`:876-878`) and `prefilter_declined_nullable` (`:873-875`). Two facts make
  the `has_var` ternary unnecessary:
  - (a) `empty_admits ⇒ nullable` (the E1 seal asserts it, nullanch1 §1), so
    rows 3 then 4 compute exactly `(has_var ? nullable : empty_admits)`;
  - (b) the rung scope (row 5) has no `has_var` population. `has_var` makes
    `fit.prefilter` false, so no prefilter machine is built and neither
    collapse rung is ever offered.

  (b) is a structural argument plus a corpus count, not a proof (critB2 m5).
  Revision 2 measured it: 1,104 `has_var` admissions over the 60 prototype
  runs, 0 with a rung or `dd` set. The trace build asserts `has_var ⇒ CR ==
  NONE && !dd` (§1.9).

  Rows 3-4 and row 5 are disjoint on `CR`, so their order is free. The order
  chosen (default before rung) is the one that minimises B7's listing move
  (§6.2).
- **Row 6** is the verdict's `(dd && CR ≠ SEL1)` clause. It also catches
  `dd && CR == SEL1 && force_off`: the ternary answers that off through
  `force_off`, while the listing answers `no-dfa-overflow` because the chain
  tests `dd` before the flag. One row gives both. Its SEL1 scope is reached
  at shipped limits (`-fno-prefilter ^(?:(?:a|b)*a(?:a|b){20})?$`: a
  `-fno-prefilter` compile still takes the [SEL-1] retry).
  - `dd && force_on` cannot arise: no retry is offered under `-fprefilter`.
  - `dd && CR == SEL1 && !would_prefilter` cannot arise: a retry is
    auto-only, and `dd` forces the VM.
- **Row 8 before row 9.** The listing chain has no `has_var` arm, so a
  `has_var` pattern lists the flag when `-fno-prefilter` is passed, else
  `no-engine-vm`. `force_on && has_var` is refused before the table
  (`select_engine.c:696`; §11 Q7, taken: the refusal stays outside T2).

**T2 row 5 and T3 row 3 answer one question twice** (critB1 MAJOR-1): "is
the collapsed rescue worth building for a nullable language?". T2 row 5 reads
`empty_admits` and declines the PREFILTER; T3 row 3 reads bare `nullable` and
declines the COLLAPSE. Where they disagree (nullable ∧ ¬empty_admits) the
rung is offered, T2 keeps the prefilter, T3 declines the collapse, and the
exact machine that just failed is rebuilt. B preserves both derivations (a
no-mover); unifying them is [DEC-COLLAPSE-WASTE]'s question (§5.1, §7).

### 1.5 T3 `pflw_rows[]`: the collapse gate and its reason

Today (`compile.c:1806-1870`):
- `pfc_wanted = chosen ≠ DFA && !deny && pfc_rep && (force ∥ rung)`;
- `collapse = pfc_wanted && (force_prefilter ∥ !nullable)`;
- the 6-way PFLW ternary.

As rows, each writing `collapse` and `prefilter_lang_why` together (D81):

| # | row | predicate | collapse | PFLW | reached (prototype) |
|---|---|---|---|---|---|
| 1 | `rung` | `wanted && (fpf ∥ !nullable) && CR ≠ NONE` | yes | the T1 row that set CR: its `pflw` cell (`SIZECAP` row 6, `SEL1` row 3) | SIZECAP: lowsize/lowboth base, plain under `-fprefilter`; SEL1: plain base |
| 2 | `forced` | `wanted && (fpf ∥ !nullable)` | yes | `PFLW_FORCED` | `-fprefilter-collapse` arm |
| 3 | `nullable` | `wanted` | no | `PFLW_NULLABLE` | plain base (the [DEC-COLLAPSE-WASTE] (ii) population), `-fprefilter-collapse` arm |
| 4 | `exact` | `pfc_rep` | no | `PFLW_EXACT` | plain base |
| 5 | `no-rep` | always | no | `PFLW_NO_REP` | plain base |

The T1 row that set CR is found by a projection, `fit_row_setting_cr(CR)`: the
unique row whose `sets.collapse_reason` equals CR. This is A's
`fit_rung_of(act)` shape and a payload read, not identity. The self-check
asserts uniqueness. The `PFLW_*` enum values and their order are unchanged, so
`>= PFLW_FORCED` iff collapsed still holds (`internal.h:2390`).

### 1.6 T4 `st_whys[]`: `UNROLL_K_WHY`

Seven rows in today's ternary order (`compile.c:1977-1984`): `option`,
`denied`, `default`, `cap-rescue`, `size-model`, `capacity-declined`,
`size-model-declined`. `cap-rescue` is `unroll-rescue`'s `ukw` cell projected;
its predicate is `st_rescue`, set inside `size_term_choose`. Row 5 of T1 has
no arrival of its own, so its reach IS `cap-rescue`'s (§4.3a).
- The `size-term` listing already prints these in this order
  (`axes_dump.c:543-565`), so §4.7's precedence becomes stated rather than
  implicit.
- The precedence sentence for `tuning.md` §2.16 rides B7 (§4.2).

### 1.7 The attribution walk (`ENGINE_SEL`)

`esel_of` stays one function, at its one call site (`select_engine.c:1125`),
with its premise check kept (`:976`). Its body becomes:

```
if (engine != AUTO)                 return ESEL_FORCED;
if (admit_row->esel != ESEL_PASS)   return admit_row->esel;      /* T2 rows 3-5 */
for (i = fit_nseq; i-- > 0; ) {                                  /* latest fired first */
    c = fit_seq[i]->esel[fit->prefilter ? KEPT : OFF];
    if (c == ESEL_PASS) continue;
    return c == ESEL_ROLE ? (dfa_was_engine ? ESEL_OVERFLOWED_DFA
                                            : ESEL_OVERFLOWED_PREFILTER) : c;
}
return ESEL_SELECTED;
```

The backward walk is the revision's answer to critB1 m2. It is a general
rule ("the latest fired row that has something to say about this outcome")
and not a special case for one sequence.

**Equivalence to the 9-arm table (`select_engine.c:909-919`), arm by arm.**
- **Arm 1** is line 1.
- **Arms 2-3** are the admission cells. They precede every ladder cell, as
  arms 2-3 precede arms 4-9. This matters on a rung compile where `dn`
  holds: arm 3 must beat the rung's cell, and it does.
- **Arm 4** (`CR_SIZECAP && prefilter`) is row 6's `kept` cell. Row 6 is the
  latest attributing row whenever CR is SIZECAP, because a drop row after it
  sets SDR (arm 5) and no [SEL-1] row can follow it (a [SEL-1] row sets CR to
  SEL1 or NONE).
- **Arm 5** (`SDR ≠ NONE`) is rows 7-9's cells.
- **Arm 6 (`!dd → selected`)** has two routes:
  - no attributing row fired: the fallback;
  - only row 6 fired and the prefilter did not survive: its `off` cell is
    PASS, the walk runs out, `selected`.
- **Arms 7-9** are rows 3-4's cells, reached directly or THROUGH row 6's
  PASS.

**The sequences the loop can take, and what the walk gives.** Row order is
not firing order; at most one firing per `once` row:

| sequence (firing order) | today's arm | the walk | populated (prototype, 60 runs) |
|---|---|---|---|
| `sel1-collapse` (then optionally `sel1-drop`) | 7, or 8/9 | row 3 or row 4's cell | yes |
| `sel1-drop` alone (`-fno-prefilter-collapse`) | 8/9 | row 4's ROLE | yes |
| `prefilter-collapse` (then optionally `drop-prefilter`) | 4, 5 or 6 | row 6 kept, row 9, or PASS → `selected` | yes |
| `drop-anchored` (then optionally `drop-premul`), `drop-premul` alone | 5 | row 7/8 | yes |
| `prefilter-collapse` → `sel1-collapse` (→ `sel1-drop`): the collapsed prefilter overflows a DFA cap | 7 or 8/9 | row 3 or 4 (latest) | no (§4.3a) |
| `sel1-collapse` → `prefilter-collapse` (critB1 m2): an F-B3 state, then the size cap | 4 if the prefilter survived, else 8/9 | row 6 kept; else PASS → row 3's ROLE | no: it needs F-B3's state (§10) |

In every row the walk's cell is what arms 4-9 compute from (CR, SDR, dd,
`dfa_was_engine`). `dfa_was_engine` is latched at the FIRST overflow by the
`latch` cell, as today.

**What a drop row and a [SEL-1] row cannot share** is still asserted by
`esel_of`'s premise check (`:976`, "a drop-ladder rung and a DFA overflow
fired on the same compile"), which stays. It is no longer the argument for
the walk's correctness, only a guard on SDR rows; the m2 sequence involves no
drop row and is covered by the walk itself. The trace build adds the legal
sequence list above as an invariant (§1.9).

**Measured.** The prototype computes this walk from the probed fired rows and
the final prefilter and compares it with the stamped `ENGINE_SEL` on every
compile of decfb0's population × 5 variants × 14 arms: 0 mismatches
(§4.3a). B2's both-derivations oracle then holds B's code to the old ternary
on the same population.

### 1.8 `COMPILE_MAX_ATTEMPTS`

Today it is the hand formula `3 + 3·(N+1) + 1 + SDR_MAX` = 25 (N = 5,
`compile.c:479`), commented rung by rung. The table bound is:

`1 + Σ retries(r) + (1 + Σ restart(r)) · (N + 1)` = 1 + 6 + 3·6 = 25.

The terms: six retrying rows (3, 4, 6, 7, 8, 9); two restarting rows (6, 9);
`size-term-trial`'s attempts are the `(N+1)` term per run. Row 0 adds no
attempt (the force loop resumes inside the finished attempt).
- B keeps the enum's value, its text and the exhaustion diagnostic
  (`:2303-2307`) byte for byte.
- It adds a self-check that the formula EQUALS the table bound. A new row
  then fails the check rather than silently truncating the search, the
  failure mode `:2294-2301` records.
- That check compares two hand-written things (critB2 m4). The independent
  half is the trace build's assertion that the OBSERVED attempt count of
  every compile is ≤ the bound, and the prototype's measurement of it: the
  most attempts any compile took over every variant and arm is 9 (critB1
  computed the worst reachable at 21).
- Turning the table into an X-macro `.def` so C could derive the constant is
  possible. It is not proposed: no measured need (D77).

### 1.9 The self-check and the trace-build invariants

`fit_tables_selfcheck()` (a unit check, run once per process in the trace
build) asserts, by REFUSING (never `abort`, the `esel_of:976` rule):
- each label has a total walk (row 10 applies to every label);
- every cell an action READS is stated (`ESEL_PASS`, `PFLW_PASS`,
  `SETS_KEEP` and NONE are named tokens, memory `pcrec-no-silent-defaults`);
- every row with `degrading` true has its `fof` stated;
- `COMPILE_MAX_ATTEMPTS ==` the §1.8 bound;
- each `CR_*` value other than NONE is written by exactly one T1 row (T3's
  projection);
- T2's last row always applies.

At their read sites, in the trace build only (the default build gains no
code), each with its prototype measurement:

| invariant | measured over the 60 prototype runs |
|---|---|
| `has_var ⇒ CR == NONE && !dd` (§1.4(b)) | 1,104 admissions, 0 violations |
| a compile ending on `sel1-drop` has no surviving prefilter (§1.2) | 1,303 compiles, 0 |
| no `once` row fires twice in one compile (critB1 m1) | 0 |
| observed attempts ≤ the §1.8 bound (critB2 m4) | max 9 of 25 |
| the fired sequence is one of §1.7's legal sequences (critB1 m2) | 1,902 compiles with a [SEL-1] row, 0 with a size row before or after it |

---

## 2. The inventory, and how it was derived

### 2.1 The reader census (K35), now derived

The member list is not hand-kept. `dec_fallback/state_readers.sh` (revision
2, critB2 M6) DERIVES it, so a new member cannot be forgotten by a list:
- **E**: every member of `EngineFit` (`internal.h`), matched qualified
  (`.m`/`->m`), because `prefilter`, `chosen` and `why` are common words;
- **L**: every `compile_driver` local declared above the attempt loop,
  not `const`, that the recovery point names (the cross-attempt state:
  `dfa_disabled` … `st_*`, `overflow_why`, `defo` whose flags the drop rows
  OR into), matched bare in `compile.c` only;
- **R**: every `cx.` member the recovery point reads or writes, and every
  `cx.job->A.B` pair there (`pf.forcing`, `fit.chosen`);
- **S**: every Ctx member seeded from an L local at the attempt head;
- **V**: every value of the four enums the state carries, read from the enum
  block that declares `CR_SEL1`, `SDR_NO_PREMUL`, `PFLW_SEL1` and
  `ESEL_SELECTED` (a prefix grep would also catch the start table's
  `CR_VM`/`CR_DFA`, a different enum);
- **D**: the function names (`esel_of`, the `fit_*` rows, …), the one
  declared list, each existence-checked.

Every source fails the script (exit 2) on an empty extraction. One trap found
while building it is recorded in the script: `printf … | grep -q` under
`pipefail` silently drops names (grep's early exit SIGPIPEs the printf).

Its output is `dec_fallback/state_readers.txt`: 408 lines at `42ab7c25`
(compile.c 251, select_engine.c 43, emit_vm.c 37, emit_dfa.c 29, internal.h
23, ir/dfa.c 9, facts.c 7, syntax_dump.c 4, facts_dump.c 4, parse.c 1).
Rev 1's hand list found 164. Each line is one of six classes:
1. a member below (§2.2);
2. a declaration in `internal.h`;
3. a WRITER of a label: `ir/dfa.c` (overflow), `compile.c:52` (nomem),
   `:2157` (size), `facts.c:430,442` (forcing). B does not change them;
4. a reader of the FINISHED fit or state that B keeps on purpose:
   `build_anchored_dfa:354`, `forces_dfa_overflow:392`, the `applies`
   bodies, the emitters' route and stamp reads (`emit_dfa.c`
   `fit.chosen`/`fit.prefilter`, `emit_vm.c:3639`, `:9368-9371`, `:11147-11361`,
   `:12775`, `:13942-14008`), `pcrec_engine_sel_name`;
5. the same member SPELLING on another struct (`r->engines` in the registry
   rows, `pf->why` in the facts record): not the family, identified by its
   receiver;
6. the driver's own plumbing of the state (seeding at the attempt head, the
   `memcpy`s).

A build lane re-runs the script on its own base. A line outside these six
classes is an undispositioned member and stops the lane.

### 2.2 The members

| site (main `42ab7c25`) | what it decides today | in B |
|---|---|---|
| `compile.c:632-680` `FitSel`/`FitAct`/`FitRung` | the size-cap row type | gains `on`/`fof`/`sets`/`repeat`/token columns (B2) |
| `compile.c:683-721` the four `fit_*_applies` + `fit_always` | the rows' predicates | UNCHANGED bodies (S237/S252/S420 anchor here; §4.4) |
| `compile.c:723-730` `fit_rungs[]` | the size-cap ladder | T1; five rows added (B2) |
| `compile.c:735-758` `fit_rung_denied`/`fit_rung_of`/`fit_select` | deny + walk | the walk takes the label set; `fof` joins the deny (B2) |
| `compile.c:1179-1182` the force-loop arm | absorb a forced ask's failure | T1 row 0 (B3) |
| `compile.c:1199-1207` the K60 propagation | nomem first | T1 row 1 (B3) |
| `compile.c:1229-1248` the size-term trial catch | "this K is out" | T1 row 2 (B3) |
| `compile.c:1277-1307` [SEL-1] `ovf_eligible`/`retry_collapse`/`retry_drop` | the overflow ladder | T1 rows 3-4 (B3) |
| `compile.c:1308-1487` the size-cap dispatch + switch | rung actions | the walk + the `sets` routine (B3) |
| `compile.c:897-916` the `dropped_*` flags | which drops fired | `fit_fired`/`fit_seq[]` (B3) |
| `compile.c:2227-2254` budget note + drop notes | stderr | label attribute + the rows' `note` cells (B3) |
| `compile.c:479` `COMPILE_MAX_ATTEMPTS` | the attempt bound | value kept, checked (§1.8, B2) |
| `compile.c:1806-1870` the collapse gate + PFLW ternary | language + reason | T3 (B5) |
| `compile.c:1977-1984` `size_term_why` | `UNROLL_K_WHY` | T4 (B5) |
| `select_engine.c:855-886` `lang_nullable_declinable` + the two flags + the ternary | the prefilter admission | T2 (B4) |
| `emit_vm.c:9443-9541` the `--emit-ir` prefilter chain | the listing's reason | T2's listing cells (B4) |
| `select_engine.c:960-994` `esel_of` | `ENGINE_SEL` | the attribution walk (B5) |
| `emit_vm.c:11264-11267` `VM_PREFILTER_WHY` | its own `SDR` test | the fired row's `pfwhy` (B5) |
| `emit_vm.c:11314-11361` the PFLW stamp switch | format | UNCHANGED (it formats; it decides nothing) |
| `emit_dfa.c:447-462` `pcrec_engine_sel_name` | the one spelling | UNCHANGED |
| `axes_dump.c:542-565`, `:604-612`, `:950-997` | the three listings | projections (B6), declared move (B7) |

### 2.3 What B does NOT change, stated so a diff can be held to it

- No predicate body changes (the four `applies`, the admission's facts, the
  gate's conjuncts).
- No `CR_*`, `SDR_*`, `ESEL_*` or `PFLW_*` value is renumbered.
- No `Ctx`/`EngineFit` field is renamed: `prefilter_declined_nullable`,
  `prefilter_declined_nullable_default`, `prefilter_lang_why` and
  `size_term_why` are now written from rows. `tuning.md:1463` cites
  `prefilter_lang_why`, so no spec hunk is needed for it.
- No deny bit is added, moved or reassigned.
- The force loop (`pcrec_facts_force_all`) is unchanged; only its arrival
  becomes a row.

---

## 3. What B preserves on purpose (each a later, separate row)

| item | today | where it lives in B | the later row |
|---|---|---|---|
| F1 | `^${v…}$` stamps `declined-nullable-default` (9 corpus rows) | T2 row 3 `var-nullable` | §5.2 |
| F-B1 | `a${v}b` lists `no-engine-vm` "--engine=vm" | T2 row 9's listing cell | §5.2 (same row as F1) |
| §4.5 | a [PF-DROP] artifact lists `no-fno-prefilter` | T2 row 8's listing cell, reached by the OR'd bit | §6.1 |
| §4.1 + critB1 MAJOR-1 | collapse rungs offered where they cannot help (no repeat; nullable ∧ ¬empty_admits) | T1 rows 3 and 6, column `requires` = `FIT_REQ_NONE` | [DEC-COLLAPSE-WASTE] (§5.1) |
| T2r5 vs T3r3 | two derivations of "is a nullable collapsed rescue worth it" | T2 row 5 and T3 row 3, both kept | [DEC-COLLAPSE-WASTE] (§5.1) |
| F-B2 | `declined-nullable-default`'s false desc | the listing's desc, moved verbatim at B6 | B7 corrects it (a listing change, not an artifact one) |
| F-B3 | `collapsed-prefilter` without a collapse (pop 0) | T1 row 3's `kept` cell | closes structurally with [DEC-COLLAPSE-WASTE] form (a) |
| §4.6 | listed order ≠ evaluated | the listing's `list` column, today's order verbatim at B6 | B7 |
| D-3-like | `size-cap-retry`'s desc names only the [OPT-4] rung | the listing's desc | B7 |
| token/why separation | one token carries both | `esel` and `pfwhy`/`pflw` are already separate columns | the abi row D151 addendum 2 names |
| F-B5 | `--pattern-esc` ignored by `--emit-ir`/`--emit-facts` | outside B (a CLI defect); B0's streams decode | a K-entry, recommended in the lane report |

---

## 4. The no-mover refactor plan

### 4.1 Principles (A's, restated for B)

- **Implement, then replace.**
  - T1 is EXTENDED in place, keeping its name: the brief says fold into
    `fit_rungs[]`, and a rename re-aims rows for nothing.
  - T2-T4 are built beside their ternaries, and readers switch commit by
    commit.
- **The edit set is data**: `dec_fallback/refactor_edit_set.tsv` (rev 2 adds
  the force-loop arm's line; the trial catch's `if (st_phase == ST_LADDER) {`
  is noted, not listed, because the text occurs three times in `src/` and no
  anchor names any of them).
  - **Grain** (`stc67_report.md` §4 item 2): `def` only for a definition
    deleted, new or rewritten throughout; otherwise the changed `token` or
    `line`.
  - A commit that edits a line the file does not name is out of plan.
  - The re-aim list is DERIVED from the file (§4.4), never prose.
- **Every commit is a no-mover with no abi event.** The exception is B7,
  which is stream-5-only and also not an abi event.
- **The build lane re-derives on its own base.** It re-runs `state_readers.sh`,
  the edit set's line check (`sabotage_anchors.py`), and
  `sabotage_anchors.py --step` per commit (admin1008b's diff-derived
  `rerun_at`). Main moves under a design note.

### 4.2 The commit sequence

| commit | what | what moves |
|---|---|---|
| B0 | **Instrument** (no `src/`): the eleven deliverables after this table. Every floor is measured here, at B0's base, in the instrument's OWN population | nothing in `src/` |
| B1 | **The fallback trace** under `-DPCREC_CAND_TRACE` (`#ifdef` text only), on C1's macros `PCREC_CAND_TRACE_REC`/`_RECF`. ONE trace stream, no parallel mechanism. Slots: `fallback` (route = the label set, row = the row taken, plus the POST-ROW STATE TUPLE as `_RECF` fields: `dd`, `cr`, `sdr`, `flags_or`, `carry`, `latch`, `restart`); `admit` (route = scope, row = T2 row, verdict); `gate` (T3 row, PFLW); `stwhy` (T4 row); `attrib` (row = the token, plus the index of the fired row whose cell gave it). Declared literal site keys. The trace build is byte-swept against the default build. `row_reach` (B0 item 8) reads it. **Cross-record**: on B1's own base, the trace's per-compile fallback sequences equal (a) decfb0's probed-copy signatures and (b) the rev-2 prototype's probe sequences (`dec_fallback/reach/`), on all five variants. Instruments with no shared source agree, and only then is the trace the gate | nothing (`#ifdef` only) |
| B2 | **Implement**: T1's new columns and rows 0-4 (`fit_select` asks only `on & size`, so the new rows are transparent to it); T2, T3, T4 and the attribution walk beside the old code; `fit_tables_selfcheck`; the §1.9 invariants. No reader switched. Under the trace build, the **both-derivations oracle** compares the old branch against the walk at every arrival, and the old ternary against the row read at every token site. It aborts on any difference and runs in both orders (A's C2 shape). Carries the `limits.md` §8 / `run_resource_tests.sh:1338` `fof` wording hunk (§1.2) | the six `fit_rungs[]` row lines; `fit_select`'s filter line; `fit_rung_denied`'s `fof` line. Re-aims S421, S423 |
| B3 | **Replace the dispatch**. The catch branch's five tests (`:1179`, `:1203`, `:1229`, `:1277-1307`, `:1316-1319`) become ONE `fit_walk(labels)`. The `sets` routine writes the state. `fit_fired`/`fit_seq[]` replace `dropped_*`. The notes loop over fired rows. **Gate adds `make alloc`** (W4 for row 1, the new W5 for row 0) and `run_fallback_table.sh`'s sequence half | re-aims S253, S259 |
| B4 | **Replace the admission**. `prefilter_decision`'s `lang_nullable_declinable`, the two flags (now written from the row) and the ternary become T2's walk. The `has_var` ternary is gone and row 3 is the F1 holder. The `--emit-ir` chain reads `fit.admit`'s listing cells; the tokens and prose move verbatim. **HARD GATE (manager ruling)**: the `emit-ir-auto` stream identical on every variant and arm, and every `check_ir_value` row green, at parent and child | re-aims S102, S165, S216, S272, S612 |
| B5 | **Replace the token derivations**: `esel_of` → the attribution walk; the PFLW ternary → T3; `size_term_why` → T4; `VM_PREFILTER_WHY` → the fired row's `pfwhy`. The oracle has nothing left to compare and is deleted (A's C5 precedent). **The registry's two source legs retire HERE** (`axes_registry_check.sh:755`, `:782`), with `run_registry_tests.sh`'s PASS-count re-pin in the same commit, behind the observed-stamp leg that has been green since B0 (§4.5) | re-aims S238, S422 |
| B6 | **The listing reads the tables**: `engine-route`, `size-term` and `prefilter-lang` (`axes_dump.c`) project T1/T2/T4/T3 through a `list` column. It carries TODAY's order, name and desc verbatim, D-3-like and F-B2 descs included. `--list-axes` is byte-identical | nothing (stream 5 identical) |
| B7 | **Declared listing commit**, stream 5 only, NOT an abi event: see the list after B0's | `--list-axes` text only |

**B0's deliverables** (each DESIGNED here; the prototype in
`dec_fallback/reach/` shows the method on decfb0's population):
1. **Limit variants.** `emit_sweep.py` gains `--variant NAME=CFLAGS`, which
   builds BOTH sides with the variant's `-D` set. FIVE variants: decfb0's
   `plain`, `lowsize`, `lowdfa`, `lowboth`, plus `lowthr`
   (`-DPCREC_SIZE_TERM_THRESHOLD=1000`, `run_size_term.sh` §7's reference
   compiler), the only variant where `capacity-declined` has a population.
   Each variant also runs with an `-e utf8` base (critB2 M2): the shipped
   size-rung witnesses are utf8 (`(\p{Xwd})`, `\p{L}`).
2. **Stream `emit-ir-auto`** (critB2 B1; the B4 hard gate). `--emit-ir` at
   the DEFAULT engine, comparing stdout AND rc AND stderr, refusals included
   (a DFA-winning pattern refuses the listing; that refusal is part of the
   stream). Every variant × base encoding, plus the arms `-fno-prefilter`,
   `-fprefilter`, `-fno-prefilter-collapse`. A DIFFER-style floor per
   listing TOKEN per variant (the nine tokens plus `yes-collapsed`), with a
   named manifest for the thin ones. The pattern is handed as DECODED bytes
   (`--pattern-esc` is ignored by `--emit-ir`, F-B5). Stream 3
   (`--engine=vm`) stays as it is.
3. **Stream `stderr`** (critB2 M1; stream 7, replacing rev 1's notes-only
   stream). The full stderr and the rc of every stream-1/2 compile, compared
   verbatim: notes, warnings, refusal text and which cap a refusal names. A
   refusal floor per variant (`both_refuse` is now COMPARED, not only
   counted).
4. **Floors in the instrument's own population** (critB2 M2). Every DIFFER
   floor, token floor and refusal floor is measured at B0 over emit_sweep's
   own population (corpus `pattern`/`pattern-esc` rows, `--features all`),
   per variant and per base encoding. The prototype's counts in
   `dec_fallback/reach/out/reach.md` come from decfb0's population (each
   block's own flags/features/encoding) and are indicative, not pins.
5. **The attempt histogram, its own driver** (critB2 M2). decfb0's
   `census.py`, run over decfb0's population at the PARENT and at the CHILD
   of every commit through B5 (both built from `git archive`), compared
   parent vs child per variant: exact equality of the per-compile attempt
   count and transition signature. decfb0's committed tables are used once,
   for B1's cross-record, never as pinned absolute counts that would rot
   with the corpus.
6. **`check_ir_value` rows** (critB2 B1, the second half of the B4 hard
   gate). `tests/prefilter/run_prefilter_tests.sh` §7 gains a hand-written
   expected listing token for every T2 row and reached scope. Each row below
   is a shipped-limit witness unless marked; probed at `42ab7c25`:

   | T2 row | scope | witness (argv) | expected |
   |---|---|---|---|
   | backref | NONE | `(a)\1` | `no-backreference` |
   | linked-call | NONE | `(a\|b(?1)c)+` | `no-linked-call` |
   | var-nullable | NONE | `^${v}$` | `no-nullable-exact` |
   | nullable-exact | NONE | `(a*)*` | `no-nullable-exact` |
   | nullable-collapsed | SEL1 | `(?:ab){0,16000}` | `no-nullable-collapsed` |
   | overflow-drop | NONE | `^(?:(?:a\|b)*a(?:a\|b){20})?$` | `no-dfa-overflow` |
   | overflow-drop | SEL1 | `-fno-prefilter ^(?:(?:a\|b)*a(?:a\|b){20})?$` | `no-dfa-overflow` |
   | forced-on | NONE | `--engine=vm -fprefilter (a)b` (exists) | `yes` |
   | forced-on | SIZECAP | `-e utf8 -fprefilter ^(\p{Xwd}{1,3})?$` | `yes-collapsed` |
   | forced-off | NONE | `-fno-prefilter (a)b` (exists) | `no-fno-prefilter` |
   | forced-off | SIZECAP | `-e utf8 (\p{Xwd})` (§4.5) | `no-fno-prefilter` |
   | var | NONE | `a${v}b` (F-B1) | `no-engine-vm` |
   | var vs forced-off order | NONE | `-fno-prefilter a${v}b` | `no-fno-prefilter` |
   | default on | NONE | `(a)b` | `yes` |
   | default on | SEL1 | `(1{0,30}?[^]abc][^abc]){28,30}0+\|a` | `yes-collapsed` |
   | default on | SIZECAP | `lowsize` reference build: `(?:a\K){2,}b` | `yes-collapsed` |
   | default off | NONE | `--engine=vm (a)b` (exists) | `no-engine-vm` |
   | (DFA route) | — | `abc` | listing refused, rc ≠ 0 |

   The lowered reference build is built once in the script, as
   `run_size_term.sh` does. The two UNREACHED cells (row 5 and row 6 at
   SIZECAP) carry their argument as a comment (§4.3a). These rows are the
   hand-written, table-independent control of T2's listing half.
   **Correction (decfbB0b, recorded at B1):** the `forced-on` SIZECAP
   witness (`-e utf8 -fprefilter ^(\p{Xwd}{1,3})?$`) stamps
   `VM_PREFILTER_LANG_WHY "size cap retry, exact N > M"`, not `forced`: on
   the size rung T3's `rung` row beats the flag (§1.5, "A RUNG BEATS THE
   FLAG"), so the witness is a T3 `rung` (SIZECAP) witness as §4.3a's table
   already lists it, and this row pins only its LISTING token.
7. **Trace tooling** (critB2 M5). `trace_diff.py` gains `--order
   SLOT=ordered|set`, so the `fallback` slot is compared as an ORDERED
   sequence and every other slot as a SET (A's C1 condition was about
   cross-site ask order, which does not apply to a single recovery point);
   `--variant` composes with `--trace`: the trace build is built per variant
   (`-DPCREC_CAND_TRACE` plus the variant's `-D` set) and each variant's
   trace is compared with the same variant's parent trace.
8. **`row_reach`.** A committed instrument over the B1 trace: variant × arm
   × row × cell counts for T1 (by label), T2 (by scope), T3, T4, with a
   DECLARED zero list (the UNREACHED cells of §4.3a). It fails when a
   declared-zero cell becomes non-zero, or a reached cell drops to 0 against
   the parent. The arms are the §4.3 item 2 list, which now includes
   `-fno-prefilter` and `--tune=min-size` (critB2 M3). Until B1 lands, the
   prototype stands in.
9. **Census and call graph.** `state_readers.sh` (now derived, §2.1) and the
   edit set re-run on B0's base. `call_graph.py` gains `--family fallback`
   (roots: the recovery-point walk and its `applies` predicates,
   `prefilter_decision`, the T3 gate, `size_term_choose`, `esel_of`; seeds:
   the derived members), so `sabotage_anchors.py` computes `rerun_at` for
   the B commits rather than the plan reading it off owners (critB2 m2).
   Owner resolution stays a hard error.
10. **`alloc_check` W5** (critB1 MAJOR-3). `tests/core/alloc_check.c` gains
    a witness that drives `pcrec_emit_facts` with the injection placed in
    the force loop's allocations (arena allocations inside a forced fact's
    derivation, e.g. `src/facts/kset.c:183-186`), and asserts rc 0 and a
    `decline:force-failed` row. It is row 0's only witness; no corpus compile
    reaches the arm (§4.3a). `run_resource_tests.sh` §2b already runs
    `alloc_check` inside `make test`.
11. **`tests/codegen/run_fallback_table.sh`**, new, in `TEST_SECTIONS` and
    with its own mech arm `fallbacktable` (critB2 M4). Three halves, each
    hand-written and independent of the tables:
    - (a) SEQUENCES: for each witness, its expected fallback-row sequence,
      read from the trace build (so it lands at B1, hand-written from
      today's behaviour). Built once with the needed lowered `-D` sets;
    - (b) the OBSERVED-STAMP LEG (critB2 M7): each of the 8 `ENGINE_SEL`
      and 7 `UNROLL_K_WHY` values is stamped by at least one witness (K35
      floors), and the observed value set equals `match_api.md` §6.3's
      hand-written set (the docs leg's extraction, reused). Lands at B0 and
      stays green through B5;
    - (c) `VM_PREFILTER_LANG_WHY` (6 forms) and `VM_PREFILTER_WHY` witnesses
      with their hand-written texts.

**B0's outcome (lane decfbB0, 2026-10-08, base main `ab583f6b`; report
`../dev/lanes/decfbB0_report.md`).** Delivered: items 1-7, 9, 10 and 11(b)/(c).
Item 8 (`row_reach`) and item 11(a) (sequences) read the B1 trace and land
at B1; until then the prototype in `dec_fallback/reach/` stands in, as item
8 says. Choices the list left open, each recorded in the report:
- `--list-limits` cannot be the variant plumbing control (it prints
  limits.def's literal). Each variant instead names witness stamps that only
  its limits produce, and `plain` must produce none of them.
- Composition is not run per variant. facts and dumps run at the first
  base only.
- The two byte-figure `_WHY` forms are held to a SHAPE (`… N > 1000000`);
  the `nfa N` form is held to its full text.
- W5's post-loop trials are a NOTE, not an assertion: 9 of 11 die by
  SIGABRT in the listing's renderer (a pre-existing abort-on-OOM in
  `pcrec_emit_facts`, recommended as a K-entry).

**B1's outcome (lane decfbB1, 2026-10-08, base `lane/decfbB0` `6794d272`;
report `../dev/lanes/decfbB1_report.md`).** The fallback trace landed as
`#ifdef PCREC_CAND_TRACE` text only on C1's `_REC`/`_RECF`: `fallback`
(route = the label set, row + the post-row tuple `dd cr sdr fo ovw sc latch
restart`; site keys `fb-forcing`, `fb-nomem`, `fb-trial`, `fb-sel1`,
`fb-size`, `fb-refuse`), `admit` (route = the CR scope; T2's row read off
today's derivation in T2's order, plus the verdict), `gate` (T3's row read
off the PFLW), `stwhy` (the T4 token) and `attrib` (the token and the row
whose cell gave it: the design's fired-row INDEX is printed as that row's
NAME, which identifies it because every attributing row fires at most once
and which needs no `fit_seq[]` before B3). The gate (`emit_sweep --ref B0
--variant all --trace`, B1's ten site keys declared) is CLEAN; the
cross-record agrees with decfb0's probes and with the prototype on every
compile of all five variants (and the prototype's 14 arms); `row_reach.py`
and `run_fallback_table.sh` (a) landed (items 8 and 11(a)); B0's S-I2/S-I3/
S-I4 are S620/S621/S622.

`call_graph.py --family fallback`'s computed RE-RUN set reproduces rev 1's
list except S189/S191/S192. Those three are seen only by `--step` at B3, so
`rerun_at` is computed per commit, as item 9 intends. Eight
`compile_driver` rows are added at B3+B5.

**B2's outcome (lane decfbB2, 2026-10-08, base main `a29f02dd`; report
`../dev/lanes/decfbB2_report.md`).** T1's new columns and rows 0-4, T2-T4
and the attribution walk landed beside the old code with no reader
switched; `fit_tables_selfcheck`, §1.9's invariants and the both-orders
oracle run in the trace build only. The gate (`emit_sweep --ref a29f02dd
--variant all --trace --trace-order fallback=ordered`) is CLEAN: 0 movers in
all 90 cells, trace CLEAN, no `--trace-declared` needed. Choices the note
left open or wrote differently, each argued in the report:
- T2 row 4 carries `!has_var`, so it asks `empty_admits` only where today's
  derivation does (an ask is visible in `--emit-facts`); equal under E1.
- FitSel gains `st_phase` for row 2, which edits B3's initializer line at
  B2 (no anchor names it).
- The field is `EngineFit.pf_admit`, not `admit` (A's `u.admit` collided in
  the state census).
- The fired record is trace-build state until B3; the walk reads it through
  `Ctx.fit_seq`, T1's cells through the shared `FitCells`.
- §1.7's legal sequences are asserted as pairwise transitions.
- A B4 finding: rows 1-2 ask no nullability fact while today's derivation
  asks one first, so B4 moves `--emit-facts`' `used` column on
  backreference and linked-call patterns unless it keeps that ask.

**B3's outcome (lane decfbB3, 2026-10-08, base main `0f37bfd8`; report
`../dev/lanes/decfbB3_report.md`).** The catch branch is one
`fit_walk(&fs, fit_labels(&cx))`: the code-action rows are a switch, every
retrying row's writes come from its `sets` cell in one routine, `fit_select`
and `dropped_*` are deleted, `fit_record` grows the fired record in the
default build, and the notes loop over the fired rows. Zero default-build
movers is the light tier's gate (the report carries the verdicts). The
oracle's arrival and notes checks RETIRED (A's C5 precedent): their old side
is gone. Findings and choices:
- Deleting row 1 (`nomem`, S-F1) is an EQUIVALENT mutant: row 2's `on`
  mask leaves NOMEM out, so a NOMEM arrival falls to `refuse`, whose action
  is PROPAGATE's. D109's guard now lives in the LABEL derivation, which is
  where S259 is re-aimed.
- The `fb-size` record line (S624's anchor) is kept verbatim, so S624 is a
  re-run, not a re-aim.
- FitSel gains no fields: the walk takes the label set as an argument and no
  `applies` reads the fired record.
- The attempt histogram and the prototype re-anchor their probes
  (`dec_fallback/probes_b3.py`; `reach/build_reach.py`); the `sel1` probe
  restates the deleted booleans from their inputs rather than reading the
  walk.
- `sabotage_anchors.py --step B3` derives 34 re-runs; it does not reach rev
  1's S189/S191/S192, which run by judgment.

**B4's outcome (lane decfbB4, 2026-10-08, base `lane/decfbB3` `69ab9650`;
report `../dev/lanes/decfbB4_report.md`).** `prefilter_decision` walks T2
after its refusals and writes `fit.pf_admit`, the verdict and the two
declined-nullable flags from the row; `lang_nullable_declinable`, the
`has_var` ternary and the verdict ternary are deleted, and row 3 is F1's
holder. The `--emit-ir` `prefilter` line lists `yes`/`yes-collapsed` on a
verdict ON and otherwise the row's `list` cell and `note` cell (the chain's
prose, moved verbatim; `overflow-drop`'s note is a `%s` format over
`dfa_overflow_why`, `FitCells.pfwhy`'s shape). The oracle's `admit` and
`admit-listing` checks retired (A's C5 precedent); the trace's `admit`
record prints the walk's row, so the trace compare against the B3 parent
is what holds the walk to the derivation it replaced. Choices and findings,
each argued in the report:
- B2's finding 7 is wider than rows 1-2: `empty_admits` has no other asker,
  and the deleted derivation asked it on EVERY compile, so the walk alone
  would flip `--emit-facts`' `used` column on every backreference, linked
  call, DFA artifact and `--engine=vm` compile. B4 keeps ONE up-front ask
  (`has_var ? nullable : empty_admits`, result discarded) ahead of the walk;
  no mover is declared.
- The re-aims are S102/S165/S272 (the row's VERDICT cell handed to the
  default: equivalent mutants of the deleted-disjunct plants, outputs
  compared on their witnesses), S216 (`pfa_default_scope`), S612 (row 4's
  predicate), plus three the design did not list: S625 (its trace
  derivation is gone; the claim moves to row 3's NAME cell), S640 (rows
  gained the `note` line) and S176 (`--step` derives a re-run, but its old
  plant pins a local the decision no longer reads, so it would be
  UNDETECTED; re-aimed to `pfa_call`).
- `state_readers.sh` and `call_graph.py --family fallback` read the shape:
  `D` named the deleted local and its existence check passed on COMMENT
  text (fixed: code lines of `.c`/`.h`/`.def` only, fail-closed verified);
  `pf_admit_walk` joins `D` and `FB_ROOTS` (the family is B3's plus the
  walk). The prototype's `adm` probe re-anchors after the row's writes
  (`reach/build_reach.py`).

**B5's outcome (lane decfbB5, 2026-10-08, base main `54d82727`; report
`../dev/lanes/decfbB5_report.md`).** Every token is a table read:
`esel_of` returns the attribution walk (`fit_attrib_walk`, §1.7) behind its
kept premise check; the collapse gate walks T3 (`pflw_walk`/`pflw_value`
give `collapse` and `VM_PREFILTER_LANG_WHY` from one row); `UNROLL_K_WHY`
is T4's (`st_why_walk`); `VM_PREFILTER_WHY` is written where the latest
fired T1 row carries a `pfwhy` cell, with the cell as its format. The four
old derivations are deleted, and so is the both-derivations oracle (A's C5
precedent), with fbt (d) and `oracle_sweep.py`; the registry's two source
legs retired in the same commit as the `cx.size_term_why =` ternary
(`run_registry_tests.sh` 214 -> 210, measured), behind fbt (b). Spot
identity against `54d82727` (44 witnesses x `-o -`/`--emit-ir`/
`--emit-facts=byte`, stdout+stderr+rc) is 132/132, and the TRACE builds'
records are identical on the same 132. Choices and findings, each argued
in the report:
- `EngineFit.prefilter_declined_nullable{,_default}` are deleted: once the
  ternary went they were written and never read (the walk reads the
  admission row's `esel` cell).
- The trace's `attrib` record prints the walk's own source (the fired
  row's name) and `gate` prints T3's row, B4's `admit` shape: the trace
  compare against the B4 parent is what held the walks to the ternaries.
- `pcrec_fit_oracle_fail` is renamed `pcrec_fit_invariant_fail`: only
  §1.9's invariants call it now, and fbt (a)'s compiles fail on its
  `CANDORACLE` line or a signal (`trace_sane`, red-tested).
- Re-aims S238 (the two optional-contributor drop rows' cells planted
  PASS), S422 (the `pfwhy` test) and S626 (derived: its record derivation
  is gone; the plant names the first fired row). S645 is derived as a
  re-aim but its anchor text is kept (a re-run). `--step` derives 34
  re-runs; none plants a local the rewritten decisions stopped reading
  (B4 finding 3's check).
- `call_graph.py`'s `FB_ROOTS` gains the three token walks, `pflw_value`
  and `st_whys` (family 86 -> 98; the parent under the same roots is the
  same 98).

**B6's outcome (lane decfbB6, 2026-10-08, base main `84da351b`; report
`../dev/lanes/decfbB6_report.md`).** The three fallback listings project
the tables. T1, T3 and T4 rows (`fit_rungs[]`, `pflw_rows[]`, `st_whys[]`)
and T2's (`pf_admits[]`) carry an `axlist` column of `FbList` cells (axis,
order, name, deny/force, lever spelling, desc) holding TODAY's text moved
verbatim from `axes_dump.c`; `pcrec_fb_list_row(axis, i)` returns the cell
of order `i + 1` over the four tables and `emit_fb_axis` replaces the
seventeen hand `emit_pred_row` calls. `--list-axes` is byte-identical to
`84da351b` (default and `--features all/byte/utf8/recursion/backrefs`), the
five-stream `emit_sweep --every 10` reads 0 movers at full reach, and the
trace build's `fit_tables_selfcheck` holds each axis to orders 1..n carried
exactly once (red-tested: a duplicated order fails 56 fbt compiles). Choices
and findings, each argued in the report:
- `forced` and `selected` are produced by no row: their cells sit in
  select_engine.c's `esel_ends[]` beside the attribution walk.
- Placement rule: a cell sits on the FIRST row, in table order, whose cells
  produce its value. So `declined-nullable-default` is on `var-nullable`,
  `overflowed-dfa`/`-prefilter` and `collapsed-prefilter` on `sel1-collapse`
  (its off cell is ROLE), `size-cap-retry` on `prefilter-collapse`, and
  T3's `count-collapsed`/`exact` on `rung`/`nullable`. B7 re-places them
  with the order swap.
- The listing's lever columns (`--engine=` on `forced`, the deny and force
  bits on `denied` and `count-collapsed`) are cell fields, verbatim, not
  derived from T1's `deny`.
- Re-aims S627 S640 S642 S644 (rows are longer now); `--step` derives 24
  (the four plus 20 re-runs, S102 S165 S272 S625 being RE-AIM by owner with
  untouched single-line anchors). The family map is 99 (`FbList` joined).

**B7's deliverables:**
- `engine-route` lists in the attribution order (§6.2: two listed orders
  swap).
- `kind` changes from `predicate` to `list` on `engine-route`, `size-term` and
  `prefilter-lang`.
- F-B2's and `size-cap-retry`'s descs are corrected.
- A precedence sentence goes into `tuning.md` §2.16 (§4.7) and §2.17.
- The spec hunk is `registry.md` §6.
- The `tests/registry/` pins are re-read (§4.5).
- Optionally, the two new axes of §11 Q4(b).
- The movement is declared in a cells file, `listing_declared_B7.tsv`, and
  checked by C7's `listing_diff.py`.

**Not split further.** B3-B5 could be fewer, larger commits. They are split so
that each re-aimed row is verified in the commit that moves it, which is A's
reason.

### 4.3 How each commit proves 0 movers

Run against the parent (`--ref HEAD~1`, both sides built from `git archive`):

1. **`emit_sweep.py`, all EIGHT streams** (the six of today, `emit-ir-auto`,
   `stderr`), `--features all`, × the five limit variants × the two base
   encodings. Identity on every stream is the TOKEN IDENTITY gate.
   - Streams 1-2 carry every `match_api.md` §6.3 vocabulary this family
     writes: `ENGINE_SEL` (8 values), `UNROLL_K_WHY` (7), `VM_PREFILTER`,
     `VM_PREFILTER_LANG`, `VM_PREFILTER_LANG_WHY` (6 forms) and
     `VM_PREFILTER_WHY`.
   - The `--emit-ir` prefilter tokens are in `emit-ir-auto` (where T2's rows
     fire) and stream 3; the stderr and rc in `stderr`; the listing in
     stream 5.
   - Reach is held at the floors B0 pinned.
2. **The flag arms**, each with a DIFFER floor and its row(s):
   - `-fno-prefilter` (T2 row 8; row 6's SEL1 scope) — added (critB2 M3);
   - `-fno-prefilter-collapse` (rows 3/6 transparent);
   - `-fprefilter` (the [SEL-1] rows ineligible: overflows refuse);
   - `--fast-or-fail` (rows 5-9 denied; rows 3-4 NOT, the `fof` column);
   - `-fprefilter-collapse` (T3 rows 2-3);
   - `-fno-size-term` and `--unroll=4` (T4 `denied`/`option`);
   - `-fno-premul-table` (row 8 inapplicable);
   - `-fno-anchored-dfa` (row 7 inapplicable);
   - `--engine=vm`/`--engine=dfa` (the `forced` line; row 10 refuses a DFA
     overflow);
   - `--tune=min-size` (several size denials at once) — added (critB2 M3).

   Each runs at `plain` and at its variant (the [SEL-1] arms at `lowdfa`, the
   size arms at `lowsize`, `--tune=min-size` at `lowsize`). `capacity-declined`
   runs at `lowthr`.
3. **The trace** (B1's build, parent reference regenerated every commit):
   - the SET compare for every slot except `fallback` (A's gate);
   - an ORDERED compare of the `fallback` records per pattern, post-row
     state tuple included. An arrival's sequence IS the attempt ORDER, so for
     this family order is the property under test;
   - records floor per variant.
4. **Attempt count and order**:
   - the per-pattern sequence of `fallback` records equals the parent's;
   - the attempt histogram (B0 item 5), parent vs child, is identical per
     variant.

   The histogram is the independent control: a probed scratch COPY that
   shares no code with the tables. Its limits (critB2 m1): it shares the
   `setjmp` site and `rung->name` with what it watches, it lumps the trial
   catch with other failures (the prototype's `trial` probe splits them), and
   it sees no state. The trace's post-row tuple is what sees the state.
5. **The both-derivations oracle** (B2-B4): in both orders, under the trace
   build, at every arrival and every token site. It is a FILTER test (the old
   and new code share every predicate by pointer, A's C2 caveat). The
   attempt histogram, the bytes and the hand-written rows (B0 items 6 and
   11) are the independent controls.
6. `make test-codegen` (which runs [SABANCHOR]), the registry suite,
   `fit_tables_selfcheck` as a unit check, `state_readers.sh` against the
   commit, `sabotage_anchors.py`, `row_reach`, and mech on every re-aimed row
   and every re-run row whose `rerun_at` names the commit. B3 adds `make
   alloc`. The full `make test` is the manager's at merge.

**The controls and what they share.**
- Bytes, listing, stderr and rc are compared against the parent's binary
  (`git archive`).
- The attempt histogram comes from a probed copy of the BASE.
- The token vocabularies are the spec's hand-written §6.3 tables, read by the
  observed-stamp leg.
- The `check_ir_value` rows and `run_fallback_table.sh`'s sequences are
  hand-written from today's behaviour, per witness.
- None of them reads T1-T4 to decide what T1-T4 should say.
- The oracle shares predicates with its subject, and this note says so (item
  5).

### 4.3a Row reach: every row's witness, or UNREACHED with its argument

critB2 M3 asked for a per-row reach instrument. B1 builds it from the trace
(B0 item 8); revision 2 PROTOTYPED it now, to replace guesses with counts:
`dec_fallback/reach/` builds probed scratch copies of the tree (decfb0's
method, the probes on stderr only, the plain build's stdout and rc identical
to `build/pcrec` on all 4,810 cases), and compiles decfb0's population (4,794
distinct corpus blocks at `42ab7c25`; decfb0 counted 4,792 at its pin) plus 17
constructed witnesses (`reach/witnesses.tsv`; the capacity witness joined for
`lowthr`'s runs) under 5 limit variants × 14 flag arms (60 runs; `lowthr`
runs 4 arms). The full table, with one
witness per cell, is `dec_fallback/reach/out/reach.md`; the checks are
`dec_fallback/reach/out/analyse.txt`.

**What the prototype also checked** (computed from this note's row lists,
sharing no code with `src/`): T2's verdict equals the probed `fit.prefilter`
on every attempt; T2's listing cell equals `--emit-ir`'s value on every final
VM attempt; T3's PFLW equals the probed `prefilter_lang_why`; the attribution
walk equals the stamped `ENGINE_SEL`; no `once` row fired twice; the most
attempts any compile took was 9. **0 mismatches.**

**Reach at the `base` arm, per variant** (attempts; the arms column says
which arms reach a cell the base arm does not):

| table / row | cell | plain | lowsize | lowdfa | lowboth | lowthr | reached only by arm | shipped-limit witness |
|---|---|---:|---:|---:|---:|---:|---|---|
| T1 0 `forcing` | forcing | 0 | 0 | 0 | 0 | 0 | — | UNREACHED-in-corpus (below) |
| T1 1 `nomem` | nomem | 0 | 0 | 0 | 0 | 0 | — | UNREACHED-in-corpus (below) |
| T1 2 `size-term-trial` | other | 3 | 21 | 3 | 6 | 3 | | `(?:(?:(?:(?:(?:(?:a\|b){41}){41}){41}){41}){41}){41}` |
| T1 3 `sel1-collapse` | overflow | 4 | 4 | 95 | 95 | 4 | | `(1{0,30}?[^]abc][^abc]){28,30}0+\|a` |
| T1 4 `sel1-drop` | overflow | 2 | 2 | 69 | 69 | 2 | | `x(?!a)(?!b)…(?!q)` (tests/ucp/ctxnode.rxt:410) |
| T1 5 `unroll-rescue` | size | (T4 `cap-rescue`) | 14 | 0 | 21 | 0 | | lowsize: `(?:a\K){0,10}ab` |
| T1 6 `prefilter-collapse` | size | 3 | 104 | 0 | 84 | 3 | | `-e utf8 (\p{Xwd})` |
| T1 7 `drop-anchored` | size | 15 | 98 | 0 | 38 | 15 | | `-e utf8 \p{L}` |
| T1 8 `drop-premul` | size | 0 | 74 | 0 | 13 | 0 | | lowsize/lowboth: `-e utf8 (*UCP)(?i)[\dk]` |
| T1 9 `drop-prefilter` | size | 3 | 92 | 0 | 75 | 3 | | `-e utf8 (\p{Xwd})` |
| T1 10 `refuse` | other | 442 | 442 | 442 | 442 | 442 | | `\A*` (a parse refusal) |
| T1 10 `refuse` | overflow | 0 | 0 | 0 | 0 | 0 | `--engine=dfa`, `-fprefilter` | `--engine=dfa (?:ab){0,16000}` |
| T1 10 `refuse` | size | 0 | 86 | 0 | 37 | 0 | every arm incl. `--fast-or-fail` | `--fast-or-fail -e utf8 (\p{Xwd})` |
| T2 1 `backref` | NONE | 453 | 453 | 453 | 453 | 453 | | `(a)\1` |
| T2 2 `linked-call` | NONE | 106 | 112 | 106 | 112 | 112 | | `(a\|b(?1)c)+` |
| T2 3 `var-nullable` | NONE | 12 | 12 | 12 | 12 | 12 | | `^${v}{2}$` |
| T2 4 `nullable-exact` | NONE | 109 | 109 | 109 | 109 | 109 | | `(a*)*` |
| T2 5 `nullable-collapsed` | SEL1 | 1 | 1 | 1 | 1 | 1 | | `(?:ab){0,16000}` |
| T2 6 `overflow-drop` | NONE | 2 | 2 | 69 | 69 | 2 | | `^(?:(?:a\|b)*a(?:a\|b){20})?$` |
| T2 6 `overflow-drop` | SEL1 | 0 | 0 | 0 | 0 | 0 | `-fno-prefilter` | `-fno-prefilter ^(?:(?:a\|b)*a(?:a\|b){20})?$` |
| T2 7 `forced-on` | NONE / SIZECAP | 0 | 0 | 0 | 0 | 0 | `-fprefilter` | `-fprefilter (a)b`; `-e utf8 -fprefilter ^(\p{Xwd}{1,3})?$` |
| T2 8 `forced-off` | NONE | 0 | 0 | 0 | 0 | 0 | `-fno-prefilter`; also [PF-DROP]'s OR'd bit when row 9 fires at CR NONE (the `-f(no-)prefilter-collapse` arms) | `-fno-prefilter (a)b` |
| T2 8 `forced-off` | SIZECAP | 3 | 92 | 0 | 75 | 3 | | `-e utf8 (\p{Xwd})` (§4.5) |
| T2 9 `var` | NONE | 11 | 11 | 11 | 11 | 11 | | `a${v}b` |
| T2 10 `default` on | NONE / SEL1 / SIZECAP | 1268 / 3 / 3 | 1502 / 9 / 104 | 1268 / 94 / 0 | 1424 / 184 / 84 | 1509 / 9 / 3 | | `(a)b`; SEL1 `(a{1,3}){65}` |
| T2 10 `default` off | NONE | 2445 | 2602 | 2430 | 2481 | 2445 | | `b\|c` (a DFA artifact) |
| T3 1 `rung` | SIZECAP | 0 | 54 | 0 | 41 | 0 | `-fprefilter` at plain | lowsize `(?:a\K){2,}b`; plain `-e utf8 -fprefilter ^(\p{Xwd}{1,3})?$` |
| T3 1 `rung` | SEL1 | 1 | 7 | 29 | 119 | 7 | | `(1{0,30}?[^]abc][^abc]){28,30}0+\|a` |
| T3 2 `forced` | — | 0 | 0 | 0 | 0 | 0 | `-fprefilter-collapse` | `-fprefilter-collapse (x)?a{0,4}\Gb` |
| T3 3 `nullable` | — | 2 | 3 | 2 | 3 | 2 | | `^(?:(?:a\|b)*a(?:a\|b){20})?$`; `-fprefilter-collapse ^(a{2,9})*$` |
| T3 4 `exact` | — | 673 | 917 | 673 | 829 | 914 | | `[^c]{1,3}\z` |
| T3 5 `no-rep` | — | 2876 | 3069 | 2921 | 3014 | 2876 | | `(a)b` |
| T4 `option` / `denied` | — | 0 | 0 | 0 | 0 | 0 | `--unroll=4` / `-fno-size-term` | `--unroll=4 a(b\|c)+d` |
| T4 `default` | — | 2102 | 2037 | 2169 | 2099 | 2061 | | `a(b\|c)+d` |
| T4 `cap-rescue` | — | 0 | 14 | 0 | 21 | 0 | | lowsize `(?:a\K){0,10}ab` |
| T4 `size-model` | — | 2 | 14 | 2 | 16 | 16 | | `((?:(?:(?:[^a]{1,2}\|[^a]??\|.{0,2}?)+){0,8}(){2,3}){1,2}){2,…` |
| T4 `capacity-declined` | — | 0 | 0 | 0 | 0 | 1 | | lowthr `--engine=vm (((?:a{0,2}b)+c){0,20}d){0,20}e` (`run_size_term.sh` §7) |
| T4 `size-model-declined` | — | 0 | 2 | 0 | 2 | 27 | | lowsize `(?:a\K){0,10}b` |

**The UNREACHED entries**, each with its argument and the alternative
witness that the B0/B1 instruments use instead:

| cell | argument | alternative witness |
|---|---|---|
| T1 row 0 (`forcing`), every label | The force loop runs only after the attempt's artifact and stamps are complete, and the only things that can fail inside a forced ask are an arena allocation (`kset.c:183-186`, …) and a `pcrec_ctx_fail` internal error (`facts.c:130-344`), neither of which a well-formed compile hits | B0 item 10: `alloc_check` W5 (injection in the force loop) |
| T1 row 1 (`nomem`) | Allocation failure only | `alloc_check` W4 (S259's existing witness) via `make alloc`, in B3's gate |
| T1 row 2 × `overflow` / `size` | `size`: the size caps refuse "only on the DEFAULT attempt … or on the FINAL attempt" (`compile.c:2144-2147`), never on a trial. `overflow`: a trial differs from the default attempt only in the VM's unroll K, and the DFA machines (the prefilter pair) are built from the same NFA, so a machine that fit on the default attempt fits on every trial. Structural for `size`; an argument for `overflow` | none needed: the `on` mask keeps today's "any label" semantics; `row_reach` declares both cells zero |
| T1 rows 3-4 × `size`/`other`/`nomem`, rows 5-9 × `overflow`/`other`/`nomem` | outside the rows' `on` masks, by design | the mask itself is planted (§4.4 S-F7) |
| T1 row 5 at an arrival | its choice is made inside `size_term_choose`, not at an arrival | its reach is T4 `cap-rescue` (lowsize 14, lowboth 21) |
| T1 row 10 × `nomem` | row 1 applies to every `nomem` arrival first | — |
| T1 sequence `prefilter-collapse` → `sel1-collapse` | the collapse replaces `X{m,n}` by `X{min(m,1),}`, which never adds NFA states, so a collapsed prefilter overflowing where the exact one fit has no constructed instance. NOT proven: the subset construction's size is not monotone in NFA size in general | the attribution walk handles it (§1.7); the trace's legal-sequence invariant lists it |
| T1 sequence `sel1-collapse` → `prefilter-collapse` (critB1 m2) | needs F-B3's state (a [SEL-1] retry whose rebuilt exact prefilter fits), which needs the first overflow to be in a machine the hybrid's pair does not build; the rebuild is the same exact language under the same caps (§10 F-B3). 0 in 60 runs | as above |
| T2 row 5 at SIZECAP | entering CR_SIZECAP needs `fit.prefilter` on the refused attempt (`fit_collapse_applies`). At CR_NONE an `empty_admits` pattern has no prefilter (rows 3-4). At CR_SEL1 a collapsible `empty_admits` pattern has none (row 5 at SEL1). The only remaining route, CR_SEL1 without a collapsible repeat, makes row 5's `collapsible_rep` false. `force_on` is excluded by the row. Structural | rev 1's sabotage #3 is re-witnessed at SEL1 scope (§4.4 S-T2c) |
| T2 row 6 at SIZECAP | the m2 sequence above | as above |
| T2 rows 1, 2, 3, 9 at SEL1/SIZECAP | no prefilter is built for them, so no DFA overflows and no collapse rung applies | — |
| T2 row 7 at SEL1 | no retry is offered under `-fprefilter` | — |
| T2 row 8 at SEL1 | row 6 catches `dd && force_off` first | — |
| T2 row 10 off at SEL1/SIZECAP | `!would_prefilter` means a DFA-chosen artifact or `--engine=vm`; a rung retry is VM-routed and `--engine=vm` builds no prefilter to collapse | — |

### 4.4 Sabotage rows (derived re-aims, planned new rows)

`../start_table/sabotage_anchors.py ROOT call_graph.txt
dec_fallback/refactor_edit_set.tsv` at `42ab7c25` (rev-2 edit set), output
`dec_fallback/sabotage_anchors.tsv`: 535 sites / 517 row files, COUNT_MISMATCH
0. The one UNRESOLVED_SRC site (S571 in `memfn_sites.c:35`) is pre-existing
and outside this family. The forcing arm's new edit-set line moves no anchor.

**11 rows are RE-AIMED**, each in the commit that moves its anchor's text,
with intent re-verified (unchanged from rev 1):

| commit | rows | why |
|---|---|---|
| B2 | S421 (`--fast-or-fail` inert), S423 (`drop-prefilter` not degrading) | `fit_rung_denied`'s line gains `fof`; the row line gains columns |
| B3 | S253 (premul drop note unstamped), S259 (K60 propagation removed) | the state writes and the nomem test become rows |
| B4 | S102, S165, S272 (prefilter on backref / call / var), S216 (the default decline neutered), S612 (`empty_admits` anchor-blind) | the ternary and `lang_nullable_declinable` become T2 rows. S612's plant ("read bare `nullable`") moves to row 4's predicate; S272's to row 9 |
| B5 | S238 (size drop unstamped), S422 (`VM_PREFILTER_WHY` unstamped) | `esel_of` rewritten; the `SDR` test becomes a row read |

**RE-RUN** (anchor text kept, owner's body or reach changed by a commit).
Rev 1 read these off owners by hand; from B0 they are COMPUTED (B0 item 9,
`call_graph.py --family fallback` plus `--step`). Rev 1's list is the
starting point the computation must reproduce or explain:
- S237, S252, S420: the three `fit_*_applies` bodies, reached by the new walk
  (B2, B3);
- S189: `build_anchored_dfa` reads `size_drop_rung` written by a row (B3);
- S191, S192: `size_term_choose`, inside row 5/row 2's action (B3);
- S193: the size-cap label at `:2157` (B3);
- S64, S176: `prefilter_decision`'s untouched lines in a rewritten function
  (B4);
- S40: `pcrec_select_engine` calls the new `esel_of` (B5);
- S224, S225, S226: `vm_emit_stamps` around the `pfwhy` site (B5).

**New rows** (S-id = next free on main at build; S614+ today). Every row's
detector is a suite mech runs ([MECH-REACH]); the witness is named so the
row can be checked to reach. "fbt" = `run_fallback_table.sh` (B0 item 11),
"ir" = `run_prefilter_tests.sh`'s `check_ir_value` rows (B0 item 6), "alloc"
= `run_resource_tests.sh` §2b over `alloc_check`, "sweep" = the emitsweep
arm's streams, "trace" = the ordered `fallback` compare.

| id | table / cell | plant | witness | expected detector |
|---|---|---|---|---|
| S-F0 | T1 row 0 | `forcing` moved below `nomem` | W5 (force-loop injection) | alloc: W5 refuses where it listed `decline:force-failed` |
| S-F1 | T1 row 1 | `nomem` row deleted (S259's intent, as a row) | W4 | alloc (the K60 absorption pin) |
| S-F2 | T1 row 2 | `size-term-trial`'s `on` narrowed to `overflow\|size` (drops `other`) | the 6-deep tower `(?:(?:…(?:a\|b){41}…){41}` | `run_size_term.sh`'s R1 cell (it compiles today, refuses planted); fbt (a) |
| S-F3 | T1 rows 3/4 | rows swapped | `(1{0,30}?[^]abc][^abc]){28,30}0+\|a` (plain) | fbt (b) (`collapsed-prefilter` → `overflowed-*`); fbt (a) |
| S-F4 | T1 `fof` | `fof` true on rows 3-4 | `--fast-or-fail (1{0,30}?…)` at plain | fbt (a): the witness refuses where it compiles |
| S-F5 | T1 `fof`/`degrading` | `degrading` false on row 9 (rev 1 S423's twin through the new column) | `--fast-or-fail -e utf8 (\p{Xwd})` | `run_resource_tests.sh` [PF-DROP] cell |
| S-F6 | T1 `deny` | row 6's deny bit dropped | `-fno-prefilter-collapse -e utf8 (\p{Xwd})` | fbt (a) (`prefilter-collapse` appears) |
| S-F7 | T1 `on` mask | `drop-premul`'s `on` widened to `overflow` | `--engine=dfa (?:ab){0,16000}` | fbt (a) + trace: an extra `drop-premul` record before `refuse` (refuse × overflow today, 1 attempt) |
| S-F8 | T1 `sets.latch` | `dfa_was_engine` latched on every overflow, not the first | `^(?:(?:a\|b)*a(?:a\|b){20})?$` (DFA first, then the prefilter overflows) | fbt (b): `overflowed-dfa` → `overflowed-prefilter` |
| S-F9 | T1 `sets.carry` (`overflow_why`) | rows 3-4 stop carrying it | the same witness | sweep stream 1 (the `ENGINE_WHY` text); fbt (c) |
| S-F10 | T1 `sets.carry` (`size_cap_*`) | row 9 stops carrying it | `-e utf8 (\p{Xwd})` | fbt (c): `VM_PREFILTER_WHY "size cap retry, hybrid N > M"` loses its figures; S422's cell |
| S-F11 | T1 `sets.restart` | row 6 no longer restarts the size term | lowsize `T > T > T > T > T > prefilter-collapse > …` witnesses | trace (the trial records after the rung disappear); the histogram |
| S-F12 | T1 `sets.flags_or` | row 8 stops OR-ing `NO_PREMUL_TABLE` | lowboth `-e utf8 (*UCP)(?i)[\dk]` | fbt (a) (the retry refuses again: `drop-premul > refuse`) |
| S-F13 | T1 `sets.dd` | row 4 stops setting `dfa_disabled` | `x(?!a)…(?!q)` | fbt (a): the compile loops to the attempt cap and refuses with the exhaustion diagnostic |
| S-F14 | T1 `sets.CR` | row 3 writes `CR_SIZECAP` | `(1{0,30}?…)` | fbt (b)/(c) (`collapsed-prefilter`/`PFLW_SEL1` lost); the self-check's CR-uniqueness assertion |
| S-F15 | T1 `sets.SDR` | row 7 stops setting `SDR_NO_ANCHORED` | `-e utf8 \p{L}` | `run_anchored_match.sh`'s K53 drop-rung cell; fbt (a) |
| S-F16 | attribution walk | the backward walk stops at the latest fired row even when its cell is PASS (returns `selected`) | the m2 sequence has no witness; the walk's PASS is reached by `prefilter-collapse`-only compiles: lowsize `(\bcat\b)+` with its prefilter dropped | fbt (b): `size-cap-retry`/`selected` split. Declared WEAK: the plant is only distinguishable on the unpopulated m2 sequence for the ROLE half; the oracle (B2-B4) is the stronger detector while it exists |
| S-T2a | T2 row 3 | the F1 holder deleted | `^${v}{2}$` | fbt (b) (`declined-nullable-default` → `selected`); ir (`no-nullable-exact` → `no-engine-vm`) |
| S-T2b | T2 row 4 | the row's `empty_admits` read as bare `nullable` (S612's intent at its new home) | `^(\s+)*$` (nullanch's witness) | S612's existing detector, re-aimed |
| S-T2c | T2 row 5 / attribution | ladder cells read before admission cells (rev 1 #3, re-witnessed at SEL1 scope: the SIZECAP scope is UNREACHED) | `(?:ab){0,16000}` | fbt (b): `declined-nullable` → ROLE |
| S-T2d | T2 row 5 | row deleted | `(?:ab){0,16000}` | ir (`no-nullable-collapsed` → `yes-collapsed`); fbt (b) |
| S-T2e | T2 row 6 | the `∥ force_off` disjunct dropped | `-fno-prefilter ^(?:(?:a\|b)*a(?:a\|b){20})?$` | ir (`no-dfa-overflow` → `no-fno-prefilter`) |
| S-T2f | T2 row 7 | moved below row 10 | `--engine=vm -fprefilter (a)b` | ir's existing "forced back on" row |
| S-T2g | T2 rows 8/9 | swapped (rev 1 #5) | `-fno-prefilter a${v}b` | ir (`no-fno-prefilter` → `no-engine-vm`) |
| S-T3a | T3 rows 1/2 | swapped | `(1{0,30}?…)` | fbt (c) (`dfa overflow retry, exact nfa N` → `forced`) |
| S-T3b | T3 row 3 | deleted (wanted ∧ nullable falls to `exact`) | `-fprefilter-collapse ^(a{2,9})*$` | fbt (c) (`nullable collapsed language` → `exact`) |
| S-T3c | T3 projection | row 6's `pflw` cell read for a SEL1 rung (the projection keyed on the wrong CR) | `(1{0,30}?…)` | fbt (c) |
| S-T4a | T4 | `cap-rescue`/`size-model` swapped | lowsize `(?:a\K){0,10}ab` | `run_size_term.sh` §6's pin; fbt (b) at lowsize |
| S-T4b | T4 | `option` row deleted | `--unroll=4 a(b\|c)+d` | fbt (b) |
| S-T4c | T4 | `capacity-declined` below `size-model-declined` | lowthr `(((?:a{0,2}b)+c){0,20}d){0,20}e` | `run_size_term.sh` §7's cell |
| S-I1 | self-check | the bound check neutered with a planted row added (rev 1 #6) | — | the `fit_tables_selfcheck` unit check |
| S-I2 | trace tooling | the `fallback` slot's order downgraded to SET (rev 1 #7) | a planted swap of two [SEL-1] records | emitsweep arm: `trace_diff.py`'s own failing-direction control |
| S-I3 | `emit-ir-auto` stream | the arm's `-fno-prefilter` lost in plumbing | — | emitsweep arm: the per-token floor on `no-fno-prefilter` |
| S-I4 | observed-stamp leg | one `ENGINE_SEL` witness dropped from fbt | — | fbt (b)'s K35 floor for that value (mech arm `fallbacktable`) |

S-F16 is declared WEAK in its own row, not hidden: the m2 sequence has no
population, so only the oracle (B2-B4) and the PASS-only compiles see the
walk's back step.

### 4.5 Structural checks that parse the source

- **`tests/registry/axes_registry_check.sh:782`** extracts `RX_UNROLL_K_WHY`'s
  values from `compile.c`'s `cx.size_term_why =` chain, and **`:755`**
  extracts `ENGINE_SEL`'s from `pcrec_engine_sel_name`'s returns. Both RETIRE
  AT B5 (critB2 M7, manager ruling): `:782` in the commit that deletes the
  chain it reads (it would go red there), `:755` in the same commit, because
  from B5 the token comes from the tables' cells and the leg's two sides
  would share the spelling function. The retirement is allowed ONLY because
  the observed-stamp leg (B0 item 11(b)) has been green since B0: the stamps
  every witness actually emits, held to `match_api.md` §6.3's hand-written
  sets with K35 floors for all 8 `ENGINE_SEL` and all 7 `UNROLL_K_WHY`
  values. `RX_VM_RESEED`'s precedent (`:788-795`) is the model: keep the
  docs leg, retire the source leg, put the emitter half in witnesses.
  `overflowed-prefilter` has no shipped-limit witness; the fbt leg uses its
  `lowdfa` reference build for it.
- **`run_registry_tests.sh`'s PASS-count pins** move with the retired legs in
  the B5 commit. This is D94 addendum's second reader class, a count that
  cites no number of B's. Re-pin by measurement in the same commit.
- **`tests/registry/limits_check.sh:525-528`** lists `SDR_*` names as
  non-limit enumerators. They are unchanged in B.
- **`run_resource_tests.sh`, `run_prefilter_collapse.sh` and
  `run_tune_dial.sh`** name `ovf_eligible`/`retry_collapse`/`fit_rungs[]`/
  `CR_*` in COMMENTS only (grep at `42ab7c25`). They move with the commit
  that retires the identifier (B3), A's `reader_grep` rule.

### 4.6 Spec hunks

Readers of the retiring identifiers outside `src/` were found by grep.
- `docs/spec/` names `fit_rungs[]` (`limits.md:801`, unchanged: the name is
  kept), `dfa_disabled` (kept) and `prefilter_lang_why` (kept).
- B2 owes ONE wording hunk with no behaviour change: `limits.md` §8's
  `--fast-or-fail` sentence ("denies every row the table marks degrading —
  today all five") becomes "every SIZE-CAP row the table marks degrading",
  because B2 adds degrading rows outside the switch's reach (§1.2, critB2
  m3). The comment at `run_resource_tests.sh:1338` moves with it.
- B7 owes:
  - `registry.md` §6 (the three `kind` flips; the listing order);
  - `tuning.md` §2.16 and §2.17 (the precedence sentences);
  - `limits.md` §8, only if §11 Q4(b) adds the ladder as a listed axis (a
    pointer sentence).

---

## 5. After B: the movers as table edits

### 5.1 [DEC-COLLAPSE-WASTE]: the §4.1 fix, filed as its own row

**Moved out of B by the manager's ruling on critB1 MAJOR-1/2.** The row is
filed in `docs/dev/plan.md` as STATE:not-started, FILED, NOT scheduled. B
keeps every attempt and every stamp value; in B the drift is the declared
cell `requires = FIT_REQ_NONE` on T1 rows 3 and 6.

**critB1's three-way split.** A collapse rung (T1 row 3 or 6) is offered,
today, on every attempt its `applies` admits. Of the attempts it buys:
- **(i) no collapsible repeat** (`!pfc_rep`): the collapsed lowering IS the
  exact one, so the rebuilt machine fails again. This is survey §4.1's
  missing conjunct;
- **(ii) nullable but not `empty_admits`**: T2 row 5 (which reads
  `empty_admits`) keeps the prefilter, T3 row 3 (which reads bare `nullable`)
  declines the COLLAPSE, so the exact machine that just failed is rebuilt and
  fails again. Live at shipped limits: `^(?:(?:a|b)*a(?:a|b){20})?$` (3
  attempts, `overflowed-dfa`; 2 under `-fno-prefilter-collapse`) and `-e utf8
  --features all ^(\p{Xwd}{1,3})?$` (3 attempts, `size-cap-retry`; 2 under the
  deny);
- **(iii) `empty_admits`**: T2 row 5 declines the prefilter, stamped
  `declined-nullable`. [OPT-4.1]'s DESIGNED outcome, not waste.

**Measured** (`dec_fallback/reach/out/analyse.txt`, `base` arm; rung
attempts by class, decfb0's population):

| variant | SEL1 (i) | SEL1 (ii) | SEL1 (iii) | SEL1 collapsed | SIZECAP (i) | SIZECAP (ii) | SIZECAP collapsed |
|---|---:|---:|---:|---:|---:|---:|---:|
| plain | 1 | 1 | 1 | 1 | 2 | 1 | 0 |
| lowsize | 1 | 1 | 1 | 7 | 48 | 2 | 54 |
| lowdfa | 63 | 2 | 1 | 29 | 0 | 0 | 0 |
| lowboth | 63 | 2 | 1 | 119 | 42 | 1 | 41 |

**The two candidate forms**, as critB1 stated them:
- **(a) compile-time only**: rows 3 and 6 gain `requires = pfc_rep &&
  !(nullable && !empty_admits && !force_prefilter)`. It removes (i) and (ii)
  and keeps (iii). Every final token is unchanged (the next row fires at
  once: `sel1-drop` or `drop-prefilter`, the same tokens), and F-B3 becomes
  structurally unreachable.
- **(b) the gate reads `empty_admits`**: T3 row 3 tests `empty_admits`
  instead of `nullable`, so (ii)'s collapsed language is BUILT. A TOKEN mover:
  `^(?:(?:a|b)*a(?:a|b){20})?$` moves `overflowed-dfa` → `collapsed-prefilter`.
  It also unifies T2 row 5 and T3 row 3 onto one fact, which (a) does not.

**The stamp-value-mover fact (critB1 MAJOR-2).** Form (a) is NOT
artifact-neutral: `VM_PREFILTER_WHY` carries the LAST refused attempt's byte
figure, and deleting the wasted attempt changes which attempt that is. On
`-e utf8 --features all (\p{Xwd})` it reads `hybrid 1028613 > 1000000`
today and `1028607` with the deny; the `.c` diff is that one line. So (a) is
a stamp-VALUE mover, and its D76/D94 status (abi or not, readers by grep,
the byte-count reader class included) is ruled when the row is built.

**Its STEP 0**: the census above re-run on the row's own base with the fate
split per class, plus a compile timing (decfb0 counted attempts and did not
time them), plus the `VM_PREFILTER_WHY` mover census for form (a).

### 5.2 F1 and F-B1: one row deleted, one cell changed

Recommended as ONE later row (§11 Q1, Frank's):
- delete T2 row 3 (`var-nullable`): the nine `^${v…}$` rows move
  `declined-nullable-default` → `selected`, the truth (`has_var` turned the
  prefilter off, `selected` is what a non-nullable var pattern reads today);
- change row 9's listing cell from `no-engine-vm` to a new DD-8 token
  `no-variable`, with a note on the `no-backreference` pattern ("erasing a
  `${…}` variable is not a superset; no flag changes this").

It is a token mover and a listing-token mover, so it carries the spec hunk:
- `match_api.md` §6.3 `declined-nullable-default` wording;
- the `--emit-ir` vocabulary in `docs/spec/`;
- the abi decision by D76/D94. A stamp VALUE moves on 9 artifacts:
  [NULLABLE-ANCH] bumped for the same shape, and `sel_cost.md` §4.6 argues a
  new value of an existing stamp is not scaffolding. The ruling is the
  manager's at that row, by grep of readers.

### 5.3 `--fast-or-fail` over the [SEL-1] rows: one column, if ever wanted

`fof` is `false` on rows 3-4. Making the policy reach them is two cells. §8
recommends against it (§11 Q2, Frank's).

### 5.4 Token/why separation (D151 addendum 2, later abi row)

The columns are already separate: `esel` is the NAME and `pfwhy`/`pflw`/`ukw`
are the WHY. Separation then changes spellings in cells, not structure.

### 5.5 [SEL-COST]'s post-build rows

See §8.1.

---

## 6. §4.5 and §4.6 under B

### 6.1 §4.5: `--emit-ir` does not know [PF-DROP]

**The mechanism.** Row 9 (`drop-prefilter`) ORs `PCREC_NO_PREFILTER` into the
retry's options (`compile.c:1467`). On the next attempt T2's `forced-off` row
fires and lists `no-fno-prefilter`, naming a flag the caller never passed.
- The stamp side is right: `VM_PREFILTER_WHY` reads the FIRED ROW (row 9's
  `pfwhy`).

**In B.** §4.5 becomes "two writers of one input bit, and a listing cell keyed
on the bit instead of on the writer". The fix (a later listing mover) is a T2
row placed before `forced-off`: `dropped-for-size` (`fit_fired` has row 9,
off), with its own listing token `no-size-cap` and the `pfwhy` text as its
note. That is one row.

**Population.** One shipped-limit witness, `(\p{Xwd})` `-e utf8`, plus the
lowered variants (T2 row 8 at SIZECAP: lowsize 92, lowboth 75).
- It is a LISTING mover: `--emit-ir` streams only, no `.c` byte.
- It is not in B, so it is filed and recommended together with §5.2's row:
  one listing-vocabulary event, one spec hunk (§11 Q1).

### 6.2 §4.6: `ENGINE_SEL`'s listed order ≠ evaluated order

**Under B5 the evaluated order IS the table order.** It is the attribution
walk: `forced`, then T2 cells in T2 order, then T1 cells (the fired ones,
latest first), then `selected`.

Listing each value at its FIRST producing cell in table order gives:

| order | today's listing | B7's listing |
|---|---|---|
| 1 | forced | forced |
| 2 | declined-nullable-default | declined-nullable-default |
| 3 | collapsed-prefilter | **declined-nullable** |
| 4 | declined-nullable | **collapsed-prefilter** |
| 5 | overflowed-dfa | overflowed-dfa |
| 6 | overflowed-prefilter | overflowed-prefilter |
| 7 | size-cap-retry | size-cap-retry |
| 8 | selected ("always (fallback)") | selected (the walk's fallback, reached through PASS cells too) |

So §4.6 is fixed with **zero artifact movers** (no `ENGINE_SEL` value moves
on any artifact; B5 already proved that). It is NOT zero LISTING movers:
- orders 3/4 swap;
- `kind` becomes `list`;
- the `size-cap-retry` and `declined-nullable-default` descs are corrected.

So it is B7, a declared listing commit like C7. B6 alone (projection with
today's order kept in the `list` column, C6's shape) is byte-identical and
does NOT fix it: it moves the disagreement from code to data, where B7 deletes
it.

**Why T2 orders `nullable-exact` before `nullable-collapsed`.** They are
disjoint on CR, so their order is free in both derivations. This order is the
one that keeps B7's move to a single swap. The alternative order moves three
listed orders.

---

## 7. Siblings of the family (forest-for-the-trees lens)

| member | question it answers | hosted in B? | why |
|---|---|---|---|
| `fit_rungs[]` size-cap ladder | which smaller form after a size refusal | **yes** (T1 rows 5-10) | the host |
| [SEL-1] overflow rungs | what after a DFA overflow | **yes** (rows 3-4) | the survey's §3.1 charter |
| the `--emit-facts` force-loop arrival | absorb a forced ask's failure | **yes** (row 0, rev 2) | the same recovery point; without it the table is not total (critB1 MAJOR-3) |
| K60 nomem propagation | propagate, don't absorb | **yes** (row 1) | an arrival label; its ordering was a comment (K60), now a row order |
| [ART-SIZE] trial catch | a ladder K failed | **yes** (row 2) | the same recovery point; its "any reason" rule becomes `on` |
| prefilter admission (Q8) | does the VM get a prefilter | **yes** (T2) | ruled into B (D151 add. 2) |
| `--emit-ir` prefilter chain | why no prefilter (listing) | **yes** (T2's listing cells) | the second derivation of Q8 |
| collapse build gate + PFLW | which language, and why | **yes** (T3) | its reason reads which rung fired |
| **T2 row 5 vs T3 row 3** | is a nullable collapsed rescue worth building | **both hosted, NOT unified** | two derivations of one question on two facts (`empty_admits` vs `nullable`); unifying them moves attempts or tokens, so it is [DEC-COLLAPSE-WASTE]'s (§5.1) |
| `UNROLL_K_WHY` | the size term's verdict | **yes** (T4) | the plan row lists the token; §4.7's precedence |
| `ENGINE_SEL` (`esel_of`) | how the engine came to be | **yes** (attribution walk) | the survey's "read which row fired" |
| `VM_PREFILTER_WHY`, drop notes, budget note | why the prefilter/contributor went | **yes** (cells; the budget note is a label attribute) | readers of "which row fired" |
| auto engine choice (`pcrec_select_engine`'s `default:` arm) | DFA or VM | **no** | the engine-selection family (D124); [SEL-COST] §4.3 plans `sel_auto_rows[]` as ITS table; B consumes `fit.chosen` |
| `forces_dfa_overflow` | the retry's input to selection | **no** | the selection channel [SEL-COST] reuses; B writes `dd` (row `sets`), selection reads it |
| `-fprefilter` / `--engine=dfa` do-or-die refusals (`select_engine.c:696-725`) | refuse a request | **no** | input validation BEFORE any decision; the sibling home is [OPT-SETS]' constraint table (`option_sets.md` §2.7, refuse/inert/derive) |
| `size_term_choose`'s argmin + capacity floor | which K | **no** (inside row 5/row 2's action) | an optimizer inside a row (memory `pcrec-decisions-as-first-match-tables`), flagged |
| `--tune` positions ORing deny bits at entry | the dial | **no** | the option-set family; noted because row 8's `applies` reads the bit `--tune=-2` sets |
| `build_anchored_dfa`'s own overflow → search-filter fallback (`compile.c:356-372`, `PCREC_ANCHORED_MAX_STATES`) | build the optional machine, or fall back to the search filter | **no** (rev 2, critB1 m3) | a fallback that never reaches the recovery point: the optional machine saves and restores `dfa_overflowed` and the artifact keeps `anchored_ok == false`, a selection outcome inside one attempt. It is a sibling of row 7 (which drops the same machine for SIZE) with its own population-zero arm (`run_anchored_match.sh` drives it by lowering the cap); hosting it would add an arrival that does not exist today |
| the start table's RETRY rows | re-seed or step after a failed ATTEMPT | **no** | a different question (inside one compile's matcher, at run time); refactor A's |
| [DEC-POSDOM] | which positions are legal | **no** | A's sibling, its own later row |

The family has four remaining dispersed SIBLINGS: auto engine choice, request
refusals, the dial ORs, and the anchored machine's own fallback. Three have a
planned home table ([SEL-COST], [OPT-SETS]); the fourth is a single
in-attempt fallback with no second member to unify with. No further
unification is proposed.

---

## 8. Interaction with [SEL-COST] §4 and `--fast-or-fail`

### 8.1 [SEL-COST]'s post-build rows land IN T1

`sel_cost.md` §4.3 plans each post-build decline to be reported like an N1
over-budget, "`cx->dfa_disabled` plus a reason, then `compile_driver`'s
existing one-shot retry", with a new token `"cost-declined"` (§4.6). Under B:
- the DFA build reports a sixth arrival label, `cost` (the "reason field"
  `forces_dfa_overflow` was to grow);
- T1 gains row(s) `on = cost`, after rows 3-4;
- each row carries its own `deny` (`-fno-sel-<row>`), `degrading = false`
  (`sel_cost.md` §4.4: a row exists only because it is faster) and `fof`
  stated `false`;
- it sets `dd = SET` and `esel {off: cost-declined}`;
- the attribution walk needs no edit: the row's cell IS the token.

**Amendment owed to `sel_cost.md` when that row is built** (not edited here,
D80 for designs):
- its §4.6 sentence placing `cost-declined` "in `esel_of`'s ladder between
  `ESEL_SELECTED` and the overflow range" becomes "a T1 row's cell";
- its §4.3 claim that `COMPILE_MAX_ATTEMPTS` "does not move" is true of the
  attempts actually taken (a cost row and a [SEL-1] row are exclusive: both
  set `dd`, and rows 3-4 need `!dd` or a SEL1 collapse). It is false of §1.8's
  checked bound, which grows by the row's `retries` (25 → 26). That is a safe
  over-approximation; the bound is a loop limit plus one diagnostic number,
  never an artifact byte.

### 8.2 `--fast-or-fail`

Today it denies every DEGRADING row of the size-cap ladder (`limits.md` §8).
`cli.md:414` calls it "a size POLICY". It does not touch [SEL-1], whose two
rungs also cost run time. That scope is consistent with the spec but stated
nowhere as a scope.

B makes it a column: `fof` is true on rows 5-9 and false on rows 3-4.
`--fast-or-fail`'s reach is then visible in the table, and in `--list-axes`
if §11 Q4(b) lists T1.

**Recommendation: keep the scope.** A caller who wants a DFA overflow refused
already has the do-or-die levers: `--engine=dfa` refuses on overflow, and
`-fprefilter` makes the [SEL-1] rungs ineligible. Widening `fof` would give
the same behaviour a third spelling. If Frank wants it, it is two cells and a
mover row with `limits.md` §8's hunk (§11 Q2).

---

## 9. Standing questions (docs/design/CLAUDE.md)

### 9.1 The measurement regime: relevant only for what B does NOT change

**B reads no timing, and every count it cites is deterministic.**
- The counts are compile outputs over the corpus: decfb0's token and attempt
  tables, the rev-2 prototype's reach table, the reader census and the anchor
  census. They are the same on any box with the same `gcc` and `-D` set,
  because selection is a compile-time function of the pattern and the limits.
  The prototype ran on the Linux dev box (gcc 15.2, `-O1` scratch builds, as
  decfb0's).
- Their regime is "shipped limits" or one of four NAMED lowered-limit
  reference builds (`lowsize`, `lowdfa`, `lowboth` from decfb0; `lowthr` from
  `run_size_term.sh` §7). The lowered values were chosen to give the ladders
  a population, and not bisected. A different choice changes the floors,
  never a decision B makes.
- **Population is part of the regime** (critB2 M2): the prototype's counts
  are over decfb0's population (each block's own flags, features, encoding
  and engine); emit_sweep's population is `--features all` per pattern. A
  floor carried from one to the other would be wrong, so B0 re-measures every
  floor in the instrument's own population.

**Two inputs B keeps, measured by others in a regime that could matter.**
- The `degrading` column's cost figures (`limits.md` §8, Mac directional).
  B neither reads nor changes them.
- [DEC-COLLAPSE-WASTE]'s compile-time delta is unmeasured: decfb0 and the
  prototype counted attempts and did not time them; that row's STEP 0 owes
  the timing.

### 9.2 The independent control: relevant

**For each gate.**
- **Bytes, listing, stderr, rc**: against the parent built from `git
  archive`.
- **Attempt count/order**: against decfb0's probed copy of the parent (B0
  item 5), which shares no code with T1 and is cross-recorded against B1's
  trace once.
- **Token vocabularies**: the spec's hand-written §6.3 tables, read by the
  observed-stamp leg (B0 item 11(b)), which shares nothing with the tables or
  the spelling function.
- **T2's listing**: the hand-written `check_ir_value` rows (B0 item 6).
- **T1's sequences**: the hand-written expected sequences in
  `run_fallback_table.sh` (B0 item 11(a)).
- **The both-derivations oracle** shares predicates with its subject, and is
  stated as a filter test only.
- The dump-vs-source registry legs RETIRE at B5, exactly when they would
  start sharing a source, and only behind the observed-stamp leg (§4.5).

**Who counts the population (K35).**
- `state_readers.sh` counts the members, from the declarations (§2.1).
- `row_reach` (prototype now, B1 later) counts every row's reach per variant
  and arm, with a declared-zero list.
- decfb0's census counts each token and attempt shape per variant; it is
  compared parent vs child, never re-derived from T1.
- `sabotage_anchors.py` counts the rows.

**[MECH-REACH].**
- Every re-aimed row keeps its `SAB_REACH`.
- Every new row in §4.4 names its witness; the witnesses that exist only
  under lowered limits get their detector a lowered reference build inside
  `run_fallback_table.sh` (or `run_size_term.sh`'s existing ones).
- Row 0's witness is the alloc injector (W5), since no compile reaches the
  arm; row 1's is W4.
- A row whose detector cannot see its plant on any populated input ships
  declared WEAK or UNREACHED, with the reason (S-F16).

### 9.3 What moves when data is regenerated: relevant, nothing for B1-B6

B has no data file, calibration or generated table. T1-T4 are code.
- **No emitted byte moves, so there is no abi event**: identity on streams
  1-2 is B's own gate.
- **B2 moves one spec sentence** (`limits.md` §8's `fof` wording), describing
  unchanged behaviour.
- **B7 moves `--list-axes`**:
  - stream 5 only;
  - the registry pins re-pinned by measurement (D94 addendum's count-reader
    class: `run_registry_tests.sh`'s PASS counts, `axes_registry_check.sh`'s
    value sets);
  - spec hunks in the same commit (§4.6, D80).
- **decfb0's `results.md` and the prototype's `reach/out/` are regenerated
  only on a base** (their probes cannot patch post-B3 code). They are pinned
  evidence, not regenerated per commit.

---

## 10. Findings this design adds (not in the survey or decfb0)

- **F-B1 (PROBED).** `build/pcrec --features all -p rx --emit-ir --pattern
  'a${v}b'` lists `prefilter  no-engine-vm  --engine=vm -- the VM scans from
  search_from itself (R21 E-6)` under `auto`.
  - The chain's own header (`emit_vm.c:9436-9441`) promises never to name a
    route no flag explains.
  - The `(a)${v}` case lists the same.
  - It is §4.5's sibling (a listing reason keyed on an input, not on the
    decision).
  - Preserved in B; fixed with F1 (§5.2).
- **F-B2 (PROBED).** `engine-route`'s `declined-nullable-default` desc says
  "auto (or forced --engine=vm plus -fprefilter)". `--engine=vm -fprefilter`
  on `(a*)*` stamps `forced` and `VM_PREFILTER "hybrid"`, because
  `lang_nullable_declinable` excludes `force_on` and `would_prefilter`
  excludes `--engine=vm`. It is a stale desc (D-3's class) and is corrected at
  B7.
- **F-B3 (READ, population 0, now with an argument).** `esel_of` arm 7 tests
  `CR_SEL1 && fit->prefilter`, not `prefilter_collapsed`. A [SEL-1] collapse
  retry that kept an UNcollapsed prefilter would stamp `collapsed-prefilter`
  beside `VM_PREFILTER_LANG_WHY "no counted repeat"`. Revision 2 found it in
  none of its 60 runs, and the reason is structural in all but one corner:
  without a collapsible repeat the retry rebuilds the SAME exact language
  under the same caps, so it overflows again (the prototype shows exactly
  this on `x(?!a)…(?!q)`: a SEL1 attempt with no repeat, then `sel1-drop`).
  The corner is an overflow in a machine the hybrid's pair does not build
  (the DFA engine's own forward machine with its views, or the subset-element
  budget summed over a different machine set); no constructed instance was
  found. It closes structurally with [DEC-COLLAPSE-WASTE] form (a).
- **F-B4 (READ).** The label set is not exclusive in the CODE: `dfa_overflowed`
  can be set without a `longjmp` by an optional machine (`ir/dfa.c:203-206`).
  The one optional machine restores the flag (`compile.c:356-370`), so no
  arrival carries both labels today. T1's walk (rows 3-4 before 5-9, `on` by
  label) reproduces today's precedence for the set anyway. Precedence is
  [SEL-1] first, falling through to the size rows when neither [SEL-1] row
  applies, as the code does today at `:1308`.
- **F-B5 (PROBED, rev 2; a pre-existing CLI defect outside B).**
  `--pattern-esc` is IGNORED by `--emit-ir` and `--emit-facts`. Both
  branches (`cli/main.c:1988`, `:2021`) return before the escape decode at
  `:2359`, so the listing describes the RAW escaped text: `--pattern-esc
  --emit-ir --pattern '"(\\z)*"'` lists `yes` where the `.c` compile of the
  decoded `(\z)*` is `declined-nullable-default`, and `--pattern-esc
  --emit-facts=byte --pattern '"\x28a\x29b"'` lists `RX_ENGINE "dfa"` where
  the `.c` compile of `(a)b` is `vm`. No error, rc 0. Found because the
  prototype first used decfb0's `--pattern-esc` argv and its listing check
  failed on 558 cells. Consequences: every B0 listing stream hands decoded
  bytes (emit_sweep already decodes); the defect itself wants a K-entry (the
  lane report recommends one; this note does not file it).
- **The §4.1 split, completed (critB1 MAJOR-1).** Rev 1 split the waste in
  two; it is three (§5.1), and the middle class is live at shipped limits.
  The fix left B (§5.1, [DEC-COLLAPSE-WASTE]).
- **The admission tables were checked before the code exists (rev 2).** The
  prototype computed T2's verdict and listing, T3's PFLW and the attribution
  walk from this note's row lists alone, and they matched today's probes,
  stamps and `--emit-ir` on every compile of 60 variant × arm runs. It is
  evidence for the tables' CONTENT; B's code is held by its own gates.

---

## 11. Open questions for Frank (each with a recommendation)

**RULINGS (Frank, 2026-10-08):**
- **Q1 YES.** [DEC-VAR-ATTRIB] is filed in plan.md as one later mover row.
- **Q2 KEEP.** `fof` stays on the size rows only. B2 carries the limits.md §8 / run_resource_tests.sh:1338 wording fix. A side ruling: the flag's NAME over-promises (it is a size-cap policy, not "fast"), so it is renamed `--size-cap=refuse|degrade` (default `degrade`) as its own later row, [SIZE-CAP-FLAG], NOT folded into B.
- **Q4(b) YES.** B7 lists T1 and T2 as new `--list-axes` axes, with a registry.md spec hunk and a bench inbox note.
- The manager takes the recommendations on Q3, Q5 (moved to [DEC-COLLAPSE-WASTE]), Q6, Q7 and Q8 (the panel has run).


The manager took Q3, Q5, Q6 and Q7 as recommended (Q5 reframed: its subject
is now [DEC-COLLAPSE-WASTE], §5.1) and Q8 is done (the panel). Three stay
open:

1. **F1 and F-B1 as one later mover row.** File one row, [DEC-VAR-ATTRIB]:
   - delete T2's `var-nullable` row, so the 9 rows move to `selected`;
   - give `${…}` patterns their own listing token `no-variable`;
   - add §6.1's [PF-DROP] listing row (`no-size-cap`) in the same change: one
     listing-vocabulary event, one spec hunk.

   **Recommend YES**, as one row after B merges. The abi ruling is by grep at
   that row (§5.2).
2. **`--fast-or-fail`'s reach.** Keep it on the size-cap rows only, with the
   new `fof` column making the scope visible? **Recommend KEEP**:
   `--engine=dfa` and `-fprefilter` are the do-or-die levers for an overflow
   (§8.2).
4. **B7's listing scope.**
   - (a) `engine-route` order + `kind` flips for `engine-route`/`size-term`/
     `prefilter-lang` + the two desc fixes: taken (it is §4.6's fix).
   - (b) ALSO list T1 and T2 as two new `kind=list` axes (`fallback`,
     `prefilter-admit`), with rows, order, deny, `degrading`, `fof` and
     `on`: **recommend YES, in B7.** [LIST-TABLES] and D152 want every table
     listed, and the cost is stream-5 rows plus registry re-pins. The
     alternative is to file it under [LIST-TABLES].

Taken by the manager (recorded, not reopened):
3. `forcing`, `nomem` and the size-term trial catch as T1 rows 0-2: ROWS.
5. §4.1's fix scope: moved out of B into [DEC-COLLAPSE-WASTE] with both
   forms; its form is ruled there.
6. Row-pointer state vs value state: VALUES (§1.3).
7. The `-fprefilter` + `has_var` refusal stays OUTSIDE T2 (§7).
8. Panel: run (`../dev/reviews/2026-10-08-r-decfallback-panel.md`); this
   revision answers it.

---

## 12. The lenses (brief)

- **Specific vs general**: one ladder for every arrival label (row 0
  included), one admission table for both of today's derivations; F1 becomes
  a visible row instead of a ternary inside a predicate; the attribution
  walk's back step is a general rule, not a sequence special case.
- **Core vs derived**: the tables read E1 facts (`kinds`, `nullable`,
  `empty_admits`) and the fit; they derive no fact.
- **Applicable vs assumption-changing**: applicable; no token, attempt,
  stderr or listing byte moves through B6.
- **Fits the architecture vs refactor**: fits; it extends the existing
  `fit_rungs[]` and reuses A's trace, sweep, anchor tooling and listing
  projection.
- **Shared question / engine hat (D124)**: T1 is engine-scoped by its
  `applies` (rows 7-8 DFA, 3-4/6/9 VM), not by separate tables.
- **Forest for the trees**: §7; four siblings remain, three with a planned
  home, and T2 row 5 vs T3 row 3 is filed as its own row.
