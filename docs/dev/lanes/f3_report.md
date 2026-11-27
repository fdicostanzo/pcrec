# f3 report: [ARENA-SCOPES] F3, the three whole-artifact rewrites as STRBUF scope clients

## Summary

Unit F3 of `docs/design/arena_scopes.md` is built on `lane/f3` (cut from main 399469aad). `target_headers_render`'s
`nb` (S10), `splice_mark`'s `tail` (S11) and `render_buf`'s `o` (S12) are now `pcrec_scope_sb` entries of a scope on
`&cx->arena`. `nb` and `o` hand their storage to csb/hsb through `pcrec_sb_adopt` (R1) before the close, so nothing is
copied. The deletions the design names are done: the scanner's 3 `ALLOW` rows and its `shape:NAME` narrowing, and
alloc_check's `target_headers_render` filed row with its stack recording and `fn` column. I also deleted the
filed-stranding table itself, because it is empty now (a judgment call, see Changes). S3572 is re-aimed at S11,
S3584 at a scratch-beside-heap second declarator, W6 is re-pinned UP (1014 of 1057), and K155's remainder is closed in
code. No abi change: 42 compiles (7 patterns x byte/utf8 x auto/vm/dfa) are byte-identical to the older main build.
SCOPE-4 measurement: above memgate's noise (noise 0 B) on VM wide-class compiles under `-e utf8` (108 of 7,402
movers, all down, median -131,120 B, max -327,920 B = -8.9%), invisible in memgate's standard population (byte, auto
engine: 0 of 2,000). Reported, not built. Heavy validation is OWED to the queue (keys in STATE AT HANDOFF), plus one
cloud growth run.

## Premise test

On main 399469aad, before any edit:
- (a) the three sites, found by name: `src/gen/memfn_stamps.c` `target_headers_render` (`StrBuf nb = { .cx = cx }`,
  heap), `splice_mark` (`StrBuf tail = { .cx = sb->cx }`, heap, freed only on the normal return), `src/gen/part_layout.c`
  `render_buf` (`StrBuf o = { .cx = cx }`, heap). Each is live across `pcrec_sb_printf`/`pcrec_sb_puts` (nomem) and,
  in `render_buf`, across `pcrec_ctx_fail`. Nothing frees any of them on a longjmp. HOLDS.
- (b) `git grep -n pcrec_sb_adopt -- src`: the definition (sb.c), the declaration (internal.h) and the two transplant
  calls (memfn_stamps.c `pcrec_sb_adopt(c, &nb)`, part_layout.c `pcrec_sb_adopt(sb, &o)`). HOLDS.
- (c) `tests/core/alloc_check.c` `known_stranded[]` held the one row `{ "src/core/sb.c", "target_headers_render", ... }`.
  `tests/core/scratch_builder_check.py` held the 3 rows `strbuf:nb`, `strbuf:tail`, `strbuf:o`, and `admits()` parsed
  `shape:NAME`. HOLDS.

## Changes

Commits on `lane/f3`: 8e6ef9d37 (code, checks, sabotage), 96785ba94 (W6 pin, K155, design), plus the report commit.
- `src/gen/memfn_stamps.c`: `splice_mark(Ctx *cx, StrBuf *sb, ...)` (its 2 callers pass `cx`; `sb->cx` is the same
  Ctx, compile.c sets `csb.cx = &cx`). The tail is a scope STRBUF entry, and the close replaces `pcrec_sb_free`.
  `target_headers_render` opens its scope at pass 2, after `pcrec_memfn_target_headers`, so no kit call runs inside it.
  The `adopt` comes before the close. The anchors of S1897 (`rest = strchr(...)`) and S1899 (`- nheld * strlen(held)`)
  are unchanged.
- `src/gen/part_layout.c` `render_buf`: the scope opens after the early return, `o` is a `StrBuf *`, and the close
  comes after the adopt and `layout_bytes = 0`. Arena allocations made inside the scope (`stamp_lines`'
  `pcrec_sb_scratch`, `pcrec_sb_upper`) are ordinary attempt-arena blocks and take no registry record.
- The comments follow r105 SCOPE-3's wording: compile_driver's handler-top unwind releases on a refusal; the teardown
  runs only on the count_groups/syntax_dump routes.
- `tests/core/scratch_builder_check.py`: the 3 `ALLOW` rows are deleted. `shape:NAME` is deleted: `classify` returns
  shapes only, `admits` compares shape, file and function, and the MUST_FLAG fixtures are shape-only. The fixture
  whose purpose was the name (`nb, leak`) is dropped, and the scratch-then-heap second-declarator fixture stays.
  `MIN_SCOPE_OPENS` 2 -> 3 (D110: half of the 6 opening sites, grep in its comment). The docstring's SINGLE-CONTROL
  line names S3584 instead of the old S3572 shape.
- `tests/core/alloc_check.c`: deleted `known_stranded[]`, `known_stranded_seen`, `N_KNOWN_STRANDED`, the
  `stack_file`/`STACK_N`/backtrace recording, `stack_has` (addr2line), `ChildReport.known`, exit code 5, `Tally`'s
  `n_known_stranded` with its NOTE line, the stale-row loop, the unwinder warm-up, and the `dladdr`/`<dlfcn.h>`/
  `<execinfo.h>` it needed. `--sites` still prints each live block's `file:line`.
  JUDGMENT (the manager may revert it): the design deletes the row, the stack recording and the `fn` column, and does not
  say whether the table stays. With no row left, the table, its seen counts, code 5 and the stale loop can never run,
  which is an unreached mechanism (learnings section 3). A zero-length C array would also need `{}`, and its
  `j < 0` loops would draw `-Wtype-limits` noise. A later filed stranding brings the table back with its first row
  (git history has it).
- W6 is re-pinned UP (D110), `504, 1010, 0` -> `504, 1014, 0` (the floor 504 is kept). Measured with `make alloc` (this
  tree, whole run, log `$PCREC_TMPDIR/scratch/f3/alloc_full.log`): "W6 (compound split): 1014 of 1057 forced
  allocations were SUCCEEDED THROUGH", against 1010 of 1045 at F1. The 12 new trials are the scope records of
  `splice_mark`/`render_buf` inside the part compiles, and 4 of them are absorbed by the compound fallback. This was
  the only red in that run. W1-W4, W6 sustained, W7 control (STRANDED), W7/W3 (528) and W5 are all PASS.
- Sabotage: S3572 is RE-AIMED (file renamed `S3572_scratch_tail_back_to_heap.sh`). Its plant puts `splice_mark`'s
  tail back on a heap local behind the same pointer name. S11 has no dynamic witness (D-8: SINGLE-CONTROL), so this
  is its net. S3584 is RE-AIMED at `target_headers_render`'s scratch `lines`: the plant adds a heap second declarator
  (`lines = pcrec_sb_scratch(..), leak = { .cx = cx }`). Neither is retired. Both plants were applied to a scratch
  copy, and each read FAIL from `scratch_builder_check.py` at the planted line. `VALIDATE_ONLY` validated
  S3572/S3584/S1897/S1899.
- Docs: `docs/design/arena_scopes.md` "Deviations at build" has an "F3 BUILT" entry. `docs/dev/known_issues.md`
  K155 has a new heading and an F3 Status paragraph (FIXED in code; the confirmation owed is the cloud growth LSan
  run). `docs/testing.md`'s stranded-heap paragraph says there are no exceptions now and gives W6's new pin.
  `tests/core/CLAUDE.md` drops the "clients by object name" wording.
- Not touched: plan.md (the [K155-STAMPS-LEAK] and [ARENA-SCOPES] row states are the manager's), memfn/, any spec (no
  caller-observable change, D80: none).
- REGISTRY-1: none of the three clients is reachable from `pcrec_facts_force_all`, because both renders run before
  `facts_force:` in compile.c. Its trigger has not fired.

## Checks moved

- Run locally (quick): `make -j16` clean; `make strict` clean ("whole tree compiles clean with -Werror -Wshadow");
  `python3 -I tests/core/scratch_builder_check.py .` PASS (92 files, 23 scratch builders, 21 allowlisted sites, 6 scope
  sites); `python3 -I scripts/m6read_check_sab_anchors.py` "all runner plants apply"; `gcc -fsyntax-only -Wall
  -Wextra tests/core/alloc_check.c` clean; mech `VALIDATE_ONLY` on S3572 S3584 S1897 S1899: 4 valid; emitted-byte
  identity, 42 of 42.
- `make alloc` (whole run, before the W6 re-pin): 12 passed, 1 failed (W6 single, the pin). After the re-pin the run
  is OWED (`190-f3-alloc`).
- Scanner population: ALLOW 24 -> 21 rows (all reached). The scope opens are 3 -> 6. `shape:NAME` has 0 users.
- alloc_check: the `known_stranded` rows go 1 -> 0 and the table is deleted.

## Memgate prediction

`sizeof(StrBuf)` = 192, measured by compiling `sizeof` against `src/core/internal.h`. A STRBUF record asks
`calloc(1, offsetof(LEnt, payload) + 192)` = 16 + 192 = 208 B. A MARK asks 16 + 24 = 40 B. Each rewrite therefore adds
+248 B of requested bytes while it is live. At most one rewrite is live at a time (all three are leaves), so a
compile's peak moves by +248 B when the peak falls inside a rewrite, about 97% of compiles per the design (C13), and
by 0 to +248 B otherwise. The bound I used is the brief's and C13's: 256 B (`MEMGATE_BOUND=256`). `rungs`: requested
peaks move by at most 248 B, so a rung move should read LAYOUT or IDENTICAL. PRE-READ (local, not the gate): `memgate.py prep base --ref 399469aad` against
this branch's HEAD (`$PCREC_TMPDIR/scratch/f3/s4/X`), `peak --limit 1500 --bound 256`: "delta (B-A) min 0 median 248 max
248; B>A 1351, equal 149, B<A 0", attempt-arena high-water raised on 0, "VERDICT WITHIN (bound 256 B: 0 over)"
(log `$PCREC_TMPDIR/scratch/f3/pre.log`). That matches the prediction exactly. The full population with `rungs` and
`instr` is the queued `200-f3-mg`.

## SCOPE-4 measurement

This was a measurement only; nothing is built or delivered. The prototype, in scratch copies only
(`$PCREC_TMPDIR/scratch/f3/s4tree`), is F2's shape on `pcrec_clskit_emit_whole`: after the empty return, open a
scope on the parent, run the body on `pcrec_scope_arena(&sc)`, then close. Both sides are git archives of this
branch's HEAD; side Y adds the prototype. The memgate tool was a scratch copy (`$PCREC_TMPDIR/scratch/f3/mgtool`)
with two env levers the in-tree tool lacks: `MG_ENC` sets `pcrec_options.encoding` in `mg_drv.c`, and `MG_ENG` sets
the corpus engine. The in-tree memgate population is byte mode with the auto engine.
- Noise: A/A, side X against a copied directory X2, 2,000 compiles: 0 B, 2,000 equal.
- The two named patterns, `-e utf8`, VM engine, requested peak: `x\p{L}y` 3,554,680 -> 3,423,560 (-131,120, -3.7%).
  `x[\p{L}\p{N}\p{M}]y` 5,390,752 -> 5,128,392 (-262,360, -4.9%). The attempt-arena block high-water drops by the same
  amounts. Under the auto engine (DFA) both are unchanged (`emit_whole` is not reached).
- Corpus slice, memgate's own regime (byte, auto engine), 2,000 compiles: 0 movers. Under `-e utf8` with the auto
  engine, 2,000 compiles: 0 movers. Under `-e utf8` with `MG_ENG=2` (VM), first 2,000: 0 movers.
- The full population under `-e utf8` + VM (5,814 corpus + 1,588 growth cells = 7,402 compiles, 0 errors): 108 movers,
  ALL DOWN, all corpus. Delta min -327,920 B, median -131,120 B, max -120 B. Relative: median -2.8%, max -8.9%
  (`corpus/5774`: 4,914,792 -> 4,586,872). No compile rose, and the attempt-arena high-water fell on 108.
- VERDICT: ABOVE NOISE where it applies (memgate noise is 0 B, and the moves are 120 B to 328 KB), but only on VM
  wide-class emission under UTF-8. memgate's standard population cannot see it. Commands: `MG_ENC=1 MG_ENG=2 python3 -I
  $PCREC_TMPDIR/scratch/f3/mgtool/memgate.py peak X Y OUT --jobs 16` (sides under `$PCREC_TMPDIR/scratch/f3/s4/`; TSV
  `s4/o_vmall/peak.tsv`). For the manager's ruling: the build would be F2's shape, about three lines plus a static
  body function. A memgate that measures it would need an encoding lever (`MG_ENC`), which is a separate question.

## Cloud runs

PLACEHOLDER (filled after dispatch).

## STATE AT HANDOFF

PLACEHOLDER
