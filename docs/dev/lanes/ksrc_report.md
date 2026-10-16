# ksrc report: [KNOW-SRC] K0 + K1 built (2026-10-16, lane ksrc, opus)

Branch `lane/ksrc`, cut from main `61c92ed22`. Design: `docs/design/measure_sets.md`
rev 3 §9.2, §9.3, §9.5, §9.7. No abi event and no spec hunk: no emitted byte, flag,
stamp or diagnostic moved (the gates below), and the two debug macros and the
`emit_sweep.py` mode are developer surfaces. K2 and K3 are NOT built (a fresh lane,
after review); §9.9 is untouched.

## What was built

**K0, the parts** (`src/core/ksrc.c` + `ksrc.h`, libc + `<dirent.h>`/`<sys/stat.h>` +
`core/ksrc.h` only):

- `pcrec_ks_name_ok` / `pcrec_ks_classify` (name-only, name-else-file, file-only);
- `pcrec_ks_resolve`, the ONE stop loop (own stop = S1 or the source directory,
  `-I` dirs, the store), driven by the row's columns; `pcrec_ks_stops_text`,
  `pcrec_ks_refuse_unknown`, `pcrec_ks_dir_has_exact`;
- `pcrec_ks_pick`, D93 fill-only returned as data;
- `pcrec_ks_digest` / `pcrec_ks_fnv1a`: literal domain bytes with an explicit
  length (`KS_DOMAIN(lit)` = the literal's `sizeof`, NUL included), sub-key,
  then the role's fold.

Every exported name carries `pcrec_` (C15's link check requires it of libpcrec; the
design's `ks_*` spellings are the same functions). Parts 1 (the section-TSV reader),
4 (`ksgen`) and 6 (the views) are not built: each lands with its first reader (M0,
K2, K3). A `KsKind` column joins in the step that reads it, so the struct carries
the §9.5 columns the resolver and the listing will read, not the `parse`/`write_*`
function columns.

**The rows and the table.** `src/parse/ks_analysis.c` (`pcrec_ks_analysis`, with
its file probe: the size cap, the `.rxt` parse, the bundle count) and
`src/parse/ks_lib.c` (`pcrec_ks_lib`, resolve-only). `src/core/ksrc_kinds.c` holds
`pcrec_ks_kinds[]` + `pcrec_ks_kind()`. It has no reader yet: the CLI reads the
analysis row directly, and the table's first reader is K3's harness driver or
[LIST-TABLES].

**Two divergences became columns beyond §9.5's list**, both needed for zero movers:

- `join`: the analysis row reports `DIR/<name>.rxt` with an unconditional `/`
  (`-I d/` prints `d//x.rxt`), while `lib` uses `join_path`'s clean join;
- the nouns (`noun`/`nouns`/`item_noun`) that the shared refusals and the note say.

A third divergence is listed and NOT unified. The `lib` refusal's stop list
(`lib_chain_text`: "the source's own directory, 'd1' ...") is worded differently
from the analysis one ("the compiling file, -I d1, ..., the built-in store"). It
stays in `rxt_source.c`. This is F12's sibling: a caller-visible change if it is
ever unified.

**K0, the census** (`scripts/emit_sweep.py --data KIND OLD NEW`):

- **analysis**: one `-DPCREC_KS_TRACE` `--bin`, `-I DIR --analysis NAME` per version.
- **limits**: `NAME=VALUE`, two `-D` builds of `--ref`. The per-compile `--max-…`
  shortcut is not built: every limit has the `-D` route, and D77 applies.
- **Streams**: 1/2 (+ their stderr) at `--bases`, and 4. The `_FINDINGS` lines are
  stripped before comparing.
- **Output**: a movers TSV. `--expect-movers` checks it against a hand-made list.
- **Attribution** is the LOOKUP TRACE (`-DPCREC_KS_TRACE`; findings.h). Records
  look like `KSTRACE analysis byte-rate <reader> <bundle>`, the reader being the
  caller's `__func__` through two macros, so no call site was edited, plus a
  per-attempt `resolve` marker. Every analysis artifact's FINAL-attempt trace must
  equal its stamp's (query, bundle) items. The final attempt is the one that
  matters because of F-5: `(\p{Xwd})x -e utf8 -fno-req-byte` asks on attempt 0 and
  stamps `""`, and the trace shows exactly that.

**K1, the rewiring**:

- `rxt_find.c`: `find_bundle` = `pcrec_ks_resolve` + building the link from the hit
  (the chain, `#include_next`, the cycle and depth refusals and the terminal stay).
- `rxt_source.c`: both `lib` searches (the existence loop and `lib_resolve`) go
  through one `lib_find` = `pcrec_ks_resolve` under the lib row.
- `cli/main.c`: the fill-only decision is `pcrec_ks_pick` (the note stays in the
  CLI), and the three name/classification sites are `pcrec_ks_classify` on the
  analysis row's `flag_classify`/`list_classify`.
- `findings.c`: the two digests are `KsDigest` ROLES (`pcrec_find_rate_role`,
  `pcrec_find_rows_role`) behind `pcrec_ks_digest`; `pcrec_find_name_ok` wraps
  `pcrec_ks_name_ok`.
- **Both-ways**: under `-DPCREC_KSRC_BOTHWAYS` the pre-K1 code is kept verbatim
  (`old_find_bundle`, `old_probe_dir`, `old_dir_has_exact`, `old_stops_text`,
  `old_lib_find`). Every lookup is made both ways, and a disagreement aborts with a
  named internal error. K2 deletes the old copies.

## The edit set and the derived re-aim map

- Edit set: `docs/design/measure_sets/k1_edit_set.tsv` (10 `def`s, 8 `line`s).
- Map: `docs/design/measure_sets/k1_anchors.tsv`, derived by
  `docs/design/start_table/sabotage_anchors.py` with `--step K1=61c92ed22..<K1 head>`
  (the anchor tool learned the `K1`/`K2` labels). The tool sources each row with
  bash, so both quote styles of `SAB_FILE=` are read.

The map has three K1 rows:

| row | class | why | action |
|---|---|---|---|
| S313 | RE-AIM | its anchor `ts.opt.analysis = t->analysis;` was rewritten | re-aimed into `pcrec_ks_pick` (`if (file_value) {` -> `&& !flag_value`), `SAB_FILE=src/core/ksrc.c`, same detector (findings §6 #12) |
| S309 | RE-RUN | `K1:reach(link_from_source)`: the new `find_bundle` calls it | re-run, anchor unchanged |
| S255 | RE-RUN | `K1:reach(pcrec_arena_alloc)`: `find_alloc`/`lib_alloc` call it | re-run, anchor unchanged |

None of the 15 `findings.c` rows that §9.7 counts anchors in a definition K1 edits
(the digests' bodies became folds, and no row anchored there). S310 and S315 sit in
`pcrec_find_chain_build`, which K1 does not touch. **Readers outside tests/mech, by
grep:** none moved. `tests/registry/limits_check.sh:365`'s
`PCREC_FIND_NTBL`/`NBUNDLES` reader stays, because the store table did not move
(that is K2's).

## Sabotage rows (new ids from S1049-S1068)

| id | plant | detector |
|---|---|---|
| S963 | the census's analysis attribution written empty (`emit_sweep.py`) | findings §13 (UNATTRIBUTED) |
| S986 | `pcrec_ks_digest` drops a sub-keyed domain's NUL | findings §4/§6 (digest vs independent FNV) |
| S989 | `ksrc.c` includes `core/internal.h` | core: `tests/core/ksrc_deps_check.sh` |
| S1049 | the analysis row's `s2_mismatch` = refuse | findings §6 #7 |
| S1050 | the lib row drops its source-directory stop | rxtsource |
| S313 | (re-aimed, above) | findings §6 #12 |

Single-row mech verdicts: see "Validation".

## New checks

- **findings §13**: builds a trace binary of the tree, runs the analysis census on
  `tests/findings/data_census/`, and requires the hand list. The control is a list
  missing one mover, which must FAIL by name.
- **core `ksrc_deps_check.sh`** (S989's detector):
  - (a) a scan of the include lines, with a population floor and a planted-include
    control;
  - (b) `ksrc.c` compiled alone with `-Isrc` (no `-Ilib`), and `nm -u` must show
    no `pcrec_` names.

  `pcrec-measure`'s `nm -u` half joins at M3.
- **`tests/findings/ksrc_zero_mover.sh OLD NEW`** (K1/K2's instrument, not in
  `make`): the resolution surfaces compared byte for byte.

## Validation (in-lane; -j4, `taskset -c 0-7`, TMPDIR in the worktree)

| check | result |
|---|---|
| `make -j16`, `make strict` | rc 0 / rc 0 (and the `-DPCREC_KSRC_BOTHWAYS` and `-DPCREC_KS_TRACE` TUs compile clean under `-Wall -Wextra -Wshadow -Werror`) |
| `make test-findings` | rc 0 (§13 new: 8 movers reproduced, control FAILs by name) |
| `make test-rxtsource` | rc 0 after one fix: the first run went red (census 284 vs 282) because the K0 fixture bundles were committed `.rxt` files and joined the corpus. They are now written per run by `tests/findings/data_census/fx_bundles.py`; census unmoved at 282/5790/70496 |
| `make test-registry` | rc 0 (limits_check: no new numeric `#define`/valued enum) |
| `make test-codegen` | rc 0 (SABANCHOR resolves every new/re-aimed row) |
| `make test-core` | rc 0 (`ksrc_deps_check` 3/3; its control fires) |
| both-ways debug build over `run_findings_tests.sh` and `run_rxtsource_tests.sh` | 88/0 and 298/0, zero `K1 both-ways` aborts |
| `tests/findings/ksrc_zero_mover.sh` (branch point 61c92ed22 vs K1 head) | 655 cases, 0 differ; failing direction: a wrapper rewording one note word → 19 DIFF |
| digest pin | `RX_FINDINGS "byte-rate=default:1822fb973b95a4da"` unchanged; findings §4 (library digest = independent FNV) green; `--list-analyses` rows_digest byte-identical in the zero-mover witness |
| data census, limits fixture (`PCREC_MAX_AUTO_DFA_ELEMS` 30000000 → 3000, two `-D` builds of HEAD) | hand list (2 movers) reproduced, 0 problems |
| plan lint | 0 violations (the row stays `not-started` in Backlog: PL13 requires `started` rows in Active, the manager's move) |

**Single-row mech** (PROCS=1 JOBS=4, `build/v/mech.sh`, launched detached at K1 head
c136b70a2; later commits on the lane are docs-only): S313, S963, S986, S989, S1049,
S1050 and the RE-RUN rows S309, S255. Verdicts land in `build/v/mech/summary` (one
line per row with its `== mech run COMPLETE` trailer) and `build/v/mech/<id>.log`;
`DONE` closes the file. **STATUS AT HANDBACK: see the handback message** (the lane
records the summary lines it saw before ending; anything not listed there is OWED).

## The armed HEAVY chain (OWED, gated on `.lift`)

ONE waiter, `build/land/waiter.sh` (PID in `build/land/waiter.pid`), polls
`worktrees/ksrc/.lift` every 60 s and then runs `build/land/chain.sh` once:

0. `make -j8` and the both-ways build (`build/both`);
1. `emit_sweep.py --ref 61c92ed22 --bin build/pcrec` (every stream, self-check first);
2. `--arms start` (byte and utf8 bases);
3. `--variant all --tree-rev <K1 head>` (all five limit variants, both bases);
4. the both-ways debug build over the whole corpus (`--bin build/both/pcrec`): any
   K1 disagreement aborts a compile and reads as a refusal mover;
5. `make test` through `scripts/perfrun --label ksrc`;
6. single-row mech S432 (the reach-derived RE-RUN the final map added).

Log `build/v/chain.log` (rc per step on its own line, `make test red sections:`
grepped with the `-E` form), completion file `build/v/DONE`. The gate is ZERO MOVERS
on steps 1-4 (rc 0 each) and a green `make test`.

## Deviations and open items

- **Parts 1, 4 and 6 are not built** (section-TSV reader, `ksgen`, the views). Each
  lands with its first reader (M0, K2, K3). The `KsKind` struct carries only the
  columns K1 reads, plus §9.5's declarative columns.
- **Exported names carry `pcrec_`** (C15).
- **Pointers in the row**: `KsKind.item`/`.stamp` are pointers to the role objects
  findings.c defines, not by-value structs. This keeps the parts table-free and
  findings.c the roles' home.
- **The `lib` row's `suffix` is not appended.** A `lib "path"` request is a PATH: its
  entry is the reference as written. The column is the listing's spelling only.
- **The trace dedupes consecutive repeats of one reader**, via a trace-build-only
  `PcrecFindRec.trace_last`. Without it one compile wrote thousands of identical
  `pcrec_prefix_ksets` records.
- **The census's cross-check reads the FINAL attempt** (the stamp's own scope until
  D167 add. 3's union lands). When that lands, the check changes to the union of
  attempts in the same commit.
- **Not unified, by design**: the `lib` refusal's stop text (`lib_chain_text`).
- **For K2**: delete the `#ifdef PCREC_KSRC_BOTHWAYS` copies. Re-run
  `tests/findings/ksrc_zero_mover.sh` against this lane's head. Re-derive the map with
  `--step K2=<K1 head>..<K2 head>`. Note that `limits_check.sh:365` moves only if the
  store table moves.
- **sabotage_anchors.py exits 2 on five UNRESOLVED rows unrelated to K1** (S176,
  S571, S640, S897, S906, also unresolved on main). The output is complete regardless.
