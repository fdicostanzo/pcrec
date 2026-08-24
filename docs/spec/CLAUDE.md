# docs/spec/ — spec documents

Spec documents detail how the tool and its surfaces actually work and how to
use them. They are deliverables like code: actively maintained (not
append-only), carry no build history, and may reference docs/design/
documents for the reasoning behind a design without repeating it.

Build history is NOT part of the spec (Frank, 2026-08-14): how a surface
came to be — panel outcomes, refuted predictions, rulings, the design
process — stays in docs/design/ and docs/dev/. A spec may refer to design
documents but only INFORMATIONALLY: such references are background for the
curious reader, never normative. The spec alone states the contract; if a
spec and a design doc disagree, the spec is what the tool promises.

## Files

- `match_api.md` — **[M4.7f], 2026-08-18: the FIRST spec document.** The
  as-built match-API contract: the generated artifact's entry points
  (`<prefix>_search`/`_match`/`_match_caps`/`_info`), the six fixed-literal
  ABI types (`rx_ctx`, `rx_matchfn`, `rx_callout_ref`, `rx_group_entry`,
  `struct rx_info`, `rx_renderfn`), capture-slot semantics (the C1–C11
  requirements restated as contract prose, with the R22 cross-iteration-
  retention/empty-final-iteration-overwrite rules folded in as first-class
  text, not an addendum), the D49 give-up code space
  (`RX_ERR_STEPS`/`_FRAMES`/`_WORK`/`_RECURSE` since [DD-14] wave A, the
  `RX_ERR_FLOOR` partition), the
  `rx_info` reflection structure and its D46 compile-time observability
  macro mirror, the compile-entry NUL-termination contract (with an
  independently measured libpcre2 10.46 comparison — `PCRE2_ZERO_TERMINATED`
  truncates identically), and `pcrec_options`/`pcrec_error`. Every claim
  is verified against the shipped surface (`lib/pcrec.h`, artifacts
  actually emitted by `build/pcrec`, cited tests) rather than copied from
  `docs/design/match_api_m4.md`, which had drifted from what shipped in
  one place (§3.5: the give-up-code collapse `match_api_m4.md` still
  describes was superseded by D49 before this graduation and the shipped
  artifact already implements the superseding rule) and carries one
  as-built deviation of its own (§2: `rx_info` ships as a struct TAG, not
  the bare typedef the design sketch showed — forced by a name collision
  with the default-prefix `<prefix>_info` instance; **RULED D57,
  2026-08-18: the struct-tag spelling is blessed as the contract and the
  typedef form is dead**, so §2 states it as settled rather than open).
  References `docs/design/match_api_m4.md`/`engine_m4.md` informationally
  for the ruling history; this document alone states what pcrec promises.

  **[M6.2] waves D and E each added a sentence to §3.1, and wave E's is the
  larger one.** Wave D's says what `\G` means under the find-all loop
  ("contiguous with the previous match", PCRE2's global-iteration semantics,
  for free because the entry already takes the parameter PCRE2 threads). Wave
  E's says that **`caps[0][0]` is where REPORTING begins, which is not always
  where matching began** — `\K` moves it — with three consequences a caller
  can see: `caps[0][0]` can exceed the offset the match began at and is
  therefore not a bound on where the engine looked; `caps[0][0] ==
  caps[0][1]` no longer implies nothing was consumed (`ab\K` reports `[2,2)`
  after two bytes); and the anchored entries of §3.2/§3.3 return the CONSUMED
  length, which is what makes the §5 callout advance terminate. The find-all
  loop is unaffected because it advances off `caps[0][1]`, and that is
  MEASURED against libpcre2 driven through the same loop
  (`tests/assertions/run_kreset_diff.sh` §5) rather than argued.

  **[M4.7g], 2026-08-18 — the R29 fix pass** (`docs/dev/reviews/
  2026-08-18-r29-match-api-spec.md`) is the document's first revision,
  and its shape is worth knowing before editing this file again: the
  MATCHING SEMANTICS survived the panel untouched, and every landed fix
  was in the surrounding surface — the library calling sequence (§8 now
  carries one worked example that was compiled and run before it went in,
  plus §8.1's D56 guarantees), the find-all protocol (§3.1, verified
  against `re.finditer` and honest about where it is lossy against
  PCRE2's NOTEMPTY retry, which pcrec cannot express), the reflection
  surface's over-claims (§6.3's macro mirror is partial, and thinner
  still on DFA artifacts), and the two shipped doc-comments an embedder
  actually reads, which BOTH denied the give-up-code space §4 promises
  (fixed in `src/gen/emit_dfa.c` and `lib/pcrec.h` in the same pass).
  The document's header now carries a VERIFICATION LEDGER recording what
  each pass re-measured; keep it current, and keep §3.5's record of the
  two errors the panel found — an idealized quotation in a document whose
  authority is "checked against the shipped surface" is the failure mode
  the document exists to prevent, and old artifacts still carry the
  comment it describes.

  **[M5-SEAM], 2026-08-18 — the second revision** (D58, the encoding seam
  prelude). Smaller in shape than R29's and worth knowing for one reason:
  it is the first revision where a recorded CAVEAT was DISCHARGED rather
  than a claim corrected. §3.1's find-all loop advanced by a literal `+ 1`
  and carried a byte-vs-character caveat saying M5 would have to sharpen
  it; the loop now advances through `<prefix>_next_pos`, the first encoding
  residual, and the new §3.1.1 states that entry's contract. The caveat's
  own text is QUOTED in §3.1.1 rather than deleted, with what discharged it
  said next to it — the same discipline §3.5 follows for the two errors R29
  found. Also in this pass: §1 and §3 count five per-artifact entry points
  instead of four; §8.2 gains the per-compile-call encoding rule and
  records the `PCREC_ENC_ASCII` -> `PCREC_ENC_BYTE` rename as an announced
  pre-v1 boundary; §8.1's D56 quotation was re-measured (its wording had
  gone stale — it promised a milestone that had already shipped). The
  find-all measurement behind §3.1 is now a SUITE (`tests/encseam/`, in
  `make test`) rather than a transcript, which is the direction to keep
  taking this document's numbers.

  **[M6.3], 2026-08-18 — the third revision** (module `named-groups`).
  The second DISCHARGE this document has recorded (the [M5-SEAM] shape,
  not a correction): §6's own open question — the `groups` array's sort
  key — is fixed (`strcmp` on the name, matching libpcre2's own
  `PCRE2_INFO_NAMETABLE` order, measured; docs/dev/decisions.md D59
  carries the evidence and the reasoning) and §6's worked example is
  re-quoted verbatim from a fresh build carrying the module, in both the
  captures-default and `--no-captures` forms.

  **[ABI-NS], 2026-08-18 — the fourth revision** (D60 + addendum, the
  emitted universal-constant namespace unification). The give-up code
  space (§4), the caps-array unset sentinel (§5), and the nine D46 stamp
  bit constants (§6.3) move from per-`<PREFIX>` spellings to one
  canonical, unprefixed `PCREC_*` spelling in the shared `PCREC_RX_ABI_H`
  block (§2); the old `<PREFIX>_*` spellings are DELETED, no alias.
  `rx_info.engine`'s formerly number-only contract (§6 used to say "no
  such constant is #defined anywhere") gains names, `PCREC_ENGINE_DFA`/
  `PCREC_ENGINE_VM`, in the same block. §1, §2, §4, §5, §6 and §6.3 are
  re-quoted this pass, verbatim from fresh builds (both a `--no-captures`
  DFA artifact and a captures-default VM one). A THIRD-PARTY collision
  was found and fixed in the same lane, outside this document's own
  scope but load-bearing for it: `lib/pcrec.h` already declared
  `PCREC_ENGINE_DFA`/`PCREC_ENGINE_VM` as `enum` members for
  `pcrec_options.engine` (the compile-time engine REQUEST), and an
  artifact's own `#define` of the identical name, included before that
  header, rewrote the enum declaration into invalid syntax — fixed by
  converting `lib/pcrec.h`'s two members to plain `#define`s
  byte-identical to the artifact's emission (`lib/CLAUDE.md` carries the
  detail).

- `table_contract.md` — the ruled contract for every command that outputs
  a DATA TABLE (`--list-syntax`, `--list-verbs`, and any future table
  surface, which adopts it at birth): `#` comments, a header row naming
  all columns, append-only columns, consumers resolve by header NAME
  (never hardcoded count/position, trailing-safe, count only as
  header-equality). Chartered by Frank 2026-08-21 from the D65
  format-consumer breakage; [SR-11] tracks consumer conversion + the
  two checks. `--emit-ir`/`--trace` are explicitly out of scope.
Maintenance: update this file when files are added/removed or their roles
change.
