# Measurement sets — the format, the store, loading, the kit channel, the tool (rev 3)

Status: DESIGN ONLY, revision 3 (lane msrev3, 2026-10-16, from main `063b4a4b4`, abi 78).
Revision record: rev 3 + sibling edit, 2026-10-16 (lane msib: `<PREFIX>_MEASURES` render
point and union-over-attempts, from `memfn/window_contract.md` rev 3.1 §3.7.3a and D167
addenda 2 and 3; §3.5, §4.2, §9.2 part 5).
Revision 2 was lane msetrev (2026-10-14, from `58338a09f`); revision 1 was lane msetdes
(same day). Nothing is built; nothing under `src/`, `cli/`, `lib/` or `tests/` changes.
Plan rows [MEASURE-SET] and, for §9, [KNOW-SRC]; ruled by D166 and its addenda 1/1.1 and 2,
and by D167 (Q-R17P-14)
(read D161 addenda 11-13, D162 and its addenda, D149 and D157 with it).

**Revision 3 answers the light re-check r2
(`../dev/reviews/2026-10-16-r2-measure-sets-recheck.md`: 0 BLOCKER, 8 MAJOR, 11 MINOR,
5 unlocks).** Read §R3 first. Changed text carries `[r2 <id>]` in place. Revision 2's
own record (§R2) follows it unchanged.

## R3. What revision 3 changed, by finding

Every finding is ACCEPTED. None is rejected. One MINOR is accepted in part, with the rest
deferred to a named trigger (n7).

| finding | disposition | section | how |
|---|---|---|---|
| M1 the evaluator parameter table missing | ACCEPTED | §9.1, §9.1a, §9.5, §9.11 (new) | A fourth kind row, `evaluator-params`: FILE only, no store, no flag, no artifact stamp; its item digest IS the prereg hash. The placement rule is a first-match row table (§9.1a). §9.11 states the canonical format the kit's `prereg.tsv` uses from today. Whether the kit reads it through pcrec's parts or its own reader is OQ-1 (§10.6) |
| M2 the shared resolver contradicts the analysis kind | ACCEPTED | §3.2, §9.2 part 2, §9.5, §9.7 | Every divergence is a declared column of the kind row: `flag_classify`, `list_classify`, `s2_mismatch`, `s2_multi`, `revs`. Measures adopt the SHIPPED `name-else-file` classification. Measures REFUSE an S2 mismatch, analysis FALLS THROUGH, and §3.2 says why they differ. K1's zero-mover witnesses name `tests/findings/res_fixtures.py` |
| M3 the round trip shares its reader and writer with its subject | ACCEPTED | §9.6, §8.5, §5.2, §3.2 | (a) A new check R5, decoded = independent: the C loader's field-by-field decode equals the python parser's decode; for analysis, the resolution digests equal `findings_ref.py bundle-digest`. S983 plants a symmetric column swap that R1-R4 miss. (b) R3's independent side for the analysis kind is `analyze/`'s own bundle-text reader, extended at K3 to every section; that extension is priced. (c) Fixed by M2: `--measures=f.tsv` is now a FILE |
| M4 the census tool duplicates `emit_sweep.py` | ACCEPTED | §9.3, §8.4, §8.5 | The census is an `emit_sweep.py` MODE (`--data KIND OLD NEW`), with an attribution stream and a movers-TSV writer. Its population is emit_sweep's pinned streams. `knowledge_census.sh` and `census_population.tsv` are withdrawn. S952 re-aims onto emit_sweep's existing reach floor |
| M5 one digest column cannot express analysis's two digests | ACCEPTED | §9.2 part 5, §9.5, §9.6, §1.6 | Each kind row has two digest ROLES, ITEM and STAMP. Each role is a literal domain BYTE STRING with its length, plus a sub-key policy (`none` or `query`). The shipped `pcrec-find-1\0<query>` and `pcrec-find-rows-1` are grandfathered byte for byte. No domain is renamed or derived. R1 uses the ITEM digest. A K1 gate pins every shipped `_FINDINGS` stamp and `rows_digest` unchanged. The note states what `rows_digest` does not cover |
| M6 the `lib` resolver is an unplaced third member | ACCEPTED | §9.1, §9.5, §9.7, §11 F12 | `lib` is a resolve-only kind row: no stamp, no digest, no flag, and its own stops (the source's directory, then `-I`). Its entry match is a COLUMN, `entry_match = probe-exists`, which keeps K1 zero-mover. The case-exactness drift is filed as finding F12 against `rxt_source.c`. Fixing it flips that column to `exact`, as its own caller-visible change. The reserved `lib <store-name>` is U4 |
| M7 the reach lever crosses the kit boundary | ACCEPTED | §4.4 (R-MS6), §8.1, §8.5 | R-MS6 asks the kit for a harness-only arm-entry counter under the reserved prefix. The admitted-arm list is the `memfn` fired-rows section (R-MS4), checked against the synthetic `dispatch` set's construction. Python reads no kit predicate. S956 re-aims at the hook |
| M8 a core→parse link edge in a "dependency-free" module | ACCEPTED | §9.2, §7.1 | The kind-independent PARTS (`src/core/ksrc.c`) include only libc and `ksrc.h`. They allocate and write through two small callback structs, and hold no kinds table. The table `ksrc_kinds[]` is assembled at the library tier. The analysis row is registered from `src/parse/`. `pcrec-measure` compiles the parts plus the measures row and nothing else. Its dependency set is stated, with a link check (S989) |
| r1 msc1-5 PARTIAL | ACCEPTED | as M7 | discharged by M7's fix |
| r1 msc2-9 PARTIAL | ACCEPTED | as M1, M2, M4, M6 | the family is complete: four ruled kinds plus `lib`, limits placed (§9.1a, U3), emit_sweep unified, the resolver's divergences declared |
| n1 sabotage re-aims not derived | ACCEPTED | §9.7 | K1 delivers a DERIVED edit set and derived re-aims (re-aim or re-run) for every `SAB_FILE=` row anchored in `rxt_find.c` or `findings.c`, plus `limits_check.sh`'s `PCREC_FIND_NTBL/NBUNDLES` reader |
| n2 `analyze/` is a second writer and reader | ACCEPTED | §9.1, §9.6, §9.9 | It is a DELIBERATELY INDEPENDENT TWIN, not a member that "exists once". It serves as R3's control |
| n3 per-kind special cases written as prose | ACCEPTED | §9.5 | They become columns: `bare_view` (`canonical` or `shipped`) and `r4` (`required` or `exempt`) |
| n4 two attribution mechanisms for analysis | ACCEPTED | §9.3 | Attribution is the lookup TRACE. The `_FINDINGS` stamp items are its cross-check |
| n5 shadow rule keyed on id only | ACCEPTED | §3.2, §3.3, §9.6 | The shadow check is keyed on (id, rev). `NAME@REV` at S2 requires the header `rev` to match. S988 |
| n6 digest codes undefined | ACCEPTED | §1.6 | A code table for the unit byte and the status byte |
| n7 the pcrec-side dependency hash over-stales | ACCEPTED in part | §2.4 | Recorded: pcrec rows over-stale BY DESIGN until M4. Body normalization is DEFERRED to M4, the first stage with a `pcrec.` row |
| n8 an excluded key versus the card's `env` | ACCEPTED | §6.2 | The cross-check runs only on keys with an agreed derived direction. An excluded key lists the card's `env` beside `excluded` in an always-printed INFO bucket |
| n9 MOVERS for a default rollback | ACCEPTED | §2.1, §8.4 | The census is keyed by TRANSITION: `measure_store/DEFAULTS.log` and `measure_store/movers/<seq>.tsv`. A rev directory holds no MOVERS file |
| n10 oracle capture per set | ACCEPTED | §8.1, §10.1 | A set's landing bar includes the libpcre2 `match-at` capture of its generated boundary subjects. That needs the local adapter's box |
| n11 the `ks_pick` tier | ACCEPTED | §9.2 part 3 | `ks_pick` returns the decision and the disagreement as data. The CLI prints the note through `cli_err` |
| U1-U5 | FILED, not built | §10.4 | each with its trigger |
| D167 Q-R17P-14 (ruled 2026-10-16) | FOLDED | §1.2, §2.4, §5.1 | `libc:<name>@<version>` is provenance in `deps`, plus a SET-level `libc-mismatch` listing flag beside `compiler-mismatch`. It is never row staleness |

One question goes to Frank (§10.6, OQ-1): whether the evaluator-parameter kind's READER is
pcrec's shared parts or the kit's own, with one shared format and digest spec either way.
Every other choice above changes no answer and is the manager's
(`pcrec-answer-free-choices-are-mine`). It is part of the
framework Frank wants before further optimization (plan row [REGIME]). Its first customer
is the kit's R17-b′ (`memfn/r17b_prime.md` §3, whose measurement table is the needs list);
the interim shape is the kit's TSV from `memfn/regime_eval.md` Q-REVAL-10. The method a set
is measured by is `docs/dev/lanes/grid1_report.md` + `gridread_report.md`.

**Revision 2 applies the D6 panel r1 (`../dev/reviews/2026-10-14-r1-measure-sets.md`: 4
BLOCKER, 22 MAJOR, 12 MINOR, every finding ACCEPTED, the dispositions binding).** Read §R2
first. Changed text carries `[r1 <id>]` in place.

**Folded into revision 2 before its review, from Frank's same-day rulings:**

- **D166 addendum 2.** Q-MS-1 is RULED: the latest set at M0/M1, the envelope default at
  M2 (§3.4). The stale default is RULED: carried stale, a listing flag and manager review,
  never a landing gate (§2.4). Both are written as RULED, not as open questions.
- **[KNOW-SRC] (Frank: "i like the consistent data tool idea ... with consistent
  loader").** §9 is that row's design: ONE knowledge-source module plus ONE data-mover
  census tool serving findings, measurement-set and limits changes. It is built FIRST,
  implement-then-replace onto the analysis loader at zero movers, before every
  [MEASURE-SET] stage (§9.7, §9.8, §10.1).
- **ROUND-TRIP IDENTITY ([KNOW-SRC]).** A listing's canonical view of one item is a
  loadable input of its kind, with the checks load→list→load (same digest) and
  list→load→list (same bytes), plus a structural R3 this revision adds (§9.6). Derived
  views are separate views, and the loader rejects their sections.
- **The analysis object's `.rxt` data format is RECONSIDERED** against the section TSV.
  Both cases and the migration cost are laid out as an OPEN item for the module's design
  (§9.9).

## R2. What revision 2 changed, by finding

| finding | section | how |
|---|---|---|
| msc1-1 (BLOCKER) | §2.1, §8.4 | `MOVERS.tsv` is the census AT its landing commit (`code_commit` in its own header). The re-run comparison runs only in the commit that adds the set or moves a `DEFAULTS` pointer, never against a later HEAD |
| msc1-2 (BLOCKER) | §2.3, §9.2 part 4 | The pre-parse is written by a C generator (`scripts/ksgen.c`, on `scripts/findgen.c`'s precedent), which links a stage-0 build of the one C reader. Python is only the checker (§8.2) and never writes an embedded byte |
| msc2-2 + msc1-4 (BLOCKER) | §3.4, §6.1, §10.1, §10.5 | M0/M1 compile with the LATEST set (D166 literal). The envelope default arrives at M2. The n=1 selection difference is stated (every cost row drops, so every pay rule takes `unpaid`) and censused at M2. A composite carries its members' unit rows as provenance (`#section members`). Q-MS-1 was re-put and is now RULED (D166 add. 2) |
| msc1-5 (treated as blocking) | §8.1 | A run-time REACH floor per dispatch arm (a harness-only counter lever). Generated boundary subjects (L\*−1, L\*, L\*+1, W±1, 2W±1) per synthetic set. Synthetic sets carry the dispatch rows, so the dispatch is emitted and reached |
| msc2-1 | §1.2 | The wire shape is `table_contract.md` §4's real `#section NAME` syntax, chosen over oracle_store's `# k=v` line, with the reason |
| msc2-3 | §3.5, §3.6 | The stamp is the EMPTY STRING when nothing was asked (the `_FINDINGS` meaning). The digest is the loaded set's `values_digest`, kept over the whole set and not the consumed subset, with the reason (§3.5). The `rx_info.measures` mirror is ADDED in M0's abi bump |
| msc2-4 / msc2-5 | §1.3 | One canonical key string: an owner, a quantity, then dimension tokens in the order the quantity's METHOD CARD declares. The format defines no placeholder. An optional free `tags` column is display only. The seven fixed vocabulary columns are gone (D157). The checker needs only grammar, uniqueness and arity. R17-b′'s keys are reconciled in §1.3.3 |
| msc2-7 | §4.1, §4.2 | Stamp-on-load: the stamp's content is fixed when the set loads. The kit returns one boolean, `consulted`. pcrec hands over only `kit.` rows, with no `status` (a NULL row is simply not handed over) |
| msc2-9 SIBLING FAMILY + msc1 U1 | §9 (new: [KNOW-SRC]) | ONE `src/core/ksrc.c` knowledge-source module (section-TSV reader/validator, name resolver, fill-only precedence, embed generator, stamp/digest builder, the `--list-<kind>` shape), parameterised by KIND: the analysis object, measurement sets, [TABLE-JUDGE]'s picks file. ONE data-mover census tool serves findings, measures and limits changes (§9.3). It is BUILT FIRST, and the analysis loader migrates onto it at zero movers (§9.7) before [MEASURE-SET]. Round-trip identity (§9.6). The `.rxt` analysis format is reconsidered as an open item (§9.9). `--list-measurements` consumes [LIST-TABLES]' census (§5.4) |
| msc2-10 | §4.4 (new), §10.1 | The kit return facts become five requests main files (R-MS1..R-MS5), each with its landing bar. M0's trigger is R17-b′ landing WITH R-MS1, R-MS2, R-MS3 and R-MS5 |
| msc1-3 | §3.6, §10.2 | D162 ruling 1 KEPT: a default-set change that moves an emitted byte IS an abi event (pre-1.0 ritual), carried with its mover census. Because the stamp names the set, every default change moves every consulting artifact, so every default change is one. Q-MS-2 is withdrawn |
| msc1-6 | §8.1 | Only "stamp empty ⇒ bytes identical across every set" is kept. The converse is dropped |
| msc1-7 | §2.4 | Staleness is TRANSITIVE: a row's own dependencies (form, compared form), its inputs, the unit row, a pcrec-side hash, and a compiler-mismatch flag |
| msc1-8 / msc2-6 | §2.4, §10.5 | The hashed canonical instance is defined: the form BODY with scaffolding normalized out, owned by the kit (R-MS3). The stale-default POLICY went to Frank and is RULED (D166 add. 2): carried stale, a listing flag and manager review, never a landing gate |
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
| unlocks | §10.4 | Filed with triggers, not built. The shared module and the census tool (U1) moved INTO scope as [KNOW-SRC] (§9) |

Both questions the panel left for Frank are RULED (D166 addendum 2, §10.5). Revision 1's
Q-MS-2 is withdrawn (D162 ruling 1 is kept). Q-MS-3..8 are settled by the manager (§10.5
lists how). One item is OPEN for the module's own design: the analysis format (§9.9).

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
   - A rev is immutable. Each `DEFAULTS` transition has a census at its landing commit,
     `movers/<seq>.tsv`, logged in `DEFAULTS.log` [r1 msc1-1, r2 n9].
   - Staleness is COMPUTED and transitive. A stale default is CARRIED STALE, with a
     listing flag and manager review, never a landing gate (RULED, D166 add. 2)
     [r1 msc1-7/msc1-8].
3. **Loading (§3): `--measures=NAME|NAME@REV|FILE`** and a config line `measures`, with
   exactly `--analysis`'s precedence. A value is a NAME if it passes the name grammar and
   a FILE otherwise: the shipped `--list-analysis` rule [r2 M2].
   - A bare compile reads the LATEST set at M0/M1. The envelope becomes the default at M2
     (RULED, D166 add. 2) [r1 msc2-2+msc1-4].
   - The stamp is `<PREFIX>_MEASURES`, mirrored in `rx_info.measures`, both added in M0's
     ONE abi event [r1 msc2-3]. It is `""` when nothing was asked, else `id@rev:digest16`.
   - Every later default-set change is an abi event with its census (D162 r1) [r1 msc1-3].
4. **Kit channel (§4).**
   - `mf_measures` on `mf_art_begin` carries `kit.` rows only.
   - Stamp-on-load. The kit returns one boolean, `consulted` [r1 msc2-7].
   - The kit-facing facts are FIVE requests main files, each with a landing bar
     (R-MS1..R-MS5, §4.4) [r1 msc2-10].
5. **`--list-measurements` (§5).** It has [KNOW-SRC]'s four views (§9.2 part 6). The
   CANONICAL view of a set IS a loadable set (round trip, §9.6). Reader rows come from
   [LIST-TABLES]' census of declared tables, not from a scan of its own [r1 msc2-9].
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
   - The census is at landing, keyed by `DEFAULTS` transition [r1 msc1-1, r2 n9].
     Sabotage S943-S963 (allocated), plus PROPOSED S983-S990 [r2].
9. **[KNOW-SRC] (§9), built FIRST.** The module has kind-independent PARTS in `src/core/ksrc.c`
   (libc only) and a kinds table assembled at the library tier [r2 M8]. It serves the four
   ruled kinds, the analysis object, measurement sets, [TABLE-JUDGE]'s picks file and the
   EVALUATOR PARAMETER TABLE [r2 M1], plus `lib` references as a resolve-only row
   [r2 M6]:
   - the reader/validator, the resolver (its per-kind divergences as declared columns,
     [r2 M2]), fill-only precedence, the embed generator, the item and stamp digests
     (two roles, literal domains, [r2 M5]) and the `--list-<kind>` shape;
   - with ROUND-TRIP IDENTITY (§9.6), whose R5 compares the C decode with an independent
     reader [r2 M3].

   The data-mover census is a MODE of `scripts/emit_sweep.py` and serves findings,
   measures and limits changes [r2 M4]. The analysis loader migrates onto the module at
   zero movers (K0-K3) before M0 [r1 msc2-9, msc1 U1]. The analysis `.rxt` format is an
   OPEN item for the module (§9.9).
10. **Plan (§10).**
    - K0-K3 ([KNOW-SRC]) first.
    - M0 rides R17-b′, with the requests, and adds the measures kind.
    - M1: `--measures=` and the census's measures arm.
    - M2: the envelope and its default flip.
    - M3: the tool. M4: pcrec's own rows.
    - Both panel questions are RULED (D166 add. 2). One question is open for Frank:
      OQ-1, the evaluator-parameter kind's reader (§10.6).

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
libc	glibc@<version>
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
- `libc`: `<name>@<version>` of the C library the measured code ran against. It is
  provenance, and the source of the set-level `libc-mismatch` listing flag (§2.4; D167
  Q-R17P-14).
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
- **`values_digest`** is FNV-1a-64, 16 lowercase hex. It is computed over the 13 domain
  bytes `pcrec-meas-1\0`, a literal byte string like every kind's domain (§9.2 part 5)
  [r2 M5]. Then, for each row in canonical order (§1.7), it takes the key, `\0`, the unit
  byte, the status byte, and `value_e6` as int64 LE (an empty value is `INT64_MIN`).
- **The unit and status BYTES [r2 n6]** are fixed codes in `docs/spec/measures.md`. C and
  python each read them from the spec's table. Neither reads them from the other's source:

  | unit | byte | | status | byte |
  |---|---|---|---|---|
  | `ratio` | `0x01` | | `measured` | `0x01` |
  | `walkbytes` | `0x02` | | `fitted` | `0x02` |
  | `bytes` | `0x03` | | `derived` | `0x03` |
  | `count` | `0x04` | | `null` | `0x04` |

  `0x00` is never assigned. A new unit or status is a spec row with a new code, never a
  reuse. The python checker's digest (§8.2(d)) is written from this table.
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
  DEFAULTS.log                    # append-only: one row per DEFAULTS transition: seq, class, old id@rev:digest16,
                                  #   new id@rev:digest16, the movers file  [r2 n9]
  movers/
    0001.tsv                      # the census of transition 1, AT ITS LANDING COMMIT (§8.4)
```

This is `oracle_store/`'s shape (one directory per source, a self-checking TSV,
PROVENANCE, a generator) applied to data derived by RUNNING pcrec's kit and engines on a
box. It is not `third_party/` (nothing is vendored from outside). The analysis object's
`src/findings/*.rxt` is the sibling on the data side.

- **The `raw/` directory is gone.** Its job (the reader's input) moved into the set's
  `cells` section, where the checker can reach it (§1.5).
- **The directory is `measure_store/`**, not R17-b′'s `measures/`. That was Q-MS-4,
  settled by the manager as a one-token choice (§10.5).

**The movers census, keyed by TRANSITION [r1 msc1-1, r2 n9].** Revision 2 wrote
`MOVERS.tsv` into the new default's rev directory. That fails for a ROLLBACK: moving
`DEFAULTS` back to an older rev that already holds MOVERS from its own landing leaves
nowhere to write, because that directory is immutable. The census therefore belongs to the
transition, not to a set:

- **`DEFAULTS.log`** is append-only. Each `DEFAULTS` change appends one row: `seq`,
  `class`, `old` and `new` (`id@rev:digest16`), and the movers file's name. `DEFAULTS` is
  the log's last row per class, and §8.3 checks that equality.
- **`movers/<seq>.tsv`** has a header naming `old`, `new`, `code_commit` (the HEAD the
  census ran on: the landing commit's parent tree plus the change) and the emit_sweep
  population's pin (§9.3). It is written once, by the census mode of
  `scripts/emit_sweep.py` (§9.3), in the commit that changes `DEFAULTS`. It is immutable
  from then on.
- **What it describes.** It states what moved AT that transition. A later code change
  that moves selections under the same default is that change's own movers (`emit_sweep`,
  the identity gate), not this file's.
- **A set that moves no default** (an older or alternative set, a scratch set) appears in
  no transition. A rollback to `zen4-grid1@1` is a new transition with its own
  `movers/<seq>.tsv`.

### 2.2 Naming, versions, rollback

- **`id`** follows `[a-z][a-z0-9_-]*` (the analysis name grammar, §9.2 part 2), by convention
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
- **`ksgen` is C.** It links a STAGE-0 build of the knowledge-source PARTS and the
  measures row (§9.2: the one section-TSV reader and the measures-kind validator, with no
  store, as `PCREC_FIND_STAGE0` does for findgen) [r2 M8]. It parses with the reader the library uses at
  run time, in its no-filesystem buffer mode.
- **No python writes an embedded byte.** Revision 1's `generate.py` wrote both the text and
  the pre-parse that the structural check then verified against its own python twin. That
  is a control sharing a source with its subject (learnings §3). The python parser is the
  CHECKER only (§8.2, §8.3).
- **Committed, not rebuilt.** Both `.inc` files are committed. A plain `make` does not
  regenerate them, and `make gen-tables && git diff --exit-code` covers the chain (§8.3).

Why keep the pre-parse for 47 rows: the library's no-filesystem path must be one code path
for every knowledge kind (§9.2 part 4), and findings already measured the parse-per-compile cost
as worth removing (findgen.c's header: ~47 µs, ~20% of a minimal compile, for `default.rxt`).

**Embedding every rev, not only the default.** 47 rows is about 6 KB of text per set and
15 KB with the pre-parse; the cells and cards add about 4 KB. Ten committed sets stay below
one `fold_tables.inc`. Rollback must work from a release build (Q-MS-7, settled §10.5).

### 2.4 Staleness: transitive, defined, and the policy RULED [r1 msc1-7, msc1-8, msc2-6]

**What a row depends on.** A row's `deps` column holds `;`-joined items
`owner:dep-id=hash`, written by the producer from the card's `deps` declaration:

- `kit:form.V1=…` and `kit:form.walk=…`: the measured form AND the compared form (`vs`),
  each hashed by the kit (R-MS3).
- `pcrec:<id>=…`: a pcrec-side hash, for rows whose measured code includes pcrec's own
  emission (a pcrec quantity, or a kit quantity measured through a pcrec-emitted consumer).
  It is the hash of the pcrec emitter's output for the card's named probe pattern, with
  the stamp lines stripped (`emit_sweep`'s normalization).

  **This over-stales BY DESIGN until M4 [r2 n7].** An abi bump or any unrelated emission
  change moves the hash, unlike the kit's body-normalized form hash. No `pcrec.` row
  exists before M4, so nothing stales falsely before then. M4 is the stage that adds the
  first pcrec quantity. It replaces this hash with the measured FUNCTION BODY under the
  same normalization R-MS3 asks of the kit (prefix, identifiers, comments, blank lines),
  or it records in the card why the whole artifact is the measured instance. That choice
  is deferred to M4, because the right instance depends on what pcrec's probe measures.
- `libc:<name>@<version>` (D167 Q-R17P-14): the C library the measured code ran against.
  It is PROVENANCE, never a staleness dependency. The artifact runs against the caller's
  library, so a library that differs from the measuring one is not a change to the
  measured code.

**The canonical instance [r1 msc1-8/msc2-6].** A form hash is over the form's BODY with
SCAFFOLDING NORMALIZED OUT. It is the text the kit emits for a fixed canonical site (fixed
set, fixed span, fixed prefix), with the prefix, generated identifiers, comments and blank
lines normalized. So it moves when the instruction text the timing measured moves, and
not when a name, a comment or a neighbouring declaration moves. The kit owns that
definition and exposes it as `mf_form_hash(form_id)` (R-MS3). pcrec compares opaque
strings. Revision 1 left "the hashed text" undefined, so every kit comment change would
have staled every row.

**A row is STALE iff any of:**

1. any `kit:` or `pcrec:` `deps` hash differs from the current one (the kit's
   `mf_form_hash`, pcrec's recomputed hash). A `libc:` item never stales a row;
   it feeds only the set-level flag below;
2. any input row of a `derived`/`fitted` row is stale (transitive through `inputs`);
3. the UNIT row is stale, for every `ratio`/`walkbytes` row. Every relative value is
   relative to it.

**A compiler mismatch** (the set header's `compiler` against the build's `$CC -dumpfullversion`
and the card's flags) is a SET-level listing flag, `compiler-mismatch`, not row staleness.
The emitted text is the same and the machine code may not be, so it is reported, never
computed into a verdict.

**A libc mismatch** (the set header's `libc` against the build's C library, read with the
same probe the header was written with) is a second SET-level flag, `libc-mismatch`,
reported the same way and never row staleness (D167 Q-R17P-14). Main owns this third
dependency owner on those terms.

**Where it is computed.** Staleness is COMPUTED, by `make test-measures` and by
`--list-measurements` against the linked kit. It is never written into a committed file,
because sets are immutable.

**A stale row in a set selected for a compile is READ.** Skipping it would move a
selection with no measurement behind the move: a silent default, which
`pcrec-no-silent-defaults` forbids. It is flagged `stale 1` in every listing.

**A stale DEFAULT is CARRIED STALE (RULED, D166 addendum 2, Frank 2026-10-14).**

- **The rule.** When a measured form's normalized body changes after its set was measured,
  the default set stays the default. Its stale rows are read. The listing flags them
  (`stale 1`, with the dependency that staled it, and a per-class count in the `sets`
  index), and the manager reviews them.
- **Never a landing gate.** A re-measure needs a quiet box or a bench window, and kit text
  changes must not wait on one.
- **What `make test-measures` does.** It prints the per-class stale counts as an
  always-printed INFO bucket (`record()`'s shape), and nothing FAILS on staleness.
- **The review.** The manager reads the count at each kit merge and schedules a
  re-measure when stale rows feed a reader.

Revision 1's rule (a stale default FAILS) was option (a) and is withdrawn. Option (c), a
declared cost-neutral equivalence row per form change, was not taken: it is a mechanism
ahead of a measured need (D77).

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

### 3.2 Resolution, in a stated order [r1 msc2-8, msc1-14, r2 M2, M3c, n5]

Classification is by spelling alone, with NO existence probe, so the same argument means
the same thing in every directory. It is the SHIPPED rule `--list-analysis` already uses
(`pcrec_find_name_ok(X)` means NAME, else FILE; `cli/main.c:1808-1809`, `2233-2236`)
[r2 M2]:

1. A value that passes the name grammar, optionally followed by `@REV` (§2.2: `@` then
   decimal digits), is a NAME.
2. Anything else is a FILE.

Revision 2's rule (a `/` means FILE, the grammar means NAME, anything else is refused)
disagreed with the shipped analysis surface on every value with no `/` that fails the
grammar. It also refused the note's own example, `--measures=f.tsv`. Under the shipped
rule, `--measures=f.tsv`, `--measures=mine.measures.tsv` and `--measures=./f.tsv` are all
FILEs, because `.` is not in the name grammar [r2 M3c]. A file literally named
`zen4-grid2` in the cwd is read as a NAME. That is the same as `--list-analysis` today,
and `./zen4-grid2` is the FILE spelling. The rule is the kind row's `flag_classify` and
`list_classify` columns (§9.5), so it is data, not a measures-only branch.

**A NAME** is looked up through [KNOW-SRC]'s resolver (§9.2 part 2), in the stops the
analysis uses minus S1 (a set is never defined inside a `.rxt`):

- S2, `DIR/NAME.measures.tsv` for each `-I DIR` in order, with the directory entry matched
  exactly (`rxt_find.c`'s `dir_has_exact`);
- S3, the store.

**An S2 file whose header names something else is REFUSED** (the kind row's
`s2_mismatch = refuse`) [r1 msc1-14]. Its header `id` must equal NAME and, for
`NAME@REV`, its header `rev` must equal REV [r2 n5]. The stamp names `id@rev`, so a file
answering a name or rev it does not carry would make the stamp lie. An unknown name
refuses the compile and names the stops searched (`stops_text`).

**Why the analysis kind does the opposite.** An analysis S2 file of another name FALLS
THROUGH to the next stop, with a note (`s2_mismatch = fallthrough-note`;
`docs/spec/findings.md` S2 row, `rxt_find.c:12-15`). A `.rxt` in a `-I` directory is
often a `lib` library that legitimately sits beside the bundles, so a mismatch there is
normal. A `.measures.tsv` has no such neighbour: its suffix says it is a set, so a
mismatch is an error, and silently skipping it would hide a typo'd id. Both kinds refuse
a file defining two or more items (`s2_multi = refuse`). The divergence is a declared
column value, and K1's resolution fixtures witness it for the analysis kind (§9.7).

**A FILE** is read directly. Its header `id` and `rev` are what the stamp carries,
subject to §3.3's shadow rule.

### 3.3 Precedence (D93)

Identical to `--analysis`: fill-only.

- A target whose config names `measures` gets that set. `--measures` names the set for
  targets whose configs name none.
- A disagreement is reported in `tune`'s shape, and the file wins: "... CLI --measures X
  and this file's measures Y disagree; using the file's value (--measures is fill-only)".
- There is a single value per compile. Sets are never mixed, so there is no per-quantity
  precedence and no chain.
- **A user set may NOT shadow a committed rev [r2 n5].** The check is keyed on
  (`id`, `rev`), not on `id` alone:
  - a `-I` or FILE set whose (`id`, `rev`) is in the store is accepted only with the same
    `values_digest` (it IS that set, the round trip of §9.6);
  - one whose `id` is in the store under a `rev` the store does NOT hold is refused ("id
    X has no committed rev N; rename"). Revision 2 accepted `id zen4-grid2`, `rev 7` with
    rev 1's digest, and that stamped `zen4-grid2@7:…`, a rev that does not exist;
  - one whose (`id`, `rev`) is in the store with a different digest is refused ("X@N is
    a committed set; rename").

  The stamp names a set by `id@rev:digest`, so a shadow would make a stamp point at a set
  that does not carry those values. S988 plants the id-only key.

### 3.4 What a bare compile reads [r1 msc2-2, msc1-4]

Priority: an explicit flag, then the config, then the BUILD'S default for the compile's
class.

**RULED (D166 addendum 2, Frank 2026-10-14): M0 and M1 ship D166's literal reading.**
Until a SECOND OFFICIAL set exists, a bare compile reads the LATEST committed
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
(D161 add. 12; RULED as the M2 step by D166 add. 2).

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
- **Rendered ONCE, after `mf_art_end`.** `<PREFIX>_MEASURES`, like `<PREFIX>_FINDINGS`,
  is written at the single render point of `docs/design/memfn/window_contract.md` §3.7.3a
  (the finishing pass, after `mf_art_end` returns), never in `emit_info_def`. It reads the
  kit's layer-invariant `consulted` (§4.2), so the emptiness test sees the kit's last
  read. This is the layer-invariance obligation revision 3 lacked (wcrev3 finding F-4).
- **The union over compile attempts.** The stamp lists the set iff ANY attempt of the
  compile consulted it (a pcrec reader asked or a kit row read it), not only the final
  attempt (D167 addendum 3; window_contract.md §3.7.3a).
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
- the transition's `DEFAULTS.log` row and `movers/<seq>.tsv` (§2.1, §8.4) [r2 n9].

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
  stamp is empty (§3.5). The OR is computed once, at the render point after `mf_art_end`
  (window_contract.md §3.7.3a), over the union of every compile attempt's asks (D167
  addendum 3), and `consulted` is layer-invariant there (the same boolean under every
  layer setting). The stamp's CONTENT was fixed when the set was LOADED, which is
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
Revision 1 named the kit facts but put them in no landing bar. They are now SIX requests
(revision 3 adds R-MS6, [r2 M7]). M0's trigger is R17-b′ landing WITH R-MS1, R-MS2, R-MS3,
R-MS5 and R-MS6. R-MS4's keys and fired-rows section are M0's too, and its safe
directions are M2's:

| id | the request (facts, D157) | landing bar | needed by |
|---|---|---|---|
| R-MS1 | `mf_measures` on `mf_art_begin` as §4.1 states (kit rows only, no `status`; NULL = no set) | the kit's tests run every finder row with NULL, with a synthetic set lacking each key in turn (the row skips to its `unpaid` pick or the next row), and with the full set; a kit row never reads a `pcrec.` key | M0 |
| R-MS2 | `consulted` out of `mf_art_end` (§4.2) | a kit test with a compile whose sites read no set key → false; one row that reads an ABSENT key → true; one that reads a present key → true. pcrec's S945 (§8.5) reaches it | M0 |
| R-MS3 | `mf_form_hash(form_id)` over the canonical instance (§2.4), and the form ids the kit's cards name in `deps` | the hash is unchanged under a zero-mover kit refactor (renamed helper, comment edit) and changed under a one-instruction body edit, both as kit fixtures; every form id a kit card names resolves | M0 (staleness listing) |
| R-MS4 | the kit's READER DECLARATION: per finder-table row, the keys it reads and, per threshold key, its SAFE direction (`max`/`min`/`none`: the side of its conservative or `unpaid` pick), as data the kit's listing exposes in [LIST-TABLES]' census shape (§5.4); and, per artifact, which finder rows fired per site, as the `--emit-facts` section `memfn` (§4.5) | keys: every key a row reads is declared (the kit-side half of §8.6's ⊆ check); directions: each declared direction agrees with the row's comparison operator by a kit test | keys M0 (the listing's readers); directions M2 (the envelope) |
| R-MS5 | the kit's METHOD CARDS for its quantities (§7.2), as a section TSV in the kit tree, versioned `kit-grid@N` | each quantity R17-b′ §3.2 lists has a card; grid1's and grid2's rows are on-card (`make test-measures` §8.2) | M0 (the first committed set must be on a card) |
| R-MS6 [r2 M7] | a HARNESS-ONLY arm-entry counter: under a lever reached only through `build/pcrec-harness` (the reserved internal name prefix and one-global fence of compound.md §A.11), each dispatch arm the kit emits increments a per-arm counter, exported under the reserved prefix with the arm's kit row id. The default emission is byte-identical with the lever off. pcrec states that it needs arm REACH; HOW the kit counts is the kit's (D157) | the lever off → zero movers on every emit_sweep arm; the lever on → each fired row's arm counts ≥ 1 on a kit fixture that enters it, and 0 on one that does not | M0 (§8.1's REACH floor) |

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
- `compiler_mismatch`, `libc_mismatch` (D167 Q-R17P-14);
- `values_digest`;
- `source` (store | `-I` file);
- `build_default_overridden` (§7.5).

### 5.2 `--list-measurements NAME|FILE`: one set (canonical view + derived views)

**The CANONICAL view** is the bare `--list-measurements NAME` (also spelled
`--view=canonical`). It is exactly the set's own sections, `header`, `cards`, `rows`,
`cells` and `members`, written by the canonical writer. Under ROUND-TRIP IDENTITY (§9.6)
it IS a loadable set: `--list-measurements=zen4-grid2 > f.tsv`, then `--measures=f.tsv`,
stamps the same `id@rev:digest`. `f.tsv` fails the name grammar, so it is a FILE under
§3.2's shipped rule. Revision 2's rule refused this very example [r2 M3c]. A committed set file equals its own canonical view
(§9.6, R4).

**DERIVED views** are separate (`--view=decoded`, `--view=readers`, `--view=stale`). They
are never part of the canonical view, and the loader REJECTS a file carrying any of those
section names (§9.5):

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
- **The cross-check.** For a key with an AGREED derived direction, the card's `env` (the
  method's declaration) must equal it. If it does not, `make test-measures` fails, naming
  the key, the card and the rows. Two declarations from two owners' artifacts must agree,
  which neither can satisfy by construction.
- **An EXCLUDED key [r2 n8]** has no derived direction to compare with. The cross-check
  skips it, and `test-measures` prints an always-printed INFO line per excluded key: the
  card's `env`, the word `excluded`, and the disagreeing rows. The exclusion is visible
  where the card claims a direction, and it is never a failure, because a disagreement
  among readers is a property of the readers and not an error of the card. Revision 2
  required `env` to equal a direction that does not exist for these keys, so every
  excluded key would have failed.
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
- **Its reader and writer are §9's PARTS plus the measures row** (`src/core/ksrc.c`,
  `src/core/ks_measures.c`), compiled into the driver as source with the driver's own
  malloc/stdio adapters and a one-row table [r2 M8]. That is allowed because the parts
  include only libc, `<dirent.h>` and `core/ksrc.h`, and the kinds table, which names
  the `.rxt` reader, is not among them (§9.2). Revision 2 compiled "the module", and its
  kinds table would have pulled in the `.rxt` parser, `Arena` and `StrBuf`. S989's link
  check holds the line.
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
adapter, committed, so the check runs on any box).

**Every set needs its own capture [r2 n10].** The generated subjects depend on THAT set's
L\* and W. So every new committed set, and every edit to a synthetic set, needs a new
`match-at` capture of its boundary subjects in `oracle_store/`. That capture is part of
the set's landing bar (§10.1). It needs the box with the local libpcre2 10.46 adapter
(the Linux dev box; docs/testing.md "The boxes"). A set landed without it fails
`test-measures-answers` as STOREUNCOVERED, the C3 tier's own clean-miss bucket, and never
falls back silently to an unchecked subject. The artifact is compared with the
oracle, not with another artifact, so the control shares no source with the subject
(learnings §3). A secondary arm compares artifacts built under two sets on the same
subjects, a differential that catches the case where both are wrong the same way.

**The REACH floor per dispatch ARM [r1 msc1-5, r2 M7].** It is a run-time counter, not a
compile count. The dispatch arms are KIT-emitted text (D157, D161 add. 14), so pcrec
cannot place a counter in them. Revision 2's lever, which "compiles a counter increment
into each emitted dispatch arm", had no owner:

- **The counter is the kit's, by request R-MS6 (§4.4).** The artifact is built through
  `build/pcrec-harness` with a harness-only lever, `--harness=reach-dispatch`. It follows
  compound.md §A.11's `--harness=no-compound` precedent: a reserved-name internal entry,
  fenced by the same one-global check. The lever asks the kit for its arm counters.
  pcrec reads the exported counts and never writes into kit text.
- **The admitted-arm list is the kit's FIRED-ROWS fact**, the `memfn` `--emit-facts`
  section of R-MS4 (§4.5): per site, which finder rows fired under this set. Revision 2
  derived it "from the set's rows by the python parser". Knowing which arm a row admits
  needs the row's PREDICATE, and R-MS4 declares only keys and directions. So python would
  have re-implemented the kit's selection, the method presumption D157 forbids.
- **The fired list is checked against the `dispatch` set's CONSTRUCTION**, not against
  itself. `dispatch` prices every pay rule to pay and puts every crossover at a small
  length. So every reader row that §5.4's census declares as reading a dispatch key
  (M16-M18 and the crossovers) must appear among the fired rows of some sampled site. The
  python check joins the census TSV with the facts section. A declared reader that never
  fires under `dispatch` FAILS, naming the row. This is the control: the census
  (declarations) and the fired-rows section (emission) come from two different kit
  outputs.
- **The floor.** Per synthetic set, every fired row's arm must count ≥ 1 over the
  population. Zero reach for a fired arm FAILS ([MECH-REACH]).

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
- the pre-parse is compared with a fresh library parse (findings tests §2/§3's shape).
  Both sides of that compare run the one C reader, so it catches a stale `.inc` and
  nothing about the reader itself. The reader's INTERPRETATION is checked by §9.6's R5
  against the independent python parser [r2 M3a];
- `PROVENANCE.md`'s and `index.tsv`'s `file_sha256` are compared with a fresh
  `hashlib.sha256` of `set.tsv` (the sha is KEPT, now with its checker);
- the default pointer table is compared with `DEFAULTS` read by awk (S947, §8.5);
- `DEFAULTS` equals `DEFAULTS.log`'s last row per class, read by a second awk [r2 n9].

### 8.4 The mover census, at landing [r1 msc1-1, msc1-9, r2 M4, n9]

This is the mechanism for D166's "selections move automatically, with a mover census in
the same commit". It is the `measures` arm of `scripts/emit_sweep.py`'s data mode
(§9.3), which serves every knowledge kind. Revision 2's `knowledge_census.sh` is
withdrawn [r2 M4]. `emit_sweep.py --data measures OLD NEW` does the following:

1. It compiles emit_sweep's pinned streams under `--measures=OLD` and `--measures=NEW`,
   with one working binary on both sides. The two sides differ only by the data argument.
2. It strips the stamp line (and the `rx_info.measures` initializer) and compares emitted
   bytes. That is emit_sweep's existing normalization.
3. It records, per artifact, the `*_WHY`/ladder tokens and any REFUSAL, under both sets
   [r1 msc1-9]. emit_sweep's stderr and tally streams already do this. A set can move a
   near-cap artifact across a size cap or onto another rung, and that is a mover even
   when the selection the set feeds did not change.

Its output is `measure_store/movers/<seq>.tsv` for the `DEFAULTS` transition being made
(§2.1):

- the artifact id (emit_sweep's stream and pattern key);
- old and new byte hashes;
- old and new tokens and refusal;
- the attribution: the ATTRIBUTION stream's fired reader rows (§9.3) whose declared keys
  have different values in OLD and NEW.

The population is emit_sweep's own pinned streams and their reach floors (§9.3). There is
no second population file.

**When the census is verified.** Only in the commit that changes `DEFAULTS` (a new
default, a flip, or a rollback). There the landing lane runs `make test-measures-census`,
which re-runs the data mode and requires byte equality with the new `movers/<seq>.tsv`.
This is part of that commit's delivery bar.

**What every build checks**, with no git history needed (CI is shallow):

- the structure: every `DEFAULTS.log` row after a class's first names a `movers/<seq>.tsv`
  that exists;
- each movers file's header `old`/`new` digests equal its log row's, and `index.tsv`'s;
- its `code_commit` names a commit (a 40-hex string, not checked for ancestry).

Revision 1 re-ran every set's census at HEAD on every build. That reds forever once any
later code moves a selection, or else forces edits to an immutable file.

**Re-pinned in the same commit, found by grep:** the abi readers (§3.6), the identity
gate's (B) pin and the EMITTED_BYTES readers.

### 8.5 Sabotage plan

S943-S963 are allocated (main's ledger: S943-S952 revision 1, S953-S963 revision 2).
S983-S990 are PROPOSED by revision 3 [r2]. They are main's next free ids as of
`063b4a4b4`, past S964-S980 (R-21); the manager allocated them to this lane (renumbered from S981-S988). Each has a REACH counter (the number of times the planted branch executed
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
| S952 | the census population shrinks silently (a stream or class skipped) [r1 msc1-11; RE-AIMED r2 M4] | emit_sweep's own per-stream REACH floors (its pinned populations), which the data mode inherits: a stream compiling fewer artifacts than its floor fails. No second manifest |
| S953 | a fitted row's value edited | §8.2(b) |
| S954 | a ratio row computed against a non-unit row | §8.2(c), exact compare |
| S955 | a row off its card (n below `launches × rounds`) accepted | §8.2(f) |
| S956 | the reach lever disconnected: pcrec never reads the kit's R-MS6 counters (they read 0) [RE-AIMED r2 M7] | §8.1 REACH floor reads 0 for a fired arm on the `dispatch` set |
| S957 | a derived row with a NULL input written non-NULL | §8.2(d) |
| S958 | a `-I` file whose header `id` differs from NAME accepted | the CLI fixture (§3.2) |
| S959 | `MOVERS.tsv` omits refusal/token changes | a near-cap synthetic pair of sets whose only difference re-rungs one artifact; the census must list it |
| S960 | the envelope ignores a reader that disagrees on direction | §6.2's exclusion listing; §8.2(e) |
| S961 | the canonical writer omits the `cells` section ([KNOW-SRC]) | R3 (§9.6). R1 and R2 both stay green, which is why R3 exists |
| S962 | a derived section (`stale`) written into the canonical view, or accepted by the loader | the loader-rejects fixture: a `--view=stale` dump fed to `--measures=` must refuse naming the section; R4 on the store |
| S963 | emit_sweep's data mode drops the attribution for one kind (the `analysis` arm writes it empty) [RE-AIMED r2 M4] | K0's findings fixture change, whose attributable artifacts are hand-listed; an empty attribution on a moved artifact fails |
| S983 [r2 M3a] | a SYMMETRIC column swap: the C reader resolves `noise_e6` into the `abs_ns_e6` field and the canonical writer writes that field back under `noise_e6` | R5 (§9.6): the decoded view's `abs_ns` ≠ the python decode. R1-R4 all stay green, which is the point of the row |
| S984 [r2 M3b] | the analysis canonical writer drops every `serves … when … via` declaration consistently | R3 (§9.6) with `analyze/`'s reader as the independent side; `rows_digest` does not cover `serves`, so R1 stays green |
| S985 [r2 M2] | the measures kind row's `s2_mismatch` reads `fallthrough-note` (a mismatched `-I` file skipped silently) | the CLI fixture of S958, and `tests/findings/res_fixtures.py` unchanged for the analysis row |
| S986 [r2 M5] | `ks_digest` hashes the analysis stamp domain without its trailing NUL | K1's shipped-digest pin: every `_FINDINGS` stamp and `rows_digest` of the three shipped bundles and the `-I` fixtures, byte-identical; emit_sweep's stamp-carrying streams |
| S987 [r2 M7] | the `memfn` fired-rows section omits one row under the `dispatch` set | §8.1's construction check: a declared dispatch-key reader that never fires fails, naming it |
| S988 [r2 n5] | the shadow check keyed on `id` alone (a FILE with a committed id and an uncommitted rev accepted) | the CLI fixture `id zen4-grid2`, `rev 7`, rev 1's digest: must refuse |
| S989 [r2 M8] | `ksrc.c` includes `core/internal.h` (the parts pick up the compiler's types) | the dependency check (§9.2): `ksrc.c`'s include list is libc + `core/ksrc.h` only, and `pcrec-measure` links with no `pcrec_`-prefixed symbol outside the parts and the measures row (`nm -u`) |
| S990 [r2 M1] | the evaluator-params item digest skips its last row | R1 and R5 on the `evaluator-params` fixture (§9.11) |

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

## 9. [KNOW-SRC]: ONE knowledge-source module and ONE data-mover census, built FIRST [r1 msc2-9, msc1 U1, r2 M1-M8]

Frank endorsed this unification on 2026-10-14: "i like the consistent data tool idea ...
with consistent loader". It is filed as plan row [KNOW-SRC]. This section is that row's
design. It is BUILT FIRST, implement-then-replace onto the analysis-object loader at zero
movers, before any [MEASURE-SET] stage (§9.8, §10.1). [MEASURE-SET]'s M0 then adds a kind
row; it does not build a loader.

### 9.1 The family [r2 M1, M6, n2]

Each member is a named, versioned, provenanced body of knowledge, loaded by name or path.
Most are stamped into what they shape. The plan row RULES four kinds (Frank, 2026-10-14);
revision 2 listed three [r2 M1]. The `lib` reference resolver is a fifth, resolve-only
member that revision 2 left unplaced [r2 M6]:

| member | content | loaded by | digests: ITEM / STAMP (§9.2 part 5) | store |
|---|---|---|---|---|
| the analysis object (D162, `--analysis`) | counts with derivations, an `include` chain, `.rxt` blocks | `--analysis` (NAME only), the `analysis` config line, `-I DIR/<n>.rxt`, the store | ITEM `rows_digest` (domain `pcrec-find-rows-1\0`). STAMP per query (domain `pcrec-find-1\0`, then the query and a NUL), rendered as `<PREFIX>_FINDINGS` + `rx_info.findings` | `src/findings/*.rxt`, embedded text + pre-parse (findgen.c) |
| measurement sets (this note) | keyed integer rows, cards, cells | `--measures` (NAME, NAME@REV or FILE), the `measures` config line, `-I DIR/<n>.measures.tsv`, the store | ITEM = STAMP = `values_digest` (domain `pcrec-meas-1\0`), rendered as `<PREFIX>_MEASURES` + `rx_info.measures` | `measure_store/`, embedded text + pre-parse (ksgen) |
| [TABLE-JUDGE]'s picks file | (cell, table, row, pick) plus arm timings | a FILE operand of the judge | ITEM a row digest (domain `pcrec-pick-1\0`). No artifact STAMP: the judge's report header carries the item digest | none (FILE only) |
| the EVALUATOR PARAMETER TABLE ([REGIME-EVAL]) [r2 M1] | the evaluator's verdict-changing constants: the G1-G4 bars, the regime caps, the outlier thresholds, the frozen population totals | a FILE (the kit's judge mode; the canonical view through the module's harness driver, §9.2 part 6) | ITEM a row digest (domain `pcrec-eval-1\0`), which IS the PREREG HASH posted to main before a judge slot. No artifact STAMP: its "stamp" is that prereg commitment | none (committed in the kit's tree beside the evaluator) |
| `lib` references (resolve-only) [r2 M6] | a `.rxt` library a source names by `lib "path"` | the `.rxt` source's `lib` line | none | none today; the reserved `lib <store-name>` form is [LIB]'s store (U4) |

- **Why a fourth kind and not a set.** The evaluator's constants are not measured
  decision inputs. No selection reads them, and they change verdicts, not bytes. The
  placement rule (§9.1a) sends them to a kind of their own. That kind has no artifact
  stamp, so its digest has a different role from the other kinds' (§9.2 part 5).
- **Why `lib` is a member.** `src/parse/rxt_source.c:4283-4340` resolves `lib "path"`
  over the source's directory and then each `-I` directory, with its own chain text
  (`lib_chain_text`), over the SAME `-I` list the analysis resolver reads
  (`cli/main.c:1812-1818`). It is a third resolver, and it has ALREADY drifted from the
  analysis one. It probes with `path_is_file(join_path(...))`, where `rxt_find.c`
  deliberately replaced that probe with `dir_has_exact` so that a case-insensitive
  filesystem cannot answer `log` with `Log.rxt` ([r2 M-S6], `rxt_find.c:9-12`). That is
  the drift §9.4 predicts ("they agree today and drift tomorrow"). Moving `lib` onto
  `ks_resolve` makes the difference a column value (`entry_match`, §9.5) that the
  listing shows, rather than a second copy of the loop. K1 keeps the shipped
  `probe-exists` value, so the move is zero-mover. The fix is finding F12 (§11), its own
  caller-visible change.
- **Limits (`limits.def`) are not a loadable kind.** They share the census (§9.3),
  because a limits default change moves bytes the same way a data change does.
  emit_sweep's `-D` limit VARIANTS already build the two sides. A read-only `limits`
  kind row is unlock U3, filed.
- **`analyze/` is a deliberately independent TWIN, not a member [r2 n2].** By charter
  `pcrec-analyze` is zero-dependency, with its own bundle-text writer and reader and its
  own SHA-256 (`analyze/CLAUDE.md`). It cannot call the module and must not. Its
  independence is what makes it R3's control for the analysis kind (§9.6). It is the one
  place the analysis format deliberately exists twice, and the module's "each piece
  exists once" does not include it.

Revision 1 built the second member as a copy of the first. It had a second name grammar, a
second `-I` probe, a second embed path, a second digest and stamp, and a second census
script. That is the parallel mechanism `pcrec-general-mechanisms-not-special-cases`
forbids, and the third and fourth members are already ruled.

### 9.1a The placement rule, as a first-match table [r2 M1]

The plan row's rule ("compiler numbers -> limits.def; measured decision numbers ->
measurement sets; harness thresholds -> a [KNOW-SRC] kind") is a declared first-match
table (`pcrec-decisions-as-first-match-tables`). A number is placed by the FIRST row that
matches:

| row | the number is … | it lives in | example |
|---|---|---|---|
| P1 | MEASURED, and read by a compile-time selection | a measurement set (§1) | β by shape, L\*, the M16-M18 charges |
| P2 | read by the compiler, and CHOSEN rather than measured (a D149 constant: a cap, a bound, a default) | `src/core/limits.def` | `PCREC_MAX_EMIT_BYTES`, the step budget |
| P3 | read only by a harness, evaluator or checker, and it changes a VERDICT | a [KNOW-SRC] kind of its own: today `evaluator-params` (§9.11) | the G2 regime caps, the G3 outlier bars |
| P4 | none of the above | REFUSED: no home until its reader is named | a constant "for later" |

P1 comes before P2 because a measured number that a selection reads is a set row even if
a person once chose its first value (D149's measured branch). P4 is the row that keeps
the table total. A card's `gate_e6` (§7.2) matches P3 and is a field of the owner's card
table, which is that kind's file for the install tool. Making the gate itself measured
is §10.4's "D149 constants as measured rows" unlock.

### 9.2 The module: kind-independent PARTS in `src/core/ksrc.c`, the kinds table at the library tier [r2 M8]

Revision 2 put the kinds table inside the module it called dependency-free. A table in
`src/core` naming the analysis row's `.rxt` reader avoids the INCLUDE but not the LINK
edge, so `pcrec-measure` would have linked the `.rxt` parser, `Arena` and `PcrecSb`
[r2 M8]. That contradicts the `analyze/` zero-dependency precedent §7.1 cites, and
`encoding_data_layout.md` §2 treats a measured `core → enc` back-edge of the same shape
as a defect. Revision 3 separates the two:

- **The PARTS**, `src/core/ksrc.c` + `src/core/ksrc.h`. These are the reader/validator,
  the resolver, `ks_pick`, the digest and stamp builders and the listing writers. They
  hold NO kinds table and include only libc, POSIX `<dirent.h>` (for the exact-entry
  probe) and `core/ksrc.h`. They allocate through a caller-supplied `KsAlloc`, write
  through a caller-supplied `KsOut`, and report errors in a fixed-buffer `KsErr`. None of
  them sees `Arena`, `StrBuf`, `Ctx` or `pcrec_error`, which all live behind
  `core/internal.h` and pull in the compiler (`arena.c` and `sb.c` include it).
- **The ROWS.** One TU per kind defines that kind's `KsKind` object:
  - `src/parse/ks_analysis.c` wraps the `.rxt` reader, so the parse layer registers the
    analysis row;
  - `src/core/ks_measures.c` uses the parts only;
  - `src/parse/ks_lib.c` is the resolve-only row;
  - picks and evaluator-params land when their kinds build (§9.8, OQ-1).
- **The TABLE** `ksrc_kinds[]` lives in `src/core/ksrc_kinds.c`, which only libpcrec
  compiles. It assembles the rows. The library tier already links core to parse
  (`compile.c:2471` calls `pcrec_find_resolve`), so this adds no new edge to libpcrec,
  and the parts stay edge-free.
- **What `pcrec-measure` compiles** (§7.1): `ksrc.c`, `ks_measures.c` and its own
  one-row table in `measure/`, with malloc/stdio adapters for `KsAlloc`/`KsOut`. Nothing
  else from `src/`. The dependency CHECK (S989) is a grep of `ksrc.c`'s and
  `ks_measures.c`'s include lines (libc, `<dirent.h>`, `core/ksrc.h` only) plus
  `nm -u` on the linked `pcrec-measure`: no `pcrec_`-prefixed symbol outside the parts
  and the measures row.

```c
/* src/core/ksrc.h — the kind-independent parts (libc + <dirent.h> only). */
typedef struct { void *(*alloc)(void *ctx, size_t n); void *ctx; } KsAlloc; /* zeroed */
typedef struct { int (*write)(void *ctx, const char *p, size_t n); void *ctx; } KsOut;
typedef struct { char msg[256]; } KsErr;

/* One digest ROLE [r2 M5]: domain BYTES (literal, grandfathered, explicit length because
 * the shipped tags hash their NUL), an optional sub-key, then the kind's own row fold. */
typedef struct {
    const unsigned char *domain;     /* NULL = this kind has no such role */
    size_t      domain_len;          /* e.g. 13 for "pcrec-find-1\0"; 18 for "pcrec-find-rows-1\0" */
    uint8_t     subkey;              /* KS_SUB_NONE | KS_SUB_QUERY: the query's bytes, then NUL */
    uint64_t  (*fold)(uint64_t h, const void *doc, const char *subkey_val);
} KsDigest;

/* One knowledge kind: a row of the closed kinds table. Every per-kind divergence the
 * resolver, the listing and the round trip have is a COLUMN here [r2 M2, n3]. */
typedef struct {
    const char *kind;           /* "analysis", "measures", "picks", "evaluator-params", "lib" */
    const char *suffix;         /* ".rxt", ".measures.tsv", ".picks.tsv", ".eval.tsv", ".rxt" */
    uint8_t     stops;          /* KS_STOP_SRCDIR | KS_STOP_S1 | KS_STOP_DIRS | KS_STOP_STORE */
    uint8_t     flag_classify;  /* KS_CLS_NAME_ONLY | KS_CLS_NAME_ELSE_FILE | KS_CLS_FILE_ONLY */
    uint8_t     list_classify;  /* the same domain, for --list-<kind> X */
    uint8_t     revs;           /* 1: NAME@REV is accepted (and is a NAME, §3.2) */
    uint8_t     s2_mismatch;    /* KS_S2_FALLTHROUGH_NOTE | KS_S2_REFUSE */
    uint8_t     s2_multi;       /* KS_S2_REFUSE for every kind today */
    uint8_t     entry_match;    /* KS_ENTRY_EXACT | KS_ENTRY_PROBE_EXISTS [r2 M6] */
    uint8_t     bare_view;      /* KS_VIEW_CANONICAL | KS_VIEW_SHIPPED [r2 n3] */
    uint8_t     r4;             /* KS_R4_REQUIRED | KS_R4_EXEMPT [r2 n3] */
    uint8_t     list_surface;   /* KS_LIST_CLI | KS_LIST_HARNESS (no CLI flag) */
    const char *cli_flag, *cfg_line, *list_flag;   /* NULL where the kind has none */
    KsDigest    item;           /* identity of the loadable item: R1, the shadow rule, the census */
    KsDigest    stamp;          /* what a compile consumed; .domain NULL = no artifact stamp */
    int  (*parse)(const KsAlloc *, const char *text, size_t len, void **doc, KsErr *);
    int  (*validate)(const void *doc, KsErr *);
    int  (*write_canonical)(const KsOut *, const void *doc);   /* §9.6 */
    int  (*write_decoded)(const KsOut *, const void *doc);     /* §9.6 R5 */
    const char *const *derived_sections;  /* section names the loader REJECTS, §9.6 */
    const KsStore *store;       /* embedded text + pre-parse, or NULL */
} KsKind;
```

The parts are six, and each exists once:

1. **The section-TSV reader/validator** (`ks_tsv_read`). It reads `table_contract.md`'s
   §2/§4 shape from a buffer, with no filesystem access:
   - `#section` lines;
   - the per-section header;
   - the field-count truthfulness rule (§5¶1);
   - columns resolved by name;
   - unknown trailing columns ignored.

   It returns sections as rows indexed by header name. A kind's `validate` adds that
   kind's rules (§1.6 for measures). The analysis kind's `parse` is its existing `.rxt`
   reader, registered from `src/parse/ks_analysis.c` (§9.9 reconsiders that format).
2. **The name resolver** (`ks_resolve`) [r2 M2]. One loop, driven by the kind row's
   columns:
   - the name grammar (`pcrec_find_name_ok` today), plus `@REV` where `revs = 1`;
   - classification by `flag_classify` or `list_classify` (§3.2): `name-only` (the
     shipped `--analysis`, `cli/main.c:1103`), `name-else-file` (the shipped
     `--list-analysis`, `cli/main.c:1808-1809`, `2233-2236`, and both measures
     surfaces), `file-only` (picks, evaluator-params);
   - the stops: `KS_STOP_SRCDIR` (the source's own directory, `lib` only), S1 the
     compiling file where the kind allows it, S2 `-I DIR/<name><suffix>`, S3 the kind's
     store;
   - the entry match at S2, by `entry_match`: `exact` (`dir_has_exact`) or
     `probe-exists` (`lib`'s shipped `path_is_file`, kept for zero movers, F12);
   - an S2 file naming something else: `s2_mismatch` (`fallthrough-note` for analysis,
     with its note text; `refuse` for measures, §3.2 says why); two or more items in one
     file: `s2_multi = refuse`;
   - the refusal text naming the stops searched (`stops_text`).

   These are `rxt_find.c`'s `probe_dir`, `dir_has_exact`, `stops_text` and
   `find_bundle`'s stop loop, and `rxt_source.c`'s `lib` search, today. The analysis
   `include` chain (the self-name `#include_next` and the terminal `default`) stays in the
   analysis kind: it is that kind's semantics, and the other kinds refuse it. Revision 2
   made "an S2 file's declared name must equal NAME" a SHARED refusal and the
   classification a shared `/` rule. Both contradicted the analysis kind's shipped,
   spec'd behaviour (`docs/spec/findings.md` S2 row; `rxt_find.c:12-15`), so K1's
   "zero movers" was false as specified [r2 M2]. As columns, the shipped values are
   reproduced exactly, and the difference between kinds is listed, not hidden.
3. **Fill-only precedence** (`ks_pick`) [r2 n11]. For a kind with both a CLI flag and a
   config line, it applies D93 fill-only: the file's value wins for its targets, and the
   flag fills targets that name none. It RETURNS the decision and any disagreement as data
   (`{chosen, source, flag_value, file_value}`) and prints nothing. The CLI prints
   `tune`'s note through `cli_err` with the kind's own flag and line names, as
   `apply_target` does today (`cli/main.c:1458-1474`). The library has no stderr, so
   moving the print into `src/core` would have made the library print a CLI note.
4. **The embed generator** (`scripts/ksgen.c KIND OUT FILE...` plus
   `scripts/embed_text.sh`). It writes, from the committed text, the kind's text table
   and its PRE-PARSE. It links a stage-0 build of the parts and the kind's row (the
   `PCREC_FIND_STAGE0` trick, generalized; the analysis row brings the `.rxt` reader, as
   findgen does today). One Makefile pattern rule (`gen-<kind>`, all called from
   `gen-tables`) replaces `gen-findings`' recipe. Python never writes an embedded byte
   (§2.3).
5. **The digests and the stamp** (`ks_digest`, `ks_stamp`) [r2 M5]. Each kind row has
   TWO digest ROLES, because the analysis kind already has two digests that mean
   different things (`docs/spec/findings.md` 8.1¶1: `rows_digest` is "a DIFFERENT hash
   from the stamp's"):
   - **ITEM**: the identity of the loadable item. R1 (§9.6), the shadow rule (§3.3), the
     index views and the census read it. It is `rows_digest` for analysis,
     `values_digest` for measures, and a row digest for picks and evaluator-params.
   - **STAMP**: what a compile consumed. For analysis it is per QUERY. The shipped query
     is `byte-rate`, over the 256 derived ppm values (`src/core/findings.c:332-344`,
     `docs/spec/findings.md` 5¶6). `findings/design.md` §7's table gives later queries
     their own consumed values (derived values for some queries, rows for others), so
     the role carries the query as a sub-key. Its stamp grammar is
     `query=bundle:digest`.
     For measures it is the item digest itself (stamp-on-load, §3.5). Picks and
     evaluator-params have none (`stamp.domain = NULL`).
     The stamp text is rendered ONCE per compile, at the single render point after
     `mf_art_end` (window_contract.md §3.7.3a), from the kit's layer-invariant `consulted`
     ORed with the union over compile attempts (D167 addenda 2 and 3); `ks_stamp` builds
     the text and does not choose when it is written.

   `ks_digest(role, doc, subkey)` is FNV-1a-64 over the role's DOMAIN BYTES, then the
   sub-key's bytes and a NUL where `subkey = KS_SUB_QUERY`, then the role's `fold`. It
   is findings.c's one `fnv1a`, kept once, and it renders as 16 lowercase hex.
   **Domains are LITERAL byte strings, never derived.** Revision 2 implied a
   `pcrec-<kind>-<N>` pattern that the shipped domains do not follow (`find`,
   `find-rows`, `meas`, `pick`). `pcrec-find-1` CANNOT be renamed: every
   `<PREFIX>_FINDINGS` stamp would move, which is an abi event as a side effect. The
   shipped domains are grandfathered byte for byte, NUL included. The shipped tags are
   hashed with `sizeof`, which counts the terminator (`findings.c:334`, `:348`), so
   `domain_len` is explicit. K1's gate pins every shipped digest unchanged (§9.7).
   **What `rows_digest` does not cover** is `serves`, `include` and provenance. A writer
   that loses one of those keeps R1 green, which is why R3 and R5 are load-bearing for
   the analysis kind (§9.6, S984). `ks_stamp` builds the stamp grammar (EMPTY = nothing
   asked; otherwise the kind's item text) and the `rx_info` mirror string, the same
   bytes as the macro.
6. **The `--list-<kind>` shape** (`ks_list`). Every kind has the same four views, each a
   `table_contract.md` section stream:

   | view | spelling | content | an input? |
   |---|---|---|---|
   | index | `--list-<kinds>` (`--list-analyses`, `--list-measurements` bare) | one row per item reachable (store + `-I`), with `default_for`, item digest, source | no |
   | CANONICAL | `--list-<kind> NAME|FILE --view=canonical` | the item itself, written by `write_canonical` | YES (§9.6) |
   | derived | `--list-<kind> NAME|FILE --view=<v>` | the kind's derived views (measures: `decoded`, `readers`, `stale`; analysis: today's `chain`, `resolution`, …, plus `decoded`) | no |
   | per-target | `--list-<kind> FILE.rxt` | per target: the resolved item, its stop, its stamp, its lookups | no |

   What a bare `--list-<kind> NAME` prints is the `bare_view` column [r2 n3]:
   `canonical` for measures and `shipped` for analysis. The analysis value keeps today's
   output (the derived `chain`/`resolution`/… sections, `findings.md` §6) until the §9.9
   format decision. That decision is a caller-visible change either way, so the default
   view moves with it in one spec change, and the move is a one-cell edit.
   `--view=canonical` exists for every kind with a CLI surface from K3. A kind with
   `list_surface = harness` (picks, evaluator-params: no `pcrec` flag) gets the same
   views from the module's test driver, `tests/knowledge/ksdump`, which links the parts
   and the rows and is what `make test-knowledge` runs. Under `name-else-file`, a
   `--list-measurements` FILE whose name ends in `.rxt` is the per-target view, and any
   other FILE is one set. That is a spelling rule with no probe, like §3.2.

The kinds table is a declared first-match table (`pcrec-decisions-as-first-match-tables`).
[LIST-TABLES] lists it once that row opens. No flag is added for it before then.

### 9.3 The data-mover census: a MODE of `scripts/emit_sweep.py` [msc1 U1; Frank 2026-10-14; r2 M4, n4]

Revision 2 specified a new tool, `scripts/knowledge_census.sh`, with its own pinned
population (`tests/knowledge/census_population.tsv`) and its own artifact manifest. It
duplicated `scripts/emit_sweep.py` piece by piece [r2 M4]. emit_sweep already:

- builds two sides, including `git archive` stage builds with `-D` limit VARIANTS
  (`plain`, `lowsize`, `lowdfa`, `lowboth`, `lowthr`), which is exactly the limits arm;
- compiles PINNED populations over eight streams, with reach floors per stream;
- strips stamps, the normalization §2.4 already borrows;
- records refusals and stderr (stream 8) and tallies `*_WHY`/prefilter tags against
  pinned floors (`VARIANT_PINS`).

Revision 3 withdraws `knowledge_census.sh` and `census_population.tsv`. The census is an
emit_sweep MODE, `--data KIND OLD NEW`, and adds three pieces to the existing tool:

1. **Data-argument sides.** Both sides are ONE working binary, and the two sides differ
   only by a data argument:

   | KIND | OLD/NEW are | the two sides differ by | attribution |
   |---|---|---|---|
   | `analysis` | two versions of a bundle (a committed rev, or a path) | `--analysis=` (or `-I` dirs) for each version; for the shipped `default`, which is found by identity, two stage builds of the store text, through emit_sweep's existing two-build path | the lookup TRACE, cross-checked by the `_FINDINGS` stamp items (below) [r2 n4] |
   | `measures` | two sets | `--measures=` for each | the trace's pcrec readers, plus the kit's fired rows (the `memfn` facts section, R-MS4) whose declared keys differ in value; `consulted` for the kit's |
   | `limits` | two `limits.def` values for one limit | the limit's `--max-…` override as a data argument where one exists, else emit_sweep's existing `-D` VARIANT builds | the limit's readers as `--list-limits` names them, and the artifact's refusal or `*_WHY` token change |

2. **An ATTRIBUTION stream**, from the lookup trace (below).
3. **A movers-TSV writer.** It writes one shape with a `kind` column. For measures the
   output is committed as `measure_store/movers/<seq>.tsv` (§2.1, §8.4). For the other
   kinds the census goes in the commit message or a review file, as the change requires.

**The population** is emit_sweep's own pinned streams (1-4 always, and 6-8 where the change
can reach them) and their reach floors. There is no second population file, and S952
re-aims onto those floors (§8.5).

**Per-artifact attribution has ONE mechanism, the lookup TRACE [r2 n4].** A debug build's
accessor for each kind takes the READER's id (§8.6) and writes
`(artifact, kind, key, reader)` to a trace stream. The census joins that trace with the
OLD/NEW difference.

- Findings readers are already one accessor per question kind (findings.c's header), so
  their trace is one line at each.
- **The `_FINDINGS` stamp is the trace's cross-check, not a second attribution.** For
  every analysis artifact, the set of queries the trace records equals the set of
  (query, bundle) items its stamp carries. A disagreement fails the census and names the
  artifact. Two independent sources agree: the accessor side and the emitter's
  scaffolding. Revision 2's table said attribution was read from the stamp, and its prose
  said it was read from the trace. Revision 3 picks the trace and uses the stamp as the
  check.
- The kit's lookups are not traced key by key (§4.2). Its attribution is the fired rows
  from the `memfn` facts section (R-MS4).

The generalization of this to ANY world pair, with one movers shape for all of them (a code
revision, a limit variant, a data version, an option set), is unlock U1. It is filed and
not built (§10.4).

### 9.4 Why one module and not a shared helper file

A helper file shared by copy-and-adapt would keep two stop loops, two embed generators,
two precedence rules, two stamp grammars and two census scripts. They agree today and drift
tomorrow. The `lib` resolver is that drift, already present (§9.1) [r2 M6]. The
`compare_stack.md` §2 record is the house's measured instance: definitions that exist
more than once, each with its own agreement check. The module's parts and emit_sweep's
data mode make each piece exist once. The deliberate exception is `analyze/`'s twin,
which is kept independent as a control (§9.1).

### 9.5 What each kind sets [r2 M1, M2, M5, M6, n3]

Every per-kind difference is a cell here, which is the kinds table's content. Revision 2
had per-kind behaviour in prose that the table did not show: the S2 rule, the
classification, "bare is canonical", and "exempt from R4 by name" [r2 n3].

| column | analysis | measures | picks | evaluator-params | lib |
|---|---|---|---|---|---|
| suffix | `.rxt` | `.measures.tsv` | `.picks.tsv` | `.eval.tsv` | `.rxt` |
| stops | S1, S2, S3 | S2, S3 | FILE only | FILE only | SRCDIR, S2 |
| `flag_classify` | `name-only` (`--analysis`) | `name-else-file` | `file-only` | `file-only` | n/a (a `lib "path"` line is a path) |
| `list_classify` | `name-else-file` | `name-else-file` | n/a | n/a | n/a |
| `revs` | 0 | 1 (`NAME@REV`) | 0 | 0 | 0 |
| `s2_mismatch` | `fallthrough-note` | `refuse` (§3.2) | n/a | n/a | n/a (no name to mismatch) |
| `s2_multi` | `refuse` | `refuse` | n/a | n/a | n/a |
| `entry_match` | `exact` | `exact` | n/a | n/a | `probe-exists` (shipped; F12) |
| parse | the `.rxt` reader (unchanged; §9.9) | `ks_tsv_read` + §1.6 | `ks_tsv_read` + its own | `ks_tsv_read` + §9.11 | none (resolve only) |
| chain | `include`, terminal `default` | none (refused) | none | none | none |
| precedence | fill-only (D93) via `ks_pick` | fill-only (D93) via `ks_pick` | n/a (one operand) | n/a (one operand) | n/a |
| ITEM digest | `rows_digest`, `pcrec-find-rows-1\0` (18 bytes) | `values_digest`, `pcrec-meas-1\0` (13) | row digest, `pcrec-pick-1\0` (13) | row digest, `pcrec-eval-1\0` (13): the prereg hash | none |
| STAMP digest | per query, `pcrec-find-1\0` (13) + query + NUL | = ITEM | none | none | none |
| stamp | `query=bundle:digest;…` / `query=none` / empty | `id@rev:digest` / empty | the judge's report header | the prereg commitment | none |
| `bare_view` | `shipped` | `canonical` | n/a | n/a | n/a |
| `r4` | `exempt` (until §9.9) | `required` | `required` | `required` | n/a |
| `list_surface` | `cli` | `cli` | `harness` | `harness` | none |
| canonical view | a normalized `.rxt` bundle (§9.6) | the set file's own sections | the picks file's own sections | the file's own sections (§9.11) | none |
| derived sections the loader rejects | `chain`, `resolution`, `declarations`, `targets`, `decoded` | `decoded`, `readers`, `stale`, `sets` | `verdicts`, `decoded` | `decoded` | none |

The `lib` row exists so the resolver is one loop. It has no load, list or round trip of
its own: the file it finds is a `.rxt` library that the `.rxt` reader parses as a source.

### 9.6 ROUND-TRIP IDENTITY (Frank, 2026-10-14, [KNOW-SRC]) [r2 M3, M5, n3, n5]

**The rule.** For every kind, the listing's CANONICAL view of one item IS a loadable input
of that kind:

```
pcrec --list-measurements=zen4-grid2 --view=canonical > f.tsv
pcrec --measures=f.tsv --pattern ...      # f.tsv is a FILE (§3.2); stamps zen4-grid2@1:<same digest>
```

Section 3.3's shadow rule allows exactly this: a FILE whose (`id`, `rev`) is committed
with the SAME `values_digest` is the same set. Any other FILE with a committed `id` is
refused [r2 n5].

**The canonical writer** (`write_canonical`) is deterministic and total over a valid
document:

- the sections in the spec's order;
- the header keys in the spec's order;
- rows in canonical key order (§1.7, bytewise);
- integers in their one decimal spelling;
- one fixed first comment line naming the kind and the spec, and no other comments.

Free prose in a hand-written file is not carried. For measures, prose lives in
`PROVENANCE.md`. For analysis, that loss is one of §9.9's costs.

**The DECODED writer** (`write_decoded`, the `--view=decoded` derived view) prints the
LOADED document field by field: every section, every row, and every column under the name
the loader resolved it to, with each value as the loader interprets it (§5.2 for
measures). It is a derived view and never an input. It exists so that R5 can compare the C
loader's interpretation with an independent reader.

**The checks**, over every committed store item, every test fixture and every kind, as
`make test-knowledge`:

| check | statement | catches |
|---|---|---|
| R1 load→list→load | digest(load(list(load(x)))) = digest(load(x)), with digest = the kind's ITEM digest (§9.2 part 5) [r2 M5] | a writer that changes a VALUE the item digest covers |
| R2 list→load→list | list(load(list(load(x)))) = list(load(x)), byte for byte | a writer that is not a fixed point (order, spelling, an unstable field) |
| R3 structural | load(list(load(x))) = load(x) as DOCUMENTS, every section and every column, compared by an INDEPENDENT reader, not by the C loader | a writer that drops a section the digest does not cover, CONSISTENTLY. R1 and R2 are both blind to that: omit `cells`, and the digest (values only) and the second listing (also without cells) both agree |
| R4 committed = canonical | for every store item of a kind with `r4 = required`, list(load(file)) = the committed file's bytes | a store file that is not canonical (so the embed IS the canonical text, and the drift gate of §8.3 covers both) |
| R5 decoded = independent [r2 M3a] | for every store item and fixture, `--list-<kind> X --view=decoded` = the independent reader's decode of the FILE `x`, field by field | a reader/writer pair that is wrong SYMMETRICALLY, which R1-R4 cannot see |

**Why R5 [r2 M3a].** R1, R2 and R4, the drift gate (§8.3) and the pre-parse-versus-fresh-
parse compare all run the SAME C reader on both sides. A symmetric defect passes all of
them. For example, suppose the reader resolves `noise_e6` into the `abs_ns_e6` field and
the writer writes that field back under `noise_e6`. The text then round-trips
byte-identically. R1 and R2 stay green. R4 stays green. R3 stays green too, because it
compares the independent reader's view of `list(load(x))` with its view of `x`, and the
two texts are identical. Yet the loaded document is wrong. That is learnings §3's
pattern: the control shares its source with what it controls. R5 compares the C
INTERPRETATION with an independent reader of the original FILE, so a swap shows up as
`abs_ns` ≠ the file's `abs_ns_e6` (S983). For the analysis kind, R5 also requires
`--list-analysis`'s resolution digests to equal `tests/findings/findings_ref.py
bundle-digest` on the same files. That compare already exists in `tests/findings/` and
is named here as a gate.

**The independent reader, per kind [r2 M3b]:**

| kind | R3's and R5's independent side | why it is independent |
|---|---|---|
| measures, picks, evaluator-params | `tests/knowledge/ks_ref.py`: a python section-TSV parser and per-kind decoder written from `docs/spec/` (the shapes and the §1.6 code table), sharing no code with `ks_tsv_read`, `envelope.py` or `ksgen` | written from the spec, in another language, by a separate reader |
| analysis | `analyze/`'s own bundle-text reader (`parse_bundle`), extended at K3 to every section the canonical writer emits, with a `--dump-doc` mode that prints the document in R3's comparison shape | zero-dependency by charter (`analyze/CLAUDE.md`): it links nothing under `src/`, so it cannot share the C loader's code. It is the deliberate twin of §9.1 |

`findings_ref.py` cannot be R3's analysis side: it reads only `row` lines, by regex, and
R3 compares every section. **The K3 extension is priced:** `parse_bundle` reads today what
`pcrec-analyze` renders (the blocks, their provenance and the derived `serves`). The
addition is `include`, the hand-written `serves … when … via` declarations, and the
`--dump-doc` printer, plus `analyze/`'s own tests for them. It is about the size of one
`analyze/` command form. The alternative, a new python `.rxt` bundle parser, would be a
third reader of a grammar with two already, so it is not taken. S984 plants a canonical
writer that drops `serves`. `rows_digest` does not cover `serves`, so R1 stays green, and
R3 through `analyze/` catches the plant.

R3 is revision 2's addition to Frank's two checks, and R5 is revision 3's. Without R3,
the round trip can pass while losing data the digest does not cover (S961). Without R5,
it can pass while misreading data consistently (S983). R4 holds for `measure_store/`
from M0. For the analysis kind, `r4 = exempt` until §9.9 decides the format, because the
shipped bundles carry prose by design. R1-R3 and R5 run on it. The exemption is a column
value (§9.5), not a name in a script [r2 n3].

**Derived views are not inputs.**

- They are separate views (§9.2 part 6), never part of the canonical view.
- The loader REJECTS any file carrying a derived section name of its kind (§9.5's last
  row), naming the section and pointing at `--view=canonical`. So a derived dump fed back
  as an input fails loudly, rather than loading with extra sections silently ignored under
  `table_contract.md` §3¶2.
- Stale flags, reader rows, per-target lookups, the decoded view and the sets index are
  derived (S962).

### 9.7 Migrating the analysis loader: implement-then-replace, zero movers [r2 M2, M4, M5, M6, n1]

| step | what | gate |
|---|---|---|
| K0 | `ksrc.c` (the parts, §9.2) lands with the ANALYSIS and `lib` rows, implemented beside the shipped paths. emit_sweep's `--data` mode lands (§9.3), run on a findings fixture change and a limits fixture change | `make strict`; the dependency check (S989); the data mode reproduces a hand-made movers list on each fixture; S963 |
| K1 | the shipped paths become calls into the parts: `rxt_find.c`'s stop loop, `probe_dir`, `dir_has_exact`, `stops_text`, `pcrec_find_name_ok`, `rxt_source.c`'s `lib` search (`entry_match = probe-exists`), the `--analysis` fill-only decision (`ks_pick`; the note stays in the CLI), and findings.c's `fnv1a` behind `ks_digest`. The chain logic stays where it is. During K1 a debug build resolves every name BOTH ways and asserts equal results | ZERO MOVERS: `emit_sweep.py` over the corpus (all arms), byte-identical; `tests/findings/` and `--list-analysis`/`--list-analyses` outputs byte-identical; the refusal and fall-through-note texts byte-identical, witnessed by `tests/findings/res_fixtures.py` (the `-I` resolution fixtures: an S2 file of another name falls through with its note, a two-bundle file refuses, a `NAME`/`FILE` spelling of each classification) [r2 M2]; `lib` resolution byte-identical over `tests/rxtsource/`; the DIGEST PIN: every shipped `_FINDINGS` stamp and every `rows_digest` of the three shipped bundles and the fixtures, byte-identical (S986) [r2 M5] |
| K2 | the old functions are deleted; `findgen.c` becomes `ksgen analysis`; `gen-findings` is the pattern rule | `make gen-tables && git diff --exit-code` clean (the regenerated `findings_table.inc` byte-identical); the K1 gates again |
| K3 | the canonical and decoded views (`--view=canonical`, a normalized `.rxt` bundle writer; `--view=decoded`), `analyze/`'s reader extension and `--dump-doc` (§9.6), and `make test-knowledge`'s R1-R3 and R5 for the analysis kind | R1-R3 and R5 green over the three shipped bundles and the fixtures; S961, S962, S984 |

**K1's derived edit set and re-aims [r2 n1].** K1 and K2 delete or relocate `rxt_find.c`'s
stop loop, `dir_has_exact`, `stops_text`, `find_bundle` and findings.c's `fnv1a`. Sabotage
rows anchor there. On main (`063b4a4b4`), S309, S310 and S315 anchor in
`src/parse/rxt_find.c`, and **15** rows anchor in `src/core/findings.c`: 11 spelled
`SAB_FILE="…"` and 4 spelled `SAB_FILE='…'`. The re-check counted 11, because its grep
matched one quote style. That is this paragraph's argument in miniature: a hand count of
the rows a move touches misses rows. Following the start_table and dec_fallback
precedent, K1 DELIVERS:

- an edit-set file listing every function K1/K2 moves or deletes;
- the derived map from that edit set to every `SAB_FILE=` row whose anchor falls in it,
  each marked RE-AIM (the planted line moves into `ksrc.c` or a row TU) or RE-RUN (the
  anchor survives, and the row is re-run to show it still reaches);
- the moved READERS outside `tests/mech`, found by grep. The known one is
  `tests/registry/limits_check.sh:365`, which reads `PCREC_FIND_NTBL`/`NBUNDLES` "in
  `src/core/findings.c`". If the store's table moves into the module, that reader moves
  in the same commit.

The edit set is the input and the map is derived from it, so a row the hand list missed
cannot be lost.

There is no abi event: no emitted byte moves. K3 is a caller-observable addition (two
new views), so `findings.md` and `cli.md` get their spec hunks in K3's commit (D80).

### 9.8 Where [KNOW-SRC] sits in the build

K0-K3 complete before [MEASURE-SET]'s M0 (§10.1). M0 then adds the `measures` kind row, its
validator, canonical and decoded writers (the set's own sections), its store, and R1-R5
for sets. emit_sweep's `measures` data arm is M1's first use. [TABLE-JUDGE] adds the
`picks` row when it builds. The `evaluator-params` row lands when OQ-1 is ruled. Until
then the kit's `prereg.tsv` uses §9.11's canonical format from day one, as the plan row
requires, so adding the row later needs no migration of the file.

**The D77 trigger.** A second kind needs a loader (the measures kind, when [MEASURE-SET] is
scheduled). [KNOW-SRC] is therefore scheduled AHEAD of [MEASURE-SET] by the same trigger.
It is not built speculatively before that.

### 9.9 OPEN for the module's design: the analysis object's DATA format, reconsidered (Frank, 2026-10-14)

Frank asks that the analysis object's `.rxt` DATA input (D83; [DD-13]'s unified format)
be reconsidered against the module's section TSV. This is NOT decided here. The K steps
keep `.rxt`, so the question is off the critical path. The case, both ways:

**For moving the analysis kind to section TSV:**

- **One reader.** One input syntax for every kind: the module's reader, validator and
  canonical writer, with no `parse` pointer into `src/parse` from the core load path.
- **Round trip becomes the uniform case.** The canonical view would be the file shape, and
  R4 would hold for the analysis store too. Today it needs an exemption.
- **Half the shape exists already.** The analysis LISTING is already section TSV
  (`--list-analysis`' data-kind sections, `findings.md` §6), so the canonical and derived
  views would share a shape. `pcrec-analyze`'s output would be a section-TSV write. It
  would stay its OWN writer, because `analyze/` is zero-dependency by charter and cannot
  call the module; it is the deliberate twin of §9.1, and R3's control [r2 n2].
- **One generator.** `ksgen`'s analysis arm would stop needing the `.rxt` reader at stage
  0.

**For keeping `.rxt`:**

- **Inline analyses.** D83/DD-13 made an analysis a DATA block of the unified
  pattern-source format on purpose: a pattern file carries its own analysis inline (stop
  S1, `rxt_find.c`). A TSV has no place inside a `.rxt` without a block kind wrapping it,
  which is a second spelling of the same data.
- **The grammar is `.rxt`'s.** The `include` chain and the `serves … when … via`
  declarations are `.rxt` grammar. In TSV they become header keys and a declarations
  section, a re-spelling with the same semantics.
- **Hand-authored rationale.** The shipped `default.rxt` is mostly citable rationale
  (319 lines; the prose explains WHY the prior is independent of the bench, learnings §3),
  which a canonical writer drops. That prose would move to a PROVENANCE file.
- **Users already author `.rxt`.** User bundles (`log.rxt`, `weblog.rxt`, and any user's
  `-I` files) exist, and `[DD-13]`'s spelling is the manager's call under a format Frank
  framed as one file for patterns, tests and data.

**A middle form, priced.** Keep `.rxt` as the authoring and inline surface, and make the
section TSV the canonical view and a second accepted input. That costs two input
spellings for one kind, a parallel mechanism the house avoids. It would need its own
justification: that the inline case cannot be served by S2/S3 references.

**The migration cost if the format moves:**

- the three shipped bundles (697 lines), re-spelled, with their prose moved;
- the S1 inline stop: either withdrawn (a caller-observable removal) or kept through a
  wrapping block;
- `ksgen`'s analysis arm;
- `pcrec-analyze`'s writer and reader (both twins: they change with the format, and
  stay independent of the module) and `analyze/` tests;
- the `tests/findings/` fixtures;
- spec hunks in `findings.md`, `rxt_format.md` and `cli.md` (D80);
- user `-I` bundles, needing a converter or a deprecation period.

The artifact side can be ZERO movers. The `_FINDINGS` digest is over the DERIVED ppm
values (`findings.md` 5¶6), not the text, so the same counts in another spelling give the
same digest and the same bytes. The cost is all on the input and documentation side.

**Who decides.** It is the module's design to settle, with Frank. The format's semantics
are his; spelling is the manager's (`pcrec-dd13b-syntax-is-managers`). The trigger is K3,
where the analysis kind's round-trip exemption (R4) is the visible cost of keeping `.rxt`.

### 9.10 `--list-measurements` and [LIST-TABLES]

The listing's reader index is [LIST-TABLES]' census (§5.4). The `sets` index and the
canonical, derived and per-target views are `ks_list`'s for the measures kind (§9.2
part 6). The analysis listing moves onto `ks_list` at K1 for its resolution sections, with
byte-identical output.

### 9.11 The evaluator-parameter file's canonical format, from today [r2 M1]

The plan row says "until built, each kind's file uses the canonical format from day
one". The kit's `prereg.tsv` ([REGIME-EVAL], `memfn/docs/responses.md:2447`: committed
alone, its hash posted to main before the judge slot) is the live instance. It is bound
NOW, before the kind row exists. So that adding the row later needs no migration, the
file is a `table_contract.md` §4 section TSV with this shape:

```
# pcrec evaluator parameters (spec: docs/spec/evaluator_params.md)
#section header
#key	value
format	1
id	reval-r17bp
rev	1
owner	kit
evaluator	regime_eval@<ver>
rows	<count>
item_digest	<16 hex>
#section params
#key	unit	value_e6	note
kit.reval.cap.simd_on.s1	ratio	150000	G2: regime cap, SIMD on, S1
kit.reval.outlier.ns	ns	50000000	G3: outlier floor, per call
...
```

- **Keys** follow §1.3's grammar: an owner, a quantity, then tokens. The owner's own
  declaration orders the tokens. No placeholders.
- **Values** are integers in `value_e6` under §1.7's literal rounding rule. The units are
  `ratio` (a fraction × 10^6), `ns` (ns × 10^6; unit byte `0x05`, a new row of §1.6's table) and `count` (× 10^6, so an integer count
  is `n000000`), and each has a code in the spec's unit table beside §1.6's. A percentage
  bar is a `ratio`. There is no float, so two readers cannot disagree on a bar.
- **`note`** is free text. It is display only, and the digest does not cover it.
- **The ITEM digest IS the prereg hash.** It is FNV-1a-64 over the 13 domain bytes
  `pcrec-eval-1\0`. Then, for each `params` row in canonical (bytewise) key order, it
  takes the key, a NUL, the unit byte, and `value_e6` as int64 LE. This is §1.6's row
  digest with the status byte dropped, since a parameter has no status. It is a
  hand-written row digest like every other kind's. Deriving every kind's item digest
  from `write_canonical` plus a column list is unlock U2, filed (§10.4). The header's
  `item_digest` is self-checking, and `rows` counts the `params` section (K35).
- **"The report's prereg diff = the census tool's diff"** (the plan row) is emit_sweep's
  data mode with `KIND = evaluator-params` once the row exists. It is a keyed diff of two
  files' `params`, with no compile, since no artifact reads these values. Until the row
  exists, the kit's own diff of two committed `prereg.tsv` revs is that diff, written in
  the same keyed shape.
- **Who reads it** is OQ-1 (§10.6). The FORMAT and the DIGEST above are fixed either way.
  The kit adopts them in its next `prereg.tsv` commit, and main relays that by request,
  since `memfn/docs/requests.md` is main's to write.

## 10. Staged build, standing questions, lenses, unlocks, questions

### 10.1 Stages (each with its D77 trigger)

| stage | content | trigger |
|---|---|---|
| K0-K3 ([KNOW-SRC], §9.7) | the PARTS `ksrc.c` (libc only) with the ANALYSIS and `lib` rows, the kinds table at the library tier, and the dependency check; emit_sweep's `--data` mode (analysis and limits arms, the attribution stream, the movers writer); the analysis loader replaced at ZERO movers (the resolution fixtures, the digest pin, the derived edit set and re-aims); `findgen.c` → `ksgen analysis`; the canonical and decoded views, `analyze/`'s `--dump-doc`, and R1-R3 + R5 for the analysis kind; S961-S963, S984-S986, S989 | [MEASURE-SET] scheduled (a second kind needs a loader); built AHEAD of M0 (Frank, 2026-10-14) |
| M0 | the MEASURES kind row (validator, canonical and decoded writers, store, R1-R5 with `ks_ref.py`); `measure_store/` with ONE set (`zen4-grid1` as scratch, replaced by `zen4-grid2`, GO since D167, when run) and its `match-at` boundary capture (§8.1) [r2 n10]; `ksgen.c`; the embed; the `<PREFIX>_MEASURES` stamp AND `rx_info.measures` (the abi event); the bare compile reads the LATEST set; cards (pcrec's file empty; the kit's via R-MS5); staleness listing with `compiler-mismatch` and `libc-mismatch`; `--list-measurements` sets and one-set views over [LIST-TABLES]' census slice; `mf_measures` + `consulted`; spec `docs/spec/measures.md` (with §1.6's code table); `test-measures` (recompute, drift gate, coverage) and `-answers` (with the synthetic sets incl. `dispatch`, boundary subjects, REACH floors through R-MS6, the fired-rows construction check, near-cap); S943-S945, S947, S948, S950, S953-S958, S983, S987 | R17-b′'s build (GO, D167), landing WITH R-MS1, R-MS2, R-MS3, R-MS5, R-MS6 (D166) |
| M1 | `--measures=`, the config line (through `ks_pick`), `-I` resolution (§3.2: `name-else-file`, `s2_mismatch = refuse`, the (id, rev) shadow key), precedence tests, the per-target view, emit_sweep's `measures` data arm + `DEFAULTS.log` and `movers/<seq>.tsv`; S946, S952, S959, S985, S988 | the first second set (grid2 after grid1, or a rollback need) |
| M2 | the envelope script, R-MS4's safe directions, the cross-member loss test, class defaults, the DEFAULT FLIP to the envelope with its census (an abi event; RULED, D166 add. 2); S949, S960 | a second box's OFFICIAL set (F5 Zen 1) |
| M3 | `pcrec-measure` (the parts + the measures row only, §7.1), the quick profile, per-group gates and PARTIAL, `local` tier, `DEFAULT_MEASURES` into `build/`; S951 | a stated install-time need (D166 item 3 names it; no scheduler for it until a user asks) |
| M4 | pcrec's own quantities (`pcrec.c_call`, `pcrec.c_byte`), their cards, the pcrec-side dependency hash's body normalization (§2.4) [r2 n7], and `cand_rows[]` as readers in the census | the regime table's pcrec-side build |
| E-P | the `evaluator-params` kind row (§9.11), its harness listing, R1-R5 over the kit's committed `prereg.tsv` revs; S990 | OQ-1 ruled; until then the kit's file uses §9.11's format |

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
- **The loader's interpretation** is checked by R5 against an independent reader per kind
  (python `ks_ref.py` for the TSV kinds, `analyze/`'s reader for analysis). Every other
  round-trip check runs the one C reader on both sides (§9.6) [r2 M3].
- **Dispatch reach** is counted by the kit's R-MS6 hook. The admitted arms come from the
  kit's fired-rows section, and that section is checked against the `dispatch` set's
  construction through §5.4's census, which is a different kit output (§8.1) [r2 M7].
- **Population counts** (statuses, census artifacts by emit_sweep's per-stream reach floors,
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
- (c) **A kit form-body change** stales the rows that depend on it, transitively. A
  stale default is CARRIED STALE (RULED, D166 add. 2): a listing flag, an INFO count and
  manager review, never a gate.
- (d) **[KNOW-SRC]'s K0-K3** move no emitted byte (§9.7). K3 adds a caller-visible view
  (`--view=canonical`) with its spec hunks.
- (d′) **A change to any knowledge kind's shipped data** (a findings bundle, a set, a
  `limits.def` default) is censused by emit_sweep's ONE data mode (§9.3), whose output names the movers
  and their attribution.
- (e) **Spec:**
  - a new `docs/spec/measures.md` (the format, the key grammar, the registry with its
    integer formulas, the NULL rule, the stamp);
  - hunks in `cli.md` (§1.1.2 flag, §1.1.4 config, §2 listing, §2.11 `--emit-facts`);
  - `match_api.md` §6 (the `rx_info` member, a ¶ beside 6¶14) and §6.3 (stamp, abi line);
  - `rxt_format.md` (the `measures` config line);
  - `registry.md`, if `--list-axes` lists `--analysis` today (grep at build);
  - `table_contract.md` §1's table (the new listing);
  - `findings.md` and `cli.md` for [KNOW-SRC]'s `--view=` spelling and the loader's
    rejection of derived sections (K3).

  `docs/guide/` points at these and never restates them.

### 10.3 Sibling-family and design lenses

| sibling | what it teaches | what a set does differently |
|---|---|---|
| analysis object / findings (D162) | NOW SHARED, not imitated ([KNOW-SRC], §9): name grammar, `-I` search, store, embed generator, digest roles, stamp grammar, `rx_info` mirror, fill-only precedence, the `--list-<kind>` shape, round trip, the census (emit_sweep's data mode). Its divergences (classification, the S2 rule, two digests) are declared columns, not copies [r2 M2, M5] | no chain, no `include`, no `serves`; keyed integer rows, not counts; its `.rxt` format is reconsidered (§9.9) |
| [TABLE-JUDGE] picks file | the third kind of §9's module; the interface the envelope's cross-member loss test and §7.3's replay claim use | FILE only, no store, no stamp in artifacts |
| [REGIME-EVAL]'s evaluator parameters [r2 M1] | the fourth kind (§9.11): the placement rule's P3 row; the prereg hash is its item digest | not measured and not read by a compile; it changes verdicts, never bytes |
| `lib` references [r2 M6] | the resolver's fifth row: one stop loop over the same `-I` list | resolve only; its entry match differs today (F12) |
| `analyze/` (`pcrec-analyze`) [r2 n2] | the deliberate independent twin of the analysis format, and R3's control | never a member: zero-dependency by charter |
| `scripts/emit_sweep.py` [r2 M4] | the two-side compare, pinned streams, reach floors, stamp normalization, refusal and tag tallies | the census is its `--data` mode, not a second tool |
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
- **Fits the architecture vs a refactor.** It fits, and the one refactor it causes
  ([KNOW-SRC] K0-K3) is a zero-mover unification the family needed anyway, built first.
- **First-match tables.** The kinds table, the reader rows, the envelope's exclusion rows
  and the card table are declared tables.
- **Unlocks** are filed in §10.4.

### 10.4 Unlocks, filed with triggers (not built)

**The re-check's unlocks (r2 U1-U5) [r2].** Each is an idea filed with its trigger. None
is built into this design, and no stage above depends on one.

| id | the idea | what it would unlock | trigger |
|---|---|---|---|
| r2-U1 | ONE TWO-WORLD COMPARE: emit_sweep's two-side machinery for ANY world pair (a code revision, a limit variant, a data version of any kind, an option set, [OPT-SETS]), with one movers and attribution TSV shape for all four | one census reading for every kind of change; a code change's movers and a data change's movers become diffable against each other | K0, the first census written (the data mode lands then; the generalization is decided on what it shows) |
| r2-U2 | ITEM DIGEST = FNV over the canonical writer's bytes of the kind's declared VALUE columns | R1 and the digest could not disagree about what is a "value"; every new kind's digest follows from `write_canonical` plus a column list, with no hand-written fold. The shipped `rows_digest` and `pcrec-find-1` stay grandfathered (§9.2 part 5) | the `evaluator-params` row's build (E-P), the first kind whose digest would otherwise be hand-written new |
| r2-U3 | LIMITS AS A READ-ONLY KIND: a kinds-table row with store only, no flag and no stamp | `--list-limits` gets the canonical view, R4 and the trace's attribution free; §9.1a's placement rule becomes rows of one table | the first `limits.def` default change censused by emit_sweep's data mode |
| r2-U4 | THE [LIB] STORE AS A RESOLVER KIND: `lib <store-name>` (reserved today in `rxt_source.c`) resolves through `ks_resolve`'s S3 | the `lib` row (§9.5) gains a store, and named libraries are found the way bundles and sets are | [LIB]'s build |
| r2-U5 | AN INLINE TABLE BLOCK: if §9.9 keeps `.rxt`, a `.rxt` DATA block `table KIND { … section TSV … }` serves ANY kind inline (S1 for measures and evaluator parameters too) | one inline spelling for every kind, in place of §9.9's "middle form" with two spellings for one kind | the §9.9 decision at K3 |

**Revision 2's list (r1 unlocks), unchanged:**

- **The shared knowledge-source module and the one census tool (U1).** MOVED INTO SCOPE as
  [KNOW-SRC] (§9), endorsed by Frank 2026-10-14 and built FIRST. Recorded here because the
  panel named them as unlocks.
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

### 10.5 Rulings, and what stays open

**Both of the panel's questions are RULED by D166 addendum 2 (Frank, 2026-10-14):**

- **Q-MS-1, the bare compile.** Until a SECOND OFFICIAL set exists (M2, the F5 Zen 1 run),
  a bare compile reads the LATEST set (D166's literal reading). The generic envelope
  becomes the default at M2. Before M2 the envelope cannot be built from official
  members, and at n=1 it would drop the cost rows and move selections. The M2 flip
  carries its census and its abi event (§3.4, §3.6).
- **The stale default.** When a measured form's normalized body changes after its set was
  measured, the default set is CARRIED STALE. The listing flags the stale rows, and a
  manager reviews them. It is never a landing gate: a re-measure needs a quiet box or a
  bench window, and kit text changes must not wait on one (§2.4).

**Ruled for [KNOW-SRC] (Frank, 2026-10-14):**

- the module and the census tool, built first (§9);
- ROUND-TRIP IDENTITY (§9.6).

**OPEN, for the module's design, not decided here:** whether the analysis object's `.rxt`
DATA input moves to the section TSV (§9.9). The case is laid out both ways with the
migration cost. Its trigger is K3.

**Revision 1's other questions, and how they stand:**

- **Q-MS-2:** withdrawn. D162 ruling 1 is kept (§3.6).
- **Q-MS-3** (tier `local` for install-time sets; `official` only from a bench run on
  targeted hardware): settled as recommended. It follows D144 add. 4.
- **Q-MS-4** (`measure_store/`): settled by the manager (a one-token choice).
- **Q-MS-5** (the 6.2% gate): replaced by per-group card gates, labelled unmeasured
  defaults (§7.3).
- **Q-MS-6:** replaced by the stale-default ruling (D166 add. 2).
- **Q-MS-7** (embed every rev): settled. Rollback must work from a release build.
- **Q-MS-8** (16 hex): settled, matching the FINDINGS width.

None of the settled choices changes an answer, and each was the manager's to make
(`pcrec-answer-free-choices-are-mine`).

**Revision 3 (manager-settled, answer-free).** Each choice below changes no answer, so each
is the manager's (`pcrec-answer-free-choices-are-mine`):

- the shipped `name-else-file` classification for measures;
- `s2_mismatch = refuse` for measures;
- the census as emit_sweep's mode;
- the two digest roles with literal grandfathered domains;
- `lib` kept at `probe-exists` through K1;
- the movers log keyed by transition;
- R5 and its readers.

### 10.6 Open question for Frank

**OQ-1: who READS the evaluator-parameter kind?**

- **The problem.** The plan row places [REGIME-EVAL]'s verdict-changing constants in "a
  [KNOW-SRC] kind" (Frank, 2026-10-14). Its only reader is the kit's judge mode, which is
  kit code in the kit's tree (`memfn/`, 0BSD, its own project and lanes). pcrec's
  compiler never reads these values. §9.11 fixes the FORMAT and the DIGEST now, so the
  file is canonical from day one either way. The open part is whether "a [KNOW-SRC]
  kind" means one READER across both projects, or one FORMAT with each project reading it
  its own way.
- **Forces for one reader (the kit compiles pcrec's parts).** It is Frank's "consistent
  loader". One reader cannot drift, and after M8 the parts are libc-only and can be
  compiled into the kit's harness as source, as `pcrec-measure` compiles them.
- **Forces against it.**
  - It makes the kit's harness depend on pcrec source (MIT into a 0BSD project, both
    Frank's).
  - It couples the kit's judge to pcrec's module revisions.
  - It inverts D146/D157's boundary in a small way: pcrec would supply method code to the
    kit, not only facts.
  - A kit-side reader of a pcrec-specified format is also a free R5 control: two readers
    of one spec, with one of them independent.
- **Leaning.** One FORMAT and one DIGEST spec (`docs/spec/evaluator_params.md`), and the
  kit keeps its own reader. pcrec's module adds the `evaluator-params` row (E-P) for the
  listing, the round trip and the census diff over the committed revs, and R5 compares
  the two readers. If the kit later wants pcrec's parts, it asks by request, and nothing
  in §9 prevents it. The decision changes no answer and no emitted byte. It goes to Frank
  because it sets a precedent for code crossing the pcrec/kit boundary, and that boundary
  is his.

## 11. Findings

- **F1.** R17-b′ §3.5 proposes `measures/<name>/`. `oracle_store/`'s shape fits better,
  because the data is derived by running our code, not vendored. Settled as
  `measure_store/<id>/<rev>/`.
- **F2 (revised) [r1 msc2-10].** The kit facts the framework needs are five requests
  (§4.4), not "two return facts". R-MS2 replaces revision 1's per-key lookup report with a
  boolean (§4.2).
- **F3 (revised) [r1 msc2-2].** D166's "latest set" and D161 add. 12's generic envelope
  differ even at one box, because the envelope drops cost rows. The design ships the first
  through M1 and flips to the second at M2 with a census (RULED, D166 add. 2).
- **F4 (revised) [r1 msc3-7].** "Derived crossovers recompute from their rows" now holds
  for `fitted` rows too, because the raw cells a fit reads are committed in the set.
- **F5.** Staleness of a row cannot be a file field in an immutable store. It is computed
  against the linked kit, transitively (§2.4). That puts the kit's form hash (R-MS3) on the
  framework's listing path, never its landing gate (RULED, D166 add. 2).
- **F6 (revised).** The stamp is defined on CONSULTATION, not on found rows (§3.5). An
  absent row skips a dispatch, so the artifact depends on the set even when nothing was
  read. The one-way check (empty ⇒ identical) is the property.
- **F7 (new) [r1 msc1-5].** The corpus cannot exercise run-time dispatch: 97.8% of 62,360
  subjects are under 36 B. Any answer-identity claim about a length-dispatching form is
  vacuous without generated boundary subjects and a per-arm run-time reach floor (§8.1).
- **F8 (new) [r1 msc2-9].** The analysis object and measurement sets are one family, and
  [TABLE-JUDGE]'s picks file is a third member. They share one module and one census tool
  ([KNOW-SRC], §9), built first, and the analysis loader migrates onto it with zero movers.
- **F10 (new).** Frank's two round-trip checks (load→list→load digest, list→load→list
  bytes) are both blind to a canonical writer that drops a section the digest does not
  cover, CONSISTENTLY: drop `cells`, and the digest and the second listing still agree. A
  third, structural check (R3, the documents compared by an independent parser) closes it
  (§9.6, S961).
- **F11 (new).** Under the round-trip rule, the shipped analysis bundles cannot equal
  their canonical view, because their prose is the point (`default.rxt` is mostly cited
  rationale). That exemption is the visible cost of keeping `.rxt`, and it is §9.9's
  trigger.
- **F9 (new) [r1 msc3-4].** grid1's own noise figures refute a run-wide noise gate.
  Per-group A/A p90 is 3.37% on F1 and 0.17% on F3, and the per-launch p90 is 6.96%. The
  noise is the walk's on 64 KiB find-all groups (gridread §1.1), so gating is per group,
  with a PARTIAL outcome.
- **F12 (new) [r2 M6].** The `lib` reference resolver (`src/parse/rxt_source.c:4283-4340`)
  probes `-I` directories with `path_is_file(join_path(...))`. The analysis resolver
  deliberately replaced that probe with an exact directory-entry match ([r2 M-S6],
  `rxt_find.c:9-12`). On a case-insensitive filesystem (the Mac), `lib "Foo.rxt"` can
  therefore resolve `foo.rxt`, where a bundle name cannot. K1 keeps the shipped behaviour
  as the `lib` row's `entry_match = probe-exists`, so the move is zero-mover. The FIX is
  a one-cell flip to `exact`. It is caller-observable on case-insensitive filesystems only,
  and it lands as its own change with its `rxt_format.md` hunk (D80). It is filed for the
  manager as a known-issues row, not fixed here.
- **F13 (new) [r2 n1].** The re-check's count of sabotage rows anchored in
  `src/core/findings.c` (11) missed 4 of 15, because their `SAB_FILE=` uses single
  quotes. Any hand-run anchor census needs both quote styles, which is why K1's re-aims
  are derived from an edit set (§9.7).
- **F14 (new) [r2 M3].** Every round-trip check revision 2 named (R1-R4, the drift gate,
  pre-parse against a fresh parse) runs the one C reader on both sides. A symmetric
  reader/writer defect passes all of them. Only a comparison of the C INTERPRETATION with
  an independent reader of the original file (R5) sees it. The same holds for any future
  kind: every kind needs a named independent reader (§9.6's table) before its round trip
  means anything.
