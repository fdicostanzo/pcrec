# PREMISE findings: bakeoff (pricing_bakeoff.md @ a7b229f3f)
## Findings
### PREMISE-1 L-ROW's "no wrongness risk" premise is false: rows are undeniable ON PURPOSE, for soundness and the give-up contract, and the census walk denies them
- status: CONFIRMED
- severity: answer
- effort: small
- blast radius: the census (§3.1 step 1) admits arms that are wrong compiles or contract-crossing compiles as "valid paths"; an arm whose give-up became an answer can pass the libpcre2 gate (libpcre2 answers too) and enter the valid set, so FM and the oracle are graded against a path the compiler must never emit. Where the answer is actually wrong, §5.5 makes it a hard stop of the whole bake-off ("a wrong compile, not a timing question") caused by the lever, not by any rule.
- where: §3.4 L-ROW ("every slot's last row is an undeniable always-sound fallback ... It can only do what a flag deny does, on rows that lack a flag"), §3.1 step 1 ("for every slot on the observed path whose row is not the slot's fallback, add a compile with that row denied (by its public flag where one exists, by the test-only row deny of §3.4 otherwise)"), §10 item 2 ("L-ROW is small and carries no wrongness risk"); review tree `src/gen/emit_dfa.c:10430-10443`.
- finding: the soundness argument only covers the LAST row; L-ROW skipping an earlier undeniable row lands the NEXT row, not the fallback. Several rows lack a deny bit precisely because denying them is unsound or crosses the give-up surface (D158). The code says so in the RETRY block: "`exact` stays first and undeniable because nothing may make an exact-language hybrid's retry adaptive: its clamped form's window END is live (D51 ruling 2) and a step would carry it stale. `clamped` is undeniable for the CONTRACT's sake: past it, an adaptive retry runs a subset of the attempts today's retry runs, so a give-up can become an answer" (`emit_dfa.c:10431-10436`); `retry-anchored` likewise (`:10439`). "Rows that lack a flag" are therefore not "rows a flag deny could have reached"; they are in part rows no deny may reach.
- repro: `build/pcrec -p rx -o e0.c --pattern 'foobar\d' --engine=vm -fprefilter` stamps `RX_VM_RESEED "exact"` (observed). `exact` is not RETRY's fallback (`fixed` is, `emit_dfa.c` row table, `cand_fallback` = last routed row), so §3.1's walk issues `PCREC_CAND_DENY=RETRY:exact`, which per `cand_select` (`:10721-10733`, `continue` past the named row) lands `adaptive-dense`/`adaptive` (`deny PCREC_NO_HYB_RESEED`, not set) — the exact case the comment forbids. Expected (per the design's claim): only sound arms reachable.
- proposed fix: L-ROW takes an ALLOWLIST of deniable rows (rows whose skipping is a speed-only change; the design names them, the RETRY validity rows, `presence-none`/`one-attempt`, LOCATE `empty`, FINISH's per-hand finishers and the BOUND rows are excluded), and the census walk denies only allowlisted rows; C-LEVER gains a planted deny of `RETRY:exact` that must be refused.

### PREMISE-2 "Every slot's last row is the fallback" is false for the hand-keyed slots: FINISH's totality is per HAND, so the walk's step can deny a hand's only finisher
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: census compiles that abort (NULL row; in the trace build a `cand_oracle_fail`) or, at worst, select nothing for a hand; the walk's arm counts and its truncation flag are then wrong for every DFA site whose FINISH row is not `report`, i.e. nearly all of them.
- where: §3.1 step 1 ("whose row is not the slot's fallback"), §3.4 L-ROW; `emit_dfa.c:10735-10747` (`cand_fallback` = the last row of the slot routed on `rt`, hand-blind), `:11396-11400` ("FINISH's totality is per HAND (§2.3): on every route FINISH is asked, the last row taking each hand an asker gives there ... is undeniable"), `:10637` (cand_select returns NULL only if totality fails).
- finding: the slot fallback by `cand_fallback` on the DFA route for FINISH is `report` (the last FINISH row, `:10627-10630`, takes SPAN only), while the `AT` hand's undeniable last finisher is `search-from`. A DFA site's default FINISH row for the match-here ask is `verify-at` ("unwrapped"); its public deny `-fno-anchored-dfa` lands `search-from` (observed below); `search-from` "is not the slot's fallback", so the walk's next step L-ROW-denies it and the AT ask has no row left.
- repro: `build/pcrec -p rx --pattern 'foo\d+' -fno-anchored-dfa` stamps `RX_DFA_MATCH "search-filter"` (= `search-from`'s tok, observed). Read `cand_fallback` (`:10740-10747`): returns `report` on the DFA route. Expected by the design: denying any non-fallback row leaves a sound row.
- proposed fix: the walk's stop condition is "the row is the last row taking that ask's hand" (the self-check's per-hand rule, `:11396-11440`), or the walk is restricted to the priced slots §3.1 itself lists (FINISH, BOUND, WIDTH, WINDOW are not among them).
### PREMISE-3 The bench's timed loop is the REPEATED regime the design rules out; "its discipline is the one the bake-off wants" is false on the one regime axis §1 names as decision-flipping
- status: CONFIRMED
- severity: answer
- effort: medium
- blast radius: the oracle (and every regret) would be measured on repeated calls per subject, which regime_eval.md §2.4 shows flatters the walk's branch predictor (branch misses far lower on repeated 64 KiB buffers); the no-search and walk-heavy arms (exactly the NEXT/no-search and window rows the options differ on) are flattered, so FM/MN/no-search can read as winning where they lose on streamed text. A wrong verdict on rows 1, 4, 5 is possible, not just noise.
- where: §5.1 ("Its discipline is the one the bake-off wants: a timed loop in its own aligned translation unit ..."), §1 item 1 ("so every timed cell is STREAMED"), §5.2 ("Every cell is STREAMED (regime_eval.md §2.4's condition (S))"); open questions B5/B6 ask about subjects and raw trials but not about streaming.
- finding: the bench times "the per-subject time per call ... Each subject's iteration count is calibrated per engine toward a fixed timed-work target" and "times a loop of repeated calls to the same compiled matcher" (pcrec-bench `docs/methodology.md:74,76`). That is a calibrated repeat count on each subject, i.e. condition (R), not (S). Nothing in methodology.md mentions a streamed condition (`grep -i stream` there: 0 hits). Handing the bench 64 distinct 64 KiB buffers (B5) does not by itself make a cell streamed if each buffer is called repeatedly. regime_eval.md:216-218: "a repeated judge flatters the walk where the table picks forms. Repeated 64 KiB survives only as a labelled, UNGATED" reading.
- repro: `grep -n -iE 'stream' pcrec-bench/docs/methodology.md` → no lines; `sed -n 74,76p` → the two quoted sentences. Expected (per §5.1): a streamed cursor over distinct buffers per timed call, as grid1's fallback has.
- proposed fix: add a bench question B7 "can a cell's timed loop stream a cursor over N distinct buffers (one call per buffer per pass), or is the per-subject calibrated repeat fixed?"; if fixed, the bench is the wrong harness for the oracle and grid1 (streamed) is primary, with COST-11 (b) stated as NOTED.

### PREMISE-4 D-sweep timings at the bench's scratch tier are "never in store/", so the design's by-reference provenance (and G3's critic re-run) has nothing to reference for D
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: K-fit, C-PRICE (whose < 0.5 on D stops stage 4 and is §9.3 row 0), C-FM/C-KIT/C-RULE's D runs read timings that have no store record id and no sha'd record; "never copied by hand ... each with the sha of the record it read" (§4.1) cannot hold for D, so the stop rules that read D are not reproducible by G3's critic.
- where: §4.1 row 2 (ground-truth timings "by reference: pcrec commit pin, testee config id, tier, record id"), §5.1 tiers bullet ("the D sweep ... may run at the SCRATCH tier (`pcrec-local` with `PCREC_LOCAL_FLAGS`)"), G3.
- finding: pcrec-bench `testees/pcrec/CLAUDE.md:60`: `pcrec-local` is "a PROVIDED binary, `$PCREC_BIN` ... No pin, SCRATCH TIER BY CONSTRUCTION, never in `store/`, never ranked". The design treats the scratch tier only as "never ranked"; it is also never stored, and has no pin.
- repro: `sed -n 60p /home/pcrec/projects/pcrec-bench/testees/pcrec/CLAUDE.md`. Expected by §4.1: every timing the scorer reads has a store record id.
- proposed fix: state D's provenance separately (the bench's scratch output files archived with their sha by the bake-off, or D at the pinned tier too), and say which stop rules read D.
### PREMISE-5 "(a) is J" contradicts the decision rule: §9.3 lists (a) among the candidate options of rows 3-6, so row 5 can crown (a) "on numbers" by construction
- status: CONFIRMED
- severity: answer
- effort: small
- blast radius: J is the model's own argmin; on any population where the model ranks arms reasonably (the very condition row 0's C-PRICE >= 0.5 and row 3 require), (a)=J has the lowest or near-lowest modelled-pick regret, so row 5 ("THAT OPTION WINS ON NUMBERS") or row 4's tie set is decided by an option whose numbers the design itself says are not a numeric case. Row 3's "largest paired placement-loss difference among the options" also includes (a), whose placement loss is identically 0.
- where: §0 item 2 and §2 ("The bake-off reports (a)'s numbers as J's and states that its case is architectural, not numeric"; "says so instead of pretending to grade (a) on picks (§6.2)") vs §9.3 ("'The options' in rows 3-6 are the CANDIDATE placements: A1, HY, Dx, MN, KF and (a)").
- finding: the two texts are incompatible. Either (a) is graded (then it cannot be J by fiat; it must carry its own text's kit rule, see PREMISE-6) or it is a reference (then it is not in rows 3-6).
- repro: read §9.3's first paragraph and §2's last paragraph of the frozen copy (lines 767-768 vs 172-175). Expected: (a) excluded from rows 3-6, or graded by a rule written from PS §7.2.
- proposed fix: remove (a) from §9.3's candidate list (report it beside J as the ceiling), and say in row 4/5 that the architectural case for (a) enters only through §9.4.

### PREMISE-6 "Every placement is the same cost model cut at a different seam" is false for the rules as written: A1/A1u/HY/KF/MN keep the kit's MARGIN 2/1 guard and J does not, so "placement loss" mixes a non-cost guard with the seam
- status: CONFIRMED
- severity: answer
- effort: small
- blast radius: A1 vs Dx (the (a′)-vs-(d) question, the round's main contest) differs by MARGIN as well as by seam: A1 "MARGIN kept", Dx takes a plain argmin. If MARGIN costs (it biases toward PARKED: a RESEED alternative wins only at less than half the least cost, `memfn/src/window.c:669-684`), Dx can beat A1 by more than δ for a reason that is not where pricing lives, and row 5 crowns (d) as a PLACEMENT. The same holds for Dp's prune (a rule simplification, not a seam). The claimed decomposition is also not additive: per cell 1+regret = (1+model error)(1+placement loss), and placement loss is negative wherever an option's pick happens to be faster than J's (J is the model's argmin, not the measured best).
- where: §0 item 1, §2 table (A1 "MARGIN kept"; Dx "takes the argmin"), §6.2 (A1 "the MARGIN guard kept (review 2 COMPOSE-5)"; J "the full sum of all terms"); K4 proposes a no-MARGIN arm only as "reported (never deciding)".
- finding: §0's premise that a seam "loses only where a decider lacks an input or a coupling crosses it" holds only if every rule is the same argmin restricted by inputs. The rules include a guard (MARGIN), a prune (Dp), first-match remnants (MN, FM) and the uncorrected term (A1u). Their gap to J is rule-form loss, not placement loss.
- repro: `sed -n 669,684p memfn/src/window.c` ("MARGIN: a RESEED alternative wins only at less than HALF the least-cost ..."); design §2 table rows A1 and Dx. Expected for the claim: identical objective in every rule, inputs the only difference.
- proposed fix: make MARGIN a declared on/off dimension applied to EVERY kit-level and backend-level rule alike (A1 and Dx both with and without), decide (a′)-vs-(d) on the pair with the same MARGIN setting, and state the decomposition as a ratio with signed placement loss.

### PREMISE-7 C-BLIND is vacuous without L-KIT, and row 1's "PRICING DOES NOT PAY" leans on it; F7 recommends running without L-KIT
- status: CONFIRMED
- severity: answer
- effort: small
- blast radius: with L-KIT refused or deferred (F7's leaning: "yes; do not wait"), no random kit option is drawn, C-BLIND's share is 0 % of 0 draws, "at or below 10 %" holds, and row 1 can end the whole question ("PRICING DOES NOT PAY on this population") with every kit within-site alternative untimed, i.e. with the oracle a lower bound by an unknown amount, which is the case row 1's own parenthesis says C-BLIND exists to bound.
- where: §3.5 (the 2 salted draws are "options drawn uniformly by salt" from L-KIT's dump), §8 C-BLIND (planted failure: "none (it is itself the probe)"), §9.3 row 1, §10 closing paragraph ("the bake-off is still worth running for rows 1-3"), F7.
- finding: a control whose reach can be zero and which has no planted failure passes vacuously (learnings §3, a population nobody counts). Row 1 also reads it on H-open at stage 2, before the stage-3b top-up exists.
- repro: design text only: §3.5 draws come from L-KIT's dump; §10 item 1 says without L-KIT the within-site options are unreachable; §9.3 row 1 requires only "C-BLIND's rate ... at or below 10 %". Expected: row 1 requires C-BLIND's reach (random arms timed per site) above a stated floor, else it reads INCONCLUSIVE.
- proposed fix: give C-BLIND a reach floor (e.g. at least one random arm on 80 % of kit sites) and make row 1 unreachable when the floor is missed; draw random cross-path arms (deny sets by salt) too, so the probe exists without L-KIT.

### PREMISE-8 C-FM can only be a tautology: FM's "valid rows on the hypothesized upstream path" are collected by no designed instrument
- status: CONFIRMED
- severity: design
- effort: medium
- blast radius: the control that "stops stage 3" if the simulator mis-models today's walk cannot go red for the reason it exists. If FM is re-derived from the census, FM is by definition the empty-deny arm, so C-FM checks a join. The planted failure (swap two NEXT rows in the simulator's table) only reaches it if the simulator has per-row validity to walk, which it does not.
- where: §6.2 FM ("walk the valid rows of each slot in `cand_rows[]` order on the hypothesized upstream path"), §6.4 C-FM ("re-derives FM from the valid-row records and the table order"), §3.4 L-VALID ("evaluates EVERY row of every slot on the DEFAULT path ... Not needed for the bake-off's correctness", "optional").
- finding: valid-row records exist only through L-VALID, which is optional and covers the default path only. Predicates read other slots' selections (`cand_nested_read`/`CAND_READ`, `emit_dfa.c:10693-10702`; G1 reads NEXT under the handoff's deny, `:10675-10680`), so validity on any other upstream path cannot be computed from the default path's dump. The census gives reached ARMS, not valid rows.
- repro: design text §3.4 vs §6.2/§6.4; code `emit_dfa.c:10675-10680` (the deny bits nested predicates select under). Expected: C-FM's input named and produced by a required instrument.
- proposed fix: make L-VALID required, run per census arm (not only on the default path), and state C-FM as "first valid row per slot in table order, from L-VALID's records of the default arm, equals the default stamps/CANDTRACE"; say plainly that it checks the simulator's table copy, nothing more.
### PREMISE-9 The census walk also denies rows in slots the design does not price (FINISH, BOUND, WIDTH, WINDOW), producing byte-distinct arms whose timed entries are byte-identical
- status: CONFIRMED
- severity: speed
- effort: small
- blast radius: arm counts roughly double on DFA sites (every arm gains a FINISH twin), the 64-compile cap truncates sooner, §5.6's ~9 arms per site and the bench sizing are low, and the twins time as pure A/A noise; "dedupe by bytes" (§3.5) cannot merge them because their `_match` differs.
- where: §3.1 step 1 ("for every slot on the observed path whose row is not the slot's fallback"), §3.1's qualifying slots list (LOCATE, PRESENCE, FIRST, NEXT, RETRY, the route pair), §3.5, §5.6.
- finding: FINISH's `verify-at` vs `search-from` changes only the match-here entry on most DFA sites; the find/next entries both call shapes time are untouched.
- repro: 64 public-flag combinations of {`-fno-run-prefilter`, `-fno-offset-skip`, `-fno-req-handoff`, `-fno-start-set`, `--memfn=no-fd-pres-g1`, `-fno-anchored-dfa`} on `foo\d+` give 10 distinct artifacts, 5 of them `-fno-anchored-dfa` twins (`RX_DFA_MATCH "search-filter"`); `diff` of the default vs `-fno-anchored-dfa` artifact: hunks only at the stamp line and lines 198-283/437 (the anchored machine and `rx_match`), `rx_search` (lines 100-197) identical. (Script: `premise/combo.py`.) On `\w+@example\.com` the same: 2 distinct, the second a FINISH twin. Expected: walk restricted to the priced slots, or twins merged by the bytes of the TIMED entries.
- proposed fix: walk only the slots §3.1 lists as priced; dedupe on the normalized bytes reachable from the timed entries (or hold FINISH at default and say so).

### PREMISE-10 RULING CHECK: the design charges D146 and D161 addendum 6 to option (a) only; the rulings each option reverses are not inventoried, yet §9.4 criterion 1 is the predicted deciding path
- status: CONFIRMED
- severity: design
- effort: medium
- blast radius: §9.1's own prediction is a numbers tie (row 4), so §9.4's criterion 1 "fewest standing rulings reversed" decides the placement. Without a pre-registered per-option inventory, criterion 1 is argued after the data, which G3 forbids.
- where: §0 item 2 ("its costs are architectural (the build retry, D146, D161 addendum 6 ...)"), §9.4 item 1, F2.
- finding: by the D-row text: D146 "pcrec does no cost comparison" (`decisions.md:8995`) is the clause Dx/Dp/HY reverse (the backend takes the argmin over the kit's options with their price components). D161 add. 15 Q-WR-9: consumer cost enters "as a per-route MEASURED constant in the D166 set, never a pcrec price model" (`decisions.md:9526`) — consistent with A1/A1u/KF/MN, reversed by Dx/Dp/HY, and it is gated: "pricing waits for add. 11's trigger (a TUG cell measured losing for want of it)". D176 Q4: presence and stop have "ONE decider, the kit's window family" (`decisions.md:9918`) — HY (backend picks presence on/off per property value) and Dx/Dp (backend picks the stop through the footprint choice) reverse it. D161 add. 11: pcrec "owns the origin, the engine/route" (`decisions.md:9497`) — (a) reverses it. D146 is not (a)'s ruling cost: (a) keeps the kit owning in-site choices; its conflict is add. 11.
- repro: the quoted lines at the cited `docs/dev/decisions.md` line numbers (main a3cc4de82). Expected: a pre-registered table option x ruling x operative clause quoted (§9.4 item 1's own counting rule).
- proposed fix: add that table to the prereg (option, ruling, clause, reverses yes/no), confirmed with F2 before any data.

### PREMISE-11 D166 addendum 2 is cited backwards, and K6 asks the wrong owner: a committed stage-1 set is the default by the ruling
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: stage 1's "nothing in the default build moves" (§1 item 3, §4.2) and §4.1's "the simulator reads the committed file" cannot both hold under the ruling as written; if K6 is answered by the kit, the answer does not bind the store, so stage 1's sets stay "uncommitted scratch" and no constant may be cited as the verdict's (§4.2 last sentence), blocking stage 3.
- where: §4.2 ("either outside the default pointer (D166 addendum 2: before a second official set, a bare compile reads the LATEST set) or as a separate set id. Which spelling is the store owner's call (open question K6)"), K6 under "For the kit".
- finding: D166 item 1: "pcrec is compiled with the latest set by default ... A default-set change carries a mover census in the same commit"; add. 2 Q-MS-1: "until a SECOND OFFICIAL set exists ..., a bare compile reads the LATEST set" (`decisions.md:9739`). So a newer committed set IS the default; add. 2 gives no "outside the default pointer" option, it rules it out. The store (`measure_store/`, `docs/design/measure_sets.md`) is main's: D167 Q-R17P-14 "Main (measure_sets' owner)". Mechanically `measure_store/DEFAULTS` is an explicit pointer (`idk zen4-grid1@1`) and `index.tsv` has a `status` column, so a spelling exists, but using it departs from the ruling and needs Frank, not the kit.
- repro: `sed -n 9739p docs/dev/decisions.md`; `cat measure_store/DEFAULTS`; spec `docs/spec/measures.md` 5¶6 ("its default is the latest committed set"). Expected: the design cites a ruling that permits a committed non-default set.
- proposed fix: move K6 to "For Frank" (F9): "may a committed set be non-default before M2 (a DEFAULTS pointer that does not follow latest), or does the bake-off read uncommitted files with their sha?"; drop the add. 2 cite as support.

### PREMISE-12 C-REPRO's "within its own stated noise band" has no band to read: every row of the only set has `noise_e6` empty
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: stage 1's early stop and C-REPRO (§4.3, §4.5, §8) cannot evaluate the kit rows of the existing card families as they are written today; 26 of 68 rows are `derived`, whose band must be propagated from inputs, a method the design does not state. A C-REPRO that compares with an absent band passes or fails by the implementer's guess.
- where: §4.3 C-REPRO, §4.2 ("Each card is a method-card row ..., with its own A/A floor (`noise_e6`)"), §4.5 stage-1 early stop (A/A floor > 20 %).
- finding: `measure_store/zen4-grid1/1/set.tsv` section rows: `noise_e6` is `-` on all 68 rows (42 measured, 26 derived). The cards carry `aa_rule pair-per-group` and `gate_e6 30000`, a gate, not a per-row band.
- repro: `awk -F'\t' '/^#section rows/{f=1;next} /^#section/{f=0} f && !/^#/{print $5"|"$7}' measure_store/zen4-grid1/1/set.tsv | sort | uniq -c` → `42 -|measured`, `26 -|derived`. Expected: a band per row, or a stated rule for deriving one.
- proposed fix: make "writes `noise_e6` on every measured row, and a propagated band on every derived row" a stated requirement of K7 and of the pcrec half; C-REPRO compares derived rows by the propagated band.
### PREMISE-13 "The pcrec cards are the store's M4 milestone, not a bake-off invention" overstates M4: M4 is two quantities with a different, unmet trigger
- status: CONFIRMED
- severity: doc
- effort: small
- blast radius: stage 1 pulls M4 forward and widens it (four card families, one of them not a box constant) under M4's name; D77/`pcrec-build-under-measurement` wants the trigger named. No verdict effect, but the store's plan row and the stage-1 lane brief would disagree about what M4 is.
- where: §1 item 3, §4.2 ("both are the store's M4 milestone (`docs/design/measure_sets.md`: pcrec `c_call` / `c_byte` cards, the pcrec dependency hash's normalization, the open key-only schema for engine rows)"; "M4 carries its own spec hunk where it adds that schema"), §11 stage 1.
- finding: measure_sets.md §10.1: "M4 | pcrec's own quantities (`pcrec.c_call`, `pcrec.c_byte`), their cards, the pcrec-side dependency hash's body normalization ..., and `cand_rows[]` as readers in the census | the regime table's pcrec-side build". The key-only schema is a separate deferred row ("Trigger: M4, if the cards for `c_call`/`c_byte` turn out to be all boilerplate", `measure_sets.md:2331-2333`), not part of M4. C-MATCH (match phase per match) and C-WALK ("counted per (site, subject)", a per-site count, not a per-box constant) are not M4 quantities; C-WALK does not fit a set row at all.
- repro: `sed -n 2200p docs/design/measure_sets.md`; `sed -n 2331,2333p` same file. Expected: the design's card list equal to M4's, or named as an M4 extension with the bake-off as its trigger.
- proposed fix: say "stage 1 builds M4 early (trigger: this bake-off, D77) and extends it by C-ENTRY/C-MATCH; C-WALK is a census count, archived with the population, not a set row".

### PREMISE-14 GOALS: the measurable forms of G1, G3, G4 and G5 disagree with the body that is meant to serve them
- status: CONFIRMED
- severity: design
- effort: small
- blast radius: a critic re-running the goals' checks gets different verdicts from the body's checks; G3's "prereg sha before the first H timing" is violated by the staging as written, which is the leak guard of a pre-registered experiment.
- where: §G table vs §8, §3.2, §11, PR R5.2.
- finding: (1) G1: "pick the same arm on 100 % of H sites"; C-RULE (§8): "100 % of D sites before H is read". (2) G3: "the prereg file's sha is in the journal before the first H timing"; §3.2 item 3: "H's timing may run before the rules are frozen", and §11 stage 3 (after stage 2's H sweep): "the prereg file frozen and its sha journalled". (3) G4: "2 on the Mac"; §11 stage 1: two windows of "~1-2 h on Zen 1 and the Mac", i.e. 2-4 h. (4) G5: H "becomes the held-out regret population PR R5.2 requires"; PR R5.2 (c) requires spanning "both engines, both SIMD layers" and R5.5 "Both SIMD layers are read", while the design times SIMD-on on H-open only and never in the verdict (§5.1 Layer). The ranked order itself is served (fairness is cited to override cost in §G, and stops are placed before cost), so the order holds; the forms do not.
- repro: the quoted sentences in the frozen copy (lines 91, 93, 94-95, 253-255, 506-507, 728, 840) and PR rev 1 (`git show 90d5150f7:docs/design/memfn/pricing_requirements.md`, R5.2, R5.5). Expected: each goal's measurable form equal to the check the body runs.
- proposed fix: G1 → D sites (or both); G3 → "the prereg SKELETON's sha (salt, counts, margins) before the first H timing; the rule shas before H is read"; G4 → 2-4 h Mac; G5 → "the SIMD-off half of PR R5.2's population".

### PREMISE-15 Cited probes and code cites that do not match the review tree
- status: CONFIRMED
- severity: doc
- effort: small
- blast radius: none on the verdict; they are the evidence §3.3 and §3.1 lean on, so they should reproduce.
- where: §3.1 item 2, §3.3, §3.4, Words, §1 item 3.
- finding / repro (each a single compile with `worktrees/crit-bakeoff/build/pcrec -p rx`, or a read):
  (a) `[<>&]x --memfn=no-window-search`: observed `RX_REQ_WHY "dominated"` (unchanged), `RX_DFA_PREFILTER "offset-set"`, `RX_DFA_START "end-minus-width"`; the design says PRESENCE moves "from `dominated` to `emitted`" (probes w2, w3). RECOVER's move holds; PRESENCE's does not; the NEXT move to `offset-set` is unmentioned.
  (b) `[.,;]\d` with every other NEXT row denied stamps `RX_DFA_PREFILTER "none"` (LOCATE `cover`, NEXT off the path), not `byte-class`; `byte-class` appears only with `--memfn=no-window-search` added. §3.3's sentence omits that flag.
  (c) `CandPath` (`emit_dfa.c:11828-11834`) holds the two routes, machine masks, the asked-slots masks and RECOVER's row; it selects only LOCATE, RECOVER and FINISH (`cand_path_row`, `:11842-11858`). It is not "the selected path as a value" in the design's sense (a row in every slot).
  (d) "The kit already has an MF_TRACE build (`window.c`, ...)": `grep -c MF_TRACE memfn/src/window.c` = 0 (it is in `gate.c`, `finder.c`, `compose.c`); the Table A code L-KIT must dump has no trace hook today.
  (e) `tests/codegen/run_form_census.sh:307-316` holds the memchr 750 floor (`:316`); the offset-set 290 floor is at `:323`, outside the range. Both floors count artifacts over "patterns x 2 engine requests", not patterns.
  (f) D156 add. 2 generates the stamps "of the LOCATE x FINISH slots" (`decisions.md:9387`); `RX_DFA_PREFILTER`, `RX_REQ_WHY` and `RX_VM_RESEED` (NEXT, PRESENCE, RETRY) are not covered by it, so C-FM's "a source it did not compute" leans on CANDTRACE for those slots.
- proposed fix: re-run w2/w3/c2 and restate; cite `gate.c` for MF_TRACE; widen the census range; say which stamps are path-generated.

### PREMISE-16 J3's blinded author over `worktrees/.corpus/` would find J1b's sealed questions in the corpus tree itself
- status: SUSPECTED
- severity: doc
- effort: small
- blast radius: the design's "NEVER J1b" (§3.2 S-real) is broken if the J3 cell copies the corpus directory whole; J1b's sealing for the regime evaluator would be contaminated.
- where: §3.2 S-real ("written by a D27-blinded 'user' agent over the real-world corpus (`worktrees/.corpus/`, seven classes) ... NEVER J1b").
- finding: `worktrees/.corpus/sealed/` holds `j1b_questions.tsv`, `j1b_build.py`, `j1b_pcre2_compile.py` (listed, not opened). The design names the sealing file (`rwquest2/SEALED.md`) but not this directory.
- repro: `ls worktrees/.corpus/sealed` (names only). Confirmed if the J3 cell's allowlist includes `.corpus/` without excluding `sealed/`.
- proposed fix: state that the J3 cell's allowlist is the seven class directories and their manifest only, `sealed/` excluded.
## PROBED-AND-HELD
- Code line cites at `a3cc4de82` (review tree): 13 checked (`cand_rows[]` 10154-10630, `cand_select` 10721-10733, `cand_fallback` comment 10735-10738, `cand_select_quiet` 10869, `PCREC_PICK_PLANT` 10974, the `used` save 10996-10998, 7872-7876, 8020-8026, 10087, `CandPath` 11828, `memfn.h:414-415`, `compose.c:309`, `window.c:620-720`): all land on the named code (CandPath's CONTENT is PREMISE-15 (c)).
- §3.3 inventory, row by row: 11 rows checked against `--list-axes` and the row table: NEXT's 8 deniable rows and their flags, `memchr*`/`byte-class*`/`pred-memchr` with no deny (5 + `next-none`), FIRST's 4 rows under `-fno-req-handoff`, RETRY's deny bits (`-fno-hyb-reseed` lands `fixed`), RECOVER's 4 rows and 3 flags, LOCATE's 3 + `empty`, PRESENCE's rows and `--memfn` denies, `-fno-rev-end-onewalk`, `-fno-premul-table`: hold. 10 public flags accepted by the CLI (`-fprefilter` refuses a DFA pattern, as §3.3 implies). Probe `e0` (`foobar\d --engine=vm -fprefilter` → `vm`/`hybrid`) and probe `a3` (`foo\d+` with every other NEXT row denied → `memchr`) reproduce.
- C-LEVER's premise (trace build = default build when no lever is set): 3 patterns byte-identical after the header-name line.
- Dedupe by bytes: a no-op deny (`-fno-rev-end` on `foo\d+`) differs from the default only in the `#include "<name>.h"` line (1 case; the normalizer must strip the output-name line, not only flag echoes).
- Observed path from stamps + CANDTRACE: per-slot CANDTRACE rows agree with the stamps on 5 patterns (one row per slot per ask site).
- Counts: 177 rwquest questions (178 lines with header) and D161 add. 14's correction "172 of 177 compile, 170 have a start-search site"; emit_sweep's "3,938 corpus pattern lines"; SIM-1's 550/85,176 (0.6 %) and worst 1.85 %, review 2's 115,248 + 85,176; SIM-2's 1-204 options; seven corpus classes; gcc 15.2.0: 6 hold.
- Store/spec: `docs/spec/measures.md` §2.3 admits owner `pcrec` and §2.1 has a `class` key; one set `zen4-grid1@1`, scratch, `x86_64-avx2/zen4`, the `idk` default; `generate.py` transcribes, `from_interim.py` one-time, `scripts/measure.sh` archives probe output: 6 hold. The window family consults no set today (`RX_MEASURES ""` on 5 window-site patterns), so FM's `plan_cost.def` constants are the right ones.
- Bench facts: per-config `flags`, `pcrec-local` + `$PCREC_LOCAL_FLAGS` as the scratch tier, five trials with the v1.4 trial-agreement rule, `pin.sh` builds a plain `make` (so B4 is rightly open): 4 hold.
- Rulings that say what the design says: D147 (both layers reported; SIMD-on as a secondary report is consistent), D153 (remodel overlap, [VMREC] order), D158 (give-up arms excluded), D172 (REPORT and find-window one request, KF's premise), D166 add. 1 (perf optional; provenance `perf: ran | skipped`), D161 add. 14 (correction figures), D77 (used only as "not triggered"): 7 hold.
- Goal ORDER: the body resolves fairness over cost (§G note, §3.5, §10) and puts every stop rule before spending: holds (the measurable forms are PREMISE-14).
- §5.6 arithmetic: 250 x 9 x 2 x 2 = 9,000 cells x 0.25 s = 37.5 min, "~40 min": holds.
- Compiles run: about 230, sequential, `gnutimeout 30 nice`.
