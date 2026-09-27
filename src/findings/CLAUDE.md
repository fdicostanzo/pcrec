# src/findings — the shipped analyses ([FINDINGS])

The findings STORE: every analysis pcrec ships, as the same `.rxt` text a
user would write (`docs/spec/findings.md`, `docs/design/findings/design.md`
§8). Nothing here is compiled as library source by the `LIBSRCS` wildcard;
the Makefile compiles the store into `libpcrec` through two generated files
(both under `build/gen/`, never committed), which `src/core/findings.c`
includes.

## Files

- **default.rxt** — the one AUTHORED analysis (step B1): the built-in
  terminal of every chain (by identity, never by name). A `freq` block whose
  256 counts are exactly the static byte-frequency prior `src/opt/prefix_k.c`
  shipped before B1, so it normalizes to that table entry for entry (design
  §0.7), and whose one `serves byte-rate when byte via unigram` line is the
  `byte`-only restriction D123-4 required to be written into the data. Its
  header carries where the numbers come from (moved from `prefix_k.c`). An
  edit here moves the `<PREFIX>_FINDINGS` digest of every artifact that
  consumed it; `tests/findings/` pins it to `tests/findings/default_ppm.tsv`.
- **findgen.c** — the build-time PRE-PARSE (step B1, design §13 B1 (3)):
  `findgen OUT FILE...` runs the one `.rxt` reader over each bundle's text in
  its no-filesystem buffer mode and writes every data block (bundle, kind,
  line, `serves` lines, 256 counts) as a C table, `findings_table.inc`. It
  links a STAGE-0 `libpcrec` whose `findings.o` is built with
  `PCREC_FIND_STAGE0` (an empty table), because the real one includes this
  program's output. Each file must define exactly one bundle named for the
  file. `tests/findings/run_findings_tests.sh` §3 checks the table against a
  fresh parse of the embedded text.

The TEXT embed is `scripts/embed_text.sh` (`findings_store.inc`); shipped
data bundles derived from vendored corpora (`log`, `weblog`) arrive at B5,
each from a `third_party/<src>/generate.py`.

Maintenance: update this file when files are added/removed or change role.
