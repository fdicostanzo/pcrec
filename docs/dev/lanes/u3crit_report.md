# u3crit — the pcrec half of review 2026-11-08-r5-xarch on the joint U2+U3 branch

Lane u3crit (opus). Branch `lane/u3crit`, cut from `lane/u3tgt` 424ddc742. The brief: apply every item
that the review's "Manager rulings" section lists under PCREC (docs/dev/reviews/2026-11-08-r5-xarch.md).
Rulings file: `docs/dev/lanes/u3crit_rulings.md`. R1 to R5 are all applied.

## Summary

- **Both gcc consumer build breaks are fixed (X-1, X-2).**
  - **The rule now.** The target region holds no `#include`. Every header line the artifact owes goes at
    file scope, just ahead of the region open. That covers the kit's header facts (`mf_includes`, spelled
    by `mf_include_c`, for this art and for each compound part through `PcrecPartFacts.includes`) and a
    compound part's own `<string.h>`.
  - **How it is written.** The placement is a TARGET HEADERS mark in its own guarded bracket. The
    finishing pass renders it (`target_headers_render`, memfn_stamps.c) after every site has rendered,
    because the bits are final only then. Lengths are decided outside the bracket, so no length decision
    sees the mark.
  - **Mark versus offset.** The kit's preview used a recorded offset, because its 3-byte mark moved one
    unroll decision. That move was not the mark's bytes. It was the in-place truncate-and-append over csb
    under a ladder trial's scratch bound, which underflowed the decide view. The render now rebuilds csb
    in a fresh buffer. The witness `((?:(?:(?:[^a]{1,2}|...){2,3}` is byte-identical to u3tgt, and the
    default sweep shows 0 movers.
  - **The four consumer-TU cells are green** (SSE2 intrinsics after a v3 artifact; v3 then x86-64 at -O2
    and at -O0; a fortified memcpy after a v3 compound). On u3tgt they were red.
- **HOUSE-4.** The target is derived once per attempt onto `Ctx.cpu_target`, by `pcrec_memfn_target_derive`
  in compile.c, which is the target's one failure point.
- **HOUSE-5, folded into X-2.** The region has one close for both engines, `pcrec_emit_artifact_end`. The
  attempt's end refuses a region that was left open.
- **X-6.** Targets and families are compared by name.
- **Checks.**
  - Consumer-TU cells, plus `ran` floors (checks-5).
  - One simd_guarded arm per listed target, plus an unread-bound control (X-4).
  - New sabotage row S1885 (wrong target) and corrected S1870 text (X-5a); new sabotage row S1895
    (headers dropped).
  - xt_place: the rx_info -1 guard and a no-include-in-region check (checks-6).
- **Docs.** match_api §6.3.10 ¶4/¶7/¶8/¶9/¶15, tuning §2.43, registry §6¶8a and limits §8.3, plus the
  EMIT-4 migration note in abi_changelog.
- **PLAN rows.** Five XARCH-* child rows, and the CONTRACT-6 rename as an [IFACE-PUSH] candidate.
- **The abi stays 98. No answer changed.**

## Disposition table

| item | disposition | where |
|---|---|---|
| X-1 placement, ¶15 amend, consumer-TU cells | DONE: the header lines (kit facts plus a part's `<string.h>`) sit at file scope ahead of the region; 4 cells green | memfn_targets.c `pcrec_memfn_target_headers`, memfn_stamps.c `target_headers_render`; run_targets.sh §4b; match_api §6.3.10¶15 |
| X-2 + HOUSE-5 | DONE: one artifact-end helper and an open-region alarm; the fortify cell is green | emit_dfa.c `pcrec_emit_artifact_end`, emit_vm.c, compile.c |
| HOUSE-4 | DONE: the target is derived once onto the Ctx | memfn_targets.c `pcrec_memfn_target_derive` |
| HOUSE-6/-7/-8 | KIT (R2); arrived in the 43ea5eedd merge | lane/memfn-u2 |
| X-4 | DONE: one guarded arm per listed target (floor 2); an unread bound row is a FAIL; floors re-pinned to simd-form 18 / named 8 | tests/memfn/simd_guarded_check.py |
| X-5a | DONE: new sabotage row S1885 (portable target stated on the art: 7 cli vrun cases red); S1870's text corrected | tests/mech/sabotages/ |
| X-6 (pcrec half) | DONE: targets and families compared by name | memfn_targets.c `set_add` |
| checks-5 | DONE: a missing pcrec on x86-64 is a FAIL; artifact and consumer RAN floors; forms check; the stripped-region control names its cause | run_targets.sh |
| checks-6 FIX-NOW | DONE: xt_place's rx_info -1 guard, a no-include-in-region check, stale comments | run_cli_tests.sh |
| checks-6 coverage, checks-4, checks-7, CONTRACT-4, SEAM-4(ii) | PLAN: [XARCH-PLACECOV], [XARCH-FIXEDTEXT], [XARCH-NEEDSOK], [XARCH-TOKERR], [XARCH-K2PULL] | docs/dev/plan.md under [XARCH-DEV] |
| CONTRACT-6 | DOC sentence in §6.3.10¶8; the rename is an [IFACE-PUSH] candidate | plan_row_bodies/IFACE-PUSH.md |
| X-7, X-8, X-9, CONTRACT-2/-3/-7 | DOC: done | match_api §6.3.10, tuning §2.43, registry §6¶8a, limits §8.3 |
| EMIT-4 | DOC: present-tense "Moving between targets" note in ¶4; history in abi_changelog (abi 98) | docs/dev/history/abi_changelog.md |
| kit merge (R4, R5) | merged lane/memfn-u2 ALONE twice: 685b6332f (bc05bbd6c tip e9faa283c) and the 43ea5eedd merge; all five mf_art_begin callers drop the policy argument; simd_levels.c reads the header from mf_include_c | |
| K35, K37 (test-codegen) | FIXED: `LC_ALL=C sort` at run_cli_tests.sh:2417; K37's existence-test pattern now covers `$PCREC_BIN` | tests/codegen/run_codegen_tests.sh |
| simdfloor / libc_census vs the header lines | target_text.py sets the header run aside (`header_run`, `aside`); simd_floor_check sets aside a moved header that OFF also carries (`moved_headers_aside`) on every leg; C9 compiles the artifact as emitted | tests/memfn/target_text.py |

## Checks

All runs below were on this branch, single targets run with `nice` under `scripts/boxlock`; the logs are in `$PCREC_TMPDIR/scratch/u3crit/`. The baseline "u3tgt" is a `git archive` build of 424ddc742.

| check | result |
|---|---|
| premise (u3tgt) | the 4 consumer-TU cells are RED on u3tgt (intrinsics, two artifacts at -O2 and -O0, fortify) |
| `make strict` (after both kit merges) | rc 0 |
| test-memfn-targets | 38 passed, 0 failed; the 4 consumer cells are green; artifact and consumer RAN floors met |
| test-cli | rc 0 (xt_place: no include inside the region; the rx_info -1 guard) |
| test-memfn-stamps | rc 0 (FORMS movers: the header lines are set aside by target_text.aside) |
| test-memfn-guarded | rc 0 (per-target arms; every bound row read) |
| test-memfn-finder | rc 0 (policy_check is built against the 5-arg mf_art_begin) |
| test-memfn-arch | arch-blind 17/0 |
| test-codegen | rc 0 (K35, K37 and SABANCHOR all green) |
| test-memfn-simdfloor | 20414 passed, 0 failed |
| identity, default arm (emit_sweep vs u3tgt, c-default + c-vm + stderr, full corpus) | 0 movers out of 6394 / 6394 / 6394 |
| identity, `-fmemfn-simd=x86-64` and `=x86-64-v3` vs u3tgt (5095 distinct patterns, byte) | movers per target: 49 at the default engine, 24 at the VM. Every differing line is an `#include <H>` line that moved (the lines outside the stamps: 0 non-header diffs, hdrcheck.py) |
| the movers proof (u3tgt_movers.py vs the abi 97 ref, x86-64-v3, --limit 400) | unpredicted 0 across all 8 cells (the proof now lets a header line move) |
| ladder witness `((?:(?:(?:[^a]{1,2}|...){2,3}` | byte-identical to u3tgt. A first in-place render underflowed the decide view and moved K 1 to 8; fixed by rebuilding in a fresh buffer |
| sabotage row S1885 (portable target on the art) | 7 cli vrun cases red |
| sabotage row S1895 (headers render writes nothing) | 17 run_targets checks red, the 4 consumer cells among them |
| test-spec-history, test-plan-lint, test-claudemd-size | rc 0 |

**Owed (the full re-run must cover these).** The six main-u3crit-* jobs, queued on this tip at prio 480:

- sections: cli, stamps, arms, arch, targets, rows, guarded, simdfloor, forms, reach, kitproof, codegen, registry, rxtsource;
- the full movers proof at both targets;
- the sweepsimd DIFFER floors (byte and utf8);
- mech rows S1870, S1871, S1872, S1885, S1895 and S724, plus u3floor's set;
- axes `--memfn`;
- make test.

Then: the D27 spec-first author on §6.3.10¶14-¶15 and §10.7¶4 (consumer TUs, two artifacts, compounds), and the joint landing.

## STATE AT HANDOFF

STATE: delivered. The last rulings entry applied is R7. Every PCREC item of review r5 is done or filed (table above), and the kit's half (lane/memfn-u2 tip 43ea5eedd) is merged. The abi stays 98. No answer changed.

Open:

- The six main-u3crit-* jobs (queued on this tip, prio 480).
- The D27 author cell.
- The joint landing: fast-forward lane/u3tgt to this tip, or land from here.

Kit-side, relayed: [XARCH-NEEDSOK] (the S726 closer).
