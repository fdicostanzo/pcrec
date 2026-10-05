# [OPT-SETS] — named option sets and how they interact (design note 1)

**Status: DESIGN ONLY** (lane optsets, 2026-10-05; plan row `[OPT-SETS]`,
opened by Frank the same day: "for simd and arch there will be sets of
choices that should be toggled together — `simd`, `no-simd` and the
various arch sets. They overlap. Plus the dial work is effectively 5 sets
of options. Formalize the idea of option sets and how they interact; there
may be other logical sets."). Nothing here is built. No emitted byte, stamp,
flag or `rx_info` field moves because of this note. Every surface it
proposes is an `abi` event when built (D76/D94) and carries its
`docs/spec/` hunk in the same change (D80). The build trigger is §6.

Every claim about today's tree was checked at `main` = `6f24e187`
(`abi` 60). The commands are given where a reader can redo them.

---

## 0. Findings first

1. **pcrec already has four set-shaped mechanisms, and each composes by a
   different rule.** These are the dial (`--tune`, five pinned rows OR'd
   into `flags`), the module gate (`--features std1`/`all`/`none`, frozen
   and derived named sets of modules), the `.rxt` `config` (a user-named
   bundle, `from`/`with` later-wins), and the findings bundle (`include`
   inside the bundle, D123). The general mechanism this note proposes is
   the one these four already approximate. It is not a fifth beside them
   (§1.3).
2. **One definition fits every case in the tree: a set is a NAMED BUNDLE
   of axis assignments.** Formally it is a partial function from axes to
   values. Sets combine by COMPATIBLE UNION, the join of partial
   functions. That join is commutative, associative and idempotent, and it
   is UNDEFINED when two sets give one axis different values. An undefined
   join is the conflict, refused by name. A predicate over the option space
   is admitted only as a way to COMPUTE a bundle's members from the axis
   registry when pcrec is built (a DERIVED set, like `--features all`). It
   is never a constraint the compiler solves. A lattice of levels (the ISA
   chain) is an ORDER on one family's members, and the constraint table
   reads it. It is not a way to merge sets (§2).
3. **A FAMILY is an exclusive group of sets, and it is an axis.** The
   dial's five positions are one family (`tune`). The ISA levels are
   another (`isa`). `scalar`/`no-simd`/`simd` are a third (`vector`).
   Exactly one member of a family is in force. Naming a member is
   assigning that family's axis, so it follows every rule an axis follows
   (later-wins on an ordered command line, file-wins across sources). Two
   members of one family therefore REPLACE each other, the way
   `--tune=min-size --tune=speed` does today. They never conflict. Only
   sets from DIFFERENT families (or standalone sets) can conflict.
4. **Precedence is a separate operator from composition, and it has only
   two tiers per source.** Within one source: the joined sets, then the
   source's own explicit per-axis flags on top. Explicit beats a set
   (Frank's 2026-09-16 dial ruling, generalized), REGARDLESS OF ORDER on
   the command line. That is the one place this design deliberately departs
   from gcc's `-ffast-math -fmath-errno` positional convention. Across
   sources, today's D93 per-axis table is unchanged: the file wins, with
   `--engine` the one exception and `--analysis` fill-only. A set named in
   a file makes the file speak about every axis in that set (§2.5).
5. **Today's tree already has three DIFFERENT answers to "one source
   contradicts itself".** A deny/force pair is REFUSED
   (`-fprefilter -fno-prefilter`, `-fstartpos-guard=align
   -fno-startpos-guard`, verified live). A repeated value option is
   LATER-WINS (`--tune`, `--engine`, `--features`, verified live). The
   comments pair is DENY-WINS (`-fcomments -fno-comments`, documented in
   `cli.md`). This note does not change any of them (§5.1). It states the
   rule they are cases of, and it names the comments pair as the one that
   does not fit (§5 Q7).
6. **The dial cannot become five sets in its current shape without four
   UNSPELLED axes.** Two of its cells already have no CLI spelling: the
   `[ART-SIZE]` ladder's bar and threshold. The entry-chain term is a
   `limits.def` constant. λ is not a cell at all, because
   `src/gen/clskit.c` reads the POSITION directly. A set may assign an
   axis that has no CLI spelling; the model needs no spelling, only a
   registry row. But λ's direct read must first become a read of a
   `cls-matcher` axis, and that change is byte-identical
   (implement-then-replace, §4.1).
7. **Nothing changes for an existing user by default (§5).** `RX_TUNE`
   stays, because pcrec-bench buckets on it. `--tune=` stays as the
   `tune` family's own spelling. The stamp this design adds,
   `<PREFIX>_SETS`, is new text on every artifact, so it IS an `abi` bump
   when built. That is the whole of its cost to a caller.
8. **The first consumer is `[MEMFN]` R4's vector rows and `--isa=L`.**
   Until a vector row or a declared ISA exists, `simd`, `no-simd` and every
   ISA member are vacuous. The dial alone does not need this mechanism; it
   ships without it. The build trigger (§6) is therefore R4c′ or R4c (the
   first `SCAN_ROWS` non-scalar row) or R4g (`--isa`), whichever lands
   first. The mechanism then lands WITH that row, and the dial is re-expressed
   on it in the same change, byte-identically.

---

## 1. Inventory: every option family today, and the ones coming

### 1.1 The families, by kind

"Kind" is the composition behaviour the axis already has, which is what
§2's model has to reproduce. Spellings are `cli.md`/`tuning.md`/`lib/pcrec.h`
at `6f24e187`.

| family | what it controls | CLI | `.rxt` | API (`pcrec_options`) | stamped as | swept by | kind today |
|---|---|---|---|---|---|---|---|
| deny bits (`-fno-X`) | one optimization each; 38 deny macros | `-fno-X`, hidden from `--help` (D47.3) | a config's `pcrec <raw>` line | `flags` bits 4-45 | per-mechanism OUTCOME stamps (D46: `RX_DFA_TABLE`, `RX_VM_PREFILTER`, …). `rx_info.flags` records each bit unless it is in `emit_info_def`'s hand-kept `strategy_denials` mask (`src/gen/emit_dfa.c` ~:2728; `[AXES-DENY-MASK]` would derive it) | `make test-axes`, one job per bit (`tests/axes/run_axes.sh`) | boolean; OR'd; idempotent |
| force bits (`-fX`) | the force twin of a deny | `-fprefilter`, `-fprefilter-collapse`, `-fstartpos-guard=align`, `-futf-check`, `-fcomments` | `pcrec <raw>` | `flags` bits 9, 20, 27, 39, 40 | as above | as above (force arms) | a deny/force PAIR on one axis is REFUSED when both are requested, except comments (deny wins) |
| contract axes | which ANSWER a call gives (§2.23, §2.36) | `-fno-startpos-guard`, `-fstartpos-guard=align`, `-futf-check` | `pcrec <raw>` | `flags` 25, 40, 39 | `RX_STARTPOS_GUARD`, `RX_UTF_CHECK`; kept in `rx_info.flags` | swept against their documented behaviour, not identity | boolean / three-valued |
| semantic bits | what the pattern MEANS | `-i`, `--ucp`, `--no-captures` | `flags` letters; `pcrec <raw>` | `flags` 0, 34, 2 | `rx_info.flags` unmasked | not swept (structurally ineligible, D125) | boolean |
| output/instrument | what the artifact CONTAINS or DOES besides matching | `--emit-main`, `--trace`, `-fcomments`/`-fno-comments` | `pcrec <raw>` | `flags` 1, 3, 26/27 | `--trace`: the instrumented artifact itself; comments: none (object byte-identical) | not swept | boolean |
| engine | coarsest selection; do-or-die for `dfa`/`vm` | `--engine=E` | `engine vm` | `engine` | `RX_ENGINE`, `RX_ENGINE_SEL`, `RX_ENGINE_WHY`, `rx_info.engine` | `make test-axes` (`dfa`, `vm`) | value; later-wins on the CLI; the one CLI-wins exception to D93 |
| ordinal value axes | a rung or a parameter | `--unroll=K`, `--vm-entry-shape=N` | `pcrec <raw>` | `unroll_k`, `vm_entry_shape` | `RX_UNROLL_K_WHY`, `RX_VM_ENTRY_SHAPE` | `--vm-entry-shape` rungs (tiered, `AXES_FULL=1`) | value; later-wins |
| the dial | a GROUP of axes from a pinned table | `--tune=N` / alias | `tune <pos>` | `tune` | `RX_TUNE` (unconditional; no `rx_info` mirror by design) | four `--tune` jobs + DIAL-S3 refusal-set check | **a set family**: five exclusive pinned bundles; deny cells OR'd, value cells read at their site (`src/core/compile.c:806`, `src/core/tune.c`) |
| encoding | the subject's character model | `-e`/`--encoding` | `encoding` | `encoding` | `rx_info.encoding` | per-encoding corpora | value; **IMPLIES** modules `unicode-props`+`ucp` under `utf8` (an enabling implication; the stamp keeps the REQUESTED features) |
| module gate | which constructs compile | `--features LIST` | `features` (UNION with configs unless `features only`) | `features` (spec string; NULL = no request) | `PCREC_FEATURE_SET`, `PCREC_FEATURE_MODULES` | not an axis (refusals change by design) | **a set mechanism**: `std1` is a FROZEN named set, `all` a DERIVED one, `none` the empty one |
| findings | which subject statistics speed reads | `--analysis NAME` | `analysis <name>` | `analysis` | `RX_FINDINGS` (`kind=source:digest`), `rx_info.findings` | not an identity axis (speed only) | **a bundle**, composed INSIDE itself by `include` (D123); config later-wins; CLI fill-only |
| resource bounds | budgets, capacities, caps | `--step-budget=`, `--work-budget=`, `--backtrack-frames=`, `--max-emit-*`, `--warn-emit-bytes=` | `budget` | the budget/cap fields | `RX_FAST_FRAMES` etc. | `limits.md`'s own checks | value; raise-only for the caps |
| size policy | refuse vs degrade | `--fast-or-fail` | `pcrec <raw>` | `flags` 41 | masked out of `rx_info.flags` | not swept | boolean |
| unspelled constants | dial cells with no flag | none (the ladder's bar is a constant beside `size_term_choose`; the threshold is `limits.def`'s `PCREC_SIZE_TERM_THRESHOLD`, kind `BUILD_D`; the entry-chain term; λ's rule) | none | none | through outcome stamps | through the dial's jobs | set only by the dial |

The table excludes MODES and LISTINGS (`--emit-ir`, `--list-*`,
`--explain`) and OUTPUT ROUTING (`-o`, `-p`, `--target`, `-I`). These
choose what pcrec does, not what an artifact is. A config's `pcrec` line
already refuses them on the same grounds (`cli.md` §1.1), and §2.1 draws
the set boundary at that line.

### 1.2 What `[MEMFN]` and `[OPT-DIAL]` add (designed, none built)

| family | source | what it controls | proposed spelling | kind |
|---|---|---|---|---|
| vector-row denies | integration.md Q15 | `SCAN_ROWS` rows 1-3 at prefilter sites; the same rows in loops (D91 budget 2); T6's `vec-masked`; the SWAR row | `-fno-vec-scan`, `-fno-vec-skip`, `-fno-vec-run`, `-fno-swar-scan` (four bits) | deny bits |
| kit-internal row denies | integration.md Q15 | the kit's C1/C2 composition rows (`cube`, `unrolled`, …) | `--memfn-deny=cube,unrolled,…` | a LIST-valued option |
| ISA level | isa_selection.md §1.2, Q4 | the declared level: x86-64-v1..v4, armv8-a(+sve/+sve2) | `--isa=L` | an ordered value; a POSET (two chains over an architecture-neutral bottom) |
| ISA route | isa_selection.md §1.2.3 | target attributes (A) vs the consumer's macros with an `#error` floor (M) | `--isa-route=macro` | value; meaningful only with `--isa` |
| ISA check / dispatch | isa_selection.md §1.2.4, Q5 | a per-entry check; an ELF `__builtin_cpu_supports` hybrid | `-fisa-check=entry`, `-fisa-dispatch=cpu-supports` | opt-in, held |
| loader marker | isa_selection.md Q6 | `GNU_PROPERTY_X86_ISA_1_NEEDED` | `--isa-marker` | opt-in; never implied by `--isa` |
| force twins for the dial's deny-only cells | opt_dial_design.md §7.2a option 1 | keep premul / anchored-dfa / tiered-entry at a size position | `-fpremul-table`, … | on demand, not promised |
| a ladder value flag | §7.2a option 2 | the ladder's bar and threshold | `--size-term-bar=`, `--size-term-threshold=` | on demand, not promised |

### 1.3 What already behaves like a set, and how

- **The dial is a set FAMILY in all but name.** `src/core/tune.c`'s
  `TUNE_TABLE[5]` is five rows of (deny mask, three value cells). The
  position names one row, and `compile.c:806` ORs its deny mask into the
  caller's flags. The value cells are read at their sites
  (`pcrec_tune_size_term_bar`, `_threshold`, `_vm_inline_chain_max`). λ is
  read off the position by clskit. `balanced` is all-sentinel, so it
  assigns nothing. That is why it is byte-for-byte today's default.
- **`std1` is a PINNED set and `all` is a DERIVED one.** "The frozen set's
  contents never change after it ships" (`cli.md`, `--features`). That is
  the same guarantee D103 gives the dial table, made earlier for modules.
  `all` follows the module roster as it grows. Both kinds are needed
  (§2.2).
- **A `.rxt` `config` is a USER-defined bundle.** It composes with `from`
  (materialized once) and `with` (flat later-wins). Its `pcrec <raw>`
  flags apply first and its typed directives on top, so within one config
  "explicit typed beats raw" already holds. Configs are what a user writes
  when they want their own set. This note adds no second user-defined set
  kind (§2.6).
- **A findings bundle composes only inside itself** (`include <other>`,
  per kind, first-found, D123). A config names ONE analysis and never a
  precedence list. D123's reason, "one composition mechanism, not two that
  both merge", is the reason §2.4 makes set composition ORDER-FREE.
- **`-e utf8` is an implication**, and so is `--engine=vm` disabling the
  DFA prefilter. Both are a fact about one axis's value that enables or
  disables something on another axis, applied silently and documented.
  §2.7 classifies these.

**A finding outside this note's scope, recorded for the manager:**
`cli.md` says `--no-captures` "forces the DFA engine". Live,
`--no-captures --engine=vm --pattern 'a(b|c)+d'` emits `RX_ENGINE "vm"` and
`RX_NCAPS 1`. The behaviour is reasonable (an explicit engine beats an
implied one, which is §2.5's own rule). The spec sentence overstates it,
and it is a one-sentence D80 fix whenever `cli.md` is next touched.

---

## 2. The model

### 2.1 Terms

- An **axis** is one row of the option registry: a name, a DOMAIN of
  values, a DEFAULT, a CLASS (§2.8) and zero or more SPELLINGS (CLI, `.rxt`,
  API). Today's axes are `src/core/axes.def`'s rows (D111), the value
  options of §1.1, and the four UNSPELLED axes the dial already sets
  (§0 item 6). An axis needs a registry row. It does not need a spelling.
- An **assignment** is a PARTIAL function from axes to values. An axis it
  does not mention is unassigned, which is different from an axis assigned
  its default value. A **pin** is an axis assigned its default value. A pin
  changes nothing on its own; it is how a set says "this axis must stay as
  it is" (§4.2).
- A **set** is a named assignment, together with the class it inherits from
  its members (§2.8).
- A **family** is a named group of sets, with one DEFAULT member, of which
  exactly one member is in force. A family is itself an axis: its domain is
  its members. A set that belongs to no family is a **standalone** set. The
  model treats a standalone set S as the two-member family {S, absent},
  where "absent" is the empty default, so "every set has exactly one family"
  holds without a special case.
- A **source** is one place assignments come from: the command line, a
  target's composed `.rxt` config, the API struct, and the built-in
  defaults. A source is ORDERED if its assignments come in a sequence
  (argv) and UNORDERED if they do not (a struct's fields).

### 2.2 What a set IS: three candidates, and the choice

| candidate | a set is… | membership | overlap | composition | verdict |
|---|---|---|---|---|---|
| **(A) bundle** | a named assignment, `{axis := value, …}` | an axis is in S iff S assigns it | two sets assign one axis | union, defined iff they agree (§2.4) | **CHOSEN** |
| (B) predicate | a constraint over the option space, `C(ω)` ("no vector row is allowed") | a configuration is in S iff it satisfies C | the intersection of two regions | conjunction; a conflict is an empty intersection | **admitted only to COMPUTE a bundle** (a derived set, §2.3) |
| (C) lattice | a level in an ordered chain (v1 ⊂ v3 ⊂ v4) | a level and every level below it | a lower and a higher level overlap by inclusion | join = max | **admitted only as an ORDER on one family's members**, read by constraints (§2.7) |

Why (A):

1. **It is predictable in Frank's D103 sense.** The resolved configuration
   is a function of the NAMES given, computed by a fold with no search. A
   predicate names a REGION. Turning a region into the one configuration an
   artifact is built with is a choice, and a choice the compiler makes on
   its own is exactly the "too unpredictable" objection D103 answered for
   the dial.
2. **An artifact can say how it was built.** A bundle's name plus the
   explicit flags reproduce the configuration. A predicate's name does not,
   because many configurations satisfy it.
3. **A conflict is decidable by inspection.** Two bundles conflict iff
   they assign one axis two different values. There is no satisfiability
   question to answer, and the diagnostic can name the axis.
4. **All four precedents in the tree are already bundles** (§1.3). (B) and
   (C) have no instance in the tree as a composition rule.
5. **It fits the house's table idiom.** A set table is rows of data, and
   it is listable (`[LIST-TABLES]`).

Why (B) and (C) are still needed, in their narrow roles:

- **(B) as a DERIVED set.** `--features all` must mean "every module this
  build has". `no-simd` must mean "every vector row", including rows added
  after the set was written, or a new vector row would escape it. So a set
  may be written as a predicate over registry ROWS ("every axis tagged
  `vector`"). The predicate is evaluated when pcrec is BUILT and
  materialized into a bundle. The compiler never solves it, and
  `--list-sets` shows the materialized bundle. A **pinned** set's bundle is
  written out and frozen by ruling: the dial (D103) and `std1` ("never
  change after it ships"). The two kinds behave differently across
  releases, and the set table says which each set is.
- **(C) as an ORDER.** The ISA members form a poset: two chains,
  `portable < x86-64-v1 < x86-64-v2 < x86-64-v3 < x86-64-v4` and
  `portable < armv8-a < armv8-a+sve < armv8-a+sve2`, with x86 and Arm
  members incomparable. The order is read by the constraint table ("a row
  declared at v4, forced, needs isa ≥ v4", §2.7), by `test-axes` (run only
  the members at or below the box, §3.5), and by `[ART-MGR]`'s catalog
  ("runs on"). **It is never used to COMBINE**: joining `x86-64-v3` and
  `x86-64-v4` by taking the max would silently pick one of two things a
  caller asked for. Both are members of one family, so the later one
  replaces the earlier (§2.3), or the conflict is refused.

### 2.3 Families: exclusive groups, and why they replace rather than conflict

The dial's positions, the ISA levels and the vector widths are
**alternatives**. "Min-size and speed" is not a configuration, and neither
is "v3 and armv8". A family makes that a property of the data, not of
anyone's judgment:

- **A family is an axis.** `--tune=speed` and `--set=speed` both assign
  the `tune` axis the value `speed`. Every rule that applies to an axis
  then applies to it unchanged: later-wins on the ordered command line
  (today's `--tune=min-size --tune=speed` → `speed`, verified live), and
  file-wins across sources (today's D93 addendum for `tune`).
- **Members of one family therefore never conflict.** They replace each
  other by the axis's own rule. Only sets in DIFFERENT families can
  conflict, and a standalone set is its own family.
- **A family declares a required CLASS for its members** (§2.8), checked
  statically against every member's bundle when pcrec is built. The `tune`
  family requires identity-class, refusal-preserving members. That is
  `tuning.md` §5.5's acceptance and D125's structurally-ineligible bucket,
  stated once as data rather than re-argued per cell.
- **A family's default member is normally EMPTY** (`balanced`,
  `portable`, `auto`). Naming the default is then the same as naming
  nothing, which is why `--tune=balanced` and no flag are byte-identical
  today, and why `tuning.md` §4's explicit-set residual costs nothing for
  `tune`.

### 2.4 Composition: the compatible union

Write `dom(S)` for the axes S assigns. The **join** of two assignments is

```
S ⊔ T  =  S ∪ T                         if S(a) = T(a) for every a ∈ dom(S) ∩ dom(T)
       =  undefined (a CONFLICT)        otherwise
```

It is commutative, associative and idempotent, so **the order in which
sets are named never matters** and naming a set twice is harmless. This is
D123's lesson applied: one composition rule with no precedence list among
sets. Two sets that agree on a shared axis (`no-simd` and a dial position
that also denies vector rows) compose silently, because there is nothing to
resolve.

**A conflict is refused, by name, before anything is compiled**:

```
pcrec: set 'simd' and set 'min-size' disagree on axis 'vec-scan'
(simd: allow, min-size: deny); name only one of them, or set the
axis explicitly (-fno-vec-scan)
```

D26 applies: the code and the named parties are exact, the wording is
not. **Explicit beats a set (§2.5), so an explicit spelling always
resolves a conflict, but only in the directions that HAVE a spelling.** A
deny-only axis can be explicitly denied and cannot be explicitly allowed.
For that half the remedy is "name only one set". The message offers only
spellings that exist. This is `tuning.md` §1's "where a spelling exists"
narrowing, met again one level up. A force or allow twin stays an
on-demand addition (`opt_dial_design.md` §7.2a option 1), never something
this mechanism invents.

**List- and set-valued options decompose into one axis per element.**
`--features` is one boolean-ish axis per module, `--memfn-deny=` one
deny/default axis per kit row, and the join is taken element by element.
Union composition then falls out with no special rule (`on ⊔ on = on`; an
unmentioned module is unassigned). `features only` is an assignment of
every element, and conflict checking is per element, so `simd`'s "keep row
X" and a list denying row X is a conflict on X alone.

**Numeric axes are equal-or-conflict.** Two sets setting the entry-chain
term to 8,192 and 4,096 conflict. Neither max nor min is taken, for the
same reason the ISA order is not used to merge.

### 2.5 Precedence: explicit over set, per source; D93 across sources

Composition (⊔) combines PEERS. Precedence combines TIERS, through a
right-biased override `S ◁ E` (E's value where E assigns one, S's
elsewhere).

**Within one source, two tiers:**

```
resolved(source) = ( ⊔ of the sets that source names ) ◁ explicit(source)
```

- **Explicit beats a set, regardless of order.** This is Frank's
  2026-09-16 dial ruling ("explicit per-switch flags beat the dial"),
  generalized from one family to all of them. `--set=min-size
  -fpremul-table` and `-fpremul-table --set=min-size` mean the same thing.
  That is a deliberate departure from gcc, where `-ffast-math
  -fmath-errno` and `-fmath-errno -ffast-math` differ. Position-dependence
  is a precedence list in disguise, and D123 ruled against having two
  composition mechanisms.
- **On an ORDERED source, a repeated explicit axis is later-wins**, which
  is what every value option does on pcrec's command line today. On an
  UNORDERED source (the API struct), two fields that assign one axis
  different values are REFUSED, because there is no order to break the tie
  (§3.3: `tune = speed` with `sets = "min-size"`).
- **Pinned deny/force pairs keep today's refusal.** `-fprefilter
  -fno-prefilter` is not one axis assigned twice. It is two bits under a
  constraint row (§2.7, row 1), and it stays refused.

**Across sources, today's per-axis rule, unchanged** (D93 and its
addendum, `cli.md` §1.1), as a first-match table over each axis:

| # | predicate on axis `a` | `a`'s value comes from | reported? |
|---|---|---|---|
| 1 | `a` is `engine` and the CLI assigned it explicitly, not `auto` | the CLI | yes, if the file disagrees (today's text) |
| 2 | `a` is `analysis` | the file if it names one, else the CLI (fill-only) | yes, if both name one (today's text) |
| 3 | the target's resolved file assignment covers `a`, explicitly OR through a set the file names | the file | yes, if the CLI assigned `a` explicitly or through a set and the values differ (generalizes today's `tune`/`engine`/`analysis` reports) |
| 4 | the CLI's resolved assignment covers `a` | the CLI | — |
| 5 | otherwise | the default | — |

Row 3's "through a set the file names" is the one new reading. **A set
named in a file makes the file speak about every axis in that set**,
because the file's author chose the set and everything in it. A CLI
`-fno-tiered-entry` survives a file's `tune min-size`, because `min-size`
does not assign `tiered-entry`. A CLI force on premultiplication would
not survive it, and would be reported. That is exactly today's behaviour,
because today the dial's cells are the only set-assigned axes.

**The resolution order, start to finish.** This is a fold, not a
selection, so it is written as numbered steps rather than as a table. The
two DECISIONS in it (who writes an axis, and the constraint verdict) are
first-match tables.

1. Per source, resolve each FAMILY axis: its explicit spelling, or a
   `--set=` naming a member, later-wins on an ordered source.
2. Across sources, resolve each family axis by the table above.
3. Expand each in-force member into its bundle, tagged with the source
   that selected it.
4. Per source, join that source's bundles. A conflict is refused here.
5. Per source, overlay that source's explicit assignments (◁).
6. Across sources, resolve each ordinary axis by the table above. Record
   each axis's PROVENANCE (default / CLI set / CLI explicit / file set /
   file explicit).
7. Walk the constraint table (§2.7) over the result. A REFUSE row stops
   the compile.
8. Complete every unassigned axis with its default.
9. Stamp (§3.4).

Step 6's provenance record IS the general mechanism `opt_dial_design.md`
§1.3 recommended and deferred: "explicit-set PROVENANCE for every
D93-composed axis … deferred to its own measured trigger (D77): the
trigger is the THIRD axis that needs the distinction". The set mechanism is
that third consumer, twice over: the override tail of the stamp (§3.4) and
the attribution in row 3's report both need to know which tier wrote an
axis. So this design builds provenance as the general form, and adds no
per-family bit (§5 Q6).

### 2.6 User-defined sets are configs; there is no second kind

A `.rxt` `config` is already a user-named bundle, with its own ruled
composition (`from` materialized once, `with` flat later-wins). A config
may NAME sets (§3.2), and a set may not name a config. Why the two are not
merged:

- A config is FILE-scoped and may carry non-option content (`analysis`,
  `budget`). Its later-wins composition is a ruled, shipping contract
  (`cli.md` §1.1, D93), and its author wrote the order.
- A set is PCREC-scoped. It is pinned or derived by ruling, listed by
  `--list-sets`, stamped, and conflict-checked.

So sets are pcrec's VOCABULARY and configs are the user's SENTENCES. Inside
one target, two sets named by any of its configs are peers of the FILE
source and are joined, so a conflict between them is refused. The configs'
own typed lines keep later-wins at the explicit tier, unchanged.

**A meta-set** (a set whose bundle assigns another family's axis, e.g. a
hypothetical `tiny` = `tune := min-size` + `vector := scalar`) is admitted by
the model. Family axes resolve first (§2.5 steps 1-2), and a static check
when pcrec is built rejects a cycle. It has no consumer, so it is not built
(D77, §5 Q11).

### 2.7 Constraints and implications: one first-match table

Some relations are not compositions. They are facts about the RESULT: two
values that cannot coexist, or a value that is meaningless without another.
They are rows of one first-match table, walked once over the resolved
assignment (§2.5 step 7). The first row whose predicate holds decides. A
REFUSE row names itself in its diagnostic. Rows are data and listable.

Three verdicts exist:

- **REFUSE**: the compile stops, naming the row's parties.
- **INERT**: the axis is kept and stamped as having no effect
  (`RX_UTF_CHECK "inert"` is the shipped precedent).
- **DERIVE**: a documented, pre-existing implication that ENABLES something
  on another axis without changing any accepted pattern's answer.

**A new rule may refuse or mark inert. It may not silently assign.**
"SIMD requires an ISA level" is therefore NOT an implication: a vector row
that needs a declared level simply does not apply below it. That is the
`SCAN_ROWS` row's own PREDICATE (integration.md §2.1, `BASE`/`DECLARED`).
Only a FORCE that cannot be honoured needs a row here.

| # | row | predicate | verdict | status |
|---|---|---|---|---|
| 1 | `prefilter-pair` | `-fprefilter` ∧ `-fno-prefilter` | REFUSE | shipped (verified live) |
| 2 | `collapse-pair` | `-fprefilter-collapse` ∧ `-fno-prefilter-collapse` | REFUSE | shipped (verified live) |
| 3 | `startpos-pair` | `-fstartpos-guard=align` ∧ `-fno-startpos-guard` | REFUSE | shipped (verified live) |
| 4 | `utf-check-extent` | `-futf-check=extent` | REFUSE (reserved) | shipped |
| 5 | `comments-pair` | `-fcomments` ∧ `-fno-comments` | DENY WINS | shipped; the one silent resolution (§5 Q7) |
| 6 | `isa-route-orphan` | `isa-route = macro` ∧ `isa = portable` | REFUSE | designed (isa_selection.md §1.2.3) |
| 7 | `isa-marker-orphan` | `isa-marker` ∧ `isa` not on the x86 chain | REFUSE | designed (isa_selection.md Q6) |
| 8 | `forced-row-below-level` | a row declared at level L is FORCED ∧ ¬(isa ≥ L) in the poset (incomparable counts as below) | REFUSE | designed here |
| 9 | `utf-check-byte` | `-futf-check` ∧ `encoding = byte` | INERT | shipped |
| 10 | `startpos-align-byte` | `-fstartpos-guard=align` ∧ `encoding = byte` | INERT | shipped |
| 11 | `utf8-enables-modules` | `encoding = utf8` | DERIVE `unicode-props`, `ucp` enabled (the stamp keeps the REQUESTED set) | shipped |
| 12 | `vm-drops-dfa-prefilter` | `engine = vm` | DERIVE no DFA prefilter (R21 E-6) | shipped |
| 13 | otherwise | — | proceed | — |

Rows 1-5 and 9-12 already exist, scattered (the pair refusals are
diagnosed at compile and carry a pattern offset). Collecting them is
implement-then-replace and byte-identical: the same diagnostics, the same
inert stamps. That is the D46 controllability half applied to the option
layer itself. A row added later is one table row, not a new `if`.

Rows 9-10 must precede any row that would REFUSE the same parties, and the
table's order says so. That is the reason this is a first-match table and
not an unordered rule set.

### 2.8 A set's class, and what the class decides

Every axis already has a class in the tree's own vocabulary (`tuning.md`
§1, §4; D125). A set's class is the WEAKEST of its members', in this order:

| class | members are… | swept by `test-axes` as | may be in `tune`? |
|---|---|---|---|
| identity | answer-preserving, refusal-preserving | identity; LOST fails | yes |
| engine-selecting | answer-preserving but may move the engine or refuse under `--engine=dfa` (`-fno-splice-calls`, `-fno-atomic-discharge`, `-fno-ctx-node`) | identity, with LOST printed where documented | no |
| policy | changes WHETHER an artifact is produced, never its answers (`--fast-or-fail`, the caps) | not swept | no |
| contract | changes which ANSWER a call gives, on purpose (`-futf-check`, `-fstartpos-guard=align`) | against its documented behaviour | no |
| semantic | changes what the pattern MEANS (`-i`, `--ucp`, `--no-captures`, `encoding`) | not swept | no |
| instrument | changes what the artifact DOES besides matching (`--trace`) or CONTAINS (`-fcomments`, object-identical) | not swept (own suites) | no |

The class column is the `kind` column `[AXES-DENY-MASK]` already wants in
the axes registry, to derive `rx_info.flags`' `strategy_denials` mask
instead of hand-keeping it. Both readers need the same column, so it
should be one column, built once (§5.2).

**`explicit-only` axes.** A few options must never be implied by any set:
`--isa-marker` (isa_selection.md Q6, "never implied by `--isa`") and the
held `-fisa-dispatch=cpu-supports`. The registry tags them, and the static
check rejects any set whose bundle assigns one. "Never implied" becomes a
property of the data rather than a promise in a design note.

---

## 3. Surfaces

Everything in this section is DESIGNED, and none of it is built (§6).

### 3.1 The command line

- **`--set=NAME[,NAME…]`**, repeatable, accumulating (the names are
  joined, §2.4). A member of a family assigns that family's axis, so
  `--set=speed` ≡ `--tune=speed`. An unknown name is refused, listing the
  vocabulary, in `--features`' shape. **`--set` is a user feature**, so
  unlike the `-f` family (D47.3) it appears in `--help`.
- **Family sugar keeps its own spelling.** `--tune=` stays exactly as
  shipped (aliases, the `=`-form rule for negatives, out-of-range
  refusal). `--isa=L` (designed) is the `isa` family's spelling. A new
  family gets a sugar flag only when it has a reason the generic `--set=`
  lacks: an ordinal spelling, as `tune` has, or a vocabulary already
  established outside pcrec, as `-march`-style level names are.
- **`--list-sets`**: a table-contract listing (`docs/spec/
  table_contract.md`), one row per (set, axis, value), with the family,
  pinned/derived, the class and the member's order position. It is a
  `[LIST-TABLES]` producer at birth. A derived set lists its bundle as
  materialized in THIS build.
- **What may be a set member** is exactly what a config's `pcrec <raw>`
  line may carry (`cli.md` §1.1: compile options only), plus the
  unspelled registry axes. Modes, listings, output routing, `-p`,
  `--pattern` and file operands are excluded on that line's own grounds.

### 3.2 `.rxt`

- **A config body gains `set <name>{, <name>}`.** It is one schema row
  (`rxt_schema.def`), config-scoped like `tune`, and the names are
  resolved and refused-if-unknown when the file is read. `--list-source`
  carries it AS WRITTEN (its `tune` column's rule). A block may not name
  sets, for the reason a block may not name `tune`: a set is a build
  configuration, and the block is the definition.
- **`tune <pos>` stays** as the `tune` family's sugar.
- **Inside one target**, every set named by any of its configs is a peer
  of the FILE source (§2.6). Sets are joined and their conflicts refused.
  The configs' typed lines keep later-wins, and the block's own directives
  keep more-specific-wins, both at the explicit tier.
- **H11 holds by construction for identity-class sets**: a target built
  under one must answer exactly as the block's own compile, which the
  harness already checks for every target. A target naming a
  contract-class set (§4.5's `pcre2-utf`) changes answers on purpose. The
  harness's H11 control must therefore read the target's set class, and
  compare such a target against its declared behaviour, the way the axes
  sweep treats a contract axis. This is a build-time obligation, named
  here so it is not discovered late.

### 3.3 The library API

- **`pcrec_options.sets`, a `const char *`** in `--set=`'s vocabulary,
  NULL meaning "no request". This is `features`' own shape and its own
  NULL rule (REL-1.11, `match_api.md` §8.2). It is resolved once in
  `pcrec_compile`, at the altitude where `tune` is validated today
  (`src/core/compile.c:800`, before any pass).
- **`tune` stays.** The struct is an UNORDERED source, so `tune ≠
  balanced` together with a `sets` string naming a different `tune` member
  is REFUSED (§2.5). The same holds for every family sugar field (`isa`
  when it exists).
- The resolved per-axis PROVENANCE (§2.5 step 6) is internal. Nothing in
  the API exposes it until a consumer asks (D77).

### 3.4 The stamp, and `rx_info`

**`<PREFIX>_SETS`**, a string emitted UNCONDITIONALLY on every artifact of
both engines, in the shared prologue beside `<PREFIX>_TUNE`:

```c
#define RX_SETS ""                              /* every family at its default */
#define RX_SETS "min-size,no-simd"              /* two non-default members */
#define RX_SETS "min-size;premul-table"         /* a member cell overridden */
```

- **Grammar: `member{,member}[;axis{,axis}]`.** The members are the
  NON-DEFAULT members in force, one per family, in registry order. The
  part after `;` names, by registry name, every axis a set in force
  assigned whose final value came from a HIGHER tier: an explicit flag, or
  the file over a CLI set (§2.5 row 3). A consumer buckets on the part
  before `;`. The tail exists so that an artifact never claims a set
  unqualified when one of its cells was overridden. The CLOSED-token
  discipline of `RX_TUNE` holds per token.
- **Only non-default members are printed**, so adding a FAMILY later moves
  no existing artifact's stamp (its default member prints nothing). The
  stamp's BIRTH is one `abi` event (D76/D94: every artifact gains a
  line). After that, a new family is not an abi event by itself. A new
  member's bundle is, if it moves emitted bytes, as any new axis is.
- **`<PREFIX>_TUNE` stays, unchanged.** It becomes the `tune` family's
  member, printed by the same token table (`pcrec_tune_token`). pcrec-bench
  buckets on it, and it is printed even at `balanced`.
- **No `rx_info.sets` mirror.** Nothing at run time behaves differently
  because of a set's NAME. This is `tuning.md` §5.3's reasoning for
  `tune`, unchanged (D77: build the mirror when a consumer asks). The
  first candidate consumer is `[ART-MGR]`'s catalog picking a variant, and
  what it needs is `rx_info.isa`/`isa_family` (isa_selection.md §1.2.3),
  which are OUTCOME fields of the `isa` axis, not a mirror of the set
  string.
- **No digest yet.** A digest over the full resolved non-default
  assignment (the `RX_FINDINGS` digest's shape) would let two artifacts be
  compared as "built identically" without reading every outcome stamp. Its
  consumer would be the bench's testee identity. It is not built until
  that consumer asks (§5 Q5).

### 3.5 How the checks treat a set

**`make test-axes`: a set is an axis.** The sweep already treats the
dial's four non-default positions as "a fifth kind of axis" on the same
RXTFLAGS/RXTDUMP mechanism (`tests/axes/run_axes.sh`, the header's
`[OPT-DIAL]` paragraph). The general form:

- **The job list** = every bit axis alone (today) ∪ every NON-DEFAULT
  member of every family ∪ every standalone set. The list is derived from
  `--list-sets`, never hand-copied. That is the script's own "the registry
  is derived, never hand-copied" rule, and it costs one more dump reader.
- **The class decides the comparison** (§2.8): an identity-class set
  fails on MISMATCH, LOST or GAINED. An engine-selecting one prints LOST.
  Contract, semantic, policy and instrument sets are not swept, and the
  run says so with the reason, as it does for `--ucp` today. DIAL-S3's
  keyed refusal-set comparison generalizes from the `tune` family to every
  family whose required class is refusal-preserving.
- **Combinatorics: no products by default.** A set alone against the
  default is the unit, as a bit axis alone is. A PAIR job exists only as a
  row of a declared `pairs` list, each row naming its reason: two families
  whose members feed the SAME table's predicates. The first such pair is
  `vector` × `isa`, both read by `SCAN_ROWS` (integration.md §2.1). A pair
  sweeps the members' product. Today's job count grows by the members,
  not by their product. At the first build that is four (`tune`) plus
  three (`vector`), plus the ISA members the box can run.
- **The `isa` family is swept per box.** A declared-ISA artifact compiles
  anywhere but RUNS only on a CPU at or above its level. So the job list
  runs the members at or below the box's level in the poset (§2.2), and
  SKIPS the rest LOUDLY with a count, PC-3's absent-library shape. This is
  the order's first real consumer. On the Mac that means `portable`,
  `armv8-a` and nothing above it natively. x86 correctness under
  Rosetta 2 (survey.md §1.2) is a separate opt-in arm.
- **Vacuous members still run** (S219's precedent, already followed for
  `max-speed`). `simd`/`no-simd`/`scalar` are vacuous until vector rows
  exist. The run prints that their resolved assignment is empty, rather
  than skipping them. A check that skips its vacuous members is the one
  that fails to fire the day they stop being vacuous.

**The identity gates.** Three, all built with the mechanism, each with an
expectation side that does NOT share a source with the set table
(`learnings.md` §3):

1. **Re-expression identity**: the dial moved onto the set table emits,
   at all five positions over the whole corpus, bytes identical to the
   shipped `TUNE_TABLE` build, except for the `RX_SETS` line itself.
   `tests/codegen/run_tune_dial.sh` already reads its expectations from
   `tuning.md` §5.4, not from `src/core/tune.c`. It keeps doing so, and
   reads the set table only as the thing under test.
2. **No-request identity**: with no set named anywhere, every artifact is
   byte-identical to the pre-mechanism build, apart from `RX_SETS ""`.
   This is the abi event's own (B) pin.
3. **Listing against spec**: `--list-sets` rows checked against the
   spec's set table (`tuning.md` gains it, §5.3), as §5.4's table is the
   contract for the dial today. The check reads the spec.

**mech (sabotage).** Rows are numbered from main's highest S-id at the
build, not here. The rows the mechanism owes, with their detectors:

| sabotage | detector |
|---|---|
| a pinned member's cell is dropped from its bundle | gate 1 (reads the spec) |
| the join stops detecting conflicts (returns the left operand) | a `tests/cli` case naming two REAL overlapping sets; see the witness note below |
| explicit loses to a set (the overlay's operands swapped) | a `tests/cli` case: an explicit flag against a set cell, asserting the artifact's outcome stamp |
| family members conflict instead of replacing | `--tune=min-size --tune=speed` must still compile, `RX_TUNE "speed"` (today's pinned behaviour) |
| the stamp's override tail is omitted | the explicit-beats-set case, asserting `RX_SETS`'s tail |
| a derived set's predicate misses a new row | a registry check: every axis tagged `vector` is denied by `no-simd`, counted from the axes file by plain-text scan (`[AXES-DENY-MASK]`'s own gate shape) |
| the constraint table's order inverts rows 9 and 1-3 | the shipped pair refusals and inert stamps, already pinned in `tests/cli` |

**Witness note.** The conflict row needs two real sets in DIFFERENT
families that assign one axis different values. Until vector rows exist,
none does. The dial's members only deny, and no other family exists. If
that is still true at build time, the row ships UNREACHED with its
derivation, as S219 did. It does not get a test-only set: a set that
exists only to be refused is a fixture the vocabulary must then carry
forever.

**The bench.** `pcrec-bench/APPROACH.md` §2 item 4 already defines a
testee as "(engine, version, build/run configuration)" and anticipates
"later SIMD on/off" as a first-class axis. Its litrun subbench already
names deny testees (`-fno-lit-run`, `-fno-altcls-factor`). A set gives
such a testee a NAME the artifact itself carries:

- A testee is spelled `--set=no-simd` and labelled from `RX_SETS`.
  `RX_TUNE` keeps working for the dial.
- A **pinned** set names the same configuration across releases (D103),
  so `pcrec[speed]` is comparable across versions in the sense the bench
  already restricts comparisons to. A **derived** set (`no-simd`) names
  "this release's vector rows, off", which is what a SIMD-off testee
  means.
- The bench chooses its testees explicitly. Nothing here asks it to sweep
  a product.
- **Bench-only questions, for relay to pcrecdev2 rather than for this lane
  to answer** (memory `pcrec-ask-bench-dev`): (i) does the adapter key a
  pcrec testee on the INVOCATION it ran or on the artifact's STAMPS?
  (ii) would an `RX_SETS` value with a `;` tail break its stamp parser?
  (iii) does it want a configuration digest (§3.4) as testee identity?
