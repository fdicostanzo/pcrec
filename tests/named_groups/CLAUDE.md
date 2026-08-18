# tests/named_groups — module `named-groups` corpus ([M6.3])

Oracle-verified behaviour of the constructs module `named-groups` PRODUCES:
the three declaring spellings `(?<name>...)` `(?'name'...)` `(?P<name>...)`,
their numbering (identical to a plain `(` group's opening-paren-order rule,
including the `(?n)` divergence — a named group captures even when `(?n)`
turns numbering off for plain groups), and the two compile-time name-syntax
refusals a `.rxt` block CAN express (duplicate name; leading digit).

## Files

- **named_groups.rxt** — the corpus. Every block carries `features
  named-groups` (this module is not in the bare-default `std1` set). Group
  spans are asserted with `g`, not `gp`: this module always forces the VM
  (a named group's AST is an ordinary `A_CAP` node, so
  `src/opt/select_engine.c`'s pre-existing generic capture-forcing rule
  selects the VM whenever captures are wanted at all — see
  `src/parse/mod_named_groups.c`'s own header), so `RX_NCAPS` already
  covers every slot these patterns declare; there is no pending-VM half
  the way tests/captures/basic.rxt has one.

## Oracle split

python3 `re` speaks only `(?P<name>...)`. The `(?P<name>...)` blocks are
therefore checked LIVE by `verify_rxt.py` on every run, same as any other
python-verifiable case. The `(?<name>...)` and `(?'name'...)` blocks carry
`# pcre2-only` and were verified by TRANSLATING the pattern text to the
identical `(?P<name>...)` spelling and running THAT through python `re` —
a mechanical, semantics-preserving translation, because all three PCRE2
spellings are the same construct differing only in delimiter (never in
what they match or how groups number), which is exactly the fact
`mod_named_groups.c`'s single shared port establishes by construction: one
producer, three registry rows, dispatched only on which closing delimiter
to look for. See `docs/dev/upstream_issues.md`'s U10 for the general rule
this exclusion follows and a worked example of the translation.

`(?n)`'s interaction with named-group numbering is ALSO `# pcre2-only` —
python's `re` has no `(?n)` construct at all (`re.error: unknown extension
?n`), so there is no translation available for that one cell. Its oracle is
`tests/probes/probe_named_groups.c` step 9, measured directly against
libpcre2 10.46 (`(?n)(a)(?P<x>b)` has `capturecount=1, namecount=1` — the
plain group gets no number at all and the named group becomes group 1, not
group 2).

Duplicate-name and leading-digit-name refusals are, perhaps surprisingly,
NOT `# pcre2-only`: python `re` independently enforces both rules on its
own named-group grammar (measured: `redefinition of group name` and `bad
character in group name` respectively), so these two `perr` blocks are
checked live. The one syntax boundary python does NOT enforce — the
128-byte maximum name length (PCRE2 error 148; python has no such ceiling)
— is NOT in this corpus at all: a `.rxt` `perr` block has no attribution
channel (it asserts only THAT a pattern refuses, never WHY, and a `.rxt`
block also cannot assert an ACCEPTING boundary's neighbour the way a
tests/reject/ pin's `reject`/`accept`-adjacent-cell pair can), so the
128-accepts/129-refuses pair lives in tests/reject/'s gated pins instead —
see its own header note on this module's four rows there.

## What tests/reject/ carries instead (not duplicated here)

- The bare-default refusal (`(?<name>...)` etc. without `--features
  named-groups`) — every module's default-off state is tests/reject/'s
  job, never a `.rxt` `perr` block (which cannot assert the module NAME in
  the diagnostic, only that compilation failed).
- The 128-accepts/129-refuses name-length boundary (python has no
  matching ceiling to co-verify the refusing half against, and a `.rxt`
  block cannot pin an attribution anyway).
- The BOUNDARY proof that backreference-by-name spellings (`\k<n>`
  `(?P=n)`) and `(?J)`/DUPNAMES both keep refusing once named-groups is
  enabled — a `.rxt` `perr` block proves a pattern refuses, never WHICH
  OTHER module's name is in the diagnostic, so this is tier-2 attribution
  and belongs in tests/reject/'s gated pins.

## d27/ — the blinded acceptance corpus

Written by a D27-blinded author (cell; allowlist docs/testing.md +
docs/spec/match_api.md + a prebuilt binary — no src/, no tests/) from
PCRE2's measured semantics BEFORE the module landed, and run against the
implementation for the first time at merge review: **83/0**. Five `.rxt`
files (spellings, name_syntax, duplicates, numbering_capture,
case_sensitivity — 41 blocks, 15 `perr`, 42 `g` assertions) that ride
`make test` through the harness's recursive `tests/` sweep like any other
corpus. `oracle.py` is the author's standalone python3 re-derivation of
every expectation (run it from d27/ to re-verify; it translates the
non-python spellings to `(?P<name>...)` and documents the two
`# pcre2-only` rows it cannot check — the 129-char refusal and the
non-ASCII-name refusal, both manager-verified against libpcre2 10.46,
2026-08-18). `README.md` is the author's methodology record, including
provenance for the corrected 128-unit length cap. These files are the
module's acceptance record — extend the main corpus above for new cells
rather than editing d27/'s, which stay as authored.

Maintenance: update this file when the corpus's file list or oracle split
changes.
