# u2fix: refuse unnamed policy bits (kit request R-37, fix to unit U2)

## Summary

`mf_define` at `MF_TARGET_REQUIRED` now refuses ANY site policy bit outside the kit's named policy set,
naming the unknown bits in hex, in place of the bit-0-only refusal. compose.c no longer mentions
`MF_P_PORTABLE_ONLY`, so pcrec can delete that `#define` in the joint merge (sheet item 8). At the
default switch (0) nothing moves.

## The change

- memfn/src/kit.h: `MF_P_KIT_NAMED` (= `MF_P_INLOOP | MF_P_SIZE_LEANING`), declared once beside
  `MF_TARGET_REQUIRED`, with a `_Static_assert` that the named bits are distinct single bits and bit 0
  stays out. A new named bit joins this one line. The switch's comment says what is refused.
- memfn/src/compose.c `define_sel`: `policy & ~MF_P_KIT_NAMED` refused with
  `mf_define: policy bits 0x%x are not in the kit's named set 0x%x`.
- memfn/src/gate.c: its two `~(MF_P_INLOOP | MF_P_SIZE_LEANING)` literals now read `MF_P_KIT_NAMED`
  (class OTHER and the refusal can no longer name different sets).
- memfn/include/memfn.h: the `MF_P_PORTABLE_ONLY` comment says no kit code reads it (the define stays).

## Sheet amendment

u2_report.md sheet item 11 amended in place (refusal of unnamed bits; item 8's delete now possible).
Deviations item 16 added.

## Sabotage row

S3000 (new; ids from S2995 up were grepped in main and every worktree, S3010-S3012 are taken elsewhere,
S3000 was free): the refusal is dropped (`if (0 && ...)`). DECLARED UNDETECTED: at the default switch the
line is not reached, and at 1 test-memfn-finder/arms are red before and after (pcrec's arts), so no
committed check tells the plant apart. Closing check: a kit test defining a site with a planted bit under
the switch at 1. Hand run at `MF_TARGET_REQUIRED 1` in a scratch copy with the planted bit `1u<<7` in
g2_simd_gen.c: unplanted, the generator fails with the refusal (hex in the message); with S3000 planted the
message count is 0 (the bit is taken and the site renders no SIMD, a different G2 failure).

## Checks run

All niced, `-j2`, on worktrees/u2 (default switch 0) unless marked scratch.

| check | verdict |
|---|---|
| `make -j2`, `make strict` | green |
| `tests/memfn/run_arch_blind.sh` | 17/0 |
| `make test-memfn-finder` (form hashes) | rc 0 |
| `make test-memfn-arms` (C5 pins) | rc 0 |
| `make test-memfn-g2` (quick; G2 window in it) | rc 0 |
| scratch, switch 1: test-memfn-finder | rc 2; 2310 failed, 1163 passed: identical to u2_report |
| scratch, switch 1: test-memfn-arms | rc 2; 343 failed, 33 passed: identical to u2_report |
| scratch, switch 1: failure classes | only "the art states no target" (159 + 201 lines), same counts as before; no new class |
| scratch, switch 1, bit `1u<<7` planted | refused: `policy bits 0x80 are not in the kit's named set 0x6` |
| S3000 by hand (scratch, switch 1) | refusal gone (0 messages), as declared |

## Charter-vs-committed checklist

| charter item | where |
|---|---|
| general refusal at the named set, hex in the message | compose.c, kit.h |
| mask declared once with a static assert | kit.h `MF_P_KIT_NAMED` |
| compose.c free of `MF_P_PORTABLE_ONLY`; memfn.h comment | grep: none outside fields.def prose; memfn.h |
| zero bytes at switch 0 | finder hashes, arms pins, G2 |
| switch-1 scratch, planted bit, S3000 | Checks run, Sabotage row |
| sheet item 11, Deviations | u2_report.md |
| arch-blind, strict | green |

## STATE AT HANDOFF

OWED: none beyond the box gates the kit manager queues at 01:00. No process of this lane is running.
