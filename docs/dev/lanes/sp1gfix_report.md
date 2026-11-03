# sp1gfix — review fixes for span_pick unit 1g

Lane sp1gfix, branch `lane/memfn-sp1gfix`, cut from `lane/memfn-sp1g` @ efd724b4b. Review: critic round
2026-11-03 (readers / emit / check / house, verifier). Everything is byte-identical in emitted C and in the
`KSRCTRACE object` records; no pcrec abi change; MF_SITE_ABI stays 22.

## Findings by id

| id | ruling | what was done | evidence |
|---|---|---|---|
| F1 | FIX-NOW | `finder_check.py` section L rewritten as `check_seam`: rate-reading sites `pre-lead`, `pre-lead-run`, `pre-opt` (no window site exists in the fixture), per-axis REACH control (the `--fd-an 0` render must differ from the no-object render, floor 1), and the static scan "no `memfn/src` file names `digest`" (comments stripped) | plants, each RED then reverted (`git checkout`, `git diff --quiet`): P3 (value-keyed, `digest == 0x5eed` in `fd_holds`) RED 1 fail (static scan; the dynamic loop cannot see a value outside its list, which is why the scan exists); P4 (`kit_pres_picks`) RED, static plus traced pre-lead and pre-lead-run cells; P5 (`kit_byte_rate`) RED, same; control P1 shape is covered by the PLAIN_SITES loop (see F2) |
| F2 | FIX-NOW | L(4a) is an ALLOWLIST: `mf_akind` == {tag, version, present, digest, payload}, `mf_analysis` == {list_v, nkinds, kinds}; the no-object render is restored as the reference on the non-consulting sites (`set10`, `byte1t`), compared with the object under every digest | P6 (`nbytes` on mf_akind plus a D1 reader) RED: member check plus byte1t cells; P7 (`bundle` on mf_analysis plus a D1 reader) RED: member check plus byte1t cells; both reverted clean |
| F3 | FIX-NOW | `analysis_trace(q, o, k)` prints DIGEST from `k->digest` (`&k[i]` passed); every other column still from the offer; `e1_object_check.py`'s opening restated (OFFER columns vs the one OBJECT column, DIGEST) | verifier's plant `k[i].digest = 0;` in `pcrec_memfn_analysis_build`: e1_object_check rc=1, 4 FAILs (C-E1-1 digest vs findings_ref.py, C-E1-4 stamp disagreement) on none/byte and weblog/byte; reverted clean; unplanted control rc=0, 9 PASS lines; records byte-identical (spot below) |
| F4 | FIX-NOW | mech row `tests/mech/sabotages/S1856_kit-byte-rate-reads-digest.sh` (arm memfnfinder, SAB_FILE `memfn/src/presence.c`, P5's shape in `kit_byte_rate`); runner's S1092 comment block now names it as the successor. S1857/S1858 not used | `VALIDATE_ONLY` ok; the row's exact SAB_AFTER applied by hand and run under finder_check L: RED (static scan plus traced pre-lead cells); reverted clean. The real single-row run takes the box lock (held by `300-main-fullsuite`): NOT run, left to the gate shard (mech3) |
| F5 | PLAN | design line added to `docs/design/memfn/span_pick.md` row 1's items: L's digest loop must mask the digest token (or compare decision lines only) once row 1's trace names the digest | text only |
| F6 | FIX-NOW | `[span_pick 1g]` marks at window_contract.md §3.6, §3.7.1 (builder row) and §13 (evidence strength) | doc |
| F7 | FIX-NOW (memfn.h, kit.h) / NOTED (compose.c) | "read by no kit row before B3a" reworded in `memfn.h` `mf_art_begin` comment and `memfn/src/kit.h`; `compose.c:882` left (1d's) | doc/comment only |
| F8 | FIX-NOW | `PRIOR_NONE` in `kit.h` and `presence.c` comments replaced by "present with no payload" | no `PRIOR_NONE` left in `memfn/src` |
| F9 | FIX-NOW | invariant comment/refusal text says "offer (the object is built from it)"; new checked clause `(o->payload == NULL) != (o->digest == 0)` in `analysis_invariant` | grep: the refusal text appears in no test and no `docs/spec` file; the clause can fire only if a payload's digest is 0 (`findings.c` `pcrec_find_offer` sets digest iff a table travels), so no caller-reachable path changes; byte-identity spot 0 diffs |
| F10 | FIX-NOW | memfn.h's digest-struct comment: "no kit row reads the digest, and the kit's trace names it from span_pick row 1" | comment |
| F11 | FIX-NOW | `arm_fixtures.c` `--fd-an`: `strtoull` with endptr/errno check, usage failure rc 2 | `--fd-an zzz` now rc 2 (checked by construction; the check's only user passes valid digests) |
| F12 | FIX-NOW | folded into the L rewrite: labels gone, `KIT_READERS_RE` renamed `RETIRED_SEAM_RE` (it names retired spellings only), the docstring and the section-L header describe what L does today, not its retirements | read |
| F13 | FIX-NOW / NOTED | `prov_check.c`: `main` dropped; `run_finder.sh` builds it `-fsyntax-only -Werror`, no link. Rename NOTED, not done | `make test-memfn-finder` green |
| F14 | NOTED | no trims | |
| F15, F16 | not mine | go to main as plan items | |
| (owed a) S678 | | found ALREADY warning-clean: r30bfix's 2026-10-31 re-plant postdates the suitetri 2026-10-27 class-A listing it was read from. Only the row's `SAB_DOC_FIGURE` changed (the measurement) | planted tree built from the row's plant; harness on `tests/possessify/possessify.rxt` (PROCS=2, outside the matrix runner): 55 failed / 3598 passed, 0 pattern-compile failures, no `-Werror`/`defined but not used`; `VALIDATE_ONLY` ok. The matrix trailer is the gate shard's |

## Validation

- `make`, `make strict`: clean.
- `make test-memfn-finder`: 1934 passed, 0 failed (1903 at 1g; L now 47 checks, the section's other parts unchanged).
- `run_finder.sh` is what the section runs; the plant runs used the same compile steps with `finder_check.py` alone (954 checks passed unplanted, `/var/tmp/pcrec-pcrec/scratch/memfn/sp1gfix/plant/run.sh`).
- e1_object_check (the file `tests/findings/run_findings_tests.sh` section 14 runs, on a scratch `-DPCREC_KS_TRACE` build): rc 0, 9 PASS.
- Byte identity vs c0f0d543b (emitted C, rc, non-trace stderr, `KSRCTRACE object` records): 100 patterns x 3 arms (default, `--analysis weblog`, `-e utf8 --analysis weblog`) x plain and trace builds = 1200 compiles, 704 object records, 0 differ.
- No `make test`, mech shard, test-axes or battery (box held).

## Gate jobs

Copied to `/var/tmp/pcrec-pcrec/scratch/memfn/sp1gfix/jobs/` as `350-kit-sp1g2-strict` .. `359-kit-sp1g2-mech3` (+ `common.sh`, `ident.sh`, `mech.sh`). All ten dry-run rc 0. NOT queued. Changes from the sp1g set: keys `kit-sp1g2-*`, TREE is `worktrees/sp1gfix` (sed it back to `worktrees/sp1g` if the manager merges first), outputs under the sp1gfix scratch (`S2`; the frozen refs and pattern files still read from the sp1g scratch), mech shard 3 gains S1856 (63 rows, 21/21/21), S1092 stays retired, S678 stays in shard 1.

## OWED

- S1856's real matrix run (needs the box lock): shard `359-kit-sp1g2-mech3`; expect DETECTED.
- S678's matrix trailer: shard `357-kit-sp1g2-mech`.
- All gate verdicts (strict, sections, reach, ident, make test, mech) are the manager's, as at 1g.
- compose.c:882 comment (1d's); F15, F16 (main plan items).

## STATE AT HANDOFF

- Branch `lane/memfn-sp1gfix`, committed; lane scratch untracked under `$PCREC_TMPDIR`.
- Jobs are prepared and dry-run green, not queued.
- No known red.
