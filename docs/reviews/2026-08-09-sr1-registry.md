# R4 — adversarial review of SR-1, the syntax construct registry

Date: 2026-08-09. Target: D24's design and the SR-1 artifact — `src/parse/registry.c`
(67 rows), the `RegRow` vocabulary in `src/core/internal.h`, and
`tests/registry/registry_check.c`. Panel per D6.

Prompted by Frank noticing SR-1 had shipped without one: R1–R3 covered earlier
checkpoints, and a design conceived and built the same day had faced no critic
at all. The gap was real, and the pass paid for itself immediately.

## Panel

Three critics, deliberately different lenses so a shared blind spot could not
hide a finding, each required to write findings incrementally to the scratchpad
(the R3 lesson: critics that batch their reporting deliver nothing).

| lens | brief |
|---|---|
| design | attack D24's claims: four doorways, base-tier fast path, four axes, flavour rebinding, static-table/dynamic-selection, and the sequencing of shipping a table nothing reads |
| pcre2 | verify all 67 rows against **libpcre2 10.46 itself**, never python `re`; sweep every `syntax` example through `pcre2_compile_8`; compare the `engines` column against `pcre2_dfa_match_8`'s real restrictions |
| tests | prove the conformance check is weaker than it looks: circularity, sweep coverage, vacuous assertions, and sabotage the existing battery would miss |

Every finding below was re-verified in the main session before being accepted.
Two were partly overstated and are recorded as such.

## Findings and disposition

### Accepted and fixed

**F1 — nine rows asserted a PCRE2 semantic that is false.** (pcre2, HIGH)
`\1`..`\9` were documented as "octal escape if no such group". PCRE2 10.46
raises error 115 "reference to non-existent subpattern" unconditionally; the
octal fallback is Perl/PCRE1 and does not survive into PCRE2. Independently
re-measured. This is precisely the class of error the registry exists to
prevent, in the registry, on day one — and it entered because the notes were
written from memory rather than checked, the exact failure the wake brief names
("measure before describing"). Notes corrected with the measurements inline;
`ESC_OCTAL` renamed `ESC_DIGIT`, since the macro names a DIAGNOSTIC SHAPE and
`\1`..`\9` are not octal. pcrec's own diagnostic still says
"(backreference/octal)" — recorded as **K2** rather than changed, because SR-2's
bar is byte-identical output.

**F2 — deleting the two collating rows was 100% invisible.** (tests, CRITICAL)
116/116 stayed green. Not caught by the per-kind empty check (the POSIX `:` row
survived), nor the coverage floor (65 ≥ 60), nor table→parser (it iterates rows
that exist, so absence is unobservable), nor the two hand-written `[.a.]` /
`[=a=]` probes — those exercise the PARSER, not table membership. The registry
could silently lose its record of the exact incident it was built to prevent.
Fixed with a hand-written **required-rows manifest**, and hand-written is the
point: a control must not share a source with the thing it controls. Validated —
the deletion now fails with two named errors. The critic's framing of the floor
is worth preserving: *a floor answers "did someone delete a lot", never "did
someone delete the right ones", and no floor loose enough to tolerate ordinary
row churn can catch a two-row deletion.*

**F3 — the sweep covered 2 of the 4 doorways.** (tests, HIGH) `RK_VERB` and
`RK_CLASSBRACKET` were never swept, while `tests/registry/CLAUDE.md` claimed the
sweep catches "a construct added to parse.c with no row" — true for half the
doorways it was written to describe. All four are now swept. Fixing it exposed a
second gap: rows whose diagnostic is fixed text carry no "requires module"
marker, so the class-bracket sweep initially validated 1 of its 3 rows; the
sweep now checks `RD_FIXED` rows against their exact message (3 of 3).

**F4 — the TS-1 citation was false.** (design, CRITICAL) D24 justified rejecting
a mutable registry by invoking "the thread-safety property TS-1 guards". TS-1
scans EMITTED OUTPUT only and would not see a mutable global in `src/`. The
honest guard is D19's compiler-side property, which D19 records as audited by
hand and mechanized by nothing. The conclusion stands; the cited guarantee did
not exist, and the miscitation had already been copied into `registry.c` and
`internal.h`. Corrected in all three places. Same shape as D19's own correction
to R3 — a wrong description of correct code, which the next reader reasons from.

**F5 — "selection resolved from `pcrec_options`" was present-tense fiction.**
(design, CRITICAL) `pcrec_options` has no flavour or enablement field, and
nothing outside the conformance test reads the feature/flavour/engine columns.
Re-stated as intent. The four-axis separation is real in the DATA and nominal in
the CODE until SR-7.

**F6 — `plan.md` contradicted the artifact in two places.** (design, MEDIUM)
SR-1's "Everything the parser currently knows about non-base syntax moves here"
is false as built; SR-6's "the registry row already names the handler" names a
field that does not exist. Both corrected. The sharper half of the second
finding is now recorded as forward work: **no status value means "implemented by
module X"** — `RS_MODULE` unconditionally implies rejection — so SR-6 carries an
unwritten schema change, not just a file move.

**F7 — SR-4 would silently drop coverage.** (design, LOW→raised) `\x{...}` and
the possessive `+` have no rows, so migrating `tests/reject/` to iterate the dump
drops their coverage unless special-cased. Recorded as a warning on SR-4 while
it is still cheap. `\N{U+hhhh}` (pcre2, MEDIUM) was added as a third known
second home — a distinct construct sharing the `N` selector byte.

**F8 — the `engines` column disagrees with PCRE2's own DFA.** (pcre2, INFO)
Measured: `pcre2_dfa_match_8` SUPPORTS lookaround, atomic groups and recursion —
all marked `VM_ONLY` — and enforces their real semantics (`(?>a+)a` does not
match "aaa" while `a+a` does). It rejects `\K`, backreferences and conditionals
(errors -42, -40), agreeing with those rows. The rows are still right for pcrec,
for a reason the file did not state: PCRE2's "DFA" is a breadth-first simulation
of compiled bytecode that can consult live capture state and re-enter itself,
whereas pcrec's is a determinized transition table with no such side channel.
Now stated explicitly, because a reader would otherwise take the column to mean
"what a DFA can do in general", which PCRE2's own matcher disproves.

### Accepted, not fixed — recorded as forward work

**F9 — `pcrec_registry_find` cannot rebind by flavour.** (design, HIGH) It takes
no flavour argument and returns the first row matching a byte, so SR-1's own
"short chain for the rare flavour-varying byte" is not expressible in the
shipped shape. Recorded on SR-7 as a signature change it must make. The critic
called this "a latent miscompile"; that half is **overstated** — a duplicate
selector is caught loudly by the well-formedness check, so it is design debt,
not a live bug.

**F10 — residual circularity.** (tests, HIGH, partly mitigated) Probes derive
from the table's own `syntax`, so the check cannot distinguish "both right" from
"both wrong". The critic tested the mitigation rather than just the hole:
`tests/reject/`'s 93 expectations are hand-written and DID catch a coordinated
wrong edit to both files. Two things narrow it further. The `M_<module>` macro
pairing, added the same day for readability, makes an invented module name a
COMPILE error — verified: `M_wrongmodule` undeclared. And the pairing closes the
critic's separate finding that the feature bitmask's VALUE was never checked,
only its zeroness. **Residual, genuinely open:** a NEW construct given the same
wrong module in both files, with no `tests/reject/` row added, is caught by
nothing. The two tables can drift in row count without either noticing.

### Not accepted as stated

**F11 — "a sixth copy of the knowledge".** (design, MEDIUM) Fair as strategy,
and the strongest argument for doing SR-2 promptly; it understates one
difference. The five copies that produced `\v` were mutually unchecked. This one
is pinned to the parser in both directions by a test that fails when they
diverge, so if SR-2 stalls the cost is extra maintained surface, not another
`\v`. Kept on the record because the maintenance argument survives the rebuttal.

**F12 — "exactly four doorways" survives only by defining exceptions out.**
(design, HIGH) A real tension, not a refutation: the claim is about where
constructs ENTER, and a possessive `+` genuinely is a quantifier suffix. But the
plan sentence that overstated it has been removed, and the exclusions are now
stated as part of the claim rather than as a footnote to it.

## Reflection

**The panel found more in the DATA than in the code, again.** F1 is the fifth
consecutive checkpoint where reading a specification against pcrec beat
executing pcrec against itself: five checkpoints and ~54M oracle-checked
comparisons have found zero compiler defects, while an afternoon of reading
PCRE2's syntax reference has now produced three. The registry was built in
response to that pattern and immediately exhibited it.

**Two of the three highest findings were in the TEST, not the artifact.** F2 and
F3 both had the same shape: a check that iterates what exists cannot see what is
missing, and documentation that describes what the check was MEANT to do rather
than what it does. The conformance test was written before the table precisely
to avoid rationalization, and it still needed a critic to find that half its
headline claim was untrue.

**Verifying the mitigation is worth more than finding the hole.** The tests
critic's most useful act was running `tests/reject/` against its own sabotage to
see whether the suite as a whole caught what one file could not. That turned
"the check is circular" from an alarm into a precise statement of residual risk.
Brief future critics to attack the defense, not just the target.

**A correction that was propagated before it was caught.** F4 existed in D24 for
hours and had already been copied into two source files. The cost of a wrong
citation scales with how attractive it is to quote — worth remembering when
writing the *reason* for a decision, not just the decision.

## Post-review state

805 corpus / 49 CLI / 112 reject / **126 registry** (was 116) / 29 codegen /
7 trie-identity, all green. Two new sabotage validations recorded in
`tests/registry/CLAUDE.md`.
