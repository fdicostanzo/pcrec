# land4 report — [CLS-TREE] S4 + [OPT-CLSPACK] landed onto main (2026-09-30, lane land4, sonnet)

Branch `lane/land4` from `lane/clspack` (`59519949`), merged with `main` twice
(`64b55d15`, then `966c9ac8` after lane silentred and lane admin86 landed on
main mid-flight). Nothing merged to main.

## 1. What the landing did

- **ONE abi event, 47 -> 48.** Main sat at 47 ([K73]); S4 (46 -> 47 on its own
  branch) and CLSPACK (47 -> 48) now ride together. `PCREC_ARTIFACT_ABI` 48;
  `ABI_EXPECT=48` and its narrative in `tests/codegen/run_codegen_tests.sh`
  keep K73's 47 entry and append ONE combined S4 + CLSPACK 47 -> 48 entry;
  `docs/spec/match_api.md` §6 keeps K73's entry as "was 47" and gains ONE 48
  entry (S4's and CLSPACK's folded, the identity/census verification of both
  named); the two stamp entries in §6.3 read `abi` 48; `tuning.md`'s S4
  sentences read `abi` 48; `src/gen/CLAUDE.md`, `tests/axes/run_axes.sh`'s K55
  comment and `lib/pcrec.h`'s bit-36 comment likewise. The readers were found
  by grep (`abi.{0,6}47`, `§2.35`, the stamp, `ABI_EXPECT`, FILEPIN) and by the
  suites that count (registry, codegen, rxtsource, cpset: all green, §3).
- **Recursion-identity (B) FILEPIN** self-pinned to the merge commit
  `64b55d15`, the last `src/` change (the K73 convention; the second merge
  moved tests and docs only). Gate 16/0.
- **Spec sections.** Main's last `tuning.md` section is §2.32, so S4 keeps
  §2.33 and CLSPACK's §2.35 became §2.34 (heading, the flags-table row, and
  every cross-reference by grep: `match_api.md`, `lib/pcrec.h`,
  `src/dump/axes_dump.c` comment, three test scripts, two CLAUDE.md files,
  the S400 header, the `.rxt` header, the plan row). **Lane reseed takes
  §2.35.** The lane reports' own §2.35 mentions are historical and left.
- **Deny bits** 36 (`-fno-cls-kit`) and 38 (`-fno-cls-pack`): main ends at 35
  (`-fno-ctx-node`), no collision; bit 37 is left free.
- **Manager ruling (a)**: `-fno-cls-kit` also denies the atom row.
  `vm_cls_tables` (`src/gen/emit_vm.c`) now masks
  `PCREC_NO_CLS_PACK | PCREC_NO_CLS_KIT` onto `1u << CLSTD_ATOM`;
  `-fno-cls-pack` stays the specific deny. Spec hunks: `tuning.md` §2.33 (the
  kit deny reaches §2.34) and §2.34 (the row's deny column, the Denied
  paragraph), the `lib/pcrec.h` comments for bits 36 and 38, the
  `--list-axes` `cls-pack` row's prose. New check `[deny-kit]` in
  `tests/codegen/run_clspack.sh` (24 -> 25 checks); **new sabotage S406**
  (plant: the kit bit dropped from that mask); S401 re-anchored (its anchor
  line is the one edited; the plant now drops `PCREC_NO_CLS_PACK` from the
  mask and leaves the kit bit, same intent).
- **Pins combined by mechanism.**
  - rxtsource census: main 256/4261/31703 + S4 (+1/+47/+744) + CLSPACK
    (+1/+5/+79) = 258/4313/32526; `RUNSH_*` 234/4313/32526; `C3_SKIP` 17711
    + 744 = 18455, `C3_SKIP_PCRE2ONLY` 3504 + 744 = 4248; `C3_PASS`/
    `C3_VERIFIABLE` (CLSPACK's +79) merged without conflict. Verified by
    running the suite (271/0, §3).
  - `run_recursion_identity.sh`: on the second merge, silentred's ctx-node
    bucket (264 -> 0) and CLSPACK's atom axis (the fourth region-moving deny)
    are both in the excuse chain (`|| CTX_POP` after `pack_a`; `stamped` and
    the ctx-hit branch count the atom axis; the (A) echo carries both column
    families). Gate 16/0, (A) `differing=0`.
  - registry axes pin, cpset manifest: both merged clean and passed as they
    stood (the 12-artifact sample's rows are byte-artifacts whose text is
    unchanged by K73).
  - Sabotage anchors: `scripts/m6read_check_sab_anchors.py` 366 sabotages /
    382 sites, all resolve (one stale, S401, before its re-anchor). The
    `SAB_DOC_FIGURE`s of S400-S405 quoted `run_clspack.sh`'s pass total, which
    moved with `[deny-kit]`; re-recorded solo (§3), S406's recorded.
- `plan.md`: main's version of the CLS-TREE row kept (it already says land4 in
  flight); the OPT-CLSPACK row records the landing.
- No conflict markers (grep over tracked sources), `make`, `make strict` clean.

## 2. Decision worth a second look

- **S401's fifth failure.** The plant (drop `-fno-cls-pack` from the mask)
  moved from `clspack:4fail/20pass` to `5fail/20pass`. The fifth is
  `[deny-kit]`, which compares its bitmap count against the
  `-fno-cls-pack` artifact the plant leaves packed. Inferred from the count
  moving by exactly the new check, not read from the log.

## 3. Validation (Mac, PROCS=2, gcc-16)

Suite verdicts are the `*** [test-X] Error` lines and the trailer counts.

| section | result | note |
|---|---|---|
| `test-cpset-structure` | green (28/0, 17/0, 24/0) | rides `run_clspack.sh` (24 then; 25/0 after `[deny-kit]`, run directly) and CHECK 3's manifest matches as it stood |
| `test-registry` | green | at `64b55d15` |
| `test-rxtsource` | **271/0**, 1 RECORD | the standing py3.9 C3 note; the pins of §1 |
| `test-codegen` | 11/12 scripts | the sole red is the standing darwin `nm could not read arm_a.o` probe, both runs (before and after the second merge) |
| `test-clskit` | green (591 sets, 8,451,676,390 code-point checks, 0 mismatches) | |
| `test-tune-dial` | 22/0 | |
| `test-anchored-match` | green (20/0, 7/0, 7/0) | ~32 min |
| `test-recursion-identity` | **16/0**, (A) `same=1912 differing=0` default, `same=1766 differing=0` vm | after the second merge; the first run (before silentred's bucket) read 264 REGION DIFFERS, all lookaround/`\b` (the ctx-node population silentred's excuse closes) |
| `run_clspack.sh` | 25/0 | |
| mech solo | S390, S391, S392, S393, S394, S395, S400, S401, S402, S403, S404, S405, S406, S365: **all DETECTED**, 0 unexpected/undetected/unreached/anomalies | figures: S390 corpus 32/712, S391 corpus 16/728, S392/S394/S395 wclass 1/16, S393 tunedial 3/19, S400 clspack 4/21 + corpus 16/63, S401 5/20, S402 5/20, S403 10/15 + corpus 46/33, S404 1/24, S405 4/21, S406 1/24, S365 wclass 3/14 |

### `cls_identity.py --ref main` (main = abi 47)

- **Raw**: 16,009 triples, `mover` 13,775, `both-refuse` 2,167, `asymmetric` 67,
  0 identical. Every compiled artifact moves: the abi digit and the two new
  stamp lines (`<PREFIX>_VM_CLS_KIT`, `<PREFIX>_VM_CLS_ATOMS`) are on all of
  them. Instrument control PASS.
- **Normalized** (scratch wrapper `build/candnorm.sh`, uncommitted: candidate
  stdout with `(abi 48)`/`.abi = 48` put back to 47 and the two stamp lines
  deleted; population 16,005 — four fewer triples than the raw run, cause not
  chased):
  - default flags: `identical` 13,257, `mover` 514, `asymmetric` 67,
    both-refuse 2,167. The 514 = 505 utf8 (S4's decode + class-matcher route;
    460 read REACH True, the rest are unmeasured-reach or the 19 caseless
    span-compare decoders) + 9 byte. The byte movers are the atom witnesses:
    `clspack_census.py --base main --cand candnorm` reads **moved 6 =
    predicted 6, 0 unpredicted, 0 predicted-but-unmoved** (3,422 patterns,
    6,097 compiled; the corpus's max per-site bitmap count is 6, so the row
    fires only on the constructed witnesses) plus the bench `timestamp`
    pattern of the next bullet.
  - **The 67 asymmetric are all `base=refuse cand=ok`, all utf8 and REACH
    True, none the other way**: S4's retired refusals (`\p{L}+`, `\P{L}+`,
    `^\p{L}{4}$`, `(\p{Ll}+)y`, `\p{Unknown}` shapes under `--engine=vm`, K55).
  - **`-fno-cls-kit`** (`CAND_EXTRA`): `identical` 13,750, `mover` **21**,
    `asymmetric` **0**, both-refuse 2,234 (2,167 + the 67). The 21 are the
    expected exceptions: 19 utf8 caseless span-compare artifacts (the decoder
    relocated into `PCREC_ENCE_DECODE`) and the bench `timestamp` pattern at
    byte and utf8 (its size-retry WHY text quotes a byte count that included
    the stamp line — S4's recorded exception). Denying the kit therefore
    also removes all 9 byte movers, i.e. the atom row (ruling (a) verified
    end to end).

## 4. OWED — Linux full `make test`

- Worktree `~/pcrec/worktrees/land4-lx` on ubuntubudu at **`966c9ac8`**
  (bundle `~/pcrec/worktrees/land4-lx.bundle`), launched detached
  (`setsid nohup`), default workers, `make -j4` then `make test`.
- Logs: `~/pcrec/worktrees/land4-lx/land4_build.log`,
  `~/pcrec/worktrees/land4-lx/land4_test.log`; completion line `MAKE_RC=`.
  Verdict = the `*** [test-X] Error` lines (never "sections ran").
- Commits after `966c9ac8` (sabotage figures, this report) are docs and
  `tests/mech/sabotages/*.sh` header fields only.
- Expected place for a red: rxtsource's C3 split tier (python 3.14 numbers):
  the Mac pins above are the box-independent classes; a Linux move would be
  re-pinned from its own numbers with the mechanism stated.
- Cleanup:

      git -C ~/pcrec worktree remove --force worktrees/land4-lx
      git -C ~/pcrec branch -D lane/land4-lx
      rm ~/pcrec/worktrees/land4-lx.bundle

## 5. Open for the manager

1. Merge order: reseed lands after this and takes `tuning.md` §2.35 and the
   next free deny bit; its abi event is 48 -> 49 (main + this = 48).
2. `plan.md` OPT-CLSPACK row still says "PENDING MERGE / full make test OWED";
   flip at merge.
3. The `(\p{Xwd})` default-axes refusal on total emitted bytes and the
   `-2` P3-larger-source note from `s4build_report.md` §3 are unchanged and
   still Frank's.
