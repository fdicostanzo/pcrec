# CRITIC check-adequacy (sonnet): arenaf3
Read /var/tmp/pcrec-pcrec/scratch/crit-arenaf3/COMMON.md FIRST. Your NAME for lanecheck: `checks`. Your file:
/var/tmp/pcrec-pcrec/scratch/crit-arenaf3/checks/findings.md (pre-created; APPEND). Scratch: checks/ only.
Finding ids: CHECK-n. This lens OWNS the round's plants (plant:S3572, plant:S3584, plant:Vnb, plant:Vo).

THE ONE QUESTION. Per check the subject changes - the scanner (tests/core/scratch_builder_check.py: three ALLOW rows
and the `shape:NAME` narrowing deleted, MUST_FLAG fixtures rewritten, `MIN_SCOPE_OPENS` 2 -> 3), alloc_check.c (the
`known_stranded` table, its stack recording, exit code 5 and stale-row loop deleted; W6 pinned 1010 -> 1014 of 1057),
sabotage rows S3572 (re-aimed at S11 `tail`, new file name) and S3584 (re-aimed beside `lines`) - what input makes
it fail, does its witness reach the site, and is its population counted (docs/dev/learnings.md section 3)? Run each
plant through the net its row names AND through the other net, and classify (scanner FAIL / alloc stranded FAIL /
silent); the design says S11 and S12 are SINGLE-CONTROL (D-8) and S10's dynamic witness is alloc_check: do plant:Vnb
and plant:Vo agree? Does any deleted piece (the per-name narrowing, the per-declarator fixtures, the stack recording)
still guard something in the remaining ALLOW rows or the remaining code? Run
`python3 -I scripts/m6read_check_sab_anchors.py` against the review tree (read its usage first; it is read-only).

Sub-part (b) TRADE AUDIT: W6's pin moved UP by 4 and MIN_SCOPE_OPENS moved; what did each give up, who judged it
(D110), and are the moved numbers' every reader consistent (grep 1010/1014/1045/1057, MIN_SCOPE_OPENS, S3572 across
the tree, excluding the denylist): docs/testing.md, tests/core/CLAUDE.md, the scanner header, known_issues.md K155,
the design's F3 row and Deviations bullet?
