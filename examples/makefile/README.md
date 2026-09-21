# examples/makefile — pcrec as a build step

The shape [REL-1.10] (D118) exists for: `pcrec` compiling `.rxt` sources
inside an ordinary Makefile, the way you would compile any other generated
source.

## Layout

- `src/greeting.rxt` — one target, `greet`, matching `hello, NAME!` and
  capturing `NAME`.
- `src/numbers.rxt` — two targets in one file, `digits` and `money`,
  demonstrating that a `target` line is per pattern, not per file.
- `Makefile` — builds `gen/*.c`/`.h` from every `.rxt` file under `src/`
  in ONE `pcrec` call, compiles each to a `.o`, archives them into
  `libmatchers.a`, and links `main.c` against it as `example`.
- `main.c` — a tiny consumer: calls `greet_search` and `digits_search`
  from the generated headers and prints what they matched.

## Build and run

```sh
make -C ../..            # builds ../../build/pcrec, once
make                      # builds this example against it
./example
```

`PCREC` defaults to `../../build/pcrec`; override it to point at any other
built `pcrec` (`make PCREC=/path/to/pcrec`). `CC`/`AR` default to `gcc`/`ar`
and can be overridden the same way.

## What to look at

- The `Makefile`'s `gen/.stamp` rule is the whole of the CLI's build-step
  contract: one `pcrec -o gen/ $(SRCS)` call, given every `.rxt` file
  under `src/` at once, writes one `.c`/`.h` pair per target it declares
  (`docs/spec/cli.md` §1.1). `src/numbers.rxt` alone contributes two of
  the three.
- `libmatchers.a` holds one object per target; `nm` shows each one's
  `<prefix>_search` entry point.
- Nothing under `src/` or in the `Makefile` calls `gcc` — that is this
  Makefile's own job, never pcrec's (D118 item 4: pcrec does not invoke a
  C compiler itself).
