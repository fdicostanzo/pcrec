# sp1g — span_pick stage 1, unit 1g (provenance leaves the seam)

Lane sp1g (opus), branch `lane/memfn-sp1g`, cut from main c0f0d543b (units 1a and 1f landed). Design of
record: span_pick.md rev 5.2 §Staging unit 1g and its reader-list row, §What stage 1 deletes (the
`mf_prov` row), §pcrec-side row 0, dispositions R1/C4/C8; D186 add. 2. Build go: the owner's conditional
approval of 2026-11-02, confirmed by main's GO for stage 1. Scope: unit 1g only; nothing from any other
unit.

STATE: delivered. Validation in the lane is COMPLETE; the landing gates are prepared as box-queue jobs and
are NOT queued (the manager queues them).

## What changed

Commits on `lane/memfn-sp1g` (oldest first): c9a6e345f (code and tests), 638c9ff01 (design revision
lines, kit journal, CLAUDE.md readers), then this report.

- **`memfn/include/memfn.h`**:
  - `mf_akind` is now {tag, version, present, digest, payload}.
  - `mf_prov`, `mf_prov_source` (with `MF_PROV_*`) and `mf_prov_fidelity` (with `MF_FID_*`) are deleted.
    The digest moved to `mf_akind.digest`.
  - The analysis-object header comment lost its stale "NO kit row reads it before B3a". It now cites unit
    1g as the amendment to window_contract.md §3.1's layout.
  - **MF_SITE_ABI 21 -> 22**, with a history entry recording the removal. The earlier entries that name
    `mf_prov` (15, and 12's "DECLARED mf_analysis") are kept as history.
  - No MF_VOCAB or MF_CLASS_V move.
- **`src/gen/memfn_sites.c`**:
  - Deleted: `akind_source_map`, the provenance stanza table `prov_fidelity_rows`,
    `prov_fidelity_token` and `pcrec_memfn_prov_stanza`.
  - Deleted: the out-of-vocabulary fidelity refusal. The schema's `closed fidelity` row already closes
    the vocabulary at parse.
  - The object builder now writes `k[i].digest = o.digest`.
  - The `KSRCTRACE object` record (`analysis_trace`) now reads pcrec's OFFER instead of the built object:
    `o->bytes`, and `o->fidelity` or `-`. Its columns are unchanged, and it is byte-identical on 1,686
    records (Witness).
  - `analysis_invariant` is unchanged. It checks the offer.
- **`src/gen/memfn_sites.h`**: the `pcrec_memfn_prov_stanza` declaration is deleted.
- **`tests/memfn/prov_check.c`**: reduced to one build-only static assertion, `offsetof(mf_akind, digest)
  == 16` on LP64. It includes only `memfn.h` and has a trivial `main`.
- **`tests/memfn/run_finder.sh`**:
  - prov_check.c still builds `-Werror` against `memfn/include` alone (no lib, no `src/`). It is never
    run.
  - The `--provchk` argument is gone.
- **`tests/memfn/finder_check.py` section L**:
  - Parts (1)-(3) are retired, with `schema_fidelity_tokens`, `prov_run`, `FID_EXPECT`, `FID_OUTSIDE` and
    the required `--provchk` argument.
  - Part (4) is re-aimed, in two halves:
    - (4a) `KIT_READERS_RE` and a member parse of `memfn.h` with comments stripped. `mf_akind`'s members
      must hold `digest` and `payload` and none of source, bundle, bytes, fidelity or `prov`. The header's
      code must name no `mf_prov*`, `MF_PROV_*` or `MF_FID_*`; history comments may.
    - (4b) A render loop over digests 0 (the reference), 1, 2, 0x1234 and 0xffffffffffffffff, with the
      rates fixed. It runs on sites set10 and byte1t, under the plain and the traced kit.
  - The docstring is updated.
- **`tests/memfn/arm_fixtures.c`**:
  - `--fd-an FID` is now `--fd-an DIGEST` (parsed with `strtoull`, base 0).
  - `fd_an_make(digest)` states the fixed `an_rates` plus `mf_akind.digest`.
  - The header and usage text are updated.
- **`memfn/tests/g2/g2_win_gen.c`**: the two `kd`/`kind` builders set `.digest = 1` (they had set
  `prov.source`/`bundle`/`digest`).
- **`tests/findings/e1_object_check.py`**: the header gains THE PREMISE. The record is the offer the
  object is built from, not the object; columns are unchanged. There is no code change.
- **Mech**:
  - `tests/mech/sabotages/S1092_prov-stanza-drops-fidelity.sh` is deleted (RETIRED).
  - The memfnfinder block of `tests/mech/run_sabotage_matrix.sh` records the retirement, and that L(4)'s
    plant was hand-run (see OWED).
- **Docs**:
  - `docs/design/memfn/window_contract.md` §3.1 and §3.2 each gain a `[span_pick 1g, MF_SITE_ABI 22]`
    revision line. The rev 3.1 block stays as the record.
  - `memfn/docs/journal.md` gets one entry.
  - CLAUDE.md files: `memfn/CLAUDE.md` (prov_check.c's role), `memfn/include/CLAUDE.md` (MF_SITE_ABI 22),
    `tests/memfn/CLAUDE.md` (prov_check.c's own entry, its role restated) and `tests/findings/CLAUDE.md`
    (e1_object_check's premise).
  - `docs/dev/history/claude_md/docs__dev__lanes.md` gets this report's index line.

Caller-visible: none. `docs/spec/` names none of the removed spellings. The grep for
`mf_akind|mf_prov|MF_PROV|MF_FID|PRIOR_NONE|PRIOR_AUTHORED|analysis object|prov_stanza|MF_SITE_ABI` over
`docs/spec/` is empty. No pcrec abi bump, no stamp, no `--list-*` row moves: MF_SITE_ABI reaches no text
or listing. A grep of src/, cli/ and lib/ for MF_SITE_ABI finds no reader.

## Readers (grep table)

The grep was `MF_PROV_\|MF_FID_\|mf_prov\|\.prov\.\|->prov\b\|prov_stanza\|provchk\|prov_check\|fidelity`
over the whole tree, excluding worktrees/, build dirs, .git and docs/dev/lanes/. It gave 126 files. Most
`fidelity` hits are pcrec's findings and `.rxt` provenance vocabulary, which 1g keeps. Narrowed to the
seam names (all but `fidelity`) at the base, it gave 42 files. The base's seam-name readers and the
dispositions:

| hit | disposition |
|---|---|
| memfn/include/memfn.h (struct, 2 enums, analysis header comment) | CHANGED |
| memfn/include/memfn.h MF_SITE_ABI history 12, 15 | KEPT as history; 22 records the removal |
| src/gen/memfn_sites.c `akind_source_map`, builder writes, `prov_fidelity_rows`, `prov_fidelity_token`, `pcrec_memfn_prov_stanza`, `analysis_trace` | CHANGED (deleted / now reads the offer) |
| src/gen/memfn_sites.h `pcrec_memfn_prov_stanza` | CHANGED (deleted) |
| tests/memfn/prov_check.c | CHANGED (reduced to the digest offset) |
| tests/memfn/run_finder.sh (prov_check build, `--provchk`) | CHANGED |
| tests/memfn/finder_check.py L, docstring, `--provchk` | CHANGED |
| tests/memfn/arm_fixtures.c `fd_an_make`, `--fd-an` | CHANGED |
| memfn/tests/g2/g2_win_gen.c :625-627, :830-832 | CHANGED |
| tests/mech/sabotages/S1092_* | RETIRED (deleted); run_sabotage_matrix.sh :503's "S1092 joined" line kept as history, retirement paragraph added |
| memfn/CLAUDE.md :38, memfn/include/CLAUDE.md, tests/memfn/CLAUDE.md :84 | CHANGED |
| tests/findings/e1_object_check.py (record columns BYTES FIDELITY) | CHANGED (header premise; columns unchanged) |
| docs/design/memfn/window_contract.md §3.1/§3.2 (18 hits) | CHANGED (revision lines); rev 3.1 text kept as record |
| docs/design/memfn/span_pick.md, docs/dev/decisions.md D186 | NOT readers: the design of record |
| docs/design/kit_proof.md :1079, docs/dev/full_suite_ledger.md :54 | KEPT as history |
| docs/design/ctx_span/call_graph*.txt, sabotage_anchors*.tsv, docs/design/measure_sets/k[23]_anchors.tsv | NOT readers: dated snapshots (CHECK_rev51 says the same) |
| docs/dev/history/claude_md/*.md, docs/dev/reviews/*, memfn/docs/journal.md, requests.md, responses.md | KEPT as history |
| src/core/findings.{c,h} (`PcrecFindOffer.bytes/fidelity`, `prov_fidelity`), src/core/internal.h, src/parse/rxt_*, rxt_schema.def, src/dump/findings_dump.c, src/findings/log.rxt | NOT seam readers: pcrec's offer/findings vocabulary, kept (the trace reads it) |
| analyze/*, tests/findings/* (other than e1_object_check.py), tests/rxtsource/*, tests/knowledge/kfixtures.py, tests/lookaround, tests/reject, tests/recursion, scripts/ksgen.c, third_party/*, docs/spec/rxt_format.md, findings.md | NOT readers: `.rxt`/findings `fidelity` vocabulary |
| tests/mech/sabotages/S240, S992, S1030 | NOT seam readers: they plant in rxt_schema.def / findings.c (S992/S1030 are in the mech list below via the e1 record) |
| emit_sweep.py :2777, run_part_analysis.sh, data_trace_check.py, S1332 (KSRCTRACE line counters) | NOT readers (the design's list; confirmed: they count or drop lines, never parse the object columns) |
| docs/dev/lanes/r33_sim/probe.c | NOT a reader (lane evidence, excluded) |
| tools/review/out/literal_census.tsv, literal_value_freq.tsv | NOT readers: generated review metrics (dated) |

Beyond the design's list, this lane found:

- `tests/findings/CLAUDE.md`, which names e1_object_check's object premise.
- The analysis-object header comment's stale "NO kit row reads it before B3a". It is reworded rather
  than just deleted.

After the change, the seam grep over src/, cli/, lib/, memfn/src, memfn/tests and tests/ code finds only
comments and the check's own regex.

## Witness (run in the lane, all light)

- `make` and `make strict` (`strict: whole tree compiles clean with -Werror -Wshadow`): clean.
- `make test-memfn-finder`: **1903 passed, 0 failed**, against 1924 at 1f. L went from 40 checks to 19:
  2 member checks, 1 code-name check and 16 render cells. The section's other parts are unchanged: proven,
  arm_reach, pr11, presence, proof.
- **L(4)'s plant is RED**, then reverted:
  - The plant went in `memfn/src/finder.c` `fd_holds`: a row holds only if the handed analysis's
    `kinds[0].digest` is odd. This is the design's "a kit row reading `mf_akind.digest`, holding iff the
    digest is odd".
  - `bash tests/memfn/run_finder.sh` (the file the section runs): 1832 passed, **47 failed**, rc 1.
  - Six of them are L cells: plain byte1t and traced set10/byte1t, each at digests 1 and
    0xffffffffffffffff.
  - The rest are collateral from real compiles: F-B1-3, arm_reach and others.
  - The file was restored byte for byte (`git diff --quiet`) and rebuilt; `make test-memfn-finder` is
    then green (the 1903 above).
- **Byte-identity spot check** (`$PCREC_TMPDIR/scratch/memfn/sp1g/tools/spot.py`, log
  `.../sp1g/logs/spot.log`):
  - Base c0f0d543b (git archive, plain and `-DPCREC_KS_TRACE` builds) against HEAD (the same two).
  - 125 patterns: job 588's 24, the first 100 of the frozen bench list, and `zzzzzzz~J`.
  - 6 arms: default, `-e utf8`, `--analysis weblog`, `--analysis log`, `-e utf8 --analysis weblog`,
    `--engine=vm --analysis weblog`.
  - Compared per compile: rc, the emitted C, the non-trace stderr and the `KSRCTRACE object` records.
  - Result: `spot: patterns 125 arms 6 compiles 3000 ksrctrace-object-records(head) 1686 differ 0`.
- Ratchet R20-R27 (1f's transcription, `.../sp1g/tools/ratchet.sh`): base `R20=3 R21=1 R22=3 R23=1 R24=2
  R25=1 R26=0 R27=0 total=11`, HEAD identical. No delta, as designed.
- Mech: `VALIDATE_ONLY` over the 62 gate rows reports `62 definition(s) valid`. Every row's SAB_BEFORE*
  anchor matches its file at HEAD with the declared count (checked by script).
- `g2_win_gen.c`: compiles with `-Wall -Wextra` (`-fsyntax-only`). Its run is inside test-memfn-g2,
  queued (job 351).

## Gate jobs (prepared, NOT queued)

Scripts are in `/var/tmp/pcrec-pcrec/scratch/memfn/sp1g/jobs/` (common.sh, ident.sh, mech.sh plus one file
per job), keys `kit-sp1g-*`. Every one dry-runs rc 0. Prefixes 350-359 are suggestions; rename freely.

Frozen inputs, all under `.../sp1g/`:

- `ref/build/pcrec` and `ref-mftrace/pcrec`: the base, from a git archive of c0f0d543b.
- `p588.txt` and `pzzz.txt`, copied from sp1f's.
- The tree's `spanpick_bench_patterns.txt` (392). Total 417, checked.

| # | key | stage | est s | after |
|---|---|---|---|---|
| 350 | kit-sp1g-strict | make strict | 240 | - |
| 351 | kit-sp1g-memfn | test-memfn-{rows,finder,link,g2,arms,stamps,deleg,manifest}, test-findings, test-registry | 900 | kit-sp1g-strict |
| 352 | kit-sp1g-reach | HEAD MF_TRACE build; reach_equal.py, 18 arms (1f's 16 + `--analysis weblog`, `-e utf8 --analysis weblog`), NO `--gone` | 1250 | kit-sp1g-memfn |
| 353-355 | kit-sp1g-ident1/2/3 | emit_sweep identity, the 67 declared arms + 2 analysis arms (`an-weblog`, `an-weblog-utf8`: `--extra`, streams c-default,c-vm,emit-ir, `--no-differ-floor`), 23 per shard; NO declared dumps delta | 2450 each | reach, ident1, ident2 |
| 356 | kit-sp1g-test | make test ALONE via `scripts/perfrun --label sp1g` | 1800 | kit-sp1g-ident3 |
| 357-359 | kit-sp1g-mech/mech2/mech3 | 62 mech rows, 21/21/20, bar `unexpected: 0, undetected: 0, unreached: U, anomalies: 0` (U = 2, 1, 0) | 2400 each | test, mech, mech2 |

The analysis-arm smoke ran both extra arms on `zzzzzzz~J` against the base: rc 0, movers 0, self-check
passed.

### Mech rows (how derived)

The rows are the union of three greps over `tests/mech/sabotages/` (list in `.../sp1g/mechids.txt`):

- **(A) Changed path or basename** (1f's method; the runner itself excluded). Changed files hit: memfn.h,
  memfn_sites.c, arm_fixtures.c, finder_check.py and run_finder.sh. memfn_sites.h, prov_check.c,
  g2_win_gen.c and e1_object_check.py name no row. Rows: S520 S526 S571 S618 S619 S671 S677 S678 S681 S682
  S800-S804 S846-S848 S917 S919 S993 S994 S1018 S1020 S1031 S1079-S1084 S1089 S1109 S1221 S1224 S1225 S1294
  S1332 S1419.
- **(B) Every `SAB_SUITES=memfnfinder` row.** That arm runs run_finder.sh and finder_check.py, both
  changed. Adds S1100 S1103 S1105-S1108 S1110 S1122 S1543-S1548.
- **(C) Every row read through the `KSRCTRACE object` record or §14's e1_object_check.py.** The record's
  source moved from the built object to the offer. Adds S991 S992 S995 S996 S1027-S1030 S1034.

Retired: S1092, in this change.

Declared UNREACHED, unchanged by 1g:

- S917 and S919, in shard 1.
- S1029, in shard 2: UNREACHED until [FINDINGS] B4.

Nothing new is UNREACHED or RETIRED beyond S1092.

## Design deviations (conservative choices)

1. **L(4b)'s reference is the same fixed-rate analysis at digest 0, not "no analysis".**
   - The old loop compared an analysis against no analysis. Design R22 says that comparison would read red
     once a priced fd row reads rates.
   - The re-aimed loop holds the rates fixed and varies only the digest, which is what "its render loop
     varies the digest" and R22 ask for.
   - The no-analysis-versus-analysis cell is dropped.
2. **L(4a) checks `memfn.h`, not `memfn/src`.**
   - `KIT_READERS_RE` now scans memfn.h's code (comments stripped) for `mf_prov*`/`MF_PROV_*`/`MF_FID_*`,
     and parses `mf_akind`'s members, as the brief words it.
   - The old memfn/src scan would be vacuous, because those names no longer compile.
3. **L(4)'s plant is a hand plant, not a matrix row.**
   - The brief names no S-id range, and BOILERPLATE forbids numbering without one.
   - It was run and shown RED in this lane (Witness).
   - The matrix row is OWED (below).
4. **The reach and identity gates add two analysis arms** that 1f's model did not have. 1g changes the
   analysis object, and the 67 declared identity arms carry no analysis.
5. **arm_fixtures' `--fd-an` operand changed meaning**, from FID to DIGEST. Its only caller is
   finder_check L.

## Charter vs committed

| 1g promise (design row / brief) | artifact |
|---|---|
| `mf_akind` = {tag, version, present, digest, payload}; digest stays | memfn.h (c9a6e345f) |
| `source`, bundle label, `bytes`, `fidelity` leave; `mf_prov`, `mf_prov_source`, `mf_prov_fidelity` go | memfn.h |
| pcrec's stanza mapping goes (`akind_source_map`, `prov_fidelity_rows`, `pcrec_memfn_prov_stanza`, the fidelity refusal) | memfn_sites.c/.h |
| MF_SITE_ABI 21 -> 22, history entry recording the removal, earlier `mf_prov` entries kept | memfn.h :39 history |
| byte-identical; no pcrec abi, MF_CLASS_V or ratchet change (11) | spot check 3000/0; ratchet 11/11; gates 352-355 OWED to the queue |
| `KSRCTRACE object` records unchanged byte for byte, reading the offer; e1_object_check.py header restated | memfn_sites.c `analysis_trace`; spot 1686 records identical; e1_object_check.py |
| finder_check L parts (1)-(3) retire with `--provchk` plumbing | finder_check.py, run_finder.sh |
| L(4) re-aimed: memfn.h states no source/bundle/bytes/fidelity; render loop varies digest; plant (digest odd) RED | finder_check.py; arm_fixtures.c; plant run (Witness) |
| S1092 RETIRED with its run_sabotage_matrix.sh reference | file deleted; matrix header paragraph |
| prov_check.c reduced to `mf_akind.digest`'s offset, build-only, run_finder.sh keeps it | prov_check.c, run_finder.sh |
| g2_win_gen.c :627/:832 -> `mf_akind.digest` | g2_win_gen.c |
| no docs/spec name | grep empty (Changes) |
| window_contract.md §3.1/§3.2 revision line | 638c9ff01 |
| memfn/CLAUDE.md, memfn/include/CLAUDE.md, tests/memfn/CLAUDE.md | 638c9ff01 (+ tests/findings/CLAUDE.md) |
| kit journal entry | memfn/docs/journal.md (638c9ff01) |
| readers found by grep, table in report | Readers section |
| gate jobs prepared, mech rows listed with derivation | Gate jobs section |
| responses-ledger line (MF_SITE_ABI 22) | OWED: kit session (single writer), trigger: 1g's gates green |
| a matrix row for L(4)'s digest plant | OWED: kit manager assigns an S-id from the kit's range; trigger: next kit mech batch (the plant text is in Witness) |
| full gate verdicts (strict, sections, reach, ident, make test, mech) | OWED: manager queues jobs 350-359 |

## Non-routine

- **An accidental launch was caught and killed before it ran anything.**
  - While checking the shard lists, I invoked mech.sh without `--dry-run`, so shards 1 and 2 started the
    real matrix.
  - Both sat WAITING on the box lock (`300-main-fullsuite` held it) and never ran a row. Each `mech.log`
    holds only the `boxlock: ... WAITING` line.
  - I killed both by `scripts/safekill`, including the loop's parent shell, and deleted their scratch. The
    only side effect was a no-op `make -j16` in my worktree.
- S678 sits on main's open class-A anomaly list (s677fix_report.md "Other class A rows remain"), and S678
  is in shard 1. If shard 1 reads `anomalies: 1` on S678, that is main's open issue, not 1g. The row's
  anchors match at HEAD.

## STATE AT HANDOFF

- Branch `lane/memfn-sp1g`, committed and clean (lane scratch untracked under `$PCREC_TMPDIR`).
- Jobs 350-359 are prepared in `.../sp1g/jobs/` and dry-run green. They are NOT queued: the manager queues
  them.
- No known red. Nothing from any other unit.
