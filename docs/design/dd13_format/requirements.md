# [DD-13a] Requirements note — the unified pattern-source/test file format

**Status: DRAFT, requirements-only.** This note enumerates what every named
consumer of the future format NEEDS, evidenced against real corpora and
ratified design/decision text. It does not propose grammar, syntax, or field
names — see the "Observations for [DD-13b]" appendix at the end for the few
places a requirement's shape got close enough to design that it had to be
quarantined rather than dropped. [DD-13b] designs from this note plus
`frank_inputs.md`; [DD-13c] panels the design, not this note.

Every claim below is either an ID'd requirement (cites the source that
compels it) or a data point from a survey command run against this worktree
on 2026-08-17 (commands reproducible; counts given verbatim, not rounded).

---

## 1. The `.rxt` harness/corpus (today's format, as-is)

Evidence: `docs/testing.md` in full; a direct survey of every `*.rxt` file
under `tests/` in this worktree.

**Corpus census** (54 files, `find tests -name '*.rxt' | wc -l`):

| directive | count | notes |
|---|---|---|
| `pattern` | 1,100 | one block each |
| `m` | 4,644 | match, startpos 0 |
| `n` | 2,755 | no-match, startpos 0 |
| `ms` | 40 | match at explicit startpos |
| `ns` | 24 | no-match at explicit startpos |
| `g` | 2,266 | live per-group capture expectation ([M4.5a]) |
| `gp` | 173 | pending-VM per-group expectation ([M4.5a]) |
| `perr` | 75 | compile-must-fail blocks |
| `flags i` | 25 | block-scoped caseless |
| `features <list>` | 100 | 54 `classes`, 40 `modifiers`, 6 `none` (explicit) |

Total expectation lines: 4,644+2,755+40+24+2,266+173+75 = **9,977** — this is
the "~10k-case corpus" the [DD-13] plan row and `frank_inputs.md` refer to;
confirmed by direct count, not restated from memory.

Per-directory breakdown (files / pattern blocks): `tests/base/` 38/759,
`tests/captures/` 5/95, `tests/classes/` 1/54, `tests/modifiers/` 6/54,
`tests/possessify/` 1/76, `tests/rungselect/` 1/29, `tests/counterk/` 1/32,
`tests/known_fail/` 1/1. `tests/base/` alone is 69% of all pattern blocks —
the corpus is heavily concentrated in one directory with per-sub-feature
files inside it (`docs/dev/known_issues.md`-linked regression files like
`k18_arm_order.rxt`, `k18_split_shapes.rxt` sit beside feature files like
`quantifiers.rxt`, `anchors.rxt`).

**R-RXT-1 (line-oriented, flat, block-scoped state):** a `pattern` line
starts a block; `flags`/`features` apply to that block only and do not carry
forward (`docs/testing.md` "The `.rxt` format"). Any successor format must
preserve — or explicitly supersede with a stated migration path — this
non-carrying-state discipline, because 1,100 existing blocks assume it.

**R-RXT-2 (whole-line comments only, no trailing comments):** `#` is a
comment only as the first character of a line; PCRE patterns and subjects
routinely contain `#`, and `docs/testing.md` records this was "found the
hard way by the R22 D27 author" — a real authoring mistake, not a
theoretical one. A successor format must not silently reintroduce
trailing-comment ambiguity.

**R-RXT-3 (self-contained escape vocabulary):** subjects use a small,
closed escape set (`\" \\ \n \t \r \f \v \xHH`, table in `docs/testing.md`)
decoded byte-exactly by `tests/harness/driver.c`, which explicitly never
uses `strlen()` on the decoded result because decoded bytes may include
`\0`. Any successor subject representation must preserve exact-byte
fidelity including embedded NULs.

**R-RXT-4 (compile-then-match two-phase model):** every block is a `perr`
XOR a sequence of `m`/`n`/`ms`/`ns` (+ optional `g`/`gp`) cases against one
compiled artifact — compile failure fails every attached case, "the block
never got far enough to check anything is not a reason to call a pending
case's non-result a pass" (`docs/testing.md`, capture-expectations section).
This all-or-nothing accounting rule is load-bearing and must survive.

**R-RXT-5 (population accounting is a first-class design concern):** three
independent accounting rules already exist and must not silently regress:
(a) an out-of-range `g` is a hard FAILURE, never a skip; (b) an out-of-range
`gp` is counted in a separate, always-visible "pending-vm" bucket, neither
pass nor fail; (c) `gp` self-activates (becomes exactly a `g` check) the
moment the artifact's capability grows to cover it, with zero corpus edit.
This is the model that let a ~10k-case corpus be authored once against
patterns' TRUE semantics and grow live as the VM emitter landed — a
successor format's expectation model needs an equivalent no-value-hidden,
no-count-silently-shrinks discipline for however it represents
"beyond today's capability."

**R-RXT-6 (features/flags are validated, not passed through blind):** an
unknown `flags` letter or `features` module name is a hard harness error,
never a silent no-op — "a dropped flag would compile a different automaton
and the block's expectations would then be verified against something
nobody asked for" (`docs/testing.md`). Whatever config surface the new
format has, invalid config must fail loudly at the point it is read, not
downstream as a mismatched expectation.

**R-RXT-7 (oracle-exclusion is declared per-block, not silently skipped):**
`# pcre2-only` immediately before a `pattern` line tells `verify_rxt.py` to
skip that block and count the skip (14 files in this worktree use it: `grep
-rl "# pcre2-only"`); `docs/testing.md`'s R1 section requires every such
exclusion to have a corresponding `docs/dev/upstream_issues.md` entry. The
new format needs an equivalent per-case (or finer) oracle-applicability
declaration that is visible in the summary, not silent.

**R-RXT-8 (three-valued match outcome, not boolean):** since [K21-class],
`rx_search`'s result is match / no-match / give-up (`RX_ERR_STEPS`/
`RX_ERR_FRAMES`, soon `RX_ERR_WORK` per D47), and the driver's exit-code
protocol (0/`nomatch`, 0/`match`, 3/`steps`|`frames`) treats a give-up as
its own hard harness-level failure category, never compared against a
match/no-match expectation. A format serving VM-forcing bench-style cases
(`--engine=vm`, explicit step/work/frame budgets — `docs/testing.md`'s usage
note on this) needs to be able to express "this case may legitimately give
up" as a distinct expected outcome from both match and no-match, since
today's corpus structurally never reaches this path (nothing in the
directive vocabulary selects `--engine=vm` or a tiny budget) and pcrec-bench
sets will (§5 below, hazard classes).

**R-RXT-9 (per-file harness-level failure modes are already distinct from
case failures):** `run.sh` already separates "pattern failed to compile"
(counted once per pattern, however many cases it had), "harness-level
failure" (compiler/driver mismatch), from ordinary case failures — three
distinct failure taxonomies. A successor format inherits the same
obligation: config/parse errors, compile errors, and expectation mismatches
must stay separately attributable, not collapsed into one failure count.

---

## 2. [V-E] manifest + finder + compilation units

Evidence: `docs/dev/plan.md` [V-E] row (lines ~374-432), D39 + addendum, D38
Q7, D20.

**R-VE-1 (N named patterns → one or more emitted units):** the manifest is a
COMPILATION SOURCE — `docs/dev/plan.md`: "N named patterns → one emitted
unit, perhaps several." The format must be able to name a compilation-unit
boundary per pattern or group of patterns, not assume one-file-in →
one-file-out.

**R-VE-2 (named entry points, no forced dispatch):** "per-pattern named
entry points exactly as today (a statically-known caller pays no dispatch —
D20's rule holds)." This is a hard invariant carried in from D20: the
generator/finder split means a single-pattern single-option request must
emit byte-for-byte today's output, and dispatch resolves once per call and
never reaches the hot loop. The format must not force per-call
indirection onto the common case of "compile one named pattern."

**R-VE-3 (content-addressed shared-data dedup):** "SHARED DATA
deduplicated by CONTENT... share by content hash, so sharing is only ever
dedup of identical bytes and never forces a pattern's specialized table
into a common shape." This is a codegen/backend property more than a file
format one, but it constrains the format insofar as the format must expose
enough about each named pattern (not just its final table) for content
hashing to work at the right granularity — noted as a requirement ON the
format's information content, not on its syntax.

**R-VE-4 (source-level vs link-level composition, kept distinct):** two
composition tiers named in the plan row: SOURCE-LEVEL (manifest references,
AST-inlined at compile time, zero runtime cost, DFA compilability
preserved — the default) and LINK-LEVEL ([M4-CALLOUTS]'s aligned ABI, for
separately-compiled parts and non-regex predicates). The format must
represent BOTH but must never let them look like the same thing — an
inlined reference and a callout reference have different compile-time and
runtime costs, and D39.2's appended-numbering rule applies only to the
source-level tier.

**R-VE-5 (appended group numbering across references, D39.2):**
"rx-reference group numbering is APPENDED — the primary keeps its own 1..N
stable; each inserted regex's groups append at N+1.. in insertion order;
names are kept... Backrefs inside an inserted regex renumber to their
appended positions at insert time (compile-time)." The format's reference
mechanism must preserve enough structure (which regex was inserted where,
in what order) for a compiler to compute this appended numbering
deterministically and reproducibly — re-ordering an unrelated part of the
file must not silently renumber an unrelated pattern's captures.

**R-VE-6 (labeled references, D39 addendum):** the collision policy is
RULED toward caller-supplied labels per insertion site (`"a:reg1"`,
`"b:reg1"` for the same regex inserted twice), composed into a path for
nested insertions (`"c:a"`). The exported index gains a `ref` column, born
at the M4 freeze with NULL/empty for the primary's own groups. **Still open
(carried to OD-ledger below, §6):** path spelling/separator, whether the
label is mandatory or optional-with-default for a single insertion, and
name-alone-vs-ref+name lookup semantics. The format must have a place for
an optional reference label at each insertion site; the label's exact
syntax is [DD-13b]'s to design.

**R-VE-7 (reference cycles rejected cleanly):** "Reference CYCLES are
rejected with a clean diagnostic (true recursion is non-regular; a future
VM-side module's business, never inlining's)." The format's reference graph
must be staticaly analyzable for cycles before or during compilation — it
cannot rely on runtime detection.

**R-VE-8 (PCRE2-desugar vs own-spelling for subroutine calls — OD-5,
inherited):** whether cross-references surface as `(?(DEFINE))`/`(?&name)`
desugar (composed pattern stays valid PCRE2, subroutine-call semantics are
ATOMIC and shift capture numbering) or pcrec's own reference spelling
(plain inlining semantics, beyond-PCRE2) is explicitly UNRESOLVED — "Q2/
K4-tier, measured never read." Carried to the OD ledger (§6, OD-5).

**R-VE-9 (usage-mode duality: CLI args AND manifest file):** "CLI
multi-pattern args with per-pattern names, and a manifest file for build
integration" are named as two usage modes to design BEFORE building. The
format's design must consider both a file-based and a command-line-args
expression of "named patterns," even though only the file form is [DD-13]'s
literal deliverable — the two should not require contradictory semantics
for the same underlying concept (a name bound to a pattern).

**R-VE-10 (manifest is a first-class user surface, not a build artifact):**
Frank, 2026-08-13: "design the manifest as a first-class user surface, not
a build artifact" — this bears on ergonomics/reviewability expectations more
than on any single testable requirement, but it rules out treating the
format as machine-only output that humans never read or hand-write.

**R-VE-11 (template field, D38 Q7):** "V-E's manifest gains a template
field when designed" — this is [M4-SUBST]'s own stated dependency on this
format; expanded in §7 below.

---

## 3. [V-F] the source-scan transformer (target format)

Evidence: `docs/dev/plan.md` [V-F] row (lines ~433-444).

**R-VF-1 ([V-E]'s output format is the natural target):** V-F rewrites C
source markers (`auto regex = rx/abc|def/`-shaped) into references into a
pcrec-compiled companion unit, and the plan row states "[V-E]'s output
format is the natural target." V-F is not a separate format consumer in its
own right — it is a PRODUCER that emits into whatever [V-E]'s manifest
format becomes. No independent requirement beyond R-VE-1..11 above; noted
here only so the DD-13 design doesn't have to re-derive this pointer.

**R-VF-2 (regularity of what V-F emits):** V-F's own constraint (the marker
grammar must be REGULAR, found by the tool being sold) is a constraint on
V-F's INPUT scanner, not on DD-13's format — flagged explicitly as
out-of-scope for this note. V-F is unstarted and has no marker-grammar
design note yet, so there is no further evidence to survey.

---

## 4. [V-G] user-facing regex testing

Evidence: `docs/dev/plan.md` [V-G] row (lines ~445-459+), `docs/testing.md`
in full (V-G is explicitly "the project's own dev testing machinery,
exposed").

**R-VG-1 (the .rxt harness IS the packaging target):** "the machinery
exists and is battle-proven (docs/testing.md); the work is packaging,
scope... and docs." Every requirement in §1 (R-RXT-1..9) is therefore also
a V-G requirement — V-G does not want a different testing model, it wants
today's model made available to a `pcrec test`-shaped user surface, with a
scoping decision (which harness features are dev-only vs user-grade) left
open. No format requirement beyond §1's, but §1 must be read as binding on
V-G too.

**R-VG-2 (bottom-up subpart testing, AMENDED 2026-08-13):** "rides [V-E]'s
named definitions — every named part of a manifest is independently
compilable, so subpart testing is the .rxt harness pointed at each
definition, per-part expectations in the same [manifest]." This is the
requirement that directly forces §1 and §2 to be THE SAME format rather
than two formats that happen to interoperate: a named pattern inside a
manifest needs to carry its own test cases, co-located, and be
independently runnable through the harness. This is also where the
interface-vs-reference-only tension (§6, OD-4) originates — see §5 of
`frank_inputs.md`, restated in the OD ledger below.

**R-VG-3 (oracle differentials are optional, not mandatory):** "optionally
cross-check against the oracles" (python-re / libpcre2, where installed) —
mirrors `docs/testing.md`'s existing loud-skip discipline for `PC-3`
(dlopens libpcre2, skips with named `SKIP:` lines and exit 0 if absent).
Whatever verification-method field the format carries (also required by §5
below for bench) must degrade the same way: absence of an oracle is a
labeled skip, never a silent pass or a hard failure for a stranger's clone.

---

## 5. pcrec-bench set requirements

Evidence: `/home/duxevents/pcrec-bench/APPROACH.md` in full (esp. §2-3,
§5, §8), `docs/design/dd13_format/frank_inputs.md` points 1-4.

**R-BENCH-1 (per-case tags, §3):** every case needs feature-tier tags (base
/ captures / backrefs / lookaround / unicode / ...), a HAZARD CLASS (none /
exponential-backtracking / ambiguous-decomposition / ...; pcrec's own K23
class is explicitly named as a target hazard), a size class, and the
expectation's VERIFICATION METHOD (which oracle, or a derived law — §5 of
APPROACH.md names "derived-law-plus-induction" as a real, already-used
method: "the K23-region method: prove a closed-form law by exhaustive
small-N induction, generate expectations from the law, re-verify
independently" — this is not hypothetical, it is the method
`docs/design/k23_impl/CLAUDE.md`'s design note actually used). The format
needs a place to carry: a set of tier tags, a hazard-class tag, a size
class, and a verification-method tag PER CASE (not per file — APPROACH.md
§5 is explicit that expectations can legitimately be verified by different
methods within one hazard band).

**R-BENCH-2 (engine/config sections — the (engine, version,
build-configuration) triple, §2.4/§4):** "A testee is an (engine, version,
build-configuration) triple — pcrec itself will appear as several testees
(scalar vs simd, DFA vs VM vs auto, captures on/off)." The format needs a
section concept that can be keyed per-testee, holding at minimum: which
files/fragments to include, and which options to apply, for THAT testee —
this is `frank_inputs.md` point 2's "ONE pattern reference... per-library
APPLICATION block" mechanism, independently corroborated by the bench
charter's own architecture sketch.

**R-BENCH-3 (adapters may legitimately refuse a case, §3):** "Adapters are
allowed to say 'unsupported' per case — a first-class result, never an
error... exactly pcrec's 'requires module X' philosophy." The verification/
expectation model must have a first-class "not applicable to this testee"
outcome distinct from "wrong answer," mirroring R-VG-3's oracle-absence
handling and R-RXT-7's `# pcre2-only` skip-with-count discipline — three
independent consumers converging on the same shape (declared
inapplicability, counted, never silent).

**R-BENCH-4 (correctness gates the scoreboard, §5):** "A testee's timing on
a case it got WRONG is excluded from rankings by default." This is a
comparator-side requirement, not directly a file-format one, but it depends
on the format being able to express, per case, an expectation strong enough
to adjudicate correctness independent of which testee is asked — i.e. the
expectation representation cannot be pcrec-specific (e.g. `RX_NCAPS`-shaped)
if RE2/Oniguruma/etc. must also be checked against it.

**R-BENCH-5 (POSIX leftmost-longest vs Perl leftmost-first tagging, §5):**
"Where engines LEGITIMATELY disagree..., the case is tagged with which
convention its expectation follows." A per-case (not per-file) MATCHING
CONVENTION tag is required — TRE (POSIX) is on the candidate roster (§4)
specifically with "different semantics, admitted with its semantics
tagged."

**R-BENCH-6 (exemplar/corpus-file references, `frank_inputs.md` +
APPROACH.md §3):** "large subjects/corpora live in external files,
referenced rather than inlined" (Frank, row creation) and independently,
APPROACH.md §3's test-set component description assumes corpora can be
large ("a larger test set than normal... big subjects"). The format needs
subject-by-reference, not only subject-by-inline-string as `.rxt` has today
(R-RXT-3's inline quoted-string model does not scale to "big subjects").

**R-BENCH-7 (declared per-library pattern tweaks, `frank_inputs.md` point
3):** "it may be fair to tweak a pattern application for a library" — but
the tweak must be DECLARED and visible in the application block, never a
silent fork, or "single pattern reference" stops being true. This is a
requirement on the format's visibility, not its syntax: wherever an
engine-specific variant of a shared pattern is expressed, the format must
make that variance impossible to miss when reading the file (carried to OD
ledger, OD-2).

**R-BENCH-8 (import from pcrec's own oracle-verified corpora, §3):** "Grows
partly by import from pcrec's oracle-verified .rxt corpora (including the
D27 blinded sets)." This is direct evidence for the compatibility question
in §9 below — pcrec-bench's own charter assumes `.rxt` content is
importable, which constrains how much semantic distance the new format may
put between itself and today's `.rxt`.

**R-BENCH-9 (config-section reuse across bench-testee and build-variant,
`frank_inputs.md` point 4):** "the SAME sectioning serves NON-bench use:
multiple compiled configurations. One source file, several configuration
sections — e.g. an AVX2 build AND a baseline build... makes a
'configuration section' the SAME kind of thing as a bench testee — pcrec-
bench APPROACH.md §2.4's (engine, version, build-config) triple — one
concept, two uses." This means R-BENCH-2's section concept is NOT
bench-specific in the format — it must be general enough to describe
"compile this named pattern under this configuration" for pcrec's own
non-bench multi-config builds too. Convergence explicitly named by Frank as
"worth preserving."

---

## 6. Machine generation (the D27 corpora, as evidence of what a generator needs)

Evidence: `tests/base/CLAUDE.md`, `tests/base/d27_*.rxt` file headers,
direct read of `tests/base/d27_nesting.rxt`.

**Census:** six live D27 quantifier-corpus files under `tests/base/`
(`d27_bodies.rxt`, `d27_edge.rxt`, `d27_forms.rxt`, `d27_nesting.rxt`,
`d27_captures.rxt`, `d27_large_counts.rxt` — 219+213+139+187+124+74 = 956
lines) plus one sibling in `tests/known_fail/`
(`d27_nested_min_boundary.rxt`, 9 lines, the K23 regression). Per
`tests/base/CLAUDE.md`: "81 blocks / 676 live case-lines written from the
PCRE promise by an author denied `src/` and `tests/`, every expectation
computed from python `re` and independently re-verified by a from-scratch
checker."

`d27_nesting.rxt`'s actual header (verbatim, read directly):
```
# NESTING: quantified groups containing quantified subexpressions, two and
# three levels deep, mixed greedy/lazy, bounded-inside-bounded with large
# products.
# Auto-generated for the D27 quantifier/bounded-repeat corpus.
# Every expectation is computed directly from python's re module.
```

**R-GEN-1 (the generator writes PLAIN `.rxt` — no generator-specific
syntax):** the D27 files are byte-for-byte ordinary `.rxt` — every directive
seen in them (`pattern`, `m`, `n`, `g`) is one already documented in
`docs/testing.md`. Machine generation today needs NOTHING from the format
beyond what a hand-author needs: the generator's contribution is in HOW
the file was produced (an author denied `src/`/`tests/`, verified against
an independent oracle, cross-checked by "a from-scratch checker" separate
from the generator itself), not in any format feature. **This is a
significant finding for [DD-13b]:** it means the D27 machine-generation
discipline provides no forcing function on the format's grammar — the
current format is already sufficient for it, and the requirement is
negative: whatever DD-13 becomes, it must not become HARDER for a
constrained/blinded author to write correctly (see R-RXT-2's `#`-comment
lesson, itself found BY a D27 author, and the anti-requirements in §8).

**R-GEN-2 (headers are a human convention, not a format feature):** the
descriptive header comment (family name, generation method, oracle used) is
plain `#` comments — there is no machine-readable provenance field in
`.rxt` today. Whether the new format should promote this from convention to
a structured field is a real open question but is NOT evidenced as a
current pain point; flagged for [DD-13b] to weigh, not asserted as a
requirement here (see "Observations for DD-13b" appendix).

**R-GEN-3 (the known_fail / live-corpus split must survive as a routing
decision, not a format feature):** `docs/dev/known_issues.md`-linked
regressions move BETWEEN directories (`tests/known_fail/` <->
`tests/base/`) as bugs are confirmed-then-fixed, per
`tests/known_fail/CLAUDE.md`'s documented convention — this is a
file-placement/build-routing decision (which directory a file lives in,
which script excludes it), not something the `.rxt` grammar itself encodes.
The new format must not need this to become an in-file flag; it is
orthogonal to the requirements above.

---

## 7. [M4-SUBST] intersection — YES, it intersects, narrowly

Evidence: `docs/design/subst_template_design.md` (full read of §1 and a
grep for file-format/manifest references), D38 ruling Q7.

**Finding:** `subst_template_design.md` itself does NOT touch file-format
territory — it is an ABI/compile-contract document (the capture-offset
CONTRACT a template compiler consumes: `rx_ctx.caps`, group count as a
compile-time constant, the `RX_UNSET` sentinel). A `grep` for
`.rxt`/"file format"/`DD-13`/manifest across the whole document returns only
three hits, all in §7 discussing `[V-E]`'s manifest as the future HOME for
a template field, never proposing format syntax itself:

> "**[V-E]**'s manifest is the ratified home for [a replacement template]...
> *Recommend: `--replace` now, and note the manifest gains a template field
> when that design lands.*" (§7, ~line 1157-1163)

This is confirmed independently by D38's own ruling text (§3 above, "Q7
`--replace` now (repeatable per §5.5); V-E's manifest gains a template
field when designed").

**R-SUBST-1 (a template-text field per named pattern, deferred field
shape):** the format needs, EVENTUALLY, a way to associate one or more
replacement-template strings with a named pattern (mirroring `pcre2
--replace`/`sed`-style templates: `$0`, `$1`, `${name}`). This is a real,
ratified obligation on [V-E]'s manifest (and therefore on DD-13, since
DD-13 subsumes V-E's manifest format per the plan row), but it has NO
shape requirements beyond "a field can hold template text co-located with
the pattern it replaces against" — the template's own internal grammar
(`$1`/`${name}` substitution syntax) is `[M4-SUBST]`'s territory entirely
and orthogonal to DD-13's grammar. **Do not design the template's internal
syntax here** — the requirement is only that the CONTAINING format has
somewhere for a template string to live per named pattern, the same way it
needs somewhere for `flags`/`features` to live per pattern today.

**R-SUBST-2 (no urgency, no other coupling):** `[M4-SUBST]` is explicitly
independent of the match API and can (and did) proceed via `--replace` on
the CLI without waiting on DD-13. There is no timing dependency forcing
DD-13 to resolve R-SUBST-1 before M4-SUBST can ship further work — it is a
"when the manifest exists" obligation, not a blocking one.

---

## 8. Consumer requirements table (cross-reference)

| Consumer | Plan row | Status | Requirements |
|---|---|---|---|
| `.rxt` harness/corpus | (pre-existing) | LIVE, ~10k cases | R-RXT-1..9 |
| Manifest + finder | [V-E] | not-started | R-VE-1..11 |
| Source-scan transformer | [V-F] | not-started | R-VF-1..2 (rides V-E) |
| User-facing testing | [V-G] | not-started | R-VG-1..3 (rides §1 + V-E) |
| pcrec-bench sets | pcrec-bench §8 Q1 | SEED | R-BENCH-1..9 |
| Machine generation | (D27 method) | LIVE | R-GEN-1..3 |
| Substitution templates | [M4-SUBST] | §9 RULED, unbuilt | R-SUBST-1..2 |

---

## 9. The `.rxt` compatibility answer: DIALECT, arguing from the survey data

The plan row asks directly: "is `.rxt` a subset, a dialect, or migrated?"
Argued from §1's census and §6's finding, not from opinion:

- **Not "subset."** A subset would mean today's `.rxt` files stay valid
  under a SMALLER grammar than the new format defines — true in the trivial
  direction (every requirement in §1 must remain expressible), but the new
  format necessarily grows well past `.rxt`'s grammar (named-pattern
  definitions with cross-references, per-testee config sections, file
  includes, exemplar references — none of which `.rxt` has any syntax for
  at all). Calling the relationship "subset" undersells how much new
  surface is required by §2 and §5 alone.

- **Not "migrated" (in the rewrite-the-corpus sense).** R-BENCH-8 is direct
  evidence against this: pcrec-bench's own charter *already assumes* `.rxt`
  content is IMPORTABLE as-is ("grows partly by import from pcrec's
  oracle-verified `.rxt` corpora"), written before DD-13a even started.
  Combined with R-GEN-1 (the D27 generator needs nothing beyond today's
  grammar) and the sheer size of the existing corpus (54 files, 1,100
  pattern blocks, 9,977 expectation lines, all oracle-verified against
  python `re` and, per `docs/testing.md`'s differential-gate principle,
  partially against libpcre2) — a flag-day rewrite of that corpus is
  expensive with no offsetting requirement demanding it. Nothing in §1-§7
  needs today's blocks to change MEANING, only for the file that contains
  them to gain new capabilities (names, references, sections, includes)
  that today's files don't use.

- **"Dialect"**, meaning: today's block-oriented `pattern`/`flags`/
  `features`/`perr`/`m`/`n`/`ms`/`ns`/`g`/`gp` vocabulary is a valid,
  unchanged SUBSET of the new format's expression for "one unnamed pattern
  with inline test cases" — every existing file parses and means exactly
  what it means today — while the new format ALSO defines a superset of
  syntax (names, references, sections, includes, exemplar files, and R-
  SUBST-1's eventual template field) that no existing file happens to use.
  This is exactly the shape [M4.5a]'s own `g`/`gp` addition already
  proved out IN today's format ("purely additive line kinds; no existing
  line's grammar or semantics changed... nothing needed re-verifying" —
  `docs/testing.md`, "Design: backward-compatible, artifact-size-agnostic")
  — DD-13a's recommendation is that DD-13b extend that SAME precedent one
  more level: new top-level constructs (names, refs, sections, includes)
  alongside the untouched block grammar, not a replacement of it.

This is a REQUIREMENT worth stating explicitly for [DD-13b] even though it
edges toward design: **R-COMPAT-1: existing `.rxt` files must remain valid,
unmodified, and semantically unchanged under the new format** — evidenced
by R-BENCH-8's import assumption, R-GEN-1's zero-forcing-function finding,
and the corpus's own size/oracle-investment (9,977 lines, all previously
oracle-verified — re-verifying them under new semantics would be pure cost
with no corresponding requirement asking for it).

---

## 10. Conflicts and tensions between consumers (stated, not resolved)

**T-1: interface-vs-reference-only patterns vs V-G's every-part-testable
promise.** `frank_inputs.md` point 5: some patterns exist only to be
referenced (private definitions, never exported as an entry point) —
codegen consequence, only interface patterns get entry points, reference-
only ones inline at their use sites. But R-VG-2 promises every NAMED part
of a manifest is independently testable. A reference-only pattern by
definition has no exported entry point to run the harness against — so
"testable" for it must mean something other than "compile this name's own
artifact and run cases against it," or it needs a TEST-ONLY compiled
surface that doesn't exist for any other purpose. `frank_inputs.md` already
names this tension explicitly and defers it to [DD-13a]/[DD-13b]; this note
carries it forward as OD-4 (§11) rather than resolving it, per the D26/D27
"do not gold-plate" discipline and the brief's own instruction not to
design.

**T-2: source-level inlining (R-VE-4's default tier) vs per-library
declared tweaks (R-BENCH-7).** Source-level composition is defined as
AST-inlining with a stated goal of DFA-compilability preservation — a
CANONICAL shared pattern. Bench's per-library tweak mechanism
(`frank_inputs.md` point 3) explicitly allows a library's application block
to modify how the shared pattern is applied. If a tweak changes the
PATTERN TEXT itself (not just compile options), the "one pattern reference"
claim central to R-BENCH-2 is threatened — `frank_inputs.md`'s own
"manager's sharpening" already flags this ("keep the shared pattern
CANONICAL and make any per-engine tweak DECLARED and visible... or 'single
pattern reference' quietly stops being true"). The requirement (R-BENCH-7)
is stated; whether the format can even express a "declared tweak" that
ISN'T secretly a second, undeclared pattern is a design question, not
resolved here.

**T-3: append-only group numbering (R-VE-5, a SOURCE-LEVEL/inlining
property) vs bench's need for a format-agnostic, engine-independent
correctness expectation (R-BENCH-4).** D39.2's numbering scheme is a
pcrec-specific compile-time artifact detail (`RX_NCAPS`-shaped, `ref`-
column-shaped). Bench needs expectations that adjudicate RE2/Oniguruma/TRE/
etc. as well as pcrec — none of which share pcrec's appended-numbering
convention or its labeled-reference mechanism. Whatever the format's
capture-expectation shape becomes, it cannot be defined ONLY in terms of
pcrec's own numbering scheme without also giving bench engine-neutral
groups (e.g. by name, where names are portable, rather than by pcrec's
post-append slot number).

**T-4: `.rxt`'s block-scoped, non-carrying `flags`/`features` (R-RXT-1)
vs bench's CASCADING per-testee options (`frank_inputs.md` point 2,
"options CASCADE to the last reference... ordered includes; later entries
add to / override earlier ones").** These are opposite defaults: today's
format resets state at every `pattern` line; bench's proposed model
accumulates state across an ordered chain of includes. Both are real,
evidenced requirements (R-RXT-1 from 1,100 existing blocks; R-BENCH-2/
frank_inputs.md point 2 from the bench charter) and they are NOT the same
scoping rule. [DD-13b] needs a scoping model that can express BOTH a
block that intentionally resets on each `pattern` (today's default,
R-COMPAT-1 requires it stay available) and a cascade across includes for
sections that want it — this is exactly what OD-1 (§11) is about, and this
note takes no position on how.

**T-5: exemplar/corpus files by reference (R-BENCH-6) vs the harness's
inline-quoted-string model (R-RXT-3) and its byte-exact escape discipline.**
An externally-referenced subject file needs the SAME byte-exact-including-
NUL guarantee R-RXT-3 gives inline subjects (driver.c's own explicit
`strlen()`-avoidance discipline exists for exactly this reason). A
reference mechanism that reads a file via any text-mode/line-oriented path
risks silently reintroducing the exact bug class R-RXT-3 was built to
avoid — flagged as a requirement on WHATEVER reference mechanism DD-13b
designs (byte-exact contents, no implicit encoding/newline transformation),
not a specific mechanism.

---

## 11. Open-decision ledger (carried forward from `frank_inputs.md`, unresolved by design)

Each OD item is restated here as: what any candidate answer MUST satisfy,
per the requirements above, followed by the decision itself left open —
consistent with the brief's instruction not to pick.

**OD-1 — where per-engine options live and their composition rules across
includes.** Must satisfy: R-BENCH-2 (a section per testee), R-BENCH-9
(the SAME mechanism serves non-bench build-config sections), T-4 (must
coexist with, not replace, `.rxt`'s existing block-scoped non-carrying
default per R-COMPAT-1). The cascade DIRECTION is already ruled
(`frank_inputs.md` point 2: ordered, last-reference-wins) — what remains
open is WHERE options may be declared (file scope / section scope /
pattern scope / case scope) and how a scope's declared options compose with
an ancestor scope's when both apply to the same referenced pattern.

**OD-2 — the declared-tweak mechanism for per-library pattern
application.** Must satisfy: R-BENCH-7 (visible, never silent),
R-BENCH-2 (per-testee application blocks), T-2 (must not silently break
"one canonical pattern" — a tweak that changes match semantics needs to be
distinguishable, at minimum by a human skimming the file, from one that
only changes compile options).

**OD-3 — configuration-section syntax unifying bench testees and build
variants.** Must satisfy: R-BENCH-2, R-BENCH-9 (explicitly the SAME
concept, "one concept, two uses" per Frank), R-VE-1 (a compilation unit can
already be "perhaps several" outputs, so a config section's relationship
to output-unit boundaries needs to be coherent with V-E's own
one-or-several-outputs model).

**OD-4 — interface/reference-only marking, and whether reference-only
patterns get a test-only surface.** Must satisfy: T-1 above (the central
tension), R-VG-2 (every named part independently testable), R-VE-2 (D20's
no-forced-dispatch rule — a test-only surface must not leak dispatch cost
into the interface-pattern's real entry point). This is the item this note
found the LEAST additional evidence for beyond `frank_inputs.md`'s own
statement of it; it stays exactly as open as Frank left it.

**OD-5 — PCRE2 `(?(DEFINE))`/`(?&name)` desugar vs pcrec's own reference
spelling (inherited from [V-E], R-VE-8).** Must satisfy: R-VE-4 (source-
level inlining, zero runtime cost, DFA-compilability preserved regardless
of which spelling is chosen — this is a property of the LOWERING, not the
surface syntax, so both candidate answers must still satisfy it), R-VE-5
(D39.2's appended numbering — the PCRE2-desugar option's own "subroutine-
call semantics are ATOMIC and shift capture numbering" is a DIFFERENT
numbering behavior than D39.2 already ruled for pcrec's own reference
form, so choosing desugar would need its own numbering reconciliation,
not an automatic inheritance of D39.2). "measured never read" — Frank's own
tag on this item — means any future measurement toward resolving it should
run libpcre2, not cite documentation.

---

## 12. Anti-requirements — what the format must NOT do

**AR-1 (must not force re-verification of the existing corpus).** Per
R-COMPAT-1 / §9: 9,977 already oracle-verified expectation lines exist.
A format design that changes the MEANING of any existing directive (not
just adds new ones) reopens all of them for re-verification, which no
consumer's requirement asks for. D18's "earn its axis" discipline (cited
generally in the plan; not reproduced here) applies: new grammar must earn
its cost, and "invalidates 54 files of prior verification work" is a cost
with no offsetting demand in this survey.

**AR-2 (must not force dispatch into the hot loop for the common case).**
D20's rule, restated as R-VE-2, is load-bearing across the whole project
(OS-0, the finder, D18's speed mandate) and not something [DD-13] gets to
relitigate: "a single-pattern single-option request emits byte-for-byte
today's output." Whatever the manifest format becomes, compiling ONE named
pattern with no references and no config sections must not become more
expensive — at compile time OR at runtime — than compiling that same
pattern stood alone today.

**AR-3 (must not conflate declared inapplicability with failure or with
silent pass).** Three independent consumers already need this distinction
and get it three different ways today (R-RXT-7's `# pcre2-only` counted
skip, `docs/testing.md`'s PC-3 loud `SKIP:` lines, R-BENCH-3's first-class
"unsupported" adapter result). The format must not collapse these into a
boolean or into an ordinary failure — every existing instance of this
pattern in the project is loud and counted, never silent.

**AR-4 (must not make the machine-generation / D27 discipline harder).**
R-GEN-1's finding is that today's format imposes NO tax on a blinded,
`src/`-and-`tests/`-denied author beyond ordinary care (R-RXT-2's `#`
lesson was found BY such an author, and fixed IN the format's spec, not
by asking authors to be more careful). A successor format that requires,
say, cross-file context to interpret a single pattern block correctly
would make this materially harder for exactly the authoring mode D27 exists
to protect ("tests written from the GOAL," CLAUDE.md's D27 paragraph) —
flagged as a constraint though no specific mechanism is known to violate it
yet.

**AR-5 (must not let a config/options mechanism become a silent semantic
fork of a "single pattern reference"), restated from T-2 / OD-2.** Not
reproduced in full here; see §10 T-2 and §11 OD-2.

**AR-6 (must not require pcrec-specific data to express bench
expectations), restated from T-3.** Not reproduced in full here; see §10
T-3.

**AR-7 (must not silently violate D18/D20's structural properties via the
FORMAT rather than the codegen).** General framing of AR-2: the mandate in
this note's brief calls out "D18/D20 structural properties it must not
force the emitter to violate" — concretely, these are: (a) no dispatch for
a statically-known single-pattern call (D20, AR-2); (b) the generator/
finder split itself — a format that makes "just compile a generator, no
finder" impossible to express (e.g. by requiring every file go through
finder-shaped multi-pattern machinery even for one pattern) would violate
D20's "you pay for the product only if you use it" as directly as a
dispatch-adding codegen change would.

---

## 13. For the [DD-13c] panel

Claims worth attacking, listed so the panel does not have to re-derive
them:

1. **The "dialect, not subset/migration" answer (§9)** rests on R-BENCH-8
   (one sentence in a SEED-status, no-code-yet charter document) and
   R-GEN-1 (one directory's generator practice). Both are real but narrow;
   attack whether they generalize to the FULL consumer set, especially
   [V-G]'s and [V-E]'s not-yet-written requirements.
2. **R-GEN-1's "no forcing function" finding** is a survey of ONE
   generator (the D27 quantifier corpus). It is the strongest evidence in
   this note for "don't add grammar the current format can't already
   express" (AR-1/AR-4), but it is a sample size of one generator, one
   feature area (quantifiers), one author. Whether it generalizes to a
   generator that (say) needs cross-references or config sections — which
   don't exist yet for any generator to have exercised — is untested by
   construction.
3. **T-3's claim that pcrec's numbering scheme can't be the ONLY capture
   expectation shape for bench** assumes bench needs engine-neutral group
   identification. Attack whether `.rxt`'s existing `g`/`gp` SLOT-NUMBER
   model (not name-based) is actually adequate for bench's roster, given
   that RE2/Oniguruma/etc. do have their own slot-numbering conventions
   that might already align closely enough in the common (non-reference,
   non-inserted) case that T-3 overstates the tension.
4. **§7's "no urgency, no other coupling" claim for M4-SUBST (R-SUBST-2)**
   was derived from D38's ruling text and the design note's own scope
   statement; it was not independently verified against whether
   `--replace`'s CLI-only existence today has already created any
   informal convention (flag spelling, template syntax choices) that a
   later manifest `template` field would be awkward to match. Not
   evidenced either way in this note — worth a direct check before
   [DD-13b] treats R-SUBST-1 as a free, unconstrained field.
5. **The corpus census in §1** was taken by direct `grep`/`find` survey of
   THIS worktree at one point in time (2026-08-17); it is reproducible
   (commands are stated) but was not cross-checked against `make test`'s
   own reported case counts from a live run. `docs/testing.md`'s own
   section-runtime tables report different aggregate counts at different
   historical commits (e.g. "corpus 1270 cases" at one older commit,
   "corpus 1679 cases" at a later `test-corpus` line) — the 9,977 figure
   in this note is internally consistent (same worktree, same moment) but
   the panel should re-run the census rather than trust it verbatim if
   material time has passed.

---

## Appendix: observations for [DD-13b] (explicitly NOT requirements)

Flagged and quarantined here per the brief's D26 instruction, rather than
silently smuggled into the numbered requirements above:

- **A structured provenance/generation-method header field** (R-GEN-2) is
  an idea, not a requirement — no consumer's evidence demands it, it only
  seemed like a natural place to promote an existing human convention. If
  [DD-13b] adopts it, it should cite this appendix, not a requirement
  number, as its justification.
- **Whether OD-1's option scoping should look like nested blocks, a
  separate top-level section, or attribute-style annotations on a
  `pattern`/name line** is a grammar sketch and stays entirely out of this
  note by design; T-4 states only that both a resetting default and an
  accumulating cascade must be expressible, not how.
- **Whether the `ref`/label mechanism (R-VE-6/D39 addendum) should be a
  file-path-like string, a dotted path, or something else** is,
  similarly, [DD-13b]'s to sketch; this note states only that a slot for
  it must exist.
