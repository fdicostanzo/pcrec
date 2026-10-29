# analyze/ — pcrec-analyze, the [FINDINGS] exemplar analyzer (end state)

`docs/design/findings/design.md` §10.1's END-STATE row, build step B6
(`docs/dev/lanes/findb6_report.md`): a **separate, zero-dependency binary**,
built by `make` into `build/pcrec-analyze`. It does not link `libpcrec.a`
and does not read anything under `src/`/`cli/`/`lib/` — its own tiny data
model (counters, a bundle-text writer, its own bundle-text reader for
`--merge`/`--check`) is entirely self-contained, and its one-shot SHA-256
is the dependency-free leaf `shared/sha256.c`, so a
clone that never builds `libpcrec` still gets this tool.

**NOT in `libpcrec` or `pcrec` (R27a)**: it is a standalone counting +
provenance tool, invoked by `third_party/*/generate.py` (the shipped `log`/
`weblog` bundles, [FINDINGS] B5) and validated end to end by
`pcrec --list-analysis NAME -I <dir>` parsing its output.

**The ONE counter (R27b)**: `count.c` is the single implementation every
shipped generator calls. A generator never counts itself.

Ported 1:1 from `scripts/pcrec_analyze.py` (the B3 PROTOTYPE, now
DELETED — implement-then-replace, design.md §10.1/§12): same four command
forms (`--scan`/`--merge`/`--digest-only`/`--check`, design.md §10.2), same
output BYTES, proven agreement (in-tree fixtures + the two real shipped
corpora + 800+ seeded-random invocations, invalid UTF-8 included) while
both implementations existed — see `docs/dev/lanes/findb6_report.md` for
what the port found and `tests/findings/run_analyzer_pinned.py` for what
carries that proof forward now that there is no python left to compare
against.

## Files

- `analyze.h` — the shared data model: `Kind`/`KindBlock`/`Bundle`, the
  sparse code-point table (`CpTable`, open addressing), sharding, strict
  UTF-8, key rendering, `derive_serves` (design.md §10.2's collision-free
  split, [r2 M-B1]), `render_bundle`, `parse_bundle`, `read_whole_file`.
- `count.c` — every function `analyze.h` declares except CLI dispatch and
  SHA-256: the one-pass freq/bigram/cpfreq counters, the shard-bounds
  arithmetic (the `k=1` freq/cpfreq exception [r2 A-1], the cpfreq
  lead-byte ownership seam [r2 A-2]), strict UTF-8 decode (Unicode's
  well-formed-byte-sequence table — CPython's own "strict" `errors`
  handler, byte for byte: overlong forms, surrogates and code points past
  U+10FFFF are all refused per lead byte), the bundle text writer
  (`render_bundle`) and its own reader (`parse_bundle`, used by
  `--merge`/`--check` — a DELIBERATELY minimal reader for design.md §2.7's
  bundle subset, not the full `.rxt` schema, same scope
  `scripts/pcrec_analyze.py`'s own `parse_bundle` carried).
- SHA-256: NOT here since [INLINE-C] stage 3 — the tree's one
  implementation is `shared/sha256.{c,h}` (`pcrec_sha256_hex`), a leaf this
  binary compiles into itself and libpcrec compiles separately (neither
  links the other; shared/CLAUDE.md). It includes nothing of pcrec's, so
  this directory's independence rule holds as written.
- **[KNOW-SRC] K3 (lane ksrc23, 2026-10-17)**: `parse_bundle` also reads ONE
  whole `analysis` bundle as an author writes it (column-1 comments, blank
  and whitespace-only lines around it, the bundle's `include`/`description`,
  every data-block line, all eleven provenance fields, prose in block-scalar
  form; from `docs/spec/rxt_format.md`, never from pcrec's reader), keeping
  the blocks' FILE order; on this tool's own emitted subset it reads what it
  always did. `dump_doc` prints the DOCUMENT in `pcrec --list-analysis NAME
  --view=decoded`'s `#section decoded` shape, and `--dump-doc FILE` is its
  command: R3's and R5's independent side for pcrec's analysis kind
  (`tests/knowledge/`). It is the deliberate TWIN of pcrec's reader
  (measure_sets.md §9.1), which is why it may not share code with it.
- `main.c` — argv parsing (mirrors `scripts/pcrec_analyze.py`'s argparse
  wiring closely enough to be indistinguishable at the CLI) and the four
  command implementations (`cmd_scan`/`cmd_merge`/`cmd_digest_only`/
  `cmd_check`).

## Build

`make` builds `build/pcrec-analyze` as part of `all` (so a plain `make`
after a clone has it). `ANALYZEFLAGS` in the top-level Makefile is its own
small flag set (`$(CFLAGS) $(WARN) -std=gnu11`) — deliberately NOT
`$(ALLFLAGS)`, whose `-Ilib -Isrc` would misstate a dependency this binary
does not have. `make strict` covers `analyze/`'s two `.c` files (and `shared/`'s)
alongside `scripts/ksgen.c` (another standalone build tool) and
`cli/main.c`.

## Tests

`tests/findings/run_analyzer_tests.py` — the standing acceptance suite
(design.md §11.8), run against this binary as part of `make test-findings`
(`TEST_SECTIONS`, since [FINDINGS] B1). `tests/findings/
run_analyzer_pinned.py` is the golden-output regression check that
replaced `run_analyzer_agree.py`'s python-comparison role once the
prototype was deleted (its own header explains the succession). See
`tests/findings/CLAUDE.md`.
