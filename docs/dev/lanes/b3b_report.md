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
| 1c489eb1f | tuning §2.40¶2 drops a walkback phrase (test-spec-history) |
| ec6139af0 | D2's refusal names the declined field (G2 enforced classes); this report |

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

All sweeps used a FROZEN copy of the tip binary (`$S/frozen/`, taken at
38ee2a848; `cmp` confirmed it unchanged through the run). Logs are in
`$S/logs/sw2/`.

| arm | result |
|---|---|
| plain, every stream (5,790 argv rows, 386 composition files) | 0 movers on every artifact stream; dumps 1 mover (`--list-axes`), exactly the declared delta: `dumps_delta.py` 3 added + 2 changed rows, 0 failures |
| `--arms start` (every DIFFER_PINS arm, byte and utf8) | every pre-existing arm holds its pins; the three new kit denies are ASYMMETRIC because the c88537116 reference REFUSES `--memfn=no-fd-pres-g1` / `-pick` / `no-pres-set-lead` (unknown options there). Their floors were measured with the branch as both sides (`$S/logs/arm_*.log`, all rc 0). Against a reference that has B3b they become ordinary DIFFER arms |
| alias: `--extra=-fno-req-set-lead`, byte and utf8 (the ref spells bit 45 natively, the tip through the alias) | 0 movers (c-default, c-vm, facts) |
| `-fmemfn-simd`, `-fcomments` | 0 movers (incl. composition) |
| base `-e utf8`, `--engine=vm` | 0 movers (c-default, c-vm, emit-ir, facts, stderr) |
| rwquest (176 questions), bench (337 distinct `bench/*/patterns/*.rx`, read-only from pcrec-bench), `--no-corpus` | 0 movers, rc 0 |
| synthetic sets through the B1 lever (`pcrec-harness --harness=measures=`: all-walk, all-v1, all-wide, every-key) | 0 movers each |
| `run_longprefix_sweep.sh`, `run_prefix_invariance.sh` | rc 0 each |
| frozen tip vs the post-G2-fix binary (c-default, c-vm, facts, stderr) | 0 movers (the fix changes refusal text only) |

The trace sweep, run earlier in the lane, has a clean SET gate (§3 item 7).

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

Runner `$S/light.sh`, one suite at a time; logs `$S/logs/light/`.

| suite | result |
|---|---|
| make, make strict | rc 0; strict clean (also after the G2 fix) |
| test-codegen | rc 0 (236 s) |
| test-rxtsource | rc 0 |
| test-memfn-g2 (quick) | RED at first (5 enforced-class cases); a B3b defect, FIXED, then 71,217,801 / 0 (see below) |
| test-spec-history | RED at first: `[walkback]`, the phrase "until [IFACE-PUSH] batches its removal" in tuning §2.40¶2 (mine); dropped in 1c489eb1f, then 145/0 |
| test-memfn-arms / -stamps / -manifest / -link / -forms / -reach / -guarded / -simdfloor / -arch / -rank / -rows / -deleg | rc 0 each |
| test-memfn-finder | 981/0 (finder 949, arm_reach 16, pr11 5, presence 10) |
| test-startset | rc 0, no re-pin needed |
| test-registry | rc 0 |
| test-cand-oracle | rc 0 |
| test-findings, test-compound, test-plan-lint | rc 0 |

**The G2 red was B3b's own defect, not pre-existing.** Five strict cases, all
FIND/ASSIGN sites with a RUN span 0, were refused with "the finder row D2's
routed pick does not serve this site" instead of a refusal naming the declined
field (`on_miss` LOOP_EXIT, `miss` unstated). Routing D2 sent these sites
through `select_arm`'s routed-row branch. D2's row is the nested walk, though,
so its decline IS the walk's decline. At c88537116 D2 was unrouted, the same
sites reached the generic walk, and `gate_describe` named the field. I did not
re-run c88537116's G2 to confirm this; the cause is read directly off the
refusal text.

The fix is in memfn/src/compose.c. `select_arm` reports whether it walked, and
`define_sel` keeps the routed-pick refusal only for a routed row that does NOT
walk. The confirming runs: G2 quick 71,217,801 / 0, finder 981/0, arms 383/0,
strict clean, sabotage anchors 806/806 resolving, and 0 movers vs the frozen
tip. The fix commit is listed in §1.

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
- the N2 census + `n2_report --floors --propose`. `--propose` PRINTS each
  row's floor(0.9 x chosen); it pins nothing. The step's rc folds N2's rc and
  the floor verdict (`floor_fail=0`). Pinning the PLACEHOLDER pcrec floors of
  P0/P2/P3/P4/P9 in `tests/memfn/row_floors.tsv` is a FOLLOW-UP COMMIT after
  the heavy chain, copied from the propose log (OWED, owner the kit manager);
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
| the PRES rows' pcrec floors | `tests/memfn/row_floors.tsv` PLACEHOLDERs | OWED: chain.sh's N2 `--propose` step PRINTS them; pinning is a follow-up commit after the chain, owner the kit manager |

## 8. Review fixes (b3brev)

Lane b3bfix (opus, 2026-10-18), on the same branch from fc2035438, applied the
kit manager's rulings on the read-only review b3brev (MERGE-WITH-FIXES). The
branch still moves NO artifact byte and makes NO pcrec abi event: the frozen
tip binary against c88537116 reads 0 movers on every artifact stream (§8.2).
Kit-side, `MF_CLASS_V` goes 3 -> 4 inside `MF_SITE_ABI` 17 (unreleased on this
branch, so 17 is not bumped). Scratch: `S = worktrees/memfn-slot/b3b`, new
logs under `$S/logs2/` and `$S/fixlogs/`.

### 8.1 Finding by finding

| # | finding | commit | what changed | evidence |
|---|---|---|---|---|
| 1 | BLOCKER: `mech_rows.txt` had a bare `S` | 087381c8f, d4a410bbb | `derive_rows.sh` re-derives the union reproducibly: (a) `sabotage_anchors.py --step b3b=c88537116..HEAD` over the base's archive, (b) rows anchored in an edited memfn/ or tests/ file or detected by a changed suite, (c) `mech_rows_judged.txt` (the first list's 103 real ids, its `S` removed), (d) every row the branch adds or re-aims. `chain.sh` refuses at arm time any line not `^S[0-9]+$` (`CHAIN FAILED at row-list`) | `mech_rows.txt` re-derived at 41341a08c: 159 ids (a 60, b 94, c 103, d 19), 0 malformed; vs the first list (141 real ids): +18 (rows anchored in `memfn/src/ofsskip.c` and the other files this fix round edits, and S729), -0. The arm-time check run on both files: the first list (with `S`) reads `CHAIN FAILED at row-list ('S ')`, the new one passes. `sabotage_anchors.py` exits 2 on the base's 8 pre-existing UNRESOLVED src anchors; `derive_rows.sh` accepts rc 2 with rows written and prints the count |
| 2a | MAJOR: no answer check under the three new denies | 55a9194dd | `chain.sh` step 6 gains `axes-pres`: `AXES="--memfn=no-fd-pres-pick --memfn=no-fd-pres-g1 --memfn=no-pres-set-lead" bash tests/axes/run_axes.sh` (no `MEMFN_REACH_ONLY`), rc honoured and any `AXIS FAIL` line folded in | OWED to the heavy chain (whole corpus x 3 denies) |
| 2b | the same, LIGHT now | 7f3f12259, 41341a08c | `tests/litscan/presence_deny.rxt` (generated by `gen_presence_deny.py` with gen_handoff.py's own oracle helpers: python3 `re` AND libpcre2 for byte blocks, libpcre2 alone for utf8 and `\K`): 11 blocks, 574 cells at every boundary start: a set member below the re-entry's scan position (`a.?b` with decoy landmarks), below the REPORTED start (`a{2,4}\Kb`), lookbehind bytes below the attempt (`(?<=qz)x?a:`, `(?<=q)a:`), whole-run/rest members after a run window, five byte landmarks (K = 14), utf8. Runs at the default route in the corpus; `run_presence.sh` [deny-answers] (part `presence` of `make test-memfn-finder`) runs it with K65/K66's files under each deny, and handoff.rxt under P9, with a reach floor (8 of 11 patterns must move under P9). The header of `req_site_define` now states the re-entry half of the argument (the start state's future is a fresh search's from `scan_position`, so any completion implies a match wholly in `[scan_position, n)`; the facts hold no lookbehind byte) | default and all three denies: 574/574 each; deny-answers P9 5,522 cases over 4 files, g1 and set-lead 614 over 3, all 0 failed; reach 9 of 11; the 43 corpus files holding every P9 handoff mover (106 patterns, `$S/fx2/p9_handoff_movers.tsv`) under each deny: 41,859 cases each, 0 failed. NO answer differs, so the guard is NOT restored and P9 does not refuse on handoff sites |
| 3 | MAJOR (U4): routed refusal did not name the field | 55a9194dd, 087381c8f | `kit_ask` gains `gate_verdict *why` (filled where the gate declines; NULL allowed); `select_arm` passes it on both branches; `define_sel` has ONE refusal: `no row serves this site (the finder row X's routed pick): <gate_describe>`; the `walked` flag is gone. S729's anchor re-aimed for the new signature (mechanical, intent unchanged) | G2 quick 71,217,801 / 0 (the enforced classes 0 failed, refusal-unnamed 0); finder 995/0. Probe (`$S/d1probe/probe.c`, a one-byte FIND with `on_miss` LOOP_EXIT): D1 `...(the finder row D1's routed pick): \`note\` (R2: stated as OTHER, not served)`, D1w `...D1w's routed pick): \`empty\` ..., \`table_ref\` ..., \`note\` ...`, D1c `...D1c's routed pick): \`empty\` ..., \`floor\` (R1: used, not stated), \`note\` ...`; G2's D2 cases `...D2's routed pick): \`on_miss\` (R2: stated as LOOP_EXIT, not served)` |
| 4 | MAJOR: N2 floor verdict not in chain rc | 55a9194dd | step 5's rc folds N2's rc, the propose step's rc and `floor_fail=0 ` (absent: rc 6). N2 DOES run the `--memfn=no-fd-pres-pick` arm (`n2_census.py` `build_arms` takes every `--memfn=` spelling of `--list-axes`' memfn section; checked: the arm list holds all three PRES denies at both tiers), so P9's reach reason `pcrec` stays honest and rows.tsv is unchanged. §5 and §7 corrected: `--propose` PRINTS; pinning the PLACEHOLDER floors is a follow-up commit after the heavy chain, OWED, owner the kit manager | `bash -n chain.sh` clean |
| 5 | MINOR (U5): routed census inferred the row from the link's shape | 55a9194dd, 087381c8f | the kit carries the deciding rows: `mf_class.pres_row[]`/`pres_led[]` (1 + the row's index in `mf_finder_rows`' listing; `MF_CLASS_V` 4, appended last; fd_rows untouched). `pcrec_memfn_pres_routed` names the row from the listing, and each record also carries the decided link and the row's template (the listing's `pick`); `routed_census_b3b.py` FAILS a row that decided a link outside its template's kind. Witness the reviewer asked for: P0's predicate made false (P9 decides REQUIRED spans with P0's own link shape): artifacts byte-identical, the records read P9 where the old inference read P0; its sabotage row is BUILT under a placeholder id (`docs/dev/lanes/b3b/pending_rows/SXXXX_pres-p0-pred-false.sh`, ids S1111-S1112 requested from main) | S1103's plant (solo-built trace binary): routed census rc 1, 5,311 link-shape violations ("P0 decided link v1p0m9o1 outside its template v1p0m0o0"); clean tip 0 violations, 16 cells, 0 failures. P0-pred-false plant: finder_check 3 failed / 946 (fd-P0 decided P9), rows 1 failed / 237 |
| 6 | MINOR (U6): trace P2 record not withheld | 55a9194dd, f7a88572f | the dropped pre-check's routed record moved into `req_pick_shadow`, after the SAME withholding test (one-attempt, LOCATE `whole`); `routed_floors_B3b.tsv` re-measured | HYB_PF P2 1,998 -> 1,903 records (floor 1,798 -> 1,712); the other cells move by the new corpus file only (+1..+6) |
| 7 | MINOR: no negative control on [pr8]; no DFA_ATTEMPT witness | 7f3f12259 | the order check reads EVERY verdict line of the search body (to its closing `}`) before the first attempt; three DFA attempt-route witnesses (`(?m)^ab[a-z]*@` byte and utf8, `(?m)^x{2,5}(?i:cat)`), `for (start = ` as the attempt marker; per witness a planted reorder (one verdict line moved after the attempt, in a copy of the text) must be reported. The first form (the FIRST verdict line) did NOT detect 5 of 6 plants: a verdict split around the attempt read green | 6/6 witnesses, 6/6 plants reported; presence 24/0 |
| 8 | MINOR: walkback phrase in lib/pcrec.h | 55a9194dd | "until [IFACE-PUSH] batches its removal" dropped; the comment now reads as tuning §2.40¶2 | test-spec-history 0 failed |
| 9 | deviations | this section | see §8.3 | `entry_use.diff`: `git apply --check` CLEAN at f7a88572f in a `git worktree add --detach` scratch (`$S/wt_check`), removed after |
| 10 | MINOR: census timeouts silent | 55a9194dd | `routed_census_b3b.py` counts `TimeoutExpired`, prints `timeouts N`, fails above 0 | clean run: timeouts 0 |
| 11 | MINOR (U11): rwin compared a window the layout did not use | 55a9194dd | for a whole-run link the shadow now compares the window `pres_layout_check` uses (the ports over the routed site's own stated proof); a run the links do not verify renders no window and is SKIPPED and counted (`MFPICKSKIP`), and `pick_census_b3b.py` prints the skips | pick census corpus/bench/rwquest: fails=0, skips 0 |

Commits in order: 7f3f12259 (2b, 7), 55a9194dd (3, 5 kit half, 6, 11, 10,
chain.sh 1/2a/4, 8), 087381c8f (5's records and census check, S729,
derive_rows.sh), f7a88572f (floors, pending row), 54d582e8b and 41341a08c
(re-pins the new corpus file moved: rxtsource census, startset forced
manifest; the generator's oracle path made arch-blind for C4), then the
mech_rows/PIN and report commits.

### 8.2 Validation (light; cores 12-15)

All under `taskset -c 12-15`, -j4, one run at a time. Logs `$S/logs2/`
(suites, sweeps, solo mech), `$S/fixlogs/` (finder, G2, censuses, re-pins).

| check | result |
|---|---|
| build, `make strict` | rc 0; strict clean |
| the 24 light suites (`$S/light2.sh`, the previous lane's list) | 22 green first time. test-rxtsource RED: the new corpus file moved the census (+1 file / +11 blocks / +574 lines; C3 +462 PASS, +112 pcre2-only), re-pinned in 54d582e8b, then 298/0. test-memfn-arch RED: the generator's default oracle path named the x86_64 multiarch dir (class 6); made arch-blind in 41341a08c, then 15/0. test-startset RED: the forced-VM mover manifest +8 presence_deny.rxt rows, and `tests/utf8/wclass_illformed.rxt:445` (`x.y`, utf8) leaves because presence_deny.rxt holds the same (text, options) and now takes its id (ssbuild3's ctxnode precedent); `census_s1.py`, corpus rows only, re-pinned in 41341a08c, then green. Others: codegen 209 s, G2 quick 71,217,801 / 0, spec-history, arms, stamps, manifest, link, forms, reach, guarded, simdfloor, plan-lint, findings, rank, finder (995/0), rows, deleg, registry, cand-oracle, compound: rc 0 |
| frozen-binary emit_sweep vs c88537116 (frozen at 54d582e8b, `cmp` unchanged through the run) | plain: 0 movers on every artifact stream over 5,801 argv rows and 387 composition files; dumps 1 mover (`--list-axes`) = the declared delta (`dumps_delta.py` 3 added + 2 changed, 0 failures). `--arms start`: every pre-existing arm holds its pins; the three new kit denies are asymmetric only because the reference refuses the unknown options (branch-side floors unchanged: P9 187 byte / 262 utf8). Alias byte/utf8, `-fmemfn-simd`, `-fcomments`, base utf8, base vm, rwquest, bench, the four synthetic sets, longprefix, prefix invariance: all rc 0, 0 movers |
| KW-8 (pick census, trace build of the fix tip, corpus/bench/rwquest x three arms) | base, `--ports-only` under each of the three denies, and `--analysis=weblog`: `fails=0`, `skips 0` every time |
| routed census | clean: 16 cells, 0 failures, link-shape violations 0, timeouts 0; S1103's plant: rc 1, 5,311 link-shape violations; P0-pred-false plant: records P9 (artifact byte-identical) |
| solo mech rows (`run_sabotage_matrix.sh ID`, from the committed tip) | S1103 DETECTED (memfnfinder 5fail/990pass, corpus 6fail/18pass); S1104 DETECTED (corpus 6fail/18pass); S1105 DETECTED (memfnfinder 18fail, prechecks 28fail); S1106, S1107, S1109 DETECTED (memfnfinder 1fail/994pass each); S1108 DETECTED (memfnfinder 5fail, prechecks 13fail); S1110 DETECTED (memfnfinder 6fail/989pass); S729 (re-aimed) DETECTED (cli 2fail, g2simd 170fail); S1018 (compose.c) DETECTED (memfnfinder 41fail/871pass) |
| presence suite (`run_presence.sh`) | 24/0: alias 5/5, PR-8 6/6 with 6/6 planted reorders reported, deny-answers 3/3, reach 9 of 11 |
| entry_use.diff | `git apply --check` clean at f7a88572f (detached scratch worktree, removed) |

### 8.3 Deviations, as ruled

- **(a) RATIFIED, a ruled deviation from §3.1:** only `req-admit` moves.
  `req-use` stays pcrec's under handoff framing (a) (tuning §2.41¶7a): the
  ORIGIN (K, the moved start, the re-entry, the K admission) is pcrec's; the
  kit decides the presence the admission reads.
- **(b) and (c), recorded as observations:** the review's deviations (b) and (c) are recorded here as OBSERVATIONS, not ratified and not re-opened, per the kit manager. Their wording is the review's: this lane asked b3brev for it and had no reply by delivery, so it does not restate them; the kit manager's ruling list is the record.
- **(d)** the kit manager asks main to apply `proposed/entry_use.diff` IN THE
  SAME MERGE as this branch. Re-checked: `git apply --check` clean at
  f7a88572f. The previous lane's scratch worktrees `$S/wt_entry` and
  `$S/wt_apply` were NOT removed: neither is clean; each holds exactly
  `entry_use.diff` applied (wt_entry's working diff is byte-identical to the
  committed file; wt_apply's differs only in the blob index lines). Removing
  them needs `git worktree remove --force`, which the ruling ("if they are
  clean") did not grant; nothing in them is unique.

### 8.4 Not done, and why

- **The heavy chain** (`chain.sh`, now with the row check, `axes-pres` and
  the N2 floor fold) is not run: OWED, owner the kit manager, at the PIN below.
- **The pending sabotage row** (`pending_rows/SXXXX_pres-p0-pred-false.sh`)
  has no id: S1111-S1112 are requested from main and not allocated. It is
  validated by hand (the planted tree: finder 3 failed, rows 1 failed,
  artifacts byte-identical) but not through `run_sabotage_matrix.sh`, which
  needs the row under tests/mech/sabotages/. The manager renames it, sets the
  id and adds it to `mech_rows.txt` (it is outside `derive_rows.sh`'s parts).
- **wt_entry / wt_apply** were not removed (not clean; §8.3 (d)).
- **The (b)/(c) deviation text** (§8.3).
- One fix commit (55a9194dd) carries several findings rather than one each;
  the table names each finding's commit(s).

### 8.5 Charter vs committed (updated)

| item | state |
|---|---|
| everything §7 lists DONE | still DONE; no artifact mover, no pcrec abi event (§8.2) |
| finding 1: mech rows re-derived, arm-time check | DONE (derive_rows.sh, 159 ids; chain.sh `row-list`) |
| finding 2a: non-reach answer-identity pass in chain.sh | DONE in chain.sh; the run is OWED with the chain |
| finding 2b: oracle-verified witnesses, wired into make test | DONE (presence_deny.rxt in the corpus; [deny-answers] in test-memfn-finder); no answer differed, guard not restored |
| finding 3: `kit_ask` why, one refusal path, `walked` dropped | DONE; G2 quick and finder green; D1/D1c/D1w/D2 refusals name the field |
| finding 4: N2 floor fold, P9 reach, report wording | DONE (P9 is reached by N2's arm list; reach unchanged) |
| finding 5: deciding row carried from the kit | DONE (`mf_class.pres_row/pres_led`, MF_CLASS_V 4); census holds the decided link to its row; S1103 now fails the census; the P0-pred-false witness row BUILT, id PENDING |
| finding 6: P2 record behind the withholding; floors re-measured | DONE |
| finding 7: negative control + DFA attempt witness, no new S-id | DONE |
| finding 8: pcrec.h wording, test-spec-history | DONE |
| finding 9: deviations recorded; entry_use.diff re-checked; scratch worktrees | DONE except removing wt_entry/wt_apply (not clean) and the (b)/(c) wording |
| finding 10: timeouts counted | DONE |
| finding 11: rwin on the layout's window, skips counted | DONE |
| light validation re-run | DONE (§8.2) |
| chain.sh PIN | set to this report's commit (the tip's parent: the tip only writes the PIN) |
| HEAVY (chain.sh) and the PRES floors' pinning commit | OWED, owner the kit manager |
