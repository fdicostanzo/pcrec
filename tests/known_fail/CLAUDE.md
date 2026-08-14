# tests/known_fail — deferred-bug regressions (expected to fail)

`.rxt` files here assert the **correct** behaviour for bugs that are CONFIRMED
but deliberately deferred rather than fixed now; each one has an entry in
`docs/dev/known_issues.md` with a minimal repro and the milestone that owns it.
`tests/harness/run.sh` excludes this directory from its default discovery, so
`make test` stays green and honest — a known bug does not get to look fixed,
and it does not get to break the build either.

## Files

- **k18_empty_exit_through_seen_eps.rxt** — K18, a live tier-1 DFA miscompile
  (`(?:(?:a|b*?)?)*` on "ab" → [0,2), both oracles [0,1)). Sibling of K1/K17:
  the empty-iteration redirect cannot be reached through an already-seen
  NON-LOOP ε state, so the walk dies one hop short of the loop entry whose
  exit is the ACCEPT. Deferred because the principled fix — keying the closure
  memo on (state, open-loop-set) instead of on state alone — is a rewrite of
  `clo_visit` in a different risk class from K17's one-line change, and needs
  a scheduling decision. The file carries seven CONTROL blocks that pass today
  alongside the eight failing shapes, so whoever fixes it is measured for
  over-reach in the same file; the ratchet only cares that the file as a whole
  still fails
- **run_known_fail.sh** — the "fixed by accident" ratchet (R2-PR8). Runs each
  `.rxt` here and INVERTS the verdict: still-failing is expected, and a file
  that has started PASSING is flagged and fails the script. Part of
  `make test`. An empty directory exits 0.

## Conventions

Adding a deferred bug: write the `.rxt` asserting the behaviour PCRE actually
has (oracle-verified, same as any other corpus file), put it here, and add the
`docs/dev/known_issues.md` entry naming the owning milestone. Never weaken an
expectation to make a bug look fixed.

Removing one: when the ratchet flags a file, MOVE it into the matching
`tests/<module>/` directory so the fix gains a live regression, close the
`known_issues.md` entry, and journal it — a fix nobody intended is worth
understanding, because its scope may be accidental too.

Maintenance: update this file when the directory's contents or contract change.
