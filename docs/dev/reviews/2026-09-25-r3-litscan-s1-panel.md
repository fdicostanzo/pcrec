# r3 — S1 FULL D6 panel on the [OPT-LITSCAN] S1 design note revision 2 (docs/design/litscan_s1.md @ main 0832bb1e, revision 2 = lane/s1b)

2026-09-25. Per D122 ADDENDUM 4 item 3 ("a change close to the vital
organs" needs a FULL D6 panel — answer soundness, selection/axis semantics,
the hybrid/VM consumer contract — before any build). Three read-only
critics, each a distinct lens named by the addendum:

- **s1crit-sound** (opus): answer soundness.
- **s1crit-axis** (sonnet): selection/axis semantics.
- **s1crit-consumer** (sonnet): the hybrid/VM consumer contract.

All three read `docs/design/litscan_s1.md` (revision 2, option B),
`compare_stack.md`, `docs/dev/decisions.md` D122 + addenda, and — for the
consumer lens — `docs/design/findings/design.md` §6.2a/§6.3; none ran
`make`. Dispositions below are the manager's, applied by lane `s1r3` the
same day as revision 3. The "applied in §" column names the revision-3
section carrying the fix.

**Verdict: no BLOCKING finding. The mechanism holds** — the row pair, the
`OfsTest` derivation, G1's widened conjunct, and the census population are
unchanged in substance. Every finding below is either a correctness/
soundness tightening at the design-note level (nothing built yet), a
sabotage-coverage gap, an open dependency the note must record but not
discharge, or a manager ruling on a question the note itself raised.

## s1crit-sound (opus) — verdict: sound as designed IF row 1 applied; no BLOCKING

Scratch instrument path: `/tmp/s1crit/sound`.

| id | sev | finding | disposition | applied in |
|---|---|---|---|---|
| 1 | SHOULD | §1.4's G1 pseudo-code (`sel = dfa_pf_of(cx,&us)`) drops `dfa_cand_scan_byte`'s `pcrec_artifact_has_dfa_scan` guard and the `ENG_ATTEMPT`/`attempt_cand` arm. With k65fix, `emit_req_set_rest` only runs after `req_admit == EMITTED` (k65fix `emit_dfa.c:891,:901/:917`): a wrong "dominated" on a no-DFA-front route would drop the pick check AND K65's whole-set proof; `unanch_start` would read a never-built `Job.dfa` (`compile.c:1520`) | FIX: §1.4 states `p` computed ONLY under `pcrec_artifact_has_dfa_scan`, with `dfa_cand_scan_byte`'s `ENG_ATTEMPT`/`attempt_cand` arm kept VERBATIM; ADD a structural check: the K65 witness `(x?)([a-z]+)+Z.@\1` must read `RX_REQ_WHY "emitted"` under S1 | §R3-1; §1.4's pseudocode rewritten; §7's stamp obligations |
| 2 | SHOULD | **C2b is REAL**, measured on the (unmerged) k65fix build: `(x?)([a-z]+)+eeeeeeee~#~#~#~#\1` — under `-e byte`, `RX_REQ_RUN "7e237e237e237e23@0"`; under `-e utf8`, `RX_REQ_RUN "6565656565656565@0"`; both `RX_VM_PREFILTER "none"`. On subject `'e'+'a'×36+'~#~#~#~#'`: byte artifact runs to steps exhaustion (~1.97s), utf8 artifact answers `nomatch` (0.00s); same result at 40 a's. K65's own fix (a) does not close it. S1 does not cause it. Couplings: S1's pin + `OfsTest.run_bytes` both read `Job.req_run` (a C2b fix must keep them on the SAME emitted field); step 6 (Q1's conversion) rewrites exactly this loop → step 6 must be SEQUENCED after the C2b fix | FILE as `known_issues.md` K66; state the coupling as an INVARIANT in §1.4/§1.1 (S1's pin and `OfsTest` must read the field any C2b fix reads); SEQUENCE step 6 (§7.2) after (a) GIVEUP1 merged AND (b) a ruling on K66 | §R3-2; `known_issues.md` K66; §7.2 step 6; §8.1a |
| 3 | SHOULD | §3.4/§7.2 step 6's safety bars don't name give-up TRANSITIONS as their own population; before GIVEUP1 (`lane/chkgaps`) lands, `run_axes.sh` counts a one-sided give-up as budget-bound, so a check built against today's `run_axes.sh` cannot see a transition step 6 introduces | Step 6's safety bar gains a NAMED, COUNTED give-up-transition population, with K64/K65/K66 as its give-up cells; sequencing per finding 2 | §7.2 step 6; §R3-3 |
| 4 | NOTE (verified) | step-5's elision cannot flip a give-up: DFA-scan only; the count-collapsed hybrid pin sits on the superset `Job.nfa` (`compile.c:1646-1647`); a run never spans a counted repeat (measured) | record, no change owed | §R3-4/5/6 |
| 5 | NOTE (verified) | `OfsTest`'s widened guard is sound (`prefix_k.c:431-435,:447-453`) | record | §R3-4/5/6 |
| 6 | NOTE (verified) | the head-of-list rows are safe (`emit_dfa.c:4290-4299`; `pcrec_dfa_scan_state_written` at `:5590`) | record | §R3-4/5/6 |
| 7 | NOTE | R4's widening list misses `compile.c:1576`'s `const unsigned pfc_flags = cx.opt->flags;`. Recommend replacing the hand list with the grep recipe `grep -rn 'unsigned .*= .*opt->flags'`. Ordering: `axis_cli_flag`'s `(unsigned)(dm)==deny` with `dm=1ull<<32` truncates to `0`, so `0==deny` reads true for every no-deny candidate — the bit-32 `#define` must NOT land before the widening commit | ADD `compile.c:1576` to the list; REPLACE the list with the grep recipe; STATE the ordering rule explicitly | §7 (R4 widening); §R3-7 |
| 8 | NOTE | sabotage gap: a plant dropping the run-row deny to `PCREC_NO_RUN_PREFILTER` only (the offset-skip half missing) is invisible to `make test-axes` (the surviving bit still denies, so the axis sweep cannot tell which bit did it) | ADD a check: router under `-fno-offset-skip` must stamp `"memchr"` | §7.1 row (k); §R3-8 |
| 9 | NOTE | K64 fix A (G2) sits ahead of G1 in `req_admit` (`emit_dfa.c:5526-5533`) and is untouched by S1; K65's set-rest mechanism (no-DFA-scan route) and S1's elision (DFA-scan route) are disjoint while finding 1's guard is kept | record, no change beyond finding 1's fix | §R3-1; §8.1 |

## s1crit-axis (sonnet) — verdict: no BLOCKING; proceed to build

| id | sev | finding | disposition | applied in |
|---|---|---|---|---|
| F1 | NOTE | R4's 32-bit truncation is REAL, independently confirmed: `dfa_select` (`emit_dfa.c:4291`) takes `unsigned flags`; `dfa_form_derive` (`emit_dfa.c:6494`) copies `cx->opt->flags` into an `unsigned`; `DfaCand.deny`/`PcrecAxisCand.deny` are `unsigned`. Widening to `uint64_t` as commit 1 is correct and necessary | confirm, no change owed beyond §7's widening commit | §7 (unchanged in substance, cross-confirmed) |
| F2 | NOTE | `census_b.py`'s B-predicate matches §1.2's clauses 0-4 line by line (`probe_b_patch.py`); `census_b_summary.txt`'s cross-tabs are consistent with §6.2. A vestigial unused `implies` variable remains in the probe (a revision-1 leftover) | flag for the build lane to delete; not a design-note change | §R3-9 |
| F3 | SHOULD | `tests/codegen/run_scan_edge_census.sh` already reads `"offset-set-bounded"` but is not named in §7's stamp-reader list (only §6.2's prose names it implicitly) | NAME it explicitly in §7's stamp-value-set list (D94 addendum: a reader whose text never cites the value still moves with it) | §7 (stamp value sets); §R3-10 |
| F4 | SHOULD | row (j)'s reachability must be a HARD delivery-bar item (build the check, run it, log the outcome) — not an either/or the build lane can skip without running anything | make row (j) a HARD delivery-bar item; `UNREACHED`-with-derivation stays an allowed OUTCOME of running it (S219 precedent), never a pre-decided choice | §7.1 row (j); §R3-11; §9 item 7 |
| N1 | ruling request | the two-bit deny (§1.2) — ACCEPT as designed, or take an axis-lens alternative? | **ACCEPTED** (D82: deny = a candidate-list filter, already covers an OR'd mask; `PCREC_NO_OFFSET_SKIP`'s byte-for-byte promise, `lib/pcrec.h` ~L365, requires both bits; `dfa_select`'s `deny & flags` needs no change) | §9 item 5; §R3-12 |
| N2 | ruling request | REJECT the `!views` conjunct alternative on clause 3(b); RATIFY R7 (B-bounded's inclusion via list-order correctness, the existing `memchr`/`memchr-bounded` pair's own precedent) | **N2 REJECTED, R7 RATIFIED** as written | §9 item 6; §R3-12 |
| N3 | ruling request | row (j)'s synthetic witness: construct one now, or defer the decision? | **ACCEPTED as F4's upgrade**: resolved as a hard delivery-bar item rather than a pre-decided choice | §9 item 7; §R3-11/12 |

## s1crit-consumer (sonnet) — verdict: no BLOCKING; 2 SHOULD, 2 NOTE, 3 PASS

| id | sev | finding | disposition | applied in |
|---|---|---|---|---|
| 1 | SHOULD | S1 rewrites `req_admit`/G1 (the `p`/`q` widening, `dfa_cand_scan_byte` widened) at the SAME site `[FINDINGS]` B1 migrates (`pcrec_byte_freq_ppm` → `pcrec_find_byte_rate`); neither document names the other; `findings/design.md` §6.2a's C3 row is written against today's "`p==-1` for every offset-set" reading, which S1 revision 2 changes (`litscan_s1.md` §1.4; `findings/design.md` §6.2a C3, §6.3; `emit_dfa.c:5514/5495/5429/5498`). Landing order/rebase owner is unstated | ADD a coordination paragraph, in BOTH `litscan_s1.md` (§1.5) and `findings/design.md` §6.2a: S1 lands first (ahead in the queue); `[FINDINGS]` B1 rebases onto S1's G1 and re-derives §6.2a's C3 row against S1's WIDENED conjunct; S1's own §1.5 states that G1/L4 admission's rate-table dependence is out of S1's must-not-preclude scope, and why | §1.5 (new paragraph); §R3-13; `findings/design.md` §6.2a (companion edit, same change) |
| 2 | SHOULD | §1.5's must-not-preclude list covers L3 (`dfa_pfs[]`/`OfsTest`) only, not L4 admission (`req_admit`/G1); `findings/design.md` §6.2a's own closing paragraph names this residual; S1 should state whether G1 stays out of scope | §1.5 states explicitly that G1/L4 admission's RATE-TABLE dependence is out of scope, and gives the reason (orthogonal axes of one conjunct — S1 changes WHAT is elided, `[FINDINGS]` changes WHETHER a rate table may move that elision) | §1.5; §R3-13 |
| 3 | NOTE | Claim 1 (§1.5) is true OF THE FACT (`o->k[0]` comes from `frontier_union`, `prefix_k.c:416-420`) but `pcrec_prefix_ksets` still requires `k0[256]` and its sole caller `unanch_start` gates on `DFA kind != DFA_PF_NONE` — the claim understates the VMSEED plumbing gap (`prefix_k.c:386-421`) | TIGHTEN claim 1: the fact's DATA is engine-neutral, but its sole PRODUCER (`unanch_start`) is DFA-gated, so the fact is unreachable, not merely unused, on a no-DFA VM route today | §1.5 claim 1 (rewritten); §R3-14 |
| 4 | NOTE | Claim 2 (§1.5): the producer `ofs_test_of(cx, us, pf, t)` takes `UnanchStart` populated from DFA kind/cand/views — VMSEED needs a DFA-shaped `UnanchStart`-LIKE object; consistent with D122 addendum 4 item 2's deferral, but the note should say so precisely | TIGHTEN claim 2 the same way: the STRUCT and the block emitter are DFA-free today, but the only constructor's INPUT (`UnanchStart`) is not, so a VM hook needs either a DFA-free `UnanchStart`-shaped object or a second constructor — neither built here | §1.5 claim 2 (rewritten); §R3-14 |
| 5 | PASS | no parallel mechanism (§R.R1, §1.3) | — | — |
| 6 | PASS | the floating-run conversion is correctly isolated as its own commit/pin (§7.2 step 6, §9, §10) | — | — |
| 7 | PASS | no conflict with S2/S4 (§1.6, §8.3; `compare_stack.md` §5, §6.1) | — | — |

## Manager rulings (beyond the axis critic's own N1-N3, above)

- **N1 (two-bit deny): ACCEPTED.** See s1crit-axis N1.
- **N2 (`!views` alternative): REJECTED. R7 RATIFIED.** See s1crit-axis N2.
- **N3 (row (j) reachability): resolved as a HARD delivery-bar item**,
  folding s1crit-axis's F4 and N3 into one disposition (they asked the same
  question from two directions).
- **K66 is FILED, not fixed, in this revision.** Its fix shape (three
  candidates) is Frank's, per K65's own precedent (a fix candidate is
  proposed, not chosen, by the lane that finds the sibling defect).
- **Step 6 (Q1's conversion) is SEQUENCED after two externals** neither of
  which this revision discharges: GIVEUP1 merging (`lane/chkgaps`) and a
  ruling on K66. This is a recorded DEPENDENCY, not a re-opening of Frank's
  Q1 ruling itself (Q1 stays RULED: convert, as S1's last commit, in the
  same abi event — only WHEN moves).

## Triage summary

Nine findings from `s1crit-sound` (one correctness-shaped SHOULD on the
G1 pseudocode's guard, one SHOULD that files a new known-issue (K66) and
states its coupling to S1 as an invariant, one SHOULD on step 6's safety
bar, three verified NOTEs requiring no change, one NOTE correcting the R4
widening list plus its ordering rule, one NOTE adding a sabotage row, one
NOTE recording a disjointness confirmation); seven findings from
`s1crit-axis` (two confirming NOTEs, two SHOULDs on the stamp-reader list
and row (j)'s delivery bar, three ruling requests all resolved this
session); seven findings from `s1crit-consumer` (two SHOULDs producing a
coordination paragraph with `[FINDINGS]` and a scope-boundary statement,
two NOTEs tightening §1.5's two claims, three PASSes). **No finding
refutes S1's central mechanism** (the row pair, the `OfsTest` derivation,
G1's widened conjunct) **or its acceptance targets** (§5). All dispositions
are applied in `docs/design/litscan_s1.md` revision 3 (lane `s1r3`, same
day) — see that document's §R3 for the change-by-change record. Two items
are recorded as OPEN and not discharged by this revision: K66's fix shape
(Frank's), and step 6's sequencing dependency on GIVEUP1/K66 (a fact about
the build order, owed to whichever lane executes §7.2).
