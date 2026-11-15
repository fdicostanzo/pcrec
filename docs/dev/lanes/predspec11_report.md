# predspec11 report: predicate spec rev 11

Lane predspec11 (opus), 2026-11-15. Design only; no build go; nothing under src/, cli/, lib/, memfn/, tests/,
docs/spec/, COND-FAMILY.md or plan.md touched. Base 7bf3c1aea (premise checked: the draft's changelog said rev 10).

## STATE AT HANDOFF

- DONE. `docs/design/predicates_draft.md` is rev 11: the 15 FIX-NOW findings of review
  `docs/dev/reviews/2026-11-15-r12-predspec10.md` applied with the picks of its DISPOSITIONS RULED; CENSUS-6 (a)
  (REJECTED) left as it stood.
- The round's critic texts copied to `docs/dev/reviews/2026-11-15-r12-predspec10/` (census.md, simulate.md,
  verify.md, COMMON.md, process.md), listed in `docs/dev/reviews/CLAUDE.md` (12,174 bytes, under the limit).
- `.claude/skills/pcrec-critic/SKILL.md`: the two accepted process changes, one sentence each (§4 simulate row: a
  re-check that folds a ruling re-applies every SAME row under it; §5: design mode copies the frozen subject and its
  rulings read-only into the round dir).
- Rulings file `docs/dev/lanes/predspec11_rulings.md`: empty at every read (before each commit and this report);
  last R-n applied: none.
- Validation: `make test-plan-lint` (2 passed, 0 failed) and `make test-spec-history` (11 passed, 0 failed) in the
  worktree; no suites owed (design only).

## FINDINGS FIXED

| id | what rev 11 does | mark |
|---|---|---|
| SIMULATE-1 | L7, L11, L13, L15, L41 SAME -> DIFFERENT: BY DESIGN, each with its witness (`S-1`, `#a\nb`, `57`, the name `dead.x`, `foobar`); §2.7, §7.1, §11 (THE FILTERED SPAN, ONE SPAN PER FILTER ROLE, REASONING) and E-CTX-1/5 respelled; a new §0.1 paragraph re-applies every SAME row; §12 REV 11 paragraph re-applies every case. No tail added (manager's pick) | anchoring RULED BY ACCEPTANCE (CF:991-993, at CF:990) for directly applied filters; L13/L15 by this document's application, LEAN |
| SIMULATE-2 | the second argument refusal NARROWED to its reason: refused only when some path reaches a backreference/conditional without having set its group in this hit; `/(.)\1/` and E-SEP's PCRE pattern admitted; §2.6, §8, L62, O53; draft:651's example now consistent | LEAN (this lane's pick; why below) |
| SIMULATE-3 | the hand-check note's reason: one row has a top-level `\|`, scoped by the `(?<hit>...)` capture | doc |
| CENSUS-1 | the selection written over the ITERATIONS in the label path, `$m.hit[(g: "x")]`; `$m.hit[2].g` read as the whole path; `$` entries carry no labels (§2.6, §3.2 tool 1, §4.3, §5.4 `[ ]` and `$` rows, C17, O50) | spelling LEAN |
| CENSUS-2 | `balanced := /(?<p>\((?:[^()]\|(?&p))*\))/`, plain PCRE (libpcre2 finds `(a(b))` in `x(a(b))y`); §11 Crossings: rx -> expression only by `${}`; the count stays two | LEAN (manager's pick) |
| CENSUS-3 | §11 `&` bullet: WHICH `&` IS THE MARK UNDER ON (lean: PCRE's own constructs keep their meaning; the mark replaces only a bare literal `&`); literal `[&]`; `\&` rewrite withdrawn; G3's counts split by token; §0 table, §0.2, §5.4, O60 (d) | LEAN (manager); OWNER QUESTION |
| CENSUS-4 | "takes no matchable PCRE meaning away" restricted to pattern positions; class and `\Q...\E` stated, restored by the `$\{` rewrite | doc |
| CENSUS-5 | the scope of an rx-text `&` (whole concatenation), the grouped guard `(?:(\d+)&${<256})`, new look-alike L67 (DIFFERENT: GAP), §11 HOLES, C3, O60 | LEAN |
| CENSUS-6 | (b) O50 (a)'s mark split; (c) C23 removed from STILL OPEN; (d) E-NEAR (c) and E-HTTP outcomes worded as EXPECTED under the unmeasured budget. (a) REJECTED: unchanged | doc |
| CENSUS-7 | MARK TABLE case columns (`/.../`, `${ }`, `@`, `,`, strings/numerals, `+`), KIND TABLE effect row, TWO-WAY CENSUS (`@assert`, new `+` row) | doc |
| CENSUS-8 | one hit RULED BY ACCEPTANCE; every hit and selection LEAN (§0.2, §2.6, §4.3, §5.4, O50) | doc |
| CENSUS-9 | the per-match rule marked once: RULED BY ACCEPTANCE (CF:997-999, at CF:1000) in §0.1 STATUS, L56, §4.2 STATUS; "reached" wording LEAN | doc |
| CENSUS-10 | transform vs filter modifier (§0 l.108, §2.1, §2.2); "searched" at the six sites plus O36 | doc |
| CENSUS-11 | `$` = the VALUE(S) of a label path (captured text, metadata, computed label); §0.3 "captured string" scoped | doc |
| CENSUS-12 | a duplicate label inside a loop is a repeated label first (iterations, each from the group it set: `b`, `a` on `ba`); "lowest-numbered set group" scoped to set-once duplicates; O35 keeps the rest | LEAN |

SIMULATE-2, WHY NARROW: the stated reason ("one iteration can see another") then IS the rule; the broad form refused
arguments whose loop answers equal find-all (the critic's sweep: 1,365 subjects, 0 differences) and created a G0
look-alike (`/(.)\1/` searched legal, `contains(/(.)\1/)` refused); the property stays static (a path check on the
argument's own pattern). The cost: one static analysis instead of a syntactic test.

CENSUS-3, ORACLE RESULT (system libpcre2-8 10.46 via its public API, and Python 3.14 `re`): `\&` compiles in both and
matches `&` (`xx&a&b`: (2,3) and (4,5)); `[&]` and `[\&]` the same; `(?<a>x)(?\&a)` is a libpcre2 compile error
("unrecognized character after (? or (?-", offset 9; Python rejects `(?\&` too). So the round's claim holds for the
REWRITE (every `&` -> `\&` breaks `(?&name)`), not for `\&` itself; the `\&` lean is withdrawn as the rewrite and
`[&]` is the one spelling. Corpus split of the 165 `&` pattern lines (working tree `tests/`): 154 `(?&name)`, 7
callout text `(?C...)`, 1 `\p{bc=L&}`, 2 class-only, 1 bare literal `&` (a URL query). Script (lane scratch, not
committed): walk `tests/**/*.rxt`, keep `pattern ` lines with `&`, and for each `&` skip escapes (`\x` two chars,
`\Q...\E` whole), class bodies, and the openers `(?&`/`(?P>`; a line with an `&` left over has a bare literal.

## ROWS AND EXAMPLES RE-APPLIED

Under the anchoring ruling (CF:991-996: a directly applied filter is anchored at both ends; `contains`/`search`
remove that; `^`/`$` in their argument are the span's ends), each in its real mode (on the value unless the row says
SEARCHED). Oracle witnesses (libpcre2 whole-value): `^S\w*` on `S-1` None vs `(?:S)(?s:.*)` match; `^#.*` on `#a\nb`
None vs startsWith match; `^5` on `57` None; `^foo` on `foo` match only; `^S\w*` on `Sab` match; `^[A-Z][\w-]*` on
`Host` match.

| row | result | note |
|---|---|---|
| L1, L2, L3, L36, L39, L42, L44, L46, L58 | unchanged (SAME holds) | no `^`/`$` in a filter |
| L4, L5, L6, L8, L9, L10, L12, L14 | unchanged | errors; L8/L9 holes and final patterns unaffected |
| L7 | ANSWER MOVED: SAME -> DIFFERENT: BY DESIGN | `S-1`; agree only on `\w` spans (E-CTX-1) |
| L11 | ANSWER MOVED: SAME -> DIFFERENT: BY DESIGN | `#a\nb`; agree on line items (E-FILE) |
| L13 | ANSWER MOVED: SAME -> DIFFERENT: BY DESIGN | `57`: `padded(/^5/)` = `padded("5")` |
| L15 | ANSWER MOVED: SAME -> DIFFERENT: BY DESIGN | a name set holds whole names: `dead.` only |
| L16 | unchanged | `^` inside `search`'s argument: span start |
| L17, L63 | unchanged (SAME holds) | the anchor sits inside `contains` |
| L18, L26, L27 | unchanged (SAME holds) | final patterns; class members; positions |
| L19 | respelled ("searched mode") | CENSUS-10 |
| L20-L33, L35, L37, L38, L40, L43, L45, L47-L57, L59-L61, L65, L66 | unchanged | no `^`/`$` in a directly applied filter; L34/L59/L66 searched answers re-read: unchanged |
| L34 | unchanged (SAME holds) | conditions already read the anchored parse |
| L41 | ANSWER MOVED: SAME -> DIFFERENT: BY DESIGN | searched in `foobar`: `foo` vs `foobar` |
| L62 | respelled (reason narrowed) | SIMULATE-2; its witness still refused |
| L64 | unchanged answer, rule now stated | CENSUS-12 |
| L67 | NEW (DIFFERENT: GAP) | CENSUS-5 |

| §12 case | result |
|---|---|
| E-JSONL | unchanged (`^`/`$` in the FINAL pattern, searched per line; `contains("timeout")` loosened) |
| E-WEEKDAY, E-CAL, E-RFC, E-SEP, E-DEPTH | unchanged (no anchor in a filter) |
| E-IPV4 | unchanged (whole and searched answers; wording "SEARCHED program") |
| E-LUHN | unchanged (`startsWith("4")` is the library call) |
| E-NEAR | answers unchanged; (c)'s default-level refusal respelled as EXPECTED under the unmeasured budget |
| E-FILE | unchanged (`!startsWith("#")`; item rx searched); "searched program" |
| E-HTTP | answers unchanged (anchored by `\A`/`\z` in the final pattern); the `count()` budget sentence respelled |
| E-CTX-1 | answer unchanged (`a Sab` match); reason respelled (x ENTIRELY `S\w*`; equals startsWith only because x is `\w+`) |
| E-CTX-2, 3, 4, 6 | unchanged (compile errors) |
| E-CTX-5 | stated equivalence MOVED: `padded(/^5/)` = `padded("5")`, not `padded(startsWith("5"))`; no-error verdict unchanged |
| E-CTX-7 | unchanged (already read as a whole-string set) |
| agreeing look-alike | unchanged |

## OPEN ITEMS

1. (Owner question, §13 O60 (d).) With the `&` switch ON, should PCRE's own constructs that contain an ampersand keep
   their PCRE meaning, so that `&` is the intersection only where PCRE would read a plain ampersand character?
   Example: in `/(?<w>\w+)(?&w)&${<256}/` the `&` inside `(?&w)` is PCRE's "call the group w" and the second `&` is
   the intersection. Most `&` in real PCRE patterns are such calls (154 of 165 corpus lines); the other reading makes
   every `&` the operator, so `(?&w)` could not be written with the switch ON. A plain ampersand under ON is written
   `[&]`. Lean: yes, PCRE's constructs keep their meaning (the manager's lean).
2. (Manager-side, LEAN, for the acceptance read.) The selection spelling `$m.hit[(g: "x")]` gives the index bracket
   two kinds of filter in a match position (a numeral by position, a condition by the iteration's labels). The
   alternative (CENSUS-1 (b): `$` entries carry labels and positions) would give `$` and "captured string" a second
   meaning. Lean: the bracket.
3. (Manager-side, LEAN.) SIMULATE-2 narrowed rather than reason-widened (above). If the static path check is judged
   too costly, the alternative is the broad rev 10 refusal with its reason widened to "any backreference or
   conditional on its own group", and draft:651's `/(.)\1/` example replaced.
4. (Manager-side.) L67 and the five rows moved to BY DESIGN raise O38's existing question: whether a warning should
   name a `^` in a directly applied filter (it looks like "starts with") and an rx-text `&` whose result is empty.
   Not proposed here as a named diagnostic.
5. E-NEAR (c) and E-HTTP now carry EXPECTED budget outcomes; they become fixed only when the ONE budget is measured
   (§13 O39, RULED as a budget, unmeasured).
