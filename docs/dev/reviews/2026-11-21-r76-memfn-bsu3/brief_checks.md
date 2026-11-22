# CRITIC CHECKS (opus): r76 memfn-bsu3

Read /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/COMMON.md first (including its "R75 ITEMS" section at
the end). Your lens dir: .../crit-memfn-bsu3/checks/
Findings file (pre-created, APPEND only): .../crit-memfn-bsu3/checks.md. Deliver file: .../checks_deliver.txt.
You OWN the round's plants: no other lens plants.

## Your ONE question
Per new or changed check in U3: what input makes it fail, does its witness reach the site it guards,
and is its population counted (learnings §3: docs/dev/learnings.md §3 at SUBJECT)?
The checks: (1) S3515 (new) and the C18 -O0 rule + control (1) in `tests/memfn/simd_floor_check.py`
(its new head family `SELECTOR`/`HELPER`, the `_b` name form); (2) S730's re-aimed REACH (the V
witness line); (3) S693's re-aim; (4) `simd_guarded_check.py`'s NAMED `vspan` witness and
`simd-form-named` 8 -> 9; (5) `simd_bounds.tsv` row `span-vector-w32 1700`, a "BOUND BY CONSTRUCTION"
(attack the construction: is 1,605 really the worst instance? several V sites in ONE artifact, the
largest handle digits, a scan row, `-e utf8`, a long prefix offset, a different prefix `-p` length);
(6) `span_vector_identity.py`'s changes; (7) `run_recursion_identity.sh`'s FILEPIN; (8) the two
`c4_allowlist.tsv` rows; plus any R75 ITEM that COMMON assigns to CHECKS.
- sub-part (a) plants: classify every plant compare SAME / SILENT-MOVE (rc 0, bytes differ) / LOUD
  (rc != 0), deleting old outputs before each compare. Prebuilt: `plant:S3515`, `plant:S730`. For a
  mutation of a CHECK SCRIPT (delete or invert one clause of the new head-family regexes, the `_b`
  form, the -O0 rule), copy the script into your lens dir and run the copy. For a mutation of the
  KIT, mutate the EMITTED C (an artifact copy) rather than asking for a rebuild; if you truly need a
  planted compiler, SendMessage `crit-memfn-bsu3` with the exact BEFORE/AFTER and continue meanwhile.
- sub-part (b) run `python3 -I /home/pcrec/projects/pcrec/scripts/m6read_check_sab_anchors.py` against
  the review tree (the subject moved and respelled window.c text: does any sabotage row's
  SAB_BEFORE/anchor still match exactly its SAB_COUNT, and does any row quote a body the subject
  re-indented?).

You MAY run, from the review tree or a plant tree, ONLY these check scripts directly (never make):
`SIMD_FLOOR_JOBS=2 nice bash <TREE>/tests/memfn/run_simd_floor.sh <TREE> --every 25` (with
`PCREC=<plant compiler>` for a plant) and `nice bash <TREE>/tests/memfn/run_simd_guarded.sh` if its
--every can be set to >= 25 and jobs to 2 (read it first); each such run counts 100 compiles.
Plant trees: /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/plants/<ROW>/tree (full source + build).
Compile cap: 400 compiles in total. State your matrix product before running it.
