# Lane opt5d — [OPT-5] STEP 2 design note (two-pass fix / reverse-pass elision)

Chartered 2026-09-01 by Frank ("i see no downside"). DESIGN ONLY: one new
document (`docs/design/opt5_step2_twopass.md`) plus this log. Nothing under
`src/` or `tests/`. Launched under the box HOLD (`worktrees/opt5d.lift`
absent); no `make`, no gcc, no `build/pcrec`, no test scripts — every number
in the note is cited from a measurement document, never re-measured here.

## Reading order completed

1. `docs/dev/plan.md` [OPT-5] row in full (STEP 0/1, STEP 2/3 candidates,
   RESIDUAL-GAP candidate), plus [ENG-ABS], [OPT-2], [ENG-COUNT], [OPT-VMLIT],
   [OPT-SIMD], [ART-SIZE], [OPT-4.1]/[OPT-4.2] rows.
2. `docs/dev/opt2_anchored_match_measurement.md` — the reverse pass is ~50 %
   of DFA cost on every matching subject; NOREV isolation 2.077x -> 1.046x,
   short emails 1.207x -> 0.571x.
3. `docs/dev/opt5_step0_profile.md` — the dependency-chain mechanism.
4. `src/opt/scanedge.c` header (criterion + five preconditions + the
   interior-deletion argument) and its `member_ok`/`shaped`/`in_degrees`.
5. `src/gen/emit_dfa.c` — `emit_unanchored` (the forward/reverse pair),
   `emit_scan_edge`, `emit_scan_loop`, `dfa_dir_forward`/`_reverse`/
   `_anchored`, axis G (`dfa_matches`), `anch_start`, `unanch_start`,
   `attempt_cand`; `src/gen/CLAUDE.md` [ENG-ABS] AXIS G section.
6. `docs/spec/match_api.md`, `docs/spec/tuning.md`.
7. `/home/duxevents/pcrec-bench/docs/dev/outbox_to_pcrec.md` O-12 (READ-ONLY)
   and its ledger `2026-08-31-opt5-step1-acceptance-a7e0bdf.md`.
8. `docs/dev/decisions.md` D76/D77/D80/D82/D91; `docs/dev/learnings.md` §3.

## Findings that bear on the plan row's own text (detail in the note)

- **F1** Site (a) is ALREADY BUILT. `[ENG-ABS]`'s second mechanism merged
  dfd112b (abi 10) and is battery-proven: `<prefix>_match`'s `unwrapped` form
  runs the third (anchored) machine from `ctx->pos` with **no reverse pass**.
  STEP 2 has nothing to add at that entry.
- **F2** The plan row's "start = end - count is already in a register at loop
  exit" is FALSE of the emitted code: `scan_run_length` is block-scoped inside
  the edge's own `if`, and an UNBOUNDED edge emits no counter at all.
- **F3** `unanch_start`'s `start_acc` is a deliberate WIDENING whose own
  comment says not to cite it as a premise; reusing it to gate the elision is
  a miscompile (`$`-shaped witness).
- **F4** The acceptance instrument's nine rungs are the
  `large-subject-throughput` (find-all) band, not a "match" band.

- **F5** The `abi` ritual's "FOUR sites" is incomplete: `docs/spec/match_api.md`
  line 159 is a FIFTH reader of the number and is already stale at `13` after
  `[CC-CLANG]` (`c657ae9`) moved it to `14` at line 1602.

## The recommended split (detail in §1.3 of the note)

- **STEP 2** = the START-PINNED SEARCH. Where the forward machine's start state
  accepts unconditionally, D3's accept-pruning kills every later start before
  the first byte, so `match_start_position == search_from` always and the
  reverse machine is not emitted at all. Provable today, no new machine, covers
  the whole nine-rung instrument, and is a size event as well as a speed one.
- **STEP 3** = construction-time scan-edge synthesis, plus the forward-tracked
  ORIGIN that multi-edge `end − Σcount` elision needs. Population today: empty
  (r48sem — the forward machine grows 0 edges on embedded shapes).
- **Its own row** = the VIEW-TOLERANT SCAN EDGE, which is what bench ask (iii)
  actually wants; its trigger already exists (the two whole-form artifacts at
  93.7 % of the `[ART-SIZE]` cap, owning both surviving warns).

## Identifiers verified against the tree at `ae3e6ca` (read, never executed)

`state_acc_any` (emit_dfa.c:2052), `dfa_needs_seed` (:2064), `start_acc`
(:2445), `.abi = 14` (:1441), `PCREC_NO_SCAN_EDGE = 1u << 21` (lib/pcrec.h:451,
the last allocated bit — so bit 22 is free), `member_ok`/`shaped`/`in_degrees`
(src/opt/scanedge.c), `PCREC_MAX_SCAN_EDGES` (src/core/limits.def:181).

## WIP timeline

- 2026-09-01: worktree `lane/opt5d` created from `ae3e6ca`; keepalive cron
  every 27 min doubling as the `.lift` poll; reading complete; note drafting.
- 2026-09-01: `docs/design/opt5_step2_twopass.md` written (§0–§9) and
  `docs/design/CLAUDE.md` given its entry. Hold still in force at delivery;
  nothing in this lane needed the lift, and nothing was executed.

---

## Revision 2 session (2026-09-02) — r49 worked

**Setup.** `git merge main` alone in its own command: clean merge of `05c984b`
(abi 15, S217 merged, D93/D94 landed, the r49 review file committed), no
conflicts, as the brief predicted. Landed lane/opt5m2's premeasure memo
(`docs/dev/opt5_step2_premeasure.md`, `docs/dev/opt5m2_m2_changed_patterns.txt`)
with two `docs/dev/CLAUDE.md` entries. The `[OPT5M2-PROBE]` `src/gen/emit_dfa.c`
hunk was deliberately NOT checked out.

**Build.** ONE `gnutimeout 900 make -j2`, exit 0, first try. Every
`build/pcrec` invocation wrapped in `gnutimeout 60`. No `make test`, no
`test-codegen`, no battery, no sanitizer target.

**Witnesses emitted and verified against the review's claims** (all from this
build, all stamps read directly):

| pattern | what it proves | result |
|---|---|---|
| `[a-z]{0,8}\|9$` | A1 witness (i): scan edge above the probe | REPRODUCED verbatim, edge opens the loop, probe 8 lines below the view select |
| `a*\|\b9` | A1 witness (ii): `wctx` alone demotes the probe, no view select emitted | REPRODUCED verbatim |
| `[a-z]{0,64}` | the `scalar-plain` control: probe FIRST | REPRODUCED |
| `\Ka*` `-fprefilter` | B1: a `\K` machine through this emitter | REPRODUCED — `RX_ENGINE "vm"`, `is_accepting[2] = {1,1}`, start-accepting |
| `a*b` `-fno-anchored-dfa` | C1: `tr[fs]['a'] == fs` | REPRODUCED — `next_state[6] = {0,0,3,…}`, legend state 1 = `"b"` ACCEPTING, `_match` body as quoted |
| `[a-z]{4096,}` | M9: `cls-atleast-4096` must not move | CONFIRMED — `PREFILTER "byte-class"`, `is_accepting[4] = {0,0,1,1}`, start does NOT accept, predicate declines |
| `[a-z]{0,64..32768}` ladder | the nine rungs' `RX_DFA_MATCH` split | 64–2048 `unwrapped`, 4096/8192/16384 `search-filter`, 32768 VM; all PREFILTER `none` |
| `(?:[a-z]{0,8192})\z` | M3 / B6: the whole form is view-declined | CONFIRMED — `byte-class-bounded`, `SCAN_EDGE "none"` |

**Code line numbers verified in this tree** (all cited in the note): `dfa_accs`
`:3572`, `acc_viewed_applies` `:3511`, `emit_scan_loop`'s calls `:4696`/`:4697`/
`:4699-4703`/`:4714`/`:4715`/`:4716`/`:4717`, `dir_fwd_skip` `:3992-4014`,
`emit_scan_edge` `:4473-4568`, `acc_emit_tail_by_class` `:3530-3570`,
`unanch_start` `:2487-2503`/`:2542-2547`/`:2581`/`:2596`, `dfa_needs_seed`
`:2161-2166`, `dfa_premul` `:2205-2215`, `seed_emit_constant` `:3496-3502`,
`dfa_table_name` `:2664-2666`, `dfa_scan_edge_name` `:2706-2715`, axes H/I
`:4317`/`:4349`, `.abi = 15` `:1514`, `member_ok` `src/opt/scanedge.c:188-194`,
the loop-order sentence `:107-109`.

**One correction to the review's own line numbers, minor:** `dfa_table_name`'s
`rdfa` read is at `:2665`, not `:2664` (`:2664` is the FORWARD read). The note
cites the pair.

**The hard item (r49 item 1) is done and the proof holds.** The repair is not
cosmetic: rev 1's Claim A was doing work it could not do (it was carrying
`caps[0][0] = search_from`, which actually comes from Claim B). §3.2.1's
proof enumerates every recording site and shows each either records or cannot
advance, so *some* accept ≥ `search_from` is always recorded.

**The item I could not fully discharge: r49 item 8 (S219's synthetic witness).**
I worked six candidate shapes and none reaches P3's discriminating branch. The
derivation in §5.6b argues the population is EMPTY on `ENG_UNANCH`, not merely
unpopulated. The brief allowed this branch; the row ships declared `UNREACHED`,
and §7 item 10 (count P3 EVALUATIONS, not declines, on both axes) is the
measurement that would settle it.

**O-14 had NOT landed** when this revision was finished (checked twice, last at
11:28 EDT 2026-09-02; the outbox's last write is 2026-09-01 18:47 and its
newest message is `## O-13`). Every scratch-tier number in §0 carries an
`[O-14 PENDING — manager fills at merge]` marker.

**Commits, in order:** memo landing, header, §0/§1.1/§1.2, §1.3+§3.2/§3.3,
§3.4/§3.5, §4, §5.2/§5.4/§5.5, §5.6, §5.7/§6/§7, §8/§9, §10, §2/§5.1/§5.3,
design/CLAUDE.md, report. Nothing under `src/` or `tests/` is touched; the
lane's whole diff against main is six documentation files.
