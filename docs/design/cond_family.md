# The conditions family: every test-then-branch and intersection construct, the machinery each needs, and what they share

**Status: SURVEY rev 0, owner answers recorded in §7 (D193, lane condans, 2026-11-10; plan row
[COND-FAMILY]).** Design and survey only: no code, no build go. Code cites are at main `568465ef7` (no change
under `src/ cli/ lib/` since `956055581`). Engine facts are MEASURED by compiling with the
main-tree `build/pcrec --features all` (`docs/dev/lanes/condsurv_evidence/engine_probe.txt`).
PCRE2 facts come from the libpcre2-measured lane condinv (`docs/dev/lanes/condinv_report.md`, 164
cases) and two new pcre2-reader notes: `docs/dev/pcre2_notes/script-run-evaluation.md` and
`docs/dev/pcre2_notes/dfa-matcher-conditions.md`. Marks: MEASURED, READ (code or a note), INFERRED.

Owner's charter (Frank, 2026-11-10): "Yes. Let's start or designate a master to all these. Perhaps
others were missing? It should look at the machinery needed to satisfy and the common elements.
Then we can plan them all together."

## Goals

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | every member found, missing ones included | the owner, planning | each construct in the registry (`--list-syntax`) and each plan row that is a test-then-branch or an intersection appears in §2 or in §2.3's "not members" list, with a reason |
| G2 | each member's machinery named, shared pieces found | whoever designs the first piece | every §3 machinery row names its members; every member names at least one machinery row |
| G3 | one recommended first piece | the owner | §5 names it, its clients, and the D77 measurement that would start it |
| G4 | each member's DFA-blocking reason, for [ENGINE-WHY] | users forcing `--engine=dfa` | §2's "blocks the DFA because / keep the DFA by" column, one line per member |

Priority on conflict: G1 > G2 > G3 > G4. Non-goals: no design of any member, no syntax choices
(D26: pcrec extensions need the owner's go and a non-colliding spelling), no measurement runs.

## Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** Not relevant to this survey: it introduces no measured quantity. The
   engine probe is a compile-time fact (which engine a pattern gets), not a timing. §5 NAMES the
   measurement that would trigger the first piece; that piece's design note answers this question.
2. **Independent control.** Partly relevant: the member list is checked against two sources that do
   not share an author with the plan rows: the compiler's own registry (`--list-syntax`) and the
   PCRE2 reader notes. The engine column is the compiler's own stamp (`RX_ENGINE`), so it is a
   statement of what pcrec does, not of what is possible; the "possible" column is INFERRED.
3. **What moves when data is regenerated.** Not relevant: no table, stamp or generated file.

## 1. The starting hypothesis, tested

The kit's analysis (accepted by Frank as a starting point): [CONDITIONALS] and [POSTFACT] are one
mechanism, one CONDITION node (test, yes-arm, no-arm) with test kinds group-set, assertion,
call-context, constant and predicate; a where-clause is that node with a fail branch; `set(a)` is
the group-set test, DFA-able with one participation bit per tested group; assertion conditions are
`&` intersection, the same layer as [ENG-LOOK]; only `(?(R))` stays VM-only; condinv's "all VM"
predates the predicate notes.

| claim | verdict | why |
|---|---|---|
| one CONDITION node serves both rows | HOLDS at the IR layer, NOT at the engine layer | condinv §3's `A_COND` (test, yes, no) covers every test-then-branch member. But the DFA never hosts a node: what makes any member DFA-able is a PRODUCT with a small checker automaton (§4, C3). POSTFACT's own 2026-11-06 note says the same ("its result is an automaton, not a node"). So the family has TWO common elements, the node (how the VM and the analyses see it) and the product (how the DFA gets it), plus the name table (§4) |
| a where-clause is the node with a fail branch | HOLDS (VM) | at the IR, `rx ## P` = `A_COND(P over the scope, yes = continue, no = fail)`. For the DFA it is `&` against P's automaton over the same span |
| `set(a)` is the group-set test, one bit per tested group | HOLDS, with a size note | "set" is publish-at-close, sticky across iterations, unset inside a failed negative lookahead, restored after a call (condinv K1, MEASURED); every one of those is finite state per path, so a determinized state is a set of (NFA state, bits) pairs: worst case x2^k states for k tested groups (INFERRED). Caveat, READ: PCRE2's own breadth-first matcher REFUSES group-set conditions at match time (error -40, `dfa-matcher-conditions.md` §1), so there is no PCRE2 prior art to lean on; pcrec's DFA is a different machine (determinized, leftmost-first) and is not bound by that choice |
| assertion conditions are `&`, the [ENG-LOOK] layer | PARTLY | `(?(?=A)Y|N)` is a POSITIONAL test (A may extend past the yes-arm's span), so it is [ENG-LOOK]'s product (a checker read at a position), not span `&`; `&` is its CONTAINED special case (POSTFACT 2026-11-08). It reaches the DFA today when A is one character wide: `(?:(?=a)ab|(?!a)cd)`, the desugared form, compiles to the DFA (MEASURED) because width-1 lookarounds are `A_CTX` nodes (`src/parse/ctxnode.c:1-11`) |
| only `(?(R))` stays VM-only | TOO NARROW | the non-regular residue is wider: recursion conditions in a RECURSIVE pattern (in a non-recursive one `(?(R))` folds to a constant per spliced copy, condinv §2), backreferences and predicates relating two unbounded run-time values (`$a < $b`, POSTFACT 2026-11-09), `scan_substring` over a capture's value, callouts, and anything with captures inside a lookaround body (VM unless the finishing pass honours it, §3 M7) |
| condinv's "all VM" predates the predicate notes | HOLDS | condinv (2026-11-05) predates POSTFACT's 2026-11-08/09 notes and does not count the width-1 `A_CTX` route |

## 2. The members

Kind codes: **SET** (did a group/label take part), **LOOK** (a positional assertion), **CTX** (a
one-character context set, `A_CTX`), **CALL** (call context), **CONST** (compile-time or call-time
constant), **PRED** (a typed predicate over a span), **AND** (span intersection/complement),
**MARK** (reported start/end), **NAME** (the name/number table). Layers (POSTFACT 2026-11-09,
Frank's three): L1 lookaround surface, L2 span algebra, L3 automata. Engine today: MEASURED where a
probe is cited, else from the registry's engines column. "Possible" is INFERRED.

### 2.1 PCRE2 constructs

| # | construct | row | what it is | kind / layer | engine today | possible, with which machinery (§3) | blocks the DFA because / keep the DFA by ([ENGINE-WHY]) |
|---|---|---|---|---|---|---|---|
| P1 | `(?(1)Y\|N)` `(?(+1)` `(?(<n>)` `(?('n')` `(?(n)`, dup names | [CONDITIONALS] | yes-arm iff the group is set | SET / L1 | refused, unbuilt (`src/parse/registry.c:1083`, VM_ONLY) | VM: M1+M2 (if/else on the slot, `vm_bref`'s test, `src/gen/emit_vm.c:9030`). DFA: M3 participation bits | "tests a group's participation"; keep DFA: none today (after M3: no captures needed elsewhere) |
| P2 | `(?(?=A)Y\|N)` and the three other assertion conditions, `(*pla:` spellings | [CONDITIONALS] | yes-arm iff the atomic assertion holds; its captures survive into the taken arm | LOOK / L1 | refused | VM: M1 + `vm_look` with two exits (`emit_vm.c:7708`). DFA: M4 (positional checker) for capture-free A; width-1 A already via CTX if lowered as `(?=A)Y\|(?!A)N` for the DFA only | "an assertion condition"; keep DFA: one-character A, written `(?:(?=a)Y\|(?!a)N)` (MEASURED dfa) |
| P3 | `(?(R)` `(?(Rn)` `(?(R&name)` | [CONDITIONALS] | inside any call / most recent call is group n | CALL / L1 | refused | VM: M1 + M11 (one trailed slot). CONST per spliced copy when no recursion (condinv §2). PCRE2's DFA matcher accepts `(?(R)` and refuses `(?(Rn)` (`dfa-matcher-conditions.md` §1) | "recursion test"; keep DFA: none in a recursive pattern |
| P4 | `(?(DEFINE)...)` | built (module recursion, `registry.c:1110`) | never runs; a library of groups for calls | CONST / L1 | DFA when the calls splice and nothing else captures: `(?(DEFINE)(?<o>[0-9]+))(?&o)\.(?&o)` -> dfa (MEASURED; `src/opt/select_engine.c:246`) | already the label-library shape (§2.2 X5) for capture groups | "a capture group outside DEFINE" (`(a)(?(DEFINE)...)` -> vm, MEASURED) |
| P5 | `(?(VERSION>=n.m)` | [CONDITIONALS] | library-version constant | CONST / L1 | refused; ruled out of scope, but the message says "not implemented yet" (condinv §0) | trivial fold | n/a |
| P6 | `(?(?C1)(?=a)Y\|N)` | [CONDITIONALS] + [INLINE-C] | a callout before an assertion condition | LOOK + callout | refused; `src/opt/callout.c:32` "Row 2 ... cannot arise" | VM only (callout) | "a callout" |
| P7 | lookaround whose body is a set of single characters | built ([UCP] U2 T3) | one context node `A_CTX(set, side, fn)` | CTX / L3 | DFA (`x(?!y)`, `(?<=[ab])c`, `(?<!\d)\d{4}(?!\d)` -> dfa, MEASURED; `src/parse/ctxnode.c:131`) | already the width-1 instance of M4 | n/a (already DFA) |
| P8 | any other lookaround, capture-free, bounded | built (VM) | positional atomic assertion | LOOK / L1 | VM (`(?=ab)a[a-z]`, `(?<=ab)c`, `x(?=y\|zz)` -> vm, MEASURED); erased to epsilon for the prefilter (`src/ir/nfa.c:759`) | DFA: M4 ([ENG-LOOK]'s product). Fixed lookbehind also by M8 (the `\K` rewrite with a floor, POSTFACT 2026-11-08) | "a lookaround wider than one character"; keep DFA: none general; a contained lookahead can often be folded by hand into the consumed text |
| P9 | bounded variable lookbehind `(?<=a{1,3})b` | [VLOOKBEHIND] (stage 1 built, D189) | lookbehind of several widths | LOOK / L1 | VM (MEASURED) | VM: built; DFA-checked inside the VM by M6 (A-REV reverse run, `docs/design/stream/arev.md`); DFA by M4 (Σ*·L checker) | "variable-width lookbehind" |
| P10 | unbounded lookbehind `(?<=a+)` | [LB-EXIST] | refused by PCRE2 too (error 125) | LOOK | refused | M4/M6 as an existence filter | n/a |
| P11 | non-atomic lookarounds `(?*..)` `(?<*..)` | built (VM) | lookaround that backtracking may re-enter | LOOK | VM (registry) | capture-free: same language as the atomic form, so M4 applies (INFERRED: re-entry changes only captures) | "non-atomic lookaround with captures" |
| P12 | `\K` | built (VM, `A_KRESET`) | resets the reported start | MARK / L3 | VM (`ab\Kcd`, MEASURED); PCRE2's DFA matcher refuses it (`dfa-matcher-conditions.md` §3) | DFA: M8 (a start mark; constant offset when the text before it is fixed width, as [ENG-TDFA] start tags in general) | "`\K` resets the start" |
| P13 | `(*FAIL)` `(*F)`, and `(?!)` | [PCRE2-GAPS-TBD] (`(*FAIL)`); `(?!)` built | always fails | CONST false | `(*FAIL)` refused (verbs); `a(?!)b` -> VM (MEASURED) | fold to "dead" ([DESC-DEAD], [NEVER-MATCH]); PCRE2's DFA matcher supports `(*FAIL)` as a failing assertion (note §3) | "an empty negative lookahead"; keep DFA: delete the dead branch |
| P14 | script runs `(*sr:..)` `(*asr:..)` (RULED D193: a member, a different SPELLING of predicates, same evaluation as a where-clause, built on the predicate machinery, no row until a use appears) | NEW (registry `(*ACCEPT)` row, verbs, unbuilt; compliance PLANNED; not in [PCRE2-GAPS-TBD]'s list) | the span the group matched must be one script; checked at the group's END, failure backtracks into the body (`script-run-evaluation.md` §1) | PRED / L2 | refused | VM: M7 exactly (honour on close). DFA: M4+M5 (a script-set checker automaton: the state is the running intersection of script sets plus the digit-set rule; finite, so regular; the compliance annotation already says "the assertion itself is regular"). PCRE2's own DFA matcher refuses it | "script run" |
| P15 | `(*scan_substring:(1)A)` `(*scs:..)` (RULED D193: re-marked planned, a member of the family, no work until a use appears) | NEW (registry ROADMAP_NEVER, `src/parse/mod_verbs.c:226`) | assert A over the text a capture group matched | AND over a capture / L2 | refused, out of scope; its annotation says "(revisit post-M4) ... needs capture state at match time" and M4 has shipped | VM: an `&`-check over a slot's span (M7's shape, run at the point, not at close). DFA only when the referenced group is fixed-offset (as [BREF-SPAN]) | "scans a captured substring" |
| P16 | backreference unset test; `PCRE2_MATCH_UNSET_BACKREF` | built (`vm_bref`); option RIDES backrefs (`docs/pcre2_options.md`) | the SET test with a compare after it | SET | VM | the SET half is P1's machinery; the compare is not regular | "backreference" |
| P17 | `(*ACCEPT)` | [PCRE2-GAPS-TBD] | ends the match at once | MARK (end) | refused | VM; it BYPASSES a script run's check (note §1) and P12's mark rules; PCRE2's DFA matcher refuses it | "(*ACCEPT)" |

### 2.2 pcrec's own surfaces (built, or proposed in [POSTFACT]'s body)

| # | construct | row | what it is | kind / layer | engine today | possible, with which machinery | DFA reason |
|---|---|---|---|---|---|---|---|
| X1 | `${name:+w}` `${name-w}` `${name:-w}` `${name:?w}` in a pattern | built ([VAR]; `docs/spec/vars.md` §2) | an arm chosen by whether a caller variable is set or empty | CONST (call-time) | VM (`A_VAR` VM_ONLY) | it is a condition already; no regular hosting (the value is run-time) | "a caller variable" |
| X2 | `${n:+set:unset}` in a substitution template | built ([M4-SUBST]; `docs/spec/subst_api.md` §2) | the SET test, on the template side of the seam | SET (after the match) | n/a (template) | same SET semantics as P1; one definition of "set" should serve both | n/a |
| X3 | callout returning fail; [INLINE-C] stage 4 `verify` (a D156 FINISH row) | built (callouts); [INLINE-C] started | a user predicate at a point | PRED, non-regular / fallback | VM | M9: the fallback for every non-regular predicate | "a callout" |
| X4 | where-clause `rx ## P` (placeholder spelling) | [POSTFACT] 2026-11-08 | predicate over the in-scope match so far | PRED / L2 | proposed | VM: M1 (fail branch) + M7. DFA: M4+M5 | — |
| X5 | labels `(?':name'...)` and calls to labels; label libraries in DEFINE | [POSTFACT] 2026-11-09 | named, non-capturing span; a call inlines it | NAME / L2 | proposed (P4 is the capture-group version, already DFA) | M2; non-recursive calls already splice (`select_engine.c:246`) | — |
| X6 | `&` and `&!` span intersection/complement | [POSTFACT] 2026-11-09, [ENG-LOOK] 2026-11-06 | both operands match the same span (or the left and not the right) | AND / L2 | proposed | DFA: M4 (complement needs the right operand determinized first). VM: M7's "run the check once per start, record its end set" (POSTFACT 2026-11-09 VM-cost note) | — |
| X7 | `set(a)` `unset(a)` | [POSTFACT] 2026-11-09 | participation of a label | SET / L2 | proposed | as P1 (M3 for the DFA) | — |
| X8 | typed predicates: integers (no width), fixed point, membership, `% k`, strings, user functions (`leap(y)`), finite-value splits across labels | [POSTFACT] 2026-10-27..11-09 | one-label predicates lower to automata; relations between two unbounded labels do not | PRED / L2 | proposed | M5 (predicate -> automaton), M4, M10 (size ladder) | — |
| X9 | group-0 group `(?<0>B)`, end mark, explicit numbers `(?<N>..)` | [POSTFACT] 2026-11-08/09 | a group that IS the match; a group writing slot N. RULED (D193): at most one group 0 on any path (alternation max, sequence sum, repeat multiply; a second is refused at its offset); a path with none reports the whole match; consumes its outside context | MARK + NAME | proposed, rule ruled | M8 + M2; VM: a capture whose span replaces the match; DFA: fixed-context form = lookaround context via C3, inside an alternation needs capture tracking (VM) | "group 0 inside an alternation needs capture tracking; use one top-level group 0 to keep the DFA" |
| X10 | `(?\|...)` branch reset | [BRANCH-RESET] | alternatives reuse numbers | NAME / L1 | refused, unbuilt (MEASURED) | M2 only (front end); sugar over X9's `(?<N>)` if that is ruled in first ([BRANCH-RESET]'s own build note) | n/a (numbering only; captures decide the engine) |
| X11 | class set operations `(?[...])` | [CLASS-SETOPS] | intersection/complement of one-character sets | AND at width 1 | refused, unbuilt | class algebra (already exists for classes); the width-1 instance of X6 and shares its operator vocabulary (POSTFACT 2026-11-06) | n/a (DFA once built) |

### 2.3 Readers and neighbours (members by use, not by construct)

- **Fact layer, the necessary-condition shadow of intersection**: [REQ-LOOKAROUND] (span_arms L1-L3:
  a positive lookaround's item as guards, met against consumed runs, `docs/design/span_arms.md` §2,
  §5), [CTX-PREFILTER], [LOOK-LOCATE], and D168's one context producer. These never change an
  engine; they read the same facts the product would compute exactly.
- **Consumers of emptiness/disjointness**: [DESC-DEAD], [NEVER-MATCH] (an empty intersection is a
  proved never-match).
- **Superset machinery for SET bits**: [ENG-TDFA] (position tags; a participation bit is a tag with
  no position) and [CAPS-KNOWN].
- **Equality post-check**: [BREF-SPAN] (a superset DFA plus one span-equality check) is the
  relational-predicate case done by locate-then-check, the same shape as M7.
- **Non-regular fallback helpers**: [SPAN-HELPERS] (callout helpers such as a numeric compare of two
  digit spans: the relational predicates X8 cannot lower).

Not members (checked, with the reason): atomic groups and possessive quantifiers (control, not a
test); `(*COMMIT)` `(*PRUNE)` `(*SKIP)` `(*THEN)` `(*MARK)` (backtracking control; PCRE2's DFA
matcher refuses them too, note §3); `\G` (a run-time position pin, already DFA, MEASURED);
[PIECE-ACCEPT-RULE] (a kit rule named "intersection" over search pieces, not regex languages);
[CALLOUT-GROUPS] and [MATCH-EVENTS] (callout surfaces, no test); [ARRAY-CAPTURE] (numbering of
iterations; touches the name table only).

## 3. The machinery

| id | machinery | exists today? | members that need it |
|---|---|---|---|
| M1 | the CONDITION node `A_COND(test, yes, no)` with every tree walker taking both arms | no; condinv §3's design; `case A_LOOK` sites are the size guide (75 in 27 files, MEASURED by grep) | P1 P2 P3 P5 P6, X4 (fail arm), X7 |
| M2 | the name table: names, numbers and slots, resolved after the whole parse; labels with no slot; explicit `(?<N>)`; dup names; name-beats-`R` | partly: `pcrec_bref_resolve` (`src/parse/mod_backrefs.c:687`, called at `src/parse/parse.c:2361`) resolves numbers and names for backrefs and calls, forward references included | P1 P3 (name-beats-R), X5 X7 X9 X10, X8 (predicates name labels) |
| M3 | participation bits in the DFA (states x bits for k tested groups/labels) | no | P1 (DFA), X7, P16's SET half; subsumed by [ENG-TDFA] if tags land first |
| M4 | ONE product construction: the main automaton with a small deterministic CHECKER, plus complement of a determinized checker | the width-1 instance exists: `A_CTX` on the DFA's class axis (`ctxnode.c:5-11`); ruled to be built once for [ENG-LOOK] and [POSTFACT] (POSTFACT 2026-11-06) | P2 P8 P9 P10 P11 P14 (DFA), X4 X6 X8 X11, [NEVER-MATCH] |
| M5 | predicate -> automaton compiler (ranges, `% k`, membership, fixed point, script sets, user functions) | no | X4 X8, P14 (script set) |
| M6 | reverse run hosted in a VM body (A-REV's automaton-run record) | designed (`docs/design/stream/arev.md`, PROPOSED rev 2; [STREAM] go for its chain) | P9, P10; its forward twin is M7 |
| M7 | VM honour-on-close: at a group/label close (or a point), run the span through a small checker DFA; failure backtracks | no; the VM's lookaround machinery (`vm_look`, `emit_vm.c:7708`) is the nearest | P14 (exactly PCRE2's own evaluation), P15, X4 X6 (VM side), X8 with captures present (POSTFACT 2026-11-09: the finishing VM must honour predicates) |
| M8 | report marks: start mark, end mark, a constant offset when the marked text is fixed width | `\K` in the VM only | P12, P17, X9, P8's fixed-lookbehind rewrite (POSTFACT 2026-11-08) |
| M9 | callout fallback for non-regular predicates | built (callouts, [INLINE-C] stages 0-3) | X3, relational X8, [SPAN-HELPERS] |
| M10 | size ladder and pricing: estimate before building, decline to the VM past the cap | the DFA state cap and [ENG-CUT]'s decline shape | every M3/M4/M5 member |
| M11 | a trailed call-context slot in the VM | no (condinv §2) | P3 only |
| M12 | the fact layer (guards, context producer) | designed (span_arms L1-L3) | §2.3's readers |

## 4. The common elements

**C1. The condition node (M1).** One IR shape, test + yes + no, with the test a declared kind
(SET, LOOK, CALL, CONST, PRED). What it unlocks: all of [CONDITIONALS] on the VM; the where-clause
as the PRED kind with a fail arm; `set()/unset()` as SET over labels. Seen through it, a lookaround
is a condition whose no-arm fails and a backreference's unset test is a SET test followed by a
compare (condinv §3). It is a VM and analysis element: no engine hosts it directly.

**C2. The name table (M2).** Names are labels (compile-time identity of a span), numbers are capture
slots (run-time values) (POSTFACT 2026-11-09). One resolver after the whole parse, which
`pcrec_bref_resolve` already is for backrefs and calls. What it unlocks: condition resolution
(numbers, relatives, names, dup names, name-beats-`R`), branch reset, `(?<0>)` and `(?<N>)`,
labels, and the predicate language's references. Every NAME member is mostly front end.

**C3. The checker product (M4, with M3, M5, M10 as its inputs).** The finding of this survey:
every way a member reaches the DFA is the SAME construction, the main automaton run in product with
a small deterministic checker, differing only in WHERE the checker starts and WHERE its state is
read. A declared (start, read) table covers the family:

| start | read | members |
|---|---|---|
| the group/label opens | it closes; must accept exactly there | X6 `&`, X4 where, X8 predicates, P14 script runs, contained lookaheads `(?=A)B` = `(AΣ*)&B` |
| the position p | when the checker accepts, possibly past the match | P2 P8 extending lookaheads ([ENG-LOOK]'s delayed acceptance) |
| the scan start (seeded from the bytes before it) | at p | P8 P9 lookbehinds, Σ*·L ([ENG-LOOK]); P7 is today's width-1 case |
| a group closes (sets a bit) | a condition | P1 X7 (M3: the checker is a k-bit flag register) |

Complement (`&!`, negative lookarounds, P2's no-arm) is the same product with the checker's accept
inverted, which needs the checker determinized and complete first (bounded bodies only). The DFA
cost of every DFA-hosted member is therefore one priced product, refused past the cap (M10).

**C4. The cross-engine check (M6 and M7).** The VM drives and a small DFA checks a span: backwards
for lookbehind (A-REV), forwards at a close for predicates, script runs and `&` with captures. It is
the VM-side twin of C3 and uses the same checker automaton, so one checker serves both engines.

## 5. Dependency graph and the first piece

Order-free graph (an arrow reads "unlocks"; members in brackets):

```
M2 name table ──> P1 P3 X5 X7 X9 X10 (resolution, numbering)
M1 cond node ──┬─> P1 P2 P3 P5 (VM) ──> P6 (+ callouts)
               └─> X4 where (VM, with M7)
M11 call slot ───> P3 (Rn)
M4 product ──┬─> P8 P11 (DFA) ──> P2 (DFA, via both polarities)
             ├─> X6 & &! ──> X11 (width-1 instance) ; [NEVER-MATCH] (empty product)
             ├─(+M5)─> X4 X8 P14 (DFA)
             └─(+M3)─> P1 X7 (DFA)
M7 honour-on-close ─> P14 P15 (VM) ; X8 with captures ; X6 (VM)
M6 reverse run ─────> P9 P10 (VM, DFA-checked)
M8 marks ───────────> P12 P17 X9 ; P8 fixed lookbehind (DFA, by rewrite)
```

Cheapest piece: M1 with SET and LOOK tests on the VM (condinv's first slice, "medium"). It flips
four corpus refusal pins and one bench syntax probe, but condinv found NO outside demand (zero wild
or realistic patterns), so it unlocks the least that anyone uses.

Owner ruling (D193): SPEED leads, so this is the first piece; the syntax-first alternative below
is an ordering question only (the product and the node are separate machinery; the name table M2
is the one shared piece).

Piece that unlocks the most: **C3, the checker product, built for its first (start, read) row,
with no new surface syntax.** First client: capture-free, bounded lookarounds that today send a
pattern to the VM (P8), which is [ENG-LOOK] itself. Why first:
- it is the only piece with a measured population: [ENG-LOOK]'s census (98 fixed-width
  occurrences, `docs/dev/eng_look_census.md`) and [CTX-PREFILTER]'s (143 still-VM patterns with a
  positive multi-character lookaround, `docs/dev/ctx_prefilter_census.md`), both 2026-09-29 and
  taken before [UCP] U2 moved the width-1 cases to `A_CTX`, so they must be re-counted;
- every later DFA member (`&`, where, predicates, script runs, set bits, assertion conditions) is
  the same construction with another (start, read) row or another checker (§4 C3), and the 2026-11-06
  ruling already says to build it once for [ENG-LOOK] and [POSTFACT];
- it moves engines, not facts, so it answers [ENGINE-WHY]'s "keep the DFA by" for the largest
  member group.

Its trigger (D77): a re-count, on the corpus plus bench, of patterns whose ONLY DFA-blocking
construct is a capture-free bounded lookaround wider than one character, with a bench cell among
them. Its gates: D153 (remodel first: the product touches `src/ir/` DFA construction, which [STREAM]
A-REV's record also touches, so the remodel-overlap column is NOT empty) and D119/D137 ([ENG-LOOK]
sits in Candidates and is selected by measurement when an [OPTLOOP] cycle opens).

If the owner instead wants pcrec to accept refused PCRE2 syntax first (completeness, not speed), the
first piece is M2 + M1 on the VM (P1, P2, X10), in that order, because the name table is what
makes conditions, branch reset and the POSTFACT naming all resolve one way.

## 6. Rulings that bear on the family (cross-checked)

| ruling | bears on |
|---|---|
| D26 (+ 2026-10-24 addendum: compatible unless a PCRE2 bug) | P5's out-of-scope message is D26-tier; every pcrec surface (X4-X9, `&`) is an extension needing the owner's go and a non-colliding spelling |
| D62 (kinds encode structure, fields parse-resolved state) | why one `A_COND` kind with a test field, not one kind per test (condinv §3) |
| D67 (SR-8: engines from producer-stamped registry masks) | a new member's engine exclusion is its registry row's VM_ONLY stamp; lifting it per test kind means the producer stamps by kind (as P7's `A_CTX` is born unstamped, `ctxnode.c:18-20`) |
| D71 (subroutine rulings) | P4 DEFINE and splicing; X5 label calls |
| D77 (build under measurement) | §5's trigger; no member is built ahead of its count |
| D119 / D137 | [ENG-LOOK] is a Candidate, selected by measurement |
| D146 / D157 (kit facts only) | none of C1-C4 is kit work; the fact layer (§2.3) talks to the kit in facts |
| D153 (remodel first) | the product's DFA-construction site overlaps [STREAM]'s A-REV |
| D156 (LOCATE x FINISH) | M7 is a FINISH-side check; X3's `verify` is a FINISH row |
| D168 (+ add. 1, 3) | P7 is a node, not a rewrite; the context producer is the fact shadow of C3's lookbehind row |
| D172 (spans carry negative offsets) | the fact layer's read-before-start (span_arms §7) |
| D181 | the two new reader notes this survey cites |
| D186 (unit vs choice changes) | C3's first client is a UNIT change for the patterns it moves (engine choice by construct) |
| D189 ([VLOOKBEHIND] stage 1) | P9 built on the VM; M6 is its DFA-checked successor |
| D192 | the master row is read through `scripts/entry` like any row |

## 7. Owner's answers (2026-11-10, D193)

Asked as six questions with leanings; answered by Frank 2026-11-10 and recorded as D193.

1. **Speed leads.** ("speed but is this just an ordering question?") The shared checker-product
   piece comes first, for capture-free lookarounds ([ENG-LOOK]), after the lookaround censuses are
   re-counted. Answer to the question asked: YES, it is an ordering question. The checker product
   (DFA side) and the condition node (VM side) are separate machinery, so neither order causes
   rework; the only piece both need is the label/name table (M2), which whichever comes first
   builds. The cost of speed-first is only that the syntax members (conditionals, branch reset)
   stay refused longer.
2. **The core is one product construction with (start, read) rows** ("yes"); the condition node
   stays the VM's and the analyses' shape.
3. **Script runs (P14) are a member** ("agree"): a different spelling of predicates (the same
   evaluation as a where-clause), built on the predicate machinery, no row of their own until a use
   appears.
4. **`(*scan_substring:...)` (P15) is re-marked planned, a member of the family** ("agree"); no
   work until a use appears.
5. **Honour-on-close** ("agree"): the backtracking engine checks label predicates at a group's
   close when captures are present, built with the first predicate build; the mix is not refused.
6. **This family owns the order of the shared pieces** (node, name table, product) ("agree");
   member rows keep their own triggers for their own front ends.

**Group 0 (X9), owner discussion 2026-11-10:** no path through the pattern may pass a group 0 more
than once (alternation: max over branches; sequence: sum; repeat: multiply; above 1 refused at the
second occurrence's offset). Each alternative may carry its own; a path with none reports the whole
match. VM: a capture whose span replaces the match (cheap). DFA: the fixed-context form (one
occurrence, outside parts fixed per pattern) reduces to lookaround context, i.e. the checker
product (C3); inside an alternation it needs one capture's tracking (VM today). [ENGINE-WHY] reason
text: "group 0 inside an alternation needs capture tracking; use one top-level group 0 to keep the
DFA". It CONSUMES its outside context (find-all resumes after the whole match, as with `\K`),
unlike lookaround.

## Evidence

- `docs/dev/lanes/condsurv_evidence/engine_probe.txt` — 28 patterns, engine or refusal, MEASURED.
- `docs/dev/pcre2_notes/script-run-evaluation.md`, `docs/dev/pcre2_notes/dfa-matcher-conditions.md`
  — new reader notes (checker passed).
- `docs/dev/lanes/condinv_report.md` and its evidence (PCRE2 semantics of every condition kind).
- `docs/design/plan_row_bodies/POSTFACT.md`, `docs/design/span_arms.md` §2 §5 §7 §8,
  `docs/design/stream/arev.md`, `docs/design/vlookbehind.md`.
