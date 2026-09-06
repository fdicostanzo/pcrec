# tests/uprops — module `unicode-props`, the checks a `.rxt` file cannot make

[M5.0] stage 3. `make test-uprops` (the `byte` arm, part of `make test`);
`make test-uprops-utf8` (the whole code-point space, opt-in).

The module's ANSWERS live in `tests/utf8/axis04_p_categories.rxt` — the
D27-blinded corpus, 136 blocks / 462 cases, promoted at this stage from the
oracle answers its author carried in each block's comment. This directory is
everything that corpus structurally cannot express.

## Files

- **run_uprops_tests.sh** — four sections, and the reason there are four is
  that each sees something none of the others can. Read its own header for
  the per-section argument; the summary is below.
- **uprops_oracle.c** — the libpcre2 side, through the shared dlopen shim
  (`tests/fuzz/pcre2_abi.h`), so a clone without libpcre2 SKIPS loudly rather
  than failing to load. Also the VERSION REPORTER the drift policy turns on.
- **uprops_sweep.c** — the pcrec side, compiled once per property against
  that property's own emitted artifact.
- **uprops_compare.py** — the comparator, and the ONE place the
  Unicode-version drift policy is written down.

## The four sections

**§1 the generated table is not stale.** `third_party/ucd-16.0.0/generate.py
--check` re-derives `src/parse/uprops_tables.inc` from the vendored UCD.
`cls_bits.inc`'s "never hand-edited" banner made mechanical.

**§2 the shipped name set, from a HAND-WRITTEN list.** The list in the script
is derived from `utf8_design.md` §3.4's families and the UCD's own category
vocabulary — the PROMISE side — and deliberately not read from the generated
table, so a property the generator silently DROPPED is a red cell rather than
a name nobody asks about. The count is asserted against the `.inc`'s row count
in both directions, which closes the other half (a property silently ADDED).

**§3 the membership differential.** Every shipped property, both encodings,
the **whole code-point space**, pcrec's own emitted artifacts against
libpcre2. It is affordable at that resolution because neither side calls the
matcher per code point: both do ONE find-all pass over a subject that is every
code point in order, so there is no sampling rule for a bug to hide behind.

**§4 the oracle-free semantic invariants.** `\P{X}` is the complement of
`\p{X}`, `\p{^X}` is `\P{X}`, `\P{^X}` is `\p{X}`, `[^\p{X}]` agrees with
`\P{X}`, and under `-i` `\p{Lu}`/`\p{Ll}`/`\p{Lt}` are `\p{L&}` while every
other property is unchanged. These hold at EVERY Unicode version, so they are
the part of the suite that never degrades to a drift budget — and each has a
NON-VACUITY CONTROL beside it (a pair required to DISAGREE), because a
compiler that answered the same set for everything would satisfy the
agreements alone.

**§4 is the section that found a real bug**, which is the argument for having
it. `[^\p{L}] == \P{L}` went red at first run: `esc_class_value` never
advanced the cursor for a produced `EXT_MEMBERS`, so `[^\p{L}]` excluded `{`
and `}` as well as the letters and `[\p{L}-z]` never saw its own dash. **The
membership differential could not see it** — both of its sides compile `\p{L}`
at an ATOM, where the bug does not live — and neither could the corpus, whose
`\p` blocks are all atom-position. It is `esc_atom`'s [M6.5.2] lesson at the
class position, which that entry predicted in advance ("a LONGER-BODIED ATOM
PRODUCER must carry its own end and advance here"); every earlier class
producer's construct IS its two-byte escape, so nothing had ever needed it.

## The Unicode-version drift policy, and why it is not a skip

`uprops_compare.py`'s header is the authority. In short: pcrec's tables are
pinned at one Unicode version and **no libpcre2 this project can reach is at
the same one** — measured 2026-09-06, the Linux reference is 10.46 / Unicode
16.0.0 (the pin), Homebrew on the Mac is 10.48 / 17.0.0, and the library the
suite's own dlopen shim actually RESOLVES on the Mac is macOS's system
libpcre2 10.42 / **14.0.0** (`upstream_issues.md` U15(b)). Demanding exact
agreement would make this suite report the environment rather than the code.

So: exact agreement when the versions match, and otherwise every disagreement
must be EXPLAINED — the differing code point must be unassigned on one side or
the other (both sides' own `\p{Cn}` line, out of the same sweep, so the rule is
symmetric and needs no version number), or appear in one of two small NAMED
exception lists. Neither list is an escape hatch: `RECLASSIFIED` costs a line
naming a specific code point, and `PCRE2_SEMANTIC_DRIFT` bounds its residue
INSIDE properties pcrec's own sweep reports in the same run, so a table bug
outside that set still fails and names its addresses.

Measured at landing: **byte 14/0 with ZERO code points attributed to drift;
utf8 14/0 with 62,121 attributed and none unexplained**, against libpcre2
10.42 / Unicode 14.0.0.

## What is NOT here

**Refusals.** Which module a diagnostic promises is `tests/reject/`'s, for
this tree's standing reason — a `perr` block asserts only that compilation
failed. The gate-open uprops wordings are pinned there (`reject_gated
unicode-props`, twelve rows).

**The name axis against a generated space.** That is PC-3's
(`tests/registry/pcre2_check.c`): the closed-gate shape differential and, since
this stage, `check_gated_uprops_space`, which asserts pcrec never ACCEPTS a
property name libpcre2 rejects.

**Six patterns that do not compile under `utf8` at default axes.** They are
`tests/known_fail/k53_uprops_oversize.rxt` and `docs/dev/known_issues.md` K53
— an engine issue (an OPTIONAL machine's bytes refusing patterns that compile
without it), not a `\p` one.

Maintenance: update this file when a section is added or its argument changes;
re-measure the two arms' figures from a run rather than reading them here.
