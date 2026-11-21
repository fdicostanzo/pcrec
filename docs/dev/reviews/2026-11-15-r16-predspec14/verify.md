# verify.md: round predspec14 (inline verification by the coordinator, per SKILL §6.2: every CONFIRMED finding is a quote claim or a one-script oracle repro)

Calls: from $R/.coord/v/: `timeout 120 python3 -I $R/simulate/sim.py`, `... $R/fixinduced/tuple_check.py`,
`... $R/fixinduced/bodies_check.py`; each output byte-identical to the critic's committed .out (diff -q silent).
Quotes: `sed -n` on $R/subject/predicates_draft_rev14.md lines 272, 1096-1102, 1110-1111, 1123-1135, 1229-1234,
2014-2017, 2053-2058, 2420-2448, 3613-3626, 3643; rulings record CF:1103-1111.

- SIMULATE-1 HOLDS: l.2422-2424 fire on any anchor in a filter role's own text; sim rows S1-S1e show the anchor changes the answer (`/\d+/ & /0*^5/` 3-4 vs 1-4 without).
- SIMULATE-2 / FIXIND-8 HOLDS (one item): l.2423 "i.e. an anchor whose innermost scoped match is that filter role's stretch" vs the table row l.2436 "a parameter the body splices into a HOLE: no"; a hole opens no scoped match (l.2297-2299).
- SIMULATE-3 HOLDS: table row `anchored(...)` "no" with the reason "the author writes no anchor" (authorship), vs CF:1110 "a user macro with the same body behaves the same"; sim S3.
- SIMULATE-4 HOLDS: sim S2 (four with/without pairs identical); the row's reason column l.2436 "so it MEANS something".
- SIMULATE-5 HOLDS: one message text l.2444-2446 for every place.
- SIMULATE-6 HOLDS (oracle S7: `tagged(/^a/)` no match); the text gap is a reading.
- SIMULATE-7 not verified (SUSPECTED; text ambiguity only).
- FIXIND-1 HOLDS: l.3624 spells `(t1: ==lo1, t2: ==lo2, ...)` without `padded`; tuple_check: 3-field literal 60/448 differ, all-padded 0/448; L20 (canonical numerals) l.346.
- FIXIND-2 HOLDS: l.1100-1102 "without it a top-level alternation in rx would split the body" vs §3.3 RULE l.1231-1233 "A hole is an atom ... `/${x}d/` = `(?:a|b|c)d`".
- FIXIND-3 PARTLY: bodies_check reproduces (170 + 27 cases, 0 differ), but it EMULATES the document's `.index`/`count`/computed-label semantics in Python (no engine for them exists), and the bodies need helper bindings that the document does not say a macro body may carry. The refutation of "NOT EXPRESSIBLE" for `length` and `month_numbered` holds under the document's own constructs; the caveats are the finding's own.
- FIXIND-4 HOLDS: l.1096-1099 (argument "NOT a role of its own ... follows from the transform's BODY") vs l.1130-1131 ("today their argument is matched whole by this section's sentence about modifiers") and table l.2440.
- FIXIND-5 HOLDS: l.1110-1111 quotes CF:1110-1111, which is the RECORD's third-person sentence; the owner's words at 20:45 are only CF:1105.
- FIXIND-6 HOLDS (quote: CF:1144 "The manager's judgment given to him").
- FIXIND-7 HOLDS: l.272 "the warning's name `anchor.operand`, text and reach (LEAN, §13 O65)".
- CENSUS-1..11: quote/count claims, spot-checked l.2440 vs l.2014-2016 (CENSUS-1) and the §5.4 `${ }` row vs E-HTTP (CENSUS-8: E-HTTP final is `anchored(block)`); HOLDS. Counts not re-run.
VERIFY COMPLETE
