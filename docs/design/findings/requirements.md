# `[FINDINGS]` — requirements and questions (step 1 of 3: think → design → critique)

**Lane `findthink`, opus, 2026-09-25. A THINKING deliverable, not a design.**
Nothing under `src/`, `cli/`, `lib/`, `tests/` changed. It lists who reads a
findings value, what the mechanism must satisfy (numbered, testable, sourced),
and the questions Frank's answers must settle before the design note
(step 2) is written. Where two shapes are live, both are stated and none is
picked unless the brief allowed a recommendation.

Sources, with short names used below: **D83** and its **A1-A4** (the
2026-09-22 addendum's items (1)-(4)); **D122**, **D122-2** (addendum 2),
**D122-3**; **RFP** = `docs/design/reqbyte_freq_pick.md` (every §10 question
RULED as recommended, 2026-09-22); **WAF** = `docs/dev/optloop/waf_attribution.md`;
**B2R** = `docs/dev/optloop/cycle2_batch2_reading.md`; **FSD** =
`docs/dev/optloop/firstset_design.md`; **OKS** = `docs/design/offset_k_skip.md`;
**CS** = `docs/design/compare_stack.md`; **FD** =
`docs/design/dd13_format/format_design.md`; **FI** = `.../frank_inputs.md`.

---

## 0. Findings first

1. **The motivating witness for D83's addendum did not reproduce.**
   D83-A was ruled on json-constant's twin running ×1.10 SLOWER ([OPT-FIRSTSET]).
   O-46 F1 (plan row [OPT-FIRSTSET]) re-ran it: twin 1.52-1.66 ns/B against
   base 3.09. So the cost model holds and **the decline rule is RETIRED**.
   [OPT-FIRSTSET] no longer needs a findings value. The addendum still binds
   as a ruling, but its customers are now the ones in §1, and none of them is
   the one that started it. The design should cite §1's customers, not
   json-constant.
2. **The measured need that remains is RUN-level, not byte-level.** Byte-level
   picks already pay using the shipped prior alone (RFP §0 finding 2: all
   three whole-call wins, and 12 of 12 movers agree out of sample). The
   misses that are still open are about how common a run or string is:
   - S4(a) picks `from` on the bench, but real traffic wants `union` (WAF §3.2).
   - The independence product (multiplying single-byte frequencies)
     mis-predicts run density by 5× to 3,257× (`reqpos_2b.md`, cited at WAF §3.2).
   - Widening G1 needs the run's rate compared with the prefilter byte's
     rate (B2R §6).
   **No value kind that answers these exists in the format, in D83, or in
   any design note.** That makes it the first thing to decide on the content
   side (§3 Q5).
3. **An exemplar's byte histogram does not have the encoding problem that
   RFP §3 describes. The shipped hand table does.** A matcher compiled with
   `-e byte` and run on UTF-8 text scans exactly the bytes that the
   exemplar's histogram counted. The inversion in RFP §3.2 is a property of a
   PRIOR that assumes some corpus. It is not a property of a MEASURED
   histogram. So RFP §3.3 clause 1 ("key must equal the compile's `-e`")
   would wrongly refuse a UTF-8 exemplar histogram for a `-e byte` compile,
   which is a common and legitimate pairing. The design needs to say what the
   key means (§3 Q6).
4. **The unit that `analysis <name>` selects is ambiguous today, and the
   documents disagree on how it is spelled.**
   - FD §4.3 and its D-e row spell the selector `analysis freq <ident>`: the
     kind, then the name, selecting one block.
   - The shipped schema has `config analysis LIST` (`rxt_schema.def:172`),
     and `rxt_format.md` says "`analysis <list>` names data blocks".
   - D83-A1 says a findings file is a SET of named values. That means a
     named analysis such as `json` is a bundle, possibly one block per kind.
   Whether `analysis json` pulls every block named `json` across all kinds,
   or has to name each kind, is the first structural question (§3 Q1).
5. **None of the three resolution routes works end to end today.**
   - `include "path"` resolves relative to the file only and refuses `<store>`.
   - `lib <store-name>` is RESERVED and refused as NOT IN THIS BUILD
     (`rxt_format.md` head table). It is the spelling FD/usecases §6.1 gave
     to "pcrec's shipped store plus `-I`".
   - pcrec has no install target, no data directory and no environment-variable
     lookup (grep: none in `src/`, `cli/`, `Makefile`).
   So "resolve `json` via `-I` like any library" has no directory to find the
   SHIPPED `json` in, unless the design adds one or builds the analyses into
   `libpcrec.a`. §2.3 sets out both options.
6. **The shipped prior has five readers, and one of them is ungated.**
   - Four read `pcrec_byte_freq_ppm` and gate on encoding: `reqbyte.c`'s
     three (`rb_pick`, `rn_scan_index`, `rn_window_start`, keyed on
     `bytekey`) and `emit_dfa.c:5499` `req_byte_dominated_by` (byte only).
   - `prefix_k.c`'s `set_ppm` reads the table directly and has NO gate
     (CS D7).
   - D122-2 (3) rules that the gate moves into the accessor. So the accessor
     change and the findings plumbing are one edit site. RFP §2.3 already
     argued this: "the change is `pcrec_byte_freq_ppm`'s body plus a `Ctx`
     parameter".
7. **The `freq` block's `reader` line is one prose line, but the value
   already has several readers.** Its purpose was "a block nobody reads is
   not emitted" (FD §2.10). That still holds, but a single-reader field
   under-describes a value that four selection points consume. It is minor,
   and it belongs to [DD-13b].

---

## 1. The customers

Every current and near-term compile decision that reads, or would read, a
findings value. "Sens." means how far the choice moves when the value moves,
with measured cases cited. The **No findings** column says what the decision
does with the shipped default only.

| # | customer (row / site) | value it needs | sens. (measured) | with no findings |
|---|---|---|---|---|
| C1 | **[OPT-FREQPICK]** `rb_pick` (`reqbyte.c`) — which member of the necessary SET the pre-check memchrs | per-byte frequency (unigram); case pairs not needed (exact members only) | **HIGH, bimodal.** Whole-call wins when the pick moves to an absent byte: nested-comment-rec 9.3 ms → 23.1 µs. The one severe hazard (email-owasp, 500× floor jump) was a pick moving to an absent byte on a one-attempt artifact; [OPT-PRECHECK-ADMIT] removed it, not the prior (B2R §4.2) | shipped prior under `byte`; rightmost rule under every other `-e` (RFP §3.3) |
| C2 | **[OPT-REQPOS] 2b** `rn_scan_index` + `rn_window_start` — which run byte to memchr, and which 8-byte window to keep | per-byte frequency; the window sum is an **independence estimate of RUN rarity** | **MED.** router-prefix-order's +80.8% came from the run FORM, not the pick (B2R §4.1: 39,098 memchr calls vs 315). The pick alone was strictly cheaper | leftmost / leftmost window outside `byte` |
| C3 | **[OPT-PRECHECK-ADMIT] G1** `req_byte_dominated_by` (`emit_dfa.c`) — is the pre-check dominated by the prefilter's scan | today a unigram compare. The **widening** B2R §6 names needs the scan byte's occurrence rate against the prefilter byte's | **HIGH on 2 cells.** router 315 vs 39,098 calls, keyword 9,470 vs 44,135 (B2R §6). The candidate rule is NOT built (D77, I-103) | identity only outside `byte` |
| C4 | **[OPT-K]/[OPT-OFSK]** offset-k selection, `set_ppm` (`prefix_k.c`) — which offsets to scan and verify | per-byte frequency summed over a set (set mass) | **LOW-MED.** Under log-measured frequencies only iso-ts moves, gaining `-`@7 because `-` is 3.6× commoner than the table says. "Not delicately balanced" (OKS C2). The 2× materiality bar absorbs noise (OKS §4.5) | shipped prior **ungated under utf8**. D122-2 (3) moves that gate, so offset-k selections move under utf8 (abi bump accepted) |
| C5 | **[OPT-LITSCAN]** the kit's FORM rows (D122 (1), D122-2 (4)): rare → memchr+verify, moderate → run check, common → inline/skip | scan-byte hit rate (unigram). Run rate for the "restarts pay" arm | **UNCALIBRATED.** memchr beat inline at 2.8% and 3.2% hit rates on every config. The crossover constant does not condition: it needs a pattern pair with well-separated frequencies, <0.5% vs >6% (bench O-51 (3)-(4)) | the prior, gated |
| C6 | **S4(a)** caseless run choice (`union-select`, WAF §3.2) — which of `union`/`select`/`from` to search | **RUN-level (joint) frequency** plus case-pair mass. A letter argmin is the wrong kind | **HIGH, and the sign flips by corpus.** Letter argmin picks `from` (predicted 0.171 ns/B on the bench). Deployment wants `union`, since prose says "from" constantly. "A design that inherits the letter argmin will look excellent on this cell and be poor in deployment" (WAF §3.2, §5 Q2, **unruled**) | letter argmin, known wrong in deployment |
| C7 | **`dfa_scans[]` stay/skip row**, conditional (WAF §3.4 plainloop twin) | set density, **plus how long membership runs last** ("a word every ~5.7 bytes") | **UNKNOWN.** Exists only if the plainloop twin lands near re2 (≤~1.8 ns/B) | today's dispatch |
| C8 | **[OPT-A]** rarest-byte selection for the DFA candidate-start scan / pair scan | per-byte frequency. The pair scan itself needs none (FSD §5.4) | not measured. stack-frame's gap is SIMD pair-scan (O-8) | `cand_from_escapes`, no prior |
| C9 | **[OPT-FIRSTSET]** set density for the skip-loop cost model | set mass | **NONE NOW.** The decline rule was retired (§0 finding 1) | model with no decline arm |
| C10 | **[OPT-4]** exact vs collapsed prefilter | per-pattern run lengths / candidate density | **RETIRED.** Ruling B deleted the knee, so collapse is fallback-only (`plan_completed.md` [OPT-4]). The question was pattern-SPECIFIC anyway ([ENG-PGO], D83 (2)) | ladder fallback |
| C11 | **[ENG-PGO]** tier-escalation rates, fast-tier hit share | pattern-specific statistics | **Out of scope:** D83 (2), a separate shape and a separate build (§4) | — |

**What the census says about VALUE KINDS:**

| kind | readers | status |
|---|---|---|
| per-byte unigram (`freq`) | C1-C5, C8 (C9) | format ships (`rxt_schema.def:146`). No reader of `row`. No encoding row |
| per-byte, per-encoding, derived from code points (`cpfreq`) | same, via derivation | **RULED as the shape of SHIPPED analyses** (RFP §3.5, §10 Q7). Not in the format |
| run-level / joint (bigram? top-K n-gram list? word list?) | C2 (window), C3 (widening), C6 | **no kind, no format, no measurement** (§0 finding 2) |
| inter-occurrence gap / burstiness (`gap`) | C5 (restart cost), C7 | Frank's illustration (FI 2026-08-29). FD §2.10: "not specified", D77 |
| set-membership run length | C7 | no kind. Conditional customer |
| line length / chunk stats (D83 (1)) | none | no customer. D77 |

---

## 2. Requirements

Each requirement is **R-n**, testable, with its source in brackets. MUST is
binding. SHOULD is the recommendation where a ruling is still owed.

### 2.1 Value kinds and shapes

- **R1 (open set).** The findings mechanism MUST carry NAMED VALUES of
  DIFFERENT KINDS. Adding a new kind adds one data-kind production and one
  accessor. It never adds a second resolution, merge or stamp mechanism.
  **Test:** adding a toy kind in a sabotage/fixture touches no resolution
  code. [D83-A1; FD §2.10]
- **R2 (membership rule).** A kind is admitted only with (a) a named reader
  (a selection point that exists, or one in the same change) and (b) its
  value MEASURED first. **Test:** every kind in the schema has a reader
  grep-able in `src/`. The `question`/`reader` lines stay required.
  [FI 2026-08-29; D77; FD §2.10]
- **R3 (integer, reproducible).** Every value the compiler reads MUST be an
  integer: ppm for distributions, counts elsewhere. No float anywhere on the
  path. One normalisation from counts to ppm is DEFINED, including the
  rounding-residue rule and the zero-count FLOOR. The floor mirrors today's
  2 ppm and is never zero, because "a zero would let the model believe a
  byte is IMPOSSIBLE". **Test:** a normalised table sums to exactly
  1,000,000 (the `run_offset_skip.sh` §1 shape, generalised). No byte is
  below the floor. The same counts give bit-identical ppm on darwin and
  Linux. [`prefix_k.c` header; RFP §2.3]
- **R4 (byte `freq` shape).** The `row` encoding of a 256-entry table is
  decided ONCE. Candidates: FD §2.10's 16×16 offset-labelled rows, or FSD
  §5.1's `byte count` rows read by declared columns (`table_contract.md`).
  It is read by ONE reader. [RFP §2.2 item 2]
- **R5 (`cpfreq`).** Shipped analyses carry code-point frequencies. The byte
  table for an encoding is DERIVED by one function that reuses
  `pcrec_lower_enc`'s encoder: `count(b) = Σ count(cp) × occurrences of b in
  encode(cp)`. **Test:** deriving `cpfreq` over ASCII-only code points gives
  the same bytes as `freq` over the same corpus. A known Latin-1 sample
  derives `0xC3`-heavy under utf8. [RFP §3.5, RULED §10 Q7]
- **R6 (run-level kind is chosen by measurement).** Before any run-level kind
  enters the format, a D77 measurement compares candidate estimators against
  TRUE run counts on at least two corpora that differ in kind. The candidate
  estimators are:
  - (a) the unigram independence product (today's);
  - (b) a bigram/Markov chain estimate;
  - (c) a top-K n-gram list, where absence implies an upper bound;
  - (d) a word/token frequency list.
  The runs tested are the necessary runs of the corpus, the bench and the WAF
  set. The winning kind has to fix the C6 sign (`union` ≺ `from` on web
  traffic, the reverse on prose), not merely lower the average error.
  [§0 finding 2; WAF §3.2, §5 Q2]

### 2.2 Sources, precedence, merge

- **R7 (four sources, one shape).** These four are all the SAME format, and
  one reader consumes them:
  - (a) the shipped DEFAULT;
  - (b) shipped NAMED analyses;
  - (c) user-supplied values (CLI or `.rxt`);
  - (d) the analyzer's output from an exemplar.
  A user's file differs from a shipped one only in where it is resolved from.
  **Test:** copying a shipped analysis into a user directory and naming it
  from there produces a byte-identical artifact apart from the stamp (and
  identical if the stamp names the analysis by content). [D83-A3; plan row]
- **R8 (resolution unit = (name, kind)).** Resolution MUST answer, for each
  KIND a reader asks for, which source supplies it. A source that lacks a
  kind FALLS THROUGH, for that kind, to the next source, and finally to the
  shipped default. This is D83-A3's "overrides OR extends" made precise.
  **Test:** a user file carrying only a run-level value plus `analysis json`
  gives json's `freq` and the user's run value. [D83-A3]
- **R9 (no blending inside a value).** A value comes whole from exactly one
  source. There is no per-byte override and no weighted mixing of two
  distributions, because a normalised table cannot have one entry replaced
  without renormalising. **Test:** the stamp names exactly one source per
  consumed kind. [R3; derived]
- **R10 (precedence order is total and stated).** Suggested order:
  1. CLI;
  2. the target's config (`analysis` list, in list order);
  3. inherited configs (`from`, per the existing `cfg_merge` join rule);
  4. the shipped default.
  When the CLI overrides a target's config there MUST be a non-fatal stderr
  diagnostic naming both. **Test:** a fixture with both prints the
  diagnostic, and the stamp shows the CLI's. [lane `rulefix` ruling-1
  precedent, RFP §3.3; `rxt_format.md` config join]
- **R11 (per-target).** Findings bind per TARGET, so one pattern can be built
  against two exemplars as two `target` lines. **Test:** a fixture with two
  targets and two analyses gives two different stamps. [FD §4.3; FI §6.4]

### 2.3 Resolution — both routes, not picked (D83-A4)

The design note owes the weighing. These are the facts it must answer to:

| | **Route I: through `-I`/`<store>`** (D83-A4's consideration) | **Route D: a dedicated lookup** |
|---|---|---|
| spelling | `lib <json>` / `include <json>` in `.rxt`. `-I DIR` extends it. `.rxt` implied (usecases §6.1) | `analysis json` resolves a name directly; a user file is `--findings FILE` / `include "f.rxt"` |
| shipped store location | **none exists** (§0 finding 5). Needs a data directory (install/relocation, a new build fact) OR a built-in store compiled into `libpcrec.a` that `<name>` falls back to after `-I` | built into `libpcrec.a` (generated `.inc`, the `uprops` shape) |
| what must change in the format | un-reserve `lib <store>`. `include <store>` is refused by value shape today and would need admitting | none beyond `analysis` resolution |
| namespace | shared with [LIB]'s future subpattern store: can `<json>` be both a subpattern library and an analysis? | its own namespace (FD §2.10 already gives data blocks their own) |
| gains | one resolution mechanism for patterns and data (the general-mechanism memory). A user's findings file is "just another include" | no filesystem dependency for shipped names. `--pattern` compiles resolve names without a `.rxt` |

- **R12.** Whichever route is chosen, `--pattern` compiles (no `.rxt`) MUST
  be able to name a shipped analysis and a user file. [RFP §2.2 item 3]
- **R13 (no ambient state).** Resolution MUST NOT read environment
  variables, the current directory (other than paths given explicitly) or a
  user home. The inputs to an artifact are the command line and the files
  it names, and nothing else. **Test:** the same invocation from two cwds
  with the same explicit paths gives identical bytes. [D76 byte-exactness;
  D118's gcc shape, where search dirs come from `-I` only]
- **R14 (hybrid is allowed).** If Route I is chosen, the SOURCE OF TRUTH for a
  shipped analysis SHOULD still be an in-tree generated `.rxt`, so that it
  can be read, diffed and re-derived. Embedding it into `libpcrec.a` is then
  a build step (a derived artifact, D85/[DD-11]), not a second copy.
  [third_party rule "a data source compiles to generated tables"]

### 2.4 CLI, `.rxt` and library surfaces

- **R15 (CLI).** There MUST be one flag that names analyses (list, in order)
  and one that takes a findings FILE. Neither takes raw exemplar text: pcrec
  never reads an exemplar (D83 "`--exemplar FILE` takes the FINDINGS file,
  never the raw text"). Both are repeatable in the `-I` sense only if R10's
  order can be stated for them. [D83 Consequences; RFP §2.2]
- **R16 (`.rxt`).** `config … analysis <list>` resolves. Its names are
  refused by name when unknown (R27). Whether pattern-block scope also takes
  `analysis` is a design decision, recorded either way. [`rxt_source.c:2756`'s
  `continue`; `rxt_format.md`]
- **R17 (library).** `pcrec_options` MUST be able to express the same inputs
  as the CLI, following the `features` string precedent ([REL-1.11]). At
  minimum it takes a name list. A file is either parsed by the library or
  handed in as parsed values; the design picks and states why. A library
  caller without a filesystem must still get the shipped default and shipped
  names. [D80; `lib/pcrec.h` `pcrec_options.features`]
- **R18 (introspection).** A query surface (`--list-source` row/column, or
  `--explain`-shaped) MUST show, per target, which source each consumed kind
  resolved to, before anything is compiled. **Test:** a fixture's resolution
  row matches the artifact's stamp. [plan row: "inputs must be visible"]

### 2.5 Byte-exactness and the stamp (D76/D94)

- **R19 (deterministic).** Same pattern, options and findings inputs give a
  byte-identical artifact within one abi. Findings inputs that differ but
  have EQUAL consumed values give an identical program region.
  **Test:** codegen identity over repeated compiles, and a whole-file
  compare. [D76]
- **R20 (stamp).** The artifact MUST stamp what findings it was built
  against, for every kind a reader consumed. SHOULD: a digest over the
  consumed VALUES only (kind + encoding key + rows), NOT over provenance.
  Otherwise re-running the analyzer on the same exemplar (a new `retrieved`
  date) would move artifacts. **Test:** editing a provenance field moves
  nothing, and editing one row moves the stamp. [D76; D83 "delivered as a
  file"; R13]
- **R21 (abi).** Adding the stamp line is a scaffolding change, and so an
  abi bump with the D94 ritual, readers found by grep. The accessor gate
  move (D122-2 (3)) SHOULD ride the SAME bump, since both touch the same
  site and the same population. [D76/D94; D122-2 (3); memory
  `pcrec-abi-changes-pre-release`]
- **R22 (shipped-data change = visible event).** Regenerating a shipped
  analysis, the default included, moves users' artifacts with no change to
  their inputs. That MUST be either an abi bump or a change in the stamped
  analysis identity (digest/version). It is never silent. **Test:** a
  pinned artifact built with `json` fails the identity gate after `json` is
  regenerated, and the failure names the analysis. [D76; D26 "a version bump
  is a re-measurement event"]

### 2.6 Encodings

- **R23 (the gate lives in the accessor).** No reader tests `-e` itself.
  The accessor answers "the byte distribution valid for THIS compile" or
  "NONE". **Test:** grep finds no `PCREC_ENC_` test beside a prior read in
  `src/opt`/`src/gen`. [D122-2 (3); CS D7]
- **R24 ("none" is explicit, per reader).** Where no valid distribution
  exists, the accessor says so. Each reader states its fallback. A UNIFORM
  table is NOT a safe stand-in for "none": it equals the fallback for
  `rb_pick` (ties rightmost) and `rn_scan_index` (ties leftmost), but it
  changes `prefix_k`'s cost model. **Test:** the existing `-e utf8`
  zero-movers control extends to every reader. [RFP §3.3 clause 2; §8 item 4]
- **R25 (the key's meaning is defined).** A `freq` value carries a required,
  closed-set `encoding` row (RFP §3.4, ruled "when needed"; this row makes
  it needed). What the key MEANS, and which compiles may consume which key,
  is §3 Q6. [RFP §3.4, §10 Q6; §0 finding 3]
- **R26 (invalid bytes).** The analyzer MUST produce a byte histogram from
  any input, invalid UTF-8 included. `cpfreq` is produced only where the
  input decodes, which in practice means generator-controlled corpora.
  [RFP §3.5]

### 2.7 The analyzer (outside pcrec)

- **R27a (outside, same block).** The analyzer is not part of the `pcrec`
  binary or `libpcrec`. Its output is an `.rxt` carrying data blocks that the
  pcrec parser accepts unchanged. **Test:** analyzer output → `pcrec
  --list-source` parses clean, and round-trips through R4's reader. [D83; FI]
- **R27b (one counter).** The shipped generators (`third_party/*/generate.py`
  shape) and the user-facing analyzer MUST share ONE counting/normalising
  implementation. Two tools that count bytes differently would be a parallel
  mechanism, and the control would share a source with what it controls
  (the other way round). [memory `pcrec-general-mechanisms-not-special-cases`;
  learnings §3]
- **R27c (deterministic, pattern-blind).** The same exemplar gives
  byte-identical rows. The analyzer takes no pattern (D83 (1): "must not
  depend on any pattern"). **Test:** rerun and diff the rows. Its CLI has no
  pattern argument.
- **R27d (only writer).** A findings file is written by the analyzer only.
  Hand edits are a red line (FD §4.3, the R30 lesson). The provenance
  `analyzer` line names the tool and its version.

### 2.8 Named-library provenance, licensing, generators

- **R28 (third_party shape).** Each shipped named analysis lives in the
  `third_party/<source>-<version>/` shape:
  - the vendored corpus sample UNMODIFIED;
  - a `PROVENANCE.md` naming what derives from it;
  - a `generate.py` beside it;
  - `make gen-tables` regenerates, and `make test` runs `--check`, so drift
    fails the suite.
  [D83-A3; `third_party/README.md`]
- **R29 (licence).** A vendored corpus MUST carry a licence that permits
  redistribution in-tree, with its `LICENSE` shipped beside it. The data
  block's own `provenance` does not require `license` (a user's exemplar has
  none). The SHIPPED ones MUST state it anyway, in `PROVENANCE.md` and in the
  block. [`third_party/CLAUDE.md`; `rxt_format.md` provenance table]
- **R30 (independence from the bench).** No shipped analysis, the default
  included, may be derived from a pcrec-bench subject or a sample of one.
  Otherwise the bench would measure a prior fitted to itself. **Test:** each
  `PROVENANCE.md` names a source disjoint from `pcrec-bench/` corpora, and a
  review check greps for bench paths. [`prefix_k.c` header;
  learnings §3; RFP §2.1]
- **R31 (earned, not catalogued).** A named analysis ships when a customer's
  measured cell needs its subject class. D83-A3's list (`html`, `tsv`,
  `json`, `log`, `prose`) is a vocabulary, not a backlog. [D77; FI membership
  rule]

### 2.9 Size limits

- **R32.** Every kind has a declared maximum: rows per block, and entries for
  sparse kinds such as `cpfreq` (CJK corpora) and any run-level list. There
  is a declared maximum count of analyses per target. Each is a
  `docs/spec/limits.md` row. Over-limit input is refused by name, never
  truncated silently. **Test:** a limit fixture per kind. [D80;
  `limits.md` pattern]
- **R33 (built-in footprint).** If shipped analyses are embedded, their total
  bytes in `libpcrec.a` are reported, and a dense kind needs a D77
  justification (a bigram table is 65,536 entries per analysis per
  encoding). [D84, shipped bytes matter]

### 2.10 Failure modes and diagnostic tier (D26)

| failure | tier | behaviour |
|---|---|---|
| unknown analysis name / unreadable findings file | **hard error**, by name | refuse the compile (same class as an unknown `lib`) |
| malformed block (schema) | **parse error**, schema tier | existing `rxt_fail` machinery |
| a distribution that cannot be normalised (all zero, over the limit) | **hard error** | never a silent fallback |
| encoding key mismatched for this compile | **non-fatal diagnostic**, then fallback per R24 | RFP §3.3 precedent: a correct answer is available, so refusing is wrong and staying silent is not acceptable |
| a kind requested by a reader and absent from every named source | **silent** fall-through to the default (R8) | the normal case |
| stale findings (exemplar changed since analysis) | **not pcrec's to detect** (pcrec never sees the exemplar). The analyzer's `--check FILE EXEMPLAR` compares `sha256` | answers are unaffected (R34), so staleness costs speed only |

- **R33a.** Diagnostic wording is D26's lowest tier: name the thing and the
  reason, nothing more. [D26]

### 2.11 Testing and oracle — findings may change SPEED, never ANSWERS

- **R34 (answer identity under any findings).** For every corpus pattern ×
  engine × encoding, the answers compiled under a set of ADVERSARIAL
  synthetic findings MUST equal the answers under the default. The set:
  - uniform;
  - inverted (the default reversed);
  - one-hot (one byte holds all the mass, every other byte at the floor);
  - all-floor-but-one;
  - a random seeded table;
  - a table that makes every prior-reading row fire.
  This is the findings axis of `make test-axes`. Its oracle is the existing
  answer sets (libpcre2/python `re`, unchanged). It is legitimate BECAUSE a
  prior is "a prior and not a promise". **Sabotage:** a reader that lets a
  prior decide SOUNDNESS (e.g. skips a verify when ppm is small) is DETECTED
  by the one-hot table. [`prefix_k.c` header; D119 rule 5; S265 shape]
- **R35 (population census per analysis).** For each shipped analysis
  against the default, the census counts how many corpus artifacts move, per
  reader. A new analysis that moves zero artifacts is not earned (R31). An
  empty population is reported as empty, never as "no hazard"
  (RFP §3.2's K59 lesson). [learnings §3; K35]
- **R36 (selection witnesses).** Each reader carries at least one
  constructed witness that moves under a named findings table and does not
  move under the default. The witness must reach its site: the [MECH-REACH]
  rule, and a witness that stopped reaching its site is a red. [learnings
  §3 MECH-REACH]
- **R37 (the gate's control).** The `-e utf8` zero-movers control is kept.
  It is extended to "under utf8 with no utf8-valid distribution, zero
  movers across ALL readers", which is the check that D122-2 (3)'s gate move
  landed at the accessor. [RFP §8 item 4]
- **R38 (perf claims name their exemplar).** A bench claim for a
  findings-driven choice names the analysis used. The analysis MUST be
  disjoint from the measured subject (R30). The default-config bench numbers
  never use a findings input. [D119 landing bar; WAF §3.2's deployment
  warning]

### 2.12 Interaction with table-driven rows (D122-2 (4))

- **R39 (findings reach rows only through the accessor).** A row's `applies`
  predicate or `cost` may read findings ONLY by calling the accessor through
  `DfaSel.cx`/`Ctx`. `DfaSel` never carries a table. **Test:** grep finds no
  prior table in any `*Sel` struct.
- **R40 (row ORDER is findings-independent).** Findings may change which row
  APPLIES, never the list order, and never the total fallback. The deny flag
  stays the answer-identity handle, so R34 × each row's deny flag covers the
  cross product. **Test:** the lists are `static const` and do not change
  under R34's sweep.
- **R41 (a findings-gated row is still a row).** A density- or run-gated row
  such as C5's arms or C7's is ONE row with a predicate that reads the
  accessor. It is never a findings-specific parallel selector. SIMD rows
  (held) gain the arch predicate in the same slot later. [D122-2 (4); D122-3]

---

## 3. Questions for Frank

The questions are ordered by how much each one constrains the design. Each
gives the options and a recommendation, except Q3, whose weighing D83-A4
assigns to the design note.

**Q1. What does `analysis <name>` select: a BUNDLE or a BLOCK?**
The spelling in FD's D-e row (`analysis freq json`) and the shipped
`analysis <list>` disagree (§0 finding 4).
- (a) Bundle: `json` means every data block named `json`, across all kinds.
  Resolution runs per (name, kind) as in R8.
- (b) Block: `analysis freq json`, one line per kind.
- **Rec. (a).** D83-A1's "a set of named analysis values" names a bundle.
  Under (b), every caller has to know which kinds exist, and a new kind would
  mean editing every config.

**Q2. The merge rule.**
- (a) Per-kind override in list order: the first source that has the kind
  wins, then fall through (R8, R9).
- (b) Last-wins.
- (c) Blending or per-entry override.
- **Rec. (a)** plus CLI-over-config with a diagnostic (R10). Rule (c) out:
  a normalised distribution cannot be partially replaced (R9).

**Q3. Resolution route: `-I`/`<store>` (Route I) or a dedicated lookup
(Route D), or the hybrid?** See §2.3. No recommendation, because D83-A4
gives the weighing to the design note. Three facts bear on it:
- no data directory exists;
- `include <store>` is refused and `lib <store>` is reserved;
- [LIB]'s store would share the `<name>` namespace.

The ruling Frank's answer SHOULD give the design is narrower: **may shipped
analyses be compiled into `libpcrec.a`**, the `uprops` shape with no install
path? Both routes can then use that as the end of the search.

**Q4. The stamp.**
- (a) Always stamp (`RX_…` naming the source + a digest of consumed values),
  default included.
- (b) Stamp only when the source is not the default.
- **Rec. (a):** one abi bump, shared with the gate move (R21). A reader can
  then tell "built with default" from "built by an older compiler". R20's
  values-only digest keeps provenance edits from moving anything.

**Q5. The first run-level kind: measure now, or wait for S4(a)?**
C6 is the one customer whose SIGN is wrong under unigram.
- (a) Charter the R6 estimator measurement now, as a measurement lane with
  no `src/`. S4(a) then lands with the right kind.
- (b) S4(a) lands on the letter argmin (bench-best, WAF §3.2) and the
  run-level kind follows under measurement.
- (c) S4(a) waits.
- **Rec. (a).** The measurement is corpus arithmetic, cheap and
  Linux-independent, and it also answers WAF §5 Q2 (unruled). (b) is the
  D119 carve-out's own warning case: it wins the cell with the pick that
  loses in deployment.

**Q6. What the encoding key MEANS.** See §0 finding 3.
- (a) Key = the compile's `-e`, consumed only on equality. This is RFP §3.3
  clause 1 as written.
- (b) Key = the exemplar TEXT's encoding.
  - A `-e byte` compile consumes any measured byte histogram, because the
    bytes are the bytes.
  - A `-e utf8` compile consumes a `utf8`- or `ascii`-keyed one.
  - Shipped analyses reach every encoding through the `cpfreq` derivation.
- **Rec. (b).** Under (a), the most common deployment is refused: a UTF-8
  log, compiled `-e byte`. The inversion (a) guards against belongs to the
  hand-assigned default, and that still falls under R24's "none" outside
  `byte`.

**Q7. The shipped DEFAULT's identity.**
- (a) Keep today's hand table BYTE-IDENTICAL, repackaged as a named
  analysis with `provenance source authored` and its cited priors. Nothing
  moves, and the 12/12 out-of-sample agreement (RFP §4.3) stays valid.
- (b) Regenerate it from a `prose` `cpfreq` corpus (RFP §3.5) in this row.
- **Rec. (a) now, (b) as its own row under measurement.** Regenerating
  moves every C1-C4 artifact and voids RFP §4.3's evidence. The provenance
  record already has `authored`, so (a) is not a special case.

**Q8. Where the analyzer lives, and its language.**
- (a) An in-repo C program, a separate binary with zero dependencies, like
  pcrec.
- (b) A python3 script in `scripts/`, which is already a dev dependency.
- (c) The bench.
- **Rec. (a) or (b), in-repo, with one counter shared with the generators
  (R27b).** (c) is out: users need it, and the bench is read-only to pcrec.
  Frank's call is (a) vs (b): user-dependency-free against faster to write.

**Q9. Reference corpora: vendor samples in-tree, or tables only?**
- (a) Small in-tree samples (≤ ~1 MB per class) under a permissive licence.
  `--check` works offline.
- (b) Only the derived table plus provenance (url, sha256). Regeneration
  then needs a fetch.
- (c) Synthetic corpora from a generator (`fidelity synthesized`). No
  licence, but the statistics are only the author's assumptions.
- **Rec. (a)**, which is the third_party rule as it stands. (c) only for a
  class with no licensable sample, and labelled as such.

**Q10. Which named analyses ship FIRST?**
- **Rec.** Only a class with a measured customer cell:
  - web-request traffic, for C6 (WAF);
  - log lines, for C4's iso-ts movement.

  Nothing else until R35's census shows movement (R31).

---

## 4. Risks and non-goals

**This mechanism MUST NOT become:**

- **Pattern-specific PGO.** Tier-escalation counts, state-visit statistics,
  "which runs of THIS pattern occur": all D83 (2), a separate shape, a
  separate build and a separate result file. A run-level kind (R6) stays
  pattern-BLIND: it answers for any run and was measured without the
  pattern. [D83 (2); ENG-PGO]
- **A runtime mechanism.** No artifact reads statistics or adapts at match
  time. Findings are compile-time inputs only; generated code never
  depends on pcrec (CLAUDE.md, the compiler's first line).
- **A soundness input.** No reader may conclude that a byte is impossible
  (R3's floor) or skip a verify because of a prior. R34's sabotage row
  enforces this.
- **A second prior table or a second accessor** (RFP §2.3; CS P6 "owed: one
  gate at the accessor"; D122 (1)). That rules out `pcrec_findings_density`
  (a double, a parallel function, FSD §5.2 — already declined).
- **A raw-text reader in pcrec** (D83).
- **A catalogue** of kinds or named analyses nobody reads (R2, R31).
- **A bench fit** (R30, R38).

**Risks worth naming in the design:**

- **Run-level values LEAK in a way a byte histogram does not.**
  FI's premise that committing a findings file "leaks almost nothing"
  depends on it being a 256-count histogram. A top-K n-gram list or word
  list from a proprietary log can carry hostnames, user IDs and token
  prefixes. A bigram table leaks less. So R6's choice has a privacy
  dimension, and the analyzer should say what each kind reveals. [FI
  2026-08-29]
- **Test-surface explosion.** Findings × axes × encodings. R34 bounds it
  with a fixed adversarial set, not a product.
- **Silent artifact drift** when a shipped analysis changes (R22).
- **A per-cell win that is a deployment loss.** The WAF §3.2 warning,
  generalised: a findings choice validated only on the bench subject is
  unvalidated (R38).
- **The format lags the mechanism.** The `encoding` row, a run-level kind
  and Q1's selector are [DD-13b]'s to write (D83-A: "the `freq` block's
  FORMAT work stays under [DD-13b]"). The design has to schedule that wave,
  not work around it.
- **Spec drift already present, noted rather than fixed here.**
  - `rxt_format.md`'s head table says a `lib` file's "CONTENTS are not
    read", but `cli.md` §1 says they have been read since [DD-13b.W1.3].
  - The `freq` body table lists `provenance` as "at most one" and omits
    that the schema also marks it `required`.
  - FD's `analysis freq <ident>` spelling does not match the shipped
    schema's `analysis <list>` (§0 finding 4).

**What this is not deciding:** the accessor's signature, the stamp's
spelling, the row encoding, or the resolution route. All of them go to
step 2's design note, as the answers to §3 direct.
