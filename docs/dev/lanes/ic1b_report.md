# ic1b — [INLINE-C] stage 1b: the callout call site, extern-bound

Lane ic1b (opus), 2026-10-26, branch `lane/ic1b` off main `43414ddac`
(stage 1a's `kindrow.def` included). Design: `docs/design/inline_c.md` §1 and
§9.1 "Stage 1b"; rulings `docs/design/plan_row_bodies/INLINE-C.md`. Build go:
Frank 2026-10-26 ("Just get the feature done"). Module `callouts`,
[M4-CALLOUTS] step 2. **abi 87 -> 89, PROVISIONAL**: written renumberable (one
constant plus the readers listed in §6); 88 is stage 0's (lane ic0). The
"traps on" `rx_matchfn` comment was not touched (ic0's).

## 1. What was built, per scope item of §9.1

| scope item | where | state |
|---|---|---|
| `(?C)`, `(?Cn)`, `(?C"name[,attrs]")`, every PCRE2 delimiter | `src/parse/mod_callouts.c` | built; `` ` ' " ^ % # $ {} `` all accepted (shapes.rxt) |
| the malformed-`(?C` row | registry row `(?Cx)` (REJECTED, fixed) + the port | built; `(?Cx)` `(?C256)` `(?C1x)` `(?C!x!)` refused as malformed with `callouts` on and off (D17); a truncated `(?C` too |
| `callout N ATTRS` line and `--callout N:ATTRS` | `src/parse/rxt_source.c`, `rxt_schema.def`, `cli/main.c`, `tests/harness/run.sh` | built; BLOCK-scoped line (see question Q1) |
| `A_CALLOUT` and its attribute row (§1.8) | `src/core/kindrow.def`, `internal.h` (`pcrec_ast_row` picks TEXT ANY per node for `consume`) | built |
| `VE_CALLOUT`'s producer, `vm-slots` view source (§1.2) | `src/gen/emit_vm.c` `vm_callout` | built: step charge, stack `rx_ctx`, `ncap` = groups + 1, slot-0 save/set/restore, call, return table |
| binding rows 2-3 (§1.4) | `rx_callout_<n>` / `rx_callout_<name>`, `extern const rx_callout_ref` in the header | built |
| site view: every group published at close and kept under `--no-captures` | `KREADS_ALL` in the marked set (`src/opt/atomic.c`) | built; A5 witness checked |
| `callsite_rows[]` lifted to the shared emit layer, `conv` column, rows 9-10, row order (§1.6) | `src/gen/callsite_rows.{c,h}` | built; compound artifacts 97/97 byte-identical vs the base at the time of the lift |
| the callee-give-up bit (§1.6, D8) | run state `callee_gave_up`, `emit_comb.c` tier test | built; checks.c's FRAMES-in-tiered-artifact check |
| step charge per fire (§1.11) | `vm_callout` | built; `match_api.md` §4¶1 says STEPS counts fires |
| `NFA_ERASED_CALLOUT`; `pf_admits` row declining the prefilter (§1.8) | `kindrow.def` ERASE column; `src/opt/select_engine.c` row `callout` | built; `-fprefilter` refuses by name |
| `PF_KIND_CALLOUT`; conjunct halves retired, S475/S496 re-scoped (§1.8) | `src/facts/`, `emit_dfa.c` comments with the recorded argument | built; S475/S496 still declared UNREACHED (verbs) |
| firing-class derivation, IR `callouts` section, `once` check (§1.10) | `src/opt/callout.c`; `emit_vm.c` listing (7 columns) | built; every §1.10 example row is a listing expectation (deviation D3: reason text) |
| the position table (§1.9) | `src/opt/callout.c` | built: lookbehind, conditional condition (via module `conditionals` unbuilt), subroutine/recursion-reached group refused |
| namespace rows (row 2 enforced, `__` refused) | `src/core/compile.c`, parser | built |
| `--emit-main`'s refusal | `src/opt/callout.c` | built |
| the fixed-literal family | `emit_dfa.c` `emit_callout_surface` (`RX_PASS 0`, `RX_FAIL (-1)`, guarded) | built |
| `_CALLOUTS` and `_CALLOUT_BINDINGS` | `src/gen/stamp_kinds.c` | built |
| `PCREC_ERR_ABORT` reserved in the spec | `match_api.md` §4¶1 | done (spec only, value -17) |

## 2. Deviations and readings

- **D1. No independent backtracker** (the brief overrides §9.2's backtracker
  leg). The ORACLE is libpcre2 10.46 with `PCRE2_NO_AUTO_POSSESS |
  PCRE2_NO_START_OPTIMIZE | PCRE2_NO_DOTSTAR_ANCHOR`, driven by the SAME
  behaviour table pcrec's bindings call (`tests/callouts/behaviors.h`). The
  behaviour is the test's input, not a shared mechanism; the two matchers
  share nothing else.
- **D2. Numbered declarations travel an internal channel.** `--callout` and
  the `callout` line reach the compile as `PcrecEmitIn.callout_decls`
  (`pcrec_compile_callouts`), not as a `pcrec_options` member: library
  options wait for [IFACE-PUSH]. A library caller cannot declare a numbered
  callout's attributes yet (a named callout carries its own).
- **D3. The class reason and the `once` refusal are generic.** The listing's
  `note` says "a choice point before the site can be resumed and reach it
  again" / "inside a repeat whose maximum is 2 or more"; the `once` refusal
  says "a quantifier, alternation or call before it can be backtracked into;
  make the quantifier possessive (X*+) or wrap it in (?>...)". §1.10's
  examples name the construct and its offset (`the quantifier \d+ at offset
  1`). Not built: naming the construct needs the walk to carry the node it
  found. Small follow-up if wanted.
- **D4. The spec's PCRE2-sensitivity examples are MEASURED values** with this
  directory's behaviours (`match_api.md` §11.6¶2): `(\d+)(?C"even")` on
  `1234` is no match at libpcre2's default flags and `[0,3)` with the three
  flags off; `(?s).*(?C"vetostart")x` on `axbx` is no match by default and
  `[1,4)` with them off; pcrec answers `[0,3)` and `[1,4)`.
- **D5. S-IC2's plant** ("an enclosing group is left unmarked") is spelled as
  "group 1 left out of a site's marked set"; the witness's enclosing group
  is group 1. **S-IC20's detecting suite** is `brefidentity` (the
  backreference-free identity gate on all three axes): my choice, not
  measured yet (job 541).
- **D6. The mech arm `callouts` runs the generated differential at 300
  patterns (floor 250)**, not 1,200: one run per row, and every row's
  witness is a named check.
- **D7. test-axes' callouts floor** ([r1 T6]): `tests/axes/run_axes.sh` fails
  an axis that reached fewer than 50 `tests/callouts/` cases (run or
  refused with a documented text) on a whole-tree sweep. `--engine=dfa` and
  `-fprefilter` refuse a callout pattern with texts their REFUSAL_PATTERN
  rows already hold.
- **D8. The `.rxt` harness manifest** is new format surface
  (`rxt_format.md` §6¶3-¶4): `harness.manifest` beside the `.rxt` files,
  one directive `link FILE`; sources compiled with `-include` of an artifact
  header. run.sh links the objects at all four link sites (batch, solo
  relink, per-pattern, target).

## 3. Tests

`tests/callouts/` (`make test-callouts`, in `TEST_SECTIONS`; CI shard 2,
weight ESTIMATED 120 s; mech arm `callouts`). Six arms; numbers from the
lane's own runs on this tree:

| arm | what | lane result |
|---|---|---|
| 1 corpus | `shapes.rxt` through run.sh, bindings via the manifest | 59/59 cases |
| 2 oracle | `verify_callouts.py`: every cell vs libpcre2 (opts off) | 49 cells + 10 group lines agree, 0 disagree |
| 3 generated | `gen_diff.py`, seed 20261026, 1,200 patterns x 6 subjects | 1,200 compiled and compared, 7,200 cases, 0 disagreements, 0 class-bound violations, 0 oracle errors (a 200-pattern run: 155 artifacts carried a checked bound) |
| 4 driver checks | A2 x3, A2b, A4 x2, A5 x2, enclosing group, STEPS and FRAMES give-up (tier hook: 0 escalations), step charge, DT-4.1, an artifact as a `consume` callee x2; traps: over-long, mid-character, `W_PRED` returning 1 | 15/15 + 3/3 traps (exit 132) |
| 5 class table | §1.10's 11 examples as listing expectations; `once` accepted on classes 1-2, refused with its reason on class 3 | 22/22 |
| 6 refusals | 4 malformed forms x module on/off, `__`, `--emit-main` | 10/10 |

Also: `tests/codegen/run_ir_listing.sh` (callouts term flipped to a
three-surface comparison, a callout fixture added, 17 baselines re-captured,
only the section header and empty note moved, one new baseline): 164/164.
`make strict` clean. `make test-ci-shards` 9/9. Registry count 142 -> 143
(the `(?Cx)` row). Compound artifacts 97/97 byte-identical vs the base.

**Sabotage rows** (reach probes 14/14 REACHED on the clean tree; detection
OWED, job 541):

| id | design | plant | witness |
|---|---|---|---|
| S1646 | S-IC1 | `fail` row routed to success | vetoing shapes |
| S1647 | S-IC2 | group 1 left out of a site's marked set | enclosing-group check |
| S1648 | S-IC3 | possessify's FIRST fold reads every site as empty | D1/P7 shape |
| S1649 | S-IC3b | `fst_row` reads a `W_PRED` path as empty | D1/P7 shape |
| S1650 | S-IC4 | give-up row collapsed to fail | give-up checks |
| S1651 | S-IC5 | slot-0 restore dropped | A4 |
| S1652 | S-IC6 | row 10 (bound) removed | overlong/midchar traps |
| S1653 | S-IC6b | req and start-set read a `consume` site as empty (two files) | `a(?C"two,consume")b`, `(?C"digits,consume")x` |
| S1654 | S-IC11 | row 9 (W_PRED trap) removed | pred1 trap |
| S1655 | S-IC19 | a failed attempt re-run once at the same start | gen_diff class bound |
| S1656 | S-IC20 | marked set unconditional | brefidentity gate |
| S1657 | S-IC25 | a site's reads omitted from the marked set | A5 |
| S1658 | S-IC26 | step charge dropped | step-budget check (by hand on the artifact: 0 instead of STEPS) |
| S1659 | S-IC27 | `once` accepts a site inside a repeat | class-table arm |

## 4. Spec hunks (D80)

`match_api.md`: §1¶6a/¶6b (the `RX_PASS`/`RX_FAIL` family), §2¶6, §4¶1
(STEPS counts fires; `PCREC_ERR_ABORT` -17 reserved), §4¶3, §4¶4 (the
temporary multiplier), §4¶10 + ¶10b (`conv`, rows 9-10), §5¶7, §6.3 rows
(`_CALLOUTS`, `_CALLOUT_BINDINGS`), §10.9¶6, NEW §11 Callouts (11.1-11.8),
the abi readers. `cli.md`: §1.6 namespace row 2, §1.10¶2 (`--emit-main`),
NEW §1.21 `--callout`. `rxt_format.md`: §1.5¶13a (the `callout` line), §6¶3-¶4
(the harness manifest). `ir_listing.md`: §3.7 (seven columns). 
`pattern_language.md`: NEW §7.11 Module `callouts`, §8.1 row removed, §9¶9,
index row. `docs/pcre2_compliance.md`: Callouts status `OK-GATED`, a headline
bullet, the `(?C1)` annotation rewritten (store + regenerated block).
`docs/dev/history/abi_changelog.md`: the 89 entry.

## 5. Bench `[inbox]` note TEXT (not written; the manager's)

> pcrec now compiles callouts ([INLINE-C] stage 1b, abi 89 provisional).
> The bench row `ca(?C1)t` moves from "did not compile" to COMPILES but does
> not LINK: the artifact declares `extern const rx_callout_ref
> rx_callout_1;` and the link fails with an undefined reference to
> `rx_callout_1` unless the bench supplies one, e.g. `static ptrdiff_t
> pass(const rx_ctx *c) { (void)c; return 0; } const rx_callout_ref
> rx_callout_1 = { pass, NULL };`. With a pass-through binding the row
> measures the VM plus one call per fire; the pattern is VM-only (no
> prefilter yet). libpcre2's side of such a row needs a callout function set
> too, or it measures a different thing.

## 6. abi readers moved (renumber at landing by changing each)

`src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`; `docs/spec/match_api.md` §1 guard
block (three lines), §6¶17 sentence, §6 `rx_info` row 1;
`tests/mech/sabotages/S693_abi_not_bumped.sh` (BEFORE/AFTER);
`docs/dev/history/abi_changelog.md` (entry); `tests/codegen/
run_recursion_identity.sh` FILEPIN self-pinned to `cfdf8f5fd` (the lane's
last src commit at the bump; the manager re-pins to the merge).

## 7. Open questions

- **Q1. The `callout` line's scope.** §9.1 says "the `callout` head line";
  built as a BLOCK line. Reading (a), a HEAD line: one declaration per file,
  applying to every block whose pattern has callout N, which makes two
  patterns in one file share a number's attributes and lets a config
  compose it. Reading (b), a BLOCK line (built): the declaration sits with
  the pattern it describes; no config composes it. Leaning (b): a numbered
  callout's attributes are a fact about one pattern's site.
- **Q2.** D3 (the reason text naming the construct and offset): build it now
  or file it?

## 8. OWED runs (queued by the lane, last act)

| job | what | verdict line(s) |
|---|---|---|
| `540-ic1b-test` | build, strict, the zero-mover census (`docs/dev/lanes/ic1b/movers.py`: base `43414ddac` vs this lane at abi 87, every corpus pattern + 336 bench patterns, 5 cells; only a `(?C` pattern may move), make test (80 sections) | `job.log.strict`, `job.log.movers` (`movers: DONE ... unexpected=0`), `job.log.make` (`sections ran: 80/80`) |
| `541-ic1b-mech` | 17 rows: S1646-S1659, S475, S496, S693 | `== mech run COMPLETE: 17 rows (... unreached: 2 ...)` (S475/S496 declared) |
| `542-ic1b-axes` | run_axes.sh (every axis, the callouts floor) + the form census | `job.log.axes`, `job.log.census` |

All three answer not-ready after 21:00 / 21:30 (nothing past 23:30). Logs:
the job directories under `worktrees/.boxqueue/`.

## 9. STATE AT HANDOFF

- Branch `lane/ic1b`, last commit: see `git -C worktrees/ic1b log -1`.
- Rulings file `docs/dev/lanes/ic1b_rulings.md`: "(none yet)" at every
  checkpoint; no ruling applied.
- Nobody else edited `src/gen/emit_compound.c` during the lift.
- Not done: stage 2+ (embedded C), `RX_CALLOUT_PCRE2` (stage 5), the
  library declaration channel (D2), D3's richer reason text.
