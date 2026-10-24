# Lane iteropt: per-call overhead of `<prefix>_next` and `<prefix>_next_n`

Lane iteropt (opus), 2026-10-22, on lane/iteropt from lane/i2build bed4bef84 (abi 84,
provisional). Build go: Frank, 2026-10-22, "let's do the optimization of next and next_n and
see where we are". RX_FOREACH is not changed. Diagnosis read from
`lane/findbench:docs/dev/lanes/fbdig_report.md` (causes a-e).

## 1. What changed (src/gen/emit_iter.c; text inside the scaffold bracket)

1. **(a) The canary.** A NULL `capture_spans` now goes to a new
   `static __attribute__((noinline)) int <p>__one_local(rx_iter *)`. This is the one function
   that declares the NCAPS-pair stack buffer. `_next` and `_next_n` declare no local array,
   so Ubuntu gcc's default `-fstack-protector-strong` puts no canary on them. `_next_n`'s
   NULL-caps arm is its own loop over `<p>__one_local`. `__one_local` writes group 0 of its
   buffer: under the part layouts, gcc -O1 `-Wmaybe-uninitialized` cannot see the search
   write it (tests/partlayout `werror` found 4 shapes).
2. **(b) Double init plus an out-of-line `__enter`.** `rx_iter_init` writes every field: the
   setters' neutral values, `rc` 1 and `flags` 0. gcc already wrote all nine fields at init,
   zero-filling the undefined ones; this makes them defined. `<p>__enter` therefore no longer
   writes `lo`/`vars`/`nvars`/`bufs`/`rc`/`flags` a second time. It is now `static inline`:
   one header store, plus the bind checks where they exist.
3. `<p>__one`'s text is UNCHANGED, so `run_one_body.sh` holds without a re-pin.

**Contract.** match_api.md §3.8¶5's last sentence was "Every field `RX_ITER_INIT` does not
write may hold any value before the first call". It now says that `RX_ITER_INIT` writes
every field. The shared block's quoted `rx_iter_init` line was updated to match (D80).
- The dirty arm (tests/findall/iter_drv.c) now checks that the init overwrites a 0xA5 struct
  with the neutral values, then holds the answers to I's.
- S1303 was re-aimed: its plant is now the init writing `lo = 1`.
- S1309/S1310/S1311/S1313 anchors followed the `_next_n` loop line.
- The partlayout census `writers.tsv` gained the `__one_local` noinline row and the
  `__enter` static-inline row.
- No answer moves for a caller using `RX_ITER_INIT`.

**abi.** The change is folded into 84, with no bump. Reason: abi 84 is lane i2build's
unlanded event, so these bytes ride the same event (abi_changelog 84 entry extended).

## 2. Instructions per cause (instructions:u, cpu7, the fbdig twin cells, fbdrv_clamp)

The columns are:
- base: bed4bef84;
- +(a): the canary fix only;
- +(a)+(b): final, identical to the delivered compiler.

Few-match cells are per find-all; dense cells are per match.

| cell | unit | I base | I +(a) | I final | N1 base | N1 final | N4 base | N4 final | N64 base | N64 final | F base | F final | LOOP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c2-e | find-all | 141 | 135 | 116 | 166 | 132 | 168 | 133 | 168 | 133 | 196 | 162 | 99 |
| c2-b | find-all | 166 | 160 | 141 | 190 | 157 | 192 | 158 | 192 | 158 | 220 | 187 | 124 |
| c2-a | find-all | 261 | 248 | 229 | 311 | 264 | 277 | 233 | 277 | 233 | 370 | 323 | 219 |
| c5 | find-all | 238 | 222 | 206 | 278 | 239 | 243 | 205 | 243 | 205 | 337 | 298 | 188 |
| c7 | find-all | 454 | 433 | 414 | 538 | 481 | 459 | 409 | 459 | 409 | 578 | 524 | 418 |
| c8 | find-all | 207 | 200 | 181 | 235 | 204 | 238 | 208 | 240 | 208 | 280 | 249 | 165 |
| c1-4k | match | 124.1 | 117.1 | 117.1 | 152.1 | 139.1 | 123.3 | 112.8 | 111.8 | 101.8 | 121.0 | 111.0 | 127.1 |
| c3-4k | match | 139.2 | 132.2 | 133.1 | 162.2 | 154.2 | 132.7 | 125.7 | 121.0 | 113.9 | 130.5 | 123.4 | 138.1 |
| c4 | match | 168.1 | 167.1 | 168.1 | 192.1 | 189.1 | 163.3 | 161.3 | 151.9 | 149.8 | 161.0 | 159.0 | 159.1 |
| c6 | match | 99.0 | 92.0 | 93.0 | 129.0 | 115.0 | 100.3 | 94.0 | 88.8 | 84.7 | 98.0 | 93.8 | 78.0 |
| d-dig | match | 86.0 | 78.0 | 79.0 | 110.0 | 100.0 | 80.5 | 74.5 | 68.8 | 63.7 | 77.9 | 72.8 | 86.0 |
| d-word | match | 136.0 | 129.0 | 130.0 | 161.0 | 151.0 | 130.8 | 122.5 | 118.8 | 110.8 | 127.9 | 119.9 | 135.0 |

Per cause:
- **(a) canary:** -7 per match on every dense cell except c4 (-1; the VM `(a)`, whose body
  is large), and -6 to -16 per find-all.
- **(b) init + inline enter:** about -19 per find-all on every few-match cell. Per match it
  is +-1, which is code-shape noise from the inlined enter.
- **(c) state through memory, and (e) `_next_n`'s k-loop spills: NOT fixed.**
  - What remains in `pa_next` (disassembly): 6 callee-saved pushes, `it`/`caps` spilled
    around the memchr call, the header check, and `lo`'s load and store.
  - What remains in `pa_next_n`: `it`, `k`, `i` and the entry pointer live on the stack
    across the search call.
  - N1 is still about 20 per match above I.
  - The fix would be a cursor-locals restructure (`__step` takes `s, n, &lo, &flags`). It
    changes `<p>__one`'s text, which breaks the run_one_body gate (ruling R1), so it is a
    manager ruling, not this lane's.
  - Two cheaper variants were measured and NOT adopted:
    - `_next_n` over a local copy of the iterator: N1 +17 per match, N64 +-3.
    - A pointer-bounded loop: N1 +3 to +8 per match, N64 -1 to -10 per match.
    Both are mixed, and N1 is the bench's worst cell.
- **(d) pd's non-tail call: NOT fixed.** `pd_next` calls `pd__find` out of line, because the
  attempt route's label-table body is `noinline` (`find_body_shared`, a layout decision).
  The K75 advance runs after it, so the call cannot be a tail call. c6 I is 93 per match
  against LOOP 78. Closing it means inlining a body gcc cannot copy, which is a layout
  question.

## 3. Predictions for the re-run (job 598; same cells as 590)

Wall time should move about in proportion to the instruction deltas above. That holds
except where the cell is memchr-bound (c1-1m, c3-1m: the per-match delta is the same,
the share smaller).
- **I:** -5% to -8% per match on dense cells (c4 about 0), and -12% to -18% on few-match
  cells (fixed cost).
- **N1:** -6% to -11% per match; -15% to -21% on few-match cells. It stays above I by about
  20 per match (cause e).
- **N4 / N64:** -5% to -9% per match; -13% to -21% on few-match cells.
- **F (RX_FOREACH), see below:** -5% to -8% per match; -10% to -17% on few-match cells.
- **LOOP:** unchanged, because its instruction counts are identical.
- **Verdict lines (in instructions; the bench reads wall time):**
  - I vs LOOP flips to I ahead on c3, d-dig, d-word and c7. I was already ahead on c1.
  - It stays behind on c2, c5, c8 (fixed cost 16-18 above LOOP), c4 (+9 per match) and c6
    (+15 per match, cause d).

## 4. RX_FOREACH

I did not touch it. F calls `_next_n`, so it inherits both fixes:
- per match: c1 121.0 to 111.0, c6 98.0 to 93.8, d-word 127.9 to 119.9;
- per find-all: c2-e 196 to 162, c7 578 to 524.

On the dense cells F is now below LOOP on c1, c3, d-dig and d-word. It ties LOOP on c4
(159.0 against 159.1) and stays above it on c6 (93.8 against 78.0, cause d). On few-match cells it is still the most expensive arm (about +45-60 per find-all
over I), which is RX_FOREACH's own begin/pull bookkeeping.

## 5. Gates

All of these are on 41b6f048c+; logs are in build/iteropt/logs/:
- `make test-findall`, which includes run_one_body.sh and the ASan cells: green;
- run_residual_twins.sh: green;
- `make test-encseam`: green;
- `make test-partlayout`: green;
- `make test-codegen` (run_entry_shape_identity.sh) and `make test-assertions`
  (run_gstart_identity.sh): RUNNING at handback, detached; logs
  build/iteropt/logs/codegen.log and assertions.log (read with scripts/verdict). OWED;
  job 597's full `make test` covers both;
- `make strict`: clean;
- the sabotage anchors of S1300-S1321: each found exactly once, `VALIDATE_ONLY` 16/16.
  The rows themselves were NOT re-run (OWED: mech).

## 6. Mover census vs bed4bef84

Method: `build/iteropt/h/census.py` compiles every distinct corpus pattern with the bed4bef84
compiler and the delivered one, at the default engine, `--engine=vm` and `-e utf8`. On each
moved artifact it undoes this lane's five text edits. The result must be byte-identical to
bed4bef84's. The edits undone are:
- the init line;
- `static inline` on `__enter` and its five normalization lines;
- the `__one_local` function;
- `_next`'s NULL test;
- `_next_n`'s loop.

Any residue is a mover outside the iterator. The undo was checked on the six measured
artifacts (pa, pw, pc, pd, pg, pl): each one restores bed4bef84's text byte for byte. The
corpus run is RUNNING at handback, queued after codegen in the same detached chain. Its
log is build/iteropt/logs/census.log, which prints counts per arm of
identical/iter-only/OTHER/okdiff. Any OTHER or okdiff pattern is listed in
build/iteropt/census/other.txt. OWED: read it; zero OTHER is the gate.

## 7. OWED

- The codegen, assertions and census results (§5, §6): a detached chain, still running.

- The full `make test` for lane/iteropt: armed as boxqueue job 597-iteropt-test, not yet run.
- The mech rows S1303, S1309, S1310, S1311 and S1313. Their anchors moved; the rows
  must be re-run to show DETECTED.
- The findbench re-run, job 598-findbench-parity-opt: staged on lane/findbench and
  dry-run checked, NOT queued.
- docs/design/findall_iter.md's IT1 row still says the bind writes the optional fields. It
  is the design record; the spec is updated. The manager decides whether the record gets
  an addendum.
- A manager ruling is needed for causes (c)/(e): a cursor-locals restructure re-pins
  run_one_body.
- Cause (d) is a layout question: the attempt body's `noinline`.
- At the landing, the history index entry below must move to main's
  `docs/dev/history/claude_md/docs__dev__lanes.md`. This branch predates that file.
