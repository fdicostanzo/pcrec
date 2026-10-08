# m4 — [MEMFN] R-7 / M4: MLINE migrates into the kit, zero movers

Lane m4 (opus), 2026-10-08, branch `lane/m4` cut from the kit branch
`lane/memfn-m4` (main post-R4h, post-advnorm, abi 68, plus kit ledger
entries). Charter: the kit manager's brief; memfn/docs/requests.md R-7;
memfn/docs/responses.md (the R-7 ack, the "R-7 (M4, MLINE): edit set and
overlap" notice with gaps G1-G3 and rulings Q-R7-1/2/3, "R-7 plan ACKED");
integration.md §15.7 and §14; the R4g/R4h precedents. Rulings file
`m4_rulings.md` R1 (ids S617-S619; S511 re-aimed). Every file:line below is
this branch's tip.

## 1. Summary (resume from here)

- **No STOP.** No emitted byte moved on any compile made (§4). No abi event,
  no spec hunk (nothing a caller observes changed).
- **Commits** (`git log 242b5180..lane/m4`, from the kit branch tip):
  - `07bfa7e4` PHASE A, M4 prep (kit-only): MF_SITE_ABI 6 (Q-R7-1/2/3), row
    `pf_memchr_back`, fixtures, gate cases, check 9;
  - `ecc43b4a` IMPLEMENT: `PcrecFind` generalized (site id, term offset,
    floor), DELEG_SITES row MLINE, the [M4 I1] shadow comparator live;
  - `a3d65a59` REPLACE: pcrec's MLINE text and the shadow deleted; manifest,
    C12, rows.tsv, sabotage re-aims/new rows, mech arm `memfnarms`;
  - `a40e538d` sabotage figures, start_table anchors re-derived, CLAUDE.md,
    integration.md §15.7 as built;
  - then this report.
- **OWED to the slot** (§8): identity gate, N2 census (pins
  `pf_memchr_back`'s pcrec_floor), G2 full, `make test`, 38 solo mech rows.
- **G2 IS RED, BY DESIGN, until a blinded lane re-derives it** (§7): Q-R7-1
  changes the range of a reads-below FIND, which G2's oracle (written to
  §14.4's old `[lo, n - end_back)`) still uses, and the new row is not
  reached by any G2 family (check (b)). `make test-memfn-g2` (a `make test`
  section) therefore fails until that lane lands. The kit manager must
  sequence it BEFORE the merge's `make test`.

## 2. PHASE A: M4 prep (kit-only, zero pcrec bytes; `07bfa7e4`)

| gap / ruling | what changed | where |
|---|---|---|
| G1 / Q-R7-1 (MF_SITE_ABI 5 -> 6) | A READS-BELOW FIND (every term's `offset + len <= 0`; E the largest) is bounded by its reads: c in [lo, n] with every read below n - end_back, i.e. `c + d <= n`, d = max(0, end_back + E); empty iff lo + d > n. Every other FIND and every other op keep [lo, n - end_back). The generic row's FIND loop (forward and reverse) and its NOP empty test change ONLY for such sites (`reads_below_d`); ALL_PRESENT's predicates and SKIP are untouched. No delegated site had one before M4. The note that [ENG-TACTICS]' "resume at hit + 1" is this same range is in memfn.h (MF_OP_FIND) and integration.md §15.7; nothing is designed for it. | memfn.h `MF_OP_FIND`, `MF_SITE_ABI`; generic.c `reads_below_d`, `find_loop`, `stmt_value` |
| G2 / Q-R7-2 | `MF_EMPTY_AT_N`, a proven-fact class: lo <= n AND the subject non-NULL, so the scanned bytes are empty only as lo == n over a valid pointer; outcome MISS's. A memchr row renders no empty test under it (a zero-length memchr misses). Refused on ADVANCE like MISS. EXCLUDED is deliberately NOT enough for the new row: on a read-bounded range it proves lo <= n only, so at n == 0 the subject may be NULL (K27). | memfn.h `mf_empty`; fields.def class `E_AT_N`; gate.c `cl_empty`; compose.c `site_check` (enum, ADVANCE refusal now names `empty`); generic.c VERIFY treats AT_N as MISS |
| G3 / Q-R7-3 | `on_miss` class LOOP_EXIT: exactly `break;` (white space allowed; `continue;` stays OTHER). A row may paste it only where its own text opens no loop around it, so the generic row's `on_miss` serves `MF_ANY & ~LOOP_EXIT`: a LOOP_EXIT site no other row serves is REFUSED naming `on_miss`. | memfn.h `mf_hooks.on_miss`; fields.def class `LOOP_EXIT`; gate.c `stmt_shape`; generic.c contract |
| the row | `pf_memchr_back` (form id `pf_memchr`, pffind.c's memchr renderer): one byte at offset -1, end_back 0, empty AT_N, `floor` stated and equal to `lo`'s text (`floor_is_lo`, re-read at use), on_miss JUMP/BRACED/LOOP_EXIT, miss_leaves 1; the store adds `k = -offset` (`+ 1`). `PF_SERVES` lost `pred`/`floor` (each row states them; `PF_AT_ZERO` for the four offset-0 rows) because a designated initializer cannot be overridden under `-Wextra`. | pffind.c, kit.h, compose.c `arms[]` (before generic) |

Fixtures and checks (tests/memfn): two new fixtures through a factored
`render_emit` (`pf-memchr-back`, MLINE's site through the row;
`find-back-reaches-n`, a G2-style reads-below FIND the generic row takes),
pinned (`ARMS_ROW_FLOOR` 74 -> 78); nine gate cases (`GATE_CASE_FLOOR` 39 ->
48): positive `back-at-n-break`, `-break-spaced`, `-return`; decline
`back-excluded-generic`, `back-floor-not-lo-generic`, `back-table-generic`;
refuse `back-excluded-break-refused`, `pf-memchr-break-refused` (`on_miss`),
`adv-at-n-refused` (`empty`); and **check 9**, which compiles both fixtures'
text into one program and runs 10 subjects against a byte loop written from
memfn.h (`"a\n"` from 0 answers 2 = n; `"a\n"` from 2, lo == n, misses
through a zero-length memchr). rows.tsv/row_floors.tsv gained the row
(ROWS_FLOOR 13 -> 14). Every MF_SITE_ABI reader found by grep: memfn.h,
memfn/CLAUDE.md, memfn/include/CLAUDE.md, memfn/src/CLAUDE.md (the rest use
the macro, or are dated history). The kit's ledger/journal entries are the
kit manager's (single writer).

Zero pcrec bytes at Phase A: 33/33 witness compiles SAME (the §4 cells).

## 3. PHASE B: the boundary (what stays pcrec's)

pcrec's ONE describer was generalized, not paralleled: `PcrecFind` moved
from core/internal.h to `src/gen/memfn_sites.h` (its site id is a
`DelegSite`; internal.h keeps a pointer comment) and gained `site` (stated by
every caller: `pf_emit_find` and `pf_vm_emit_first_class` say `DELEG_PF`),
`offset` and `floor`. `find_site` refuses any other site, and any
below-candidate FIND that is not the unbounded memchr at -1 with a floor.

| text / decision | owner | where |
|---|---|---|
| `if (cpre)`, the D63 comment, the K50/K73 guards, the `for` header, `start_max` | pcrec | `emit_attempt` (unchanged) |
| the guard `if (start > X && subject[start - 1] != b) {` and its `}` | pcrec | `emit_attempt` (the printf split; S82's anchor line kept byte for byte) |
| X = `gseed ? "search_from" : "0"` | pcrec | `dfa_needs_gseed`, `emit_attempt` |
| NEXT (`attempt_next_of`, `pred-memchr`), BOUND (`attempt_cand`'s `CAND_BOUND_ONE`), `cand.byte`/`cand.offset` (`cand_from_live_seeds`) | pcrec | unchanged |
| the site's description: row MLINE, term `{b}` at `-cand.offset`, floor `start`, AT_N, `on_miss` `break;` (on_miss_leaves 1), no `miss` | pcrec | `find_site` via `pcrec_emit_find` |
| `const void *q = memchr(subject + start, b, subject_length - start);` / `if (!q) break;` / `start = (size_t)((const unsigned char *)q - subject) + 1;` | **kit** | `memfn/src/pffind.c` `pf_memchr_use` (row `pf_memchr_back`) |

`miss` is left UNSTATED for MLINE on purpose: under Q-R7-1 the range reaches
`len`, so `MF_MISS_N` would name a value a hit can take; no row reads it (the
miss runs `on_miss`, which leaves). DELEG_SITES `MLINE` is
FIND / ASSIGN / SET, DELEG_SCAN, MF_USE_POSITION (C10 5/0: D91's scan list
already named it).

## 4. Shadow-comparator and zero-mover evidence

- **I1 shadow (IMPLEMENT `ecc43b4a`).** `pcrec_memfn_shadow` (R4g's, reborn)
  rendered the MLINE site through a scratch art and compared it byte for
  byte with the span pcrec had just written; a mismatch fails the compile
  `[M4 I1]`. Over the 4,378 unique corpus `pattern` lines x 5 configs
  (default, `-e utf8`, `-fcomments`, and every pattern `(?m)`-prefixed under
  default and `-e utf8`; `--features all`): **21,890 compiles, 693 MLINE
  sites compared, 0 mismatches, 0 internal errors**
  (`build/m4scratch/shadow_sweep.implement.log`, gitignored).
- **REPLACE byte identity, corpus tier** (`a3d65a59` vs `pcrec.base`, the
  binary copied before the first edit, sha256 8f4fbe4f…; `-p rx -o rx.c`
  both; `.c`, `.h`, rc and stderr compared): the same 4,378 patterns x 6
  configs (the five above plus `(?m)` + `-fcomments`): **26,268 pairs, 0
  movers, 990 MLINE sites** (`build/m4scratch/ident_sweep.log`).
- **Witness tier** (`build/m4scratch/zm.sh`): **33/33 SAME** at Phase A, at
  IMPLEMENT and at REPLACE (and again at the final tip): `(?m)^abc`,
  `(?m)^\d+`, `(?m)^`, `(?m)^$`, `^a|(?m)^b`, `(?m)^a|\Gb`, `(?m)^(a|b)$`,
  `(?m)^ERROR`, `(?m)^[a-z]+:\s`, `(?m)^\b\w`; `-e utf8` x6 (incl.
  `(?m)^é+`); `-fcomments` x4 (one with `-e utf8`), `-fno-comments`;
  hybrids (`(?m)^(a|b)(c|d)*$`, `(?m)^(a|b)$` and its utf8 twin carry
  `RX_VM_PREFILTER "hybrid"` AND the MLINE memchr; two backref hybrids
  that do not reach it); `--engine=vm` (not reached, as the notice said);
  `--engine=dfa`, `-fno-start-set`; controls PF/STAY/OFS/PRE/utf8-PF.
- `run_mline_diff.sh` 4/0, `run_gstart_diff.sh` 8/0 (clean tree).

## 5. C12 / C17 (measured by running)

- **C12** (`make test-memfn-forms`): 7 forms in 5 groups, 5 ceiling rows
  (span-decode 1, span-index 4, walk-back 1, walk-open 1); `emit_dfa.c`'s
  memchr row DELETED (1 -> 0): no `memchr(` outside the kit, the ratchet's
  end. `C12_CEIL_ROWS_FLOOR` 6 -> 5. 4/0.
- **C17** (`make test-memfn-manifest`): 13 rows, **delegated 10 / pending 3**
  (N6, VMSTRIDE, N7); 17/0 (one rule-4 check fewer: `emit_attempt` left the
  pending set). MLINE's emitters: `emit_attempt,find_site,pcrec_emit_find`;
  companions `attempt_cand,cand_from_live_seeds`. Rule 2's reach for MLINE
  is satisfied through the shared describer `pcrec_emit_find` (the door's
  traced caller for PF and MLINE alike); MLINE's OWN reach is rows.tsv's
  `pf_memchr_back` row (witness `(?m)^abc`, signature `- subject) + 1;`,
  control `abc[0-9]+xyz`, the trace choosing the row) and, once pinned, its
  census floor.
- Other light targets at the tip: arms 239/0 (78 rows, 48 gate cases),
  rows 122/0 (UNREACHED: 2 PLACEHOLDER floor cells, `pf_memchr_back`'s
  pcrec_floor and g2_floor), deleg 5/0, stamps 14/0, link 8/0, arch 15/0,
  `make strict` clean.

## 6. Sabotage

| row | anchor now | defect | hand-measured (plant applied, rebuilt) |
|---|---|---|---|
| S82 | UNCHANGED (`gseed ? "search_from" : "0",`, the guard's argument line kept its column) | the prefilter bounded at 0 | gpos.rxt **3 failed / 327 passed**, `run_gstart_diff.sh` **1 failed / 7 passed** (the row's recorded figures) |
| S524 | RE-PINNED: `pcrec_memfn_emit(f->cx, f->site, s, &h, c);` | a `memchr(` returns in pcrec_emit_find, now against a ceiling of 0 (no row) | C12 **1 failed / 3 passed** ("1 form(s) spelled, ceiling 0") |
| S511 | RE-AIMED (R1) to VMSTRIDE: `vm_stride_loop`'s `while ((%s_span_cursor + %d <= %s)`, SAB_REACH_POP on the VMSTRIDE row | a pending emitter respelled, its row stale | C17 **1 failed / 16 passed** (rule 4: vm_stride_loop spells no form) |
| S617 (new) | `memfn/src/pffind.c`: `if (k) kit_out(o, " + %d", (int)k);` | the kit's `+ k` store dropped | arms **2 failed / 237 passed** (pin 178 -> 174 bytes; check 9: the row answers c - 1 on 7 of 10 subjects). **Answer-neutral on pcrec's corpus** (multiline.rxt + gpos.rxt 3655/0; d27 multiline/composition + utf8 k73 + litscan handoff 2545/0; mline_diff 4/0): the attempt at the newline's own position enters a dead seeded state and `start++` lands on the line start. Hence a new arm. |
| S618 (new) | `memfn/src/generic.c` `find_loop`: the reads-below forward bound `<=` | the range stops one short of n | arms **2 failed / 237 passed** (pin 387 -> 386; check 9: generic misses n on 6 of 10) |
| S619 (new) | `memfn/src/generic.c` contract: `[FLD_on_miss] = MF_ANY & ~CM(LOOP_EXIT),` | the generic row serves LOOP_EXIT | arms **1 failed / 238 passed** (`back-excluded-break-refused` RENDERs generic). Its sibling `pf-memchr-break-refused` stays refused: pf_memchr is chosen at define (on_miss is use-only) and its own use re-check refuses. |

Each new row's SAB_REACH reaches on the clean tree (S617: the MLINE text
with `+ 1`; S618: the fixture through generic with `<= rx_mf1_n`; S619: the
refusal naming `on_miss`). New mech arm **`memfnarms`**
(`tests/memfn/run_arm_pins.sh` against the sabotaged tree's
`build/libpcrec.a`), documented in run_sabotage_matrix.sh and
tests/mech/CLAUDE.md, because none of S617-S619 moves a pcrec answer or
artifact byte.

`python3 scripts/m6read_check_sab_anchors.py`: **523 sabotages / 541 anchor
sites, all resolve.** `docs/design/start_table/{call_graph.txt,
sabotage_anchors.tsv,.total}` re-derived by their scripts: apart from line
numbers, ONE owner moves (S511 `emit_attempt` -> `vm_stride_loop`, RE-RUN ->
OTHER) and three rows are new (S617-S619, `outside`); S571's UNRESOLVED (rc
2) is pre-existing. `inventory_check.py`: 150/150.

## 7. G2: what a blinded lane must add (memfn/tests/ not edited)

G2 quick at Phase A (`build/m4scratch/g2q_phaseA.log`): **45,210,392 passed,
19,294 failed**, every failure in family `base` (46 failed sites), plus rows
check (b) "rows never chosen: arms/pf_memchr_back". At the tip, with
`--keep`: see §7.1 (filled from `build/m4scratch/g2q_final.log`). The
baseline before any edit was 45,229,686 / 0. Needs, in contract terms only:

1. **The reads-below FIND's range (Q-R7-1).** A FIND whose every term has
   `offset + len <= 0` has candidates c in [lo, n] with `c + d <= n`, d =
   max(0, end_back + E), E the largest `offset + len`; empty iff lo + d > n.
   Every other FIND, and ALL_PRESENT / SKIP / VERIFY / ON_CAND, keep
   [lo, n - end_back). G2's oracle range must make that split; a family at
   offset -1 with the byte at s[n-1] must find n.
2. **MF_EMPTY_AT_N (Q-R7-2).** An AT_N site's driver must establish lo <= n
   and a non-NULL subject (never lo > n, never s NULL); its outcome on an
   empty scan is MISS's. AT_N on ADVANCE must REFUSE. A family that reaches
   the new row: FIND / STMT / ASSIGN, one REQUIRED one-byte SET term at
   offset -1, end_back 0, empty AT_N, `floor` the same text as `lo`,
   `on_miss` a leaving statement (on_miss_leaves 1), no result_decl/note.
   That is what makes check (b) green (`pf_memchr_back` chosen >= 1) and
   gives row_floors.tsv a g2_floor for it.
3. **LOOP_EXIT (Q-R7-3).** `on_miss` exactly `break;` classifies LOOP_EXIT;
   a site whose only candidate rows are generic must REFUSE naming
   `on_miss`. A rendered LOOP_EXIT site must be run inside a loop the
   driver owns (the break must leave THAT loop: the kit's text may not
   enclose it).
4. **FLOOR_ROWS** in run_g2.sh: 13 -> 14 (the registry now has 14 rows).
5. The `MF_SITE_ABI + 1` refusal case keeps working (now 7).

### 7.1 G2 quick at the tip (`--keep`, `build/m4scratch/g2q_final.log`)

**45,210,392 passed, 19,294 failed**, identical to Phase A (the tip's kit is
Phase A's). Every failure is in family `base`: **46 sites, and all 46 are
reads-below FINDs** (every term's `offset + len <= 0`; checked against the
generated site tables): FIND/EXPR/RETURN 26 failure lines, EXPR/BOOL 24,
FUNC/RETURN 24, STMT/ASSIGN 8, FUNC/BOOL 6, STMT/ON_MISS 4. Each is the kit
answering a candidate the old oracle range excludes and Q-R7-1 includes,
e.g. site 17 (one term at -7, end_back 1, n 8): kit 7, oracle "miss 8";
site 33 (E -1, end_back 1, n 6): kit 6 = n. Plus check (b): `pf_memchr_back`
never chosen. No other family, W1 witness or floor moved. Failure lines:
`build/m4scratch/g2q_final_failures.err` (gitignored).

## 8. The slot chain the manager must run

1. Merge `lane/m4` into the kit branch ALONE; `make -j16 && make strict`.
2. **The blinded G2 lane (§7) must land before step 6.**
3. Identity gate, 0 movers on all six streams (MLINE is DFA-route; default
   and `-e utf8` reach it): `python3 scripts/emit_sweep.py --ref <base tip>
   …` (the R4c invocation), judged by `python3 docs/design/memfn/probes/
   lxrun/memfn_r4c_gate.py --zero-dumps <out>`. Witness cells: `(?m)^$` on
   "a\n", find-all `(?m)^`, `(?m)^a|\Gb`, `(?m)^(a|b)$`, `^a|(?m)^b`.
4. N2 census (`docs/design/memfn/probes/rowcon/n2_census.sh`, JOBS=16),
   then `n2_report.py <out> --floors tests/memfn/row_floors.tsv --propose`:
   pin `pf_memchr_back`'s pcrec_floor (PLACEHOLDER now). Expect
   would_decline 0.
5. G2 full (`make test-memfn-g2-full`), after step 2; pin the row's
   g2_floor from it.
6. `make -k -j16 -Otarget test`; verdict `grep -E '\*\*\* \[(Makefile:[0-9]+:
   )?test-'`.
7. Mech, each SOLO (`bash tests/mech/run_sabotage_matrix.sh <id>`), rule (b)
   + the brief's list, 38 rows: **S68 S81 S82 S185 S214 S235 S265 S267 S279
   S285 S443 S444 S445 S447 S450 S454 S455 S464 S478 S511 S512 S513 S514
   S515 S517 S522 S523 S524 S525 S526 S528 S570 S571 S573 S616 S617 S618
   S619** (anchored in a changed definition: emit_attempt, pf_vm_emit_first_
   class, pcrec_emit_find; every row on a memfn/ or tests/memfn/ file; the
   re-pinned/re-aimed S82 S511 S524; the brief's S235 S81; the new S617-S619
   on the new arm `memfnarms`).
8. Not lane work: the kit's responses.md entry and journal line (single
   writer), pcrec's dev_journal line, plan.md's [MEMFN] M4 state.

## 9. Charter checklist

| item | state |
|---|---|
| G1 / Q-R7-1, MF_SITE_ABI 6, generic.c bound only for reads-below FINDs, readers re-pinned by grep, [ENG-TACTICS] noted not designed | DONE (§2) |
| G2 / Q-R7-2 class, memchr row with no empty test | DONE (AT_N; EXCLUDED refused on the row, reason §2) |
| G3 / Q-R7-3 LOOP_EXIT, generic does not serve it | DONE |
| fields.def/gate.c classes, memfn.h comments, fixtures + gate cases (decline/refuse/positive), pins | DONE (48 gate cases, 78 pins, check 9) |
| a G2-style negative-offset case that reaches n, in tests/memfn | DONE (`find-back-reaches-n`, check 9) |
| memfn/tests/ untouched; G2's needs listed | DONE (§7); G2 is red until that lane |
| ONE describer generalized (site id, term offset, floor), no parallel builder | DONE (`PcrecFind`/`find_site`/`pcrec_emit_find`) |
| DELEG_SITES MLINE (FIND/ASSIGN/SET/DELEG_SCAN/MF_USE_POSITION) | DONE |
| emit_attempt describes the three statements, pcrec's hooks; guard/X/start decisions pcrec's | DONE (§3) |
| shadow comparator, default and -e utf8, the five named shapes | DONE (21,890 compiles, 0 mismatches) |
| REPLACE: pcrec's text deleted | DONE |
| manifest 10/3; C12 row deleted, floor by running; new row in rows.tsv/row_floors.tsv (PLACEHOLDER); ROWS_FLOOR, arms pins | DONE; G2 FLOOR_ROWS 13 -> 14 owed (blinded file) |
| S82/S524 re-pinned, S511 re-aimed, S617-S619 with reaching SAB_REACH | DONE (§6) |
| call_graph/sabotage_anchors re-derived; m6read green | DONE |
| zero movers on 25+ witness compiles, same -o basename, default/utf8/both comment tiers/hybrid | DONE (33/33; corpus 26,268/0) |
| CLAUDE.md files | DONE (memfn, memfn/include, memfn/src, src/gen, tests/memfn, tests/mech) |
| no abi event | none needed |
