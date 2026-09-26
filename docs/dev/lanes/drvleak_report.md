# drvleak — driver.c's `vars` leak (2026-09-26)

## Task

Linux `make asan` at `fe233552` (defect present on `main` too) went red in the
harness section: LeakSanitizer reported a 48-byte direct leak from
`calloc` at `tests/harness/driver.c:423`, and all 81 case failures were in
`tests/vars/{basic,caseless,unset}.rxt`. Hypothesis to confirm: the leak is
the single root cause of all 81 (LSan's nonzero exit replacing the driver's
real exit status).

## Root cause, confirmed

`driver.c`'s `vars` array — one `rx_var` per `${name}` binding on
`argv[5..]`, `calloc`'d at what was line 423 — was freed on only 3 of
`main()`'s 9 exit paths: the two early failures inside the binding-build
loop (`!vb`, `!buf`) already freed it; the `mode_count` find-all loop's two
returns, the caller-buffer allocation-failure path, the `_in`-entries
cross-check's `bad` exit, and the two ordinary end-of-`main` returns
(give-up and match/nomatch) did not.

**A second, narrower leak rode along in the same allocation and was NOT
named in the LSan trace**: each SET binding's decoded value
(`decode()`'s own fresh `malloc`, stored at `rx_var.p`) is a *separate*
allocation from the `vars` array itself, and was never freed anywhere in
the file. Found by reading every write to `.p`, not assumed from the bug
report.

Confirmed directly (not inferred) with macOS's own `leaks(1)` tool against
a real var-bearing artifact (`^${v}$` under `--features vars`), since this
Mac cannot run LeakSanitizer's leak detector at all (see "Darwin
validation" below):

- **before the fix**: `2 leaks for 48 total leaked bytes` — the `calloc` at
  `driver.c:423` (root leak) plus one `<malloc in decode>` (16 bytes, the
  bound value `"hello"`).
- **after the fix**: `0 leaks for 0 total leaked bytes`.

## Fix

`free_vars(rx_var *vars, size_t nvars)` (declared beside `parse_route`,
before `main`): frees each populated slot's `.p` (an UNSET slot's is
already `NULL` — a no-op) then the array itself. `nvars` is exactly right
at every one of the loop's own early-failure returns too, because
`calloc` zero-initializes every slot at or above the current count.

Called at every exit from the `vars` allocation onward (the two loop
failures already had `free(vars)` and now call `free_vars` instead; six
more sites gained the call: the `mode_count` give-up and success returns,
the caller-buffer OOM path, the `_in` cross-check's `bad` exit, and the
two ordinary end-of-`main` returns).

The misleading comment above the allocation ("outlives the call by
construction ... without a second allocation policy") is rewritten to
state the actual lifetime rule: a fresh `decode()`-malloc'd copy, freed by
`free_vars` on every exit path.

## Sibling drivers — grepped, and the false positives are worth recording

Grepped every `tests/**/*.c` with a `main()` for the same shape (calloc/
malloc assigned to a name never later passed to `free(...)`). First pass
used a naive variable-name regex and produced several false positives —
`cx.job`/`cx->job` calloc sites in `tests/mrl/cwmax_check.c`,
`tests/parse/branch_count_check.c`, `tests/registry/definitions_check.c`
and `tests/registry/definitions_oracle_gen.c` all read as "never freed"
because the regex didn't extract the struct-member lvalue — each of these
already has a proper `release(cx)` / `pcrec_arena_free(&cx.arena); free(cx.job)`
pair at every exit. Re-checked by hand: no leak.

**Two real, trivial, same-class defects found and fixed alongside the
main one** — the exact "two `calloc`s checked together, only one freed on
the shared OOM path" shape driver.c's own `frames_mem`/`trail_mem` check
already gets right:

- `tests/registry/definitions_oracle_driver.c` — `caps_a`/`caps_b`'s
  shared OOM check didn't free either on failure.
- `tests/thread/ts2_driver.c` — `tids`/`args`'s shared OOM check didn't
  free either on failure. `tests/thread/` is deliberately excluded from
  `ubsan`/`asan`/`san` (the TSan-vs-ASan non-composition reason, Makefile),
  so this fix has no sanitizer-battery consequence — it's a correctness
  tidy-up only, not a finding.

Everything else found by the grep (`tests/uprops/uprops_oracle.c`,
`uprops_sweep.c`, `tests/bench/compare/eng_pcre2.c`,
`tests/recursion/d27/sr_driver.c`, `tests/fuzz/pcre2_oracle.c`,
`tests/thread/ts3_driver.c`/`ts4_driver.c`) genuinely never frees its
buffer(s) at end of `main`, but NONE of these files is reachable from
`tests/lib/san_scripts.txt` (checked each by name; `tests/thread/` is
excluded wholesale, `tests/uprops/`/`tests/bench/`/`tests/fuzz/pcre2_oracle.c`/
`tests/recursion/d27/sr_driver.c` are not in the list and `sr_driver.c`
has no runner script referencing it at all today) — not fixed, flagged
here rather than silently patched, since none is "clearly trivial" in the
same sense (several hold `Job`/`Ctx` state whose correct teardown isn't
obvious without reading each file's own arena-ownership contract).

## Darwin validation — why no local LSan run

`ASAN_OPTIONS=detect_leaks=1` **hangs unconditionally** on this box
(gcc-16 16.2.0/arm64), leak or no leak — reproduced live (had to
`scripts/safekill` the process): this is K54's already-documented
Darwin-LSan-hangs-at-exit defect, which is exactly why the Makefile's
`SAN_DETECT_LEAKS` derivation forces `0` on Darwin (`ifeq
($(UNAME_S),Darwin)`). So `make asan` on this Mac never runs the leak
tier at all, and forcing `detect_leaks=1` by hand just hangs — confirmed
with the FIXED driver.c too (the hang is unconditional, not leak-gated).

Used macOS's native `leaks(1)` tool instead (codesigned the driver
binaries with `com.apple.security.get-task-allow` to get past the
"process is not debuggable" restriction) — see the before/after counts
above. This is a genuine, independent confirmation of the root cause and
the fix, on a different instrument from LSan.

## Validation

- `bash tests/harness/run.sh tests/vars/` — **83/0** (unchanged from
  before the fix; the leak never affected any answer, only exit-code
  fidelity under LSan).
- `bash tests/rxtsource/run_rxtsource_tests.sh` — **255 passed / 1
  recorded / 0 failed**, `INV-COMPAT holds over 220 files / 4016 blocks /
  29224 expectation lines` (untouched by this change; run to confirm the
  driver.c comment edit didn't move anything the census counts).
- `make strict CC=gcc-16` — clean (`-Werror -Wshadow`, whole tree).
- `make -j4 CC=gcc-16` — clean build.
- `make test CC=gcc-16` — **LAUNCHED DETACHED as this lane's last act**
  (`nohup ... > /tmp/drvleak_make_test.log 2>&1 < /dev/null & disown`),
  confirmed alive and doing real work (compiling `driver.c` against
  generated matchers under `tests/assertions/`) ~90s in. **OWED**: read
  `/tmp/drvleak_make_test.log`'s tail for the `sections ran: N/M` trailer
  and any `*** [test-X] Error` line (docs/dev/learnings.md §3's rule: the
  verdict is that line, never "sections ran" alone and never a `FAIL:`
  grep). Expected wall time ~100 min per BOILERPLATE's own Mac figure.

## No abi impact

`driver.c` is test infrastructure — never compiled into an emitted
artifact, never shipped. Confirmed: nothing under `src/gen/` or
`lib/pcrec.h` touched, `rx_info`/`PCREC_ARTIFACT_ABI` untouched. No
`docs/spec/` hunk owed (D80 applies to caller-observable pcrec surface;
this is test-harness-only).

## Docs updated in the same change

- `docs/testing.md` — new "Sanitizer findings inventory" entry **F2**
  (the first since F1, 2026-08-13), with the K54/Darwin-can't-run-LSan
  caveat stated inline so a future reader doesn't re-attempt
  `detect_leaks=1` locally and hit the same hang.
- `tests/harness/CLAUDE.md` — a dated `[VAR fix, 2026-09-26, lane
  drvleak]` paragraph appended to the `driver.c` entry, pointing at F2 for
  the full mechanism.

## Commits

Single commit on `lane/drvleak`, `6767a93e`:
`tests/harness: fix driver.c's vars-array leak (LSan, 81 vars failures)`.

## Handback

Sent to `main` before this turn ends; `make test`'s completion is the one
owed item, log path above.
