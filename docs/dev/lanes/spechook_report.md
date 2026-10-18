# Lane spechook: conditional spec gate in the pre-commit hook

Branch `lane/spechook`. Opt-in hook only; NOT installed anywhere.

## What changed
- `tests/spec_history/spec_history.py ROOT --staged` (new mode) and
  `spec_cites.py` (`Index`, `run_staged`, `parse_tsv`; `check_numbering`,
  `check_toc`, `check_cites` take optional staged text/reader): the same
  functions the tree-wide scan runs, judged on `git show :path` / `git
  cat-file --batch`. Allowlist, baseline and `cite_exclude.tsv` are read from
  the index too. The tree mode is unchanged (its output and 144+ checks are
  the same; verified).
- `scripts/hooks/pre-commit`: plan lint kept as is (messages, bypass,
  opt-in install); adds the spec check when a staged file is md/txt/tsv/py/
  sh/c/h/Makefile. Check 1 (any such staged file): no line cite, no dangling
  section cite. Check 2 (a staged numbered `docs/spec/*.md`): history markers
  vs allowlist/baseline, numbering, contents (via `spec_toc.build`), and every
  citation of that doc across the index (`git grep --cached`).
- `tests/spec_history/run_hook_selftest.sh`: scratch repo under `build/`,
  real hook and checkers, 11 planted cases; called by
  `run_spec_history.sh` (so `make test-spec-history`).
- Docs: scripts/CLAUDE.md, docs/testing.md hook section, Makefile `hooks`
  comment, tests/spec_history/CLAUDE.md.

## Measured cost (Linux dev box, hook end to end, 3 runs each)
- text files staged, no spec: 49-50 ms.
- a numbered spec staged (tuning.md): 442-449 ms (wide index scan for its
  citations dominates).
- unrelated commit (no covered extension): grep only, checker not started.
- full `make test-spec-history` section: 3.7 s including the self-test.

## Validation
`bash tests/spec_history/run_hook_selftest.sh`: 11/11. Tree-wide mode run
standalone: 1 failure, PRE-EXISTING and not from this lane: the main commit
32c4db6ac put a literal line-number example in
docs/dev/lanes/BOILERPLATE.md (its last paragraph), which the tree scan
reads as a line cite of match_api. The new hook, run with a match_api edit
staged, reports it (rc=1) -- the gate works, and main's
test-spec-history is red until that example is reworded or excluded.
No make test run (box rule).

## Notes
- The hook's covered-extension list is the gate for starting the checker; the
  tree-wide scan still covers every tracked text file and remains the backstop.
- Staged mode has no floor check (a subset has no census).
