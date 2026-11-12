# k382c2b: the findings reader c2b after K38-2 (lane report)

Branch lane/memfn-k382. Brief: the kit manager's ruling of 2026-11-12, take (A).

## Summary

- **(A) is applied.** `tests/findings/gen_adversarial.py` reads both c2 readers from
  `RX_REQ_RUN`'s `@`. The row is told from the artifact:
  - **c2a** is the `@` where row 1 produced it. The artifact has a `_reqrun` pre-check block.
  - **c2b** is the `@` where row 2 produced it. There is no `_reqrun` block: a `cover` find or a
    run-pinned prefilter reads the run.
  - A row-3 artifact has no `@`, so neither reader has a value there.
  - The hex before `@` is the whole run, which no rate chooses. No reader reads it any more.
  - `anti_tables` builds `anti-c2b` beside `anti-c2a`, and both index the whole run's hex.
- **Witness rows read their own row.** `witness()` marks a c2a or c2b stamp that came from the
  other row ("(not row N)"). A witness that drifts to the other row is therefore red.
- **Witnesses re-pinned** (`tests/findings/witness/witness.tsv`):
  - w-c2a keeps `github_pat_[0-9]+`. It is `...@10` under the default and `...@7` under its
    bundle, and both are row 1.
  - w-c2b's pattern moves to `[a-z]abcdefghijkl\d+`, which is run-pinned with no `_reqrun`. It is
    `6162636465666768696a6b6c@9` under the default and `@5` under w-c2b ('f' rarest, position 5).
    Both are row 2.
  - The old w-c2b pattern `(a|b)+foobarbazquux` is a row-1 artifact, so it cannot witness c2b.
  - w-c2b.rxt's header line is restated.
- **The contract (D80).** `docs/spec/findings.md` §4's scan-member row now names which row of
  `match_api.md` §6.3.7¶7's table each reader reads. `docs/design/findings/design.md` §6.2a
  gains a dated note: C2b's window is gone, and the C2a/C2b ids keep new meanings. The witness
  CLAUDE.md is restated. Nothing in `docs/spec/` named c2b by id.
- **The regenerated census is queued, not committed.** It includes census.tsv, fire-*.rxt and
  reach.tsv, as job `591-kit-k382c2b-gen2`.

OWED: job 591-kit-k382c2b-gen2. It regenerates census.tsv, fire-*.rxt and reach.tsv for the
re-aimed readers, then runs reach and `make test-findings` over them. Its output is NOT committed.
A fresh agent reads the verdict (`scripts/monread kit --wait`) and then:
- checks that the census c2b column of the fire-c2b winner is >0 (condition 2's population);
- commits `tests/findings/adversarial/` (named paths);
- re-reads `measured_axes.tsv`/`cloud_axes_shards.tsv`. They need no edit under (A), since the
  arms keep their names.

## Ruling applied (A or fallback B, with why)

**(A)**, per the ruling and span_runs_sheet.md §4.3 ("the c2a/c2b rows re-aimed at rows 2 and 3
and counted"). The fallback (B) did not trigger, because condition (2) holds: a rate moves row 2's
`@` on a real artifact. Two pieces of evidence:
- w-c2b moves @9 to @5 under its bundle, with row 2 on both sides.
- The committed fire-c2b ('inverted') moves the new c2b on 1 of its 10 old reach rows. Those rows
  were derived for the old reader. Run: `gen_adversarial.py reach`, `REACH fire-c2b 1 of 10`.

Row 3 has no `@`, so it has nothing to count. Its artifacts fall out of both readers, and the
census treats them like any non-reader artifact.

## Disjointness plants

Each plant was a temporary edit to `src/gen/emit_dfa.c` `req_run_at`, built and run against
`gen_adversarial.py witness`, then reverted with `git checkout`. The tree was rebuilt and all five
witnesses PASS again. Logs are in `$PCREC_TMPDIR/scratch/memfn/k382c2b/`.

| plant | edit | w-c2a | w-c2b | others |
|---|---|---|---|---|
| 1: break row 1 only | `return cls->run.scan` -> `return whole_len - 1` (rate-free) | **FAIL**: bundle `@10`, pinned `@7` | PASS | PASS |
| 2: break row 2 only | the cover row's `req_run_in_cover(...)` and the run-pinned row's `run_member - (o - at)` -> `whole_len - 1` | PASS | **FAIL**: default `@11`/bundle `@11`, pinned `@9`/`@5` | PASS |

Each reader goes red on its own witness and not on the other's (`plant1.witness.txt`,
`plant2.witness.txt`).

## Rate population

- **The witness.** w-c2b moves `@9` to `@5` under w-c2b. This is a real scanned byte: 'j' becomes
  'f' in the run-pinned prefilter's member.
- **The committed fire-c2b over its old reach rows** moves the new c2b on **1 of 10**. §7 reads
  `REACH fire-c2b 1` (green) even before the regeneration.
- **The census population** is the regenerated census.tsv's c2b column for the fire-c2b winner,
  over the fixed 1,200-config sample. It is OWED from job 591-kit-k382c2b-gen2: the gen's stderr
  line `gen: <cand>: ... c2b=N`, plus census.tsv.

## Checks

| check | result |
|---|---|
| `gen_adversarial.py witness` (current build) | 5/5 PASS |
| `make test-findings` (`scratch/.../findings1.log`, against the committed adversarial/ files) | EXIT 0, every section `checks failed: 0`; §7 fire-c2b REACH 1, §8 w-c2a/w-c2b PASS |
| `make strict` | clean (`strict.log`) |
| `make test-codegen` | rc 0, 920 PASS, 21/21 scripts, no `*** [test-` line (`codegen.log`) |
| `CLAUDEMD_ROOT=worktrees/k382 scripts/check_claudemd_size.sh --all` | 365 within limits |
| plants 1 and 2 | disjoint (above) |
| `make test-findings` over the REGENERATED files | OWED: job 591-kit-k382c2b-gen2 |

## Gate jobs

Under (A) no axes arm changes. fire-c2b keeps its name and file, so `tests/ci/cloud_axes_shards.tsv`,
`measured_axes.tsv` and the axes arm list stay. Gate jobs 600-609 in
`$PCREC_TMPDIR/scratch/memfn/k382/jobs/` are not re-pointed and not queued. No `src/` change
landed, so their BASE and abi stand. The only job queued is `591-kit-k382c2b-gen2`, and its dry
run passed. It is `scratch/memfn/k382c2b/591-kit-k382c2b-gen`: gen, then reach, then
`make test-findings`, with expect `cands=29`.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| take (A): c2a = row-1 `@`, c2b = row-2 `@` | 121116c3d (`choices()`, `anti_tables`, docstring) |
| re-pin both witnesses | 121116c3d (witness.tsv; w-c2b.rxt header) |
| re-derive the fire-* reach rows | OWED: job 591-kit-k382c2b-gen2 (generated, to be committed by a fresh agent) |
| (1) disjoint plants | done, table above (not committed: temporary plants, reverted) |
| (2) rate moves c2b, population >0 | witness + REACH 1 now; census count OWED from 591 |
| (3) fallback B | not triggered |
| findings.md §4 and every place naming c2b (D80) | 6cb2c037b (spec §4, design §6.2a note, witness CLAUDE.md) |
| test-findings, strict, test-codegen, claudemd size | see Checks |
| report + lanecheck | this file |

## STATE AT HANDOFF

- Branch lane/memfn-k382 committed and clean; no rulings file.
- Owed: job 591-kit-k382c2b-gen2's verdict (queue key kit-k382c2b-gen2; its log carries the
  `gen: <cand>: ... c2b=N` lines, the REACH lines and the test-findings summary), then the commit of
  its regenerated `tests/findings/adversarial/` files and the c2b population number in this report.
- The deliver file declares `owed: none`, but the brief's box rule makes the census regeneration a
  queued job, and that job waits behind kclose2's mech chain. So this lane stops honestly instead
  of idle-waiting.

OWED: job 591-kit-k382c2b-gen2 (census/fire/reach regeneration + test-findings over it), then the
commit of `tests/findings/adversarial/`.

STATE: stopped (everything else delivered; the queued census regeneration is the one owed item)
