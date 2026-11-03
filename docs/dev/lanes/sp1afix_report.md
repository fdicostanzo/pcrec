# sp1afix report: FIX-NOW items of the unit 1a code review (2026-11-03 r3)

Lane sp1afix (branch lane/memfn-sp1afix, cut from lane/memfn-sp1a at c0c73bc20). Review text:
`docs/dev/reviews/2026-11-03-r3-memfn-sp1a.md` at b420f30af. Fix commit: 822b15c38. Unit 1a's emitted bytes are
unchanged by construction (the only code edit is deleting an unused enum bit and its listing letter).

## Fixes by id

- CHECK-1: `tests/memfn/reach_equal.py` compares the ROW SET (rows with any line) of each arm, BASE less the declared gone rows against HEAD; an absent line is no longer read as 0. A plant that drops the surviving zero-reach row `fd/D1c` from HEAD's trace FAILS (`derived gone set` and `row sets differ ... lost [('fd','D1c')]`); the real tree passes.
- CHECK-2 + SLOT-6: the gone set is DERIVED (rows with lines at BASE, none at HEAD, over all arms) and must equal `--gone` in both directions; each gone row's BASE chosen/asked per arm is printed (R3a, R3b, R4: all 0). Plants: `--gone` without R4 FAILS; `--gone` with an extra surviving row (fd:R1) FAILS; the empty declaration FAILS.
- CHECK-3: per (pattern, arm) the key->count maps are compared (paired as the two sides finish, so memory stays bounded), not population sums. Plant: HEAD wrapper adding 1 to one pattern's `fd/D1 site_kind` count and subtracting 1 from another's (sum preserved) FAILS with both patterns named in `DIFF:` lines.
- CHECK-4: a `--limit` run is a smoke run: skips nothing silently, its trailer is `reach_equal: LIMITED rc=N ...` (not DONE) and it exits 3 when clean, 1 when not, never 0. Shown on the real tree (exit 3).
- CHECK-5: compile return codes and timeouts are recorded; the SETS of failing patterns per arm must be equal at BASE and HEAD (cause compared too); an identical failure on both sides is printed with its count. Plants: HEAD wrapper exiting 1 on one pattern FAILS; HEAD wrapper hanging on one pattern (`--timeout 3`) FAILS.
- CHECK-6a: `definitions()` carries a has-body flag; `fn` and `part` members need a body. In-suite plant `plant prototype fd_route` (the function replaced by a bare prototype) turns A red (1 error); real tree green.
- CHECK-6b: `MEMBER_FLOOR` 45 replaced by the exact `MEMBER_COUNT` 50 (edit with the map). Plant: the map minus one row (`--map` new option) FAILS with "holds 49 members, not MEMBER_COUNT 50".
- CHECK-6c: `plant()` returns a labelled reason instead of a StopIteration traceback when its anchor/opener/closing brace is missing. Plant: window.c copy with the anchor respelled (`ms < bmX ||`) prints `FAIL: plant window.c: anchor ... is not in window.c (respelled? re-aim the plant)`, rc 1, no traceback.
- SLOT-1: finder_check.py header "the 16 rows" now "the 13 rows" (R8 R1 R2 D1 D1c D1w PAIR R7w P0 P2 P3 P4 P9).
- SLOT-3: memfn/CLAUDE.md states the deleted chain as UNMEASURED since span_pick 1a; the 13.7 KB / 47.1 KB history moved to the new memfn/NOTES.md.
- SLOT-4: KN_H, its name letter `H` in `needs_names` (now "PEAIMN") and the listing loop bound (7 -> 6) deleted from `memfn/src/finder.c`; grep of memfn/, tests/, src/, lib/ finds no other reader (no row carries KN_H, no test reads the alphabet; `needs[MF_FINDER_MAX][8]` unchanged). finder.c's "A3 at B9" reworded to "A3 with its first row"; finder_history.md line for R3a/R3b/R4 records the deletion.

## Checks run

- `make -j4` and an MF_TRACE build into the scratch dir: green.
- `make test-memfn-rows test-memfn-finder` on the fixed tree (log `/var/tmp/pcrec-pcrec/scratch/memfn/sp1afix/sections.log`): no `*** [test-` line; census 56 checks passed, 0 failed (55 before, plus the prototype plant), finder 0 failed.
- reach_equal.py smoke, `--limit 40`, 2 arms, BASE trace build vs the fixed tip: derived gone fd/R3a, R3b, R4; 0 differing patterns; LIMITED rc=0, exit 3. The plants listed above were each run with `--limit 40` (the plant wrappers live in the scratch dir, not committed).
- Not run: byte identity (owed, jobs below), `make test`, strict (the first, and the whole battery, are the manager's at merge).

## Queue jobs

Scripts in `/var/tmp/pcrec-pcrec/scratch/memfn/sp1afix/jobs/` (copied from sp1a's 302-305, pointed at worktrees/sp1afix, no not-before, base builds shared from sp1a's scratch, patterns files copied): 310-kit-sp1a-reach2 (18 arms, `--gone fd:R3a,fd:R3b,fd:R4` now derived-checked), then `after` chain 311-kit-sp1a-ident1b, 312-kit-sp1a-ident2b, 313-kit-sp1a-ident3b (23 of 69 identity arms each). Expect lines: reach `arms=18 lines=^arm ` and `done=1 lines=^reach_equal: DONE rc=0 `; ident `arms=23 last=^ident: arms run ` and `failed=0 last=^ident: arms failed `; every regex matches all labels its own job prints. All four dry-run clean. Job 301 (old tip) not waited on. OWED: all four verdicts (kit-sp1a-reach2 kit-sp1a-ident1b kit-sp1a-ident2b kit-sp1a-ident3b).

## STATE AT HANDOFF

Fixes committed (822b15c38 plus this report); witness jobs queued as the last act, results OWED. Unit 1a's PLAN items (CHECK-8, SLOT-7, SLOT-8) and the DOC item SLOT-2 are not in this lane. A fresh agent resumes by reading `scripts/boxqueue status` for the four keys and `scripts/verdict` on each log.
