# condinv report: what it would take to support PCRE2's conditional groups

Lane condinv (opus), 2026-11-05. INVESTIGATION ONLY: no design note, no build,
nothing under `src/` `cli/` `lib/` `memfn/src/` `tests/` touched. Branch
`lane/condinv` from main `6c6e68086`. Plan row [CONDITIONALS] (PCRE2 gap rank 2).
PCRE2 side: the installed libpcre2 10.46 used as a LIBRARY (`condinv_evidence/probe.c`,
options 0) plus the public pcre2pattern semantics; the pinned PCRE2 source copy
was not opened (D181). Rulings file `condinv_rulings.md`: empty at every read
(no entry applied).

STATE: delivered (investigation complete; no runs owed).

## For the owner, in plain words

1. Nothing is half-built: every condition kind except `(?(DEFINE)` is refused
   cleanly today ("module 'conditionals' is enabled but (?(...) is not
   implemented yet"). DEFINE already ships, as part of the recursion module.
2. There is NO real demand in our data. The 5 "corpus patterns" the scoreboard
   counted are all pcrec's OWN refusal tests (4 in `tests/recursion/refused.rxt`,
   1 excluded cell in `tests/compound/split.rxt`). The bench has exactly one: a
   syntax probe `(<)?item(?(1)>)`. Wild and realistic patterns: zero.
3. Most of the machinery already exists. "Was group N set" is the same test a
   backreference already makes before comparing; an assertion condition is the
   lookaround we already have, with a second exit; DEFINE already shows how the
   `(?(` doorway parses a body and counts its branches.
4. The general form is one new tree node: "test a condition, then run the yes
   arm or the no arm". Four kinds of test fit in it (group set, assertion,
   "are we inside a subroutine call", a compile-time constant). Seen this way a
   plain lookaround is a conditional whose no-arm fails, and a negative
   assertion condition is a positive one with the arms swapped.
5. All of it runs on the backtracking VM. The DFA cannot host it today. A
   group-set test could in principle go into the DFA (one extra bit per tested
   group), but nothing here argues for building that.
6. Size: group-set conditions (numbered, relative, named) medium; assertion
   conditions small on top of that; recursion conditions `(?(R)` medium and
   only useful with recursive patterns; `(?(VERSION>=..)` is a one-line
   constant but is ruled out of scope.
7. Recommended first slice, if you want one: the new node with group-set and
   assertion conditions, `(?(R...)` parsed but still refused. Leaning: do not
   schedule it ahead of variable-width lookbehind (rank 1), given zero demand.

Measured vs inferred: every PCRE2 behaviour below is MEASURED (164 libpcre2
cases, `condinv_evidence/semantics_pcre2.tsv`); pcrec's refusals are MEASURED
(`premise_pcrec.txt`); the population is MEASURED (`population.tsv`). Engine
placement, reuse claims and sizes are INFERRED from reading the code and are
marked so.

## 0. Premise test and stop rule

| pattern | build/pcrec --features all | libpcre2 10.46 |
|---|---|---|
| `(a)?(?(1)b\|c)` | refused, rc=1: "module 'conditionals' is enabled but (?(...) is not implemented yet (pattern offset 4)" | compiles; "ab" -> (0,2) g1=(0,1); "c" -> (0,1); "b" -> no match |
| `(?(?=a)ab\|cd)` | refused, rc=1, same message, offset 0 | compiles; "ab" (0,2), "cd" (0,2), "ad" no match |

STOP RULE: no condition kind the scoreboard called refused is supported. All
17 spellings in `premise_pcrec.txt` (number, `+1`, `-1`, `<n>`, `'n'`, bare `n`,
`R`, `R1`, `R&g`, the four assertions, `*pla:`, VERSION, three arms, a missing
group) refuse with the same message. Only `(?(DEFINE)` compiles (module
`recursion`, D71 item 4), as the scoreboard already said.

One disagreement found (recorded, not resolved): `docs/pcre2_compliance.md`
"Conditional patterns" marks `(?(VERSION>=n.m)` `OUT-OF-SCOPE`, and the scoreboard
lists it under row 18 "refused: out of scope", but the compiler says "module
'conditionals' is enabled but ... not implemented yet", i.e. promises it. A
D26-tier wording fix belongs to whoever builds the module (a `VERSION` tail row
with the out-of-scope diagnostic, the way DEFINE has its own tail row).

## 1. PCRE2 10.46 semantics, by condition kind (all MEASURED)

Evidence: `condinv_evidence/semantics_cases.tsv` (input),
`semantics_pcre2.tsv` (output). Cells quoted as pattern / subject -> result.

### K1 group-set, absolute number `(?(N)yes|no)`
- True iff group N is SET at that moment. `^(a)?(?(1)b|c)$`: "ab" match, "c"
  match, "b" no match.
- SET INCLUDES SET-TO-EMPTY: `^(a*)(?(1)x|y)$` / "y" -> no match, "x" -> (0,1)
  g1=(0,0). This is exactly the backreference rule (backrefs_design.md §8.3).
- Missing no-arm = empty: `^(a)?(?(1)b)c$` / "c" match, "ac" no match.
- Three arms refused: `(a)(?(1)x|y|z)` -> error 127 "conditional subpattern
  contains more than two branches" @3. An alternation INSIDE a grouped arm is fine.
- Forward numbers are legal if the group exists anywhere: `(?(1)a|b)(x)` accepted,
  and the condition is false there (`^(?(1)a|b)(x)$` / "bx" match). A number
  beyond the group count: error 115 "reference to non-existent subpattern"
  (`(?(1)a|b)`, `(?(0)a|b)`, and `(?(2)..)` with one group). `(?(01)` is accepted.
- `(?()a|b)` -> error 162.
- Group set in an EARLIER iteration stays set: `^(?:(a)|x)+(?(1)y|z)$` / "axy"
  match; `^(?:(a)|b(?(1)c|d))+$` / "bdabc" match, "abd" no match.
- A condition inside its OWN group reads the previous published value:
  `^(a(?(1)b|c))$` / "ac" match, "ab" no match; `^(?:(a(?(1)b|c)))+$` / "acab" match.
  This is publish-at-close, which pcrec's VM already does for backreferences.
- A capture written inside a called group is restored after the call:
  `^(?1)(?(1)y|z)(a)$` / "aza" match, "aya" no match.
- Captures inside a negative lookahead are not set afterwards:
  `^(?!(a)b)(?(1)x|a)` / "ac" -> (0,1) g1 unset.
- Backtracking re-decides the condition with the restored state:
  `^(a+)?(?(1)ab|b)$` / "aab" -> (0,3) g1=(0,1).

### K2 relative `(?(+N)` `(?(-N)`
- Resolved to an absolute number at parse time: `^(?(+1)a|b)(x)$` / "bx" match;
  `(a)(?(-1)b|c)` / "ab" match; `(?(-1)a|b)(a)` -> error 115 (no group before it).

### K3 named `(?(<n>)` `(?('n')` `(?(n)`
- All three spellings agree with the numbered form (`semantics_pcre2.tsv`
  lines for `^(?<n>a)?(?(..)b|c)$`). A forward name is legal: `^(?(n)a|b)(?<n>c)$`.
- An unknown name is error 115, including the lowercase `(?(define)` and the
  prefix `(?(DEF)` (both in pcrec's `tests/recursion/define.rxt` as refusals).
- DUPLICATE NAMES (`(?J)`): true iff ANY member is set. `(?J)(?:(?<n>a)|(?<n>b)|x)(?(<n>)c|d)`:
  "ac" and "bc" match (g2 set, g1 unset in "bc"), "xd" match, "xc" no match.
  This is the backreference's "first member that is set" walk without the compare.
- NAME BEATS RECURSION: a group NAMED `R` or `R1` turns `(?(R)`/`(?(R1)` into a
  group test, even when declared later: `^(?:(?(R)b|c)(?<R>a))+$` / "caba" match,
  "caca" no match; `^(x)?(?<R1>a)?(?(R1)b|c)$` / "ab" match reading group 2 (named R1),
  not group 1. So the kind of `(?(name)` is decided only once the whole pattern
  is parsed (registry.c's header comment already warns about this).

### K4 recursion `(?(R)` `(?(Rn)` `(?(R&name)`
- `(?(R)`: true iff executing inside ANY subroutine call, recursive or not:
  `^(a(?(R)b|c))(?1)$` / "acab" match, "acac" no match; `(?(R)a|b)` at top level is
  false ("b" matches). Nested: `^(a(?1)?(?(R)b|c))$` / "aabc", "aaabbc" match.
- `(?(Rn)` and `(?(R&name)`: true iff the MOST RECENT call was into group n
  (not "any call on the stack"): `^(?1)(?(DEFINE)(a(?2))((?(R1)x|y)))$` / "ay"
  match, "ax" no match, while `(?(R)` in the same place is true ("ax" match).
  `^(a(?2))((?(R1)x|y)(?(R2)p|q))$` / "aypyq" match.
- `(?(R1)a|b)(x)` accepted; `(?(R2)..)` with one group -> 115; `(?(R&g)` with
  no group g -> 115; with duplicate-name groups accepted.

### K5 assertion conditions `(?(?=..)` `(?(?!..)` `(?(?<=..)` `(?(?<!..)`
- `^(?(?=a)ab|cd)$`, `^(?(?!a)cd|ab)$`, `^x(?(?<=x)y|z)$`, `^x(?(?<!x)y|z)$` behave as read.
- The assertion is ATOMIC and evaluated once: `^(?(?=(a+))\1a|x)$` / "aaa" no
  match (a non-atomic body would retry `a+` as "aa"). Non-atomic assertions are
  refused as conditions: `(?(?*a)` and `(?(*napla:a)` -> error 128 "atomic
  assertion expected after (?( or (?(?C)"; the alphabetic atomic spellings
  `(*pla:` `(*nla:` `(*plb:` `(*positive_lookahead:` are accepted.
- Captures from a POSITIVE condition carry into the yes arm:
  `^(?(?=(a))a\1|b)$` / "aa" match g1=(0,1).
- Captures from a NEGATIVE condition that FAILED carry into the no arm:
  `^(?(?!(a))b|a)$` / "a" -> g1=(0,1). So `(?(?!A)Y|N)` behaves exactly as
  `(?(?=A)N|Y)`.
- A callout may precede the assertion: `(?(?C1)(?=a)a|b)` accepted; before
  anything else error 128 (`(?(?C1)(1)a|b)`).
- A lookbehind condition follows lookbehind's own rules: `(?(?<=a|bb)` fine,
  `(?(?<=a+)` error 125.

### K6 `(?(VERSION>=x.y)` and `(?(DEFINE)`
- VERSION is a compile-time constant against the library's version:
  `(?(VERSION>=99.0)a|b)` matches "b"; `=` and `>=` only (`>` error 179).
- DEFINE: compiles and never runs its body; a second branch is error 154. pcrec ships it.

### K7 interactions
- Quantified conditionals compile, possessive included: `(?(1)a|b)++(x)`;
  `^(a)?(?(1)b+|c)++b$` / "abb" no match (possessive), match without `++`.
- Inside lookaround: `^(a)?(?!(?(1)b|c))..$` behaves; inside a LOOKBEHIND with
  unequal arms `(?<=(?(1)a|bc))x(a)` is ACCEPTED (10.46's variable-length
  lookbehind), equal arms `^(a)?b(?<=(?(1)ab|bb))c$` work.
- An empty-matching arm under `*` terminates: `^(?:(?(1)|a)(b)?)*c$`.
- `\K` inside an arm works: `^(?(?=a)a\Kb|c)$` / "ab" -> (1,2).

## 2. pcrec today (code read; INFERRED unless a probe is cited)

- **The refusal.** One registry row, `src/parse/registry.c` `GROUP('(', "(?(1)a|b)",
  conditionals, VM_ONLY, ...)`, module `conditionals`, `FEAT_CONDITIONALS`
  (`src/core/internal.h`), roadmap planned, QF_NO. With no port wired, the
  generic unbuilt path in `src/parse/ext.c` (the `UNBUILT` macro) raises
  "is not implemented yet". DEFINE is the tailed row (tail `DEFINE)`) right
  below it, wired to `mod_recursion.c`'s DEFINE port. `compliance` index:
  `REJECTED / unbuilt / planned / conditionals / vm`.
- **Parsing an arm pair already exists.** The DEFINE port (`src/parse/mod_recursion.c`,
  the port that refuses "DEFINE subpattern contains more than one branch") saves
  scoped options, calls `pcrec_parse_body(cx, &info)` and refuses on
  `info.nbr > 1`. A conditionals port is the same shape with `nbr > 2` (error
  127 at `at + 3`, MEASURED offset) and the top-level `A_ALT` split into yes/no.
- **Resolving numbers and names already exists, at end of parse.**
  `pcrec_bref_resolve` (`src/parse/mod_backrefs.c`) settles every `PendingRef`
  (backreferences AND calls, "one resolver, two rules") after the whole pattern
  is read, which is what makes forward references legal. A condition is a THIRD
  rule on the same resolver: number/relative/name -> the SET of group numbers
  (the dup-name run, as `A_BREF.u.bref.refs[]`), and the K3 name-beats-recursion
  rule (a name that is not a group and spells `R`, `Rn`, `R&name` becomes a
  recursion test; otherwise 115). This is the "whole-pattern group-name table"
  registry.c's header says conditionals will need; the resolver already is one.
- **The group-set test already exists, in the VM.** `vm_bref`
  (`src/gen/emit_vm.c`) tests the published START slot against `PCREC_UNSET`,
  walks the dup-name run in ascending number, and only then calls the compare.
  "Set" there includes set-to-empty and is total because of publish-at-close and
  the trail (same function's header). A group-set condition is that test with
  two exits and no compare, and no choice point (a plain if/else, no frame).
- **The assertion half already exists.** `vm_look` (`src/gen/emit_vm.c`)
  emits the atomic lookaround with a saved cursor, a cut, and for the negative
  form a pushed "body-failed" continuation. An assertion condition is the
  positive form whose body-failed continuation goes to the NO arm instead of
  failing, and whose success goes to the YES arm with the captures kept
  (exactly K5's measured capture rule); the negative condition is the same with
  the arms swapped. Lookbehind conditions reuse `vm_look_behind` unchanged.
- **The recursion state does NOT exist as a value.** The call linkage (`A_CALL`,
  `u.call.save/nsave/link`, `vm_call`/`vm_splice`) saves and restores captures
  around a call on the trail, but nothing records "which group was most recently
  called". `(?(Rn)` needs one more slot written on call entry and restored on
  return through the same trailed save; `(?(R)` is "that slot is not the
  top-level value". Under `CALL_SPLICE` the answer is a compile-time constant
  in each spliced copy that is not reached by a non-spliced call.
- **Marking.** `pcrec_bref_mark` (`src/opt/atomic.c`) marks referenced and
  called groups so `--no-captures` keeps their `A_CAP`. A condition's groups
  must join that set, or `--no-captures` deletes group 1 out from under
  `(a)?(?(1)b|c)` and the condition is always false: a silent miscompile,
  sabotage-row material.
- **Callouts.** `src/opt/callout.c`'s header says its "Row 2 (a conditional's
  condition) cannot arise" because module `conditionals` has no producer. The
  `(?(?C1)(?=a)..)` form would make it arise; the first slice should keep it refused.
- **Engine selection and prefilter.** `src/opt/select_engine.c` declines a
  prefilter for brefs/calls/vars (`has_bref`/`has_call`/`has_var`), and
  `src/ir/nfa.c` lowers a lookaround to an epsilon (a sound superset, with the
  MRL span-end ceiling dropped). A conditional could lower in `nfa.c` to the
  alternation `yes|no` (with the assertion erased as lookaround already is):
  every match takes one arm, so it is a superset at every start position,
  sound for rejection and span start, not exact for span end (same caveat as
  lookaround). INFERRED; it would need its own control in the build.
- **Cost of a new tree kind.** `case A_LOOK` appears 73 times in 26 files under
  `src/`; that is the order of switch sites a new kind would meet (lookaround's
  own enumerator budget was 23 `-Wswitch` sites when it was added).

### Which engine can host which kind (INFERRED)

| kind | pcrec DFA today | could the DFA ever? | VM |
|---|---|---|---|
| group-set (number, relative, name, dup-name) | no: pcrec's DFA is a determinized table with no capture side channel (registry.c header) | in principle yes: "is group N set" is one bit per tested group along the path, so a product construction (states x 2^k) keeps it regular under leftmost-first; NOT [ENG-TDFA]'s position tags, a cheaper bit; unbuilt, no row | yes (if/else on a slot) |
| assertion | no | only through [ENG-LOOK]'s product construction (chartered, not built) | yes (`vm_look` with a second exit) |
| recursion `(?(R)` `(?(Rn)` | no (calls are VM-only) | no: meaningful only inside calls, which are not regular | yes (one trailed call-context slot); compile-time false when no call reaches it |
| VERSION, DEFINE | yes (constant) | yes | yes |

Inside a call or a lookaround the capture-restore rules are the VM's anyway.

## 3. Approaches and the general form

**The general form (recommended).** One AST kind, call it `A_COND`: `l` = yes
arm, `r` = no arm (A_EMPTY when missing), payload = a PREDICATE:

| predicate | test | where it is evaluated | existing mechanism reused |
|---|---|---|---|
| SET(refs[]) | any listed slot is set | VM if/else, no frame | `vm_bref`'s unset test and dup-name walk; `pcrec_bref_resolve`; `pcrec_bref_mark` |
| LOOK(child) | an atomic lookaround body | VM, `vm_look` with two exits | `vm_look`, `vm_look_behind`; negative = arms swapped |
| CALLCTX(any / group n) | most recent call target | VM if/else on one trailed slot | `vm_call`'s trailed save; constant under splice or with no calls |
| CONST(bool) | known at compile time | folded away before any engine | DEFINE already does this as `{0}`; VERSION would be one |

Why one kind: D62 (kinds encode structure, fields encode parse-resolved
state); every kind shares the structure "test, then one of two arms", and
every analysis needs the same answer for all four (width = min/max over the
arms, nullable = either arm, first-set = union, the nfa.c superset =
`yes|no`). Seen this way lookaround and the backreference's unset test are
degenerate conditionals (no-arm = fail); folding them INTO `A_COND` is not
proposed (both are shipped and tuned), but the shared helper ("emit the slot
test", "emit the lookaround with a success exit and a failure exit") should be
factored so `vm_bref`/`vm_look` and the condition share one copy rather than
gaining a parallel one. Frank's "general mechanisms, not special cases" points
here.

**Alternative for assertion conditions only: desugar, no new kind.**
`(?(?=A)Y|N)` == `(?:(?=A)Y|(?!A)N)`, and `(?(?!A)Y|N)` == `(?:(?!A)Y|(?=A)N)`.
INFERRED answer-identical (the alternation rewinds captures, so the second
evaluation of A sees the same state and gives the opposite verdict; the
retained-captures cell `^(?(?!(a))b|a)$` comes out right because `(?=A)` keeps
its captures). Costs: A is evaluated twice on the no path (the VM's work
budget charge doubles, which can move a limit verdict), and a callout inside A would fire twice
(observable). Reasonable as implement-then-replace, not as the end state.

**Alternative for group-set: an ALT of two zero-width tests.**
`(?:SET(1) Y | UNSET(1) N)`: exact, but pushes a choice point the if/else does
not need, and still needs a new zero-width atom kind. No better than `A_COND`.

## 4. The population

`condinv_evidence/population.tsv`. All MEASURED by grep and the scoreboard's
compile logs.

| source | patterns | kinds | what they are |
|---|---|---|---|
| pcrec corpus (6,304) | 5 | group-set x3, `(?(R)` x1, positive lookahead x1 | ALL pcrec's own refusal pins: `tests/recursion/refused.rxt` lines 45/50/55/60 (perr), `tests/compound/split.rxt` 10572 `(?(?=^)a\|ab)c` (`# pcre2-only`, perr). When the module lands these flip from refusal to expectation (re-pin work, not demand). |
| bench (392 .rx) | 1 | group-set | `bench/syntax/patterns/cnd-group.rx` = `(<)?item(?(1)>)`, a syntax probe of the optional-matching-bracket idiom |
| bench wild (32) / realistic (40) | 0 | - | `wild-json-validate` uses `(?(DEFINE)` (built) |
| real-world harvest | none exists | - | [UTF-RW] not-started |

`tests/recursion/define.rxt`'s `(?(define)..)` and `(?(DEF)..)` are NAME
conditions that libpcre2 also rejects (115); not demand.

## 5. Risks, tests, overlap

**Answer identity** (each is a measured PCRE2 rule a builder can get wrong):
set-to-empty is set; dup-name is "any set"; name beats `R`/`Rn` even when declared
later; `(?(Rn)` is most-recent-call, `(?(R)` is any call; negative-condition
captures survive into the no arm; the assertion is atomic; a condition in its
own group reads the previous iteration; a forward condition is legal and false.
`--no-captures` must keep conditioned groups (mark). Every analysis that walks
the tree (possessify, start sets, literal runs, minimum width, the nfa.c superset)
must take BOTH arms; one that reads only the yes arm is a miscompile no
compiler diagnostic catches (the D62 control-3 shape, three sabotage rows the
way lookaround and calls got them).

**Engine selection.** Registry row stays `VM_ONLY`; every conditional pattern
goes to the VM, including the bench probe. A pattern whose only condition is a
CONST fold keeps its engine choice (DEFINE's precedent).

**Size.** One if/else per group-set or recursion condition; a lookaround's code
per assertion condition. No size risk found (INFERRED).

**Test plan sketch.** Oracle = libpcre2 differential: this lane's 164 cases are
the seed (`semantics_cases.tsv`, every cell with its measured answer), promoted
to a `tests/conditionals/` corpus; PC-3 picks up the registry rows; the four
refused.rxt cells and the split.rxt cell re-pinned; sabotage rows for the mark,
both-arms analyses and the swapped-arm negative. **Recommend a D27 spec-first
author: yes**, for the group-set and assertion slice. The rules in K1/K3/K5
are exactly the kind a code-derived test inherits from its author (the
dup-name and name-beats-R rules surprised this lane's own first probe round:
three of its cases were mis-designed and had to be re-cut), and D27 found a
tier-1 miscompile the last time.

**Overlap with in-flight work.**
- [VLOOKBEHIND] (rank 1, lane vlbinv): a conditional with unequal arms inside a
  lookbehind (`(?<=(?(1)a|bc))`, accepted by 10.46) needs variable-width
  lookbehind; equal arms do not. Build order: either; the combined case waits
  for both.
- `docs/design/alt_normal_form.md` ([RUN-POS-SET], rev 0): its normal form
  merges capture-free fixed-width literal alternation branches. An `A_COND` is
  not an alternation and must not be merged as one (moving the condition past a
  shared prefix moves an assertion's position). Reading it as `yes|no` for a
  "required in both arms" fact is sound. Low overlap; one line in its reader
  audit when either lands.
- span_pick (kit): no overlap found. Conditional patterns are VM-only and,
  with the nfa.c superset, would feed ordinary prefilter span sites; no new
  search-site shape.
- [ENG-LOOK] / [ENG-TDFA]: only if a DFA conditional were ever wanted (table above).

## 6. Sizes, first slice, questions

| kind | size (INFERRED) | depends on |
|---|---|---|
| `A_COND` node + parser port + resolver rule + VM if/else + all-walker arms + marks (group-set: number, relative, name, dup-name) | medium | nothing new |
| assertion conditions on that node | small | `vm_look` refactor to two exits |
| recursion conditions `(?(R)` `(?(Rn)` `(?(R&n)` | medium | one trailed call-context slot; splice folding optional |
| `(?(VERSION..)` | tiny (constant fold) | Frank's out-of-scope ruling stands |
| DFA hosting of group-set conditions | large | a new nfa.c product; no row, not recommended |

**Recommended first slice** (if Frank opens a design lane): `A_COND` with SET
and LOOK predicates, all spellings of both parsed, `(?(R..)` PARSED and
resolved (the name-beats-R rule must live in the resolver from day one, or a
later slice changes the meaning of a pattern that compiled) but refused with a
"recursion condition is not implemented yet" message; callout-before-assertion
refused; VERSION given its own out-of-scope diagnostic. That proves the node is
general (two predicates through one mechanism) and flips 4 of the 5 corpus pins
and the bench probe.

**Questions for Frank, in plain words**
1. With no outside demand at all (one bench syntax probe, zero real patterns),
   do you want conditionals designed now, or parked behind variable-width
   lookbehind? Leaning: park until lookbehind's design is settled; the module
   is well-understood and will not get harder.
2. If designed: one general "condition" node (lookaround and backreference
   tests share its helpers), or the cheaper rewrite of assertion conditions into
   an alternation of two lookarounds first? Leaning: the general node; the
   rewrite double-runs the assertion and double-fires callouts.
3. Should the first slice include recursion conditions `(?(R)`? They only
   matter for recursive grammar patterns (JSON-validator style), of which our
   bench has a few that use DEFINE but none that use `(?(R)`. Leaning: no, but
   parse and resolve them from day one.
4. `(?(VERSION>=..)` is ruled out of scope, yet today's message says "not
   implemented yet". Fine to give it the out-of-scope message when the module
   is built (not before)? Leaning: yes, at build time.

**Named question for a pcre2-reader (none needed for this report).** Every fact
above was settled by the library. If the design lane needs it: "In PCRE2 10.46,
when `(?(Rn)` is evaluated inside a group entered by ordinary (non-call)
matching that is itself nested inside a call to group m, is 'most recent
recursion' m (the innermost call frame) in every case, including after a
call has returned and its caller continues?"

## Evidence

- `condinv_evidence/probe.c` — libpcre2 probe driver (build line in its header).
- `condinv_evidence/semantics_cases.tsv` / `semantics_pcre2.tsv` — 164 cases, 3 rounds.
- `condinv_evidence/premise_pcrec.txt` — pcrec's answer for 18 condition spellings, `--features all` and default.
- `condinv_evidence/population.tsv` — every conditional in corpus, bench, wild, realistic.
- Scoreboard raw data read: `$PCREC_TMPDIR/scratch/scoreboard/corpus_compile.tsv`, `bench_compile*.tsv`, `p2_*.tsv` (not copied).
