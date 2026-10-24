# crit-memfn-s3-c1 house-rules review (SUBJECT ae83da9d, BASE c3ea619c)

Read-only. Denylist: nothing opened. Evidence of frames: `gcc -O2 -fstack-usage`
on window.c/finder.c/compose.c/ofsskip.c compiled to the scratchpad only (no make).
File:line below are in the review tree's `memfn/src/`.

## Round-1 recheck

| round-1 finding | status | evidence |
|---|---|---|
| E-find duplicates the floor's frame / prologue / position loop | FIXED (one residue) | `wf_frame` window.c:2228 serves both (floor_use 2318, find_use 2586); `wf_open/wf_cand/wf_close` 2165-2187 and `wf_test_to` 2126 are shared. Residue: the candidate `for` loop itself is still written twice (floor 2197-2201 and 2303-2307, E-find 2514-2547), and `wf_rc_init` 2000 eagerly allocates 14 names for every caller |
| Table D as an if-chain | PARTLY | Predicates and path/next data are a `kit_table` (`wf_drows` 1599, `wf_dtable` 1617). The ACTIONS are still if-chains on `w->hors` / `drow`: 1729, 1735, 1762, 1769, 2479, 2508, 2516, 2520, 2542, 2562, 2566, 2624. A third resume row means ~10 edits and no selector edit would suffice (fails "expandable") |
| `e_find_holds` writing through a const predicate | FIXED for E-find, MOVED to D | `e_find_holds` 1394 is now a pure read of `fx->holds`. The write moved: `d_hors_holds` 1572-1577 casts `const void *` to `wf_dx *` and writes `wlo/whi` (F1 below) |
| the 320-byte literal | PARTLY | Named `WF_WHY_MAX` 1783 with a comment, but the comment says "gate_describe's buffer bound", which is not a shared constant: compose.c:1051/1185 use 200, ofsskip.c:403 and runcmp.c:222 use their own. The 320 is not derived and the claimed link does not exist (F7) |
| "wf-find" spelled three times | PARTLY | Code now has `WF_FIND_ID` 1347, used for Table E row 1443, arm name 2682 and deny 2689, refusals. Still literal outside it: options.def:96 (the registry, fine), and `"wf-hors"` is a bare literal at 1606 (single site, no macro). Comments in finder.c:303, memfn.h:408, emit_dfa.c:4709/9850, known.c:368 spell it (docs, acceptable) |
| `find_groups` on the query path | PARTLY | Still called on the query (`wf_find_prepare` 1778 via `wf_prepare` 1833, `build = !quiet`). It no longer allocates on a query, but it is one function with two modes selected by a flag (1473). Header says the query "reads the class, which reads the count alone", which is true (`w->libc` from `nrun`) |

## Findings, ranked by cost to the next editor

### F1 (maintenance, CONFIRMED) Side effects in predicates, now three
- `d_hors_holds` window.c:1572: `wf_dx *dx = (wf_dx *)x;` casts away const and fills `dx->wlo/whi` as the walk's output; `wf_find_decide` 1727-1731 then reads them back. The walk's only way to return D-hors's window is a write inside a predicate.
- `e_legacy_holds` 1377-1384: `translate(.., e->L)` rewrites the shared legacy storage as a side effect of "holds".
- `b_fn_holds` 1640-1650: same, `translate(.., b->fn)`.
- Cost: the table is documented "observable, every verdict printable" (architecture.md); a quiet or traced walk, or a second walk over the same row (wf_find_decide runs twice, quiet then not, 1804/1829), re-executes writes. Reordering Table D rows changes which values survive.
- Fix: predicates pure over a precomputed fact (compute `hors_window` once in `wf_find_decide`, put it in `wf_dx` as const input); effort small (D), moderate for translate (E/B). Blast radius: window.c only.

### F2 (maintenance, CONFIRMED) Table D / Table B are declared tables whose actions are if-chains
- See recheck row 2. The same holds for Table B: `wf_brows[].libc` (1665-1676) restates what `wf_b_memchr` 2406-2421 and `wf_b_pair` 2433-2451 do (`includes |= STRING_H`, `mf_art_note_libc("memchr")`). Three statements of "this renderer calls memchr": the flag, the renderer body, and `wf_find_prepare` 1776-1777. Add a renderer and forget the flag and `libc_free` in the class is wrong silently.
- Shared abstraction that should exist: a row carries its renderer function and its text-bounds (`libc`, `includes`), and `wf_find_prepare` reads them from the row; likewise a Table D row carries `prepare` (window, shift table) and `render` (probe/resume text) callbacks, so `w->hors` is never tested outside the row. Effort: medium. Blast: window.c (about 10 sites), compose.c `wf_plan_brow` coupling.

### F3 (maintenance, CONFIRMED) `wplan` is a parallel mechanism beside the arm table in compose.c
- Branches on `wplan`/`r->wplan` at compose.c:965, 1024, 1036, 1060, 1075, 1100, 1113, 1178, 1259, 1261. S3 adds one (`out->includes = r->wplan ? r->cls.includes : r->arm->includes`, 1261) while the E-find `arm` record still carries its own `includes`/`libc` fields (window.c:2689-2693, "its widest text") that the wplan path then ignores. Two sources for the same fact.
- Fix: make `arm.includes`/`libc_free` read through one accessor taking the site record (plan or arm), or drop the fields from the family arms (they are inert for a plan site). Effort small-medium; blast: compose.c, window.c arm literals.

### F4 (doc, CONFIRMED) Comments that disagree with the code
- `wf_b_search` header window.c:2397-2398: "(`hit`: the offset it found, else N; a declaration of Q otherwise)". No `hit` parameter; the function takes `(rc, b, p, d, byte)` and only declares Q.
- Stale "preview art" language after `mf_preview` retired: kit.h:254 ("rendered on a preview art"), kit.h:767 ("the preview's own route"), kit.h:795 ("On a preview art: *out is a copy..." but `wf_parts_prepare` compose.c:939 runs on every art), window.c:1857 ("On a preview art the part's plan ... replaces the part's terms", same), memfn.h:502 (historical, but states "through commit 5" in a live comment; acceptable). These mislead a reader into thinking the parts path is conditional.
- `wf_find_expr` window.c:2503 `(void)want_value; /* E-find's frame is ASSIGN alone */` yet `wf_frame`'s ON_MISS arm calls `expr(rc, o, 0)` (2254): E-find's contract (2669-2671) serves CM(ASSIGN) only, so the ON_MISS arm is unreachable for it, and the code relies on that silently; `wf_close(rc,&b,1)` hardcodes it.
- Effort: trivial. Blast: none.

### F5 (maintenance, CONFIRMED) Altitude: `wf_find_expr` window.c:2503-2552 (50 lines, two levels)
- One function interleaves the loop skeleton, D-hors's probe/shift text, B-pair's pending-hit state, B-fn's escape hatch and D-one's resume, with `w->hors` tested three times and `bren` twice. It has no header (HDR-1, coding.md 4.2).
- Fix: split into `wf_find_head` (state declarations), `wf_find_hors_body` and `wf_find_b_body`, the pieces F2 would make row callbacks. Effort medium.
- Also no HDR-1 header: `wf_find_expr` 2503, `wf_find_use` 2580, `wf_floor_applies` 2589, `wf_plan_reads_table` 2617, `wf_plan_brow` 2622 (its `!w->hors` clause is an undocumented reason), `wf_plan_row` 2627, `d_one_holds` 1580, `wf_need` 2215, `wf_floor_define/use` 2275/2310, `wf_part_site` 1874, `wf_has_parts` 1867, `wf_parts_check/prepare`.

### F6 (maintenance, CONFIRMED) Duplicate set-up in fd_route / fd_find (finder.c)
- `fd_route` (~866-905) and `fd_find` (~920-946) both build an `fd_x`, set `ff.kind/layer`, call `fd_decide`, check `terminal >= FD_NROWS`/`npiece != 1`. S3 extracted `set_facts` and `seek_facts` (good) but not the shared tail: a `fd_decide_one(q, tc) -> (row, pick)` would hold both. `fd_route`'s `switch (d.pick[0])` now lists `FF_PAIR` in its decline arm with no comment that PAIR can only reach it through fd_find (the row is documented at 296-301 only).
- Also `fd_row.step` (finder.c:153) is now read only by the listing (1154) after `fd_previews` retired: a column whose only job was previews. Effort small; blast: finder.c, listing tests.

### F7 (maintenance, CONFIRMED) Unlabelled/underived constant and a message carrying history
- `WF_WHY_MAX = 320` (1783): see recheck. The longest fixed text is about 175 chars, `gate_describe` truncates to its `n`, so nothing overflows; the problem is the claimed derivation. Fix: either `gate_describe`'s documented bound is exported from kit.h and used by compose.c too, or the comment says "unmeasured default, ample". Effort trivial.
- The REPORT refusal text (1818-1820) ends "(the kit manager's R2 ruling)": history in a user-visible diagnostic (coding.md 4.2, style.md Naming: no row ids in caller-facing text). Same in compose.c:1046-1049 ("window.c's E-find row renders it, D172 S3").

### F8 (maintenance, CONFIRMED) Dead/inert residue of retired mechanisms
- `PcrecHarnessOptions.kit_proof` and `pcrec_kit_proof_routed` (src/core/internal.h:3849-3855, comment says "INERT since D172 S3 ... read only by the KITPROOF trace record"). A lever that routes nothing; the comment records the filing (s3_report), so this is declared debt, not a silent leftover. Cost: a reader assumes `--harness=kit-proof` does something. SUSPECTED that nothing else reads it (grep of `src/` for `kit_proof` not run beyond internal.h/known.c).
- compose.c `select_arm` (272-283): `*row = NULL;` is set, then `fd_route` overwrites it via `rid`; the added early `if (s->site_kind == MF_SK_REPORT) return NULL;` runs before `fd_route`, so `*row` stays NULL and `define_sel` re-tests `MF_SK_REPORT` (1045): the REPORT refusal exists in two places (select_arm and define_sel) with two messages (S3 added 1045). Silent-refusal check: both paths are loud, fine; duplication is the cost.

### F9 (speed/memory, SUSPECTED) `wf_prepare` allocates five arena objects per call including the ~5 KB legacy translation, on the query path
- window.c:1790-1798 runs for every `mf_ask` (quiet) and again at define; the arena only frees at art end. Not measured here; flag for the stack/arena owner. R-28 comment (1793-1794) shows the alloc was deliberate for the stack.

### F10 (stack, CONFIRMED within limit, close at -O0/-Os risk)
`-O2 -fstack-usage`: define_sel 3456 B (compose.c:1012), `wf_parts_prepare` 3376 (window.c:1917), `wf_parts_check` 3024 (1899), fd_pres 1728, fd_decide 1040, wf_prepare 720. All under the 4096 R-28 bar, but `wf_parts_check`/`wf_parts_prepare` hold an `mf_site` on the frame (`mf_site ps`) and `wf_part_site` copies the whole thing: 3 KB of frame margin gone at one more field. `tests/memfn/run_link_checks.sh` is the guard; not run (read-only). Suggest a field-count note at `mf_site`.

## Not findings (checked)
- Symbol hygiene: new exports `wf_plan_class`, `wf_plan_row`, `wf_plan_brow`, `wf_find_arm`, `fd_find`, `ofs_fn_serves`, `ofs_fn_define_at` all have `MF_NS` defines in kit.h; every new helper in window.c is `static`.
- `e_find_holds` itself is pure; `WF_NEROWS`/`WF_NDROWS`/`WF_NBROWS` are derived from the tables with `_Static_assert` pairing for `wf_b_text` (2454-2457) and `ff_name` (finder.c:78).

## Done well
- Shared frame/prologue/test: `wf_frame`, `wf_open/cand/close`, `wf_test_to` with the "THE SHARED PIECES" header; E-find is a real second caller of one mechanism.
- Table D, B and E are `kit_table`s on the one `kit_walk` (no parallel walk); `fd_find` asks the finder's own FIND slot rather than a private copy (addenda/kit.md "one table per slot" honoured).
- Retirements were mostly clean: `fd_nested_walk`, `kit_report_exact`, `fd_previews`, `fd_row_decides`, `mf_preview`, `SF_PROOF_EXACT` and `art->preview` are gone from code; tombstones are one-liners with the retired bit named (finder.c:109).
- `_Static_assert`s tie `ff_name`, `wf_b_text`, `MF_MAX_TERM`/`int8_t` grp, `MF_MAX_SPAN_POS`/`uint8_t` shift to their tables.
- HORS_MIN is labelled PROVISIONAL with its job, in-sample caveat and derivation (plan_cost.def:55-64); new deny rows are in options.def with the OFF arm stated.
- Frame use: the legacy translation moved off the stack (R-28) and the reason is in the code.
