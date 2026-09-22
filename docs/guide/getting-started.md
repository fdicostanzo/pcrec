# Getting started

pcrec is an ahead-of-time compiler: you give it a PCRE pattern, and it
writes out C source that matches exactly that pattern. There's no
interpreter and no runtime library — the C file it writes is
self-contained and depends only on a small ABI block it emits into its
own header.

## Build it

You need a C compiler and GNU make (see the top-level
[README.md](../../README.md) for the exact requirements).

```sh
make
```

This builds `build/pcrec` (the CLI) and `build/libpcrec.a` (the library,
for [using pcrec from your own C program](using-the-library.md) instead
of shelling out). Check what you built:

```sh
build/pcrec --version
```

prints one line, `pcrec 0.1.0-beta`, and exits.

## Compile your first pattern

```sh
build/pcrec -p rx --emit-main -o matcher.c --pattern 'a(b|c)+d'
gcc -O2 -o matcher matcher.c
./matcher 'xxabcbdyy'
```

This prints `match 2 7` — the span of the leftmost match in the subject
you gave on the command line. `--emit-main` is what makes the generated
file directly runnable this way (it appends a small `main()`); it's the
quickest way to try a pattern, but not how you'd use pcrec in a real
program — see [building with make](building-with-make.md) and [using the
matcher from C](using-the-matcher-from-c.md) for that.

## What just happened, flag by flag

- `-p rx` sets the prefix on every generated symbol (`rx_search`,
  `rx_match`, …). It defaults to `rx` if you leave it off.
- `--emit-main` appends a standalone `main()` that reads the subject from
  `argv[1]` and prints what it found. Its exit code is its own small
  vocabulary (0 match, 1 no-match, 2 usage, 3 give-up) — see
  [troubleshooting](troubleshooting.md) for how that relates to pcrec's
  own exit codes and to a matcher's give-up codes, which are three
  separate things that happen to share small integers.
- `-o matcher.c` is where the C goes.

## The two output files

`-o FILE` normally writes two files: `FILE` itself (the `.c`) and a
matching header with the same name but a `.h` extension. The header
declares everything a caller needs — the entry points, the capture-count
macro, the reflection structure — and the `.c` includes it. In the
example above there's only one file because `--emit-main` needs nothing
else to include; a pattern with captures, or one you intend to call from
another translation unit, gets both.

You can also ask for one self-contained file with no header at all:

```sh
build/pcrec -p rx -o - --pattern 'a(b|c)+d'
```

prints the whole `.c` — declarations and all — to stdout. That's the form
several of pcrec's own tests use to compare two artifacts byte for byte,
and it's a handy way to look at what a pattern compiles to without
littering a directory with files.

## Reading the generated header

Open the `.h` file pcrec wrote and you'll find, roughly top to bottom: a
shared ABI block (give-up codes, the `rx_ctx` type — identical text across
every artifact, prefix or not), then this artifact's own entry point
declarations, some capacity macros (`<PREFIX>_NCAPS` and friends), and an
`extern const struct rx_info <prefix>_info` — a reflection structure a
caller can read at runtime to ask what this artifact is (which engine,
which limits it was built under, and more). None of that is meant to be
memorized; [using the matcher from C](using-the-matcher-from-c.md) is the
guided tour, and [`docs/spec/match_api.md`](../spec/match_api.md) is the
exact contract behind it.

## Next

- Building more than one pattern into a real project:
  [building with make](building-with-make.md).
- Calling the matcher: [using the matcher from C](using-the-matcher-from-c.md).
- Compiling patterns from your own program instead of the CLI:
  [using the library](using-the-library.md).
