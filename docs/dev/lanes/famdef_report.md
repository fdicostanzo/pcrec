# famdef report: [FEAT-FAMILIES] pre-move work; default NOT moved (lane famdef, sonnet, 2026-11-10)

## STATE AT HANDOFF

**Default NOT moved; no frozen member added.** Reasons below (section "Why the move is held"). What IS delivered:
the two owed differentials, the widened fuzz, the release checklist draft, all committed on lane/famdef. Validation of
the new checks is OWED as queued jobs (the full suite holds the box until ~08:00 Wed).

### 1. Owed pre-move checks (D37 addendum 2026-11-06)

| check | built | verdict |
|---|---|---|
| quoting vs libpcre2 10.46 | `tests/families/run_quoting_diff.sh` (+ `module_diff.sh`): 43 patterns x 628 subject/startpos cells = 27,004 cells, span and group spans; 5,149 matching cells; 14 accept/refuse agreements | ran ONCE locally while building it: 27,004/27,004 agree, 14/14 refusals agree, 0 divergences (single process, not a box-lock run). Queue job `410-main-famdef-quoting` OWED for the queued record |
| named-groups vs libpcre2 10.46 | `tests/families/run_named_diff.sh`: 39 patterns x 553 = 21,567 cells; 5,719 matching; 20 accept/refuse agreements (three spellings, numbering with `(?n)`, `\k` `\g` `(?P=)` refs, lookbehind neighbours, `(?J)` duplicates, 40-char names) | ran ONCE locally: 21,567/21,567 agree, 20/20 refusals agree, 0 divergences. Queue job `411-main-famdef-named` OWED |
| fuzz widened to the set | `tests/fuzz/fuzz.py --set extended`: 60% of patterns from `EXTENDED_TEMPLATES` (lookaround, atomic, backrefs, named groups, `\Q..\E`, inline modifiers, assertions, pairwise nestings), compiled with the `extended` family's module list written out; default `--set base` stream unchanged (extra random draw only in extended mode) | smoke only: seed 7, 40 patterns (33 both accept, 495 subject pairs): 0 content, 0 accept/reject divergences. Campaign seeds 1-4 x 1500: queue job `412-main-famdef-fuzzext` OWED (it exits nonzero on any divergence) |
| fixed-seed slice in `make test` | NOT built. The addendum asks for it; it needs the family NAME to exist (or the explicit list pinned) and a decision on cost. Left for the owner's call | OWED/NOT DONE |
| `make test` on the lane (san_excluded entries, CLAUDE.md sizes, fuzz.py edit) | queued `413-main-b20261110180211618330.test` | OWED. Local: `make strict` green, `make test-plan-lint` green, `check_claudemd_size --all` green |

The differentials found nothing to fix. They are opt-in (not in `make test`), listed in `tests/lib/san_excluded.txt` as OWN-TIER.

### 2. Graduation criterion

The criterion in the lead's brief (panel + PC-3 per module) was RETIRED by the D37 addendum of 2026-11-06 (decisions.md; lane gradthink): a module
is in a family's next frozen member iff it is BUILT at the cut, and a release checklist replaces the per-module verdict. So the check I made
is the addendum's: built status per module from `build/pcrec --list-syntax` (rows built / rows), against the design's section 7 table.

| module | built rows | in family | built at the cut? | note |
|---|---|---|---|---|
| classes, modifiers | 12/12, 12/12 | basic | PASS | (std1 today) |
| quoting | 2/2 | basic | PASS | no landing panel as subject (gradthink G1); differential now exists (above) |
| named-groups | 3/3 | basic | PASS | no landing panel as subject (G2); differential now exists |
| ucp | 3/3 | basic | PASS | |
| unicode-props | 2/3 | basic | PASS by the lean in gradthink Q2 (missing row `\N{U+hhhh}` stays "not implemented yet"); needs the owner's confirmation |
| assertions | 7/7 | basic/extended | PASS but see `\K` below | K74 open (utf8 end-of-ill-formed subject) |
| atomic-groups, backrefs, lookaround | 5/5, 13/13, 18/18 | extended | PASS | |
| recursion | 36/36 | pcre2 | PASS | |
| conditionals, branch-reset | 0/1, 0/1 | extended | FAIL (unbuilt) | not in any frozen member under P2 |
| verbs | 0/1 | pcre2 | FAIL (unbuilt) | not in any frozen member |
| misc, comments, extended-classes | 0/5, 0/1, 0/1 | basic | FAIL (unbuilt) | not in any frozen member |

### Why the move is held (blockers; the owner decides)

1. **`\K` is still in module `assertions`.** Frank ruled (2026-11-06) `\K` its own module; `--list-syntax` still shows `\K` under `assertions` (`vm`).
   Freezing `extended1 = {..., assertions, ...}` first and splitting `\K` later would make `extended1` stop accepting `\K` (its list no longer enables it): a
   frozen-set violation. The split (new FEAT bit, module name, registry row, corpus `features` lists, `--list-syntax`/compliance pins, spec) is a build
   needing a name and its own go; I did not start it. It must land BEFORE the first freeze.
2. **K74** (open wrong answer, `assertions`, `-e utf8`, ill-formed subject end): the addendum says "documented at the move"; needs the announcement text, not a lane.
3. **Unbuilt members**: under "frozen = BUILT" the frozen members are smaller than Frank's definitions (extended1 lacks conditionals/branch-reset; pcre2-1
   lacks verbs). Consistent with the ruling; stated here so the announcement says so (`pcre2-1` must not be read as "all of PCRE2").
4. **Owed runs** (section 1) have not been read; item 2/3 of the checklist are not discharged until they are green.
5. Frozen members would also need the abi/identity ritual (stamp text carries the set name) and spec hunks (cli.md 1.17, pattern_language.md 2.3, match_api.md 8.2);
   those are written together with the move, not before.

Proposed member lists once 1 is done (explicit lists, never references): `basic1` = classes, modifiers, quoting, named-groups, ucp, unicode-props, assertions-without-`\K`;
`extended1` = basic1 + `\K`-module, backrefs, lookaround, atomic-groups; `pcre2-1` = extended1 + recursion. Bench effect (design section 5, MEASURED 2026-11-06):
229 -> 333 of 392 compile with `extended`.

### D37 addendum text for main

The 2026-11-06 addendum already stands. Suggested ONE-LINE additions when appended: "Prerequisite recorded 2026-11-10 (lane famdef): `\K` becomes its own module BEFORE the first frozen member is shipped, so a frozen member's accepted language cannot lose `\K` to a later split; the quoting and named-groups differentials exist (`tests/families/`) and the set-alphabet fuzz exists (`fuzz.py --set extended`)."

### Announcement draft (for the move, main + owner publish)

> pcrec <version>: the bare default feature set moves from `std1` to `extended` (frozen as `extended1`). A pattern that
> compiled before still compiles with the same matches; patterns using lookahead/lookbehind, atomic groups, backreferences,
> `\b`-family assertions, named groups, `\Q..\E` and Unicode properties now compile without a flag. To keep the old behaviour pass
> `--features std1` (or `none`). `extended1` lists only modules that are built today: conditionals and branch-reset groups,
> verbs, `(?#...)`, `\R \X`, and `(?[...])` are not in it. Recursion is in `pcre2-1`; callouts and `${var}` are in `all` only.
> Known divergence: the `$`/`\B`/`\z`/`\Z` assertions at the end of an ILL-FORMED subject under `-e utf8` differ from PCRE2 (K74).

### Jobs queued (all OWED, not read)

`410-main-famdef-quoting`, `411-main-famdef-named`, `412-main-famdef-fuzzext`, `413-main-b20261110180211618330.test` (make test via perfrun). Completion: each job's
`done/` entry (`scripts/boxqueue state KEY`); verdict via `scripts/verdict` on its log.

### Files

`tests/families/{module_diff.sh,run_quoting_diff.sh,run_named_diff.sh,CLAUDE.md}`, `tests/fuzz/fuzz.py` + README, `tests/lib/san_excluded.txt`, `tests/NOTES.md`,
`docs/dev/release_checklist.md` (DRAFT) + `docs/dev/CLAUDE.md` pointer. No `src/`, spec or decisions.md edit.
