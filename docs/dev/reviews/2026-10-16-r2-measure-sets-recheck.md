# 2026-10-16 r2: light re-check of docs/design/measure_sets.md (lane msrecheck)

One read-only critic (opus) with the unlock lens. The subject is `docs/design/measure_sets.md` at `e8d35840e`. The brief calls it "rev 2.1": rev 2 plus Frank's same-day rulings, and its header still says "revision 2". It is checked against the r1 panel (`2026-10-14-r1-measure-sets.md`), D166 and its addenda 1, 1.1 and 2, and the [KNOW-SRC] plan row (`docs/dev/plan.md:877-884`).

Totals: 0 BLOCKER, 8 MAJOR, 11 MINOR. The r1 discharge is good: every blocker is DISCHARGED or PARTIAL with a narrow residual. The new findings are concentrated in §9 ([KNOW-SRC]), which has not been reviewed before.

## Part 1: r1 BLOCKERs and MAJORs, discharge status

| r1 id | status | where | residual |
|---|---|---|---|
| msc1-1 (B) | DISCHARGED | §2.1, §8.4 | Minor N9 below: a default ROLLBACK to an older rev has nowhere to write its MOVERS, because that rev's directory is immutable and may already hold one |
| msc1-2 (B) | DISCHARGED | §2.3, §9.2 part 4 | The C reader's interpretation is never compared with an independent reader (see M3) |
| msc2-2+msc1-4 (B) | DISCHARGED | §3.4, §6.3, §6.4, §10.5 (ruled, D166 add. 2) | none |
| msc1-5 (treated B) | PARTIAL | §8.1 | See M7. The reach lever instruments "each emitted dispatch arm", but those arms are KIT-emitted text, and no R-MS request asks the kit for a counter hook. The "admitted arms derived by python from the set's rows" needs each kit row's PREDICATE, not only its keys and directions (R-MS4), so python would re-implement the kit's selection (D157) |
| msc2-1 | DISCHARGED | §1.2 (`table_contract.md` 4¶2 confirmed) | none |
| msc2-3 | DISCHARGED | §3.5, §3.6 | The justification for a whole-set digest holds for measures, but it makes the family's "stamp digest" mean two different things (M5) |
| msc2-4/5 | DISCHARGED | §1.3 | n6: the digest's "unit byte" and "status byte" codes are not defined |
| msc2-7 | DISCHARGED | §4.1, §4.2 | none |
| msc2-9 (family) | PARTIAL | §9 | The unification is designed but incomplete. The fourth ruled kind is missing (M1). The analysis resolver's semantics differ from the proposed shared ones (M2). Two more siblings are unplaced: the `lib` resolver (M6) and `emit_sweep.py` (M4) |
| msc2-10 | DISCHARGED | §4.4 | The reach hook is not among R-MS1..5 (M7) |
| msc1-3 | DISCHARGED | §3.6 | none |
| msc1-6 | DISCHARGED | §8.1 | none |
| msc1-7 | DISCHARGED | §2.4 | n7: the pcrec-side hash uses emit_sweep's stamp normalization only, so it over-stales |
| msc1-8/msc2-6 | DISCHARGED | §2.4, §10.5 (ruled) | none |
| msc1-9 | DISCHARGED | §8.1 part 3, §8.4 step 3 | none |
| msc1-10 | DISCHARGED | §6.2, §8.2(e) | n8: for an EXCLUDED key (readers disagree), the rule for what the card's `env` must equal is undefined, so the cross-check would fail |
| msc1-11 | DISCHARGED | §8.3, §8.5 S947/S952 | none |
| msc3-1 | DISCHARGED | §1.4 | none |
| msc3-2 | DISCHARGED | §7.2 | none |
| msc3-3 | DISCHARGED | §6.2-§6.4 (loss test at M2) | none |
| msc3-4 | DISCHARGED | §7.3 | none |

All r1 minors are discharged.

## Part 2: findings

### M1 (MAJOR): the fourth ruled kind, the EVALUATOR PARAMETER TABLE, is absent from §9

- **Evidence.** The plan row `docs/dev/plan.md:884` reads: "KINDS (Frank 2026-10-14): analysis object, measurement sets, [TABLE-JUDGE] picks, AND the EVALUATOR PARAMETER TABLE ([REGIME-EVAL]'s verdict-changing constants: the prereg hash = the kind's digest, the report's prereg diff = the census tool's diff). Placement rule: ... harness thresholds -> a [KNOW-SRC] kind. Until built, each kind's file uses the canonical format from day one."
  - That row was committed at `5cfd2e1c0`, after `e8d35840e`. The note therefore predates the ruling, but the note is the row's design of record.
  - §9.1, §9.2's `KsKind` comment, §9.5 and §10.3 all list three kinds.
  - The kit's `prereg.tsv` (`memfn/docs/responses.md:2447`) is the live instance, and "until built, canonical format from day one" binds it now.
- **Why it matters.** This kind shapes the generality of the digest (M5) and of the census, and it has no stamp in artifacts: its "stamp" is a prereg commitment.
- **Fix.**
  - Add the `evaluator-params` row to §9.1 and §9.5. It is FILE plus a store or not, no CLI flag, and no artifact stamp; its digest is the prereg hash.
  - Add the placement rule as a first-match row table: compiler number → `limits.def`; measured decision number → set; harness threshold → kind.
  - State the canonical format the kit's `prereg.tsv` must use today, so that it does not need a migration later.

### M2 (MAJOR): K1's "zero movers" is false as specified, because the shared resolver's rules contradict the analysis kind's shipped, spec'd rules

- **Evidence.**
  - **(1) The S2 name mismatch is handled in opposite ways.**
    - §9.2 part 2 makes "the rule that an S2 file's declared name must equal NAME" a SHARED part, and §3.2 says such a file is REFUSED.
    - The analysis S2 does the opposite, by spec. `docs/spec/findings.md` S2 row: "A file that defines no bundle, or one of another name, FALLS THROUGH to the next stop with a note on stderr; a file defining two or more bundles is refused". The same text is in `src/parse/rxt_find.c:12-15`.
  - **(2) Spelling classification.**
    - §3.2 says: `/` means FILE, else the id grammar means NAME, else refuse.
    - The shipped `--list-analysis X` says: `pcrec_find_name_ok(X)` means NAME, else FILE (`cli/main.c:1808-1809`, `2233-2236`). So `--list-analysis foo.rxt` and `--list-analysis Foo` are FILE reads today and would be REFUSED under §3.2.
    - The shipped `--analysis` accepts NAME only (`cli/main.c:1103`), with no FILE and no `@REV`.
  - **(3) The grammar differs.** Measures add `@REV`; analysis has no revs.
  - §9.7 K1's gate ("`--list-analysis`/`--list-analyses` outputs byte-identical; the refusal texts byte-identical") would go red, or force the analysis kind to keep its own copies, which is the parallel mechanism §9.4 exists to remove.
- **Fix.**
  - Make each divergence a declared column of the kind row:
    - `classify`: `name-else-file` | `slash-file` | `name-only`;
    - `s2_mismatch`: `fallthrough-note` | `refuse`;
    - `revs`: yes | no;
    - `s2_multi`: `refuse`.
  - Name them in the K1 edit set, with the `-I` resolution fixtures (`tests/findings/res_fixtures.py`) as the zero-mover witnesses.
  - Better: adopt the SHIPPED `name-else-file` classification for measures too. That also fixes M3's example (below).
  - Whether measures should refuse or fall through on an S2 mismatch is a per-kind choice, and the note should state why the two kinds differ. Analysis falls through because a `lib` file can sit beside a bundle; a `.measures.tsv` has no such neighbour.

### M3 (MAJOR): the round-trip checks share their reader and writer with their subject; also, the note's own round-trip example is refused by §3.2

- **(a) Shared source.**
  - R1, R2 and R4, the drift gate (§8.3), and "pre-parse vs a fresh library parse" all run the SAME C reader (`ks_tsv_read` plus the kind's validator, which `ksgen` links at stage 0) on both sides.
  - Take a symmetric reader/writer defect. For example, the reader resolves `noise_e6` into the `abs_ns_e6` field, and the writer writes that field back under `noise_e6`. The text then round-trips byte-identically:
    - R1 and R2 stay green;
    - R4 stays green;
    - R3 stays green, because python compares python(list(x)) with python(x), and both texts are identical.
  - Yet the C document is wrong.
  - Only §8.1's structural arm compares the C interpretation with an independent reader, and only for keys a dispatch literal shows. Every unit-relative recompute in §8.2 reads FILES, never the loaded document.
  - This is learnings §3's pattern: the control shares its source with what it controls.
  - **Fix.** Add **R5, decoded = independent**. For every store item and fixture, `--list-<kind> NAME --view=decoded` (the C loader's interpretation, field by field) must equal the python parser's decode of the file. For analysis, the existing `--list-analysis` resolution digests must equal `findings_ref.py bundle-digest`. Add a sabotage row with a symmetric column swap; R1-R4 stay green and R5 goes red.
- **(b) R3 for the analysis kind has no independent parser to run.**
  - `tests/findings/findings_ref.py` reads only `row` lines, by regex.
  - R3 compares "every section and every column", and for `.rxt` that means `include`, `serves … when … via`, provenance and blocks.
  - **Fix.** Price a python bundle parser into K3. Alternatively name `analyze/`'s own bundle-text reader as R3's independent side: it is zero-dependency by charter (`analyze/CLAUDE.md`: "its own bundle-text reader for `--merge`/`--check`").
- **(c) The note's own example is refused by its own §3.2.**
  - §9.6 and §5.2 use `--measures=f.tsv`. `f.tsv` contains no `/` and fails the id grammar, so §3.2 rule 3 refuses it.
  - **Fix.** Use the shipped `name-else-file` rule (M2), or spell the example `./f.tsv`. The first is better: users will type `--measures=mine.measures.tsv`.

### M4 (MAJOR, sibling family): `knowledge_census.sh` duplicates `scripts/emit_sweep.py`

- **Evidence.** emit_sweep already does each piece of what the census tool would do (`scripts/emit_sweep.py:1-62`):
  - it builds two sides, including `git archive` stage builds with `-D` limit VARIANTS (`plain`, `lowsize`, `lowdfa`, `lowboth`, `lowthr`), which is exactly §9.3's `limits` arm ("else two stage builds");
  - it compiles pinned populations over eight streams;
  - it strips stamps, a normalization §2.4 already borrows;
  - it records refusals and stderr, which §9.3's "tokens and refusals" re-specifies;
  - it tallies `*_WHY`/prefilter tags against pinned floors (`VARIANT_PINS`).
  
  §9.3 nevertheless adds a second tool, a second pinned population (`tests/knowledge/census_population.tsv`) and a second artifact manifest (S952).
- **Fix.** Make the census an emit_sweep MODE:
  - `--data KIND OLD NEW`: the two sides differ by data arguments (`--analysis=`, `--measures=`) or by a variant build (limits);
  - an ATTRIBUTION stream (the lookup trace);
  - a movers-TSV writer;
  - the population taken from emit_sweep's pinned streams.

  S952's manifest then becomes emit_sweep's existing reach floor. The general form is one "two-world compare" (code revision, limit variant, data version, option set); see U1.

### M5 (MAJOR): the digest spec does not generalize as written; the analysis kind already has TWO digests and a per-QUERY domain

- **Evidence.**
  - The stamp digest is per query. Its domain is `pcrec-find-1\0<query>\0`, it covers DERIVED values for `byte-rate` and `via` plus rows for `run-rarity` (`findings/design.md` §7 table, lines 1103-1109; `src/core/findings.c:332-344`), and the stamp grammar is `query=bundle:digest`.
  - The item digest is `rows_digest`, with domain `pcrec-find-rows-1` (`findings.c:346`, `docs/spec/findings.md` 8.1¶1), and the spec states that it is "a DIFFERENT hash from the stamp's".
  - `KsKind` has ONE `digest_domain` ("pcrec-find-1"). It cannot express the query sub-domain or the second digest.
  - The measures stamp digest is an ITEM digest (`values_digest`, stamp-on-load, §3.5). So "the kind's stamp digest" means consumed-subset for analysis and whole-item for measures.
  - R1 ("digest = the kind's stamp digest") is UNDEFINED for an analysis bundle. Which query, and which encoding? It is VACUOUS for a bundle serving no `byte-rate`.
  - The domains do not follow `pcrec-<kind>-<N>`: they are `find`, `find-rows`, `meas` and `pick`. They CANNOT be renamed, because changing `pcrec-find-1` moves every `<PREFIX>_FINDINGS` stamp, which is an abi event.
  - The evaluator-params kind (M1) needs a whole-file digest (a prereg commitment), a third meaning.
- **Fix.**
  - Give the kind row two digest ROLES:
    - an ITEM digest: identity of the loadable item, used by R1, the shadow rule and the census. It is `rows_digest` for analysis, `values_digest` for measures, and a file digest for picks and evaluator-params.
    - a STAMP digest: what a compile consumed. It is per-(query, enc) for analysis, and equals the item digest for measures.
  - Make each domain a literal column value, grandfathering `pcrec-find-1` and `pcrec-find-rows-1`, rather than a derived `pcrec-<kind>-<N>`.
  - State that `rows_digest` covers neither `serves` nor `include` nor provenance, so R3 (M3b) is load-bearing for those.

### M6 (MAJOR, sibling family): the `lib` reference resolver is a third `-I` resolver, unplaced, and it has ALREADY drifted

- **Evidence.**
  - `src/parse/rxt_source.c:4283-4340` resolves `lib "path"` over the source's directory, then each `-I` dir, with its own chain text (`lib_chain_text`). It RESERVES `lib <store-name>` for the [LIB] store, a name→store lookup, which is §9.2's S3.
  - It probes with `path_is_file(join_path(...))`. The analysis resolver deliberately replaced that probe with `dir_has_exact`, to stop a case-insensitive filesystem answering `log` with `Log.rxt` ([r2 M-S6], `rxt_find.c:9-12`).
  - This is the drift §9.4 predicts ("they agree today and drift tomorrow"), already present between two members over the SAME `-I` list (`cli/main.c:1812-1818` shares it).
- **Fix.** Name `lib` (and the future [LIB] store reference) as a member of the resolver family in §9.1. Either give it a kind row (no stamp, no digest, resolve only) or exclude it with a reason. File the case-exactness drift as a finding against `rxt_source.c`.

### M7 (MAJOR, msc1-5 residual): the REACH lever and the admitted-arm list cross the kit boundary with no request

- **Evidence.**
  - §8.1: the lever "compiles a counter increment into each emitted dispatch arm". The dispatch arms are kit text (D157, D161 add. 14), so pcrec cannot place a counter in them.
  - "The admitted-arm list is derived from the set's rows by the python parser". Knowing which arm a row ADMITS under given values needs the row's predicate. R-MS4 declares keys and directions only. So python would re-implement kit selection, the method presumption D157 forbids.
- **Fix.**
  - Add R-MS6: a kit harness hook that counts arm entries, under the reserved prefix.
  - Take the admitted-arm list from the kit's `--emit-facts memfn` fired-rows section (R-MS4), checked against the synthetic `dispatch` set's construction: every pay rule is priced to pay, so every reader row must fire. Then reach = run-time count ≥ 1 for each fired arm.

### M8 (MAJOR): the kinds table puts a core→parse link edge into a module the note calls dependency-free

- **Evidence.**
  - §9.2 says the analysis row's `parse` "is its existing `.rxt` reader, reached through the pointer, so `src/core` does not include `src/parse`". A table in `src/core` that names that function still LINKS it: the include is avoided, but the edge is not.
  - §7.1 compiles `ksrc.c` "into the driver as source ... allowed because the module has no dependency on the compiler". With the analysis row in `ksrc_kinds[]`, `pcrec-measure` must link the `.rxt` parser, `Arena` and `PcrecSb`. That contradicts the `analyze/` zero-dependency precedent it cites.
  - `encoding_data_layout.md` §2 treats exactly this shape (a measured `core → enc` back-edge) as a defect.
- **Fix.** Separate the kind-independent parts (reader, resolver, digest, list) from the kinds table. The table is assembled at the library tier, with the analysis row registered from `src/parse`. `pcrec-measure` links the parts plus the measures row only. State the dependency set it compiles.

### Minors

- **n1 (sabotage re-aims not derived).** K1/K2 delete or relocate `rxt_find.c`'s stop loop, `dir_has_exact`, `stops_text`, `find_bundle` and `findings.c`'s `fnv1a`. Rows S309, S310 and S315 anchor in `src/parse/rxt_find.c`, and 11 rows anchor in `src/core/findings.c` (`grep '^SAB_FILE='`). Per the start_table/dec_fallback precedent, §9.7 needs a derived edit set and derived re-aims (re-aim vs re-run) as a K1 deliverable. `tests/registry/limits_check.sh:365` reads `PCREC_FIND_NTBL/NBUNDLES` "in src/core/findings.c". If the store moves into `ksrc`, that is a moved reader.
- **n2 (a second writer and reader of the analysis format, unplaced).** By charter `analyze/` has its own bundle-text writer and reader and a SHA-256 (`analyze/CLAUDE.md`). §9.9 says "`pcrec-analyze`'s output would be one table write", but it cannot call `ksrc`. State that it is a deliberately independent twin, which is also its value as R3's control (M3b), and that it is not a member that "exists once".
- **n3 (per-kind special cases as prose).** The note has two: "bare `--list-analysis NAME` keeps its shipped output" against "bare `--list-measurements NAME` IS canonical" (§9.2 part 6), and "the analysis store is exempt from R4 by name" (§9.6). Make both kind-row columns (`bare_view`, `r4`), so the special case is data the kinds table lists.
- **n4 (attribution: two mechanisms for analysis).** §9.3's table says analysis attribution reads "the artifact's `_FINDINGS` stamp items". The paragraph below it says the census "joins that trace", with "findings readers ... one line at each". Pick one, the trace, with the stamp as its cross-check, and say so in the table.
- **n5 (shadow rule keyed on id only).** §3.3 and §9.6 accept a FILE whose `id` is committed with the same `values_digest`. A file with `id zen4-grid2`, `rev 7` and the rev-1 digest is accepted and stamps `zen4-grid2@7:…`, a rev that does not exist. Key the shadow check on (id, rev). Separately, §3.2 does not say how `NAME@REV` resolves at S2 (match the header `rev`?).
- **n6 (digest codes undefined).** §1.6's "the unit byte, the status byte" need a code table in the spec (`ratio`/`walkbytes`/`bytes`/`count`; `measured`/`fitted`/`derived`/`null`). Otherwise C and python can agree only by sharing a source.
- **n7 (pcrec-side dependency hash over-stales).** §2.4: the hash of the emitter's output for a probe pattern, "stamp lines stripped", moves on every abi bump and any unrelated emission change. Apply the same body-normalization msc1-8 required of the kit (hash the measured function body), or record that pcrec rows over-stale by design.
- **n8 (excluded key versus the card's `env`).** §6.2: a key whose readers disagree is EXCLUDED, yet "the card's `env` must equal the derived direction" or the test fails. Define `env` for an excluded key (`none`, or the cross-check skips it).
- **n9 (MOVERS for a default rollback).** §2.1 and §8.4 write `MOVERS.tsv` into NEW's immutable rev directory. Moving `DEFAULTS` back to an older rev that already holds MOVERS from its own landing has nowhere to write. Key the census by transition (a `DEFAULTS` change log, e.g. `measure_store/movers/<seq>.tsv`), not by rev directory.
- **n10 (oracle capture per set).** §8.1's generated boundary subjects depend on each set's L\* and W. Every new set (and every synthetic set edit) therefore needs a new libpcre2 `match-at` capture in `oracle_store/`. Make that part of a set's landing bar, and say that it needs the local adapter's box.
- **n11 (`ks_pick` tier).** Fill-only precedence lives in `cli/main.c:1458-1474` (`apply_target`) and prints through `cli_err`. Moving it into `src/core` makes the library print a CLI note. Keep the decision in core and the message at the CLI, or say why not.

## Part 3: unlocks (filed with triggers, not built)

- **U1, one two-world compare.** emit_sweep's two-side machinery (M4) generalizes to any world pair: a code revision, a limit variant, a data version (analysis, measures, evaluator params), or an option set ([OPT-SETS]). Movers and attribution become one TSV shape for all four. Trigger: K0, the first census written.
- **U2, item digest = FNV over the canonical writer's bytes of the kind's declared value columns.** Every kind's item digest (`rows_digest`, `values_digest`, the prereg hash) would follow from `write_canonical` plus a column list, so R1 and the digest could not disagree about what is "value". Trigger: the evaluator-params kind (M1), the first kind with no hand-written digest.
- **U3, limits as a read-only kind.** Add a kinds-table row with store only, no flag and no stamp. `--list-limits` would then get the canonical view, R4 and the lookup trace's attribution for free, and the plan row's placement rule becomes three rows of one table. Trigger: the first `limits.def` default change censused by the tool.
- **U4, the [LIB] store as a resolver kind.** `lib <store-name>` (reserved today, `rxt_source.c`) resolves through `ks_resolve`'s S3. Trigger: [LIB]'s build.
- **U5, an inline TABLE block.** If §9.9 keeps `.rxt`, then a `.rxt` DATA block `table KIND { … section TSV … }` serves ANY kind inline (S1 for measures and evaluator params too), instead of the "middle form"'s two spellings for one kind. Trigger: the §9.9 decision at K3.
