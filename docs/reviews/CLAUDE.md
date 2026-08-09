# docs/reviews — compiled checkpoint critic reviews

One file per checkpoint (D6): the adversarial critic panel's findings, the
triage decision on each, and a reflection. These are the densest source of
"why is it like this" in the project — most of the non-obvious code in src/ and
most of the odd-looking test cases trace to a finding recorded here.

## Files

- **2026-08-09-m1.md** — R1, end of M0/M1.
- **2026-08-09-m2.md** — R2, mid-M2.
- **2026-08-09-m2-close.md** — R3, M2 close. The largest: a live stack
  regression, a 56x compile-time cliff, two holes in guards written the same
  day, and five refuted claims.

## Conventions

Findings are labelled CONFIRMED (reproduced, with the repro) or SUSPECTED, and
triaged FIX-NOW | PLAN | DOC | REJECTED | NOTED. Every review also carries a
PROBED-AND-HELD list with case counts, because a negative result with evidence
behind it is worth as much as a finding and stops the same ground being
re-covered next time.

Two rules earned the hard way and enforced here:

- **Do not declare a milestone reviewed until the reports are in hand.** R3 was
  compiled as self-audit-only because the panel had not reported; the panel
  then found a live segfault, a hole in a freshly-built guard, and a regression
  five independent nets had missed.
- **Review the artifact a stranger would get, not the working tree.** R1 and R2
  both missed that `.gitignore`'s unanchored `core` had excluded `src/core/`
  from every commit since M0, so a fresh clone did not build. Cloning and
  building is now step 5 of the process critic's brief.

The NOTED list of the most recent review is the honest inventory of what is
still unguarded; read it before starting new work.

Maintenance: add a file per checkpoint and list it here.
