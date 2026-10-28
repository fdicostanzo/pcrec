# Embedded code: C inside a pattern

Some checks are easy in C and painful in a regex: "a number from 0 to
255", "a date that exists", "a key that is in my table". Module `code-c`
lets a pattern carry a small piece of C that runs at one point in the
match and says "keep going" or "back off". pcrec compiles that C into the
generated matcher; nothing runs at compile time. The exact contract is
[`docs/spec/match_api.md`](../spec/match_api.md) §11.9 (embedded code) and
§11.10 (the span helpers); §11.1-§11.8 are the callout rules it shares.

## The shape

```
(?C`c: return rx_in(RX_CAP(1), 0, 255) ? RX_PASS : RX_FAIL;`)
```

It is PCRE2's own string callout. The string starts with the language tag
`c` and a `:`, and the rest is the body of a C function that returns
`RX_PASS` (continue the match here) or `RX_FAIL` (back off and try
something else). PCRE2 sees the same bytes as an ordinary string callout.
The macros `RX_CAP(n)`, `RX_CAP_P(n)`, `RX_CAP_LEN(n)`, `RX_POS` and the rest
read the match so far. The `rx_` helpers (`rx_eq`, `rx_in`, `rx_u64`,
`rx_find`, ...) work on a group's bytes without copying them.

## You must grant it

Code in a pattern is code that ends up in your program, so pcrec compiles
it only when you ask for it in the command, not in the pattern or in a
feature list:

    pcrec --allow-code=c ip.rxt -o ip.c

Without `--allow-code=c` the segment is refused by name and no file is
written. Through the library, set `pcrec_options.allow_code` to `"c"`.
`--features all` does not include it, and code in a definition pulled in
from another file (through `lib` or `include`) is refused even with the
grant. Only the file you named, `--pattern` text and your own library call
count as local.

## A validator: anchor it

An IPv4 address whose octets are at most 255, as one `.rxt` line:

```
pattern ^(\d{1,3})(?C`c: return rx_in(RX_CAP(1), 0, 255) ? RX_PASS : RX_FAIL;`)\.(\d{1,3})(?C`c: return rx_in(RX_CAP(2), 0, 255) ? RX_PASS : RX_FAIL;`)\.(\d{1,3})(?C`c: return rx_in(RX_CAP(3), 0, 255) ? RX_PASS : RX_FAIL;`)\.(\d{1,3})(?C`c: return rx_in(RX_CAP(4), 0, 255) ? RX_PASS : RX_FAIL;`)$
```

Compile it with the grant, link `ip.c` with your program and call
`rx_search`: `10.0.0.1` and `255.255.255.255` match; `10.0.0.256` and
`999.1.1.1` do not.

Keep the `^` and `$`. Without them this is a search, not a validator: on
`999.1.1.1` the first octet fails at offset 0, the search moves on, and
it finds `99.1.1.1` starting at offset 1. The code ran and said no; the
search found a different match that it accepts.

## `once`

A site normally runs every time the matcher reaches it, including
retries after backtracking, so code with side effects (counting, logging)
can run more than once per match. The `once` attribute,
``(?C`c,once: ...`)``, is a promise that the site cannot be retried, and
pcrec checks it: with `^\d{3}` before the site it compiles; with `^\d+` it
is refused, naming the quantifier and offering a fix (`\d++`) that does
not change what matches.

## Escaping, one layer at a time

Most errors come from mixing up the layers:

1. **The callout string.** The code ends at the first closing delimiter
   that is not doubled. Backticks are the easy choice because C rarely
   uses them; `$` works too. A doubled delimiter is one byte of code, so
   with `"` as the delimiter a C string `"a"` is written `""a""`.
2. **The `.rxt` file.** A `pattern` line is raw text: no extra escaping.
3. **The shell.** Put `--pattern` text in single quotes. A C character
   constant like `'x'` then needs the usual `'\''` dance, or put the
   pattern in a `.rxt` file instead.
4. **A C string literal** (a library call): escape `\` and `"` as for any
   C string, so `\d` becomes `"\\d"`.

## Your own functions

To call your own C, add a `code-header c "myfile.h"` line to the `.rxt`
file (or `--code-header c:myfile.h` with `--pattern`). pcrec writes the
`#include` into the generated `.c` without opening the file, so put the
header where your compiler finds it. A compile error in your code is
reported at the `.rxt` file and line where you wrote it.

Each generated header also defines `<PREFIX>_CODE_LANGS`, listing the code
languages compiled in (`"c"`), so a build can see that a matcher carries
embedded code.
