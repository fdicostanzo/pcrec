# src/gen/enc — the ENCODING BACKENDS

The DD-12 residual seam, built at [M5-SEAM] (D58, 2026-08-18) as a prelude
to M6 so M6's encoding-sensitive residue is born on the seam rather than
retrofitted onto it. Everything an artifact carries that depends on which
ENCODING it was compiled for lives in this directory, in exactly one file
per encoding.

## The rule this directory exists to make structural

DD-12 (7), ruled in as a requirement by Frank: **no encoding conditionals
anywhere** — not in the compiler, not in the emitter, not in the emitted
artifact. Encodings are SEALED BACKENDS, and the only "switch" is WHICH
backend's text an artifact embedded. So there is no `if (enc == UTF8)` in
this tree, and adding one is the design-stop signal, not a patch.

The complementary half is that the per-encoding header is the RIGHT seam
for the enumerable runtime-identity RESIDUE and the WRONG seam for the HOT
PATH (gcc cannot invert decode+compare back into a byte automaton;
malformed-input handling would degrade from automaton structure to runtime
branches). Enforced, not asserted: `tests/codegen/run_codegen_tests.sh`'s
`[M5-SEAM/DD-12(7)]` check reads every emitted engine body for a residual
reference, sabotage-validated by
`tests/mech/sabotages/S68_residual_in_hot_loop.sh`. That sabotage changes
no ANSWER — under the byte backend the residual is the identity — which is
exactly why a structural check is the only instrument that can see it.

## Files

- **enc.h** — the seam's whole interface: the `PcrecEnc` row (id, the ONE
  spelling of the encoding's name, and the two blocks of residual TEXT it
  contributes to every artifact compiled under it), the registry accessors,
  and `pcrec_enc_emit_text`. Read its header comment before adding a
  backend; it carries the third-encoding recipe and the reason a backend is
  TEXT rather than emitter code.
- **enc.c** — the registry TABLE (the encoding namespace's one definition),
  the by-id/by-name lookups, the rendered name menu for diagnostics, and the
  `$`-to-prefix substitution every backend's text goes through. The table
  carries a row for `utf8` with NO backend on purpose: a name pcrec knows
  but cannot compile must be refused BY ITS OWN NAME (`src/core/compile.c`
  reads the row's `name`), never fall out of a lookup as "unknown". That is
  [SR-10]'s single-namespace rule applied to the half this table owns — its
  motivating instance was compile.c's diagnostic and cli/main.c's name
  mapping drifting apart, and neither of those sites maps an encoding name
  of its own any more.
- **enc_byte.c** — the `PCREC_ENC_BYTE` backend, and the only one built.
  One byte is one character, so every residual entry is the identity shape.
  Today it contributes ONE entry, `<prefix>_next_pos` (the next character
  boundary strictly after `pos`, every position >= n counting as a
  boundary), whose contract comment is emitted into the artifact alongside
  the declaration — the contract lives with the backend so a future backend
  cannot land a residual declaration nobody wrote a contract for.

## Adding a backend (the DD-12 third-encoding recipe)

One new `enc_<name>.c` here, plus its `extern` in `enc.h` and its row in
`enc.c`'s table. Both of those are files in THIS directory; the Makefile
already globs `src/gen/enc/*.c`. **Nothing in `src/core`, `src/gen`, `cli/`
or `lib/` is touched.** If a backend ever requires touching a shared file
outside this directory, that is the derailment DD-12 names — stop and take
it to a design decision rather than patching the shared file.

Two constraints on the residual text itself:

- **`$` is the prefix placeholder and the only character substituted**, so
  residual text must contain no other `$`.
- **Emitted text is ASCII-only**, including inside comments — the artifact
  is source someone else's toolchain compiles (src/gen/CLAUDE.md's standing
  rule).

## Where the seam is consumed

`src/gen/emit_dfa.c`'s `emit_residual_decls`/`emit_residual_defs` (the
declarations ride `pcrec_emit_prologue`, so they land in the `.h` of a split
artifact and the `.c` of a self-contained one; the definitions ride the
exported `pcrec_emit_residual`, called by BOTH emitters). Those two
functions are the entire extent of the emitter's knowledge about encodings:
look up the backend, copy its text, substitute the prefix.

`src/core/compile.c` gates on the registry (a member with no backend is
refused, a non-member is refused with the rendered menu) and `cli/main.c`
resolves `-e NAME` / `--encoding=NAME` through `pcrec_enc_by_name`.

Maintenance: update this file when files are added/removed or their roles
change.
