# [TT-7] combined ASan+UBSan axis — evidence memo

Written 2026-08-23, lane/tt7san, gcc 15.2.0 (Ubuntu 15.2.0-16ubuntu1), 12-core
box. Prepares `make san` (Makefile, next to `ubsan:`/`asan:`) for the
manager's timing run; this memo carries the evidence steps 2-4 of the brief
asked for. The ADOPTION DECISION ITSELF IS PENDING — see "Status" at the
bottom.

## What was built

`make san` — a THIRD separate tree, `build-san/` (gitignored like
`build-ubsan/`/`build-asan/`), both axes instrumented (compiler via
`SANFLAGS`, every generated matcher via `GENCFLAGS`), same 26-script suite
list and `tests/thread/` exclusion `ubsan`/`asan` already use (same TSan
reason, `Makefile:576-580` — combining ASan/UBSan with an already-TSan'd
build is not how these compose on this toolchain; that reasoning says
nothing about ASan+UBSan combined with EACH OTHER, which is the routine,
well-supported case this target exercises). `ubsan:`/`asan:` are untouched.

```
SAN_CFLAGS := -O1 -g -fsanitize=address,undefined,leak -fno-sanitize-recover=undefined
```

**Reconciling the two single-axis CFLAGS** (`UBSAN_CFLAGS` at
`Makefile:585`, `ASAN_CFLAGS` at `Makefile:638`): beyond their sanitizer
lists, the two differ in exactly one flag — `UBSAN_CFLAGS` carries
`-fno-sanitize-recover=undefined`, `ASAN_CFLAGS` does not. That flag only
affects the `undefined` sanitizer (meaningless to `address`/`leak`), so it
carries into the combined flags unconditionally: it keeps UBSan's
first-hit-abort-with-a-stack-trace property (the same reason `ubsan:` itself
sets it) without changing ASan/LSan's behavior. Both single axes already
share `-O1 -g`, so there was nothing else to reconcile. `SAN_ENV` exports
BOTH single axes' `*_OPTIONS` together
(`UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=1"`,
`ASAN_OPTIONS="detect_leaks=1"`, `LSAN_OPTIONS=""`), which was a real
(if unremarkable) wiring step neither single-axis env needed to do alone.

## 2. Diagnosis distinctness — verified in the failing direction

Per the box rule, all of this was small-scale (single-file compiles, one
generated matcher), never a suite run. Full commands are reproducible —
compile with `SAN_CFLAGS` exactly as `make san` would, run with `SAN_ENV`'s
`UBSAN_OPTIONS`/`ASAN_OPTIONS`/`LSAN_OPTIONS` exported.

### Scratch programs (three tiny `main()`s, `-Wall -Wextra -std=gnu11` + `SAN_CFLAGS`)

| sabotage | report header | exit |
|---|---|---|
| signed overflow (`INT_MAX + argc`, both operands `volatile` so gcc can't fold it) | `runtime error: signed integer overflow: 2147483647 + 2 cannot be represented in type 'int'` — named UBSan's own class, `#0 ... in main ub_overflow.c:6` | 1 (fatal, `-fno-sanitize-recover=undefined` working) |
| heap overflow (`malloc` a runtime-sized 8 bytes, `memset` 9) | `AddressSanitizer: heap-buffer-overflow` ... `WRITE of size 9` ... `0 bytes after 8-byte region` | 1 |
| leak (`malloc(12345)`, K26's own canary size, never freed) | **no report**, silent | 0 |

The heap-overflow case needed one iteration: at `-O1` the first version
(write, `free`, no read) compiled clean and exited 0 — gcc's dead-store
elimination legally erased the unobserved write before ASan's
instrumentation ever saw it, the exact "one measured gotcha" already on
file in `docs/testing.md`'s sabotage-validation section for the single-axis
targets. Adding a `printf` that reads the overflowed byte back (forcing the
write to be observed) reproduced the report above. Recorded again here
because it is not this target's own bug — it is the flag level (`-O1`) both
single axes and the combined axis share.

**The leak result is K26, not a new gap.** `docs/dev/known_issues.md` K26:
LSan is a documented no-op on THIS box (`/proc/sys/kernel/yama/ptrace_scope`
is 1, the suspected cause) — a control leaking K26's own canary size exits 0
under the single-axis battery's exact `ASAN_OPTIONS`/`LSAN_OPTIONS` too.
Re-ran the identical 12,345-byte canary under `SAN_CFLAGS`/the combined
`SAN_ENV`: same result, exit 0, no report, `ptrace_scope` confirmed `1`.
**Combining the axes neither fixes nor worsens K26** — the leak tier is
still not exercising anything, under one axis or two, on this host.

### The real path — a generated matcher + `tests/harness/driver.c`

```
build-san/pcrec -p rx -o gen.c -- 'a(b|c)+d'
cc -O1 -std=gnu11 -Wall -Wextra $SAN_CFLAGS -I. -o t tests/harness/driver.c gen.c
```
(the `GENCFLAGS` shape `SAN_ENV` sets — matches `ubsan:`/`asan:`'s own
`-O1 -std=gnu11 -Wall -Wextra $(UBSAN_CFLAGS|ASAN_CFLAGS)` pattern.)

Clean run, unmodified `driver.c`: `./t "abcd"` -> `match 0 4 2 3` (exit 0),
`./t "aXd"` -> `nomatch` (exit 0) — both correct against the pattern.

Then three COPIES of `driver.c`, each with one sabotage planted right after
`int main(int argc, char **argv) {`, compiled the same way and linked
against the same `gen.c`:

| copy | sabotage | result |
|---|---|---|
| `driver_ub.c` | forced-observable signed overflow (`volatile`-sourced) | UBSan: `runtime error: signed integer overflow: 2147483647 + 2 ...`, names `driver_ub.c:143`, exit 1 |
| `driver_heap.c` | heap-buffer-overflow, made observable (`fprintf` reads the overflowed byte, same gotcha as above) | `AddressSanitizer: heap-buffer-overflow`, `WRITE of size 10`, names `driver_heap.c:143` and the `9-byte region` it overran, exit 1 |
| `driver_leak.c` | `malloc(12345)` (K26 canary size), never freed | exit 0, no report — K26 reproduces through the REAL generated-matcher compile path too, not just the scratch programs |

**Distinctness holds through the real path**: the UB and the memory-safety
sabotage each get their own tool's report and diagnostic class, with the
right file/line, and both are still fatal under the combined flags. The
brief asked for "one UB and one leak" through the real path; the leak half
reproduces K26 rather than a fresh finding, so a heap-overflow was run
alongside it to confirm ASan's OWN report (not just UBSan's) is reachable
end-to-end through a real generated matcher under the combined axis, not
only in an isolated scratch program.

## 3. Budget check — D45 stays byte-identical under the combined flags

`tests/lib/gen_timeout.sh`'s four budget functions key off the LITERAL
SUBSTRING `-fsanitize=` in `GENCFLAGS`/`CFLAGS`/`TSANFLAGS`/`SANFLAGS`
(`case " ... " in *-fsanitize=*) ... esac`) — a boolean axis check, not a
per-sanitizer one. Sourced `tests/lib/gen_timeout.sh` directly and called
each function with `GENCFLAGS` set to four cases:

| `GENCFLAGS` | `gen_timeout_secs` | `gen_cpu_secs` | `pcrec_timeout_secs` | `gen_run_secs` |
|---|---|---|---|---|
| unset (plain) | 60 | 10 | 20 | 10 |
| `-fsanitize=undefined -fno-sanitize-recover=undefined` (ubsan-shaped) | 180 | 60 | 60 | 60 |
| `-fsanitize=address,leak` (asan-shaped) | 180 | 60 | 60 | 60 |
| `-fsanitize=address,undefined,leak -fno-sanitize-recover=undefined` (`SAN_CFLAGS`, TT-7) | **180** | **60** | **60** | **60** |

**The combined flags land on the exact same sanitizer-axis numbers as
either single axis, byte-identical, all four functions.** This was
chain_profile.md candidate (a)'s own stated expectation ("no gen-timeout
work needed") — now measured directly against the real function calls
rather than read off the glob pattern.

**Hypothesis for the manager's timing run** (open question, not answered
here — the box rule blocks running the suite this lane): instrumented code
under BOTH tools is plausibly slower per-compile and per-run than under
either alone, even though the BUDGET stays the same. If the combined axis's
real wall/CPU cost exceeds what the shared 60s/180s ceiling assumes by a
wide enough margin, cases that pass comfortably under `ubsan` or `asan`
alone could start landing close to the budget under `san` — a real risk
worth watching in the timing run's own suite-pass results (any D45 failure
naming a case is the signal), not assumed here. Quantitatively: if a
combined compile costs "ASan alone plus a UBSan delta" (chain_profile.md
§4a's own unmeasured hypothesis, ~45-55 min for the suite pass vs. today's
75 min for two passes), that is still comfortably inside the existing
60s/180s per-compile ceiling — the SUITE-level wall estimate and the
PER-COMPILE budget are different quantities, and only the timing run
settles the former.

## 4. The one-line measurement for the manager

On `main`, after [TT-6] merges, box free:

```
gnutimeout 5400 /usr/bin/time -v make -j12 san > build/san_m1.log 2>&1
```

**Baseline to compare against, same HEAD, back to back:**

```
gnutimeout 5400 /usr/bin/time -v make -j12 ubsan > build/ubsan_m1.log 2>&1
gnutimeout 5400 /usr/bin/time -v make -j12 asan  > build/asan_m1.log 2>&1
```

**Pass criteria:**
- `san` wall time < `ubsan` wall + `asan` wall (today's two-pass total —
  75m00s at m65, per `docs/dev/chain_profile.md`'s measured trend; use
  whatever this run's own ubsan+asan total is, not the stale m65 number, in
  case the trend in chain_profile.md §1a — ubsan +19%/asan +24% in one day —
  has continued).
- Zero sanitizer reports across the `san` run (the suite's own PASS/FAIL
  scan already enforces this the same way `ubsan`/`asan` do).
- Suite counts (pass/fail/skip per script) identical to `make test`'s own
  counts for the same HEAD, modulo the fixed, pre-existing exclusions
  (`tests/thread/`, `make bench`/`mech`/`fuzz`, `tests/spec_mod0/`,
  `tests/probes/` — unchanged from `ubsan`/`asan`).

If `san` wall ends up ≥ `ubsan` wall + `asan` wall, the combination loses
and the candidate is a NO — recorded as chain_profile.md's own framing of
the failure condition.

## Status

**PENDING** — this lane built and small-scale-verified the target and its
distinctness/budget properties; it did NOT run the full suite (box rule).
The manager's timing run above is the only evidence that can flip this to
ADOPTED or DECLINED. Until then `docs/testing.md`'s "[TT-7] combined axis"
subsection and this memo both read PENDING, and `ubsan`/`asan` remain the
battery's sanitizer stages.
