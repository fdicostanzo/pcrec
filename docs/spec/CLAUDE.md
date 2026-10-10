# docs/spec/ — spec documents

Spec documents detail how the tool and its surfaces actually work and how to
use them. They are deliverables like code: actively maintained (not
append-only), carry no build history, and may reference docs/design/
documents for the reasoning behind a design without repeating it.

Build history is NOT part of the spec (Frank, 2026-08-14), and
`make test-spec-history` (`tests/spec_history/`) flags it mechanically, with
the other docs' current history counted as known debt: how a surface
came to be — panel outcomes, refuted predictions, rulings, the design
process — stays in docs/design/ and docs/dev/. A spec may refer to design
documents but only INFORMATIONALLY: such references are background for the
curious reader, never normative. The spec alone states the contract; if a
spec and a design doc disagree, the spec is what the tool promises.

## Numbering and citation (Frank, 2026-10-09; lane specnum)

A spec is cited like a legal code: by NUMBER, which never changes. `match_api.md`
is the first document to carry it; every other spec adopts it when it is
rewritten facts-only (`tests/spec_history/cite_floors.tsv` has a row per
adopter, and the checks below run on any `docs/spec/*.md` that carries the
contents block).

- **Sections.** Every heading below the `# ` title begins with its dotted
  number (`## 3.`, `### 3.1`, `#### 3.1.3`; depth = heading level - 1) and is
  preceded by a line `<a id="s3-1-3"></a>` (`s` + the number, dots to dashes).
- **Paragraphs.** Every prose paragraph, list item and block quote begins
  `<a id="s3-1-3-p4"></a>[3.1.3¶4] ` -- the section's number, `¶`, the
  paragraph's number: 1, 2, 3 ... in document order within its innermost
  section (the preamble above the first heading is section `0`). A fenced
  code block or a table belongs to the paragraph it follows, or to its
  section when nothing precedes it. `¶`, not another dot, because a section
  can hold both subsections and paragraphs: `§3.1.1` is a subsection of
  §3.1, `§3.1¶1` a paragraph of it.
- **The citation form** is `match_api.md §3.1.3` or `match_api.md §3.1.3¶4`
  (a human may add the topic). Never a line number, never an anchor name. A
  shell or emitted string may use `S3.1`, the form the emitted
  `<prefix>_next_pos` comment already has.
- **Stability.** A number is never reused and never changes. An addition takes
  a letter after its predecessor: a section between §3.2 and §3.3 is `§3.2a`
  (its subsections `3.2a.1`, its paragraphs `§3.2a¶1`), a paragraph after ¶4
  is `¶4a`. A removal leaves a one-line stub under the same number -- the
  heading `### 3.2 — retired` or the paragraph `[3.2¶4] — retired.`, optionally
  naming where the text went (`— retired (moved to §7¶2)`). Moving text to
  another section is a removal plus an addition.
- **Contents.** A block between `<!-- spec-toc:begin -->` and
  `<!-- spec-toc:end -->` right under the title lists every numbered heading,
  number and link, and is GENERATED: `python3 scripts/spec_toc.py FILE` (add
  `--init` the first time) rewrites it; never edit between the markers.
- **Checks** (`make test-spec-history`, `tests/spec_history/spec_cites.py`):
  the numbering is well-formed (anchors, labels, order); the contents are
  current; every `<doc>.md §N` / `§N¶K` / `SN` cited anywhere in the tree
  names a number that exists (a retired stub exists); no `<doc>.md:<line>`
  citation remains. What no check can see is a RENUMBERING that leaves every
  cited number resolvable (a paragraph deleted and its successors shifted
  up): review the diff of a spec edit for a changed label.
- **Adopting it in another spec**: number the headings, give each its anchor
  line, label the paragraphs (`studies/specnum/number.py` is the one-time pass
  that labelled `match_api.md`; adapt it, it refuses a numbered file), run
  `scripts/spec_toc.py --init`, add the doc's row to `cite_floors.tsv`,
  and re-point the tree's citations of it (`studies/specnum/repoint.py` did
  that for the anchor form).

## Files

- `match_api.md` — the match-API contract, FACTS ONLY (rewritten by lane
  specclean, 2026-10-09): §1 symbols and namespaces (the shared ABI block and
  its `abi`-valued guard), §2 the fixed ABI types verbatim, §3 the entry points
  (`<prefix>_search` with the find-all loop at §3.1 — the emitted
  `<prefix>_next_pos` comment cites "match_api.md S3.1", so the loop stays
  there — `_next_pos`, `_valid_upto`, `_match`, `_match_caps`, `_info`,
  give-ups across entries, the `(?:P)\z` idiom), §4 the give-up and refusal
  codes, §5 captures and groups (slot rules, concurrency at §5.3, named groups,
  composition), §6 `rx_info` field by field and the `abi` rule, §6.3 every
  stamp macro (an inventory table, then one anchored entry per stamp), §7 the
  NUL-terminated compile entry, §8 the library structures, §9 encodings and
  character positions, §10 the `_in` entries and the tiered default. **Cite it
  by number** (`match_api.md §3.1.3`, or one paragraph, `§3.1.3¶4`), never
  by line or anchor name; the numbering rule above applies, its contents
  block is generated by `scripts/spec_toc.py`, and a §6.3 stamp is a numbered
  paragraph of §6.3.x (the inventory table at §6.3.2¶1 gives each one). Every §6.3 value set is a table directly under a
  `<!-- value-set: RX_NAME -->` marker, which `tests/registry/
  axes_registry_check.sh` and `tests/codegen/run_fallback_table.sh` anchor on:
  keep the marker with its table. Its history (revision notes, rulings,
  walkbacks) is `docs/dev/history/match_api_record.md`, its `abi` change log
  `docs/dev/history/abi_changelog.md`; `make test-spec-history`
  (`tests/spec_history/`) keeps history out. `studies/specclean/claims.tsv`
  maps every claim of the pre-rewrite text to its new home.

- `table_contract.md` — the ruled contract for every command that outputs
  a DATA TABLE (`--list-syntax`, `--list-verbs`, and any future table
  surface, which adopts it at birth): `#` comments, a header row naming
  all columns, append-only columns, consumers resolve by header NAME
  (never hardcoded count/position, trailing-safe, count only as
  header-equality). Chartered by Frank 2026-08-21 from the D65
  format-consumer breakage; [SR-11] tracks consumer conversion + the
  two checks. **[DD-8], 2026-09-19: `--emit-ir` ADOPTED IT** and is the
  Sections mechanism's third producer, the first with no anonymous table
  and the first whose sections carry different column counts; `--trace`
  remains out of scope.

- `facts_listing.md` — **[PATFACTS] step 3.0, 2026-09-26 (D126, ruled Q8).**
  `--emit-facts`' output format: its two `#section` blocks (`facts`,
  `decisions`) and their columns, the CLOSED `status` (`derived`/`denied`/
  `declined`/`absent`) and `used` vocabularies, the `why` token grammar
  (`deny:<flag>`/`decline:<reason>`/`rate:<source>`), the three guarantees
  (never refuses a compile that succeeded; never changes the compile; one
  spelling per value, shared with the fact-valued stamps), and what is NOT
  promised (fact names, reason names, prose). A DEBUG listing with
  `ir_listing.md`'s status — no `abi` number. The per-flag "Facts emptied"
  lines it points at live in `tuning.md` §2.25-§2.28 and are what
  `tests/codegen/run_facts_checks.sh` checks the listing against.

- `ir_listing.md` — **[DD-8], 2026-09-19.** `--emit-ir`'s output format:
  its nine `#section` blocks (`summary`, `slots`, `rungs`, `strategies`,
  `pruning`, `program`, `choicepoints`, `islands`, `callouts`) and their
  columns, the `prefilter` value vocabulary and the `program` `op`
  vocabulary, the multi-valued-cell and escaping rules, and the three
  things the listing is NOT — not an IR anything consumes, not lossless
  (lossy on operands, by ruling), not a DFA listing. Sits UNDER
  `table_contract.md` (it conforms to it and adds only what is specific
  to this listing) and beside `cli.md` §2 (the flag's reference entry).
  The producer-side rule that an empty population is a ROW rather than a
  comment lives here, because it follows from the table contract's own
  header rule rather than from taste. Read it before changing anything
  `vm_render_listing` prints.

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

  **2026-09-10 (Frank's ruling, lane rpkg, wording only, no behaviour
  changed):** §5's K33 fit criterion is restated as free STACK HEADROOM AT
  THE CALL SITE (entry + deep >= 134,400 B for the witness artifact class)
  rather than "against a musl-default 128 KB thread stack" — the earlier
  wording named a thread's total SIZE where what actually decides fit is
  headroom REMAINING at the point the call happens, and the two coincide
  only at call depth ~0. The musl-128KB and glibc-8MB numbers stay as
  worked EXAMPLES of headroom at depth ~0; `docs/dev/known_issues.md`'s new
  K33 DARWIN ADDENDUM is the measured case where the two diverge (macOS
  grants MORE than a requested size, so a nominal 131,072 B thread's actual
  headroom exceeds its own stated size).

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
  `--emit-dot` does not). Every flag verified against
  `cli/main.c` AND a live `build/pcrec` run at this worktree's branch
  point (`0e2b23d`); where `--help`'s wording and the code agreed, cited
  directly rather than restated from memory.

  **[DD-13b.W1.2], 2026-08-31**: §1 gains `--source` / `--target` /
  `--lib-path` and the `-o` output-naming rule (a FILE for one target, an
  existing DIRECTORY for several, `-` for one on stdout); §4's
  "no multi-pattern compilation units" and "no `--lib FILE`" bullets are
  NARROWED to what is now true rather than deleted — several patterns per
  invocation, still one artifact per translation unit (D88), and
  `--lib-path` resolves a `lib` reference's EXISTENCE without reading a
  library's contents. Nothing in the single-pattern surface changed.

  **[REL-1.4], 2026-09-21 (D115)**: §1 gains a `--version` entry — prints
  `pcrec 0.1.0-beta` (`PCREC_VERSION`, `lib/pcrec.h`) and exits 0, parsed
  identically to `-h`/`--help`. No existing flag's shape changed.

  **[REL-1.10], 2026-09-21 (D118) — THE gcc SHAPE.** §1's usage line and
  operand rule are rewritten: a positional operand is an INPUT FILE now
  (new §1.1, several may be given, pooled into one `-o` decision), never a
  pattern; `--pattern 'X'` is the one way to give a literal pattern;
  `--source FILE` is RETIRED (an unknown option, no alias); `-I DIR` joins
  `--lib-path DIR` as its short spelling; `--probe-ask WANT CONSTRUCT`
  takes CONSTRUCT as its own second argument rather than through the (now
  file-only) operand slot; a positional operand in any query mode is
  refused. §4's multi-pattern bullet is reworded for several FILES rather
  than one `--source`. No compile FLAG's own semantics changed.

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

  **2026-09-29 (D131 item 1, lane adm131 applying clsfit's verbatim diff):**
  §2's λ (class-matcher kit) row moves off `reservation` for the first
  time — it states the RULED policy (one kit constant λ=4 plus a
  first-match rule over the whole-set tables, `docs/design/
  opt_dial_design.md` §4) — but is still a design-stage entry: `[CLS-TREE]`
  is unbuilt, so the row documents what the mechanism will read the day it
  lands, not a shipped behaviour.

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


  **[DD-13b.W1.2], 2026-08-31**: the head table's `target` row stops
  reading "Parsed, not yet built" and its `lib` row stops reading
  "Recorded, not yet resolved"; a new "Building from a source file"
  section states what belongs to the FORMAT rather than to the CLI — a
  definition is a block's `name` in the FILE namespace, the
  no-target-plus-one-unnamed-block compatibility default, the
  library-builds-nothing outcome, the `features` UNION and the
  more-specific-wins table, and the harness's per-target agreement control.

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

- `findings.md` — **[FINDINGS] B1, 2026-09-27 (D122/D123/D126).** The
  findings contract: the terms, the `freq` kind and its row grammar, the
  closed query/derivation vocabularies, the `unigram` normalization with its
  test vectors, the per-question-KIND NONE answers and each reader's kind and
  guarantee, the `<PREFIX>_FINDINGS` stamp grammar with the digest's byte
  layout and the name-disclosure statement, and the shipped default and store.
  It grows by step (resolution and the CLI at B2, the analyzer at B3/B6,
  `run-rarity` at B4, `cpfreq` at B5), and says at each section what is not
  built yet.
- `vars.md` — **module `vars`' caller-observable contract** ([VAR], 2026-09-23):
  `${name}` in a pattern, whose bytes the caller supplies per call. The
  spelling and its five bash-shaped operators, the `rx_var` type and the
  BY-NAME rule (an index is meaningless across separately compiled
  artifacts), where the array is passed (`rx_ctx` for the `rx_matchfn`-shaped
  entries, a trailing pair for `<prefix>_search` and its `_in` siblings),
  `PCREC_ERR_UNSET_VAR`'s below-the-floor refusal class and why an unset
  variable is loud rather than empty, every refusal the module can raise, and
  the engine/caseless facts. The ABI surface itself is `match_api.md` §2 and
  §6's `abi` 32 entry; the numbers are `limits.md` §3.6. Design:
  `docs/design/variables_common.md` / `variables_pattern.md`.

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
