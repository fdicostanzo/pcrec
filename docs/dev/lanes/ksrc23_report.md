# ksrc23 report: [KNOW-SRC] K2 + K3 built (2026-10-17, lane ksrc23, opus)

Branch `lane/ksrc23`, cut from main `343605a57` (K0/K1 merged with int3, E-1
and RP/union merged). Design: `docs/design/measure_sets.md` rev 3 §9.2, §9.5,
§9.6, §9.7. Commits: K2 `f227cca55`; K3 `66c51d710`; `f90a6a036` (report
draft, K3 map, measured sabotage figures); `00cdb5f41` (the view refusal
names the kind when it has no listing flag, which no CLI path reaches: a
guard, zero movers by construction); then this report (tip in the
handback). The zero-mover runs in §3 used the frozen K3 binary
`66c51d710`. No abi event: no emitted byte moved (§3). §9.9's
format question is untouched.

## 1. What changed, per step

### K2 (`f227cca55`)

- **The old functions are deleted.** K1's `-DPCREC_KSRC_BOTHWAYS` copies of
  the pre-K1 code (`rxt_find.c`: `stop_store`, `old_dir_has_exact`,
  `old_probe_dir`, `old_stops_text`, `old_find_bundle`, `find_bothways`;
  `rxt_source.c`: `old_lib_find` and its check) and the wrapper
  `pcrec_find_name_ok` (findings.c/.h). Its two callers
  (`pcrec_find_chain_build`, `analysis_name_check`) call `pcrec_ks_name_ok`.
  `rxt_find.c` no longer includes `<dirent.h>`/`<sys/stat.h>`.
- **`scripts/findgen.c` becomes `scripts/ksgen.c`** (`git mv`):
  `ksgen KIND OUT FILE...`. The kind is looked up in the kinds table
  (`pcrec_ks_kind`, the table's FIRST reader), which also supplies the file
  suffix. One arm per kind with a store, chosen from a first-match table
  `gen_arms[]` (`analysis` = findgen's body, split out of `main`).
- **`gen-findings` is the pattern rule.** One static-pattern rule
  `$(KS_STORES:%=gen-%): gen-%:` with the store's row as variables
  (`KS_KIND_findings := analysis`, `KS_SRCS_`, `KS_TEXT_`, `KS_TABLE_`).
  `gen-tables` calls `$(KS_STORES:%=gen-%)`. `make strict`/`make lint` list
  `scripts/ksgen.c`.
- Docs: Makefile comments, `scripts/`, `src/core/`, `src/parse/`,
  `src/findings/`, `analyze/` CLAUDE.md files, findings.c/.h comments.

### K3 (`66c51d710`)

- **The parts (part 6)** `src/core/ksrc.c`/`.h`: `KsOut` (the caller's
  writer); three new row columns, `write_canonical`, `write_decoded` (both
  `int (*)(const KsOut *, const void *doc, KsErr *)`) and `derived_sections`;
  `pcrec_ks_view_write` (a view NAME to its writer column, a first-match
  table of column offsets; an unknown view or a missing writer refuses);
  `pcrec_ks_derived_section` (a file's first column-1 `#section NAME` with
  NAME in the row's list). `ks_probe_dir` asks it before the kind's probe, so
  a listing fed back through `-I` refuses naming the file, the section and
  `--view=canonical`. Still libc + POSIX + `core/ksrc.h` only (adds
  `<stddef.h>`); `ksrc_deps_check.sh` green.
- **The analysis row's views** (`src/parse/ks_analysis.c`, item handle
  `PcrecKsAnalysisItem` = the parse + the bundle name, `internal.h`):
  - CANONICAL: one fixed comment line, `analysis NAME`, its `include <x>` and
    `description`, then the data blocks in FILE order; each block's lines in
    `rxt_format.md` §1.10's table order, rows ascending in the format's
    spelling, provenance fields in §1.9's order. A prose value
    (`description`, `license-note`, `adaptation`, `attribution`) is written
    as loaded (trailing whitespace kept) and in block-scalar form when it
    holds a newline or is the single byte `|`; every other value trimmed.
  - DECODED: `#section decoded` (`scope`, `field`, `value`; one row per field
    of the loaded document) and `#section item` (`rows`, the `rows_digest` of
    the same parse).
  - `derived_sections`: `chain`, `resolution`, `declarations`, `targets`,
    `decoded`, `item`.
- `rxt_source.c` `close_section_frame`: a BUNDLE frame keeps its
  `description` on the `analysis` row (the views need it; nothing kept it
  before). `--list-source` prints a row's `description` for pattern rows only,
  so no dump moves (ksrc_zero_mover and emit_sweep's dumps stream agree).
- `src/dump/findings_dump.c` `pcrec_find_list_view`; `cli/main.c` `--view=V`
  / `--view V` (`CliState.list_view`), a modifier of `--list-analysis NAME`,
  refused with a FILE value or any other mode. `scripts/ksgen.c` refuses a
  store text carrying a derived section (same part).
- **analyze/** (the deliberately independent twin): `parse_bundle` now reads
  one whole author-written bundle (column-1 comments, blank and
  whitespace-only lines, `include`, `description`, `question`/`reader`/
  `analyzer`/`serves`, all eleven provenance fields, block-scalar prose, the
  blocks' file order), written from `rxt_format.md` §1.4/§1.9/§1.10; on its
  own emitted subset it reads what it always did (the analyzer suites:
  `run_analyzer_tests.py` 37/0, `run_analyzer_pinned.py` 11/0). `dump_doc` +
  `--dump-doc FILE` print the document in the decoded view's
  `#section decoded` shape. Still zero-dependency.
- **`tests/knowledge/`** (new; `make test-knowledge`, in `TEST_SECTIONS`, CI
  shard 1 with an ESTIMATED weight; mech arm `knowledge`):
  `run_knowledge_tests.sh` and `kfixtures.py` (§4).
- Spec hunks (D80): `findings.md` §7's failure table (the derived-section
  row), new §8.4 (`--view=canonical`) and §8.5 (`--view=decoded`), contents
  regenerated; `cli.md` §2.9¶2 (`--view`).
- The derived re-aim maps: `docs/design/measure_sets/k2_edit_set.tsv`,
  `k2_anchors.tsv`/`.summary` (committed with K3, a WIP slip), and
  `k3_edit_set.tsv`, `k3_anchors.tsv`/`.summary` (this report's commit).
- CLAUDE.md: `src/core`, `src/parse`, `src/dump`, `cli`, `analyze`, `tests`,
  `tests/knowledge` (new), `tests/mech`, `docs/design/measure_sets`,
  `docs/dev/lanes`.

## 2. The gen-tables diff

`make gen-tables` on the K2 tree (before committing the regenerated file)
changed exactly ONE line of `src/core/findings_table.inc`, its first:

```
-/* GENERATED by scripts/findgen.c from src/findings/<name>.rxt:
+/* GENERATED by scripts/ksgen.c analysis from src/findings/<name>.rxt:
```

The body from line 2 on is byte-identical, and `findings.o` compiled with the
old and the new `.inc` is byte-identical (`cmp`). `findings_store.inc` and
both `third_party/*/generate.py` outputs did not move. After the K2 commit,
`make gen-tables && git diff --exit-code` is CLEAN (and again at K3).
Departure D1 below.

## 3. Zero-mover evidence

| instrument | sides | result |
|---|---|---|
| `tests/findings/ksrc_zero_mover.sh` (the resolution surfaces: stops, refusals, notes, both listings, fill-only, `lib`) | branch point `343605a57` build vs K2 head | 655 cases, 0 differ |
| same | branch point vs K3 head (frozen `build/new/pcrec`) | 655 cases, 0 differ |
| `findings.o` across the generated-comment change | old vs new `.inc` | byte-identical |
| emit_sweep data census, canonical view vs original, for `log`, `weblog` and `default` (`--data analysis OLD NEW`, a `-DPCREC_KS_TRACE` build of the K3 head, an EMPTY expected-movers list; `default` renamed `kdefault` in both copies, because the data mode refuses `-I` for the name the terminal finds by identity) | each bundle vs its own canonical view, byte and utf8 bases, streams 1/2 + stderr + 4 | **0 movers** for each of the three, 18,882 artifacts compiled per side, 0 problems (`ksrc23_evidence/census.txt`) |
| emit_sweep, E-1's G1-E1 product (`e1build_evidence/g1e1_sweep.sh`: arms default / `-fno-req-byte` / `-fno-req-byte -fno-req-run -fno-prefilter` / `--engine=vm -fno-req-byte -fno-req-run`, each at byte and utf8, × analysis cells none / `--analysis weblog` / an `-I` user bundle `mine` / `l1none` (utf8)), REF = the branch point's build, NEW = the K3 head; every stream (c-default, c-vm, emit-ir-vm, facts, emit-ir-auto ×4, stderr, composition, dumps) | 28 runs, 11-12 streams each | **0 movers, 0 asymmetric on every stream of every run** (`ksrc23_evidence/g1e1_summary.tsv`). The 20 rc-1 runs are the instrument floors E-1 recorded, identical on both sides and grepped in every log: `emit-ir-vm` reach 0 in 20 runs (`--emit-ir` refuses `--analysis` on both sides), and two `l1none` runs at stream-1 reach 1,905 / 3,246 (E-1's own figures: those compiles refuse "counts nothing via encode-latin1" on both sides) |
| emit_sweep `--data` census tool itself | `make test-findings` section 13 (the K0 fixture's hand list reproduced; its control fails by name) | green |

## 4. R1-R3 / R5 results

`make test-knowledge` at K3: **212 checks, 0 failed, ~2.3 s.** 40 items:

| set | items | policy |
|---|---|---|
| `src/findings/*.rxt` (shipped) | 3 | all must load |
| `kfixtures.py` | 3 | all must load |
| `tests/findings/adversarial/` | 11 | all must load |
| `tests/findings/witness/` | 5 | all must load |
| res_fixtures `A` | 15 (of 21; cycles, the 9-link chain, the library, the two-bundle file and `Mixed.rxt` refuse by design) | floor 15 |
| res_fixtures `B` | 3 | floor 3 |

Per item: R1 (item digest across load->list->load), R2 (canonical fixed
point), R3 (analyze/ reads original and canonical as one document), R5
(decoded = `--dump-doc` of the file; plus 1-2 resolution digests per item =
`findings_ref.py bundle-digest`). All green. Also: both derived listings fed
back are refused by the derived-section rule, no canonical view carries a
`#section`, and the three controls fail as they must (a dropped description
breaks R3; a dropped `serves` encoding leaves R1's digest unmoved and breaks
R3; two swapped decoded rows break R5). `kfixtures.py` exercises what the
shipped bundles do not: cpfreq before freq, `include`, a ragged block-scalar
description with a whitespace-only line, all eleven provenance fields, prose
with trailing spaces, a prose value that is the single byte `|`, a TAB in a
`question`, four- to six-digit code points, a two-encoding `serves` list.
R4 is exempt for this kind (the row's `r4` column), as designed.

## 5. Sabotage rows and re-aims

New rows (ids allocated in §8.5), each run SOLO through `make mech`'s
matrix at the K3 head `66c51d710`:

| row | plant | verdict |
|---|---|---|
| S961 | the canonical writer omits the bundle's `description` | DETECTED, `knowledge:14fail/198pass`, every failure R3 (R1, R2 green) |
| S962 | the resolver's derived-section refusal planted out (`if (sec && 0)`) | DETECTED, `knowledge:2fail/210pass` |
| S984 | the canonical writer keeps only the first encoding of each `when` list | DETECTED, `knowledge:32fail/180pass`, every failure R3 (R1, R2 green) |

The derived maps (`sabotage_anchors.py`, the start_table/dec_fallback
precedent; tool exit 2 on 8 rows UNRESOLVED in the PRE tree, none K2's or
K3's — K1's five plus S995, S1028, S1029):

| step | RE-AIM | RE-RUN | solo verdict |
|---|---|---|---|
| K2 (`343605a57..f227cca55`) | 0 | S309 (reach), S255 (reach), S1050 (reach) | S309 DETECTED `findings:630fail/86pass`; S255 DETECTED `resource:5fail/37pass`; S1050 DETECTED `rxtsource:2fail/295pass` (at `f227cca55`) |
| K3 (`f227cca55..66c51d710`) | 0 | S1049 (hunk), S310 (reach), S315 (reach) | S1049 DETECTED `findings:1fail/102pass`; S310 DETECTED `findings:2fail/102pass`; S315 DETECTED `findings:2fail/102pass` (at `66c51d710`) |

No reader outside `tests/mech` moved: `tests/registry/limits_check.sh`'s
`PCREC_FIND_NTBL`/`NBUNDLES` reader stays (the store table did not move).
`make test-codegen`'s SABANCHOR: all 788 rows resolve.

## 6. Spec hunks

- `docs/spec/findings.md`: §7's failure table gains the derived-section row;
  §8.4 `--list-analysis NAME --view=canonical` (3 paragraphs); §8.5
  `--view=decoded` (2 paragraphs and its section table); the contents block
  regenerated (`scripts/spec_toc.py`).
- `docs/spec/cli.md` §2.9¶2: `--view`.
- `make test-spec-history`: 145/0.

## 7. Departures (the code's facts won; none moves a byte)

- **D1. The generated table's first line changed.** §9.7's K2 gate reads
  "findings_table.inc byte-identical"; the file's own generated-by comment
  named `scripts/findgen.c`, and the generator is renamed, so line 1 now
  names `scripts/ksgen.c`. Body and object are byte-identical (§2); the gate
  as stated in the brief (`make gen-tables && git diff --exit-code` clean)
  holds. findb6's precedent (the same comment-only shape).
- **D2. The pattern rule's stem is the STORE name, not the kind's.** §9.2
  part 4 says `gen-<kind>`; §2.3 of the same note says `make gen-measures`.
  Keyed by store, `gen-findings` stays the rule's analysis instance, so every
  reader of `make gen-findings` (the embedded store's own header,
  third_party generators, docs, tests) stays true with no alias and
  `findings_store.inc` does not move.
- **D3. S961 and S984 are re-stated for the analysis kind.** §8.5 wrote S961
  for measures' `cells` section; its analysis analogue is the bundle's
  `description`. §8.5's S984 drops every `serves` line, but `serves` is
  REQUIRED in a data block (`rxt_format.md` §1.10¶5): the view would refuse
  to load and R1 would go red too, defeating the row's point; the plant
  drops the later encodings of each `when` list instead, which `rows_digest`
  does not cover. S962's plant is on the resolver's refusal (the loader
  half of "written into the canonical view, or accepted by the loader").
- **D4. The canonical writer keeps the blocks' FILE order**, not kind order:
  `rows_digest` folds the blocks in file order (`findings.md` §8.1), so a
  reorder would change the ITEM digest and fail R1. `serves` lines and
  `when` lists are written as loaded, not sorted. The document shape (both
  readers) keeps file order too.
- **D5. A sixth derived section, `item`.** The decoded view carries the ITEM
  digest (R1 needs one for `-I` items; `--list-analyses` lists the store
  only), in its own section, so the row's list is §9.5's five plus `item`.
- **D6. `--view` applies to `--list-analysis NAME` only.** With
  `list_classify = name-else-file`, a FILE value is the per-target view,
  which has no single item; it is refused rather than given a meaning. The
  canonical view resolves the whole chain as the NAME listing does, so a
  bundle whose `include` chain refuses (a cycle) has no canonical view.
- **D7. The derived-section refusal is at the `-I` stop (and in ksgen)**,
  not at S1 (the compiling file is a pattern source, not an item file) nor
  on `analysis_source`.
- **D8. The view columns take a `KsErr *`** (the design's signature has
  none), so a writer can refuse.
- **D9. `tests/knowledge/ksdump` (§9.2 part 6's harness driver) is not
  built**: no harness-surface kind exists yet (picks and evaluator-params
  are unbuilt; D77). The analysis kind has a CLI surface.
- **D10. analyze/'s reader now accepts inputs it used to refuse** (a file
  that starts with a comment, a bundle with `include`/`description`, a
  block-scalar prose field). Every input it accepted before reads the same.
- **D11. A bundle's `description` is kept on its `analysis` row** (a new use
  of `RxtRow.description`); before K3 the parser validated it and kept it
  nowhere.

## 8. Validation run in-lane (-j4, TMPDIR in the worktree)

| check | result |
|---|---|
| `make -j4`, `make strict` | rc 0 / rc 0 |
| `make gen-tables && git diff --exit-code` | clean at K2 and K3 |
| `make test-knowledge` | 212/0 |
| `make test-findings` | rc 0 (104/0, analyzer 37/0, pinned 11/0) |
| `make test-core` | rc 0 (incl. `ksrc_deps_check`) |
| `make test-registry` | rc 0 |
| `make test-rxtsource` | rc 0 (census unmoved: kfixtures are written per run) |
| `make test-codegen` | 16/16 after one fix (a K37 false positive on `$(dirname "$PCREC")` in the new script, rewritten) |
| `make test-spec-history` | 145/0 |
| `make test-plan-lint` | rc 0 |
| `make test-ci-shards` | rc 0 (72 sections, each in one shard) |
| analyze's own tests | inside test-findings, green |
| mech solo rows | §5 |

## 9. Heavy validation owed (the manager's)

- the full `make test` (through `scripts/perfrun`); `test-knowledge` is new
  in `TEST_SECTIONS` and its CI shard weight is ESTIMATED (5 s);
- `make mech` (new arm `knowledge`; rows S961/S962/S984 measured solo);
- `make test-axes` was not run (no axis changed);
- the zero-mover runs above are COMPLETE (§3); none is owed.
