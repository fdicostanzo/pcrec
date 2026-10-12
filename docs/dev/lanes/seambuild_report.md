# seambuild — [LOSS-REVIEW] candidate 1: the seam helpers stop being exported

Lane seambuild, opus, 2026-10-11, branch `lane/seambuild` from main `6d80ba45`.
Ruling: Frank 2026-10-11, "those helpers shouldn't be exported. Easy win". The
manager chose to re-home the readers rather than keep an exported wrapper
(r2 panel row C1, Q3). Evidence for the gain:
`docs/dev/optloop/lossreview/twintime/summary.md` (bak-1 +13.5%, bak-2 +9.7%,
mod-j-uc +5.6% on Zen 4; the PLT is 80-87% of the gain).

ONE abi event, **75 -> 76**.

## 1. What changed

**The entries.** In both backends (`src/enc/enc_byte.c`, `src/enc/enc_utf8.c`)
the rows `PCREC_ENCE_SPAN`, `PCREC_ENCE_SPAN_CASELESS`,
`PCREC_ENCE_SPAN_CASELESS_UCP` (byte only) and `PCREC_ENCE_BACK_STEP` are now
`inline_def`, the column `$_decode` already used. Each row now has:

- an empty `decls`;
- its old declaration doc kept as the entry's CONTRACT doc (`decls_doc`), with
  "exports this same entry" reworded and a "NOT A CALLER ENTRY: `static
  inline`, declared nowhere" paragraph added;
- a definition that starts `static inline`, with its parameter lines
  re-wrapped.

`$_BACK_STEP_NONE` moves from the declarations to the `defs` text, just above
`$_back_step`. In utf8, the `DECODE` row moved ahead of the span rows: the
inline half is emitted in table order, and the caseless compare (now inline)
calls `$_decode`.

**The seam emitter** (`src/enc/enc.c`, `enc.h`):

- `pcrec_enc_emit_decls` skips `inline_def` rows.
- The inline half of `enc_emit_defs` writes an inline row's `decls_doc`
  beside its definition, through the comment gate as before.
- `pcrec_enc_emit_inline_defs` takes the rendered N7 sites, the same way
  `pcrec_enc_emit_defs` does.

The comment on the `inline_def` column states the new meaning of `decls_doc`
and the table-order rule.

**The gen layer** (`src/gen/emit_dfa.c`, `emit_vm.c`, `src/core/internal.h`):

- The site-render loop is factored out of `emit_residual_defs` into
  `residual_sites(cx, enc, inline_half, &ns)`. It renders the N7 loop through
  the kit for the entries of ONE half.
- A new `pcrec_emit_residual_inline(cx, sb)` renders the inline half's sites
  and calls `pcrec_enc_emit_inline_defs`. Both engines' existing inline
  placements call it. The VM's placement already sat ahead of every engine
  body, beside the wide-class matchers.
- The kit's N7 loop is rendered unchanged inside the entry. It is now
  rendered at the inline placement instead of the epilogue (§5).

**The emitted text** (default flags, diffed at the same `-o` against a build
of main):

- the `.h`/prologue loses the declaration(s) and `rx_BACK_STEP_NONE`;
- the definitions move from the epilogue to just ahead of the VM body, as
  `static inline`;
- the abi digits change.

Nothing else moves: not the program, not any stamp, and not
`RX_VM_PROGRAM_BYTES` or the entry-shape knee. `nm` on `-O2 -fPIC` objects
shows no `rx_span_match*`/`rx_back_step` symbol at all, in byte, utf8 and
`--ucp`.

**Spec** (`docs/spec/match_api.md`): §3¶2 is rewritten. The span compares and
`<prefix>_back_step` are `static inline`, defined ahead of the engine body,
declared nowhere and not exported. `<prefix>_var_valid` is still exported. None
of them is a caller entry. The abi readers are updated (see §3).
`docs/spec/vars.md` §7 says only that the residual names the entry, so it
stays true. No other spec sentence names the three entries.

## 2. The mover census

`docs/dev/lanes/seambuild_movers.py` (committed) compiles every distinct
corpus pattern (emit_sweep's enumeration, 4,542) with a main build and the
lane build under `--features all`, on four arms. It normalizes the abi digit
on abi lines only.

**Rule:** an artifact may differ ONLY if main's text defines one of the three
entries as an exported function and the lane's defines it `static inline` and
not exported.

| arm | identical | movers | both refuse | outside the rule |
|---|---:|---:|---:|---:|
| byte default | 3,473 | 691 | 378 | 0 |
| byte `--engine=vm` | 3,474 | 691 | 377 | 0 |
| utf8 default | 3,452 | 723 | 367 | 0 |
| utf8 `--engine=vm` | 3,454 | 723 | 365 | 0 |

Expected population: every artifact whose mask carries `SPAN`,
`SPAN_CASELESS`, `SPAN_CASELESS_UCP` or `BACK_STEP` (backreference-,
variable- and lookbehind-bearing). The census found exactly that set:

- 0 carriers stayed identical;
- 0 movers carried no entry;
- 0 refusals moved.

The brief asked for `scripts/emit_sweep.py` here. It has no abi
normalization, so it would report every artifact as a mover, and the census
script above runs the population check it cannot. The streams emit_sweep adds
(`--emit-ir`, composition, dumps, facts) do not contain these entries.
emit_sweep runs in the slot's chain (§6); its expected reading is
all-movers on the `.c` streams by the abi digit, and 0 movers on the dumps.

## 3. Readers found by grep

**The abi number** (`git grep` for `abi ... 75`; historical `(abi 75)`
annotations left as they are):

- `src/gen/emit_dfa.c:54`, `PCREC_ARTIFACT_ABI` 76;
- `docs/spec/match_api.md`: the guard block (×3 lines), the `abi` row of the
  `rx_info` table and §6¶17's sentence;
- `tests/codegen/run_codegen_tests.sh`: `ABI_EXPECT` 76 and its ledger
  message (75->76 appended);
- `tests/mech/sabotages/S693_abi_not_bumped.sh` (BEFORE 76 / AFTER 75);
- `docs/dev/history/abi_changelog.md`: new top entry, the old one becomes
  "was 75";
- the recursion-identity (B) FILEPIN, self-pinned to `337f9a6e`, this lane's
  only src commit.

**The byte counts that move with the scaffolding** (the second reader class):

- `tests/codegen/manifests/m5_stage1_stamps.tsv`: two rows,
  `(\w+)\s+\1` 28,966 -> 28,897 and `(?<=foo)bar` 30,325 -> 30,296. Both were
  diffed and explained in a re-record note in `run_cpset_structure.sh`. The
  other ten rows do not move, because the abi digits keep their width.
- `tests/resource`'s rung pins: its witnesses carry no seam entry. To be
  confirmed by the pre-chain run (§6).

**The three symbols** (`git grep span_match\|back_step\|BACK_STEP_NONE` over
the whole tree):

- `tests/backrefs/fold_agreement_check.c`, `fold_agreement_utf8_check.c` and
  `fold_agreement_ucp_check.c` are RE-HOMED. They `#include "gen.c"`, the
  artifact's own translation unit, and call the shipped `static inline`
  definition directly. `run_backref_diff.sh` §9/§9b/§9c compiles them without
  linking gen.c, and the population guards read the `static inline`
  definition in gen.c instead of the `.h` declaration. The same 65,536-pair
  and relation sweeps run; brefdiff reads 13/0.
- `tests/codegen/run_codegen_tests.sh` [M5-SEAM]: the declared-set check
  `residual_names` read only exported declarations, so all 15 seam fixtures
  went red (30 FAIL). It is split in two:
  - (1) exported entries against the fixture's exported half;
  - (1b) a new `inline_entries` reading the `static inline` heads in both
    `.c` forms against the inline half.

  The per-site call counts (`calls_in_bodies`) needed no change: the head
  detection reads the `static inline ... rx_span_match(` heads.
- `tests/codegen/run_encoding_checks.sh` DD12a(i): `SIG_RE` lacked a
  `static inline ptrdiff_t` head, so the span regions were "never excised"
  and the K50 list and strict pairs drifted (4 FAIL). Adding the head made
  it 11/0.
- `tests/memfn/site_manifest.tsv` row N7: the emitter became
  `residual_sites`, the function that now renders the loop for both halves.
  `emit_residual_defs` and `pcrec_emit_residual_inline` are added as
  companions and the text is updated. C17's floor does not move.
- Sabotage anchors (`scripts/m6read_check_sab_anchors.py`, all 698 resolve):
  - re-anchored S394 (the utf8 caseless row's `inline_def` column, false ->
    true; the plant still clears only `requires`);
  - re-anchored S673 (the byte exact compare's re-wrapped last parameter line;
    its `SAB_REACH_POP` reads the N7 row's new emitter);
  - re-aimed S693.

  Every other row naming the symbols still resolves. Their re-runs are in the
  chain (§6).
- No reader: the kit's N7 renderer (`memfn/src/mismatch.c`), `PcrecEncSite`
  and the M7 pins (`tests/memfn/pins/n7_target/`, the loop text only).
  Placement moves (§5), the text does not. `test-memfn-*` is in the pre-chain
  run.
- Prose only, not changed (design records, reviews, studies, journals):
  `docs/design/*`, `docs/dev/optloop/*`, `memfn/docs/*`, `studies/*`.
  `src/core/fold.c:9`'s comment is still true.

## 4. Sabotage S825

S825 (`tests/mech/sabotages/S825_span_match_exported.sh`) is the first free id
after the kit's reserved S820-S824.

- **Plant:** the byte backend's `"static inline ptrdiff_t $_span_match(` loses
  `static inline`, so the exact compare is an exported, PLT-called function
  again. No answer moves.
- **Reach:** `SAB_REACH` compiles the detectors' own fixture `(a|b)\1` on the
  clean tree and requires the exact line the plant edits. `SAB_REACH_POP`
  requires both detectors' fixture rows (`residbref1`, `expbref`).
- **Detectors** (arm `codegen`):
  - [M5-SEAM] (1): the `_sc.c` exports `rx_span_match`;
  - [M5-SEAM] (1b): the `.c` forms no longer define it `static inline`;
  - [LOSS-REVIEW c1]: `nm` on the `expbref`/`expvar` `-O2 -fPIC` objects
    shows `rx_span_match` global.

**Measured:**

- Solo mech at `fab229fd`: `reach:ok(1/1)`, both pops 1, `codegen:22fail/328pass`,
  DETECTED, `unexpected: 0`.
- A hand plant at `2124a247` showed the nm arm firing itself, on `(a|b)\1`
  and `^${v}$`: 21 failures, where the nm arm had first been masked by its own
  reach check.

The nm arm's reach check now reads the definition whatever its linkage. At
first it required `static inline` and so returned early on the plant: the
S806/S807 lesson, a witness that does not reach its plant. The chain re-runs
S825 solo at the tip.

## 5. Placement

The inline entries are emitted at `emit_vm.c`'s existing inline-defs site,
ahead of the wide-class matchers and the prefilter. The DFA's placement is
ahead of `pcrec_emit_dfa_engine`; no DFA body calls these entries. The kit's
N7 loop is rendered there too, by the same `pcrec_memfn_emit` door through the
attempt's art, so its trace order and `MEMFN_LIBC` inventory see the same
sites. That inventory is a finishing pass over the whole artifact. The lane's
light run of `test-memfn-stamps`/`-manifest`/`-forms` is §6, and S513/S517 run
in the chain.

## 6. Validation

**Light, before the chain** (Linux dev box; `.lift` was present at start):

| check | result |
|---|---|
| `make -j16` | clean, no warnings |
| `bash tests/backrefs/run_backref_diff.sh` | 13/0 (§9/§9b/§9c fold agreement re-homed) |
| `bash tests/codegen/run_codegen_tests.sh` | 331/0 |
| `make test-codegen` (16 scripts, first run, before the M5-SEAM split) | only run_codegen_tests red (30, the split); the other 15 scripts 0 failed |
| `bash tests/codegen/run_encoding_checks.sh` | 11/0 |
| `bash tests/codegen/run_cpset_structure.sh` | 29/0 after the two-row re-record |
| mover census (§2) | 0 outside the rule, 4 arms |
| sabotage anchors | 698 rows resolve |
| mech S825 solo | DETECTED, `codegen:22fail/328pass` |
| `make test-resource` (pre-chain) | rc 0, 0 failed: the rung pins do not move |
| `make test-registry` (pre-chain) | rc 0 |
| `make test-rxtsource` (pre-chain) | rc 0 |
| `make test-recursion-identity`, `test-memfn-manifest/-stamps/-forms` (pre-chain) | running at hand-off; `build/land/pre_summary.log`, copied into `chain.log` |

**The chain** is `build/land/chain.sh`, launched detached as the lane's last
act. It writes one verdict line per stage in `build/land/chain.log`:

- `make`, `make strict`;
- `make test` through `scripts/perfrun` (`build/land/test.log`; verdict
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`);
- `make test-axes` (`axes.log`);
- the pre-chain's `make test-recursion-identity` and `test-memfn-*` verdicts
  (`pre_test-<target>.log`), copied into `chain.log` (the chain waits for the
  pre-chain to finish, one heavy suite at a time);
- solo mech rows S825 S693 S394 S673 plus the re-run list S106 S109 S116 S133
  S134 S271 S273 S669 S-U5 S-U9 S10 S390 S391 S442 S591 S229 S-U6 S233 S340
  S409 S410 S412 S513 S517 (`mech_<row>.log`).

The completion line is `chain DONE`. These verdicts are OWED at hand-off.

**Scope note.** The lane's first suite runs and the first S825 mech row used
the scripts' default `/tmp` scratch, which each cleaned up. From the census on,
everything runs with `TMPDIR` and `MECH_SCRATCH` under the worktree's `build/`.

## 7. Notes for the manager

- An inline entry's contract doc now sits in the `.c` beside its definition.
  It is emitted only under `-fcomments`, like every residual doc. A split
  artifact's `.h` no longer names the three entries at all.
- `<prefix>_var_valid` stays exported. It is called once per call from the
  entry wrapper, never per attempt, so the ruling's reason does not reach it.
  Making it inline is a separate decision.
