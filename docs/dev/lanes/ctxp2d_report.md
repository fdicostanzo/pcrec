# ctxp2d — [DD-11.5] P2d: the `\A`/`\z` fold at the NFA layer (delivery report)

Lane ctxp2d (opus, engine code), 2026-10-20, branch `lane/ctxp2d` from main
`39457a796` (abi 81). Design: `docs/design/ctx_span.md` rev 2.1 §4.2, §4.6, §7;
rulings D168 + addenda 1-3 (addendum 3 rules this step: NFA layer only, the AST
kinds stay, P2e lifts them later). Build go: Frank, 2026-10-20 ("Then let's
schedule the anchor work. I remember our discussion and the 9 table."). Box rule:
the memfn kit held the one heavy slot, so this lane ran LIGHT work only. Nothing
heavy ran (no `make test`, no mech, no full emit_sweep, no test-axes); §7 is the
owed list.

## 0. Premise test (first, per the brief)

`command grep -rn 'N_BOT\|N_END' src` at the base found the 12 engine sites
§4.6's census names. Line numbers moved after P2c, but the count is the same:

| site | census (`3b0f87b55`) | base `39457a796` |
|---|---|---|
| NKind members | `internal.h:1993`, `:1995` | `internal.h:1962`, `:1964` |
| lowering arms | `nfa.c:620`, `:642` | `nfa.c:615`, `:637` |
| eps labels | `dfa.c:693`, `:695` | `dfa.c:684`, `:686` |
| closure arms | `dfa.c:1019-1021`, `:1027-1029` | `dfa.c:1014-1017`, `:1022-1025` |
| kset labels | `kset.c:136`, `:138` | same |
| VM arms | `emit_vm.c:8892`, `:8952` | `emit_vm.c:8909-8918`, `:8929-8940` (they are `A_BOL`/`A_END` arms; the VM emits from the AST) |

The two GENERIC clauses also exist as stated: `pcrec_nfa_has_bot`'s `N_BOT`
clause (`nfa.c:1313`) and the `has_end` hoist's `case N_END` (`dfa.c:1573`).
There is no difference to report.

## 1. What landed

| commit | what |
|---|---|
| `f3e5ac219` | the build (below) |
| `a78b0961e` | CK-8 covers the two new rows; assertions §1d |
| `21784a338` | S75's anchor kept (see F-4); sabotage rows S1171-S1176; directory CLAUDE.md entries; the regenerated edit set and the derived rows |
| (this report's commit) | report |

The build:
- **`src/core/ctxfn.def`** gains two rows. `SUBJECT_START` is 0x1C0
  (`0,0,0, 0,0,0, 1,1,1`, VM side `VMCTX_START`, role text
  `"^ attempt_position of subject (absolute offset 0)"`). `SUBJECT_END` is 0x124
  (`0,0,1, 0,0,1, 0,0,1`, `VMCTX_END`, `"\\z end of subject (absolute)"`). Both
  role strings are copied verbatim from the VM arms they replace. The
  `_Static_assert` ties each grid to its hex. The derived predicates give the
  design's columns: START reads absent prev only, END reads absent next only,
  and neither reads membership.
- **`internal.h`**: `N_BOT`/`N_END` are deleted from `NKind`. A new
  `pcrec_anchor_ctxfn(AKind)` maps `A_BOL` to SUBJECT_START and `A_END` to
  SUBJECT_END, and any other kind to 0. It is the design's "table lookup",
  stated once, and both engines read it.
- **`nfa.c`**: the two lowering arms are now `frag_ctx_row(b,
  pcrec_anchor_ctxfn(a->k))`, an N_CTX state with an empty `cls`. The
  `pcrec_nfa_has_bot` clause `k == N_BOT ||` is deleted, because the existing
  absent-prev predicate covers `^`. The S1157 anchor line is unchanged.
- **`dfa.c`**:
  - The two eps labels and the two closure arms are deleted. The N_CTX arm's
    gated absent index reads `left_abs`/`right_abs`, and `sides_of` sets them
    from `bot_ok`/`end_ok`: forward `left_abs = bot_ok`, both directions
    `right_abs = end_ok`. That is the deleted arms' predicate, so nothing new is
    needed.
  - `case N_END` in the `has_end` hoist is deleted. The absent-next predicate
    already covers it.
  - `cr_ctx_reads` now reads `ctxfn_reads_membership`. This was the design's one
    new generic predicate; F-1 shows it is load-bearing, though for another
    reason than the design gave.
  - **`Clo.bot_ok` and `closure()`'s `bot_ok` parameter are deleted** (F-2).
- **`kset.c`**: the two labels are deleted.
- **`emit_vm.c`**:
  - `vm_ctx` is split. `vm_ctx_row(v, entry, fn, si, next)` looks up the form
    and emits it. `vm_ctx` keeps the set check and the `vm_cls` interning (F-3).
  - Two new sides, `VMCTX_START` and `VMCTX_END`, emit today's two expressions
    character for character.
  - The two hand arms collapse into one `case A_BOL: case A_END:` arm that calls
    `vm_ctx_row(..., pcrec_anchor_ctxfn(a->k), -1, ...)`.
- **Comments** that named the retired kinds were reworded in `revdet.c`,
  `mod_assertions.c`, `emit_dfa.c` (two comments in the emitter source, not
  emitted text), `run_endvar_identity.sh` and `run_search_pinned.sh`.

**The AST is unchanged.** `A_BOL`/`A_END` and every analysis label stay, which
is D168 add. 3's NFA-only form. There are 0 recognizers.

## 2. Light checks and verdicts

| check | result |
|---|---|
| `make -j16`, `make strict` | clean (after each commit) |
| **mover probe** (scratch `build/p2d/probe.py`, not committed): every distinct corpus pattern (4,636, from `--list-source` over every `tests/**/*.rxt`), base `39457a796` vs P2d, byte-compared on c-default, c-vm, c-utf8, c-utf8-vm, `--emit-ir` (vm) and `--emit-facts=byte,utf8` | **0 movers on every arm** |
| the same probe on `-fno-rev-end`, `-fno-anchored-dfa`, `-fno-rev-end-onewalk`, `-fno-scan-edge` | 0 movers |
| the probe's failing direction: a temporary plant (the VM's `\z` form changed, plus `cr_ctx_reads` without the clause) | c-vm 82 movers, c-default 18 (VM-routed). The probe sees moves. |
| the eight `--list-*` dumps, base vs new | identical |
| CK-8 `ctxfn_table_check.py` (now 10 rows; SUBJECT_START asked as `(?<![\s\S])`, `\A`, `^`; SUBJECT_END as `(?![\s\S])`, `\z`) | 0 failures. Planted flips (START's absent/absent cell, END's in/in cell) are reported by row and cell: 5 failures across the 5 spellings |
| assertions §1b-§1d, run from the section standalone (the real file's lines, extracted) | 7 pass / 0 fail. Under S1171's plant binary §1d reads 0 pass / 4 fail |
| harness `tests/assertions/absolute.rxt` | 869 passed, 0 failed |
| `[SABANCHOR]` (`scripts/m6read_check_sab_anchors.py`) | 835 rows, all anchors resolve |
| `make test-codegen` (at `21784a338` + docs) | `run_group: 16/16 scripts passed`, run_codegen_tests 35/0, rc 0 (`[SABANCHOR]` 835 inside it) |

**Mover census (CK-4 for P2d): ZERO, as the design predicted.** No emitted byte,
listing byte, facts row or dump moved. The design's fallback ("if a moved byte
appears it is an abi event like P2c") did not fire. So **this is NOT an abi
event: abi stays 81, the FILEPIN is not re-pinned, and the brief's 82 is unused**
(D76: an emitted-byte change is the trigger; there is none). For the manager to
confirm.

**No spec hunk.** Nothing a caller can observe changed: bytes, `--emit-ir`
role text, `--emit-facts`, the `--list-*` surfaces and routes are all identical.
`docs/spec/` names neither kind.

## 3. The abi readers

Not applicable: zero bytes moved, so the number does not change and there is no
reader to move (§2).

## 4. The edit set, regenerated from the real diff (R4)

`docs/design/ctx_span/regen_edit_set.py` was run over P2d's commit `f3e5ac219`
against the base call graph (`call_graph_p2d_base.txt`). The output is in
`edit_set_p2d.tsv` (23 distinctive removed code lines) and
`edit_set_compare_p2d.txt`. The script's "planned, not made" half reads the
P2a-P2c labels only, so the P2d comparison was done by hand:
- **Planned and made** (the design's P2d tokens): `case N_BOT:`, `k == N_BOT ||`,
  `case N_END`, `N_BOT,`, `N_END,`.
- **Planned, not made, BY RULING** (D168 add. 3, NFA layer only): `case A_BOL`,
  `k = A_BOL`, `A_BOL,`, `case A_END`, `k = A_END`, `A_END,`. These are P2e's.
- **Made, not planned**, each justified:
  - the two VM arm bodies (the census named the arms, but the edit set did not
    list their lines);
  - `cr_ctx_reads` (planned as GENERIC in the census, not listed in the set);
  - the `VMCTX_*` enum (two sides added);
  - `vm_ctx`'s lookup lines, which moved into `vm_ctx_row` (F-3);
  - `Clo.bot_ok`, the `closure()` parameter and its two call/initializer lines
    (F-2).

**Derived population** (`sabotage_anchors.py --step P2d=39457a796..f3e5ac219`,
then `derive_rows.py` → `derived_rows_p2d.tsv`):
- Owner rows, RE-RUN at P2d: S1100, S14, S746 (`compile_ast`); S1151, S1159
  (`pcrec_build_dfa`); S1157 (`pcrec_nfa_has_bot`); S1161 (`vm_ctx`); S341
  (`clo_walk`); S365, S86 (`vm_emit_node`); S69, S882 (`make_state`).
- Anchor row: S75 (`vm_ctx`). Its anchor text is in the edit set, and the build
  keeps the line (F-4), so it is a RE-RUN, not a re-aim.
- The `witness:P2c` rows the script also prints are P2c's (its witness regex
  names `(?m)`), so P2d places no obligation on them.
- The "after-P2d" RE-RUN bucket (233 rows) is the start-table family's
  default-final class. The anchor map assigns it whatever the edit set; it is
  not P2d-derived.
- No row loses its site, and none retires.

## 5. Sabotage rows (S1171-S1176, from S1171-S1185; S1177-S1185 unused)

| row | plant | detector (by-hand reach, 2026-10-20) |
|---|---|---|
| S1171 | `cr_ctx_reads` without the membership clause | assertions §1d: 0 pass / 4 fail. Corpus: 0 of 4,636 move |
| S1172 | SUBJECT_START's (absent, absent) cell is 0 | CK-8: 3 failures; `absolute.rxt`: 5 failed |
| S1173 | SUBJECT_END's (in, in) cell is 1 | CK-8: 2 failures; §1d: 4 fail. Answers do not move, because the set is empty |
| S1174 | `pcrec_anchor_ctxfn` swaps the rows | `absolute.rxt`: 237 failed; §1d: 4 fail |
| S1175 | the VM's `\z` passes at `n-1` | harness over the 25 corpus files carrying `\z`: 27 failed / 36,087 passed (e.g. `revend/stage2_captures.rxt` `(a?)\z`, `atomic_groups/atomic_assert.rxt` `(?>a\z|ab)`) |
| S1176 | `frag_ctx_row` writes `ctxfn = 0` | `absolute.rxt`: 193 failed |

Every SAB_DOC_FIGURE reads OWED. The solo mech verdicts are owed (§7).

## 6. Findings

- **F-1 (the design's reason for `ctxfn_reads_membership` is wrong; the clause
  is still load-bearing).** §4.6 says that without the clause an absent-only row
  "contributes a set ... or every artifact gains an atom". It does not gain an
  atom: the set is empty, so it refines no class, and every byte's atom vector
  keeps bit k clear. The cost is elsewhere. The entry is a live A_CTX-row entry,
  so `ctx_atoms` sets `Dfa.clsctx`. That turns on `wctx` and the D11 `views`
  flag (`emit_dfa.c`, and `anch_start`), which changes the candidate scan's form.
  Witnesses `a(?:\z|)` and `(?:\z)?a` (byte and utf8) stamp `memchr-bounded`
  instead of `memchr`. **No corpus pattern reaches it** (0 of 4,636 under the
  plant), so the corpus alone could not have caught the clause going missing.
  Assertions §1d is the check, with its failing direction measured. The
  SUBJECT_START side reaches nothing observable on 14 tried witnesses: the
  ENG_ATTEMPT emitter reads no `clsctx` that moved. S1171 therefore covers the
  `\z` side only.
- **F-2 (`Clo.bot_ok` was the N_BOT arm's alone).** After the arm deleted,
  nothing read the field, so the field and `closure()`'s `bot_ok` parameter go.
  `bot_ok` still reaches the closure, now only as `left_abs` through `sides_of`.
  This was not in the design's edit set. It deletes a field a future arm could
  read in the wrong direction (A1's hazard class).
- **F-3 (the VM needed a row emitter that interns no set).** `vm_ctx` always
  interned the node's set (`vm_cls`). An absent-only row has none: interning an
  empty bitmap would add a class-pool entry (not measured, because the split
  avoids it). `vm_ctx_row` takes `si = -1` for such rows. This was not in the
  design.
- **F-4 (an anchor the first cut broke).** S75's `SAB_BEFORE` is `    int si =
  vm_cls(v, bits);`. The first commit inlined that call and broke the anchor.
  `[SABANCHOR]` would have gone red in `make test-codegen`. The line is restored
  verbatim in `21784a338`, and all 835 anchors resolve. My first anchor grep had
  searched the deleted lines' tokens, not the moved lines.
- **F-5 (S1175 is caught by the corpus, but not by `absolute.rxt`).** The
  plant changes only VM-routed `\z` answers. The first witness tried, `(a)\z`
  on "ab", stays nomatch under the plant even though it is VM-routed: the end
  window/pin starts the attempt late. `(a|ab)\z` on "aab" does show it (plant
  (1,2), oracle (1,3)). Over every corpus file carrying `\z`, 27 cells fail,
  so the row is DETECTED and needs no new cells.
- **F-6 (a role string to file, not fix).** The VM's `^`/`\A` role text reads
  `"^ attempt_position of subject (absolute offset 0)"`, and the `(?m)^` row
  reads `"(?m)^ attempt_position of subject or ..."`. Both look like a
  `start`→`attempt_position` rename that reached a string. They are kept
  verbatim, because changing them moves `--emit-ir` bytes (an abi event) and is
  out of this lane's scope. Filed for [IFACE-PUSH]-style doc work.
- **F-7 (P2e's remaining work).** After P2d, the engine layer has no
  start/end-of-subject kind. P2e's AST fold now touches only the analysis layer
  and the parser: the 109 label tokens, the 8 STILL-SPECIAL sites and D168 add.
  3's CLASS column. The lowering map `pcrec_anchor_ctxfn` is the one line P2e
  replaces, with "the node's own row".

## 7. OWED heavy validation (a fresh lane, after the kit's slot)

Run in this order, one heavy run at a time, from the worktree
`/home/pcrec/projects/pcrec/worktrees/ctxp2d` at the branch tip. REF =
`39457a796`.

1. `make test`: `scripts/perfrun --label ctxp2d -- build/val/test.log`. Expected:
   green with no re-pins. No corpus file changed, and zero bytes moved, so
   rxtsource, startset and size pins should not move. Read the verdict with
   `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/val/test.log`. Sections
   that count most:
   - assertions (§1b CK-8 at 10 rows, the new §1d);
   - codegen (`[SABANCHOR]` 835, `ABI_EXPECT=81` unchanged);
   - `run_endvar_identity.sh` and `run_wordctx_identity.sh` (both still
     identity);
   - recursion identity (FILEPIN NOT re-pinned: if (B) reads a mover, that is a
     finding against the zero-mover census, not a pin to move).
2. emit_sweep against REF, every arm: `python3 -I scripts/emit_sweep.py --ref
   39457a796 --out build/val/sweep_default` and again with `--arms start` (plus
   `--extra -e --extra utf8` per the ctxbuild precedent). Expected: **0 movers on
   every stream and arm**, dumps identical, every floor held. CK-4(a) for P2d is
   "the empty set". Any mover is a finding.
3. mech, solo rows:
   - new: `S1171 S1172 S1173 S1174 S1175 S1176`;
   - derived re-runs: `S1100 S14 S746 S1151 S1157 S1159 S1161 S341 S365 S86
     S69 S882 S75`;
   - the [SABANCHOR] count gate (six rows added, none deleted).
   Read each row from its own `== mech run COMPLETE` trailer. Expected: all
   DETECTED except S1160 (still declared UNREACHED; unchanged). 
4. CK-5-style identity: subsumed by item 2's zero-mover requirement on the
   forward/reverse machines (the bytes carry the tables, `eolvar`/`endvar` and
   the views flag). Also add the four non-corpus witnesses: `a(?:\z|)`,
   `(?:\z)?a`, `(?:\A|x)a`, `\A\z`, at byte and utf8, base vs tip.
5. U-B3: `PCREC=build/pcrec python3 -I docs/design/kit_proof/conj.py` (census,
   witnesses, per-pattern dump) with REF's compiler and with the tip's. Expected:
   byte-identical.
6. `make test-axes` in the battery shape: `AXES_FULL=1 HARNESS_BATCH=64`, bound
   10,800 s (the unbatched default shape timed out at 7,200 s in
   ctxbuild-val). Expected: every axis answer-identical.
7. recursion-identity FILEPIN: no re-pin owed (no abi event). The gate's run in
   item 1 is its check.

That is seven items.

## 8. Decision text for the manager

None is required. D168 add. 3 rules this step. Two things could be recorded:
- a D168 addendum-3 note: "P2d built 2026-10-20 at the NFA layer with zero
  movers, no abi event";
- F-1's correction to ctx_span.md §4.6. The membership clause is load-bearing
  through `clsctx`/views, not through atoms.

## 9. STATE AT HANDOFF

- Branch `lane/ctxp2d`, tip = this report's commit. The tree is clean.
- Rulings file `docs/dev/lanes/ctxp2d_rulings.md` was re-read before each
  commit and before this report. It is empty, so no ruling was applied.
- Light checks are complete. Heavy validation is OWED (§7).

## 10. STATE AT HANDOFF (p2dval)

(The brief called this section 8; §8 and §9 were taken, so it is §10.)

- Merge of main (20e0fe126) into lane/ctxp2d: `2059ba434`. One conflict, docs/dev/lanes/CLAUDE.md (this lane's report row and runkit's row, both kept). `make strict` green. No src/ edit.
- Rulings file re-read: last entry applied is "2026-10-20 manager rulings on the handback (805356b70)", rulings 1-4. Ruling 1 still binds: any emit_sweep mover turns P2d into an abi event (82).
- Chain armed detached, `--keep-going`, pid 2221081, logdir `/home/pcrec/projects/pcrec/worktrees/ctxp2d/build/p2dval/chain`. Stages file `/home/pcrec/projects/pcrec/worktrees/ctxp2d/build/p2dval/stages.txt` (not committed), helper scripts in `build/p2dval/s/` (mkref.sh, witness.sh, conj.sh; not committed). 10 stages, total cap 32,340 s (axes 15,600 = 10,381 x 1.5; test is ttune 2,940).
- Differences from §7: the REF compiler is built in-chain by `mkref.sh` (git archive 39457a796); §7 item 4's four witnesses and item 5's conj.py (census, witnesses, rarm; REF vs tip cmp) are scripted stages; the per-pattern dump of ctxbuild (`build/v/conj_pp.py`) is not reproduced; `run_mline_diff.sh` is not owed here; item 7 is covered by the `test` stage. emit_sweep `--arms start` carries `--extra -e --extra utf8` as written in §7.

```
# p2dval: ctxp2d heavy validation, ctxp2d_report.md section 7 order. REF = 39457a796.
build    light 300   make -j16
refbuild light 900   build/p2dval/s/mkref.sh
test     light ttune scripts/perfrun --label p2dval -- "$STAGE_LOG.make"
sweepdef heavy 1500  python3 -I scripts/emit_sweep.py --ref 39457a796 --out build/p2dval/sweep_default
sweepstart heavy 3000 python3 -I scripts/emit_sweep.py --ref 39457a796 --arms start --extra -e --extra utf8 --out build/p2dval/sweep_start
mechnew  heavy 2400  make mech S1171 S1172 S1173 S1174 S1175 S1176
mechold  heavy 3600  make mech S1100 S14 S746 S1151 S1157 S1159 S1161 S341 S365 S86 S69 S882 S75
witness  heavy 900   build/p2dval/s/witness.sh
conj     heavy 1200  build/p2dval/s/conj.sh
axes     heavy 15600 env AXES_FULL=1 HARNESS_BATCH=64 make test-axes
```

- watch:   scripts/watchrun /home/pcrec/projects/pcrec/worktrees/ctxp2d/build/p2dval/chain
- verdict: scripts/verdict /home/pcrec/projects/pcrec/worktrees/ctxp2d/build/p2dval/chain/chain.log
- stop:    scripts/safekill 2221081

## 11. STATE AT HANDOFF (p2dfix, 2026-10-20)

Rulings file last entry applied: item 5 (owed item 7, recursion-identity gate).

Fixes to the four mis-invoked p2dval stages (first chain: build/p2dval/chain, axes still running):
- sweepstart: argparse read `-e` as an option; spelled `--extra=-e --extra=utf8`.
- mechnew/mechold: `make mech S1171 ...` made the ids MAKE TARGETS, so the full matrix ran and hit the caps. The selector is the script's positional args (matched at the id boundary, every id must match, else FATAL): `bash tests/mech/run_sabotage_matrix.sh S1171 ...`. Caps 1500 s (6 rows) and 2400 s (13 rows), from about 30 s/row measured earlier today (39 rows, ~20 min).
- witness: the old script wrote ref.c/tip.c, so the emitted `#include "<name>.h"` differed (same-basename -o trap). build/p2dval/s2/witness.sh uses the same basename `m.c` in two directories. VERDICT, run in the foreground: 8/8 SAME (byte and utf8 x 4 patterns), zero movers; ruling 1 condition on witnesses holds (the heavy sweeps still decide the rest).
- recid: owed item 7, `make test-recursion-identity`, added (takes the box lock itself; no re-pin).

Chain2: build/p2dval/s2/stages.txt, 5 stages (sweepstart, mechnew, mechold: heavy; witness, recid: light), logdir build/p2dval/chain2. chainrun is one-per-tree (exit 75 while chain 1 lives), so build/p2dval/s2/arm.sh (detached, pid 3036831) waits on `flock build/.chainrun.lock` and then runs `chainrun --fg --keep-going` on the stages file; the heavy stages also queue on the boxlock. After chain 1 ends, chain2/chain.log appears. Watch: `tail -f build/p2dval/chain2/chain.log` (or `scripts/watchrun <tree>`). Verdict: `command grep -E '^== (stage|CHAIN)' build/p2dval/chain2/chain.log`. Stop: `scripts/safekill 3036831` before it starts; once running, the pid in chain2/chain.pid.
