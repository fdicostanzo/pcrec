# r26z1 — R-26.1-R-26.5 (kit_proof Z1) at zero artifact movers

Lane r26z1, 2026-10-21. Branch `lane/memfn-r26z1` cut from the kit branch
`lane/memfn-r26` @ `cc4f87ad3` (main `d970abbbc` + the kit's ack). Request:
`memfn/docs/requests.md` "## R-26", items R-26.1 to R-26.5. Design:
`docs/design/kit_proof.md` rev 2.1 §3.4-§3.6, §4.1-§4.3, §6, §7 (Z1). Frank's
build go: 2026-10-21 ("both you and kit please proceed", quoted in the request).

**Verdict: Z1 BUILT. One MF_SITE_ABI event (17 -> 18), MF_CLASS_V 4 -> 5, no
MF_VOCAB move, no pcrec abi bump (stays 81). Zero artifact movers MEASURED on
the plain and rwquest arms; the other seven arms and `make test` are OWED in
the queued job `500-kit-r26z1-heavy` (§6).**

## 0. Questions and findings for the kit manager (none blocks Z1)

None of these stopped the build. Each records a choice I made where the text
left room, or something the build found. Please rule on Q1-Q4 or confirm.

- **Q1 (numbering).** The request and kit_proof.md §4.2 say "MF_CLASS_V 4".
  B3b already took 4 (`pres_row`/`pres_led`, inside MF_SITE_ABI 17), so
  `proven[]` makes it **5**. memfn.h records the history.
- **Q2 (span 0's class is required, not optional).** The request refuses an
  UNSTATED `prefix_stated` on a BOUNDED span 0. If `span_class` itself could
  be left UNSTATED on a forward FIND, a builder that forgot both facts would be
  accepted silently. That is the bug class the brief names. So **a forward
  FIND's `pred` must state BOUNDED or CONTEXT, and UNSTATED is refused**
  (`window_stated`'s rule, applied to the class). CONTEXT is allowed only on a
  context stop, where every term reads below the candidate.
- **Q3 (REPORT needs span 0).** A REPORT site with no BOUNDED span 0 is
  refused ("a REPORT site reports span 0's candidate"). This rule is
  restrictive only. The request's REQUIRED-all rule presumes span 0 exists.
- **Q4 (MF_FLOOR_LO widened).** kit_proof §3.5 refuses LO together with a
  CONTEXT term below the origin. A span-0 term below the origin (a BOUNDED span
  with a negative offset, which the vocabulary allows) is the same case: the
  byte exists and may not be read. So LO is refused with **any** term below the
  origin. Under LO, then, no row reads below its candidate, and every row
  serves every `read_floor` value.
- **F-1 (BOUNDED was never stated).** kit_proof §4.1 says "BOUNDED on span 0 is
  R17-b′ B3b's statement". As built, B3b states no class on `pred` at all:
  `pres_pred_clear` refused any `span_class` there. **Z1 is where span 0's
  class is first stated** (pcrec: PF and OFS BOUNDED, MLINE CONTEXT). The
  `fd_rows[]` decisions read term offsets, not the class, so nothing moved.
- **F-2 (the class space is full).** `fields.def` already had 64 classes
  (kit.h's `_Static_assert`). The seven new fields read through classes that
  already exist, each named in its doc: `ctx` uses NONE/BACK/NONNEG, `absent`
  and `consumable` use YES/NO as bit sets, `read_floor` uses ZERO/OTHER, and
  the lengths use ZERO/ONE/MANY. With seven new fields the **field** space is
  now full too (64). `kind_cl` maps REPORT to OTHER, which is in no row's
  kinds, so the gate declines every finder row on a REPORT site. **R-26.6's
  REPORT row needs a class of its own, so it must widen the mask first** (or
  free a class). That is OWED to Zk.
- **F-3 (a wider SATISFIES item proves only its outermost position).** Found
  by the generated family (proof_run's PROOF check, site 2: `(?<!ab)`-shaped
  RUN at -2 under SATISFIES, subject "cb" from 1). Under R-26.2 an ITEM holds
  wherever SOME read of it lies outside the subject. So at `c = 1` the byte at
  -1 is unconstrained, and `proven[-1]` may not claim the item's set there.
  - `kit_class` therefore proves, for a SATISFIES item: its lowest offset when
    it lies below the candidate, its highest when it lies after span 0, and
    nothing when it straddles (`pred_proves`, compose.c).
  - kit_proof §4.2's "position-wise, the proven positions are a SUPERSET of the
    REQUIRED ones" holds for width-1 SATISFIES items only.
  - Stage 1's machine reading sends width-1 items only (kit_proof §3.3), so
    B1's population is unaffected.
  - The design text is the manager's to amend. I did not edit kit_proof.md.
- **F-4 (consumer's zero is RESULT).** `mf_consumer`'s zero is `MF_C_RESULT`.
  A REPORT site that never writes `consumer` therefore reads as RESULT, which
  is the pattern §4's attack (a) warns about. The request keeps the enum
  unchanged, so I left it and noted it in memfn.h. Renumbering it with an
  UNSTATED zero would be its own MF_SITE_ABI event.
- **F-5 (pre-existing, recorded).** A routed finder row whose pick does not
  serve a site REFUSES it; nothing falls back (`select_arm`, B2's rule). The
  generated family therefore avoids D1's one-byte shape without pcrec's table
  hooks. That is not an R-26 defect.

## 1. What was built, per item

**R-26.1 (span 0's prefix facts).**
- New fields: `mf_pred.prefix_stated` (`mf_prefix`, an UNSTATED zero),
  `exact_len` and `consumable_len`, appended last.
- `kit_proof_check` (compose.c, inside `site_check`) refuses:
  - `prefix_stated` UNSTATED or out of enum on a forward FIND's BOUNDED
    `pred`;
  - `exact_len` > MF_MAX_SPAN_POS, and `exact_len` over a position no term
    sends ("[0, L) are all SENT");
  - `consumable_len` > `exact_len`;
  - any of the three stated on any other predicate (a context stop, a `ctx`
    entry, a `pspans` or `preds[]` entry).
- pcrec: `pcrec_memfn_span0_today` states BOUNDED / STATED / 0 / 0 on PF
  (`find_site`) and OFS (`ofs_site_define`), and carries the
  `_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_MAX_SPAN_POS)`.

**R-26.2 (context spans, absent, consumable, read floor).**
- New fields: `mf_pred.absent` (`mf_absent`) and `consumable`
  (`mf_consumable`); `mf_site.read_floor` (`mf_read_floor`) and `ctx`/`nctx`,
  all appended last.
- Refusals:
  - `absent` or `consumable` UNSTATED on a CONTEXT predicate, or nonzero on any
    other;
  - a `ctx` entry that is not CONTEXT, states a window, plan or presence fact,
    has a non-SET/RUN term, or has a term outside
    `[-MF_MAX_BACK, 0) ∪ [k, k + MF_MAX_AHEAD)`;
  - `nctx` > MF_MAX_CTX, or `nctx` and `ctx` disagreeing;
  - `ctx` on a site with no BOUNDED span 0 reaching past its candidate;
  - `read_floor` UNSTATED under a CONTEXT term below the origin, LO with any
    term below it, or out of enum.
- Binding and completeness read `absent`. The **generic row** is the only row
  that tests `ctx` entries and renders SATISFIES (`ctx_pred_test`,
  `site_test`), and its text for a site with neither is unchanged. Every other
  row, and every finder row, serves `ctx` NONE and `absent` NO (FAILS) only
  (`MF_SERVES_PROOF_TODAY`), so they decline a site stating either.
- pcrec: `pcrec_memfn_context_stop` gives MLINE's stop CONTEXT / FAILS / NO and
  `read_floor` SUBJECT.

**R-26.3 (REPORT).**
- `MF_SK_REPORT` is in the enum. `kit_proof_check` refuses a REPORT site
  unless all of these hold:
  - `consumer` is MF_C_RESULT;
  - span 0 is BOUNDED (Q3);
  - span 0 and every term are REQUIRED;
  - every context item and term is REQUIRED.
- A well-formed REPORT site is refused at selection. `select_arm` admits REPORT
  only through a routed finder row, `kind_cl(REPORT)` is in no row's kinds, and
  the refusal text is "no row serves `site_kind` REPORT". That is the
  request's "refused before R-26.6; admitted wherever a REPORT row exists".

**R-26.4 (the per-offset proof).**
- `mf_class.proven[MF_MAX_FWD - MF_PROOF_LO][32]` is appended last
  (MF_CLASS_V 5).
- `kit_class` builds it per TESTED term and position (`term_prove`), for span 0
  (or the stop) and every `ctx` entry, with F-3's rule (`pred_proves`).
- `proven0` and `proven_prev` are COPIED from `proven[0]` and `proven[-1]`.
- The MF_TRACE re-ask checks Q-R17P-25 at every offset (exists 0 proves
  nothing) and checks the two copies.

**R-26.5 (declarations).**
- `MF_MAX_SPAN_POS` = MF_MAX_TERM (derived).
- `MF_MAX_AHEAD` 1: CHOSEN under D77, labelled with its trigger (a declined
  site, counted at Z2 or later, whose after-context is wider than 1).
- `MF_MAX_CTX` 2: derived from stage 1's source, with trigger UL-8.
- `MF_PROOF_LO` = -MF_MAX_BACK, and `MF_MAX_FWD` = MF_MAX_SPAN_POS +
  MF_MAX_AHEAD.

**Spec hunks.** kit_proof §6.2: "Z1: none for callers. The kit's memfn.h
comments are the contract text." None were owed, and none were written. The
§6.2 sibling design edits (`window_contract.md` §2.2-§2.4) are not step-tagged
to Z1, so they are left for the step that consumes them.

## 2. Readers, re-derived by grep at the build commit

- **The number (MF_SITE_ABI 17 -> 18).**
  - `memfn/include/memfn.h` (the define and its history);
  - `memfn/include/CLAUDE.md` ("carries MF_SITE_ABI 18" and its history);
  - `memfn/CLAUDE.md`, `memfn/src/CLAUDE.md`, `src/gen/CLAUDE.md` (history
    entries).
  - Every code and test reader uses the symbol, not the literal:
    `src/gen/memfn_sites.c`, `emit_dfa.c`, `arm_fixtures.c`, `proven_check.c`,
    `prov_check.c`, `g2_gen.c`, `g2_simd_gen.c`, `formhash.c`.
  - `git grep` of `MF_SITE_ABI[^0-9]{0,3}17` finds only HISTORY sentences
    ("MF_SITE_ABI 17, R17-b' B3b"), and those stay.
  - **Not edited:** `memfn/docs/wake.md:41` ("`MF_SITE_ABI` 17, ...
    `MF_CLASS_V` 4"). It is the kit session's orientation file, so it is the
    kit manager's to rewrite.
- **The class (MF_CLASS_V 4 -> 5):** `memfn.h` (the define, `mf_class`) and
  `compose.c` (`kit_class`, the presence ask's init, the trace re-ask).
  `arm_fixtures.c:371` compares with the symbol. pcrec's
  `emit_dfa.c:cand_class_eq` compares only `exists`/`proven0`/`proven_prev`,
  which are unchanged.
- **The new fields (K96, per field: class and serves):**
  - `fields.def`: 7 `MF_FIELD` rows (prefix_stated, exact_len, consumable_len,
    ctx, absent, consumable, read_floor);
  - `gate.c`: the `cl_*` classifiers and `class_set_of`'s bit sets;
  - `kit.h`: `MF_SERVES_PROOF_ANY`/`_TODAY` inside `MF_SERVES_WINDOW_TODAY`,
    which carries it to every `[FLD_x] =` contract table that uses it:
    `ofsskip.c` (`ofsskip_ct`, `fn_pair_ct`, `fn_memchr_ct`), `pffind.c`,
    `precheck.c`, `runcmp.c`, `vrun.c`, `mismatch.c`;
  - `generic.c` (its own MF_ANY entries);
  - `finder.c` (`FD_SERVES_REST`, and `kind_cl`'s REPORT case at its
    `[FLD_site_kind]` gate);
  - `formhash.c` (the canonical site states span 0).
- **G2:** `memfn/tests/g2/g2_gen.c`, `g2_simd_gen.c` (`g2_span0` in `g2_win`).
- **Fixtures:** `tests/memfn/arm_fixtures.c` (`fx_span0` in `fx_win` and
  `seq_case`), `tests/memfn/proven_check.c` (C3's site).
- **Mech anchors:** SABANCHOR (847 rows) found **S1083** stale, because
  `kit_class` was rewritten.
  - Re-anchored on the `proven_prev` copy with the same intent: all ones,
    proves nothing below the candidate.
  - Detection re-verified by hand: the planted build gives `(?m)^\n` →
    `RX_REQ_WHY "emitted"`, against `"dominated"` unplanted.
  - All 847 anchors now resolve.
- **The suites that count:** registry, codegen and rxtsource. See §5 for what
  I ran (codegen) and the OWED `make test`.

## 3. The checks (`tests/memfn/run_proof.sh`, part `proof` of `make test-memfn-finder`)

Each check runs against a source the subject does not share.

- **A, refusal fixtures (proof_check.c).** 58 cases: 7 ACCEPT controls and 51
  REFUSE cases. Each refusal is held to the field it names in backquotes, and
  `mf_ask` must refuse it too.
  - UNSTATED cases: `prefix_stated`, `span_class`, `absent` on a context stop
    and on a `ctx` entry ("UNSTATED absent read as 0"), `consumable` on both,
    and `read_floor` under a stop and under a before-item.
  - Ranges: `exact_len`, `consumable_len`, `nctx`, `ctx` ranges.
  - LO under a context term and under a span-0 term below the origin.
  - REPORT: `consumer`, an OPTIONAL term, an OPTIONAL item, no span 0, and
    well-formed but no row.
- **B, the class.** `proven[d]` at -8, -3, -2, -1, 0, 1, 2, 3, 4 and
  MF_MAX_FWD-1 on a site with a RUN span 0, an OPTIONAL term after it, a
  SATISFIES item at -2 and a FAILS item at 3. Expected sets are member
  strings. Also the copies, the version, and the context stop's `proven[-1]`
  and `proven_prev`.
- **C, C-PROOF and the generated family.**
  - 400 seeded sites: 100 span 0 + 0..2 context items under either `absent`
    with OPTIONAL items, 100 span 0, 100 context stops, and 100 FUNC (generic
    and offset-skip shapes).
  - Forms reached: generic 353, ofsskip 47 (floor 2 forms).
  - Each site's class is asked at SIMD-off, -fmemfn-simd,
    `--memfn=no-vrun-w32` and `no-vrun-w16`, and must be EQUAL at every
    offset.
- **proof_run.c, the byte-loop oracle.** It includes no kit header; its input
  is G2's own generated facts plus the kit's class (the claim).
  - Each site is run over every subject of length 0..4 on its alphabet and 120
    sampled to length 7, from every `lo`, through EVERY candidate.
  - Per-call checks: BIND, PROOF (including negative offsets, offsets after
    the span, and the absent rule), EXACT, and COMPL (obligation 1).
  - Per-site checks: the binding subset and the superset (F-3's scope).
  - K35 floors on the cells R-26.2 names. Measured: SATISFIES yielded before
    span 0 (c = 0) 229,721, after it (c + k = n) 29,990; FAILS refused before
    164,597, after 25,605 (floor 100 each).
  - Size: 4,049,892 calls, 855,524 candidates.
- **Traced.** The same against the kit compiled with -DMF_TRACE. Every define
  re-asks its class and checks every offset and the copies.

**Verdicts (light, run directly, at 4 cores or fewer).**

| check | result |
|---|---|
| `make strict` | clean |
| `make test-memfn-finder` (with part proof) | 1,955 passed / 0 failed |
| `make test-memfn-arms` | 383 / 0 (no arm pin moved) |
| `make test-memfn-g2` (quick tier) | 71,217,801 / 0 |
| `make test-memfn-rows` | 244 / 0 |
| `make test-memfn-forms` | 5 / 0 |
| `make test-memfn-deleg` | 14 / 0 |
| `make test-memfn-manifest` | 13 / 0 |
| `make test-memfn-link` | 8 / 0 |
| `make test-memfn-stamps` | 25 / 0 |
| `make test-memfn-reach` | 4 / 0 |
| `make test-memfn-arch` | 15 / 0 |
| `make test-memfn-rank` | 15 / 0 |
| `make test-memfn-guarded` | 10 / 0 |
| `make test-memfn-simdfloor` | 51 / 0 |
| `make test-codegen` | red on SABANCHOR (S1083) only. Fixed in 2077c4f54. Re-run GREEN: 16/16 scripts, no `*** [...test-codegen]` line (§5) |
| emit_sweep plain arm vs cc4f87ad3 (+dumps; 5,811 argv, 387 composition) | 11/11 streams movers=0 asymmetric=0 (`build/r26/sweep/plain.log`) |
| emit_sweep rwquest arm (172 patterns) | 6/6 streams movers=0 |

**The plants (S1221-S1226, the ids main reserved).** Each one was applied to a
COPY of memfn/src by `run_proof.sh --plant ID` (`build/r26/plants.log`). The
unplanted run is green (930 / 0). Each plant goes red:

| id | plant | red where |
|---|---|---|
| S1221 | the class proves one position past each RUN term (an untested offset) | B proven[0]; proof_run PROOF/EXACT (29,953 fails) |
| S1222 | SATISFIES rendered as FAILS (a candidate dropped) | proof_run EXACT, e.g. site 0 lo 0 "ab" (196,465) |
| S1223 | every context item rendered SATISFIES (a FAILS candidate yielded) | proof_run EXACT, e.g. site 0 lo 0 "b" (146,398) |
| S1224 | a proof bit only when the policy allows SIMD | C-PROOF on 101 sites |
| S1225 | an OPTIONAL SET term tests one member fewer (over-filter) | proof_run EXACT/COMPL (14,506) |
| S1226 | `absent` UNSTATED accepted (read as FAILS) | A: the two "UNSTATED absent read as 0" refusals |

## 4. Proposed kit-side sabotage anchors (ids reserved by main: S1221-S1226)

These are listed as PROPOSED. I did not add ledger rows: BOILERPLATE's mech
section does not say that lanes add rows for reserved ids. The texts are
`run_proof.sh`'s plant table (FILE@@FROM@@TO).
- **Detector:** `make test-memfn-finder` (mech arm `memfnfinder`, part
  `proof`).
- **Expected:** DETECTED for every row.
- **Reach:** every row is reached by the family's own populations (the floors
  above).

| id | SAB_FILE | SAB_BEFORE (once) | SAB_AFTER |
|---|---|---|---|
| S1221 | memfn/src/compose.c | `long d = (long)t->offset + j;` | `long d = (long)t->offset + j + (t->kind == MF_T_RUN);` |
| S1222 | memfn/src/generic.c | `if (p->span_class != MF_SPAN_CONTEXT \|\| p->absent != MF_ABSENT_SATISFIES)` | `if (1)` |
| S1223 | memfn/src/generic.c | (the same line) | `if (p->span_class != MF_SPAN_CONTEXT)` |
| S1224 | memfn/src/compose.c | `    /* proven0 and proven_prev are COPIES` | `    if (!(s->policy & MF_P_PORTABLE_ONLY)) out->proven[0 - MF_PROOF_LO][0] &= 0xFE;` + the line |
| S1225 | memfn/src/generic.c | `if (member_test(rc, b, tm, id, bx)) {` inside the SET branch | narrow an OPTIONAL term's set by its lowest member first (run_proof.sh S1225) |
| S1226 | memfn/src/compose.c | `    if (p->absent == MF_ABSENT_UNSTATED)` | `    if (0)` |

## 5. Re-runs at the tip

`make test-codegen` after the S1083 re-anchor (`build/r26/codegen2.log`) is
GREEN: `run_group: 16/16 scripts passed`, rc 0, and the grep for make's
`*** [...test-codegen]` line returns nothing.

## 6. OWED heavy validation (queued, not waited on)

- **Job:** `500-kit-r26z1-heavy` (kit band). Its source is
  `build/r26/heavy/500-kit-r26z1-heavy`, and its dry run is clean.
- **What it runs:**
  - `make -j16`;
  - emit_sweep's nine arms against base `cc4f87ad3`: plain (+dumps), simd,
    comments, utf8, vm, start (each against the reference binary
    `build/r26/sweep/pcrec.ref`), rwquest (`build/r26/rwquest_patterns.txt`),
    then variant (`--variant all`) and trace (`--trace`), both
    `--ref cc4f87ad3 --tree-rev 2077c4f54`;
  - then `scripts/perfrun --label r26z1 -- build/r26/heavy/maketest.make.log`.
- **Logs:**
  - one per step: `build/r26/heavy/<step>.log`;
  - the job log: `worktrees/.boxqueue/{done,failed}/<TS>-500-kit-r26z1-heavy/job.log`.
- **Completion:**
  - the job ends `== r26z1 heavy: 0 step(s) failed`;
  - its population is `sweeps=9` lines of `emit_sweep: DONE rc=0`;
  - make's verdict is `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'
    build/r26/heavy/maketest.make.log` (empty = green), read with its
    `.perfrun` note.
- **Expected:**
  - zero movers on every stream of every arm. Any mover means this is not Z1:
    stop, it is a byte event;
  - `make test` green.
- `--arms start` may again show R-25's pre-existing manifest miss (`a.{1,5}z`
  not in the population, b3b's DIFFER_PINS row). That would be a known rc 1,
  not a mover.

## 7. Charter vs committed

| promise | artifact | state |
|---|---|---|
| R-26.1 prefix facts on a BOUNDED span 0, UNSTATED refused, 0 elsewhere, consumable_len <= exact_len | memfn.h `mf_prefix`/fields; compose.c `kit_proof_check` | done |
| one MF_SITE_ABI event, readers by grep | 17 -> 18; §2 | done |
| pcrec states STATED / 0 / 0 on every site | `pcrec_memfn_span0_today` (PF, OFS) | done |
| zero movers on every emit_sweep arm | plain + rwquest measured 0 | **OWED** (7 arms): job 500-kit-r26z1-heavy, owner kit manager, trigger: the job's end |
| R-26.2 ctx[]/nctx, absent/consumable, offsets/ranges, MF_MAX_CTX, no-span-0 refusal | memfn.h; compose.c; generic.c renders them | done |
| MLINE's stop CONTEXT / FAILS / NO | `pcrec_memfn_context_stop` | done (read_floor SUBJECT too) |
| completeness/binding read absent | generic.c `ctx_pred_test`; checked by proof_run | done |
| read_floor enum, LO + below-origin CONTEXT refused | compose.c (widened, Q4) | done |
| G2 fixture per absent value at c = 0 and c + k = n, completeness by the byte-loop oracle | proof_run floors (§3) | done, as a G2-shaped family in `tests/memfn/` (NOT D27-blinded; it can move under `memfn/tests/` if the kit prefers) |
| refusal fixture per UNSTATED field incl. "UNSTATED absent read as 0" | proof_check family A | done |
| R-26.3 MF_SK_REPORT, consumer RESULT, REQUIRED-all, no row serves it | compose.c, finder.c `kind_cl`, `select_arm` | done |
| OPTIONAL-on-REPORT refusal fixture | family A (term and item) | done |
| host equality check C14 | — | not Z1 (pcrec's, at Z2/B1) |
| R-26.4 mf_class.proven[], copies, MF_CLASS_V | compose.c `kit_class`; MF_CLASS_V **5** (Q1) | done |
| proven[] holds at every candidate incl. negative, after-span, absent rule | proof_run PROOF | done (F-3 found and fixed) |
| COMPLETENESS with an over-filter plant | proof_run COMPL/EXACT; S1225 red | done |
| C-PROOF across SIMD off and every live level | family C (4 variants); S1224 red | done |
| Q-R17P-25 trace check at every d | compose.c MF_TRACE block; run traced | done |
| R-26.5 declarations, each derived or labelled with its trigger | memfn.h | done |
| six kit-side sabotage rows, PROPOSED | §4 (S1221-S1226), plants red | done (ledger rows: manager's) |
| docs/spec hunk | none owed at Z1 (§6.2) | n/a |
| per-directory CLAUDE.md | memfn/, memfn/include, memfn/src, memfn/tests, src/gen, tests/memfn | done |
| REPORT row, mf_preview | — | NOT Z1 (R-26.6, Zk); Zk must widen the class mask (F-2) |

## 8. State at handoff

- Branch `lane/memfn-r26z1`; tip in the handback message.
- Rulings file: last entry applied is "main merged lane/memfn-b4 (4c46ddcba);
  do not merge main", together with the S1221-S1226 reservation.
- Not merged anywhere.
- Scratch, gitignored: `build/r26/` (reference build, sweep logs, plants
  log, heavy job dir).
