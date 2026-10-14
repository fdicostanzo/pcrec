# Measurement sets — the format, the store, loading, the kit channel, the tool (rev 0)

Status: DESIGN ONLY, rev 0 (lane msetdes, 2026-10-14). Nothing is built; nothing under
`src/`, `cli/`, `lib/` or `tests/` changes. Plan row [MEASURE-SET]; ruled by D166 (read
D161 addenda 11-13, D162, D149, D157 with it). It is part of the framework Frank wants
before further optimization (plan row [REGIME]). Its first customer is the kit's R17-b′
(`memfn/r17b_prime.md` §3, whose measurement table is the needs list); the interim shape is
the kit's TSV from `memfn/regime_eval.md` Q-REVAL-10. The method a set is measured by is
`docs/dev/lanes/grid1_report.md` + `gridread_report.md`.

## 0. Answers first

Ruled by D166 and NOT re-opened here: sets (one box, one run, one method version, never
mixed); versioned and committed; the binary embeds the latest as the default; an older set
is selectable by name; selections move automatically with a mover census in the same
commit; values are RELATIVE (units of the scalar walk's per-byte cost, derived crossovers,
absolute ns only as provenance); loaded at COMPILE time (`--measures=FILE|NAME` + a config
line); the machine-side twin of the analysis object; key A = which set; the generic class
is a DERIVED envelope set labelled composite; answers never depend on the set; an
install-time tool can produce a set.

Recommendations (each priced below):

1. **Format (§1): a SIBLING of the analysis format, not the same file format.** A plain
   two-section TSV in `table_contract.md`'s wire shape (`[header]`, `[rows]`), integer
   values only (`value_e6`), one row per measured quantity keyed by seven owner-vocabulary
   dimensions, a per-row status (`measured`/`fitted`/`derived`/`null`), a per-row
   `form_hash`, a values digest in the header. Sets never `include` one another (the
   analysis chain's defining feature is the one thing a set must not have). It shares
   the house's TSV contract, its name grammar and its digest family, not the `.rxt` reader.
2. **Store (§2): `measure_store/<id>/<rev>/`**, `oracle_store/`'s shape (committed
   self-checking TSV + `PROVENANCE.md` + generator + `MOVERS.tsv`). `make gen-tables`
   embeds EVERY non-synthetic committed rev (a few KB each, so rollback needs no repo) as
   text and pre-parse, as findings B1 does, with a per-class default pointer file.
   Immutable once committed; a re-measure is a new id, a corrected re-read is a new rev.
   Staleness is COMPUTED (row `form_hash` against the kit's current form hash), never
   edited into a file; a stale DEFAULT is a test failure, a stale older set is a listing
   flag.
3. **Loading (§3): `--measures=NAME|FILE|NAME@REV`**, config line `measures`, exactly
   `--analysis`'s precedence (fill-only; the file wins, D93, a disagreement reported in
   `tune`'s shape). One new every-artifact stamp `<PREFIX>_MEASURES` = `none` or
   `id@rev:digest16`; ONE abi event (it rides R17-b′'s, Q-R17P-2, or lands alone if
   [MEASURE-SET] builds first); `rx_info` mirror waits for [IFACE-PUSH]. A DEFAULT-set
   change is NOT an abi event (the `<PREFIX>_FINDINGS` precedent, findings.md 5¶9): it is
   a census + identity re-pin.
4. **Kit channel (§4): `mf_measures`, as `r17b_prime.md` §4.3 proposes**, plus one return
   fact: the kit reports the keys it LOOKED UP (found or absent). pcrec builds the stamp,
   the per-artifact listing and the census attribution from that report. An absent or
   `null` row is SKIPPED; there is no fall-through to another set and no nearby key.
5. **`--list-measurements` (§5):** three views (sets, one set with decoded rows and reader
   rows, a per-target view over a `.rxt` file / `--emit-facts` for a pattern), in
   `--list-analysis`'s shape. Reader rows come from each owner's declared decision table.
6. **Envelope (§6):** a script derives a composite set from the latest official set of each
   box in an ISA level, per-row `env` direction (`max`/`min`/`none`) declared by the
   quantity's method. A key absent from any member is excluded. n=1 is legal and labelled.
7. **Install tool (§7): one driver, `pcrec-measure`, in a new `measure/` directory** (C,
   zero-dependency like `pcrec-analyze`, compiling probes with `$CC` at run time), running
   owner-supplied METHOD modules (the kit's harness mode for kit quantities, pcrec's for
   its own). It measures only quantities that have a reader row, gates the run on A/A
   noise (refuse) and each row on the NULL rule (absent), writes tier `local`, never a
   default, never an envelope member.
8. **Independence (§8):** answers checked against the .rxt oracle under every committed
   set plus three synthetic extremes; derived rows recomputed by an independent python
   from the closed derivation registry; the census compiles a pinned population under old
   and new; ten sabotage rows S943-S952.
9. **Plan (§9):** M0 rides R17-b′ (reader, store, one set, stamp, listing, kit seam); M1
   `--measures=` + census + tests; M2 envelope; M3 the tool. Eight questions for Frank
   (§9.4); the two that matter are Q-MS-1 (what a bare compile reads) and Q-MS-2 (a
   default-set change is not an abi event).

## 1. The set FORMAT

### 1.1 What a set holds

Everything R17-b′ §3.2 lists (18 families, about 45 values), plus pcrec's own engine
quantities (armread's `C_call`, `c_byte`) when their reader rows exist. Four properties
force the shape:

- **Owners.** pcrec parses and validates the container and never interprets a kit-owned
  key (D157: the kit's vocabulary, the kit's method). The format therefore fixes the
  DIMENSIONS and leaves their VALUES to the owner.
- **Integers only.** A selection reads integers (`value_e6`), as `r17b_prime.md` §4.3
  proposes: no float in a selection, so no platform-dependent threshold.
- **Absence is data.** A quantity can be unmeasured (no row), measured-but-null (below the
  NULL rule, gridread §1.2), or present. The three must be told apart in the listing and
  must read identically (skip) in a selection.
- **Provenance travels with the value.** A reader of a number in a listing can name the
  run, the method version, the box and the code it was measured on.

### 1.2 The file

A set is ONE file, `set.tsv`, in `table_contract.md` §4's section shape (comment lines `#`,
a header row naming every column, append-only columns, resolution by header name).

```
# pcrec measurement set (spec: docs/spec/measures.md)
[header]
key	value
format	1
id	zen4-grid2
rev	1
class	x86_64-avx2/zen4
isa	x86-64-v3 avx2 sse4.2 popcnt bmi2
tier	scratch
composite	0
unit_key	kit.beta.walk.PF.-.1t0e0c.-
method	grid2@1
run	slot grid2, 2026-10-xx
box	AMD Ryzen 7 7700X; governor performance; kernel ...
compiler	gcc 15.2.0 -O2
code_commit	<measured-code commit>
rows	47
values_digest	<16 hex>
[rows]
quantity	form	vs	kind	shape	layer	subject	unit	value_e6	abs_ns_e6	noise_e6	n	status	derivation	inputs	env	form_hash	source
...
```

Header (one line each, `key<TAB>value`): `format`, `id`, `rev`, `class` (ISA level
`/` tuning class: the A of D161 add. 11, spelled by whatever axis [R4g `--isa`] settles),
`isa` (the box's availability at measurement time; PROVENANCE and an applicability check,
§3.4, NOT a selection input: "ISA availability stays a separate fact"), `tier`
(`scratch` | `official` | `local` | `synthetic`: D144 add. 4; `local` is §7's, `synthetic`
is the test fixtures'), `composite` (1 for an envelope), `members` (envelope only: `id@rev:digest16`
list), `unit_key`, `method`, `run`, `box`, `compiler`, `code_commit`, `counters` (§7.4a), `rows`, `values_digest`.
One run means the header's provenance is the set's and every row inherits it. Row-level
columns carry only what varies by row.

Row columns:

| column | meaning |
|---|---|
| `quantity` | `OWNER.name` (`kit.beta`, `kit.cross`, `pcrec.c_call`). The owner prefix is the namespace; pcrec never reads a `kit.` value |
| `form`, `vs`, `kind`, `shape`, `layer`, `subject` | the key dimensions. `form` and `vs` the measured form and the compared form; `kind` the site kind (`PF`, `PF-bounded`, `DFA-hat`, `VM-hat`, `ANY`); `shape` the cover multiset `r2e0c0` (R17-b′ §3.1); `layer` SIMD-on/off; `subject` the condition (`fit-repeated`, `streamed`, `fresh`: regime_eval Q-REVAL-10's per-row subject condition). `-` = not split by this dimension. Values are the owner's vocabulary; the FORMAT fixes only that a dimension is a short token and the full key is the `.`-join of the seven |
| `unit` | `ratio` (dimensionless, to the unit row), `walkbytes` (u·B), `bytes`, `count` |
| `value_e6` | the value × 10^6 as int64. Empty iff `status` is `null` |
| `abs_ns_e6` | provenance only: the absolute ns (or ns/B) × 10^6. No reader may read it (the independent parser's check, §8) |
| `noise_e6` | the row's measured noise as a fraction of the value × 10^6 (gridread's A/A floor for its group) |
| `n` | launches × rounds behind the row |
| `status` | `measured` (read straight off the run), `fitted` (a fit or an interpolation over cells not in the set; the fit transcript hash is in the row's `source`), `derived` (recomputable from `inputs`, `derivation`), `null` (measured; indistinguishable from no effect under the NULL rule) |
| `derivation`, `inputs` | for `derived`: a name from the CLOSED registry (§1.5) and the row keys it reads |
| `env` | `max` / `min` / `none`: the envelope direction (§6), declared by the quantity's method |
| `form_hash` | the hash of the measured form's text as the kit emitted it (staleness, §2.4). pcrec treats it as opaque |
| `source` | free text: the report section / script and its commit. Display only |

Why seven dimensions as fixed columns and not one opaque key string: the listing can filter
and sort on them, the staleness and applicability checks can group on `form` and `layer`,
and a sanity checker can require `(quantity, key dims)` unique with no knowledge of any
owner's vocabulary. The cost is that a new dimension is an appended column, which
`table_contract.md` §2 already makes cheap. The kit's key string (`kit.beta.V1.ANY.r2e0c0`)
is the canonical join of the columns, so nothing in `r17b_prime.md` §4.3 changes.

### 1.3 The relative unit

The unit row is `unit_key`, a row with `unit ratio`, `value_e6 1000000` by construction
and its absolute in `abs_ns_e6`. R17-b′ §3.1's choice stands as the FIRST set's unit: u =
β_walk(PF, 1 term) = 0.1892 ns/B. The format does not fix WHICH row is the unit; it fixes
that exactly one is named in the header, that it is a `ratio` of value 1.0, and that no
other row's `value_e6` was computed against a different row. The checker enforces the
last by recomputing every `ratio`/`walkbytes` row's `value_e6` from its `abs_ns_e6` and
the unit row's `abs_ns_e6` to within rounding (§8.2). That check is NOT circular: the
producer writes both columns from the raw run; the checker re-derives one from the other.

A set whose unit row is noisy is noisy in every row. So the unit row's `noise_e6` is
gated more tightly than any other (§7).

### 1.4 Crossovers

A crossover is a ROW, in `bytes` (or `count`), `status derived` where its inputs are in the
set (L* = (F_b − F_a) / (β_a − β_b), the single-call crossover from M7/M8's fixed parts and
M3-M5's per-byte costs) and `fitted` where its inputs are cells the set does not carry (g*
interpolated in log2 g over the grid: the raw cells stay in the run's transcript, whose
hash is in `source`). A selection reads the crossover, never recomputes it. The reason is
the same as `memfn/r17b_prime.md` §2.6's: a literal in the emitted dispatch must equal a
set value, so the structural check (§8.1) can compare them.

Why not store only costs and let every reader derive the crossover: two readers would
derive it twice (the kit's finder and pcrec's `cand_rows[]`), and the `fitted` crossovers
have no derivable inputs. Why not store only crossovers: the pay rule (R17-b′ §2.5) needs
costs, and a listing that shows only the output hides the inputs the reader must be able to
check.

### 1.5 The derivation registry

`derivation` names a function from a CLOSED list in the spec (`docs/spec/measures.md`),
each given as a formula in text, and implemented independently in the producer (C) and in
the checker (python, §8.2):

`ratio` (a / b), `diff` (a − b), `cross-lin` ((F_b − F_a) / (β_a − β_b), bytes), `step`
(the block width: DERIVED from the form's width, not measured), `min`/`max` of inputs.

A new derivation is a spec row plus both implementations. A row whose derivation is not in
the registry is refused at load. The closed list is what makes "recomputes from its rows" a
check rather than a promise.

### 1.6 Self-checking

- `rows` equals the row count (K35: the producer is not the counter).
- `values_digest` = FNV-1a-64, 16 lowercase hex, over `pcrec-meas-1\0` followed, for each
  row in the sorted canonical-key order, by the key, `\0`, the unit byte, the status byte,
  and `value_e6` as int64 LE (empty value = `INT64_MIN`). It excludes every provenance
  column, so the same values from any provenance give the same digest, exactly the
  `<PREFIX>_FINDINGS` digest's property (findings.md 5¶6). `PROVENANCE.md` (§2.1) carries
  a sha-256 of the whole file for transport integrity.
- Keys unique; every `derived` row's inputs present; every `env` in its domain; every
  `unit` in its domain; exactly one unit row; unknown columns tolerated (`table_contract.md`
  §3¶2); unknown dimensions tokens tolerated (they are the owner's).

### 1.7 Sibling or same file? (priced)

| | A: sibling TSV (RECOMMENDED) | B: a `measures` block kind inside `.rxt`'s `analysis` | C: JSON / a C header | D: the kit's interim TSV, unchanged |
|---|---|---|---|---|
| reader | a ~150-line TSV reader (the house has one for every listing) plus the digest | the `.rxt` reader, which exists for `-I` resolution | a new parser | exists, kit-side only |
| fit | rows are keyed, numeric, provenanced; no counts, no derivation from counts | an `analysis` block is COUNTS with named derivations (`unigram`, `markov1`); a measurement row is a fourth kind with none of the block machinery | n/a | kit-only; pcrec's own quantities need a second file |
| `include` | none (D166: never mixed) | the analysis chain's whole design is `include`, first-block-serves; a set must forbid it, so the block must be a special case | n/a | none |
| compile-time reader | a fixed parser, tiny, shared by `pcrec` and `pcrec-measure` | a full `.rxt` parse for 47 rows | n/a | n/a |
| editing by hand | possible (a test fixture is a TSV) | possible | worse | possible |
| risk | one more file type | `analysis` semantics leak into sets (the chain, `serves`) | a second data language | the Q-REVAL-10 interim; unowned columns |

Recommendation A. B buys name-resolution reuse (the `-I` search) which §3 gets by calling
the same search function over a different suffix, and pays for it with a block that has to
refuse everything an analysis block is for. Q-REVAL-10's interim TSV becomes a strict
subset of A's columns (it adds `subject`; the evaluator's reader keeps working on the
shared columns by header name, `table_contract.md` §3): the migration is a column-adding
conversion, not a rewrite.

## 2. The STORE

### 2.1 Layout

```
measure_store/
  CLAUDE.md  README.md            # the index and the maintenance note (third_party's shape)
  DEFAULTS                        # one line per class:  <class> <TAB> <id>   (the default pointer)
  index.tsv                       # one row per committed rev: id, rev, class, box, tier, composite,
                                  #   supersedes, values_digest, status (default|older|synthetic)
  generate.py                     # gen-tables hook (§2.3); validates and embeds, names no set
  envelope.py                     # §6
  zen4-grid2/
    1/
      set.tsv                     # the set, self-checking
      PROVENANCE.md               # what derives from it; sha-256 of set.tsv; the run, the method, the
                                  #   reader script + commit; the raw transcript's location and hash
      MOVERS.tsv                  # the census versus `supersedes` (§8.4); empty for the first set
      raw/                        # the SMALL raw (the reader's input digests); big raw stays in the slot,
                                  #   hash in PROVENANCE.md
```

This is `oracle_store/`'s shape (one directory per source, self-checking TSV,
PROVENANCE, a generator) applied to data derived by RUNNING pcrec's kit and engines on a
box. It is not `third_party/` (nothing is vendored from outside). The analysis object's
`src/findings/*.rxt` is the sibling for the data side. A new top-level directory is
`measure_store/`, not `measures/` (R17-b′ §3.5's spelling), to line up with `oracle_store/`;
a one-token choice, Q-MS-4.

### 2.2 Naming, versions, rollback

- `id`: `[a-z][a-z0-9_-]*` (the analysis name grammar), `<class-token>-<run>` by convention
  (`zen4-grid2`). Global across the store; a user set may not reuse a committed id
  (§3.3).
- A committed rev is IMMUTABLE. A re-measure on the same box is a NEW id (`zen4-grid3`),
  because it is a new run. A corrected RE-READING of the same raw data is a new `rev`
  of the same id (`zen4-grid1` rev 2, as gridread re-read grid1). `NAME` resolves to the
  latest rev, `NAME@REV` pins one. The stamp always carries both.
- ROLLBACK is `--measures=zen4-grid1@1` (or a config line naming it). Because every
  non-synthetic rev is embedded (§2.3), rollback works from an installed binary with no
  checkout.
- Supersession is recorded in `index.tsv` (`supersedes`), which is also what the census
  reads (§8.4).

### 2.3 The default, and `make gen-tables`

`DEFAULTS` maps each class to one id. `generate.py` (one script, like `third_party/*/
generate.py`, and called from the same `gen-tables` loop; it NAMES NO SET) does, for every
rev in the store:

1. validates it (§1.6, with the same rules the loader enforces, the python twin);
2. emits `src/core/measures_store.inc` (every non-synthetic rev's TEXT) and
   `src/core/measures_table.inc` (its PRE-PARSE: rows as static const arrays) from the one
   committed text, on findings B1's pattern (both committed, an agreement check
   `tests/measures/` compares text with pre-parse). Sets are small, so the parse could be
   lazy and skip the pre-parse; the pre-parse is kept for ONE reason: the loader's
   no-filesystem mode must be the same code path as findings';
3. emits the default pointers.

`make gen-tables && git diff --exit-code` covers the chain, as it does for findings and
`third_party/`. The embed is committed; a plain `make` does not regenerate it.

Embedding every rev, not only the default: 47 rows is about 6 KB of text per set, 15 KB
with the pre-parse. Ten committed sets is below the size of one `fold_tables.inc`. The
alternative (default only, older sets loaded from files) makes rollback depend on a
checkout and makes a bench result's `--measures=zen4-grid1` unreproducible from a release
build. Q-MS-7.

### 2.4 Staleness

A row is STALE iff its `form_hash` differs from the hash of the form the kit would emit
NOW. The kit exposes `mf_form_hash(form_id)` (a fact it returns, not a method pcrec
presumes); pcrec stores and compares opaque strings.

- Staleness is COMPUTED by `make test-measures` and by `--list-measurements` against the
  linked kit. It is never written into a committed file (immutability).
- A STALE ROW in an older set is allowed and flagged in the listing (`stale 1`): it is a
  true measurement of code that no longer exists, which is exactly what rollback is for.
  It is still READ by a selection that asks for that set, because skipping it would move
  the selection with no measurement behind the move (a silent default, the thing
  `pcrec-no-silent-defaults` forbids).
- A stale row in a DEFAULT set fails `make test-measures`. The default is the set the
  current code was measured on; a form-text change in the kit forces a re-measure or a
  rev before it can land. That makes the kit's form change and the set's refresh one
  landing, the same cadence the abi ritual has (D76/D94).
- A form hash is of EMITTED TEXT for the form, not of the kit source tree: a refactor that
  leaves the text byte-identical does not stale a row.

## 3. LOADING

### 3.1 The surface

- `--measures NAME|NAME@REV|FILE` (or `--measures=...`): a `--pattern` compile or each
  target of a file operand. Legal with a compile and with `--list-measurements`; refused
  elsewhere (`--analysis`'s list, cli.md 1.1.2).
- `.rxt` config line `measures NAME|NAME@REV|FILE`, one per config (the `analysis` line's
  place). Inside the `pcrec` config line is refused when the file is read (as `--analysis`).
- Library: a `pcrec_options` field, appended in the same [IFACE-PUSH] batch the analysis
  field belongs to (§3.6).

### 3.2 Resolution

A value that matches the id grammar (optionally `@REV`) is a NAME; anything else (contains
`/` or `.`, or an existing path) is a FILE. A NAME is looked up in the search path first
(`-I DIR`: `DIR/NAME.measures.tsv`, the analysis rule's `DIR/N.rxt` analogue), then the
store. A FILE is read directly. An unknown name refuses the compile and names the stops
searched.

### 3.3 Precedence (D93)

Identical to `--analysis`: fill-only. A target whose config names `measures` gets that one;
`--measures` names it for targets whose configs name none. A disagreement is reported in
`tune`'s shape with the file winning ("... CLI --measures X and this file's measures Y
disagree; using the file's value (--measures is fill-only)"). A single value per compile:
sets are never mixed, so there is no per-quantity precedence and no chain.

A user set may NOT take a committed id: a `-I` or FILE set whose `id` is in the store with a
different `values_digest` is refused ("id X is a committed set; rename"). The stamp names a
set by `id@rev:digest`, so a shadow would make a stamp point at a set that does not carry
those values.

### 3.4 What a bare compile reads (Q-MS-1)

Priority: explicit flag, then config, then the BUILD'S default for the compile's class.
The class is the A the compile declares (ISA level + tuning class, once the axis exists);
a compile that declares none is the "idk" class. Two readings:

- **Literal D166 reading ("compiled with the latest set"):** a bare compile reads the
  latest committed set. With one measured box, that applies Zen 4's thresholds to every
  machine.
- **D161 add. 12 reading (RECOMMENDED):** an unmeasured or unspecified class reads the
  GENERIC envelope for its ISA level, and "latest" is per class. With one box the envelope
  of {Zen 4} is Zen 4's rows labelled `composite n=1` (honestly derived, honestly flagged),
  and the second box (F5, Zen 1) moves it. The listing shows which.

The second reading is what add. 12 says (an unmeasured specific class reads generic, never
WALK) and it keeps a stamp's `class` meaningful. The first is simpler and wrong the moment
the second box exists. Recommend the second; the difference at n=1 is the label.

ISA applicability: the set's `isa` header against the compile's declared target. A row
whose `form` needs an ISA the target lacks is inapplicable and skipped, listed as such in
the per-target view; the target not being the measuring box is the POINT of key A and is
not an error.

### 3.5 The stamp

`<PREFIX>_MEASURES` in every artifact, beside `<PREFIX>_FINDINGS`:

- `"none"` iff no lookup was attempted: no selection in this compile asked for a set
  value (the kit's report, §4, plus pcrec's own readers). Then the artifact bytes are the
  same under every set (an invariant §8.1 checks).
- otherwise `"<id>@<rev>:<values_digest>"`: the active set, full 16-hex digest (the
  FINDINGS stamp's width; R17-b′ §5.3 proposed 8, Q-MS-8). A lookup that found nothing
  still counts as a lookup: the artifact depends on the set because an absent row skipped.

The stamp names the SET, not the rows read: the artifact is a function of (pattern,
options, analysis, measurements), and the measurements are the set. The rows actually read
are recoverable by the per-target listing (§5.3), not stored in the artifact (bytes).
The macro is plain text, so a shipped binary discloses the set id; name sets neutrally
(findings.md 5¶8).

### 3.6 The abi event and its readers

The stamp is emitted scaffolding in every artifact: `abi` bumps (78 → 79 today) and the
identity gate re-pins, in the same change (D76/D94). The readers are found BY GREP when it
lands, from this floor (R17-b′ §5.2's list is the authority; mine is the cross-check):
`PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c`); match_api.md's K80 `#error` text and its
"abi is N" sentence and §6.3's stamp table; `docs/dev/history/abi_changelog.md`;
`run_codegen_tests.sh`'s `ABI_EXPECT`; `run_recursion_identity.sh`'s FILEPIN / `ABI_SUBJ`;
the alpha scripts' normalizers; the byte-count readers
(`tests/codegen/manifests/m5_stage1_stamps.tsv` `EMITTED_BYTES`, `run_resource_tests.sh`'s
`a{5,25000}` count, the size-term and K59/K53 rung witnesses, the cpset manifest,
emit_sweep's `VARIANT_PINS`); the mover-by-ID manifests that read VM-hat or PF-site text;
then the registry, codegen and rxtsource suites (D94 addendum), `make test-codegen`.

This design adds NO second abi event: if R17-b′ builds first, the stamp rides its bump; if
[MEASURE-SET] M0 builds first, M0 is the bump and R17-b′ rides a later one with its own
readers. A `rx_info.measures` mirror is NOT added now: an `rx_info` member is an
[IFACE-PUSH] batch item (Frank 2026-10-10) and nothing reads the mirror yet (the bench and
[ART-MGR] read the macro). A DEFAULT-set change, or any new set, is not an abi event: the
scaffolding is unchanged, the selection moved. The precedent is findings.md 5¶9 ("a change
to the shipped data moves the digest of every artifact that consumed it"). What it does
move is the identity gate's (B) pin and the EMITTED_BYTES readers, which the census (§8.4)
enumerates and re-pins in the same commit. Q-MS-2.

### 3.7 The cache key

[ART-MGR]'s cache key becomes (pattern, options, analysis digest, MEASURES digest of the
LOADED set), the set digest regardless of whether anything read it: the cache is consulted
before the compile that would report `none`. Two sets that differ only in rows nobody read
produce byte-identical artifacts under different keys, which the cache's content hash
dedupes on the store side; a key on the READ subset is an unlock (§9.3) with a measured
trigger (recompile churn), not a start.

## 4. The channel to the kit (facts only, D157)

### 4.1 What pcrec hands over

`mf_measures` is `r17b_prime.md` §4.3's struct, unchanged in spirit: per compile, on
`mf_art` (not per site, not on the analysis's per-site placement: every site of a compile
reads one set, and a per-site pointer would let two sites disagree). It carries the
parsed rows keyed by the canonical key string, `value_e6`, `unit`, `status` (the kit must
tell `null` from absent only for its listing), the set `id`, `rev`, `values_digest`,
`class`, `tier`, `composite`. pcrec computes no threshold and hands over ALL rows; the kit
ignores keys it does not own (`pcrec.` rows) and unknown keys (totality).

It does not hand over `abs_ns_e6`, `noise_e6` or `source`: provenance is pcrec's listing's,
not the kit's input. A kit that wants noise reads `noise_e6` through a fact added to the
struct by a REQUEST (`memfn/docs/requests.md`, single writer: main), not by default; no
selection reads noise today.

### 4.2 What the kit returns

One new fact: after `mf_art_end`, the kit's report lists each key it LOOKED UP with
`found` (present / absent / null / inapplicable). pcrec uses it for the stamp (§3.5), the
per-target listing (§5.3), the census attribution (§8.4). This is the kit's output (what it
did), not pcrec presuming its method, so D157 holds. It is a request to file (R-n, main's
to file per `pcrec-requests-are-mine-to-file`); it is also the one seam change the kit
sees beyond R17-b′'s own.

`mf_form_hash(form_id)` (§2.4) is the second return fact. Together with the reader table
(§5.2) these are the kit's three outputs to the framework.

### 4.3 An unmeasured quantity

A row that resolves to absent, `null` or inapplicable is NOT EVALUABLE: the row is skipped
as a row needing E is skipped when E is absent (r17b_prime.md §3.4). No fallback to another
set; no fallback to a nearby key. The decision falls through to the next row; the table's
last row (R7, LINER) reads no set value, so the table is total with an empty set or none.
"Never a presumed value" and "the generic class" fit together as follows: generic is
chosen BEFORE the compile, by set (§3.4), never inside it by quantity. A quantity that
is unmeasured IN the chosen set falls to the table's own default; it does not borrow the
generic set's value, because that would mix two runs, which D166 forbids.

## 5. `--list-measurements`

In `--list-analysis`'s family, `table_contract.md` sections, a [LIST-TABLES] member. Legal
alone, with a NAME, or with a `.rxt` operand.

### 5.1 `--list-measurements` (no argument): the sets

Section `sets`: `id`, `rev`, `class`, `box`, `tier`, `composite`, `members` (an envelope's),
`supersedes`, `default_for` (the classes it is the default of), `rows`, `stale`
(computed against the linked kit), `values_digest`, `source` (store | `-I` file).

### 5.2 `--list-measurements NAME|FILE`: one set

Sections:

- `header`: the §1.2 header, verbatim.
- `rows`: every row decoded: the key dims, `unit`, the VALUE as a decimal, `status`,
  `abs_ns`, `noise`, `n`, `form_hash`, `stale`, `source`, and **`readers`**: the decision
  rows that read this key, as `owner:row-id` items. Readers come from each owner's
  DECLARED decision table: pcrec's `cand_rows[]` registers its keys; the kit supplies its
  finder table's key references (`mf_finder_readers`, the third output of §4.2; R17-b′ §1.4
  already lists the table with the active set's provenance). A row with no reader is
  printed `readers -` and counted.
- `readers`: the converse. Every decision row, its keys, and per key `present` / `absent` /
  `null` in THIS set: a reader table row with an absent key is exactly the place
  R17-b′ §3.3 says "no dispatch is emitted" reads out. This section is the audit that the
  skip is honest.

### 5.3 The per-artifact view: `--list-measurements FILE.rxt` (and `--emit-facts`)

For each target: which set it resolves to and by which stop (flag, config, build default),
and a section `reads`: each key the compile looked up, `found`/`absent`/`null`/
`inapplicable`, the value read and the decision row that read it. It is produced by
running the compile (so the kit's report, §4.2, is its source) and discarding the
emitted text, like `--list-analysis FILE`'s per-target view. A `--pattern` compile gets
the same rows as an `--emit-facts` section, in that listing's existing shape (a spec hunk
in cli.md §2.11 at build).

### 5.4 Checks that read the listings

A reader coverage check (`make test-measures`): every committed non-synthetic row has at
least one reader OR is marked provenance-only in the method doc; every reader key resolves
in at least one committed set OR is declared ABSENT-known (R17-b′'s M16-M18 now). The
population is counted by an awk over the TSVs, not by the listing (K35).

## 6. The generic ENVELOPE set

A DERIVED set (`composite 1`) for an ISA level, built from MEASURED sets, labelled
composite everywhere (header, stamp class, listing).

- **Inputs:** the latest rev of the latest official-tier set of each tuning class in the
  ISA level. A `scratch`, `local` or `synthetic` set is never a member; the envelope's own
  tier is the LOWEST of its members' (so a Zen-4-only envelope today is `scratch` until
  the bench run makes grid2 official).
- **Rule (mechanical):** a key enters the envelope iff it is PRESENT AND NON-NULL in every
  member, and its value is the members' `max` or `min` per the row's `env` column. `env`
  is declared by the quantity's method, because the conservative direction depends on the
  loss asymmetry the reader row has: "pick the wider form when n ≥ L*" is safe at the max
  L* over boxes; "pick the walk when g < g*" is safe at the min g*. `none` excludes the row
  (a cost whose envelope has no safe direction, e.g. a per-byte cost the pay rule divides
  by). A key missing from any member is excluded, not imputed: the envelope never presumes
  a value for a box that has none.
- **What is lost:** costs (the unit row, `β`) do not envelope, so the envelope holds
  crossovers and flags, and a pay rule that needs costs falls to its `unpaid` pick under
  the envelope. That is the honest consequence, not a bug; it is priced at the first
  second box (§9.3).
- **Derivation script:** `measure_store/envelope.py CLASS MEMBER...` writes
  `measure_store/<envelope-id>/1/set.tsv`; each envelope row is `status derived`,
  `derivation env-max`/`env-min`, `inputs` the member keys. So the §8.2 recompute check
  covers envelope rows with no new machinery. Header `members` lists `id@rev:digest16` per
  member.
- **Labelling:** the id is `generic-<isa-level>-<n>`; the listing prints `composite n=K
  members=...`; the stamp is the ordinary `id@rev:digest16` (the id says generic).
- **Regeneration:** a new member set or a rev of a member makes a NEW envelope id; the
  default pointer moves with a census. Nothing re-derives in place.

## 7. The install-time tool

### 7.1 Home: one driver, owner-supplied methods

`pcrec-measure`, a standalone C binary in a new `measure/` directory, built by `make`
beside `pcrec-analyze`, not linking `libpcrec` (the `analyze/` pattern: zero-dependency;
an install on a stranger's machine needs `make` and `$CC`, which pcrec already requires).
It owns what is shared across owners: run control (quiet gate, governor, affinity, A/A
pairs), the NULL rule, the set writer and its self-check, naming and immutability. It
runs METHOD modules the owners supply: a kit quantity is measured by the kit's harness
mode (the forms and their timing arms are the kit's, D157), a pcrec quantity by pcrec's
probes (armread's engine arms). The driver compiles each probe with `$CC` at run time.

Priced alternatives: (b) a mode of the kit's harness only: the kit would own the set format
writer for pcrec's quantities too, which inverts the ownership (the kit owns its rows, pcrec
owns the plumbing) and gives pcrec a build dependency on the kit's harness for a
pcrec-owned set; (c) one script (python): the grid1 reader is python, but install-time
must not need python; (d) keep measuring only in slots and ship sets: leaves out the
D166 install-time case entirely. Recommend the driver.

### 7.2 What it measures

The reader closure: the quantities with at least one reader row (§5.2), computed from the
listing at run time. Removing a decision row removes its measurement; a quantity nobody
reads is not measured (D77: no measurement ahead of a reader). It measures CROSSOVERS and
the costs those crossovers derive from, not the full grid: the quick profile covers the
single-call crossovers (M7-M12), β by shape (M3-M5), the dispatch charges (M16-M18 once
they have a method) and a reduced g* ladder. The full profile is grid1's, run in a slot
(§7.5), not at install.

### 7.3 The noise gate

Two levels, because a bad run and a bad row are different:

- **Run level, REFUSE:** the quiet gate (load1, governor `performance` where the OS exposes
  it, affinity held), the A/A pairs on every group, and a refusal (exit status 3, a
  diagnostic naming the worst group, NO set written) when the p90 A/A floor exceeds the
  gate. grid1's p90 was 3.09% on the quiet dev box (gridread §1.1; the walk's, not the
  forms'). The initial gate is **2 × that = 6.2%**, a LABELLED UNMEASURED DEFAULT (D149,
  `pcrec-suspect-tuning-constants`): derive it from the committed official sets' observed
  p90 once there are two boxes. The unit row's noise is gated at half.
- **Row level, NULL:** a row whose effect is within `max(A/A, base floor)` is written
  `status null`, with no value, never a rounded number (gridread §1.2's NULL rule).
  A set may be PARTIAL; the header counts `rows` and the listing counts NULL rows. Partial
  is legal: absent rows skip.

### 7.4 What it writes

Tier `local` (§1.2): never a default, never an envelope member, never committed (it is
written to a path the user names, `build/measure/` by default). Its id is `local-<host
hash>-<date>`; it can be used by `--measures=FILE` or installed as the build's default with
`make DEFAULT_MEASURES=path` (a build-time re-embed; no environment variable, no hidden
run-time state). The stamp then reads `local-...@1:digest`, and a shipped artifact says
it was built under a local measurement.

### 7.4a Perf counters are OPTIONAL (D166 addendum 1, addendum 1.1)

No set, method, gate or tool may REQUIRE perf counters (`kernel.perf_event_paranoid`
varies per box). Every set must be producible from TIMING ALONE, and every gate in §7.3
reads timing only (A/A floors, the NULL rule). A branch-miss pass (gridread F2's
predictability diagnosis) is an optional DIAGNOSTIC: when counters are unavailable it
SKIPS LOUDLY (one stderr line naming the cause) and the skip is RECORDED in the set's
provenance. Header gains `counters` = `none` | `skipped:<reason>` | `branch-misses` (and the
paranoid value read), so a listing shows whether the diagnosis exists for that set. No row's
`status` or selection depends on it; counter-derived rows, if a method adds any, are
`measured` extras that readers may not require (an absent counter row is skipped like any
absent row).

When counters are unavailable the tool PRINTS A SUGGESTION AND NEVER ACTS ON IT (it does not
run sudo, sysctl or write /etc). The text shows the current `kernel.perf_event_paranoid`
value; that 2 or lower enables the optional counter pass; what it adds (branch misses, the
predictability diagnosis); and the commands: one-off
`sudo sysctl kernel.perf_event_paranoid=2`; persistent: put
`kernel.perf_event_paranoid = 2` in `/etc/sysctl.d/99-perf.conf`. A check asserts the
suggestion text is printed with counters denied and that no set content differs between a
counters-on and counters-off run except the `counters` header and optional extras.

### 7.5 Wall time

Install target: **5 minutes, labelled a TARGET, unmeasured** (the quick profile is not
built; the number is a design budget). The official profile is grid1's shape: five
launches, A/A per group, about 83 minutes on grid1 (19:33-20:56), run by a bench slot
request, never at install. A `--profile quick|full` flag selects; `full` refuses to run
unless the box is idle by the gate.

## 8. Independence checks

### 8.1 Answers are identical under every set

`make test-measures-answers` (this is the generalized `test-memfn-sets` of R17-b′ §6.4;
that name is kept for the kit's half). The population: the R17-b mover sample (1 in 8 by
pattern) plus every `.rxt` cell for those patterns, compiled once per committed set and per
SYNTHETIC extreme set (`all-walk`, `all-v1`, `all-wide`: test fixtures, tier `synthetic`,
never embedded, never a default; reached by `--measures=FILE` from M1 and by the harness
lever until then). The EXPECTATION is the `.rxt` cells' oracle-verified answers
(libpcre2 / python `re`): the artifact is compared with the oracle, not with another
artifact, so the control shares no source with the subject (learnings §3). A secondary arm
compares artifacts built under two sets on the same subjects (a differential), as a
detector for the case where both could be wrong the same way. A K35 floor counts, per
synthetic set, the sites that reached each form; zero reach is a failure ([MECH-REACH]).
A third arm checks that `<PREFIX>_MEASURES` is `none` exactly when the artifact's bytes
are identical across all sets.

The structural arm: each artifact's dispatch literals equal the set's values as read by an
INDEPENDENT parser of `set.tsv` (the python twin), and the stamp names the loaded set.

### 8.2 Derived rows recompute; units recompute; digest agrees

`tests/measures/recompute.py` reads only `set.tsv` and the spec's registry text. It
recomputes (a) every `derived` row from its `inputs` by the registry formula, (b) every
`ratio`/`walkbytes` row's `value_e6` from `abs_ns_e6` and the unit row, (c) the
`values_digest` and `rows` count, (d) every `env-max`/`env-min` envelope row from its
member sets' files. The producer (C) and this checker (python) implement the same
registry from the spec's formulas, not from each other. `fitted` rows are not
recomputable: the check COUNTS them (population: derived / fitted / measured / null per
set, a floor on the recomputed fraction, K35), and requires each `fitted` row's `source`
to carry a transcript hash that exists in `PROVENANCE.md`.

### 8.3 Embedded = committed

`tests/measures/` compares each embedded text with the committed `set.tsv` byte for byte,
the pre-parse with a fresh parse (findings tests §2/§3), and `make gen-tables && git diff
--exit-code` covers the chain. The default pointer's id must exist, its class must match,
and its rows must not be stale (§2.4).

### 8.4 The mover census

The mechanism for D166's "selections move automatically, with a mover census in the same
commit". `scripts/measure_census.sh OLD NEW` compiles a pinned POPULATION under
`--measures=OLD` and `--measures=NEW`, strips the stamp line, and compares emitted bytes.
Its output is `MOVERS.tsv` in NEW's directory: the artifact id, old and new byte hashes,
and the attribution (the `reads` rows whose value differs, from §5.3). The population is
`tests/measures/census_population.tsv` (the identity gate's corpus as the start; the exact
file is pinned at M1 by grep), COUNTED by an awk over that file and floored.

The state check (no git history needed, CI is shallow): for every non-first set in
`index.tsv`, `MOVERS.tsv` exists, its header names `supersedes` and `values_digest`
equal to the index's, and re-running the census at HEAD gives the same file. A default
change without a census, or a census run against the wrong predecessor, fails.
Also re-pinned in the same commit and found by grep: the identity gate's (B) pin and the
EMITTED_BYTES readers (§3.6) when the default changes.

### 8.5 Sabotage plan (S943-S952)

Each has a REACH counter (the number of times the planted branch executed in the sampled
run) and fails the named check; none is answer-detectable except where stated.

| id | plant | detected by |
|---|---|---|
| S943 | `values_digest` excludes one column (a value changes, the digest does not) | §8.2(c); the independent digest |
| S944 | an absent or `null` key read as 0 | a set with the key removed must produce the table's last row only (R17-b′ SB8) |
| S945 | the stamp names the build default when `--measures` loaded another | §8.1 stamp arm; SB10 |
| S946 | `--measures` beats the config line (fill-only broken) | the CLI fixture (the F-8 analogue): a target whose config names Y, compiled with `--measures X`, must stamp Y and print the note |
| S947 | `gen-tables` embeds the previous default | §8.3 agreement check |
| S948 | a `derived` row's value edited, inputs unchanged | §8.2(a) |
| S949 | the envelope takes `min` where `max` is declared | §8.2(d) |
| S950 | the staleness comparison always reports fresh | a kit form-text change fixture must flag its rows; REACH counts stale rows seen |
| S951 | the install tool's noise gate never fires | a recorded 20% A/A-spread fixture must exit 3 and write no set |
| S952 | the census population shrinks silently (a class skipped) | the awk floor and the MOVERS drift |

S944 and S946 are answer-NEUTRAL (every form answers alike) except through the structural
arm; the plan declares them so, as R17-b′ declared SB12.

## 9. Staged build, questions, lenses

### 9.1 Stages (each with its D77 trigger)

| stage | content | trigger |
|---|---|---|
| M0 | the shared reader/validator (`src/core/measures.c`), `measure_store/` with ONE set (`zen4-grid1` as scratch, replaced by grid2 as default when run), `generate.py`, the embed, the `<PREFIX>_MEASURES` stamp (the abi event), `--list-measurements` sets and one-set views, `mf_measures` and the lookup report, spec `docs/spec/measures.md` | R17-b′'s build (D166); rides its abi event |
| M1 | `--measures=`, the config line, `-I` resolution, precedence tests, the per-target view, `measure_census.sh`, `test-measures` + `-answers`, S943-S948 | the first second set (grid2, or a rollback need) |
| M2 | the envelope script, class defaults, `composite` labelling, S949 | a second box's official set (F5 Zen 1) |
| M3 | `pcrec-measure`, the quick profile, the noise gate, `local` tier, `DEFAULT_MEASURES`, S950-S952 | a stated install-time need (D166 item 3 names it; no scheduler for it until a user asks) |
| M4 | pcrec's own quantities (`pcrec.c_call`, `pcrec.c_byte`) and their `cand_rows[]` readers | the regime table's pcrec-side build |

### 9.2 The three standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.** Every number a set holds is a regime-bound
   measurement. The set stores the regime it was measured in: the header (box, governor,
   compiler, `code_commit`, run) and the row's `subject` condition (repeated vs streamed
   flips the walk 150-250 vs 0.4-22 branch misses/KiB, gridread F2). A different regime can
   flip a row, which is why a set is one run and never mixed, and why the envelope carries
   `env` directions rather than averages. The tool measures in ONE regime per profile and
   names it in the set.
2. **Independent control: RELEVANT.** Answers: checked against the `.rxt` oracle, not
   against another artifact (§8.1). Derived rows: recomputed by a python implementation of
   the SPEC's formulas, not by the C producer (§8.2). Population counts (derived/fitted/
   measured/null, census size, sites per form) are counted by awk over the TSVs (K35).
   Each sabotage row names its detector and its REACH counter. The unavoidable shared
   source: the measured numbers' own truth, which is controlled by gridread's A/A floors
   and the out-of-sample replay (regime_eval), not by this design.
3. **What moves when regenerated: RELEVANT.** (a) A new set or a changed DEFAULT moves the
   selections that read a moved quantity (the census), the stamp on every consulting
   artifact, the identity gate's (B) pin and the EMITTED_BYTES readers: NOT an abi event
   (Q-MS-2). (b) Introducing the stamp IS an abi event (§3.6). (c) A kit form-text change
   stales the default set's rows and fails `test-measures` until the set is refreshed.
   (d) Spec: new `docs/spec/measures.md`; hunks in `cli.md` (§1.1.2 flag, §1.1.4 config,
   §2 listing, §2.11 `--emit-facts`), `match_api.md` §6.3 (stamp, abi line),
   `rxt_format.md` (the `measures` config line), `registry.md` if `--list-axes` lists
   `--analysis` today (grep at build), `table_contract.md`'s enrolment. Docs/guide points,
   never restates.

### 9.3 Sibling-family lens

| sibling | what it teaches | what a set does differently |
|---|---|---|
| analysis object / findings (D162) | name grammar, `-I` search, fill-only precedence (D93), `config` line, digest in an every-artifact stamp, embedded-twice store, `--list-analysis` shape, `.rxt` DATA scope | no chain, no `include`, no `serves`: one set per compile; rows keyed numerics, not counts; integer values; a different suffix |
| limits (`limits.def`, `--list-limits`) | one declared table, listing and binary cannot disagree | limits are D149 constants chosen by people; set rows are MEASURED, provenanced and versioned; limits have no run, no box |
| axes (`--list-axes`) | a registry whose rows are the options | a set is not an option; `--measures` is one axis whose VALUE is a set |
| option sets ([OPT-SETS], `--set=`) | NAME collision: "set" there is a bundle of options | a measurement set is always spoken in full ("measurement set"); `--measures` cannot collide with `--set=` |
| `oracle_store/` / `third_party/` | the committed-data directory shape, `PROVENANCE.md`, `generate.py`, `gen-tables` | derived by running our own code on a box, immutable, with a census |
| `D149` constants | a number that is a CHOICE vs a number that is a MEASUREMENT | this design is D149's measured branch; a number that is neither stays suspect |
| `[ART-MGR]` | the cache key (§3.7) | |

The design lenses (docs/design/CLAUDE.md memory `pcrec-design-evaluation-lenses`): general
vs specific: the format is general (any owner's quantities); the first set is specific
(Zen 4). Core vs derived: costs are core, crossovers derived. Fits the architecture vs a
refactor: it fits (a sibling of the analysis object; it adds one stamp and one seam).
First-match tables (`pcrec-decisions-as-first-match-tables`): the reader rows ARE the
declared tables; this design adds data they read.

### 9.4 Unlocks, with triggers

- Cache key on the READ subset: [ART-MGR] build and measured recompile churn (§3.7).
- `rx_info.measures` mirror: the [IFACE-PUSH] batch, or a consumer that cannot parse the
  macro.
- `--list-measurements --diff A B` (a set-to-set diff by key): the first default change,
  to read a census with the cause beside it (S-census attribution already needs the
  per-key difference).
- The bench stamps the set in its results: the bench shim's first sub-bench (it reads the
  macro).
- Run-time set choice: NOT an unlock; D166 ruled compile time.
- pcrec's own rows (C_call, c_byte) as a first-match engine selection input: the regime
  table's build.
- A second-box envelope that holds COSTS (min/max of per-byte costs is unsound for a pay
  rule): only if the pay rule's unpaid pick under the envelope measurably loses.
- Rows with a per-quantity tolerance: when the first `null`/noisy row blocks a reader.

### 9.5 Questions for Frank (each with a recommendation)

- **Q-MS-1. What does a bare compile read?** The literal D166 ("latest set") vs D161 add.
  12 (generic envelope per ISA level, n=1 labelled). Recommend the second (§3.4). It decides
  what every un-flagged compile of the corpus emits and so what the first census moves.
- **Q-MS-2. A default-set change is not an abi event.** The stamp format is; a new
  default is a census + identity re-pin (the `<PREFIX>_FINDINGS` precedent). Recommend yes.
  If no, every re-measure costs a bump and the readers sweep.
- **Q-MS-3. Tier `local` for install-time sets**, never default, never an envelope member;
  `official` only from a bench run on targeted hardware (D144 add. 4). Recommend yes.
- **Q-MS-4. Store directory:** `measure_store/` (oracle_store's sibling) vs `measures/`
  (R17-b′'s word). Recommend `measure_store/`; trivial.
- **Q-MS-5. The noise gate:** 2 × grid1's p90 (6.2%) as an unmeasured initial default,
  re-derived from committed sets after the second box. Recommend yes; it is labelled.
- **Q-MS-6. A stale row in a non-default set is READ and flagged, not skipped.** A stale
  DEFAULT fails the test. Recommend yes (§2.4).
- **Q-MS-7. Embed every committed rev** (about 15 KB each) vs the default only.
  Recommend every rev (§2.3): rollback must work from a release build.
- **Q-MS-8. Stamp digest width:** 16 hex (FINDINGS' width) vs R17-b′'s 8. Recommend 16.

## 10. Findings

- **F1.** R17-b′ §3.5 proposes `measures/<name>/`; `oracle_store/`'s shape fits better
  (the data is derived by running our code, not vendored) and I recommend
  `measure_store/<id>/<rev>/` (Q-MS-4).
- **F2.** The kit's lookup report (§4.2) and `mf_form_hash` are two return facts the framework
  needs and R17-b′'s seam does not carry. They are requests to file, not part of
  R17-b′'s landing bar as written.
- **F3.** D166 says "compiled with the latest set"; D161 add. 12 says an unmeasured class
  reads the generic envelope. They agree only at one box and differ afterward; the design
  makes the difference a per-class pointer (Q-MS-1).
- **F4.** "Derived crossovers recompute from their rows" holds only for rows whose inputs
  are in the set. The g* family is interpolated over grid cells that are not (`fitted`);
  the check counts them and requires a transcript hash instead of pretending to recompute.
- **F5.** Staleness of a row cannot be a file field in an immutable store; it is computed
  against the linked kit (§2.4). That puts the kit's form hash on the framework's critical
  path for `test-measures`.
- **F6.** The stamp must be defined on LOOKUPS, not on found rows: an absent row skips a
  dispatch, so the artifact depends on the set even when nothing was read (§3.5).
