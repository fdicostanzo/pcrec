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
  `RX_ERR_FLOOR` partition) and the below-the-floor `RX_ERR_INTERNAL`
  (NOT a give-up, [DD-14] wave A commit 2), the
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

  **[DD-14.FB], 2026-08-24 — the fifth revision, and the first that states
  a contract BEFORE it exists** (D71 item 2, the caller-provided frame
  buffer). Every earlier revision recorded what shipped; this one adds
  **§10, marked "SPECIFIED, NOT YET BUILT" in its own first line**, because
  D71 item 2 rules the buffer's shape "decided at docs/spec/match_api.md
  under D40" and the three existing entries' compatibility story is a fact
  about this document's contract. **The marking is the point, and an
  editor of this file must keep it**: this document's authority is that
  every claim was checked against the shipped surface, so a forward-looking
  section is only safe while it says loudly that it is one — §1-§9 are what
  pcrec promises today, §3/§4/§5.3/§6 carry one-line forward pointers that
  each name the pending status, and nothing in §1-§9 changed in substance.
  When the implementation lands, §10's status block comes off and its
  content merges into §3/§5/§6 where it belongs; that merge is the
  revision, not a re-write. Specified: three `_in` entries taking a
  per-artifact `<prefix>_buffers` descriptor (deliberately NOT one of §1's
  fixed-literal `rx_*` types — a frame's SIZE differs per artifact, so a
  literal spelling would advertise an interchangeability that does not
  exist), `buf == NULL` DEFINED as a call to the un-suffixed entry,
  `PCREC_ERR_FRAMES` unchanged and retry defined, a sizing surface with
  `abi` 2 → 3, and §5.3 extended by exactly one conjunct (own buffers per
  concurrent call). The design record — alternatives, costs, and the
  ASK — is `docs/design/frame_buffer_design.md`.
  **One shipped-behaviour note rides this revision and is NOT
  forward-looking**: §5.3 gains a MEASURED paragraph saying the concurrency
  promise is collectable only on a large-enough thread stack.
  `<prefix>_search`'s stack frame is 131,296 bytes on a call-bearing
  artifact whose frame requirement is not statically bounded, which does
  not fit a musl-default 128 KB thread and faults on a 2-byte subject. That
  is a live gap between §5.3's contract and the shipped artifact, filed as
  the design note's FINDING-1.

  **[SPEC-1.4], 2026-08-26 — the docs/spec/ consolidation pass's own patch
  set (D80), five small additions, no shipped behaviour changed.** §4 now
  points at `docs/spec/limits.md` for the give-up codes' numeric trigger
  defaults rather than leaving them unfound; §6.3's DFA-stamp-gap caveat
  (survey row C2) was re-verified against a fresh DFA/hybrid build and
  found already discharged by `[DD-13c]` — no wording changed there; §6
  gained a caller-facing `abi` paragraph stating D76's rule in contract
  terms (what a bump means, what stays fixed within one number, and that
  pre-v1 the bump IS the whole of the announcement, D40 regime 1); §8.2
  now leads with "`byte` is the only encoding implemented today" rather
  than requiring a reader to find it three paragraphs down; and a new §3.6
  states the `(?:P)\z` whole-subject/end-anchored idiom (survey row F9) —
  why `\z` and not `$` (verified live: `(?:foo)$` matches `"foo\n"`,
  `(?:foo)\z` does not), the `a|ab` counter-example showing a naive
  `length == n` test is insufficient (verified live: `a|ab` on `"ab"`
  reports `[0,1)`, `(?:a|ab)\z` on the same subject reports `[0,2)`), its
  ruled-permanent status (`docs/dev/decisions.md` D77, plan row `[OS-4]`),
  and the idiom's own DFA stamps (verified live: `RX_DFA_SCAN
  "unanchored"`, `RX_DFA_PREFILTER "byte-class-bounded"`/
  `"memchr-bounded"`).

- `table_contract.md` — the ruled contract for every command that outputs
  a DATA TABLE (`--list-syntax`, `--list-verbs`, and any future table
  surface, which adopts it at birth): `#` comments, a header row naming
  all columns, append-only columns, consumers resolve by header NAME
  (never hardcoded count/position, trailing-safe, count only as
  header-equality). Chartered by Frank 2026-08-21 from the D65
  format-consumer breakage; [SR-11] tracks consumer conversion + the
  two checks. `--emit-ir`/`--trace` are explicitly out of scope.

- `limits.md` — **[SPEC-1.1], 2026-08-25.** The resource-bound contract:
  the give-up code space (pointing at `match_api.md` §4 rather than
  restating it), the step/work/frame/trail budget numbers each cited to
  their compiled-in constant and CLI override, the compile-time
  state-count ceilings pcrec actually promises versus D45's
  test-harness compile timeout (which it does not), a re-measured worked
  example (`^(a(?1)?b)$` gives up at n = 343, an 686-byte subject,
  matching `match_api.md` §10.1 exactly at this commit), K33's stack
  frame re-measured via `make test-stackdepth` (131,216 B — flagging a
  stale 131,296 B figure still standing in `docs/dev/known_issues.md`'s
  and D73's own prose, not corrected by this pass), and K34/D74's
  documented-divergence framing at spec depth.

- `cli.md` — **[SPEC-1.2], 2026-08-25.** The full `pcrec` command-line
  reference: compiling a pattern (`-o`/`-o -`, `-p`'s C-identifier prefix
  grammar, `-e`/`--encoding` — byte-only today, `-i`, `--emit-main`,
  `--no-captures`, `--engine=`'s do-or-die refusal, the budget/frame flags
  pointing at `limits.md` for their numbers, `--features`' 17-module
  roster with each module's shipped status read live off `--list-syntax`'s
  `built` column, and the `-f`/`-fno-` tuning family pointing at
  `tuning.md`), the three listing surfaces (`--list-syntax`/
  `--list-verbs`/`--list-families`, pointing at `table_contract.md` for
  the column contract itself), diagnostics ([SPEC-1.7] folded in as its
  own section — the three exit codes verified live and DISTINGUISHED from
  an `--emit-main` binary's own unrelated 0/1/2/3, the D26 tiers restated
  caller-side, the offset-pinning convention from D26's tension addendum),
  and an honest "what the CLI does not do" section (no runtime, no
  multi-pattern units `[V-E]`, no `--lib` `[LIB]`, `--emit-ir` ships while
  `--emit-dot` does not — `[DD-8]` confirmed still STATE:not-started,
  which means `table_contract.md`'s own "TO BE CONSIDERED" note about
  `--emit-ir` is current, not stale). Every flag verified against
  `cli/main.c` AND a live `build/pcrec` run at this worktree's branch
  point (`0e2b23d`); where `--help`'s wording and the code agreed, cited
  directly rather than restated from memory.
- `tuning.md` — **[SPEC-1.3], 2026-08-25.** The `-f`/`-fno-` tuning-axis
  contract: what a tuning flag is (a generation-time choice, D18/D46/D47.3),
  one section per axis (every `-f`/`-fno-` flag, `--unroll=K`,
  `--engine=`'s tuning-adjacent role) stating what each denies/forces, its
  default, its emitted stamp (verified by an artifact diff), whether it is
  ANSWER-IDENTITY-preserving or ENGINE-SELECTING, and the differential that
  validates it with a measured population count. Also states the DFA side's
  own stamps (§3 — the `[DD-13]` gap this document once recorded was closed
  by `[DD-13]`/`[DD-13c]`, and `[OPT-3]` added `RX_DFA_TABLE` on 2026-08-26
  with its own axis at §2.13) and a
  `pcrec_options`-field-to-flag mirror table. Found and flagged one drift in
  the process: `lib/pcrec.h`'s own comment names the splice/linkage stamp
  `<PREFIX>_VM_CALLS`; the shipped emitter (`src/gen/emit_vm.c`) actually
  emits two macros, `RX_VM_CALL_SPLICED`/`RX_VM_CALL_LINKED` — this document
  states the as-built name; `lib/pcrec.h`'s comment was corrected at 40d9f79.

- `rxt_format.md` — **[SPEC-1.6], 2026-08-25.** The `.rxt` test-corpus
  format and the harness driver protocol, extracted from `docs/testing.md`
  (lines ~124-467 there): the full directive grammar (`pattern`/`flags`/
  `features`/`perr`/`m`/`n`/`ms`/`ns`/`g`/`gp`/`gu`/`engine`/`budget`/
  `frames-buffer=`), the subject escape table, the oracle-verification
  requirement (the default python-`re` oracle, the `# pcre2-only`
  exclusion convention, per-directory oracle overrides), how `run.sh`
  scores a block, `tests/harness/driver.c`'s CLI/exit-code contract
  (including the `_in`-entry anchored cross-check's exit `4`, previously
  undocumented in prose anywhere), the D45 budget policy stated as policy
  rather than measurement, and how to add a new component test directory.
  Every claim verified against `tests/harness/run.sh`/`driver.c` at this
  worktree's branch point (`d39ce94`); `docs/testing.md` keeps the process
  record (runtimes, battery composition, sanitizer/lint measurements,
  TT-* notes, the living oracle-exclusion catalog) and gained a header
  note plus a one-paragraph pointer where the moved sections stood.

- `registry.md` — **[SPEC-1.5], 2026-08-25.** The `--list-syntax`/
  `--list-verbs`/`--list-families` TSV COLUMN CONTRACT: every column
  by header name and its value set (which are a closed, stable
  vocabulary versus which are free text), read live off a fresh build.
  Distinct from `table_contract.md` (the generic wire format every
  table shares) and from `cli.md` §2 (what each surface answers, in
  prose) — this document is the data contract itself: 17 columns for
  `--list-syntax` (128 rows this pass), 6 for `--list-verbs` (50 rows),
  7 for `--list-families` (90 rows), the `built` (D65) vs.
  `status`/`roadmap` distinction stated at the detail cli.md's one
  sentence points past, and the `family` (D71 item 3) grouping rule
  (AND-over-members `built`, dispatch identity unchanged per row, R6).
  States what `tests/registry/`'s two batteries pin (self-consistency
  vs. the independent libpcre2 check, PC-3) and what neither guarantees.
  Flags one drift found in the process: `tests/registry/CLAUDE.md`'s
  own prose still cites the row count as "100 since Q2/SR-9"; the live
  count today is 128 (`registry_check.c`'s own exact-count assertion
  agrees) — not corrected in that file by this pass.
  **[DD-11.2], 2026-08-29**: `registry.md` gained §9, `--list-definitions`
  (D85, the FIFTH surface) — this bullet's own "`--list-syntax`/
  `--list-verbs`/`--list-families`" summary and its 128/90 row counts are
  now stale on TWO counts (this addition, and the pre-existing `--list-
  axes`/[CHK-2] omission this paragraph never picked up either); not
  rewritten wholesale in this pass — see `registry.md` itself for the
  live figures (§2's 138, §5's 100, §9's 50 and counting; §2's `kind`
  column also gained a sixth value, `bare`, at the manager's `RK_BARE`
  ruling, 2026-08-29).

**`docs/pcre2_compliance.md` is SPEC-TIER IN PLACE** ([SPEC-1.9], manager
ruling, 2026-08-25): it meets this tier's bar through its own
three-component annotated-derivation discipline (generated facts +
independent PCRE2-side survey + keyed hand-written annotations, held in
checked tension — `.claude/skills/compliance-refresh/SKILL.md`) rather
than by moving under `docs/spec/`; it stays at its current path because
its tooling (`tests/registry/compliance_section.py`, the annotation
store) is path-keyed.

Maintenance: update this file when files are added/removed or their roles
change.
