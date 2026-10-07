# 2026-10-07 ROWCON r1 — light D6 panel: [MEMFN-ROWCON] row_contracts.md rev 1

Subject: `docs/design/memfn/row_contracts.md` rev 1 (kit branch
`lane/memfn-rowcon`, 30a41a8a, worktree `worktrees/memfn`), with the two
audits it rests on (`audit_kit_rows.md`, `audit_pcrec_tables.md`). Four
read-only critics; nothing compiled or run. Texts are beside this file:
`critic_{soundness,reach,visibility,contract}.md`. Dispositions are the kit
manager's (`dispositions.md`), by theme T-A..T-J, and are binding.

## Panel

| critic | lens | model | verdict | B / M / m (stated) |
|---|---|---|---|---|
| soundness | is the logic sound? | opus | not sound as written; sound with its section F | 3 / 6 / 5 = 14 |
| reach | does reach/independence hold (K35, [MECH-REACH])? | (kit panel) | not ready as written; mechanism sound | 2 / 5 / 3 = 10 |
| visibility | can a human see why a row was chosen or declined? | (kit panel) | revise before passing; mechanism sound | 2 / 6 / 4 = 12 stated, 13 listed (see reconciliation) |
| contract | contract, boundary, docs, D77, D153 | (kit panel) | not ready as written; core (T0-T3, T5) sound | 1 / 6 / 6 = 13 |

**Verdict, all four: not ready as written; the core is sound.** The core is
the allowlist (`honours`) gate in place of the fail-open `applies()`
denylist, one table type, and a per-row reach floor. The rev-1 gate, applied
literally, would refuse every PRE and OFS site pcrec sends (a `make test`
compile break). Its Q-ROW-1 `miss` recommendation would refuse pcrec's live
PRE handoff sites. T3 cannot be zero-mover. Reach is defined at a grain that
would have passed K96 green. The decision record has no reader. None of this
touches the core; all of it is repairable inside the design's own frame
(soundness section F), as rev 2.

Models: soundness opus; reach, visibility and contract sonnet (kit manager,
from the spawn records).

## Themes (dispositions condensed from dispositions.md)

**T-A Binding time** (contract B1; sound B1, B1a, S8, #4; vis define/use
points). ACCEPT. `fields.def` gains a binding column: SITE, DEFINE_BOUND
(value-equal at define and use; FUNC `floor` is the S8 case), USE_ONLY
(subset check at use, refusal only), DEFINE_ONLY. Each phase runs its own
gate. The rev-1 "use mask == define mask" rule is withdrawn. Consequence
stated plainly: for use-only fields the gate cannot fall back to generic, it
can only refuse (sound B1a).

**T-B Contract rulings are contract changes** (contract M1; sound B2; S1;
#1-#3, #5-#7 as to defaults). ACCEPT. Defaults keep pcrec's live meaning: an
unstated `miss` is `n` for every valued handoff (PRE ASSIGN included), and
`floor` NULL is equivalent to "0". These land as integration.md rev 4.9, an
`MF_SITE_ABI` bump (kit-internal, no pcrec byte), a responses.md notice, and
G2 expectation updates by a BLINDED author after g2x. REFER Q-ROW-1.

**T-C Text shape** (S2-S7; sound B3; #8, #9). ACCEPT the contract route:
`s`/`n`/`lo` hook text must be a primary expression and `on_miss` one
statement (or braced); the kit REFUSES non-conforming text by a conservative
lexical check. Zero-mover. Parenthesizing or bracing in the kit (sound B3
option b) is REJECTED: a byte move with no measured need (D77). Part of
Q-ROW-1.

**T-D Listing is a declared mover** (contract M3; vis M5). ACCEPT. T2's
`--list-axes` rows are a declared dumps-stream mover, with a D80 spec hunk
and registry count re-pins (including the `memfn` section floor going from
UNREACHED to REACHED) under the same-commit rule. The arm denies move no
default byte. "Zero-mover" is restated as "zero ARTIFACT movers; one
declared listing mover".

**T-E Charter and generality** (contract M2; vis B1, M6). ACCEPT the gap and
REFER the charter: Q-ROW-4. A generic table engine widens D146's charter.
Recommendation yes, as a kit UTILITY under `MF_NS` with a charter line in
memfn/CLAUDE.md. For the migration mapping: `mf_select` takes a SCOPE (slot
id plus route-mask filter) so one array with a slot field fits (start_table
Q2); a ROUTE_SKIPPED verdict; the record carries scope and the caller's site
key as an opaque `const char *` (pcrec's macro keeps the literal check and
passes it).

**T-F Visibility channel** (vis B2; contract M4; reach M3; Q-ROW-2).
RESOLVED without a pcrec change. A compile-time kit-side trace (MF_TRACE, off
by default) prints each decision record to stderr during pcrec's own
compile; site_census.py's traced build turns it on. The record stays
kit-internal: no `mf_result`/`mf_call` ABI change, no `form_id` comparison.
`mf_explain` is the API G2 and K3 call. T6 is DROPPED, so Q-ROW-2 is
answered: no R-6. (Vis B2's own fix, T6 required, is not taken; the finding
is accepted.)

**T-G Reach grain and independence** (reach B1, B2, M2, M4, M5, m1; contract
M6; vis M7 deny-delta). ACCEPT. Reach cells are (row, honoured field,
declared value-class), classes declared in `fields.def`. Independent
controls: a name-level manifest of rows and witnesses (committed, not
derived); text signatures checked in the artifact; G2 byte-loop agreement;
start_table section 3.4's deny-delta control. Closed reason vocabulary for
rows unreachable from pcrec: total-fallback, pending-site+trigger,
contract-reach+G2-family; anything else is deleted. Count at successful
render. Counters are summed across the corpus by the census (trace route),
not kept in `mf_art`. Witness drift is detected because each witness asserts
its row by signature.

**T-H Gate model** (sound M1, M2, M3, M4, M5, M6; vis M1-M4, M6 no-row
semantics; reach m1 ignores-vs-honours). ACCEPT. Fields get a kind
(obligation, permission, requirement, rendering) and per-value bits for
enums. Hooks are NORMALIZED once before the gate and rows read only the
normalized form (this also settles #2, #3, #5-#7). Rows have `requires`
(positive, e.g. precheck's `miss_leaves`) as well as `honours`.
Shape-dependent honouring is a split row or an honours FUNCTION. The vacuous
generic-honours-ALL static assert is replaced by G2's per-field cells on
generic. The record keeps the FULL failing mask, a predicate-false reason
code, the deny source and a bounded nesting depth. No row applies: NULL, and
the CALLER's policy decides (the kit refuses; pcrec may keep crashing).

**T-I Scope trims** (contract M5; reach M1; Q-ROW-3). ACCEPT. T4
(sub-tables) is dropped until a measured need, i.e. a K96-class finding
inside a row's sub-choice (reach M1's manifest rule applies if it is ever
revived). pcrec adoption stays an OFFER after START-TABLE C7, not planned
work. Q-ROW-3 answered "not now" (unanimous).

**T-J D153 overlap** (contract D153 section; contract m6). NOTED. T0-T5
touch no pcrec file except T2's `axes_dump` listing hunk (an M1b-touched
file, now merged; no in-flight lane edits it), re-checked at T2's cut.

Anything not covered by a theme: ACCEPT-AS-MINOR, folded into rev 2's text.

## By-id completeness table

Legend: disposition ACCEPT, ACCEPT-AS-MINOR, REJECT, REFER Q-ROW-n. Severity
B = BLOCKER, M = MAJOR, m = MINOR; S = suspect cell (audit 2.5); D = one of
the 13 disagreements (audit 3, soundness's by-id table). Where a finding's
own suggested fix differs from the ruling, the disposition column says so.

### Soundness (14 findings + 8 S rows + 13 D rows)

| critic | id | sev | summary | theme | disposition |
|---|---|---|---|---|---|
| sound | B1 | B | define/use equal-mask rule refuses every PRE (94) and OFS (40) site; needs binding time | T-A | ACCEPT |
| sound | B1a | (part of B1) | for use-only fields the gate can only refuse, not fall to generic | T-A | ACCEPT (counted inside B1) |
| sound | B2 | B | Q-ROW-1 `miss` recommendation refuses PRE ASSIGN handoffs; unstated miss = `n` for all valued handoffs, default_test cross-field | T-B | ACCEPT; REFER Q-ROW-1 |
| sound | B3 | B | T3 not zero-mover for S2-S7; "drop from honours" breaks compile; settle by contract ruling | T-C | ACCEPT option (a); option (b) REJECT; REFER Q-ROW-1 |
| sound | M1 | M | non-default is four kinds (obligation/permission/requirement/rendering); per-value enum bits; preds/term aggregation | T-H | ACCEPT |
| sound | M2 | M | rows read raw hooks; canonicalize before gate, grep check that raw reads are gone | T-H | ACCEPT |
| sound | M3 | M | T2 zero-mover depends on an unspecified honours mapping; pcrec states many non-default fields; list obligation set per row | T-H | ACCEPT |
| sound | M4 | M | `mf_row` lacks precheck's positive `miss_leaves` requirement; wrong answer if dropped; add C5 decline fixture | T-H | ACCEPT |
| sound | M5 | M | honouring is per shape (PRE bytes vs run parts on `floor`); honours function or split row | T-H | ACCEPT |
| sound | M6 | M | "generic honours ALL" static assert shares source with what it controls; list refuse_test rows, G2 per-field cells | T-H | ACCEPT |
| sound | m1 | m | arms pairwise disjoint; order matters only inside RROWS; sub-tables pass own field table or 0 | (own) | ACCEPT-AS-MINOR |
| sound | m2 | m | `denies` and `opts` are selection inputs, keep out of `fields.def` | (own) | ACCEPT-AS-MINOR |
| sound | m3 | m | `policy` PORTABLE_ONLY is the inverted case, works by luck; obligation only for SIMD rows | T-H | ACCEPT-AS-MINOR |
| sound | m4 | m | several of the "13 disagreements" are not disagreements about a default; overclaim | (own) | ACCEPT-AS-MINOR |
| sound | m5 | m | "8 more K96-class" mixes ignoring (S1, S8) with mis-rendering (S2-S7); count 2 + 6 | (own) | ACCEPT-AS-MINOR |
| sound | S1 | S | PRE x `miss`: selection cannot see it; Q-ROW-1 as written refuses NULL miss on ASSIGN | T-B | ACCEPT; REFER Q-ROW-1 |
| sound | S2 | S | PRE x `s` parenthesization | T-C | ACCEPT (contract route) |
| sound | S3 | S | PRE x `n` parenthesization | T-C | ACCEPT (contract route) |
| sound | S4 | S | PRE x `lo` parenthesization | T-C | ACCEPT (contract route) |
| sound | S5 | S | PRE x `on_miss` braces (one statement) | T-C | ACCEPT (contract route) |
| sound | S6 | S | RUNA x `s` parenthesization (101 VM compares) | T-C | ACCEPT (contract route) |
| sound | S7 | S | RUNA x `lo` parenthesization | T-C | ACCEPT (contract route) |
| sound | S8 | S | GEN x `floor` define/use; equality refuses legit sites; DEFINE_BOUND value-equality | T-A | ACCEPT |
| sound | D1 | D | `miss` NULL: recommended refusal breaks PRE ASSIGN | T-B | ACCEPT; REFER Q-ROW-1 |
| sound | D2 | D | `miss` != `n`: enforced at use only, ofsskip `miss_is_n` must go | T-B/T-H | ACCEPT; REFER Q-ROW-1 |
| sound | D3 | D | `floor` "0" vs NULL: raw reads still decline; canonicalize | T-B/T-H | ACCEPT; REFER Q-ROW-1 |
| sound | D4 | D | `floor` define vs use | T-A | ACCEPT |
| sound | D5 | D | `n` NULL is a requirement, not a default | T-H | ACCEPT |
| sound | D6 | D | `indent` NULL: requirement, or canonicalize NULL to "" | T-H | ACCEPT |
| sound | D7 | D | `on_miss` NULL on ASSIGN: requirement | T-H | ACCEPT |
| sound | D8 | D | hook precedence (S2-S4, S6, S7) | T-C | ACCEPT (contract route); REFER Q-ROW-1 |
| sound | D9 | D | `on_miss` statement shape (S5) | T-C | ACCEPT (contract route); REFER Q-ROW-1 |
| sound | D10 | D | member vs immediate/table probe: rendering choice, not a defect | (own) | ACCEPT-AS-MINOR (declare non-disagreement) |
| sound | D11 | D | `note` called or not: rendering, not a defect | T-H | ACCEPT-AS-MINOR (kind RENDERING) |
| sound | D12 | D | `lo` > `n`: agree, nothing to settle | (own) | ACCEPT-AS-MINOR (no action) |
| sound | D13 | D | OPTIONAL `need`: agree; kind PERMISSION | T-H | ACCEPT-AS-MINOR (no action) |

### Reach (10 findings)

| critic | id | sev | summary | theme | disposition |
|---|---|---|---|---|---|
| reach | B1 | B | per-row CHOSEN grain would pass K96/S2-S8 green; reach must be (row, field, value-class) cells | T-G | ACCEPT |
| reach | B2 | B | every named control shares a source with the kit; need manifest, text-signature oracle, byte-loop agreement | T-G | ACCEPT |
| reach | M1 | M | sub-table rows are in the mechanism but not in the reach story | T-I | ACCEPT (T4 dropped; manifest rule kept if revived) |
| reach | M2 | M | witness drift to another row ([MECH-REACH]) not designed; signature, executed-witness count, hard-fail on empty/skipped | T-G | ACCEPT |
| reach | M3 | M | Q-ROW-2: T6 not needed; text signature plus existing traced census build | T-F | ACCEPT (T6 dropped) |
| reach | M4 | M | "unreachable from pcrec" needs a closed reason vocabulary with triggers | T-G | ACCEPT |
| reach | M5 | M | counters in `mf_art` mix populations; count at successful render, not selection | T-G | ACCEPT |
| reach | m1 | m | K35 populations still uncounted (6 sub-items: cell sites, refuse_test witnesses, DENIED drivers, mismatch refusals, ignores vs honours, default probes) | T-G (sub-items to T-H, T-B) | ACCEPT-AS-MINOR, folded into rev 2 |
| reach | m2 | m | density/hint-sensitive row choices unwitnessed | (own) | ACCEPT-AS-MINOR |
| reach | m3 | m | shadowed rows: add "first applicable" witness definition | T-G | ACCEPT-AS-MINOR |

### Visibility (13 listed; 12 stated)

| critic | id | sev | summary | theme | disposition |
|---|---|---|---|---|---|
| vis | B1 | B | record does not map onto C1 trace / CandRow (slot, route, site, route-skip verdict, formatted names) | T-E | ACCEPT; REFER Q-ROW-4 |
| vis | B2 | B | no reader or surface for the record; V not delivered | T-F | ACCEPT finding; its fix (T6 required) REJECTED in favour of MF_TRACE |
| vis | M1 | M | "first failing field only" discards the full mask | T-H | ACCEPT |
| vis | M2 | M | PRED_FALSE has no reason code | T-H | ACCEPT |
| vis | M3 | M | DENIED does not say by which switch | T-H | ACCEPT |
| vis | M4 | M | fixed-size record and nested decisions unspecified | T-H | ACCEPT (bounded depth); sub-table linkage moot while T4 is dropped |
| vis | M5 | M | listing is not "listing change only": moves registry/dumps stream; deny use moves bytes | T-D | ACCEPT |
| vis | M6 | M | generality blockers for pcrec adoption (routes, no-row semantics, typed applies, derived deny, MF_NS, rec==NULL fast path) | T-E (no-row: T-H) | ACCEPT; REFER Q-ROW-4 |
| vis | M7 | M | CHOSEN-only counters; add EVALUATED; adopt deny-delta control; two homes for counters | T-G | ACCEPT |
| vis | m1 | m | show rows after the winner as NOT_EVALUATED | T-H | ACCEPT-AS-MINOR |
| vis | m2 | m | `mf_explain` text is diagnostic; checks read the structured record | T-F | ACCEPT-AS-MINOR |
| vis | m3 | m | T6 must extend C1's 25 site keys | T-F | ACCEPT-AS-MINOR (moot: T6 dropped; note kept for any later pcrec hook) |
| vis | m4 | m | record would turn "pcrec never reaches generic" from inference to measurement | T-G | ACCEPT-AS-MINOR |

### Contract (13 findings)

| critic | id | sev | summary | theme | disposition |
|---|---|---|---|---|---|
| contract | B1 | B | define/use equal-mask rule refuses legitimate FUNC sites; needs phase column | T-A | ACCEPT |
| contract | M1 | M | Q-ROW-1 is a contract change (memfn.h, integration.md, G2, ABI bump, responses notice), not a table edit | T-B | ACCEPT; REFER Q-ROW-1 |
| contract | M2 | M | kit-exported generic `mf_select` is outside the written charter | T-E | ACCEPT gap; REFER Q-ROW-4 |
| contract | M3 | M | "zero-mover throughout" is false for the listing stream; floor born; deny moves bytes | T-D | ACCEPT |
| contract | M4 | M | record via `res` is an ABI change; T6 vs `form_id` opacity (C4 class 7) | T-F | ACCEPT |
| contract | M5 | M | D77: T4 and pcrec adoption have no measured need | T-I | ACCEPT |
| contract | M6 | M | hit counters in per-attempt `mf_art`; accumulation point unspecified | T-G | ACCEPT |
| contract | m1 | m | `mf_select` signature inconsistent between 1.3 and 1.5; `applies` loses type safety | T-E | ACCEPT-AS-MINOR |
| contract | m2 | m | table.c needs PROVENANCE/SPDX; `fields.def` under C16; MF_NS and c15 allowlist; generic name collision | T-E | ACCEPT-AS-MINOR |
| contract | m3 | m | static assert shares source with `honours`; say it is structural only | T-H | ACCEPT-AS-MINOR |
| contract | m4 | m | T3 soundness depends on the G2 hook-style axis; order it before T3 | T-C/T-G | ACCEPT-AS-MINOR |
| contract | m5 | m | state order: vocabulary gate, `refuse_test`, selection; where loud-error text names the arm | T-H | ACCEPT-AS-MINOR |
| contract | m6 | m | kit lanes (m1b*, r4c2*) edit compose.c/runcmp.c/precheck.c concurrently: rebase tax | T-J | ACCEPT-AS-MINOR (NOTED) |

Contract's D153 section and "docs made stale" table have no ids; the D153
note is T-J and the stale-docs list is folded into the rev-2 change list
below.

### Reconciliation

| critic | stated | rows in table (excluding S/D rows, B1a) | match |
|---|---|---|---|
| soundness | 3 B + 6 M + 5 m = 14 | B 3 (B1, B2, B3), M 6, m 5 = 14 | yes (B1a is a corollary inside B1) |
| reach | 2 B + 5 M + 3 m = 10 | 2 + 5 + 3 = 10 | yes (m1 has 6 sub-items, one id) |
| visibility | 2 B + 6 M + 4 m = 12 | 2 + 7 + 4 = 13 | NO: critic lists M1-M7 (seven MAJORs) but states 6 |
| contract | 1 B + 6 M + 6 m = 13 | 1 + 6 + 6 = 13 | yes |

Headline findings: 14 + 10 + 13 + 13 = **50** (51 rows if B1a is counted
separately). Add soundness's by-id tables, S1-S8 (8) and D1-D13 (13), for
**71** table rows (72 with B1a). The panel totals reconcile for three of four
critics. The visibility critic's stated count (6 MAJOR, 12 total) is one low
against its own text (7 MAJOR, 13 total); every id it lists is in the table,
so no finding is lost. The critic's stated count should be treated as a
miscount, not a withdrawn finding.

## Questions for Frank

Q-ROW-1 and Q-ROW-4 are open. They go to Frank in plain text with a
recommendation (no question UI).

**Q-ROW-1 — contract rulings (themes T-B, T-C).** Do you accept the
following as kit contract changes, landing as integration.md rev 4.9, an
`MF_SITE_ABI` bump (kit-internal; no pcrec byte moves), a responses.md
notice to the pcrec manager, and G2 expectation updates by a blinded author
after g2x?
1. An unstated `miss` is `n` for every valued handoff (RETURN, ASSIGN,
   ON_CAND, the FUNC call), including pcrec's PRE ASSIGN sites. Generic
   renders it as `(n)`. Text-equal-to-`n` counts as default.
2. `floor` NULL is equivalent to "0" (already memfn.h's text).
3. The T-C text-shape rule: `s`, `n`, `lo` hook text must be a primary
   expression (identifier, parenthesized, or postfix) and `on_miss` must be
   one statement (or braced). The kit refuses non-conforming text with a
   conservative lexical check. G2's unparenthesized-ternary and
   two-statement `on_miss` styles become out-of-contract inputs that G2
   asserts are REFUSED.
4. The remaining per-field defaults (`indent` NULL, `n` NULL, `on_miss` NULL
   on ASSIGN) are settled as requirements or normalizations per T-H, each
   naming which side (contract or row) is edited, preferring "tighten the
   row" where the contract is silent.

Recommendation: YES to all. They keep pcrec's live meaning, move zero
artifact bytes, and are the only route that makes S2-S7 settled without a
byte move. The alternative (kit parenthesizes and braces) is a byte move
with no measured need and is rejected under D77.

**Q-ROW-4 — charter.** May the kit export a generic decision-table engine
(`mf_row`/`mf_table`/`mf_select`/`mf_decision`/`mf_explain`) as a kit
utility under `MF_NS`, with a charter line added to memfn/CLAUDE.md, widening
D146's "returns the C text for a search site"? Recommendation: YES, because
decisions move into the kit (Frank's ruling recorded in the plan row) and the
kit cannot link pcrec. Mapping: `mf_select` takes a scope (slot id plus
route-mask filter), a ROUTE_SKIPPED verdict, and the record carries scope and
the caller's site key as an opaque `const char *`; pcrec keeps its literal
macro. The contract critic's alternative, keep T0-T5 `static` and export
only the record accessor until a pcrec table adopts it, is the fallback if
you decline. pcrec adoption itself stays an offer after START-TABLE C7
(Q-ROW-3).

**Q-ROW-2 — ANSWERED (T-F).** Is a pcrec-side hook (T6, an R-6 request)
needed to deliver the decision record? No. A kit-side compile-time trace
(MF_TRACE, off by default) printing the record to stderr during pcrec's own
compile, picked up by site_census.py's traced build, plus artifact text
signatures, gives the census its channel. T6 is dropped; no R-6; no
`mf_result`/`mf_call` ABI change.

**Q-ROW-3 — ANSWERED (T-I).** Should pcrec adopt the table mechanism now?
Not now (unanimous). Adoption stays an offer after START-TABLE C7.

## Rev-2 change list (row_contracts.md)

Section names are rev 1's; where a section is new it is marked.

- **Header / section 0 (headline):** restate "zero-mover" as "zero ARTIFACT
  movers; one declared listing mover" (T-D). Split the "8 more K96-class
  cells" count into 2 ignored fields (S1, S8) and 6 mis-rendered (S2-S7);
  state the gate addresses the first class and the contract text-shape rule
  the second (sound m5). Retract "settles the 13 disagreements": mark D10 and
  D11 non-defects, D12 and D13 agreements (sound m4).
- **Section 1.1 (fields.def):** add a `binding` column (SITE, DEFINE_BOUND,
  USE_ONLY, DEFINE_ONLY) and a `kind` column (obligation, permission,
  requirement, rendering) with per-value bits for enums (`empty`, `use`,
  `policy`); aggregation rule for `preds[]`/`term[]`; value-class list per
  field for reach cells (T-A, T-G, T-H). `default_test` takes `(site, hooks)`
  and may read siblings. Remove `denies` and `opts` from the field set (sound
  m2). Move shape enums (`form`, `op`, `handoff`) to `applies()`. Add the
  Q-ROW-1 defaults, with a positive and a negative probe per ruling.
- **Section 1.2 (the gate):** withdraw "use mask == define mask"; per-phase
  gates (SITE and DEFINE_BOUND at define, USE_ONLY at use, DEFINE_BOUND
  value-equal across phases; FUNC `floor` is S8). State that use-only
  failures refuse and cannot fall back to generic (sound B1a). Add
  `requires` alongside `honours`; add normalization (floor "0" to NULL;
  unstated or `n`-text `miss` to canonical `n`; `indent` NULL to "") before
  any row sees the hooks, plus a grep check that no row reads raw values
  (sound M2). Add the text-shape refusal (lexical check) for `s`/`n`/`lo`/
  `on_miss`. State the order: vocabulary gate, `refuse_test`, selection
  (contract m5). Replace the "generic honours ALL" static assert with G2
  per-field cells; keep the assert only as a labelled tripwire.
- **Section 1.3 (decision record):** full failing mask per GATED row;
  predicate reason code with an adapter for 0/1 predicates; DENIED carries
  its source (MF_D bit or options.def row); NOT_EVALUATED for rows after the
  winner; ROUTE_SKIPPED verdict; scope and opaque caller site key; bounded
  nesting depth and overflow flag; `rec == NULL` fast path; no-row result is
  NULL with the caller's policy. Add the corrected field-mapping table
  against `PCREC_CAND_TRACE_REC`/`CandRow` (vis B1) and say `mf_explain` is
  not the CANDTRACE format and checks read the structured record only. Name
  the surfaces: `mf_explain` for G2/C5/K3 and the MF_TRACE stderr trace for
  the census (T-F).
- **Section 1.4 (reach):** replace per-row CHOSEN with cell grain
  (row, honoured field, value-class); EVALUATED count alongside CHOSEN;
  count at successful render, not at selection or on a DENIED verdict; counters
  summed by the census, not kept in `mf_art`; independent controls (name-level
  manifest of rows and witnesses, text signatures, G2 byte-loop agreement,
  deny-delta); closed unreachable-reason vocabulary with a pinned count per
  reason; refuse_test and deny drivers get witnesses; `ignores` distinct from
  `honours`; shadowed-row witness definition; executed-witness count with
  hard-fail on empty or skipped witnesses; pcrec-side invariant paired with
  each corpus witness (T-G).
- **Section 1.5 (mf_row / mf_select):** one `mf_select` signature (contract
  m1) taking scope and carrying site and both hook sets; `requires` slot for
  precheck's `miss_leaves` (fold the composer's `arm.miss_leaves` column into
  `precheck_applies`, add C5 fixture `pre-decline-leaves`); honours may be a
  function or the row is split (sound M5); sub-tables pass their own field
  table or 0; typed-applies discipline (macro or documented casts); a
  caller-side `denied()` hook for derived denies; MF_NS names, PROVENANCE and
  SPDX rows, c15 allowlist (contract m2); keep `mf_run_row` as a read-only
  projection so `axes_dump.c` does not change beyond the T2 listing hunk.
  T4 text (sub-tables) marked HELD with the trigger "a K96-class finding
  inside a row's sub-choice" (T-I).
- **Section 2 (generality / migration):** record the Q-ROW-4 charter question
  and its recommendation; the slot/route/site mapping (T-E); pcrec adoption
  marked an offer after START-TABLE C7; Q-ROW-3 answered "not now".
- **Section 3 (soundness argument):** rewrite per kind and per binding time;
  3.3 "rows cannot disagree on unstated" is by canonicalization, not by
  `fields.def` alone; 3.5 states the gate does not see mis-rendering (S2-S7),
  handled by the text-shape rule plus G2's hook-style axis; 3.6 order
  rationale required only where two rows' predicates can both hold (RROWS,
  later any SIMD row over its scalar twin).
- **Section 4 (plan, T0-T6):**
  - T0: add the T0c contract-text deliverables (memfn.h hook comments,
    integration.md rev 4.9 section, `MF_SITE_ABI` bump, responses.md notice,
    G2 expectation updates by a blinded author after g2x), and the Q-ROW-1
    per-field table naming which side is edited.
  - T2: the gate becomes "streams 1-4 and 6 byte-identical; stream 5
    (`--list-axes`) moves by exactly the declared rows"; deliverables list
    the spec hunk (registry.md section 6, table_contract.md, cli.md), the
    `memfn` floor literal born in the same commit, and pinned PASS counts;
    state that deny use falls to generic and so moves bytes under the deny
    (needs the C5 pin and `--memfn=` documentation).
  - T3: settle S2-S7 by the contract text-shape rule; order the G2 hook-style
    axis (T5) before T3 (contract m4).
  - T4: HELD, trigger named (T-I).
  - T5: reach floors at cell grain with the manifest; census via the MF_TRACE
    traced build.
  - T6: DROPPED (T-F). Add a sequencing note against the active m1b* and
    r4c2* lanes on compose.c/runcmp.c/precheck.c (T-J).
- **Section 5 (questions):** Q-ROW-1 reworded to the T-B and T-C rulings with
  its recommendation; Q-ROW-2 and Q-ROW-3 recorded as answered; Q-ROW-4
  (charter) added.
- **Docs made stale by ROWCON (contract's table), to update at the cut of
  the step that makes each stale:** memfn/CLAUDE.md (layout, option
  namespace, boundary, status), memfn/src/CLAUDE.md (first-match arm table
  paragraphs and `arm` description), memfn/tests/CLAUDE.md (G2 per-row
  floor, refusal table), tests/memfn/CLAUDE.md (`ARMS_ROW_FLOOR`,
  `ARMS_EXPECTED`, census witnesses), memfn/PROVENANCE.md, memfn.h
  (`MF_SITE_ABI`, hook comments), integration.md (sections 14.0-14.2, 15.1,
  17, 10.2, 22, new rev 4.9), docs/spec/registry.md section 6 and the
  `memfn` floor, table_contract.md, cli.md `--list-axes`, plan.md
  [MEMFN-ROWCON] row and its trigger rows, decisions.md (new D-id for the
  mechanism and Q-ROW-1 rulings), `tests/registry/axes_registry_check.sh`
  (`[memfn floor]` becomes REACHED), emit_sweep.py docstring (stream 5 has
  declared movers).
