# tests/known_fail — deferred-bug regressions (expected to fail)

`.rxt` files here assert the **correct** behaviour for bugs that are CONFIRMED
but deliberately deferred rather than fixed now; each one has an entry in
`docs/dev/known_issues.md` with a minimal repro and the milestone that owns it.
`tests/harness/run.sh` excludes this directory from its default discovery, so
`make test` stays green and honest — a known bug does not get to look fixed,
and it does not get to break the build either.

## Files

- **d27_nested_min_boundary.rxt** — K23 (2026-08-16): `(a{10,20}){10,50}`
  on the exact-minimum 100-byte subject returns `RX_ERR_STEPS` where the
  oracle answers span (0,100)/group (90,100) instantly. Asserts the correct
  behaviour per this directory's contract; owning milestone [M4.6]. Found by
  the D27 blinded quantifier corpus (its live siblings: `tests/base/d27_*.rxt`).
- **(previously empty)** — from 2026-08-15 until K23, no confirmed bug was deferred with a
  repro on file, which the ratchet treats as a legitimate good state (it
  reports "nothing to ratchet" and exits 0). The last resident was
  `k18_empty_exit_through_seen_eps.rxt`, which moved to `tests/base/` when K18
  was fixed; it is worth reading as the worked example of this directory's
  contract, because the ratchet is what forced the move and the
  `known_issues.md` close to land in the SAME commit. Three sibling files
  joined it there (arm-order, `{0,2}` split shapes, deep nesting) — a deferred
  bug's repro is written from the bug as FOUND, and the fix lane owes the axes
  that repro's own alphabet could not reach
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
