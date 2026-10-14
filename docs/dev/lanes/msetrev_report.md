# msetrev report — [MEASURE-SET] design revision 2 (2026-10-14, design only)

Lane `msetrev` (opus), from main `58338a09f` (abi 78). Brief: revise
`docs/design/measure_sets.md` to revision 2, applying every finding of the D6 panel
`docs/dev/reviews/2026-10-14-r1-measure-sets.md` as dispositioned there. Nothing under
`src/`, `cli/`, `lib/` or `tests/` changed; no build or suite was run (docs only).

## Delivered

- `docs/design/measure_sets.md` revision 2. Its §R2 maps each finding id to the section
  changed and how; changed text is marked `[r1 <id>]` in place.
- The `docs/design/CLAUDE.md` entry, with a revision-2 paragraph.
- This report and its `docs/dev/lanes/CLAUDE.md` line.

## The decisions the revision made (where the brief left a choice)

- **Wire shape.** `table_contract.md` §4's `#section` lines, chosen over oracle_store's
  `# k=v` line. Header values carry spaces, a set has four or five tables, the file and
  `--list-measurements NAME` share one shape and one truthfulness check, and the picks file
  needs sections too (§1.2).
- **Stamp digest.** The loaded set's `values_digest`, over the whole set, stamped on load.
  It is not a consumed-subset digest. The kit returns only a boolean, so the subset is
  unknowable without a per-key report (a D157 concern), and the id@rev already
  distinguishes sets in the bytes. The consumed-subset digest is filed as an unlock behind
  per-artifact dependency records (§3.5, §10.4).
- **Key.** `owner.quantity` followed by the dimension tokens in the order declared by the
  card's `dims`. The format defines no placeholder. R17-b′'s `kit.beta.V1.ANY.r2e0c0`
  conforms unchanged, and whether `ANY` means "unsplit" is the kit's meaning (§1.3.3).
- **Where the safe direction lives.** It is declared by the reader rows through R-MS4 and
  [LIST-TABLES]' census, and the card's `env` is the cross-check (§6.2).
- **Fitted rows.** They recompute because the raw cells a fit reads are committed in the
  set's `cells` section, and `interp-log2` is a registry derivation (§1.5, §1.6).
- **Rounding.** Integer arithmetic with round half away from zero, specified so that C and
  python agree EXACTLY (§1.7).
- **Sibling module.** `src/core/ksrc.c`, with four parts (section-TSV reader, resolver,
  store, stamp/digest) and a kinds table. The analysis `include` chain stays in the
  analysis kind. findgen.c becomes `ksgen analysis`. The migration is K0 (M0), then K1/K2
  (M1) at zero movers (§9).
- **Census at landing.** The re-run comparison happens only in the commit that adds a
  default or moves a pointer. Every build checks the structure only (§8.4).
- **Requests main files** (§4.4), M0's trigger being R17-b′ landing WITH R-MS1/2/3/5:
  - R-MS1: `mf_measures`, kit rows only, no status.
  - R-MS2: `consulted`.
  - R-MS3: `mf_form_hash` over the canonical form body.
  - R-MS4: the reader declaration with safe directions, plus the `--emit-facts` `memfn`
    section. That section does not exist today; revision 1's draft wrongly called it
    existing, and this lane corrected it before commit.
  - R-MS5: the kit's method cards.
- **Sabotage.** S943-S952 are kept, re-aimed where the panel said they missed (S945, S947,
  S951, S952). S953-S960 are PROPOSED: free on main and in every worktree as of
  `58338a09f`, outside the kit-reserved ranges, and main allocates them.

## Round 2 (same day): Frank's rulings folded in

- **D166 addendum 2.** Q-MS-1 and the stale-default policy are written as RULED (§3.4,
  §2.4, §10.5).
- **[KNOW-SRC].** §9 is rewritten as that row's design:
  - the module (reader/validator, resolver, `ks_pick` fill-only precedence, `ksgen` embed
    generator, stamp/digest builder, the four-view `--list-<kind>` shape);
  - ONE census tool, `scripts/knowledge_census.sh KIND OLD NEW`, with analysis, measures
    and limits arms and per-artifact lookup attribution from a debug-build reader trace.
    It replaces `measure_census.sh`.
  - Staging: K0-K3 BUILT FIRST at zero movers, ahead of M0 (§9.7, §9.8, §10.1). M0 now
    only adds the measures kind row.
- **ROUND-TRIP IDENTITY** (§9.6): the canonical writer, plus checks R1 (Frank's digest),
  R2 (Frank's bytes), R3 (NEW: structural document equality by the independent python
  parser) and R4 (committed store file = its canonical view). R3 exists because R1 and R2
  both pass when a writer consistently drops a non-digested section (`cells`). Derived
  views are separate `--view=` spellings, and the loader rejects their section names.
  For the analysis kind, the bare `--list-analysis NAME` keeps its shipped output until
  §9.9 decides, so the CLI moves once. The analysis store is R4-exempt by name until then.
- **§9.9, OPEN:** the `.rxt` analysis format against the section TSV, both cases, a priced
  middle form, the migration cost (input and docs side only; zero artifact movers, since
  the `_FINDINGS` digest is over derived values), with K3 as the trigger.
- **New proposed sabotage ids:** S961-S963.

## Questions for Frank (round 1; both RULED since, D166 addendum 2)

- Q-MS-1 as re-put: the latest set through M1, then the envelope from M2 with the flip's
  census (it moves selections even at n=1). Recommend yes.
- Q-MS-STALE: what a stale row in a default set does. The manager's leaning is
  carried-stale plus a listing flag and manager review, never a landing gate.

Revision 1's Q-MS-2 is withdrawn (D162 ruling 1 kept). Q-MS-3..8 are recorded as settled
(§10.5).

## For a follow-up round

Nothing is owed from this lane. Two things are the next design's to check:

- **§9.5 K1's gate list.** It needs the exact `-I` refusal fixtures named by grep at build.
- **The census row shape.** Whether [LIST-TABLES]' STEP 0 census accepts a `reads` column
  in the shape §5.4 assumes. That row is not started; the shape is proposed here, and
  [LIST-TABLES] owns it.
