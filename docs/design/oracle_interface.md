# The oracle interface and the answer store — design note

**PROPOSED, NOT PANELED.** Lane `oraiface`, 2026-09-10. Scope per Frank's
directives (`docs/dev/wake.md`'s lane-3 spec, 2026-09-09 late) and D77: this
note designs the interface and the store; **it builds neither**. No code
lands from this lane. The manager runs a D6 panel on this note; the uprops
instance (the store's first real customer) builds only after the panel's
dispositions.

## 0. The charter, verbatim

Two directives, both Frank's, both 2026-09-09 late:

> "the oracle isn't going to give different results at different times —
> cache results and only consult for new questions"

> "think of the interface so that all oracles can follow it and be
> interchangeable"

The committed anchor points from the wake.md spec: `OracleId = (name,
version, config)` as the store's outer key; `Question` a small closed
kind-set aligned with the `.rxt` cell vocabulary, canonically serialized,
hashed to the store key; `Answer` kind-specific and byte-stable; the adapter
contract is `answer(BATCH)` plus a per-oracle capability declaration
(batch-first, since the ssh reference's stdin-payload method is the
contract's own native shape); **only the oracle side caches** — pcrec
computes fresh every run, which is the store's whole safety property
(`docs/dev/learnings.md` §3: a store no check-under-test can write); the
reference-version store is COMMITTED, local-version caches are gitignored;
first customers are the uprops whole-space sweeps (the S-U6/S-U9 closing
witnesses ride it), then the C3 python oracle, then the PC-3 probe families;
`.rxt` expectations gain formal provenance as a dividend, not a requirement
of this design.

## 1. Survey: every existing oracle consumer, and what it asks

This section reads the tree as it stands (worktree branch point `9e436d31`)
rather than assuming a shape. Every consumer below is a candidate adapter or
a store consumer; §9 orders them into a migration ladder. None of the
mechanisms below are being changed — the survey is read-only, per this
lane's box.

### 1.1 `tests/harness/verify_rxt.py` — the C3 default oracle (python `re`)

In-process (`import re`), one call per `.rxt` case, driven straight off the
parsed directive stream (`compiled.search(subj, p)`, `match.span(slot)` —
`tests/harness/verify_rxt.py:1026,1056,1084,1114,1139`). Asks exactly two
question shapes: **match-at** (`m`/`n`/`ms`/`ns`) and **captures**
(`g`/`gp`). No external process, no version drift to speak of (python's `re`
ships with the interpreter pinned by the box's own python3), so the caching
dividend here is near zero — the whole point of an in-process pure-python
call is that it is already as cheap as a cache hit. It is still in scope for
the ADAPTER side of this design (§6), because "all oracles interchangeable"
is exactly the property that lets a differential compare python-`re` against
libpcre2 through the identical Question/Answer shape instead of a bespoke
comparator, which is what `docs/spec/rxt_format.md`'s own oracle-exclusion
catalogue (the `# pcre2-only` marks) is doing by hand today.

### 1.2 `tests/registry/pcre2_check.c` (PC-3) — the registry against libpcre2

Direct-linked (`tests/fuzz/pcre2_abi.h`, D98/[ORACLE-LINK]), in-process C, no
subprocess per probe. Every question is **compile-accept**: `pcre2_try(pat,
len, msg, sizeof msg)` (`tests/registry/pcre2_check.c:105`) returns 0-or-error-
code-plus-message, no matching at all — "PC-3 compares compile VERDICTS
only" is the file's own header. Eight independent sweeps share this one
primitive (`check_rows`, `check_verb_names`, `check_class_brackets`,
`check_class_delim_bytes`, `check_posix_names`, `check_posix_positions`,
`check_option_runs`, `check_group_tails`, `check_gated_uprops_space`), and
the populations are large and EXACT: `check_posix_positions`'s POSIX-class
probe count is pinned per resolved oracle version (**149,804** probes at
10.46, `pcre2_check.c:1666`), and `check_gated_uprops_space` sweeps every
name pcrec's own table holds — **1,053** names across three namespaces
(`tests/uprops/CLAUDE.md`). This is the largest compile-accept population in
the tree and the one for which Frank's caching remark is most directly
true: every probe is a fixed string, `options` is pinned at 0 project-wide
("ALL COMPILES USE options = 0 — no PCRE2_UTF, no PCRE2_UCP, no
PCRE2_CASELESS", `pcre2_check.c`'s own header), and the answer cannot change
until the resolved library version changes.

### 1.3 `tests/registry/pc4_check.c` (PC-4) — the semantic differential

Same direct-link binding, same in-process C, but drives `pc4_driver.c` as a
**subprocess-per-pattern** to run the accepted patterns against the shared
subject set (`pc4_subjects.h`, embedded by both sides). Asks **compile-
accept** (both directions — over-acceptance and over-rejection) then
**match-at** for every both-accept pattern over every subject (leftmost
search from startpos 0). Population is EXACT and derived, not counted: 273
patterns, 41 refusals, 232 accepted × 271 subjects = **62,872 cells**
(`pc4_check.c`'s own header comment). `mlimit` (a PCRE2 backtracking-budget
stop) is asserted zero on this backtrack-free space rather than treated as a
third verdict — worth naming here because a real match-limit population
elsewhere would need the **giveup** answer variant §5 defines.
`tests/registry/definitions_oracle_check.c`/`_driver.c`/`_gen.c` are the same
shape one table over (A==C leg against libpcre2, `definitions_oracle_
check.c:1-45`) and would migrate identically.

### 1.4 `tests/uprops/uprops_oracle.c` + `uprops_compare.py` — the FIRST
NAMED CUSTOMER

Direct-linked, in-process C (`uprops_oracle.c`), but the question shape is
distinct from everything else in the tree: **membership**. One call sweeps
the WHOLE code-point space for one property (`uprops_oracle --version` for
version reporting; `uprops_oracle {byte|utf8} NAME...` for the sweep,
`uprops_oracle.c:93-159`) via one find-all pass over a subject that IS every
code point in order, printing the member set as ascending intervals
(`NAME lo-hi lo-hi ...`) — exactly the shape `uprops_sweep.c` prints for
pcrec, so the comparator needs to know nothing about either producer. The
byte-encoding population is **91 properties** (measured, `tests/uprops/
CLAUDE.md`, post-[ORACLE-LINK] re-measurement); the utf8-encoding population
is **45 categories + 171 scripts × 2 swept namespaces (bare/scx=, sc=) =
387 properties** (derived from `run_uprops_tests.sh`'s own `CATEGORIES`
and `script_values()` counts, not independently re-measured here — flagged
as an item for the migration lane to confirm against a real run). This is
the population Frank named directly ("the uprops whole-space sweeps") and
the one currently blocked on a real constraint the store dissolves: the
byte arm runs cheaply against whichever local libpcre2 the box resolves
(Homebrew 10.48 here), but the EXACT arm against the pinned 10.46 reference
cannot run as a normal `make test` step — `docs/dev/lanes/BOILERPLATE.md`'s
own rule is light ssh probes only, never suite runs, on the reference box —
so it is a manual, one-off, currently-owed measurement (wake.md: "the STAGE-5
10.46 EXACT arm ... OWED to I-63"). A committed answer store turns that one-
off measurement into a permanent asset instead of a debt that recurs every
time someone wants the exact number.

### 1.5 `tests/backrefs/bref_oracle.py` + `bref_batch.c`, and its borrowers

`bref_oracle.py` is **the same oracle the rest of the tree uses, not a
second one** — its own header says so: it is a thin wrapper over
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`, the project's
committed ctypes binding to the installed libpcre2-8 runtime. Two other
modules build on it directly rather than re-implementing: `docs/design/
lookaround_measurements/probes/la_oracle.py` (`import ... br_oracle`) and
`docs/design/utf8_measurements/probes/u8_oracle.py` (same chain, one level
further). `tests/atomic_groups/atomic_oracle.py`/`atomic_batch.c` and
`tests/recursion/run_recursion_diff.sh` (which explicitly reuses `bref_
oracle.py`/`bref_batch.c` rather than a third copy) are the same shape.
Every one of these asks **match-at** + **captures** together, already
BATCHED — `bref_batch.c`'s protocol reads `<subject-file>\t<startpos>` on
stdin and writes one result line per input line, explicitly because "one
process per cell makes a sweep of this size subprocess-bound by two orders
of magnitude" (`bref_batch.c`'s own header, citing `atomic_batch.c`'s
measurement). This whole family is the tree's existing, working precedent
for what an adapter's batch call should look like: a `(pattern-id, subject,
startpos)` triple in, a `(verdict, group-spans)` tuple out, one process per
`(pattern, arm)` rather than per cell.

### 1.6 `tests/fuzz/pcre2_oracle.c` — the ONE unbatched shape

A minimal CLI oracle, one process per `(pattern, subject, startpos)` call
(`pcre2_oracle 'PATTERN' subject-file [startpos]`, one line of output). Used
by the fixed-seed capturediff gate and by `tests/assertions/run_kreset_
diff.sh`/`run_gstart_diff.sh`/`run_mline_diff.sh` for constructs (`\Z`,
`\G`, `\K`, multiline `^`) that need the match-here question no ctypes
binding here answers directly. Same question shape as §1.5 (**match-at** +
**captures**, per its own header's group-span protocol) but the WEAKEST
transport fit of anything surveyed — one process per call is exactly the
anti-pattern `tests/harness/`'s own `HARNESS_BATCH` axis exists to retire on
the compile side. It is named here because it would benefit the most from
being wrapped in a batch-first adapter, not because this lane proposes
touching it.

### 1.7 `tests/fuzz/fuzz.py` + `fuzz_driver.c` — the fuzzer differential

Same direct-link/ctypes-family access, but the QUESTION POPULATION is
randomly generated per run (seeded for `make test-capturediff`'s fixed-seed
slice, unseeded for the manual `make fuzz` campaign). Asks **compile-accept**
+ **match-at** + **captures** together. A poor caching candidate for the
open-ended campaign (each run explores new pattern space, so a cache would
mostly miss); the FIXED-SEED slice is deterministic and would get real
value, though at low priority — it is already fast and already in `make
test`.

### 1.8 `docs/design/utf8_measurements/probes/bundle.py` + `archive.sh` —
the REMOTE reference-oracle transport

**The one lane in the tree whose oracle runs on another machine as a matter
of design, not of convenience.** libpcre2 10.46 (the project's pin) lives
only on the reference box; every other consumer above resolves whatever
local library the box has. `bundle.py` embeds the borrowed oracle chain
(`pcre2_ctypes.py` → `br_oracle.py` → `u8_oracle.py`) verbatim as `repr()`
of each file's source plus an `importlib` shim, so the WHOLE program travels
on **stdin** and nothing is written on the far end — `archive.sh`'s own
comment: `ssh -o ConnectTimeout=10 -o BatchMode=yes $OLDBOX 'python3 -'`.
This is the mechanism the wake.md spec names as "the native shape" for a
batch adapter, and it already IS one: one ssh round trip, one payload, one
run, one printed transcript — batch-first by construction because a light
ssh probe cannot afford a round trip per question. §6 generalizes this
exact shape rather than inventing a new one.

### 1.9 `docs/pcre2_compliance.md`'s independent survey — explicitly NOT a
customer

Named here to rule it out rather than to omit it by accident. `[DOC-DRV]`'s
whole architecture (`docs/CLAUDE.md`'s entry on the file) is a hand-written
survey held in CHECKED TENSION against the generated registry index,
"deliberately never generated from the registry, since its value is
answering 'what does PCRE2 have that the registry doesn't even list'."
Folding it into a cached-oracle pipeline would collapse the very
independence the tension check exists to verify. §10 restates this.

## 2. The question kind-set

Five kinds, aligned with `docs/spec/rxt_format.md`'s own directive
vocabulary (`pattern`/`perr`, `m`/`n`/`ms`/`ns`, `g`/`gp`) but not a bare
1:1 mapping onto it — two kinds below (`name-accept`, `membership`) answer
questions no single `.rxt` cell asks, because their whole value is asking
about a NAME or a WHOLE SPACE rather than one pattern text. Every kind's
fields are named exactly, because §4's hash needs a closed, ordered field
list per kind — an open-ended "extra options" bag would make the
serialization non-canonical by construction.

1. **`compile-accept`** — "does this pattern text compile under this
   oracle's config?" Fields: `pattern` (raw bytes, PC-3/PC-4's own
   population). Answer: accept, or reject with an error identity (§5.1). The
   `.rxt` cousin is `perr` (which asserts only the pcrec side of this
   question — no `.rxt` directive exists for asking an EXTERNAL oracle to
   reject a pattern; PC-3 is where that question lives today).

2. **`match-at`** — "searching this subject from this byte startpos, does
   this pattern find a match, and where?" Fields: `pattern`, `subject` (raw
   bytes), `startpos` (non-negative integer). Answer: match(start, end),
   nomatch, or giveup(code) (§5.2). Direct cousin of `.rxt`'s `m`/`n`/`ms`/
   `ns`.

3. **`captures`** — "for the match found by the corresponding match-at
   question, what are group k's slot bounds, for every k?" Not
   independently askable — it always accompanies a `match-at` question over
   the same (pattern, subject, startpos) and reports one row per requested
   slot count (padded with the unset sentinel past whatever the oracle
   actually captured — `bref_oracle.py`'s own padding rule, §5.3). Direct
   cousin of `.rxt`'s `g`/`gp`.

4. **`name-accept`** — "is this NAME a member of this NAMESPACE, according
   to this oracle?" Fields: `namespace` (a closed, adapter-declared
   vocabulary — `uprops-category`, `uprops-script-bare`, `uprops-script-sc`,
   `uprops-script-scx`, `verb`, `posix-class`, …), `name` (the bare
   identifier, e.g. `Greek`, `MARK`, `alpha`). This is deliberately its OWN
   kind rather than a `compile-accept` question over a synthesized probe
   string (`\p{Greek}`, `(*MARK)`, `[[:alpha:]]`), for three reasons: (a)
   the synthesis template is oracle-and-namespace-specific and belongs in
   the adapter, not in every caller that wants to ask about a name; (b) a
   `(namespace, name)` key is directly diffable across oracle versions ("did
   libpcre2 gain `\p{Kawi}` between 10.46 and 10.48") in a way a raw pattern
   string buries inside itself; (c) it matches how the tree already asks
   this question — `check_verb_names`, `check_posix_names`,
   `check_gated_uprops_space` all iterate a NAME POOL, not a pattern corpus.
   Answer: accepted, or rejected with an error code (§5.4). No `.rxt`
   cousin exists (per §1.4/§1.2, this is PC-3's and uprops §2's own
   territory), which is exactly what "aligned with" rather than "equal to"
   the `.rxt` vocabulary means.

5. **`membership`** — "over this whole code-point space, under this
   encoding, what does `\p{property}` (or the analogous per-oracle
   construct) match?" Fields: `property` (the bare spelling, e.g. `Greek`,
   `sc=Greek`, `Lu`), `encoding` (`byte` | `utf8`). Answer: the ascending
   code-point interval list §1.4's sweep already produces (§5.5). No `.rxt`
   cousin either — a `.rxt` file expresses one match at a time and this
   kind's whole reason to exist is answering all 1,114,112 of them in one
   call.

## 3. `OracleId` — the store's outer key

`OracleId = (name, version, config)`, exactly as chartered. Today there is
one real implementation (`libpcre2`), but every field below is chosen so a
second (`python-re`, or a second reference PCRE2 build) needs no schema
change.

- **`name`** — a short adapter identifier (`libpcre2`). Not a file path, not
  a host name: two adapters that both wrap the same library on different
  transports (in-process direct-link vs. ssh-remote) share `name` and differ
  in `version`/`config` if their answers can differ, or are simply the same
  `OracleId` reached two ways if they cannot (§8 makes this precise).
- **`version`** — the resolved library's own version string, exactly as
  `pcre2_abi_version()` reports it (`tests/fuzz/pcre2_abi.h`) or as the
  reference box's pinned number (`10.46`). Two boxes with the SAME version
  string ARE the same `OracleId` and share store rows; a version bump is a
  new `OracleId` by construction (§8).
- **`config`** — a small closed record of the oracle-side settings that can
  change an ANSWER, never ones that only change performance. Measured from
  the survey: `utf: bool` (PCRE2_UTF — every uprops/PC-4 use of it is
  compile-time-semantic), `caseless: bool` (PCRE2_CASELESS — PC-4's `-i`
  block). **`PCRE2_NO_UTF_CHECK` is explicitly EXCLUDED from `config`**: it
  is a match-time performance flag whose semantic effect only diverges from
  its absence on ILL-FORMED UTF-8 input, and `uprops_oracle.c`'s own subject
  construction is always well-formed by design (surrogates excluded,
  `uprops_oracle.c:73-77`) — so for every question this design's kinds ask,
  the flag is inert and does not belong in a key that exists to distinguish
  answers that can differ. A future kind whose subject can be ill-formed
  would need to reopen this, and should do so by measuring the divergence
  first (D77's own discipline), not by defensively widening `config` now.
  `PCRE2_UCP` is not in `config` either: it has no producer anywhere in this
  tree today (`utf8_design.md` ASK 4, declined) and adding it speculatively
  would be exactly the "build ahead of a measured need" `docs/dev/
  pcrec-build-under-measurement.md` rules against.

## 4. Canonical serialization and the question hash

Each `Question` serializes as a fixed, ordered, tab-separated record whose
first field is the kind name, reusing the ONE escape vocabulary this tree
already has for exactly this purpose — `.rxt`'s own subject escapes (`\"
\\ \n \t \r \f \v \xHH`, `docs/spec/rxt_format.md`'s "`<subject>` is
double-quoted text" table) — rather than inventing a second one. Any field
that can contain an embedded tab or newline (`pattern`, `subject`) is
escaped through it before joining; every other field (`startpos`, `encoding`,
`namespace`, `name`, `property`) is already tab-and-newline-free by its own
grammar (a decimal integer, or an identifier). This is the same principle
`rxt_format.md` itself states for the `.rxt` format: "a `.rxt` author already
knows this one."

```
compile-accept  <pattern>
match-at        <pattern>\t<subject>\t<startpos>
captures        <pattern>\t<subject>\t<startpos>\t<nslots>
name-accept     <namespace>\t<name>
membership      <property>\t<encoding>
```

`captures` carries `nslots` (how many capture pairs the caller wants back,
matching `bref_oracle.py`'s own `<ngroups>` field) because the answer's
SHAPE — how many pairs come back, padded or not — depends on it; two callers
asking for different slot counts over the identical match are, correctly,
two different cached rows, since the padding differs.

**The question hash** is `sha256(serialized_question)`, truncated to the
first 16 hex characters — the exact truncation `docs/design/
utf8_measurements/probes/bundle.py` already uses for its own embedded-file
hashes, reused rather than re-decided. 64 bits of a cryptographic hash gives
a collision probability irrelevant at any population this tree can produce
(the largest surveyed, PC-3's 149,804 compile-accept rows, is nowhere near
the birthday bound); a shorter hash keeps the store's rows human-scannable,
which the diffability requirement (§7) cares about.

**Byte-stability rule**: the hash is computed over the SERIALIZED bytes,
never over a re-parsed/re-normalized structure — a `Question` with a
leading-zero startpos string and one without are different byte sequences
and therefore different hashes UNLESS the producer normalizes before
serializing (every current producer already emits canonical decimal, so
this is a stated invariant rather than an open problem). The store never
"fixes up" a key; a caller that wants a canonical form normalizes before
asking.

## 5. Answer shapes, byte-stable, kind-specific

### 5.1 `compile-accept`
`accept` | `reject\t<code>\t<message>`. Both the code (a stable numeric
identity — PCRE2's own `pcre2_get_error_message` code) and the message are
stored: PC-3's whole `RS_REJECTED` check is "libpcre2 must reject WITH A
MATCHING ERROR IDENTITY" (`pcre2_check.c`'s header), so a code alone would
throw away half of what the file checks for.

### 5.2 `match-at`
`match\t<start>\t<end>` | `nomatch` | `giveup\t<code>`. The third state is
not in the surveyed populations today (PC-4 asserts its own `mlimit`
population zero rather than reporting it) but is included because
`docs/spec/rxt_format.md`'s own `gu` directive already has this three-way
shape on the pcrec side, and a future oracle question against a hostile
subject (a real PCRE2 `PCRE2_ERROR_MATCHLIMIT`/`_ERROR_DEPTHLIMIT`) needs
somewhere to land that is not silently coerced into `nomatch`.

### 5.3 `captures`
`<s0>\t<e0>\t<s1>\t<e1>\t...\t<s(nslots-1)>\t<e(nslots-1)>`, one pair per
requested slot, unset written as the literal pair `-1\t-1` — the identical
convention `docs/spec/rxt_format.md`'s `g`/`gp` directive and `match_api.md`
already use for `RX_UNSET`, reused rather than re-invented. Only meaningful
attached to a `match` answer; a `captures` question over a subject that
turns out `nomatch` has no answer to give and the adapter reports the pair
together (§6) rather than the caller reconstructing it from two calls.

### 5.4 `name-accept`
`accept` | `reject\t<code>`. No message field: PC-3's own `check_verb_names`/
`check_posix_names`/`check_gated_uprops_space` never inspect the rejection
WORDING, only the verdict — D26's own tiering rule (never gold-plate
diagnostic wording) applies here exactly as it does to pcrec's own
diagnostics.

### 5.5 `membership`
`<lo1>-<hi1> <lo2>-<hi2> ... <loN>-<hiN>` (space-separated, ascending,
inclusive both ends) — `uprops_oracle.c`'s own printed line format, byte-
identical to what `uprops_sweep.c` already emits for pcrec, verbatim. No
translation layer: the adapter for this kind IS this format, because it
already round-trips through `uprops_compare.py` today with zero
reinterpretation.

## 6. The adapter contract

```
capabilities() -> { oracle_id: OracleId,
                     kinds: [kind, ...],       # which of §2 it answers
                     transport: enum,          # in-process | subprocess-batch
                                                # | ssh-stdin-payload
                     max_batch: int | none }
answer(batch: [Question]) -> [Answer]          # one Answer per Question,
                                                # positional correspondence
```

**Batch-first because every surveyed mechanism already is one.** §1.5's
`bref_batch.c` reads a whole subject list from stdin and answers
positionally; §1.3's `pc4_check.c` reads a whole `patterns.tsv` and writes a
whole `results-dir`; §1.8's `bundle.py`/`archive.sh` sends one ssh payload
for a whole probe run. The ONE outlier (§1.6, `pcre2_oracle`, one process per
call) is named as the shape a real adapter implementation should NOT
imitate, not as a precedent.

**Two concrete adapter shapes, both already implied by the survey:**

- **Local direct-link adapter** (`libpcre2`, in-process): wraps §1.2/§1.3's
  existing `pcre2_abi.h` binding. `answer()` is a C loop over the batch,
  `OracleId.version` read once via `pcre2_abi_version()`, `capabilities()`
  reporting every kind except none (a direct-linked library can answer all
  five). `max_batch: none` — an in-process loop has no round-trip cost to
  amortize.
- **Remote reference adapter** (`libpcre2`, ssh): wraps §1.8's `bundle.py`
  mechanism generalized from one probe script to one Question-batch payload:
  the whole batch serializes to one stdin blob, the far end runs the SAME
  borrowed binding chain (never re-implemented — `bundle.py`'s own stated
  reason, "a lane that re-implements the binding it is checking cannot
  detect that the original moved") and prints one Answer per line, and
  `archive.sh`'s `BatchMode=yes`/`ConnectTimeout=10` discipline is inherited
  unchanged. `max_batch` here is a REAL knob (unlike the local adapter): a
  batch too large to fit comfortably on one stdin payload or to complete
  within a light-probe's time budget should be split by the CALLER, not
  silently truncated by the adapter — `BOILERPLATE.md`'s own "LIGHT probes
  only... never suite runs" rule is a constraint on HOW MUCH is asked in one
  sitting, and the adapter's job is to make that constraint visible
  (`capabilities().max_batch`), not to hide it.

**Interchangeability, concretely.** Any code that wants an oracle answer
depends only on `capabilities()` + `answer()` + the five `Question`/`Answer`
shapes above — never on whether the oracle is python's `re`, a direct-linked
library, or a machine three thousand miles away. A differential that
compares two oracles is: same `Question` batch, two `OracleId`s, two
`answer()` calls, one diff — which is exactly what §9's migration ladder
turns PC-3/PC-4's darwin-vs-reference divergence handling into, instead of
the ad hoc per-check version-drift policy `tests/uprops/uprops_compare.py`
and `pcre2_check.c`'s `g_lib_major`/`g_lib_minor` branches each currently
hand-roll.

## 7. The store

### 7.1 Physical format

**TSV-ish, one file per `(OracleId, kind)`, diffable.** This follows the
house style already established for every comparable artifact in this tree
— `docs/dev/artifact_size_log.tsv` (a header row naming the commit/date/row
count, one row per compiled artifact), `pc4_check.c`'s own `patterns.tsv`/
per-id results files, `docs/spec/table_contract.md`'s general rule (a header
row naming every column, consumers resolve by NAME never position) — rather
than JSON or a binary format, for the same reasons those files give: a
`git diff` on an updated store shows exactly which questions moved, in a
reviewer's own terminal, with no tool needed to read it.

One file per `(OracleId, kind)` rather than one file per `OracleId` (all
kinds together): the five kinds have genuinely different answer shapes
(`membership`'s one field can be hundreds of bytes of interval list; every
other kind's answer is a handful of short fields), and mixing them in one
table would either force a ragged column count or a serialized-answer blob
column that defeats the diffability this format exists for. Layout:

```
<store-root>/<oracle-name>-<version>[-<config-tag>]/<kind>.tsv
```

with `<config-tag>` present only when more than one `config` is exercised
against the same `(name, version)` (today: PC-4's `caseless` block is the
only non-default config in the whole survey, so most files carry no tag).
Each file's header row names its columns by the table-contract convention
(`question_hash`, `question` — the human-readable serialized form, kept
BESIDE the hash rather than instead of it, so a reviewer reads what changed
without recomputing a hash by hand — then the kind's own answer columns from
§5), rows sorted by `question_hash` for a stable, minimal diff across
re-generation.

### 7.2 Location: reference store committed, local caches gitignored

The reference-version store (today: `libpcre2-10.46`, the project's pin)
is COMMITTED — it is vendored external data by the same shape `third_party/`
already uses for the UCD (`docs/CLAUDE.md`'s entry: "one directory per
source with the version in its name, a PROVENANCE.md naming what derives
from it"). This design recommends the SAME discipline for the store rather
than inventing a new one: a `PROVENANCE.md`-equivalent per `OracleId`
directory naming the resolved library version, the host it was captured on,
the date, and the exact command that produced it — because a committed
answer with no capture record is exactly the "provenance imitation" failure
class `docs/dev/learnings.md` §3 already catalogues for this project's other
archived-output directories (R30 M7). Local-version caches (whatever
libpcre2 the DEV box resolves — Homebrew 10.48 here) are gitignored, under
a `build/`-shaped separate output tree (`build-ubsan/`/`build-asan/`'s own
precedent: never touching what a plain `make`/`make test` reads), since a
local cache's whole value is saving a same-box re-run and it has no reason
to travel with the repository or to be trusted by another box.

**Where, exactly, is an open question for the panel (§13).** Two candidates,
both consistent with the above: a new top-level `oracle_store/` (mirroring
`third_party/`'s own top-level standing, since this is external-derived data
too, just derived by RUNNING a library rather than by vendoring a data
file), or `tests/oracle_store/` (since every consumer today lives under
`tests/`). This note leans toward the top-level form on `third_party/`'s own
precedent but does not rule it — the deciding fact is whether a NON-test
consumer (a future `docs/design/` measurement lane, per §1.8's own pattern)
would read it, which favors top-level.

### 7.3 Size, from measured populations

Every number below is either directly measured in §1 or a stated derivation
from a measured count (labelled). None are invented.

| kind | source | population | per-row bytes (rough) |
|---|---|---|---|
| compile-accept | PC-3 posix probes | 149,804 (measured, `pcre2_check.c:1666`) | ~40-80 (short pattern + verdict) |
| compile-accept + match-at | PC-4 | 273 patterns / 62,872 cells (measured, header) | match-at rows ~30 |
| name-accept | uprops §2 gated space | 1,053 (measured, `tests/uprops/CLAUDE.md`) | ~20 |
| membership | uprops byte arm | 91 properties (measured) | tens to low hundreds of bytes/property (short intervals) |
| membership | uprops utf8 arm | ~387 properties (derived, §1.4 — NOT independently re-measured this lane) | up to several KB for a property with many disjoint ranges (e.g. `\p{L}`'s minimized-DFA state count of 283, `utf8_design.md`, suggests a comparably modest interval count, but this is an inference from a DIFFERENT measurement and should be confirmed, not assumed, at migration time) |

The PC-3 table alone is comfortably under ten megabytes at these row-size
estimates; the utf8 membership table is the one genuinely unmeasured
quantity and is exactly what §9 Step 1's migration run measures directly
rather than estimates further.

## 8. The staleness-impossibility argument

Frank's directive is that the oracle "isn't going to give different results
at different times." This is not an assumption the design adds — it is
already how every surveyed check treats libpcre2: PC-3, PC-4, uprops all
treat one resolved library as a pure function of `(pattern-or-name bytes,
subject bytes, config)`, with no run-to-run variance and no environmental
dependence beyond which library got resolved. The store's correctness
argument is three short claims, each already implicit in the code above and
now made explicit:

1. **Same `OracleId` + same question hash ⇒ same `Answer`, always.** This
   follows from the oracle being a pure function per (1): the library binary
   named by `(name, version)` compiled/matched against fixed bytes under a
   fixed `config` cannot answer two different things on two different days.
   Nothing in this design WEAKENS that guarantee — it only writes the
   already-true answer down once instead of recomputing it every run.

2. **A version bump is a clean miss, never a stale hit.** `OracleId`
   includes `version`; the moment the resolved library changes (a Homebrew
   bump, a new reference pin), every lookup keys against a `(name,
   NEW-version, config)` directory that does not exist yet, so every
   question is, correctly, a fresh live call. There is no expiry policy to
   get wrong, no TTL to tune, and no manual invalidation step to forget —
   the same reason `docs/pcre2_compliance_annotations.txt`'s own staleness
   check works (`docs/CLAUDE.md`'s `[DOC-DRV]` entry): the check is a
   structural fact about the key, not a promise a human keeps.

3. **Only the oracle side caches, so a stale PCREC answer can never hide
   behind a fresh-looking oracle one.** `docs/dev/learnings.md` §3's own
   standing lesson — "a control must not share a source with what it
   controls" — applies here in its sharpest form: if pcrec's own answers
   were ALSO cached, a regression in pcrec between two runs could be masked
   by a stale pcrec-side cache entry that happens to still agree with the
   (correctly cached) oracle answer, and no differential would ever see the
   regression. The directive's own asymmetry — "ONLY the oracle side
   caches — pcrec answers compute fresh every run" — is this design's single
   most load-bearing rule, and every adapter in §6 answers ONLY oracle
   questions; nothing in this design defines a pcrec-side cache, and none
   should ever be added under this same mechanism.

## 9. Migration ladder

**Step 1 — uprops (byte + utf8).** The local direct-link adapter answers the
byte arm live today (cheap, no reason to defer using the store's shape even
though caching buys little there — using the identical code path for both
arms is the point). The utf8 arm's reference run becomes ONE remote-adapter
batch call — every `membership` question for the whole shipped property set,
in one ssh round trip, against the 10.46 reference — with the answers
committed to `oracle_store/libpcre2-10.46/membership.tsv`. This is the exact
mechanism that discharges wake.md's owed "STAGE-5 10.46 EXACT arm" without
requiring darwin to own the reference, and it is what turns S-U6/S-U9's
closing witnesses from a recurring manual measurement into a one-time
capture followed by permanent, free, local `make test-uprops-utf8` runs
against the committed table.

**Step 2 — C3 (python `re`).** Wrap `verify_rxt.py`'s existing calls in the
adapter shape (§1.1) for uniformity, not for caching value. The dividend is
architectural: once python-`re` speaks the same `Question`/`Answer` contract
as libpcre2, a drift check between the two ("does python's `re` module in
THIS python version still disagree with libpcre2 on exactly the documented
set, `docs/dev/upstream_issues.md` U8/U11/U11b/U11c/U12/U14") becomes a
batch-diff over the store rather than a bespoke script, and any future
python version bump is a version-scoped `OracleId` the same way a libpcre2
bump is.

**Step 3 — PC-3 / PC-4.** The local adapter answers the darwin-vs-Homebrew
arm live, same as today (its in-process C cost is already low; caching here
mainly buys re-run speed, not correctness). The REAL value: the reference-
box arm currently owed to I-63 (wake.md: "PC-3 209, POSIX pool 149804@10.46")
runs ONCE over the remote adapter and is committed — dissolving the whole
U13/U15b divergence-attribution class for every CACHED question (a probe
already asked of 10.46 is answered from the store on darwin without ever
touching a library that isn't there), while a genuinely NEW probe (a new
registry row, a new candidate name) still falls through to a live call
against whatever local library is resolved, correctly reported as
un-cross-checked against the reference until someone runs the remote batch
again.

**Step 4 (unchartered, named for completeness) — the shared-binding family.**
`bref_oracle.py`/`la_oracle.py`/`u8_oracle.py`/`atomic_oracle.py`
already share one binding chain (§1.5); wrapping that chain in the §6
contract is mechanical once the contract exists, because the adapter
boundary these files already drew (one shared `pcre2_ctypes.py`, borrowed
not copied) is the same boundary this design draws around "the local
direct-link adapter." Not scheduled ahead of Steps 1-3 by this note.

## 10. What does NOT change

- **`.rxt` files and the driver protocol are untouched.** `docs/spec/
  rxt_format.md`'s grammar, `tests/harness/run.sh`'s per-block evaluation
  and `tests/harness/driver.c`'s exit-code contract are the CONTRACT
  (D80); this design is oracle-SIDE tooling consulted by test authors and
  CI checks producing or validating expectations, never a runtime
  dependency of `pcrec` itself or of a compiled artifact.
- **Every existing check's verdict logic is unchanged.** PC-3's polarity
  rules (`RS_REJECTED` must reject WITH a matching identity; `RS_MODULE`
  must compile), PC-4's over-acceptance/over-rejection double-direction
  check, uprops' drift-budget policy (`RECLASSIFIED`/`PCRE2_SEMANTIC_DRIFT`,
  §4's oracle-free invariants) — none of these move. The adapter changes
  HOW an answer is obtained; it never changes what a check does with one.
- **`docs/pcre2_compliance.md`'s independent survey stays independent**
  (§1.9) — it is explicitly not a store customer, by design, forever,
  unless `[DOC-DRV]`'s own checked-tension architecture is separately
  revisited.
- **No pcrec-side cache exists or is proposed** (§8.3).

## 11. `.rxt` provenance — the dividend, sketched not designed

Once real per-question hashes exist, a `.rxt` block's expectation could cite
"oracle `libpcre2@10.46(utf=0,caseless=0)`'s answer to hash `H`" instead of
the current convention (a CLAUDE.md prose sentence naming "libpcre2 10.46
through the committed ctypes binding" for a whole directory). This is named
as a dividend the store's existence makes possible, not designed here: it
would need its own `.rxt` directive or accompanying manifest format, its own
migration of the existing corpus's provenance claims, and its own D77
trigger (a real reader confusion the current prose convention causes) before
becoming a chartered row. Out of scope for this lane.

## 12. Fixture-shaped examples

One worked example per kind, using real corpus material, showing the
serialized `Question`, its hash (illustrative — not actually computed by
this read-only lane), and the `Answer` in the format §5 defines.

**compile-accept** — a PC-3 fabrication-check probe (`pcre2_check.c`'s own
worked example, a verb doorway typo):
```
Question:  compile-accept\t(*BADVERB)
Answer:    reject\t134\tunknown POSIX class name in [::]
```
(the code/message pair is illustrative of shape, not a real PCRE2 return for
this exact text — the fixture demonstrates the FIELD LAYOUT, not a captured
number.)

**match-at** + **captures** — the re-entry family `backrefs_design.md` names
as the sharpest case for publish-at-close semantics:
```
Question (match-at):  match-at\t(a|b\1)+\tab\t0
Answer:                match\t0\t2

Question (captures):  captures\t(a|b\1)+\tab\t0\t2
Answer:                0\t2\t1\t2
```
(slot 0 is the whole match, slot 1 is group 1 — libpcre2's PUBLISH-AT-CLOSE
answer per `backrefs_design.md`'s own R32 finding, `(0,2)` overall with
group 1 = `(1,2)`.)

**name-accept** — a uprops script name, and the PC-3-style refusal control
a fabricated name would hit:
```
Question:  name-accept\tuprops-script-bare\tGreek
Answer:    accept

Question:  name-accept\tuprops-script-bare\tKawi
Answer:    reject\t134     # (10.46 predates Kawi's addition; a real capture
                            #  would report the reference's ACTUAL code)
```

**membership** — the byte-arm control property the drift policy leans on:
```
Question:  membership\tsc=Greek\tbyte
Answer:    370-373 3B6 386 388-38A 38C 38E-3A1 3A3-3E1 ...
```
(illustrative truncation — the real answer is `sc=Greek`'s full Latin-1-
clamped interval set, exactly what `uprops_oracle.c`'s own sweep already
prints for this property today.)

## 13. Open questions for the panel / for Frank

1. **Store location** — top-level `oracle_store/` (this note's lean, on
   `third_party/`'s precedent) vs. `tests/oracle_store/` (every current
   consumer lives under `tests/`). §7.2.
2. **Hash truncation length** — 16 hex chars (`bundle.py`'s own precedent,
   reused rather than re-decided) vs. a longer/shorter cut. No population
   surveyed approaches a collision risk at 16; the question is purely
   human-scannability vs. row-width.
3. **Is `name-accept` really a fifth kind**, or should it fold into
   `compile-accept` via a per-namespace synthesis template carried in the
   adapter? §2 item 4 argues for keeping it separate (diffability,
   matching the tree's own name-pool iteration shape); a panel that
   disagrees should say which of the three stated reasons it rejects.
4. **Does the reference `OracleId`'s `config` need a `host`/`method` field**
   for provenance, even though — by definition — it must never affect the
   ANSWER (§3's own rule: `config` holds only fields that can change an
   answer)? This note keeps provenance in the per-`OracleId` directory's
   `PROVENANCE.md`-equivalent (§7.2) rather than in the key, on the
   argument that provenance and identity are different questions, but the
   panel should confirm that split rather than inherit it silently.
5. **Git storage for the large `membership` table** — plain committed text
   (this note's default, matching every other archived-output convention in
   the tree) is untested at the utf8 arm's real size (§7.3's honestly-
   unmeasured row). If Step 1's migration measures a table too large for
   comfortable plain-text committing, that is itself the D77 trigger for
   revisiting compression or a different physical format — not a reason to
   guess at one now.
