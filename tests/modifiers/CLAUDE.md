# tests/modifiers — module `modifiers` corpus (MOD-0.5c)

Oracle-verified behaviour of the constructs module `modifiers` PRODUCES —
`(?i)`/`(?-i)`/`(?i:...)` scoping and restore, `(?s)` dotall, `(?U)` greed
swap, `(?n)` no-auto-capture, single-`x` and `xx` extended-mode lexing, the
`(?^)` per-letter reset rule — plus the recognition-surface cells that are
NOT producer semantics: malformed option-setting runs, non-construct option
letters, and per-letter refusals (`m` -> module 'assertions', `J` -> module
'named-groups'), written from the [MOD-0.5a] design gate
(`grep -n "MOD-0.5" docs/plan.md`; docs/plan.md's rulings 1-6).

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
  `features modifiers` alone; six gate-off pins. The one file that is
  fully green (11/11) against today's binary, by design — everything
  else here is a watched-failing probe until MOD-0.5c lands.

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

## The D33 §9.3 record

Each file's header carries its own measured pass/fail split against the
[MOD-0.5a]-gate binary (vocabulary landed, `modifiers` has no producer).
Whole-directory total: 56 cases, 16 PASS today (11 in
`malformed_and_gate.rxt`'s already-correct gate pins, reset.rxt's J-cell
`perr`, plus 4 control/coincidental-agreement cells scattered through the
others), 40 FAIL with "requires module 'modifiers'" — measured 2026-08-12
via `PCREC=<binary> bash tests/harness/run.sh tests/modifiers`, before
MOD-0.5b/c land. Re-run per file with the same command pointed at one
`.rxt` path. (Separately, `python3 tests/harness/verify_rxt.py
tests/modifiers` reports its own PASS=26/26 — that is the ORACLE
cross-check on the 26 non-`# pcre2-only` cases, a different axis from the
pcrec-binary pass/fail count above; do not conflate the two.)

Maintenance: add blocks when the module's producing scope grows (M5's
UTF/UCP re-measurement of the `r`/`aD aP aS aT aW` no-ops, per [MOD-0.5a]
ruling 1, brings its own cases; so does `assertions`/`named-groups` landing
enough to turn the two forward pins above green).
