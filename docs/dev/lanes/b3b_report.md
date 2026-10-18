# Lane b3b — R17-b′ B3b, the PRES rows and D2 routed (2026-10-18)

Lane b3b (opus), kit session, branch `lane/memfn-b3b` from c88537116 (main after
B3a). The task: `docs/design/memfn/r17b_prime.md` rev 3, §3.1 row B3b, which
serves R-21 ST3, PR-4, PR-8 and PR-9 under D167's build GO.

**Delivered:**

- The PRES rows (P0, P2, P3, P4, P9) and D2 are `routed` = 1.
- The presence links decide WHICH parts a pre-check tests. pcrec lays the
  parts out from those links, and the kit holds the layout to them.
- Bit 45 is retired to `--memfn=no-pres-set-lead` in the same commit.
  `PCREC_NO_REQ_SET_LEAD` stays a working alias, and the alias is tested (Q-19).
- `MF_VOCAB` 4 (`MF_USE_ENTRY`) and `MF_SITE_ABI` 17.
- Three new kit denies; the memfn floor goes 11 → 14.
- The D80 spec hunks.
- Eight new sabotage rows and ten re-aimed ones, all DETECTED solo.
- A proposed main-side diff for the ENTRY use.

**No pcrec abi event and zero artifact movers.** Stream 5 moves only by its
declared delta, checked both ways. The heavy runs are OWED in
`docs/dev/lanes/b3b/chain.sh`.

## 1. Commits (c88537116..tip)

| commit | what |
|---|---|
| 450e17878 | the routing commit. `fd_pres` (the PRES slot's walk, ports, per-span facts, P4 as an order row asked after the terminal, head/coverage/order applied); the presence ask (`mf_ask` on an ALL_PRESENT site with pspans, links only); `pres_layout_check`; `mf_pres_proof` as a stated site fact (`MF_SITE_ABI` 17); `MF_USE_ENTRY` (`MF_VOCAB` 4); the three `options.def` denies. pcrec: `req_site_define` lays the parts out from the links, `req_dominated_applies` / `req_set_leads_applies` read the kit, and `req_lead_byte` is deleted. Bit 45's `axes.def` row is removed; `compile.c` rewrites `PCREC_NO_REQ_SET_LEAD` into `no-pres-set-lead`; the CLI keeps `-fno-req-set-lead` |
| db76656e1 | the facts `used` record kept: `pcrec_fact_req_whole_run` pass-asked on every emitted pre-check, `req_set` on set-leads and no-DFA routes (766 facts movers before this, 0 after) |
| fe20a7dc4 | presence asks traced (`phase=ask`); arm/fd fixtures; finder_check section M; rows.tsv / row_floors.tsv rows |
| 56fd9bb4c | spec hunks (tuning §2.29/§2.40/§2.41, registry §6/¶8a/¶8b, facts_listing §4.1, `lib/pcrec.h`); registry retired-bit arm; count pin 238 → 236 |
| d109657b7 | the declared registry-dump delta and `dumps_delta.py` (both ways) |
| fd305b4b1 | re-aims S277 S278 S316 S452 S457 S458 S459 S462 S596 S1018 |
| 8444f0ed5 | `memfn/docs/finder_history.md`: the B3b routing and P4's order-row reading |
| 903f94667 | the routed-decision records in the five-pick shadow (`rdom rlead rhead rwin rwhole rrest`) with witnesses and plants; DIFFER_PINS for the PRES denies |
| 5cb5ce658 | `MFROUTED PRE` records (pcrec side); census wrappers; MEMFN_CLASS rows |
| 9fa11093e | `tests/memfn/run_presence.sh` (alias + PR-8); the omin fixture; `run_axes.sh` reads retired bits |
| 9c90179e0 | sabotage rows S1103-S1110 |
| 4dc2031ff | census floors and transcripts |
| b4a700fd6 | a pre-check P2 drops records as `MFPRESDROP` (C10's `MFROUTED` stays the defined sites'); the shadow takes no `mf_site` by value |
| 3b5abf3ae | CLAUDE.md updates; memfn.h link semantics; tuning.md tables for the retired bit |
| d15ba93e5 | `docs/dev/lanes/b3b/`: proposed ENTRY diff, heavy `chain.sh`, mech rows, scorer |
| (this) | this report |

## 2. What the routing is

**The kit's side.**

- **The rows.** `fd_rows[]`'s PRES rows P0 `required`, P2 `dominated`,
  P3 `pick`, P4 `set-leads` and P9 `default` are `routed` = 1, and so is D2
  `run` (D2 maps to the nested `fn_rows[]` walk through a marker arm,
  `fd_nested_walk`).
- **The walk.** `fd_pres` (memfn/src/finder.c) walks the PRES slot over the
  site's `pspans`. It runs the ports (`kit_pres_picks`, the arithmetic
  B3a ported) and sets the per-span facts. Then it decides each span with
  `fd_decide`.
- **P4 is an ORDER row,** asked on its own (`kit_ask`, `verify` = 1) after the
  terminal has decided the span. Its link puts the set's pick at the head of
  the chain.
- **Coverage.** A REST member that is an exact position of a run verified
  whole is not tested again (today's `req_set_rest_members` rule, now read
  from the links).
- **The presence ask.** An ALL_PRESENT site with `pspans` and no `preds`
  returns the links only: `exists` 0, proofs all ones.
- **The define.** It holds pcrec's parts to the links' layout
  (`pres_layout_check`, memfn/src/compose.c). A part the links did not decide
  is a refusal.

**pcrec's side.**

- `req_site_define` lays the head byte, the run (whole or window) and the
  rests out from the links; the head is asserted equal to `req_byte` when no
  run ships.
- `req_dominated_applies` keeps its LOCATE check, then asks the kit: every
  span must be `proven_by`.
- `req_set_leads_applies` returns `req_pres_head(…, true) >= 0`, and
  `req_lead_byte` is deleted.
- `req_pres_site` is the one constructor for the presence site; the shadow,
  the ask and the define all build through it.

**Withheld presence (Q-WR-4).** At G2's linear one-attempt and at LOCATE
`whole`, pcrec's own rows `one-attempt` and `dominated`'s LOCATE half decide
first and no span reaches the kit. The census counts these sites as
`withheld-one-attempt` (299 corpus) and `withheld-whole` (66 corpus).

**Handoff framing (a) (Q-WR-5).** The ORIGIN stays pcrec's: K, the moved start,
the re-entry and the K admission. The kit decides the presence the admission
reads, so the `req-use` rows' `--list-axes` text does not move (tuning
§2.41¶7a).

**The alias (Q-19, binding).** The compile driver (src/core/compile.c) rewrites
`PCREC_NO_REQ_SET_LEAD` into the memfn option string with `no-pres-set-lead`
appended, then clears the bit. An overflow of the option buffer is a refusal,
never a drop. The CLI keeps `-fno-req-set-lead`, which sets the bit.

`tests/memfn/run_presence.sh [alias]` checks five witnesses (floor 4), byte
and utf8. For each it asserts:

- `-fno-req-set-lead`'s artifact equals `--memfn=no-pres-set-lead`'s;
- both differ from the default;
- beside another kit option, the alias is the joined deny.

S462 (the rewrite dropped) and S1110 (rewritten to the wrong row) are both
DETECTED.

**PR-8.** `run_presence.sh [pr8]` checks that on the no-DFA VM route the
presence verdict precedes the first attempt, today's order.

## 3. Deviations from the design text, and why

1. **P4 is an order row asked after the terminal**, not a terminal in the
   first-match walk. As a terminal it would shadow P3's member decision on
   every set-leads span; its link carries `order` only. This is logged in
   finder_history.md.
2. **pcrec lays the parts out from the links, and the kit CHECKS the layout**
   (`pres_layout_check`), rather than the kit rendering the parts. The
   renderers already are the kit's (`precheck*`). Moving the layout too
   would have moved bytes; the check makes a divergence a refusal (S1107).
3. **`pres_proof` is a stated SITE fact** (`mf_pres_proof{byte, stop, run,
   stated}`, `MF_SITE_ABI` 17). P2 must know what span 0's search proves, and
   UNSTATED with `pspans` present is refused (S1109).
4. **The ENTRY use is a PROPOSED diff, not landed** (`proposed/entry_use.diff`).
   The kit side is in: `MF_USE_ENTRY`, allowed on ALL_PRESENT only, and
   `MF_VOCAB` 4. pcrec's adoption touches DELEG_SITES' PRE use ceiling,
   `check_use`/`deleg_check`, the two `s->use` writes and the deleg sed
   plant, which are main's files.
   - `git apply --check` is clean in a `git worktree add --detach` scratch
     (`$S/wt_apply`).
   - Applied, it reads test-memfn-deleg 14/0, -manifest 13/0 and -finder
     981/0, with 0 emit_sweep movers against the branch.
   - The C10 fixtures needed no change, and C17's PRE row is already
     `delegated`.
5. **D2 is routed, and vacuously so.** Its reach is `pending-site:R-18`: no
   pcrec site states a RUN span 0 FIND today. The routed census shows no D2
   record, and finder_check section M exercises D2 on the `run3` fixture.
6. **Only one `--list-axes` axis moves (`req-admit`), not two.** Under framing
   (a) the `req-use` rows stay pcrec's word for word (§2.41¶7a states that).
   The declared delta is `req-admit/dominated` (`applies`) plus
   `req-admit/set-leads` (`deny_macro`, `deny_bit`, `cli_flag`, `applies`),
   plus the three `memfn` rows.
7. **The declared TRACE delta is EMPTY.** The trace sweep's SET gate is clean.
   The ordered diagnostic differs only by fewer repeated records
   (528,814 → 523,885 and 185,615 → 177,167), because pcrec's own
   `req_lead_byte` re-derivations are gone. test-cand-oracle reads 141/0
   with no re-pin.
8. **The kit's per-kind "consulted" bit was not built.** The presence ask reads
   no set value, so nothing is consulted. The bit stays zero-mover by
   construction.
9. **`MFPRESDROP` is a new trace record.** A pre-check that P2 drops was never
   defined, so it records as `MFPRESDROP`, not as C10's `MFROUTED PRE`. An
   extra kind record had spoiled a C10 fixture.

## 4. Validation (light, this lane; cores 12-15, -j4)

Scratch: `S = worktrees/memfn-slot/b3b`. The reference is c88537116, built at
`$S/ref/build/`.

### 4.1 Byte identity (emit_sweep, reference c88537116)

VALIDATION_SWEEPS_TABLE

### 4.2 KW-8 on the kit-sourced proof (B3a's binding note)

`pick_census_b3b.py` over corpus 4,624 / bench 367 / rwquest 177, on three
arms (`-`, `-e utf8`, `--engine=vm`).

- **Base:** every pick and every routed record (`rdom rlead rhead rwin rwhole
  rrest`) agrees 100%. Every non-trivial floor passes, for example corpus
  `dominated` nt_agree 3,260 ≥ 2,934 and `set` 2,465 ≥ 2,218. `fails=0`.
- **The three deny arms** (`--ports-only`) and **the measured `weblog`
  bundle:** `fails=0`.

Transcripts are in `docs/design/memfn/r17b_prime/b3b/out/pick_census_*.txt`.

The routed census (`routed_census_b3b.py`) reads 16 cells with 0 failures. PRE
by row:

| route | P0 | P2 | P3 | P4 |
|---|---|---|---|---|
| DFA_SCAN | — | 1,688 | 2,803 | 9 |
| HYB_PF | — | 1,998 | 1,104 | 7 |
| DFA_ATTEMPT | — | 8 | 136 | 2 |
| VM_ATTEMPT | 5,305 | — | — | 24 |

- P0 (REQUIRED) appears only on the no-DFA route.
- P9 appears only under `--memfn=no-fd-pres-pick`.
- D2 has no pcrec site.

The transcript is `out/routed_census.txt`.

### 4.3 Suites

LIGHT_SUITES_TABLE

### 4.4 Sabotage (solo, `tests/mech/run_sabotage_matrix.sh ID`)

All 18 rows are DETECTED. Logs are in `$S/sab/<id>.log` and the status is in
`$S/logs/sab.status`.

| row | anchor | detecting cells |
|---|---|---|
| S1103 pres-p0-narrowed (NEW) | memfn/src/finder.c | memfnfinder 2fail/979pass, corpus 6fail/18pass |
| S1104 pres-rest-last-untested (NEW, absent-at-end) | memfn/src/precheck.c | corpus 6fail/18pass |
| S1105 pres-p0-unrouted (NEW, SN-1 for PRES) | memfn/src/finder.c | memfnfinder 14fail, prechecks 28fail |
| S1106 pres-omin-below-start (NEW, re-asked range omin < 0) | memfn/src/compose.c | memfnfinder 1fail/980pass |
| S1107 pres-layout-unchecked (NEW) | memfn/src/compose.c | memfnfinder 1fail/980pass |
| S1108 pres-lead-not-head (NEW) | memfn/src/finder.c | memfnfinder 5fail, prechecks 13fail |
| S1109 pres-proof-unstated-accepted (NEW) | memfn/src/compose.c | memfnfinder 1fail/980pass |
| S1110 set-lead-alias-wrong-row (NEW) | src/core/compile.c | memfnfinder 6fail/975pass |
| S277 precheck-whole-set-removed (re-aimed) | memfn/src/finder.c | prechecks 6fail, corpus 6fail |
| S278 precheck-whole-run-removed (re-aimed) | memfn/src/finder.c | prechecks 7fail, corpus 8fail |
| S316 findings-k65-pick-decides-giveup (re-aimed) | memfn/src/finder.c | findings 17fail/102pass |
| S452 set-rest-marks-masked (re-aimed) | memfn/src/finder.c | corpus 6fail, codegen 2fail |
| S457 set-leads-never-applies (re-aimed) | memfn/src/finder.c | prechecks 6fail |
| S458 set-leads-tie-leads (re-aimed) | memfn/src/presence.c | prechecks 3fail |
| S459 set-rest-retests-lead (re-aimed) | src/gen/emit_dfa.c | prechecks 73fail |
| S462 set-lead-deny-ignored (re-aimed) | src/core/compile.c | prechecks 3fail |
| S596 cand-row-deny-dropped (re-aimed) | memfn/src/finder.c | candoracle 1fail/164pass |
| S1018 sn2-query-class-lies (re-aimed) | memfn/src/compose.c | memfnfinder 41fail/857pass |

The KW-10 plants reach NON-DFA routes. S1103, S1104 and S1105 fail corpus cells
on the no-DFA VM route, where a NOMATCH turns into a step give-up. These are
answer-level reds, not DFA-route-only ones.

## 5. OWED (heavy; not this lane's)

`docs/dev/lanes/b3b/chain.sh` holds the whole list, armed by the kit manager at
a pinned tip. Its verdict is the last line of `chain.status`,
`^CHAIN (COMPLETE|FAILED)`.

- build + strict;
- `make test` via perfrun;
- the 142 mech rows in `mech_rows.txt`, each SOLO and scored against its
  SAB_EXPECT. The rows: sabotage_anchors `--step` c88537116..HEAD, plus the
  kit, test-edit and suite-derived rows, plus B3b's 18;
- G2 full;
- the N2 census + `n2_report --floors --propose`. This pins the PLACEHOLDER
  pcrec floors of P0/P2/P3/P4/P9 in `tests/memfn/row_floors.tsv`;
- the `MEMFN_REACH_ONLY` memfn reach arm;
- the form census;
- B3b's own two censuses with floors.

The manager also owes cleanup of the scratch detached worktrees `$S/wt_entry`
and `$S/wt_apply` (via `git worktree remove` on the main repo; the lane did
not prune them).

## 6. Rulings received

- **2026-10-18 (kit manager):** main's lane e1 builds on cores 0-7 and this
  lane stays on 12-15. CPU-bound work ends by 19:30. e1 bumps the abi 79 → 80
  when it lands; whether to merge main is the kit manager's call. As of this
  report it had not landed and I did not merge main.

## 7. Charter vs committed

| §3.1 B3b promise (and the brief) | artifact | state |
|---|---|---|
| PRES rows and D2 `routed` = 1 | memfn/src/finder.c (`fd_rows[]`, `fd_pres`), 450e17878 | DONE |
| KW-5: the presence class | `mf_site.pspans` (B3a) read by `fd_pres`; `pres_proof` stated | DONE |
| KW-6: G-1/G-2 (REQUIRED all, the WHOLE run, before the first element) | P0's link (`verify`, `member` 0, whole run); PR-8 check; S1103/S1104 | DONE |
| KW-7: the PRE composite's several uses; the ALL_PRESENT renderers as the ENTRY use's renderings | kit: `MF_USE_ENTRY` on ALL_PRESENT; pcrec: `proposed/entry_use.diff` | kit DONE; pcrec side PROPOSED, owner main, trigger: main's review of this delivery |
| the applicability rule (C-9) | P0 precedes, gate over `need` and `site_kind`; finder_check M | DONE |
| handoff framing (a) (Q-WR-5) | tuning §2.41¶7a; `req-use` unchanged | DONE |
| presence withheld at G2 one-attempt and LOCATE `whole` (Q-WR-4) | pcrec rows decide first; census `withheld-*` counts | DONE |
| bit 45 retired to `--memfn=no-pres-set-lead`, same commit | 450e17878 (`axes.def`, `options.def`, compile.c) | DONE |
| `--emit-facts` `used`/`why` re-sourced | db76656e1; facts stream 0 movers; facts_listing §4.1¶2 | DONE |
| `--list-axes` `req-admit`/`req-use` re-sourced | `req-admit` text names the kit rows; `req-use` unchanged by framing (a) | DONE (one axis moves, §3 item 6) |
| Q-19: the alias works, or refuses loudly; tested | compile.c rewrite; `run_presence.sh [alias]` 5/5; S462, S1110 | DONE |
| PR-8 checked | `run_presence.sh [pr8]` | DONE |
| `MF_USE_ENTRY` as an MF_VOCAB event | memfn.h `MF_VOCAB` 4 | DONE (kit); pcrec adoption PROPOSED (above) |
| denies `fd-pres-g1`, `fd-pres-pick`, `pres-set-lead`; floor 11 → 14 in docs/spec | options.def; registry §6¶8a/¶8b | DONE |
| emit_sweep drops bit 45's two DIFFER_PINS rows | scripts/emit_sweep.py (four rows: byte and utf8 of both) plus the new deny pins | DONE |
| KW-8 re-run on the kit-sourced proven0; every deny arm and the measured bundle at 100% | §4.2 | DONE |
| zero artifact movers; no pcrec abi event | §4.1 | DONE |
| stream 5 a DECLARED registry delta | `dumps_declared_B3b.tsv` + `dumps_delta.py` | DONE |
| declared trace delta; startset readers and test-cand-oracle re-pinned | trace SET gate clean (empty delta); cand-oracle 141/0; startset in §4.3 | DONE (no re-pin needed) |
| D80 spec hunks: tuning §2.40/§2.29/§2.41, registry §6 + ¶8a/8b, `lib/pcrec.h` bit 45, facts_listing | 56fd9bb4c, 3b5abf3ae | DONE |
| main-side items as PROPOSED diffs, `git apply --check` in a detached-worktree scratch | `docs/dev/lanes/b3b/proposed/entry_use.diff` (DELEG_SITES and C17 need no other change; C10 fixtures unchanged) | DONE |
| KW-10's presence family with NON-DFA-route plants; S1103-S1110 solo with SAB_EXPECT | §4.4 | DONE |
| C-3/C-4/C-5/C-6 (window_contract revisions implemented by r17b_prime §4.4/§4.1/§1.4) | the routed rows and links; C-7/C-8's text edits are main's (with window_contract rev 3) | DONE in code; doc edits main's |
| light validation list | §4 | DONE |
| HEAVY: make test, mech derived rows, G2 full, N2 + `--propose`, the reach arm, form census | `docs/dev/lanes/b3b/chain.sh` | OWED, owner the kit manager, trigger a heavy slot at the pinned tip |
| the PRES rows' pcrec floors | `tests/memfn/row_floors.tsv` PLACEHOLDERs | OWED to chain.sh's N2 `--propose` step |
