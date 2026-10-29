# landwalk critic — lens SLOTS (slot tracing + ruling check)

Subject: docs/dev/lanes/p1dsg_report.md @ 3afd1a439. Code read at main HEAD 13056c942
(src/gen/emit_dfa.c `cand_rows[]` lines 10160-10650, src/core/compile.c 378-560 and
3080-3130, src/gen/known.c `cover_conj[]`, src/core/internal.h 8985-9060).
Read-only; no compiles needed for this lens.

## Findings

### SLOT-1 — the reach guard's hand (LOWER) is not a take cell of FIN4 on CAND_ROUTE_DFA
CONFIRMED (table read). Severity: design (answer risk if built as written). Effort: small.
Blast radius: the DFA hat's guard path, every stage-1 admitted row whose guard trips.
Subject §Mechanism "DFA hat (stage 1)": "hand `s*(j)` as LOWER to FIN4 `search-from` on
`composite`". In the table, `search-from`'s take on CAND_ROUTE_DFA is
`{ CAND_HAND_AT, CAND_HAND_ENDSET }` (emit_dfa.c ~10620); LOWER is a take cell ONLY on
CAND_ROUTE_VM. The walk "keeps such a row on a route only where the ask's hand is one of its
take cells" (CandRow.take comment, ~5690), so asked with LOWER on the DFA route FIN4 does not
apply and the FINISH walk falls to `nomatch`/`report` — neither takes LOWER either, so the
ask has NO row. The design must add the cell (`[CAND_ROUTE_DFA] = {AT, ENDSET, LOWER}`) and say
what E-FL-for-LOWER means on the DFA route (today ENDSET's RELOCATE is the only relocate there),
or hand the guard's start as ENDSET-shaped RELOCATE. Neither is named. Not in the Build plan's
step 4 ("the reach guard -> FIN4") either.

### SLOT-2 — `RX_VM_START_SCAN` is NEXT's stamp, not LOCATE's; the stage-2 stamp line conflates slots
CONFIRMED (code read). Severity: doc/design (spec hunk would be wrong). Effort: trivial.
Subject §Mechanism "three standing questions" item 3: "the stamps `RX_DFA_SCAN
"landmark-walk"` and `RX_VM_START_SCAN`". `cand_list_stamp` (emit_dfa.c ~12157) maps
CAND_SLOT_LOCATE -> `RX_DFA_SCAN` on EVERY route and CAND_SLOT_NEXT on CAND_ROUTE_VM ->
`RX_VM_START_SCAN` (value = `vm_start_row(...)->tok`, ~8171). A LOCATE row's name can never
appear in `RX_VM_START_SCAN`. What the design presumably means is that on a VM artifact where
`landmark-walk` is selected, NEXT's `first-class` goes off the path, so `RX_VM_START_SCAN`
should read the path-absent token (`cand_stamp_absent`), and `RX_DFA_SCAN` reads
"landmark-walk" on a VM artifact (a DFA-family stamp on a VM route; today composite's VM hat
has no `.scan` token at all, `.scan` is filled for DFA/ATTEMPT only). The match_api.md §6.3
hunk must say both, per slot. Also omitted: `RX_DFA_MATCH` (FINISH's stamp) and the
member-fold stamps (SLOT-4).

### SLOT-3 — `.needs[CR_DFA]` restates the path closure (F + composite's slots, and A) instead of declaring the row's own use
CONFIRMED (code read). Severity: maintenance/design (a private copy of §2.7's closure).
Effort: trivial (delete from the proposal). Blast radius: the path members, every
member-fold stamp, the size-cap ladder's strict-subset test.
Subject §Mechanism "`.needs`": `[CR_DFA] = {W, A, F + the composite's slots (the fallback),
PRESENCE}`. The closure already derives both: `cand_path_finish` (emit_dfa.c ~11905) adds the
FALLBACK LOCATE row's `needs[reloc].mach` and visits its cells whenever FIN4 `search-from` is
asked with a non-AT hand (the guard's relocate), and FIN3 `verify-at` declares `CAND_MA` itself
(~10606). The sibling `rev-end`, whose ENDSET also relocates to `composite`, declares only
`{ CAND_MR, RECOVER, PRESENCE }` (~10197) and gets F through the closure. Declaring F and A
on the LOCATE row puts them on the path even where the walk never relocates or verifies
(and makes ¶2a's "strict subset" test of limits §8.4 read a machine set the closure would
not have produced). Declare `{ W, 0, PRESENCE }` (+ whatever the walk itself runs) and let
the closure add the rest.

### SLOT-4 — no admission row for "the anchored machine A was built": the walk's AT hand then cycles through FIN4 back into `landmark-walk`
CONFIRMED (table trace; design-level, nothing is built). Severity: answer/hang if built as
written. Effort: one admission row. Blast radius: every admitted pattern whose anchored
machine overflows `PCREC_ANCHORED_MAX_STATES` or is denied (`-fno-anchored-dfa`), and the
ladder's rung 3.
The walk hands `s*(j)` as AT to FINISH. `verify-at` applies only where `anchored_ok`
(`finish_available`, ~9423); otherwise FINISH falls to `search-from`, whose DFA-route AT
meaning is "the search entry's own LOCATE ask from the caller's position, filtered to a match
starting there" (E-FC; FINISH comment ~10585; in `cand_path_finish` an AT hand is NOT
relocated to the fallback, it follows `search-from.needs = {0, CN(LOCATE)}` on the SAME route,
i.e. the selected LOCATE row). The selected LOCATE row is `landmark-walk` itself, which walks
the same hit back to the same `s*(j)` and hands AT again. `landmark-walk` is the first LOCATE
row that hands AT at all (`rev-end`/`cover` hand SPAN/NOMATCH/ENDSET), so no existing row has
met this. The sibling `cover` has exactly this conjunct (`cover_conj[]` C4 `anchored-A`,
known.c:373). The admission table (§Admission) has no such row; the design instead adds a
ladder rung "before rung 3 because dropping A under a selected landmark-walk would leave
needs ⊄ built". With an `A built` conjunct the predicate declines when A is dropped, the
artifact falls to `composite`, and ¶2a's existing strict-subset rule already does the right
thing: the new rung's stated reason disappears (see SLOT-12).

### SLOT-5 — the admission table omits declines the design states elsewhere, so `--list`'s "deciding row" would be wrong for them
CONFIRMED (subject vs subject). Severity: doc/design (the listing promise). Effort: small.
Blast radius: the [LIST-TABLES] declined reason the design promises per compile.
§Admission says "only `excl-cand` and `excl-lower` select" and "`--list` can print the deciding
row per compile". Declines stated elsewhere in the subject have NO row:
- W overflowed (§Mechanism "Overflow is a DECLINE");
- A not built (SLOT-4);
- the route/stage: `excl-lower` is "VM hat only, stage 2", and `CR_VM` is stage 2; on stage 1 a
  VM artifact reaching row 6/7 must decline by some row;
- utf8 with a non-ASCII `L[0]` (unsound-case table, last line: "stage 1 admits utf8 only where
  `L[0]` is ASCII");
- `\G` (locate_finish E8: a relocate producer that cannot keep `lo` and `search_from` apart
  declines `\G`; the design lists `\G` only as a TEST, Build plan 8);
- the deny flag (`revend_forms[]` puts its deny as row F0 `denied` "so the listing names the
  row", emit_dfa.c ~13512).
Each would today print `fallback` or a wrong earlier row.

### SLOT-6 — the admission table IS a second selection table inside one row's predicate, and its row 3 restates another slot's rows in different words
CONFIRMED (code read). Severity: design (answer-neutral; a population falls between two
mechanisms). Effort: small (re-spell row 3 as a read; make the table data).
(a) It selects more than yes/no: rows 6/7 choose the HAND (CAND→FIN3 vs LOWER→FIN4) and the
stage, i.e. a FORM choice exactly like `revend_forms[]` (rev-end's sub-axis); row 3 redirects
to another slot's rows. Built as "the conjuncts of `locate_landmark_walk_applies`" (§Admission)
it is code-only: plan [LIST-TABLES] says "NEW tables are designed listable (rows as data
carrying a name + predicate description, not code-only)", and D163 add. 4 (b) asks "each row's
admission as listed conjuncts the listing can show (not opaque predicates)" — which is how
`split_conj[]` (compound.c:248) and `cover_conj[]` (known.c:373) are built.
(b) Row 3 `fixed`: "`P` has one fixed width `k` → decline to the EXACT-k NEXT rows". Those
rows' predicates are NOT "P fixed width": `pf_ofs_applies_common` (emit_dfa.c ~7300) is
"forward scan ∧ an offset-0 prefilter approved ∧ the kit's reply chose RESEED
(`next_key_holds(NK_OFFSET_SET)`)", and run-pinned adds a pinned necessary run. The house rule
(src/gen/NOTES.md: "a slot's predicate asks another slot's row, never restates it"; `CAND_READ`)
says row 3 should be `CAND_READ(LOCATE, NEXT) ∈ {run-pinned*, offset-set*}`. As written, a
fixed-width-P pattern the kit did not give an offset set to (or under `-fno-offset-skip`)
declines BOTH mechanisms and lands on plain `composite` (105 corpus / 14 bench sit in row 3;
the split between "offset row took it" and "nothing took it" is unmeasured).

Repro (slots/probe_row3.sh, 3 compiles, HEAD build): `[a-z]{3}@[a-z]+` takes `offset-set`;
the same with `-fno-offset-skip` takes `handoff`; `x[0-9]{4}=[a-z]+` (P = `x[0-9]{4}`, fixed
width 5, L = `=`) takes `memchr`. In the last two a fixed-width P is declined by row 3 although
no EXACT-k row runs — under the design they get neither the walk nor an offset row, and a deny
of one optimization (`-fno-offset-skip`) silently denies another.

### SLOT-7 — on the VM route the walk is a NEXT/FIRST row, not LOCATE; placing it in LOCATE is what makes stage 2 wait on L3
SUSPECTED (design argument; argues locate_finish.md F-5, not a D-row). Severity: design
(schedule + one fewer mechanism). Effort: re-scope stage 2. Blast radius: stage 2, the
relation table's handoff "fold".
F-5 (locate_finish §4.6) put rev-inner in LOCATE because "a NEXT row hands a candidate into the
composite, whose RECOVER walks back for the start; rev-inner already HAS the start". That
argument is about the DFA composite. The VM composite has no RECOVER: its NEXT row on
`CR_VM` (`first-class`, `pf->u.pf.emit_vm`, emit_dfa.c ~8150) hands candidate STARTS to the
attempt loop, and FIRST's `handoff-attempts[-entry]` hand a LOWER bound to it. The design's own
words match those slots exactly: the dup-param twin "splices into `rx_search_run`, before the
attempt loop" and "replaced exactly [first-class]" (excl-cand = a VM NEXT row handing exact
candidates `s*(j)`, RETRY "else the next hit"); `excl-lower` "LOWER(s*(j0)) to FIN4, the attempt
loop runs from there" = a FIRST handoff whose K is computed per hit by W (the design itself
calls today's handoff "the walk's bounded-width special case"). As NEXT/FIRST rows on CR_VM:
no VM LOCATE hat (L3) is needed, the req-handoff "fold" is simply row ORDER inside the same
slot (the walk above `handoff-attempts`, falling to it on decline), and the VM's existing
BOUND/RETRY/WIDTH cells keep working. Keep LOCATE for the DFA hat, where F-5's reasoning holds.

### SLOT-8 — W's BUILD condition is unstated, and the predicate needs W while W is built only for a selected row
CONFIRMED (code read; design gap). Severity: design (compile cost or a circular decision).
Effort: small (say it). Blast radius: every compile with an inner landmark.
The design names WHERE W is built (compile.c beside the optional machines, `revend_build_one`
pattern) but not WHEN. Rows 5-7 need values only W gives (overflow = decline; UNIQUE "lives
with the machine"), yet building W for every pattern rows 1-4 pass is ~300+ extra
`pcrec_build_min_dfa` calls over the corpus whether rarity then declines or not. Every sibling
states this: `build_notempty_dfa` "built where the retry table's winner needs it"
(compile.c:430); `revend_choose_form` walks its table twice, "once before anything is built (F0
and F1 need nothing), and again after the lowered builds" (emit_dfa.c ~13478); `split_conj[]`
marks each conjunct `CC_PRE`/`CC_POST` (compound.c:248). The admission table should carry the
same phase column (fact rows 1-6-without-UNIQUE PRE, W-fit/UNIQUE/A-built POST). Also: the cited
build site (compile.c ~3080-3105, beside `build_anchored_dfa`) is inside the ENG_UNANCH branch;
stage 2's W on a VM artifact has no named build site.

### SLOT-9 — UNIQUE has two homes and no stage-1 reader; the stage-1 LF-E1/DUPNAMES tests are vacuous
CONFIRMED (subject read). Severity: doc/test. Effort: trivial.
(a) §Admission: UNIQUE "is decided at build time on rev(P)"; §Build plan stage 2: "UNIQUE,
decided on W" (W = rev(P·L)); the facts paragraph: "UNIQUE needs rev(P), which exists only at
machine-build time". rev(P) and rev(P·L) are different machines; pick one.
(b) On the DFA route row 6's `G4 ∨ UNIQUE` is always decided by G4 (no references reach the DFA;
D151 add. 4: "On the DFA route G4 holds by construction"; row 2 `g1` already declines
backreferences), so UNIQUE has no stage-1 reader, yet the facts paragraph places its home now.
(c) Build plan 8 asks for "LF-E1 and DUPNAMES as DECLINES on the DFA route": both carry
backreferences, so they are VM-routed and declined by row 2 before row 6 is reached; the test
checks nothing about row 6/7. The witnesses belong to stage 2.

### SLOT-10 — a fourth member machine: the member folds and the always-built set are F/R/A-shaped, and the name `W` collides with walk form W
CONFIRMED (code read). Severity: maintenance/doc (stamps silently ignoring W). Effort: small.
`dfa_member_machines` (emit_dfa.c 4893) fills `const Dfa *out[3]` from F, R, A only; it feeds
the table-form name (4906), `<PREFIX>_DFA_SCAN_EDGE` (~4976) and `_DFA_UNIFORM_FOLDS` (~5039).
`cand_path_of` builds `p.built` from F|R / ATT / A / VM (~11927) and the FINISH totality
self-check has its own `always_built[3]` (~11405). A W bit must be added in all of them (and W's
scan edge — the design's whole optimization — must be reflected in `_DFA_SCAN_EDGE`, which folds
over members). The subject's "What moves on regeneration" lists only `RX_DFA_SCAN` and
`RX_VM_START_SCAN` (see SLOT-2). Naming: D164/endmark.md §R.4.6 already calls the walk FORM
"form W" (seed views resolved before the loop; `revend_seed_state`), which is the form this
walk should use; a machine bit `W` (CAND_MW) beside it invites misreading. Suggest `CAND_ML`
(landmark) or similar.

### SLOT-11 — the card prices the KIT's find on pcrec's card, and the landmark find + PRESENCE are two trips where D161 add. 14 rules one request
SUSPECTED (the p48 row text is in a denied lane report; argued from the subject + rulings).
Severity: design (D157/D146 boundary). Effort: small (move the quantity, merge the ask).
(a) §Measurement card: `lwbyte` = "the find floor per byte" (0.13 instr/B), owner `pcrec`. The
find of `L` is a kit site ("The kit's find of `L` supplies the hit"); measure_sets.md §7.1: "A
kit quantity is measured by the kit's harness mode: the forms and their timing arms are the
kit's (D157)". D161 add. 14: "the kit decides whether to scan at all". The committed set
measure_store/zen4-grid1/1 already carries kit-owned per-form costs and crossovers against the
DFA walk (`kit.beta.{A1,S1,V1,WALK}.DFA_SCAN`, `kit.xover.*.WALK.DFA_SCAN`). A pcrec card for
the find floor presumes the kit's method (memchr: the twins' `memchr '@'`) and duplicates a kit
quantity. The same applies to p48's "k* ≈ 2.3 B" price for the one-state relaxation if it is a
scan-vs-step crossover (that is what `kit.xover.*` is). Only `lwhit` (walk + verify per hit,
pcrec's machine) is pcrec's.
(b) The `.needs` keep a PRESENCE front (the pre-check on `req_byte`, which for 5b IS `@` = L,
`RX_REQ_BYTE "64"`) AND the walk's own find of L. D161 add. 14's clarification: "the pre-scan
and the candidate search are ONE request ... The kit returns one stream: EMPTY = no match".
The row should set `u.locate.whole` (the walk answers presence of L over the window; then
PRESENCE's `dominated` row fires, emit_dfa.c 8596) and state the landmark hits as ONE window
request to the kit, not a pre-check plus a find. Neither `.whole` nor the kit site/row
(DELEG_SITES list, `--memfn=no-NAME`, arms.tsv re-pin, C10 census) is in the Build plan.

### SLOT-12 — the ladder rung: wrong reason, and placed against the ladder's own cheapest-first order
CONFIRMED (spec read). Severity: speed (over-cap artifacts) / doc. Effort: small.
§Size: rung `drop-landmark-walk` "before rung 3 `drop-anchored`" because dropping A "would
leave `needs ⊄ built`, which is a defect", and before VM rung 1. (1) With SLOT-4's `A built`
conjunct the predicate declines when A is dropped and limits §8.4¶2a's strict-subset rule
already covers it (the rev-end precedent sentence of ¶2a is the same shape). (2) §8.4¶2: "The
order is by measured cost, cheapest first". The walk is the LARGEST measured gain in the design
(x70 on 5b), against `drop-anchored` ("`<prefix>_match`'s one-pass form") and `unroll-rescue`;
putting it first gives up the most run time first. A rung that drops W (keeping A) is still
legitimate, but its default place is LAST among its engine's rungs until measured (D149 label
kept), not first.

### SLOT-13 — Remodel overlap (D153) omits three STARTED rows the build touches
CONFIRMED (plan.md grep, `STATE:started`). Severity: design/schedule. Effort: trivial.
The subject's overlap list names [OPT-REVEND], [COMPOUND]/[MATCH-SPLIT], [DD-11.5], [INLINE-C].
Missing:
- [ENTRY-TABLE] (E0/E0c/E1 started, D163 add. 7): every exported entry is a controller over
  LOCATE/FINISH parts; a new LOCATE row that hands AT/LOWER to FINISH and relocates to the
  composite is exactly a new part edge in `entry_rows[]`;
- [FINDALL-NEXT] (started): `<prefix>_next` and its residual twins run the body per match; the
  walk's per-hit loop and the reach guard's `reach` are cross-call state candidates (D163's
  controller hook) and the find-all restart is cited in the unsound table;
- [MEASURE-SET] (started): `measure/cards.tsv` and the driver are its M3 deliverables
  (measure_sets.md §7.1-7.2); the subject's build "creates it", i.e. builds another row's
  artifact.

### SLOT-14 — which walk text: the twin wrapped RECOVER's reverse-pass, the ruled walk form is rev-end's form W
SUSPECTED (maintenance). Severity: maintenance (a third walk spelling). Effort: small (say it).
§Mechanism: "the existing reverse-pass floor code"; twins: "`extract_rw.py` wraps pcrec's own
reverse-pass text of `P·L`". [OPT-REVEND]'s [REVEND-WALK-FORM] answered "B3 adopts W for its
walks" (seed views resolved before the loop, first step peeled; per-iteration view probe was
the whole gap, T/W 1.47-1.90x), implemented as `emit_rev_end_one_seed`/`_tagged` over a
reverse `DfaForm` (emit_dfa.c 13696-13903). A seeded-at-`j+|L|` walk is that walk with a
different seed source and machine; the build should name it as a parameterisation of the
rev-end walk emitter, not a copy of RECOVER's reverse pass (which is seeded at a forward-pass
end and reads no landmark). This is also the general form below.

### SLOT-15 — row 3's input (P's width) has no home in the `back_walk` fact, and the fact's epoch/depends would not admit it
CONFIRMED (facts.def read). Severity: design (a private width derivation risk). Effort: small.
The `back_walk` value lists: landmark, P's sub-tree id, EXCLUSION, G4, top-level branch count,
rarity inputs — no width of P, yet row 3 `fixed` and the UNIQUE "fixed width implies it" form
need it. The row is `PF_FACT(BACK_WALK, ..., 2, PF_DERIVED, 0, ..., "req_set req_run
req_set_maxoff req_landmark_maxoff")`: epoch 2, while the width facts are E3 (`width`,
`kset_walk`, `run_pin`, facts.def:57-61, and E3 is "per branch"). Either back_walk reads an E3
fact (epoch must be 3, depends must name it) or it derives P's width itself (a second width
derivation, against "one derivation per pattern fact"). If row 3 becomes a `CAND_READ` of NEXT
(SLOT-6b) the width input disappears from this fact entirely. The depends column also omits the
byte-rate prior the rarity inputs read (allowed for PF_DERIVED, but say so).

## Ruling check

| ruling | agrees? | consequence the design did not draw |
|---|---|---|
| D161 add. 17 "Structure" | yes: reverse DFA as scaffolding, scan edges inside, admission table instead of tiers, fold candidates named | add. 17 says "Today's cases where a specialised method REPLACES the reverse DFA are candidates to fold under it". RECOVER's `pinned`/`end-minus-width`/`landing` replace R's walk with a constant; the relation table answers "no: a different seed" — true for W, but they are fold candidates of the SAME family (R's end-seeded walk) and want a fold row with a trigger, like `offset-set`'s |
| D161 add. 17 "Owner of the walk" | reconciled, not cited: the walk LOOP and W live in pcrec (compile.c, emitter); the kit owns the EDGE ADVANCE inside it | the design never states that "Structure" governs over "the walk is the kit's"; it should, in one line. Consistent with it: 5b's W is 9 cells / 1 edge, i.e. one kit reverse ADVANCE (`PcrecAdvance reverse`) inside a pcrec loop, which add. 17 says the kit already owns. No FIELD of `back_walk` presumes a kit method. The CARD does (SLOT-11) |
| R1 "no new table" (as the report states it) | holds for `cand_rows[]` (one row) | the admission table is a sub-table of the row (SLOT-6), the fourth of its kind (Sibling section): R1 is satisfied only if it takes the family's shared shape rather than a fifth private one |
| D151 + add. 1-7 | add. 1 (fold first: one row): yes; add. 4 (DFA hat first): yes; item 4 / D148 Q6 (one-way give-up): yes; item 6 / add. F=2 labelled: yes; "model re-run against 10.46": yes (unique_model) | add. 6/7 RULED a stage-1 admission of ONE common L across branches with per-branch verify and a composition rule; row 4 declines every multi-branch pattern and moves it to [MATCH-SPLIT]. That is a NARROWING of a ruled admission (population small: 1 corpus / 2 bench incl. ipv6, which D151 add. 4 listed among the top K12 cells) and needs to say so. add. 5's factor-free arm is HELD (row 8) with a trigger: acceptable, but also a narrowing to record |
| D148 | yes: one table, two hats, one deny | the VM hat's slot (SLOT-7) |
| D157 / D146 | fields: yes. Card + find: no (SLOT-11) | the landmark find is a delegated site the Build plan never names (site row, `--memfn=no-NAME`, arms.tsv pin, abi event) |
| D153 remodel first | partly | SLOT-13: [ENTRY-TABLE], [FINDALL-NEXT], [MEASURE-SET] missing from the overlap column |
| D174 | yes: `landmark-walk`, `-fno-landmark-walk` describe behaviour ("landmark" is already caller-facing in the `req-use` desc) | none |
| D149 | yes: F = 2, `gate_e6`, rung order all labelled UNMEASURED | the rung's PLACE is argued structurally, not left at the default end of the ladder (SLOT-12) |
| D164 | yes: `revend_build_one` is the right builder (overflow record saved/restored) | none found: the `tagged` swap of `job->dfa/rdfa/adfa` (compile.c ~555) fires only where LOCATE is `rev-end` (`pcrec_revend_form_asked`), and `rev-end` precedes the new row |

## Sibling of a family

YES. The admission table is the FOURTH member of the family "a row's own admission/form
sub-table": a declared list, walked first-match, whose first failing row is the decline reason
(or whose first holding row is the form), owned by ONE row of a bigger table:
1. `split_conj[]` — `CompConj` {id, desc, phase CC_PRE/CC_POST, holds, reads} (compound.c:248),
   the admission of `compound_rows[]`'s `split` row (D163 add. 4 (b));
2. `cover_conj[]` — `CoverConj` {cid, id, kind, holds} (known.c:373), the admission of the
   `cover` LOCATE row, first failing = `why` ("the `split_conj[]` shape");
3. `revend_forms[]` — `RevendFormRow` {name, deny, applies, form, desc} (emit_dfa.c ~13512),
   the FORM of the `rev-end` LOCATE row, listed as the `rev-end-form` sub-axis;
4. proposed: `landmark-walk`'s admission (conjuncts) PLUS its hand form (CAND vs LOWER).
Three private struct types and three walkers today, a fourth proposed. Unified table: one row
type `RowConj { id; desc; phase (PRE/POST, the build split SLOT-8 needs); deny; holds; form }`,
one walker returning `{why, form}`, one listing projection (`pcrec_cand_list_row` sub-axis
`<row>-admit`, generalising today's `rev-end-form` special case at emit_dfa.c ~12206), one trace
record. `CandRow` (and `CompRow`) carry `.admit = {table, n}`; a LOCATE row's predicate is the
walk of its admit table. `landmark-walk` is then built as a table on that type, and the three
existing ones migrate as no-mover commits (simplification: three structs and two hand walks
deleted). Trigger: the stage-1 build (the fourth instance is written then).

## General form and unlocks

General form: START RECOVERY BY A REVERSE WALK (D161 add. 17's family) as ONE walk with three
columns — SEED SOURCE {forward-pass end (RECOVER `reverse-pass`), subject end (`rev-end`),
landmark hits (`landmark-walk`), the kit's candidate/window stream}, MACHINE {R, rev(P·L),
L4's relaxed machine}, OUTPUT {smallest accept, every accept ascending} — one emitter (form W
over a reverse `DfaForm`), rows differing only in their admission sub-table (above).
Unlocks, each with its trigger:
- U1 OUTPUT = every accept ascending (`starts(j)` per hit, verified in order): exact without
  UNIQUE or G4 (each start the shipped loop could try for that hit is tried), so `excl-cand` /
  `excl-lower` merge on the VM and the ruled D151 add. 6 multi-branch admission (common L,
  per-branch starts) falls out of one reverse DFA over the alternation. Trigger: stage 2 opens,
  or a bench cell in the `branches` row (ipv6, `altwide/sfx-*`) is a mover.
- U2 SEED = the kit's window stream (D161 add. 7/9: the finder streams exact candidate starts):
  the landmark becomes any kit window, not only a `req_*` literal, and PRESENCE + find become one
  request (SLOT-11b). Trigger: the kit's window request (R-21) delivers a stream pcrec can read.
- U3 one walk emitter for `rev-end` and `landmark-walk` (SLOT-14). Trigger: now (stage 1).
- U4 fold RECOVER's constant-width shortcuts and the EXACT-k NEXT rows as constant walks.
  Trigger: the stage-1 `lwhit` card at width k within noise of `offset-set`/`end-minus-width`.
- U5 a forward twin: a landmark-seeded FORWARD machine over L·S for the end, replacing the
  anchored verify from `s*`. Trigger: the `lwhit` card shows verify, not walk, dominating per hit.

## PROBED-AND-HELD

- Relation-table row names and slots, against `cand_rows[]` (emit_dfa.c 10160-10650), 15 rows:
  `rev-end`, `cover`, `composite` are LOCATE in that order (`empty` first); `run-pinned[-bounded]`,
  `offset-set[-bounded]` are NEXT, CR_DFA, `CM_EXACTK`; `handoff`, `handoff-attempts`,
  `handoff-attempts-entry` are FIRST; `handoff-reentry` is NEXT (CR_DFA); `first-class` is NEXT
  on CR_VM; RECOVER is `pinned`, `end-minus-width`, `landing`, `reverse-pass` in that order;
  `rev-end-relaxed` is filed (locate_finish §2.4). All held as stated.
- Placement `empty, rev-end, cover, landmark-walk, composite`: held (both earlier rows answer
  the whole call with no per-hit loop; `composite` is `cand_always`).
- Deny-bit budget: bits 0-54 and 56 used; 55 (kept free by D163 add. 2) and 57-63 free = 8,
  as the subject says; one more leaves 7, above [IFACE-PUSH]'s ≤ 4 trigger. Held.
- `PF_FACT` row shape (7 fields) and its depends names (`req_set`, `req_run`,
  `req_set_maxoff`, `req_landmark_maxoff` all exist, facts.def:50-56): held (epoch: SLOT-15).
- `revend_build_one` (compile.c:450) as the builder: overflow saved/restored, scan-edge pass run
  on the machine: held.
- Stamp of a LOCATE row is `RX_DFA_SCAN` on every route (`cand_list_stamp`): held for the DFA
  hat (SLOT-2 for the VM line).
- Ladder count: 8 rows today (0, 0a, 1, 2, 3, 4, 4a, 5), "all eight" → nine: held.
- D164 `tagged` swap vs the new row: no interaction (only under `rev-end`). Held.
- LOWER is an existing hand (`CAND_HAND_LOWER`, taken by FIN4 on CR_VM): the VM hat's
  `excl-lower` hand needs no new vocabulary; only the DFA route does (SLOT-1).
- Probe: 3 compiles (slots/probe_row3.sh) for SLOT-6(b); no other compiles.
