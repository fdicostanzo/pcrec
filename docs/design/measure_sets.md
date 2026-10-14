# Measurement sets — the format, the store, loading, the kit channel, the tool (rev 2)

Status: DESIGN ONLY, revision 2 (lane msetrev, 2026-10-14, from main `58338a09f`, abi 78).
Revision 1 was lane msetdes (same day). Nothing is built; nothing under `src/`, `cli/`,
`lib/` or `tests/` changes. Plan row [MEASURE-SET]; ruled by D166 and its addendum 1/1.1
(read D161 addenda 11-13, D162 and its addenda, D149 and D157 with it). It is part of the
framework Frank wants before further optimization (plan row [REGIME]). Its first customer
is the kit's R17-b′ (`memfn/r17b_prime.md` §3, whose measurement table is the needs list);
the interim shape is the kit's TSV from `memfn/regime_eval.md` Q-REVAL-10. The method a set
is measured by is `docs/dev/lanes/grid1_report.md` + `gridread_report.md`.

**Revision 2 applies the D6 panel r1 (`../dev/reviews/2026-10-14-r1-measure-sets.md`: 4
BLOCKER, 22 MAJOR, 12 MINOR, every finding ACCEPTED, the dispositions binding).** Read §R2
first. Changed text carries `[r1 <id>]` in place.

## R2. What revision 2 changed, by finding

| finding | section | how |
|---|---|---|
| msc1-1 (BLOCKER) | §2.1, §8.4 | `MOVERS.tsv` is the census AT its landing commit (`code_commit` in its own header). The re-run comparison runs only in the commit that adds the set or moves a `DEFAULTS` pointer, never against a later HEAD |
| msc1-2 (BLOCKER) | §2.3, §9.4 | The pre-parse is written by a C generator (`scripts/ksgen.c`, on `scripts/findgen.c`'s precedent), which links a stage-0 build of the one C reader. Python is only the checker (§8.2) and never writes an embedded byte |
| msc2-2 + msc1-4 (BLOCKER) | §3.4, §6.1, §10.1, §10.5 | M0/M1 compile with the LATEST set (D166 literal). The envelope default arrives at M2. The n=1 selection difference is stated (every cost row drops, so every pay rule takes `unpaid`) and censused at M2. A composite carries its members' unit rows as provenance (`#section members`). Q-MS-1 is re-put |
| msc1-5 (treated as blocking) | §8.1 | A run-time REACH floor per dispatch arm (a harness-only counter lever). Generated boundary subjects (L\*−1, L\*, L\*+1, W±1, 2W±1) per synthetic set. Synthetic sets carry the dispatch rows, so the dispatch is emitted and reached |
| msc2-1 | §1.2 | The wire shape is `table_contract.md` §4's real `#section NAME` syntax, chosen over oracle_store's `# k=v` line, with the reason |
| msc2-3 | §3.5, §3.6 | The stamp is the EMPTY STRING when nothing was asked (the `_FINDINGS` meaning). The digest is the loaded set's `values_digest`, kept over the whole set and not the consumed subset, with the reason (§3.5). The `rx_info.measures` mirror is ADDED in M0's abi bump |
| msc2-4 / msc2-5 | §1.3 | One canonical key string: an owner, a quantity, then dimension tokens in the order the quantity's METHOD CARD declares. The format defines no placeholder. An optional free `tags` column is display only. The seven fixed vocabulary columns are gone (D157). The checker needs only grammar, uniqueness and arity. R17-b′'s keys are reconciled in §1.3.3 |
| msc2-7 | §4.1, §4.2 | Stamp-on-load: the stamp's content is fixed when the set loads. The kit returns one boolean, `consulted`. pcrec hands over only `kit.` rows, with no `status` (a NULL row is simply not handed over) |
| msc2-9 SIBLING FAMILY | §9 (new) | ONE `src/core/ksrc.c` knowledge-source module (a section-TSV reader/validator, a name resolver, a store, a stamp/digest builder), parameterised by KIND: the analysis object, measurement sets, [TABLE-JUDGE]'s picks file. The analysis loader migrates onto it implement-then-replace at zero movers (§9.5). `--list-measurements` consumes [LIST-TABLES]' census (§5.4) |
| msc2-10 | §4.4 (new), §10.1 | The kit return facts become five requests main files (R-MS1..R-MS5), each with its landing bar. M0's trigger is R17-b′ landing WITH R-MS1, R-MS2, R-MS3 and R-MS5 |
| msc1-3 | §3.6, §10.2 | D162 ruling 1 KEPT: a default-set change that moves an emitted byte IS an abi event (pre-1.0 ritual), carried with its mover census. Because the stamp names the set, every default change moves every consulting artifact, so every default change is one. Q-MS-2 is withdrawn |
| msc1-6 | §8.1 | Only "stamp empty ⇒ bytes identical across every set" is kept. The converse is dropped |
| msc1-7 | §2.4 | Staleness is TRANSITIVE: a row's own dependencies (form, compared form), its inputs, the unit row, a pcrec-side hash, and a compiler-mismatch flag |
| msc1-8 / msc2-6 | §2.4, §10.5 | The hashed canonical instance is defined: the form BODY with scaffolding normalized out, owned by the kit (R-MS3). The stale-default POLICY goes to Frank, with the manager's leaning (carried-stale, a listing flag and manager review, never a landing gate). Until he rules, nothing fails on staleness |
| msc1-9 | §8.1, §8.4 | The census records refusals and every `*_WHY`/ladder token. The answer arm always includes the near-cap artifacts plus a synthetic near-cap fixture |
| msc1-10 + msc3-3 | §6.2, §6.3, §8.2 | The envelope's safe direction belongs to the READER ROW. It is derived from the readers' declared comparison and cross-checked against the card's `env`. `envelope.py` and `recompute.py` share no helper. A cross-member loss test is added. n=1 is distinct in the stamp (the id carries `n1`) |
| msc1-11 | §8.5 | S947: the default pointer is read from `DEFAULTS` independently and compared. S952: a compiled-artifact manifest is counted, not the population file |
| msc3-1 | §1.4 | The unit row's regime is PINNED (streamed, fresh buffer, long, member-free), with its own A/A and a bimodal flag. Cross-set comparison happens only within one `method@ver` |
| msc3-2 | §7.2 (new) | Per-quantity METHOD CARDS form a closed table (subject, lengths, launches, rounds, A/A rule, gate, `env`, `dims`, `deps`). The checker refuses a row that is off its card |
| msc3-4 | §7.3 | A third outcome, PARTIAL (a set of the passing groups, with a printed summary). Gating is per group. Noise is the A/A floor and the fit spread in quadrature. grid1's numbers are quoted correctly. No claim that a local set beats the envelope without a replay test |
| msc1-12 | §8.3 | `make gen-tables && git diff --exit-code` (the drift test) is named as THE gate for embedded = committed |
| msc1-13 | §5.4, §8.6 | Reader coverage is checked against each class's DEFAULT set. Lookup keys ⊆ the declared readers' keys |
| msc1-14 | §1.7, §1.6, §3.2, §2.1 | The canonical order is a bytewise sort (`LC_ALL=C`). The rounding rule is literal (integer, half away from zero). A `-I` file's header `id` must equal NAME. `PROVENANCE.md`'s sha-256 is KEPT, with a checker |
| msc2-8 | §3.2, §7.5, §1.2 | Name-vs-path order is stated (a `/` means FILE, no existence probing). `DEFAULT_MEASURES` generates into `build/` and leaves the tree clean. `counters` and `members` are in the header example |
| msc3-5 | §1.6 | A derived row with a NULL input is NULL |
| msc3-6 | §1.6, §1.7, §2.1 | The NULL rule applies to a crossover's denominator. The rounding mode is named. The file sha covers `noise_e6` (the values digest does not) |
| msc3-7 | §1.5, §8.2 | The raw cells a fit reads are kept (`#section cells`), so `fitted` rows recompute |
| msc3-8 | §7.4 | The NULL rule is restated in full, including the sign-disagreement clause |
| unlocks | §10.4 | Filed with triggers, not built |

Two questions for Frank remain (§10.5): Q-MS-1 as re-put, and the stale-default policy.
Revision 1's Q-MS-2 is withdrawn (D162 ruling 1 is kept). Q-MS-3..8 are settled by the
manager (§10.5 lists how).

## 0. Answers first

Ruled by D166 and NOT re-opened here:

- **Sets.** One box, one run, one method version, never mixed. Versioned and committed.
- **The default.** The binary embeds the latest set as the default. An older set is
  selectable by name.
- **Moves.** Selections move automatically, with a mover census in the same commit.
- **Values are RELATIVE.** They are in units of the scalar walk's per-byte cost, plus
  derived crossovers. Absolute ns is provenance only.
- **Loading.** At COMPILE time, by `--measures=FILE|NAME` and a config line. A set is the
  machine-side twin of the analysis object, and key A is "which set".
- **The generic class** is a DERIVED envelope set, labelled composite.
- **Answers never depend on the set.**
- **An install-time tool** can produce a set.

D162 ruling 1 is kept: data regeneration that moves an emitted byte is an abi event [r1 msc1-3].

Recommendations (each priced below):

1. **Format (§1): a SIBLING of the analysis format, not the same file.**
   - The file is a `table_contract.md` §4 SECTION TSV [r1 msc2-1], with sections `header`,
     `cards`, `rows`, `cells` (and `members` for an envelope).
   - Values are integers only (`value_e6`, a literal rounding rule).
   - One row per measured quantity, keyed by ONE canonical key string: owner, quantity,
     then dimension tokens in the order the quantity's method card declares, with no
     placeholders and an optional free `tags` column [r1 msc2-4/msc2-5].
   - Each row has a status (`measured`/`fitted`/`derived`/`null`), its dependency hashes
     (`deps`), and a values digest in the header.
   - Sets never `include` one another.
2. **Store (§2): `measure_store/<id>/<rev>/`**, oracle_store's shape.
   - `make gen-measures` (called from `gen-tables`) embeds every non-synthetic committed rev
     as text and as a C pre-parse, written by `scripts/ksgen.c` with the one C reader
     [r1 msc1-2].
   - A rev is immutable. `MOVERS.tsv` is the census at its landing commit [r1 msc1-1].
   - Staleness is COMPUTED and transitive. What a stale default does is Frank's call
     (§10.5) [r1 msc1-7/msc1-8].
3. **Loading (§3): `--measures=NAME|NAME@REV|FILE`** and a config line `measures`, with
   exactly `--analysis`'s precedence.
   - A bare compile reads the LATEST set at M0/M1. The envelope becomes the default at M2
     (Q-MS-1, re-put) [r1 msc2-2+msc1-4].
   - The stamp is `<PREFIX>_MEASURES`, mirrored in `rx_info.measures`, both added in M0's
     ONE abi event [r1 msc2-3]. It is `""` when nothing was asked, else `id@rev:digest16`.
   - Every later default-set change is an abi event with its census (D162 r1) [r1 msc1-3].
4. **Kit channel (§4).**
   - `mf_measures` on `mf_art_begin` carries `kit.` rows only.
   - Stamp-on-load. The kit returns one boolean, `consulted` [r1 msc2-7].
   - The kit-facing facts are FIVE requests main files, each with a landing bar
     (R-MS1..R-MS5, §4.4) [r1 msc2-10].
5. **`--list-measurements` (§5).** Three views, in `--list-analysis`'s shape. Reader rows
   come from [LIST-TABLES]' census of declared tables, not from a scan of its own
   [r1 msc2-9].
6. **Envelope (§6).** A script derives a composite from the latest official set of each box
   in an ISA level.
   - The SAFE DIRECTION per key comes from the reader rows' declared comparisons,
     cross-checked against the card's `env` [r1 msc1-10/msc3-3].
   - A key the readers disagree on, or that is absent from any member, is excluded.
   - n=1 is legal and visibly distinct in the id and the stamp.
   - Members' unit rows travel as provenance [r1 msc2-2].
7. **Install tool (§7): one driver, `pcrec-measure`, in `measure/`.**
   - It is C and zero-dependency, and runs owner-supplied METHOD CARDS and probes
     [r1 msc3-2].
   - Its gates are per group. There are three outcomes: FULL, PARTIAL (passing groups only,
     summary printed), REFUSED [r1 msc3-4].
   - Noise is A/A and fit spread in quadrature. The NULL rule is stated in full
     [r1 msc3-8].
   - It writes tier `local`. Perf counters are optional (D166 add. 1/1.1).
8. **Independence (§8).**
   - Answers are checked against the `.rxt` oracle under every committed set, three
     synthetic extremes and a dispatch-carrying synthetic set.
   - Each dispatch arm has a run-time REACH floor, with generated boundary subjects
     [r1 msc1-5].
   - Derived and fitted rows are recomputed by an independent python from the closed
     registry and the raw cells [r1 msc3-7].
   - The census is at landing [r1 msc1-1]. Sabotage S943-S952, plus PROPOSED S953-S960.
9. **The sibling family (§9).** ONE knowledge-source module in `src/core/` serves the
   analysis object, measurement sets and [TABLE-JUDGE]'s picks file. The analysis loader
   migrates onto it at zero movers [r1 msc2-9].
10. **Plan (§10).**
    - M0 rides R17-b′, with the requests.
    - M1: `--measures=`, the census, the analysis migration.
    - M2: the envelope and its default flip.
    - M3: the tool. M4: pcrec's own rows.
    - TWO questions for Frank.

## 1. The set FORMAT

### 1.1 What a set holds

A set holds everything R17-b′ §3.2 lists: 18 families, about 45 values. It also holds
pcrec's own engine quantities (armread's `C_call`, `c_byte`) once their reader rows exist.
Four properties force the shape:

- **Owners.** pcrec parses and validates the container. It never interprets a kit-owned key
  (D157: the kit's vocabulary, the kit's method). So the format fixes the KEY GRAMMAR, and
  each quantity's dimension order is declared by its owner's method card [r1 msc2-5].
- **Integers only.** A selection reads integers (`value_e6`), as `r17b_prime.md` §4.3
  proposes. There is no float in a selection, so no platform-dependent threshold.
- **Absence is data.** A quantity can be unmeasured (no row), measured but null (below the
  NULL rule, §7.4), or present. The listing tells the three apart. A selection reads all
  three identically: it skips.
- **Provenance travels with the value.** A reader of a number in a listing can name the
  run, the method card and its version, the box, and the code the value was measured on.

### 1.2 The file and its wire shape [r1 msc2-1]

A set is ONE file, `set.tsv`, in `table_contract.md`'s section shape. That is §2: TAB
separation, `#` comment lines, and the last `#` line before data as the header. §4: one
`#section NAME` line per section, columns resolved by header name, append-only per
section. Revision 1 cited a `[header]`/`[rows]` syntax that does not exist; the real one is
used below.

```
# pcrec measurement set (spec: docs/spec/measures.md)
#section header
#key	value
format	1
id	zen4-grid2
rev	1
class	x86_64-avx2/zen4
isa	x86-64-v3 avx2 sse4.2 popcnt bmi2
tier	scratch
composite	0
members
unit_key	kit.beta.walk.PF.r1e0c0
method	kit-grid@2
run	slot grid2, 2026-10-xx
box	AMD Ryzen 7 7700X; governor performance; kernel ...
compiler	gcc 15.2.0 -O2
code_commit	<measured-code commit>
counters	skipped:perf_event_paranoid=4
partial	0
rows	47
values_digest	<16 hex>
#section cards
#owner	quantity	ver	dims	unit	subject	lengths	launches	rounds	aa_rule	gate_e6	env	deps
...
#section rows
#key	unit	value_e6	abs_ns_e6	noise_e6	n	status	derivation	inputs	deps	tags	source
...
#section cells
#cell	group	arm	length	launch	round	ns_e6
...
```

**Why `#section` and not oracle_store's `# k=v` line.** Both are house shapes. The section
shape wins on four counts:

- **Spaces in values.** The header carries values with spaces (`box`, `run`, `compiler`),
  which a space-separated `k=v` line cannot hold without a quoting rule nobody has written.
- **Four tables in one file.** A set has four tables (header, cards, rows, cells). A `k=v`
  line plus one header row is a single-table shape.
- **The listing shares the format.** `--list-measurements NAME` (§5.2) EMITS sections
  under `table_contract.md`. One reader then serves both the file and its listing, and
  `table_check_truthfulness` (`table_contract.md` §5¶1) checks both.
- **The sibling family reads sections.** `[TABLE-JUDGE]`'s picks file has more than one
  table too, so §9's shared reader is a section reader in any case.

oracle_store's self-checking `rows=` count is kept, as the header's `rows` (§1.6). An empty
field means "none" (`table_contract.md` §2¶5): the non-envelope `members` above is empty.

**Header keys** (one row each):

- `format`, `id`, `rev`.
- `class`: ISA level `/` tuning class. This is the A of D161 add. 11, spelled by whatever
  axis [R4g `--isa`] settles.
- `isa`: the box's availability at measurement time. It is provenance and an applicability
  check (§3.4), NOT a selection input.
- `tier`: `scratch` | `official` | `local` | `synthetic` (D144 add. 4).
- `composite`: 1 for an envelope.
- `members`: an envelope's members, as `id@rev:digest16` `;`-joined. It is empty for a
  measured set.
- `unit_key`.
- `method`: the card table's `owner-name@ver` (§7.2).
- `run`, `box`, `compiler`, `code_commit`.
- `counters`: `none` | `skipped:<reason>` | `branch-misses` (§7.4a).
- `partial`: 1 when §7.3's PARTIAL outcome wrote the set [r1 msc3-4].
- `rows`, `values_digest`.

`counters` and `members` are now in the example [r1 msc2-8]. One run means the header's
provenance is the set's, and every row inherits it.

**Sections:**

| section | contents |
|---|---|
| `header` | the key/value rows above |
| `cards` | a COPY of the method card rows the set was measured under (§7.2), so an immutable set describes itself after the owner's card table moves on |
| `rows` | the quantities (§1.3) |
| `cells` | the raw per-launch cells every `fitted` row and every `measured` row of a NULL-rule decision reads (§1.5) [r1 msc3-7]. Empty for an envelope |
| `members` | envelope only: each member's `id@rev:digest16`, its unit row's key and `abs_ns_e6`, and its `box` (§6.4) [r1 msc2-2] |

### 1.3 The key [r1 msc2-4, msc2-5]

#### 1.3.1 One canonical string

```
key   := owner "." quantity { "." token }
owner := "kit" | "pcrec"                   (closed list in docs/spec/measures.md)
quantity := [a-z][a-z0-9_]*
token := [A-Za-z0-9_+-]+  , and not the single character "-"
```

- **Dimension order.** The tokens after the quantity are the quantity's DIMENSION VALUES,
  in the order its method card's `dims` column declares (`dims` = `form;kind;shape`, say).
  The arity is the number of declared dimensions.
- **No placeholders.** The format defines none. A quantity not split by a dimension leaves
  that dimension out of its `dims`; it does not spell a `-`. Revision 1's seven fixed
  columns (`form`, `vs`, `kind`, `shape`, `layer`, `subject` plus `quantity`) are GONE. Each
  was a piece of the kit's vocabulary built into pcrec's format, which presumes the kit's
  method (D157).
- **Tags.** The optional `tags` column holds `name=value` items, `;`-joined (`layer=simd;
  subject=streamed`). It is free and display-only. The listing can filter on it, and no
  check and no selection reads it. A distinction that keys a VALUE belongs in the key, not
  in a tag.
- **What the checker needs.** Grammar, uniqueness of `key` within a set, a card for
  `owner.quantity`, and arity equal to that card's `dims` count. It needs nothing of any
  owner's vocabulary.

#### 1.3.2 What a fixed column bought, and what replaces it

Revision 1 kept columns so that the listing could sort, staleness could group by form, and
applicability could group by layer.

- **Sorting.** The listing sorts on the key string (bytewise, §1.7) and on the tags.
- **Staleness.** It reads `deps` (§2.4), which names the forms a row depends on as data.
  It does not need a column that happens to hold a form name.
- **Applicability.** It reads the card's `deps` and the set's `isa` (§3.4).

#### 1.3.3 Reconciled with R17-b′'s keys (`r17b_prime.md` §4.3)

- **The key strings are unchanged.** R17-b′'s key `kit.beta.V1.ANY.r2e0c0` is a
  conforming key: owner `kit`, quantity `beta`, and tokens `V1`, `ANY`, `r2e0c0` under a
  card whose `dims` is `form;kind;shape`.
- **`ANY` is the kit's token.** Whether it reads as "measured unsplit by kind" is the kit's
  meaning (D157). The format sees a token. If the kit prefers to drop the dimension for an
  unsplit quantity, that is the kit's card edit (D161 add. 13: free until lockdown). R17-b′
  §4.3's key strings therefore need no change.
- **`mf_measure` changes in one way.** It carries no `status`, because a NULL row is not
  handed over (§4.1).

### 1.4 The relative unit, and its pinned regime [r1 msc3-1]

The unit row is `unit_key`. It is a row with `unit ratio`, `value_e6 1000000` by
construction, and its absolute value in `abs_ns_e6`. R17-b′ §3.1's choice stands as the
first set's unit: u = β_walk(PF, 1 term), 0.1892 ns/B on grid1.

- **What the format fixes.** Exactly one unit row is named in the header. It is a `ratio`
  of value 1.0. No other row's `value_e6` was computed against a different row.
- **The checker's recompute.** It re-derives every `ratio`/`walkbytes` row's `value_e6`
  from its `abs_ns_e6` and the unit row's `abs_ns_e6`, EXACTLY, under §1.7's integer rule.
  Revision 1 said "within rounding". This is not circular: the producer writes both
  columns from the raw cells, and the checker re-derives one from the other.

A relative value is only as good as the unit's own regime: the unit cost is a different
number in a different subject condition. So the unit row's regime is PINNED, by its card,
for every set under that method:

- **The subject.** STREAMED, from a FRESH buffer (no repeated-buffer predictor training,
  gridread F2), LONG (the slope over 64 KiB → 1 MiB, R17-b′ §3.1's F3 measurement), and
  member-free (no landings: a walk that never stops).
- **Its own A/A.** An A/A pair is measured on the unit group itself and recorded as the
  unit row's `noise_e6`. The unit row's gate is tighter than any other group's (half its
  card's group gate, a labelled unmeasured default, D149).
- **A bimodal flag.** gridread §1.1 measured the walk BIMODAL across launches on repeated
  64 KiB groups. The unit card's A/A rule tests bimodality over the launches: a gap between
  the two launch clusters larger than the group's A/A floor. A bimodal unit refuses the
  run (§7.3). The pinned regime (fresh, streamed) is chosen to avoid the condition, and the
  flag catches it if it appears anyway.
- **Cross-set comparison is only within one `method@ver`.** A different unit regime is a
  different method version, and its ratios are not comparable with the old ones. The
  listing's set-to-set views (and the unlock `--diff`, §10.4) refuse to compare across
  method versions. The envelope admits only members of one `method@ver` (§6.1).

### 1.5 Crossovers, and the cells that make fits recomputable [r1 msc3-7]

A crossover is a ROW in `bytes` (or `count`).

- **`status derived`** where its inputs are rows of the set: L\* = (F_b − F_a) /
  (β_a − β_b), the single-call crossover from M7/M8's fixed parts and M3-M5's per-byte
  costs.
- **`status fitted`** where it is an interpolation over raw cells: g\* interpolated in
  log2 g over the grid.

Revision 1 left the raw cells in the run's transcript, so a `fitted` row could not be
checked. Revision 2 commits the cells the fit reads in the set's `cells` section. A fitted
row names its fit as a REGISTRY derivation (`interp-log2`, §1.6) and its `inputs` as cell
ids. So a fitted row recomputes like a derived one; the only difference is what its inputs
are (cells, not rows).

The cells are few: the g\* ladder is tens of cells per form, not grid1's 6,725 launches.
Cells no row reads are not committed. Their transcript hash goes in `PROVENANCE.md`.

A selection reads the crossover and never recomputes it. The reason is
`memfn/r17b_prime.md` §2.6's: a literal in the emitted dispatch must equal a set value, so
that the structural check (§8.1) can compare them. Storing costs and crossovers both is
deliberate:

- **Not costs only.** With costs only, two readers would derive the crossover twice (the
  kit's finder and pcrec's `cand_rows[]`).
- **Not crossovers only.** The pay rule needs costs, and a listing must show the inputs a
  reader checks.

### 1.6 The derivation registry, NULL propagation, self-checking

`derivation` names a function from a CLOSED list in the spec (`docs/spec/measures.md`).
Each is given as a formula in text, and is implemented independently in the C producer and
in the python checker (§8.2):

| derivation | formula |
|---|---|
| `ratio` | a / b |
| `diff` | a − b |
| `cross-lin` | (F_b − F_a) / (β_a − β_b), in bytes |
| `step` | the block width: DERIVED from the form's width, not measured |
| `min`, `max` | of the inputs |
| `interp-log2` | linear in log2 of the abscissa between the two bracketing cells where the measured effect changes sign under the NULL rule [r1 msc3-7] |
| `env-max`, `env-min` | over the envelope's members (§6) |

A new derivation is a spec row plus both implementations. A row whose derivation is not in
the registry is refused at load.

**NULL propagates [r1 msc3-5, msc3-6]:**

- A `derived` or `fitted` row with any NULL input is NULL.
- A `cross-lin` row is NULL when its DENOMINATOR (β_a − β_b) is NULL under §7.4's rule: the
  difference is within the two rows' noise in quadrature, or its launch-paired signs
  disagree. Division by a cost difference that is noise is the one place a derivation
  could otherwise manufacture a confident number from nothing.
- `interp-log2` is NULL when no bracketing pair exists, which means no sign change survives
  the NULL rule.

**Self-checking:**

- `rows` equals the row count of the `rows` section (K35: the producer is not the counter).
- **`values_digest`** is FNV-1a-64, 16 lowercase hex. It is computed over `pcrec-meas-1\0`
  followed, for each row in canonical order (§1.7), by the key, `\0`, the unit byte, the
  status byte, and `value_e6` as int64 LE (an empty value is `INT64_MIN`).
- **What the digest excludes.** It leaves out every provenance column (`abs_ns_e6`,
  `noise_e6`, `n`, `source`, `deps`, `tags`) and the cards and cells sections. So the same
  values from any provenance give the same digest, the property of the `<PREFIX>_FINDINGS`
  digest (findings.md 5¶6). The FILE sha-256 in `PROVENANCE.md` and `index.tsv` covers
  everything else, `noise_e6` included [r1 msc3-6], and has a checker (§8.3) [r1 msc1-14].
- Keys are unique and on-card (§1.3). Every `derived`/`fitted` row's inputs are present.
  Every `unit`/`status` is in its domain. There is exactly one unit row.
- Unknown columns are tolerated (`table_contract.md` §3¶2), and so are unknown tags.

### 1.7 Order and rounding, literally [r1 msc1-14, msc3-6]

- **Canonical order** is a BYTEWISE sort of the key strings, the C locale's (`LC_ALL=C`;
  `strcmp` in C, `sorted(key.encode())` in python). Never a collation: R24 M-F1's
  `sort -u` merged strings under a UTF-8 locale.
- **Rounding.** Every `value_e6` is computed in INTEGER arithmetic from integer `*_e6`
  inputs, with round half AWAY FROM ZERO at the final division. In C this uses
  `__int128` intermediates; in python, integer `divmod`. For a `ratio`:
  `value_e6 = rhafz(abs_e6 × 10^6, unit_abs_e6)`, where
  `rhafz(n, d) = sign · ((|n| + |d|/2) / |d|)` with truncating division and `|d|/2`
  truncated. `cross-lin` and `interp-log2` are specified the same way in the spec, the
  latter with its log2 computed on an integer fixed-point of 2^-32, stated bit for bit.
  The C producer and the python checker must then agree EXACTLY, so a one-unit difference
  is a failure, not a tolerance.

### 1.8 Sibling or same file? (priced, unchanged in substance)

| | A: sibling section TSV (RECOMMENDED) | B: a `measures` block kind inside `.rxt`'s `analysis` | C: JSON / a C header | D: the kit's interim TSV, unchanged |
|---|---|---|---|---|
| reader | §9's section-TSV reader, shared with the picks file and with every listing's consumer | the `.rxt` reader | a new parser | exists, kit-side only |
| fit | rows are keyed, numeric, provenanced; no counts | an `analysis` block is COUNTS with named derivations; a measurement row is a kind with none of the block machinery | n/a | kit-only; pcrec's quantities need a second file |
| `include` | none (D166: never mixed) | the analysis chain's whole design is `include`, so a set must forbid it | n/a | none |
| risk | one more file type, absorbed by §9's module | `analysis` semantics leak into sets | a second data language | the Q-REVAL-10 interim; unowned columns |

Recommendation A. The NAME resolution B would have reused is shared anyway, through §9's
resolver.

- **The Q-REVAL-10 migration.** Its interim TSV converts by a script: its key columns join
  into the canonical key under a kit card, and the rest are renamed by header.

## 2. The STORE

### 2.1 Layout

```
measure_store/
  CLAUDE.md  README.md            # the index and the maintenance note (third_party's shape)
  DEFAULTS                        # one line per class:  <class> <TAB> <id>@<rev>   (the default pointer)
  index.tsv                       # one row per committed rev: id, rev, class, box, tier, composite,
                                  #   method, supersedes, values_digest, file_sha256, status
  envelope.py                     # §6 (writes a set; never embeds)
  zen4-grid2/
    1/
      set.tsv                     # the set, self-checking (§1.6)
      PROVENANCE.md               # what derives from it; sha-256 of set.tsv; the run, the method card
                                  #   version, the reader script + commit; the raw transcript's location + hash
      MOVERS.tsv                  # the census AT ITS LANDING COMMIT (§8.4); absent for a set that moves no default
```

This is `oracle_store/`'s shape (one directory per source, a self-checking TSV,
PROVENANCE, a generator) applied to data derived by RUNNING pcrec's kit and engines on a
box. It is not `third_party/` (nothing is vendored from outside). The analysis object's
`src/findings/*.rxt` is the sibling on the data side.

- **The `raw/` directory is gone.** Its job (the reader's input) moved into the set's
  `cells` section, where the checker can reach it (§1.5).
- **The directory is `measure_store/`**, not R17-b′'s `measures/`. That was Q-MS-4,
  settled by the manager as a one-token choice (§10.5).

**`MOVERS.tsv` [r1 msc1-1].**

- **Its header** names `old` (`id@rev:digest16` of the default it replaces, per class),
  `new`, `code_commit` (the HEAD the census ran on, that is the landing commit's parent
  tree plus the set) and the population manifest's sha.
- **When it is written.** It is written once, by `scripts/measure_census.sh`, in the commit
  that adds the set as a class's default or moves a `DEFAULTS` pointer to it. It is
  immutable from then on, like the set.
- **What it describes.** It states what moved AT that commit. A later code change that
  moves selections under the same default is that change's own movers (`emit_sweep`, the
  identity gate), not this file's.
- **A set that moves no default** (an older or alternative set, a scratch set) has no
  MOVERS file.

### 2.2 Naming, versions, rollback

- **`id`** follows `[a-z][a-z0-9_-]*` (the analysis name grammar, §9.3), by convention
  `<class-token>-<run>` (`zen4-grid2`). Envelope ids are `generic-<isa-level>-n<K>`
  (§6.4). Ids are global across the store, and a user set may not reuse a committed id
  (§3.3).
- **A committed rev is IMMUTABLE.**
  - A re-measure on the same box is a NEW id (`zen4-grid3`), because it is a new run.
  - A corrected RE-READING of the same cells is a new `rev` of the same id.
  - `NAME` resolves to the latest rev, and `NAME@REV` pins one. The stamp always carries
    both.
- **ROLLBACK** is `--measures=zen4-grid1@1`, or a config line naming it. Every
  non-synthetic rev is embedded (§2.3), so rollback works from an installed binary with no
  checkout.
- **Supersession** is recorded in `index.tsv` (`supersedes`).

### 2.3 The default, and `make gen-measures` [r1 msc1-2]

- **`DEFAULTS`** maps each class to one `id@rev`. At M0/M1 there is one row, for the
  `idk` class (a compile that declares no class), and it names the latest set (§3.4).
- **`make gen-measures`** is called from `gen-tables`, exactly as `gen-findings` is. It is
  `gen-findings`' shape:
  1. **The text.** `scripts/embed_text.sh` writes `src/core/measures_store.inc`: every
     non-synthetic rev's TEXT, from the one committed file.
  2. **The pre-parse.** `scripts/ksgen.c` writes `src/core/measures_table.inc`: the same
     text PRE-PARSED into static const arrays.
  3. **The pointers.** `ksgen` also writes the default pointers from `DEFAULTS`, as a
     table in the same `.inc`.
- **`ksgen` is C.** It links a STAGE-0 build of the knowledge-source module (§9: the one
  section-TSV reader and the measures-kind validator, built with an empty table, as
  `PCREC_FIND_STAGE0` does for findgen). It parses with the reader the library uses at
  run time, in its no-filesystem buffer mode.
- **No python writes an embedded byte.** Revision 1's `generate.py` wrote both the text and
  the pre-parse that the structural check then verified against its own python twin. That
  is a control sharing a source with its subject (learnings §3). The python parser is the
  CHECKER only (§8.2, §8.3).
- **Committed, not rebuilt.** Both `.inc` files are committed. A plain `make` does not
  regenerate them, and `make gen-tables && git diff --exit-code` covers the chain (§8.3).

Why keep the pre-parse for 47 rows: the library's no-filesystem path must be one code path
for every knowledge kind (§9.4), and findings already measured the parse-per-compile cost
as worth removing (findgen.c's header: ~47 µs, ~20% of a minimal compile, for `default.rxt`).

**Embedding every rev, not only the default.** 47 rows is about 6 KB of text per set and
15 KB with the pre-parse; the cells and cards add about 4 KB. Ten committed sets stay below
one `fold_tables.inc`. Rollback must work from a release build (Q-MS-7, settled §10.5).

### 2.4 Staleness: transitive, defined, and policy deferred [r1 msc1-7, msc1-8, msc2-6]

**What a row depends on.** A row's `deps` column holds `;`-joined items
`owner:dep-id=hash`, written by the producer from the card's `deps` declaration:

- `kit:form.V1=…` and `kit:form.walk=…`: the measured form AND the compared form (`vs`),
  each hashed by the kit (R-MS3).
- `pcrec:<id>=…`: a pcrec-side hash, for rows whose measured code includes pcrec's own
  emission (a pcrec quantity, or a kit quantity measured through a pcrec-emitted consumer).
  It is the hash of the pcrec emitter's output for the card's named probe pattern, with
  the stamp lines stripped (`emit_sweep`'s normalization).

**The canonical instance [r1 msc1-8/msc2-6].** A form hash is over the form's BODY with
SCAFFOLDING NORMALIZED OUT. It is the text the kit emits for a fixed canonical site (fixed
set, fixed span, fixed prefix), with the prefix, generated identifiers, comments and blank
lines normalized. So it moves when the instruction text the timing measured moves, and
not when a name, a comment or a neighbouring declaration moves. The kit owns that
definition and exposes it as `mf_form_hash(form_id)` (R-MS3). pcrec compares opaque
strings. Revision 1 left "the hashed text" undefined, so every kit comment change would
have staled every row.

**A row is STALE iff any of:**

1. any `deps` hash differs from the current one (the kit's `mf_form_hash`, pcrec's
   recomputed hash);
2. any input row of a `derived`/`fitted` row is stale (transitive through `inputs`);
3. the UNIT row is stale, for every `ratio`/`walkbytes` row. Every relative value is
   relative to it.

**A compiler mismatch** (the set header's `compiler` against the build's `$CC -dumpfullversion`
and the card's flags) is a SET-level listing flag, `compiler-mismatch`, not row staleness.
The emitted text is the same and the machine code may not be, so it is reported, never
computed into a verdict.

**Where it is computed.** Staleness is COMPUTED, by `make test-measures` and by
`--list-measurements` against the linked kit. It is never written into a committed file,
because sets are immutable.

**A stale row in a set selected for a compile is READ.** Skipping it would move a
selection with no measurement behind the move: a silent default, which
`pcrec-no-silent-defaults` forbids. It is flagged `stale 1` in every listing.

**A stale DEFAULT is a POLICY question for Frank (§10.5, Q-MS-STALE).** Revision 1 made a
stale default fail `make test-measures`, which puts every kit form-text change on the bench
box: no kit form edit could land without a slot run. The options:

- (a) **block**, revision 1's rule;
- (b) **carried-stale**: the default stays, its stale rows are read, the listing flags
  them with a count, and the manager reviews the count at each kit merge and schedules a
  re-measure when the stale rows feed a reader;
- (c) **a declared cost-neutral equivalence row**: the kit's change carries a row saying
  "form X's new body is cost-equivalent to the measured one", with its evidence, and the
  check accepts the stale row under it.

**The manager's leaning is (b), and never a landing gate.** (c) is a mechanism ahead of a
measured need (D77). Until Frank rules, nothing FAILS on staleness: `test-measures` prints
the per-class stale counts as an always-printed INFO bucket (`record()`'s shape).

## 3. LOADING

### 3.1 The surface

- **`--measures NAME|NAME@REV|FILE`** (or `--measures=...`) applies to a `--pattern`
  compile or to each target of a file operand. It is legal with a compile and with
  `--list-measurements`, and refused elsewhere (`--analysis`' list, cli.md 1.1.2).
- **The `.rxt` config line** `measures NAME|NAME@REV|FILE` is one per config, in the
  `analysis` line's place. Inside the `pcrec` config line it is refused when the file is
  read, as `--analysis` is.
- **The library** gets a `pcrec_options` field, appended in the same [IFACE-PUSH] batch
  the analysis field belongs to.

### 3.2 Resolution, in a stated order [r1 msc2-8, msc1-14]

Classification is by spelling alone, with NO existence probe, so the same argument means
the same thing in every directory:

1. A value containing `/` is a FILE (`./mine.measures.tsv` reads a file in the cwd).
2. Otherwise, a value matching the id grammar, optionally with `@REV`, is a NAME.
3. Anything else is refused, naming both rules.

**A NAME** is looked up through §9.3's resolver, in the stops the analysis uses minus S1
(a set is never defined inside a `.rxt`):

- S2, `DIR/NAME.measures.tsv` for each `-I DIR` in order, with the directory entry matched
  exactly (`rxt_find.c`'s `dir_has_exact`);
- S3, the store.

A file found at S2 must carry a header `id` equal to NAME, or it is refused [r1 msc1-14]:
the stamp names the id, so a file answering a name it does not carry would make the stamp
lie. An unknown name refuses the compile and names the stops searched (`stops_text`).

**A FILE** is read directly. Its header `id` is what the stamp carries.

### 3.3 Precedence (D93)

Identical to `--analysis`: fill-only.

- A target whose config names `measures` gets that set. `--measures` names the set for
  targets whose configs name none.
- A disagreement is reported in `tune`'s shape, and the file wins: "... CLI --measures X
  and this file's measures Y disagree; using the file's value (--measures is fill-only)".
- There is a single value per compile. Sets are never mixed, so there is no per-quantity
  precedence and no chain.
- **A user set may NOT take a committed id.** A `-I` or FILE set whose `id` is in the store
  with a different `values_digest` is refused ("id X is a committed set; rename"). The
  stamp names a set by `id@rev:digest`, so a shadow would make a stamp point at a set that
  does not carry those values.

### 3.4 What a bare compile reads [r1 msc2-2, msc1-4]

Priority: an explicit flag, then the config, then the BUILD'S default for the compile's
class.

**M0 and M1 ship D166's literal reading.** A bare compile reads the LATEST committed
non-synthetic set: `DEFAULTS` has one row, and it names the newest official set, or the
newest scratch set while no official one exists. With one measured box that applies
Zen 4's rows to every machine, and the listing says so ("default: zen4-grid2, measured on
one box").

**The envelope default (D161 add. 12) arrives at M2.** Revision 1 recommended it from M0.
The panel showed it cannot exist before M2, for three reasons:

- **No member.** An envelope's members are OFFICIAL sets (§6.1). Before a second box,
  there may not even be one official set.
- **No unit.** An envelope has no unit row of its own (§6.3), so the loader could not
  check its relative values against one.
- **Selections move at n=1 [r1 msc1-4].** An n=1 envelope is NOT "Zen 4's rows relabelled".
  Every row whose safe direction is `none` (every per-byte COST, the unit included) is
  excluded from an envelope. So under it, every pay rule (R17-b′ §2.5, which needs costs)
  fails its test and takes its `unpaid` pick, and every reader of a cost row skips. The
  n=1 envelope therefore MOVES selections relative to the latest-set default, wherever a
  pay rule or a cost reader fires.

At M2 the default for each class flips from "latest set" to "that ISA level's envelope"
(D161 add. 12, Q-MS-1).

- **The flip is a default-set change.** It carries a census in its commit (§8.4), and
  that census is exactly the cost-row population above.
- **It is an abi event** (§3.6), and its commit goes through the identity gate's re-pin.

**ISA applicability.** The set's `isa` header is checked against the compile's declared
target.

- A row whose card declares an ISA dependency the target lacks (`deps` on a `form` whose
  kit card names `avx2`) is inapplicable and skipped. It is listed as such in the
  per-target view.
- The target not being the measuring box is the POINT of key A, and is not an error.

### 3.5 The stamp [r1 msc2-3, msc2-7]

`<PREFIX>_MEASURES` appears in every artifact, beside `<PREFIX>_FINDINGS`, and follows the
`_FINDINGS` meanings (findings.md 5¶4):

- **The EMPTY STRING** when nothing was asked: no pcrec reader looked up a key, and the kit
  returned `consulted = false` (§4.2). Then the artifact bytes are the same under every set
  (§8.1 checks this direction only, msc1-6).
- **Otherwise `"<id>@<rev>:<digest16>"`**, the set the compile LOADED. Revision 1 used
  `"none"` for nothing asked, which inverted the `_FINDINGS` reading, where `none` means
  "asked, and nothing answered".
- **No `asked-and-nothing-answered` spelling.** A lookup that found nothing still makes the
  artifact depend on the set (an absent row skipped a dispatch), so it stamps the set.

**The digest is the loaded set's `values_digest` (stamp-on-load), not a digest of the
consumed rows.** The review asked for the consumed subset or a justification. This is the
justification:

- **The kit reports a boolean.** It returns whether it consulted the set, not which keys
  (§4.2). A per-key report would be the kit describing its own method's internals to
  pcrec, the presumption D157 forbids in the other direction too. So pcrec cannot know the
  consumed subset of kit rows.
- **The precision would buy nothing in bytes.** The stamp names `id@rev`, so two sets
  differing only in unread rows already give different stamps through the id.
  `_FINDINGS` can digest the consumed rates because its bundle name and its digest are the
  only identity it has. A set has an immutable id@rev, which a consumed-subset digest
  would not make any more exact.
- **The read rows are recoverable** by listing (§5.3) through the owners' decision
  listings, not from the artifact.

A consumed-subset digest is filed as an unlock with its trigger: the [ART-MGR] read-subset
cache key (§10.4).

**Other properties of the stamp:**

- **Width.** The 16-hex width matches the FINDINGS stamp (Q-MS-8, settled).
- **`rx_info.measures`** equals the macro byte for byte (§3.6), as `rx_info.findings` does
  (match_api.md 6¶14).
- **Disclosure.** Both the macro and `rx_info` are plain text, so a shipped binary
  discloses the set id. Name sets neutrally (findings.md 5¶8).

### 3.6 The abi events and their readers [r1 msc2-3, msc1-3]

**M0's event.** The stamp is emitted scaffolding in every artifact, and M0 also APPENDS
`rx_info.measures` (a `const char *`, after `findings`). That is ONE abi event: `abi` bumps
from 78 to the next number at landing (never a literal in a brief), and the identity gate
re-pins in the same change (D76/D94).

- **Why the mirror is added now.** Revision 1 deferred it to [IFACE-PUSH]. The panel's
  disposition: it costs nothing extra inside a bump that happens anyway, and `rx_info` is
  the canonical machine-readable record (D43, match_api.md 6¶14). A deferred mirror would
  be a second struct-layout event later.
- **Readers, by grep.** The readers are found BY GREP for the abi number when M0 lands. R17-b′ §5.2's list is the
  authority, and this is the cross-check floor:
  - `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c:54`);
  - match_api.md's K80 `#error` text, its "abi is N" sentence, §6.3's stamp table and
    §6's `rx_info` member table (a new row, a new ¶ beside 6¶14);
  - `docs/dev/history/abi_changelog.md`;
  - `run_codegen_tests.sh`'s `ABI_EXPECT`, and `run_recursion_identity.sh`'s FILEPIN /
    `ABI_SUBJ`;
  - the alpha scripts' normalizers;
  - the byte-count readers (`EMITTED_BYTES`, the `a{5,25000}` count, the size-term and
    K59/K53 rung witnesses, the cpset manifest, emit_sweep's `VARIANT_PINS`);
  - then the registry, codegen and rxtsource suites (D94 addendum) and
    `make test-codegen`.
- **One event, not two.** If R17-b′ builds first, the stamp and the mirror ride its bump.
  If M0 builds first, M0 is the bump.

**Every later default-set change [r1 msc1-3].** D162 ruling 1 is KEPT: data regeneration
that moves an emitted byte is an abi event. The stamp names the set, so a default change
moves the stamp of every consulting artifact. Every default-set change is therefore an abi
event, pre-1.0, under the ritual (`pcrec-abi-changes-pre-release`), in one commit:

- the abi bump;
- the readers by grep;
- the identity gate's (B) pin;
- the EMITTED_BYTES readers;
- the set's `MOVERS.tsv` (§8.4).

Revision 1's Q-MS-2 ("not an abi event", on findings.md 5¶9's precedent) is WITHDRAWN.
D162 ruled the data side, so no re-ruling is sought. A NEW non-default set is not an event,
because no default compile reads it.

### 3.7 The cache key

[ART-MGR]'s cache key becomes (pattern, options, analysis digest, the LOADED set's
`id@rev:values_digest`).

- **Why the whole set.** The cache is consulted before the compile that would discover the
  stamp is empty, so it keys on the loaded set regardless of whether anything reads it.
- **The cost.** Two sets differing only in rows nobody read produce byte-identical
  artifacts under different keys. The cache's content hash dedupes those on the store side.
- **The read subset as a key** is an unlock (§10.4).

## 4. The channel to the kit (facts only, D157)

### 4.1 What pcrec hands over [r1 msc2-7]

`mf_measures` is `r17b_prime.md` §4.3's struct, on `mf_art_begin` (per compile, not per
site: every site of a compile reads one set). It carries only:

- the `kit.` rows that are present and non-NULL: the key string, `value_e6`, `unit`, and
  `source` (R17-b′ §1.4's listing displays it; no selection reads it);
- the set's `id`, `rev`, `values_digest`, `class`, `tier`, `composite`.

What it leaves out:

- **No `pcrec.` rows.** The kit owns none of them.
- **No `status`.** A NULL row is simply not handed over, so the kit sees NULL and absent
  identically, as a skip. Telling them apart is pcrec's listing's job. A kit reader that
  needs the distinction asks by request.
- **No provenance columns.** `abs_ns_e6`, `noise_e6`, `n`, `deps`, `tags` and the cells are
  pcrec's listing's. A kit row that wants noise asks by REQUEST (`memfn/docs/requests.md`,
  single writer: main). No selection reads noise today.

pcrec computes no threshold. The kit ignores unknown keys (totality).

### 4.2 What the kit returns [r1 msc2-7]

ONE fact: after `mf_art_end`, `consulted` (a boolean). It is true iff any kit row of this
compile resolved a key against the set, found or absent.

- **The stamp.** pcrec ORs `consulted` with its own readers' lookups to decide whether the
  stamp is empty (§3.5). The stamp's CONTENT was fixed when the set was LOADED, which is
  what stamp-on-load means: no per-key traffic shapes the bytes.
- **Why a boolean.** Revision 1 asked for a per-key "looked up" report. That is the kit
  narrating its method to pcrec (D157's concern from the other side). It also puts a second
  per-key data path beside the kit's own decision listing, which already says which row
  fired and with which value. The per-target view (§5.3) and the census attribution (§8.4)
  read that listing instead.

`mf_form_hash(form_id)` (§2.4) is a second kit OUTPUT, used by staleness. The reader
declaration (R-MS4) is a third. Neither is part of a compile's data flow.

### 4.3 An unmeasured quantity

A row that resolves to absent, NULL or inapplicable is NOT EVALUABLE, exactly as a row
needing E is skipped when E is absent (r17b_prime.md §3.4).

- **No fallbacks.** There is no fallback to another set and no fallback to a nearby key.
  The decision falls through to the next row. The table's last row (R7, LINER) reads no
  set value, so the table is total with an empty set or with none.
- **"Never a presumed value" and "the generic class" fit together.** Generic is chosen
  BEFORE the compile, by set (§3.4), never inside it by quantity.
- **No borrowing.** A quantity unmeasured IN the chosen set falls to the table's own
  default. It does not borrow the generic set's value, because that would mix two runs,
  which D166 forbids.

### 4.4 The requests main files, with their landing bars [r1 msc2-10]

`memfn/docs/requests.md` is single-writer MAIN (`pcrec-requests-are-mine-to-file`).
Revision 1 named the kit facts but put them in no landing bar. They are now five requests,
and M0's trigger is R17-b′ landing WITH R-MS1, R-MS2, R-MS3 and R-MS5 (R-MS4's safe
directions are M2's):

| id | the request (facts, D157) | landing bar | needed by |
|---|---|---|---|
| R-MS1 | `mf_measures` on `mf_art_begin` as §4.1 states (kit rows only, no `status`; NULL = no set) | the kit's tests run every finder row with NULL, with a synthetic set lacking each key in turn (the row skips to its `unpaid` pick or the next row), and with the full set; a kit row never reads a `pcrec.` key | M0 |
| R-MS2 | `consulted` out of `mf_art_end` (§4.2) | a kit test with a compile whose sites read no set key → false; one row that reads an ABSENT key → true; one that reads a present key → true. pcrec's S945 (§8.5) reaches it | M0 |
| R-MS3 | `mf_form_hash(form_id)` over the canonical instance (§2.4), and the form ids the kit's cards name in `deps` | the hash is unchanged under a zero-mover kit refactor (renamed helper, comment edit) and changed under a one-instruction body edit, both as kit fixtures; every form id a kit card names resolves | M0 (staleness listing) |
| R-MS4 | the kit's READER DECLARATION: per finder-table row, the keys it reads and, per threshold key, its SAFE direction (`max`/`min`/`none`: the side of its conservative or `unpaid` pick), as data the kit's listing exposes in [LIST-TABLES]' census shape (§5.4); and, per artifact, which finder rows fired per site, as the `--emit-facts` section `memfn` (§4.5) | keys: every key a row reads is declared (the kit-side half of §8.6's ⊆ check); directions: each declared direction agrees with the row's comparison operator by a kit test | keys M0 (the listing's readers); directions M2 (the envelope) |
| R-MS5 | the kit's METHOD CARDS for its quantities (§7.2), as a section TSV in the kit tree, versioned `kit-grid@N` | each quantity R17-b′ §3.2 lists has a card; grid1's and grid2's rows are on-card (`make test-measures` §8.2) | M0 (the first committed set must be on a card) |

### 4.5 [r1 msc2-9] The kit's own listing, consumed not duplicated

R17-b′ §1.4 proposes a kit listing of the finder table with the active set's provenance
and the per-row value. pcrec's per-target view (§5.3) and the census attribution (§8.4)
READ that listing's per-artifact half (which rows fired, per site) rather than re-deriving
which kit rows fired. It reaches pcrec as a new `--emit-facts` section, `memfn`. That
section does not exist today (`facts_listing.md` 3¶3: `facts` and `decisions` only), so it
is an append to that section set and part of R-MS4.

## 5. `--list-measurements`

This is in `--list-analysis`'s family: `table_contract.md` sections, a [LIST-TABLES]
member. It is legal alone, with a NAME, or with a `.rxt` operand.

### 5.1 `--list-measurements` (no argument): the sets

Section `sets`, with the columns:

- `id`, `rev`, `class`, `box`, `tier`, `composite`, `members`, `method`, `supersedes`;
- `default_for` (the classes it is the default of);
- `rows`, `null_rows`;
- `stale_rows` (computed against the linked kit);
- `compiler_mismatch`;
- `values_digest`;
- `source` (store | `-I` file);
- `build_default_overridden` (§7.5).

### 5.2 `--list-measurements NAME|FILE`: one set

Sections:

- **`header`, `cards`, `rows`, `cells`, `members`:** the set's own sections, verbatim.
  This is the same wire shape as the file (§1.2), so one reader reads both.
- **`decoded`:** every row decoded. It shows the key, its tags, `unit`, the VALUE as a
  decimal, `status`, `abs_ns`, `noise`, `n`, `stale` with the dependency that staled it,
  `source`, and **`readers`** (the decision rows that read this key, as `owner:table:row`
  items, from §5.4's census). A row with no reader prints `readers` empty and is counted.
- **`readers`:** the converse. Every declared decision row that reads a set key, with its
  keys and, per key, `present` / `absent` / `null` / `stale` in THIS set. A reader row
  with an absent key is exactly the place R17-b′ §3.3's "no dispatch is emitted" reads
  out. This section is the audit that the skip is honest.

### 5.3 The per-artifact view: `--list-measurements FILE.rxt` (and `--emit-facts`)

For each target, it shows:

- which set the target resolves to, and by which stop (flag, config, build default);
- the stamp it would carry;
- `consulted` per owner: pcrec's readers, and the kit's boolean;
- the owners' fired rows, with the set keys those rows declare. The kit's rows come from
  the `--emit-facts` `memfn` section R-MS4 adds (§4.5), joined with §5.4's census; pcrec's
  come from its own trace.

It is produced by running the compile and discarding the emitted text, like
`--list-analysis FILE`'s per-target view. A `--pattern` compile gets the same rows as an
`--emit-facts` section (a spec hunk in cli.md §2.11 at build).

### 5.4 The reader index is [LIST-TABLES]' census [r1 msc2-9, msc1-13]

`--list-measurements` does not scan for readers. [LIST-TABLES] (Frank's "every selection
table listable") owns the census of declared decision tables, which holds rows as data
with a name, a predicate description and a deny flag. This design adds one column to that
census row shape: `reads`, the set keys the row's predicate reads, with each threshold
key's safe direction (R-MS4). The reader index is then a JOIN of that census with a set's
keys.

- **Ahead of [LIST-TABLES] STEP 0.** M0 contributes the census's first two entries, the
  kit's finder table (via R-MS4) and, at M4, pcrec's `cand_rows[]`. It contributes them in
  the census's shape, so [LIST-TABLES] absorbs them as rows, never as a parallel
  mechanism.
- **Coverage checks** (`make test-measures`), counted by an awk over the set TSVs and the
  census TSV, not by the listing (K35):
  - every committed non-synthetic row has at least one reader, or is marked
    provenance-only on its card;
  - every reader key resolves in EACH CLASS'S DEFAULT set, or is declared ABSENT-known
    (R17-b′'s M16-M18 today) [r1 msc1-13].

    Revision 1 asked for "at least one committed set", which a set nobody compiles under
    satisfies. The default is the set every bare compile reads, so coverage is checked
    against it.

## 6. The generic ENVELOPE set (M2)

### 6.1 Inputs

A DERIVED set (`composite 1`) for an ISA level, built from MEASURED sets.

- **Members.** The latest rev of the latest OFFICIAL set of each tuning class in the ISA
  level, all under ONE `method@ver` (§1.4).
  - A `scratch`, `local` or `synthetic` set is never a member.
  - The envelope's tier is the LOWEST of its members'.
  - With no official set there is no envelope, and the class's default stays the latest
    set (§3.4).
- **The script.** `measure_store/envelope.py CLASS MEMBER...` writes a new
  `measure_store/<envelope-id>/1/set.tsv`. Each row has `status derived`, `derivation
  env-max`/`env-min` and `inputs` naming the member keys.

### 6.2 The safe direction belongs to the reader row [r1 msc1-10, msc3-3]

Revision 1 put a per-row `env` on the set, declared by the method and never checked.
Conservative is a property of a DECISION, not of a column. "Pick the wider form when
n ≥ L\*" is safe at the max L\* over boxes; "pick the walk when g < g\*" is safe at the min
g\*. The same key read by two rows with opposite comparisons has no single safe direction.

- **The derived direction.** For each key, the envelope script collects every reader row's
  declared safe direction from §5.4's census (R-MS4).
  - If all agree, that is the key's direction.
  - If they disagree, or any says `none`, the key is EXCLUDED, and the exclusion is listed
    with the disagreeing rows.
- **The cross-check.** The card's `env` (the method's declaration) must equal the derived
  direction. If it does not, `make test-measures` fails, naming the key, the card and the
  rows. Two declarations from two owners' artifacts must agree, which neither can satisfy
  by construction.
- **No shared helper.** `envelope.py` (the producer) and `tests/measures/recompute.py`
  (§8.2) share no code. The checker re-derives the directions from the census TSV and the
  members' files with its own parser.

### 6.3 The rule, and what is lost

- **The rule.** A key enters the envelope iff it is PRESENT AND NON-NULL in every member,
  and its direction is not `none` or excluded. Its value is the members' `max` or `min`. A
  key missing from any member is excluded, not imputed.
- **Costs do not envelope.** The unit row, β and every per-byte cost are `none`: a pay rule
  divides by them. So the envelope holds crossovers and flags, and every pay rule falls to
  its `unpaid` pick under the envelope (the n=1 consequence of §3.4). That is the honest
  consequence, censused at M2.
- **The cross-member loss test [r1 msc3-3].** Per-column conservatism is not per-decision
  conservatism. A max L\* and a min g\* chosen independently can combine into a pick no
  member would make. So for each member m, the test replays the declared tables' picks
  under the envelope and under m's own set, on m's own arm timings (m's `cells`, through
  [TABLE-JUDGE]'s interface: picks plus arm timings). It reports the envelope's regret on
  m.
  - A regret above m's NULL rule (§7.4) on any cell FAILS the envelope, naming the key.
  - The fix is an exclusion row in the envelope script's declared exclusions (a
    first-match table, not a code branch), with the regret as its evidence.
  - Not built before M2. The interface it needs is [TABLE-JUDGE]'s, which builds then or
    is this test's first client.

### 6.4 Labelling and provenance [r1 msc2-2, msc3-3]

- **The id** is `generic-<isa-level>-n<K>`, so `generic-x86-64-v3-n1` and
  `generic-x86-64-v3-n2` are different ids, and n=1 is DISTINCT in the stamp class: the
  stamp carries the id. An n=1 envelope is honestly derived but transfers nothing. That is
  now visible in every artifact built under it, not only in the listing.
- **The listing** prints `composite n=K members=...`, and for n=1 "single box: not an
  envelope over boxes".
- **The `members` section** carries each member's `id@rev:digest16`, its unit row's key
  and `abs_ns_e6`, and its `box`. An envelope has no unit of its own (§6.3), so its
  members' units are the provenance a reader needs to interpret any absolute claim made
  about it.
- **Regeneration.** A new member set, or a rev of a member, makes a NEW envelope id (or
  rev). Moving the default to it is a default-set change (§3.6). Nothing re-derives in
  place.

## 7. The install-time tool (M3)

### 7.1 Home: one driver, owner-supplied cards and probes

`pcrec-measure` is a standalone C binary in a new `measure/` directory.

- **Build.** `make` builds it beside `pcrec-analyze`. It does not link `libpcrec` (the
  `analyze/` pattern: zero-dependency; an install on a stranger's machine needs `make` and
  `$CC`, which pcrec already requires).
- **What the driver owns.** Everything shared across owners:
  - run control: the quiet gate, the governor, affinity, A/A pairs;
  - the card interpreter;
  - the NULL rule;
  - the set writer and its self-check;
  - naming and immutability.
- **Its reader and writer are §9's module**, compiled into the driver as source. That is
  allowed because the module has no dependency on the compiler.
- **What owners supply.** Owners supply METHOD CARDS (§7.2) and PROBES. A kit quantity is
  measured by the kit's harness mode: the forms and their timing arms are the kit's
  (D157). A pcrec quantity is measured by pcrec's probes (armread's engine arms). The
  driver compiles each probe with `$CC` at run time.

Priced alternatives:

- **(b) A mode of the kit's harness only.** It inverts the ownership: the kit would own
  the writer for pcrec's quantities too.
- **(c) One python script.** Install time must not need python.
- **(d) Slots only.** It leaves out D166's install-time case.

Recommend the driver.

### 7.2 METHOD CARDS: a closed per-quantity table [r1 msc3-2]

A card is ONE row per (owner, quantity, ver), in the owner's card table: the kit's in its
tree (R-MS5), pcrec's in `measure/cards.tsv`. Its columns:

| column | meaning |
|---|---|
| `owner`, `quantity`, `ver` | identity; a committed (owner, quantity, ver) row never changes (append-only by version) |
| `dims` | the key's dimension names in order (§1.3) |
| `unit` | the row's unit |
| `subject` | the subject regime: `streamed-fresh` / `fit-repeated` / `landed:<g-ladder>` … (an owner token; the driver knows only how to build each token's buffer from the card's own parameters) |
| `lengths` | the call lengths measured |
| `launches`, `rounds` | the minimum per cell |
| `aa_rule` | the A/A design (`pair-per-group`, `pair-per-launch`, `bimodal-test` for the unit, §1.4) |
| `gate_e6` | the group's refusal gate (§7.3): a LABELLED UNMEASURED DEFAULT (D149) until derived from committed sets |
| `env` | the method's declared safe direction (cross-checked, §6.2) |
| `deps` | the dependency ids the producer hashes into `deps` (§2.4) |

**The checker refuses a row OFF ITS CARD.** That is a row whose quantity has no card in
the set's `cards` section; whose key arity ≠ `dims`; whose `n` < `launches × rounds`;
whose cells' lengths or subject are not the card's; or whose `deps` lacks a card dep.
A set's `cards` section must equal the owner's committed card rows at that `ver`, compared
by `test-measures` for official sets.

The closed table is what makes "the regime the number was measured in" (standing question
1) a checkable property of every row, not prose in a report.

### 7.3 What it measures, and the gates [r1 msc3-4]

**The reader closure.** It measures the quantities that have at least one reader row
(§5.4), computed from the census at run time. A quantity nobody reads is not measured (D77).

- **The quick profile** covers the single-call crossovers (M7-M12), β by shape (M3-M5),
  the dispatch charges (M16-M18 once they have cards) and a reduced g\* ladder.
- **The full profile** is grid1's shape, run in a slot (§7.6).

**Noise per row** is the group's A/A floor and the fit's spread, in QUADRATURE:
`noise = sqrt(aa² + fit²)`, both as fractions of the value. Here `fit` is the residual
spread of a fitted row, or the launch spread of a measured mean. Revision 1 used the A/A
floor alone, which understates a fitted crossover's uncertainty.

**Gates are PER GROUP.** A group passes iff its noise ≤ its card's `gate_e6` and the quiet
gate held during it. The unit group's gate is half its card's, and the unit group also
passes its bimodal test (§1.4). Three outcomes:

| outcome | condition | written |
|---|---|---|
| FULL | every group passes | the set, `partial 0` |
| PARTIAL | the unit group passes and at least one other group passes | a set holding only the passing groups' rows (and rows derived only from them), `partial 1`, and a printed summary naming every refused group, its noise against its gate, and the readers that will now skip; exit status 4 |
| REFUSED | the unit group fails, or nothing else passes | no set; a diagnostic naming the worst group; exit status 3 |

- **PARTIAL is legal** because absent rows skip (§4.3). A partial set changes selections
  only where it carries a row.
- **grid1's figures, quoted correctly.** Revision 1's 6.2% (2 × 3.09%) misquoted them.
  gridread §1.1 gives the per-group A/A p90 as 3.37% on F1 (141 groups), 0.17% on F3,
  0.38% on EXT, and the per-LAUNCH A/A p90 as 6.96% on F1. The 3.09% is the NULL rule's
  FRG, the grid's own p90 as gridread §1.2 computes it.
- **The gate is per group, from its card.** A single run-wide gate at 6.2% would have
  refused most user boxes, whose noisiest groups (the 64 KiB find-all groups, gridread
  §1.1) set the p90. A per-group gate refuses only those groups, and the rest of the set
  stands.
- **No local-beats-envelope claim.** A `local` set is not claimed to beat the envelope (or
  the shipped default) on its own box until a REPLAY test on that box says so: the
  [TABLE-JUDGE] interface run over the local cells. The tool prints its outcome and the
  set; it makes no claim.

### 7.4 The NULL rule, in full [r1 msc3-8]

A delta row (an arm's effect against its base: a crossover's signed side, a charge, a
regret) is NULL when EITHER:

1. **|Δ| ≤ max(A/A floor of its group, FRG × base).** FRG is THIS RUN's own p90 of the
   per-group A/A over every group (grid1: 3.09%). It is a property of the run, recorded in
   the header's provenance, not a constant.
2. **The launch-paired deltas disagree in sign.** These are the per-launch values of
   (arm − base) in the same round, one per launch. The row is NULL if they do not all
   share a sign, whatever their mean.

A NULL row is written `status null` with an EMPTY `value_e6`, never a rounded number.
Through §1.6 it makes every row derived from it NULL. A crossover is NULL when its
denominator is.

A cost row (β, F) is not a delta. It has no NULL rule of its own. Its noise is recorded,
and it becomes NULL only through §7.3's group refusal (absent) or as a denominator (§1.6).

### 7.4a Perf counters are OPTIONAL (D166 addendum 1, addendum 1.1)

No set, method, card, gate or tool may REQUIRE perf counters (`kernel.perf_event_paranoid`
varies per box).

- **Timing alone suffices.** Every set must be producible from TIMING ALONE, and every gate
  in §7.3 reads timing only (A/A floors, the NULL rule, the bimodal test).
- **The branch-miss pass** (gridread F2's predictability diagnosis) is an optional
  DIAGNOSTIC. When counters are unavailable it SKIPS LOUDLY (one stderr line naming the
  cause), and the skip is RECORDED in the set's `counters` header (`none` |
  `skipped:<reason>` | `branch-misses`, with the paranoid value read). So a listing shows
  whether the diagnosis exists for that set.
- **Nothing selects on it.** No row's `status` or selection depends on it. Counter-derived
  rows, if a card adds any, are `measured` extras that readers may not require; an absent
  counter row is skipped like any absent row.

When counters are unavailable, the tool PRINTS A SUGGESTION AND NEVER ACTS ON IT. It does
not run sudo or sysctl, and it does not write /etc. The text shows:

- the current `kernel.perf_event_paranoid` value;
- that 2 or lower enables the optional counter pass;
- what that adds (branch misses, the predictability diagnosis);
- the commands: one-off, `sudo sysctl kernel.perf_event_paranoid=2`; persistent, put
  `kernel.perf_event_paranoid = 2` in `/etc/sysctl.d/99-perf.conf`.

A check asserts that the suggestion text is printed with counters denied. It also asserts
that no set content differs between a counters-on and a counters-off run, except the
`counters` header and optional extras.

### 7.5 What it writes [r1 msc2-8]

It writes tier `local`: never a default in the committed store, never an envelope member,
never committed. It writes to a path the user names, `build/measure/` by default, with id
`local-<host hash>-<date>`.

It can be used by `--measures=FILE`, or installed as a BUILD's default with
`make DEFAULT_MEASURES=path`:

- **What the override does.** The Makefile runs `ksgen` on that file into
  `build/gen/measures_default.inc` and compiles THAT in place of the committed pointer
  table. The committed `src/core/*.inc` are untouched, so the tree stays clean and
  `git diff --exit-code` stays green. Revision 1's re-embed rewrote committed files, which
  needed an uncommitted tree.
- **What the build says.** Such a build stamps `local-…@1:digest`; `--version` and
  `--list-measurements` print `build_default_overridden 1` with the path. A shipped
  artifact therefore says it was built under a local measurement.
- **No hidden state.** There is no environment variable and no hidden run-time state.

### 7.6 Wall time

- **Install target.** 5 minutes, labelled a TARGET and unmeasured (the quick profile is
  not built; the number is a design budget).
- **The official profile** is grid1's shape: five launches, A/A per group, about 83
  minutes on grid1 (19:33-20:56). It runs by bench slot request, never at install.
- **The flag.** `--profile quick|full` selects; `full` refuses to run unless the box is
  idle by the gate.

## 8. Independence checks

### 8.1 Answers are identical under every set, and the dispatch is REACHED [r1 msc1-5, msc1-6, msc1-9]

`make test-measures-answers` is the generalized `test-memfn-sets` of R17-b′ §6.4 (that name
is kept for the kit's half).

**The sets:**

- every committed set;
- the SYNTHETIC extremes `all-walk`, `all-v1` and `all-wide`;
- `dispatch`, a synthetic set CARRYING the dispatch rows. M16-M18 are present and priced
  low enough that every pay rule pays, and its crossovers sit at small lengths, so the N
  dispatch is EMITTED wherever a reader allows it [r1 msc1-5].

Synthetic sets are tier `synthetic`, never embedded and never a default. They are reached
by `--measures=FILE` from M1, and by the harness lever until then.

**The population**, in three parts:

1. **The R17-b mover sample** (1 in 8 by pattern) plus every `.rxt` cell for those
   patterns.
2. **Boundary subjects [r1 msc1-5].** The corpus cannot reach run-time dispatch: 97.8% of
   its 62,360 subjects are under 36 B, and 42 fall in [36,64). So for each synthetic set
   and each sampled pattern with a dispatching site, the check GENERATES subjects of length
   L\*−1, L\*, L\*+1, W−1, W, W+1, 2W−1, 2W+1. L\* and W are read from THAT set by the
   independent python parser (§8.2), not from the artifact. The bytes are drawn from the
   site's own set and its complement, to place a landing before, at and after each
   boundary.
3. **Near-cap artifacts [r1 msc1-9].** The corpus artifacts within 10% of either emitted
   size cap (D84), plus one SYNTHETIC near-cap fixture. A set can move the size of the
   dispatch, and so whether an artifact is refused or re-rung by the fallback ladder.
   Under each set the arm records the refusal or ladder token and compares answers only
   where both compile. The token differences go to the census (§8.4) as movers, not as
   answer failures.

**The expectation.** The `.rxt` cells' oracle-verified answers. For generated subjects, it
is libpcre2's answer through `oracle_store`'s `match-at` kind (captured once by the local
adapter, committed, so the check runs on any box). The artifact is compared with the
oracle, not with another artifact, so the control shares no source with the subject
(learnings §3). A secondary arm compares artifacts built under two sets on the same
subjects, a differential that catches the case where both are wrong the same way.

**The REACH floor per dispatch ARM [r1 msc1-5].** It is a run-time counter, not a compile
count:

- The artifact is built through `build/pcrec-harness` with a harness-only lever,
  `--harness=reach-dispatch` (compound.md's `--harness=no-compound` precedent: a
  reserved-name internal entry, fenced by the same one-global check). The lever compiles a
  counter increment into each emitted dispatch arm.
- Per synthetic set, every arm the set's rows admit must execute ≥ 1 time over the
  population. Zero reach for an admitted arm FAILS ([MECH-REACH]).
- The admitted-arm list is derived from the set's rows by the python parser, not read from
  the artifact.

**The stamp arm (one direction only) [r1 msc1-6].** An artifact whose `<PREFIX>_MEASURES`
is empty must be byte-identical across every set. Revision 1 also demanded the converse
("empty EXACTLY when identical"), which is red on day one: an artifact that consulted the
set and whose reader rows all skipped is identical across sets yet correctly stamped. Only
empty ⇒ identical is a property; the converse is not.

**The structural arm.** Each artifact's dispatch literals equal the set's values as read by
the INDEPENDENT python parser of `set.tsv`, and the stamp names the loaded set.

### 8.2 Derived and fitted rows recompute; units recompute; digests agree [r1 msc3-7, msc1-10]

`tests/measures/recompute.py` reads only the set files, the census TSV and the spec's
registry text. It shares no code with `envelope.py` or `ksgen`. It recomputes, EXACTLY
under §1.7's integer rule:

- (a) every `derived` row from its `inputs`;
- (b) every `fitted` row from its `cells` (the raw cells are committed now, §1.5, so
  revision 1's count-and-hash dodge is gone);
- (c) every `ratio`/`walkbytes` row from `abs_ns_e6` and the unit row;
- (d) `values_digest`, `rows` and the NULL propagation of §1.6;
- (e) every `env-max`/`env-min` envelope row from its members' files, AND each key's safe
  direction from the census, against the card's `env` (§6.2);
- (f) every row against its card (§7.2).

The producer (C) and this checker (python) implement the registry from the spec's
formulas, not from each other. Population counts per set (measured / fitted / derived /
null, rows per card) are counted by awk and floored (K35).

### 8.3 Embedded = committed; the drift test is the gate [r1 msc1-12, msc1-14]

**THE GATE** is `make gen-tables && git diff --exit-code`, run by `test-measures` (and by
CI's existing gen-tables check). `ksgen` regenerates both `.inc` files from the committed
text, and any difference fails.

The secondary checks are:

- `tests/measures/` compares each embedded text with `set.tsv` byte for byte;
- the pre-parse is compared with a fresh library parse (findings tests §2/§3's shape);
- `PROVENANCE.md`'s and `index.tsv`'s `file_sha256` are compared with a fresh
  `hashlib.sha256` of `set.tsv` (the sha is KEPT, now with its checker);
- the default pointer table is compared with `DEFAULTS` read by awk (S947, §8.5).

### 8.4 The mover census, at landing [r1 msc1-1, msc1-9]

This is the mechanism for D166's "selections move automatically, with a mover census in
the same commit". `scripts/measure_census.sh OLD NEW` does the following:

1. It compiles a pinned POPULATION under `--measures=OLD` and `--measures=NEW`.
2. It strips the stamp line (and the `rx_info.measures` initializer) and compares emitted
   bytes.
3. It records, per artifact, the `*_WHY`/ladder tokens and any REFUSAL, under both sets
   [r1 msc1-9]. A set can move a near-cap artifact across a size cap or onto another rung,
   and that is a mover even when the selection the set feeds did not change.

Its output is `MOVERS.tsv` in NEW's directory:

- the artifact id;
- old and new byte hashes;
- old and new tokens and refusal;
- the attribution: the fired reader rows (from the owners' decision listings, §5.3) whose
  declared keys have different values in OLD and NEW.

The population is `tests/measures/census_population.tsv` (the identity gate's corpus as
the start, pinned at M1 by grep).

**When the census is verified.** Only in the commit that adds the set as a default or
moves a `DEFAULTS` pointer. There the landing lane runs `make test-measures-census`, which
re-runs the census and requires byte equality with the committed `MOVERS.tsv`; this is
part of that commit's delivery bar.

**What every build checks**, with no git history needed (CI is shallow):

- the structure: every `DEFAULTS` target that has a predecessor has a `MOVERS.tsv`;
- its header's `old`/`new` digests equal `index.tsv`'s;
- its `code_commit` names a commit (a 40-hex string, not checked for ancestry).

Revision 1 re-ran every set's census at HEAD on every build. That reds forever once any
later code moves a selection, or else forces edits to an immutable file.

**Re-pinned in the same commit, found by grep:** the abi readers (§3.6), the identity
gate's (B) pin and the EMITTED_BYTES readers.

### 8.5 Sabotage plan

S943-S952 are revision 1's allocation. S953-S960 are PROPOSED: they are free on main and
in every worktree as of `58338a09f`, and are outside every kit-reserved range; main
allocates them. Each has a REACH counter (the number of times the planted branch executed
in the sampled run), and each fails the named check.

| id | plant | detected by |
|---|---|---|
| S943 | `values_digest` excludes one row's value | §8.2(d) |
| S944 | an absent or NULL key read as 0 | a synthetic set with the key removed must produce the table's next row (R17-b′ SB8); structural arm |
| S945 | the stamp is empty although the kit returned `consulted` true (the OR dropped) | the stamp arm: the artifact differs across sets with an empty stamp; reaches R-MS2 |
| S946 | `--measures` beats the config line (fill-only broken) | the CLI fixture: a target whose config names Y, compiled with `--measures X`, must stamp Y and print the note |
| S947 | the generated pointer table names a different id than `DEFAULTS` [r1 msc1-11] | §8.3's pointer compare: `DEFAULTS` read by awk, INDEPENDENT of `ksgen`, against `--list-measurements`' `default_for` column |
| S948 | a `derived` row's value edited, inputs unchanged | §8.2(a) |
| S949 | the envelope takes `min` where the readers' direction is `max` | §8.2(e) |
| S950 | the staleness comparison always reports fresh | a kit form-body change fixture must flag its rows and their transitive dependants; REACH counts stale rows seen |
| S951 | the install tool's per-group gate never fires | a recorded 20% A/A-spread group fixture must be dropped (PARTIAL, exit 4) and a failing unit group must REFUSE (exit 3) |
| S952 | the census population shrinks silently (a class skipped) [r1 msc1-11] | a compiled-ARTIFACT manifest: the census writes one line per artifact it compiled, awk counts them against `census_population.tsv`'s row count; a shortfall fails |
| S953 | a fitted row's value edited | §8.2(b) |
| S954 | a ratio row computed against a non-unit row | §8.2(c), exact compare |
| S955 | a row off its card (n below `launches × rounds`) accepted | §8.2(f) |
| S956 | the dispatch arm's counter never incremented (reach lever disconnected) | §8.1 REACH floor reads 0 on the `dispatch` set |
| S957 | a derived row with a NULL input written non-NULL | §8.2(d) |
| S958 | a `-I` file whose header `id` differs from NAME accepted | the CLI fixture (§3.2) |
| S959 | `MOVERS.tsv` omits refusal/token changes | a near-cap synthetic pair of sets whose only difference re-rungs one artifact; the census must list it |
| S960 | the envelope ignores a reader that disagrees on direction | §6.2's exclusion listing; §8.2(e) |

S944 and S946 are answer-NEUTRAL (every form answers alike) except through the structural
arm. The plan declares them so, as R17-b′ declared SB12.

### 8.6 Lookup keys ⊆ declared readers [r1 msc1-13]

Every key a selection actually LOOKS UP is in some declared reader row's `reads`.

- **pcrec's side.** Its set accessor takes the reader row's id, and a debug-build assertion
  checks the key against that row's declaration. `make test-measures` runs the corpus
  sample under the debug build.
- **The kit's side.** It is R-MS4's landing bar. The kit's own test checks that its
  finder rows read only declared keys.

So the census (§5.4) cannot miss a reader, and `readers` in the listing is complete by a
check, not by assumption.

## 9. The sibling family: ONE knowledge-source module [r1 msc2-9]

### 9.1 The three members

Each of these is a named, versioned, provenanced body of knowledge, loaded by name or path
and stamped into what it shapes:

| member | content | loaded by | stamp/digest | store |
|---|---|---|---|---|
| the analysis object (D162, `--analysis`) | counts with derivations, an `include` chain, `.rxt` blocks | `--analysis`, the `analysis` config line, `-I DIR/<n>.rxt`, the store | `<PREFIX>_FINDINGS` + `rx_info.findings`, FNV-1a-64 `pcrec-find-1` | `src/findings/*.rxt`, embedded text + pre-parse (findgen.c) |
| measurement sets (this note) | keyed integer rows, cards, cells | `--measures`, the `measures` config line, `-I DIR/<n>.measures.tsv`, the store | `<PREFIX>_MEASURES` + `rx_info.measures`, FNV-1a-64 `pcrec-meas-1` | `measure_store/`, embedded text + pre-parse (ksgen.c) |
| [TABLE-JUDGE]'s picks file | (cell, table, row, pick) plus arm timings | a FILE operand of the judge | a digest in the judge's report | none (FILE only) |

Revision 1 built the second as a parallel copy of the first: a second name grammar, a
second `-I` probe, a second embed path, a second digest and stamp. That is the parallel
mechanism `pcrec-general-mechanisms-not-special-cases` forbids, and the third member is
already filed.

### 9.2 The module: `src/core/ksrc.c` / `ksrc.h`

ONE module, parameterised by a KIND row, with four parts:

```c
/* One knowledge kind: a row of the closed kinds table (ksrc_kinds[]). */
typedef struct {
    const char *kind;          /* "analysis", "measures", "picks" */
    const char *suffix;        /* ".rxt", ".measures.tsv", ".picks.tsv" */
    const char *digest_domain; /* "pcrec-find-1", "pcrec-meas-1", "pcrec-pick-1" */
    uint8_t     stops;         /* KS_STOP_S1 | KS_STOP_DIRS | KS_STOP_STORE */
    /* parse the text into the kind's document; the measures and picks kinds
     * use ks_tsv_read below, the analysis kind its existing .rxt reader */
    int  (*parse)(Arena *, const char *text, size_t len, void **doc, pcrec_error *);
    int  (*validate)(const void *doc, pcrec_error *);
    const KsStore *store;      /* embedded text + pre-parse, or NULL */
} KsKind;
```

1. **The section-TSV reader/validator** (`ks_tsv_read`). It reads `table_contract.md`'s
   §2/§4 shape from a buffer (no filesystem):
   - `#section` lines;
   - the per-section header;
   - the field-count truthfulness rule (§5¶1);
   - columns resolved by name;
   - unknown trailing columns ignored.

   It returns sections as arrays of rows indexed by header name. The same reader serves
   the files and the listings' own consumers. The measures kind's `validate` holds §1.6's
   rules; the picks kind's will hold its own.
2. **The name resolver** (`ks_resolve`). It handles:
   - the shared name grammar (`pcrec_find_name_ok` today);
   - §3.2's spelling classification;
   - the stops (S1 the compiling file, if the kind allows it; S2 `-I DIR/<name><suffix>`
     with exact entry matching; S3 the kind's store);
   - the refusal text naming the stops searched.

   These are the pieces `src/parse/rxt_find.c` has today as `probe_dir`,
   `dir_has_exact`, `stops_text` and `find_bundle`'s stop loop. The analysis CHAIN
   (`include`, `#include_next` self-reference, the terminal `default`) stays in the
   analysis kind: it is that kind's semantics, not a resolver feature, and the other kinds
   forbid it.
3. **The store** (`ks_store_text`, `ks_store_doc`). It gives the embedded text plus the
   pre-parse, keyed by name, for every kind with a store. It is generated by ONE
   generator, `scripts/ksgen.c`, which grows a kind argument, so findgen.c becomes
   `ksgen analysis …`.
4. **The stamp/digest builder** (`ks_digest`, `ks_stamp`). It provides FNV-1a-64 with a
   per-kind domain prefix (the one `fnv1a` in findings.c today), the 16-hex rendering, and
   the stamp grammar: empty = nothing asked; otherwise the kind's item list. It also
   provides the `rx_info` mirror's string (the same bytes as the macro).

It sits in `src/core/` because the compile reads it, and in no layer above: the parse
layer's `.rxt` reader is reached only through the analysis kind's `parse` pointer, so
`src/core` does not include `src/parse`.

`pcrec-measure` (§7) and the picks judge compile `ksrc.c` as source with a stage-0 kind
table, as findgen does today.

### 9.3 What each kind sets

| | analysis | measures | picks |
|---|---|---|---|
| suffix | `.rxt` | `.measures.tsv` | `.picks.tsv` |
| stops | S1, S2, S3 | S2, S3 (FILE always) | FILE only |
| parse | the `.rxt` reader (unchanged) | `ks_tsv_read` + §1.6 | `ks_tsv_read` + its own |
| chain | `include`, terminal `default` | none (refused) | none |
| precedence | fill-only (D93) | fill-only (D93) | n/a (one operand) |
| stamp | `query=bundle:digest;…` / `query=none` / empty | `id@rev:digest` / empty | the judge's report header |

### 9.4 Why one module and not a shared helper file

A helper file shared by copy-and-adapt would keep two stop loops, two embed generators and
two stamp grammars that agree today and drift tomorrow. The `compare_stack.md` §2 record is
the house's measured instance: definitions that exist more than once, each with its own
agreement check. The module makes each piece exist once. The kinds table is a declared
first-match table (`pcrec-decisions-as-first-match-tables`), listable by [LIST-TABLES] as
`--list-knowledge-kinds` when that row opens (no new flag before).

### 9.5 Migrating the analysis loader onto it: implement-then-replace, zero movers

| step | what | gate |
|---|---|---|
| K0 | `ksrc.c` lands with the MEASURES kind only (M0); findings untouched | the measures tests; `make strict` |
| K1 | the analysis kind is registered (its existing `.rxt` parse as `parse`, `findings_store.inc`/`findings_table.inc` as its store). `rxt_find.c`'s stop loop, `probe_dir`, `dir_has_exact`, `stops_text`, `pcrec_find_name_ok` and findings.c's `fnv1a` become calls into `ksrc`, the chain logic staying where it is. During K1 a debug build resolves every name BOTH ways and asserts equal results | zero movers: `emit_sweep.py` over the corpus (all arms), byte-identical; `tests/findings/` and `--list-analysis`/`--list-analyses` outputs byte-identical; the refusal texts byte-identical (the `-I` fixtures) |
| K2 | the old functions are deleted; `findgen.c` becomes `ksgen analysis`; `make gen-findings` calls it | `make gen-tables && git diff --exit-code` clean (the regenerated `findings_table.inc` byte-identical); the same three gates as K1 |

K1/K2 belong to M1 (§10.1), with the second loader, so the module exists with two clients
before the third ([TABLE-JUDGE]) arrives. No abi event: no emitted byte moves.

### 9.6 `--list-measurements` and [LIST-TABLES]

The listing's reader index is [LIST-TABLES]' census (§5.4). Its `sets` and one-set views
are the knowledge-source module's listing for the measures kind, the same code path that
`--list-analyses`/`--list-analysis` move onto at K1 for their name-resolution and
`provenance` sections. The analysis listing's data-kind sections stay its own.

## 10. Staged build, standing questions, lenses, unlocks, questions

### 10.1 Stages (each with its D77 trigger)

| stage | content | trigger |
|---|---|---|
| M0 | `ksrc.c` (K0) with the measures kind; `measure_store/` with ONE set (`zen4-grid1` as scratch, replaced by `zen4-grid2` when run); `ksgen.c`; the embed; the `<PREFIX>_MEASURES` stamp AND `rx_info.measures` (the abi event); the bare compile reads the LATEST set; cards (pcrec's file empty; the kit's via R-MS5); staleness listing; `--list-measurements` sets and one-set views over [LIST-TABLES]' census slice; `mf_measures` + `consulted`; spec `docs/spec/measures.md`; `test-measures` (recompute, drift gate, coverage) and `-answers` (with the synthetic sets incl. `dispatch`, boundary subjects, REACH floors, near-cap); S943-S945, S947, S948, S950, S953-S958 | R17-b′'s build, landing WITH R-MS1, R-MS2, R-MS3, R-MS5 (D166) |
| M1 | `--measures=`, the config line, `-I` resolution (§3.2), precedence tests, the per-target view, `measure_census.sh` + `MOVERS.tsv`, the analysis migration K1/K2 (§9.5); S946, S952, S959 | the first second set (grid2 after grid1, or a rollback need) |
| M2 | the envelope script, R-MS4's safe directions, the cross-member loss test, class defaults, the DEFAULT FLIP to the envelope with its census (an abi event, Q-MS-1); S949, S960 | a second box's OFFICIAL set (F5 Zen 1) |
| M3 | `pcrec-measure`, the quick profile, per-group gates and PARTIAL, `local` tier, `DEFAULT_MEASURES` into `build/`; S951 | a stated install-time need (D166 item 3 names it; no scheduler for it until a user asks) |
| M4 | pcrec's own quantities (`pcrec.c_call`, `pcrec.c_byte`), their cards, and `cand_rows[]` as readers in the census | the regime table's pcrec-side build |

### 10.2 The three standing questions (docs/design/CLAUDE.md)

**1. Measurement regime: RELEVANT.** Every number a set holds is a regime-bound
measurement.

- **Per quantity**, the regime is now a closed METHOD CARD (§7.2): subject, lengths,
  launches, rounds, the A/A rule. The checker refuses a row off its card.
- **The unit's regime is pinned** (§1.4), so a ratio means one thing within a
  `method@ver`. Across method versions nothing is compared.
- **The set header** records box, governor, compiler, `code_commit`, run and counters.
- **A different regime can flip a row.** Repeated against streamed subjects moves the
  walk from 150-250 to 0.4-22 branch misses/KiB (gridread F2). That is why the subject is
  on the card, why a set is one run, and why the envelope's direction belongs to the
  reader row (§6.2).

**2. Independent control: RELEVANT.**

- **Answers** are checked against the `.rxt` oracle and libpcre2 (`oracle_store`), not
  against another artifact. The dispatch is proven REACHED by a run-time counter per arm
  over generated boundary subjects (§8.1).
- **Derived, fitted and unit rows** are recomputed exactly by a python implementation of
  the SPEC's formulas, with no shared code with the C producer or the envelope script
  (§8.2).
- **The embed** is gated by regeneration plus `git diff`, with an independent awk read of
  `DEFAULTS` (§8.3).
- **Population counts** (statuses, census artifacts by a compiled-artifact manifest,
  sites per arm) are counted by awk over TSVs (K35).
- **Directions** come from two owners' declarations that must agree (§6.2).
- **The unavoidable shared source** is the measured numbers' own truth. It is controlled by
  per-group A/A floors, the NULL rule and replay ([TABLE-JUDGE], §6.3, §7.3), not by this
  design.

**3. What moves when regenerated: RELEVANT.**

- (a) **A new DEFAULT set** (including M2's flip to the envelope) moves the selections
  that read a moved quantity, the stamp of every consulting artifact, the identity gate's
  (B) pin and the EMITTED_BYTES readers. Under D162 ruling 1 it IS an abi event, carried
  with its `MOVERS.tsv` [r1 msc1-3]. A new non-default set moves nothing.
- (b) **Introducing the stamp and `rx_info.measures`** is M0's abi event (§3.6).
- (c) **A kit form-body change** stales the rows that depend on it, transitively. What
  that does to a default is Q-MS-STALE (§10.5). Until it is ruled, it is a listing flag
  and an INFO count.
- (d) **The K1/K2 analysis migration** moves no byte (§9.5).
- (e) **Spec:**
  - a new `docs/spec/measures.md` (the format, the key grammar, the registry with its
    integer formulas, the NULL rule, the stamp);
  - hunks in `cli.md` (§1.1.2 flag, §1.1.4 config, §2 listing, §2.11 `--emit-facts`);
  - `match_api.md` §6 (the `rx_info` member, a ¶ beside 6¶14) and §6.3 (stamp, abi line);
  - `rxt_format.md` (the `measures` config line);
  - `registry.md`, if `--list-axes` lists `--analysis` today (grep at build);
  - `table_contract.md` §1's table (the new listing).

  `docs/guide/` points at these and never restates them.

### 10.3 Sibling-family and design lenses

| sibling | what it teaches | what a set does differently |
|---|---|---|
| analysis object / findings (D162) | NOW SHARED, not imitated (§9): name grammar, `-I` search, store, digest, stamp grammar, `rx_info` mirror, fill-only precedence, `.rxt` DATA scope | no chain, no `include`, no `serves`; keyed integer rows, not counts |
| [TABLE-JUDGE] picks file | the third kind of §9's module; the interface the envelope's cross-member loss test and §7.3's replay claim use | FILE only, no store, no stamp in artifacts |
| [LIST-TABLES] | the census of declared tables; the reader index IS its census with a `reads` column (§5.4) | a set adds a column, never a scanner |
| limits (`limits.def`, `--list-limits`) | one declared table, listing and binary cannot disagree | limits are D149 constants chosen by people; set rows are MEASURED, provenanced and versioned |
| axes (`--list-axes`) | a registry whose rows are the options | a set is not an option; `--measures` is one axis whose VALUE is a set |
| option sets ([OPT-SETS], `--set=`) | NAME collision: "set" there is a bundle of options | always spoken "measurement set"; `--measures` cannot collide with `--set=` |
| `oracle_store/` / `third_party/` | the committed-data directory shape, `PROVENANCE.md`, a self-checking row count | derived by running our own code on a box, immutable, with a census at landing |
| D149 constants | a number that is a CHOICE vs a MEASUREMENT | this design is D149's measured branch; the gates in cards are labelled unmeasured defaults until derived |
| [ART-MGR] | the cache key (§3.7) | |

The design lenses (memory `pcrec-design-evaluation-lenses`):

- **General vs specific.** The format and the module are general (any owner, any kind);
  the first set is specific (Zen 4).
- **Core vs derived.** Costs are core; crossovers and envelopes are derived.
- **Fits the architecture vs a refactor.** It fits, and the one refactor it causes (K1/K2)
  is a zero-mover unification the family needed anyway.
- **First-match tables.** The kinds table, the reader rows, the envelope's exclusion rows
  and the card table are declared tables.
- **Unlocks** are filed in §10.4.

### 10.4 Unlocks, filed with triggers (not built)

- **The shared knowledge-source module.** BUILT BY THIS DESIGN (§9), now, with the second
  loader. Recorded here because the panel named it as an unlock and the disposition moved
  it into scope.
- **One data-mover census tool for findings, limits and measures.** `measure_census.sh`
  generalized to "compile a population under two knowledge states and attribute the
  bytes". Trigger: the next `src/findings/default.rxt` change, or a `limits.def` default
  change, that needs a census by hand.
- **Per-artifact dependency records.** An artifact (or its sidecar) records the exact set
  rows and analysis kinds its selections read. This gives exact staleness per artifact,
  the [ART-MGR] read-subset cache key and a consumed-subset stamp digest. Trigger:
  [ART-MGR]'s cache build with measured recompile churn, or the kit agreeing to a per-key
  report for another reason.
- **Incremental re-measure.** Measure only (transitively stale rows ∩ the reader
  closure). Trigger: the first re-measure slot whose stale-row list is under half the set.
- **D149 constants as measured rows.** The cards' own gates (`gate_e6`) and other tuning
  constants become measured rows of a set, which makes the gate itself data. Trigger: two
  official sets, whose observed per-group A/A distributions give the derivation.
- **Per-set out-of-sample replay.** Set A's picks judged on box B's cells. Trigger: the
  second official box (M2), through [TABLE-JUDGE].
- **Regime-tagged sets.** One box measured under two regimes (streamed vs repeated) as two
  sets, selected by a declared regime knowledge key. Trigger: a reader row whose pick
  flips between the regimes on the bench's populations (gridread F2 is the candidate).
- **A key-only schema for pcrec's own engine rows.** `pcrec.` quantities declared by key
  pattern with no card prose. Trigger: M4, if the cards for `c_call`/`c_byte` turn out to
  be all boilerplate.
- **`--list-measurements --diff A B`.** A set-to-set diff by key within one `method@ver`.
  Trigger: the first default change, to read a census with the cause beside it.
- **The bench stamps the set in its results.** Trigger: the bench shim's first sub-bench
  (it reads the macro or `rx_info.measures`).
- **A second-box envelope that holds COSTS.** Trigger: the pay rule's `unpaid` pick under
  the envelope measurably loses (§6.3, M2's census).
- **Rows with a per-quantity tolerance.** Trigger: when the first NULL or noisy row blocks
  a reader.
- **Run-time set choice.** NOT an unlock: D166 ruled compile time.

### 10.5 Questions for Frank (two)

- **Q-MS-1 (re-put). What does a bare compile read?** M0 and M1 compile with the LATEST
  set (D166's literal reading). At M2, when a second box's official set exists, each
  class's default flips to its ISA level's generic envelope (D161 add. 12).
  - **The cost of the flip.** Even at n=1 it MOVES selections: an envelope carries no cost
    rows, so every pay rule takes its `unpaid` pick and every cost reader skips. The flip
    is therefore an abi event with a census that lists exactly those movers.
  - **Recommend:** yes, latest set through M1 and the envelope from M2, with the census as
    the flip's landing bar.
- **Q-MS-STALE. What does a STALE row in a DEFAULT set do?** (§2.4)
  - (a) block the landing;
  - (b) carried-stale: read, flagged in the listing with a count, the manager reviews the
    count at each kit merge and schedules a re-measure when stale rows feed a reader;
  - (c) a declared cost-neutral equivalence row per form change.

  **The manager's leaning is (b), never a landing gate.** (a) puts every kit form edit on
  the bench box, and (c) is mechanism ahead of need (D77).

**Revision 1's other questions, and how they stand:**

- **Q-MS-2:** withdrawn. D162 ruling 1 is kept (§3.6).
- **Q-MS-3** (tier `local` for install-time sets; `official` only from a bench run on
  targeted hardware): settled as recommended. It follows D144 add. 4.
- **Q-MS-4** (`measure_store/`): settled by the manager (a one-token choice).
- **Q-MS-5** (the 6.2% gate): replaced by per-group card gates, labelled unmeasured
  defaults (§7.3).
- **Q-MS-6:** replaced by Q-MS-STALE.
- **Q-MS-7** (embed every rev): settled. Rollback must work from a release build.
- **Q-MS-8** (16 hex): settled, matching the FINDINGS width.

None of the settled choices changes an answer, and each was the manager's to make
(`pcrec-answer-free-choices-are-mine`).

## 11. Findings

- **F1.** R17-b′ §3.5 proposes `measures/<name>/`. `oracle_store/`'s shape fits better,
  because the data is derived by running our code, not vendored. Settled as
  `measure_store/<id>/<rev>/`.
- **F2 (revised) [r1 msc2-10].** The kit facts the framework needs are five requests
  (§4.4), not "two return facts". R-MS2 replaces revision 1's per-key lookup report with a
  boolean (§4.2).
- **F3 (revised) [r1 msc2-2].** D166's "latest set" and D161 add. 12's generic envelope
  differ even at one box, because the envelope drops cost rows. The design ships the first
  through M1 and flips to the second at M2 with a census (Q-MS-1).
- **F4 (revised) [r1 msc3-7].** "Derived crossovers recompute from their rows" now holds
  for `fitted` rows too, because the raw cells a fit reads are committed in the set.
- **F5.** Staleness of a row cannot be a file field in an immutable store. It is computed
  against the linked kit, transitively (§2.4). That puts the kit's form hash (R-MS3) on the
  framework's listing path, not its landing gate (pending Q-MS-STALE).
- **F6 (revised).** The stamp is defined on CONSULTATION, not on found rows (§3.5). An
  absent row skips a dispatch, so the artifact depends on the set even when nothing was
  read. The one-way check (empty ⇒ identical) is the property.
- **F7 (new) [r1 msc1-5].** The corpus cannot exercise run-time dispatch: 97.8% of 62,360
  subjects are under 36 B. Any answer-identity claim about a length-dispatching form is
  vacuous without generated boundary subjects and a per-arm run-time reach floor (§8.1).
- **F8 (new) [r1 msc2-9].** The analysis object and measurement sets are one family, and
  [TABLE-JUDGE]'s picks file is a third member. They share one module (§9), and the
  analysis loader migrates onto it with zero movers.
- **F9 (new) [r1 msc3-4].** grid1's own noise figures refute a run-wide noise gate.
  Per-group A/A p90 is 3.37% on F1 and 0.17% on F3, and the per-launch p90 is 6.96%. The
  noise is the walk's on 64 KiB find-all groups (gridread §1.1), so gating is per group,
  with a PARTIAL outcome.
