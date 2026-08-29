# The .rxt format, grown — use cases first, then an outline, then how it is used

Manager's evaluation for Frank, 2026-08-28 (forty-fourth session), on his
ask: "I'd like to see a set of use cases then an outline and how it'd be
used. I heard of a directory format but I'm not buying it. Evaluate on use
cases, flexibility, over complicated, whatever else." This is a position
paper, not the [DD-13b] design note — it proposes the SHAPE and names the
rulings the design note would then build under. Inputs: today's
`docs/spec/rxt_format.md` (178 files, 3,262 blocks, ~10k expectation
lines, every one oracle-verified); `requirements.md` in this directory
(the [DD-13a] survey: consumers, tensions T-1..T-6, anti-requirements
AR-1..AR-7, OD-1..OD-5); `frank_inputs.md`; pcrec-bench
`docs/design/requirements.md` §4.5/§5 (the sub-bench DIRECTORY + sidecar
model); the [LIB] and [V-E] plan rows.

## 0. The answer in six lines

1. `.rxt` stays a flat, line-oriented file of blocks. Every existing file
   is valid, unchanged in meaning (AR-1). Nothing new is required to write
   the files people write today.
2. Growth is a handful of NEW LINE KINDS, orthogonal, each answering one
   use case: `name`/`target`/`lib` (composition), `include`/`@file:`/`mc`/
   `tag` (large and generated sets), `config`/`use`/`variant`/`oracle`
   (per-engine and per-build application). Ten additions, staged in three
   waves by demand; wave 1 alone unblocks [LIB].
3. A library, a module corpus, a bench sub-bench, and a user's own pattern
   file are the SAME KIND OF FILE. One parser; the harness and `pcrec`
   both read it.
4. The DIRECTORY stays an organizing convention (where files live, a
   CLAUDE.md/NOTES.md, a generator script beside its output). It is NOT a
   format: no sidecar schema, no role-by-filename, nothing a tool has to
   understand about a directory to run one file. The sidecar's fields
   become lines in the file, next to the pattern they describe.
5. Composition uses PCRE2's own spelling — `(?&name)` — and the file
   supplies what PCRE2 would need `(?(DEFINE)…)` for. The oracle sees the
   EXPANDED plain PCRE2 pattern, which makes the harness's expansion the
   splice-vs-linkage control by construction.
6. Scoping stays two-level: file-top declarations (`lib`, `include`,
   `use`, `tag`, `oracle`) and block-scoped lines that reset at each
   `pattern`, exactly as today. No section scope, no case scope. Cascade
   exists in ONE place — `config … from …`, ordered, last wins.

## 1. Use cases — who, what they type, what must be true

| # | who / consumer | the situation | what must be true |
|---|---|---|---|
| U1 | module test author (today) | `tests/<module>/x.rxt`: pattern blocks with `m`/`n`/`perr`/`g`; `make test` | unchanged, byte for byte; ~10k verified lines never re-verified (AR-1) |
| U2 | D27 blinded author | writes from the spec, denied `src/` and `tests/`; a file must be readable with no cross-file context | a block's meaning is local; anything file-level is at the TOP and visible (AR-4) |
| U3 | generator / machine sets | a script emits 3,000 blocks; a hand-written file wants them run without carrying them inline | `include` splices a file's blocks; summary unit = the include closure, failures still print the real `file:line` (T-6) |
| U4 | [DD-14] composite pattern | `local`, `domain` defined; `email = ^(?&local)@(?&domain)$`; parts tested on their own; only `email` ships | three users per definition — reference / test / target (OD-4); a tested part is compiled as a TEST artifact, not a deliverable |
| U5 | [LIB] shipped library | `lib/rfc5322.rxt` carries definitions + their tests; a user file `lib`s it and writes `(?&email)` | names resolve file-first then libraries in order, collisions refused by name; a `lib`'d file contributes NO targets and its tests are not re-run by the includer |
| U6 | [V-E] multi-config build | one source, an AVX2 build and a baseline build; or captures-on and captures-off | a `config` is a named set of pcrec options; a block or file that `use`s two configs is two compiled units |
| U7 | pcrec-bench sub-bench | canonical pattern(s) + subjects + expectations with method + objective/hazard/size/role tags + per-testee options and declared variants + regimes | all of it expressible IN the file beside the pattern; a testee is a `config` like any other (pcrec is not special, frank_inputs pt 2) |
| U8 | large subjects | a 1 MB log; the useful expectation is a find-all COUNT and a first span | `@file:path` subject spelling, read byte-exact (T-5); `mc` count line |
| U9 | oracle options | a block needs `re.MULTILINE`, or libpcre2 rather than python, or is not oracle-checkable | `oracle` line per file or block; `# pcre2-only` stays as an alias of `oracle pcre2` |
| U10 | [V-G] end user | tests their own pattern with pcrec's harness; no pcrec internals | same file, same harness entry; nothing pcrec-specific is needed to write cases (AR-6) |
| U11 | [V-F]/[M4-SUBST] | transformer target, substitution templates | noted; ride on `name`/`target`/`config`; no line kind of their own in this note |

Two consumers set the hard constraints: U1/U2 (the format must stay
trivially local and unchanged) and U4/U5 (it must carry named
definitions with three kinds of user). Everything else is a line kind
or two.

## 2. Outline — the additions, grouped by the use case that earns them

Conventions carried from today: whole-line `#` comments only; a line
kind is its first word; unknown line kinds are hard errors; block-scoped
lines reset at each `pattern`; file-level lines are only legal BEFORE
the first `pattern` (so a D27 reader sees them at the top, U2).

### Wave 1 — composition (earns [LIB]; [DD-14]'s multi-pattern files)

- `name <ident>` — block-scoped, at most once: names this block's
  pattern as a definition. `<ident>` is a PCRE2 group name
  (`[A-Za-z_][A-Za-z0-9_]*`), unique per file after `lib` resolution.
- `(?&name)` INSIDE a pattern, PCRE2's spelling, resolves to a `name`d
  block: this file's own names first, then `lib`s in order; a name
  defined twice across that search is REFUSED by name (never shadowed).
  No new in-pattern syntax at all (OD-5 answered: PCRE2's spelling, not
  our own). A pattern's OWN groups keep priority over libraries.
- `lib <path>` — file-level: makes `<path>`'s definitions referenceable.
  Contributes no targets, runs none of its tests (they run when the
  library file itself is under test). Transitive `lib` is allowed;
  cycles refused.
- `target` — block-scoped marker: this block is a compilation target
  for the build reader. Default rule: an UNNAMED block is a target (so a
  one-block file behaves exactly like `pcrec 'pattern'` — AR-2/AR-7); a
  NAMED block is reference+test only unless it says `target`. Test
  compilation is unaffected — the harness compiles every block with
  cases, as today; `target` only speaks to `pcrec --source`.
- Oracle: the harness EXPANDS `(?&name)` references into a plain PCRE2
  pattern (a `(?(DEFINE)(?<name>…))` prefix, or inlining — the design
  note picks; both are PCRE2) before handing it to python `re`/libpcre2.
  The expanded text is also what `A == B` splice-vs-linkage controls
  compare against ([DD-14.G]'s bar).

### Wave 2 — large and generated sets (earns bench sub-benches, D27 sets)

- `include <path>` — file-level: splices `<path>`'s BLOCKS as if written
  here (its tests run; its targets are targets; its file-level lines
  are refused — an included fragment is blocks, not a file with a
  head). Summary lines report the include closure under the entry
  file's name; every failure keeps its own `file:line`.
- `@file:<path>` as a subject: `m @file:big.log 12 40`, `n @file:x`,
  usable wherever a `"…"` subject is. Read as bytes, no newline/encoding
  transformation, NUL-safe (T-5 — the driver already avoids `strlen`).
  Paths are relative to the file that names them.
- `mc <subject> <count>` — asserts the find-all total over the subject
  (restart semantics per match_api §3.1). The bench's throughput regime
  is timing, not expectation — that stays the bench's.
- `tag <key>=<value>` — file-level or block-scoped, repeatable. Free
  vocabulary; the harness only checks well-formedness. The bench's
  sidecar fields become tags: `tag objective=subroutines`,
  `tag hazard=catastrophic`, `tag size=large`, `tag role=floor`,
  `tag regime=search-short`. (Sidecar schema v1.3's fields map 1:1 —
  this is the "absorbs them mechanically" the bench's R6 asked for.)

### Wave 3 — per-engine and per-build application (earns bench testees, [V-E] configs, OD-1..OD-3)

- `config <name>` — starts a CONFIG block (a block kind beside
  `pattern`), whose lines are pcrec-option lines already in the format
  (`flags`, `features`, `engine`, `budget`) plus `pcrec <raw flags>`
  (e.g. `-fno-premul-table`, `--unroll=1`, `-march=…` via `cc`; the
  emitted-size limits' raise-only overrides `--max-emit-bytes=N` /
  `--max-emit-code-bytes=N` belong HERE — per target, declared beside the
  pattern, D84 addendum 3), and
  bench-facing `testee <engine>[/<version>]` + `option <k>=<v>` lines
  for a non-pcrec engine. `config <name> from <other>` inherits then
  overrides, in order — Frank's cascade, and the ONLY cascade in the
  format (T-4 resolved: block resets stay the default; cascade lives
  only inside `config`).
- `use <config>[,<config>…]` — file-level or block-scoped: run/compile
  under each named config, one cell per config. No `use` = today's
  single default cell. A config's pcrec options and a block's own
  `flags`/`features` compose block-wins (the block is more specific).
- `variant <testee> <pattern-text>` — block-scoped: the DECLARED
  per-engine re-spelling of the canonical pattern, beside it in the
  file, never in a sidecar (R-BENCH-7, T-2/AR-5: a variant is visible
  or it is a fork). Optional `groups <name>=<n>,…` after it for capture
  correspondence by NAME (T-3/AR-6: engine-neutral). Constraint 1 of
  bench §4.5 is mechanical: the variant is checked against the block's
  own expectations; a difference invalidates the cell. Constraint 2
  (objective preserved) is a review obligation stated in a comment —
  the format cannot check it and should not pretend to.
- `oracle <method>` — file-level or block-scoped: `python` (default),
  `pcre2`, or `none <reason>` (counted skip, AR-3). `# pcre2-only`
  before a `pattern` remains accepted and means `oracle pcre2`.

That is the whole grammar: ten line kinds over three waves. Each wave
ships only when its consumer is real (D77): wave 1 when [LIB]/[DD-14]
files need it; wave 2 when the first sub-bench is authored in-format;
wave 3 when the bench has a second testee to declare or [V-E] a second
build config. No parser is written before the design note and its panel
([DD-13b.panel]).

## 3. How it is used — three worked files

### 3a. A library and a user of it ([LIB], U4/U5)

`lib/rfc5322.rxt`:

```
# RFC 5322 address pieces. Definitions are private; `email` is the only target.
tag objective=subroutines

pattern [A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*
name local
m "john.doe" 0 8
n ".john"

pattern (?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}
name domain
m "example.com" 0 11

pattern ^(?&local)@(?&domain)$
name email
target
m "john.doe@example.com" 0 20
n "john.doe@"
```

A user's `mail.rxt`:

```
lib lib/rfc5322.rxt

pattern From: (?&email)
m "From: a@b.co" 0 12
```

- `make test` on `mail.rxt`: the harness resolves `(?&email)` →
  `(?&local)`/`(?&domain)`, expands to plain PCRE2 for the oracle,
  compiles the block, runs its two cases. The library's own tests do
  not run here.
- `pcrec --source mail.rxt -o mail.c`: one target (the unnamed block),
  one artifact, byte-identical to `pcrec 'From: ^…$'` hand-inlined —
  [DD-14.G]'s bar. `pcrec --source lib/rfc5322.rxt -o email.c` emits
  `email` only. Multiple targets in one source → one `.c` per target
  by default; a single multi-pattern UNIT is [V-E]'s charter, not the
  format's.

### 3b. A bench sub-bench as one file ([B11.4] bounded repeats, U7/U8)

`bench/bounded/bounded.rxt`:

```
tag objective=bounded-repeat
tag regime=search-long
oracle pcre2
include gen/cases.rxt          # 400 generated blocks, committed with gen/make_cases.py

config pcre2-jit
  testee pcre2/10.42
  option jit=on
config pcrec-nopremul from pcrec
  pcrec -fno-premul-table
use pcrec, pcrec-nopremul, pcre2-jit

pattern @
tag role=floor
mc @file:subjects/log1m.txt 41200

pattern \b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b
tag hazard=none size=medium
variant re2 [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}   # re2 has no \b in this mode; declared, reviewed
m @file:subjects/log1m.txt 118 154
mc @file:subjects/log1m.txt 3117
```

The directory `bench/bounded/` still exists — `NOTES.md`, `gen/`,
`subjects/` live there — but no tool reads the directory as a schema.
The bench runner opens `bounded.rxt`; the record keys a cell by
(file, block, config), which is a stable identity a person can find by
`file:line`.

### 3c. Two build configurations from one source ([V-E], U6)

```
config baseline
  pcrec --no-captures
config avx2 from baseline
  pcrec --simd=avx2
use baseline, avx2

pattern (?i)error|warn|fatal
target
m "an ERROR here" 3 8
```

`pcrec --source log.rxt --config avx2 -o log_avx2.c` — one config, one
artifact; the harness runs the block's cases under both configs as two
cells, and identity between them is a free control.

## 4. Evaluation — the directory model vs the grown file

What the bench's directory model actually carries: a goal statement,
canonical patterns, a subject generator with a manifest, expectations
with method, tags, per-engine notes/options/variants, regimes, a version
snapshot. Of these, only the GENERATOR SCRIPT and the NOTES are not
naturally lines in a pattern file — and those are files that sit beside
one, not a format.

| criterion | directory + sidecar | grown `.rxt` |
|---|---|---|
| use-case coverage (U1-U10) | U7 only, by design; U4/U5/U6 need something else anyway | all ten, one file kind |
| flexibility | each new field is a schema change in a second grammar | each new need is a line kind; unknown tags are free |
| identity of a case | a pattern keyed across two files (block index or an ID column) — the population-nobody-counts hazard (K35, check-design lessons) | `file:line`, one file |
| authoring / D27 (AR-4) | cross-file context by construction | local; file-level lines at the top |
| tooling | a directory reader + sidecar parser + `.rxt` parser | one parser, shared by harness and `pcrec` |
| what it is good at | prose, generators, snapshots | patterns, cases, declarations |
| complexity budget | two grammars, three conventions (role by filename) | ten line kinds, staged |

Verdict: keep the directory as a CONVENTION (organization, discovery,
NOTES.md, a generator beside its output — exactly what `tests/<module>/`
already is), and put every declarative field in the `.rxt` beside the
pattern it describes. Drop the sidecar; its schema v1.3 fields become
`tag`/`variant`/`config` lines. A "sub-bench directory" is then a
directory that happens to contain one entry `.rxt` — the bench's record
keys on the file, which is what it should key on anyway.

Where I would push back on the accumulated inputs (over-complication):

- **Four scoping levels** (file/section/pattern/case, OD-1's open
  question): no. Two levels — file-top and block — plus `config` as the
  one cascading thing. A case-level option has no consumer in the
  survey; a section scope is what `include` + `use` already give.
- **Options cascade across ordered `include`s** (frank_inputs pt 2, as
  literally stated): the cascade belongs in `config … from …`, not in
  include order. Making an include's POSITION change the meaning of a
  later block is exactly the cross-file context AR-4 forbids, and it
  makes `include` two things at once. The intent — "for python3.x,
  include these files in order, then add options" — is met by a config
  chain, with `include` staying pure splice.
- **A test-only compiled surface as a distinct concept** (T-1/OD-4): no
  new concept. A named block with cases is compiled by the harness as a
  test artifact, as every block is today; `target` is a separate,
  build-only bit. Testability never implies target-ness.
- **Our own reference spelling** (OD-5): no. `(?&name)` is PCRE2's, the
  oracle understands it after expansion, and nothing in the file is
  outside PCRE2's alphabet except the line kinds.
- **The variant's "objective preserved" statement as a checked field**:
  it is a review obligation; the format records it (a comment or
  `tag variant-note=…`) and does not pretend to verify it.

Risks the design note must carry, not this paper: `include` closures
and the summary unit (T-6 — proposal above: entry-file name, per-file
lines kept); byte-exactness of `@file:` (T-5 — the driver's existing
discipline extended to a file read); `config` composition with a block's
own `flags` (block wins — stated, needs a table in the spec); name
collision rules across `lib` chains (refuse, never shadow — stated);
and R-COMPAT-1 proven by running the whole existing corpus through the
new parser with zero diff in results.

## 5. What I would ask Frank to rule (the design note builds under these)

1. Flat file, directory as convention, sidecar dropped — the shape above.
2. PCRE2's `(?&name)` as the reference spelling; the file supplies the
   definitions (OD-5).
3. Defaults: unnamed block = target; named block = reference+test unless
   `target`; a `lib`'d file contributes no targets (OD-4).
4. Two scopes only (file-top, block); cascade only inside `config … from`;
   `include` is pure splice (OD-1/OD-3, T-4).
5. Waves shipped by demand: 1 (composition) → 2 (sets) → 3 (configs);
   wave 1 is what [LIB] and [DD-14]'s multi-pattern files wait on.
6. Multi-target source emits one `.c` per target; the single multi-pattern
   unit stays [V-E]'s question.

If these hold, [DD-13b] is: the grammar for the ten line kinds in
`docs/spec/rxt_format.md` (a dialect section, existing text untouched),
the resolution/expansion semantics, the summary-unit rule, and the
migration story (none — no existing line changes meaning), then the
[DD-13b.panel] and a parser in the harness first, `pcrec --source`
second.

## 6. Frank's follow-ups (2026-08-28, same evening) — folded in

**6.1 Local vs library resolution — C's `""` vs `<>`.** Yes, and it is a
separate axis from the VERB. `lib`/`include` say what the file
contributes (definitions vs spliced blocks); the PATH SPELLING says where
to look:

- `lib "lib/rfc5322.rxt"` — relative to the file that names it (local).
- `lib <rfc5322>` — searched on the library path: pcrec's shipped store
  ([LIB] (3)) plus `--lib-path DIR` entries in order, the `-I` model;
  `.rxt` is implied. Never relative to the including file.
- The same two spellings work for `include`. `@file:` subjects are
  always local (quoted spelling only — a subject is data, never a
  library).
- A name reached both ways is the same file if it resolves to the same
  path; two different files defining one name are refused by name, as
  §2 wave 1 already says.

**6.2 A target needs a NAME for reference — the emitted prefix.** Agreed;
§2's "unnamed block = target" was too thin. A target is what a caller
links, so it needs the C-identifier the artifact is emitted under
(`-p rx` today → `rx_search`, `rx_match`, `RX_NCAPS`…). Rule:

- `target [<prefix>]` — the block is a compilation target emitted under
  `<prefix>`. `target` alone uses the block's `name` as the prefix (a
  PCRE2 group name is a valid C identifier). A block with neither
  `name` nor a `target` argument, in a file with exactly one target,
  gets `rx` — today's single-pattern behaviour; the CLI's `-p` still
  overrides for that case.
- Two namespaces, deliberately: `name` is the PCRE2 reference name
  (`(?&local)`), `target`'s argument is the C prefix. They coincide by
  default and may differ (`name email` / `target rfc5322_email`).
- `pcrec --source file.rxt --target <prefix> -o out.c` selects by
  prefix; two targets with one prefix in an include closure are refused.
- Tests keep addressing blocks by `file:line`; the prefix is for the
  BUILD reader and the record (a bench cell keyed by `(file, prefix,
  config)` is more stable than a block index — this also answers the
  "identity of a case" row in §4's table for target blocks).

The ruling list in §5 gains: 7. path spelling `""` local / `<>` library
path; 8. `target [<prefix>]`, defaulting to `name`, `rx` for the lone
unnamed target.

**6.3 "Prefix in the C file, or name in the `rx_info` structure."** Both,
and they are two identities with two consumers. The PREFIX is the
link-time identity (`<prefix>_search`, `<prefix>_info` — the symbol a
caller links, unique per translation unit). `rx_info` today carries
`.pattern`/`.pattern_len` but no name; it gains **`const char *name`**
(runtime identity: what [V-E]'s finder, a bench record, or a debugger
prints — a `.rxt` `name`, not a C symbol). Defaults keep them equal:
`target` alone → prefix = name = the block's `name`; but they may
differ, and the case where they must is exactly U6: one target
`email` built under two configs is two artifacts `email_avx2_*` /
`email_base_*` whose `rx_info.name` is `"email"` in both. An unnamed
lone target has `name == "rx"` (the prefix) so no artifact ever carries
a NULL name. Adding the field is an `abi` bump under D76's ritual
(bump + re-pin + spec hunk in one change) and rides wave 1's first
landing, not a separate event. Ruling list item 8 is amended
accordingly: `target [<prefix>]`; `rx_info.name` = the block's `name`
(or the prefix when unnamed).

**6.4 Separate the TARGET spec from the PATTERN spec** (Frank: "there is
a set of lib patterns I want to include in my compiled file but I want
to specify the options for them; I may want the same pattern under
different options — simd x86, simd on a different cpu"). Yes — and this
SUPERSEDES §2 wave 1's block-scoped `target` marker and §6.2/§6.3's
defaults. A target is its own file-level declaration, a triple:

```
target <prefix> = <name> [with <config>[,<config>…]]
```

- `<name>` is any pattern in scope — this file's or a `lib`'d one. So a
  user file that `lib`s a library and declares targets for three of its
  patterns, under the user's own configs, ships exactly those three;
  the library file itself declares no targets and needs no knowledge of
  the user's options.
- The same pattern may be named by several targets:
  `target email_avx2 = email with avx2` /
  `target email_base = email with baseline` — two artifacts, one
  pattern, `rx_info.name == "email"` in both (§6.3), prefixes distinct
  (a duplicate prefix in the include closure is refused).
- `with` names a `config` (§2 wave 3); absent, the default options.
  Composition is one rule: target config over block-scoped
  `flags`/`features` over defaults — the more specific wins.
- Pattern blocks carry NO target marker at all. A block's `name` is its
  only identity; whether and how it is built is the target list's
  business. This is the cleaner cut for U2 (a D27 author never writes
  build declarations) and for [V-E] (the target list IS the manifest —
  one line per artifact, all at the top of the file).
- The harness TESTS every declared target as a cell (pattern's cases ×
  the target's config), so `use` (§2 wave 3) is only for testing a
  config nobody ships; it may turn out unnecessary and is the first
  line kind to drop if so.
- Compatibility default: a file with no `target` line and exactly one
  UNNAMED block is `target rx = <that block>` — today's
  `pcrec 'pattern'`; every other file builds nothing unless it says so.
  `pcrec --source f.rxt --target <prefix>` selects; no `--target` with
  several declared builds them all, one `.c` each (§5 item 6).

§3a's user file becomes `lib "lib/rfc5322.rxt"` / `target mail_rx = …`
over an inline `name`d block; §3c collapses to two `target` lines over
one config pair. Rulings 3 and 8 in §5 are REPLACED by: **a target is a
file-level `target <prefix> = <name> [with <config>…]` declaration;
pattern blocks carry no build marker; the lone-unnamed-block file is
`target rx` by default.** Item 6's "one `.c` per target" stands.
