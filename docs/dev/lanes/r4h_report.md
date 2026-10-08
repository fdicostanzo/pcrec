# r4h — [MEMFN] R4h / M3: STAY, the scan edge's loops and VMSPAN at stride 1 migrate into the kit, zero movers

Lane r4h (opus), 2026-10-08, branch `lane/r4h` cut from the kit branch
`lane/memfn-r4h` (= main c4c37af8, abi 67). Charter: the kit manager's brief;
memfn/docs/responses.md 2026-10-08 (the R4h edit set notice, Q-R4h-1 (a)+(b),
R4h prep, the frozen ADVANCE target); r4hprep_report.md, advtarget_report.md;
the R4g precedent (r4g_report.md). Rulings: `r4h_rulings.md` R1 (ids
S614-S617). Every file:line below is this branch's tip.

## 1. Summary (resume from here)

- **No STOP.** No emitted byte moved on any compile made (§4), and no abi
  event was needed. The kit's existing generic ADVANCE render
  (`memfn/src/generic.c` `stmt_advance`) reproduces main's normalized text
  exactly; no kit source changed.
- **Commits** (`git log c4c37af8..lane/r4h`): `991b5c49` IMPLEMENT (DELEG
  rows, builders, I1 shadow), REPLACE (kit door at the five loop sites,
  pcrec's loop text deleted, `vm_emit_span_scan` split, shadow deleted),
  manifest + C12, sabotage, S512 + anchors re-derived, CLAUDE.md, this
  report.
- **Checks re-pinned in this delivery:** manifest (STAY/EDGE/VMSPAN
  `delegated`, VMSTRIDE on `vm_stride_loop`), C12 (`emit_dfa.c` walk-open
  and walk-stmt rows deleted, 8 -> 6 rows, 12 -> 8 forms, floor 8 -> 6),
  sabotage S72/S214/S512 re-anchored, S614/S615/S616 new,
  `call_graph.txt` + `sabotage_anchors.{tsv,total}` re-derived.
- **OWED** (the manager's slot): §8.

## 2. What was built

### 2.1 pcrec (src/gen)

- `memfn_sites.def`: three rows, `DELEG_SITE({STAY,EDGE,VMSPAN}, MF_OP_SKIP,
  DELEG_H(MF_H_ADVANCE), MF_TK_SET, DELEG_LOOP, MF_USE_POSITION)`. C10's
  D91_LOOP literal already classified all three (`run_deleg_sites.sh` 5/0).
- `memfn_sites.{h,c}`: `PcrecAdvance` (the builder's record: the term's
  256-byte set, `reverse`, the hook texts `more`/`peek`/`step`/`cursor`,
  pcrec's own `member` text, the caller's `count`/`count_start`, the cap
  `span`, `indent`) and `pcrec_memfn_advance_site` (the one shared
  description: STMT / SKIP / ADVANCE over one SET term at offset 0,
  `empty` NOP since the range IS `more` (Q-G2-5), `use` POSITION,
  `consumer` ENGINE, `count_by_caller` = `count != NULL`). The `member`
  hook (`adv_member`) returns the caller's text and never reads the
  offered byte expression (advtarget's caveat). No new door: callers
  render through `pcrec_memfn_emit`, so `site_census.DOORS` is unchanged and
  C17 rule 2 attributes the render to the emitting function.
- Builders beside each decision:
  - `stay_advance` (emit_dfa.c, AXIS F): the stay set (`stay_set`, the ONE
    derivation `emit_stay_table` now also reads), the direction's
    `peek`/`advance`/`posv`, the member `<p>_<machine>_stay<K>[<peek>]`,
    `more` passed by the caller (`dir_fwd_skip`: `scan_position + 1 <
    subject_length` under a view, else `<`; `dir_rev_skip`:
    `f->dir->scan_more`).
  - `edge_advance` (emit_dfa.c, axis H): the edge class's set, the
    direction's `scan_more`/`peek`/`advance`/`posv`, the member `test` =
    `scan_test(f, head)` (T4, now returning arena text; written twice as
    before, so `SCAN_TEST_CALLS` 2 still holds), and on a counted edge
    `count` `scan_run_length`, `count_start` 1 (after the peeled step),
    `span` the run's cap.
  - `vm_span_advance` (emit_vm.c): the body's class bitmap expanded to 256,
    `more` `<p>_span_cursor + 1 <= {lim_|subject_length}`, `peek`
    `subject[<p>_span_cursor + 0]`, `step` `<p>_span_cursor += 1`, the
    member = position 0's `vm_cls_test` text (captured as written into
    `scr_test`, arena-copied), `count` `it_` (`count_start` 0, cap rmax) for
    a bounded quantifier.
- `vm_emit_span_scan` split: it keeps the block (brace, `it_`, `lim_`, the
  cursor init) and dispatches stride 1 to the VMSPAN site and stride > 1 to
  `vm_stride_loop` (the strided `while`, pcrec's, VMSTRIDE, pending).

### 2.2 The kit

Unchanged. The generic row renders all eight frozen shapes; no row was
added, so no `options.def` row, no arms re-pin, no MF_SITE_ABI move.

## 3. The boundary: what stays pcrec's (function names)

| text / decision | owner | where |
|---|---|---|
| the STAY skip's `if/else if (state == K...) {` entry, the reverse view guard on the entry, the accept store (`if (!f->views && ...accept)`), the closing brace | pcrec | `dir_fwd_skip`, `dir_rev_skip` |
| the forward STAY view bound (`+ 1 <`) | pcrec, as the `more` hook | `dir_fwd_skip` |
| the stay tables and their set | pcrec | `emit_stay_table`, `stay_set` |
| the scan edge's comment, peeled guard (`if (state == H && more && test)`), peeled `advance;`, `unsigned long scan_run_length = 1;`, the fall-through block (`if (scan_run_length == span) {...}`), the accept stores | pcrec | `emit_scan_edge` |
| the run test (T4), the member hook's text | pcrec | `scan_test`, `scan_choice`, `scan_table`, `scan_name` |
| `dfa_edge_of`/`dfa_edges[]`, axis F (`DfaDir`), `pick_skip_states` | pcrec | emit_dfa.c (untouched) |
| the span block, `unsigned long it_ = 0;`, `lim_`/`PRUNE_CLAMP_SPAN`, `<p>_span_cursor = scan_position;` | pcrec | `vm_emit_span_scan` |
| the class tests, the member text | pcrec | `vm_cursor_rep` (test loop), `vm_cls_test` |
| the strided loop | pcrec (VMSTRIDE, M6) | `vm_stride_loop` |
| the `while` with its range, cap, member and step/count | **kit** | `memfn/src/generic.c` `stmt_advance` |

## 4. Shadow-comparator and zero-mover evidence

**I1 shadow (IMPLEMENT, 991b5c49).** `pcrec_memfn_advance_shadow` rendered
each site through a scratch art and compared it byte for byte with the span
pcrec had just written (a mismatch failed the compile with `[R4h I1]`).
Over every unique `pattern` line of `tests/**/*.rxt` (4,376 patterns,
`--features all`) under four configs (`-fno-comments`, `-fcomments`,
`--engine=vm`, `-e utf8`): **17,504 compiles, 0 I1 failures, 78,298 sites
compared** (STAY 446, EDGE 5,198, VMSPAN 72,654); a rerun over three configs
found 0 `memfn`/internal-error refusals. Log: `build/r4hscratch/
shadow_sweep.tsv` (gitignored).

**Byte identity (cheap tier).** `build/r4hscratch/zm.sh`: 38 cells, the
REPLACE build vs `build/pcrec` copied before the first edit
(`pcrec.base`, sha256 03f428ce…), `-p rx -o rx.c` both, `.c`, `.h` and rc
compared: **38/38 SAME**. Cells: STAY fwd/rev/anchored (`a[^x]*`), STAY
view (`a[^x]*x$`), EDGE unbounded/counted fwd+rev (`[a-z]*`,
`a[0-9]{3,20}x`, `[a-z]{0,2}`), fold/kit run tests (`(?i)xa{3,}b`,
`--tune=-2`), `foo\B`, `\b\w+\b`, `(?m)[^c]*$`, `-fno-scan-edge`,
`-fcomments` x3, `--engine=vm` x11 (VMSPAN with/without `it_`, MRL `lim_`
18 sites, strided stride 2 x2, lazy, possessive, comments), hybrids x2,
`-e utf8` x8 (incl. `--engine=vm -e utf8`). The same 38 were SAME at
IMPLEMENT with the shadow live.

## 5. C12 / C17 numbers (measured by running)

- C12 (`make test-memfn-forms`): 8 forms in 6 groups, 6 ceiling rows, sum 8
  (memchr 1, span-decode 1, span-index 4, walk-back 1, walk-open 1);
  `emit_dfa.c` walk-open 2 -> 0 and walk-stmt 2 -> 0 (rows deleted);
  `emit_vm.c` walk-open stays 1 (`vm_stride_loop`). `C12_CEIL_ROWS_FLOOR`
  8 -> 6. 4/0. (The notice's prediction matched.)
- C17 (`make test-memfn-manifest`): 13 rows, delegated 9 / pending 4; 18/0.
  Corpus pass: 424 renders over 276 compiles, including `dir_fwd_skip` 7,
  `dir_rev_skip` 6, `emit_scan_edge` 93, `vm_emit_span_scan` 43.

## 6. Sabotage

| row | anchor now | defect (same as before / new) | hand-measured |
|---|---|---|---|
| S72 | RE-ANCHORED: `dir_rev_skip`'s builder call + door + the accept-store guard `if (!f->views && ...)` | `!f->views` leaves the guard (unchanged) | anchor count 1; not run (codegen + wordb_basic) |
| S214 | RE-ANCHORED kit-side: `memfn/src/generic.c` `stmt_advance`'s cap line, plant scoped `count_start != 1` | the scan edge's loop loses `scan_run_length < <span>ULL` (unchanged) | bounded_repeats.rxt **11 failed / 40 passed** (the row's original figure); VMSPAN witness green |
| S512 | RE-ANCHORED: deletes the SETREST row (emitter still named by PRE/VERIFY) | one manifest row gone, only the K35 floor red (unchanged class; VMSTRIDE's deletion would now also trip rule 1) | `FAIL: the manifest holds 12 rows, below its K35 floor of 13`, 17/1 |
| S614 (new) | `dir_fwd_skip`: `f->views ? "+ 1 <" : "<"` -> `"<"` | the forward STAY view bound | gate.rxt **4 failed** (also multiline 2, review_r2 2, eol_engine 1; eol_scan_avoidance/anchors 0) |
| S615 (new) | `edge_advance`: `.more = span < 0 ? "1" : ...` | the unbounded EDGE loop's subject bound | start_pinned_startpos.rxt **6 failed** (exit 139 on `.*`, 3/3 runs) |
| S616 (new) | kit-side, `stmt_advance`'s cap line, plant scoped `count_start != 0` | VMSPAN's `it_` cap | possessify.rxt **26 failed / 3511 passed** (bounded_repeats, counterk 0: hybrid/counter rung) |
| S617 | unused | — | — |

S614 and S615 are anchored PCREC-side: their bounds are the caller's `more`
hook text, which the kit pastes opaque (Q-G2-5), and no site fact separates
the unbounded edge from the STAY skips and the VM span, so a kit-side plant
could single them out only by sniffing hook text. Each new row has
`SAB_REACH`/`SAB_REACH_EXPECT` checked on the clean build (all three reach).
Finding: the `+ 1 <` bound was undetected by `eol_scan_avoidance.rxt` (the
greedy `.*$` family), detected only by lazy/bounded `$` shapes elsewhere.

`python3 scripts/m6read_check_sab_anchors.py`: **517 sabotages / 535 anchor
sites, all anchors resolve.** `sabotage_anchors.tsv` re-derived by its own
method: owner changes S214 `emit_scan_edge def` -> `file:memfn/src/generic.c
outside`; new S614 `dir_fwd_skip`, S615 `edge_advance`, S616 generic.c;
`OTHER_ROWS_NAMING_FAMILY` 0 -> 1 (S512's new anchor names
`req_site_define`, a manifest text line); S571's UNRESOLVED (rc 2) is
pre-existing. `inventory_check.py` against the new `call_graph.txt`: 150/150.

## 7. Validation (light tier, this lane)

- `make -j4`, `make -j4 strict` clean.
- `make test-memfn-{forms 4/0, arms 221/0, rows 117/0, stamps 14/0, deleg
  5/0, link 8/0, arch 15/0, manifest 18/0}`.
- codegen single scripts (PCREC=build/pcrec): `run_scan_edge_census.sh`
  20/0, `run_vm_frameless.sh` 6/0, `run_premul_table.sh` 0 failed.
  `run_scan_edge_dispatch.sh` FAILS 2 (http-5xx, two-chain: "INCONCLUSIVE
  the table load is not on a cycle (gcc hoisted it)") **identically with
  the pre-edit binary**: pre-existing, not wired into make, not this lane's.
- G2 `--quick` pinned (`taskset -c 12-15`, `make test-memfn-g2`): see §8
  item 0 / the handback (log `build/r4hscratch/g2quick.log`).

## 8. The slot chain the manager must run

0. (If not reported green in the handback) `make test-memfn-g2`, log above.
1. Merge `lane/r4h` into the kit branch ALONE; `make -j16 && make strict`.
2. Identity gate, 0 movers expected on every stream including `--engine=vm`
   (VMSPAN is reached only there) and both comment tiers:
   `python3 scripts/emit_sweep.py --ref <base tip> …` (the R4c invocation),
   judged by `python3 docs/design/memfn/probes/lxrun/memfn_r4c_gate.py
   --zero-dumps <out>`. Witness cells the notice names: `a[^x]*`,
   `a[^x]*x$`, `[a-z]*`, `a[0-9]{3,20}x`, `(a)[a-z]{2,9}x` / `a[a-z]*x`
   under `--engine=vm`.
3. N2 census (`docs/design/memfn/probes/rowcon/n2_census.sh`, JOBS=16):
   would_decline 0 (three new site kinds reach the gate).
4. G2 full (`make test-memfn-g2-full`).
5. `make -k -j16 -Otarget test`; verdict `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`.
6. Mech, each SOLO (`bash tests/mech/run_sabotage_matrix.sh <id>`):
   - re-pinned: S72 S214 S512;
   - new: S614 S615 S616;
   - the notice's solo list: S433 S61 S39;
   - anchored in a changed definition: S37 S57 (`vm_cursor_rep`), S571
     (`memfn_sites.c`);
   - the C12/C17 rows whose populations moved: S510 S511 S524 S525 S526
     S527.
   The file-level superset is `bash tests/mech/rows_for.sh $(git diff
   --name-only c4c37af8..lane/r4h)` (224 rows).
7. Not lane work: the kit's responses.md entry and journal line; pcrec's
   dev_journal line at the merge.

## 9. Charter checklist

| item | state |
|---|---|
| DELEG_SITES rows STAY/EDGE/VMSPAN (SKIP/ADVANCE/SET, DELEG_LOOP, MF_P_INLOOP) | DONE |
| builders beside each decision, hooks as text, member = pcrec's own test text, count_by_caller where pcrec owns the counter | DONE (`stay_advance`, `edge_advance`, `vm_span_advance`) |
| shadow comparator, both comment tiers, `--engine=vm`, `-e utf8` | DONE (17,504 compiles, 0 mismatches) |
| REPLACE: through the door, pcrec loop text deleted | DONE |
| `vm_emit_span_scan` split, VMSTRIDE stays pcrec's | DONE (`vm_stride_loop`) |
| manifest STAY/EDGE/VMSPAN delegated, VMSTRIDE pending | DONE |
| C12 ceilings + floor re-derived by running | DONE (6 rows / 8 forms, floor 6) |
| everything the notice keeps pcrec's stays pcrec's | DONE (§3) |
| S214 / S72 re-anchored, same defect | DONE (S214 kit-side, scoped; plus S512, which REPLACE made stale) |
| anchors tsv + call_graph re-derived, m6read check green | DONE |
| three new rows with reaching witnesses, numbered from the rulings | DONE (S614-S616; S617 unused) |
| zero movers, 20+ compiles, same -o basename | DONE (38/38) |
| arms/rows/manifest/forms/stamps green, G2 --quick pinned | DONE except G2: see handback |
| CLAUDE.md: src/gen, memfn/src, tests/memfn | DONE |
| no abi event | none needed |
