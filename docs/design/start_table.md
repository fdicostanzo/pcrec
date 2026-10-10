# One start-strategy table — the row contract, the inventory, the no-mover refactor

**DESIGN NOTE, PROPOSED, REVISION 2.1, nothing built.** Revision 2.1: lane
`starttabrev3`, 2026-10-06, the short D6 re-check's fixes (both critics:
"CLEARS with listed fixes"; record `../dev/reviews/2026-10-06-r2-starttable-recheck.md`),
marked `[r2.1 <id>]` inline and dispositioned in §R's second table; Q1 is
RULED (D151 addendum 1). Revision 1: lane
`starttable`, 2026-10-06, from main `74379fe0`, abi 64. Revision 2: lane
`starttabrev`, 2026-10-06, from main `4743ebb5` (no `src/` change since
`74379fe0`; the same `build/pcrec`, abi 64). It applies the light D6 panel
(`../dev/reviews/2026-10-06-r-starttable-panel.md`; critics
`…-crit-sound.md` and `…-crit-checks.md`), every finding ACCEPTED. **Read §R
first.** Changes are marked `[r2 <finding-id>]` inline. Nothing under `src/`,
`cli/`, `lib/` or `tests/` changes. The instruments and their committed output
are in `start_table/` (own CLAUDE.md). Rulings are Frank's; §6 lists the open
questions, each with a recommendation.

Frank (2026-10-06): "So are we going to reorganize around a single start strategy
decision table?" — then "Agree with direction" to the manager's three-step plan:
(1) this note and a light panel; (2) a NO-MOVER refactor that puts every existing
start mechanism into ONE first-match table under one row contract, gated by
`scripts/emit_sweep.py` at 0 movers; (3) new rows afterwards, each its own abi
event. And, during the panel: **"can the start table be re-entered, e.g. VM
then prefilter?"** — answered in §1.6 [r2 frank-reentry].

Read before writing: `where_to_start.md` (the study, D151), D148 + addenda 1-4 and
`startset.md`, D124, D152, `decision_families_survey.md` (families 2-4, §4.2),
`offset_k_skip.md`, `litscan_k82h.md` §2.1 (why `req_uses[]` was born separate),
`docs/dev/optloop/revend_census.md` ([OPT-REVEND]), K88/K90, [ARTREV]
`generalize.md` I5, `src/facts/facts.def`, `docs/spec/facts_listing.md`,
`docs/design/memfn/integration.md` §8.5 + `tests/memfn/site_manifest.tsv`, and the
table sites in `src/gen/emit_dfa.c` / `src/gen/emit_vm.c` at this pin.

---

## R. Panel disposition (revision 2)

Every finding of both critics, with where the revision answers it. "Fixed" means
the note now says the corrected thing; "answered" means the finding's premise is
corrected with evidence.

| finding | resolution | where |
|---|---|---|
| sound M1 (ATTEMPT-engine hybrids misfiled; BOUND on two routes in one artifact; census double count) | fixed: a DFA-shaped body's route is `job->engine` of the PREFILTER, never `fit.chosen`; seven route CLASSES, disjoint; per-(slot, route) within one artifact made explicit; the census keys every joint stamp on the route class, so no artifact counts twice | §1.1 `routes`, §2.2, §2.3, `row_census.py` |
| sound M2 (K65 set-rest, K66 whole-run missing) | fixed: PRESENCE gains a ROUTE-KEYED payload (`u.admit.noscan`), not rows; posture FIXED; S277/S278/S316/S459 named; on the C1 trace | §1.1, §2.2 PRESENCE, §3.3 |
| sound M3 (`prefix_k.c`'s admission) | fixed: named as N3/N4's admission and as the "pick inside a row" level the table does not own; S187/S188 counted in the derived family | §2.2 NEXT, §2.5 |
| sound M4 / survey §4.2 (D-4) | fixed: D-4 added, preserved by the refactor, fix named as a separate ruled change ([TIE-ALIGN] re-scope) | §2.4 D-4, §6 Q10 |
| sound M5 (four predicates restate BOUND) | fixed: P2, R3, N7 and `attempt_cand` become READERS of BOUND in a new no-mover commit C5b; the slot graph lists PRESENCE→BOUND, RETRY→BOUND, NEXT→BOUND (both routes); typed handoffs between slots, every re-entry a checked edge | §1.3, §1.6, §3.2 C5b |
| frank-reentry ("VM then prefilter?") | answered YES with the edge list: the retry re-enters the prefilter after a failed VM attempt; find-all re-enters the entry; the future reverse walk's give-up hands `s*` to NEXT | §1.6 |
| sound M6 / checks M1 (re-aim undercount; hand family list; SAB_FILE2) | fixed: the family is DERIVED by call graph (`call_graph.py`), the re-aim list by an edit-set file (`refactor_edit_set.tsv`); every site incl. SAB_FILE2 and non-emitter files; **14 re-aims, 81 re-runs, 95 family rows** (was 6/47/53; revision 2.1: 15 / 85 / 100, §R.1). The per-commit exact-count gate already exists: `scripts/m6read_check_sab_anchors.py`, wired as `make test-codegen` [SABANCHOR] | §3.5 |
| checks M2 (C0 cannot fail on its plumbing) | fixed: per-arm DIFFER floors (an arm must differ from default on its own side), seeded from the deny-delta census; `-fno-end-window` at utf8 an asserted EXACT 0; stream 4 under utf8 partial by design | §3.3 item 2 |
| checks M3 (trace under-specified; C2 oracle tests only the filter) | fixed: record = (pattern-index, seq, slot, route, row, site); printed at the walk's RETURN; reference regenerated from the PARENT every commit; the trace build is never the byte-sweep build and is itself byte-swept at C1; the C2 oracle is stated as a FILTER test, run in both orders, with the deny-delta census as the independent control | §3.3 items 5-6 |
| checks M4 (gap list stale; R6 asserted; H1 reads a constant; P4/P5 share a stamp; B1/B2 no anchor) | fixed: per-row control = the deny-delta count (shares nothing with `cand_rows[]`); `row_census` gains the deny arms; H1 read two ways; witnesses and planned sabotage rows for B1/B2/H1/P4/P5 | §3.4 |
| sound m1 (stamps/listing keep reading the fact) | fixed: C5 moves `END_WINDOW`, `VM_START`, `VM_ROOT_MINW` and `--emit-ir`'s `root-minw` onto the row | §3.2 C5, §3.6 |
| sound m2 (`dfa_search_is_pinned` compares row pointers) | fixed: `u.recover.pinned`, read by all 7 readers | §1.1, §3.2 C3 |
| sound m3 (`match` axis; N12's axis; B5's listed name) | fixed: `match` removed from C6; N12's listing projection is empty; the listing projection is PER ROUTE (`list[route] = {axis, order, name}`), distinct from `c.name` | §1.1, §3.2 C6 |
| sound m4 (`-fprefilter-collapse` arm) | fixed: a sweep arm and a deny-census arm | §3.3 item 4 |
| sound m5 (trace mapping self-authored for inline sites; set vs sequence) | answered: for inline sites the trace proves only that the print matches the emitted text; bytes are the control there; diffs compare ordered sequences, multiplicity changes declared per commit | §3.3 item 5 |
| sound m6 (utf8 gap narrower) | fixed: the utf8-native corpus is swept by stream 4; what is missing is the byte corpus × utf8 | §0a item 5, §3.3 item 2 |
| sound n1 (ask ORDER unobservable; predicates longjmp) | fixed: the invariant is SET equality plus "no new predicate evaluation reaches an assertion" | §1.3, §2.3 |
| sound n2 (slot order ≠ ask order) | fixed: slot order is table order; the per-route ask order is stated as the code has it | §1.2 |
| sound n3 (missed asks) | fixed: VM-only asks FIRST (declines); every artifact asks NEXT on route VM for `VM_START_SCAN` | §2.3 |
| sound n4 (route set coarser than predicates) | answered: stated as a third axis read inside predicates; filed, not folded | §2.3 |
| sound n5 (S490 equivalence premise moves at C3) | fixed: re-verify the argument at C3 | §3.5 |
| sound n6 (D-1 on ATTEMPT hybrids) | fixed | §2.4 D-1 |
| checks m1 (widened name check false-positives) | fixed: the literal half keys on (row name AND a `c.name`/projection receiver) | §3.5 |
| checks m2 (regexes in `cand_rows_check.py`) | fixed: both re-aims named (`:130`, `[cand-route-walk]` `:177`) | §3.5 |
| checks m3 (new checks without sabotage rows) | fixed: one planned row per new check | §3.5 |
| checks m4 (emit_sweep floors stale) | fixed: C0 re-pins every floor to the measured reach | §3.2 C0 |
| checks m5 (argv streams drop per-pattern flags) | fixed: a `-i` arm; per-row options stay stream 4's, stated | §3.3 item 2 |
| checks m6 (`--emit-facts` sees six facts) | fixed: the six facts and their rows named; `--emit-facts=byte,utf8` needs no `--extra` | §3.3 item 3 |
| checks m7 (no witness injection) | fixed: C0 adds `--patterns-file`; every named witness is a committed `.rxt` cell first | §3.2 C0, §3.4 |
| checks m8 (`registry.md:267` names `dfa_select`) | fixed: its spec hunk rides C3 | §3.2 C3 |
| checks notes (exact-count manifests; asserted zero) | adopted | §3.3, §3.4 |

### R.1 Re-check disposition (revision 2.1)

The short re-check (§6 Q9) returned "CLEARS with listed fixes" from both
critics. Every fix is ACCEPTED (one with a measured nuance, C-M2); the
finding-by-finding record is `../dev/reviews/2026-10-06-r2-starttable-recheck.md`.

| finding | resolution | where |
|---|---|---|
| C-N1 (61 anchor sites with owner `?`, start-family rows silently OTHER) | fixed: `call_graph.py` parses types, sized/initializer/string data, object-like macros and headers (1,892 definitions); `sabotage_anchors.py` resolves a site by `def` / `factrow` / `datarow` / `lead` (header comment) / `filescope` / `outside`, and an UNRESOLVED `src/` site is a hard error (exit 2; 0 today; control: deleting `DfaCand`'s def makes S282 unresolved and the script exits 2). The five rows the critic named (S282, S299, S475, S479, S496) are family, and nothing else moved: **100 family rows, 15 re-aim, 85 re-run** (was 95/14/81) | §2.1, §3.5 |
| C-N2 (the trace has no instrument) | fixed: C0's deliverable list names the trace stream, its diff tool, `-DPCREC_CAND_TRACE` through `build_from_rev` (`scripts/emit_sweep.py:344` runs plain `make`), stderr capture, the pattern-index/arm attachment, C5b's multiplicity filter, a per-arm records floor, and a failing-direction control with its sabotage row | §3.2 C0, §3.3 item 5 |
| C-M2 (utf8 and `-i` DIFFER floors "measured at C0") | fixed, MEASURED now: plain `-e utf8` differs on 3,188 / 3,189 of 3,221 / 3,222 (auto / vm, plus 74 refusal moves), and moves a START stamp on 674 / 341; `-i` differs on every artifact and moves a start stamp on 1,752 / 1,567 (byte) and 1,775 / 1,605 (utf8). Stated: with `-e utf8` dropped on both sides, 8 of the 13 utf8 deny floors still pass; the asserted 0, the plain utf8 floor, and (by the accident of which encoding is larger) four deny floors catch it | §3.3 item 2 |
| C-N3 (deny census over 13 hand-picked flags) | measured on a 1-in-10 sample over all 29 other `--list-axes` flags × 4 arms (43,200 compiles, 321 s at 6 jobs; the full sweep ≈ 54 min at 6 jobs). Route-input flags move the start rows through the route; four flags move start stamps WITHOUT a route change, `-fno-length-prune` (bit 7) the clearest: it reaches R1 through `Vm.mrl_win`, a seed field, so it joins the deny arms. The full sweep is C0's deliverable | §3.3 item 4, §3.4 |
| C-N4 (reader list `src/`-only) | fixed: `reader_grep.sh` finds every reader outside `src/` by grep (`reader_grep.txt`, 61 lines); the spec readers ride C3's hunk, the test/CLAUDE.md readers ride their commits | §3.2 C3, §3.5 |
| C-N5 (re-run rows swept once after C5b) | fixed: `sabotage_anchors.py`'s `rerun_at` column names every commit whose edit set touches the row's OWNER; 32 re-run rows (34 sites) re-run in their commit (sites: C3 12, C5 20, C5b 4; two rows at both C3 and C5), the other 53 once after C5b | §3.5 |
| C-N7 ("all five streams") | fixed: six | §3.3 item 1 |
| checks: nothing mechanical reconciles methods 2/3 against the family | fixed: `reconcile.py` + `reconcile_map.tsv` fail on an unmapped moved stamp key, an unmapped or ambiguous hidden fingerprint, a mapped member not in `inventory.tsv`, or an OTHER sabotage row whose anchor names a family identifier (control: two map lines removed → exit 1) | §2.1 |
| S-N1 (a) declaring `LOWER` does not prove termination | fixed: a per-row PROGRESS obligation, checked at review; E11 resumes past the previous hit | §1.6 |
| S-N1 (b) E10 on an empty match | fixed: the strict advance is the caller's empty-match rule | §1.6 |
| S-N1 (c) E5's in-scan cycle missing | fixed: added, with its termination argument | §1.6 |
| S-N1 (d) CAND's obligation | fixed: `x ≥` the accepted `LOWER` | §1.6 |
| S-N1 (e)/(f) the type check unevaluable | fixed: `HIT` and `START` types; non-slot successors named (verifier, loop header, caller); PRESENCE's gate hit is `HIT` (E3); E11 re-typed | §1.2, §1.6 |
| S-N2 (§2.3's "the one dispatch") | fixed: 15 `job->engine` tests enumerated; ONE `cand_route_of(cx)` in the edit set (C2), read by all of them from C3; S490's anchor is one of them (a C3 re-aim, which also discharges sound-n5's re-verification) | §2.3, §3.2, §3.5 |
| S-N3 (edit set misses R3's C5b line and m1's stamp/listing lines; 463 vs 462) | fixed: added; S441 is moved by C5 AND C5b and the classifier lists both; S169 is CONFIRMED shared by two row files (filed as a finding in the record) | §3.5 |
| S-N4 ("three methods share no source") | fixed: two independent derivations plus a cross-record | §2.1, §5.2 |
| S-N5 (§1.3(b) has no population) | fixed: `assert_reach.py` → `assert_reach.tsv` | §1.3 |
| both: §6 Q1 | RULED (D151 addendum 1) | §6 |
| sibling lens: the position domain | filed as [DEC-POSDOM] (`docs/dev/plan.md`) | §2.5, §5.4 |
| Frank 2026-10-06, R-Q3 ([DEC-FALLBACK] tokens) | RULED: today's tokens kept, a pure no-mover; name/why separation is a later abi row | §6 R-Q3, D151 add. 2 |
| Frank 2026-10-06, R-Q4 (streamlining) | RULED: two serial no-mover refactors, A (this fold) then B ([DEC-FALLBACK]); B absorbs Q8; movers (Q4, Q5, Q6, Q10/D-4, [DEC-POSDOM], token separation) are later separate rows | §6 Q8, R-Q4; §5.4; D151 add. 2 |
| Frank 2026-10-06, R-Q5 (memfn sequencing) | RULED: kit R4c (main `05c33ce0`) before C1-C7, C0 in parallel; C1-C7 re-derive their edit set on post-R4c main; B1-B18 are input; ping the kit at C0's merge (it awaits the full I2) | §3.2, §6 R-Q5; D151 add. 2 |
| Frank 2026-10-06, Q2 (array shape) | RULED: ONE `cand_rows[]`, a `slot` field per row, the walk takes a slot; not per-slot arrays | §6 Q2; D151 add. 3 |
| Frank 2026-10-06, Q3 (selection trace) | RULED: YES, CONDITIONAL on a C0 experiment (plants detected, neutral commits clean); else dropped, bytes + deny-delta counts | §6 Q3; §3.3 item 5; D151 add. 3 |
| Frank 2026-10-06, Q4 (D-1) | RULED: G1 declines EXACTPRED as its own later row after C7, gated on measuring the 33 artifacts first (D77); not in the fold | §2.4 D-1, §6 Q4; D151 add. 3 |
| Frank 2026-10-06, Q5 (D-2) | RULED: `attempt-start`, a later low-priority row batched with the next abi event, with the D80 spec hunk | §2.4 D-2, §6 Q5; D151 add. 3 |
| Frank 2026-10-06, Q6 (D-2b) | RULED: file, don't fix; D77 trigger = a pattern that pays for the full-position search | §2.4 D-2b, §6 Q6; D151 add. 3 |
| Frank 2026-10-06, Q7 (census scripts) | RULED: as recommended, with run-time, sabotage-row and parse-robustness conditions | §6 Q7; D151 add. 3 |
| Frank 2026-10-06, Q10 (D-4) | RULED: YES, [TIE-ALIGN] re-scoped; a form mover after C7, one `PF_DERIVED` fact ([PATFACTS]) | §2.4 D-4, §6 Q10; D151 add. 3 |

---


## 0. Why the start decision is a table (manager's statement, recorded at Frank's request, 2026-10-06; general rationale D152)

"Where can a match start, and where can the search skip to?" is answered today by about ten sites — 5 arrays and 5 inline decisions over 3 routes — that READ EACH OTHER: req-use reads req-admit; REQ_WHY "dominated" reads the DFA scan byte; the K82 handoff turns a pre-check hit into a scan start; the bound predicate is restated at four places. [r2: the derived count is in §2.1 — 5 arrays, 7 inline decision sites and 2 route-keyed payload decisions over 7 route classes; the statement below stands.]

**Advantages specific to this family:**
1. **It fixes measured defects:** `run-pinned` is unreachable whenever two byte-pickers disagree (systematic under utf8); G1 reads a predecessor-byte skip as a start byte (33 artifacts); a stamp says "reverse-pass" on 452 artifacts with no reverse machine; a fix to the bound predicate must today find four copies. One predicate per question removes the duplication, and each disagreement becomes a visible row to rule on.
2. **The queued work becomes one row each:** D151's reverse walk, [ARTREV] I5's VM word-start filter (a column on an existing row), K90's dense-start fix (the existing re-seed disarm extended to the VM route: a route bit on existing rows). Dispersed, each adds sites and cross-reads — START-SET stages 2 and 3 each needed a panel that found check gaps.
3. **It is measurable per mechanism:** a trace and per-row hit counter give each row's population, dead rows, and per-row timing; A01's -72% ("scan `(` not `a`") was a question of which landmark row wins, which a table makes an explicit ordering/admission choice.
4. **Give-up posture becomes a field:** the K82 Q10 vs D148 Q6 difference is a column every new row must fill.

**What it does not do:** it makes nothing faster by itself (the fold is no-mover). The payoff comes from the queued rows and the inconsistency fixes it enables; without planned new start mechanisms the inconsistencies would still be fixed, but the fold would rank lower.

## 0a. Answers first

[r2: this section was a second "§0"; renumbered.]

1. **Yes, and the table is literally one array.** Today the start decision is
   made at five first-match arrays (`dfa_pfs[]`, `req_admits[]`, `req_uses[]`,
   `dfa_search_starts[]`, `pcrec_reseed_rows[]`) and at seven inline decision
   sites with no table at all: ENG_ATTEMPT's predecessor-byte skip
   (`attempt_cand`), ENG_ATTEMPT's `start_max`, the VM's `attempt_max`, the
   end-window clamp, the root minimum-width check, and the two route dispatches
   that decide which body asks at all (`pcrec_emit_dfa_engine` on `job->engine`;
   the `fit.chosen == ENGM_DFA` gate on the entry's W/P/F asks) [r2 sound-M1].
   Two more decisions are route-keyed PAYLOAD of an existing row rather than
   choices (K65 set-rest, K66 whole-run) [r2 sound-M2], and one admission lives
   inside a landmark derivation (`prefix_k.c`) [r2 sound-M3]. **The list is
   derived, not hand-written** (§2.1): a call graph from the emitters to every
   landmark read, a deny-delta census over the corpus, and the sabotage anchors,
   with a completeness check that fails on any undispositioned member. The
   design folds the arrays and inline decisions into ONE array, `cand_rows[]`
   (D148 Q2's name), of ONE row type, `CandRow`, selected by ONE walk.
2. **"One first-match table" needs a SLOT column, and that is not a planner.** An
   artifact today runs several start mechanisms at once: an end-window clamp,
   then a presence pre-check, then a handoff, then an in-loop skip, then a
   reverse pass. A single first-match winner per artifact cannot express that
   without product rows (`set-leads-handoff`, …), which is the parallel-row smell
   `litscan_k82h.md` §2.1 rejected. So each row carries the QUESTION it answers
   (its slot: window, presence, width, first-scan, next-candidate, retry, bound,
   recover), and the walk is first-match per (slot, route). This is the
   mechanism the table already uses for engines: `dfa_pfs[]` carries a `routes`
   mask since START-SET, and the VM route and the DFA route each get their own
   first-match over the one list (`cand_routed`, `emit_dfa.c:5139`). The slot is
   the same filter along a second axis. Composition across slots is fixed by the
   search-body skeleton (§1.3), never selected. **What one slot hands the next
   is TYPED** (§1.6): a lower bound, an upper bound, a candidate, a window or a
   verdict; each slot declares what it accepts, and every re-entry path (the
   retry back into the prefilter, find-all, the future reverse walk's give-up)
   is a checked edge [r2 sound-M5, frank-reentry].
3. **The inventory is 37 rows in 8 slots over 3 routes**, asked in 7 route
   CLASSES (the route of a DFA-shaped body is its prefilter's engine, so a VM
   hybrid can be an ATTEMPT customer and ask BOUND twice, once per route)
   [r2 sound-M1]. The census finds five places where today's dispersed sites
   disagree (§2.4: D-1, D-2, D-2b, D-3, D-4). None is an answer disagreement. A
   no-mover refactor preserves all five, and each fix is named as a separate
   ruled change [r2 sound-M4].
4. **The refactor is nine commits, implement-then-replace** (§3.2). Predicate
   and emitter FUNCTIONS stay byte-stable except a declared EDIT SET
   (`start_table/refactor_edit_set.tsv`): the tables and walks, the inline
   predicate lines, and in C5b the four BOUND restatements [r2 sound-M5]
   (R3's line was missing from the file; added [r2.1 S-N3]). The sabotage consequences are DERIVED from that file and the
   call graph: **15 of the 100 start-family sabotage rows are re-aimed, 85
   re-run** [r2 sound-M6, checks-M1; r2.1 C-N1, S-N2]. No abi event: every emitted byte and every stamp value is
   unchanged, and the listing (`--list-axes`, stream 5) is byte-identical until
   one declared listing commit.
5. **`emit_sweep` alone cannot prove the no-mover claim, for three measured
   reasons** (§3.3-§3.4):
   - its argv streams (1-3) never pass `-e utf8` (`compile_stream_c`,
     `scripts/emit_sweep.py:429`). Stream 4 does sweep the utf8-NATIVE corpus
     (the `.rxt` blocks that declare `encoding utf8`); what is missing is the
     byte corpus compiled under utf8 [r2 sound-m6];
   - `--emit-facts`' `used` column records which of six facts a predicate
     ASKED, which no emitted byte shows [r2 checks-m6];
   - a row the corpus never selects is not proven by any byte sweep.

   The plan adds the first two as sweep arms (commit C0), each with a floor that
   makes the arm FAIL if its own plumbing drops the flag [r2 checks-M2], and
   gives every zero-population row a constructed witness.
6. **The new rows each land in one slot** (§4): the D151 reverse-walk row in
   NEXT (the DFA and VM hats) plus `handoff-rev` in FIRST; I5 as a context
   column on the VM hat row; K90's dense-start fix as the RETRY slot's adaptive
   rows gaining the VM-only route. That last is the generalization: K90's
   proposed "density-adaptive disarm" IS [OPT-HYB-RESEED]'s rule, which today
   serves only the hybrid.

---

## 1. The row contract

### 1.1 The fields

One row is one way of answering one start question on one or more routes. Fields
(designated initializers, K84's house rule: an omitted field is its zero value,
so a reader never falls back to the NAME):

| field | what it holds | today's equivalent |
|---|---|---|
| `c.name` | the row's IDENTITY: unique across `cand_rows[]`, what the walk, the trace and the checks key on [r2 sound-m3] | `DfaCand.name` |
| `c.deny` | the `lib/pcrec.h` bit(s) that REMOVE the row (`uint64_t`, so bits ≥ 32 deny) | `DfaCand.deny` |
| `c.applies` | the admission predicate over [PATFACTS] facts and the compile, `bool (*)(const CandSel *)`. A predicate may `pcrec_ctx_fail` (longjmp): `pf_dfa_start_set` and `pf_vm_start_applies` do [r2 sound-n1] | `DfaCand.applies` |
| `slot` | the question answered (§1.2) | implicit: which array the row is in |
| `routes` | `CAND_ON(route)` mask over `CR_DFA` (the ENG_UNANCH scan body), `CR_ATTEMPT` (the ENG_ATTEMPT start loop), `CR_VM` (the VM attempt loop); 0 means `CR_DFA` alone, today's default. **The route of a DFA-shaped body is `job->engine` of the machine that body runs, never `fit.chosen`**: the VM hybrid's inlined prefilter is `CR_DFA` when its machine is ENG_UNANCH and `CR_ATTEMPT` when it is ENG_ATTEMPT (every pattern with a BOT, `compile.c:1874`→`:1913`) [r2 sound-M1] | `DfaPf.routes` (two values today) |
| `landmark` | the fact(s) the row reads, as `facts.def` names (`start_set`, `kset_walk`, `run_pin`, `req_run`, `req_run_maxoff`, `req_set`, `req_byte`, `req_whole_run`, `end_window`, `start_anchor`) or a machine property (`s0 escapes`, `seed liveness`, `interior deadness`, `root_minw`, `mrl_win`, `nclamp`) | prose in each predicate's header |
| `scan` | the scanner KIND, and for a scan the memfn site id it is delegated through: `PF`, `PRE`, `OFS`, `SETREST`, `MLINE`, `VMSTART`, or `none` (`tests/memfn/site_manifest.tsv`'s ids; D146) | `DfaPf.scan` (`PF_SCAN_*`), the manifest |
| `map` | the hit→candidate mapping (§1.4) | prose |
| `hands` | the TYPE of what the row hands the next slot: `LOWER`, `UPPER`, `CAND`, `WINDOW`, `VERDICT` (§1.6) [r2 frank-reentry] | implicit in the emitted text |
| `hat` | the consumer: the DFA (re-seeded or not), the attempt loop, the VM attempt, the reverse machine | `reseeds`, `emit*` hooks |
| `giveup` | the row's give-up posture (§1.5) | prose in two design notes |
| `stamp` | the stamp macro the row is reported through and the token it projects (a PROJECTION; N12 projects `"memchr"`, P4 projects `"emitted"`) | the `*_name` functions |
| `list[route]` | the `--list-axes` projection PER ROUTE: `{axis, order, listed name}`, empty where the row has no listing on that route. B5 is listed `unanchored` (order 3) under `vm-anchor-bound` on `CR_VM` and has no listing on `CR_ATTEMPT`; N12 has none [r2 sound-m3] | `axes_dump.c`'s per-axis emitters |
| `desc` | the listing's one-line `applies` text, BESIDE the row | `req_admits[].desc`, `pcrec_reseed_rows[].applies_desc`, and for `dfa_pfs[]` a SEPARATE hand table in `axes_dump.c:85-` (§2.4 D-3: it has drifted) |
| `u` | the slot's payload, a typed union: `u.pf` (today's `DfaPf` emit hooks, `reseeds`, `run_term`, `scan_set`, `emit_vm`), `u.admit` (`ReqAdmit` verdict, plus `noscan`: the route-keyed K65/K66 composition, §2.2), `u.use` (`ReqUse`), `u.reseed` (action, start column, armed), `u.bound` (`one`: none / 0 / `search_from`, and the emitted bound string), `u.recover` (`pinned`: the property `dfa_search_is_pinned`'s 7 readers test [r2 sound-m2]) | the five arrays' own row structs |

A union rather than a `const void *`: each slot's emitter reads its own member
with a compile-time type, and a row initialised with another slot's member is a
`run_cand_rows.sh` failure (§3.5), not a cast.

### 1.2 The slots

The slot order below is the TABLE's order (one block of rows per question). It
is not the order a body asks: each body asks in its own skeleton order, written
per route in §2.3, and that order is the code's, kept as it is [r2 sound-n2].
Within a slot the rows are in information order (`where_to_start.md` §1.4:
EXACT before WINDOW before LOWER-BOUND before PRESENCE; rarity is an admission
conjunct, never an order).

| slot | the question | asked at | today | accepts / hands (§1.6) |
|---|---|---|---|---|
| `WINDOW` | can a match begin before some position computed from the END? | the caller-facing entry, once | `pcrec_emit_end_window_clamp` (inline) | accepts `LOWER` (the caller's startpos); hands `LOWER` |
| `PRESENCE` | does the window hold every necessary landmark at all? | the entry, once | `req_admits[]` | accepts `LOWER`; hands `VERDICT` (+ the gate's `HIT` to FIRST [r2.1 S-N1]) |
| `WIDTH` | can the remaining subject hold a match at all? | the VM entry, once | `root_minw` test (inline) | accepts `LOWER`; hands `VERDICT` |
| `FIRST` | where does the first scan begin? | the entry, once | `req_uses[]` | accepts `HIT`; hands `LOWER` |
| `NEXT` | how is the next candidate start found? | the loop: at `s0` (DFA), between attempts (ATTEMPT, VM entry and retry) | `dfa_pfs[]`, `attempt_cand` (inline) | accepts `LOWER`; hands `CAND` (+ `WINDOW` from a hybrid's prefilter) to the VERIFIER |
| `RETRY` | after a failed VM attempt behind a prefilter, step or re-seed? | the hybrid's loop tail | `pcrec_reseed_rows[]` | accepts the failed `CAND`; hands `LOWER` back to NEXT (re-entry) or the next `CAND` (step) |
| `BOUND` | how many start positions can match at all? | the loop header | `start_max` (inline, ATTEMPT), `attempt_max` (inline, VM) | hands `UPPER` to the LOOP HEADER |
| `RECOVER` | given a match END, where does it start? | after the forward scan | `dfa_search_starts[]` | accepts the END and the entry's `LOWER`; hands `START` to the CALLER |

Three successors are not slots [r2.1 S-N1(e)]: the VERIFIER (the forward
machine, the ATTEMPT loop's attempt, or the VM attempt: accepts `CAND`, and
`WINDOW` where its slot hands one), the LOOP HEADER (accepts `UPPER`), and the
CALLER (accepts `START` and the match end; re-enters at E1 for find-all). The
structural check (§3.5) reads them as `accepts` sets like any slot's.

### 1.3 The walk, and what it does not do

```c
const CandRow *cand_select(CandSlot slot, CandRoute route, const CandSel *s, uint64_t flags);
/* first row with row->slot == slot, !(row->c.deny & flags),
 * routed for `route` (cand_routed's rule), and row->c.applies(s) */
```

- **Total per (slot, route).** Every (slot, route) pair a body asks has a last
  row whose predicate is `cand_always`, so `NULL` stays unreachable (today's
  `dfa_select` property, `emit_dfa.c:5155`). A structural check enumerates the
  pairs (§3.5).
- **No eager plan.** Each body site asks exactly the (slot, route) it asks today,
  when it asks today. A whole-artifact "resolve every slot up front" pass is NOT
  part of the refactor. It would evaluate predicates today's code never reaches,
  and predicates have observable side effects: `pcrec_find_byte_rate` records
  its first ask, the ask is what puts `RX_FINDINGS` into the artifact
  (`pcrec_find_stamp`, `src/core/findings.c:373`), the facts layer's `used`
  column records every ask (§3.3 item 3), and a predicate can `pcrec_ctx_fail`.
- **The invariant is a SET, not an order** [r2 sound-n1]. No artifact surface
  records ask ORDER: `used` is a per-fact yes/no (`facts.c:115`), and
  `RX_FINDINGS` reads a boolean written after every emitter has run
  (`findings.c:373-380`). So the refactor's obligation is: (a) the SET of
  predicates evaluated per artifact is today's, except additions the commit
  declares and shows to be pure (C5b's BOUND reads, §3.2); and (b) no newly
  evaluated predicate reaches an assertion, because the one order-sensitive
  effect is which internal error wins when two predicates assert. The trace
  (§3.3 item 5) still compares ORDERED sequences, because a reorder it sees is
  a change of the skeleton the refactor promised not to make.
- **(b)'s population is derived** [r2.1 S-N5]. `assert_reach.py` walks the
  call graph from every predicate root (`inventory.tsv`'s PRED, WALK and
  INLINE members, 34) and lists every `pcrec_ctx_fail` it reaches
  (`assert_reach.tsv`). 13 roots reach an assertion, through 8 sites in 5
  definitions: `ofs_test_of` (`emit_dfa.c:6106`, `:6111`), `pf_dfa_start_set`
  (`:6668`, `:6671`), `vm_start_assert_starts` (`:6779`, reached from N7),
  `pf_scan_set_of` (`:6922`, reached from P3 and RETRY) and the byte-rate
  prior's `find_derive_byte_rate` (`src/core/findings.c:305`, `:309`). The
  facts layer adds one (`src/facts/req.c:252`, the `req_*` facts' shared walk,
  which asserts on the first ask whoever asks). One more assertion sits beside
  an INLINE site rather than under a predicate: BOUND's one-way check in
  `emit_attempt` (`emit_dfa.c:9374-9382`), which stays in the body after C5.
  The only predicates the refactor ADDS to an artifact's ask set are C5b's
  BOUND reads (§2.3 item 4): `dfa_interior_dead` and the `start_anchor` fact,
  and neither reaches any site in the list. So (b) holds for C5b by the
  population, not by the sentence; a later commit that adds an ask re-runs the
  script.
- **Slots read each other only through the walk.** A predicate that needs
  another slot's SELECTION calls `cand_select` (or today's walk) for it; it
  never restates that slot's predicate (`litscan_k82h.md` r1 C-C10). Revision 1
  named three such reads and claimed none restates; that was false for BOUND
  [r2 sound-M5]. The slot DAG of SELECTION reads is:

  | reader | reads | today | after |
  |---|---|---|---|
  | P3 `dominated` (G1) | NEXT, on the artifact's route (`CR_DFA` or `CR_ATTEMPT`) | `dfa_cand_scan` `:7034` (calls) | reads through `cand_read`, edge declared (C6) |
  | F1 `handoff` | PRESENCE | `req_handoff_applies` calls `req_admit` `:7336` | reads through `cand_read`, edge declared (C6) |
  | R4 `adaptive-dense` | NEXT's scanned set | `pcrec_dfa_cand_ppm` `:7079` (calls) | reads through `cand_read`, edge declared (C6) |
  | P2 `one-attempt`, DFA arm | BOUND on `CR_ATTEMPT` | RESTATES B1∨B2 (`engine == ATTEMPT && dfa_interior_dead(s1u)`, `:7141`) | calls (C5b) |
  | P2 `one-attempt`, VM arm | BOUND on `CR_VM` | RESTATES B3∨B4 (`start_anchor != NONE`, `:7138`) | calls (C5b) |
  | N7 `first-class` | BOUND on `CR_VM` | RESTATES (declines where B3/B4 apply, `:6813`) | calls (C5b) |
  | R3 `anchored` | BOUND on `CR_VM` | RESTATES (`start_anchor != NONE`, `emit_vm.c:11090`) | calls (C5b) |
  | N12 `pred-memchr` (`attempt_cand`) | BOUND on `CR_ATTEMPT` | RESTATES B1∨B2 as its own loop (`:4110`) | calls (C5b) |

  The four restatements agree with BOUND today only because BOUND is itself a
  direct read of the same fact or machine property. Any new or changed B row
  (D-2b's own fix, a VM B row reading the machine on hybrids, any §4 bound row)
  would leave them behind; reading BOUND makes that impossible. The SELECTION
  graph is acyclic: BOUND reads nothing, NEXT reads BOUND, PRESENCE reads NEXT
  and BOUND, FIRST reads PRESENCE, RETRY reads NEXT and BOUND.

### 1.4 The mapping column

`where_to_start.md` §1.1's four strengths, sharpened to the cases the inventory
actually contains:

| `map` | a hit (or the slot's event) says | rows | `hands` |
|---|---|---|---|
| `EXACT0` | the hit IS a candidate start | `memchr*`, `byte-class*`, `first-*` | `CAND` |
| `EXACTK` | a candidate starts `k` before the hit | `offset-set*`, `run-pinned*` | `CAND` |
| `EXACTPRED` | a candidate starts one AFTER the hit (a predecessor byte) | N12 (ENG_ATTEMPT `memchr`) | `CAND` |
| `EXACTREV` | (future) a reverse walk from the hit records the candidate | D151's row | `CAND` (give-up: `LOWER`) |
| `WINDOWLO` | no start below `n − W` | `window` | `LOWER` |
| `WINDOWHI` | no start above `n − minw` (none at all if the window is too short) | `ceiling` | `VERDICT` |
| `LOWERBOUND` | no start below `hit − K`; scan forward from there | `handoff` | `LOWER` |
| `PRESENCE` | absence of the landmark in the window proves no match | `emitted`, `set-leads` | `VERDICT` |
| `ONE` | at most one start position exists (0, or `search_from`) | the bound rows | `UPPER` |
| `RECOVER` | the start is read from the end (reverse machine) or is `search_from` (pinned) | `reverse-pass`, `pinned` | the start |
| `STEP` / `RESEED` / `ADAPT` | the retry's next candidate: advance one character, re-call the prefilter, or switch by gap | the reseed rows | `CAND` / `LOWER` (re-entry) |
| `NONE` | nothing is skipped | every fallback | the slot's identity |

The column is DATA for checks and the listing. No emitter branches on it (the K84
rule: a reader tests a field that names a property, and `map` names one).

### 1.5 The give-up posture column

Three postures exist today, and the refactor writes each down per row:

- `NEUTRAL`: the row changes no attempt the VM runs. Every DFA-route row, and the
  presence rows (they answer NOMATCH only where no attempt could succeed).
- `ONE_WAY`: the row skips VM attempts the deny arm runs, so a give-up may become
  an answer, never the reverse (D148 Q6 + Q-R3: steps, work, frames, trail, the
  `_in` buffers). Rows: `first-class` (VM hat), the `anchored`/`gstart` VM bound
  rows, `adaptive-dense`/`adaptive` (`hyb_reseed.md` §4's contract), `ceiling`.
- `FIXED`: the row must never move the give-up surface. Rows: `handoff`
  (Frank's Q10: declined on a count-collapsed prefilter so the deny flag never
  moves it), and PRESENCE's route-keyed `noscan` payload, K65 set-rest and K66
  whole-run: they exist exactly to give a no-DFA-scan route a linear no-match
  proof that does not depend on the prior's pick (K65/K66) [r2 sound-M2].

D151 Q4 ruled the reverse-walk row `ONE_WAY`. The column makes the K82-vs-D148
difference a visible property instead of a sentence in two notes.

### 1.6 Typed handoffs and the re-entry graph [r2 sound-M5, frank-reentry]

Frank asked whether the start table can be re-entered, for example VM then
prefilter. **Yes, and today's artifacts already do it**: the table is asked
once per question at COMPILE time, but the emitted search runs the selected
rows as a small state machine at RUN time, and three of its edges loop back.
The refactor makes every edge DATA: each row declares what it `hands` (§1.1),
each slot what it `accepts` (§1.2), and each edge below is a pair the skeleton
wires. A structural check (§3.5) fails if a row hands a type its successor slot
does not accept.

**The handoff types**, each with the soundness obligation the handing row owes:

| type | meaning | the row's obligation |
|---|---|---|
| `LOWER` | no match starts below `x` | every match start ≥ the accepted lower bound is ≥ `x` (nothing skipped); on a re-entry, the row's PROGRESS obligation below |
| `UPPER` | no match starts above `x` | every match start ≤ `x` |
| `CAND` | `x` is the next position that can start a match | `x ≥` the accepted `LOWER`, and no match starts in `[accepted LOWER, x)` [r2.1 S-N1(d)]. Today's VM retry satisfies the first half by construction: the prefilter searches from `attempt_position` and the loop assigns its answer (`emit_vm.c:13280-13290`) |
| `WINDOW` | the candidate's match lies in `[x, e)` | every match starting at `x` ends by `e` (H3: dropped on a cut-bearing program, `pcrec_vm_prefilter_window`) |
| `VERDICT` | NOMATCH now, or pass the accepted bound through unchanged | NOMATCH only where no attempt could succeed |
| `HIT` [r2.1 S-N1(e)] | `x` is the LEFTMOST occurrence of the gate's landmark at or after the accepted `LOWER` | no occurrence in `[accepted LOWER, x)` (`litscan_k82h.md` §1.1a's contract, which the handoff's soundness depends on) |
| `START` [r2.1 S-N1(e)] | `x` is the reported match's start | `x` is the leftmost-first start of the match ending at the accepted END, and `x ≥` the accepted `LOWER` |

**The edges** (E1-E10 are shipped; E11-E12 are §4's sockets):

| # | from (hands) | to (accepts) | where it is emitted today | re-entry? |
|---|---|---|---|---|
| E1 | caller (`LOWER` = startpos) | WINDOW | every entry; the position domain (§2.5) applies first | — |
| E2 | WINDOW W1 (`LOWER`) | PRESENCE, FIRST, NEXT | `pcrec_emit_end_window_clamp` raises `search_from` | — |
| E3 | PRESENCE (`VERDICT`, and `HIT` = the gate's leftmost hit `c` [r2.1 S-N1(e)]) | FIRST (accepts `HIT`) | `pcrec_emit_req_byte_check` | — |
| E4 | FIRST F1 (`LOWER` = `max(search_from, c − K)`) | NEXT | `emit_req_handoff`'s `handoff_position` → `fwd.from` (DFA body) or the prefilter's startpos (`first`, `emit_vm.c:13413`) | — |
| E5 | NEXT on the DFA body (`CAND`) | the VERIFIER (the forward machine, re-seeded per `reseeds`) | `dfa_form_derive` | **yes, inside the scan** [r2.1 S-N1(c)]: a hit the verifier rejects re-enters the scan. On EXACTK rows `cand` is `k` BEHIND the hit, so the scan resumes below a byte it has already seen |
| E6 | NEXT on a hybrid's inlined prefilter (`CAND` = `window[0][0]`, `WINDOW` = `window[0][1]` under `mrl_win`) | the VM attempt loop (`attempt_position`, `window_end`) | `vm_emit_search_body` `:13416-13426` | — |
| E7 | **RETRY (`LOWER` = the failed attempt's position, advanced one character by K49) → NEXT on the inlined prefilter**, which hands E6's `CAND`/`WINDOW` again | the VM attempt loop | `retry_win` (`emit_vm.c:13281`) and the adaptive `retry_seed` (`:13329`) | **yes: the "VM then prefilter" loop** |
| E8 | NEXT on the VM-only hat N7 (`CAND`) | the VM attempt; after a failed attempt the loop advances and RE-SEEKS (the hat's own re-entry) | `pcrec_emit_vm_start_seek` | **yes** |
| E9 | BOUND (`UPPER`) | the ATTEMPT / VM loop header | `start_max` (`emit_dfa.c:9385`), `attempt_max` (`emit_vm.c:13479`) | — |
| E10 | the artifact's return (`START` and the match END) | the CALLER, who re-enters at E1 with `LOWER` = the end (find-all) | the caller-driven loop, `match_api.md` §3.1; the entry re-applies the position domain (K73's offset-0 rule, K75's alignment) to the new `LOWER` | **yes: find-all** |
| E11 | (future) NEXT `rev-inner` give-up (`LOWER` = the resume point, past the previous landmark hit `h`) | NEXT's forward scan (accepts `LOWER`); the row that wires the edge is FIRST's `handoff-rev`, selected at compile time | §4.1 | yes |
| E12 | (future) RETRY on `CR_VM` (`LOWER`) | NEXT N7's seek | §4.3, K90 | yes |

[r2.1 S-N1(e)] revision 2 wrote E11 as "→ FIRST `handoff-rev`", which handed
`LOWER` into a slot that accepts only `HIT`: the edge was ill-typed, and the
check §3.5 promises would have rejected the note's own socket. At run time
the give-up hands `LOWER` to NEXT's scan; FIRST is where the row is SELECTED.

**Termination of every cycle: a per-row PROGRESS obligation** [r2.1
S-N1(a)-(c)]. Revision 2 said a re-entering row "inherits the termination
proof by declaring `hands = LOWER`". It does not: `LOWER` is a soundness type
(nothing skipped), and a row can satisfy it while re-entering at the same
position forever. So each re-entering edge carries its own PROGRESS argument,
written in the row's review and checked there (the structural check can see
that an edge re-enters; it cannot prove the advance):
- **E5** (inside the scan): on EXACTK rows `cand = hit − k` can sit below
  bytes the scan already read, and the cycle still terminates because `_ofsskip` returns a `cand ≥ scan_position`
  (`pf_emit_ofs`, `emit_dfa.c:6520-6524`: `scan_position = cand`) and the
  verifier consumes at least one byte before the scan is asked again.
- **E7, E8**: K49's character advance (`pcrec_enc_advance`, never zero) moves
  the failed attempt's position before NEXT is asked again.
- **E10**: on a NON-empty match the new `LOWER` is the end, past the start. On
  an EMPTY match `end == start`, and the strict advance is the CALLER's
  empty-match rule (`match_api.md` §3.1, "The empty-match advance",
  `#find-all`), not the artifact's: the artifact's obligation ends at reporting the
  span [r2.1 S-N1(b)].
- **E11** (future): the landmark search must resume PAST the previous hit `h`.
  A scan restarted at `s* < h` re-finds `h`, and the walk from `h` reaches the
  same `s*` again, which is a cycle with every type obligation met
  [r2.1 S-N1(a)].
- **E12** (future): as E7, K49's advance before the re-seek.

**RECOVER's accepted `LOWER`.** The reverse pass keeps the ENTRY's `search_from`
as its lower bound, never the handoff's (`litscan_k82h.md` Q6): RECOVER accepts
E2's `LOWER`, not E4's. The edge table makes that a declared input, which is
what keeps a later FIRST row from silently narrowing the reverse pass.

**What the refactor does with this.** The no-mover refactor declares `hands` on
every row and `accepts` on every slot as data, and checks the pairs; it moves
no emitted handoff text. The emitted state machine is the same; what changes is
that a new row (§4) is reviewed against a written edge, not against prose.

---

## 2. The inventory

### 2.1 How it was derived, and how we know it is complete (K35) [r2 sound-M2/M3/M6, checks-M1]

Revision 1 hand-listed ten sites, and both critics found sites it did not name.
For a no-mover refactor the inventory IS the claim, so revision 2 derives it by
TWO INDEPENDENT DERIVATIONS and one CROSS-RECORD, and checks them against one
another. [r2.1 S-N4] Revision 2 said "three methods that share no source"; that
was false: method 3 takes its family from `call_graph.txt`, so it is not
independent of method 1. Methods 1 and 2 share no source (a parse of `src/`;
the compiler's output). Method 3's independent content is which sites someone
found worth defending, and it is read against method 1, never as a third vote.
All instruments are in `start_table/` and read nothing in this note.

1. **The call graph** (`call_graph.py` → `call_graph.txt`). It parses every
   top-level definition under `src/`, headers included (1,892 at revision 2.1:
   functions, tables, initializer and string data, types, function-like and
   object-like macros, so that `DFA_SELECT(...)` reaches `dfa_select`; revision
   2 parsed 1,392 and missed types, sized tables, string constants and header
   `static inline`s [r2.1 C-N1]), draws an edge for every definition a body
   names (a call, a function pointer stored in a table row, a table walked; a
   TYPE is never an edge), and computes:
   - R, everything reachable from the two emitters (`pcrec_emit_dfa`,
     `pcrec_emit_vm`), each member tagged by whether the three search-body
     writers (`emit_unanchored`, `emit_attempt`, `vm_emit_search_body`), the
     two stamp writers, or only the emitter's plan reach it;
   - SEEDS, the landmark reads: every `pcrec_fact_*` accessor `facts.def`
     declares except the E1 shape facts (`kinds`, `nullable`), the route read
     `pcrec_artifact_has_dfa_scan`, and the four MACHINE landmark producers
     (`unanch_start`, `dfa_interior_dead`, `cand_from_live_seeds`,
     `pcrec_dfa_cand_ppm`) plus the VM program properties read as fields
     (`root_minw`, `mrl_win`, `nclamp`, `prefilter_collapsed`). The machine
     list is the one hand input; it is the row contract's `landmark` column,
     and it is named in the script so a reviewer can contest it;
   - the FAMILY: members of R from which a seed is reachable (plus every
     function a family table stores, plus the ROW TYPES: every family table's
     element type and the types it embeds by value [r2.1 C-N1]): **110
     definitions + 15 seeds** (revision 2: 99; the eleven added are nine row
     types, among them `DfaCand`, `DfaPf`, `ReqAdmitRow`, `PcrecReseedRow`,
     plus `dfa_matches[]`'s `DfaMatch` (NOTSTART) and the `pcrec_reseed_nrows`
     count);
   - the SITES: every conditional line in a family body that names a seed, a
     family member, or a local bound from one: **149** (the added one is
     `vm_plan_reseed`'s walk bound, `pcrec_reseed_nrows`).
2. **The deny-delta census** (`deny_census.py` → `deny_census.tsv`,
   `deny_transitions.tsv`, `deny_hidden.tsv`). Every distinct corpus pattern
   (3,595) is compiled at default and under each of the 13 start-family
   deny/force flags, in four arms (auto / `--engine=vm` × byte / utf8): 201,320
   compiles. A MOVER is an artifact whose emitted bytes differ. Each mover is
   attributed to the start stamps that moved with it (route-keyed, so a stamp
   shared by two routes' rows is split); a mover whose bytes moved while NO
   start stamp did is HIDDEN, and its first differing emitted line is
   fingerprinted. A decision site no stamp reports is therefore found by its
   emitted TEXT. It reads bytes and stamps only. The 13 flags are a hand
   choice; [r2.1 C-N3] a 1-in-10 sample over the other 29 `--list-axes` flags
   (`allflags_sample.tsv`, §3.3 item 4) found one more flag that moves a start
   row without changing the route (`-fno-length-prune`, through `Vm.mrl_win`).
3. **The sabotage anchors, a cross-record** (`sabotage_anchors.py` →
   `sabotage_anchors.tsv`). Every anchor site of every sabotage row (463 row
   files, 462 distinct ids — S169 is shared by two files, a finding in the
   re-check record — 480 sites: `SAB_FILE` and `SAB_FILE2`, every target file)
   is mapped to the definition it sits in, by the call graph's own parse. A
   row is in the start family iff its owner is in the call-graph family, so
   this method's FAMILY comes from method 1 [r2.1 S-N4]. **Owner resolution is
   total on `src/`** [r2.1 C-N1]: revision 2 left 61 sites with owner `?` (a
   comment block, a struct, a `.def` row, a header) and classed them OTHER,
   which dropped five start-family rows (S282 in `DfaCand`, S299 the
   `req_run` fact row, S475/S479/S496 the verb/callout conjunct comments). The
   resolution is now, in order: the innermost definition; a `facts.def` row →
   its fact seed (the graph's own seed rule); another `.def` row → the row,
   family iff a decision SITE names it; a header comment → the definition it
   heads; a file-scope directive; a file outside `src/` (the graph's scope);
   and anything else in `src/` is a HARD ERROR. Today: def 440, outside 24,
   datarow 11, lead 3, factrow 1, filescope 1, unresolved 0.

**The completeness argument.**
- `inventory_check.py` fails unless every family member and seed has exactly
  one disposition line in `inventory.tsv` and that file names nothing the graph
  does not. Today: 125 / 125 (TABLE 5, WALK 6, PRED 27, EMIT 19, INLINE 1,
  READER 9, PROJ 11, ROUTE 3, BODY 3, LANDMARK 15, PLAN 5, NOTSTART 12,
  TYPE 9). Every NOTSTART line carries its reason (the machine-form census,
  the match-here axis, the MRL storage). A future site enters the family
  through the graph and fails the check until it is dispositioned.
- **Methods 2 and 3 are reconciled MECHANICALLY** [r2.1 checks]. Revision 2
  said "every hidden fingerprint is mapped" in prose. `reconcile.py` reads
  `reconcile_map.tsv` and fails on: a start stamp key a deny-census mover
  moved that no line maps to a member (10 keys, 10 mapped); a hidden-mover
  fingerprint that matches no line or two (5,192 hidden movers over five
  members: the prior's ask `req_byte_dominated_by` 3,494, the fact stamp
  `pcrec_fact_req_run` 1,594, `pcrec_fact_req_byte` 55, P4's body
  `pcrec_emit_req_byte_check` 46, and `OUTSIDE:§2.5` 3, the collapse rung's
  `ENGINE_SEL`); a mapped member not in `inventory.tsv`; and an OTHER sabotage
  row whose anchor text names a family identifier (0). Its failing direction
  is measured: two map lines removed → `UNMAPPED STAMP VM_START_SCAN`, 12
  unmapped fingerprints, exit 1.
- Every family sabotage row's owner is dispositioned (it must be: the family IS
  the graph's), and every RE-AIM row's anchor overlaps the edit set (§3.5).
- **What the methods found that revision 1 did not name** (each now in §2.2):
  K65 set-rest (`emit_req_set_rest` `:1267`) and K66 whole-run
  (`req_run_tests` `:1041`) — family EMIT members with route reads, and the
  `-fno-req-run`/`-fno-req-byte` hidden-mover fingerprints; `prefix_k.c`'s admission — the only
  `src/opt/` family member (LANDMARK), S187/S188; the hybrid-prefilter route
  dispatch on `job->engine` (`pcrec_emit_dfa_engine` `:10271`, ROUTE) and the
  entry gate `fit.chosen == ENGM_DFA` (`:8854`, `:8867`, `:9152`), which
  together decide that an ATTEMPT hybrid's inlined body is an ATTEMPT customer;
  `pcrec_vm_prefilter_window`, the WINDOW handoff (E6); `dfa_search_is_pinned`
  and its 7 pointer-comparing readers; `vm_render_listing`'s second H1 reader.
- **What the methods cannot see.** A start decision made by a definition that
  reads no landmark (a constant choice) is not a decision. A decision read only
  at run time inside emitted text (the adaptive re-seed's gap test) is the row's
  payload, not a compile-time site; it is dispositioned through its emitter.

The populations below come from `deny_census.py`'s per-arm stamp census, which
is `row_census.py`'s census plus its DENY ARMS [r2 checks-M4], written to
`row_census.tsv` from the same compiles (`row_census.py` alone reproduces any
arm). `anchor_agree.py` compares the two derivations of "every match starts at
one position" on the ATTEMPT population (§2.4 D-2b).

### 2.2 The table, in first-match order

Columns:
- **pop** is the corpus artifact count in the arms where the row is reachable.
  `a/b` means auto/byte; `vm/b` means `--engine=vm`/byte; `a/u` and `vm/u` are
  the utf8 twins. Route-keyed where a stamp serves two routes [r2 sound-M1].
- **predicate** is today's function, reused by pointer (except the EDIT SET,
  §3.1).

**WINDOW** (routes DFA, ATTEMPT, VM; the caller-facing entry only: on a DFA body
under `fit.chosen == ENGM_DFA`, so the VM hybrid's inlined prefilter never clamps
and the VM entry clamps before calling it; `emit_dfa.c:8867`, `:9166`,
`emit_vm.c:13170`):

| # | row | deny | predicate | map | pop |
|---|---|---|---|---|---|
| W1 | `window` | — (the bit is a FACT deny: `-fno-end-window`, bit 29, empties `end_window`, `facts.def`) | `pcrec_fact_end_window(cx) >= 0` (today `w < 0` returns, `emit_dfa.c:938-939`) | `WINDOWLO` | a/b 288, a/u 0 (the fact declines every non-boundary encoding) |
| W2 | `none` | — | `cand_always` | `NONE` | rest |

**PRESENCE** (all routes; the entry; today `req_admits[]`, `emit_dfa.c:7249`,
asked by `pcrec_emit_req_byte_check` `:1375`, `req_lead_byte` `:7280`,
`req_handoff_applies` `:7336`, the `<string.h>` decision `:10007`, the stamp):

| # | row | deny | predicate | map | pop (a/b) |
|---|---|---|---|---|---|
| P1 | `none` | — | `req_none_applies` `:7193` (no `req_byte` and no `req_run` of length ≥ 2) | `NONE` | 1,178 |
| P2 | `one-attempt` | — | `req_one_attempt_applies` → `req_route_one_attempt` `:7135` (VM arm: BOUND(`CR_VM`) ≠ `all` ∧ (exact hybrid ∨ frameless); DFA arm: route ATTEMPT ∧ BOUND(`CR_ATTEMPT`) ≠ `all`) — RESTATED today, a BOUND read after C5b [r2 sound-M5] | `NONE` | 263 |
| P3 | `dominated` | — | `req_dominated_applies` `:7201` → `req_byte_dominated_by` `:7171` over `dfa_cand_scan` (reads NEXT) | `NONE` | 1,198 |
| P4 | `set-leads` | 45 | `req_set_leads_applies` `:7212` | `PRESENCE` | stamps `"emitted"`; deny-delta 14 (a/b), 8 (a/u) |
| P5 | `emitted` | — | `cand_always` | `PRESENCE` | 582 (incl. P4) |

PRESENCE's payload carries one ROUTE-KEYED composition, `u.admit.noscan`
[r2 sound-M2]: where the artifact has no DFA scan (`!pcrec_artifact_has_dfa_scan`:
route VM-ONLY), the emitted pre-check also tests every other member of the
necessary set with its own `memchr` (**K65 set-rest**, `emit_req_set_rest`
`:1259`, decision `:1267`) and compares the whole run before the window (**K66
whole-run**, `req_run_tests` `:1023`, decision `:1041`). These are not
first-match alternatives — they compose with P4/P5 — so they are not rows (a row
would be the product-row smell §0a item 2 rejects); they are a function of
(the selected P row, the route). Posture `FIXED` (§1.5). Sabotage rows S277,
S278, S316, S459 sit on them. Their population is the VM-ONLY share of P4/P5:
124 VM-ONLY artifacts in auto/byte stamp `REQ_WHY "emitted"`, 125 in auto/utf8. The bodies stay byte-stable; the C1 trace records each decision.

**WIDTH** (route VM; `emit_vm.c:13234`):

| # | row | deny | predicate | map | pop |
|---|---|---|---|---|---|
| H1 | `ceiling` | — | `v->root_minw >= PCREC_MINW_MAX` | `WINDOWHI` | 6 in every arm (stamp and emitted test agree, §3.4) |
| H2 | `none` | — | `cand_always` | `NONE` | rest |

The ceiling row's predicate reads a `Vm` field. So `CandSel` gains a
`const CandVmFacts *vm` pointer carrying the five `Vm` fields that rows read
(`root_minw`, `mrl_win`, `nclamp`, `has_push`, and the reseed calibration). It is
filled by the one VM caller and NULL elsewhere. That pointer is the only new
input.

**FIRST** (all routes asked; today `req_uses[]`, `emit_dfa.c:7364`, asked by
`pcrec_emit_req_byte_check`'s return `:1392`, the body assertion `:8878`, the
stamp `:7391`; VM-ONLY asks it too and F1 declines there on `!has_dfa_scan`
[r2 sound-n3]):

| # | row | deny | predicate | map | pop |
|---|---|---|---|---|---|
| F1 | `handoff` | 46 | `req_handoff_applies` `:7332` (calls PRESENCE; `pcrec_artifact_has_dfa_scan`; K finite; not collapsed; the `\G`-hybrid decline) | `LOWERBOUND` | a/b 163 (DFA-UNANCH 116, DFA-ATTEMPT 10, HYB-UNANCH 34, HYB-ATTEMPT 3), a/u 280 (192, 10, 75, 3) |
| F2 | `scan-from-startpos` | — | `cand_always` | `NONE` | rest |

**NEXT**. Today `dfa_pfs[]` (`emit_dfa.c:6863-6898`, asked by `dfa_pf_of`
`:6903` (5 call sites), `vm_start_row` `:6931` (3), `pf_scan_set_of` `:6915`,
`pcrec_dfa_scan_state_written` `:7435`, `dfa_form_derive` `:8378`) plus
`attempt_cand` (`:4105`; 4 readers: emission `:9323`, G1 `:7044`, the
`<string.h>` test `:9997`, the stamp `:10411`). Every DFA row's predicate is gated
on `s->forward` and on `UnanchStart.kind` (`unanch_start` `:4191`, ONE derivation),
so it is only ever reached on an ENG_UNANCH forward machine. The S490 argument,
`emit_dfa.c:6650`.

**N3/N4's real admission is not in their predicate** [r2 sound-M3]. They apply
iff `UnanchStart.ofsk.nsel > 0`, and `nsel` is the output of
`pcrec_prefix_ksets` (`src/opt/prefix_k.c:179-326`, called from `unanch_start`
`:4319`): a cost model over the byte-rate prior (`pcrec_find_set_ppm` `:186`)
with two admission rules, the MATERIAL bar (`:280`) and the measured "the scan
must move off offset 0" rule (`:281-308`, the call graph's site `:308`).
Sabotage S187/S188 sit there. That is the "pick INSIDE a row" level (the survey's
family 3.2): the table reads its result and does not own it (§2.5). It also
decides N1/N2's reachability, which is D-4.

| # | row | routes | deny | predicate | map | scan | pop (a/b; a/u) |
|---|---|---|---|---|---|---|---|
| N1 | `run-pinned-bounded` | DFA | 16\|32 | `pf_run_bounded_applies` `:6051` | `EXACTK` | OFS + VERIFY | 18; 0 |
| N2 | `run-pinned` | DFA | 16\|32 | `pf_run_applies` `:6054` (common `:6023`, the identity clause: D-4) | `EXACTK` | OFS + VERIFY | 114; 3 |
| N3 | `offset-set-bounded` | DFA | 16 | `pf_ofs_bounded_applies` `:5990` (admission: `prefix_k.c`) | `EXACTK` | OFS | 48; 71 |
| N4 | `offset-set` | DFA | 16 | `pf_ofs_applies` `:5993` (common `:5984`; admission: `prefix_k.c`) | `EXACTK` | OFS | 333; 530 |
| N5 | `first-memchr-bounded` | DFA | 47 | `pf_first_memchr_bounded_applies` `:6681` (core `pf_dfa_start_set` `:6648`, T = S, D148 add. 3) | `EXACT0` + re-seed | PF | 36; 25 |
| N6 | `first-class-bounded` | DFA | 47 | `pf_first_class_bounded_applies` `:6679` | `EXACT0` + re-seed | PF | 34; 34 |
| N7 | `first-class` | VM | 47 | `pf_vm_start_applies` `:6806` (its anchoring conjunct `:6813` RESTATES BOUND(`CR_VM`); a BOUND read after C5b) | `EXACT0` | VMSTART | 66 (vm/b 2,327); 68 (vm/u 2,352) |
| N8 | `memchr-bounded` | DFA | — | `pf_memchr_bounded_applies` `:5798` | `EXACT0` | PF | 162; 151 |
| N9 | `memchr` | DFA | — | `pf_memchr_applies` `:5801` | `EXACT0` | PF | 775 (281 DFA + 494 hybrid); 722 (225 + 497) |
| N10 | `byte-class-bounded` | DFA | — | `pf_bcls_bounded_applies` `:5804` | `EXACT0` | PF | 100; 101 |
| N11 | `byte-class` | DFA | — | `pf_bcls_applies` `:5807` | `EXACT0` | PF | 538; 564 |
| N12 | `pred-memchr` (NEW NAME, row ID only; stamps `"memchr"`) | ATTEMPT | — | `attempt_cand` `:4105` (s1u live ∧ the live-seed set `usable ∧ use_memchr`; its `anchored` loop `:4110` RESTATES BOUND(`CR_ATTEMPT`)) | `EXACTPRED` | MLINE | 33 (DFA 27 + HYB 6); 33 |
| N13 | `none` | DFA, ATTEMPT, VM | — | `cand_always` | `NONE` | — | a/b: DFA-UNANCH 258, DFA-ATTEMPT 185, HYB-ATTEMPT 170, DFA/HYB-EMPTY 50/14, HYB-UNANCH 0; VM-ONLY 287 (vm/b 895) |

Row N12 needs a row name distinct from N9, because the walk and the checks key on
identity. It still stamps `"memchr"` (its `stamp` projection), so
`RX_DFA_PREFILTER` keeps today's token (D-1). **The VM hybrid's inlined
prefilter body takes the rows of ITS machine's route** [r2 sound-M1]: an
ENG_UNANCH prefilter is a `CR_DFA` customer of N1-N11/N13, an ENG_ATTEMPT
prefilter (any pattern with a BOT) a `CR_ATTEMPT` customer of N12/N13. In
auto/byte: 935 hybrids on `CR_DFA`, 176 on `CR_ATTEMPT` and 14 empty on
`CR_ATTEMPT` (`row_census.tsv`'s `HYB-UNANCH:` / `HYB-ATTEMPT:` keys; revision
1's `HYBRID:` key counted both, and the ATTEMPT ones a second time under
`ATTEMPT:`). The split corrects revision 1 in two places: all 184 of its
`HYBRID: "none"` were ATTEMPT (170) or empty (14) hybrids, not DFA-route
customers (an ENG_UNANCH hybrid prefilter stamps `none` 0 times), and 6 of its
500 hybrid `memchr` were N12's predecessor scan. F1 also fires on the ATTEMPT
route (10 DFA + 3 hybrid in auto/byte).

**RETRY** (route VM, asked only where `fit.prefilter` holds, the caller's guard
kept: `vm_plan_reseed`, `emit_vm.c:11107`, decided before the VM body, n2; today
`pcrec_reseed_rows[]` `emit_vm.c:11010`, whose predicates are a closed tag read
by a `switch`, `vm_reseed_holds` `:11082`; the refactor turns each tag into a
predicate function with the same body):

| # | row | deny | predicate | map | pop (a/b) |
|---|---|---|---|---|---|
| R1 | `exact` | — | `Vm.mrl_win` | `STEP` (or the clamp recompute) | 562 |
| R2 | `clamped` | — | `Vm.nclamp > 0` | `RESEED` | 112 |
| R3 | `anchored` | — | BOUND(`CR_VM`) ≠ `all` (today RESTATED as `start_anchor` ≠ NONE; a BOUND read after C5b) | `STEP` (never reached) | 48 |
| R4 | `adaptive-dense` | 37 | `pcrec_dfa_cand_ppm(cx) · cal.gap > 10⁶` (reads NEXT) | `ADAPT`, armed | 13 |
| R5 | `adaptive` | 37 | `cand_always` | `ADAPT`, probation | 390 |
| R6 | `fixed` | — | `cand_always` | `STEP` | 0 at default; 403 a/b, 420 a/u under the deny arm (COUNTED, `row_census.tsv`) |

**BOUND** (`emit_dfa.c:9333-9388` for ATTEMPT, `emit_vm.c:13471-13483` for VM).
An ATTEMPT hybrid asks BOUND TWICE, on two routes: `CR_ATTEMPT` in its inlined
prefilter and `CR_VM` in its VM loop [r2 sound-M1]; `^(a)(b|c)` emits
`start_max = 0` in the prefilter and `attempt_max = search_from` in the loop.

| # | row | routes | deny | predicate | map | pop |
|---|---|---|---|---|---|---|
| B1 | `bot` | ATTEMPT | — | `dfa_interior_dead(d, s1u) ∧ dfa_interior_dead(d, s1g)` (`#ifdef PCREC_NO_GSTART` folds the second into the first) | `ONE` (0) | 293 (DFA 136 + HYB 157) |
| B2 | `gstart` | ATTEMPT | — | `dfa_interior_dead(d, s1u)` | `ONE` (`search_from`) | 21 (DFA 16 + HYB 5) |
| B3 | `anchored` | VM | — (FACT deny bit 28 empties `start_anchor`) | `start_anchor == BOT` | `ONE` (0, via `attempt_max = search_from`) | a/b 332, vm/b 468 |
| B4 | `gstart` | VM | — (bit 28, as B3) | `start_anchor == GSTART` | `ONE` | a/b 5, vm/b 20 |
| B5 | `all` | ATTEMPT, VM | — | `cand_always` | `NONE` | ATTEMPT 74 (60 + 14); VM 1,141 |

Today the VM's two values share ONE emitted line (`attempt_max = search_from`)
and differ only in the stamp (`RX_VM_START`). The rows keep that: `u.bound` holds
the same string on B3 and B4, so the literal MOVES into the row (§3.5: S263 is
re-aimed) [r2 sound-M6]. The ATTEMPT route's `start_max` keeps its three strings,
also in `u.bound`.

**RECOVER** (today `dfa_search_starts[]` `emit_dfa.c:7894`, asked by
`dfa_search_start_of` `:7902` and through `dfa_search_is_pinned` at 7 sites,
which today compare the selected row's POINTER to `&dfa_search_starts[0]`
`:7917`; after C3 they read `u.recover.pinned` [r2 sound-m2]):

| # | row | routes | deny | predicate | map | pop (a/b) |
|---|---|---|---|---|---|---|
| S1 | `pinned` | DFA | 22 | `start_pinned_applies` `:7860` (P1-P4) | `RECOVER` (`search_from`) | 183 |
| S2 | `reverse-pass` | DFA, ATTEMPT | — | `cand_always` | `RECOVER` (reverse) | 2,685 (incl. 388 ATTEMPT + 64 empty, D-2) |

**Row count:**
- 37 rows: W 2, P 5, H 2, F 2, N 13, R 6, B 5, S 2; plus PRESENCE's route-keyed
  `noscan` payload (K65, K66).
- 7 deny bits act on these rows directly: 16, 32, 45, 46, 47, 22, 37.
- 5 more act through FACT denies: 28, 29, 30, 31, 44 (`facts.def`'s deny
  column). That makes the 12 start-family bits; the deny arms also sweep the
  force bit 20 (`-fprefilter-collapse`) [r2 sound-m4].
- No bit is renumbered (§3.7).

### 2.3 Does the table reproduce today's choice on every route?

By construction, before any measurement:

1. Every row's predicate IS today's function (pointer identity, not a re-spelling),
   except the declared edit set (§3.1, `refactor_edit_set.tsv`). Revision 1
   counted two mechanical exceptions; the derived count is larger
   [r2 sound-M6]:
   - the reseed tags become five two-line functions (S441 plants the `anchored`
     arm);
   - `attempt_cand`'s boolean becomes N12's predicate, with its `CandSet` output
     carried in `CandSel` as `pf_dfa_start_set`'s `t` is today (S81, S82);
   - seven INLINE conditions become predicate functions: W1 (`w < 0`), H1
     (`root_minw >= PCREC_MINW_MAX`), B1/B2 (the `a_bot`/`a_gst` pair with its
     `#ifdef PCREC_NO_GSTART`), B3/B4 (the `start_anchor` `if`). Their only
     witnesses today are the anchors S169 (H1), S263 (B3/B4's literal) and none
     for B1/B2 (§3.4 adds them);
   - C5b's four BOUND restatements become BOUND reads (§1.3).
2. Within each slot, the rows keep today's relative order. Today's arrays are
   per-question already, so a slot's rows ARE one of today's arrays, or (NEXT) one
   array plus a row on a route no existing row serves. BOUND, WINDOW and WIDTH
   were if/else chains, and their order is the chain's.
3. Routes are disjoint where they need to be. N12 is ATTEMPT-only, and ATTEMPT
   never consulted `dfa_pfs[]` (`dfa_cand_scan`'s branch `:7039`,
   `dfa_prefilter_name`'s branch `:10402`, `pcrec_dfa_scan_state_written`'s
   UNANCH test), so adding the ATTEMPT route cannot move an UNANCH selection, and
   vice versa. The route of the hybrid's inlined body is `job->engine`; a
   `CandSel` built anywhere from `fit.chosen` is the M1 mis-route, and it is
   the C1 trace (row identity, not stamps) that would show it, because N9 and
   N12 both stamp `"memchr"` [r2 sound-M1].

   **There is no "one dispatch"** [r2.1 S-N2]. Revision 2 said the route "is
   taken at the one dispatch that already decides it"; `emit_dfa.c` tests
   `job->engine` at fifteen places, each choosing `CR_DFA` vs `CR_ATTEMPT`
   (or EMPTY) for itself:

   | line | definition | what it decides |
   |---|---|---|
   | `:4354` | `dfa_engine_is_empty` | the EMPTY route |
   | `:4386`, `:4458`, `:4519` | `dfa_table_name`, `dfa_scan_edge_name`, `dfa_uniform_folds` | machine-form stamps (NOTSTART readers) |
   | `:6656` | `pf_dfa_start_set` | N5-N7's route conjunct (S490's anchor) |
   | `:7039` | `dfa_cand_scan` | G1 reads N12 or NEXT |
   | `:7090` | `pcrec_dfa_cand_ppm` | R4 reads the scanned set |
   | `:7141` | `req_route_one_attempt` | P2's DFA arm (also C5b's) |
   | `:7428` | `pcrec_dfa_scan_state_written` | NEXT's scan-state reader |
   | `:7865` | `start_pinned_applies` | S1 |
   | `:9995` | `pcrec_emit_prologue` | the `<string.h>` decision |
   | `:10271` | `pcrec_emit_dfa_engine` | THE body dispatch |
   | `:10382`, `:10402`, `:10483` | `dfa_scan_name`, `dfa_prefilter_name`, `dfa_prefilter_offsets` | the stamps |

   They agree today because each reads the same field. The refactor adds ONE
   derivation, `cand_route_of(cx)` (C2, in `refactor_edit_set.tsv`), and from
   C3 every one of the fifteen reads it, so a later change to the route rule
   (the route class in `CandSel`, filed below) is one edit, not fifteen. The
   fifteen lines are `line` entries of the edit set, so the sabotage rows
   anchored on them are derived re-aims (S490 at C3).
4. Every body site asks the same (slot, route) at the same point (§1.3). So the
   SET of predicates evaluated is today's, except C5b's declared BOUND reads,
   which evaluate `dfa_interior_dead` (pure: no fact, no prior, no assertion) on
   `CR_ATTEMPT` and the `start_anchor` fact on `CR_VM` — a fact P2, N7 and R3
   already ask, so the `used` column cannot move [r2 sound-n1].

Per route class, then — the (slot, route) pairs ONE artifact asks, in the
code's ask order [r2 sound-M1, sound-n2, sound-n3]:

| route class | entry (route) | DFA-shaped body (route) | loop | also |
|---|---|---|---|---|
| DFA-UNANCH | W, P, F (`CR_DFA`) | RECOVER (asked first, `dfa_search_is_pinned`, `:8829`), N, S (`CR_DFA`) | — | N on `CR_VM` for the `VM_START_SCAN` stamp |
| DFA-ATTEMPT | W, P, F (`CR_ATTEMPT`) | N12/N13 then B (`CR_ATTEMPT`), S2 by stamp | — | as above |
| DFA-EMPTY | W, P, F | the empty machine (`dfa_engine_is_empty`, read inside F1/S1) | — | as above |
| VM-ONLY | W, P, H, F (F1 declines) (`CR_VM`) | — | N7/N13, B (`CR_VM`) | — |
| HYB-UNANCH | W, P, H, F (`CR_VM`) | N, S (`CR_DFA`) | RETRY (planned before the body), B (`CR_VM`) | — |
| HYB-ATTEMPT | W, P, H, F (`CR_VM`) | N12/N13, **B (`CR_ATTEMPT`)**, S2 by stamp | RETRY, **B (`CR_VM`)** | BOUND asked on two routes |
| HYB-EMPTY | as HYB-* | the empty machine | RETRY, B | — |

- **utf8:** no slot reads the encoding. Rows read facts whose derivations do
  (`end_window`'s decline, `start_set`'s `start_cls` assertion, the
  `req_byte` prior gate, the run pick that D-4 turns on), and those are not
  touched.
- **The route set is coarser than the predicates** [r2 sound-n4]: HYBRID vs
  VM-ONLY (`fit.prefilter`, read inside N7 and P2) and EMPTY
  (`dfa_engine_is_empty`, read inside F1 and S1) are route distinctions
  re-tested inside predicates. The `routes` column cannot express them, so
  there is a third axis inside the predicates. The refactor keeps those tests
  where they are (no mover); a later change can carry the route CLASS in
  `CandSel` so the predicates read it instead of re-testing. Filed, not folded.

The sweep (§3.3) is then the measurement that this argument has no hole.

### 2.4 Where today's sites disagree

The census found five. **None changes an answer.** A no-mover refactor preserves
each; each fix is its own ruled change.

- **D-1. One token, two mechanisms.**
  - **What:** `RX_DFA_PREFILTER "memchr"` means "a `memchr` for the byte a match
    BEGINS with" on ENG_UNANCH (N9, offset 0). On ENG_ATTEMPT it means "a
    `memchr` for the byte BEFORE a candidate" (N12, offset −1:
    `(?m)^ERROR`'s newline).
    [Frank 2026-10-06, measured on main `build/pcrec`: N9 `memchr` does NOT fire
    on a plain literal like `ERROR`, which takes `offset-set` (offsets `0,1*`,
    rarity-picked); N9 fires for e.g. `E[0-9]+`.]
  - **Population:** 33 (27 DFA + 6 HYBRID) ENG_ATTEMPT artifacts in auto/byte stamp it,
    DFA and HYBRID alike: D-1 also fires on ATTEMPT hybrids (`(?m)^(a)`:
    `REQ_WHY "dominated"` elides the `a` pre-check on a predecessor-`\n` scan)
    [r2 sound-n6].
  - **What disambiguates it:** `RX_DFA_SCAN`. The spec says so.
  - **Who is fooled:** G1 (`dfa_cand_scan` `:7044`) reads N12's byte as "the
    byte scanned", and `req_byte_dominated_by`'s density compare then prices a
    predecessor-byte scan as if it were a start-byte scan. No answer moves (an
    elided pre-check is an optimization). But the dominance argument ("the scan
    already tests the byte the pre-check would") is about a different byte
    position. R4's read of the same byte is NOT a victim: the predecessor byte
    IS the scan's stop density, which is what R4 prices.
  - **Refactor:** keeps the token (N12's `stamp` projection) and the G1 read.
  - **Fix:** a separate change, either G1 declining `EXACTPRED` rows (a `map`
    read) or a stamp value `pred-memchr`. Recommend the first. §6 Q4.
- **D-2. `RX_DFA_START "reverse-pass"` on artifacts with no reverse machine.**
  - **What:** `dfa_search_starts[]`' fallback stamps every non-pinned DFA scan,
    including the 388 ENG_ATTEMPT and the 64 empty-engine artifacts.
    `(?m)^ERROR`'s artifact carries no reverse table and stamps
    `"reverse-pass"`.
  - **The spec:** `docs/spec/match_api.md#stamp-dfa-start` documents the value as "the
    artifact carries its reverse machine and walks it backwards", then lists
    "whose scan is `attempt` or `empty`" among its population. The two sentences
    contradict each other.
  - **Refactor:** keeps the token (S2 routes DFA|ATTEMPT).
  - **Fix:** a third value (`attempt-start`) on ATTEMPT/empty. That is an abi
    event and a stamp-vocabulary change (D80 spec hunk, readers by grep). §6 Q5.
- **D-2b. Two derivations of "one start position", disagreeing on one pattern —
  inside one artifact** [r2 sound-M1].
  - **The two derivations:** the ATTEMPT route reads the MACHINE (B1/B2:
    `dfa_interior_dead`). The VM route, G2's VM arm and `RETRY`'s `anchored` row
    read the AST FACT `start_anchor`.
  - **The census** (`anchor_agree.txt`, 388 ATTEMPT artifacts, byte): 293
    agree on `bot`, 20 agree on `gstart` and 74 agree on unanchored. One
    disagrees: `(?(DEFINE)(?<g>\Ga))(?&g)`, where the machine proves `gstart`
    and the fact says unanchored. The fact does not see through the call.
  - **Inside one artifact:** the capturing twin `(?(DEFINE)(?<g>\Ga))(?&g)(b)`
    is an ATTEMPT HYBRID: its inlined prefilter emits
    `start_max = search_from /* fully \G-anchored */` (B2) while its VM loop has
    no `attempt_max` (B5, the fact says unanchored). Re-probed on this build.
    So D-2b is a disagreement between two routes of ONE artifact, which is why
    BOUND is keyed per (slot, route) and never per artifact.
  - **Direction:** this is the direction `emit_dfa.c:9358-9372` calls
    "welcome": a tighter bound on the DFA, a looser one on the VM. It is
    correct either way, and only the VM runs extra attempts that fail.
  - **Refactor:** keeps route-specific predicates (B1/B2 vs B3/B4) and the
    one-way assertion `:9374-9382`. C5b's readers read BOUND on THEIR route (P2's
    VM arm reads `CR_VM`), so D-2b's split is preserved exactly.
  - **Fix:** teaching `start_anchor` to see through a non-recursive call is a
    FACT change. It is a mover on the VM route and its own ruling. §6 Q6.
- **D-3. The listing's own text has drifted from the row.**
  - **What:** `--list-axes`' `first-memchr-bounded` row still reads "T = S & E*
    (E* every seed state's escape set; T == S)" (`src/dump/axes_dump.c:106`).
    D148 addendum 3 retracted `S & E*`, and the code reads `T = S`
    (`pf_dfa_start_set` `:6648`).
  - **Cause:** the text lives in a hand table in another file from the row.
    `req_admits[]` and `pcrec_reseed_rows[]` carry theirs beside the row.
  - **Refactor:** moves every `desc` beside its row VERBATIM, the stale text
    included, so stream 5 stays identical.
  - **Fix:** the declared listing commit C7 (§3.2) corrects it. DONE at C7
    (lane stc67): the row now reads "scanned as T = S, a non-empty proper
    subset of the start state's escape set E".
- **D-4. The run pin vs the offset-k pick: two derivations of "which byte the
  scan tests"** [r2 sound-M4; survey §4.2].
  - **What:** N1/N2 (`run-pinned[-bounded]`) apply only if the pin's scan offset
    EQUALS the offset-k model's (`pf_run_applies_common`, `emit_dfa.c:6037-6041`,
    an identity clause). The two offsets come from different pickers: the run
    reader picks by rarity with a RIGHTMOST tie (`findings.c:518`); `prefix_k`
    picks by its cost model with a LEFTMOST strict `<` (`prefix_k.c`).
  - **Probed on this build** (all DFA artifacts):

    | pattern | arm | `REQ_RUN` | offsets | `DFA_PREFILTER` | `REQ_WHY` |
    |---|---|---|---|---|---|
    | `\d\dzq` | byte | `7a71@0` | `0,2*,3` | run-pinned | dominated |
    | `\d\dzq` | utf8 | `7a71@1` | `0,2*` | **offset-set** | **emitted** (+ `REQ_HANDOFF "2"`) |
    | `\d\dxyz` | byte | `78797a@2` | `0,2*` | **offset-set** | **emitted** |
    | `[0-9][0-9]hello` | byte | `68656c6c6f@3` | `0,4*` | **offset-set** | **emitted** |
    | `abc$` | byte | `616263@1` | `0,1*,2` | run-pinned-bounded | dominated |
    | `abc$` | utf8 | `616263@2` | `0,1*` | **offset-set-bounded** | **emitted** (+ `REQ_HANDOFF "0"`) |

  - **Systematic under utf8, not a tie:** the prior is NONE under utf8, so the
    run reader takes the rightmost member while `prefix_k` keeps the leftmost;
    the pin and the pick then disagree on whole families. This — not a coverage
    accident — is why `run-pinned-bounded` is 0 and `run-pinned` 3 under utf8
    (§2.2, revision 1's §3.4 read it as a gap).
  - **What it moves:** N1/N2's reachable population on a whole encoding,
    `REQ_WHY` (dominated vs emitted) and `REQ_HANDOFF` on the affected artifacts.
    No answer: the offset-set row plus a separate run pre-check is exact too.
  - **Refactor:** preserves it: N1/N2's predicate keeps the identity clause by
    pointer, and both pickers stay where they are (§2.5: the pick inside a row is
    not the table's).
  - **Fix:** a separate ruled change, [TIE-ALIGN] re-scoped from "ties" to "one
    landmark-candidate ranking with one tie rule" (the survey's family 3.2), which
    removes the identity clause. It moves prefilter FORMS by construction, so it
    needs D119's bench evidence. §6 Q10.

Not disagreements, but recorded because a reader will ask:
- The K73 offset-0 seek moves `search_from` on the DFA body and
  `attempt_position` on the VM (by design: `\G` reads `search_from`).
- The VM entry clamps before calling the hybrid's prefilter, which itself does
  not (by design: one clamp per search).
- The handoff is declined on VM-only artifacts even where the VM hat seeks
  (`where_to_start.md` §1.3 item 1: computed and thrown away). That is a missing
  row, not a disagreement, and §4.1's `handoff-rev`/VM-first socket is where it
  is served.

### 2.5 What is NOT in the table, and why

Every site below touches "where a match begins". Each stays outside because it
answers a different question:

- **The position domain.** The startpos guard (`-fstartpos-guard`, 3 rows), the
  UTF check (`-futf-check`), K73's offset-0 rule (`pcrec_emit_start_zero`, 7
  call sites in 3 spellings), K50's attempt-loop boundary guard (`:9452`) and
  K49's retry advance (`pcrec_enc_advance`, `emit_vm.c:13270`). These define
  which positions are LEGAL candidates under the encoding and the caller
  contract. They are the encoding backend's text and apply to every row's
  output and to every re-entering `LOWER` (§1.6 E7, E8, E10). They are not
  alternatives to any row, and no row may move them. They stay a fixed layer
  under the table. Their selections (`startpos-guard`, `utf-check`) are
  caller-contract axes with their own first-match rows in the listing.
  [r2.1 sibling lens] They are themselves a dispersed decision family (K73's
  rule in 3 spellings, K50 site 2's "THREE 'try the next start' mechanisms",
  `emit_dfa.c` ~`:9390`, and K49's advance), filed as its own
  FILED-not-scheduled row **[DEC-POSDOM]** (`docs/dev/plan.md`), evaluated
  after the fold and never folded into `cand_rows[]`.
- **The pick INSIDE a row** [r2 sound-M3, sound-M4]. Which byte at which offset
  a row scans — `prefix_k.c`'s cost model and admission (N3/N4), the run reader
  (`findings.c:518`), the pin (`kset.c`), the set pick (`req_set_pick`) — is a
  RANKING, not a first-match choice (D152: "an argmin is a planner"). The rows
  read the ranking's result through facts and `UnanchStart`. The refactor does
  not touch it; its one cross-picker identity clause is D-4.
- **The machine's start STATE.** `dfa_seeds[]` (`seeded`/`constant`) decides how
  an attempt's state is computed at a candidate, which is the verifier, not the
  candidate. The DFA hat's re-seed READS it (`pf_emit_moved_reseed`) and does
  not choose it.
- **The match-here entry** (`dfa_matches[]`, `unwrapped`/`search-filter`): the
  caller supplies the start, so there is nothing to find. (The call graph puts
  it in the family only because it reads the empty-engine route; it is NOTSTART
  in `inventory.tsv`.)
- **Scan edges and stay skips** (`dfa_edges[]`, `dir_fwd_skip`): skips INSIDE an
  attempt's walk, past bytes that keep a non-start state where it is. They read
  no start landmark.
- **Engine selection and prefilter admission** (`select_engine.c`'s `analyses[]`,
  `fit.prefilter` `:862`, `prefilter-lang`, `fit_rungs[]`): these decide which
  ROUTE an artifact is, and the table reads the route. §5.4 argues they stay
  separate tables.

---

## 3. The no-mover refactor plan

### 3.1 Principles

- **Implement, then replace** (memory `pcrec-general-mechanisms-not-special-cases`:
  "implement-then-replace is fine"). The new array and walk exist beside the old
  ones, and readers switch slot by slot.
- **Functions stay; tables, walks and a declared edit set move.** Every
  predicate and every emitter function keeps its name, its file and its body
  text, EXCEPT what `start_table/refactor_edit_set.tsv` lists [r2 sound-M6]:
  the five arrays and six walks (`def`), the identifiers they retire (`token`),
  and the inline predicate lines and BOUND restatements that become rows or
  row reads, the stamp/listing readers C5 moves and the fifteen route tests
  that read `cand_route_of` [r2.1 S-N2, S-N3] (`line`), each with its commit. That file is the plan's one
  statement of what changes; the sabotage consequences are derived from it
  (§3.5), and a commit that edits a line the file does not name is out of plan.
  Every memfn manifest emitter name stays valid (C17 reads functions by name,
  `tests/memfn/site_manifest.tsv`).
- **D148 Q2's rename rides the NEXT-slot commit** (C3): `DfaPf` → `CandRow`'s
  `u.pf`, `DfaSel` → `CandSel`, `dfa_pfs[]` → `cand_rows[]`. It is the commit
  D151 Q5 scheduled, widened. D151 Q5 said "until `handoff-rev` exists". Frank's
  2026-10-06 direction moves the fold ahead of that row (§6 Q1).
- **Every commit is a no-mover with no abi event**: abi stays 64, and no spec
  sentence about an artifact moves. The exceptions are C7, a declared
  stream-5-only change, and C3's spec hunk to `docs/spec/registry.md:267`, a
  sentence about an INTERNAL (it names `dfa_select`) that goes stale when C3
  deletes it (D80) [r2 checks-m8].

### 3.2 The commit sequence

| commit | what | what moves |
|---|---|---|
| C0 | **DONE (lane stc0, 2026-10-06; `../dev/lanes/stc0_report.md`, the C0 outcome paragraph below)**. **instrument** (no `src/`): `emit_sweep.py` gains `--extra ARG` (repeatable, appended to streams 1-4 on BOTH sides, before `--pattern`), a sixth stream `--emit-facts` (streams 1/2's patterns, `--emit-facts=byte,utf8`, identity required), `--patterns-file` (constructed witnesses into streams 1-3) [r2 checks-m7], and per-arm DIFFER floors (§3.3 item 2) [r2 checks-M2]; every existing floor re-pinned to the measured reach (today 3,480 against a reach near 4,100; composition 32 against 38) [r2 checks-m4]; the census scripts move per Q7. **And the TRACE instrument** [r2.1 C-N2], so that C1 has something to run: (i) a seventh stream `--trace` that builds both sides with `-DPCREC_CAND_TRACE` — `build_from_rev` (`scripts/emit_sweep.py:327`, whose `:344` runs plain `make -j4 CC=…`) gains a `CFLAGS` pass-through, used on BOTH sides; (ii) the trace's stderr captured per compile, never mixed into the artifact on stdout; (iii) each record tagged with its pattern index and arm by the sweep, not by the compiler; (iv) a trace-DIFF tool that compares per-pattern ORDERED sequences and applies the commit's declared-multiplicity filter (C5b: records whose `site` is one of its BOUND readers, and nothing else); (v) a records-per-arm FLOOR (a trace arm that prints nothing passes any diff); (vi) a FAILING-DIRECTION control: a planted swap of two records and a planted reorder within one pattern, each of which the diff must report, run at C0 and kept as a sabotage row on the diff tool (S-id next free on main at build); also the full all-flag deny sweep (§3.3 item 4, ≈54 min at 6 jobs) | nothing in `src/` |
| C1 | **BUILT (lane stc1, 2026-10-07; `../dev/lanes/stc1_report.md`, the C1 outcome paragraph below)**. **selection trace** under `-DPCREC_CAND_TRACE` (a compile-time knob, `OPTK_DEBUG`'s precedent `emit_dfa.c:4320`; scratch builds only): every decision site `inventory.tsv` classes WALK or INLINE, the two ROUTE dispatches, K65/K66's decisions (`:1041`, `:1267`) and `prefix_k`'s admission outcome (`nsel`) print one record (§3.3 item 5). C1 byte-sweeps the trace build's stdout against the default build (the trace must move no emitted byte) | nothing in the default build (`#ifdef` text only) |
| C2 | **BUILT (lane stc2, 2026-10-07; `../dev/lanes/stc2_report.md`, the C2 outcome paragraph below), pending merge**. **implement**: `CandRow`, `CandSlot`, `CandSel` (`DfaSel` + `vm` + `route`, typedef'd to the old name), `cand_select`, `cand_route_of(cx)` (the ONE route derivation, §2.3 item 3 [r2.1 S-N2]), and `cand_rows[]` holding all 37 rows with today's predicates and the `hands`/`accepts`/`list[route]` columns. No reader switched. Under `PCREC_CAND_TRACE` each old walk ALSO runs `cand_select` and aborts on a different row (the both-walks FILTER oracle, run in both orders, §3.3 item 6) | nothing |
| C3 | **BUILT (lane stc3, 2026-10-07; `../dev/lanes/stc3_report.md`, the C3 outcome paragraph below), pending merge**. **replace NEXT + RECOVER**: `dfa_pf_of`, `vm_start_row`, `pf_scan_set_of`'s callers, `pcrec_dfa_scan_state_written`, `dfa_form_derive`, `dfa_search_start_of` and N12's four `attempt_cand` readers read `cand_select`, each body building its `CandSel` route from `cand_route_of(cx)`, and the fifteen `job->engine` tests (§2.3 item 3) reading it too [r2.1 S-N2]; `dfa_search_is_pinned` reads `u.recover.pinned`; `dfa_pfs[]`/`dfa_search_starts[]` deleted; D148 Q2's rename; `cand_rows_check.py` re-aimed (§3.5); the SPEC hunk: `registry.md:267`, and the readers `reader_grep.sh` finds outside `src/` [r2.1 C-N4] — `docs/spec/match_api.md` (formerly `:2348`, `:2441`; the rewritten doc no longer names `dfa_pfs[]`) and `docs/spec/tuning.md:2530` name `dfa_pfs[]`; `lib/CLAUDE.md:421`, `tests/codegen/CLAUDE.md`, `tests/mech/CLAUDE.md`, `tests/mech/run_sabotage_matrix.sh:2579`, `tests/codegen/run_cand_rows.sh:3` and the `Makefile:517` comment name retiring identifiers and move in the commit that retires them (C3's `dfa_pfs`/`dfa_select`, C4's `req_admit`, C5's `pcrec_reseed_rows` readers at C7) | re-aims (derived): S222, S283, S284, S490 |
| C4 | **BUILT (lane stc4, 2026-10-07; `../dev/lanes/stc4_report.md`, the C4 outcome paragraph below), pending merge**. **replace PRESENCE + FIRST**: `req_admit`/`req_use` read `cand_select`; `req_admits[]`/`req_uses[]` deleted; `pcrec_req_admit_row`/`pcrec_req_use_row` become projections of `cand_rows[]`; D148 Q2's `DfaSel` → `CandSel` spelling sweep (ruled "C4 or C7", taken here) | S462, S473; the sweep's S518-S521, S527 |
| C5 | **BUILT (lane stc5, 2026-10-07; `../dev/lanes/stc5_report.md`, the C5 outcome paragraph below), pending merge**. **replace RETRY + BOUND + WINDOW + WIDTH**: `vm_plan_reseed`'s loop → `cand_select`; the `VRS_P_*` tag and `vm_reseed_holds` deleted; the inline bound strings (into `u.bound`), the end-window test and the root-minw test read their slot's row; AND their stamp and listing readers do too: `<PREFIX>_END_WINDOW`, `<PREFIX>_VM_START`, `<PREFIX>_VM_ROOT_MINW` and `--emit-ir`'s `root-minw` row project the row (the value still from its landmark) [r2 sound-m1]; the start tables' last `DFA_SELECT` callers deleted (`req_admits[]`/`req_uses[]` go at C4; `dfa_select` itself STAYS: the six machine-form axes `dfa_reprs`, `dfa_views`, `dfa_seeds`, `dfa_accs`, `dfa_matches`, `dfa_edges` walk it and are outside the start table, §2.5; C3 already removed its route plumbing — ruled 2026-10-07, `../dev/lanes/stc3_report.md` §4 item 1) | S169, S263, S371, S372, S441 |
| C5b | **BUILT (lane stc5b, 2026-10-08; `../dev/lanes/stc5b_report.md`, the C5b outcome paragraph below), pending merge**. **BOUND readers** [r2 sound-M5]: P2 (both arms), N7's anchoring conjunct, R3 and `attempt_cand`'s `anchored` loop call `cand_select(BOUND, route)` instead of restating it. Byte-identical because each restatement equals its route's B rows today (§1.3); the ask set grows only by `dfa_interior_dead` on `CR_ATTEMPT` (§2.3 item 4), declared to the trace diff | S269, S274, S276, S492, and S441 again (R3's line, `emit_vm.c:11090`, which C5 also moves) [r2.1 S-N3] |
| C6 | **BUILT (lane stc67, 2026-10-08; `../dev/lanes/stc67_report.md`, the C6/C7 outcome paragraph below), pending merge**. **the listing reads the table**: `axes_dump.c`'s `prefilter`, `search-start`, `req-admit`, `req-use`, `hyb-reseed`, `vm-anchor-bound`, `end-window` sections project `cand_rows[]` by `list[route]` (NOT `match`: `dfa_matches[]` stays outside, §2.5 [r2 sound-m3]), printing today's `kind`, order, listed name and `desc` text byte for byte; N12 has no listing; `AXIS_DESC`'s start rows deleted | nothing (stream 5 identical) |
| C7 | **BUILT (lane stc67, 2026-10-08), pending merge; REFACTOR A IS COMPLETE**. **declared listing commit, stream 5 only, NOT an abi event**: D-3's stale desc corrected; `kind` becomes `list` for the start axes that ARE lists now; spec hunk in `docs/spec/registry.md`; `tests/registry/` pins re-read | `--list-axes` text only |

**C0's outcome** (lane stc0, `../dev/lanes/stc0_report.md`). Built as listed,
in `scripts/emit_sweep.py` and a new `scripts/trace_diff.py`, with self-tests
`scripts/tests/{emit_sweep,trace_diff}.py.test` (mech arm `emitsweep`). The
arm table is `DIFFER_PINS` (64 cells: the 14 deny/force arms × byte/utf8 ×
two streams, the plain `-e utf8`/`-i` cells, the asserted zeros, a null arm),
pinned from `deny_census.tsv`/`plain_arms.tsv` (no `src/` or corpus change
since `4743ebb5`), `-fno-length-prune` re-pinned from the full-corpus gate
run (lane stc0b, ubuntubudu, 2026-10-06: 449/112 and 678/0 at byte, 468/118
and 815/0 at utf8; every other floor already equalled its measured value).
The full every-flag sweep (29 flags × 4 arms, 543 s at `-j10`) found no new
route switch; four non-start flags move `REQ_WHY`/the start family at a
handful of patterns (`-fno-possessify` 6/9, `-fno-altcls-merge` 2/8,
`-fno-altcls-factor` 0/1, `-fno-premul-table` 2 at utf8), recorded as a C1
edit-set input candidate (the VM frame/one-attempt verdict the admission
reads) in `stc0_report.md` §6. Sabotage rows S550-S555 are on mech arm
`emitsweep`. The census scripts' Q7 move (`call_graph.py` and its siblings to
`tests/codegen/`) did NOT ride C0, and the report files it as owed. The trace
EXPERIMENT (Q3) PASSED its bar. The C0 hook was a prototype on the scratch
branch `scratch/stc0-trace`, not merged. Its results, and the two design
conditions for C1 (a declared site literal, never `__func__`; the SET compare
as the gate), are in §6 Q3.

**C1's outcome** (lane stc1, `../dev/lanes/stc1_report.md`).
`PCREC_CAND_TRACE_REC`/`_RECF` (`src/core/internal.h`) print one record
per start decision at 25 declared site keys. They cover:
- the walks;
- §0a's inline sites;
- the two route dispatches, plus `dfa_engine_is_empty`;
- K65/K66;
- `prefix_k`'s `nsel`;
- the kit's decision reads B1-B5, B5′, B8, B19 and B20.

The site table is the report's §2 and is C2's input. Frank's two conditions
are structural:
- the macro pastes `"" site`, so a non-literal site does not compile;
- `emit_sweep --trace` gates on the SET compare and prints the ordered
  compare as a diagnostic (`--trace-ordered` swaps them).

The records floor is re-pinned at 256,608 / 62,962 (C1), then at the post-R4c′ landing to 262,901 / 64,776 (the measured count at lane/stc1 185a4a8c). Every declared site
key must be reached. Three corrections to this note:
- "every site `inventory.tsv` classes WALK or INLINE" under-names C1, since
  the inventory has one INLINE member and §0a lists seven inline decisions;
- the K65/K66 citations above are pre-R4c (now `req_set_rest_members` and
  `req_run_tests`, read by `req_site_define`);
- `refactor_edit_set.tsv` names no line for K65/K66's decisions, so
  S277/S278/S316 class RE-RUN where C4 will re-aim them (proposed additions
  in the report §3.1, not applied).

The inventory itself was stale after R4c (five members undispositioned),
and is re-dispositioned 127/127.

**C2's outcome** (lane stc2, `../dev/lanes/stc2_report.md`). Built as listed,
with no reader switched: `CandRow`/`cand_rows[]` (37 rows), `cand_nodes[]`
(the `accepts` column per slot and for the three non-slot successors),
`CandSel` (`DfaSel` renamed, plus `vm`), `cand_select(slot, sel, flags)`,
`cand_route_of(cx)`, and `CandSlot`/`CandVmFacts`/`CandRoute` (now with
`CAND_ROUTE_ATTEMPT`) in `src/core/internal.h`. Under `-DPCREC_CAND_TRACE`
all thirteen old decisions (the eight walks and the five inline sites) run
the both-walks oracle, in both orders (`-DPCREC_CAND_NEW_FIRST`), with
nested walks quiet so the `CANDTRACE` stream stays C1's, plus a table
self-check (§3.5's planned structural checks, in C) and a `CANDROW` hit
counter (§3.4). A route oracle holds `cand_route_of` to the body dispatch.
`tests/codegen/run_cand_oracle.sh` (`make test-cand-oracle`) runs both builds
over 42 witnesses that reach every row; S594-S599 (a predicate difference, a
route mis-key, a dropped deny, a wrong inline restatement, a non-total slot,
an unaccepted handed type) are all DETECTED. `call_graph.py` gained
`cand_select` as a root (`TABLE_ROOTS`), so the table joins the family at C2:
inventory 141/141. Corrections to this note, all in the report §4: §1.1's
"`c.name` unique" contradicts §2.2's four `none`s and two each of
`anchored`/`gstart` (identities made unique, a `tok` column keeps today's
spelling); §1.2's `accepts` cannot type §1.6's own E2 (FIRST accepts
HIT | LOWER) and gives VERDICT no consumer (the CALLER accepts it);
§1.3's `cand_select` carries the route twice (built from `s->route`, so §3.5's
"every CandSel initializer names `.slot`" has nothing to check); NEXT's
"+ WINDOW" is a route-class property, not a row's; `u` is deferred to C3-C5,
which move each old table's fields in. The full-corpus both-orders run, the
byte sweep against main, `make test-codegen` and `make test` are OWED in the
lane's detached chain (report §6).

**C3's outcome** (lane stc3, `../dev/lanes/stc3_report.md`). Built as
listed, with no emitted byte moved (the report's §3 carries the sweep):
`dfa_pfs[]` and `dfa_search_starts[]` are deleted into `cand_rows[]`
(`DfaPf` is the NEXT payload `CandPf`, `CandRow.u.pf`; RECOVER's is
`CandRecover`, `u.recover.pinned`, which `dfa_search_is_pinned` returns);
every NEXT and RECOVER reader asks `cand_select` with its route from
`cand_route_of`, N12's four readers through `attempt_next_of` on
`CAND_ROUTE_ATTEMPT` (the candidate set rides `CandSel.cand`); fourteen of
the fifteen `job->engine` tests read `cand_route_of` (the fifteenth,
`req_route_one_attempt`'s, is C5b's line in the edit set and anchors S269
and S276); `prefilter`/`search-start` `--list-axes` rows project the table;
re-aims S222/S283/S284/S490 as derived, plus S495 (its anchor read
`pf->scan`, now `pf->u.pf.scan`), with S490's equivalence re-verified under
the moved premise; S594/S595 re-homed onto the hit counter (`cand_hit`).
Corrections to this note, all in the report §4: `dfa_select` is NOT deleted
at C5 (six machine-form axes keep it; C3 drops its route parameter and
`cand_routed`/`DFA_SELECT_ROUTED`); `dfa_search_start_of` is kept as the
RECOVER slot's one `CandSel` builder (the edit set's "function deleted"
token is retired, `dfa_pf_of`/`vm_start_row` being kept the same way);
RECOVER asked on `cand_route_of` moves the C1 trace record's ROUTE field
from `dfa` to `attempt` on ENG_ATTEMPT artifacts (row unchanged, no byte),
a declared trace difference; the `DfaSel` spelling sweep is held (78 sites,
five memfn-arch anchors on `req_handoff_applies(const DfaSel *s)`).

**C4's outcome** (lane stc4, `../dev/lanes/stc4_report.md`). Built as
listed, with no emitted byte moved on the light gates (the heavy chain is the
report's §6): `req_admits[]`/`req_uses[]` are deleted into `cand_rows[]`
(their fields are the PRESENCE payload `CandAdmit`, `u.admit`: verdict and
description, and the FIRST payload `CandUse`, `u.use`); `req_admit` and
`req_use` walk the table and print the row's `tok`;
`pcrec_req_admit_row`/`pcrec_req_use_row` project the listed rows and return
false past the last (the `nrows` externs are gone, `axes_dump.c` loops on the
return). Corrections and choices, all in the report §4: the entry slots are
asked on `CAND_ROUTE_DFA`, the C1 trace's route, NOT on `cand_route_of`,
because §2.3's entry route on the VM route classes is `CR_VM`, which
`cand_route_of` cannot derive (it reads `job->engine`); the trace build
instead holds every other asked route to the same row (`cand_hit_every`,
sabotage S600), so the choice is honest until the filed route-class change.
The `rerun_at` column names NO row at C4 (no anchor sits in a C4 owner's
body; the two re-aims are S462/S473); the lane re-ran the walk-reached
predicate rows by judgment ([MECH-REACH]). The `DfaSel` sweep rode C4 (the
edit set's new `token DfaSel`), re-aiming S518-S521 and S527.

**C5's outcome** (lane stc5, `../dev/lanes/stc5_report.md`). Built as
listed, with no emitted byte moved and the C1 trace record-for-record
unchanged on the light gates (the report's §3; the heavy chain is its §6):
`pcrec_reseed_rows[]`, its `VRS_*` tags and `vm_reseed_holds` are deleted
into the RETRY rows (payload `CandReseed`, `u.reseed`: action, start, armed,
desc; in `core/internal.h`, since `emit_vm.c` reads it), `vm_plan_reseed`
asks `pcrec_cand_select_vm(RETRY)`, and `pcrec_reseed_row` projects the rows
for `--list-axes` (C4's bool-accessor shape; `pcrec_reseed_nrows` gone). The
inline decisions read their slot's row: WINDOW (`u.window.clamp`) through
`cand_window_clamps` on CAND_ROUTE_DFA (C4's entry rule) with
`cand_hit_every`; WIDTH (`u.width.check`) through `vm_width_row`; BOUND on
CAND_ROUTE_ATTEMPT in `emit_attempt` and on the VM route through
`vm_bound_row`, `u.bound` carrying `one` and each route's text (`start_max`;
the VM's one `attempt_max` line, `CAND_VM_BOUND_ONE`, S263's new anchor).
The stamps and the listing row project the same rows: `<PREFIX>_END_WINDOW`
(the fact's window where the row clamps, the row's listed `none` where not),
`<PREFIX>_VM_START` (the BOUND row's listed name, which is the stamp's
vocabulary), `<PREFIX>_VM_ROOT_MINW` and `--emit-ir`'s `root-minw` (the WIDTH
row; the value from `root_minw`). `dfa_select` STAYS (the C3 ruling; the
edit set's `def DFA_SELECT` is annotated). The C2 both-walks oracle had
nothing left to compare and is deleted (`CandRow.was` with it);
`run_cand_oracle.sh` builds one trace compiler. Corrections and choices, all
in the report §4: each stamp and listing reader RE-ASKS the one derivation
its body asks (the RECOVER precedent) rather than reading a selection stored
before the stamps, because §1.3's "no eager plan" and §3.6's "one selection"
meet in the VM's phase order and the trace's ordering decides it; the edit
set named four lines that C5 keeps (a landmark value read and two stamp
calls; amended, with reasons) and its `rs->row` token is `rs->row->`; the
`rerun_at` rule's gap recurs (rows reached through the new walks re-ran by
judgment, listed); `[cand-no-name-strcmp]` widened to every slot under §3.5's
row-name-expression rule, with new sabotage S605.

**C5b's outcome** (lane stc5b, `../dev/lanes/stc5b_report.md`). Built as
listed, with no emitted byte moved. P2 (both arms), N7's anchoring
conjunct, R3 and N12 read BOUND through ONE selection read,
`cand_read(reader, slot, sel, site)` (`CAND_READ`; `CAND_BOUND_ONE` tests
`u.bound.one`), on their own route: P2's VM arm and N7/R3 on
CAND_ROUTE_VM, P2's DFA arm on `cand_route_of` (the fifteenth `job->engine`
test, now gone) and N12 on its own CAND_ROUTE_ATTEMPT selection
(`attempt_cand` takes the `CandSel`). The slot graph gains §1.3's selection
DAG as data, `CandNode.reads[]` per route (PRESENCE->BOUND and NEXT->BOUND
on ATTEMPT and VM, RETRY->BOUND on VM): the trace build aborts on a read the
graph does not declare (`undeclared-read`, S606), and the self-check on a
read of an unasked (slot, route) or a cycle in the reads. Each read prints
its own trace record, at four site keys that are C5b's declared
multiplicity (`start_table/trace_declared_C5b.txt`); every other record is
identical in order. Re-aims as derived: S269, S274, S276, S441 and S492,
each re-verified by a plant. Corrections, all in the report §4: the reads
G1, F1 and R4 (§1.3's table) are not yet declared in `reads[]` (they predate
the selection read; their own commit can route them through it); the call
graph needed two fixes to see the read at all (a one-line macro's
`#define` line is body, and reaches-seed is a fixpoint once the walk makes
the graph cyclic), both neutral on main.

**C6's and C7's outcome** (lane stc67, `../dev/lanes/stc67_report.md`).
C6 built as listed: every start axis's `--list-axes` rows are
`cand_rows[]`'s rows projected by `list[route]` through ONE accessor,
`pcrec_cand_list_row`, and ONE dump emitter, `emit_cand_axis`; each row's
`desc` sits beside it (`CandRow.desc`, moved verbatim, D-3's stale text
included), the stamp is the row's SLOT's on the listed route
(`cand_list_stamp`) and the value the stamp writer's spelling
(`cand_list_value`); `CandList.fact_deny` carries the FACT deny the listing
shows on the anchored BOUND rows and `window` (§3.7). The self-check holds
every listed row to a `desc` and each listed order to its table position.
The per-axis accessors and `PcrecAxisCand.stamp` are gone. `--list-axes`
byte-identical to main. By the manager's ruling on stc5b §4 item 1, C6 also
routes §1.3's three other reads through `cand_read` and declares each edge
in `cand_nodes[].reads` in the same commit: G1 and R4 read NEXT
(`dfa_cand_scan(cx, reader, …)`, CR_DFA and CR_ATTEMPT), F1 reads PRESENCE
(`req_admit_read`, CR_DFA). The DFA-route reads and F1's print the records
the old selections printed; the ATTEMPT-route read adds one per read (site
`attempt-next`, `start_table/trace_declared_C6.txt`). Zero movers. C7 built as
listed: D-3 corrected and the five start axes that were `predicate` list as
`list`; the 19 moved cells are declared in `start_table/
listing_declared_C7.tsv` and checked by `start_table/listing_diff.py`; spec
hunk `docs/spec/registry.md` §6. Not an abi event (it moves no artifact
byte). Corrections, all in the report §4: §3.5's "accessors kept until C7"
had been overtaken at C5; the C6 row does not name `cand_nodes`, which the
routed reads edit (S606 re-aimed); and §1.1's `stamp` column is the slot's,
not a per-row field.

**Sequencing against the kit's R4c** [Frank 2026-10-06, R-Q5; §6]: R4c (`memfn/docs/requests.md`
R-4, main `05c33ce0`) lands BEFORE C1-C7, and C0 (no `src/`) runs in parallel
with it. The edit set, the anchor census and every `refactor_edit_set.tsv` line
number below were derived on pre-R4c main: C1-C7 RE-DERIVE them (the
instruments re-run) on post-R4c main before the first edit. Once R4c has landed,
a change to a migrated emitter's TEXT is kit work (D146/D147), not this fold's;
the start DECISION reads inside those emitters (the kit's list B1-B18) stay
pcrec-side and ARE this fold's edit set, taken as input from the kit's report.
C0's full I2 (every axis x both comment tiers) is awaited by the kit: ping it
when C0 merges. Serial order of the two decision-family refactors: this fold (A)
first, then [DEC-FALLBACK] (B, whose STEP 0 census runs after C7 merges) [R-Q4].

C5's stamp/listing readers are `line` entries of the edit set since revision
2.1 (`END_WINDOW` `emit_dfa.c:10114`, `VM_START` `emit_vm.c:11558`, and the
`--emit-ir` listing's `st->root_minw` test `emit_vm.c:9492`, which revision 2's
`v->root_minw` line did not match) [r2.1 S-N3]; no current sabotage row
anchors on them, which the derivation now shows rather than assumes.

C3-C5b can be fewer, larger commits if the panel prefers. The split exists so
each re-aimed sabotage row is verified in the commit that moves it, and the
re-aim list per commit is `sabotage_anchors.tsv`'s `commit` column, not prose.

### 3.3 How each commit proves 0 movers

Every commit C1-C6 runs, against its parent (`--ref HEAD~1`, both sides built by
the script from `git archive`):

1. **`emit_sweep.py`, all six streams, `--features all`**, at default: streams 1
   (`.c`, auto), 2 (`.c`, `--engine=vm`), 3 (`--emit-ir`), 4 (composition over
   every `.rxt`/`.rxtin`), 5 (the seven `--list-*` dumps), and C0's stream 6
   (`--emit-facts`, item 3) [r2.1 C-N7: revision 2 said "five" while adding a
   sixth]. Identity required on all six, reach at the floors C0 re-pinned.
2. **The `--extra` arms, each with a DIFFER floor** [r2 checks-M2, sound-m6,
   checks-m5]. An arm that silently drops its flag makes both sides
   byte-identical to the default arm and passes identity, so identity alone
   cannot fail on the arm's own plumbing. Each arm therefore also counts, ON
   EACH SIDE, the patterns whose bytes differ from the same side's default arm,
   and fails below a floor:
   - `-e utf8`: the byte corpus × utf8 (the utf8-NATIVE corpus is already
     swept by stream 4, whose `-e utf8` arm is partial by design: a file that
     declares `encoding byte` refuses, e.g. `compose_encoding_clash.rxtin`).
     DIFFER floors, MEASURED [r2.1 C-M2] (`plain_arms.tsv`, the deny census run
     with `--encoding=utf8` and `-i` as its two "flags"): byte → utf8 moves the
     bytes of **3,188 of 3,221** auto artifacts and **3,189 of 3,222** vm ones,
     plus 74 refusal moves each way counted separately; it moves a START stamp
     on **674** (auto) and **341** (vm). Two floors per arm, because the whole-
     byte count is near-total (the encoding is stamped on every artifact) and so
     catches only a flag dropped outright, while the start-stamp count catches a
     flag that reaches the stamp but not the start decisions.
   - `-i` (caseless is its own start population; per-row `flags`/`encoding`/
     `engine` columns stay stream 4's — 132/635/131 of the 4,606 rows — and the
     note says so rather than claiming them). DIFFER floors, MEASURED [r2.1
     C-M2]: every artifact's bytes move (`rx_info.flags` records the bit), so
     the whole-byte floor is the population itself (3,221 / 3,222 byte, 3,229 /
     3,230 utf8); the start-stamp floor is **1,752 / 1,567** (auto / vm, byte)
     and **1,775 / 1,605** (utf8).
   - **What a dropped `-e utf8` looks like to the deny floors** [r2.1 C-M2]. If
     the `-e utf8` arm's plumbing dropped the flag on BOTH sides, each utf8 deny
     arm would measure the BYTE delta against the BYTE default. Of the 13 auto
     utf8 deny floors, 8 still pass then, because the byte delta is at least
     the utf8 one (`-fno-run-prefilter` 132 vs 3, `-fno-start-set` 136 vs 127,
     `-fno-req-set-lead` 14 vs 8, and `-fno-start-pinned`,
     `-fno-vm-anchor-bound`, `-fno-req-byte`, `-fno-req-run-fold`,
     `-fprefilter-collapse`); 4 fail only because utf8's population happens to
     be the larger (`-fno-offset-skip` 513 vs 604, `-fno-req-handoff` 163 vs
     280, `-fno-hyb-reseed` 403 vs 420, `-fno-req-run` 530 vs 572), which is
     an accident, not a control. The controls that catch it BY DESIGN are the
     asserted 0 for `-fno-end-window` at utf8 (byte reads 288) and the plain
     utf8 arm's own DIFFER floors above.
   - the deny arms (item 4), each with its own DIFFER floor from
     `deny_census.tsv`, and a MANIFEST of named patterns that must differ
     (exact-count floors disarm themselves; a manifest names irreplaceable
     rows). **`-fno-end-window` at utf8 is an asserted EXACT 0** (W1's fact
     declines every non-boundary encoding), not a floor, so the arm cannot read
     as a dead flag.
3. **The `--emit-facts` stream** (C0). The facts listing's `used` column records
   which facts a predicate ASKED, per fact, yes/no. It varies on exactly six
   facts over the corpus [r2 checks-m6] and so watches the rows that read
   them: `start_anchor` (P2, N7, R3, B3/B4), `req_set` (P4), `req_whole_run`
   (P4/P5, K66), `req_run_maxoff` (F1), `kset_walk` (N1-N4), `run_pin` (N1/N2).
   It sees neither order nor count (§1.3). `--emit-facts=byte,utf8` compiles both
   encodings in one call, so this stream needs no `--extra`.
4. **The deny arms**, at C3, C4, C5 and C5b (the commits that rewrite deny
   filtering or route reads): streams 1-2 with `--extra` for each of the 12
   start-family deny bits AND `-fprefilter-collapse` (bit 20, which sets
   `fit.prefilter_collapsed` that F1, P2's VM arm and R1 read; K39's witness is
   no longer the only population) [r2 sound-m4], AND `-fno-length-prune`
   (bit 7) [r2.1 C-N3]: it empties the MRL pruning that `Vm.mrl_win` records,
   and R1 `exact` reads `mrl_win`, so it moves `VM_RESEED` with no route change
   (11 `VM_RESEED` movers in each auto arm of the 1-in-10 sample, 0 under `--engine=vm`). Each arm runs at byte and
   utf8: 28 arms per commit. Each arm is ~2 × 3,600 compiles; measured on this
   Mac the whole deny census (4 base arms × 14 compiles × 3,595 patterns) took
   about 23 minutes at 9 jobs (201,320 compiles); it runs serially and in the background, one heavy run at a
   time (memory `pcrec-box-concurrency`).
   **The other 29 flags** [r2.1 C-N3]. The 13 were a hand choice from the
   start family. A 1-in-10 sample (360 patterns) over every OTHER flag
   `--list-axes` names, in all four base arms (`allflags_sample.tsv`; 43,200
   compiles in 321 s at 6 jobs, so the full sweep is ≈ 54 min at 6 jobs, ≈ 36
   at 9) splits them three ways:
   - **route inputs** (they change `ENGINE`, `VM_PREFILTER` or `DFA_SCAN`, and
     the start rows follow the route): `-fprefilter`, `-fno-prefilter`,
     `-fno-prefilter-collapse`, `-fno-atomic-discharge`, and part of
     `-fno-splice-calls` and `-fno-ctx-node`. The table reads the route, so
     these move rows by moving the table's input;
   - **landmark inputs with no route change**: `-fno-length-prune` (above;
     added to the deny arms), `-fno-ctx-node` (6: `DFA_PREFILTER`/`REQ_WHY`
     on HYB-UNANCH: the context node changes the machine N's predicates
     read), `-fno-splice-calls` (10: `REQ_WHY` on VM-ONLY: splicing changes
     the tree the `req_*` facts read) and `-fno-cls-kit` (1: `REQ_WHY` on
     VM-ONLY under utf8). These move the facts or the machine, never a
     predicate's code, so they are inputs, not table decisions; the refactor
     sweeps them because a fold that mis-reads an input would show there;
   - **no start stamp moves** (the rest; their hidden movers fingerprint to
     their own stamps: `RX_DFA_TABLE`, `RX_RESUME_FRAMES`, `RX_UTF_CHECK`, …).
     Three of them (`-fno-atomic-discharge`, `-fno-scan-edge`,
     `-fno-splice-calls`) first differ at `rx_info`'s `.flags` line, and on
     `(?:\Ga|b)c` (no atomic group, no call) that line is the ONLY one that
     moves: `.flags = 0ULL` → `4096ULL` / `2097152ULL` / `8192ULL`. That is
     the [AXES-DENY-MASK] shape on bits 12 and 13 as well as the survey's 21,
     a cross-note for lane flagbits (filed on the row's addendum).
   The full sweep, all 29 at every pattern, is C0's deliverable; the sample is
   what sized it and what put bit 7 in the arms.
5. **The selection trace** (C1's build), specified [r2 checks-M3, sound-m5],
   and run by C0's trace instrument (the `--trace` stream, the `CFLAGS`
   pass-through in `build_from_rev`, stderr capture, the sweep-side
   pattern-index/arm tags, the diff tool with its multiplicity filter, the
   records floor and the planted swap/reorder control, §3.2 C0) [r2.1 C-N2]:
   - **The record** is `pattern-index, arm, seq, slot, route, row, site` —
     keyed per compile and per pattern, and ORDERED (`seq` is the ask's ordinal
     within the compile). A diff compares each pattern's ordered sequence; a
     corpus-wide multiset would cancel a swap between two patterns.
   - **Printed at the walk's RETURN** (`dfa_select`'s return and
     `vm_plan_reseed`'s chosen row today; `cand_select`'s return after C3), never
     at a reader's use. An inline fallback left behind after C3 (ask, print,
     then ignore the answer) would pass the trace, so the "no reader keeps an
     inline chain" property is a STRUCTURAL check instead: after each commit no
     `token` or `line` of `refactor_edit_set.tsv` assigned to that commit or an
     earlier one survives in `src/` (grep).
   - **The reference is regenerated from the PARENT every commit** (the parent
     built with `-DPCREC_CAND_TRACE` from `git archive`), never recorded once at
     C1: a stored reference goes stale on the first corpus change and teaches the
     reviewer to re-record, which is how a control comes to share a source with
     its subject.
   - **Multiplicity is declared.** No commit may change a pattern's sequence
     except by the additions it declares (C5b: records whose `site` is one of
     its four BOUND readers); the diff filters exactly those and requires the
     rest identical.
   - **The trace build is NEVER the byte-sweep build.** Items 1-4 run on the
     default builds; C1 additionally byte-sweeps the trace build against the
     default build, so a trace that changed emitted bytes is caught.
   - **What it proves for INLINE sites** [r2 sound-m5]: the five inline sites
     (and K65/K66) have no walk today, so which branch prints `B2` or `W1` is
     chosen by the C1 author — the same author whose mapping defines C2's rows.
     For those sites the trace proves only that the print agrees with the
     emitted text; the emitted BYTES (items 1-2) are the control. The trace is
     stronger than bytes only at the walked sites, where it sees a row change
     between two rows whose emitted text coincides (`run-pinned` vs
     `offset-set` on a model that already tests the run).
6. **The independent controls** [r2 checks-M3]:
   - **The C2 both-walks oracle tests only the FILTER** (slot, route mask, deny
     order, first-match), because the old walk and `cand_select` share every
     predicate by pointer. It runs twice, OLD-then-NEW and NEW-then-OLD, because
     a predicate with a side effect (`pcrec_find_byte_rate` records its first
     ask) evaluated by the first walk is cached for the second.
   - **The deny-delta census** is the independent control for row SELECTION:
     it reads only bytes and stamps (no `cand_rows[]`, no trace), so a row whose
     population moves under its own deny flag moves the census (§3.4).
   - **The stamp-vs-text agreements** for rows the census reads two ways: H1
     (`VM_ROOT_MINW` value vs the emitted test), B1/B2 (`start_max`'s literal),
     B3/B4 (`VM_START` vs `attempt_max`).
7. `make test-codegen` (which runs [SABANCHOR], §3.5), the registry suite,
   `run_cand_rows.sh`, the memfn manifest check (C17), `inventory_check.py`
   against a fresh `call_graph.py` (the family changes only by the edit set's
   definitions: C2's new ones in, the deleted ones out), `sabotage_anchors.py` (exit 2 on an unresolved `src/` site),
   `reconcile.py`, `assert_reach.py` where the commit adds an ask (C5b) [r2.1],
   and mech on every re-aimed row of the commit and every re-run row whose
   `rerun_at` names it (§3.5). The full
   `make test` is the manager's at merge.

**The controls and what they share.** The reference side of every byte
comparison is the PARENT commit's binary, built from `git archive`, so it shares
no source with the change under test (learnings §3). The trace's reference is
the parent's trace build. The deny census and the stamp census share no source
with `cand_rows[]` or the trace. None of them reads `cand_rows[]` to decide what
`cand_rows[]` should say.

### 3.4 Rows the corpus cannot prove, and each row's own control [r2 checks-M4]

**The per-row control is the deny-delta count.** For every row with a deny bit,
the number of artifacts that move under that bit (`deny_census.tsv`) is a
byte-observable reach that shares nothing with the code under refactor; it is
pinned per arm as a DIFFER floor plus a named manifest (§3.3 item 2). Measured on
this build (movers / of which no start stamp moved):

| flag | rows it removes | auto/byte | auto/utf8 | vm/byte | vm/utf8 |
|---|---|---|---|---|---|
| `-fno-offset-skip` (16) | N1-N4 | 513 | 604 | 0 | 0 |
| `-fno-run-prefilter` (32) | N1/N2 | 132 | 3 | 0 | 0 |
| `-fno-start-set` (47) | N5-N7 | 136 | 127 | 2,327 | 2,352 |
| `-fno-start-pinned` (22) | S1 | 183 | 183 | 0 | 0 |
| `-fno-req-set-lead` (45) | P4 | 14 (14 hidden) | 8 (8) | 16 (16) | 8 (8) |
| `-fno-req-handoff` (46) | F1 | 163 | 280 | 0 | 0 |
| `-fno-hyb-reseed` (37) | R4/R5 | 403 | 420 | 0 | 0 |
| `-fno-vm-anchor-bound` (28, fact) | B3/B4, P2, N7, R3 | 337 | 337 | 488 | 488 |
| `-fno-end-window` (29, fact) | W1 | 288 | **0 (asserted)** | 288 | **0** |
| `-fno-req-byte` (30, fact) | P*, F1, N1-N4 via the facts | 2,639 (596) | 2,631 (560) | 3,222 (1,179) | 3,230 (1,159) |
| `-fno-req-run` (31, fact) | P*, F1, N1/N2 | 530 (229) | 572 (273) | 530 (513) | 572 (557) |
| `-fno-req-run-fold` (44, fact) | the run's cube positions | 48 (16) | 38 (7) | 48 (31) | 38 (23) |
| `-fprefilter-collapse` (force 20) | F1/P2/R1 conjuncts | 213 (1) | 213 (2) | 0 | 0 |
| `-fno-length-prune` (7) [r2.1 C-N3] | R1 `exact` (via `Vm.mrl_win`) | 46 (35), 1-in-10 sample; the 11 visible all move `VM_RESEED` | 49 (38), sample | 69 (69), sample | 85 (85), sample |

No arm moved a refusal (0 refusal moves in all 52). The auto/byte column
reproduces the checks critic's measured table exactly (513, 136, 14, 163, 183,
403, 337, 288, 48). **Every hidden mover is accounted for by its first differing
line** (`deny_hidden.tsv`), in four classes and nothing else:
- `-fno-req-set-lead`: the pre-check BODY (`if (subject_length <= search_from ||`
  …) — P4 is stampless, so all its movers are hidden; its deny delta is its own
  control (below);
- `-fno-req-run`/`-fno-req-run-fold`/`-fno-req-byte`: the FACT stamps
  `RX_REQ_RUN`/`RX_REQ_BYTE`, which are landmarks, not rows;
- `-fno-req-byte`: `RX_FINDINGS` — the byte-rate prior's ASK disappears with
  the fact, and the stamp records the ask. On a no-landmark pattern
  (`[ab]*c?`) this is the ONLY byte that moves. It is §1.3's side-effect channel
  observed on the corpus (1,179 of 3,222 vm/byte movers);
- `-fprefilter-collapse`: `RX_ENGINE_SEL "collapsed-prefilter"` on 1-2
  artifacts (the one corpus pattern the collapse rung already takes).

So the census found no start decision that moves bytes without a stamp or a
named landmark, beyond P4 (known) and the prior's ask (§1.3).

Read with these caveats:
- Bits 16 and 32 act as a PAIR on N1/N2 (`16|32`), and 16 alone also removes
  N3/N4: read `-fno-offset-skip` (N1-N4) and `-fno-run-prefilter` (N1/N2 only)
  as two deltas, never one.
- P4 (`set-leads`) shares the `"emitted"` stamp with P5, so its stamp count
  cannot separate them; its deny delta (`-fno-req-set-lead`) is its OWN control
  and it is byte-visible. Revision 1's "invisible to every stamp, needs an
  out-of-sweep witness" conflated no-stamp with no-byte.
- R6 (`fixed`) has population 0 at default and 403 (auto/byte) / 420 (auto/utf8) under `-fno-hyb-reseed`,
  COUNTED by the deny arm of the stamp census (`row_census.tsv`), not asserted.
- `-fno-end-window` at utf8 reads 0: the asserted zero of §3.3.

**Rows with no deny bit and a small population have only the stamp and the
corpus**, so each gets a named witness, committed as an `.rxt` cell first so
every sweep sees it [r2 checks-m7], and a planned sabotage row:

| row | population | witness | sabotage (planned; S-id = next free on main at build) |
|---|---|---|---|
| H1 `ceiling` | 6, every arm; read twice (the `VM_ROOT_MINW` value against the constant's spelling AND the emitted `< …_VM_ROOT_MINW) return 0;` test, which shares nothing with `PCREC_MINW_MAX`) [r2 checks-M4 H1] | `tests/mrl/`'s cells + `^((?1)a)$` | exists: S169 (re-aimed at C5) |
| B1 `bot` (ATTEMPT) | 293 (DFA 136 + HYB 157) | `(?m)^` and `^`-led alternations in `tests/assertions/` (`^(a)(b|c)` as a hybrid) | NEW: `start_max` literal `0` → `subject_length` (detectable only by step/attempt-count cells: the answer is unchanged, so the row needs a work-budget `gu` cell or an attempt-count probe; until it has one it ships declared `UNREACHED`) |
| B2 `gstart` (ATTEMPT) | 21 (DFA 16 + HYB 5) | the `\G` blocks of `tests/assertions/`; `(?(DEFINE)(?<g>\Ga))(?&g)(b)` (D-2b) | NEW: `a_bot` read as `a_bot && a_gst` (B2 collapses into B5: same detection caveat) |
| B4 `gstart` (VM) | 5 auto / 20 vm | `tests/assertions/` `\G` blocks | exists through the fact (bit 28 sweep) |
| R4 `adaptive-dense` | 13 | `docs/dev/reseed/`'s cells | exists: S441's family; deny bit 37 |
| P4 `set-leads` | deny delta 14 a/b, 8 a/u | `run_prechecks.sh` §5.11 | exists: S460, S457, S458 |
| P5 vs P4 | stamp shared | the P4 deny delta separates them | — |
| count-collapsed hybrids (F1/P2/R1 conjuncts) | under `-fprefilter-collapse`: 213 movers | the force arm itself | — |

C2 adds, under `PCREC_CAND_TRACE`, a per-row hit counter that `row_census.tsv`
cross-checks against the stamp counts; for P4/P5 and N9/N12 (shared stamps) the
cross-check is against the deny delta and the route-keyed key respectively. A row
whose counter reads 0 across all arms is listed in the commit's report as
UNPROVEN-BY-SWEEP and needs its constructed witness run explicitly (the
[MECH-REACH] shape).

### 3.5 Gates and sabotage rows

**The derivation** [r2 sound-M6, checks-M1; r2.1 C-N1, C-N5, S-N3].
`sabotage_anchors.py` reads every anchor SITE of every row (463 row files /
462 ids, S169 shared by two files; 480 sites: `SAB_FILE` and `SAB_FILE2`, any
target file, including `src/opt/prefix_k.c`), finds its owner by the call
graph's own parse with the total resolution of §2.1 method 3 (0 unresolved
`src/` sites; an unresolved one is a hard error), and classifies it from
`call_graph.txt` and `refactor_edit_set.tsv` alone:
- **100 rows are in the start family** (owner in the derived family or its
  seeds), against revision 2's 95 (which missed S282, S299, S475, S479, S496:
  the owner-`?` sites, C-N1) and revision 1's 53 from a hand list that missed
  `emit_req_set_rest`, `req_run_tests`, `emit_req_run_check`, `unanch_start`,
  `cand_from_live_seeds` and `prefix_k.c` (S187, S188, S277, S278, S316,
  S459), the stamp writers and the VM storage/entry functions.
- **15 are RE-AIMED** (the anchor sits in an edit-set `def`, or its text
  OVERLAPS an occurrence of an edit-set `token` or `line`), each in EVERY
  commit that column names; a row two commits move lists both (S441):

  | commit | rows | why |
  |---|---|---|
  | C3 | S222 | `dfa_search_start_name`'s body reads the deleted walk (in neither of revision 1's lists) |
  | C3 | S283, S284 | `dfa_pfs[]`'s run rows (deny, `reseeds`) |
  | C3 | S490 [r2.1 S-N2] | its anchor is `pf_dfa_start_set`'s route conjunct (`:6656`), one of the fifteen `job->engine` tests that read `cand_route_of`; the EQUIVALENCE argument is re-verified in the same re-aim (sound-n5: its premise moves from "ATTEMPT callers never call `dfa_pf_of`" to "the `routes` column excludes ATTEMPT from N5/N6") |
  | C4 | S462, S473 | `req_admits[]`'s `set-leads` deny; `req_uses[]`'s `handoff` deny |
  | C4 | S518-S521, S527 [stc4] | D148 Q2's `DfaSel` spelling sweep: `req_handoff_applies`' signature |
  | C5 | S169 | the root-minw `if` H1 becomes a row read |
  | C5 | S263 | B3/B4's shared literal moves into `u.bound` (§2.2 wins over revision 1's §3.5) |
  | C5 | S371 | `rs->row->action` → `u.reseed` |
  | C5 | S372, S441 | `vm_plan_reseed`'s calibration swap; `vm_reseed_holds`' `anchored` tag |
  | C5b | S269, S274, S276 | `req_route_one_attempt`'s two arms read BOUND |
  | C5b | S441 [r2.1 S-N3] | R3's predicate line (`emit_vm.c:11090`) reads BOUND: S441 is re-aimed at C5 (the tag switch goes) AND at C5b |
  | C5b | S492 | N7's anchoring conjunct reads BOUND |

  Each re-aim plants the same edit on the same row or read, with intent
  re-verified (BOILERPLATE: "a re-anchor needs its intent re-verified").
- **85 are RE-RUN** (anchors the plan keeps byte-stable), each row's
  `SAB_REACH` probe included — a re-run row whose plant is reached only
  through a walk is reached only if the walk still asks it ([MECH-REACH],
  checks-M1's second class). **Re-run per commit, not once** [r2.1 C-N5]: the
  `rerun_at` column names every commit whose edit set touches the row's OWNER
  definition (its body changes around the unchanged anchor), and the row
  re-runs in that commit: 32 rows (C3: S218, S219, S220, S480, S486-S489,
  S495, and S82/S235 also at C5; C5: S36, S63, S85, S88, S141, S144, S168,
  S181, S224-S226, S264, S370, S400, S422, S430, S469; C5b: S491, S493, S496,
  S497). The other 53 rows' owners no commit touches; they re-run once, as
  one mech sweep after C5b. S495's REACH probe must still find a name read.
- **The duplicate id** [r2.1 S-N3] (RESOLVED 2026-10-07, lane admin1007:
  `S169_root_minw_unchecked.sh` is now `S556_root_minw_unchecked.sh`; the
  id S169 belongs to the older postresolve row alone; the prose below and the
  counts in this document are the revision-2.1 snapshot): `S169_root_minw_unchecked.sh` (H1's row)
  and `S169_postresolve_pass_deleted.sh` ([DD-14.LB]) share `S169`, both
  committed 2026-08-24 by two lanes. Revision 2's "462 rows" counted ids and
  merged them; rows are now keyed by FILE. The fix (renumber one, at the next
  free id on main) is the mech owner's, filed in the re-check record; the
  re-aim at C5 names the FILE, so the shared id cannot misdirect it.

**The per-commit anchor gate already exists.**
`scripts/m6read_check_sab_anchors.py` checks that every row's `SAB_BEFORE`
(and `SAB_BEFORE2`) occurs EXACTLY `SAB_COUNT` (`SAB_COUNT2`) times in its file,
and `make test-codegen` runs it as [SABANCHOR] (`tests/codegen/run_codegen_tests.sh:3421`);
today 463 row files / 480 sites resolve. Revision 1 did not name it and the checks
critic believed no such gate existed. Every commit C3-C5b runs it (§3.3 item 7):
an unplanned re-aim fails there, loudly, before mech — and a planned one is
listed in `sabotage_anchors.tsv` before the commit is written.

**Structural checks that parse the source:**
- `tests/codegen/cand_rows_check.py` reads `static const DfaPf dfa_pfs[] = {`
  literally (`:130`; names regex `\{\s*(?:\.c\s*=\s*)?\{\s*"([^"]+)"`, which
  returns no names from designated initializers) and every `DfaSel NAME = {`
  initializer (`:174`), and its `[cand-route-walk]` check anchors on
  `static const void \*dfa_select\(` (`:177`). All three are re-aimed at C3
  (`static const CandRow cand_rows[] = {`, `.c.name = "…"`, `CandSel`,
  `cand_select(`). Each fails LOUD if left behind (its own K35 guard), so a red
  there at C3 is the planned re-aim, not a regression [r2 checks-m2].
- It gains four checks:
  - every (slot, route) pair a body asks ends in a `cand_always` row;
  - no row's `u` member mismatches its slot, and no row's `hands` type is
    outside its successor's `accepts` — a slot's, or a non-slot successor's
    (the verifier, the loop header, the caller, §1.2 [r2.1 S-N1(e)]) (§1.6);
  - no comparison reads a `cand_rows[]` row NAME: K84's check widened to every
    start row (K89's fix shape). To avoid day-one false positives on names like
    `all`/`exact`/`window`/`fixed` (`src/parse/enabled.c:262` has
    `strcmp(spec, "all")`), the literal half fires only where the other operand
    is a row-name expression (`->c.name`, or a `*_name(` projection call)
    [r2 checks-m1];
  - every `CandSel` initializer names `.slot` and `.route`.
- **Each new check ships with its sabotage row** [r2 checks-m3]: delete a slot's
  last row; initialise a row with another slot's `u` member (and a row whose
  `hands` its successor does not accept); add a
  `strcmp(sel->row->c.name, "exact")`; omit `.slot` from a `CandSel`. Today
  `tests/mech` has one `candrows`-arm row (S495).
- `tests/registry/axes_registry_check.sh` and `run_registry_tests.sh` read
  `pcrec_reseed_rows` by name in comments only. At C6 the projection keeps
  `pcrec_reseed_rows`/`pcrec_reseed_nrows` as accessors until C7. No sabotage
  row anchors in `axes_dump.c` or `AXIS_DESC` (grep, 0), so C6 re-aims none.
  [stc67] Superseded: C5 had already replaced those two with
  `pcrec_reseed_row`, and C6 deleted every per-axis accessor for one
  projection (`pcrec_cand_list_row`). C6 did re-aim one row, S606, because
  it also routed G1/F1/R4 through `cand_read` and so edited `cand_nodes`.
- **Identity gates** (`tests/codegen/run_*_identity.sh`, 11 of them) compare
  emitted artifacts across arms. No emitted byte moves, so none of their pins
  moves. They run unchanged as part of `make test-codegen`.
- **The memfn site manifest (C17).**
  - Its emitter and companion names are all function names the plan keeps:
    `pf_emit_find`, `pf_vm_emit_first_class`, `pcrec_emit_req_byte_check`,
    `emit_req_set_rest`, `emit_attempt` (MLINE).
  - C17_ROW_FLOOR does not move, because no site is added.
  - The row `scan` column (§1.1) names the manifest id, and C17 gains a
    cross-check: every `cand_rows[]` row whose `scan` is a manifest id names an
    id that exists in the manifest.

### 3.6 Stamps whose vocabularies stay byte-identical

Every value set below is untouched through C6. A row's `stamp` projection names
today's token, including where §2.4 says the token is ambiguous. After C5 every
stamp in this table is written from the row the body used (the body and the
stamp read ONE selection), never from the fact directly [r2 sound-m1]:

| stamp | rows that project into it | `rx_info` mirror |
|---|---|---|
| `<PREFIX>_DFA_PREFILTER` | N1-N6, N8-N13 (N12 as `"memchr"`) | `rx_info.prefilter` |
| `<PREFIX>_DFA_PREFILTER_OFFSETS` | N1-N4's offset list | — |
| `<PREFIX>_VM_START_SCAN` | N7, N13 on route VM | — |
| `<PREFIX>_REQ_WHY` | P1-P5 (`req_why_name`: P4 → `"emitted"`) | — |
| `<PREFIX>_REQ_HANDOFF` | F1 (the decimal K), F2 (`"none"`) | — |
| `<PREFIX>_VM_RESEED` | R1-R6 | — |
| `<PREFIX>_VM_START` | B3, B4, B5 (route VM) | — |
| `<PREFIX>_VM_ROOT_MINW` | H1 (the value from `root_minw`) | — |
| `<PREFIX>_DFA_START` | S1, S2 | `rx_info.search_form` |
| `<PREFIX>_END_WINDOW` | W1 (the bound), W2 (`"none"`) | — |
| `<PREFIX>_REQ_BYTE`, `_REQ_RUN` | facts, not rows (read by P/F) | — |

The fact-valued stamps keep `pcrec_fact_stamp`'s spelling (`facts.c`). The
`--emit-ir` listing's `root-minw` row (`vm_render_listing`, `emit_vm.c:9492`)
reads H1 the same way.

### 3.7 Deny flags and the axes

- **No bit is renumbered or reassigned.** Row denies stay on their rows: 16, 32,
  45, 46, 47, 22 and 37.
- **FACT denies stay on their facts** (`facts.def`): 28 `start_anchor`, 29
  `end_window`, 30/31/44 the `req_*` facts. That split is
  `patfacts/design.md` §7.1's, and it is load-bearing:
  - `-fno-vm-anchor-bound` empties the FACT, so it also turns off G2's VM arm
    (P2), the VM hat's anchoring conjunct (N7) and RETRY's `anchored` row (R3),
    not only the BOUND rows. After C5b those three read BOUND, whose B3/B4
    predicates read the emptied fact, so the reach is identical.
  - A refactor that moved bit 28 onto rows B3/B4 would change those three other
    readers before C5b and leave them unchanged after it — a mover either way
    on the arms that set bit 28. The deny arms (§3.3 item 4) are exactly what
    would catch it.
  - The listing keeps showing bit 28 on `vm-anchor-bound`'s rows, as a
    projection.
- **Two rows carry two bits** (N1/N2, `16|32`). `cand_select`'s test is
  `deny & flags`, unchanged, so either bit removes the pair.
- **The `rx_info.flags` mask.** None of the 12 start-family bits enters
  `strategy_denials` on an artifact it cannot act on (probed: on `xyz`, every
  start-family flag except the two that act on it is byte-identical). The two
  unmasked bits the survey found (18 `-fno-size-term`, 21 `-fno-scan-edge`,
  §4.3) are not start-family; [AXES-DENY-MASK] owns them.
- **`test-axes`** enumerates its arms from `--list-axes` (deny and force macros
  and CLI flags). Through C6 that surface is byte-identical, so the axis sweep's
  arm set does not move. At C7 only `kind` and one `desc` change, and no flag
  appears or disappears.
- **No new deny or force flag.** D148 Q3's "deny only" is kept for the new rows
  too (§4).

---

## 4. The new-row sockets

Each is its own abi event AFTER C7, with its own movers census, spec hunk and
sabotage rows. Nothing below is built by the refactor. Each declares its
`hands` type and its edge in §1.6 before it is designed further.

### 4.1 The reverse-walk row (D151; [ENG-TACTICS] re-scoped)

- **Slot NEXT, two rows**, bounded first (`where_to_start.md` §1.4's order):
  - `rev-inner-bounded` (DFA, `views`);
  - `rev-inner` (routes DFA and VM; D124's two hats).

  They go after N11 and before N13. An offset-0 row that applies is already
  scanning a start; the new row beats it only through its admission (G3, F = 2×
  labelled UNMEASURED per D151 Q6) — an admission that competes with
  `prefix_k.c`'s own for the same patterns (§2.2 NEXT) [r2 sound-M3]. On the VM
  route they go after N7.
- **Predicate:** G1 ∧ G2 ∧ G3, each conjunct a separate line with its sabotage
  row from `where_to_start.md` §2.6's mutation table.
- **Mapping:** `EXACTREV`; `hands = CAND`, and on give-up `LOWER` (edge E11).
  **Give-up:** `ONE_WAY` (D151 Q4). **Hat:** DFA: the anchored forward machine
  from `s*` (`anchored_match_unwrapped.md`'s entry). VM: one anchored attempt.
- **Slot FIRST, one row** `handoff-rev`, before F1: the candidate loop's
  give-up hands the current `s*` to the unanchored scan as its startpos
  (`where_to_start.md` §2.7's measured `fallback`), a `LOWER` handoff whose
  termination comes from the type (§1.6). It is the FIRST slot's second
  LOWER-BOUND row, and with it in place §2.4's VM-only "computed and thrown
  away" gap has its row.
- **New fact:** `inner_split` (`facts.def`, E2, `PF_CORE`, owner
  `src/facts/split.c`): the spine index of the chosen landmark, `P`'s byte
  width `[a, b]`, and the G1/G2 bits. G2's alphabet is a new byte-set union over
  `P`'s consuming nodes, not `first_of`. The census's stand-in reader parses only
  85% / 73%, and D151 names that as the revisit trigger.
- **New machinery:** a PREFIX reverse machine, `pcrec_build_nfa` over `P`'s
  sub-tree, reverse and exact. It is the third reverse machine: [OPT-REVEND]'s
  is the whole pattern seeded at `n`, and the shipped reverse pass is the whole
  pattern seeded at the end. Build it once as a parameter of the existing
  builder, never a second builder (`where_to_start.md` §1.3 item 4).
- **memfn:**
  - The landmark scan is a `FIND` over one literal or run, the PRE/OFS kernel
    the kit already plans to own. No new vocabulary.
  - The reverse walk itself is a DFA step loop, which §8.5 marks "never
    delegated" (T8).
  - The verify chain's `VERIFY` of `L` at the hit is VERIFY's existing site.
  - Request one item: a FIND whose handoff RETURNS each hit and resumes at
    `hit + 1` (self-overlap, `where_to_start.md` §2.1). Today's sites resume at
    `hit + |L|` or return once.
- **Gate:** D151 item 2, the `dup-param-detect` hand twin winning the VM cell,
  and the 10.46 re-run of the soundness model.

### 4.2 [ARTREV] I5: the VM word-start filter

- **Not a new row: a CONTEXT COLUMN on N7** (`first-class`, VM route), which
  `generalize.md` I5 §4 already places "on the same table, its own row,
  sequenced after stage 3".
- **The column:** `ctx`, a predicate on the PREVIOUS byte (`\b` at the
  pattern's start: previous ∉ `\w`). The seek then tests the pair
  (`prev`, `cur`) instead of `cur` alone. Row N7's predicate is unchanged.
- **Why a column and not a row:** the population (bench 2, corpus 1) is a
  subset of N7's, and the same row with a narrower test is the general form. A
  separate `first-class-ctx` row would be a second VM-hat row, the parallel
  special case.
- **New fact:** `start_ctx` (E2, `PF_CORE`): the leading context assertion as a
  previous-byte set, or `none`. It is the zero-width information `start_set`
  erases by design (`startset.md` §3.2). It is the VM analogue of the DFA hat's
  re-seed, which reads the same context off the machine.
- **memfn:** a FIND over a TWO-POSITION predicate (`prev ∈ A ∧ cur ∈ B`), which
  is not in the vocabulary today. It is a kit request (the PF site's predicate
  widened), and the kit decides its form.
- **Give-up:** `NEUTRAL` per `generalize.md` I5 §5 (skipped attempts fail at
  their first instruction, before any charge). The row's posture stays
  `ONE_WAY` because the column narrows the same row.
- **The L5 restart** (skip past a failed attempt's dead span) is a separate
  RETRY-slot question and is not part of I5's column.

### 4.3 K90 (and K88): dense starts

- **Two shapes, two slots, no new mechanism.**
  - **K90 L3 / K88 (a hit at the first position):** a peel, "test the current
    position before the first seek". This is a property of the SEEK, i.e. of
    the row's emission, not a new row. N7's `u.pf.emit_vm` and F1's
    `emit_req_handoff` each gain the peel under one shared helper. The two
    witnesses are the same shape (K90: "same family as K88").
  - **K90 L1/L2 (a dense subject):** this is EXACTLY the RETRY slot's question,
    "after a failed attempt, step or re-seek?". Today that slot serves the
    hybrid (re-call the prefilter: edge E7). The fix is to give R4/R5
    (`adaptive-dense`, `adaptive`) the VM-only route, where "re-seed" means
    "re-seek with the VM hat" (edge E12, the same `LOWER` type as E7) and
    "step" means K49's advance alone.
- **The general answer is the existing one:** the gap-armed block rule and its
  calibration rows (`vm_reseed_cal`, frameless/framed) already measure exactly
  this crossover for the hybrid. K90 then adds no mechanism, only a route bit on
  two rows plus a predicate conjunct for the VM-only route (the hat selected
  N7).
- **Owed:** the calibration's regime does not transfer automatically. A seek is
  cheaper than a prefilter call, so the `gap` crossover is re-measured for the
  VM-only route (D149: labelled UNMEASURED until it is). The alpha is K90's
  three cells.
- **Give-up:** `ONE_WAY` already (R4/R5's contract).
- **memfn:** none new.

### 4.4 Where else the table reaches (filed, not designed)

- **[OPT-REVEND]** is a WINDOW-slot row (`EXACTREV` from the subject end). It
  sits before W1, because an exact start beats a window. It shares §4.1's
  reverse builder. Its `hands` is `CAND` where W1's is `LOWER`, which §1.6's
  check would show to WINDOW's successors before it is built.
- **[OPT-A]** is NEXT rows with a multi-literal landmark.
- **[OPT-VMSEED] stage 4** (D148 add. 2 Q-R4: filed, not planned) is a FIRST
  slot row on the VM route.

---

## 5. Standing questions and siblings

### 5.1 The measurement regime: RELEVANT, briefly

The refactor measures no time and claims no speed: it is answer- and
byte-identical by requirement. The populations in §2.2 and the deny deltas in
§3.4 are compile-time COUNTS, regime-free, read from `build/pcrec` at `4743ebb5`
(abi 64, the same `src/` as `74379fe0`) on the Mac. They are corpus counts, not
bench counts, so a different corpus moves them and moves no decision; the
DIFFER floors are re-measured at C0 for that reason. The one timed number, the
deny census's wall time, sizes the gate's cost only. The new rows of §4 each
carry their own regime question:
- §4.1's F (2×, UNMEASURED);
- §4.3's `gap` crossover, re-measured on the VM-only route, which is exactly
  the case where a hybrid-measured number would flip a decision if carried
  over.

### 5.2 The independent control: RELEVANT

See §3.3 items 5-6 and "what they share". In addition:
- The census reads STAMPS and BYTES, never `src/`. Its population is
  `emit_sweep`'s own `enumerate_corpus`, so the census and the gate count the
  same population. That is shared on purpose: it is the population, not the
  expectation.
- The INVENTORY rests on TWO derivations that share no source (a parse of
  `src/`; the compiler's output) and one cross-record (the mech rows, whose
  family membership is TAKEN from the call graph, so they are not a third
  independent vote) [r2.1 S-N4]. The completeness check and `reconcile.py`
  (§2.1) are the comparison among them. The call graph's one hand input (the
  machine-landmark producers) is named in the script.
- The disagreement probe (`anchor_agree.py`) compares two derivations that
  share no code (the machine's `dfa_interior_dead` vs `src/facts/startanch.c`).
- Witness reach: §3.4's UNPROVEN-BY-SWEEP list and the planned B1/B2 rows (which
  ship `UNREACHED` until a work-count cell reaches them) are the [MECH-REACH]
  answer; the re-run rows run with their REACH probes.

### 5.3 What moves when data is regenerated: RELEVANT, nothing for the refactor

The refactor regenerates nothing. Through C6 no emitted byte, no stamp, no pin
and no listing byte moves, and no abi event occurs. C3's `registry.md` hunk is
a sentence about an internal. C7 moves `--list-axes` text only: a
registry-surface change with a `docs/spec/registry.md` hunk, read by
`tests/registry/` (the format readers are found by grep, the `NF != 15`
lesson of `registry_built_status_memo.md`). C7 adds no column, so no
field-count reader moves.

The instruments' own committed outputs (`call_graph.txt`, `sabotage_anchors.tsv`,
`row_census.tsv`, `deny_*.tsv`) move with the tree; they are design evidence
read by no check. At C0, the ones the gate consumes (the DIFFER floors and
manifests) are re-measured and pinned in `emit_sweep.py`, and from then on a
corpus change that moves them is a floor re-pin with a stated reason.

The new rows (§4) are abi events. Two data dependencies arrive with them:
- G3 reads the byte-rate prior, so a regenerated `default_ppm.tsv` moves
  `rev-inner` admissions. That is the same exposure [OPT-REQBYTE] has today.
- K90's re-measured `gap` is a calibration row; changing it moves the adaptive
  text's literals, which `tests/codegen`'s calibration check reads back.

### 5.4 SIBLING-OF-A-FAMILY: which decision families touch the start table

The start table is one member of a family of first-match decisions about a
search. Each sibling below is weighed against the lens "one table per
question" (D124), and against `decision_families_survey.md`'s families 2-4,
which overlap this note:

| sibling | the question | how it touches the start table | keep separate? |
|---|---|---|---|
| ENGINE selection (`select_engine.c` `analyses[]`, `engine-route`) | which execution core runs the match | it decides the ROUTE (`CR_DFA`/`CR_ATTEMPT`/`CR_VM`), which the table reads as a column | **Yes.** It answers a different question with a different contract (D124 item 3: the cores stay distinct). Its input is the AST and build outcomes, not landmarks |
| PREFILTER admission (`fit.prefilter`, `select_engine.c:862`; `prefilter-lang`; `fit_rungs[]`) | does a VM get a DFA in front, and which language | makes the VM route a hybrid: N on the inlined body, RETRY on the VM side. FIRST's handoff reads it (`pcrec_artifact_has_dfa_scan`) | **Yes, for now.** It is a build-time selection with a retry ladder (`compile_driver`'s one recovery point). Folding it in would put a build outcome into a row predicate. **But** it should become a first-match table itself: it is the one family member still a ternary (`:862`). **RULED [Frank 2026-10-06, R-Q4]: folded into [DEC-FALLBACK] (refactor B), not its own row**, §6 Q8 |
| REQ pre-check admission (`req_admits[]`) | — | this note FOLDS it in as PRESENCE, because "no landmark → no candidate" IS a start mapping, and G1 reads NEXT's choice. Keeping it separate would leave a cross-table read as today | **No: folded** |
| The engine-shape prelude (survey family 4: 11 `PCREC_ENG_ATTEMPT` tests, the attempt route bypassing `dfa_pfs[]`) | is there a table walk; which route | its "parallel mechanism for which prefilter" IS N12 and the ATTEMPT route of this table | **No: folded** (N12, `CR_ATTEMPT`, and the route taken from `job->engine`) |
| The landmark pick (survey family 2: six pickers, five tie rules) | which byte at which offset a row scans | the rows read its result; D-4 is its one identity clause with the table | **Yes: a ranking, not a table** (§2.5); [TIE-ALIGN] re-scoped, §6 Q10 |
| The deny-mask family (survey family 3) | which bits a deny flag removes and records | the 12 start bits are masked correctly (§3.7) | **Yes**: [AXES-DENY-MASK] |
| The req FACTS (`req_byte`, `req_run`, `req_run_fold`'s pick) | what is necessary | the landmark column; facts, not rows | **Yes**: facts layer (D120) |
| Position domain (startpos guard, UTF check, K73, K50, K49) | which positions are legal | applies to every row's output and every re-entering `LOWER` | **Yes**: §2.5; its own family, filed as [DEC-POSDOM] [r2.1] |
| Machine-form axes (repr, view, seed, accept, scan edge, scan body, match) | how the verifier is emitted | the re-seed rows read `seed`; the machine census reads RECOVER | **Yes**: they answer "how does a candidate get verified" |
| memfn's `DELEG_SITES` and the SIMD switch | how a delegated scan is spelled | the `scan` column names the site | **Yes**: the kit owns the inside of a site (D146) |

**The forest-for-the-trees check:**
- Every sibling that answers WHERE a match may begin is folded.
- Every sibling that answers WHO runs it, WHETHER a prefilter exists, WHICH BYTE
  a row scans, or HOW a scan or verify is spelled stays its own table or
  ranking, and reaches this table as a route bit, a fact or a site id.
- The one family member that is not yet a first-match table (prefilter
  admission) is not folded here; it is folded into [DEC-FALLBACK], the second
  serial no-mover refactor (§6 Q8, RULED [Frank 2026-10-06, R-Q4]).

---

## 6. Open questions for Frank (restated for revision 2)

- **Q1. Fold now, ahead of `handoff-rev`?** **RULED** [r2.1]: D151
  addendum 1 (Frank, 2026-10-06) — fold FIRST, as a no-mover refactor before
  `handoff-rev` or any other new start row, GATED on this revision clearing
  the short re-check, then C0, then C1-C7. The re-check cleared with listed
  fixes, which revision 2.1 applies. The text below is the question as it
  was put. D151 Q5 ruled "two tables stay
  until the `handoff-rev` row exists", and your 2026-10-06 direction puts the
  no-mover fold first. **(Was: PENDING your ruling.)** The manager recommends **"fold
  first, gated on the revised note clearing a short re-check"**, and this
  revision agrees: the fold is what makes `handoff-rev` (and every §4 row) a
  one-row addition with a declared edge (§1.6); doing it as a no-mover now is
  cheaper than inside a mover later; and revision 2's inventory is now derived
  and checked, which is what the panel said the first one was not. The re-check
  should be the two critics' own findings against §2.1, §1.6 and §3.3-§3.5.
- **Q2. One array with a slot column, or one array per slot sharing the row
  type and walk?** **RULED [Frank 2026-10-06]: ONE single `cand_rows[]` for every slot, each row tagged with a `slot` field, the walk takes a slot; NOT per-slot arrays.** Frank's reason: "otherwise logic is spread around which is the opposite of what we want". (Was: recommend ONE array, unchanged.) The revision adds a
  reason: the typed-handoff check (§1.6) and the selection DAG (§1.3) are
  checks ACROSS slots, and one array is where they read from. Per-slot arrays
  would keep eight tables with a shared type, which is today's structure renamed.
- **Q3. A compile-time selection trace (`-DPCREC_CAND_TRACE`) in `src/`?**
  **RULED [Frank 2026-10-06]: YES, CONDITIONAL on an experiment in C0** (Frank: "test the theory, seems brittle"). (1) DETECTION: planted selection changes on a scratch branch (a row-order swap, a predicate flip, a route mis-key, a row change where the bytes stay identical); record trace-diff vs byte-sweep detection per plant. (2) BRITTLENESS: run the trace across selection-NEUTRAL commits (a rename, a function move, an emitter reformat); any trace diff is a false alarm. (3) BAR: catches every plant with zero false alarms; otherwise the refactor DROPS the trace and relies on bytes + deny-delta counts, and the note says why. (Was: recommend YES,) now with its specification (§3.3 item 5: ordered
  per-pattern records at the walk's return, the parent as reference every
  commit, never the byte-sweep build) and its stated limit (it proves nothing
  at the inline sites that bytes do not).
  **C0 EXPERIMENT RESULT (lane stc0, 2026-10-06; `start_table/trace_experiment.py`
  → `start_table/trace_experiment.tsv`; `../dev/lanes/stc0_report.md` §4): BAR
  MET.** The prototype hook prints at today's walk sites. Population: 3,595
  distinct patterns × streams 1-2. Every reached plant was caught by the trace:
  the row swap (18), both predicate flips (3,642; 48), the route mis-key
  (2,480 against bytes' 2,158) and a bytes-identical row change (the
  scan-state reader built with `.forward = false`: trace 176, bytes 15). The
  rename, the function move and the reformat gave 0 false alarms. Two
  findings set C1's design:
  (1) a `__func__` site field false-alarms on the rename (6,443 sequences),
  so `site` must be a declared literal;
  (2) one selection-neutral change outside the ruled set, a reader asking
  once more, false-alarms the ORDERED compare (6,443 sequences) and is clean
  under the SET compare. The set compare caught every plant at the same count
  as the ordered one, so C1 gates on the set compare (`trace_diff.py
  --unordered`) and reads the ordered compare as a diagnostic.
  One plant, the original run-pinned→offset-set swap at the scan-state reader,
  reached 0 corpus patterns: neither instrument saw it. That is a population
  fact, recorded rather than counted as a catch.
  Scoped to the refactor's life plus a
  permanent home as the per-row hit counter (§3.4). A debug knob, not an axis.
- **Q4. D-1 (the ATTEMPT `memchr` read as a start byte by G1)?** **RULED [Frank 2026-10-06]: fix option (1), G1 declines `EXACTPRED` rows, as its OWN later row after C7, GATED ON MEASURING the 33 artifacts (27 DFA + 6 HYB, auto/byte) FIRST (D77). If restoring the pre-check is slower, the right fix may be a correct dominance argument for predecessor scans instead. Nothing inside the fold.** (Was: recommend, unchanged:) after C7, G1 declines `EXACTPRED` rows (a read of the `map`
  field). It now moves the pre-check emission of every ATTEMPT artifact
  stamping `memchr`, DFA and HYBRID alike (33 (27 DFA + 6 HYBRID) in auto/byte), and only
  where it was elided. Keep the stamp token.
- **Q5. D-2 (`DFA_START "reverse-pass"` on attempt/empty artifacts)?**
  **RULED [Frank 2026-10-06]: option (a), a third value `attempt-start`, a later LOW-priority row, batched with the NEXT abi event (no standalone bump), with the D80 spec hunk fixing `match_api.md#stamp-dfa-start`'s contradiction and a bench adapter note.** (Was: recommend (unchanged)) a third value `attempt-start` for ATTEMPT and empty,
  as its own abi event with the spec hunk correcting `match_api.md#stamp-dfa-start`'s
  contradiction. Low priority: no consumer is known to be misled. The
  alternative is a spec-only fix stating that the value means "not pinned".
- **Q6. D-2b (`start_anchor` blind through a non-recursive call)?**
  **RULED [Frank 2026-10-06]: FILE, don't fix; the D77 trigger is a bench or real-world pattern that pays for the full-position search.** (Was: recommend (unchanged): file, don't fix.) Population 1 in the corpus (and
  its capturing twin, where the split is inside ONE artifact, §2.4). The fact
  change is a VM-route mover with a correctness-neutral gain, so a D77 trigger
  is needed. After C5b it is ONE fact change and every BOUND reader follows.
- **Q7. Where do this note's census scripts live after the refactor?**
  **RULED [Frank 2026-10-06]: as recommended, with conditions:** `call_graph.py` + `inventory.tsv` + `inventory_check.py` go to `tests/codegen/` as a standing check (a new start decision fails `make test-codegen` until dispositioned) WITH its run time MEASURED at landing, its own SABOTAGE row (plant an undispositioned decision, must FAIL), and a ROBUSTNESS verdict on `call_graph.py`'s parse (if not robust enough to gate on, it stays design evidence); `deny_census.py`'s DIFFER counts become C0's `emit_sweep` floors; `row_census.py` goes to `tests/codegen/` as the trace hit-counter's cross-check IF the trace passes Q3's experiment, arms pinned as floors; `sabotage_anchors.py`, `refactor_edit_set.tsv`, `anchor_agree.py` stay as design evidence. (Was: recommend:) `call_graph.py` + `inventory.tsv` + `inventory_check.py` move to
  `tests/codegen/` as a standing check (a new start decision anywhere fails it
  until dispositioned — the general form of "derive the inventory, never
  hand-list it"); `deny_census.py`'s per-flag DIFFER counts become C0's floors
  inside `emit_sweep.py`; `row_census.py` becomes the C2 hit-counter's
  cross-check under `tests/codegen/`, its arms pinned as floors (D110's shape);
  `sabotage_anchors.py` + `refactor_edit_set.tsv` and `anchor_agree.py` stay
  here as design evidence.
- **Q8. Prefilter admission as a first-match table?** It is the sibling still
  spelled as a ternary (`select_engine.c:862`). **RULED [Frank 2026-10-06,
  R-Q4]: folded into [DEC-FALLBACK] (refactor B below), NOT its own row** and
  not part of this refactor (A). Its retry-ladder interaction is
  `compile_driver`'s, outside the start table; B owns it. (Was: recommend file
  as its own no-mover row.)
- **Q9. Panel shape.** **DONE** [r2.1]: the short re-check ran and both
  critics returned "CLEARS with listed fixes"
  (`../dev/reviews/2026-10-06-r2-starttable-recheck.md`). Revision 1 had its light panel (two critics, no blocker,
  ten majors). **Recommend a SHORT RE-CHECK by the same two critics** against
  their own findings (§R), not a new panel: the refactor still changes no
  answer and no byte, and the full bar applies to each §4 row when it lands.
- **Q10 (new). D-4's fix** [r2 sound-M4]. **RULED [Frank 2026-10-06]: YES.** Direction (manager's answer to Frank's question whether it fits [PATFACTS]): YES, as ONE `PF_DERIVED` fact (facts.def: "a function of core facts and the byte-rate"); the run pin already lives in facts (`src/facts/facts.c:265` calls `pcrec_run_pin` with `pcrec_find_byte_rate`), and `prefix_k`'s pick (`src/opt/prefix_k.c`) is the outside re-ranker that creates D-4. STEP 0 (done at ruling time): `prefix_k.c` reads no compile option (no `tune`, no `cx->` option read); its inputs are the byte-rate (through `pcrec_find_set_ppm`, gated in `pcrec_find_byte_rate`) and the `kset_walk` fact, so no option effect needs a deny/input route. Re-check at build if the cost model grows a `--tune` dial: either that effect enters via the fact's deny/input mechanism or that part stays outside facts as policy over the fact-provided ranking. Cross-ref [PATFACTS], [TIE-ALIGN]. (Was: recommend:) re-scope [TIE-ALIGN]
  from "align the tie rules" to "one landmark-candidate ranking with one tie
  rule, read by the run reader, the pin and `prefix_k`", which deletes N1/N2's
  identity clause. It is a form mover (answer-identical), so it is its own abi
  event after C7, gated on D119's bench bar; its census is D-4's utf8 families
  plus the byte-arm `\d\dxyz` shapes. Not part of the fold. **Confirmed a later
  separate row, never folded into A or B (R-Q4 below).**

**Rulings of Frank, 2026-10-06** (answers to the manager's three questions on
decision families, streamlining and memfn sequencing; numbered R-Q3..R-Q5 here
so they do not collide with this note's own Q-numbers above):

- **R-Q3. [DEC-FALLBACK]'s token contract.** **RULED** [Frank 2026-10-06]:
  [DEC-FALLBACK] KEEPS today's tokens (`ENGINE_SEL`, `UNROLL_K_WHY`, the
  `*_LANG_WHY` values, `VM_PREFILTER_WHY`; `match_api.md` §6.3 vocabularies): a
  PURE no-mover. Separating the "name" token from the "why" token is a later,
  separate abi row. (Replaces "manager recommends, Frank to confirm".)
- **R-Q4. Streamlining: two serial no-mover refactors.** **RULED** [Frank
  2026-10-06]. **A** = this note's start-table fold (C0, C1-C7 + C5b,
  `cand_route_of`, the checked handoff graph §1.6). **B** = [DEC-FALLBACK]
  (`fit_rungs[]` + [SEL-1]'s two overflow rungs folded into one table, tokens
  kept per R-Q3), and **B ABSORBS this note's Q8** (the prefilter admission
  ternary, `select_engine.c:862`): Q8 is RULED as folded into [DEC-FALLBACK],
  not its own row. Order: **A first; B's STEP 0 census runs after A's C7
  merges.** The MOVERS are later separate rows and are NEVER folded into A or B:
  Q4 (G1 declines `EXACTPRED`), Q5 (`attempt-start`), Q6 (D-2b), Q10/D-4
  ([TIE-ALIGN]), the position-domain family ([DEC-POSDOM]) and the token
  separation of R-Q3.
- **R-Q5. memfn sequencing.** **RULED** [Frank 2026-10-06]. The kit's R4c
  (`memfn/docs/requests.md` R-4, main `05c33ce0`: the composite PRE site and the
  offset-skip trio's search TEXT move behind memfn, zero movers) lands BEFORE
  C1-C7. C0 (the `emit_sweep` extension, no `src/`) runs IN PARALLEL with R4c.
  C1-C7 RE-DERIVE their edit set (the instruments re-run) on post-R4c main.
  After R4c, edits to migrated emitter text are KIT work (D146/D147); the start
  DECISION reads stay pcrec-side, and the kit is listing 18 such reads (B1-B18)
  inside the migrated emitters, which the fold's edit set takes as INPUT (§3.2).
  The kit awaits C0's full I2 (every axis x both comment tiers): **ping the kit
  when C0 merges.**

---

## 7. The lenses

- **specific vs general:** general. Twelve decision sites become one walk and
  two route-keyed payload columns, K90's fix becomes a route bit on existing
  rows, and every handoff becomes one typed edge rather than a sentence.
- **core vs derived:** the table is derived. It reads facts (core) and the route
  (engine selection), and owns no analysis. The pick inside a row stays core.
- **applicable vs assumption-changing:** applicable. No contract changes: the
  give-up postures and handoff types are written down, not altered.
- **fits the architecture vs refactor:** a refactor, by request, and a no-mover
  one. It completes D148 Q2's rename and D151 Q5's fold.
- **shared question / engine hat (D124):** this is D124 item 1 applied to its
  own example, "where can a match start", with the engine as a route column and
  the prefilter's engine as the route of a hybrid's inlined body.
- **sibling of a family:** §5.4.
