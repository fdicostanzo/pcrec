# repin2 — post-batch-2 landing: recursion identity (B) re-pinned to 8e4e9c6c

Branch `lane/repin2` from main `8e4e9c6c` (the batch-2 merge, abi 30). Task:
finish what batch 2 (lane optimpl2) deliberately left owed — `RECURSION_IDENTITY_FILEPIN`
was left at `6ab2464e` (batch 1's own merge) per D76, since a lane branch's own
commit is never a valid (B) pin.

## 1. Re-pin

`tests/codegen/run_recursion_identity.sh`'s `FILEPIN` moved `6ab2464e` ->
`8e4e9c6c`, with the script's own narrative comment updated the way
8d716693's batch-1 landing did it. Gate run: `make test-recursion-identity
CC=gcc-16` (log `build/recid_8e4e9c6c.log`).

**Verdict: `checks passed: 16` / `checks failed: 0`.** All four axes
(default/vm/noprefilter/nocaptures) read (B) whole-file identity against
`8e4e9c6c` at zero differing/zero refusal-mismatch, and (A) program-region
identity against the unchanged pre-module pin `ac4917d` at zero differing
(elision/size-term/island/fold movers exactly matching their named-population
counts, per that gate's own established shape).

## 2. `emit_sweep.py --ref c051a69b`

`python3 scripts/emit_sweep.py --ref c051a69b` (log
`build/emit_sweep_8e4e9c6c.log`, 268.0s). `c051a69b` is the pre-batch-2 commit
(the ratification commit immediately before lane optimpl2 started).

**Self-check PASSED: all-identical, no asymmetry, at full reach** (two
independent builds of `c051a69b`, 0 movers on all five streams).

Real ref-vs-tree sweep — matches the predicted shape exactly:

| stream | population | reach | movers | asymmetric | shape |
|---|---|---|---|---|---|
| c-default | 3954 | 3532 | 3532 | 0 | moves on EVERY reached artifact — abi 29->30 header |
| c-vm | 3954 | 3533 | 3533 | 0 | moves on EVERY reached artifact — abi 29->30 header |
| emit-ir-vm | 3954 | 3533 | 0 | 0 | untouched — the program region is unmoved |
| composition | 306 files / 33 producing | 98 artifacts | 98 | 0 | header-only, every composed artifact moves |
| dumps | 7 | 7 | 2 | 0 | `--list-axes` +1 row (req-run), `--list-limits` +2 rows (PCREC_MAX_REQ_RUN_EMIT, PCREC_MAX_REQ_RUN_SCAN) |

No `FLOOR VIOLATION`, no asymmetric movers, DELIVER witness OK. Sampled
diffs confirm the c-default/c-vm/composition movers are exactly the
`(abi 29)` -> `(abi 30)` header substitution (each diff hunk shown is the
first hunk only, the provenance line — full-file identity past that line
is what the recursion-identity gate above already measured directly).

## 3. abi-29 reader grep, on main's tree

`grep -rn -E "abi 29|ABI 29|abi=29|abi29|\.abi = 29|abi.{0,3}29\b" docs/ tests/
src/ lib/ CHANGELOG*`, dispositioned:

| hit | disposition |
|---|---|
| `tests/codegen/run_recursion_identity.sh` (FILEPIN + narrative) | **stale -> FIXED in this lane** (§1 above) |
| `docs/design/CLAUDE.md:2180` | historical — describes the abi 29->30 event itself; left |
| `docs/spec/match_api.md:2025,2037` | historical — the abi change log's own 29->30 transition prose (D76 addendum: this is the one home for the change log); left |
| `docs/dev/optloop/cycle1_ledger_reading.md:19` | historical — BEFORE/AFTER pins of a batch-1 measurement ledger; left |
| `tests/codegen/run_cpset_structure.sh:533` | historical — "RE-RECORDED ... at batch 2 (abi 29 -> 30)" re-pin note; the file's live manifest already reflects abi 30 (batch 2's own delivery); left |
| `tests/codegen/run_codegen_tests.sh:2862` | the cumulative D94 ritual narrative string — already includes the 29->30 entry; `ABI_EXPECT=30` confirmed live at line 2860; left |
| `tests/resource/run_resource_tests.sh:566,582` | historical — successive re-pin narrative quoting past artifact text; the file's live pin is `762338`/abi 30 (confirmed by the same comment block); left |
| `CHANGELOG.md:48` | correct changelog entry, "`rx_info.abi` 29 -> 30"; left |
| `docs/dev/optloop/linux_ask_i89.md:15` | **flagged, not touched**: an UNSENT draft executor ask deliberately pins `main` at `8d716693` (abi 29) for a scoped, reproducible measurement ("STOP and report what moved rather than proceeding on an off-pin tree"). Main has since advanced to `8e4e9c6c` (abi 30) via batch 2. Whether the ask should move its pin forward is the ask owner's/manager's call — out of this lane's scope (re-pinning the identity gate script), and redirecting an outbound ask is not mine to decide unilaterally. |

No other stale reader found. Every hit besides the FILEPIN itself was
already correctly updated by its own landing lane, or is a deliberate
historical/ledger citation.

## 4. Validation summary

- `bash tests/codegen/run_recursion_identity.sh` (via `make
  test-recursion-identity CC=gcc-16`): **16/0**, log
  `build/recid_8e4e9c6c.log`.
- `python3 scripts/emit_sweep.py --ref c051a69b`: self-check PASSED, real
  sweep matches the predicted five-stream shape exactly, log
  `build/emit_sweep_8e4e9c6c.log`.
- `make -j4 CC=gcc-16` clean build at branch head.

Nothing owed. Commit: `97f3d3ba` (`repin2: re-pin recursion identity (B) to
batch-2 merge 8e4e9c6c (abi 30)`).
