# covs2e report — [COVER-CAP] stage 2 design addendum, cover_cap.md rev 5.1 (review r13 fixes)

## STATE AT HANDOFF

STATE: done. Design only; no code, no spec, no plan or decisions edit.
- Branch `lane/covs2e` (cut from lane/covs2d). `docs/design/cover_cap.md` is REV 5.1, committed
  (342ae6586, then this report's commit). Edited: that file and this report only.
- Rulings file `docs/dev/lanes/covs2e_rulings.md`: EMPTY AT EVERY READ (start, before each commit,
  before this report). No R-n applied. The owner's route-versus-stretch answer had not arrived;
  rev 5.1 writes the manager's LEAN, marked "LEAN, OWNER QUESTION OPEN" everywhere it is stated
  (header R5 note, §0 G4 note, §1 table, §8, §11.2) and asks it as §9 Q7.
- Premise test: held (r13 has "DISPOSITIONS RULED"; rev 5 with §11 on the branch; main resolves to
  469d4205c; 4c8cf3c38 is an ancestor of main).
- Code cites: verified at main 469d4205c. `git diff --stat b9b9e8635 main -- src lib cli memfn
  tests` prints nothing, so every r13 file:line cite held; I re-read each one rev 5.1 uses
  (known.c, known.h, memfn_sites.c, memfn.h, emit_dfa.c, emit_vm.c, compound.c, limits_dump.c,
  limits.def, limits.h, cli/main.c, compile.c, cases.tsv, run_cover.sh, S3223, the two reference
  builds). No cite moved in substance; the STOP RULE fired on no item. Corrected while verifying:
  the kitproof floors at main are verdict 48 / facts 19 / answer 105 (`run_cover.sh:141-143`), not
  §5.3's rev-4 numbers (noted in §5.3 and §11.6.2).
- TODAY NUMBERS added by rev 5.1, each with its command, on main built in scratch (`git archive
  main | tar -x -C $PCREC_TMPDIR/scratch/covs2e/main`, `nice make -j2 build/pcrec`, rc 0; 2
  compiles + 2 gcc, inside the evening-hold allowance): `$P -p rx --features all -o hexN.c
  --pattern '[0-9a-f]{N}'`, `gcc -O2 -std=gnu11 -c hexN.c`, `size -A` `.text`: N=24 1,752 B,
  N=32 1,960 B (+208); emitted C 17,710 -> 18,918 B (~151 B per position). This REPRODUCES rev 5's
  absolutes; r13 PREMISE-4's 2,695 -> 2,903 came from another emit command; the delta agrees (F30).
- Validation (in the worktree): `make test-spec-history` GREEN (11 passed, 0 failed).
  `make test-plan-lint` RED, 1 check failed, by TWO PRE-EXISTING PL14 hits in files this lane did
  not touch: `docs/dev/lanes/covs2d_report.md` (its STATE paragraph quotes an older PL14 message
  that itself spells a plan line cite) and `docs/dev/lanes/land1115c_report.md` (already respelled
  on main by ab81b2e31). The same target on main's tree (scratch archive) is GREEN (0 failed). The
  manager or landing lane must respell covs2d_report.md's quoted message before this branch
  reaches main, or PL14 goes red there. The pre-commit spec-rules hook passed (52 checks) after I
  respelled cites of the two NOT-YET-EXISTING spec sections as "section 3.12 (new)" / "section
  2.56 (new)" (a `§` cite of a missing number fails the dangling-cite check).
- OWED: none.

## FINDINGS FIXED

Every FIX-NOW as DISPOSITIONS RULED words it, plus the DOC/PLAN items. "§" = cover_cap.md rev 5.1.

| finding | what rev 5.1 does | where |
|---|---|---|
| F1 | proof comparison over the reply's WHOLE counted range; all ones for every offset past `k` (context aside); a range ending before offset `k` is a named internal error; rev 5's `[MF_PROOF_LO, k+1)` struck; a plant of the OPPOSITE error (P3 cut to k+1 + P4 kit text over-tests k+1; witness `answer a{5}` subject `aaaaa`; control P4 alone declines C14) | §11.1 B5; §11.6.3 row 5; §11.5 FACT (proof); §8 |
| F2 | pcrec's own span writers listed (`memfn_sites.c:544, 548, 553-554, 557-568`): width type holds 4095, `j` bounded before the write; reader method gains "grep the writers of `mf_wspan` fields" | §11.1 readers, B1 |
| F3 | the seam is THREE bounds (positions >= ceiling-1, reach >= ceiling, proof forward >= ceiling); the assertion and the ask cover all three; `window_bounds_check` gets item B4 | §11.1 seam bullet, B2, B4; §11.5 FACT + ASK (1); §3.5; §8 |
| F4 | §11.1 split into A (before the reply: MkEnd pointer + uint16 k, the row/refusal/registry, the option, the rename, the kitproof loader letter, prediction tooling, two default-arm sabotage rows) and B (on the named combined branch: B1-B7) | §11.1 items; §11.6.1 |
| F5 | `MF_MAX_TERM` readers (`emit_vm.c:234`, `memfn_sites.c:630, 948`, `memfn.h:658`) and by-value `mf_class` (8 stack places + CandAsked, PcrecCover, mf_result; 131,328 B per class at 4,104 offsets vs the 442,368 B stack budget) listed; §11.5 gains both as FACTS and asks whether the coupling stays | §11.1 readers, B6; §11.5 FACT (hold), FACT (coupling), ASK (2) |
| F6 | rename readers listed with the two compared VALUES' new values (`cases.tsv:65` `width-limit|41|41|...`, `:72` `width-limit|4095|4095|...`), S3220/S3223 REACH-WHY, notes, known.c 349/439/455, kit_proof.md:239, `facts_listing.md` §4.5¶2; predict.py's home named (`docs/dev/lanes/covs1_evidence/predict.py`, read in place) | §11.2 readers; §11.1 A6 |
| F7 | kitproof FLAGS letter `W` (`--window-search-width=<ceiling-1>`); which row KIND carries each witness (the why by `facts` rows); §5.3's stage-2 verdict sentence fixed; floors' stage-2 deltas stated | §11.6.2; §5.3 |
| F8 | the proof-range plant's pair NARROWS (offset 36 of `[0-9a-f]{40}`, digits dropped); witness an `answer` row on `W` with a digit at 36; P2 alone recorded as the control (declines C14) | §11.6.3 row 4 |
| F9 | S3223 IS the bypass row (re-described, REACH-WHY re-pinned); NEW row "seam assertion removed/inverted", witness a one-TU reference compile with `-DPCREC_ANCHORED_MAX_STATES=<kit bound + 2>` that must FAIL, checked by its message; host `run_anchored_match.sh` new §4c | §11.6.3 rows 1, 3 |
| F10 | mech rows copying rewritten code listed (S1131, S1148, S1144/S1135) with the grep that finds them | §11.1 readers; §11.6.3 tail |
| F11 | compile cost a RECORDED measurement (pcrec CPU/RSS, emitted C bytes vs the 1,000,000 cap and 250,000 warning, gcc time/RSS/.text) with one criterion (a legal width whose compile fails is a kit finding, filed); `req_run_in_cover`'s cost corrected to O(k + len^2 x 256) | §11.1 answer identity |
| F12 | resolved by the option: a `pcrec_options` field is copied into every compound part (`compound.c` `part_compile`: `o = *parent`); one trace compile confirms | §11.1 answer identity; §11.2.1 |
| F13 | at-default/past-default witnesses DERIVED from the shipped default (`@D`/`@D1` substitution; `width=N` verdict values), so nothing re-points when the default moves | §11.6.2; §11.6.1 (6); §11.7 Q3 |
| F14 | the two lowered-ceiling reference builds (`run_anchored_match.sh:423`, `run_b3_checks.sh:303`) also pass `-DPCREC_DEFAULT_WINDOW_SEARCH_WIDTH=` 5 / 2; listed as readers; the grep for others named | §11.2 legal range; §11.1 readers |
| F15 | B's axes named (scan, start, prefilter, req why/handoff, forward DFA, kit site; 21,993 vs 32,965 C bytes): the intended route A/B, not one variable | §11.4 B |
| F16 | plan of record: time on the combined branch, land ONCE with the measured default; fallback 32 + a second abi event (manager's choice); synthetic long cells `[0-9a-f]{64}`, `a{500}` added | §11.6.1; §11.4 B; §11.1 abi |
| F17 | the rule can land at any counted width, below 32 included (24 twins added; the 31 scenario stated); the EMPTY outcome stated (owner's call, interim 32); rev 5's "24 or below" corrected | §11.2 default rule; §11.4 B |
| F18 | both build-time checks are `_Static_assert` (the ceiling is an enum at the default) | §11.1 B2; §11.2 legal range |
| F19 | outcome table rewritten FIRST MATCH: validity rows first, a row per previously uncovered case, agrees with the rule (a not-warm loss is a slower cell like any other); interim default named (32) | §11.4 table |
| F20 | unit (bench time; instructions reported, not ruled on), launches (>= 5, median), floor (max A/A deviation), slower, outlier, bimodal, a missing cell voids; bench field names a relay question | §11.4 procedure |
| F21 | the per-compile VALUED option designed (§11.2.1; see THE VALUED OPTION); §11.5's two untrue facts corrected; the test-only lever DROPPED (the option serves every check) | §11.2.1; §11.5 FACT (population); §4.5; §11.6.4 |
| F22 | the dial is live (`tuning.md` §5, §5.4 knee cells, §1¶9); the width a candidate §5.4 row once measured; "always inline" a dial cell, not a `--memfn=` value | §11.3; §11.7 unlocks 1-2 |
| F23 | every stale sentence: title, header R5 ("No new constant" now stage 1, note), G4 (+ LEAN note with the cliff example), G6's Q4 -> Q5, §1 table row, §3.1 bound heading, §3.5, §3.6 Q3, §4.2 (superseded; "C15 retires" called wrong), §4.3 note, §4.5 stage 2, §8 (two bullets), §9 Q1/Q2 (answers recorded), §9 Q7 (the owner question); D198 addendum TEXT below | as listed; OPEN QUESTIONS |
| F24 | §11.3 states the owner's amendment of D198 (e) for this request; the D198 addendum text and the dated [EARNED-SKIP] note text below | §11.3; §11.5 OWNER DIRECTION; below |
| F25 | the record quoted VERBATIM (journal session 132 afternoon entry; labelled as the manager's record of the owner's ruling, since it is not his own words); "a class-only width" moved off the NOT-list to §9 Q8, asked only if near-miss cells lose, leaning stated | §11.2 EMITTED-2; §9 Q8; §11.6.4 |
| F26 | unit `positions`; name `WINDOW_SEARCH` (the shipped caller word): the manager's spelling call, my pick stated with reasons (not `max_*`: those option fields are raise-only) | §11.2 Where, Name |
| F27 | [SIZE-KNEE] family named, a PLAN line for main, general form, unlocks (1)-(4) with triggers | §11.7 Q4 |
| F28 | `--list-limits` shows the shipped literal; a `-D` build is the builder's own record | §11.2 Where |
| F29 | `limits.md` new section 3.12 "The window search's width", anchor `3.12`, caller-facing | §11.2 Where; §11.2.1 spec row |
| F30 | the `.text` delta quoted with its command (absolutes reproduced at main; r13's other pair explained) | §11.3; §11.5 FACT (cost) |
| F31 | PREMISE: "no row bounds the cover ROUTE's width; the stretch is bounded by `limits.def:186`" | §11 PREMISE |
| MEASURE-6 | §11.4 A "as a BUNDLE" (95 commits; the A/A cell on the same two binaries) | §11.4 A |
| MEASURE-8 Q1 | unit named (time ruled; instructions reported) | §11.4 procedure |
| MEASURE-4 | REJECTED by the round; its residual point kept: a cell counts only if its artifact takes the cover | §11.2 rule; §11.4 row 3 |

### D198 addendum TEXT (draft for the manager to number and file; F23, F24)

> **D198 addendum (2026-11-15, the owner's stage-2 words and the reading taken).** Verbatim,
> journal session 132: 14:10 "1. reading dfa for the span is fine. In my goal of partial span
> proofs that means either rebuilding the dfa on the remainder or editing out the proven span
> states. 2. set in limits. If it's a user setting it could be shorter then adjusted by the user
> per artifact. 3. explain."; 14:35 "2. stage 2 is fine. 3. we have a performance dial for
> pcrec. it could include some options for the kit. Also, I would default to sub span loops
> (excepting the measured head inline ) then measure if inline was faster than the other way
> around. Measure three: all inline, all loops, header inline then loops. Then the speed dial
> option can be always inline should it prove that is faster"; 15:00 "I predict most all rx will
> only have a short span and will inline due to being under the inline head portion of the
> prover. Therefore, this issue is mostly moot". (1) The machine reading is accepted; the
> partial-proof routes are recorded on [EARNED-SKIP]. (2) Consequences' (g) row is REPLACED:
> rev 3's new stretch limit was deleted by rev 4 (it could never bind under the existing
> 4096-state anchored ceiling, which is the stretch's only bound), and at stage 2 the owner's
> "set in limits" becomes ONE `limits.def` row, `PCREC_DEFAULT_WINDOW_SEARCH_WIDTH`, with a
> per-compile option (`--window-search-width=N`) and a measured default. READING TAKEN (the
> manager's LEAN, owner question open): it bounds the cover ROUTE, not the stretch; the walk,
> record and listing still state the stretch to the ceiling; a pattern over the limit runs as
> today, which is a cliff (limit 32: `[0-9a-f]{32}` covers, `[0-9a-f]{33}` runs the engine for
> all 33 positions), NOT Consequences' "no cliff: past it the first positions up to the limit
> are still stated". The no-cliff form is [EARNED-SKIP]'s (PARKED). (3) (e) is AMENDED by the
> owner for the stage-2 kit request: his rendering direction is carried to the kit verbatim as
> his; D157 still binds pcrec (facts only from pcrec). (4) (f) stands; the stage-2 timing adds a
> defined A/A noise procedure. Revisit when: the owner answers the route-versus-stretch question,
> or (g)'s limit is re-measured. Applied in `docs/design/cover_cap.md` rev 5.1.

### [EARNED-SKIP] note TEXT (dated, for the manager to append to its row body)

> **2026-11-15 (manager, from [COVER-CAP] rev 5.1, review r13 F23/F24).** [COVER-CAP] stage 2
> bounds the cover ROUTE by a per-compile width (`--window-search-width=N`, default measured): a
> fixed-width pattern wider than the limit gets no cover and runs the engine for every position,
> a CLIFF. The no-cliff form, "prove the first N positions, the engine finishes the rest", is
> this row's proof extent read at the width limit, and it is where the cliff goes away (the
> owner's 14:10 "1." names its two engine-side routes, recorded above). Status unchanged:
> PARKED. Trigger unchanged (lookaround-as-run lands, then a bench cell where the engine's
> finish is a measurable share), plus one: the owner answers [COVER-CAP]'s route-versus-stretch
> question for the stretch.

## THE VALUED OPTION

(cover_cap.md §11.2.1, in ten lines.)
1. Row: `PCREC_DEFAULT_WINDOW_SEARCH_WIDTH`, 32 UNMEASURED until §11.4, unit `positions`, kind `selection knee`, override `FLAG_D` (`flag+-D`), anchor `3.12` (new `limits.md` section), home `LIMITS_H`; registry 81 -> 82.
2. Field: `int window_search_width` in `pcrec_options`, 0 = built-in default (the `unroll_k` shape); CLI `--window-search-width=N` beside `--unroll=` in `cli/main.c`, `cli_int_value`, not in `--help`.
3. Legal range `1 .. PCREC_ANCHORED_MAX_STATES - 1` (4095 shipped); refused, never clamped: CLI `cli_err("--window-search-width wants an integer in 1..4095 (got '...')")`; library `pcrec_compile` -1 with `invalid window_search_width %d (1..%d, or 0 for the built-in default)` (the out-of-range `tune` path, `compile.c:2074`); build default by `_Static_assert` (not `#if`).
4. Override order: explicit option > a dial cell if one is ever measured (an explicit spelling beats the dial, `limits.md` §8b¶2's rule) > `-D` build default > the row's literal. `--memfn=no-window-search` still denies the route at any width.
5. Reaches compound parts by construction (`part_compile` copies the parent's options): F12 closes.
6. Stamp: NONE (manager decision open; lean none): `<PREFIX>_DFA_SCAN` already records the outcome and the listing names `width-limit` with `k`. So the option is NOT an `abi` event of its own; the stage-2 joint landing's one event covers stage 2. A stamp, if ruled, folds into that event.
7. `rx_info.flags`: not a bit. `.rxt`: no line (neither precedent has one).
8. Spec hunks in the same change (D80): `tuning.md` new section 2.56 + its §2¶4 table row + its §4 field-table row + a pointer from §2.43¶3d; `limits.md` new section 3.12 + contents line; `match_api.md` §8.2 options listing and §6.3.4¶2's `"cover"` row; `facts_listing.md` §4.5¶2 (one word); the abi changelog entry. `cli.md` §1.18: no hunk (generic).
9. The two lowered-ceiling reference builds pass `-DPCREC_DEFAULT_WINDOW_SEARCH_WIDTH=` 5 and 2.
10. The test-only lever is DROPPED: the option serves the kitproof `W` rows, the `test-axes` arm, the compile-cost record and the timing; nothing needs a lever-fence entry.

## KIT REQUEST DRAFT

Re-issued complete and facts-only (D157); the owner's direction quoted as his. The manager files
it as R-n (next after R-44) only after the readiness re-check of rev 5.1; this lane did not edit
`memfn/docs/requests.md`. Text as in cover_cap.md §11.5:

> **R-n (DRAFT, pcrec manager) — window spans of up to 4095 positions ([COVER-CAP] stage 2)**
> - GO: the owner's build go covers stage 2 ("Go on all stages", Frank 2026-11-15); pcrec's
>   stage-2 design (cover_cap.md §11, rev 5.1) passed its critic round (r13) and a readiness
>   re-check before this request was filed.
> - FACT (statement). pcrec states one REPORT window site per cover: span 0 of `k` exact
>   positions, `1 <= k <= 4095` (4095 = pcrec's anchored-machine ceiling, 4096 states, less
>   one), with a context position at -1 and at `k` where they constrain. Today the statement
>   stops at 32 positions.
> - FACT (the three bounds pcrec relies on). Today pcrec admits a cover only where all three of
>   your bounds hold: `k <= MF_WSPAN_POS` (positions per span), `k + 1 <= MF_WREACH` (the
>   after-context span sits at offset `k`), `k < MF_MAX_FWD` (offset `k` is inside the proof
>   range). For `k` = 4095 that is: positions per span >= 4095, reach >= 4096, proof range
>   forward >= 4096. pcrec will assert its ceiling against all three at its build time.
> - FACT (how pcrec reads the proof). pcrec compares the reply's WHOLE counted proof range with
>   its statement: the stated set at each of offsets 0..k-1, the stated context at -1 and `k`,
>   and "nothing proven" (all 256 bytes) at every other offset, every offset past `k`
>   included. A reply whose range ends before offset `k` is a pcrec internal error.
> - FACT (how pcrec holds the reply). pcrec holds the reply's class record (`mf_class`) BY
>   VALUE: in its cover record, four per `CandAsked` record, in `mf_result`, and on the C stack
>   in 8 places (one local and 7 `CandScan` locals in `src/gen/emit_dfa.c`). Today the record is
>   41 offsets x 32 B = 1,312 B; at 4,104 offsets x 32 B it would be 131,328 B each, against
>   pcrec's compile stack budget of 442,368 B (`PCREC_COMPILE_STACK_BUDGET`).
> - FACT (coupling). `MF_MAX_SPAN_POS` is defined as `MF_MAX_TERM`, and pcrec reads
>   `MF_MAX_TERM` at three sites of its own (the VM stride assertion, the term-count bound, the
>   ADVANCE stride bound); pcrec needs to know whether they stay equal.
> - FACT (population, census of 11,738 compiles, both encodings, before pcrec's stage 1).
>   1,852 compiles took the cover; almost all are short. Beyond 32 today: `k` = 36 (two uuid
>   shapes), 40, 49, 60, 500, 1000, mostly runs of one byte class; the bench's are `lit-l40` and
>   two uuid shapes. pcrec states no span longer than its width limit: such a pattern runs
>   pcrec's engine route. The limit has a built-in default (32 until pcrec's stage-2 timing
>   sets it, before the joint landing) and a per-compile option up to 4095
>   (`--window-search-width=N`, `pcrec_options.window_search_width`).
> - FACT (cost, stage 1). `[0-9a-f]{24}` -> `{32}` cover: `.text` +208 bytes, about 26 per
>   position (gcc 15.2 `-O2 -std=gnu11 -c` on pcrec's default emit, `size -A`; 1,752 -> 1,960
>   by that command). Review r9 EMITTED-2: `dig-exact-32` on (31 digits + `g`) repeated,
>   instructions:u 230.7 M (engine route) vs 1,534.8 M (cover), x6.65; +14 % on `z`*n. The
>   statement gives every position's set.
> - OWNER DIRECTION (Frank 2026-11-15 14:35, verbatim; his direction to the kit, amending
>   D198 (e) for this request): "we have a performance dial for pcrec. it could include some
>   options for the kit. Also, I would default to sub span loops (excepting the measured head
>   inline ) then measure if inline was faster than the other way around. Measure three: all
>   inline, all loops, header inline then loops. Then the speed dial option can be always inline
>   should it prove that is faster". And (15:00): "I predict most all rx will only have a short
>   span and will inline due to being under the inline head portion of the prover. Therefore,
>   this issue is mostly moot". Size the measurement to that. pcrec's dial (`--tune=N`) is
>   live and can carry a kit option as a cell once your cards show one faster.
> - ASK. (1) Can the statement and the reply carry spans up to 4095 positions? Name the three
>   bounds you declare (positions per span, reach, proof range forward) and the reply's counted
>   proof range. (2) Do `MF_MAX_SPAN_POS` and `MF_MAX_TERM` stay equal? (3) The three forms'
>   cards per the owner's direction, at lengths of your choosing within the population above.
>   (4) Your reading of the dense near-miss regime above (no form asked). Reply in
>   responses.md with the form you choose before building.
> - Deliver: a kit branch for merge review, for ONE joint landing with pcrec's stage 2.


## OPEN QUESTIONS

### OWNER (plain words; each says "reply either way")

1. **What does your span limit stop: the shortcut, or the proof?** (cover_cap.md §9 Q7.) We read
   "set in limits ... adjusted by the user per artifact" as a limit on the SHORTCUT: a pattern
   whose matches are always exactly N characters, N up to the limit, is found by testing those
   characters directly, with no matching engine; a longer one runs on the engine as today.
   Example at limit 32: a 32-character hex id takes the shortcut, a 33-character one runs the
   engine for all 33 characters: a cliff. The other reading (prove the first N, engine finishes
   the rest) removes the cliff but is the parked "partial span" work. Leaning: the shortcut
   reading, cliff stated in the spec; the no-cliff form waits for its trigger.
2. **(Only if the timing night's dense near-miss cells lose.) Your class-run width, or one width
   for all?** (§9 Q8.) One width would also send the winning long literals back to the engine;
   a class-run width keeps them but is a rule keyed on what the positions hold. Leaning: ask the
   kit to render class runs so a near miss does not re-test the whole run first; your class-run
   width if that does not close the loss.
3. **FYI (§9 Q9):** the per-artifact option is added now with stage 2, not at the interface push.
   Say if it should wait.

### MANAGER

1. Spelling (F26, yours): I picked `WINDOW_SEARCH` (`PCREC_DEFAULT_WINDOW_SEARCH_WIDTH`,
   `--window-search-width=N`, `window_search_width`) over rev 5's `WINDOW_MATCH`, to match the
   shipped `--memfn=no-window-search`. Confirm or respell before the build.
2. Stamp for the option: none (lean), or a `<PREFIX>_...` value stamp like the precedents' (it
   would be scaffolding on every DFA artifact, folded into the joint landing's abi event).
3. Plan of record (F16): land once with the measured default on the combined branch (my text),
   or the 32 fallback. Needs a bench night on a non-main branch.
4. File the D198 addendum and the [EARNED-SKIP] note (texts above); add the width limit to
   [SIZE-KNEE]'s member list (F27 PLAN).
5. Before merging lane/covs2e (or its successor) to main: respell
   `docs/dev/lanes/covs2d_report.md`'s quoted PL14 message (pre-existing PL14 red on this
   branch's base; green on main).
6. Bench-only question for relay (memory `pcrec-ask-bench-dev`): the bench report's field names
   for its launch count, spread/bimodal flag and validity verdict, so §11.4's procedure names
   them; and cell names for the 24-position twins and the two synthetic long cells.
7. The F1/P4 plant (the kit's text over-tests offset k+1) lives in the kit's tree on the combined
   branch: whether pcrec's mech arm may host it or the kit hosts it as its row is a kit-rules
   question to settle at the build go.
8. Readiness re-check scope (r13's recommendation): one opus critic on the §11.1/§11.2/§11.6
   diff of rev 5.1.
