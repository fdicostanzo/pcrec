# SIMULATE findings: predspec12

## Findings

### SIMULATE-1 (CONFIRMED; severity design/answer; effort small text + one owner question; blast radius every top-level `&` program whose operand writes `^`/`$`/`\A`/`\z`, L39, L41, §11)
WHICH SIDE OF `rx & rx` IS "THE FILTER SIDE". The rule (CF:1011, draft:2088) anchors "the filter side of `&`" and leaves
"everywhere else" (a final pattern) searched; the owner's words are "the filter POSITION of &" (CF:1004), and §2.1
(draft:556) says `X & R` FILLS R's operand WITH X (X is the operand, not the filter). But `&` on two rx is commutative
(§2.2 draft:641, L39) and §11 STRING SETS (draft:2078) makes EVERY "`&` operand" a set position. The draft never says
which reading holds for the LEFT operand of a program's top-level `&`, and each reading breaks a row:
- Reading F (draft:2078, both operands are filters, `^` = the span's start): `/^\d+$/` vs `/^\d+$/ & <256` searched in
  `x300 12`: the lone pattern finds nothing (oracle search: None), the `&` program matches `30` at (1,3); `/^foo/` vs
  `/^foo/ & /(?s).*/` (intersection with EVERY string) on `xfoo`: None vs (1,4). A look-alike with no L-row and no
  class; the user's own anchors in a guarded final pattern silently stop meaning the subject's ends (draft:2110 says
  only the LONE `/^foo/` differs).
- Reading O (the owner's/record's words, draft:556: the left operand is NOT in filter position, so it is "everywhere
  else", searched, `^` = the subject's start): `/^foo/ & /\w+/` finds nothing in `xfoo`, `/\w+/ & /^foo/` finds (1,4):
  L39's SAME ("`A & B` and `B & A` accept the same subjects") is false.
Oracle: simulate/sim2.py (libpcre2 whole-span matches per operand, D196 leftmost start; 39 calls).
FIX: state which reading the one rule takes for `rx & rx`; under F add a row `P` vs `P & /(?s).*/` (DIFFERENT, a
class: GAP or a proposed `anchor.operand` warning for `^`/`$`/`\A`/`\z` in a top-level `&` operand of a final
program) and note `/^\d+$/ & <256` is "contains a numeral below 256"; under O, L39 becomes DIFFERENT. An owner
question either way (his "filter position" presumes an asymmetry `&` does not have). Location §11 draft:2088-2096,
draft:2078; §0.1 L39 draft:294, L41 draft:296; §2.1 draft:556.

### SIMULATE-2 (CONFIRMED; severity answer/doc; effort one sentence; blast radius every filter written INSIDE a hole of a final pattern, incl. E-HTTP's own hole)
THE HOLE SENTENCE OVERREACHES. draft:2158-2160: a hole's "`^`/`$` are the ends of the scoped match of the rx it sits
in, the enclosing filter's span or a final pattern's subject"; draft:2122-2123: "Nothing written INSIDE a filter opens
a span of its own, because a hole has no scoped match of its own". Read literally, a `label:` condition or `&` operand
INSIDE a hole of a final pattern gets the SUBJECT's ends, contradicting the rule's first bullet (a condition matches
the WHOLE value, draft:2088). Witness: E-CTX-7's condition placed in E-HTTP's anchored hole,
`/\A${headers & (name: /^[A-Z][\w-]*/)}\z/` on `Host: a\r\nAccept: b`: hole-literal reading (`^` = subject start)
no match (oracle search: None); filter reading (`^` = each name's start, adds nothing) match (0,18); E-CTX-7 (draft:2541)
claims match for the same condition at top level. `/x${/^a/ & /\w+/}/` on `xa`: None vs (0,2). Oracle: simulate/sim3.py,
sim2.py. FIX: "an rx in a hole, OUTSIDE any filter role written inside the hole, ..."; every filter role (an `&`
operand, a `label:` condition, a modifier's argument) opens its own scoped match wherever it stands. (Same root as
SIMULATE-1: what opens a scoped match.) Location §11 draft:2120-2125, draft:2158-2160; §0.3 "scoped match" draft:455.

## PROBED-AND-HELD
- (a) §0.1, ALL 69 rows re-read under the one rule (CF:1011-1020), each in its stated mode (value unless SEARCHED).
  Anchor-bearing rows ORACLED from the draft's TEXT bodies (§2.6 draft:732, §8 draft:1883-1886, holes as `(?:x)`),
  brute force with Python `re` over all 1,365 strings of length 0-5 on {e,r,x,\n} plus libpcre2 on each witness:
  L7, L11, L41 (DIFFERENT, witnesses hold), L16 (search min 0 = every string, 0 diffs), L17 (SAME, 0 diffs),
  L58 (SAME, 0 diffs), L63 (DIFFERENT: exactly the 5 strings ending `err\n`; `contains(/err\z/)` = `endsWith("err")`,
  0 diffs), L68 (final: `anchored(er)` vs `\A..\z` differ only on strings ending `\n`, so "agree on every subject not
  ending in a newline" holds), L69 (identity for `e|er`, `r\n?`; `/^e/` = `/e/` in a filter), draft:2089
  `m & /^err$/` = `m & /err/` (0 diffs), §8's "same SETS as the record" for lazy `endsWith`, `contains`,
  `startsWith(/e$/)` (0 diffs each). L13, L15 by reading (compile-time / modifier argument as whole filter: consistent).
  L34, L59 (whole `123`: a=`12`; `12`: a=`1`; into-pattern a=`1`), L55, L57 (min 2 re-cuts to `a`@0, `a`@1) oracled:
  hold. Every other row writes no anchor or only in a final pattern, or is an ERROR/GAP/OPEN row whose class the rule
  does not touch: verdicts and classes unchanged. Only the SIMULATE-1 rows (L39, and the missing `P & U` row) fail.
- (a) §12, all twelve cases in their real mode: E-IPV4 searched (`56.1.1.1`, `1.2.3.4`, `\b` final finds (14,22)),
  E-LUHN (searched, all three answers; `startsWith("4")` as gap body), E-SEP (4 answers), E-CTX-1 (x = `Sab` whole),
  oracled; E-JSONL, E-HTTP, E-FILE (anchors in the final pattern / item rx), E-WEEKDAY, E-CAL, E-RFC, E-NEAR, E-DEPTH,
  E-CTX-2..7 by reading: hold as top-level programs (E-HTTP holds because its hole writes no anchor in a filter;
  SIMULATE-2 shows the hole sentence would break E-CTX-7's condition moved into it). Note: E-NEAR has no final
  program line, so its mode is unstated (not anchoring-relevant).
- The lane's predspec12_anchor.py: all 16 rows re-run; every spliced body equals the draft text (the §2.6 hole
  `(?<hit>${x})` spliced as `(?<hit>(?:x))`, per the hole semantics draft:740); each row's mode matches the rule.
- Oracle calls: ~125 libpcre2 (sim1 34, sim2 39, sim3 4, sim4 ~48) plus Python `re` brute force.

## FOLD-IN (b)
- Siblings: `\b` at a span edge stays the edge-assertion ERROR while `^`/`$` read the span as the subject (draft:2133-2139
  argues an anchor reads no character; `$` does read one, a final newline, but only inside the scope, so consistent).
  Lookbehind at an edge: same error, consistent. `\G`: refused in the strict subset. Compile-time name sets read as
  whole-string filters (LEAN) and `records` item rx searched: both consistent with the rule. `\Z` (PCRE's `$` twin) is
  not named in draft:2094's list (`\A`, `\z`, `(?m)`): doc nit. The sibling the draft handles INCONSISTENTLY is what
  OPENS a scoped match: SIMULATE-1 (the left operand of `&`) and SIMULATE-2 (a filter inside a hole).
- General form + unlock: "a scoped match is opened by exactly two things, the PROGRAM (the subject, searched) and every
  FILTER ROLE wherever it stands (its span, matched whole); nothing else opens one; every anchor reads the innermost."
  Unlock: `anchored(P)` can be defined as "P in filter role on the enclosing scope" rather than a text splice, giving
  exact ends with no new rule and dissolving L68/O62. Trigger: the owner rules O62, or a case writes `anchored(block)`
  (E-HTTP's record suggestion).
- Goals in order: G0 served by honesty (L63, L68 now stated DIFFERENT BY DESIGN) but SIMULATE-1 is an unlisted G0
  look-alike; G0b: one added name, no new mark; G1, G2 untouched; G3 served (`$` is plain PCRE's).
