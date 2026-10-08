# posswcls — [CLS-TREE] census [5b] red on the [ART-POSS-ARMS] arms (2026-10-07)

Lane `posswcls` (opus), branch `lane/posswcls` from possfin `e8c676d3`.
Trigger: posstri's full `make test` red in `test-cpset-structure`,
`tests/codegen/run_wclass_census.sh` PART 1:
`[5b] A_WCLASS shares an arm with A_CLASS` at `src/opt/possessify.c:297,
:382, :1281, :1467`.

## Verdict

**No miscompile. The shipped arms code cannot read a wide class's set:** all
four flagged switches run inside `pcrec_select_engine`, ABOVE
`pcrec_lower_enc` (src/core/compile.c:1662 vs :1726), and `A_WCLASS` is made
only by that lowering (D-1). A wide class reaches this pass as an `A_CLASS`
of code points, which `first_of` widens past 0xFF (`pcrec_cls_bits_widen`,
the sound direction). None of the four sites reads a set itself anyway:
three defer to `first_of`, whose own `A_WCLASS` arm is the loud
`pcrec_wcls_misplaced`, and one is a leaf return in an index walk.

The red was the census's correct objection to the arm SHAPE (a label run
holding both kinds), not to behaviour. The census has no exemption
mechanism, so the sites were restructured, not allowlisted.

## Per site (line numbers at e8c676d3)

| site | function | what the shared arm did | correct? | fix |
|---|---|---|---|---|
| :297 | `cap_index` (arm B's capture index walk) | leaf `return` | yes, reads nothing | own arm `case A_WCLASS: return;` with the S3 comment, `pss_walk`'s idiom (a hunting walk) |
| :382 | `text_first` (arm B's TEXT first) | `return first_of(q, a)` | yes, `first_of` is loud on it | own arm `pcrec_wcls_misplaced(q->cx, "text_first")`, `first_of`/`gk_build`'s idiom |
| :1281 | `ps_node` (arms A0/A1 summary) | `break` to `first_of` | yes, same | own arm `pcrec_wcls_misplaced(P->cx, "ps_node")` |
| :1467 | `item_first` (arm A1 plain fold) | `break` to `first_of` | yes, same | own arm `pcrec_wcls_misplaced(P->cx, "item_first")` |

The loud arm names the walk that met the node. The old fall-through into
`first_of` refused too, but under `first_of`'s name. Behaviour is otherwise
identical, and so is every emitted byte (the node never arrives).

## Evidence (measured, not argued)

`build/wcls/probe.py` / `probe2.py` (scratch, uncommitted): wide-class
patterns in the arms' shapes. Each was compiled by pcrec with the arms on
and with `-fno-poss-ctx-follow -fno-poss-bref-first`, under `-e utf8`,
`-e utf8 --ucp` and `-e utf8 -i`, then compared on the group-0 span
against libpcre2 10.46 (ctypes, UTF / UTF|UCP / UTF|CASELESS) over every
subject of length <= 3 on {a, x, é, É, Ā, space, .} (400 subjects).

- probe (default route): 65 pattern x config compiles, 26,000 cells, **0
  diffs**. 13 compiles were refused by pcrec under `--ucp` (UCP `\b`/`\w`
  under utf8 is not built yet, U3/U4), and libpcre2 compiled them all.
- probe2 (`--engine=vm`, +10 A-shapes with a wide follow): 86 compiles,
  34,400 cells, **0 diffs**.
- Reach: `RX_VM_POSS_ARMS` read off each armed artifact. A1 (0x2) decided
  on `a+\bé`, `x+\b[éa]`, `[a-c]+\b\x{100}`, `é?a+\b`, `\w+\b[éĀ]`,
  `[a-c]+\bé?x`, `é+\b`, `[à-ÿ]+\b`, `\w+\b[é]` (utf8 and utf8 -i). B (0x4)
  was needed on `(é)x+\1`, `([éa])x+\1`, `([à-ÿ]+)\s+\1`, `(é?)x+\1x`
  (utf8, ucp, -i). A0 (0x1) fired on none of these shapes, and that
  population is unprobed.

## Tests added

- `tests/possessify/possessify.rxt` tail: 12 wide-class witnesses x
  (greedy, possessive spelling) = 24 blocks, under their own header, all
  `# pcre2-only`, `encoding utf8`, `engine vm`. Expectations are libpcre2
  10.46's (generator `build/wcls/gencells.py`, scratch). Each comment
  carries that pattern's measured `RX_VM_POSS_ARMS`, and two are
  widen-direction witnesses at 0x0u: the nullable `(\x{e9}?)x+\1x`, and
  caseless `(\x{100})x+\1`, whose U+0101 fold partner is outside the byte
  tier. Harness on the file: 3537 passed / 0 failed.
- `tests/possessify/run_possessify_tests.sh` section 11 (R4SUM/R-5): this
  check compiled every corpus pattern under BYTE, ignoring its block's
  `encoding`/`flags`, so `\x{100}` refused (12 FAILs on the first
  test-possessify run). It now carries each block's `encoding`/`flags`
  after a TAB (the synthetic lines have none), which also checks the
  existing utf8/-i cells under the encoding they were written for.
- Pins moved, in `tests/rxtsource/run_rxtsource_tests.sh` (readers found
  by running the suite): CENSUS_BLOCKS / RUNSH_BLOCKS 5392 -> 5416,
  CENSUS_LINES / RUNSH_LINES 51505 -> 51960, C3_SKIP 34184 -> 34639,
  C3_SKIP_PCRE2ONLY 17108 -> 17563. Re-ran standalone, 0 failed.
- No sabotage row added or re-pinned. No miscompile was found, and none of
  the edited lines is a mech anchor (grep of every sabotage naming
  possessify.c).
- `tests/possessify/CLAUDE.md` updated.

## Light checks (this lane, Linux dev box)

- `make strict`: clean.
- `python3 tests/codegen/wclass_census.py src`: `[5b]` PASS (was FAIL x4).
- `make test-cpset-structure` (run_cpset_structure.sh +
  run_wclass_census.sh + run_clspack.sh): 59 passed / 0 failed, rc 0.
  Standalone: `run_wclass_census.sh` 17/0, `run_cpset_structure.sh` 28/0.
- `bash tests/rxtsource/run_rxtsource_tests.sh` after re-pin: 0 failed.
- `make test-possessify` (run_possdiff.sh, which has the utf8/ucp/utf8i
  arms files in its default mode, + run_possessify_tests.sh): rc 0,
  2/2 scripts. possdiff compared 623,938 cells, reach 15/15, manifest
  35/35. run_possessify_tests.sh read 44 passed / 0 failed, including
  R4SUM/R-5 over 205 patterns x 3 compiles.
- `bash tests/harness/run.sh tests/possessify/possessify.rxt`: 3537 / 0.

## STATE AT HANDOFF

Committed on `lane/posswcls`. OWED: the full `make -k -j16 -Otarget test`,
armed detached behind `worktrees/posswcls/.lift`. Its script is
`build/wcls/chain.sh`, its log `build/wcls/maketest.log`, and the
completion line is `== chain COMPLETE ... reds=N`. `build/wcls/verdict.txt`
holds make's `*** [test-X]` lines (empty = green). The chain restores
`docs/dev/artifact_size_log.tsv` and then touches `build/wcls/DONE`. A
separate `run_possdiff.sh` step is not in the chain: its utf modes run
inside `test-possessify` within `make test`.

## Addendum: startset manifests re-pinned (lane possmani, 2026-10-07)

posswcls's full `make test` (`build/wcls/maketest.log`) had ONE red, `test-startset`,
the same shape posstri item 4 fixed one step earlier. Read from the log: only the two
`[vm-movers]` checks failed ("24 not in the manifest, 0 manifest rows not movers", auto
and forced); the other 20+ checks in the section passed, including `[vm-iff]`,
`[vm-route]`, `[vm-deny]`, `[vm-table]` and the every-startpos differential. All 24
unlisted movers are `tests/possessify/possessify.rxt:4033-4681`, lines `git blame`
attributes to f87a3d73 (posswcls's wide-class cells).

Regenerated with the manifests' own generator (`docs/design/startset/s1/census_s1.py`, its
`-fno-start-set` arm, BENCH pointed read-only at pcrec-bench) on the 5afc7e51 build and
diffed against the committed manifests with `LC_ALL=C`:

| manifest | added | gone | changed hex |
|---|---|---|---|
| s2_vm_auto | 24 | 0 | 0 |
| s2_vm_forced | 24 | 0 | 0 |
| s3_dfa | 0 | 0 | 0 |

The 24 rows were appended to the two VM manifests under a dated comment line (e39c74b3).
Nothing else differed, so nothing else was touched.

Validation: `make -k -j16 -Otarget test-startset` on the possmani tree reads no
`*** [... test-` line; `[vm-movers]` now PASSes (auto 386 rows, forced 3168 rows,
0 off-diagonal). Log: `worktrees/possmani/build/mani/startset.log`.

OWED: the full `make test`, armed detached (waits for `worktrees/possmani/.lift`).
Verdict: `worktrees/possmani/build/verdict.txt` once `build/DONE` exists (empty verdict
= green); log `build/mt.log`.
