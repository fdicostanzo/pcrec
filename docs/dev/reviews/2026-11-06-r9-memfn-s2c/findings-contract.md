# findings — contract — memfn-s2c

Method: I wrote `contract/spec.py` from the measures.md §3.4-§3.5 TEXT (I had read only est.py's file readers
first), and `contract/j1fuzz.py`'s rule from span_cards.md §3.6. `contract/gen.py` builds synthetic RUNDIRs
(cells.J*.tsv + run_record.tsv) from plan.py's rows. `contract/cmp.py` diffs est.compute against spec.compute
row by row (value, noise, null, absent and its cause), drift by job, and the outcome with its causes.
Scripts: fuzz.py, fuzz2.py, targ.py, drilltab.py.

## Findings

### CONTRACT-1: the spec says the recompute reads "the set file and the run record, and nothing else", but three of its own rules need producer text that is in neither
- **CONFIRMED** (by text). Severity: doc/design (Goal 3 and M3). Effort: S (spec wording) to M (make the facts data). Blast radius: M3 and S2e's recompute author.
- `measures.md` §3.4¶1 says a checker reads the set file and the run record and nothing else. Three rules contradict that:
  (a) §3.4¶6: "the fifth field equals the base the row's quantity declares by the base rule of the set's
  `method` ... A set whose `method` the recompute holds no base rule for is refused." kit-grid@3's base rule
  (find_hit.<form> -> base.<form>, verify_cmp.<form>.<cls> -> base.null.<cls>, enter.<k>.<e> -> base.fail.<k>.<e>)
  is stated only in span_cards.md §3.4. It is not in the spec, the card rows, the cards CLAUDE.md or the record.
  (b) §3.5¶8 and ¶11: a floor clause's `when` is "a condition token the producer defines". The meaning of `unless-j1-b`
  ("j1_verdict is b") is in span_cards.md §3.5 only, so a generic recompute cannot tell which clauses are ACTIVE.
  That means it cannot compute outcome rows 2-4.
  (c) §3.5¶10: "any verdict the record states that its producer derives from cells the record holds, RE-DERIVED".
  J1's rule (m 0.5, k 5) is in span_cards.md §3.6 only.
- An implementer working from the spec alone, as the design intends for M3, cannot compute the base check, the floor
  or the outcome. Design §3.8 step 4 does point S2e at §3.6, so S2e is covered; M3 and the spec's own sentence are not.
- Fix options:
  - Make §3.4¶1 name the producer-defined rules as a third input, and have the record's `run` section name where they live.
  - Or turn the facts into data. A `when` of the form `unless:<run-key>=<value>` (`unless:j1_verdict=b`) is generic and
    needs no producer knowledge. A base column in the card, or a record `bases` section, would carry the base rule.
  - Unlock: the generic `when` form lets any later producer declare a conditional floor with no spec change.

### CONTRACT-2: the slot's estimator does not read the record or the cell ids the spec makes authoritative, and its halving differs from the spec's for an odd gate
- **CONFIRMED** (plants in `contract/targ.py`). Severity: maintenance. On today's inputs it is latent; if it ever fires it is
  an answer-level disagreement that only S2e's recompute finds, after the window is spent. Effort: S. Blast radius: est.py's `compute`.
- Where est.py takes its inputs:
  - the row list, floor, bases, events, lengths, L and gate: from `plan.build()` and plan.py constants. It does not use
    the record's `plan`/`floor`/`jobs` sections (`read_record` parses only `run` and `jobs`, and `compute` uses
    neither for "ran"), the cells' fifth id field, the cards' `lengths`/`launches`/`gate_e6`, or the ctl cells' own lengths.
  - whether a job ran: from whether its cells file exists (`ran = {jobs with cells}`, est.py:90).
  - Spec §3.5¶10 takes the record's `jobs` as the given input and cross-checks it against the cells.
- Divergences found:
  - Record says J4 `never-ran` but cells.J4.tsv exists: est prices all 14 verify rows and returns FULL 0. The spec gives
    ABSENT never-ran:J4, and a real ¶10 recompute refuses the set.
  - Record says J5 `ran` but there are no cells: est returns REFUSED on the enter floor. The spec refuses the recompute.
  - The libc hit cells name `base.walk` in their fifth field: est still subtracts `base.libc` (from plan.py), and 4 rows
    differ from the spec's reading. Under ¶6 the set is refused.
  - A cell id whose launch differs from its `launch` column: est returns FULL. The spec refuses (¶6).
- Today run.py and est.py share plan.py at one commit, so these need a job killed between writing its cells and
  ending green, a hand-edited record, or a plan change between the window and the draft.
- Gate halving: est uses `plan.GATE_E6 // 2` (est.py:131, :143, :151; run.py `screen`). The spec says
  `2 x noise x 10^6 <= G x value`, `2(s_k - s_(k-1)) > G` and `2 x drift > G`. These are equal only for an even G.
  Counterexample: G 30001, value 2,000,000, noise 30001: est fails the unit's half gate, the spec passes it (computed).
  Latent: every kit-grid@3 gate is 30000.
- Fix: `compute` reads the record's plan/floor/jobs, the base from the fifth field (asserting it equals plan.py's), and
  L/gate/lengths from the cards. Use the spec's doubled comparisons. Cross-check jobs against cell presence and refuse
  on a mismatch. These changes also serve Goal 4: one home for each card fact.

### CONTRACT-3: §2.1's `partial` still has the format-1 meaning; the S2c hunk did not amend it
- **CONFIRMED** (by text). Severity: doc (D80, caller-visible header). Effort: XS. Blast radius: measures.md §2.1.
- `measures.md:67` still says "`1` when only some groups passed their gates". In format 2, `partial 1` means some planned key
  is absent: its job never ran, was drift-refused, or its cost row failed alone (§3.5¶12 row 3, where rows, not
  groups, pass gates). In practice the case is a J1 (b) run whose J2p never ran, and no gate failed in it at all.
- Fix: one clause in §2.1 pointing at §3.5¶12 for format 2.

### CONTRACT-4: smaller gaps in the spec text that two independent implementations could resolve differently
- **CONFIRMED** (by text and computation). Severity: doc. Effort: S. Blast radius: measures.md §3.4-§3.5.
  (a) **L = 7 is assumed but not stated.** L is "the card's launches" (§3.4¶2) and the bimodal range is "2 .. L-2", but
  §3.5¶3 says "the SIX launches". K_TRIM_E6 is "the factor ... a seven-launch trim removes" and K_MED_E6 is "seven
  normal launches". A card with L != 7 would get the wrong constants silently. Fix: state "every format-2 card has
  launches 7; another value refuses the recompute", or write the constants per L. (est.py and j1_rule.py also
  hardcode 7 via range(2, 6) and plan.L_LAUNCHES.)
  (b) **An absent unit row is not covered.** If the unit's job never ran, the unit row is absent and W is undefined.
  Table row 1 says "the unit row fails (¶5)", which ¶5 defines only as gate or bimodal. est and my implementation both
  return REFUSED `unit`; another implementer could crash or read row 2.
  (c) **W <= 0.** The unit's value is exactly 10^6 by construction (rhafz(W x 10^6, W)), so its "value_e6 > 0" check is
  vacuous. W < 0 flips every other row's sign, and W = 0 divides by zero. An `events` of 0 on a delta arm also
  divides by zero. Fix: the spec should say med(v) of the unit must be > 0 and E > 0 on an arm, else the recompute refuses.
  (d) **§3.4¶14's parenthetical** "(a `ratio` row: x 10^6; a `walkbytes` row: unit bytes x 10^6)" reads as two scalings.
  It is one formula with two unit names.
  (e) **The null row's `abs_ns_e6`** is unspecified. est writes med(abs_l). It is provenance and not digested, so this is harmless.

### CONTRACT-5: run-record step 2 (finalize) can hang behind boxqueue's `after`, and finalize's state vocabulary is not boxqueue's (S2d hand-on)
- **SUSPECTED.** It needs S2d's job scripts, which are not in S2c. Severity: design. Effort: S. Blast radius: the window's last step.
- **The hang.** Design §3.5 says J9's `--ready` answers 0 once no job is pending or running, "whatever each ended as".
  But `scripts/boxqueue` `cmd_after` answers 75 ("waiting") forever for a FAILED upstream. So when J1, J2 or J3 fails,
  its `after` dependents stay pending and J9 never becomes ready until someone cancels by hand.
- **The cascade.** span_cards §9 S2d says "J3-J5 chained `after`". If J3 chains after J2p, then J2p's own 77 under (b)
  (`cancelled`) makes `after J2p` answer 77 and cancels J3-J5. That turns the designed PARTIAL into REFUSED.
- **The vocabulary.** record.py `finalize` reads STATES in green/failed/wait-timeout/never. boxqueue's states are
  green/pending/running/failed/cancelled. `cancelled` maps to cause `failed`, and J2p `never` maps to
  `declined-j1b` whatever the real cause was.
- **Missing keys.** `set` and `run_id` are written only by the J1 step, so a run whose J1 failed has a record without
  the `run_id` that §3.5¶8 and ¶9 require.
- **Effect on the verdict.** The causes are not read by the outcome table (it uses `never-ran:J<j>`), so only the
  hang and the cascade could move a verdict.
- Fix (S2d): chain J3-J5 after J2 or J1, not J2p. Have J9's ready also treat a failed job's pending dependents as ended,
  or cancel them. Make finalize write `set`/`run_id` itself and map boxqueue's states explicitly.

### CONTRACT-6: the draft writer leaves header provenance empty and writes even when the outcome is REFUSED
- **CONFIRMED** (by reading). Severity: doc (low). Effort: XS. Blast radius: S2d's report and S2e's step 2.
- **Empty provenance.** `write_draft` fills `isa`, `box` and `libc` from record `run` keys that record.py never writes, so
  they are empty (legal: not R keys, §2.1). `box` is a `--list-measurements` column.
- **Written on REFUSED.** The draft is written for a REFUSED outcome too (exit 3). §3.5¶13 says "a REFUSED run writes no
  set". The draft is not the set, but S2d's "names the draft's path and sha" step must gate on the exit code.
- **Form hashes.** `form_hash` reads the CURRENT `build/arm_fixtures --hash` at draft time, not the hash link.py checked
  at link time. That is the same thing only when the draft runs at the window's frozen commit.

## PROBED-AND-HELD
- **Estimator and gates (§3.4-§3.5), random fuzz.** 400 + 400 synthetic runs, every job and row family, noise 0.03-5 %,
  A/A 0.02-2 %, per-job control drift 0-3 %, per-row delta costs including 0 and negative, j1 verdict a/b/c, random
  never-ran jobs. **Zero diffs** between est.py and my spec implementation. Agreement covered:
  - every row's value_e6, noise_e6, null and absent cause (about 6,900 priced values and 5,000 nulls)
  - drift_j and its verdict per job
  - the outcome and its causes: FULL, PARTIAL (the J1 (b) case, exactly the 9 pair keys) and REFUSED (unit, and
    about 15 floor-clause combinations)
- **Targeted cases** (the design's predicted outcome first, then adversarial):
  - clean: FULL in both
  - J1 (b) with J2p never-ran: PARTIAL with the 9 pair keys, `partial 1`
  - one base launch missing: both fail loudly (est KeyError)
  - zero per-event verify and negative enter.3: null, and REFUSED on floor:enter.3 and floor:verify.*, in both
- **Design §3.5's constructed table, through est's own functions, reproduced exactly:**
  - clean: 60000/92; one outlier: 60000/92; bimodal non-unit row: noise 2034
  - A/A 1 %: 604; A/A 3.3 %: 2001
  - signs mixed: -500 survives the trim
  - drift inside a wide spread: 2.0 % < 2.28 %; tight 3 %: refused
- **Arithmetic and boundaries:**
  - rhafz, isqrt_rn, lower median, and the trim tie (later launch) match the text
  - half gate, bimodal (2 x gap > G) and drift (2d > G AND d > 3 s.e., versus design's max(G/2, ...)) are equal for even G
  - NULL boundary med(D) == aa_D is null in both (strict >)
- **J1 rule (§3.6, m 0.5, k 5).** My implementation from the text against j1_rule.verdict on 3000 random 8-cell sweeps
  (b 2092, c 548, a 360): zero diffs in verdict and widths.
- **Goal 2's floor.** plan.py's 18 clauses match §1 Goal 2 and §3.5 exactly: byte.<form> per find_byte key; hit.<form>
  over the random keys; verify.<form>.<cls> over p0/p50 for every vcls pair; enter.<kind> over NONE for every census
  kind; `unless-j1-b` exactly on J2p's lines.
- **Cells.** run.py's cell ids follow §3.4¶5's grammar: the fifth field on arm and twin, none on bases or ctl; events `-` on
  slope arms and ctl, 0 on bases. plan.py's bases follow the design's family rule. The draft keeps refused jobs' and
  gate-failed rows' cells, and J1's cells go to the record, not the set.
- **Run record.** It has the five sections and columns of §3.5¶8 and the table. The draft's header `run` is
  `<id> record:<sha>`.
- **Amendments elsewhere.** measure_sets.md and span_pick.md [s2] hunks: consistent with the spec, including §7.4's
  format-2 exception and the "read cell" amendment.
- **D174/D80 naming.** No caller-visible name in the new spec text uses kit, memfn or proof vocabulary. The new tokens
  (`slope`, `delta`, `twin-per-arm`, `bimodal-test`, `null`, REFUSED/PARTIAL/FULL) name behaviour.
- **Goals in rank order.** Goal 2's floor is exact. Goal 3's kept data (all J2-J5 cells; record with j1_cells, plan,
  floor, jobs, transcript sha) is sufficient once the producer rules of CONTRACT-1 are reachable. Goal 4: est duplicates
  card facts in plan.py (CONTRACT-2).
- **Not run:** no slot dry runs (the contract lens did not need them), no compiles.
