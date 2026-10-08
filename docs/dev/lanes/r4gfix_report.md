# r4gfix report: the PF rows' contract audit, the ASSIGN miss contract, mf_emit's selection phases

Lane r4gfix (branch lane/r4gfix, cut from lane/memfn-r4g @ f4612149). Kit-only
change; no pcrec file under src/ moved. G2 (memfn/tests/g2/, run_g2.sh) untouched.

## Per finding

### Finding 1 (kit defect): stated ret_pred / npred+preds moved PF to generic
Change (memfn/src/pffind.c, `PF_SERVES`): `preds` and `ret_pred` go from
`CM(NONE)` to `MF_ANY`, as ofsskip declares them (memfn.h reads them on
ALL_PRESENT/DENSE only). The common block now states the convention in its header.

Field disposition for the four PF rows (pf_memchr, pf_memchr_bounded, pf_walk, pf_walk_bounded):

| field | before | after | why |
|---|---|---|---|
| form, op, handoff, reverse, pred, guard_by_caller | stated class | unchanged | pf_shape: the shape itself (guard_by_caller: ofsskip declines it likewise) |
| preds (npred+preds) | NONE | **ANY** | not read on FIND; ofsskip is ANY |
| ret_pred | NONE | **ANY** | not read on FIND; ofsskip is ANY |
| span_hi, fn_ref, result, step, more, peek, count, count_start, on_cand, on_cand_reach, member, fn_name, note_tag, indent, comment_tier | ANY | unchanged | not read |
| denies | NONE or RUN_OVERLAP | unchanged | as ofsskip |
| s, n, lo | IDENT | unchanged | pasted raw |
| floor, result_decl, note | 0 (decline) | unchanged | the text would drop what a stated one asks (R2); real declines |
| empty, end_back, table_ref, table_name, miss, on_miss | per row | unchanged | per-row, as before |
| on_miss_leaves (bounded, walk, walk_bounded) | NO | unchanged, KEPT | tried ANY (it is moot, no on_miss runs) and reverted: it is the DEFINE-time witness of a use-time on_miss, so a leaving ASSIGN goes to generic at mf_define instead of being refused at mf_use. ANY made 228 separate define+use sites refuse in the G2 run. A comment records this |
| on_miss_leaves (pf_memchr) | YES | unchanged | the miss_leaves column |

### Finding 2 (contract amendment): result on a miss under on_miss_leaves = 1
memfn.h only, comments only, no layout change: the `MF_H_ASSIGN` comment and the
`on_miss_leaves` field comment now say `result` is UNSPECIFIED on a miss when
`on_miss_leaves` is 1 (a form may or may not write `miss` first) and `on_miss`
must not read it; at 0 the miss value is written first and may be read.
Rows checked against it: pf_memchr (leaves 1, writes nothing on a miss: inside
the amendment, bytes unchanged); precheck_assign (leaves 1 required, writes the
run call's value, inside); generic (writes first, inside both readings);
pf_memchr_bounded and the walks (leaves 0 only, write `miss`, matching the
at-0 sentence). No other row's documented behaviour contradicts it.

### Finding 3 (kit defect): mf_emit selected with the define hooks only
Change (memfn/src/compose.c): `select_arm` takes the phase mask the gate reads;
`mf_define` is now a thin wrapper over `define_sel(..., MF_PH_DEFINE)` and
`mf_emit` calls `define_sel(..., MF_PH_DEFINE | MF_PH_USE)` (the only one-call
entry; `mf_call` only uses). The gate already took a phase mask, so no field is
special-cased: a row whose use-time fields (result_decl, on_miss, floor, ...) the
one-call hooks fail to serve now declines at selection and the walk reaches a
serving row (generic). Separate mf_define/mf_use calls are unchanged (no
re-selection). The trace still labels the walk `define` (trace_format.md notes it),
so the reach tallies and the MFTRACE format do not move.

## Compile identity (zero pcrec movers)
Baseline: build/pcrec built from f4612149 before the first edit, kept in scratch.
Compared with the edited tree's build/pcrec, `--emit-main`, 15 pattern/flag
pairs (30 compiles, the whole budget): `foo\d+bar`, same with `--engine=vm`,
`[xy]a+b` and its VM twin, `x[0-9]*y$`, `(?:foo|bar)\d`, `Hello, World`, `-i hello\d`,
`[a-f0-9]+z` (a can-begin-match table walk), `abc|abd`, `a.*b.*c`, `foo$`,
`[^a]b`: 13 byte-identical (the one differing line is the `#include "<out>.h"`
name, since the output names differed; verified by normalising it). `(a)\1b` and
`x+y(?=z)` are refused by both binaries (rc 1/1), so they say nothing. The
corpus includes memchr, byte-class walks and the VM hat; I did not confirm that
every one of memchr-bounded, byte-class-bounded and the first-*-bounded DFA hat is
among them (no budget to probe). All 30 compiles ran on the tree that also had
`on_miss_leaves = ANY` on three rows; that was then reverted (it restores the
baseline declines, so it can only move text back toward the baseline). The final
tree was not recompiled with the 30. Why zero movers is also true by construction:
pcrec calls only mf_emit, and a site the stricter selection now declines was one mf_use
would have refused, which would have failed the compile.

## Fixtures (C5) and floors
tests/memfn/arm_fixtures.c: `render_pf` takes a `result_decl`; three fixtures:
`pf-memchr-ret-pred` (stays pf_memchr, digests equal pf-memchr's),
`pf-walk-preds` (npred 1 + preds; stays pf_walk, digests equal pf-walk's),
`pf-emit-result-decl` (mf_emit with result_decl selects generic and renders).
tests/memfn/pins/arms.tsv +6 rows (comment block r4gfix), `ARMS_ROW_FLOOR`
48 to 54 in run_arm_pins.sh. `make test-memfn-arms`: 54 rows over 27 fixtures, 20
gate cases, 138 passed / 0 failed. `make test-memfn-stamps` 14/0. `make -j4`, `make strict`
clean.

## G2 quick (2 runs used, both on the tree with `on_miss_leaves = ANY`)
Run 1 and run 2 (identical): answer checks 43,426,453 passed / 0 failed over 11,048
sites, K1 377,000/0; poison differential 10,180 sites 0 moved (ret_pred and
npred+preds: 8,105 sites moved=0, the 871 are gone). Overall `failed: 314`, all
one cause, NOT a wrong answer:
the generator stage trial-renders each site with `mf_emit` (g2_gen.c `render_text`,
:892), then renders the real site by its `via` path. For the PF edge sites (stated
result_decl or on_miss) the trial now renders (generic, finding 3's fix), where before it
refused and the site was filed as a lawful named refusal. On the separate
`mf_define` + `mf_use` paths (`via` 1 and 2) the PF row is still chosen at define
and mf_use still refuses, naming the field (as the brief says it must). G2 reads that as
"kit refused a contract site": 228 on_miss (pf_memchr_bounded) + 74 result_decl
(pf_memchr) render fails, 6 api fails, one libc-record batch, and the edge run floors
(sites that never ran). The brief's expectation of 0 failed does NOT hold.
NEEDS: the blinded G2 author must make the trial use the same entry as the real path, or
accept a named refusal on the via-1/2 paths for pf-edge sites. I did not touch
g2/. Run 3 is owed after that. Not re-run with the final on_miss_leaves = NO
(the 2-run budget was spent); with NO restored the 228 on_miss cases keep refusing
on via 1/2 the same way, so the picture is unchanged.

## Anchors
`python3 scripts/m6read_check_sab_anchors.py`: 498 sabotages, 516 anchor sites, all
resolve (run on the final tree). No sabotage anchor lives in the edited
kit lines (mech sabotages touching the kit: S520/S526 anchor memfn.h elsewhere).
No row re-pinned. The arm-pin floor is raised (above).

## Charter checklist
- [x] Finding 1 fixed in the general convention, dispositions listed
- [x] Finding 2 comment-only amendment, rows cross-checked, bytes unchanged
- [x] Finding 3 via the gate's phases, no result_decl special case; define/use unchanged
- [x] Zero pcrec movers shown (13 identical of 15; 2 refused by both; caveats above)
- [x] C5 fixtures + arms.tsv + floor raised
- [ ] G2 quick: 0 answer failures, but 314 generator-stage fails owed to a G2 harness change (above)
- [x] anchors check; no scaffolding emitted by pcrec changed (no abi event)
