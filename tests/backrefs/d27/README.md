# tests/backrefs/d27 — D27 blinded acceptance corpus, module `backrefs`

## Author and blindness statement

Written by a D27-blinded test author for plan step [M6.5.3], working
FROM THE PCRE2 GOAL, not from any pcrec implementation. `src/` and
`tests/` were denied for the whole of this work; the cell allowlist
permitted only `GOAL_FACTS.md`, `docs/testing.md`, `docs/spec/match_api.md`,
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`,
`docs/design/backrefs_measurements/probes/br_oracle.py`, and a prebuilt,
not-yet-implementing `build/pcrec` binary (permitted only to confirm
refusal-direction cells). **libpcre2 10.46 is the oracle of record**
(measured live via `br_oracle.py`; version string `10.46 2025-08-27`).
Every expectation in every `.rxt` file below was measured against real
libpcre2 before being written down — none were derived, guessed, or
carried over from GOAL_FACTS.md's own prose without independent
re-measurement (GOAL_FACTS.md's facts were used to decide WHAT to test,
never as the source of an expected VALUE).

**Auto-injected disclosure** (files present in context at spawn that
were not fetched by choice): the session-root `CLAUDE.md` at
`/home/duxevents/pcrec/CLAUDE.md` (project mandate/conventions) and the
memory index `MEMORY.md` plus its three linked memory files
(`pcrec-process-preferences.md`, `pcrec-project-status.md`,
`pcrec-check-design-lessons.md`) under
`/home/duxevents/.claude/projects/-home-duxevents-pcrec/memory/`.

## What is, and is not, checked against pcrec

**Nothing in this corpus's acceptance cells (numeric/octal/spellings/
caseless/dupnames/interactions/syntax_errors) has been run against
`build/pcrec`.** The `backrefs` module is unbuilt (every `backrefs` row
in `build/pcrec --list-syntax` reads `unbuilt`), so every acceptance
pattern here currently fails to COMPILE under pcrec, for reasons that
have nothing to do with whether the expectation itself is right. That
is expected and correct for a D27 corpus authored ahead of its module:
the record stays exactly as authored, and the acceptance run happens at
merge review once `backrefs` lands.

**The one exception is `gating.rxt`.** Its cells assert pcrec's CURRENT
refusal behavior (both directions of the module gate), which the D27
brief explicitly permits confirming today. Every cell in `gating.rxt`
was run against the real `build/pcrec` in this checkout and does exit
nonzero as asserted; `oracle.py --` (see below) re-confirms this
automatically whenever it processes that file.

## Per-file table (grep-counted)

| File | pattern blocks | perr | `# pcre2-only` blocks | m | n | ms | ns | gp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `numeric.rxt` | 13 | 0 | 4 | 11 | 12 | 1 | 1 | 12 |
| `octal.rxt` | 19 | 3 | 18 | 15 | 4 | 0 | 0 | 6 |
| `spellings.rxt` | 14 | 2 | 11 | 12 | 6 | 0 | 0 | 13 |
| `caseless.rxt` | 7 | 0 | 2 | 6 | 6 | 0 | 0 | 6 |
| `dupnames.rxt` | 14 | 2 | 14 | 16 | 12 | 0 | 0 | 21 |
| `interactions.rxt` | 6 | 0 | 6 | 5 | 2 | 0 | 0 | 5 |
| `syntax_errors.rxt` | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| `gating.rxt` | 11 | 11 | 0 | 0 | 0 | 0 | 0 | 0 |
| **TOTAL** | **94** | **28** | **55** | **65** | **42** | **1** | **1** | **63** |

(Counts are `grep -c` over each file: `^pattern `, `^perr$`, `^# pcre2-only`,
`^m `, `^n `, `^ms `, `^ns `, `^gp `. No `g` (LIVE) lines appear anywhere in
this corpus — every capture expectation is `gp` (pending-VM), since
`backrefs` is entirely unbuilt today and forces the VM engine once it
does land (registry: `engines vm` on every `backrefs` esc row); see "On
g vs gp" below.)

`octal.rxt` and `dupnames.rxt` are near-entirely `# pcre2-only`
(18/19 and 14/14 pattern blocks respectively) because python3's `re`
has no octal-fallback disambiguation at all and no `(?J)`/DUPNAMES/`\k`
support at all (see the divergence list below) — both files say so in
their own headers.

## Oracle: `oracle.py`

```
python3 oracle.py                     # checks every *.rxt in this directory
python3 oracle.py numeric.rxt ...     # checks specific files
```

`oracle.py` is INDEPENDENT: it does not import or share code with any
other `.rxt` parser in the tree (all of them live under `tests/`, denied
to this cell anyway). It re-derives the `.rxt` grammar directly from
`docs/testing.md`'s prose (pattern/flags/features/perr/m/n/ms/ns/g/gp,
the subject-escape table, the `g`-vs-`gp`/population rules) and
re-queries libpcre2 through `br_oracle.py` for every single `m`/`n`/
`ms`/`ns`/`g`/`gp` line in every file — marked `# pcre2-only` or not,
since libpcre2 is the oracle of record for ALL of them (D26); the
`# pcre2-only` mark only says whether a SECOND, python-side check would
also apply, which this script does not attempt (python's `re` is not
this lane's oracle of record; every python fact quoted in the comments
above was measured separately, ad hoc, during authoring, and is not
wired into `oracle.py` itself).

**Result on this checkout**, freshly re-run for this README:

```
libpcre2: 10.46 2025-08-27
file                    checked  failed   perr
caseless.rxt                 18       0      0
dupnames.rxt                 49       0      2
gating.rxt                   11       0     11
interactions.rxt             12       0      0
numeric.rxt                  37       0      0
octal.rxt                    25       0      3
spellings.rxt                31       0      2
syntax_errors.rxt             0       0     10
TOTAL                       183       0     28
```

183 measured expectations (spans + capture slots across every `m`/`ms`
case), zero failures, exit code 0. The 28 `perr` blocks are compile-time
assertions oracle.py does not re-derive a span for; for `gating.rxt`
specifically (and only that file), `oracle.py` ALSO shells out to
`build/pcrec` for each of its 11 `perr` cells and confirms a nonzero
exit under the declared `features` — all 11 pass today.

## Divergence list (python3 `re` vs. libpcre2, this module's scope)

Every python fact below was measured directly against python 3.14.4
during authoring, not assumed from GOAL_FACTS.md prose (which already
asserted most of these; each was re-confirmed independently):

- **Self- and forward-references**: python raises `cannot refer to an
  open group` / `invalid group reference` at COMPILE time for
  `(a\1)`, `\2(a)(b)`, etc. — no python expectation exists for any such
  cell (numeric.rxt).
- **The whole \N octal-vs-backreference disambiguation** (F4): python
  always reads `\NN` as a decimal backreference and never falls back to
  octal — `re.compile(r'(a)\10')` raises `invalid group reference 10`,
  where libpcre2 reads it as octal `\010`. octal.rxt is consequently
  ~entirely pcre2-only (18 of 19 pattern blocks).
- **`\g`, `\k`, `(?J)`/DUPNAMES**: absent from python3's `re` entirely
  (F5). Any cell using any of these spellings has no python oracle.
  `(?<n>...)` is ALSO refused by python (only `(?P<n>...)` is accepted),
  so `^(?<n>a)(?P=n)$` has no python expectation even though `(?P=n)`
  alone is python syntax.
- **Non-leading `(?i)`/`(?-i)`** (F15): python refuses a global inline
  flag anywhere but the pattern's own start — `^((?i)a)\1$` and
  `^(?i)(a)(?-i)\1$` are both python compile errors, even though the
  second one's OWN leading `(?i)` is, in isolation, legal python syntax.
  The SCOPED form `(?i:...)`, by contrast, IS python-legal at any
  position and is used in caseless.rxt where it suffices.
- **Class-position `[\8]` `[\9]` `[\k]` `[\g]`** (F16): python rejects
  all four as bad escapes inside a class; PCRE2 reads them as the
  literal characters `8`, `9`, `k`, `g`. octal.rxt's class-position
  block is entirely pcre2-only.
- **`flags i` (CLI `-i` / `PCRE2_CASELESS`) IS python-checkable** via
  `re.IGNORECASE | re.ASCII` (docs/testing.md's own convention for
  `verify_rxt.py`), and was used that way for caseless.rxt's F8 cells
  (byte-mode fold boundary) rather than the pcre2-only-marked inline
  `(?i)`/`(?-i)` cells, since the CLI-level mechanism agreed with
  libpcre2 on all three subjects tested (measured: `re.IGNORECASE|
  re.ASCII` also does NOT fold `\xc0`/`\xe0` or `\xdf`/`ss`).

## A registry finding, flagged for the merge review (not fixed here)

`build/pcrec --list-syntax` currently attributes DUPNAMES/`(?J)`
entirely differently from every other construct in this corpus:

- `(?J)` itself is gated by module **`modifiers`**
  (`requires module 'modifiers'`), not `backrefs`.
- The actual duplicate-name RESOLUTION logic is attributed to module
  **`named-groups`**, not `backrefs` — measured message: `inline option
  'J' (dupnames): module 'named-groups' does not implement duplicate
  group names (see docs/pcre2_compliance.md)`.
- That wording ("does not implement... out of pcrec's scope", per the
  registry's fuller text) reads as more final than every other
  backrefs-family refusal in this corpus, which says "is not
  implemented **yet**". Whether DUPNAMES resolution eventually lands
  under `backrefs`, under `named-groups`, or is jointly owned is a
  module-boundary question for the merge review, not something this
  blinded lane can or should resolve — `dupnames.rxt` and `gating.rxt`
  document today's actual behavior (cells 9–11 in `gating.rxt`) without
  asserting what SHOULD be true.
- A second, more minor finding in the same area: `(?J)` is refused
  UNCONDITIONALLY once its syntax is recognized (module `modifiers`
  present), even in a pattern with no duplicate name at all anywhere
  (`(?J)a` alone refuses, measured) — not merely refused lazily at the
  point a collision is actually declared.
- Separately, `docs/pcre2_compliance.md` is named in that refusal
  message but is NOT reachable from this cell's allowlist (not under
  `docs/design/`, `docs/spec/`, or any other permitted path) — noted
  here rather than fetched.

## What this corpus deliberately does NOT attempt

- **A find-all-loop cell.** `docs/spec/match_api.md` §3.1's find-all
  loop (empty-match advance via `<prefix>_next_pos`) is a caller-side
  protocol built on repeated `<prefix>_search` calls, not a single
  `.rxt` case — the `.rxt` format has no find-all directive. `startpos`
  IS covered directly (numeric.rxt's `ms`/`ns` block, F12), which is the
  primitive the loop is built from.
- **`PCRE2_INFO_NAMETABLE` ordering under duplicates** (F11). Measured
  independently for this README (see below) and confirmed to match
  GOAL_FACTS's claim, but it is metadata about `rx_info.groups`'
  compile-time layout, not a `m`/`n`/`g` matching fact — no `.rxt`
  directive expresses it. Recorded here as a re-derivation check, not a
  corpus cell: `(?<z>1)(?<a>2)(?<z>3)(?<a>4)` compiled with
  `PCRE2_DUPNAMES` reports `[(2, 'a'), (4, 'a'), (1, 'z'), (3, 'z')]` —
  sorted name-ascending, then number-ascending within a name, exactly as
  F11 states.
- **`\g<name>`/`\g'name'` as MATCHED subroutine calls.** Confirmed (F6)
  to be genuine PCRE2 subroutine-call semantics, not backreferences —
  testing their match behavior is module `recursion`'s corpus, not this
  lane's. `spellings.rxt` documents the split and includes only
  compile-refusal cells for these two spellings; `gating.rxt` does not
  duplicate them.

## GOAL_FACTS.md facts checked and found accurate

Every numbered fact (F1–F16) that this corpus exercises was independently
re-measured against libpcre2 before being trusted, including the exact
spans GOAL_FACTS.md itself quotes (F2, F9, F12, F13, F14) — all matched
on first measurement, with no corrections needed to any GOAL_FACTS.md
claim. The one place this lane went beyond GOAL_FACTS.md's own text was
discovering the module-attribution finding above, which GOAL_FACTS.md
does not address (it describes PCRE2's semantics, not pcrec's registry).
