# The `.rxt` test format and driver protocol

This is the contract for `.rxt`, pcrec's test-corpus format, and for the
harness that runs it: what a `.rxt` file may say, what `tests/harness/run.sh`
does with each line, and what `tests/harness/driver.c` prints and exits with.
Read this before adding a `.rxt` file or a new component test directory.

Every claim below is checked against `tests/harness/run.sh` and
`tests/harness/driver.c` at this worktree's branch point (`d39ce94`); code
citations are `file:line`. Where this document and the parser disagreed, the
parser won — see "Drift found and fixed" at the bottom.

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

Four file-level declarations exist in this build:

| declaration | means |
|---|---|
| `lib "path"` / `lib <store>` | a subpattern library this file draws definitions from. The path reference has C's own two spellings: `"local"` and `<store-name>`. **The `"path"` form is RESOLVED as far as existence** (against the source file's own directory, then each `pcrec --lib-path` in order) and refused by name if it names no readable file; its CONTENTS are not read, so no pattern can call a definition that lives in it. `<store-name>` is refused as NOT IN THIS BUILD |
| `target <prefix> = <definition> [with <c1,c2>]` | an artifact to build: its symbol prefix, the definition it is built from, and the configs it is built under. **BUILT** since [DD-13b.W1.2] — see "Building from a source file" below |
| `config <name> [from <c1,c2>]` | a named build configuration, with an indented body |
| `description <text>` | a machine-readable prose field — a FIELD, not a comment, so a script can summarize what a file holds. `#` comments go back to being operational notes |

A `config` body holds indented `pcrec` (raw pcrec flags), `flags`,
`features`, `encoding`, `engine` and `budget` lines — the same
productions a pattern block's own directives use, so the two cannot
disagree about what `budget frames=` means.

Keywords belonging to a later wave of this format (`include`, `tag`,
`freq`, `use`, `oracle`, `analysis`, `testee`, `option`, `mc`, `variant`)
are recognised and refused **by name, as NOT IN THIS BUILD** — never as
unknown. They are real, spelled correctly, and simply not implemented
here; reporting them as unknown would send a reader hunting a typo in a
word they just read in the format's own documentation.

### Building from a source file

`pcrec --source FILE -o OUT` builds this file's `target` declarations;
`docs/spec/cli.md` §1 is the command-line contract and states the `-o`
forms, `--target`, `--lib-path` and the precedence rules. What belongs to
the FORMAT rather than to the CLI is this:

- **A `target`'s definition is a pattern block's `name`**, which lives in
  the FILE namespace — the same namespace a block's `name` is unique in.
  A `target` may name a block that appears later in the file: the head
  precedes the body and resolution is a whole-file pass.
- **No `target` and exactly ONE UNNAMED pattern block means `target rx`.**
  That is what makes every file written before this format grew a head
  buildable without declaring anything.
- **No `target` and anything else builds NOTHING.** The file is a library
  of definitions; `pcrec` says so and exits 0. It is not an error, and it
  is a different outcome from a file `pcrec` refuses.
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

### Lexical rules

These bind on every line kind, old and new:

- **Whole-line `#` comments only.** A `#` anywhere but column 1 is data.
  The one comment with meaning is `# pcre2-only` immediately before a
  `pattern` line (see "Oracle verification").
- Blank lines are ignored.
- **A line kind is its first whitespace-delimited token**, and an unknown
  first token is a HARD ERROR — never a silent no-op, never a comment.
- **Each CONTEXT has its own closed vocabulary**, and a token unknown *in
  its context* is a hard error that NAMES the context. There are three:
  the head, a `config` body, and a pattern block. Nothing is a keyword
  everywhere — `pcrec` is a `config`-body line and not a block one;
  `perr` is a block line and not a head one.
- **IN THE HEAD, INDENTATION MEANS CONTINUATION.** A line indented by one
  or more spaces or tabs continues the declaration above it: a `config`
  body and a block scalar's own lines are the same rule. A head
  construct ends at the first non-indented line — **including a blank
  one** (r46sem finding 10, RULED): a blank line is not indented, so it
  terminates a `config` body or a block scalar's continuation exactly as
  any other non-indented line does, and a directive after it belongs to
  the file, not to whatever the blank line's continuation would have
  been.
- **A PATTERN BLOCK's lines are NOT indented**, and a block ends at the
  next `pattern` line or end of file. This asymmetry between head and
  body is deliberate and is the only one: the body's shape is fixed by
  compatibility with every existing file, and the head is new territory
  where indentation costs nothing.
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
  quoting, no escaping).
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
  offset 0 GIVES UP with the typed code `<code>`, one of `steps` / `frames`
  / `work` / `recurse` (`recurse` is `PCREC_ERR_RECURSE`, reserved with no
  producer yet, so no block can pass with it today — the directive still
  accepts the word). `internal` is REFUSED at parse time, by name:
  `PCREC_ERR_INTERNAL` is the artifact catching its own analysis/emission
  bug, never a planned outcome a corpus block gets to expect. Scored
  against the driver's exit `3` plus its printed word, the one case kind
  that WANTS that exit — see "The driver protocol" below.
- `name <ident>` — block-scoped: names the block. An `ident` is a PCRE2
  group name AND a C identifier (first byte a letter or `_`, then letters,
  digits or `_`), one rule, so a name that can be a group cannot fail to
  be a symbol later. **The name is in the FILE namespace**, not the
  pattern's group namespace, and must be unique within the file.
- `description <text>` — block-scoped: a machine-readable prose field for
  this block. One-line form only (see "Lexical rules" above).
- `encoding <ident>` — block-scoped: the subject encoding for this
  block's compile, passed as `--encoding=<ident>`. Per-block, never
  global, exactly as the CLI option is per-compile: two blocks in one file
  may use different encodings. Whether the named encoding is IMPLEMENTED
  is pcrec's answer, not the harness's — `utf8` is refused until milestone
  M5, and a block asking for it hears that from the compiler.
- `features only <list>` — as `features`, except that the list REPLACES
  what a `config` would otherwise contribute rather than being unioned
  with it. Parsed and recorded in this build; it becomes operative when
  `config` composition lands.
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
| 1 | `kind` | all | `lib` \| `target` \| `config` \| `description` \| `pattern` |
| 2 | `line` | all | 1-based first line of the declaration or block |
| 3 | `name` | target, config, pattern | the target's PREFIX; the config's name; the block's `name` (empty if unnamed) |
| 4 | `value` | lib, target, description, pattern | `lib`'s path reference; `target`'s definition name; a `description`'s text; a block's own `description` |
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

**Sectionless**, and the trigger for that changing is concrete. The table
contract's `#section` mechanism exists for one command emitting several
tables with different columns; it is declined here because the head/body
INTERLEAVING is exactly what a consumer of this output checks, and that
is expressible only as row order in ONE stream. Adopting sections later
is free (a stream with no `#section` line is a single anonymous section),
and what would earn it is a data block whose rows cannot be columns of
this table under any reading.

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
body. MEASURED: no file in `tests/` is head-bearing, so no existing file
makes the call.

Failures print as `file:line: expected ... got ...` beside the pattern
under test. The final summary reports total cases passed/failed, a
per-file failure breakdown, the distinct count of patterns that failed to
compile, and the `group cases pending-vm: N` count.

## The driver protocol

`tests/harness/driver.c` is one small C program, shared by every case, that
adapts the generated match API to a CLI:

```
t <subject> [startpos] [route]
```

`<subject>` is the case's subject text with escapes still encoded exactly as
they appear inside the `.rxt` file's quotes. `[startpos]` defaults to `0`
(`run.sh` always passes it explicitly). `[route]` is the `frames-buffer=`
route documented above (`default`/absent, `null`, `<n>`, `<frames>,<trail>`)
and selects WHICH ENTRY answers — it changes nothing else about the call or
the protocol below, which is what makes a route a control rather than a
variant.

The driver:

1. Decodes escapes into a length-tracked byte buffer (the decoded bytes may
   include `\0`, so it never uses `strlen` on the result). An invalid
   escape prints to stderr and **exits `2`**.
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

Exit codes, summarized: `0` match/nomatch, `2` malformed CLI input
(startpos or escape), `3` give-up or internal-error code (HARD failure
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
