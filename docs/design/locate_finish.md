# Search is LOCATE × FINISH — the model, the table, the family, and [OPT-REVEND] in it

**DESIGN NOTE, PROPOSED, REVISION 2.1, nothing built.** Revision 1: lane `locfin`,
2026-10-09, from main `525dec33` (abi 71). Revision 2: lane `locfin2`, 2026-10-09,
from main `7efca415` (`src/` identical to `525dec33`, abi 71), applying the FULL D6
panel `../dev/reviews/2026-10-09-r-locfin-panel.md` (38 ids, every ACCEPT binding);
§R2 is its disposition table and `[r2 <id>]` marks its edits. **Revision 2.1: lane
`locfin21`, 2026-10-09, from main `00ddf7d5` (`src/` identical, abi 71), applying
that review's "RE-CHECK of revision 2" (27 ids, LR-G1..G14 from lfre2 and LR-S1..S13
from lfre1, every disposition binding). Read §R2.1 first**: one row per id, and every
in-place edit carries an `[r2.1 <id>]` mark. The central change, where both critics
converge, is §2.7: the MACHINE/PATH derivation (each row declares `.needs`, the
selected path is the closure over the selected rows, membership = needs ∩ what was
built) moves INTO L0, ahead of the `dfa_matches[]` fold, and every reader of "which
machines and slots does this artifact use" reads it. Charter: D156 (Frank,
2026-10-09): *"look for the general rule to expand. We have dfa prefilter then vm
now. This is the same but the prefilter is reverse."* Nothing under `src/`, `cli/`,
`lib/`, `tests/` or `docs/spec/` changes. Evidence: `../../studies/locate_finish/`
(own CLAUDE.md; a compile-side census with FIVE controls since revision 2.1, the L0
edit set and its derived sabotage re-aims). No further panel (lfre1's
recommendation, accepted): the manager checks each fix directly.

Read before writing: D156; `where_to_start.md` §1-§3 (§2.2 step 1 is CORRECTED in
place, `[r2 E1]`, and its G4 is the closed predicate of §4.6 here, `[r2.1 LR-S5]`);
`start_table.md` rev 2.1 (§1.2-§1.6, §3.7's `fact_deny`);
the shipped code at this pin (`src/gen/emit_dfa.c` `cand_rows` `:8160`,
`cand_nodes` `:8053`, `cand_select` `:8447`, `cand_read` `:323`, `dfa_matches`
`:7706`, the three membership readers `:4438`/`:4510`/`:4568`,
`pcrec_artifact_has_dfa_scan` `:437`, `pcrec_emit_dfa_engine` `:11212`;
`src/gen/emit_vm.c`'s hybrid entry `:12703-12733`, `:13146-13426`;
`src/core/compile.c` `:227-231`, `:2381`); `revend.md` revision 2 (§R2, §0, §5.2 —
superseded here, §5.1); `litscan_k82h.md` (§1.1a, §3.1a, the rulings); `pf_know.md`
§0-§3; `../dev/walk_survey.md` K3/K4 (§7.3 here).

---

## §R2.1. What revision 2.1 changed, by re-check id

Status column: **A** = applied as the disposition reads; **A′** = applied in the
closest sound version, the reason and the evidence in the row; **F** = filed (a
candidate with a trigger, §7). Section numbers are this revision's.

### lfre2 — generality / family / unlocks

| id | status | what changed, and where |
|---|---|---|
| LR-G1 | A | FINISH is FOUR rows, `FIN1 nomatch`, `FIN2 report`, `FIN3 verify-at`, `FIN4 search-from`, each with its hat from the finisher route and its AVAILABILITY a predicate on that route's machines (`needs[route] ⊆ built`, §2.7): `verify-at` needs the anchored machine on `CR_DFA`, the attempt machine on `CR_ATTEMPT`, the VM on `CR_VM`. Rev 2's seven rows (three verify-at, two search-from) are gone. `-fno-anchored-dfa` now denies only what it removes, the anchored BUILD (`compile.c:230`, its one reader), and the `match` listing shows it on `verify-at` as a `CandList.fact_deny` (`start_table.md` §3.7's precedent, already used by `vm-anchor-bound` and `end-window`), so the listing bytes stay identical. F-11/Q7 is ONE visible cell kept for L0's no-mover proof: `verify-at`'s `take[CR_ATTEMPT]` omits `AT`. Done at L0 with the fold (§1.3, §2.3, §3.4, §5 L0). |
| LR-G2 | A | The result is `(I, e, D)`, `e` = "some match starts in `I`" (§1.2). FINISH is keyed on the existing `CT_*` bits; `NOMATCH`/`SPAN`/`ENDSET`/`LOWER`/`AT` stay as LISTING ALIASES of masks; `AT` = `CT_LOWER\|CT_UPPER` at a point, a REQUEST filter that is never degraded (§1.2, §2.2). One vocabulary inside and at the boundary. |
| LR-G3 | A′ | The body's lowering RECORDS its applied erasure set on the machine it built (`Nfa.erased`: look, atomic, count today; backref/var/Σ*-call when §7.1 adds those arms); for a body in front of a VM finisher, exact ⇔ the set is empty (§1.2). `pcrec_vm_prefilter_window`, `cand_lang_exact` and (d′) (`emit_dfa.c:7361`, through the first) read it at L0, closing the latent hole (BREF/VAR were never tested); it is a stated precondition on §7.1. **Why A′:** `RX_VM_PREFILTER_LANG` reads the record's COUNT member only at L0, byte-identically. Reading the whole set would move the stamp on the 727 superset hybrids that stamp `"exact"` today (19 bench / 708 corpus, census); that blind spot is filed as F-13, a vocabulary mover for a later abi event. The C4 wording is fixed (LR-S2). |
| LR-G4 | A | §2.7 is new: every row declares `.needs[route]` (machines F/R/A/ATT/VM and the (slot, route) cells it runs); the selected PATH is the closure over the selected rows; MEMBERSHIP = needs ∩ built (`anchored_ok` stays an input). Every reader of "which machines/slots are used" reads it (§2.7's reader table): LR-S1's three readers, the orientation block, `emit_vm.c:11330`, the eight `dfa_engine_is_empty` callers, `pcrec_artifact_has_dfa_scan`'s twelve callers, the F-9/F-10 spellings, `compile.c:229`/`:2381`, `emit_dfa.c:10713`, `cand_finish_of`, `cand_locate_route`. "Off the path ⇒ absence" is ONE generated stamp rule (§5.1), landing at L2.1, whose first absence cell IS D-2. L0's route functions are fields of the derivation; rev 2's L2.0 is absorbed into L0 and disappears. Census control C5 holds today's membership rule against the bytes: 0 / 5,355 (§3.1). |
| LR-G5 | A | `[GIVEUP-DIFF]` is no new section: `make test-axes`' GIVEUP1 relation (`tests/axes/run_axes.sh:1270-1320`, default vs each deny, an exact-key allowance) becomes DIRECTION-CHECKED from the derived classification, gains a budget-ladder arm, and gets W1's constructed witness, measured here (§1.5, §5). |
| LR-G6 | A | No REQ_WHY `"locator"`: PRESENCE is asked in BOTH stages and `u.locate.whole` selects `dominated`; REQ_WHY stays four tokens. The `dominated` disjunct and its PRESENCE → LOCATE read move from L3 to L2 (§4.3, §5 L2, §5.1). |
| LR-G7 | A | `CandSel.lroute` is dropped (no reader; its 0 default meant DFA, C11's shape) (§2.2). |
| LR-G8 | A | The match-here locator is `caller ⊓ body`: the meet, in the product, of the caller's point request and the body's STATIC verdict. On an `empty` body the meet is `∅`, so the ask is `NOMATCH`, `verify-at` is never asked, and `match_unwrapped_applies`' `!dfa_engine_is_empty` conjunct is dropped. The L0 carve-out: FIN1 lands at L2, so at L0 `search-from` (sound on every shape) takes that `NOMATCH`, today's bytes; at L2 FIN1 takes it, a named mover (53 corpus / 0 bench, §5 L2) (§1.2, §2.3, §2.7). |
| LR-G9 | A | Notes recorded: the posture split fits rev-end, relaxed-reverse and rev-inner with no new column; an UNDENIABLE row's control is the window-identity twin, its population stratified by L0's derivations and LR-G3's erasure set (§1.5, §6.2). |
| LR-G10 | A | `[START-LANDING]`'s placement is written up as a filed section that folds §7.3 in: RECOVER rows `pinned` (zero bytes of evidence), `landing` (one), `end-minus-width`, then `reverse-pass`; each hands `SPAN` to FINISH unchanged, NEUTRAL on hybrids, and R leaves the member set through §2.7 with no stamp special case. Trigger MET (walk_survey K3/K4); ranks above REVEND (50.9 vs 30.9 ms est.); utf8 needs a fixed BYTE width (§7.3). |
| LR-G11 | F | §7.6 `candidate-verify`, with its trigger. |
| LR-G12 | F | §7.7: match-here across the three routes is ONE row under LR-G1 (`verify-at`); K8's trigger. |
| LR-G13 | F | §7.8: the bounded-interval hand is `AT` with `t > s` under `search-from`'s filter; VMSEED stage 4's trigger, the entry itself BOONIES. |
| LR-G14 | F | §7.9 (BOONIES). |

### lfre1 — soundness / table fit

| id | status | what changed, and where |
|---|---|---|
| LR-S1 | A | Fixed by §2.7: `dfa_table_name`, `dfa_scan_edge_name`, `dfa_uniform_folds` fold over the path's members, never over a FINISH selection, so on a hybrid (reached through `pcrec_emit_dfa_scan_stamps`, `emit_vm.c:11330`, and the orientation block's `emit_dfa.c:10870`, which VM artifacts reach through `pcrec_emit_prologue`, `emit_vm.c:13964`) nothing asks FINISH on `CR_VM`. The brief's "`emit_vm.c:10870`" is `emit_dfa.c:10870`; the evidence is the call path just named. The three functions, `:10713` and `:11330` are in the edit set; the hybrid witness is `(a+)b` (C5: 1,231 hybrids carry F+R text and none A); a sabotage plant re-keys the readers to FINISH and must abort (§2.3, §2.7, §5 L0). |
| LR-S2 | A | C4 is relabelled PLUMBING (two readers of `Vm.mrl_win`'s conjuncts agree); the answer-level control is named before L3: E9's window-identity twin against libpcre2 10.46. The projection covers the three window-consumer sites BY CONSTRUCTION: it is computed once, at `Vm.mrl_win`'s one assignment (`emit_vm.c:10368`), and the entry (`:13396-13406`), the RETRY recompute (`:13261-13276`) and the adaptive re-seed (`:13310-13327`) all read that field (§1.2, §3.1, §5 L0, §5 L3). |
| LR-S3 | A | `ENDSET` never reaches the VM's verify-at: `FIN3`'s `take[CR_VM]` = {`SPAN`, `AT`}; struck from §1.3 and from §1.4's matrix; `ENDSET` on `CR_VM` goes to `search-from` (§1.3, §1.4, §2.3, §4.3). |
| LR-S4 | A | Both halves: the model gains the edge E-VR (`verify-at` on `CR_VM` fails → RETRY), which the shipped code has, and L3's twin counts its traversals and asserts 0 on exact hybrids (§2.5, §5 L3). |
| LR-S5 | A | G4 is a CLOSED predicate over node kinds, an exhaustive switch with no `default:`: no member of ANY `A_BREF.refs[]` in `S` names a group of `P`; `A_CALL` and `A_VAR` fail closed; a kind added later (conditionals, callouts) is a compile error at the switch. The DUPNAMES witness `(?J)(?<n>a+)X(?<n>b)?\k<n>` fails it. Stated in BOTH notes (§4.6; `where_to_start.md` §2.2, §2.4). |
| LR-S6 | A | The edit set grows from 31 to 55 entries (LR-S1's sites, `emit_vm.c:11330` and `:10368`, the F-9 spellings, the LR-G3 arms, the listing sites, the RETRY `.contract` rows) and is re-derived with `sabotage_anchors.py` at `00ddf7d5`: **8 re-aim (S140, S494, S566, S599, S606-S609), 35 rows re-run at L0, 76 after**. Names reconciled (`hand = AT`, not `BOUNDED`). The `(\w+)\1` witness is reached by the path derivation's LOCATE ask on `CR_VM` (§2.7 places it). S88/S141 (`:13405`) are re-RUN after L0, not re-aimed: the projection's record sits at its one assignment, not beside `:13405` (§5 L0). |
| LR-S7 | A | L2's inbox note names pcrec-bench's `tools/selfcheck.py` pins (read at `76e13c1d`): `"dfa_start": "reverse-pass"` at `:3705-3707` (provably-empty) and `:3729-3731` (anchored attempt), exactly L2.1's movers; the provably-empty case's `"dfa_match": "search-filter"` (`:3707`), LR-G8's L2 mover; `"dfa_scan": "unanchored"` at `:3552-3554`, a closed-vocabulary reader that does not move (`foo[0-9]+bar` has no end pin); and the adapter's closed `dfa_match` enum (`adapter.py:1011-1013`) (§5 L2). |
| LR-S8 | A | Absorbed by §2.7: F-9 is FOUR spellings (`pcrec_artifact_has_dfa_scan`, `emit_dfa.c:10713`'s `(!vm \|\| prefilter)`, `:10922`'s `dfa_body`, `compile.c:2381`), all read the path's body bit at L0; `compile.c:229` reads the derivation's NEEDS half; `-fno-anchored-dfa` is read once, at `compile.c:230`. |
| LR-S9 | A | Same as LR-S1: within L0 the derivation lands before the fold. |
| LR-S10 | A | `match_api.md §6.3.4¶2`'s "the O(n) forward+reverse table pair" is false on `pinned` artifacts today; its spec hunk is owed by L0 (drafted in §5 L0). |
| LR-S11 | A | `.contract = CG_FIXED` also on RETRY `exact`, `clamped` and `retry-anchored`, citing `emit_dfa.c:8331-8345`'s rulings; their control is the window-identity twin, not a deny differential (§1.5). |
| LR-S12 | A | The size ladder's drop rungs get a rev-end clause stated through §2.7: a rung applies only if the member set it leaves is a strict subset of the one before; under form C's T2, dropping A turns T2 into T3 and ADDS F, so `SDR_NO_ANCHORED` skips there (§5 L2). |
| LR-S13 | A | LR-G2 resolves the key; `AT`'s `I` is a request filter, never degraded; the FINISH row ids are renamed `FIN1`-`FIN4` (rev 2's F1-F7 and rev 1's F6 collided with each other and with the findings F-n) (§1.2, §2.3). |

---

## §R2. What revision 2 changed, by panel id

Status column: **A** = applied as the disposition reads; **A′** = applied in the
closest sound version, the reason and the measurement in the row; **F** = filed (a
candidate with a trigger, §7). Line numbers are this revision's sections.

### lfcrit3 — generality / simplicity / family

| id | status | what changed, and where |
|---|---|---|
| G1 | A | `CAND` and `LOWER` are ONE type; the one-try-then-re-locate vs attempt-loop difference is RE-ENTRY POLICY, which RETRY / the verifier's resume already chooses (§1.2, §1.3). Degradation: a superset locator hands `{LOWER, NOMATCH}` (§1.2). F-6 is WITHDRAWN (D156's list was right; §0 item 3, §10). `CT_CAND` survives in code only as a spelling INSIDE the composite (NEXT → VERIFIER), never on the LOCATE → FINISH boundary (§1.2). |
| G2 | A | The result type is a PRODUCT: start interval `[s, t]` × a "`s` proven" bit × an end set `D` (the priority end at `s` lies in `D`). The six types become points; totality and O1-O10 are stated on the two axes (§1.2, §1.4, §2.3). Enum spellings stay in code (§1.2's last table). The `\|D\| ≤ 2` cap is dropped. `UPPER` is mapped to the interval's `t`; `CT_WINDOW` is DELETED (accepted by VERIFIER, handed by no row) at L0 (§1.2, §5 L0). |
| G3 | A | Four finisher ACTIONS — report, nomatch, verify-at `s`, search-from `s` — each with a DFA or VM HAT chosen by the finisher's route (D124 lens 5; `CandPf.emit`/`emit_vm` precedent). The `vm-*` rows go; F6 is search-from with the VM hat entered at its loop head (§1.3, §2.3). |
| G4 | A | FINISH absorbs what exists: `cand_nodes`' VERIFIER/LOOP/CALLER are promoted into FINISH's action set (§1.3, §2.5), and `dfa_matches[]` (axis G) is FOLDED into FINISH as its verify-anchored / search-from rows for the match-here entry — the last entry-point axis outside the table, axis J's C3 precedent (§3.4). This gives FINISH a real choice and a deny (`-fno-anchored-dfa`). F-2 dissolves (§3.4, §10). |
| G5 | A | Q1 answered: FINISH is a SLOT BLOCK of `cand_rows[]`, keyed (finisher route, shape), justified by G4(b)'s real choice; one array keeps the listing per take-set, the trace's `hand` field and the typed-edge check in one walk (§2.2). Q1 is struck from §8. |
| G6 | A′ | Relocate names the route's FALLBACK LOCATE row (the last undeniable one), never "the next row in table order" (§2.5). Progress is stated as a lexicographic measure `(lo, rank)`: `lo` never falls, and on equal `lo` the target row's rank strictly rises; a same-locator re-entry (RETRY's re-seed, the VM hat's re-seek, find-all) is a separate edge class that must raise `lo` strictly. **Why A′:** "progress = strictly raised `lo`" alone is false for relocate — rev-end's tie hands `s* = lo` whenever the leftmost match begins at `search_from` itself, so on that call the strict increase can only be the rank's. The succ-graph check (C2) is the cycle check on this measure (§2.5). |
| G7 | A | Posture is TWO columns: a DERIVED classification (a join over the artifact classes a (row, route) cell covers; N/A on DFA finisher routes) and a DECLARED, checked contract (`CG_FIXED`, K82 Q10), §1.5. The declared `.giveup` classification column is deleted at L0 (it had no reader), so F-1's wrong zero value cannot recur. The independent control is a GIVE-UP DIFFERENTIAL, default vs deny over swept budgets on K82h §3.1a's 35 budget blocks plus the VM-only end-window witnesses (§1.5, §6.2), built as its own row `[GIVEUP-DIFF]` ahead of the first VM-finisher LOCATE row (§5). |
| G8 | A | A3/A4/A5 are ONE `composite` LOCATE row with a hat by route (fwd+rev on `CR_DFA`, the candidate loop with its fused verifier on `CR_ATTEMPT`, the attempt loop on `CR_VM`). `empty` and WIDTH `ceiling` are recorded as one "nothing fits → NOMATCH" family; they stay in their slots (one is static, one is a per-call width compare) and their unification is a later one-row edit (§2.4). |
| G9 | A | Stage 2's `locate-decides` is NOT a new row: PRESENCE's `dominated` (G1 of the req admission) gains a dominator through a new selection-DAG read PRESENCE → LOCATE; "LOCATE first" holds per BODY, not per artifact (§4.3). |
| G10 | A | The stamp rule cites DD-13c (§5.1); DFA_SCAN readers that use `"unanchored"` as a MACHINE proxy are classified (§5 L2, reader census); D-2's census and sabotage stay SEPARABLE inside L2 (commits L2.1 / L2.2, one abi event) so a red bisects (§5). |
| G11 | A | The stage-1 conjunct reads `cand_finish_of` (`cand_finish_of(cx) != CAND_ROUTE_VM`), not `fit.chosen` (§4.1). |
| G12 | A | L0 is cut to {LOCATE `empty`/`composite`; `cand_finish_of` replacing the ten reads; the F-3 and F-1 data corrections; the `dfa_matches[]` fold}. FINISH rows with no choice (report, nomatch, the VM hats, verify-attempt) wait for the producer that gives them one (L2/L3) (§5 L0). |
| G13 | F | §7.1, with its trigger. |
| G14 | F | §7.2-§7.5, (1)-(4) each with its trigger; (4) BOONIES-class. |

### lfcrit2 — table fit / checks / census / readers

| id | status | what changed, and where |
|---|---|---|
| C1 | A | FINISH totality is keyed on (locator route, finisher route): a hybrid's body locates on `CR_DFA`/`CR_ATTEMPT` while its finisher runs on `CR_VM` (§2.3, §2.6). The verify row is SPLIT: `verify-attempt` (`CR_ATTEMPT`, the attempt machine, always built) and `verify-anchored` (`CR_DFA`, gated on `unwrapped`, deny `-fno-anchored-dfa`) (§2.3). F-3 is NOT data-only and the revision says so: exactness is applied at the LOCATE → FINISH boundary by a derivation, `cand_lang_exact(cx)`, which reads `pcrec_vm_prefilter_window(cx)` — the very function `Vm.mrl_win` is assigned from (`emit_vm.c:10368`) and which needs only a `Ctx`, so RECOVER's `CandSel` does not need the `Vm` (§1.2, §2.5). Match-here's type is settled: the CALLER locator hands `[s, s]`, unproven, `D = ⊤` (shape `AT`, §1.2, §3.4). |
| C2 | A | The VM-route ask of LOCATE is made only by an artifact with no DFA body: `cand_locate_route(cx)` returns `CAND_ROUTE_VM` iff `!pcrec_artifact_has_dfa_scan(cx)` (§2.6), so the composite's VM arm cannot fire on a hybrid. "Next locator in table order" is gone (G6). The self-check gains a PROGRESS check on succ cycles (§2.5). |
| C3 | A | L0's re-aims are DERIVED by the start_table edit-set method: `studies/locate_finish/l0_edit_set.tsv` (31 entries) through `start_table/sabotage_anchors.py` against a call graph regenerated at this pin: **6 re-aim (S566, S599, S606-S609), 18 re-run at L0, 98 after L0**; S222 is a re-run, not a re-aim (it sits in `dfa_search_start_name`, which L0 does not touch). The `empty` decision inside the two emitters (`emit_unanchored` `:9729`, `emit_attempt` `:10094`) is in the edit set (§5 L0). |
| C4 | A | G12 defers every FINISH row with no producer, so L0 ships NO unreached row; `run_cand_oracle.sh` gains a declared-unreached allowance file (one line per row, with its argument and the commit that gives it a producer; a row in the file that IS reached fails), first used by L2's `verify-attempt` (§5 L0, L2). |
| C5 | A | L0's sabotage plan is rebuilt (§5 L0): no declared-vs-derived posture plant (circular, and the declared column is deleted); new plants for `.hand` dropped (hand mandatory on a FINISH ask; a 0 hand aborts), the verify-anchored / search-from ORDER swapped, and F-2 reverted (a grep row: no row-POINTER compare in `src/gen`). F-3's plant no longer waits on a later landing: the boundary degrade is L0's, witnessed on a superset hybrid. |
| C6 | A | REQ_WHY gains ONE token, `"locator"` (no pre-check: the selected locator is not the composite); DFA_TABLE / DFA_UNIFORM_FOLDS / DFA_SCAN_EDGE / the orientation block fold over the machines the artifact EMITS, through one membership derivation (L2.0, a no-mover) — under form C the forward machine is absent and they read the reverse (+ anchored) machines; the supersession of `revend.md` §5.2 is recorded in BOTH notes (§5.1; `revend.md` gains a forward pointer). |
| C7 | A | pcrec-bench's `testees/pcrec/adapter.py`, `pcrecbench/report.py` and `tools/selfcheck.py` are listed as READERS of DFA_SCAN/DFA_START (§5 L2); L2's deliverable includes an `[inbox]` adapter note to pcrec-bench and the window handshake. |
| C8 | A | §3.3 is corrected: the reader grep includes `pcrec_artifact_has_dfa_scan` (12 callers, `:3119`/`:3193` the `rx_info.scan`/`search_form` mirrors), `:10708` is dispositioned (it is `pcrec_artifact_has_dfa_scan` spelled locally), and the VM class is 15 lines, not 16. DFA_SCAN's machine-proxy readers join L2's reader list (§3.3, §5 L2). |
| C9 | A | Spec citations corrected: DFA_START is `match_api.md §6.3.4¶11`; the VM stamp block is `match_api.md §6.3.5`. Every DFA_SCAN value table that needs the fourth value is listed in L2's spec hunk (§5 L2). |
| C10 | A | `analyze.py` gains C4 (the exact/superset classifier vs the INDEPENDENT stamp `RX_VM_RESEED "exact"`: 759 exact / 734 superset hybrids, 0 disagreements) and a TWO-SIDED C3 (the converse holds outside two declared exceptions, both the shipped fact's own declines: 22 multibyte rows, 2 `\G`; plus a width-direction check with a declared probe-blind-call exception, 138 rows). Re-run: every existing table line unchanged (§3.1, `summary.txt`). |
| C11 | A | The PRESENCE → LOCATE read is gated on `pcrec_artifact_has_dfa_scan` (no body, no locator to defer to: the 275 end-pinned VM-only artifacts never defer) and is spelled as G9's read on `dominated` (§4.3). |
| C12 | A | `CT_WINDOW` deleted (G2); SPAN's `D` upper bound is what a VM ceiling reads (§1.2). L2 commits a declared-listing file for the new `locate` axis (`listing_declared_L2.tsv`, read by `start_table/listing_diff.py`). `nomatch` on `CR_VM` has its producers: the WIDTH ceiling's verdict and the PRESENCE verdict, both inside the composite (§2.3). |

### lfcrit1 — exactness / give-up surface

| id | status | what changed, and where |
|---|---|---|
| E1 | A | rev-inner's precondition G4 (`S` holds no reference into `P`'s groups: backreference, group condition, and conservatively `${...}`); without G4 it hands `LOWER(s*(j₀))` to the attempt loop (§4.6). `where_to_start.md` §2.2 step 1, §2.4 and §3 are CORRECTED in place with `[r2 E1]` notes. On `${...}`: a pattern variable names a CALLER value, never a group (`variables_pattern.md`), so its inclusion is conservative, not necessary; it is kept because the disposition names it and it costs nothing. |
| E2 | A | O4 is a subsequence of (start, ceiling) PAIRS, plus an explicit obligation that every ceiling is ≥ the priority end at its start (D51's unsound direction: a WRONG answer, not a posture) (§1.4). |
| E3 | A | F6's case kept (search-from VM, §2.3); its sabotage witness re-aimed to the lazy tie `(\s+?){2}$` (window compare), and the give-up hazard marked UNWITNESSED (§4.3, §5 L3). |
| E4 | A | §4.5's fold is the REFERENCE's own compare fold (ascii / latin1 under `--ucp` byte since K94 / utf8 simple fold), not "the 52-byte `cls_casefold` set" (§4.5). |
| E5 | A | relax = the UNION over `A_BREF.refs[]` (DUPNAMES) (§4.5). |
| E6 | A | Closure on the LOWERED positive set, `S ∪ fold(S)` on the bitmap/interval, never a re-parse under caseless mods (§4.5). |
| E7 | A | `A_VAR` → Σ* or decline; a recursive call inside `G_N` → Σ*; the cost gate excludes EVERY Σ* source, not only a cyclic reference (§4.5). |
| E8 | A | Relocate hands `lo` and leaves `\G` reading the caller's `search_from` (K82 Claim 2′, the handoff's mechanism); a relocate producer that cannot keep them apart declines `\G` (§1.4 O7, §2.5, §4.6). |
| E9 | — | Upheld (stage 2 NEUTRAL, 0 / 5,199,120 window diffs); cited in §4.3. |
| E10 | A | The X1 (dead-seed skip) sabotage row gets a HYBRID witness at L3 (§5 L3). |
| E11 | — | Upheld (the tie table / `dfa_matches[]`); cited in §4.2. |
| E12 | — | Upheld (§4.5 as a start bound; ONE_WAY); cited in §4.5. |

---

## 0. Answers first

1. **The model (§1).** A LOCATOR is a DFA walk named by its seed(s), its direction,
   the slice of the pattern its machine covers and that machine's LANGUAGE (exact,
   or a superset by erasure). It hands ONE result type, a product
   `(I, e, D)` **`[r2.1 LR-G2]`**: a start interval `I = [s, t]` (every match start
   ≥ `lo` lies in it), `e` = "some match starts in `I`", and an end set `D` that
   contains the priority end of the leftmost match. FINISH is keyed on the existing
   `CT_*` bits; the names `NOMATCH`, `SPAN`, `ENDSET`, `LOWER` and `AT` are listing
   aliases of masks (`AT` = `CT_LOWER|CT_UPPER` at a point, a caller's request that is
   never degraded). `CAND` is `LOWER` (`[r2 G1]`). A superset locator's result degrades
   to `{LOWER, NOMATCH}` by one lattice projection, applied where the body's lowering
   RECORDED an erasure (`[r2.1 LR-G3]`). A FINISHER is one of four rows — `nomatch`,
   `report`, `verify-at`, `search-from` — wearing the DFA or the VM hat of the route
   it runs on, its availability a predicate on that route's machines
   (`[r2.1 LR-G1]`). Obligations O1-O10 are stated on the product (§1.4); give-up
   posture is a derived classification plus a declared contract (§1.5).
2. **The table (§2).** Two new slots of the ONE `cand_rows[]` (D151 add. 3 Q2):
   `LOCATE`, a BODY slot, and `FINISH`, a slot block keyed (finisher route, hand
   mask), asked by each caller-facing entry. FINISH promotes `cand_nodes`'
   VERIFIER/LOOP/CALLER and FOLDS `dfa_matches[]`. Totality is keyed on (locator
   route, finisher route); relocate goes to the route's fallback locate row with a
   lexicographic progress measure. **`[r2.1 LR-G4]` Every row declares `.needs`**
   (machines F/R/A/ATT/VM and the (slot, route) cells it runs), and §2.7's ONE
   derivation computes the selected PATH as the closure over the selected rows:
   membership = needs ∩ what was built. Every reader of "which machines and slots
   does this artifact use" reads it, which is what fixes LR-S1 (the membership
   readers run on hybrids and must never ask FINISH there).
3. **The family (§3).** Every shipped start mechanism casts as (seed, direction,
   language) → a point of the product; the census puts every compiled artifact in
   exactly one of eleven (locator, finisher) pairs (bench 343, corpus 5,012), under
   FIVE controls, all at 0 disagreements; C5 (`[r2.1 LR-G4]`) holds today's
   machine-membership rule against the emitted bytes, 0 / 5,355 (§3.1). **No shipped
   output falls outside the product, so D156's revisit trigger does not fire.**
4. **REVEND (§4).** `rev-end` is one LOCATE row (route `CR_DFA`, predicate `end_pin`,
   deny `-fno-rev-end`, needs R); its tie arms are FINISH's `verify-at` (T2) and
   `search-from` (T3). Stage 2 (captures) is the same row with the VM hat, NEUTRAL by
   window identity, FILED on its population; under it `ENDSET` goes to `search-from`,
   never the VM's verify-at (`[r2.1 LR-S3]`). PRESENCE is asked in BOTH stages and
   reads `dominated` through the locator's `.whole` (`[r2.1 LR-G6]`). The
   relaxed-reverse locator is sound as specified: FILED. rev-inner needs the closed
   predicate G4 (`[r2.1 LR-S5]`), or it hands `LOWER` to the attempt loop.
5. **Build (§5).** L0, a no-mover: the two slots, §2.7's path derivation and its
   readers, `FIN3 verify-at` and `FIN4 search-from` (the `dfa_matches[]` fold), the
   erasure record, the data corrections and a spec hunk for `match_api.md §6.3.4¶2`
   (`[r2.1 LR-S10]`); its re-aims DERIVED from a 55-entry edit set (8 re-aim, 35
   re-run, `[r2.1 LR-S6]`). L1 = `revend.md` S0+S1. L2 = REVEND stage 1, the abi
   71 → 72 event, as two separable commits: L2.1 the GENERATED stamp rule (its first
   absence cell is D-2's `attempt-start`) and L2.2 `rev-end` with FIN1/FIN2; rev 2's
   L2.0 is absorbed into L0. `[GIVEUP-DIFF]` is GIVEUP1 made direction-checked, with a
   ladder arm and W1's witness (`[r2.1 LR-G5]`). L3-L5 FILED; `[START-LANDING]` is
   placed and filed (§7.3).
6. **Questions (§8)** restated under revision 2.1, with both critics' judgments where
   they gave one: L0's scope, stage 2, the stamp RULE, the one-way spec sentences, the
   relaxed locator's deny, rev-inner's rank after E1, and the ATTEMPT match-here form.

---

## 1. The model (D156 item (a))

### 1.1 LOCATE

A locator is a DFA walk with four parameters:

| parameter | values today and proposed |
|---|---|
| **seed** | `search_from` with every start state live (the unanchored forward scan); a candidate position (a NEXT row's hit, `hit − k`, the predecessor byte + 1); the END of a match (RECOVER); the subject end `n` and `n − 1` (REVEND); a landmark hit `j` (rev-inner); the caller's position (the match-here entry, `[r2 C1]`) |
| **direction** | forward; reverse |
| **slice** | the whole pattern; the prefix `P` of `P·L·S` (rev-inner) |
| **language** | EXACT (the capture-erased pattern, D31: the same machine, `engine_m4.md` §6.1) or a SUPERSET (lookaround → ε, atomic transparent, count collapse, and §4.5's backreference relaxation; `pf_know.md` §0: `L(P) ⊆ L(erase(P))` for every erasure `src/ir/nfa.c` performs) |

A locator may be a COMPOSITE: the shipped forward+reverse locator is the chain
WINDOW → PRESENCE → FIRST → NEXT → (VERIFIER: the forward machine) → RECOVER, every
link of which already hands a typed result (`start_table.md` §1.6). `[r2 G8]` The
three shipped composites are ONE locator with a hat by route: fwd+rev on `CR_DFA`,
the candidate loop with its fused anchored verifier on `CR_ATTEMPT`, the attempt loop
on `CR_VM`. The chain stays as it is; this note names its OUTPUT.

The match-here entry (`<prefix>_match`) has a locator too, the trivial one:
`caller`, which hands the position the caller gave (`[r2 G4(b)]`, §3.4).
**`[r2.1 LR-G8]`** It is composed with the body: the match-here entry's locator is
`caller ⊓ body`, the MEET (§1.2's order) of the caller's point request and the body
LOCATE row's STATIC verdict. Today only `empty` has one (`I = ∅` for every `lo`), so
on an `empty` body the meet is `∅` and the entry asks FINISH for `NOMATCH`; on every
other body the meet is the caller's request, `AT`. This is why `verify-at` needs no
`!dfa_engine_is_empty` conjunct: it is never asked there.

### 1.2 The result is a product `[r2 G2, r2.1 LR-G2]`

A locator hands `r = (I, e, D)`, relative to its accepted lower bound `lo`:

| component | meaning | the locator's obligation |
|---|---|---|
| `I = [s, t]` | every match start ≥ `lo` lies in `I`; `t` may be `∞` | no match starts in `[lo, s)` and none above `t`; `I = ∅` (written `s > t`) means NO match from `lo` |
| `e` | **`[r2.1 LR-G2]`** EXISTENCE: some match starts in `I` | with `I` a point `[s, s]`, `e` makes `s` the leftmost start ≥ `lo` (O1); with `t > s` it proves only that one exists |
| `D` | a set of positions that contains the PRIORITY end of the leftmost match | meaningful under `e` at a point; `D = ⊤` means "unknown" (every position ≥ `s`) |

Revision 2's bit `p` ("a match starts AT `s`") could not say "a match exists in
`[s, t]`", which `[OPT-VMSEED]` stage 4's seed window and §7.5's subset locator both
need (LR-G2); `p` is `e` at a point.

**The FINISH key is the hand's `CT_*` mask `[r2.1 LR-G2]`.** One vocabulary serves
the composite's inside and the LOCATE → FINISH boundary; rev 2's five-valued shape
key is gone and its names survive as LISTING ALIASES of masks:

| alias | `CT_*` mask | point of the product | rev 1 type | shipped producer |
|---|---|---|---|---|
| `NOMATCH` | `CT_VERDICT` | `I = ∅` | `NOMATCH` | PRESENCE / WIDTH verdicts, `empty`, `caller ⊓ empty` |
| `SPAN` | `CT_START` | `[s, s]`, `e`, `D = {e}` | `SPAN` | the composite's RECOVER (exact language) |
| `ENDSET` | `CT_START \| CT_ENDSET` | `[s, s]`, `e`, `\|D\| > 1`; **no cap on `\|D\|`** | `ENDSET` | `rev-end`'s tie (L2) |
| `LOWER` | `CT_LOWER` | `[s, ∞)`, `¬e` | `LOWER` **and** `CAND` (`[r2 G1]`) | WINDOW W1, FIRST's handoff, RETRY's re-seed, the VM-route composite, any superset locator |
| `AT` | `CT_LOWER \| CT_UPPER`, **at a point** | `[s, s]`, `¬e`: a REQUEST | (none) | the `caller` locator of the match-here entry |
| (window, filed §7.8) | `CT_LOWER \| CT_UPPER`, `t > s` | `[s, t]`, `¬e` | (none) | `[OPT-VMSEED]` stage 4 |
| (exists, filed §7.5) | `CT_LOWER \| CT_UPPER \| CT_START` | `[s, t]`, `e` | (none) | a subset locator (BOONIES) |

"At a point" is a property of the ASK, not a bit: the asker states it
(`CandSel.point`; `caller` always asks a point), and only `verify-at`'s `take` cells
read it. **`AT` is never degraded `[r2.1 LR-S13]`**: its `I` is the caller's filter
("a match starting exactly at `s`"), not a locator's claim, so the boundary
projection below never touches it; `search-from` honours it as a filter.

**`CAND` is `LOWER` `[r2 G1]`.** Their obligation cells were identical in
revision 1's matrix. "One anchored try, then re-locate" versus "an attempt loop from
`s`" is a RE-ENTRY POLICY, which RETRY already chooses. In code `CT_CAND` stays the
spelling of NEXT → VERIFIER inside the composite (an edge that never crosses the
LOCATE → FINISH boundary); at the boundary there is no `CAND`.

**Degradation is a lattice projection.** Order points by information: `r ⊑ r′`
(`r′` says no more than `r`) iff `I ⊆ I′`, `e ≥ e′` and `D ⊆ D′`; the MEET `r ⊓ r′`
is `(I ∩ I′, e ∨ e′, D ∩ D′)` where both are sound (LR-G8's composition, §1.1). A
locator over a SUPERSET language `L′ ⊇ L` hands `degrade(r) = ([s, ∞), ¬e, ⊤)`, or
`∅` unchanged: the leftmost `L′` start is ≤ the leftmost `L` start, so the lower bound
survives; nothing else does — not `e`, not `t`, not `D` (`atomic_groups_design.md`'s
122 refuting cells; the `mrl_win` gate). `NOMATCH` survives (`L ⊆ L′`). So a superset
locator hands `{LOWER, NOMATCH}`. `pf_know.md` §0 measured exactly this split.

**Where the projection is applied, and what it reads `[r2 C1, r2.1 LR-G3, LR-S2]`.**
At the LOCATE → FINISH boundary, not on a row. The composite's RECOVER hands `SPAN`
truthfully OF ITS BODY'S LANGUAGE; whether that language is `L` is a fact about the
body, and revision 2.1 makes it a RECORDED fact rather than a list of known erasures:

- **The erasure record.** `src/ir/nfa.c`'s lowering writes, into the machine it
  builds, the set of language-widening erasures it APPLIED (`Nfa.erased`: `LOOK` at
  the `A_LOOK` arm `:710`, `ATOMIC` at the `A_ATOMIC` arm `:905`, `COUNT` where the
  collapse fires `:796-799`). The arms that fail into the internal error today
  (`A_BREF`, `A_VAR`, `A_CALL` in a cycle) record `BREF`, `VAR`, `CALLSTAR` the day
  §7.1 gives them a relaxation, which is why this is §7.1's PRECONDITION: without it
  the relaxed prefilter would read EXACT (no listed erasure fires), the boundary would
  hand `SPAN`, and `mrl_win` would use a superset's window END as a ceiling, the
  atomic-groups 122-cell class.
- **The rule.** For a body in front of a VM finisher, `exact ⇔ Nfa.erased = ∅`. A body
  whose finisher is a DFA is exact by D67/SR-8's routing (any erasure that could widen
  its language forces the VM), so `cand_lang_exact(cx) = path.finish != CR_VM ||
  pcrec_vm_prefilter_window(cx)`, and `pcrec_vm_prefilter_window` becomes `fit.prefilter
  && body.erased == ∅`.
- **Its readers.** `pcrec_vm_prefilter_window` (hence `Vm.mrl_win`, `emit_vm.c:10368`),
  `cand_lang_exact`, the handoff's (d′) decline (`emit_dfa.c:7361`, through the first),
  and `RX_VM_PREFILTER_LANG` (`emit_vm.c:11239`), which at L0 reads the record's `COUNT`
  member only, byte-identically; its blind spot is F-13 (§10).
- **The no-mover obligation.** The record must reproduce today's `PF_KIND_ATOMIC` /
  `PF_KIND_LOOK` / `prefilter_collapsed` conjuncts on every hybrid. The arms are
  reached exactly where the kinds fact sees the node, by construction of both walks,
  but that is an argument; L0's gate is the emit sweep plus a direct compare of the
  two predicates over every census hybrid, and a disagreement is a finding before the
  commit lands. Two places to look first: a discharged possessive (a proven no-op
  `A_ATOMIC`) on a hybrid reads inexact under both, and reading it exact would be a
  sound MOVER, not taken (D77); and a collapsed build in which no repeat had a count to
  collapse would leave `prefilter_collapsed` true with nothing recorded (the [OPT-4.1]
  ladder gates collapse on a collapsible repeat, so this should be empty; the compare
  proves it rather than assuming it).
- **Where it is computed.** Once, at `Vm.mrl_win`'s one assignment (`emit_vm.c:10368`,
  `v->mrl_win = cand_lang_exact(cx)` on the VM route), with ONE trace record
  (`CANDTRACE BOUNDARY vm <SPAN|LOWER>`). The three consumers of the inlined body's
  window — the entry (`:13396-13406`), the RETRY recompute (`:13261-13276`) and the
  adaptive re-seed (`:13310-13327`, which reads only `window[0][0]`, the `LOWER` half)
  — all read that field, so the projection covers all three BY CONSTRUCTION
  (`[r2.1 LR-S2]`); rev 2's record at the entry alone would have covered one.

The census's C4 is PLUMBING, not a control (`[r2.1 LR-S2, LR-G3]`): `RX_VM_RESEED
"exact"` is the RETRY row whose predicate IS `Vm.mrl_win`, so C4 checks that two
readers of one derivation agree. The answer-level control is E9's window-identity
twin against libpcre2 (§6.2), named before L3. Revision 1's F-3 was right about the
effect and wrong about the fix: no RECOVER row changes; the boundary does.

**What becomes of the remaining enum bits** (all stay spellings in code):

| bit | today | in the product |
|---|---|---|
| `CT_LOWER` | WINDOW, FIRST, RETRY hands; most slots accept | `I`'s lower end; the `LOWER` key, alone |
| `CT_UPPER` | BOUND → LOOP | `I`'s upper end `t`; with `CT_LOWER`, the `AT` key (a point) and §7.8's window |
| `CT_CAND` | NEXT, RETRY hand; RETRY, VERIFIER accept | `LOWER` (G1); kept only as NEXT → VERIFIER's spelling inside the composite |
| `CT_WINDOW` | accepted by VERIFIER, handed by NO row | **deleted at L0** (`[r2 G2, C12]`); the ceiling a VM verifier reads is `e` of a `SPAN`, and O4 states its obligation |
| `CT_VERDICT` | PRESENCE / WIDTH → CALLER | `I = ∅`, the `NOMATCH` key (or "pass", the bound unchanged) |
| `CT_HIT` | PRESENCE → FIRST | inside the composite only (the gate's landmark); not a locator output |
| `CT_START` | RECOVER → CALLER | `e` at a point with `D = {e}`, the `SPAN` key |
| `CT_ENDSET` (new, L2) | — | qualifies `CT_START`: `\|D\| > 1`, the `ENDSET` key |

### 1.3 FINISH: four rows, two hats `[r2 G3, G4, r2.1 LR-G1, LR-S3]`

A finisher consumes one hand and returns the answer, or relocates. Revision 2.1 makes
the four ACTIONS the four ROWS (rev 2 had seven: three verify-at rows and two
search-from rows split by hat and machine). Each row's HAT is the finisher route's
(`path.finish`, §2.7), which is D156's "capture need" (the VM hat iff `fit.chosen ==
ENGM_VM`); its AVAILABILITY on a route is `needs[route] ⊆ built`, a predicate on that
route's machines, not a second row.

| row | `take` per route (aliases) | DFA hat (`CR_DFA` / `CR_ATTEMPT`) | VM hat (`CR_VM`) | needs per route | shipped today as |
|---|---|---|---|---|---|
| `FIN1 nomatch` | `NOMATCH` everywhere | return 0 | return 0 | — | PRESENCE / WIDTH verdicts, the empty engine (CALLER) |
| `FIN2 report` | `SPAN` on DFA / ATTEMPT; not routed on `CR_VM` (the VM must write groups ≥ 1) | return `(s, e)` | — | — | every DFA artifact's return (CALLER) |
| `FIN3 verify-at` | `CR_DFA`: `ENDSET`, `AT`; `CR_ATTEMPT`: `ENDSET` (**not `AT`: the F-11 cell**, Q7); `CR_VM`: `SPAN`, `AT` (**never `ENDSET`**, LR-S3) | the anchored run from `s`: `adfa` on `CR_DFA`, the attempt machine on `CR_ATTEMPT` | one anchored VM attempt at `s`, ceiling `e` (a `SPAN`) or `n` (an `AT`) | `CR_DFA`: A; `CR_ATTEMPT`: ATT; `CR_VM`: VM | `dfa_matches[0]` `unwrapped`; ATTEMPT's fused per-candidate run (VERIFIER); the exact hybrid's attempt at `window[0][0]`; the VM's `_match` |
| `FIN4 search-from` | `ENDSET`, `LOWER`, `AT` (point or window), and, at L0 only, the `NOMATCH` of `caller ⊓ empty` (LR-G8) | relocate: a LOCATE ask from `lo = s` (§2.5), filtered to `I` | the attempt loop from `s`; its loop head re-locates through the inlined composite where a prefilter exists; RETRY on failure | DFA, ATTEMPT: the LOCATE cell it relocates to; VM: VM, the VM entry's front (WINDOW, PRESENCE, WIDTH, FIRST, BOUND) and RETRY on `CR_VM` | `dfa_matches[1]` `search-filter`; the VM-only loop and the inexact hybrid (LOOP + RETRY) |

- **Availability, not a deny `[r2.1 LR-G1]`.** `verify-at` on `CR_DFA` is available
  where the anchored machine was BUILT (`anchored_ok`, an input). `-fno-anchored-dfa`
  denies what it removes, the build (`compile.c:230`, the flag's one reader; today the
  flag is read there AND as `dfa_matches[0]`'s deny, LR-S8's "half true"). The `match`
  listing keeps showing the flag on the `unwrapped` row as a `CandList.fact_deny`, a
  FACT's deny the listing shows and the walk never reads (`start_table.md` §3.7, the
  shape `vm-anchor-bound` and `end-window` already use), so `--list-axes`' `match`
  lines are byte-identical.
- **Why `verify-at` on `CR_VM` never takes `ENDSET` `[r2.1 LR-S3]`.** The VM hat's
  verify is NEUTRAL only when its ceiling equals the deny arm's, and on a clamped
  hybrid that ceiling is the composite's priority end, which only the composite
  computes. `max(D)` is sound (O4(ii)) but moves the (start, ceiling) pair (O4(i)), and
  `n` moves it the other way. So `ENDSET` on `CR_VM` goes to `search-from`, whose loop
  head relocates through the composite. Revision 2's §1.3 cell ("ceiling `max(D)` where
  the artifact clamps") and its matrix cell are struck; §4.3 was already right.
- **The F-11 cell.** On `CR_ATTEMPT` the attempt machine always exists, so an
  availability-only `verify-at` would take the match-here `AT` and move 20 bench / 308
  corpus `_match` bodies from `search-filter` to one anchored run. L0 is a no-mover, so
  `take[CR_ATTEMPT]` omits `AT`: ONE visible cell, deleted by Q7's row when measured.

`cand_nodes`' VERIFIER, LOOP and CALLER are not separate successors of FINISH: they
ARE its rows' actions (VERIFIER = `verify-at`, LOOP = `search-from`'s VM hat,
CALLER = `report` / `nomatch`). After L0 "verify a candidate" has ONE home. D156's
finisher list (return, anchored DFA run, VM over the span, VM search from a lower
bound) is the same four rows with the hats spelled out; the one D156 does not name,
relocate, is `search-from` with the DFA hat — shipped twice already (the K82 handoff's
`LOWER` into NEXT inside the composite, and `search-filter`).

### 1.4 The exactness obligations, on the product `[r2 G2, r2.1 LR-G2]`

- **O1 leftmost-first start.** Under `e` at a point (`I = [s, s]`; revision 2's
  `p`), `s` is the smallest start ≥ `lo` of any match of the LOCATOR's language; it
  is the answer's start iff that language is `L` (§1.2's boundary projection). PCRE2 takes the smallest start with any match;
  priority acts only among ends at that start (`revend.md` §3.1).
- **O2 end priority.** `D` contains the priority end at `s` (PCRE2's, not the
  longest). `|D| = 1` claims it; a locator that cannot see priority (a reverse walk)
  hands `ENDSET` whenever more than one end is possible, and only a finisher that
  sees priority resolves it: the anchored machine (priority-aware, K17/K18 fixed),
  the composite (search-from), or the VM.
- **O3 captures equal PCRE2's.** Only the VM hat writes groups ≥ 1, from its own
  anchored attempt, never from a locator's positions (D44.6; the DFA hat's
  dead-group fill `emit_dfa.c:1650` is a FINISH read, §3.3).
- **O4 the give-up surface `[r2 E2]`.** Let `A` be the sequence of (attempt start,
  ceiling) PAIRS the VM hat runs, and `A₀` the deny arm's. (i) `A` equals `A₀`
  (classification NEUTRAL) or is a SUBSEQUENCE of `A₀` as PAIRS, in the same order
  (ONE_WAY: a give-up may become an answer, never the reverse); anything else is
  forbidden. A pair with the same start and a different ceiling is NOT in `A₀`, so a
  looser ceiling (more steps, a possible new give-up) and a tighter one are both
  excluded by (i). (ii) Independently of posture, every ceiling either arm passes is
  ≥ the priority end at its start — D51's unsound direction. A ceiling below it is a
  WRONG ANSWER, not a posture difference: `(\s+){2}$` on `"  \n"` answers g1 (1,3)
  where PCRE2 says (2,3) (critic lfcrit1: 2,188 + 4,010 wrong of 27,884 cells under
  a control). Revision 1's "subsequence with no ceiling looser" admitted exactly
  that tighter ceiling.
- **O5 `search_from` and find-all.** A locator accepts no start below `lo` and READS
  `subject[lo − 1]` for left context (`assertions_design.md` §3.8.3.1;
  `where_to_start.md` §2.5's `lo0`/`slice` mutations). Find-all re-enters with the
  returned end; the empty-match advance is the caller's (`match_api.md` §3.1).
- **O6 utf8 boundaries.** Every `s`, every `lo` handed back, is a character start;
  the position-domain layer (K49, K50, K73, K75, `start_table.md` §2.5) applies
  unchanged. A reverse walk over a byte machine satisfies this by accepting only after
  whole characters (`revend.md` §3.6).
- **O7 views, `\G` and `\K` at the span edge `[r2 E8]`.** Left context at `s − 1` and
  right context at `e` come from the real subject. `\G` reads the CALLER's
  `search_from`, never `s` and never a relocated `lo` (`litscan_k82h.md` Claim 2′):
  relocate hands `lo` as a SCAN START, exactly as FIRST's handoff does, and leaves
  `search_from` alone; a relocate producer that cannot keep the two apart declines
  `\G`. A `\K` pattern's REPORTED start is the VM's.
- **O8 seeded walks.** A SPECULATIVE seed (`n`/`n − 1`, a landmark hit) may be DEAD
  and is tested before the first view lookup (X1); seeds must be sound for the walk's
  OWN language (§4.4).
- **O9 progress `[r2 G6]`.** Every re-entry decreases a well-founded measure:
  relocate goes to the route's fallback locate row with `lo′ ≥ lo` and a strictly
  higher rank on equal `lo`; every same-locator re-entry (E5 the retry into the
  prefilter, E7/E8 the VM hat's re-seek, find-all) raises `lo` strictly
  (`start_table.md` §1.6's per-row obligation). §2.5 states the check.
- **O10 cost.** A locator costs at most the deny arm's locator, up to a constant
  (REVEND: depth from `n` ≤ `n − lo`).

**The pair matrix.** Rows are hand keys (aliases), columns FINISH rows; a dash is a
pair FINISH never forms.

| hand ↓ / row → | `FIN2 report` | `FIN1 nomatch` | `FIN3 verify-at` | `FIN4 search-from` |
|---|---|---|---|---|
| `SPAN` | DFA: O1 O2 O5-O7 | — | VM: O1-O7, ceiling `e` (O4 NEUTRAL by window identity) | — |
| `ENDSET` | — | — | DFA only: O1 O2 O5-O8 (**`[r2.1 LR-S3]`** the VM cell is struck: `ENDSET` never reaches the VM's verify-at) | O1 O5-O9; VM: the loop head's priority end is the ceiling |
| `LOWER` | — | — | — | O3-O7 O9 (VM: O4 ONE_WAY when it skips) |
| `AT` | — | — | O1-O3 O5-O7 (DFA: `unwrapped`; VM: the VM's `_match`; not on `CR_ATTEMPT`, the F-11 cell) | DFA: O5-O7, filter `start == s` |
| `NOMATCH` | — | O5 | — | O5, at L0 only (`caller ⊓ empty`, LR-G8): the relocated search answers 0 |

### 1.5 The give-up posture: two columns `[r2 G7, r2.1 LR-G5, LR-G9, LR-S11]`

Revision 1 proposed "derive the posture from the pair". The panel showed it is not a
function of the pair: (a) W1 on `CR_VM` is NEUTRAL on an exact hybrid (the exact
prefilter skips those starts anyway) and ONE_WAY on a VM-only or count-collapsed
artifact, so a cell is a JOIN over the artifact classes it covers; (b) WIDTH
`ceiling` was declared ONE_WAY while the same-shape PRESENCE verdicts read NEUTRAL;
(c) the handoff's `CG_FIXED` is a RULED CONTRACT (K82 Q10) that a derivation would
erase; (d) a declared value checked against a derivation from the same table shares a
source; (e) on DFA finisher routes no VM runs, so posture is N/A, not NEUTRAL.

So two columns:

- **Classification (derived, never declared).** Per (row, route) cell: the JOIN, over
  the artifact classes the cell covers (exact hybrid / superset hybrid / VM-only;
  DFA finisher routes are N/A), of the class posture, where a row that removes an
  attempt the deny arm would run on that class is ONE_WAY and a row that removes none
  is NEUTRAL (join order NEUTRAL < ONE_WAY < forbidden). It is computed by an
  INSTRUMENT over the corpus (the trace build records (row, route, artifact class) per
  compile; the join is a table), not by the compiler, and nothing in `src/` declares
  it. **The `.giveup` field is deleted at L0**: its seven initializers were declared
  classification, it had no reader, and its zero value is how F-1 happened (W1 read
  NEUTRAL by default). Deleting the declaration is the F-1 correction; no zero default
  is left to be wrong.
- **Contract (declared, checked) `[r2.1 LR-S11]`.** `.contract = CG_FIXED` where a
  ruling forbids any move of the give-up surface. Today four rows carry one: FIRST's
  `handoff` (K82 Q10), and RETRY's `exact`, `clamped` and `retry-anchored`, whose
  rulings sit at `emit_dfa.c:8331-8345` (`exact`: nothing may make an exact hybrid's
  retry adaptive, its window END is live; `clamped`: a step block would ADD attempts,
  so an answer could become a give-up; `retry-anchored`: the choice does not exist,
  the retry is never reached). An unset contract is a wildcard (memory
  `pcrec-no-silent-defaults`). The CHECK is behavioural (below), not a comparison of
  two columns.
- **The independent control: GIVEUP1, direction-checked `[r2 G7, r2.1 LR-G5]`.**
  Revision 2 proposed a new `[GIVEUP-DIFF]` section. Most of it exists: `make
  test-axes`' GIVEUP1 relation (`tests/axes/run_axes.sh:1270-1320`) already compiles
  the whole corpus default vs each deny and FAILS on any case where exactly one side
  gives up, unless an exact `(axis, file:line)` key is in `GIVEUP1_ALLOWANCE`. It
  ignores DIRECTION. So `[GIVEUP-DIFF]` is three additions to it, no new section:
  1. **Direction from the derived classification.** An allowance key is admissible
     only in the direction the row's classification permits: ONE_WAY admits "default
     answers, deny gives up" and the converse is a failure whether or not a key names
     it; NEUTRAL and FIXED rows admit no key at all.
  2. **A budget-ladder arm.** The witnesses below run at a swept ladder of step and
     work budgets (`budget` directives, ~19 points, E3's shape), default vs deny, with
     the same direction rule per budget point.
  3. **Witnesses per ONE_WAY row**: K82h §3.1a's 35 budget / `gu` blocks, the VM-only
     end-window witnesses (T6a's 13 start-unanchored), and one constructed witness per
     ONE_WAY row. F-1's PRESENCE half is already witnessed (64 `-fno-req-byte` keys,
     22 `-fno-start-set`); **W1's is constructed and measured here** (lane locfin21,
     this tree, gcc 15.2, python `re` as the span oracle): `(\w|\w\w)x$` with
     `--engine=vm --step-budget=50` on `"ab" × 600 + "abx"` answers `(1200, 1203)` by
     default (W1 stamps `RX_END_WINDOW "4"`) and gives up (`PCREC_ERR_STEPS`) under
     `-fno-end-window`; python `re` agrees on the span. That is the ONE_WAY direction.
     Without `--engine=vm` the same pattern is an exact hybrid and both arms answer
     (W1 NEUTRAL there), which is the classification's join in miniature.
  It reads ANSWERS, so it shares no source with the table. It must exist before the
  first VM-finisher LOCATE row (L3, L4, L5).
- **Undeniable rows `[r2.1 LR-G9, LR-S11]`.** A row with no deny (RETRY `exact`,
  `clamped`, `retry-anchored`; `rev-end`'s stage-2 VM hat; FINISH's rows) has no deny
  arm to differ from, so its control is the WINDOW-IDENTITY twin (E9's: the walk's or
  the row's window against the shipped prefilter's, every string to length 6-7 at every
  `lo`, then libpcre2), its population STRATIFIED by L0's derivations (`path.finish`,
  `path.locate`, the member set) and by LR-G3's erasure set, so a class the corpus does
  not populate is visible as an empty stratum rather than averaged away.

**Classification of today's rows** (by the rule; the instrument confirms):
W1 `window` ONE_WAY (VM-only and collapsed classes covered; witness above);
PRESENCE `set-leads` / `emitted` ONE_WAY on `CR_VM`; `presence-none`, `one-attempt`,
`dominated` NEUTRAL (no check emitted); WIDTH `ceiling` ONE_WAY; NEXT `first-class`
ONE_WAY; BOUND `vm-anchored`/`vm-gstart` ONE_WAY; RETRY `adaptive*` ONE_WAY,
`exact`/`clamped`/`retry-anchored`/`fixed` NEUTRAL (the first three with contract FIXED);
FIRST `handoff` NEUTRAL on its population (every hybrid mover's prefilter is `exact`,
K82h §3.1a) with contract FIXED. LR-G9's note: rev-end (NEUTRAL on hybrids by window
identity), the relaxed-reverse locator (ONE_WAY) and rev-inner (ONE_WAY on the VM)
each fill this classification with no new column.

**Where to attack §1.** (a) A shipped or filed locator whose output is not a point
of the product. (b) The boundary projection: a body whose `cand_lang_exact` is true
but whose RECOVER span is not `L`'s — an `src/ir/nfa.c` arm that widens the language
without recording it in `Nfa.erased` (`[r2.1 LR-G3]`). (c) O4(ii): a VM verify-at
ceiling that is not `e` of a `SPAN` or `n`. (d) The progress measure (O9): a relocate
whose target rank does not exceed the handing row's. (e) §1.5's classification rule
on a row that both adds and removes attempts. (f) The meet `caller ⊓ body`
(`[r2.1 LR-G8]`): a body with a static verdict other than `empty`'s.

---

## 2. Mapping onto the start table (D156 item (b))

### 2.1 What the eight slots are in this frame

They are the INSIDE of the composite locator: WINDOW (`LOWER`), PRESENCE (`NOMATCH`
or pass), WIDTH (`NOMATCH`), FIRST (`LOWER`), NEXT (`LOWER`, spelled `CT_CAND`),
RECOVER (`SPAN` from an end), BOUND (the interval's `t`) and RETRY (the VM hat's
re-entry). None moves. What the table lacks is (i) a place to choose BETWEEN
locators, which REVEND is the first to need, and (ii) the finisher choice, which today
is spread over ten `fit.chosen` reads (§3.3) and one table outside `cand_rows[]`
(`dfa_matches[]`, §3.4).

### 2.2 Two new slots, in the one array `[r2 G5, r2.1 LR-G2, LR-G7]`

**FINISH is a SLOT BLOCK of `cand_rows[]`** (D151 addendum 3, Q2: "otherwise logic is
spread around"). The panel answered revision 1's Q1 with G4(b): FINISH already has a
real first-match choice with a deny — `dfa_matches[]` — so it is a table in its own
right, and the one array keeps its listing (per take-set), its trace record (with the
`hand` field) and its typed edges in the walk and the self-check that already exist;
a separate array would duplicate the walk, the listing projection and the trace, and
split the typed-edge check across two arrays.

| slot | the question | asked at | routes | accepts / hands |
|---|---|---|---|---|
| `LOCATE` (first) | which walk produces the result? | each DFA-shaped body, once (the entry body AND the hybrid's inlined `<p>_prefilter`, both via `pcrec_emit_dfa_engine`), on the body's route; an artifact with NO DFA body, once, on `CR_VM` (`cand_locate_route`, §2.6) | `CR_DFA`, `CR_ATTEMPT`, `CR_VM` | accepts `LOWER` (E1, and relocate); hands its declared `CT_*` masks to FINISH across the boundary projection |
| `FINISH` (last) | which row, in which hat, finishes this hand? | each caller-facing entry, once per hand its locator can give: `<prefix>_search` (hands from LOCATE), `<prefix>_match`/`_match_caps` (`AT`, or `NOMATCH` where `caller ⊓ body` is empty) | `CR_DFA`, `CR_ATTEMPT` (DFA hat), `CR_VM` (VM hat) | accepts `CT_*` hand masks; hands to the CALLER, relocates to LOCATE |

`CandSel` gains `hand` (the `CT_*` mask being finished) and `point` (the ask is a
point request, §1.2), and FINISH rows declare a `take` cell PER ROUTE
(`u.finish.take[route]`, a set of masks, `.list[route]`'s shape) **`[r2.1 LR-G2,
LR-S3]`**; `cand_select` keeps a FINISH row on route `r` iff `s->hand` is one of
`take[r]` (and, for the `AT` mask, iff `s->point`), exactly as it filters the route.
Per-route take cells are where a hat's limits live as data: `verify-at`'s `CR_VM` cell
omits `ENDSET` (LR-S3) and its `CR_ATTEMPT` cell omits `AT` (F-11). **`hand` is
MANDATORY on a FINISH ask**: a FINISH ask with `hand == 0` aborts (a check, not a
default), and no other slot reads it (`[r2 C5]`). **`[r2.1 LR-G7]`** Revision 2's
`CandSel.lroute` is dropped: no predicate read it, and its zero value meant
`CR_DFA`, the shape C11 found in `cand_route_of`'s default.

### 2.3 The FINISH table (design of record), totality on (locator route, finisher route) `[r2 C1, r2.1 LR-G1, LR-S1, LR-S3, LR-S13]`

First match per (finisher route, hand). Four rows, ids `FIN1`-`FIN4` (revision 2's
F1-F7 are retired: they collided with rev 1's F6 and with the findings F-n, LR-S13).
Rows marked L0 exist at L0 (the `dfa_matches[]` fold); the others land with the
producer that gives them a choice.

| # | row | routes | `take[route]` (aliases) | needs[route] (§2.7) | availability | listing | lands |
|---|---|---|---|---|---|---|---|
| `FIN1` | `nomatch` | all | `NOMATCH` | — | always | — | L2 |
| `FIN2` | `report` | DFA, ATTEMPT | `SPAN` | — | always | — | L2 |
| `FIN3` | `verify-at` | DFA, ATTEMPT, VM | DFA: `ENDSET`, `AT`; ATTEMPT: `ENDSET` (F-11 cell); VM: `SPAN`, `AT` (LR-S3) | DFA: A; ATTEMPT: ATT; VM: VM | `needs[route] ⊆ built` (on `CR_DFA`: `anchored_ok`; elsewhere always) | `match` 1 `unwrapped`, `fact_deny` = `PCREC_NO_ANCHORED_DFA` | **L0** (`AT` on DFA); `ENDSET` at L2; VM cells at L3 |
| `FIN4` | `search-from` | all | `ENDSET`, `LOWER`, `AT` (point or window); at L0 also `NOMATCH` (LR-G8) | DFA, ATTEMPT: the LOCATE cell it relocates to (§2.5); VM: VM and the VM entry's front and RETRY on `CR_VM` | always | `match` 2 `search-filter` | **L0** (`AT`, `NOMATCH` on DFA/ATTEMPT); the rest at L2/L3 |

The `match` listing is the rows' `.list[CR_DFA]` projection with the descriptions
moved beside the rows verbatim from `src/dump/axes_dump.c:135-136`, so
`--list-axes`' two `match` lines are byte-identical, the deny column included
(`fact_deny`, §1.3).

**Why `FIN3` does not take `AT` on `CR_ATTEMPT` (and the finding behind it).** On
`CR_ATTEMPT` the match-here entry is `search-filter` today (`anchored_ok` is never set
on ENG_ATTEMPT: `build_anchored_dfa` is called only on the ENG_UNANCH branch,
`compile.c:2540`), so an ATTEMPT artifact's `_match` runs the WHOLE search from `s` and
discards a later start — O(n) on a failing call where one anchored run of the attempt
machine would answer. Taking `AT` there is a real improvement and a MOVER (308 corpus /
20 bench `DFA_MATCH "search-filter"` artifacts change form; answers identical), which
is `anchored_match_unwrapped.md` §10's filed "ENG_ATTEMPT's own match-here form" and,
with LR-G12, one row across three routes (§7.7). L0 is a no-mover, so the cell omits
`AT`; §8 Q7 carries the mover.

**Totality** is checked on the triples that occur, not on (route, type):

| locator route → finisher route | who | hands the locators can give (after the boundary projection) | last row taking each |
|---|---|---|---|
| `CR_DFA` → `CR_DFA` | DFA artifact, ENG_UNANCH | `SPAN`, `NOMATCH`; `ENDSET` (rev-end, L2) | `FIN2`, `FIN1`, `FIN4` |
| `CR_ATTEMPT` → `CR_ATTEMPT` | DFA artifact, ENG_ATTEMPT | `SPAN`, `NOMATCH` | `FIN2`, `FIN1` |
| `caller ⊓ body` → `CR_DFA` / `CR_ATTEMPT` | the match-here entry | `AT`; `NOMATCH` on an `empty` body (LR-G8) | `FIN4`, `FIN4` at L0 (`FIN1` from L2) |
| `CR_DFA` / `CR_ATTEMPT` → `CR_VM` | the hybrid | `SPAN` (exact body), `LOWER` (superset body, projected), `NOMATCH`; `ENDSET` (stage 2) | `FIN3`, `FIN4`, `FIN1`, `FIN4` |
| `CR_VM` → `CR_VM` | VM-only | `LOWER`, `NOMATCH` (the WIDTH / PRESENCE verdicts inside the composite, `[r2 C12]`) | `FIN4`, `FIN1` |
| `caller` → `CR_VM` (L3) | a VM artifact's match-here | `AT` (`FIN3` selected) | `FIN4` |

The self-check's totality test ("every asked (slot, route) ends in an undeniable
`cand_always` row") is extended through `.needs` (§2.7): for every (locator route,
finisher route) pair whose asker exists and every hand some LOCATE row on that locator
route gives (projected where `cand_lang_exact` can be false on that pair), the last
FINISH row on the finisher route taking that hand is undeniable and AVAILABLE BY
CONSTRUCTION there: its `needs[route]` lies inside the machines that route always
builds (DFA: F, R; ATTEMPT: ATT; VM: VM). `FIN3` on `CR_DFA` is not (A is built only
under `anchored_ok`), which is why `FIN4` follows it. A later LOCATE row that hands a
mask no FINISH row takes fails the self-check, not the compile. The declared-unreached
allowance (`cand_oracle_unreached.tsv`, `[r2 C4]`) is keyed on the (row, route, hand)
CELL, since rows no longer split by hat: its first entry is (`verify-at`,
`CR_ATTEMPT`, `ENDSET`), with its argument (no `ENDSET` producer on `CR_ATTEMPT`
until a reverse machine exists there), at L2.

**The FINISH askers, and which readers are NOT askers `[r2.1 LR-S1]`.** Revision 2
said "at L0 the only FINISH asker is the match-here entry". That was false: the three
machine-membership readers (`dfa_table_name` `:4438`, `dfa_scan_edge_name` `:4510`,
`dfa_uniform_folds` `:4568`) call `dfa_match_is_unwrapped` today, and they run on
HYBRIDS (through `pcrec_emit_dfa_scan_stamps`, `emit_vm.c:11330`, and the
orientation block's `emit_dfa.c:10870`, reached through `pcrec_emit_prologue` at
`emit_vm.c:13964`). Re-keyed to `cand_finish_of`, which is `CR_VM` on a hybrid, they
would have asked FINISH for `AT` on `CR_VM`, where no row exists at L0: a NO-ROW
selection on every forward+reverse hybrid (C5: 1,231 artifacts, 39 bench / 1,192
corpus, e.g. `(a+)b`). Under §2.7 they are not askers at all: they fold over the
path's MEMBERS. The askers at L0 are exactly:

- §2.7's derivation, for the match-here entry when `path.finish ≠ CR_VM` (one ask, hand
  `AT`, or `NOMATCH` on an `empty` body);
- the `_match` emission (`emit_dfa.c:11588`, `dfa_match_is_unwrapped`) and the
  `RX_DFA_MATCH` stamp and `rx_info.match_form` (`dfa_match_name`, `:3145`), all three
  DFA-artifact-only, reading the derivation's recorded selection.

Until L2, RECOVER keeps CALLER as its successor and the search entry asks no FINISH
row; the VM entry asks at L3.

### 2.4 The LOCATE table `[r2 G8, G12, r2.1 LR-G4]`

| # | row | routes | deny | predicate | hands | needs (§2.7) | lands |
|---|---|---|---|---|---|---|---|
| A1 | `empty` | DFA, ATTEMPT | — | `dfa_engine_is_empty`'s old body | `NOMATCH` (static: every `lo`) | no machine; PRESENCE (`.whole`) | **L0** |
| A2 | `rev-end` | DFA | `PCREC_NO_REV_END` | `end_pin ≠ NONE` ∧ the stage-1 conjunct (§4.1) | `SPAN`, `NOMATCH`, `ENDSET` iff `nl_last` | R; RECOVER (seeded at `n`, `n − 1`); PRESENCE (`.whole`) | L2 |
| — | `rev-inner[-bounded]` | DFA, VM | its own | G1 ∧ G2 ∧ G3, and G4 for `SPAN`-producing hats (§4.6) | `SPAN`/`NOMATCH`, or `LOWER` without G4 | R of `P`'s prefix machine | filed (D151) |
| — | `rev-end-relaxed` | VM | its own | §4.5's gate | `LOWER`, `NOMATCH` | the relaxed reverse machine | filed |
| A3 | `composite` | DFA, ATTEMPT, VM | — | always | by route: fwd+rev (`SPAN`/`NOMATCH`), candidate loop with fused verify (`SPAN`/`NOMATCH`), the VM attempt loop's front (`LOWER`/`NOMATCH`) | DFA: F, NEXT, RECOVER; ATTEMPT: ATT, NEXT, BOUND; VM: VM, NEXT, BOUND; on every route the ENTRY slots where this row runs the entry's front (§2.7) | **L0** |

**`empty` is the first PATH-CHANGING locator `[r2.1 LR-G4]`** (`rev-end` is the
second, `[START-LANDING]`'s rows the third and fourth, §7.3): selecting it takes F, R
and the composite's slots off the path, which is what the eight
`dfa_engine_is_empty` callers have each been spelling by hand (§2.7's reader table).
`empty` and WIDTH `ceiling` are one "nothing fits → NOMATCH" family (G8): the first is
a static verdict on the body's language, the second a per-call comparison of the
remaining subject with the root minimum width. They stay in their slots at L0; the
family is recorded so that a third member is a one-row edit, not a third spelling.

**The route is NOT a projection of LOCATE.** The route (`cand_route_of`,
`job->engine`) says which MACHINES the compile built; LOCATE says which WALK over
them the search uses, and §2.7 says which of the built machines that walk USES. Today
each route has one walk (A3's three hats; A1 a special case on two); `rev-end` is the
first second walk on a route.

### 2.5 What changes in the handoff graph `[r2 G4, G6, C2, C12, r2.1 LR-S4, LR-G8]`

- **Nodes.** `LOCATE` and `FINISH` join `cand_nodes[]`. VERIFIER, LOOP and CALLER
  stay as NODES inside the composite (NEXT → VERIFIER, BOUND → LOOP, PRESENCE/WIDTH
  → CALLER for the in-composite verdict) — they are the same actions FINISH's rows
  emit, and FINISH's rows NAME them as their action (`u.finish.act` ∈ {REPORT,
  NOMATCH, VERIFY, SEARCH}). VERIFIER's accept set loses `CT_WINDOW`.
- **E-LF** LOCATE → FINISH, typed by the LOCATE row's hand masks, through the boundary
  projection (§1.2). At L2 RECOVER's successor becomes FINISH (the composite's output
  crosses the boundary there); at L0 it keeps CALLER and LOCATE's successors are the
  composite's entry (WINDOW, `LOWER`) and CALLER (`empty`'s `NOMATCH`).
  PRESENCE/WIDTH keep CALLER for the in-composite verdict.
- **E-FL** `search-from` → LOCATE, from a LOCATE row's hand: RELOCATE. Target: the
  FALLBACK row of the finisher's locator route — the last undeniable LOCATE row on it
  that is available by construction, today always `composite` — never "the next row in
  table order" (`[r2 G6, C2]`). `lo := s`; `\G` keeps the caller's `search_from`
  (`[r2 E8]`). Progress class `RANK`.
- **E-FC `[r2.1 LR-G8]`** `search-from` → LOCATE, from the `caller` locator: the
  match-here entry's search is the SEARCH ENTRY's own LOCATE ask from `lo = s`,
  filtered to `start == s` — whatever that ask selects (`composite` today; `rev-end`
  on an L2 artifact whose anchored machine was not built), not the fallback row.
  Revision 2 called the folded `search-filter` "a relocate from `caller` to
  `composite`"; on an `empty` body `_match` wraps the `empty` body, and on a `rev-end`
  body it would wrap the walk, so the target is the entry's selection. It cannot
  cycle: `caller` is not a LOCATE row and nothing re-enters it (progress class
  `ENTRY`, one traversal per call).
- **E-FR** `search-from` (VM hat) → RETRY: a failed attempt; today's E7/E8, renamed.
- **E-VR `[r2.1 LR-S4]`** `verify-at` (VM hat) → RETRY: a FAILED verify of a `SPAN`.
  The shipped code has it (the RETRY slot's `exact` row runs after the hybrid's attempt
  at `window[0][0]` fails), revision 2's model did not. On an exact hybrid the edge
  should be unreachable (the window is the match), so L3's window-identity twin counts
  its traversals and asserts 0 on exact hybrids; a nonzero count is a finding against
  `cand_lang_exact`, not noise. Progress class `RAISE` (RETRY's re-seed raises `lo`).
- **The progress check `[r2 C2, G6]`.** Each re-entry edge carries a progress class:
  `RANK` (relocate: the target row's rank exceeds the handing row's on the same
  locator route; a relocate whose handing row IS the fallback row is a self-check
  failure), `RAISE` (`lo` strictly increases: E5, E7, E8, E11, E-VR, find-all) or
  `ENTRY` (E-FC). The self-check computes, over the row-level graph (LOCATE rows ×
  FINISH rows × the composite's internal re-entries), that removing every `RAISE`
  edge leaves the graph ACYCLIC, and that every `RANK` edge satisfies its rank
  inequality.
- **`revend.md`'s E13 (WINDOW → CALLER) stays withdrawn**: REVEND's result travels
  E-LF.
- **E6** (the hybrid's prefilter → the VM loop) is E-LF on an inlined body:
  LOCATE (on `CR_DFA`/`CR_ATTEMPT`) → FINISH (on `CR_VM`), the same edge as the
  DFA-only artifact's with a different hat — D156's "REVEND with captures is
  reverse-from-end × the same finisher".

### 2.6 Routes, X4, and the hybrid `[r2 C1, C2, r2.1 LR-G4]`

The three route derivations are FIELDS of §2.7's one derivation, not three functions
with their own reads:

- `cand_route_of(cx)` (shipped): the BODY's route, `CR_ATTEMPT` iff ENG_ATTEMPT, else
  `CR_DFA`. An INPUT to the derivation (`job->engine`), meaningful only where a DFA
  body exists.
- `cand_locate_route(cx)` = `cand_path_of(cx)->locate` (new, L0): the body route where
  `path.body`, else `CAND_ROUTE_VM`. The route LOCATE is asked on by the search entry.
  It keeps `composite`'s VM arm off hybrids (`[r2 C2]`): a hybrid asks LOCATE once,
  from its inlined body, on the body's route.
- `cand_finish_of(cx)` = `cand_path_of(cx)->finish` (new, L0): the body route where
  `fit.chosen == ENGM_DFA`, else `CAND_ROUTE_VM`. The finisher's route: "is the
  finisher a DFA finisher on this entry?", the one question the ten reads of §3.3 ask.

X4 required REVEND's row to be route-independent because WINDOW is an ENTRY slot. As
a LOCATE row the question changes: LOCATE is a BODY slot, asked once per body on that
body's route, and `rev-end`'s route mask is `CR_DFA` because only an ENG_UNANCH body
has a reverse machine. Its predicate reads no `s->route` (bar the stage-1 conjunct),
so the inlined prefilter of a hybrid ASKS LOCATE on `CR_DFA` exactly as a DFA-only
body does, and FINISH, keyed on the finisher route, decides whether the result goes
to the caller or the VM.

### 2.7 The PATH derivation: what the selected rows use `[r2.1 LR-G4, LR-S1, LR-S8, LR-S9, LR-G8]`

**The finding.** F-9, F-10, the `empty` off-path conjuncts (eight `dfa_engine_is_empty`
callers), `pcrec_artifact_has_dfa_scan`'s twelve callers, the four spellings of
"does a DFA body exist", `cand_finish_of`, and §5.1's per-stamp edits are ONE family:
each asks which machines and which slots the SELECTED path uses. `empty` is the first
locator that changes the path, `rev-end` the second, `[START-LANDING]`'s rows the third
and fourth. Revision 2 left the family dispersed and put one piece of it (L2.0's
`dfa_machines_of`) AFTER the fold; that order is what made LR-S1's blocker possible,
since the fold re-keys readers that are membership questions to a FINISH selection.

**The declaration.** Every `cand_rows[]` row declares `.needs[route]`, beside
`.list[route]`: the MACHINES its emitter runs on that route (a mask over F = the
forward machine `job->dfa`, R = `job->rdfa`, A = `job->adfa`, ATT = the attempt
machine, VM = the VM program) and the (slot, route) CELLS its emitter asks. A row's
needs are what its emitter RUNS, not what it might: `reverse-pass` needs R, `pinned`
needs nothing, `verify-at` needs A on `CR_DFA`, `search-from` needs the LOCATE cell it
relocates to. The ENTRY slots (WINDOW, PRESENCE, FIRST; WIDTH and BOUND on `CR_VM`)
are needed by the row that runs the entry's FRONT: on a DFA-finisher artifact the
selected LOCATE row (`composite` runs all three, `empty` and `rev-end` only PRESENCE,
which their `.whole` answers), on a VM-finisher artifact the VM hat (`FIN3`/`FIN4` on
`CR_VM`, the code at `emit_vm.c:13146-13165`) — which is exactly today's entry gate
(`emit_dfa.c:9784`, `:10083`, "is the body the entry?"), read from here. The L0 build
lane writes the cells from the emitters as they stand; the controls below hold them.

**The closure.** `cand_path_of(cx)`, one function, memoized per compile (the facts
layer's shape), computes:

| field | what it is | from |
|---|---|---|
| `body` | a DFA-shaped body is emitted | `fit.chosen == ENGM_DFA ∨ fit.prefilter` — the condition `compile.c:2381` builds under, now spelled ONCE |
| `locate`, `finish` | the two route fields of §2.6 | `body`, `fit.chosen`, `cand_route_of` |
| `built` | the machines the compile built | `body` (F, R on ENG_UNANCH; ATT on ENG_ATTEMPT), `anchored_ok` (A), `fit.chosen == ENGM_VM` (VM) |
| `needs`, `asks` | the union of `.needs` over the SELECTED closure | the roots below, then every selected row's cells, each asked on its route, visited once per (slot, route) |
| members | `needs ∩ built` | — |

The ROOTS are the entries the artifact emits:

1. the search entry's LOCATE ask on `locate` (on a DFA-finisher artifact the selected
   row also runs the entry's front: `composite` WINDOW, PRESENCE, FIRST; `empty` and
   `rev-end` PRESENCE only);
2. on `finish = CR_VM`, the VM search entry, which IS `FIN4`'s VM hat (§1.3): its needs
   are `FIN4.needs[CR_VM]` (VM; the front WINDOW, PRESENCE, WIDTH, FIRST, BOUND and
   RETRY on `CR_VM`) although no FINISH ask selects `FIN4` on `CR_VM` before L3;
3. the match-here entry: on `finish ≠ CR_VM` its FINISH ask, with hand `caller ⊓ body`
   (`AT`, or `NOMATCH` on a body whose selected LOCATE row is `empty`, LR-G8); on
   `finish = CR_VM` the VM's own `_match`, which is `FIN3`'s VM hat (VM), until L3
   routes it through the table.

Because the closure follows `cand_nodes`' finite graph and visits each (slot, route)
once, it terminates; because it evaluates the same
`cand_select` the emitters call, it cannot disagree with them about a selection.
In the trace build `needs ⊆ built` is asserted: a selected row needing an unbuilt
machine is a defect, never a silent intersection.

**The NEEDS half, before the build.** `compile.c:229` (`build_anchored_dfa`'s
`fit.chosen != ENGM_DFA` return) decides whether A is built before any selection
exists. It reads the static half of the same declarations: A is built iff some FINISH
row routed on `finish` declares A in `needs[finish]` — today only `verify-at` on
`CR_DFA`, so the answer equals `fit.chosen == ENGM_DFA` on the ENG_UNANCH branch it is
called from, byte for byte. `-fno-anchored-dfa` stays where it is (`compile.c:230`),
now its only reader (`[r2.1 LR-G1, LR-S8]`). `compile.c:2381` reads `body`.

**Every reader, and what it reads at L0** (each is in the edit set, §5 L0):

| reader | today | at L0 |
|---|---|---|
| `dfa_table_name` `:4438`, `dfa_scan_edge_name` `:4510`, `dfa_uniform_folds` `:4568` (F-10) | "forward always, reverse unless pinned, anchored iff `dfa_match_is_unwrapped`", with `dfa_engine_is_empty` and `CR_ATTEMPT` early returns | fold over members ∩ {F, R, A}; the empty set gives `"none"` / 0, which is what the early returns spelled; NEVER a FINISH selection (LR-S1) |
| the orientation block (`emit_dfa.c:10704-10713`, its table paragraph `:10870`) (F-10's fourth spelling) | `vm`, `prefilter`, `(!vm \|\| prefilter) && dfa_search_is_pinned` | `finish`, `body`, and RECOVER's selected row where RECOVER is asked; the table paragraph reads `dfa_table_name` |
| `emit_vm.c:11330` | `pcrec_artifact_has_dfa_scan` gate on the hybrid's DFA stamps | `body` |
| `pcrec_artifact_has_dfa_scan` `:437` (F-9) and its twelve callers (`:1094`, `:1362`, `:1492`, `:1501`, `:1505`, `:3119`, `:3193`, `:6972`, `:7049`, `:7102`, `:7355`, `emit_vm.c:11330`) | the condition, copied verbatim from `compile.c` (its own comment says so) | the function returns `body`; the callers are untouched. Two of them ask a PATH question under a body spelling (`:7355`'s handoff, `:7049`/`:7102`'s NEXT scan reads): `:7355` moves to "F or ATT is a member" at L0 (same value: it already conjoins `!empty`); the rest keep `body`, and the ones whose answer would differ under a path-changing locator are re-read when `rev-end` lands (L2.2's reader census) |
| `emit_dfa.c:10922` `dfa_body`, `compile.c:2381` (F-9's third and fourth spellings) | `chosen != VM \|\| prefilter` | `body` |
| `compile.c:229` | `fit.chosen != ENGM_DFA` | the NEEDS half (above) |
| the eight `dfa_engine_is_empty` callers | each spells "is the composite on the path?" | `:4440`, `:4512`, `:4573` become the member fold; `:7355` (handoff) the member read; `:7703` (`match_unwrapped_applies`) is DROPPED by LR-G8; `:7895` (`start_pinned_applies`' P4) reads "RECOVER is asked on the path"; `:10094` (`emit_attempt`'s empty arm) moves into the `empty` row's emitter; `:11325` (`dfa_scan_name`) reads the LOCATE row's listed name. `dfa_engine_is_empty` itself becomes "LOCATE selected `empty`" |
| `cand_finish_of`, `cand_locate_route` | new | fields |
| the ten FINISH reads of §3.3 | `fit.chosen` | `finish` |

**What it absorbs.** Revision 2's L2.0 (`dfa_machines_of`, a no-mover at L2) is this
derivation's member fold, moved into L0 ahead of the fold and generalized; L2.0
disappears (§5). F-9's four spellings become one field; F-10's four become one fold.

**The stamp rule is generated from it, at L2.1 `[r2.1 LR-G4]`.** "A slot's stamp
reads its slot's selection where the slot is asked on the path, and the slot's ABSENCE
value where it is not" is ONE function over `cand_list_stamp`'s slot → stamp table
(`emit_dfa.c:8789`) plus an absence column, reading `asks`. At L0 every stamp keeps
its current derivation (no mover); L2.1 switches the slot stamps to the generated
rule, and its first movers are exactly D-2's (`RX_DFA_START` on every artifact whose
path asks no RECOVER: T8, 37 bench / 606 corpus) plus F-12's (`RX_END_WINDOW` on an
`empty` body with a finite end window, 0 measured, §10). §5.1.

**The controls.** Neither shares a source with the `.needs` declarations:

- **C5, membership vs the bytes** (census, measured at this pin): the member rule the
  three readers spell today, read off the stamps, against which machine identifier
  families (`rx_forward_`, `rx_reverse_`, `rx_anchored_`) the emitted C carries, every
  compiled artifact, hybrids included: **0 disagreements over 5,355**, with 1,231
  forward+reverse hybrids carrying F and R and none A (§3.1). At L0 the build lane
  swaps the stamp side for the derivation's own member set and keeps the text side.
- **The trace vs `asks`.** The C1 selection trace records every (slot, route) the
  emitters asked; at L0 it must contain `asks` exactly, plus a DECLARED set of
  stamp-only asks, written from the L0 trace itself (it holds at least RECOVER on
  `CR_ATTEMPT` and on `empty` bodies, which today's `RX_DFA_START` asks for its value);
  L2.1's generated rule empties that set, after which the two are equal.

**Where to attack §2.** (a) Does `cand_select`'s first-match per (slot, route)
extend to (slot, route, hand) without a second walk? (`take[route]` is a filter like
the route mask.) (b) The inlined body is called from three places (entry, RETRY's
recompute, the adaptive re-seed, `emit_vm.c:13261-13327`, `:13396`); a walk there must
answer the same at every call (§4.3). (c) Totality over the triple table: a (locator
route, finisher route) pair missing from it. (d) The progress check on a relocate
from a FUTURE second fallback (a route with two undeniable rows). (e) §2.7: a reader
of "which machines/slots" the table above misses, or a `.needs` cell that is not what
its emitter runs (the trace control's job). (f) The NEEDS half: a future row that
needs A on a route other than `CR_DFA`.

---

## 3. The family survey (D156 item (c))

### 3.1 Today's pairs, measured (`studies/locate_finish/results/summary.txt`)

Population: every bench export (367; 343 compile) and every `.rxt` pattern block
(5,431; 5,012 compile, 4,191 distinct), `src` at `525dec33` (= `7efca415`), each
compiled as its own testee/block does. **Five controls `[r2 C10, r2.1 LR-G4]`**, the
script exiting 1 on any disagreement; four share no source with what they check, and
C4 is relabelled PLUMBING (`[r2.1 LR-S2]`):

| control | checks | against | result |
|---|---|---|---|
| C1 | the reverse-machine stamp | the emitted text (any `rx_reverse_` identifier) | 0 / 5,355 |
| C2 | the hybrid stamp | the text (`rx_prefilter(`) | 0 / 5,355 |
| C3 (two-sided, `[r2 C10]`) | forward: shipped `end_window` numeric ⇒ the borrowed probe (a copy of `ew_walk`) pins; converse: probe pinned ∧ width finite ⇒ shipped numeric | `src/facts/endwin.c` vs the probe | forward 0 / 400 (+ width direction: 262 agree, 138 a DECLARED probe-blind exception — the probe never expands calls, e.g. `^(a\|b)\g<1>$`); converse 0 disagreements outside two DECLARED exceptions that are the shipped fact's own declines: 22 multibyte rows (16 distinct, e.g. `^.{5}$` utf8), 2 `\G` (`\G\z`, `\G$`) |
| C4 (`[r2 C10]`; PLUMBING since `[r2.1 LR-S2, LR-G3]`) | the census's exact / superset hybrid classifier (`RX_VM_PREFILTER_LANG` + the `kinds` fact's atomic / lookaround bits) | the stamp `RX_VM_RESEED == "exact"` (the RETRY row whose predicate is `Vm.mrl_win`) | 759 exact / 734 superset, 0 disagreements; superset rows stamp `adaptive` 466, `clamped` 173, `anchored` 58, `adaptive-dense` 37; non-exact reasons: language 7, atomic 250, lookaround 515. **Not independent**: `Vm.mrl_win` is `pcrec_vm_prefilter_window`, whose conjuncts are the same kinds and collapse facts the classifier's stamps come from, so C4 shows two readers of one derivation agree, not that the derivation is right. The answer-level control is E9's window-identity twin against libpcre2 (§6.2), named before L3 |
| C5 (new, `[r2.1 LR-G4, LR-S1]`) | the machine-MEMBERSHIP rule the three membership readers spell today ("forward always, reverse unless `pinned`, anchored iff `unwrapped`", nothing on `attempt`/`empty`), read off the stamps | which of `rx_forward_` / `rx_reverse_` / `rx_anchored_` the emitted C carries | **0 / 5,355**: DFA `unanchored` FRA 2,383, FR 42, FA 243, F 3; `attempt` 328 and `empty` 53 with none; hybrids FR 1,231 and none 262 (never A: LR-S1's population); VM-only 810 with none. The membership §2.7's derivation must reproduce |

The re-run (lane locfin2) moved no existing table line; only the control blocks were
added. The second re-run (lane locfin21, main `00ddf7d5`, `src` identical) added two
TEXT columns (`t_fwd`, `t_anch`) and C5; every pre-existing cell of all 5,798 rows is
byte-identical (compared column by column) and every other summary line is unchanged.
The pair names below are revision 2's finisher spellings: `report` = `FIN2`,
`nomatch` = `FIN1`, `verify-vm` = `FIN3` on `CR_VM`, `search-vm` = `FIN4` on `CR_VM`.

| today's pair (T1) | bench | corpus (distinct) |
|---|---:|---:|
| `composite`/fwd-rev × report | 233 | 2,192 (1,768) |
| `composite`/fwd-rev, RECOVER `pinned` × report | 15 | 231 (192) |
| `composite`/candidate loop × report (verify fused) | 20 | 308 (237) |
| `empty` × nomatch | 0 | 53 (47) |
| `composite`/VM × search-vm (VM-only) | 19 | 791 (668) |
| hybrid fwd-rev × verify-vm (exact) | 17 | 571 (497) |
| hybrid fwd-rev × search-vm (superset, projected) | 22 | 621 (585) |
| hybrid candidate loop × verify-vm | 14 | 145 (115) |
| hybrid candidate loop × search-vm | 3 | 82 (66) |
| hybrid `empty` × verify-vm / search-vm | 0 / 0 | 12 / 6 |
| hybrid `pinned` (either) | 0 | 0 |

Every compiled artifact is in exactly one row (`census.py classify` is total by
construction). The census's own column names (`L-candloop × F-anch-dfa`,
`F-vm-span`, `F-vm-cand`) are revision 1's spellings; the mapping is one-to-one.

### 3.2 Every shipped start mechanism as (seed, direction, language) → a point

| mechanism | seed | dir. | language / slice | hands (shape) | a row today? | in this design |
|---|---|---|---|---|---|---|
| the forward+reverse pass (ENG_UNANCH) | `search_from`, all starts live | fwd, then rev from the end | exact, whole | `SPAN` | the route + RECOVER S2 | `composite` / DFA hat |
| `pinned` ([OPT-5]) | `search_from` | fwd | exact, whole | `SPAN` (`s = search_from`) | RECOVER S1 | inside `composite` |
| ENG_ATTEMPT | each candidate ≤ `start_max` | fwd, anchored | exact, whole | `SPAN` (the verify is fused) | the route + N12/B1/B2 | `composite` / ATTEMPT hat |
| the empty engine | — | — | — | `NOMATCH` | `dfa_engine_is_empty` (inline, twice) | LOCATE `empty` |
| hybrid prefilter, exact | as above | as above | capture-erased = `L` | `SPAN` | route class + `mrl_win` | `composite` × `FIN3` (VM hat) |
| hybrid prefilter, superset | as above | as above | `L′ ⊋ L` (an erasure RECORDED, `[r2.1 LR-G3]`) | `SPAN` of `L′`, projected to `LOWER` | route class + `mrl_win` | `composite` × `FIN4` (VM hat) |
| K82 handoff | the gate's run hit `c` | arithmetic | — | `LOWER = max(lo, c − K)` | FIRST F1 | inside `composite` |
| offset-k / run-pinned | the rarest offset's hit | arithmetic | — | `LOWER` (`hit − k`, spelled `CT_CAND`) | NEXT N1-N4 | inside `composite` |
| START-SET DFA / VM hat | a byte in `S` | — | — | `LOWER` | NEXT N5/N6, N7 | inside `composite` |
| memchr / byte-class | `s0`'s escape set | — | — | `LOWER` | NEXT N8-N11 | inside `composite` |
| pred-memchr (ATTEMPT) | the predecessor byte | — | — | `LOWER` (hit + 1) | NEXT N12 | inside `composite` |
| W1 end window | `n` | arithmetic | — | `LOWER` (`n − maxw − eps`) | WINDOW W1 | inside `composite` |
| H1 width ceiling | — | — | — | `NOMATCH` | WIDTH H1 | inside `composite` (the "nothing fits" family) |
| PRESENCE pre-checks, K65/K66 | the landmark scan | fwd | — | `NOMATCH` / pass (+`HIT`) | PRESENCE P1-P5 | inside `composite` |
| BOUND | — | — | — | the interval's `t` | BOUND B1-B5 | inside `composite` |
| RECOVER reverse pass | the forward pass's end | rev | exact, whole | `SPAN` given the end | RECOVER S2 | inside `composite` |
| RETRY | the failed attempt + K49 | — | — | `LOWER` (re-locate or step: policy) | RETRY R1-R6 | `FIN4`/`FIN3` (VM hat)'s re-entry (E-FR, E-VR) |
| the match-here entry | the caller's position | — | — | `AT` (`NOMATCH` on an `empty` body) | `dfa_matches[]` (axis G) | `caller ⊓ body` × `FIN3` / `FIN4` |
| [OPT-REVEND] (L2) | `n`, `n − 1` | rev | exact, whole | `SPAN`/`ENDSET`/`NOMATCH` | — | LOCATE `rev-end` |
| rev-inner (filed) | landmark hits `j` | rev | exact, prefix `P` | `SPAN`/`NOMATCH` under G4, else `LOWER` | — | LOCATE (§4.6) |
| relaxed reverse (filed) | `n`, `n − 1` | rev | `L′ ⊇ L` (§4.5) | `LOWER`, `NOMATCH` | — | LOCATE (§4.5) |

**Which output is not a point of the product: none.** D156's trigger does not fire.

### 3.3 Where the FINISH decision is spelled today `[r2 C8, r2.1 LR-G4, LR-S8]`

`studies/locate_finish/finish_sites.sh` lists every CODE line under `src/gen/` that
tests `fit.chosen`, `fit.prefilter` or `prefn`: 32 lines. Revision 2 added the
`pcrec_artifact_has_dfa_scan` callers; revision 2.1 adds the two `src/core/compile.c`
spellings the `src/gen/` grep cannot see (`:229`, `:2381`, LR-S8) and dispositions
every line to a field of §2.7's derivation:

| class | lines | what they decide | after L0 |
|---|---|---|---|
| **FINISH reads** ("is the finisher a DFA finisher on this entry?") | `emit_dfa.c:1650` (the dead-group fill), `:1728` (the startpos guard on the caller-facing body), `:3145` (`rx_info.match_form`), `:9768`, `:9769` (trace), `:9784` (`emit_unanchored`'s entry gate), `:10068`, `:10070` (trace), `:10083` (`emit_attempt`'s), `:10707` (`vm`, the orientation block); `compile.c:229` (whether A is built) | 11 lines, 7 decisions, one question | read `path.finish`; `compile.c:229` reads the NEEDS half (§2.7) |
| **"does a DFA body exist"** (F-9: `pcrec_artifact_has_dfa_scan` and its 12 callers, plus three local spellings) | `emit_dfa.c:439` (the definition), `:1094`, `:1362`, `:1492`/`:1501`/`:1505` (PRESENCE's gate need and its trace), `:6972`, `:7049`, `:7102`, `:7355`; the `rx_info.scan`/`prefilter` mirror `:3119` and the `search_form` mirror `:3193`; `emit_vm.c:11330` (the hybrid's DFA stamps); the local spellings `emit_dfa.c:10708`/`:10713` (`(!vm \|\| prefilter)`), `:10922` (`dfa_body`) and `compile.c:2381` (the build condition itself) | the existence of a LOCATE ask on a DFA route | every spelling reads `path.body` at L0 (`:10922` and `compile.c:2381` move into L0 with LR-G4); `:7355` reads the member set (§2.7's table) |
| **machine membership** (F-10) | `dfa_table_name` `:4438`, `dfa_scan_edge_name` `:4510`, `dfa_uniform_folds` `:4568`, the orientation block's table paragraph `:10870` | which machines' tables the stamps and the prose fold over | the member fold (§2.7), never a FINISH selection (LR-S1) |
| route-class reads inside predicates (start_table §2.3's third axis) | `:6847` (N7), `:7155`, `:7159` (P2), `:7360` (F1's (d′)) | stay (not FINISH) | unchanged |
| the VM finisher's locator calls and exactness | `emit_vm.c:3645` (`mrl_win`, the body's language), `:11071`, `:11182`, `:11218` (stamps, the RETRY plan), `:12703-12733` (emit the inlined locator), `:13261-13327` (RETRY's re-locate), `:13393-13404` (the entry's locate call, E6) | **15 lines** that ARE the VM hat's implementation | unchanged at L0, except that `pcrec_vm_prefilter_window` (`:3643`) reads the erasure record (LR-G3) and `Vm.mrl_win`'s assignment (`:10368`) becomes the projection's one site (LR-S2) |

So the finisher choice is one question asked at seven decisions in three files, "does a
body exist" is spelled four ways, and the membership rule four ways. L0 gives each
ONE home, a field of one derivation.

### 3.4 The ≥3 rule, and the `dfa_matches[]` fold `[r2 G4, C1, r2.1 LR-G1, LR-G8]`

FINISH's shipped members (report, nomatch, verify-at in three hats, search-from in
two) are all dispersed; the house rule (memory `pcrec-forest-for-trees`) asks for the
unified table at three, and §2.3 is that table. **`dfa_matches[]` IS FINISH's existing
first-match block** and folds in: the match-here entry's locator is `caller ⊓ body`,
its hand `AT = ([s, s], ¬e, ⊤)` (or `NOMATCH` on an `empty` body), and its two rows
become `FIN3 verify-at` on `CR_DFA` (the anchored machine; available iff A was built;
`match_unwrapped_applies` loses its `!dfa_engine_is_empty` conjunct, LR-G8, and keeps
`anchored_ok` as the availability read) and `FIN4 search-from` (the search entry's own
LOCATE ask from `s`, filtered to `start == s`, E-FC). `-fno-anchored-dfa` is no longer
a row deny: it removes the anchored BUILD and the listing shows it as `fact_deny`
(§1.3). Axis J's C3 precedent (`dfa_search_starts[]` deleted into RECOVER's rows) is
the shape: the table goes, its rows stay, the `--list-axes` `match` axis is the rows'
`list[route]` projection with identical bytes, and `<PREFIX>_DFA_MATCH` /
`rx_info.match_form` read the selected row's listed name. **F-2 dissolves**:
`dfa_match_is_unwrapped` (`emit_dfa.c:7727`) compared the selected row's POINTER to
`&dfa_matches[0]`; after the fold it reads `u.finish.act == CAND_FIN_VERIFY`, and its
only remaining caller is the `_match` dispatch (`:11588`).

**Where to attack §3.** (a) C5 says today's membership rule matches the bytes on
every artifact; is there a machine a reader folds over that has no identifier family of
its own (a future representation, as `[CC-DIFF]`'s uniform fold once was for C1)?
(b) §3.3's dispositions: a FINISH or body read the greps still miss (outside
`src/gen/` and `compile.c`). (c) The fold: does any reader compare `dfa_match_name` to
a string outside the two stamps?

---

## 4. REVEND in this frame (D156 item (d))

### 4.1 The locator row `[r2 G11, r2.1 LR-G4, LR-G6]`

```
{ .c = { "rev-end", PCREC_NO_REV_END, cand_rev_end_applies },
  .slot = CAND_SLOT_LOCATE, .routes = CR_DFA, .tok = "rev-end",
  .map = CM_EXACTREV, .hands = CT_START | CT_VERDICT | CT_ENDSET /* ENDSET iff nl_last */,
  .list = { [CAND_ROUTE_DFA] = { "locate", 1, "rev-end", PCREC_NO_REV_END } },
  .needs = { [CAND_ROUTE_DFA] = { .mach = M_R,
             .asks = ASK(CAND_SLOT_PRESENCE) | ASK(CAND_SLOT_RECOVER) } },
  .desc = "...end_pin...", .u.locate = { .walk = CAND_WALK_REV_END, .whole = true } }

static bool cand_rev_end_applies(const CandSel *s)
{
    if (pcrec_fact_end_pin(s->cx) == PCREC_EPIN_NONE) return false;  /* R1 */
    return cand_finish_of(s->cx) != CAND_ROUTE_VM;                     /* stage-1 conjunct */
}
```

(`.needs`' spelling is the build lane's; `M_R`/`ASK()` stand for §2.7's machine mask
and (slot, route) cells.) **`[r2.1 LR-G4]` What `.needs` says here.** The walk runs the
reverse machine only, so on a form-C artifact (T1/T2) F leaves the member set and the
three membership readers fold over R (plus A under T2) with no stamp special case;
RECOVER is ASKED (the walk is RECOVER's reverse block seeded at `n`, `n − 1`,
`revend.md` §8's helper), so `RX_DFA_START` reads `"reverse-pass"` truthfully through
the selection; WINDOW, FIRST and NEXT are not asked, so the L2.1 stamp rule gives
their stamps the absence value. **`[r2.1 LR-G6]` PRESENCE is asked in this stage
too**: `.whole` makes `req_dominated_applies` select `dominated` (§4.3's disjunct,
which now lands with this row at L2, not with stage 2), so `RX_REQ_WHY` reads
`"dominated"` where `REQ_BYTE ≠ "none"` — "the scan already tests it", true of the
walk — and REQ_WHY stays four tokens.

`revend.md` §2.3's four conjuncts: R1 is the predicate; R2 (`cand_route_of ==
CAND_ROUTE_DFA`) is the route mask `CR_DFA`; R4 (`!dfa_engine_is_empty`, X11) is row
order (`empty` precedes `rev-end`); R3 (`fit.chosen == ENGM_DFA`) is the ONE
remaining conjunct, now a read of `cand_finish_of` = `path.finish` (`[r2 G11, r2.1
LR-G4]`: it is one of the reads §3.3 centralizes), and exactly stage 2's switch. X3's assertion (RECOVER never
`pinned` under `end_pin`) stays at the walk's emission and is measured too (census
T4: 0 / 5,012). The emitted walk is `revend.md` §5.1's text; the helper is §8's.

### 4.2 The tie table is FINISH

| `revend.md` | here |
|---|---|
| T1 `no-tie` (`\z`, or `nl_last` false) | the row's hand set omits `ENDSET`: FINISH is asked for `SPAN`/`NOMATCH` only (`FIN2`, `FIN1`) and no tie code is emitted |
| T2 `anchored` (`DFA_MATCH "unwrapped"`) | `FIN3 verify-at` on `ENDSET` (DFA hat, A) — the same row the match-here entry selects, now with a second hand |
| T3 `body` (`"search-filter"`) | `FIN4 search-from` on `ENDSET`: relocate (E-FL) to `composite` from `s*`, which puts F and the composite's slots back on the path |

`nl_last` stays as `revend.md` defines it (on the BUILT reverse machine); it decides
the hand set, so it is a LOCATE-row property, and its sabotage row (revend §9.2 row
10) is unchanged. E11 upheld this table (18 form-C twins, 0 / 1,682,892 cells, 0 vs
libpcre2).

### 4.3 Stage 2: the same locator with the VM hat `[r2 G9, C11, E3, r2.1 LR-S3, LR-G6]`

**What it is.** Drop the stage-1 conjunct. The hybrid's inlined `<p>_prefilter` asks
LOCATE on `CR_DFA` and selects `rev-end` exactly where a DFA-only body would; the VM
entry asks FINISH on `CR_VM` and gets `FIN3 verify-at` (`SPAN`) or `FIN4 search-from`
(`ENDSET` — never the VM's verify-at, `[r2.1 LR-S3]` — and the projected `LOWER`). The reverse tables are already there (census T2:
39 bench / 1,192 corpus `P-fwdrev` hybrids; C1 confirms by text).

**Its classification is NEUTRAL** (correcting `revend.md` §3.9's ONE_WAY), and E9
upheld it as the round's best-evidenced result: walk vs shipped prefilter on 48
hybrids (exact, clamped, ties, views, `\K`, `-i`, supersets, collapsed, X1, utf8),
every string to length 6-7 at every `lo`: 0 / 5,199,120 window diffs, 0 capture
diffs, 0 / 4,565,716 vs libpcre2, 0 / 719,283 find-all, ASan clean. The argument
stays: the inlined body is the DFA emitter's output for the capture-erased pattern
(STRUCTURAL), the walk's span equals that body's on every call (MEASURED), so the
VM's (start, ceiling) pairs are the same (O4(i) equality), PROVIDED an `ENDSET` on a
CLAMPED hybrid goes to `FIN4` (whose loop head relocates through the composite for
the priority end) and not to the VM's verify-at with `max(D)`: a looser ceiling
prunes less (O4(i) excludes the pair), while never being wrong (O4(ii) holds for
`max(D)`). Revision 2.1 makes this a TAKE cell, not a rule a predicate must
remember: `verify-at`'s `take[CR_VM]` has no `ENDSET` (§2.3).

**`[r2 E3]` The search-from-not-verify-at hazard is ARGUED, not witnessed.** The named witnesses are
greedy, where `max(D)` IS the priority end (0 / 27,884 differ). Only a LAZY tie
moves the window: `(\s+?){2}$` moves it on 2,188-3,282 cells with captures equal and
the give-up threshold equal over 19 budgets × 5 lengths. So the L3 sabotage row's
witness is re-aimed to `(\s+?){2}$` and detected by the window-identity twin
(`window[0][1]` compare), and the give-up hazard is recorded as UNWITNESSED: the
rule stands on O4(i)'s pair equality, not on an observed give-up.

**PRESENCE defers through `dominated`, not a new row, in BOTH stages `[r2 G9, C11,
r2.1 LR-G6]`.** The disjunct lands with `rev-end` at L2 (stage 1, §4.1); stage 2 only
widens where it is read. On the hybrid
the VM entry runs W1, then the PRESENCE pre-check (an O(n) `memchr`), then FIRST,
then calls the prefilter (`emit_vm.c:13146`, `:13165`, `:13396`), and the pre-check
would eat the walk's win (X7's finding). Revision 1 added a row `locate-decides`.
G9: that IS the existing `dominated` (G1) — "the scan already tests it" — with a
new dominator. So `req_dominated_applies` gains one disjunct: the body's LOCATE row
declares it answers presence itself (`u.locate.whole`, true on `rev-end`), read
through `cand_read` on a new selection-DAG edge PRESENCE → LOCATE, **gated on
`pcrec_artifact_has_dfa_scan`** (`[r2 C11]`): with no body there is no locator to
defer to, and `cand_route_of` would otherwise default to DFA on the 275 end-pinned
VM-only artifacts. PRESENCE is an ENTRY slot (`cand_hit_every`: its choice must not
depend on the asking route), and the new read is route-independent because it reads
the BODY's LOCATE on `cand_route_of`, whatever route PRESENCE was asked on. "LOCATE
first" therefore holds per BODY, not per artifact (G9): the entry still asks WINDOW
and PRESENCE before calling the body. FIRST's handoff declines through its existing
PRESENCE read. W1 and H1 stay (O(1), they only raise `lo`).

**Population and verdict.** 0 bench / 13 corpus (T5: 12 exact, 1 superset; 11 already
W1-bounded; the 2 unbounded `(a\z)+` and `(a+)$` are correctness witnesses). The 15
bench / 192 corpus end-pinned hybrids that exist are ENG_ATTEMPT (`^...$` validators,
nothing to locate). **Leaning: FILED** with `revend.md`'s trigger; §8 Q2.

### 4.4 O8 for superset languages: does an erasure keep the end pin?

Unchanged from revision 1 (the panel upheld it, E10): the walk seeds only at `n`/`n −
1`, sound for `L′` only if every `L′` match ends there, and each erasure `src/ir/nfa.c`
applies maps a pinned tree to a pinned language — lookaround → ε (`ew_walk` returns no
pin from a lookaround's interior; a zero-width factor is transparent in `A_CAT`),
atomic → transparent, count collapse `X{m,n}` → `X{min(m,1),}` (`A_REP` pins only for
`rmin ≥ 1`), §4.5's relaxation and a call's Σ* (an `A_BREF`/`A_CALL` at an
alternative's END is not pinned by `ew_walk` at all). Argument, not measurement; L3's
window-identity twin measures it, and E10 found X1 load-bearing on stage 2 too (four
lookaround shapes SEGV without the dead-seed skip), so the X1 sabotage row gets a
hybrid witness (§5 L3).

### 4.5 The backreference relaxed-reverse locator `[r2 E4-E7]`

**Where its reverse machine comes from.** A new erasure arm, for the REVERSE machine
only: `A_BREF` lowers to `relax(refs) = ⋃_{N ∈ A_BREF.refs[]} relax(G_N)`
**`[r2 E5]`** — the UNION over every group the reference can name (DUPNAMES `(?J)`
makes `refs[]` a set: `(?J)(?:(?<n>a)|(?<n>b))\k<n>$` on `"xbb"` matches (1,3), and
relaxing the first member only rejects it). `relax(G_N)` is the group's sub-tree with
its views and lookarounds erased to ε and atomicity transparent, and where the
REFERENCE is caseless its positive class sets closed under **the reference's own
compare fold** **`[r2 E4]`** — the fold the emitted `bref_match_caseless` applies:
ASCII under plain byte mode, LATIN-1 under `--ucp` byte (since K94: `(\xe9)(?i)\1$`
`--ucp` on `"\xe9\xc9"` matches (0,2), which the ASCII-closed relaxation rejects), and
the utf8 simple (1:1) fold under utf8 — never "the 52-byte `cls_casefold` set", which
was stale. **The closure is taken on the LOWERED positive set `[r2 E6]`**: `S ∪
fold(S)` on the bitmap / interval set the class already lowered to, never by
re-lowering a copy of the sub-tree under caseless mods (that folds BEFORE negation
and SHRINKS a negated class: `([^b])(?i)\1$` on `"BB"`). Nested references and calls
inside `G_N` are relaxed recursively while the reference graph is acyclic. **Σ*
sources `[r2 E7]`:** a reference inside its own group (cyclic), a RECURSIVE CALL inside
`G_N` (the call's Σ*, `subroutines_design.md` §8.3), and an `A_VAR` `${v}` (a caller
value has no relaxation at all: Σ* or decline). `src/ir/nfa.c`'s `A_BREF` arm keeps
its internal error in every OTHER mode, so `select_engine.c`'s `backref` prefilter
decline (`:667`) is untouched: this machine is never a forward prefilter (that is §7.1's
candidate).

**Soundness: `L(P) ⊆ L(relax(P))`.** The bytes a backreference matches are a
per-code-point case variant (under the reference's fold) of the bytes SOME `G_N` in
`refs[]` matched in its own context; that path is a path of `relax(G_N)` (erasing a
view admits every path it admitted, a transparent atomic every path the atomic did,
the fold closure every case variant), so it is in the union. An unset group makes the
reference FAIL, which removes strings. A group in a loop is referenced at its last
iteration's capture, still a string `G_N` matched. **It is not the erasure
`select_engine.c:877-886` measured unsound** (that one kept the assertions in the
copy: `(\ba)\1` → `(\ba)\ba`); E12 upheld this with the true closure: 0 violations
over 3,000 generated patterns (~1.08M checks, byte and UCP), while `:877`'s
assertion-keeping copy gives 117.

**Shape and finisher.** `LOWER = s*′` or `NOMATCH`, to `FIN4 search-from`, VM hat (the VM-only
attempt loop from `s*′`, its START-SET hat and BOUND unchanged), not one walk per
failed attempt (each re-walk from `n` costs O(n − lo)).

**Classification: ONE_WAY** (attempts below `s*′` are skipped, each fails since `L ⊆
L′`; from `s*′` on the pairs are the deny arm's): D148 Q6's sentence. E12 upheld the
direction.

**Cost (O10) and the gate `[r2 E7]`.** The walk reads ≤ `n − lo` bytes, bounded by the
VM's own work on an end-pinned match. Where the relaxation contains Σ* the walk does
not die and `s*′ = lo`: pure overhead. So the gate excludes EVERY Σ* source (cyclic
reference, recursive call in `G_N`, `A_VAR`), not only the cyclic reference.

**Population (census T6):** 275 end-pinned VM-only corpus artifacts, 255
start-anchored; start-unanchored 13 distinct, of which 7 carry a backreference and are
unbounded, all corpus correctness witnesses; bench 0. **FILED (D77)**; trigger: a
bench or real-world end-pinned backreference cell that pays the VM's attempt loop.

### 4.6 `[ENG-TACTICS]` reverse-inner: a LOCATE row `[r2 E1, E8, r2.1 LR-S5]`

- **Slot LOCATE, not NEXT** (correcting `start_table.md` §4.1's placement; F-5). A NEXT
  row hands a candidate into the composite, whose RECOVER walks back for the start;
  rev-inner already HAS the start `s*(j)` and needs the END and a verdict.
- **Precondition G4 `[r2 E1]`, and what it buys.** `where_to_start.md` §2.2 step 1 is
  CORRECTED in place: the per-occurrence tactic ("verify at `s*(j)`; on failure move to
  the next occurrence") is UNSOUND when `S` references a group of `P`, because the
  capture `P` makes depends on `s`, so the verify at `s*(j)` can fail while a larger
  `s ∈ starts(j)` succeeds. `(a+)X\1` on `"aaXa"`: libpcre2 (1,4), the tactic
  NOMATCH; a second witness returns a LATER match; 82 wrong / 82,903 over the 1,199
  gated cases with a backreference in `S` (lfcrit1), the study's 0 / 129,222 having
  counted too few of them (K35).
- **G4 is a CLOSED predicate over node kinds `[r2.1 LR-S5]`.** Revision 2 stated G4 as
  a list ("no backreference or group condition into `P`'s groups"). lfre1 found the
  list's natural reading wrong under DUPNAMES: in `(?J)(?<n>a+)X(?<n>b)?\k<n>`
  (libpcre2 on `"aaXa"`: (1,4)) the reference's `refs[]` = {1, 2} spans `P` (group 1)
  AND `S` (group 2), so a G4 that asks "is the reference into `S`?" passes and the
  per-occurrence verify answers NOMATCH. G4 is therefore one function, an EXHAUSTIVE
  switch over `AKind` with no `default:` (the house rule, `mrl.c:18-24`: a kind added
  later is a COMPILE ERROR at the switch, which is the alarm a list cannot raise), run
  over every node of `S`, with `groups(P)` the capture numbers `P` defines:
  - PASS, reading no capture state: `A_CLASS`, `A_WCLASS`, `A_EMPTY`, `A_BOL`, `A_EOL`,
    `A_END`, `A_CTX`, `A_GSTART` (`\G`'s own reference point is O7's question, not
    G4's), `A_KRESET`;
  - RECURSE into the children: `A_CAT`, `A_ALT`, `A_REP`, `A_CAP` (a group IN `S` is
    written, not read), `A_ATOMIC`, `A_LOOK`;
  - `A_BREF`: pass iff NO member of `refs[]` is in `groups(P)` — `refs[]` read as the
    SET it is (DUPNAMES), every member, never the first;
  - FAIL CLOSED: `A_CALL` (a called body inherits the caller's captures, so a
    reference inside it can read `P`'s groups; refinable later by recursing into the
    callee with a cycle guard, not needed today), `A_VAR` (conservative: a variable
    names a caller value, never a group, `variables_pattern.md`; kept because it
    costs nothing);
  - not built today, and FAIL CLOSED when built: group conditions (`(?(1)...)`) and
    callouts. Neither has a node kind, so neither reaches the switch; whichever lands
    adds its `case` there, and the compiler refuses to build until it does.
  The same predicate, word for word, is `where_to_start.md` §2.2's G4 and §2.4's gate
  row. So:
  - **under G4**: the row hands, per occurrence, a proven `SPAN` (DFA hat: `FIN3
    verify-at` from `s*`; VM hat: `FIN3`'s one anchored attempt) or moves on —
    revision 1's design;
  - **without G4**: the row hands `LOWER(s*(j₀))`, `j₀` the first occurrence with a
    non-empty `starts`, to `FIN4 search-from` (VM or DFA hat) — the attempt loop from
    there. `starts(j)` depends on `P` alone, so step 2's monotonicity still makes it a
    sound lower bound; the critic's `lowerbound` form measured 0 wrong.
  This is the VM-route population §3 of that note was built for
  (`\b(\w+)=[^&]*&(?:[^&]*&)*\1=`, `(\w+) \1`): it gets a lower bound, not a
  candidate per occurrence (§8 Q6).
- **Row:** `rev-inner-bounded` then `rev-inner` (views first), routes `CR_DFA` and
  `CR_VM`, after `rev-end` and before `composite`; predicate G1 ∧ G2 ∧ G3, with G4
  choosing the hand set; seed = each landmark hit `j`; reverse over the PREFIX
  machine (`revend.md` §8's helper; a landmark seed is speculative, X1).
- **Give-up hand-off:** where the forward-verify guard trips (`where_to_start.md`
  §2.7), `FIN4 search-from` relocates `s*` as `lo` to `composite` (the measured
  `fallback`); `start_table.md`'s FIRST-slot `handoff-rev` row is not needed. **`\G`
  `[r2 E8]`:** rev-inner, unlike REVEND, does not decline `\G`; relocate hands `lo` as a
  scan start and leaves `\G` on the caller's `search_from` (`(?:\G|b)(b?)\w*X` on
  `"-bbX"`: g1 (2,3) from 0; a relocate that moved `\G`'s reference would give (1,2)).
  If the composite cannot separate the two on some route, rev-inner declines `\G` there.
- **Classification** ONE_WAY on the VM (D151 Q4). Not built: D151 item 2's trigger is
  NOT MET (`where_to_start.md` §7).

**Where to attack §4.** (a) The PRESENCE → LOCATE read: does reading the BODY's
LOCATE from an entry slot keep `cand_hit_every`'s route-independence on an ATTEMPT
hybrid (two body routes in one artifact, D-2b)? (b) search-from-not-verify-at on
clamped ties, still unwitnessed: construct a give-up. (c) §4.5: a fifth Σ* source; a
fold the emitted compare applies that the relaxation does not. (d) G4's PASS list: a
kind there that reads capture state after all (`A_KRESET` under a future
`\K`-in-lookaround; a verb kind if `(*ACCEPT)` ever gets a node).

---

## 5. Build sequencing (D156 item (e))

No ids are taken here (counts only); the build lane numbers from the range its brief
names (BOILERPLATE: the kit's reserved ranges are not free).

### L0 — two slots, the path derivation, the fold: no mover `[r2 G12, C3, C4, C5; r2.1 LR-G1, LR-G3, LR-G4, LR-G8, LR-S1, LR-S2, LR-S6, LR-S9, LR-S10, LR-S11]`

- **What, as three no-mover commits, in this order** (LR-S9: the derivation lands
  BEFORE the fold, so no membership reader is ever re-keyed to a FINISH selection; a
  red bisects to one commit):
  - **L0.1 — the slots, the LOCATE rows and the path derivation.**
    1. `CAND_SLOT_LOCATE`/`CAND_SLOT_FINISH` in `CandSlot` (`core/internal.h`) and in
       `cand_nodes[]` (VERIFIER loses `CT_WINDOW`; `CT_WINDOW` deleted; the edges
       E-LF, E-FL, E-FC, E-FR, E-VR with their progress classes `RANK`/`RAISE`/`ENTRY`).
    2. LOCATE rows `empty`, `composite`; `pcrec_emit_dfa_engine` dispatches on the row
       (`composite` by route = today's `emit_unanchored`/`emit_attempt`; `empty` = the
       empty body, moved out of the two emitters' arms `:9729`/`:10094` into the row's
       emitter, byte-identical or the commit does not land); `dfa_engine_is_empty`
       becomes "LOCATE selected `empty`".
    3. §2.7: `.needs[route]` on every row; `cand_path_of` with its fields (`body`,
       `locate`, `finish`, `built`, `needs`, `asks`, members); the NEEDS half;
       `cand_locate_route` and `cand_finish_of` as its fields; and EVERY reader in
       §2.7's table re-pointed — LR-S1's three membership readers (the member fold),
       the orientation block (`:10704-10713`, `:10870`), `emit_vm.c:11330`, F-9's four
       spellings (`pcrec_artifact_has_dfa_scan`, `:10713`, `:10922`, `compile.c:2381`),
       `compile.c:229`, the eight `dfa_engine_is_empty` callers (`:7703`'s drop is
       L0.2's), the ten FINISH reads.
       At L0.1 the match-here root still reads `dfa_matches[]`, the table the next
       commit folds.
  - **L0.2 — the `dfa_matches[]` fold.** FINISH rows `FIN3 verify-at` and `FIN4
    search-from` with only their L0 take CELLS (`FIN3`: `AT` on `CR_DFA`; `FIN4`: `AT`
    and the `NOMATCH` of `caller ⊓ empty` on `CR_DFA`/`CR_ATTEMPT`); every other cell
    lands with the producer that asks it (L2, L3), so L0 declares no unreached cell.
    `match_unwrapped_applies` keeps `anchored_ok` as `FIN3`'s `CR_DFA` availability and
    LOSES `!dfa_engine_is_empty` (LR-G8: the meet asks `NOMATCH` there);
    `-fno-anchored-dfa` stays at `compile.c:230` only and the listing shows it as
    `fact_deny`. `dfa_match_of` → `cand_select(FINISH, path.finish, hand = caller ⊓
    body, point)`, recorded by the derivation; `dfa_match_is_unwrapped` reads
    `u.finish.act` (F-2); the `match` listing is the rows' projection with the two
    descriptions moved verbatim from `axes_dump.c:135-136`, byte-identical.
    `CandSel.hand` (mandatory on a FINISH ask) and `CandSel.point`; `cand_select`'s
    FINISH filter on `take[route]`. No `lroute` (LR-G7).
  - **L0.3 — the data corrections and the erasure record.** `.giveup` deleted (F-1;
    the classification is derived, §1.5); `.contract = CG_FIXED` on `handoff` and on
    RETRY `exact`, `clamped`, `retry-anchored` (LR-S11). `src/ir/nfa.c` records its
    applied erasures in `Nfa.erased` (LR-G3); `pcrec_vm_prefilter_window` reads it;
    `RX_VM_PREFILTER_LANG` reads its `COUNT` member, byte-identically; the boundary
    projection `cand_lang_exact` is computed at `Vm.mrl_win`'s one assignment
    (`emit_vm.c:10368`) with one trace record (`CANDTRACE BOUNDARY vm <SPAN|LOWER>`),
    so the entry, the RETRY recompute and the adaptive re-seed all read it (LR-S2).
    Nothing that emits reads `cand_lang_exact` before L3 beyond what `Vm.mrl_win`
    already gates.
- **abi:** none. No emitted byte, no stamp, no listing byte moves.
- **Spec `[r2.1 LR-S10]`:** one hunk, owed by L0 although no behaviour changes, because
  the CONTRACT is already false: `match_api.md §6.3.4¶2` defines `RX_DFA_SCAN
  "unanchored"` as "the O(n) forward+reverse table pair", and on every `pinned`
  artifact (15 bench / 231 corpus, census T1) there is no reverse machine. Draft:
  *"`"unanchored"` (the O(n) forward scan from `search_from`, D7, followed by a reverse
  pass that recovers the match start unless `RX_DFA_START` is `"pinned"`)"*. The
  pcrec-bench adapter's enum description (`adapter.py:699-705`) says the same and is
  named in L2's inbox note. `start_table.md` §1.2/§1.6 gain the two slots and the edges
  at the manager's merge.
- **Checks:**
  - `scripts/emit_sweep.py` at 0 movers on every arm (the six streams, `-e utf8`,
    `-i`, the deny arms incl. `-fno-anchored-dfa`, `-fprefilter-collapse`), per commit;
  - the C1 trace's SET compare (`trace_diff.py --unordered`) with a declared-trace file
    for the new LOCATE/FINISH/BOUNDARY records (`trace_declared_L0.txt`);
  - **C5 at L0** (`[r2.1 LR-G4]`): the census's membership-vs-text control with the
    stamp side replaced by the derivation's own member set (dumped by the trace
    build), 0 disagreements over the census population, hybrids included;
  - **the trace vs `asks`** (§2.7): equal, up to the declared stamp-only asks file;
  - **the erasure record vs today's conjuncts** (`[r2.1 LR-G3]`): over every census
    hybrid, `Nfa.erased == ∅` ⇔ `!atomic ∧ !look ∧ !collapsed`; a disagreement is a
    finding before L0.3 lands;
  - `cand_rows_selfcheck` extended: totality through `.needs` (the last row taking a
    hand is available by construction, §2.3), the take cells, the progress check with
    `ENTRY`, `hand` mandatory, `needs ⊆ built` on every compile of the trace build;
  - `tests/codegen/run_cand_rows.sh`; `run_cand_oracle.sh` with a witness per new row
    and cell — `[^\x00-\xff]` (`empty`; its `_match` is `FIN4` on `NOMATCH`, LR-G8),
    `a` (`composite` DFA; `FIN3` via its `_match`), `^a` (`composite` ATTEMPT; `FIN4`
    via its `_match`), `(\w+)\1` (`composite` VM, REACHED by the derivation's LOCATE
    ask on `CR_VM`, which is the item revision 2 lacked, LR-S6), `a` with
    `-fno-anchored-dfa` (`FIN4` on `CR_DFA`), and `(a+)b` (a hybrid: the membership
    readers fold F and R and NO FINISH ask happens, LR-S1) — and the declared-unreached
    allowance (`cand_oracle_unreached.tsv`, keyed on (row, route, hand) cells), EMPTY at
    L0;
  - `start_table/call_graph.py` + `inventory_check.py` re-derived.
- **Re-aims, DERIVED `[r2 C3, r2.1 LR-S6]`.** `studies/locate_finish/l0_edit_set.tsv`
  grows from 31 to **55 entries** (18 `def`, 2 `token`, 35 `line`): rev 2's set plus
  LR-S1's three readers, `emit_vm.c:11330`, `:10713`, `:10922`, `compile.c:229` and
  `:2381`, the two `dfa_engine_is_empty` callers whose LINE changes
  (`start_pinned_applies`' P4 `:7895`, `req_handoff_applies` `:7355`, as precise
  lines, not their whole definitions), `pcrec_artifact_has_dfa_scan`, `dfa_scan_name`,
  `pcrec_vm_prefilter_window` and its assignment `:10368`, the three `src/ir/nfa.c`
  erasure arms, the match axis's listing sites and the three RETRY `.contract` rows,
  with rev 2's `hand = BOUNDED` reconciled to `AT`. Through
  `start_table/sabotage_anchors.py` on a call graph regenerated at `00ddf7d5`
  (`results/l0_sabotage_anchors.tsv`, `.summary`): **RE-AIM at L0: 8** — S140
  (`pcrec_vm_prefilter_window`'s body, the look conjunct), S494
  (`pcrec_artifact_has_dfa_scan`'s body), S566 (`emit_unanchored` `:9767`), S599 (the
  WIDTH `ceiling` row's `.giveup` line), S606-S609 (`cand_nodes`); **RE-RUN at L0: 35
  rows / 36 sites** (S07, S65, S67, S82, S218-S221, S223-S226, S235, S283, S284,
  S295, S422, S462, S467, S473, S475, S476, S518-S521, S527, S529, S572, S594-S596,
  S598, S600, S610); **76 rows / 78 sites once after L0** (S88, S141, S222 and S264
  among them). S88/S141 (`emit_vm.c:13405`, `:13273`) are re-RUN, not re-aimed:
  revision 2 placed the boundary record beside `:13393-13405`, which would have
  re-aimed them; revision 2.1 places it at the projection's one assignment (`:10368`),
  where no anchor sits (LR-S6). Defining the two changed callers as whole `def`s
  instead of lines re-aims 12 more rows for no text change (measured: 20 vs 8), so the
  precise lines are the honest set. The tool still reports the 3 pre-existing
  unresolved `src/` sites outside the family (S176, S640, S571) and exits 2 for them,
  as it did for revision 2.
- **New sabotage ids: 10** `[r2 C5, r2.1]`:
  (1) LOCATE order swap (`empty` after `composite`: the empty engine emits a scan;
  emit sweep); (2) `path.finish` misderives a hybrid as a DFA finisher (the inlined
  body emits W/P/F twice; emit sweep + codegen); (3) the match-here ask drops its
  `hand` (asks with 0): the hand-mandatory check aborts in the trace build
  (`run_cand_oracle.sh`); (4) `FIN3`/`FIN4` order swapped (every `_match` becomes
  `search-filter`; `DFA_MATCH` stamp check + emit sweep); (5) the boundary projection
  dropped (a superset hybrid's trace records `BOUNDARY vm SPAN`; oracle witness
  `\w{1,2}(?:(?=)|)$` must record `LOWER`); (6) the `RAISE` class removed from E5
  (RETRY's re-locate): the self-check must report a cycle with no `RAISE` edge;
  **(7) `[r2.1 LR-S1]`** the three membership readers re-keyed to the FINISH selection
  on `path.finish`: `(a+)b` (and every forward+reverse hybrid) hits a NO-ROW selection
  and aborts (codegen + emit sweep); **(8) `[r2.1 LR-G4]`** a `.needs` cell dropped
  (`reverse-pass` loses R): C5-at-L0 reads `rx_reverse_` text with no R member, and the
  member fold moves `RX_DFA_TABLE` on the `mixed` artifacts (emit sweep);
  **(9) `[r2.1 LR-G3]`** the `A_LOOK` arm stops recording: `pcrec_vm_prefilter_window`
  reads exact on lookaround hybrids, `Vm.mrl_win` arms the window ceiling, and the
  atomic/lookaround ceiling checks (S141's codegen rules 1(a)) and the emit sweep go
  red; **(10) `[r2.1 LR-G8]`** the meet dropped (the match-here entry asks `AT` on an
  `empty` body): `FIN3` is selected wherever the anchored machine was built, and
  `DFA_MATCH` reads `"unwrapped"` on `empty` artifacts (emit sweep). F-2's revert is a
  grep row in `make test-codegen` (no `== &cand_rows[` and no pointer compare against
  a FINISH row in `src/gen`), not a plant.
- **Deny/force:** none new; `-fno-anchored-dfa`'s readers go from two to one.

### L1 — `revend.md` S0 and S1, unchanged

The `end_pin` fact split (W1's `end_window` becomes its reader) and the parameterized
reverse-block helper with the dead-seed skip and the which-seed report. No mover.
Checks, sabotage and spec as `revend.md` §9.1 items 1-2. The helper is also RECOVER's
own block, which is what lets `rev-end` ask RECOVER (§4.1).

### L2 — `rev-end` (stage 1, DFA hats): the abi event, two separable commits `[r2 G10, r2.1 LR-G4, LR-G6, LR-G8, LR-S7, LR-S12]`

Revision 2's L2.0 (`dfa_machines_of`, the machine-membership no-mover) is GONE: it is
§2.7's member fold, built at L0 (LR-G4).

- **L2.1 — the GENERATED stamp rule; D-2 is its first absence cell.** One function
  over `cand_list_stamp`'s slot → stamp table plus an ABSENCE column reads §2.7's
  `asks`: a slot asked on the path stamps its selected row's value, a slot not asked
  stamps its absence (WINDOW `"none"`, FIRST `"none"`, NEXT `"none"`, RECOVER
  `"attempt-start"` — D-2's ruled value, `start_table.md` §6 Q5; spellings are the
  manager's). RECOVER's `CR_ATTEMPT` route bit (which exists only so the stamp could
  say `"reverse-pass"`) is dropped, and the trace's declared stamp-only asks file
  empties. Movers, its own census delta: `RX_DFA_START` (and `rx_info.search_form`) on
  every artifact whose path asks no RECOVER (census T8: 37 bench / 606 corpus rows,
  481 distinct, hybrids included), plus F-12's `RX_END_WINDOW` correction on an
  `empty` body with a finite end window (0 in the census; `[^\x00-\xff]$` stamps
  `"2"` today over a `return 0` body). `emit_sweep` default vs parent must equal T8 ∪
  F-12's set exactly. Its own sabotage row (the stamp forked from `asks`), its own
  spec hunk (`DFA_START` gains `"attempt-start"` at `match_api.md §6.3.4¶11` and
  `:4829-4839`, and §6.3 gains the rule's sentence). **Separable**: a red in L2.2
  bisects to L2.2.
- **L2.2 — `rev-end`.** LOCATE row A2 with its `.needs` (R, PRESENCE, RECOVER) and the
  stage-1 conjunct; `nl_last`; FINISH rows `FIN1 nomatch` and `FIN2 report` with
  their cells, `FIN3`'s `ENDSET` cells on `CR_DFA` and `CR_ATTEMPT` (the latter
  DECLARED UNREACHED with its argument: no `ENDSET` producer on `CR_ATTEMPT` until a
  reverse machine exists there), `FIN4`'s `ENDSET`/`LOWER` cells on DFA/ATTEMPT;
  RECOVER's successor becomes FINISH; the `dominated` disjunct and its PRESENCE →
  LOCATE DAG edge gated on `path.body` (LR-G6, C11 — moved here from L3); the walk
  emission (`revend.md` §5.1); `-fno-rev-end` (one new bit, the manager's allocation);
  the `locate` listing axis (`rev-end` 1, `composite` 2, `empty` listed or not by the
  manager's spelling call) with a DECLARED LISTING FILE `listing_declared_L2.tsv` read
  by `start_table/listing_diff.py`; the stamps fall out of L2.1's rule and the member
  fold (§5.1), with no per-stamp edit. **`FIN1` also takes `caller ⊓ empty`'s
  `NOMATCH`** (LR-G8): the 53 corpus `empty` artifacts' `_match` becomes `return 0`
  (0 bench), `RX_DFA_MATCH` gains a third value there (the manager's spelling),
  answers identical — a named mover, the general rule's, not a special case kept to
  avoid it (§8 Q3 discusses it). **The size ladder's rev-end clause `[r2.1 LR-S12]`**:
  a drop rung applies only if the member set it leaves (§2.7, computed with the rung's
  machine removed from `built`) is a strict subset of the member set before it. Under
  form C's T2 the members are {R, A}; dropping A sends `ENDSET` to `FIN4`, which
  relocates to `composite` and needs F, giving {R, F}: not a subset, so
  `SDR_NO_ANCHORED` is skipped there and the ladder moves to its next rung, where
  without the clause it would GROW the artifact by the forward machine and the
  composite.
  **`[r2-landing]` The RECOVER hand (`start_landing.md` rev 2 §4.3, panel SL-C6).**
  `rev-end`'s walk asks RECOVER at SPECULATIVE ends `{n − 1, n}`: its hand is the
  WINDOW mask `CT_LOWER | CT_UPPER` (`¬e`), where the composite's VERIFIER → RECOVER
  ask hands the EXISTS mask `CT_LOWER | CT_UPPER | CT_START` (§1.2's table; §7.5's
  filed mask gains its first producer). `cand_select` filters RECOVER asks by
  `take & hand` exactly as FINISH asks, the hand MANDATORY (abort on 0). `reverse-pass`
  takes both masks; `pinned`, and `[START-LANDING]`'s `end-minus-width` and `landing`,
  take only a hand carrying `e`. §2.7's closure key is (slot, route, HAND): the
  `RX_DFA_START`/`search_form` stamp and every reader of the RECOVER selection read the
  cell the PATH asked — on an artifact where `rev-end` is selected that is `rev-end`'s
  WINDOW ask (→ `reverse-pass`), never a fresh hand-less ask (6 bench / 41 corpus
  end-pinned fixed-width artifacts would otherwise stamp `end-minus-width` over a
  reverse walk). SEQUENCING: whichever of L2.2 and `[START-LANDING]`'s SL3 lands second
  carries it. If L2.2 lands first it adds the field and the masks with `reverse-pass`
  taking every mask and `pinned` taking EXISTS (no mover: `pinned` never co-occurs with
  `end_pin`, revend X3's assertion, now a declaration); SL3 then adds the two rows'
  `take`. Its sabotage row (`start_landing.md` §7.5 row 8) becomes reachable here.
- **abi:** 71 → 72, once, for the L2 merge. Readers BY GREP at build time (D76/D94):
  (a) the abi NUMBER (`revend.md` §5.3 (a)); (b) the byte-count readers (§5.3 (b));
  (c) the `DFA_SCAN` value readers — `revend.md` §5.3 (d)'s 33 files / 6 sabotage rows
  plus every MACHINE-PROXY reader (a reader that takes `"unanchored"` to mean "the
  forward machine is present"; the contract itself after L0's hunk no longer does);
  `pcrec_artifact_has_dfa_scan`'s 12 callers, which remain TRUE on a `rev-end`
  artifact (`path.body`: it has a DFA body; what it lacks is F among the members), each
  re-read for whether it asks a BODY or a PATH question (§2.7's table); (d) the
  `DFA_START` value readers (19 files, 5 rows) for L2.1; the `DFA_MATCH` value readers
  for `FIN1`'s value; (e) **outside the repo** (pcrec-bench at `76e13c1d`, read-only):
  `testees/pcrec/adapter.py` `:699-705` (`"dfa_scan"`: enum `["unanchored", "attempt",
  "empty"]`), `:802-806` (`"dfa_start"`: enum `["pinned", "reverse-pass"]`) and
  `:1011-1013` (`"dfa_match"`: enum `["unwrapped", "search-filter"]`), all CLOSED
  vocabularies; `pcrecbench/report.py` (`_dfa_scan_display` `:2282`, the
  `start=<pinned|reverse-pass>` legend `:763-767`); **`tools/selfcheck.py`
  `[r2.1 LR-S7]`**, which DOES pin the vocabularies: `"dfa_start": "reverse-pass"` at
  `:3705-3707` (the provably-empty case) and `:3729-3731` (the anchored attempt case)
  — exactly L2.1's movers —, the provably-empty case's `"dfa_match": "search-filter"`
  (`:3707`), L2.2's `FIN1` mover, and `"dfa_scan": "unanchored"` at `:3552-3554`, a
  reader that does not move (`foo[0-9]+bar` has no end pin); then the counting suites
  (registry, codegen, rxtsource) whether or not they cite the number (D94 addendum).
- **pcrec-bench deliverable `[r2 C7, r2.1 LR-S7]`.** An `[inbox]` adapter note
  (`pcrec-bench/docs/dev/inbox_from_pcrec.md`, the manager's single-file commit, D78)
  naming the new `DFA_SCAN` value `"rev-end"`, the new `DFA_START` value
  `"attempt-start"`, `DFA_MATCH`'s third value, the abi number, the movers'
  population, and the `selfcheck.py` pins above as KNOWN MOVERS (so the bench's own
  check is updated in the same window rather than read as a regression); REQ_WHY needs
  no line (it keeps its four tokens, LR-G6); and the window handshake before any bench
  cell reads an L2 artifact.
- **Movers:** census T4: 12 bench (the five tail patterns, `letters-bounded-tail-z`,
  the six class-B cells incl. `wild-semdiv-dollar-trailing-newline-pcre2` in two sets),
  corpus 171 rows / 121 distinct (L2.2); T8's 37 bench / 606 corpus (L2.1); the 53
  corpus `empty` `_match` bodies (L2.2, `FIN1`); F-12's 0. The `emit_sweep` default vs
  `-fno-rev-end` census must equal the set whose text carries `revend_seed`
  (`revend.md` §5.4).
- **Checks:** `revend.md` §9.1 item 3's list, E13 replaced by E-LF. The answer net
  `tests/assertions/rev_end.rxt` (§9.3), the codegen structural check (`"rev-end"` ⇔
  `revend_seed` emitted; `nl_last` false ⇔ no tie text; a declining pattern
  byte-identical under `-fno-rev-end`), the test-axes floor arm (X13), the refusal-set
  check, C17 and the memfn stamps; `run_cand_oracle.sh` witnesses for A2, `FIN1`
  (incl. `[^\x00-\xff]`'s `_match`), `FIN2` and the `ENDSET` cells of `FIN3`/`FIN4`
  (`a$` T1, `ab$` with a final-newline subject T2, `ab$` with `-fno-anchored-dfa` T3);
  the (`verify-at`, `CR_ATTEMPT`, `ENDSET`) cell in the unreached file; C5 and the
  trace-vs-`asks` compare (now equal, no declared file) on every commit.
- **New sabotage ids: 19**: `revend.md` §9.2's 16 recast (rows 1-10 unchanged; 11 (R2)
  "the route mask widened to `CR_ATTEMPT`"; 12 (R3) "the stage-1 conjunct dropped";
  13 (R4) "`empty` after `rev-end`"; 14 the deny unplumbed; 15 `FIN4` made to take
  `ENDSET` ahead of `FIN3`; 16 the stamp forked from the selection (`DFA_SCAN`)); plus
  1 for L2.1 (a slot stamp read from its selection although the slot is off the path:
  `RX_DFA_START "reverse-pass"` returns on the T8 set); plus 1 for the deference
  dropped (a pre-check emitted ahead of the walk; codegen; moved from L3 by LR-G6);
  plus 1 for the size-ladder clause dropped (a T2 artifact under `SDR_NO_ANCHORED`
  emits the forward machine; the size log's tripwire on a constructed witness).
  Re-aims: derived by re-running `sabotage_anchors.py` with L2's edit set at build
  time (S222, S264 and S693 are known members).
- **Spec (D80) `[r2 C9]`:** `tuning.md` §2.x `-fno-rev-end`; `match_api.md`:
  `DFA_SCAN` gains `"rev-end"` in every value table (the stamp list `§6.3.4¶2`, the
  `rx_info` table `§6¶6`, the field comments `§6¶1`, and the tables in
  `facts_listing.md:113-126` and `registry.md:421`, each confirmed by the build's
  grep), `DFA_START` gains `"attempt-start"` at `§6.3.4¶11` (L2.1), `DFA_MATCH` its third value, the
  generated stamp rule's sentence, the REQ_WHY `dominated` description widened to "the
  scan or the locator already tests it", `rx_info.search_form`, the abi sentence and
  TU-guard example; `registry.md`'s axis counts and the `locate` axis;
  `facts_listing.md` `end_pin`; `cli.md` where it lists axes.
- **Deny/force:** `-fno-rev-end` (deny only).

### `[GIVEUP-DIFF]` — GIVEUP1, direction-checked, before the first VM-finisher LOCATE row `[r2 G7, C5, r2.1 LR-G5]`

No new section (LR-G5): three additions to `make test-axes`' existing GIVEUP1
relation (`tests/axes/run_axes.sh:1270-1320`), §1.5's list — the direction rule read
from the derived classification, a budget-ladder arm, and the witnesses (K82h
§3.1a's 35 blocks, T6a's 13, W1's constructed witness `(\w|\w\w)x$` measured in
§1.5, one per further ONE_WAY row) — plus the corpus instrument that derives the
classification column, plus a spec sentence for every row it classifies ONE_WAY that
has a deny flag (§8 Q4). No `src/` change. It must exist before L3, L4 or L5 claims a
posture, and it answers F-1 behaviourally (W1's half now witnessed, PRESENCE's half
already).

### L3 — stage 2 (VM hats): FILED

Drop the stage-1 conjunct; `FIN3`'s VM cells (`SPAN`, `AT` — and the VM's `_match`
then routes through the table), `FIN4`'s VM cells (`ENDSET`, `LOWER`); the PRESENCE
deference is already in place (L2). **The answer-level control `[r2.1 LR-S2]`** is
E9's window-identity twin against libpcre2 10.46 (the walk's window vs the shipped
prefilter's, every string to length 6-7 at every `lo`, then captures vs libpcre2),
**which also counts E-VR traversals and asserts 0 on exact hybrids `[r2.1 LR-S4]`**;
the answer net's captures cells (`(\d+)$`, `(a+)$`, `a\Kb$`, the unclamped tie
`([^c]{1,3})$`, the clamped ties `(\s+){2}$`, `(\s$){1,3}` and the LAZY `(\s+?){2}$`,
the superset witness). abi 72 → 73 (or folded into L2 if Frank rules so, §8 Q2).
Movers: 0 bench / 13 corpus. **New sabotage ids: 4**: a clamped tie sent to the VM's
verify-at (the `take[CR_VM]` cell widened to `ENDSET`; `[r2 E3]` witness `(\s+?){2}$`,
the twin's `window[0][1]` compare); a superset walk projected as `SPAN` (answer net on
a constructed superset witness); the inlined LOCATE asked on `CR_VM`; and the X1
dead-seed skip dropped on a HYBRID witness `[r2 E10]` (a lookaround hybrid; E10's SEGV
shapes). Spec: `match_api.md`'s hybrid stamps. Trigger: `revend.md`'s.

### L4, L5 — FILED

L4 `rev-end-relaxed` (§4.5): its own erasure mode in `src/ir/nfa.c` (which RECORDS
`BREF`/`VAR`/`CALLSTAR` in `Nfa.erased`, LR-G3, so nothing reads it as exact), a
LOCATE row on `CR_VM`, its own deny (§8 Q5), ONE_WAY with D148 Q6's sentence; requires
`[GIVEUP-DIFF]`. L5 rev-inner (§4.6): D151's trigger; requires `[GIVEUP-DIFF]`.

### 5.1 The stamp rule: generated from the path `[r2 C6, G10, r2.1 LR-G4, LR-G6]`

**The rule (DD-13c's: a stamp names the selection that was emitted, from the one
derivation that emitted it).** The locator is named ONCE, on `RX_DFA_SCAN`, whose
values are the selected LOCATE row's listed name on the body route (`unanchored` and
`attempt` are `composite`'s two DFA hats, `empty` is `empty`, `rev-end` is the fourth
value) — not a new `RX_LOCATE` stamp, which would put bytes on every artifact and move
every byte-count reader for no new information. Every OTHER slot stamp reads its
slot's selection where §2.7 asks that slot on the path, and its ABSENCE value where it
does not: ONE generated function (L2.1), not a per-stamp table edited per locator.
Machine stamps fold over §2.7's members (L0). So a `rev-end` artifact's stamps need no
edit of their own:

| stamp | reads on a `rev-end` artifact (form C, T1/T2; under T3 the composite is on the path and these keep their values) | why |
|---|---|---|
| `RX_DFA_SCAN` | `"rev-end"` | LOCATE's listed name |
| `RX_DFA_START` | `"reverse-pass"` | RECOVER is ASKED (the walk is its block seeded at the end): its selection, true |
| `RX_END_WINDOW` | `"none"` | WINDOW is not asked: absence; X10's one-spelling rule holds |
| `RX_DFA_PREFILTER`, `_PREFILTER_OFFSETS` | `"none"` | NEXT is not asked: absence |
| `RX_REQ_BYTE`, `RX_REQ_RUN` | unchanged | they are FACTS about the pattern, not selections |
| `RX_REQ_WHY` | **`"dominated"`** where `REQ_BYTE ≠ "none"`, `"none"` otherwise **`[r2.1 LR-G6]`** | PRESENCE is ASKED; `.whole` selects `dominated` ("the scan already tests it", true of the walk). Revision 2's fifth token `"locator"` is withdrawn: it re-created the parallel spelling G9 removed |
| `RX_REQ_HANDOFF` | `"none"` | FIRST is not asked: absence |
| `RX_DFA_TABLE`, `RX_DFA_UNIFORM_FOLDS`, `RX_DFA_SCAN_EDGE` | folded over the members: R, plus A under T2 | §2.7's fold, already built at L0; a stamp naming a machine the file lacks is the defect class `start_table.md` §0 lists |
| the orientation block (comment) | describes the walk | it reads the members too (L0); non-essential comment text, inside L2's abi event |
| `RX_DFA_MATCH`, `rx_info.match_form` | unchanged (`FIN3`'s or `FIN4`'s name) | the match-here entry's own FINISH row |

`RX_DFA_START "attempt-start"` is the same rule on ATTEMPT / `empty` paths, which ask
no RECOVER: L2.1 is the rule's first application, and D-2 is its first absence cell
rather than a special row. **This supersedes `revend.md` §5.2** (which had
`RX_END_WINDOW` and `RX_DFA_START` read `"rev-end"`) and revision 2's §5.1 (which
added a REQ_WHY token); the supersession is recorded here and in `revend.md` §5.2
itself. Spellings are the manager's call (memory `pcrec-dd13b-syntax-is-managers`);
the rule is Frank's (§8 Q3).

**Where to attack §5.** (a) L0's "no mover": the `empty` arm's move out of two
emitters (the two arms differ in where the head is emitted); the meet on the 18
`P-empty` hybrids (their `_match` is the VM's, so the derivation asks no FINISH
there). (b) The derived re-aims: an anchor the edit set's text misses because L0
rewrites it by a token not listed. (c) §5.1: a DFA_SCAN reader that treats
`"unanchored"` as "a forward machine exists". (d) §2.7's member fold: a fifth spelling
of the membership rule. (e) L2.1: a slot whose stamp has no absence cell but can be
off a path. (f) The size-ladder clause: a rung whose machine is needed by a row that
is not FINISH's.

---

## 6. Standing questions (`docs/design/CLAUDE.md`)

### 6.1 The measurement regime — RELEVANT, briefly

This note takes no timing. Every number is compile-side (the census: counts from
stamps, facts and emitted text, regime-free), a critic's answer-level count (E1-E12:
correctness, regime-free), `revend.md`'s scratch-tier Linux timing (7700X, warm
repeated calls, cited for REVEND only), or walk_survey's load counts and twins (cited
for §7.3's ranking, scratch tier, a loaded box). The one decision a regime could flip
is stage 2's value, which is FILED on a population, not a timing; §7.3's ranking above
REVEND rests on bench-weighted estimates (50.9 vs 30.9 ms) that a design lane re-takes
before building. GIVEUP1's budgets are step/work counts, not clock time, so they are
box-independent; W1's witness (§1.5) was run once on this box and is a count, not a
time.

### 6.2 The independent control — RELEVANT

- **The census.** Five controls (§3.1): the emitted text (C1, C2, and C5 for the
  machine-membership rule `[r2.1 LR-G4]`), a borrowed copy of `ew_walk` against the
  shipped fact in both directions with each decline DECLARED and counted (C3), and C4,
  which revision 2.1 relabels PLUMBING (`[r2.1 LR-S2]`: its stamp's row predicate is
  `Vm.mrl_win`, built from the same conjuncts the classifier reads). `analyze.py` exits
  1 and prints no table on any disagreement. The population is counted by the borrowed
  `bench_pop`/`corpus_pop` (K35: who counts is named).
- **The design's checks.** The extended self-check is a CONSISTENCY check: it shares
  its source with the table. The controls are elsewhere:
  - for L0: the emit sweep (bytes, not selections); C5 with the derivation's member
    set against the text; the C1 trace's asks against §2.7's `asks` (what the emitters
    asked vs what the rows declared); the erasure record against today's conjuncts
    over every census hybrid;
  - for L2: libpcre2 10.46 on the answer net and `-fno-rev-end` (`revend.md` §12.2);
    the census delta of L2.1 against T8 ∪ F-12;
  - for L3 and every UNDENIABLE row (`[r2.1 LR-G9, LR-S11]`): the window-identity twin
    against libpcre2, stratified by `path.finish`, `path.locate`, the member set and
    the erasure set, and counting E-VR (`[r2.1 LR-S4]`);
  - for POSTURE: GIVEUP1, direction-checked with a ladder arm (`[r2.1 LR-G5]`), which
    reads answers at budgets and shares nothing with the table.
- **Witness reach ([MECH-REACH]).** Every L0 row and cell has a constructed witness,
  including the VM `composite` arm, reached by the derivation's LOCATE ask
  (`[r2.1 LR-S6]`); L2's (`verify-at`, `CR_ATTEMPT`, `ENDSET`) cell is the first entry
  in the declared-unreached file, with its argument; W1's ONE_WAY witness exists
  (§1.5).

### 6.3 What moves when data is regenerated — RELEVANT

- L0 moves nothing (no abi event). Its spec hunk corrects a sentence, not a value.
- L2.1: `RX_DFA_START` and `rx_info.search_form` on T8's set, `RX_END_WINDOW` on
  F-12's (empty today). L2.2: the abi number; `DFA_SCAN`'s value and the member-folded
  machine stamps on T4's movers (§5.1); `DFA_MATCH` on the 53 corpus `empty`
  artifacts. No calibration or data file is read (`end_pin`, `nl_last`, the path and
  the erasure record are per compile).
- L4's relaxed machine reads no data; rev-inner's G3 reads the byte-rate prior
  (`default_ppm.tsv`).
- The census outputs (`rows.tsv.gz`, `summary.txt`, `l0_sabotage_anchors.tsv`) move
  with the tree; no check reads them. The L0 edit set is data the build lane re-derives
  against its own pin.

---

## 7. Candidates with triggers (filed, not designed beyond the trigger) `[r2 G13, G14, r2.1 LR-G3, LR-G10..G14]`

### 7.1 The relaxed-backref machine run FORWARD (G13)

§4.5's `relax(P)` is a SOUND general erasure for `A_BREF`. Run forward, it is a
superset prefilter for every acyclic-backref VM-only artifact (`backrefs_design.md`
§7.4's chartered prefilter, needing no E2 gate since the relaxation is
assertion-erased; VM-only search measured 6.2-130× slower than a hybrid). **Stated
precondition `[r2.1 LR-G3]`: the erasure record.** Its lowering arm must record
`BREF` (and `VAR`/`CALLSTAR` where those relax) in `Nfa.erased`, so
`pcrec_vm_prefilter_window`, `cand_lang_exact` and (d′) read the prefilter as a
SUPERSET; today's kinds-list predicate never tests BREF/VAR and would read it EXACT,
hand `SPAN` across the boundary, and use the superset's window END as the MRL ceiling
(the atomic-groups 122-cell class). The record lands at L0, so the precondition is
met before this row can be built. **Trigger:** a census of VM-only backref artifacts
where `relax(P)` is acyclic and the N7 START-SET hat does not narrow, PLUS one bench
backref cell paying the attempt loop.

### 7.2 rev-end as rev-inner with landmark = end: a seed-SET reverse walk (G14(1))

`(?m)$` seeded at every `'\n'` + `n`. **Trigger:** a bench or real-world `(?m)...$`
cell whose attempt loop or forward scan dominates (the finding names the cell).

### 7.3 `[START-LANDING]`: RECOVER rows that know the start without walking `[r2.1 LR-G10]`

Plan row `[START-LANDING]` (filed 2026-10-09 from `../dev/walk_survey.md` §7 F1, its
classes K4 and K3), with revision 2's §7.3 (G14(2), the fixed-width row) FOLDED IN:
they are one family and one placement.

- **Placement: the composite's RECOVER slot**, the question "given a match END, where
  does it start?", as four first-match rows ordered by how much the start needs:
  1. `pinned` (shipped, [OPT-5] STEP 2): ZERO bytes of evidence — the forward machine's
     start state accepts unconditionally, so the match starts at `search_from`;
  2. `landing` (new): ONE byte — the forward scan's skip loop LANDED on `L`, and a
     compile-time fact holds: every start-set byte, in its start view, takes the
     anchored machine to an accepting state; then a match starts at `L` and, `L` being
     the first candidate ≥ `search_from`, it is the leftmost (walk_survey §4 K4, "what
     makes it exact"); the fact holds for `C+`, `C`, `C{1,n}`, `C+D*` token shapes and
     fails for literals and a leading assertion;
  3. `end-minus-width` (new; revision 2's §7.3): a fixed-width pattern's start is
     `end − W`; under `-e utf8` `W` must be a fixed BYTE width (a fixed character
     width is not, K49/K50);
  4. `reverse-pass` (shipped): the fallback.
- **One row each, nothing else moves.** Each hands `SPAN` across the boundary exactly as
  `reverse-pass` does, so FINISH is unchanged; on a hybrid the window is the same span
  (NEUTRAL by window identity, the same argument as stage 2's). R leaves the member
  set through §2.7 when `landing` or `end-minus-width` is selected, so the stamps fold
  over F (+A) with no special case, and `RX_DFA_START` names the selected row (two new
  values: a closed-vocabulary event for the bench adapter, `adapter.py:802-806`).
- **Trigger: MET.** walk_survey measured K4 on 176 / 343 bench patterns (85.7% of
  reverse-pass bytes on throughput cells are landing bytes; twins −20..−42%) and K3 on
  74 bench / 1,002 corpus (`abcd` −36..−37%), est. 50.9 ms bench-weighted, which
  RANKS IT ABOVE `[OPT-REVEND]` (30.9 ms) on the next `[OPTLOOP]` candidate list. Its
  design lane owns the landing record (where the skip loop's landing is kept), the
  fact's derivation and its control, and K4's fact-less form, which is §7.6's
  separate row.

### 7.4 A forward regular-prefix locator over `P·Σ*` (G14(3))

**Trigger:** the finding's: a population where the prefix's language is regular, the
suffix is not, and no landmark rescues the start.

### 7.5 A subset locator handing EXISTS (G14(4), BOONIES-class)

A machine for a SUBSET of `L` proves a match exists and bounds the start from above:
the hand `CT_LOWER | CT_UPPER | CT_START` = `([s, t], e)` (§1.2's table). **BOONIES**
(memory `pcrec-high-impact-focus`): no measurement chartered; trigger as the finding
states.

### 7.6 `candidate-verify`: K4's fact-less form, a second LOCATE row (LR-G11)

Where `landing`'s compile-time fact fails, the ATTEMPT candidate loop with the
UNWRAPPED anchored machine verifying each landing (one anchored run per candidate;
continue unanchored from `L + 1` on a death) is a second LOCATE row on `CR_DFA`,
`.needs` = F, A. It costs an anchored attempt per false landing, so it is a selection
question. **Trigger:** a fact-less bench cell where reverse-pass bytes dominate AND
the measured landing-hit rate clears the break-even of one anchored attempt per false
landing (walk_survey's 36 no-landing throughput cells are where it only costs).

### 7.7 Match-here across three routes is ONE row (LR-G12)

F-11 (ATTEMPT's `_match` runs a whole search), K8 (the VM route's `_match` scans for a
start the anchored question does not need) and the `empty` / `-fno-anchored-dfa`
fallbacks are one row under LR-G1: `verify-at` taking `AT` on every route whose
machine is built (the F-11 cell deleted, the VM cell asked at L3). **Trigger:** K8's —
a long-subject match cell (the bench's match subjects are ≤ 5 KB today, est. 0.01 ms).
§8 Q7.

### 7.8 The bounded-interval hand (LR-G13)

`[OPT-VMSEED]` stage 4's seed window, G14(4)'s interval and a "match starting in
`[s, t]`" entry are the `CT_LOWER | CT_UPPER` mask with `t > s` (§1.2): `search-from`
takes it under its filter (a start above `t` is `NOMATCH`); `verify-at` does not
(it is not a point). **Trigger:** VMSEED stage 4's; the caller-facing entry itself is
BOONIES.

### 7.9 On superset hybrids the landing is already a LOWER (LR-G14, BOONIES)

On a superset hybrid the forward skip loop's landing `L` is a sound `LOWER` without
the reverse pass: every match of `L(P)` starts at a start-set byte at or after
`search_from`, so none starts below `L`. **BOONIES**: no measurement
chartered.

---

## 8. Questions for Frank (discussion), restated under revision 2.1

**Settled and struck.** Revision 1's Q1 (FINISH is a slot block: G4/G5). Revision 2's
Q1, "L0 before REVEND, or folded into REVEND's abi event?": both re-check critics put
L0 first (lfre2: "L0 first, with LR-G1 and LR-G4 adopted there"; lfre1: "L0 is NOT
build-ready until LR-S1 is fixed; L2 is ready after L0 plus LR-S3/S5/S7"), and the
binding dispositions place work AT L0 (LR-G1, LR-G4), so the question is answered. One
force it had is now larger and worth knowing: L0 grew from four items to three
commits, a 55-entry edit set and 8 re-aims, because it now carries the path
derivation; it is still a no-mover, and every piece of the growth is a reader that
would otherwise be re-keyed wrongly by the fold (LR-S1). Revision 2's Q7 (ATTEMPT's
match-here form) is FILED by LR-G12 as §7.7, one row across three routes, with K8's
trigger (lfre2: "measured as the K8 family"); the F-11 cell stays visible in
`verify-at`'s take until then. Revision 2's Q5 (the relaxed locator's deny): the
leaning (its own bit when built) and lfre2's judgment agree and lfre1 gave none, so it
is recorded as AGREED unless you object, not discussed again.

The critics' judgments below are as the review records them: lfre2's in the
re-check's paragraph on §8, lfre1's read from its findings where they bear on a
question (lfre1 recorded no separate §8 judgments).

**Q1′ (new). After L0: REVEND or `[START-LANDING]` first?** *Problem:* this note was
chartered for REVEND, and the re-check placed a second, larger family in the same
frame: `[START-LANDING]`'s RECOVER rows (§7.3), whose trigger is already MET.
*Forces:* walk_survey's bench-weighted estimates put `[START-LANDING]` at 50.9 ms and
REVEND at 30.9 ms; `[START-LANDING]` is smaller in kind (RECOVER rows, no new slot, no
new LOCATE row, two new `RX_DFA_START` values) while REVEND carries L1's fact split,
L2's walk and the generated stamp rule; both ride L0, and `[START-LANDING]` needs L0
more than it looks — without §2.7, taking R off the path for `landing` would be a
FOURTH conjunct in each of the three membership readers, the special-case trap
LR-G4 exists to close. Against: REVEND is designed, panelled twice and has its twins;
`[START-LANDING]` has measurements and a placement, not a design. *Leaning:* L0 first
regardless; then put `[START-LANDING]` on the next `[OPTLOOP]` round's candidate list
ranked by its estimate, ahead of REVEND, and let the round decide, since ranking is the
loop's job, not this note's. *lfre2:* `[START-LANDING]` belongs in RECOVER and ranks
above REVEND (LR-G10); rev-inner ranks below both. *lfre1:* no judgment recorded.

**Q2. Stage 2 with stage 1?** *Problem:* the stage-1 conjunct (`path.finish !=
CR_VM`) is the one place a route-independent locator is kept off a route. *Forces:*
the mechanism is now smaller than in revision 2 — the PRESENCE deference lands with
stage 1 anyway (LR-G6), so stage 2 is the conjunct, `FIN3`/`FIN4`'s VM cells and the
twin; it is NEUTRAL by window identity (E9: 0 / 5,199,120); not building it is the
special case. But the population is 0 bench / 13 corpus, 11 already W1-bounded, and
D77 says wait; and LR-S3/S4 show the VM side has two sharp edges (`ENDSET` must not
reach the VM's verify-at; E-VR must be unreached on exact hybrids) that only the twin
watches. *Leaning:* FILED with `revend.md`'s trigger, the conjunct commented as stage
2's switch. If you weigh generality above D77 here, it folds into L2 for one conjunct,
two take cells and one twin. *lfre2:* stage 2 FILED. *lfre1:* no judgment on filing;
its LR-S3/LR-S4 are the conditions any build of it must meet.

**Q3. The stamp RULE, now generated.** **RULED 2026-10-09: agree — the leaning as written, standing for every future locator (D156 addendum 2).** *Problem:* a locator that does not run most
slots must leave their stamps saying something true, and every future path-changing
locator (`empty`, `rev-end`, `[START-LANDING]`'s rows, rev-inner) meets the same
problem. *Forces:* revision 2 wrote a per-stamp table for `rev-end` and a new REQ_WHY
token; revision 2.1 generates the rule from §2.7 (a slot asked on the path stamps its
selection, one not asked stamps its absence), keeps REQ_WHY at four tokens by ASKING
PRESENCE (LR-G6), and makes D-2 the rule's first absence cell at L2.1. The cost of
being general shows in two places: F-12 (an `empty` body's `RX_END_WINDOW` is
corrected, population 0 today) and LR-G8's `FIN1` on `caller ⊓ empty`, which moves the
53 corpus `empty` artifacts' `_match` to `return 0` and gives `RX_DFA_MATCH` a third
value that the bench adapter's closed enum and `selfcheck.py:3707` must learn — for no
measurable gain, because the general rule does it, not a need. Keeping today's
`search-filter` there would take a predicate that excludes one hand from one row,
which is the parallel special case the rule exists to remove. A new `RX_LOCATE` stamp
remains the more explicit alternative and moves every artifact. *Leaning:* the
generated rule, with the `empty` `_match` move taken inside L2's abi event and named
in the inbox note. Whether "off the path ⇒ absence, the locator named once, generated
from the path" is the rule for every future locator is yours. *lfre2:* the stamp rule
generated from the path derivation; no REQ_WHY token. *lfre1:* LR-S10 (the
`"unanchored"` sentence is already false on `pinned` artifacts) and LR-S12 (the size
ladder) are the rule's two existing casualties, both fixed by stating membership once.

**Q4. The one-way spec sentences.** **RULED 2026-10-09: agree (lfre2's form), generalized by Frank to a standing rule: optimizations never reduce any pattern's ability to complete (D158; known violator K102).** *Problem:* W1 and the VM-route PRESENCE checks
skip attempts the deny arm runs, so a budget-limited call can answer where the deny
arm gives up (ONE_WAY), and no spec sentence says so; §1.5 now has W1's witness
(`(\w|\w\w)x$`, `--engine=vm`, step budget 50: default answers, `-fno-end-window`
gives up). *Forces:* GIVEUP1, direction-checked, will hold every ONE_WAY row to its
direction, and a caller who sets a step budget can observe it; one sentence per
`tuning.md` entry repeats itself across W1, `-fno-req-byte`, `-fno-start-set`, the
anchor bound and the adaptive re-seed. *Leaning:* lfre2's form — ONE preamble sentence
in `tuning.md` §2 stating what ONE_WAY means for a caller's budget, and a per-entry
MARKER on each ONE_WAY row with a deny — landing with `[GIVEUP-DIFF]`, worded as D148
Q6's. *lfre2:* one preamble sentence with per-entry markers. *lfre1:* LR-S11 adds that
the undeniable rows' contracts (RETRY `exact`/`clamped`/`retry-anchored`) are part of
the same surface and are checked by the twin, not by a deny differential.

**Q6. rev-inner after E1 and LR-S5.** **RULED 2026-10-09 (D151 addendum 4): the question was framed on the wrong route. Rev-inner's value is the DFA population (walk_survey K12, G4 by construction). Stage 1 = the DFA hat, triggered by a K12 twin after G2. Stage 2 = the VM LOWER form, keeping the `dup-param-detect` trigger. Rank third, after [START-LANDING] and REVEND.** *Problem:* rev-inner's per-occurrence verify is
sound only under G4, now a closed predicate that also fails DUPNAMES references
spanning `P` and `S`; on its VM-route population (a backreference in `S` to a group of
`P`) it can only hand a LOWER bound to the attempt loop. *Forces:* D151 placed the
reverse walk partly FOR that population; a lower bound still skips the prefix work up
to the first viable occurrence, but no longer verifies one occurrence at a time, so its
win shrinks on dense subjects; and §7.3's `[START-LANDING]` and REVEND now rank above
it on measured estimates. *Leaning:* keep D151's trigger unchanged (the
`dup-param-detect` twin), have the twin measure the LOWER form FIRST (the only sound
one there), and rank rev-inner below `[START-LANDING]` and REVEND. Does the reduced VM
value change how you rank it? *lfre2:* rev-inner ranks below `[START-LANDING]` and
REVEND, and its twin measures the LOWER form first. *lfre1:* LR-S5 (the DUPNAMES
witness) is the reason G4 is a closed predicate; no ranking judgment.

---

## 9. The lenses

- **specific vs general:** general. One product type keyed on the existing `CT_*`
  bits, four FINISH rows, two hats cover every shipped mechanism; REVEND's E13, tie
  table, R2/R4 and stage 2 are instances, `dfa_matches[]` stops being a parallel
  table, and `empty`'s eight hand-spelled off-path conjuncts become one derivation
  (`[r2.1 LR-G4]`).
- **core vs derived:** the tables, the path, the boundary projection and the
  classification are derived; `end_pin`, `nl_last`, the relaxed machine, the erasure
  record and the inputs of `cand_lang_exact` are core facts or machine properties;
  `.needs` is declared because it is a property of each row's emitter (and is held to
  the emitters by the trace and the text); the contract column is declared because it
  is a ruling.
- **applicable vs assumption-changing:** applicable; no contract changes at L0 (its
  spec hunk corrects a sentence that is already false).
- **fits the architecture vs refactor:** L0 is a refactor in refactor A's shape, now
  three commits; L2 fits, and its stamp work is the generated rule rather than edits.
- **shared question / engine hat (D124):** FINISH is D124's other axis: "what does the
  engine still have to compute", with the hat by route and the availability by the
  route's machines.
- **sibling of a family (memory `pcrec-forest-for-trees`):** revision 2 surfaced three
  families (FINISH; "does a DFA body exist"; machine membership); the re-check showed
  they are ONE, "what the selected path uses", with `empty`, `rev-end` and
  `[START-LANDING]`'s rows as its members (§2.7). It also shows the next sibling to
  watch: the slot stamps' absence values, which the generated rule turns from a
  per-locator table into a column.

---

## 10. Findings for the record

- **F-1** (revised) W1 `window` and the VM-route PRESENCE checks are ONE_WAY by §1.5's
  rule, and their declared posture read NEUTRAL by the zero value; the declared column
  had no reader. Fixed at L0 by deleting the declaration (§1.5); W1's half is now
  WITNESSED (`[r2.1 LR-G5]`, §1.5), PRESENCE's half already was; GIVEUP1,
  direction-checked, holds both.
- **F-2** `dfa_match_is_unwrapped` (`emit_dfa.c:7727`) compares a row POINTER; dissolved
  by the fold (§3.4).
- **F-3** (revised twice) On the 22 bench / 621 corpus superset hybrids the inlined
  body's `SPAN` is not `L`'s; the fix is the boundary projection `cand_lang_exact`,
  reading the RECORDED erasure set (`[r2.1 LR-G3]`), computed once where `Vm.mrl_win` is
  assigned (§1.2).
- **F-4** `revend.md` §3.9's stage-2 posture (ONE_WAY) is NEUTRAL given that a clamped
  tie goes to `search-from`, never to the VM's verify-at (§4.3; E9; `[r2.1 LR-S3]`).
- **F-5** rev-inner is a LOCATE row, not NEXT (§4.6).
- **F-6** WITHDRAWN `[r2 G1]`: D156's type list did not omit anything; `CAND` is
  `LOWER`.
- **F-7** (revised `[r2.1 LR-S6]`) Revision 1's "L0 re-aims 0 sabotage rows" was wrong
  (rev 2 derived 6); with revision 2.1's edit set the derived count is 8 (S140, S494,
  S566, S599, S606-S609).
- **F-8** (`[r2 E1]`, sharpened `[r2.1 LR-S5]`) `where_to_start.md` §2.2 step 1 was
  unsound when `S` references `P`'s groups; corrected in place, and its G4 is now the
  closed predicate of §4.6 (the DUPNAMES reference spanning `P` and `S` fails it).
- **F-9** (revised `[r2.1 LR-S8]`) "Does a DFA body exist" is spelled FOUR ways
  (`pcrec_artifact_has_dfa_scan`, `(!vm || prefilter)` at `emit_dfa.c:10707-10713`,
  `dfa_body` at `:10922`, and `compile.c:2381`, the build condition itself); all read
  `path.body` at L0 (§2.7).
- **F-10** (revised `[r2.1 LR-G4]`) The machine-membership rule is spelled four times
  (`dfa_table_name`, `dfa_uniform_folds`, `dfa_scan_edge_name`, the orientation block);
  L0's member fold unifies it (revision 2's L2.0 is absorbed), and C5 holds today's
  rule against the bytes (0 / 5,355).
- **F-11** An ENG_ATTEMPT artifact's `_match` is `search-filter` (a whole search from
  `s`); under LR-G1 the alternative is one take cell of `verify-at` (§2.3, §7.7).
- **F-12** (new, lane locfin21) `[^\x00-\xff]$` stamps `RX_END_WINDOW "2"` while its
  search body is a bare `return 0` that applies no window (measured on this tree's
  build): a stamp naming a selection that was not emitted, the defect class DD-13c
  rules out. Population 0 in the census (all 71 `empty` rows stamp `"none"`), so it
  is reachable only off-corpus. The generated stamp rule corrects it at L2.1 (WINDOW
  is not asked on an `empty` path).
- **F-13** (new, `[r2.1 LR-G3]`) `RX_VM_PREFILTER_LANG` reads `"exact"` on 727 of the
  734 superset hybrids (19 bench / 708 corpus): its vocabulary names only the count
  collapse, so an atomic- or lookaround-erased prefilter stamps `"exact"`. This is
  `pf_know.md`'s "blind spot", now counted. Reading the whole erasure record would fix
  it and move the stamp on all 727 (a closed-vocabulary event for any bench reader);
  filed for a later abi event, not taken at L0 or L2 (D77: no reader is known to be
  misled today, `RX_VM_RESEED` carries the truth).
