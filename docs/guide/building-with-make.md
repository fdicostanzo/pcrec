# Building with make

pcrec's CLI is shaped like `gcc`: it takes source files as positional
operands and writes compiled output with `-o`. That shape exists so
compiling your patterns is an ordinary Makefile build step, not a special
case. This chapter walks the worked example under
[`examples/makefile/`](../../examples/makefile/); read that directory
alongside this chapter rather than copying from here — it's the thing
that actually gets built and run by pcrec's own test suite, so it can't
go stale the way a doc snippet can.

## The `.rxt` source

A pattern you want to compile lives in a `.rxt` file — the same format
pcrec's own test corpus uses, described in full in
[`docs/spec/rxt_format.md`](../spec/rxt_format.md). For a build step, the
part that matters is the head-and-body shape: a `target` line names an
artifact, and a `pattern` block gives it a pattern.

```
target greet = hello

pattern hello, ([A-Za-z]+)!
name hello
```

`examples/makefile/src/greeting.rxt` is exactly this. A file can hold
several independent patterns, each with its own `target` line —
`examples/makefile/src/numbers.rxt` declares two (`digits` and `money`).
If a file has no `target` line and exactly one unnamed pattern block, it
still builds — as `target rx` — which is what lets a plain single-pattern
`.rxt` file compile with no head at all.

## One `pcrec` call, several files, several artifacts

```sh
pcrec -o gen/ src/*.rxt
```

A positional operand that names an existing file is a `.rxt` source to
compile — never a literal pattern (that's `--pattern`, below). You can
give several files at once; pcrec pools every `target` they declare
into one flat list before deciding what `-o` means. Point `-o` at an
existing directory and you get one `.c`/`.h` pair per target, named after
its prefix — this one call builds all three targets across
`greeting.rxt` and `numbers.rxt`.

If you only have one target in play, `-o` can instead name a single file
(exactly like the single-pattern form) or `-o -` for one self-contained
`.c` on stdout. Giving `-o` a plain filename over several pooled targets
is refused — it can't know which target you meant — naming the targets
and pointing you at `--target NAME` or an output directory instead.

## Compiling a literal pattern instead of a file

The two ways of giving pcrec something to compile are mutually
exclusive: a file operand, or `--pattern 'PATTERN'`. This is the flip
side of [getting started](getting-started.md)'s first example — `pcrec
-o matcher.c --pattern 'a(b|c)+d'` compiles a literal pattern with no
`.rxt` file involved. You can't combine the two: a build either compiles
files, or compiles one typed-in pattern, never both in the same
invocation.

## The Makefile shape

`examples/makefile/Makefile` is the whole recipe: one `pcrec` call turns
every `.rxt` file under `src/` into `gen/*.c`/`.h`, each gets compiled to
a `.o`, `ar` archives them into `libmatchers.a`, and a small consumer
(`main.c`) links against it. Build and run it yourself:

```sh
make -C ../..          # build ../../build/pcrec, once
cd examples/makefile
make
./example
```

Two things worth noticing when you read the Makefile:

- The rule that calls `pcrec` depends on the `.rxt` sources and writes a
  stamp file, because make resolves a rule's prerequisites before any
  recipe runs and the `gen/` directory (and the file names inside it)
  don't exist yet on a fresh checkout — you can't glob for outputs that
  aren't there. The prefix list is written out for the same reason.
- Nothing in the Makefile or under `src/` invokes a C compiler on
  pcrec's behalf. pcrec writes `.c`/`.h` pairs; your Makefile decides how
  they get compiled and linked, exactly as if they were any other
  generated source. pcrec never calls `gcc` itself.

## Library references (`-I` / `--lib-path`)

If your `.rxt` sources reference a shared library file (`lib "path"` in
the head), `-I DIR` — or its long form, `--lib-path DIR` — adds a search
directory, in the order given, after each source file's own directory.
It's repeatable, the one flag in this CLI that accumulates instead of
replacing. The worked example here doesn't use one; the full resolution
and scoping rules (including what a definition inside a library exports
to its caller) are in
[`docs/spec/cli.md`](../spec/cli.md) §1.1 and
[`docs/spec/rxt_format.md`](../spec/rxt_format.md).

## Per-target build options live in the file, not the flag

A `.rxt` source can set its own compile options — encoding, engine,
tuning, feature list — in a `target`'s config. When it does, **the
file's value wins over the same flag on the command line**, on exactly
the axes the file speaks about; everything else you pass on the command
line still applies untouched. That's deliberate: a source file states
the build its patterns are meant to have, and that shouldn't silently
change depending on who invokes `pcrec`. If you need the command line to
win on an axis the file sets, the answer is to remove it from the file,
not to expect the flag to override it. `--engine` is the one named
exception — an explicit `--engine=` on the command line wins and reports
the conflict, non-fatally, on stderr. The full precedence rules,
including that exception, are in
[`docs/spec/cli.md`](../spec/cli.md) §1.1.

## Next

- What the generated `.c`/`.h` pair actually gives you to call:
  [using the matcher from C](using-the-matcher-from-c.md).
- The `.rxt` format in full: [`docs/spec/rxt_format.md`](../spec/rxt_format.md).
- Every flag this chapter used: [`docs/spec/cli.md`](../spec/cli.md).
