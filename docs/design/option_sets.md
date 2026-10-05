# [OPT-SETS] — named option sets and how they interact (design note 1)

**CROSS-NOTE 2026-10-05 (manager; Frank's ruling on [MEMFN] Q12): pcrec carries NO architecture knowledge in its decision tables.** It passes an OPAQUE token to the [MEMFN] kit's K0 price query, and the kit chooses ISA forms internally (docs/design/memfn/integration.md revision 2, §7). Consequences for this note: the `isa` family reduces to ONE opaque token axis (no ISA poset, no isa-route, constraint rows 6-8 removed); the `vector` family reduces to the kit's three deny flags (`-fno-kit-scan/-loop/-native`). §4's ISA/vector worked examples are superseded where they conflict; the next revision folds this in. **CROSS-NOTE 2026-10-05, later (D146; integration.md REVISION 3, §12.1): the K0 price query is itself superseded by DELEGATION.** The `vector` family becomes family `memfn` (`auto` / `simd` / `no-simd` / `memfn-off`) over three deny bits, `-fno-memfn-scan` and `-fno-memfn-loop` (D91 budget 1 / budget 2 sites to the kit's frozen BASELINE profile, pcrec's pre-migration text) and `-fno-memfn-native` (the portable profile; DEFAULT ON during the SIMD hold); `scalar` dissolves; `--memfn-deny=` passes through unparsed; the `isa` axis stays one opaque, HELD value. `memfn-off` is likely §6.1's first trigger (the bench's kit-off testee, D146's guard), and trigger 2's predicted size/vector disagreement dissolves (a size position sends a policy bit to the kit instead of denying). **CROSS-NOTE 2026-10-05, revision 4 (integration.md §20.2, §14.10; r3 panel G-F2/G-F12): the polarity is corrected and the kit's switches become axes.** `memfn-native` is a deny/force PAIR, DEFAULT OFF, enabled by `-fmemfn-native` (D112's `-fcomments` shape); the native default flip (R4f) changes only its default. So family `memfn` is `auto` (∅), `simd` (`memfn-native := force`), `no-simd` (`memfn-native := deny`), `memfn-off` (`-fno-memfn-scan -fno-memfn-loop`). All three bits join `strategy_denials`. The kit's own per-form switches are no longer an unparsed pass-through only: each is published by the kit's switch table and becomes a GENERATED axis row spelled `--memfn-deny=NAME`, listed by `--list-axes` and swept by `test-axes`, with pcrec never spelling the names in `src/`. **CROSS-NOTE 2026-10-05, revision 4.2 (D147; integration.md §L, Q50-Q52): the `memfn-off` set and its two bits are withdrawn.** D147 makes the scalar algorithm a live layer and SIMD a layer on top, each accepted on its own, so there is no permanent frozen baseline for `-fno-memfn-scan`/`-fno-memfn-loop` to select. Family `memfn` is `auto` (∅), `simd` (`memfn-native := force`, the SIMD-on reading) and `no-simd` (`memfn-native := deny`, the SIMD-off reading, which runs the CURRENT scalar layer). A kit change's off arm is its own generated `--memfn-deny=NAME` row (D144 item 4). §6.1's first trigger becomes the bench's `pcrec[simd]` testee at R4e′. **CROSS-NOTE 2026-10-05, revision 4.3 (D147 addenda 6-7; integration.md §R4.3.1): ONE SIMD switch.** Addendum 6 replaces the off / portable / native profiles with one switch and a meaning. OFF gives portable C (plain C, SWAR, libc; runs anywhere). ON gives text hardware-optimized for a specific CPU, which may not execute elsewhere, and whose forms, levels and cascades are the kit's per-site choice. Addendum 7 makes it OFF by default until the SIMD hold lifts, and the flip is its own ruled event. The axis is `memfn-simd`, a deny/force pair `-fno-memfn-simd` / `-fmemfn-simd`, `PCREC_AXIS_DEFAULT_OFF` (D112's `-fcomments` shape), with both bits in `strategy_denials`. So family `memfn` is `auto` (∅), `simd` (`memfn-simd := force`) and `no-simd` (`memfn-simd := deny`). Until the flip, `auto` and `no-simd` render the same text. A target ISA level is a kit form question, not a pcrec axis (addendum 6). So the held `isa` token axis and integration.md's R4i (`--isa=`) are withdrawn as pcrec options, re-opened only by a ruling. A kit change's off arm is still its own generated `--memfn-deny=NAME` row.

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

**REVISION 2** (lane optsrev, 2026-10-05, from main `9fd125cb`, still
`abi` 60). It applies the light D6 panel r1
(`docs/dev/reviews/2026-10-05-r1-option-sets.md`, two critics, eighteen
findings, all ACCEPTED by the manager). **Read §R first.** Each change is
marked `[r1 <id>]` where it is made. The idea held: a set is a partial
assignment, a family is an exclusive axis, and the dial's five positions
are pinned members. What moved:

- Today's cross-source composition is now MEASURED per axis kind (§2.5a,
  42 cells, `option_sets_measurements/`). It is six different rules, not
  "D93 file-wins per axis". The model is restated against that table, and
  every place it would change today's behaviour is a numbered ruling for
  Frank (§5.4, R1-R7).
- A deny/force pair is ONE three-valued axis (§2.4a).
- The constraint table applies every row, REFUSE rows first (§2.7).
- `RX_SETS` is recommended NOT built until a consumer asks (§3.4). Its
  conditional design is stated in case one does.
- Every check's expectation side is re-sourced (§3.5).
- The triggers are tightened, and the dial re-expression is its own step
  with its own trigger (§6).

The revision-1 text survives where it was not refuted. Superseded
sentences are replaced, not struck through, and the `[r1 …]` mark says
which finding moved them.

---

## R. Revision 2 — every r1 finding and where it is answered

| id | sev | finding (short) | answered in |
|---|---|---|---|
| OS-M1 | BLOCKER | deny/force pairs are one registry row; cross-source they union then refuse, they are not file-wins | §2.4a (one three-valued axis); §2.5a rows A1-A10 (measured); §2.5 cross-source table row 1; §4.1/§4.4 examples fixed; R1 |
| OS-M2 | MAJOR | raw bits UNION and `features` is WHOLE-LIST file-wins; "D93 per axis, unchanged" is false | §2.5a (one row per axis kind, 42 cells); §2.5's cross-source table rewritten against it; §4.5 restricted to the file tier; R2, R4, R5 |
| OS-M3 | MAJOR | constraint rows co-fire, so the table is not first-match | §2.7 rewritten: every row applies, REFUSE rows first, first-match only within one party's rows; cell M3 measured |
| OS-M4 | MAJOR | "conflicts refused" and "explicit beats set" hold only within one source | §0 item 4, §2.5 "Across sources": refuse on three-valued `-f` axes, report-not-refuse (D93) on value axes; R3 |
| OS-M5 | MAJOR | not "a fifth beside them" | §0 item 1 reworded ("a fifth that absorbs the dial, at its own step"); §4.5 names the `features` migration trigger |
| OS-m6 | MINOR | order matters on family axes | §2.3, §2.5: family axes are ONE ordered CLI tier; explicit-over-set covers non-family axes only |
| OS-m7 | MINOR | meta-set resolution is circular | §2.6: meta-sets FORBIDDEN by a build-time check until a consumer names one (Q11) |
| OS-m8 | MINOR | cells made inert by a DOMINATING axis | §2.7a: a `dominates` relation, measured witness (`--tune=min-size -fno-size-term`) |
| OS-m9 | MINOR | "weakest member" order is incoherent; ladder cells move the give-up surface; class check reads a hand tag | §2.8: an explicit rule table, not an order; the give-up carve-out; DIAL-S3 named as the real control |
| OS-m10 | MINOR | row 5 deny-wins is a fourth verdict; DERIVE also disables | §2.7: verdict GRANDFATHERED-ASSIGN; DERIVE defined as enable OR disable |
| OS-m11 | MINOR | row 8 needs a FORCE the mechanism never invents | §2.7 row 8 ships UNREACHED with its derivation; "not ≥" wording |
| OS-n12 | NOTE | dial byte-identity sound, code locations need correcting | §1.3, §4.1 corrected (`compile.c:955`, `clskit.c:524-526/:697/:781`, the K59 drop rung at `compile.c:1406-1425`) |
| OS-n13 | NOTE | raw `--tune` in a config wins silently today, so row 3 adds a report | §2.5a cell E2; R4 lists the stderr change |
| OS-n14 | NOTE | a D103 diff adding a vector deny to a pinned member turns an accepted pair into a refusal | §4.1 "the D103 ritual gains one step"; §6.2 |
| S1 | high | the tail stamps the SPELLING | §3.4: tail DROPPED; the conditional stamp is computed from the resolved configuration |
| S2 | high | two stamps for one fact | §3.4: families that own a stamp (`tune`, `isa`) are excluded |
| S3 | high | no consumer, always emitted (D77) | §3.4: recommend NO stamp until a consumer asks; if built, emitted only when a set is NAMED. Q5 |
| S4 | high | request-dependent stamp length feeds size selection | §3.4: placeholder rendering after every decision (K79's mechanism) + a set-invariance check; §5.2 |
| S5 | med | the byte-count reader class is understated | §5.2a: the reader class, found by grep, with the D94-addendum suites |
| S6 | med | registry names become stamp vocabulary | §3.4: with the tail dropped only MEMBER names are vocabulary; a member rename is an abi event |
| S7 | med | config surface overlap; silent CLI loss; API error code | §3.1/§3.2: `--set` refused on a `pcrec` line; §3.3: refused through `pcrec_error` as `features` is; R4's report covers the silent loss |
| S8 | high | three of seven sabotage rows unreachable today | §3.5 sabotage table: a reach column; every unreachable row declares `SAB_EXPECT=UNREACHED` + reason + a `SAB_REACH` probe, so `NOW REACHED` fires |
| S9 | med | the conflict path may stay unreached after the trigger | §2.4 + §6.1: the join-conflict machinery is DEFERRED; a build-time table check refuses the first cross-family disagreement, which is the trigger to build it |
| S10 | high | the derived-set check shares its source with its subject | §3.5: the population is counted from `axes.def` by NAME PATTERN and from `SCAN_ROWS`' emit sites, never from the `vector` tag |
| S11 | med | gate 3 cannot read a spec for DERIVED sets | §3.5 gate 3: pinned sets against the spec table; derived sets against S10's independent count |
| S12 | high | the test-axes job list derives from `--list-sets` | §3.5: an independent member-count floor from the spec's family table |
| S13 | high | v4/SVE/SVE2 never run on a house box | §3.5a: a compile-only arm per architecture; a runtime owner per ISA member, two members UNOWNED; R6 |
| S14 | med | vector × isa is 32 corpus runs | §3.5: the size stated; the pairs rows floored at 3 × 2 per box |
| S16 | high | triggers 1 and 2 are not real triggers; Q12 moves a working mechanism | §6 rewritten (three independent triggers, each a request or a witness, not a landing); the dial re-expression is §6.2's own step with its own D77 trigger; Q12 |

---

## 0. Findings first

1. **pcrec already has four set-shaped mechanisms, and each composes by a
   different rule.** These are the dial (`--tune`, five pinned rows OR'd
   into `flags`), the module gate (`--features std1`/`all`/`none`, frozen
   and derived named sets of modules), the `.rxt` `config` (a user-named
   bundle, `from`/`with` later-wins), and the findings bundle (`include`
   inside the bundle, D123). **[r1 OS-M5] The mechanism this note proposes
   is a FIFTH, and it absorbs exactly one of the four: the dial, at its own
   later step (§6.2).** The other three stay separate on purpose. A config
   is the user's sentence and a set is pcrec's word (§2.6). A findings
   bundle is subject data that speed decisions read, composed inside
   itself (D123). `--features` gates SYNTAX in a vocabulary of modules.
   Its migration trigger is the first set that must assign a module
   (§4.5), and no set does today. Until then the count is four plus one,
   and after §6.2 it is four.
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
   reads it. It is not a way to merge sets (§2). **[r1 OS-M1] A deny/force
   pair (`-fno-X`/`-fX`) is ONE axis with three values** (default, deny,
   force), because it is one `axes.def` row. It is not two booleans under a
   constraint (§2.4a).
3. **A FAMILY is an exclusive group of sets, and it is an axis.** The
   dial's five positions are one family (`tune`). The ISA levels are
   another (`isa`). `scalar`/`no-simd`/`simd` are a third (`vector`).
   Exactly one member of a family is in force. Naming a member is
   assigning that family's axis, so it follows the rule its axis KIND
   follows (§2.5a): later-wins on the ordered command line, and file-wins
   with a report across sources, which is what `tune` does today. Two
   members of one family therefore REPLACE each other, the way
   `--tune=min-size --tune=speed` does today. They never conflict. Only
   sets from DIFFERENT families (or standalone sets) can conflict. **[r1
   OS-m6] So ORDER matters on a family axis**: `--set=min-size,speed` is
   `speed`, its reverse is `min-size`, and `--tune=` and `--set=` naming
   members of one family are one ordered tier, later-wins between them.
4. **Precedence is a separate operator from composition.** Within one
   source there are two tiers: the joined sets, then the source's own
   explicit per-axis flags on top. On NON-family axes, explicit beats a set
   REGARDLESS OF ORDER on the command line (Frank's 2026-09-16 dial
   ruling, generalized). That is the one place this design deliberately
   departs from gcc's `-ffast-math -fmath-errno` positional convention.
   **[r1 OS-M2/OS-M4] Across sources there is no single rule today.** It
   was measured per axis kind (§2.5a), and there are six rules: union then
   the pair rule for `-f` bits, union for `flags` letters, whole-list
   file-wins for `features`, the CLI-wins exception for a typed `engine`
   line, fill-only for `analysis`, and silent file-wins for everything
   else (`encoding`, budgets, value options, any raw-line spelling). The
   model KEEPS each kind's rule. A set named in a source contributes at
   that source's set tier. **"Conflicts are refused" therefore holds in
   two places only**: between sets of different families within one
   source, and on a three-valued `-f` axis across sources (today's
   union-then-refuse, §2.4a). On a value axis a cross-source disagreement
   involving a set is file-wins and REPORTED, D93's own shape (§2.5, R3).
   "Explicit beats a set" likewise holds within one source. Across sources,
   a file's set beats a CLI explicit on a value axis, and it is reported.
5. **Today's tree already has three DIFFERENT answers to "one source
   contradicts itself".** A deny/force pair is REFUSED
   (`-fprefilter -fno-prefilter`, `-fstartpos-guard=align
   -fno-startpos-guard`, verified live). A repeated value option is
   LATER-WINS (`--tune`, `--engine`, `--features`, verified live). The
   comments pair is DENY-WINS (`-fcomments -fno-comments`, documented in
   `cli.md`). **[r1 OS-M1] The first and third hold ACROSS sources too.** A
   file's `pcrec -fno-prefilter` with a CLI `-fprefilter` is refused, in
   either direction, and a file's `-fcomments` with a CLI `-fno-comments`
   is deny-wins in either direction (cells A1/A2/A5/A6/A7). This note does
   not change any of the three (§5.1). It states the rule they are cases
   of, and it names the comments pair as the one that does not fit (§5 Q7).
6. **The dial cannot become five sets in its current shape without four
   UNSPELLED axes.** Two of its cells already have no CLI spelling: the
   `[ART-SIZE]` ladder's bar and threshold. The entry-chain term is a
   `limits.def` constant. λ is not a cell at all, because
   `src/gen/clskit.c` reads the POSITION directly. A set may assign an
   axis that has no CLI spelling; the model needs no spelling, only a
   registry row. But λ's direct read must first become a read of a
   `cls-matcher` axis, and that change is byte-identical
   (implement-then-replace, §4.1). **[r1 S16] That re-expression is its
   own step with its own trigger (§6.2).** It does not ride the first
   build.
7. **Nothing changes for an existing user by default (§5).** `RX_TUNE`
   stays, because pcrec-bench buckets on it. `--tune=` stays as the
   `tune` family's own spelling. **[r1 S3] The recommended first build
   adds NO stamp.** No emitted byte moves because of the set layer, so it
   carries no `abi` event of its own (§3.4). If a consumer asks for a set
   stamp, it is emitted only on artifacts that NAME a set. The caller-
   visible changes are new stderr reports where a cross-source
   disagreement is silent today (R4). Each is listed as a ruling.
8. **The first consumer is `[MEMFN]` R4's vector rows and `--isa=L`.**
   Until a vector row or a declared ISA exists, `simd`, `no-simd` and every
   ISA member are vacuous. The dial alone does not need this mechanism; it
   ships without it. **[r1 S16] The build trigger (§6.1) is the first of
   three, and each is a REQUEST or a WITNESS, not a row landing:** a named
   consumer asks for one name over two or more vector-family bits that are
   already on main; the first cross-family DISAGREEMENT appears in the set
   table (the conflict path's first witness); or the bench asks, through
   pcrecdev2, for a named SIMD-off or ISA testee. R4g's `--isa=L` alone
   is NOT a trigger: a family is an axis, so `--isa` ships as an ordinary
   value option without this mechanism. R4c′'s lone SWAR bit is not one
   either.

---

## 1. Inventory: every option family today, and the ones coming

### 1.1 The families, by kind

"Kind" is the composition behaviour the axis already has, which is what
§2's model has to reproduce. Spellings are `cli.md`/`tuning.md`/`lib/pcrec.h`
at `6f24e187`.

| family | what it controls | CLI | `.rxt` | API (`pcrec_options`) | stamped as | swept by | kind today |
|---|---|---|---|---|---|---|---|
| deny bits (`-fno-X`) | one optimization each; 35 deny bits (bits 4-45 less the five force bits, `--ucp` (34) and `--fast-or-fail` (41)) | `-fno-X`, hidden from `--help` (D47.3) | a config's `pcrec <raw>` line | `flags` bits 4-45 | per-mechanism OUTCOME stamps (D46: `RX_DFA_TABLE`, `RX_VM_PREFILTER`, …). `rx_info.flags` records each bit unless it is in `emit_info_def`'s hand-kept `strategy_denials` mask (`src/gen/emit_dfa.c` ~:2728; `[AXES-DENY-MASK]` would derive it) | `make test-axes`, one job per bit (`tests/axes/run_axes.sh`) | boolean; OR'd; idempotent. **[r1 OS-M2] Across sources: UNION** (cell A4: a file's `-fno-premul-table` and a CLI `-fno-req-byte` both apply) |
| force bits (`-fX`) | the force twin of a deny | `-fprefilter`, `-fprefilter-collapse`, `-fstartpos-guard=align`, `-futf-check`, `-fcomments` | `pcrec <raw>` | `flags` bits 9, 20, 27, 39, 40 | as above | as above (force arms) | **[r1 OS-M1] with its deny, ONE three-valued axis per `axes.def` row.** Both values requested, from ONE source or from TWO, is REFUSED (cells A1, A2, A5, A9). The exception is comments, where deny wins in either direction (A6, A7, A10) |
| contract axes | which ANSWER a call gives (§2.23, §2.36) | `-fno-startpos-guard`, `-fstartpos-guard=align`, `-futf-check` | `pcrec <raw>` | `flags` 25, 40, 39 | `RX_STARTPOS_GUARD`, `RX_UTF_CHECK`; kept in `rx_info.flags` | swept against their documented behaviour, not identity | boolean / three-valued |
| semantic bits | what the pattern MEANS | `-i`, `--ucp`, `--no-captures` | `flags` letters; `pcrec <raw>` | `flags` 0, 34, 2 | `rx_info.flags` unmasked | not swept (structurally ineligible, D125) | boolean. **[r1 OS-M2] Across sources, the letters UNION** with the CLI's `-i`/`--ucp`/`--no-captures` (cells B1-B4). Within the file, a typed config `flags` line is REPLACED whole by the block's (B8), while a raw `pcrec -i` line unions with the block (B7) |
| output/instrument | what the artifact CONTAINS or DOES besides matching | `--emit-main`, `--trace`, `-fcomments`/`-fno-comments` | `pcrec <raw>` | `flags` 1, 3, 26/27 | `--trace`: the instrumented artifact itself; comments: none (object byte-identical) | not swept | boolean |
| engine | coarsest selection; do-or-die for `dfa`/`vm` | `--engine=E` | `engine vm` | `engine` | `RX_ENGINE`, `RX_ENGINE_SEL`, `RX_ENGINE_WHY`, `rx_info.engine` | `make test-axes` (`dfa`, `vm`) | value; later-wins on the CLI; the one CLI-wins exception to D93. **[r1 OS-M2] The exception is SPELLING-dependent**: it holds for the typed `engine vm` line (D1, reported), but a config's raw `pcrec --engine=vm` beats a CLI `--engine=dfa` SILENTLY (D3) |
| ordinal value axes | a rung or a parameter | `--unroll=K`, `--vm-entry-shape=N` | `pcrec <raw>` | `unroll_k`, `vm_entry_shape` | `RX_UNROLL_K_WHY`, `RX_VM_ENTRY_SHAPE` | `--vm-entry-shape` rungs (tiered, `AXES_FULL=1`) | value; later-wins. **[r1 OS-M2] Across sources: file-wins, SILENT** (H1) |
| the dial | a GROUP of axes from a pinned table | `--tune=N` / alias | `tune <pos>` | `tune` | `RX_TUNE` (unconditional; no `rx_info` mirror by design) | four `--tune` jobs + DIAL-S3 refusal-set check | **a set family**: five exclusive pinned bundles; deny cells OR'd, value cells read at their site (`src/core/compile.c:806`, `src/core/tune.c`). **[r1 OS-M2/OS-n13] Across sources**: a typed `tune` line wins, REPORTED (E1); a raw `pcrec --tune=` wins SILENTLY (E2); a config carrying both resolves typed-over-raw and its report names the config's raw value as "CLI --tune=…" (E3, a misattribution) |
| encoding | the subject's character model | `-e`/`--encoding` | `encoding` | `encoding` | `rx_info.encoding` | per-encoding corpora | value; **IMPLIES** modules `unicode-props`+`ucp` under `utf8` (an enabling implication; the stamp keeps the REQUESTED features). **[r1 OS-M2] Across sources: file-wins, SILENT**, by either spelling (G1, G2); block over config (G4) |
| module gate | which constructs compile | `--features LIST` | `features` (UNION with configs unless `features only`) | `features` (spec string; NULL = no request) | `PCREC_FEATURE_SET`, `PCREC_FEATURE_MODULES` | not an axis (refusals change by design) | **a set mechanism**: `std1` is a FROZEN named set, `all` a DERIVED one, `none` the empty one. **[r1 OS-M2] Across sources it is ONE WHOLE-LIST axis, file-wins, SILENT**: a CLI `--features lookaround` is dropped under a file `features atomic-groups` (C5, C6). Within the file, config and block UNION (C8). `--features` on a `pcrec` line is refused (C3) |
| findings | which subject statistics speed reads | `--analysis NAME` | `analysis <name>` | `analysis` | `RX_FINDINGS` (`kind=source:digest`), `rx_info.findings` | not an identity axis (speed only) | **a bundle**, composed INSIDE itself by `include` (D123); config later-wins; CLI fill-only, REPORTED when both name one (F1, F2) |
| resource bounds | budgets, capacities, caps | `--step-budget=`, `--work-budget=`, `--backtrack-frames=`, `--max-emit-*`, `--warn-emit-bytes=` | `budget` | the budget/cap fields | `RX_FAST_FRAMES` etc. | `limits.md`'s own checks | value; raise-only for the caps. **[r1 OS-M2] Across sources: file-wins, SILENT**, by either spelling (H3, H4) |
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
  **[r1 OS-n12] The code locations, corrected.** `TUNE_TABLE` is at
  `src/core/tune.c:61`. Its bar cells are integer PERCENT (95, 85), and
  the default bar is the constant beside `size_term_choose` in
  `src/core/compile.c` (~:530), read through `pcrec_tune_size_term_bar` at
  `compile.c:955`. λ is not a single read of the position. clskit's
  first-match table carries a per-row POSITION MASK column (`TPOS`,
  `src/gen/clskit.c:524-526`), tested at `:697` and `:781`. The deny cell
  has a second reader: the K59 drop ladder's `FIT_DROP_PREMUL` rung
  (`compile.c:1406-1425`) ORs the same `PCREC_NO_PREMUL_TABLE` bit, and it
  must keep reading the BIT, not a set cell.
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
  declared at v4, forced, needs isa ≥ v4", §2.7 row 8, designed and not
  built), by `test-axes` (run only the members at or below the box,
  §3.5a), and by `[ART-MGR]`'s catalog
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
- **[r1 OS-m6] Family axes are ONE ordered tier on the command line.**
  `--tune=`, `--isa=` and `--set=` naming a member of the same family all
  assign that family's axis, so they are later-wins among THEMSELVES, in
  argv order, and within one `--set=` list in list order:
  `--set=min-size,speed` is `speed` and `--set=speed --tune=min-size` is
  `min-size`. The "explicit beats a set regardless of order" rule (§2.5)
  covers NON-family axes only. A family axis has no set tier above or
  below its own spellings: every spelling of it IS an explicit
  assignment of it.
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
X" and a list denying row X is a conflict on X alone. **[r1 OS-M2] This
per-element reading is the JOIN's, among PEERS of one source. It is not
the cross-source rule.** Across sources, `--features` is one whole-list
axis today and the file's list replaces the CLI's silently (§2.5a C5/C6).
The per-element reading stays out of the cross-source tier. Moving
`--features` there would make a pattern refused today compile, and that
is ruling R5, recommended against.

**Numeric axes are equal-or-conflict.** Two sets setting the entry-chain
term to 8,192 and 4,096 conflict. Neither max nor min is taken, for the
same reason the ISA order is not used to merge.

**[r1 S9] The conflict path is BUILT only when it has a witness.** Today
no two sets in different families assign one axis. The dial's members
only deny, no other family exists, and the first vector and ISA members
assign disjoint axes (§4.2, §4.3). A join with no possible conflict is a
plain union. So the first build ships the union, plus a BUILD-TIME check
over the set table: if any two sets in different families assign one
axis DIFFERENT values, pcrec's build fails, naming the pair and saying the
conflict path now has its first witness. Sets that agree on a shared axis
(`readable` and `trace` on `comments`, §4.4) join silently and do not
trip it. That failure is §6.1's trigger 2. The runtime
refusal, its diagnostic and its sabotage row land with the change that
creates the disagreement, which also supplies their witness. There is no
UNREACHED refusal code in the meantime, and no test-only fixture set.

### 2.4a [r1 OS-M1] A deny/force pair is ONE three-valued axis

`src/core/axes.def` has one row per optimization axis, and a row with a
force twin is still ONE row. Revision 1 modelled `-fprefilter` and
`-fno-prefilter` as two booleans under a constraint row. The revision
models them as one axis `prefilter` with domain {default, deny, force}.
Four consequences follow.

1. **Self-contradiction refuses uniformly, at every tier.** A source, or a
   union of sources, that assigns one three-valued axis both `deny` and
   `force` is refused, naming the axis and where each value came from.
   This is today's behaviour, measured within one source and across two
   (§2.5a A1, A2, A5, A9). The model states it once, not as three
   constraint rows. The comments axis is the one grandfathered exception
   (deny wins, A6/A7/A10; §2.7 row 5, Q7).
2. **A three-valued axis composes across sources by UNION, then the
   refusal.** The file does NOT win on an `-f` axis today. A CLI
   `-fprefilter` is not discarded by a file's `-fno-prefilter`; the
   compile is refused. The model keeps that, so §2.5's file-wins row is
   not applied to three-valued axes.
3. **A set's cell on such an axis is a value, not a bit.** `min-size`
   assigns `premul-table := deny`. A future `-fpremul-table` (force) on
   the same command line beats it (explicit over set, within one source).
   Across sources it is UNION-then-refuse, by item 2: a file's `tune
   min-size` together with a CLI `-fpremul-table` would be REFUSED, where
   revision 1 said "the file wins, reported". No force twin exists for any
   dial cell today, so no shipped invocation changes. The rule is R1.
4. **Deny-only axes are three-valued with an unspelled `force`.** That is
   why §2.4's remedy message offers only the spellings that exist.

### 2.5 Precedence: explicit over set, per source; each kind's own rule across sources

Composition (⊔) combines PEERS. Precedence combines TIERS, through a
right-biased override `S ◁ E` (E's value where E assigns one, S's
elsewhere).

**Within one source, two tiers:**

```
resolved(source) = ( ⊔ of the sets that source names ) ◁ explicit(source)
```

- **Explicit beats a set, regardless of order, on a NON-family axis.**
  This is Frank's 2026-09-16 dial ruling ("explicit per-switch flags beat
  the dial"), generalized from one family to all of them. `--set=min-size
  -fpremul-table` and `-fpremul-table --set=min-size` mean the same thing.
  That is a deliberate departure from gcc, where `-ffast-math
  -fmath-errno` and `-fmath-errno -ffast-math` differ. Position-dependence
  is a precedence list in disguise, and D123 ruled against having two
  composition mechanisms. **[r1 OS-m6]** A FAMILY axis is different: every
  spelling of it (`--tune=`, `--isa=`, `--set=` naming a member) is an
  explicit assignment of it, and they are later-wins among themselves in
  argv order (§2.3).
- **On an ORDERED source, a repeated explicit axis is later-wins**, which
  is what every value option does on pcrec's command line today (§2.5a
  E4). On an UNORDERED source (the API struct), two fields that assign one
  axis different values are REFUSED, because there is no order to break
  the tie (§3.3: `tune = speed` with `sets = "min-size"`).
- **[r1 OS-M1] A three-valued `-f` axis assigned both `deny` and `force`
  is refused** (§2.4a). It is one axis assigned two values, refused
  because both were asked for, not later-wins. Comments is the
  grandfathered exception (§2.7 row 5).

### 2.5a [r1 OS-M1/OS-M2] Today's cross-source composition, MEASURED per axis kind

Revision 1 said "D93 per axis, unchanged: the file wins". The panel
measured that this is false for raw bits and for `features`. This
revision re-measured every axis KIND on `build/pcrec` (main `9fd125cb`,
`abi` 60). Each cell is a scratch `.rxt` with a `config` and a `target`,
compiled with CLI flags, and its stamps and stderr read. The 42 cells,
their script and transcript are `option_sets_measurements/`
(`cases.sh`, `out/cross_source.txt`). "Within the file" is config
against block.

| kind | spelling in the file | across sources (file vs CLI) | within the file | reported on stderr? | cells |
|---|---|---|---|---|---|
| three-valued `-f` axis (deny/force pair) | raw `pcrec -fX` / `-fno-X` | **UNION, then refuse** if both values are present, in either direction. Distinct axes all apply | raw lines accumulate under the same rule | the refusal names the pair | A1, A2, A3, A4, A5, A9 |
| the comments pair | raw `pcrec -fcomments` / `-fno-comments` | UNION, then **deny wins**, in either direction | same | no | A6, A7, A8, A10 |
| `flags` letters (`i`, `u`) and the raw `-i` / `--ucp` / `--no-captures` | typed `flags` or raw | **UNION** with the CLI's bits | a typed config `flags` is REPLACED whole by the block's; a raw `pcrec -i` UNIONS with the block's | no | B1, B2, B3, B4, B7, B8 |
| `features` | typed only (`--features` on a `pcrec` line is refused, C3) | **WHOLE LIST, file wins**: the CLI's list is dropped | config ∪ block | **no: silent** | C1, C2, C5, C6, C8 |
| `engine` | typed `engine vm` | CLI wins if it typed a non-`auto` engine (the D93 exception) | — | yes | D1, D2 |
| `engine` | raw `pcrec --engine=vm` | **file wins** | — | **no: silent** | D3 |
| `tune` | typed `tune <pos>` | file wins | typed beats raw | yes, **but a config's raw `--tune=` value is named "CLI --tune=…"** | E1, E3 |
| `tune` | raw `pcrec --tune=` | file wins | — | **no: silent** | E2 |
| `analysis` | typed `analysis` | file if it names one, else CLI (fill-only) | — | yes | F1, F2 |
| `encoding` | typed or raw | file wins | block beats config | **no: silent** | G1, G2, G4 |
| value options and budgets | raw `--unroll=`, `--step-budget=`; typed `budget steps=` | file wins | — | **no: silent** | H1, H3, H4 (H6 the control) |
| any value option, CLI only | — | later-wins in argv order | — | — | E4 |

There are six rules, not one. Union, then the pair rule, holds for `-f`
axes. Union holds for flag letters. Whole-list file-wins holds for
`features`. The typed `engine` line has the CLI exception. `analysis` is
fill-only. Silent file-wins holds for everything else.

**Three findings for the manager, outside this note's model** (each is a
fact about today's tree, true whether or not sets are built):

1. **`cli.md` §1.1 misstates two kinds.** It says `flags` is
   more-specific-wins against the config and file-wins against the
   command line ("every other axis … (`flags`, `encoding`, `budget`,
   `tune`, `analysis`) still follows the file-wins rule"). Against the
   command line `flags` UNIONS (B1-B4), and so do raw `-f` bits, which
   then refuse if they contradict (A1/A2). This needs a D80 sentence
   correction whenever `cli.md` is next touched.
2. **The `--engine` exception and the `tune` report depend on the
   SPELLING.** A config's raw `pcrec --engine=vm` beats a CLI
   `--engine=dfa` silently (D3), and the typed `engine vm` line does not
   (D1). A raw `--tune=` wins silently (E2), and the typed line reports
   (E1). D93 and its addendum are stated per AXIS, so the spelling should
   not decide. Ruling R2 makes them agree.
3. **The `tune` report misattributes.** With a config carrying both
   `pcrec --tune=min-size` and `tune speed` and NO CLI flag at all, pcrec
   prints "CLI --tune=min-size and this file's `tune speed` disagree"
   (E3). The raw config line is reported as the command line. Per-axis
   provenance (step 6 below) fixes this by construction.

**What the model keeps, and what it would change.** It keeps every row
above as a kind's rule, with two exceptions, and it adds reports. Every
change is a ruling for Frank (§5.4):

- **R1, set cells on a three-valued axis join the union-then-refuse
  rule.** A file set's `deny` with a CLI explicit `force` is refused, not
  file-wins (§2.4a item 3). No shipped invocation changes, because no
  dial cell has a force twin.
- **R2, one axis, one rule, whatever the spelling.** A raw `pcrec` line's
  `--engine=`/`--tune=`/`-e`/budget values are the SAME axes as the typed
  rows. D3 then flips: the CLI's explicit `--engine=dfa` wins, reported,
  as D1 already does. E2 gains the report E1 already prints. This is the
  one CHANGE OF OUTCOME in the list.
- **R3, a cross-source disagreement involving a set is file-wins and
  REPORTED on a value axis**, D93's shape, not a refusal. On a
  three-valued axis it is refused (R1).
- **R4, the report generalizes.** Every axis where the CLI explicitly
  assigned a value, the file's value differs, and the file wins gets one
  non-fatal stderr line naming both sources and values: `encoding`,
  budgets, value options, the raw spellings, and a dropped CLI
  `--features` list. Stderr only. No artifact byte moves. This also
  answers S7: a CLI flag lost to a file set no longer leaves no trace.
- **R5, `features` stays a whole-list axis across sources.** The
  per-element join is a peer rule within one source (§2.4). Applying it
  across sources would make C6's refused pattern compile. Recommend: keep
  the rule, and let R4 report the drop.

Flag letters need no exception. A letter is a boolean axis that every
source can assign only `on`, because there is no spelling for "not
caseless". So "file-wins where the file assigns, else the CLI" gives
exactly the measured union. Within the file, the typed config line's
whole-value replacement by the block's (B8) is the config contract's own
more-specific-wins rule (§2.6), unchanged.

**Across sources, the model's rule**, as a first-match table over each
axis `a`. It reproduces §2.5a row for row, plus R1-R5:

| # | predicate on axis `a` | `a`'s value comes from | reported? |
|---|---|---|---|
| 1 | `a` is a three-valued `-f` axis | the UNION of every source's resolved value. Both `deny` and `force` present: REFUSE, naming both sources. For comments, `deny` | the refusal |
| 2 | `a` is `engine` and the CLI assigned it explicitly, not `auto`, by any spelling (R2) | the CLI | yes, if the file disagrees |
| 3 | `a` is `analysis` | the file if it names one, else the CLI (fill-only) | yes, if both name one |
| 4 | `a` is `features` | the file's list if the file names one, else the CLI's (R5) | yes, if the CLI named one (R4) |
| 5 | the target's resolved file assignment covers `a`, explicitly OR through a set the file names | the file | yes, if the CLI assigned `a` explicitly or through a set and the values differ (R3, R4) |
| 6 | the CLI's resolved assignment covers `a` | the CLI | — |
| 7 | otherwise | the default | — |

Row 5's "through a set the file names" is the one new reading. **A set
named in a file makes the file speak about every axis in that set**,
because the file's author chose the set and everything in it. A CLI
`-fno-tiered-entry` survives a file's `tune min-size`, because `min-size`
does not assign `tiered-entry` (cell T1: both apply). **[r1 OS-M1]** A
future CLI `-fpremul-table` against that file line is three-valued, so
row 1 decides it and it is REFUSED (R1). Revision 1 said "would not
survive it, and would be reported", which was row 5's answer applied to
an axis row 5 does not own.

**The resolution order, start to finish.** This is a fold, not a
selection, so it is written as numbered steps rather than as a table. The
two DECISIONS in it (who writes an axis, and the constraint verdicts) are
tables.

1. Per source, resolve each FAMILY axis from its spellings, later-wins on
   an ordered source (§2.3).
2. Across sources, resolve each family axis by the table above (row 5 or
   6: file-wins, reported).
3. Expand each in-force member into its bundle, tagged with the source
   that selected it. **[r1 OS-m7]** A bundle may not assign a family axis
   (§2.6), so this step never feeds back into step 1.
4. Per source, join that source's bundles. **[r1 S9]** Until §6.1 trigger 2
   fires, the build-time check guarantees the join is a plain union.
5. Per source, overlay that source's explicit assignments (◁).
6. Across sources, resolve each ordinary axis by the table above. Record
   each axis's PROVENANCE (default / CLI set / CLI explicit / file set /
   file explicit).
7. **[r1 OS-M3]** Apply the constraint table (§2.7). Every row whose
   predicate holds applies, REFUSE rows first. Any REFUSE stops the
   compile.
8. Complete every unassigned axis with its default.

(Revision 1's step 9, "stamp", is gone with the stamp, §3.4.)

Step 6's provenance record IS the general mechanism `opt_dial_design.md`
§1.3 recommended and deferred: "explicit-set PROVENANCE for every
D93-composed axis … deferred to its own measured trigger (D77): the
trigger is the THIRD axis that needs the distinction". **[r1 S1/OS-M2]**
Its consumers are now named without the dropped stamp tail. The reports
of rows 2-5 need to know which source and tier wrote an axis, for every
kind R4 covers, and so does the unordered-source refusal of §3.3. Getting
provenance right is also what fixes finding 3's misattribution. So this
design builds provenance as the general form, and adds no per-family bit
(§5 Q6).

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
hypothetical `tiny` = `tune := min-size` + `vector := scalar`) is
**[r1 OS-m7] FORBIDDEN, by a check when pcrec is built.** Revision 1
admitted it with "family axes resolve first", but that order is circular.
A meta-set's family selection is only known after its bundle is
expanded (step 3), and step 3 runs after the family axes are resolved
(steps 1-2). The two ways out are a fixpoint over steps 1-3, or the
prohibition. A fixpoint is machinery with no consumer (D77), so the
static check rejects any bundle that assigns a family axis. When a
consumer names a meta-set, the fixpoint is designed then, with that
consumer's case as its witness (§5 Q11).

### 2.7 Constraints and implications: one table, every row applies

Some relations are not compositions. They are facts about the RESULT: two
values that cannot coexist, or a value that is meaningless without another.
They are rows of one table, applied once to the resolved assignment (§2.5
step 7). A REFUSE row names itself in its diagnostic. Rows are data and
listable.

**[r1 OS-M3] It is NOT a first-match table, because rows co-fire today.**
Cell M3 (`-futf-check -fstartpos-guard=align`, encoding `byte`) applies
TWO rows on one compile: `RX_UTF_CHECK "inert"` and `RX_STARTPOS_GUARD
"permissive"`, the byte encoding's only value. A first-match walk would
apply one and silently drop the other. The rule is:

1. **Every row whose predicate holds applies.**
2. **REFUSE rows are evaluated first.** If any holds, the compile stops.
   The diagnostic names the first such row in table order, so the message
   is deterministic, and no other verdict is applied.
3. **First-match holds only among rows that share a PARTY (an axis)**,
   which is the case revision 1's order argument was really about. Row 4
   (`-futf-check=extent`, REFUSE) and row 9 (`-futf-check` under `byte`,
   INERT) share `utf-check`. Rule 2 already puts the refusal first, which
   is today's measured answer (M3b: refused as reserved under the default
   `byte` encoding). Among non-REFUSE rows, no two shipped or designed
   rows share a party with overlapping predicates today (rows 9 and 11
   have disjoint encodings). A future pair that did would be ordered
   within its party, and the table check rejects two such rows that are
   unordered.

Four verdicts exist:

- **REFUSE**: the compile stops, naming the row's parties.
- **INERT**: the axis is kept and its own stamp says it had no effect. The
  stamp is in the axis's own vocabulary. `RX_UTF_CHECK "inert"` says it
  in words, and `-fstartpos-guard=align` under `byte` stamps
  `"permissive"`, the only value that axis has there (M3).
- **DERIVE** **[r1 OS-m10]**: a documented, pre-existing implication that
  ENABLES or DISABLES something on another axis, without changing any
  accepted pattern's answer. Row 11 enables, and row 12 disables
  (`engine = vm` drops the DFA prefilter). Revision 1 said "enables" only,
  which row 12 contradicted.
- **GRANDFATHERED-ASSIGN** **[r1 OS-m10]**: the comments pair's deny-wins
  (row 5). It resolves a self-contradiction by choosing a value, which no
  other verdict does. It is a fourth verdict with exactly one row, kept
  because it is shipped and documented (Q7). No new row may use it.

**A new rule may refuse or mark inert. It may not silently assign.**
"SIMD requires an ISA level" is therefore NOT an implication: a vector row
that needs a declared level simply does not apply below it. That is the
`SCAN_ROWS` row's own PREDICATE (integration.md §2.1, `BASE`/`DECLARED`).
Only a FORCE that cannot be honoured would need a row here (row 8).

| # | row | predicate | verdict | status |
|---|---|---|---|---|
| 1-3 | `both-values` **[r1 OS-M1]** | any three-valued axis assigned `deny` and `force` (today `prefilter`, `prefilter-collapse`, `startpos-guard`; the union over sources, §2.4a) | REFUSE | shipped (A1, A2, A5, A9). Revision 1's three pair rows are ONE row over the axis kind |
| 4 | `utf-check-extent` | `-futf-check=extent` | REFUSE (reserved) | shipped (M3b) |
| 5 | `comments-pair` | `comments` assigned `deny` and `force` | GRANDFATHERED-ASSIGN: deny | shipped; the one silent resolution (A6, A7, A10; §5 Q7) |
| 6 | `isa-route-orphan` | `isa-route = macro` ∧ `isa = portable` | REFUSE | designed (isa_selection.md §1.2.3) |
| 7 | `isa-marker-orphan` | `isa-marker` ∧ `isa` not on the x86 chain | REFUSE | designed (isa_selection.md Q6) |
| 8 | `forced-row-below-level` **[r1 OS-m11]** | a row declared at level L is FORCED ∧ `isa` is NOT ≥ L in the poset (below it, or incomparable) | REFUSE | **NOT in the first build** (below) |
| 9 | `utf-check-byte` | `-futf-check` ∧ `encoding = byte` | INERT | shipped (M3) |
| 10 | `startpos-align-byte` | `-fstartpos-guard=align` ∧ `encoding = byte` | INERT | shipped (M3) |
| 11 | `utf8-enables-modules` | `encoding = utf8` | DERIVE: `unicode-props`, `ucp` enabled (the stamp keeps the REQUESTED set) | shipped |
| 12 | `vm-drops-dfa-prefilter` | `engine = vm` | DERIVE: no DFA prefilter (R21 E-6) | shipped |

**[r1 OS-m11] Row 8 is designed and NOT built.** Its predicate needs a
FORCE on a vector row, and this mechanism never invents a force
(§2.4). `[MEMFN]` R4 proposes vector rows with DENY spellings only
(`-fno-vec-scan`, …, integration.md Q15). So no invocation can satisfy
the predicate, and a row with an empty predicate population would ship a
sabotage row nobody can reach. The row lands in the change that adds a
vector FORCE twin, which also supplies its witness. Its wording is "isa
is NOT ≥ L", not "isa < L": in a poset an incomparable level (`armv8-a`
against an x86 row) is neither below nor at-or-above, and it must refuse.

Rows 1-5 and 9-12 already exist, scattered (the pair refusals are
diagnosed at compile and carry a pattern offset). Collecting them is
implement-then-replace and byte-identical: the same diagnostics, the same
inert stamps. That is the D46 controllability half applied to the option
layer itself. A row added later is one table row, not a new `if`.

### 2.7a [r1 OS-m8] Dominance: a cell can be inert without a row

A cell can also be made inert by ANOTHER AXIS's value, with no constraint
row involved. Measured: `--tune=min-size -fno-size-term` against
`--tune=min-size` on `x(ab|cd)+y` differs in exactly two places,
`RX_UNROLL_K_WHY` (`"denied"` against `"default"`) and `rx_info.flags`
(bit 18). No code byte moves. `min-size`'s two ladder cells
(`size-term-bar`, `size-term-threshold`) are read only when the size term
runs, and the deny turns the size term off. The deny DOMINATES them.

Revision 1's "the stamp's tail shows every overridden cell" missed this
case, because provenance records who WROTE an axis, not whether its value
MATTERED. The tail is gone (§3.4), but two readers still need the
relation:

- `test-axes`' vacuity print (§3.5) must not count a dominated cell as
  exercised;
- `--list-sets` notes a member cell's dominators, so a reader of the set
  table can see it.

So the registry gains a `dominates` column: (axis, value) → the axes
whose values are not read under it. Today it has one row, `size-term :=
deny` → {`size-term-bar`, `size-term-threshold`}. It is data, read by
those two places, and it never changes a value. The note claims nothing
broader. A dominance the column does not list is a documentation gap, not
a miscompile, because nothing the column says changes code.

### 2.8 A set's class, and what the class decides

Every axis already has a class in the tree's own vocabulary (`tuning.md`
§1, §4; D125):

| class | members are… |
|---|---|
| identity | answer-preserving, refusal-preserving (with the give-up carve-out below) |
| engine-selecting | answer-preserving but may move the engine or refuse under `--engine=dfa` (`-fno-splice-calls`, `-fno-atomic-discharge`, `-fno-ctx-node`) |
| policy | changes WHETHER an artifact is produced, never its answers (`--fast-or-fail`, the caps) |
| contract | changes which ANSWER a call gives, on purpose (`-futf-check`, `-fstartpos-guard=align`) |
| semantic | changes what the pattern MEANS (`-i`, `--ucp`, `--no-captures`, `encoding`) |
| instrument | changes what the artifact DOES besides matching (`--trace`) or CONTAINS (`-fcomments`, object-identical) |

**[r1 OS-m9] A set's class is the SET of its members' classes, and each
decision reads it by an explicit rule.** Revision 1 called it "the
WEAKEST, in this order" and listed the classes as a chain. They are not a
chain. Contract and instrument are incomparable, and revision 1's own
example (`trace`, instrument, assigning `comments`, instrument) never
tested the order. The rules, as one first-match table per decision:

| decision | first-match rows over the set's class set C |
|---|---|
| may be a `tune` member | (a) C = {identity} → yes. (b) otherwise → no |
| `test-axes` comparison | (a) C = {identity} → identity; LOST, GAINED or MISMATCH fails. (b) C ⊆ {identity, engine-selecting} → identity, with LOST printed where documented. (c) C ⊆ {identity, contract} → against the declared behaviour, the way the axes sweep treats a contract axis. (d) otherwise → not swept, and the run prints the reason |
| the H11 harness control (§3.2) | (a) contract ∈ C → compare against the declared behaviour. (b) otherwise → answer identity with the block's own compile |

**The give-up carve-out.** "Identity" means match results and captures
are identical. It does not mean the give-up surface is: the dial's
ladder cells change the unroll K, and `artifact_size_term.md` §2.0 (3)
measured that K moves the minimum step budget and the minimum backtrack
frames. A `tune` member is identity-class on that reading, which is the
reading `[ART-SIZE]`'s own K sweep uses when it excludes `budget`/`gu`
cells. The set sweep inherits the exclusion and says so.

**The class check reads a hand tag, so it is a typo guard, not the
control.** The static check compares member axes' class tags with the
family's required class, and both are hand-entered. It catches a cell
proposed in the wrong family. It cannot catch a tag that is wrong. **The
real control is DIAL-S3**: `test-axes`' keyed refusal-set comparison per
`tune` position, which MEASURES refusal preservation over the corpus,
together with the identity sweep that measures answers. It generalizes to
every family whose required class is identity (§3.5).

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
  unlike the `-f` family (D47.3) it appears in `--help`. **[r1 OS-m6]**
  The names are JOINED only across families. Two members of one family in
  one list or across repeats are later-wins in argv order, together with
  that family's sugar flag (§2.3).
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
- **[r1 S7] `--set=` is REFUSED on a config's `pcrec` line.** A config
  names sets with its own `set` line (§3.2), which is how `--features`
  (cell C3) and `--analysis` are treated on that line today. One spelling
  per surface means the raw line and the typed line cannot disagree about
  which sets a file named, which is the spelling dependence §2.5a finding 2
  measured for `engine` and `tune`.

### 3.2 `.rxt`

- **A config body gains `set <name>{, <name>}`.** It is one schema row
  (`rxt_schema.def`), config-scoped like `tune`, and the names are
  resolved and refused-if-unknown when the file is read. `--list-source`
  carries it AS WRITTEN (its `tune` column's rule). A block may not name
  sets, for the reason a block may not name `tune`: a set is a build
  configuration, and the block is the definition.
- **`tune <pos>` stays** as the `tune` family's sugar.
- **Inside one target**, every set named by any of its configs is a peer
  of the FILE source (§2.6). Sets are joined. **[r1 S9]** Until §6.1
  trigger 2 there is nothing to refuse (§2.4). The configs' typed lines
  keep later-wins, and the block's own directives keep more-specific-wins,
  both at the explicit tier. **[r1 OS-M2]** That includes `flags`' measured
  quirk (a typed config line replaced whole by the block's, B8), which is
  the config contract's own rule and unchanged.
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
- **[r1 S7] Its refusals travel the channel `features` uses.** An unknown
  set name, a family-sugar disagreement on this unordered source, and a
  both-values refusal (§2.4a) all fail `pcrec_compile` through
  `pcrec_error`, with the wording the CLI's stderr line quotes. That is
  exactly how `features`' unknown-name refusal is surfaced today
  (`match_api.md` §8.2), with `input = PCREC_ERR_INPUT_PATTERN` and `pos =
  0`. No new `pcrec_err_input` tag is proposed. An OPTIONS input tag is
  the general fix for every option refusal, `features` included, and it
  is a separate row if a caller ever needs to tell the two apart (D77).
  The §8.2 hunk states this in the build's change (§5.3).
- The resolved per-axis PROVENANCE (§2.5 step 6) is internal. Nothing in
  the API exposes it until a consumer asks (D77).

### 3.4 The stamp, and `rx_info`

**[r1 S3] Recommendation: build NO set stamp until a consumer asks.**
Revision 1 proposed `<PREFIX>_SETS` on every artifact of both engines.
The panel found four defects in that proposal (S1-S4), and each is
answered below. One fact decides it: no consumer exists. The bench has
not answered §3.5's question (i), whether it keys a testee on the
invocation or on the stamps. `[ART-MGR]`'s catalog needs the `isa`
OUTCOME fields, not a set name. A set changes nothing at run time. The
outcome stamps (D46: `RX_DFA_TABLE`, `RX_VM_PREFILTER`, …) already
record what every set DID. So D77 applies: the first build emits no set
stamp, moves no artifact byte, and carries no `abi` event of its own
(§5 Q5). `RX_TUNE` stays as shipped.

**If a consumer asks, this is the stamp to build.** Each property answers
one finding.

- **[r1 S3] Emitted ONLY when a set is NAMED**, by any source, from a
  family that has no stamp of its own. An artifact naming no set has no
  line, so every existing artifact stays byte-identical, and the
  no-request identity gate's (B) pin does not move. The stamp's birth is
  still an `abi` event by D76's rule, because it adds scaffolding
  vocabulary, but its re-pin set is only the readers of the number.
- **[r1 S2] Families that own a stamp are excluded.** `tune` has
  `RX_TUNE`, printed even at `balanced`, and the bench buckets on it.
  `isa` will have `<PREFIX>_ISA_LEVEL` (isa_selection.md §1.2.3).
  Printing either again would be two stamps for one fact, with different
  default rules.
- **[r1 S1] The VALUE is a function of the RESOLVED configuration, not of
  the spelling.** It lists, in registry order, every member of a
  stampless family whose bundle the final resolved assignment SATISFIES IN
  FULL, whether or not that member was named. A named member that an
  explicit flag partly overrode is not printed. If nothing qualifies, there
  is no line. Revision 1's `;axis` override tail is DROPPED: it recorded
  provenance, which is a fact about the spelling. S1's witness pair,
  `--set=trace -fno-comments` against `--trace -fno-comments`, resolves
  to one configuration that does not satisfy `trace`'s bundle, so neither
  artifact has a line, and they are byte-identical. What remains
  spelling-dependent is the line's PRESENCE, which records that a set was
  named. `--set=readable` and `-fcomments` resolve identically, and only
  the first has the line, with the value `readable`. That asymmetry is the
  price of S3's no-bytes-without-a-request rule, and it is stated here
  rather than hidden.
- **[r1 S6] The vocabulary is MEMBER names only.** With the tail gone,
  no axis registry name reaches emitted text. Renaming a member is an
  `abi` event, and for a pinned member it is also a ruled diff (D103).
  The CLOSED-token discipline of `RX_TUNE` holds per token.
- **[r1 S4] Size-neutral rendering.** The stamp's length depends on the
  request, and today's size-predicated selections read emitted text that
  includes the prologue. The emitted-size caps and the `[ART-SIZE]`
  ladder measure the whole `.c` plus `.h` (`emit_size_measure`,
  `src/core/compile.c` ~:2010), and the near-cap corpus artifact sits 75
  bytes under `PCREC_MAX_EMIT_BYTES` (`opt_dial_design.md` §6.2a). A
  20-byte set list could therefore move a cap verdict or a ladder rung.
  K79 fixed the same defect for the prefix (`docs/dev/known_issues.md`
  K79). The emitters write a fixed placeholder, and
  `pcrec_sb_render_prefix` spells the real value after every decision.
  The set stamp uses that mechanism: the emitter writes a fixed-length
  placeholder, and the post-decision render spells the value. Every size
  decision then sees one canonical length, whatever was named.
- **[r1 S4] Its check is `run_prefix_invariance.sh`'s shape.** For every
  listed member whose bundle has a spelling for every axis, compile the
  check's population twice: once with `--set=M`, once with M's bundle
  spelled as explicit flags. The two artifacts must be byte-identical
  except for the `<PREFIX>_SETS` line. Members with an unspelled axis are
  counted and printed as skipped, never silently dropped. The near-cap
  artifact (`tests/utf8/axis12_scripts.rxt:296`) is in the population as
  the control a purely synthetic family would not have.
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
  that consumer asks (§5 Q5). If the bench asks, a digest of the resolved
  assignment answers S1 completely, presence asymmetry included, and is
  the better stamp. That is the bench's question (iii).

### 3.5 How the checks treat a set

**[r1 S10/S11/S12] Every check below names its EXPECTATION SOURCE, and
none of them is the set table it checks.** Revision 1 derived the job list
from `--list-sets`, the derived-set check from the `vector` tag and gate 3
from a spec that cannot list a derived set's members. Each is fixed below
(`learnings.md` §3: a control that shares a source with its subject).

**`make test-axes`: a set is an axis.** The sweep already treats the
dial's four non-default positions as "a fifth kind of axis" on the same
RXTFLAGS/RXTDUMP mechanism (`tests/axes/run_axes.sh`, the header's
`[OPT-DIAL]` paragraph). The general form:

- **The job list** = every bit axis alone (today) ∪ every NON-DEFAULT
  member of every family ∪ every standalone set. The list is read from
  `--list-sets`, never hand-copied, which is the script's own rule.
  **[r1 S12] It is checked against an INDEPENDENT floor**: the spec's
  family table (`tuning.md` §6, written and ruled by hand, §5.3) states
  each family's member count. The runner prints both counts per family
  and fails if `--list-sets` yields fewer jobs than the spec names. A
  member deleted from the set table cannot silently delete its own job.
- **The class decides the comparison**, by §2.8's first-match table.
  DIAL-S3's keyed refusal-set comparison generalizes from `tune` to every
  family whose required class is identity, and it is the measured control
  §2.8 names. A member's dominated cells (§2.7a) are printed as not
  exercised.
- **Combinatorics: no products by default.** A set alone against the
  default is the unit, as a bit axis alone is. A PAIR job exists only as a
  row of a declared `pairs` list, each row naming its reason: two families
  whose members feed the SAME table's predicates. The first such pair is
  `vector` × `isa`, both read by `SCAN_ROWS` (integration.md §2.1).
  **[r1 S14] Its size.** The full product is 4 `vector` members × 8 `isa`
  members = 32 jobs, each one a full corpus run (20-30 minutes on darwin
  for the `.rxt` section alone, BOILERPLATE), so 11 to 16 hours per box,
  and no box can run every `isa` member (§3.5a). So the pairs rows are
  floored, not producted. Per box they are each non-default `vector`
  member × {`portable`, the box's TOP runnable declared level}: 3 × 2 = 6
  jobs, about 2 to 3 hours on darwin. Those are the two `SCAN_ROWS`
  predicate regimes, `BASE` and `DECLARED`. The run prints the product
  size it did NOT run. The floor (6 per box) is computed from the spec's
  family table and the box's level, never from `--list-sets`.
- **Vacuous members still run** (S219's precedent, already followed for
  `max-speed`). `simd`/`no-simd`/`scalar` are vacuous until vector rows
  exist. The run prints that their resolved assignment is empty, rather
  than skipping them. A check that skips its vacuous members is the one
  that fails to fire the day they stop being vacuous.

**[r1 S10] The derived-set population is counted independently of the
tag.** `no-simd` is "every axis tagged `vector`", so "every axis tagged
`vector` is denied by `no-simd`" checks the tag against itself. A vector
row added WITHOUT the tag escapes both. The check counts the population
twice, from two sources that are not the tag:

1. **by NAME**: `axes.def` rows whose registry name matches `^vec-`
   (integration.md Q15's naming: `vec-scan`, `vec-skip`, `vec-run`),
   counted by plain-text scan, `[AXES-DENY-MASK]`'s gate shape;
2. **by EMIT SITE**: the distinct `PCREC_NO_VEC_*` deny bits read in the
   `SCAN_ROWS` emitters, counted by grep of `src/gen/`.

Both counts must equal the materialized `no-simd` bundle's size, and all
three are printed. An untagged vector row moves count 1 or 2 and fails.
`SAB_REACH_POP` floors on count 1 (≥ 2 at the build, §6.1 trigger 1).

**The identity gates.** Each is built with what it checks, and each has
an expectation side that does NOT share a source with the set table
(`learnings.md` §3):

1. **Re-expression identity** (built at §6.2, NOT at the first build,
   [r1 S16]): the dial moved onto the set table emits, at all five
   positions over the whole corpus, bytes identical to the shipped
   `TUNE_TABLE` build. `tests/codegen/run_tune_dial.sh` already reads its
   expectations from `tuning.md` §5.4, not from `src/core/tune.c`. It
   keeps doing so, and reads the set table only as the thing under test.
2. **No-request identity**: with no set named anywhere, every artifact is
   byte-identical to the pre-mechanism build. **[r1 S3]** With no stamp
   there is no exception line at all, and even with §3.4's conditional
   stamp there is none, because the line exists only when a set is named.
3. **[r1 S11] Listing against an independent source, split by kind.** A
   PINNED set's `--list-sets` rows are checked against the spec's set table
   (`tuning.md` §6), which states a pinned bundle in full, as §5.4 does for
   the dial today. A DERIVED set's spec entry states its PREDICATE, not
   its members, so the spec cannot be its expectation. Its rows are
   checked against the independent counts above.

**mech (sabotage).** Rows are numbered from main's highest S-id at the
build, not here. **[r1 S8] Each row states whether its witness is
reachable at the first build** (the `vector` trigger, §6.1). An
unreachable row is not omitted. It declares `SAB_EXPECT=UNREACHED` with
its `SAB_EXPECT_REASON` and a `SAB_REACH` probe, so that mech reports
`NOW REACHED` the day its witness appears (`tests/mech/CLAUDE.md`, the
reach mechanism). That is the runner check the panel asked for, and it
exists already.

| sabotage | detector | witness at the first build |
|---|---|---|
| a PINNED member's cell is dropped from its bundle | gate 3 (reads the spec) | **UNREACHED** for a `vector`-only build: every `vector` member is DERIVED. It is reached by the first pinned non-`tune` member (`isa`, or a standalone set). `SAB_REACH` = `--list-sets` shows a pinned row outside `tune` |
| the cross-family DISAGREEMENT check stops firing (§2.4) | the checker run over a fixture TABLE FILE holding one disagreement must fail. The fixture is an input to the checker, not a set in pcrec's vocabulary | reached (the fixture) |
| explicit loses to a set (the overlay's operands swapped) | a `tests/cli` case, `--set=simd -fno-vec-scan`, asserting that the scan-site outcome stamp shows the row denied | reached at trigger 1: `simd` pins `vec-scan`, and the explicit deny disagrees with it |
| family members conflict instead of replacing | `--tune=min-size --tune=speed` must still compile, `RX_TUNE "speed"` (cell E4, today's pinned behaviour); `--set=min-size,speed` likewise | reached today |
| family order is lost (`--set=` joins one family's members) **[r1 OS-m6]** | `--set=speed,min-size` must stamp `RX_TUNE "min-size"` | reached today |
| a derived set's predicate misses a new row | the S10 counts above | reached at trigger 1 (≥ 2 `vec-` rows) |
| a REFUSE row is evaluated after an INERT one **[r1 OS-M3]** | `-futf-check=extent` must still refuse as reserved under `byte` (cell M3b) | reached today |
| the table reverts to first-match **[r1 OS-M3]** | `-futf-check -fstartpos-guard=align` under `byte` must stamp BOTH `RX_UTF_CHECK "inert"` and `RX_STARTPOS_GUARD "permissive"` (cell M3) | reached today |
| a three-valued axis composes file-wins instead of union-then-refuse **[r1 OS-M1]** | the `.rxt` cell A1 (file `-fno-prefilter`, CLI `-fprefilter`) must still refuse | reached today |

Revision 1's "the stamp's override tail is omitted" row is withdrawn with
the tail. If §3.4's conditional stamp is ever built, its set-invariance
check is its detector and it brings its own row.

**[r1 S9] The witness note, replaced.** Revision 1 said the conflict row
"ships UNREACHED". The conflict PATH is no longer built ahead of its
witness (§2.4): the build-time disagreement check stands in for it, and
that check's own sabotage row is reached through a fixture table file.
The runtime refusal, its diagnostic and its sabotage row arrive with the
change that creates the first cross-family disagreement, and that change is
the witness. Revision 1's refusal to use a test-only SET stands: a set in
the vocabulary that exists only to be refused would ship forever. A
fixture table read only by the checker is not in the vocabulary.

### 3.5a [r1 S13] Who runs each ISA member

A declared-ISA artifact compiles on a box whose gcc targets its
architecture, and it RUNS only on a CPU at or above its level. No house
box covers every member. ubuntubudu is Zen 1 (AVX2, no AVX-512). The Mac
is an M1 (NEON, no SVE). CI runs no `test-axes` (`docs/testing.md` "CI").
The Mac's `gcc-16` targets aarch64 only, so no box cross-compiles the
other architecture's chain. So the sweep has two arms per box:

- **compile-only, every member of the box's own architecture's chain**:
  `gcc -march=<level> -c` on every artifact the population emits. It
  proves the target-attributed code is well-formed and the route-M
  `#error` floor fires where it should. It proves no answers.
- **runtime, every member at or below the box's level**, skipping the
  rest LOUDLY with a count, PC-3's absent-library shape.

| member | compile-only arm | runtime owner |
|---|---|---|
| `portable` | every box | every box |
| `x86-64-v1`, `-v2`, `-v3` | ubuntubudu | ubuntubudu |
| `x86-64-v4` | ubuntubudu | **UNOWNED**: no house box has AVX-512 |
| `armv8-a` | Mac | Mac |
| `armv8-a+sve`, `+sve2` | Mac (`-march=armv8-a+sve`/`+sve2`) | **UNOWNED**: the M1 has no SVE |

x86 under Rosetta 2 on the Mac (survey.md §1.2) stays a separate opt-in
correctness arm, and its own x86 level is a fact to measure, not to
assume. The two UNOWNED rows are ruling R6 (§5.4). The recommendation is
to ship those members compile-only-verified, with the runtime arm
skipping them loudly, and to file an emulator arm (Intel SDE for AVX-512,
`qemu-user` with SVE) as its own row, triggered when one of those members
becomes a requested testee. `[MEMFN]` R4g's own trigger is a measured
level gain ON ubuntubudu (integration.md §6), so `x86-64-v3` is the
likely first member, and it is owned.

**The bench.** `pcrec-bench/APPROACH.md` §2 item 4 already defines a
testee as "(engine, version, build/run configuration)" and anticipates
"later SIMD on/off" as a first-class axis. Its litrun subbench already
names deny testees (`-fno-lit-run`, `-fno-altcls-factor`). A set gives
such a testee a NAME the artifact itself carries:

- A testee is spelled `--set=no-simd`. **[r1 S3]** With no set stamp
  (§3.4), the bench labels it from its own invocation, which is how its
  deny testees (`-fno-lit-run`) are labelled today. `RX_TUNE` keeps
  working for the dial.
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
  (ii) **[r1 S1]** (withdrawn: the `;` tail is dropped; if a stamp is ever
  built, the question becomes whether an OPTIONAL `RX_SETS` line, present
  only on set-named artifacts, breaks its parser) (iii) does it want a
  configuration digest (§3.4) as testee identity? A yes to (i)-as-stamps
  or to (iii) is a consumer, and it fires §6.1 trigger 3 and §3.4's
  conditional design.

---

## 4. Worked examples

Axis names below are REGISTRY names (a hyphenated noun, the `-fno-` stem
where one exists). Values are the axis's own domain. "(pin)" marks an axis
assigned its default.

### 4.1 The dial: family `tune`, five pinned members

Re-expressing `tuning.md` §5.4 needs four UNSPELLED axes. Three already
exist as constants or position reads, and the fourth makes λ's direct
position read an axis:

| unspelled axis | domain | default | today it is… |
|---|---|---|---|
| `size-term-bar` | a ratio, stored as integer percent **[r1 OS-n12]** | 75 | a constant beside `size_term_choose` in `src/core/compile.c` (~:530), read through `pcrec_tune_size_term_bar` at `compile.c:955` |
| `size-term-threshold` | bytes | 120,000 | `limits.def`'s `PCREC_SIZE_TERM_THRESHOLD` (`BUILD_D`), overridden by `pcrec_tune_size_term_threshold` |
| `vm-entry-term` | bytes | 4,096 | the entry chain's size term, overridden by `pcrec_tune_vm_inline_chain_max` |
| `cls-matcher` | `size` / `balanced` / `max-speed` | `balanced` | **not an axis today**: `src/gen/clskit.c`'s first-match table carries a per-row POSITION MASK (`TPOS`, `:524-526`), tested at `:697` and `:781` **[r1 OS-n12]** |

The five members, read straight off `src/core/tune.c`'s `TUNE_TABLE` and
`tuning.md` §5.4:

| member | bundle |
|---|---|
| `min-size` (−2) | `size-term-bar := 95`, `size-term-threshold := 40,000`, `premul-table := deny`, `cls-matcher := size` |
| `size` (−1) | `size-term-bar := 85`, `size-term-threshold := 80,000`, `cls-matcher := size` |
| `balanced` (0, default) | ∅ |
| `speed` (+1) | `vm-entry-term := 8,192` |
| `max-speed` (+2) | `vm-entry-term := 8,192`, `cls-matcher := max-speed` |

- **The family's required class is identity and refusal-preserving.**
  Every axis in every bundle above is identity-class, with §2.8's give-up
  carve-out (the ladder cells move K, so they move the minimum budgets).
  **[r1 OS-m9]** The static check catches a cell proposed with a
  contract-class or engine-selecting TAG. DIAL-S3 is the control that
  catches a wrong tag, because it measures refusals instead of reading the
  tag.
- **Today's behaviour is preserved exactly.** The deny mask is OR'd today
  (`compile.c:806`). In the model, a member's `deny` joins an unassigned
  axis, and an explicit `-fno-tiered-entry` at `min-size` overlays an
  axis `min-size` does not assign (cell T1: both apply). **[r1 OS-M1]** A
  FUTURE `-fpremul-table` at `min-size` on the SAME command line would
  beat the cell (explicit over set, within one source). That is the ruled
  "explicit beats the dial, where a spelling exists". The same force on
  the command line against a FILE's `tune min-size` is three-valued
  union-then-refuse, so it is REFUSED (§2.4a, R1). Revision 1 said "the
  file wins and the stamp records it". No stamp is built (§3.4), and the
  outcome stamp `RX_DFA_TABLE` records what was done, as it does today.
- **[r1 S16] At the FIRST build, the dial does not move.** The set layer
  reads the `tune` family's bundles THROUGH `TUNE_TABLE`'s existing
  accessors (`pcrec_tune_deny_flags`, `pcrec_tune_size_term_bar`, …). That
  is one table with a second reader, not a second table. The set layer
  needs those bundles for two things only: the cross-family disagreement check
  (§2.4) and `--list-sets`. No emitted byte moves, and the
  general-mechanisms rule is kept, because the dial's cells are written in
  exactly one place.
- **The re-expression is its OWN step (§6.2), with its own trigger.** When
  it fires, the one code change it needs is that clskit reads
  `cls-matcher` instead of its per-row position mask. Each position maps to
  exactly the rule it selects today, so the change is byte-identical
  (identity gate 1, §3.5). The three value cells' readers already go
  through accessors, so only their source of truth moves, from
  `TUNE_TABLE` to the set table. `TUNE_TABLE` is then deleted, not kept
  beside it. The K59 drop rung (`compile.c:1406-1425`) keeps ORing the
  `PCREC_NO_PREMUL_TABLE` bit, because it reads the axis, not the member
  (§1.3).
- **D103 is unchanged**: the members are PINNED, a cell changes only by a
  ruled diff to `tuning.md` §5.4, and the rubric stays advice. The set
  table is where the ruled cells live in `src/`, exactly as `TUNE_TABLE`
  is today.
- **[r1 OS-n14] The D103 ritual gains one step.** A cell diff can CREATE a
  cross-family disagreement. integration.md Q16's case is the example: a
  `min-size` cell denying `vec-scan` disagrees with `simd`'s pin, so `--set=
  simd,min-size`, accepted the day before, would be refused the day after.
  So every ruled cell diff runs the disagreement check over the whole set table
  and lists, in the diff Frank rules on, every set pair that comes to
  DISAGREE on an axis and so becomes refused. Until §6.1 trigger 2 has built the
  runtime refusal, the disagreement check fails the build instead, and the
  diff cannot land without that trigger's change. Either way the new
  refusal is ruled, not discovered.

### 4.2 `simd` / `no-simd`: family `vector`, four members

D122 addendum 3 draws the hold's line at ARCHITECTURE-SPECIFICITY, not at
data parallelism ("SWAR is fine"). So SWAR is not "simd", and the family
has a member for each side of that line:

| member | kind | bundle |
|---|---|---|
| `auto` (default) | — | ∅: every vector row decides by its own predicate; the dial and other sets may deny |
| `simd` | derived | every axis tagged `vector` := allow (pin) |
| `no-simd` | derived | every axis tagged `vector` := deny. The SWAR row stays allowed |
| `scalar` | derived | `no-simd`'s bundle ∪ `swar-scan := deny`: one byte at a time, the D122-reference spelling |

At [MEMFN] R4's proposed granularity (integration.md Q15), the axes
tagged `vector` are `vec-scan`, `vec-skip` and `vec-run`. `swar-scan` is
tagged `swar`. The kit-internal rows behind `--memfn-deny=` need no tag:
every one of them sits under a `vec-*` row, so denying the family makes
them unreachable.

- **Why `simd` pins rather than being the default**: a caller who names
  `simd` is asking for the vector rows to stay. If a dial member later
  denies `vec-scan` (integration.md Q16 raises exactly that for un-declared
  builds, since the `#if` ladder costs bytes), then `--set=simd,min-size`
  is a CONFLICT and is refused by name. This is Frank's "they overlap"
  made concrete. **[r1 S9/OS-n14]** That cell diff is also the first
  cross-family disagreement, so it is §6.1 trigger 2: the runtime refusal is
  built in the same change, and its own refused pair is its witness. The
  D103 diff lists the newly refused pair (§4.1). `--set=min-size` alone (vector family at `auto`) lets the
  dial deny without complaint. Without the pin, `simd` would be a name for
  "nothing", and the caller's request would be silently overruled.
- **`no-simd` and `scalar` overlap and agree.** They are one family, so
  they never meet in a join: `--set=no-simd --set=scalar` is later-wins,
  `scalar`, and so is `--set=no-simd,scalar` (§2.3). **[r1 OS-m7]**
  Revision 1's example of a meta-set implying `scalar` is withdrawn,
  because meta-sets are forbidden (§2.6).
- **The interaction with ISA is not composition.** `SCAN_ROWS`' rows read
  both axes as predicate inputs (integration.md §2.1):

| `vector` | `isa` | what the scan sites get |
|---|---|---|
| `auto` / `simd` | `portable` | `BASE` rows: the `#if` ladder whose `#else` is pcrec's next scalar row (integration.md §2.5) |
| `auto` / `simd` | `x86-64-v3` | `DECLARED(v3)` rows: one spelling, no ladder, target-attributed matcher |
| `no-simd` | `x86-64-v3` | the scalar and SWAR rows only, in a target-attributed matcher (gcc may still vectorize on its own; pcrec emitted no vector row) |
| `scalar` | any | the byte-at-a-time rows only |

### 4.3 The ISA levels: family `isa`, a poset

| member | bundle | order |
|---|---|---|
| `portable` (default) | ∅: architecture-neutral C; route M if the consumer's `-march` raises the macros (isa_selection.md §1.2.2) | bottom |
| `x86-64-v1` | `isa := x86-64-v1`, `isa-route := attr` | x86 chain |
| `x86-64-v2` | `isa := x86-64-v2`, `isa-route := attr` | x86 chain (listed for completeness; isa_selection.md §1.2.1 believes it buys kernels nothing) |
| `x86-64-v3` | `isa := x86-64-v3`, `isa-route := attr` | x86 chain |
| `x86-64-v4` | `isa := x86-64-v4`, `isa-route := attr` | x86 chain, top |
| `armv8-a` | `isa := armv8-a`, `isa-route := attr` | Arm chain |
| `armv8-a+sve` | `isa := armv8-a+sve`, `isa-route := attr` | Arm chain |
| `armv8-a+sve2` | `isa := armv8-a+sve2`, `isa-route := attr` | Arm chain, top |

- `--isa=L` is the family's sugar. `--isa-route=macro` is an explicit
  overlay on `isa-route`, and constraint row 6 refuses it at `portable`.
- `x86-64-v1` is NOT the same as `portable`. It declares the architecture,
  so the artifact is x86-only, with the target attribute and the
  caller-once `cpu_ok()`. That is the mandatory baseline member of
  isa_evaluation.md's (d) variant group (its Q9).
- **A variant group is the family ENUMERATED**: one artifact per listed
  member, which is what (d) builds and `[ART-MGR]`'s catalog picks among.
  The model provides the enumeration for free, because a family is an axis
  with a finite domain. HOW a group is spelled is `[ART-MGR]`'s question,
  not this note's.
- `--isa-marker` is `explicit-only` (§2.8): no member's bundle may assign
  it, which is isa_selection.md Q6's "never implied by `--isa`" as data.
- **[r1 S2] `isa` owns its stamps, so no set stamp repeats it.**
  isa_selection.md §1.2.3's `<PREFIX>_ISA_LEVEL` / `<PREFIX>_ISA` and
  `rx_info.isa` carry D46's two halves, what was asked and what was done.
  Under route M the outcome is a preprocessor ladder that can differ from
  any request. Revision 1 also printed the member in `RX_SETS`, a second
  stamp for the request with a different default rule.

### 4.4 `readable` and `trace`: two standalone sets

| set | class | bundle |
|---|---|---|
| `readable` | instrument (object-identical) | `comments := force` |
| `trace` | instrument | `trace := on`, `comments := force` |

- Both assign `comments := force` and agree, so `--set=readable,trace`
  composes silently.
- `--set=trace -fno-comments` is explicit over a set: the trace build
  without commentary. **[r1 S1/OS-M1]** Revision 1 stamped it
  `RX_SETS "trace;comments"`. There is no stamp now, and under §3.4's
  conditional stamp it would have no line, exactly like `--trace
  -fno-comments` (S1's witness pair). `comments` is three-valued, so the
  same flags across sources (a file's `set trace`, a CLI `-fno-comments`)
  meet row 5's grandfathered deny-wins, not a refusal (cells A6/A7).
- Neither is swept by `test-axes` (instrument class). `--trace` has its
  own design home (`[V-H]`), and comments are already checked for object
  identity (`cli.md`, `-fcomments`).
- **What is NOT in a debug set**, and why: `--emit-ir`, `--emit-facts` and
  `--list-*` are modes (§3.1). `--emit-main` changes the artifact's
  linkage, which is an output choice rather than a debugging one.
  Sanitizer instrumentation of the COMPILEE (`make ubsan`'s `GENCFLAGS`)
  belongs to the consumer's gcc flags, which pcrec does not run (D118).

### 4.5 From the tree: the module gate, and a PCRE2-contract set

**`--features` already IS this model, and it checks the model.**
Decomposed per module (§2.4): `std1` is a PINNED set (`classes := on`,
`modifiers := on`), `all` is a DERIVED set (every module := on), `none`
assigns every module off, an explicit list is the explicit tier, and
`features only` is an assignment of every element. The config/block UNION
rule is the elementwise join. Row 11 (utf8 enables `unicode-props`/`ucp`)
is a DERIVE row whose stamp records the REQUESTED set, which is the request
stamp vs outcome distinction of §4.3, already shipped. **Recommendation:
do NOT move `--features` onto `--set`.** Its vocabulary is modules, not
options, it works, and moving it moves no measurement (D77). It is listed
here because a model that could not express it would be the wrong model.

**[r1 OS-M2] The model check holds at the FILE tier only.** Config and
block UNION per module, which is the elementwise join (cell C8). Across
sources `--features` is one whole-list axis, file-wins and silent (C5,
C6), which is NOT the elementwise join. Revision 1 claimed the model
check without that qualifier, and it fails across sources. The model
keeps today's cross-source rule as row 4 of §2.5's table (R5), with R4's
report added.

**[r1 OS-M5] The migration trigger.** `--features` moves onto the set
mechanism only when a SET must assign a MODULE: a set whose meaning
includes "and these constructs compile", such as a `pcre2-compat` set
enabling modules beside its options. Until then the module gate's own
named sets (`std1`, `all`, `none`) are the simpler mechanism for a
simpler vocabulary. If that set is never asked for, `--features` never
moves, and §0 item 1's count stays four plus one.

**`pcre2-utf`, a contract-class standalone set** (illustrative, no
consumer today):

| set | class | bundle |
|---|---|---|
| `pcre2-utf` | {semantic, contract} **[r1 OS-m9]** | `encoding := utf8`, `utf-check := on` (PCRE2_UTF without `PCRE2_NO_UTF_CHECK`: an ill-formed subject is refused, `PCREC_ERR_UTF`) |

It shows three rules meeting:

- A config naming it, on a target whose BLOCK says `encoding byte`: the
  block's explicit line wins (more-specific, explicit tier), so `encoding`
  is overridden. Constraint row 9 then marks `utf-check` INERT. The
  artifact stamps `RX_UTF_CHECK "inert"` and `rx_info.encoding = 0`.
  **[r1 S1/S3]** Revision 1 also stamped `RX_SETS "pcre2-utf;encoding"`.
  With no set stamp, the OUTCOME stamps say what was done, and the set's
  name is not recorded. Under §3.4's conditional stamp the line would be
  absent, because the resolved assignment does not satisfy the bundle.
- Its class set holds `contract`, so by §2.8's tables it may not be a
  `tune` member, `test-axes` does not sweep it (row (d): `semantic` is in
  the set), and the H11 harness control compares a target built under it
  against its declared behaviour (§3.2).
- It assigns a SEMANTIC axis (`encoding`). The model permits that: a set
  is a bundle of any compile options. The class is what stops it from
  going anywhere answer-identity is promised.

---

## 5. Existing users, migration, and questions

### 5.1 What changes for an existing user

| surface | after the first build |
|---|---|
| every `-f`/`-fno-` flag, its bit, its effect | unchanged |
| a three-valued `-f` axis across sources (union, then refuse) | unchanged; set cells join the same rule (R1) |
| `--tune=`, its aliases, `tune` config lines, the file-wins report | unchanged |
| `RX_TUNE` | unchanged, still unconditional |
| `--features`, `std1`, `all`, `none`, its whole-list cross-source rule | unchanged (R5); a dropped CLI list is now REPORTED (R4) |
| D93's file-wins, the `--engine` exception, `--analysis` fill-only | unchanged for the typed spellings |
| **[r1 OS-M2] a config's RAW `pcrec --engine=` against a CLI `--engine=`** | **CHANGES** under R2: the CLI's explicit engine wins, reported, as the typed line already does (cell D3 flips). The one change of outcome |
| **[r1 OS-n13] stderr on a silent cross-source loss** (raw `--tune=`, `encoding`, budgets, value options, `features`) | **NEW**: one non-fatal report line (R4). No artifact byte moves |
| the three "source contradicts itself" behaviours (pair refusal, value later-wins, comments deny-wins) | unchanged (§0 item 5) |
| every emitted byte, at every dial position, with or without a set named | **[r1 S3]** unchanged: no stamp is built (§3.4) |

The new surfaces are `--set=`, `--list-sets`, the `set` config line and
`pcrec_options.sets`. A user who names no set sees R2's flip (only if
their config spells `--engine=` on a `pcrec` line and they also type a
different engine) and R4's reports. Both are rulings, not side effects.

### 5.2 Migration inside the tree (implement-then-replace, byte-identical)

The FIRST build (§6.1):

1. **The registry gains its class column, its `dominates` column (§2.7a)
   and its unspelled axes.** The class column is the `kind` column
   `[AXES-DENY-MASK]` wants. If that row lands first, the set build reads
   its column. If not, the set build adds it, and `[AXES-DENY-MASK]`
   becomes a reader of it. Either order is one column.
2. **A set table**, `src/core/sets.def`, an X-macro in `axes.def`'s and
   `limits.def`'s shape: one row per (set, axis, value), plus family rows
   (name, default, required class, order). The derived sets' predicates
   are evaluated by the generator that materializes them. **[r1 S16]** The
   `tune` family's rows are not copied in. They are read through
   `TUNE_TABLE`'s accessors (§4.1). The build-time checks run over it:
   the cross-family disagreement check (§2.4), the meta-set prohibition
   (§2.6), the `explicit-only` tag (§2.8) and the class-tag check.
   `--list-sets` dumps it.
3. **The scattered pair refusals and inert rules move into the constraint
   table**, with the three pair rows as one `both-values` row over the
   three-valued kind (§2.7). The diagnostics are unchanged.
4. **Provenance per axis** replaces the ad-hoc "was `--engine` typed"
   tracking, for every spelling (R2), and feeds the reports (R4). The
   `--engine=auto` residual (`tuning.md` §4) becomes expressible, though
   its RULE does not change.
5. **The first consumer's family** (`vector`, §6.1) lands in the same
   change, with its rows' own `abi` event (R4c's `SCAN_ROWS` work carries
   one already). The set layer adds no emitted byte of its own.

The dial re-expression is NOT in this list (§6.2).

### 5.2a [r1 S5] The byte-count reader class

A set stamp is no longer proposed, so the first build moves no emitted
byte and owes this class nothing. The class is recorded because anything
later that adds prologue text owes it: §3.4's conditional stamp, §6.2's
re-expression if it moves a byte, or a digest. Revision 1 named only the
`abi` readers. The readers of a BYTE COUNT are a separate and larger
class, because a stamp that changes length changes every count, even
where no reader cites the abi number.

Found by grep, at `9fd125cb`:

    grep -rlE "emit_bytes|EMIT_BYTES|code_bytes|CODE_BYTES|size_count|SIZELOG|artifact_size_log|wc -c|PROGRAM_BYTES|st_size" src cli lib tests scripts

That command lists 75 files. By role:

- **selections inside the compiler that read emitted length**: the two
  emitted-size caps and the `[ART-SIZE]` ladder (`emit_size_measure` over
  `.c` + `.h`, `src/core/compile.c` ~:2010), the VM entry shape
  (`vm_plan_entry` over the program buffer, `src/gen/emit_vm.c`), and the
  `--warn-emit-bytes` advisory. These are why §3.4 requires placeholder
  rendering: K79's class.
- **stamps that count bytes**: `<PREFIX>_VM_PROGRAM_BYTES`.
- **pinned counts in the suites**: `tests/lib/size_count.sh` and the
  harness's `SIZELOG` pass, `tests/size/`'s tripwire against
  `docs/dev/artifact_size_log.tsv`, `scripts/size_diff`, and the codegen
  checks that compare sizes (`run_size_term.sh`, `run_comments_axis.sh`,
  `run_tune_dial.sh`, `run_prefix_invariance.sh`). Then the CLI's
  near-cap fixture, `tests/bench/run_bench.sh`, `tests/fuzz/fuzz.py`'s
  size-refusal bucket, `tests/axes/run_axes.sh`, and the mech rows that
  name size sites (S192, S193, S237, S405, S437).

The D94 addendum applies unchanged. The lane that adds prologue text
greps this class, moves every pin it touches, and then RUNS the suites
that count (registry, codegen, rxtsource, size), because a reader that
never names the number still moves with it.

### 5.3 The spec plan (D80), for the build lane

- `docs/spec/tuning.md` gains a "§6 Option sets" section: the model in a
  page, the FAMILY TABLE with each family's member count (§3.5's
  independent floor), every PINNED set's bundle as a CONTRACT table, every
  DERIVED set's predicate, the constraint table, the class table, and
  §2.5a's per-kind cross-source table as the stated rule. The dial's §5.4
  table stays where it is, and §6 points at it until §6.2 moves it. The
  identity gates' expectation side reads THIS.
- `docs/spec/cli.md` gains `--set=`, `--list-sets`, the R2/R4 sentences in
  the file-wins section, and one sentence saying a set named in a file
  makes the file speak about its axes (§2.5 row 5). **[r1 OS-M2]** The same
  hunk corrects §2.5a finding 1 (`flags` and raw `-f` bits UNION across
  sources).
- `docs/spec/rxt_format.md` gains the `set` config line.
- `docs/spec/match_api.md` §8.2 gains `pcrec_options.sets`, its NULL rule
  and its refusal channel (§3.3). **[r1 S3]** No stamp-list entry.
- `docs/spec/table_contract.md` lists `--list-sets` as a producer.

### 5.4 Questions for Frank

Each has a recommendation. None blocks the others. Q1-Q12 are revision
1's, re-derived. R1-R6 are the rulings §2.5a and §3.5a require, because
each would change something a caller sees today or leaves a member
unowned. R7 is the comments pair, Q7 under its own number.

1. **Q1, the definition.** A set is a named BUNDLE of axis assignments,
   pinned or derived, combined by compatible union. A predicate is allowed
   only to COMPUTE a derived bundle when pcrec is built, and an order only
   as a family's poset for constraints and sweeps (§2.2). A deny/force
   pair is one three-valued axis (§2.4a). **Recommendation: yes.**
2. **Q2, explicit over set, regardless of argv order, on non-family
   axes, within one source** (§2.5). This generalizes the 2026-09-16 dial
   ruling and departs from gcc's positional `-ffast-math` rule. Family
   axes stay later-wins among their own spellings (§2.3).
   **Recommendation: yes.** Order-free is the predictable reading, and
   it is the one the dial already ships.
3. **Q3, conflicts.** Sets in DIFFERENT families that disagree on an axis
   are refused by name within one source. Members of ONE family replace
   each other. No max/min merging on ordered domains. The runtime refusal
   is built at its first witness, with a build-time check standing in
   until then (§2.4, §6.1 trigger 2). **Recommendation: yes.**
4. **Q4, the `vector` family**: `auto` (default, empty) / `simd` (pins
   the vector rows) / `no-simd` (denies them, SWAR kept) / `scalar` (also
   denies SWAR), all derived from a registry tag and checked against
   independent counts (§4.2, §3.5). **Recommendation: yes.** It follows
   D122 addendum 3's line, and the `simd` pin is what makes "they overlap"
   refusable rather than silently overruled.
5. **Q5, the stamp.** **[r1 S1-S4]** No set stamp in the first build.
   `RX_TUNE` is kept. No `rx_info` mirror and no digest. If a consumer
   asks, §3.4's conditional stamp: emitted only when a set is named,
   valued from the resolved configuration, `tune`/`isa` excluded,
   rendered after every size decision, with a set-invariance check.
   **Recommendation: no stamp until the bench answers (i)/(iii) or
   `[ART-MGR]` asks, and prefer the digest if the bench's answer is
   "stamps".** Revision 1 recommended an unconditional stamp. That is
   reversed.
6. **Q6, provenance.** Build per-axis provenance (default / CLI set / CLI
   explicit / file set / file explicit) WITH the set mechanism, as
   `opt_dial_design.md` §1.3's deferred general form. Its consumers are the
   R2/R4 reports and the unordered-source refusal (§2.5).
   **Recommendation: yes.** No per-family bit.
7. **Q7 (= R7), the comments pair.** `-fcomments -fno-comments` is the
   tree's one SILENT resolution of a self-contradiction (deny wins,
   documented), within one source and across two (A6, A7, A10). It is
   GRANDFATHERED-ASSIGN, a fourth verdict with one row (§2.7).
   **Recommendation: leave it.** It is an output-only axis with no answer
   or byte of object code at stake, and changing a shipped, documented
   behaviour needs a reason this note does not have. Align it to refusal
   if it is ever touched for another reason.
8. **Q8, the sweep's shape** (§3.5). A set is a job, with no products
   except a declared, reasoned `pairs` list, floored at 3 × 2 per box
   rather than the 32-job product. ISA members run at or below the box's
   level and skip loudly above it, and vacuous members still run. The job
   list is checked against the spec's member counts. **Recommendation:
   yes.**
9. **Q9, the spelling.** `--set=NAME[,…]` on the command line, `set
   <names>` in a config (and `--set` refused on a `pcrec` line),
   `pcrec_options.sets` in the API. **Recommendation: `--set=`.**
   `--profile=` reads as one choice where several compose, and `-fset=`
   would hide a user feature in the testing family D47.3 keeps out of
   `--help`.
10. **Q10, user-defined sets.** None. A `.rxt` config is the user's set,
    and it may name pcrec's sets (§2.6). **Recommendation: yes.** Two
    user-bundle kinds would be the parallel mechanism.
11. **Q11, meta-sets.** **[r1 OS-m7]** Forbidden by a build-time check,
    because revision 1's resolution order was circular. A fixpoint is
    designed when a consumer names a meta-set. **Recommendation: yes.**
12. **Q12, the dial.** **[r1 S16]** Revision 1 recommended re-expressing
    the dial in the first build. Reversed: at the first build the set
    layer READS `TUNE_TABLE` through its accessors, a second reader of one
    table, not a second table (§4.1). The re-expression (clskit's
    `cls-matcher`, `TUNE_TABLE` deleted) is §6.2's own step with its own
    trigger. **Recommendation: yes, as its own step.**
13. **R1, set cells on a three-valued axis across sources.** A file set's
    `deny` with a CLI explicit `force` is refused (union-then-refuse, the
    measured rule for explicit bits), not file-wins (§2.4a).
    **Recommendation: yes.** No shipped invocation changes.
14. **R2, one axis, one rule, whatever the spelling.** A config's raw
    `pcrec --engine=`/`--tune=`/`-e`/budget values are the same axes as
    the typed rows. Cell D3 flips (the CLI's explicit `--engine=dfa` wins,
    reported), and E2 gains E1's report. **Recommendation: yes.** D93 and
    its addendum are rulings about axes. Today a spelling decides
    precedence, and nothing ruled that. Surveyed: in this tree one fixture spells it
    (`tests/rxtsource/fixtures/three_configs.rxtin:37`, `pcrec
    --engine=dfa`), and its test passes no CLI engine, so R2 moves
    nothing there. No `.rxt` in pcrec-bench's tree spells it.
15. **R3, a cross-source disagreement involving a set, on a value axis.**
    File wins and REPORTED, D93's shape, not refused (§2.5 row 5).
    **Recommendation: yes.** Refusing it would make a file's set
    un-overridable and un-buildable together with any CLI flag on any of
    its axes, a stricter rule than D93 applies to explicit lines.
16. **R4, the report generalizes** to every axis the file wins on against
    an explicit CLI value, including a dropped `--features` list. Stderr
    only. **Recommendation: yes.** It closes S7's "silently lost" case and
    fixes §2.5a finding 3's misattribution by construction.
17. **R5, `features` keeps its whole-list cross-source rule.** The
    per-element join is a within-source peer rule only (§2.4, §4.5).
    **Recommendation: yes** (no outcome changes; R4 adds the report).
18. **R6, the UNOWNED ISA members** (`x86-64-v4`, `armv8-a+sve`, `+sve2`,
    §3.5a). (a) Ship them compile-only-verified, the runtime arm skipping
    them loudly. (b) Add an emulator runtime arm (Intel SDE, `qemu-user`).
    (c) Hold the members until a box exists. **Recommendation: (a) now,
    and file (b) as its own row, triggered when one of those members
    becomes a requested testee.**

**For the manager, not Frank**: §2.5a's three findings (the `cli.md`
sentence, the spelling-dependent exception, the misattributed report)
are facts about today's tree. They stand whether or not any of the above
is ruled.

---

## 6. The build trigger (D77)

**Nothing here is built until a consumer needs two or more axes to move
together under ONE NAME.** The dial does not qualify: it already ships its
own table, and moving it alone would be a refactor with no measured need.

### 6.1 The first build's triggers [r1 S16]

Revision 1's first two triggers were row LANDINGS. "R4c lands and a second
deny is landing" fires on a schedule, not on a need. "R4g lands `--isa`"
is not a need at all, because a family is an axis and `--isa=L` ships as
an ordinary value option without this mechanism. The revision's triggers
are each a REQUEST or a WITNESS, and each is independent of the others:

1. **A named consumer asks for one name over vector-family bits that are
   already on main.** Precondition: at least two `vec-` deny rows are on
   main (counted by §3.5's name scan, not the tag). Request: a `test-axes`
   job, a bench testee or a user needs them off together, and spelling
   them out is the documented burden. Two bits on main with nobody asking
   is not a trigger.
2. **The set table's first cross-family DISAGREEMENT.** The build-time
   check (§2.4) fails pcrec's own build when a change makes two sets in
   different families disagree on an axis: integration.md Q16's
   `min-size`-denies-`vec-scan` is the predicted first case. That change
   then carries the runtime refusal, its diagnostic, its `tests/cli` case
   and its sabotage row, with itself as the witness. This trigger applies
   only once the set layer exists. Before that, the same change is
   §6.2's trigger, because two families' tables then have to agree.
3. **pcrec-bench asks, through pcrecdev2, for a named SIMD-off or ISA
   testee**, or answers §3.5's question (i)/(iii) in a way that needs a
   set's name in the artifact. This also fires §3.4's conditional stamp.

When one fires, the build is one lane, in §5.2's order: registry columns,
set table with `tune` read through `TUNE_TABLE`, constraint table,
provenance with the R2/R4 reports, the triggering family, and §5.3's spec
hunks. It adds no emitted byte of its own. Until then the plan row stays
design-only.

### 6.2 The dial re-expression: its own step, its own trigger [r1 S16]

Moving the dial onto the set table moves a working, pinned mechanism.
That needs a measured need of its own (D77), and the first build does not
supply one, because §4.1's accessor read already gives the set layer
everything it needs. The re-expression fires on the FIRST of:

1. **A ruled D103 cell diff needs an axis `TUNE_TABLE` has no column
   for** (for example a `vec-*` deny, integration.md Q16, or a force twin
   from `opt_dial_design.md` §7.2a). Widening `TUNE_TABLE` would then
   duplicate the set table's row shape, which is the parallel mechanism
   `pcrec-general-mechanisms-not-special-cases` names. Moving the dial
   costs no more than the widening would.
2. **A second reader of the λ position appears** outside clskit, so that
   the position mask (`TPOS`) would be copied rather than read.

When it fires, it is its own change: `cls-matcher` becomes an axis,
clskit reads it, the value cells' source of truth moves, `TUNE_TABLE` is
deleted, and identity gate 1 (§3.5) proves the five positions
byte-identical over the corpus. It carries the D103 ritual's new step
(§4.1).

**Where a panel should attack first** (revision 2):

- §2.5a's cell set. Is there an axis KIND with a cross-source rule that
  none of the 42 cells exercises (the `--fast-or-fail`/cap family, the
  `--max-emit-*` overrides, `--warn-emit-bytes`)?
- R2's flip of cell D3. The `.rxt` survey (R2) found one fixture and no
  caller relying on it. Is there a non-`.rxt` driver (a bench adapter, a
  Makefile recipe) that passes `--engine=` against a config that also
  sets it?
- §3.4's conditional stamp: is the presence asymmetry (`--set=readable`
  against `-fcomments`) acceptable to a consumer, or is the digest the
  only honest stamp?
- §3.5's pairs floor (6 per box). Does `SCAN_ROWS` have a third predicate
  regime between `BASE` and the top `DECLARED` level that the floor skips?
- §2.7's REFUSE-first rule. Is there a shipped REFUSE whose diagnostic
  today depends on an INERT row having run first?
