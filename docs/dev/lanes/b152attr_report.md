# b152attr report (lane b152attr, sonnet)

## Summary

Bench window b152 (O-122, pcrec-bench outbox) named regressed cells and two prep questions. This lane reads the
emitted C only; it times nothing. The box lock was held by the bench's `make check` job
(`queue:700-bench-b152chk`, from 08:11, about one hour), so the build-bound runs are queued, not done.

- Task 3 (`char-step` has no `locate` row): ANSWERED below; it should have one. It is an omission, not a ruling.
- Task 1 (attribution) and Task 2 (landmark walk size): answered below (object-code comparison; walk size measured).

## Regression attribution

Method (rerun, semantic): the first-parent range cb32eda28..d6c5e71a5 was bisected (bisect.log "BISECT DONE", changes.json) to
six merges where some cell's comment-stripped emitted C moved; this rerun then BUILT the compiler at the probe points
(idx 0,20,21,24,25,29,30,33,34,35,39,40,57 = cb32eda28 .. f27256133; `git diff f27256133 HEAD -- src cli lib memfn/src` is empty,
so 57 IS main's code), emitted the nine cells (`-p rx --features all`, bench plain arm), compiled each with `gcc -O2 -c`,
and compared `objdump -d` text with addresses stripped (scratch `sem.py`, `sem.json`, `sem_<idx>/<cell>.{c,dis}`). Only 4 of
the 6 merges change any object code; cf578177e (abi 98, +34 B of C) and e30a31174 (famland, +18 B) change stamps only (every cell:
identical instruction stream, identical .text/.rodata sizes). Resolution is the merge, not the lane commit inside it
(`git log MERGE^1..MERGE^2` to go further; not done, no timing here).

Executable changes (instructions in `.text`; ro = .rodata+.data bytes):

| merge | what changed in the executable program |
|---|---|
| f7eb10528 sar1mrg "span arms R1" (idx 25) | qnt-poss-plus: required-run search changed from 2-byte `ab` (memchr 'b' at +1, memcmp) to 3-byte `aab`@2 (memchr at +2, two rx_w2 word compares): +9 insn. username-password-pair: the `rx_reqrun` handoff pre-filter (a two-sided U/u memchr hunt, `RX_DFA_PREFILTER "handoff"`) is GONE, now `"byte-class"`: -90 insn, ro +259 B. Other seven cells: no change. |
| 51481d1b3 s1land (abi 100->103) | one new early-out `if (subject_length - search_from < W) return 0;` plus a hoisted `attempt_max = subject_length - W` that replaces `subject_length` in the per-attempt bound test `attempt_position >= attempt_max` (W = min match width: 3, 3, 3, 3, 3, 4, 77; cls-range gets width guards at two places). Same engine, same tables (ro unchanged); +6 to +89 insn (rec-fwd +89: the guard lands in more search sites). username-password-pair +9 insn. dig-exact-8: nothing. |
| 7c16349d7 memfn-k382 (abi 103->104) | slack-webhook-url only: its required-run literal widens from `RVICES/T`@6 to `COM/SERVICES/T`@12 (memchr '/' at +12, one rx_w8 compare at +6; handoff slack 26->20). cls-range: object code unchanged (stamp/text only). |
| 9cecc3caa RUN-POS-SET S2 (abi 105) | cls-range: gains a real required-run prefilter (`RX_DFA_PREFILTER "offset-set"` -> `"run-pinned"`, a new `rx_reqrun` function: memchr 'x' then `0x`+hex-class check, called before the scan; the per-candidate test `subject[cand]==48` becomes `memcmp("0x",2)`): +30 insn, +128 B text. slack-webhook-url: its required run grows from 14 to ~24 bytes and the word compare becomes 6 per-byte class tests on subject[cand+16..21] plus one rx_w2: +91 insn, +416 B text. |

Per cell (ranked, most plausible cause first; "none" = no executable change in range):

- dig-exact-8 (+34 % large, +75 % short): NO executable change at all. Object code and rodata are byte-identical at cb32eda28 and
  at main (339 insn, 1160 B text, 304 B ro); only stamps/comments differ. It was already `RX_DFA_SCAN "cover"` at cb32eda28. The program
  the bench times did not change in this range, so the cause is outside the emitted C (the bench's own build/flags, the testee compile, or
  a box/noise effect the cross-window null does not cover). Not a pcrec-program cause.
- grp-cap, grp-named, grp-named-quote (+13 to +17 %): ONE executable change, 51481d1b3 (s1land): +31 insn, +96 B text, a
  min-width early-out and an `attempt_max` bound in the search loop. The three cells are the same program (identical instruction
  hash 3ca945eab918). The change is a cold prologue compare plus a loop bound held in a different variable, so the plausible
  mechanism is a code-layout or register-allocation shift in the per-attempt loop, not extra per-byte work; a +13-17 % move from
  that alone is larger than the diff suggests, so a box effect near the +4-7 % null cannot be excluded. Timing needed to settle.
  Candidate single commit: whichever s1land lane commit added `attempt_max` (`git log 51481d1b3^1..51481d1b3^2`).
- rec-fwd: same single cause, 51481d1b3, larger footprint (+89 insn, +288 B text; the guard appears at more sites). Most plausible of the five by size.
- qnt-poss-plus: TWO executable changes. Rank: f7eb10528 first (the required run `ab`@1 became `aab`@2: a different search form with a
  two-word compare per candidate, in the hot candidate loop, +9 insn), 51481d1b3 second (the s1land guard, +7 insn).
- cls-range (+18.6 % large): TWO executable changes (7c16349d7 moves no object code here). Rank: 9cecc3caa first (+30 insn: a new
  required-run prefilter `rx_reqrun` before the scan, `offset-set` -> `run-pinned`, and `memcmp("0x",2)` per candidate; hot-path work
  on a cheap scan), 51481d1b3 a distant second (+7 insn, cold guards).
- wild-secrets-slack-webhook-url (+15.3 % large): THREE changes. Rank: 9cecc3caa first (+91 insn: per-candidate verify went from one
  word compare to six class tests plus one word compare), 7c16349d7 second (longer required literal, memchr hunt moves from +6 to +12,
  changes how often candidates are rejected; same instruction count), 51481d1b3 last (+6 insn, cold).

Also moved, not in the task list: username-password-pair (f7eb10528 dropped its handoff prefilter; 51481d1b3 +9 insn).
Every "plausible" above is from the diff alone; this lane timed nothing.

## Landmark walk size

Reproduced at main's code (build f27256133; `git diff f27256133 HEAD -- src cli lib memfn/src` is empty), nocaps plain,
`-p rx --features all --no-captures`: default .c = 604,426 B, `-fno-landmark-walk` = 560,122 B, delta +44,304 B. The bench's
609,262 / 564,961 are about 4.8 KB higher in both arms (its own emit/wrapper, not reproduced; `--emit-main` gives 605,239 / 560,935),
with the same +44.3 KB delta. The `.h` is 15,872 B in both.

Where the +44,304 B is (static table sizes in the emitted C, default minus denied):

| piece | bytes | what |
|---|---|---|
| `rx_lmverify_*` tables (byte_class, next_state[3200], is_accepting[3200]) | 36,281 | the second anchored copy |
| `rx_landmark_*` tables (next_state[289], byte_class, is_accepting[289]) | 4,767 | the reverse machine of P followed by L |
| walk code (landmark loop, lmverify loop, scan97 table, typedefs/inlines) | 3,256 | remainder |
| total | 44,304 | |

Every other table is identical in both builds (`rx_forward` 452,893, `rx_reverse` 53,051, `rx_anchored` 36,281).

Verdict: by design in KIND (tuning.md 2.54 p1/p5 name exactly these two; [LANDWALK] stage 1 landed them), but there IS
excess within the design: the `rx_lmverify_byte_class`, `_next_state` and `_is_accepting` tables are BYTE-IDENTICAL to
`rx_anchored_*` (checked by comparing the array bodies; same stop threshold 3104). The walk emits a second copy of the very same
tables instead of referring to the existing ones. So 36,281 of the 44,304 B (82 %) is a verbatim duplicate, avoidable without
changing any answer; the reverse machine (4.8 KB) and walk code (3.3 KB) are the genuine cost. The size cap also counts the
duplicate (2.54 p5), so a pattern near the cap loses the walk (`drop-landmark-walk`) for bytes that carry no information.
One pattern measured; whether the identity holds for every admitted pattern is not checked.

Draft plan row (not filed; manager to decide):

    - [LANDWALK-SHARE] STATE:not-started - the walk's verify machine reuses the anchored machine's tables instead of a second copy
      filed: 2026-11-24 lane b152attr2
      trigger: a measured size or compile-cost mover (b152 username-password-pair: 36,281 B of the 44,304 B is a verbatim duplicate); size-cap refusals of landmark-walk artifacts in [LANDWALK-CENSUS]
      refs: docs/spec/tuning.md 2.54 p1/p5; docs/spec/limits.md 8.4 (drop-landmark-walk); [LANDWALK-CENSUS]
      Emit one table set when the walk's verify machine equals the anchored machine (same DFA, same stop threshold), keep two only
      when the walk specialises it. Emitted-scaffolding change = abi bump + identity re-pin (D76/D94); spec hunk for 2.54 p1/p5
      ("its tables again" becomes "its tables, shared with 2.15's where identical").

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

- Rulings file `docs/dev/lanes/b152attr_rulings.md`: empty at last read, no entry applied.
OWED: none
- All three tasks answered. Scratch worktree `$PCREC_TMPDIR/scratch/b152attr/wt` (registered in the main repo's
  worktree list) is still there; remove it with `scripts/wtprune`.
- Not done: lane-commit resolution inside the four named merges (`git log MERGE^1..MERGE^2`); no timing.
