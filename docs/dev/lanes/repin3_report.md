# repin3 — post-admitimpl landing: recursion identity (B) re-pinned to 6ef76820

Branch `lane/repin3` from main `6ef76820` (the `[OPT-PRECHECK-ADMIT]` merge,
abi 31). Task: finish what `admitimpl` (`docs/dev/lanes/admitimpl_report.md`
§3) deliberately left owed — `RECURSION_IDENTITY_FILEPIN` was left at
`8e4e9c6c` (batch 2's own merge, repin2's pin) per D76, since a lane branch's
own commit (`lane/admitimpl`'s tip) is never a valid (B) pin.

## 1. Re-pin

`tests/codegen/run_recursion_identity.sh`'s `FILEPIN` moved `8e4e9c6c` ->
`6ef76820`, narrative comment appended in repin2's own shape (the prior
paragraph kept as history, a new one added rather than rewritten). Gate run:
`make test-recursion-identity CC=gcc-16` (log `build/recid_6ef76820.log`).

**Verdict: `checks passed: 16` / `checks failed: 0`.** All five axes
(default/vm/noprefilter/nocaptures/linkage) read (B) whole-file identity
against `6ef76820` at zero differing/zero refusal-mismatch, and (A)
program-region identity against the unchanged pre-module pin `ac4917d` at
zero differing (elision/size-term/island/fold movers matching their named
populations, per this gate's own established shape).

## 2. `emit_sweep.py --ref 32902104`

`python3 scripts/emit_sweep.py --ref 32902104 --jobs 4` (log
`build/emit_sweep_6ef76820.log`, 250.5s). `32902104` is main immediately
before the admitimpl merge (abi 30).

**Self-check PASSED: all-identical, no asymmetry, at full reach** (two
independent builds of `32902104`, 0 movers on all five streams).

Real ref-vs-tree sweep, matching the predicted shape exactly:

| stream | population | reach | movers | asymmetric | shape |
|---|---|---|---|---|---|
| c-default | 3954 | 3532 | 3532 | 0 | moves on EVERY reached artifact — abi 30->31 header + `RX_REQ_WHY` insertion |
| c-vm | 3954 | 3533 | 3533 | 0 | moves on EVERY reached artifact — abi 30->31 header + `RX_REQ_WHY` insertion |
| emit-ir-vm | 3954 | 3533 | 0 | 0 | untouched — the listing carries no `#define` and no `RX_REQ_WHY` |
| composition | 306 files / 33 producing | 98 artifacts | 98 | 0 | header-only twice over (`.c`+`.h` pairs) — every composed artifact moves |
| dumps | 7 | 7 | 0 | 0 | untouched — no axis bit was spent, no registry surface moved (matches admitimpl_report.md §5.1 item 4's own prediction) |

No `FLOOR VIOLATION`, no asymmetric movers, DELIVER witness OK. The script's
own exit code is 1 (`identity_required=True` on c-default/c-vm/composition
flags any mover as non-identical), which is the EXPECTED shape for a
ref-before-the-bump comparison and not a finding — the same shape repin2's
own `--ref c051a69b` run produced.

**Three sampled mover diffs, built by hand from the sweep's own kept
`build-emitsweep/src_ref` binary against `build/pcrec`** (matched
basenames, avoiding the `#include` trap):

- `a(b|c)+d` (c-default): two abi digits (30->31) plus one inserted line,
  `#define RX_REQ_WHY "emitted"` — nothing else in the 438-line file moves.
- `(b|c)` (c-default, G1/G2-declined): same two abi digits plus
  `#define RX_REQ_WHY "none"` inserted — the declined case's own token.
- `\bx*` (composition fixture `start_pinned_startpos.rxt`): same two abi
  digits plus `#define RX_REQ_WHY "none"` inserted.

Each is exactly the abi-bump header substitution plus admitimpl's one new
stamp line, matching `admitimpl_report.md` §2's own movers census
(zero-added-line, pure-deletion-plus-stamp shape) applied in the other
direction (ref-had-neither -> tree-has-stamp-and-declined-text-removed nets
out, on these three call-free/non-declining witnesses, to a pure insertion).

## 3. abi-30 reader grep, on the merged tree

`grep -rn -E "abi 30|ABI 30|abi=30|abi30|\.abi = 30|abi.{0,3}30\b" docs/
tests/ src/ lib/ CHANGELOG*`, dispositioned:

| hit | disposition |
|---|---|
| `tests/codegen/run_recursion_identity.sh` (FILEPIN + narrative) | **stale -> FIXED in this lane** (§1 above) |
| `docs/spec/match_api.md` §6 (the ONE change log, [REVW.A1]/D76 addendum) | already correctly updated by admitimpl's own delivery — the `abi 31` entry is the live head, the `abi 30` entry re-headed "was"; left |
| `docs/dev/lanes/admitimpl_report.md`, `docs/dev/lanes/repin2_report.md` | own lanes' committed reports — historical record of what each lane did; left |
| `docs/dev/lanes/CLAUDE.md:2747` (repin2 entry), `:2899` (admitimpl entry) | historical lane-index entries, correctly describing what each landed; left |
| `tests/resource/run_resource_tests.sh:566-612` | live pin already re-recorded to `762367` by admitimpl (§5.1 item 2 of its own report); the `abi 30`/`abi 29` mentions are the file's own re-pin narrative history; left |
| `tests/codegen/run_cpset_structure.sh:533-550` | live manifest already re-recorded (all twelve `EMITTED_BYTES` rows) by admitimpl; the `abi 30 -> 31` mentions are the same re-pin narrative history; left |
| `src/gen/CLAUDE.md:3080` | admitimpl's own new `[OPT-PRECHECK-ADMIT]` section header, correct as written; left |
| `tests/codegen/CLAUDE.md` §5 entry | correct, current documentation of the abi 30->31 stamp split; left |
| `docs/dev/dev_journal.md` (multiple) | append-only journal entries, historical by convention; left |
| `docs/dev/plan.md:435` | the `[OPT-PRECHECK-ADMIT]` row itself, correctly narrating its own abi 30->31 delivery; left |
| `docs/dev/optloop/**` (cycle1/cycle2 readings, b2ledger, dated run snapshots under `runs/2026-09-23-o49-b1885a83/`) | dated measurement pins/snapshots naming a specific abi as part of a reproducible before/after record — `repin2_report.md`'s `linux_ask_i89.md` precedent: historical by construction, not touched |
| `docs/design/variables_pattern.md:56` | design note citing `[OPT-REQPOS] tier 2b, abi 30` as the historical landing point of a *different* mechanism (the run-check, not this bump) — correct as written; left |
| `docs/dev/reviews/2026-09-23-r1-var-design.md:149` | review doc citing the same historical landing point; left |
| `docs/dev/lanes/admitimpl_census.py:43` | normalizes `"(abi 30)"` -> `"(abi X)"` as its own comparison logic (the census tool's documented purpose, per admitimpl_report.md); not a stale reference; left |

No stale reader found besides the FILEPIN itself. Every other hit was
already correctly updated by admitimpl's own delivery or is a deliberate
historical/dated citation.

## 4. Validation summary

- `bash tests/codegen/run_recursion_identity.sh` (via `make
  test-recursion-identity CC=gcc-16`): **16/0**, log
  `build/recid_6ef76820.log`.
- `python3 scripts/emit_sweep.py --ref 32902104 --jobs 4`: self-check
  PASSED, real sweep matches the predicted five-stream shape exactly, log
  `build/emit_sweep_6ef76820.log`.
- `make -j4 CC=gcc-16` clean build at branch head.

Nothing owed. Commit: `085bd662` (`repin3: re-pin recursion identity (B) to
admitimpl merge 6ef76820 (abi 31)`).
