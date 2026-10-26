# ic1a — [INLINE-C] stage 1a: the per-kind attribute row

Lane ic1a (opus), 2026-10-26, branch `lane/ic1a` off main `7f7f67dc6`.
Design: `docs/design/inline_c.md` §1.8 and §9 "Stage 1a". Build go: Frank
2026-10-26 ("Just get the feature done"). No abi event: the stage is
ZERO emitted-byte movers by charter, and nothing emitted was touched.

## 1. What was built

- `src/core/kindrow.def` — ONE declared row per `AKind`, X-macro
  `KIND_ROW(KIND, TEXT, PATH, READS, ERASE)`, in enum order (§2 below).
- `src/core/internal.h` — the row's types (`KindText`, `KindPath`,
  `KindReads`, `KindRow`), a per-row `_Static_assert` on its AKind
  position, and `pcrec_kind_row(AKind)` / `pcrec_ast_row(const Ast *)`,
  whose switch is generated from the table under
  `#pragma GCC diagnostic error "-Wswitch"`: **a kind without a row fails to
  compile in every translation unit**, with or without `make strict`.
  `pcrec_ast_row` takes the NODE, not the kind, so stage 1b's `A_CALLOUT`
  can answer per node (its W_PRED / W_ANY width classes) without touching a
  reader.
- The readers (§3): each converted arm calls a small per-file helper that
  switches on the row COLUMN (no `default:`), so the walks keep their
  exhaustive `AKind` switches (coding.md 1.3's alarm) and only the leaf
  "roster" arms changed.
- `tests/core/kindrow_check.sh` (in `run_core_tests.sh`, so `make
  test-core` / `make test`): the completeness check (§5).
- `Makefile`: `kindrow.def` joins `FACTS_HDRS` (every object depends on it,
  `ctxfn.def`'s precedent).

## 2. The row table (as committed)

| kind | TEXT | PATH | READS | ERASE |
|---|---|---|---|---|
| A_CLASS | OWN | TRANSPARENT | NONE | 0 |
| A_CAT | OWN | TRANSPARENT | NONE | 0 |
| A_ALT | OWN | TRANSPARENT | NONE | 0 |
| A_REP | OWN | TRANSPARENT | NONE | 0 (the count collapse is per node) |
| A_EMPTY | ZERO | TRANSPARENT | NONE | 0 |
| A_EOL | ZERO | TRANSPARENT | NONE | 0 |
| A_CTX | ZERO | TRANSPARENT | NONE | 0 |
| A_GSTART | ZERO | TRANSPARENT | NONE | 0 |
| A_KRESET | ZERO | TRANSPARENT | NONE | 0 |
| A_CAP | OWN | TRANSPARENT | NONE | 0 |
| A_ATOMIC | OWN | TRANSPARENT | NONE | NFA_ERASED_ATOMIC |
| A_BREF | ANY | OPAQUE | REFS | 0 |
| A_LOOK | ZERO | GATE | NONE | NFA_ERASED_LOOK |
| A_CALL | OWN | OPAQUE | TARGET | 0 |
| A_VAR | ANY | OPAQUE | NONE | 0 |
| A_WCLASS | OWN | TRANSPARENT | NONE | 0 |

TEXT and PATH are separate columns on purpose: a lookaround is ZERO to a
text reader but must never be absent to a path reader ([ART-POSS-ARMS]
rev 2.1 N1 was that confusion as a live miscompile). A_CTX is rowed as
today's kind (ZERO/TRANSPARENT); its pins stay in `ctxfn.def`'s class
column, and possessify's context record stays under [POSS-CTX-TABLE], as
the brief ruled.

## 3. The arm inventory

### 3.1 Converted (the arm now reads the row)

| site | arms | column read | helper |
|---|---|---|---|
| `src/opt/mrl.c` `pcrec_cwmax` | EMPTY, EOL, CTX, GSTART, KRESET, LOOK, BREF, VAR | TEXT | `row_cwmax` (ZERO 0, ANY/OWN unbounded) |
| `src/facts/req.c` `rb_walk_at` | the zero-width roster + BREF, VAR | TEXT | `rb_row_into` (ZERO assert, else unbounded gap) |
| `src/facts/startset.c` `ss_walk` | EMPTY, EOL, CTX, GSTART, KRESET, LOOK, BREF, VAR | TEXT | `ss_row` (ZERO passes `acc`, else every byte, nullable) |
| `src/ir/nfa.c` `compile_ast` (the prefilter lowering) | EMPTY, KRESET, LOOK; ATOMIC's erase bit | TEXT + ERASE | `frag_row` (ZERO: epsilon, ORs the row's erase bit) |
| `src/opt/possessify.c` `first_of` | BREF (arm B's fallback), VAR, LOOK, CALL, KRESET/EMPTY | PATH + TEXT | `fst_row` |
| `src/opt/possessify.c` `text_first` | the zero roster merged with CLASS/BREF/CALL/VAR | TEXT | inline `pcrec_ast_row(a).text == KTEXT_ZERO` |
| `src/opt/possessify.c` `gk_build` | BREF/VAR, LOOK, CALL, EMPTY..KRESET | PATH + TEXT | `gk_row` |
| `src/opt/atomic.c` `pcrec_bref_mark` (the ONE marked set) | the leaf roster (BREF, VAR, CLASS, EMPTY, EOL, CTX, GSTART, KRESET) + CALL | READS | `bref_mark_reads` (NONE / REFS loop / TARGET) |

The four pass families the note names are all present: fact walks
(cwmax, req, startset), possessify follow (first_of, text_first,
gk_build), prefilter language (nfa.c), marked set (bref_mark).

### 3.2 Kept as code, and why

| site | why it keeps its code |
|---|---|
| `mrl.c` `pcrec_minw`, `pcrec_cwmin`, `pcrec_nullable`; `facts/widths.c` `em_set`, `rw_node` | ROW-INVARIANT: every non-OWN value gives the same answer (a ZERO and an ANY node both contribute minimum 0 / nullable), so a row read would be a lookup whose answer never varies — a branch with one outcome. The cwmax half is the one whose answer differs, and that half converted. |
| `facts/startanch.c` `sa_walk`; `facts/endwin.c` `ew_walk`, `em_tails` | CONTEXT, not kind: the answers depend on A_CTX's pin class (`ctxfn.def`) and on position, which the row deliberately does not carry (§1.8 "a row states the kind-level answer only"). |
| `opt/revdet.c` (`rd_shape`, `rd_reverse`, `revdet_first`, `rd_alt_disjoint`, `rd_walk`) | ROW-INVARIANT for the shape gate (it declines every non-class leaf alike); `rd_alt_disjoint` has a KRESET-specific clause and `revdet_first` widens on every opaque kind — no column distinguishes what the code distinguishes. |
| `possessify.c` `ps_node`, `item_first`, `pss_walk`, `cap_index` | STRUCTURE: they recurse into children or defer to `first_of` (already converted), and read no kind-level attribute themselves. |
| `atomic.c` `has_*` predicates, `dis_walk` | Per-kind PREDICATES over structure ("does a backreference occur below"), not attributes; converting them would rename `a->k == A_BREF` as a column test with the same single member. |
| `kinds.c`, `select_engine`, `callgraph.c`, `ctxnode`, the parser, `emit_vm.c` | Out of 1a's scope (the emitters are explicitly excluded; the engine selector and callgraph decide per node, with node fields). |

## 4. Finding: `pcrec_bref_mark` read `u.bref` on an `A_VAR` node

At the base, `pcrec_bref_mark` (`src/opt/atomic.c`) shared one arm
between `A_BREF` and `A_VAR` and looped over `a->u.bref.refs[0..nrefs)`.
An `A_VAR` node's payload is `u.var` = `{ const VarExp *exp; int slot;
bool caseless; }`, which overlays `u.bref` = `{ const int *refs; int nrefs;
...}`: on x86-64 the loop read `nrefs` = the variable's `slot` and
`refs[i]` = the leading ints of the `VarExp` struct, marking any of those
that happened to fall in `(0, nmark)` as a referenced group. A union
misread (D70's "a writer may touch `u.<payload>` only under a kind check
that owns it").

The row states the truth — a variable reads NO group (READS NONE; its
bytes come from the caller) — so 1a's conversion removes the misread.
Consequence for the zero-mover proof: if a pattern with both a `${var}`
and capture groups ever had a group spuriously marked, its emitted bytes
move under 1a (a publish-at-close that should never have been there). The
14-pattern spot check (§6) saw no mover; the full sweep is the evidence.
**For main:** this is a latent defect of the base tree; if the sweep finds
a mover it will be in a `vars` pattern and this is its cause (the
brief's stop rule then applies: it is a mover I can explain but should not
"remove" by restoring a union misread — main rules).

This is also why S1641 (S-IC24) is aimed at `A_BREF`'s READS, not the
brief's "A_VAR's reads": A_VAR's row is already NONE, so flipping it would
plant nothing.

## 5. The completeness check (`tests/core/kindrow_check.sh`)

Six sub-checks, one `-fsyntax-only` each on a copy of `src/`+`lib/`:
(1) census as TEXT — the AKind enumerators in `internal.h` and the
KIND_ROW rows are the same 16 names in the same order (K35 floor 16);
(2) control — a probe TU calling `pcrec_kind_row` compiles on the live
tree; then four plants that must FAIL: (3) a new kind appended to AKind
with no row (`enumeration value 'A_KINDROW_PROBE' not handled in switch`);
(4) the A_VAR row deleted; (5) the A_EMPTY/A_EOL rows swapped (`is not at
its AKind position`); (6) the A_LOOK row duplicated (`redeclaration of
enumerator`). Measured locally: 6/6 PASS; `run_core_tests.sh` 8/8 PASS.

## 6. Zero-mover proof

- Local spot check (reference `git archive 7f7f67dc6` built in
  `build/ref_main`): 14 patterns covering every converted arm × three
  modes (`.c` default engine, `.c --engine=vm`, `--emit-ir --engine=vm`
  incl. the `possessify marked/total` line) — 0 movers.
- `make strict`: rc 0 on the lane tree.
- **The full proof is OWED (§9, queued):** `scripts/emit_sweep.py --ref
  7f7f67dc6` over the corpus (all eight streams: `.c` default, `.c` VM,
  `--emit-ir` VM — which carries `possessify marked/total` per pattern —,
  composition, registry dumps, `--emit-facts=byte,utf8`, emit-ir-auto,
  stderr), and the same over the 336 distinct pcrec-bench patterns
  (`docs/dev/lanes/ic1a_bench_patterns.txt`, built read-only from
  `pcrec-bench/bench/*/patterns/*.rx`, `--patterns-file … --no-corpus`).

## 7. Sabotage rows

### 7.1 New (S1638-S1641; one per column family, all planted in `kindrow.def`)

| id | design id | plant | reader family | detector | measured by plant | reach (clean tree) |
|---|---|---|---|---|---|---|
| S1638 | S-IC21 | A_LOOK PATH GATE→TRANSPARENT | possessify follow | harness on `tests/possessify/composition_d27.rxt` | 18/9002 cases fail | `a*(?=a(?!a))` `--emit-ir` reads `possessify 0/1` (plant: 1/1) — REACHED |
| S1639 | S-IC22 | A_VAR TEXT ANY→ZERO | fact walks (cwmax, req, startset, text_first) | `vars` arm | 28/88 corpus cases fail | `${v}x` `--emit-facts` start_set `nullable` (plant: `{x}`) — REACHED |
| S1640 | S-IC23 | A_LOOK ERASE→0 | prefilter language | harness on `tests/lookaround/prefilter.rxt` | 6/53 cases fail | S746's hybrid probe — REACHED |
| S1641 | S-IC24 (re-aimed, §4) | A_BREF READS REFS→NONE | marked set | `dupnamesdiff brefdiff harness` (dupnames.rxt) | harness 3/88 fail on dupnames.rxt | `(a)\1` `--emit-ir` names `group 1 PUBLISHED` (plant: absent) — REACHED |

"Measured by plant" = the plant built by hand in `build/plants/` and the
row's detector run on it; the mech run of the rows themselves is owed
(§9). Reach was evaluated by running each row's `SAB_REACH` on the clean
tree (the matrix's `REACH_ONLY=1` waited on the box lock).

### 7.2 Re-aimed (their anchor moved with the conversion; meaning unchanged)

S104, S108 (site 2), S157 (both sites), S158, S159, S498, S499, S500,
S501, S746. Each carries a `[INLINE-C] stage 1a … RE-AIMED` note naming
where its plant went. S499/S500/S501 were re-planted so the kinds that
fall through into the sabotaged label keep their row read (a first draft
let `A_LOOK`/the zero kinds fall into the plant). Anchor tripwire
(`scripts/m6read_check_sab_anchors.py`): all 1038 anchor sites resolve;
each plant compiles (`-fsyntax-only`). Detection is owed (§9).

## 8. Files

`src/core/kindrow.def` (new), `src/core/internal.h`, `src/opt/mrl.c`,
`src/facts/req.c`, `src/facts/startset.c`, `src/ir/nfa.c`,
`src/opt/possessify.c`, `src/opt/atomic.c`, `Makefile`,
`src/core/CLAUDE.md`, `tests/core/{kindrow_check.sh,run_core_tests.sh,
CLAUDE.md}`, 14 files under `tests/mech/sabotages/`,
`docs/dev/lanes/{ic1a_report.md,ic1a_job,ic1a_bench_patterns.txt}`.
Not touched: `memfn/`, `emit_compound.c`, any emitter, the abi stamp.
No new AST kind.

## 9. Owed runs (queued — DO-THEN-FINISH)

One boxqueue job, `docs/dev/lanes/ic1a_job`, name `520-ic1a-test`
(key `ic1a-test`), runs in this worktree: `make -j16`; `make strict` →
`job.log.strict`; `run_core_tests.sh` → `job.log.core`; emit_sweep corpus
→ `job.log.sweep` (scratch `build/ic1a_sweep_corpus/`); emit_sweep bench
→ `job.log.sweepbench` (`build/ic1a_sweep_bench/`); the 14 mech rows →
`job.log.mech`; `scripts/perfrun --label ic1a` (make test) →
`job.log.make`. Logs land in the job's run dir under
`worktrees/.boxqueue/{running,done,failed}/…-520-ic1a-test/`.

Completion lines (the job's declared expects; all must hold for green):
- `strict: whole tree compiles clean` (1)
- `checks failed: 0` in job.log.core (1)
- `emit_sweep: DONE rc=0` in job.log.sweep and in job.log.sweepbench (1 each)
- `== mech run COMPLETE: 14 rows (unexpected: 0, undetected: 0, unreached: 0, …)`
- `sections ran: 79/79`

Ready gate: the job is not ready from 2026-10-26 21:00 local (~3 h of
work must end before the 00:05 full suite owns the box); if still pending
then, the manager re-times it.

## 10. STATE AT HANDOFF

- Rulings file `docs/dev/lanes/ic1a_rulings.md`: "(none yet)" at every
  re-read, last at report time; no rulings entry applied.
- Code complete for 1a; every validation beyond the local checks above is
  the queued job. Stop rule not triggered (no mover seen; no new AST kind;
  `emit_compound.c` untouched).
- Open for main: §4's latent `A_VAR` misread (fixed by the row; may
  surface as a `vars` mover in the sweep) and S-IC24's re-aim.
