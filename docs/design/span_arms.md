# Span arms: the REP, EMPTY and positive-LOOKAROUND arms of the one fixed-width description

**Status: rev 3.3, L1 BUILT** `[REV 3.3]` (lane l1ffix, opus, 2026-11-19: L1 as built after review r55
(`docs/dev/reviews/2026-11-19-r55-l1feat.md`, FIX-NOW A-I applied, DOC items here) and the D27 witnesses' five
findings; also review r53's owed DOC items F2, F5, F11, F13; the record is §14.8, and each amended passage carries a
`[REV 3.3 ...]` marker pointing at it; L3 and L2 text unchanged). Rev 3.2: **PROPOSED rev 3.2** `[REV 3.2]` (lane spanarms9, sonnet, 2026-11-18: applies the manager's rulings on the confirm critic of rev 3.1, `/var/tmp/pcrec-pcrec/scratch/conf-spanarms8/findings.keep.md` (conf-spanarms8 D1-D4); text only; each changed passage carries `[REV 3.2, conf-spanarms8 Dn: ...]`; D1 the `zero` arm's facts (§14.3 D-1), D2 the head-rule remodel named in §14.0 and D-10, D3 the BACK row's `++ rg` clause in the L2-first order (§14.4 L2, §8), D4 §14.5's durable pointer). Rev 3.1: **PROPOSED rev 3.1** `[REV 3.1]` (lane spanarms8, opus, 2026-11-18: applies every finding of review r51,
`docs/dev/reviews/2026-11-18-r51-spanarms7.md`, AS RULED by the manager that day; each changed passage carries
`[REV 3.1, review r51 <id>: ...]`; §14 stays the design of record for L1, L3, L2. Verdict as ruled: all three units
READY WITH THE LISTED TEXT FIXES; none builds before a confirm critic has checked this revision, and L3's answer/safety
fixes READYL3-1, -4, -6 gate its build). Rev 3: **PROPOSED rev 3** `[REV 3]` (lane spanarms7, opus, 2026-11-18: the lookaround units L1, L2, L3 re-based on the
ACCEPTED architecture note `docs/design/req_lookaround_arch.md` rev 2.1 and the tree at main `8993b8f82`; their design of
record is §14, and every rev 2.2 passage §14 replaces carries an inline `[REV 3: ...]` marker; E1, R1 and E2 are BUILT and
untouched). Rev 2.2: **PROPOSED rev 2.2** (lane spanarms6, opus, 2026-11-08; design and single-pattern
measurement only, no build go). Rev 2.2 applies the L2/L3 findings READY2-1..7 and READY3-1..9 of
review `docs/dev/reviews/2026-11-08-r4-spanarms5.md` as RULED in its "Manager rulings
(2026-11-08)" section. No verifier ran in that round, so every finding was re-checked before its
text changed (HOLDS / REFUTED / PARTLY in §R4, evidence `docs/dev/lanes/spanarms6_evidence/`, the
lane's own build of `1ffcce0c1`). It changes L2/L3 text only (§5.2's TOP row, §5.4, §5.6's L2/L3
rows, §5.7's L2/L3 witnesses, §8's L2/L3 rows and the new §8.1-§8.2, §9, §12's D-next, §13);
the disposition table is §R4, and changed text is marked `[r4 READY2-n]`/`[r4 READY3-n]`. L1, E1, R1 and E2 text is rev 2.1's,
unchanged. Rev 2.1
applies the L1 text fixes READY-1..10 of review `docs/dev/reviews/2026-11-08-r3-spanarms3.md` as
RULED in its "Manager rulings (2026-11-08)" section, and changes L1's text ONLY (§5.1, §5.2's
L1 rows, §5.7's mechanism sentence and L1 witnesses, §5.8, §8's L1 row, §9's L1 rows, §11 point
2, the §12 D168 addendum, §3.7's `look` cell); the disposition table is §R3, changed text is marked
`[r3 READY-n]`. L2 and L3 text is rev 2's, unchanged. Rev 2 (lane spanarms3, opus, 2026-11-08; design
and single-pattern measurement only) answers re-check review `docs/dev/reviews/2026-11-08-r2-spanarms2.md` as
RULED in its "Manager rulings (2026-11-08)" section; the disposition table is §R2, and changed
text is marked `[r2 Sn]`. Rev 1 (lane spanarms2) answered review 2026-11-08 r1 (§R1, `[r1 Fn]`).
Rev 0: lane spanarms, main `7b9ddd890`.

**Rev 2.2's base: main `1ffcce0c1`.** Every rev 2.2 cite was read at that base; the r4 critics
found no cite moved between `c054e38e7` and `9161402da`, and `1ffcce0c1` adds design text only.

**Base: main `c054e38e7`.** `git diff dd2fe2de9 c054e38e7` over `src cli lib memfn docs/spec tests`
is empty, so every `file:line` this note cites holds at rev 0's, rev 1's and rev 2's bases. Rev 2's
measurements: `docs/dev/lanes/spanarms3_evidence/` (the lane's own build of `c054e38e7`;
libpcre2-8 10.46 through `tests/lib/p2probe.c`).

Plan rows: [REPEAT-RUN], [REQ-EMPTYCAT] (its quantified half), [REQ-LOOKAROUND]. Parent note:
`docs/design/alt_normal_form.md` (§3.5's arm table, §3.6, §9 rows S2-S4, and §10's "the follow-up
notes ... decision points listed, not decided" are what this note decides). Next in Frank's
2026-11-06 order: [REWRITE-ADJ], after this note settles.

**Readiness, as ruled.** The REP + EMPTY half (units E1, R1, E2) was READY WITH TEXT FIXES at r1;
rev 1 applied them. At r2, E1 and R1 needed nothing more, and E2 takes S16's sentence and witness
(§4.1, §4.5) before its go. The LOOKAROUND half: the rules were found sound (two exhaustive
populations, zero unsound runs); the text was not buildable. Rev 2 closes it. As ruled, L1 gets
ONE readiness critic over the re-spelled witnesses (no full round), and L2 and L3 get a readiness
critic each before any go.

Evidence: rev 0's `docs/dev/lanes/spanarms_evidence/`, plus rev 1's
`docs/dev/lanes/spanarms2_evidence/`: `oracle.out` (every expected answer rev 1 adds, libpcre2-8
10.46 through `tests/lib/p2probe.c`, driver `or.sh`), `facts_today.out`/`facts_extra.out`
(today's facts and stamps of every witness, `build/pcrec` at `dd2fe2de9`, driver `facts.sh`),
`spell.out` (the spelled equivalents), `span_decline.out` and `nested_lb.out`. "Measured" means
one of those files. "Predicted" means the spelled-out equivalent was measured. "Hand-derived"
means the rule was applied by hand; rev 1 uses it only where no spelling is equivalent, and says
so.

The note's one claim: **each arm is ONE rule over the description, stated as a language identity
or as a placement of one fact, so its soundness is the CAT arm's soundness and nothing new**:

- REP: `X{m,n}` IS `X^m · X{0,n-m}` and IS `X{0,n-m} · X^m`; `X^m` is m copies through CAT.
- EMPTY: a node that consumes nothing contributes the WIDTH-0 UNIT of CAT. `[r1 F16]` Rev 0's
  EXACT/GUARDED split had no reader and is gone from every rule.
- positive LOOKAROUND `[r1 F1, F2, F15]` `[r2 S2, S8]`: the width-0 unit plus the lookaround's
  ITEM: the subject's EXACT per-offset sets at signed offsets from the cursor, as D168's ONE
  context producer states them (§5.3). That covers both lowerings of a positive lookaround, the
  `A_LOOK` sub-match and the one-character `A_CTX` the `ctx-node` row makes. The run is a READER:
  it derives its own cube hull of the item within `pos_set` and carries it as PENDING GUARDS on
  the run value. `rr_cat` meets them against its neighbour, carries them across an `all`
  neighbour and drops them anywhere else. Only the top level decides whether a guard extends the
  run past the attempt's consumed span, and that is the reach the readers admit.

## §R4. Disposition table (every finding of review 2026-11-08 r4, as ruled; units L2 and L3)

No verifier ran in r4, so each finding was RE-CHECKED before its text changed: HOLDS (the finding
is right as stated), PARTLY (right in part; the part that is not is named), REFUTED. Evidence:
`docs/dev/lanes/spanarms6_evidence/` (`facts_r4.out`, `facts_tw.out`: the lane's `build/pcrec` at
`1ffcce0c1`; `oracle_r4.out`: libpcre2-8 10.46 through `tests/lib/p2probe.c`). "Read" means the
cited code was read at `1ffcce0c1`. No plant was re-run (no source edits in this lane); where a
critic's plant is the evidence, the re-check is the code reading plus the spelled measurement.
Rulings file entry applied: R1 (the W-T2/W-T3 arithmetic, below).

| finding | ruling | re-check | what rev 2.2 changed | where |
|---|---|---|---|---|
| READY2-1 W-T2 cannot fail at default flags | FIX-NOW | PARTLY. HOLDS that it cannot fail at default flags. REFUTED that it fails under `--memfn=no-fd-pres-pick`: with the corrected keep-last value `a^12 b^20` (READY3-1's arithmetic; rulings R1) both spellings list the window `6262626262626262@7` at K 24, and the flag adds only a whole-run PRESENCE test from `search_from` (`rx_reqrun_whole`, read in the emitted C of `x a^12 b^20`), which the sabotaged run passes (it is a substring of `a^20 b^20`). The critic's plant grafted a K-0 handoff from the whole run, which no build emits | W-T2 is a `req_whole_run` LISTING row only; the new answer witness W-T2a `a^20(?=b^5 z b^14)` moves the WINDOW's K (its consumed positions hold the one `z`); §5.7 condition (5) | §5.7, §8 L2 |
| READY2-2 the scan member is the kit's reply (L2 blocker) | FIX-NOW (ruled: a facts request; one decision) | HOLDS (read: `req_run_member` `emit_dfa.c:1058-1076` compares the kit's `run_member`, verify YES = least mass of ALL window positions, `window.c:855-890`, with `r->idx` and fails loudly; every reader goes through it, `:1102`, `:1222`, `:11050`, `:11229`, `:15831`, `:15859`; the spelling `barbaz` lists the member at 5, `z`, where A13 picks in `bar`). STOP RULE not met: the blocker stands | §8.2 part A: the consumed extent stated on the window and the presence span as a fact; the member is the KIT's one decision; pcrec states the whole run once, reads the kit's member, cuts its window around it, and every reader reads the reply; A1, A13, the closing paragraph, §9's two rows | §5.4, §8.2, §9, §12, §13 Q7 |
| READY2-3 W-S4b's check does not hold the witness | FIX-NOW | HOLDS (grep: `reqcube_check.py`'s `WIT` holds no lookaround pattern) | L2's gate ADDS `bar(?=baz)` to `WIT` | §5.7, §8 L2 |
| READY2-4 the trigger names a benefit A13 forbids | FIX-NOW | HOLDS (read: `pcrec_req_window` cuts the window around the member, `req.c:841-852`, `findings.c:780`; under A13 the member is consumed) | the trigger names the compare's false-candidate rate; Q4 states the leaning's cost | §8 L2, §13 Q4 |
| READY2-5 L2's spec-hunk list | FIX-NOW | HOLDS (read: tuning §2.28¶1 "every match must contain"; `findings.md` §4's member row "the window's truncation keeps pcrec's own index"; match_api §6.3.7¶4, ¶5, ¶7 stay true under A13) | hunks ¶6, tuning §2.28¶1 (L2 owns the run's definition, L3 the bit-31 sentence), findings.md §4's member row; ¶4, ¶5, ¶7, ¶11, §2.27¶4 CHECKED-UNCHANGED | §5.4 A7, §8 L2 |
| READY2-6 AHEAD removes the run pin | FIX-NOW (the pin reads `cons`) | HOLDS (read `kset.c:294-318`; measured `bar(?=baz)`: `run_pin 0`, `run-pinned`, `dominated`, k-set 3 positions) | `pcrec_run_pin` reads `cons`; the pre-check's WHY moves `dominated` → `emitted` (`ofs_test_verifies_run` asks every window position), a listed mover | §5.4 A5, §5.6, §8 L2, §9 |
| READY2-7 L2/L3 dependencies | FIX-NOW | HOLDS (measured: `a{20}` has no run today) | W-T2's listing row waits on R1; W-T2a (literal) does not; L3 depends on L2's `cons` or builds it first; one kit request for both | §8 L2/L3, Order |
| READY3-1 W-T3 cannot fail | FIX-NOW | HOLDS (the spellings `a^20 b^12`/`a^12 b^20`: the same window and K, measured; presence-only flag, read) | W-T3 is a listing row; the answer witness W-T3a `(?<=a^20)b^8 z b^11` (with `y` the prior picks a uniform `b^8` window, measured, so the rare byte is `z`); the `a^8` slip corrected to `a^12` in both rows | §5.7, §8 L3 |
| READY3-2 the margin's unsigned cast; the re-entry move unreached | FIX-NOW | HOLDS (read `emit_dfa.c:9057-9063`: a negative K casts to ~2^64, margin −1; `lmwalk.c:248` passes a non-negative K; the kit's twin `presence.c:199-222` reads `head_max` unsigned) | A3 names the margin and its cast; the admission reads `max(K, 0)`; the kit is told the fact (§8.2 part B); the re-entry move's reaching witness is W-L14 (through READY3-4's admission) | §5.4 A3, §8 L3, §8.2, §9 |
| READY3-3 K is `omin + at`, of either sign | FIX-NOW | HOLDS (the spelling `e^15 qzx`: window at `at` 10, so K = 0 at L3; oracle `(?<=e{10})eeeeeqzx` (10,18) from 0/5/10, N from 11/12; the K > 0 twin `(?<=e{8})eeeeeeeeeeqzx`: K 5 today and at L3, oracle (8,21) from 0/8, N from 9, 13, 14, 15) | K = `omin + at` in TOP and A3; `req_run_omin` is the whole run's; W-L11 (K = 0) and W-L12 (K > 0, the wrap) | §5.2, §5.4 A3/A9, §5.6, §5.7, §9 |
| READY3-4 A8's decline is a default-flags mover | ADMIT (ruled) | HOLDS (measured: `(?<=foo)bar(\w)\1` `RX_REQ_HANDOFF "0"`, `RX_VM_PREFILTER "none"`; `(?<=foo)bar` and `(?<=ab)ab[a-z]*q` under `-fno-prefilter`: `"0"`; oracle `foobarxx` (3,8) from 0/3, N from 4) | the decline is deleted; both attempt-loop rows run A3's move; mover `"0"` → the signed K; spec hunks tuning §2.41¶8b, match_api §6.3.7¶11; W-L13 (entry row) and W-L14 (re-entry row), both oracle-checked | §5.4 A8, §5.6, §5.7, §8 L3, §9, §12, §13 Q3 |
| READY3-5 A10 needs no change | FIX-NOW | HOLDS (read `facts.h:88-89`, `facts_derive.h:114`, `req.c:853`) | A10's BACK cell "yes, already signed"; A10 leaves L3's changed list | §5.4 A10, §8 L3 |
| READY3-6 L3 needs `cons`; no BACK A13 witness | FIX-NOW | HOLDS (the spelling `qzab` lists `req_byte 122`; `(?<=qz)ab`'s `req_set` is {97,98}, measured) | L3's depends-on; W-S4c with `(?<=qz)ab` ADDED to `WIT` | §5.4 A13, §5.7, §8 L3 |
| READY3-7 the A-POSDOM cell undecided | BUILD NOW (ruled) | HOLDS (`[DEC-POSDOM]` `STATE:not-started`; A-POSDOM's prerequisite A-SEAM; its next step is the call-site table; L3's sites `emit_dfa.c:1175`, `:7799` are ROUNDUP calls) | §8.1 states L3's two sites in that table's shape (site, mode, the hand it guards) and the kit's floor as a non-pcrec site; no new mode, R08 does not grow | §8 L3, §8.1, §13 Q8 |
| READY3-8 sentinel sites; `head_max`'s none bit | FIX-NOW | HOLDS (grep: `facts.c:104`, `:840`; `pcrec_fact_req_run_maxoff` declared in `facts.h:568`, no caller outside `facts.c`) | §9's sentinel row lists every site; the stated/none bit is for K only; `head_max`'s none state is the kit's `handoff` field, stated in §8.2 | §5.4 A9, §8 L3, §8.2, §9 |
| READY3-9 five L3 witnesses are `dominated` today | FIX-NOW | HOLDS (measured: S-L/W-L1, W-L3, W-L10, W-T3 `"dominated"`; W-L8 `"emitted"`) | §5.7 records today's WHY; condition (6): each L2/L3 gate row checks `RX_REQ_WHY "emitted"` and its HANDOFF before its plant counts | §5.7, §8 L2/L3 |

## §R3. Disposition table (every finding of review 2026-11-08 r3, as ruled; unit L1 readiness)

| finding | ruling | what rev 2.1 changed | where |
|---|---|---|---|
| READY-1 W-T1 cannot fail on the answer at default flags | FIX-NOW | §5.7's mechanism gains the fourth condition (the difference lies inside the emitted window, or the gate tests the whole run). W-T1 is checked under `--memfn=no-fd-pres-pick` (`_reqrun_whole`) and is a listing row on `req_whole_run`; the sabotage's empty meet lists the live pattern dead, so W-D7 lists it NOT dead. Every other L1 witness re-checked against the window: runs of at most 8 positions are tested whole. Observed at the main tree's `build/pcrec`: the flag is accepted, and the emitted C contains `rx_reqrun_whole` (0 occurrences by default, 5 under the flag), while `RX_REQ_RUN` stays the 8-position window | §5.7, §8 L1 |
| READY-2 `x(?!foo(?=bar)baz)y` cannot fail | FIX-NOW | W-D5 is a structural note (no body walked, no plant site), not a witness | §5.2 (g), §5.7 |
| READY-3 W-S4's check does not hold the witness | FIX-NOW | L1's gate says `x(?=qr)[pq]r` is ADDED to `reqcube_check.py`'s `WIT` list (and `bar(?=baz)` for L2's W-S4b); a BUILD-time edit, the script is not touched here | §5.7, §8 L1 |
| READY-4 the `-fno-ctx-node` equality is vacuous on W-C1 | FIX-NOW | §5.1, §11 point 2 and the L1 gate name the rows on which the equality can fail (`a(?=b)[bc]` at listing level, `ab[xy](?=(?<=x)y)[xy]`); W-C1's own plant is the PREV-as-NEXT plant | §5.1, §5.7, §8 L1, §11 |
| READY-5 the listing hunk is under-stated | FIX-NOW (the manager's form) | `dead` and `harness:<source>` are WHY VALUES, one per run, first match `dead` > `harness:` > the existing reasons; no second field; which facts carry them is stated | §3.7, §5.2 (g), §8 L1, §9 |
| READY-6 the D168 addendum leaves members homeless | FIX-NOW (the manager's form) | the addendum says the producer's members, its widening and its bound, in three sentences; the `\b` fold and the negative lookarounds are named NOT members (zero-width cuts, the EMPTY/E2 arm's) | §12 |
| READY-7 reader census incomplete, one cite wrong | FIX-NOW | A12 gains `fd_why` and `pf_done_why` (and the status of a dead run: `derived`); `dead` vs `decline:dead-start` in one sentence; `pcrec_req_walk`'s prototype added to the ledger; `cli/main.c` cites corrected; `harness:` is visible only from `build/pcrec-harness` | §5.4 A12, §3.7, §9 |
| READY-8 S-L missing from §8's L1 gate | FIX-NOW | S-L added | §8 L1 |
| READY-9 `look` overlaps `zero` | FIX-NOW (PARTLY; one cell) | `look` restores "E-5 as E2's plain unit (no item, no guards), reach `[0, maxoff]`"; `zero` keeps E-4's cut, and so does not move L1's own delta | §3.7, §5.8 |
| READY-10 the two dead members have no plant | FIX-NOW | a plant per dead member (W-D1: the consumed-position EMPTY-MEET branch does not set DEAD; W-D2: the guard-vs-guard branch drops positions without setting DEAD); W-D1..W-D7 numbered | §5.7, §5.2 |

## §R2. Disposition table (every finding of review 2026-11-08 r2, as ruled)

| finding | ruling | what rev 2 changed | where |
|---|---|---|---|
| S1 A3's move at a negative K is unsound | FIX-NOW | A3 now states the only sound move, `pos = max(posvar, c − K)` with K signed and no `size_t` wrap, and the re-entry re-ask condition `c − K < pos`; match_api §6.3.7¶11's `max(startpos, that − K)` is kept and said to hold for signed K. `emit_req_handoff_rest` and `emit_req_landmark_move` are L3 sites. W-L10 `(?<=ab)ab[a-z]*q` on `abababq` from 3 (oracle M 4 7; the rev-1 move reports (2,7)) | §5.4 A3, §5.7, §8 L3 |
| S2 one-character lookarounds are `A_CTX` | FIX-NOW (decided: (a)) | ITEM reads the producer's item for EVERY positive one-sided context: `A_LOOK` positive and `A_CTX` with `CTXFN_NEXT`/`CTXFN_PREV`; every other `A_CTX` function stays E-4. The run is then the same under `-fno-ctx-node`, which the L1 gate checks. The six witnesses are re-spelled with multi-character bodies, and W-C1 is the `A_CTX` witness. §5.2 (c)/(d) and the §5.6/§5.7 rows are re-derived | §0, §2, §5.1, §5.2, §5.6, §5.7, T1, T3 |
| S3 W-L5, W-RG `cover`-dominated | FIX-NOW | both re-spelled (`xy(?=bc)[bc]c`, `(?:abc(?=ab)){2}`: VM, `RX_DFA_SCAN "unanchored"`, measured); the mechanism sentence adds "the locator is not `rev-end`/`cover`/`landmark-walk`/`empty`", and every witness row states its measured `RX_DFA_SCAN` | §3.6, §5.7 |
| S4 `req_byte` can leave `req_set` | FIX-NOW (RULED) | L1: a meet that narrows a CONSUMED position to one byte puts that byte in the necessary SET at that position's offset (row CAT-SET). L2/L3: the scan member is picked among CONSUMED positions only, read from a stored consumed extent (`RbRun.cons`, reader `pcrec_req_pick` and the scan-index pick). A guard byte is never the scan member. New row A13 | §5.2, §5.4 A13, §8, §9 |
| S5 guard bound and kept end unstated | FIX-NOW | §2: a guard is stored at the run's bound and keeps the end NEAREST the value's edge (`lg` the tail form, `rg` the head form); its `trunc` is never read; REP's saturation does not count guards. TOP: a candidate's `++` keeps the FIRST positions (`rn_app`), BACK's `t` is the STORED `lg.n`. Witnesses W-T1 (guard, L1), W-T2 (TOP, L2), W-T3 (TOP, L3) | §2, §5.2 TOP, §5.7 |
| S6 dead fact has no propagation rows | FIX-NOW | T4 has a DEAD column (CAT either, ALT both, REP `m = 0` never, `m ≥ 1` the body's, positive lookaround the body's, negative never; any empty meet, guard-guard included, states it). U-dead reads the ROOT's bit. Carrier: a `why` value `dead` on `req_whole_run`. FACT witnesses listed NOT dead | §5.2, T4, §8 L1, §9, §10 |
| S7 the BACK floor is the kit's behaviour | FIX-NOW | A2: "the kit's two uses (entry and re-entry), from the stated `omin`, clamped at 0". L3 depends on the kit HONOURING a negative presence `omin` at entry and re-entry and a signed `head_max`, with the origin re-defined as the ATTEMPT start. W-L1 is the kit's witness, planted in the kit's emitted text | §2, §5.4 A1-A2, §5.7, §8 L3 |
| S8 the F15 form | FIX-NOW (RULED) | §5.3 rewritten: ONE producer of EXACT per-offset subject sets at signed offsets (`look-fixed`'s fact), `A_CTX` and `A_LOOK` alike; the guard is a READER that derives its own cube hull within `pos_set`. The producer is the body's DESCRIPTION placed at the cursor (exact 256-bit position sets, unmoved by bit 44). L1 builds that slice and files the D168 addendum (§12); kset's `A_CTX` reading is the producer's in-span half. The coordinate reading is flagged for the manager | §5.3, §8 L1, §12 |
| S9 the lever is not one site | FIX-NOW (RULED) | §3.7 rewritten as a declared table of WALK PARAMETERS (`pos_set`, the reach, the restored-arm set; with `max_pieces` and `lb_bytes`, the walk's other inputs), two lever sources (public bit, harness), applied at the one walk entry; `facts.def`'s deny column keeps its one meaning (empty a fact, `pf_enter`); listed through a new `facts_listing.md` §4.1.3 token `harness:<arms>` | §3.7, §5.8, §8, §9 |
| S10 `lb_bytes` per encoding | DOC (RULED) | §5.5: the row's purpose is a per-call step-back COST cap (safety is not its job), stated per encoding; the "reads further back than `lb_max`" fact is libpcre2's NON-UTF behaviour only (UTF mode: `(?<=c(?<=bc)d)e` from 3 is N, measured); Q5 corrected | §5.5, §13 Q5 |
| S11 L3's spec hunks | DOC | L3's gate names match_api §6.3.7¶10/¶11, tuning §2.41¶1, facts_listing §4.1.2¶8/¶8b and the new `omin` paragraph, by paragraph; ¶11's formula kept for signed K | §8 L3 |
| S12 `omin` is a new pcrec field | DOC | ledger rows for `RbRun.omin`, `ReqRun.omin` and one `facts.def` row `req_run_omin` (sibling of `req_run_maxoff`, the house pattern of one row per offset fact) | §5.4 A9, §9 |
| S13 L1's depends-on incomplete | FIX-NOW | L1 depends on E2; on E1 for W-F4; on R1 for the REP row (without R1 the REP row is today's best-only and carries no guard). The harness source is built by the first unit built of 2a/E1/R1/E2/L1 | §8, §9 |
| S14 W-L4, W-L8 gates | FIX-NOW | W-L4 and W-L8 move to L1's gate (W-L8 stays at L3 too) | §5.7, §8 |
| S15 two §5.4 cites | DOC | A1 drops `site_kind_of` (it reads no run); A9 cites the run's bound at `facts.c:236` | §5.4 |
| S16 E2 changed beyond its fixes | FIX-NOW | one T3 sentence: E2 gives every positive lookaround (`A_LOOK` and the `A_CTX` NEXT/PREV rows) the plain unit until L1 adds its item; E2's own witness W-E3 `xy(?<!ab)cd` on `xycd` | §4.1, §4.5, §8 E2 |
| standing: walk-input family | FIX-NOW in S9 | the walk-parameter table is that family's general form | §3.7 |
| standing: signed-offset "none" sentinels | DOC | L3's gate: every signed offset (`omin`, `maxoff`, K, `head_max`) carries a stated/none bit beside it, the −1 sentinel retired in the same unit | §8 L3 |
| standing: U-exactwidth | PLAN | §10 row, trigger L1's census of guards dropped at fixed-width non-literal neighbours | §10 |

## §R1. Disposition table (every finding of review 2026-11-08 r1, as ruled)

| finding | ruling | what rev 1 changed | where |
|---|---|---|---|
| F1 the lookahead arm never sees its right neighbour | FIX-NOW | the guard is carried IN the run value (`rg`, `lg`) and met in `rr_cat` against `r.head`/`l.tail`: T4 is a set of combinator rows, not an arm rule. Witness W-L5 `a(?=b)[bc]`/`ab` | §2, §5.1, §5.2 row CAT-R, T4, §5.7 |
| F2 guard propagation unstated | FIX-NOW | one declared row per combinator: ITEM (with nested lookarounds, (d)), CAT-R, CAT-L, CAT-EDGE (stacking, (c)), ALT (b), REP, EMPTY-MEET, TOP (tail/best, (e)). No extension below the top level, so `all` never sees guard bytes (a) and no min width is needed (f). "Back never shrinks": a guard is absorbed, carried across an exact-width neighbour, or dropped (f). Each row has a witness with libpcre2 answers | §5.2, T4, §5.7 |
| F3 no witness for `maxw` from the c copies | FIX-NOW | W-R6 `(a.){10}xyz` (VM, K 20 measured) and its DFA twin `(?:a.){10}.?xyz` (K 21 measured); plant `maxw = c·w` | §3.6 |
| F4 T2 row 1 has no guard column | FIX-NOW | T2 has a guard column; a min-0 width-0 repeat drops its guard. Witness `x(?=ab)?a[bc]`/`xac` in L1's gate (rev 0's `x(?=ab)?ac` empties a position, which no reader sees, F5) | T2, §5.7, §8 |
| F5 W-E1 and W-L3 cannot fail | FIX-NOW | the run after an empty meet is stated (EMPTY-MEET: the position keeps its consumed value, the dead fact is listed). W-E1 is `x(?!ab)a[bc]`/`xac`. L1 has `[ac]b(?<=ab\|b)c`/`cbc`; `(?<=ab\|b)c` stays at L3. W-E1 leaves E2's gate (E2 has no meet site) for L1's | §4.5, §5.2, §5.7, §8 |
| F6 W-R5 equivalent mutant; saturation one copy loose | FIX-NOW | saturation is `ceil(32/w)` over the content fields; offsets come from the c-copy prefix; W-R5's plant is `ceil(32/w) − 1` copies (30 positions against 32) | §3.1, §3.6, T2 |
| F7 T2 row 2 shadows `X{0}` | FIX-NOW | row 2 deleted (a deleted special case); `m = n = 0` reaches the `m = n` row; W-R3's plant is "c from max(m, 1)" | T2, §3.6, §9 |
| F8 BACK reader census incomplete | FIX-NOW | §5.4 rows A8-A12 (handoff entry, the derivations and the −1 sentinel, the pick arithmetic, trace readers, the printers); the kit's `head_max` beside `omin`; the K sinks; the VM route's caller text. BACK changes at seven sites, not four | §5.4, §8 L3, §13 Q3 |
| F9 the BACK bound is borrowed from the wrong seam | FIX-NOW | the reach is the run's signed interval `[omin, maxoff]` from the attempt start, two existing slots. The bound is a declared POLICY row, `-omin <= lb_bytes` (`Ctx.lb_max` in the encoding's bytes). It is not an invariant: a nested lookbehind reads further back than `lb_max` (measured, §5.5) | §2, §5.5, §13 Q5 |
| F10 §5.2's reason for "no extension" is wrong | DOC | corrected: `[bc]` is a cube; the guard's second position meets no stored run position because `a.` is not `all`; rev 1 predicts `xa` | §5.6 |
| F11 `kset_walk` does not decline on lookarounds | DOC | §0 corrected; E2's census counts the window statement's R-span movers too | §0, §4.3, §8 E2 |
| F12 "the kit verifies a candidate against every span" | DOC | "the kit honours each span's verify flag" | §5.3 |
| F13 `emit_vm.c:4093` is a comment | DOC | `emit_vm.c:4177` | §4.2 |
| F14 "the match" must mean the attempt span | DOC | defined once in §2; §4.3 and the L2 spec hunk use it | §2, §4.3, §8 L2 |
| F15 D168 not cited | FIX-NOW | the guard READS D168's producer at its ITEM grain. STOP-RULE finding: the producer's signed-offset half does not exist at `dd2fe2de9`, so the item is designed as its FIRST member, and span_facts' context half becomes its second reader (§5.3) | §5.3, §10, §12 *(superseded by cover_cap.md rev 4, 2026-11-15)* |
| F16 `ahead` and EXACT/GUARDED have no reader | FIX-NOW | no stored `ahead` (L2 widens the run and the stamp sentence only); no EXACT/GUARDED rule; `exact = false` is kept on a can-fail width-0 group as a sound superset, with no reader | §2, T2, T3, §4.2, §12 |
| F17 remodel-overlap column missing | FIX-NOW + PLAN | §8 has the column (L3 against A-POSDOM and A-REV; E1/E2 against stage 2a); one fixed-tail producer is named (the description's tail affix of a subtree); the stale gate text of plan rows [REQ-LOOKAROUND] and [RUN-POS-SET] is refreshed | §5.2, §8; plan.md |
| F18 the lever fires the parent's general form without taking it | FIX-NOW (ruled: take FIX-8's form) | `facts.def`'s deny admits a HARNESS source; the restorable arms are rows of one table; the `--harness=` if-chain is filed as a PLAN member | §3.7, §5.8, §9; plan.md |
| F19 the lever rule is cited to memory; bit 31 at L3 | DOC | repo homes cited; L3 re-specifies bit 31's text (tuning.md §2.28¶1) | §3.7, §5.8, §8 L3 |
| F20 a "fact" kind D186 does not have | DOC (ruled: trigger NOT fired) | "a fact change is an INPUT to the existing choice rows, judged at the pick rows it moves, with D186's choice bar applied there" | G4, §8 |
| F21 `facts_listing.md` hunk | DOC | named in the L1 and L2 gates (facts_listing.md §4.1.2 and §4.1.3) | §8 |
| F22 W-R3/W-R4's correct run is a tie | NOTED | noted beside the witnesses | §3.6 |
| standing questions (sibling; general form + unlocks) | PLAN | the general form is §5.3; the four unlocks are filed as plan rows with triggers ([LOOK-LOCATE], [CTX-SIDES-PRODUCER], [PRES-OMIN-TRUE], [DESC-DEAD]), nothing scheduled | §10; plan.md |
| F18 ruling, second half | PLAN | the `--harness=` lever if-chain in `cli/main.c` is filed as [HARNESS-LEVERS], a member of the facts.def-deny family | plan.md |

## 0. Premise tests (main `dd2fe2de9`, all HOLD unless marked; rev 2's re-run at `c054e38e7`)

- **A one-character positive lookaround is `A_CTX`, not `A_LOOK`** `[r2 S2]` (rev 2's premise
  test). `pcrec_look_t3`'s `ctx-node` row (`src/parse/ctxnode.c:117-142`, default on, deny
  `-fno-ctx-node`) lowers `(?=C)`/`(?<=C)` with a body whose language is a set of single
  one-byte characters to `A_CTX(C, CTXFN_NEXT|CTXFN_PREV)`. Measured: `a(?=b)c` lists
  `kinds none` (`facts_listing.md` §4.1.2¶4: a context node is not a `lookaround`),
  `span_facts 0` and `RX_DFA_SCAN "empty"`; `ab(?<=b)[bc]d\w*e` lists `kinds none` and DFA, and *(superseded by cover_cap.md rev 4, 2026-11-15)*
  under `-fno-ctx-node` `kinds lookaround` and VM, with the same run (`6162`). `req.c:756-761`
  sends `A_CTX` to the same ZERO cut as `A_LOOK`.
- **The body's description holds EXACT position sets, unmoved by bit 44** `[r2 S8]`.
  `desc.h:1-13`: a description is width groups of position SETS (the byte alphabet is a 256-bit
  set). `[ab](?:bc|d)e` lists `req_pieces 3:[97,98][100][101]|4:[97,98][98][99][101]` with and
  without `-fno-req-run-fold`; the run's cube domain `pos_set` is read only by the run's own
  arms (`req.c:366`, `:381`, `:610`).

- **REP keeps only the body's best.** `rb_rep_into` (`src/facts/req.c:549-558`) builds
  `rr_none(rr_rep_w(rmax, ...))`, copies in `b->runs.best` alone and sets the description to
  `pcrec_pd_none()`, with the comment "REP{n,n} is [REPEAT-RUN]'s (§3.5)" (`:557`). The `A_REP` arm
  (`:708-740`) takes it at `rmin >= 1` (`:721`) and a gap at `rmin == 0` (`:739`). Nothing is
  joined across an iteration. Measured: `A{4}` gives run none against `AAAA`'s `41414141`;
  `xy(?:ab){2}zw` gives `ab` (2) against `xyababzw`'s 8; `ab{3}c` gives none against `abbbc`'s 5.
- **The lookaround cuts the run.** `case A_LOOK:` (`req.c:761`) falls into `rb_row_into`
  (`:637-645`), whose `KTEXT_ZERO` arm calls `rb_assert_into` (`:627-631`): `rr_none(0)`, a cut,
  and the description `pd_none`. Measured: `(?<=foo)bar` gives `bar`, `bar(?=baz)` gives `bar`,
  and `xyz(?<=yz)abc` gives `abc` (the consumed `xyz` is cut too).
- **The EMPTY arm is not built either.** `case A_EMPTY:` is in the same cut list (`req.c:756`).
  Stage 2a of alt_normal_form is census-first and unbuilt. §4 keeps 2a's direct half as its first
  row, unchanged.
- **The description module has no power or guard arm.** `src/facts/desc.h:43-47` has unit,
  none, pos, cat and alt. The adjacency head's REP arm is a WALL (`src/opt/altnf.c:223-230`).
- **The walk is right-to-left and every non-leftmost spine element gets a fresh accumulator**
  `[r1 F1]`. The `A_CAT` arm walks `a->r` into a fresh slot (`req.c:682`), and every
  `rb_walk_at` starts with `rb_init(acc)` (`:677`). So an arm sees "everything to its right" only
  when it is the LEFTMOST element of its spine. Any rule that must see a neighbour therefore lives
  in `rr_cat`, which every concatenation passes through.
- **The SPAN facts see through repeats; only `span_facts` declines on a lookaround** *(superseded by cover_cap.md rev 4, 2026-11-15)*
  `[r1 F11]`. `kset_walk` reports `A{4}` as `65,65,65,65` and is DERIVED on every lookaround
  witness: `xyz(?<=yz)abc` gives `120,121,122,97,98,99`, all six consumed bytes. `span_facts` *(superseded by cover_cap.md rev 4, 2026-11-15)*
  DECLINES (`decline:erased-nfa`) on `(?<=foo)bar`, `bar(?=baz)` and `xyz(?<=yz)abc`
  (`span_decline.out`). It states only where the recognizer made an `A_CTX` (`a(?=b)[bc]` gives
  `2:97,98`).
- **D168's producer at `dd2fe2de9`** `[r1 F15]` (the brief's premise test; §5.3 has the finding).
  `span_facts` is `MkLang` (`src/facts/facts.h:286-292`): `S_d` at offsets `d >= 0` from the match *(superseded by cover_cap.md rev 4, 2026-11-15)*
  start only. The context half (`MkCtx`, per-item terms at negative offsets and past the end,
  `docs/design/ctx_span.md` §3.2) is designed and not built ([DD-11.5] part 1, P1a/P1b). `grep -n
  'nctx\|MkCtx' src/facts/facts.h` finds nothing.
- **What the window site carries today (D172).** Span starts in `[-MF_MAX_BACK, MF_WREACH)` =
  `[-8, 64)` *(`[-8, 4096)` since R-45 plan B: MF_WREACH 4096, a refusal bound only)* (`memfn/include/memfn.h:235`, `:586-591`), checked at `src/gen/memfn_sites.c:587-592`.
  pcrec states two negative starts, both `-1`: MLINE's predecessor stop (`src/gen/emit_dfa.c:8393`)
  and the cover site's context-before side (`src/gen/known.c:465`, `MkEnd.ctx_before`,
  `src/gen/known.h:25-27` with `absent_*`). The run span R never starts below 0 (`walk_proves`
  refuses `d < 0`, `emit_dfa.c:6809`). The UTF check's step back is `<prefix>_VALID_LB` =
  `Ctx.lb_max` (`emit_dfa.c:3610-3617`).

## 1. Goals

Ranked; the higher wins a conflict.

| # | goal | who benefits | measurable form (comparison, margin) |
|---|---|---|---|
| G1 | No answer moves | every caller | answer identity over corpus + bench, every encoding and axis (`make test`, `make test-axes`), PC-3 unchanged; margin 0 |
| G2 | Each arm is ONE rule in the one description | maintainers | per unit, the ledger (§9) lists the special cases deleted and the rows added; no second walk, no per-construct clause; the run stays `req.c`'s one walk; a lookaround body's per-offset sets have ONE producer (§5.3) |
| G3 | No reader reads a run outside its admitted reach | every caller | every reader of a moved fact is in §5.4's table with its reach; a unit that widens a reach names the reader and its witness; an unlisted reader is red at review |
| G4 | D186's bar at every pick row a unit moves, per regime `[r1 F20]` | users with pinned performance | every unit is a FACT change: an INPUT to the existing choice rows, judged at the pick rows it moves, with D186's choice bar applied there (no regime loses beyond noise on a bench cell whose pick moved; a loss narrows that pick row's condition) |
| G5 | The movers are the census's | the build lane, the critic | each unit's emitted movers equal an independent model's list (two-sided) over corpus + bench, both encodings; the predicted movers here are its spot checks |

Non-goals: the VM half of [REPEAT-RUN] (§3.8); lookaround REMOVAL, span intersection as an IR
node, the end-of-match mark and the group-0 group ([POSTFACT], §7); negative lookarounds beyond
the width-0 unit; [REWRITE-ADJ]; making kset/startset/endwin readers of the description
(alt_normal_form G-1); new public flag bits; the necessary SET taking guard bytes (§5.2: T4 is a
run rule).

## 2. The general form

alt_normal_form §3.5: every fixed-width, capture-free piece has ONE description, built bottom-up by
the arm combinators of `src/facts/desc.c` and read by `req.c`'s walk (the run) and `altnf.c` (the
adjacency head). This note adds three arms and one carried value.

**The attempt span** `[r1 F14]`. Every run statement is relative to the ATTEMPT: from the
position the attempt starts at (`p`, where `search_from` and the handoff put it) to the end of
what the attempt consumed. The REPORTED match may start later (`\K`): today `abc\Kd` stamps
`RX_REQ_RUN "616263@1"` while its match is (3,4) (measured; oracle M 3 4). Every reader is
attempt-relative (invariant F, `src/facts/facts.h:79-87`, "every successful attempt at `p`"), so
no answer depends on the distinction. The wording does, and §8's spec hunks use "attempt".

**The reach is the run's signed offset interval `[omin, maxoff]`** `[r1 F9, F16]`. `maxoff` is
`ReqRun.maxoff` (K82): the largest offset from the attempt start at which the run can begin.
`omin` is its lower twin, the smallest such offset. The kit's presence span already has that slot
(`memfn.h:679-684`, `int32_t omin`, "the smallest offset, from the MATCH START, at which an
occurrence of the span can begin"; refused below 0 today, `memfn/src/compose.c:608`). `[REV 3: delivered by R-38 K38-2, MF_SITE_ABI 27-29; §14.1 item 13]` Every run
today has `omin = 0`. The soundness statement becomes: "every successful attempt at `p` holds the
run at some `q` in `[p + omin, p + maxoff]`". `omin < 0` (the run begins before the attempt
start) is BACK, L3. A run that ends past the attempt's consumed end (AHEAD, L2) needs no new
value: no reader reads the run's end (§5.4), so no `ahead` field is stored (D77) until one does.
A run with `omin < 0` still lies inside the subject: the scan begins at
`max(0, search_from + omin)`, and the bytes before `search_from` are ones the matcher may read,
because PCRE2 lets a lookbehind read before the start offset. `[r2 S7]` That floor is the KIT's
behaviour, not pcrec's text: pcrec states `omin`, and the kit's pre-check (entry and re-entry)
honours it (§5.4 A1-A2, L3's kit request). The kit's `omin` today is measured from the MATCH
start (`memfn.h:679`); this note's is from the ATTEMPT start, so L3's request re-defines the
origin (the two differ under `\K`).

**Pending guards** `[r1 F1, F2]`. A run value (`RbRuns`) carries two pending guards beside its
consumed runs: `lg`, run positions at offsets `[-t, 0)` before the value's start, and `rg`, run
positions at offsets `[0, h)` after its end. Each guard position is a cube, like a run position.
A guard comes only from a positive lookaround's ITEM (§5.1). `[r2 S5]` A guard is an `RbRun`
stored at the run's bound (`PCREC_MAX_REQ_RUN_SCAN`, 32 positions) and keeps the end NEAREST the
edge it touches: `lg` keeps its LAST positions (the tail form, `rn_pre`), `rg` its FIRST (the
head form, `rn_app`), so every kept position stays at its stated offset as a guard grows (ITEM's
"followed by"/"preceded by", CAT-EDGE's merged leftover). A guard's `trunc` is never read: a
truncated guard is a shorter necessary condition at the same offsets. REP's saturation (§3.1
point 3) does not count guards. Below the top level a guard is never
a byte of `head`, `tail` or `best`. `rr_cat` MEETS it against its neighbour's consumed positions
(an intersection), CARRIES what is left across an `all` neighbour (whose width is exact), and
DROPS it at any other neighbour. Only the top level (row TOP) may extend the run with a guard,
and only at the reach its readers admit. Dropping a guard drops a necessary condition, which is
always sound; an intersection of two necessary conditions is necessary.

**The three arms, one row each in the arm table (§6 T1):**

| node | consumed part | guards | proof |
|---|---|---|---|
| REP `X{m,n}` | §3's T2 rows: `X^c` through CAT, head/best from `X^c · X{0,n-m}`, tail from `X{0,n-m} · X^c` | the copies' guards, through CAT (`lg` from the left decomposition, `rg` from the right); none at `m = 0` for a width-0 body | `X{m,n}` = `X^m X{0,n-m}` = `X{0,n-m} X^m`; CAT is sound on each |
| a node that consumes nothing (`A_EMPTY`, `\b`, `$`, `\G`, `\K`, a check callout, a negative lookaround, any `A_CTX` but the two below) | the width-0 unit (`rr_unit()`: no run, `all`, width 0) | none | consumed bytes on either side of a zero-width node are adjacent in the subject |
| positive LOOKAROUND (`A_LOOK` positive; `A_CTX` with `CTXFN_NEXT`/`CTXFN_PREV`) `[r2 S2]` | the width-0 unit | the hull of the producer's ITEM (§5.1, §5.3): `rg` at the item's terms `[0, h)` (lookahead), `lg` at `[-t, 0)` (lookbehind), plus the body's own guards at their offsets | the body matches at the cursor, so the subject holds the item's sets there |
| backref, variable, call | unchanged walls | none | — |

`[r1 F16]` Rev 0's EXACT/GUARDED split is gone. It had one claimed reader (the owner), and the
owner reads `PdHead`, which has no exact bit (`altnf.c:187-212`); `PdGroup.exact` is read only
inside `desc.c`. A width-0 group for a node that can fail keeps `exact = false` in the
description, a sound superset (`facts.h:95-96`) with no reader. A unit that needs the distinction
(R2, if its census fires) names its reader and witness then.

## 3. The REP arm ([REPEAT-RUN], alt_normal_form §9 S3)

### 3.1 The rule and its six decision points

1. **REP as the description's power arm, not a `req.c`-local rule.** One combinator in `desc.c`
   (`pcrec_pd_pow`, name at build), and the run walk's `A_REP` arm calling the CAT step on the
   body's value. A `req.c`-local `rr_rep` would be a second spelling of CAT; the power reuses
   `rr_cat` and `pcrec_pd_cat` and adds only the copy loop.
2. **The iteration-boundary join is sound because it is the CAT join.** reqpos_2b.md §2.4 item 4
   declined it "for want of a witness family", not for a soundness gap. The join between copy i's
   tail and copy i+1's head is `rr_cat`'s own `join` (`req.c:450-468`). §3.6 is the family.
3. **The copy count is DERIVED from the run's storage bound, no constant** `[r1 F6]`. Unrolling
   stops at `c = min(m, sat)`, where `sat` is the copy count after which no CONTENT field (head,
   tail and best bytes, `all`, `trunc`) can change. A body that is not `all` saturates at 2 (every
   later copy adds the same `tail · head` join). An `all` body of width w ≥ 1 saturates at
   `ceil(PCREC_MAX_REQ_RUN_SCAN / w)` copies (`limits.def:409`, 32 bytes): its stored head is full
   there, and T2 forces `all` false whenever `c < m`. Rev 0's `+ 1` changed only `best.off` (it
   loosens by w per extra copy, soundrep SOUNDREP-2). OFFSETS are not content: they come from the
   c-copy prefix (below), never from more copies. `maxw` is ALWAYS the exact `rr_rep_w(rmax, ...)`
   (`req.c:436-440`), never `c · w` (F3, W-R6). No limits row is added. Any `c <= m` is sound,
   since `X^c` is a factor of `X^m`; `sat` is where more copies stop adding information. For a
   body that carries a guard (an L unit), one more copy can still narrow the last stored copy by
   its neighbour's guard. That is a looser but sound value at `sat`, and L1's census shows whether
   it matters.
4. **The VM half is a separate CHOICE row** (§3.8): not this note's.
5. **`NFA_ERASED_COUNT` is unaffected.** The run is AST-derived (`req.c:107`).
6. **The population census is the trigger (D77)**, §8 unit R1.

**Offsets ([K82]).** In `X^c · X{0,n-m}` the copies start at the repeat's start: the head is at 0
and `best` keeps the offset the c-copy CAT computes. In `X{0,n-m} · X^c` the tail ends at the
repeat's end, so `rn_tail_off(maxw, n)` (`req.c:428-431`) applies with the exact `maxw`. The best
is taken from the first decomposition (its offsets are the smaller bounds); the second
contributes the tail and `rg` only.

### 3.2 The owner and the code it touches

- `src/facts/req.c` `rb_rep_into` (`:549-558`) and the `A_REP` arm (`:708-740`) become T2's rows
  (§6). The header paragraph `:64-69` and the arm comment `:709-719` are rewritten with them.
- `src/facts/desc.c`: a power combinator, `pcrec_pd_cat` applied c times with the same saturation
  (a group stores at most `max_pos` positions, `desc.h:32-39`). `REP{m,n}` with m < n gives
  `pd_none` exactly as today, so `req_pieces` moves only for exact repeats of a multi-group body.
- NOT touched by R1: `altnf.c:223-230`, the adjacency head's REP wall (unit R2, §8).

### 3.3 Readers it moves (found by grep at `7b9ddd890`; the cites hold at `dd2fe2de9`)

The run walk's outputs are `req_set` (unchanged), `req_set_maxoff` (unchanged), `req_whole_run`
and its derived `req_run`, `req_run_maxoff`, `req_byte`, `req_landmark_maxoff`, `run_pin`
(`src/facts/facts.def:50-60`), and `req_pieces`. For REP the reach stays `[0, maxoff]`, so every
reader in §5.4 admits the moved run as it admits today's. The readers whose OUTPUT moves are the
pick readers (`src/core/findings.c`), the window statement's R span (`emit_dfa.c:6815-6871`) and
the stamps `RX_REQ_RUN`/`RX_REQ_BYTE`/`RX_REQ_WHY`/`RX_REQ_HANDOFF`; `--emit-facts` lists the new
values. Answers do not move (§3.5).

### 3.4 Predicted movers (measured spellings)

| pattern | today (measured) | predicted (the spelling, measured) |
|---|---|---|
| `A{4}` | none | `41414141` (`AAAA`) |
| `ab{3}c` | none | `6162626263` (`abbbc`) |
| `xy(?:ab){2}zw` | `6162` (2) | 8 (`xyababzw`) |
| `(?i)xy(?:ab){2}zw` (byte and utf8) | none | 8 cube positions (`(?i)xyababzw`) |
| `abcd(?:ab\|Ab){2}efgh` | `65666768` (4) | 12 positions |
| `xy(?:ab){2,3}zw` | `6162` (2) | 6, `xyabab` (`xyabab(?:ab)?zw`) |
| `xy(?:abc\|abd){2}zw` | `6162` (2) | 4, `xyab` |
| `x(?:a[bc]){2}y` | none | 6 (`xa[bc]a[bc]y`) |
| `xy(?:é){3}zw` utf8 | `c3a9` (2) | 10 |
| `(?:abc){20}` | `616263` (3) | 32 positions, truncated at the storage bound (W-R5) |
| `xy(?:ab)+zw`, `xy(?:ab){1,}zw` | `6162` | 4, `xyab` |
| `xy(?:ab){0}zw` `[r1 F7]` | `7a77` (2) | 4, `78797a77` (`xyzw`, measured) |
| `xy(?:ab){0,2}zw`, `xy(?:ab)*zw`, `[0-9]{4}` | `7a77` / none | unchanged |

### 3.5 Answer identity

The run is a necessary condition. A longer necessary run moves which run the pre-check compares
and where, never which subjects match. The two decompositions are language identities and the
unrolled CAT is `rr_cat`, so an unsound run can come only from a wrong decomposition, a wrong
width or a wrong copy count: what the witnesses plant.

### 3.6 Sabotage witnesses (each can fail; expected answers from libpcre2)

Each failure mechanism: the sabotaged run clears the 16-bit floor (`limits.def:410`), is absent
from the subject, and is not walk-verifiable, so it is never `dominated` (the pin needs every
position to be a k-set singleton, `kset.c:294-318`). `[r2 S3]` And the artifact's locator is not
one that decides presence itself (`RX_DFA_SCAN` is not `"rev-end"`, `"cover"`, `"landmark-walk"`
or `"empty"`): match_api §6.3.7¶8's `dominated` row declines the run check there whatever the
run is. Both halves are checked per witness (the `RX_DFA_SCAN` and k-set columns of §5.7). So
the pre-check compares the run and answers NOMATCH (soundrep and soundlook PROBED-AND-HELD (b)).

| id (role) | planted error | pattern, subject, expected | correct run | sabotaged run, and why it fails |
|---|---|---|---|---|
| W-R1 (all at m < n) | `all` set for `X{m,n}` with m < n | `xy(?:ab){1,2}zw` on `xyababzw`: (0,8) | `xyab` | `xyabzw`: absent, NOMATCH |
| W-R2 (copies = n) | unroll `rmax` copies, not `rmin` | `xy(?:ab){1,3}zw` on `xyabzw`: (0,6) | `xyab` | `xyababab...`: absent, NOMATCH |
| W-R3 (min-0 as m = 1) `[r1 F7]` | c computed from `max(m, 1)` (the C-comment shape `req.c:723-738` names) | `ab(?:cd){0,2}ef` on `abef`: (0,4) | `ab` or `ef` (a tie, F22: the build's tie-break picks one; the sabotage is detected either way) | `abcd` or `cdef`: absent, NOMATCH |
| W-R4 (width-0 test reads min width) | the width-0 row reads `minw == 0` instead of `maxw == 0` | `ab(?:c?){2}de` on `abcde`: (0,5) | `de` (tie with `ab`, F22) | `abde`: absent, NOMATCH |
| W-R5 (FACT witness, saturation) `[r1 F6]` | saturation at `ceil(32/w) − 1` copies | `(?:abc){20}` | 32 positions (11 copies, truncated) | 30 positions (10 copies): shorter, sound, cannot move an answer; checked on the facts listing |
| W-R6 (exact width) `[r1 F3]` | `maxw` taken from the c unrolled copies (`c · w`) instead of `rr_rep_w` | VM: `(a.){10}xyz` on `a-a-a-a-a-a-a-a-a-a-xyz`: (0,23); DFA: `(?:a.){10}.?xyz` on the same subject: (0,23), and from offset 2: NOMATCH | K = `req_run_maxoff` 20 (VM, `RX_REQ_HANDOFF "20"`, measured) and 21 (DFA, `"21"`, measured) | `a.` is not `all`, so c = 2 and `maxw` = 4: K becomes 4 (5), an attempt at 0 is admitted only with `xyz` in `[0, 4]`, the handoff skips it, and no later start matches: NOMATCH where (0,23) is expected |

W-R3's subject is `abef`: on `abcdef` the sabotaged run is present by accident. The plain
`(?:a.){10}xyz` is `dominated` today (`RX_REQ_HANDOFF "none"`, measured), so its K is never read
and it cannot fail; that is why W-R6's DFA twin carries `.?`. Each witness's REACH (the plant's
site is reached by the witness) is part of the build's mech row ([MECH-REACH]).

### 3.7 Deny lever `[r1 F18, F19]`

**The rule.** The owner's 2026-10-29 rule ("the flag follows what a change can DO to a caller":
a PUBLIC deny only for a change that can be SLOWER, a TEST-ONLY lever for a WRONG-answer risk,
none for a refactor). It has no D-row. Its repo homes are review 2026-10-29 r3 vmtrail F11,
`docs/design/alt_normal_form.md` §11 (r7 RDY-9), `docs/dev/lanes/vmcons_report.md` (R1) and the
comment at `memfn/include/memfn.h:1427-1428` ("a change that cannot make a caller slower carries
no public deny"). Every unit here can be slower only through the pick rows that read the moved
fact, each with its own deny, where D186 narrows a loss (alt_normal_form §11's stage-2a row).
Its wrongness risk is W-R1..W-R6. So it gets a TEST-ONLY lever and no public bit.

**The form: a declared table of WALK PARAMETERS** `[r2 S9]` (RULED; alt_normal_form §3.5 r7
FIX-8's harness source, placed where it acts). FIX-8's trigger was "a second such change", a
second test-only lever on a core fact; it FIRES here (2a's lever was the first, this note's
`rep`, `zero` and `look` the second to fourth). Rev 1 put the arms "beside the deny bits" in a
fact's `facts.def` row. That was not one application site: the deny column EMPTIES a fact in
`pf_enter` (`facts.c:147-153`, for every `PF_FACT`), while bit 44 is read separately as the
walk's `pos_set` (`facts.c:208-211`), and one walk call produces four facts at once (`req_set`,
`req_set_maxoff`, `req_whole_run`, `req_pieces`, `facts.c:212-249`), so "the fact rows an arm
applies to" was ill-formed. Rev 2:

| parameter | what the walk reads it as | default | lever source | T-row that reads it |
|---|---|---|---|---|
| `pos_set` | the run's cube domain | `PCREC_MAX_REQ_RUN_POS_SET` (`limits.def`) | public bit 44 `-fno-req-run-fold` → 1 | every run arm (`rn_common_head`, the class arm) and the guard's hull (§5.1) |
| `max_pieces` | the description's group bound | `PCREC_MAX_REQ_PIECES` | none | the description (`PdCfg.max_groups`) |
| reach `[REV 3: not a parameter: TOP's rows with an arm column, §14.3 D-4]` | TOP's admitted interval | `[0, maxoff]` at L1; AHEAD at L2; BACK at L3 | harness arm `look` → `[0, maxoff]` | TOP |
| restored arms | the arms run in today's form | none | harness arms `alt`, `empty` (2a), `rep` (T2 → today's best-only REP), `zero` (T3 E-4 → today's cut; E-5 stays E2's plain unit), `tie` (R1's rarity tie rule, `rn_choice_rows` rows 2-4 → information, then the first run; added by lane sartie, Frank 2026-11-10, so that `rep`+`tie` reproduces the pre-R1 compiler exactly), `look` (T4 off: E-5 as E2's plain unit, no item and no guards, and reach `[0, maxoff]`) `[r3 READY-9]` | T1's arm switch |
| `lb_bytes` | TOP's BACK step cap (§5.5) `[REV 3: read through RM-5's accessor, §14.3 D-11]` | `Ctx.lb_max` × the encoding's widest character | none (a `Ctx` policy field, deliberately not a fact accessor, `internal.h:3979-3997`) | TOP |

- The table is filled ONCE, at the one walk entry (`pf_derive_req_walk`'s call of
  `pcrec_req_walk`, `facts.c:208-211`, which already reads bit 44 there) and handed to the walk
  as one parameter record. There is no second deny path.
- `facts.def`'s deny column keeps its one meaning: a public bit there EMPTIES the fact
  (`pf_enter`). A walk parameter never empties a fact; it changes how the walk derives it.
- `--emit-facts` lists a restored arm through a new `facts_listing.md` §4.1.3 token
  `harness:<arm>[+<arm>...]` `[r3 READY-5, READY-7]`. It is a WHY VALUE like the others: the
  listing keeps "exactly one why" per run, and `dead` (§5.2 (g)) and `harness:` join `deny:`,
  `decline:` and `rate:` under one first-match order, **`dead` > `harness:` > the existing
  reasons**; there is no second field. (A `deny:` fact is empty, `pf_enter`, so neither value
  arises on it.) It sits on the facts a restored arm can change: at L1's `look` arm
  `req_whole_run` and the facts derived from it (`req_run`, `req_run_maxoff`, `req_byte`); each
  later unit's gate names its arm's facts. `dead` sits on `req_whole_run` only. A dead
  `req_whole_run` is `derived` (the walk produced a value, `foobaz`; `dead` annotates it), so
  `pf_done_why` (`facts.c:169-182`) takes `dead` and `harness:` out of its `decl` list, and
  `run_facts_checks.sh`'s status/why pairs gain the two. `dead` is not `decline:dead-start`: that
  is `land_char`'s and `span_facts`' decline (the start machine finds no match; value `0`, *(superseded by cover_cap.md rev 4, 2026-11-15)*
  `facts_listing.md` §4.1.2¶7a/¶7c, status `declined`), while `dead` is the run walk's own
  empty meet on a `derived` fact; neither reads the other, and one pattern can list both on
  different facts. The token closes the invisibility alt_normal_form's stage-2a lever note
  records: `pin` is built at `cli/main.c:2903` (at `9161402da`) without `.harness`, passed at
  `:3145`, and the encoding-list loop between them (`:3121-3135`) is not where it is built. The
  token is visible only from `build/pcrec-harness` (`#ifdef PCREC_HARNESS`, `cli/main.c:28`);
  `build/pcrec` has no `--harness=`. The token is named in the gate of the first unit that builds
  the table (§8).

The spelling (one `--harness=` value naming arms) is the build's. The `--harness=` levers
themselves are an if-chain of one-bit fields (`cli/main.c:1430-1443`, `PcrecHarnessOptions`) and
another member of the same family (`pres-window` is the same restore-the-old-form shape). That is
filed as [HARNESS-LEVERS], not fixed here (as ruled).

**Public bits.** `-fno-req-run` (bit 31, tuning.md §2.28) and `-fno-req-run-fold` (bit 44,
tuning.md §2.39) keep their texts through E1, R1, E2, L1 and L2. Bit 44 already denies every
multi-member position, so `(?i)xy(?:ab){2}zw`'s cube run is under it. At L3 see §5.8.

### 3.8 The VM half (pointer only)

The row's "the VM's literal-run selection" (`vm_det_seq`/`vm_cursor_fits`, ratchet row R02's
area A-SKIP) is a separate CHOICE row with per-regime evidence and its A-ISL overlap (roadmap
R04). It reads the same power description when built; nothing in R1 depends on it.

## 4. The EMPTY arm ([REQ-EMPTYCAT], alt_normal_form §3.6, §9 S2)

### 4.1 What stage 2a moves, and what remains

Stage 2a moves ONE kind: `case A_EMPTY` (`req.c:756`) becomes the description's EMPTY arm, the
unit of CAT; the kind row stays (`src/core/kindrow.def:61`, TEXT `ZERO`). It is row E-1 below.
What remains is every other node whose consumed description is width 0:

| row | the subtree | run value | today | after |
|---|---|---|---|---|
| E-1 | `A_EMPTY` (`abcd()efgh`, `abcd(?:\|)efgh`, altcls's empty residue, derive's pruned nodes) | the unit | cut | unit (stage 2a) |
| E-2 | a repeat whose body is width 0 and consumes nothing that can fail (`(?:)*`, `(?:){3}`) | the unit (T2 row 1) | cut / gap | unit |
| E-3 | `X{0,n}` whose body is width 0 (`(?:\b)*`) | the unit, no guard (T2 row 1, `m = 0`) | gap | unit |
| E-4 | a zero-width node that can fail: `\b`/`\B` (`A_CTX`), `$`/`^` (`A_EOL`, `A_CTX`), `\G`, `\K`, a check callout, a negative lookaround (`A_LOOK` or a negative `A_CTX`), and `X{m,n}`, m ≥ 1, of such a body (`(?:\b)+`, `pcrec_wrap_bare_anchor`'s `<anchor EMPTY>` under a quantifier) | the unit (`exact = false` in the description, no reader, §2) | cut | unit (joins consumed contiguity) |
| E-5 | a positive lookaround: `A_LOOK` positive, `A_CTX` with `CTXFN_NEXT`/`CTXFN_PREV` `[r2 S2]` | E2: the unit; L1: the unit plus its item | cut | §5 |

`[r2 S16]` **Until L1, E-5 is the plain unit.** E2 makes every zero-width node the unit, a
positive lookaround included (both lowerings), and reads no body. L1 then adds the item to E-5's
unit. So under E2 `xyz(?<=yz)abc` gives `xyzabc` (§4.4) and S-L's plant (the body walked as
consumed) has a site in E2's own arm.

E-2/E-3 follow from T2 with no extra clause. E-4 is alt_normal_form §9 S2 point (3): decided as
a census, unit E2, because its soundness is not in question. The bytes on either side of a
zero-width node ARE adjacent (`req.c:748-751` says so); what the header forbids (`:752-755`) is
joining through the BODY of a lookaround, which E-4 does not do. S-L separates the two.

### 4.2 The owner and the code it touches

`req.c`'s cut list (`:756-771`) splits by row: E-1 (2a) and E-2/E-3 (E1) take `rb_init`'s identity
(`rr_unit()` + `pcrec_pd_unit()`, `:511-516`) through T2; E-4 (E2) takes `rr_unit()` for the run
and a width-0 description group with `exact = false`. `rb_row_into`'s `KTEXT_ZERO` row
(`:637-645`) is where E-4 lands. The kind row is untouched. `endwin.c:301` and `emit_vm.c:4177`
`[r1 F13]` (the island walk's `case A_EMPTY:`; rev 0 cited `:4093`, a comment) stay kind tests
(alt_normal_form FIX-9).

### 4.3 Readers it moves

The same fact set as §3.3, at reach `[0, maxoff]`: a width-0 unit joins two consumed runs that
are both inside the attempt span `[r1 F14]` (with `\K`, a joined run may straddle the reported
start, as `foo\Kbar` would give `foobar` with the match at (3,6); every reader is attempt-
relative, §2). `[r1 F11]` The window statement's R span also moves: `kset_walk` already proves
the consumed bytes on both sides of an erased lookaround (`xyz(?<=yz)abc` gives all six), so after
E2 an R over `xyzabc` is walk-provable with no U-G1. E2's census counts R-span movers beside run
movers.

### 4.4 Predicted movers (measured spellings)

| pattern | today | predicted |
|---|---|---|
| `abcd()efgh`, `abcd(?:\|)efgh` (E-1, 2a's) | 4 | 8 |
| `abcd(?:)*efgh`, `abcd(?:){3}efgh` (E-2) | 4 | 8 |
| `abcd(?:\b)+efgh` (E-4; never matches) | 4 | 8 (sound: a pattern that cannot match has every run) |
| `xyz(?<=yz)abc` (E-5 under E2, the plain unit; the body not read) | `abc` (3) | 6, `xyzabc` (spelling measured) |
| `x(?!ab)ac` (a negative lookaround, E-4) | `ac` | 3, `xac` |

### 4.5 Witnesses

| id | planted error | pattern, subject, expected | correct | sabotaged |
|---|---|---|---|---|
| S-g (alt_normal_form, 2a) | a consuming kind (`A_BREF`) sent to the EMPTY arm | `(ab)x\1y` on `abxaby`: (0,6) | `abx` | `abxy`: absent, NOMATCH |
| W-E1 (a negative body read as an item) `[r1 F5]` | a negative lookaround's body read as a positive item (its head affix met against the right side) | `x(?!ab)a[bc]` on `xac`: (0,3); on `xab`: NOMATCH | `xa[bc]` (E-4) | `xab` (the cube `[bc]` narrowed by the body's `b`): absent from `xac`, NOMATCH |
| W-E2 (E-5's join through the body, S-L) | §5.7 | | | |
| W-E3 (E2's own, a negative body) `[r2 S16]` | a negative lookaround's body walked as CONSUMED | `xy(?<!ab)cd` on `xycd`: (0,4); on `xyabcd`: NOMATCH; `abcd` from 2: NOMATCH | `xycd` (E-4 joins) | `xyabcd` (48 bits): absent from `xycd`, NOMATCH |

W-E3, measured today: `kinds lookaround`, VM, `RX_DFA_SCAN "unanchored"`, run `6364@0`,
`RX_REQ_WHY "emitted"`, k-set `120,121,99,100`: no locator decides presence, and the sabotaged
run's position 2 (`a`) is not the k-set's `99`, so it is not pinned.

W-E1's plant has a site only once item code exists, so it is in L1's gate, not E2's (rev 0 listed
it at E2, which has no meet site). Rev 0's `x(?!ab)ac` emptied a position, and an emptied position
is not a run value a reader sees (EMPTY-MEET, §5.2), so it could not fail. `x(?!a)[ab]c`/`xbc`
(soundlook's, oracle M 0 3) is not used: `[ab]` is not a cube at `pos_set` 2 (`0x61 ^ 0x62` has
two bits), so the run has no position there for the plant to narrow.

### 4.6 What closes [REQ-EMPTYCAT]

S2's five points: (1) decided by alt_normal_form; (2) E-2/E-3 by T2; (3) E-4 a census, unit E2;
(4) the producer census is E2's, per producer kind; (5) the row closes when 2a, E1 and E2 have
landed or been declined by their census.

## 5. The positive LOOKAROUND arm ([REQ-LOOKAROUND], alt_normal_form §9 S4) `[r1: rewritten; r2: S1-S8, S10, S14]`

### 5.1 The item and where the run meets it `[r1 F1]` `[r2 S2, S8]`

**The item (the producer's, §5.3).** For a positive lookaround node at cursor `c`, its ITEM is
the subject's per-offset EXACT sets at signed offsets from `c` that the body's success implies,
with a form (EXACT where the terms are equivalent to the node, else SUPERSET). It has two
lowerings and one rule:

- `A_CTX` with `CTXFN_NEXT`: one term, the node's set at offset 0; with `CTXFN_PREV`: one term at
  −1 (ctx_span §3.3's `ctx-onesided` row, positive functions only: their absent cell FAILS). Every
  other `A_CTX` function (`\b`, `\B`, the negated one-sided rows, `^`, `$`, `\A`, `\z`) is E-4's
  plain unit: a two-sided relation is not a per-offset set (D168 "Revisit when"), and a term whose
  absent cell SATISFIES is not a byte every attempt holds.
- `A_LOOK` positive `[REV 3: AHEAD reads the head column, BEHIND the description, §14.3 D-10]`: the body's DESCRIPTION (`desc.c`, its width groups of exact position sets)
  placed at the cursor, a lookahead's groups left-aligned at `[0, w)` and a lookbehind's
  right-aligned at `[-w, 0)`, then united per offset across groups. An offset some group does not
  reach takes all bytes, so it is no term (ctx_span §3.3 `look-fixed`'s fact). A body with one
  exact group is EXACT; several groups, or a group with a zero-width node in it (E-4/E-5's
  `exact = false`), make it SUPERSET. A body the description walls (a variable piece past
  `max_groups`, a backref, a call) has no item. A nested positive lookaround is its OWN item
  (ctx_span §3.6: items are conjoined, never merged), which the run reaches as the body's guards.

**The guard (the run's reading).** The run derives its guard locally from the item: term by term
outward from the cursor, the cube hull of the term's set if the hull is inside the run's domain
(`rn_members(hull) <= pos_set`), the guard ending at the first term that is not. Then:

- a LOOKAHEAD: `rg` = that hull at `[0, h)`, followed by the body's own `rg` when the body is
  `all` (exact width, so its end offset is known); `lg` = the body's own `lg` (a lookbehind nested
  in the body, at its own offset);
- a LOOKBEHIND: `lg` = that hull at `[-t, 0)`, preceded by the body's own `lg` when the body is
  `all`; `rg` = the body's own `rg` (a lookahead nested in the body).

The body's own guards come from the run walk's descent into the body (`rb_walk(w, a->l, ...)`
from L1 on), which reads each nested item by this same rule, so nesting keeps its offsets
(soundlook's case (d)). For the shapes rev 1 named, the hull equals rev 1's "body's head/tail
affix": `(?=ab|ac)`'s item is `{0: a, 1: {b,c}}`, hull `a[bc]`, which is `rr_alt`'s common head;
`(?<=ab|b)`'s is `{-1: b}` (−2 is reached by one group only); `(?<=fo{1,3})`'s is
`{-1: o, -2: {f,o}}` SUPERSET, and `{f,o}`'s hull has four members, so the guard is `o`.

**One lowering, one run** `[r2 S2]`. Because both lowerings reach ITEM, the run of a
one-character lookaround is the same with and without `-fno-ctx-node`; that difference is
deleted, and L1's gate checks it `[r3 READY-4]` on the rows where the equality CAN fail: W-C1's
run is `ab[bc]d` both ways, so the equality is vacuous there (W-C1's own plant, PREV read as
NEXT, is what fails). The rows that hold the `A_CTX` ITEM row are `a(?=b)[bc]` (without the row,
`a[bc]`: the run is none against `ab`; measured at `9161402da`: default `kinds none`,
`RX_DFA_SCAN "cover"`, run none today, under `-fno-ctx-node` `kinds lookaround`, VM, run none
today) and `ab[xy](?=(?<=x)y)[xy]` (`ab[xy]y` against `abxy`), compared at listing level
(`req_whole_run`, `req_run`), where `a(?=b)[bc]` is `cover` and answers cannot move.

**Where the run meets it.** The arm returns the width-0 unit carrying the guards (T4 row ITEM).
Everything else happens in `rr_cat`, which every concatenation passes through. That matters
because the walk hands the arm a fresh accumulator at every spine position but the leftmost
(§0). So `xy(?=bc)[bc]c`'s lookahead meets `[bc]c` in `rr_cat(item, [bc]c)`, not at its arm. Rev
0 met it at the arm and laid the guard end to end with the neighbour (premise PREMISE-1).

### 5.2 The guard rows, one per combinator (§6 T4, first match within each combinator) `[r1 F2]` `[r2 S4, S5, S6]`

Notation: `l` is to the left of `r` in subject order; `o` is the result. "Meet" is position-wise
intersection of cubes at equal subject offsets (a cube ∩ a cube is a cube or empty, D187); a
missing position is all bytes. `[REV 3: DEAD is the never family's propagation, rendered as `dead`, §14.3 D-9]` DEAD is a per-value bit, "this subtree cannot match"; the root's
bit is the listed dead fact.

| row | combinator | rule | DEAD | witness (§5.7) |
|---|---|---|---|---|
| ITEM | positive lookaround | the unit; `lg`/`rg` = the guard derived from the item (§5.1) | the body's | W-N1, W-N2, W-F5, W-C1, W-L3 |
| CAT-R | `rr_cat(l, r)`, `l.rg` | `l.rg` meets `r`'s positions at `[0, min(h, r.head.n))` from `r`'s start: `r.head`, and where `r.all` also `r.tail` and `r.best` (the same positions). The narrowed `r.head` feeds `o.head` and the join as today | as CAT | W-L5 |
| CAT-L | `rr_cat(l, r)`, `r.lg` | `r.lg` meets `l`'s last positions at `[-min(t, l.tail.n), 0)` from `l`'s end: `l.tail`, and where `l.all` also `l.head` and `l.best` | as CAT | W-F5, W-S1 |
| CAT-SET `[r2 S4]` `[REV 3: one step at the walk's exit, §14.3 D-3]` | `rr_cat(l, r)`, after CAT-R/CAT-L | a CONSUMED position a meet narrowed to ONE byte puts that byte in the side's necessary SET at the position's offset, before the SET's own CAT shifts it (an `r` position at index `i` enters `r`'s set at offset `i`; an `l` position at `l.maxw − k` enters `l`'s at that offset, where `l.all` makes it exact). Every match holds the byte there (consumed, and both conditions necessary), so the set stays a set of necessary bytes, and `pcrec_req_pick`'s exact scan member stays one of them | — | W-S4 (FACT) |
| CAT-EDGE | `rr_cat(l, r)`, the leftovers | `o.lg` = `l.lg`, met at equal offsets with `r.lg`'s positions beyond `l.tail.n` shifted by `l.maxw`, IF `l.all` (exact width); otherwise `o.lg` = `l.lg` and the leftover is DROPPED. Mirror: `o.rg` = `r.rg` met with `l.rg`'s leftover beyond `r.head.n` shifted by `−r.maxw`, IF `r.all`; else dropped. Stored as §2 says (kept end nearest the edge). `o.all` is `rr_cat`'s as today (guards never touch it) | `l.dead OR r.dead OR` an empty meet in this step | W-L2, W-L6, W-L7, W-L8, W-S1, W-T1 |
| ALT | `rr_alt(l, r)` | `o.lg` = `rr_alt`'s own common-TAIL rule applied to `l.lg` and `r.lg` (right-aligned at the alternation's start, hull within `pos_set`, ended at the first position outside the domain or missing from a branch); `o.rg` = the common-HEAD rule on `l.rg` and `r.rg`. A branch with no guard gives none | `l.dead AND r.dead` | W-A1 |
| REP | T2 | through CAT, per copy; T2's guard column (none at `m = 0` for a width-0 body). Needs R1's T2 rows 2-3; without R1 the REP arm is today's best-only and carries no guard | `m = 0` (and `{0}`): never; `m >= 1`: the body's | W-F4, W-RG, W-T1 |
| EMPTY-MEET | any meet | an empty intersection at a CONSUMED position: that position KEEPS its un-narrowed value. A guard position whose meet with a guard position is empty is dropped with every position outward of it. Either way the result's DEAD bit is set (two necessary conditions with no common byte) | set | W-D1..W-D4, W-D6, W-D7 (FACT) |
| (others) | negative lookaround, E-4 nodes | the unit | never (a negative lookaround over a dead body always succeeds) | W-D5 (a structural note, no plant site) |
| TOP `[REV 3: a combining row table, the window and `omin + at` retired, §14.3 D-4, D-7]` | the root value, at the admitted reach | reach `[0, maxoff]` (L1): the guards are dropped. AHEAD admitted (L2): a candidate `tail ++ rg` at offset `rn_tail_off(maxw, tail.n)`, computed from the CONSUMED `tail.n`; where `all`, `head ++ rg` at 0. BACK admitted (L3): a candidate `lg ++ head` at offset `−t`, `t` the STORED `lg.n`, if `t <= lb_bytes` (§5.5); where `all`, `lg ++ head ++ rg` `[REV 3.1, review r51 READYL2-5: this clause is L2's, §14.3 D-4]`. `[r4 READY3-3]` `−t` is the WHOLE run's offset (`whole_maxoff`, and `omin`: `head` is at 0); the landmark K is the WINDOW's offset, `omin + at` (`facts.c:332`, `req.c:853`), signed and of EITHER sign: `(?<=e{10})eeeeeqzx`'s whole run `e^15 qzx` is at −10 with its window at `at` 10, so K = 0 (spelling measured). `[r2 S5]` Every `++` here keeps the FIRST positions (`rn_app`), so the stated offset stays the candidate's first position. Each candidate records its CONSUMED extent (`cons`, §5.4 A13), in the candidate's own positions: `[0, tail.n)` for `tail ++ rg`, `[0, head.n)` for `head ++ rg`, `[t, t + head.n)` for `lg ++ head`, each clipped at the stored bound. `best` is `rn_better` over the consumed best and the candidates | the root's bit is listed (`req_whole_run`'s `why` `dead`, §9) | W-L4 (L1), W-L9, W-T2, W-T2a, W-S4b (L2), S-L, W-L1, W-L3, W-L8, W-L10, W-L11..W-L14, W-T3, W-T3a, W-S4c (L3) |

What these rows settle, against each soundlook case (`[r2 S2]`: re-derived with both lowerings):

- **(a) `all` and materialized leftovers.** No row below TOP turns a guard into bytes, so `all`
  never sees one. `y(?:x(?<=yx))z`: in the group, `x` meets `x` and the leftover `y` is carried
  as the group's `lg` (`x` is `all`). Outside, it meets `y`. The run is `yxz` (spelling `yxz`
  measured), and rev 0's reading gave `yyxz`.
- **(b) ALT.** `xy[ac]b(?:(?<=ab)b|c)`: the branch `c` has no guard, so the alternation has none;
  the run is `xy[ac]b[bc]`. (Rev 1's `(?:(?<=a)b|c)` is an `A_CTX` PREV under default flags; with
  (a) it is an item too, and the row reads the same.)
- **(c) Stacking.** Two lookbehinds at one cursor: the right one's `lg` is a leftover across the
  left one (width 0, `all`), met with the left one's `lg` at EQUAL offsets.
  `[ac][ac]cc(?<=acc)(?<=cc)d`: `lg` `acc` (the meet of `acc` and `cc`), not `acccc`; the run is
  `[ac]accd`. `(?<=ab)(?<=b)c` (the second is an `A_CTX` PREV) gives `ab` the same way.
- **(d) Nesting.** A body's guards keep their own offsets (ITEM). `ab[xy][xy](?=(?<=xx)y)[xy]`:
  the lookahead's `rg` is `y` and its body's own `lg` is `xx`; the run is `abxxy`.
  `[ac][ac](?<=ac(?=cc))cc`: `lg` `ac`, the body's own `rg` `cc` at the cursor; the run is
  `accc`. Rev 1's one-character forms (`x(?=(?<=x)y)y`, `(?<=a(?=b))b`) read the same once the
  inner `A_CTX` is an item.
- **(e) tail/best.** Extension happens once, at TOP, and its offset is computed from the consumed
  tail length (W-L9).
- **(f) The reach across nesting.** A guard crosses only an `all` neighbour, whose width is
  exact, so the top-level leftover is exact and no minimum width is needed. "Back never shrinks"
  holds by construction: a leftover is absorbed, carried exactly, or dropped.
  `y*(?:ab(?<=xab)c)`: `x` is carried to the group's edge and dropped at `y*` (not `all`); the
  run is `abc` at reach 0, which W-L8 plants against.
  `(?:(?=abcd)ab)cd`: the group's `rg` `cd` meets the outer `cd` (CAT-R), and the run is `abcd`
  at reach 0. `(?:(?=abcd)ab)c?` (oracle M 0 3 on `abcd`): `rg` `cd` is dropped at `c?`, so the
  run is `ab`.
- **(g) The dead fact** `[r2 S6]` `[r3 READY-2, READY-10]`. DEAD is a value's bit, so a dead
  branch does not kill its parent. Numbered as §5.7's W-D1..W-D7: `foo(?=bar)baz` (W-D1,
  consumed `z` against the guard's `r`) and `(?<=ab)(?<=cb)c` (W-D2, guard against guard at −2)
  never match (oracle N) and list dead; `x(?:foo(?=bar)baz)?y` (W-D3, REP `m = 0`),
  `(?:foo(?=bar)baz|q)` (W-D4, ALT), `x(?!foo(?=bar)baz)y` (W-D5, negative) and
  `(?:foo(?=bar)baz){0}x` (W-D6) all match (oracle M) and list NOT dead. W-D5 is a STRUCTURAL
  NOTE, not a witness: L1 never walks a negative lookaround's body (E-4's unit, §4.1; the
  "(others)" row above), so the one walk-level-flag sabotage never sets DEAD there and no
  plant site exists; the other three live members do fail, because their inner positive
  lookaround is walked. W-D7 is W-T1's pattern, listed NOT dead (§5.7).

**A variable lookaround's fixed part** `[r1 F17]` `[r2 S8]` `[REV 3: at T a split repeat walls the description: `(?<=fo{1,3})bar` stays `bar`, §14.1 item 17]`. S4 point (2): a lookbehind body of
bounded variable width still constrains the offsets every group reaches, and the producer states
exactly that (§5.1: `(?<=fo{1,3})bar` gives `lg` `o`, back 1; `(?<=ab|b)c` gives `lg` `b`). Rev 1
called the body's `RbRuns.tail` the "one fixed-tail producer". Under the S8 ruling the producer is
the description placed at the cursor, which is the same module (alt_normal_form §3.5, one
description, its alphabet a parameter, r7 FIX-7). `docs/design/vlookbehind_pieces.md`'s HELD
fixed-tail hoist reads the description at each BRANCH's node, at code-point level at its VM call
site; the item reads it at the lookbehind BODY's node, byte level, united across groups. Two
readers of one description at two nodes, not two producers.

### 5.3 The producer: ONE source of exact per-offset context sets; the guard reads it `[r2 S8, RULED]` `[REV 3: "Where it lives", the window paragraph and "Bounds" are STALE: §14.1 items 1, 2, 12; the producer's home and form are §14.3 D-10 and §12's rev 3 addendum]`

**The ruling.** "The per-offset fact is ONE producer of EXACT per-offset subject sets at signed
offsets from the attempt start (ctx_span §3.3 `look-fixed`'s fact: union over branches, exact),
covering `A_CTX` and `A_LOOK` alike. The run's guard is a READER of it and derives its own cube
hull within `pos_set` locally ... L1 builds the producer's slice it needs at that shape ... and
files a D168 addendum naming where the producer lives, in the same change. No second producer
beside kset's frontier."

**What the producer computes.** Per positive one-sided context node, its ITEM (§5.1): terms
`{off, set[32]}` at signed byte offsets from the node's cursor, a form (EXACT/SUPERSET) and an
absent cell (FAILS for every member L1 builds). That is ctx_span §3.2's `MkCtx` record (one record
per item, `[r4 U-B4]`), with ctx_span §3.3's `ctx-onesided` (positive functions) and `look-fixed`
contributions. The sets are EXACT 256-bit sets, never hulls: the description's positions are
sets (§0), and neither `pos_set` nor bit 44 is read (§0's measurement). So the two defects
FIXIND-6 found in rev 1 are gone: the item is not weaker than `look-fixed` (`(?<=[a-z]x)` states
`{-2: [a-z], -1: x}` EXACT; the GUARD keeps only `x`, because `[a-z]` is not a cube, and that
loss is the run's own), and a RUN deny does not move it.

**The coordinate (flagged for the manager).** The ruling says "at signed offsets from the attempt
start". The producer states each item from its own CURSOR, which is ctx_span §3.3's own
coordinate ("contribution (offsets relative to the item's position `p`)"). An item whose cursor
sits at a fixed offset `d` from the attempt start is at `off + d` in the attempt's coordinates:
that shift is the `MkCtx` placement at span 0 (P1a/P1b), and TOP's (the run's `[omin, maxoff]`).
Where the cursor's offset varies (`[a-z]+foo(?=bar)`), only a reader that places the item against
its neighbours can use it, which the run does in `rr_cat`. Rev 2 reads the ruling as fixing the
FACT (exact per-offset sets) and its signed range, and the cursor as the producer's origin. If the
ruling means the attempt-start origin strictly, the guard would read only items at a fixed
offset, and every row of §5.6 after a variable-width piece would lose its mover; the census
would count that population.

**Where it lives (the D168 addendum L1 files).** D168 named `span_facts` in `src/facts/spans.c`, a *(superseded by cover_cap.md rev 4, 2026-11-15)*
file that was never built (ctx_span §3.1: span_facts is the extended k-set walk, owner `kset.c`). *(superseded by cover_cap.md rev 4, 2026-11-15)*
The producer has two halves by PLACEMENT, and one source each:

| half | placement | computed by | reads |
|---|---|---|---|
| in-span (`d >= 0`) | narrows `S_d` per thread inside span 0 | kset's frontier (`kset.c:686-700`, the `N_CTX` arm; built) | the lowered `N_CTX`'s set and 9-cell function (`ctxfn.def`), per thread with the previous side known |
| items | an item's terms from its cursor; placed by each reader | the description's item combinator in `src/facts/desc.c` (new at L1), called by `req.c`'s walk at the lookaround node | `A_CTX`: the node's set and function (`ctxfn.def`); `A_LOOK`: the body's description |

- **kset's existing `A_CTX` reading** is the in-span half, and stays as built: it needs the
  NFA's thread separation (ctx_span §3.4 "why the union is wrong"), which an AST item cannot give,
  and the lowered machine has no `A_LOOK` body to read (the NFA erases it). Both halves read the
  ONE truth table (`ctxfn.def`) for an `A_CTX`, so there is one definition of what the node
  constrains, and no second walk computes the same sets: the item half adds the out-of-span
  placement kset cannot reach. That is the ruling's second option, "the producer's `d >= 0` half
  is kset's".
- **Not a second producer beside kset's frontier**: P1a/P1b's records before and after span 0
  (`ctx-onesided` at the origin, `look-fixed`) READ the item, placed at span 0; their
  `look-fixed` row then needs no body walk of its own (ctx_span §3.3 planned one). `cover` reads
  EXACT items only, as D168 says.
- **Storage.** No stored item fact until a second reader exists (D77, F16): at L1 the walk calls
  the combinator inline. The `facts.def` row (`ctx_items`, `PF_CORE`, owner `req.c`, E2) arrives
  with P1a, the first second reader.
- **Bounds.** The item stores at most the description's `max_pos` (`PCREC_MAX_REQ_RUN_SCAN`)
  positions per group, the LAST ones (`desc.h:32-39`). A lookahead body wider than that loses its
  head terms: the guard is then empty, a sound loss the L1 census counts.

**The window: the scan begins before the start offset.** S4 point (4). A run with `omin = −t` is
found in `[max(0, search_from − t), subject_length)`:

- the WINDOW statement: span starts down to `-MF_MAX_BACK` and a floor (`MF_WFLOOR_SUBJECT`/
  `_EXPR`, `emit_dfa.c:6882-6897`). Its R span is walk-verified (A5) and never starts below 0
  (`walk_proves`), so BACK does not move it. The window spans are the producer's reader at
  U-locate ([LOOK-LOCATE], whose dependency is this producer, not U-G1);
- the PRESENCE statement (the pre-check, `req_site_define`) carries BACK as `omin = −t`: a kit
  contract change, together with `head_max` (§5.4 A1-A2);
- the span check (S4 point (6)) `[r1 F12]`: the kit honours each stated span's VERIFY flag (D172;
  `memfn.h:536-538`; pcrec states R `MF_VERIFY_NO`, `emit_dfa.c:6867`). A back span stated
  later, whether a filter (NO) or a checked span (YES), uses an existing kit mechanism. Until
  [LOOK-LOCATE] the item reaches the kit only through the presence run.

### 5.4 Readers and the reach each admits `[r1 F8]` `[r2 S1, S4, S7, S15]` `[REV 3: the line cites predate the tree at T; A1's kit change, A3's margin and A13's three deciders are STALE (§14.1 items 2, 3, 15, 16); the readers are the note's site map, the decisions §14.3]`

Every reader of the run walk's facts at `7b9ddd890`, found by grep for the accessors
(`pcrec_fact_req_*`, `pcrec_fact_run_pin*`, `pcrec_fact_stamp_req_*`) over `src/` and `cli/`, plus
the readers of K and `whole_maxoff` downstream of them (premise PREMISE-2, soundlook SOUNDLOOK-6),
re-checked at `dd2fe2de9` (and by the r2 critics at `f07aaef69`: every call site maps to a row;
the missed reader was `pcrec_req_pick`'s membership contract, now A13). `emit_vm.c` calls no
accessor, but the VM route reads A1-A3 through the exported emitters
`pcrec_emit_req_run_blocks`/`pcrec_req_site_in_prefilter` (`emit_vm.c:13474`),
`pcrec_emit_req_byte_check` (`:13583`) and `pcrec_emit_req_attempt_reentry` (`:13945`). So every
BACK change below applies to the VM caller's text too (its `search_from` is also what `\G` reads,
`emit_vm.c:13579-13582`), and the handoff is not DFA-only (`x(?<=ab)ab[a-z]*q`: VM,
`RX_REQ_HANDOFF "1"`, measured).

| # | readers (function, `emit_dfa.c` unless named) | assumption, with its cite | AHEAD admitted? | BACK admitted? |
|---|---|---|---|---|
| A1 `[r4 READY2-2, READY3-2]` | the presence statement `req_pres_spans` (`:1477-1508`), `req_site_define` (`:1536-1584`), `req_parts_in_whole` (`:8864-8872`); the kit field `s->head_max = (uint64_t)req_handoff_k(cx)` (`:1629`). `[r2 S15]` `site_kind_of` (`:1440-1455`) is dropped: it reads no run or offset | `omin = 0`, every occurrence at or after the start (`:1465-1467`, `:1501`); the kit's `omin` ">= 0 ... A negative value is refused" (`memfn.h:679-684`, `compose.c:608`), from the MATCH start; `head_max` is `uint64_t` (`memfn.h:820-824`); the presence run span states no consumed extent | yes in substance (a span is tested over `[start + omin, n)`, no upper bound), but NOT pcrec-only: the presence run span carries the consumed-extent fact (§8.2 part A), and `memfn.h:679-681`'s "presence bytes lie inside [start, end)" is the kit's sentence to change | NO: pcrec states `omin = −t`, a signed `head_max` and the consumed extent; the kit honours them (A2), one `MF_SITE_ABI` event, the kit's (§8.2 parts A and B) |
| A2 `[r2 S7]` | the pre-check's entry (`pcrec_emit_req_byte_check`, `:1699-1708`, which refuses any position but `search_from`, `memfn_sites.h:205-214`) and re-entry (`emit_req_reentry_use`, `:1724-1741`, `.lo = posvar`), and the VM caller | "any match it can still complete ... implies one wholly in [scan_position, n)" (`:1519-1529`) | yes | NO in pcrec's text, by design: the floor is the KIT's two uses, from the stated `omin`, clamped at 0 (entry `max(0, search_from + omin)`, re-entry `max(0, scan_position + omin)`). pcrec's hook shape (`.lo = posvar`, the ORIGIN assertion) is unchanged. L3's kit request |
| A3 `[r2 S1]` `[r4 READY3-2, READY3-3]` | the landmark K: `req_handoff_applies` (`:8826-8841`), `req_handoff_k` (`:8971`), `pf_handoff_applies` (`:9095`), `req_landmark_hit_ppm` (`:8994-8999`), `req_pick_shadow` (`:11187-11255`), `req_handoff_stamp` (`:9133-9139`), the K admission's margin `pcrec_landmark_margin` (`:9057-9063`, via `req_landmark_admits` `:9064-9072`, which `pf_handoff_applies` and `req_pick_shadow` call; its other caller `lmwalk.c:248` passes a non-negative K and does not move), and its sinks `emit_req_handoff_rest` (`:1167-1204`) and `emit_req_landmark_move` (`:7793-7813`, via `pf_emit_handoff` `:7769-7783` and `pcrec_emit_req_attempt_reentry` `:7823-7832`) | invariant F (`facts.h:79-87`), so the hit `c >= p` ("`c >= posvar` always", `:1158`); `-1` is the "no run" SENTINEL (`facts.h:566-573`), declined at `:8835`; the margin casts K, `(unsigned long long)k * h >= 1000000u` | yes (K bounds the run's START) | NO, and rev 1's cell was WRONG: at `k <= 0` `emit_req_handoff_rest` emits nothing (the body starts at the kit's hit `c`) and `emit_req_landmark_move` sets `pos = landmark_position`; under BACK the hit can lie BEFORE the match start, so both start the body too early and REPORT A MATCH BEFORE THE START OFFSET (W-L10: (2,7) where (4,7) is expected). The only sound move is `pos = max(posvar, c − K)` with K signed, computed without a `size_t` wrap; the re-entry re-asks while `c − K < pos`. match_api §6.3.7¶11's `max(startpos, that − K)` already is this form and holds for signed K. A signed K needs a "none" state apart from −1 first. `[r4 READY3-3]` K is the WINDOW's offset, `omin + at`, of EITHER sign, not `−t`: at K = 0 with `omin` < 0 today's text moves nothing and the body starts at the hit (W-L11); at K > 0 the scan floor `posvar + omin` lets the hit fall below `posvar`, and today's `handoff_position - posvar` wraps (W-L12); on re-entry the re-ask from `pos + omin` can return a hit below `pos`, and `landmark_position - pos` wraps into a backward move that re-runs the same attempt forever (W-L14). `[r4 READY3-2]` The margin's cast turns every negative K into ~2^64, so the margin is −1 and NEXT's `handoff-reentry` row declines at every BACK landmark (sound, silent): the admission reads `max(K, 0)` (a landmark that begins at or before the match start costs no step back), and the kit's twin admission (`memfn/src/presence.c:199-222`, `unsigned long long k = s->head_max`) is told the same fact (§8.2 part B), else `req_pick_shadow`'s `landmark` record disagrees |
| A4 | the set's offsets `req_set_maxoff` (`facts.h:141-147`; `RbSet.off` `uint32_t`, `facts_derive.h:74-81`) and its readers `req_set_leads_applies` (`:8658-8659`), `req_set_leads_own` (`:11045-11049`), `req_byte_dominated_by` (`:8586`), `req_none_applies` (`:8607`) | a set member is a byte at a non-negative offset | unchanged | unchanged: the SET takes no guard byte (T4 is a run rule, §1 non-goals); CAT-SET adds only CONSUMED bytes, at non-negative offsets |
| A5 `[r4 READY2-6]` | the window statement `pf_window_of` (`:6825-6826`), `us_run_pin` (`:7364`), `ofs_test_of` (`:7419`), `ofs_test_verifies_run` (`:7487-7505`), `pf_run_applies_common` (`:7374`), `pcrec_run_pin` (`kset.c:294-318`, called `facts.c:343` on the `req_run` window) | SELF-VERIFYING: R is stated only where the k-set walk proves it at a non-negative offset (`walk_proves`, `:6808-6813`; the pin check `:6827-6834`); the pin picks over EVERY exact window position and pins ALL-OR-NOTHING over the maximal exact stretch around its pick (`l <= nwalk`) | NO as is (rev 2's "an unproved position is not stated" is `pf_window_of`'s widening, which runs only after a pin exists): the k-set walk never reaches past the consumed end, so an extended run loses its pin (`bar(?=baz)` today: `run_pin 0`, `RX_DFA_PREFILTER "run-pinned"`, `RX_REQ_WHY "dominated"`, `kset_walk` 3 positions, measured; its L2 window `barbaz` has 6). Fix: `pcrec_run_pin` reads `cons` (its pick and its stretch inside the consumed extent; the guard positions stay pre-check compare bytes), so the pin and the `run-pinned` prefilter stay. `ofs_test_verifies_run` still asks every WINDOW position at the pin, so the guard positions are not verified by the start search: the pre-check is no longer dominated, a listed mover (`RX_REQ_WHY` `dominated` → `emitted` on `bar(?=baz)`, §5.6; hand-derived from the two functions) | the same fix (L3 reads `cons`; a BACK run's guard positions lie before `cons`) |
| A6 | the run compare `req_run_tests` (`:1093-1104`), `req_note_run` (`:1221`), `req_part_window` (`:1119-1131`) | the compare tests the run AT its hit, `[0, len)` from the hit (`:1128-1130`) | yes | yes: what moves for BACK is A1-A3, not the compare |
| A7 `[r4 READY2-5]` | the stamps `<PREFIX>_REQ_RUN`, `_REQ_BYTE` (`pcrec_emit_prologue`, `:15831-15859`) and the contract sentences that define the run | "a literal run every match must contain" (`match_api.md` §6.3.7¶6); tuning §2.28¶1 "the longest run of contiguous literal POSITIONS every match must contain"; `docs/spec/findings.md` §4's row "the necessary run's scan member" ("the window's truncation keeps pcrec's own index") | NO in wording (spec hunks, D80): ¶6 and tuning §2.28¶1 take the attempt sentence; the findings.md §4 member row takes the kit-owned member over the consumed extent (§8.2). CHECKED-UNCHANGED: ¶4 (`_REQ_BYTE`, "a byte every match must contain", kept true by A13), ¶5 and tuning §2.27¶4 ("a member of the necessary set"), ¶7 (`@idx`, the member the `memchr` scans, a consumed position), ¶11 (K bounds the run START, unchanged by AHEAD), findings.md §4's window row ("any window is necessary") | NO in wording (the same hunks, BACK half; tuning §2.28¶1's bit-31 sentence is L3's, §8) |
| A8 `[r4 READY3-4, ADMITTED]` | `req_handoff_entry_applies` (`:8908-8923`) and its caller `req_handoff_attempts_applies` (`:8929-8932`), the VM route's `handoff-attempts`/`handoff-attempts-entry` rows; their text `emit_req_handoff_rest` (entry) and `pcrec_emit_req_attempt_reentry` → `emit_req_landmark_move` (re-entry) | reads `whole_maxoff`, declines `< 0` (`:8921`) | yes | ADMITTED, as ruled: the `whole_maxoff < 0` conjunct is DELETED (a special case the general move covers) and both rows run A3's signed move, entry and re-entry. Rev 2's "declined, which is sound" was a silent default-flags speed loss: today `(?<=foo)bar(\w)\1` (VM, `RX_VM_PREFILTER "none"`) and every lookbehind pattern under `-fno-prefilter` stamp `RX_REQ_HANDOFF "0"` (measured), and at L3 the decline would move them to `"none"` with no pick row deciding it. Mover: `"0"` → the signed K (`"-3"` on `(?<=foo)bar(\w)\1`, its whole run `foobar` at −3; `foobarxx` from 3: c = 0, first attempt `max(3, 0 + 3)` = 3, (3,8), the oracle's). Spec hunks tuning §2.41¶8b and match_api §6.3.7¶11 (§8). Witnesses W-L13 (entry), W-L14 (re-entry: the re-entry move's reaching witness, which READY3-2 found missing) |
| A9 `[r2 S12, S15]` `[r4 READY3-3, READY3-8]` | the derivations: `pf_derive_req_walk` (`src/facts/facts.c:201-249`; the run's bound `whole_maxoff = run.off` at `:236`, the floor admission at `:231`), the landmark derivation that MAKES the −1 sentinel (`facts.c:332-333`), its deny/reset path (`facts.c:104`, `req_landmark_maxoff = -1`), its printer (`facts.c:840`, `< 0` → `none`) and `pcrec_fact_req_run_maxoff`'s −1 (`facts.c:581`; no caller outside `facts.c`, so it retires for free) | `maxoff >= 0`; −1 = none | yes | NO: the sentinel split (A3) lands here first; `omin` is derived beside `maxoff` (`RbRun.omin` → `ReqRun.omin`, its own `facts.def` row `req_run_omin`, §9). `req_run_omin` lists the WHOLE run's `omin` (the presence span's, which the kit's floor reads); the window's offset is `omin + at`, which is K (`req_landmark_maxoff`). `ReqRun.maxoff`/`whole_maxoff` already have a none state (`len`/`whole_len < 2`, `facts.h:82-84`), so the stated/none bit is needed for K only |
| A10 `[r4 READY3-5]` | the pick arithmetic: `pcrec_req_window`/`pcrec_req_pick` (`src/facts/req.c:826-876`, `whole_maxoff + at`), `pcrec_find_run_scan_index` (`src/core/findings.c:745`), `pcrec_find_run_window_start` (`:780`), `pcrec_find_set_pick` (`:686`, also from `emit_dfa.c:8598`) | offsets non-negative | yes | yes, ALREADY SIGNED: `ReqRun.whole_maxoff`/`maxoff` are `long long` (`facts.h:88-89`), `RbRun.off` `long long` (`facts_derive.h:114`), the window offset is `pcrec_sat_add(run->whole_maxoff, s, PCREC_W_UNBOUNDED)` (`req.c:853`), correct for a negative base, and the picks take no offset. No change (rev 2's "NO: signed arithmetic" named a change with nothing to change); kept in the re-grep |
| A11 | trace-build and choice readers: `req_rest_own_sig` (`:11064-11083`), `req_use_row` (`:8946`), `req_use_whole` (`:8961`) | offset-free, or attempt-relative | yes | yes (at worst a lost dismissal, sound) |
| A12 `[r3 READY-7]` | the `--emit-facts` printers (`facts.c:772-866`; the only reader of `req_pieces`, `:804`), the `why` renderer `fd_why` (`src/dump/facts_dump.c:93-121`, an exhaustive switch over `PfWhyCode`: L1 adds `dead` and `harness:`), the status decision `pf_done_why` (`facts.c:169-182`: a dead run is `derived`, not in its `decl` list, §3.7) and `run_facts_checks.sh`'s status/why pairs | the listing's vocabularies (`facts_listing.md` §4.1.2, §4.1.3) | the dead fact's `why` (L1); L2's widened sentence | `req_run_omin`'s value and negative K values: L3's hunks |
| A13 `[r2 S4, RULED]` `[r4 READY2-2, READY3-6]` | `req_byte`'s exact scan member: `pcrec_req_pick` (`req.c:866-876`, "every value here stays a member of `req_set`") and the scan-index pick it reads (`pcrec_find_run_scan_index`, `findings.c:745`, which also cuts the window, `req.c:841`); `req_run_member` (`emit_dfa.c:1058-1076`) and every reader that goes through it, `req_run_tests` (`:1102`), `req_note_run` (`:1222`), `req_set_leads_own` (`:11050`), `req_pick_shadow` (`:11229`) and both stamps `<PREFIX>_REQ_BYTE`/`_REQ_RUN` (`:15831`, `:15859`); the kit's window-family `run_member` (`memfn/src/window.c:855-890`, tie `T_MASS_STRETCH` `:84-92`) and its presence picks `pres_layout_check` (`memfn/src/compose.c:688`) | the scan member is a byte every match contains: tuning §2.27¶4, match_api §6.3.7¶5, `tests/codegen/reqcube_check.py:256-257` (check 4); and the member has THREE deciders held equal by two loud checks: pcrec's `pcrec_find_run_scan_index` (`r->idx`), the kit's `run_member` (verify YES: the least-mass position of ALL of R) and the kit's presence picks; `req_run_member` raises "internal error" when the first two differ | NO as is: `barbaz`'s pick is `z` (122, measured), a guard byte. `[r4 READY2-2]` A consumed-only pick in pcrec alone is not a fix: the kit's reply still ranks every position, so every affected compile fails loudly (the r4 plant: `[a-z]?[a-z]abc`, `barbaz`, `xbarbazq*` → "the window family's run member N is not the run window's own index 0"). Fix: ONE decision, the KIT's (D172; §8.2). pcrec states the consumed extent `cons` (`RbRun.cons`/`ReqRun.cons`, `[lo, hi)` in positions, written by TOP) on the run window and on the presence run span, and READS the kit's member at every reader, the window cut included; `pcrec_find_run_scan_index` leaves the member's path | NO as is, the same fix and the same request: `(?<=qz)ab`'s L3 run `qzab` would scan `z` (the spelling `qzab`: `req_byte 122`), a lookbehind byte outside `req_set` {97,98} (W-S4c). At L1 (reach 0) every position is consumed, and CAT-SET keeps a narrowed exact byte in the set (`x(?=qr)[pq]r`: run `xqr`, pick `q`, which today's set `{114,120}` lacks) |

`[r4 READY2-2, READY2-6, READY3-4, READY3-5]` `[REV 3: STALE: the kit's part is delivered and the member is no longer pcrec's to cut; §14.3 D-14]` So **AHEAD is not pcrec-only.** It needs the kit's
consumed-extent fact and its member over it (A1, A13: §8.2 part A, the kit's `MF_SITE_ABI` event,
which L2's go waits for), pcrec reading that member at every reader (A13), the pin reading `cons`
(A5), and A7's/A12's spec hunks. **BACK needs changes at these sites**: the kit's `omin`/`head_max`
and its floor plus part A's fact (A1, A2: the kit's), A3 the sentinel split, a signed K of either
sign, the margin's `max(K, 0)` and the two move emitters, A8's two attempt-loop rows admitted at
signed K, A9 the derivation's sentinel and `omin`, A5 and A13 as AHEAD, and A12's listing hunks.
A10 needs no change. The fact has ONE reach, raised for every reader together in the unit that
audits them (L2 for AHEAD, L3 for BACK). A reader added later is
admitted only by adding its row here (G3). The build lane re-greps at its own base.

### 5.5 The BACK bound is a declared policy, a step-back cost cap `[r1 F9]` `[r2 S10, RULED]`

`MF_MAX_BACK` (`memfn.h:235`) bounds WINDOW span starts and term offsets (`:586-591`, `:614`). L3
routes BACK through the PRESENCE `omin`, which has no such bound (an `int32_t` refused only below
0), so rev 0's cap was borrowed from a seam L3 does not use. Rev 2:

- **The row and its purpose.** TOP admits a BACK candidate only if `t <= lb_bytes`; otherwise the
  run keeps its reach-0 value. The row is a per-call STEP-BACK COST cap: it bounds how many bytes
  before `search_from` one pre-check call scans (a find-all regime pays it per call, §11). It is
  NOT a safety bound: the scan is memory-safe at any `t`, because it is clamped at subject offset
  0 and the pre-check compares bytes without decoding them.
- **Per encoding.** `lb_bytes` = `Ctx.lb_max` (PCRE2's `max_lookbehind`, in characters,
  `src/core/internal.h:3979-3997`) times the encoding's widest character in bytes: `lb_max` under
  `byte`, `4 · lb_max` under `utf8`. It is a walk parameter (§3.7's table).
- **It is not an invariant, and the measured case is NON-UTF only.** `lb_max` is a running max
  per construct ("nesting does not accumulate"), so a nested lookbehind can need more than it.
  `(?<=c(?<=bc)d)e`: `_VALID_LB 2` under both encodings; libpcre2 10.46 matches it on `bcde` FROM
  OFFSET 3 at (3,4) in non-UTF mode, reading byte 0, three bytes back; in UTF mode it does NOT
  match from 3 (`N`; from 2, `M 3 4`; measured). The item gives `lg` `bcd`, `t = 3`: refused under
  `byte` (3 > 2), ADMITTED under `utf8` (3 <= 8). Both are sound: the run is a necessary
  condition of every match, and under UTF there is no match from 3 to lose. So the row is a sound
  refusal, never a check that would fire.
- **What the kit admits is the kit's.** `[REV 3: the kit states no bound on a negative run `omin` (memfn.h, MF_SITE_ABI 27), so TOP reads `lb_bytes` alone]` The `omin`/`head_max` change (A1-A2) may carry the kit's
  own bound. If it does, TOP's row reads the smaller of the two, and both are named in L3's
  request.

### 5.6 Predicted movers (rule applied; spellings measured where equivalent) `[r2 S2]` `[REV 3: the "today" column and several L1 cells are stale at T; re-measured in §14.2]`

| pattern | today (measured) | reach `[0, maxoff]` (L1) | full reach (L2/L3) |
|---|---|---|---|
| `xyz(?<=yz)abc` | `abc` | `xyzabc` (E2 already: E-5 is the unit; L1's `lg` `yz` meets `xyz`'s tail, no change; spelling measured) | same |
| `a(?=b)[bc]` (`A_CTX` NEXT) | none | `ab` (ITEM via the `A_CTX` row, then CAT-R; spelling measured). No speed effect: the DFA's `cover` decides presence (`RX_DFA_SCAN "cover"`) | same |
| `xy(?=bc)[bc]c` | `xy` | `xybc` (CAT-R) | same |
| `y(?:x(?<=yx))z` | `yx` | `yxz` (spelling measured) | same |
| `(?:(?=abcd)ab)cd` | `abcd` | `abcd` (no mover) | same |
| `xy[ac](?:(?<=a)b\|c)` | `xy[ac]` | `xy[ac][bc]` (ALT drops the `A_CTX` PREV's guard; E2 alone gives the same value) | same |
| `xy[ac]b(?:(?<=ab)b\|c)` | `xy[ac]b` (`78796162/fffffdff`) | `xy[ac]b[bc]` (ALT) | same |
| `[ac][ac]c(?<=ac)(?<=c)d` | `[ac][ac]c` | `[ac]acd` (stacking, the second an `A_CTX` PREV) | same |
| `[ac][ac]cc(?<=acc)(?<=cc)d` | `[ac][ac]cc` (`61616363/fdfdffff`) | `[ac]accd` (stacking) | same |
| `ab[xy](?=(?<=x)y)[xy]` | `ab[xy]` | `abxy` (nesting; the inner `A_CTX` PREV is the body's own `lg`) | same |
| `ab[xy][xy](?=(?<=xx)y)[xy]` | `ab[xy][xy]` (`61627878/fffffefe`) | `abxxy` (nesting) | same |
| `x(?=ab\|ac)a.` `[r1 F10]` | none | `xa`: the item's hull is `a[bc]`, but `a.` is not `all` (`.` is a gap), so `[bc]` meets no stored run position and is dropped (hand-derived; `xa[bc]` is necessary, reachable only when guards meet DESCRIPTION positions: §10 U-descguard) | same |
| `foo(?=bar)baz` | `baz` | DEAD; run `foobaz` (EMPTY-MEET: the emptied position keeps `z`; oracle N, N) | same |
| `bar(?=baz)` | `bar` (`run_pin 0`, `"run-pinned"`, `"dominated"`) | `bar` | `barbaz`, `omin = maxoff = 0`, the kit's scan member among `bar` (A13); `[r4 READY2-6]` the pin stays on `bar` (A5 reads `cons`), and the pre-check is no longer dominated: `RX_REQ_WHY` `dominated` → `emitted` (hand-derived); `xyz(?=abc)` (`run_pin 0`, `"handoff"` today) moves the same way |
| `(?<=foo)bar` | `bar` | `bar` | `foobar` at −3 |
| `(?<=fo{1,3})bar` | `bar` | `bar` | `obar` at −1 (item `{-1: o, -2: {f,o}}`, SUPERSET) |
| `(?<=ab\|b)c` | none | none | `bc` at −1 |
| `(?<=ab)ab[a-z]*q` | `ab` | `ab` | `abab` at −2 (W-L10's) |
| `(?<=\x00\x01)[a-z]+` | none | none | `\x00\x01` at −2 (the plan row's locate example; `[a-z]` is not a cube) |
| `(?<=qz)ab` `[r4 READY3-6]` | `ab` (`req_set` 97,98) | `ab` | `qzab` at −2; the scan member stays `a`/`b` (A13; the spelling `qzab` would scan `z`, 122) |
| `(?<=e{10})eeeeeqzx` `[r4 READY3-3]` | `eeeeeqzx` (K 0, `"emitted"`) | same | `e^15 qzx` at −10 (`omin` −10), window at `at` 10, K = 0 |
| `(?<=e{8})eeeeeeeeeeqzx` `[r4 READY3-3]` | `e^10 qzx`, window at 5, K 5 | same | `e^18 qzx` at −8, window at 13, K = 5 (unchanged), `omin` −8 |
| `(?<=foo)bar(\w)\1` `[r4 READY3-4]` | `bar`, `RX_REQ_HANDOFF "0"` (VM, `RX_VM_PREFILTER "none"`) | same | `foobar` at −3, `RX_REQ_HANDOFF "-3"` (A8 admitted); every lookbehind pattern under `-fno-prefilter` the same way (`(?<=foo)bar`, `(?<=ab)ab[a-z]*q`: `"0"` today) |

Today's values are measured (rev 1's `facts_today.out`/`facts_extra.out`, rev 2's
`spanarms3_evidence/facts_w.out`).

### 5.7 Witnesses (each can fail; libpcre2 answers measured) `[r2 S2, S3, S5, S6, S14]`

Failure mechanism as in §3.6: each sabotaged run clears the 16-bit floor (each spelled sabotage
lists a `req_run`, measured), is absent from the subject, is not pinned (the "k-set" column shows
the position where the sabotaged run differs from the witness's k-set, or where the k-set is not a
singleton), and the witness's locator does not decide presence (the "scan" column, measured at
`c054e38e7`). `[r3 READY-1]` A fourth condition: the position where the sabotaged run differs
from the correct one lies INSIDE the emitted window (`pcrec_req_window`, `req.c:826-852`:
`PCREC_MAX_REQ_RUN_EMIT` = 8 positions, `limits.def:399`), or the gate tests the whole run
(`--memfn=no-fd-pres-pick`, the emitted `rx_reqrun_whole`). Re-checked for every L1 witness
below: each correct and sabotaged run is at most 8 positions, so the window is the whole run,
except W-T1's 32-position runs, which is why W-T1 runs under the flag. Every witness below lists `kinds lookaround` (an `A_LOOK`) unless marked `A_CTX`, so
its plant site exists under default flags.

`[r4 READY2-1, READY3-1, READY3-9]` `[REV 3: condition (5)'s window is retired: W-T2/W-T3 become answer witnesses, W-L11's K is −10, W-L12 is RETIRED; §14.1 items 4, 6, 7]` **L2/L3 witnesses: two more conditions.** (5) The window
condition re-checked for L2/L3 at `1ffcce0c1`: `--memfn=no-fd-pres-pick` adds only a whole-run
PRESENCE test from `search_from` (the emitted `rx_reqrun_whole`, read on the spelling
`x a^12 b^20`; `RX_REQ_HANDOFF` stays the WINDOW's K), so a sabotage whose wrong run is still a
substring of the subject cannot fail under the flag either. A TOP-offset sabotage fails on the
answer only where it moves the WINDOW's K and the window holds a byte that occurs once (W-T2a,
W-T3a); otherwise it is a listing row. (6) A pre-check site must exist: five of the six L3
witnesses stamp `RX_REQ_WHY "dominated"` today (no pre-check, so no plant site; measured: S-L,
W-L1, W-L3, W-L10, W-T3; W-L8 is `"emitted"`). At L2/L3 a run that extends past the consumed
positions is not verified by the start search (A5: the pin covers `cons` only, and
`ofs_test_verifies_run` asks every window position), so the pre-check is predicted `"emitted"`
(hand-derived). Each L2/L3 gate row therefore checks `RX_REQ_WHY "emitted"` and the expected
`RX_REQ_HANDOFF` on its pattern BEFORE its plant counts; a row whose WHY stays `"dominated"`
is reported, not counted.

| id (row; unit gate) | planted error | pattern, subject, expected (oracle) | correct | sabotaged, and why it fails | scan / k-set (measured) |
|---|---|---|---|---|---|
| S-L (alt_normal_form §3.5; E2, L1, L3) | the lookbehind's body read as CONSUMED (offset 0, not −3) | `(?<=foo)bar` on `foobar` from 3: (3,6) | E2/L1: `bar`; L3: `foobar` at −3 | `foobar@0`: a pre-check from 3 finds none: NOMATCH | VM `unanchored`, `RX_REQ_WHY "dominated"` today `[r4 READY3-9]`; k-set `98,97,114` |
| W-L1 (TOP BACK floor; L3, the KIT's witness) `[r2 S7]` | the kit's emitted pre-check scans from `search_from`, not `max(0, search_from + omin)` | `(?<=foo)bar` from 3: (3,6); from 2: (3,6); from 4: NOMATCH | the scan from 0 finds `foobar` | the scan from 3 misses it: NOMATCH where (3,6) is expected. Plant site: the kit's text (A2) | as S-L |
| W-L2 (CAT-EDGE; L1) | a carried leftover materialized as head bytes with `all` kept | `(?:(?=abcd)ab)cd` on `abcd`: (0,4) | `abcd` | `abcdcd`: absent, NOMATCH | VM `unanchored`; k-set 4 deep, the sabotage's positions 4-5 unpinned |
| W-L3 (ITEM, several groups; L3) | the item's −2 term taken from the FIRST group, not the union | `(?<=ab\|b)c` on `xbc`: (2,3) | `bc` at −1 | `abc` at −2: absent, NOMATCH | VM `unanchored`, `"dominated"` today `[r4 READY3-9]` (run none, `"memchr"`); k-set `99` |
| W-F5 (ITEM + CAT-L; L1) `[r1 F5]` | the same plant, reachable at reach 0 | `[ac]b(?<=ab\|b)c` on `cbc`: (0,3) | `[ac]bc` | `abc` (`a` ∩ `[ac]`): absent, NOMATCH | VM `unanchored`; k-set `[2],98,99` (position 0 not a singleton) |
| W-L4 (FACT, the reach leak; L1) `[r2 S14]` | at reach 0 an `rg` kept at TOP | `bar(?=baz)` | `bar` | `barbaz`: sound for every reader, so it cannot move an answer; checked on the listing and the stamp at L1 (at L2 the correct value IS `barbaz`, so L2 cannot tell them apart) | — |
| W-L5 (CAT-R; L1) `[r2 S3]` | the guard laid end to end with `r` (met at the arm, rev 0's text) | `xy(?=bc)[bc]c` on `xybc`: (0,4); on `xybb`: NOMATCH | `xybc` | `xybc[bc]c`: absent from `xybc`, NOMATCH | VM `unanchored`; k-set `120,121,[2],99` (position 2) |
| W-L6 (CAT-EDGE, non-`all` `r`; L1) | a leftover carried across a non-`all` neighbour, shifted by its `maxw` | `(?:(?=abc)a.?)[bc]c` on `abc`: (0,3) | `[bc]c` (15 bits, under the floor, so no run check) | `cc` (16 bits, spelled `cc` lists a run): absent, NOMATCH | VM `unanchored`; k-set `97,[255],[2]` |
| W-L7 (CAT-EDGE, F2 (a); L1) | a carried leftover materialized as head bytes | `y(?:x(?<=yx))z` on `yxz`: (0,3) | `yxz` | `yyxz`: absent, NOMATCH | VM `unanchored`; k-set `121,120,122` (position 1) |
| W-L8 (CAT-EDGE, F2 (f); L1 and L3) `[r2 S14]` | a leftover kept as consumed at a non-`all` left neighbour | `y*(?:ab(?<=xab)c)` on `xabc` from 1: (1,4) | `abc` (`x` dropped at `y*`) | `xabc` at reach 0: a scan from 1 finds none: NOMATCH. The plant is a CAT-EDGE row, red at reach 0 | VM `unanchored`, `RX_REQ_WHY "emitted"` today; k-set `[2],[3],[4]` |
| W-L9 (TOP, F2 (e); L2) `[REV 3.1, review r51 READYL2-3: the correct run is `[a-z]abc` at K 1, the plant gives K −1; numbers in §14.4 L2 Tests]` | the extended candidate's offset computed from the EXTENDED length | `[a-z]?[a-z]a(?=bc)` on `zzabc`: (0,3) | `abc` at `maxoff` 2 | `maxoff` 0: an attempt at 0 is admitted only with `abc` at 0, the handoff skips it, and the first answer is no longer (0,3) | VM `unanchored`, `RX_REQ_HANDOFF "2"` today; k-set `[26],[26]` |
| W-L10 (A3, the BACK move; L3) `[r2 S1]` | rev 1's move: at `K <= 0` the body starts at the hit (`pos = landmark_position`) | `(?<=ab)ab[a-z]*q` on `abababq` from 3: (4,7); from 2: (2,7) | run `abab` at −2 (K = −2); scan floor 1, hit `c = 2`, body from `max(3, 2 + 2)` = 4: (4,7) | the body starts at 2 and reports (2,7), a match before the start offset | VM `unanchored`, `"dominated"` today `[r4 READY3-9]`; k-set `97,98,[26]` (positions −2/−1 lie outside the k-set: not pinned). Twins: `abab[a-z]*q` `RX_REQ_HANDOFF "0"` (DFA), `x(?<=ab)ab[a-z]*q` `"1"` (VM) |
| W-L11 (A3 at K = 0, `omin` < 0; L3) `[r4 READY3-3]` `[REV 3.1, review r51 READYL2-2: RETIRED, cannot fail with the window gone, §14.1 item 7]` | today's move kept at K = 0 (no text: the body starts at the hit) | `(?<=e{10})eeeeeqzx` on `e^15 qzx`: (10,18) from 0, 5, 10; NOMATCH from 11, 12 | whole run `e^15 qzx` at −10, window at `at` 10, K = 0; from 11: floor 1, hit c = 10, body at `max(11, 10)` = 11: NOMATCH | the body starts at 10 and reports (10,18) from 11 and 12, a match before the start offset (the r4 critic's real plant; re-derived here) | VM `unanchored`, `"emitted"`, `RX_REQ_HANDOFF "0"` today |
| W-L12 (A3 at K > 0, the wrap; L3) `[r4 READY3-3]` | today's entry text kept (`handoff_position - posvar > K`, unsigned) | `(?<=e{8})eeeeeeeeeeqzx` on `e^18 qzx`: (8,21) from 0, 8; NOMATCH from 9, 13, 14, 15 | whole run `e^18 qzx` at −8, window at 13, K = 5; from 14: floor 6, hit c = 13, body at `max(14, 8)` = 14: NOMATCH | `13 − 14` wraps, the branch subtracts K: the body starts at 8 and reports (8,21) from 14 (hand-derived) | VM `unanchored`, `"emitted"`, `RX_REQ_HANDOFF "5"` today |
| W-L13 (A8 entry row at signed K; L3) `[r4 READY3-4]` `[REV 3.1, review r51 READYL2-6 (4): the plant's reason is not a wrap: today's entry text emits NO move block at K <= 0 under `byte` (`if (k > 0 \|\| round.len > 0)`), so the attempt is at c = 2 and answers (2,7) from 3 against the oracle's (4,7); the conclusion holds]` | today's entry text kept on the VM attempt loop's `handoff-attempts-entry` row | `(?<=ab)ab[a-z]*q(\w*)\1` on `abababq`: from 3 (4,7); from 2 (2,7); from 5 NOMATCH | whole run `abab` at −2, K = −2; from 3: floor 1, c = 2, first attempt at `max(3, 4)` = 4: (4,7) | `2 − 3` wraps, the first attempt is at 2: (2,7) from 3 | VM, `RX_VM_PREFILTER "none"`, `"emitted"`, `RX_REQ_HANDOFF "0"` today (entry row only: the emitted attempt loop has no landmark re-entry, read) |
| W-L14 (A8 re-entry row, the re-entry move's reaching witness; L3) `[r4 READY3-2, READY3-4]` | today's `emit_req_landmark_move` text kept (`landmark_position - pos > K`, unsigned) | `(?<=ab)ab(\w)\1` on `xababab-` from 0, 3, 4: NOMATCH | whole run `abab` at −2, K = −2; from 3: floor 1, c = 1, first attempt at 3 fails; re-entry at 4 re-asks from floor 2, c = 3, `pos = max(4, 5)` = 5 fails; re-ask from floor 4 finds none: NOMATCH | the re-ask returns c = 3 below `pos` = 4, `3 − 4` wraps, `pos` moves BACK to 3, and attempt 3 re-runs forever: the gate's timeout fires (hand-derived) | VM, `RX_VM_PREFILTER "none"`, `"emitted"`, `RX_REQ_HANDOFF "0"` today, with the re-entry emitted (read: `landmark_position < attempt_position` re-ask) |
| W-A1 (ALT; L1) `[r2 S2]` | a guard only one branch carries is kept | `xy[ac]b(?:(?<=ab)b\|c)` on `xycbc`: (0,5); on `xycbb`: NOMATCH | `xy[ac]b[bc]` | `xyab[bc]`: absent from `xycbc`, NOMATCH | VM `unanchored`, `"emitted"` today; k-set `120,121,[2],98,[2]` (position 2) |
| W-S1 (CAT-EDGE, stacking; L1) `[r2 S2]` | stacked leftovers concatenated (`acc` ++ `cc`), not met at equal offsets | `[ac][ac]cc(?<=acc)(?<=cc)d` on `caccd`: (0,5); on `ccccd`: NOMATCH | `[ac]accd` | `ccccd` (the concatenated `acccc` meets the left four positions with `cccc`): absent, NOMATCH | VM `unanchored`; k-set `[2],[2],99,99,100` (position 0) |
| W-N1 (ITEM, nested lookbehind in a lookahead; L1) `[r2 S2]` | the body's own guard flattened into its head at offset 0 | `ab[xy][xy](?=(?<=xx)y)[xy]` on `abxxy`: (0,5); on `abxyy`: NOMATCH | `abxxy` | `ab[xy][xy]x` (`rg` `xxy` at 0 meets the next `[xy]` with `x`): absent, NOMATCH | VM `unanchored`; k-set `97,98,[2],[2],[2]` (position 2) |
| W-N2 (ITEM, nested lookahead in a lookbehind; L1) `[r2 S2]` | the body's tail taken with its inner lookahead's guard appended | `[ac][ac](?<=ac(?=cc))cc` on `accc`: (0,4); on `cccc`: NOMATCH | `accc` | `cccc` (`lg` `accc` right-aligned, its `cc` meets `[ac][ac]`): absent from `accc`, NOMATCH | VM `unanchored`; k-set `[2],[2],99,99` (position 0) |
| W-F4 (REP row 1, F4; L1 on E1) | a min-0 repeat of a width-0 body keeps its guard | `x(?=ab)?a[bc]` on `xac`: (0,3) | `xa[bc]` | `xab`: absent, NOMATCH | VM `unanchored`; k-set `120,97,[2]` (position 2) |
| W-RG (REP through CAT; L1 on R1) `[r2 S3]` | a copy's `rg` laid end to end with the next copy | `(?:abc(?=ab)){2}` on `abcabcab`: (0,6); on `abcabcac`: NOMATCH | `abcabc` | `abcababc`: absent, NOMATCH | VM `unanchored`; k-set `97,98,99,97,98,99` (position 5: `a` against `99`) |
| W-C1 (ITEM, `A_CTX`; L1) `[r2 S2]` | an `A_CTX`'s PREV read as NEXT | `ab(?<=b)[bc]d\w*e` on `abcde`: (0,5) | `ab[bc]d` | `abbd`: absent from `abcde`, NOMATCH | `A_CTX` (`kinds none`), DFA `unanchored` (not `cover`); k-set `97,98,[2],100,[63]` (position 2). Under `-fno-ctx-node`: `kinds lookaround`, VM, the same run today; the equality is vacuous on this row (`ab[bc]d` both ways, `[r3 READY-4]`), so L1's gate lists it on `a(?=b)[bc]` and `ab[xy](?=(?<=x)y)[xy]`, where it can fail (§5.1) |
| W-E1 (§4.5; L1) | a negative body read as an item | `x(?!ab)a[bc]` on `xac`: (0,3) | `xa[bc]` | `xab`: absent, NOMATCH | VM `unanchored`; k-set `120,97,[2]` |
| W-T1 (guard bound, `lg` kept end; L1 on R1) `[r2 S5]` `[REV 3.1, review r51 READYL1-8 (c): the window reason below is stale (§14.1 item 4); the flag still gives the whole-run test, so the row stands under it]` | a growing `lg` keeps its FIRST 32 positions | `[ac]{17}[bc]{17}(?<=(?<=ca{16})b{17}).` on `c a^16 b^17 d`: (0,35) | the inner and outer `lg` merge to `c a^16 b^17` (34), kept `a^15 b^17` at `[-32, 0)`, met with the consumed `[ac]{17}[bc]{17}` | keep-first stores `c a^16 b^15` at `[-32, 0)`: shifted two places, it narrows the consumed run to a string absent from the subject (and lists the live pattern dead): NOMATCH (SIM-1, reproduced by the verifier). `[r3 READY-1]` At DEFAULT flags the answer does not move: the correct run (`a^15 b^17 @2`) and the sabotage (`c a^14 [bc][bc] b^15 @2`) both stamp `RX_REQ_RUN "6262626262626262@7"` (the 8-position window, `b`s only) and answer `match 0 35`. So W-T1's answer check runs under `--memfn=no-fd-pres-pick` (the whole-run test `_reqrun_whole`: the sabotage answers NOMATCH, the correct run matches as the oracle), and W-T1 is a listing row on `req_whole_run` (compared two-sided). The sabotage's empty meet lists the live pattern dead, so the pattern is W-D7 (listed NOT dead). The unmasked `c a^16 b^15` is a substring of the subject and matches even under the flag; only the EMPTY-MEET-masked value fails | VM `unanchored`, run none today |
| W-T2 (TOP `++`; L2 on R1, a LISTING row) `[r2 S5]` `[r4 READY2-1, READY2-7]` `[REV 3.1, review r51 READYL2-1: an answer witness under `--memfn=no-fd-pres-pick` only, §14.1 item 6]` | TOP's `tail ++ rg` keeps the LAST positions (`rn_pre`) | `a{20}(?=b{20})` on `a^20 b^20`: (0,20); from 1: NOMATCH | `a^20 b^12` at 0 | `a^12 b^20` stated at 0 (the last 32 of 40; rev 2's `a^8 b^20` was an arithmetic slip). It CANNOT fail on the answer, at default flags or under `--memfn=no-fd-pres-pick`: both runs give the window `b^8` at `at` 24, K 24 (the spellings `a^20 b^12` and `a^12 b^20` both list `req_run 6262626262626262@7`, `req_run_maxoff 24`, measured), and the whole sabotaged run is a substring of the subject. So it is a listing row on `req_whole_run` (compared two-sided), run at R1's landing if L2 lands first; the answer witness is W-T2a | VM `unanchored`, `"dominated"` today; k-set `a` × 20; run none today (R1 gives `a{20}` its run) |
| W-T2a (TOP `++`; L2, no R1) `[r4 READY2-1]` `[REV 3.1, review r51 READYL2-6 (3): the reason below is the retired window's. At L2 K is the whole run's offset, 0 in both builds; what differs is the HIT: the kit's 8-position verify around `z` (at B `memchr(... + 25, 122 ...)`, `memcmp(subject + cand + 20, "bbbbbzbb", 8)`) matches only at c = 8 under the plant, so the body starts at 8 and the answer is NOMATCH from 0, as stated; today's stamps at B are `RX_REQ_HANDOFF "0"`, `RX_REQ_RUN "...@19"`, not "12"]` | the same plant (`rn_pre`) | `a^20(?=b^5 z b^14)` (spelled literally) on `a^20 b^5 z b^14`: (0,20); from 1, 8, 12: NOMATCH | `a^20 b^5 z b^6` at 0, `cons` `[0,20)`, the member an `a` | `a^12 b^5 z b^14` stated at 0, truly at 8; its consumed positions hold `z` (index 17), the least-mass byte, so the window holds the one `z` and its K is 8 too small: the body starts at 8 and nothing matches (NOMATCH from 0). Hand-derived over the stated move; the build re-measures | VM `unanchored`, `RX_REQ_WHY "emitted"`, `RX_REQ_HANDOFF "12"` today (run `a^20`); k-set `a` × 20 |
| W-T3 (TOP `++` at BACK; L3 on R1, a LISTING row) `[r2 S5]` `[r4 READY3-1]` `[REV 3.1, review r51 READYL2-1: an answer witness under `--memfn=no-fd-pres-pick` only, §14.1 item 6]` | the same plant at `lg ++ head` | `(?<=a{20})b{20}` on `a^20 b^20` from 0 and from 20: (20,40); from 21: NOMATCH | `a^20 b^12` at −20 | `a^12 b^20` stated at −20 (truly −12). It CANNOT fail: placed at −20 both windows are `b^8` at attempt offset +4, so the pre-check and K are byte-identical, and the whole sabotaged run is present under the flag (READY3-1, the spellings measured). A listing row on `req_whole_run`; the answer witness is W-T3a | VM `unanchored`, `"dominated"` today; k-set `b` × 20 |
| W-T3a (TOP `++` at BACK; L3, no R1) `[r4 READY3-1]` `[REV 3.1, review r51 READYL2-6 (3): the reason below is the retired window's. At L3 K is −20 in both builds; the kit's 8-position verify (`+ 28`, `cand + 21, "bbbbbbbz"` at B) matches only at c = 8 under the plant, so the body starts at 28 and the answer is NOMATCH from 0, as stated]` | the same plant (`rn_pre`) at `lg ++ head` | `(?<=a^20)b^8 z b^11` (spelled literally) on `a^20 b^8 z b^11`: (20,40) from 0, 12, 20; NOMATCH from 21, 28 | `a^20 b^8 z b^3` at −20, `cons` `[20,32)`, the member `z` (index 28), window `b^7 z` at `at` 21, K = 1 (the spelling's window, measured) | `a^12 b^8 z b^11` stated at −20, truly −12: `z` is at index 20, inside `cons`, so the window `b^7 z` sits at `at` 13 and K reads −7 where it is 1: from 0 the body starts at `21 + 7` = 28, NOMATCH (hand-derived; `t` 20 = `lb_bytes` 20). A rarer byte than `b` is needed: with `y` the prior picks a uniform `b^8` window and the plant cannot fail (measured) | VM `unanchored`, `"dominated"` (`run-pinned`), `RX_REQ_HANDOFF "none"` today: the gate's WHY precondition applies |
| W-S4 (FACT, CAT-SET; L1) `[r2 S4]` | the narrowed byte not put in the set | `x(?=qr)[pq]r` | run `xqr`, `req_set` takes `q` (113; the spelled `xqr` lists `req_set 113,114,120`) | `req_byte 113` with `req_set {114,120}`: `reqcube_check.py` check 4 red; no answer moves. `[r3 READY-3]` Check 4 iterates a fixed `WIT` list (`reqcube_check.py:226-239`, 12 patterns) that lacks `x(?=qr)[pq]r`, so "check 4 green" holds the witness only once L1's BUILD adds the pattern to `WIT` (and L2's, `bar(?=baz)`, for W-S4b); with it added, check 4 is red under the sabotage (`REQ_BYTE 113 not in [114,120]`) and green on the correct set | — |
| W-S4b (FACT, A13; L2) `[r2 S4]` `[r4 READY2-3]` `[REV 3.1, review r51 READYL2-6 (2): "the kit's member over `cons` first (§8.2), else the compile fails" is stale: §8.2 is withdrawn and the member is pcrec's own pick over the consumed extent (D-6); the plant and check 4 hold as stated (check 4 does not test `@idx` against `req_set`)]` | the scan member picked at a guard position | `bar(?=baz)`, ADDED to `reqcube_check.py`'s `WIT` list by L2's build (READY-3's form; the list holds no lookaround pattern today, grep) | run `barbaz`, the kit's member among `bar` | `req_byte 122` (`z`, the spelled `barbaz`'s pick, measured), outside `req_set` {97,98,114}: check 4's first clause red. The correct build needs the kit's member over `cons` first (§8.2), else the compile fails before check 4 runs | — |
| W-S4c (FACT, A13 at BACK; L3) `[r4 READY3-6]` | the scan member picked at a guard position | `(?<=qz)ab`, ADDED to `WIT` by L3's build | run `qzab` at −2, the member `a` or `b` | `req_byte 122` (the spelled `qzab`'s pick, measured), outside `req_set` {97,98}: check 4 red | — |
| W-D1..W-D7 (FACT, DEAD; L1) `[r2 S6]` `[r3 READY-1, READY-10]` | W-D1: the consumed-position EMPTY-MEET branch does not set DEAD. W-D2: the guard-vs-guard branch drops positions without setting DEAD (SIM-2's corner). And the walk-level-flag sabotage: DEAD as one flag, any empty meet kills the root | W-D1 `foo(?=bar)baz` (N, N) and W-D2 `(?<=ab)(?<=cb)c` (N on `abc`, `cbc`; 2,005 subjects N, verifier) list dead; W-D3 `x(?:foo(?=bar)baz)?y`, W-D4 `(?:foo(?=bar)baz\|q)`, W-D6 `(?:foo(?=bar)baz){0}x` match (M on `xy`, `q`, `x`) and list NOT dead; W-D5 `x(?!foo(?=bar)baz)y` (M on `xy`) lists NOT dead and is a structural note (§5.2 (g)); W-D7 is W-T1's pattern, listed NOT dead | as the oracle | W-D1, W-D2: each plant lists the pattern NOT dead, the listing check is red. W-D3, W-D4, W-D6 under the flag sabotage: listed dead, the listing check is red `[REV 3.3, review r55 CHECK-5: W-D7
dropped from this claim, §14.8 item 8]` (and at U-dead they would answer NOMATCH) | — |

Rev 1's one-character witness spellings (`a(?=b)[bc]`, `(?:ab(?=a)){2}`, `xy[ac](?:(?<=a)b|c)`,
`[ac][ac]c(?<=ac)(?<=c)d`, `ab[xy](?=(?<=x)y)[xy]`, `[ac](?<=a(?=c))c`) stay as oracle facts and
§5.6 rows. With S2's choice their plants have a site again, but `a(?=b)[bc]` and
`(?:ab(?=a)){2}` are `cover`-dominated (`RX_DFA_SCAN "cover"`, measured), so they cannot fail,
and the rest are covered by W-C1 for the `A_CTX` row and by the multi-character re-spellings for
every T4 row. Soundlook's raw shapes, `(?:(?<=a)b|c)`, `(?<=ab)(?<=b)c`, `x(?=(?<=x)y)y` and
`(?<=a(?=b))b`, stay as oracle facts (rev 1's `oracle.out`).

### 5.8 Lever `[r1 F18, F19]` `[r2 S9]`

The `look` arm of §3.7's walk-parameter table restores E-5 as E2's plain unit (no item, no
guards; both lowerings) and forces reach `[0, maxoff]` `[REV 3: by passing over E-5i and TOP's rows, §14.3 D-1, D-4]`, so L2 and L3 have no separate lever
`[r3 READY-9]`. `zero` restores E-4's cut only `[REV 3.1, review r51 READYL1-1: no longer: E-5i carries `look | zero`, so `zero` keeps E2's shipped meaning, every lookaround back to the old CUT (§14.3 D-1)]`: E-5's plain unit is E2's, which `look` keeps, so
the answer-identity sweep under `look` isolates L1's own delta and `zero` isolates E2's. Public bits: L3's earlier scan start is a cost INSIDE
the pre-check row, and its only public deny is the coarse `-fno-req-run` (bit 31), which removes
the run check rather than restoring today's start. L3 therefore RE-SPECIFIES bit 31's text
(tuning.md §2.28¶1: the deny also removes a scan that begins before the start offset), as
alt_normal_form §11 re-specifies bit 44, and adds no bit.

## 6. Decisions as declared tables (each first-match; the build spells them as rows)

**T1, the arm table** (one row per node class, §2): CLASS, EMPTY and zero-width (the unit),
positive LOOKAROUND (the unit + item: `A_LOOK` positive, `A_CTX` NEXT/PREV), CAT, ALT, REP
(power), BREF/VAR/consume callout/CALL (wall). The `switch` in `rb_walk_at` stays exhaustive with
no default (`req.c:116-121`); the `A_CTX` case dispatches on the node's function through
`ctxfn.def`'s rows, never on a spelling.

**T2, the REP rows** (first match) `[r1 F4, F6, F7]`:

| # | condition | consumed value | guards | `all` |
|---|---|---|---|---|
| 1 | body width 0 (`maxw == 0`, any m, n) | `m = 0`: the unit; `m >= 1`: the body's value (width-0 copies coincide) | `m = 0`: NONE; `m >= 1`: the body's | true |
| 2 | m = n (including m = n = 0, where `X^0` is the unit) | `X^c`, c = min(m, sat), `maxw` := `rr_rep_w` (exact), `tail.off` from it | `X^c`'s | iff c = m and `X^c.all` |
| 3 | otherwise (m < n or unbounded; m = 0 included, where `X^0 · gap` is today's gap) | head, best, `lg` from `X^c · gap`; tail, `rg` from `gap · X^c`; `maxw` exact | as the cells say | false |

Rev 0's row 2 ("m = 0: today's gap") is deleted: it is row 3 at c = 0 (simulate SIM-1, soundrep
SOUNDREP-3), and it shadowed `X{0}` (`xy(?:ab){0}zw` stayed a gap where `xyzw` gives 4). T2's DEAD
cell is T4's REP row.

**T3, the zero-width rows**: §4.1's E-1..E-5, first match on the kind row's TEXT `ZERO` and the
node kind (`A_EMPTY` first; `A_LOOK` positive before negative; `A_CTX` by function, NEXT/PREV to
E-5, every other function to E-4). Under E2, E-5 is the unit (§4.1, S16).

**T4, the guard rows** `[REV 3: fixed steps of `rr_cat` plus ALT's post-step, TOP a combining row table, the never rows shared, §14.3 D-3, D-4, D-9]`: §5.2's ITEM, CAT-R, CAT-L, CAT-SET, CAT-EDGE, ALT, REP, EMPTY-MEET and TOP,
first match within each combinator, with the DEAD column. TOP's reach and `lb_bytes` are walk
parameters (§3.7).

**T5, the reader admission rows**: §5.4.

**T6, the units and their triggers**: §8 `[REV 3: for L1-L3, §14.4]`.

**T7, the walk parameters**: §3.7.

## 7. Forward context only: where the lookaround arm meets [POSTFACT]'s 2026-11-08 entries

Noted, not designed (`docs/design/plan_row_bodies/POSTFACT.md`):

- **Span intersection** (lookaheads CONTAINED in the span become a plain automaton): CAT-R's
  meet is the FACT shadow of the contained case.
- **Lookbehind removal by `\K` with an earlier scan and a floor**: the same step-back as TOP's
  BACK candidate (scan from `max(0, s − maxlen(A))`, accept at or after `s`). If it lands, a
  fixed lookbehind becomes consumed text plus a start mark, and `omin` becomes the mark's offset.
- **The end-of-match mark**: AHEAD's extension is that mark's distance to the consumed end.
- **The group-0 group** (`A(?<0>B)C`): both marks at once; the run's `[omin, maxoff]` relative to
  the attempt, and the reported span, are the vocabulary it needs.
- **"Is read-before-start already a span fact?"**: the SHAPE is (D172 spans down to −8); the
  statement is not (§0).

## 8. Staging (separable units; each names the measurement that triggers it, D77) `[r1 F17, F20, F21]` `[r2 S4, S7, S9, S11, S13, S14, S16]` `[REV 3: E1, R1 and E2 are BUILT (§14.0); the L1, L2 and L3 rows below are superseded by §14.4, in the order L1, L3, L2; "after the kit delivers §8.2" is MET]`

Every unit is a FACT change (G4): an input to the existing choice rows, judged at the pick rows
it moves, with D186's choice bar applied there. It is not a third kind of change. The kind column
says which regimes' pick rows a unit can move. **The walk-parameter table (§3.7) is built by the
first unit built of 2a, E1, R1, E2 and L1** `[r2 S13]`; that unit's gate names the
`facts_listing.md` §4.1.3 `harness:` token hunk, and each later unit adds its arm rows.

| unit | content | depends on | remodel overlap (D153) | kind (byte / utf8) | trigger (D77) | gates |
|---|---|---|---|---|---|---|
| E1 | T2 row 1 and T3 E-2/E-3; rides with stage 2a (E-1) if 2a's census fires, else alone | none (the span_pick 1e gate in the plan rows is discharged: [MEASURE-SET] "stage 1 COMPLETE at the 1e merge") | alt_normal_form stage 2a: the same `req.c` cut list and the same walk-parameter table | fact change / fact change | stage 2a's census extended to REP-of-width-0 producers, a bench cell among the movers | the census list = observed movers (two-sided); B0 identity diff with only those movers; PC-3; `make test`, `make test-axes` with the `empty` arm; S-g, W-R4 |
| R1 | T2 rows 2-3 (the power arm, runs and pieces) | none | none (`req.c` REP arm only; [REWRITE-ADJ] reads T2 later, U-rewrite) | fact change / fact change | [REPEAT-RUN]'s census: corpus + bench compiles whose run grows under an independent model of T2, a bench cell among them | as E1 with the `rep` arm; W-R1..W-R6; the pieces listing moves only for exact repeats |
| E2 | T3 E-4, and E-5 as the plain unit (§4.1, S16) | none | stage 2a (as E1) | fact change / fact change | compiles whose run is cut by a zero-width node, per producer kind (both lookaround lowerings counted apart), a bench cell among them; R-span movers counted (F11) | as E1 with the `zero` arm; S-L (E-5's plant: the body walked as consumed) and W-E3 red-able |
| L1 | T4 ITEM (both lowerings), CAT-R/L/SET/EDGE, ALT, REP, EMPTY-MEET with the DEAD column, TOP at reach `[0, maxoff]`; the producer's item combinator (§5.3) and the D168 addendum (§12) in the same change | E2; E1 for W-F4 (T2 row 1); R1 for T4's REP row, W-RG and W-T1 (without R1 the REP arm is today's best-only and carries no guard, so those three move to R1's landing) | [DD-11.5] part 1: the item combinator is its producer's item half; its `look-fixed` row reads it when built (§5.3) | fact change / fact change | compiles with a positive lookaround (either lowering) whose run grows at reach 0 | as E1 with the `look` arm; S-L, W-L2, W-L4, W-L5, W-L6, W-L7, W-L8, W-F4, W-F5, W-A1, W-S1, W-N1, W-N2, W-RG, W-C1, W-E1, W-T1 `[r3 READY-8]` (W-T1's answer check under `--memfn=no-fd-pres-pick`, plus its `req_whole_run` listing row `[r3 READY-1]`); FACT W-S4 with `x(?=qr)[pq]r` ADDED to `reqcube_check.py`'s `WIT` list in the same change (and `bar(?=baz)` for L2's W-S4b), check 4 then green on the correct set and red under the plant `[r3 READY-3]`; W-D1..W-D7 (W-D5 is a structural note, a plant each for W-D1 and W-D2, §5.7); the run listed equal with and without `-fno-ctx-node` on the rows where it CAN fail, `a(?=b)[bc]` and `ab[xy](?=(?<=x)y)[xy]` (W-C1's is vacuous, §5.1) `[r3 READY-4]`; the `look` arm restores E-5 as E2's plain unit, so the sweep isolates L1 `[r3 READY-9]`; `facts_listing.md` §4.1.3 hunk: `dead` and `harness:<arm>` as why values, one per run, first match `dead` > `harness:` > the existing reasons (§3.7), with the reader census of A12 (`fd_why`, `pf_done_why`, `run_facts_checks.sh`, the harness-binary note) `[r3 READY-5, READY-7]`; tuning §2.27¶4 and match_api §6.3.7¶5 checked unchanged (CAT-SET keeps them true) |
| L2 `[r4 READY2-1..7]` | TOP's AHEAD candidate; the consumed extent `cons`, written by TOP and stated to the kit on the run window and the presence run span; pcrec READS the kit's member over `cons` at every reader, the window cut included (A13, §8.2: one decision, the kit's); `pcrec_run_pin` reads `cons` (A5) | L1; the kit's delivery of §8.2 part A (its `MF_SITE_ABI` event); R1 only for W-T2's listing row, which runs at R1's landing if L2 lands first (L1's form) | none | fact change (byte) | `[r4 READY2-4]` a bench cell whose pre-check's false-candidate rate falls when the lookahead's bytes join the COMPARE. The consumed member stays the scan byte (A13), so a rare lookahead byte is never the `memchr` byte, and an extension byte enters the emitted test only within 7 positions of the consumed member (the 8-position window is cut around it, `findings.c:780`); K is unchanged. The whole extended run is compared only on R-30's route (VM, `RX_VM_PREFILTER "none"`) or under `--memfn=no-fd-pres-pick` | §5.4 re-grepped at the build's base: every AHEAD cell's fix in, the kit's delivery read at `req_run_member`'s readers; spec hunks BY PARAGRAPH `[r4 READY2-5]`: match_api §6.3.7¶6 ("every successful ATTEMPT holds the run, which may extend past the attempt's consumed end", attempt-relative per §2, F14), tuning §2.28¶1 (the same sentence for "every match must contain"; L3 adds bit 31's sentence to the same paragraph, so L2 owns the run's definition and L3 the deny's reach), `docs/spec/findings.md` §4's member row (the member is the kit's over the consumed extent; "the window's truncation keeps pcrec's own index" goes); CHECKED-UNCHANGED: match_api §6.3.7¶4, ¶5, ¶7, ¶11, tuning §2.27¶4, findings.md §4's window row; `facts_listing.md` §4.1.2 if the listing shows the extension; the census's movers include `RX_REQ_RUN`, `RX_REQ_WHY` and `RX_DFA_PREFILTER` (A5); witnesses W-L9, W-T2a (answers), W-T2 (listing, `req_whole_run`), W-S4b with `bar(?=baz)` ADDED to `reqcube_check.py`'s `WIT`; each witness's WHY/HANDOFF precondition (§5.7 condition 6) |
| L3 `[r4 READY3-1..9]` | TOP's BACK candidate (`omin < 0`, `t <= lb_bytes`); A3's move at a signed K of either sign and the margin's `max(K, 0)`; A8's two VM attempt-loop rows admitted at signed K; `req_run_omin` (the whole run's); and, if L3 lands before L2, `cons` and the kit-member read (A13, A5), which L2 then reads: one mechanism, built by whichever lands first | L1; L2's `cons` or its own build of it (above) `[r4 READY3-6]`; the kit's delivery of §8.2 parts A and B (one request, filed with L2's) | `[r4 READY3-7, RULED: BUILD NOW]` A-POSDOM (`docs/design/stream/roadmap.md`; [DEC-POSDOM] `STATE:not-started`, prerequisite A-SEAM unscheduled): L3 builds now and states its sites in the shape A-POSDOM's declared table will take (§8.1), adding no `PCREC_START0_*` mode and no call site, so R08 does not grow and the remodel step inherits the rows byte-identically; the stream ruling (areas migrate riding along with the optimizations that touch them) applies. A-REV (ownership ruling 1: `vlookbehind.md` holds the lookbehind admission rows; arev S3 the lookbehind hand-off): L3's item reads the body's description, the hoist the branches' (§5.2), and neither moves the other's rows | fact change | the plan row's census (corpus + bench compiles whose rarest bytes sit inside a positive lookbehind) | §5.4's A1-A3, A5, A8, A9, A12, A13 changed in the same unit (A10 re-grepped: no change, READY3-5), A3's sentinel split before any negative K; `emit_req_handoff_rest` and `emit_req_landmark_move` moved to `max(posvar, c − K)` with no `size_t` wrap at EITHER sign of K `[r2 S1]` `[r4 READY3-3]`; the margin reads `max(K, 0)` `[r4 READY3-2]`; K carries a stated/none bit, the −1 sentinel retired at every §9 site (`omin`/`maxoff` already have a none state; `head_max`'s is the kit's `handoff` field) `[r4 READY3-8]`; spec hunks BY PARAGRAPH `[r2 S11]` `[r4 READY3-4]`: match_api §6.3.7¶10 (a negative `<PREFIX>_REQ_HANDOFF`), §6.3.7¶11 (the search block returns the least occurrence at or after `max(0, startpos + omin)`; `max(startpos, that − K)` kept, said to hold for signed K; its attempt-loop clause "a whole run with a finite `K`" kept, K now of either sign), tuning §2.41¶1 (the same two sentences), tuning §2.41¶8b (the attempt-loop rows: `K` the whole run's offset of either sign; the entry's `c` the least occurrence at or after `max(0, startpos + omin)`, the re-entry's at or after `max(0, attempt position + omin)`), tuning §2.28¶1 (bit 31: the deny also removes a scan that begins before the start offset), `facts_listing.md` §4.1.2¶8 and ¶8b (negative values) and a new paragraph for `req_run_omin`; the L2 hunks' BACK half; witnesses S-L, W-L1 (the kit's), W-L3, W-L8, W-L10, W-L11, W-L12, W-L13, W-L14 (W-L14's sabotage is a hang the gate's timeout reports), W-T3a (answers), W-T3 (listing, `req_whole_run`, at R1), W-S4c with `(?<=qz)ab` ADDED to `WIT`; each with §5.7's WHY/HANDOFF precondition `[r4 READY3-9]` |
| R2 | the REP adjacency head (`altnf.c:223-230`'s wall becomes `X^m`'s head, `closed` iff m = n) | R1 | [REWRITE-ADJ] (both read T2) | fact change (tree movers) | a census of owner refusals whose intervening branch's head is a REP: `(?:ab\|ax{2}\|ad)` has `RX_ALTCLS_MERGES` 0 against 1 for `(?:ab\|axx\|ad)` (measured, rev 0's `owner_rep.out`); `[REV 3.1, review r51 CONFORM-9]` plus the positive LOOKAHEAD bodies whose head walls at a repeat (`(?=(?:ab){2}c)`: no AHEAD item at L1/L2), since the head's per-kind rule is one rule for both readers (§14.3 D-10) | the parent's S-d/S-k shapes re-run with a REP branch; R2's own witness is designed at its design pass, where it names the reader of EXACT if it needs one (F16) |

Order: E1 → (R1, E2 independent) → L1 (after R1 for its REP row) → L2 and L3 in either order `[REV 3.2, conf-spanarms8 D3: the BACK row's `++ rg` clause lands with whichever of L2 and the BACK row (L3's) comes second: with L3 first it is L2's addition, with L2 first it is part of the BACK row L3 then builds, §14.4 L2]`, both
after the kit delivers §8.2 (`[r4 READY2-7, READY3-6]`: the first of them to land builds `cons` and
the kit-member read, the other reads them); R2 after R1 when its census fires. As ruled, L3 goes to
Frank with rev 2.2's text; L2 goes after the kit's answer plus one readiness critic on its changed
text. No unit is an abi event by itself unless its movers include emitted scaffolding;
each unit's identity gate says which streams move.

### 8.1 L3's position-domain sites, in A-POSDOM's table shape `[r4 READY3-7, RULED: BUILD NOW]`

A-POSDOM's next step is "a declared table of today's call sites (site, mode, the hand it guards)"
(`docs/design/stream/roadmap.md`, A-POSDOM). L3 touches these position-domain sites, stated in that
shape so the remodel step takes the rows as they are. L3 adds no mode and no call site; what it
changes is the move arithmetic BEFORE each site's rounding, never the rounding call.

| site (call of `pcrec_emit_start_zero`, at `1ffcce0c1`) | mode | the hand it guards | what L3 changes |
|---|---|---|---|
| `emit_req_handoff_rest` (`emit_dfa.c:1175`) | `PCREC_START0_ROUNDUP` | `handoff_position` after the ENTRY move: the DFA scan's first start, the VM hybrid prefilter's first start, the VM attempt loop's first attempt (A8's `handoff-attempts-entry`/`handoff-attempts`) | the move before the rounding: `max(posvar, c − K)`, K signed, no `size_t` wrap (A3) |
| `emit_req_landmark_move` (`emit_dfa.c:7799`) | `PCREC_START0_ROUNDUP` | `pos` after a RE-ENTRY move: the forward scan's `handoff-reentry` (`pf_emit_handoff`), the VM attempt loop's re-entry (`pcrec_emit_req_attempt_reentry`) | the same move, and the re-ask's hit compared signed (W-L14) |

Not pcrec call sites, named so the table's census is complete: the pre-check's scan floor
`max(0, search_from + omin)` and its re-entry twin are the KIT's text (A2, §8.2 part B); when
A-POSDOM's FIND frame "carries the floor", this floor is one of its values, a kit statement.
`\G`'s `search_from` (`emit_vm.c:13579-13582`) does not move.

### 8.2 The kit request, stated as facts (D157), for main to file once rev 2.2 is ruled `[r4 READY2-2, READY3-2, READY3-3, READY3-8]` `[REV 3: DELIVERED in §12a's form by R-38 K38-2, Part D and R-41 (MF_SITE_ABI 29) and WITHDRAWN; kept as the record, §14.1 item 2]`

ONE request, two parts; part A gates L2 and L3, part B gates L3. The kit picks its method and the
number of `MF_SITE_ABI` events; pcrec names none. Text:

> **R-n (pcrec manager) — span_arms L2/L3: the necessary run reaches outside the match.**
> Design: `docs/design/span_arms.md` rev 2.2 (§5.2 TOP, §5.4 A1-A3/A13, §8). No build go yet:
> L2's and L3's go waits for this delivery.
>
> **Part A (L2 and L3): the run's CONSUMED extent.**
> - FACT. pcrec's necessary run may now extend past the bytes a match consumes: after the consumed
>   end (a positive lookahead's bytes, L2) or before the start (a positive lookbehind's, L3). Every
>   successful attempt holds EVERY stated position of the run; only the positions in
>   `[cons_lo, cons_hi)` (the span's own positions) are inside the match. pcrec states
>   `[cons_lo, cons_hi)` on the run WINDOW statement (the span `req_run_member` states,
>   `emit_dfa.c:1058`) and on the PRESENCE run span (`req_pres_spans`, `emit_dfa.c:1475`). A run
>   with no extension states its whole span, today's value, so nothing moves until L2/L3 build.
> - WHY IT MATTERS (pcrec's use of the reply, not a method). pcrec reports the member's byte as
>   `<PREFIX>_REQ_BYTE`, contracted as "a byte every match must contain"
>   (`docs/spec/match_api.md` §6.3.7¶4, ¶5), and its index as `<PREFIX>_REQ_RUN`'s `@idx`, "the
>   member the emitted `memchr` scans" (¶7). A member outside the consumed extent falsifies the
>   first, so pcrec needs the reply's member inside `[cons_lo, cons_hi)` wherever that extent is
>   non-empty. How the kit ranks positions there, and whether the extent changes its compare, its
>   stretch or its presence layout, is the kit's.
> - OWNERSHIP: ONE decision, the kit's. The member is already the kit's reply (D172;
>   `docs/spec/findings.md` §4's member row), but pcrec still computes its own index to cut the
>   window before any statement exists, and `req_run_member` fails loudly when the two differ;
>   the kit's presence side holds a third pick (`pres_layout_check`, `compose.c:688`). After this
>   request pcrec stops picking: it states the WHOLE run (with its consumed extent) once, reads the
>   kit's member, and cuts its 8-position window around that member (the window's length is
>   pcrec's statement limit, `PCREC_MAX_REQ_RUN_EMIT`); every reader (`req_run_tests`,
>   `req_note_run`, `req_set_leads_own`, `req_pick_shadow`, both stamps) reads that one reply.
>   pcrec needs the reply at fact-derivation time, before a site exists (the window is a pattern
>   fact listed by `--emit-facts`); whether that is `mf_wdecide` over a site-free statement or
>   another entry is the kit's.
>
> **Part B (L3): a negative presence `omin` and a signed `head_max`.**
> - FACT. On a BACK run the presence span's smallest occurrence offset is NEGATIVE: an occurrence
>   may begin up to `−omin` bytes BEFORE the attempt start (`memfn.h:679-684` refuses this today).
>   The origin of `omin` and of `head_max` is the ATTEMPT start (the position the pre-check is
>   asked from: `search_from` at entry, the scan or attempt position at re-entry). pcrec relies
>   on the reply's occurrence being the least at or after `max(0, origin + omin)` at entry and at
>   re-entry (span_arms §5.3; the subject's offset 0 is the clamp).
> - FACT. `head_max` (K) may be NEGATIVE or ZERO with `omin < 0`: the landmark's occurrence then
>   begins up to `−K` bytes BEFORE the match start. Which `omin`: the WHOLE run's (the presence
>   span's); the window's offset is `omin + at`, which is K. A negative K's admission meaning:
>   a landmark at or before the match start costs no step back, so pcrec's own margin reads
>   `max(K, 0)`, and the kit's twin admission (`presence.c:199-222`, which reads `head_max`
>   unsigned) is compared with it by `req_pick_shadow`'s `landmark` record.
> - `head_max`'s none state stays the kit's own (`handoff != MF_H_ASSIGN`, "0 elsewhere",
>   `memfn.h:820-832`); pcrec adds a stated/none bit for K on its side only.
> - BOUND. If the kit bounds the negative `omin` (as `MF_MAX_BACK` bounds window spans,
>   `memfn.h:235`), pcrec's TOP row reads the smaller of that bound and `lb_bytes` (span_arms
>   §5.5); say which.
>
> Deliver: a kit branch for merge review; the `MF_SITE_ABI` event(s) the kit's; name what pcrec
> must read from the reply (fields, entry) so L2/L3's lane builds against it.

## 9. The ledger (G2) `[REV 3: the L rows are restated per unit in §14.4's "Deletes"; the `cons`, member-pick, `omin` and sentinel rows are stale, §14.1 items 3, 5, 11]`

| change | where (`dd2fe2de9` = `c054e38e7`) | kind |
|---|---|---|
| "a repeat's head and tail do not survive" | `req.c:64-69`, `:709-719`, `rb_rep_into` `:549-558` | REPLACED by T2 (R1) |
| "min-0 is a gap" for a width-0 body | `req.c:723-739` | REPLACED by T2 row 1 (E1) |
| rev 0's T2 row 2 (m = 0) `[r1 F7]` | this note | DELETED (row 3 at c = 0) |
| `pcrec_pd_none()` for REP | `req.c:557` | REPLACED by the power combinator (R1) |
| the ZERO-text cut | `req.c:627-645`, `:756-771` | SPLIT by T3: unit (E1/2a/E2, E-5 included), unit + item (L1) |
| `A_LOOK`'s "joining across" comment | `req.c:744-755` | REWRITTEN (E2: joining across is sound; reading the body is L1's item) |
| rev 0's EXACT/GUARDED split `[r1 F16]` | this note | DELETED (no reader) |
| the ctx-node / no-ctx-node run difference `[r2 S2]` | `A_CTX` in the ZERO cut, `A_LOOK` read by ITEM | DELETED (L1: one ITEM row for both lowerings) |
| the REP adjacency wall | `altnf.c:223-230` | REPLACED (R2) |
| the power combinator | `desc.c` (new) | ADDED (R1) |
| the item combinator: a body's description placed at a cursor, united per offset `[r2 S8]` | `desc.c` (new); called by `req.c`'s walk | ADDED (L1), with the D168 addendum (§12) |
| the pending guards `lg`/`rg` | `RbRuns` (`req.c:154`) | ADDED (L1) |
| CAT-SET: a narrowed consumed byte enters the set `[r2 S4]` | `rr_cat` | ADDED (L1) |
| the DEAD bit and the `dead` why token `[r2 S6]` `[r3 READY-7]` | `RbRuns`; `req_whole_run`'s `why` (`facts_listing.md` §4.1.3); `fd_why` (`src/dump/facts_dump.c:93-121`), `pf_done_why` (`facts.c:169-182`, status `derived`) | ADDED (L1) |
| the walk-parameter table (`pos_set`, `max_pieces`, reach, restored arms, `lb_bytes`) and the `harness:` token `[r2 S9]` | `facts.c:208-211` (the one walk entry); `pcrec_req_walk`'s signature (`req.c:789`, its prototype `src/facts/facts_derive.h:132`, and the `req.c:233` comment that names it) takes one record `[r3 READY-7]` | ADDED once (the first unit built of 2a/E1/R1/E2/L1), rows per unit; replaces rev 1's "harness source in `facts.def`'s deny" |
| the consumed extent `cons` `[r2 S4]` `[r4 READY2-2, READY2-6]` | `RbRun`, `ReqRun` (written by TOP); stated to the kit on the run window (`req_run_member`'s span) and the presence run span (`req_pres_spans`), the kit's statement field (§8.2 part A); readers `pcrec_req_pick`, `pcrec_run_pin` (`kset.c:294-318`, pick and stretch inside `cons`) | ADDED (L2, or L3 if it lands first) |
| pcrec's own member pick `[r4 READY2-2]` | `pcrec_req_window`'s `pcrec_find_run_scan_index` call (`req.c:841`) and `req_run_member`'s equality check (`emit_dfa.c:1058-1076`) | REPLACED by the kit's one member (§8.2): the window is cut around the reply's member, and every reader reads the reply (L2, or L3 if first) |
| the VM attempt-loop rows' BACK decline `[r4 READY3-4]` | `req_handoff_entry_applies`'s `r->whole_maxoff < 0` (`emit_dfa.c:8921`) | DELETED (L3): the rows run A3's signed move |
| the margin's unsigned K `[r4 READY3-2]` | `pcrec_landmark_margin` (`emit_dfa.c:9057-9063`) | REPLACED by `max(K, 0)` at its BACK caller (L3) |
| `omin` `[r2 S12]` `[r4 READY3-3]` | `RbRun.omin`, `ReqRun.omin`; one `facts.def` row `req_run_omin` (`PF_DERIVED`, owner `req.c`, depends `req_run`, beside `req_run_maxoff`: one row per offset fact), the WHOLE run's `omin` (the window's is `omin + at` = K); a listing value | ADDED (L3) |
| the −1 "none" sentinel on the landmark K `[r4 READY3-8]` | `facts.c:104` (deny/reset), `:332-333` (derivation), `:581` (`pcrec_fact_req_run_maxoff`, no outside caller), `:840` (printer `< 0` → `none`); `facts.h:566-576`; readers `emit_dfa.c:8835` (`k < 0`) and `pcrec_landmark_margin`'s cast (`:9059`) | REPLACED by a stated/none bit beside K (L3); `omin`/`maxoff` keep their `len < 2` none state; `head_max`'s none state is the kit's `handoff` field |
| the handoff move at `k <= 0`, and the unsigned distance at `k > 0` `[r2 S1]` `[r4 READY3-3]` | `emit_req_handoff_rest` `emit_dfa.c:1167-1204`, `emit_req_landmark_move` `:7793-7813` | REPLACED by `max(posvar, c − K)`, signed, no wrap at either sign (L3; sites in §8.1's shape) |

## 10. Unlocks (each with its trigger)

| id | unlock | trigger | plan row |
|---|---|---|---|
| U-dead `[REV 3: the never family's step, [NEVER-MATCH]'s, §14.3 D-9]` | a pattern whose root value is DEAD cannot match (`foo(?=bar)baz`, `(?<=ab)(?<=cb)c`). The compile could emit the constant NOMATCH artifact. `[r2 S6]` It reads the ROOT's bit only; the DEAD column states only what meets prove, so `a(?!)b` or an empty class is a further row of U-dead's own census, not this note's | a corpus or user pattern that is dead this way (counted at L1's census) | [DESC-DEAD] |
| U-locate | a lookbehind's item as a LOCATE candidate: a window span at its negative offset, in the one find-the-span choice set (`(?<=\x00\x01)[a-z]+`) | L3, and a bench cell whose rarest bytes are in a lookbehind | [LOOK-LOCATE] |
| U-ctxsides | `MkEnd.ctx_before/ctx_after` read from the producer instead of the anchored DFA | a second machine-side consumer, or cover B1 | [CTX-SIDES-PRODUCER] |
| U-omin | the kit's true positive presence `omin` (`memfn.h:679-684`, "the true omin is B5's") from the run's `[omin, maxoff]` | the kit's B5 request | [PRES-OMIN-TRUE] |
| U-descguard | guards meet DESCRIPTION positions, where a gap is a position (`x(?=ab\|ac)a.` → `xa[bc]`) | alt_normal_form stage 3 (set positions) or G-1, whichever makes the description the run's position source | (inside [RUN-POS-SET]) |
| U-exactwidth `[r2]` | CAT-EDGE carries a guard across any EXACT-WIDTH neighbour (`minw == maxw`), not only an `all` one: `(?=abc).bc` keeps `a` (the run-side half of U-descguard, needing widths only) | L1's census showing guards dropped at fixed-width non-literal neighbours | (inside [REQ-LOOKAROUND]) |
| U-nesteditem `[REV 3.3, D27 F4]` | a nested positive lookaround's narrowing reaches the outer item: the head-guard meets the body's CONSUMED head run, read through the nested item (`(?=[a-z]{2}(?<=xy))[a-z]{2}z` → `xyz`) | a census of corpus and bench patterns with a positive lookaround nested in a positive lookaround's head that the rule would move (D27 rows A11, A11k, A11w are the witnesses) | (inside [REQ-LOOKAROUND]) |
| U-assoc `[REV 3.3, D27 F5]` | guards compose ASSOCIATIVELY: adjacent items meet each other before either meets a consumed neighbour, so `(?=xy)(?=xz)\w+` lists `dead` and `(?=ab)(?=a.c)` states `abc` | a census of adjacent positive lookarounds whose meet differs from the right-nested one (D27 row B05 is the witness) | (inside [REQ-LOOKAROUND]) |
| U-vm | an exact `X{n}` matched by one compare in the VM | a VM bench cell with an exact counted repeat on its hot path | (inside [REPEAT-RUN]) |
| U-pieces | `req_pieces` through repeats feeds alt_normal_form U3 | the kit's answer to that request | (inside [RUN-POS-SET]) |
| U-G1 | kset/startset/endwin read the description (alt_normal_form G-1) | G-1's own census | (inside [RUN-POS-SET]) |
| U-rewrite | [REWRITE-ADJ]'s REP members read T2 | [REWRITE-ADJ]'s first build | (inside [REWRITE-ADJ]) |
| U-post | [POSTFACT]'s marks use the reach as their vocabulary (§7) | a design lane for span intersection or the marks | (inside [POSTFACT]) |
| U-bestof `[REV 3.1, review r51 CONFORM-11]` | ONE candidate reducer `rn_best_of(const RbCand *c, n)` over (run, extent, arm) candidates with `rn_cmp` its relation; TOP's table, `rr_cat`'s five-way `rn_better` chain (`{l.best, r.best, join, head, tail}`) and `rr_alt_affix`'s pair its callers; each `rr_cat` candidate source becomes arm-restorable and the listing can name WHICH candidate won as a why | [RUN-POS-SET] stage 3m (the next change to `rr_cat`'s best selection), or a fourth candidate source; not L3 (TOP needs only `rn_cmp`) | (inside [RUN-POS-SET]) |
| U-bound `[REV 3.1, review r51 CONFORM-12]` | `PfBound` (D-7) grows into the offset-bound family's one value: states `NONE`, `NEVER`, `BOUNDED`, `UNBOUNDED` with a signed `[lo, hi]`; K a `PfBound` read at position 0, the run's `[omin, maxoff]` the same type; `RB_OFF_UNBOUNDED` and `whole_len < 2` retired as encodings; the `PCREC_W_UNBOUNDED == PCREC_MINW_MAX` pun separated into two states | the kit's B5 request ([PRES-OMIN-TRUE]'s trigger) or the next touch of `RbSet.off`/`ReqSet.maxoff` (register row 24's event) | [PRES-OMIN-TRUE] / register row 24 |
| U-edge `[REV 3.1, review r51 CONFORM-13]` | one desc.c reader of the positions nearest an edge, `pcrec_pd_edge(desc, dir, max_pos)`, shared by the item (D-10) and [VLOOKBEHIND] stage 2's fixed-tail hoist; A-REV's reverse readers and [CTX-SIDES-PRODUCER] read the same edges | whichever of the hoist and L1 builds first: the second calls the first's reader | (inside [VLOOKBEHIND] / [REQ-LOOKAROUND]) |

## 11. Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.** Every number here is a compile-time fact of this box's
   compiler (gcc 15.2, Zen 4, the lane's own build of `c054e38e7`); answers from libpcre2-8
   10.46. Each unit's speed claim is owed per regime at the pick rows it moves (bench strata; for
   L3 a find-all regime, where the step back is paid per call and `lb_bytes` caps it). A
   different regime can flip a pick, which D186's bar at those rows decides.
2. **Independent control: RELEVANT.** Each census is an independent model of T2/T3/T4 over byte
   spellings of the lowered trees (no compiler code), compared two-sided with the observed movers
   (K35: the population is corpus + bench, counted). Each witness has a libpcre2 expectation,
   never pcrec's. Each sabotage reaches its site ([MECH-REACH]): rev 2 checked the lowering
   (`kinds`), the locator (`RX_DFA_SCAN`) and the pin (k-set) of every witness at `c054e38e7`
   (§5.7), the r2 lesson. Each witness's failure needs its sabotaged run to clear the floor and
   stay unverifiable (§3.6), which the build re-measures. The `-fno-ctx-node` run identity
   is a control that shares no source with ITEM's `A_CTX` row: the other lowering reaches
   ITEM through the description. `[r3 READY-4]` It is shown to FAIL on the rows it names
   (`a(?=b)[bc]`, `ab[xy](?=(?<=x)y)[xy]`, §5.1), not on W-C1, where the run is `ab[bc]d` with
   or without the row.
3. **What moves when data is regenerated: NOT RELEVANT beyond today's.** The arms add no table,
   calibration or data file; a UCD regeneration moves fold classes and so runs, as today.

## 12. Proposed decision (D-next, text only) and the D168 addendum L1 files

**D-next.** The one fixed-width description gets its REP, EMPTY and positive-LOOKAROUND arms, and a
run's reach is its signed interval `[omin, maxoff]`. `X{m,n}` reads as `X^c · X{0,n−m}` (head,
best) and `X{0,n−m} · X^c` (tail), c derived from the run's storage bound and `maxw` always exact.
Every node that consumes nothing is CAT's width-0 unit. A positive lookaround, in either lowering
(`A_LOOK`, or `A_CTX` NEXT/PREV), is the unit plus its ITEM, read from D168's one context producer;
the run derives its own cube hull of the item within `pos_set` and carries it as pending guards
that `rr_cat` meets, carries across an exact-width neighbour or drops; a narrowed consumed byte
joins the necessary set; a value carries a DEAD bit; only the top level may extend the run, at the
reach its readers admit (BACK capped by the `lb_bytes` step-cost row), and the scan member is
always a consumed position: `[r4 READY2-2]` pcrec states the run's consumed extent and the kit's
one member decision picks inside it, which every pcrec reader reads (no second picker). No stored `ahead`. The walk's inputs are one declared table of walk
parameters filled at the one walk entry; `facts.def`'s deny column keeps its one meaning. No
public flag bit (bit 31 re-specified at L3). The handoff's K is the window's offset of either
sign, and every move from it is `max(posvar, c − K)`; the VM attempt-loop rows take it like every
other row `[r4 READY3-4]`. Staged E1, R1, E2, L1, L2, L3, R2, each on its census.

**D168 addendum (text L1 files with its build)** `[r2 S8]` `[r3 READY-6]` `[REV 3: SUPERSEDED by the rev 3 addendum below: the span slice it names is deleted]`. "The context producer has two halves
by placement, one source each. The IN-SPAN half (offsets `d >= 0` inside span 0, per thread) is
`span_facts`' k-set frontier in `src/facts/kset.c` (D168 named `src/facts/spans.c`, which was *(superseded by cover_cap.md rev 4, 2026-11-15)*
never built), reading the lowered `N_CTX` nodes. The ITEM half is one combinator of the fixed-width
description (`src/facts/desc.c`), called by the run walk (`src/facts/req.c`) at each positive
one-sided context node: an `A_CTX` NEXT/PREV gives its set at 0/−1, a positive `A_LOOK` its body's
description placed at the cursor and united per offset across width groups. Each item's terms are
EXACT byte sets at signed offsets from the item's cursor, with a form (EXACT/SUPERSET) and an
absent cell. Both halves read `ctxfn.def` for an `A_CTX`, so the node has one definition. Readers
place an item in their own coordinates: the run against its neighbours (span_arms §5.2), span_facts' *(superseded by cover_cap.md rev 4, 2026-11-15)*
context records at span 0 (ctx_span P1a/P1b, whose `look-fixed` row reads the item rather than
walking the body), the window spans ([LOOK-LOCATE]) and the presence `omin` (span_arms L3). No
reader derives the sets a second way; a reader that narrows them (the run's cube hull within
`pos_set`) does so locally and never writes back.
The item half's members are the POSITIVE lookarounds (`A_LOOK` positive, and `A_CTX` NEXT/PREV),
placed at signed offsets from the item's cursor, the cursor being the origin ruled at rev 2.
This WIDENS D168 in one respect: a bounded variable-width lookbehind gets a SUPERSET item
covering positions outside the match on both sides, where ctx_span §3.3's `look-other` gives
none; the step-back through a lookbehind is bounded by the per-encoding `lb_bytes` cost cap
(span_arms §5.5), and a lookahead needs no bound. The `\b`/`\B` fold, the negated one-sided
rows, `look-neg-1` and `pos-start` at −1 are NOT members of the item half: they are zero-width
cuts, owned by the EMPTY/E2 arm (span_arms §4.1), and are homed there, not in a second
producer."
**D-next, rev 3 amendment** `[REV 3]` (D191.1 adopted §12's D-next "as amended by 2 and 3"; this states the
lookaround half as the tree at T and the accepted architecture note leave it, for the manager's record, not a
new ruling). A positive lookaround, in either lowering, is CAT's width-0 unit plus its ITEM, built in the
description's own area (`src/facts/desc.c`): a lookahead's item from the head column (`PdHead`, the FIRST
positions), a lookbehind's from the body's description (its LAST positions), united per offset by the
module's one union (`pcrec_ph_alt`). The run carries pending guards that `rr_cat` meets (fixed steps), carries
across an exact-width neighbour or drops; "this run can never match" is the never family's ONE propagation
(rows shared with derive.c's prune), rendered on `req_whole_run` as the why `dead`; a narrowed consumed byte
joins the necessary set at the walk's exit. Only TOP extends the run, by a combining row table (AHEAD, BACK)
whose rows the `look` arm passes over; BACK is capped by `lb_bytes`. The run crosses to the kit as ONE uncut
span; K is its position-0 offset with a stated state (none / bounded / unbounded), of either sign; `omin` is
`min(0, K)`, the sound under-estimate (`[REV 3.1, review r51 CONFORM-8]` the true interval is [PRES-OMIN-TRUE]'s); the consumed extent is pcrec's own (`req_byte`, the run pin); every move from K is
`max(posvar, c − K)` with no unsigned wrap; the VM attempt-loop rows take it like every other row. No public
flag bit (bit 31 re-specified at L3). Staged L1, L3, L2 (§14.4), each on its census.

**D168 addendum, rev 3 (the text the first unit, L1, files; the manager files it in decisions.md)**
`[REV 3.1, review r51 RULING-2, RULING-3: the quoted text now says what it amends in D168 and whose reading "ONE
producer" is; the manager files it without the inline REV markers]`
`[REV 3.3, review r55 TABLE-3: the text now says what L1 BUILT: member sets, not hulls; no form/absent cell; assembled
in req.c]`
`[REV 3]` "The context producer of D168 is ONE producer of per-offset sets at signed offsets: the lookaround
ITEM, assembled by the run walk (`src/facts/req.c`, its own statics) at each positive one-sided context node
from the fixed-width description's readers (`src/facts/desc.c`: the head column, the description read reversed);
the assembly moves into `desc.c` when a second reader of the item exists (D77). An `A_CTX` NEXT/PREV gives its set at 0/−1; a
positive lookahead gives the head column of its body (the positions every match consumes FIRST, at offsets
0..h−1); a positive lookbehind gives its body's description placed right-aligned at the cursor, united per
offset across width groups (offsets −h..−1). Each term is an EXACT byte set, a set of members (D187
addendum 1), never a hull; a term the run's domain does not admit ends the item there. The item has no form and no
absent cell: a SUPERSET form and an absent cell are not built until a reader needs them (D77; L3's bounded
variable-width lookbehind is the first). D168's named home, the span slice (`span_facts`), was deleted by
[COVER-CAP] stage 1; the cover's own edge context (the byte before and after its span) is the anchored
machine's walk (`src/gen/known.c`), which answers a different question (two-sided, per thread) and is not a
second producer of these sets. Every reader places an item in its own coordinates and reads it from this one
producer: the run (as pending guards), the kit's presence run span (the run uncut, `foobar` at −3 for
`(?<=foo)bar`: the owner's span, 2026-11-18; that this makes ONE producer is the manager's reading of his
ruling, checked against D168, D172 and D191.3 `[REV 3.1, review r51 RULING-2]`), D172's window site,
[LOOK-LOCATE], [CTX-SIDES-PRODUCER]. A reader
that narrows the sets (the run's meet by set membership within `pos_set`) does so locally and never writes back.
[CTX-FACTS-NEG] keeps only what the item cannot state: `\b`/`\B` folded at an offset, the width-1 negative
lookbehind's complement, sets past the subject's end, and thread context. The `\b`/`\B` fold, the negated
one-sided rows and every negative lookaround are NOT item members: in the run walk they are CAT's width-0
unit (the EMPTY/E2 arm). Not stored as a fact until a second reader exists (D77). `[REV 3.1, review r51
RULING-3]` THIS ADDENDUM AMENDS D168: its title and member list. D168 named one `span_facts` producer with three
members (`\b`/`\B` through the fold, the fixed positive lookbehind, the width-1 negative lookbehind's
complement); from this addendum the ITEM is the one producer of POSITIVE one-sided lookaround sets, and `\b`/`\B`
and the negative complement move to [CTX-FACTS-NEG]. This is not D168's "two mechanisms for one fact": the
item states the sets a positive context REQUIRES on one side of the cursor; `\b`'s fold needs both sides (the
byte before AND the byte after, a relation the item cannot state) and the negative complement states what is
EXCLUDED, a different fact; neither is an item member, so each fact still has one producer. [CTX-FACTS-NEG]'s
scope here (`\b`/`\B` folded at an offset, the width-1 negative lookbehind's complement, sets past the subject's
end, thread context) adds the negative complement to the plan row's NOTE (`\b`, past the end, thread context);
the manager aligns that NOTE when filing."

## 12a. Owner ruling 2026-11-08: scan bytes from any run position

Frank, on question 4 / READY2-4 ("why must the scan byte be inside the match?"): "Now or later, the scan bytes should come from any span position. In barbaz case, it could then validate the entire span and finish the search."

Consequences (manager, to be folded into the L2 text and the §8.2 kit request before L2's readiness critic):
- The CONSUMED-ONLY scan pick (A13, CAT-SET's L2/L3 restriction) is the interim form at most; the end state is that every run position, consumed or guard, is a scan candidate, chosen by the kit (question 7's leaning stands: the kit picks).
- Two facts, not one: `<PREFIX>_REQ_BYTE` keeps its published meaning (a byte every MATCH consumes); the scan choice is the kit's internal pick over the whole run (what every successful ATTEMPT reads). This is a split of two genuinely different facts, not a parallel mechanism.
- The §8.2 request therefore states, per run position, its byte set and its signed offset from the attempt start, and NOTHING about consumption (Frank 2026-11-08: "why does kit need the byte consumed?"; it does not). The kit's search reads only where an attempt could start relative to a position; which positions the match consumes is pcrec's own fact, read by pcrec's readers only (the `<PREFIX>_REQ_BYTE` stamp, chosen by pcrec among consumed positions, and the reported match bounds). With the kit the only scan picker, pcrec's stamp is no longer a copy of the scan pick, so today's agreement check between the two picks retires. No unused field crosses the seam (memory: no silent defaults; D157).
- "Validate the entire span and finish": when the run is the whole attempt's fixed text (`bar(?=baz)`: the attempt is `barbaz`, the match `bar`), a hit verified across the whole run IS the match, so the matcher reports it without the engine's own finish. This is D187 add. 1's "earn a skip" (the kit replies exact, pcrec skips its finish), stated per run; it needs the run to be exact over the whole attempt; pcrec turns the verified attempt position into the match bounds itself (two offsets it already holds), so even here the kit is told nothing about consumption.
- NO PRE-CUT (Frank 2026-11-08, "does kit still get a list of spans with offsets and max overshoot?"): the seam stays D172's list of span statements (position sets, D187; signed offsets from the attempt start, `omin`/`maxoff`, `head_max`, the verify flag). §8.2's step "pcrec cuts its 8-position window around the member" is withdrawn: pcrec states the WHOLE run as ONE span, uncut, and the kit chooses the scan position and how much of the run it verifies, replying with its choice; pcrec's readers (the stamps, `--emit-facts`) read that reply. `PCREC_MAX_REQ_RUN_EMIT` (an unmeasured pcrec constant) stops shaping what the kit sees; any length limit is the kit's own priced choice. A run is one contiguous fact: pcrec never splits it into several spans (that would be pcrec choosing the kit's layout again).
- Timing (manager's leaning): fold it into L2 now, because L2 already waits on the kit's request; the request is written once with the end-state fact.

## 12c. Correction to §12a's 'validate the entire span and finish' (review 2026-11-09 r2 r38s F1, ruled)

A run stated as per-position byte sets is a COVER of the attempt, not its language: `(?:ac|ca)xyz` states `[ac][ac]xyz`, which admits `aaxyz` (libpcre2: no match). So a verified run proves the match only when two pcrec facts hold for that run: SUFFICIENT (every string the stated sets admit is an attempt of the pattern over the span) and OUTPUTS-DETERMINED (the reported bounds and every capture follow from the attempt position alone: no capture inside the span, no `\K`). The kit reports only how far it verified; the earned skip is pcrec's decision when all three hold. The owner's ruling stands with these preconditions.

## 12b. Owner rulings 2026-11-09 on §13

- Q1 (repeats as copies): YES. Frank's concern: the kit proves `abab` but pcrec cannot reverse from the proof and must rematch. Recorded answer: repeats-as-copies does not add a reversal; each copy has a fixed width, so the attempt start stays the hit minus a fixed offset wherever it was fixed before. A rematch (the engine's finish) happens today for every run that does not cover the whole attempt exactly; where the run IS the whole attempt and exact (e.g. `xy(?:ab){2}zw` alone), D187 add. 1's earned skip applies and no rematch is needed. Variable repeats (`X{2,5}`) count only the X^m prefix, so the finish still runs.
- Q2 (zero-width assertions stop cutting the run): YES, read as "complete the task while we're in there" (Frank: "cracking open a piece of code comes with overhead"): unit E2 joins across every zero-width item that shares the cut site (`\b`, `$`, `\K`, lookarounds), not `\b` alone; its census still runs, as the unit's measurement record, not as a build gate.
- Q4 (lookbehind cap = declared lookbehind length): AGREED.
- Q5 (L3 before the start-position clean-up, sites in its table shape): AGREED.
- Q6 ([REWRITE-ADJ] design starts once this note is ruled): AGREED.
- Q3 (one run value vs two facts): (a) ONE VALUE, Frank 2026-11-09; every reader raised together in one unit.
- Frank's follow-up (2026-11-09): for `abc(ab){3,5}xxx`, once the search has proved `abcababab`, can the finish start after it? Answer: yes in principle, already filed as [MATCH-KNOWN]'s prefix-skip member (D142); span arms lengthens the provable prefix; the skip additionally needs the kit to REPORT how far it verified (§12a lets it choose). Not part of this build.

## 12d. Build-time scope rulings (manager, 2026-11-09; recorded for the frozen §4, §8 and T7 text)

- E1 (lane sae1): T2 row 1 (a width-0 repeat with m>=1 takes its body's value) also moves `(?:\b)+`/`(?:^)+`, which §4.1 gave E2: KEPT under E1 as the general rule; E2 reuses it (review 2026-11-09 r3).
- E2 (lane sae2): takes T3 row E-1 (plain A_EMPTY mid-CAT) from alt_normal_form stage 2a (not scheduled); restore arms: `empty` for plain A_EMPTY and width-0 repeats, `zero` for E-4 and E-5 (both restored at E2; L1 re-splits E-5). E2 owns the run's definition in match_api §6.3.7¶6 and tuning §2.28¶1 ('every successful attempt contains the run', covering `\K`); L2 adds only its past-the-consumed-end clause. `<PREFIX>_REQ_BYTE` is a byte every successful ATTEMPT consumes (D191's 'consumes'), the same frame; under `\K` it may lie before the reported start (review 2026-11-09 r4).
- R1 (lane sar1): the manager first accepted two §3.4 cells that tie the other way (`xy(?:ab){2,3}zw` -> `ababzw`, `xy(?:ab)+zw` -> `abzw`) as answer-free; REVERSED by review 2026-11-09 r5 (EMIT-1/EMIT-2: equal answers, 4-7x the instructions): no run choice depends on argument order or spelling; equal-length candidates, also at a truncated join where the 32-position store fills, are broken by the byte-rarity estimate the pick already reads. Under utf8 `(a.){10}xyz`'s pieces' drop reason moves (advisory); the reason is made order-free (r5 CONTRACT-2).

## 13. Open questions for Frank (plain words, each with a leaning)

1. **Should a repeat count as its copies for the required run?** Today `xy(?:ab){2}zw` gives the
   two-byte run `ab`; spelled out, `xyababzw` gives all eight. The rule reads `X{2}` as `XX` and
   `X{2,5}` as two copies then "maybe more" (for the start) and "maybe more" then two copies (for
   the end). Leaning: yes, as unit R1, built when its census shows a bench cell.
2. **Should `\b`, `$`, `\K` and lookarounds stop cutting the run?** They consume nothing, so the
   bytes on either side are adjacent: `xyz(?<=yz)abc` could give `xyzabc`. Leaning: count it
   (unit E2's census) and build it if a bench cell moves.
3. **A run that reaches outside the match: one value for every reader, or two facts?** With a
   lookbehind, the run of `(?<=foo)bar` is really `foobar`, starting three bytes before the
   attempt. Most readers already cope; the ones that do not are the kit's start-offset and
   landmark-distance fields (the kit honours them), the handoff's offset and its two "move the
   start" emitters (today they would report a match before the start offset, the r2 review's one
   forced error, now fixed in the text), the facts' own derivation, the pick arithmetic and the
   listing. Option (a): one run, computed at the reach every reader accepts, raised for all of
   them together in one unit. Option (b): a second, wider run beside today's. Leaning (a): one fact
   and one walk; (b) is the parallel mechanism you asked us not to build.
   `[r4 READY3-4]` One reader changed since: the VM's attempt loop (patterns with a backreference)
   would have quietly switched its start-skipping off for every lookbehind run; it now uses the same
   corrected move as everyone else, so no pattern loses it (`(?<=foo)bar(\w)\1` keeps it).
4. **The `<PREFIX>_REQ_RUN` stamp promises "a run every match must contain".** A lookahead run
   (`bar(?=baz)`'s `barbaz`) extends past the match, and a `\K` pattern's run already lies before
   the reported match. Leaning: at L2, reword it as "every successful attempt holds this run",
   keep `<PREFIX>_REQ_BYTE` a byte the match itself consumes, show the reach in `--emit-facts`,
   and leave any new stamp spelling to the interface push.
   `[r4 READY2-4]` The cost of this leaning, so you rule it knowingly: because the reported byte
   stays one the match consumes, the byte the search SCANS for is always a consumed one. A rare
   byte inside a lookahead (`bar(?=baz)`'s `z`) then never becomes the scanned byte; it only joins
   the comparison done at each hit (fewer false hits), and only when it sits within 7 bytes of the
   scanned byte. A pattern whose only rare bytes are in a lookahead gains less than a scan on them
   would give. The other choice, reporting a byte outside the match, breaks a promise callers can
   read today.
5. **How far back may a lookbehind run start?** The scan for `(?<=foo)bar`'s `foobar` begins
   three bytes before the start offset. The cap is the pattern's own declared lookbehind length
   (PCRE2's `max_lookbehind`) in bytes: the same number under `byte`, four times it under
   `utf8`. It is there to bound the extra bytes each search call re-reads, not for safety (the
   scan never reads outside the subject). A lookbehind inside a lookbehind can need more: in
   PCRE2's non-UTF mode `(?<=c(?<=bc)d)e` reads three bytes back while its declared length is
   two, so under `byte` such a run keeps today's value; in UTF mode PCRE2 does not match it from
   that far, and under `utf8` the cap admits it. Both are safe. Leaning: this cap, plus whatever
   bound the kit puts on its start-offset change.
6. **When does [REWRITE-ADJ] start?** Leaning: start its design once this note is ruled, not after
   its units are built.
7. **Who picks the byte the search scans for: pcrec or the search kit?** `[REV 3: answered by D191.2 and delivered at K38-2, §14.1 item 3]` `[r4 READY2-2]` Today both
   compute it, by the same rule, and the compile stops with an internal error if they disagree.
   The lookahead unit changes the rule (only bytes inside the match may be picked), so changing it
   on one side alone breaks every such compile (measured by the review's plant). Leaning: the kit
   picks, as it already officially does; pcrec tells it, as a plain fact, which positions of the
   run are inside the match, and stops computing its own pick. Consequence: the lookahead unit
   waits for the kit's delivery, and the request is written (§8.2) for the manager to file.
8. **Build the lookbehind unit now, ahead of the planned clean-up of start-position handling?**
   `[r4 READY3-7]` The clean-up (the roadmap's position-domain step) will first list today's
   start-adjusting code sites in one table; it is not scheduled, and it waits on another step. The
   lookbehind unit changes the arithmetic at two of those sites but adds no new kind of site. The
   manager ruled: build now, and the note lists the two sites in the table's own shape (§8.1), so
   the clean-up copies them unchanged. Leaning: confirm.
9. **Which of the two run-extension units goes first?** Both need the same new piece (which run
   positions are inside the match) and the same kit delivery. Leaning: whichever is approved first
   builds that piece and the other reuses it; the lookbehind unit is the one ready for your go now,
   the lookahead unit after the kit answers and one more short review.

## 14. REV 3: the lookaround units L1, L3, L2 against the accepted architecture note `[REV 3]`

Lane spanarms7 (opus, 2026-11-18), the DESIGN step of [REQ-LOOKAROUND]'s requirements → architecture →
design → build split. This section is the design of record for L1, L2 and L3 against
`docs/design/req_lookaround_arch.md` (ACCEPTED rev 2.1, "the note"; its site ids are "site n", its remodels
RM-1..RM-5, its hand-ons D-1..D-16) and the tree at **T = main `8993b8f82`**. Where rev 2.2's text above
still holds it stays; every rev 2.2 passage this section replaces carries an inline `[REV 3: ...]` marker
pointing here. E1, R1 and E2 are not this revision's: they are cited only as built state (§14.0).

### 14.0 Base, built state, binding rulings

- **No code drift from the note's tree.** `git diff --stat 57fcb5737 8993b8f82 -- src memfn/src
  memfn/include lib cli docs/spec tests/mech/sabotages docs/dev/decisions.md docs/design/span_arms.md`
  prints one file, `memfn/docs/requests.md` (R-46, a request text): every code cite of the note holds at T
  (C-R0). Code cites below are read at T.
- **E1, R1, E2 are BUILT at T** (C-R1: `git grep -n "span_arms E1\|span_arms R1\|span_arms E2" 8993b8f82 --
  src/facts/req.c` prints req.c:477 (R1's tie rows), :732 (the power arm, R1), :991 (T2 row 1, E1), :993 (T2
  rows 2-3, R1), :1077, :1080, :1082 (T3 E-1, E-5, E-4, E2)). So L1's depends-on (E2; E1 for W-F4; R1 for the
  REP guard row, W-RG, W-T1) is MET, and W-T2/W-T3 need no "at R1's landing" clause.
- **Binding rulings, quoted.** D191.1: "**BUILD GO** (Frank 2026-11-09, "Go on build") for the units of
  docs/design/span_arms.md rev 2.2 §8: E1, R1, E2, L1 and L3; L2 after the kit's delivery of R-38 plus one
  readiness critic on its changed text"; "a unit whose census finds NO mover anywhere stops and reports".
  D191.2: "the run crosses as ONE uncut span with byte sets at signed offsets from the attempt start; nothing
  about consumption crosses the seam". D191.3: "a run outside the match is ONE run value, every reader raised
  together, never a second wider fact"; "the lookbehind step back is capped at the declared lookbehind
  length"; "L3 builds now, ahead of A-POSDOM, its two sites in that table's shape (§8.1)". The owner,
  2026-11-18 (context-producer-home), in full: "I do feel like we've covered this ground several times. The
  search span the pcrec delivers to kit should have "foobar" with starting index -3. in this case, the match
  is proved and search is over. Otherwise, the kit reports back the 0 span subject offset and pcrec does the
  match". The manager's r50 rulings A6 (RM-3 merges the ARITHMETIC only, the two ROUNDUP calls stay in their
  callers), A8 (the never fact has ONE home, the never family; READY-5's listing is its rendering), A17 (the
  design decides between SHARED through desc.h's head column and a noted deviation). The manager's
  remodel-go call: "the unit's CENSUS first ... then its remodel commits, then the feature; a unit stopped at
  its census lands no remodel commit".
- **Order of the units: L1, then L3, then L2.** L3 has its go and L2 has only its readiness critic left
  (§14.1 item 2), so L3 lands first and builds the shared pieces the arch note says "whichever lands first"
  builds (the consumed extent, RM-4); L2 reads them. `[REV 3.1, review r51, the manager's ruling on READYL2 as
  D191.1's critic: review r51's READYL2 lens IS L2's "one readiness critic on its changed text"; it is DISCHARGED ON
  CONDITION, when this revision applies READYL2-1..6 and the confirm critic reports them applied.]`
- `[REV 3.1, review r51 CONFORM-6, CONFORM-10]` **A sixth remodel, RM-6, outside the note's RM-1..RM-5:** the never
  rows as a NEVER column of `src/core/kindrow.def` (D-9). It RIDES L1 as its own answer-identical commit after
  RM-1 (the manager's ruling, confirming the spanarms7 report's F-3: covered by the remodel-go call's reasoning,
  answer-identical and gated alone). It carries register row 5, whose event "per pass, when the pass is next
  touched" fires at this commit for derive.c. `[REV 3.2, conf-spanarms8 (register proposal), RULED: row 5 is a per-pass row, so "riding" for the
  whole row misstated it]` Register row 5's status, ENTERED 2026-11-18: "open (per pass); derive.c's never pass rides L1
  (RM-6, span_arms.md)".
- `[REV 3.2, conf-spanarms8 D2]` **An L1 remodel outside the RM-n series, the head-rule extraction ("remodel 3" in §14.4 L1), outside the
  RM-n series:** READYL1-6's move of the per-kind head rule from altnf.c's `anf_head` into desc.c with a position
  callback (D-10) IS a remodel commit of L1, listed here beside RM-1..RM-6 as an L1 remodel that carries no RM number.
  It rides register row 27's own event (L1: "one per-offset-head primitive for the description and the item", row 27's
  form (a)). Confirmed by the manager 2026-11-18 (conf-spanarms8 D2); it rides the owner's 11-09 build go under the
  manager's remodel-go reading, which the owner may overrule `[REV 3.3, review r53 F11: now ruled, D191 addendum 2
  ("small refactors ride the build go"); §14.8 item 10]`. Its answer- and byte-identity is a BUILD-LANE GATE, the
  remodel commit's own identity check (§14.4 L1 remodel 3), not a claim made at design time.

### 14.1 What in rev 2.2 is STALE at T, and what replaces it

| # | rev 2.2 passage | why it is stale at T (command) | replaced by |
|---|---|---|---|
| 1 | §5.3 "Where it lives": the producer's two halves, kset's in-span half, `span_facts`, `MkCtx`, P1a/P1b as the item's second reader; §12's D168 addendum naming `span_facts` | [COVER-CAP] stage 1 deleted the span slice (C-R3: `git grep -n -i -E "span_facts\|MkCtx\|pcrec_span_walk" 8993b8f82 -- src` prints nothing); the cover's edge context is `known.c`'s anchored-machine walk | §14.3 D-10 (the item is built in desc.c's own area, SHARED with the head column) and §12's rev 3 addendum (ONE producer: `[REV 3.1, review r51 RULING-2: the MANAGER'S READING of the owner's 2026-11-18 ruling (REQ-LOOKAROUND.md: "to be checked by the design lane"); the owner's words name one SPAN, "foobar" at −3, not one producer. CHECKED, it holds on the record: D168's title "context around a search span is ONE `span_facts` producer of per-offset sets"; D172 "sourced from main's D168 producer"; D191.3 "a run outside the match is ONE run value, every reader raised together, never a second wider fact"]`) |
| 2 | §8.2, the kit request (parts A and B), and every "after the kit's delivery of §8.2" in §8 and its Order paragraph | DELIVERED in §12a's end-state form: R-38 K38-2 (MF_SITE_ABI 27) then Part D + R-41 (29). memfn.h's MF_SITE_ABI history: "`omin` is measured from the ATTEMPT start and may be negative on the run span; head_max is int64_t, the run's position-0 offset; the twin admits by max(K, 0)"; the presence class text: "the run part's candidates c satisfy max(0, lo + omin) <= c, computed without an unsigned wrap"; `head_max` "SIGNED: with a negative run `omin` it may be negative or 0"; `MF_HEAD_MAX_UNBOUNDED` "is the stated value "K unbounded"" (C-R4) | withdrawn; nothing is asked of the kit by L1-L3. `[REV 3.1, review r51 RULING-9: "after the kit's delivery of R-38" (D191.1) is read as delivered for parts A, B and D (MF_SITE_ABI 29; review r51's READYL2 confirms Part A); R-38 Part C is UNSCHEDULED (memfn/docs/requests.md: it "rides with whichever unit builds the earned skip", plan row [EARNED-SKIP], PARKED by D194's addendum) and L2 does not need it. This is a READING of a ruling's precondition, the manager's (ruled FIX-NOW in r51), not the owner's words]` |
| 3 | §5.4 A13 and its closing paragraph ("THREE deciders held equal by two loud checks", `req_run_member`'s internal error, "the KIT's one member decision picks inside `cons`"), A1's "the presence run span carries the consumed-extent fact", §9's "pcrec's own member pick" row, §12's D-next "the kit's one member decision picks inside it" | the loud check retired at K38-2 (C-R5: `git grep -c req_run_member 8993b8f82 -- src` prints nothing); D191.2: the kit picks the scan position over the WHOLE run and "nothing about consumption crosses the seam" | the consumed extent is pcrec-internal, read by `req_byte` and the run pin only (§14.3 D-5, D-6, D-14) |
| 4 | the 8-position window: `pcrec_req_window`, `PCREC_MAX_REQ_RUN_EMIT`, the rows `req_run`/`req_run_maxoff`, the window's `at`, "K is the WINDOW's offset, `omin + at`" (§5.2 TOP, §5.4 A3/A9, §5.7 condition (5), W-L11, W-L12, W-T2, W-T3, §8 L2's trigger "within 7 positions of the consumed member"; `[REV 3.1, review r51 READYL1-8 (c)]` W-T1's §5.7 reason, which still argues from the window: at T its pattern stamps the whole 32-position run, `RX_REQ_RUN "6161...6262@31/fdfd...fefe"` (r51 READYL1, measured), and `--memfn=no-fd-pres-pick` still "tests every member and the whole run" (tuning §2.29¶1), so W-T1's L1 row under the flag stays valid; its default-flag answer is NOT claimed to move: the kit's 8-position verify picks one stretch for both runs, as READYL2-1 measured for W-T2's) | retired at K38-2: facts.h's header "Since R-38 K38-2 nothing is CUT: the window `bytes`/`mask`/`at` and its `maxoff` retired with `PCREC_MAX_REQ_RUN_EMIT`"; facts.c:345-357 derives K as the WHOLE run's `whole_maxoff`; `facts_listing.md` §4.1.2¶8 lists the run once | K is the whole run's position-0 offset; at L3 a BACK run's K is `−t` (§14.3 D-7) |
| 5 | §9's `req_run_omin` row "beside `req_run_maxoff`: one row per offset fact" and §5.4 A9's `omin` fields `RbRun.omin`/`ReqRun.omin` | its sibling row retired (item 4); every run TOP builds has `omin = min(0, K)` (§14.3 D-7), so a stored `omin` is a second spelling of K `[REV 3.1, review r51 CONFORM-8: of the SOUND UNDER-ESTIMATE only. `min(0, K)` is not the run's true interval: `x.?bcd` states `bcd` at K 2 whose true position-0 offsets are {1, 2}, so the true `[omin, maxoff]` is [1, 2] and is not derivable from K (r51 probe at B)]` | no field and no row: one accessor `pcrec_run_omin` (§14.3 D-7), stating the under-estimate. `[REV 3.1, review r51 CONFORM-8]` The note's site 11 row `req_run_omin` and the TRUE interval are DEFERRED to [PRES-OMIN-TRUE] on its own trigger (the kit's B5 request), not retired: that row will need the walk's LEAST offset, a new `RbRun` quantity beside today's `off` |
| 6 | §5.7's W-T2 and W-T3 "CANNOT fail on the answer" and their R1 clause | no window cuts the run any more, and R1 is built: the sabotaged run (`a^12 b^20` stated at 0, truly at 8; `a^12 b^20` stated at −20, truly at −12) is found at 8 by the presence scan, and the move from it starts the body past the match (hand-derived, §14.5 L3/L2 witness tables) | both are ANSWER witnesses at their unit; W-T2a/W-T3a are kept as the literal twins. `[REV 3.1, review r51 READYL2-1: at DEFAULT flags W-T2 and W-T3 still CANNOT fail: on their hybrid route the KIT verifies 8 positions around its scan member and picks the SAME stretch for the correct and the sabotaged 32-position run (identical reqrun bodies over 6 compiles at B, `memcmp(subject + cand + 24, "bbbbbbbb", 8)`). So W-T2 and W-T3 are answer witnesses UNDER `--memfn=no-fd-pres-pick` only (the run block becomes the whole-run compare: the sabotage finds c = 8 and answers NOMATCH against the oracle's (0,20) / (20,40)), as W-T1 is, plus their `req_whole_run` listing rows; the answer witnesses at default flags are W-T2a and W-T3a]` |
| 7 | W-L11 "K = 0", W-L12 "K > 0, the wrap" | K is the whole run's offset: −10 and −8 (item 4). A BACK run has `omin = maxoff = −t`, so "K > 0 with `omin < 0`" is UNREACHABLE (§14.3 D-7); W-L12's plant (today's text kept) answers (8,21) from 8 and NOMATCH from 9-15 like the oracle (hand-derived: from 14 the floor 6 finds no occurrence; from 8 the body at the hit 0 still finds (8,21)) | ~~W-L11 kept with K = −10~~; W-L12 RETIRED (cannot fail). `[REV 3.1, review r51 READYL2-2: W-L11 is RETIRED with W-L12. Its plant at K −10 ("the body starts at the hit") IS W-L10's plant, and on its own subject it cannot fail: `e^15 qzx` holds ONE occurrence of the whole run, at c = 0, so from 0/5/10 both builds give (10,18) and from 11/12 both NOMATCH, as the oracle. A start-at-hit plant fails only where a match starts in `[c, pos)` (overlapping occurrences), which W-L10, W-L13 and READYL3-1's witness carry]` |
| 8 | the `reach` walk parameter (§3.7's table row, §5.8 "forces reach `[0, maxoff]`") | a second spelling of "is the look form restored" beside the `look` arm (review r50 A15) | TOP's candidate rows with an arm column (§14.3 D-4) |
| 9 | CAT-SET as a step of `rr_cat` (§5.2) | `rr_pow`/`rr_rep_split` call `rr_cat` on `RbRuns` with no set (req.c:755-788), so a meet narrowed inside a repeat's copy joins would never reach the set, and `req_byte` could leave `req_set` (check 4) | one step at the walk's exit over the best's CONSUMED positions (§14.3 D-3) |
| 10 | DEAD as a T4 column of its own and a bit only the run walk propagates (§5.2 DEAD column, §9's DEAD row, §10 U-dead) | the manager's r50 A8 ruling: one home, the never family | the never family's shared propagation rows (§14.3 D-9); the `dead` why token KEPT as its rendering |
| 11 | "K carries a stated/none bit" (§8 L3, §9's sentinel row) | RM-2's three states (review r50 A7: ten hand tests, an unbounded state the kit names) | §14.3 D-7 |
| 12 | §5.1 "`A_LOOK` positive: the body's DESCRIPTION placed at the cursor" for BOTH directions; §5.3 "Bounds" (a wide lookahead body loses its head terms) | the description keeps a group's LAST positions (desc.h's `PdCfg`), the wrong end for a lookahead; desc.h's head column keeps the FIRST (review r50 A17) | AHEAD reads the head column, BEHIND the description (§14.3 D-10) |
| 13 | §2 "refused below 0 today, `memfn/src/compose.c:608`"; A1 "`memfn.h:679-681`'s ... is the kit's sentence to change" | delivered (item 2) | §14.3 D-14 |
| 14 | §5.6's "today" column and its L1 cells for rows E2 already moved | E1, E2 and R1 moved it (C-R2) | §14.2 |
| 15 | §5.4 A3's margin cast `[r4 READY3-2]` | DISCHARGED at T: `pcrec_landmark_margin` reads `k > 0 ? k : 0` (emit_dfa.c:9293, the note's F-3) | nothing to build |
| 16 | every `emit_dfa.c`/`facts.c` line cite in §5.4, §8.1, §9 | the file moved since `1ffcce0c1` | the note's site map (its cites hold at T, item 0) |
| 17 | `(?<=fo{1,3})bar` → `obar` at −1 (§5.6, §5.2's "variable lookaround's fixed part") | `rb_rep_split_val` describes a split repeat as `pcrec_pd_none()` (req.c:905-914, C-R8), so the body's description walls and there is no BEHIND item | `bar` at L3 (a sound loss; the census counts it; [REPEAT-RUN] R2 lifts the head wall, not the description's) |

### 14.2 Today at T, and the predicted values (C-R2)

Measured with the main tree's `build/pcrec -p rx --features all --emit-facts --pattern P` (C-R2); "L1" and
"L3/L2" are hand-derived from §14.3's rules. Run values are `req_whole_run`'s; K is `req_landmark_maxoff`.

`[REV 3.4, lane l3r65, review r65 A/J/K]` Every "L3:" cell below is the run under `--engine=vm` (or `-fno-req-handoff`), where
no forward scan re-enters. By default the pick rule (§14.4 L3's REV 3.4 addendum) keeps the "today" run wherever the consumed part
has one at a bounded K: `(?<=foo)bar`, `(?<=ab|b)c`, `(?<=ab)ab[a-z]*q`, `(?<=qz)ab`, `(?<=e{10})eeeeeqzx`, `(?<=foo)bar(\w)\1`,
`(?<=foo)bar(?=baz)` and W-D2 `(?<=ab)(?<=cb)c` list their "today" values on the default route. UNPREDICTED MOVERS the table
did not carry, recorded (review r65): W-D2 `(?<=ab)(?<=cb)c` gains BACK's `bc` at −1 with an EMITTED pre-check (`"-1"`), why still
`dead`, answers unchanged (K: under `--engine=vm` only since REV 3.4); `(?<=xyz)a+xyz` moves `RX_REQ_BYTE` 122 → 97 (J: the
BACK run `xyza` at −3 has the one-byte consumed extent `a`; kept on the default route too, its consumed best `xyz` being
unbounded; measured not slower, 0.33-0.82).

| pattern | today at T (run; K; `RX_REQ_WHY`; `RX_REQ_HANDOFF`) | L1 (reach 0) | L3 / L2 (full reach) |
|---|---|---|---|
| `(?<=foo)bar` | `626172`; 0; dominated; none | same | L3: `foobar`, K −3 |
| `bar(?=baz)` | `626172`; 0; dominated; none | same | L2: `barbaz`, K 0, consumed `[0,3)` |
| `xyz(?<=yz)abc` | `78797a616263` (E2); 0; emitted; 0 | same (the `lg` `yz` meets `xyz`'s tail) | same |
| `a(?=b)[bc]` (`A_CTX`) | none; 0; dominated; none (`cover`); `req_set` 97, `req_byte` 97 | `ab` (listing only: `cover`); `[REV 3.1, review r51 READYL1-5]` `req_set` gains 98, `req_byte` 97→98 (an EMITTED stamp, `RX_REQ_BYTE`) | same |
| `xy(?=bc)[bc]c` | `78796263/fffffeff` (`xy[bc]c`, E2); 0; emitted; 0; `req_set` 99,120,121, `req_byte` 120 | `xybc`; `[REV 3.1, review r51 READYL1-5]` `req_set` gains 98 | same |
| `foo(?=bar)baz` | `666f6f62617a` (E2); 0; dominated; none; `never_matches` no | `foobaz`, why `dead` | same |
| `(?<=ab)(?<=cb)c` | none; 0; dominated | none, why `dead` (guard against guard at −2) | same |
| `ab[xy][xy](?=(?<=xx)y)[xy]` | `6162787878/fffffefefe`; 0; emitted; 0; `req_set` 97,98, `req_byte` 98 | `abxxy`; `[REV 3.1, review r51 READYL1-5]` `req_set` gains 120, 121; `req_byte` 98→120 (`RX_REQ_BYTE`) | same |
| `[ac][ac]cc(?<=acc)(?<=cc)d` | `6161636364/fdfdffffff`; 0; emitted; 0; `req_set` 99,100, `req_byte` 99 | `[ac]accd`; `[REV 3.1, review r51 READYL1-5]` `req_set` gains 97 | same |
| `xy[ac]b(?:(?<=ab)b\|c)` | `7879616262/fffffdfffe` (E2); 0; emitted; 0 | same (ALT drops the one-branch guard) | same |
| `x(?=qr)[pq]r` | `787072/fffeff`; `req_set` 114,120; `req_byte` 120 | `xqr`; `req_set` gains 113 (the TOP set step); `[REV 3.1, review r51 READYL1-5]` `req_byte` 120→113 (`RX_REQ_BYTE`) | same |
| `x(?=ab\|ac)a.` | `7861`; 0 | same (`.` is a gap) | same |
| `(?<=ab\|b)c` | none; 0; dominated | none | L3: `bc`, K −1 |
| `(?<=fo{1,3})bar` | `626172`; 0 | same | same (item 17 of §14.1) |
| `(?<=ab)ab[a-z]*q` | `6162`; 0; dominated | same | L3: `abab`, K −2 |
| `(?<=qz)ab` | `6162`; `req_byte` 98 | same | L3: `qzab`, K −2; `req_byte` stays 97 or 98 (consumed extent `[2,4)`) |
| `(?<=e{10})eeeeeqzx` | `6565656565717a78`; 0; emitted; 0 | same | L3: `e^15 qzx`, K −10 |
| `(?<=foo)bar(\w)\1` | `626172[\w]`; 0; emitted; `"0"` (VM, `RX_VM_PREFILTER "none"`) | same | L3: `foobar[\w]`, K −3, `RX_REQ_HANDOFF "-3"` |
| `[a-z]?[a-z]a(?=bc)` | none; K 2 (the byte's); emitted; 2 | same | L2: ~~`abc` at `maxoff` 2~~ `[REV 3.1, review r51 READYL2-3]` `[a-z]abc`, K 1, consumed `[0, 2)`: a 26-member position is a run position since [RUN-POS-SET], so the walk's tail is `[a-z]a` and the AHEAD candidate is `[a-z]a ++ bc` at `rn_tail_off(3, 2)` = 1 (the spelled `[a-z]?[a-z]abc` reads `[61-7a]616263`, K 1, at B) |
| `y*(?:ab(?<=xab)c)` | `616263`; unbounded | same (`x` dropped at `y*`) | same |
| `foo(?!x)bar`, `x(?!ab)ac` | `666f6f626172`, `786163` (E2, negative = width-0 unit) | same | same |
| `(?<=foo)bar(?=baz)` `[REV 3.1, review r51 READYL2-5]` | `626172`; 0; dominated; `run_pin` 0 | same | L3: `foobar`, K −3 (BACK only: L3 ships no run past the consumed end); L2: `foobarbaz` at −3, consumed `[3,6)` (the BACK row's `++ rg` clause, L2's) |
| `(?<=foobar)\d*x` `[REV 3.1, review r51 READYL3-6]` | (not measured at T) | same | L3: BACK `foobar` at −6 beats the default `x`; its consumed extent is EMPTY (`head.n` = 0): no run pick, `req_byte` the set's (120), the pin states nothing (D-6) |
| `(?<=foo)` `[REV 3.1, review r51 READYL3-6]` | (not measured at T) | same | L3: `foo` at −3 (`all`), consumed extent empty: `req_byte` none, pin none; matches (3,3) on `foo` (oracle `M 3 3`) |
| `(?<=a{32})b` `[REV 3.1, review r51 READYL3-6]` | (not measured at T) | same | L3: `lg ++ head` clipped at the stored bound 32 keeps `lg` only: consumed extent empty, as the row above |

### 14.3 The design step's decisions (the note's D-1..D-16, each answered)

**D-1, the ITEM row and the body walk (sites 1, 2).** T3 keeps its one dispatch: `rb_walk_at`'s `case
A_LOOK`/`case A_CTX` reach `rb_row_into` → `rb_zero_into` as today; no `A_LOOK` arm is added beside it. L1
changes two things there: (1) `rb_row_into`/`rb_zero_into` take the walk mutable and this level's two child
slots `t` (`rb_walk_at` already holds them), because the ITEM action walks a lookaround body with
`rb_walk(w, a->l, &t[0])`; (2) `rb_zero_rows` gains one row, placed BEFORE today's E-5 row:

| T3 row (first match) | when | action | arm (restored → passed over) |
|---|---|---|---|
| E-1 | `A_EMPTY` | the unit, described as the empty string | `empty` |
| E-1 restored | `A_EMPTY` | the cut | — |
| **E-5i (L1, new)** | `rb_zero_look_pos` (`A_LOOK` positive, `A_CTX` NEXT/PREV) | the unit carrying the item's guards, the body's guards and the body's never bit (T4 ITEM, §5.1) | `look` \| `zero` (`look` new, walk_arms.def) `[REV 3.1, review r51 READYL1-1]` |
| E-5 | `rb_zero_look_pos` | the plain unit (E2's), `pcrec_pd_zero()` | `zero` |
| E-4 | every zero-width node | the plain unit | `zero` |
| default | — | the cut | — |

Under the `look` arm E-5i is passed over and E-5 answers, which is §5.8's "restores E-5 as E2's plain unit"
by the table's own arm column. `[REV 3.1, review r51 READYL1-1: E-5i carries `PCREC_WALK_ARM(LOOK) |
PCREC_WALK_ARM(ZERO)`, so `--harness=restore=zero` passes over it too and `zero` keeps E2's shipped meaning (a
lookaround of either lowering back to the old CUT). With `look` alone, restore=zero would still answer E-5i:
run_facts_checks.sh's [facts-arm] ZP expectation (`xyz(?<=yz)ab\Bcd` → `78797a harness:zero`) would read
`78797a6162` and go red, and five readers of `zero`'s meaning (walk_arms.def's `zero` row comment, facts_listing
§4.1.3¶4a's `zero` text, run_axes.sh's comment, req.c's T3 header, that check) would turn false. With the mask
every one stays true; `look` alone still isolates L1 (§5.8).]`
`[REV 3.2, conf-spanarms8 D1: the mask has a consequence the five readers did not name. Passing over E-5i under `zero` also
moves `req_set` and `req_set_maxoff`, for the very reason READYL1-2 gives for `look`: the TOP set step writes the walk's SET
outputs from the item's guards, and a cut lookaround carries none. CHOICE: form (a), the ZERO row of walk_arms.def gains
`PF_REQ_SET` and `PF_REQ_SET_MAXOFF` at L1, `(1u << PF_REQ_WHOLE_RUN) | (1u << PF_REQ_PIECES) | (1u << PF_REQ_SET) |
(1u << PF_REQ_SET_MAXOFF)`, so `zero`'s tokens appear on those two facts too and `[facts-arm]` gains their expectations
(`harness:zero` on `req_set`/`req_set_maxoff` of a lookaround pattern the TOP set step moves). WHY (a): the code makes
it true (walk_arms.def's rule is "the walk OUTPUTS the arm can change", and under restore=zero these two outputs
change at L1, none before it); form (b), splitting the arm so `zero` keeps its fact set, would un-do READYL1-1's own
reasoning (the mask exists so that `zero` keeps E2's shipped meaning, a lookaround cut) by leaving `zero` without the
token on a fact it moves. Readers moved with it: D-13's L1 row (below) and §14.4 L1's Feature bullet.]`
What leaves the body: ONLY the item (§D-10), the body's own `lg`/`rg` and its
never bit. The body's set, description and consumed runs stay in `t[0]` and are never joined into `acc`
(the action calls `rb_zero_unit_into(w, acc, pcrec_pd_zero())` `[REV 3.3, review r55 TABLE-4 (b): as built it
re-spells that function's two lines in `rb_zero_item_into`; §14.8 item 6]`, so the parent's description is E2's,
unchanged). An `A_CTX` NEXT/PREV item is its node's set at offset 0/−1; it walks no body.

**D-2, where the guards and the never bit live (site 3).** In `RbRuns`: `RbRun lg, rg; bool never;` beside
`best/head/tail/all/maxw`. Reason: every combinator that must meet or carry them is an `RbRuns` operation
(`rr_cat`, `rr_alt`, and `rr_pow`'s and `rr_rep_split`'s copies, which never see an `RbVal`). Stored bound:
`PCREC_MAX_REQ_RUN_SCAN` positions each; `lg` keeps its LAST positions (`rn_pre`), `rg` its FIRST (`rn_app`),
§2's rule unchanged. So RM-1's `RbRuns` half applies (§14.4 L1).

**D-3, T4's spelling (sites 4, 5).** CAT-R, CAT-L and CAT-EDGE are FIXED STEPS of `rr_cat` in that order,
not alternatives; each has at most two cases, so none is a table (the house rule's threshold is more than
two). `[REV 3.1, review r51 CONFORM-2: so T4 is no longer "a NEW declared table" (the note's site 4 class); the
one new declared table of L1-L3 is TOP (D-4), and it is a COMBINING table, which req.c's `RB_ROW_SCAN` cannot
walk (it leaves the index of the FIRST row whose test holds and breaks). The note's basis for NOT carrying
register row 19 ("T4 and TOP ... use req.c's existing `RB_ROW_SCAN` and add no walker") therefore no longer
holds; D-4 names the walker and row 19's event.]` They share ONE meet primitive, `rn_meet(w, a, b, off, &empty)` (position-wise intersection at equal
subject offsets, EMPTY-MEET's rule inside it: an empty consumed position keeps its un-narrowed value, an
empty guard position is dropped with everything outward of it, and `empty` is reported). The steps:

| step (in order, every `rr_cat`) | reads | writes |
|---|---|---|
| CAT-R | `l.rg`, `r.head` (and `r.tail`/`r.best` where `r.all`) | the narrowed `r` positions; the leftover of `l.rg` past `r.head.n` |
| CAT-L | `r.lg`, `l.tail` (and `l.head`/`l.best` where `l.all`) | the narrowed `l` positions; the leftover of `r.lg` before `l.tail.n` |
| the consumed join (today's `rr_cat` body, unchanged) | the narrowed values | `o.best/head/tail/all/maxw` |
| CAT-EDGE | the two leftovers | `o.lg` = `l.lg` met with `r.lg`'s leftover shifted by `l.maxw` where `l.all`, else `l.lg` (leftover dropped); `o.rg` its mirror |
| never | `l.never`, `r.never`, any `empty` | `o.never` by the never rows (D-9) |

ALT's guard rule is ONE post-step of `rr_alt` after its row scan (both `rr_alt_union` and `rr_alt_affix`
answer the consumed part; neither touches guards): `o.lg = rn_common_tail(l.lg, r.lg)`, `o.rg =
rn_common_head(l.rg, r.rg)`, the existing primitives (site 5: no second spelling of the union). REP: through
`rr_cat` per copy; the two one-field copies get their writes (`rr_rep_split`: `o.rg` from the same
`rr_cat(w, gap, p)` call as `o.tail`; `rb_rep_best_val` is a restored form and carries no guard; `[REV 3.1,
review r51 READYL1-8 (a)]` it DOES copy the body's `never`, so D-9's "REP, `m >= 1`: the body never" holds under
`--harness=restore=rep` too, and `(?:foo(?=bar)baz)+` lists dead under that arm as by default). The `look`
arm's restore semantics: E-5i passed over (D-1) and TOP's candidate rows passed over (D-4); no T4 step reads
the arm (with no item no guard exists, so the steps are inert).

**CAT-SET, re-spelled** `[REV 3: replaces §5.2's CAT-SET row]` `[REV 3.3, review r55 A, TABLE-4 (a): SUPERSEDED as
built: CAT-SET is back in `rr_cat` as first written, choice-free, and DOES set an empty set's pick; §14.8 item 1]`. At the walk's exit, after TOP: every
CONSUMED position of the chosen run that is ONE byte joins the necessary set at its offset (~~the run's
`whole_maxoff` plus its index~~ `[REV 3.1, review r51 READYL1-7: `run.off + i`, on the walk's own `RbRun`,
saturating to `RB_OFF_UNBOUNDED` as `rb_union` does, BEFORE the run floor. `whole_maxoff` is `ReqRun`'s, written
later in facts.c and 0 below the floor, so read literally a below-floor run such as `(?=q)[pq]` would join at
offset `0 + i` whatever its true bound: an under-stated `req_set_maxoff`]`), if the set lacks it. `RbSet.pick`
(the threaded rightmost) is NOT updated by the step: sound, since a joined byte is a necessary byte at its offset
and the pick stays a member; stated because `pcrec_find_set_pick` falls back to it under NONE. Without guards it is a no-op (every exact consumed
position already came from a single-byte class, an ALT union both branches carry, or a copy of a body whose
set the repeat keeps: req.c's `pcrec_req_pick` comment "every value here stays a member of `req_set`"), so it
moves only where a meet narrowed a position; and it reaches a narrowing inside a repeat's copies, which
`rr_cat`'s step could not. W-S4 is unchanged.

**D-4, TOP (sites 7, 8, 9).** TOP is a stage at the one walk exit (`pcrec_req_walk`, after `rb_walk`), a
DECLARED ROW TABLE of candidates with an arm column; it is walked IN FULL (every row whose arm is not
restored and whose `when` holds contributes a candidate), a combining table, not first-match:

| TOP row | when | candidate | its consumed extent | arm | built by |
|---|---|---|---|---|---|
| BACK | `lg.n > 0` and `lg.n <= lb_bytes` | `lg ++ head` at offset `−lg.n` (L3); where `all`, `lg ++ head ++ rg` (L2 adds this clause) `[REV 3.1, review r51 READYL2-5]` | `[lg.n, lg.n + head.n)`, which may be EMPTY (D-6) `[REV 3.1, review r51 READYL3-6]` | `look` | L3; its `++ rg` clause L2 |
| AHEAD | `rg.n > 0` | `tail ++ rg` at `rn_tail_off(maxw, tail.n)`; where `all`, `head ++ rg` at 0 | `[0, tail.n)` / `[0, head.n)` | `look` | L2 |
| default | — | the consumed `best`, extent `[0, n)` | — | — | today |

Each `++` keeps the FIRST positions (`rn_app`), and an extent is clipped at the stored bound. The run is
the best of the default and the candidates by the ONE run choice (`rn_choice_rows`); to keep each
candidate's extent beside it, `rn_better`'s row scan is split into a comparator `rn_cmp` (the sign) that
`rn_better` and TOP both call: a byte-identical split that lands ~~with L3's feature commit~~ `[REV 3.1, review r51
READYL3-7 / CONFORM-3: as L3's REMODEL commit 5, its own commit so its byte identity is gated alone (§14.4 L3);
it is not part of the note's RM-4, whose anchor ranges never covered it; its binding: S474 (anchored on the very
`RB_ROW_SCAN(i, w, rn_choice_rows,` line the split moves) re-aimed at `rn_cmp` and shown red there, S1930 (the
choice table's rows) checked, the anchor map gaining req.c's `rn_better` range]`.
`[REV 3.1, review r51 READYL2-5]` The BACK row's `++ rg` clause belongs to L2: at L3 a BACK candidate never
reaches past the consumed end, so D191.1's gating of L2 ("L2 after ... one readiness critic") stays literal and
`(?<=foo)bar(?=baz)` moves at L2 (to `foobarbaz` at −3, consumed `[3,6)`), not at L3.
`[REV 3.1, review r51 CONFORM-2]` TOP is walked by an ALL-ROWS sibling of `RB_ROW_SCAN` beside it in req.c
(`RB_ROW_EACH(i, w, TAB, TEST)`: the same arm filter, every row whose test holds, no `break`), not by a loop of
its own. Register row 19's event, "the next new declared table", FIRES at TOP's landing (L1, with no rows; its
first row at L3). `[REV 3.2, conf-spanarms8 (register proposal), RULED]` Register row 19's status, ENTERED 2026-11-18: "open;
event fired by span_arms L1's `RB_ROW_EACH` (an all-rows walker, not the first-row one)" (row 19 is a FIRST-row walker, so
`RB_ROW_EACH` is a further local walker, not an instance of it; whether the row also absorbs `RB_ROW_SCAN`, the note's F-6,
stays the manager's). `reach` is NOT a
walk parameter (§14.1 item 8): at L1 the table has no rows, so TOP is "guards dropped". `lb_bytes` IS a walk
parameter row (`ReqWalkParams.lb_bytes`, filled in `pf_derive_req_walk` from RM-5's accessor, D-11), read
only by the BACK row.

`rn_scan_mass` ranks over EVERY run position, and its comment changes from "the same estimate the
`req_byte` pick reads" to "the scan the kit may place on any run position (D191.2)": the ranking estimates
what the search will scan, which D191.2 gives to the kit over the whole run; `req_byte` reads the consumed
extent from L2/L3 on (D-6), so the two diverge exactly there, and the comment must say which it follows.
No byte moves at T (every run's extent is the whole run).

**D-5, where `omin` and the consumed extent live (site 10).** NOT on `RbRun` (no `rn_*` constructor
becomes a writer). The walk's OUTPUT carries the chosen run's consumed extent (a `ReqWalkOut`-style result
beside `*run`, or two out-parameters: the build's spelling), and `ReqRun` gains `cons_lo, cons_hi`
(positions; `[0, whole_len)` for every run without a candidate). `omin` is not stored (D-7). The new fields
are declared part of facts.h's interface where they are added, with the accessor (D-6) as their one
spelling for gen. Both `ReqRun` writers (facts.c:97-100, :253-262) start from RM-1's stated empty value.
`[REV 3.1, review r51 READYL1-8 (b)]` RM-1's `ReqRun` half has no reader at L1 (the extent lands at L3). It still
rides L1, as one commit with the `RbRuns` half, because register row 23 names RM-1 whole as L1's ("[REQ-LOOKAROUND]
L1 (unit RM-1 ...)") and its subject is every record builder of the run path, not a field; it is answer- and
byte-identical, so riding early costs no mover (D77 is about building ahead of a NEED; this builds nothing new).
The clause "the facts.c writers' anchors by the anchor map" binds NOTHING: the map over facts.c 86-110 and
235-280 finds 0 sabotage anchors (r51 READYL1); the commit's facts-stream gate is its only control there.

**D-6, the scan member and the consumed extent (sites 18, 19).** Two questions, one primitive:
`pcrec_find_run_scan_index(rate, pos, n)` (findings.c:757) already IS the one pick over a stretch of
positions. What is duplicated is the WHOLE-RUN call spelled three times (req.c:423 on an `RbRun`, req.c:1284
and emit_dfa.c:11345 on a `ReqRun`). RM-4: ONE facts accessor `pcrec_run_scan_index(rate, run, lo, hi)`
(req.c beside `pcrec_req_pick`, declared facts.h), the pick over `run->pos[lo..hi)` returned as a run index;
req.c:1284 and emit_dfa.c:11345 call it with `[0, whole_len)` (byte-identical). At L3 `pcrec_req_pick` calls
it over the CONSUMED extent (`pcrec_run_cons(run, &lo, &hi)`, the consumed-extent accessor, landing with L3),
so `req_byte` stays "a byte every match consumes" (D191.2). `[REV 3.1, review r51 READYL3-6]` AN EMPTY
CONSUMED EXTENT (`lo == hi`: a BACK run with `head.n = 0`, such as `(?<=foobar)\d*x` or `(?<=foo)`, or one whose
`lg` fills the stored bound, `(?<=a{32})b`) HAS NO RUN PICK: the accessor returns none at `lo == hi` and never
calls `pcrec_find_run_scan_index` with `n = 0` (that call reads an uninitialised `cand[0]` in
`pcrec_find_pos_pick` and returns index −1, `lo − 1`, a lookbehind byte: UB in the compiler and a `req_byte` no
match consumes); `pcrec_req_pick` then falls to the set's pick exactly as for a pattern with no run (or none),
and the run pin states nothing. The BACK row keeps such a candidate (no `head.n > 0` clause): a lookbehind-only
run is a valid presence fact, and the clipped case `(?<=a{32})b` has `head.n = 1` and an empty extent all the
same, so only the extent rule covers both. The trace shadow `req_set_leads_own` KEEPS the
whole run: it predicts the kit's P4, which scans any run position (`[REV 3.1, review r51 READYL3-9 (4)]` so its
comment's "pcrec's own pick (`req_byte`'s derivation ...)" at emit_dfa.c:11342-11343 is restated at L3: from L3 on
the shadow and `req_byte` are two derivations, the whole run and the consumed extent); it is not "the pcrec/kit agreement check"
D191.2 retired (that was `req_run_member`'s internal error, gone at K38-2, §14.1 item 3).
`pcrec_run_pin` and its gen readers (site 19) read the consumed extent through the same accessor at L3:
the pin's pick and stretch lie inside it, and `walk_proves`' `d >= 0` refusal keeps the R span consumed.

**D-7, K's state (site 12).** K (`req_landmark_maxoff`, and `req_handoff_k`'s whole-run branch) becomes a
stated value with a state, `{ PF_OFF_NONE, PF_OFF_BOUNDED, PF_OFF_UNBOUNDED }` plus a signed `long long`;
`PF_OFF_UNBOUNDED` keeps `PCREC_W_UNBOUNDED` in the value so every printed byte is today's. One predicate
per question: "is K stated and bounded" (the hand tests :8990, :9360, facts.c:356, :869 and the emitters'
:1099, :7926, :7961) and "is K stated" (none: facts.c:106, :355, emit_dfa.c:9174's `-1`, the printer's
`< 0 → none` at facts.c:868). `req_site_define` maps `PF_OFF_UNBOUNDED` onto `MF_HEAD_MAX_UNBOUNDED` at its
one writer (:1644). K ALONE carries the state: `omin` is a FUNCTION of K, `pcrec_run_omin(run) = min(0,
whole_maxoff)`, because every candidate TOP builds has either `omin = maxoff = −t` (BACK: `head` sits at 0)
or `omin = 0 <= maxoff` (default, AHEAD), so storing the interval would state one fact twice. `[REV 3.1, review
r51 CONFORM-8: "one fact twice" holds of the SOUND UNDER-ESTIMATE pcrec states, not of the true interval (`x.?bcd`:
true [1, 2], `min(0, K)` = 0); site 11's row and the true interval are DEFERRED to [PRES-OMIN-TRUE], §14.1 item 5.]`
`[REV 3.1, review r51 CONFORM-12]` The state type is NAMED FOR THE FAMILY, not for K: `PfBound` (owned by
facts.h; states `NONE`, `BOUNDED`, `UNBOUNDED` and a signed value; `PF_OFF_*` above read as its states), with K
its ONLY user at L3, so the offset-bound family's second member (register row 24) joins it without a rename. Its
general form (a `NEVER` state separating today's `PCREC_W_UNBOUNDED == PCREC_MINW_MAX` pun, and a signed `[lo,
hi]`) is §10's U-bound, on its own trigger; nothing of it is built here. The rest of
the offset-bound family (`RbSet.off`, `ReqSet.maxoff`, `ReqRun.whole_maxoff`'s `whole_len < 2` none) keeps its
encodings to its own next touch (P2's row).

| K's state | the move emitters | `head_max` | `<PREFIX>_REQ_HANDOFF` | listing |
|---|---|---|---|---|
| none | not reached (no handoff row applies) | 0 (no ASSIGN) | `none` | `none` |
| unbounded | the `[REQ-PAST-LAST]` branch (no move) | `MF_HEAD_MAX_UNBOUNDED` | as today | `unbounded`, `decline:unbounded` |
| bounded, `K >= 0` | today's text, byte-identical | K | K | K |
| bounded, `K < 0` (L3) | the signed form (D-8) | K | K (`"-3"`) | K (`-3`) |

**D-8, RM-3's shape, and acting through the row (sites 12, 15).** The one emitter takes `(hit, pos,
target, K)` and prints the condition and the assignment; the target-is-the-hit rule replaces a mode: where
`target` IS `hit` (the entry, `handoff_position`) it prints `target -= K` (nothing at K = 0), else
`target = hit - K` (`target = hit` at K = 0). Every other difference stays in its caller (the note's list):
(1) the entry's `if (k > 0 || round.len > 0)` guard (`[REV 3.1, review r51 READYL3-1]` kept in the caller, but spelled `k != 0 || round.len > 0` at L3 so the K < 0 row always emits: the table's guard column), (3) its `else`, (4) the re-entry's reseed splice, (5)
both unbounded branches, the re-ask block, and the two `ROUNDUP` calls. Plants: S470 keys on the in-place
branch and S809 on the assign branch of the one emitter, so per-caller detection survives; S471, S814,
S1701 stay per caller with their calls.
The emitters RE-TEST K's state through D-7's one predicate rather than acting through a start row: the
entry text serves the DFA scan, the hybrid prefilter and the VM attempt loop, each chosen by a different
table, and only the attempt loop's rows (`handoff-attempts-entry`/`-unbounded`) decide boundedness; the
state is K's, and the rows' predicates read the same predicate.
L3's signed form, first match on K's state `[REV 3.1, review r51 READYL3-1, READYL3-4: the entry guard is stated
PER ROW (new column); the K < 0 cells gain the end clamp, and their "cannot pass the subject's end" claim is
withdrawn]`:

| K | the entry's guard (is the move block emitted) | entry (`hit` = `target` = `handoff_position`) | re-entry (`hit` = `landmark_position`) |
|---|---|---|---|
| unbounded | today's | today's | today's |
| `K >= 0` | today's `k > 0 \|\| round.len > 0` (under `byte` at K = 0: no block, today's bytes) | today's text (`hit >= pos` holds: `omin = 0`, so the kit's floor is `pos`) | today's re-ask `landmark_position < pos`, today's move |
| `K < 0`, `B = −K` | ALWAYS emitted: the guard is spelled `k != 0 \|\| round.len > 0`, byte-identical at `K >= 0` | `if (n - hit < B)` the miss path (no attempt can start inside the subject: NOMATCH, the pre-check miss's own exit); else `if (hit >= pos \|\| pos - hit < B) hit += B; else hit = pos;` (no subtraction that can wrap) | the re-ask condition becomes "the kept hit is stale": `landmark_position < pos && pos - landmark_position > B` (today's `landmark_position < pos` at `K >= 0`); then `if (n - landmark_position < B)` the miss path; else `if (landmark_position >= pos \|\| pos - landmark_position < B) pos = landmark_position + B;`. A re-asked hit lies at or after `max(0, pos − B)` (the kit's floor), so it is never stale and the re-ask cannot repeat (W-L14) |

`[REV 3.1, review r51 READYL3-1]` WHY THE GUARD IS PER ROW. Rev 3 kept the entry's `if (k > 0 || round.len > 0)`
in the caller (difference (1)), so under `byte` at K < 0 the whole block, the new `hit += B` included, was NOT
emitted and the attempt began at the raw hit, up to B bytes before the start offset. ANSWER WITNESS, with its run
(r51 READYL3, the D-8 model executed literally, against libpcre2-8): `(?<=a)a(\w)\1` (L3 run `aa[\w]` by the BACK
row, K −1, `omin` −1, B 1) on `-aaaaaq-b` searched from 3: kit floor 2, hit 2; with the guard KEPT no move is
emitted and the attempt at 2 answers (2,5); the oracle answers (3,6); with the guard per row (the K < 0 row
always emits) the move gives `hit = 3` and (3,6). Over 1857 starts (subjects to 22 bytes) the kept guard gives 22
wrong answers, the per-row guard 0. A run that cannot recur within B bytes (`(?<=foo)bar`, `e{10}`) hides it, so
this witness (a self-overlapping lookbehind run, period below B + 1) is L3's, with a guard plant (§14.4 L3).
`[REV 3.1, review r51 READYL3-4]` WHY THE CLAMP. Rev 3 said "`hit + B` cannot pass the subject's end, since `B` is
the run's lookbehind prefix and the occurrence at `hit` holds the whole run". That is false on the DFA-scan and
hybrid routes: there the candidate guarantees only the stretch the kit VERIFIES (tuning §2.41¶1: "`c` holds the
stretch of the run the pre-check verifies"; at B a 27-position run emits `if (cand + 21 >= n) return n;` and
verifies 8 positions), and D191.2 lets the kit place that stretch anywhere on the run, the lookbehind prefix
`[0, B)` included. A candidate whose verified stretch ends before index `B − 1` near the subject's end gives
`hit + B > n`: a start past the end, and the DFA reseed's `subject[pos − 1]` read one past it. The answer there is
NOMATCH either way (no match starts past `n`), so the clamp moves no answer; it states the bound pcrec owns
rather than asking the kit for one (nothing is asked of the kit by L1-L3, §14.1 item 2). The VM attempt loop
verifies the whole run (p4.c's `rx_reqrun`) and is unaffected; the clamp is emitted on every K < 0 row alike.
`[REV 3.4, review r65 F]` MEASURED: the read past the end does not happen on the built tree. A downstream guard
(`if (search_from > subject_length) return 0`) answers first on every route, so removing the clamp moves no answer and
reads nothing past `n` (S3407: 0 red on spanarms.rxt, 0 wrong starts on 4 routes). The clamp is DEFENCE IN DEPTH,
kept (one compare); W-L16 is a planted record, UNDETECTED by construction.
`[REV 3.1, review r51 CONFORM-14]` These K-sign rows (unbounded / `K >= 0` / `K < 0`, per caller, with the guard
column) are A-POSDOM's INPUT: its declared table takes them as rows when it lands, and they are not grown further
here.
`[REV 3.1, review r51, the manager's ruling on the spanarms7 report's F-7: ACCEPTED as a NOTED DEVIATION]` The
emitters re-testing K's state through one predicate instead of acting through a start-table row is a noted
deviation. `[REV 3.2, conf-spanarms8 (register proposal), RULED]` ENTERED 2026-11-18 as register row 30, in the register's own columns and wording (status "noted, lands with L3": the code does not exist yet; the table below is the proposal it was entered from):

| # | remodel | shape (rule) | where | event that carries it | size, gate | deletes | status |
|---|---|---|---|---|---|---|---|
| (next) | NOTED DEVIATION: the landmark-move emitters re-test K's state through one predicate (D-7's) instead of acting through a start-table row; the entry text serves the DFA scan, the hybrid prefilter and the VM attempt loop, chosen by three different tables | Act through the row | `emit_req_handoff_rest` (the entry) and `pf_emit_handoff` / `emit_req_landmark_move` (the re-entry), emit_dfa.c | the A-POSDOM table's landing (D191.3: "L3 builds now, ahead of A-POSDOM, its two sites in that table's shape") | small (one site, no new reader of another unit's structure, no seam changed) | the deviation itself | noted at L3's landing (proposed), until corrected at A-POSDOM |

The "cannot underflow" premise moves into the one emitter at RM-3 and is restated per row at L3. The miss
value (the gate's subject length) reaches no move: an ALL_PRESENT pre-check's miss is NOMATCH before it
(the build re-reads the gate text and says so in its report).

**D-9, the never propagation (site 21).** Answer (a): ONE propagation, taken from a primitive shared with
derive.c's prune. derive.c's PRUNE rules (its header: "a `CAT` with a never item is never; an `ALT` drops
never arms; `REP{m>=1}` of never is never and `REP{0,...}` of never is EMPTY; a positive `LOOK` of never is
never, a negative one EMPTY") are inline in `q_cat`/`q_alt`/... today. ~~L1's first remodel commit extracts
them as a declared row table in the AST's own area (beside the kind rows~~ `[REV 3.1, review r51 CONFORM-10,
CONFORM-6, RULING-1]` L1's remodel commit RM-6 (after RM-1; §14.0, §14.4) extracts them as a NEVER COLUMN of
`src/core/kindrow.def` ("THE PER-KIND ATTRIBUTE ROW: one row per `AKind`, the kind-level facts every pass family
reads"; register row 5, "Kind defaults as a kindrow.def column, per pass"), NOT a new table beside the kind rows,
which would restate the kind list (row 5's "deletes: restated leaf lists"). Column values: `ANY` (CAT: any item
never), `EVERY` (ALT: every arm), `BODY` (positive LOOK, group, atomic: the body), `NO` (negative LOOK: never
not), `NODE` (the answer depends on the node: REP by `m`, the class leaf by its set). By kindrow.def's own rule
("An answer that depends on the node ... keeps its code in the reader and reads the row for the kind-level
part"), the `NODE` parts stay in each reader: derive.c keeps `is_never_leaf` and REP's `m` split; the run walk
tests its own rendered set's emptiness (`rn_count(ps) == 0` in `rb_class_into`'s out-of-domain branch: the same
leaf, "no byte can match here", read at the byte level after lowering, where derive.c reads the class before it)
and its empty meet. The home follows the owner's words, 2026-11-18 (the plan row body ARCH-STEP.md, "HIS
WORDS"): "looking for functionality wholly dependent on eg the AST, can be built in the AST area" (rev 3 quoted
the record's restatement, "can be built in that structure's own area", as his; corrected). Read by derive.c's
`q_*` (byte-identical: the derivation's own group-keep rule stays derive.c's) and by `rr_cat`/`rr_alt`/T2/E-5i
for the walk's `never`. The rows below are the column's values per combinator:

| never row (first match on the combinator) | never iff |
|---|---|
| leaf: the empty class (`is_never_leaf`) | always |
| leaf: an empty meet (the run walk's, D-3) | always |
| CAT | any item never |
| ALT | every arm never |
| REP, `m >= 1` | the body never |
| REP, `m = 0` | never not (EMPTY) |
| LOOK positive | the body never |
| LOOK negative | never not (EMPTY) |
| transparent (group, atomic, lookahead of never) | the body never |

The walk's root `never` is RENDERED as `req_whole_run`'s why `dead` (READY-5's listing, kept: "`dead` >
`harness:` > the existing reasons", one why per run, `dead` on `req_whole_run` only, a dead run is
`derived`, `pf_done_why` takes `dead` and `harness:` out of its `decl` list, `run_facts_checks.sh`'s
status/why pairs gain the two, `dead` is not `decline:dead-start`). It does NOT reach `never_matches` or
compile.c's empty artifact at L1: `never_matches` stays keyed on the final machines, so L1 moves no byte
through it; reading the walk's root as a second source of `never_matches` is [NEVER-MATCH]'s step, whose
trigger "span_arms L1's landing" FIRES at L1 (a scheduling fact for the manager). P6 is therefore not needed.
The empty-class leaf widens `dead` to patterns like `x[^\x00-\xff]y` under `byte` (listing only); the census
lists them apart.
`[REV 3.1, review r51 CONFORM-7]` The never family's other members, one sentence each (A8's one-home rule):
mrl.c's `PCREC_MINW_MAX` saturation ("`minw == PCREC_MINW_MAX` MEANS THE CALLEE MATCHES NOTHING", read by the
`ceiling` row) STAYS a width saturation, not a second never propagation: `minw` is a width, its "matches nothing"
is the saturating arithmetic's by-product, and its rules are a width's (a positive LOOK of a never body has width 0
there but is never in the column); whether mrl.c reads the NEVER column is [NEVER-MATCH]'s question, not L1's.
`PfNever` and the `empty` LOCATE row stay machine-level (above: `never_matches` stays keyed on the final
machines). `[REV 3.1, review r51 READYL1-4]` RM-6's gate gains `tests/codegen/run_cpset_structure.sh`: its `[2b]`
allowlist names `src/opt/derive.c:is_never_leaf` BY FUNCTION and turns a moved or read-less allowed function into
`STALE` (a red). With the column form `is_never_leaf` stays in derive.c (a `NODE` answer), so the allowlist stays
true; the check is in the gate so a build that moves it sees the red at its own commit. RM-6's binding plant is
S899 (`if (it[i].never && !it[i].keeps)` in `q_alt`, the ALT never row, the line the extraction rewrites)
`[REV 3.3, review r53 F2: it is NOT the line RM-6 rewrote; S899 binds the per-arm drop, and the column's own cells
have their rows (§14.8 item 9)]`;
S893, S1189, S1190 (KILL) and S904 (the keep rule) are not moved, checked.

**D-10, the item's form (sites 22, 23): (a) SHARED, no deviation row.** AHEAD reads the head column
(`PdHead`, `pcrec_ph_*`, desc.h's "second column": "the positions every match consumes FIRST"), BEHIND
the body's description (`RbVal.desc`, which keeps the LAST positions). Each half reads the column that keeps
the positions NEAREST the cursor, which is review r50 A17's point. The head column runs over the byte
alphabet the walk already passes (`rb_pd_bytes`); its combinators are unchanged. It is computed for a
subtree exactly when the subtree lies inside a positive lookahead's body (E-5i turns it on for its body
walk): FIRST positions in a right-to-left walk copy up to `max_pos` positions per step (`pcrec_ph_cat`),
which a 20,000-byte literal must not pay. BEHIND's per-offset union across width groups reuses
`pcrec_ph_alt`, the module's one per-offset union: each group, read from its LAST position backwards, IS a
head (of the reversed string), and `ph_alt` over them unites the offsets every group reaches. So the one new
desc.c function is that READER (a group as a reversed head), not a third combinator family; register row 29
(ND-2) is not taken, and row ~~26~~ 27 (P5) `[REV 3.1, review r51 CONFORM-1: row 26 is P4, RM-4's scan member, which L3 carries; a landing that closes "row 26" at L1 would close the wrong row]` is DISCHARGED by L1 (one per-offset-head primitive for the description
and the item). The item is built in the description's own area (desc.c) and called by the walk; nothing is
stored (D77) until a second reader exists. Bounds: `max_pos` positions per half, the nearest ones; a repeat
is a head WALL until R2 (the head's REP arm, §8) and a split repeat walls the description (§14.1 item 17).
`[REV 3.1, review r51 READYL1-6]` WHERE THE HEAD'S PER-KIND RULES LIVE. The combinators (`pcrec_ph_unit/pos/wall/
cat/alt`) are half of a head; the other half is the per-kind rule (a class is a position; EMPTY, EOL, CTX, GSTART,
KRESET, a check callout and a LOOK are a unit read THROUGH; REP, BREF, VAR, CALL and a consuming callout are a
wall), spelled once today, at code-point level, in altnf.c's `anf_head`. L1 does not spell it a second time: the
rule moves into desc.c as ONE per-kind head rule with a position callback (altnf passes the `Ast` node at
code-point level; the run walk passes its byte set; `A_WCLASS`, a wall in `anf_head` and transparent in the
byte-level walk, is the callback's answer, an alphabet fact), read by `anf_head` and by the walk. This is
register row 27's own move ("One per-offset-head primitive for the description and the item ... from the second
caller", event L1), so it rides L1 as an answer- and byte-identical commit before the feature (§14.4 L1 remodel
3). `[REV 3.2, conf-spanarms8 D2]` It IS a remodel commit of L1, numbered "remodel 3" in §14.4 and listed in §14.0 beside RM-1..RM-6 as an L1 remodel outside the RM-n series (the earlier "not a sixth remodel" is withdrawn). Confirmed by the manager 2026-11-18 (conf-spanarms8 D2); it rides the owner's 11-09 build go under the manager's remodel-go reading, which the owner may overrule. Its answer- and byte-identity is a build-lane gate (the remodel commit's own identity check, §14.4 L1 remodel 3). The form chosen is register row 27's (the shared per-kind head rule in desc.c with a position callback), so row 29 (form (b), the noted deviation) is not taken. The walk threads the head as `RbVal.head` (a `PdHead`), written only while E-5i walks a
positive lookahead's body, by every `RbVal` writer: `rb_init`, `rb_cat_into`, `rb_alt_into`, `rb_gap_into` (a class
outside the run's domain is still a POSITION, not a wall, or `(?=a.b)` loses its tail terms), `rb_class_into`,
`rb_assert_into` (a restored cut still reads THROUGH, or a restored arm changes the item), `rb_zero_unit_into`,
the five `rb_rep_*_val` and the kind-row gap. `src/facts/CLAUDE.md`'s line that the head description is read
"only by the alternation owner (`src/opt/altnf.c`); one reader of both is design G-1" moves with L1 (req.c becomes
the second reader).
`[REV 3.1, review r51 CONFORM-9]` WHY THE REP WALL STAYS UNTIL R2. The note's lean to form (a) rested on "a wall
whose trigger has fired" (R1's copies are in the run walk at T). With the per-kind rule now ONE rule read by both
walkers (above), the head's REP arm is that rule's row, and lifting the wall in the run walk alone would split it
again; so the wall is lifted once, for both readers, by [REPEAT-RUN] R2 (§8), and the note's "fired" premise reads
R1's run copies, not the head rule's REP row. The loss is sound and is now COUNTED: R2's trigger census gains the
lookahead bodies with a repeat (`(?=(?:ab){2}c)` yields no AHEAD item at L1/L2), §8's R2 row.
`[REV 3.1, review r51 CONFORM-13]` The BEHIND reader ("a group read as a reversed head") answers the question
[VLOOKBEHIND] stage 2's fixed-tail hoist asks of the description at a node (the positions nearest an edge). Its
general form is ONE desc.c reader of the positions nearest an edge, `pcrec_pd_edge(desc, dir, max_pos)` (FIRST
positions for AHEAD through the head column, LAST for BEHIND through the reversed groups united by `ph_alt`); the
hoist and the item are its two callers, and whichever of [VLOOKBEHIND] stage 2's hoist and L1 builds first, the
second calls the first's reader. This is the cross-reference on span_arms' side; the matching sentence in
`docs/design/vlookbehind.md` is the manager's to place (this lane edits only this note).

**D-11, `lb_bytes` (site 20).** RM-5's accessor answers in CHARACTERS (`lb_max`, PCRE2's `max_lookbehind`);
the walk-parameter filler multiplies by the encoding's widest character in bytes (1 under `byte`, 4 under
`utf8`), the rule §5.5 and ~~the owner's Q4 ("cap = declared lookbehind length", AGREED)~~ `[REV 3.1, review r51
RULING-8: §12b's "Q4" is §13's question 5; the binding words are D191.3's: "the lookbehind step back is capped at
the declared lookbehind length"]` fix. [VLOOKBEHIND]
stage 2 (backreferences inside a lookbehind) does not interact: a body holding a backreference has no
description (`A_BREF` is a wall), so it yields no BACK candidate whatever `lb_max` holds, and `lb_bytes` caps a
cost, not safety (§5.5). If stage 2 changes what `lb_max` means before L3 lands, L3's census re-measures; the
accessor's contract ("the declared lookbehind length, in characters") is what L3 reads.

**D-12, PCRE2 facts (site 16): QUESTIONS for a pcre2-reader (D181), not read here.** (a) In UTF mode, may a
lookbehind read before the start offset, and what bounds how far (the declared `max_lookbehind`, nested
lookbehinds)? §5.5's measurement (`(?<=c(?<=bc)d)e` from 3: match in non-UTF, no match in UTF) stands; the
reason is not known from code, and no design choice depends on it (the BACK row is a sound cost cap either
way). `[REV 3.1, review r51 RULING-10]` (a) is PARTLY answered by `docs/dev/pcre2_notes/lookbehind-invalid-utf.md`
(its step 2: in UTF mode the fixed-length backward step fails "if the pointer is at or before the "start of UTF
checking" pointer"; step 3: the variable-length step stops at the whole subject's start). The question left for
a pcre2-reader, should the manager dispatch it, narrows to: for a VALID UTF subject searched from a start offset
above 0, where is that checking-start pointer placed, and does `max_lookbehind` bound it. (b) Does PCRE2's "last code unit" start optimisation ever take a unit from inside a positive
lookahead? Informative only.

**D-13, the spec hunk list at T (site 28; D80), by section.** Re-derived against the spec at T: E2 owns
match_api §6.3.7¶6 and tuning §2.28¶1's run definition ("every successful attempt contains the run",
§12d); `facts_listing.md` §4.1.2¶8 already lists the run once with K in ¶8b; §4.1.3¶4a (`harness:`) is BUILT.

| unit | changes | checked unchanged |
|---|---|---|
| L1 | `facts_listing.md` §4.1.3¶1 (the order gains `dead` first) and a new ¶ for `dead` (the walk proved no attempt can match; on `req_whole_run` only; status `derived`); `[REV 3.1, review r51 READYL1-2]` `facts_listing.md` §4.1.3¶4a: the arm list gains `look` and its tokens, on `req_whole_run`, `req_set` and `req_set_maxoff` (the TOP set step writes the walk's SET outputs), not `req_pieces` (D-1 keeps the parent's description); `zero`'s CUT text stays true (E-5i's `look \| zero` mask, D-1) `[REV 3.2, conf-spanarms8 D1]` but `zero` gains `req_set` and `req_set_maxoff` in the same ¶ (walk_arms.def's ZERO row gains PF_REQ_SET and PF_REQ_SET_MAXOFF at L1, D-1) | match_api §6.3.7¶4, ¶5, ¶6, ¶7; tuning §2.27¶4, §2.28¶1 (the run's values move, not its definition; the TOP set step keeps ¶4/¶5 true) |
| L3 | match_api §6.3.7¶10 (a negative `<PREFIX>_REQ_HANDOFF`), ¶11 (the least occurrence at or after `max(0, startpos + omin)`, `omin = min(0, K)`; `max(startpos, that − K)` holds for signed K); tuning §2.41¶1, ¶8b (the attempt-loop rows at K of either sign); tuning §2.28¶1 (bit 31 also removes a scan that begins before the start offset); `facts_listing.md` §4.1.2¶8b (`req_landmark_maxoff` may be negative). `[REV 3.1, review r51 READYL3-3 / READYL2-4 / CONFORM-4]` THE RUN'S DEFINITION, BEFORE SIDE (L3 lands before L2, so it owns this side): match_api §6.3.7¶6 (a successful attempt consumes the run "between that position and the end of its match": the run may BEGIN up to the declared lookbehind length, −K bytes, before the attempt start, inside a positive lookbehind; its consumed part is unchanged); tuning §2.28¶1's definition sentence (the same); `facts_listing.md` §4.1.2¶8 ("at or after the attempt start": the run may begin −K bytes before it; "No byte of it lies inside a lookbehind" is dropped); tuning §2.41¶8c's "at or after its attempt start" (the past-last stop's premise restated for a run that begins before the attempt). THE PICK'S STRETCH (READYL2-4 named these in L2's row; they are false from the first unit that gives the consumed extent a value, L3 in this order (D-6: `(?<=qz)ab`'s `req_byte` stays in `ab` while the whole run's least-mass byte may be `q` or `z`); if L2 lands first they move with L2): match_api §6.3.7¶5, tuning §2.27¶4 and §2.28¶7, each "the least-mass exact position of the whole run" → "of the run's consumed positions" | match_api §6.3.7¶4, ¶7 (`req_byte` stays consumed: D-6). `[REV 3.1, review r51 READYL3-9 (5)]` ¶7's `@idx` is the KIT's scan position, which D191.2 lets the kit place on any run position, lookbehind bytes included: ¶7's TEXT is checked unchanged, D-6 is not its reason, and no check tests "`@idx` inside the consumed extent"; `findings.md` §4 |
| L2 | match_api §6.3.7¶6 and tuning §2.28¶1: the AFTER side, the clause "which may extend past the attempt's consumed end" (E2 owns the rest of the sentence, L3 its BEFORE side); `[REV 3.1, review r51 READYL2-4]` `facts_listing.md` §4.1.2¶8's "The run occurs inside every match" (it may extend past the match end); tuning §2.41¶8c's "occurs inside every match" (the stop stays sound: the run still begins at or after the attempt start on an AHEAD run, e.g. `x*foo(?=bar)` with unbounded K); the BACK row's `++ rg` clause (READYL2-5) is covered by the same AFTER-side hunks | ¶4, ¶7, ¶11; `findings.md` §4 (the member row's text is already the kit's, K38-2) |

**D-14, L2 refreshed.** The kit scans any run position (D191.2) and the request §8.2 asked is delivered
(§14.1 item 2): L2's text reads `bar(?=baz)`'s `barbaz` as ONE uncut presence span with `omin` 0, and the
kit may scan its `z`. The consumed extent stays pcrec-internal (`req_byte`, the pin). L2's precondition
"after the kit's delivery of R-38" is MET `[REV 3.1, review r51 RULING-9: for parts A, B and D; Part C is not
required (§14.1 item 2), the manager's reading]`; ~~only its readiness critic remains (D191.1)~~ `[REV 3.1: its
readiness critic is review r51's READYL2 lens, DISCHARGED ON CONDITION (§14.0)]`.

**D-15, the "today" column**: §14.2 (C-R2).

**D-16, the emitted comments that print K (site 16; FINDING: three sites, not one).** emit_dfa.c:1117-1121
("every match begins at most %lld bytes before its whole run"), :7898-7900 ("no match begins more than %lld
bytes before it") and :7965-7967 (the same sentence). At `K < 0` each reads wrongly. L3 prints, at `K < 0`,
"every match begins at least %lld bytes after its whole run" (`B`) at all three, and nothing changes at
`K >= 0`. `[REV 3.4, review r65 O]` Worded "after the START of its whole run" (the run's end misread it); the
forward-scan site's K < 0 sentence is deleted with its unreachable text (review r65 C), so two sites print it. These are emitted text: L3 is an abi event (§14.4 L3).

### 14.4 The units, in order (T6 rev 3)

Common to every unit, from the manager's remodel-go call and D191.1: (1) the CENSUS runs first, on the
unit's base, as its measurement record; a unit whose census finds no mover anywhere (corpus and bench) STOPS
and reports, and lands no remodel commit; `[REV 3.1, review r51 RULING-4]` THE STOP READS THE MODEL'S PREDICTED
POPULATION. D191.1: "a unit whose census finds NO mover anywhere stops and reports". At the unit's base no part
of the unit is built, so its facts stream cannot move and an OBSERVED population there is empty by construction:
read literally, every census would stop every unit. So at the base each census runs its independent model over
corpus and bench and STOPS if the model predicts no mover anywhere; the two-sided comparison (observed movers
against the model) runs after the feature, at the feature's gate. THE MANAGER'S READING of D191.1 (review r51,
ruled), to be told to the owner `[REV 3.3, review r55 TABLE-7: answered since, agreeing, by D191 addendum 1; its (b)
is the two-sided compare's landing condition, §14.8 item 10]`; (2) then its remodel commits, each answer-identical AND
byte-identical in emitted code, each gated alone; (3) then the feature. The identity tool for every gate is
`scripts/emit_sweep.py --ref-bin <the unit's base build> --bin <the commit's build>` over the corpus and
`docs/dev/lanes/sae1_evidence/bench_patterns.txt`, verdict by `docs/dev/lanes/sae1_evidence/ident_check.py`
(E2's tools); "the .c streams" are its streams 1-2 and 4, "the facts stream" its stream 6 (`--emit-facts`),
which a unit touching the facts layer owes explicitly (coding.md: "The four byte-identity gates compare the
`.c` artifact"). A remodel's binding sabotages are the anchor map's (the note's C37:
`docs/dev/reviews/2026-11-18-r50-archlook/firstunit_anchors.py` over an export of the unit's base), re-run
at the base, each anchor re-aimed with the move and shown RED under its plant ([MECH-REACH]). New sabotage
rows take ids from the manager's range.

#### L1 — the item, the guards, the never bit, TOP at reach 0

- **Census (first).** Instrument `census_l1.py` in the lane's evidence dir: the scanner of
  `docs/dev/lanes/sae1_evidence/census_e1.py` plus E2's item classes (`look-ahead-pos`, `look-behind-pos`,
  split `:ctx`/`:look` by the reference `kinds` fact), over every `.rxt` pattern of `tests/` and the bench
  file. Model (independent of T4's code): for each pattern with a positive lookaround, an exact-set model in
  Python over the byte spelling (the body's per-offset sets, met with the neighbour's positions; abstain on
  what it cannot read: `(?x)`, callouts, verbs, conditionals, recursion, calls) predicts the reach-0 run
  and whether the root is never, `[REV 3.1, review r51 READYL1-5]` and applies the TOP SET STEP (every exact
  one-byte consumed run position joins the set at its offset), so it predicts `req_set` and `req_byte` too, not `[REV 3.3, review r53 F13: by DELEGATION, §14.8 item 11]`
  only observes them. Observed movers: the facts stream's `req_whole_run`, `req_set`, `req_byte`,
  `req_set_maxoff`, why; compared two-sided. Expected movers (§14.2's L1 column): `xy(?=bc)[bc]c`,
  `a(?=b)[bc]` (listing only), `ab[xy][xy](?=(?<=xx)y)[xy]`, `[ac][ac]cc(?<=acc)(?<=cc)d`, `x(?=qr)[pq]r`
  (`req_set`), and the never rows `foo(?=bar)baz`, `(?<=ab)(?<=cb)c` (why `dead`); non-movers `xyz(?<=yz)abc`,
  `xy[ac]b(?:(?<=ab)b|c)`, `x(?=ab|ac)a.`. `[REV 3.1, review r51 READYL1-5]` The expected fact movers include
  the set step's (§14.2): `req_set` on `xy(?=bc)[bc]c`, `ab[xy][xy](?=(?<=xx)y)[xy]`,
  `[ac][ac]cc(?<=acc)(?<=cc)d`, `a(?=b)[bc]` and `x(?=qr)[pq]r`, and `req_byte` with its emitted `RX_REQ_BYTE` on
  `x(?=qr)[pq]r` (120→113), `ab[xy][xy](?=(?<=xx)y)[xy]` (98→120) and `a(?=b)[bc]` (97→98). ~~STOP if the
  observed population is empty in corpus and bench.~~ `[REV 3.1, review r51 RULING-4]` STOP if the MODEL predicts
  no mover in corpus and bench (common (1)); the observed movers are compared two-sided at the feature's gate.
- **Remodel commits, in order.**
  1. RM-1, `RbRuns` half (D-2) and `ReqRun` half (D-5): `rr_unit`, `rr_pos`, `rr_cat`, `rr_alt` and each
     `rr_alt_rows` row start from a stated value; the two `ReqRun` writers (facts.c:97-100, :253-262) start
     from one stated empty `ReqRun`. Gate: the .c streams AND the facts stream. Binding: the note's RM1 list
     (S268, S446, S466, S807, S1910, S1915-S1919, S1923, S3129-S3132) and `tests/litscan/spanarms.rxt`; ~~the
     facts.c writers' anchors by the anchor map at the base~~ `[REV 3.1, review r51 READYL1-8 (b): the map finds
     0 anchors over the facts.c writers; why the `ReqRun` half rides early is D-5]`.
  2. `[REV 3.1, review r51 CONFORM-6, CONFORM-10, READYL1-4]` **RM-6**, the never rows as kindrow.def's NEVER
     column (D-9; outside the note's RM-1..RM-5, riding L1 after RM-1 under the manager's ruling, §14.0): derive.c's
     `q_*` read the column; the `NODE` answers stay in the readers. Gate: the .c streams, which barely reach
     derive.c (it runs on compound parts only: over the corpus this gate is near-VACUOUS for this commit, said so
     that nobody reads it as the control); the gate that EXERCISES derive.c is the derivation's tests (`git grep -l
     pcrec_derive_split_q 8993b8f82 -- tests`: `tests/compound/compound_drive.c`, with the compound suite) and
     `tests/codegen/run_cpset_structure.sh` (its `[2b]` allowlist, D-9). Binding: S899 (re-aimed if its line
     moves, shown red), S893, S1189, S1190, S904 checked; the anchor map gains a derive.c range group.
  3. `[REV 3.2, conf-spanarms8 D2]` (an L1 remodel outside the RM-n series, §14.0; confirmed by the manager 2026-11-18)
     `[REV 3.1, review r51 READYL1-6]` The head's per-kind rule moved from altnf.c's `anf_head` into desc.c with a
     position callback (D-10; register row 27's own move, event L1), `anf_head` its first caller. Gate: the .c
     streams (altnf's rewrites move no byte); binding: the anchor map over altnf.c's `anf_head` range (a range group
     the build adds), each anchor re-aimed and shown red. `[REV 3.2, conf-spanarms8 D2]` Answer- and byte-identity is a
     BUILD-LANE GATE, this commit's own identity check (the manager's remodel-go reading: each remodel gated alone;
     `[REV 3.3, review r53 F11]` ruled since by D191 addendum 2), not
     a design-time claim; the sweep should include patterns with `\w`-class heads, where `A_WCLASS` is a wall in altnf
     and transparent in the byte-level walk (conf-spanarms8 judgement (b)).
  4. (none else: RM-5 rides with L3; P5's discharge, register row 27, completes with L1's feature, D-10.)
  `[REV 3.1, review r51 CONFORM-5]` REMODEL OVERLAP: register row 14 records [RUN-POS-SET]'s stages 2a and 3m
  (still to follow) editing the same alternation fold, `rr_alt`'s rows and `rr_alt_affix`. L1's ALT guard rule is
  ONE post-step after `rr_alt`'s row scan, reading only the two values' `lg`/`rg`, and RM-1 makes each row start
  from a stated value without changing what it answers; neither depends on the row SET, so both survive either
  landing order. Whichever lands second re-reads the other's rows at its base (its anchor map re-run there); no
  serialisation is needed.
- **Feature (sites 1-9, 21, 23).** E-5i and the `look` arm (D-1; `walk_arms.def` gains `look`, its
  `walk_arm_facts` naming ~~`req_whole_run` and the facts derived from it~~ `[REV 3.1, review r51 READYL1-2: the
  walk OUTPUTS the arm can change, by walk_arms.def's own rule (derived facts inherit the token through `pf_ask`):
  PF_REQ_WHOLE_RUN, PF_REQ_SET and PF_REQ_SET_MAXOFF, not PF_REQ_PIECES]`; E-5i's arm mask `look | zero`
  `[REV 3.1, review r51 READYL1-1]` `[REV 3.2, conf-spanarms8 D1: and the ZERO row gains PF_REQ_SET and PF_REQ_SET_MAXOFF in the
  same commit (D-1); D4: the stray close paren after READYL1-1 is removed]`; `RbRuns.lg/rg/never` (D-2); T4's
  steps and ALT's post-step (D-3); the item: the head column for lookahead bodies and the description's
  reversed-head reader (D-10, desc.c); TOP's table with no rows (D-4: guards dropped at reach 0); the TOP set
  step (D-3); the never rows' run reading and the `dead` why (D-9). The D168 addendum (§12 rev 3) is filed by
  the manager in the same landing. `[REV 3.1, review r51 CONFORM-2]` TOP's walker `RB_ROW_EACH` beside
  `RB_ROW_SCAN` (D-4). `[REV 3.1, review r51 READYL1-6]` `RbVal.head` and its writers (D-10); src/facts/CLAUDE.md's
  "only reader" line rewritten. `[REV 3.1, review r51 READYL1-3]` THE FEATURE COMMIT'S ANCHORS (the anchor map
  extended over req.c's T3 rows, `rb_zero_into`/`rb_row_into`, `pcrec_req_walk` and `rn_better`, r51 READYL1 at
  B): S1925, S1926, S1927, S1653, S1928, S1929, S1887, S1907, S465, S474, S1930, each re-checked for reach after
  the feature; S474 and S1930 belong to L3's remodel 5 (D-4), checked here only for reach.
- **Contract (D80).** `facts_listing.md` §4.1.3¶1 and a new `dead` paragraph (D-13). No stamp or flag is
  added; run values move (a fact change, G4).
- **abi.** None expected: no emitted scaffolding moves, only per-pattern stamp values (`RX_REQ_RUN`,
  `RX_REQ_BYTE`) and run text `[REV 3.3, review r55 EMITTED-4: and every per-pattern value downstream of the run and
  the set, §14.8 item 7]`. If the identity verdict shows any scaffolding mover, STOP (E2's rule).
- **Tests.** `tests/litscan/spanarms.rxt` gains §5.7's L1 rows, each on both engines, every expectation
  libpcre2-8's (`tests/lib/p2probe.c`): S-L, W-L2, W-L4 (listing), W-L5, W-L6, W-L7, W-L8, W-F4, W-F5, W-A1,
  W-S1, W-N1, W-N2, W-RG, W-C1, W-E1, W-T1 (under `--memfn=no-fd-pres-pick` and as a `req_whole_run` listing
  row), W-D1..W-D7 (listing rows: `dead` / not dead), and W-S4 with `x(?=qr)[pq]r` ADDED to
  `tests/codegen/reqcube_check.py`'s `WIT`; the `-fno-ctx-node` run equality on `a(?=b)[bc]` and
  `ab[xy](?=(?<=x)y)[xy]` (listing level). New: W-D8 `x[^\x00-\xff]y` (byte) lists `dead` (the empty-class
  leaf, D-9). Mech rows: one sabotage per §5.7 planted error (ids from the manager's range), each with its
  `SAB_REACH` on its witness; W-D1 and W-D2 plant the two never branches of `rn_meet`. `[REV 3.1, review r51
  READYL1-3]` S1925 (S-L's plant, in `rb_zero_into`'s `case RB_ZERO_UNIT:`) stops being reached at default flags
  once E-5i answers every positive lookaround (RB_ZERO_UNIT then sees them only under `restore=look`): it is
  RE-AIMED onto E-5i's action in the feature commit and shown red there (deleting it is not a fix). D27: a blinded author
  is asked for goal-written witnesses of "a positive lookaround's fixed bytes join the required run of its
  neighbours" and "a pattern whose lookaround contradicts its consumed text is listed dead and still answers
  as PCRE2", from the plan row and match_api §6.3.7 only `[REV 3.1, review r51, D27 recommendation ACCEPTED:
  these goal-level witnesses are OWED BY THE BUILD LANE, written at the build by a D27-blinded author]`. Sweeps:
  `make test`, `make test-axes` with the `look` arm (isolates L1: §5.8), PC-3.
- **Measurement card.** None: no find/scan/skip/verify method is added (G4: an input to the existing pick
  rows).
- **Deletes.** E-5's plain unit as the default (it stays the `look` restore's row); the ctx-node /
  no-ctx-node run difference; rev 2.2's DEAD column as a second propagation (the never rows, D-9); register
  row ~~26's~~ 27's second per-offset union (D-10) `[REV 3.1, review r51 CONFORM-1]`; `anf_head`'s private
  per-kind head rule (D-10, remodel 3); derive.c's inline never rules (RM-6).

#### L3 — BACK: the run reaches before the start offset

- **Census (first).** `census_l3.py`: the plan row's census, corpus and bench compiles with a positive
  lookbehind whose item reaches the run's left edge; predicted movers by the L1 model plus the BACK row
  (`t <= lb_bytes`); observed: the facts stream (`req_whole_run`, `req_landmark_maxoff`, `req_byte`) and
  `RX_REQ_HANDOFF`/`RX_REQ_WHY`. Expected movers: §14.2's L3 rows (`(?<=foo)bar`, `(?<=ab|b)c`,
  `(?<=ab)ab[a-z]*q`, `(?<=qz)ab`, `(?<=e{10})eeeeeqzx`, `(?<=foo)bar(\w)\1`; `[REV 3.1, review r51 READYL3-6]`
  and the empty-extent rows `(?<=foobar)\d*x`, `(?<=foo)`, `(?<=a{32})b`; `[REV 3.1, review r51 READYL3-1]`
  `(?<=a)a(\w)\1`). ~~STOP if empty.~~ `[REV 3.1, review r51 RULING-4]` STOP if the MODEL predicts no mover
  (common (1)); observed against the model two-sided at the feature's gate. `[REV 3.1, review r51 READYL2-5]` No
  row with both a lookbehind and a lookahead moves at L3 (`(?<=foo)bar(?=baz)` stays `foobar` at −3: the `++ rg`
  clause is L2's).
- **Remodel commits, in order** (each byte-identical, its own gate):
  1. RM-2 (D-7): K's three states; the −1 sentinel retired at facts.c:106, :355, :868 and emit_dfa.c:9174;
     the hand tests through the predicates; `MF_HEAD_MAX_UNBOUNDED` at :1644. Gate: the .c streams and the
     facts stream. Binding: S467, S476, S529, S1957, S811, S1707, S1712, S463, S809 (the note's RM-2 list);
     S1706 and S1956 stay with the feature. `[REV 3.1, review r51 READYL3-8]` S3075 checked here too: its
     two-line anchor's FIRST line, `long long k = req_handoff_k(cx);`, moves if RM-2 changes `req_handoff_k`'s
     return (at both :1087 and :7922, as S463's shared line at :1087 does). The type is `PfBound` (D-7,
     CONFORM-12).
  2. RM-3 (D-8): one emitter of the move arithmetic; ROUNDUP calls, the re-ask, the reseed, the `else` and
     the unbounded branches stay in the callers; the "cannot underflow" premise moves into it. Gate: the .c
     streams. Binding: S463, S3075, S1711, S1955, S471, S470, S809, S813, S814, S1701 (the note's list), S470
     and S809 re-aimed per D-8. `[REV 3.1, review r51 READYL3-8]` S3075 is in the note's list at ":1087" only by
     the anchor tool's FIRST-LINE rule (`firstunit_anchors.py` matches a multi-line SAB_BEFORE's first line and
     stops at the first in-range hit); its real two-line site is emit_dfa.c:7922-7923, the re-ask printf, which
     RM-3 does not move (the re-ask stays in the caller) and L3's FEATURE rewrites. Every list built on that tool
     carries this limitation for multi-line anchors whose first line recurs.
  3. RM-5: `lb_max`'s read accessor beside `pcrec_lb_raise`; emit_dfa.c:3643-3644 reads it. Gate: the .c
     streams. Binding: S901; `tests/assertions/run_assertions_tests.sh`'s `VALID_LB` reads.
  4. RM-4 (D-6): `pcrec_run_scan_index` with its two callers at `[0, whole_len)`; ~~and `rn_better`'s
     comparator split `rn_cmp` (D-4)~~ (`[REV 3.1, review r51 READYL3-7 / CONFORM-3]` moved to commit 5). Gate: the .c streams, the facts stream AND the trace build
     (`tests/memfn/run_pres_picks.sh`). Binding: S453, S280, `S461_pick_none_ignores_size`,
     `tests/codegen/run_prechecks.sh`, `tests/findings/structural_check.py`, `tests/findings/e1_object_check.py`.
  5. `[REV 3.1, review r51 READYL3-7 / CONFORM-3]` `rn_better`'s comparator split `rn_cmp` (D-4), its own
     commit (the note's RM-4 never covered it). Gate: the .c streams and the facts stream. Binding: S474
     (`SAB_BEFORE='    RB_ROW_SCAN(i, w, rn_choice_rows,'`, the line the split moves) re-aimed at `rn_cmp` and
     shown red there; S1930 (the choice table's rows) checked; the anchor map gains req.c's `rn_better` range.
- **Feature.** TOP's BACK row (D-4) with `lb_bytes` (D-11); the consumed extent on `ReqRun` and its accessor
  (D-5, D-6), read by `pcrec_req_pick` and the run pin; `pcrec_run_omin` (D-7) stated on the run span's
  `omin` (emit_dfa.c:1479, the run's entry only; members stay 0; FINDING: the span's start at :1469 stays
  0, because memfn.h's run span is "start 0, verify NO, core all", so site 16's ":1469 start stating the
  fact" moves nothing there); the signed move (D-8 table) at both callers and the re-ask, `[REV 3.1, review r51
  READYL3-1, READYL3-4]` with the entry guard spelled `k != 0 || round.len > 0` and the end clamp on every
  K < 0 row; `[REV 3.1, review r51 READYL2-5]` TOP's BACK row WITHOUT its `++ rg` clause (L2's); `[REV 3.1,
  review r51 READYL3-6]` the empty-extent rule (D-6); the `k >= 0`
  conjunct of `req_handoff_entry_applies` (:9085) deleted (~~A8~~ `[REV 3.1, review r51 RULING-7]` §5.4 A8, r4
  READY3-4, ADMITTED; not review r50's A8, the never family); the three K comments (D-16); the
  presence comment's "no lookbehind byte" premise (:1543-1546) restated; `rn_scan_mass`'s comment (D-4).
  `[REV 3.1, review r51 READYL3-9]` Also RESTATED, premises L3 makes false: (1) facts.h:70-74
  `ReqRun.whole_maxoff`'s "every successful attempt at `p` holds the run at some `q` in `[p, p + whole_maxoff]`"
  (at K −3 that interval is empty; true: `q` in `[p + omin, p + K]`, so `q = p + K` exactly for BACK);
  (2) emit_dfa.c:1067-1072's "`c`, the LEFTMOST position >= `posvar`" (`c >= max(0, posvar + omin)`);
  (3) emit_dfa.c:7880-7891's "an in-flight thread ... completes only with a landmark at or after
  `scan_position`" (the move stays sound: equal DFA states have equal futures, so a completion implies a fresh
  match at `s'' >= q` whose run lies at `>= q − B`, which the kit floor finds, and `h + B <= s''`; the comment
  gains that reason); (4) the trace shadow's comment at :11342-11343 (D-6). `[REV 3.1, review r51 READYL3-8]` The
  feature's binding gains S3075, re-aimed with the re-ask edit (emit_dfa.c:7922-7923) and shown red; S3074,
  S3076 and S1702's REACH greps on `if (landmark_position < attempt_position) {` stay valid only because their
  patterns have `K >= 0`, which is checked and said in the report.
  The two ROUNDUP sites stay as §8.1 states them (A-POSDOM's two rows).
- **Contract (D80).** D-13's L3 row.
- **abi.** abi +1 at landing: the signed move, the re-ask condition and the K comments are new emitted
  text. Every reader of the number found by grep at the base (`git grep -n -w "<the abi number at the base>"`
  over `src tests docs/spec docs/testing.md`, plus `PCREC_ARTIFACT_ABI` at emit_dfa.c:55 and the identity
  gate's (B) pin), then `make test-codegen` and the suites that count (registry, codegen, rxtsource; D94
  addendum).
- **Tests.** `tests/litscan/spanarms.rxt` and the VM twin file (`tests/litscan/handoff_vm.rxt`, or the
  spanarms blocks on both engines): S-L, W-L1, W-L3, W-L8, W-L10, ~~W-L11 (K −10)~~, W-L13, W-L14 (its
  sabotage is a hang the gate's timeout reports), W-T3 `[REV 3.1, review r51 READYL2-1: an answer witness UNDER
  `--memfn=no-fd-pres-pick` only, plus its listing row]` and W-T3a as ANSWER witnesses (§14.1 item 6), W-S4c
  with `(?<=qz)ab` ADDED to `WIT`; each with §5.7's WHY/HANDOFF precondition (condition 6). W-L12 RETIRED
  (§14.1 item 7); `[REV 3.1, review r51 READYL2-2]` W-L11 RETIRED with it (its plant is W-L10's, and its one
  occurrence cannot place a match in `[c, pos)`).
  `[REV 3.1, review r51 READYL3-1]` W-L15, an ANSWER witness on both engines: `(?<=a)a(\w)\1` on `-aaaaaq-b`
  searched from 3, oracle (3,6) (libpcre2-8, `tests/lib/p2probe.c`); its run: with the entry guard kept as
  `k > 0 || round.len > 0` the attempt starts at the raw hit 2 and answers (2,5); 22 of 1857 starts differ with
  the guard kept, 0 with the per-row guard (r51 READYL3's literal execution of D-8). Its plant: the entry guard
  restored to `k > 0 || round.len > 0` (a sabotage on the guard, id from the manager's range), red on W-L15.
  `[REV 3.1, review r51 READYL3-4]` W-L16, a SAFETY witness under `make asan`: a BACK run whose kit-verified
  stretch sits at the lookbehind's left end, on a subject that ends inside the lookbehind's bytes (candidate
  `(?<=Content-Length: )\d` on a subject ending `...Content-Length:`; the build measures which spelling places
  the kit's stretch inside `[0, B)` and says so), oracle NOMATCH; its plant: the clamp removed, red as an ASan
  report or a start past `n`. `[REV 3.4, review r65 F]` MEASURED UNDETECTED by construction (the downstream
  `search_from > subject_length` guard answers first): S3407 is a planted record (`SAB_EXPECT=UNDETECTED`).
  `[REV 3.1, review r51 READYL3-6]` W-L17, W-L18, W-L19 (facts and answers): `(?<=foobar)\d*x` (`req_byte` 120,
  pin none), `(?<=foo)` (`req_byte` none; on `foo` matches (3,3), oracle `M 3 3`), `(?<=a{32})b` (empty extent
  at the bound); each under `make asan`/`make ubsan` too (the compiler's `cand[0]` read is the plant: the
  accessor's `lo == hi` refusal removed).
  `[REV 3.1, review r51 READYL3-2]` `tests/codegen/run_prechecks.sh`: (1) `s512_presence` [5.12b] gains a K < 0
  arm (a `"-3"` stamp today falls into the K = 0 arm, which checks only that nothing is subtracted): the add and
  the distance test carry `-$st`; (2) [5.12a], the independent hand-K pin table, gains lookbehind rows derived by
  hand from this text, never from the walk: `(?<=foo)bar(\w)\1` under `byte` (K −3), `(?<=e{10})eeeeeqzx` (K −10),
  and a `utf8` row where B counts the bytes of a multibyte lookbehind (D-11).
  `[REV 3.1, review r51 READYL3-5]` `tests/startset/vmhat_checks.py`'s handoff value rule (`isdigit()`, its
  header's contract "`RX_REQ_HANDOFF` is `"none"` or a decimal K") admits a SIGNED decimal; else every VM
  start-set mover with a BACK run is an unexplained `handoff` red mid-gate. The lookaround-pinning witnesses no remodel moves but L3 does: S1887 (`(?<=abc)x`, run
  none today) re-aimed if its run moves (`abcx` at −3 is the prediction), S3076 checked. D27: goal-written
  witnesses of "a match is never reported before the start offset when the required run begins in a
  lookbehind" (the start-offset family: from 0, from inside the lookbehind's bytes, from just past them)
  and "find-all over overlapping lookbehind runs" `[REV 3.1, review r51, D27 recommendation ACCEPTED: OWED BY THE
  BUILD LANE; brief the author with the start-offset family as written, not with READYL3-1's witness]`. Sweeps: `make test`, `make test-axes` (`look`), PC-3;
  `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` (a strategy fires in new places: the handoff on
  lookbehind runs).
- **Measurement card.** No new method: the scan before the start offset is the kit's K38-2 run part (its
  card is the kit's). ~~The COST row this unit adds is §5.5's per-call step back in a find-all regime: the
  bench cell the trigger names is its measurement; the cap is `lb_bytes`, and the user can turn it off
  (bit 31, re-specified).~~ `[REV 3.4, review r65 B]` The COST row is a SECOND SCAN per call, not the step back:
  where BASE judged the run pre-check `dominated` by a run-pinned prefilter (`(?<=foo)bar`), the BACK run
  (`foobar`) is not dominated, so the emitted pre-check (`rx_reqrun`) runs before an equivalent prefilter on every
  find-all call. Measured (review r65 EMIT-2; `perf stat -e instructions:u`, 1 MB, a match every 64 bytes):
  `(?<=foo)bar` +17.9% (~56 instructions a call at B = 3, not scaling with B), `(?<=qz)ab` +9.1%,
  `(?<=a{20})b{8}zb{11}` +10.0%, `--engine=vm` +7.1%; 0.47 on decoy subjects, neutral where the run is absent. The
  cap `lb_bytes` does not bound it; bit 31 still turns it off. After the REV 3.4 pick rule the default route keeps
  BASE's run on every one of those shapes, so the row remains only where BACK is still chosen (`--engine=vm`,
  `-fno-req-handoff`, a consumed part with no run or an unbounded one): `(?<=foo)bar --engine=vm` measured again at
  l3r65, +1.9% (absent) / +7.1% (a match every 64 bytes) / 0.86 (decoy). The bench cell measures THIS mechanism. A
  dominance row for a BACK run whose consumed extent is the prefilter's pinned run (check the lookbehind once on the
  prefilter's hit) is ASKED of the owner (slug back-findall-cost), not built.
- **Deletes.** The −1 sentinel (RM-2); one copy of the move arithmetic (RM-3); the direct `lb_max` read
  (RM-5); one copy of the scan-index expression (RM-4); `rn_better`'s inline row scan (remodel 5); the `k >= 0`
  conjunct (~~A8~~ §5.4 A8 `[REV 3.1, review r51 RULING-7]`); the "cannot underflow"
  premise as a universal (restated per K row); `p[i].omin = 0` on the run span; the presence comment's "no
  lookbehind byte" premise.

- `[REV 3.3, lanes l3feat/l3feat2, ruling R-1 (manager, 2026-11-20)]` **PREMISE (3) IS REFUTED BY MEASUREMENT; the
  forward scan's re-entry is DECLINED at K < 0.** The restated premise (3) above ("the move stays sound: equal DFA states
  have equal futures, so a completion implies a fresh match at `s'' >= q`") is false for a BACK run. WITNESS (W-L17):
  `(?<=foobar)\d*x` on the default route (VM hybrid, `RX_DFA_PREFILTER "handoff"` before the decline) answered NOMATCH on
  `foobar12x` (libpcre2 (6,9)) and (15,16) on `xfoobar9xfoobarx` (libpcre2 (7,9)). CAUSE: `\d*` is absorbed into the
  machine's start state, so at scan position 7 the state is the start state while the true match begun at 6 is in flight;
  the re-entry reads that as a fresh search from 7, requires the run at or after `7 − 6 = 1`, re-asks, and finds none.
  State equality covers only the CONSUMED part of a match: the lookbehind's bytes are tested by the machine but are never
  in the language its start state's future recognises, so "equal states, equal futures" says nothing about a run that
  lies before the scan position. THE DECLINE: `pf_handoff_applies` (the prefilter table's `handoff` row) gains a declared
  condition, `req_k_reentry_sound` (K bounded and negative refuses), so at K < 0 the start-byte row below takes the
  artifact (`(?<=foobar)\d*x` becomes `RX_DFA_PREFILTER "memchr"` with `RX_REQ_HANDOFF "-6"`: the entry move still
  applies ~~)~~ `[REV 3.4, review r65 A/CONTRACT-5]` where the start-byte row does not DOMINATE the pre-check; where it
  does (`(?<=x)qzjv[a-z]*\d`, BASE `handoff` at K 0 -> `memchr-bounded`, `RX_REQ_WHY "dominated"`, no pre-check and no
  entry move) nothing of the run is left, and since REV 3.4 that shape keeps BASE's run). The ENTRY move and the VM attempt loop's re-entry stay: an attempt there is a real fresh start, which the
  argument needs. COUNTS (the l3feat witness file, 1,232 cells over W-L1/3/10/13..19, W-T3a, utf8 and bench 333 on both
  engines): with the decline 1,232 pass; without it 15 fail, all W-L17 (`tests/harness/run.sh` over the generated
  file, builds with and without the decline). Of the census's 57 movers no stamp changes under the decline ~~.~~ `[REV 3.4, review r65 A]` (a census of decline
  against no-decline; against BASE the stamps DID move, see REV 3.4). Its plant is
  S3405, red on W-L17. Premise (3)'s sentence in emit_dfa.c (`pf_emit_handoff`'s header) keeps its form for K >= 0, where
  the run lies wholly in the consumed part.

- `[REV 3.4, lane l3r65, review r65 rulings (manager, 2026-11-20 19:25)]` **THE LOSS AGAINST BASE, AND THE PICK RULE.**
  MEASURED AGAINST BASE (the merge-base `694d91dc4`, built clean; review r65 EMIT-1/CONTRACT-5): at L3 the run choice
  preferred the BACK run, and R-1's decline then refused the `handoff` row, so a pattern whose consumed part BASE handed
  off lost its forward re-entry: `(?<=qz)x?a:` BASE `handoff` on `a:` (K 1) -> `memchr` with `qz` at -2, an EMPTY
  consumed extent; on 1 MB with no `:` 225,064 -> 2,325,063 instructions (x10.3), 0.74-0.87 on English-like text;
  `-i (?<=foo)bar`, `-i (?<=item )done`, `(?<=a)\Kb`, `(?>(?<=a)b)` `handoff` -> `byte-class`/`memchr-bounded`;
  `(?<=x)qzjv[a-z]*\d` `handoff` -> `dominated`. THE PICK RULE (D191 addendum 1's RECORD (b), the manager's record line: "After the build,
  a result that differs from the census's expectation is a reason to reassess, not to push on." `[REV 3.5, review r66
  TRADE-3: quoted, was a paraphrase]`; its ruling of record is D191 addendum 3, review r66 TRADE-4): TOP's BACK row gains a declared `displaces` column (src/facts/req.c `rb_top_back_displaces`),
  read before the run choice compares the two runs: on a compile that may RE-ENTER A FORWARD SCAN, a BACK candidate
  displaces only a consumed `best` that is EMPTY or begins at no static bound (a K >= 0 run at a bounded offset is the
  one the re-entry keeps), and a candidate with an EMPTY consumed extent displaces no consumed run. "May re-enter a
  forward scan" is a walk parameter (`ReqWalkParams.fwd_reentry`): false only under `--engine=vm` (no hybrid
  prefilter) and `-fno-req-handoff` (no handoff row), the two compiles where no forward re-entry exists whatever route
  the engine selection takes; the run choice is a fact below the route, so the parameter reads the options, never the
  route. A default-engine VM artifact with no prefilter (`(?<=a)a(\w)\1`) is conservative: it keeps BASE's run. Its
  plant is S3455 (the column passed over), red on [facts-look]'s default-route cells.
  RE-MEASURED BASE -> SUBJECT at l3r65 (`perf stat -e instructions:u`, `taskset -c 7`, 5 repeats, median; 1 MB
  subjects absent/rare/common/decoy, scratch `perf/results.tsv`): `(?<=qz)x?a:`, `-i (?<=foo)bar`, `-i (?<=item )done`,
  `(?<=a)\Kb`, `(?>(?<=a)b)`, `(?<=x)qzjv[a-z]*\d` (and `(?<=foo)bar`, `(?<=foobar)\d*x`, `(?<=qz)ab`) emit C
  byte-identical to BASE but for the abi digits, and every cell is 1.000 (`(?<=qz)x?a:` absent 225,059 -> 225,059).
  Where BACK is still chosen it wins: `(?<=xyz)a+xyz` 0.33-0.82, `(?<=foo)` x8 (12,712,033 -> 1,518,991 absent).
  THE CENSUS, BASE -> SUBJECT (all 428 corpus `(?<=` patterns x byte, `-i`, utf8 and `--engine=vm`; scratch
  `census_lb.tsv`): default byte/`-i`/utf8: 2 movers each, `(?<=foo)` (no run -> `foo` at -3, `RX_REQ_WHY "none"` ->
  `"emitted"`) and `(?<=xyz)a+xyz` (`xyza` at -3, `RX_REQ_BYTE` 122 -> 97, review r65 J; `RX_DFA_PREFILTER` unchanged,
  `memchr`); `--engine=vm`: 93 movers, L3's whole effect (the VM attempt loop's signed move); `RX_DFA_PREFILTER` moves
  on NO pattern on any stream; the program region (`goto rx_L0;` .. `rx_accept:`, the recursion identity gate's (A) region) is identical on
  all 1,712 cells. W-D2 `(?<=ab)(?<=cb)c` (review
  r65 K) lists BASE's `none`/`dead` by default and `bc` at -1 under `--engine=vm`; §14.2's row is read per route.
  "The entry move still applies" now holds where BACK is chosen on a forward route and the start-byte row does not
  dominate the pre-check (`(?<=xyz)a+xyz`: `memchr`, `RX_REQ_HANDOFF "-3"`, the entry move emitted).
  STEP 2 (review r65 A, HOUSE-6 unlock 1): a re-entry on the run restricted to its consumed extent, `K' = whole_maxoff
  + cons_lo >= 0`, needs its own soundness argument (the decline's lesson); plan row [L3-CONS-REENTRY], triggered by
  L2's design, which also records the owner's 2026-11-20 lean that graph-based re-entry waits for a general rx/graph
  manipulation layer `[REV 3.5, review r66 TRADE-2: its home is main's docs/design/plan_row_bodies/REQ-LOOKAROUND.md,
  the LEAN paragraph, landed after this branch's base; his words, verbatim:]` "Looking forward, we are probably going to
  have to build a bunch of rx and graph manipulation stuff for the predicate language. I don't know how you planned to
  implement rx intersection or subtraction but this sounds an awful lot like that. Perhaps we save both this and match
  start for then when it can be proper manipulation rather than one offs" (a discussion, not a ruling).
  REVIEW r65 C: the K < 0 forward-scan texts the decline made unreachable are DELETED (the hybrid prefilter's K < 0
  kept-hit init and `pf_handoff_applies`'s K < 0 sentence); at that state the compile refuses with the house's internal
  error, so S3405 (the decline removed) now refuses `(?<=xyz)a+xyz` and is red in run_prechecks.sh [5.12a];
  run_prechecks.sh [5.12l]'s K < 0 arm (it ran zero times, and was red on correct text when planted) is deleted and
  its `nd` count restored for K >= 0. L2 brings its own text and check with a witness (D77).
  REVIEW r65 E: the D27 goal-written witnesses this unit's Tests owe (the start-offset family; find-all over
  overlapping lookbehind runs) are owed BEFORE LANDING by a SEPARATE blinded D27 cell lane the manager launches after
  this fix lane; the build lane's "owed" is read as owed before landing.
  THE RULINGS THIS UNIT RELIED ON, copied verbatim from the l3feat lane's rulings file (review r65's freeze note: they
  had no committed record):
  > R-1 (manager, 2026-11-20 ~16:40): l3feat's STOP is accepted. ADOPT THE DECLINE: pf_handoff_applies declines the forward-scan `handoff` row whenever the stated K < 0 (a declared row condition in the existing table, not an if-spiderweb). The entry move and the VM attempt-loop re-entry stay. span_arms §14.4 L3's "RESTATED premise (3)" (the forward-scan re-entry is sound at K<0 because equal DFA states have equal futures) is REFUTED by measurement: state equality covers only the run's consumed part; the lookbehind bytes are never in the DFA's language. Record it as a REV 3.3 addendum in span_arms §14.4 L3 (the witness, the cause, the decline, the counts 1232 pass / 15 fail without), and a one-line note in §14.4 L2 that AHEAD bytes are likewise outside the DFA's language, so L2's design must re-check any forward-scan re-entry before relying on it. The bff1a3d89 deviation (hybrid prefilter's landmark_position init now asks the kit at init) goes in "Deviations from the design". A sabotage row (from S3405-S3429) removes the decline and must go red on W-L17. Also fix gen_presence_deny.py --check-pcrec so its mkdtemp uses $PCREC_TMPDIR (default /var/tmp/pcrec-<user>), never /tmp.
  >
  > R-2 (manager, 2026-11-20 ~17:00; a question from the owner, reply in the report's "Forward-scan decline at K<0" section): for `(?<=foobar)\d*x`, bench 258 `(?<=item )done`, bench 333, and every census mover whose prefilter the decline changes, state (by command) at BASE, at L3 without the decline, and at L3 with it: DFA_PREFILTER, the byte(s) or run the prefilter actually searches for, and whether that byte/run comes from the lookbehind. Also count how many of the 57 census movers the decline touches at all. The owner asked whether the decline throws away the point of L3 (lookbehind bytes in the search); the answer must be measured, not argued.

- `[REV 3.5, lane l3r66, review r66 rulings (manager, 2026-11-21 01:40)]` **THE PICK RULE KEYED ON THE LANDMARK, AND THE
  `-fprefilter` ROUTE.** Two speed findings against BASE (`694d91dc4`, built clean), both re-measured by `perf stat -e
  instructions:u`, `taskset -c 7`, 5 repeats, a 1 MiB buffer searched 5 times (fill floor ~9.0M; scratch
  `l3r66/perf/m.sh`, `emit23.tsv`):
  (EMIT-2) `fwd_reentry` read `engine != VM`, but `-fprefilter` (PCREC_FORCE_PREFILTER) forces the forced VM a hybrid
  prefilter whose forward scan takes the `handoff` row: `(?<=qz)x?a: --engine=vm -fprefilter` went `handoff` on `a:` at 1
  -> `memchr` on `qz` at -2, 8,998,887 -> 14,170,843 on English text. Now `fwd_reentry = !-fno-req-handoff && (engine !=
  VM || -fprefilter)`, still options-only: 8,998,888, BASE's stamps. Plant S3480.
  (EMIT-3) an EMPTY consumed run is not "nothing to keep": with no consumed run BASE's forward scan hands off on the
  necessary BYTE (facts_listing §4.1.2¶8b's landmark), and `best->n == 0` let BACK displace it: `(?<=qz)(?:a.|.a)` went
  `handoff` on `a` at K 1 -> `byte-class` on `qz` at -2: qz-dense text (`qz bqz cqz `) 8,998,891 -> 39,964,842 (x4.4
  LOSS); English 85,622,145 -> 14,170,871 (x6 WIN, BASE's re-entry thrashes on `a`). RULED: keyed on the landmark. The
  BACK row's `displaces` now reads the root's necessary set beside its consumed `best`, one declared row condition:
  BACK displaces (1) an EMPTY `best` whose set has no member at a static bound (`rb_set_bounded_landmark`, over
  `RbSet.off`), or (2) a `best` at no static bound by a candidate with a consumed position, or (3) anything where no
  forward re-entry exists. "Some member bounded" is a superset of "the picked member is bounded" (the pick is a derived
  rate choice the core walk does not read); the superset only keeps BASE more often. Re-measured: qz-dense 8,998,891,
  English 85,622,144, BASE's stamps on both. The English win is given up: plan row [L3-BYTE-LANDMARK-WIN] (trigger:
  L2's design, or a bench pattern reaching the shape). Plant S3481.
  The rule's narrowing direction (review r66 CHECK-4's plants): S3482 (no empty-best arm, red on `(?<=foo)`), S3483 (no
  unbounded arm, red on `(?<=xyz)a+xyz`), S3484 (no engine clause, red on the `--engine=vm` cells).
  RE-CHECKED BASE -> SUBJECT at l3r66: the six r65 A patterns (`(?<=qz)x?a:`, `-i (?<=foo)bar`, `-i (?<=item )done`,
  `(?<=a)\Kb`, `(?>(?<=a)b)`, `(?<=x)qzjv[a-z]*\d`) emit C identical to BASE but for the abi digits and read 1.000 in every
  cell (absent/rare/common/decoy). THE CENSUS (the 428 corpus `(?<=` patterns x byte, `-i`, utf8, `--engine=vm` and,
  new, `--engine=vm -fprefilter`): default byte/`-i`/utf8 2 movers each (`(?<=foo)`, `(?<=xyz)a+xyz`, unchanged from
  REV 3.4); `--engine=vm` 93 (unchanged); `--engine=vm -fprefilter` the same 2 as the default; the program region is
  identical on all 2,140 cells. No corpus pattern reaches EMIT-3's shape, so the census does not move with it.

#### L2 — AHEAD: the run reaches past the consumed end (after its readiness critic) `[REV 3.1, review r51: the critic is r51's READYL2 lens, discharged on condition, §14.0]`

- **Census (first).** `census_l2.py`: compiles with a positive lookahead whose item reaches the run's right
  edge; observed `req_whole_run`, `req_byte`, `run_pin`, `RX_REQ_WHY`, `RX_DFA_PREFILTER`. Expected movers:
  `bar(?=baz)` (`barbaz`; WHY `dominated` → `emitted`, hand-derived: the pin covers the consumed extent only),
  `xyz(?=abc)` (`xyzabc`), `[a-z]?[a-z]a(?=bc)` (~~`abc` at 2~~ `[REV 3.1, review r51 READYL2-3]` `[a-z]abc`, K 1;
  any other AHEAD prediction whose tail ends in a set position is re-measured the same way), `[REV 3.1, review r51
  READYL2-5]` `(?<=foo)bar(?=baz)` (`foobarbaz` at −3, consumed `[3,6)`: the BACK row's `++ rg` clause). ~~STOP if
  empty.~~ `[REV 3.1, review r51 RULING-4]` STOP if the MODEL predicts no mover (common (1)).
- **Remodel commits.** None of its own (RM-4 and the consumed extent landed with L3; if L2 lands first,
  RM-4 and the extent move here, as the note says). `[REV 3.1, review r51 READYL2-6 (1)]` If L2 lands first, ALL
  of these move to it: RM-4 (L3's remodel 4), the `rn_cmp` split (L3's remodel 5, which AHEAD's candidates need
  to keep their extents), the `ReqRun` extent with `pcrec_run_cons` and the empty-extent rule (D-5, D-6), and
  `rn_scan_mass`'s comment (D-4: `req_byte` and the ranking diverge at AHEAD too); and D-13's "pick's stretch"
  hunks. `[REV 3.2, conf-spanarms8 D3]` WHERE THE BACK ROW'S `++ rg` CLAUSE LIVES IF L2 LANDS FIRST: the clause is a part of the
  BACK row (D-4's table), and the BACK row is L3's, so with L2 first there is no row to host it: L2 does not carry it and
  ships the AHEAD row alone (no BACK candidate exists, so `(?<=foo)bar(?=baz)`'s `foobarbaz` at −3 does not move at L2); L3,
  landing second, adds the BACK row WITH the clause (the clause is the part of the row that needs the `rg` guard and the
  extent L2 already built), and the census row and test row for `(?<=foo)bar(?=baz)` (W-L9's neighbour, below) move from L2 to
  L3 in that order. In the ruled order (L3 first) it is as written: L3 ships the BACK row without the clause, L2 adds it. The
  rule in one line: the clause lands with whichever of {L2, the BACK row} comes second. D-13's AFTER-side hunks follow the
  clause, so they land with L2 in either order (they cover AHEAD's own reach); the BACK clause adds no hunk of its own.
- `[REV 3.3, L3's R-1]` AHEAD bytes, like a lookbehind's, are outside the DFA's language (a lookahead's bytes past the
  consumed end are tested, never consumed), so L2's design must re-check any forward-scan re-entry (§14.4 L3's REV 3.3
  addendum) before relying on it.
- **Feature.** TOP's AHEAD row (D-4) `[REV 3.1, review r51 READYL2-5]` and the BACK row's `where all, lg ++ head
  ++ rg` clause; the pin reads the consumed extent (already, from L3). An AHEAD candidate's K can be negative only
  under W-L9's plant (`rn_tail_off` from the EXTENDED length gives K −1 and `pcrec_run_omin` −1 on a lookahead
  run, a state D-7's "AHEAD has omin 0" never meets): the gate expects that state under the plant only, as a
  red.
- **Contract.** D-13's L2 row.
- **abi.** None expected (no new emitted form); STOP on a scaffolding mover.
- **Tests.** W-L9 (`[REV 3.1, review r51 READYL2-3]` correct `[a-z]abc` at K 1: on `zzabc` from 0 the occurrence
  c = 1 gives start 0 and (0,3) (oracle `M 0 3`; from 1 `M 1 3`; from 2 `N`); its plant gives K −1: after L3
  the start is 1 + 1 = 2 and NOMATCH, before L3 (L2 first) no move is emitted at K <= 0 and the attempt at 1
  answers (1,3); wrong either way), W-T2 (`[REV 3.1, review r51 READYL2-1]` an answer witness UNDER
  `--memfn=no-fd-pres-pick` only, plus its listing row) and W-T2a (answers; §14.1 item 6), `[REV 3.1, review r51
  READYL2-5]` a `(?<=foo)bar(?=baz)` row (from 0 and 3 `M 3 6` on `foobarbaz`, from 4 `N`; listing `foobarbaz` at
  −3) with a plant on the `++ rg` append at BACK, W-L4's listing row at L1 becomes L2's mover
  (`barbaz` is now correct), W-S4b with `bar(?=baz)` ADDED to `WIT` (`req_byte` stays in `bar`), each with
  the WHY/HANDOFF precondition. S1700 and S469 (lookahead plus a run/handoff stamp) re-checked. D27:
  "the required run of a pattern ending in a lookahead is found in the subject even when the match ends
  before the lookahead's bytes" `[REV 3.1, review r51, D27 recommendation ACCEPTED: OWED BY THE BUILD LANE]`.
- **Measurement card.** None (no new method).
- **Deletes.** W-L4's "reach leak" as a sabotage (it is the correct value at L2); the AHEAD half of §8's
  stale kit dependency.

### 14.5 The never fact and the cover route: what the owner's 2026-11-18 words ask of L1-L3

"The search span the pcrec delivers to kit should have "foobar" with starting index -3": L3's presence run
span (`omin` −3, K −3, the whole run uncut, D191.2). "in this case, the match is proved and search is over":
for a pattern that IS that span, the kit's verified hit is the match where §12c's SUFFICIENT and
OUTPUTS-DETERMINED hold; at T that ending is the `cover` route, which today takes `(?<=f)bar` (one-character
context, `known.c`'s −1 side; `RX_DFA_SCAN "cover"`) and NOT `(?<=foo)bar` (`"unanchored"`, C-R6). ~~Making
the cover take a wider lookbehind is a READER of L1's item ([CTX-SIDES-PRODUCER] / D172's window site /
[LOOK-LOCATE]), on its own trigger; L1-L3 build the item and the presence span it reads and nothing more.~~
`[REV 3.1, review r51 RULING-5]` L1-L3 DO NOT DELIVER that ending: they build the item and the presence span
it reads and nothing more, and the owner is not to be told that L3 delivers it. The row that owes it is
[CTX-SIDES-PRODUCER] (the cover's `MkEnd` `ctx_before`/`ctx_after` read from the one producer instead of the
anchored machine's one-position reading); ~~whether its trigger has fired is the manager's, from the facts in
the spanarms8 report~~ `[REV 3.2, conf-spanarms8 D4: the transient report pointer is replaced by the durable record, the [CTX-SIDES-PRODUCER] plan row's status line (main): "trigger FIRED (cover B1 = bc675b020, 2026-10-23, before this row was filed); row unstarted; owner question open"]`.
"Otherwise, the kit reports back the 0 span subject offset and pcrec does the match": the existing presence
pre-check and the signed move (D-8). `[REV 3.1, review r51 RULING-6]` The two "0"s: in the owner's indexing span
index 0 is the attempt start (`b`, the `foo` at −3..−1); the kit, told only offsets (D157, D191.2), reports the
run occurrence's position 0 (the `f`, the run's first byte: memfn.h's `head_max` is "the largest offset, from
the attempt start, of the ASSIGNED landmark's position 0"), and pcrec adds `B` (D-8's `hit += B`) to reach the
owner's 0. Same answers; the conversion is pcrec's, an answer-free division of work (the manager's call).

### 14.6 Standing questions (rev 3)

1. **Measurement regime: RELEVANT**, as §11.1; every T number above is a compile-time fact of the main
   tree's `build/pcrec` (gcc 15.2, the dev box), C-R2. L3's cost is per call in a find-all regime.
2. **Independent control: RELEVANT.** Each census model is a Python exact-set model over byte spellings,
   sharing no code with T4; witnesses carry libpcre2 answers; the remodels' controls are the anchor map's
   sabotages found by LOCATION, each shown red under its plant; the identity gates compare against the
   unit's BASE build, a different binary.
3. **What moves when data is regenerated: NOT RELEVANT.** No table, calibration or data file is added.

### 14.7 Commands (rev 3; outputs in `$PCREC_TMPDIR/scratch/spanarms7/`, not committed)

- C-R0 `git diff --stat 57fcb5737 8993b8f82 -- src memfn/src memfn/include lib cli docs/spec tests/mech/sabotages docs/dev/decisions.md docs/design/span_arms.md` (1 file: memfn/docs/requests.md)
- C-R1 `git grep -n "span_arms E1\|span_arms R1\|span_arms E2" 8993b8f82 -- src/facts/req.c` (7 lines: :477, :732, :991, :993, :1077, :1080, :1082)
- C-R2 `python3 -I probe.py pats.txt` (scratch): for each pattern, `timeout 60 build/pcrec -p rx --features all --emit-facts --pattern P` (the main tree's binary), rows `req_whole_run`, `req_byte`, `req_landmark_maxoff`, `req_set`, `never_matches`, `run_pin`, `RX_REQ_RUN`, `RX_REQ_WHY`, `RX_REQ_HANDOFF`, `RX_DFA_SCAN`, `RX_VM_PREFILTER`, `kinds`; output `probe_T.out` (29 patterns)
- C-R3 `git grep -n -i -E "span_facts|MkCtx|pcrec_span_walk" 8993b8f82 -- src` (0)
- C-R4 `git show 8993b8f82:memfn/include/memfn.h | grep -n -E "^#define MF_SITE_ABI|may be NEGATIVE|negative on the run span|SIGNED: with a negative|MF_HEAD_MAX_UNBOUNDED"` (MF_SITE_ABI 29 at :39)
- C-R5 `git grep -c "req_run_member\|pcrec_req_window" 8993b8f82 -- src` (0)
- C-R6 the C-R2 probe on `foobar`, `bar`, `(?<=f)bar`, `(?<=foo)bar` (`probe_cover.out`: `cover`, `cover`, `cover`, `unanchored`)
- C-R7 `git show 8993b8f82:src/gen/emit_dfa.c | grep -n "%lld bytes before"` (3: :1118, :7900, :7967)
- C-R8 `git show 8993b8f82:src/facts/req.c | sed -n '905,914p'` (`rb_rep_split_val`: its description is `pcrec_pd_none()`)
- C-R9 `git show 8993b8f82:src/gen/emit_dfa.c | grep -n "define PCREC_ARTIFACT_ABI"` (:55, 108 at T; the landing's number is "abi +1 at landing")

`[REV 3.1, review r51]` Rev 3.1 is TEXT applied from review r51's findings as ruled; its numbers are the review's
measurements at B = main `1403873df` (critic texts and verifier in `docs/dev/reviews/2026-11-18-r51-spanarms7/`), not
re-measured here. The lane's own runs (RULING-5's fact task, reported to the manager, not a design input):
- C-R10 `grep -rn "B1" docs/design/kit_proof.md` (the kit-proof note is `docs/design/kit_proof.md`; nothing under `docs/design/memfn/` matches `kit_proof*`)
- C-R11 `scripts/entry CTX-SIDES-PRODUCER -l 2`, `scripts/entry LOOK-LOCATE -l 2`, `scripts/entry COVER-CAP -l 1`
- C-R12 `timeout 60 build/pcrec -p rx --features all --emit-main -o $PCREC_TMPDIR/scratch/spanarms8/lbfN.c --pattern P` (the main tree's binary) for `(?<=foo)bar`, `(?<=f)bar`, `foobar`, then a grep for `RX_DFA_SCAN`, `RX_REQ_`, `COVER`

### 14.8 REV 3.3: L1 as built (review r55, the D27 witnesses, review r53's owed text) `[REV 3.3]`

Lane l1ffix, 2026-11-19. The build of record is lane/l1feat plus l1ffix's fixes. Each item names its source and the
passage it amends; a passage above carries a `[REV 3.3 ...]` marker pointing here.

1. **CAT-SET is choice-free (r55 A; supersedes D-3's "CAT-SET, re-spelled" and TOP's set step).** As D-3's T4 table
   first had it, a FIXED STEP of `rr_cat`, between CAT-L and the consumed join: every consumed position the meet
   narrows to ONE byte joins the necessary set at its own offset, if the set lacks it; an empty set takes it as its
   pick. A repeat's copies thread the set through `rr_pow`, so a narrowing inside a copy still joins it, which was
   rev 3's reason for moving the step to TOP. The set reads no run choice again: `req_set`/`req_set_maxoff` are CORE
   facts once more (CONTRACT-3); a byte joins whichever run the choice keeps (`x(?=y)[yz].*qr`: `113,114,120,121`
   in byte and utf8 alike). TABLE-1 holds only where a restore removes a narrowing: the arms `empty` and `rep` (a
   cut or a best-only copy separates a guard from its position) now name `req_set`/`req_set_maxoff` with `zero` and
   `look` (walk_arms.def; measured: `alt` and `tie` move no set). EMITTED-1 (a present member keeps its looser
   offset, `[ac][ac](?<=ac)cc` `99:2`) is unchanged, as ruled, a PLAN row.
2. **The pin claims only what the walk proves (r55 B; discharges §14.1's L2 A5 in the same rule).** `pcrec_run_pin`
   pins, around the rarest exact byte that has one, the longest stretch of the run's exact positions the k-set walk
   proves (ties to the smallest offset). Where nothing is narrowed it is BASE's pin: the argmin is monotone and the
   proved stretch is the maximal one. A narrowed position the walk does not see shortens the stretch instead of
   losing it (`xy(?=bc)[bc]c` `0:0+2`, `foo(?=b)[bc]{2,4}` `0:0+3`, BASE's values). L2's AHEAD extension (A5: "an
   extended run loses its pin") is the same case: no third per-case patch. tuning §2.30¶4 states it.
3. **One never leaf on an empty position (r55 C, TABLE-5 item 2).** `rb_never_pos`: a position whose set admits no
   byte is a never leaf, read where the walk turns a node into a position: the class (out of the run's domain too:
   it enters `rr_cat` as a gap carrying the bit, so the CAT row decides, not a hard-coded ANY) and the `A_CTX` item.
   `x(?=[^\x00-\xff])y` lists `dead` with and without `-fno-ctx-node` (W-D9, `[facts-look]`).
4. **The `dead` token and the others (r55 CONTRACT-2, CONTRACT-4).** facts_listing §4.1.3¶4a gains ONE CLAUSE (the
   lane's choice over letting `harness:` co-exist): a dead `req_whole_run` lists `dead` by ¶1's order though a
   restored arm may move its value; its derived facts carry the token. ¶1a: `dead` on a DERIVED `req_whole_run`
   only (a denied one lists `deny:`), independent of `never_matches`.
5. **The two sabotage rows that reached nothing (r55 CHECK-3, CHECK-4).** The design's W-L2 and W-L6 groups are
   leftmost: the walk flattens them into the spine and never reaches CAT-EDGE with them. Their rows (S3366, S3368)
   take OWN witnesses where the group is a right operand: W-L2b `x(?:(?=abcd)ab)cd`, W-L6b
   `[xy](?:(?=apq)a.?)[pq][qz]zz` (spanarms.rxt, both engines, libpcre2's answers). The critic skill's plant step
   now applies every `SAB_*n` edit and removes the copied binaries (separate commit), the cause of CHECK-5's miss.
6. **TABLE-4 (b).** E-5i's action re-spells `rb_zero_unit_into`'s two lines (`rb_zero_item_into`); one reader of
   both is the fold when the item gets its second reader.
7. **EMITTED-4.** The per-pattern values that move with L1 are every value downstream of the run and the set:
   `RX_REQ_RUN`, `RX_REQ_BYTE`, `RX_REQ_WHY`, `RX_REQ_HANDOFF`, `RX_DFA_PREFILTER(_OFFSETS)`, `RX_DFA_SCAN_EDGE`,
   `RX_MEMFN_LIBC`, `RX_RUN_WORDS`, `RX_VM_RESEED` and the route templates they select. Still no scaffolding mover.
   TABLE-4 (a): `RX_REQ_BYTE` moves none → a value where an empty set takes a narrowed pick (`(?=q)[pq]` → `113`);
   §14.2's movers include those.
8. **CHECK-5.** S3382's flag sabotage lists W-D3, W-D4 and W-D6 dead; W-T1's pattern (W-D7) has no dropped empty
   meet under it, so the claim names three rows, not four.
9. **r53 F2.** S899 binds the ALT row's per-arm drop (`!it[i].keeps`), not the NEVER column, which RM-6 moved to
   `pcrec_never_by_row`; the column's cells carry their own rows (r53's FIX-NOW).
10. **r53 F11, r55 TABLE-7.** The remodel commits ride the build go by D191 addendum 2 ("small refactors ride the
    build go"), not a contingent reading; the census STOP and the two-sided compare follow D191 addendum 1: the
    census is fail-fast, and (b) "a result that differs from the census's expectation is a reason to reassess, not
    to push on". (b) counts performance movers too, so the compare judges `run_pin` and `req_landmark_maxoff`
    beside the facts (lane l1ffix's `compare_l1.py`).
11. **r53 F13.** The census model predicts the NARROWING and the never bit only; the predicted run, `req_byte` and
    `req_set_maxoff` are the reference compiler's facts of the model's SPELLING. So the run choice is shared between
    prediction and observation, a known limit of the two-sided compare (it cannot find a wrong run CHOICE, only a
    wrong narrowing); `(?i)` and `(?x)` patterns abstain.
12. **r53 F5.** `anf_head_pos`'s `A_WCLASS` answer is unreachable at remodel 3 (`A_WCLASS` is built after
    `pcrec_altcls`), so the `\w`-head identity requirement cannot discriminate there; the concern is real only for
    the run walk's byte-level reader, the L1 feature.
13. **The D27 witnesses' findings (lane l1d27; dispositions by lane l1ffix).** 88 witnesses answer as libpcre2 on
    both engines; 29 list LESS than the promise allows. None is in L1's stated scope; each rests on a stated limit,
    recorded per row in `tests/lookaround/d27_l1/l1d27_limits.tsv` and checked by `make test-lookaround` (a lifted
    limit turns it red):
    - F1 `domain`: a consumed class outside the run's domain (`.`, `[^z]`) is a gap, not a position, so no guard
      meets it (§5.1 "The guard"). Unlock: §10 U-descguard.
    - F2 `guard-domain`: a guard ends at its first term outside the domain. Same unlock.
    - F3 `rep-wall`: the head's REP arm is a wall until R2 (D-10). Unlock: [REPEAT-RUN] R2.
    - F4 `nested-item`: a nested positive lookaround is its own item and reaches the run only as its body's edge
      guards; its narrowing of the body stays in the body (D-1). The general rule that would lift it: meet the
      head-guard with the body's CONSUMED head run (the head column read through a nested item;
      `(?=[a-z]{2}(?<=xy))[a-z]{2}z` would state `xyz`). Not built at L1 (D77): §10 U-nesteditem, with its trigger.
    - F5 `edge-drop`: CAT-EDGE drops a leftover guard across a non-`all` neighbour (D-3), and `dead` is one-sided:
      in `(?=xy)(?=xz)\w+` the concatenation nests to the right, so `(?=xz)` meets `\w+` first and its leftover
      `z` is dropped there; `(?=xy)` then meets a consistent `x`, and the `y`/`z` contradiction is never seen. The
      general rule: guards compose ASSOCIATIVELY (two adjacent items meet each other before either meets a
      consumed neighbour). §10 U-assoc, with its trigger.
14. **UNLOCKS filed (r55 J).** Two plan rows, not scheduled: `start_set` and the k-set walk read the item
    (`(?=a)[ab]c` lists `start_set {a,b}` where `{a}` is sound); and [NEVER-MATCH]'s trigger, fired by L1 (utf8
    `x(?=\x{100})y` lists `dead` with `never_matches no`).
