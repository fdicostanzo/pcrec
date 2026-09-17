# Triage: `battery_20260917_102334`'s `test`-stage red (lane btriage)

Note on the filename: this lane's brief named it `btriage`, matching an
earlier lane (`btriage2`, 2026-09-10) whose own report is already
committed at `docs/dev/lanes/btriage_report.md` — a different battery, a
different date, historical and never edited afterwards per this
directory's own rule. This report uses a date-qualified name instead of
overwriting it.

## Verdict

**The red does NOT block the `cf0962e3` pin. The dial+K59 train is not
defective.** Both failures are stale test-side pins — one a real, intended,
well-documented consequence of the K59 fix that same merge shipped (the
merge's own delivery should have re-pinned it and didn't), the other
pre-existing staleness inherited from an unrelated same-day commit
(`e0bc115b`, lane `cmtfix`, O-31 F1) that also forgot to re-pin one file.
Neither implicates the `--tune`/K59RUNG mechanism itself: `dialtrain_byteid.md`'s
corpus-wide byte-identity sweep already confirmed the train moves no byte
beyond the `RX_TUNE` stamp on the DEFAULT-flags corpus census; both failures
here are in CUSTOM-flag/non-corpus test scaffolding that sweep does not
reach. Both are fixed in this worktree and re-validated locally; a fresh
`make test` on the Linux box would need to confirm ONLY that
`test-resource`/`test-rxtsource` are green (this box's darwin C3 pins are
non-native and RECORD rather than FAIL by design, so my local run cannot
exercise the exact pinned numbers the way ubuntubudu can).

## Per-failure disposition table

| # | test.log location | check | cause | classification | fix |
|---|---|---|---|---|---|
| 1 | `tests/resource/run_resource_tests.sh` (K7 §1, `size_moved` loop) | `'(?:[a-z][0-9]){1,8000}' was ACCEPTED` | K59's new `SDR_NO_PREMUL` drop-ladder rung (`src/core/compile.c`) now fires on EVERY `--tune` position, not just `min-size` — on any DFA-engine artifact refused by the total emitted-size cap that still carries a premultiplied transition table, it retries with `-fno-premul-table`. This witness's old 1,065,432-byte artifact drops to 634,778 and clears the 1,000,000-byte cap. | Real, intended consequence of the K59 fix (verified: the compiler emits `pcrec: note: the emitted-size cap forced a smaller artifact: dropped the premultiplied DFA transition table`). Stale test pin — the merge's own delivery should have re-pinned this row and didn't (`dialtrain_byteid.md`'s corpus sweep only covers default-flags corpus `pattern`/`pattern-esc` lines, not this custom-flag CLI-driven row). | Re-witnessed at a larger count (`{1,8000}` → `{1,13000}`) that still exceeds the cap even with both drop-ladder rungs exhausted (measured 1,034,779 bytes). Fast, safe compile — no K25 risk at this size. |
| 2 | same loop | `'a{5,25000}' was ACCEPTED` | Same mechanism, second witness (`-fno-scan-edge -fno-start-pinned`). Old 1,104,674-byte artifact drops to 769,835. | Same as #1 — real, intended, undocumented pin gap. | **No larger safe witness exists for this shape.** Measured: raising `N` past ~31,500 under these flags moves straight from "still under the rescued size" into 20+ second single-compile stalls before ever regaining the cap (K25's own chain-minimization pathology — `a{m,n}`'s single-byte-class chain is exactly its documented worst case). Two substitute shapes tried under the same flags (a period-2 alternating chain at a comparable count; two independent `{5,16000}` chains concatenated) either hit the same slow zone or fell out of the DFA engine into a work-budget VM fallback before reaching the byte cap at all. Retired this row from the refusal loop; added a dedicated acceptance check asserting the rescue itself (mirroring this file's own [OPT-4.1]/[OPT-4.2] precedent of flipping a cell's assertion when a mechanism generally rescues a shape rather than leaving it silently untested). Row 3 (`(a|b){5,30000}` with `-fprefilter`) is untouched and still refuses at its old size — `-fprefilter` forces the VM engine, which the rung's `fit.chosen == ENGM_DFA` scope structurally cannot reach, so it is a real, ongoing witness that the cap still exists. |
| 3 | `tests/rxtsource/run_rxtsource_tests.sh` (C3 population pin) | `C3: population pin(s) MOVED: PASS: got 13714, pinned 13708` | `e0bc115b` (lane `cmtfix`, [O-31 F1], merged 2026-09-17 04:01 — hours before k59rung's 10:23 merge, on the same day, both ancestors of `cf0962e3`) added `tests/base/comment_escape.rxt` (2 pattern blocks, 6 m/n lines) and correctly re-pinned `CENSUS_*`/`RUNSH_*` (+1/+2/+6, its own commit message says so) but never re-pinned `C3_PASS`. All 6 new lines are plain literal-escape/character-class patterns, fully python-`re`-expressible — isolated confirmation: `python3 tests/harness/verify_rxt.py tests/base/comment_escape.rxt` reports `PASS=6 FAIL=0 SKIP=0 INFO=0` — so the entire delta lands in `C3_PASS` and nothing else moves (`C3_SKIP`/`C3_INFO` unchanged in the battery's own log, matching this isolation exactly). This is **pre-existing staleness inherited into `cf0962e3`, unrelated to k59rung's own diff** (`git show cf0962e3 --stat` touches zero `.rxt` files, only `tune_dial_fixtures.rxtin`, which is excluded from the corpus by extension). It surfaced in THIS battery only because it is the first `make test` run after `e0bc115b` landed. | Stale pin, pre-existing, not caused by the dial+K59 train. | `C3_PASS=13708` → `13714`, with a dated derivation comment following this file's own established re-pin-comment convention (`arm61fix`, `abifix` precedents). |

## Reproduction and validation

Built `build/pcrec` in this worktree with `gcc-16` (`make -j4 CC=gcc-16`,
clean). Direct compiler reproduction for #1/#2 confirmed the exact
mechanism and byte counts before any test-file edit was made (see the
table above). `tests/base/comment_escape.rxt` isolated through
`verify_rxt.py` directly confirms #3's derivation independent of any
box-sensitive aggregate.

Post-fix, targeted section runs on this worktree (not the battery's own
binary — the remote battery was still mid-run at hand-off and the
box-concurrency rule forbids touching it):

- `bash tests/resource/run_resource_tests.sh`: **25 passed, 0 failed**
  (was 20 passed / 2 failed in the battery's log; the count differs
  because row 2 moved from the refusal loop's pass count into a
  dedicated new check, net +5 assertions). Section 2 SKIPs on darwin as
  documented (unrelated to this fix).
- `bash tests/rxtsource/run_rxtsource_tests.sh`: **212 passed, 0 failed,
  1 recorded** (was 211 passed / 1 failed in the battery's log). The one
  `RECORD:` line is the pre-existing, by-design darwin box-sensitivity
  note (`tests/rxtsource/CLAUDE.md`'s "record() / the darwin pin RECORD"
  — this box's raw C3 numbers are non-native and print as a RECORD, never
  a FAIL, so this run cannot exercise the Linux-native pin comparison the
  battery itself did; the isolated per-file measurement above is what
  establishes the fix is correct independent of that).
- `make strict`: not re-run — no `src/` files touched by this lane, only
  two `tests/*.sh` scripts; `strict` (warnings-as-errors on the C tree)
  cannot be affected.

One process note, since BOILERPLATE names it a delivery-cost lesson worth
repeating: my first `run_rxtsource_tests.sh` re-run used
`PCREC=build/pcrec` (relative) as an env override and produced a false
`FAIL: W23-S6 arm 2` — `timeout: failed to run command 'build/pcrec': No
such file or directory`, because that check `cd`s into a scratch
directory before invoking `$PCREC`. Re-ran with `$PCREC` unset (the
script's own default resolves an absolute path via `$ROOT_DIR`) and the
false failure disappeared; this was my own invocation mistake, not a
regression, and is not attributed to either fix above.

Also caught and self-corrected: my byte-count pin for the new row-2
rescue check was off by one (measured 769836 on a scratch file
`/tmp/o2.c` vs. the harness's own `769835` using its actual `o.c`
basename) — the same "different output basename produces a false byte
difference" class this tree has already recorded three times elsewhere
(`w23fix3_report.md` et al.). Caught by running the actual test file
before considering the fix done, not by re-deriving the number by hand.

## A minor, unrelated, out-of-scope observation

`setsid.log` shows `bash: line 14: load3: command not found` three times.
`scripts/battery.sh:124` calls `load=$(load3)` where `load3` is not a
defined function — cosmetic (the trailer's `load=` field prints empty
instead of a number), does not affect any stage's pass/fail, and is
unrelated to the `test`-stage red this brief scoped me to. Flagged for
the manager's awareness only; not fixed here.

## Commits

Branch `lane/btriage`, two commits:

1. `tests/resource/run_resource_tests.sh` — re-witness row 1 at a larger
   count; retire row 2 from the refusal loop and add a dedicated
   [K59-PREMUL] rescue-acceptance check in its place.
2. `tests/rxtsource/run_rxtsource_tests.sh` — re-pin `C3_PASS` 13708 →
   13714 for `comment_escape.rxt`'s 6 python-verifiable cells, with a
   dated derivation comment.

Not merged to main; not pushed. The manager's full battery on ubuntubudu
is the merge/close standard — this lane's own validation used its
worktree's local build, matching the box's own C3 native/non-native
distinction.
