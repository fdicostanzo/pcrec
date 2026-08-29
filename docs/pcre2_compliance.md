# PCRE2 syntax compliance — anticipated and actual

Reference: <https://www.pcre.org/current/doc/html/pcre2syntax.html> (the syntax
quick reference; section names and order below follow it). DFA-feasibility
judgements additionally draw on
<https://www.pcre.org/current/doc/html/pcre2matching.html>, which documents what
PCRE2's OWN non-backtracking matcher (`pcre2_dfa_match`) can and cannot do —
useful prior art, since pcrec is also non-backtracking by construction.

**Last surveyed: 2026-08-09** against pcrec at `ddb73a2`+ and libpcre2 10.46.
**Last refreshed: 2026-08-22** ([M6.5.2], module `backrefs`) — components 1
and 3 regenerated and reconciled; component 2 (the independent PCRE2-side
survey) is UNCHANGED, because no PCRE2 construct appeared or moved: what
changed is which of them pcrec compiles.
This is a living document; see "Keeping this current" at the end.

**This page is three components of DIFFERENT provenance, held in checked
tension ([DOC-DRV], 2026-08-21).** Ruled by Frank, carried by the
`compliance-refresh` skill:

1. **Generated facts** — the "Registry construct index" at the end of this
   file, printed by `pcrec --list-syntax` and never hand-edited (SR-4,
   D65). Cannot drift from the compiler because it is the compiler that
   writes it.
2. **The independent survey** — every section's `syntax | status |
   becomes` table above, hand-maintained from PCRE2's own documentation.
   Deliberately NOT generated from the registry: its value is answering
   "what does PCRE2 have that pcrec's registry doesn't even list", and
   deriving it from the registry would certify completeness from the
   thing being audited.
3. **Keyed annotations** — the measurements and judgment that used to sit
   inline in each row's notes column (OK-LIMITED qualifiers, oracle
   divergences, K-list caveats, D26 tiers, deferral analysis) now live
   construct-keyed in `docs/pcre2_compliance_annotations.txt` and render
   back into this page as the small `<!-- BEGIN GENERATED ANNOTATIONS:
   ... -->` block after each section's table — `make test`
   (`tests/registry/compliance_section.py --check-annotations`) fails if a
   key names a construct that no longer exists or if the rendered text
   has drifted from the store, so a wave landing does not leave a stale
   claim sitting unnoticed the way it did before this restructure (three
   recorded instances in [M6.2] alone — see docs/dev/plan.md's [DOC-DRV]
   row).

Components 1 and 2 are independently derived and checked against each
other (`compliance_section.py --tension`, informational); component 3 is
checked for staleness against component 1's live construct list. Edit the
survey tables directly; edit annotations in the `.txt` store and re-run
`--write-annotations`; never hand-edit inside a generated marker.

## What the statuses mean

Frank asked for compliant / mostly compliant / anticipated compliance /
anticipated non-compliance / proven non-compliance. Two distinctions turned out
to matter enough to split those:

- **verified vs believed.** "It works" and "it works and an oracle agrees" are
  different claims, and this project has been burned by the second being
  assumed from the first.
- **rejected cleanly vs miscompiled.** The project mandate is that an
  unsupported construct "must fail with a clean `requires module 'X'` error,
  never miscompile". A clean rejection is a DESIGNED state, not a gap, and it
  deserves its own status rather than being lumped in with non-compliance.

Each row carries TWO values, because mixing them is what made the first draft
inconsistent (some rows said `REJECTED → PLANNED`, others buried the trajectory
in prose). `status` is what is true TODAY — one value, greppable. `becomes` is
the intended end state, or `—` when there is no plan.

| status (today) | meaning |
|---|---|
| `OK` | Supported, exercised by the .rxt corpus, cross-verified against an oracle |
| `OK-LIMITED` | Supported, correct within a limit stated in the row — and the row must name the limit's KIND: a RESOURCE cap (correct until a measured size, then a clean failure), or a CAPABILITY not yet built (part of the construct's contract unimplemented). A speed-only caveat is not a limit; it stays `OK` with the caveat in the note (DOC-1, 2026-08-11 — the value had accreted three unrelated meanings) |
| `OK-GATED` | Built and oracle-verified (corpus + PC-4's 62,872-cell live differential), but compiled ONLY under an explicit `--features` naming it (the module itself, or a named set that includes it) — NOT reachable via the bare default. Added 2026-08-12 when module `classes` shipped the first producers, when the bare default was still empty; **as of [STD1b] (`ab7592d`, 2026-08-13, D37) the bare default maps to the frozen named set `std1` = {`classes`, `modifiers`}**, so those two modules' rows graduated to plain `OK` — see the Headline. `OK-GATED` remains the correct status for a built module OUTSIDE the current bare-default set (e.g. a future graduate whose named set has not yet become the bare-default mapping per D37's announced-boundary rule); `--features none` still refuses every gated construct with the module name exactly as `REJECTED` describes |
| `REJECTED` | Not supported. Exits 1 with `requires module 'X'`, writes no output, never miscompiles. Pinned construct-by-construct by `tests/reject/` |
| `AGREES-REJECT` | PCRE2 rejects it too, and pcrec rejects it the same way. Refusing the pattern IS compliance here — not a gap |
| `OUT-OF-SCOPE` | Deliberately excluded, with the reason |
| `DIVERGENCE` | An OPEN measured difference from libpcre2. Currently none: the two ever found were fixed on 2026-08-09 and their rows say so |

| becomes | meaning |
|---|---|
| `—` | no plan; the status is the end state. A row's note may still record a revisit TRIGGER — a condition under which the question reopens — which is not a plan and does not change the value (DOC-1, 2026-08-11: three OUT-OF-SCOPE rows carry such triggers, and the column and note were read as contradicting) |
| `PLANNED` | a named module/milestone owns it, no known architectural obstacle |
| `PLANNED-HARD` | owned, but the architecture makes it genuinely difficult — needs the M4 VM engine, or fights the D7 two-pass DFA design. Reason per row |
| `never` | generated index only: the registry's `ROADMAP_NEVER` — real PCRE2 syntax pcrec deliberately excludes, which no module will ever implement, and whose diagnostic says so instead of promising one (K14). Synonymous with a hand-table `OUT-OF-SCOPE`/`—` pairing, rendered from the row so it cannot drift (DOC-1: the value was in use, undefined here) |

Roughly against the vocabulary Frank asked for: `OK` = compliant;
`OK-LIMITED` = mostly compliant; `becomes: PLANNED` = anticipate compliance;
`becomes: PLANNED-HARD` = anticipate compliance with risk; `OUT-OF-SCOPE` =
anticipate permanent non-compliance, by choice; `DIVERGENCE` = proven
non-compliance. `REJECTED` and `AGREES-REJECT` have no equivalent in that list
and are the reason it needed splitting — a clean refusal is a designed state.

**These two columns are the prototype of the registry's `status`/`becomes`
fields (D24).** The registry landed (SR-1) and SR-4 connected it to this file —
but not by rendering the whole document, which was the original plan and would
have been a bad trade. What is generated is the **construct index** at the end:
one row per registry row, printed by the compiler itself, so the INVENTORY
cannot drift. What stays hand-written is the SURVEY — the `syntax | status |
becomes` verdict in each section's table above, which makes this a survey
rather than a listing, and every row about BASE syntax, which the registry
deliberately does not describe. The DFA-feasibility judgements, the `PLANNED`
vs `PLANNED-HARD` reasoning, the divergence post-mortems and the rest of the
analysis that used to sit in each row's notes column are now the KEYED
ANNOTATIONS ([DOC-DRV], see this file's intro above) —
`docs/pcre2_compliance_annotations.txt`, rendered back per section.

Four `make test` checks hold the seams (`tests/registry/compliance_section.py`):
the generated index must match `pcrec --list-syntax` (`--check`); every module
named in the hand-written prose must be a module the registry actually knows
(`--names`) — the one that catches the realistic component-2 failure, a module
renamed in `registry.c` leaving this document confidently describing something
that no longer exists; every annotation key must name a live construct and the
page's annotation blocks must match the store (`--check-annotations`) — the
component-3 equivalent, and the one that retires the recurring failure this
restructure exists for (a construct's annotation going stale after a wave
lands with nothing to notice); and the checked-tension report between the
survey and the registry (`--tension`, informational).

## Headline

pcrec implements a deliberately small base tier and rejects the rest by design.
Of PCRE2's syntax surface:

- The base tier (literals, `.`, classes, ranges, quantifiers incl. lazy,
  alternation, groups, `^`, `$`, the character escapes) is `OK`, with 876
  corpus cases at 100% oracle agreement (844 of them python-verified; the rest
  are `# pcre2-only` blocks checked against libpcre2 directly).
- Modules `classes` and `modifiers` shipped `OK-GATED` on 2026-08-12 (built
  and oracle-verified, compiled only under `--features classes` or
  `--features modifiers`); as of [STD1b] (`ab7592d`, 2026-08-13, D37) both
  are `OK` — the bare default
  now maps to the frozen named set `std1` = {`classes`, `modifiers`}, so a
  bare `pcrec` compiles their constructs with no flag needed. `--features
  none` is the only invocation that still refuses them, with the module name.
- Six further modules have shipped `OK-GATED` since — built and
  oracle-verified, but compiled ONLY under an explicit `--features` naming
  them, and refused by name under the bare default: `assertions` (`\b \B \G`
  and `\K`, [M6.2], complete 2026-08-19), `named-groups` ([M6.3],
  2026-08-18), `atomic-groups` (`(?>...)` and the possessive quantifier
  suffixes, [M6.4.2], 2026-08-22), `backrefs` (every backreference
  spelling, PCRE2's octal disambiguation at the atom position, and
  `(?J)`/DUPNAMES — [M6.5.2], 2026-08-22) and `lookaround` (SIX constructs
  in EIGHTEEN spellings — `(?=` `(?!` `(?<=` `(?<!` `(?*` `(?<*` and the
  twelve `(*` alpha spellings — [M6.6.2], 2026-08-24). **`lookaround` is the
  first module to move a survey row from `REJECTED` to `OK-LIMITED`**: the
  lookbehind pair ships fixed-width-PER-BRANCH, which is wider than
  "fixed-length lookbehind" and narrower than PCRE2, and the row names the
  limit's kind. It also moved the twelve alpha spellings from module `verbs`
  — the wrong module, promised for a year of sessions by a `(*` doorway whose
  ONE row answered for every name in both of PCRE2's verb tables — and gave
  each of them an index row of its own, folded into its primary's family line
  (D71 item 3). **`recursion` is the SIXTH** (subroutine calls and recursion
  in every spelling, plus `(?(DEFINE)` — [DD-14], 2026-08-24): its survey row
  reads `OK-LIMITED` and names TWO limits, a CAPABILITY one (VM engine only —
  `--engine=dfa` refuses by name, and the language a call generates is
  genuinely not regular) and a RESOURCE one (every call is a resume frame that
  outlives its return, so depth is bounded by the artifact's frame capacity
  and a runaway gives up cleanly). **That row read `REJECTED` from the day
  waves B+C and D landed until wave F's compliance refresh caught it** — the
  same class of staleness the `\b \B \G` row above records, found by the
  ritual rather than by a reader. Wave F also added NINE index rows for
  spellings the compiler ALREADY handled and no surface named — the
  multi-digit calls `(?10)`/`(?-10)`, the `(?+N)` siblings, `\g<0>`/`\g'0'`
  and the leading-zero absolutes — and collapsed the module's 26 one-line
  entries into NINE family lines (D71 item 3's index layer, second customer).
  **`backrefs` moved THREE survey
  rows and fourteen index rows in one landing**: `\0dd, \ddd as an ATOM` and the bundled backreference row in
  their own sections, and `(?J) dup names` in Option setting — whose owning
  module moved from `named-groups` to `backrefs` with it (ASK-1), the fourth
  attribution that letter has carried and the first one that is both true and
  actionable. It also ADDED two index rows born `unbuilt` (`\g<1>`, `\g'1'`,
  module `recursion`), splitting a doorway that carried two different
  constructs under one row. **All three `assertions` rows read plain `OK`
  from 2026-08-19 until 2026-08-22, which this page's own vocabulary
  reserves for constructs a bare `pcrec` compiles**: `\A \Z \z` at
  `211c5da` (wave A) and `\b \B \G` + `\K` at `f6d5430` (wave E) — and
  `f6d5430` was itself correcting a two-wave-stale `REJECTED` on
  `\b \B \G`, overshooting the gated value on the way past it. All three
  now read `OK-GATED`, verified by running a bare `pcrec` against `\Aa`,
  `a\Z`, `a\z`, `a\b`, `a\B` and `a\K` and reading the refusal each
  time — as does `(?m)` multiline in Option setting, a FOURTH row of the
  same class: the letter is produced by `modifiers` (default-on) but
  ATTRIBUTED to `assertions`, so a bare `(?m)^a` answers "inline option
  'm' (multiline) requires module 'assertions'" while its neighbours
  `(?s)` and `(?x)` compile — measured the same way, all three in one
  pass. Their own annotations said "behind the gate" throughout — the
  status column and the annotation had been contradicting each other for
  three days, which is the pairing `--tension` does not check.
- Everything outside those modules is `REJECTED` — measured live at
  [M6.4.2] (2026-08-22, module `atomic-groups`) from
  `tests/reject/run_reject_tests.sh`'s own summary,
  not transcribed: **279** hand-written rows individually assert exit 1 and
  the right diagnostic (most name a module; some — the base-grammar brace
  errors K5/K6/K8, the verb doorway's outcomes, the `unknown escape` pins —
  name a PCRE2-flavoured wording instead, and offsets are pinned where a
  message alone cannot distinguish sites), **99** accept-controls proving the
  table cannot pass by rejecting everything, **65** `reject_gated` pins
  asserting a refusal that holds only under a NON-default `--features` spec
  — 40 of them `--features none`, pinning the pre-[STD1b] bare behaviour
  verbatim now that the bare default is `std1` (D37), and 25 GATE-OPEN pins,
  where the construct's own module is enabled and the pattern is still
  refused or still gets a particular diagnostic (`a*++` under `--features
  atomic-groups`; `(?m:a$)` under `--features modifiers`) — the split
  counted from the same run (this sentence described all of them as the
  `--features none` half until 2026-08-22, which was true of well under
  two-thirds) — and (SR-4) **103**
  further checks that iterate `pcrec --list-syntax` so no registry row can
  escape a probe (`tests/reject/`) — **547** checks passing, **0**
  known-wrong. (The previous figures, 274/99/55/99 = **528**, were measured
  at `ab7592d`+ on 2026-08-13 and had been overtaken by every wave since;
  the same "read them from a run" rule applies to the values above.)
  **This paragraph previously cited 144/45/66: those figures
  were already stale independent of the STD1b flip — `tests/reject/CLAUDE.md`'s
  own count history records several unrelated intermediate values this
  survey never caught up to (the file's own maintenance note: "read them
  from a run, never from here"). What is written above is a fresh whole-suite
  measurement, not a same-category update of the old numbers.** The two
  layers (hand-written and iterated) answer different questions and neither
  subsumes the other: iteration guarantees coverage but reads the same table
  the parser renders from, so it cannot see a WRONG module name — measured, by
  changing `\d`'s row to `misc`, which the hand-written rows catch twice and
  iteration does not catch at all.
- **Two proven divergences have been found, both fixed:** `\v` (Character
  types) and POSIX collating elements (Character classes). Both were silent —
  pcrec compiled something PCRE2 does not — and in both cases python `re`
  agreed with pcrec, so the base-tier oracle was blind to them.

The single most useful thing this survey produced was not the table. It was
finding that the mandate's central guarantee had no test at all (see "How this
survey earned its keep").

---

## Quoting

| syntax | status | becomes |
|---|---|---|
| `\` + non-alphanumeric | `OK` | — |
| `\Q...\E` | `REJECTED` | `PLANNED` |

<!-- BEGIN GENERATED ANNOTATIONS: quoting -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:quoting-backslash-nonalnum`**

Escaped punctuation is a literal; corpus-covered.

**`\Q`**

Pure front-end lexing; `PLANNED`-easy whenever wanted.

<!-- END GENERATED -->

## Braced items

| syntax | status | becomes |
|---|---|---|
| whitespace inside `{ }` in `\g{2}` etc. | `REJECTED` | — |
| `\u{...}` (ALT_BSUX) | `OUT-OF-SCOPE` | — |

<!-- BEGIN GENERATED ANNOTATIONS: braced-items -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:braced-whitespace-scope`**

Reached only via constructs that are themselves rejected. **This row's
scope was too narrow and its dismissal was wrong for the case that
mattered** (R7): the REPEAT quantifier is base-tier and very much reached,
and pcrec silently compiled `a{ 1}` as literal text until K8. See the
Quantifiers section.

**`base:alt-bsux-u-brace`**

An ECMAScript-compatibility spelling gated on a PCRE2 option pcrec does not
model.

<!-- END GENERATED -->

## Escaped characters

| syntax | status | becomes |
|---|---|---|
| `\a` `\e` `\f` `\n` `\r` `\t` | `OK` | — |
| `\xhh` | `OK` | — |
| `\x{hh..}` | `REJECTED` | — |
| `\cx` | `REJECTED` | — |
| `\0dd`, `\ddd` as an ATOM | `OK-GATED` | — |
| `\0dd`..`\ddd`, `\8` `\9` `\g` `\k` INSIDE A CLASS | `OK` | — |
| `\o{ddd..}` | `REJECTED` | — |
| `\N{U+hh..}` | `REJECTED` | — |
| `\U`, `\uhhhh` (ALT_BSUX) | `OUT-OF-SCOPE` | — |

<!-- BEGIN GENERATED ANNOTATIONS: escaped-characters -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:escapes-control-letters`**

Each verified byte-for-byte against libpcre2 during this survey.

**`base:hex-escape-xhh`**

1–2 hex digits; `digits missing after \x` matches PCRE2 error 178.

**`base:hex-escape-braced`**

Module `unicode-props`.

**`\cX`**

Trivially implementable; base tier simply does not include it.

**`\0`** (2026-08-22)

module `backrefs` — PCRE2 resolves octal-vs-backreference by context, so
they share an owner. SHIPPED 2026-08-22 ([M6.5.2]): `\0` is ALWAYS octal
(at most three digits COUNTING the leading zero, so `\0377` is `\037` then a
literal `'7'`) and can never be a backreference, because there is no group 0
to address. It keeps its `backrefs` gate — moving it to the base grammar
would be a compatibility change to the BASE tier made as a side effect of a
module landing, and no build that accepts `\0` today stops accepting it. Its
row is the one member of the digit family that is ANY_ENGINE, and the
character node it produces is deliberately NOT stamped with the row: `(a)\10`
is the octal byte 0x08 and compiles to a pure DFA, while `(a)\1` refuses
`--engine=dfa` by name — asserted in both directions.

**`base:class-escape-fallbacks`** (2026-08-11)

**FIX-3 (K13), 2026-08-11.** A backreference is impossible inside a class,
so PCRE2 falls back and pcrec now agrees: `\0`..`\7` open an octal escape
(up to three octal digits; above `\377` it is PCRE2 error 151, wording and
offset reproduced), `\8` `\9` `\g` `\k` are the LITERAL characters (the
complete fallback set over all 62 `[\c]` probes), tails re-enter as members
(`[\k<n>]` matches k `<` n `>`), and decoded escapes are ordinary range
endpoints (`[0-\k]`, `[\1-\7]`). Measured cell-by-cell against libpcre2
10.46 — tests/probes/probe_fix3.c, 41 cells, zero disagreements; pinned by
tests/base/class_escape_fallbacks.rxt (127 cases) and the `[\400]`/`[\377]`
boundary rows in tests/reject/. Until this change all twelve answered
"requires module 'backrefs'" here — the K13 over-promise.

**`\N{U+0041}`** (2026-08-11)

The registry's answer is authoritative here (this row said `classes` until
DOC-1, 2026-08-11, contradicting the generated index below; the pointer it
gave to a "note under Character types" pointed at a note that did not
exist — it does now).

**`base:alt-bsux-U-uhhhh`**

Option-gated compatibility spellings.

<!-- END GENERATED -->

## Character types

| syntax | status | becomes |
|---|---|---|
| `.` | `OK` | — |
| `\d \D \s \S \w \W \h \H \V \N` | `OK` | — |
| `\v` | `REJECTED` | `PLANNED` |
| `\C` | `REJECTED` | `PLANNED` |
| `\p{..}` `\P{..}` | `REJECTED` | — |
| `\R` | `REJECTED` | `PLANNED` |
| `\X` | `REJECTED` | `PLANNED-HARD` |

<!-- BEGIN GENERATED ANNOTATIONS: character-types -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:dot`**

Excludes `\n` only, PCRE2's default. `(?s)` dotall is `OK` by default since
[STD1b] (module `modifiers`, MOD-0.5c; still refused under `--features
none`).

**`\d`** (2026-08-12)

Module `classes` SHIPPED THESE 2026-08-12 (MOD-0.3): both positions,
negation as the probe-asserted complement. Default-on since [STD1b]
(`ab7592d`, 2026-08-13): `classes` is in the bare-default named set `std1`
(D37), so a bare `pcrec` compiles these with no flag; `--features none`
still refuses with the module name, and `--features classes`/`--features
std1` are unchanged. Oracles: tests/classes/, PC-4. **The `\N` spelling
clash** (the note the Escaped-characters table references): `\N` here is
the BARE form only — "any character except newline", a class-shaped
predicate owned by `classes`. `\N{U+hh..}` is a DIFFERENT construct (a
code point by number, module `unicode-props`; K10 recorded the
`[\N{U+41}]` class-position divergence, FIXED 2026-08-12 by MOD-0.6 — see
docs/dev/known_issues.md K10), and `\N{name}` is real PCRE2 syntax pcrec
will never implement (`never`). Three meanings on one selector byte,
resolved by the registry's tails — which is why the two `\N{` rows sit in
the registry SHORTEST-tail-first (SR-9's precedence rule).
This annotation is keyed to `\d` as the representative spelling of the
bundled prose row `\d \D \s \S \w \W \h \H \V \N`; all nine share it.

**`\v`** (2026-08-09)

**Was a proven divergence, fixed 2026-08-09.** PCRE2 defines `\v` as
vertical WHITESPACE (`0x0a 0x0b 0x0c 0x0d 0x85`, measured against libpcre2
10.46); pcrec decoded it as vertical tab `0x0B` only, inside classes as
well as outside. Now `REJECTED` to module `classes` like its negation `\V`.
It survived because python `re` also reads `\v` as `0x0B`, so the
base-tier oracle agreed with the bug — see "How this survey earned its
keep".

**`\C`**

"one code unit". In the ASCII tier that is just "any byte", i.e. trivial.
PCRE2 forbids it under its own DFA matcher in UTF modes for the reason
that will apply to us in M5.

**`\P{L}`**

Single-position predicates, so DFA-friendly; the work is Unicode tables,
not engine.
This annotation is keyed to `\P{L}` (not `\p{L}`) to avoid colliding with
the Unicode-properties section's own `\p{L}` row below; it covers the
bundled prose row `\p{..}` `\P{..}`.

**`\R`**

Not a single character — a small alternation of literal sequences (CR, LF,
CRLF), so still regular and `PLANNED`-feasible.

**`\X`**

extended grapheme cluster: variable-length, Unicode-table-driven
segmentation. Regular in principle, substantial in practice. M5 at the
earliest.

<!-- END GENERATED -->

## Unicode properties (general category, PCRE2 special, binary, script, bidi)

| syntax | status | becomes |
|---|---|---|
| `\p{L}` `\p{Lu}` … (general categories) | `REJECTED` | — |
| `\p{Xan}` `\p{Xps}` `\p{Xsp}` `\p{Xuc}` `\p{Xwd}` | `REJECTED` | — |
| `\p{<binary property>}` | `REJECTED` | — |
| `\p{scriptname}` `\p{sc:..}` `\p{scx:..}` | `REJECTED` | — |
| `\p{Bidi_Class:..}` `\p{BC:..}` | `REJECTED` | — |

All of these lower to byte-range sets over UTF-8, which APPROACH §4/§10 already
commits to. The blocker is table generation and size, not matching.

<!-- BEGIN GENERATED ANNOTATIONS: unicode-properties -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:uprops-k16-byte-census`** (2026-08-12)

**A RULED, deliberate tier-2 divergence (K16, D26; Frank, 2026-08-12):**
libpcre2 treats 164 of 256 possible `\p{...}` BODY bytes (`!"#$%`, `{|~`,
DEL, most C0 controls, every byte ≥ 0x80) as malformed the instant they
appear — error 146 at the bad byte, before the name scan continues and
regardless of the 128/48 caps — where pcrec's MOD-0.6 scanner reads past
them as ordinary name characters and refuses in its own
unknown-name/generic category at its scan-completion offset. Both engines
refuse every such pattern and the module attribution is identical, which
is what keeps this tier 2. Found by R19's engine critic
(docs/dev/reviews/2026-08-12-r19-mod06.md); recorded at
docs/dev/known_issues.md K16 with the full byte census; fix deferred to
the first `unicode-props` producer, when the scanner is remeasured anyway.
The reject pins for `\p{!}`/`\p{9}`/`\p{=}` claim pcrec's own current
behavior, not oracle agreement, until then.

**`\p{L}`**

M5.
This annotation is keyed to `\p{L}` and covers the survey's general-
category row (`\p{L}` `\p{Lu}` …); the four rows beneath it in the same
table (`\p{Xan}` etc., binary properties, script names, `Bidi_Class`) carry
no distinct content of their own — each reads only "same" in the
source prose, pointing back to this one. See the [DOC-DRV] migration
manifest: those four rows are disposition dropped-trivial, not silently
omitted.

<!-- END GENERATED -->

## Character classes

| syntax | status | becomes |
|---|---|---|
| `[...]`, `[^...]`, `[x-y]` | `OK` | — |
| `[[:alpha:]]`, `[[:^alpha:]]` and the 14 POSIX names | `OK` | — |
| `[[.ch.]]` collating elements, `[[=ch=]]` equivalence classes | `AGREES-REJECT` | — |
| `\Q...\E` inside a class | `REJECTED` | — |
| `[x&&y]`, `[x--y]`, `[x~~y]` (UTS#18 set ops) | `OK` | `PLANNED` |
| `(?[...])` Perl extended classes, `& - ^ ! +` operators | `REJECTED` | `PLANNED` |

<!-- BEGIN GENERATED ANNOTATIONS: character-classes -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:class-brackets-basic`**

corpus-covered incl. `]` first, `-` last, high bytes, out-of-order range
rejection.

**`[[:alpha:]]`** (2026-08-12)

Module `classes` SHIPPED THESE 2026-08-12 (MOD-0.3): all 14 names, both
polarities. Default-on since [STD1b] (`ab7592d`, 2026-08-13): `classes` is
in the bare-default named set `std1` (D37); `--features none` still
refuses with the module name (`[[:<:]]`/`[[:>:]]` are assertions, module
`assertions`, still refused in every configuration — not in `std1`).
Oracles: tests/classes/ (every name pinned without libpcre2 since R16),
PC-4.

**`[[.a.]]`** (2026-08-09)

**Was a proven divergence, fixed 2026-08-09.** PCRE2 does not support
these and REJECTS them ("POSIX collating elements are not supported");
pcrec silently accepted them as a class of literal `[` `.` `a` characters.
Now rejected with PCRE2's own wording, so rejecting IS compliance here.
The trigger was pinned against libpcre2 rather than guessed: `[` + `.`/`=`
opens a collating element ONLY when the matching `.]`/`=]` terminator
appears later, and a negated class suppresses it — so `[.a]`, `[.]`,
`[[.]`, `[a[.b]`, `[^.a.]` and `[a.b.]` must all still COMPILE.
Over-rejecting here would break patterns PCRE2 accepts, which is why those
six are accept-controls in `tests/reject/`. This covers both collating
elements (`[[.ch.]]`) and equivalence classes (`[[=ch=]]`); see also
`[[=a=]]`'s own (stub) annotation.

**`[[=a=]]`**

See `[[.a.]]`'s annotation — the same finding and fix cover both
collating elements and equivalence classes.

**`base:class-quoting-e`**

Module `quoting`.

**`base:class-set-ops-uts18`**

pure bitmap algebra at parse time; no engine implication at all.

**`(?[[a]])`**

same — a parser feature that produces one bitmap. Note `^` means XOR here,
not negation; a spelling trap worth a test when implemented.

<!-- END GENERATED -->

## Quantifiers

| syntax | status | becomes |
|---|---|---|
| `? * + {n} {n,m} {n,} {,m}` greedy | `OK` | — |
| `?? *? +? {n,m}? {n,}? {,m}?` lazy | `OK` | — |
| `?+ *+ ++ {n,m}+ {n,}+ {,m}+` possessive | `OK-GATED` | — |
| quantifier on `^`/`$` | `OK` | — |
| double quantifier `a**`, `a{2}{3}` | `OK` | — |
| count above 65535, `a{65536}` | `AGREES-REJECT` | — |
| `{m,n}` with nothing to quantify, `{1}` | `AGREES-REJECT` | — |
| space/tab inside `{m,n}`, `a{ 1}` | `OK` | — |
| brace diagnostic PRECEDENCE | `OK` | — |
| large bounded repeat, `a{0,65535}` | `OK-LIMITED` | `PLANNED` |

<!-- BEGIN GENERATED ANNOTATIONS: quantifiers -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:quantifiers-greedy`**

`{,m}` = `{0,m}` per PCRE2 10.43+, found by our own fuzzer.

**`base:quantifiers-lazy`**

priority subset construction preserves greedy/lazy preference (D3).

**`base:quantifiers-possessive`** (2026-08-22)

Module `atomic-groups`, SHIPPED 2026-08-22 ([M6.4.2]). Possessiveness prunes
alternatives that a priority simulation explores in parallel, so it is a real
semantic change needing explicit cut support, not a no-op — which is why the
registry gives these four rows `engines: vm` alone. That mask is ANDed over
the tree the discharge LEAVES, though, so it is not a property of the
spelling: `a*+a` and `(?:a|ab)*+c` are VM-forced and `--engine=dfa` refuses
them by name, while `a*+b` — whose cut can discard nothing, because no `a`
can also be the following `b` — is discharged and compiles on the DFA,
`--engine=dfa` included. Measured 2026-08-22 on all three, and worth stating
at this length because the shorter claim — "possessive means VM" — is false
for `a*+b`, which is the first shape anyone reaches for. All the
spellings are built, `{n}+` `{n,}+` `{,n}+` included: PCRE2 defines `X q+` as
`(?>X q)`, and pcrec desugars the suffix to that exact node at the quantifier
site in `src/parse/parse.c`, so the suffix and the group are ONE construct
here — the corpus puts each spelling beside its group twin to say so.
`--features none` (the bare default) still refuses with the module name;
`--features atomic-groups` compiles. The registry lists the four suffix rows
under kind `quant-suffix` rather than `after (?`, and they are not
quantifiable themselves: `a*?+` and `a*++` are pinned rejections in
tests/reject/. Oracles: tests/atomic_groups/possessive.rxt and the same
differential as `(?>...)`. One MEASURED oracle divergence the corpus carries
with its controls: over a two-exit body the BRACE possessive cuts at the
GROUP EXIT in PCRE2 and PER ITERATION in python `re`, so `(?:a|ab){2}+` on
"aba" is (0,3) in PCRE2 and NO MATCH in python, while `(?:a|ab)*+` on "aba"
is (0,1) in both. pcrec follows PCRE2 (D26); the block is marked
`# pcre2-only` for exactly that reason.

DEVIATION, RULED (D68, 2026-08-22): on libpcre2 10.46 a possessive or atomic
BOUNDED repeat of a GROUP preceded by a backtrack point that consumed —
`a?(?:b){0,4}+a` on "a" — reports NO MATCH, where the documented semantics,
python `re` and a hand derivation give (0,1). pcrec answers (0,1) and does not
reproduce libpcre2 here; the divergence is classified a suspected PCRE2 defect
(docs/dev/upstream_issues.md U9, three isolating controls). The cells are in
tests/atomic_groups/possessive.rxt section 9, python-verified, excluded from
the libpcre2 pass with a loud, counted marker.

**`base:quantifier-on-anchors`**

rejected as PCRE2 error 109 does; `(^)*` is accepted because a group
wrapper makes it quantifiable, matching PCRE2.

**`base:double-quantifier`**

rejected, corpus-covered. Note the WORDING differs on `a{1}{2}`: PCRE2
says error 109, pcrec says "multiple quantifiers on the same item". Same
verdict, and the offset agrees.

**`base:quantifier-count-overflow`** (2026-08-10)

PCRE2 error 105. **Was a MISCOMPILE until 2026-08-10 (K5, FIX-1)** —
silently reinterpreted as literal text, so the emitted matcher accepted a
different language than the pattern named. The overflow is judged only
once the form is CONFIRMED to be a quantifier, which is what PCRE2 does:
`a{65536x}`, `a{65536,x}` and `a{65536` all stay literal in both engines.

**`base:quantifier-nothing-to-quantify`** (2026-08-10)

PCRE2 error 109. **Was a MISCOMPILE until 2026-08-10 (K6, FIX-1)**; `*`,
`+` and `?` had always been rejected in this position and only `{` was
missed, because `try_quant` is reached from `p_rep`, i.e. after an atom.
Malformed braces (`{}`, `{,}`, `{1`, `a{`) stay literal in both engines,
and the reject suite's accept-controls pin that.

**`base:quantifier-brace-whitespace`** (2026-08-10)

PCRE2 (following Perl 5.34) skips 0x20 and 0x09 in each of the four gaps
`{`_m_`,`_n_`}`, and no other byte. **Was a MISCOMPILE until 2026-08-10
(K8)** — silently literal text, and invisible to a verdict comparison
because both engines accept in quantifier position. Whitespace never joins
digits (`a{1 2}` is literal) nor stands in for a number (`a{ }`, `a{ , }`
stay literal). Found by R7's spec critic, not by the 49 probes that
certified K5/K6.

**`base:quantifier-brace-precedence`**

measured, not assumed: in atom position PCRE2 answers 105 for `{65536}`
and 104 for `{3,1}`, not 109; and too-big beats out-of-order, so
`a{65536,1}` is 105. pcrec agrees on all three, offsets included.

**`base:quantifier-large-bounded-repeat`** (2026-08-18)

limit kind: RESOURCE cap. **K7, fixed 2026-08-18 ([M4.7b]); this row
previously made two claims that were wrong as written, corrected here.**
The BOUNDED-OPTIONAL form is correct up to the NFA size cap and refuses
above it in ~0.1 s and ~11 MB (bisected: `a{0,31999}` compiles,
`a{0,32000}` refuses; `a{0,20000}` compiles at 13 MB; `a{0,65535}` refuses
on the 131072-state NFA cap). The EXACT-COUNT form is correct to `a{9795}`
(bisected; `a{9796}` refuses) and refuses above it on the subset-element
bound (`a{65535}`: 216 MB, 0.9 s). Neither form can exhaust memory or abort
a caller any more, and a compile under a caller-set memory limit now
reports "out of memory compiling this pattern" rather than killing the
caller's process. Not a miscompile; no wrong code is emitted, and no
pattern that compiled before this fix compiles to different bytes after
it. **The two corrected claims, kept visible because the doc's own
vocabulary is what made them wrong:** (1) this row said "limit kind:
RESOURCE cap", which the table at the top of this file defines as
"correct until a measured size, THEN A CLEAN FAILURE" — the defining
property K7 was filed for not having, so the row asserted a category it
did not meet; (2) it said the process "is SIGKILLed", which was true only
with no limit set — under a caller's limit it SIGABRTed, and the
difference matters because a caller who set a limit is exactly the caller
the row was describing. A third statement, "`a{65535}` does hit the cap
cleanly", was true in verdict but reached that verdict after 2.1 GB and
12.3 s, which is not what "cleanly" means anywhere else in this document.

<!-- END GENERATED -->

## Anchors and simple assertions

| syntax | status | becomes |
|---|---|---|
| `^` | `OK` | — |
| `$` | `OK` | — |
| `\A \Z \z` | `OK-GATED` | — |
| `\b \B \G` | `OK-GATED` | — |

<!-- BEGIN GENERATED ANNOTATIONS: anchors-assertions -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:anchor-caret`** (2026-08-11)

start of subject, accepted and correct in every position (probed at class
open, mid-pattern, and per alternation branch — DOC-1, 2026-08-11, which
found the old `OK-LIMITED` stating no limit; the multiline gap it gestured
at is `$`'s too and both rows now carry it the same way). Multiline `^` is
`REJECTED` — since MOD-0.5c the gate-open answer names module `assertions`
per-letter (the MOD-0.5a ruling); the DFA-state-context design for it is
DD-6. One SPEED caveat, not a correctness limit: unanchored patterns with
`^` in some branches stay on the slower ENG_ATTEMPT engine until DD-7's
unification (D8).

**`base:anchor-dollar`**

end of subject or before a final newline — PCRE2's default. Mid-pattern
`$` is fully general via EOL-variant states.

**`\A`** (2026-08-19)

Module `assertions` SHIPPED THESE 2026-08-19 ([M6.2] wave A), behind the
gate: `--features assertions` compiles them, a bare invocation still
refuses by name (`assertions` is not in the bare-default set `std1`). `\A`
and `\Z` turned out to be EXACT ALIASES of the `^`/`$` nodes pcrec has
shipped since M1 — pcrec's own node comments are PCRE2's definitions word
for word — so they cost no engine work at all (measured, 1,008
differential cells / 0 disagreements). `\z` is genuinely stronger than `\Z`
and needed a third closure view, interned only where it differs from the
EOL view, so a `\z`-free pattern's artifact is byte-identical (gated:
tests/codegen/run_endvar_identity.sh). Oracle note: python `re` is the
WRONG oracle for `\Z` (its `\Z` is PCRE2's `\z`) — tests/assertions/
carries its own libpcre2 verifier, U11.
This annotation is keyed to `\A` and covers the bundled prose row
`\A \Z \z`.

**`\b`** (2026-08-19)

Module `assertions` SHIPPED THESE 2026-08-19 ([M6.2] waves B and D),
behind the gate, and this row was CORRECTED in the source document — it
said `REJECTED` and described the work as pending for two waves after
those waves landed. `\b`/`\B` cost a byte-equivalence-class refinement, a
bit of DFA state identity, a class-indexed accept and runtime start-state
seeding from a byte OUTSIDE the search window at `startpos > 0`
(assertions_design.md §3.8, whose reverse TERMINATION half was a
lost-match defect found by the R30 re-check). `\G` cost a third closure
bit, a second interior start-state family and a three-way start dispatch —
and did NOT need DD-4's wrap toggle, because ENG_ATTEMPT already emits the
un-self-looped shape and `\G` is `start_max = startpos`. Oracles:
tests/assertions/wordb_basic.rxt, wordb_empty_compose.rxt,
wordb_engattempt.rxt, wordb_vm.rxt (the wave B corpus, shard-split
2026-08-21 — see tests/assertions/CLAUDE.md) and gpos.rxt (the latter
`# pcre2-only` in its entirety — python has no `\G` at all, U11c).
This annotation is keyed to `\b` and covers the bundled prose row
`\b \B \G`. This is the row whose staleness (read `REJECTED` for two
waves after the module shipped) motivated the [DOC-DRV] restructure
itself — see docs/dev/plan.md's [DOC-DRV] row and the compliance-refresh
skill.

<!-- END GENERATED -->

## Reported match point setting

| syntax | status | becomes |
|---|---|---|
| `\K` | `OK-GATED` | — |

<!-- BEGIN GENERATED ANNOTATIONS: match-point -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`\K`** (2026-08-19)

Module `assertions` SHIPPED THIS 2026-08-19 ([M6.2] wave E, the module's
last construct), behind the gate. **VM-ONLY, and the old `PLANNED-HARD`
reasoning on this row was RIGHT ABOUT THE OBSTRUCTION AND WRONG ABOUT THE
SHAPE.** It said `\K` "interacts directly with the reverse machine". It
does not: `\K` changes no LANGUAGE, so `src/ir/nfa.c` lowers it to an
epsilon and the capture-erased prefilter built for `a\Kb` is the machine
`ab` builds — which is exactly what the hybrid needs, since the
prefilter's span start is then the PRE-`\K` start and is used only to
bound the search. The real obstruction is narrower: the reported position
is a property of the WINNING PATH and a subset state is a
priority-ordered SET, which does not carry one. A tagged DFA (Laurikari)
recovers exactly such positions; pcrec's is not one and this is recorded
as closed BY CHOICE rather than by mathematics (assertions_design.md
§6.1, R30 E7). PCRE2 likewise does not support `\K` in its own DFA
matcher. So a `\K` pattern is VM-forced (the second `forces_*` row in
src/opt/select_engine.c) and `--engine=dfa` REFUSES it by name rather
than silently downgrading (D44.6). The write is a trailed capture write to
group 0's start slot, so a `\K` crossed on a path that then LOSES is
undone: `(?:a\K|ax)c` on "axc" is (0,3). Oracle: tests/assertions/
kreset.rxt, `# pcre2-only` in its entirety — python has no `\K` at all and
a lookbehind is not a translation of it (U11d).

<!-- END GENERATED -->

## Alternation, capturing, atomic groups

| syntax | status | becomes |
|---|---|---|
| `a\|b` | `OK` | — |
| `(...)` | `OK-LIMITED` | — |
| `(?:...)` | `OK` | — |
| `(?<name>...)` `(?'name'...)` `(?P<name>...)` | `OK-GATED` | — |
| `(?>...)` | `OK-GATED` | — |
| `(*atomic:...)` | `REJECTED` | `PLANNED` |

<!-- BEGIN GENERATED ANNOTATIONS: alternation-capturing -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:alternation-basic`**

incl. empty branches; leftmost-first preference via priority pruning (D3).

**`base:capturing-group-limit`**

limit kind: CAPABILITY not yet built. Parses and groups correctly, but
capture SPANS are not reported — only the overall match. Captures arrive
with the M4 VM engine.

**`(?<name>a)`** (2026-08-18)

Module `named-groups`, SHIPPED 2026-08-18 ([M6.3]): all three declaring
spellings parse and capture as their group number (opening-paren order,
exactly as an unnamed group — including under `(?n)`, which suppresses a
PLAIN group's number but NOT a named one's, measured). `rx_info.groups` is
populated, sorted by NAME (strcmp, byte-exact and case-sensitive —
"name"/"NAME" are two distinct groups, even under `(?i)`, measured both
oracles) — PCRE2's own `PCRE2_INFO_NAMETABLE` is sorted the identical way,
measured directly (tests/probes/probe_named_groups.c), which is this
module's own evidence for the sort key docs/spec/match_api.md §6 had left
open (fixed only for today's ref-empty rows — see D59). A duplicate name
is a compile error (PCRE2 error 143) **unless `(?J)` is in force at that
declaration** — DUPNAMES SHIPPED 2026-08-22 ([M6.5.2]) and the split is:
DECLARING a duplicate name is this module's (the check below is conditional
on the scoped letter), RESOLVING a reference to one, and the `(?J)` letter
itself, are module `backrefs`'. Backreference-BY-NAME
spellings (`\k<n>` `\k'n'` `\k{n}` `(?P=n)`) are module `backrefs`, SHIPPED
in the same landing — Since Q2/SR-9 `(?<` names ONLY this module at the DECLARING
position: the three lookbehind tails `=` `!` `*` have rows of their own.
`--features none` (the bare default) still refuses with the module name;
`--features named-groups` compiles. Oracles: tests/named_groups/.
This annotation is keyed to `(?<name>a)` and covers the bundled prose row
`(?<name>...)` `(?'name'...)` `(?P<name>...)`.

**`(?>...)`** (2026-08-22)

Module `atomic-groups`, SHIPPED 2026-08-22 ([M6.4.2]); design
`docs/design/atomic_groups_design.md`, panel-approved at R31. The cut is a
real semantic change, not a no-op: `(?>ab|a)b` matches "abb" while
`(?>a|ab)b` matches only its first two bytes, because each group commits to
whichever branch its OWN order tried first — swap the branches and the
language changes. `--features none` (the bare default) still refuses with the
module name; `--features atomic-groups` compiles. VM-ONLY by registry row: a
priority DFA explores the alternatives in parallel and has nowhere to put a
cut, so a pattern that still carries one after the discharge below selects the
backtracking engine (SR-8, D67) and `--engine=dfa` refuses it by name
(`(?>a|ab)b`, measured). A cut whose section-2.2 proof shows it
can discard nothing is DELETED before engine selection
(`pcrec_discharge_atomic`; `-fno-atomic-discharge` disables it), which is why
`(?>a*)b` is still a DFA pattern — accepted even under an explicit
`--engine=dfa` — and `(?>a*)a` is not. Measured at
2026-08-22 from the artifacts' own `.engine` stamp: DFA, VM, and VM again for
`(?>a*)b` under `-fno-atomic-discharge`, which is the flag's controllability
witness. Oracles:
tests/atomic_groups/ — every cell produced by libpcre2 10.46 through the
project's committed ctypes binding — plus `run_atomic_diff.sh`'s differential
over subjects x start positions on BOTH engines and with the discharge off,
and `tests/codegen/run_atomic_identity.sh`'s byte-identity gate against the
pinned pre-module commit.
The `(*` spelling `(*atomic:...)` is a SEPARATE survey row and is NOT this
module: it is still answered "requires module 'verbs'" (see that section's
`base:verbs-module-attribution-gap`), and enabling `atomic-groups` does not
make it compile.
This annotation is keyed to `(?>...)`.

<!-- END GENERATED -->

## Comment

| syntax | status | becomes |
|---|---|---|
| `(?#....)` | `REJECTED` | `PLANNED` |

<!-- BEGIN GENERATED ANNOTATIONS: comment -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`(?#...)`**

module `comments` (previously misattributed to `modifiers`; fixed in this
survey). Pure lexing, `PLANNED`-trivial.

<!-- END GENERATED -->

## Option setting

| syntax | status | becomes |
|---|---|---|
| `(?i)` `(?i:...)` `(?-i)` | `OK` | — |
| `(?s)` dotall | `OK` | — |
| `(?m)` multiline | `OK-GATED` | — |
| `(?x)` `(?xx)` extended | `OK` | — |
| `(?U)` ungreedy | `OK` | — |
| `(?n)` no-auto-capture | `OK` | — |
| `(?J)` dup names | `OK-GATED` | — |
| `(?a)` `(?aD)` `(?aS)` `(?aW)` `(?aP)` `(?aT)` `(?r)` | `OK` | — |
| `(?^)` reset options | `OK` | — |
| `(*LIMIT_DEPTH=)` `(*LIMIT_HEAP=)` `(*LIMIT_MATCH=)` `(*LIMIT_RECURSION=)` | `OUT-OF-SCOPE` | — |
| `(*NO_JIT)` `(*NO_START_OPT)` `(*NO_AUTO_POSSESS)` `(*NO_DOTSTAR_ANCHOR)` | `OUT-OF-SCOPE` | — |
| `(*NOTEMPTY)` `(*NOTEMPTY_ATSTART)` | `REJECTED` | `PLANNED` |
| `(*UTF)` `(*UCP)` | `REJECTED` | `PLANNED` |
| `(*CASELESS_RESTRICT)` `(*TURKISH_CASING)` | `OUT-OF-SCOPE` | — |

<!-- BEGIN GENERATED ANNOTATIONS: option-setting -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`(?i)`** (2026-08-12)

Module `modifiers` SHIPPED THESE 2026-08-12 (MOD-0.5c): the D23 fold
driven by scoped parse state (`cx->mods`), the measured 17/17 group-scope
rule (leaks across sibling branches, restored at the enclosing `)`).
Default-on since [STD1b] (`ab7592d`, 2026-08-13): `modifiers` is in the
bare-default named set `std1` (D37); `--features none` still refuses with
the module name, `--features modifiers`/`--features std1` unchanged.
Oracles: tests/modifiers/, spec_mod0 check12.
This annotation is keyed to `(?i)` and covers the bundled prose row
`(?i)` `(?i:...)` `(?-i)`.

**`(?s)`** (2026-08-12)

Module `modifiers` SHIPPED 2026-08-12 (MOD-0.5c): `.` census 255 -> 256,
measured against the oracle. Default-on since [STD1b] (`ab7592d`,
2026-08-13, D37 `std1` set); `--features none` still refuses with the
module name.

**`(?m)`** (2026-08-19)

Module `assertions` SHIPPED THIS 2026-08-19 ([M6.2] wave C). MOD-0.5a's
ruling held: `^`/`$` at internal newlines IS assertion-engine work, so the
letter is produced by module `modifiers`' option run and attributed to
`assertions`, and needs BOTH enabled (`--features assertions,modifiers`;
`modifiers` is default-on under `std1`, `assertions` is not, so a bare
invocation still refuses by the letter's own name). Scoped by
construction: `(?m)` is resolved AT PARSE TIME onto the `^`/`$` node (D62,
`Ast.multiline`), so `(?m:...)`, `(?m)...(?-m)` and a mid-pattern `(?m)`
are right without any downstream pass re-deriving scope — and the SCOPED
cells are the ones D47.5's own wording did not ask for and the pre-cure
code got wrong. `\A`/`\Z`/`\z` are UNAFFECTED under `(?m)`, PCRE2's own
rule. **`(?m)^` is NOT the mirror of `(?m)$`**: PCRE2's multiline `^` does
not match after a newline that ENDS the string (python3 `re`'s does —
upstream_issues.md U11b, found here as a live defect first). `(?-m)`
remains an accepted no-op. Oracles: tests/assertions/multiline.rxt (both
oracles, 2,700+ cells), tests/assertions/run_mline_diff.sh (a generated
sweep against libpcre2 on both engines).

**`(?x)`** (2026-08-12)

Module `modifiers` SHIPPED THESE 2026-08-12 (MOD-0.5d): skip set
{09,0A,0B,0C,0D,20,85} (NOT `\s`'s set — NEL is skipped), `#`-comments to
0x0A only (the NEWLINE_LF convention), xx's class-interior {09,20}
deletion ahead of the endpoint rule (the D30 §7 `(?xx)[a- ]` hazard, now
compiled correctly), doubled-x ADJACENCY rule incl. the later-bare-x
downgrade — every clause probe-measured (probe_mod05*.c). Default-on
since [STD1b] (`ab7592d`, 2026-08-13, D37 `std1` set); `--features none`
still refuses with the module name.
This annotation is keyed to `(?x)` and covers the bundled prose row
`(?x)` `(?xx)`.

**`(?U)`** (2026-08-12)

Module `modifiers` SHIPPED 2026-08-12 (MOD-0.5c): default greed inverted
at quantifier construction, `?` re-inverts; NOT reset by `(?^)` (measured).
Default-on since [STD1b] (`ab7592d`, 2026-08-13, D37 `std1` set);
`--features none` still refuses with the module name.

**`(?n)`** (2026-08-12)

Module `modifiers` SHIPPED 2026-08-12 (MOD-0.5c): plain `(` stops counting
(`--count-groups` oracle-tied via check02's channel); does NOT imply J
(measured). Default-on since [STD1b] (`ab7592d`, 2026-08-13, D37 `std1`
set); `--features none` still refuses with the module name.

**`(?J)`** (2026-08-22)

**SUPPORTED since 2026-08-22 ([M6.5.2]), and the OWNER is module
`backrefs`** — ASK-1, ruled with R32. The attribution has now moved four
times and the history is kept because each move was wrong for a different
reason:

1. **`named-groups`, with "requires" framing** (MOD-0.5a) — true while that
   module did not exist, a LIE the moment it shipped WITHOUT dupnames, since
   "requires X" reads as "enabling X fixes this".
2. **K14's ROADMAP_NEVER shape** ([M6.3], briefly) — wrong the other way:
   `docs/pcre2_options.md`'s `PCRE2_DUPNAMES` row is `RIDES(M4/captures)`,
   RATIFIED D38, a PLANNED-LATER disposition, and `(?J)` does not meet K14's
   "architecturally out of scope per the survey" bar.
3. **`named-groups`, without the "requires" framing** ([M6.3], ruled) — right
   about the DECLARING half and silent about the RESOLVING one.
4. **`backrefs`, with "requires" back and TRUE this time** ([M6.5.2]). What
   makes the letter mean anything is the rule for resolving a reference to a
   duplicated name, and that machinery is this module's. **The split the page
   now records: DECLARING a duplicate name is `named-groups`; RESOLVING a
   reference to one, and the letter itself, are `backrefs`.**

**THE SCOPING RULE, MEASURED over seventeen libpcre2 cells**: the duplicate
check is made AT EACH DECLARATION, against the SCOPED `(?J)` state in force at
THAT declaration. Four cells separate it from every plausible alternative —
`(?<a>x)(?J)(?<a>y)` is LEGAL (the second declaration is under it);
`(?J:(?<a>x))(?<a>y)` is an error (the second is not); `(?<a>x)(?<a>y)(?J)` is
an error, which kills "(?J) anywhere legalises everything"; and
`(?J)(?<a>x)(?-J)(?<a>y)` is an error EVEN WITH the PCRE2_DUPNAMES API bit
set, which is what settles pcrec having the letter and no option bit.

**THE RESOLUTION RULE: the FIRST member of the name-run, by ASCENDING GROUP
NUMBER, that is SET** — "set" including set-to-empty. Measured against four
candidate rules over eighteen cells, and swept over name-runs of size 1..4
with every subset participating. `rx_info.groups` may now hold adjacent rows
with equal names, sorted (name asc, then NUMBER asc) — libpcre2's own
`PCRE2_INFO_NAMETABLE` order, measured — because
`docs/spec/match_api.md` §6's caller algorithm selects the lowest-numbered
participating member only if that order holds.

`(?-J)` accepted, and it really does turn the state back off. With `backrefs`
disabled the letter refuses naming it; with `modifiers` disabled the `(?`
doorway's own row refuses first, naming `modifiers` — two refusal sites for
one construct, both pinned. Pins: tests/reject/, tests/cli case11,
tests/backrefs/dupnames.rxt.

**`(?a)`**

MEASURED NO-OPS at options=0 C locale (probe_mod05.c: `(?ri)` vs `(?i)` 0
diff cells over 256x256; all four a-sub pairs census-identical) —
accepted and applied as nothing, which is exactly PCRE2's observable
behaviour in this mode. They become real under UTF/UCP: MOD-0.6/M5 own
that day (DD-12). Default-on since [STD1b] (`ab7592d`, 2026-08-13, D37
`std1` set); `--features none` still refuses with the module name.
This annotation is keyed to `(?a)` and covers the bundled prose row
`(?a)` `(?aD)` `(?aS)` `(?aW)` `(?aP)` `(?aT)` `(?r)`.

**`(?^)`**

Module `modifiers` SHIPPED 2026-08-12 (MOD-0.5c): resets i,m,n,s,x,xx to
the HARDWIRED defaults; U and J SURVIVE — "unset imnsx" is the measured
rule, and the reset is to-constant, not to-compile-option (both from
probe_mod05b.c). Default-on since [STD1b] (`ab7592d`, 2026-08-13, D37
`std1` set); `--features none` still refuses with the module name.

**`base:verbs-limit-depth`**

these bound a BACKTRACKING search. pcrec is O(n) by construction, so
there is nothing to limit. D22 also removes the adversarial-input
motivation. `LIMIT_RECURSION` is PCRE2's older synonym for `LIMIT_DEPTH`
— it was in pcrec's verb tables but missing from this row until the K14
check compared them (2026-08-11).

**`base:verbs-no-jit-family`**

knobs for PCRE2 implementation internals that pcrec does not have.

**`base:verbs-notempty`**

match-time semantics, expressible; no owner yet.

**`base:verbs-utf-ucp`**

module `verbs`; the underlying capability is M5.

**`base:verbs-caseless-turkish`**

for the ASCII tier — revisit with DD-1's Unicode work.

**`base:option-run-doorway-ordering`** (2026-08-12)

**A RULED, deliberate tier-2 divergence (D26; manager ruling 2026-08-12,
MOD-0.8c): the per-letter MODULE GATE answers before the option run's own
VALIDITY check.** An option run that is BOTH invalid as a run AND contains
a letter pcrec defers to another module is reported as the deferral, not
as the invalidity:

    $ build/pcrec --features modifiers -o - '(?m--)'
    pcrec: inline option 'm' (multiline) requires module 'assertions'
    libpcre2 10.46: error 194, "invalid hyphen in option setting"

`(?i--)`, whose letters are all implemented, IS diagnosed as the malformed
run it is — so the ordering is only observable through a deferred letter.
At measurement time (2026-08-12) that was exactly two letters, `m` (→
`assertions`) and `J` (→ `named-groups`) — both still true after [M6.3]
(2026-08-18): `J`'s wording moved (twice, same day — see the `(?J)`
annotation above) but it still names `named-groups` as its owning module,
so both letters remain MODULE-shaped deferrals, just with `J`'s phrasing
avoiding the false "requires" framing (`named-groups` IS enabled once
this diagnostic is reachable; enabling it again would not fix anything).

**Why this is tier 2 and not tier 1.** Both engines REFUSE, and neither
emits anything: what differs is which REFUSAL CATEGORY the user is told
about, which is the same distinction that keeps K15 at tier 2. Nothing
miscompiles, no pattern changes meaning, and pcrec's answer is not false —
`(?m--)` genuinely does need module `assertions` before it could ever
compile. It is simply the less useful of two true sentences, and D26 puts
diagnostic category for a construct pcrec has not implemented outside the
exact tier.

**MEASURED 2026-08-12** (re-measured for this entry, not transcribed from
the report that found it):

- Over `tests/spec_mod0/check14_option_runs.c`'s generated space: **286
  deferred cells of 4,385 compared — 189 by letter, 97 by doorway byte.**
  That is every deferral, of which the ordering divergence is the subset
  landing on an invalid run.
- Over PC-3's own option-run space (19,448 cells: the Q2 alphabet, runs of
  length 0-3, both terminator shapes), **14,986 cells are runs libpcre2
  calls invalid** (error 111 or 194). Of those, pcrec diagnoses 14,844 as
  invalid and DEFERS on **142** at the closed gate — all to `modifiers`,
  the row-level deferral before the run is ever read — and diagnoses
  14,978 and defers on **8** with the gate open (4 to `assertions`, 4 to
  `named-groups`: `(?m--)`, `(?m--:a)`, `(?^m-)`, `(?^m-:a)` and the `J`
  equivalents). Nothing is accepted in either state. **"Closed gate" here
  meant the bare default at measurement time (2026-08-12), when the bare
  default was empty; since [STD1b] (`ab7592d`, 2026-08-13, D37 `std1` =
  {`classes`, `modifiers`}) the BARE default reproduces the 8-cell
  gate-open figures for `modifiers` letters (verified live: bare
  `(?m--)` and `--features modifiers '(?m--)'` both give "requires module
  'assertions'") — only `--features none` reproduces the original
  142-cell closed-gate figure now.**

**THE POPULATION HAS REACHED ZERO. RE-MEASURED 2026-08-22 ([M6.5.2]): all
EIGHT cells now give the GRAMMAR error at the open gate**, so the open-gate
deferral count for this entry is **0**, not 8:

    --features all '(?m--)' '(?m--:a)' '(?^m-)' '(?^m-:a)'
    --features all '(?J--)' '(?J--:a)' '(?^J-)' '(?^J-:a)'
        -> all eight: "invalid hyphen in option setting (pattern offset 4)"

Both halves closed by the mechanism this entry predicted, in two separate
landings: 142 → 8 was opening the gate, and 8 → 0 is every letter whose
module lands and VALIDATES the letter. `m`'s 4 cells closed when
`assertions` shipped; `J`'s 4 closed on 2026-08-22 when module `backrefs`
shipped the letter — **which is the event this entry named and MIS-LOCATED**:
it said the `J`-half closes "when a FUTURE dupnames producer lands INSIDE
`named-groups`", and the producer landed inside `backrefs` instead, because
the letter's meaning is the rule for resolving a reference to a duplicated
name. The prediction that it would close, and by what mechanism, was right;
the module it named was not. Recorded rather than quietly corrected, since
this entry's whole subject is a deferral that expires on its own.

**AT THE BARE DEFAULT the cells still defer**, and that is the GATE rather
than this deferral: `std1` is {`classes`, `modifiers`}, so bare `(?m--)`
answers "requires module 'assertions'" and bare `(?J--)` answers "requires
module 'backrefs'" — measured the same day. Those close when the modules
join a named default set (D37's announced-boundary rule), which is a
different event from this one.

**REVISIT TRIGGER: DISCHARGED, both halves.** The re-ordering this entry
considered and did NOT take — deciding run validity before the module gate —
is now moot for the measured population, and the reason for not taking it
stands unchanged: it would move a grammar decision ahead of the gate for a
benefit that has now expired on its own, and the option-run grammar is one
home (`mod_modifiers.c`) precisely so the doorway does not acquire a second
copy of it. The entry is KEPT rather than deleted because the mechanism it
records — a validity check ordered after a module gate, producing a
diagnostic category that expires as modules land — is the thing worth
remembering, and because its prediction was checkable and half-wrong.

Found by the MOD-0.8b D27 blinded writer (recorded in
`docs/dev/reviews/2026-08-12-r20-mod08.md` as SPEC divergence 2) and ruled
document-don't-reorder. **No K row**: `docs/dev/known_issues.md` is for
confirmed BUGS deferred rather than fixed, and this is a ruled category
divergence with a self-closing population — the same treatment shape as
this file's K15 and K16 paragraphs, minus the defect.

<!-- END GENERATED -->

## Newline convention and `\R`

| syntax | status | becomes |
|---|---|---|
| `(*CR)` `(*LF)` `(*CRLF)` `(*ANYCRLF)` `(*ANY)` `(*NUL)` | `REJECTED` | `PLANNED` |
| `(*BSR_ANYCRLF)` `(*BSR_UNICODE)` | `REJECTED` | `PLANNED` |

<!-- BEGIN GENERATED ANNOTATIONS: newline-convention -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:newline-convention-verbs`**

module `verbs`. Newline convention is a compile-time parameter affecting
`$`, `.` and `\R` — exactly the kind of thing D18 says should be
hyperspecialized away.

**`base:newline-bsr`**

same, scoped to `\R`.

<!-- END GENERATED -->

## Lookaround

| syntax | status | becomes |
|---|---|---|
| `(?=...)` `(?!...)` | `OK-GATED` | — |
| `(?<=...)` `(?<!...)` — CAPABILITY limit: every TOP-LEVEL BRANCH of the body must be fixed-width; widths may DIFFER between branches (`(?<=a\|bc)x` compiles, `(?<=(a\|bc))x` is refused with a capability message and a pattern offset) | `OK-LIMITED` | `PLANNED` |
| `(*pla:)` `(*nla:)` `(*plb:)` `(*nlb:)` `(*positive_lookahead:)` `(*negative_lookahead:)` `(*positive_lookbehind:)` `(*negative_lookbehind:)` verbose spellings — module `lookaround`, NOT `verbs` | `OK-GATED` | — |
| `[[:<:]]` `[[:>:]]` — a word-boundary assertion, module `assertions`, filed in this section by the original survey | `REJECTED` | `PLANNED` |
| `(?*...)` `(?<*...)` `(*napla:)` `(*naplb:)` `(*non_atomic_positive_lookahead:)` `(*non_atomic_positive_lookbehind:)` non-atomic lookaround | `OK-GATED` | — |
| `(*nanla:)` `(*nanlb:)` — there is no non-atomic NEGATIVE form; PCRE2 error 195 | `AGREES-REJECT` | — |

<!-- BEGIN GENERATED ANNOTATIONS: lookaround -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`(?=...)`** (2026-08-24)

**SHIPS since [M6.6.2]** (design docs/design/lookaround_design.md,
panel-approved at R33). The pre-landing note read "lookahead is automaton
intersection — feasible, not cheap, and it multiplies states", which was
an analysis of the wrong engine: the module is VM-only (every row carries
`ENGM_VM` and SR-8 stamps it), and the lowering is the atomic group's
shape plus a saved cursor, not an intersection. The DFA still sees a
lookaround — `src/ir/nfa.c` lowers it to an EPSILON — but only as a
PREFILTER; that erasure is sound as a filter and would be a miscompile as
a machine, and the VM_ONLY stamp is the only thing between the two
readings.

**SIX CONSTRUCTS, EIGHTEEN SPELLINGS, and pcrec ships every one PCRE2
has** — `(?=` `(?!` `(?<=` `(?<!` `(?*` `(?<*` plus the twelve `(*` alpha
spellings below. The two shapes PCRE2 does NOT have are `(*nanla:` and
`(*nanlb:` (there is no non-atomic NEGATIVE form; error 195, measured on
10.46), and pcrec refuses both with PCRE2's own wording.

**`\K` IS REFUSED INSIDE A LOOKAROUND, PERMANENTLY** (measured:
`(?=a\K)b` is refused at the assertion's own offset; `a(?=b)\Kc` and
`(?<=a)\Kb` compile). libpcre2 10.46 refuses it in all four polarities
with error 199, whose text names `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK`;
pcrec matches the DEFAULT and does not implement that option — adopting
any `EXTRA_*` bit is a D38 ruling event, and Frank closed the reopening
on 2026-08-23. The refusal is recursive through nested groups and nested
lookarounds and stops at the assertion's own `)`.

**`(?<=...)`** (2026-08-24)

**SHIPS since [M6.6.2], FIXED-WIDTH PER BRANCH** — which is a WIDER rule
than "fixed-length lookbehind" and the difference is measurable, not
cosmetic. Every TOP-LEVEL BRANCH of the body must have a fixed width;
widths may DIFFER between branches. So `(?<=a|bc)x` COMPILES (two
branches, widths 1 and 2 — a pattern python `re` refuses outright), while
`(?<=(a|bc))x` is REFUSED: one branch of width 1..2. The two differ by a
pair of parentheses and by whether the longest-first step-back loop
PCRE2 runs within a branch is needed, which this module does not build.

The refusal is a CAPABILITY limit and is worded as one, at the
assertion's own pattern offset — "variable-length lookbehind is not
implemented: every alternative of a lookbehind must have a fixed length
(this one can match 1..2 characters)" — never as "requires module
'lookaround'", which would be an actionable-sounding lie to a caller who
has already enabled it. An unbounded body (`(?<=a*)x`) gets the same
refusal naming unboundedness; libpcre2's own answer there is error 125.

The pre-landing note ("tractable via the reverse machine D7 already
builds") named a mechanism the module did NOT use: the lowering is a
back-step to a known offset followed by a FORWARD body match and an
end-check, not a reverse machine — see the design's §3.5 for why.

**A BODY CARRYING A SUBROUTINE CALL IS MEASURED AFTER THE CALL GRAPH
EXISTS** ([DD-14.LB], `src/opt/postresolve.c`). A call's width is not
knowable at the parse hook — "how wide is `(?1)`" is a question about a
group that may not have been seen yet, and about a graph that does not
exist until every call is resolved — so the parse hook RECORDS the
lookbehind's offset and the width rule is re-asked at that offset once
`pcrec_callgraph_build` has run. The fixed-per-branch subset itself is
UNCHANGED by this; what changes is when it can be evaluated.

The two outcomes, MEASURED on 10.46 and on this tree (2026-08-24):

    (a)(?<=(?1))b           COMPILES both sides — an ACYCLIC callee of
                            fixed width composes, and so does calling it
                            twice: `(a)(?<=(?1)(?1))b` is width 2.
    (a(?1)?b)(?<=(?1))c     REFUSED both sides, at the SAME OFFSET (9).
                            A RECURSIVE callee is unbounded, so the body
                            is unbounded. libpcre2 answers error 125,
                            "length of lookbehind assertion is not
                            limited" — the same code and the same
                            sentence it gives the call-free `(?<=a*)x`.
                            pcrec answers its own capability wording
                            naming unboundedness.

    (a|bc)(?<=(?1))d        REFUSED HERE and accepted there — the
                            PRE-EXISTING fixed-per-branch limit above,
                            reached through a call rather than by
                            writing the alternation out. Nothing about
                            it is new; it is listed so the reader can
                            see the call does not change which rule
                            applies, only when it is asked.

**`base:lookaround-verb-spellings`** (2026-08-24)

**THE TWELVE `(*` ALPHA SPELLINGS ARE MODULE `lookaround`, AND SAYING
`verbs` WAS A REAL DEFECT** — this note itself said "module `verbs`; same
underlying feature" until [M6.6.2] wave F, and so did the compiler.
`(*pla:` `(*positive_lookahead:` `(*nla:` `(*negative_lookahead:`
`(*plb:` `(*positive_lookbehind:` `(*nlb:` `(*negative_lookbehind:`
`(*napla:` `(*non_atomic_positive_lookahead:` `(*naplb:`
`(*non_atomic_positive_lookbehind:` all answered *"(\*...) requires
module 'verbs'"* — promising a module that will never implement them,
while the module that does was never named. The cause: the `(*` doorway
was ONE registry row whose module answered for every name in both of
PCRE2's verb-name tables. D26 puts module attribution in tier 2, where
the standard is exact.

**EACH IS AN ALIAS OF A `(?` PRIMARY, and that is MEASURED rather than
read off the name** (libpcre2 10.46, 84 templates x 19 subjects, every
startpos, match span and every group span, 0 divergences): `(*pla:` and
`(*positive_lookahead:` are `(?=`; `(*nla:`/`(*negative_lookahead:` are
`(?!`; `(*plb:`/`(*positive_lookbehind:` are `(?<=`;
`(*nlb:`/`(*negative_lookbehind:` are `(?<!`;
`(*napla:`/`(*non_atomic_positive_lookahead:` are `(?*`; and
`(*naplb:`/`(*non_atomic_positive_lookbehind:` are `(?<*`. A spelling
that merely compiles proves nothing about what it is, which is why the
corpus separates them by the answers they give rather than by their
names.

Each has its own registry row and its own line in the index above, folded
into its primary's family (D71 item 3): the rows keep no byte-keyed
dispatch identity — the `(*` doorway decides by NAME — but a spelling a
caller can write is a spelling this page owes a line for, which is the
whole reason the twelve were added.

`(*atomic:` `(*script_run:` `(*sr:` `(*asr:` `(*atomic_script_run:`
`(*scs:` `(*scan_substring:` are NOT in this family and correctly still
name `verbs`.

**`base:posix-word-boundary-classes`** (2026-08-24)

**RECOGNISED, ATTRIBUTED, NOT BUILT — and the survey row above reading
`REJECTED` is CORRECT.** R33's staleness pass flagged this record as
reading like a ship claim beside a `REJECTED` row; re-measured today,
nothing ships: `[[:<:]]def` is refused as *"[[:<:]] is a word-boundary
assertion and requires module 'assertions'"* at every enabled set
INCLUDING `--features all`, so the module owns the construct and has no
producer for it. What MOD-0.3a moved was the ATTRIBUTION, not the
implementation. (This record also still sits in the LOOKAROUND section
because that is where the original survey filed it; the construct is
module `assertions`'.)

Module `assertions` since MOD-0.3a (2026-08-12; the split the earlier
text assigned to whoever implemented the doorway) — they are NOT
character classes but zero-width WORD BOUNDARY assertions PCRE2 inherited
from its Unix ancestry, measured on "abc def" (`[[:<:]]def` matches
[4,7), `abc[[:>:]]` matches [0,3)); `^` does not negate them. Found by
PC-3's generated name differential (FIX-2), not by reading. **And they are
POSITION-RESTRICTED (R9/C3-4):** libpcre2 accepts them ONLY as a class's
ENTIRE content, so `[[:<:]]` compiles while `[x[:<:]]`, `[[:<:]a]` and
even `[^[:<:]]` are all error 130 — unlike every ordinary POSIX name,
which works in any position. pcrec promised module `classes` for all of
those until R9; it now answers "unknown POSIX class name", and
`check_posix_positions` in tests/registry/ crosses name against position,
which is the axis pair neither earlier differential varied.

**`(?*a)`** (2026-08-24)

**SHIPS since [M6.6.2], and it is a DIFFERENT CONSTRUCT from `(?=`, not a
spelling of it** — measured on "abab", which is the cell that fixes it:
`(?*(a|ab))\1$` matches (2,4) because the body RETRIES and finds "ab",
where `(?=(a|ab))\1$` is NOMATCH because the atomic form commits to the
body's first success. `(?<*` is the same difference one direction over.
The lowering is the atomic shape MINUS the cut.

**This row was RIGHT and the registry was WRONG** until R8/C4-8:
`(?*...)` had no registry row, so the `(?` catch-all answered "requires
module 'modifiers'" for it. Three homes, one disagreeing — the `\v` shape
exactly, and found the same way, by reading an outside source rather than
by any test. The non-atomic variants are defined by their backtracking
behaviour.

<!-- END GENERATED -->

## Substring scan, script runs

| syntax | status | becomes |
|---|---|---|
| `(*scan_substring:...)` `(*scs:...)` | `OUT-OF-SCOPE` | — |
| `(*script_run:...)` `(*sr:...)` `(*atomic_script_run:...)` `(*asr:...)` | `REJECTED` | — |

<!-- BEGIN GENERATED ANNOTATIONS: substring-scan -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:scan-substring`**

(revisit post-M4) — re-matches against previously CAPTURED text, so it
needs capture state at match time.

**`base:script-run`**

module `verbs`. Needs Unicode script data (M5); the assertion itself is
regular.

<!-- END GENERATED -->

## Backreferences

| syntax | status | becomes |
|---|---|---|
| `\1` `\g1` `\g{n}` `\g{+n}` `\g{-n}` `\k<n>` `\k'n'` `\k{n}` `(?P=n)` | `OK-GATED` | — |

<!-- BEGIN GENERATED ANNOTATIONS: backreferences -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`\1`** (2026-08-22)

**Backreferences are not a regular language** — no DFA can do them, and
PCRE2's own DFA matcher does not.

**Module `backrefs` SHIPPED 2026-08-22 ([M6.5.2]).** Every spelling in the
bundled row above parses and matches: the numeric forms (`\1`..`\N` for any
N — measured to `\812`, with PCRE2's octal disambiguation resolved by four
ordered questions), `\g1` `\g{n}` `\g{+n}` `\g{-n}` `\g{name}`, `\k<n>`
`\k'n'` `\k{n}` and `(?P=n)`. VM-only, by all twelve rows' `engines` mask
consumed through SR-8's generic consultation (D67) — there is no
backrefs-specific engine analysis. Oracles: tests/backrefs/ (226 generated
cells, every one driven through libpcre2 before it was written) plus two
differentials whose PRIMARY arms compare 14,128 cells against libpcre2 on the
match span AND every group span — 13,300 over 35 patterns x 91 subjects x every
startpos, and 828 over name-runs of size 1..4 with every subset participating.
Their other arms (both engine selections, --no-captures, the three entry
points, the find-all loop, the span-divergence detector and a 65,536-pair fold
agreement) compare more again.

**THE OCTAL ASYMMETRY IS THE PART A READER SHOULD KNOW.** `\1`..`\9` count
groups over the WHOLE pattern (`\1(a)` compiles — the group is AFTER the
escape), while `\10`+ count only groups BEFORE the escape (`\10(a)..(j)` is
the OCTAL byte 0x08, and `(a)\10` is octal 010 rather than "group 1 then
'0'"). A run beginning `8` or `9` is ALWAYS decimal, because those are not
octal digits and the re-read would consume nothing. Measured cell by cell.

**AN UNSET REFERENCE FAILS; AN EMPTY ONE SUCCEEDS**, and the two are one `if`
apart: `^(a)?\1$` on "" is NO MATCH, while `^(x?)y\1z$` on "yz" is (0,2) with
group 1 = (0,0). `PCRE2_MATCH_UNSET_BACKREF` would flip 2 of the 8 measured
unset cells and is explicitly out of scope (it needs a second emitted shape
for one construct, selected by an option pcrec does not have).

**A REFERENCE INSIDE A RE-ENTERED GROUP SEES THE LAST *COMPLETED* ITERATION.**
`(a|b\1)+` on "ab" is (0,1) with group 1 = (0,1). That is why a referenced
group's capture pair is PUBLISHED TOGETHER at the group's close rather than
written as control traverses each end — under the latter a re-entered group
holds a half-open pair that is neither UNSET nor a capture, and two shapes
underflow a `size_t` in emitted code.

**D23's BOUNDARY, and it is where the encoding seam earned its second
customer.** A CASELESS backreference compares subject text to subject text,
which cannot fold into the automaton, so the fold happens at MATCH time in the
encoding residual `$_bref_match_caseless` — the [M5-SEAM]'s second and third
entries. The caselessness is the option in force AT THE REFERENCE, not at the
group: `^(a)(?i:\1)$` matches "aA" and `^(?i:(a))\1$` does not.

**NO PREFILTER**, and that is measured rather than cautious: the
capture-erased approximation a hybrid would be built from is not even a
SUPERSET once the referenced group's transitive closure holds an assertion or
an atomic/possessive operator (12 of 18 positive-control cells are false
negatives), and where it IS a superset its leftmost SPAN differs from the true
one on up to 389 subjects in one family. The cost is one to two orders of
magnitude on the families where a prefilter would have helped, and a
nomatch-only filter gated on that closure is chartered rather than dropped.

All ATOM position: inside a class these spellings are not backreferences at
all — octal or literal fallback, supported since FIX-3 (K13); see Escaped
characters. **The module does not touch the class position**, which
tests/backrefs/octal_class.rxt pins with the module ENABLED.
This annotation is keyed to `\1` and covers the bundled prose row
`\1` `\g1` `\g{n}` `\g{+n}` `\g{-n}` `\k<n>` `\k'n'` `\k{n}` `(?P=n)`.

<!-- END GENERATED -->

## Subroutine references and recursion

| syntax | status | becomes |
|---|---|---|
| `(?R)` `(?n)` `(?+n)` `(?-n)` `(?&name)` `(?P>name)` `\g<name>` `\g'n'` `\g<0>` `\g'0'`, the multi-digit and leading-zero spellings `(?10)` `(?01)` `(?00)` `(?+2)` `(?-10)` — TWO LIMIT KINDS, both RESOURCE-shaped, plus one CAPABILITY note. (1) RESOURCE, the stamped capacity (D73): every LINKED call is a resume frame that outlives its return, so call depth is bounded by the artifact's frame/trail capacities — 2048/3072 by default, and the TRAIL binds first (measured 2.0 frames vs 9.0 trail entries per nesting level of `^(a(?1)?b)$`, so the default gives up at n = 342, a 684-byte subject). Past it the answer is a clean `PCREC_ERR_FRAMES`, never a wrong one, and the remedy is the caller-provided buffer ([DD-14.FB]'s `_in` entries, 64 MB `MAP_NORESERVE` matching 800 KB in 0.056 s) rather than a bigger default. (2) RESOURCE, the runaway give-up where PCRE2 CONCLUDES (K34): on some same-position left recursions — `(a\|(?1)a)b` on `"a"`, `^(a\|(?1)a)$` on `"aaaaab"` — libpcre2 10.46 returns a clean NOMATCH and pcrec returns `PCREC_ERR_FRAMES`. A give-up says nothing about the language, so this is not a wrong answer under D26; it is a documented answer, and K34 carries the measured rule (65/65 cells) with the lane's recommendation not to adopt it. CAPABILITY note: `--engine=dfa` refuses each call row BY NAME, but that describes the LINKED form — a spliceable (acyclic) callee is inlined exactly and its pattern gets whatever engine the hand-inlined pattern gets (wave G; see the `(?1)` annotation below) | `OK-LIMITED` | `PLANNED` |
| `(?R(grouplist))` and capture-retaining forms | `OUT-OF-SCOPE` | — |

<!-- BEGIN GENERATED ANNOTATIONS: subroutine-recursion -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`(?1)`** (2026-08-24)

**WHAT `vm` IN THE `engines` COLUMN MEANS FOR A CALL ROW, AFTER [DD-14] WAVE
G.** It is a claim about the LINKED form of the construct, not about every
pattern that spells it. `engines` is a per-ROW field and a call's true engine
is a per-PATTERN fact: the language `^(a(?1)?b)$` generates is `aⁿbⁿ`, which is
not regular and is VM-only for ever — but `(a)(?1)` names an ACYCLIC callee,
which `src/opt/callgraph.c` SPLICES and `src/ir/nfa.c` lowers EXACTLY, so it is
as regular as `(a)a` and compiles to whichever engine the hand-inlined pattern
would. Read the column as: **a call in a CYCLE forces the VM; a spliceable call
does not, and its pattern gets the engine its inlined equivalent gets.**

This is `(?>`'s situation one construct over (genuinely VM-only for
`(?>a|ab)c`, genuinely not for `[^"]*+"`), and the column stays conservative
for the same D67 reason in both cases. Where the two differ is HOW the gap is
closed: `pcrec_discharge_atomic` DELETES the atomic node before engine
selection looks, while a call cannot be deleted without copying its callee's
`A_CAP` nodes into the tree — so a call's gap is closed by the LINKAGE, a fact
`pcrec_callgraph_build` computes and `first_dfa_excluding` reads.

MEASURED: `--no-captures --engine=dfa '(a)(?1)'` COMPILES;
`--no-captures --engine=dfa '(a(?1)?b)'` refuses naming `(?1)`; and
`--no-captures --engine=dfa -fno-splice-calls '(a)(?1)'` refuses naming `(?1)`
— the third being the flag doing exactly what lib/pcrec.h says it does, and the
axis on which this column is exactly true. `tests/registry/registry_check.c`'s
engine-capability check asks its refusal under that flag for this reason.

**`(?R)`** (2026-08-25)

**SHIPS since [DD-14]** (design docs/design/subroutines_design.md,
R34-approved). This annotation is keyed to `(?R)` and covers the bundled
prose row for every call spelling.

**THE PRE-LANDING NOTE WAS RIGHT ABOUT THE OBSTACLE AND WRONG ABOUT THE
CONCLUSION.** It read: "Recursion makes the pattern language
context-free, which is outside both a DFA and a plain Pike VM; it needs a
recursive/backtracking matcher." The premise holds and is MEASURED —
`^(a(?1)?b)$` is a^n b^n, matching at n = 400,000 — which is exactly why
the `engines` column on every call row reads `vm` and why `--engine=dfa`
refuses each of them BY NAME rather than silently downgrading. What the
note got wrong is that pcrec's VM is not a plain Pike VM: it is a
backtracking machine with a resume stack, so a call lowers to a saved
return site and a shared callee region and needs no new engine.

**THE SURVEY ROW NAMES TWO LIMIT KINDS, BOTH RESOURCE-SHAPED, PLUS A
CAPABILITY NOTE — and this record takes them in that order.** The
CAPABILITY note is the engine restriction above, and wave G narrowed it
to the LINKED form (see the `(?1)` record). The FIRST resource limit is
that a call's
resume frame OUTLIVES ITS RETURN (design §5.1/§5.3), so recursion and
call-driven iteration are both bounded by the artifact's frame capacity;
past it the answer is a clean `PCREC_ERR_FRAMES`, never a wrong one.
MEASURED at a real size rather than in principle: the RFC 5322 email
specimen's call-factored spelling gave up about 2 K iterations into a
2000-deep subject at the 2048-frame stamped default
(docs/design/subroutines_measurements/email_specimen/README.md) — and at
[DD-14] wave G it gives up on NO subject in that population, because a
spliced call consumes no resume frame.

**THE CAPACITY IS D73's, AND THE NUMBER THAT BINDS IS THE TRAIL'S**
(Frank, 2026-08-24, superseding D71 item 2's "a larger stamped default
for call-bearing patterns"). The default STAYS at 2048 frames / 3072
trail entries: the run struct lives on the C stack of the un-suffixed
entries (131,144 B call-bearing), which already SIGSEGVs a musl-default
128 KB thread (K33), and the trail binds BEFORE the frames — 2.0 frames
against 9.0 trail entries per nesting level of `^(a(?1)?b)$` — so the
shipped default gives up at n = 342, a 684-byte subject, and raising
frames alone would change nothing. The remedy is not a bigger default
but the CALLER-PROVIDED BUFFER ([DD-14.FB]'s three `_in` entries: a
224 B frame, a 64 MB `MAP_NORESERVE` reservation matching 800 KB in
0.056 s). That is why the `becomes` column reads `PLANNED` rather than
permanent — the path around the limit ships, it is just not the default.

**THE SECOND RESOURCE LIMIT IS A DIVERGENCE RATHER THAN A CAP: K34.** On some same-position LEFT recursions pcrec answers
`PCREC_ERR_FRAMES` where libpcre2 10.46 CONCLUDES with a clean NOMATCH —
`(a|(?1)a)b` on "a"/"aa"/"b"/"" and `^(a|(?1)a)$` on "aaaaab" are the
measured cells. It is not a wrong answer under D26 (a give-up says
nothing about the language), and it is not the naive rule the design
§3.3 refuted: PCRE2's own guard returns error −52 only when a nearest
same-group ancestor recursion exists AND the subject pointer AND the
`last_used_ptr` high-water mark are both unchanged, which is why 199
same-position recursions can still MATCH and why the unanchored runaways
conclude. Lane srK34 pinned that rule on a 65/65-cell probe matrix
(docs/design/subroutines_measurements/out/recurse_loop.txt) and
RECOMMENDED against adopting it — a faithful copy needs a stored subject
pointer and a `last_used_ptr` equivalent threaded through every
fail-and-return site of the emitted artifact, not an O(1) per-callee
slot. The inverse case exists too and no expectation is writable for it:
`((?1)?a)` and `((?1)*a)` on "a" MATCH here and are −52 there. **RULED
(D74, Frank 2026-08-25): DOCUMENTED DIVERGENCE, not adopted.** The
give-up stays pcrec's answer for this shape; the eleven affected corpus
cells stay parked under the known-fail ratchet, visible as
pcrec-wrong-by-capability rather than pending a fix. K34 is CLOSED as a
divergence, not a bug.

**THE LEADING-ZERO RULE IS THE SHARP EDGE OF THIS FAMILY**, and it is
why the index shows spellings a reader might take for redundant. The
WHOLE DIGIT RUN after `(?` — or inside the angle-bracket and quoted `\g`
spellings — is read as decimal, so `(?0)` and `(?00)` are the ROOT while
`(?01)` is GROUP 1. MEASURED on the ANCHORED discriminator, since the
unanchored form answers the same either way: `^(a(?01)?b)$` on "aabb" is
(0,4) and `^(a(?0)?b)$` is NOMATCH. A port written from "`(?0)` is a
synonym for `(?R)`" compiles `(?01)` as the root and miscompiles it.

**AND THAT RULE IS WHY [DD-14] WAVE F ADDED NINE INDEX ROWS.** The
multi-digit calls `(?10)`/`(?-10)`, the `(?+N)` siblings, `\g<0>`/
`\g'0'` and the leading-zero absolutes are all spellings this compiler
ALREADY handled correctly — the ports read the digit run, they never
read the row's selector as a number — and none of them appeared on any
surface pcrec publishes. They are index rows (D71 item 3): they never
dispatch, they carry the byte their spelling really enters at, and each
is folded into its primary's family line above.

**`base:recursion-grouplist`**

(revisit post-M4) — capture-state dependent.

<!-- END GENERATED -->

## Conditional patterns

| syntax | status | becomes |
|---|---|---|
| `(?(n)...)` `(?(<name>)...)` `(?(name)...)` | `REJECTED` | `PLANNED-HARD` |
| `(?(R)` `(?(Rn)` `(?(R&name)` | `REJECTED` | — |
| `(?(DEFINE)...)` — module `recursion`, NOT `conditionals` (D71 item 4); filed in this section because that is where PCRE2's own syntax summary puts it | `OK-GATED` | — |
| `(?(assert)...)` | `REJECTED` | — |
| `(?(VERSION>=n.m)...)` | `OUT-OF-SCOPE` | — |

<!-- BEGIN GENERATED ANNOTATIONS: conditional-patterns -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`(?(1)a|b)`**

The condition is "did group N participate", i.e. capture state —
explicitly unsupported by `pcre2_dfa_match` for the same reason.

**`base:conditional-recursion-test`**

recursion-dependent.

**`(?(DEFINE)(?<w>a))`** (2026-08-24)

**SHIPS since [DD-14] wave F, AND IT IS MODULE `recursion`'S** rather
than `conditionals`' (D71 item 4, Frank 2026-08-23, overruling the
subroutines design's own §2.5 "RULED: no DEFINE"). It is a TAILED row on
the `(?(` doorway — tail `DEFINE)`, rank 25 — and EVERY OTHER condition
at that doorway is still `conditionals`' and still refused. Enabling
`recursion` does not unlock `(?(1)`, `(?(R)` or `(?(<name>)`; the cell
that pins that is in `tests/recursion/refused.rxt`.

**THE TAIL INCLUDES THE CLOSING PARENTHESIS**, which is not tidiness:
MEASURED on 10.46, `(?(define)...)` and `(?(DEF)...)` are read as NAME
conditions ("reference to non-existent subpattern"), so a tail of
`DEFINE` alone would have claimed `(?(DEFINED)` — a `conditionals`
construct — for this module.

**ONE ROW, ZERO NEW MECHANISM.** `(?(DEFINE)BODY)` is a conditional
group whose condition is never true, so BODY never runs where it is
written and exists only to be called — which is exactly what
`(?:BODY){0}` means, and the `{0}` layout rule the R34 verifier forced
already IS DEFINE's semantics (design §4.4c). The port produces the
node `(?:BODY){0}` produces, an `A_REP` with rmin == rmax == 0 over the
body, so `callgraph.c`, `vm_count_slots` and `emit_vm.c` gained not one
line. That claim is CHECKED rather than asserted: codegen rule 4
compiles both spellings and requires the artifacts to be identical byte
for byte once the pattern text and offsets are normalised away, with the
`{1}` spelling as its positive control.

**THE ONE REFUSAL IS PCRE2'S OWN RULE**: a DEFINE's own top level may
carry only one branch. `(?(DEFINE)a|b)` is "DEFINE subpattern contains
more than one branch" at offset 3 — the byte after `(?(`, MEASURED in
three positions — and pcrec blames the same byte with the same sentence.
An alternation INSIDE the defined group (`(?(DEFINE)(?<w>a|b))`) is
fine; the rule is about the DEFINE's top level.

**WHAT IS NOT REFUSED, measured rather than assumed**: an empty body
(`(?(DEFINE))`), a body that defines no group at all
(`(?(DEFINE)abc)`), and a QUANTIFIED DEFINE (`(?(DEFINE)(?<w>a))*`) all
COMPILE on 10.46, so all three compile here.

**IT IS THE ONE ROW IN MODULE `recursion` THAT IS NOT `VM_ONLY`**, and
the index above shows it as `dfa|vm`. Every other row in the module is
VM_ONLY structurally — `^(a(?1)?b)$` generates a^n b^n, which is not
regular — but a DEFINE is not a call: it is a zero-width definition, and
a pattern containing one is exactly as regular as the pattern without
it. MEASURED on the shipped compiler: `--engine=dfa --no-captures
'(?:(?<g>a)){0}b'` produces a pure DFA artifact. What forces the VM in
every real use of a DEFINE is the CALL that reads it, which carries its
own row and its own stamp.

**THE INTERIM "TWO EXACT SUBSTITUTES" NOTE IS RETIRED** with this wave.
It documented `(?:(?<w>X)){0}` and `^(?!)(?<w>X)|BODY` as stand-ins while
the row did not exist. The first of them is not a substitute any more —
it is the SAME PROGRAM, which is what codegen rule 4 measures — and the
second remains a legal spelling nobody now needs.

**`base:conditional-assert`**

lookaround-dependent.

**`base:conditional-version`**

tests the PCRE2 library version; meaningless for a different
implementation. If a compatibility layer (V-A) ever wants it, it is a
parse-time constant fold.

**`base:conditional-name-disambiguation`**

**Disambiguation trap worth recording**: PCRE2 resolves `(?(name)` as a
group-reference condition when a group of that name exists and as a
recursion test otherwise. Any conforming implementation must replicate
that rule exactly or it will silently miscompile ambiguous patterns.

<!-- END GENERATED -->

## Backtracking control verbs

| syntax | status | becomes |
|---|---|---|
| `(*FAIL)` `(*F)` | `REJECTED` | `PLANNED` |
| `(*ACCEPT)` | `REJECTED` | `PLANNED-HARD` |
| `(*COMMIT)` `(*PRUNE)` `(*SKIP)` `(*SKIP:NAME)` `(*THEN)` `(*MARK:NAME)` `(*:NAME)` | `OUT-OF-SCOPE` | — |

<!-- BEGIN GENERATED ANNOTATIONS: backtracking-verbs -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:verbs-doorway-q1`** (2026-08-10)

**Since Q1 (2026-08-10, D25) the `(*` doorway distinguishes NAMES.**
Everything in this section is still `REJECTED`, but a name PCRE2 does not
have is now told so — `(*NOTAVERB)` gets PCRE2's own "(*VERB) not
recognized or malformed" instead of a promise that module `verbs` will
one day implement it. The distinction runs deeper than the table below
shows: PCRE2 keeps TWO name tables selected by the CASE of the first
byte, with a different error for each, and its argument rules are
PER-NAME (`(*ACCEPT:x)` compiles, `(*CR:x)` does not, `(*MARK)` alone is
an error, `LIMIT_*` takes `=digits` with a magnitude limit, and a name
over 128 bytes is a third complaint again). pcrec reproduces all of it,
and `tests/registry/pcre2_check.c` re-measures every bit of it against
libpcre2 on each run. `pcrec --list-verbs` prints the tables.

**`base:verbs-k15-name-length`** (2026-08-12)

**A RULED, deliberate tier-2 divergence (K15, D26; Frank, 2026-08-12):**
for a verb "name" over the 128-code-unit cap made ENTIRELY of
non-identifier bytes, pcrec answers "subpattern name is too long
(maximum 128 code units)" where libpcre2 10.46 answers error 160, "(*VERB)
not recognized or malformed", at offset 2. Root cause: pcrec's extent scan
(`pcrec_verb_name_extent_scan`, scans.c) reads every byte up to `)` `:`
`=` EOF before it ever compares the run to a table entry, so an over-cap
run hits the length check first; libpcre2's own scan stops at the first
non-alnum/`_` byte and reports "not recognized" about the short prefix it
actually extracted. Both are honest refusals of a name that can never
match a real verb — the two engines diverge on which REFUSAL CATEGORY,
never on accept vs. reject, which is what keeps this at tier 2 rather
than tier 1. Found by the R18 panel's engine critic
(docs/dev/reviews/2026-08-12-r18-mod04.md), recorded at
docs/dev/known_issues.md K15, and confirmed on both controls: UNDER the
128-byte cap a non-identifier run gets "not recognized" on both sides
(agreement — K15's own control), and OVER the cap an IDENTIFIER run gets
the exact same "too long" text on both sides (also agreement — the
128-byte rule itself is right for identifier names).
`tests/registry/pcre2_check.c`'s `k15_excluded()` carries the one
exclusion this divergence needs, scoped to exactly that cell; extending
the extent scan to stop at the first non-identifier byte is deferred to
SR-6, when module `verbs` first produces and the scan's semantics get
remeasured anyway. See also docs/dev/known_issues.md K15 and
docs/pcre2_compliance.md's own Backtracking control verbs section.

**`base:verbs-module-attribution-gap`** (2026-08-22)

What pcrec does NOT yet claim is which MODULE owns each name:
`(*atomic:…)` and `(*pla:…)` are answered "requires module 'verbs'"
though they are atomic groups and lookarounds, and correcting that
belongs to SR-6 with the module itself.
SHARPER since [M6.4.2] (2026-08-22): `(?>...)` and the possessive suffixes
now BUILD under module `atomic-groups`, so `(*atomic:...)` is the one
spelling of a SHIPPED construct that still refuses — and it names `verbs`,
not `atomic-groups`, so enabling the module that implements the construct
does not make this spelling compile. Still a naming gap, not a miscompile:
the refusal is clean and D26-conforming, and SR-6 still owns the fix.

**`base:verbs-out-of-scope-diagnostic`** (2026-08-11)

**Since MOD-0.1's K14 fix (2026-08-11) the diagnostic honours this
section's own OUT-OF-SCOPE calls:** every name below marked OUT-OF-SCOPE
carries `ROADMAP_NEVER` in the verb tables and answers "... is outside
pcrec's scope and no module will implement it" instead of promising
module `verbs`. `compliance_section.py --names` holds this section and
the column together in both directions, so editing an OUT-OF-SCOPE cell
here without moving the column (or vice versa) fails `make test`. (`(?C`
callouts at the `(?` doorway carried the same OUT-OF-SCOPE/`ROADMAP_NEVER`
pairing until [M4-CALLOUTS] step 1 moved it to `PLANNED` — see the
Callouts section below. The live population of non-verb `ROADMAP_NEVER`
rows is zero as a result; the check that ties this column to the prose
stays column-derived rather than deleted, so it re-arms the day a second
such row exists.)

**`base:verb-fail`**

module `verbs`. The one verb PCRE2's DFA matcher DOES support: in a
priority simulation it is simply a path that never reaches an accept
state.

**`(*ACCEPT)`**

Expressible in principle (force an accept), but it interacts with the
two-pass end-then-start architecture.

**`base:verbs-backtracking-control-family`**

these are DEFINED in terms of a backtracking engine's search order —
which alternatives to abandon and where to resume. A simulation engine
explores all alternatives at once, so there is no backtracking tree to
prune. PCRE2's own DFA matcher supports none of them. `(*MARK)`
additionally requires reporting state back to the caller.

<!-- END GENERATED -->

## Callouts

| syntax | status | becomes |
|---|---|---|
| `(?C)` `(?Cn)` `(?C"text")` | `REJECTED` | `PLANNED` |

<!-- BEGIN GENERATED ANNOTATIONS: callouts -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`(?C1)`** (2026-08-14)

**[M4-CALLOUTS] step 1 (D36, Frank, 2026-08-12; flipped 2026-08-14):**
re-scoped from `OUT-OF-SCOPE` to `PLANNED`, module `callouts`, explicitly
LOW priority — parked behind the M4 VM engine that hosts the behavior
(callouts are engine-forcing like backrefs: the compiled DFA erases the
pattern positions a callout fires at, so callout patterns compile to the
VM engine only). The PATTERN layer (syntax, where callouts may appear) is
D26-exact and PCRE2-compatible; the CALLBACK CONTRACT mirrors
`pcre2_callout_block` field for field; the REGISTRATION API is
pcrec-native (a compile-time-bound `extern` the embedding program
defines, zero cost when absent) rather than a runtime
`pcre2_set_callout`-style registration. The obstacle that kept this
`OUT-OF-SCOPE` no longer applies as a permanent one: generated code's
zero runtime dependency on pcrec is preserved by the static-extern
binding, not by refusing the construct. Step 2 (the behavior itself) is
not yet built — see `docs/dev/plan.md`'s `[M4-CALLOUTS]` row.

Module `callouts`, M4-hosted, VM-only (D36). Callback block and return
semantics (0/positive/negative) mirror `pcre2_callout_block` field for
field; fire-point precision is documented engine-relative, with PCRE2's
own `PCRE2_NO_START_OPTIMIZE` latitude as the cited precedent that fire
counts are not the contract.

<!-- END GENERATED -->

## Replacement strings

| syntax | status | becomes |
|---|---|---|
| `$1` `${n}` `$<name>` `$&` `` $` `` `$'` `$_` `$+` `$*MARK`, `\l \u \L \U \E` | `OUT-OF-SCOPE` | — |

<!-- BEGIN GENERATED ANNOTATIONS: replacement-strings -->

<!-- Generated by tests/registry/compliance_section.py from
     docs/pcre2_compliance_annotations.txt. Do not edit by
     hand: `make test` fails on drift. Edit the annotation
     store and re-run with --write-annotations. -->

**`base:replacement-strings`**

pcrec compiles a MATCHER. It has no substitution API, and APPROACH does
not propose one. Listed for completeness because pcre2syntax.html covers
it; a substitution layer would be a separate product decision.

<!-- END GENERATED -->

---

## How this survey earned its keep

Three findings, all of which existed before the survey and none of which any
test could see.

**1. `\v` was miscompiled, and the oracle agreed with the bug.** PCRE2's `\v` is
vertical whitespace; pcrec decoded it as vertical tab. Measured against
libpcre2 10.46: PCRE2 matches `0x0a 0x0b 0x0c 0x0d 0x85`, pcrec matched `0x0b`
alone — six bytes versus one, inside classes as well as outside. It survived
because python `re`, the base-tier oracle, also reads `\v` as `0x0B`, so
`tests/base/escapes.rxt` asserted the wrong answer and passed. The asymmetry
that gave it away was in the parser itself: `\V` was routed to module `classes`
while `\v` was decoded as a control character — the same construct treated two
different ways, ten lines apart.

The lesson generalises past this one escape: **where python `re` and PCRE2
disagree, a python-verified corpus certifies the divergence instead of catching
it.** That is the argument for the M7 libpcre2 differential work, restated with
a concrete casualty.

**1b. POSIX collating elements were accepted, and PCRE2 rejects them.**
`[[.a.]]` and `[[=a=]]` are collating-element and equivalence-class syntax.
PCRE2 does not implement them and errors out; pcrec compiled them into a class
of literal `[`, `.`, `a` characters — a pattern PCRE2 refuses, given a meaning
PCRE2 never assigns it. python `re` accepts them too (with a FutureWarning), so
again the base-tier oracle could not see it.

The fix was worth doing carefully rather than quickly. The naive reading —
"reject any `[.` inside a class" — over-rejects: PCRE2 only treats it as a
collating element when the matching `.]` terminator actually appears, so
`[.a]`, `[.]`, `[[.]`, `[a[.b]` and `[a.b.]` are ordinary classes that must keep
compiling, and a leading `^` suppresses the rule entirely (`[^.a.]` compiles).
All 18 forms were checked against libpcre2 and pcrec now agrees with it on
every one. The six that must still compile are accept-controls, because
over-rejection is the opposite failure and just as wrong.

**2. The mandate's central guarantee had no test.** "Unsupported constructs
must fail with a clean `requires module 'X'` error, never miscompile" is the
project's core promise, and nothing checked it. It could not live in the .rxt
corpus: a `perr` block asserts only THAT a pattern is rejected, never WHY, and
the module name is the caller's only pointer to what would implement the
construct.

**CORRECTED 2026-08-10 (R7).** This paragraph used to give a second reason —
that a `perr` block also needs the python oracle to fail, and that the
`# pcre2-only` escape hatch "does not apply because `verify_rxt.py`'s `perr`
branch never consults it". The first half is true; the second is FALSE and was
never measured. `verify_rxt.py`'s skip test precedes its `perr` branch, so a
marked block is skipped like any other case while `run.sh` still asserts it
against pcrec. FIX-1 corrected the claim in `tests/reject/`, and a critic found
this third copy still standing here, in the present tense, unflagged — the same
"one claim, several files, never measured" shape the document elsewhere warns
about.

`tests/reject/run_reject_tests.sh` asserts, per construct, that pcrec exits
exactly 1 (not 0, not a crash, not a timeout), carries the right diagnostic,
and writes no output file — 144 rows, plus 45 accept-controls, at R7 when this
was first built; the count has moved several times since and the same
hand-copied-figures failure mode this document warns about elsewhere (see
"Keeping this current") applied here too. **Current whole-suite figures,
measured live at [M6.4.2] (2026-08-22): 279 hand-written rows, 99
accept-controls, 65 `reject_gated` pins, 103 iterated, 547 checks passing, 0
known-wrong — see the Headline above; do not re-copy these either, re-run the
script. (Both this paragraph and the Headline held the [STD1b] figures —
274/99/55/99 = 528 — from 2026-08-13 until 2026-08-22, and went stale
together: one measurement transcribed into two places, which is exactly the
shape the sentence above warns about. If a third copy is ever wanted, cite
the Headline instead of transcribing it.)** The table also carries a short
manifest naming the rows whose
deletion the counts alone would not catch. Reproducing the `\v` bug's exact shape on a different
escape (silently decoding `\d` to a literal `d`) fails 2 reject checks and
**zero** corpus and codegen checks.

**Diagnostics fixed while surveying** (all were clean rejections already; none
was a miscompile — they simply failed to name a module, so the caller was told
their syntax was nonsense rather than what would implement it):

| construct | was | now |
|---|---|---|---|
| `(*ACCEPT)`, `(*SKIP)`, `(*CR)`, `(*script_run:…)`, all `(*…)` | `quantifier does not follow a repeatable item` | `(*...) requires module 'verbs'` — and since Q1, only for names PCRE2 actually has; `(*)` went back to the quantifier error, which is what PCRE2 says |
| `\K` | `unknown escape \K` | module `assertions` |
| `\c`, `\o` | `unknown escape` | module `misc` |
| `(?#…)` | module `modifiers` | module `comments` |
| `(?C…)` | module `modifiers` | module `callouts` |
| `(?&name)` | module `modifiers` | module `recursion` |
| `(?\|…)` | module `modifiers` | module `branch-reset` |

## Keeping this current

This report is only worth what its evidence is worth, so update it from
evidence, not from memory:

1. Re-read <https://www.pcre.org/current/doc/html/pcre2syntax.html>. PCRE2 adds
   syntax; a construct absent from this document is invisible to it. Compare
   section-by-section, since the page's own structure is this file's spine.
2. Run `bash tests/reject/run_reject_tests.sh`. Every `REJECTED` row above is
   only true because that table says so — if a row here has no counterpart
   there, it is an assertion, not a status.
3. When a module lands, move its rows off `REJECTED` and add corpus coverage
   in `tests/<module>/`. **The landing value is `OK-GATED`, not `OK`, unless
   the module is in the bare-default named set** (`std1` = {`classes`,
   `modifiers`} today, D37): `OK` says a bare `pcrec` compiles the construct,
   which is a stronger claim than a gated module has earned, and getting this
   wrong is not hypothetical — four rows (`\A \Z \z`, `\b \B \G`, `\K`,
   `(?m)`) read `OK` from their 2026-08-19 landing until 2026-08-22 while a
   bare `pcrec` refused all four, and their own annotations said "behind the
   gate" the whole time. Decide it by RUNNING a bare `pcrec` on the
   construct, not by reading the roadmap. Then update the reject table in the
   same change: a construct cannot be both supported and asserted to be
   rejected — but its rows MOVE rather than disappearing, into
   `reject_gated` pins: `--features none` for the bare-default half, and a
   gate-OPEN pin wherever the module is enabled and the pattern is still
   refused or still earns a particular diagnostic. The reject suite's floor
   check will notice either way.
4. Any new `DIVERGENCE-PROVEN` row must cite a measurement against libpcre2,
   not a doc reading, and get an entry in `docs/dev/known_issues.md` if it is not
   fixed in the same change.
5. Re-stamp "Last surveyed" and note what moved.

The `PLANNED`/`PLANNED-HARD` split is a judgement about pcrec's architecture,
not a schedule. Treat it as a prediction to be checked the way D18's option
predictions were — and record it here when one turns out wrong.

### How to read the generated index below (added 2026-08-19, [M6.2] repair slice; shrunk 2026-08-21, D65)

Its `status` and `roadmap` columns are the REGISTRY's two fields (`RegStatus`
and `Roadmap`, `src/core/internal.h`), and answer a fact about PCRE2 and
about pcrec's BASE grammar, never whether a construct's owning module has
been BUILT: `status` reads `REJECTED` for `RS_MODULE`, "the base grammar
does not implement this, and the `module` column names what does" — the same
reading for `\d`, `(?i)` and `\b` alike, whether or not any of the three
compiles today.

**AND THE `engines` COLUMN IS A CLAIM ABOUT THE CONSTRUCT, NOT ABOUT EVERY
PATTERN THAT SPELLS IT** — which matters for exactly two families today and is
worth one sentence here because a reader will otherwise take `vm` for a verdict
on their own pattern. For module `recursion`'s call rows, `vm` describes the
LINKED form: a call whose callee is in a CYCLE forces the VM for ever
(`^(a(?1)?b)$` generates `aⁿbⁿ`, which is not regular), while an ACYCLIC callee
is SPLICED — inlined exactly — and its pattern compiles to whichever engine the
hand-inlined equivalent would, so `--no-captures --engine=dfa '(a)(?1)'`
succeeds. Module `atomic-groups`' rows read the same way for the same reason
(`(?>a|ab)c` is VM-only, `[^"]*+"` is not, because the free discharge deletes a
cut it proves dead). The `(?1)` and `(?>...)` annotations below the survey
tables carry the full argument and the measurements.

**The `built` column (D65) answers that third question directly, per
construct** — `built`/`unbuilt`, or `—` where it does not arise
(`RS_BASE`/`RS_REJECTED` rows). It is DERIVED, not hand-maintained: measured
live, per row, by driving the row's own `syntax` through a gate-forced-open
doorway call (`pcrec_construct_built_status`, src/parse/syntax_dump.c) — the
same "cannot drift from the compiler because it is printed by it" property
SR-4 already gives the rest of this table. A construct read `REJECTED |
built` is base-grammar-absent but its module compiles it today (`\d`); one
read `REJECTED | unbuilt` genuinely does not compile yet, whatever `--features`
says (`(?=...)`, `\g<1>`, `(?R)`). **[M6.5.2], 2026-08-22**: `\k` and `(?J)`
were this paragraph's own examples until module `backrefs` landed and both
read `built`; the examples are replaced rather than deleted, because a
sentence about the column that names no unbuilt construct would stop
illustrating anything. `\g<1>` is a good replacement for a second reason —
it is one of two rows that lane ADDED born unbuilt, splitting the `\g`
doorway's SUBROUTINE half (module `recursion`) away from its BACKREFERENCE
half, which had shared one row and would otherwise have read `built` for a
construct nothing implements.

This column exists because its absence already misled once, and the history
is worth one sentence: the [M6.2] wave E lane read `REJECTED | planned` on
module `assertions`' rows as staleness SPECIFIC to that module and proposed
a whole-module registry flip; the repair slice refuted it (34 shipped-module
rows all read that way, so flipping eight would make the index inconsistent
rather than current, and would break the `RS_BASE => ROADMAP_NONE` pairing
`registry_check` enforces) and named the real fix as a registry BUILT-STATUS
field — `docs/design/registry_built_status_memo.md`, ratified wholesale as
D65 and built in the same session. Per-construct granularity was the point:
of the 34 rows the repair slice measured, 33 read `built` and one — `(?J)`,
whose letter then refused unconditionally, gate open or closed (a
PLANNED-LATER disposition, not a permanent one: see its own annotation
above and `docs/pcre2_options.md`'s `PCRE2_DUPNAMES` row, RIDES(M4/
captures), RATIFIED D38) — read `unbuilt`, a distinction a per-module flip
could never have expressed.

**THAT ONE ROW FLIPPED ON 2026-08-22 ([M6.5.2])**, and the flip is worth
recording because it is what the column was built to make visible: `(?J)` is
now `built`, its owner moved from `named-groups` to `backrefs` (ASK-1 — the
letter's MEANING is the rule for resolving a reference to a duplicated name,
and that machinery is backrefs'), and thirteen further rows flipped with it
(`\0`, `\1`..`\9`, `\k`, `\g`). Two rows were ADDED born `unbuilt`
(`\g<1>`, `\g'1'`, module `recursion`), which is the other half of the same
change: the `\g` doorway carries a BACKREFERENCE construct and a SUBROUTINE
CALL, the table had one row for both, and claiming the second would have been
a miscompile of the kind D26 tier 1 forbids. The tally moved 104 rows =
38 built + 60 unbuilt + 6 n/a to **106 = 52 + 48 + 6**, asserted EXACT by
`tests/registry/registry_check.c` rather than rendered into a string.

<!-- BEGIN GENERATED: registry construct index (SR-4) -->

<!-- Generated by tests/registry/compliance_section.py from
     `pcrec --list-syntax`. Do not edit by hand: `make test` fails
     on drift. Add a construct by adding a row to
     src/parse/registry.c, then re-run with --write. -->

## Registry construct index (generated)

Every non-base construct pcrec knows, as the parser itself sees it — 135 rows from one declarative table (D24), rendered as 97 lines because a construct with several SPELLINGS gets one line naming them all (D71 item 3). The prose sections above carry the analysis; this is the inventory, and it cannot drift from the compiler because it is printed by it.

`built` on a multi-spelling line is ANDed over its spellings: the line reads `built` only if every one of them does.

| doorway | syntax | status | built | roadmap | module | engines | PCRE2 semantics |
|---|---|---|---|---|---|---|---|
| after `\` | `\d` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any decimal digit |
| after `\` | `\D` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any character that is not a decimal digit |
| after `\` | `\s` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any whitespace character |
| after `\` | `\S` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any character that is not whitespace |
| after `\` | `\w` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any word character (letter, digit or underscore) |
| after `\` | `\W` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any character that is not a word character |
| after `\` | `\h` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any horizontal whitespace character |
| after `\` | `\H` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any character that is not horizontal whitespace |
| after `\` | `\v` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any vertical whitespace character (NOT vertical tab; python re disagrees) |
| after `\` | `\V` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any character that is not vertical whitespace |
| after `\` | `\N` | `REJECTED` | `built` | planned | `classes` | dfa|vm | any character except newline (PCRE2 forbids it inside a class) |
| after `\` | `\N{name}` | `AGREES-REJECT` | — | never | — | — | \N{name} — PCRE2 states it does not support this Perl construct |
| after `\` | `\N{U+0041}` | `REJECTED` | `unbuilt` | planned | `unicode-props` | dfa|vm | a Unicode code point by number — PCRE2 error 193 outside UTF mode, which is recognition, not rejection |
| after `\` | `\b` | `REJECTED` | `built` | planned | `assertions` | dfa|vm | word boundary — but inside a class it is BASE syntax: backspace (0x08) |
| after `\` | `\B` | `REJECTED` | `built` | planned | `assertions` | dfa|vm | not a word boundary |
| after `\` | `\A` | `REJECTED` | `built` | planned | `assertions` | dfa|vm | start of subject |
| after `\` | `\Z` | `REJECTED` | `built` | planned | `assertions` | dfa|vm | end of subject, or before a final newline |
| after `\` | `\z` | `REJECTED` | `built` | planned | `assertions` | dfa|vm | end of subject |
| after `\` | `\G` | `REJECTED` | `built` | planned | `assertions` | dfa|vm | first matching position in the subject |
| after `\` | `\K` | `REJECTED` | `built` | planned | `assertions` | vm | reset the reported start of the match |
| after `\` | `\k<name>` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference by name: \k<n> \k'n' \k{n} — literal 'k' inside a class |
| after `\` | `\g{-1}` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference by number or relative position: \g1 \g{-1} \g{name} — literal 'g' inside a class |
| after `\` | `\g<1>` | `REJECTED` | `built` | planned | `recursion` | vm | subroutine call into a group by number or name: \g<1> \g<name> — NOT a backreference (it re-runs the group's pattern) — also spelled `\g<0>`, `\g<01>` |
| after `\` | `\g'1'` | `REJECTED` | `built` | planned | `recursion` | vm | subroutine call into a group, quoted spelling: \g'1' \g'name' — NOT a backreference — also spelled `\g'0'`, `\g'01'` |
| after `\` | `\p{L}` | `REJECTED` | `unbuilt` | planned | `unicode-props` | dfa|vm | a character with the given Unicode property |
| after `\` | `\P{L}` | `REJECTED` | `unbuilt` | planned | `unicode-props` | dfa|vm | a character without the given Unicode property |
| after `\` | `\Q` | `REJECTED` | `unbuilt` | planned | `quoting` | dfa|vm | begin literal quoting, until \E |
| after `\` | `\E` | `REJECTED` | `unbuilt` | planned | `quoting` | dfa|vm | end literal quoting begun by \Q |
| after `\` | `\R` | `REJECTED` | `unbuilt` | planned | `misc` | dfa|vm | any Unicode newline sequence |
| after `\` | `\X` | `REJECTED` | `unbuilt` | planned | `misc` | dfa|vm | a Unicode extended grapheme cluster |
| after `\` | `\C` | `REJECTED` | `unbuilt` | planned | `misc` | dfa|vm | one data unit (byte), even in UTF mode |
| after `\` | `\cX` | `REJECTED` | `unbuilt` | planned | `misc` | dfa|vm | control character: \cX is X xor 0x40 |
| after `\` | `\o{101}` | `REJECTED` | `unbuilt` | planned | `misc` | dfa|vm | character with the given octal code |
| after `\` | `\0` | `REJECTED` | `built` | planned | `backrefs` | dfa|vm | octal escape \0dd — never a backreference (there is no group 0) |
| after `\` | `\1` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference to capture group 1 (PCRE2 error 115 if no such group) |
| after `\` | `\2` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference to capture group 2 (PCRE2 error 115 if no such group) |
| after `\` | `\3` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference to capture group 3 (PCRE2 error 115 if no such group) |
| after `\` | `\4` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference to capture group 4 (PCRE2 error 115 if no such group) |
| after `\` | `\5` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference to capture group 5 (PCRE2 error 115 if no such group) |
| after `\` | `\6` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference to capture group 6 (PCRE2 error 115 if no such group) |
| after `\` | `\7` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference to capture group 7 (PCRE2 error 115 if no such group) |
| after `\` | `\8` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference to capture group 8 (PCRE2 error 115 if no such group) |
| after `\` | `\9` | `REJECTED` | `built` | planned | `backrefs` | vm | backreference to capture group 9 (PCRE2 error 115 if no such group) |
| after `\` | `\a` | `OK` | — | — | — | dfa|vm | alarm, hex 07 |
| after `\` | `\e` | `OK` | — | — | — | dfa|vm | escape, hex 1B (not backslash-escape, the ASCII ESC character) |
| after `\` | `\f` | `OK` | — | — | — | dfa|vm | form feed, hex 0C |
| after `\` | `\n` | `OK` | — | — | — | dfa|vm | linefeed, hex 0A |
| after `\` | `\r` | `OK` | — | — | — | dfa|vm | carriage return, hex 0D |
| after `\` | `\t` | `OK` | — | — | — | dfa|vm | tab, hex 09 |
| after `\` | `\x41` | `OK` | — | — | — | dfa|vm | hex, exactly 2 digits (bare \x; \x{...} requires module 'unicode-props') |
| after `(?` | `(?:...)` | `OK` | — | — | — | dfa|vm | non-capturing group |
| after `(?` | `(?=...)` | `REJECTED` | `built` | planned | `lookaround` | vm | positive lookahead — also spelled `(*pla:a)`, `(*positive_lookahead:a)` |
| after `(?` | `(?!...)` | `REJECTED` | `built` | planned | `lookaround` | vm | negative lookahead — also spelled `(*nla:a)`, `(*negative_lookahead:a)` |
| after `(?` | `(?<=...)` | `REJECTED` | `built` | planned | `lookaround` | vm | positive lookbehind — also spelled `(*plb:a)`, `(*positive_lookbehind:a)` |
| after `(?` | `(?<!...)` | `REJECTED` | `built` | planned | `lookaround` | vm | negative lookbehind — also spelled `(*nlb:a)`, `(*negative_lookbehind:a)` |
| after `(?` | `(?<*a)` | `REJECTED` | `built` | planned | `lookaround` | vm | non-atomic positive lookbehind — the (? spelling of (*naplb:...) — also spelled `(*naplb:a)`, `(*non_atomic_positive_lookbehind:a)` |
| after `(?` | `(?<name>a)` | `REJECTED` | `built` | planned | `named-groups` | dfa|vm | named capture group (?<name>...) — the lookbehinds take = ! * and have their own rows |
| after `(?` | `(?'name'...)` | `REJECTED` | `built` | planned | `named-groups` | dfa|vm | named capture group, Perl-style quoting |
| after `(?` | `(?P<name>a)` | `REJECTED` | `built` | planned | `named-groups` | dfa|vm | python-style named capture group |
| after `(?` | `(?P=n)` | `REJECTED` | `built` | planned | `backrefs` | vm | python-style backreference to a named group |
| after `(?` | `(?P>n)` | `REJECTED` | `built` | planned | `recursion` | vm | python-style subroutine call into a named group |
| after `(?` | `(?PX)` | `AGREES-REJECT` | — | never | — | — | only (?P< (?P= and (?P> exist — every other byte after (?P is PCRE2 error 141 |
| after `(?` | `(?>...)` | `REJECTED` | `built` | planned | `atomic-groups` | vm | atomic (non-backtracking) group |
| after `(?` | `(?*a)` | `REJECTED` | `built` | planned | `lookaround` | vm | non-atomic positive lookahead — the (? spelling of (*napla:...) — also spelled `(*napla:a)`, `(*non_atomic_positive_lookahead:a)` |
| after `(?` | `(?#...)` | `REJECTED` | `unbuilt` | planned | `comments` | dfa|vm | comment, discarded up to the next ')' |
| after `(?` | `(?C1)` | `REJECTED` | `unbuilt` | planned | `callouts` | vm | callout to user code: (?C) (?C1) (?C{text}) -- PLANNED (D36): M4-hosted, VM-only; the compiled DFA erases the pattern positions a callout fires at |
| after `(?` | `(?\|...)` | `REJECTED` | `unbuilt` | planned | `branch-reset` | vm | branch reset group: alternatives reuse the same capture numbers |
| after `(?` | `(?(1)a\|b)` | `REJECTED` | `unbuilt` | planned | `conditionals` | vm | conditional group (?(condition)yes\|no) |
| after `(?` | `(?(DEFINE)(?<w>a))` | `REJECTED` | `built` | planned | `recursion` | dfa|vm | define-only group: the body never runs where it is written and exists to be called -- the same thing (?:BODY){0} means |
| after `(?` | `(?&name)` | `REJECTED` | `built` | planned | `recursion` | vm | recurse into the named group |
| after `(?` | `(?R)` | `REJECTED` | `built` | planned | `recursion` | vm | recurse the whole pattern |
| after `(?` | `(?0)` | `REJECTED` | `built` | planned | `recursion` | vm | recurse the whole pattern -- the whole DIGIT RUN is read as decimal, so (?0) and (?00) are the root while (?01) is group 1 — also spelled `(?00)` |
| after `(?` | `(?1)` | `REJECTED` | `built` | planned | `recursion` | vm | recurse into capture group 1 — also spelled `(?2)`, `(?3)`, `(?4)`, `(?5)`, `(?6)`, `(?7)`, `(?8)`, `(?9)`, `(?10)`, `(?01)` |
| after `(?` | `(?+1)(a)` | `REJECTED` | `built` | planned | `recursion` | vm | relative subroutine call to the Nth group to the RIGHT — also spelled `(?+2)(a)(b)` |
| after `(?` | `(a)(?-1)` | `REJECTED` | `built` | planned | `recursion` | vm | relative subroutine call to the group 1 to the LEFT — also spelled `(a)(?-01)`, `(a)(a)(?-2)`, `(a)(a)(a)(?-3)`, `(a)(a)(a)(a)(?-4)`, `(a)(a)(a)(a)(a)(?-5)`, `(a)(a)(a)(a)(a)(a)(?-6)`, `(a)(a)(a)(a)(a)(a)(a)(?-7)`, `(a)(a)(a)(a)(a)(a)(a)(a)(?-8)`, `(a)(a)(a)(a)(a)(a)(a)(a)(a)(?-9)`, `(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)(?-10)` |
| after `(?` | `(?[[a]])` | `REJECTED` | `unbuilt` | planned | `extended-classes` | dfa|vm | extended character class with set operations: (?[[a]&&[b]]) (?[[a]-[b]]) |
| after `(?` | `(?)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | empty option setting |
| after `(?` | `(?-i)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | unset options: (?-i) (?-im:...) |
| after `(?` | `(?^)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | reset all options to their default |
| after `(?` | `(?J)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | allow duplicate names (PCRE2_DUPNAMES) |
| after `(?` | `(?U)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | ungreedy: invert the greediness of quantifiers |
| after `(?` | `(?a)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | ASCII-restrict class escapes (PCRE2_EXTRA_ASCII_*) |
| after `(?` | `(?i)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | caseless |
| after `(?` | `(?m)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | multiline: ^ and $ match at internal newlines |
| after `(?` | `(?n)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | no auto-capture: plain (...) stops capturing |
| after `(?` | `(?r)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | restrict caseless matching to within ASCII or non-ASCII |
| after `(?` | `(?s)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | dotall: . matches newline |
| after `(?` | `(?x)` | `REJECTED` | `built` | planned | `modifiers` | dfa|vm | extended: ignore unescaped whitespace and # comments |
| after `(?` | `(?q)` | `AGREES-REJECT` | — | never | — | — | no construct begins with this byte — PCRE2 error 111 |
| after `(*` | `(*ACCEPT)` | `REJECTED` | `unbuilt` | planned | `verbs` | vm | backtracking verb ((*SKIP), (*ACCEPT)), start-of-pattern option ((*CR), (*UTF)) or script run ((*script_run:...)) |
| after `[` in a class | `[[:alpha:]]` | `REJECTED` | `built` | planned | `classes` | dfa|vm | POSIX character class |
| after `[` in a class | `[[.a.]]` | `AGREES-REJECT` | — | never | — | — | POSIX collating element — PCRE2 rejects it, and so must we |
| after `[` in a class | `[[=a=]]` | `AGREES-REJECT` | — | never | — | — | POSIX equivalence class — PCRE2 rejects it, and so must we |
| quant-suffix | `a*+` | `REJECTED` | `built` | planned | `atomic-groups` | vm | possessive `*` — `X*+` is PCRE2's own spelling of `(?>X*)` |
| quant-suffix | `a++` | `REJECTED` | `built` | planned | `atomic-groups` | vm | possessive `+` — `X++` is PCRE2's own spelling of `(?>X+)` |
| quant-suffix | `a?+` | `REJECTED` | `built` | planned | `atomic-groups` | vm | possessive `?` — `X?+` is PCRE2's own spelling of `(?>X?)` |
| quant-suffix | `a{1,2}+` | `REJECTED` | `built` | planned | `atomic-groups` | vm | possessive braces — `X{n,m}+` is `(?>X{n,m})`; also {n}+ {n,}+ {,n}+ |

<!-- END GENERATED -->
