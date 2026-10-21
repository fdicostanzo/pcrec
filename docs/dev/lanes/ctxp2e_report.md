# ctxp2e — [DD-11.5] P2e: `\A`/`\z` as A_CTX rows with a derived class column (delivery report)

Lane ctxp2e (opus, engine code), 2026-10-20, branch `lane/ctxp2e` from main
`73c2bb655` (abi 81, P2d landed). Design: `docs/design/ctx_span.md` rev 2.1 §4.2,
§4.6, Q7 (RULED: D168 addendum 3). Build go: Frank (wake.md, session 120 close),
"P2e (the AST fold with the derived class column; Frank's go covers it, own abi
event)"; the manager's brief is the build go.

## 0. Premise test

- `grep -c "PCREC_ARTIFACT_ABI 81" src/gen/emit_dfa.c` is 1 (`emit_dfa.c:54`).
- `grep -n SUBJECT_START docs/design/ctx_span.md` finds the §4.2 table row
  (line 620) and §4.6.
- `git log -1 --format=%h` at the start was `73c2bb655`.

## 1. The sites, re-derived by grep on the base

`command grep -rn '\bA_BOL\b\|\bA_END\b' src` at `73c2bb655` gives 118 code lines
in 26 files. Each line was read beside the `A_CTX` arm of the same switch
(§4.6's method).

**The 8 STILL-SPECIAL sites.** §4.6's census lists 8, and the base has 8.
Each now switches on `pcrec_ctx_class(n)` with no `default:`. Lines are on the
base:

| # | site (base `73c2bb655`) | kind | what the class switch answers |
|---|---|---|---|
| 1 | `src/facts/startanch.c:114` `sa_walk` | `A_BOL` → `SA_BOT` | PIN_START → SA_BOT; PIN_END, CONTEXT → nothing |
| 2 | `src/opt/derive.c:225` `q_rewrite` | `A_BOL` killed | PIN_START killed (outside a lookbehind); PIN_END, CONTEXT kept |
| 3 | `src/opt/derive.c:291` `qp_walk` | `A_BOL` counted | PIN_START counted (`bol_out`); the others not |
| 4 | `src/facts/widths.c:128` `em_set` | `A_BOL` → `EM_S` | PIN_START → EM_S |
| 5 | `src/facts/widths.c:132` `em_set` | `A_END` → `EM_E` | PIN_END → EM_E; CONTEXT → mask 0 |
| 6 | `src/facts/endwin.c:134` `ew_walk_marked` | `A_END` → `EW_Z` | PIN_END → EW_Z; PIN_START, CONTEXT → EW_NONE |
| 7 | `src/opt/possessify.c:662` `first_of` | `A_END` transparent | PIN_END → `fst_empty(true)`; PIN_START, CONTEXT → the widen (below) |
| 8 | `src/parse/definitions.c:429` `eol_tail_plain` | `A_END` admitted | PIN_END → true; the others false |

**DELETED.**
- `internal.h`: the `A_BOL` and `A_END` members (`:739`, `:752`) and
  `pcrec_anchor_ctxfn` (`:1210`, P2d's map).
- `nfa.c`: the two lowering arms (`:627`, `:651`) and `frag_ctx_row`. A pin
  now takes the A_CTX arm, which builds the same N_CTX state, empty `cls`.
- `emit_vm.c`: the `case A_BOL: case A_END:` arm (`:8929`).
- `possessify.c`: the `A_BOL` arm (`:641`). The A_CTX arm's widen answers the
  same: a pin reads an absent side, so `pcrec_poss_ctx_admits` never narrows
  it.

**GENERIC.**
- The producers. `pcrec_ast_pin` (parse.c) builds an anchor-spelled A_CTX
  over no set. `^` (`parse.c:1724`) and `\A`/`\z` (`mod_assertions.c:86`,
  `:88`) call it, and `\A` keeps its `pcrec_lb_raise(cx, 1)`.
- `pcrec_is_bare_anchor` (`parse.c:185`). Its two labels go; the A_CTX arm
  reads `u.ctx.anchor`, which the builder sets.
- `vm_ctx` (`emit_vm.c`). A row that reads no membership goes straight to
  `vm_ctx_row` with set -1, before the byte-image check, so no empty class is
  interned (P2d F-3).
- **`ps_node` (`possessify.c`, NOT in the census as a non-label: F-2).** Its
  non-gate A_CTX branch now copies `first_of`'s nullability.

**LABEL.** Every other line drops its `case A_BOL:`/`case A_END:` tokens. The
A_CTX label already shared each arm; I checked each for a statement between
the labels. The diff deletes 122 case tokens in all (61 + 61), counting the
special arms' own labels. `pcrec_ast_is_core` loses both (A_CTX answers core,
the same answer).

## 2. The CLASS column

- **ctxfn.def.** Each row gains `CLASS` after its grid: `CONTEXT`,
  `PIN_START` or `PIN_END`. It sits on the second line, so the four grid-line
  sabotage anchors keep their text.
- **internal.h** derives the class from the grid. `CTXFN_CLASS_OF(fn)` tests
  equality with `CTXFN_GRID_PIN_START` (0,0,0 0,0,0 1,1,1) and
  `CTXFN_GRID_PIN_END` (0,0,1 0,0,1 0,0,1). A per-row `_Static_assert` checks
  the written column against it, the same shape as the HEX check.
- `pcrec_ctx_class(const Ast *)` reads the derivation and never the column.
  `CtxClass` is the closed enum the analyses switch on.
- **Why equality and not the predicates (F-1).** "Reads absent prev, reads no
  membership" is also true of `(?<=[\s\S])` (0x03F, the start pin's
  complement), so a predicate composition would have called it a pin.
- **The class's independent control is CK-8's new half**
  (`tests/assertions/ctxfn_table_check.py`). Each row's written class must
  equal the class that libpcre2's observed nine cells imply, with a floor of
  one row per class (K35). Today it reads `classes CONTEXT=8 PIN_END=1
  PIN_START=1: 0 failures`. Failing direction, measured on planted copies of
  the .def:
  - SUBJECT_END written CONTEXT gives 3 failures: canonical, native, and the
    empty PIN_END class.
  - Both pins written CONTEXT gives 7 failures.

## 3. Mover census (N-3 included): predicted ZERO, measured ZERO

**Prediction.** I wrote it before the measurement and after reading every
site; it went into this file during the build.
- The NFA is state-for-state P2d's: the A_CTX arm builds the same N_CTX state
  `frag_ctx_row` built.
- The VM emits the same rows through `vm_ctx_row`.
- Every analysis answers what its kind arm answered, through the class.
- N-3 (the end-mark lowering's tagged form reads `A_END`): `eol_tail_plain` is
  sub-parsed over `\Z`'s row `(?=\n?\z)`. Its `\z` is now the end pin, which
  the class switch admits exactly as `case A_END` did, so the tail and the
  tagged form are unchanged.
- The one site where the fold changes an arm's input is `ps_node` (F-2). It is
  fixed generically, so its answers are today's.

Predicted movers: **none**, on every arm, the listing and the facts.

**Measured** with P2d's probe (`build/p2e/probe.py`, copied from
`worktrees/ctxp2d/build/p2d/probe.py`, not committed). It covered every
distinct corpus pattern (4,636 from 5,811 `--list-source` rows over
`tests/**/*.rxt`), base `73c2bb655` against the P2e build, byte-compared:

| arm | movers |
|---|---|
| c-default, c-vm, c-utf8, c-utf8-vm | 0, 0, 0, 0 |
| `--emit-ir` (vm) | 0 |
| `--emit-facts=byte,utf8` | 0 |
| `-fno-poss-ctx-follow`, `-fno-end-window`, `-fno-rev-end`, `-fno-vm-anchor-bound` | 0, 0, 0, 0 |
| `-fno-start-pinned`, `-fno-anchored-dfa`, `-fno-prefilter`, `-fno-ctx-node` | 0, 0, 0, 0 |
| the 8 `--list-*`/`--features` dumps | identical |
| 19 non-corpus witnesses (`^abc`, `\Aabc`, `abc\z`, `a(?:\z\|)`, `(?:\z)?a`, `(?:\A\|x)a`, `\A\z`, `x*\z`, `(a\|ab)\z`, `^\w+\b`, `a{0,3}\z`, `[ab]*\z`, `(?m)^a$`, `a\Z`, `a$`, `\Gab`, `^(?:a\|^b)`, `(?<=^)a`, `ab(?=\z)`) x {auto, vm} x {byte, utf8} | 76 of 76 identical (`.c` and `.h`) |

Prediction and measurement agree by ID: the empty set equals the empty set.
The heavy sweeps are owed (§7).

## 4. The abi: NOT bumped (manager ruling 1)

The brief said "P2e is ITS OWN abi event: 81 -> 82". D76/D94 key the abi on
emitted text, and the light census moved nothing (§3). The interim message
asked the manager to rule.

**Ruling 1 (manager, 2026-10-20):** no bump; abi stays 81. D168 add. 3's "own
abi event" was conditional on movers, and N-3's mover census measured zero.

**The condition:** the heavy chain's emit_sweep against `73c2bb655` must also
read 0 movers, on the plain sweep, `--arms start` and every variant. Any
mover there turns P2e back into the 81 -> 82 event, with the full reader
ritual (§4.5.1: grep `81`'s readers, run `make test-codegen`, registry,
codegen and rxtsource). In that case the lane stops and reports before
landing. Abi 82 is not taken.

**No spec hunk is owed by D80.** Bytes, listings, facts, routes and
diagnostics are all unchanged. One spec sentence named the deleted kind:
`registry.md` §9¶2 said "its primitive form, `A_BOL`, is core". It now reads
"the `SUBJECT_START` context node", which is vocabulary, not contract.
`make test-spec-history` is green (11/0).

## 5. Sabotage rows

**Ids used:** S1186-S1197 (of S1186-S1205; S1198-S1205 unused).

**Re-aimed** (their sites were deleted; the anchor map's RE-AIM class plus the
[SABANCHOR] tripwire):

| row | was | now |
|---|---|---|
| S1174 | `pcrec_anchor_ctxfn` swaps the rows | mod_assertions.c's two pin builders swap them (two sites) |
| S1176 | `frag_ctx_row` writes `ctxfn = 0` | the NFA's A_CTX arm writes 0 for every row that reads no membership |
| S49 | possessify's `A_BOL` arm made transparent | the A_CTX arm's `CTX_PIN_START` case returns `fst_empty(true)` |
| S1172, S1173 | one pin grid cell flipped (+hex) | the same, plus a second site writing the class the flipped grid derives (CONTEXT). Otherwise the class assert refuses the build and CK-8 stops being their detector |

**New rows,** with reach measured by hand. `build/p2e/plant.sh` applies a row
to a scratch copy of the tree, builds it and runs one detector; the log is
`build/p2e/measure.log` (scratch, not committed).

| row | plant | detector (by hand, 2026-10-20) |
|---|---|---|
| S1172 (re-aimed) | SUBJECT_START's (absent, absent) cell 0, hex and class updated | CK-8 7 failures (cell + class); `absolute.rxt` 5 failed |
| S1173 (re-aimed) | SUBJECT_END's (in, in) cell 1, hex and class updated | CK-8 5 failures; `absolute.rxt` 22 failed (`(\z)*`'s generated C fails `-Werror`) |
| S1174 (re-aimed) | `\A` builds SUBJECT_END, `\z` SUBJECT_START | `absolute.rxt` 201 failed / 668 passed |
| S1176 (re-aimed) | the NFA writes `ctxfn = 0` for every no-membership row | `absolute.rxt` 193 failed / 676 passed |
| S49 (re-aimed) | possessify's start-pin case made transparent | possdiff 1 pattern diverged (`a{0,4}^`) |
| S1186 | SUBJECT_END's class written CONTEXT | BUILD REFUSED (static assert), `SAB_EXPECT=BUILD-REFUSED` |
| S1187 | `CTXFN_CLASS_OF` never answers PIN_END | BUILD REFUSED (static assert) |
| S1188 | startanch: end pin -> SA_BOT | harness over tests/assertions 3 failed |
| S1189 | derive: start pin kept in Q | test-compound red (split-f/-np/-q no longer admitted) |
| S1190 | derive's G5 count blind to the start pin | test-compound red (same fixtures) |
| S1191 | widths: start pin marks EM_E | `nullable_anch.rxt` 2 failed; prefilter-collapse 6 failed |
| S1192 | widths: end pin unmarked | prefilter-collapse 1 failed (`nullable_anch.rxt` 0: answer-identical) |
| S1193 | endwin: start pin -> EW_Z | harness over tests/assertions 120 failed |
| S1194 | possessify: end pin widens | run_assertions_tests.sh 1 failed (the STRATS exemption stamp) |
| S1195 | `eol_tail_plain` refuses the end pin | run_b3_checks.sh: six one-seed witnesses read `overflow` |
| S1196 | `ps_node` drops `first_of`'s nullability | harness over tests/assertions + tests/possessify 5 failed |
| S1197 | `pcrec_ast_pin` leaves `anchor` false | `tests/assertions/d27/syntax_errors.rxt` 10 failed (the reject table reads 0, so the row names the corpus file) |

The solo mech verdicts are owed (§7).

`[SABANCHOR]`: 847 rows, 877 anchor sites, all resolve (`scripts/m6read_check_sab_anchors.py`).

**Derived population** (R4). I ran `regen_edit_set.py` over `fe37f93be` →
`edit_set_p2e.tsv`. Then `sabotage_anchors.py --step
P2e=73c2bb655..fe37f93be --final after-P2e` and `derive_rows.py` produced
`derived_rows_p2e.tsv`: 44 owner/anchor rows, 15 comment-only.

The re-run list:

S-U4 S14 S49 S52 S58 S59 S84 S86 S91 S94 S97 S104 S107 S108 S127 S156 S157
S158 S159 S160 S174 S177 S302 S305 S338 S339 S365 S366 S446 S465 S498 S499
S500 S501 S588 S613 S746 S761 S807 S893 S904 S1100 S1174 S1176

The `witness:P2c` rows the script also prints belong to P2c.

**Hand comparison with §4.6's census:**
- **Planned and made:** the census's DELETED, GENERIC and STILL-SPECIAL sites
  (§1).
- **Planned, not made:** none.
- **Made, not planned:**
  - `ps_node` (F-2);
  - `frag_ctx_row` and `pcrec_anchor_ctxfn` (P2d's own additions, which P2e
    retires);
  - `vm_ctx`'s early route;
  - the CTXFN_ROW macro's new parameter at its three includers.

## 6. Findings

- **F-1: the class must be derived by grid equality.** A composition of the
  three predicates admits `(?<=[\s\S])` as a start pin (§2). The derivation
  and its comment say so.
- **F-2: one §4.6 LABEL site was not a label.**
  - `possessify.c`'s `ps_node` (the A1 chain summary) returned the A_CTX branch
    as "non-nullable, as `first_of`". Every A_CTX was non-nullable before P2e;
    `\z` is the one that is not (end-pin transparency).
  - The census saw `case A_END` in the bottom label list and called the line a
    LABEL. But the A_CTX arm above it answered differently, so the fold would
    have flipped `\z`'s summary nullability.
  - Fixed generically: the branch copies `first_of`'s nullability, which keeps
    every existing answer. The chain summary's premise comment now says "every
    gate", not "every A_CTX".
  - S1196 plants the old line.
  - This does NOT change the count of 8: it is not a recognizer. It is a site
    the census's arm comparison missed, because the two arms sit 50 lines
    apart.
- **F-3: a doc finding, filed rather than fixed.** The registry's `^` row
  description still reads "already core (A_BOL, the same node \A builds)"
  (`registry.c`, bare_rows). It is `--list-syntax` output and part of
  `docs/pcre2_compliance.md`'s generated section, so rewording it is a dump
  change that needs a compliance refresh: [IFACE-PUSH]-style doc work. The
  code comment above it is fixed.
- **F-4: the class check supersedes S1172/S1173's build path.** A flipped pin
  cell is no pin, so the class assert now refuses the plant. They gained a
  second site (§5) so that CK-8 stays their detector. S1186 is the
  build-refusal row.
- K112 (P2d F-6, the stale `attempt_position` role text) is untouched: P2e
  emits the same role strings from the same rows.

## 7. OWED heavy validation (armed detached; a fresh agent reads it)

REF = `73c2bb655`. The chain is `build/p2e/stages.txt` (not committed), log
directory `build/p2e/chain/`:

```
# ctxp2e owed heavy validation (ctxp2e_report.md §7). REF = 73c2bb655.
build      light 300   make -j16
strict     light 900   make strict
test       light ttune scripts/perfrun --label ctxp2e -- "$STAGE_LOG.make"
sweepdef   heavy 1800  python3 -I scripts/emit_sweep.py --ref 73c2bb655 --out build/p2e/sweep_default
sweepstart heavy 3600  python3 -I scripts/emit_sweep.py --ref 73c2bb655 --arms start --out build/p2e/sweep_start
sweepvar   heavy 10800 python3 -I scripts/emit_sweep.py --ref 73c2bb655 --tree-rev "$(git rev-parse HEAD)" --variant all --out build/p2e/sweep_var
mechnew    heavy 1800  bash tests/mech/run_sabotage_matrix.sh S1172 S1173 S1174 S1176 S49 S1186 S1187 S1188 S1189 S1190 S1191 S1192 S1193 S1194 S1195 S1196 S1197
mechold    heavy 3600  bash tests/mech/run_sabotage_matrix.sh S-U4 S14 S52 S58 S59 S84 S86 S91 S94 S97 S104 S107 S108 S127 S156 S157 S158 S159 S160 S174 S177 S302 S305 S338 S339 S365 S366 S446 S465 S498 S499 S500 S501 S588 S613 S746 S761 S807 S893 S904 S1100
recid      light 3600  make test-recursion-identity
```

- **Dry runs** (2026-10-20, `--limit 3`): `emit_sweep.py --ref 73c2bb655 --arms
  start` rc 0; `--tree-rev HEAD --variant all` rc 0, `VARIANTS: CLEAN`.
  `chainrun --check` parses all nine stages. Every mech id matches exactly
  one row file.
- **The mech rows:** `mechnew` holds the 12 new rows plus the 5 re-aimed ones
  (S49, S1172-S1174, S1176). `mechold` holds the other 41 derived re-run
  rows.

- **Expected:**
  - every stage green;
  - all three sweeps (plain, `--arms start`, `--variant all`) report zero
    movers; any mover makes P2e an abi event (§4, ruling 1);
  - every mech row DETECTED (S1186/S1187 as BUILD-REFUSED);
  - recursion identity green with no re-pin.
- **test-axes is not in the chain:** no axis moved in the probe's eight-axis
  arm (the brief: "test-axes if an axis moved").
- **Verdicts:**
  - `scripts/verdict build/p2e/chain/chain.log`;
  - make test's verdict:
    `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/p2e/chain/test.log.make`.

## 8. STATE AT HANDOFF

- **Branch `lane/ctxp2e`.** The code is `fe37f93be`; the tip is this
  report's commit. The tree is clean apart from this commit.
- **Commits:**
  - `fe37f93be`: the build;
  - `14f541ac0`: CK-8's class half, the rows and re-aims, the derived rows,
    docs, the spec vocabulary and the plan status;
  - `fd8f54d27`: the reach figures, the S1191/S1192/S1197 detectors, and CK-8
    reading a commented row;
  - `c82239beb`: this report's reach table, ruling 1 and the chain;
  - `6edf3227f`: the owning directories' CLAUDE.md.
- **Rulings file** `docs/dev/lanes/ctxp2e_rulings.md` was re-read before each
  commit and before this report. The last entry applied is "2026-10-20 manager
  ruling 1": no abi bump, conditional on the heavy sweeps reading 0 movers.
- **Light checks, complete:**
  - `make -j16` and `make strict` clean;
  - `ctxfn_table_check.py` 0 failures (classes CONTEXT=8 PIN_END=1
    PIN_START=1);
  - `make test-spec-history` 11/0;
  - `[SABANCHOR]` all 877 anchor sites resolve;
  - the mover probe: 0 on 6 arms and 8 axes, dumps identical, 76/76 witnesses
    identical;
  - every new or re-aimed row reached by hand (§5).
- **Chain ARMED, detached, waiting on the lift file:**
  - pid 1545267; lift `worktrees/ctxp2e/.lift` (the manager creates it);
    `--keep-going`;
  - log directory `/home/pcrec/projects/pcrec/worktrees/ctxp2e/build/p2e/chain`;
  - chain head `6edf3227f`.
  - Watch: `scripts/watchrun /home/pcrec/projects/pcrec/worktrees/ctxp2e/build/p2e/chain`.
  - Verdict: `scripts/verdict /home/pcrec/projects/pcrec/worktrees/ctxp2e/build/p2e/chain/chain.log`.
  - Stop: `scripts/safekill 1545267`.
  - The completion line is `== CHAIN DONE`, or `== CHAIN FAILED stage=...`.
- **Owed:** every stage of §7, listed there with its expectations. Any mover
  in `sweepdef`, `sweepstart` or `sweepvar` turns P2e into the 81 -> 82 event:
  stop and report before landing (ruling 1).
- **Scratch** (gitignored, not committed), under `build/p2e/`: `base_pcrec`,
  `probe.py`, `plant.sh`, `measure.sh`, the measure and probe logs, the movers
  TSVs, and `ptree/` (a plant tree, safe to delete).
