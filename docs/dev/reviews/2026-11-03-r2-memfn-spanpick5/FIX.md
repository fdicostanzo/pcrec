# FIX lens: span_pick rev 5 (9c9aadb60), fix-induced findings + ruling check against main 7f55a62f9

Review tree: worktrees/crit-memfn-spanpick5 (main 7f55a62f9). The rulings are main's D186 add. 1-2
(`git show 7f55a62f9:docs/dev/decisions.md`, "## D186") plus the [MEASURE-SET] plan row
(fa736a260/7f55a62f9). Compiles run: 30 single compiles (review-tree `build/pcrec`), no make.

## Findings

### FIX-1  Main RULES that the provenance fields leave the seam IN STAGE 1. Rev 5 leaves it as "main's call", and stage 1's unit list has no unit for it
- status: CONFIRMED (text). Main D186 add. 2, "Blind compiles use the default": "The provenance fields (`mf_prov.source`, the bundle "default" label, memfn.h) leave the seam in span_pick stage 1: the kit never sees the source." Rev 5 §pcrec-side findings: "whether the field stays is main's call"; §Owner rulings "For main: ... `mf_prov.source`'s future". Rev 5 §Staging units 1a-1f do not contain it.
- severity: design ; effort: one stage-1 unit plus a spec hunk ; blast radius: kit ABI, 6 files of tests ; where: §pcrec-side findings (rate source), §Staging (stage 1 table), Goal 2
- body: this is a layout change to `mf_prov`, which is embedded in `mf_akind` (memfn.h :1223-1233, :1235-1241). It needs an MF_SITE_ABI event that rev 5 does not count. Rev 5 says 1f is stage 1's only MF_SITE_ABI event (§What moves across, §Staging 1f). Every reader the unit must touch, traced in the review tree:
  - `src/gen/memfn_sites.c` :186-191 `akind_source_map`, :273-276 (writes `prov.source/bundle/digest`), and `pcrec_memfn_prov_stanza` (:~600). Also :233-249: the `KSRCTRACE object` record reads `k->prov.bytes`/`k->prov.fidelity` FROM THE BUILT KIT OBJECT "so tests/findings/e1_object_check.py holds the wiring itself". If those fields leave, the record and that check's premise both move.
  - `tests/memfn/prov_check.c` :27-34, :42: static `offsetof` assertions on all five fields (a build failure).
  - `tests/memfn/finder_check.py` :654-740, section L `check_prov` (R-24). Parts (1)-(3) test pcrec's mapping into `mf_prov.fidelity/bytes`. Part (4) greps memfn/src for `mf_prov|mf_akind|->prov|.prov` (KIT_READERS_RE, :658).
  - `tests/memfn/arm_fixtures.c` :1267, :1569-1590: `fd_an_make` states source MEASURED, bundle "weblog", bytes and fidelity.
  - `docs/design/memfn/window_contract.md` §3.1 (the layout's spec), memfn.h's ABI history block and memfn/include/CLAUDE.md.
  Stage 1's unit list needs a unit (say 1g, or a declared part of 1f) with its witness. Its witness is byte-identity, since no kit .c reads the source today (grep, PROBED below).

### FIX-2  The ruling names `source` and the bundle label. Rev 5 leaves their siblings `bytes`, `fidelity` and `digest` unstated, yet relies on two of them
- status: CONFIRMED (code + text)
- severity: design ; effort: one paragraph + the FIX-1 unit ; where: §The shape row 1, §The band, §pcrec-side findings
- body: `mf_prov` holds {source, bundle, digest, bytes, fidelity} (memfn.h :1223-1233).
  - **digest.** Rev 5 hands "ONE table with its digest" and puts that digest in the kit's trace "from row 1". Its only home today is `mf_prov.digest`. No kit .c reads it (grep), so the kit trace's digest is an ADDED read. That read also trips finder_check.py L(4)'s regex `\.prov\b|->prov\b` (:658, :720-727 scans memfn/src). The design must name the digest's post-stage-1 home (`mf_prov` reduced to the digest, or a field beside `payload`) and re-aim L(4).
  - **bytes and fidelity.** These are R-24's (MF_SITE_ABI 15) facts "for the kit to weigh" (memfn.h :1216-1220). For the default, `bytes` is 0 (findings.c :579: only MEASURED states bytes). For a measured bundle it is nonzero. If they stay, the kit CAN tell the default from a bundle, which breaks main's "the kit never sees the source". If they leave, rev 5's band rule ("no stated noise (an authored default, a `fidelity synthesized` bundle) means no sampling term", §The band) must be pcrec-side: pcrec states the noise, or states none. The design should say which.
  - **The added field.** The bundle sampling-noise field that rev 5 adds ("STATED by pcrec with the rates") is a new seam field in `mf_analysis`. §Noise reaches the kit lists only `mf_measure`'s noise field, so this second MF event is unlisted. Its SHAPE is also unstated: a per-byte sd cannot give a set's block-bootstrap noise, because bytes are correlated on clustered text. That means per-set noise from pcrec, which pcrec cannot know because the kit forms the sets, or replicate tables.

### FIX-3  Main declares the NONE path a member-count TIE-BREAK, "not a rate model". In today's code, and in rev 5, it is a rate model that thresholds read
- status: CONFIRMED (code). presence.c :58-62: `uniform_mass(k) = k*1e6/256` is returned as a MASS by `cube_mass`, `kit_set_mass`, `kit_set_sum` and `window_mass` when the rate is NULL. That mass is compared with absolute thresholds:
  - window.c :1596, D-hors: `kit_set_mass(rate, stop) >= COST(HORS_MIN)` with HORS_MIN 145,822 ppm (plan_cost.def :61). Under NONE this admits Horspool iff the stop set has 38 or more members.
  - MARGIN's `best*NUM < base*DEN` (window.c :669-683) over costs built from mass.
- severity: design ; effort: a declared statement plus maybe NONE rows ; blast radius: every `-e utf8` compile (blind is NONE there: `--list-analysis default` resolves byte-rate under utf8 to `none`; probe `(?i)x/1234 -e utf8` stamps `byte-rate=none` and stops on '4') ; where: §pcrec-side findings ("NULL takes the uniform-mass NONE answer ... arithmetic, no table"), §Staging 1b (U4 "the NONE-mode total (62,500)")
- body: main (7f55a62f9): "With NO rates handed, the kit's rules rank sets by MEMBER COUNT (a uniform mass), declared as the rules' own tie-break, not a rate model." Rev 5 neither declares the rule nor scopes which readers may treat the uniform mass as a density. Two readers do today: the HORS_MIN threshold, and MARGIN's ratio of NONE-mode costs (the step-4 "No rates handed: keep" is not reached there). If the ruling means "ordering only", unit 1b (U4, the one mass primitive) is where it lands. It needs:
  - a declared NONE row (rank by member count);
  - either a statement that HORS_MIN and MARGIN keep reading the uniform mass as today's answer (a named exception with a trigger), or NONE rows for them, which may be a unit change, not a no-mover.
  - The sibling: pcrec's own NONE answer (`pcrec_find_set_mass(NULL, ...)`, findings.c :606/:814, D126 Q4) is the same arithmetic. It needs the same declaration or a pointer.

### FIX-4  `art->consulted` is not a "purity breaker today": it has no writer. Its fence "taken call only" has no named mechanism, and it does not match pcrec's union rule
- status: CONFIRMED (grep: memfn/src writes `art->consulted` nowhere; it is only read at compose.c :1303; finder.c :378/:862 "never at B1 ... the first one that does is B4's")
- severity: doc (list) / design (fence) ; where: §A-PLAN open points (d), §Staging 1d
- body:
  - **The list.** (d) is a FUTURE breaker (T-PICK's rows, rev 3 C7). Today `_MEASURES` is "" because nothing sets it, which agrees with §What moves.
  - **The fence.** "Counted on the taken call only" needs the kit to know which call is taken. For REACH this mechanism already exists and holds: `gate_tctx.quiet`. gate.c :943/:956/:978 return early when quiet, so reach is counted on non-quiet walks only. `mf_wdecide` decides with quiet = 1 (window.c :1070). Rev 5 should name `quiet` as the probe mode, and give `consulted` the same rule (set only on a non-quiet decision), rather than leave it unnamed.
  - **pcrec's rule.** pcrec ORs `consulted` over EVERY attempt and every compound part (memfn_stamps.c :275-286: "the artifact's bytes depend on all of them"). The fence must say that "taken" means taken by a define, and that every attempt's define still counts. Otherwise the kit-side and pcrec-side rules disagree on the measures stamp.

### FIX-5  Reach-counter readers: rev 5 names `reach_print` and rows_check.py and misses run_g2.sh, run_g2_gate.sh and the trace spec
- status: CONFIRMED (grep for `MFTRACE REACH`)
- severity: maintenance ; where: §A-PLAN open points (c)
- body: the counters at gate.c :850-856 reach artifacts through `reach_print` (:884-907). Other readers:
  - `memfn/tests/run_g2.sh` :986-1024, the per-ROW floor (4b). These are the "reach floors" of rev 5's own §Staging witness.
  - `memfn/tests/run_g2_gate.sh` :144 (`precheck_assign_byte` chosen).
  - `memfn/docs/trace_format.md`, the format's spec.
  - rows_check.py's equation (2) ("each fd row's `asked` EQUALS the number of FD phase=ask records", :70-84). It holds only while trace records and counters are fenced together, so 1d must fence both or neither.
  Today's counts do not move (`mf_wdecide` is already quiet).

### FIX-6  The rate-source table has 3 rows. The code has a 4th outcome: REFUSE (rule 9)
- status: CONFIRMED.
  - Repro: tests/findings/e1_fixtures.py's `l1none` bundle (copied to FIX/L1/l1none.rxt). Run `build/pcrec -p rx -e utf8 --analysis l1none -I FIX/L1 -o t.c --pattern 'x/1234'`.
  - Observed: "pcrec: analysis 'l1none': its 'cpfreq' block at line 2 counts nothing via encode-latin1, ..." and the compile fails. The same holds on 8 of 8 patterns. Blind `-e utf8` compiles succeed (`byte-rate=none`).
  - Expected by the table: row 1 ("an `--analysis` chain answers byte-rate for this encoding -> that bundle") or a fall to row 3.
- severity: doc (contract) ; effort: one row ; where: §pcrec-side findings table (and main's D186 add. 2 list (1)-(3))
- body: the code (findings.c :286-330, :500-516 T-KIND `underivable-arrives`, window_contract §3.3 rule 9) says: when a chain answers but cannot derive, the compile is REFUSED iff the kind is CONSULTED. The offer states PRESENT + PRIOR_NONE with no payload, so `kit_byte_rate` returns NULL and the kit computes the NONE answer.
  - Rev 5's table should carry a first row: "a chain answers underivably -> refuse on consult (rule 9)". Main's ruling text omits it too.
  - Related (SUSPECTED): "consulted" for the `_FINDINGS` stamp and for rule 9 is pcrec's own asks only (memfn_stamps.c :264-270 `ks_consulted` = `pcrec_find_asked` and its unions). The kit reports a consult only for measures (`mf_art_end`'s one uint8).
    - Correctness today rests on pcrec MIRROR asks: emit_dfa.c :4783-4791 "asks the byte-rate, for exactly the population prefix_k's selection asked it", and facts.c :327. memfn_stamps.c :385 still says "no routed kit row consults a kind yet", which is false since `decide` reads `kit_byte_rate` (window.c :991).
    - known.c's cover site (:462-481) has no mirror ask of its own.
    - Rev 5 adds rate readers (every priced row; the priced incumbent at all six scenarios) and no unit that makes the kit report a rate consult. Nor does it add a check that the mirror covers every plan call.
    - To confirm: a census of compiles whose kit trace shows an A-mass or T-PICK read with `ks_consulted` lacking the byte-rate bit. That is a sweep, more than 50 compiles: not run. My spot checks (8 byte + 8 utf8 patterns) all had the mirror ask.

### FIX-7  "With data" proof, step 1: the candidate set is defined relative to the incumbent, and the incumbent reads rates
- status: CONFIRMED (text + code: KEY's A-mass and M's MARGIN read `d->rate`, window.c :421/:470/:552/:774; witness.out: the default arm's incumbent is {X,x} blind and '4' with prose)
- severity: design ; where: §The pick 1, "Why the structure gives it", "NOT covered"
- body:
  - Step 1 says the candidates "differ from the incumbent only at the row's levels, built from site facts alone (no rate input), so a blind and a with-data compile of one site see ONE candidate set". The incumbent is rate-dependent at the position level (KEY) and the alternative level (M), so the two candidate sets are equal only where inc_P and inc_B agree outside the row's levels.
  - The proof's parenthetical admits this. But the "NOT covered" clause names a different population: "sites no priced row admits". The gap: sites a row ADMITS whose incumbents differ outside its levels, e.g. a position-level row at a two-alternative site where MARGIN flips PARKED/RESEED between P and B.
  - Row 1 is safe: its class is one NONE alternative (291 sites), so there is no M choice. Later rows are not ("RESEED at any set size").
  - Fix: either define candidates as "every plan over the row's levels × the incumbent's OTHER levels under every rate source", or add this population to the NOT-covered census and to the property's (iv). Also drop "no rate input" from step 1.

### FIX-8  The new tie rows contradict D176 Q5's "decided by the EXISTING declared tie rows". Ties between qualifiers have no assigned row except at the method level
- status: CONFIRMED (text; window.c :75-104: `wf_tie_to` has no TIE_DEFAULT; every row breaks a tie of EQUAL MASS by offset)
- severity: design ; where: §The pick 3, §The tables (TIE)
- body: D176 Q5 (main): "prices within the measurement-noise band tie, decided by the existing declared tie rows".
  - Rev 5 adds T_BAND -> TIE_DEFAULT, a new row with a new target. It also says "the method-level tie row is row 1's design item".
  - Qualifiers that tie within band can differ in POSITION and METHOD at once. smp20's two candidates are {X,x} PAIR @0 and '/' memchr @1. No existing row compares two such plans: T_MASS_SET/T_MASS_STRETCH are keyed by equal mass at a set or stretch position.
  - The design should say that Q5's "existing rows" is amended (an owner/manager line), or map each level's tie to a named row. That covers position (offset rule by span kind), alternative (T_MARGIN's PARKED) and method (new).
  - T_BAND belongs to the MARGIN family (see below).

### FIX-9  Rev 5's lists of open items are stale against main 7f55a62f9, and stage 2's card list contradicts main's [MEASURE-SET] row
- status: CONFIRMED (main's plan.md row [MEASURE-SET] and D186 add. 2)
- severity: doc (plus a consequence for stage 2) ; where: §What moves, §Owner rulings "For main", §Cost cards, §Staging stage 2
- body:
  - (a) "M2's order"/"M2-dark: PENDING-RECORD" are now RULED on main: "M2 is NOT ordered against span_pick's row 1 ... priced rows go DARK on bare compiles ... INTENDED".
  - (b) "the byte-rate default's log line"/"log form PENDING-RECORD": main rules that "its log is filed with the first such change".
  - (c) Main's [MEASURE-SET] `next:` names the stage-2 cards as "memchr, two-stream pair, walk, verify; Horspool-probe later". Rev 5's stage 2 measures `hors.probe`, `find.hit(hors)`, `enter` and `memchr-back` too. A consequence for rev 5's own rule: with the Horspool cards deferred, every D-hors incumbent is UNPRICED, so §The pick 4 "Unpriced incumbent: keep" freezes those sites. The design should state that.
  - (d) Main's "smp20 blind keeps {x,X} (correct under the default)" against rev 5's forecast "the cards may land above k* and move blind to '/'". Not a contradiction in substance (either is "the default's"), but main's sentence reads as a prediction that rev 5 shows may fail. Flag it for main's wording.
  - (e) Main keeps the "Minimax is PAIRWISE against the incumbent" line live, "within one rate source". Rev 5 calls it SUPERSEDED. Within one source, the kinds collapse to one and the pairwise rule IS §The pick 3's qualifier test. Rev 5 should say "reduced to" rather than "superseded", or main should strike the line.

### FIX-10  The finder_check L(4) control will go red at row 1: it varies rates and provenance together
- status: SUSPECTED (confirm: row 1's T-PICK on an `fd` site with the L fixture)
- severity: maintenance ; where: §Staging row 1 witness list; finder_check.py :728-740
- body: L(4) asserts that sites `set10`/`byte1t` render byte-identically with NO analysis object and with `fd_an_make`'s object. That object carries a degenerate byte-rate payload (all mass on byte 0, arm_fixtures.c :1569-1590), so the check also asserts "no fd row reads the RATES".
  - When a priced row prices an fd site under the handed rates, the control moves. That is correct behaviour reported as red.
  - The fix doubles as the purity check main's ruling needs: hold the rates fixed and vary only source/bundle/bytes/fidelity. Then "the kit never distinguishes a bundle from the default" becomes a check that can fail.

### FIX-11  Cite drift (minor)
- status: CONFIRMED ; severity: doc ; where: §pcrec-side findings
- body: "memfn.h :1212" is `#define MF_ANALYSIS_LIST_V`; the `mf_prov_source` enum is :1213-1214, `source`/`bundle` :1224-1225 (correct). "findings.h :300" is the comment; the declaration is :303. compose.c :882's comment "no row reads it before B3a" is stale: `kit_byte_rate` reads `art->an` (window.c :991, presence.c :155). It is no cite of rev 5's, but stage 1d touches that line.

## PROBED-AND-HELD

- **Kit sees no source today:** grep of memfn/src for `prov.|->prov|MF_PROV_|MF_FID_|fidelity|mf_akind`: zero reads. `kit_byte_rate` (presence.c :48-56) reads `tag`, `present` and `payload` only. No built-in or fallback rate table in memfn/src. Rev 5's kit-grep claim HOLDS.
- **pcrec's resolution matches rows 1-3 for the byte encoding:**
  - `--list-analysis default`: byte-rate byte -> default `1822fb973b95a4da`, utf8 -> none.
  - Stamps on 4 arms x 4 sources (witness.out) and on my own compiles: `byte-rate=default:1822fb...` (byte) and `byte-rate=none` (utf8).
  - Shipped bundles move no blind compile (pcrec only reads them when named). HOLDS.
- **Purity breakers (a)-(c) cites:**
  - window.c :1062 (err), :997/:1007/:1734/:1818, finder.c :930, ofsskip.c :486 and compose.c :268/:281 are all `art->nsites + 1` labels, trace-only (gate.c :936).
  - gate.c :850-856 statics; runcmp.c :515 `wused & ~wemitted`; ofsskip.c :565-567 `simd_inc`.
  - 13 of 13 cites say what rev 5 says. Other art writes (`words`, `includes`, `libc`, `reach_row`) are emitting-face or harness-only; `levers`/`reach_stem` are refused after the first define. C3's scoping to the plan call HOLDS.
- **Reach is already quiet on the plan call** (gate.c :943/:956/:978; window.c :1070 `decide(..., 1, d)`), so 1d's reach fence moves no count today.
- **The incumbent rule (§The pick 2):** smp20 incumbent '4' under prose and {X,x} under the default (witness.out, 16 lines). `-e utf8` blind gives NONE and stops on '4' (my compile). "Its NONE answers when none handed" matches the code.
- **The qualifier logic (§The pick 3):** under one model, cheapest-qualifier-else-incumbent never picks a non-qualifier, and a never-qualifying candidate cannot move the pick. The proof's two cases (c_P qualifies / does not) are algebraically sound where c_P is in B's candidate set (FIX-7 is the exception).
- **smp20 table arithmetic:** 144,694 < 153,476 (hit 20), 166,634 > 153,476 (hit 40): 1.086x. weblog 434,532/302,235 = 1.438x. Both HOLD.
- **Rulings that agree with rev 5:** minimax struck; D186 over D144 item 3; C9 (SIMD row, scalar bar, utf8-lead witness); one plan with trace; pure function over (site facts, frame, set, rates); witness passes on '/' or '4'; O3 WAIT; `zen4-grid3`; flat guard dropped on a random-like regime in every row's evidence (Goal 2, §Robustness, §Staging, §Measurement regime all carry it).
- **Compiles:** 30 single compiles, no sweep.

## Sibling and general form

**Sibling 1: the handed-fact resolution family.** Rev 5's rate-source table is the third member of a family pcrec already runs twice:
- (a) the measurement set: `--measures=NAME`, else `DEFAULTS`, else at M2 the idk envelope that "prices nothing". Handed as `mf_measures`, stamped `_MEASURES id@rev:digest` iff consulted. The consult is reported BY THE KIT (`mf_art_end`).
- (b) the byte-rate: `--analysis`, else the per-encoding default, else NONE, with REFUSE on an underivable consulted answer (FIX-6). Handed in `mf_analysis`, stamped `_FINDINGS byte-rate=src:digest` iff consulted. The consult is reported by PCREC'S MIRROR ASKS only.
- (c) `run-rarity`: the same T-KIND rows, ABSENT today.
- (d) the analysis chain itself: `pcrec_find_chain_answer`, first link that serves.

**General form:** per compile and per kind, a first-match table (caller's explicit choice -> per-(encoding|target) default -> NONE, with an underivable answer refusing on consult) yields (payload, digest). pcrec stamps (source, digest) iff consulted. The kit receives (payload, digest), never the source, and reports which kinds it consulted.

**Unlocks:**
- (i) ONE consult channel: `mf_art_end` returns a per-kind bitmask (PCREC_FQ_BIT shape) beside the measures bit. That retires the mirror asks (emit_dfa.c :4790's "for exactly the population" contract, facts.c :327), and makes rule 9 and the `_FINDINGS` stamp true for kit-only reads (FIX-6). Trigger: the first priced row reading rates, or now (a simplification).
- (ii) The provenance removal (FIX-1) and the noise field (FIX-2) land as one seam reshape: `mf_akind` = {tag, version, present, digest, payload, noise}.
- (iii) A future kind (run-rarity, a cpfreq kind for UTF-8, a per-target measures kind) joins by adding a T-KIND row, not a mechanism. Trigger: the first kind with version > 0 beside byte-rate, e.g. [SPAN-PICK-UTF8]'s per-encoding prior.

**Sibling 2: "depart only beyond the incumbent's band" (hysteresis).** Members:
- compile time: MARGIN (a RESEED wins at < 1/2), T_BAND -> TIE_DEFAULT, §The pick 3's qualifier test, `pcrec_landmark_margin` (+ `LMWALK_K_HIT_UNMEASURED`), and the HORS_MIN admission threshold, which is a fixed-margin admission against the incumbent D-one;
- evaluation time: D186's own bar (movers new/old <= 1 + A/A floor), the batch gate, and [BENCH-WITHDATA]'s same-or-better.

**General form:** depart(reference, challenger, price, uncertainty) = price(ref) - price(ch) > k·σ. Its four parameters are the incumbent, the price model, the stated noise (cards + sampling) and the coverage factor k.
- Rev 5's E2 unifies the compile-time members at row 1 (trigger: the `enter` cards).
- **Unlock:** use the SAME declared rule for the evaluation side. Then the predicted-vs-measured print (R5.3) compares like with like: a row's predicted departure and its measured mover are judged by one formula with σ_pred vs the A/A floor. A measured k (from row 1's predicted-vs-measured spread) replaces the UNMEASURED coverage factor. Trigger: row 1's evidence run.
- The NONE answer (FIX-3) is the family's degenerate member (no price: keep), and should be declared as such.
