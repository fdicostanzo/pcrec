# lookaround (module `lookaround`, [M6.6]): architecture note (RETRO TEST, written 2026-11-17)

RETRO: written by lane archroles for [ARCH-STEP] unit A6's first half, from the tree AS IT WAS before the lookaround
design began, with the `pcrec-architect` template (first draft, commit 469221e92). Only facts readable at `T` are
used; nothing below was checked out (every command is `git grep <T>` / `git show <T>:path`). The verdict on what
this note caught and missed is in `docs/dev/lanes/archroles_report.md`, THE RETRO TEST, not here.

STATUS: DRAFT (retro; never reviewed)
FORM: full (trigger, PROPOSED: 7 existing decision sites touched, see the site map; mechanisms added: a new AST kind
with a variable-length payload, a new encoding-seam entry, a new VM sub-match shape)
TREE: T = 74947afd8 (2026-08-23 13:44, main just before docs/design/lookaround_design.md's first commit 33ca65562)
REQUIREMENTS: `docs/dev/plan.md` rows [M6.6] and [M6.6.1] items (i)-(ix) @T; D58 (encoding seam), D62 (node kinds
vs node fields), D66 (the DD-11 lookbehind-anchor core form) in `docs/dev/decisions.md` @T; APPROACH.md @T.
REGISTER READ: none existed at T (part 3 of architecture.md is 2026-11-17). The lookup below is done against the
equivalent records at T: D-row "Revisit when" triggers and the plan rows that name a deferred remodel.

## Goals served
Goal 1 (one home per question): the feature asks three questions the tree already answers (subtree width, "does
the pattern contain kind K", "what is true of the characters around this position"). Goal 4 (a shape covers the
planned inputs): the feature is the fourth kind with a private payload on a struct that has no per-kind payload.
Goal 2 (a new choice is a row): the prefilter decision for a pattern holding lookaround joins a hand chain. Goal 3
(seams): a new encoding-seam entry (D58) and a parse-tier width check that today could only call into `src/opt`.

## Requirements read
[M6.6.1] (i) construct table incl. the lookbehind length rule (fixed length PER ALTERNATIVE), (ii) VM lowering as an
atomic sub-match on the RX_CUT substrate, (iii) the back-step as the encoding seam's THIRD residual entry, (iv)
engine selection VM_ONLY plus a DFA-eligible one-character subset and the prefilter-soundness argument (erasing a
lookaround gives a superset; NEGATIVE lookaround inverts it), (v) the D66 hand-off: `(?m)^` = `\A|(?<=\n)(?!\z)`.
VOCABULARY: `A_` kinds; `struct Ast` fields; `pcrec_minw`; `pcrec_has_*`; `fit.prefilter`, `force_on`; `VM_ONLY`,
`Ast.reg`; `PcrecEncEntry`, `PCREC_ENCE_`; `vm_cut`, `vm_atomic`; `N_BOT`..`N_GSTART` (the NFA context nodes);
`multiline`. REQ-OPEN: (i)'s variable-length lookbehind ruling (`max_varlookbehind`) changes the width question
from "fixed per branch" to "bounded"; the sites below hold for both.

## Site map
| # | site | command (at T) | today | class | goal/rule |
|---|---|---|---|---|---|
| 1 | `struct Ast` (src/core/internal.h) | `git show T:src/core/internal.h \| grep -n -A40 '^struct Ast {'` | one struct; per-kind fields at top level: `cls[32]` (A_CLASS), `rmin/rmax/greedy/possessive/revbody` (A_REP), `capno` (A_CAP), `multiline` (A_BOL/A_EOL), `refs/nrefs/caseless` (A_BREF). Every node carries every kind's fields. The feature adds a fifth payload (direction, polarity, atomicity, a per-branch width ARRAY and its count) | WIDEN | goal 4; rule "A shape states the inputs it covers" |
| 2 | generic writers and copiers of `Ast` | `git grep -n -E '(->\|\.)(possessive\|revbody)\s*=[^=]' T -- src`; `git grep -n 'sizeof(Ast)\|\*n = \*src' T -- src` | `rd_node` (src/opt/revdet.c:207-214) copies a node of ANY kind with `*n = *src` and then writes `revbody = NULL; possessive = false` without testing the kind; `parse.c:38` allocates the one size | WIDEN (hazard list for unit R1) | goal 4 |
| 3 | kind switches | `git grep -c 'case A_' T -- 'src/*.c'` (230 labels, 10 files; emit_vm.c 61, possessify.c 37, revdet.c 36, atomic.c 31) and `git grep -c 'default:' T -- <each>` | exhaustive switches with no `default:` in nfa.c, altcls.c, mrl.c, possessify.c (the compile alarm D62 relies on); `default:` arms in emit_vm.c x4, revdet.c x2, atomic.c x2, select_engine.c x2 | AS-IS for the kind itself (the `-Wswitch` net reports every exhaustive site); the `default:` sites are each a read-the-code item for the design step | rule "A new AST kind states its cost" |
| 4 | subtree width | `git grep -n 'pcrec_minw\|vm_fadd' T -- src` | ONE width function, `pcrec_minw` (src/opt/mrl.c:85, saturating), called from emit_vm.c x5; emit_vm.c also spells its own saturating add `vm_fadd`. No maximum-width answer exists. Lookbehind's length rule needs the max (= min) width of each branch, AT PARSE TIME (the refusal is the parser's) | SHARED (min and max width in one home) + layering: `src/CLAUDE.md` @T orders parse before opt, so a parse-tier caller of `src/opt/mrl.c` is a wrong-way call | goal 1, goal 3; rules "One question, one primitive", "Layering holds at the call level" |
| 5 | "does the pattern contain kind K" | `git grep -n -E '^bool pcrec_has_\w+' T -- src` | two whole-tree walks, `pcrec_has_atomic` (atomic.c:37) and `pcrec_has_bref` (atomic.c:295), 27 call/reference hits (`git grep -n -E 'has_(bref\|atomic\|kreset\|gstart)\b' T -- src \| wc -l`). The feature needs a third (prefilter soundness, the MRL ceiling) | SHARED (one "kinds present" fact computed once per compile, read by every consumer) | goal 1; rule "Notice siblings" (third member) |
| 6 | the prefilter decision | `git show T:src/opt/select_engine.c \| sed -n 520,556p` | a refusal chain (`if (force_on && has_bref) ctx_fail`, `force_on && force_off`, `force_on && fit.chosen != ENGM_VM`) then a ternary `fit.prefilter = has_bref ? false : force_on ? true : force_off ? false : ...`. Negative lookaround makes the erased prefilter UNSOUND (requirement (iv)), so the feature adds an arm to both | CHAIN->TABLE (prefilter admission rows + refusal rows) | goal 2; rules "Decisions are declared tables", "Refusals are a decision family" |
| 7 | encoding seam | `git show T:src/gen/enc/enc_byte.c \| grep -n PCREC_ENCE_` | a declared table `entries_byte[]` of `PcrecEncEntry` (NEXT_POS, BREF, BREF_CASELESS) | ROW (the back-step is a fourth row; [M6.6.1] (iii) says "third residual entry"; INFERRED: it counts BREF_CASELESS with BREF) | goal 2, goal 3 |
| 8 | engine selection | `git grep -n 'VM_ONLY' T -- src/parse/registry.c src/opt/select_engine.c` | registry rows stamp VM_ONLY through `Ast.reg`; select_engine.c reads the stamp generically (its own header, :116-134) | ROW (four GROUP rows already exist at registry.c:580-600 with module `lookaround`) | goal 2 |
| 9 | VM sub-match | `git grep -n 'static void vm_cut\|static void vm_atomic' T -- src/gen/emit_vm.c` | `vm_cut` (:2119) and `vm_atomic` (:4242) implement the atomic sub-match the requirements reuse | AS-IS (reuse; the design step decides the shape) | rule "Build the general form" |
| 10 | context assertions | `git grep -n -E 'case A_(BOL\|EOL\|WORDB\|NWORDB\|GSTART)' T -- src/ir/nfa.c`; `git grep -c -E '\bN_(BOT\|BOT_M\|EOL\|EOL_M\|WORDB\|NWORDB\|GSTART)\b' T -- src` | six NFA node kinds, one per flavour (`N_BOT`, `N_BOT_M`, `N_EOL`, `N_EOL_M`, `N_WORDB`, `N_NWORDB`) plus `N_GSTART`; the AST spells `(?m)` as the `multiline` FIELD (D62) and the NFA re-splits it into kinds. Requirement (iv)'s one-character lookarounds (`(?<=\n)`, `(?<!\w)`, `(?=\w)`) are the same question: a predicate on the character before and after a position | CHAIN->TABLE: one context-predicate table (before-class x after-class), each assertion a row; the one-character lookaround recognizer adds rows | goal 1, goal 2; rule "Notice siblings" (seven members) |
| 11 | captures inside lookaround | `git grep -n 'capno' T -- src/gen/emit_vm.c \| wc -l` | captures are slot writes restored by the trail | AS-IS (requirements (ii); design decides) | - |

Hit counts at T: 230 `case A_` labels in 10 .c files; field-read hits (`git grep -c -E '(->\|\.)FIELD\b' T -- src`,
comments included): cls 39, rmin 61, rmax 55, capno 22, greedy 34, multiline 37, possessive 37, revbody 11, refs 5,
nrefs 6, caseless 17. Checks that bind those spellings: `git grep -l -E '(->\|\.)(cls\|rmin\|rmax\|capno\|multiline\|possessive\|revbody\|caseless\|refs)\b' T -- tests/mech \| wc -l` = 13 sabotage files.

## Register rows looked up
No register at T. The equivalent records:
- D62 "Revisit when" (decisions.md @T, D62's own text): "Bounded: AST-walking analyses are rare (four today)" and
  the accepted residual "a FUTURE analysis's author must read the field comment". The feature adds a kind, a payload
  and at least two walks (sites 4-5): the trigger is met. RIDES FIRST as unit R1.
- [M6.0] POST-MODULE QUEUE / D66: the core lookbehind-anchor form is "sequenced behind [M6.6] lookaround + the DD-11
  design". Site 10's table is that form's home. NOT CARRIED by this feature (the requirements hand it to [DD-11]);
  PROPOSED register row below so the trigger is written where a planner looks.
PROPOSED rows (register columns):
| remodel | shape (rule) | where | event | size, gate | deletes |
|---|---|---|---|---|---|
| Context predicates as one table | Decisions are declared tables; Notice siblings | `N_BOT`..`N_GSTART` in src/ir/nfa.c, src/ir/dfa.c, `multiline` on Ast | [DD-11]'s design, or the first one-character lookaround recognizer | M, abi (artifacts move) | six flavour kinds, the AST `multiline` field |
| Width library below parse | One question, one primitive; Layering | `pcrec_minw` mrl.c:85, `vm_fadd` emit_vm.c, the new max width | this feature (unit R2) or the next parse-tier width question | S, no-mover | the opt-tier home, the sat twin |
| Kinds-present fact | One question, one primitive | `pcrec_has_atomic`, `pcrec_has_bref` (atomic.c) | this feature (unit R3) | S, no-mover | two walks |

## Remodels that land first
- R1 `Ast` payload per kind (site 1-2). What changes: the per-kind fields move into one payload per kind (the
  layout is the design step's); common fields stay. GATE: no-mover, byte identity of every artifact over the corpus
  on every axis, against a pinned pre-unit SHA. SIZE: M (230 switch labels unchanged; about 320 field-read hits (324 by the counts below)
  respelled; 13 sabotage files re-anchored in the same unit). SEPARABLE: yes, it lands before any lookaround code
  and the feature then adds one payload. HAZARD the unit must close: every generic writer of a per-kind field
  (site 2: `rd_node` writes REP-only fields on every kind) becomes a write into ANOTHER kind's bytes once payloads
  share storage; each gets a kind guard. SPEED: emitted bytes identical, so no cell moves; compiler memory only.
  DELETES: the dead per-kind fields on every node.
- R2 width library (site 4). The max-width answer is added beside `pcrec_minw` in ONE home callable from parse;
  `vm_fadd` joins it. GATE: no-mover. SIZE: S. SEPARABLE: yes (pure move plus the existing callers). Without it the
  lookbehind check either re-walks widths in the parser (a second width mechanism) or calls src/opt from parse (a
  wrong-way call). DELETES: the saturating twin.
- R3 kinds-present fact (site 5). GATE: no-mover. SIZE: S. SEPARABLE: yes. DELETES: two walks.
- Site 6 (prefilter chain): NOT a first unit: the feature adds one arm, a third member of the refusal family
  (`has_bref`, `force_off`, engine); at three, rule "Notice siblings" says PROPOSE the table: a register row
  "prefilter admission and refusals as rows" with trigger "the next prefilter-soundness kind".

## The general form and its siblings
- The general form of lookaround is a sub-match at a position that leaves the position unchanged; atomic groups
  (`vm_atomic`) are its sibling, sharing the cut. The general form of its one-character subset is a context
  predicate: siblings `^`, `$` (both flavours), `\b`, `\B`, `\G` (site 10).
- Planned rows that extend the same shapes (goal 4): [DD-11] (more context rows), D66's anchor forms, variable
  lookbehind (REQ-OPEN: a bounded width, so the width library answers min AND max), the UTF-8 backend ([M5.0],
  APPROACH.md @T: back-step counts characters, so the seam row's signature is per encoding).
- Unlocks: R1 makes every later kind's payload a declared member (trigger: the next kind); R2 serves every
  per-branch width question (trigger: variable lookbehind).

## Seams
| seam | writer | readers | facts down | facts up | new calls | text round trip |
|---|---|---|---|---|---|---|
| encoding backend (D58) | `entries_byte[]` per backend | emit_vm.c | the back-step count in characters | whether start-of-subject was hit | none upward | yes (a row id and a count) |
| parse -> width library | R2's home | mod_lookaround (new) | a branch | its min and max width | parse calls DOWN into R2's home only | n/a (in-process) |
| AST -> VM emitter | the parser (payload) | emit_vm.c | direction, polarity, atomicity, widths | none | none | yes |

## What is deleted
R1: every kind's dead copy of every other kind's fields. R2: the opt-tier width home's parse callers, `vm_fadd`.
R3: two walks. The feature itself deletes nothing.

## What the design step must decide
The payload layout (site 1; union or pointer); the sub-match shape and its trail/slot interplay (sites 9, 11);
the back-step row's signature (site 7); the prefilter soundness argument and its measurement (site 6); the
one-character recognizer's shape list (site 10).

## Open questions for the owner
- `payload-first`: should the Ast payload remodel (R1) land before the module, as its own no-mover unit, rather
  than adding a fifth set of top-level fields? Leaning: yes; D62's own trigger ("four analyses today") is met.
- `context-table-home`: is the one-character lookaround subset this module's rows or [DD-11]'s? Leaning: [DD-11]'s,
  with the register row above, so the module ships the general lowering only.
