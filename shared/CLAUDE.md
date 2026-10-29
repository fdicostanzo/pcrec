# shared/ — dependency-free leaf sources compiled into more than one binary

One implementation, compiled SEPARATELY into each binary that needs it, so
two binaries that must not link each other (`libpcrec`/`pcrec` and the
zero-dependency `build/pcrec-analyze`) still share one source instead of
keeping two copies. Design: `docs/design/inline_c.md` §5.5 (the one
SHA-256 home).

## Rules

- LEAF FILES ONLY: a file here includes nothing from `src/`, `lib/`, `cli/`,
  `analyze/` or `memfn/`, and depends on nothing beyond the C library
  (`stddef.h`, `stdint.h`, `string.h`). That is what lets `analyze/` keep
  its "reads nothing under src/" rule verbatim and `src/` never reach into
  `analyze/`.
- A file's control is an outside one (published vectors, a system tool),
  never one binary's output compared with the other's.
- Update this file when files are added or removed, and the Makefile's
  `SHAREDSRCS` and `tests/lib/lib_srcs.sh` with it.

## Files

- `sha256.h` / `sha256.c` — one-shot SHA-256 (FIPS 180-4),
  `pcrec_sha256_hex`. Readers: `analyze/main.c` (exemplar provenance
  digests) and `src/parse/rxt_source.c` (the `sha256 <hex64>` pin on an
  `include`/`lib` line, computed over the buffer the reader parses).
  Checked by `tests/code/run_code_tests.sh`'s pin arm (NIST vectors and
  `sha256sum` agreement over the corpus's pinned files).
