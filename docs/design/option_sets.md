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
