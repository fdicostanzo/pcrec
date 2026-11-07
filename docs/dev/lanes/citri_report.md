# citri report (2026-11-07, sonnet): CI red on main d9908dfc3

Run 42377116304 (merge c44649a69, variable lookbehind stage 1): shards 1/3 and 3/3 red, 2/3 green. No code changed by this lane.

## Failures

1. **test-stackdepth, [DD-10] `optnest` nested 250 deep KILLED (exit 139) on the 442368-byte thread** (shard 1/3, make `Makefile:1716: test-stackdepth`).
   - Cause class: REAL REGRESSION, compiler stack growth from c44649a69 (stop rule; not fixed, engine).
   - Evidence: the per-family high-water record (RECORD hw=) at the 250 cap, previous green CI (65722f996) vs this CI vs local (same gcc 15.2): optnest 395728 -> killed (>442368); altnest 317304 -> 390328. Local, built from 65722f996 vs current: optnest 385568 -> 418480, altnest 309032 -> 342072, grp 165608 -> 182712; look/lookbehind/callouter etc. flat or small. CI runs ~10-50 KB hotter than local, so the +33 KB growth crosses the 442368 budget there but not on this box (the script passes locally, rc=0, only ~5.4% headroom left).
   - Frame growth by `-fstack-usage` (65722f996 vs current, src/*/*.c): `pcrec_ast_visit.constprop` (internal.h) 144/160 -> 208 bytes (+48..64 per nesting level), `vm_emit_node` (emit_vm.c) 624 -> 672, `la_widths` (mod_lookaround.c) 80 -> 112, `pcrec_lookaround_fix_widths` 336 -> 352, `vm_r_seek` 16 -> 32; `pcrec_emit_vm` 3072 -> 4096 (not recursive). A ~100-130 B/level growth over 250 levels matches the +33 KB.
   - Repro: `make -j8; bash tests/thread/run_compile_stack.sh` and compare the `RECORD: optnest@250` hw line against 65722f996 (385568). Needs the manager/engine owner: shrink the recursive frames (the new `pcrec_ast_visit` callback state is the largest), or re-budget limits.md 3.10 deliberately (spec hunk).
   - Fix commit: not fixed, engine change without a build go.

2. **test-lookaround section 5, `utf8-invalid  (?<*(.{1,3}))b`: 5 of 36 cells differ** (shard 3/3, `Makefile:1198: test-lookaround`; the other 660 patterns agree).
   - Cause class: suspected CI-ENVIRONMENT (oracle build difference); not proven.
   - Evidence: first differing cell is subject s01 = bytes `ff 61 62`, startpos 0: pcrec `match 2 3 1 2` (group 1 = 1..2), CI libpcre2 `match 2 3 0 2` (group 1 = 0..2, the lookbehind consumed the invalid byte). Locally (distro libpcre2 `10.46-1ubuntu0.1`, same oracle code, same flags PCRE2_UTF|MATCH_INVALID_UTF) the oracle answers `match 2 3 1 2`, identical to pcrec: section 5 passes 661/661 and `vlb_one.sh` passes 3 of 3 for this pattern. pcrec's output is the same in both places; only the oracle's changes. CI uses vanilla 10.46 built from the tarball (no distro patches); this box uses Ubuntu's patched package. This is the first CI exposure of section 5 (new in the landing), so no earlier green covers it.
   - Not proven which libpcre2 is "right" for a lookbehind stepping back over an invalid byte under MATCH_INVALID_UTF. Next step (needs the owner): either a `pcre2-reader` question (D181) on lookbehind over invalid UTF with MATCH_INVALID_UTF, or build vanilla 10.46 locally (tarball download needs explicit approval, with checksum, per the security rule) and rerun `tests/lookaround/vlb_one.sh`. If vanilla is right, pcrec's utf8-invalid lookbehind needs a fix (real answer gap, D142/W13/W15 area) or the cell must be a documented stated divergence.
   - Fix commit: not fixed, cause not shown.

## STATE AT HANDOFF

- Branch lane/citri: this report only (plus deliver file); no pins, test expectations or CI config touched, because neither cause is shown to be a stale pin.
- Local confirmations run narrowly (no queue needed): `tests/lookaround/run_lookaround_diff.sh` (8/8 pass) and `tests/thread/run_compile_stack.sh` (rc 0) in the worktree; stack-usage comparison built from `git archive 65722f996` in scratch.
- Rulings file citri_rulings.md was empty at the last read; no entry applied.
- Scratch: /var/tmp/pcrec-pcrec/scratch/citri/ (CI logs job128416894541.log = shard 1, job128416894703.log = shard 3; prev1.log = last green shard 1).
- Owed runs: none.
