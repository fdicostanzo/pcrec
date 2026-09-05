# n1budget report — [LIM-2] N1: the work-budget fallback + the raise-and-retry surface

Lane `n1budget`, worktree `worktrees/n1budget`, branch `lane/n1budget`, forked
from `main` at `ecc069e5`. Sonnet lane per the charter. `git diff
$(git merge-base HEAD main)..HEAD --stat` is the clean 26-file diff this
report describes; a `git diff main --stat` run after this report was written
also shows unrelated deletions from main's own subsequent utf8-design work —
that divergence is main moving forward past this lane's fork point, not
anything this lane touched.

**Disclosure (scope mandate).** Context injected at spawn: the session-root
`CLAUDE.md` (repo-wide conventions — the situation-index table, the D80
"spec hunk in the same change" rule, the D77 build-under-measurement rule)
and the memory index (`pcrec-general-mechanisms-not-special-cases`,
`pcrec-check-design-lessons`, `pcrec-two-machine-split`, among others named
generically in the index — none named a fact specific to this charter). No
named fact from either shaped a design decision beyond what the charter
itself and the files it named already directed; the "generalize the raise
surface as one table" decision follows directly from the charter's own
"one general mechanism, not four copy-pastes" instruction and the memory
pointer it names, not from anything else in the injected context.

## 1. What shipped

1. **THE BUDGET.** `PCREC_MAX_AUTO_DFA_ELEMS` (30,000,000, `src/core/
   limits.def`), a smaller threshold on the SAME counter
   (`Ctx.subset_elems`, K7's own accounting) `PCREC_MAX_SUBSET_ELEMS`
   bounds, checked at the same site in `src/ir/dfa.c`'s `intern()`, BEFORE
   the hard cap. It applies only to a MANDATORY machine (`!d->optional` —
   an optional [ENG-ABS] machine's overflow already never refuses) built
   under `--engine=auto` (`cx->opt->engine == PCREC_ENGINE_AUTO` — an
   explicit `--engine=dfa` request pays the full `PCREC_MAX_SUBSET_ELEMS`
   cap, unaffected). Crossing it joins the IDENTICAL `[SEL-1]`
   `dfa_overflowed`/`dfa_overflow_why` recording shape a hard-cap overflow
   uses, so `compile_driver`'s existing one-shot retry (`forces_dfa_
   overflow`) falls back to the VM with no new code path there at all.
2. **THE RAISE SURFACE.** `--max-nfa-states=N`, `--max-dfa-states-goto=N`,
   `--max-subset-elems=N` and `--max-auto-dfa-elems=N`, all raise-only
   (D84 ruling 1's shape), dispatched through ONE new table in
   `cli/main.c` (`raise_only_limits[]`, `offsetof`-addressed) that also
   now drives the two pre-existing `--max-emit-*` flags — see §3.
3. **DIAGNOSTICS.** The auto-fallback's one-line stderr note (`pcrec:
   note: auto route's DFA attempt exceeded the work budget
   (--max-auto-dfa-elems); falling back to the VM instead of refusing.
   --engine=dfa pays the full --max-subset-elems cap instead.`), printed
   ONLY on the attempt that succeeds via the N1 fallback specifically (a
   new `Ctx.dfa_overflow_is_budget` flag distinguishes it from an ordinary
   hard-cap fallback, which prints nothing new); the hard-cap `ctx_fail`
   messages for `PCREC_MAX_NFA_STATES` and `PCREC_MAX_SUBSET_ELEMS` now
   name their own raise flag.
4. **THE RAW-PROJECTION WARNING** (stretch item 4): NOT built — everything
   else landed with room to spare, and the charter is explicit that this
   item is never gold-plated in.

## 2. The default's derivation (MEASURED, not guessed)

`studies/n1budget/n1_measure.c` drives the real, unmodified `pcrec_build_dfa`
pipeline (modelled on `studies/lim2_census/lim2_census.c`'s own precedent)
over the whole `.rxt` corpus plus pcrec-bench's `bench/altwide` set, and
reports the FINAL `Ctx.subset_elems` for every pattern that does not already
refuse — the exact population the new budget must not disturb.

**MEASURED 2026-09-04:** 3,386 pattern blocks (193 `.rxt` files, 33 altwide
patterns); 390 refused (any `ctx_fail`, the K7 hard cap included); 2,157
`route=unanch` + 433 `route=attempt`, both not refused. **MAX
`subset_elems` over non-refused rows: 24,050,003**
(`tests/counterk/counterk.rxt:1845`, `((a)|bc){0,4000}d` — one of three
near-identical 8,002-raw-state exact-repeat witnesses in that file, at
lines 1725/1807/1845). `PCREC_MAX_AUTO_DFA_ELEMS` = 30,000,000 sits **1.25x**
above that measured maximum (25% headroom), and 62.5% of the hard
`PCREC_MAX_SUBSET_ELEMS` cap (48,000,000) — enough margin that no known
population is anywhere near it, and enough room below the hard cap that the
budget genuinely bites before the full spend on a hypothetical larger
pattern, rather than being a rounding error on the same number.

The measurement tool's own methodology note (its header comment, and
`studies/n1budget/CLAUDE.md`) records the one place it goes further than
`lim2_census.c`'s precedent: it ALSO builds the [ENG-ABS] optional third
machine inline (mirrored, since `build_anchored_dfa` is `static` to
`compile.c` and not exported) for a DFA-chosen artifact, so its reported
total is the real full spend a corpus artifact pays today, not an
under-count of it — verified NOT to move the maximum (a counter,
`n_dfa_chosen_anchored_built`, confirmed 1,074 of the 2,590 non-refused
patterns built it; the witness at 24,050,003 elements is VM-chosen and
never reaches that optional build at all).

## 3. Which caps are raisable — the survey, and the one refusal

The charter named four caps (limits.def lines 136-140's neighbourhood):
`PCREC_MAX_NFA_STATES`, `PCREC_MAX_DFA_STATES_GOTO`,
`PCREC_MAX_DFA_STATES_TABLE`, `PCREC_MAX_SUBSET_ELEMS`. The survey (reading
every consumer of each, not just its own comment) found:

| cap | raisable? | why |
|---|---|---|
| `PCREC_MAX_NFA_STATES` | YES | pure memory backstop (`src/ir/nfa.c`'s `nst()`); the NFA is never emitted, so no format constrains it |
| `PCREC_MAX_DFA_STATES_GOTO` | YES | the ENG_ATTEMPT engine's states are LABELS addressed by `void *` (`src/gen/emit_dfa.c`'s `<p>_targets_K[]`) — no narrow numeric packing. The real cost of raising it is gcc's own superlinear computed-goto compile time (R1 A-3), the caller's own cost to accept, exactly the two byte-caps' "raise-only, the user's own trade" precedent |
| `PCREC_MAX_DFA_STATES_TABLE` | **NO** | the table-engine's emitted transition cell is a C `short`/`unsigned short` (`PREMUL_DEAD` = 65,535 the pre-multiplied form's reserved dead sentinel; `-1` the indexed form's — `src/gen/emit_dfa.c`). 32,000 already sits just under that ceiling with a K38-style margin. Raising the CHECK past ~32,767 would let a state number the ARTIFACT cannot represent through, silently truncating — the charter's own "structurally requires a compile-time constant" exemption, applied for real rather than assumed. Reported here, not forced; `src/core/limits.def`'s own comment on the row and `docs/spec/limits.md` §3.3 both carry the finding |
| `PCREC_MAX_SUBSET_ELEMS` | YES | pure internal counter (`Ctx.subset_elems`, a `long long`), no emission-width tie |
| `PCREC_MAX_AUTO_DFA_ELEMS` (new) | YES, by construction | the same counter as above, with no direct emission effect at all |

**The emit-cap plumbing survey** (charter's own trigger for the
generalization, "if the survey shows the emit-cap plumbing is itself two
one-offs"): confirmed exactly that. `--max-emit-code-bytes=N`/
`--max-emit-bytes=N` were two `else if (!strncmp(a, "--max-emit-code-bytes=",
22))`/`else if (!strncmp(a, "--max-emit-bytes=", 17))` blocks in `cli/
main.c`, each hand-spelling its own flag string, floor constant and
destination field, sharing only the `parse_raise_only` helper's body. The
general form: `raise_only_limits[]`, one row per flag (`{flag, floor,
offsetof(pcrec_options, field)}`), and `raise_only_match(a)` (called once
per argv token into a local computed before the whole `else if` chain
begins) tells ONE new branch whether `a` matches any row. The two original
flags became rows 0 and 1 of the same table rather than staying special —
a sixth raise-only cap now costs one table row, not one more block.

## 4. The before/after engine-selection census (the charter's own backstop)

Built a reference compiler from `main` at the fork point (`ecc069e5`, in a
throwaway `git worktree`) and compared it against this branch's compiler
over the SAME population `run_size_term.sh` already uses (every distinct
`pattern` line under `tests/`, `LC_ALL=C` sorted) plus pcrec-bench's 33
altwide patterns — 2,878 patterns total, each compiled by both binaries
under identical default options, comparing (a) whether the compile
accepts or refuses and (b) the `RX_ENGINE` stamp on an accepted artifact.

**MEASURED result: 0 differences, either direction, on either population.**

    corpus (2,845 patterns):    both refuse 288, before-only-ok 0, after-only-ok 0, engine differs 0
    bench altwide (33 patterns): both refuse 14,  before-only-ok 0, after-only-ok 0, engine differs 0

Today's engine selections do not move — the census, not merely the
arithmetic in §2, is what proves it.

## 5. Diagnostics: an observed textual family, not a defect

`RX_ENGINE_WHY`'s two overflow spellings share a PREFIX by design (`"dfa
overflowed: subset construction exceeds"`), because both are members of
the same D26 diagnostic family and `tests/resource/run_resource_tests.sh`
pins that prefix rather than the full string. The N1 budget's own suffix
differs (`"... %lld elements (N1 auto budget)"` vs the hard cap's `"... %lld
state-set elements (K7)"`), and the NUMBER differs too (30,000,000 vs
48,000,000 at the shipped defaults), so a reader who reads the whole string
can always tell which cap fired — verified live: `a{65535}` under plain
`auto` now reports `RX_ENGINE_WHY "dfa overflowed: subset construction
exceeds 30000000 elements (N1 auto budget) at pattern offset 0"` where it
used to report the 48,000,000/K7 spelling, and `tests/resource/
run_resource_tests.sh`'s own pinned check (a prefix match) still passes
(26/26, full section run) because that pattern's own AUTO-mode outcome
(rc 0, `RX_ENGINE "vm"`, the shared prefix) is unchanged in every respect
the test actually asserts. The two `--engine=dfa`-forced `name_check`
cells in that same file, which DO care about the exact 48,000,000-cap
wording, are untouched by this change (the budget never applies there) and
still pass verbatim.

`tests/reject/` itself carries no message pinning this change's wording
touches (grepped for "NFA exceeds", "subset construction exceeds", "too
complex for the DFA", "pattern too large" — no hits there; the only hits
are in `tests/resource/`, covered above).

## 6. Tests, spec, validation

- **`tests/codegen/run_n1_budget.sh`** (13 checks, wired into `test-codegen`'s
  `run_group`): the shipped default moves nothing on an ordinary witness
  (natural population zero, per `run_size_term.sh`'s own §5 precedent); a
  `-DPCREC_MAX_AUTO_DFA_ELEMS=2000`-lowered reference compiler trips the
  fallback under `--engine=auto` (`RX_ENGINE "vm"`, the stderr note); the
  fallback artifact ANSWERS CORRECTLY (`--emit-main`, run against two
  subjects, not merely "compiles"); the SAME lowered reference is
  UNAFFECTED under `--engine=dfa`; the raise flag round-trips (raising past
  the witness's own spend cancels the fallback); raise-only floor rejection
  against both the reference build's own lowered default and the shipped
  one. Validated in the failing direction (a temporary `if (0 && ...)`
  sabotage in `src/ir/dfa.c`, reverted before delivery) — reproduces
  exactly the two expected symptoms (`RX_ENGINE` stays `"dfa"`, no note)
  with the other 11 checks unaffected.
- **`tests/registry/limits_check.sh`**: manifest count 55 -> 56,
  `PCREC_MAX_AUTO_DFA_ELEMS` named; the doc-drift check (part 2) required
  the spec hunk below before it passed.
- **Spec**: `docs/spec/limits.md` §3.3 gains two paragraphs — the general
  raise-surface table (with `PCREC_MAX_DFA_STATES_TABLE`'s non-raisability
  stated as a finding) and the N1 budget's own contract (why a smaller
  budget below the hard cap, the derivation, the census).
- **CLAUDE.md** updated in every touched directory: `src/core/`, `src/ir/`,
  `cli/`, `lib/`, `studies/` (+ new `studies/n1budget/CLAUDE.md`),
  `tests/codegen/`.
- **`make strict`**: clean (`-Werror -Wshadow`).
- **Targeted sections run** (light local testing per the charter — never
  the full `make test`): `test-registry` (limits_check.sh's own 22 checks
  green; the wider section's PC-3/verb-differential failures confirmed
  PRE-EXISTING on a clean `main` build in a throwaway worktree — a broken
  `/usr/lib/libpcre2-8.dylib` symlink on this macOS box, unrelated to this
  change), `test-cli` (287/287), `test-codegen` (6 of 8 scripts clean
  including the new one at 13/13; the two pre-existing failures —
  `run_codegen_tests.sh`'s OS-0b/K24/SABANCHOR cells and
  `run_inline_capability.sh`'s `nm` probe — touch no file this lane changed
  and are each documented in their own header as compiler-version-sensitive
  or environment-dependent by design, not correctness checks this change
  could have broken).
- **The corpus-wide before/after census** (§4): a stronger, direct
  instrument than any of the above for the one claim that matters most —
  "today's engine selections move NOT AT ALL" — run explicitly rather than
  inferred from the identity-gate suites above.

## 7. Escalations / open items

- None blocking. The raw-projection warning (stretch item 4) is the one
  named, deliberate omission, per the charter's own "never gold-plated in"
  instruction.
- `PCREC_MAX_TABLE_ENTRIES` (the fifth cap in the limits.def neighbourhood
  the charter's line range spans, 136-140) was NOT given a raise flag: the
  charter names only the other four explicitly, and it interacts with
  `PCREC_MAX_DFA_STATES_TABLE`'s own raise question (a raised
  `PCREC_MAX_DFA_STATES_TABLE` — had it been raisable — would be silently
  re-clamped by `PCREC_MAX_TABLE_ENTRIES / d->ncls` in `src/ir/dfa.c`'s
  `pcrec_build_dfa`, `states*classes <= 2,000,000`) which is moot given
  `PCREC_MAX_DFA_STATES_TABLE` itself is non-raisable, but is worth a
  future reader knowing about if `PCREC_MAX_TABLE_ENTRIES` is ever raised
  on its own.
- The two-lever shape (`BUILD_D` + a runtime raise flag) `PCREC_MAX_AUTO_
  DFA_ELEMS` uses, needed specifically so `run_n1_budget.sh` could drive a
  positive control (the natural population is zero at the shipped
  default), means `src/core/limits.h`'s "five BUILD_D rows" `#ifndef`
  block is now six; the file's own header comment there is updated.

## 8. Files touched

`cli/main.c`, `lib/pcrec.h`, `src/core/{compile.c,internal.h,limits.def,
limits.h}`, `src/ir/{dfa.c,nfa.c}`, `docs/spec/limits.md`,
`tests/registry/limits_check.sh`, `tests/codegen/run_n1_budget.sh` (new),
`studies/n1budget/` (new: `n1_measure.c`, `Makefile`, `README.md`,
`run_sweep.sh`, `CLAUDE.md`, `n1_data.tsv`, `n1_summary.txt`),
`Makefile` (wires the new test into `test-codegen`), `.gitignore`
(the study's own compiled binary/dSYM), and CLAUDE.md in every directory
above plus `studies/CLAUDE.md`.
