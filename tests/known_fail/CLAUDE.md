# tests/known_fail — deferred-bug regressions (expected to fail)

`.rxt` files here assert the **correct** behaviour for bugs that are CONFIRMED
but deliberately deferred rather than fixed now; each one has an entry in
`docs/dev/known_issues.md` with a minimal repro and the milestone that owns it.
`tests/harness/run.sh` excludes this directory from its default discovery, so
`make test` stays green and honest — a known bug does not get to look fixed,
and it does not get to break the build either.

## Files

- **`k64_precheck_forced_vm.rxt` — GONE, 2026-09-25, RETIRED AT MERGE (lane `chkgaps` landed it as standing check-gap coverage while K64 was still open; lane `k64fix`** ...
- **`k34_leftrec_giveup.rxt` — GONE, 2026-09-23, by the front door ([OPTLOOP.1.impl] batch 2, lane `optimpl2`; the known-fail triage, lane `b2fix`).** Lived here ...
- **`k49_utf8_lookbehind_retry.rxt` — GONE, 2026-09-05, by the front door.** It lived here for one day.
- **`k50_utf8_dfa_midchar_start.rxt`** — [K50] (`docs/dev/known_issues.md`), landed 2026-09-05 by lane `k49fix`, which found it while fixing K49 by asking whether the ...
- **(EMPTY of `.rxt` from 2026-08-24 [DD-14.LB] until the same day's K34 park, above)** — the legitimate good state this directory's own header describes: no confirmed bug ...
- **(previously empty)** — from 2026-08-15 until K23, no confirmed bug was deferred with a repro on file, which the ratchet treats as a legitimate good state (it reports ...
- **run_known_fail.sh** — the "fixed by accident" ratchet (R2-PR8).
- `dd14_bc_open.rxt` — section "`dd14_bc_open.rxt` — CLOSED 2026-08-24 by [DD-14.LB]" (history file)
- `k53_uprops_oversize.rxt` — section "`k53_uprops_oversize.rxt` — GONE, 2026-09-10, by the front door ([M5.0] stage 3, 2026-09-06 .. [K53-SELRETRY], 2026-09-10)" (history file)

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

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__known_fail.md`.
