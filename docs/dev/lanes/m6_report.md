# m6 — [MEMFN] R-10 / M6, cut to VMSTRIDE: the VM span scan at stride > 1 migrates into the kit, zero movers

Lane m6 (opus), 2026-10-08, branch `lane/m6` cut from the kit branch
`lane/memfn-m6`, stacked on `lane/memfn-m7` @ 00b1f3da (M7, MF_SITE_ABI 7).
Charter: the kit manager's brief; R-10 (memfn/docs/requests.md); the R-10
rulings (memfn/docs/responses.md, "R-10 scoping ACKED by main" and the
kit-side rulings Q-R10-2..12); design input docs/dev/lanes/m6scope_report.md.
Every file:line below is this branch's tip.

## 1. Summary (resume from here)

- **No STOP. Zero movers, no pcrec abi event, NO `docs/spec/` hunk, NO
  `MF_VOCAB` bump.** The contract step is kit-side: `MF_SITE_ABI` 7 -> 8.
- **Commits** (`git log 00b1f3da..lane/m6`):
  - `ca63c779` PHASE A, M6 prep (kit-only): MF_SITE_ABI 8, MF_MAX_TERM 32,
    the strided ADVANCE in `site_check`/`stmt_advance`, gate fields
    `stride`/`cursor`, K1 `mf_ref_skip_blocks`, 7 fixtures, 9 gate cases,
    `pins/m6_target/` (6 frozen shapes), C5 checks 12/13, S526 re-anchored;
  - `432753cf` IMPLEMENT: `PcrecAdvance.stride` + per-position sets/members,
    DELEG_SITES row VMSTRIDE, ONE `vm_span_advance` for every stride, the
    `[M6 I1]` shadow, C14's stride bound + its `_Static_assert`, C10;
  - `e1e1199f`, `423b82ad`, `962fcc4c` REPLACE: `vm_stride_loop` and the
    shadow deleted, manifest VMSTRIDE delegated + VMLAZY pending, C12/C17
    literals, sabotage re-aims and new rows (measured), line-number maps
    regenerated, docs;
  - then this report.
- **OWED to the slot** (§8): identity gate, `make test`, G2 full, 66 solo mech
  rows. No N2 census is needed for a new row (no kit row was added); the
  generic row's floors are untouched.
- **G2 is GREEN at Phase A** (48,566,739 passed / 0 failed, quick tier): the
  strided ADVANCE is a relaxation G2 does not yet generate, so nothing it
  generates moved. Its NEW coverage (§7) is the blinded lane's.
- **Findings:** (F1) the scoping report's N6 reach probes and the strided
  VM sites are unaffected (N6 untouched by ruling); (F2) S684's first plant
  (a closed `while (...) {`) was UNDETECTED: C17/C12's `walk-open` line only
  sees a `while (` whose condition the literal leaves OPEN. The row now plants
  the realistic respell (the old two-printf form) and is DETECTED; the
  vocabulary's stated limit (§R4.3.4) is the reason, recorded in the row.
  (F3) S676/S678's answer-level detection rests on four
  `(?:a\.)+\b` cells in tests/possessify/possessify.rxt plus a compile
  failure (an unused class bitmap); no cell has a strided body whose first
  byte matches and whose later byte does not, apart from those. Not added
  here (oracle work), recommended.

## 2. PHASE A: M6 prep (kit-only, zero pcrec bytes; `ca63c779`)

| ruling | what changed | where |
|---|---|---|
| Q-R10-2 (W SET terms, no new term kind) | Q-G2-9 relaxed on ADVANCE only: W in 1..MF_MAX_TERM SET terms, every one REQUIRED, term i at offset i; `reverse` refused at W > 1; every non-ADVANCE SKIP keeps one term at 0. Each refusal names `pred` or `reverse` | memfn.h (MF_OP_SKIP, ADVANCE hooks); compose.c `skip_check` |
| Q-R10-3 (MF_MAX_TERM 32) | `MF_MAX_TERM` 8 -> 32 (`mf_site` 2,696 bytes on x86_64); the build-time `_Static_assert(MF_MAX_TERM >= VM_MAX_STRIDE)` is pcrec's (IMPLEMENT) | memfn.h:70 |
| Q-R10-4 (`s[cursor + i]`) | where the kit tests a term itself (no member hook) the byte at offset i is `((unsigned char)((s)[(cursor) + i]))`; at W = 1 it stays `peek`. A strided site must STATE `s` and `cursor`: the gate's new field `stride` (ONE/MANY, read on ADVANCE only) makes the generic row USE both at MANY (a conditional `uses` entry); the new hook field `cursor` (IDENT/OTHER) | generic.c `stmt_advance`, `generic_uses`; fields.def; gate.c `cl_stride`, `cl_cursor`; every other row serves both MF_ANY ("not read (ADVANCE's)", the count_by_caller precedent, so no other row's verdict moves) |
| Q-R10-5 (span_hi iterations) | restated in memfn.h; `stmt_advance` unchanged (it already capped the counter) | memfn.h ADVANCE hooks |
| render | `stmt_advance` loops over `nterm`: one `(member)` per term, ` && `-joined, the member hook called with each term's id; at W = 1 byte-identical to R4h's render | generic.c |
| K1 | `mf_ref_skip_blocks(s, n, sets, w)` (F5 strided) | k1_ref.c, memfn.h |
| MF_SITE_ABI 7 -> 8 | readers by grep: memfn.h, memfn/CLAUDE.md, memfn/include/CLAUDE.md, memfn/src/CLAUDE.md (the rest cite 7 historically: "MF_SITE_ABI 7 added X") | |

No `options.def` row: zero movers (M7's judgement call, same reasoning).

Fixtures and checks (tests/memfn): seven strided fixtures (`STRIDES`,
`render_stride`, the VM's own hook texts, one member per term):
`adv-vmstride-it` (W 2, the caller's `it_` capped at 5), `adv-vmstride`,
`adv-vmstride-lim` (`lim_`), `adv-vmstride-u8w3` (utf8 W 3),
`adv-vmstride-w32` (W 32), `adv-vmstride-range` (range members) and
`adv-vmstride-own` (no member hook: the kit's own `s[cursor + i]`). Pinned
(`ARMS_ROW_FLOOR` 88 -> 102). Nine gate cases (`GATE_CASE_FLOOR` 65 -> 74):
RENDER W 2 and W 32; REFUSE `reverse`, a gap (`pred`), an OPTIONAL term
(`pred`), a RUN term (`pred`), a strided non-ADVANCE SKIP (`pred`), unstated
`s`, unstated `cursor`. **Check 12**: `pins/m6_target/` holds the six shapes'
loops CUT from pre-edit build/pcrec artifacts (`(?:ab){2,5}c`, `(?:ab)*c`,
`x(?:ab)*abc`, utf8 `(?:aé)+x`, the 32-byte body, `(?:[a-z][0-9])+@`), compared
byte for byte with the kit's fresh render, with a planted-byte control.
**Check 13**: three strided bodies (`-it`, `-lim`, `-own`) compiled in the
cursor rung's shape and run over every subject of length 0..9 on a 3/4-letter
alphabet, every start, every `lim_`, and a NULL subject at n = 0, against a
loop written from memfn.h's contract (cursor AND counter): 5,142,837 calls,
0 wrong (`STRIDE_CALL_FLOOR` 500,000).

At Phase A: arms 338/0, manifest 13/0, arch 15/0, forms 4/0, reach 4/0,
link 8/0, stamps 14/0, deleg 5/0, rows 127/0, G2 quick 48,566,739/0,
`make strict` clean. **Zero pcrec bytes: 40/40 witness compiles
byte-identical** (`build/m6scratch/witness.tsv`; 27 reach a strided loop,
8 reach N6's walk; both encodings, `-fcomments`, `-fno-length-prune`,
`-fno-possessify`, `--tune=-2`, `-fno-cls-kit`, `-fno-cls-pack`,
`-fmemfn-simd`, `--emit-main`, a 60-byte `-p`, `--features all`, the lazy
and stride-1 controls, `--no-captures` reach control).

## 3. The boundary as built (IMPLEMENT `432753cf`, REPLACE `e1e1199f`)

| text / decision | owner | where |
|---|---|---|
| rung ladder, cursor admission (`vm_cursor_fits`, `VM_MAX_STRIDE`), possessify verdict, MRL fold/clamp, `vm_cls_test` member texts, stride and row choice (V1-V11, V13-V15) | pcrec | emit_vm.c, unchanged |
| the block `{ … }`, `it_` decl, `lim_` decl, cursor init, everything after the loop (V9, V12) | pcrec | `vm_emit_span_scan`, `vm_cursor_rep` |
| describing the site: W sets, `more` `cur + W <= bound`, `step` `cur += W`, `peek`, cursor, subject, `count` `it_`, `span` rmax (iterations), indent | pcrec, ONE builder | `vm_span_advance` (every stride) |
| `PcrecAdvance.stride`, STATED by every builder (STAY/EDGE `.stride = 1`); `pcrec_memfn_advance_site` fails the compile on 0 or > MF_MAX_TERM (Q-R10-12) | pcrec | memfn_sites.{h,c}, emit_dfa.c `stay_advance`/`edge_advance` |
| the row: VMSPAN at 1, VMSTRIDE above (Q-R10-6); budget 2 | pcrec | memfn_sites.def, `vm_emit_span_scan` |
| `_Static_assert(MF_MAX_TERM >= VM_MAX_STRIDE)` (C14's build half) | pcrec | emit_vm.c:226-232 |
| the `while` loop | **kit** | memfn/src/generic.c `stmt_advance` |

Not migrated: the lazy arm's rmin prefix (VMLAZY, pending, Q-R10-7) and N6
(untouched: manifest row, `walk-back` line, C12 row and `vm_rev_emit`, by
ruling).

## 4. Shadow and zero-mover evidence

- **I1 shadow (IMPLEMENT).** `vm_emit_span_scan` at stride > 1 still emitted
  `vm_stride_loop`'s text and `pcrec_memfn_advance_shadow` rendered the same
  site through a SCRATCH art and failed the compile `[M6 I1]` on any byte
  difference. Population: `build/m6scratch/patterns.bin`, 4,444 unique
  patterns = every corpus `pattern` (emit_sweep's `enumerate_corpus`) plus
  the 40 witnesses plus 36 synthetic strided bodies at W 4..33. x 14 configs,
  `--features all`: byte / utf8 / -fcomments (default route and
  `--engine=vm`), `--engine=vm` with `-fno-possessify`, `-fno-length-prune`,
  `--tune=-2`, `-fno-cls-pack`, and `(?i)` byte/utf8:
  **62,216 compiles, 0 mismatches, 0 internal errors, 1,477 strided sites
  compared.** Sites per stride: 2:921 3:180 4:66 5:30 6:10 7:30 8:30 9:30
  16:27 17:27 24:27 30:36 31:27 32:36. Per config (artifacts / sites): byte
  41/58, utf8 46/63 (each also with -fcomments), vm-byte 103/120, vm-utf8
  128/145 (each also with -fcomments), vm-noposs / vm-nolp / vm-tune-2 /
  vm-nopack 103/120 each, vm-i-byte 103/120, vm-i-utf8 88/105. Log
  `build/m6scratch/shadow_sweep.log`. Witnesses 40/40 against the IMPLEMENT
  binary.
- **REPLACE corpus pairs** (`build/m6scratch/ident_sweep.py`): `pcrec.base`
  (pre-edit, sha256 9d02e07d…) vs `pcrec.replace`, the same 4,444 x 14
  configs, `-p rx -o rx.c` in sibling dirs, `.c`, `.h`, rc and stderr
  compared: **62,216 pairs, 0 movers.** Reach per config (artifacts with a
  strided `+ W <=` / such forms / artifacts with VMSPAN's `+ 1 <=`): byte
  42/60/589, utf8 47/65/561, vm-byte 111/136/1529, vm-utf8 136/161/1284,
  vm-i-utf8 96/121/1241 (the strided count includes the lazy prefix's
  `+ W <=`). Log `build/m6scratch/ident_sweep.replace.log`.
- **Witness tier**: 40/40 SAME at Phase A, IMPLEMENT and REPLACE.
- **Other streams**: `--list-axes`, `--list-limits`, `--list-syntax`,
  `--list-families`, `--list-definitions`, `--list-schema`,
  `--list-analyses` identical; `--emit-ir` and `--emit-facts` identical on
  all 40 witnesses (80/80).
- **Light checks at the tip:** arms 338/0, manifest 13/0 (15 rows, 12
  delegated / 3 pending), forms 5/0, deleg 5/0 (10 rows), rows 127/0, stamps
  14/0, link 8/0, reach 4/0, arch 15/0, `limits_check.sh` 37/0, `make strict`
  clean. `make test-codegen` 15/15 and G2 quick 48,566,739/0 at the tip (§9).

## 5. C12 / C17 / C10 / C14 (measured by running)

- **C17**: VMSTRIDE `delegated` (emitters `vm_span_advance,
  vm_emit_span_scan`; companions `vm_cursor_rep,vm_cls_test`); new row
  **VMLAZY** (`vm_cursor_rep`, pending, step "after M6", trigger in the row
  text, Q-R10-7) with the new vocabulary line `span-count` (`while \(\w+ <
  %d\w*\) \{`, probed: it matches only the lazy prefix in src/gen and
  src/enc). `C17_ROW_FLOOR` 14 -> 15. At IMPLEMENT rule 2 was red on the
  shadow (it called `mf_emit`), as at M4/M7; gone at REPLACE.
- **C12**: `src/gen/emit_vm.c walk-open 1` DELETED; `src/gen/emit_vm.c
  span-count 1` ADDED (VMLAZY's form, seen for the first time by ruling, not
  a raise; recorded in the TSV header); 3 rows / 3 forms, floor 3 unchanged.
  `walk-back` (N6) and `span-decode` (N7U) stay.
- **C10**: `D91_LOOP` gains VMSTRIDE (budget 2).
- **C14**: form_checks.py asserts `MF_MAX_TERM >= VM_MAX_STRIDE`, the enum
  READ from emit_vm.c (hard-fail if absent), with its own control (lowered to
  31, only the stride assert fires): 4 -> 5 checks.

## 6. Sabotage

Every figure HAND-MEASURED (plant applied to the worktree, tree rebuilt, the
row's suites run, restored and rebuilt, `restored-clean` checked by git;
`build/m6scratch/plant.sh`, logs `build/m6scratch/plants/`). Every new row's
SAB_REACH / SAB_REACH_POP reaches on the clean tree (`build/m6scratch/
reach.sh`, the matrix's own evaluation).

| row | anchor | defect | measured |
|---|---|---|---|
| S511 | RE-AIMED (Q-R10-8) to `tests/memfn/site_manifest.tsv` | VMSTRIDE flipped back to `pending` | memfnmanifest 2 failed / 13 passed (rule 4 on both emitters); POP on the delegated row |
| S526 | RE-ANCHORED twice (A: the new `#define MF_MAX_TERM 32`; B: re-aimed to the binding bound) | MF_MAX_TERM 32 -> 31, emit_vm.c's build copy removed (FILE2) | the tree BUILDS; memfnforms 1 failed / 4 passed (C14 stride assert) |
| S676 (new) | generic.c `stmt_advance`'s term loop | only term 0 rendered at W > 1 | harness possessify.rxt 20/3517 (`(?:a\.)+\b` on "aa.a." (0,2) not (1,3)); memfnarms 14/324 (pins, freezes, check 13: 829,945 of 5,142,837 calls wrong) |
| S677 (new) | the ` && ` join | terms `||`-joined | harness possessify.rxt 223/3314; memfnarms 14/324 (check 13 fails to build, -Werror=parentheses) |
| S678 (new) | memfn_sites.c `adv_member` | member[0] for every term | harness possessify.rxt 20/3517; whole corpus: every failing cell in possessify.rxt |
| S680 (new) | emit_vm.c `vm_span_advance`'s `.span` | strided `it_` cap lost | harness d27_bodies.rxt 4/155 (`(ab){2,4}` on "ababababab" (0,10) not (0,8)); whole corpus 12 cases |
| S681 (new) | compose.c `skip_check` reverse refusal | strided reverse accepted | memfnarms 1/337 (stride-reverse RENDER) |
| S682 (new) | compose.c `skip_check` offset rule | offsets 0, 2 accepted | memfnarms 1/337 (stride-gap RENDER) |
| S683 (new) | memfn_sites.def VMSTRIDE row | budget DELEG_SCAN | memfndeleg 2/3 |
| S684 (new) | emit_vm.c `vm_emit_span_scan`'s door call | pcrec spells `while ((%s_span_cursor + %d <= %s)` again at W > 1 | memfnmanifest 1/12 (rule 3), memfnforms 1/4 (C12 walk-open 1 > ceiling 0) |
| S685 (new) | search_vocab.tsv `span-count` | the line blinded | memfnmanifest 1/12 (rule 4 on VMLAZY) |

S679 (`more` keeps `+ 1` at W > 1) NOT built: its detector is the
sanitizer arm, a measurement first (the scoping report's MEASURE).
`python3 scripts/m6read_check_sab_anchors.py`: **570 sabotages / 588 anchor
sites, all resolve.** Maps REGENERATED by their scripts (never hand-edited):
`docs/design/start_table/{call_graph.txt, sabotage_anchors.tsv, .total}`
(`call_graph.py .`; `sabotage_anchors.py . call_graph.txt
refactor_edit_set.tsv`) and `docs/design/dec_fallback/{call_graph_fallback.txt,
sabotage_anchors.tsv, .summary}` (`--family fallback`; `--final after-B6
--edit-names`); both exit 2 on the pre-existing S571. `.total` now carries
the script's UNRESOLVED line verbatim (M7's copy had dropped it).
`inventory_check.py` 150/150.

## 7. G2: what a blinded lane must add (memfn/tests/ not edited)

G2 builds and is green against MF_SITE_ABI 8 (quick tier 48,566,739/0 at
Phase A). Needs, in CONTRACT terms only (memfn.h is the source):

1. **The strided ADVANCE oracle.** STMT / SKIP / ADVANCE over W in
   1..MF_MAX_TERM REQUIRED SET terms, term i at offset i. From cursor c0 the
   final cursor is c0 + j·W, j the least j >= 0 with: `more` false at
   c0 + j·W (pcrec's `more` is "c + W <= B"), or j == span_hi (span_hi counts
   ITERATIONS), or some i < W with s[c0 + j·W + i] not in S_i. The counter
   advances exactly j times from its start, owned by the kit or the caller
   (count_by_caller). W = 1 is today's ADVANCE.
2. **The generated space.** W in {1, 2, 3, 7, 8, 9, 16, 31, 32}; B − c0
   around every multiple of W ± 1 (a partial last block is never read); caps
   0, 1, around the run length, unbounded; per-position sets singleton,
   range, sparse, full, EMPTY at one position; subjects failing at every
   position i < W.
3. **Reads.** Only [cursor, cursor + W) per iteration, only while `more`
   holds: guard pages at B; `s` NULL with B = 0.
4. **Hooks.** The member hook present (called once per term with that
   term's id, its text opaque) AND absent (the kit's own test of the byte at
   offset i, `s[cursor + i]`: `s` and `cursor` REQUIRED at W > 1, refused
   naming each when unstated; at W = 1 neither is required and the byte is
   `peek`). Non-identifier `s`/`cursor` texts must work (the generic row
   parenthesizes).
5. **Refusals** (each names its field): `reverse` 1 at W > 1 (`reverse`);
   offsets not 0..W-1 or out of order, an OPTIONAL term, a non-SET term
   (`pred`); nterm > MF_MAX_TERM; a non-ADVANCE SKIP with nterm > 1 (`pred`,
   Q-G2-9 still holds there); MF_SITE_ABI 7 at an 8 kit.
6. **Rows / K1.** Check (b) must see the generic row render strided sites;
   FLOOR_ROWS unchanged (no new row). `G2_MAXT` re-read (MF_MAX_TERM 32). K1:
   `mf_ref_skip_blocks(s, n, sets, w)` is the reference (a cap K is the
   caller's n: min(n, K·w)).

## 8. The slot chain the manager must run

1. Merge `lane/m6` into `lane/memfn-m6` ALONE; `make -j16 && make strict`.
2. Identity gate, 0 movers on every stream, BOTH bases, ref = M6's
   merge-base (re-take it after any refactor-B merge, Q-R10-9):
   `python3 scripts/emit_sweep.py --ref <merge-base> --bases byte,utf8`
   with `--extra --engine=vm`, `--extra -fno-possessify`, `--extra
   -fno-length-prune`, `--extra -fcomments`, `--extra -fno-cls-pack`,
   `--extra --tune=-2`, judged by `python3 docs/design/memfn/probes/lxrun/
   memfn_r4c_gate.py --zero-dumps <out>`; print the reach per (base, arm):
   `_span_cursor \+ ([2-9]|[1-9][0-9]+) <=` (VMSTRIDE), `_span_cursor \+ 1 <=`
   (VMSPAN control).
3. The blinded G2 lane (§7) may land before or after; G2 is green today.
   G2 full (`make test-memfn-g2-full`).
4. `scripts/perfrun --label m6 -- <log>`; verdict `grep -E '\*\*\*
   \[(Makefile:[0-9]+: )?test-'`.
5. Mech, each SOLO (`bash tests/mech/run_sabotage_matrix.sh <id>`), rule (b):
   rows anchored in the changed definitions (`vm_span_advance`,
   `vm_emit_span_scan`, `vm_cursor_rep`, `stay_advance`, `edge_advance`,
   `pcrec_memfn_advance_site`, `adv_member`, memfn_sites.*), every row on a
   `memfn/` or `tests/memfn/` file or a memfn arm, the re-aimed rows, the new
   rows and the scoping report's confidence set — **66 rows**: S37 S39 S56
   S57 S61 S68 S72 S185 S214 S265 S267 S279 S285 S443 S444 S445 S447 S450
   S454 S455 S460 S464 S510 S511 S512 S513 S514 S515 S516 S517 S518 S519 S520
   S521 S522 S523 S524 S525 S526 S527 S528 S529 S570 S571 S573 S614 S615 S616
   S617 S618 S619 S666 S667 S669 S670 S671 S673 S676 S677 S678 S680 S681 S682
   S683 S684 S685. Expect every row DETECTED except those whose files expect
   otherwise (S525 TRIPWIRE). S616/S214 (the generic cap line) now also reach
   VMSTRIDE: DETECTED with more reach.
6. Not lane work: the kit's responses.md entry and journal line (single
   writer); pcrec's dev_journal line and plan.md's [MEMFN] M6 state;
   Frank's Q-R10-1 (N6).

## 9. Validation at the tip (light)

- `make test-codegen` (PROCS=4, pinned 12-15): **15/15 scripts passed, rc 0**
  (`build/m6scratch/test-codegen.log`).
- G2 quick at the tip: **48,566,739 passed / 0 failed**
  (`build/m6scratch/g2q_final.log`).
- memfn checks, `make strict`, `limits_check.sh`, m6read: §4, §6.

## 10. Charter checklist

| item | state |
|---|---|
| MF_SITE_ABI 7 -> 8, NO MF_VOCAB bump; readers by grep | DONE (§2) |
| multi-term ADVANCE (Q-G2-9 relaxed on ADVANCE), refusals naming fields | DONE (§2) |
| MF_MAX_TERM 8 -> 32 with a `_Static_assert` (emit_vm.c) + C14 | DONE (§2, §5) |
| span_hi restated as iterations (Q-R10-5) | DONE (memfn.h) |
| no silent stride default (Q-R10-12): every builder states `stride`, 0 refused | DONE (§3) |
| Q-R10-4 kit reads `s[cursor + i]`; `s`/`cursor` required at W > 1 | DONE (§2) |
| Q-R10-6 one builder, separate VMSTRIDE row; STAY/EDGE state stride 1 | DONE (§3) |
| fixtures, gate cases (positive/refuse), K1, frozen targets cut from pre-edit artifacts | DONE (§2) |
| Phase A zero pcrec bytes, both encodings | DONE (40/40) |
| I1 shadow over the corpus, both encodings, VM/default routes, comment tiers, strides incl. 30/32, 0 mismatches, sites per stride | DONE (§4: 62,216 compiles, 1,477 sites) |
| REPLACE: pcrec loop text deleted, VMSTRIDE delegated | DONE |
| Q-R10-7 VMLAZY pending by function + C17 line + C17/C12 literals | DONE (§5) |
| N6 untouched (row, walk-back, C12 row, vm_rev_emit) | DONE |
| Q-R10-8 S511 re-aimed (manifest flip); S526 re-anchored | DONE (§6) |
| new rows from S676-S685, grepped free, reaching, hand-measured DETECTED | DONE: S676-S678, S680-S685; S679 NOT BUILT (measure first) |
| call_graph/sabotage_anchors re-derived; m6read green; start_table/dec_fallback regenerated by script | DONE (§6) |
| zero movers: corpus pairs both encodings + engine arms + comment tiers; 25+ witnesses; --list-*/--emit-ir/--emit-facts | DONE (§4) |
| CLAUDE.md files (memfn, memfn/include, memfn/src, src/gen, tests/memfn, tests/memfn/pins/m6_target, tests/mech, docs/dev/lanes) | DONE |
| no docs/spec hunk | DONE: none needed (nothing caller-observable moved) |
| memfn/tests untouched; G2's needs listed | DONE (§7) |
| identity gate, make test, G2 full, mech rows | OWED to the slot (§8) |

## 11. N6 retirement (D147 add. 12)

Frank ruled (D147 addendum 12) that N6 (`vm_rev_emit`'s backward walk) is
not a search site: a mirrored one-position VM step, which integration.md
§R4.3.4 already excludes. No change to src/ or the kit's code.

**Deleted:** the N6 row of tests/memfn/site_manifest.tsv; the `walk-back`
line of tests/memfn/search_vocab.tsv; the `src/gen/emit_vm.c walk-back` row
of tests/memfn/c12_ceilings.tsv.

**Literals moved (each commented, citing D147 add. 12):**
`C17_ROW_FLOOR` 15 -> 14 (run_site_manifest.sh); `C12_CEIL_ROWS_FLOOR`
3 -> 2 (run_form_checks.sh); the c12_ceilings.tsv header's row/total echo
(3 -> 2 forms). C17 now reads 12 delegated / 2 pending (N7U, VMLAZY).

**Sabotage rows touched** (none retired; no other row anchors on N6, the
`walk-back` line or its C12 row; S160's `vm_rev_emit` default: and S490's
N5/N6 are the unrelated cand_rows/engine N6, untouched):
- S512 (row below floor): REACH_POP re-anchored `^C17_ROW_FLOOR=13$` ->
  `^C17_ROW_FLOOR=14[[:space:]]` (it had read the stale 13 since the M7/M6
  floor raises, and the live literal carries a trailing comment). Hand
  measure, plant applied to the tree and reverted: clean 12 passed / 0
  failed; plant (SETREST commented out) `FAIL: the manifest holds 13 rows,
  below its K35 floor of 14`, 11 passed / 1 failed.
- S511 (stale pending row): comment note and figure updated only. Hand
  measure: clean 12/0; plant (VMSTRIDE flipped to pending) 2 failed (rule 4
  on vm_emit_span_scan and vm_span_advance) / 12 passed.
- S525, S685 (vocabulary rows): read, unaffected (S685 plants `span-count`,
  S525 `memchr`; neither touches walk-back). Not re-measured.

**Commands:** `bash tests/memfn/run_site_manifest.sh` (12/0 clean),
`bash tests/memfn/run_form_checks.sh` (C12 "2 forms in 2 groups", 5/0),
`python3 scripts/m6read_check_sab_anchors.py` (all anchors resolve),
`make -j4 strict` (clean), all under `taskset -c 12-15`. Docs updated:
tests/memfn/CLAUDE.md, integration.md (§8.5 inventory, §R4.3.4 lists, §22 M6,
end-state notes, in place). mech matrix NOT run: manager's slot, rows S511 S512.
