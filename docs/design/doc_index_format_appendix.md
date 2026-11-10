# Appendix to doc_index_format.md (rev 3): census, owner table, cite forms, worked examples, readers, T1 plants

Companion to `docs/design/doc_index_format.md` rev 3 (lane docfmt3,
2026-11-10; rev 2 by lane docfmt2). Holds the worked tables so the design
itself stays readable. Counts are at main 6638e3679 unless marked;
decisions.md is byte-identical at e9687de27, the re-check's build tree.
Finding ids: `F<n>` are round r1's (`docs/dev/reviews/2026-11-10-r1-docfmt.md`),
`R2-<n>` the re-check's (`docs/dev/reviews/2026-11-10-r2-docfmt2.md`). Ids,
not line numbers, name places in the ruling files (C8, §2.4).

## A. The decisions addendum census (F1, F17; rev 3: R2-10, R2-13, R2-15)

**The scan** (design §5.2): every line; an optional prefix (`>`, a list
marker, `**`, `#`s) is stripped and kept as `class`; a CANDIDATE carries
`addend` (any case) or `Dn add.` in the remainder's first 120 characters.
**The marker rule:** the LEADING LABEL (the bold span; the heading text; a
plain line's start; each cut at its first ` — `, ` -- `, `(` or `:`) must
fully match

    ^(D[0-9]+ )?([A-Z][A-Z0-9-]*[0-9] )?((first|second|third|fourth|fifth|FIRST|...|FIFTH) )?
     (addendum|ADDENDUM|Addendum)( [0-9]+(\.[0-9]+)?[a-z]?| [0-9]{4}-[0-9]{2}-[0-9]{2})?
     ( note| NOTE)?(,.*)?$

(one line in the code), and a `plain`-class label must begin with its id.
Every other candidate is a MENTION, excluded with that reason (the census
prints both lists). Prototyped over decisions.md at e9687de27
(`$PCREC_TMPDIR/scratch/docfmt3/scan.py`, not committed; 1.0 writes its own):

| | count | by class |
|---|---|---|
| candidates | 250 | |
| MARKERS | 193 | h3 71, bold 85 (62 id-named, 23 id-less), bullet-bold 17 (id-less), plain 13, h2 7 |
| mentions | 57 | plain 33 (prose and two WRAPPED sentences whose line starts "ADDENDUM, is ..." and "addendum 2 — ..."), bullet-bold 17 (labels like `**Correction:**`, `**Reading (manager):**`), bold 4, bullet 3 |

Rev 2's "148" was a hand total and is withdrawn; the number of record is the
census's count at the unit's build commit (the scan above gives 193 = the
critics' 180 prefix-form markers + the 13 plain-line ones).

Classes the earlier spelling lists missed:

| missed class | instances | examples |
|---|---|---|
| `**Dn addendum[ k] (...)**` (bold, id-named) | 62 (54 `**Dn addendum`, 8 `**Dn ADDENDUM`) | D147 ×16, D148 ×5, D151 ×7, D144 ×4, D45 ×4 (ordinal words) |
| `**RULING-5 ADDENDUM` | 2 | D47's a3 and a4 |
| `### D31 ADDENDUM` (upper case) | 1 | D31 |
| PLAIN-LINE `Dn ADDENDUM[ k] (...)` (no typography) | 13 | D122 ADDENDUM, 2, 3, 4; D123 ADDENDUM, 2, 3, 3a, 4-8 |

Placement against the `^## Dn\b` heading cut (the cut rows_check.py and every
`grep '^## Dn'` recipe use):

| where the addendum sits | count | members |
|---|---|---|
| `###` heading inside a LATER entry | 17 | D163 ×5 in D167; D94 in D112; D161 ×2 in D162; D89 in D94; D111 in D112; D104 in D113; D156 ×2 in D157; D166, D165 ×2, D162 in D167 |
| bold marker inside a LATER entry | 17 | D51 in D52; D69 in D79; D76 and D40 in D81; D144 in D147; D148 ×5 in D149/D150/D151; D147 ×4 in D149, ×1 in D155, ×2 in D159 |
| PLAIN-LINE marker inside a LATER entry | 2 | D122 ADDENDUM 4 in D123; D123 ADDENDUM 8 in D124 |
| own `## Dn ADDENDUM` heading after a later entry | 4 | D47 ×2 after D48; D58 in D96's span; D58 in D154's span |
| own `## Dn ADDENDUM` heading right after its entry | 3 | D106 ×3 (outside D106's cut) |
| id-less continuation inside a foreign entry | 3 | D89's "Addendum 2/3/4" inside D94 (owner D89: tree cites `D89 addendum 4` in src/parse/rxt_compose.c and src/gen/emit_vm.c) |

So 46 sit outside their own cut (36 id-named in a later entry, 7 own `##`
headings, 3 id-less). The census GATE (§5.2 (b)) fails on any line-start
`Dm ADDENDUM|addendum|add.` inside a foreign entry with no table row, so a
future plain-line misplacement cannot pass silently.

Numbering shapes (each with a §2.2 rule):

| shape | instances | cites | rule (§2.2) |
|---|---|---|---|
| duplicate number | `### D162 addendum 4` twice (the second inside D167) | 31 | first keeps a4; second takes the next free number + `(was: "...", second of two)`; the old label aliases to both |
| sub-number | D155 `Addendum 4.1`, D166 `Addendum 1.1`, D123 `ADDENDUM 3a` | ~28 | `.a4.1`, `.a3a`; C6 orders 4 < 4.1 < 5 and 3 < 3a < 4 |
| note on an addendum | `### D168 addendum 3 note` ×2 | 5 | `class=note`, `new_id` `D168.a3#1`/`#2`: a `####` sub-heading inside D168.a3, label verbatim. Only the `addendum K note` form; D47's "RULING-5 ADDENDUM, LANDED NOTE" is the numbered a4 (ruled row) |
| ordinal words | D45 third/second/fourth (filed 3, 1, 2, 4); D47 SECOND | 54 | an ordinal IS a number (second = 2); addenda sit in number order |
| undated label | "same exchange", "same day", "same session" (D89, D60, D150, D163.a1, D166, every D123 plain-line marker) | — | date inherited from the nearest earlier dated marker of the same owner (`inherit:` in the table); 28 of 193 |
| unnumbered first, numbered rest | D84 (ADDENDUM, 2, 3); D147 (one unnumbered, then 2-16: a14 in D155, a15-a16 in D159); D122 (ADDENDUM, 2-4); D123 (ADDENDUM, 2-8 + 3a) | — | the table's `new_id` is ruled; the default (lowest free number in date order) is checked against today's cites |
| mixed spellings in one entry | D163 a1-3 bullets, a4-7 `###`, a8-12 `###` inside D167 | 107 (a7-12) | one owner, numbers kept |

Other census facts (F17, R2-15): decisions headings come in three forms (155
end `(date, who)`; 33 are `## Dn — YYYY-MM-DD — title`; D27 and D28 bare).
D98's heading wraps onto TWO continuation lines (the heading line plus the
next two); the join is declared for D98 ALONE, and plant P11 applies it to
another heading. "SUPERSEDED" is 5 upper-case lines, 47 "supersed*": every
`sup>`/`part>` state is a writer's judgement.

## B. The addendum OWNER TABLE, its control plants and witnesses (F1, F5; rev 3: R2-11, R2-12, R2-14)

`docs/dev/doc_index/decisions_owners.tsv`, committed in unit 1.0. Produced by
`scripts/doc_census.py` (NOT the converter, and not its author's code: §5.2),
plus hand rulings. One row per MARKER of appendix A's scan:

| column | content |
|---|---|
| `census_rev` | the commit the scan ran on (each landing re-run appends rows, never rewrites old ones) |
| `old_line`, `old_end` | the EXTENT: the marker line to the line before the next marker or `## ` heading; `old_end` RULED for a marker inside a foreign entry whose host text resumes after it (a migration record, exempt from C8) |
| `extent_hash` | sha256 (12 hex) of the extent's bytes. Replaces rev 2's `body_hash` (the first line after the marker), which meant nothing for the 33 one-line addenda followed directly by a marker or heading (D147 a4, D151 a1-a7) |
| `old_label` | the FULL marker text (heading text, bold span joined across its wrap, or a plain line's label through its first `(...)` group); cut only for display |
| `class` | h2, h3, bold, bullet-bold, plain, quote; `note` for `addendum K note` |
| `owner` | the `Dn` the addendum belongs to |
| `owner_src` | `label` (the marker names its id), `enclosure` (id-less, inside its own entry), `ruled` (hand ruling, with `note`) |
| `old_number` | as written: `4`, `4.1`, `3a`, `second`, `2026-10-24`, `-` (none) |
| `new_id` | `D163.a7`, `D155.a4.1`, `D162.a13`, `D168.a3#1` (note) |
| `date` | resolved date, or `inherit:<date>` |
| `who` | Frank, owner, manager or kit when the label's date/who group names one in its first two items, else `-` |
| `title` | by the rule below, cut at 120 characters on a word boundary + `…` |
| `cites` | count of tree cites of `owner` + `old_number` in any alias spelling (C), at `census_rev` |
| `note` | the ruling's reason for `ruled` rows; `second of two` for duplicates; `title ruled` when the manager overrides a title |

**Title rule** (first match; prototyped: 136 / 45 / 7 / 5 of 193 rows):

| # | when | title |
|---|---|---|
| 1 | the label minus its leading words (id, tag, ordinal, addendum, number, `note`) and minus its date/who `(...)` group leaves text | that text (`### D47.a1 — 2026-08-16, Frank: F-1 ruled: K does NOT vary per-quantifier in v1; ...`) |
| 2 | an inline marker (bold or plain) whose label is only words + group | the text after the label on its line, joined across the paragraph's wrap up to its first sentence end |
| 3 | still empty | the group's remaining items (not the date, the who, or "N-th session"/"same day" words) |
| 4 | still empty | `(untitled)` |

The heading is cosmetic for G2 (the label survives verbatim); the rule makes
it deterministic and census-side, and the control checks the heading equals
the columns (clause iv).

Rules: every id-less marker (40 today: 23 bold, 17 bullet-bold) is listed for
a hand ruling, and the census refuses to finish while one is unruled; the
ruling cites its evidence (tree cites of the owner and number, the "same
exchange" text). The converter refuses a marker with no row (matched by
`old_label` + `extent_hash`).

**Control plants** (`doc_control.py --selftest` over a toy original + its
correct conversion; each plant must go RED by the clause named, and 1.0's
ACCEPTANCE lists every one; P1-P19 are the re-check's faith plants, kept
under their ids):

| plant | the wrong conversion | red by |
|---|---|---|
| P1 | an addendum under the wrong owner (table right) | (ii), (iii) |
| P2 | a body line moved to another entry | (iii) |
| P3 | the first line of an addendum moved to the next | (iii), `extent_hash` |
| P3b | NON-first lines moved between two addenda of one owner | (iii) |
| P4 | an addendum line moved into its owner's body | (iii) |
| P5, P6 | a line dropped; a line duplicated | (iii) |
| P7 | a fence dropped plus a fence duplicated in one owner | (iii) |
| P8 | a body heading (e.g. D30's `### 1. Resolution is by DECLARED RANK`) dropped | (iii) |
| P9 | a body heading moved to another entry | (iii) |
| P10 | an entry title rewritten | (iv) |
| P11 | D98's join applied to another heading | (iii), (iv) |
| P12, P13 | a body line rewritten into `(was:)` / `rulings:` form | (iii), (v) |
| P14 | a blank line dropped (two paragraphs merge) | (iii) |
| P15 | two lines reordered inside an entry | (iii) |
| P16 | an addendum heading's date or title differs from the table | (iv), C3 |
| P17 | an invented `### D2.a1` heading inside a body | (ii) |
| P17b | a real addendum split by an invented `### D3.a3` | (ii), (iii) |
| P18 | an extra `(was: "...")` line with a false label | (v) |
| P19 | a `rulings:` block written in unit 1 | (v) |
| P20 | (census) a plain-line `D122 ADDENDUM 4` inside D123: the census must emit a row with owner D122, and the gate fails when that row is deleted from the table | gate (b) |
| P21 | a one-line addendum (followed directly by the next marker) moved | (iii), `extent_hash` |

The multiset check (rev 2's (iii), now the sixth check) still catches P1, P2,
P5, P6, P12, P13; the plants above it alone could not catch (P3b, P4, P7-P10,
P14-P19) are why the extent comparison exists.

**Unit 1 acceptance witnesses** (named checks in the control, chosen by the
review, not by the converter's author):

| witness | what must hold after conversion |
|---|---|
| D47 | `entry D47` prints D47.a1-a4 (two former `## D47 ADDENDUM` headings after D48, two inline RULING-5 ones, a4 the LANDED NOTE) and no D48 text |
| D89 in D94 | D89.a1-a4 inside D89 (a2-a4 by ruling); D94 holds none of them |
| D122 | a1-a4 inside D122, a4 moved out of D123; each a plain-line label kept as its first body line |
| D123 | a1-a8 with a3a, a8 moved out of D124; D124 holds none of them |
| D162 a4 | two addenda, a4 and the next free number; `entry 'D162 addendum 4'` prints both |
| D155 a4.1, D166 a1.1, D123 a3a | ids `D155.a4.1`, `D166.a1.1`, `D123.a3a`; C6 order holds |
| D58 | both `## D58 ADDENDUM` headings (in D96's and D154's spans) inside D58 |
| D84 | unnumbered first → a1; ADDENDUM 2, 3 → a2, a3 |
| D147 | a1 (the unnumbered one) through a16, including those inside D149, D155, D159 |
| D45 | ordinals second/third/fourth → a2/a3/a4, in number order |
| D168 | both "addendum 3 note" rows as `####` sub-headings inside D168.a3 |
| D163 | a1-a12, a8-a12 moved from D167; 107 cites of a7-a12 resolve unchanged |
| D26 | the three unnumbered markers → a1-a3 by date; a3 with its `(was: ...)` line |

## C. Cite forms after the split (F2; READERS-7's counts, tree minus the tracker files; rev 3: R2-19)

| form | count | after unit 1 (decisions) / 2 (plan) / 3 (known) |
|---|---|---|
| bare `Dn`, `Kn`, `Un`, `[TAG]` | 36k `Dn`, 26k `Kn` tree-wide | land on the index line |
| `decisions.md Dn` / `known_issues.md Kn` / `upstream_issues.md Un` | 122 / 226 / 48 | land (the index keeps the file name) |
| `plan.md [TAG]`, `grep -n '^- \[TAG\]'`, STATE greps | 184 / skills / 9 | land (head line kept) |
| `[TAG]`'s trigger/next/refs/status/charter | 175 | details only after unit 2: `entry TAG -l 1` |
| `Kn` Witness / Fix | ≤ 410 | details only after unit 3: `entry Kn -l 1` |
| `Dn add. k`, `Dn addendum k` | 1,553 / 941 | `entry` alias → `Dn.ak` via the owner table; plain grep lands on the kept label |
| `Dn ADDENDUM`, `Dn SECOND ADDENDUM`, unnumbered `Dn addendum` | 84 / — / 1,325 | same; an unnumbered alias prints every addendum of Dn whose `old_number` is `-` |
| `Dn add. k.m`, `Dn ADDENDUM 3a` | 20 | `Dn.ak.m`, `Dn.a3a` |
| DATE alias `Dn addendum YYYY-MM-DD` (D26 addendum 2026-10-24, D93 addendum 2026-09-16, D138 addendum 2026-09-30) | 3 | resolves by the table's `date` (routing row 1); never read as number 2026 |
| `addendum k of Dn` | 4 | resolver form, same row as `Dn addendum k` |
| dotted `Dn.k` (a ruling number in the body: D47.6, D71.1) | 1,011 | `entry D47.6` prints D47 at level 2 with the trailer `ruling 6 is in the body`; C13 checks Dn exists |
| `decisions.md:N`, `known_issues.md:N` | 161 / 25 | BREAK (lines move): the live ones rewritten to ids in their unit (E); the rest exempt |
| `grep '^## Dn'` recipes (review COMMONs, rows_check) | 11 | land on the details file only; recipes move to `entry` / `entry --rev` |
| `plan_row_bodies/X.md` | 36 | BREAK at unit 2 (§10 unit 2) |

The resolver (`scripts/doc_cites.py`, unit 1.0) runs BEFORE conversion
(through the owner table on the old file) and AFTER (through the headings and
the alias map), over the cites outside C8's exemption prefixes. Acceptance:
every cite that resolved to a set of owner-table rows before resolves to the
same set after. A cite that dangles BEFORE (the PROPOSED `D155 addendum 6` /
`D155 add. 6` ×5 in docs/design/memfn/target_seam.md and
target_seam_units.md is the known case) is written to
`docs/dev/doc_index/dangling_before.tsv` (file, cite text, reason); from unit
1 on, C13 fails on any dangling cite NOT in that baseline, and fails on a
baseline row whose cite now resolves or is gone (the baseline only shrinks).
A design that proposes a future addendum therefore either names it as text
the resolver ignores (an id-less phrase) or adds its row in the same change,
visible in review.

## D. Worked examples (F4): statements that pass the §5.3 procedure

Each statement was written from the whole entry plus its inbound list
(`doc_cites.py --inbound`, prototyped for this appendix over the build tree),
and checked against the seven questions. A ruling is one operative clause a
session could act on by itself (§2.1); rationale, provenance, revisit-when,
measured facts and LANDED notes are not rulings.

**D26** — inbound: 22 later entries cite it (D27-D36, D42, D56, D68, D75, D89,
D92, D94, D142, D164, D178, D180, D181, D189); none carries a supersede/amend
verb; all apply it. State `live`.

    - D26 pcre2-compat-tiers live a3 — PCRE2 compatibility: matching and which syntax is real are exact; accept all PCRE2 accepts (more allowed); follow the standard over an evidenced PCRE2 bug; never chase unimplemented-construct wording. (+4 more) {oracle 10.46 offsets drift}

    rulings:
    r1* matching (tier 1) and recognition (tier 2: real PCRE2 syntax, which module owns it) are exact
    r2* diagnostics for unimplemented constructs are functional ("requires module 'X'" discharges); never-implementing constructs get a clean rejection and a name
    r3 nothing already pinned is removed (tests/reject wording, verb form bits, PC-3 identity stay)
    r4 a PCRE2 upgrade that reddens a check: tier 1/2 is a finding to follow; tier 3/4 is drift: journal it, demote the assertion, do not chase it
    r5 pin pcrec's own diagnostic offsets against pcrec's own convention, never against PCRE2's
    r6 the source of truth is the PINNED oracle (libpcre2 10.46); a version bump is a deliberate re-measurement event (a1)
    r7* where PCRE2 has an evidenced bug, follow the standard, record it in upstream_issues.md, admit it in the differential; claim "compatible", never "the same" (a2)
    r8* accept every pattern PCRE2 accepts; more is allowed where it matches correctly, each excess listed with its oracle plan (a3)

Statement 200 chars, line 276 B; 8 rulings, 4 starred, `(+4 more)`. Rev 1's
keyword `{diagnostics floor 10.46}` paired a3's "floor" with the oracle
version, a false keyword (Q7); replaced.

**D47** — inbound: D49 (settles the rider's re-opened −1 collapse and the work
bound's default; its supersede verb names D42.3, not a D47 ruling), D58 and
D62 (D62 builds a3's cure), D158. No D47 ruling is replaced: state `live`.
Rev 1's "K is one per-artifact named constant (8)" was stale wording: 8 is
the named DEFAULT, and the size-term ladder now picks K per pattern
(docs/spec/tuning.md §2.10¶3), which a1's "never per quantifier" still allows.

    - D47 brep-counterk live a4 — Bounded repeats: each quantifier walks possessify, rung select, counter-K; K is one value per artifact, never per quantifier (named default 8); frameless forward work has its own bound and code. (+6 more) {ENG-BREP ALLOW/DENY}

    rulings:
    r1* each quantifier walks possessify, rung select, counter-K; the possessify pass is built first
    r2* K's shipped default is 8, a named constant in the constants file, never inline
    r3 forcing surface: gcc-style ALLOW/DENY flags plus a K value parameter; a denied strategy in a stamp fails the test; denying both fallbacks is a compile error; `(*...)` hints deferred
    r4 third-amendment consequence (b) is struck and replaced in the plan row
    r5 the `$`-follow exemption ships gated live; order and path decisions within bounds are the manager's
    r6 the lazy conjunct is accepted; its 20 cells join the .rxt corpus as guards
    r7* K never varies per quantifier in v1; the clamp is deferred to [ENG-CLAMP] (a1)
    r8* frameless forward work gets its own bound, rx_info field and RX_ERR_ code; the step budget keeps its meaning (a2)
    r9 until the first release, API/ABI changes are on the table; "final" means "stable absent a reason" (a2 rider)
    r10 multiline resolves at parse time onto the `$` node; ruling 5's test obligation widens to the scoped cells (a3)

Statement 194 chars, line 258 B; 10 rulings (a4 is a LANDED note), 4 starred,
`(+6 more)`. Level 1 adds `later: D49* D58 D62 D158` (§2.3).

Details headings, D47, as appendix B's title rule derives them (bodies
verbatim, not shown; rev 3 replaces rev 2's hand-written headings, R2-14):

    ## D47 brep-counterk — the six [ENG-BREP] §9 rulings (Frank, 2026-08-16, twenty-fourth session continuation)
    rulings:
    r1* each quantifier walks possessify, rung select, counter-K; the possessify pass is built first
    ...
    ### D47.a1 — 2026-08-16, Frank: F-1 ruled: K does NOT vary per-quantifier in v1; the clamp is DEFERRED to its own row
    (was: "## D47 ADDENDUM — F-1 ruled: K does NOT vary per-quantifier in v1; the clamp is DEFERRED to its own row (Frank, 2026-08-16, twenty-seventh session, on the R25 panel)")
    ### D47.a2 — 2026-08-17, Frank: F-2 ruled: the uncharged forward work gets its OWN bound (settlement 4); plus a pre-release ABI rider
    (was: "## D47 SECOND ADDENDUM — F-2 ruled: the uncharged forward work gets its OWN bound (settlement 4); plus a pre-release ABI rider (Frank, 2026-08-17, twenty-eighth session, on the R25 §7 arc)")
    ### D47.a3 — 2026-08-18: Ruling 5's LIVE-check requirement is NECESSARY BUT NOT SUFFICIENT as shipped: the gate reads `cx->mods.multiline` at…
    **RULING-5 ADDENDUM (2026-08-18, thirty-third session, from the R30
    ### D47.a4 — 2026-08-19: The cure above is BUILT, per D62's flag ruling (which closed the Q8 the paragraph above still calls open):…
    **RULING-5 ADDENDUM, LANDED NOTE (2026-08-19, thirty-fourth session,

a1/a2 take title rule 1, a3/a4 rule 2 (no `who`: their groups name none).
The `(was:)` lines carry the FULL old heading; the inline labels stay as the
unchanged first body lines.

`scripts/entry D47 -l 1` prints the index line, the rulings list, these four
`###` lines and `later: D49* D58 D62 D158`.

**D191** — inbound: none (the newest entry). State `live`.

    - D191 span-arms-go live — Span arms: build E1 R1 E2 L1 L3 (L2 after kit R-38); a run crosses the seam as one uncut span of byte sets at signed offsets; repeats count as copies; zero-width items do not cut it. (+11 more)

    rulings:
    r1* BUILD GO for E1, R1, E2, L1, L3; L2 after the kit's R-38 plus one readiness critic
    r2 span_arms.md §12's proposed decision is adopted as amended
    r3 each unit's census is a measurement record, not a gate; a unit with no mover anywhere stops and reports
    r4 the scan byte may come from any run position; the kit picks the scan position and the verify extent
    r5* the run crosses as ONE uncut span with byte sets at signed offsets from the attempt start
    r6 nothing about consumption crosses the seam
    r7 `<PREFIX>_REQ_BYTE` keeps its meaning (a byte every match consumes), chosen by pcrec
    r8 the pcrec/kit agreement check retires
    r9* repeats count as their copies (`X{2}` as `XX`; `X{2,5}` gives its two fixed copies)
    r10* zero-width items stop cutting the run, all in unit E2
    r11 a run outside the match is ONE run value, every reader raised together
    r12 the lookbehind step back is capped at the declared lookbehind length
    r13 L3 builds now, ahead of A-POSDOM
    r14 [REWRITE-ADJ]'s design starts now
    r15 the prefix skip after a proved run stays [MATCH-KNOWN]'s; R-38 asks the kit how far it verified

Statement 182 chars, line 222 B; 15 rulings, 4 starred, `(+11 more)`. A
build-go entry with many sub-rulings is why the rulings list exists: a
200-char sentence cannot carry 15 rulings, and an uncounted omission is what
rev 1's three examples all committed.

**The planted-line witnesses** every batch critic must catch (§5.3): D42 `live`
keeping the −1 collapse (D49 supersedes it; inbound list); D47
`{per-quantifier K}` (false keyword, the rule a1 rejected); and, until R2-26
is fixed before 1.S, D47 `(+5 more)` with 6 unstarred lines, which C11
refuses before the critic sees it, so it measures the linter, not the critic
(the replacement is a reader-only plant, design §10).

**Plan examples** are unchanged from rev 1 (`now` lines under 160 chars for
OPT-REVEND and ANCH-AT; XARCH-TOKERR at level 1 via `entry --work -k token`),
except that 31 of today's 38 status lines exceed 160 chars, so unit 2's
provisional `now` carries the plan profile's `?` mark (§10 unit 2).

## E. C8's population, exemption set and the cite-to-id pass (F7; rev 3: R2-17, R2-20)

`<file>.md:<line>` cites at e9687de27 (READYU1-7, FIXIND-4), counted by
§2.4's C8 form (`<file>\.md:~?[0-9]+(-[0-9]+)?(, ?[0-9]+)*`, not under a
`pcrec-bench/` path): `decisions.md:N` 161 lines in 77 files;
`known_issues.md:N` 26-27; `plan_completed.md:N` 18; `plan.md:N` 0 (PL14);
`upstream_issues.md:N` 0.

**Unit 1's live population: 26 decisions cites in 11 files**:
docs/dev/spec_survey.md 15; docs/design/prior_cost_unify.md 2,
sel_cost.md 2, compare_stack.md, litscan_k82h.md, memfn/span_cards.md,
patfacts/design.md, variables_pattern.md, where_to_start.md;
docs/dev/known_issues.md 1 (a decisions cite inside the known file, rewritable
at unit 1 because known_issues.md is not split yet); docs/dev/chain_profile.md 1.
Plus forms the rev-2 pattern missed, all in spec_survey.md: two `decisions.md:~N` cites and one comma list
of four line numbers; and a relative `../dev/decisions.md:N` cite in
docs/design/engine_m4.md (written here with `N`, so this file is no C8 case). The
`known_issues.md:N` cites (rev 2's "~36" mixed them in) wait for unit 3,
including the one in a live docs/dev/plan.md row (a `known_issues.md:N` cite).

**The cite-to-id pass** (unit 1): a cite with an id NAMED in the same clause
becomes that id; the line number is history, usually stale: 16 of the 22
id-bearing live cites point into the PRECEDING entry, 6-30 lines off (e.g.
spec_survey.md's D46 cite, whose line falls inside D45). An
id-less cite (where_to_start.md, span_cards.md, chain_profile.md,
known_issues.md, sel_cost.md ×2) maps by CONTENT ANCHOR: the cited words or
keyword at that place are found in the census-commit text and the entry or
owner-table row holding them is the target, never the entry holding line N.
Every cite whose line map and named id disagree, and every id-less cite with
its anchor, is listed in the lane report for the manager.

Declared exemption set (a column of the profile table and the cite-form
table, one source for C8, C13 and their selftests):

| prefix | why |
|---|---|
| `docs/dev/dev_journal.md` | append-only |
| `docs/dev/plan_completed.md` | append-only archive; exempt for EVERY profile (it carries a `known_issues.md:N` cite) |
| `docs/dev/reviews/` | frozen review records (and their critic texts) |
| `docs/dev/lanes/` | frozen lane reports |
| `docs/dev/history/` | frozen archive |
| `studies/` | adopted exploratory work, never rewritten |
| `memfn/` except `memfn/docs/requests.md` | the kit's files; main does not edit them (requests.md is main's and live) |
| `docs/dev/doc_index/` | the owner tables carry `old_line` by design |
| PL14's existing list | as today |

A cite under `pcrec-bench/` is not pcrec's and never counts; the bench's
own readers get the manager's inbox note (H).

## F. The candidate-file census (F14, F17)

Sizes are bytes at main 6638e3679; "entries" counts the file's own heading
form; size spread is per entry.

| file | bytes | entries | entry heading | size median / p90 / max | parsed by |
|---|---|---|---|---|---|
| docs/dev/decisions.md | 832,382 | 191 ids, 198 `## D` headings | three forms: `## Dn — title (date, who)` (155), `## Dn — date — title` (33), bare (D27, D28; D98 wraps) | 2,834 / 9,279 / 36,010 (D29) | tests/memfn/rows_check.py (§1.2) |
| docs/dev/plan.md | 467,976 | 339 rows (296 not-started, 36 started, 2 blocked, 5 deferred); 31 child rows with 4-space attributes | `- [TAG] STATE:s — title` + attribute lines (`filed:`, `refs:`, `next:`, `trigger:`, `status (date):`) | 1,090 / 2,490 / 4,969 | scripts/plan_lint.py (PL01-PL17), pre-commit, pre-push-light |
| docs/design/plan_row_bodies/ | 21 bodies + CLAUDE.md, ~146 KB | 1 file per row | `TAG.md` | 1.0-28 KB | plan_lint PL15 |
| docs/dev/plan_completed.md | 1,212,690 | 397 head lines under 65 `## <date>` headings; 297 heads are prose; 6 tags also live in plan.md (stale snapshots); 4 tags twice | as plan.md, plus states completed, completed-in-place, delivered, ... | archive | plan_lint (PL06, PL07, PL15) |
| docs/dev/known_issues.md | 466,753 | 134 ids under 139 `## Kn` headings (K3, K4, K11, K12, K41 carry a second "original entry" heading); leading state: FIXED 68, OPEN 35-37, CLOSED 6, ACCEPTED 1, other 24-27 (INFRASTRUCTURE ×10, CHECK DESIGN ×2, RULED ACCEPTABLE, RE-SCOPED, none) | `## Kn — STATE ... — title` | 2,443 / 6,655 / 19,008 | none (cited from ~70 tests) |
| docs/dev/upstream_issues.md | 70,369 | 25 `## Un` + 1 id-less `##` heading; state in a body bullet `**Status**:` (suspected-bug 8, divergence-by-design 10, not-a-bug 2, fixed-upstream 1, prose variants) | `## Un — engine: title` | small | none |
| memfn/docs/requests.md | 92,851 | 38 `## R-n` (main's single-writer file) | `## R-n (date, who) — title` | — | post_compact.sh names it |
| memfn/docs/responses.md | 300,327 | 16 `## R-n`/`## N-n` + `###` notices (kit's file) | `## R-n — title` | — | rows_check.py LEDGERS |
| docs/dev/learnings.md | 41,996 | §1-§6, §3.a-§3.ac | `## n.` / `### 3.x` | — | none |
| docs/testing.md | 344,067 | ~50 topical sections | `## The ...` | — | none |
| docs/dev/dev_journal.md | 1,886,739 | 448 dated entries, append-only | `## date` | tail-read | known_fail, test_trailer (append) |
| docs/dev/full_suite_ledger.md | 50,678 | landing lines | prose lines | — | queuemon, fullsuite_job.sh |
| memfn/docs/ideas.md | 54,470 | 28 dated raw notes, append-only | `## date — note` | — | none |
| REFERENCES.md | 41,510 | 55 `### [Key]` | `### [Key] authors (year)` | small | none |

Files a session loads at start (design §1.3): root CLAUDE.md 17,876 B (auto, cap 20 KB); ~/.claude/CLAUDE.md 1,175; MEMORY.md 23,494 (manager and every lane); owner.md 5,430 (post_compact); wake.md 22,115 (5,000 injected); pcrec-manager SKILL.md 14,919; lanes add BOILERPLATE.md 10,872 (+ RUNS.md 15,564 on trigger). Today's always-on manager load is ~85 KB.

## G. Proposal to the kit (sendable as is; design §8)

*From the pcrec manager to the kit manager, for feedback; the kit decides
whether and how its own files adopt any of it.*

**What pcrec is doing.** pcrec is moving its long ruling and tracker files
(decisions.md 832 KB, plan.md 468 KB, known_issues.md 467 KB) to a PAIR: a
short INDEX with one line per entry (id, a short slug, a state, and ONE
sentence stating the current ruling or status, with a count of what the
sentence left out), and a DETAILS file holding each full entry verbatim under
a `## <ID> <slug> — title` heading, with any later addenda INSIDE their entry
as `### <ID>.aN`. Existing ids and addendum numbers never change. One
accessor, `scripts/entry ID`, prints an entry at a chosen level (0 the index
line, 1 plus its working fields, 2 the full entry), greps by item, and lists
open work; one profile table declares each file's ids, states, levels and
soft size caps. Full design: docs/design/doc_index_format.md.

**Why.** A session can hold an index (about 40-48 KB) in context and know
every current ruling in one line, and fetch exactly one full entry when it
needs specifics. Today an entry is found by grepping a heading and reading a
line range, which costs 3-36 KB per entry and misses addenda filed elsewhere
(about 40 in decisions.md sit outside their entry's heading).

**What it would look like in the ledgers (facts about the files, for the kit
to weigh).** requests.md has 38 `## R-n (date, who) — title` items, written
only by main; responses.md has 16 `## R-n`/`## N-n` items plus `###` notices,
written only by the kit; they are read in order, as a dialogue. A shape that
fits them: an index block at the top of each file, one line per item (`- R-38
<slug> <state> — the ask (or the answer) in one sentence`), with the bodies
left where they are, so the ledgers stay single-writer and in order. Main
would write the block in requests.md. A `kit` row in the profile table would
give the kit `scripts/entry R-38` and an open-items view from the same
accessor. rows_check.py's LEDGERS reader reads the bodies, so an index block
does not touch it.

**What we ask.** Feedback on the format itself (anything that would not fit
the kit's files or its wake read), and whether the kit wants the ledger index
blocks, a split, or neither. No change to either ledger happens without the
kit's answer.

## H. Who reads what, and how (design §1.2)

| reader | file | how |
|---|---|---|
| scripts/plan_lint.py (+ .sh, tests/plan_lint/, Makefile `test-plan-lint`) | plan.md, plan_completed.md, plan_row_bodies/ | full parse: PL01-PL17, caps (title 100, status/next 300, line 1000, row 12 lines / 6000 chars), PL14 no `plan.md:N` cites, PL17 floor 150 |
| structural name lists | the lint section | tests/ci/shards.tsv (exactly one row per TEST_SECTIONS member, check_shards.sh), tests/lib/san_excluded.txt ([TT-9]: every `tests/**/run_*.sh` listed once), Makefile `.PHONY` |
| scripts/hooks/pre-commit, pre-push-light; scripts/tests/hooks.test | plan files | pre-commit glob names the plan files only; pre-push-light runs the lint only `[ -f tests/plan_lint/run_plan_lint.sh ]` (silent skip if moved); hooks.test pins that literal; INSTALLED copies under .git/hooks are `install` copies, not links; installed ONCE into the COMMON git dir (`git rev-parse --git-path hooks`), so one copy serves every linked worktree, old trees included (R2-21) |
| tests/memfn/rows_check.py `support_faults` | decisions.md, responses.md | cuts `^## Dn\b.*?(?=^## D[0-9]\|\Z)`, requires the quoted ruling sentence inside |
| tests/memfn/stream_support.tsv | decisions.md | 2 rows `"sentence" @ docs/dev/decisions.md D190` |
| scripts/boxqueue header; plan_completed [BOXQUEUE]; docs/design/vlookbehind.md | plan_row_bodies/ | comment pointer; an archived row's refs; an in-force design that tells a build commit to CREATE `VMREC.md` there (§10 unit 2) |
| scripts/hooks/post_compact.sh | owner.md, wake.md | ROLE-SPLIT (scripts/session_role: main, kit, none): main injects owner.md + 5,000 chars of wake.md; nothing re-reads an index. Unit 1 adds the decisions re-read line to the MAIN branch only (R2-23) |
| .claude/skills pcrec-manager, q, pcrec-critic, pcrec-memfn-manager | plan.md, decisions.md, ledgers | STATE greps; write rulings; critic FREEZE diffs two named files; critic COMMONs read `git show <sha>:docs/dev/decisions.md` and `grep -n '^## Dn'`; deny by `grep -n '^- \[TAG\]'`; the freeze step records rulings as `file:line`; kit boundary list of main's files |
| LINE CITES `<file>.md:N` | decisions, known, plan_completed | ~161 / ~26 / 18 in ~100 files, most in frozen records; 26 live decisions cites in 11 files (E); three pcrec-bench files cite by basename, never counted (C8 anchor; inbox note) |
| CONTENT GREPS (manager memory, skills, briefs) | plan.md, decisions.md, known_issues.md | memory `pcrec-grep-plan-before-chartering` and `pcrec-done-line-verify-claims` grep for topic words; after a split they search the index only (`literal.run`: 1 of 7 plan hits). Outside the repo: a manager step per unit, never a lane edit |
| scripts/gestalt (ROWS table) and its readers: scripts/tests/gestalt.test, .claude/skills/pcrec-manager/monitoring.md (main and kit heartbeat prompts) | — | gestalt.test pins `--all` ≤ 12 lines and runs a real-tree "silent" case; monitoring.md lists the threshold kinds and says every printed line "gets acted on": T1 adds "docs over soft cap: record it, the owner's revisit trigger, no lane" (R2-8) |
| docs/dev/NOTES.md (decisions bullet) | decisions.md | a WRITE instruction ("add an entry whenever ..."): unit 1 names both files and the at-once rule (§2.7) |
| pcrec-bench: docs/dev/pcrec_references.md, docs/design/subbench_directory_model.md, docs/dev/research/2026-09-12-b42-rxt-as-source.md | decisions.md | `decisions.md:N` line cites and "grep the id if a line has moved"; no bench script parses pcrec's file. By D78 pcrec writes only `inbox_from_pcrec.md` there: unit 1's MANAGER STEP is one `[inbox]` note, never a lane edit (R2-23) |
| D27 cell briefs (scripts/mk_d27_cell.sh has no default allowlist) | decisions.md | a brief that allowlists decisions.md must add decisions_details.md: a manager/brief step named in unit 1 (R2-23) |
| root CLAUDE.md, docs/dev/CLAUDE.md, ~57 CLAUDE.md files | all | prose pointers ("decisions.md D26") |
| tests, src comments | all | cite ids only; no parse; src/gen/emit_dfa.c emits "docs/dev/known_issues.md K24" (an emitted byte: name-keeping saves an abi event) |

T2's `--stale`-at-wake mentions (READERS-1): scripts/NOTES.md,
docs/dev/NOTES.md, docs/dev/CLAUDE.md, scripts/CLAUDE.md, tests/CLAUDE.md and
plan.md's Policy. T2's shims: `scripts/plan_lint.sh` and
`tests/plan_lint/run_plan_lint.sh` exec the doc_lint equivalents (the
installed pre-push copy tests the old runner path) and keep their san list
row until deleted.

## I. Other files: verdicts (design §4)

| file | verdict | reason |
|---|---|---|
| known_issues.md | APPLY, unit 3 | same shape as decisions; 467 KB nobody can hold; symptom-in-one-line recall prevents re-filing |
| upstream_issues.md | APPLY (small, last), unit 4 on its trigger | 25 entries; nearly free once the tool exists |
| plan_completed.md | ARCHIVE TIER | stays the archive with its own `archive` profile (§10 unit 2); `entry` falls through to it only when plan.md lacks the tag |
| docs/design/plan_row_bodies/ | ABSORBED at unit 2 | live rows' 21 bodies become plan_details.md entries; completed rows' bodies per §10 unit 2; the directory and PL15 retire, C12 refuses new files |
| memfn/docs/requests.md, responses.md | PROPOSAL TO THE KIT (§8) | the kit adopts it or not |
| memfn/docs/ideas.md | DO NOT APPLY | append-only raw log |
| docs/dev/learnings.md | DO NOT APPLY (now) | 42 KB of doctrine cited by section number; already the summary tier |
| docs/testing.md | DO NOT APPLY | a handbook cited by section name |
| dev_journal.md, full_suite_ledger.md | DO NOT APPLY | append-only; scripts append and grep |
| REFERENCES.md | DO NOT APPLY | its own index |
| wake.md, owner.md, memfn wake | DO NOT APPLY | rewritten whole each session |
| MEMORY.md, CLAUDE.md/NOTES.md | SAME FAMILY, kept out | own owners and checkers (§2); §9 names the triggers that would fold them in |

## J. T1's gestalt row and its plants (R2-2, R2-3, R2-4, R2-5, R2-6, R2-7, R2-9)

**The row** (scripts/gestalt's ROWS table; the `docidx` PLACEHOLDER line is
deleted):

    docs         | [ -n "$docbad" ]                   | L_docs

`L_docs` = the `docs:` line of `timeout 2 python3 -I "${GESTALT_ENTRY:-$here/entry}" --over-cap`
(empty when nothing is over cap); `docbad` is set when that line is non-empty,
or the call exits non-zero, times out, or prints no `entry: over-cap` trailer,
in which case `L_docs="docs: unavailable"`. The `--all` loop prints a row's
line only when it is non-empty: the general rule that replaces the
`kind = idle-held` special case (L_idleheld is already empty when idle-held
does not fire), so `--all` on a normal box stays at 11 lines + DONE. The
header's kind list and "~12 lines" text name `docs`.

**`entry --over-cap` output:** at most one `docs:` line (several over-cap
indexes joined with `; `), then always the trailer `entry: over-cap checked
<n> pair index(es), <m> over`; exit 0. Format per index: `<file> <S> KB over
soft cap <C> KB (+<S-C> KB, <p>%)`, KB = bytes / 1024 TRUNCATED to one
decimal, p = floor(100 × bytes / cap bytes).

**Plants** (each red when built from rev 2's text, green after):

| id | where | plant | expected |
|---|---|---|---|
| J1 | gestalt.test | `--all` on a normal fixture with `GESTALT_ENTRY` = a stub printing only the trailer | ≤ 12 lines; no empty line |
| J2 | gestalt.test | the real-tree "silent" test runs with `GESTALT_ENTRY` = an under-cap stub; a second case with an over-cap stub | silent; then exactly the `docs:` line |
| J3 | gestalt.test | stub exits 3; stub sleeps 5 s; stub prints no trailer | `docs: unavailable` each, whole run < 5 s |
| J4 | entry --selftest | a FIXTURE `pair` profile, cap 48 KB: index of 52592 B; 52593 B; 52633 B; 49152 B | 106%; 107%; `51.3 KB` (not 51.4); no `docs:` line (at cap is not over) |
| J5 | entry --selftest | KEY `D26`, `K139`, `D47.a2`, `D26 addendum 2` against the real (dormant) profiles | exit 1, trailer `entry: profile decisions dormant (unit 1)` (known: unit 3) |
| J6 | entry --selftest | archive fixture with a tag on a HEAD_OK line and again on a non-STATE line (FIX-2's shape) | one row, exit 0 |
| J7 | make test-ci-shards / test-codegen / sections ran | the section with no shard row; with no san row; a recipe without the trailer touch | `0 shard rows`; TT-9 `UNLISTED`; `sections ran` names it missing |
| J8 | entry --selftest | `--rev` at a SHA before T1 (plan `single`), the working tree's table | the plan row at that commit |
| J9 | entry --selftest | `-g ID` over plan.md | the Policy section's `- [ID]` / `- [CHILD-ID]` templates are not items |
| J10 | tests/plan_lint | a planted row `[K50]` (and `[D26.a1]`, `[pcre2-compat-tiers]`) | PL18 refuses each |

Routing plants (one per routing row, on fixture profiles) are `entry
--selftest`'s own list (§2.3); J5 is the dormant behaviour on the real table.
