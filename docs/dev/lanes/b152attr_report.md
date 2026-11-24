# b152attr report (lane b152attr, sonnet)

STATE: stopped (compile-only runs OWED behind the box lock; tasks 1 and 2 have no result yet, task 3 is answered)

## Summary

Bench window b152 (O-122, pcrec-bench outbox) named regressed cells and two prep questions. This lane reads the
emitted C only; it times nothing. The box lock was held by the bench's `make check` job
(`queue:700-bench-b152chk`, from 08:11, about one hour), so the build-bound runs are queued, not done.

- Task 3 (`char-step` has no `locate` row): ANSWERED below; it should have one. It is an omission, not a ruling.
- Task 1 (attribution) and Task 2 (landmark walk size): OWED, one detached job already waiting on the lock.

## Regression attribution

OWED. Job: `scripts/boxlock run --label b152attr-bisect -- python3 -I $PCREC_TMPDIR/scratch/b152attr/bisect.py`,
waiting on the lock since 08:28 (log `$PCREC_TMPDIR/scratch/b152attr/bisect.log`; completion line `BISECT DONE`;
results in `changes.json` beside it, each entry (index, commit, cells whose comment-stripped emitted C changed)).

Method as built: the first-parent history `cb32eda28..d6c5e71a5` has 5,579 commits, of which 57 first-parent merges
touch `src/`, `cli/`, `lib/` or `memfn/src/`. The script builds `build/pcrec` at each probe commit in a scratch
worktree (`$PCREC_TMPDIR/scratch/b152attr/wt`, `nice make -j8`), emits the nine cells with the bench's plain-arm flags
(`-p rx --features all --pattern P`; the bench's `pcrec-auto` testee), hashes the emitted C with the first line and the
`.abi` line removed (raw hash, and a comment-stripped hash it bisects on), and recursively splits every interval whose
endpoints differ. A cell whose hashes agree at both ends has no program cause. Pattern texts are the `pattern` line
above each `name` line in the bench's `bench/*/export/*.rxt` and `bench/capability/patterns.rxt` (copies in
`scratch/b152attr/pat/`).

Facts already read with the cb32eda28 binary (abi 93): `dig-exact-8` is ALREADY `RX_DFA_SCAN "cover"` there, so the
bench's "abi 92 cover" is not the commit for the +34 %/+75 %; the cause is a later change and the job will name it.
Old emit sizes (bytes): dig-exact-8 12,067; cls-range 20,879; grp-cap 21,279; wild-secrets-slack-webhook-url 103,923;
wild-secrets-username-password-pair 551,825.

When a first-parent merge is named, the exact lane commit is found by repeating the search over that merge's
second-parent range (`git log MERGE^1..MERGE^2`), same script shape.

## Landmark walk size

OWED (needs a build). What is known from the spec: `tuning.md` §2.54 `-fno-landmark-walk` (bit 57): the walk adds a reverse
machine of the prefix P followed by the landmark L (tables `<prefix>_landmark_*`) and a SECOND COPY of the anchored machine
(`<prefix>_lmverify_*`); §2.54¶5 states both count toward the emitted-size caps and `limits.md` §8.4 row 2a
(`drop-landmark-walk`) removes exactly these two when a cap refuses. So growth of the order of the pattern's own anchored
machine is by design. Plan row: [LANDWALK] (stage 1 landed at abi 95; its census child [LANDWALK-CENSUS] is
not-started and is the row that owns "compile cost over the admitted corpus"). What stays to decide after reproducing:
whether +44.3 KB is about one anchored-machine copy plus a reverse machine (as designed) or exceeds that, and whether
the admission's size term sees it. Reproduce with the d6c5e71a5 build, `--features all --no-captures`, default vs
`-fno-landmark-walk`, and compare the `<prefix>_landmark_*`/`<prefix>_lmverify_*` table bytes to the anchored tables.
The 13 KB between cb32eda28's 551,825 and the denied arm's 564,961 is a separate, earlier mover (the bisect job's
nocaps variant will cover it if added).

## char-step locate row

Should it have a row: YES. Why it is absent: an omission in the candidate table. `locate` rows in `--list-axes` come from
`pcrec_cand_list_row` (`src/gen/emit_dfa.c`), which lists exactly the `cand_rows[]` entries that carry a `.list`
member for the axis (rev-end 1, cover 2, landmark-walk 3, unanchored 4). The `char-step` entry (U3, lane ucax3,
D134/D174) was added as a LOCATE row with `.scan "char-step"` and no `.list` and no `.desc`, so the listing walks past it.
No test catches it: the registry value-set pairs (`tests/registry/axes_registry_check.sh`) cover `RX_DFA_SCAN_EDGE`,
`RX_DFA_START` and others but not `RX_DFA_SCAN`, and `attempt` (an `ENG_ATTEMPT` body) is likewise unlisted.
The stated rule at the `locate` call in `src/dump/axes_dump.c` is "the LOCATE rows that are a choice", with `empty`
excluded because no flag can make it; `char-step` is admitted by population (no all-byte form), has no deny bit, so it is
`empty`'s case by that rule and `cover`'s by the registry's (cover also has no flag, and is listed). The caller-facing
stamp `RX_DFA_SCAN "char-step"` (`match_api.md` §6.3.4¶2) is a value a reader sees, which is what the registry's
"one row per stamp value" (`registry.md` §6) is for. Draft row (not applied, registry untouched):

    locate  1  char-step  list  RX_DFA_SCAN  char-step  (deny: none)  (cli: none)
      applies: the pattern needs a character set that is not byte-expressible under -e utf8 (UCP \b/\B, cli.md §1.9¶7):
      ASCII bytes step the table, a whole non-ASCII character is one symbol, the end is found by the forward walk and the
      start by the reverse machine stepping back the same way; first and alone on its population (no all-byte form exists);
      no flag denies it

Source edit it implies: `.list = { [CAND_ROUTE_DFA] = { "locate", 1, "char-step" } }` plus a `.desc` on its `cand_rows[]`
entry, with rev-end/cover/landmark-walk/unanchored renumbered 2..5 (a registry listing change: re-pin the registry
expectations and the `docs/spec/registry.md` §6 examples by grep). Alternative with no renumbering: order 5 with a
note that the walk order is by `cand_rows[]`, but the axis states PREFERENCE order, and char-step is walked first.
Plan row to propose (not filed): [LOCATE-CHARSTEP-ROW] "list `char-step` on the `locate` axis (order 1), add a registry
check that every `RX_DFA_SCAN` value is a row or a named non-choice (`empty`, `attempt`)".

## STATE AT HANDOFF

- Rulings file `docs/dev/lanes/b152attr_rulings.md`: empty at last read (08:5x), no entry applied.
- Task 3 answered above. Tasks 1 and 2 OWED to the queued job (bisect.py; label b152attr-bisect, waiting on the lock).
- A fresh agent: read `bisect.log` for `BISECT DONE`, read `changes.json`, name each commit and its plan tag
  (`git log -1 COMMIT`, `scripts/entry`), then build the final binary from `scratch/b152attr/wt` (checked out at the last
  probe) for Task 2 and re-run this report's two OWED sections. The scratch worktree is registered in the main repo's
  worktree list: remove it with `scripts/wtprune` when done.
