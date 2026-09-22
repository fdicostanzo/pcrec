# Using the library

Everything the CLI does to compile a pattern is also available as a C
library — `lib/pcrec.h` is the only public header, backed by
`build/libpcrec.a`. Use it when you want to compile patterns from inside
your own program instead of shelling out to `pcrec`. This chapter is a
complete, minimal example; [`docs/spec/match_api.md`](../spec/match_api.md)
§8 is the exact contract, including two guarantees worth knowing up
front: `pcrec_compile()` never aborts your process on a hostile pattern,
and a resource refusal (a pattern too large or too expensive to compile)
comes back through the same `-1`/`pcrec_error` path as a syntax error, so
check the message, not just the return value, if you want to tell them
apart.

## A complete program

This compiles, links against `build/libpcrec.a`, and runs as shown.

```c
#include <stdio.h>
#include "pcrec.h"

int main(void)
{
    pcrec_options opt;
    pcrec_output  out;
    pcrec_error   err;

    /* Mandatory first step. A zero-initialized pcrec_options has
       prefix == NULL, and pcrec refuses a NULL prefix outright. */
    pcrec_default_options(&opt);
    opt.header_name = "matcher.h";   /* NULL = self-contained .c, no header */
    opt.features = "all";            /* see the NULL note below */

    if (pcrec_compile("(?=a)b|[0-9]+", &opt, &out, &err) != 0) {
        fprintf(stderr, "pcrec: %s (at byte %zu)\n", err.msg, err.pos);
        return 1;
    }

    FILE *c = fopen("matcher.c", "w");
    if (c) { fputs(out.c_src, c); fclose(c); }
    if (out.h_src) {
        FILE *h = fopen("matcher.h", "w");
        if (h) { fputs(out.h_src, h); fclose(h); }
    }

    pcrec_output_free(&out);   /* frees both buffers, NULLs both fields */
    return 0;
}
```

Build it against the library and run it:

```sh
gcc -O2 -Ilib -o libdemo libdemo.c build/libpcrec.a
./libdemo
```

Four things in this example are contract, not style:

1. **`pcrec_default_options()` is mandatory.** Skipping it fails every
   compile — a zeroed struct has `prefix == NULL`.
2. **`pcrec_output` owns two `malloc`'d buffers, and you free them** with
   `pcrec_output_free()`, which is safe to call twice and safe on an
   output whose header was never produced.
3. **`h_src` is non-NULL exactly when you set `header_name`.** Test
   `h_src`, not `header_name`, before writing it.
4. **Check the return value.** `pcrec_compile()` returns `0` on success,
   `-1` on failure, and only fills `err` on failure.

## The `features` field — the one thing that will trip you up

`pcrec_options.features` is the library's equivalent of the CLI's
`--features` flag: a comma-separated module list, `"std1"`, `"all"`, or
`"none"`. **But its `NULL` default does NOT mean `"std1"`** — the CLI's
own bare-invocation default. `NULL` means "make no request", which today
resolves to pcrec's raw, all-off-except-base-grammar default. If you want
the CLI's own default module set, set `opt.features = "std1"` explicitly.
This is a real, deliberate asymmetry (not a bug you're working around),
and it's the one thing about this field a library user reliably trips
over — the example above sidesteps it entirely by asking for `"all"`,
since the pattern it compiles (`(?=a)b`, a lookaround) needs a module
`std1` doesn't include. `--features` and its module roster are the
subject of [features and modules](features-and-modules.md).

## Options you'll set most often

- `opt.prefix` — the symbol prefix (default `"rx"`, set by
  `pcrec_default_options`).
- `opt.encoding` — `PCREC_ENC_BYTE` (default) or `PCREC_ENC_UTF8`; see
  [encodings and subjects](encodings-and-subjects.md).
- `opt.flags` — a bitmask (`PCREC_CASELESS`, `PCREC_EMIT_MAIN`, …).
- `opt.engine` — `PCREC_ENGINE_AUTO` (default), `_DFA`, or `_VM`.
- `opt.header_name` — `NULL` for a self-contained `.c`, or a name for the
  matching header.

The full field list, including the tuning and budget knobs, is
`lib/pcrec.h` itself (every field is documented inline) and
[`docs/spec/match_api.md`](../spec/match_api.md) §8.2.

## Errors

`pcrec_error` is a fixed `{msg[256], pos, input}`: a human-readable
message, a byte offset into whichever input `input` names (today always
the pattern — nothing else feeds a compile yet), and that discriminator
itself. There's no error-code enum to switch on; read the message.

## Next

- What the generated `.c`/`.h` pair this produces gives you to call:
  [using the matcher from C](using-the-matcher-from-c.md).
- The module list `features` accepts:
  [features and modules](features-and-modules.md).
