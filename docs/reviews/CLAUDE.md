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
- **2026-08-09-sr1-registry.md** — R4, SR-1 (the syntax construct registry).
  Nine rows asserting a PCRE2 semantic that does not exist, a row deletion that
  was invisible to a 116-check suite, a sweep covering two of the four doorways
  it claimed, and a citation of a guard (TS-1) that does not guard what was
  claimed — already copied into two source files before it was caught.
- **2026-08-10-r5-sr2-sr4.md** — R5, the SR-2/SR-3/SR-4 arc. SR-2's
  byte-identity claim HELD under a stronger instrument than the one that made
  it; everything else found was pre-existing, and there was a lot of it. Four
  confirmed bugs (K3–K6), **two of them miscompiles of the exact class the
  charter forbids**, plus a false "this fails the build" claim in three of my
  own comments and a silent hole in my own harness where byte 0x0A became the
  empty string. Two critics converged independently on the class-bracket bugs.
  The most productive question was "which of the branches I just added can no
  test see?" — asked because a sabotage returned zero, and every other bug came
  from pointing it somewhere else.

- **2026-08-10-r7-fix1.md** — R7, FIX-1 (K5/K6, the two brace miscompiles).
  The panel found a THIRD miscompile of the same class in the same function
  (K8, whitespace in `{m,n}`), one space away from all 49 forms the fix had
  been certified against — invisible because those probes compared VERDICTS and
  the bug lives where both engines accept. Also: nothing in the repo asserted an
  error offset, though the code kept per-number state for no other purpose; the
  over-reach guard was tested on one half of a two-sided rule; `{k,k}` did not
  exist anywhere in the suite; the exact-count hazard was measured disarming the
  one row the commit called irreplaceable, in a two-line diff, which is what the
  new MANIFEST answers. Four of my claims were false, one of them a number I had
  inferred from an error message and copied into four files.

- **2026-08-10-r8-pc3-q1.md** — R8, PC-3 and Q1 (the first EXTERNAL check).
  Three of the new instrument's four headline claims failed the same way — a
  control sharing a source with the thing it controls: the "external" candidate
  pool could contribute zero names with nothing failing, the fabrication check
  was defeated by hiding a row's syntax in a PCRE2 comment, and the row check
  never ran pcrec at all. Two real bugs on axes the sweep held fixed (a missing
  magnitude rule, a name-length boundary the candidate cap sat below), a fix
  whose guard scored ZERO until two probe forms were added, and the headline:
  the over-promise Q1 removed at the doorway with ONE row is still open at the
  doorways with 24 and 3, which are 217x and 900x wider.

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
