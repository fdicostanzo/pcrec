# D27 blinded corpus: module `named-groups`

Author: D27-blinded test author (worktrees/ngauthor-cell), 2026-08-18.
Written from PCRE2's documented/observable semantics for named
capturing groups, without access to pcrec's `src/` or `tests/` trees
(the cell's own allowlist: `docs/testing.md`, `docs/spec/match_api.md`,
`build/pcrec`, nothing else). This is the acceptance corpus for the
PROMISE of module `named-groups` -- it is not expected to pass today.
Verified live against `build/pcrec` (2026-08-18): every declaring
spelling ((?<name>...), (?'name'...), (?P<name>...)) currently refuses
with `requires module 'named-groups'`, `--features named-groups` is
already a recognized module name (no "unknown module" error), and an
unrelated control pattern `(a)(b)(c)` compiles cleanly -- confirming
both the module's absence and that this cell's copy of `build/pcrec` is
otherwise healthy.

## Files

| File | Patterns / blocks | perr blocks | Focus |
|---|---|---|---|
| `spellings.rxt` | 10 | 0 | Declaring-spelling equivalence: `(?<name>...)`, `(?'name'...)`, `(?P<name>...)` are one ordinary capturing group; unnamed-group baseline for direct comparison; quantified named groups; mixed-spelling alternation |
| `name_syntax.rxt` | 16 | 10 | Name-syntax edges: valid underscore/digit-after-first-char/32/33/128-char names; invalid leading-digit/empty/hyphen/space/dot names (all three spellings for leading-digit); non-ASCII name; 129-char name |
| `duplicates.rxt` | 5 | 5 | Duplicate names rejected: same spelling, mixed spelling, non-adjacent, across alternation branches |
| `numbering_capture.rxt` | 8 | 0 | Named/unnamed interleaving, nesting, optional participation, alternation, and the two cross-iteration capture rules (docs/spec/match_api.md S5.1) applied to named groups |
| `case_sensitivity.rxt` | 2 | 0 | Group NAME is case-sensitive identity, distinct from CASELESS matching of the group's content: `name` and `NAME` are two distinct groups, with and without the block's `flags i` |
| `oracle.py` | -- | -- | Standalone python3 verifier for the five files above (see below) |

**Totals** (grep-counted, matches `oracle.py`'s 39+2=41 blocks
processed): 41 pattern blocks. 15 are `perr` compile-failure
expectations; the remaining 26 carry `m`/`g` match-and-capture
expectations, totaling 42 individual `g` capture-slot assertions
across them (including a 3-way check for the nested-named-groups case
and a 3-way check each for the two cross-iteration-retention cases).

**Revision note (2026-08-18, case-sensitivity addition):** added
`case_sensitivity.rxt` (2 blocks, both `m`/`g`, both python-verifiable,
no `pcre2-only`) per a manager-relayed question: whether `(?<name>...)`
and `(?<NAME>...)` in one pattern are the same group (duplicate-name
rejection) or two distinct groups. Measured (libpcre2 10.46 and
python3 `re` agree): two distinct groups, both capturing independently,
unaffected by whether the block also matches caselessly (`flags i`
changes which bytes the group's own text matches, not name identity).
See "Coverage axes" below.

**Revision note (2026-08-18, post-manager-review):** the length-cap
figure below was corrected from 32 to 128 code units after the manager
independently probed real libpcre2 10.46 (ctypes dlopen, outside this
cell) -- see "Unverifiable" below for the full before/after. The
33-char-name block moved out of the `perr`/`pcre2-only` set into an
ordinary oracle-verified `m`/`g` match (it is valid at the corrected
limit), and two new blocks were added at the real boundary: a 128-char
valid name and a 129-char `perr` name. The 32-char block is unchanged
in behavior, just re-captioned -- it was never wrong, only mis-labeled
as "at the limit."

Every non-`perr` block uses `features named-groups` so that, once the
module lands and is enabled, the block exercises the module's real
semantics rather than accidentally passing because named-groups was
folded into the default feature set (`PCREC_DEFAULT_FEATURES`, today
`std1 = {classes, modifiers}` per docs/spec/match_api.md's discussion
of the fuzzer's default invocation -- there is no reason to assume
`named-groups` joins that default, and the corpus does not assume it).
`perr` blocks also carry `features named-groups` for the same reason:
once implemented, they must still fail for their OWN reason (bad name
syntax, duplicate name), not merely because the module was off.

## Oracle: `oracle.py`

A from-scratch python3 script (this cell was not given
`tests/harness/verify_rxt.py`, which lives outside the allowlist). It
parses the subset of the `.rxt` grammar docs/testing.md documents that
this corpus uses (`pattern`, `features`, `flags`, `perr`, `m`, `n`,
`g`; `ms`/`gp` are not used by this corpus and are unimplemented in the
parser), translates every pattern to python `re`'s only accepted
spelling, `(?P<name>...)`, and re-derives every expectation
independently.

Run it from this directory: `python3 oracle.py` (defaults to the five
`.rxt` files here). Current output: **PASS=39, FAIL=0,
DIVERGENCE-DOCUMENTED=2, SKIP-UNVERIFIABLE=0**, `python3 --version` =
`Python 3.14.4` (this box). The 39 PASS rows are every block not
marked `# pcre2-only`; the 2 DIVERGENCE-DOCUMENTED rows are the two
`# pcre2-only` blocks (below -- both now at the corrected 128-code-unit
boundary, not the stale 32). A `FAIL` row would mean this corpus's own
hand-derived expectation disagrees with python's actual behavior on the
translated pattern -- there are none.

### Translation applied

- `(?<name>...)` -> `(?P<name>...)`, guarded against colliding with
  lookbehind `(?<=`/`(?<!` (this corpus contains no lookbehind, but the
  regex doing the substitution excludes those two forms on principle).
- `(?'name'...)` -> `(?P<name>...)`.
- `(?P<name>...)` needs no translation.

This is a pure spelling substitution: PCRE2 documents all three as
producing an identical ordinary capturing group, so the translated
pattern's match/capture behavior is what all three spellings must
produce.

### Unverifiable (2 blocks, both in `name_syntax.rxt`, both marked `# pcre2-only`)

python3's `re` diverges from PCRE2 on two name-syntax rules. This
cell has no dlopen shim for libpcre2 in its allowlist (unlike
`tests/fuzz/pcre2_abi.h`, which docs/spec/match_api.md mentions but
this cell does not have), so this author's original figures came from
recollection of PCRE2's own documentation, not a runnable instrument --
and one of them was WRONG. The manager subsequently probed the real
libpcre2 10.46 on the project box directly (ctypes dlopen, from outside
this cell, 2026-08-18) and both rows below now carry that measurement
in place of the original documentation-only figure:

1. **Group-name length.** This cell originally wrote "32-code-unit cap
   for the 8-bit library," sourced from documentation recollection, not
   measurement. **That figure was stale.** Manager-measured against
   real libpcre2 10.46: 32, 33, 127, and 128-character names all
   COMPILE; 129 characters REFUSES with err 148, "subpattern name is
   too long (maximum 128 code units)." The real cap is 128, not 32.
   This corpus now reflects the measured figure: the 33-char-name block
   (originally the corpus's `perr` case for "past the cap") is now an
   ordinary valid `m`/`g` block, matching a 128-char-name block added
   alongside it, and the `perr`/`pcre2-only` boundary case moved out to
   129 characters, citing the manager's libpcre2 measurement directly
   in its comment. python's `re` imposes no length cap on a group name
   at all -- confirmed live, both at the old (33-char) and new
   (129-char) boundary -- so the 129-char block still cannot be
   python-oracle-verified and stays `pcre2-only`; `oracle.py` reports
   it as `DIVERGENCE-DOCUMENTED`. The 32-, 33-, and 128-char blocks are
   NOT marked `pcre2-only` and ARE oracle-verified as ordinary matches,
   since python compiling and matching them correctly is real evidence,
   independent of where the cap actually sits.
2. **Character set for the name.** PCRE2 restricts a group name to
   ASCII alphanumeric characters and underscore. python's `re` follows
   python identifier rules, which admit non-ASCII Unicode letters --
   confirmed live: `re.compile("(?P<náme>a)")` compiles without error.
   This row's PCRE2-side claim is now **manager-verified against real
   libpcre2 10.46** (2026-08-18): `(?<namé>a)` REFUSES with err 162,
   "subpattern name expected" -- upgraded from this author's original
   documentation-only claim, which the measurement confirmed was
   correct on this axis (only the length-cap axis above was wrong). The
   corpus's non-ASCII-name block (one literal accented character, raw
   UTF-8 bytes in the pattern text, since `.rxt` pattern lines take no
   escaping per docs/testing.md) asserts `perr`, marked `pcre2-only`,
   and stays that way -- python still accepts the pattern, so it still
   cannot be python-oracle-verified.

**Provenance summary**: both rows are now backed by a real oracle run
(libpcre2 10.46, manager-executed, 2026-08-18) rather than
this author's documentation recollection. One of the two original
figures (the length cap) was wrong by a factor of 4; the other (the
ASCII-only character set) was confirmed correct. Neither is
"documented, not assumed" any more in the weaker sense the original
text used -- both are now instrument-measured, just not by an
instrument this cell had access to.

Every OTHER `perr` block in `name_syntax.rxt` and all of
`duplicates.rxt` IS oracle-supported in the weaker-but-real sense
docs/testing.md's own exclusion philosophy uses for `perr`: python
also rejects the pattern (confirmed by `oracle.py`'s PASS rows, which
show python's actual `re.error` text), which is convergent evidence
even though the two engines' internal reasons for rejecting may not be
worded identically -- per this project's D26 compatibility standard
(compatibility standard, project CLAUDE.md), what a pattern MATCHES
(here, that it's REFUSED at all) is the exact-tier obligation, not the
diagnostic's wording.

## Module boundary: what this corpus deliberately does NOT test

- **Backreference-by-name spellings** (`\k<name>`, `\k'name'`,
  `\k{name}`, `(?P=name)`) belong to a different module, `backrefs`,
  per the brief. No pattern in this corpus uses any of them, and no
  match expectation anywhere here depends on backreferencing a named
  group. `named-groups`' own promise is the DECLARING spellings only.
- **`rx_info.nnames`/`rx_info.groups` reflection** (docs/spec/match_api.md
  S6): the `.rxt` `m`/`n`/`g` mechanic drives `tests/harness/driver.c`,
  which prints only `<prefix>_search`'s `caps[]` pairs -- it has no path
  to read `<prefix>_info` at all. This corpus therefore cannot exercise
  `nnames` or the `groups[]` array (including its still-unfixed sort
  key, docs/spec/match_api.md S6: "no document states the sort KEY").
  That is an instrument limitation of the `.rxt` format, not a decision
  to skip the promise -- flagging it honestly rather than writing a
  `.rxt` case that cannot actually check what it claims to.
- **Conditional-pattern named-group references** (`(?(name)...)`) and
  **recursion into a named group** (`(?&name)`, `(?P>name)`) are
  `advanced`-module constructs per `tests/CLAUDE.md`'s component list
  (docs/testing.md's "Organizing tests by component" table) and are out
  of scope for the same reason as backrefs.
- **Capture delivery is by NUMBER, not by name.** docs/spec/match_api.md
  S5.2 states plainly there is "no run-time name lookup" in the frozen
  match API -- `numbering_capture.rxt`'s header note makes this
  explicit so a reader does not go looking for a name-indexed `g`-line
  syntax that does not exist and was never proposed.

## Coverage axes, summarized

- **Declaring-spelling equivalence**: all three spellings, cross-checked
  pairwise and in mixed-spelling alternation, always reducing to the
  same left-to-right group number and the same capture span as the
  unnamed form.
- **Name syntax**: valid (underscore-leading, underscore-only,
  digit-after-first-char, 32/33/128-char names) and invalid (leading
  digit, empty, hyphen, space, dot, non-ASCII, 129-char, past the
  manager-measured 128-code-unit cap) names, with the leading-digit
  case repeated across all three spellings to show the validation is
  spelling-independent.
- **Duplicate names**: same spelling, mixed spelling, non-adjacent
  (third group intervening), and across alternation branches -- all
  rejected under PCRE2's DUPNAMES-off default, which is pcrec's only
  reachable behavior (no flag surfaces PCRE2_DUPNAMES).
- **Numbering interleave**: named among unnamed groups, nested named
  groups, named groups under a quantifier's cross-iteration retention
  and empty-final-iteration-overwrite rules (both already part of
  pcrec's shipped, unnamed-group contract per docs/spec/match_api.md
  S5.1 -- this corpus checks that a named group is not a special case
  of that rule), and named/unnamed groups in different alternation
  branches.
- **Case sensitivity of the name itself**: `name` and `NAME` are two
  distinct names (two distinct groups, capturing independently), not a
  duplicate-name collision (contrast `duplicates.rxt`) -- checked both
  under default matching and under the block's `flags i`, since
  caseless matching of a group's CONTENT is a different axis from
  case-sensitive identity of its NAME, and the two must not be
  conflated.

## What "PASS" means here, and what it does not

`oracle.py`'s PASS count is evidence this corpus is internally
consistent with python3 `re`'s behavior on the translated patterns --
it is NOT evidence about pcrec, which does not implement this module
yet (verified above). When module `named-groups` lands, the intended
use of this corpus is exactly docs/testing.md's own prescription for a
component directory: run these `.rxt` files against the real
`build/pcrec` (`bash tests/harness/run.sh d27_named_groups` from a
tree that has the harness) and expect every non-`perr` block's `m`/`g`
lines to hold and every `perr` block to still refuse to compile.
