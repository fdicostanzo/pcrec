# fdb2 — R17-b′ step B2: ST2, one-byte FIND routed

Lane fdb2 (opus), 2026-10-16, for the memfn kit manager. Branch `lane/fdb2`
from `lane/memfn-fd` @ 285590dc6 (B0 + B1; abi 78, `MF_SITE_ABI` 12).
Charter: `docs/design/memfn/r17b_prime.md` rev 3 §3.1 row B2. Box: Linux dev
box, every run `taskset -c 12-15`, `-j4`.

**Verdict: B2 BUILT. ZERO ARTIFACT MOVERS on every emit_sweep arm run
(§2). NO pcrec abi event. `MF_SITE_ABI` 12 → 13, no `MF_VOCAB` move.**
D1, D1c and D1w are routed; the kit writes the one-byte sites' guard,
post-test, bounded block and moved test; pcrec's G1/R4/L4 read `mf_ask` and
the reader shadow is retired. The one arm whose bytes move is the step's
declared one: `--memfn=no-fd-d1` (D1w's walk, §2.3). fdb1's floor token did
NOT hold and is corrected in its own commit (16770a07c, §5.2).

## 1. What changed, item → file

| item (row B2) | where |
|---|---|
| D1, D1c, D1w `routed` = 1 (locked from here, §1.8) | `memfn/src/finder.c` `fd_rows[]`; `fd_route` (the routed decision: OFF variant, the stated kind; the pick's arm asked on its own, a declining arm REFUSED); `memfn/src/compose.c` `select_arm` asks it first; `memfn/docs/finder_history.md` |
| PR-1: the candidate set a SET term at every count, the table offered | `src/gen/emit_dfa.c` `find_site`/`pf_find_of` (`PCREC_FIND_NO_TABLE` is MLINE's context stop only); every PF row DEFINED above the body (memchr rows gained `pf_define_find[_bounded]` and their table emitter, so the table is emitted iff the kit's form reads it); `memfn/src/pffind.c` memchr rows serve an offered table |
| PR-2: miss and move as hooks | `PcrecFind.on_miss` (an unbounded site's leaving miss), the bounded `len - 1`, `PcrecFind.moved` / `mf_hooks.moved` (the DFA hat's re-seed, `pf_moved_reseed_of`); `mf_site.empty` MISS (unbounded) / NOP (bounded) |
| PR-3: `site_kind`, categorical, DFA_ATTEMPT included | `memfn.h` `mf_site_kind` (`MF_SK_*`; `MF_KIND_*` was taken by the analysis object) + `mf_site.site_kind`; `pf_find_kind` (DFA_HAT / HYB_PF / DFA_SCAN), VM hat VM_ATTEMPT, MLINE DFA_ATTEMPT, `req_site_kind` (the PRE composite, by route); `finder.c` `kind_cl` (the gate reads the stated kind) |
| `need` re-numbered, UNSTATED zero, every builder states it | `memfn.h` `mf_need`; `compose.c` `pred_kinds` refuses an unstated term/predicate need; pcrec's builders already stated it (no refusal on any sweep); fixtures (`tests/memfn/arm_fixtures.c`) and G2 (`g2_need` at the kit call, two new refusal cases) state it |
| PR-9: readers switched to `mf_ask`, the shadow retired | `emit_dfa.c` `cand_ask`, `cand_pf_site`, `dfa_cand_scan` (G1), `dfa_cand_ppm_of` (R4), `start_landing_applies` (L4); the trace build keeps the traps (`cand_ask_check`, `cand_ask_field`); PR-9's rename `DFA_PF_ONE_BYTE`, `CandSet.one_member`, `CandScan.one_byte` |
| KW-1 (D1), KW-2, KW-3 (the kit writes guard, post-test, wrapper, moved hook), KW-4 | `pffind.c` (`moved_open`/`moved_close`, `one_stmt`, the MISS guard, the NOP block, the walk post-test); the six axis-B emitters collapse to `pf_emit_skip` |
| F-B1-3 | `mf_class.proven_prev` (`MF_CLASS_V` 2), `compose.c` `kit_class`; §5.1 |
| R-22 / R-MS6, the arm-entry counter | `memfn.h` `mf_reach`/`mf_reach_table`, `compose.c`; `cli/main.c` `--harness=arm-reach`, `src/core/internal.h` `PcrecHarnessOptions.arm_reach`, `memfn_sites.c` (the stem), `memfn_stamps.c` (the table); check `tests/memfn/run_arm_reach.sh` (run by `make test-memfn-finder`); §6 |
| the routed-record count (§1.6 [rev3 B5]) | `memfn_sites.c` `routed_record` (pcrec's `MFROUTED` record from `mf_result.row`, trace build + `PCREC_MF_ROUTE_TRACE`); census `docs/design/memfn/r17b_prime/fdb2/routed_census.py` |
| checks | `tests/memfn/finder_check.py` K (routing), A (routed set per step); `run_finder.sh` F-B1-3 witness; `rows.tsv` D1/D1c/D1w → `pcrec` (signature from `MFTRACE FDROUTE`), `row_floors.tsv`; `scripts/emit_sweep.py` fd-d1 DIFFER floors |
| floor token (item 3) | separate commit 16770a07c: `finder.c` `K_EPS`, `memfn/data/sets/generate.py` + four synthetic sets, B4's predicted-mover manifest regenerated |
| sabotage | re-aimed S288, S481-S485, S495; new S922 (allocated, design §8.3); staged SKB2-1..5 (`docs/design/memfn/r17b_prime/fdb2/sabotage/`); §8 |

`MF_SITE_ABI` readers by grep: `memfn.h` (value + log), `memfn/include/
CLAUDE.md`, `compose.c`'s `s->abi` check, G2 (reads the macro). The other
"12" mentions are historical.

## 2. Validation (logs `worktrees/fdb2/build/land/`, verdicts `verdict.txt`)

Chain `build/land/chain.sh` at c5808f920; later commits are check fixes
and docs (listed under each row where they matter).

Pinned `taskset -c 12-15`, `-j4` (re-runs on 8-11 in an archived copy of
the tip, `build/land/rerun/`, so the running chain's `build/` was not
touched). Both layers: SIMD-off is every row; SIMD-on is the `simd` sweep,
`test-memfn-simdfloor`, `test-memfn-guarded` and `test-memfn-stamps`.

| run | result | log |
|---|---|---|
| `make`, `make strict` | rc 0, rc 0 | `chain.log` |
| `test-memfn-finder` (incl. `run_arm_reach.sh`, F-B1-3 witness) | 13/0 (arm-reach 13/0) | `test-memfn-finder.log` |
| `test-memfn-arms` / `-rows` / `-forms` | 383/0, 232/0, 5/0 | |
| `test-memfn-deleg` | chain: red (`mf_result` by value); fixed 0f2c115ab; re-run 5/0 | `rerun/test-memfn-deleg.log` |
| `test-memfn-stamps` / `-guarded` / `-simdfloor` | 25/0, 10/0 (4,088 cells), 51/0 (44 movers, floor 39) | |
| `test-memfn-rank` / `-manifest` / `-link` / `-reach` / `-arch` | 15/0, 11/0, 8/0, 4/0, 15/0 | |
| `test-registry` | chain: red (limits `[code]` on `CAND_ASKF_PROVEN_PREV`); fixed 975bd1821; re-run 79/0 | `rerun/test-registry.log` |
| `test-rxtsource` / `test-prechecks` / `test-startset` | 298/0, 395/0, 35/0 | |
| `test-cand-oracle` | 100/0 (75 witness lines, 48 rows) | |
| `test-compound` / `test-ci-shards` | 0 failed / 9/0 | |
| `test-codegen` | re-run 35/0 + ONE FAIL: [K37] `tests/axes/run_axes.sh:1185`, pre-existing on the base (F-B2-2); my own K37 hit fixed | `rerun/test-codegen.log` |
| `test-memfn-g2` (quick) | 52,987,694 / 0 | `test-memfn-g2.log` |
| emit_sweep plain (5,790 rows, 11 streams incl. dumps, composition 386 files) | 0 movers, 0 asymmetric | `sweep_plain.log` |
| emit_sweep `--arms start` | every arm/stream 0 movers EXCEPT `--memfn=no-fd-d1` c-default 1,004 byte / 985 utf8 (§2.3, the declared flip; c-vm 0); DIFFER_PINS updated in 9543303e7 | `sweep_start.log` |
| emit_sweep `-fmemfn-simd` / `-fcomments` / `-e utf8` | 0 movers each | `sweep_{simd,comments,utf8}.log` |
| emit_sweep synthetic sets (all-walk, all-v1, all-wide, every-key) | 0 movers each | `sweep_syn-*.log` |
| emit_sweep `--engine=vm`, rwquest, variants, trace; mech rows; SKB2; CTRACE census | RUNNING in the detached chain at hand-off (§9a) | `verdict.txt` |
| hand checks before the chain | `build/tmp/cmp.sh`: 65 cells identical vs ref285 (plain, `-fcomments`, `--engine=vm`, `-fmemfn-simd`, `-e utf8`); lever fence PASS; SAB anchors 748/748 | |

### 2.3 The one declared byte delta: `--memfn=no-fd-d1`

D1 routes, so its deny now moves every one-byte DFA and hybrid site to D1w's
walk over the offered table (`while (... && !rx_can_begin_match[...]) ...;
if (pos >= n) return 0;`, plus the table): 1,004 (byte) / 985 (utf8)
c-default artifacts, 0 on c-vm, 0 start stamps. The reference (B1) predates
the routing, so the arm's identity against it reads those as movers; they
are the flip §3.4 schedules ("fd-d1: DIFFER, floor = the one-byte DFA/hybrid
population"), pinned in `scripts/emit_sweep.py` DIFFER_PINS from this
measurement. Answer identity of the deny arm is test-axes' `--memfn=` arm's
(OWED, §9).

## 3. The declared trace delta

Declared (the step's whole intended trace change), checked by the `trace`
sweep still running in the chain (`build/land/sweep_trace.log`):

- **new** `MFTRACE FDROUTE art=<a> site=<s> row=<D1|D1c|D1w> arm=<pf_memchr|pf_memchr_bounded|pf_memchr_back|pf_walk|pf_walk_bounded>` (kit, MF_TRACE build) on every one-byte PF/MLINE/VM-hat site;
- **new** `MFROUTED\t<site>\t<kind>\t<row>` (pcrec, `PCREC_CAND_TRACE` build with `PCREC_MF_ROUTE_TRACE` set; absent otherwise, so the default trace build's record set is unchanged);
- **changed** `MFTRACE` arm-walk records for the PF sites: the site now states `site_kind`, `empty`, `on_miss` and the table offer, so field values in the existing records move (no record added or dropped);
- **changed** test-cand-oracle's witness reads: G1/R4/L4 ask `mf_ask` (`cand_ask`), so the reader shadow's `CANDASK` comparison records are gone and the trap lines (`cand_ask_check`, `cand_ask_field`) take their place; PRESENCE/RETRY declare `CAND_ASKF_PROVEN_PREV` (re-pinned: 75 witness lines, 48 rows, 100/0);
- **inventory_check / start-table reads DAG**: one new member `req_site_kind` (dispositioned NOTSTART), and `dfa_cand_scan`/`attempt_next_read` re-enter the graph (F-B2-3).

No other record kind moves; artifacts are byte-identical (§2).

## 4. Findings

- **F-B2-1 (pre-existing red, fixed).** `tests/compound/run_lever_fence.sh`
  (c) was red on the base: fdb1's `cli/CLAUDE.md` sentence names
  `--harness=measures=`. `cli/CLAUDE.md` joins the allowlist (the harness's
  own record), with the new arm-reach check.
- **F-B2-2 (pre-existing red, NOT mine).** `make test-codegen`'s [K37] flags
  `tests/axes/run_axes.sh:1185` (`--pcrec "$PCREC"` on a python line, from
  lane runaxes): red on the base too. My own K37 hit (an error message
  naming the shipped binary's path) is fixed.
- **F-B2-3 (pre-existing staleness).** `docs/design/start_table/
  inventory_check.py` against a freshly derived call graph is red on the
  base (48 undispositioned / not-in-graph); B2 adds one member
  (`req_site_kind`, dispositioned NOTSTART) and brings `dfa_cand_scan` and
  `attempt_next_read` back into the graph (now 46). A full re-derivation is
  not B2's.
- **F-B2-4 (a naming collision).** `MF_KIND_*` is the analysis object's
  kind-state enum; the consumer kinds are `MF_SK_*`.
- **F-B2-5 (a contract gap the step had to close).** A routed row whose pick
  renders the same text as the pre-table arm cannot be told apart in the
  artifact, so rows.tsv's text signatures cannot witness D1/D1c/D1w (a
  one-member VM hat and a many-member one print the same walk). A routed
  `fd` row's signature is read from `MFTRACE FDROUTE`; the population count
  is the routed census (§1.6 [rev3 B5] item 1).
- **F-B2-6.** `fields.def`'s class space is full (64), so the `moved` hook's
  one-statement shape is the serving rows' predicate (`one_stmt`), not a
  class.
- **F-B2-7.** G2's sites were written when need 0 meant REQUIRED; the
  renumbering would have refused 143 refusal-table bases. G2 states the old
  meaning at the kit call (`g2_need`, not blinded text) and gains
  `need-unstated`, `pred-need-unstated` and `site-kind-out-of-enum`.
- **F-B2-8 (D157).** `mf_result.row` hands pcrec a kit ROW id. It is a
  report for the routed-record count (a test-build record), read by no
  selection; it carries no method.
- **F-B2-9.** The inventory.tsv line rode the floor-token commit (16770a07c)
  by accident; it belongs to B2's change.

## 5. F-B1-3 and the floor token

### 5.1 F-B1-3: MLINE's ATTEMPT arm

Before B2, G1 and R4 read ENG_ATTEMPT's skip byte from pcrec's own row (the
predecessor `\n`, `memchr_form` true); the B1 class proved no offset-0 byte
there, so a switch to `proven0` would have dropped the byte (466 records,
fdb1) and moved artifacts (`(?m)^\n` alone: its one-byte pre-check would go
from `dominated` to `emitted`). Handled per D1c: D1c's form is a CONTEXT
stop, and what it proves is a context fact, not a span-0 byte. `mf_class`
gains `proven_prev` (`MF_CLASS_V` 2): "every candidate's PREDECESSOR byte
lies in it", written by `kit_class` for a FIND over one SET term at -1. On
the ATTEMPT route G1/R4 ask the MLINE site (DFA_ATTEMPT, `PCREC_FIND_NO_TABLE`,
offset -1) and read `proven_prev` (declared `CAND_ASKF_PROVEN_PREV` on
PRESENCE and RETRY); its one byte is the scanned byte, and a candidate found
at or after `start` puts it in the pre-check's window, which is the
soundness G1's identity needs. Zero movers on every sweep; the witness
`(?m)^\n` (dominated) is in `make test-memfn-finder`; SKB2-5 plants the
regression (DETECTED, §8).

### 5.2 fdb1's `kit.eps.findall.l64k`: does NOT hold

Rev 3 [C4]: "Each test now reads the floor of the regime its operands were
measured in". R0/R7 compare a `saving` key, derived (`ratio-complement`)
from `beta` slopes, and the `beta` card (`kit-grid@1`) is measured over
member-free single calls (subject streamed, slope 64Ki-1Mi): gridread's F3
regime, whose A/A p90 is `kit.eps.streamed.slope` (0.173%). fdb1 chose F1's
streamed find-all floor (3.365%) because it reproduced §3.5's predicted
movers, which is choosing a floor by its outcome. Corrected in 16770a07c:
`K_EPS` = `kit.eps.streamed.slope`, the synthetic sets carry that key, and
B4's predicted-mover manifest is regenerated with fdb1's own tool: 860
(arm, pattern) movers (was 817): the (2,0,0) cover's 43 sites R0 WALK →
R7 V1 (its measured saving 1.385% now exceeds the floor), 377 unmeasured
r2-shape sites R0 WALK → R7w WALK (no move). R0 and R7 are unrouted until
B4: zero artifact movers. §3.5's "285 + 15" prediction moves with it
(design text, main's/the kit manager's to re-state).

## 6. R-MS6, the arm-entry counter

The kit counts, the host names. With the harness lever on, pcrec calls
`mf_reach(art, stem)` once before the first define, the stem being its
reserved name `pcrec_harness_reach_<prefix>` (prefix placeholder, rendered
with the rest of the text, so the kit never inspects it). From then on each
site rendered by a ROUTED finder decision gets one counter slot per dispatch
arm (one arm while no dispatch is emitted, B4/B8), and its use writes, as
the arm's first statement, `{ extern unsigned long <stem>[]; <stem>[k]++; }`.
After the body pcrec calls `mf_reach_table`, which appends at file scope
the counts array, `<stem>_row[]` (each slot's finder row id) and `<stem>_n`.
Without the lever neither call is made: the default emission path is the
same code, so lever off is byte-identical by construction, and checked.

The check (`tests/memfn/run_arm_reach.sh`, inside `make test-memfn-finder`)
reads the counters from the RUNNING artifact through a driver written in
the script, never from the kit's records. Per fired row (D1 on `x+y`, D1w
under `--memfn=no-fd-d1` and on the VM hat `(x[a-z]+)y\1`, D1c on `(?m)^ab`)
it asserts: lever off, the harness build's artifact equals the shipped
compiler's and names no counter; lever on, the row's arm counts ≥ 1 on a
subject that enters it and 0 on one that does not (a start past the end, or
a first attempt that matches before MLINE's seek). The lever's fence
(compound.md §A.11) holds: no new global in `libpcrec.a`, and the check is
on `run_lever_fence.sh`'s allowlist. SKB2-2 (counter written lever-off) and
SKB2-3 (counter adds 0) are its plants. Not built: per-interval counters
(no dispatch exists yet); the M0 REACH floor itself is [MEASURE-SET]'s.

## 7. Proposed main-side diffs (main's files; not edited)

1. **C17 `tests/memfn/site_manifest.tsv`, the `site_kind` column.** Add a
   column `kind` (the consumer kinds a row's instances state), with C17
   checking each instance's stated kind against it:
   `PF	… 	kind=DFA_SCAN,DFA_HAT,HYB_PF,VM_ATTEMPT`;
   `MLINE	…	kind=DFA_ATTEMPT`;
   `PRE	…	kind=DFA_SCAN,HYB_PF,VM_ATTEMPT,DFA_ATTEMPT`; every other row `-`.
   The PF row's `companions` lose nothing (every listed function still
   exists; `pf_emit_skip`, `pf_find_kind`, `pf_moved_reseed_of` may join).
2. **C10 fixtures for the one-byte rows** (`memfn_sites.c`'s C10 /
   `tests/memfn/run_deleg_sites.sh`): one fixture per one-byte kind, each a
   `PcrecFind` through `find_site`: DFA_SCAN (`x+y`'s memchr, unbounded),
   DFA_HAT (`\B(?<!a)d`, bounded with a moved hook), HYB_PF (`(x+)y` under a
   hybrid), VM_ATTEMPT-presence (the PRE composite on a no-DFA VM route,
   `(x[a-z]+)y\1`'s pre-check) and DFA_ATTEMPT (`(?m)^ab`'s MLINE stop); each
   asserting the kit's `mf_result.row` (D1, D1, D1, -, D1c) and that the
   site states its kind. The kit-side twins already run in
   `finder_check.py` K (`byte1t`, `byte1vm`, `hat1`, `mline`).
3. **The landmark admission's input restated as facts** (`emit_dfa.c`
   `req_landmark_admits`, names and comments only): the input is the start
   set's PRIOR mass, h and K (D167 add. 1); the comment that prices "what
   the displaced scan skips" (~7920-7934 on main) becomes "the prior mass of
   the start set the displaced row tests". No code moves.
4. **`tests/axes/run_axes.sh`'s `--memfn=` arm**: `fd-d1` flips from
   ASSERT_ZERO to DIFFER with floor 1,004 (byte) / 985 (utf8) c-default, as
   emit_sweep now has it.

## 8. Sabotage (each solo)

Each row runs solo in the chain (`run_sabotage_matrix.sh <id>` /
`run_skb2.sh`); verdicts land in `build/land/verdict.txt` (`MECH <id>` and
`SKB2` lines), still running at hand-off.

| id | plant | expected (verdict in verdict.txt) | detector |
|---|---|---|---|
| S288 (re-aimed) | `one_byte` member test broken | DETECTED | test-cand-oracle / prechecks |
| S481-S485 (re-aimed to pffind.c) | walk `moved_close` dropped; memchr `moved_close` dropped; moved test inverted; guard dropped; NOP block dropped | DETECTED | emit_sweep identity + startset hat diff |
| S495 (re-aimed) | `dfa_cand_ppm_of` re-reads the row by name | DETECTED | `[cand-no-name-strcmp]` |
| S289 (re-aimed) | `DFA_PF_ONE_BYTE` row predicate | DETECTED | cand-oracle |
| S922 (new) | a finder row routed one step early | DETECTED | finder_check K/A |
| S1019 | (derived re-run) | DETECTED | — |
| SKB2-1 | D1 unrouted | DETECTED | finder_check K |
| SKB2-2 | arm-reach counter written with the lever off | DETECTED | run_arm_reach lever-off identity |
| SKB2-3 | counter adds 0 | DETECTED | run_arm_reach entering fixture |
| SKB2-4 | walk post-test dropped | DETECTED | arms pins + answers |
| SKB2-5 | `proven_prev` not filled | DETECTED | `(?m)^\n` dominated witness |

The SKB2 ids are placeholders for real `tests/mech` ids (OWED, §9).

## 9a. The chain still running at hand-off

`build/land/chain.sh` (tip c5808f920; `run_skb2.sh` and mech archive HEAD
at run time). Remaining: sweeps `vm`, `rwquest`, `variants`, `trace`; MECH
S288 S481-S485 S495 S1019 S922; SKB2; CTRACE build; ROUTED_CENSUS
(writes `build/land/routed_floors_measured.tsv`, the D1/D1c/D1w floors to
pin into `tests/memfn/row_floors.tsv`). Completion line: `CHAIN_DONE` in
`build/land/verdict.txt`.

## 9. OWED (heavy runs, the manager's slot)

| item | command | trigger |
|---|---|---|
| full `make test` | `scripts/perfrun --label fdb2 -- build/land/test.log` (from the worktree) | merge slot |
| mech derived rows (start-table re-run family) | `python3 -I docs/design/start_table/sabotage_anchors.py --step fdb2=285590dc6..lane/fdb2` then `bash tests/mech/run_sabotage_matrix.sh <each listed id>` | merge slot |
| G2 full | `make test-memfn-g2-full` | merge slot |
| N2 census (the D1/D1c/D1w `pcrec_floor`s, now PLACEHOLDER) | the N2 census (`tests/memfn/run_n2_sample.sh` / `n2_report.py --floors`) | merge slot; then pin `row_floors.tsv` |
| test-axes `--memfn=` arm (fd-d1 answer identity) | `make test-axes AXES="--memfn=no-fd-d1"` | merge slot |
| bench patterns in the sweep | `scripts/emit_sweep.py --patterns-file <bench list> --no-corpus …` (no committed bench pattern list found in this tree) | when main names the list |
| the G2 one-byte family (KW-10) | a G2 lane: count rule over generated sites with stated kinds, MLINE's generic shape; NONE's two items are B5's (F0 unbuilt) | B3 or a G2 lane |

## 10. Charter vs committed (row B2)

| chartered | committed | where |
|---|---|---|
| D1, D1c, D1w `routed` = 1 | yes | finder.c `fd_rows[]`, `fd_route`; finder_check K; rows.tsv |
| PR-1: SET term at every count, one member included, table offered | yes | `find_site`/`pf_find_of`; memchr rows serve a table_ref |
| PR-2: `empty`/`on_miss`, the `n − 1` bound, moved hook | yes | `PcrecFind.on_miss`/`.moved`, `mf_hooks.moved`, FLD_moved |
| PR-3: `site_kind`, categorical, DFA_ATTEMPT | yes | `mf_site_kind` (`MF_SK_*`), every builder |
| PR-4: `need` re-numbered, UNSTATED zero, stated by every builder | yes | `mf_need`; `pred_kinds` refuses; G2 + fixtures state it |
| PR-9: G1, R4, L4 switched to `mf_ask`; reader shadow retired | yes | `cand_ask`, `dfa_cand_scan`, `dfa_cand_ppm_of`, `start_landing_applies` |
| A11: landmark admission's input restated (names/comments) | NO, proposed as a main-side diff | §7 item 3 (main's file region; the brief listed it as main's) |
| KW-1 (D1), KW-2, KW-3, KW-4 | yes | pffind.c (guard, post-test, NOP block, moved hook) |
| KW-10 (the G2 one-byte family) | partial: count rule in finder_check K; NONE not built | OWED (§9) |
| A8: C10 fixtures, C17 `site_kind` columns | proposed diffs, not edited (main's files) | §7 items 1-2 |
| PR-10 (PF comment) unchanged, proven by `-fcomments` arm | yes | §2 SWEEP comments: 0 movers |
| zero-mover | yes, every arm except the declared `fd-d1` flip | §2, §2.3 |
| F-B1-3 | yes | §5.1, `proven_prev`, witness in `test-memfn-finder` |
| R-22 / R-MS6 arm-entry counter | yes | §6, `run_arm_reach.sh` 13/0 |
| fdb1 floor token checked | yes: wrong, fixed separately | §5.2, 16770a07c |
| Q-19: `PCREC_NO_REQ_SET_LEAD` alias, bit 45 untouched | yes (not touched) | `git diff 285590dc6.. -- lib/pcrec.h src/core/axes.def` shows no bit-45 line |
| declared trace delta | yes | §3 |
| no pcrec byte move without a stop | none found (no abi event) | §2 |
| sabotage SK-B2-n, each solo, DETECTED | yes (SKB2-1..5) + re-aims | §8 |
| CLAUDE.md files updated | yes | memfn/, memfn/include, memfn/src, src/gen, tests/memfn, cli, docs/design/memfn/r17b_prime |
