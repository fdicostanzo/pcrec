# msetdes report — [MEASURE-SET] design (2026-10-14, design only)

Deliverable: `docs/design/measure_sets.md` (rev 0). Nothing under src/, cli/, lib/, tests/ changed; no builds, no timing.

Recommendations (full pricing in the note):
- Format: sibling TSV (`[header]`/`[rows]`), integer `value_e6`, seven owner-vocabulary key dims, status measured/fitted/derived/null, closed derivation registry, provenance-free `values_digest`. Not an `.rxt` analysis block (no `include`, no counts).
- Store: `measure_store/<id>/<rev>/` (oracle_store shape), gen-tables embeds every non-synthetic rev, per-class DEFAULTS pointer, staleness computed from the kit's form hash.
- Loading: `--measures`/`measures` line, fill-only like `--analysis`; `<PREFIX>_MEASURES` stamp (one abi event, riding R17-b'); default-set change = census + re-pin, not abi.
- Kit: `mf_measures` + two return facts to request (lookups made; form hash); absent/null rows are skipped, never borrowed from another set.
- Envelope: per-row `env` max/min over official members; key missing from any member excluded; n=1 labelled composite.
- Tool: `pcrec-measure` driver, owner-supplied methods, reader-closure only, run-level refuse + row-level NULL, tier `local`.
- Checks: answers vs .rxt oracle under every set; python recompute of derived rows/units/digest; census with state check; sabotage S943-S952.

Open for Frank: Q-MS-1 (bare compile: generic envelope vs latest specific), Q-MS-2 (default change not abi), Q-MS-3..8 (tier `local`, dir name, noise gate 6.2% labelled unmeasured, stale-in-older-set read+flag, embed all revs, 16-hex digest).

Findings: the kit seam in R17-b' lacks a lookups-made report and a form hash; D166 "latest set" and D161 add. 12 "generic" agree only at one box; g* rows are fitted and not recomputable (counted instead).
Resume: a fresh agent can start M0 from the note's section 9.1.
