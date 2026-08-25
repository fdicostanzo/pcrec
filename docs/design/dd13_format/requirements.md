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
forward (`docs/spec/rxt_format.md` "The `.rxt` format", moved there
[SPEC-1.6] after this requirements note was written — same content). Any successor format must
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

**R-RXT-10 (`perr` asserts THAT, never WHY — `tests/reject/`'s own
documented limitation):** `tests/reject/CLAUDE.md` states directly: "A
`perr` block cannot express the part that matters most — that the
diagnostic names the RIGHT module. That name is the caller's only pointer
to what would implement the construct, and `perr` asserts only that
compilation failed." This is why `tests/reject/`'s 306+ hand-maintained
rows (plus generated sweeps) live in a C table rather than `.rxt` at
all — a structural gap in today's format, not an oversight, and the
reason `tests/reject/` exists as a wholly separate consumer this note's
earlier draft did not survey. Whether a successor format closes this gap
(e.g. an expected-diagnostic-substring or expected-module assertion) is
[DD-13b]'s decision, not this note's — but the requirements note may not
omit a consumer whose entire existence is explained by a documented
format limitation. Note the same THAT-not-WHY shape reappears
independently in `subst_template_design.md`'s proposed `serr` directive
(R-SUBST-3, §7) — a bare "the template fails to compile," no diagnostic
content — so if [DD-13b] decides to close this gap, it likely wants one
mechanism serving both `perr` and `serr`-shaped needs, not two.

---

## 2. [V-E] manifest + finder + compilation units

Evidence: `docs/dev/plan.md` [V-E] row (lines ~374-432) and, for R-VE-1
specifically, the [DD-13] row itself (lines ~722-768, which restates and
extends [V-E]'s scope); D39 + addendum, D38 Q7, D20.

**R-VE-1 (N named patterns → one or more emitted units):** the manifest is a
COMPILATION SOURCE — `docs/dev/plan.md`'s **[DD-13] row** (line 726, not
[V-E]'s own row — corrected per R27 F11, which caught this note citing the
wrong row): "N named patterns → one emitted unit, perhaps several." The
format must be able to name a compilation-unit boundary per pattern or
group of patterns, not assume one-file-in → one-file-out.

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
(carried to OD-ledger below, §11):** path spelling/separator, whether the
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
(plain inlining semantics, beyond-PCRE2) is explicitly UNRESOLVED —
"OPEN CHOICE (Frank's, **Q2/K4-tier — measured, never read from docs**)"
(exact quote restored per R27 F11; an earlier draft compressed this to
"measured never read," dropping "from docs," which is the operative part —
it is an instruction about METHOD, not just a status tag). Carried to the
OD ledger (§11, OD-5).

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

**R-VE-12 (a per-pattern encoding field):** `docs/dev/plan.md`'s [V-E] row
states the manifest entry shape directly: "the MANIFEST is the user-facing
FILE FORMAT for specifying regexes (**name, pattern, flags, encoding per
entry** → one compiled unit)" (line 396). No requirement above covers this
explicitly — R-VE-9/10 discuss usage modes and the manifest's status as a
user surface, not the per-entry field list itself. The format needs a
place for an ENCODING selector per named pattern, alongside its `flags`.
This note does not survey what pcrec's encoding axis currently contains
(that is APPROACH.md/D20/OS-1 territory, not this note's) — the
requirement is only that the field exists per pattern; its value space is
[DD-13b]'s (and ultimately the encoding axis's own design's) to define.

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
scope... and docs." Every requirement in §1 (R-RXT-1..10) is therefore also
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
interface-vs-reference-only tension (§10 T-1, §11 OD-4) originates — see
§5 of `frank_inputs.md`, restated in the OD ledger below.

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
methods within one hazard band). **Attribution note (R27 F12):** grouping
these four together as one "per-case tag set" is this note's own synthesis
of §3's prose list — APPROACH.md §3 lists tier/hazard/size/
verification-method as prose, not as a formal four-field schema; the
GROUPING is this note's inference, not a structure APPROACH.md itself
declares.

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
APPROACH.md §2):** "large subjects/corpora live in external files,
referenced rather than inlined" (Frank, row creation) and independently,
APPROACH.md **§2**'s first founding principle assumes corpora can be large
("a larger test set than normal... big subjects" — corrected per R27 F11;
an earlier draft mis-cited this as §3, the architecture-sketch section,
when it is actually §2's founding-principles list). The format needs
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
checker."[^676] 

[^676]: This note's own direct count of case-lines across the six files
    (`m` + `n` + `g`: 335 + 81 + 263) is **679**, not 676. The quoted
    `tests/base/CLAUDE.md` figure has drifted — apparently during a later
    re-pin unrelated to this note (the counter-K era) — not this note's
    arithmetic, which is why the quote is kept verbatim above rather than
    silently "corrected" to match a recount `tests/base/CLAUDE.md` itself
    doesn't yet say. `tests/base/CLAUDE.md` is deliberately left unedited
    here (R27 F8): it should be fixed after the held d27k23 branch merges,
    since that branch touches the same file and a fix here would create a
    gratuitous conflict.

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
lesson, itself found BY a D27 author, and the anti-requirements in §12).

**Additional evidence (R27 F13): this is not a sample of one.** An earlier
draft's own §13 self-critique called R-GEN-1 "a survey of ONE generator...
a sample size of one generator, one feature area, one author" — the panel
found this too harsh, because the note had not looked past the D27
quantifier corpus for other generation events already in the repo. There
are at least **five** independent instances of the same pattern (plain
`.rxt`, no format-specific syntax, produced by something other than a
human directly transcribing test cases), not one:

1. The D27 quantifier corpus itself (`tests/base/d27_*.rxt`, above).
2. **A second, independent D27-blinded generation event**: the [M4.5d]
   capture author, `tests/captures/` (`docs/dev/reviews/2026-08-15-r22-m45d-capture-author.md`,
   R22) — "85 m/ms cases + 145 group lines, python-derived and twice
   verified, 230/230 green against the VM," described in that review as
   "the strongest independent capture-correctness evidence in the
   project." A different author, a different feature area (captures, not
   quantifiers), same result: plain existing `.rxt` directive vocabulary
   (`pattern`/`m`/`ms`/`g`/`gp`), no format extension needed.
3. **`tests/possessify/possessify.rxt`** (76 pattern blocks, this note's
   own §1 census) — a systematically GENERATED, non-blinded
   oracle-verified corpus for the [ENG-BREP] possessification rung; per
   `tests/possessify/CLAUDE.md`, "not a module directory... no block here
   carries a `features` directive" — plain `pattern`/`m`/`n` (+ `g`
   where captures are involved), nothing new.
4. **`tests/rungselect/rungselect.rxt`** (29 pattern blocks) — the same
   generated-corpus shape one rung up the [ENG-BREP] ladder, per
   `tests/rungselect/CLAUDE.md` structurally identical in format
   requirements to (3).
5. **`tests/counterk/`'s `.rxt` corpus** (32 pattern blocks) — the
   [ENG-BREP] COUNTER rung's own generated differential corpus, same
   shape again.

All five were checked directly (file counts from this note's own §1
census; `tests/captures/CLAUDE.md`, `tests/possessify/CLAUDE.md`,
`tests/rungselect/CLAUDE.md` read for their stated generation method) and
all five use only directive vocabulary `docs/testing.md` already
documents. The no-forcing-function finding is **n=5**, spanning two
authoring modes (D27-blinded and systematically-generated-non-blinded),
at least three feature areas (quantifiers, captures, emission-strategy
differentials), and at least three separate authors/lanes — not the
single narrow sample an earlier draft of this note's own §13 believed it
was reporting.

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

## 7. [M4-SUBST] intersection — YES, and more than an earlier pass of this note found

Evidence: `docs/design/subst_template_design.md`, full read of every
section (§1-§10), D38 ruling Q7.

**Correction (R27 F1, a blocker in the panel review of this note's first
draft).** An earlier draft reported: *"a `grep` for `.rxt`/'file
format'/`DD-13`/manifest across the whole document returns only three
hits, all in §7."* That count was written down without being re-run, and
it was wrong. Re-run directly:

```
$ grep -n '\.rxt\|file format\|DD-13\|manifest' docs/design/subst_template_design.md
756:natural hook for **[V-E]**'s manifest (a template becomes a field of a named
992:neither of which `.rxt` can express. The extension follows the existing
993:directive grammar exactly (`docs/testing.md`, "The `.rxt` format") — a
1157:   the obvious flag. But **[V-E]**'s manifest is the ratified home for
1159:   field of that entry. *Recommend: `--replace` now, and note the manifest
1163:   `[V-E]`'s manifest gains a template field when that design lands.
```

Six hits, not three, and the earlier draft had surveyed only the three at
§7 (lines 1157/1159/1163 above). Line 756 (§5.5) and lines 992-993
(§8) were never read. §8 in particular is not a passing mention — it is a
fully-worked, ten-question-earlier, PROPOSED (unpaneled) `.rxt` extension
for substitution testing, and it is the single most concrete piece of
format-extension prior art anywhere in this repository. Certifying it
absent was the failure; both R27 panel lenses caught it independently.

**§5.5 (line 756) — a second, independent manifest hook.** "*nothing in
this design ties one pattern to one template. The splice code is
per-template; the matcher is per-pattern and shared. Emitting
`rx_subst_redact` and `rx_subst_expand` over one matcher is the same
named-entry-point mechanism as §5.3 and needs no new machinery. This is
the natural hook for **[V-E]**'s manifest (a template becomes a field of a
named entry) and is noted so the design does not accidentally preclude
it.*" This is the SAME field R-SUBST-1 already states as a requirement
(one field, potentially many templates per pattern) — no new requirement
follows, but it is independent corroboration that the design note itself
already assumed a manifest field would exist, at two separate points in
the document, not one.

**§8 "Testing sketch" (lines 987-1090) — the prior art R-SUBST-3 records
below.** §8.1 proposes a concrete `.rxt` extension (`repl`/`s`/`sg`/
`serr`); §8.2 proposes an oracle strategy (python's `re.sub`, with one
documented, measured exclusion); §8.3 is a phase-1 test plan identifying
what is testable before M4/captures land; §8.4 argues this feature is "an
unusually good D27 candidate." All of it PROPOSED, none of it panelled or
ruled.

**R-SUBST-1 (a template-text field per named pattern, deferred field
shape):** the format needs, EVENTUALLY, a way to associate one or more
replacement-template strings with a named pattern (mirroring `pcre2
--replace`/`sed`-style templates: `$0`, `$1`, `${name}`). This is a real,
ratified obligation on [V-E]'s manifest (and therefore on DD-13, since
DD-13 subsumes V-E's manifest format per the plan row), corroborated
independently at two points in `subst_template_design.md` (§5.5 and §7),
but it has NO shape requirements beyond "a field can hold template text
co-located with the pattern it replaces against" — the template's own
internal grammar (`$1`/`${name}` substitution syntax) is `[M4-SUBST]`'s
territory entirely and orthogonal to DD-13's grammar. **Do not design the
template's internal syntax here** — the requirement is only that the
CONTAINING format has somewhere for a template string to live per named
pattern, the same way it needs somewhere for `flags`/`features` to live
per pattern today.

**R-SUBST-2 (no urgency; the coupling is real but non-blocking):**
`[M4-SUBST]` is explicitly independent of the match API and can (and did)
proceed via `--replace` on the CLI without waiting on DD-13. There is no
timing dependency forcing DD-13 to resolve R-SUBST-1 before M4-SUBST can
ship further work. The "no other coupling" language an earlier draft used
here was too strong given R-SUBST-3 below — read this item as "no
*blocking* coupling," not "no coupling."

**R-SUBST-3 (repl/s/sg/serr — PRIOR ART, not a binding requirement):**
`subst_template_design.md` §8.1 works out a full block-scoped `.rxt`
extension for substitution testing:

```
# repl <template>       — block-scoped, like flags/features; does not carry
# s  "<subject>" "<expected output>"    — first-match substitution
# sg "<subject>" "<expected output>"    — global substitution
# serr                                  — the TEMPLATE fails to compile
```

with a worked example, an oracle strategy (§8.2: python's `re.sub` is
measured a valid oracle for global-mode splice geometry — byte-for-byte
agreement with libpcre2 on every empty-match cell measured — with one
documented, measured exclusion: unset-but-existing groups diverge between
the two oracles depending on how D38's Q3 ruling is read), and a
phase-1 test plan (§8.3) identifying which parts are testable before
M4/captures land at all (the whole template compiler minus `$1..$n`;
every literal-only splice; the entire global-mode splice geometry, since
`$0` is already `rx_span`). §8.4 argues this is "an unusually good D27
candidate," for the same reason this note's own R-GEN findings (§6) argue
the quantifier and capture corpora were.

This is UNPANELED, PROPOSED design — not a Frank ruling, not a binding
requirement on [DD-13b] — but [DD-13b] should read it directly rather than
rediscover its shape. Two structural facts in it bear directly on this
note's own OD-1/T-4 (§10/§11): the proposed `repl` directive is
block-scoped and explicitly does **not** carry forward across `pattern`
lines — the same non-carrying default R-RXT-1 already established for
`flags`/`features` — and the `<expected output>` field reuses R-RXT-3's
existing escape set unchanged, which is independent evidence (from a
different author, a different feature) that R-RXT-3's byte-exact
discipline is the thing to reuse rather than reinvent, relevant again to
T-5's exemplar-file byte-exactness concern.

---

## 8. Consumer requirements table (cross-reference)

| Consumer | Plan row | Status | Requirements |
|---|---|---|---|
| `.rxt` harness/corpus | (pre-existing) | LIVE, ~10k cases | R-RXT-1..9 |
| `tests/reject/` (module-diagnostic table) | (pre-existing) | LIVE, structurally separate from `.rxt` | R-RXT-10 |
| Manifest + finder | [V-E] | not-started | R-VE-1..12 |
| Source-scan transformer | [V-F] | not-started | R-VF-1..2 (rides V-E) |
| User-facing testing | [V-G] | not-started | R-VG-1..3 (rides §1 + V-E) |
| pcrec-bench sets | pcrec-bench §8 Q1 | SEED | R-BENCH-1..9 |
| Machine generation | (D27 method + 4 more, §6) | LIVE, n=5 sources | R-GEN-1..3 |
| Substitution templates | [M4-SUBST] | §9 RULED, unbuilt | R-SUBST-1..3 |

---

## 9. The `.rxt` compatibility answer: DIALECT — held under adversarial review, confidence softened (R27 F6)

The plan row asks directly: "is `.rxt` a subset, a dialect, or migrated?"
**R27's panel attacked this conclusion directly** (r27b's brief was to
steelman AGAINST it) and reported it could not construct a case where a
strictly-additive dialect structurally violates any R-* requirement in
this note; T-4's cascade-vs-non-carrying tension in particular looks
resolvable by scoping cascades to new top-level constructs that legacy
files never opt into. **The DIALECT conclusion stands** — but the earlier
draft's evidence for it claimed more certainty than it supports, and this
revision states the argument more carefully.

- **Not "subset."** A subset would mean today's `.rxt` files stay valid
  under a SMALLER grammar than the new format defines — true in the trivial
  direction (every requirement in §1 must remain expressible), but the new
  format necessarily grows well past `.rxt`'s grammar (named-pattern
  definitions with cross-references, per-testee config sections, file
  includes, exemplar references — none of which `.rxt` has any syntax for
  at all). Calling the relationship "subset" undersells how much new
  surface is required by §2 and §5 alone.

- **Not "migrated" (in the rewrite-the-corpus sense) — but this is weaker
  evidence than an earlier draft treated it as (R27 F6).** R-BENCH-8 cites
  pcrec-bench's charter: "grows partly by import from pcrec's
  oracle-verified `.rxt` corpora." An earlier draft read "import" as
  settling the question; it does not. "Import" is consistent with BOTH a
  dialect (existing files parse unchanged under the new format) AND a
  migration-with-tooling (existing files are mechanically converted by an
  importer, which is also fairly described as "growing by import"). The
  seed-doc sentence is one clause in a no-code-yet charter and does not by
  itself disambiguate the two. **A second, independent corroboration this
  note had not cited**: `pcrec-bench/APPROACH.md` §8 Q1 itself, ruled in
  direction the same day DD-13 was created, describes the format as
  "grown **from** `.rxt`" — directional language, closer to "dialect
  extending a base" than to "migrated," and written by a different author
  (Frank, in the row-creation ruling) than R-BENCH-8's charter prose. Two
  independent sources leaning the same direction is stronger than one, but
  neither is a proof, and this note treats both as corroborating evidence
  for the argument below, not as the argument itself.

- **The `.rxt`-import claim should read import-PLUS-AUGMENTATION, not
  import-as-is (R27 F6).** R-BENCH-1..9 establish that bench needs
  per-case tags (tier, hazard class, size, verification method) and
  section/testee concepts that `.rxt` has no syntax for at all today.
  So even under the DIALECT reading, an imported `.rxt` file does not
  become a bench SET merely by being parsed — it becomes one after bench
  augments it with the tags and sections its own requirements demand.
  "Importable" is the right word for "existing files remain syntactically
  valid input"; it is the wrong word for "existing files are already
  complete bench sets," which nothing in this note establishes and
  R-BENCH-1/2/5 argue directly against.

- **The `.rxt`-precedent argument (g/gp) is real but categorically
  FLATTER than what DD-13 needs (R27 F6).** [M4.5a]'s own `g`/`gp`
  addition is genuine, measured precedent for "add new line kinds to
  `.rxt` without disturbing existing semantics" ("purely additive line
  kinds; no existing line's grammar or semantics changed... nothing
  needed re-verifying" — `docs/testing.md`). But `g`/`gp` added two new
  FLAT line kinds to an already-flat, single-file, non-hierarchical
  model. DD-13's own requirements (§2, §5) are HIERARCHICAL
  (named-pattern definitions, cross-references with appended numbering),
  CROSS-FILE (includes, exemplar references), and CASCADING (per-testee
  option composition, T-4/OD-1) — none of which `g`/`gp` exercised or
  tested. The precedent supports "additive extension is possible in
  principle and has one measured success," not "additive extension at
  THIS scale of new structure is proven safe." This note downgrades that
  claim accordingly: it is supporting evidence for the RECOMMENDATION
  below, not proof that the recommendation is risk-free.

- **"Dialect"**, meaning: today's block-oriented `pattern`/`flags`/
  `features`/`perr`/`m`/`n`/`ms`/`ns`/`g`/`gp` vocabulary is a valid,
  unchanged SUBSET of the new format's expression for "one unnamed pattern
  with inline test cases" — every existing file parses and means exactly
  what it means today — while the new format ALSO defines a superset of
  syntax (names, references, sections, includes, exemplar files, and R-
  SUBST-1's eventual template field) that no existing file happens to use.
  DD-13a's recommendation is that [DD-13b] extend the g/gp precedent one
  more level — new top-level constructs (names, refs, sections, includes)
  alongside the untouched block grammar, not a replacement of it — while
  recognizing, per the point above, that this is a bigger step than g/gp
  took and deserves its own verification (byte-identical re-parse of the
  full existing corpus under the new grammar) before [DD-13c] treats
  compatibility as settled.

This is a REQUIREMENT worth stating explicitly for [DD-13b] even though it
edges toward design: **R-COMPAT-1: existing `.rxt` files must remain valid,
unmodified, and semantically unchanged under the new format** — evidenced
by R-BENCH-8's and APPROACH §8 Q1's converging (not conclusive) import/
grown-from language, R-GEN-1's now-n=5 zero-forcing-function finding (§6),
and the corpus's own size/oracle-investment (9,977 lines, all previously
oracle-verified — re-verifying them under new semantics would be pure cost
with no corresponding requirement asking for it). R-COMPAT-1 itself is not
weakened by any of the softening above — it is a requirement this note
states regardless of which of the three compatibility answers turns out
truest; what is weakened is only the confidence with which "dialect" is
argued to be the descriptively correct label for what [DD-13b] will
produce.

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
carries it forward as OD-4 (§11) rather than resolving it, per the brief's
own do-not-design instruction (in D26's effort-tiering spirit — D26 itself
is about PCRE2-diagnostic wording, not requirements-note scope, but the
"spend effort where it's owed, not further out" logic generalizes and the
brief's own wording invokes it this way).

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

**T-6: R-RXT-9's per-FILE population accounting vs FILE INCLUDES.** R-RXT-9
documents that `run.sh` already keeps three distinct failure taxonomies
(pattern-compile failure, harness-level failure, ordinary case failure) —
but this exists today because the ACCOUNTING UNIT is the FILE: `run.sh` is
invoked per `.rxt` file (or discovers files recursively) and its summary is
a per-invocation tally over that file. `frank_inputs.md`'s FILE INCLUDES
requirement (case sets composed from included fragments, so a hand-written
source isn't bloated by a machine-generated set, and per-engine/config
fragments compose for the bench use) breaks that unit: once a named
pattern's definition, or its test cases, can live across an included file
and the file that includes it, "which file failed to compile" and "which
file's case count is N" both stop being well-defined questions — the
natural accounting unit becomes the INCLUDE CLOSURE (the entry file plus
everything it transitively includes), not any single file within it. No
requirement stated in this note anticipates that shift, R-RXT-9's own text
included. [DD-13b]'s population-accounting design — which R-RXT-5's `g`/
`gp` discipline shows the project already treats as a first-class
concern, not an afterthought — needs to define explicitly what unit a
summary line refers to once includes exist, rather than silently
inheriting "the file" from today's harness.

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
only changes compile options). **Note on provenance:** the
semantic-tweak-vs-compile-option-tweak split just stated is this note's
own derived distinction (T-2's synthesis of `frank_inputs.md` point 3
against R-BENCH-2) — `frank_inputs.md` itself does not draw this line; it
states only that a tweak must be declared and visible, not that there are
two kinds of tweak with different stakes.

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

1. **The "dialect, not subset/migration" answer (§9), already attacked once
   (R27 F6/r27b's steelman) and held, but not proven.** R27's panel tried
   directly to construct a case where a strictly-additive dialect
   structurally violates an R-* requirement in this note and failed;
   T-4's tension looked resolvable by scoping cascades to new top-level
   constructs. §9 now states two independent, converging (not
   conclusive) textual corroborations (R-BENCH-8's "import," APPROACH §8
   Q1's "grown from .rxt") plus R-GEN-1's n=5 zero-forcing-function
   finding — stronger than the earlier draft's single citation, but still
   evidence about what has been NEEDED so far, not a proof about what
   [DD-13b]'s actual grammar will require. The residual, sharpest version
   of the attack: everything measured so far (§6's five generators, the
   bench charter's own prose) predates any generator or consumer actually
   exercising cross-references, config sections, or file includes — the
   exact features that make DD-13 bigger than g/gp's precedent (§9's own
   new point). A panel with more time could try to construct a HYPOTHETICAL
   include/reference pattern and check whether it is even representable as
   "existing files unchanged, new top-level constructs added," rather than
   relying on absence-of-counterexample from a note that (by its own
   admission) surveyed no generator that has tried.
2. **R-GEN-1's "no forcing function" finding is n=5, not n=1** (§6,
   corrected per R27 F13 — an earlier draft's self-critique here
   undercounted its own evidence and the panel caught it). It is the
   strongest evidence in this note for "don't add grammar the current
   format can't already express" (AR-1/AR-4), and it now spans two
   authoring modes and at least three feature areas. What is STILL
   genuinely untested, and worth the panel's attention: none of the five
   sources needed cross-references, config sections, file includes, or
   anything else §2/§5 of this note require — every one of them is a flat
   corpus of independent pattern blocks. Whether the no-forcing-function
   finding generalizes to a generator that DOES need those (which don't
   exist yet for any generator to have exercised, blinded or not) is
   untested by construction, and n=5-with-zero-variance-on-the-untested-
   axis is a different, narrower claim than n=5 alone might suggest.
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

Flagged and quarantined here per the brief's own do-not-design instruction
(in D26's effort-tiering spirit — see the T-1 note above on this label),
rather than silently smuggled into the numbered requirements above:

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
- **Keyword-collision risk between reserved directive words and named
  definitions is unexamined (R27 F10).** If [DD-13b]'s named-pattern
  syntax resembles `frank_inputs.md`'s own working shorthand (`regexa =
  abc|def`, quoted in the [DD-13] plan row), a name that collides with a
  reserved first-token — `pattern`, `flags`, `features`, `m`, `n`, `ms`,
  `ns`, `g`, `gp`, `perr`, and now (per R-SUBST-3) `repl`/`s`/`sg`/`serr`
  — is ambiguous to a line-oriented, first-token-dispatching parser
  unless [DD-13b] either reserves those words as illegal names or picks a
  syntax where a name can never be mistaken for a directive (a sigil, a
  required delimiter, a distinct keyword introducing a definition). Not
  evidenced as a current problem — nothing today defines names — but the
  risk is structural, grows with every directive this note's own R-SUBST-3
  and R-VE-12 add to the reserved-word list, and is cheap to flag before
  [DD-13b] commits to a grammar.
- **Whether the `ref`/label mechanism (R-VE-6/D39 addendum) should be a
  file-path-like string, a dotted path, or something else** is,
  similarly, [DD-13b]'s to sketch; this note states only that a slot for
  it must exist.
- **[M3.1]'s chunk-boundary tests are a future case SHAPE this note did
  not survey (R27 F4).** `docs/dev/plan.md` [M3.1]: "*_stream_* API for
  the DFA engine, chunk-boundary tests" — not-started, scheduled after
  M6, no design note exists yet. A streaming match call is fed the
  subject in pieces across multiple calls; a chunk-boundary case needs to
  assert something about state AS OF a boundary partway through a
  sequence of calls, not just a final span from one call. Today's `m`/
  `n`/`ms`/`ns` model is one call against one whole subject. Flagged only
  so [DD-13b] does not shape the case-expectation grammar in a way that
  forecloses a later multi-call case kind — no requirement is stated,
  because nothing in the repo yet specifies what such a case should look
  like.
- **[DD-11]'s newline-convention axis has no candidate `.rxt`-level
  directive spelling anywhere in the repo (R27 F4).** Checked
  `docs/pcre2_options.md`, `docs/testing.md`, and `docs/dev/decisions.md`
  directly: every mention of DD-11 describes the PCRE2-SIDE mechanism
  only (the start-only `(*CR)`-family verbs, or a compile-context API
  option) — none proposes a test-format directive. [DD-11] is itself
  not-started. The same caution as the M3.1 bullet applies one level
  removed: once DD-11 lands, blocks will presumably need a way to select
  a newline convention the same way they select `flags`/`features`
  today (block-scoped, non-carrying, per R-RXT-1) — flagged as a future
  axis the format's config-scoping mechanism (OD-1/T-4) should not
  accidentally foreclose, not as a requirement, since nothing in the
  repo yet specifies its shape.
