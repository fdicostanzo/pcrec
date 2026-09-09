# tests/uprops — module `unicode-props`, the checks a `.rxt` file cannot make

[M5.0] stages 3 and 5. `make test-uprops` (the `byte` arm, part of
`make test`); `make test-uprops-utf8` (the whole code-point space, opt-in).

The module's ANSWERS live in two corpus files: `tests/utf8/
axis04_p_categories.rxt` — the D27-blinded corpus, 136 blocks / 462 cases,
promoted at stage 3 from the oracle answers its author carried in each block's
comment — and `tests/utf8/axis12_scripts.rxt`, stage 5's, whose expectations
are the 10.46 REFERENCE's own answers rather than this box's. This directory
is everything those corpora structurally cannot express.

## Files

- **run_uprops_tests.sh** — four sections, and the reason there are four is
  that each sees something none of the others can. Read its own header for
  the per-section argument; the summary is below.
- **uprops_oracle.c** — the libpcre2 side, through the shared binding
  (`tests/fuzz/pcre2_abi.h`, direct-linked since [ORACLE-LINK]/D98,
  2026-09-09), so a clone without libpcre2 SKIPS loudly at BUILD time
  (`run_uprops_tests.sh` probes `tests/lib/resolve_pcre2.sh` before
  attempting the compile) rather than failing to load at runtime. Also the
  VERSION REPORTER the drift policy turns on.
- **uprops_sweep.c** — the pcrec side, compiled once per property against
  that property's own emitted artifact.
- **uprops_compare.py** — the comparator, and the ONE place the
  Unicode-version drift policy is written down.
- **uprops_names.py** — [M5.0] stage 5: §2's PROMISE SIDE, re-derived from the
  vendored UCD and compared against the shipped table's rows in BOTH
  directions. It exists because the stage-3 shape — a hand-written list of
  names — does not survive 171 script values in four spellings across three
  namespaces; its own header states what deriving from the source cannot
  close, and which check does.

## The four sections

**§1 the generated table is not stale.** `third_party/ucd-16.0.0/generate.py
--check` re-derives `src/parse/uprops_tables.inc` from the vendored UCD.
`cls_bits.inc`'s "never hand-edited" banner made mechanical.

**§2 the shipped name set, PROMISE SIDE, never read from the generated
table.** The 45 general-category names stay a HAND-WRITTEN list (three of them
are PCRE2 inventions with no UCD file to read them from); the 171 SCRIPT
values are re-derived from the vendored `PropertyValueAliases.txt` by
`uprops_names.py`, which then requires SET EQUALITY with the `.inc`'s own
rows in both directions — a name the generator dropped and a row nobody
promised each fail, naming themselves. Every promised name is then COMPILED,
scripts in all three namespaces, because a row in the table is not the same
claim as a construct that builds.

That half is derived from the generator's own INPUT, and the honest limit is
stated where it is enforced: it cannot see a name PCRE2 has that the UCD does
not. PC-3's `check_gated_uprops_space` is where that is asked, by sweeping
pcrec's table and putting every name to the LIVE oracle.

**§3 the membership differential.** Every shipped property, both encodings,
the **whole code-point space**, pcrec's own emitted artifacts against
libpcre2. It is affordable at that resolution because neither side calls the
matcher per code point: both do ONE find-all pass over a subject that is every
code point in order, so there is no sampling rule for a bug to hide behind.

**The two arms' script POPULATIONS differ, and the split is measured.** Both
namespaces of a script (`\p{X}` and `\p{sc=X}`) are swept, because they are
different SETS on 151 of the 171 values. The utf8 arm sweeps every value; the
byte arm sweeps the SEVENTEEN whose set is non-empty under the Latin-1 clamp
plus a named empty CONTROL, since the other 154 would be empty-versus-empty
comparisons costing `make test` minutes for one fact — and `uprops_names.py`
asserts, in both directions, that those seventeen really are the scripts with
a low code point, so the list cannot silently stop being right. Fifteen of the
seventeen are there only through Script_Extensions: U+00B7 MIDDLE DOT carries
a fifteen-script scx list.

**§4 the oracle-free semantic invariants.** `\P{X}` is the complement of
`\p{X}`, `\p{^X}` is `\P{X}`, `\P{^X}` is `\p{X}`, `[^\p{X}]` agrees with
`\P{X}`, and under `-i` `\p{Lu}`/`\p{Ll}`/`\p{Lt}` are `\p{L&}` while every
other property — including every script — is unchanged. Stage 5 added the
SPELLING identities (`\p{X}` == `\p{scx=X}`, `Script=` == `sc=`, `:` == `=`,
the four-letter alias == the long name) and, beside them, the one cell in this
directory that is required to DISAGREE for an interesting reason:
`\p{sc=Greek}` must NOT equal `\p{Greek}`. An implementation that read
`Scripts.txt` and wired all three namespaces to it passes every other cell in
this file and fails that one. These hold at EVERY Unicode version, so they are
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
16.0.0 (the pin), Homebrew on the Mac is 10.48 / 17.0.0. **[ORACLE-LINK]
(D98, 2026-09-09) retired the dlopen shim this paragraph used to describe a
THIRD row for** — the Mac oracle used to be whatever the dlopen candidate
list happened to resolve (macOS's own system libpcre2, 10.42 / **14.0.0**,
`upstream_issues.md` U15(b)), a library nobody's toolchain otherwise saw;
direct linking makes the Mac oracle the SAME 10.48/17.0.0 the header/pkg-
config toolchain already names, so there are two rows now, not three.
Demanding exact agreement would make this suite report the environment
rather than the code.

So: exact agreement when the versions match, and otherwise every disagreement
must be EXPLAINED — the differing code point must be unassigned on one side or
the other (both sides' own `\p{Cn}` line, out of the same sweep, so the rule is
symmetric and needs no version number), or appear in one of two small NAMED
exception lists. Neither list is an escape hatch: `RECLASSIFIED` costs a line
naming a specific code point, and `PCRE2_SEMANTIC_DRIFT` bounds its residue
INSIDE properties pcrec's own sweep reports in the same run, so a table bug
outside that set still fails and names its addresses.

Stage 5 widened the policy in two places, both because SCRIPTS drift where
categories do not. `RECLASSIFIED`'s sentence moved from "general category" to
"property value" and gained seventeen entries — Unicode revises the
Script_Extensions of ALREADY-ASSIGNED code points between versions, so they
sit in neither side's `Cn` and the symmetric budget cannot reach them; the
drift runs in both directions at once here, one entry (U+00B7 MIDDLE DOT)
against the OLDER oracle and sixteen combining marks against the NEWER one.
And a whole NAME the oracle does not have is now excusable, but only when
every code point pcrec attributes to it is unassigned on the oracle's side —
a name pcrec invented still fails, naming its addresses.

Measured at stage 3's landing: **byte 14/0 with ZERO code points attributed to
drift; utf8 14/0 with 62,121 attributed and none unexplained**, against
libpcre2 10.42 / Unicode 14.0.0 (the pre-[ORACLE-LINK] dlopen shim's resolved
library on that box). Re-measured post-[ORACLE-LINK] (2026-09-09, direct
linking, this box's real Homebrew 10.48 / Unicode 17.0.0): `byte` arm **91
properties compared, 0 code points attributed to drift** — still clean, on a
materially different oracle. Re-measure from a run rather than reading
these here.

## What is NOT here

**Refusals.** Which module a diagnostic promises is `tests/reject/`'s, for
this tree's standing reason — a `perr` block asserts only that compilation
failed. The gate-open uprops wordings are pinned there (`reject_gated
unicode-props`, twelve rows).

**The name axis against a generated space.** That is PC-3's
(`tests/registry/pcre2_check.c`): the closed-gate shape differential, and
`check_gated_uprops_space`, which asserts pcrec never ACCEPTS a property name
libpcre2 rejects — since stage 5 by sweeping EVERY name pcrec's own table
holds (1,053 across the three namespaces) rather than a hand-written list, and
with a drift rule of its own, since Unicode ADDS scripts and an older oracle
genuinely does not have `\p{Kawi}`.

**The patterns that do not compile under `utf8` at default axes.** They are
`tests/known_fail/k53_uprops_oversize.rxt` and `docs/dev/known_issues.md` K53
— an engine issue (an OPTIONAL machine's bytes refusing patterns that compile
without it), not a `\p` one. Six at stage 3; stage 5 added four blocks and
the population is smaller than its own shape suggests — of 684 script
patterns measured at default axes, exactly two SETS refuse, and they are
`\p{Unknown}` under its four spellings.

Maintenance: update this file when a section is added or its argument changes;
re-measure the two arms' figures from a run rather than reading them here.
