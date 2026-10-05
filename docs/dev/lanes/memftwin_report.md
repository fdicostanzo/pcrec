# Lane memftwin — [MEMFN] R1d, the hand twins (2026-10-04)

Opus lane, MEASUREMENT. Branch `lane/memftwin` from main 8a41efd2.
Deliverable: `docs/design/memfn/twins.md`. Evidence:
`docs/design/memfn/probes/twins/` (the twins, run script, subject
materializer, table renderer) and `docs/design/memfn/probes/out/twins/`
(the Mac run, verbatim). Nothing under `src/`, `cli/`, `lib/` or `tests/`
changed. pcrec-bench was read only (subjects regenerated into the scratch
tree, sha256-checked against its manifests: 0 mismatches; its `git status`
stayed clean).

## Summary (resume point)

The question (D77): does a kernel TAILORED to the pattern beat a fixed
generic kernel, on real bench cells? Mac numbers, directional (D144 add. 1):

- **T-A, set classifier per shape vs the generic nibble lookup (shufti) vs
  a scalar 256-table loop.** Worth it only where the scan rejects, and
  small: on a miss the shape classifier saves ~1,000 ns per 64 KiB for a
  range or a one-bit cube, ~600-700 for eq2 / two-bit cube / nibble-unique,
  0 for eq3, and loses ~1,000 for `\w` (nib2 is the right `\w` form). At
  16-64 B: NULL. On dense text every find-first vector form pays ~7.5 ns a
  hit and loses to the scalar loop; the `iter` control (mask kept across
  hits) is the lever there, not the classifier. On SSE2-only x86 the shape
  forms are the only vector forms (no `pshufb`). k memchr calls lose
  everywhere, and go super-linear on dense real text.
- **T-B, fused scan+verify vs today's emitted K82 run gate.** Worth it,
  ~7x on all three cells: union-select gate 16,829 -> 2,408 ns per 64 KiB
  (478,402 -> 38,964 at 1 MiB), userpass sweep 27,912 -> 3,907, mod-i
  sweep 40,594 -> 5,331, short subjects 5.5-6.8 -> 3.6-3.7 ns. The cost
  removed is the per-scan-byte stop (~10 ns, 1,431 `c`/`C` in the
  capability t-64k against a run that never occurs). A second filter byte
  at its known offset is enough (`ffl`); ANDing all L offsets (`fall`) is
  slower. Composes with litscan_k82b.md's T3 handoff.
- **T-C, one header kernel + `static const` descriptor vs the hand kernel.**
  Worth it, and the enabling result: same instructions (clang: identical
  multiset on 4 of 6 shapes, the rest differing only in the scalar n < 16
  loop's table addressing; gcc: same vector loop, different allocation /
  schedule) and the same speed at every span. A writable EXTERNAL
  descriptor does not fold (~320-330 instructions, +600-700 ns per 64 KiB
  under clang). The hoisted run-time library form equals hand from 4 KiB,
  +0.3-1.6 ns a call below.

Correctness: every twin exhaustive vs an independent scalar reference
(positions x lengths 0..300/200 x alignments 0..31, all 256 byte values,
guard pages both ends, fuzz), 0 bad on NEON gcc/clang/clang-ASan+UBSan and
on x86 SSE2/SSSE3/AVX2 + AVX2 ASan+UBSan under Rosetta 2 (46.4M / 24.5M /
31.7M cases per build). The checks fire: a real bug on the first run
(`{A,B,a,b}` written as an absolute cube, following cls_tree_study.md
§4.3's prose; it is a cube only over c − 'A': 1,746,728 bad, fixed) and two
sabotages (12,750 and 6,036 bad).

## Validation

- `make -f docs/design/memfn/probes/probes.mk twins-check twins-check-asan
  twins-check-x86` — all green (`probes/out/twins/check.rosetta.txt`).
- `sh docs/design/memfn/probes/twins/twins_run.sh /Users/fdicostanzo/pcrec-bench`
  at commit e4dfe3ca — `run.log` trailer `MEMFN-TWINS-RUN COMPLETE ...
  fails=0`; archived verbatim to `probes/out/twins/`.

## OWED

- **The Linux run** (manager-scheduled, ~50 min, pinned):
  `sh docs/design/memfn/probes/linux_run.sh` now ends with one appended call
  to `twins/twins_run.sh "${BENCH:-../pcrec-bench}"`; its trailer
  `MEMFN-TWINS-RUN COMPLETE <dir> fails=<n>` (in
  `build/memfn_twins/<stamp>/run.log`, and on stdout after linux_run.sh's
  own) ends the whole run. Or alone: `sh docs/design/memfn/probes/twins/twins_run.sh`.
  It decides the x86 T-A ranking (SSE2 menu cost, `pshufb` nib2, AVX2), T-B
  against glibc's AVX2 `memchr`, the short-call deltas on a pinned loop,
  and T-C's code identity on x86 (twins.md §5).

## Notes for the manager

- cls_tree_study.md §4.3's table writes bc019 `{A,B,a,b}`'s cube as
  `(c & ~0x21) == 'A'`, which is false (`'B'` fails it); `cube_of`'s own
  offset form is right. A one-line erratum there is the study owner's call.
- The `mut` control had to be EXTERNAL: a writable `static` descriptor that
  nothing writes is folded by clang anyway (interprocedural constant
  propagation), which an emitter relying on "not const, so not folded" (or
  on the reverse) should know.
