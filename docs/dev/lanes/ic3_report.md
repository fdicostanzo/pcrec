# Lane ic3 report: [INLINE-C] stage 3, sha-pinned includes and the reviewer's view

Lane ic3 (opus), branch `lane/ic3`, based on main 89831df9a. Design:
`docs/design/inline_c.md` "Stage 3", §1.9, §3.3, §5.2-§5.6. 2026-10-29.

## Summary

Stage 3 is built. Code read from another file now compiles under the grant
when every `include`/`lib` chain to it is pinned:

- `sha256 <hex64>` on `include` and `lib` lines, verified over the bytes the
  reader parses;
- the every-chain rule (order independent);
- a site inside a composed definition is admitted and sees the definition's
  own groups;
- a lib's `code-header` lines travel with its segments;
- the harness compiles a fragment's block through pcrec's FILE path
  (`--include-block`), so pcrec, not the harness, judges provenance;
- `pcrec --list-callouts FILE` is the reviewer's view.

F38 (source on the node) and F27 (the entry class as a CLI_MODE_TABLE
column) are built. F28/[OPT-SCOPE] is not built and no per-option scope
check was needed. Emitted bytes do not move for any existing input, so
there is no abi event (abi stays 91; the mover census in job 680 is the
check). All local suites are green; see "Tests and sabotage".

## Premise test

The brief's premise was that a lib definition reaches the target through a
call that the composer wraps (`A_REP{0,0}(A_CAP)` + `A_CALL`), so lifting
§1.9 rows 3b/4 needs:

- (a) the sites pass to walk through calls;
- (b) a per-site view map.

Probed before building:

- `target t = u` with `(?&d)` and a callout in `d` was refused by
  `src/opt/callout.c`'s "reached by a subroutine call" rule;
- `rc_assign` erased a definition's undelivered groups, which would leave a
  view with no slots.

Both held. A cost the design did not state: the composer CALLS a definition
(one body, many calls) rather than splicing it. So "two calls give two
sites" (§1.9) is false here, and see Design deviations 1.

## What was built

- **shared/sha256.{c,h}**: the one SHA-256, moved from `analyze/`, with its
  own CLAUDE.md. It is compiled separately into libpcrec and into
  `build/pcrec-analyze`.
- **Pins and the reach graph** (`src/parse/rxt_source.c`):
  - `path_pin` parses `"path" [sha256 <hex64>]`, which is §1.6¶7's
    spelling, case-insensitive;
  - every include and lib edge is recorded with its pin and its target's
    digest (one read: `slurp_lines` hashes the buffer it parses, and a
    fragment parse is kept rather than re-read);
  - `pcrec_rxt_reach_verify` refuses a stale pin whether or not there is
    code or a grant;
  - `pcrec_rxt_reach_unpinned` returns the first unpinned line of the first
    chain holding one, from a taint-state DFS (bounded at 2 x edges, so it
    terminates on cycles);
  - an OOM fails closed.
- **The trust rule** (`src/parse/mod_code.c`): `local` when the code's file
  is the local one; otherwise `pinned`, or refused naming the code's
  file:line and the unpinned line.
  - Under `code_review` (`--list-callouts`), the refusal and a
    bidi/control flag are recorded on the node instead of raised.
- **F38**: source text, file, line, column and escape state live on the
  A_CALLOUT node. A definition's site names its own file in `#line`.
- **The definition-site view** (`rxt_compose.c`, `callout.c`, `emit_vm.c`,
  `emit_code.c`):
  - a definition holding a site keeps all its groups;
  - each site carries `view_n`/`view_map`/`view_names`;
  - `vm_callout` builds a local `P_co_view[N][2]` only at such sites;
  - `RX_G_` names are re-pointed for the segment and restored after it;
  - the sites pass descends through `A_CALL`: a definition reached twice is
    `repeated`, and one reaching itself is refused.
- **Lib code-headers**: emitted with the segment, deduplicated, under a
  `#line` naming the lib file.
- **`--include-block FRAG:LINE ENTRY`** (`cli.md` §1.23): compiles one
  fragment block as a local pattern whose provenance is the fragment,
  reached from ENTRY's closure.
  - The harness uses it for every fragment block of an entry whose manifest
    grants code (§5.2).
- **`--list-callouts FILE`** (`cli.md` §2.15, `src/dump/callouts_dump.c`):
  - 13 columns: target, site, source, binding, symbol, lang, width, class,
    class_reason, trust, chain, flag, code;
  - every byte outside printable ASCII is printed as `\xNN`;
  - it is a DESCRIBE mode, so the same rows come out with or without the
    grant.
- **F27**: CLI_MODE_TABLE gained a class column (`TAKES`/`DESCRIBE`/
  `WRITES`). It is read by the dispatcher (the describe grant) and by
  `run_code_tests.sh` arm 4, which now reads every mode's class from the
  table.

## Design deviations

1. **Site numbering for a definition called more than once**
   (§1.9 "two calls give two sites").
   - What was built: one site, numbered once; its class is the worst over
     the calls (`repeated` with two calls).
   - Why: the composer emits one body and calls it, so there is one site in
     the artifact. Splicing would be a composer remodel.
   - Spec: match_api §11.1¶1b states the built behaviour.
2. **Mismatch wording** (§5.5).
   - Built: `include "PATH": sha256 pin mismatch, the file hashes to <h>;
     re-inspect it, then update the pin`. The design's sentence also
     repeats the pin and the naming line.
   - Why: the full sentence overflows `pcrec_error.msg`'s 256 bytes on
     real paths ([ERR-MSG-TRUNC] is filed). The line is in the
     diagnostic's `file:line` prefix and the pin is in the file.
3. **`--list-schema`** (§5.3: "shows the key on both rows").
   - The schema's value column stays `token`. Per `check_value_shape`'s
     rule, the pin grammar stays with the production; a schema clause
     would need a new constraint kind.
   - The pin is documented in rxt_format §1.1 and §1.1.1, and §1.6¶8 is
     amended (pcrec checks head pins, not case-line pins).
4. **One row source** (§5.6: the IR listing's `callouts` section).
   - `--list-callouts` reads the compile's own A_CALLOUT nodes through the
     driver's facts hook (a projection, not a second derivation). The IR
     listing's `callouts` section stays unbuilt.
   - The "mode" and "4.3 row" columns are absent: they are stage 4's
     `verify`.
5. **The D27 row `file.local_def_delivering_refused`** was a MASKED row
   (D27 finding 3.3) asserting a refusal that stage 3 removes.
   - It is re-pinned as `file.local_def_delivering_admitted` (build
     succeeds, `t.c t.h` written).
   - match_api §11.9¶8a's "not observable today" paragraph is replaced by
     the observable rule.
6. **`run_code_tests.sh` arm 3**: the needle "is not allowed" (the pre-pin
   refusal) became the stage-3 refusal "carries no sha256 pin".

## Tests and sabotage

- **Arm 13** of `tests/code/run_code_tests.sh` (38 checks, all PASS
  locally): every test the brief lists.
  - The FIPS 180-4 vectors run against `shared/sha256.c`, and pcrec's
    digest of the four `frag/pin[1-4]_*.rxt` files is checked against
    `sha256sum`.
  - The definition-site view check runs a driver (ncap 3, group 1 `a`
    while the caller's group 1 is `x`, `RX_G_w` 2).
  - The F38 `#line` row is the ASan corpus row (it rides `make asan`'s
    code axis).
- **Corpus**: `tests/code/frag/` gained one four-file chain:
  - `pin1_entry` -> `pin2_ok`, pinned in upper-case hex, whose code
    compiles;
  - `pin2_ok` -(no pin)-> `pin3_mid`;
  - `pin3_mid` -> `pin4_leaf`, pinned, but its code is refused because a
    middle link is unpinned.

  The harness compiles these files via `--include-block`, and
  `verify_code.py`'s CELLS_PIN goes from 36 to 41. The chain is linear
  with numbered names because of K132.
- **Arm 4 (F27)**: 18 modes, classes read from the table.
- **D27 suite**: 545 passed, 0 failed.
- **Sabotage rows** S1760-S1764. Each row's reach command was checked on
  the clean tree; mech in job 681.

| row | design id | sabotage |
|---|---|---|
| S1760 | S-IC12 | the pin compare is skipped |
| S1761 | S-IC13 | only the last link is checked |
| S1762 | S-IC14 | the local exemption reaches an `--include-block` block |
| S1763 | S-IC31 | the first chain's verdict is used |
| S1764 | S-IC32 | the view uses the caller's numbering |

Local results:

- `make test-code`: green before the fixture rename, except two digest
  checks; both are fixed. After the rename, the `--include-block` rows
  and the digest rows were re-checked by hand. The full suite rides
  job 680.
- `make test-rxtsource`: green after the census re-pins (+4 files,
  +4 blocks, +6 lines; 4 fragments; head 8/21/3; C3 SKIP and own-oracle
  +1; fragment lines 7).
- Green: strict, test-cli, test-registry, test-codegen, test-callouts,
  test-recursion, test-claudemd-size and test-corpus
  (`scratch/ic3/logs/small1.log`).
- `test-spec` is red: K131, pre-existing and not in make test.

## Movers and abi

No emitted byte moves for an existing input. The view, the `RX_G_`
re-pointing and the lib headers apply only at sites inside composed
definitions, which every existing input refused before.

Job 680 runs `docs/dev/lanes/ic3/movers.py` (main 89831df9a vs lane/ic3,
both abi 91):

- every corpus and bench pattern line, in six `--pattern` cells including
  a granted `--allow-code=c` cell;
- the 44 target-bearing `.rxt`/`.rxtin` files as FILE operands.

Expected: 0 unexpected. `tests/code/d27/rxt/deliver_local.rxtin` is the
one declared GAINED file (deviation 5). abi stays 91.

## OPT-SCOPE and F27

- **F28/[OPT-SCOPE]**: not built, as ruled.
  - The describe grant needs no per-option scope check: the CLI decides it
    once from the mode's class column.
  - `--include-block` and `--list-callouts` refuse other modes through the
    existing MODE_ADMITS sets.
- **F27**: built as ruled. The class column is read by the dispatcher
  (`cli_mode_class`) and by the entry-point test, which no longer keeps
  its own copy of the classes.

## Filed rows

- **K132**: the rxtsource C1 legs diff blocks in order, and leg B
  (run.sh) orders a closure differently from legs A and C (file name).
  Its head-row count also assumes one declaration per file. It is worked
  around in the fixtures, not the check.

Deviation 2 rides the existing [ERR-MSG-TRUNC]. The unbuilt IR
`callouts` section (deviation 4) is already the design's §5.6 text, and
stage 4 owns its columns. K133 and D181-D182 are unused.

## STATE AT HANDOFF

Rulings file `docs/dev/lanes/ic3_rulings.md`: the last entry applied is
**R1** (manager, 2026-10-29: queue 680/681 well before 19:30; declare no
`not-before`). Both jobs were queued with no `not-before`, and the lane
builds nothing on the box after queueing.

Branch `lane/ic3`, commits 24c77044a..HEAD. Queued jobs:

- `680-ic3-test`: build, strict, the mover census and make test;
- `681-ic3-mech`: S1760-S1764.

Merge on 680 and 681 GREEN.
