# ic2 critic: check adequacy + trade audit (lens "checks")

Subject: lane/ic2 at 864902a48 vs BASE 614d45eb3. Source reading only: the
review tree had no build/ at any point (box-lock queue), so nothing below
was run; where a claim needs the compiler it is marked SUSPECTED and says
what would confirm it. No denylisted file was opened.

## Findings

### CHK-1 (design/maintenance, CONFIRMED by reading) The entry-point table does not derive from `--help` and a new mode OUTSIDE CLI_MODE_TABLE slips by
- Promised: inline_c.md 5.9 and 9.1 Stage 2: "the test enumerates the modes
  from `pcrec --help`'s mode table and fails on a mode with no row, so a new
  mode cannot slip past the gate".
- Built: tests/code/run_code_tests.sh arm 4 runs `sed` over the
  `#define CLI_MODE_TABLE(X)` block of cli/main.c (17 rows) and fails if a row
  of that macro has no line in the hand-written EP_ROWS. It never reads
  `--help` (nothing in the arm calls `pcrec --help`).
- Why it is narrower than the promise: CLI_MODE_TABLE (cli/main.c:672-689) is
  the table of PATTERN-QUERY modes only. Modes that exist today and are not in
  it: `--emit-support` (cli/main.c:1215, dispatched at 2403), `--subst` /
  `--subst-file` (1203, dispatched 2400), `--analysis`, `--measures`,
  `--view`, `--tune`, `--help`, `--version`. The writers `--pattern`,
  `--pattern-esc`, `-o -`, `--emit-main`, `--trace` have rows only because the
  lane typed them into EP_ROWS; nothing enumerates them.
- Input that would make it fail: a new `--list-*`/query mode added to
  CLI_MODE_TABLE with no EP_ROWS line (that does fail, and the
  `grep -qF -- "$m|"` test is sound: `--pattern|` cannot match inside
  `--pattern-esc|`, `--list-analysis|` not inside `--list-analyses|`).
  Input that does NOT make it fail: a new standalone flag of the
  `--emit-support` / `--subst` shape (an `else if (!strcmp(a, ...))` arm
  that compiles or emits). Who chose the input: the maintainer who adds the
  mode; the check can only fail on the 17-row subpopulation.
- Second hole: the class column (writes / describes / takes) is hand-chosen.
  A new table mode that actually compiles a pattern but is filed `takes`
  passes, because the `takes` assertion is "output and rc are identical with
  and without the grant" and an ungated writer is identical both ways.
- Floor: `nmodes -ge 15` against 17 rows; deleting two table rows is silent.
- Fix shape: derive from `pcrec --help` (or a `--list-modes` the CLI prints
  from the same macro) and add the non-table modes to the macro or to a second
  declared list the test also enumerates; make the class a column of the
  table, not of the test. Effort: small-medium. Blast: trust gate (D80 5.9).

### CHK-2 (design, SUSPECTED) The live-macro arm exempts exactly what the emitter keeps, so it cannot see internal `<PREFIX>_*` macros left live
- Promised (inline_c.md 3.2, spec match_api.md 11.9 para 4): before the
  include block the emitter `#undef`s "every artifact-internal macro", and a
  codegen check over a corpus "fails when that set intersects the macro set or
  holds any name outside the public contract". The design names
  `<prefix>_VALID_LB` among the macros that must be undef'd.
- Built: emit_code.c:159-166 keeps, with the first row `"\x01Q_"` prefix =
  ALL `<PREFIX>_*` names, plus `PCREC_*`, `RX_PASS`, `RX_FAIL`,
  `RX_ITER_INIT`, `__has_attribute`. The check (arm 7) subtracts
  `^(_|${upx}_|PCREC_|RX_PASS$|...)`, i.e. the same `<PREFIX>_` family. Code
  and check share one source for the exemption (learnings 3: a control that
  shares a source with what it controls).
- Evidence the exempt set is not only stamps: emit_dfa.c:3585 defines
  `<PREFIX>_VALID_LB`; emit_vm.c:12122-12230 defines `<PREFIX>_CHARGE_WORK`,
  `_PRUNE_TOO_SHORT`, `_PRUNE_CLAMP_SPAN`, `_TRAIL`, `_SET`, `_PUSH`, `_CUT`,
  `_CALL`, `_TIER_NOTE`; the only `#undef %s_...` in emit_vm.c is TRAIL/SET/
  PUSH (13165). So `_CUT`, `_CHARGE_WORK`, `_PRUNE_*`, `_CALL` are
  (by reading) still live at the segment block and the arm cannot report them.
- Population: the 8 patterns in the arm have no verb, no lookbehind, no
  `(*PRUNE)`; only `(?1)` exercises the call macros. The arm's own tripwire
  (`nart -ge 8`) equals the heredoc size, so it guards deletion, not reach.
- Confirm by: `pcrec --allow-code=c -p x -o x.c --pattern 'a(*PRUNE)b(?C`c: return RX_PASS;`)c'`
  and grep `#define` minus `#undef` before the first `#define RX_SUBJ`.
  Fix: classify the stamp family by what it is (object-like stamps and the
  declared list), not by prefix, in BOTH places from one declared table; add a
  lookbehind, a verb and a recursion pattern to the corpus. Effort: small.
  Blast: spec/design claim, not an answer.

### CHK-3 (trust/maintenance, CONFIRMED by reading) The one-call-form check reads x86-64 assembly and never shows the site is reached in the three "direct" builds
- tests/code/run_code_tests.sh arm 10: `grep -cE '^\s+call\s+\*'` over
  `$CC -O2 -S`. (a) On aarch64 (`blr`) the control build shows 0 indirect calls
  and the arm goes red ("the asm reader is blind"): loud, so not silent, but
  the Mac box named in CLAUDE.md as the fallback cannot pass this arm if it is
  arm64. (b) Only the control (`ua.c`, binding in another file) is shown to
  contain a call site. For `unity`, `embedded`, `artifact-as-callout` the check
  asserts `n == 0`, which is also what a build with the site deleted or
  dead-code-eliminated produces; there is no positive witness (e.g. the inlined
  `le3` compare, or a count of the callee's body in the .s). (c) It detects
  what gcc folded, not the source form: a regression from `<binding>.fn(&ctx)`
  to an opaque function-pointer variable that gcc still folds in a unity build
  stays green. The ruling (INLINE-C.md, 2026-10-27 ONE CALL FORM) asks for
  exactly "ONE check ... fails on any indirect call", so (c) is the ruling's
  own shape and not a finding against the lane; (a) and (b) are.
- (d) `sep_bind.c` is written (`printf ... > "$A/sep_bind.c"`) and never compiled
  or read: dead scaffolding.
- Indirect call fails it: yes when gcc leaves `call *%reg` (the control proves
  the reader sees one). A tail-call `jmp *` would not count, but the result of
  `fn(&ctx)` is consumed, so none occurs at these sites.

### CHK-4 (maintenance, CONFIRMED) Six of the eleven arms have no sabotage, and the trap rows accept any signal
- Sabotage coverage vs design 9.1 Stage 2 list: S-IC8 -> S1680, S-IC9 -> S1681,
  S-IC10 -> S1682, S-IC28 -> S1683, S-IC29 -> S1684, S-IC30 -> S1685. All six
  promised rows exist; S-IC7 deferred by R1 (not a finding).
- Unplanted: arm 4 (entry table), 7 (live macro), 8 (DT-4.1 and trap rows),
  9 (span helpers), 10 (call form), 11 (card), the bidi/control-byte refusals,
  and the `pattern-esc` `#line` path (emit_code.c:385; S1682 drops only the
  non-esc call at 377). learnings 3 says sabotage-validate every check; the
  design list is a minimum. At least these would be cheap: remove
  `code_undef_live` (arm 7), change `rx_u64`'s overflow bound (arm 9), make
  `RX_PASS`-for-`1` unreachable (arm 8), swap the call form (arm 10).
- `trap_row` (arm 8) passes on `rc > 128 && rc != 137`: SIGSEGV (139), SIGABRT
  (134), SIGFPE all count as "traps". `__builtin_trap()` is SIGILL (132) on
  x86-64 gcc. A check-returning-1 path that crashes some other way would be
  green. Assert the one expected signal (or that stderr/exit shows the trap).

### CHK-5 (maintenance, CONFIRMED by reading) rxtsource: head-bearing files now leave the independent leg-C comparison, the stale comment still says that is free, and the dropped population is unpinned
- tests/rxtsource/run_rxtsource_tests.sh: the C1 B-vs-C diff now drops leg B's
  rows for every head-bearing file (`awk ... !($2 in head)` into PROJ_B), and
  `check_counts C` subtracts `head_blocks`/`head_cases`. Today that is
  ipv4.rxt, geoip.rxt, frag/entry.rxt: 5 blocks, 16 subject-bearing case lines
  (counted by me: ipv4 3+12, geoip 1+3, entry 1+1). Leg C (the Python reader)
  no longer reads those cells; the harness and verify_code.py still do.
- The justification comment at lines ~1157-1165 ("a head-bearing file's leg-B
  dump is exactly zero rows too ... dropping it changes nothing it could have
  compared") is now false: these files have leg-B rows. Doc/maintenance.
- `head_blocks`/`head_cases`/`head_perr`/`head_group` are computed only to
  subtract; no assertion pins their values. A future head line added to a big
  corpus file moves that whole file out of the independent comparison with
  every count still reconciling (exact-count disarm; learnings 3 "floors answer
  did someone delete a lot, never the right ones"). Pin them
  (5 / 16 / 0 / 0) next to CENSUS_FRAGMENTS, which IS pinned and cross-checked
  against the raw `include` count (that part is good).
- The +6/+22/+46/+44 census moves are right: I recounted 22 `pattern` lines
  and 46 expectation lines in tests/code (5 `g`, 3 `perr`).

### CHK-6 (answer-adjacent, CONFIRMED) Two corpus cells in tests/code have no oracle, and verify_code's floor is below the real count
- verify_code.py is invoked with `"$SCRIPT_DIR"/*.rxt`: top level only.
  `frag/entry.rxt` (`m "xy" 0 2`) and `frag/frag_code.rxt` (`m "ab" 0 2`) are
  not given to it, and verify_rxt.py skips them as own-oracle (any
  `verify_*.py` up the tree), counting them in C3_SKIP_OWNORACLE/
  C3_FRAGMENT_LINES. Both cells are trivially true; the point is that "every
  corpus cell against libpcre2" (arm 2 header) is 34 of 36 m/n cells.
- Floor: the comment says "floor 30 against the 36 checkable cells"; the
  checkable count is 34 (ipv4 12 + macros 19 + geoip 3; macros' 2 consume cells
  are skipped). The floor leaves 4 cells of slack and the comment's 36 is wrong.

### CHK-7 (maintenance, SUSPECTED) No axes floor for tests/code, though the section links user C like callouts
- inline_c.md 3.6 / [r1 T6]: the axes runner must report, per axis, the count
  of section cases BUILT and LINKED and be red below a floor, because "a LINK
  failure gave no dump line on either side and was silent". run_axes.sh has
  that floor only for tests/callouts (lines 1506-1522, floor 45) and is
  unchanged by this diff. tests/code is discovered by the axes sweep
  (`find tests -name '*.rxt'`) and has `link geoip.c`; a link failure there on
  an axis is the same silent shape. Confirm by running one axis with geoip.c
  unreadable. The stage-2 test list does not name an axes floor, so this is a
  gap against 3.6's reasoning, not a missing promised test.

### CHK-8 (maintenance, low) The inline card's smoke arm cannot see a counting segment that never fires
- tests/code/card_inline.sh --smoke passes when it builds, runs, the inline and
  twin hit counts agree at 64 bytes, and >=3 rows read UNMEASURED. `fires`
  (the card's reason for the count build) is printed and never asserted:
  `site_hit` with `fires == 0` is green. Add `fires > 0` for site_hit and tail
  rows in smoke mode.

### CHK-9 (maintenance, low, SUSPECTED) HARNESS_BATCH path and `code_inc`
- run.sh adds `"${code_inc[@]}"` to `batch_member_compile` and the standalone
  compile. `code_inc` is a per-FILE global reset at each file's start; the
  batch compile runs at flush time. If a code-bearing block can ever be batched
  (HARNESS_BATCH>=1 is opt-in; `perr` and esc blocks are excluded, manifests
  are not obviously excluded) a member would compile with the last file's -I.
  Confirm by `HARNESS_BATCH=8 bash tests/harness/run.sh tests/code/` (not run:
  forbidden). Low: default is 0.

### CHK-10 (design, low) Harness entry in 5.9 has no row of its own
- 5.9: "plus the library and harness entries". The library is fully covered
  (pcrec_compile is the only public compile entry; lib_check.c has 6 rows incl.
  `features "all"` and `"code-c"`). The harness's grant is covered through the
  manifest (S1684) but `build/pcrec-harness`/`pcrec_harness_compile` is not
  exercised as an entry with and without the grant.

## Per-sabotage plant audit (read the plant, applied to the source)

| row | compiles? | catches for the stated reason? | note |
|---|---|---|---|
| S1680 (mod_callouts.c) | yes: `i`, `j`, `n`, `k` all in scope at the BEFORE site; `continue` inside `for(;;)`; BEFORE text matches lines 94-97 once | yes: arm 3 "unknown attribute is refused (S-IC8)" wants "bogus"; the plant makes pcrec accept -> "pcrec ACCEPTED it". The callouts suite would also see it but SAB_SUITES names only `code` | reach row proves the refusal text exists pre-plant |
| S1681 (compile.c) | yes: `pcrec_code_all_langs()` is in internal.h:5733, declared before use | yes: arm 3 no-grant row, `t2.rxt` block 1 (`perr` unmet), entry table "writes" rows (refused-without-grant fails), lib_check row 1; also trips the unknown-language row (`py`), incidental but same cause | |
| S1682 (emit_code.c) | yes: only the non-esc `code_line_dir` call is bypassed; the function is still used at 385/415 so no unused warning | yes: arm 5 `err.rxt:3:25` and `<command line>:1:17` read gcc's text; with the plant gcc names the generated file. `pe.rxt` (esc) is NOT touched by this plant | exact column pinned (8+16+1=25): good; quoting broken `error:` shape on purpose |
| S1683 (enabled.c) | yes; BEFORE matches line 295 at 16 spaces | yes: arm 3 `blk_all`/`cfg_all`/`--features all`, `t2.rxt` block 2, lib_check `"all"` | |
| S1684 (tests/harness/run.sh) | yes (`true \|\| return 0`) | yes: with the entry test gone the manifest's grant reaches `frag_code.rxt` (same dir, same manifest), the `perr` block compiles, case fails, run.sh nonzero -> arm 1 bad | SAB_REACH only proves the include line exists, not that the plant fires; the row's DETECTED verdict is the real proof |
| S1685 (emit_dfa.c) | yes: `cx->emit_in->code_headers[].header` exist (internal.h:276) | yes, and by the TEXT check first: arm 6 compares line numbers of `#include "poison.h"` vs the last `ph_search(const unsigned char` definition, so it reads "does not follow the matcher" rather than a compile error; the compile is a second line | `poison.h` poisons memchr/memcmp/memcpy and the arm first greps that the matcher uses them: a good non-vacuity guard |
| S693 (abi 90/89) | yes | unchanged detector | |

Mech arm (`code`, run_sabotage_matrix.sh): mirrors `callouts`; runs
run_code_tests.sh from the sabotaged tree, so S1684's edit to run.sh is the one
the arm executes. Scored from the `checks failed:` trailer.

## Promised vs delivered (inline_c.md 9.1 Stage 2, 5.7, 5.9, 3.2, 3.6)

Present: UC-1a DT-1.1-1.6 (ipv4.rxt); UC-3 DT-3.1/3.2 (geoip.rxt, with a
polarity pair so the user function is shown reached), DT-3.3 (4 rows incl.
`pattern-esc` and a missing header), DT-3.4; DT-4.1 inline; entry table (see
CHK-1); `features all` refused in block/config/`--features`/library;
`features code-c` and `pcrec`-line `--allow-code` refused; fragment refusal
(frag/); T2 (t2/); check returning 1 and falling off the end (traps, see
CHK-4); live-macro corpus (CHK-2); bidi (U+202E), U+200B and C0 refused and
named; reached code refused; measurement card (smoke only, CHK-8); the six
sabotage rows.
Missing or narrowed: (1) entry table derivation from `--help` (CHK-1); (2)
"the harness" entry (CHK-10); (3) the "flagged" half of "bidi refused and
flagged" is stage 3's reviewer view, fine; (4) 3.6 axes floor (CHK-7); (5)
`pcrec`-line `--features all`/`code-c` rows (only `--allow-code` in a `pcrec`
line is tried; `--features` itself is covered on the CLI and the `pcrec` line
shares that parser: low). Deferred and NOT findings: S-IC7, the scanner table,
the `(?{` rows (R1).

## Trade audit (every moved number in tests/)

| pin | old -> new | gained / given up | explained? |
|---|---|---|---|
| ABI_EXPECT (codegen) | 89 -> 90 | tracks the abi bump; no stale 89 reader remains (grepped tests/, src/, spec, lib) | yes |
| S693 | 90 / 89 | re-aimed, same detector | yes |
| recursion-identity FILEPIN | 719a17ccb -> 94568296a (lane self-pin) | `git diff 94568296a..864902a48` touches no src; later commits are tests/docs | yes; conventional |
| cli case11 rows | 51 -> 52 | the code-c row | yes |
| reject iteration | 132 -> 133 | the code-c row, nothing retired | yes |
| registry rows / built / families / ports | 143->144, 115->116 built, 104->105 families, 96->97 ports, 76/63/63 -> 77/64/64 | one new row, one producer, built | yes, each with a dated comment |
| registry PASS / PC-3 | 232->233, 216->217 | "MEASURED" per comment (not reproducible by me: no build); +1 each is consistent with one row | claimed measured |
| registry witness lookup | pass 0 prefers a witness whose name equals the row's syntax | changes the match rule for ALL VM_ONLY rows, not just the two sharing (group,'C'); row coverage still forced by `checked != built_wired`; pass 1 keeps old first-match | explained in a comment |
| compliance_section.py rows | 143 -> 144; double-backtick fence | needed for a backtick in a syntax; syntax_index_check CELL_CODE regex widened to N backticks (`^(`+)(.*?)\1$`) | yes |
| rxtsource CENSUS_FILES/BLOCKS/LINES | 300->306, 6219->6241, 74663->74709 | +6 files, +22 blocks, +46 lines: recounted, exact | yes |
| RUNSH_*, C3_SKIP, C3_SKIP_OWNORACLE | +6/+22/+46, +44, +44 | exact | yes |
| C3 discovered files | CENSUS_FILES -> CENSUS_ENTRIES = FILES - 1 fragment | fragment cross-checked against raw `include` count | yes |
| rxtsource head-bearing handling | new | GIVEN UP: independent leg-C cross-read of 5 blocks/16 cells; unpinned (CHK-5) | partly: stale comment |
| keyword census | 28 -> 27 (`include` graduated) | the format keyword now has a use in the corpus | yes |
| shards.tsv | test-code 60.0 "ESTIMATED" | a guessed cost in a measured table | labelled |
| san_scripts.txt | +tests/code/run_code_tests.sh | gains ubsan/asan on both axes | yes |
| verify_rxt.py | head-bearing + own-oracle -> counted skip instead of ValueError | gives up python re-check of tests/code (replaced by verify_code.py) | yes |
| verify_code floor | 30 vs 34 real | CHK-6 | comment says 36 |

## PROBED-AND-HELD

- Entry-point derivation logic on the 17 table rows (read-only reading): every
  row has an EP_ROWS line; fixed-string matching has no prefix collisions
  (checked `--pattern`/`--pattern-esc`, `--list-analysis`/`--list-analyses`,
  `--emit-ir`/`--emit-facts`); `describe` rows catch a raw multi-line print
  (NLMARK at column 0); `writes` rows require refused + message + no file + rc 0
  with the grant. (17 rows + 6 hand rows read.)
- Refusal arm: 16 `refuse` rows. `$?` after `err="$(pc ...)"` is the command's;
  the "wrote nothing" check removes the output first. Each of the five .rxt
  grant routes (block `features all`, config `features all`, config `pcrec`
  line, block `features code-c`, reached code) has its own row.
- DT-3.3 column arithmetic: `err.rxt:3:25` (8-char `pattern ` + 16 chars) and
  `<command line>:1:17` (16 chars) both recomputed by hand and agree.
- t2/ and frag/ rely on `perr`, which asserts no reason; held because S1681,
  S1683, S1684 each flip exactly one of those blocks.
- Harness entry-only rule: `rxt_entries` is filled after the fragment-drop
  (rule 3) so a fragment is never an entry; manifest and fragment share a
  directory, which makes S1684 a genuine witness.
- ipv4/geoip/macros cells: all three directions of each predicate exercised
  (pass, veto, boundary); geoip proves reach by polarity (a public and a
  private address). Counts: 12 + 3 + 19 verifiable m/n cells.
- verify_code.py: the macro set is re-written independently (functions, from
  11.9) and `(?J)` walking matches the emitted algorithm by reading; `pattern-esc`
  lines go to `unread` and turn the arm red, so they cannot be silently skipped.
- span_check.c: references are written from the table (UTF-8 from Table 3-7,
  overflow by a second formulation of the bound); population 7^0..7^3 spans x
  57 needles plus 256x9x9x9 UTF-8 shapes, far above its 100000 floor.
- Registry/reject/cli pins: every +1 is one row and carries a dated comment.
- Self-pin: no src commit after 94568296a.
