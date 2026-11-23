# l3axtri report: red cloud axes run 44946077375 (kind axes, sha fcf710c02)

## Verdict
Class (b), a stale pin, NOT an L3 answer change and NOT a shard-table defect in the flag rows. Only `shard (1/20)` and `gather` failed. The failing section is the D3-FLOOR gate (`tests/memfn/run_d3floor.sh`, the last step of the axes baseline in shard 1), red on all four cells. No axis flag row failed (the seven axis units of shard 1 all ran; units.tsv). The fix is `D3FLOOR_REPIN=1 bash tests/memfn/run_d3floor.sh` plus committing d3_census.tsv and d3_floor.tsv. It is NOT applied here (see Fix).

## Failing jobs
Shard 1/20 rc=1 (wall 3410 s); gather RED only because shard 1 was. Artifact cloud-shard-1of20 test.log:
- byte/c-default: compiles 5277 vs pinned 5163 (+114), failed 487 vs 486 (+1), records 452 vs 433.
- byte/c-vm: compiles 5278 vs 5164, failed 486 vs 485, records 1334 vs 1253, census 213 vs 206.
- utf8/c-default: compiles 5348 vs 5233, records 600 vs 566.
- utf8/c-vm: compiles 5325 vs 5210, records 1457 vs 1375, census 287 vs 280.

## Diagnosis
Reproduced locally on this branch (build at fcf710c02 + report): the same numbers on all four cells (run_d3floor.sh, d3check.log).
Every moved number, by name:
- Corpus +114 compiles: the L3 D27 witness file tests/lookaround/d27_l3/l3d27_witnesses.rxt (284 pattern lines in the corpus), wired into make test by 8a4bc96d6 after the last pin move (548b2a7ac, 2026-11-20). make test does not run D3-FLOOR, so that landing was green without a re-pin.
- Failed +1 (byte cells only; utf8 unchanged): `(?<=a)\x{100}` from l3d27_witnesses.rxt. "failed" in D3-FLOOR (d3_floor.py failed_count) is any corpus compile with rc != 0. This pattern is refused in byte mode ("code point value in \x{...} is too large (max U+00FF under encoding 'byte')"); main's build/pcrec (dd8107f47) gives the identical refusal, and utf8 compiles it. A designed refusal on a new corpus row, not an L3 regression (class a ruled out).
- c-vm census GAINED 7 (both byte and utf8): `(?<=\d{3})x`, `(?<=ab)c|(?<=ca)b`, `(?<=abc)\d`, `(?<=ab|cd)ef`, `(?<=ab|cde)f`, `(?<=foo|bar)baz`, `(?<=xy)\w+`: L3's designed effect (a lookbehind's fixed bytes join the required run under --engine=vm), now also reached by the d27 witnesses.
- Records +19 / +81 / +34 / +82 follow from the same added patterns.
Why cc96bb7a8's earlier axes run passed: cc96bb7a8 and fcf710c02 differ only in tests/ci/cloud_axes_shards.tsv, cloud_mech_shards.tsv and a report (no code, no corpus). I could not find that earlier axes run among `gh run list` (latest 40 show only its mech and test runs, both green; D3-FLOOR is in neither). So it is NOT shown that it ran D3-FLOOR; most likely it ran a different scope. The table regen did not change which shard runs D3-FLOOR (no d3 row in the table; it rides shard 1's baseline).

## Fix
None committed. The re-pin is a suite-sized sweep (about 2 min plus a build) and the brief's cutoff for suite-sized runs (19:45) had passed when the diagnosis finished. OWED, exact: on lane/l3axtri or lane/l3pop, `D3FLOOR_NOTE='L3 d27 witnesses wired (8a4bc96d6) + L3 vm census' D3FLOOR_REPIN=1 bash tests/memfn/run_d3floor.sh <tree>` under boxlock, review the printed diff (must show exactly: the 7 gained members above, byte failed +1, no member lost), commit d3_census.tsv + d3_floor.tsv, then rerun the check green. Allowlist rule: `git log --since=14.days` on those files shows two re-pins (548b2a7ac for L3, 47ba76682 for L1), different causes; this would be the third in 14 days. Scope defect worth a ruling: any landing that grows the corpus or moves a lookbehind site must run test-memfn-d3floor, which make test does not.
Not a main red: main's pin matches main's corpus; the +114 rows exist only on the L3 branch.

## Validation
- Failing numbers read from the CI artifact (test.log) and reproduced locally with identical output.
- Failed pattern identified from the kept sweep (byte_c-default.jsonl rc != 0 rows for lookaround notes); main refusal confirmed by running its build.

## STATE AT HANDOFF
Rulings file empty (no R-n applied). No src/ or pin edit. Scratch: /var/tmp/pcrec-pcrec/scratch/l3axtri (logs). Re-pin OWED as above; no cloud dispatch made.
OWED: none (the re-pin above is a follow-up for main to dispatch, not a run of this lane)
