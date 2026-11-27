# f2f6 report: [ARENA-SCOPES] client units F2 (clskit) and F6 (uprops_produce)

## Summary

Two commits on `lane/f2f6` (cut from main cd17dea82): `02132bc91` F2, `17c6cfb36` F6. Both units are built; every
heavy validation is OWED to the queue (keys under STATE AT HANDOFF). Premise test held on main: (a) `pcrec_clskit_emit_kit`
has 3 src callers (`emit_dfa.c:13225`, `emit_vm.c:13313`, `emit_vm.c:13344`) plus the test driver (`tests/clskit/clskit_driver.c:197,206`);
(b) `mod_uprops.c:296` `Arena tmp = { .cx = cx }`; (c) the scanner carried the clskit `arena:a` row and the uprops `arena:tmp` row;
(d) `alloc_check.c:238` carried the `uprops_produce` `known_stranded` row. No emitted-byte change expected: 5 UTF-8 patterns
(`\p{L}+`, `[\p{Lu}\p{Nd}]x`, a negated high range, a Greek/Han alternation, `\P{Han}\w+`) compile byte-identical to the older main build
(`build/pcrec` of main), including the 815 KB `\p{L}+` text. The manager's emit sweep is the real 0-movers gate (not run here). No abi bump.

## F2

- `pcrec_clskit_emit_kit(StrBuf *c, Arena *parent, const char *fn, const ClsKit *k, unsigned cp_max)` (`src/gen/clskit.c`, `clskit.h`).
  The scope opens AFTER the empty-set return, so the empty path (the design's STOP row) opens no scope, takes no record and no
  block; on the non-empty path the child is `pcrec_scope_arena(&sc)`, closed at the end. Callers: `emit_dfa.c` passes `&f->cx->arena`,
  `emit_vm.c` (2) `&cx->arena`, the test driver its own detached arena `a` (cx NULL; scopes on a detached arena are allowed, D-2).
- D-11's binder rule: `d11_findings` in `tests/core/scratch_builder_check.py`, keyed on the TYPE `mf_arena` (declaration), catching an
  assignment binder (`NAME->u =`, `NAME.u =`) and a brace-initializer binder (`mf_arena NAME = { X, ...}`), plus any `mf_art_begin(`
  caller outside `pcrec_memfn_art`. The one allowed binder is `pcrec_memfn_art`'s `ma->u = &cx->arena`; a floor requires it to be
  SEEN (a scan that reaches nothing fails, K35). Fixtures: 4 must-fail (assignment, initializer, the allowed function binding something
  else, a foreign `mf_art_begin`) and 1 must-pass.
- Scanner `ALLOW` row for clskit deleted (`shape:NAME` stays: nb, tail, o). Sabotage rows S3613 (clskit close deleted) and S3614
  (the art's binder spelled through a cast; core arm).
- W6 pin: not touched. W6 (`^abc|x+$`, a compound walk) was not measured to reach clskit, and the brief makes the re-pin conditional on
  W6 reaching it; the OWED test run reads W6 and a red pin there is a re-pin UP (D110).

## F6

- `uprops_produce` (`src/parse/mod_uprops.c`): `Scope sc = pcrec_scope_open(&cx->arena); Arena *tmp = pcrec_scope_arena(&sc);`
  `pcrec_ucd_find` allocates into `tmp`; `pcrec_scope_close(&sc)` replaces `pcrec_arena_free`. The comment states the refusal path
  (the compile arena's teardown releases the child) and keeps the +29% reason for not decoding into `cx->arena`.
- Scanner: `SCOPE_PARSE_ALLOW` carries the one row (`src/parse/mod_uprops.c`, `uprops_produce`); the uprops `ALLOW` row is deleted.
  Fixtures: another function of mod_uprops.c opening a scope must FAIL (L4); `uprops_produce` opening and closing passes.
- `alloc_check.c`: the filed `uprops_produce` `known_stranded` row deleted (its comment and the W7 rows' comment updated). S3602's
  re-aim: its second witness was that row, so it now rests on the planted-strand control alone (REACH_POP re-anchored on `w7_plant`).
- Docs: D-10's sentence in `src/core/internal.h` (Arena comment: two kinds plus the scope's child); the K155 uprops sibling line in
  `docs/dev/known_issues.md` deleted; the design's "Deviations at build" gains a F2/F6 BUILT entry; `tests/core/CLAUDE.md` names the scope
  and D-11 rules. Sabotage S3615 (uprops close deleted).

## Gates

Run locally (quick, no queue): `make` clean; `make strict` clean; `python3 tests/core/scratch_builder_check.py` PASS
(92 files, 24 allowlisted sites, 3 scope sites); `m6read_check_sab_anchors.py` all plants apply; `VALIDATE_ONLY` mech validation of
S3613 S3614 S3615 S3602 valid; `make test-clskit` GREEN (5 checks passed, 0 failed) at the F2 build.
OWED to the queue: `make test` (includes test-alloc through the resource arm), mech, memgate (bound 112 B = 72 + 40, the F2/F6 bound), plus
a measuring job.
- WATCH ITEM, W7/W3 floor: `alloc_check.c`'s `W7/W3` `min_total` is 267, half of 535 measured when `uprops_produce`'s hand-kept window
  was in the population. After F6 that window is gone (the child arena's own allocations are not in a window; the class constructor's
  allocations on `cx->arena` are scope-window points at stride 4), so the population is probably well under 535. I could not measure
  it (the box was held when I stopped working); the queued job `190-f2f6-alloc` prints W7's populations with `--w7-only`. If the
  `200-f2f6-test` test-alloc section is red on that floor, RE-PIN it to half the new measured population (D110); that is expected work,
  not a design stop. W3 reaching the deleted row cannot be judged any other way: the SEEN gate's verdict is that W7/W3 reads GREEN with
  the row deleted AND a nonzero scope-window population.

## Scanner and register rows

ALLOW rows: 26 -> 24 reached sites (the clskit row at F2, the uprops row at F6);
`SCOPE_PARSE_ALLOW`: 0 -> 1 (the L4 row). `known_stranded`: 1 -> 0 rows in alloc_check (the uprops row; the K155 `target_headers_render`
row stays until F3). The design's "Clients" rows F2 and F6 are recorded as BUILT in "Deviations at build". `docs/dev/guide/architecture.md`
carries no ARENA-SCOPES register row (grep: none), so nothing to update there. K155's own Status paragraph (history) still names clskit
and uprops as first clients; left as the record.

## STATE AT HANDOFF

- Built: F2 (`02132bc91`) and F6 (`17c6cfb36`), report committed. Last ruling applied: R1 (the owner lifted tonight's hold; jobs queued
  WITHOUT a time gate, same keys).
- Local checks: see Gates (all green). Local emit identity spot-check on 5 patterns: identical.
- STOP rows touched: none seen. The child's first block on clskit's empty path: by construction impossible (the scope opens after the
  empty return); the memgate job reads it. W3 reaching the uprops row at F1 was the F1 lane's gate (REACHED then); not re-run.
- OWED queue keys: `200-f2f6-test`, `200-f2f6-mech`, `200-f2f6-mg`, and the extra measuring job `190-f2f6-alloc` (W7 populations
  for the floor re-pin). A fresh agent reads the verdicts with `scripts/verdict` and `scripts/monread`, re-pins the W7/W3 floor from
  `190-f2f6-alloc` if needed, and commits.
