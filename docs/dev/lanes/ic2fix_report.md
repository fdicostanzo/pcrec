# ic2fix — the r1-ic2 code review's FIX-NOW findings on [INLINE-C] stage 2

Lane ic2fix (opus), 2026-10-27/28, worktree `worktrees/ic2fix` (branch
`lane/ic2fix`, from `lane/ic2` @864902a48). Review:
`docs/dev/reviews/2026-10-27-r1-ic2-code.md` (+ dir), committed first
(ade81545b, one cite disambiguated, accepted by the manager). Last rulings
entry applied: `ic2fix_rulings.md` 2026-10-27 ~23:55 (F3 (a)+(b)).

## Summary

Every ruled FIX-NOW finding is landed, one commit per finding or tight
group, each citing its F-id: F1-F15 (F15: the false "is enabled" sentence
only), F19-F25, F31-F34, F35 (done with F1/F2), plus the manager's
span-fold addition. DOC items F16, F17, F30 are in one commit; F18's DOC
half (goal 3b restated) is its own design-note commit, and a second design
commit brings inline_c.md §2.4/§3.1/§3.2 in line with the fixes. Every
reproducible finding got a test row that failed on 864902a48's binary (or
script) and passes now; the exceptions are named in the table.

abi stays 90 (open): every emitted-text move folds into it, no bump. Local
validation green: `make strict`, test-code (all arms), test-registry,
test-rxtsource, test-codegen (see "abi and re-pins"). Owed and queued: the
full make test + mover census, mech, axes (640/641/642).

One deviation to report: F3's contract column also marks `_CALL_TOP_NONE`
and `_TRACE` internal (the ruling named R_* and NSLOTS). Both are absent from
match_api.md §6.3.2's inventory, and the new check found them live.

## Fixes by finding id

| F-id | commit | test row | seen failing first |
|---|---|---|---|
| F1 F2 F35 | 63113a2ff | arm 3: U+061C, U+3164, U+00AD, U+E0041, U+2028, U+0085, CR/VT/FF refused; CRLF + é accepted | yes (10 FAILs) |
| F9 | d363f61ff | arm 8: `{0}` and uncalled DEFINE site under -Werror | yes |
| F10 | 16d18b537 | span_check.c one(NULL,0), set-NULL span; driver nu_search(NULL) vs "" | yes |
| F12 F31 | f83167ac0 (+ sort fix in the F12 follow-up commit) | arm 5: hd.rxt's highest cited line <= 4, hd.c named | yes (line 12 of 4) |
| F3 | dfc8849a9, 56cb7715f (S910 anchor) | arm 7: live names minus (.h + §6.3.2 inventory) empty; S1720 | yes (S1720 by hand: 8 FAILs) |
| span-fold | 6ab02f034 | arm 9: sf_eq's x86-64 CFG has no call and no cycle | yes (loop on old) |
| F22 | d4b697c12 | trap rows want SIGILL/SIGTRAP by arch; segfault control; S1721 | yes (S1721 by hand) |
| F21 | d570d6d76 | arm 10: per-build positive witness (le3_mark / ub_mark / oc_match reached); sep_bind.c deleted | yes, by hand (`(\d+)x`: 0 indirect calls, witness not reached) |
| F4 | 361c185c0 | arm 3: --emit-facts shows no RX_FAKE, "zzz" or RX_SUBJ rows | yes |
| F5 | d7377950f | registry_check: a module's rows agree on RF_INVOKER_ONLY; S1683 re-aimed | no: not reproducible on this branch (by reading; today's lists are safe) |
| F6 | 7e8afa961 | arm 3: allow-code manifest allow-list; two-line manifest is a harness failure | yes (old run.sh rc 0; stray manifest appears) |
| F7 | f70ae57b6 | arm 3: refused two-target -o DIR build writes nothing | yes (fr.c fr.h written) |
| F8 | 0660cce36 | arm 3: --allow-code= equals no grant for 3 describe modes | yes (--emit-ir, --emit-facts) |
| F11 F13 F14 F34 | 82aa0108b | arm 3: 300 code-header lines -> 300 includes; --help lists both; `c:` shape refusal | yes (256 / absent / malloc: Success); F34 refactor, no row |
| F15 | 03fcf78ac | arm 3: verify refusal names code-c | yes |
| F32 F33 | ffdbf19dd | refactors, answer-identical (test-code green) | n/a |
| F19 | a16264d32 | arm 11: hit/tail fire, miss row hits>0 fires 0 | yes (old row: hits 0, equal instr 135137/135118) |
| F20 | 29684deb7 | arm 4: 7 non-table modes run; mode count exact 17 | yes, by hand (added X() row reads 18) |
| F24 | 1faee72f7 | verify_code over tests/code + frag, CELLS_PIN 36 exact | yes (old invocation: 34 != 36) |
| F25 | f08f902d9 | run_axes: tests/code floor 35 (measured 38) | yes (broken geoip.c copy: 2 rows) |
| F23 | 42110da4f | rxtsource: head population pinned 5/16/0/3 | n/a (new pin; green at its measured value) |
| DOC F16 F17 F30 | 43c0444fe | docs only | n/a |
| F18 (DOC half) | 949d203bd | design only | n/a |
| design follow-up | 6bfa67eca | design only | n/a |

## Spec and design hunks

- match_api.md §11.9¶3 (refused characters by UCD property, line ends, C0/DEL), §6 ASCII paragraph, pattern_language.md §7.12¶3 (F1/F2).
- match_api.md §11.2¶1a (unused attribute, F9; -O1 condition, F16); §11.10¶1 (unset = negative length, F10); §11.9¶4/¶5 (macro set once before the first #line, F12/F31; §6.3.1¶10 internals #undef'd, F3; what a segment can affect, F4; #line names reach gcc raw, F17); §11.9¶8 (describe modes: absent/empty/list, F8).
- facts_listing.md §4.2¶3 (the code block is not listed, F4).
- rxt_format.md §6¶3/¶3a/¶4 (allow-code allow-list, -I sentence, second line, F6).
- cli.md §1.1.1¶4 (every target compiles before any write, F7); §1.22¶1 (describe grant, F8).
- No spec hunk for F11/F13/F14/F15 (behaviour now matches existing text; wording not spec'd).
- Design inline_c.md: goal 3b restated "within the binding path's own cost" (F18); §2.4 refused-character row and the stale unknown-tag row (F1/F2/F15); §3.1/§3.2 macro-set order (F12/F31) and the catalogue keep rule (F3). All marked with the review tag.

## Tests and sabotage

- tests/code/run_code_tests.sh: the rows in the table above (89 checks, 0 failed, at handoff).
- tests/code/span_check.c, card_inline.sh (tab-separated rows, hits, instructions:u), verify_code.py (CELLS_PIN), tests/harness/run.sh (second allow-code line), tests/registry/registry_check.c (grant uniformity), tests/rxtsource (head pins), tests/axes/run_axes.sh (code floor).
- New sabotage rows: S1720 (code_keep by prefix, F3), S1721 (fall-off segfaults instead of trapping, F22), each planted by hand and caught. Re-aimed: S1683 (F5's mask line), S1681 (F8 rename), S910 (F3's new column; its anchor had stopped matching, found by comparing every row's anchor count against 864902a48). Unused ids: S1722-S1739.

## abi and re-pins

abi 90 still open; no bump. Emitted-text moves folded into it: the `unused`
attribute on code `_ref`s (F9), the span helpers (F10, span-fold), the macro
set's position (F12/F31), the keep set's `#undef`s (F3). All are callout /
code artifacts only; the queued mover census (640) checks that nothing else
moved. Local suites: strict, test-registry, test-rxtsource, test-code green;
test-codegen green on the re-run (its first run found one ambient-locale
`sort` in the F12 test row, fixed in the F12 follow-up commit). No abi-90 reader needed a number change
(the number did not move).

## Not done and why

- Not this lane's (per brief): F18's PLAN row, F27-F29, F36-F38, the D27 tests.
- F15's other wordings (`py:`, `c,:`) stay NOTED (D26 tier), per the ruling.
- F22's sabotage rows for arms 9-10 are PLAN (review).
- F5 has no reproducing row: both lenses found it by reading; it is guarded by the registry assertion and S1683.
- The card's verdict still compares against the callout-free twin; goal 3b's new comparison (the unity-binding twin) is a card change for F18's PLAN row.
- rx_eqi still loops over the bytes (span-fold claims only rx_eq's literal case).

## STATE AT HANDOFF

- Branch `lane/ic2fix`, all work committed (this report in the last commit).
  The untracked `docs/dev/lanes/ic2fix_deliver.txt` is the manager's, not touched.
- Local, on the lane's HEAD before this report: `make strict` rc 0,
  test-registry rc 0, test-code rc 0 (89 passed, 0 failed), test-rxtsource
  rc 0 (306 files / 6241 blocks / 74709 lines), test-codegen rc 0 (re-run
  after the sort fix). Logs in /tmp/claude-1001/ic2fix/val_*.log.
- QUEUED (not run by the lane), box queue `pending/`, each `--dry-run` clean
  before `boxqueue add`:
  - `640-ic2fix-test`: build, strict, mover census vs 6d0974b74 at abi 90
    (`ic2_movers.py`, expect unexpected=0), full make test (81 sections).
    Copied from 620-ic2-test (TREE, SCR, perfrun label, header).
  - `641-ic2fix-mech`: S1680-S1685, S693, S910, S1720, S1721 (10 rows).
    Copied from 621-ic2-mech (TREE, IDS, header).
  - `642-ic2fix-axes`: AXES_FULL=1 HARNESS_BATCH=64 run_axes + form census.
    Copied from 622-ic2-axes (TREE, header); cap raised 15600 -> 18000
    because 622 used 14848 s of 15600.
  Ahead of them at queue time: 630-reqvm1-test (running), 631, 632.
- Merge: lane/ic2fix carries lane/ic2 plus the review files; merge it (not
  lane/ic2) after 640-642 are green, per the manager's plan.
