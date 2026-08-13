# tests/modifiers — module `modifiers` corpus (MOD-0.5c)

Oracle-verified behaviour of the constructs module `modifiers` PRODUCES —
`(?i)`/`(?-i)`/`(?i:...)` scoping and restore, `(?s)` dotall, `(?U)` greed
swap, `(?n)` no-auto-capture, single-`x` and `xx` extended-mode lexing, the
`(?^)` per-letter reset rule — plus the recognition-surface cells that are
NOT producer semantics: malformed option-setting runs, non-construct option
letters, and per-letter refusals (`m` -> module 'assertions', `J` -> module
'named-groups'), written from the [MOD-0.5a] design gate
(`grep -n "MOD-0.5" docs/dev/plan.md`; docs/dev/plan.md's rulings 1-6).

## R20/SPEC-1 — the quantifier controls in scope.rxt

`scope.rxt` gained two blocks at R20: `a(?i:b)*` and `(?i)a*` must keep
compiling and matching. They are ACCEPT-CONTROLS for a tier-1 miscompile fixed
the same session — a bare option run is not a repeatable item, so `a(?i)*` now
refuses (err 109's wording, pinned with its offset in tests/reject/), and these
two are what stop that fix reaching into the SCOPING form, which libpcre2 and
python both accept. The refusal half cannot live here: a `perr` block asserts
only THAT a pattern rejects, never WHICH diagnostic came back, and the whole
point is which one.

## Files

Every block carries the `features modifiers` directive except the
gate-off pins in `malformed_and_gate.rxt` (default enabled set stays
empty, and that refusal stays pinned; the module-NAME half of that check —
WHY a pattern is refused, not just THAT — is tests/reject/'s job, not
this directory's, since a `.rxt` `perr` block cannot assert WHY).

- **scope.rxt** — where `(?i)`/`(?-i)`/`(?i:...)` starts and stops
  applying: from-position, unset mid-pattern, group-close restore, and the
  measured PARSE-1 sibling-alternation-branch leak.
- **reset.rxt** — the `(?^)` rule: resets i/m/n/s/x/xx to hardwired
  defaults, does NOT touch U or J. The J cell is a `perr` (not a match
  pin): the survives-`(?^)` semantics are measured in
  tests/probes/probe_mod05b.c, but pinning them as a corpus match case
  needs `named-groups` too, which this milestone does not land — no block
  in this directory may depend on a module MOD-0.5 doesn't ship. The perr
  pins what IS true under `features modifiers` alone (stably refuses, in
  both today's and MOD-0.5c's epoch, for two different real reasons).
- **letters.rxt** — `(?s)` dotall, `(?U)` greed swap (both directions),
  `(?n)` no-auto-capture plus the backreference-to-uncaptured-group error.
- **xmode.rxt** — single `x`: whitespace skip outside classes, `#`-comment,
  escaped-whitespace-stays-literal, class interiors untouched. Notes the
  one cell the line-oriented `.rxt` format cannot express (comment-to-
  embedded-newline; see tests/probes/probe_mod05.c instead).
- **xxmode.rxt** — the D30 §7 `xx` hazard: `(?xx)[a- ]` / `(?xx)[a-\ ]` /
  `(?xx)[\ -a]`, plus tab deletion in class interiors, both against the
  single-`x` contrast.
- **malformed_and_gate.rxt** — `(?i-m-s)` (recognised malformed run) vs
  `(?iZ)` (not a construct at all); `m`/`J`'s per-letter refusal under
  `features modifiers` alone; six gate-off pins. Before the MOD-0.5c/d
  landing this was the one file already fully green (11/11), by design —
  every other file was a watched-failing probe until the producers landed
  (they have; the whole directory is green now — see the §9.3 record below).

## Oracle split

python-verifiable where the construct is expressible at pattern position 0
(plain `(?i)`, `(?i:...)`, `(?s)`) or, for the perr-only blocks in
`malformed_and_gate.rxt`, where python fails to compile the identical text
for its OWN independent reason (global inline flags not at position 0,
unsupported letters U/n/^/J, `Z` as an unknown flag) — genuine two-oracle
agreement on THAT a pattern rejects, not a claim that WHY matches. Every
other block is `# pcre2-only`; `xxmode.rxt` is entirely pcre2-only because
python's `(?xx)` does not delete class-interior bytes the way libpcre2/
pcrec's does — the two engines DISAGREE on the discriminating cell.
Expectations there were measured against live libpcre2 10.46 with a
throwaway scratchpad oracle patterned on tests/probes/probe_mod05.c and
probe_mod05b.c (not committed — those probes remain the canonical,
reproducible measurement).

## The D33 §9.3 record (HISTORICAL — the producers have since landed)

Each file's header carries the pass/fail split that was MEASURED 2026-08-12
against the [MOD-0.5a]-gate binary, BEFORE MOD-0.5c/d landed the producers
(at that point the vocabulary existed and `modifiers` had no producer):
56 cases, 16 PASS (11 in `malformed_and_gate.rxt`'s already-correct gate
pins, reset.rxt's J-cell `perr`, plus 4 control/coincidental-agreement
cells), 40 FAIL with "requires module 'modifiers'" — via
`PCREC=<binary> bash tests/harness/run.sh tests/modifiers`. That record is
kept as the watched-failing evidence and as a regression-check recipe:
re-run it against any binary suspected of losing the module wiring (the
tests/classes/ precedent). CURRENT status since the MOD-0.5c/d landing
(commit 9f18c06): 59/59 green — the count grew from 56 when the tab block
was split at the landing (see xxmode.rxt's correction note). (Separately,
`python3 tests/harness/verify_rxt.py tests/modifiers` reports PASS=26/26 —
the ORACLE cross-check on the non-`# pcre2-only` cases, a different axis
from the pcrec-binary count; do not conflate the two.)

Maintenance: add blocks when the module's producing scope grows (M5's
UTF/UCP re-measurement of the `r`/`aD aP aS aT aW` no-ops, per [MOD-0.5a]
ruling 1, brings its own cases; so does `assertions`/`named-groups` landing
enough to turn the two forward pins above green).
