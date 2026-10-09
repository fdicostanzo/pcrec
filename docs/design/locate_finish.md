# Search is LOCATE × FINISH — the model, the table, the family, and [OPT-REVEND] in it

**DESIGN NOTE, PROPOSED, REVISION 2, nothing built.** Revision 1: lane `locfin`,
2026-10-09, from main `525dec33` (abi 71). **Revision 2: lane `locfin2`, 2026-10-09,
from main `7efca415` (`src/` identical to `525dec33`, abi 71), applying the FULL D6
panel `../dev/reviews/2026-10-09-r-locfin-panel.md` (38 ids, every ACCEPT binding).
Read §R2 first**: it is the disposition table, one row per id, saying what changed
and where; every in-place edit carries an `[r2 <id>]` mark. Charter: D156 (Frank,
2026-10-09): *"look for the general rule to expand. We have dfa prefilter then vm
now. This is the same but the prefilter is reverse."* Nothing under `src/`, `cli/`,
`lib/`, `tests/` or `docs/spec/` changes. Evidence: `../../studies/locate_finish/`
(own CLAUDE.md; a compile-side census with FOUR controls since revision 2, the L0
edit set and its derived sabotage re-aims). A focused re-check by two critics (one
with the generality/unlocks lens) reviews this revision before any `src/` change.

Read before writing: D156; `where_to_start.md` §1-§3 (§2.2 step 1 is CORRECTED in
place by this revision, `[r2 E1]`); `start_table.md` rev 2.1 (§1.2-§1.6);
the shipped code at this pin (`src/gen/emit_dfa.c` `cand_rows` `:8160`,
`cand_nodes` `:8053`, `cand_select` `:8447`, `cand_read` `:323`, `dfa_matches`
`:7706`, `pcrec_emit_dfa_engine` `:11212`; `src/gen/emit_vm.c`'s hybrid entry
`:12703-12733`, `:13146-13426`); `revend.md` revision 2 (§R2, §0, §5.2 — superseded
here, §5.1); `litscan_k82h.md` (§1.1a, §3.1a, the rulings); `pf_know.md` §0-§3.

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
| C3 | A | L0's re-aims are DERIVED by the start_table edit-set method: `studies/locate_finish/l0_edit_set.tsv` (30 entries) through `start_table/sabotage_anchors.py` against a call graph regenerated at this pin: **6 re-aim (S566, S599, S606-S609), 18 re-run at L0, 98 after L0**; S222 is a re-run, not a re-aim (it sits in `dfa_search_start_name`, which L0 does not touch). The `empty` decision inside the two emitters (`emit_unanchored` `:9729`, `emit_attempt` `:10094`) is in the edit set (§5 L0). |
| C4 | A | G12 defers every FINISH row with no producer, so L0 ships NO unreached row; `run_cand_oracle.sh` gains a declared-unreached allowance file (one line per row, with its argument and the commit that gives it a producer; a row in the file that IS reached fails), first used by L2's `verify-attempt` (§5 L0, L2). |
| C5 | A | L0's sabotage plan is rebuilt (§5 L0): no declared-vs-derived posture plant (circular, and the declared column is deleted); new plants for `.hand` dropped (hand mandatory on a FINISH ask; a 0 hand aborts), the verify-anchored / search-from ORDER swapped, and F-2 reverted (a grep row: no row-POINTER compare in `src/gen`). F-3's plant no longer waits on a later landing: the boundary degrade is L0's, witnessed on a superset hybrid. |
| C6 | A | REQ_WHY gains ONE token, `"locator"` (no pre-check: the selected locator is not the composite); DFA_TABLE / DFA_UNIFORM_FOLDS / DFA_SCAN_EDGE / the orientation block fold over the machines the artifact EMITS, through one membership derivation (L2.0, a no-mover) — under form C the forward machine is absent and they read the reverse (+ anchored) machines; the supersession of `revend.md` §5.2 is recorded in BOTH notes (§5.1; `revend.md` gains a forward pointer). |
| C7 | A | pcrec-bench's `testees/pcrec/adapter.py`, `report.py` and `tools/selfcheck.py` are listed as READERS of DFA_SCAN/DFA_START (§5 L2); L2's deliverable includes an `[inbox]` adapter note to pcrec-bench and the window handshake. |
| C8 | A | §3.3 is corrected: the reader grep includes `pcrec_artifact_has_dfa_scan` (12 callers, `:3119`/`:3193` the `rx_info.scan`/`search_form` mirrors), `:10708` is dispositioned (it is `pcrec_artifact_has_dfa_scan` spelled locally), and the VM class is 15 lines, not 16. DFA_SCAN's machine-proxy readers join L2's reader list (§3.3, §5 L2). |
| C9 | A | Spec citations corrected: DFA_START is `match_api.md:788-796` and `:4829-4839`; `:4686-4703` is now the VM stamp block. Every DFA_SCAN value table that needs the fourth value is listed in L2's spec hunk (§5 L2). |
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
   or a superset by erasure). `[r2 G2]` It hands ONE result type, a product: a start
   interval `[s, t]`, a bit saying whether a match is PROVEN to start at `s`, and an
   end set `D` that contains the priority end at `s`. Revision 1's six types are
   points of it (`SPAN` = proven, `D = {e}`; `ENDSET` = proven, `|D| > 1`; `LOWER` =
   `[s, ∞)` unproven; `NOMATCH` = the empty interval; the caller's match-here = `[s, s]`
   unproven), and `CAND` is `LOWER` (`[r2 G1]`): "one try, then re-locate" vs "an
   attempt loop" is the re-entry policy RETRY already chooses. A superset locator's
   result degrades to `{LOWER, NOMATCH}` by one lattice projection. `[r2 G3]` A
   FINISHER is one of four actions — report, nomatch, verify-at `s`, search-from `s`
   — wearing the DFA or the VM hat of the route it runs on. Obligations O1-O10 are
   stated on the two axes (§1.4); give-up posture is two columns, a derived
   classification and a declared contract, with a give-up differential as the
   independent control (§1.5, `[r2 G7]`).
2. **The table (§2).** Two new slots of the ONE `cand_rows[]` (D151 add. 3 Q2):
   `LOCATE`, a BODY slot asked once per DFA-shaped body (and once by an artifact with
   no DFA body, on `CR_VM`), and `FINISH`, a slot block keyed (finisher route, shape),
   asked by each caller-facing entry. `[r2 G4]` FINISH is not new machinery: it
   promotes `cand_nodes`' VERIFIER/LOOP/CALLER and FOLDS `dfa_matches[]`, which is
   already a first-match choice with a deny (`-fno-anchored-dfa`). `[r2 C1]`
   Totality is keyed on (locator route, finisher route). `[r2 G6]` Relocate goes to
   the route's FALLBACK locate row with a lexicographic progress measure, checked on
   every succ cycle.
3. **The family (§3).** Every shipped start mechanism casts as (seed, direction,
   language) → a point of the product; the census puts every compiled artifact in
   exactly one of eleven (locator, finisher) pairs (bench 343, corpus 5,012), now under
   FOUR controls, all at 0 disagreements (§3.1, `[r2 C10]`). **No shipped output
   falls outside the product, so D156's revisit trigger does not fire**; revision 1's
   proposed wording amendment (add `CAND`, F-6) is WITHDRAWN (`[r2 G1]`).
4. **REVEND (§4).** `rev-end` is one LOCATE row (route `CR_DFA`, predicate `end_pin`,
   deny `-fno-rev-end`); its tie arms are FINISH's `verify-anchored` (T2) and
   `search-from` (T3) rows — the folded `dfa_matches[]` — and whether a tie can arise
   (`nl_last`, T1) is a property of the row's hand shapes. Stage 2 (captures) is the
   same row with the VM hat; NEUTRAL by window identity (E9 upheld it: 0 / 5,199,120)
   but FILED on its population (0 bench / 13 corpus). Its PRESENCE deference is a read
   on `dominated`, not a new row (`[r2 G9]`). The relaxed-reverse locator is sound with
   the reference's own fold, the union over `refs[]`, the closure on the lowered set
   and every Σ* source gated (`[r2 E4-E7]`): FILED. rev-inner needs `S` free of
   references into `P` (`[r2 E1]`, G4), or it hands `LOWER` to the attempt loop.
5. **Build (§5).** L0, a no-mover cut to the panel's list (`[r2 G12]`), its re-aims
   DERIVED (6 re-aim, 18 re-run, `[r2 C3]`); L1 = `revend.md` S0+S1; L2 = REVEND stage
   1, the abi 71 → 72 event, as three separable commits (L2.0 the machine-membership
   no-mover, L2.1 D-2's `attempt-start`, L2.2 `rev-end`) with the bench adapter note
   (`[r2 C7]`); `[GIVEUP-DIFF]` before any VM-finisher LOCATE row; L3-L5 FILED. The
   stamp rule (§5.1) names the locator once, on `RX_DFA_SCAN`, adds one REQ_WHY token
   and supersedes `revend.md` §5.2 (`[r2 C6]`).
6. **Questions (§8)** restated under the revised model: L0's place, stage 2, the stamp
   RULE, the one-way spec sentence, the relaxed locator's deny, rev-inner's reduced
   VM value after E1, and the ATTEMPT match-here form the fold exposes.

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

### 1.2 The result is a product `[r2 G2]`

A locator hands `r = (I, p, D)`, relative to its accepted lower bound `lo`:

| component | meaning | the locator's obligation |
|---|---|---|
| `I = [s, t]` | every match start ≥ `lo` lies in `I`; `t` may be `∞` | no match starts in `[lo, s)` and none above `t`; `I = ∅` (written `s > t`) means NO match from `lo` |
| `p` | proven: a match DOES start at `s` | under `p`, `s` is the leftmost start ≥ `lo` (O1); without `p`, nothing about `s` beyond the bound |
| `D` | a set of positions that contains the PRIORITY end of the match at `s` | meaningful under `p`; `D = ⊤` means "unknown" (every position ≥ `s`) |

Revision 1's types are points of it, and the FINISH key is the SHAPE of the point,
a five-valued projection:

| shape (FINISH key) | point | rev 1 type | shipped producer |
|---|---|---|---|
| `NOMATCH` | `I = ∅` | `NOMATCH` | PRESENCE / WIDTH verdicts, the empty engine |
| `SPAN` | `p`, `D = {e}` | `SPAN` | the composite's RECOVER (exact language) |
| `ENDSET` | `p`, `\|D\| > 1` | `ENDSET` | `rev-end`'s tie (L2); **no cap on `\|D\|`** |
| `LOWER` | `¬p`, `t = ∞` | `LOWER` **and** `CAND` (`[r2 G1]`) | WINDOW W1, FIRST's handoff, RETRY's re-seed, the VM-route composite, any superset locator |
| `AT` | `¬p`, `I = [s, s]` | (none in rev 1) | the `caller` locator of the match-here entry (`[r2 C1]`) |

**`CAND` is `LOWER` `[r2 G1]`.** Their obligation cells were identical in
revision 1's matrix (O1 O5-O9 vs O5 O6 O9, the difference being O1, which is a
property of the FINISHER that reads the start, not of the hand). "One anchored try,
then re-locate" versus "an attempt loop from `s`" is a RE-ENTRY POLICY, and the
table already has the slot that chooses it: RETRY (`exact` / `clamped` re-seed vs
`fixed` step vs `adaptive`), and the composite's own verifier resume (NEXT's
re-seed). In code, `CT_CAND` stays as the spelling of NEXT → VERIFIER inside the
composite (an edge that never crosses the LOCATE → FINISH boundary); at the boundary
there is no `CAND`.

**Degradation is a lattice projection.** Order points by information: `r ⊑ r′`
(`r′` says no more than `r`) iff `I ⊆ I′`, `p ≥ p′` and `D ⊆ D′`. A locator over a
SUPERSET language `L′ ⊇ L` hands `degrade(r) = ([s, ∞), ¬p, ⊤)`, or `∅` unchanged:
the leftmost `L′` start is ≤ the leftmost `L` start (every `L` match is an `L′` match
with the same span), so the lower bound survives; nothing else does — not `p` (an
`L′` match at `s` proves no `L` match), not `t` (the `L` start may be anywhere above),
not `D` (`atomic_groups_design.md`'s 122 refuting cells; the `mrl_win` gate). And
`NOMATCH` survives (`L ⊆ L′`). So a superset locator hands `{LOWER, NOMATCH}`
(`[r2 G1]`; revision 1's "at most `CAND`" and §4.5's `LOWER` were the same claim
spelled twice). `pf_know.md` §0 measured exactly this split: the START is a sound
lower bound on every hybrid, the span exact only under `Vm.mrl_win`.

**Where the projection is applied `[r2 C1]`.** At the LOCATE → FINISH boundary,
not on a row. The composite's RECOVER hands `SPAN` truthfully OF ITS BODY'S
LANGUAGE (the body is the capture-erased, possibly erased-further pattern); whether
that language is `L` is a fact about the body, `cand_lang_exact(cx) =
fit.chosen == ENGM_DFA || pcrec_vm_prefilter_window(cx)`, and the boundary applies
`degrade` where it is false. `pcrec_vm_prefilter_window` takes a `Ctx` and is the
function `Vm.mrl_win` is assigned from (`emit_vm.c:10368`), so the boundary needs no
`Vm`, and the census's control C4 holds the derivation against the independent
`RX_VM_RESEED "exact"` stamp (759 / 734, 0 disagreements, §3.1). Revision 1's F-3
("the inlined RECOVER declares `CT_START` where it hands `CAND`") was right about the
effect and wrong about the fix: no RECOVER row changes; the boundary does.

**What becomes of the remaining enum bits** (spellings in code stay, per G2):

| bit | today | in the product |
|---|---|---|
| `CT_LOWER` | WINDOW, FIRST, RETRY hands; most slots accept | the `LOWER` shape; inside the composite, unchanged |
| `CT_UPPER` | BOUND → LOOP | the interval's `t`; stays the spelling of BOUND → LOOP inside the composite. No locator hands `t < ∞` across the boundary except `caller` (`AT`); `[OPT-VMSEED]` stage 4's seed window would be the first (§7) |
| `CT_CAND` | NEXT, RETRY hand; RETRY, VERIFIER accept | `LOWER` (G1); kept only as NEXT → VERIFIER's spelling inside the composite |
| `CT_WINDOW` | accepted by VERIFIER, handed by NO row | **deleted at L0** (`[r2 G2, C12]`); the ceiling a VM verifier reads is `max(D)` of a `SPAN`/`ENDSET`, and O4 states its obligation |
| `CT_VERDICT` | PRESENCE / WIDTH → CALLER | the `NOMATCH` shape (or "pass", the bound unchanged) |
| `CT_HIT` | PRESENCE → FIRST | inside the composite only (the gate's landmark); not a locator output |
| `CT_START` | RECOVER → CALLER | the `SPAN` shape's `s` |
| `CT_ENDSET` (new, L2) | — | the `ENDSET` shape |

### 1.3 FINISH: four actions, two hats `[r2 G3, G4]`

A finisher consumes one shape and returns the answer, or relocates. Its ACTION is
chosen by the shape; its HAT by the route it runs on (the entry's: `cand_finish_of`,
§2.6), which is D156's "capture need" (the VM hat iff `fit.chosen == ENGM_VM`).

| action | takes | DFA hat (`CR_DFA` / `CR_ATTEMPT`) | VM hat (`CR_VM`) | shipped today as |
|---|---|---|---|---|
| **report** | `SPAN` | return `(s, e)` | — (the VM must write groups ≥ 1: verify-at instead) | every DFA artifact's return (CALLER) |
| **nomatch** | `NOMATCH` | return 0 | return 0 | PRESENCE / WIDTH verdicts, the empty engine (CALLER) |
| **verify-at `s`** | `SPAN` (VM), `ENDSET`, `AT` | the anchored machine from `s`: `adfa` on `CR_DFA` (built only under `anchored_ok`, deny `-fno-anchored-dfa`), the attempt machine itself on `CR_ATTEMPT` (always built) | one anchored VM attempt at `s`, ceiling `max(D)` where the artifact clamps, `n` otherwise | `dfa_matches[0]` `unwrapped`; ATTEMPT's fused per-candidate run (VERIFIER); the exact hybrid's attempt at `window[0][0]`; the VM's `_match` |
| **search-from `s`** | `ENDSET`, `LOWER`, `AT` | the route's FALLBACK locate row (the composite) from `lo = s`, filtered to `I` (a start above `t` is NOMATCH) | the attempt loop from `s`; its loop head re-locates through the inlined composite where a prefilter exists; RETRY on failure | `dfa_matches[1]` `search-filter` (`AT`, `t = s`); the VM-only loop and the inexact hybrid (LOOP + RETRY) |

`cand_nodes`' VERIFIER, LOOP and CALLER are not separate successors of FINISH: they
ARE its actions (VERIFIER = verify-at, LOOP = search-from's VM hat, CALLER = report /
nomatch). After L0 "verify a candidate" has ONE home. D156's finisher list (return,
anchored DFA run, VM over the span, VM search from a lower bound) is the same four
actions with the hats spelled out; the one D156 does not name, relocate, is
search-from with the DFA hat — shipped twice already (the K82 handoff's `LOWER` into
NEXT inside the composite, and `search-filter`). Revision 1's F6 ("vm-relocate") is
search-from with the VM hat entered at its loop head (§4.3).

### 1.4 The exactness obligations, on the two axes `[r2 G2]`

- **O1 leftmost-first start.** Under `p`, `s` is the smallest start ≥ `lo` of any
  match of the LOCATOR's language; it is the answer's start iff that language is `L`
  (§1.2's boundary projection). PCRE2 takes the smallest start with any match;
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

**The pair matrix on the two axes.** Rows are shapes, columns actions; a dash is a
pair FINISH never forms.

| shape ↓ / action → | report | nomatch | verify-at | search-from |
|---|---|---|---|---|
| `SPAN` | DFA: O1 O2 O5-O7 | — | VM: O1-O7, ceiling `e` (O4 NEUTRAL by window identity) | — |
| `ENDSET` | — | — | DFA: O1 O2 O5-O8; VM: O1-O8, ceiling `max(D)` only where unclamped (§4.3) | O1 O5-O9; VM: the loop head's priority end is the ceiling |
| `LOWER` | — | — | — | O3-O7 O9 (VM: O4 ONE_WAY when it skips) |
| `AT` | — | — | O1-O3 O5-O7 (DFA: `unwrapped`; VM: the VM's `_match`) | DFA: O5-O7, filter `start == s` |
| `NOMATCH` | — | O5 | — | — |

### 1.5 The give-up posture: two columns `[r2 G7]`

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
- **Contract (declared, checked).** `.contract = CG_FIXED` where a ruling forbids any
  move of the give-up surface (today: the handoff, K82 Q10). An unset contract is a
  wildcard (memory `pcrec-no-silent-defaults`: an unused field is a wildcard, not a
  presumed value). The CHECK is behavioural (below), not a comparison of two columns.
- **The independent control: a give-up differential.** For each row with a deny
  flag on a VM route, compile every witness twice (default, deny), run each at a swept
  budget ladder (steps and work, `budget` directives, ~19 points, `E3`'s shape), and
  compare the per-budget outcome (answer vs give-up): FIXED and NEUTRAL require
  identical outcome sets; ONE_WAY allows default-answers-where-deny-gives-up and
  forbids the converse. Witnesses: K82h §3.1a's 35 budget / `gu` blocks (all VM, no
  DFA scan), plus the VM-only end-window witnesses (T6a's 13 start-unanchored), plus
  one constructed witness per ONE_WAY row. It reads ANSWERS, so it shares no source
  with the table. Built as row `[GIVEUP-DIFF]` (§5), before the first VM-finisher
  LOCATE row. **Classification of today's rows** (by the rule; the instrument confirms):
  W1 `window` ONE_WAY (VM-only and collapsed classes covered); PRESENCE `set-leads` /
  `emitted` ONE_WAY on `CR_VM`; `presence-none`, `one-attempt`, `dominated` NEUTRAL
  (no check emitted); WIDTH `ceiling` ONE_WAY; NEXT `first-class` ONE_WAY; BOUND
  `vm-anchored`/`vm-gstart` ONE_WAY; RETRY `adaptive*` ONE_WAY, `exact`/`clamped`/
  `anchored`/`fixed` NEUTRAL; FIRST `handoff` NEUTRAL on its population (every hybrid
  mover's prefilter is `exact`, K82h §3.1a) with contract FIXED.

**Where to attack §1.** (a) A shipped or filed locator whose output is not a point
of the product. (b) The boundary projection: a body whose `cand_lang_exact` is true
but whose RECOVER span is not `L`'s (an erasure `pcrec_vm_prefilter_window` misses).
(c) O4(ii): a ceiling source that is not `max(D)` of a proven point. (d) The progress
measure (O9): a relocate whose target rank does not exceed the handing row's.
(e) §1.5's classification rule on a row that both adds and removes attempts.

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

### 2.2 Two new slots, in the one array `[r2 G5]`

**FINISH is a SLOT BLOCK of `cand_rows[]`** (D151 addendum 3, Q2: "otherwise logic is
spread around"). The panel answered revision 1's Q1 with G4(b): FINISH already has a
real first-match choice with a deny — `dfa_matches[]` — so it is a table in its own
right, and the one array keeps its listing (per take-set), its trace record (with the
`hand` field) and its typed edges in the walk and the self-check that already exist;
a separate array would duplicate the walk, the listing projection and the trace, and
split the typed-edge check across two arrays.

| slot | the question | asked at | routes | accepts / hands |
|---|---|---|---|---|
| `LOCATE` (first) | which walk produces the result? | each DFA-shaped body, once (the entry body AND the hybrid's inlined `<p>_prefilter`, both via `pcrec_emit_dfa_engine`), on the body's route; an artifact with NO DFA body, once, on `CR_VM` (`cand_locate_route`, §2.6) | `CR_DFA`, `CR_ATTEMPT`, `CR_VM` | accepts `LOWER` (E1, and relocate); hands its declared shape set to FINISH across the boundary projection |
| `FINISH` (last) | which action, in which hat, finishes this shape? | each caller-facing entry, once per shape its locator can hand: `<prefix>_search` (shapes from LOCATE), `<prefix>_match`/`_match_caps` (shape `AT` from `caller`) | `CR_DFA`, `CR_ATTEMPT` (DFA hat), `CR_VM` (VM hat) | accepts the five shapes; hands to the CALLER, relocates `LOWER` to LOCATE |

`CandSel` gains `hand` (the shape being finished) and FINISH rows declare
`u.finish.take`; `cand_select` filters `take & s->hand` on the FINISH slot exactly as
it filters the route. **`hand` is MANDATORY on a FINISH ask**: a FINISH ask with
`hand == 0` aborts (a check, not a default), and no other slot reads it (`[r2 C5]`).
The selection's second key, the LOCATOR's route, is a `CandSel` field too
(`lroute`), read by predicates only (§2.3).

### 2.3 The FINISH table (design of record), totality on (locator route, finisher route) `[r2 C1, G3, G12]`

First match per (finisher route, shape). Rows marked L0 exist at L0 (the
`dfa_matches[]` fold); the others land with the producer that gives them a choice.

| # | row | action / hat | takes | finisher routes | deny | predicate | lands |
|---|---|---|---|---|---|---|---|
| F1 | `nomatch` | nomatch | `NOMATCH` | all | — | always | L2 |
| F2 | `report` | report / DFA | `SPAN` | DFA, ATTEMPT | — | always | L2 |
| F3 | `verify-anchored` | verify-at / DFA (`adfa`) | `ENDSET`, `AT` | DFA | `PCREC_NO_ANCHORED_DFA` | `match_unwrapped_applies` (`anchored_ok ∧ ¬empty`, today's `dfa_matches[0]`) | **L0** (`AT`); `ENDSET` at L2 |
| F4 | `verify-attempt` | verify-at / DFA (attempt machine) | `ENDSET` | ATTEMPT | — | always (the machine exists on the route) | L2, DECLARED UNREACHED (no ENDSET producer on `CR_ATTEMPT`) |
| F5 | `search-from` | search-from / DFA | `ENDSET`, `LOWER`, `AT` | DFA, ATTEMPT | — | always | **L0** (`AT`, today's `dfa_matches[1]`); `ENDSET`/`LOWER` at L2 |
| F6 | `verify-vm` | verify-at / VM | `SPAN`, `AT` | VM | — | always | L3 (`AT` is the VM's own `_match`, not routed through the table until a choice exists) |
| F7 | `search-vm` | search-from / VM | `ENDSET`, `LOWER` | VM | — | always | L3 |

**Why F4 does not take `AT` (and the finding behind it).** On `CR_ATTEMPT` the
match-here entry is `search-filter` today (`anchored_ok` is never set on ENG_ATTEMPT:
`build_anchored_dfa` is called only on the ENG_UNANCH branch, `compile.c:2540`), so an
ATTEMPT artifact's `_match` runs the WHOLE search from `s` and discards a later start
— O(n) on a failing call where one anchored run of the attempt machine would answer.
Letting F4 take `AT` is a real improvement and a MOVER (308 corpus / 20 bench
`DFA_MATCH "search-filter"` artifacts change form; answers identical), which is
`anchored_match_unwrapped.md` §10's already-filed "ENG_ATTEMPT's own match-here form".
L0 is a no-mover, so F4 takes `ENDSET` only; §8 Q7 carries the mover.

**Totality** is checked on the triples that occur, not on (route, type):

| locator route → finisher route | who | shapes the locators can hand (after the boundary projection) | last row taking each |
|---|---|---|---|
| `CR_DFA` → `CR_DFA` | DFA artifact, ENG_UNANCH | `SPAN`, `NOMATCH`; `ENDSET` (rev-end, L2) | F2, F1, F5 |
| `CR_ATTEMPT` → `CR_ATTEMPT` | DFA artifact, ENG_ATTEMPT | `SPAN`, `NOMATCH` | F2, F1 |
| `caller` → `CR_DFA` / `CR_ATTEMPT` | the match-here entry | `AT` | F5 |
| `CR_DFA` / `CR_ATTEMPT` → `CR_VM` | the hybrid | `SPAN` (exact body), `LOWER` (superset body, projected), `NOMATCH`; `ENDSET` (stage 2) | F6, F7, F1, F7 |
| `CR_VM` → `CR_VM` | VM-only | `LOWER`, `NOMATCH` (the WIDTH / PRESENCE verdicts inside the composite, `[r2 C12]`) | F7, F1 |

The self-check's existing totality test ("every asked (slot, route) ends in an
undeniable `cand_always` row") is extended: for every (locator route, finisher route)
pair in the table above and every shape some LOCATE row on that locator route hands
(projected where `cand_lang_exact` can be false on that pair), the last FINISH row on
the finisher route taking that shape is undeniable and `cand_always`. A later LOCATE
row that hands a shape no FINISH row takes fails the self-check, not the compile.

### 2.4 The LOCATE table `[r2 G8, G12]`

| # | row | routes | deny | predicate | hands | lands |
|---|---|---|---|---|---|---|
| A1 | `empty` | DFA, ATTEMPT | — | `dfa_engine_is_empty`'s old body | `NOMATCH` | **L0** |
| A2 | `rev-end` | DFA | `PCREC_NO_REV_END` | `end_pin ≠ NONE` ∧ the stage-1 conjunct (§4.1) | `SPAN`, `NOMATCH`, `ENDSET` iff `nl_last` | L2 |
| — | `rev-inner[-bounded]` | DFA, VM | its own | G1 ∧ G2 ∧ G3, and G4 for `SPAN`-producing hats (§4.6) | `SPAN`/`NOMATCH`, or `LOWER` without G4 | filed (D151) |
| — | `rev-end-relaxed` | VM | its own | §4.5's gate | `LOWER`, `NOMATCH` | filed |
| A3 | `composite` | DFA, ATTEMPT, VM | — | always | by route: fwd+rev (`SPAN`/`NOMATCH`), candidate loop with fused verify (`SPAN`/`NOMATCH`), the VM attempt loop's front (`LOWER`/`NOMATCH`) | **L0** |

`empty` and WIDTH `ceiling` are one "nothing fits → NOMATCH" family (G8): the first is
a static verdict on the body's language, the second a per-call comparison of the
remaining subject with the root minimum width. They stay in their slots at L0 (moving
the WIDTH test into LOCATE would make LOCATE's VM arm a per-call test, which is a
second shape for the slot); the family is recorded so that a third member is a
one-row edit, not a third spelling.

**The route is NOT a projection of LOCATE.** The route (`cand_route_of`,
`job->engine`) says which MACHINES the compile built; LOCATE says which WALK over
them the search uses. Today each route has one walk (A3's three hats; A1 a special
case on two); `rev-end` is the first second walk on a route.

### 2.5 What changes in the handoff graph `[r2 G4, G6, C2, C12]`

- **Nodes.** `LOCATE` and `FINISH` join `cand_nodes[]`. VERIFIER, LOOP and CALLER
  stay as NODES inside the composite (NEXT → VERIFIER, BOUND → LOOP, PRESENCE/WIDTH
  → CALLER for the in-composite verdict) — they are the same actions FINISH's rows
  emit, and FINISH's rows NAME them as their action (`u.finish.act` ∈ {REPORT,
  NOMATCH, VERIFY, SEARCH}). VERIFIER's accept set loses `CT_WINDOW`.
- **E-LF** LOCATE → FINISH, typed by the LOCATE row's shape set, through the boundary
  projection (§1.2). RECOVER's successor becomes FINISH (the composite's output
  crosses the boundary there); PRESENCE/WIDTH keep CALLER for the in-composite verdict.
- **E-FL** FINISH `search-from` → LOCATE: relocate. Target: the FALLBACK row of the
  finisher's locator route — the last undeniable `cand_always` LOCATE row on it,
  today always `composite` — never "the next row in table order" (`[r2 G6]`: every
  concrete relocate in revision 1 targeted the composite; a fallback ladder inside a
  first-match table would need a second walk `cand_select` cannot do, `[r2 C2]`).
  `lo := s`; `\G` keeps the caller's `search_from` (`[r2 E8]`).
- **E-FR** FINISH `search-vm` → RETRY: a failed attempt; today's E7/E8, renamed.
- **The progress check `[r2 C2, G6]`.** Each re-entry edge carries a progress class:
  `RANK` (relocate: the target row's rank exceeds the handing row's on the same
  locator route; a relocate whose handing row IS the fallback row is a self-check
  failure) or `RAISE` (`lo` strictly increases: E5, E7, E8, E11, find-all). The
  self-check computes, over the row-level graph (LOCATE rows × FINISH rows × the
  composite's internal re-entries), that removing every `RAISE` edge leaves the graph
  ACYCLIC, and that every `RANK` edge satisfies its rank inequality. Revision 1's
  self-check tested cycles only in the selection-READS graph, so E-FL's cycle was
  unchecked.
- **`revend.md`'s E13 (WINDOW → CALLER) stays withdrawn**: REVEND's result travels
  E-LF.
- **E6** (the hybrid's prefilter → the VM loop) is E-LF on an inlined body:
  LOCATE (on `CR_DFA`/`CR_ATTEMPT`) → FINISH (on `CR_VM`), the same edge as the
  DFA-only artifact's with a different hat — D156's "REVEND with captures is
  reverse-from-end × the same finisher".

### 2.6 Routes, X4, and the hybrid `[r2 C1, C2]`

Three route derivations, each ONE function:

- `cand_route_of(cx)` (shipped): the BODY's route, `CR_ATTEMPT` iff ENG_ATTEMPT, else
  `CR_DFA`. Meaningful only where a DFA body exists.
- `cand_locate_route(cx)` (new, L0): `pcrec_artifact_has_dfa_scan(cx) ?
  cand_route_of(cx) : CAND_ROUTE_VM`. The route LOCATE is asked on by the search
  entry. It is what keeps `composite`'s VM arm off hybrids (`[r2 C2]`): a hybrid asks
  LOCATE once, from its inlined body, on the body's route.
- `cand_finish_of(cx)` (new, L0): `fit.chosen == ENGM_DFA ? cand_route_of(cx) :
  CAND_ROUTE_VM`. The finisher's route: "is the finisher a DFA finisher on this
  entry?", the one question the ten reads of §3.3 ask.

X4 required REVEND's row to be route-independent because WINDOW is an ENTRY slot. As
a LOCATE row the question changes: LOCATE is a BODY slot, asked once per body on that
body's route, and `rev-end`'s route mask is `CR_DFA` because only an ENG_UNANCH body
has a reverse machine. Its predicate reads no `s->route` (bar the stage-1 conjunct),
so the inlined prefilter of a hybrid ASKS LOCATE on `CR_DFA` exactly as a DFA-only
body does, and FINISH, keyed on the finisher route, decides whether the result goes
to the caller or the VM.

**Where to attack §2.** (a) Does `cand_select`'s first-match per (slot, route)
extend to (slot, route, hand) without a second walk? (`take & hand` is a filter like
the route mask; the predicate reads `lroute`.) (b) The inlined body is called from
three places (entry, RETRY's recompute, the adaptive re-seed, `emit_vm.c:13261-13327`,
`:13396`); a walk there must answer the same at every call (§4.3). (c) Totality over
the triple table: a (locator route, finisher route) pair missing from it. (d) The
progress check on a relocate from a FUTURE second fallback (a route with two
undeniable rows).

---

## 3. The family survey (D156 item (c))

### 3.1 Today's pairs, measured (`studies/locate_finish/results/summary.txt`)

Population: every bench export (367; 343 compile) and every `.rxt` pattern block
(5,431; 5,012 compile, 4,191 distinct), `src` at `525dec33` (= `7efca415`), each
compiled as its own testee/block does. **Four controls `[r2 C10]`**, each sharing no
source with what it checks, the script exiting 1 on any disagreement:

| control | checks | against | result |
|---|---|---|---|
| C1 | the reverse-machine stamp | the emitted text (any `rx_reverse_` identifier) | 0 / 5,355 |
| C2 | the hybrid stamp | the text (`rx_prefilter(`) | 0 / 5,355 |
| C3 (two-sided, `[r2 C10]`) | forward: shipped `end_window` numeric ⇒ the borrowed probe (a copy of `ew_walk`) pins; converse: probe pinned ∧ width finite ⇒ shipped numeric | `src/facts/endwin.c` vs the probe | forward 0 / 400 (+ width direction: 262 agree, 138 a DECLARED probe-blind exception — the probe never expands calls, e.g. `^(a\|b)\g<1>$`); converse 0 disagreements outside two DECLARED exceptions that are the shipped fact's own declines: 22 multibyte rows (16 distinct, e.g. `^.{5}$` utf8), 2 `\G` (`\G\z`, `\G$`) |
| C4 (new, `[r2 C10]`) | the census's exact / superset hybrid classifier (`RX_VM_PREFILTER_LANG` + the `kinds` fact's atomic / lookaround bits) | the independent stamp `RX_VM_RESEED == "exact"` (the RETRY row whose predicate is `Vm.mrl_win`) | 759 exact / 734 superset, 0 disagreements; superset rows stamp `adaptive` 466, `clamped` 173, `anchored` 58, `adaptive-dense` 37; non-exact reasons: language 7, atomic 250, lookaround 515 (both kind spellings live) |

The re-run (lane locfin2) moved no existing table line; only the control blocks were
added.

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
| hybrid prefilter, exact | as above | as above | capture-erased = `L` | `SPAN` | route class + `mrl_win` | `composite` × verify-vm |
| hybrid prefilter, superset | as above | as above | `L′ ⊋ L` | `SPAN` of `L′`, projected to `LOWER` | route class + `mrl_win` | `composite` × search-vm |
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
| RETRY | the failed attempt + K49 | — | — | `LOWER` (re-locate or step: policy) | RETRY R1-R6 | search-vm's re-entry |
| the match-here entry | the caller's position | — | — | `AT` | `dfa_matches[]` (axis G) | `caller` × FINISH F3 / F5 |
| [OPT-REVEND] (L2) | `n`, `n − 1` | rev | exact, whole | `SPAN`/`ENDSET`/`NOMATCH` | — | LOCATE `rev-end` |
| rev-inner (filed) | landmark hits `j` | rev | exact, prefix `P` | `SPAN`/`NOMATCH` under G4, else `LOWER` | — | LOCATE (§4.6) |
| relaxed reverse (filed) | `n`, `n − 1` | rev | `L′ ⊇ L` (§4.5) | `LOWER`, `NOMATCH` | — | LOCATE (§4.5) |

**Which output is not a point of the product: none.** D156's trigger does not fire.

### 3.3 Where the FINISH decision is spelled today `[r2 C8]`

`studies/locate_finish/finish_sites.sh` lists every CODE line under `src/gen/` that
tests `fit.chosen`, `fit.prefilter` or `prefn`: 32 lines. Revision 2 adds the
`pcrec_artifact_has_dfa_scan` callers, which revision 1's grep missed. Dispositioned:

| class | lines | what they decide | after L0 |
|---|---|---|---|
| **FINISH reads** ("is the finisher a DFA finisher on this entry?") | `emit_dfa.c:1650` (the dead-group fill), `:1728` (the startpos guard on the caller-facing body), `:3145` (`rx_info.match_form`), `:9768`, `:9769` (trace), `:9784` (`emit_unanchored`'s entry gate), `:10068`, `:10070` (trace), `:10083` (`emit_attempt`'s), `:10707` (`vm`, the orientation block) | 10 lines, 6 decisions, one question | read `cand_finish_of` |
| **"does a DFA body exist"** (`pcrec_artifact_has_dfa_scan`, 12 callers) | `emit_dfa.c:439` (the definition), `:1094`, `:1362`, `:1492`/`:1501`/`:1505` (PRESENCE's gate need and its trace), `:6972`, `:7049`, `:7102`, `:7355`; the `rx_info.scan`/`prefilter` mirror `:3119` and the `search_form` mirror `:3193`; `emit_vm.c:11330` (the hybrid's DFA stamps); plus `:10708` (`prefilter`, which with `:10707` spells `(!vm \|\| prefilter)` = this predicate locally) and `:10922` (`dfa_body`, the same predicate spelled a third way) | the existence of a LOCATE ask on a DFA route | unchanged at L0 except `:10708` and `:10922`, which read the predicate (they are in L0's edit set by text); `cand_locate_route` reads it |
| route-class reads inside predicates (start_table §2.3's third axis) | `:6847` (N7), `:7155`, `:7159` (P2), `:7360` (F1's (d′)) | stay (not FINISH) | unchanged |
| the VM finisher's locator calls and exactness | `emit_vm.c:3645` (`mrl_win`, the body's language), `:11071`, `:11182`, `:11218` (stamps, the RETRY plan), `:12703-12733` (emit the inlined locator), `:13261-13327` (RETRY's re-locate), `:13393-13404` (the entry's locate call, E6) | **15 lines** (revision 1 said 16) that ARE the VM hat's implementation | unchanged at L0 |

So the finisher choice is one question asked at six decisions in two emitters, and
"does a body exist" is spelled at least three ways (`pcrec_artifact_has_dfa_scan`,
`(!vm || prefilter)` at `:10707-10708`, `dfa_body` at `:10922`). L0 gives the first
ONE derivation, `cand_finish_of(cx)` (the `cand_route_of` precedent), and points the
two local re-spellings of the second at the shared predicate.

### 3.4 The ≥3 rule, and the `dfa_matches[]` fold `[r2 G4, C1]`

FINISH's shipped members (report, nomatch, verify-at in three hats, search-from in
two) are all dispersed; the house rule (memory `pcrec-forest-for-trees`) asks for the
unified table at three, and §2.3 is that table. **`dfa_matches[]` is not "read" by
FINISH (revision 1); it IS FINISH's existing first-match block** and folds in: the
match-here entry's locator is `caller`, its shape `AT = ([s, s], ¬p, ⊤)`, and its two
rows are F3 `verify-anchored` (the anchored machine; deny `-fno-anchored-dfa`; its
predicate `match_unwrapped_applies`, moved verbatim) and F5 `search-from` (the search
entry from `s`, filtered to `start == s`). Axis J's C3 precedent (`dfa_search_starts[]`
deleted into RECOVER's rows) is the shape: the table goes, its rows stay, the
`--list-axes` `match` axis is the rows' `list[route]` projection with identical bytes,
and `<PREFIX>_DFA_MATCH` / `rx_info.match_form` read the selected row's listed name.
**F-2 dissolves**: `dfa_match_is_unwrapped` (`emit_dfa.c:7727`) compared the selected
row's POINTER to `&dfa_matches[0]`, the shape `start_table.md` sound-m2 removed from
RECOVER; after the fold it reads `u.finish.act == CAND_FIN_VERIFY`, and the table that
pointer pointed into no longer exists.

**Where to attack §3.** (a) C4 says the classifier and `RX_VM_RESEED` agree on every
hybrid; is there a fourth erasure neither sees (both read `mrl_win`'s inputs
differently: the classifier the stamps, the stamp the function)? (b) §3.3's
dispositions: a FINISH read the greps still miss. (c) The fold: does any reader
compare `dfa_match_name` to a string outside the two stamps?

---

## 4. REVEND in this frame (D156 item (d))

### 4.1 The locator row `[r2 G11]`

```
{ .c = { "rev-end", PCREC_NO_REV_END, cand_rev_end_applies },
  .slot = CAND_SLOT_LOCATE, .routes = CR_DFA, .tok = "rev-end",
  .map = CM_EXACTREV, .hands = CT_START | CT_VERDICT | CT_ENDSET /* ENDSET iff nl_last */,
  .list = { [CAND_ROUTE_DFA] = { "locate", 1, "rev-end", PCREC_NO_REV_END } },
  .desc = "...end_pin...", .u.locate = { .walk = CAND_WALK_REV_END, .whole = true } }

static bool cand_rev_end_applies(const CandSel *s)
{
    if (pcrec_fact_end_pin(s->cx) == PCREC_EPIN_NONE) return false;  /* R1 */
    return cand_finish_of(s->cx) != CAND_ROUTE_VM;                     /* stage-1 conjunct */
}
```

`revend.md` §2.3's four conjuncts: R1 is the predicate; R2 (`cand_route_of ==
CAND_ROUTE_DFA`) is the route mask `CR_DFA`; R4 (`!dfa_engine_is_empty`, X11) is row
order (`empty` precedes `rev-end`); R3 (`fit.chosen == ENGM_DFA`) is the ONE
remaining conjunct, now a read of `cand_finish_of` (`[r2 G11]`: it is one of the
reads §3.3 centralizes), and exactly stage 2's switch. X3's assertion (RECOVER never
`pinned` under `end_pin`) stays at the walk's emission and is measured too (census
T4: 0 / 5,012). The emitted walk is `revend.md` §5.1's text; the helper is §8's.

### 4.2 The tie table is FINISH

| `revend.md` | here |
|---|---|
| T1 `no-tie` (`\z`, or `nl_last` false) | the row's shape set omits `ENDSET`: FINISH is asked for `SPAN`/`NOMATCH` only (F2, F1) and no tie code is emitted |
| T2 `anchored` (`DFA_MATCH "unwrapped"`) | F3 `verify-anchored` on `ENDSET` — the same row the match-here entry selects, now with a second shape |
| T3 `body` (`"search-filter"`) | F5 `search-from` on `ENDSET`: relocate to `composite` from `s*` |

`nl_last` stays as `revend.md` defines it (on the BUILT reverse machine); it decides
the shape set, so it is a LOCATE-row property, and its sabotage row (revend §9.2 row
10) is unchanged. E11 upheld this table (18 form-C twins, 0 / 1,682,892 cells, 0 vs
libpcre2).

### 4.3 Stage 2: the same locator with the VM hat `[r2 G9, C11, E3]`

**What it is.** Drop the stage-1 conjunct. The hybrid's inlined `<p>_prefilter` asks
LOCATE on `CR_DFA` and selects `rev-end` exactly where a DFA-only body would; the VM
entry asks FINISH on `CR_VM` and gets F6 `verify-vm` (`SPAN`) or F7 `search-vm`
(`ENDSET`, the projected `LOWER`). The reverse tables are already there (census T2:
39 bench / 1,192 corpus `P-fwdrev` hybrids; C1 confirms by text).

**Its classification is NEUTRAL** (correcting `revend.md` §3.9's ONE_WAY), and E9
upheld it as the round's best-evidenced result: walk vs shipped prefilter on 48
hybrids (exact, clamped, ties, views, `\K`, `-i`, supersets, collapsed, X1, utf8),
every string to length 6-7 at every `lo`: 0 / 5,199,120 window diffs, 0 capture
diffs, 0 / 4,565,716 vs libpcre2, 0 / 719,283 find-all, ASan clean. The argument
stays: the inlined body is the DFA emitter's output for the capture-erased pattern
(STRUCTURAL), the walk's span equals that body's on every call (MEASURED), so the
VM's (start, ceiling) pairs are the same (O4(i) equality), PROVIDED an `ENDSET` on a
CLAMPED hybrid goes to F7 (whose loop head relocates through the composite for the
priority end) and not to F6 with `max(D)`: a looser ceiling prunes less (O4(i)
excludes the pair), while never being wrong (O4(ii) holds for `max(D)`).

**`[r2 E3]` The F7-not-F6 hazard is ARGUED, not witnessed.** The named witnesses are
greedy, where `max(D)` IS the priority end (0 / 27,884 differ). Only a LAZY tie
moves the window: `(\s+?){2}$` moves it on 2,188-3,282 cells with captures equal and
the give-up threshold equal over 19 budgets × 5 lengths. So the L3 sabotage row's
witness is re-aimed to `(\s+?){2}$` and detected by the window-identity twin
(`window[0][1]` compare), and the give-up hazard is recorded as UNWITNESSED: the
rule stands on O4(i)'s pair equality, not on an observed give-up.

**PRESENCE defers through `dominated`, not a new row `[r2 G9, C11]`.** On the hybrid
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

**Shape and finisher.** `LOWER = s*′` or `NOMATCH`, to F7 `search-vm` (the VM-only
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

### 4.6 `[ENG-TACTICS]` reverse-inner: a LOCATE row `[r2 E1, E8]`

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
  counted too few of them (K35). So:
  - **under G4** (`S` holds no backreference or group condition into `P`'s groups;
    conservatively no `${...}`): the row hands, per occurrence, a proven `SPAN` (DFA
    hat: F3 `verify-anchored` from `s*`; VM hat: F6 one anchored attempt) or moves on —
    revision 1's design;
  - **without G4**: the row hands `LOWER(s*(j₀))`, `j₀` the first occurrence with a
    non-empty `starts`, to F7 `search-vm` / F5 `search-from` — the attempt loop from
    there. `starts(j)` depends on `P` alone, so step 2's monotonicity still makes it a
    sound lower bound; the critic's `lowerbound` form measured 0 wrong.
  This is the VM-route population §3 of that note was built for
  (`\b(\w+)=[^&]*&(?:[^&]*&)*\1=`, `(\w+) \1`): it gets a lower bound, not a
  candidate per occurrence (§8 Q6).
- **Row:** `rev-inner-bounded` then `rev-inner` (views first), routes `CR_DFA` and
  `CR_VM`, after `rev-end` and before `composite`; predicate G1 ∧ G2 ∧ G3, with G4
  choosing the shape set; seed = each landmark hit `j`; reverse over the PREFIX
  machine (`revend.md` §8's helper; a landmark seed is speculative, X1).
- **Give-up hand-off:** where the forward-verify guard trips (`where_to_start.md`
  §2.7), F5 `search-from` relocates `s*` as `lo` to `composite` (the measured
  `fallback`); `start_table.md`'s FIRST-slot `handoff-rev` row is not needed. **`\G`
  `[r2 E8]`:** rev-inner, unlike REVEND, does not decline `\G`; relocate hands `lo` as a
  scan start and leaves `\G` on the caller's `search_from` (`(?:\G|b)(b?)\w*X` on
  `"-bbX"`: g1 (2,3) from 0; a relocate that moved `\G`'s reference would give (1,2)).
  If the composite cannot separate the two on some route, rev-inner declines `\G` there.
- **Classification** ONE_WAY on the VM (D151 Q4). Not built: D151 item 2's trigger is
  NOT MET (`where_to_start.md` §7).

**Where to attack §4.** (a) The PRESENCE → LOCATE read: does reading the BODY's
LOCATE from an entry slot keep `cand_hit_every`'s route-independence on an ATTEMPT
hybrid (two body routes in one artifact, D-2b)? (b) F7-not-F6 on clamped ties, now
unwitnessed: construct a give-up. (c) §4.5: a fifth Σ* source; a fold the emitted
compare applies that the relaxation does not. (d) G4's member list: anything else in
`S` that reads `P`'s capture state (a callout? `(*ACCEPT)` inside `S`?).

---

## 5. Build sequencing (D156 item (e))

No ids are taken here (counts only); the build lane numbers from the range its brief
names (BOILERPLATE: the kit's reserved ranges are not free).

### L0 — two slots, one derivation, the fold: no mover `[r2 G12, C3, C4, C5]`

- **What (G12's list, nothing else):**
  1. `CAND_SLOT_LOCATE`/`CAND_SLOT_FINISH` in `CandSlot` (`core/internal.h`) and in
     `cand_nodes[]` (VERIFIER loses `CT_WINDOW`; `CT_WINDOW` deleted; E-LF / E-FL with
     their progress classes).
  2. LOCATE rows `empty`, `composite`; `pcrec_emit_dfa_engine` dispatches on the row
     (`composite` by route = today's `emit_unanchored`/`emit_attempt`; `empty` = the
     empty body, moved out of the two emitters' arms `:9729`/`:10094` into the row's
     emitter, byte-identical or the commit does not land); `dfa_engine_is_empty`
     becomes the reader of LOCATE's selection (its old body is `empty`'s predicate;
     its eight callers do not change); `cand_locate_route`.
  3. `cand_finish_of(cx)` read by the ten FINISH reads (§3.3); `:10708`/`:10922` read
     `pcrec_artifact_has_dfa_scan`.
  4. The `dfa_matches[]` fold: FINISH rows F3 `verify-anchored` and F5 `search-from`
     taking `AT`; `dfa_match_of` → `cand_select(FINISH, cand_finish_of, hand = AT)`;
     `dfa_match_is_unwrapped` reads `u.finish.act` (F-2); the `match` listing is the
     rows' projection, byte-identical.
  5. `CandSel.hand` (mandatory on a FINISH ask) and `lroute`; `cand_select`'s FINISH
     filter.
  6. The data corrections: `.giveup` deleted (F-1; the classification is derived,
     §1.5), `.contract = CG_FIXED` on `handoff`; the boundary projection
     `cand_lang_exact` (F-3), recorded in the trace (`CANDTRACE FINISH <route>
     <shape>`), read by nothing that emits.
- **abi:** none. No emitted byte, no stamp, no listing byte moves.
- **Checks:** `scripts/emit_sweep.py` at 0 movers on every arm (the six streams,
  `-e utf8`, `-i`, the deny arms incl. `-fno-anchored-dfa`, `-fprefilter-collapse`); the
  C1 trace's SET compare (`trace_diff.py --unordered`) with a declared-trace file for
  the new LOCATE/FINISH records (`trace_declared_L0.txt`); `cand_rows_selfcheck`
  extended (totality over the §2.3 triple table, the shape filter, the progress check,
  `hand` mandatory); `tests/codegen/run_cand_rows.sh`; `run_cand_oracle.sh` with a
  witness per new row — `[^\x00-\xff]` (`empty`), `a` (`composite` DFA, and F3 via its
  `_match`), `^a` (`composite` ATTEMPT, and F5 via its `_match`), `(\w+)\1`
  (`composite` VM), `a` with `-fno-anchored-dfa` (F5 on `CR_DFA`) — and **the new
  declared-unreached allowance** (`cand_oracle_unreached.tsv`: row, argument, the
  commit that gives it a producer; a listed row that IS reached fails, so the file
  cannot rot) `[r2 C4]`, EMPTY at L0 because G12 deferred every producer-less row;
  `start_table/call_graph.py` + `inventory_check.py` re-derived.
- **Re-aims, DERIVED `[r2 C3]`.** `studies/locate_finish/l0_edit_set.tsv` (30
  entries: 11 `def`, 2 `token`, 17 `line`) through `start_table/sabotage_anchors.py`
  (ORDER gained `L0`, `L2`) on a call graph regenerated at `7efca415`
  (`results/l0_sabotage_anchors.tsv`, `.summary`): **RE-AIM at L0: 6** — S566
  (`emit_unanchored` `:9767`, the `fit.chosen` req-run line), S599 (the WIDTH `ceiling`
  row's `.giveup` line), S606, S607, S608, S609 (`cand_nodes`); **RE-RUN at L0: 18**
  sites (S07, S221, S223, S235, S283, S284, S295, S462, S473, S594, S595, S596, S598,
  S600, S610, S65, S67, S82), **98** more once after L0. S222 is a re-run after L0 (it
  sits in `dfa_search_start_name`, untouched), not a re-aim; revision 1's "0 re-aims"
  was wrong by six. The tool reports 3 unresolved `src/` sites (S176, S640 at
  `select_engine.c:553-554`, S571 at `memfn_sites.c:35`), none in L0's family; they are
  the tool's pre-existing resolution gap (the dec_fallback run had S571 too) and are
  recorded, not fixed here.
- **New sabotage ids: 6** `[r2 C5]`: (1) LOCATE order swap (`empty` after `composite`:
  the empty engine emits a scan; emit sweep); (2) `cand_finish_of` misderives a hybrid
  as a DFA finisher (the inlined body emits W/P/F twice; emit sweep + codegen);
  (3) the FINISH filter ignores `hand` (F5 selected for a `SPAN`; self-check, and the
  oracle's F3 witness stops reaching F3); (4) F3/F5 order swapped (every `_match`
  becomes `search-filter`; `DFA_MATCH` stamp check + emit sweep); (5) the boundary
  projection dropped (a superset hybrid's trace records `SPAN` on `CR_VM`; oracle
  witness `\w{1,2}(?:(?=)|)$` must record `LOWER`); (6) a relocate edge whose target is
  the handing row (self-check `progress`). F-2's revert (a row-pointer compare) changes
  no behaviour, so it is a grep row in `make test-codegen` (no `== &cand_rows[` and no
  pointer compare against a FINISH row in `src/gen`), not a plant. Revision 1's plant 5
  (declared vs derived posture) is withdrawn: it was circular, and the declared column
  no longer exists.
- **Spec:** none (no caller-observable change). `start_table.md` §1.2/§1.6 gain the two
  slots and the edges at the manager's merge.
- **Deny/force:** none new (F3 carries `-fno-anchored-dfa`, moved with its row).

### L1 — `revend.md` S0 and S1, unchanged

The `end_pin` fact split (W1's `end_window` becomes its reader) and the parameterized
reverse-block helper with the dead-seed skip and the which-seed report. No mover.
Checks, sabotage and spec as `revend.md` §9.1 items 1-2.

### L2 — `rev-end` (stage 1, DFA hats): the abi event, three separable commits `[r2 G10]`

- **L2.0 — the machine-membership derivation (no mover).** `dfa_table_name`,
  `dfa_uniform_folds` and `dfa_scan_edge_name` each spell today's membership rule
  ("forward always, reverse unless `pinned`, anchored iff `unwrapped`",
  `emit_dfa.c:4455-4580`), and the orientation block spells it a fourth time in prose.
  One function, `dfa_machines_of(cx)` (a bitmask F/R/A), read by all four. No byte
  moves; it is the ground L2.2's stamps stand on, and the fourth sibling makes it a
  forest-for-trees unification in its own right.
- **L2.1 — D-2's `attempt-start` (`start_table.md` §6 Q5, ruled: a LOW-priority row
  batched with the next abi event).** `RX_DFA_START` gains `"attempt-start"` on every
  artifact whose locator carries no reverse machine (census T8: 37 bench / 606 corpus
  rows, 481 distinct, hybrids included), and `rx_info.search_form` with it. Its own
  census delta (`emit_sweep` default vs parent = T8's set exactly), its own sabotage
  row (`DFA_START` forked from RECOVER's absence), its own spec hunk. **Separable**: a
  red in L2.2 bisects to L2.2.
- **L2.2 — `rev-end`.** LOCATE row A2 with the stage-1 conjunct; `nl_last`; FINISH rows
  F1, F2 and the `ENDSET` takes of F3/F5; F4 `verify-attempt` (declared UNREACHED with
  its argument: no `ENDSET` producer on `CR_ATTEMPT` until a reverse machine exists
  there); the walk emission (`revend.md` §5.1); `-fno-rev-end` (one new bit, the
  manager's allocation); the `locate` listing axis (`rev-end` 1, `composite` 2,
  `empty` listed or not by the manager's spelling call) with a DECLARED LISTING FILE
  `listing_declared_L2.tsv` read by `start_table/listing_diff.py` `[r2 C12]`; the
  stamps by §5.1.
- **abi:** 71 → 72, once, for the L2 merge. Readers BY GREP at build time (D76/D94):
  (a) the abi NUMBER (`revend.md` §5.3 (a)); (b) the byte-count readers (§5.3 (b));
  (c) the `DFA_SCAN` value readers — `revend.md` §5.3 (d)'s 33 files / 6 sabotage rows
  plus every MACHINE-PROXY reader (`[r2 G10, C8]`: a reader that takes `"unanchored"`
  to mean "the forward machine / its scan edge / its prefilter is present"; the census
  is L2's first deliverable, and §5.1 lists the in-tree ones found here);
  `pcrec_artifact_has_dfa_scan`'s 12 callers, which remain TRUE on a `rev-end`
  artifact (it has a DFA body; what it lacks is the forward machine); (d) the
  `DFA_START` value readers (19 files, 5 rows) for D-2; (e) **outside the repo
  `[r2 C7]`**: pcrec-bench `testees/pcrec/adapter.py` (`:699-705` and `:802-806` hold
  CLOSED `dfa_scan` / `dfa_start` vocabularies), `report.py` and `tools/selfcheck.py`;
  then the counting suites (registry, codegen, rxtsource) whether or not they cite the
  number (D94 addendum).
- **pcrec-bench deliverable `[r2 C7]`.** An `[inbox]` adapter note
  (`pcrec-bench/docs/dev/inbox_from_pcrec.md`, the manager's single-file commit, D78)
  naming the new `DFA_SCAN` value `"rev-end"`, the new `DFA_START` value
  `"attempt-start"`, the `REQ_WHY` token `"locator"`, the abi number, and the movers'
  population, ahead of the merge; and the window handshake before any bench cell reads
  an L2 artifact.
- **Movers:** census T4: 12 bench (the five tail patterns, `letters-bounded-tail-z`,
  the six class-B cells incl. `wild-semdiv-dollar-trailing-newline-pcre2` in two sets),
  corpus 171 rows / 121 distinct; plus L2.1's T8 population. The `emit_sweep` default
  vs `-fno-rev-end` census must equal the set whose text carries `revend_seed`
  (`revend.md` §5.4).
- **Checks:** `revend.md` §9.1 item 3's list, E13 replaced by E-LF. The answer net
  `tests/assertions/rev_end.rxt` (§9.3), the codegen structural check (`"rev-end"` ⇔
  `revend_seed` emitted; `nl_last` false ⇔ no tie text; a declining pattern
  byte-identical under `-fno-rev-end`), the test-axes floor arm (X13), the refusal-set
  check, C17 and the memfn stamps; `run_cand_oracle.sh` witnesses for A2, F1, F2 and the
  `ENDSET` takes of F3/F5 (`a$` T1, `ab$` with a final-newline subject T2, `ab$` with
  `-fno-anchored-dfa` T3), F4 in the unreached file.
- **New sabotage ids: 17**, `revend.md` §9.2's 16 recast (rows 1-10 unchanged; 11 (R2)
  "the route mask widened to `CR_ATTEMPT`"; 12 (R3) "the stage-1 conjunct dropped";
  13 (R4) "`empty` after `rev-end`"; 14 the deny unplumbed; 15 F5 made to take `ENDSET`
  ahead of F3; 16 the stamp forked from the selection (`DFA_SCAN`)), plus 1 for D-2 in
  L2.1. Re-aims: derived by re-running `sabotage_anchors.py` with L2's edit set at
  build time (S264 and S693 are known members).
- **Spec (D80) `[r2 C9]`:** `tuning.md` §2.x `-fno-rev-end`; `match_api.md`:
  `DFA_SCAN` gains `"rev-end"` in every value table (the stamp list `:4714-4740`, the
  `rx_info` table `:2145`, the field comments `:1904`/`:1940`, and the tables in
  `facts_listing.md:113-126` and `registry.md:421`, each confirmed by the build's grep),
  `DFA_START` gains `"attempt-start"` at `:788-796` and `:4829-4839` (revision 1's
  `:4686-4703` is now the VM stamp block), the REQ_WHY token, the downstream stamps'
  values on movers, `rx_info.search_form`, the abi sentence and TU-guard example;
  `registry.md`'s axis counts and the `locate` axis; `facts_listing.md` `end_pin`;
  `cli.md` where it lists axes.
- **Deny/force:** `-fno-rev-end` (deny only).

### `[GIVEUP-DIFF]` — the posture control, before the first VM-finisher LOCATE row `[r2 G7, C5]`

§1.5's differential as a `tests/` section (a budget ladder per witness, default vs each
VM-route deny), plus the corpus instrument that derives the classification column, plus
a spec sentence for every row it classifies ONE_WAY that has a deny flag (§8 Q4).
No `src/` change. It must exist before L3 or L4/L5 claims a posture, and it answers
F-1 behaviourally (W1, PRESENCE on `CR_VM`).

### L3 — stage 2 (VM hats): FILED

Drop the stage-1 conjunct; the `dominated` disjunct and its PRESENCE → LOCATE edge
gated on `pcrec_artifact_has_dfa_scan` (§4.3); F6/F7's `ENDSET`/`SPAN` takes; the
window-identity twin and the answer net's captures cells (`(\d+)$`, `(a+)$`, `a\Kb$`,
the unclamped tie `([^c]{1,3})$`, the clamped ties `(\s+){2}$`, `(\s$){1,3}` and the
LAZY `(\s+?){2}$`, the superset witness). abi 72 → 73 (or folded into L2 if Frank
rules so, §8 Q2). Movers: 0 bench / 13 corpus. **New sabotage ids: 5**: the deference
dropped (a pre-check emitted ahead of an inlined walk; codegen); a clamped tie sent to
F6 with `max(D)` (`[r2 E3]` witness `(\s+?){2}$`, the twin's `window[0][1]` compare); a
superset walk projected as `SPAN` (answer net on a constructed superset witness); the
inlined LOCATE asked on `CR_VM`; and **the X1 dead-seed skip dropped on a HYBRID
witness `[r2 E10]`** (a lookaround hybrid; E10's SEGV shapes). Spec: `match_api.md`'s
hybrid stamps. Trigger: `revend.md`'s.

### L4, L5 — FILED

L4 `rev-end-relaxed` (§4.5): its own erasure mode in `src/ir/nfa.c`, a LOCATE row on
`CR_VM`, its own deny (§8 Q5), ONE_WAY with D148 Q6's sentence; requires
`[GIVEUP-DIFF]`. L5 rev-inner (§4.6): D151's trigger; requires `[GIVEUP-DIFF]`.

### 5.1 The stamp rule (no new stamp) `[r2 C6, G10]`

**The rule (DD-13c's: a stamp names the selection that was emitted, from the one
derivation that emitted it).** The locator is named ONCE, on `RX_DFA_SCAN`, whose
three values today (`unanchored`, `attempt`, `empty`) are exactly the `composite`'s
two DFA hats and `empty` (census T1 classifies on it; C1 holds it against the text).
`rev-end` is its fourth VALUE, not a new `RX_LOCATE` stamp (which would put bytes on
every artifact and move every byte-count reader for no new information). Every OTHER
slot stamp on an artifact whose selected locator does not run that slot reads an
ABSENCE value — the slot is off the locator's path — and, where the stamp has no
absence value that is TRUE, gains one:

| stamp | reads on a `rev-end` artifact (form C, T1/T2; under T3 the composite is emitted and these keep their values) | why |
|---|---|---|
| `RX_DFA_SCAN` | `"rev-end"` | the locator |
| `RX_DFA_START` | `"reverse-pass"` | TRUE: the start is found by walking the reverse machine |
| `RX_END_WINDOW` | `"none"` | W1 is off the path; X10's one-spelling rule holds (`"rev-end"` is spelled once, on `DFA_SCAN`) |
| `RX_DFA_PREFILTER`, `_PREFILTER_OFFSETS` | `"none"` | NEXT is off the path |
| `RX_REQ_BYTE`, `RX_REQ_RUN` | unchanged | they are FACTS about the pattern, not selections |
| `RX_REQ_WHY` | **`"locator"`** (new token) where `REQ_BYTE ≠ "none"`; `"none"` otherwise | none of the four closed tokens is true: `"none"` must hold iff `REQ_BYTE` is `"none"` (the stamp's own checked invariant, `emit_dfa.c:11120`), and `"emitted"`/`"dominated"`/`"one-attempt"` each claim something about a PRESENCE row that never ran. `"locator"`: no pre-check, because the selected locator is not the composite |
| `RX_REQ_HANDOFF` | `"none"` | FIRST is off the path |
| `RX_DFA_TABLE`, `RX_DFA_UNIFORM_FOLDS`, `RX_DFA_SCAN_EDGE` | folded over the machines the artifact EMITS (`dfa_machines_of`, L2.0): reverse, plus anchored iff F3 is reachable | today each folds over "forward always", which form C does not emit; a stamp naming a machine the file lacks is the defect class `start_table.md` §0 lists |
| the orientation block (comment) | describes the walk: reverse from the end, then (ties) the anchored run or the composite | it reads `dfa_machines_of` too; non-essential comment text, inside L2's abi event |
| `RX_DFA_MATCH`, `rx_info.match_form` | unchanged | the match-here entry's own FINISH row |

`RX_DFA_START "attempt-start"` (L2.1) is the same rule on ATTEMPT / empty locators: a
slot not on the locator's path names its absence truthfully rather than claiming
`"reverse-pass"`. **This supersedes `revend.md` §5.2** (which had `RX_END_WINDOW` and
`RX_DFA_START` read `"rev-end"`); the supersession is recorded here and in
`revend.md` §5.2 itself (a forward pointer, `[r2 C6]` in that note). Spellings are the
manager's call (memory `pcrec-dd13b-syntax-is-managers`); the rule is Frank's (§8 Q3).

**Where to attack §5.** (a) L0's "no mover": the `empty` arm's move out of two
emitters (the two arms differ in where the head is emitted); `cand_finish_of` vs
`fit.chosen` on the `P-empty` hybrids (18 corpus). (b) The derived re-aims: an anchor
the edit set's text misses because L0 rewrites it by a token not listed. (c) §5.1:
a DFA_SCAN reader that treats `"unanchored"` as "a forward machine exists". (d)
L2.0's membership function: a fifth spelling of the membership rule.

---

## 6. Standing questions (`docs/design/CLAUDE.md`)

### 6.1 The measurement regime — RELEVANT, briefly

This note takes no timing. Every number is compile-side (the census: counts from
stamps, facts and emitted text, regime-free), a critic's answer-level count (E1-E12:
correctness, regime-free), or `revend.md`'s scratch-tier Linux timing (7700X, warm
repeated calls, cited for REVEND only). The one decision a regime could flip is stage
2's value, which is FILED on a population, not a timing. The `[GIVEUP-DIFF]` budgets
are step/work counts, not clock time, so they are box-independent.

### 6.2 The independent control — RELEVANT

- **The census.** Four controls (§3.1), each with a different source: the emitted
  text (C1, C2), a borrowed copy of `ew_walk` against the shipped fact in both
  directions with each decline DECLARED and counted (C3), and the RETRY row's stamp
  against the census classifier (C4). `analyze.py` exits 1 and prints no table on any
  disagreement. The population is counted by the borrowed `bench_pop`/`corpus_pop`
  (K35: who counts is named).
- **The design's checks.** The extended self-check is a CONSISTENCY check: it shares
  its source with the table. The controls are elsewhere: the emit sweep (bytes, not
  selections) for L0; libpcre2 10.46 on the answer net and `-fno-rev-end` for L2
  (`revend.md` §12.2); the window-identity twin for L3; and for POSTURE, the give-up
  differential (§1.5), which reads answers at budgets and shares nothing with the
  table (`[r2 G7]`), replacing revision 1's declared-vs-derived compare, which shared
  everything.
- **Witness reach ([MECH-REACH]).** Every L0 row has a constructed witness; L2's F4 is
  the first entry in the declared-unreached file, with its argument.

### 6.3 What moves when data is regenerated — RELEVANT

- L0 moves nothing (no abi event).
- L2: the abi number; `DFA_SCAN`/`DFA_START`/`REQ_WHY` values and the folded machine
  stamps on movers (§5.1); no calibration or data file is read (`end_pin`, `nl_last` per
  compile).
- L4's relaxed machine reads no data; rev-inner's G3 reads the byte-rate prior
  (`default_ppm.tsv`).
- The census outputs (`rows.tsv.gz`, `summary.txt`, `l0_sabotage_anchors.tsv`) move
  with the tree; no check reads them. The L0 edit set is data the build lane re-derives
  against its own pin.

---

## 7. Candidates with triggers (filed, not designed beyond the trigger) `[r2 G13, G14]`

### 7.1 The relaxed-backref machine run FORWARD (G13)

§4.5's `relax(P)` is a SOUND general erasure for `A_BREF`. Run forward, it is a
superset prefilter for every acyclic-backref VM-only artifact (`backrefs_design.md`
§7.4's chartered prefilter, needing no E2 gate since the relaxation is
assertion-erased; VM-only search measured 6.2-130× slower than a hybrid). **Trigger:**
a census of VM-only backref artifacts where `relax(P)` is acyclic and the N7 START-SET
hat does not narrow, PLUS one bench backref cell paying the attempt loop.

### 7.2 rev-end as rev-inner with landmark = end: a seed-SET reverse walk (G14(1))

`(?m)$` seeded at every `'\n'` + `n`. **Trigger:** a bench or real-world `(?m)...$`
cell whose attempt loop or forward scan dominates (the finding names the cell).

### 7.3 A fixed-width RECOVER row: start = end − W (G14(2))

For a fixed-width pattern the reverse pass is arithmetic. **Trigger:** a measured
reverse-pass share on a fixed-width bench cell (the finding names it).

### 7.4 A forward regular-prefix locator over `P·Σ*` (G14(3))

**Trigger:** the finding's: a population where the prefix's language is regular, the
suffix is not, and no landmark rescues the start.

### 7.5 A subset locator handing `UPPER` + EXISTS (G14(4), BOONIES-class)

A machine for a SUBSET of `L` proves a match exists and bounds the start from above
(the product's `t`). **BOONIES** (memory `pcrec-high-impact-focus`): no measurement
chartered; trigger as the finding states.

---

## 8. Questions for Frank (discussion)

Settled by the panel and struck: revision 1's Q1 (FINISH is a slot block, G4/G5).
Reshaped: Q5 (posture) by G7, now a narrower question about a spec sentence.

**Q1. L0 before REVEND, or folded into REVEND's abi event?** *Problem:* REVEND needs a
home; LOCATE is that home. *Forces:* G12 cut L0 to four items, and it now delivers
something on its own (the `dfa_matches[]` fold, one finisher derivation in place of
ten reads, F-1/F-2/F-3 corrected, a progress check the table lacked); D153 (remodel
first) and the start table's precedent favour a no-mover first. Against: one more
panel-reviewed step before a measurable win. *Leaning:* L0 first; folding it into L2
would turn L0's "no mover" proof into "movers = REVEND's set exactly", which is
harder to read and to bisect.

**Q2. Stage 2 with stage 1?** *Problem:* the stage-1 conjunct is the one place a
route-independent locator is kept off a route. *Forces:* the mechanism is small (one
`dominated` disjunct, one DAG edge, F6/F7 takes, the twin), NEUTRAL (E9's evidence is
the strongest of the round), and not building it is the special case; but the
population is 0 bench / 13 corpus, 11 already W1-clamped, and D77 says wait.
*Leaning:* FILED with `revend.md`'s trigger, the conjunct commented as stage 2's
switch. If you weigh the generality argument above D77 here, it folds into L2 for one
read and one twin.

**Q3. The stamp RULE.** *Problem:* a `rev-end` artifact does not run most slots; their
stamps must say something true. *Forces:* naming the locator once and having
off-path slots read an absence value keeps the bytes small and the readers few, but
it means one stamp (`REQ_WHY`) gains a token and three stamps change their fold
(§5.1); a new `RX_LOCATE` stamp is more explicit and moves every artifact. *Leaning:*
§5.1's rule, which also supersedes `revend.md` §5.2. The spellings are mine to
settle; whether "off the path ⇒ absence, the locator named once" is the rule for every
future locator is yours.

**Q4. The one-way spec sentence.** *Problem:* W1 and the VM-route PRESENCE checks skip
attempts the deny arm runs, so a budget-limited call can answer where the deny arm
gives up (ONE_WAY), and no spec sentence says so; the WIDTH ceiling's does exist in
spirit. *Forces:* `[GIVEUP-DIFF]` will confirm the classification behaviourally, and a
caller who sets a step budget can observe it; saying nothing leaves `tuning.md`'s
`-fno-end-window` / `-fno-req-byte` entries silently incomplete. *Leaning:* add the
one-way sentence to those entries when `[GIVEUP-DIFF]` lands, worded as D148 Q6's.

**Q5. The relaxed-reverse locator's deny.** *Problem:* it is `rev-end`'s walk over a
different machine. *Forces:* one deny keeps the family one switch; but its
classification (ONE_WAY), its erasure mode and its population differ, and `test-axes`
isolates only what has its own bit. *Leaning:* its own bit when built; noted now so
L2's bit is not later overloaded.

**Q6. rev-inner after E1.** *Problem:* E1 shows rev-inner's per-occurrence verify is
unsound exactly on its VM-route population (a backreference in `S` to a group of `P`),
so there it can only hand a LOWER bound to the attempt loop. *Forces:* D151 placed
the reverse walk partly FOR that population; a lower bound still skips the prefix
work up to the first viable occurrence, but no longer verifies one occurrence at a
time, so its win shrinks on dense subjects. *Leaning:* keep D151's trigger unchanged
(the `dup-param-detect` twin), and have the twin measure the LOWER form, which is the
only sound one there. Does the reduced VM value change how you rank it?

**Q7. The ATTEMPT match-here form the fold exposes.** *Problem:* folding
`dfa_matches[]` makes visible that an ENG_ATTEMPT artifact's `_match` runs a whole
search from `s` and discards later starts, where `verify-attempt` would answer with one
anchored run. *Forces:* a form mover on 20 bench / 308 corpus artifacts, answers
identical, already filed as `anchored_match_unwrapped.md` §10's open item; L0 must
stay a no-mover. *Leaning:* leave it to its filed row and give that row this note's
F4 as its mechanism (one `take` bit), measured before it is built (D77).

---

## 9. The lenses

- **specific vs general:** general. One product type, four actions, two hats cover
  every shipped mechanism; REVEND's E13, tie table, R2/R4 and stage 2 are instances,
  and `dfa_matches[]` stops being a parallel table.
- **core vs derived:** the tables, the boundary projection and the classification are
  derived; `end_pin`, `nl_last`, the relaxed machine and `cand_lang_exact`'s inputs
  are core facts or machine properties; the contract column is declared because it is
  a ruling.
- **applicable vs assumption-changing:** applicable; no contract changes at L0.
- **fits the architecture vs refactor:** L0 is a small refactor in refactor A's shape;
  L2 fits.
- **shared question / engine hat (D124):** FINISH is D124's other axis: "what does the
  engine still have to compute", with the hat by route.
- **sibling of a family (memory `pcrec-forest-for-trees`):** three families surfaced:
  FINISH (ten reads + `dfa_matches[]`), "does a DFA body exist" (three spellings, §3.3),
  and the machine-membership rule (four spellings, L2.0).

---

## 10. Findings for the record

- **F-1** (revised) W1 `window` and the VM-route PRESENCE checks are ONE_WAY by §1.5's
  rule, and their declared posture read NEUTRAL by the zero value; the declared column
  had no reader. Fixed at L0 by deleting the declaration (§1.5); confirmed behaviourally
  by `[GIVEUP-DIFF]`.
- **F-2** `dfa_match_is_unwrapped` (`emit_dfa.c:7727`) compares a row POINTER; dissolved
  by the fold (§3.4).
- **F-3** (revised) On the 22 bench / 621 corpus superset hybrids the inlined body's
  `SPAN` is not `L`'s; the fix is the boundary projection `cand_lang_exact`, not a
  RECOVER declaration (§1.2).
- **F-4** `revend.md` §3.9's stage-2 posture (ONE_WAY) is NEUTRAL given F7-not-F6 on
  clamped ties (§4.3; E9).
- **F-5** rev-inner is a LOCATE row, not NEXT (§4.6).
- **F-6** WITHDRAWN `[r2 G1]`: D156's type list did not omit anything; `CAND` is
  `LOWER`.
- **F-7** (new, `[r2 C3]`) Revision 1's "L0 re-aims 0 sabotage rows" was wrong: the
  derived count is 6 (S566, S599, S606-S609).
- **F-8** (new, `[r2 E1]`) `where_to_start.md` §2.2 step 1 was unsound when `S`
  references `P`'s groups; corrected in place.
- **F-9** (new) "Does a DFA body exist" is spelled three ways (`pcrec_artifact_has_dfa_scan`,
  `(!vm || prefilter)` at `emit_dfa.c:10707-10708`, `dfa_body` at `:10922`); L0 points
  the two local spellings at the predicate.
- **F-10** (new) The machine-membership rule is spelled four times (`dfa_table_name`,
  `dfa_uniform_folds`, `dfa_scan_edge_name`, the orientation block); L2.0 unifies it.
- **F-11** (new) An ENG_ATTEMPT artifact's `_match` is `search-filter` (a whole search
  from `s`); the fold makes the alternative a one-bit row change (§2.3, §8 Q7).
