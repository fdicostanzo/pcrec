# [RECEIVED INPUT] pcrec-bench's rxt_needs_v1.md — the [B42] capability-set format needs

RECEIVED 2026-09-12 from pcrec-bench (their docs/design/rxt_needs_v1.md,
lane b42rxtneeds, merged b108f7b in THEIR repo; announced by outbox item
O-26). Copied verbatim below the marker line for pcrec's design record —
the [DD-13b.W23] revision builds against THIS copy; on any doubt about
drift, re-fetch from the bench repo and diff. The bench's own repo copy
is canonical for THEIR process; this copy is canonical for OUR lanes.

Frank's rulings already attached to this input (O-26 §9, 2026-09-12):
- F-Q1: NO W2-only first sample — the first delivery is Tier 1 AND
  Tier 2 (both waves plus the extensions those tiers name).
- F-Q2: multi-line patterns are a MUST (roadblock #1 / N-2); the set
  will NOT flatten a (?x) pattern; pattern-esc (or equivalent) is
  first-delivery scope alongside the NUL refusal.

=== VERBATIM COPY BELOW — DO NOT EDIT ===

# What the capability survey set needs from the `.rxt` format

**[B42], lane `b42rxtneeds`, 2026-09-12. This note is FEEDBACK TO pcrec
(`pcrecdev1`), not a design of this project's own.** It says, need by
need, what a capability survey set built ON `.rxt` requires; which
existing W1/W2/W3 production carries each need and whether that
production's designed semantics actually fit; where no production exists
at all; and what this project will VERIFY when pcrecdev1 delivers.

---

## 0. Purpose, the ruling, and how to read this

### 0.1 The ruling this note exists to serve

Frank ruled on 2026-09-12 (plan row `[B42]`, RULINGS Q3):

> **Q3 `.rxt` = THE SET IS A DRIVER OF THE FORMAT**: build on `.rxt` for
> real, not the hybrid; when the effort hits an `.rxt` capability
> roadblock it PARKS, this project sends pcrecdev1 DETAILED FEEDBACK on
> the needed capabilities (against `~/pcrec/docs/spec/rxt_format.md` +
> `dd13_format/`), pcrecdev1 builds them, the effort RESTARTS and this
> project REVIEWS and VERIFIES that work.

Frank's framing, quoted by the manager: *"This is as much a driver of the
rxt format as anything."*

Two consequences bind everything below.

1. **The hybrid is off the table.** `docs/dev/research/2026-09-12-b42-rxt-as-source.md`
   (N3) §6 recommended Option B — `.rxt` holds pattern text and identity,
   a sidecar holds the rest — and `docs/design/capability_set_v1.md` §9.1
   ADOPTED it. Frank's ruling supersedes both. This note is written for
   Option A: **the set's own truth lives in `.rxt`**, and where it cannot,
   that is a format need, not a sidecar workaround. Where a need could
   still be met in the sidecar for one release, the table says so in the
   `priority` column and §4 sequences it; that is a scheduling
   observation, not a reopening of the ruling.
2. **The roadblock is not a failure.** The set PARKS at each one. This
   note's job is to make the parked list complete and precise enough that
   pcrecdev1 can build against it without a second round of discovery.

### 0.2 What was read, and what was MEASURED

Read in full: `~/pcrec/docs/spec/rxt_format.md` (the as-built contract),
`~/pcrec/docs/spec/cli.md` §1 (`--source`/`--target`/`--lib-path`),
`~/pcrec/docs/design/dd13_format/requirements.md` §5 (R-BENCH-1..9),
`~/pcrec/docs/design/dd13_format/format_design.md` §§1.3, 1.4, 2.8-2.10,
4.5, 6.2 and §7's open questions, and `~/pcrec/src/parse/rxt_source.c`
where the spec was silent. On this side: `docs/design/capability_set_v1.md`
v0.1 (§3-§6, §9, §12), the three R5 critic files, `docs/design/
subbench_directory_model.md` ([B29]), `pcrecbench/subbench.py`,
`tools/export_rxt.py`, `bench/syntax/subbench.toml`,
`bench/altwide/subbench.toml`, `schema/record.schema.json`.

**Eleven facts in this note were MEASURED against the pinned binary**
(`build/pcrec-d34c9131/build/pcrec --list-source`, pin d34c9131, abi 23 —
parse-only, no compile, nothing built) rather than inferred from the
spec. They are marked **MEASURED** where they appear, and §1.9 collects
them. Two of them contradict a claim a committed document in this repo
makes today (§1.9 items M2 and M11).

### 0.3 Relationship to R-BENCH-1..9

`~/pcrec/docs/design/dd13_format/requirements.md:316-411` states this
project's needs as R-BENCH-1..9, evidenced from APPROACH.md and Frank's
inputs. Every one of the nine is answered TODAY by a sidecar field
(`subbench_directory_model.md:127-140`). This note's relationship to them:

| id | the original ask (`requirements.md:<line>`) | this note |
|---|---|---|
| R-BENCH-1 | per-case feature tier, hazard class, size class, VERIFICATION METHOD (`:321-340`) | **CONFIRMS and EXTENDS.** The four fields fold into `tag` (W2) as `format_design.md:1825-1908` §4.5 already works out. The EXTENSION is that a capability set needs three more per-case field families the ask did not anticipate: PROVENANCE (§1.3, nine fields), REQUIRES capability tags with a CLOSED, validated vocabulary (§1.4), and `role` (§1.2 N-9). The verification-method half is confirmed as needed and found **INSUFFICIENT as specified**: `tag method=<name>` carries the method's NAME but not the oracle's VERSION, which a cross-engine correctness claim needs (§1.6 N-22) |
| R-BENCH-2 | a section keyed per TESTEE: what to include, which options (`:341-350`) | **CONFIRMS**, and finds one hazard the ask did not: D93 makes a `config` in a set file BEAT the command line, and this repo's whole testee matrix is command-line flags. A set that carries a testee roster needs a stated SCOPING rule (§1.7 N-29) |
| R-BENCH-3 | first-class "unsupported by this testee", counted, never silent (`:351-359`) | **CONFIRMS.** W3's `variant <testee> unsupported <reason>` is the right shape. EXTENDED: the capability set decides `unsupported` from a DECLARATION (`capability_set_v1.md` §5.3) rather than per-pattern-per-testee by hand, so the format needs to carry the REQUIRES tag the declaration reads (§1.4), not only the per-pair refusal |
| R-BENCH-4 | expectations strong enough to adjudicate correctness, NOT pcrec-shaped (`:360-367`) | **CONFIRMS**, and finds the sharpest gap in this note: expectations today are TESTEE-BLIND, one row per (pattern, subject, regime), and a POSIX-leftmost-longest engine's different-but-correct answer has nowhere to live (§1.6 N-12 — R5 finding B1's format half) |
| R-BENCH-5 | a per-CASE matching-convention tag (`:368-374`) | **CONFIRMS as necessary and INSUFFICIENT.** A convention TAG says which convention an expectation follows. It does not supply the SECOND expectation an engine with another convention is scored against. The tag without the alternate answer is unusable (§1.6 N-11, N-12) |
| R-BENCH-6 | subjects by REFERENCE, not inline (`:375-384`) | **CONFIRMS.** W2's `@file:` is the production. EXTENDED with two asks: an integrity hash on the reference (§1.5 N-14) and a statement of NUL-safety on the reference path (§1.5 N-15) |
| R-BENCH-7 | per-library pattern tweaks DECLARED, impossible to miss (`:385-393`) | **CONFIRMS.** W3's `variant` is the production. EXTENDED: `variant_kind`, `objective_preserved` and `capture_map` are three separate fields the sidecar carries today and `variant`'s designed body carries only two of (§1.7 N-27) |
| R-BENCH-8 | import from pcrec's own oracle-verified `.rxt` corpora (`:394-400`) | **CORRECTED.** `subbench_directory_model.md:554-560` Q4 states the import direction is lossless because "`foo_bar` is a legal slug". **It is not** — the record schema's slug rule forbids `_` (§1.9 M11). Every pcrec block name that is a C identifier with an underscore is an ILLEGAL bench `pattern_id` today. This is this project's problem to solve, not pcrec's, but the format note should not carry the wrong claim forward |
| R-BENCH-9 | the same section concept serves pcrec's own multi-config builds (`:401-411`) | **UNTOUCHED.** Nothing this set needs bears on it |

Two needs in §1 have no R-BENCH ancestor at all and are new with this
set: **per-pattern provenance** (§1.3) and **the capability/REQUIRES
model** (§1.4). Both come from Frank's `[B42]` charter items (1) and the
capability clause, which postdate DD-13a by two and a half weeks.

### 0.4 How to read §1's table

Seven columns, one row per need:

- **need** — stated precisely enough to check.
- **today** — where it lives in this project now, cited `file:line`.
- **production** — the EXISTING `.rxt` production that would carry it,
  spelled exactly as `format_design.md` §1.3 spells it, or **NEW** where
  none does.
- **fits?** — whether that production's DESIGNED semantics actually serve
  the need. `yes` / `partial (<what is missing>)` / `no`.
- **wave / status at d34c9131** — `BUILT`, `REFUSED BY NAME` (designed,
  in a later wave, refused as NOT IN THIS BUILD — `rxt_format.md:57-62`),
  or `ABSENT` (no production in any wave).
- **priority** — `MUST` (the set cannot ship a first sample without it),
  `SHOULD` (the set ships but a stated capability is missing), `COULD`.

Where `format_design.md`'s intent is ambiguous the row says so in the
`fits?` cell rather than resolving it; §5 collects those as questions for
pcrecdev1.

---

## 1. THE NEED TABLE

Fifty needs in eight blocks, numbered N-1..N-53 (three rows — N-29,
N-51, N-53 — are recorded for completeness and ask the format for
nothing). Counts by priority: **36 MUST** (one of them conditional on
N-42 landing), **9 SHOULD**, **5 COULD**. Counts by status at the pin:
**14 BUILT**, **2 BUILT AND LOSSY**, **20 REFUSED BY NAME** (designed, a
later wave), **15 ABSENT** (no production in any wave).

The MUST count is high because Frank's ruling makes it so: under the
hybrid, everything in blocks C through H could have stayed in a sidecar
and been a SHOULD. Built on the format for real, a set cannot express its
own patterns' provenance, tags, subjects or expectations without W2 and
W3, so those become MUSTs by the ruling rather than by this note's
judgment. §4 separates what blocks a FIRST SAMPLE from what blocks the
set's full claims.

### 1.1 Block A — pattern text

| # | need | today | production | fits? | wave / status | pri |
|---|---|---|---|---|---|---|
| **N-1** | one-line pattern text, raw bytes, no escaping | `patterns/<id>.rx`, read raw (`pcrecbench/subbench.py:242-246`) | `pattern` , ws , rest-of-line (`format_design.md:396`; `rxt_format.md:192-195`, `:210-212`) | **yes** — MEASURED byte-exact for ASCII, tab, backslash, mid-line CR (§1.9 M4) | W1, **BUILT** | MUST |
| **N-2** | a pattern with a LITERAL NEWLINE — a `(?x)` free-spacing body authored across lines, which family 6's VS Code `number` rule is in its source (`capability_set_v1.md:183`, N1 §18) | not exercised: no `.rx` file contains a newline (`subbench_directory_model.md:69-70`) | **NEW** — `pattern` is one line with no continuation and no escaping, so a newline has NO representation at all | **no** | **ABSENT** | **MUST** |
| **N-3** | raw high bytes (non-UTF-8) in pattern text — family 12 (`capability_set_v1.md:189`) | `.rx` files are raw bytes, never decoded (`subbench.py:242-246`) | `pattern` rest-of-line | **yes** — MEASURED byte-exact through `--list-source` (§1.9 M3) | W1, **BUILT** | MUST |
| **N-4** | a literal NUL byte in pattern text | not exercised | `pattern` rest-of-line | **no — SILENTLY TRUNCATED.** MEASURED: `pattern ab<NUL>cd` dumps as `ab`, exit 0, no diagnostic (§1.9 M1). The parser slurps the file and splits it into NUL-TERMINATED C strings (`~/pcrec/src/parse/rxt_source.c:437-456`), so every rest-of-line value ends at the first NUL | W1, **BUILT AND LOSSY** | SHOULD to EXPRESS; **MUST to REFUSE** (§2.7) |
| **N-5** | a pattern whose last byte is a CR | not exercised | `pattern` rest-of-line | **no — SILENTLY TRIMMED.** MEASURED (§1.9 M2): `\r\n` is trimmed to `\n` unconditionally (`rxt_source.c:450`), which is right for a Windows-edited file and wrong for a pattern that ends in CR. A CR anywhere ELSE in the line survives exactly | W1, **BUILT AND LOSSY** | COULD |
| **N-6** | a pattern larger than a comfortable line | `canonical_text` capped at 1 MiB by the RECORD, not by `.rxt` (`docs/design/record_schema.md` §4, KB-7) | `pattern` rest-of-line | **yes** — MEASURED: a 20,000-byte pattern line parses (§1.9 M9). `.rxt` imposes no line-length bound | W1, **BUILT** | COULD |

**Why N-2 is MUST and not SHOULD.** The charter's requirement (1) is
patterns from the wild. Free-spacing `(?x)` bodies authored across lines
are how real editor grammars, CRS rules and validators are actually
written; flattening one to a single line is a `fidelity: adapted` edit
whose correctness has to be proved by an oracle run
(`capability_set_v1.md:1089-1100`). Under Frank's 2026-09-12 ruling the set is
built on the format for real, so "flatten it because the format cannot
hold it" is exactly the kind of accommodation the ruling removes. **This
is roadblock #1.** MEASURED, the failure is at least LOUD: an indented
continuation line is refused by name ("a pattern block's lines are NOT
indented", §1.9 M8), not silently swallowed.

### 1.2 Block B — pattern identity and descriptive metadata

| # | need | today | production | fits? | wave / status | pri |
|---|---|---|---|---|---|---|
| **N-7** | a pattern id that is the RECORD's `pattern_id` with no second naming | `[[patterns]].name`, checked against the record schema's slug rule at load (`subbench.py:80-90, 161-162`) | `name` , ws , ident, widened to "a first byte that is a letter or `_`, then letters, digits, `_`, `-` or `.`" (`rxt_format.md:278-282`), unique in the file namespace | **yes.** The grammar was widened FOR this project (`rxt_format.md:290-296`). MEASURED: `crs-942.160` and `Upper.Name-1` both accepted; a duplicate name is refused by name (§1.9 M6, M7). The bench's slug rule is STRICTER (no `_`, no `.`, no uppercase) so every legal bench id is a legal `.rxt` name — the containment runs one way only, which matters for import (§1.9 M11) | W1, **BUILT** | MUST |
| **N-8** | a one-line human description per pattern | `[[patterns]]`'s TOML comment, not a field (`bench/syntax/subbench.toml:70`) | `description` , ws , rest-of-line, block-scoped, ONE-LINE ONLY (`rxt_format.md:297-298`; the W1.1 correction, `format_design.md:434-448`) | **partial.** One line is enough for a description. Two hazards: a SECOND `description` in one block SILENTLY OVERWRITES the first, last wins, no diagnostic (MEASURED, §1.9 M5); and the one-line rule means a provenance/adaptation sentence cannot live here (which is why §1.3 asks for fields, not prose) | W1, **BUILT** | MUST |
| **N-9** | per-pattern classification: `family`, `role` (`member`/`floor`), `hazard_class`, `size_class`, `feature_tier` | `[[patterns]]` five fields (`bench/syntax/subbench.toml:72-79`); `role` is `record_schema.md` §5 v1.3 | `tag` , ws , tag-item , { ws , tag-item } — repeatable, accumulating, bare labels and `k=v` pairs on one line (`format_design.md:416`, the U1 ruling at `:1846`) | **yes.** `format_design.md:1825-1908` §4.5 already maps all five. The bench's own vocabularies stay the bench's (AR-6) | W2, **REFUSED BY NAME** (MEASURED, §1.9 M10) | **MUST** |
| **N-10** | `hazard_class` is the field §6.3's whole rewrite rule keys on, and it must be a CLOSED set the format can refuse a typo in | closed enum in the record schema (`schema/record.schema.json:298`; `record_schema.md:381`) | `tag hazard=<label>` | **partial — no vocabulary declaration.** `tag-value` is free vocabulary by design (`format_design.md:337-339`; the AR-6 argument at `:1229`). A typo (`hazard=exponential-backtraking`) is a legal tag. R5 finding B3 makes the identical point about `patterns[].tags` on this side | W2, **REFUSED BY NAME** | **MUST** |

**Roadblock #2 is N-9 plus N-10 together.** `tag` is the production that
carries essentially every descriptive field the set has, and it is
refused by name at the pin. Its *shape* fits; what is missing is a way to
DECLARE a closed vocabulary and have the parser refuse a value outside
it. §2.2 proposes one.

### 1.3 Block C — per-pattern PROVENANCE (no production exists in any wave)

The charter's requirement (1): "provenance recorded per pattern".
`capability_set_v1.md:311-339` §4.1 fixes a CLOSED nine-field record, and
Frank's Q1 ruling adds a tenth obligation (an `inspired` pattern is
validated as not an actual copy of its source). N3 §1.3 establishes that
**no pattern-level provenance production exists in any wave** — the
`freq` data block has required provenance fields (`exemplar`, `bytes`,
`sha256`, `analyzer`, `date`; `format_design.md:1272-1278`) but that
family exists for exemplar-analysis findings, not for a pattern's origin.

| # | need | today | production | fits? | wave / status | pri |
|---|---|---|---|---|---|---|
| **N-11** | `source_name` — a registered source slug | — | **NEW** | no | **ABSENT** | MUST |
| **N-12** | `source_url` — the exact URL fetched | — | **NEW** | no | **ABSENT** | MUST |
| **N-13** | `source_ref` — file/rule/line inside the source (`rules/REQUEST-942-…conf#942160`) | — | **NEW** | no | **ABSENT** | MUST |
| **N-14** | `licence` — an SPDX id from the source's own LICENSE, fetched | — | **NEW** | no | **ABSENT** | MUST |
| **N-15** | `licence_note` — where a source's own licence metadata disagrees with itself (the Davis Zenodo/GitHub mismatch, `capability_set_v1.md:464-466`) | — | **NEW** | no | **ABSENT** | SHOULD |
| **N-16** | `retrieved_utc` — RFC 3339, the date of the fetch that produced THIS text | — | **NEW** | no | **ABSENT** | MUST |
| **N-17** | `fidelity` — `verbatim` / `adapted` / `inspired`, a CLOSED three-value set | — | **NEW** | no | **ABSENT** | MUST |
| **N-18** | `adaptation` — one checkable sentence, required when `fidelity ≠ verbatim` | — | **NEW** | no | **ABSENT** | MUST |
| **N-19** | `attribution` — required where the licence demands it (CC BY-SA 4.0) | — | **NEW** | no | **ABSENT** | MUST |

**Why prose in `description` is not an answer.** It is the answer the
format offers today (W1, BUILT) and `capability_set_v1.md:340-346`
already rejects it: a reviewer checking sixty attributions against sixty
prose sentences is the failure mode a derived, checkable table exists to
close. Three further reasons specific to the format: a block's
`description` is ONE LINE (`rxt_format.md:297-298`), nine fields do not
fit in one line; a second `description` silently overwrites the first
(§1.9 M5), so a two-line workaround loses data without saying so; and
conditional REQUIREDNESS (`adaptation` iff `fidelity ≠ verbatim`) is the
kind of rule the format already knows how to enforce structurally — the
`freq` block's `question`/`reader` lines are required and a block without
them is refused (`format_design.md:1250-1258`), which is the precedent
§2.1 builds on.

**Roadblock #3.** Nine fields, no production, and requirement (1) is the
charter's first item.

### 1.4 Block D — the capability model (REQUIRES, and the closed vocabulary)

The charter's standing clause: every pattern carries what an engine must
support to run it, and an engine that cannot is a recorded `unsupported`
outcome, never an error. `capability_set_v1.md:497-531` §5.1 fixes a
sixteen-tag vocabulary (fifteen in the table plus `true-end-anchor` added
at `:739`).

| # | need | today | production | fits? | wave / status | pri |
|---|---|---|---|---|---|---|
| **N-20** | per-pattern REQUIRES tags (`backrefs`, `lookaround`, `lookbehind-variable`, `atomic-possessive`, `recursion`, `conditionals`, `k-reset`, `control-verbs`, `unicode-properties`, `named-groups`, `free-spacing`, `callouts`, `span-reporting`, `non-utf8-subject`, `captures`, `true-end-anchor`) | nothing — this set is the first to need it; `[[patterns]].tags` is the nearest thing and is DIAGNOSTIC, not filterable (`record_schema.md:1025`, R5 B3) | `tag requires=<label>` (W2), by the same generic mechanism as N-9 | **partial.** The carrier fits. What does NOT fit is the CLOSED-SET requirement: `capability_set_v1.md:521-525` states "the vocabulary is CLOSED and validated at set load. A tag outside it is a load error naming the closed set", and `tag`'s value space is deliberately free | W2, **REFUSED BY NAME** | **MUST** |
| **N-21** | a DECLARATION of the closed vocabulary, in the file, that the parser enforces | — | **NEW** | no | **ABSENT** | **MUST** |
| **N-22** | per-CONFIG capability declarations — which tags a given (engine, version, config) SATISFIES; `pcre2-dfa` and `pcre2-interp` are one library at one version with different tag sets (`capability_set_v1.md:532-552`) | `testees/<engine>/configs.toml` would gain a `capabilities = [...]` key (proposed, unbuilt) | `config <name>` body + `testee`/`option` (W3) — the section concept R-BENCH-2/9 names | **partial.** W3's `config` body has `testee engine-ref` and `option tag-pair` (`format_design.md:376-377`) and nothing that says what an engine CAN do. `option capability=backrefs` would work syntactically and would be an abuse: `option` is "that engine's options" (`:377`), a build/runtime setting, not a capability claim | W3, **REFUSED BY NAME** | SHOULD |
| **N-23** | the pre-compile policy `REQUIRES(pattern) ⊄ capabilities(config) ⇒ unsupported-by-declaration` decided BEFORE any compile (`capability_set_v1.md:554-585`) | nothing emits that outcome today (R5 B7: it is schema-legal and has never been produced) | consumes N-20 + N-22; the OUTCOME is W3's `variant <testee> unsupported <reason>` | **yes once N-20/N-22 exist** — the outcome production is right; R-BENCH-3 and AR-3 already rule it (`format_design.md:2044`) | W3, **REFUSED BY NAME** | SHOULD |

**Note on where the capability declaration belongs.** It is genuinely
arguable that per-CONFIG capabilities are the bench's business and not
the format's: they describe an ENGINE, not a set. This note asks for them
in the format anyway, for one reason: `format_design.md`'s own §4.5 puts
`[testees.<id>]`'s whole content into `config` blocks with `testee`
lines, and a capability list is the one field of that section a reader of
the FILE needs in order to understand why a pattern has no result for a
testee. If pcrecdev1 prefers to leave it bench-side, that is a legitimate
answer and §5.1 P-Q4 asks it directly — but then the format owes nothing and
this project keeps a second file, which is the hybrid Frank's ruling
removed.

### 1.5 Block E — subjects

| # | need | today | production | fits? | wave / status | pri |
|---|---|---|---|---|---|---|
| **N-24** | small typed subjects inline | generated `subjects/<id>.bin` + `manifest.tsv` (`subbench.py:184-213`) | `quoted-subject` with the seven-escape vocabulary (`rxt_format.md:374-385`) | **yes** for short ASCII-ish subjects | W1, **BUILT** | MUST |
| **N-25** | LARGE subjects by reference — 64 KB to 1 MB throughput runs (`capability_set_v1.md:216-244`) | `throughput/` tree + `manifest_throughput.tsv` | `@file:"path"` (`format_design.md:333`, semantics at `:1183-1208`) | **yes** — local spelling only, relative to the naming file, the file's bytes ARE the subject, NUL-safe, no size limit | W2, **REFUSED BY NAME** | **MUST** |
| **N-26** | an INTEGRITY HASH on a subject reference — every subject this project measures carries a committed sha256 and `make check` re-derives it byte for byte (`subbench.py:184-213`; the generic manifest gate, `tools/CLAUDE.md`) | `manifest.tsv` columns `id len sha256 description [periodic]` | `@file:` | **no — DECLINED BY DESIGN.** `format_design.md:1203-1208`: "No content hash on a subject reference. ARGUED... provenance is required exactly where the source is not committed." The reasoning is sound for pcrec's corpus and does not transfer: our subject trees are GITIGNORED and regenerated (`subbench.py:37-40`), so a `.rxt` reference points at a file that is NOT committed and NOT reviewed. §2.5 asks for an optional hash, not a mandatory one | W2, **REFUSED BY NAME**, and the extension is **ABSENT** | **MUST** |
| **N-27** | subject METADATA — a stable subject id, byte length, a description, the `periodic` column ([B17]) | `manifest.tsv` | **NEW** — `@file:` carries a path and nothing else; there is no subject id at all, and a case's identity is `file:line` (`format_design.md:2279-2284`) | **no.** Every expectation key in this project is `(pattern, subject_id, regime)` (`subbench.py:268-271`); every report row and every interpreter fact names a subject by id. `file:line` is not a substitute — it moves when a line is inserted | **ABSENT** | **MUST** |
| **N-28** | subjects that are not valid UTF-8, and subjects containing NUL — family 12 (`capability_set_v1.md:189`) | raw bytes throughout | `@file:` | **yes, as designed** — `format_design.md:1193-1199` states file-subject bytes are taken raw, NUL-safe, no decoding. **UNVERIFIED at the pin** (the production is refused, so nothing could be measured). An INLINE quoted subject carries `\xHH` and so can express a high byte but the driver protocol passes subjects as `argv` strings, which "can carry neither a NUL nor a megabyte" (`:1200-1202`) | W2, **REFUSED BY NAME** | MUST |
| **N-29** | a SET-LOCAL generator beside its output, with the manifest re-derivable | `gen_subjects.py` + `gen_throughput_subjects.py` per set, gated by `make check-harness` | "the directory convention" (`format_design.md:1847`) — an explicit non-production | **yes, as a convention.** Nothing is asked of the format here; recorded so the list is complete | n/a | n/a |

**Roadblock #4 is N-27, and it is quieter than the others.** `@file:`
carries a PATH. Every expectation key, every report row and every
interpreter fact in this project names a subject by ID
(`subbench.py:268-271`), and the format's answer is that a case's
identity is `file:line` (`format_design.md:2279-2284`). A line number
moves when a line is inserted, and a generated fragment's line numbers
move on every regeneration — so an `.rxt`-sourced set would have no
stable name for the thing every one of its numbers is about. §2.5 asks
for `as <id>` on the reference.

### 1.6 Block F — expectations, conventions, and the oracle

This block contains the need this note is least able to route to an
existing production, and the one R5 finding B1 identified independently
on the harness side.

| # | need | today | production | fits? | wave / status | pri |
|---|---|---|---|---|---|---|
| **N-30** | match / no-match with a byte span, per (pattern, subject, regime) | `expectations.tsv`, 9 columns (`subbench.py:124-138`) | `m` , ws , subject , ws , int , ws , int / `n` , ws , subject (`rxt_format.md:230-233`) | **yes** | W1, **BUILT** | MUST |
| **N-31** | a match from an explicit start position | not used by this project today | `ms` / `ns` (`rxt_format.md:234-237`) | yes | W1, **BUILT** | COULD |
| **N-32** | a FIND-ALL count over a subject (the throughput regime's `nmatches`) | `expectations.tsv`'s `nmatches` column | `mc` , ws , subject , ws , int (`format_design.md:417`) | **partial — the non-overlap rule is unstated.** This project's driver protocol fixes `pos = max(end, pos+1)` (`pcrecbench/adapters.py:19-23`). `mc`'s designed semantics are one integer beside a subject; whether it counts non-overlapping matches under the same rule is not stated anywhere I could find. Two engines counting differently would both "pass" | W2, **REFUSED BY NAME** | **MUST** |
| **N-33** | CAPTURE spans per case | not carried — `expectations.tsv` has no capture columns at all (MEASURED by pcrec, `format_design.md:1979`, and still true) | `g` / `gp` , ws , slot , ws , span (`rxt_format.md:239-267`) | **partial and pcrec-shaped.** `g` is scored against the artifact's own `RX_NCAPS` and `gp` has a pcrec-specific `pending-vm` bucket. T-3 flags exactly this (`format_design.md:2033`); the engine-neutral resolution is `variant … groups <name>=<n>` (W3). Not needed for v1 (this project's OD-B9 is unopened) but it is where capture checking would land | W1 (`g`/`gp`), **BUILT**; the neutral half W3, **REFUSED** | COULD |
| **N-34** | the MATCHING CONVENTION an expectation follows, per case — `perl-leftmost-first` / `posix-leftmost-longest` / `all-ends` | `[[patterns]].convention` (`bench/syntax/subbench.toml:76`), carried into the record's `testee.conventions` and never read by anything (R5 B1, B7) | `tag convention=<label>` (W2), as `format_design.md:1845` maps it | **yes as a TAG** | W2, **REFUSED BY NAME** | MUST |
| **N-35** | an expectation under a NON-canonical convention — the SECOND correct answer a `posix-leftmost-longest` engine gives to `a\|ab` on `"ab"` | **nothing.** `Subbench.expectation()` is keyed `(pattern, subject_id, regime)` with no testee axis (`subbench.py:268-271`); `harness.outcome_for()` has no convention parameter (R5 B1) | **NEW.** `m`/`n` carry no qualifier; `variant` supplies different pattern TEXT for a testee, never a different expected ANSWER for the same text | **no** | **ABSENT** | **MUST** |
| **N-36** | which ENGINE checked an expectation | `[expectations].default_method` conflates it with the method | `oracle` , ws , ( `python` \| `pcre2` \| `none` <reason> ), file-level or block-scoped, block wins (`format_design.md:1209-1241`) | **partial — a closed engine enum of two.** The set's roster is pcre2, RE2, Rust `regex`, Oniguruma, TRE, Vectorscan, python, perl (`capability_set_v1.md` §8). `oracle` admits `python` and `pcre2` and nothing else. A set whose family 11 needs a POSIX engine as ITS oracle cannot name one | W3, **REFUSED BY NAME** | **MUST** |
| **N-37** | the verification METHOD, per case — R-BENCH-1's own ask, including non-oracle methods | `[expectations].default_method = "libpcre2-differential"` | `tag method=<name>` — pcrec's own ruling that method and engine are TWO fields (`format_design.md:1850`, r44-consumers U3) | **yes** | W2, **REFUSED BY NAME** | MUST |
| **N-38** | the oracle's VERSION — "checked against libpcre2 **10.46**" | implicit: `pcrecbench/oracle_pcre2.py` binds whatever the box has; the record carries the engine version of the TESTEE, not of the oracle | **NEW.** `oracle pcre2` names an engine with no version slot; `engine-ref = ident , [ "/" , version-chars ]` exists but only for `testee` (`format_design.md:379`) | **no** | **ABSENT** | SHOULD |

**Roadblock #5, and it is the deepest one: N-35.** The set's family 11
(`semantics-divergence`, six members, v1) exists to measure engines that
answer DIFFERENTLY AND CORRECTLY. R5 finding B1 establishes that this
project's harness cannot score that today. This note adds the format
half: **`.rxt` cannot express it either.** A case line is one expected
answer for one (pattern, subject); `variant` changes the TEXT for a
testee, not the ANSWER. Whatever pcrecdev1 builds, the format needs a way
to say "under `posix-leftmost-longest` the answer to this case is
`0 2`, and a testee tagged with that convention is scored against it."
§2.4 sketches one.

### 1.7 Block G — per-testee variants and the testee roster

| # | need | today | production | fits? | wave / status | pri |
|---|---|---|---|---|---|---|
| **N-39** | a per-engine SPELLING variant of a pattern, declared beside it and impossible to miss | `[testees.<id>].variant` (`harness_contract.md:41-55`, quoted at `subbench_directory_model.md:85-86`) | `variant` , ws , ident , ws , rest-of-line (`format_design.md:419`, `:421-423`) | **yes** for the text | W3, **REFUSED BY NAME** (MEASURED, §1.9 M10) | MUST |
| **N-40** | a per-engine DECLARED REFUSAL with a reason | `[testees.<id>].unsupported` | `variant <testee> unsupported <reason>` (`format_design.md:421`) | **yes** — one line kind for both halves of the axis, which `format_design.md:1873-1874` explicitly designed | W3, **REFUSED BY NAME** | MUST |
| **N-41** | `variant_kind` (`syntax-only` / `restructured`), `objective_preserved` (a reviewed statement), `capture_map` | three separate sidecar fields (`record_schema.md:1026-1038`) | `variant`'s body carries text and an optional `groups <name>=<n>` map (`format_design.md:422-423`); `objective_preserved` is `tag variant-note=…` (`format_design.md:1887`) | **partial.** `capture_map` ↔ `groups` fits. `variant_kind` has NO carrier — it is a closed two-value enum this project's reporter is meant to show beside a number (`requirements.md §4.5`, and R5 B2 finds the reporter never implemented it). `tag variant-note=` carries prose but a `tag-value` may contain **no whitespace** (`format_design.md:339`), so a reviewer's sentence does not fit in one | W3 + W2, **REFUSED BY NAME**; `variant_kind` **ABSENT** | SHOULD |
| **N-42** | a testee ROSTER for NON-pcrec engines, with per-engine options | `[testees.<id>].options` (empty on every set today) | `config <name>` with `testee engine-ref` + `option tag-pair` lines, enumerated by a head `use config-list` (`format_design.md:376-377`, `:355`) | **yes in shape**, with the D93 hazard below | W3, **REFUSED BY NAME** | SHOULD |
| **N-43** | **a set file that declares NO pcrec `target` and NO pcrec `config`, legally and PERMANENTLY** | n/a — the exporter already writes such files (`tools/export_rxt.py:34-37` rule 5) | the absence of `target`/`config`; "No `target` and anything else builds NOTHING… It is not an error" (`rxt_format.md:126-127`) | **yes today** — MEASURED: an authored head-plus-blocks file with no `target` and no `config` parses and dumps cleanly (§1.9 M12). What is missing is a CONTRACT that this stays true | W1, **BUILT**; the guarantee **ABSENT** | **MUST** |
| **N-44** | a scoping rule so a set's own config can never pin this project's testee matrix | the exporter's rule 5 — never write `config`/`flags`/`engine`/`budget`/`encoding` (`tools/export_rxt.py:34-37`) | **NEW.** D93: "a `.rxt` source's composed config wins over a command-line flag on the same axis" (`subbench_directory_model.md:441-448`), and `engine` composes more-specific-wins (`rxt_format.md:133-136`) | **no.** The moment a set carries a `config … testee re2/2024-07-02` block (N-42) the file has configs, and a reader has no way to know that the `pcrec` half of those configs must never reach a build. §2.6 asks for the separation | **ABSENT** | **MUST if N-42 lands** |

**Roadblock #6 is the D93 interaction.** `format_design.md:2198-2284`
§6.2's worked bench file carries `config pcrec` / `config pcre2` /
`config re2` and a `use` line naming all three. Under D93 the `config
pcrec` block in a file this project treats as its corpus WINS over the
adapter's command line, and this project's entire sixteen-config pcrec
testee matrix is command-line flags (`testees/pcrec/configs.toml`). The
worked example and D93 are both right on their own and collide when the
file is a bench set. This is a DESIGN question for pcrecdev1, not a bug.

### 1.8 Block H — set-level identity, composition, and tooling

| # | need | today | production | fits? | wave / status | pri |
|---|---|---|---|---|---|---|
| **N-45** | set `id` and `version` — the frozen snapshot records compare within (`docs/design/requirements.md §5`) | `subbench.toml`'s `id`/`version` (`bench/syntax/subbench.toml:5-6`) | `tag id=capability version=0.1` file-level (`format_design.md:1838`) | **yes**, with N-10's caveat (free vocabulary; a typo in `version` is a legal tag) | W2, **REFUSED BY NAME** | MUST |
| **N-46** | set `objective` + `objective_kind` + `description` — multi-paragraph prose | `subbench.toml` (`bench/syntax/subbench.toml:7-49`) | head `description` with the `\|` BLOCK SCALAR (`rxt_format.md:196-203`), plus `tag objective=<kind>` | **yes** — MEASURED: a head block scalar parses and dumps with `\n` escapes preserved (§1.9 M12) | W1, **BUILT** (the `tag` half W2) | MUST |
| **N-47** | the BLINDING / authorship statement — which discipline the author worked under (pcrec D27; `bench/syntax/NOTES.md`) | `NOTES.md` prose | head `description` block scalar, or `tag` | **yes as prose**; there is no structured carrier and this note does not ask for one | W1, **BUILT** | COULD |
| **N-48** | which REGIMES the set exercises, and per-pattern regime membership | `regimes = [...]` (`bench/syntax/subbench.toml:54`); every pattern runs every declared regime (`subbench.py:154-157, 258-266`) | `tag regime=search_short throughput` file-level, refined per block; and for a per-regime SUBJECT SET, `format_design.md:1888-1901` §4.5 item 4's mechanism: name the canonical pattern once as a definition and write one block per regime whose pattern is `(?&<name>)` | **NO for the per-regime mechanism, on this project's ids.** A definition whose name carries `-` or `.` **cannot be called from a pattern** — `(?&cls-upto-1024)` goes through PCRE2's own group-name grammar and is refused there (`rxt_format.md:284-291`). EVERY pattern id in this repo's five sets is a hyphenated slug. §4.5's own regime mechanism is therefore unusable for this project unless ids are renamed to identifiers — which re-introduces exactly the name map the widened grammar was created to abolish (`rxt_format.md:290-296`) | `tag` W2, **REFUSED**; the wrapper mechanism **BROKEN for our ids** | **MUST** |
| **N-49** | the regime → subject-set mapping, and `short_search_max_bytes` | `subbench.py:258-266`; `[subjects].short_search_max_bytes` | `tag short-search-max-bytes=256` (`format_design.md:1848`) | **partial.** The tag carries the number. The MAPPING (which subjects a regime sees) is harness semantics that `format_design.md` §4.5 resolves by giving each regime block its own subject list — which is N-48's broken mechanism | W2, **REFUSED**; the mapping **ABSENT** | SHOULD |
| **N-50** | a shared SUBJECT VOCABULARY across sets, or across a set's own fragments | not needed today; each set generates its own | `include` , ws , path-ref (`format_design.md:353`); fragments are blocks-only, no head (`format_design.md:2232`) | **yes in shape.** The capability set would want it for the generated-fragment split §6.2 models (one entry file, `include`d case fragments). Population accounting is designed (`format_design.md:1289-1300`) | W2, **REFUSED BY NAME** (MEASURED, §1.9 M10) | SHOULD |
| **N-51** | a CONTENT HASH over the whole set, so a record names exactly what was measured | `Subbench.content_hash()` over every committed file in the directory (`subbench.py:287-311`); carried as `subbench.content_hash` in every record | **nothing is asked of the format** — a `.rxt` file is a committed file and hashes like any other. Recorded so the list is complete; note that `include`d fragments and `@file:` subjects must ALL be inside the hashed directory, which is a bench-side rule | n/a | n/a | n/a |
| **N-52** | **a head-only READER that emits the descriptive productions as TSV**, so this project never writes a second parser | `pcrec --list-source` today, used in the export→verify direction (`tools/selfcheck.py`'s `check_rxt_export`, [B38]) | `--list-source`'s sixteen-column TSV (`rxt_format.md:425-442`) | **partial, and this is the tooling ask.** The dump has NO column for `tag`, `oracle`, `variant`, `mc`, `requires` or any provenance field, and none for a case line at all. `--list-source` is explicitly THE SEAM (`rxt_format.md:418-423`) and the reason the harness grows no head parser; the same argument applies to every descriptive production W2/W3 adds | W1 **BUILT**, the extension **ABSENT** | **MUST** |
| **N-53** | comments stay operational; every machine-readable fact is a FIELD | `subbench.toml` comments are prose only | R-RXT-2 (`requirements.md:59`) and the `description`-is-a-field ruling (`format_design.md:450-457`) | **yes — and this note endorses it without qualification.** No need below is proposed as a `#` convention. `rxt_format.md:149-150`: whole-line `#` only, a `#` elsewhere is data — MEASURED: `pattern #` is a pattern, not a comment (§1.9 M13), which is what makes `bench/altwide`'s and `bench/syntax`'s floor patterns expressible | W1, **BUILT** | n/a |

### 1.9 The thirteen MEASURED facts

Every one from `build/pcrec-d34c9131/build/pcrec --list-source` at pin
d34c9131 (abi 23), parse-only — no compile, no artifact, no timing, so
the box's state is irrelevant to every number here.

**ARCHIVED, with its reproducing script beside it** (the D35 convention,
`docs/dev/measurements/CLAUDE.md`):
`docs/dev/measurements/2026-09-12-rxt-format-probes-d34c9131.txt` is the
verbatim output under a source header, and
`docs/dev/measurements/probe_rxt_format.py` re-derives it
(`python3 docs/dev/measurements/probe_rxt_format.py`, under a second;
`$PCREC_BIN` overrides the pin). Twenty probes produce
the thirteen facts below; each fixture is at most six lines and is
printed beside its result, so a reviewer re-runs the whole set at the
DELIVERED pin and diffs (§3 group G3).

| # | probe | result |
|---|---|---|
| **M1** | `pattern ab<NUL>cd` | **TRUNCATED to `ab`. Exit 0, no diagnostic.** The parser splits the slurped file into NUL-terminated C strings (`rxt_source.c:437-456`), so every rest-of-line value ends at the first NUL. **This resolves N3 §5's explicitly unverified risk: the answer is silent data loss, not refusal** |
| **M2** | `pattern abc\r\n` | dumps as `abc` — the CR is trimmed. Documented (`rxt_source.c:395-396`) and correct for a Windows-edited file; lossy for a pattern that ends in CR |
| **M3** | `pattern caf\xe9[\x80-\xff]+` | **byte-exact round trip** through the dump's `\xNN` escaping |
| **M4** | a literal TAB mid-pattern; a doubled backslash; a mid-line CR; trailing spaces | all **byte-exact**. Trailing spaces are kept (rest-of-line is data) |
| **M5** | two `description` lines in one block | **the second SILENTLY WINS.** No diagnostic, exit 0 |
| **M6** | `name crs-942.160`, `name Upper.Name-1` | both accepted — the widened grammar, confirmed |
| **M7** | two blocks with the same `name` | refused by name, exit 1: "duplicate block name 'dup' (already named …)" |
| **M8** | a `(?x)` pattern continued on an indented second line | refused by name, exit 1: "a pattern block's lines are NOT indented". **LOUD, which is the good half of N-2** |
| **M9** | a 20,000-byte `pattern` line | parses; no line-length bound |
| **M10** | `tag`, `variant`, `oracle`, `include` | each refused BY NAME with its wave: "'tag' is a wave-2 pattern-block declaration and is NOT IN THIS BUILD… the keyword is real, not a typo". Exactly as `rxt_format.md:57-62` promises |
| **M11** | this repo's slug rule `^[a-z0-9]([a-z0-9-]*[a-z0-9])?$` against a pcrec-style block name | `iso_ts` is **NOT** a legal bench `pattern_id` (underscore is not in the slug alphabet); nor is `crs.942` or `Upper`. **`subbench_directory_model.md:554-560` Q4's claim that the import direction is lossless because "`foo_bar` is a legal slug" is WRONG.** Ours to fix, not pcrec's, but R-BENCH-8 should not inherit the error |
| **M12** | an authored file: head `description \|` block scalar, two blocks with `name` + one-line `description`, **no `target`, no `config`** | parses; dumps one `description` head row and two `pattern` rows with `line`, `name`, `value` (the block description) and `pattern` columns filled. This is N-43's shape working today |
| **M13** | `pattern #` | a pattern, not a comment — the floor-pattern case |

One further measured observation with no probe number, because it is an
absence rather than a result: **`--list-source` accepted a block
containing `m @file:"subj.bin" 0 3` without complaint.** The head parser
recognises `m` as a block keyword and never reads its value
(`rxt_source.c:153-166`'s comment says so: "it reads none of their
values"), so a `@file:` subject inside a case line passes the dump
silently even though `@file:` is a refused W2 production. `--list-source`
is therefore not a validator for case-line content — which matters for
§3's acceptance checks and for N-52.

---

## 2. The productions this would need

Twelve proposals. Each gives a grammar sketch in `format_design.md`
§1.3's own EBNF style, states scope and repeatability, and says what
pcrec's OWN harness could do with it — because the format's stated stance
is one format for both repos (`format_design.md:1903-1908`: "what the
bench must still own… this note's contribution is that when they do, the
sidecar has somewhere to go"), and an ask that only serves one consumer
is a worse ask.

**These are sketches, not a specification.** Every one is pcrecdev1's to
accept, redesign or refuse. Where this note has a preference it says so;
where the choice is genuinely open it says that instead.

### 2.1 A `provenance` block — needs N-11..N-19

**The gap.** Nine required-or-conditional fields per pattern, no
production in any wave, and `description`'s one line cannot hold them
(§1.3).

**The precedent to copy, not invent.** The `freq` data block already does
exactly this shape: a keyword, a name, an indented body of `<key> <value>`
lines, with SOME LINES REQUIRED and a block missing them REFUSED
(`format_design.md:1242-1288`; the membership rule at `:1250-1258`, the provenance half at `:1272-1278`). Its
own provenance half — `exemplar`, `bytes`, `sha256`, `analyzer`, `date`
— is required "because the exemplar is absent by design" (`:1279-1283`).
A wild pattern's source is absent by exactly the same logic: a URL fetched
on a date, a licence nobody committed into this repo.

**Grammar sketch** (W2; block-scoped; at most ONE per pattern block):

```ebnf
(* ---------- body: a pattern block ---------- *)
block-line  = … | provenance-block ;

provenance-block = "provenance" , eol , { INDENT , prov-line , eol } ;
prov-line =
      "source"     , ws , ident            (* a registered source slug, REQUIRED *)
    | "url"        , ws , rest-of-line     (* the exact URL fetched,  conditional *)
    | "ref"        , ws , rest-of-line     (* file/rule/line inside it, conditional *)
    | "licence"    , ws , spdx-id          (* from the source's own LICENSE, REQUIRED *)
    | "licence-note" , ws , prose-value    (* optional *)
    | "retrieved"  , ws , iso-date         (* RFC 3339,                 REQUIRED *)
    | "fidelity"   , ws , ( "verbatim" | "adapted" | "inspired" )   (* REQUIRED *)
    | "adaptation" , ws , prose-value      (* REQUIRED iff fidelity != verbatim *)
    | "attribution", ws , prose-value ;    (* REQUIRED iff the licence demands it *)
```

**Scope and rules.**

- Block-scoped, at most one per pattern block. A SECOND `provenance`
  block in one block is REFUSED by name — not last-wins, which is the
  `description` hazard M5 measured.
- `source`, `licence`, `retrieved`, `fidelity` are REQUIRED; a block
  missing one is refused naming the missing line, exactly as a `freq`
  block without `question`/`reader` is.
- `url` and `ref` are REQUIRED unless `source` is the reserved slug
  `authored`, which is the value a freshly-written pattern carries and
  which by definition has neither. An `authored` block that writes one
  anyway is refused: the slug and the fields must agree, or `authored`
  stops meaning anything.
- `adaptation` is REQUIRED iff `fidelity` is not `verbatim`. This is the
  one conditional the format would have to enforce and it is the whole
  value of making it structural: a mechanically-changed pattern with no
  stated change is the failure a reviewer cannot catch by reading.
- `attribution`'s conditionality on the LICENCE is a policy the format
  should NOT know (SPDX ids are an open set). Proposal: the format
  enforces nothing here and the consuming project's own gate does — but
  the FIELD must exist, because a CC BY-SA 4.0 pattern with nowhere to
  put its attribution is a licence breach with a format cause.
- **It carries a block scalar.** `adaptation` and `attribution` are
  prose, so they take `prose-value` — and here the head/body asymmetry
  bites: a block scalar is a HEAD form only (`rxt_format.md:196-203`),
  because a pattern block's lines are not indented. A `provenance` block
  is ITSELF indented continuation, which means it is a head-shaped
  construct living in the body. **This note flags that as the design
  problem in its own proposal and does not resolve it**; §5.1 P-Q1 asks it.
  The alternative, if the asymmetry must hold, is nine flat block-scoped
  lines (`prov-source`, `prov-url`, …) — uglier, no indentation, and it
  keeps the body's one rule intact.

**Worked example** — one real capability-set member, a CRS rule imported
verbatim (family 3, `capability_set_v1.md:180`):

```
pattern (?i)\b(?:d(?:atabas|b_nam)e[^0-9A-Z_a-z]*\(|schema_name\b)
name waf-sqli-keywords
description CRS 942140's database/schema keyword alternation
provenance
  source        crs
  url           https://raw.githubusercontent.com/coreruleset/coreruleset/v4.x/rules/REQUEST-942-APPLICATION-ATTACK-SQLI.conf
  ref           rules/REQUEST-942-APPLICATION-ATTACK-SQLI.conf#942140
  licence       Apache-2.0
  retrieved     2026-09-12
  fidelity      adapted
  adaptation    the ModSecurity `@rx` wrapper and its transformation chain
                dropped; the regex body is byte-identical to the rule's
```

**What pcrec's own harness gets.** pcrec's corpus already carries
imported material whose origin lives only in a file header comment —
`tests/base/d27_*.rxt`'s generator provenance, the `# pcre2-only` marks
whose justification lives in `docs/dev/upstream_issues.md`
(`rxt_format.md:509-513`). A structured `provenance` block gives pcrec's
own imports (the Fowler suite, PCRE2 `testdata`-derived cases) the same
machine-readable origin, and makes "where did this block come from" a
`--list-source` column rather than a grep through comments. It is also
the natural home for the D27 blinded corpora's own authorship statement.

### 2.2 A vocabulary DECLARATION for closed tag keys — needs N-10, N-21, and N-20's closed half

**The gap.** `tag` is the carrier for family, role, hazard class, size
class, convention, regime, method and REQUIRES — eight key families —
and `tag-value` is free vocabulary by design (`format_design.md:337-339`).
A typo is a legal tag. `capability_set_v1.md:521-525` states the closed-set
requirement for REQUIRES in the strongest terms and R5 finding B3 makes
the identical point about this project's own `patterns[].tags`: "a typo
that silently becomes a new tag is a capability claim nobody checked."

**What is NOT being asked.** Not a fixed vocabulary in the format. AR-6
forbids putting engine-shaped enums in the format
(`format_design.md:2047`) and the bench's own vocabularies must stay the
bench's. What is asked is a way for a FILE to declare its own closed sets
and have the parser enforce them.

**Grammar sketch** (W2; head-only; repeatable, one per key):

```ebnf
decl-line = … | "vocabulary" , ws , tag-key , ws , tag-value , { ws , tag-value } ;
```

**Rules.** A `vocabulary <key> <v1> <v2> …` head line declares that
`tag <key>=<value>` may only take a listed value; a `tag` whose key is
declared and whose value is not listed is REFUSED BY NAME, naming the
key, the offending value and the declared set. A key with NO `vocabulary`
line keeps today's free-vocabulary behaviour exactly, so nothing in the
existing corpus changes and the production is purely additive. A
`vocabulary` line for a key no `tag` uses is legal (it is a declaration,
not an assertion) but a `--list-source` consumer can see it and warn.

**Worked example** (the head of the capability set):

```
vocabulary hazard   none exponential-backtracking ambiguous-decomposition \
                    exact-minimum-boundary large-count wide-alternation
vocabulary fidelity verbatim adapted inspired
vocabulary requires backrefs lookaround lookbehind-variable atomic-possessive \
                    recursion conditionals k-reset control-verbs \
                    unicode-properties named-groups free-spacing callouts \
                    span-reporting non-utf8-subject captures true-end-anchor
```

(The continuation shown here as `\` is illustrative only — a
`vocabulary` line is a head declaration, so INDENTATION IS CONTINUATION
already, `rxt_format.md:160-168`, and the real spelling wraps with an
indented second line. Stated because it is the kind of detail an
implementer should not have to guess.)

**Why `requires` should be a `tag` key and not its own production.** It
was tempting to ask for `requires <label> …` as a first-class block line.
Against it: `tag` already accumulates across repeated lines and already
mixes bare labels with pairs (`format_design.md:1846`, the U1 ruling), so
`tag requires=backrefs requires=lookaround` costs nothing new; and a
dedicated production would make the capability model a FORMAT concept,
which is exactly the engine-neutrality line AR-6 draws. With
`vocabulary`, the closed-set discipline is available to every key without
the format knowing what any of them mean.

**What pcrec's own harness gets.** pcrec's corpus has its own closed sets
that live in prose today — `gu`'s four give-up codes are enforced by the
parser, but a file-level convention like `tests/known_fail/`'s membership
rule is not. More directly: `vocabulary` is what makes
`format_design.md`'s own §4.5 mapping SAFE. That table sends
`hazard_class`, `size_class`, `convention` and `role` — four closed
record-schema enums — into free-vocabulary tags. Without a declaration
mechanism, the absorption silently downgrades four validated fields to
unvalidated strings, which is a regression the format should not have to
ship.

### 2.3 A per-config capability declaration — need N-22

**The gap.** W3's `config` body can say what an engine IS
(`testee pcre2/10.46`) and what options it takes (`option k=v`), but not
what it CAN DO. `capability_set_v1.md:532-552` establishes that the
declaration must be PER CONFIG, not per engine: `pcre2-dfa` and
`pcre2-interp` are one library at one version satisfying different tag
sets.

**Grammar sketch** (W3; a `config`-body line; repeatable, accumulating):

```ebnf
config-line = … | "capable" , ws , tag-value , { ws , tag-value } ;
```

**Rules.** Lists the vocabulary values (§2.2) this config SATISFIES.
Repeatable and accumulating, like `tag`. **Absent means NOTHING is
satisfied** — fail-closed, deliberately, so a new adapter cannot claim
capabilities by omission (`capability_set_v1.md:549-552`). Under §2.2's
`vocabulary requires …` declaration the values are checkable, which is
the point: a `capable backrefs` on a config beside a `vocabulary requires`
that does not list `backrefs` is a typo the parser can catch.

**Worked example:**

```
config pcre2-dfa
  testee pcre2/10.46
  option match-mode=dfa
  capable lookaround atomic-possessive recursion conditionals
  capable unicode-properties named-groups free-spacing true-end-anchor
  # NOT capable: captures, k-reset, backrefs, control-verbs
  # (man pcre2matching items 2, 4, 7)

config tre-default
  testee tre/0.8.0
  capable named-groups
```

**This is the proposal this note is least sure of** — see §1.4's own
note. A capability list describes an engine, and a format that carries it
is carrying engine knowledge. The counter-argument is that `config … testee`
ALREADY carries engine knowledge (a version string), and that a reader of
the file who sees a pattern with no result for `tre-default` needs the
reason in the same file. §5.1 P-Q4 puts it to pcrecdev1 as an open choice.

### 2.4 Convention-scoped expectations — need N-35 (the deepest gap)

**The gap.** One pattern, one subject, TWO different correct answers. `a|ab`
against `"ab"` is `0 1` under `perl-leftmost-first` and `0 2` under
`posix-leftmost-longest`. Today a case line is one expected answer, and
`variant` supplies different pattern TEXT for a testee rather than a
different ANSWER for the same text. R-BENCH-5 asked for the convention
TAG and got it designed; it did not ask for the second answer, and without
it the tag cannot be acted on.

**Grammar sketch** (W3; a case-line QUALIFIER, not a new case kind):

```ebnf
block-line = … | "under" , ws , tag-value , ws , case-line ;
case-line  = ( "m" | "n" | "ms" | "ns" | "mc" ) , … ;   (* today's, unchanged *)
```

**Rules.**

- An UNQUALIFIED case line means what it means today: the expectation
  under the file's or block's declared convention (`tag convention=…`),
  which is the canonical one.
- `under <convention> m "<subject>" <start> <end>` states the answer a
  testee tagged with THAT convention is scored against, for the same
  (pattern, subject). A testee whose convention has no `under` line for a
  case falls back to the unqualified line — so a set that declares no
  conventions behaves exactly as today, and the production is additive.
- `<convention>` is a `tag-value`, so §2.2's `vocabulary convention …`
  declaration closes it. The format does not know what
  `posix-leftmost-longest` means, which is the AR-6 line held.
- Two `under` lines for one (convention, subject) pair are REFUSED as a
  duplicate, not last-wins.

**Worked example** (family 11's separator case):

```
pattern a|ab
name sem-alt-order
description the leftmost-first / leftmost-longest separator
tag family=semantics-divergence hazard=none size=tiny role=member
tag convention=perl-leftmost-first
provenance
  source        authored
  licence       n-a
  retrieved     2026-09-12
  fidelity      inspired
  adaptation    written from the leftmost-first vs leftmost-longest rule
                as stated in re2's own Syntax documentation
m "ab" 0 1
under posix-leftmost-longest m "ab" 0 2
```

**Why not `variant`.** `variant tre a|ab` would give TRE the same text and
still score it against `m "ab" 0 1`. Making `variant` carry an answer
would conflate two axes the format deliberately separates: a variant is
about SPELLING (R-BENCH-7), a convention is about SEMANTICS (R-BENCH-5).
`format_design.md:1237-1241` already states the rule that makes this
matter: "a testee's variant is checked against the *canonical*
expectations, which the *canonical* oracle produced." That rule is right
and it is exactly why conventions need their own carrier.

**What pcrec's own harness gets.** Less than the others, honestly —
pcrec is a single-convention engine and `tests/harness/run.sh` has one
oracle. Two things: `tests/assertions/`'s `verify_pcre2.py` differential
exists because several constructs "have no python equivalent at all"
(`rxt_format.md:516-522`), which is the same shape one step smaller — an
`under python …` line would let a divergence be STATED in the corpus
instead of parked behind a `# pcre2-only` mark plus an
`upstream_issues.md` entry. And `docs/testing.md`'s "Oracle exclusions"
list becomes data.

### 2.5 A subject reference with an id and an optional hash — needs N-26, N-27

**The gap.** `@file:"path"` gives a path. This project needs a stable
subject ID (every expectation key, report row and interpreter fact names
one) and an integrity hash (its subject trees are gitignored and
regenerated, so the referenced file is NOT committed and NOT reviewed —
which is precisely the condition under which `format_design.md:1203-1208`
itself says provenance IS required).

**Grammar sketch** (W2, extending `file-subject`):

```ebnf
file-subject = '@file:"' , path-chars , '"' , [ ws , "as" , ws , ident ]
                                            , [ ws , "sha256" , ws , hex64 ] ;
```

**Rules.** `as <id>` names the subject; the id is in a per-file subject
namespace and must be unique there, so a case can be cited as
`(pattern, subject-id)` rather than by line. `sha256 <hex64>` is OPTIONAL
and, when present, is CHECKED by whatever reads the subject: a mismatch
is a refusal naming the path, the expected and the actual digest. Absent
means today's behaviour, unchanged.

**Why optional rather than required.** `format_design.md:1203-1208`'s
argument against a hash is that a committed subject file "sits in the repo
beside the `.rxt` and is covered by the same review and the same history".
That argument is exactly right for pcrec's corpus and exactly wrong for a
generated subject tree. Optional keeps both true: pcrec writes none, this
project writes one on every reference, and neither has to argue.

**Worked example:**

```
m @file:"subjects/http-mixed-004.bin" as http-mixed-004 sha256 3f2a…  1284 1309
n @file:"subjects/http-mixed-005.bin" as http-mixed-005 sha256 91c0…
```

**What pcrec's own harness gets.** A named subject makes a failure line
`file:line: subject http-mixed-004: expected … got …`, which is more
useful than a line number when a corpus is generated and its line numbers
move on every regeneration. pcrec's own generated corpora
(`tests/recursion/gen_corpus.py`, the D27 sets) have exactly that
property.

### 2.6 A scoping rule that keeps a set's config out of pcrec's build — need N-44

**The gap, restated.** D93: a `.rxt` source's composed config WINS over a
command-line flag on the same axis
(`subbench_directory_model.md:441-448`; `rxt_format.md:133-136`). This
project's entire pcrec testee matrix — sixteen configs — is command-line
flags. `format_design.md:2198-2284` §6.2's own worked bench file carries
`config pcrec` with a `pcrec --features all` line and a `use pcrec, pcre2,
re2`. If that file is the corpus, every pcrec testee compiling from it is
silently pinned by the file. The exporter already refuses to write such a
line (`tools/export_rxt.py:34-37` rule 5) precisely for this reason.

**Three candidate resolutions**, in this note's order of preference.

1. **A file declares whether its configs are BUILD directives or TESTEE
   descriptions.** One head line, `configs describe` (default: `build`,
   today's meaning). Under `describe`, `config` blocks are read by
   consumers and IGNORED by `pcrec --source`, which then builds only what
   its command line says. A set file writes `configs describe` once and
   the collision cannot occur.
2. **A `config` carrying a `testee` line is inert for pcrec's own
   build.** No new production: the rule becomes "a config that names a
   foreign testee is a description, not a build config." Cheaper, but it
   leaves `config pcrec` in §6.2's example still winning, which is the
   actual hazard.
3. **The set writes no `config` at all**, as today's exporter does, and
   the testee roster lives somewhere else. This is the status quo and it
   is the hybrid Frank's ruling removed — recorded as the null option.

**What pcrec's own harness gets.** Resolution 1 also answers a question
`--source` has today: a file whose configs are descriptions can be listed,
diffed and reviewed without any risk that reading it changes what a build
does. It makes `--list-source`'s "AS WRITTEN, never resolved" stance
(`rxt_format.md:476-482`) into a property of the FILE rather than only of
the dump.

### 2.7 A pattern spelling that can carry a newline, a NUL or a trailing CR — needs N-2, N-4, N-5

**The gap.** `pattern` is rest-of-line, verbatim, unquoted, unescaped
(`rxt_format.md:210-212`). That is a GOOD rule — it is why this project's
185 patterns export byte-exactly with no escaping layer
(`tools/export_rxt.py:38-61` rule 6) — and it means three byte values
have no representation: `\n` (no continuation), `\0` (silently truncated,
MEASURED M1), and a CR immediately before the line end (silently trimmed,
MEASURED M2).

**What is NOT asked.** Do not change `pattern`. Every existing file and
every existing exporter depends on its verbatim rule.

**Grammar sketch** — a SECOND spelling, distinctly named (W2):

```ebnf
block-line = … | "pattern-esc" , ws , quoted-pattern ;
quoted-pattern = '"' , { subject-char | escape } , '"' ;   (* the SAME seven escapes *)
```

**Rules.** `pattern-esc "…"` starts a block exactly as `pattern` does and
means the same thing; its text is the decoded bytes, using the format's
OWN seven-escape subject vocabulary (`rxt_format.md:374-385`) and no
second vocabulary. A block carries one or the other, never both. Because
the escape table already includes `\n`, `\xHH` and `\\`, all three
unrepresentable cases become expressible with nothing new invented, and
`tests/harness/driver.c`'s existing `decode()` already implements the
decoder (`rxt_format.md:462-464` makes that point about the dump's
escaping).

**Worked example** (family 6's VS Code `number` rule, as authored):

```
pattern-esc "(?x)\n  -?  (?:0 | [1-9]\\d*)\n  (?: \\.\\d+ )?\n  (?: [eE][-+]?\\d+ )?\n"
name code-json-number
description VS Code JSON.tmLanguage's `number` rule, free-spacing, as written
```

**And a refusal, whichever way this goes.** Even if `pattern-esc` is
refused as a feature, **M1's silent truncation should become a refusal**.
A NUL in a `pattern` line today produces a shorter pattern, exit 0, no
diagnostic — a wrong artifact from a valid-looking file. `slurp_lines`
(`rxt_source.c:399-456`) already reads the whole file and knows every
byte; a scan for an embedded NUL before splitting would refuse by name at
no measurable cost. **This note ranks that refusal ABOVE `pattern-esc`
itself**: a missing capability is a known limit, a silent truncation is a
trap.

**What pcrec's own harness gets.** The NUL refusal is unambiguously
pcrec's own win — its corpus is hand-written and a stray NUL from a bad
editor or a botched generator would today produce a passing test of the
wrong pattern. `pattern-esc` is more marginal for pcrec, though
`tests/modifiers/`'s `(?x)` coverage is the one place its corpus has the
same shape as family 6.

### 2.8 `variant_kind`, and a tag value that can hold a sentence — need N-41

**Two small gaps in one place.** `variant`'s designed body carries the
replacement text and an optional `groups <name>=<n>` map
(`format_design.md:419`, `:421-423`). This project carries three more fields:
`variant_kind` (a closed two-value enum, `syntax-only` / `restructured`,
which the reporter is meant to show beside the number), `objective_
preserved` (a reviewed sentence) and `capture_map` (↔ `groups`, fits).
`format_design.md:1887` routes the reviewed sentence to
`tag variant-note=…` — but a `tag-value` may contain **no whitespace**
(`format_design.md:339`), so a sentence does not fit in one.

**Grammar sketch** (W3, extending `variant-body`; and W2 for the second half):

```ebnf
variant-body = "unsupported" , ws , rest-of-line
             | [ "kind" , ws , tag-value , ws ] , rest-of-line ,
               [ eol , "groups" , ws , group-map ] ;

(* and, for prose: *)
tag-item = tag-label | tag-pair | tag-prose ;
tag-prose = tag-key , "=" , quoted-subject ;   (* whitespace allowed inside quotes *)
```

**Rules.** `kind <value>` is optional and closed by §2.2's `vocabulary
kind …`. The quoted `tag-prose` form lets a reviewer's sentence be a tag
value without loosening the bare form's no-whitespace rule; the existing
seven escapes apply inside the quotes, so the vocabulary count stays at
one.

**What pcrec's own harness gets.** `tag-prose` is generally useful the
moment `tag` ships — a one-word tag value is a real constraint for any
descriptive key (`method=`, `question=`, an exclusion reason). The
`variant kind` half is bench-only.

### 2.9 An oracle that can name any engine, at a version — needs N-36, N-38

**The gap.** `oracle-spec = "python" | "pcre2" | "none" , ws ,
rest-of-line` (`format_design.md:363`) is a closed set of two engines. A
capability set's roster is eight, and family 11's POSIX cases want a
POSIX engine as their own oracle. Separately, no production names the
oracle's VERSION, and a cross-engine correctness claim that does not say
"libpcre2 10.46" is not reproducible.

**Grammar sketch** (W3, widening the existing production):

```ebnf
oracle-spec = "none" , ws , rest-of-line
            | engine-ref ;                 (* ident , [ "/" , version-chars ] *)
```

**Rules.** `oracle python` and `oracle pcre2` keep their exact meanings
(they are `engine-ref`s with no version), so nothing in pcrec's corpus
moves. `oracle pcre2/10.46` pins the version. `oracle tre/0.8.0` names an
engine a consumer may not have — which is already handled: R-VG-3's rule
is that "an absent oracle degrades to a labelled skip, never a silent
pass and never a hard failure" (`format_design.md:1221-1223`), and that
rule is what makes widening the enum safe rather than a portability
hazard.

**What pcrec's own harness gets.** A version on the oracle is the fact
`docs/testing.md`'s "Oracle exclusions" list is implicitly about — a
divergence is between pcrec and a SPECIFIC python or libpcre2 build, and
recording which one is what makes the exclusion re-checkable when the
oracle moves.

### 2.10 `mc`'s counting rule, stated — need N-32

**Not a new production — a semantics statement the spec owes.** `mc ,
ws , subject , ws , int` (`format_design.md:417`) is a match COUNT. Its
overlap rule is not stated anywhere this note could find. This project's
driver protocol fixes non-overlapping advancement as
`pos = max(end, pos+1)` (`pcrecbench/adapters.py:19-23`) — the `+1` is
what makes an empty match terminate. Two engines counting under different
rules would both satisfy the same `mc` line, which is R-BENCH-4's
adjudication requirement failing quietly.

**The ask is one paragraph in `rxt_format.md`**, not code: state whether
`mc` counts non-overlapping matches, and if so under which advancement
rule for an empty match. If the intended answer is "the harness's rule,
whatever it is", say that — it is still better than silence, because a
foreign-engine adapter then knows it must match the harness rather than
its own library's default (RE2's `FindAll`, PCRE2's `pcre2_match` loop
and Oniguruma's `onig_scan` do not all agree here).

### 2.11 Regime membership without the subroutine wrapper — need N-48

**The gap, and it is a real defect in a shipped design.**
`format_design.md:1888-1901` §4.5 item 4 resolves regimes by writing the
canonical pattern once as a `name`d definition and one block per regime
whose pattern is `(?&<name>)`. That mechanism **cannot be used by any set
in this repository**: a delivering or plain subroutine call goes through
PCRE2's own group-name grammar, which refuses `-` and `.`, and
`rxt_format.md:284-291` states it outright — "a definition whose name
carries `-` or `.` **cannot be called from a pattern**". Every pattern id
in all five sets here is a hyphenated slug (`cls-upto-1024`, `iso-ts`,
`w-256`, `anc-caret`). The widened name grammar exists precisely so those
ids need no map (`rxt_format.md:290-296`) — and the regime mechanism
needs the narrow grammar. The two rulings are individually right and
jointly unusable.

**Three ways out**, none of which this note picks for pcrecdev1:

1. **`tag regime=` alone, with the subject set attached to the case
   lines rather than to the block.** A block carries all its cases; each
   case is tagged with its regime. Needs a per-CASE scope, which Frank
   ruled against (`format_design.md:1888-1889`: "there is no case scope").
2. **A regime-scoped case group inside one block** — an indented
   `regime <label>` sub-block holding its own case lines. Same head/body
   indentation problem as §2.1.
3. **Let a definition be called by a NAME MAP the format derives**, the
   way `target =` already derives a C prefix by `-`/`.` → `_`
   (`rxt_format.md:107-110`). `(?&cls_upto_1024)` would reach
   `name cls-upto-1024` by the same rule. Cheap, uses machinery that
   already exists, and has one sharp edge: the derivation is deliberately
   NOT injective (`a-b` and `a.b` both give `a_b`, and the spec says the
   refusal is where that is paid for, `:111-119`), so a call would need
   the same collision refusal a duplicate `target` prefix gets.

**This note's observation, not a recommendation:** option 3 costs the
least and reuses a rule the format already defends. But the deeper point
for pcrecdev1 is that §4.5 item 4 should not be treated as settled — it
was measured against `bench/loglines`' eleven patterns, whose ids include
`iso-ts` and `level-context`, and the mechanism it proposes cannot
express either of them.

### 2.12 `--list-source`, extended to the descriptive productions — need N-52

**The gap, and why it matters more than it looks.** `--list-source` is
THE SEAM (`rxt_format.md:418-423`): pcrec owns the head grammar, is its
only implementation, and `tests/harness/run.sh` "gains no head arms at
all". This project relies on the same seam in the export direction today
(`tools/selfcheck.py`'s `check_rxt_export`, [B38]). The dump's sixteen
columns cover W1's head and the pattern block's W1 attributes and NOTHING
ELSE — no `tag`, no `oracle`, no `variant`, no `mc`, no provenance, and
no case lines at all. If W2/W3 land without extending it, a bench-side
loader must grow its own parser for exactly the productions the seam
exists to keep single-implementation. **That is the same hazard one wave
later, and it is the cheapest of the twelve asks to get wrong.**

**Two shapes, and this note prefers the second.**

1. **More columns.** A `tag` row kind and a `variant` row kind in the
   same stream, with the existing sixteen columns plus a few. Keeps one
   table; the column count grows toward thirty and most are empty on most
   rows.
2. **Sections.** `docs/spec/table_contract.md`'s `#section` mechanism
   exists for one command emitting several tables with different columns,
   and `rxt_format.md:484-491` DECLINES it here for a stated reason —
   head/body INTERLEAVING is what a consumer checks, and that is
   expressible only as row order in one stream — while naming the trigger
   that would earn it: "a data block whose rows cannot be columns of this
   table under any reading." A `provenance` block (§2.1) is exactly that:
   nine keyed lines that are not attributes of the `pattern` row. So the
   trigger the spec named is met by this note's own first ask, and
   adopting sections stays free ("a stream with no `#section` line is a
   single anonymous section").

**One thing the extension must not lose.** MEASURED (the observation
after §1.9): `--list-source` accepts a case line containing a REFUSED
`@file:` subject without complaint, because the head parser recognises
`m` as a keyword and reads none of its values. That is correct today and
becomes wrong the moment a consumer treats the dump as a validator for
the whole file. Whatever the extension does, it should say plainly which
productions it VALIDATES and which it merely recognises.

**What pcrec's own harness gets.** The same thing it got the first time:
`run.sh` never grows a parser for a production pcrec already parses. With
W2's `include`, the dump is also the only place the include CLOSURE is
visible without re-implementing resolution — which the format's own
population accounting (`format_design.md:1289-1300`, its §2.11) will need
a reader for.

---

## 3. THE ACCEPTANCE CHECKLIST for the restart

What this project will verify when pcrecdev1 delivers, written so a
reviewer can run it. Forty-one checks in seven groups, each naming the
need it closes, the command, and the pass criterion. **Every check that
GATES something is paired with its negative arm in the same group** —
this repo's own check-design rule, stated at `tools/CLAUDE.md`: "every
gate is exercised against an input it must REJECT in the same run that
exercises it against one it must accept. A check with no failing case
proves nothing." The pairs are C1/C2, C5/C6, C8/C9, B3/B4 and F2/F3,
with C3 as the compatibility control; the checks marked **(existing)**
carry a MEASURED BEFORE instead, which is the same discipline read
backwards — the contrast is against a recorded fact rather than a
planted one.

Notation: `$P` is the pinned binary, `$F` a fixture directory. Fixtures
are small enough to write inline; the ones marked **(existing)** are the
probes §1.9 already ran, reproduced so the delivery is compared against a
measured BEFORE rather than against a remembered one.

### Group A — the productions parse (needs N-9, N-20, N-25, N-32, N-34, N-36, N-37, N-39, N-40, N-50)

| # | check | command | pass |
|---|---|---|---|
| **A1** | every W2/W3 keyword this set needs is ACCEPTED where it was refused | `$P --list-source $F/w2w3.rxt` on a file carrying `tag`, `mc`, `@file:`, `include` at head and block scope | exit 0; **BEFORE (existing, M10): each refused by name with its wave** |
| **A2** | the same for W3 | as A1 with `oracle`, `variant`, `use`, `config … testee`, `config … option` | exit 0; BEFORE as A1 |
| **A3** | an unknown keyword is STILL a hard error naming its context | `$P --list-source $F/bogus.rxt` with a line `taggg family=x` | exit 1, the diagnostic names the CONTEXT (head / config body / pattern block), per `rxt_format.md:154-159` |
| **A4** | a W2 keyword in the WRONG context is still refused | `tag` inside a `config` body | exit 1 naming the context |
| **A5** | `tag` accumulates across repeated lines and mixes bare labels with pairs | two `tag` lines on one block, one bare-label one pair-valued | both sets present in the dump; per `format_design.md:1846` |

### Group B — raw bytes round-trip (needs N-1, N-3, N-4, N-5, N-28)

| # | check | command | pass |
|---|---|---|---|
| **B1** **(existing)** | a high-byte pattern round-trips byte-exactly | `printf 'pattern caf\xe9[\x80-\xff]+\nname h\n'`, dump, decode the `pattern` column with `tools/export_rxt.py`'s `decode_rxt_escape` | bytes equal; **BEFORE: already passes (M3)** — a regression here is a delivery failure |
| **B2** **(existing)** | a mid-line tab, a doubled backslash, a mid-line CR, trailing spaces | as B1 | all byte-exact; BEFORE: passes (M4) |
| **B3** | **a NUL in a pattern line is REFUSED BY NAME** | `printf 'pattern ab\x00cd\nname h\n'` | exit non-zero, the diagnostic naming the file, the line and the NUL. **BEFORE (M1): exit 0 and the pattern silently becomes `ab`.** This is the single highest-value item in the checklist |
| **B4** | the NUL refusal does not fire on a NUL-free file | any existing corpus file | exit 0 — the control that B3 is not refusing everything |
| **B5** | if `pattern-esc` (§2.7) ships: a newline, a NUL and a trailing CR all round-trip | `pattern-esc "a\nb\x00c\r"` decoded against the source bytes | byte-exact |
| **B6** | if `pattern-esc` ships: a block carrying BOTH `pattern` and `pattern-esc` is refused | — | exit 1 naming both lines |
| **B7** | `@file:`'s bytes are taken raw — a subject file containing a NUL and invalid UTF-8 reaches the matcher whole | a 3-byte file `\x00\xff\x41` referenced by `@file:` | the case runs and the engine sees three bytes. `format_design.md:1193-1199` promises this; nothing has ever verified it |

### Group C — refusal by name, and the negative arms (needs N-10, N-21, N-26)

| # | check | command | pass |
|---|---|---|---|
| **C1** | a `tag` value outside a declared `vocabulary` is refused BY NAME | `vocabulary hazard none exponential-backtracking` + `tag hazard=exponentail-backtracking` | exit 1 naming the key, the bad value and the declared set |
| **C2** | the same key with a LISTED value is accepted, same run | — | exit 0. C1's control |
| **C3** | a key with NO `vocabulary` line keeps free-vocabulary behaviour | `tag whatever=anything` | exit 0 — the compatibility control; no existing corpus file may start failing |
| **C4** | a `provenance` block missing a REQUIRED line is refused naming the line | drop `licence` | exit 1 naming `licence` |
| **C5** | `fidelity adapted` with no `adaptation` is refused | — | exit 1 naming the conditional |
| **C6** | `fidelity verbatim` with no `adaptation` is ACCEPTED | — | exit 0. C5's control |
| **C7** | a SECOND `provenance` block in one pattern block is refused | — | exit 1. Not last-wins — the M5 hazard must not be repeated |
| **C8** | `@file:` with a `sha256` that does not match the file is refused naming both digests | — | exit 1 |
| **C9** | `@file:` with a MATCHING `sha256` is accepted | — | exit 0. C8's control |
| **C10** | **a second `description` in one pattern block** | **(existing)** | this note asks for a refusal; if pcrecdev1 keeps last-wins, the check records the CHOICE rather than failing. **BEFORE (M5): silently last-wins, exit 0** |

### Group D — `--list-source` columns (need N-52)

| # | check | command | pass |
|---|---|---|---|
| **D1** | every descriptive production this set writes appears in the dump | `$P --list-source bench/capability/patterns.rxt` | a row or column for each of: `tag`, `provenance`'s nine keys, `oracle`, `variant`, `mc`, `under`, `@file:`'s id and hash |
| **D2** | the dump is re-parseable without a second parser | this project's loader reads ONLY the dump | the loader contains no `.rxt` tokenizer of its own — verified by code review at the restart, and by a grep for the format's keywords in `pcrecbench/` |
| **D3** | the dump's escaping is documented and round-trips | as B1/B2, through every escaped column | byte-exact |
| **D4** | the dump states which productions it VALIDATES vs merely recognises | read the spec section | a sentence exists. **BEFORE: a case line's `@file:` subject passes the dump although `@file:` is refused** (the observation after §1.9) |
| **D5** | if sections (§2.12 shape 2) ship: a stream with no `#section` line still reads as one anonymous section | any existing corpus file | exit 0, output unchanged from the current pin |

### Group E — the set loads and measures (needs N-7, N-27, N-30, N-35, N-45, N-48)

| # | check | command | pass |
|---|---|---|---|
| **E1** | every block name in the set is a legal bench `pattern_id` | `python3 -m pcrecbench run --subbench capability …` refuses in under a second on a bad id | the KB-12 pre-flight (`pcrecbench/subbench.py:80-90`) fires on the `.rxt`-sourced ids exactly as it does on sidecar ones |
| **E2** | the id containment holds both ways for THIS set | a script over the set's names | every name is both a legal `.rxt` block name and a legal slug — i.e. `[a-z0-9-]` only, no `_`, no `.`, no uppercase (§1.9 M11) |
| **E3** | a subject is addressable by ID, not by line | insert a blank line above a case and re-run | every expectation key and every report row is unchanged |
| **E4** | a duplicate block name is refused | **(existing, M7)** | exit 1. BEFORE: already passes; a regression is a delivery failure |
| **E5** | an `under <convention>` case reaches the harness as a SECOND expectation for the same (pattern, subject) | a two-testee cell, one per convention | both are scored `matched-as-expected`. **This check cannot pass on the format alone** — R5 finding B1 establishes that `harness.outcome_for()` has no convention parameter, so a matching harness change is owed on THIS side and is named in §4 |
| **E6** | `make check-harness`'s generic per-set gates pass on an `.rxt`-sourced set | `make check-harness` | the manifest, `gen_*.py --check`, expectations re-derivation and floor-pattern smoke all enumerate the new set (`tools/CLAUDE.md`'s `subbench_dirs()`) |
| **E7** | the set's `content_hash` covers the `.rxt`, every `include`d fragment and every `@file:` subject | `Subbench.content_hash()` (`subbench.py:287-311`) | a one-byte edit to any of the three moves the hash |

### Group F — D93 and engine neutrality (needs N-43, N-44)

| # | check | command | pass |
|---|---|---|---|
| **F1** | a `target`-less, `config`-less set file parses and is a PERMANENT legal shape | **(existing, M12)**, plus the spec sentence | exit 0 AND a sentence in `rxt_format.md` saying so. The parse already works; the CONTRACT is the ask |
| **F2** | whatever scoping rule ships (§2.6), a `config` in the set cannot change what a pcrec testee compiles | compile one pattern from the set with `--engine=vm` on the command line while the file declares `engine` in a config | the command line wins, or the file is refused — **either is acceptable, silence is not** |
| **F3** | the negative arm: planting a build directive in the set file FAILS this project's own gate | `capability_set_v1.md:1075`'s "no build directives" gate, restated per R5 finding B5 / consolidated CS8 as "no `target`/`config`-kind ROW, and every `pattern`-kind row's flags/features/encoding/engine/budget columns EMPTY" | a planted `engine vm` line makes `make check` fail by name |
| **F4** | the set carries no pcrec-oracled limits file and no pcrec-shaped expectation | review | R-BENCH-4 / AR-6; Frank's [B31] clearance already set this precedent |

### Group G — the format's own regressions (all needs)

| # | check | command | pass |
|---|---|---|---|
| **G1** | every existing `.rxt` file in pcrec's corpus parses identically | pcrec's own `make test` | green. R-COMPAT-1 |
| **G2** | this repo's five committed exports still round-trip | `make check-harness`'s `check_rxt_export` ([B38]) | 185/185 patterns match `--list-source` |
| **G3** | the thirteen MEASURED facts of §1.9 are re-run at the delivered pin | `python3 docs/dev/measurements/probe_rxt_format.py`, diffed against the committed archive | **M1 MUST change** (check B3, the NUL refusal — the one item this note ranks first). **M10 changes by design** (the W2/W3 keywords stop being refused). **M5 changes only if the C10 ask is accepted**, and the check records which. M2-M4, M6-M9 and M11-M13 must be UNCHANGED; any other movement is a finding |

**How this checklist will be run.** As a lane, at the restart, against a
pcrecdev1-delivered pin, before any pattern of the capability set is
authored — the same order [B39]'s prep lane used (predict, then confirm
at the build). The fixtures are cheap: `--list-source` is parse-only,
measured at ~2 ms for a 95-pattern file and under 0.2 s for all five sets
including python startup (`tools/CLAUDE.md`, [B38]), so the whole group
fits inside `make check-harness` rather than needing its own target.

---

## 4. Sequencing — what blocks the first sample, what can land later

### 4.1 The minimal W2/W3 subset that unblocks a FIRST SAMPLE

A first sample is: sixty patterns × six pinned testees × two regimes,
measured into `store/`, reported and read. To reach it, a set must be able
to state its patterns, its subjects, its expectations and its identity.
Nothing else is load-bearing on night one.

**Tier 1 — required for a first sample** (ten needs, six rows):

| need | production | why it cannot wait |
|---|---|---|
| N-9, N-45, N-48 | `tag` (W2) | the set's id, version, regimes and every per-pattern classification. The record cannot be built without `hazard_class`/`size_class` — both are REQUIRED fields (`schema/record.schema.json:298`) |
| N-25, N-27 | `@file:` (W2) + a subject id (§2.5) | 1 MB throughput subjects cannot be inline strings, and every expectation key names a subject id |
| N-32 | `mc` (W2) + its counting rule (§2.10) | the throughput regime's comparable |
| N-36, N-37 | `oracle` (W3) + `tag method=` (W2) | R-BENCH-1's verification method; without it an expectation is unattributed |
| N-43 | the permanence sentence (§2.6 / F1) | the whole file layout rests on it, and it is a sentence, not a feature |
| N-52 | a `--list-source` that emits the above | otherwise this project writes the second parser the seam exists to prevent |

**Tier 2 — required before the set makes its stated CLAIMS, not before
it first runs** (nineteen needs, six rows):

| need | production | what is missing without it |
|---|---|---|
| N-11..N-19 | `provenance` (§2.1) | charter requirement (1). The set can measure without it; it cannot CLAIM wild provenance |
| N-20, N-21 | `tag requires=` + `vocabulary` (§2.2) | the capability model. Without it, an engine that cannot run a pattern produces a refusal rather than a declared `unsupported` |
| N-39, N-40, N-41 | `variant` (W3) | charter's syntactic-adjustment clause. Not needed while the roster is pcre2 + pcrec, which run every pattern canonically — this is why the first sample can precede it |
| N-22, N-23 | `capable` (§2.3) | the pre-compile policy |
| N-10 | `vocabulary` on `hazard` | §6.3's rewrite rule keys on it |
| N-34, N-35 | `under <convention>` (§2.4) | family 11. **Also blocked on a harness change on THIS side** (R5 B1) |

**Tier 3 — genuinely later** (N-2/N-4/N-5 pattern escaping, N-26's hash,
N-38's oracle version, N-50's `include`, N-33's neutral capture map,
N-6, N-47, N-49, N-31).

**The one Tier-3 item this note asks for out of order: the NUL
refusal (§2.7's second half, check B3).** It is not a capability, it is
the removal of a silent-wrong-answer path, and it is independent of every
wave.

### 4.2 Why the first sample cannot simply be Tier 1

A candid statement, because the tiering above could read as optimism:
**Tier 1 is `tag` + `@file:` + `mc` + `oracle` + `--list-source` — that
is most of W2 and part of W3.** There is no smaller cut that produces a
measurable set, because the four things a sub-bench is made of (patterns,
subjects, expectations, identity) map onto exactly those productions.
What the tiering buys is a smaller FIRST delivery, not a small one.

If pcrecdev1 wants a still smaller first delivery, the honest minimum is
**W2 alone** — `tag`, `@file:`, `mc`, `include`, and the `--list-source`
extension for them. With W2 and no W3, a set can be authored, loaded,
measured and reported against the two pcre2 testees and the sixteen pcrec
ones, with its oracle declared in prose and its variants absent (the
current roster runs every pattern canonically, so no variant is needed).
That is a real, publishable first sample with two stated gaps: no
per-pattern provenance and no declared capability model. §5.1 P-Q6 asks
whether that is the shape pcrecdev1 prefers.

### 4.3 What this project does in the interim

**Nothing is built under `bench/`.** Frank's ruling parks the effort; the
plan row already states "Nothing measured, nothing under bench/ touched
until (e)". Concretely, between this note and the restart:

- No `bench/capability/` directory, no patterns, no subjects, no sidecar.
- No loader change in `pcrecbench/subbench.py`, no `source_format = "rxt"`
  key, no schema change.
- `tools/export_rxt.py` and its `make check-harness` round-trip are
  UNTOUCHED — the five existing sets keep their derived exports, which is
  orthogonal to this ask.

Three things this project CAN do without the format, and which the R5
panel's findings make it want to:

1. **The convention-scoring harness change** (R5 B1). `under` in the
   format is useless if `harness.outcome_for()` still grades every testee
   against one expectation. This side's half is a per-testee/variant
   expected-answer override, and it is ours to design whether or not the
   format ships §2.4.
2. **`variant.kind` rendering** (R5 B2) — claimed built, never
   implemented, and needed the moment a variant exists.
3. **The wild-vs-designed bucketing decision** (R5 B3) — whether
   provenance becomes a real enumerated record field or stays set-local.
   §2.1's `provenance` block answers where it lives in the SET; it does
   not answer what the RECORD carries, and the two questions are
   separable.

None of the three touches `bench/`, all three are on the critical path at
the restart, and all three are this project's own work. They are named
here so the parked period is not idle; sequencing them is the manager's
call, not this note's.

---

## 5. Open questions

### 5.1 For pcrecdev1 (design choices that are theirs)

**P-Q1 — The head/body indentation asymmetry, against `provenance` and
regime grouping.** `rxt_format.md:169-173` calls the asymmetry
deliberate and "the only one": head lines take indented continuation, a
pattern block's lines do not. Both §2.1's `provenance` block and §2.11's
option 2 want an indented sub-block IN THE BODY. Three answers are
available — relax the asymmetry for a named set of body sub-blocks; keep
it and make provenance nine flat block-scoped lines; or move provenance
to the head keyed by block name (which splits a pattern's truth across
two places and this note recommends against). **This is the single
biggest shape decision in the note and it is entirely pcrecdev1's.**

**P-Q2 — Is `vocabulary` (§2.2) the right mechanism for closed sets, or
does the format prefer to keep every tag free and leave validation to
consumers?** The cost of the latter: `format_design.md` §4.5's own
absorption table silently downgrades four validated record-schema enums
to unvalidated strings.

**P-Q3 — Does `mc` count non-overlapping matches, and under which
advancement rule for an empty match?** (§2.10.) A one-paragraph answer,
and the only one of the twelve that may need no code.

**P-Q4 — Should per-config CAPABILITY declarations (§2.3) live in the
format at all, or is that engine knowledge the bench should keep?** A
legitimate "no" leaves this project with one non-`.rxt` file, which is a
partial return of the hybrid Frank's ruling removed — so the answer
should be explicit rather than defaulted.

**P-Q5 — §4.5 item 4's regime mechanism is unusable for this project's
pattern ids** (§2.11, `rxt_format.md:284-291` against `:290-296`). What
replaces it? The note sketches three options and picks none.

**P-Q6 — Would pcrecdev1 prefer a W2-only first delivery** (§4.2), with
provenance, capability and variants following in a second? This project
can run a real first sample on W2 alone, with two stated gaps.

**P-Q7 — Is the NUL refusal (§2.7, check B3) acceptable as a standalone
change**, independent of any wave? It is a silent-truncation fix, not a
feature, and it is the item this note would take first if it could take
only one.

**P-Q8 — `@file:`'s optional `sha256` (§2.5) against
`format_design.md:1203-1208`'s explicit "no content hash on a subject
reference".** That ruling's premise — a subject file is committed and
reviewed — does not hold for a generated, gitignored subject tree. Does
pcrecdev1 read the ruling as a principle or as a default?

**P-Q9 — Two hazards this note found in SHIPPED behaviour, both silent:**
a second `description` in a block overwrites the first (M5), and a NUL
truncates a pattern line (M1). Both are outside this note's ask and both
are the kind of thing a corpus author would rather hear about now.

### 5.2 For Frank

**F-Q1 — The sequencing question §4.2 exposes.** Tier 1 is most of W2
plus part of W3. If pcrecdev1's W2 lands and W3 does not, the capability
set can take a real first sample with no per-pattern provenance and no
declared capability model — i.e. **charter requirement (1) and the
capability clause both unmet at the first sample**, with everything else
met. Is that an acceptable first sample, or does the set wait for both
waves? This note does not recommend; the charter is Frank's.

**F-Q2 — The `.rxt` format cannot express a multi-line `(?x)` pattern at
all** (N-2, roadblock #1), and `capability_set_v1.md:1089-1100` already
proposed flattening such a pattern to one line as `fidelity: adapted`
with an oracle check. Under Frank's 2026-09-12 ruling, is flattening an acceptable
accommodation — or is this a capability the format must gain before the
set's family 6 is authored? The difference is one pattern family's
fidelity against one format production.

**F-Q3 — This note is written for Option A** (the set's truth lives in
`.rxt`) per Frank's 2026-09-12 ruling, which supersedes both N3 §6's
recommendation and `capability_set_v1.md` §9.1's adoption of Option B.
**Those two documents are now stale on their central recommendation**,
and this note edits neither — it is feedback, not a revision. The
consolidated R5 panel already plans the repair
(`docs/dev/reviews/2026-09-12-r5-capability-set-v1.md`, the manager's
ratification: Q10-Q12 SUPERSEDED, "§9 becomes a pointer to
`rxt_needs_v1.md` plus the restart acceptance checklist… the revision
lane opens once `rxt_needs_v1.md` is merged so the two agree"). So F-Q3
is not really a question for Frank at all — it is a sequencing fact, and
it is recorded here only so a reader of THIS file is not misled by the
stale §9 while both documents stand.

---

## Appendix — the roadblocks, in one list

The six places the effort PARKS, in the order Frank's ruling would have
it read them:

| # | roadblock | need(s) | §  |
|---|---|---|---|
| 1 | a multi-line `(?x)` pattern has NO representation | N-2 | §1.1 |
| 2 | `tag` is refused, so no per-pattern classification is expressible — and when it lands, no closed vocabulary can be declared | N-9, N-10, N-20, N-21 | §1.2, §1.4 |
| 3 | no pattern-level PROVENANCE production exists in any wave | N-11..N-19 | §1.3 |
| 4 | `@file:` gives a subject a PATH and no stable ID, and the format's answer is `file:line` — which moves on every regeneration | N-27 | §1.5 |
| 5 | a second correct answer under another convention has no carrier — and the harness could not score one either (R5 B1) | N-34, N-35 | §1.6 |
| 6 | D93 vs a set file carrying a testee roster: `format_design.md` §6.2's own worked bench file would pin this project's testee matrix from inside the set | N-42, N-44 | §1.7 |

And two silent-loss defects found in shipped behaviour, outside the ask:
a NUL truncates a pattern line (M1), a second `description` overwrites the
first (M5).
