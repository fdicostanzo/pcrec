# Encodings and subjects

## Byte vs UTF-8

pcrec compiles two subject encodings, chosen per pattern at compile time
with `-e byte|utf8` (or `PCREC_ENC_BYTE`/`PCREC_ENC_UTF8` in the library):

- **`byte`** (the default) — 8-bit clean, no notion of "character" above
  a single byte, no Unicode meaning.
- **`utf8`** — a character is one to four bytes; `.` and a character
  class match a whole character; `\x{…}` accepts code points above
  `0xFF`. There's no validation pass: an ill-formed byte sequence in the
  subject simply matches nothing, because the byte-wise automaton has no
  path through it — not an error, just a dead end.

This is a per-compile choice, never a process-wide setting: two patterns
in the same binary can use different encodings, because there's no global
to set.

One consequence of UTF-8 worth knowing before it surprises you: a
`startpos` you pass to `<prefix>_search` must land on a character
boundary. A position inside a multi-byte character is refused outright
(`PCREC_ERR_STARTPOS`) rather than silently rounded to the nearest
boundary. `<prefix>_next_pos` is the supported way to produce a valid
`startpos` — use it when scanning for successive matches, and you'll
never hit this.

## Subjects are length-counted; patterns are NUL-terminated

This is an asymmetry between the two strings pcrec deals with, and it's
worth stating plainly because it isn't obvious from the signatures alone:

- **A subject** you hand to `<prefix>_search`/`_match` is `(s, n)` —
  length-counted, never NUL-terminated. The matcher never reads `s[n]`,
  and a subject may contain embedded NUL bytes freely.
- **A pattern** you hand to `pcrec_compile()` (or type as `--pattern`) is
  a plain NUL-terminated C string with no length parameter. A raw `0x00`
  byte inside a pattern silently truncates it — the compile succeeds, on
  the shorter pattern, with no warning. If you're building a pattern
  string programmatically and it might contain a NUL, check for one
  yourself before compiling (a `strlen` pre-flight), or use
  `--pattern-esc` at the CLI, whose escaped form refuses an embedded
  `\x00` by name.

## Newline convention

pcrec is fixed at PCRE2's own default newline convention (`NEWLINE_LF`):
`$` matches at the end of the subject, and also immediately before a
trailing `\n`. There's no flag today to change this. If you want a
pattern to match only at the true end of the subject regardless of a
trailing newline, anchor with `(?:PATTERN)\z` instead of ending in `$` —
`\z` never admits a trailing newline, where `$` does.

## What `-i` folds

`-i` (or `PCREC_CASELESS`) folds case at compile time, into the
automaton — there's no runtime cost, no flag, and no `tolower()` call in
the generated matcher. **Which characters fold is a property of the
encoding, and the two disagree rather than nest:**

| under | folds by |
|---|---|
| `byte` (default) | the 52 ASCII letters only |
| `utf8` | full Unicode simple case folding |

So `(?i)k` matches `k` and `K` under either encoding, but under `utf8` it
also matches U+212A KELVIN SIGN — a fold partner nowhere near the letter
`k` visually, reached because folding operates on code points before any
byte-level lowering. A named byte class like `\d`/`\w`/`\s` or a POSIX
bracket never gains Unicode fold partners this way; only a literal
character or an explicit range does.

## Next

- What "byte" vs "the fold" means for the constructs you can use:
  [features and modules](features-and-modules.md).
- The exact rules and measurements behind everything on this page:
  [`docs/spec/cli.md`](../spec/cli.md) §1 (`-e`, `-i`).
