# 2026-10-14 r1 — D6 panel on docs/design/measure_sets.md ([MEASURE-SET], lane msetdes)

Three read-only critics (session 112): **msc1** checks/independence/staleness (opus),
**msc2** contract/boundaries/sibling family (sonnet), **msc3** measurement validity
(sonnet). Every critic carried the unlock lens. Totals: 4 BLOCKER, 22 MAJOR, 12 MINOR.
**Every finding is ACCEPTED**; dispositions below bind the revision lane. Items marked
FRANK wait on his ruling.

## Blockers

| id | finding | disposition |
|---|---|---|
| msc1-1 | MOVERS.tsv lives in the immutable rev dir, but §8.4 re-runs the census at HEAD for every set: red forever or edits to immutable files | ACCEPT: MOVERS is the census AT its landing commit (code_commit in its header), verified only in the commit that adds the set or moves a DEFAULTS pointer |
| msc1-2 | generate.py emits both the embedded text and the pre-parse the structural check verifies against its own python twin | ACCEPT: a C pre-parse on the findgen.c precedent (the one C reader); python only as checker |
| msc2-2 + msc1-4 | the envelope default (Q-MS-1) cannot exist before a second OFFICIAL set (M2), cannot load (no unit row), and at n=1 drops every env=none cost row, so selections MOVE | ACCEPT: M0/M1 ship D166's literal reading (the latest set); the envelope default arrives at M2; the n=1 selection difference is stated and censused; a composite carries members' unit rows as provenance. Q-MS-1 re-put to FRANK with this cost |
| msc1-5 (MAJOR, treated as blocking for M0's checks) | the answer-identity population cannot reach run-time dispatch: 97.8% of 62,360 corpus subjects are < 36 B, 42 in [36,64) | ACCEPT: a runtime REACH floor per form arm; generated boundary subjects (L*-1, L*, L*+1, block±1) per synthetic set; synthetic sets carrying the dispatch rows |

## Majors (contract and family)

- **msc2-1** the cited wire shape (`[header]`/`[rows]`) is invented; use table_contract.md's `#section` lines or oracle_store's `# k=v` line. ACCEPT.
- **msc2-3** the stamp deviates from `_FINDINGS`: `none` vs empty-string meanings inverted; digest over all rows vs consumed rows; no rx_info mirror (D43, match_api 6¶14). ACCEPT: empty string = nothing asked; digest the consumed subset or justify; ADD the rx_info mirror in M0's abi bump (cheap now).
- **msc2-4 / msc2-5** key strings do not match the kit's; fixed kit-vocabulary columns presume the kit's method (D157); pcrec rows have no layer/subject. ACCEPT: one canonical key string (declared dimension order, no placeholders) + optional free tags; the checker needs only uniqueness.
- **msc2-7** stamp-on-load + the kit returns a boolean "consulted"; hand the kit only `kit.` rows, no `status` unless a kit reader asks. ACCEPT.
- **msc2-9 SIBLING FAMILY**: the analysis object, measurement sets and [TABLE-JUDGE]'s picks file are three knowledge sources loaded by name. ACCEPT the unification: ONE `src/core` knowledge-source module (section-TSV reader/validator, name resolver, stamp/digest builder) parameterised by kind; `--list-measurements` consumes [LIST-TABLES]' census rather than running its own.
- **msc2-10** M0's kit return facts are in no landing bar. ACCEPT: main files the requests; M0's trigger is R17-b′ only with them.
- **msc1-3** Q-MS-2 contradicts D162 ruling 1 ("data regeneration that moves an emitted byte is an abi event"). DISPOSITION (manager): KEEP D162 r1, so a default-set change that moves bytes IS an abi event (pre-1.0 ritual), with its mover census. No re-ruling sought.

## Majors (checks and staleness)

- **msc1-6** "none EXACTLY when bytes identical" is red on day one; keep only none ⇒ identical. ACCEPT.
- **msc1-7** staleness is not transitive (vs form, the unit row, derived inputs, pcrec rows, the compiler). ACCEPT: union staleness + a pcrec-side hash + a compiler-mismatch flag.
- **msc1-8 / msc2-6** "a stale DEFAULT fails" puts every kit text change on the bench box; the hashed canonical instance is undefined. ACCEPT the definition fix (hash the form body with scaffolding normalized out). POLICY to FRANK: block / carried-stale with a listing flag and manager review / a declared cost-neutral equivalence row. Manager leaning: carried-stale + flag + review, never a landing gate.
- **msc1-9** answers can depend on the set through the size cap and fallback ladder (a near-cap artifact refused or re-rung). ACCEPT: the census records refusals and *_WHY/ladder tokens; §8.1 always includes near-cap artifacts plus a synthetic near-cap fixture.
- **msc1-10** `env` is declared and never checked. ACCEPT: derive the expected direction from the reader row's comparison and cross-check; envelope.py and recompute.py share no helper.
- **msc1-11** S947 and S952 miss their sites. ACCEPT both fixes (pointer == DEFAULTS read independently; a compiled-artifact manifest counted).

## Majors (measurement validity)

- **msc3-1** the relative unit is regime-dependent. ACCEPT: pin the unit's subject (streamed, fresh, long, no landings), its own A/A and a bimodal flag; cross-set comparison only within one method@ver.
- **msc3-2** subject regime not pinned per quantity. ACCEPT: a closed per-quantity METHOD CARD table (subject, lengths, rounds, A/A rule); the checker refuses a row off its card.
- **msc3-3** the envelope is conservative per column, not per decision; the safe direction belongs to the reader row. ACCEPT (with msc1-10); add the cross-member loss test; mark n=1 distinctly in the stamp class.
- **msc3-4** the 6.2% gate misquotes grid1's numbers and refuses most user boxes. ACCEPT: a third outcome (a PARTIAL set of passing groups with a printed summary), per-group gating, noise = A/A and fit spread in quadrature; no claim a local set beats the envelope without a replay test.

## Minors

msc1-12 (name the drift test as the gate), msc1-13 (reader coverage against each class default; lookup keys ⊆ declared readers), msc1-14 (bytewise LC_ALL=C sort; the literal rounding rule; -I name = header id; a PROVENANCE sha checker or drop it), msc2-8 (name-vs-path order; DEFAULT_MEASURES build override needs an uncommitted tree; `counters`/`members` in the header example), msc3-5 (a derived row with a null input is null), msc3-6 (the NULL rule on crossover denominators; a named rounding mode; the file sha covers noise_e6), msc3-7 (keep raw cells so fitted rows recompute), msc3-8 (restate the NULL rule incl. the sign-disagreement clause). All ACCEPTED.

## Unlocks (filed in the note's unlock section with triggers, not built)

The shared knowledge-source module (now, with the second loader); one data-mover census tool for findings/limits/measures; per-artifact dependency records (exact staleness, [ART-MGR] read-subset cache key); incremental re-measure (transitive staleness ∩ reader closure); D149 constants as measured rows (the gate itself); per-set out-of-sample replay (set A's picks on box B); regime-tagged sets; a key-only schema for pcrec's own engine rows.

## For Frank

1. **Q-MS-1, re-put:** M0/M1 compile with the latest set (D166 literal); the generic envelope becomes the default at M2. Recommend.
2. **Stale-default policy:** recommend carried-stale + a listing flag + manager review, never a landing gate.
