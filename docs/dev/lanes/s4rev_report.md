# Lane s4rev — `[OPT-LITSCAN]` S4 C3 design revision (r1 light panel)

Lane `s4rev` (opus), 2026-10-03, branch `lane/s4rev` from main `92b8bbf0`.
Design only. Nothing under `src/`, `cli/`, `lib/` or `tests/` changed.

## Deliverable

`docs/design/litscan_s4.md` §2.3 is rewritten against
`docs/dev/reviews/2026-10-03-r1-litscan-s4-c3.md`. Every finding (S1-S4,
C1-C7) carries an in-place `[r1 X]` mark. §R1 is the disposition table.
§0 items 7-8, §2.4, §3 (bit 44), §4 (21 code readers by grep, the test
readers, 11 named spec hunks), §5.1 (the classification table and the
planned `reqcube.rxt` cells), §5.4, §5.5 (S447 re-aimed, S448-S452 new),
§6.2 (slack is no longer a C3 control; http-5xx added), §7-§9, and §10
Q4/Q5/Q8 are revised.

## The census (compile-only, Mac, bounded)

`docs/dev/optloop/s4/c3census/` holds a scratch prototype of the r1 walk
(`proto.patch`, never under `src/`). It was run against main over 3,898
corpus and 317 bench compiled patterns, with every compile under a 60 s
`timeout`. None fired.

| | corpus | bench |
|---|---|---|
| A1: no run → masked (round 0's population) | 15 | 8 |
| B: exact → the same exact run | 505 | 98 |
| B!: exact → a different exact run | 0 | 0 |
| C: exact → masked (new, single ranking) | 15 | 3 |
| C: caseless AND shadowed by an exact 2-run | 0 | 0 |
| C: pin lost / `run-pinned` selection moved | 8 / 2 | 2 / 0 |

So exact-only artifacts are byte-identical, and the biconditional still
holds (moved ⇔ masked). The C4 shadowing is 2 artifacts (`slack`,
`(?i)x/1234`). Class C is mostly the S1 hull on exact branches
(`frank|fred` → `fr[ae]`).

## Shape changed beyond the fixes: YES (three items, §R1)

1. The run's position domain is narrowed to a byte or a two-member cube.
2. The single ranking moves `dfa_pfs[]` INPUTS: 10 pins and 2 corpus
   selections (`a[bc]de`, `(?i)x/1234`, `run-pinned` → next row).
3. The hull makes exact-branch alternations masked movers.

Recommendation (Q4): a second LIGHT round with two lenses, answer soundness
(the hull and the pair arm) and selection semantics (the 2 moved
selections).

## Not done / owed

- No `make` beyond a plain build of the branch point, and no test suite run
  (design only).
- The S2b L = 30 witness's libpcre2 answer (NOMATCH or match-limit) is owed
  to the build lane as one light 10.46 probe.
- The utf8 observation (the walk does not join a run across a lowered
  multi-byte caseless class) is named as a possible separate row. It is not
  filed.
