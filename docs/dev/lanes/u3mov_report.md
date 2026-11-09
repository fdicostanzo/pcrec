# u3mov: the U3 declared-movers proof, repaired for the kit's one-call selector

## Summary

Job `main-u3fix-movers` ended `== u3tgt movers COMPLETE: unpredicted 83`. All 83 were the
`simd` cells at `x86-64-v3` (the x86-64 run was `unpredicted 0`), and every one was one shape:
`unpredicted ref line removed '    return rx_reqrun__w16(subject, n, pos);'`. The hypothesis was
right: the kit's final U2 (7fb1fa153) renders the level selector as ONE call, so the ref's
`#if AVX2 ... #elif SSE2 ... #else` chain collapses and the lower rungs' calls go. No answer
changed. `docs/dev/lanes/u3tgt_movers.py` now predicts that move; the full proof is
`unpredicted 0` at both targets (numbers below).

## Cause

Emitted C of `(?i)(cat)s?dog` at `-fmemfn-simd=x86-64-v3`, ref (59846b211-era pcrec, abi 97) vs
lane (abi 98). The ref's selector is a chain: `AVX2 -> return rx_reqrun__w32`, `elif SSE2 ->
return rx_reqrun__w16`, `else -> return rx_reqrun__body`. The lane's is
`return rx_reqrun__w32(subject, n, pos);` alone; `__w16` is still defined and still reached as
`__w32`'s own fall-through. The proof's cutter already dropped the CPU `#if` lines and the
`__body` arm and any arm of an unadmitted level, but not the arm of an ADMITTED lower rung. At
`x86-64` only one rung exists (w16 is the top), so the old rule sufficed. At v3 the w16 arm is a
lower admitted rung. The kit declares this form (`u2_report.md`: "the selector is one call to
the top admitted rung, or `__body`"; `u3floor_report.md`: routing_shape accepts the one-call
level selector). Not an undeclared move.

## Fix

In `judge` (simd mode) the cutter now reads, off the LANE text, the level each selector calls
(`    return <fn>__wNN(subject`; the maximum per helper family) and accepts the removal of a ref
selector arm `return <fn>__wMM(` iff `MM` is below that top. It also rejects a lane selector
that calls a level above the top of the lane's own `MEMFN_FORMS`. The expected text is thus the
kit's own rendered call, not a typed copy. The planted-line control is untouched and runs on
every compiled cell.

## Answer check

Three patterns (`(?i)(cat)s?dog`, `((?i:abc))`, `(?i)(ca)tx+z`; the corpus's `(?i)(ca)t\1` and
`(?i)(?>abc)` need modules the bare CLI lacks here), each compiled with `--emit-main` at
`-fmemfn-simd=x86-64` and `x86-64-v3`, run on 4-5 subjects each (short, 70-byte-padded front,
back and both, so the w32 path runs), compared with python `re`: 86 comparisons, 0 differences
(`scratch/u3mov/chk.py`).

## STATE AT HANDOFF

Rulings applied: none later than the brief (`u3tgt_rulings.md` R1-R5 predate this lane).
Validation COMPLETE. The proof re-run directly (nice, timeout 1800, --jobs 8) at tip 15d32cebe plus
the script edit, ref = the scratch abi-97 build: `u3tgt_movers.py REF LANE TREE x86-64` and
`... x86-64-v3`, each 5095 patterns, all 8 cells `unpredicted 0` (simd cells serve 26/24/16/17),
`== u3tgt movers COMPLETE: unpredicted 0` twice (scratch/u3mov/full.log). The brief's owed queue
job `main-u3floor-movers` is already queued and needs no change. Nothing else owed.

R6 applied (rulings R1-R6, last R6): merged lane/memfn-u2 6aa26ba77 alone (conflicts only in the two
index/notes files, both sides kept); deleted `#define MF_P_PORTABLE_ONLY` (its one reader,
tests/memfn/policy_check.c, now passes 0, the art's unread policy argument); reworded the
run_sabotage_matrix.sh simdfloor comment ISA-free. On the merged tip: `make strict` rc 0,
`make test-memfn-arch` 17/0, `make test-memfn-finder` 3321/0, and the movers proof re-run at both
targets `unpredicted 0` (scratch/u3mov/full2.log).
