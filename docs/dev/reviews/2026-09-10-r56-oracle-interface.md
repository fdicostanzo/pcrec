# r56 — the oracle interface + answer store design note (lane oraiface)

2026-09-10. Two read-only sonnet critics on worktrees/oraiface's
docs/design/oracle_interface.md: r56cons (consumer fidelity — every
survey number re-derived from source) and r56mech (mechanism design —
serialization/keying/store attacks). Verdict: the survey is exact
(every population number reproduces; the DOC-DRV exclusion is stronger
than written; bundle.py's transport generalizes with no wire-format
impedance), but the mechanism has TWO deterministic-failure blockers
and the ladder one misattribution. Revision lane `oraiface2` applies
R56-1..8; the B13-contract verify pass RUNS before merge.

## Dispositions

**R56-1 (MECH-1 + MECH-3, BLOCKING) — serialization injectivity.**
The note's escaping is ambiguous between the tree's TWO vocabularies
and its own §12 example is non-injective (unescaped backslashes: a
pattern's literal `\`+`t` collides with an escaped raw TAB —
deterministic, on ordinary patterns). FIX: the canonical serialization
is the rxt_format.md:458-474 FIVE-ESCAPE TSV-FRAMING SUBSET
(`\\ \t \n \r \xNN`), backslash escaped FIRST, stated normatively
with the producer rule spelled out, both vocabularies named and the
quoted-context one explicitly rejected, §12's examples corrected, and
the trailing-backslash edge case a stated test vector.

**R56-2 (MECH-2, BLOCKING) — limits join the key.** match_limit/
depth_limit/heap_limit are answer-affecting (this tree's own
sr_oracle/atomicity/leftrec probes vary them to FLIP answers) and the
design's own giveup answer state anticipates exactly that population.
FIX: the limit triple joins OracleId.config with explicit defaults;
§8 Claim 1 is restated over the widened key; a giveup answer is
cacheable ONLY under fully-keyed limits. §3's exclusion argument
stays for NO_UTF_CHECK/UCP (both verified sound).

**R56-3 (MECH-10, MUST-FIX) — the serialization itself is versioned.**
A store-format/serialization-rule version field (per-file header) so
an encoding change is a CLEAN MISS exactly as an oracle version bump
is — §8 gains Claim 4.

**R56-4 (MECH-4 + MECH-7, MUST-FIX) — the store self-checks.** Every
per-(OracleId,kind) file's header carries its own row count +
provenance (the artifact_size_log.tsv precedent's ACTUAL shape, which
the note cited but did not follow); readers verify a fetched row's
question text equals the query's serialization before trusting the
answer (the cheap collision/corruption tripwire).

**R56-5 (MECH-5, MUST-FIX) — store discipline stated.** Regeneration
is sorted-by-hash with a DUPLICATE-HASH DETECTOR as a check (also the
MECH-1-class tripwire); the owning lane regenerates, appends never
land unsorted in a committed store; the merge protocol (re-derive on
conflict, never hand-merge rows) written down.

**R56-6 (cons-F1, BLOCKING) — the two owed items un-conflated.**
S-U6/S-U9's closing witnesses are next_pos/back_step ill-formed-
subject cells — they ride the MATCH-AT kind's ill-formed population,
a LATER ladder rung. What uprops-first discharges is the STAGE-5
drift-zeroing 10.46 arm (S-U12's neighborhood). Fix both places in
the note + the lane report's echo; wake.md's lane-3 line inherits the
correction at the next rewrite.

**R56-7 (cons-F2, MUST-FIX) — the sixth kind.** pattern-info
(a compiled pattern's structural properties: the NAMETABLE/NAMECOUNT
ordering differential that D59's rx_info.groups layout rests on) is a
real, oracle-consulted, pure-function-of-(pattern,config) question no
current kind expresses. FIX: `pattern-info` joins the closed set
(six kinds; store customer deferred), and the kind-set gains an
EXTENSION RULE (a kind addition = store-format minor bump, existing
kinds never re-keyed).

**R56-8 (MECH-8 + MECH-9, NOTE→required text) — named invariants.**
newline/BSR and JIT-vs-interp are excluded from config BY MEASURED
FACT (no adapter varies them today) — the note names them explicitly
with the rule that an adapter varying either must widen config first.

**Ratified as-is** (both critics + the note agree): 16-hex hash (the
birthday math holds ONCE R56-1 restores injectivity — the threat was
never the hash), top-level oracle_store/, name-accept stays its own
kind, measure-before-deciding on the membership table's git posture
(MECH-11 bounds it low-single-digit MB — fine either way).

**Also in the revision** (cons survived-attack side-finding):
tests/uprops/uprops_oracle.c's header still describes the retired
dlopen shim — one stale-comment fix, D98's residue.

## Survived adversarial verification (recorded)

All population numbers exact (149,804 / 62,872 / 1,053 / 91-measured
+387-derived-and-flagged); the ssh stdin transport has no wire
conflict (argv baked as %r — a batch embeds identically); DOC-DRV's
exclusion structural (the survey never asks an oracle anything); the
UCP/NO_UTF_CHECK exclusions verified in the binding's own code; no
JIT anywhere in today's bindings.

## Outcome

Revision lane oraiface2 (sonnet) applies R56-1..8 + the stale-comment
fix in one commit; the completion-contract VERIFY PASS runs (a fresh
agent confirms every disposition against the revised text before
merge — B13's lesson, practiced); then the manager merges. The
implementation (store + uprops instance) opens after, per the
original lane plan.
