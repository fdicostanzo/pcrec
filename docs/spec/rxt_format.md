# The `.rxt` test format and driver protocol

This is the contract for `.rxt`, pcrec's test-corpus format, and for the
harness that runs it: what a `.rxt` file may say, what `tests/harness/run.sh`
does with each line, and what `tests/harness/driver.c` prints and exits with.
Read this before adding a `.rxt` file or a new component test directory.

**THE FORMAT HAS THREE READERS AND THIS DOCUMENT IS THE CONTRACT ALL
THREE ANSWER TO**: `pcrec` itself (a file operand / `--list-source`
[REL-1.10], the only reader of a file's HEAD), `tests/harness/run.sh`, and
`tests/harness/verify_rxt.py`. Every claim below is checked by RUNNING
them rather than by reading a design; where a stated rule and a reader
disagreed, the reader won — see "Drift found and fixed" at the bottom.
Where a rule is enforced by only some of the three, this document says
which, and `pcrec --list-schema`'s `validated_by` column is the
per-line-kind answer a consumer fetches instead of remembering.

Battery composition (`make test`'s eight scripts, runtimes, the sanitizer
battery, the `timeout` binary, `PROCS`/load-guard mechanics) is process
record, not contract, and stays in `docs/testing.md`.

## The `.rxt` format

A `.rxt` file has a **HEAD** and a **BODY**. The body is a flat,
line-oriented list of **pattern blocks**: each block starts with a
`pattern` line and is followed by zero or more expectation and directive
lines that apply to that pattern, until the next `pattern` line or end of
file. The head is a list of file-level declarations.

**The head ENDS at the first `pattern` line, and nothing file-level may
appear after it.** That is the whole boundary rule, and everything below
depends on it: a reader of any block needs to look in exactly one other
place — the top of the file — and that place is bounded. A file whose
first non-comment line is `pattern` has NO head, and behaves exactly as
it did before the head existed. Every file in `tests/` is of that shape
today.

A file may have a head and NO pattern blocks (a pure library file is
exactly that shape). That is legal, and it is a DISTINCT OBSERVABLE from
a file the harness could not read: `tests/harness/run.sh` runs zero
blocks and reports its existing "no pattern blocks parsed from file"
failure, on its own exit status, while a file whose head does not PARSE
is reported as a harness failure carrying pcrec's own diagnostic. The two
can never be confused.

### The head

Eleven file-level declarations exist in this build, and the authoritative
roster is `pcrec --list-schema`'s `file`-scope rows rather than this
table — which restates them for a reader, and says what each MEANS:

| declaration | means |
|---|---|
| `lib "path"` / `lib <store>` | a subpattern library this file draws definitions from. The path reference has C's own two spellings: `"local"` and `<store-name>`. **The `"path"` form is RESOLVED** (against the source file's own directory, then each `pcrec --lib-path` in order) and refused by name if it names no readable file; **since [DD-13b.W1.3] its CONTENTS ARE READ** when a target is built (`--source`): the library's named definitions — and nothing else, not its configs, targets or cases — join the lookup a pattern's call resolves against ("The delivering call" below). `--list-source` still reads only this file's own bytes. `<store-name>` is refused as NOT IN THIS BUILD |
| `target [<prefix>] = <definition> [with <c1,c2>]` | an artifact to build: its symbol prefix, the definition it is built from, and the configs it is built under. **BUILT** since [DD-13b.W1.2] — see "Building from a source file" below. **The prefix may be OMITTED** (`target = <definition>`), which derives it from the definition name |
| `config <name> [from <c1,c2>]` | a named build configuration, with an indented body |
| `description <text>` | a machine-readable prose field — a FIELD, not a comment, so a script can summarize what a file holds. `#` comments go back to being operational notes. **At most ONE per file**: a second file-level `description` is refused by name, naming the earlier line |
| `include "path"` | **[DD-13b.W23.3, resolution DD-13b.W23.3a]** a `.rxt` fragment this file draws blocks from. The path is DOUBLE-QUOTED and that is the format's only path spelling — `include <store>` is refused by value shape, unlike `lib`, which carries C's two spellings for historical reasons. **UNLIKE EVERY OTHER HEAD DECLARATION, `pcrec` DOES open something for this one**: the path is resolved (relative to the referencing file's own directory, `realpath(3)`) AT PARSE TIME, so `--list-source`'s row carries the path AS WRITTEN in `value` and the RESOLVED REAL PATH in `name` — the one deliberate exception to "a pure function of the file's own bytes", because `--list-source` is the only call the harness ever makes over an `include` line and a resolution only compiling the file could see would leave it nothing to read. A path naming no readable file, or a second `include` resolving to a file already named earlier in this same file, IS a parse error here (value-shape / schema-constraint respectively). Repeatable |
| `vocabulary <key> <v1> <v2> …` | **[DD-13b.W23.3]** declares a CLOSED SET named `<key>`, whose members are the remaining words. It is how a FILE declares the members of a schema `closed` constraint whose row names no members (see "The `constraints` column's clause spellings" below); the keys it can close are `tag`'s own keys, `under`'s convention and `variant`'s `kind`. The key is an identifier; a set with no members is refused by name, because a closed set nothing satisfies can only ever refuse. **One line per key**: a second `vocabulary` for a key already declared is refused, naming the earlier line. Its value may use the block-scalar continuation form (`vocabulary <key> \|` with the members on indented lines) |
| `oracle <engine-ref>[/<version>]` | **[DD-13b.W23.3]** the file-level default oracle (see "Oracle verification"). **At most ONE per file** |
| `tag <item>{, <item>}` | **[DD-13b.W23.3]** file-level classification. Each item is a bare LABEL or a `key=value`, and neither half may carry whitespace. Repeatable |
| `use <c1,c2>` | **[DD-13b.W23.3]** a config list, in `with`/`from`'s own `config-list` grammar. Parsed and validated as a list; it composes nothing in this build. Repeatable |
| `analysis <name>` | **[FINDINGS] B0** a named ANALYSIS — a BUNDLE of subject-statistics data blocks, with an indented body (see "`analysis` — the bundle" below). The name is LOWERCASE (`[a-z][a-z0-9_-]*`), unique in the file. Repeatable. It REPLACES the file-level `freq <name>` data block, which is withdrawn: a `freq` block now lives inside a bundle |
| `ext <consumer>` | **[DD-13b.W23.3]** an AUX block: consumer-namespaced data pcrec carries and does not interpret (see "`ext` — the aux production" below). Repeatable |

A `config` body holds indented `pcrec` (raw pcrec flags), `flags`,
`features`, `encoding`, `engine`, `tune`, `budget` and `analysis` lines —
the same productions a pattern block's own directives use, so the two
cannot disagree about what `budget frames=` means. **`analysis <name>`
names ONE analysis (a bundle)** — at most one per config body, in the
bundle-name grammar; its name is not resolved in this build ([FINDINGS]
B2 resolves it). **The `pcrec` line may not carry `--analysis`** (refused
at parse): a config names its analysis with its own `analysis` line, so
the choice is visible in the file. **[REL-1.10]/D118 addendum (iv)**: the `pcrec`
line's raw text is re-parsed by the CLI's own option parser
(`docs/spec/cli.md` §1.1's config-block paragraph), so a literal pattern on
that line is spelled `--pattern 'X'` there too, exactly as on the command
line — no corpus fixture carries one today.

**NOT IN THIS BUILD, AND THE LIST IS DERIVED RATHER THAN HAND-KEPT**
([DD-13b.W23.1]): every line kind the format has is a row in a declared
schema (`pcrec --list-schema`), and a row whose `wave` column is above
the one this build implements is recognised and refused **by name, as
NOT IN THIS BUILD** — never as unknown, which would send a reader
hunting a typo in a word they just read in this document. **At this
build the derived list is EMPTY**: `--list-schema`'s `# wave-built:`
trailer names the wave every non-reserved row carries, so there is
nothing above it. The refusal is kept for the next wave's rollout, and
the emptiness is a fact a reader can fetch rather than a claim to
believe.

A WITHDRAWN production cannot linger in that list either — it has no
row, so it has no wave, so it refuses as an unknown token in its scope,
which is the truth about it. `config … testee` and `config … option`
left the format that way (D99): they were once named here as later-wave
keywords and are not keywords at all any more.

**`version` is the one word that is neither**, and "The schema and its
surface" below states it.

### The delivering call — reaching a definition's exported groups

**[DD-13b.W1.3]** A definition's `export` line says what it offers; a call
says what it takes. Three forms, and the plain one is PCRE2's own:

| written in a pattern | meaning |
|---|---|
| `(?&name)` | the plain call: run the definition, keep nothing. PCRE2's own capture-transparent meaning, unchanged |
| `(?&site=name)` | DELIVER: the definition's exported groups become the caller's, named `site.group` |
| `(?&=name)` | the same, with the definition's own name as the site |
| `(?&*=name)` | DELIVER FLAT: the exported groups become the caller's under their own names |

All three delivering spellings were checked against libpcre2 10.46 before
adoption and are refused by it, so adopting them changes the meaning of no
legal pattern (the constraint `format_design.md` §1.5 states, and the one
that disqualified an earlier candidate PCRE2 turned out to accept).

- **A site is a scope.** Two delivering calls of one definition under two
  site names give two independent sets of groups.
- **A clash is refused by name** — a flat import landing on a group the
  caller already has, two flat imports exporting one name, or two sites
  sharing a name.
- **A delivering call whose target is a group in the SAME pattern is
  refused.** Delivery is a definition's interface; a local group has no
  export list and is already the caller's own.
- **A delivering call on a RECURSIVE definition is refused**, because
  delivery needs the callee written out at the site.
- What a caller then reads is `docs/spec/match_api.md` §6's "Composition".

### Building from a source file

`pcrec -o OUT FILE` builds this file's `target` declarations — a
positional FILE OPERAND, the retired `--source FILE` flag's own mechanism
since [REL-1.10]/D118. `docs/spec/cli.md` §1.1 is the command-line
contract and states the `-o` forms, `--target`, `--lib-path`/`-I` and the
precedence rules. What belongs to the FORMAT rather than to the CLI is
this:

- **A `target`'s definition is a pattern block's `name`**, which lives in
  the FILE namespace — the same namespace a block's `name` is unique in.
  A `target` may name a block that appears later in the file: the head
  precedes the body and resolution is a whole-file pass.
- **A `target`'s PREFIX is a C identifier** and is never mapped. Written
  out, it is exactly what the emitted symbols carry.
- **`target = <definition>` DERIVES the prefix from the definition
  name**, by replacing every `-` and `.` with `_` and copying every other
  byte. This is the form an exporter writes: a set of patterns whose ids
  carry `-` becomes a source with one `target =` row per pattern and no
  hand-written mapping anywhere.
- **Two definitions that map to one prefix are REFUSED**, and the
  diagnostic names BOTH definitions, the line of the first, and the
  prefix they share. The mapping is deliberately not injective — `a-b`
  and `a.b` both give `a_b` — because a mapping that could not collide
  would have to mangle a name its author wrote; the refusal is where that
  is paid for, and an explicit `target <prefix> = <definition>` on either
  one settles it. Writing one prefix twice is refused with the older
  "duplicate target prefix" sentence, which is the same collision seen
  from the side where naming both definitions would say nothing new.
- A derived prefix is still subject to every rule a written one is,
  including the symbol-prefix length bound in `docs/spec/limits.md`.
- **No `target` and exactly ONE UNNAMED pattern block means `target rx`.**
  That is what makes every file written before this format grew a head
  buildable without declaring anything.
- **No `target` and anything else builds NOTHING.** The file is a library
  of definitions; `pcrec` says so and exits 0. It is not an error, and it
  is a different outcome from a file `pcrec` refuses.
- **A FILE WITH NO `target` AND NO `config` PARSES, BUILDS NOTHING, AND
  EXITS 0 — PERMANENTLY, AS A CONTRACT.** This is the shape a set of
  patterns carried purely as data has: definitions, expectations,
  provenance, tags, aux blocks and nothing that names an artifact. A
  consumer may rely on it, and on the distinction it rests on: building
  nothing is a successful outcome that writes no output file, and it is
  never reported as, nor confusable with, a file `pcrec` could not read
  (which exits 1 with a diagnostic naming the file, the line and the
  construct). The behaviour has always shipped; this sentence makes it a
  promise rather than an observation, so that a file format used as a
  data carrier cannot be broken by a later build deciding a target is
  mandatory.
- **One definition may be named by several targets**, which is the point
  of the `with` list: three targets naming one definition under three
  configs are three artifacts with three prefixes and ONE
  `rx_info.name` (`docs/spec/match_api.md` §6).
- **`features` composes as a UNION** of the target's configs and the
  block's own line, unless the block wrote `features only`, in which case
  the block's list stands alone. `flags`, `encoding`, `engine` and
  `budget` are more-specific-wins: the block's value beats the configs'.

**THE HARNESS BUILDS THEM TOO, as a control rather than as a second set of
expectations.** For a head-bearing file, `tests/harness/run.sh` builds every
target that names a block and requires each to answer that block's own
`m`/`n`/`ms`/`ns` cases EXACTLY as the block's own compile did. So a `.rxt`
author writes no expectation per target, and a config that changed an
ANSWER — rather than only how one is found — would make that control red
rather than pass silently.

### Lexical rules — the file's shape, in TWO LAYERS

**[DD-13b.W23.1]** The format's shape is stated as two layers with a thin,
declared interface between them:

- **the STRUCTURE layer** — how a reader with NO keyword table recovers the
  file's tree from syntax alone: blocks, sub-blocks, line membership.
- **the SCHEMA layer** — which line kinds exist, in which scope, what each
  takes, and whether a recovered tree is VALID. It is a declared table
  (`pcrec --list-schema`, below), not a set of rules this document lists.

**The split's test, and it is the whole point:** keywords and the schema say
what the structure MEANS and whether it is valid; they NEVER decide where
structure begins or ends. The structure layer takes exactly THREE
parameters from the schema, and all three are one `--list-schema` query, so
a generic reader FETCHES them instead of hard-coding them.

#### S0 — the four line classes

| class | what it is | what it does |
|---|---|---|
| **BLANK** | the EMPTY line — zero bytes — and nothing else | closes every open attachment, returning to indent 0 |
| **WHITESPACE-ONLY** | nothing but spaces and tabs, at least one | **INERT**: no indent is read off it, it attaches to nothing and nothing attaches to it, no first token is dispatched. A reader steps over it. Inside an opaque region it is BYTES, which makes it the format's only paragraph break |
| **COMMENT** | `#` in **column 1**. A `#` anywhere else is data | closes attachment exactly as a BLANK does — the same rule, not a carve-out |
| **CONTENT** | everything else | its INDENT is its count of leading **SPACES** |

**INDENTATION IS SPACES.** A leading TAB does not open an indent and is
refused BY NAME. A tab inside a VALUE is still data and is untouched. Two
spellings of indentation have no agreed depth between them, so a file
mixing them has no defined tree under any depth rule.

The one comment with meaning is `# pcre2-only` immediately before a
`pattern` line (see "Oracle verification").

#### S1 — attachment

A CONTENT line whose indent is GREATER than the immediately preceding
CONTENT line's **attaches to it as a CHILD**. Equal indent makes them
SIBLINGS. Lesser indent closes back to the nearest enclosing level with
that indent; an indent matching no enclosing level is a structure error, as
is an indented line following a blank or a comment, or one with nothing
before it.

**What may be indented under a kind is the schema's `children` column and
nothing else.** There is ONE attachment rule and it is the same rule in the
head and in a block: a `config` body, a block scalar's own lines and a
sub-block's attributes are all S1. The head/body indentation asymmetry
earlier versions of this document stated is DELETED, not narrowed.

#### S2 — grouping

Among SIBLINGS, a line whose first token is a member of the **BLOCK-OPENER
SET** starts a group that absorbs the following siblings until the next
opener at that level or the end of the enclosing scope. The opener set is
closed and declared: it is **structure-layer parameter 1**, the schema rows
with `opens_group: true`, today `pattern` and `pattern-esc`.

#### S3 — opaque regions

A CONTENT line opens an **OPAQUE REGION** when all three hold: its KIND is
prose-region-opening (**structure-layer parameter 2**, the schema rows
carrying `value: prose` AND `children: prose`, read as a PAIR); its value,
after trailing spaces and tabs are TRIMMED, is exactly the single byte `|`;
and it is not inside an open subtree.

Its EXTENT is structural and is the only structural fact about it: the
region runs from the next line up to, and not including, the FIRST of a
CONTENT line whose indent is <= the opener's, a BLANK line, or a COMMENT
line. Every line inside is BYTES — S0 does not classify it for dispatch, S1
does not attach it, S2 does not test it — so **a reader can find a region's
end without tokenising a single line inside it**.

Inside a region an indented `#` is PROSE and ragged indentation is legal
prose shape; outside one the indented-`#` refusal is unchanged.

**Decoding the region into a value.** The region's DEDENT DEPTH is set once,
by the FIRST line's own leading whitespace, and every line's decoded text is
that same byte count stripped from its front — so a line indented DEEPER
than the first keeps its relative indentation (`prose_ragged`'s shape) and a
WHITESPACE-ONLY line, having nothing but whitespace to strip, decodes to an
empty line regardless of its own width (the format's only paragraph break).
**A CONTENT line indented LESS than the first — one with a non-whitespace
byte inside the dedent depth — is REFUSED, class `value-shape`, naming both
the line's own indent and the depth the first line set**, rather than having
that byte silently stripped away: a byte count cannot dedent a line shorter
than itself without deleting content, and this format never loses bytes
silently. All three parsers enforce this identically (`prose_dedent.rxtin`/
`prose_dedent_body.rxtin`).

#### The OPEN SUBTREE — structure-layer parameter 3

A CONTENT line whose kind carries `children: tree` roots an **open
subtree**: itself and every line S1 attaches below it, transitively, to any
depth. Inside that subtree, and only there, **S2's opener set is EMPTY** (no
line starts a group, whatever its first token) and **S3 NEVER OPENS** (a
trimmed bare `|` there is the literal value `|`). Both are properties of the
SUBTREE and never of a keyword: a reader fetches `children` for the line it
is attaching under, and the value `tree` is what switches the two devices
off.

#### The SCHEMA layer

- **A line kind is its first whitespace-delimited token**, and a token with
  no schema row IN ITS SCOPE is a HARD ERROR that NAMES the scope — never a
  silent no-op, never a comment. Nothing is a keyword everywhere: `pcrec` is
  a `config`-body line and not a block one; `perr` is a block line and not a
  head one.
- **Cardinality is declared per row.** `one` requires exactly one
  occurrence in its scope; `at-most-one` refuses a second, naming the
  earlier line; `repeat` permits one; `accumulate` joins (`budget`
  accumulates over its FIELD set, which is why `budget steps=` and `budget
  frames=` are legal in one block and a repeated FIELD is not).
- **Constraints** are drawn from a closed vocabulary of SEVEN kinds:
  `required`, `required-if`, `forbidden-if`, `exactly-one-of`, `closed`,
  `unique-by`, `functional-binding`. The vocabulary is what a row MAY
  declare, not what some row does: `functional-binding` has no row in this
  build (its one rule, the subject id's, lives on a CASE line, and this
  parser recognises case lines without reading them — see "Named subjects"
  below, which states who enforces it). A reader takes the set of kinds
  actually in use from the dump, not from this sentence.
- **WHEN each constraint is answered is part of the contract**, because it
  decides what a refusal can name. `closed` and `unique-by` are answered
  AT THE LINE — which is what lets a duplicate-key refusal name both
  lines. Every other kind is answered when the SCOPE CLOSES, because each
  of them names a SIBLING and siblings arrive in any order (`url` may
  precede the `source authored` that forbids it), and because `required`
  cannot be answered before the scope's last line has been read. Such a
  refusal is reported at the line that CLOSED the scope (or at the file's
  last line), because where the offence is a MISSING line there is no
  offending line to point at — the one exception being `forbidden-if`,
  which has an offending line and names it.
- The whole table is printed by `pcrec --list-schema` (see "The schema and
  its surface" below), and the parser is its reader: one derivation, two
  readers, so a dump that disagrees with the parser is not expressible.

- **TRAILING WHITESPACE after a directive's value is ignored.** A
  directive whose value is a token or a list (`flags`, `features`,
  `engine`, `budget`, `encoding`, `name`, `lib`, and the `config`/`target`
  cascades `with` and `from`) means the same thing with or without spaces
  after it. **Three** productions are REST-OF-LINE and keep every byte,
  because there the trailing space is data: `pattern`, `description`,
  and a `config` body's `pcrec` line (the raw flag text passed to a
  build) (r46sem finding 21, FIXED — the list above previously omitted
  `lib`/`with`/`from` from the trimmed set, whose code already trimmed
  `lib` but not `with`/`from`, and omitted `pcrec` from the rest-of-line
  set the code already gave it correctly).
- **A TAB IS REFUSED INSIDE A `with`/`from` CONFIG LIST** (r46sem finding
  2, FIXED), never accepted as a separator alongside a space. `config
  <name> from <c1,c2>` and `target <prefix> = <def> [with <c1,c2>]`'s
  lists both refuse a literal tab anywhere in the list text: a tab there
  is never what an author means, and letting one through would have to
  reach `--list-source`'s columns 13/14 (`with`/`from`) unescaped, since
  those two columns are not among the three the dump escapes.
- **`pattern` takes exactly one SPACE before its regex**, not arbitrary
  whitespace: the pattern text is rest-of-line verbatim from the byte
  after that space, so the separator cannot be part of it and a tab there
  is a hard error.
- **One line, one value — with exactly one exception, the BLOCK SCALAR.**
  A line whose value is prose may write `<kind> |` and continue on
  indented lines; newlines are preserved and the value ends at the first
  non-indented line. The exception is a property of the VALUE production
  rather than of any one keyword, so a second prose field inherits it
  rather than inventing it. **It is a HEAD form only**: a pattern block's
  lines are not indented, so a block's `description` takes the one-line
  form, and `|` there is refused by name.


- Blank lines and lines starting with `#` are ignored. Comments are
  WHOLE-LINE ONLY — a `#` after case fields is not a comment, it makes the
  line unparseable (a pattern or subject may legitimately contain `#`, so the
  parser never guesses where data ends and commentary begins).
- `pattern <regex>` — starts a new block. `<regex>` is everything after the
  first space on the line, taken verbatim to the end of the line (no
  quoting, no escaping). **A NUL byte anywhere in the file is refused**, by
  name, naming the file and the 1-based line it falls on — never silently
  truncated. The format is line-oriented text and NUL has no
  representation in any production today: the escaped spelling below
  refuses `\x00` on its own, separate grounds, so no production expresses
  a NUL pattern and this refusal narrows nothing.
- `pattern-esc "<quoted>"` — **[DD-13b.W23.3] THE SECOND BLOCK STARTER.**
  It starts a block exactly as `pattern` does, and is the second and only
  other member of the block-opener set (S2). Its value is DOUBLE-QUOTED
  text and the block's pattern is the DECODED bytes.

  - **The escape vocabulary is the format's OWN subject vocabulary and
    there is no second vocabulary** — the seven escapes of the
    `<subject>` table below, `\" \\ \n \t \r \f \v \xHH`, byte for byte.
    An unknown escape, a trailing backslash, an unescaped `"` inside the
    text, an unquoted operand, and `\x` without exactly two hex digits are
    each refused by name. This is what buys multi-line CAPABILITY (a
    `(?x)` body written across lines, a raw high byte, a trailing CR)
    without multi-line SYNTAX: every reader's line-oriented loop is
    intact, and a `.rxt` author already knows the table.
  - **`\x00` IS REFUSED, and the refusal names K9.** `pcrec`'s compile
    entry takes no pattern length (`docs/dev/known_issues.md` K9), so a
    NUL-bearing pattern would compile as its PREFIX and report success —
    the same silent-wrong-artifact trap the whole-file NUL refusal closes
    for `pattern` lines. Expressing a NUL pattern is therefore a KNOWN
    LIMIT with a named owner and a **stated lifting trigger**, not a
    silence: the refusal is lifted when the compile entry takes a length
    (`rx_info.pattern_len`'s API half). Nothing else in the escape table
    is restricted.
  - **`pattern` itself is untouched**: rest-of-line, verbatim, byte-exact.
    The two spellings are alternatives for one block, not layers.
  - **A block carries exactly one pattern line, and that is structural
    rather than a refusal anybody wrote**: both spellings are block
    OPENERS, so a second opener starts the NEXT block (S2).
  - **The decoding has ONE home, and the CLI exposes it**:
    `pcrec --pattern-esc` (`docs/spec/cli.md` §1) takes `--pattern`'s
    VALUE [REL-1.10] in this same quoted-escape form and runs it through
    this same decoder, which is how a harness passes a block's text
    through undecoded instead of re-implementing the table.
  - **[DD-13b.W23.5] THE DUMP-VALUE SEAM: `--list-source`'s `pattern`
    column carries the DECODED bytes (below); a harness reading the raw
    file — as `tests/harness/run.sh` and `tests/harness/verify_rxt.py`
    both do, to avoid a second and a third copy of the escape table —
    reports the text AS WRITTEN, quotes included, and passes it through
    `pcrec --pattern-esc` for compilation instead of decoding it
    themselves. So a THIRD READER of a `.rxt` file (one that is not
    `pcrec` itself) sees the operand form, never the decoded bytes,
    unless it either decodes independently or calls `pcrec
    --list-source`. This is stated here because it is observable by any
    caller comparing the two, not only by the two harness legs above.
- `flags <letters>` — compile options for the current block, block-scoped
  (does not carry to the next block). Only `i` is defined (case-insensitive,
  `pcrec -i`). An unknown letter is a hard error, not a silent no-op.
- `features <list>` — enabled feature modules for the current block,
  block-scoped: a comma-separated list of module names exactly as
  `--list-syntax`'s module column spells them, passed to pcrec as
  `--features <list>`. The harness validates each distinct list once against
  a trivially-valid pattern (`pcrec` refuses an unknown module name with
  exit 1, and a `perr` block would otherwise read the typo as its expected
  rejection).
- `perr` — asserts that the current pattern fails to compile. A `perr` block
  has no `m`/`n`/etc. lines; the pattern text is the entire test. **`pcrec`
  must exit exactly `1`** (`tests/harness/run.sh:338-350`) — `0` (accepted)
  fails as "expected pattern to fail to compile ... but pcrec succeeded",
  and any OTHER nonzero exit (timeout `>=124`, crash `139`, …) fails
  separately as "pcrec CRASHED or timed out ... instead of cleanly
  rejecting". A crash is never scored as a clean rejection.
- `m "<subject>" <start> <end>` — asserts that searching `<subject>` from
  byte offset 0 finds a match spanning bytes `[<start>, <end>)`.
- `n "<subject>"` — asserts that searching `<subject>` from byte offset 0
  finds **no** match.
- `ms <P> "<subject>" <start> <end>` / `ns <P> "<subject>"` — the same two
  assertions with an explicit `startpos = <P>` (a non-negative decimal
  integer, given before the quoted subject). `m`/`n` are exactly `ms`/`ns`
  with `<P>` fixed at 0.
- `g <slot> <start> <end>` / `gp <slot> <start> <end>` — asserts a
  per-GROUP capture-slot expectation, attached to the most recently
  preceding `m`/`ms` case in the current block (never `n`/`ns` — a
  no-match assertion has no captures; a `g`/`gp` line with no preceding
  `m`/`ms` case is a hard parse-time failure). `<slot>` indexes `caps[]`
  exactly as the match API does (slot 0 is the whole match, the same value
  as the case's own `<start> <end>`). `<start>`/`<end>` are two
  non-negative integers for a real span, or the literal pair `-1 -1` for
  `RX_UNSET` — one `-1` without the other is a hard parse error, since
  `RX_UNSET` is symmetric in both slots.

  - **`g` is LIVE**: the slot must be checkable by the artifact under test
    RIGHT NOW. `run.sh` reads the artifact's actual `RX_NCAPS` from its
    generated `gen.h` (never assumed) and compares it to `<slot>`. A `g`
    line whose slot is `>= RX_NCAPS` is a **hard FAILURE**, never a silent
    skip, naming the fix ("use 'gp'").
  - **`gp` is PENDING-VM**: the slot may be beyond what today's engine
    delivers. If `<slot> >= RX_NCAPS` the case is counted in a separate
    `group cases pending-vm: N` summary bucket — not pass, not fail. If
    `<slot> < RX_NCAPS` a `gp` line self-activates and is checked exactly
    like `g`, with no corpus edit required.
  - A block-level compile or driver-build failure fails every attached
    `g`/`gp` expectation too, `gp` included — a block that never ran proves
    nothing about a slot being future-live.
  - The default python-`re` oracle (`tests/harness/verify_rxt.py`) checks
    `g` and `gp` identically against `match.span(<slot>)`: pending-ness is a
    fact about what the CURRENT pcrec artifact can deliver, which the
    python oracle has no notion of. A `<slot>` beyond the pattern's own
    lexical group count (`compiled.groups`) is always a hard failure there,
    regardless of `g`/`gp`.

- `gu <code> "<subject>"` — asserts that searching `<subject>` from byte
  offset 0 returns the typed negative code `<code>`, one of `steps` /
  `frames` / `work` / `recurse` / `unset-var` (`recurse` is
  `PCREC_ERR_RECURSE`, reserved with no producer yet, so no block can pass
  with it today — the directive still accepts the word). `internal` is
  REFUSED at parse time, by name: `PCREC_ERR_INTERNAL` is the artifact
  catching its own analysis/emission bug, never a planned outcome a corpus
  block gets to expect. Scored against the driver's exit `3` plus its
  printed word, the one case kind that WANTS that exit — see "The driver
  protocol" below.

  **`unset-var` is the one member that is NOT a give-up** ([VAR]):
  `PCREC_ERR_UNSET_VAR` sits BELOW `PCREC_ERR_FLOOR` and means the call was
  REFUSED before anything was attempted, which is `PCREC_ERR_STARTPOS`'s
  class. A block MAY expect it — unlike `internal` — because it is the
  CALLER's own doing and is exactly what a `var-unset` line is written to
  produce. `gu` is the directive for it rather than a new one: this line
  kind already means "the search returned a typed negative code and here is
  which", and a second directive for a second class of negative code would
  be two spellings of one question.

- `var <name> "<value>"` — block-scoped, repeatable: binds a module-`vars`
  variable for every case in this block ([VAR]). `<name>` is a letter or `_`
  then letters, digits or `_`; the value is a double-quoted string in the
  SAME escape vocabulary a subject carries, and there is no second one.
  `var n ""` is the EMPTY state (`rx_var.p != NULL`, `len == 0`).
- `var-unset <name>` — block-scoped, repeatable: declares the slot UNSET
  (`rx_var.p == NULL`). It is a DECLARATION and not an omission, and the
  difference is testable: omitting the name entirely ALSO reads UNSET at the
  artifact, so a block can assert both routes to one state.

  The harness builds an `rx_var[]` array from these lines VERBATIM — one
  entry per line, in source order, with no lookup and no de-duplication —
  and passes it through. A DUPLICATE name is legal to write and the
  artifact's own rule is FIRST MATCH WINS; collapsing it here would make
  that cell untestable. `docs/spec/vars.md` is the module's contract.
- `name <defname>` — block-scoped: names the block, declaring it as a
  DEFINITION. A `<defname>` is a first byte that is a letter or `_`,
  then letters, digits, `_`, `-` or `.`. **The name is in the FILE
  namespace**, not the pattern's group namespace, and must be unique
  within the file.

  - **A definition name is neither a PCRE2 group name nor a C
    identifier**, and both halves of that matter. It is not a group name,
    so a definition whose name carries `-` or `.` **cannot be called by
    that SPELLING**: `(?&some-id)` goes through PCRE2's own group-name
    grammar and is refused there, and under D26 that grammar is PCRE2's
    and not one this format may widen. It is not a C identifier, so it
    cannot be a symbol prefix as written — `-` and `.` **map to `_`** to
    produce one (see `target` below).
  - **[DD-13b.W23.3] THE DEFINITION IS NEVERTHELESS REACHABLE, THROUGH
    ITS DERIVED IDENTIFIER.** A by-name call binds to the definition
    whose name, mapped by that same `-`/`.` → `_` derivation, equals the
    call's identifier: `(?&cls_upto_64)` reaches `name cls-upto-64`. It
    is a second key on the same set, produced by the same one mapping the
    `target` prefix is produced by — no second namespace and no change to
    the name grammar. So the sentence that survives is exactly the one
    about SPELLING: `(?&cls-upto-64)` is still refused, by PCRE2.
  - **A call whose identifier TWO definitions derive is REFUSED, naming
    BOTH**, with each definition's own file and line and the identifier
    they share. **An exact spelling does not win the tie**: `x_y` beside
    `x-y` both derive `x_y`, and "exact" is only the identity case of the
    same mapping, so a silent tie-break would make the mapping's
    non-injectivity free exactly where it bites. The refusal is at the
    CALL, not at the declaration — two colliding definitions coexist for
    as long as nothing calls the shared identifier — and the repair is to
    rename one, which is why the diagnostic names both rather than only
    the identifier.
  - **The LENGTH rule is: refuse BEFORE mapping.** A `target`'s own
    prefix and definition-name fields are length-capped and refused by a
    diagnostic naming the cap (`docs/spec/limits.md`) before any
    derivation runs, so no two names can ever collide by being cut.
  - **CALLABILITY carries a 128-byte bound, and it is PCRE2's, not
    pcrec's.** A call's name is capped at `PCREC_MAX_GROUP_NAME` bytes,
    inherited under D26 from libpcre2's own limit rather than declared
    here as a pcrec choice. A call naming a longer definition is refused
    with the bound and the definition's own line stated — never left to
    read as a misspelling.
  - The wider set exists because an exported set of patterns carries ids
    a person chose (`cls-upto-64`, `w-512`), and requiring an identifier
    would force every such export to carry a name map beside it — a
    second place a pattern's identity is written.
- `description <text>` — block-scoped: a machine-readable prose field for
  this block. One-line form only (see "Lexical rules" above). **At most
  ONE per block**: a second `description` line in the same pattern block
  is refused by name, naming the block and both lines.
- `encoding <ident>` — block-scoped: the subject encoding for this
  block's compile, passed as `--encoding=<ident>`. Per-block, never
  global, exactly as the CLI option is per-compile: two blocks in one file
  may use different encodings.

  **[DD-13b.W1.3] ON A BLOCK USED AS A DEFINITION, an `encoding` that
  differs from the artifact's is REFUSED**, naming the definition, both
  encodings and the definition's own line. A definition does not inherit
  the target's config, so its `encoding` line is a thing it stated — but
  a composed artifact has exactly ONE encoding, so a definition asking for
  another is asking for something the format cannot give. Equal or absent
  composes normally. The refusal exists rather than a silent ignore
  because a dropped directive is a population nobody counts. Whether the named encoding is IMPLEMENTED
  is pcrec's answer, not the harness's — `utf8` is refused until milestone
  M5, and a block asking for it hears that from the compiler.
- `export <name>{, <name>}` — block-scoped: **the definition's declared
  INTERFACE**, the group names it offers to a caller that DELIVERS from it.
  The `config-list` shape `with`/`use`/`from` already use; the names are
  GROUP names, so they follow PCRE2's group-name grammar (a letter or `_`,
  then letters, digits or `_`) and not the wider definition-name grammar a
  block's own `name` uses.

  - **The default is NOTHING exported.** A block with no `export` line
    offers no names, and a delivering call on it delivers nothing.
  - **A name the definition does not declare as a group is REFUSED**,
    naming both the export and the definition. The check happens where the
    pattern has been parsed, not at the `export` line — this format's head
    reader does not parse patterns.
  - Exporting a name does not by itself put anything in an artifact: the
    list says what MAY be delivered, and a DELIVERING CALL decides what IS
    (see "Composition" in `docs/spec/match_api.md` §6). An exported name
    that no site delivers costs nothing at all — no slot, no row.
  - **A delivering call on a definition that exports nothing is REFUSED.**
    The default being "nothing" is what makes that a real check rather than
    a formality: it is the shape a caller reaches by assuming a library
    publishes its named groups automatically, which this format deliberately
    does not do.
- `features only <list>` — as `features`, except that the list REPLACES
  what a `config` would otherwise contribute rather than being unioned
  with it. Parsed and recorded in this build; it becomes operative when
  `config` composition lands.
- `tune <position>` — **[OPT-DIAL]** config-scoped: the SPEED-VS-SIZE
  DIAL for everything built under this config. Its value set is exactly
  `--tune=`'s — the ordinal `-2` `-1` `0` `1` `2`, or equivalently
  `min-size` `size` `balanced` `speed` `max-speed` — and both spellings
  are accepted on equal terms. The ordinal needs no `=` here: the `=`
  form is a command-line requirement about argv, not a property of the
  value. An unknown value is refused by name, class `value-shape`.

  **THE FILE WINS OVER AN EXPLICIT CLI `--tune=`**, which is the general
  rule of this format's config resolution rather than an exception to it.
  A disagreement is REPORTED — one non-fatal line on stderr naming both
  sources and both values — and the file's value is used. `tune` is
  deliberately NOT a second `--engine` exception: `--engine` is a
  comparability facility that a caller types precisely to compare two
  builds of one pattern, and it can make a pattern refuse, while a dial
  position can do neither (every position answers identically). There is
  no override flag. `docs/spec/cli.md` carries the diagnostic's wording
  and `docs/spec/tuning.md` §5 carries the per-position switch table.

- `engine vm` — block-scoped: forces `--engine=vm` for the current block's
  compile. Only `vm` is defined.
- `budget steps=<n>` / `budget frames=<n>` — block-scoped: passes
  `--step-budget=<n>` / `--backtrack-frames=<n>` respectively. Either,
  neither, or both may appear (two separate `budget` lines). These, with
  `engine vm`, are the minimal route that lets a block actually reach a
  give-up: no other directive can select `--engine=vm` or a tiny budget.
- `frames-buffer=<route>` — **POSITIONAL WITHIN THE BLOCK, not
  block-scoped**: it names the entry the cases BELOW it run through, until
  another `frames-buffer=` line changes it or the block ends. Four routes:

  | route | the case runs through |
  |---|---|
  | `default` (also the initial state) | `<prefix>_search` |
  | `null` | `<prefix>_search_in(..., NULL)` — defined to BE the call above (an identity control, not a variant) |
  | `<n>` | `<prefix>_search_in` with `<n>` resume frames AND `<n>` trail entries |
  | `<frames>,<trail>` | the same, with the two capacities set separately |

  It does not overlap `budget frames=<n>`: that one is `--backtrack-frames`,
  which sizes the ARTIFACT at compile time; this one sizes the CALL. A
  block may carry both. On a DFA artifact every route answers identically,
  because that engine's `_in` entries take a descriptor and ignore it.

**[DD-13b.W23.3] Seven more block-scoped lines**, each with its own
subsection below because each carries more than a sentence:

- `mc "<subject>" <n>` — a FIND-ALL COUNT case ("`mc` — the find-all
  count").
- `under <convention> <case-line>` — a second correct answer, qualified
  by convention ("`under`").
- `tag <item>{, <item>}` — block-level classification, the same grammar
  the file-level `tag` uses: each item a bare LABEL or a `key=value`,
  neither half carrying whitespace. A `key=value` whose KEY a
  `vocabulary` line declares is checked against that set; a bare label is
  keyless and is never checked. Repeatable.
- `oracle <engine-ref>[/<version>]` — this block's oracle, overriding the
  file's ("Oracle verification"). At most one per block.
- `provenance` — a sub-block saying where the pattern came from
  ("`provenance`"). At most one per block.
- `variant <testee>` — a sub-block carrying a named testee's own spelling
  ("`variant`"). Repeatable.
- `ext <consumer>` — a consumer's own data, which pcrec carries and does
  not interpret ("`ext` — the aux production"). Repeatable.

The `RXTROUTE` environment variable sets the INITIAL route for every block
in a run (same four-way grammar), overridden per block by a
`frames-buffer=` line; `RXTFLAGS` appends extra `pcrec` flags to every
compile in a run, for sweeping a corpus over a compiler axis the format has
no directive for. Both are manual-only (nothing in `make test` sets them) —
see `docs/testing.md`'s environment-variable table for the full list
(`PCREC`, `CC`, `GENCFLAGS`, `KEEP`, `VERBOSE`, `PROCS`, `RXTROUTE`,
`RXTFLAGS`).

`<subject>` is double-quoted text; literal spaces are fine (the quotes, not
whitespace, delimit it). These escapes are recognized inside the quotes, no
others:

| Escape | Meaning |
|--------|---------|
| `\"`   | literal `"` |
| `\\`   | literal `\` |
| `\n`   | newline |
| `\t`   | tab |
| `\r`   | carriage return |
| `\f`   | form feed |
| `\v`   | vertical tab |
| `\xHH` | byte `0xHH` (exactly two hex digits) |

### Named subjects — the `@file:` form

**[DD-13b.W23.3]** A case's subject may be the CONTENTS OF A FILE instead
of quoted text:

```
m  @file:"path" [as <id>] [sha256 <hex64>] <start> <end>
n  @file:"path" [as <id>] [sha256 <hex64>]
ms <P> @file:"path" [as <id>] [sha256 <hex64>] <start> <end>
ns <P> @file:"path" [as <id>] [sha256 <hex64>]
mc @file:"path" [as <id>] [sha256 <hex64>] <n>
```

The two suffixes are INDEPENDENTLY OPTIONAL and, when both are written,
`as` precedes `sha256`. Everything else about the case line is unchanged:
`ms`/`ns` carry their startpos before the subject and `m`/`n`/`mc` carry
none, exactly as their quoted forms do.

- **THE BYTES ARE THE FILE'S, BYTE-EXACT.** No escape decoding, no
  encoding assumption, no trailing-newline rule of any kind — not
  stripped, not required, not added. A subject carrying a NUL byte or
  ill-formed UTF-8 reaches the matcher as the file holds it, which is
  precisely what an argv-carried escape vocabulary cannot express (argv
  cannot carry a NUL at all). An EMPTY file is a legitimate empty
  subject, not an error.
- **The path resolves against the `.rxt` file's OWN directory** (an
  absolute path is used as written). A path naming no readable file is a
  failure that names both the written path and what it resolved to.
- **`as <id>` names the subject**, in a per-FILE id namespace. The id is
  spelled in the wide `defname` grammar, since the ids a set carries are
  a person's.
- **THE BINDING IS FUNCTIONAL, NOT A UNIQUENESS KEY**, and the
  distinction is the production's whole point. One id maps to one
  `(path, sha256)` pair. **Restating the SAME binding on many case lines
  is the NORMAL spelling** — every case line naming the subject carries
  it again — so equal ids with equal values is the common case and
  nothing is refused. Only a CONFLICTING re-binding is refused (the same
  id with a different path or a different hash), and the refusal **names
  both lines**, because the repair needs to know where the other one is.
  Two different ids for one path are legal, pointless and harmless.
- **`sha256 <hex64>` pins the file's contents**, exactly 64 hex digits,
  case-insensitively compared. A `sha256` keyword with anything else
  after it is refused as a value-shape error.
- **WHO CHECKS THE HASH: whatever READS the subject, which is the
  harness.** `tests/harness/run.sh` and `tests/harness/verify_rxt.py`
  each digest the resolved file and refuse on mismatch, naming the path,
  the digest the line claims and the digest the file has; `run.sh`
  additionally refuses — rather than silently passing — when no sha256
  tool is available at all, because a digest nobody computed must not
  read as a digest that matched. **`pcrec` checks neither the hash nor
  the 64-digit syntax**: `--list-source` performs no file I/O and reads a
  case line without parsing it (`--list-schema`'s `#section surface` row
  `subject-content` is where that non-coverage is declared).

### `mc` — the find-all count

**[DD-13b.W23.3]** `mc "<subject>" <n>` (or the `@file:` form above)
asserts that the find-all protocol over the subject reports exactly `<n>`
matches. It takes no startpos.

**THE COUNTING RULE HAS ONE HOME AND THIS IS NOT IT**: the rule is
`docs/spec/match_api.md` §3.1's shipped find-all protocol, by reference —
searching from a position, resuming at a non-empty match's END, and, off
an EMPTY match, resuming one CHARACTER past the match's own **REPORTED
START** (`<prefix>_next_pos(caps[0][0])`), with no empty-match retry.
That section states the loop, and an `mc` line asks for its count and
nothing else.

Two consequences are worth stating here, where an author meets them:

- **The advance is off the REPORTED START, not off the loop variable**,
  and the two differ: an empty match can be found at a position later
  than the one searched from, so advancing off the searched-from position
  double-counts it. `(?=a)` over `"xax"` is **1**, not 2.
- **An `mc` count is NOT a `re.finditer` count on an empty-preferring
  pattern.** §3.1 names the class: engines that RETRY at the same
  position under an "empty match not permitted here" constraint report
  the non-empty match as well, and pcrec's entry points cannot express
  that retry — so the protocol's spans are always a strict SUBSET.
  `a*?` over `"aaa"` is 4 under the protocol and 7 under `finditer`. An
  author takes the number from the protocol.

**THE ADVANCE OVER ILL-FORMED UTF-8 IS NORMATIVE AND IS STATED IN BOTH
PLACES A READER MEETS IT** (here and in `match_api.md` §3.1.1): under an
encoding with multi-byte characters, the one-character step is *from
`pos + 1`, then past every byte in the range `0x80`-`0xBF`*, landing on
the next non-continuation byte or on the end of the subject. It is the
rule the emitted artifacts already implement, and it is written down
rather than left to "the next character boundary" because for ill-formed
input that phrase has no single reading and an `mc` count is exactly what
a foreign consumer compares against.

### `under` — a second correct answer, per convention

**[DD-13b.W23.3]** `under <convention> <case-line>`, where `<case-line>`
is an UNCHANGED `m`/`n`/`ms`/`ns`/`mc` line. One pattern and one subject
can have two different CORRECT answers — `a|ab` on `"ab"` is `0 1`
leftmost-first and `0 2` leftmost-longest — and an unqualified case line
has no room to say which it means.

- **An UNQUALIFIED case line is unchanged**: it means the expectation
  under the file's or block's own canonical convention. A file declaring
  no conventions behaves exactly as it did before this production
  existed, which is what makes `under` purely additive.
- **FALLBACK**: a consumer whose convention has no `under` line for a
  case falls back to that case's unqualified line.
- **`<convention>` is a tag value, closable by `vocabulary convention`.**
  With such a line in the file, a convention outside the declared set is
  refused naming the vocabulary line and its members; with no such line
  any name is accepted. The format does not know what
  `posix-leftmost-longest` MEANS — scoring against the right expectation
  is the consumer's act, not the format's.
- **DUPLICATES ARE REFUSED, NOT LAST-WINS.** Two `under` lines stating
  the same `(convention, case kind, startpos, subject)` are refused as a
  duplicate, naming the earlier line. The key is that four-part tuple and
  not the whole line: two `under` lines that differ only in their
  EXPECTATION are the contradiction this refuses.
- **`under` NEVER wraps `g`, `gp` or `gu`**, and `g`/`gp` attach only to
  unqualified `m`/`ms` cases. A capture expectation under a foreign
  convention has no consumer today, and admitting one would force the
  attachment rule to answer a question nobody has asked.
- **pcrec's own harness treats every `under` line as a COUNTED, LABELLED
  SKIP**, never a silent one and never a scored case. Scoring one would
  require the harness to know pcrec's own convention BY NAME, which is
  engine knowledge a test runner must not hold. The summary prints
  `under expectations skipped: N` unconditionally, so a file whose
  expectations are all qualified reads as "0 cases, N under-skips"
  instead of as a file that quietly tested nothing. Scoring is the
  consuming runner's.

### `provenance` — where a pattern came from

**[DD-13b.W23.3]** `provenance` takes no value and opens a SUB-BLOCK of
indented fields. **At most one per parent**, and it has two parents — a
pattern block and a bundle's DATA block (`freq`) — which are **one record,
not two productions**: the eleven fields are the same eleven at both, and
what differs is which of them are REQUIRED.

| field | value | notes |
|---|---|---|
| `source` | token | **required at both parents.** The literal value `authored` means the pattern was written here |
| `url` | token | **required under a PATTERN block unless `source authored`; FORBIDDEN when `source authored`**; optional under a DATA block ([FINDINGS] B0: a user's private exemplar has no URL) |
| `ref` | token | the same rule as `url` |
| `retrieved` | token | **required at both parents** |
| `license` | token | **required under a PATTERN block** |
| `license-note` | prose | optional; takes the block-scalar form |
| `fidelity` | token | **required under a PATTERN block**; a closed set — `verbatim`, `adapted`, `synthesized` |
| `adaptation` | prose | **required when `fidelity` is not `verbatim`** — adaptation iff not verbatim |
| `attribution` | prose | optional |
| `bytes` | int | **required under a DATA block unless `source authored`** ([FINDINGS] B0: authored data, such as the shipped default table, has no exemplar to measure) |
| `sha256` | token | the same rule as `bytes` |

Every field is at-most-one within the record.

- **The per-parent split is a property of the ROWS, not a second
  record.** The conditions are spelled over the reserved field `parent`
  (see "The `constraints` column's clause spellings" below), so a pattern
  block requires `{source, license, retrieved, fidelity}` (plus `url`/`ref`
  when not authored) and a data block requires `{source, retrieved}`
  (plus `bytes`/`sha256` when not authored) off one set of fields. Duplicating the scope would have produced two records that
  rhyme: an exemplar owes no `license` (a user's own log file has none to
  state) and no `fidelity` (nothing about a byte histogram was adapted),
  and that is the whole of the difference.
- **The spelling is `license` and `license-note`**, two fields: the
  identifier and the prose about it. A note is not a longer licence.
- **Every condition names a SIBLING**, so the whole record is read before
  any of them is answered — `url` may be written above the `source
  authored` that forbids it, and a missing `adaptation` cannot be
  detected until the record ends.

### `analysis` — the bundle

**[FINDINGS] B0** (`docs/design/findings/design.md` §3). `analysis <name>`
is a file-level BUNDLE: the named analysis a `config`'s `analysis` line
selects. It holds **at most one data block per KIND**, an optional
`include <other>`, and an optional `description`. It is a HEAD
declaration, so it sits above the first `pattern` line. Nothing in this
build CONSUMES a bundle: B0 is the format, parsed and reported; the
compiler's reading of it arrives with [FINDINGS] B1/B2.

- **The name** is LOWERCASE ONLY, `[a-z][a-z0-9_-]*`, and unique in the
  file (a second `analysis` with the same name is refused naming the
  first). An uppercase letter is refused by that rule's name: a bundle is
  found as a directory entry `<name>.rxt`, matched exactly, so `Log` and
  `log` must never both be spellable.
- **Not in an include fragment.** An `analysis` line in a file reached
  through an `include "path"` line — at any depth of the closure — is a
  parse error of the ENTRY, naming the fragment's own `file:line`: a
  bundle is found in the compiling file, a `-I` directory or the shipped
  store, never in a fragment. Only this refusal is propagated to the
  entry; a fragment broken for any other reason remains the harness's
  `[resolution]` class (below).

| bundle line | cardinality | value |
|---|---|---|
| `include <other>` | at most one | another analysis, in C's SEARCH spelling `<name>` (the bundle-name grammar). A quoted path is refused: this is not the head's `include "path"` splice. `<other>` may name the bundle's own name (resolution, B2, gives that `#include_next` meaning) |
| `description <text>` | at most one | prose; takes the block-scalar form |
| `freq` | at most one | a DATA block (below), takes no value: a kind block is named by its bundle |

`cpfreq` and `bigram` are not bundle lines in this build; each is admitted
with its first reader.

**The DATA block** (a kind block's indented body):

| body line | cardinality | value |
|---|---|---|
| `question <text>` | **exactly one, required** | what this table answers |
| `reader <text>` | **exactly one, required** | the selection point that consumes it (prose) |
| `analyzer <text>` | **exactly one, required** | the tool that produced the table |
| `encoding <e>` | **exactly one, required** | what the COUNTED DATA was — closed set `ascii`, `utf8`, `latin1`, `bytes`. A DESCRIPTION of the data: never consulted to decide which compiles the block serves |
| `serves <query> when <enc>[,<enc>…] via <derivation>` | **at least one**; at most one per `<query>` in the block | the OPERATIVE applicability line: this block answers `<query>` for a compile whose encoding is listed, computed by `<derivation>` |
| `row <key> <count>` | repeatable | one table entry |
| `provenance` | **exactly one, required** | the record the section above describes |

- **`serves`' vocabularies are closed.** `<query>` is `byte-rate` or
  `run-rarity`. `<enc>` is a compile encoding — a name `pcrec -e`
  accepts (`byte`, `utf8`). `<derivation>` is `unigram` (a `freq`
  derivation, answering `byte-rate`), `encode-utf8` or `encode-latin1`
  (`cpfreq`, `byte-rate`) or `markov1` (`bigram`, `run-rarity`); a
  derivation must belong to the block's kind and answer the line's
  query.
- **At most one block per (query, encoding) in a bundle.** A second claim
  of one (query, encoding) pair anywhere in the same bundle — a second
  block, or the same encoding twice on one line — is refused, naming the
  line that claimed it first. (While `freq` is the only kind, a bundle
  holds one block, so the reachable case is the duplicated encoding.)
- **`row`'s key grammar is per kind.** Under `freq` a row is `row HH N`:
  one byte key as TWO LOWERCASE hex digits (`00`..`ff`) and a count.
  Keys are **strictly ascending** through the block, so a duplicate key is
  refused at the line. The count is a canonical decimal: no leading zero,
  and never `0` — **a zero count is written by omitting the row**.

A bundle's own reach into the dump: see `--list-source`'s `analysis` row
below.

### `variant` — a testee's own spelling

**[DD-13b.W23.3]** `variant <testee>` opens a SUB-BLOCK carrying the
pattern text a NAMED testee needs, for the same case. Repeatable within a
block.

| attribute | value shape | what it says |
|---|---|---|
| `text` | rest-of-line, verbatim | the replacement pattern for this testee |
| `unsupported` | line | this testee cannot express the pattern, and why |
| `kind` | token | what KIND of difference this is; closable by `vocabulary kind` |
| `groups` | list | the group correspondence |
| `note` | prose | free prose, block-scalar form available |

- **EXACTLY ONE of `text` and `unsupported`.** A variant that states
  neither says nothing; one that states both contradicts itself. Each is
  at most one.
- **`kind`, `groups` and `note` are legal only BESIDE `text`**: a
  declared refusal has no replacement text to classify, so each is
  refused when `unsupported` is present.
- **`kind`'s vocabulary is a FILE hook**: with a `vocabulary kind …` line
  the value is checked against that set, naming the vocabulary line and
  its members on a miss; with no such line the key is free.
- **THE TESTEE NAME IS A `defname`, NOT AN `ident`** — the wide grammar,
  because real testee names are hyphenated slugs (`pcre2-dfa`,
  `pcre2-interp`) and an identifier-only rule would make them unspellable.
- **It is validated as a name, as UNIQUE within its block — and against
  NOTHING ELSE.** Two `variant` blocks naming one testee in one pattern
  block are refused, naming the earlier line. There is no roster of
  testees in this format and pcrec does not know what engines exist, so
  an unknown name is accepted. **This is a deliberate non-check**: the
  absence of a `closed` clause on the row is where a reader fetches it,
  and cross-checking a testee name against a real roster is the
  consuming tooling's job.

### `ext` — the aux production

**[DD-13b.W23.3] The format carries one production whose defining
property is that pcrec does not understand it.** `ext <consumer>` opens a
block of structured data belonging to a named consumer: **pcrec parses
the structure, dumps it faithfully, and interprets nothing.**

**[DD-13b.W23.4] "Dumps it faithfully" is `--list-source`'s `#section
aux`**, above: one row per line of the tree, the opener included at
depth 0, in source order, every value the line's own token remainder and
nothing more. That section is the whole of what pcrec ever does with an
`ext` body's contents.

```
ext bench
  roster pcre2 re2 hyperscan
  matrix
    rows 16
    columns 4
  policy strict
```

- **Two parents, one production**: FILE scope and BLOCK scope. File scope
  carries what is true of the whole set, block scope what is true of one
  pattern.
- **`<consumer>` is a free `defname`, RESOLVED AGAINST NOTHING.** There
  is no registry of consumers, no refusal for an unknown one, and adding
  one is not a format change.
- **`cardinality: repeat`, at BOTH scopes.** Several `ext` blocks for one
  consumer are legal and several consumers are the point. Nothing
  accumulates, nothing last-wins, and there is no duplicate refusal —
  because a duplicate refusal is a judgement about what the data MEANS,
  which is exactly what this production declines to make. It is the one
  place in the format where "at most one" would have been wrong.
- **The body is ordinary indented records under the SAME structure rules
  as everything else.** S0's line classes and S1's attachment apply
  verbatim, to any depth; a key inside the body may be spelled
  identically to a format keyword and is still just a key.
- **Its row carries `children: tree`, which makes the body an OPEN
  SUBTREE — structure-layer parameter 3.** Two consequences a reader gets
  by FETCHING that column rather than by knowing about `ext`: **no line
  inside an `ext` body opens a group** (S2's opener set is empty there,
  `pattern` and `pattern-esc` included), and **no bare `|` there opens a
  prose region** (S3 never opens inside an open subtree, so a trimmed `|`
  is the literal value `|`). Therefore **every aux value is ONE LINE**,
  and a paragraph is written as child lines a reader hands back in source
  order.
- **The body's own contents are never schema-checked.** There are no rows
  for an aux key, no value shapes, no cardinalities and no vocabulary
  hook — a `vocabulary` line naming an aux key constrains nothing,
  because checking a key's values would be interpreting them.
  `--list-schema`'s `#section surface` row `ext-tree-contents` is where
  that non-coverage is declared. What IS checked is the STRUCTURE, and
  that is the point of checking it at all: a malformed body is a
  structure error REPORTED ON ITS OWN LINE, never a silent mis-parse that
  reattributes the lines after it.

**THE GRADUATION RULE, normative.** *The day something in an `ext` block
needs pcrec to ACT on it, it must GRADUATE to a real production. Aux
never grows semantics in place.* Five clauses make that testable:

1. **"Act on" means any of**: a build reads it, a check reads it, a
   diagnostic cites its VALUE (as opposed to a structure error on its
   own line), a config resolution consults it, the composer looks in it,
   or any pcrec surface other than the faithful dump reports it. A change
   making any of those true of an aux body IS the graduation event and is
   refused as an aux change.
2. **Graduating costs the ordinary price**: a production in this
   document, a schema row with its scope, value shape, cardinality,
   constraints and `validated_by`, and a place in the wave table. That
   cost is the POINT — it is what a format-level commitment is, and `ext`
   exists so that a consumer's experiment need not pay it before anyone
   knows whether the idea survives.
3. **A graduated spelling need not keep its aux spelling**, and usually
   should not: an aux key was never held to the naming standard a
   production is held to.
4. **The failure mode this rule names** is the one every extension
   namespace eventually has: a field everybody writes, that one tool
   reads "just this once", that becomes load-bearing without ever being
   specified — after which the format has a production nobody designed,
   cannot change and does not document.
5. **AND THE VALUE RULE, which is what polices the routes AROUND clauses
   1-4.** Clauses 1-4 enumerate READERS; two routes reach the same place
   without reading anything. A schema constraint on the `ext` OPENER (a
   cardinality, a uniqueness rule over the consumer token) would make a
   refusal depend on how many aux blocks a file has; a derived COUNT (an
   aux-row total in a summary, a number pinned by a check) would make an
   aux edit turn a tree red. So the clause is stated over VALUES:

   > **Nothing in pcrec — no test, no dump summary or count, no refusal,
   > no diagnostic, no selection — may take a value that CHANGES when an
   > aux body changes, except the faithful per-line rows reporting that
   > body itself.**

   That is a property of pcrec's OUTPUTS, so it holds however a reading
   is spelled, and it is checkable in the direction that matters: edit an
   aux body, and every pcrec output except those rows must be
   byte-identical.

**The disambiguating sentence, because the two are easy to confuse**: *an
`ext` block extends what a file CARRIES, never what the format MEANS.*
It is not a config — nothing in it reaches a compile, a flag, a limit or
an axis, in any mode, and there is no mode. It is not a second `tag`:
`tag` is a pattern-level classification pcrec's own harness reads,
validates the shape of and reports, while aux is a consumer's tree pcrec
repeats. They differ in who the data is for, which is the only
distinction that needed drawing.

**This is the one place the format promises something by promising NOT to
do it**, and that is why it is spec text rather than a design note: a
consumer who cannot cite a sentence saying *pcrec will not read this* has
no basis for putting anything there.

### The schema and its surface — `pcrec --list-schema`

**[DD-13b.W23.1]** The format's rules are DECLARED as data rather than
implied by a parser's control flow. One table, one reader, one dump:

- **the table** is compiled into pcrec, one row per (scope, line-kind);
- **the reader** is the parser itself, which walks it;
- **the dump** is `pcrec --list-schema`, a TSV under
  `docs/spec/table_contract.md` and the **SEVENTH** registry surface.

The dump walks the same table the parser enforces, so a dump that
disagrees with the parser about which rows exist is not expressible. What
it does NOT prove is that the parser ENFORCES what a row declares; that is
an independent check's job (`tests/rxtsource/`'s W23-S3, which drives each
row's own behaviour and compares the result against this output — never
the output against the table, which would be the same source twice).

Ten columns, in two named sections.

| column | what it says |
|---|---|
| `scope` | `file`, `block`, or a named child scope (`config`, `bundle`, `data`, `provenance`, `variant`) |
| `kind` | the line's first token, as an author types it |
| `value` | the value shape: `none`, `token`, `int`, `line`, `prose`, `list`, `pair`, `subject`, `case`, `qualified-line`, `raw` |
| `opens_group` | **structure-layer parameter 1** (S2) |
| `children` | `none`, `prose`, `tree`, or the child scope this kind admits — the four real cases: takes nothing indented, takes BYTES, takes structurally-parsed lines with no scope and no rows, takes schema-checked lines in a named scope. With `value` it is **parameter 2**; alone, the value `tree` is **parameter 3** |
| `cardinality` | `one`, `at-most-one`, `repeat`, `accumulate` |
| `constraints` | zero or more of the seven kinds, `;`-separated, each with its own argument text |
| `source` | `format` (pcrec declares the row) or `file` (a `vocabulary` line declares it) |
| `validated_by` | `pcrec`, `all-readers` (pcrec, `tests/harness/run.sh` and `tests/harness/verify_rxt.py`, with a fixture proving the three agree), or `none` |
| `wave` | which delivery introduces the kind |

**`value` is the SHAPE, and it is asserted at the level every row shares**
([DD-13b.W23.3]). `none` takes no value; `int` takes digits and nothing
else; every other shape takes a non-empty value, except `prose`, whose
empty form is legal. The precise grammar of a `token`, a `list` or a
`qualified-line` belongs to the production that owns it and is stated
where that production is — `lib "a path"` is a `token` row whose value
carries a space, so a generic no-whitespace test would refuse a shipped
spelling. The column is published, so it under-claims rather than
over-claims on purpose: a reader can act on what it says. `frames-buffer=`
is declared `token` for exactly this reason — its four routes are
`default`, `null`, `<n>` and `<frames>,<trail>`, and only the third is an
integer.

`#section surface` is the second section: the **declared non-coverage**,
one row per thing the schema deliberately does not validate, with its
reason. An absence in a table reads as something nobody got to; a declared
non-coverage row reads as something somebody decided.

**A keyword this build does not implement is refused BY NAME**, as NOT IN
THIS BUILD, with its wave — never as an unknown token, which would send a
reader hunting a typo in a word that is in this document. That list is
DERIVED from the `wave` column and is not kept by hand anywhere, so a
keyword cannot be forgotten in it and a WITHDRAWN production cannot linger
in one: a withdrawn production has no row, therefore no wave, therefore no
entry, and it refuses as an unknown token in its scope, which is the truth
about it. **At this build the derived list is empty** — no row's wave is
above `# wave-built:` — so the branch is reachable only by the next wave's
rollout, and a consumer confirms that from the dump rather than from here.

**`version` is RESERVED** — recognised as a word the format owns, with no
production behind it in any build. It is one line of insurance against the
day a change to this format is not additive; nothing today is. Its schema
row carries the RESERVED sentinel wave (`--list-schema`'s `# wave-reserved:`
trailer names the value), and it refuses BY NAME as RESERVED — not as NOT
IN THIS BUILD, which would promise a wave that is not coming.

#### The `constraints` column's clause spellings

**[DD-13b.W23.3]** Three clause spellings carry an argument, and the dump
publishes them, so a consumer reads the rule off the row rather than
remembering it:

- **`closed <selector> [member…]`** — the SELECTOR names the SET and the
  remaining words are the FORMAT-declared members. **No members means the
  set is FILE-declared only**: it is whatever a `vocabulary <selector> …`
  line in the file declares, and with no such line the key keeps
  FREE-VOCABULARY behaviour and nothing is refused. Both halves therefore
  read the same way — `closed fidelity verbatim adapted synthesized` is a
  format-declared set, `closed kind` a file-declared one — and adding a
  `vocabulary` line is what turns the second from free into closed.
- **`closed per-key`** — the value is a LIST of `key=value` items and
  **each item's own KEY selects the set**. A per-row selector cannot
  express this, because the set is chosen per item rather than per row. A
  BARE label in such a list is keyless and is therefore never
  vocabulary-checked.
- **`required-if` / `forbidden-if <field> <op> [value]`** — `op` is `==`,
  `!=` or `present`. `<field>` names a SIBLING row in the same scope,
  except for **`parent`, the ONE reserved field name**, which reads the
  ENCLOSING scope's own name. `parent` is how ONE `provenance` record
  serves two different parents without being two records: `required-if
  parent == block` and `required-if parent == data` select the two
  required sets off a single set of rows. **[FINDINGS] B0: conditions
  join with ` and `** — `required-if parent == data and source !=
  authored` holds when every conjunct holds. Conjunction only.

### Example

```
# Literal matching and basic quantifiers.

pattern abc
m "abc" 0 3
m "xxabcxx" 2 5
n "ab"

pattern a+
m "aaa" 0 3
n "b"

# An invalid pattern: unbalanced group.
pattern (bad
perr

pattern colou?r
m "The color and colour are spelled differently." 4 9
m "colour" 0 6
m "byte \x41 then newline\n" 5 6
```

## `--list-source` — reading a `.rxt` file's structure

`pcrec --list-source FILE` prints the file AS WRITTEN as a TSV under
`docs/spec/table_contract.md`: one row per head declaration and per
pattern block, **in FILE ORDER**. It takes no pattern and no `-o`, and it
compiles nothing.

**It is the SEAM.** pcrec owns the head grammar and is its only
implementation; `tests/harness/run.sh` keeps its own body parser and
gains no head arms at all. For a head-bearing file the harness calls this
once, reads the `line` column of the FIRST `pattern` row, and starts its
own per-line loop there — so the head is an untouched byte range whose
boundary comes from the one head parser, and the two cannot drift.

| # | column | on | value |
|---|---|---|---|
| 1 | `kind` | all | `lib` \| `target` \| `config` \| `description` \| `pattern` \| `include` \| `analysis` |
| 2 | `line` | all | 1-based first line of the declaration or block |
| 3 | `name` | target, config, pattern, include, analysis | the target's PREFIX; the config's name; the block's `name` (empty if unnamed); an `include`'s RESOLVED REAL PATH; the bundle's name |
| 4 | `value` | lib, target, description, pattern, include, analysis | `lib`'s path reference; `target`'s definition name; a `description`'s text; a block's own `description`; `include`'s path AS WRITTEN; a bundle's own `include <other>` AS WRITTEN (empty with none) |
| 5 | `pattern` | pattern | the block's pattern text |
| 6 | `flags` | pattern, config | the letters |
| 7 | `features` | pattern, config | the module list |
| 8 | `features_only` | pattern | `1` if the block wrote `features only` |
| 9 | `encoding` | pattern, config | the ident |
| 10 | `engine` | pattern, config | `vm` |
| 11 | `budget_steps` | pattern, config | N |
| 12 | `budget_frames` | pattern, config | N |
| 13 | `with` | target | the config list, as written |
| 14 | `from` | config | the config list, as written |
| 15 | `pcrec` | config | the raw flag text |
| 16 | `export` | pattern | the block's `export` list, as written ([DD-13b.W1.3]) |
| 17 | `tags` | pattern | every `tag` line's items, comma-joined in source order ([DD-13b.W23.4]) |
| 18 | `oracle` | pattern | the block's own `oracle <ref>` override, or empty ([DD-13b.W23.4]) |
| 19 | `esc` | pattern | non-empty exactly when the block opened with `pattern-esc` ([DD-13b.W23.4]) |
| 20 | `tune` | config | the `tune` position AS WRITTEN — the ordinal or the alias the author typed, never a normalisation of it ([OPT-DIAL]) |

Column 1's value set also gains four head-scoped kinds, each printed as
its own row ([DD-13b.W23.4], `lib`'s own one-row-per-line convention):
`vocabulary` (`name` = the key, `value` = the escaped member list),
`oracle` (the file-level override, `value` = the reference text), `tag`
(`value` = the item list as written) and `use` (`value` = the
comma-separated config list).

**A `pattern-esc` BLOCK IS REPORTED AS A `pattern` ROW, WITH ITS DECODED
BYTES** ([DD-13b.W23.3]/[DD-13b.W23.4]). The decoding is pcrec's own, so
the row's `pattern` column carries the same bytes a compile sees,
re-escaped in the dump's own vocabulary below — a byte-exact round trip,
the same table in both directions. **Column 19 (`esc`) is the marker**
that disambiguates which spelling wrote them, once thought to be a gap
this dump could not close; read `pattern` together with `esc` to
reproduce a file as written, and read `pattern` alone for the bytes,
since both spellings deliver the same bytes.

**THE W23 PRODUCTIONS ARE NOW REPORTED** ([DD-13b.W23.4], superseding the
"parse and are not reported" rule this section stated through W23.3).
`include` gained its row at [DD-13b.W23.3a]; `vocabulary`/`oracle`/`tag`/
`use` gain theirs above; the block-scoped `tag`/`oracle` lines reach
columns 17-18; and `provenance`, `variant`, the eight CASE-kind lines
(`m`/`n`/`ms`/`ns`/`mc`/`gu`/`g`/`gp`, `under`-wrapped ones included) and
`ext` reach the four `#section` blocks below. **[FINDINGS] B0**: each
`analysis` bundle is one `analysis` row. **A bundle's `include <other>`
is that row's `value`, NEVER a head `include` row** — the head `include`
kind is the path splice, and a harness reading `include` rows to walk a
closure must never meet a bundle link. A kind block's own body (`question`,
`reader`, `analyzer`, `encoding`, `serves`, `row`) is parsed and not
reported — no `#section freq` exists — and its `provenance` sub-record
rides `#section provenance`, with `block_line`/`block_name` naming the
enclosing BUNDLE (its `analysis` line and name).

### The four `#section` blocks

Emitted **unconditionally when non-empty, always AFTER the main table,
never interleaved with it** (table_contract.md's `#section` mechanism,
one header comment line per section naming its columns). A file using no
W23 production emits no `#section` line at all, so its stream differs
from a pre-W23.4 one only in the header row's three appended columns —
`table_contract.md`'s own compatible-evolution rule, resolved by name.
**No `#section` row's field 1 may equal any main-table `kind` token**:
every section's own field 1 is the integer `line`, which can never equal
a kind word — the invariant an EQUALITY-reading consumer (one that tests
`$1 == "pattern"`) relies on, and the reason sections are declared to
follow the main table unconditionally rather than interleave with it.

- **`#section provenance`** — one row per `provenance` sub-block, on
  either parent: `line`, `block_line`, `block_name`, then the record's
  eleven fields as columns — `source`, `url`, `ref`, `retrieved`,
  `license`, `license-note`, `fidelity`, `adaptation`, `attribution`,
  `bytes`, `sha256` (see "`provenance`" below for what each means).
- **`#section variants`** — one row per `variant <testee>` sub-block:
  `line`, `block_line`, `block_name`, `testee`, `kind`, `text`, `groups`,
  `note`, `unsupported`.
- **`#section cases`** — one row per CASE-kind line, in source order,
  including one wrapped in an `under` line: `line`, `block_line`,
  `block_name`, `kind`, `under` (the qualifying convention, or empty),
  `startpos` (the effective value — `0` for `m`/`n`/`mc`/`gu`, the
  written value for `ms`/`ns`, empty for `g`/`gp`, which have none of
  their own), `subject_form` (`inline` | `file`, empty for `g`/`gp`),
  `subject` (the quoted text AS WRITTEN, or the `@file:` path, empty for
  `g`/`gp`), `subject_id`, `sha256`, `start`, `end` (decimal, or the
  literal `-1` pair for `g`/`gp`'s own `RX_UNSET`), `count` (`mc` only),
  `giveup` (`gu` only), `slot` (`g`/`gp` only), `route` (the
  `frames-buffer=` route live at that line — always set, `default`
  initially).
- **`#section aux`** — one row per LINE of an `ext` tree, the opener line
  itself included: `line`, `block_line` (empty at file scope), `block_name`
  (empty at file scope), `consumer`, `depth` (`0` for the opener),
  `key` (the line's first token — `ext` for the opener, whose `value`
  is then the consumer token), `value` (everything after the key's
  separating whitespace, verbatim to end of line, escaped — empty for a
  bare key), `parent_line` (empty for the opener; otherwise the `line` of
  the row it attaches under). Row order is source order, guaranteed —
  the only semantics an aux tree has that pcrec preserves. This section
  is where "dumped faithfully" (§2.27's own promise) is discharged and is
  the ONLY surface that reads an `ext` tree at all: a `value` is escaped
  bytes, never interpreted, never decided to be a number, a list or a
  boolean.

**The dump VALIDATES what it emits and no more**: a row's own
`validated_by` column, printed by `pcrec --list-schema`, is the live,
derivable answer to "does the dump check this line's value" — `pcrec`
(this parser alone), `all-readers` (every one of the three `.rxt`
readers must agree), or `none`, in which case `--list-schema`'s own
`#section surface` names the reason. Subject content (a `sha256` digest,
a `@file:` path's readability) and pattern text are never validated here
regardless of section — `--list-source` performs no file I/O and
compiles nothing.

**`kind` carries the DECLARATION NAME**, not a `head`/`body`
supercategory. There is no column saying whether a row is a head row and
there does not need to be: the head ends at the first `pattern` row, so a
head row is exactly one preceding it. That is a property of the ORDER,
and a column for it would be a second home for a fact the row order
already carries — free to disagree with it.

**Column 10 (`engine`) reads only `vm`** (r46sem finding 4, FIXED): this
table briefly disagreed with this same document's own "the .rxt format"
section below, which has always ruled `dfa` NOT DEFINED for W1.1 (the
smaller change; it arrives when a test needs it, D77) — `tests/harness/
run.sh` refused it from the start, and `src/parse/rxt_source.c` and
`tests/harness/verify_rxt.py` are now consistent with that ruling too.

**Columns 4, 5 and 15 are ESCAPED** in the `.rxt` format's own subject
escape vocabulary (`\t`, `\n`, `\r`, `\\`, `\xNN` — the table above under
"`<subject>` is double-quoted text"). This is not decorative: a `pattern`
line is rest-of-line VERBATIM and may contain a literal tab, and the
corpus contains three such blocks today. No second escape vocabulary is
invented — a `.rxt` author already knows this one, and
`tests/harness/driver.c`'s decoder already implements it.

**This is a SUBSET of the full subject escape table above** (r46sem
finding 22, noted): the dump's five escapes (`\t \n \r \\ \xNN`) are the
ones needed to protect TSV FRAMING, not the full seven-escape subject
vocabulary (which adds `\"` and named `\f`/`\v`). `\f`/`\v` still
round-trip correctly through the dump's own `\xNN` form (`\f` as `\x0c`,
`\v` as `\x0b`); a literal `"` is deliberately left unescaped, which is
harmless for TSV framing but means a dumped field is not directly
re-feedable to `tests/harness/driver.c`'s `decode()` as a quoted
subject without re-adding that one escape first.

**AS WRITTEN, never resolved.** `config` composition and the `with` /
`from` cascades are VALIDATED (an unknown config name and a `from` cycle
are both refused, naming the members) but NOT APPLIED here. The output
reports what the file says, so that it can be compared against another
parser of the same file; a resolved dump would report something only
pcrec computes, against no counterpart. `--list-source --resolved` is
named and unbuilt.

**THE MAIN TABLE STAYS SECTIONLESS**, and the head/body INTERLEAVING that
reasoning was always about — a consumer's row-order check over ONE
stream — is unaffected by [DD-13b.W23.4]'s four `#section` blocks above:
those carry data whose rows genuinely cannot be columns of the main table
under any reading (`provenance`/`variant`/`ext` sub-records, one-row-
per-case-line and one-row-per-aux-line data), which is exactly the
trigger this paragraph named in advance. The main table's own rows never
move into a section.

## Oracle verification

Every corpus expectation must be independently verifiable, not merely
believed. The default oracle is python3 `re`:
`python3 tests/harness/verify_rxt.py [files-or-dirs]` (default
`tests/base`) checks every `m`/`n`/`ms`/`ns`/`g`/`gp` line against
`compiled.search`/`match.span`, run on the same subject/startpos as the
`.rxt` case. Run it whenever a corpus file changes.

`flags i` maps to `re.IGNORECASE | re.ASCII` — the `re.ASCII` is required,
since python's plain `IGNORECASE` folds Unicode and would silently disagree
with pcrec's deliberately ASCII-only fold. `features <list>` is understood
as a no-op (python `re` has no module gate).

**A block correct for PCRE2 but not python-verifiable carries a
`# pcre2-only` comment line immediately before its `pattern` line.** The
verifier skips it and reports the skip count. Keep such marks rare and
justified: every exclusion needs a corresponding entry in
`docs/dev/upstream_issues.md` naming the divergence. `docs/testing.md`'s
"Oracle exclusions" carries the current, evolving list of known python/PCRE2
divergences behind existing `# pcre2-only` marks.

**A directory may name its own additional or replacement oracle** instead of
(or beside) the default. `tests/assertions/` is the one directory in the
tree whose oracle rule differs by design: it carries `verify_pcre2.py`, a
libpcre2 differential that re-checks every cell — marked and unmarked — on
every `make test`, because several of its constructs (`\Z`, `\G`, `\K`)
have no python equivalent at all. A new per-module directory that needs the
same treatment follows that precedent rather than inventing a new one; see
that directory's own CLAUDE.md for the worked example.

### `oracle` — declaring which engine an expectation was checked against

**[DD-13b.W23.3]** `oracle <engine-ref>` is a DECLARATION, legal at FILE
scope and at BLOCK scope, at most one of each. A block's own line is the
more specific of the two. It is recorded and shape-checked; no reader in
this build RESOLVES an oracle declaration to a verification — the default
python-`re` tier and the `# pcre2-only` convention above are unchanged by
it, and a declaration's effect today is the counted skip below.

**`<engine-ref>` is an engine name, optionally `/` and a version.** The
ENGINE half is an identifier (a letter or `_`, then letters, digits or
`_` — no `-` and no `.`); the VERSION half, when written, additionally
admits `.` and `-`. A `/` with nothing after it is refused by name.

- **`oracle python` and `oracle pcre2` keep their EXACT current
  meanings** — they are engine-refs with no version — so nothing in the
  existing corpus moves.
- **A version PINS what a correctness claim was checked against**:
  `oracle pcre2/10.46`. It is part of the DECLARATION and is not a
  dispatch key — a consumer holding that engine at another version
  reports the mismatch as its own finding.
- **NAMING AN ORACLE A READER CANNOT REACH IS A LABELLED SKIP, NEVER A
  REFUSAL.** `oracle tre/0.8.0` names an engine this repository has no
  binding for, and that is not an error: pcrec's harness drives pcrec's
  own artifacts and has no second engine to consult, so it COUNTS the
  declaration and prints `oracle declarations skipped: N` in its summary
  rather than failing a block for naming something true. That rule is
  what makes widening the enum safe rather than a portability hazard: an
  absent oracle degrades to a counted, named skip, never a silent pass
  and never a hard failure.
- **`oracle` names the ENGINE, not the METHOD**, and it never selects
  what pcrec COMPILES — only what an expectation is checked against. A
  verification METHOD (including non-oracle methods) is written as a
  `tag method=<name>`, free-vocabulary like any other tag; folding the
  two would make a method with no engine behind it unspellable.
- `# pcre2-only` immediately before a `pattern` line is untouched by this
  production and keeps exactly the meaning "Oracle verification" above
  gives it.

## How the harness evaluates a block

For each pattern block, `run.sh` (`tests/harness/run.sh`):

1. Runs `$PCREC -p rx -o <tmp>/gen.c '<pattern>'` (plus any `flags`/
   `features`/`engine`/`budget`-derived options).
2. If the block is `perr`: scores it as described above and stops — no
   further steps run.
3. Otherwise, if `pcrec` failed to compile the pattern, every `m`/`n`/…
   case in the block is reported failed (with `pcrec`'s stderr included),
   and the pattern is counted once toward the "pattern-compile failures"
   total in the summary, however many cases it had.
4. Otherwise it compiles the generated matcher against the shared driver:
   `$CC $GENCFLAGS -I<tmp> -o <tmp>/t tests/harness/driver.c <tmp>/gen.c`.
   A failure here is a **harness-level failure** (broken codegen or a
   driver/compiler mismatch, not a single bad case), reported separately
   from ordinary case failures.
5. For each case, runs `<tmp>/t '<subject>' '<P>' '<route>'` and scores the
   result per "The driver protocol" below.

Before any of that, for a file whose first non-comment line is not
`pattern`, the harness makes ONE `pcrec --list-source` call and starts the
loop above at the `line` column of the first `pattern` row (see
"`--list-source`" below). The head is never parsed by the harness. Three
outcomes are distinct and stay distinct: the call FAILS (a harness
failure carrying pcrec's own diagnostic), the file has a head and no
`pattern` rows (zero blocks run, and the existing "no pattern blocks
parsed from file" failure fires on its own), or the loop starts at the
body. MEASURED: no file in `tests/` is head-bearing on its own, so no
plain corpus file makes the call by itself — an `include`-bearing file
(below) is the one shape that always does.

**[DD-13b.W23.3a] `include` AND THE ACCOUNTING UNIT.** A file whose head
carries one or more `include "path"` lines is an **entry**, and its
**closure** is the entry's own body plus every fragment its `include`
lines name, walked **depth first, in include order** — a fragment may
itself carry `include` lines, and those are followed the same way. A
**cell** is what the closure produces: one (block, cases) unit per
`pattern` block anywhere in the closure, entry or fragment, run as part
of the entry's own turn (never as an independent file of its own).

Three rules the harness enforces, each because a check needs it to be a
rule rather than an emergent property:

1. **A fragment is never its own entry.** A file that is BOTH separately
   discoverable (`.rxt`) and named by another file's `include` line is
   counted once, under the includer, whether or not it was also named
   explicitly — if it was named explicitly the summary says
   `<file>: named, absorbed into <entry>`.
2. **A failure names the FRAGMENT's own `file:line`**, never the entry's.
   The closure is one accounting unit; a diagnostic inside it still points
   at the physical file and line the author would open to fix it.
3. **An unresolved `include`, a second `include` of the same resolved real
   path in one closure, or a cycle is a RESOLUTION failure** — a fourth
   failure class beside a pattern-compile failure, a harness-level
   failure and an ordinary case failure. It is reported separately (a
   line tagged `[resolution]`) and counted toward the "pattern-compile
   failures" total for the ENTRY, on the same rule a `perr` block already
   follows: "this pattern does not compile" is true whether the resolver
   or `pcrec` said so, and the entry's own body still runs — a broken
   fragment does not delete the entry's own cases.

The summary gains two lines for this, printed unconditionally:
`entry files: N` (files run as entries, after the subtraction above) and
`fragments spliced: M` (fragments actually added to some entry's
closure). MEASURED: no file in `tests/` carries an `include` line today,
so `M` is 0 and `N` equals the corpus's own file count on every run.

Failures print as `file:line: expected ... got ...` beside the pattern
under test. The final summary reports total cases passed/failed, a
per-file failure breakdown, the distinct count of patterns that failed to
compile, the `group cases pending-vm: N` count, and **[DD-13b.W23.3]** two
counted, labelled skips — `under expectations skipped: N` and `oracle
declarations skipped: N`. Both lines print unconditionally, including at
zero, which is the point of counting them: a skip nobody counts is
indistinguishable from a line nobody parsed, and a file whose expectations
are all convention-qualified must read as "0 cases, N under-skips" rather
than as a file that quietly tested nothing.

## The driver protocol

`tests/harness/driver.c` is one small C program, shared by every case, that
adapts the generated match API to a CLI:

```
t <subject> [startpos] [route] [mode]
```

`<subject>` is the case's subject text with escapes still encoded exactly as
they appear inside the `.rxt` file's quotes. `[startpos]` defaults to `0`
(`run.sh` always passes it explicitly). `[route]` is the `frames-buffer=`
route documented above (`default`/absent, `null`, `<n>`, `<frames>,<trail>`)
and selects WHICH ENTRY answers — it changes nothing else about the call or
the protocol below, which is what makes a route a control rather than a
variant.

**[DD-13b.W23.3] `@<path>` AS THE SUBJECT ARGUMENT.** If the subject
argument's first byte is `@`, the rest of it is a PATH and the file's
bytes are the subject, **byte-exact**: no escape decoding, no NUL
handling, no encoding assumption, and no trailing-newline rule in either
direction. That is what makes the `@file:` case form of "Named subjects"
real rather than approximated — a subject carrying a NUL or ill-formed
UTF-8 reaches the matcher as the file holds it, which argv cannot express
at all. An empty file is a legitimate empty subject; an unreadable path
prints to stderr and **exits `2`**.

**The `@` prefix is a MARKER and therefore a collision, and it is closed
on the OTHER side**: a literal quoted subject whose first byte is `@` is
handed to the driver with that byte written `\x40`, which the decoder
below already produces as `@`. The escape is byte-exact rather than a
special case, so no quoted subject is unreachable.

**[DD-13b.W23.3] `[mode]` selects WHAT IS ASKED**, and its set is CLOSED
at two. `one` (or absent) is the single-search question every existing
invocation asks, unchanged. `count` runs `docs/spec/match_api.md` §3.1's
find-all loop and prints `count <n>` — the `mc` line's question, with the
empty-match advance going through the artifact's own `<prefix>_next_pos`
residual off the match's REPORTED START. An unrecognised mode is a usage
error (**exit `2`**), never a silent fall back to `one`: a mis-spelled
`count` would otherwise answer the wrong question and pass.

The driver:

1. Decodes escapes into a length-tracked byte buffer (the decoded bytes may
   include `\0`, so it never uses `strlen` on the result). An invalid
   escape prints to stderr and **exits `2`**. A `@<path>` subject skips
   this step entirely — its bytes are never decoded.
2. Parses `[startpos]`, if given, as a non-negative decimal integer; a
   malformed value **exits `2`**.
3. Calls the search entry named by `[route]` with `caps` declared
   `ptrdiff_t caps[RX_NCAPS][2]` — `RX_NCAPS` comes from the pattern's own
   generated `gen.h`, so the array is always exactly the size the artifact
   under test delivers.
4. On a match, prints `match` followed by every `caps[k][0] caps[k][1]`
   pair for `k` in `[0, RX_NCAPS)`, then a newline; on no match, prints
   `nomatch\n`. Either way it **exits `0`**. A `g`/`gp` case's own slot is
   read out of this line by position: fields `1+2*slot` and `2+2*slot`
   after the leading `match` token, so a `run.sh`-side check is a
   parsed-field comparison, never a whole-line compare (later fields are
   simply not looked at).
5. The search entry's return is three-valued, not boolean: a VM artifact
   can also GIVE UP (a negative `PCREC_ERR_STEPS`/`_FRAMES`/`_WORK`/
   `_RECURSE` sentinel; a DFA artifact never returns one), or return the
   below-the-floor `PCREC_ERR_INTERNAL`, which is not a give-up. On either,
   the driver prints the matching word (`steps`/`frames`/`work`/`recurse`/
   `internal`; an unrecognized negative code prints `giveup <N>`) and
   **exits `3`**. `run.sh` treats exit `3` as its own unconditional HARD
   failure for every case kind EXCEPT `gu`, which scores it against its
   expected word instead — the one case kind that WANTS this exit.
6. **On a non-`default` route only**, the driver additionally calls the
   artifact's anchored `<prefix>_match_in`/`<prefix>_match_caps_in` entries
   on the same subject and cross-checks them against their un-suffixed
   siblings (`<prefix>_match`/`<prefix>_match_caps`). Agreement is
   required exactly, EXCEPT that the two may differ if EITHER answer is a
   give-up — a smaller caller-supplied capacity may refuse what the
   default matches, and a larger one may match what the default refuses;
   that direction is the feature the check exists to allow. On the `null`
   route no divergence at all is permitted (`null` is defined to be the
   un-suffixed call). A disagreement outside that allowance **exits `4`**,
   the driver's own outcome, checked by `run.sh` ahead of every other
   branch (including `gu`) so no case kind can hide it.
7. **[DD-13b.W23.3] In mode `count` only**, steps 3-6 are replaced by the
   find-all loop: it prints `count <n>\n` and **exits `0`**. A GIVE-UP
   anywhere inside the loop is NOT a count — it prints its own word and
   **exits `3`** exactly as the single-search path does, because a
   partial count reported as a count is a wrong answer where a give-up is
   a named outcome. The routed cross-check of step 6 is not offered in
   this mode and `run.sh` keeps an `mc`-bearing case off the routed path:
   `mc` asks about the artifact's ANSWER, and the `_in` entries answer
   the same question through different storage.

Exit codes, summarized: `0` match/nomatch or a `count`, `2` malformed CLI
input (startpos, escape, unreadable `@<path>` or unknown mode), `3`
give-up or internal-error code (HARD failure
unless the case is `gu`), `4` an anchored `_in` entry disagreeing with its
sibling beyond the give-up allowance (HARD failure for every case kind).
`run.sh` additionally treats `>=124` as a compile/run timeout and `>=126`
(other than the exit codes above) as a crash, both HARD failures.

**Every compile and every matcher run in the harness is bounded** (D45):
generated-code compiles run under a CPU-primary budget with a wall
backstop (`gen_cc`, `tests/lib/gen_timeout.sh`), pcrec's own invocation is
bounded separately, and matcher execution is bounded and RSS-capped
(`gen_run`/`gen_run_secs`). Exceeding a bound is a loud, named FAILURE,
never a hang or a silent skip. The exact numbers, their calibration
history, and the coverage sweep that closed the remaining bare call sites
are process record — `docs/testing.md`'s "D45 — every generated-code
compile runs under a budget" carries them; this document states only that
the bound exists and fails loudly, since the numbers are recalibrated by
measurement independent of the format itself.

**A usage note**: `--engine=vm` disables the DFA prefilter, so it is a
diagnostic mode, not a faster path — a `.rxt` block that forces it over a
large subject should also carry an explicit `budget` line, since the
default budgets are calibrated against the prefiltered path.

## Organizing tests by component

Per `APPROACH.md` §7, test files live in one directory per compiler
component, mirroring `APPROACH.md`'s component ladder:

```
tests/
├── harness/       run.sh, driver.c (this document describes both)
├── base/          literals, ., [...] classes, |, quantifiers, ^ $, groups
├── captures/      (...), (?<name>...), numbered/named capture
├── classes/       POSIX classes, \d \w \s and negations
├── assertions/    \b \B \A \z \Z, multiline ^ $
├── lookaround/    (?= (?! (?<= (?<!
├── backrefs/      \1, \k<name>
├── modifiers/     (?i) (?m) (?s) (?x), inline and scoped
├── unicode/       \p{...} and friends (UTF-8 tier)
├── advanced/      conditionals, atomic groups, possessive quantifiers, recursion
└── bench/         throughput + compile-speed budgets (not .rxt)
```

Each directory holds one or more `*.rxt` files; there is no required naming
scheme within a directory beyond `*.rxt`, though grouping by sub-feature
(e.g. `tests/base/quantifiers.rxt`, `tests/base/anchors.rxt`) keeps
failures easy to scan. See `tests/CLAUDE.md` for the current, per-directory
roster of what each one covers, its oracle rule, and its own supplementary
checks (differential drivers, structural/identity gates) that no `.rxt`
block can express.

### Adding a new component test directory

1. Create `tests/<component>/` and add one or more `.rxt` files following
   the format above. `run.sh` picks up any `*.rxt` under `tests/`
   automatically — no registration step needed.
2. If the component isn't implemented yet, its tests should assert the
   clean "module required" compile error via `perr`, per `APPROACH.md` §7's
   *expected-unsupported* policy — this keeps the suite green at every
   milestone rather than red until the component lands. A generated corpus
   can do this without losing the oracle: drive the real answer through the
   target oracle at authoring time, render the block as `perr` (pinning the
   refusal that must exist today), and keep the driven answer alongside it
   in a comment so landing the module is "delete one generator argument and
   re-run" rather than a rewrite (`tests/recursion/gen_corpus.py`'s
   `wave=` argument is the worked example).
3. Once the component is implemented, replace or extend those `perr` blocks
   with real `pattern`/`m`/`n`/… cases.
4. Run `bash tests/harness/run.sh tests/<component>` to iterate on just
   that directory while developing it.
5. A cell whose correct answer is DISPUTED, not merely unbuilt, is not a
   `perr` case: move it to `tests/known_fail/` instead (the ratchet that
   fails loudly if a parked cell starts passing — `tests/known_fail/
   CLAUDE.md`), leaving a comment at its former position saying where it
   went and why. `perr` pins a refusal that must exist; `known_fail` pins
   an answer pcrec currently disagrees with.
6. Every directory added or re-roled gets its own CLAUDE.md entry (or a new
   CLAUDE.md), per this repository's convention — see `tests/CLAUDE.md` for
   the existing entries' shape (oracle rule, corpus size, own checks).

## Drift found and fixed by this document

- **`perr`'s exit-code contract was stated too loosely.** The prior prose
  said `pcrec` "must exit nonzero"; the parser (`tests/harness/run.sh:
  338-350`) actually requires exit **exactly `1`** — a crash or timeout is
  nonzero too but is scored as its own distinct failure ("CRASHED or timed
  out ... instead of cleanly rejecting"), not as a satisfied `perr`. Fixed
  above; the parser was not changed.
- **The `<prefix>_match_in`/`<prefix>_match_caps_in` anchored-entry
  cross-check (driver exit `4`) was undocumented in prose anywhere in
  `docs/testing.md`**, though it is live, parser-enforced behavior on every
  non-`default` route (`tests/harness/driver.c:344-386`,
  `tests/harness/run.sh:440-465`). Added above under "The driver protocol",
  point 6.
- **`RXTFLAGS` was documented in `tests/harness/run.sh`'s own header
  comment (`tests/harness/run.sh:13-22`) but had no row in
  `docs/testing.md`'s environment-variable table.** `docs/testing.md`
  gained the row in the same change that created this document (see its
  own note).
