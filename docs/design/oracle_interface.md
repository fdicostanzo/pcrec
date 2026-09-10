# The oracle interface and the answer store — design note

**PROPOSED, PANELED (R56) AND REVISED.** Lane `oraiface`, 2026-09-10; revision
lane `oraiface2`, 2026-09-10, applying R56-1..8 plus a stale-comment side fix
against `docs/dev/reviews/2026-09-10-r56-oracle-interface.md` (two critics,
r56cons + r56mech: the survey held exact under re-derivation, the mechanism
had two deterministic-failure blockers and a ladder misattribution, all fixed
in place below). Scope per Frank's directives (`docs/dev/wake.md`'s lane-3
spec, 2026-09-09 late) and D77: this note designs the interface and the
store; **it builds neither**. No code lands from this lane. A B13-contract
completion-contract VERIFY PASS runs against this revision before merge; the
uprops instance (the store's first real customer) builds only after that
pass and the manager's merge.

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
first customers are the uprops whole-space sweeps (**R56-6, BLOCKING,
corrected**: it is `S-U12`'s neighborhood — the STAGE-5 drift-zeroing 10.46
`membership` arm — that rides this step; `S-U6`/`S-U9`'s own closing
witnesses are `match-at`-kind cells riding a LATER ladder rung — S-U9's
over an ILL-FORMED continuation run, S-U6's over a WELL-FORMED subject
(the find-all/empty-match boundary defect; the two rows' populations are
not the same axis, r56verify's correction) — §9 states the distinction in
full), then the C3 python
oracle, then the PC-3 probe families;
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

**Six kinds** (R56-7 added the sixth), aligned with `docs/spec/rxt_format.md`'s
own directive vocabulary (`pattern`/`perr`, `m`/`n`/`ms`/`ns`, `g`/`gp`) but
not a bare 1:1 mapping onto it — three kinds below (`name-accept`,
`membership`, `pattern-info`) answer questions no single `.rxt` cell asks,
because their whole value is asking about a NAME, a WHOLE SPACE, or a
pattern's own STRUCTURE rather than one match. Every kind's
fields are named exactly, because §4's hash needs a closed, ordered field
list per kind — an open-ended "extra options" bag would make the
serialization non-canonical by construction.

**Extension rule (R56-7).** The kind-set is closed but not frozen: adding a
seventh kind is a STORE-FORMAT MINOR VERSION BUMP (§8 Claim 4's version
field, one number up) and touches nothing about the kinds already
defined — no existing kind is ever re-keyed, re-fielded, or re-ordered to
make room for a new one. A kind addition is additive by construction the
same way `rx_info`'s own struct-append rule is (D76/D94's "append after
`nentries`, no existing offset moves" precedent, one layer over): a store
reader built against store-format version N reads every row a version-N+1
writer produced for kinds 1..N unchanged, and simply does not recognise
rows of the new kind until it is updated.

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

6. **`pattern-info`** — "compiled under this oracle's config, what are this
   pattern's own STRUCTURAL properties?" (R56-7, cons-F2, MUST-FIX: a real,
   oracle-consulted, pure-function-of-(pattern,config) question no earlier
   kind expresses.) Fields: `pattern` (raw bytes) — no subject, no startpos;
   this kind asks about the compiled pattern object itself, never a match
   attempt against it. Answer: the capture count, the name count, and the
   NAMETABLE as an ORDERED LIST of `(name, group-number)` pairs — and the
   list's canonical form is not free to choose, because a producer and a
   store reader must agree on ONE ordering byte for byte. It is the
   ordering `docs/dev/decisions.md` D59 measured `PCRE2_INFO_NAMETABLE`
   itself to use — the evidence `tests/probes/CLAUDE.md` also records, one
   layer closer to the probe, as "the evidence behind... D59's sort-key
   ruling" — and that pcrec's own `rx_info.groups` sort key adopts:
   **name-ascending, byte-exact `strcmp`, case-sensitive**. D59's own
   words, measured against libpcre2 10.46 via `tests/probes/
   probe_named_groups.c`: "a 3-name pattern declared `zeta`/`alpha`/`mu`
   by opening-paren order comes back `alpha`/`mu`/`zeta`." That
   population — the same construct D59 already measured
   to decide pcrec's own layout — is `pattern-info`'s citable evidence that
   the kind answers a question this tree already asks and already has a
   settled convention for, not a new one invented for this design. The
   answer's wire form (§5.6) serializes the nametable in exactly that
   order, so a `pattern-info` answer and `rx_info.groups`' own sort rule
   are provably the same convention rather than two conventions that
   happen to agree today. No `.rxt` cousin exists (a `.rxt` cell asserts a
   match or a rejection, never a pattern's own reflection surface), which
   is again "aligned with" rather than "equal to" the `.rxt` vocabulary. A
   store customer for this kind is DEFERRED (nothing in §9's migration
   ladder consumes it yet); the kind is defined now because §2's field-list
   canonicality argument applies to it exactly as it does to the other
   five, and defining it later would be a store-format bump either way.

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
  block), and — **R56-2, BLOCKING** — the **limit triple**,
  `match_limit`/`depth_limit`/`heap_limit`. These are ANSWER-AFFECTING, not
  performance-only: this tree's own `docs/design/subroutines_measurements/
  probes/sr_oracle.py` (the shared oracle behind the subroutines,
  atomic-groups and left-recursion probes) exists specifically to vary them
  and MEASURES the flip — `match_limits(r"^(a+)+$", "a"*24+"b", match=1000)`
  (`sr_oracle.py:322`) answers `PCRE2_ERROR_MATCHLIMIT`, and its own
  control cell one line down (`sr_oracle.py:331`, the SAME pattern under a
  huge `match=100000000`) is required to reach a clean `nomatch`, "or the
  row above proves nothing about the LIMIT" (`sr_oracle.py:329`'s own
  comment) — the identical construct under two limit values answering two
  different verdicts, asserted by the probe's own self-check. `depth_of()`'s
  whole method (`sr_oracle.py:158-176`) is a bisection over
  `depth_limit` for the SMALLEST value at which one fixed pair still matches
  — a method with no content unless the limit is answer-affecting. The
  design's own `giveup(code)` answer state (§5.2) anticipates exactly this
  population and cannot be given a defensible cache key without it: a
  `giveup` answer cached under a key that omits the limit that produced it
  is a lie the moment a caller asks the identical question under a
  different limit and gets a live PCRE2 call back with the opposite
  verdict. FIX: `OracleId.config` gains all three fields, with EXPLICIT
  DEFAULTS rather than "whatever the library ships with" — measured
  2026-09-10 via `pcre2_config()` against this box's resolved binding
  (Homebrew 10.48, `PCRE2_CONFIG_MATCHLIMIT`/`_DEPTHLIMIT`/`_HEAPLIMIT`):
  `match_limit = 10000000`, `depth_limit = 10000000`, `heap_limit =
  20000000` (KiB — PCRE2's own unit for this one field). These are PCRE2's
  long-stable compiled-in defaults, not a 10.46-vs-10.48 drift figure — the
  measurement pins the SOURCE (a real `pcre2_config()` call against a real
  binding, not a value copied from memory or from documentation alone) and
  every `config` record that does not name these three fields explicitly is
  understood to mean exactly these three values, never "unset" or "whatever
  ran". §8 Claim 1 is restated below over this widened key; **a `giveup`
  answer is cacheable ONLY under a fully-keyed `config`** — a caller with no
  opinion on the limit triple gets the defaults above, explicitly, never an
  unkeyed wildcard.

  **`PCRE2_NO_UTF_CHECK` is explicitly EXCLUDED from `config`** (verified
  sound at R56 unchanged): it
  is a match-time performance flag whose semantic effect only diverges from
  its absence on ILL-FORMED UTF-8 input, and `uprops_oracle.c`'s own subject
  construction is always well-formed by design (surrogates excluded,
  `uprops_oracle.c:73-77`) — so for every question this design's kinds ask,
  the flag is inert and does not belong in a key that exists to distinguish
  answers that can differ. A future kind whose subject can be ill-formed
  would need to reopen this, and should do so by measuring the divergence
  first (D77's own discipline), not by defensively widening `config` now.
  `PCRE2_UCP` is not in `config` either (verified sound at R56 unchanged):
  it has no producer anywhere in this
  tree today (`utf8_design.md` ASK 4, declined) and adding it speculatively
  would be exactly the "build ahead of a measured need" `docs/dev/
  pcrec-build-under-measurement.md` rules against.

  **R56-8 — two more axes are excluded, named rather than silently absent.**
  Newline convention/BSR (PCRE2's `PCRE2_NEWLINE_*`/`PCRE2_BSR_*` option
  words, DD-11's territory) and JIT-vs-interpreted execution are BOTH
  excluded from `config` by the same measured-fact argument as
  `PCRE2_UCP` above: no adapter surveyed in §1 varies either one — every
  probe in this tree links `pcre2_compile`/`pcre2_match` at their default
  newline/BSR settings, and the R56 panel's own adversarial verification
  pass confirmed it directly ("no JIT anywhere in today's bindings",
  `docs/dev/reviews/2026-09-10-r56-oracle-interface.md`'s "Survived
  adversarial verification" record). Naming them here
  rather than leaving them as two more things nobody asked about states the
  rule an adapter author must follow the day either changes: **an adapter
  that varies newline/BSR or that runs under JIT must widen `config`
  FIRST**, measuring the divergence before adding the field, on the exact
  discipline `PCRE2_UCP`'s own exclusion above already follows — not a new
  rule, the same one applied to two more axes so a future reader does not
  have to re-derive it.

## 4. Canonical serialization and the question hash

**R56-1, BLOCKING — corrected in full.** The first version of this section
named the WRONG vocabulary and its own worked example in §12 was
non-injective, deterministically, on ordinary patterns already in this
corpus. The concrete collision: `rxt_format.md` itself records that a
`pattern` line is rest-of-line VERBATIM and "the corpus contains three
such blocks today" carrying a literal raw TAB byte (0x09) directly in the
pattern text. Take a pattern whose raw source bytes are `a`, TAB, `b`
(three bytes — a real, legal `.rxt` pattern line) beside a second,
UNRELATED pattern whose raw source bytes are `a`, `\`, `t`, `b` (four
bytes — an ordinary PCRE2 pattern spelling `a`, an ESCAPE SEQUENCE `\t`,
then `b`; at the byte level this is just the ASCII characters backslash
and lowercase `t`). Serializing the first pattern by escaping its one raw
TAB the naive way produces the four characters `a`, `\`, `t`, `b` — BYTE-
IDENTICAL to the second pattern's own raw, un-escaped text. Two different
patterns, one serialized form, one hash: exactly the collision the review
found, and it needed no adversarial input to reach, only two patterns this
tree already has reason to hold side by side.

**The canonical serialization is the `docs/spec/rxt_format.md`:458-474
FIVE-ESCAPE TSV-FRAMING SUBSET, stated normatively, not the seven-escape
quoted-context vocabulary that section explicitly calls out as a
different, larger thing.** This tree has TWO escape vocabularies and they
serve different jobs:

- **The quoted-context vocabulary** (`rxt_format.md`'s "`<subject>` is
  double-quoted text" table, seven escapes: `\" \\ \n \t \r \f \v \xHH`) —
  for a `<subject>` literal written BETWEEN QUOTES inside a `.rxt` file,
  where `\"` protects the closing delimiter. **This design REJECTS it
  explicitly**: a `Question`'s serialized record has no quoted context and
  no closing delimiter for `\"` to protect, so importing that vocabulary
  wholesale would carry an escape with nothing to guard and would be one
  more thing a reader has to know does nothing here.
- **The TSV-framing subset** (`rxt_format.md`:458-474, five escapes: `\\
  \t \n \r \xNN`) — the ones `pcrec --list-source`'s own dump already uses
  to protect TSV FRAMING for exactly this reason: "the dump's five escapes
  ... are the ones needed to protect TSV FRAMING, not the full seven-escape
  subject vocabulary." `\f`/`\v` are not named escapes in this subset; a
  literal form-feed or vertical-tab byte still round-trips correctly
  through the `\xNN` form (`\f` as `\x0c`, `\v` as `\x0b`) exactly as
  `rxt_format.md` states for the dump. **This is the vocabulary this
  design adopts**, reused rather than re-decided, because a `Question`
  record is TSV framing and nothing else — there is no quoted context to
  protect and no reason to carry an escape that exists only for one.

**The producer rule, stated normatively: BACKSLASH IS ESCAPED FIRST.** A
producer serializing a field escapes every literal `\` byte to `\\` BEFORE
applying any of the other four escapes (`\t`, `\n`, `\r`, `\xNN` for any
other byte requiring protection). This is not a stylistic preference — it
is what makes the five-escape subset INJECTIVE at all. Un-escaped, a raw
TAB byte and a literal two-byte sequence `\` + `t` both serialize to the
same two characters `\t`; escaping the backslash first turns the literal
sequence into THREE characters, `\\t` (backslash, backslash, letter-t),
which cannot be confused with the two-character escaped TAB. §12's
`(a|b\1)+` example is corrected below to demonstrate this rule in a real
pattern from this tree's own corpus.

**The trailing-backslash test vector**, stated as its own edge case because
it is the one place the rule's ORDER matters twice: a pattern whose raw
bytes END in a literal backslash immediately before the TSV field boundary
— say pattern text `a\` (two bytes: `a`, then a lone trailing `\`). Escaped
backslash-first, this serializes as `a\\` (three characters: `a`, `\`,
`\`), which the reader parses as one literal `a` followed by one escaped
backslash — NOT as a dangling, incomplete escape reaching across the field
boundary into whatever follows the row's real (unescaped) tab delimiter.
Any implementation must be exercised against this exact vector before
shipping: a producer or reader that escapes in the wrong order, or that
treats a trailing `\\` as ambiguous with the start of a new escape, fails
on this one pattern and no other, which is exactly the shape of bug this
design's own injectivity claim exists to rule out.

```
compile-accept  <pattern>
match-at        <pattern>\t<subject>\t<startpos>
captures        <pattern>\t<subject>\t<startpos>\t<nslots>
name-accept     <namespace>\t<name>
membership      <property>\t<encoding>
pattern-info    <pattern>
```

`captures` carries `nslots` (how many capture pairs the caller wants back,
matching `bref_oracle.py`'s own `<ngroups>` field) because the answer's
SHAPE — how many pairs come back, padded or not — depends on it; two callers
asking for different slot counts over the identical match are, correctly,
two different cached rows, since the padding differs.

Every field that can contain an embedded tab, newline, or backslash
(`pattern`, `subject`) is escaped through the five-escape subset above,
backslash first, before joining; every other field (`startpos`, `encoding`,
`namespace`, `name`, `property`) is already tab/newline/backslash-free by
its own grammar (a decimal integer, or an identifier) and needs no
escaping at all.

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

### 5.6 `pattern-info` (R56-7, MUST-FIX)
`<capturecount>\t<namecount>\t<name1>:<num1> <name2>:<num2> ... <nameN>:<numN>`
— two leading integer fields (`PCRE2_INFO_CAPTURECOUNT`/`_NAMECOUNT`'s own
values), then the nametable as a SPACE-SEPARATED ORDERED LIST, one
`name:number` pair per named group, in the CANONICAL ORDER §2's kind
definition states: name-ascending, byte-exact `strcmp`, case-sensitive —
`PCRE2_INFO_NAMETABLE`'s own measured order (D59, `tests/probes/
probe_named_groups.c`), which is also `rx_info.groups`' own sort key on the
pcrec side. An unnamed group contributes no entry to the list (the list's
length is `namecount`, never `capturecount`) and is otherwise invisible to
this kind — a caller wanting the full 1..`capturecount` numbering without
names is asking `capturecount` alone, already in the answer's first field.
The delimiter choice deliberately avoids both TAB (the record's own field
separator) and comma (a valid byte in a group NAME under some namespaces
elsewhere in this tree); a space is safe here because `tests/probes/
CLAUDE.md`'s own measured name grammar ("first byte letter/`_`, later bytes
alnum/`_`") admits no space in a legal PCRE2 group name, so the list's own
internal delimiter can never collide with a name it separates.

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
  six — `pattern-info` is a `pcre2_compile()` plus a `pcre2_pattern_info()`
  call, the same primitive PC-3/PC-4 already use). `max_batch: none` — an
  in-process loop has no round-trip cost to amortize.
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
depends only on `capabilities()` + `answer()` + the six `Question`/`Answer`
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
kinds together): the six kinds have genuinely different answer shapes
(`membership`'s one field can be hundreds of bytes of interval list;
`pattern-info`'s nametable field is a variable-length ordered list too;
every other kind's answer is a handful of short fields), and mixing them in
one table would either force a ragged column count or a serialized-answer
blob column that defeats the diffability this format exists for. Layout:

```
<store-root>/<oracle-name>-<version>[-<config-tag>]/<kind>.tsv
```

with `<config-tag>` present only when more than one `config` is exercised
against the same `(name, version)` (today: PC-4's `caseless` block is the
only non-default config in the whole survey, so most files carry no tag —
**R56-2 widens what a non-default tag can mean**: the limit-triple defaults
stated in §3 are the UNTAGGED baseline, and a store row captured under any
other `match_limit`/`depth_limit`/`heap_limit` value carries its own
`<config-tag>` exactly as `caseless` does today).

**R56-3, MUST-FIX — the serialization itself is versioned (§8 Claim 4).**
Each file's header row carries, beside the column names, a
`store_format_version` field naming the serialization-rule version this
file's rows were written under — the escape vocabulary and producer rule
of §4, and this document's own kind-set revision (the extension rule in
§2). A reader that encounters a version it does not implement treats every
row in the file as a CLEAN MISS, on exactly the argument `OracleId.version`
already makes for a library bump (§8 Claim 2): there is no partial reading
of a format a reader does not speak, so there is nothing to get subtly
wrong.

**R56-4, MUST-FIX — the store self-checks (the `artifact_size_log.tsv`
precedent's ACTUAL shape, followed rather than merely cited).** That file's
own header names the commit, the date, the load at start, AND "the row
count the SAME run produced (so a truncated file is detectable by comparing
the two)" — `docs/CLAUDE.md`'s own description of it. Each per-`(OracleId,
kind)` file's header therefore carries its own ROW COUNT and PROVENANCE
(the resolved `OracleId`, the capture date, the exact command that produced
it — the same three facts §7.2's per-`OracleId` `PROVENANCE.md`-equivalent
names, now ALSO stamped per file so a single truncated or corrupted
`(OracleId, kind).tsv` is detectable without cross-referencing a sibling
document) alongside the `store_format_version` field above. **And readers
verify a fetched row's `question` column against the query's own
serialization before trusting its answer column** — the cheap
collision/corruption tripwire this design's whole hash-keyed lookup needs:
`question_hash` alone is 16 hex characters of `sha256`, chosen in §4
precisely because a collision is statistically irrelevant at any surveyed
population, but a bit-flip in a committed file, a hand-edit gone wrong, or
a future population large enough to make the birthday bound relevant are
all cheaper to catch by re-comparing the stored `question` TEXT (already
kept beside the hash for exactly this reason, §7.1's own "kept BESIDE the
hash... so a reviewer reads what changed") than to leave undetected. A
mismatch is a hard read failure, never a silently-returned wrong answer.

Each file's header row names its columns by the table-contract convention
(`question_hash`, `question` — the human-readable serialized form, kept
BESIDE the hash rather than instead of it, so a reviewer reads what changed
without recomputing a hash by hand — then the kind's own answer columns from
§5), rows sorted by `question_hash` for a stable, minimal diff across
re-generation.

### 7.1a Store discipline (R56-5, MUST-FIX)

**Regeneration is sorted-by-hash, with a DUPLICATE-HASH DETECTOR as a
check** — the same MECH-1-class tripwire this design's own collision
argument (§4, §7.1's row-verification above) demands: a regeneration run
that writes two rows with the same `question_hash` and two different
`question` texts is exactly the collision R56-1 fixed one layer down, and
the detector's job is to make that fact loud rather than let the second
row silently shadow or corrupt the first. The detector runs as part of
whatever process WRITES a store file, not as a separate periodic audit —
the same "the check rides the thing it guards" discipline `tests/size/`'s
own SIZELOG ratchet already follows for `docs/dev/artifact_size_log.tsv`.

**Regeneration ownership: the owning lane regenerates; appends never land
unsorted in a committed store.** A store file is not a log a caller appends
a line to — it is a SORTED SNAPSHOT (§7.1's own "rows sorted by
`question_hash` for a stable, minimal diff"), so a new question joining the
population is a REGENERATION of the whole file by whichever lane owns that
`(OracleId, kind)`'s population (the migration-ladder step that introduced
it, per §9), never an unsorted line appended by whichever caller happened
to ask first. An appended, unsorted row would defeat the diffability §7.1
exists for on the very next `git diff`.

**Merge protocol: re-derive on conflict, never hand-merge rows.** Two
branches that both regenerate the same `(OracleId, kind)` file produce two
independently-sorted, independently-correct snapshots that a textual
three-way merge cannot safely interleave — a hand-resolved merge conflict
in a TSV store file is exactly the shape `docs/dev/plan.md`'s own git-merge
situation-index row warns about for a different file ("a conflicted merge
leaves MERGE_HEAD... resolve, then commit"), and the resolution here is
narrower and safer than a text merge: RE-RUN the regenerating process
against the post-merge tree and let it overwrite both sides. A merge that
tries to interleave two sorted TSV files by hand is the one thing this
protocol forbids outright.

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
| pattern-info | none (deferred store customer, §2 kind 6) | 0 — no store row is written for this kind by any step §9 schedules | n/a |

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

1. **Same `OracleId` + same question hash ⇒ same `Answer`, always — RESTATED
   OVER THE WIDENED KEY (R56-2).** This follows from the oracle being a pure
   function per (1): the library binary named by `(name, version)`
   compiled/matched against fixed bytes under a fixed `config` — now
   including the limit triple `match_limit`/`depth_limit`/`heap_limit`, §3
   — cannot answer two different things on two different days. The claim
   was never false for `utf`/`caseless` alone; it would have been false in
   practice the moment a `giveup(code)` answer was cached against a key
   that omitted the limit that produced it, because the identical
   `(pattern, subject, startpos)` triple under a DIFFERENT limit is a
   REAL, measured different answer (§3's `sr_oracle.py` citation) rather
   than noise the pure-function argument could paper over. Nothing in
   this design WEAKENS that guarantee — it only writes the
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

4. **A store-format or serialization-rule change is a clean miss, exactly
   like an oracle version bump (R56-3).** §7.1's `store_format_version`
   field makes this a structural fact about the FILE rather than a promise
   a human keeps: a reader that speaks a different version treats every
   row under the old one as unread, never as a row it partially
   understands and partially guesses at. This is claim 2's own argument
   ("there is no expiry policy to get wrong... the check is a structural
   fact about the key") applied to the SERIALIZATION rather than to the
   library — an encoding change (a new escape rule, a widened kind-set)
   invalidates a store file's readability exactly as cleanly as
   `OracleId.version` invalidates its content, and for the same reason:
   both are facts a reader checks before trusting anything else in the
   file.

## 9. Migration ladder

**Step 1 — uprops (byte + utf8).** The local direct-link adapter answers the
byte arm live today (cheap, no reason to defer using the store's shape even
though caching buys little there — using the identical code path for both
arms is the point). The utf8 arm's reference run becomes ONE remote-adapter
batch call — every `membership` question for the whole shipped property set,
in one ssh round trip, against the 10.46 reference — with the answers
committed to `oracle_store/libpcre2-10.46/membership.tsv`. This is the exact
mechanism that discharges wake.md's owed "STAGE-5 10.46 EXACT arm" without
requiring darwin to own the reference — **and it is `S-U12`'s neighborhood
this discharges, not S-U6/S-U9 (R56-6, BLOCKING, corrected)**: the STAGE-5
drift-zeroing arm is uprops' own script-namespace `membership` differential
(`tests/utf8/axis12_scripts.rxt`, `S-U12`'s own "bare spelling vs. Script
property" population) measured against whichever local library darwin
resolves today rather than against the true 10.46 pin, which is precisely
the `membership`-kind, whole-code-point-space question this step's remote
adapter answers once and commits. `S-U6`/`S-U9`'s own closing witnesses are
a DIFFERENT kind's population and a LATER ladder rung: both are `match-at`
questions over an ILL-FORMED-UTF-8-SUBJECT population (`S-U6`'s find-all
empty-match-at-a-multi-byte-boundary cell; `S-U9`'s ill-formed
continuation-run cell under a negative lookbehind), and both rows' own
headers name the SAME blocked instrument — "the same UTF8-vs-libpcre2
instrument S-U6 names as blocked on a corpus follow-up in the admin queue
(an ill-formed-subject axis..., axis03/axis10's own precedent)"
(`S-U9_back_step_length_test_deleted.sh`) — which is a `match-at`
differential over ill-formed subjects, not this step's `membership` sweep.
That instrument rides Step 2 or a dedicated later rung once such a
differential exists; nothing in Step 1 reaches it.

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
as the sharpest case for publish-at-close semantics, **corrected for R56-1's
backslash-first rule**: the pattern's raw text is `(a|b\1)+`, whose one
literal `\` byte MUST be escaped to `\\` before serializing, exactly as §4
now states normatively — the note's first draft showed this Question
UNESCAPED, which is the non-injective example the review found:
```
Question (match-at):  match-at\t(a|b\\1)+\tab\t0
Answer:                match\t0\t2

Question (captures):  captures\t(a|b\\1)+\tab\t0\t2
Answer:                0\t2\t1\t2
```
(slot 0 is the whole match, slot 1 is group 1 — libpcre2's PUBLISH-AT-CLOSE
answer per `backrefs_design.md`'s own R32 finding, `(0,2)` overall with
group 1 = `(1,2)`.)

**compile-accept — the trailing-backslash test vector, from a REAL corpus
pattern rather than a constructed one.** `tests/base/escapes.rxt:34`'s
`pattern \\` compiles a PCRE2 pattern whose raw source bytes are TWO literal
backslash characters (`\`, `\` — a pattern that matches one literal
backslash, `tests/base/escapes.rxt:35`'s own `m "\\" 0 1` cell, which is
itself a `.rxt` SUBJECT literal decoded through the SEVEN-escape
quoted-context vocabulary — a different vocabulary, for a different field,
per §4's own distinction). Serialized through this design's five-escape,
backslash-first rule, EACH of the pattern's two raw backslash bytes is
escaped independently and in sequence, producing FOUR characters in the
`Question` record:
```
Question:  compile-accept\t\\\\
Answer:    accept
```
This is exactly the shape §4's trailing-backslash test vector describes —
a pattern's own bytes ending, and in this case consisting entirely of,
literal backslashes — demonstrated on real, already-shipped corpus text
rather than an invented one.

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

**pattern-info** — D59's own opening-paren-order witness (R56-7's cited
population, `tests/probes/probe_named_groups.c:159`), which is the real,
already-measured pattern that motivated `rx_info.groups`' sort key in the
first place:
```
Question:  pattern-info\t(?<zeta>a)(?<alpha>b)(?<mu>c)
Answer:    3\t3\talpha:2 mu:3 zeta:1
```
(capture count 3, name count 3; the nametable comes back name-ascending —
`alpha`, `mu`, `zeta` — NOT in opening-paren order, which is `zeta`(1),
`alpha`(2), `mu`(3): D59's own measured fact, "a `zeta`/`alpha`/`mu`
declaration order comes back `alpha`/`mu`/`zeta`," reproduced here as this
kind's canonical answer shape rather than restated as prose.)

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
