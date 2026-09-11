# [S5-ARM] abifix — fix summary + owed landing validation

Lane `abifin` finished the validation/disposition/report abifix's fix
(WIP commit d22ca9df) had left owed. The fix itself is unchanged from that
commit; this report documents what was verified on darwin, disposes the
utf8-count discrepancy, and hands the Linux executor an exact re-run list
for the 6 stages S5-ARM found red.

## 1. The fix (d22ca9df, already committed, not touched by this lane)

[ORACLE-LINK]/D98 converted `tests/fuzz/pcre2_abi.h` from a dlopen shim to
direct linking and, in doing so, moved `#include <pcre2.h>` ABOVE the
`#define _GNU_SOURCE` / `#include <dlfcn.h>` block, on the claim that
`pcre2.h` "does not touch `<features.h>` itself." That claim is false:
`pcre2.h` includes `<stdlib.h>`, which is a real glibc header and pulls in
`<features.h>` as its own first action — so on glibc, the OLD ordering
locked the feature-test-macro decision through `pcre2.h`'s own `<stdlib.h>`
before this file's own `_GNU_SOURCE` define ever ran, silently
reintroducing the exact `K-uprops-abi-order` hazard the existing guard was
built to catch, for every consumer, regardless of the consumer's own
include order. Invisible on darwin (the `#ifndef __APPLE__` branch never
runs there) for two days, until the header was next built on the Linux
reference box (S5-ARM), where it broke `dladdr`/`Dl_info` declarations in
six suite stages.

Fixed by three changes, all in `tests/fuzz/pcre2_abi.h`:
- moving `#define _GNU_SOURCE` / `#include <dlfcn.h>` back above
  `#include <pcre2.h>` (restores the dlopen-shim-era ordering, makes the
  header's own correctness independent of what `pcre2.h` happens to
  include);
- adding a second, PORTABLE guard (`#ifdef NULL #error ...` at the very
  top, before the header's own first `#include`) so a genuine
  includer-side ordering mistake now fails at darwin build time too, not
  only on the Linux box.

`tests/probes/probe_altcls_pcre2norm.c` had exactly that includer-side
mistake (its own `#define _GNU_SOURCE` before `<stdio.h>`/`<string.h>`,
with `pcre2_abi.h` included last) — caught by the new portable guard the
first time this probe was rebuilt, fixed by making `pcre2_abi.h` the file's
first `#include`.

`tests/rxtsource/run_rxtsource_tests.sh`'s C3 population was re-pinned
(+0 PASS / +72 SKIP, all +72 pcre2-only; every other `C3_SKIP_*` reason
unchanged) for the S5-ARM Linux reference run at pin `13b56a12`
(`SKIP=15074→15146`, `pcre2-only=2872→2944`). Attribution, isolated
directly (not copied from a Linux log — see the commit's own derivation):
the entire delta is `tests/utf8/axis12_scripts.rxt` (new file, lane
utf8s5, +72 pcre2-only cells), not lane pyrole's C3 mechanism merge
(`db142b16` touches zero `.rxt` files). `CENSUS_LINES=28943` was already
correct (re-pinned a day earlier, commit `9bbdc0f9`); this re-pin closes
the gap between that pin and C3's own breakdown.

`tests/fuzz/CLAUDE.md` documents the bug for future readers.

## 2. Darwin validation (lane abifin)

Per the brief, build / `make strict CC=gcc-16` / registry DD-11.3
self-oracle were already green this morning and were NOT re-run.
Everything below is new to this lane, each run async with a generous
`timeout`, log paths under this session's scratchpad.

### 2a. uprops

- `bash tests/uprops/run_uprops_tests.sh` (default axis, byte+utf8 in one
  run): **47 passed, 0 failed.** The brief's stated expectation of
  "26/26" does not match this tree's current section count (uprops has
  grown since stage 5 added the script-spelling and Script/scx identity
  cells) — 0 failed is the green criterion and it holds.
- `ENC=utf8 bash tests/uprops/run_uprops_tests.sh` (utf8-only):
  **26 passed, 0 failed — exactly the brief's expected 26/26**, with the
  `[STORE]` coverage line reading `387 of 387 properties this run asks
  about are in the committed store and were compared (exact); 0 are NOT
  covered` — the exact `[STORE] 387/387` line the brief named. (The
  earlier default/combined run in the first bullet reports 47 passed
  because it also runs the byte arm's own §1-§4 cells in the same
  process; the brief's "26/26" was specifically the utf8-only
  invocation, which matches.)

### 2b. rxtsource

`bash tests/rxtsource/run_rxtsource_tests.sh`: **checks passed: 119,
checks recorded: 1, checks failed: 0** — exactly the brief's expected
darwin 119/1/0.

The RECORD line (C3's darwin-vs-Linux-pin comparison) confirms the
re-pin landed correctly:

```
RECORD: C3: population pins are Linux-reference numbers; this box's deltas:
    PASS: got 12729, pinned 13708
    SKIP: got 16118, pinned 15146
    INFO: got 7, pinned 0
    no-python-expression: got 2851, pinned 1875
    perr-python-accepts: got 10, pinned 14
```

The **pinned SKIP value read back is 15146** — the new C3_SKIP this
lane's predecessor commit set — confirming the re-pin is live and
consistent; the `got` numbers differ from the pins for the pre-existing,
documented reason (box/python-version sensitivity, not this fix), same
as every prior `[arm61fix]`/`[ntriage]`-era re-pin.

### 2c. atomic_diff

`bash tests/atomic_groups/run_atomic_diff.sh` (`make test-atomic`'s
script): **checks passed: 8, checks failed: 0.** Every named population
floor held (26 cut / 10 dead-cut / 13 carve-out / 4 control patterns;
61,586 default-engine cells against libpcre2, exact agreement across
`--engine=vm` and `-fno-possessify` arms too; the §3 discharge
differential's 61,586 answer cells identical with/without
`-fno-atomic-discharge`; §4's 19,292 consumed-length cells agree with
libpcre2's `\G(?:PAT)` oracle).

### 2d. utf8 harness (the count confirmation)

`bash tests/harness/run.sh tests/utf8/`, timeout 1800s: **OWED — launched
last per BOILERPLATE's DO-THEN-FINISH (this is the long one; a previous
attempt hit the harness's 300s default and did not complete). See §5 for
the log path and how to read it once done.**

## 3. The utf8 count disposition (I-63: expected 1833, Linux printed 1829, 0 failed)

**The exact ±4 arithmetic, derived from `git log`/`git diff` over
`tests/utf8/` between pins `013e5e03` and `13b56a12` (independent of the
live local run):**

`git log --oneline 013e5e03..13b56a12 -- tests/utf8/` shows exactly two
commits touching the directory in that range, both `[K53-SELRETRY]`
(lane utf8k53):

- `e638afee` — the 16 blocks parked in
  `tests/known_fail/k53_uprops_oversize.rxt` return to their authored
  files: 12 to `axis04_p_categories.rxt` at their canonical
  general-category positions, 4 to `axis12_scripts.rxt`;
  `known_fail/k53_uprops_oversize.rxt` removed.
- `880ba16d` — fixes the move's OWN defect: the splitter used in
  `e638afee` ran its last group to end-of-file, which **duplicated the
  four script blocks (`\p{Unknown}`, `\p{sc=Unknown}`, `\p{scx=Unknown}`,
  `\p{Zzzz}`) into `axis04_p_categories.rxt`** on top of their correct
  home in `axis12_scripts.rxt`. `880ba16d`'s diff on
  `axis04_p_categories.rxt` is exactly a 54-line deletion removing those
  four duplicate blocks (verified directly: `git show 880ba16d --
  tests/utf8/axis04_p_categories.rxt`), each block one `pattern` line
  plus three assertion lines, all four marked `# pcre2-only`.

**I-63's "expected 1833" was measured against the tree at (or including)
`e638afee`'s state — before `880ba16d`'s dedup fix — so it counts the 4
duplicate blocks once each. The correct, de-duplicated corpus that
`880ba16d` leaves at `13b56a12` has exactly 1833 − 4 = 1829 cases, which
is what the Linux run printed. `0 failed` is the green signal: the
corpus is answer-correct, and 1829 (not 1833) is the right number going
forward** — any future re-pin of a "1833" expectation anywhere in the
tree would itself be wrong and should read 1829.

This is confirmed structurally (the exact 4 removed blocks are named and
their content shown above); §2d's live darwin run of
`tests/harness/run.sh tests/utf8/` is corroborating evidence only, marked
owed in §2 and to be filled in by whoever reads the log named in §5.

## 4. C3 re-pin attribution (from d22ca9df, restated here for the record)

Already fully derived and cited in `tests/rxtsource/run_rxtsource_tests.sh`
itself (search `[S5-ARM re-pin`). Summary: the +72 SKIP/+72 pcre2-only
delta from I-61's prior pins (`SKIP=15074/pcre2-only=2872`) to the new
ones (`SKIP=15146/pcre2-only=2944`) is attributed ENTIRELY to
`tests/utf8/axis12_scripts.rxt` (lane utf8s5's new file, 72 `# pcre2-only`
non-ASCII-script-name cells), not to lane pyrole's C3 three-way-verdict
merge (`db142b16`, which touches zero `.rxt` files — verified by `git show
db142b16 --stat | grep -c '\.rxt$'` = 0). `[K53-SELRETRY]`'s own move
(the 16 blocks discussed in §3) is a wash for C3's SKIP breakdown: 462
pcre2-only SKIP in `axis04_p_categories.rxt` before + 44 in the deleted
`known_fail/k53_uprops_oversize.rxt` = 506 pcre2-only SKIP in
`axis04_p_categories.rxt` after — 462+44=506 exactly, zero net C3
movement, because `880ba16d`'s own `CENSUS_*`/`RUNSH_*` re-pin already
absorbed that move at the file/block/line level.

## 5. Owed to the Linux executor: the exact 6 red-stage re-run commands

The S5-ARM Linux run (ubuntubudu, glibc, gcc-15.2, pin `13b56a12`, build
`build/s5_arm_20260911`) hit `dladdr`/`Dl_info` compile failures in six
stages, all traced to the single `pcre2_abi.h` ordering bug §1 fixes.
Re-run each against this lane's commit(s) on `lane/abifix` (after merge,
against `main`):

1. **san** — `make san`
   (on Linux, `CC ?= gcc` resolves to real GCC by default — unlike this
   Mac, no `cc_resolve.sh` shimming needed; see `santriage_report.md` for
   why the Mac needs that and Linux does not.)
2. **registry/PC-3** — `make test-registry`
   (equivalently `bash tests/registry/run_registry_tests.sh`; PC-3 is the
   `pcre2_check` differential built and run inline at
   `tests/registry/run_registry_tests.sh:172-194`.)
3. **pc4** — same command as (2): `run_pc4.sh` is invoked FROM WITHIN
   `run_registry_tests.sh` (`tests/registry/run_registry_tests.sh:374`,
   `bash "$SCRIPT_DIR/run_pc4.sh" 2>&1 | tee "$PC4OUT"`) — PC-3 and PC-4
   are two named sub-stages of the one script, not two separate
   invocations.
4. **uprops_byte §3** — `ENC=byte bash tests/uprops/run_uprops_tests.sh`
   (or the default `bash tests/uprops/run_uprops_tests.sh`, which covers
   both encodings in one run — §2a above ran the default form on darwin).
5. **uprops_utf8 §3** — `ENC=utf8 bash tests/uprops/run_uprops_tests.sh`
   — **the one to watch for the `[STORE] 387/387` line**
   (`tests/uprops/uprops_compare.py`'s `[STORE] coverage: N of M
   properties ... compared (exact)` message); this is the check the
   ordering bug broke by breaking the libpcre2 dlopen build entirely on
   Linux.
6. **atomicdiff** — `make test-atomic` (equivalently
   `bash tests/atomic_groups/run_atomic_diff.sh`).

All six share one root cause (§1) and none needs its own separate
diagnosis — a green run on all six after the merge is full discharge of
the S5-ARM red.

## 6. Status at hand-off

Owed to a follow-up (same worktree, branch `lane/abifix`):
- §2c's atomic_diff run — read `.../abifin_logs/atomic_diff.log`, tail
  for its completion line (script prints a numeric progress counter while
  running; completion is a summary block — see
  `tests/atomic_groups/run_atomic_diff.sh`'s own tail for the exact
  success wording).
- §2d's `tests/harness/run.sh tests/utf8/` run — read
  `.../abifin_logs/utf8_harness.log`; expect **1829 cases, 0 failed**
  per §3's arithmetic (NOT 1833 — that number is stale, see §3).

None of these three affects the fix's correctness (already committed,
unchanged) or the C3/utf8 arithmetic (derived independently in §§3-4 from
`git log`/`git diff`, not from the live runs) — they are corroborating
evidence only, and the exact commands to re-run them if a fresh agent or
the manager needs to are given in full above.
