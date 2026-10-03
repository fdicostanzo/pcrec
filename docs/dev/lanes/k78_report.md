# k78 report — K78 fixed (a DFA dead-group artifact wrote `caps` on a no-match)

Lane k78, opus, 2026-09-30. Branch `lane/k78` from `lane/k7980` (44fc6ad5, abi 54).
One abi event, 54 -> 55.

## 1. Cause

A DFA artifact with `<PREFIX>_NCAPS >= 2` promises groups that no match can
set. Each such group is reached only through a subroutine call or sits under a
`{0}` ([DD-14 wave G]'s dead-capture elision; PCRE2 counts these groups and
reports them unset). `<prefix>_search` reports them as `PCREC_UNSET`.

`emit_search_head` (src/gen/emit_dfa.c) emitted that fill at the TOP of
`<prefix>_search`, after the startpos guard and before the `search_from >
subject_length` return and any answer. So every non-success return overwrote
`caps[1..NCAPS-1]` with `{-1,-1}`, against match_api.md §3.1 ("`caps` left
untouched" on `0`). Reproduced on the branch point with the uvbuild witness:
`(?(DEFINE)(?<x>\b))b(?&x)` gives `rx_search("zz", 2, 0, caps)` = 0 with
`caps[1]` written.

## 2. Fix (the mechanism, not the witness)

The fill is now `emit_dead_group_fill(cx, c, ind)`, a helper that emits the
existing fill block at a given indent. It is called on every SUCCESS path of
every DFA search form, after the `caps[0]` write and before `return 1`:

| form | site |
|---|---|
| unanchored, reverse-pass | `emit_unanchored`, after the reverse scan |
| unanchored, pinned | `emit_unanchored`, the `pinned` branch |
| attempt (per-start) | `emit_attempt`, the `_done` accept |
| empty | no success path, so no fill (it now just returns 0) |

`emit_search_head` no longer writes `capture_spans`. Its header now says
nothing there may, because that code runs before any answer. The
`fit.chosen == ENGM_DFA` gate (which keeps the fill out of the VM hybrid's
static prefilter) moved into the helper unchanged.

Emitted text moves only on DFA artifacts with `NCAPS >= 2`, and only in the
fill's position. Every other artifact changes only in its abi digits. The fill
text itself is byte-for-byte the old block. The split string literals keep the
S221 anchor line verbatim, and S190's anchored `_match_caps` site is untouched;
`scripts/m6read_check_sab_anchors.py` reports 391 rows / 407 sites, all
resolving.

## 3. Other sites checked

The brief asked whether the same caps-write discipline is wrong anywhere else.
The new check drives every entry that takes a caps array on both compilers:

| site | pre-fix | post-fix |
|---|---|---|
| DFA `_search` / `_search_in`, dead-group artifacts | **wrote caps on no-match** | clean |
| DFA `_match_caps` / `_match_caps_in` (unwrapped: its own fill after the early return; search-filter: a local array, copied on success only) | clean | clean |
| VM `_search` / `_match_caps` and the `_in` spellings (NULL descriptor and a one-frame descriptor, so FRAMES give-ups are included) | clean | clean |
| VM hybrid (corpus slice, auto route) | clean | clean |
| `-e utf8`: the startpos guard's -7 refusal, emitted above the fill | clean for -7; wrote caps on a plain no-match | clean |

So the defect was only in the one site. Also clean on both compilers: every
success wrote all NCAPS pairs and never wrote past NCAPS.

## 4. The check: `tests/codegen/run_nomatch_caps.sh` (+ `nomatch_caps_driver.c`)

- **Contract.** A sentinel fills the array plus one guard pair past NCAPS.
  After a non-success, every pair must still hold the sentinel. After a
  success, pairs `0..NCAPS-1` must be written and the guard pair must still
  hold the sentinel.
- **Calls.** Four entries, at every startpos `0..n+1` of twenty subjects. On a
  VM artifact the `_in` spellings also run with a one-frame descriptor.
- **Population.**
  - Eight dead-group witnesses on four routes: auto, `--engine=vm`,
    `-fno-anchored-dfa`, `-e utf8`. Each witness must reach its declared DFA
    search form on the auto route (reverse-pass ×3, pinned ×2, attempt ×2,
    empty ×1). Each of the four forms must be covered.
  - Every 12th distinct capture-bearing corpus `pattern`, on auto and vm.
- **Size.** 406 artifacts. 378 are driven; 28 are refused by pcrec, counted
  and not scored. 0 fail to build.
- **Floors.** At least 300 artifacts, 50,000 non-success calls, 24 dead-group
  DFA artifacts with 3,000 non-success calls, and 100 VM artifacts.
- **Cost.** About 90 s at 8 procs. It runs in `make test-codegen`, on the mech
  arm `nomatchcaps`.

| compiler | result |
|---|---|
| this branch | **7 passed / 0 failed**: 238,870 non-success calls, 33,290 successes, 27 DFA dead-group artifacts |
| pre-fix (44fc6ad5 archive) | **3 passed / 4 failed**: W auto 2,094 of 4,284 non-success calls wrote caps; C auto 1,041 (from corpus dead-group patterns, e.g. `(?(DEFINE)(?<g>\Ga))(?&g)`); W nfad 2,094; W utf8 2,058. The VM routes and reach stay green, correctly. |
| **S439** planted by hand (the fill re-emitted at the search entry) | 3 passed / 4 failed, the same four rows and counts |
| second direction planted by hand (`emit_dead_group_fill` returns at once: the fill is never emitted) | 3 passed / 4 failed, the same four rows: 0 non-success writes; 786 (W auto), 39 (C auto), 786 (W nfad), 774 (W utf8) successes left a slot unwritten. These are the `_search` successes; the unwrapped `_match_caps` keeps its own fill and stays clean. |

The harness's own first run found a bug in itself: auto and vm rows shared one
work-directory index, so two workers interleaved one `.c` file ("null
character(s) ignored"). Indices now carry the route. The first run also had
the reach lookup pointing at the wrong row. Both were fixed before any number
above was taken.

**Sabotage S439** (`tests/mech/sabotages/S439_k78_dead_group_fill_at_entry.sh`).
It adds `emit_dead_group_fill(cx, c, "    ");` after `emit_search_head`'s
guard, which is the pre-K78 placement. `SAB_REACH`: the witness stamps
`RX_NCAPS 2`. Mech arm `nomatchcaps` is registered in
`tests/mech/run_sabotage_matrix.sh`. It was not run through `make mech` (heavy
tier); the hand plant above is the same edit.

## 5. abi 54 -> 55: readers found by grep

`grep -rn '\b54\b'` over src lib cli tests docs/spec docs/guide examples
scripts Makefile tools, filtered to abi contexts:

1. `src/gen/emit_dfa.c:52` `PCREC_ARTIFACT_ABI` 54 -> 55 (feeds `.abi`, the
   header line, the valued guard and the `#error`).
2. `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT=55`, plus a 54->55 clause
   at the end of its failure message.
3. `docs/spec/match_api.md` §2's quoted guard block (`!= 55`, `abi 55`,
   `#define PCREC_RX_ABI_H 55`), because it shows the current emitted text.
4. `docs/spec/match_api.md` §6: a new `rx_info.abi is 55` entry above the 54
   one, which becomes "was 54".
5. `tests/codegen/run_recursion_identity.sh`: the (B) `FILEPIN` is re-pinned
   to `6b86a29b`, this lane's last `src/` code commit (the self-pin
   convention). The manager re-pins at merge if that commit is rewritten.

Every other `54` hit is historical prose and is correctly unchanged: the K79/K80
notes in the CLAUDE.md files, the S437/S438 headers, limits.md/tuning.md
"since abi 54", and run_codegen_tests.sh's "pre-54 empty guard" K80-b cells,
which describe the rule's origin. The K80 cells read the abi off the artifact.

**Readers that never cite the digit** (a count or byte manifest that moves):
the run of `test-codegen` / `test-cpset-structure` / `test-registry` /
`test-rxtsource` in §7 is the evidence. The abi digit keeps its length, so only
dead-group DFA artifacts change in length.

## 6. Spec (D80)

- match_api.md §3.1 gains one paragraph. Every return other than `1` leaves the
  whole `caps` array untouched, on every engine and every caps-taking entry,
  and that includes dead-group artifacts, whose slots are written only on a
  success (K78, abi 55).
- match_api.md §6: the abi 55 change-log entry.

## 7. Light validation (Mac, gcc-16)

- `make` clean. `make strict`: "whole tree compiles clean with -Werror -Wshadow".
- `scripts/m6read_check_sab_anchors.py`: 391 / 407, all resolve.
- `run_nomatch_caps.sh`: 7/0 here, 4 of 7 red pre-fix and under S439 (§4).
- `make test-codegen`: **13/14 scripts** (191 s). `run_nomatch_caps.sh` 7/0.
  `run_codegen_tests.sh` passes, which covers `ABI_EXPECT=55` and SABANCHOR's
  391 rows. The one red is `run_inline_capability.sh` ("nm could not read
  arm_a.o"), the standing darwin probe. It was A/B'd: it is red identically
  with the branch-point compiler, so it predates this lane.
- OWED, still running detached when this was written: `test-registry`,
  `test-rxtsource`, `test-cpset-structure`, `test-anchored-match`, and the
  corpus slice (`tests/recursion/define.rxt realworld.rxt tests/captures/*.rxt
  tests/base/groups.rxt`). The chain is `worktrees/k78/build/k78s/chain.sh`.
  Its summary is `worktrees/k78/build/k78s/chain_summary.txt`: one
  `<target> rc=N Ns` line per target, ending in `CHAIN-DONE`. Read each
  target's verdict from the make-error lines in its
  `worktrees/k78/build/k78s/v_<target>.log` (`v_corpus.log` for the slice).
  Of these, cpset's `EMITTED_BYTES` manifest and anchored-match's dead-group
  witnesses are the likeliest readers to move.

## 8. Owed (manager)

- Full `make test` and `make mech` on the combined tree (S439 through
  `nomatchcaps`).
- `make test-recursion-identity` (~35 min): its (B) pin is `6b86a29b`, and (A)
  is expected untouched because no VM program region moved.
- Re-pin FILEPIN if the merge rewrites `6b86a29b`.
- Linux run, per the two-machine rule.

## 9. Post-merge with the k7980 tip (2026-10-03)

`lane/k7980` 3698dae6 merged into `lane/k78` as 1a9d4eed. 3698dae6 is k7980
plus main d0487a97's merge (the [CLS-TREE] S2 merge, artmgr docs, plan and
journal) plus the k7980tri fix a111a150.

- **Conflicts.** One, in the `docs/dev/lanes/CLAUDE.md` index, where both
  sides appended report lines. All three are kept: k7980tri, artmgr, k78.
- **abi.** It stays 55, with no conflict. S2's 50->53 and K79/K80's 54 were
  already under k78's base 44fc6ad5. The merge brings no emitted-scaffolding
  change. Readers checked by grep: `PCREC_ARTIFACT_ABI 55`, `ABI_EXPECT=55`,
  and match_api.md §2's guard block (`!= 55` / `abi 55` /
  `PCREC_RX_ABI_H 55`).
- **Composition with a111a150.** The only incoming `src/` change is
  `src/gen/emit_vm.c`'s `--emit-ir` caps cell, which now reads
  `pcrec_sb_upper(&cx->arena, cx->user_prefix)`. K78's
  `emit_dead_group_fill` (emit_dfa.c) writes `gn.upper` into artifact text
  with `pcrec_sb_printf`. It never goes through `pcrec_sb_row`'s escaper, so
  the finish-time prefix render still sees its placeholder. The two edits are
  disjoint. Spot check: `--emit-ir '(a)(b)c'` prints `RX_NCAPS` at `-p rx`
  and `MYRX_NCAPS` at `-p myrx`.
- **Re-pin.** The recursion-identity (B) `FILEPIN` 6b86a29b -> 1a9d4eed.
  The merge brings a111a150 (a `src/` change), so it is now the combined
  tree's last `src/` commit, following the self-pin convention. a111a150
  moves no artifact byte, so 6b86a29b would also still have held. No other
  pin or manifest moves: the merge changes no emitted artifact.
- **Checked (Mac, gcc-16; light only, because a full `make test` was running
  in worktrees/k7980):**
  - `make`: clean.
  - `make strict`: "whole tree compiles clean with -Werror -Wshadow".
  - `tests/codegen/run_ir_listing.sh`: 155/0, including every BYTE-NEUTRALITY
    baseline.
  - `run_prefix_invariance.sh`: 9/0.
  - `run_nomatch_caps.sh`: 7/0. Same counts as §4: 238,870 non-success calls,
    27 dead-group DFA artifacts.
  - `run_codegen_tests.sh`: 130/0, covering `ABI_EXPECT=55` and SABANCHOR.
  - `scripts/m6read_check_sab_anchors.py`: 391 rows / 407 sites, all resolve.
- **OWED (manager, on Linux):** the full `make test`, `make mech` (S439 via
  `nomatchcaps`) and `make test-recursion-identity` against the new
  1a9d4eed pin.
