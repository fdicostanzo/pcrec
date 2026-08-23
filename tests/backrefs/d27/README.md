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

## Status: module landed, acceptance run complete (2026-08-22)

The `backrefs` module landed at main `3aa446f`. The corpus was run
against it at merge review: **193 pass / 7 fail on the first run, 0 of
the 7 an implementation divergence** — all seven were corpus-side
authoring bugs in this lane's own `.rxt` files, in two classes (a
`features`-line ordering slip in `caseless.rxt`, and three `gating.rxt`
cells whose `perr` assertion went vacuous the moment the module they
were gating started compiling — success, not a bug). All seven are
fixed; see "Acceptance run" below for the full account, and the
per-file table and oracle result below reflect the corpus AS FIXED.
`group cases pending-vm: 0` on that run — every `gp` line in this
corpus scored LIVE, so none needed conversion to `g` (see "On `g` vs
`gp`" further down).

## What is, and is not, checked against pcrec

Originally (at authoring time, module unbuilt) nothing in this corpus's
acceptance cells had been run against `build/pcrec` — every acceptance
pattern failed to COMPILE, for reasons unrelated to whether the
expectation itself was right, and `gating.rxt` was the sole exception
(its cells assert refusal, which the brief explicitly permitted
confirming pre-landing). **That has changed**: post-landing, every cell
in every file in this corpus has now been run end-to-end against the
real, refreshed `build/pcrec` — compiled, built with a from-spec driver,
and executed against every subject — with zero unexpected failures
(140/140; see "Acceptance run" below for the tool and counts).

## Per-file table (grep-counted, post-fix)

| File | pattern blocks | perr | `# pcre2-only` blocks | m | n | ms | ns | gp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `numeric.rxt` | 13 | 0 | 4 | 11 | 12 | 1 | 1 | 12 |
| `octal.rxt` | 19 | 3 | 18 | 15 | 4 | 0 | 0 | 6 |
| `spellings.rxt` | 14 | 2 | 11 | 12 | 6 | 0 | 0 | 13 |
| `caseless.rxt` | 7 | 0 | 2 | 6 | 6 | 0 | 0 | 6 |
| `dupnames.rxt` | 14 | 2 | 14 | 16 | 12 | 0 | 0 | 21 |
| `interactions.rxt` | 6 | 0 | 6 | 5 | 2 | 0 | 0 | 5 |
| `syntax_errors.rxt` | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| `gating.rxt` | 11 | 8 | 0 | 3 | 3 | 0 | 0 | 4 |
| **TOTAL** | **94** | **25** | **55** | **68** | **45** | **1** | **1** | **67** |

(Counts are `grep -c` over each file: `^pattern `, `^perr$`, `^# pcre2-only`,
`^m `, `^n `, `^ms `, `^ns `, `^gp `. `gating.rxt`'s perr count dropped from
11 to 8 and gained 3 pattern blocks' worth of `m`/`gp` cases — see
"Acceptance run" below for why. No `g` (LIVE) lines appear anywhere in
this corpus — every capture expectation is written as `gp` (pending-VM at
authoring time, since `backrefs` was unbuilt then and forces the VM
engine, registry: `engines vm` on every `backrefs` esc row) — but as of
the acceptance run every `gp` line now SCORES live (`group cases
pending-vm: 0`), per the `gp`-self-activates rule in docs/testing.md; see
"On `g` vs `gp`" below.)

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

**Result on this checkout**, freshly re-run for this README (post-fix,
against the module-landed `build/pcrec`):

```
libpcre2: 10.46 2025-08-27
file                    checked  failed   perr
caseless.rxt                 18       0      0
dupnames.rxt                 49       0      2
gating.rxt                   18       0      8
interactions.rxt             12       0      0
numeric.rxt                  37       0      0
octal.rxt                    25       0      3
spellings.rxt                31       0      2
syntax_errors.rxt             0       0     10
TOTAL                       190       0     25
```

190 measured expectations (spans + capture slots across every `m`/`ms`
case), zero failures, exit code 0. The 25 `perr` blocks are compile-time
assertions oracle.py does not re-derive a span for; for `gating.rxt`
specifically (and only that file), `oracle.py` ALSO shells out to
`build/pcrec` for each of its 8 `perr` cells and confirms a nonzero exit
under the declared `features` — all 8 pass.

## Acceptance run (2026-08-22, module landed at main `3aa446f`)

The manager's acceptance run (the real `tests/harness/run.sh`, outside
this cell) reported **193 pass / 7 fail on the first run against the
landed module, 0 real divergences, `group cases pending-vm: 0`**. All
seven were corpus-side and are now fixed in this cell, in two classes:

**(a) A directive-ordering bug in `caseless.rxt`'s F8 section (3
blocks, `flags i` byte-mode-fold cells).** During authoring, a
follow-up edit to those three blocks (converting them from inline
`(?i)` to the CLI-level `flags i` form) was written before a later
corpus-wide pass that moved every `features`/`flags` directive to
AFTER its `pattern` line (docs/testing.md: "given after its pattern
line") — that later pass's own sed-style fix missed re-normalizing
this specific edit's output, leaving `features backrefs` stranded
BEFORE `pattern` in those three blocks. The practical effect: the
harness read those blocks as having no `features` line at all,
defaulting to `std1` (`classes,modifiers`) — no `backrefs` — so `\1`
inside them refused to compile. Fixed by moving `features backrefs` to
after each block's `pattern` line (the same convention every other
block in the corpus already used correctly). Independently re-verified,
both via direct `build/pcrec` compile and via the full end-to-end tool
described below.

**(b) Three `gating.rxt` cells were VACUOUS `perr` blocks once the
module landed**: `(a)\1` under `features backrefs` (cell 2), `(?<n>a)
\k<n>` under `features backrefs,named-groups` (cell 7), and
`(?J)(?<a>x)(?<a>y)` under `features modifiers,named-groups,backrefs`
(cell 10) all now COMPILE — which is the module landing working
correctly, not a regression. Converted in place to real `m`/`gp` match
cases, verified against libpcre2 (cell values re-measured, not assumed
from the pre-landing `perr` text). Cell 10 additionally required
updating stale commentary: pre-landing, `(?J)`'s dupname-resolution
refusal named module `named-groups`; post-landing (R32 ASK-1) it names
`backrefs` directly (`pcrec: inline option 'J' (dupnames) requires
module 'backrefs'`) — the corpus's OUTCOME expectations never depended
on this attribution (they come from PCRE2, D26), only the comment
trail needed updating, in `gating.rxt` and `dupnames.rxt` both.

**Full end-to-end re-verification.** Since `build/pcrec` now
implements this module, this lane wrote a from-spec re-implementation
of `tests/harness/driver.c`'s protocol (`docs/testing.md`'s own
description — subject-escape decoding, `RX_NCAPS`-pair printing,
give-up codes — tests/ itself stays denied) and compiled + ran EVERY
block in every `.rxt` file in this directory against the real,
refreshed binary: **140/140 pass, 0 unexpected failures**, confirming
both fixes above and that nothing else regressed. This tool is
scratch-only (not part of the deliverable — the real acceptance
instrument is `tests/harness/run.sh`, run by the manager outside this
cell) but its result is recorded here as this lane's own independent
confirmation before resubmitting.

### On `g` vs `gp`

Every capture expectation in this corpus was written `gp` (pending-VM)
at authoring time, per docs/testing.md's own guidance for a corpus
authored ahead of its module ("so the corpus can be authored once...
and grow LIVE automatically as the VM emitter lands"). The acceptance
run's `group cases pending-vm: 0` confirms every `gp` line in this
corpus now scores exactly like `g` under the landed module — per
docs/testing.md's self-activation rule, this needs no corpus edit
("Authors are free to leave the `gp` marker in place after that point
... or promote it to `g` for documentation clarity — the harness
behaves identically either way"). No `gp` lines were promoted to `g`
in this fix pass; that stayed a no-op by design.

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

## A registry finding, flagged for the merge review — RESOLVED at landing

Pre-landing, `build/pcrec --list-syntax` attributed DUPNAMES/`(?J)`
entirely differently from every other construct in this corpus: `(?J)`
itself was gated by module `modifiers`, and the actual duplicate-name
RESOLUTION logic was attributed to module `named-groups` (not
`backrefs`), with a message reading "does not implement duplicate
group names ... out of pcrec's scope" — wording that read as more
final than the "not implemented **yet**" wording every other
backrefs-family refusal carried. That was flagged here at authoring
time as a module-ownership question for the merge review, not
something this blinded lane could or should resolve on its own.

**Resolution (R32 ASK-1, landed 2026-08-22 at main `3aa446f`):** the
landed module attributes BOTH `(?J)` and DUPNAMES resolution to
`backrefs`. Measured post-landing: `pcrec: inline option 'J' (dupnames)
requires module 'backrefs'` — `named-groups` no longer appears in that
refusal at all. `dupnames.rxt` and `gating.rxt` (cells 9 and 11) are
updated to record both the pre-landing behavior (for the historical
record) and the post-landing attribution; none of this corpus's
OUTCOME expectations changed, since they were always derived from
PCRE2 (D26), never from pcrec's own module boundaries — only the
commentary describing WHY a cell refuses needed updating.

The one still-true minor finding from authoring time: `(?J)` is refused
UNCONDITIONALLY once its syntax is recognized (module `modifiers`
present), even in a pattern with no duplicate name at all anywhere
(`(?J)a` alone refuses, re-measured post-landing too) — not merely
refused lazily at the point a collision is actually declared. And
`docs/pcre2_compliance.md`, named in the pre-landing refusal message,
was never reachable from this cell's allowlist — noted rather than
fetched, then or now.

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
