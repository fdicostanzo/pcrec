# process.md — crit-predspec6 (design)

Coordinator: opus (crit-predspec6). Started 2026-11-15T20:19:40Z.
Freeze: subject docs/design/predicates_draft.md @ 22ec6bf73bb10c714dec0249e7cface1ba19a5f8 (rev 6);
build/main HEAD aa9348f3d98a054bc87a0d8416eef9e2fb1ca103 (draft identical: git diff empty).
Rulings freeze: decisions.md @ bf8319fb8, plan.md @ 782502e99, COND-FAMILY.md @ 41ee4641b (all ancestors of aa9348f3d).
In-force ruling record: COND-FAMILY.md:846-878 (2026-11-15 "type picture"). No review worktree (design, no build).
Lenses: owner-criteria(+goals), census (one-symbol-one-meaning; + sibling/general-form standing questions),
simulate (§5.4 rules applied token by token to §12 + every other example), rulings (CF vs draft; stale pre-rev-6 text).
Not run: cost-and-overlap, emitted, measurement (out of scope per launcher); premise folded into rulings/owner.

## Agents
- 4 critics launched ~20:15Z together (opus, background, unnamed): owner (a8f8e769, 34 tools, 5.7 min), census (ab3ae54b, 33 tools, 9.0 min), simulate (a9092387, 23 tools, 5.2 min), rulings (a1ad859c, 24 tools, 4.7 min). All four returned in the launch turn; final replies NOT delivered ("ended without SubagentHandback") but every file complete; lanewatch DONE rc=0 for all four. No resend/nudge needed.
- Findings raised: owner 12, census 26, simulate 12 (10 CONFIRMED, 2 SUSPECTED), rulings 13 (12 CONFIRMED, 1 SUSPECTED) = 63 raw.
- Brief confusion: COMMON's first lanecheck wording "prints DONE" was wrong (lanecheck prints `DONE rc=1` on failure); fixed before launch.
- Overlaps: hole-guard (OWNER-4/RUL-1/CENSUS-10), bracket order (OWNER-3/CENSUS-1/RUL-5/SIM-6), record exception (OWNER-11/CENSUS-3/SIM-12), `:` split (OWNER-8/CENSUS-4), contains anchoring (SIM-1/CENSUS-12), each_group(&) (CENSUS-7/SIM-4/RUL-7), dot (OWNER-9/CENSUS-24), L9 (SIM-2/CENSUS-6), L36 (SIM-3/CENSUS-8), records maps (RUL-12/CENSUS-23), search match-time (OWNER-10/RUL-9).
- 20:30Z FREEZE DRIFT: main 8d3c348f2 added CF:880-887 (owner note: a search result is the ARRAY of all results) mid-round. Per skill §3.1, fresh critic 'drift' on §2.6 + dependents vs the note. Verifier launched in parallel.
- 20:31Z drift critic (opus, a1d75871, 29 tools, 4.3 min) and verifier (sonnet, a694412b, 37 tools, 5.1 min) launched together; both returned in the launch turn without a delivered reply; files complete; lanewatch DONE rc=0.
- Verifier: 16 items: HOLDS 7 (V1, V5, V6, V10, V13, V14, V11 mostly), PARTLY 8, REFUTED sub-claims 6 (listed P6-18). No REFUTED rests on a crafted input (design round), so no coordinator re-run needed.
- Draft written 20:38Z: 71 raw -> 18 consolidated (FIX-NOW 10, PLAN 5, DOC 1, REJECTED 1, NOTED 1). Time from start to draft ~25 min.
- Blinding: no leaks noticed; critics read only COMMON-named files (not audited beyond their citations). No review worktree created, none to remove.
- Rulings re-diffed at each return and at hand-back: only CF:880-887 (8d3c348f2) moved; decisions.md/plan.md unchanged.

## Process observations
- Every nested agent (6/6) ended "without SubagentHandback": final replies are lost, files are everything. The skill's files-first design carried the round with zero resends.
- Overlap was heavy and useful as corroboration: the hole-guard contradiction was found by 3 lenses independently, the tuple reason by 4. For a notation subject, owner-criteria and census overlap ~40%; a 3-critic round (census, simulate, rulings) would have found all answer-level items.
- The census lens was the most productive (26 raw, 9 consolidated items touched); simulate found both answer-level items with repros.
- lanecheck prints "DONE rc=1" on failure; COMMON's first wording ("until it prints DONE") would have let a critic end on a failing check. Caught before launch.

## Proposed changes
1. skill §4 lens table: add a row "D | a grammar or notation (marks, keywords) | census | classify every occurrence of each mark and key word by meaning; report any with two | opus" (evidence: 26 findings, quantified the comma criterion 200/200).
2. skill §5 COMMON template: say "until lanecheck exits 0 (DONE rc=0)", never "until it prints DONE" (evidence: this round's near-miss wording).
3. skill §4 staffing note: when owner-criteria and census both run on a notation subject, brief owner-criteria on ECONOMY (counts, needed-by-a-case) only, leaving per-mark meanings to census (evidence: ~40% overlap).

## Framework notes
- Coordinator pattern fit well for a design round with no build: ~25 minutes, one batch launch, one drift critic, one verifier, no manager turns spent. The mid-round ruling re-diff (skill §3.1) caught an owner note on the subject's own section that would otherwise have made the review stale on arrival.
- 20:39Z after hand-back: simulate, census and drift each relayed their summaries by SendMessage (their handback had failed because the coordinator turn had ended). All three summaries match the files already used in the draft, so nothing changes.
