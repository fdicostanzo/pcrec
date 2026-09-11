# msgtrim — shorten four `.rxt`-source refusal messages (2026-09-10)

Frank-ruled task: `tests/rxtsource/run_rxtsource_tests.sh`'s W1.2
truncation CLASS check and its W1.3 duplicate-definition refusal check
both fail on darwin. macOS's default `TMPDIR` (`/var/folders/<hash>/T/`,
measured ~49 bytes on this box) makes the embedded fixture paths long
enough to push several refusal messages past `pcrec_error.msg`'s fixed
256-byte buffer — the ruled remedy (stated in the checks' own text) is to
shorten the message prose, never raise the buffer.

## Sites fixed

Four call sites, two files, no other files touched.

### 1. `src/parse/rxt_source.c` — no-such-definition refusal (~line 1857)

An earlier fix already reordered this message contract-first (comment at
the site records that history) and shortened the `lib`-chain rendering
(`lib_chain_text`, unchanged here). It was still landing AT the 263-byte
class-check limit on this box.

- **Old**: `"'target %s' names no definition '%s': no pattern block here
  has that name; searched %s (a lib's definitions need the composer,
  W1.3)"`
- **New**: `"'target %s' -> no definition '%s'; searched %s"`

Needles preserved: `'level_filter'` (the `%s` substitution), `'no
definition'`, `'searched'`.

### 2. `src/parse/rxt_source.c` — lib-STORE refusal (~line 1733)

- **Old**: `"'lib %s' is a library-STORE reference, which is NOT IN THIS
  BUILD (the store scan arrives with [LIB]; the spelling is real, not a
  typo). The \"path\" form resolves today"`
- **New**: `"'lib %s' is a STORE reference: NOT IN THIS BUILD (see [LIB]);
  use a \"path\" instead"`

Needles preserved: `'<common>'` (the `%s`), `'NOT IN THIS BUILD'`, `'LIB'`
(via `[LIB]`).

### 3. `src/parse/rxt_source.c` — duplicate-definition-across-the-closure
refusal (~line 1650, `closure_walk`)

**The worst case of the four**: this is the only site with TWO full
paths under one message — `rxt_fail`'s own `<path>:<line>: ` prefix names
the file currently being scanned, and the body's `%s:%zu` names the file
where the name was first declared. Both grow with `TMPDIR` at once, so it
needed the tightest prose of the four and two rounds of trimming (the
first round, matching the other three sites' style, still measured
truncating the second file's own `.rxt` extension on a sufficiently long
scratch directory).

- **Old**: `"definition '%s' is declared twice in the lib closure: also
  at %s:%zu"`
- **New**: `"'%s' dup: %s:%zu"`

Needles preserved: `"word"` (the `%s` group/definition name — literal in
the fixture), `"common.rxt"` (the current-file path, via `rxt_fail`'s own
prefix), `"compose_dup_definition.rxt"` (the other-file path, the `%s`
that was being cut).

### 4. `cli/main.c` — config's `pcrec` line escape refusal (~line 833,
`apply_target`)

Not on `pcrec_error.msg`'s buffer at all (`apply_target` writes straight
to `stderr` via `fprintf`, no fixed-size destination) — but it joins the
same truncation CLASS check in `run_rxtsource_tests.sh`'s loop and its
`cli->source` operand grows with `TMPDIR` exactly like `rxt_fail`'s
prefix does, so the same "shorten prose, keep path and content" rule
applies for the check to see consistent headroom rather than a message
that happens not to hit a buffer it was never near.

- **Old**: `"a \`config\` block's \`pcrec\` line may set compile options
  only — not an output path, a pattern, a prefix, a query mode or another
  source ('%s')"`
- **New**: `"\`pcrec\` line: compile options only, not
  output/pattern/prefix/query/source: '%s'"`

Needles preserved: `'compile options only'`, `'prefix'`.

## Worst-case byte math (measured, not eyeballed)

This box's `TMPDIR`: **49 bytes** (`/var/folders/sj/jbcblbpx13n6342cgcfhgbxr0000gn/T/`).
The real test harness builds its fixture directory under it as
`mktemp -d "$TMPDIR/pcrec-rxtsource.XXXXXX"` then `$WORKDIR/fix/` — a
**77-byte directory prefix**, measured directly (`printf '%s' "$W/fix/" |
wc -c`).

Reproduced each fixture against a real `mktemp`-generated `TMPDIR`-based
directory (not a hand-typed path) and measured total `stderr` bytes
(`wc -c` on `pcrec: ... \n`), against the check's 263-byte limit
(`pcrec_error.msg`'s 256 bytes minus 1 for NUL, plus the `"pcrec: "`
7-byte prefix `fprintf`s, plus the newline):

| fixture | old (measured before fix) | new (measured after fix) | margin |
|---|---|---|---|
| `no_such_definition` | 263 (at limit, failing) | 231 | 32 B |
| `lib_store` | 263 (at limit, failing) | 214 | 49 B |
| `config_pcrec_escape` | 268 (failing) | 229 | 34 B |
| `compose_dup_definition` (W1.3, two paths) | truncated (needle missing) | 218 | 45 B |

The first three rows above were measured under an even LONGER path
(a 101-byte fixed scratch-directory prefix, deliberately used as a
stress test before falling back to the real `TMPDIR`-based harness
shape) — so their margins against the REALISTIC 77-byte harness prefix
are larger still, estimated **56, 73 and 58 bytes** respectively (each
extra byte of directory-prefix length costs the message exactly one
byte, since each embeds the path once). The fourth row, `compose_dup_definition`,
was measured directly against the real `mktemp`-based harness directory
(two embedded paths, so each extra `TMPDIR` byte costs this message
**two** bytes of budget — the reason it needed two trimming passes and
carries the smallest per-`TMPDIR`-byte margin of the four: roughly 22
extra bytes of directory growth before it would need trimming again,
against 30–70+ bytes for the other three).

All four now sit comfortably under the 263-byte class-check limit with
today's TMPDIR, and would tolerate TMPDIR (or the mktemp suffix/fixture
directory nesting) growing by several dozen bytes before any of them
approached the buffer again.

## Pinned-wording audit (D94: every reader found by grep)

Grepped the whole tree for distinctive phrases of all four OLD messages
(`"is declared twice in the lib closure"`, `"library-STORE reference,
which is"`, `"names no definition"`, `"no pattern block here has that
name"`, `"definitions need the composer"`, `` "a `config` block's `pcrec`
line may set" ``, `"not an output path, a pattern, a"`):

- **`docs/dev/lanes/w13_report.md`** quotes the old duplicate-definition
  wording verbatim (as history). Per `docs/dev/lanes/CLAUDE.md`, lane
  reports are historical once merged and are never edited afterward — left
  untouched, correctly.
- **`tests/rxtsource/CLAUDE.md`** says "resolution refusals (no such
  definition, an unresolvable `lib` path, a ...)" — a category
  description, not a literal needle; the new wording still says "no
  definition", so this stays true and needed no edit.
- **`tests/rxtsource/run_rxtsource_tests.sh`**'s own `w12_refuse` needle
  list (`'compile options only'`, `'prefix'`, etc.) — every needle used
  by the four `w12_refuse`/`w13_refuse` calls for these sites was checked
  against the NEW wording before landing; all preserved (see per-site
  sections above).
- **`docs/spec/cli.md`** (lines 447, 750) describes the duplicate-
  definition BEHAVIOR ("refused, naming both files") rather than quoting
  wording — still true of the new message, no spec hunk needed.
- **`docs/spec/rxt_format.md`** quotes `"NOT IN THIS BUILD"` — preserved
  verbatim in the new lib-STORE message.
- No other `.sh`/`.py`/`.md`/`.c`/`.h` file in the tree matched any of
  the old phrases.

No `docs/spec/` hunk was needed: this is a diagnostic-wording change at
D26's loosest tier (pcrec's own message, not a PCRE2 wording match), and
every caller-observable FACT (which refusal fires, on what, naming what)
is unchanged — only the prose around the same contract content.

## Confirmed: compiler diagnostic path, not emitted text

Both files touched (`src/parse/rxt_source.c`, `cli/main.c`) are the
compiler's own CLI/parser diagnostic paths — `rxt_fail` writes into
`pcrec_error.msg`, and `apply_target`'s `fprintf` goes straight to the
process's own `stderr`. Neither writes into `src/gen/`'s emitted-C
templates or the `StrBuf` that becomes an artifact's `.c`/`.h` text. No
emitted text was touched; **no `abi` bump, no identity-gate re-pin**.

## Validation (all run in this worktree)

- **`tests/rxtsource/run_rxtsource_tests.sh`**: **115 passed / 3 failed
  before -> 117 passed / 1 failed after.** The one remaining failure is
  **C3** (`verify_rxt.py`'s python-oracle re-run), reporting its
  pre-existing, separately-ruled-pending divergences in `caseless.rxt`,
  `counterk.rxt` and `captures.rxt` (plus the `d27_k23_...` bounded-time
  skip) — untouched by this change, and explicitly named in the brief as
  expected to still fail. **W1.2's truncation check and W1.3's
  duplicate-definition refusal check both flipped to PASS.**
- **`make strict`**: `strict: whole tree compiles clean with -Werror
  -Wshadow`.
- **`tests/cli/run_cli_tests.sh`** (targeted, since `cli/main.c` was
  touched): **284 passed / 0 failed**, plus the `--warn-emit-bytes`
  section (4/4).
- No other section's script grep-matched any of the old wording (see the
  pinned-wording audit above), so no further targeted run was needed.
  `make test` was not run — the change is two isolated diagnostic-string
  edits in the compiler's own error path, confirmed by grep to have no
  other readers, with `make strict` and the two directly-relevant
  sections (`rxtsource`, `cli`) both green; full-battery validation is
  the manager's at merge per `BOILERPLATE.md`.

## Validation status

**COMPLETE** for the delivery bar in the brief — no numbers owed. Branch
`lane/msgtrim`, one commit, this report committed alongside it.
