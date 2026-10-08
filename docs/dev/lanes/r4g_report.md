# r4g — [MEMFN] R4g / M2: PF migrates into the kit, zero movers

Lane r4g (opus), 2026-10-07, branch `lane/r4g` cut from the kit branch
`lane/memfn-r4g` (= main 5e9ec93c). Charter: the kit manager's brief (main's
edit set and conditions, `memfn/docs/responses.md` notice 2026-10-07 "R4g
edit set vs [START-TABLE] C4-C7"), integration.md §22 (rev4.x and rev4.8 R4g
rows), §9.4 M2, §15.7, §15.2, §19 rows 6-7, §14, row_contracts.md §1-§2.
Every file:line below is THIS tip's (`lane/r4g`).

## 1. Summary (resume from here)

- **No STOP.** No CandPf/CandRow field and no `cand_rows[]` row changed
  (condition 1). No emitted byte moved on any compile I made (condition 3,
  §4). No start decision moved (§3). No pcrec abi event, no spec hunk owed
  (nothing a caller observes changed).
- **Commits** (`git log 5e9ec93c..lane/r4g`): `94122bd0` IMPLEMENT (the
  kit's arm + I1 shadow), `5b7e9280` REPLACE (pcrec's spelling deleted,
  checks), `c83d4395` mech re-pins, `1714c435` docs + anchors re-derived,
  then this report.
- **The kit's new rows:** `memfn/src/pffind.c`, two renderers as four rows
  (`pf_memchr`, `pf_memchr_bounded`, `pf_walk`, `pf_walk_bounded`), each
  with `uses`/`serves` in fields.def terms; the gate passes them on every PF
  site pcrec sends (each shape compiled, §4; C5 fixtures, §2).
- **One deliberate widening of main's edit set** (§2.3): the memchr forms'
  NULL test and position store moved WITH the `memchr` line, because the
  line alone yields a pointer, which is not a FIND result and which the
  generic row could not render. Every guard, the `return 0` TEXT (passed as
  pcrec's `on_miss` hook), the clamp TEXT (pcrec's `miss` hook), the entry
  tests, the re-seeds and the comments stay pcrec's.
- **Mech:** 3 rows re-pinned (S68 kit-side, S524, S478), 6 verified
  unchanged; all 9 solo-run DETECTED (§5). [SABANCHOR] 497 rows / 515
  sites, all resolve.
- **§19 row 6 is NOT moved** (§2.4): its rarity half is a pre-check
  ADMISSION decision; it needs a ruling.
- **OWED** (the manager's slot, post-C4 main): §8.

## 2. The edit set as built

### 2.1 The kit (memfn/)

- **`memfn/src/pffind.c`** (NEW; SPDX 0BSD; `Provenance: pcrec 5e9ec93c
  (relicensed 0BSD by its author, D145 addendum 1)`; PROVENANCE.md row,
  C16 13/13). ONE site shape: FIND / STMT / ASSIGN over one REQUIRED SET
  term at offset 0 of a REQUIRED predicate, forward, `result` the position.
  - `pf_memchr` (one-byte set, `end_back` 0, `empty` EXCLUDED,
    `on_miss_leaves` 1, the `miss_leaves` column set):
    `const void *q = memchr(s + lo, b, n - lo);` / `if (!q) <on_miss>` /
    `<result> = (size_t)((const unsigned char *)q - s);`.
  - `pf_memchr_bounded` (`end_back` 1, EXCLUDED, no `on_miss`): the
    `memchr` over `n - 1 - lo`, then `<result> = q ? (…) \n <pad>: <miss>;`
    with `:` under `?` (pad = strlen(result) + 5). `miss` must be exactly
    `<n> - 1` (the range's end; `miss_is_end`).
  - `pf_walk` / `pf_walk_bounded` (a set pcrec names by `table_ref`, `empty`
    NOP): `while (lo[ + 1] < n && !<table_name(ref)>[s[lo]]) lo++;`. In
    place: `result` must be `lo`'s text; `miss` the range's end (MF_MISS_N
    at `end_back` 0, `<n> - 1` at 1).
  - Contracts (end of file, each declaration cited by function): `uses`
    per (STMT, ASSIGN) and phase; `serves`: s/n/lo IDENT, `floor` 0,
    `result_decl` 0, `note` 0 (never called: a stated writer declines),
    `on_miss` JUMP|BRACED on `pf_memchr` and 0 elsewhere, `miss` ANY /
    OTHER / MISS_N / OTHER by row, `table_ref` NONE (memchr) / REF (walk),
    `empty` E_EXCLUDED / E_NOP, `end_back` ZERO / ONE, `on_miss_leaves`
    YES / NO. What a class cannot say (the set's size, `result == lo`,
    the miss text `n - 1`) is held by the predicates and re-read at the use
    (`pf_use_ok`, `pf_walk_use`), refused loudly on a mismatch.
  - `memchr` noted on the libc record and `MF_INC_STRING_H` set at the
    render (the R4c/libcnote rule). D149: no tuning constant.
- `kit.h`: the four externs; `compose.c`: the four rows above the generic
  row, header comments.
- No `MF_SITE_ABI`/`MF_VOCAB` change: (FIND, ASSIGN, SET) is in the
  vocabulary.

### 2.2 pcrec (src/)

- `src/gen/memfn_sites.def`: `DELEG_SITE(PF, MF_OP_FIND,
  DELEG_H(MF_H_ASSIGN), MF_TK_SET, DELEG_SCAN, MF_USE_POSITION)` (C10:
  PF was already in D91_SCAN; `run_deleg_sites.sh` 5/0).
- `src/core/internal.h`: `PcrecFind` gains `cx`, `set`, `on_miss`;
  `table` becomes a `PcrecFindTable` enum (no `strcmp` on a tag; the enum
  value IS the site's `table_ref`).
- `src/gen/emit_dfa.c`:
  - `find_table_tag[]`, `find_table_name` (the kit's `table_name` hook:
    `<p>_<tag>`), `find_site` (the description), `pcrec_emit_find` (now:
    describe, then the door `pcrec_memfn_emit(cx, DELEG_PF, …)`; it spells
    no form);
  - `pf_emit_find` takes the caller's `on_miss`; `pf_emit_memchr` passes
    `"return 0;"` and lost its two lines (the NULL test, the store);
    `pf_emit_memchr_bounded` and `pf_emit_first_memchr_bounded` lost the
    clamped store (two lines each); the walk callers are unchanged in text;
  - `pf_vm_emit_first_class` fills `v` ahead of the entry test (the site's
    SET term needs it at both calls), one indent level out.
- IMPLEMENT only (deleted at REPLACE): `pcrec_memfn_shadow` in
  `memfn_sites.c` (a scratch art and StrBuf, the kit's text compared byte
  for byte with the span pcrec had just written for the same site).

### 2.3 The one widening of main's edit set, and why

Main cleared "the memchr find line". The line is
`const void *q = memchr(…);`: its value is a POINTER (NULL on a miss). A
FIND's result is a POSITION or `miss` (§8.3 rule 3, §14.3); a site whose
`result` were `q` would be dishonest, and the test that proves it is the
generic row, which renders every site in the vocabulary: it would write a
`size_t` into `q`, and pcrec's following `if (!q)` would be wrong. So the
smallest honest site is the search, its NULL test and the store, which is
§15.7's own shape minus the guard. What moved and what did not:

| text | owner now | how |
|---|---|---|
| `if (scan_position >= subject_length) return 0;` before the memchr | pcrec | unchanged line (6018); the site's `empty` is EXCLUDED because of it |
| `if (scan_position + 1 < subject_length) {` around the bounded memchr | pcrec | unchanged (6038, 6665) |
| `const void *q = memchr(…);` | kit | the search |
| `if (!q) return 0;` | kit writes `if (!q) `, pcrec gives `return 0;` | `on_miss` hook (`pf_emit_memchr`, 6019), `on_miss_leaves` 1 |
| `scan_position = (size_t)(… q - subject);` | kit | the ASSIGN store |
| `… : subject_length - 1;` (the bounded clamp) | kit writes the store, pcrec gives `subject_length - 1` | `miss` hook (`find_site`) |
| `while (… && !<tbl>[…]) pos++;` | kit | the walk |
| `if (scan_position >= subject_length) return 0;` after the walk / `attempt_position` after the seek | pcrec | unchanged (6052, 6782) |
| `size_t skip_from = …;`, the re-seed, `pf_open`, the comments, the tables | pcrec | unchanged |

`q` is now kit-internal: nothing after the site reads it (the re-seed
reads `skip_from` and the position; checked by grep).

### 2.4 §19 rows 6 and 7

- **Row 7** (K84's `strcmp` readers): already fixed on main (START-SET
  stage 1, `DfaPf.scan`; responses.md's notice says so). Nothing to do.
- **Row 6** (`req_byte_dominated_by` → `pcrec_find_no_commoner`, G1's
  elision of the pre-check): **not moved.** Its rarity half would make the
  necessary byte an OPTIONAL term of the PF site and let the kit decide
  whether testing it pays. That changes the PF site's shape (a second
  term) and moves an ADMISSION decision of the pre-check into the kit;
  main's clearance keeps every predicate and admission pcrec's ("a
  migration moves search TEXT, never a start DECISION"), and the elision
  is read in `req_admits[]`, outside the edit set. Proposal: rule it as
  its own step after C5b (it touches the pre-check's admission table,
  which [START-TABLE]/[DEC-FALLBACK] edit), byte-identical then by a
  baseline row that always tests (or never tests) exactly as pcrec does.

### 2.5 Checks re-pinned in the REPLACE commit

- Manifest (`tests/memfn/site_manifest.tsv`): PF `pending` → `delegated`;
  emitters `find_site,pcrec_emit_find` (the builder and the door's caller,
  the PRE precedent); companions gain `pf_emit_first_memchr_bounded`,
  `pf_emit_first_class_bounded`, `find_table_name`.
- C12 (`tests/memfn/c12_ceilings.tsv`): `emit_dfa.c` memchr 2 → 1 (the one
  left is `emit_attempt`, M4); the walk-fmt row (1 → 0) deleted;
  `C12_CEIL_ROWS_FLOOR` 9 → 8 (`run_form_checks.sh`). Form checks 4/0.
  The header's "13 forms" was already stale (the check counted 14); now 12.
- C5 (`tests/memfn/arm_fixtures.c`, `pins/arms.tsv`, `run_arm_pins.sh`):
  `render_pf` with pcrec's `find_site` hooks; fixtures `pf-memchr`,
  `pf-memchr-bounded`, `pf-walk`, `pf-walk-bounded` and the edge
  `pf-decline-not-in-place` (generic); 10 rows, `ARMS_ROW_FLOOR` 38 → 48,
  `ARMS_EXPECTED` += `pf_memchr pf_walk`. `make test-memfn-arms` 126/0
  (48 rows, 24 fixtures, 20 gate cases).
- `make test-memfn-stamps` 14/0 (the FORMS half UNREACHED, as before).

## 3. Decision reads left on pcrec's side (named)

All `src/gen/emit_dfa.c`:

| # | line | read |
|---|---|---|
| P1 | 5988-5990 (`pf_emit_find`) | `f->pf->u.pf.scan == PF_SCAN_BYTE` (memchr vs table) and `f->pf->u.pf.scan_set` (`start_bytes` vs `can_begin_match`): the row `cand_select(NEXT)` chose |
| P2 | 6019, 6039, 6051, 6068, 6667, 6681 (the `pf_emit_*` callers) | `holdback` 0/1: the D11 bound the row's form carries (→ `end_back`) |
| P3 | 6019 | `on_miss` `"return 0;"`: what a NULL hit does (the search ends) |
| P4 | 5991-5992 | `f->cand.set` / `f->cand.byte`: the candidate set `unanch_start`/`pf_scan_set_of` computed, read, not decided |
| P5 | 6018, 6038, 6052, 6665 | the guards (`pos >= n` before a memchr and after a walk; `pos + 1 < n` around a bounded memchr): pcrec text, the reason the memchr site's `empty` is EXCLUDED |
| P6 | 6772-6773, 6782 (`pf_vm_emit_first_class`) | `s->ss->bits` (the start_set fact, read), `entry` (where the table is declared), the `attempt_position` guard |
| P7 | 5943-5950 (`find_site`) | `table`, `empty`, `on_miss_leaves` are DERIVED from P1/P2 (descriptions of the form pcrec chose), not decisions |

Not touched: every `pf_*_applies` predicate and deny, `cand_select`/
`dfa_pf_of`, `unanch_start`, `pf_scan_set_of`, `dfa_cand_scan`,
`pcrec_dfa_cand_ppm`, `pf_emit_moved_reseed`, `pf_emit_ofs*`/
`pf_block_ofs`, the tables, `cand_rows[]`. No `PCREC_CAND_TRACE_REC` sits in
an edited function (stc1's `pf-of` record at 6796 is in the caller).

## 4. Compile-identity evidence (condition 3)

Method: `build/pcrec` built at the branch tip BEFORE the first src edit,
copied to scratch as the reference; every compile with the same `-p rx` and
the same `-o` basename (`rx.c`, the trap learnings §3 records), `.c` and
`.h` compared with `cmp`. 41 of the 60 compiles used (14 reference + 14 at
IMPLEMENT + 13 at REPLACE). At IMPLEMENT the I1 shadow comparator ALSO ran
inside every one of those compiles: the kit's text for each PF site
rendered through a scratch art and compared byte for byte with pcrec's; a
mismatch fails the compile, so a passing compile is a per-site proof.

| id | args | stamp | IMPLEMENT | REPLACE |
|---|---|---|---|---|
| memchr | `x[a-z]*y` | DFA_PREFILTER `memchr` | SAME | SAME |
| memchrb | `-fno-start-set x[a-z]*$` | `memchr-bounded` | SAME | SAME |
| bcls | `[xy][a-z]*z` | `byte-class` | SAME | SAME |
| bclsb | `-fno-start-set [xy][a-z]*$` | `byte-class-bounded` | SAME | SAME |
| fmb | `--features all \B(?<!a)d` | `first-memchr-bounded` | SAME | SAME |
| fcb | `--features all \b(?:ab\|cd)\b` | `first-class-bounded` | SAME | SAME |
| vmhat | `--features all (ab)\1` | VM_START_SCAN `first-class` | SAME | SAME |
| u8vmhat | `--features all -e utf8 (ab)\1` | VM `first-class` | SAME | SAME |
| vmforce | `--engine=vm [ab]c+d` | VM `first-class` | SAME | SAME |
| ci | `-i xy[0-9]+q` | `byte-class` | SAME | SAME |
| cmtbcls | `-fcomments [xy][a-z]*z` | `byte-class` | SAME | SAME |
| noovl | `-fno-run-overlap x[a-z]*y` (site denies RUN_OVERLAP) | `memchr` | SAME | SAME |
| u8memchr | `-e utf8 é[a-z]*x` | `offset-set` (control: OFS, not PF) | SAME | SAME |

(One more reference/IMPLEMENT pair, `-e utf8 \b(?:ab|cd)\b`, refused in both
binaries for want of `--features all`; it measured nothing.) Every PF form
(both START-SET hats, the VM hat, the four plain prefilter forms) was hit;
0 movers.

## 5. Sabotage rows (condition 2)

`bash tests/mech/rows_for.sh <changed files>` lists every row whose
SAB_FILE is a changed file (it is file-level: ~150 rows on emit_dfa.c
alone); the rows ANCHORED in R4g's functions are the brief's nine,
confirmed against `sabotage_anchors.tsv`'s owner column and
`m6read_check_sab_anchors.py` (3 stale after REPLACE: S68, S524, S478; the
others' anchors are byte-unchanged lines in edited or adjacent functions).

| row | anchor now | planted defect (same as before) | solo verdict (`taskset -c 12-15`, HEAD c83d4395) |
|---|---|---|---|
| S68 | RE-PINNED kit-side: `memfn/src/pffind.c` `pf_walk_use`'s `kit_out(o, "%swhile (…) %s++;\n", …)` (as S285 at M1b) | the table walk advances via `<prefix>_next_pos(s, n, pos)` (the art's prefix = pcrec's D143 placeholder) instead of `pos++` | DETECTED `codegen:18fail/327pass,corpus:0fail/56pass` |
| S186 | unchanged (`pf_emit_ofs_reseed`) | offset-skip lands without re-seed | DETECTED `corpus:9fail/89pass,offsetskip:1fail/22pass` |
| S478 | RE-PINNED: `pf_vm_emit_first_class`'s `for … v[b] = s->ss->bits…` (one indent level out) | the emitted `rx_start_set` drops its lowest member | DETECTED `reach:ok(1/1),vmhat:561fail/18pass` |
| S481 | unchanged (`pf_emit_first_class_bounded`, `pf_emit_moved_reseed(c, f, in4);`) | first-class-bounded never re-seeds | DETECTED `reach:ok(1/1),dfahat:88fail/0pass` |
| S482 | unchanged (`pf_emit_first_memchr_bounded`, `…in8);`); its AFTER reads `q`, which the kit still declares in the same block | re-seed only on the clamp landing | DETECTED `reach:ok(1/1),dfahat:61fail/0pass` |
| S483 | unchanged (as S481) | re-seed only before n-1 | DETECTED `reach:ok(1/1),dfahat:14fail/0pass` |
| S484 | unchanged (as S482; AFTER reads `q`) | re-seed only after a hit | DETECTED `reach:ok(1/1),dfahat:19fail/0pass` |
| S485 | unchanged (`pf_emit_moved_reseed`) | unconditional re-seed | DETECTED `reach:ok(1/1),dfahat:14fail/0pass` |
| S524 | RE-PINNED: `pcrec_emit_find`'s `pcrec_memfn_emit(f->cx, DELEG_PF, s, &h, c);` | one more `memchr(` spelled in a listed emitter: the SECOND against the new ceiling 1 (C12) | DETECTED `reach:ok(2/2),memfnforms:1fail/3pass` |

9 of the 12 allowed calls, all rc 0, 0 unexpected/undetected/unreached/anomalies. Logs: `worktrees/memfn-slot/r4g/mech/S*.log`, chain `mech/chain.log`.

## 6. `docs/design/start_table/sabotage_anchors.tsv`

Re-derived on this tree by the file's own method (`call_graph.py ROOT >
call_graph.txt`, `sabotage_anchors.py ROOT call_graph.txt
refactor_edit_set.tsv`, the stc3 precedent); `call_graph.txt` and
`sabotage_anchors.total` re-derived with it. Against the committed file:
apart from line numbers (every row after the edit moves), ONE row changes
owner: S68 `src/gen/emit_dfa.c pcrec_emit_find def` → `memfn/src/pffind.c
file:… outside` (OTHER either way). The after-C5b rows now point at R4g's
anchors: S478 `pf_vm_emit_first_class` 6772, S481/S483
`pf_emit_first_class_bounded` 6682, S482/S484 `pf_emit_first_memchr_bounded`
6668, all still RE-RUN after-C5b. S524 `pcrec_emit_find` 5977. Totals:
515 sites, 497 ids, family 114, re-aim 12, re-run 102, 0 count mismatches;
`RESOLUTION def 448 → 447, outside 49 → 50` (S68). The one UNRESOLVED src
site (S571 in memfn_sites.c, a data line) is pre-existing on main
(`rc=2` both before and after; the committed `.total` already lists it).

## 7. G2 needs (for the blinded author; contract terms only)

The kit now has four rows for one site shape G2 should cover directly:

- FIND / STMT / ASSIGN, one REQUIRED SET term at offset 0 (the whole
  predicate REQUIRED), forward, `guard_by_caller` 0, no `result_decl`, no
  `note`, no `floor`:
  1. a ONE-member set, no `table_ref`, `end_back` 0, `empty` EXCLUDED,
     `on_miss_leaves` 1, `on_miss` a leaving statement (`return …;`,
     `goto`), any `miss`: on a hit `result` = the leftmost position of the
     byte in [lo, n); on none, `on_miss` runs. Precondition: the caller has
     proven lo < n (EXCLUDED), so G2 must generate only lo < n subjects
     for this cell (and the generic row's rendering for EXCLUDED sites is
     the control).
  2. the same set, `end_back` 1, EXCLUDED (lo + 1 < n proven), no
     `on_miss`, `miss` stated as the text `<n> - 1`: `result` = the
     leftmost hit in [lo, n - 1), else `n - 1`.
  3. a multi-member set reached by a `table_ref` (the `table_name` hook
     names a 256-entry table whose nonzero entries ARE the set; rule 7),
     `empty` NOP, `end_back` 0, `result` the SAME text as `lo` (in place),
     `miss` MF_MISS_N (or `n`'s text): `lo` ends at the leftmost member in
     [lo, n), else at `n`; on an empty range (lo ≥ n, lo > n included)
     nothing is written.
  4. as 3 with `end_back` 1 and `miss` `<n> - 1`: stops at n - 1; empty iff
     lo + 1 ≥ n.
- Edges worth a family: `result` ≠ `lo` on a table site (must not take the
  walk: the generic row renders it); a stated `floor`, `note`,
  `result_decl` or `on_miss` (on cases 2-4) must decline those rows; a
  `miss` other than the range's end on 2-4 must not take the PF rows; the
  table's contents disagreeing with `set[32]` is a caller defect G2 can
  plant to show the walk reads the TABLE (rule 7) while the generic row
  reads the bits.
- `MEMFN_LIBC` must list `memchr` for cases 1-2 and nothing for 3-4.

G2 quick tier, run once (`taskset -c 12-15 gnutimeout 2400 bash memfn/tests/run_g2.sh --quick`, log `worktrees/memfn-slot/r4g/g2q1.log`): checks passed 38,989,416, failed 0, rc 0; ENFORCED classes all at or above their floors. **No G2 family reached the new rows**: the per-family form ids are `generic`, `runcmp`, `ofsskip`, `precheck` only (distinct ids 4, floor 4), so the four PF rows are exercised today by C5's fixtures and pcrec's own compiles only. That is the G2 need above; its FORM_FLOORS will want `pf_memchr` and `pf_walk` once the families exist.

## 8. VALIDATION OWED (manager's slot, post-C4 main)

Exact commands, in the main tree after this branch reaches the kit branch:

1. `git merge lane/r4g` (via the kit branch) ALONE in its own command; read
   the result; resolve; then `make -j16 && make strict`.
2. The identity gate against the main tip the merge sits on (zero movers
   expected on every stream):
   `python3 scripts/emit_sweep.py --ref <post-C4 main tip> …` (the R4c
   invocation, every axis and both comment tiers), judged by
   `python3 docs/design/memfn/probes/lxrun/memfn_r4c_gate.py <sweep out>`.
3. The N2 census, expecting 0 refusals / 0 would-declines on every pcrec
   site (the PF site is new to it):
   `bash docs/design/memfn/probes/rowcon/n2_census.sh`.
4. `make -k -j16 -Otarget test`; verdict from
   `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` (empty = green). New
   ground for it: C17 rule 2 must see the PF row REACHED through the door
   (`pcrec_emit_find` → `pcrec_memfn_emit`) and rule 3 must find no form in
   `find_site`/`pcrec_emit_find`; `test-memfn-deleg`, `-forms`, `-arms`,
   `-manifest`, `-reach`, `test-startset`, `test-codegen` ([SABANCHOR]).
5. Mech, solo, for `rows_for.sh`'s full list on the merged tree:
   `for r in $(bash tests/mech/rows_for.sh src/gen/emit_dfa.c src/core/internal.h src/gen/memfn_sites.def memfn/src/compose.c memfn/src/kit.h memfn/src/pffind.c); do bash tests/mech/run_sabotage_matrix.sh "$r"; done`
   (this lane ran the nine anchored rows, §5).
6. G2 full (`make test-memfn-g2-full`) once the blinded author has the
   families of §7.

## 9. Charter vs committed

| charter item | committed |
|---|---|
| SEARCH TEXT behind the kit: `pcrec_emit_find`, `pf_emit_find`, the memchr line of `pf_emit_memchr`(+bounded), the walk of `pf_emit_bcls`(+bounded), the VM hat's FIND | ✓ all; memchr widened to search + NULL test + store (§2.3, reasoned) |
| `pf_emit_first_*_bounded` follow through `pf_emit_find` with no text edit | first-class: ✓ no edit; first-memchr: its clamped store moved into the site (2 lines deleted), per §2.3 |
| memfn_sites.def / DELEG_SITES PF | ✓ |
| manifest PF pending → delegated | ✓ |
| C12 `memchr(` 3 → 1 | ✓ as measured on today's tree: 2 → 1, plus walk-fmt 1 → 0 |
| stays pcrec-side: guards, `return 0`s, clamps, comments, predicates, cand_select, unanch_start, pf_scan_set_of, dfa_cand_scan, cand_ppm, reseed, tables | ✓ (§3; `return 0`/clamp text as hooks) |
| new kit rows declare uses/serves, pass the gate on every PF site | ✓ (§2.1, §4, C5) |
| condition 1: no CandPf/CandRow change | ✓ |
| condition 2: re-pin + solo-run S68 S186 S478 S481-S485 S524; anchors tsv re-derived | ✓ (§5, §6) |
| condition 3: zero movers on ≤ 60 compiles across the shapes vs a pre-edit binary | ✓ 41 compiles, 0 movers (§4) |
| CLAUDE.md, PROVENANCE/SPDX | ✓ memfn/src, src/gen, tests/memfn; PROVENANCE row |
| `python3 scripts/m6read_check_sab_anchors.py` | ✓ all resolve |
| §19 row 6 rarity half | ✗ not moved, ruling requested (§2.4) |
| §19 row 7 (K84) | already done on main |
