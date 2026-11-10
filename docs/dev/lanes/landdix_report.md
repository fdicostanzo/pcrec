# landdix report: merge lane/dixt1 into main

## STATE AT HANDOFF
- Merge commit 81449f5a0 (main, local). Not pushed: `gh run list` shows CI in_progress (push owed).
- Conflicts (all docs, resolved as a UNION): docs/dev/history/claude_md/docs__dev__lanes.md (both report lines kept), scripts/CLAUDE.md (Checkers line merged: entry + doc_profiles.py + doc_census.py/doc_control.py), tests/CLAUDE.md (both doc_lint bullets), tests/doc_lint/CLAUDE.md (add/add: rewritten to list both lanes' files and run paths). No code conflicts. 0 conflict markers.
- Checks on the merged tree: make test-doc-lint "checks passed: 2 / failed: 0" (entry selftest 48 checks, 0 failures); run_doc_index.sh "DONE rc=0" (5 passed); make test-plan-lint "341 rows, 0 violations; 38 plants, 0 failures"; check_claudemd_size --all "363 files within limits"; gestalt.test "54 pass, 0 fail"; scripts/entry --help prints usage; `scripts/entry D26` prints "profile decisions dormant (unit 1)" rc 0 (-i is not a T1 flag).
- OWED: `make testscripts` via boxlock (label landdix), queued behind queue:532-kit-k381g-ident2; log /var/tmp/pcrec-pcrec/scratch/landdix/ts.log (still WAITING at handoff).
- Pruning of dixt1 dix10 docfmt gquiet gidle flr: NOT done (deferred until the owed run is green).
