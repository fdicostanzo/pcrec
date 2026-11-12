# kclose5 report: re-pin emit_sweep's UTF8 variant TAG floors

STATE: delivered (branch lane/memfn-kclose)

## Summary

The utf8 cells of `VARIANT_PINS` in scripts/emit_sweep.py were stale on main because of
ebcc10aa1 (lane/trailgc, K134, D183, abi 93: about +1860 B per artifact with a trail
checkpoint; accepted 2026-11-10) plus corpus growth. Re-pinned all five utf8 cells from the
job's pins.py with a dated comment. Byte cells untouched (verified identical to HEAD). No utf8 mover.

## The utf8 job

597-kit-kclose5-utf8 (copy of kclose2's 580 with `--bases utf8`, no r13a compare, hold-only
`--ready`), file /var/tmp/pcrec-pcrec/scratch/memfn/kclose5/jobs/597-kit-kclose5-utf8; dry-run rc=0.
It ran 813 s, rc=0; the queue marked it RED only because the sweep's own tail line
`emit_sweep: DONE rc=1 / VARIANTS: FAILED` (the stale TAG FLOOR lines, expected before the re-pin)
matched its red-line scan. Not a sweep failure: pins.py is complete. Log:
/var/tmp/pcrec-pcrec/scratch/memfn/kclose5/utf8/sweep.log, pins:
/var/tmp/pcrec-pcrec/scratch/memfn/kclose5/utf8/pins.py.

## Measured vs old pins

Population 6,479 rows, movers=0 and asymmetric=0 in every stream (grep of sweep.log), side a
(BASE dc1988069) equals side b (tip) in every TAG FLOOR line. Examples: lowboth/lowsize
no-size-cap 256 -> 410 / 279 -> 439; lowered-cap no-linked-call 100 -> 16; no-backreference
462 -> 421; yes 1302 -> 1255; yes-collapsed 34 -> 26; plain/lowdfa/lowthr no-linked-call 131 -> 132.
Thin-tag manifest witnesses were re-measured too (shortest pattern per tag), as in kclose4.

## Re-pin

scripts/emit_sweep.py `VARIANT_PINS`: the five utf8 cells replaced through pprint width 120,
comment cites job 597, ebcc10aa1 and D183. Script: /var/tmp/pcrec-pcrec/scratch/memfn/kclose5/repin.py.

## Checks

- `make strict` in worktrees/kclose: rc=0 (log .../kclose5/strict.log).
- `python3 -I -m py_compile scripts/emit_sweep.py`: ok.
- scripts/tests/emit_sweep.py.test: rc=0, 28 passed / 0 failed (log .../kclose5/selftest.log).

## Charter-vs-committed checklist

- Job written, dry-run passed, queued: done.
- Re-pin utf8 tag cells only, dated comment: done.
- Any utf8 mover: none (STOP not triggered).
- strict / py_compile / self-test: done, all clean.

## STATE AT HANDOFF

Re-pin committed; strict rc=0; self-test 28/0; job 597 verdict read (mover-free).

OWED: none
