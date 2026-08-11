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
  doorways with 24 and 3, which are 217x and 900x wider. The panel's closing
  report then found a LIVE wrong-module bug — `(?*...)` is the non-atomic
  positive lookahead and was answered "requires module 'modifiers'" — with the
  registry the only one of its three homes that had it wrong.

- **2026-08-10-r9-fix2.md** — R9, FIX-2 (K3/K4 and the class-bracket doorway).
  **The panel that ran a session late**, because FIX-2 was committed before its
  critics could be convened. The split is the point: both critics who attacked
  the RULE confirmed it — one over 1,239,480 generated patterns, one over ~2.4
  billion POSIX-name probes against libpcre2, with the 16-name table
  independently regenerated and found exactly right — while both critics who
  attacked the CHECKS found defects. Undefined behaviour in the new
  differential's one nested-opener shape (a `const char *` read as `%c`), so the
  construct it existed to sweep appeared ZERO times for two of three delimiters
  while the header printed 1680; a `size_t` underflow held safe only by an
  unrelated function's length-check-before-memcmp; a MANIFEST entry hollowed by
  a duplicated row, plus two more duplicates the critic's own inventory missed;
  and three of four counts in a CLAUDE.md contradicting the commit that wrote
  them. The liveness guard added for the first finding **was wrong in the same
  way the finding was** and passed its sabotage until the positive control was
  run.

- **2026-08-11-r10-mod0-design.md** — R10, MOD-0's DESIGN (D29 and the MOD-0
  substeps). **The first panel run against a design rather than an
  implementation, and the cheapest review in the project's history**: comparable
  severity to R9, found before a line was written, every fix an edit to a
  paragraph. D29's spine survived — recogniser-per-row, two ports with two
  signatures, the semantic port recursing into `p_alt`, no allocation in
  recognition. Its central guard did not: "exactly one recogniser may answer"
  FIRES ON A CORRECT REGISTRY, because every tailed bucket has a tail-less
  fallback row whose honest recogniser is "always matches" and two buckets hold
  opposite verdicts; and it is a UNIQUENESS guard traded for the REACHABILITY
  guard it retired, proved on D29's own `-\d+)` collapse, which would have been a
  tier-2 regression. Both proposed controls were the defect they were meant to
  cure — `--explain` never enters a doorway, and module-shipped probes are
  co-location (the drift cure) applied to a circularity problem. The most
  serious finding is D27's own mechanism turned on the designer:
  `src/parse/registry.c:62-72`, dated the day before, says *"Do not design a
  handler signature that assumes it can"* about the exact signature D29
  specifies, and D29 neither cites nor answers it. And "17 tailed rows,
  measured" was 18 — measured by one grep for a macro NAME, missing the one
  tailed row not written through a macro, which was the centrepiece of the
  argument the number supported. The generalisation, sharper than D27 reached:
  D29's three defences were all LIVENESS arguments where every failure this
  project records is a VALUE or SET argument — ask not "does this check run" but
  **"what would have to be true for it to fail, and who chose that input".**
- **2026-08-11-r11-parse1-mod01.md** — R11, two panels in one session:
  PARSE-1's design+implementation and MOD-0.1's design. The PARSE-1 half is
  absorbed into D31; its sharpest finding arrived **after the commit** —
  `p_alt` had no linkage, so the step titled "make `p_alt` a usable module
  callback" had left the callback uncallable, and the rule "re-poll before
  compiling" was applied twice successfully and lost anyway because its
  boundary was the build, not the panel. **A checkpoint is not closed until
  every critic has IDLED.** The MOD-0.1 half REFUTES PARTS OF D30 the way R10
  refuted D29 and is deliberately left unresolved: D30 §2's non-optional check
  ("promise a module wherever libpcre2 DISPATCHES") is false — 93 counterexamples
  in 1,672 probes, ALL of them pcrec being correct, because "dispatched" does not
  imply a module is owed; D30 §3 gets that right and D30 §2 ignores it two
  sections apart. Rank is almost entirely unchecked (20 of 22 rows accept any
  value to 250; the one prefix pair is a single THRESHOLD, not an ordering) and
  two of D30's three required checks fire on identical boundaries in all 5,632
  probes. And the returning-doorway defect is FOUR call sites across three
  doorways, one of which is undefined behaviour: making `pcrec_ext_escape`
  return makes `build/pcrec` itself SIGSEGV on `[a\qb]`, while `a\qb` silently
  launders the pointer out of `%rax`. Of the group-discard class, 7 of 18
  generated patterns are byte-identical to a smaller pattern and 0 of 18 behave
  as the contract promises. Second process finding: a five-part critic brief
  delivered materially worse than a brief with one clear primary item — two of
  four produced only headers.

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
