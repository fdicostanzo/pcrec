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
  (`RX_ERR_STEPS`/`_FRAMES`/`_WORK`, the `RX_ERR_FLOOR` partition), the
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

Maintenance: update this file when files are added/removed or their roles
change.
