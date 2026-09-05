# Lane formchar1 — [FORM-CHAR] STEP 1: the `fold` char-match form (VM emitter)

Branch `lane/formchar1`, worktree `worktrees/formchar1`, 2026-09-05.
Basis: `docs/dev/form_char_step0.md` (family A closed by compiler evidence),
the `[FORM-CHAR]` plan row, D82's ritual. Charter: where a VM class is
exactly an ASCII fold pair, emit the folded compare; everything else stays.

## 1. Design

**The emission rule.** `vm_cls_test`'s shape choice was three inline
conditions in that function plus a SECOND inline spelling of the same
conditions in the class-bitmap table-emission loop (`pcrec_emit_vm`, "the
class bitmaps"). Both now read ONE classifier, `vm_cls_shape(v, bits, &lo,
&hi) -> {ALL, SINGLE, RANGE, FOLD, BITMAP}` — so a class whose test
compiles to a compare can never leave an unread table behind, and a class
whose test reads a table can never find it missing (the duplicated
derivation was a latent drift this change retires in passing). The FOLD arm
emits `(byte | 0x20) == lower`; the table loop emits a bitmap only for
BITMAP-shaped classes; the `<PREFIX>_VM_CLS_FOLDS` stamp is the same
classifier aggregated over the pool. The enum's comment reserves member
space for `[FORM-CHAR]` objects (4)/(5) (`utf8-simple-fold`,
`utf8-full-fold`, M5.0's stages); nothing is built for them.

**The recognizer predicate.** `count == 2 && (lo ^ hi) == 0x20 && lo >= 'A'
&& lo <= 'Z' && !PCREC_NO_CLS_FOLD`. Ordered after the RANGE check (a
0x20-pair is never contiguous, so the two cannot overlap). The deny flag is
tested at the classifier — the one derivation — on `-fno-alt-island`'s
precedent (the VM side has no candidate-list `deny` field to ride).

**The identity argument.** `(b | 0x20) == (lo | 0x20)` is true for exactly
`b ∈ {lo, lo | 0x20}` — the set's own two members — so the fold compare and
the bitmap read are the same predicate over bytes; no answer can move.
Chain shape is untouched by construction: the change is confined to the
test EXPRESSION a site emits and the table pool, never to the sites, labels
or rungs around them ([OPT-VMLIT]'s chains survive verbatim).

**One deliberate narrowing, flagged for review.** The compare would be
exact for ANY 0x20-pair (e.g. `` {@,`} ``), letters or not; the brief's
recognizer says "both letters" and that is what shipped. The letters
conjunct makes the form mean what `[FORM-CHAR]` object (2) defines
(ascii-fold, what D23's caseless folding produces) rather than "any
two-member compare trick"; widening is a one-conjunct change if a
measurement ever wants it. Against the general-mechanisms rule I read this
as choosing the general FACT (the fold pair) over an accidental wider
population, not as a special case — but it is a judgement call, so it is
named here rather than buried.

## 2. The D82 ritual, item by item

- **Stamp**: `<PREFIX>_VM_CLS_FOLDS`, §6.3 family (b), an activity COUNT on
  `RX_VM_ALT_ISLANDS`' precedent — unconditional on every VM artifact
  (0 spelled), never on a pure-DFA artifact, no `rx_info` mirror (D77).
  One derivation, two readers: the classifier writes the count and the
  emitted text carries the distinct fold constants a check can count.
- **Deny flag**: `-fno-cls-fold` / `PCREC_NO_CLS_FOLD` (bit 24) — lib/pcrec.h,
  cli/main.c, `--list-axes` row (`cls-fold`, activity-count shape), and the
  `strategy_denials` mask (the axis changes no answer; a fold-free artifact
  is byte-identical under the flag — verified by the identity gate's new
  converse arm corpus-wide). `tests/registry/axes_registry_check.sh`: 99/0
  with the row; `tests/axes/run_axes.sh` derives its flag list from
  lib/pcrec.h bits, so the axis joins `make test-axes` with no list edit.
- **Answer identity**: `tests/axes/run_axes.sh AXES="-fno-cls-fold"`,
  default vs denied over the whole corpus (the fold-bearing population
  rides it, including every `flags i` cell). RESULT (2026-09-05, manager's
  window, PROCS=4, CC=gcc-16, 2,200 s wall): **OK —
  keys_base=22488 keys_axis=22488 agree=22488, mismatches=0, lost=0,
  gained=0, budget-bound=0, refusals 0/0**; the run's PC-4 live-libpcre2
  oracle cross-check 0-failure on both arms. Log:
  `axes_clsfold.log` (session scratchpad; summary line quoted here is the
  record).
- **Form-census floor**: `run_form_census.sh` collects
  `RX_VM_CLS_FOLDS` as banded tokens (`>0`/`0`) on both populations and
  floors them — measured 11 default-axis / 23 vm-axis corpus patterns
  stamp folds > 0; floors 6 (D) and 12 (V), K35-generous. The default-axis
  population is small because a capture-free caseless literal routes to
  the DFA; the vm-forced population is the wider one the stamp serves.
- **Sabotage row**: S228 (`tests/mech/sabotages/`), the fold form's unsound
  direction — the recognizer widened to ANY two-member class, so `[ac]`
  takes the fold compare and loses `'a'` / admits `'C'`. Detector is the
  new `tests/base/cls_fold.rxt` (58 cells, every expectation python3-`re`
  verified; fold pairs AND nonpair controls in one file, capture-bearing so
  the default engine is the VM). MEASURED via a solo single-row mech run:
  DETECTED, reach:ok(1/1), corpus:7fail/51pass, fold-pair blocks green.
  SAB_REACH probes BOTH recognizer arms from birth.
- **Spec hunks (D80)**: `docs/spec/tuning.md` §2.22 (the contract);
  `docs/spec/match_api.md` §6.3 `_VM_CLS_FOLDS` entry + the family (b)
  list + both `rx_info.abi` sentences.
- **abi ritual (D76/D94)**: 22 -> 23 at `emit_dfa.c`'s one `.abi` site,
  with a per-artifact-kind comment. D94 grep for readers of 22 found FIVE
  sites, all moved in this change: the `.abi` stamp itself,
  `run_codegen_tests.sh`'s `ABI_EXPECT` + its bump narrative (clause
  appended), match_api.md's §6 general-rule sentence, match_api.md's
  reflection-facts bullet, and `run_recursion_identity.sh`'s (B) FILEPIN
  (re-pinned to this lane's last src commit in a follow-up no-src commit,
  [ENG-ISL]'s lane precedent; the manager re-pins to the merge). The
  narrative in the emitter comment notes the merge may renumber if a
  concurrent lane's abi event serializes ahead (utf8s2).
- **Identity gate (A)**: the fold is the SECOND change ever to move the VM
  program region, so (A)'s island excuse generalizes: a moved region is
  excused IFF denying exactly the stamped region-moving axes
  (`-fno-alt-island` and/or `-fno-cls-fold`, per the artifact's own
  stamps) restores the PINNED region byte for byte; both converse
  directions asserted per axis (stamped-but-deny-is-a-noop, and
  unstamped-but-deny-moves — the fold's converse scoped to VM artifacts,
  since the flag's one consumer is `vm_cls_shape` and a DFA artifact is
  byte-identical under it by construction); `FOLD_PATTERNS` is the
  enumerated non-vacuity manifest (4 default-axis corpus patterns spanning
  the recognizer). Gate run: see §4.

## 3. Measurements

**Sizes, SHIPPED emitter** (`(?i)abcdef`-equivalent `-i --engine=vm`
witness, gcc-16 -O2 -c, Mach-O on this box so `.text`+`.rodata` read as
`__TEXT`): fold 1,072 B vs denied 1,552 B (-31%), the six 32-byte class
tables gone entirely (0 `class_bitmap` declarations vs 6 tables + 12
mentions denied). Step-0's family-A direction (-38% ELF `.text`, `.rodata`
deleted) reproduces from the shipped emitter; the exact ELF numbers
belong to the Linux box. **The size log** (`docs/dev/artifact_size_log.tsv`)
is NOT regenerated here — it regenerates on the Linux box at the next
battery, per the brief.

**Recognizer census** (whole corpus, both engine requests, this lane's
sweep): 11 default-axis / 23 vm-axis patterns stamp `RX_VM_CLS_FOLDS > 0`.
Recognizer edge cells verified by hand: `[Aa]`, `(?i)k`, `[Zz]` fold;
`[ac]` (non-pair) and `` [@`] `` (non-letter pair) stay bitmap; denied
build restores bitmaps and stamps 0.

**Witness answers**: `(?i)abcdef` fold build 4/4 (`abcdef`/`ABCDEF`/
`AbCdEf` match 0 6, `xyz` nomatch).

## 4. Validation record

- `make strict CC=gcc-16`: clean.
- `tests/registry/axes_registry_check.sh`: 99 passed / 0 failed.
- `tests/harness/run.sh tests/base/cls_fold.rxt`: 58/58;
  `verify_rxt.py`: ALL CHECKS PASSED.
- mech single row S228: DETECTED (figure above), 0 anomalies.
- `make test-codegen` (CC=gcc-16): 103 passed / 5 failed — and the SAME
  FIVE fail on an unmodified MAIN tree on this box (verified by running
  `run_codegen_tests.sh` + the anchor script there read-only): OS-0b's
  two-engine compile trio, [K24]'s de-sugar control, [SABANCHOR]'s S199
  stale anchor (main: 223 rows, 1 stale; branch: 224 rows, same 1 —
  S228's own anchor resolves). All five are inherited Mac-box residuals
  (§5 items 2/6), ZERO from this branch. Every check my change touches is
  green: the abi expectation reads 23 on both engines, the bump narrative
  parses, rule 3's extractor still reports exactly one distinct
  membership test, and `run_dfa_stamps.sh`/`run_trie_identity.sh` (500
  patterns × 2, `-i` included)/`run_offset_skip.sh`/`run_size_term.sh`/
  `run_scan_edge_census.sh`/`run_n1_budget.sh` all pass in full.
- `run_form_census.sh` (PROCS=4): result in §4a below.
- `run_recursion_identity.sh`: full run NOT taken here (whole-corpus; see
  the gate-machinery bullet below).
- `run_axes.sh AXES="-fno-cls-fold"`: **GREEN** — 22,488/22,488 cells
  agree on the denied arm against default, 0 mismatches/lost/gained/
  budget-bound, PC-4 oracle cross-check 0-failure both arms (§2's answer-
  identity item has the full line).
- Gate-machinery witnesses (hand-driven, this box): a fold-stamped
  artifact's program region DIFFERS under `-fno-cls-fold`
  (`(?i)(?>abc)`, folds=3) and a zero-stamped VM artifact's is
  byte-IDENTICAL (`(a)(b)c`, folds=0) — the two converse directions the
  gate asserts, plus `bash -n` on the edited script. The FULL
  `run_recursion_identity.sh` run (5 axes, two reference builds) is a
  whole-corpus job and was NOT run in this lane's window — it is owed at
  the merge (it rides utf8s2's queued "identity gate full arm" acceptance
  or its own slot, the manager's call), with the FILEPIN re-pinned per §2.

### 4a. Form census run

**GREEN** (PROCS=4, 295 s wall, EXIT:0, every floor OK including the two
new ones): `D:RX_VM_CLS_FOLDS=>0` = **16** against floor 6,
`V:RX_VM_CLS_FOLDS=>0` = **28** against floor 12 (the census's
`--features all` per-artifact banding counts a few more than this lane's
own pre-landing sweep's 11/23 — same direction, comfortably above both
floors either way; bands: D 16 `>0` / 1,501 `0`, V 28 `>0` / 2,593 `0`).
Every pre-existing floor also OK on this tree.

## 5. Deviations and findings for the manager

1. **[MACPORT] mech row filter** (`run_sabotage_matrix.sh:2169`) used
   `grep -P`, which BSD grep rejects with a usage error — on this box the
   matrix assembled ZERO rows and the completeness check scored every
   requested sabotage a lost measurement. Fixed in its own commit (ERE +
   `$'\t'`); found because S228's run needed it. Worth a Linux re-run of
   any row to confirm the spelling is GNU-clean too (it is plain ERE, so
   it should be).
2. **Pre-existing, unrelated**: `tests/captures/structure_anchors_misc.rxt`
   fails 2 cases on this box when the harness compiles generated code with
   Apple clang (default `cc`): `(a+)$`'s artifact trips
   `-Werror,-Wc23-extensions` ("label followed by a declaration") at a
   `rx_reverse_state reverse_view_state = reverse_state;` line. Not this
   lane's construct (no class in the pattern) and not touched here;
   `CC=gcc-16` avoids it. Flagging as a macport residual in the EMITTER
   (a label-adjacent declaration), not the harness.
3. **The letters conjunct** (§1's flagged narrowing) — reviewable in one
   line if Frank wants the general 0x20-pair.
4. **Pre-existing test-codegen failures on this box** (same five on main,
   measured): OS-0b's two-engine fixture fails to compile and both its
   dependents fail with it; [K24]'s de-sugared control retains 4 accessor
   calls; [SABANCHOR] reports S199's anchor stale against
   tests/harness/run.sh; and (under `make test-codegen`'s group)
   `run_inline_capability.sh` cannot read `rx_search` out of `nm` —
   Mach-O prefixes symbols with `_`, so the probe reads no symbol even
   under gcc-16. None are this branch's; all look like macport residuals
   worth their own admin slice.
5. **The bump-history narrative** in `run_codegen_tests.sh` had already
   stopped at 19->20 while ABI_EXPECT read 22 (events 20->21, 21->22 are
   absent from the prose). My 22->23 clause is appended; the two missing
   clauses are the manager's call (I did not invent text for other lanes'
   events).
6. **Merge order**: hunks on shared files (tuning.md, axes_dump.c,
   pcrec.h, run_codegen_tests.sh, run_recursion_identity.sh) are minimal
   and self-contained; expect clean rebase onto utf8s2's merge, with the
   abi number and FILEPIN the two things to re-check there (D94).
