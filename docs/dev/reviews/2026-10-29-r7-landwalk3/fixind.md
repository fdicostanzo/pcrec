# crit-landwalk3 / fixind — fix-induced lens on p1dsg3_report.md (rev 2)

Critic: fixind (opus), 2026-10-29. Subject: `docs/dev/lanes/p1dsg3_report.md` at cdb5717d9.
Code traced in the review tree `worktrees/crit-landwalk3` (main ffb9254cb). Read only. 3 pcrec
compiles (all `--emit-facts`, 14:11-14:13), no matcher runs, nothing after 19:00.
Probe dir: `/var/tmp/pcrec-pcrec/scratch/crit-landwalk3/fixind/` (subject copy, facts listings).

Disclosure: one `grep -rl` over `docs/` (looking for readers of `fit_seq_legal`) printed four
file NAMES under `docs/dev/lanes/`. I did not open them or read any of their content.

The question: for each change rev 2 makes for r5, does the added read, hand, row, field or check
newly break something, or leave it unproven? I traced each one in today's code, evaluating checks
by their condition.

## Findings

### FIX-1 — the LOWER relocate puts RECOVER on the walk's path, and RECOVER's hand is read off the walk row, which declares none
- **CONFIRMED by code trace** (no twin build). Severity **design**: an admitted compile would crash.
  Effort: small. Blast radius: every admitted walk compile (5b, qnt-plus, cls-s-ucp).
  Subject §A2 (the LOWER row of the hands table), §Size (`.applies`), Build plan step 4.
- Trace in today's code (emit_dfa.c):
  1. `cand_path_finish` (≈11903): a non-AT hand selecting a FIN_SEARCH row relocates. It visits
     the fallback's cells: composite DFA cells = NEXT | RECOVER.
  2. `cand_path_visit(RECOVER)` → `cand_path_row` → `dfa_search_start_of(cx)` (≈9708) =
     `dfa_search_start_at(cx, cand_locate_of(cx)->u.locate.recover)`. That is the hand of the
     SELECTED LOCATE row, here `landmark-walk`, not the hand of the relocated fallback (composite,
     `EXISTS`).
  3. Rev 2's row declares `.c.deny`, `.needs {ML|MA, 0, PRESENCE}`, `.whole` and `gives[]`, but no
     `.recover`. So the hand is 0, no RECOVER row takes 0, and the selection is NULL.
- Consequences:
  - The stamp rule asks RECOVER, because the path now asks it. Then `dfa_search_start_name`
    (≈9717) evaluates `dfa_search_start_of(cx)->tok`. That is a NULL dereference in release. In
    the trace build, `cand_hit_as` aborts first with `recover-no-hand`. `dfa_search_act` has the
    same problem.
  - Inside the quiet derivation, `p->recover = NULL`, so reverse-pass's `CAND_MR` never enters
    `p.needs`. §Size's member claim `{ML, MA, MF, MR} → {MA, MF, MR}` (the reason the rung needs
    no shrink test) is therefore false under today's derivation.
- Why it never shows today: `rev-end` (the only row with a relocate) visits RECOVER first through
  its own `.needs` cells, with its own `WINDOW` hand. `cover` and `empty` hand nothing that
  relocates.
- Fix:
  - Either the relocated cells are asked with the FALLBACK row's RECOVER hand: the closure names
    the row whose cells it visits, the general form of FINISH's per-hand keying.
  - Or the walk row declares `.recover = CAND_HAND_EXISTS` explicitly. `table-recover-not-total`
    then counts it as an EXISTS asker; reverse-pass takes EXISTS, so it passes. State which one,
    and correct §Size's member claim either way.
  - Rev 2's sibling-field audit (`fin` → `gives[]`) should cover `.recover`: it is the other
    hand-declaring field of `u.locate`.

### FIX-2 — L8's start set is a NEW kit ask by LOCATE, undeclared ("no new kit ask" is false)
- **CONFIRMED by code reading.** Severity **maintenance**: the trace build fails, or a check
  passes only because the label is wrong. Effort: small. Subject §The NEXT read cycle ("The memo
  also holds the start set NEXT_cf's row proves (`cand_row_scan`, as `req_start_set` reads it)"),
  §Checks row `table-read-unasked`/`table-ask-unread` ("no new kit ask … PASS").
- `cand_row_scan` (emit_dfa.c ≈8367) calls `cand_ask` → `mf_ask` for every PF_SCAN_BYTE or
  PF_SCAN_SET row: `memchr` (qnt-plus, cls-s-ucp) and `byte-class` (5b). So all three stage-1
  admitted rows make this ask.
  - The ask is made FOR LOCATE's L8, about NEXT's site. `cand_ask` runs `cand_ask_check(reader,
    NEXT, …)`, so in the trace build it traps `undeclared-ask` and `undeclared-ask-field`.
    `cand_nodes[LOCATE]` has no `kask`/`kfields`.
  - Or the build copies `req_start_set`'s hard-coded `reader = CAND_SLOT_NEXT`. Then it passes
    with a WRONG label: the trap checks the reader the checked code names, which is a control
    sharing a source with what it controls (learnings §3).
- Fix:
  - Declare `kask[CAND_SLOT_NEXT] = CAND_ON(CAND_ROUTE_DFA)` and `kfields = EXISTS | PROVEN0` on
    LOCATE. That is 5 fields, not 3. `table-ask-unread` then holds, because `reads[NEXT]` covers
    DFA.
  - Make the ask after the fill's NEXT selection has closed. The want is `F | NO_LW`, LOCATE's
    `under`, and `ask-while-open` would trap if that NEXT(F|NO_LW) frame were still open.
  - Correct the §Checks row and add an S1019-shaped sabotage.

### FIX-3 — the `drop-landmark-walk` rung's reader list misses the ladder's sequence table and its act
- **CONFIRMED by code reading.** Severity **maintenance**: a trace-build invariant fails on a
  reachable sequence. Effort: small. Subject §Size "Its readers move in the same commit, FOUND BY
  GREP", Build plan step 6.
- compile.c `fit_seq_legal[]` (≈1794) is §1.7's legal pairwise transitions. `fit_record` asserts
  them in the trace build (`pcrec_fit_invariant_fail("fit-sequence", …)`, ≈1866) for every
  ATTRIBUTING row, i.e. a row whose `esel` cell is not PASS.
  - A rescued artifact must stamp `size-cap-retry` (sabotage S238's rule), so the new rung
    attributes, as `drop-anchored` does.
  - Then a walk artifact still over the cap after the walk drop goes on to `drop-anchored` (its
    precondition stays true by design, SDR KEEP). That makes the sequence
    `{DROP_LANDMARK_WALK → DROP_ANCHORED}`, which is not listed, so `fit-sequence` fails.
    `→ DROP_PREMUL` is the same.
- Also unlisted:
  - the `FitAct` enum value, the recovery switch's retrying case list (≈2553) and the act text
    (≈1658);
  - `docs/design/dec_fallback.md` §1.7/§1.9 and `dec_fallback/row_reach.py`'s `SIZE` tuple;
  - the `engine-route` order-7 `--list-axes` desc on `prefilter-collapse`, which enumerates the
    PF-DROP rungs (observable text).
- Rev 2's shape leaves `.cells`, `.act`, `.retries`, `.repeat` and `.fof` unstated.
  `fit_tables_selfcheck` refuses only the enumerated-0 cells, so it would not catch the missing
  sequence pair. Fix: add the two pairs and the act, and name these readers.

### FIX-4 — deleting L0 `denied` (SLOT-6) takes the deny away from the compile-time ML gate
- **CONFIRMED by code reading** (rev 2's own text). Severity **size/compile-cost + listing**.
  Effort: small. Subject §Admission "Shape" ("Rev 1's L0 `denied` row is DELETED"), §Mechanism
  "Where and when it is built", §The NEXT read cycle ("the bit has exactly one selection reader").
- The deny now lives only on `.c.deny`, which only `cand_select` reads.
  - The ML gate does NOT go through `cand_select`. Rev 2: it "runs the walk row's PRE phase
    through `cand_applies`", and "the gate does not read LOCATE".
  - So under `-fno-landmark-walk`, and on every `drop-landmark-walk` retry (`defo.flags |=
    NO_LW`), the gate still runs rows 1-9. That includes row 8's memo fill (its CANDTRACE
    `lmwalk-cf` record and the facts `used` marks), and it BUILDS ML.
  - The rung exists to shed ML, but ML is rebuilt on the retry, unused: not a member, so not
    emitted.
- Precedents read their deny at the build gate: `rev-end`'s gate goes through `cand_locate_of`
  (deny honoured), and `build_anchored_dfa` reads `PCREC_NO_ANCHORED_DFA` itself.
- Fix: the gate tests the row's `.c.deny`, named as the bit's second reader (a build reader, not
  a selection reader, so the counterfactual argument is untouched). Or restore a PRE `denied`
  conjunct for the gate only.

### FIX-5 — the memo fill moves `--emit-facts` `used` on cover/rev-end artifacts (the no-mover claim compares to the wrong compile)
- **SUSPECTED.** Severity **listing (spec-visible)**. Effort: small. Subject §Checks row
  "`--emit-facts` used record … the same facts as the walk-off compile (the lemma: same NEXT
  row); no mover expected".
- The gate fills `NEXT_cf` on artifacts where `cover`/`rev-end` outrank the walk; rev 2 accepts
  this for the ML cost. On those artifacts the walk-off compile never selects NEXT
  (`RX_DFA_PREFILTER` is the absence value), so the lemma's "same NEXT row" has nothing to
  compare to.
- Witness, `c[ac]t` (bench cls-pair-ctl, LOCATE `cover`):
  - The PRE rows 1-7 pass by hand: DFA finisher; A built (cover needs it); L = `t` at position
    2; P = `c[ac]`; one branch; `t` ∉ {c, a}.
  - Its listing has `run_pin`, `req_landmark_maxoff`, `width`, `end_window`, `req_set` and
    `req_whole_run` at `used no`. With NEXT on the path (`--memfn=no-window-search`) they read
    `yes` (`fixind/facts_cact*.txt`, 3 compiles).
  - Which of them NEXT's own rows read (rather than the pre-check builder) needs the trace build
    of the design. `run_pin` is the likely one (`us_run_pin`, read by `run-pinned*`, the first
    NEXT rows).
- Confirm: the build's listing of `c[ac]t`, diffed against today's.
- Precedent: `req_pres_proof_quiet` saves and restores `pf.used` for exactly this reason, and
  facts_listing.md §4.1¶2 explicitly exempts cover's admission read.
- Fix: the fill restores `pf.used`, or a facts_listing.md hunk says the walk's counterfactual
  read sets `used`.

### FIX-6 — `asker` with a trap on 0 does not cover RECOVER's asks
- **CONFIRMED by code reading.** Severity **maintenance**. Effort: small. Subject §A2 "The asker".
- `cand_takes` runs for every HANDED slot (`CAND_HANDED_SLOTS` = FINISH | RECOVER, ≈10729).
  RECOVER's asks map onto none of BODY/CALLER/SEED cleanly:
  - `dfa_search_start_at` (≈9693) sets no `.point`, so it would get asker 0 and trip the new trap
    on every RECOVER selection;
  - RECOVER's totality check sets `.point = true` (≈11450), which would read as CALLER, but its
    asker is a LOCATE row's walk.
- Neither site is among rev 2's "three emitter asks". RECOVER's `WINDOW` is numerically
  `CAND_HAND_AT`, so the asker test must stay gated on `slot == FINISH`.
- Fix: scope the trap and `at_askers` to FINISH and say so, or give RECOVER's two sites BODY.
  The explicit `.point` sites number 7 plus `cand_path_finish`'s parameter and its 5 calls, so
  "about 17" holds only if the implicit RECOVER initializers are counted.

### FIX-7 — `fin` has test-tree readers: two sabotages carry its spelling
- **CONFIRMED.** Severity **maintenance**. Effort: trivial. Subject §A2 ("`fin`'s one reader is
  `cand_locate_hands` (grep: 3 lines)").
- `tests/mech/sabotages/S770_empty_after_revend.sh` and `S738_locate_order_swapped.sh` match
  `.fin = CT_VERDICT`, `.fin = CT_START | CT_VERDICT | CT_ENDSET` and `.fin = CT_START` in their
  SAB_BEFORE/SAB_AFTER text. After `gives[]` replaces `fin`, both plants stop applying, so mech
  needs a re-aim in the same commit.
- `tools/review/out/literal_census.tsv` also lists it (a generated artifact).

### FIX-8 — `gives[]` has no route; the rank check's VM skip is still load-bearing
- **CONFIRMED by code reading.** Severity **doc**. Effort: trivial. Subject §Checks
  `table-progress-rank`.
- `gives[]` is route-independent (`composite` {SPAN}). On CAND_ROUTE_VM, composite's FINISH hand
  is the PROJECTED one: `cand_vm_search_hand` gives LOWER with no DFA body or on a superset body.
  `search-from` VM takes LOWER and ENDSET.
  - With the `rt == CAND_ROUTE_VM` skip removed, the amended check would pass VM by an operand
    that does not describe VM. Today's operand fires there (`CT_LOWER & ~CT_LOWER == 0`).
  - The skip is semantically required: VM `search-from` IS the search entry, not a relocate.
- Rev 2 does not say the skip stays. It must, and the VM totality list stays hand-coded for the
  same reason.

## PROBED-AND-HELD

- **`table-read-cycle`, re-run by hand** on the amended `cand_nodes[]`. The edges, with `under`
  and `by`:
  - LOCATE→NEXT (LW, LW);
  - PRESENCE→{BOUND, NEXT (RH, –), LOCATE};
  - FIRST→{PRESENCE, BOUND, LOCATE, RECOVER, FINISH};
  - NEXT→{BOUND, FIRST (–, RH), NEXT (RH, RH)};
  - RETRY→{BOUND, NEXT};
  - RECOVER→{NEXT (RH, –), LOCATE}.

  From all 12 roots no (slot, mask) state repeats: the deepest chain is NEXT(0)→FIRST(0)→
  LOCATE(0)→NEXT(LW)→FIRST(LW)→LOCATE(LW), then stopped. **Passes.** Both controls hold: without
  `by`, (NEXT, LW) repeats; without `under`, (LOCATE, 0) repeats.
- **`table-read-unasked`:** `reads[NEXT]` = DFA ⊆ NEXT `.asks` (all routes). **`undeclared-read`:**
  the fill's top NEXT selection sits under the LOCATE frame (declared). The nested FIRST,
  PRESENCE, LOCATE, RECOVER and FINISH edges are all declared today. The fill must not use
  `cand_select_quiet`, which sets the stack aside; rev 2 says it stays on the stack.
- **`ask-while-open`:** enumerated the stack states for the live chain plus one fill, across
  NEXT(F), NEXT(F|RH), NEXT(F|LW) and NEXT(F|LW|RH). No kit ask's want equals an open frame.
- **`table-progress-rank`, every route, today and amended:**
  - Today: DFA {AT exempt, ENDSET passes}; ATTEMPT {AT}; VM skipped.
  - Amended: the same 0 verdict moves, and the new DFA LOWER cell passes.
  - The amendment RESTORES the check's power. The planted SPAN control fires only under the new
    operand: with today's operand, `CT_START & ~CT_LOWER ≠ 0` passes it.
  - The premise control (`at_askers ∋ SEED` on search-from) fires. Totality stays green under
    that plant.
- **`table-finish-not-total` lists rebuilt from the LOCATE rows' routes:**
  - DFA: empty{NOMATCH}, rev-end{SPAN, NOMATCH, ENDSET}, cover{SPAN, NOMATCH}, composite{SPAN},
    plus the caller {AT, NOMATCH}. That equals today's list.
  - ATTEMPT: empty and composite (rev-end and cover are CR_DFA only), plus the caller. That
    equals {AT, NOMATCH, SPAN}.
  - Walk cells: (DFA, AT/SEED) → verify-at, `finish_available`, MA ⊆ the walk's needs;
    (DFA, LOWER) → search-from. Both pass. S741 (search-from before verify-at) still fires on
    the CALLER AT.
- **`table-progress-cycle`:** `FINISH.raise |= LOCATE` moves nothing, because FINISH→LOCATE is
  already out of `fwd` through `rank` and `entry`. No check reads a `raise` claim, so the
  declaration is not load-bearing (fine, but unproven).
- **The memo key against compile order:**
  - Scan-edge runs on `dfa` before A is built, and `tagged` swaps `dfa.st`/`dfa.n` (keyed).
  - Any LOCATE read made before A exists declines at row 2, before row 8.
  - `pcrec_cand_drop_anchored_shrinks` toggles `anchored_ok`, so row 2 declines and the memo is
    left untouched.
  - LOCATE is only ever selected under the compile's own flags (or F|LW inside the fill, where
    the walk is denied), so a flags-free key is safe. The facts hook's `hopt` differs only in
    `prefix`.
- **Retry staleness:** `Ctx`/`Job` are per attempt (`job_cleanup`), so the memo cannot cross a
  retry. The retry's `defo.flags` carries NO_LW, so `.c.deny` skips the walk (FIX-4 aside).
- **The options-copy toggle:** `pcrec_memfn_policy` reads only the SIMD axis, and
  `pcrec_memfn_denies` maps only `PCREC_NO_RUN_OVERLAP`, so an `mf_art_begin` inside a fill is
  the same art. `pcrec_cover` is options-free apart from the `prefix` pointer, which the copy
  shares.
  - Caveat (held, low): a `longjmp` out of a fill leaves `cx.opt` pointing at the copy. The
    reachable arrivals (nomem propagate, OTHER refuse) end the attempt without reading `cx.opt`.
    The force loop resumes the attempt, but it runs no selection. Keep the copy where a longjmp
    cannot strand a dead pointer (Job or arena), or reset `cx.opt` at the recovery point.
- **Ladder arithmetic:**
  - `fit_attempt_bound()` = 1 + Σretries + (1+restarts)(N+1) + lever. One retrying,
    non-restarting row adds +1, matching the hand formula's +1.
  - SDR KEEP keeps `drop-anchored`'s `SDR_NONE` precondition, and the dominance order is
    consistent.
  - `.applies` reads LOCATE at the recovery point before `job_cleanup`, so the memo is still
    valid.
- **`.needs ∋ MA`:** `build_anchored_dfa` reads FINISH rows' needs only
  (`pcrec_cand_finish_needs`), so no build moves. Members do not move either: verify-at's closure
  already adds MA.
- **`path-needs-unbuilt` sabotage reach:** with `anchored-A` dropped and `-fno-anchored-dfa`, the
  quiet derivation swallows the NULL seed-AT selection (`if (!r) return`). Its end check fires on
  MA ∉ built at the first `cand_path_of`. If the walk's emitter asks FINISH(SEED) first, it aborts
  with `no-row` instead. Either way the plant is DETECTED; name the oracle loosely in the
  sabotage row.
- **`dfa_search_calls_match` over `gives[]`:** a no-mover today, since only rev-end's ENDSET can
  select a CAND_FIN_VERIFY row.

## Standing questions

- **Sibling (third member).** The NEXT_cf options copy is the THIRD "evaluate the selection in an
  edited world by mutating shared context, then restore" site:
  1. `pcrec_cand_drop_anchored_shrinks` (toggles `Job.anchored_ok`);
  2. the facts hook (`cx.opt = &hopt`, compile.c ≈3506);
  3. NEXT_cf (`cx->opt` → a copy).

  `pcrec_cover` + NEXT_cf are two per-Job key-checked memos (a third would earn a shared helper).
  FIX-1 is a further sibling of "a field read off the SELECTED row for a cell visited on another
  row's behalf".
- **General form and unlocks.** An explicit selection WORLD (deny bits plus Job overrides) passed
  down `cand_select`/`cand_read` instead of mutated `Ctx` state.
  - It is reentrant and longjmp-safe.
  - It lets `under` propagate as the static walk already assumes (U-a's general form, without a
    memo).
  - The ladder's shrink test and `.applies`, the memo and the facts hook become one mechanism.
  - Trigger: the next counterfactual reader (stage 2's VM walk, or a second `under` read that
    sits more than one level down), or the next toggle site.
  - For FIX-1, the general form is the path closure keyed by the row whose cells it visits.
    Trigger: now, the walk's relocate.
