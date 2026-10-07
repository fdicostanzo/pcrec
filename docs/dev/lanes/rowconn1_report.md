# Lane rowconn1 — [MEMFN-ROWCON] N1: the row-contract gate in WARN mode

Branch `lane/rowconn1`, cut from the kit branch `lane/memfn-rowcon` at
f7647b9e. Design of record: `docs/design/memfn/row_contracts.md` rev 4.1
(§2, §3, §5's N1 row). Evidence read: `probes/rowcon/audit_kit_rows.md`,
`probes/rowcon/hook_census.md`.

## 1. What was built

All kit-internal (`memfn/src/`, `memfn/docs/`). No pcrec source change, no
`memfn.h` change, no `--list-axes` change, no table engine, no snapshot.

- **`memfn/src/fields.def`** (new): two X-macros.
  - `MF_CLASS(name, doc)`: 37 value classes, kit-wide; `OTHER` is in every
    field's set.
  - `MF_FIELD(name, phase, absent, classify, classes, doc)`: 39 fields, every
    `mf_site`/`mf_hooks` field some row reads, plus the run compare's two
    term fields. `phase` is `MF_PH_DEFINE` / `MF_PH_USE` (either or both),
    or `MF_PH_RUN` (the run compare's walk). `absent` is `HOOK` (NULL is
    UNSTATED), `VALUE` (intrinsic, never absent) or `OBLIG` (the written
    per-kind obligation exemption, in the doc column as `OBLIG: …`).
  - The text-shape classes: `s`/`n`/`lo` ∈ {IDENT, OTHER} (lexical bare
    identifier); `on_miss` ∈ {JUMP, BRACED, OTHER}.
  - The obligation exemptions: `comment_tier`, `reverse`,
    `guard_by_caller`, `on_miss_leaves`, `end_back`, `fn_ref`, `table_ref`
    (r3 M7's list), and two NEW numeric hooks, `count_start` and
    `on_cand_reach` (§5 item 4).
- **`memfn/src/gate.c`** (new): the classify functions, `kit_is_ident` (the
  one lexical identifier check; `compose.c`'s private copy is gone),
  `gate_check` (rules 1-3 of §2), and the MF_TRACE records and reach
  counters.
- **`memfn/src/kit.h`**: `gate_use`, `gate_contract`, `gate_in`,
  `gate_verdict`, `CL_*`/`FLD_*` enums from fields.def, `CM()`/`FM()`/
  `MF_ANY`; `arm` gains a last column `ct` (its contract); `site_rec` gains
  `warn_define`/`warn_use`; `mf_art` gains `run_warns` and `trace_id`; the
  trace calls (no-op `static inline`s unless `MF_TRACE`).
- **The gate at DEFINE**: `compose.c` `select_arm` runs `gate_check` on each
  arm at `MF_PH_DEFINE` before its predicate, records the chosen arm's
  verdict on `site_rec.warn_define`.
- **The gate at USE**: `mf_use` (so every `mf_call` too) re-checks the
  chosen arm at `MF_PH_USE` against the use hooks, OR-ing into
  `site_rec.warn_use`.
- **The gate in the run walk**: `runcmp.c` `rc_row_of` runs it on each
  undenied row at `MF_PH_RUN` before its predicate; a chosen row it would
  decline bumps `art->run_warns`.
- **WARN mode**: in all three walks the predicate alone still chooses; the
  verdict is only recorded (and traced). Nothing is refused.
- **`uses`/`serves` on all 8 rows** (4 arms, 4 run-compare rows), declared
  at the end of each row's own file, one comment per declaration citing the
  line that justifies it (§2 below).
- **MF_TRACE** (compile-time, off by default): per selection an `MFTRACE`
  SEL / ROW… / END block on stderr, every row's verdict (`DENIED:<deny>`,
  `PRED_FALSE`, `CHOSEN`, `RECHECK` at use) with its gate verdict (`PASS` or
  `DECLINED` with every failing field as `name:R1:UNSTATED` /
  `name:R2:<class>`), and `would_decline` on END, at both phases (and the
  run walk). At exit, `MFTRACE REACH` lines: chosen per row (every row, 0
  included) and per (row, used field, class). Format:
  `memfn/docs/trace_format.md` (new).
- Docs: `memfn/src/CLAUDE.md`, `memfn/docs/CLAUDE.md`, `memfn/PROVENANCE.md`
  (rows for fields.def and gate.c; both carry SPDX + Provenance headers),
  `compose.c`'s header, `memfn/docs/journal.md`.

## 2. uses / serves per row (with citations)

Line numbers are the files' own at the tip; each is also written beside its
declaration in the source. "MF_ANY" = declared irrelevant to the row's text.
Fields not listed for a row serve nothing. The arms' contracts are read at
define/use only; the run rows' at the run walk only (they list `run` and
`run_len` alone).

**What `uses` means (a choice made here, §5 item 1):** the fields the row's
text reads with NO reading of its own for the unstated case (it refuses or
presumes). A field read with a CONTRACT reading for NULL (memfn.h: `floor`
"0", `result_decl`, `count`, ASSIGN's optional `on_miss`, `member`) is not
a use. A field read only for some shapes, and held by the row's predicate or
a refusal, is not declared (named per row below): N3's row split is where
that resolves.

### A1 ofsskip (ofsskip.c)

| uses (kind, phase) | fields | cite |
|---|---|---|
| FUNC/RETURN, define | fn_name, miss | :403-404 refuses without fn_name; :384 reads an unstated miss as `n` |
| FUNC/RETURN, use | s, n, lo, miss | :280-281 refuses without s/n/lo; :420 reads an unstated miss as `n` |
| not declared (shape) | table_name | multi-byte SET only: :111 at define, :149 at the call |

| serves | classes | cite |
|---|---|---|
| form / op / handoff | FUNC / FIND / RETURN | :389-390 |
| reverse | NO | :391; forward stream :258-260 |
| empty | E_MISS | :390; empty range returns n, :252/:273 |
| end_back | ZERO | :391 |
| pred | NONNEG | :105 |
| guard_by_caller | NO | :391; own bounds :267 |
| denies | NONE, RUN_OVERLAP | :184 via the run walk (fallback per domain) |
| fn_ref | REF | :392, :405 |
| table_ref | NONE, REF | :111; singleton :186-188, run :183 read none |
| s, n, lo | IDENT | :284 raw in the call's argument list (a top-level comma splits it) |
| floor | (nothing) | :99 declines any stated floor; :282-283 refuses one at the call |
| miss | MISS_N | :384; the function's miss is n, :262 |
| member | MF_ANY | not read; set bits are the truth (:187-188, :190-193) |
| table_name, fn_name, note, comment_tier | MF_ANY | :147, :405, :410, :335 as given |
| preds, ret_pred, on_miss_leaves, span_hi, result, result_decl, on_miss, step, more, peek, count, count_start, on_cand, on_cand_reach, note_tag, indent | MF_ANY | not read |

### A2 precheck (precheck.c)

| uses (kind, phase) | fields | cite |
|---|---|---|
| STMT/ON_MISS+ASSIGN, use | s, n, lo, indent, on_miss | :224-225 refuses without |
| STMT/ASSIGN, use | result, miss | :204-205 refuses without result; :209 tests `result >= n`, reading an unstated miss as `n` (S1) |
| not declared (shape) | fn_name | FUNC parts only, :144-146; run_part needs it, :66 |

| serves | classes | cite |
|---|---|---|
| form / op / handoff | STMT / ALL_PRESENT / ON_MISS, ASSIGN | :72-73 |
| reverse / empty / end_back | NO / E_MISS / ZERO | :74 |
| preds | NONNEG | :54, :65 (every part at offset 0) |
| ret_pred | NONE, PRED | :88, :203 |
| on_miss_leaves | YES | the arm's miss_leaves column; compose.c:140 |
| denies | NONE, RUN_OVERLAP | :154 via the run walk |
| s / n / lo | IDENT | :167-168, :187 raw in `<=`, `+`, `-` (S2-S4) |
| floor | (nothing) | :67 → ofsskip.c:99; ofsskip.c:282-283 |
| miss | MISS_N | :209 (the run call's miss is its n) |
| on_miss | JUMP, BRACED | :169, :188, :209, :214: the `if`'s one unbraced statement (S5) |
| result, result_decl | MF_ANY | :206, :209 an lvalue / a prefix |
| fn_name, note, note_tag, indent, comment_tier | MF_ANY | :147, :152/:229, :99, :165/:180, :98 |
| pred, guard_by_caller, span_hi, fn_ref, table_ref, member, table_name, step, more, peek, count, count_start, on_cand, on_cand_reach | MF_ANY | not read |

### A3 runcmp (runcmp.c, the arm)

| uses | fields | cite |
|---|---|---|
| EXPR/BOOL, use | s, lo | :367-368 refuses without; :371 reads |

| serves | classes | cite |
|---|---|---|
| form / op / handoff / guard_by_caller | EXPR / VERIFY / BOOL / YES | :351-352 |
| pred | NONNEG | :373-374 reads at lo + offset; compose.c:245 |
| denies | NONE, RUN_OVERLAP | :374 via the walk :176 |
| s, lo | IDENT | :371 raw `%s + %s` then `+ off` (S6, S7) |
| floor | MF_ANY | reads at lo + offset >= lo >= floor (compose.c:245, Q-G2-6) |
| every other field | MF_ANY | not read (reverse, empty, end_back: the guard decides) |

### A4 generic (generic.c)

Serves MF_ANY on every field (§2: it parenthesizes every pasted hook,
:293/:304-308/:360/:456/:612, and braces statements, :348); each field's
reading is cited in the source.

| uses (kind, phase) | fields | cite |
|---|---|---|
| EXPR+STMT except ADVANCE, use | s, n, lo | :643 need_subject |
| EXPR/RETURN, use | miss | :646 |
| STMT/ON_MISS, use | on_miss | :363 |
| STMT/ASSIGN, use | result, miss | :372 |
| STMT/ON_CAND, use | on_cand, result, miss | :444-446 |
| STMT/ADVANCE, use | step, more, peek | :525-526 |
| FUNC, define | fn_name | :566-567 |
| FUNC/RETURN, use | miss | :574, :609-610 |
| not declared (shape) | a FUNC call's s, n, lo, floor | :608-610 refuses exactly the params its definition took |
| not a use (contract default / layout) | floor, result_decl, on_miss (ASSIGN), count, member; indent | :79, :384, :386, :530, :131; :356 |

### B1-B4, the run compare's rows (runcmp.c)

All four use `run` and `run_len` (rc_of, :123-127).

| row | run | run_len | cite |
|---|---|---|---|
| words | EXACT, MASKED | MANY | :226 exact words, :229-235 masked; rc_width(1) = 2 puts the last word at -1 (:223-225) |
| overlap | EXACT, MASKED | MANY | the same writer (RC_F_WORDS, :98 → :282) |
| bytes | EXACT, MASKED | ONE, MANY | :256-257 per position (:252); UNSAT would be a tautological compare |
| memcmp | EXACT | ONE, MANY | :288-293 never reads the mask |

UNSAT is served by no row: `run_cmp_sat` (:262-268) keeps it off every walk.

## 3. Validation (Mac)

OWED — filled from `build/scratch/validate.log` when the chain completes.

## 4. The trace demo (16 pcrec compiles + the C5 fixture driver)

Trace build: `make BUILD_DIR=build/scratch/trace CFLAGS="-O2 -g
-DMF_TRACE"`. Its 16 artifacts are byte-identical to the default build's
(`cmp`, 16/16).

| # | argv (`-p rx`) | selections | would-decline |
|---|---|---|---|
| 1 | `user:pass[0-9]` | ofsskip ×2 (define+use), memcmp ×2 | 2 |
| 2 | `(?:foo\|bar)+baz` | precheck ×2, overlap ×2 | 0 |
| 3 | `--engine=vm abcd[0-9]` | runcmp ×2, precheck ×2, memcmp ×3 | 0 |
| 4 | `x{2,5}(?i:cat)` | precheck ×2 (ASSIGN), words ×2 | 1 |
| 5 | `--features all (x?)([a-z]+)+Z.@\1` | precheck ×2 (gate + set rest) | 0 |
| 6 | `--engine=vm -i abcd[0-9]` | precheck ×2, words ×2 | 0 |
| 7 | `--engine=vm abcdefg[0-9]` | runcmp ×2, precheck ×2, overlap ×3 | 0 |
| 8 | `-fno-run-overlap --engine=vm -i abcd[0-9]` | precheck ×2, bytes ×2 (words/overlap DENIED) | 0 |
| 9 | `[a-c]x[0-9]q` | ofsskip ×2, precheck ×2 | 2 |
| 10 | `--engine=vm -i hello[0-9]` | precheck ×2, words ×2 | 0 |
| 11 | `(?:a\|bb)?catdog` | precheck ×2 (ASSIGN), overlap ×2 | 1 |
| 12 | `(?i)userpass[0-9]` | precheck ×2 (ASSIGN), words ×2 | 1 |
| 13 | `--engine=vm (ab\|cd)xyz[0-9]` | runcmp ×2, precheck ×2, overlap ×3 | 0 |
| 14 | `foo[0-9]+bar` | precheck ×2, overlap ×2 | 0 |
| 15 | `userpass(a\|b)+` | ofsskip ×2, runcmp ×2, memcmp ×3 | 2 |
| 16 | `--engine=vm x(a\|b)+hello` | runcmp ×2, precheck ×2, overlap ×3 | 0 |

(×2 for an arm = its define selection and its use re-check.)

An ofsskip site (#1):

    MFTRACE SEL table=arms art=1 site=1 phase=define form=FUNC op=FIND handoff=RETURN
    MFTRACE ROW table=arms art=1 site=1 phase=define row=ofsskip verdict=CHOSEN gate=DECLINED fields=miss:R1:UNSTATED
    MFTRACE END table=arms art=1 site=1 phase=define chosen=ofsskip would_decline=1 fields=miss:R1:UNSTATED
    MFTRACE SEL table=runcmp art=1 site=- phase=run run=EXACT len=8
    MFTRACE ROW table=runcmp art=1 site=- phase=run row=words verdict=PRED_FALSE gate=PASS fields=-
    MFTRACE ROW table=runcmp art=1 site=- phase=run row=overlap verdict=PRED_FALSE gate=PASS fields=-
    MFTRACE ROW table=runcmp art=1 site=- phase=run row=bytes verdict=PRED_FALSE gate=PASS fields=-
    MFTRACE ROW table=runcmp art=1 site=- phase=run row=memcmp verdict=CHOSEN gate=PASS fields=-
    MFTRACE END table=runcmp art=1 site=- phase=run chosen=memcmp would_decline=0 fields=-
    …
    MFTRACE SEL table=arms art=1 site=1 phase=use form=FUNC op=FIND handoff=RETURN
    MFTRACE ROW table=arms art=1 site=1 phase=use row=ofsskip verdict=RECHECK gate=DECLINED fields=miss:R1:UNSTATED
    MFTRACE END table=arms art=1 site=1 phase=use chosen=ofsskip would_decline=1 fields=miss:R1:UNSTATED

A precheck ASSIGN site (#4) and a runcmp site (#3):

    MFTRACE ROW table=arms art=1 site=1 phase=define row=ofsskip verdict=PRED_FALSE gate=DECLINED fields=form:R2:STMT,op:R2:ALL_PRESENT,handoff:R2:ASSIGN,pred:R2:OTHER,fn_ref:R2:NONE
    MFTRACE ROW table=arms art=1 site=1 phase=define row=precheck verdict=CHOSEN gate=PASS fields=-
    MFTRACE ROW table=runcmp art=1 site=- phase=run row=words verdict=CHOSEN gate=PASS fields=-
    MFTRACE ROW table=arms art=1 site=1 phase=use row=precheck verdict=RECHECK gate=DECLINED fields=miss:R1:UNSTATED

    MFTRACE ROW table=arms art=1 site=1 phase=define row=ofsskip verdict=PRED_FALSE gate=DECLINED fields=form:R2:EXPR,op:R2:VERIFY,handoff:R2:BOOL,empty:R2:E_EXCLUDED,guard_by_caller:R2:YES,fn_ref:R2:NONE
    MFTRACE ROW table=arms art=1 site=1 phase=define row=precheck verdict=PRED_FALSE gate=DECLINED fields=form:R2:EXPR,op:R2:VERIFY,handoff:R2:BOOL,empty:R2:E_EXCLUDED,preds:R2:NONE,on_miss_leaves:R2:NO
    MFTRACE ROW table=arms art=1 site=1 phase=define row=runcmp verdict=CHOSEN gate=PASS fields=-
    MFTRACE ROW table=arms art=1 site=1 phase=use row=runcmp verdict=RECHECK gate=PASS fields=-

The deny path (#8):

    MFTRACE ROW table=runcmp art=1 site=- phase=run row=words verdict=DENIED:MF_D_RUN_OVERLAP gate=-
    MFTRACE ROW table=runcmp art=1 site=- phase=run row=overlap verdict=DENIED:MF_D_RUN_OVERLAP gate=-
    MFTRACE ROW table=runcmp art=1 site=- phase=run row=bytes verdict=CHOSEN gate=PASS fields=-

A generic site: no pcrec site reaches the generic row, so the demo takes
it from the C5 fixture driver (`tests/memfn/arm_fixtures.c`, linked against
the trace build's `libpcrec.a`). Its two K96 decline fixtures
(`ofs-decline-miss`, `ofs-decline-floor`) show the GENERAL gate reaching
the same decline as ofsskip's ad hoc K96 checks, each on the right field:

    MFTRACE ROW table=arms art=6 site=1 phase=define row=ofsskip verdict=PRED_FALSE gate=DECLINED fields=miss:R2:OTHER
    MFTRACE ROW table=arms art=6 site=1 phase=define row=generic verdict=CHOSEN gate=PASS fields=-
    MFTRACE ROW table=arms art=7 site=1 phase=define row=ofsskip verdict=PRED_FALSE gate=DECLINED fields=floor:R2:OTHER
    MFTRACE ROW table=arms art=7 site=1 phase=define row=generic verdict=CHOSEN gate=PASS fields=-

### The would-decline findings (N2's preview; none fixed here)

Every would-decline in the demo is one of THREE (row, phase, field) cells,
all rule 1, all the unstated `miss`:

| # | row | phase | field | where (pcrec) | records in the demo |
|---|---|---|---|---|---|
| W1 | ofsskip | define | miss:R1:UNSTATED | `ofs_site_define` (src/gen/emit_dfa.c:6208) states no `miss` | 3 |
| W2 | ofsskip | use | miss:R1:UNSTATED | `pf_ofs_call` (emit_dfa.c:6229) states no `miss` | 3 |
| W3 | precheck | use (ASSIGN sites only) | miss:R1:UNSTATED | `pcrec_emit_req_byte_check` (emit_dfa.c:1552) states no `miss` | 3 |

These are the design's own prediction (§5 R-6: "`MF_MISS_N` at the
ofsskip site, define and call, plus any enum N2 names"); W3 is the precheck
half (S1, §5 N3 "precheck serves a stated `miss`"). No other field, row or
phase declined on a pcrec site in the demo. The fixture driver shows the
same three cells (ofsskip 4 define + 8 use, precheck 2 use) and no other.

## 5. Choices made, and deviations from the design text (for review)

1. **`uses` excludes contract-defaulted reads** (`floor`, `result_decl`,
   `count`, `member`, ASSIGN's `on_miss`) and generic's `indent` (layout
   only; generic presumes `""`, a presumption by R1's letter that changes
   whitespace, not an answer). If the kit session reads R1 as covering
   `indent`, generic's STMT entries gain it.
2. **Shape-dependent reads are not declared** (ofsskip `table_name`,
   precheck `fn_name`, generic's FUNC call operands): declaring them would
   decline sites that never read them. They are N3's split input.
3. **precheck serves `on_miss` BRACED as well as JUMP.** The design's
   sentence says a raw-pasting row serves only JUMP; but precheck pastes
   `on_miss` as an `if`'s single statement, where one block is exactly as
   safe as one jump. If BRACED were never served by a non-generic row the
   class would not need to exist.
4. **`on_cand` has the class set {OTHER} only.** It is a WRITER op, not text:
   its text exists only once called, inside generic's capture sink. The
   design lists it with `on_miss`'s classes; only generic uses it and
   generic serves everything, so no selection depends on it.
5. **`count_start` and `on_cand_reach` are OBLIG fields** (numeric hooks
   whose 0 is a value), beyond r3 M7's list; marked NEW in fields.def.
6. **A third phase, `run`,** for the run compare's term fields (`run`,
   `run_len`): the rows of table B select over a RUN term, not a site.
7. **`result` has no IDENT class:** it is an lvalue, and no lvalue binds
   looser than the `>=`/`=` it is pasted beside.
8. **ofsskip serves `s`/`n`/`lo` IDENT only**, stricter than the audit's
   "raw in arg list (safe)": a top-level comma expression would split the
   argument list.
9. **`floor`: NULL is unstated; ofsskip and precheck serve no class**, so a
   `"0"` text declines them, exactly today's code (the audit's
   disagreement 3, kept, not fixed).
10. **The gate runs in every build**, not only under MF_TRACE: its verdicts
    are recorded on `site_rec.warn_define`/`warn_use` and
    `mf_art.run_warns` (kit-internal). It reads hook strings and never
    calls a hook.
11. **memfn.h's "one sentence per class"** (§2) is not added: in WARN mode
    the contract would state what the kit does not yet do. It belongs with
    N3's enforcement.
12. **Fields no row reads are not in fields.def**: `cursor`, `use`,
    `consumer`, `policy`, `opts`, `span_lo`, the ppm hints, `npred` (read
    through `preds`).
13. **MF_TRACE's counters are process-wide file-scope state** (trace builds
    only): an exception to the kit's re-entrancy, documented in gate.c and
    trace_format.md.

## 6. Charter checklist

- [x] fields.def: one row per used field, phase, classify, closed class set
      with OTHER, doc.
- [x] Text-shape classes (IDENT lexical; JUMP/BRACED/OTHER).
- [x] Written obligation exemptions (the seven, plus two NEW).
- [x] `uses`/`serves` on all 4 arms and all 4 rc rows, derived from the
      code, one citation per declaration; MF_ANY explicit; absent = nothing;
      generic serves every class.
- [x] Gate at DEFINE (select_arm, rc walk, before the predicate) and at USE
      (re-check of the chosen arm), rules 1-3, WARN mode.
- [x] Selection unchanged (the predicate alone chooses; zero-mover gate §3).
- [x] MF_TRACE, off by default: SEL/ROW/END with DENIED/DECLINED fields/
      PRED_FALSE/CHOSEN and would_decline at both phases; REACH per row and
      per (row, used field, class) at exit; trace_format.md.
- [x] No table engine, snapshot, --list-axes change, pcrec source change or
      memfn.h change.
- [x] C15/C16: MF_NS names, statics, SPDX + Provenance headers, PROVENANCE
      rows; src/CLAUDE.md and docs/CLAUDE.md updated.
- [ ] Validation: §3 (OWED until the chain completes).
