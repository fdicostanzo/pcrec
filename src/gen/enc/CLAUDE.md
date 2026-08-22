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
  spelling of the encoding's name, and a NULL-terminated table of
  `PcrecEncEntry` rows), the entry ids that are also the bits of a
  per-artifact MASK, the registry accessors, and `pcrec_enc_emit_text`. Read
  its header comment before adding a backend; it carries the third-encoding
  recipe and the reason a backend is TEXT rather than emitter code.

  **THE ENTRIES BECAME A TABLE AT [M6.5.2], and that is D58's own revisit
  clause being honoured** — *"the second consumer is the seam's validation
  event; ANY INTERFACE CHANGE IT FORCES GETS RECORDED AGAINST THIS ENTRY."*
  The second consumer arrived early (a caseless backreference compare) and it
  forced one: with three entries, two unconditional text blobs would put two
  exported functions of DEAD CODE into every artifact pcrec has ever emitted,
  including one with no backreference in it. They cannot be `static` (an
  unused `static` fails the harness's `-Werror` generated-code build, which is
  why `next_pos` is exported), so they would be LINKED dead weight. A
  per-entry mask keeps the cost where the construct is. The road not taken was
  two more string fields — simpler, and it does not generalise: lookbehind's
  back-step ([M6.6]) is the next residual entry D58 already names.

  `pcrec_enc_ready` moved with it (from `decls != NULL` to "has a non-empty
  entries array"), which R32 E11 found: the readiness predicate is a THIRD
  site the change touches, not the two emit functions alone, and the
  `-e utf8` refusal path reads it.

  **`engine_callable` is the other half**, and it is a fact about the ENTRY
  rather than about any artifact. `next_pos` carries `false`: unanchoredness
  is the automaton's own self-loop, so there is no external advance for an
  engine to route through, and an engine that DID route through it would match
  identically under this backend while changing the hot path's shape under any
  other. The two backreference entries carry `true`, because a backreference
  compare has NO automaton representation whatsoever — forbidding the call
  forbids the construct.
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
  One byte is one character, so every residual entry is the identity shape or
  close to it. THREE entries today, each with its contract comment emitted
  into the artifact alongside its declaration — the contract lives with the
  backend so a future backend cannot land a residual declaration nobody wrote
  a contract for:

  - `<prefix>_next_pos` — the next character boundary strictly after `pos`,
    every position >= n counting as a boundary.
  - `<prefix>_bref_match` / `<prefix>_bref_match_caseless` ([M6.5.2]) — the
    backreference compare, case-sensitive and case-folding. **TWO ENTRIES, NOT
    ONE WITH A FLAG**: D18/D23's rule is that an option compiles away, and D23
    MEASURED the alternative (a runtime fold indirection) costing 26% on a
    pattern containing no letters at all.

  **THE RETURN IS A LENGTH, AND THE SIGN CARRIES A SECOND FACT**, and both
  halves are designed for the backend that does not exist yet. Under this
  backend the compare cannot change length — but `(?i)^(ss)\1$` on "ss\xdf"
  is the cell a UTF-8 build has to answer differently, with one captured
  character folding to two and the consumed length no longer equalling the
  captured one. Returning a LENGTH is what lets that backend give a different
  answer WITHOUT THE SHARED EMITTER CHANGING A CHARACTER: it never computes a
  length, it only adds the one it is given. On failure the value is negative
  and `-(r) - 1` is the prefix that DID compare equal — the work a
  `(a*)\1`-shaped compare does before failing, which the fail label never sees
  and the work budget must therefore be told about. A bare `-1` sentinel could
  not carry it (R32 E4: the first design recommended charging that prefix and
  its own signature could not express it).

  **THE FOLD IS SPELLED ARITHMETICALLY AND IS TIED TO pcrec's OWN.** A
  `tolower()` here would be a DEFECT rather than a shortcut — it is
  locale-dependent at the CALLER's run time, in a locale pcrec does not
  control, and an artifact whose answers change with `setlocale` is not the
  self-contained matcher APPROACH promises. What keeps this spelling in step
  with `cls_casefold`'s is `tests/backrefs/fold_agreement_check.c`, which
  walks all 65,536 ordered byte pairs against `pcrec_ascii_fold`
  (src/core/fold.c) with the residual side read out of an artifact pcrec
  actually emitted.

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
look up the backend, copy the text of every entry the artifact's MASK names,
substitute the prefix.

**THE MASK IS DISCOVERED BY EMITTING, not predicted.** `Job.enc_mask` starts
at `PCREC_ENCE_NEXT_POS` (promised unconditionally by
docs/spec/match_api.md §3.1) and the VM emitter ORs in whichever compare
entries its `A_BREF` arm actually emits calls to — which is why the prologue
is written AFTER the program body, the same discipline the class pool and the
cursor local already follow. So "the artifact declares exactly the entries it
calls" is true by construction, and a backref-free artifact carries exactly
the residual text it always did.

`src/core/compile.c` gates on the registry (a member with no backend is
refused, a non-member is refused with the rendered menu) and `cli/main.c`
resolves `-e NAME` / `--encoding=NAME` through `pcrec_enc_by_name`.

Maintenance: update this file when files are added/removed or their roles
change.
