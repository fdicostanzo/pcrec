# PCRE2 syntax compliance — anticipated and actual

Reference: <https://www.pcre.org/current/doc/html/pcre2syntax.html> (the syntax
quick reference; section names and order below follow it). DFA-feasibility
judgements additionally draw on
<https://www.pcre.org/current/doc/html/pcre2matching.html>, which documents what
PCRE2's OWN non-backtracking matcher (`pcre2_dfa_match`) can and cannot do —
useful prior art, since pcrec is also non-backtracking by construction.

**Last surveyed: 2026-08-09** against pcrec at `ddb73a2`+ and libpcre2 10.46.
This is a living document; see "Keeping this current" at the end.

## What the statuses mean

Frank asked for compliant / mostly compliant / anticipated compliance /
anticipated non-compliance / proven non-compliance. Two distinctions turned out
to matter enough to split those:

- **verified vs believed.** "It works" and "it works and an oracle agrees" are
  different claims, and this project has been burned by the second being
  assumed from the first.
- **rejected cleanly vs miscompiled.** The project mandate is that an
  unsupported construct "must fail with a clean `requires module 'X'` error,
  never miscompile". A clean rejection is a DESIGNED state, not a gap, and it
  deserves its own status rather than being lumped in with non-compliance.

Each row carries TWO values, because mixing them is what made the first draft
inconsistent (some rows said `REJECTED → PLANNED`, others buried the trajectory
in prose). `status` is what is true TODAY — one value, greppable. `becomes` is
the intended end state, or `—` when there is no plan.

| status (today) | meaning |
|---|---|
| `OK` | Supported, exercised by the .rxt corpus, cross-verified against an oracle |
| `OK-LIMITED` | Supported, correct within a limit stated in the row |
| `REJECTED` | Not supported. Exits 1 with `requires module 'X'`, writes no output, never miscompiles. Pinned construct-by-construct by `tests/reject/` |
| `AGREES-REJECT` | PCRE2 rejects it too, and pcrec rejects it the same way. Refusing the pattern IS compliance here — not a gap |
| `OUT-OF-SCOPE` | Deliberately excluded, with the reason |
| `DIVERGENCE` | An OPEN measured difference from libpcre2. Currently none: the two ever found were fixed on 2026-08-09 and their rows say so |

| becomes | meaning |
|---|---|
| `—` | no plan; the status is the end state |
| `PLANNED` | a named module/milestone owns it, no known architectural obstacle |
| `PLANNED-HARD` | owned, but the architecture makes it genuinely difficult — needs the M4 VM engine, or fights the D7 two-pass DFA design. Reason per row |

Roughly against the vocabulary Frank asked for: `OK` = compliant;
`OK-LIMITED` = mostly compliant; `becomes: PLANNED` = anticipate compliance;
`becomes: PLANNED-HARD` = anticipate compliance with risk; `OUT-OF-SCOPE` =
anticipate permanent non-compliance, by choice; `DIVERGENCE` = proven
non-compliance. `REJECTED` and `AGREES-REJECT` have no equivalent in that list
and are the reason it needed splitting — a clean refusal is a designed state.

**These two columns are the prototype of the registry's `status`/`becomes`
fields (D24).** The registry landed (SR-1) and SR-4 connected it to this file —
but not by rendering the whole document, which was the original plan and would
have been a bad trade. What is generated is the **construct index** at the end:
one row per registry row, printed by the compiler itself, so the INVENTORY
cannot drift. What stays hand-written is everything that makes this a survey
rather than a listing — the DFA-feasibility judgements, the `PLANNED` vs
`PLANNED-HARD` calls and their reasoning, the divergence post-mortems, and every
row about BASE syntax, which the registry deliberately does not describe.

Two `make test` checks hold the seam (`tests/registry/compliance_section.py`):
the generated index must match `pcrec --list-syntax`, and every module named in
the prose above must be a module the registry actually knows. The second is the
one that catches the realistic failure — a module renamed in `registry.c` leaves
this document confidently describing something that no longer exists.

## Headline

pcrec implements a deliberately small base tier and rejects the rest by design.
Of PCRE2's syntax surface:

- The base tier (literals, `.`, classes, ranges, quantifiers incl. lazy,
  alternation, groups, `^`, `$`, the character escapes) is `OK`, with 842
  corpus cases at 100% oracle agreement (824 of them python-verified; the rest
  are `# pcre2-only` blocks checked against libpcre2 directly).
- Everything else is `REJECTED` — 137 rows in `tests/reject/` individually
  assert exit 1 and the right diagnostic (117 of them a module name; the other
  20 are the base-grammar brace errors K5/K6 landed on 2026-08-10, which name a
  PCRE2 error instead), with 37 accept-controls proving
  the table cannot pass by rejecting everything, and (SR-4) a further 66 checks
  that iterate `pcrec --list-syntax` so no registry row can escape a probe
  (`tests/reject/`). The two layers answer different questions and neither
  subsumes the other: iteration guarantees coverage but reads the same table
  the parser renders from, so it cannot see a WRONG module name — measured, by
  changing `\d`'s row to `misc`, which the hand-written rows catch twice and
  iteration does not catch at all.
- **Two proven divergences have been found, both fixed:** `\v` (Character
  types) and POSIX collating elements (Character classes). Both were silent —
  pcrec compiled something PCRE2 does not — and in both cases python `re`
  agreed with pcrec, so the base-tier oracle was blind to them.

The single most useful thing this survey produced was not the table. It was
finding that the mandate's central guarantee had no test at all (see "How this
survey earned its keep").

---

## Quoting

| syntax | status | becomes | notes |
|---|---|---|---|
| `\` + non-alphanumeric | `OK` | — | escaped punctuation is a literal; corpus-covered |
| `\Q...\E` | `REJECTED` | `PLANNED` | module `quoting`. Pure front-end lexing; `PLANNED`-easy whenever wanted |

## Braced items

| syntax | status | becomes | notes |
|---|---|---|---|
| whitespace inside `{ }` in `\g{2}` etc. | `REJECTED` | — | reached only via constructs that are themselves rejected |
| `\u{...}` (ALT_BSUX) | `OUT-OF-SCOPE` | — | an ECMAScript-compatibility spelling gated on a PCRE2 option pcrec does not model |

## Escaped characters

| syntax | status | becomes | notes |
|---|---|---|---|
| `\a` `\e` `\f` `\n` `\r` `\t` | `OK` | — | each verified byte-for-byte against libpcre2 during this survey |
| `\xhh` | `OK` | — | 1–2 hex digits; `digits missing after \x` matches PCRE2 error 178 |
| `\x{hh..}` | `REJECTED` | — | module `unicode-props` |
| `\cx` | `REJECTED` | — | module `misc`. Trivially implementable; base tier simply does not include it |
| `\0dd`, `\ddd` | `REJECTED` | — | module `backrefs` — PCRE2 resolves octal-vs-backreference by context, so they share an owner |
| `\o{ddd..}` | `REJECTED` | — | module `misc` |
| `\N{U+hh..}` | `REJECTED` | — | module `classes` (see note under Character types about the `\N` spelling clash) |
| `\U`, `\uhhhh` (ALT_BSUX) | `OUT-OF-SCOPE` | — | option-gated compatibility spellings |

## Character types

| syntax | status | becomes | notes |
|---|---|---|---|
| `.` | `OK` | — | excludes `\n` only, PCRE2's default. `(?s)` dotall is `REJECTED` (module `modifiers`) |
| `\d \D \s \S \w \W \h \H \V \N` | `REJECTED` | `PLANNED` | module `classes`. All are single-position bitmap predicates — `PLANNED`, easy, no engine work |
| `\v` | `REJECTED` | `PLANNED` | **Was a proven divergence, fixed 2026-08-09.** PCRE2 defines `\v` as vertical WHITESPACE (`0x0a 0x0b 0x0c 0x0d 0x85`, measured against libpcre2 10.46); pcrec decoded it as vertical tab `0x0B` only, inside classes as well as outside. Now `REJECTED` to module `classes` like its negation `\V`. It survived because python `re` also reads `\v` as `0x0B`, so the base-tier oracle agreed with the bug — see "How this survey earned its keep" |
| `\C` | `REJECTED` | `PLANNED` | "one code unit". In the ASCII tier that is just "any byte", i.e. trivial. PCRE2 forbids it under its own DFA matcher in UTF modes for the reason that will apply to us in M5 |
| `\p{..}` `\P{..}` | `REJECTED` | — | module `unicode-props`, M5. Single-position predicates, so DFA-friendly; the work is Unicode tables, not engine |
| `\R` | `REJECTED` | `PLANNED` | module `misc`. Not a single character — a small alternation of literal sequences (CR, LF, CRLF), so still regular and `PLANNED`-feasible |
| `\X` | `REJECTED` | `PLANNED-HARD` | extended grapheme cluster: variable-length, Unicode-table-driven segmentation. Regular in principle, substantial in practice. M5 at the earliest |

## Unicode properties (general category, PCRE2 special, binary, script, bidi)

| syntax | status | becomes | notes |
|---|---|---|---|
| `\p{L}` `\p{Lu}` … (general categories) | `REJECTED` | — | module `unicode-props`, M5 |
| `\p{Xan}` `\p{Xps}` `\p{Xsp}` `\p{Xuc}` `\p{Xwd}` | `REJECTED` | — | same |
| `\p{<binary property>}` | `REJECTED` | — | same |
| `\p{scriptname}` `\p{sc:..}` `\p{scx:..}` | `REJECTED` | — | same |
| `\p{Bidi_Class:..}` `\p{BC:..}` | `REJECTED` | — | same |

All of these lower to byte-range sets over UTF-8, which APPROACH §4/§10 already
commits to. The blocker is table generation and size, not matching.

## Character classes

| syntax | status | becomes | notes |
|---|---|---|---|
| `[...]`, `[^...]`, `[x-y]` | `OK` | — | corpus-covered incl. `]` first, `-` last, high bytes, out-of-order range rejection |
| `[[:alpha:]]`, `[[:^alpha:]]` and the 14 POSIX names | `REJECTED` | `PLANNED` | module `classes`. `PLANNED`, easy |
| `[[.ch.]]` collating elements, `[[=ch=]]` equivalence classes | `AGREES-REJECT` | — | **Was a proven divergence, fixed 2026-08-09.** PCRE2 does not support these and REJECTS them ("POSIX collating elements are not supported"); pcrec silently accepted them as a class of literal `[` `.` `a` characters. Now rejected with PCRE2's own wording, so rejecting IS compliance here. The trigger was pinned against libpcre2 rather than guessed: `[` + `.`/`=` opens a collating element ONLY when the matching `.]`/`=]` terminator appears later, and a negated class suppresses it — so `[.a]`, `[.]`, `[[.]`, `[a[.b]`, `[^.a.]` and `[a.b.]` must all still COMPILE. Over-rejecting here would break patterns PCRE2 accepts, which is why those six are accept-controls in `tests/reject/` |
| `\Q...\E` inside a class | `REJECTED` | — | module `quoting` |
| `[x&&y]`, `[x--y]`, `[x~~y]` (UTS#18 set ops) | `OK` | `PLANNED` | pure bitmap algebra at parse time; no engine implication at all |
| `(?[...])` Perl extended classes, `& - ^ ! +` operators | `REJECTED` | `PLANNED` | same — a parser feature that produces one bitmap. Note `^` means XOR here, not negation; a spelling trap worth a test when implemented |

## Quantifiers

| syntax | status | becomes | notes |
|---|---|---|---|
| `? * + {n} {n,m} {n,} {,m}` greedy | `OK` | — | `{,m}` = `{0,m}` per PCRE2 10.43+, found by our own fuzzer |
| `?? *? +? {n,m}? {n,}? {,m}?` lazy | `OK` | — | priority subset construction preserves greedy/lazy preference (D3) |
| `?+ *+ ++ {n,m}+ {n,}+ {,m}+` possessive | `REJECTED` | `PLANNED-HARD` | module `atomic-groups`. Possessiveness prunes alternatives that a priority simulation explores in parallel, so it is a real semantic change needing explicit cut support, not a no-op |
| quantifier on `^`/`$` | `OK` | — | rejected as PCRE2 error 109 does; `(^)*` is accepted because a group wrapper makes it quantifiable, matching PCRE2 |
| double quantifier `a**`, `a{2}{3}` | `OK` | — | rejected, corpus-covered. Note the WORDING differs on `a{1}{2}`: PCRE2 says error 109, pcrec says "multiple quantifiers on the same item". Same verdict, and the offset agrees |
| count above 65535, `a{65536}` | `AGREES-REJECT` | — | PCRE2 error 105. **Was a MISCOMPILE until 2026-08-10 (K5, FIX-1)** — silently reinterpreted as literal text, so the emitted matcher accepted a different language than the pattern named. The overflow is judged only once the form is CONFIRMED to be a quantifier, which is what PCRE2 does: `a{65536x}`, `a{65536,x}` and `a{65536` all stay literal in both engines |
| `{m,n}` with nothing to quantify, `{1}` | `AGREES-REJECT` | — | PCRE2 error 109. **Was a MISCOMPILE until 2026-08-10 (K6, FIX-1)**; `*`, `+` and `?` had always been rejected in this position and only `{` was missed, because `try_quant` is reached from `p_rep`, i.e. after an atom. Malformed braces (`{}`, `{,}`, `{1`, `a{`) stay literal in both engines, and the reject suite's accept-controls pin that |
| brace diagnostic PRECEDENCE | `OK` | — | measured, not assumed: in atom position PCRE2 answers 105 for `{65536}` and 104 for `{3,1}`, not 109; and too-big beats out-of-order, so `a{65536,1}` is 105. pcrec agrees on all three, offsets included |
| large bounded repeat, `a{0,65535}` | `OK-LIMITED` | `PLANNED` | correct up to roughly `{0,20000}`. Above that the NFA/DFA build exhausts memory and the process is SIGKILLed instead of reaching the 32000-state cap that exists to prevent exactly this — see **K7**. `a{65535}` (the exact-count form) does hit the cap cleanly. Not a miscompile; no wrong code is emitted |

## Anchors and simple assertions

| syntax | status | becomes | notes |
|---|---|---|---|
| `^` | `OK-LIMITED` | — | start of subject. Multiline `^` is `REJECTED` (module `modifiers`); the DFA-state-context design for it is DD-6 |
| `$` | `OK` | — | end of subject or before a final newline — PCRE2's default. Mid-pattern `$` is fully general via EOL-variant states |
| `\A \Z \z \b \B \G` | `REJECTED` | — | module `assertions`. `\A`/`\z` are trivial. `\b`/`\B` need a one-byte lookbehind, which is a state-context change (same machinery as DD-6). `\G` additionally collides with `nfa_wrap_unanchored`'s baked-in start self-loop — that is DD-4 |

## Reported match point setting

| syntax | status | becomes | notes |
|---|---|---|---|
| `\K` | `REJECTED` | `PLANNED-HARD` | module `assertions` (previously fell through to `unknown escape \K`; fixed in this survey). Architecturally awkward for a specific reason: D7's engine finds the match END with a forward pass and then rescans BACKWARD for the start. `\K` redefines what "start" means mid-pattern, so it interacts directly with the reverse machine rather than being a local annotation. PCRE2 does not support `\K` in its own DFA matcher either |

## Alternation, capturing, atomic groups

| syntax | status | becomes | notes |
|---|---|---|---|
| `a\|b` | `OK` | — | incl. empty branches; leftmost-first preference via priority pruning (D3) |
| `(...)` | `OK-LIMITED` | — | parses and groups correctly, but capture SPANS are not reported — only the overall match. Captures arrive with the M4 VM engine |
| `(?:...)` | `OK` | |
| `(?<name>...)` `(?'name'...)` `(?P<name>...)` | `REJECTED` | — | modules `lookaround/named-groups` / `named-groups`. Gated behind captures (M4) |
| `(?>...)`, `(*atomic:...)` | `REJECTED` | `PLANNED-HARD` | module `atomic-groups` / `verbs`. Same reasoning as possessive quantifiers: a cut, not a no-op |

## Comment

| syntax | status | becomes | notes |
|---|---|---|---|
| `(?#....)` | `REJECTED` | `PLANNED` | module `comments` (previously misattributed to `modifiers`; fixed in this survey). Pure lexing, `PLANNED`-trivial |

## Option setting

| syntax | status | becomes | notes |
|---|---|---|---|
| `(?i)` `(?i:...)` `(?-i)` | `REJECTED` | `PLANNED` | module `modifiers`. The MECHANISM already exists and is measured: `options.caseless` / `pcrec -i` folds case into class construction with zero runtime cost (D23). Scoped spellings need only a parser state variable saved/restored at group boundaries, because the fold is applied per-class at construction time |
| `(?s)` dotall | `REJECTED` | `PLANNED` | module `modifiers`. One bitmap change to `.` |
| `(?m)` multiline | `REJECTED` | `PLANNED-HARD` | module `modifiers`. `^`/`$` at internal newlines is DFA state context; interacts with the state budget (DD-6) |
| `(?x)` `(?xx)` extended | `REJECTED` | `PLANNED` | module `modifiers`. Pure lexing |
| `(?U)` ungreedy | `REJECTED` | `PLANNED` | swaps default quantifier preference — a front-end flip of the split edge order |
| `(?n)` no-auto-capture, `(?J)` dup names | `REJECTED` | — | gated behind captures/named groups (M4/M6) |
| `(?a)` `(?aD)` `(?aS)` `(?aW)` `(?aP)` `(?aT)` `(?r)` | `REJECTED` | — | UCP-restriction options; meaningless until M5 exists to restrict |
| `(?^)` reset options | `REJECTED` | — | module `modifiers` |
| `(*LIMIT_DEPTH=)` `(*LIMIT_HEAP=)` `(*LIMIT_MATCH=)` | `OUT-OF-SCOPE` | — | these bound a BACKTRACKING search. pcrec is O(n) by construction, so there is nothing to limit. D22 also removes the adversarial-input motivation |
| `(*NO_JIT)` `(*NO_START_OPT)` `(*NO_AUTO_POSSESS)` `(*NO_DOTSTAR_ANCHOR)` | `OUT-OF-SCOPE` | — | knobs for PCRE2 implementation internals that pcrec does not have |
| `(*NOTEMPTY)` `(*NOTEMPTY_ATSTART)` | `REJECTED` | `PLANNED` | match-time semantics, expressible; no owner yet |
| `(*UTF)` `(*UCP)` | `REJECTED` | `PLANNED` | module `verbs`; the underlying capability is M5 |
| `(*CASELESS_RESTRICT)` `(*TURKISH_CASING)` | `OUT-OF-SCOPE` | — | for the ASCII tier — revisit with DD-1's Unicode work |

## Newline convention and `\R`

| syntax | status | becomes | notes |
|---|---|---|---|
| `(*CR)` `(*LF)` `(*CRLF)` `(*ANYCRLF)` `(*ANY)` `(*NUL)` | `REJECTED` | `PLANNED` | module `verbs`. Newline convention is a compile-time parameter affecting `$`, `.` and `\R` — exactly the kind of thing D18 says should be hyperspecialized away |
| `(*BSR_ANYCRLF)` `(*BSR_UNICODE)` | `REJECTED` | `PLANNED` | same, scoped to `\R` |

## Lookaround

| syntax | status | becomes | notes |
|---|---|---|---|
| `(?=...)` `(?!...)` | `REJECTED` | `PLANNED-HARD` | module `lookaround`. Lookahead is automaton intersection — feasible, not cheap, and it multiplies states |
| `(?<=...)` `(?<!...)` | `REJECTED` | `PLANNED-HARD` | module `lookaround/named-groups`. Fixed-length lookbehind is tractable via the reverse machine D7 already builds; variable-length is much harder |
| `(*pla:)` `(*nla:)` `(*plb:)` `(*nlb:)` verbose spellings | `REJECTED` | — | module `verbs`; same underlying feature |
| `(?*...)` `(?<*...)` `(*napla:)` `(*naplb:)` non-atomic lookaround | `REJECTED` | `PLANNED-HARD` | the non-atomic variants are defined by their backtracking behaviour |

## Substring scan, script runs

| syntax | status | becomes | notes |
|---|---|---|---|
| `(*scan_substring:...)` `(*scs:...)` | `OUT-OF-SCOPE` | — | (revisit post-M4) — re-matches against previously CAPTURED text, so it needs capture state at match time |
| `(*script_run:...)` `(*sr:...)` `(*atomic_script_run:...)` `(*asr:...)` | `REJECTED` | — | module `verbs`. Needs Unicode script data (M5); the assertion itself is regular |

## Backreferences

| syntax | status | becomes | notes |
|---|---|---|---|
| `\1` `\g1` `\g{n}` `\g{+n}` `\g{-n}` `\k<n>` `\k'n'` `\k{n}` `(?P=n)` | `REJECTED` | `PLANNED-HARD` | module `backrefs`. **Backreferences are not a regular language** — no DFA can do them, and PCRE2's own DFA matcher does not. They need the M4 VM engine plus capture state. Note also D23's boundary: a CASELESS backreference compares subject text to subject text, which cannot fold into the automaton and needs a match-time comparison |

## Subroutine references and recursion

| syntax | status | becomes | notes |
|---|---|---|---|
| `(?R)` `(?n)` `(?+n)` `(?-n)` `(?&name)` `(?P>name)` `\g<name>` `\g'n'` … | `REJECTED` | `PLANNED-HARD` | modules `recursion` / `backrefs`. Recursion makes the pattern language context-free, which is outside both a DFA and a plain Pike VM; it needs a recursive/backtracking matcher. Unsupported by PCRE2's DFA matcher too |
| `(?R(grouplist))` and capture-retaining forms | `OUT-OF-SCOPE` | — | (revisit post-M4) — capture-state dependent |

## Conditional patterns

| syntax | status | becomes | notes |
|---|---|---|---|
| `(?(n)...)` `(?(<name>)...)` `(?(name)...)` | `REJECTED` | `PLANNED-HARD` | module `conditionals`. The condition is "did group N participate", i.e. capture state — explicitly unsupported by `pcre2_dfa_match` for the same reason |
| `(?(R)` `(?(Rn)` `(?(R&name)` | `REJECTED` | — | recursion-dependent |
| `(?(DEFINE)...)` | `REJECTED` | — | only useful with subroutine calls |
| `(?(assert)...)` | `REJECTED` | — | lookaround-dependent |
| `(?(VERSION>=n.m)...)` | `OUT-OF-SCOPE` | — | tests the PCRE2 library version; meaningless for a different implementation. If a compatibility layer (V-A) ever wants it, it is a parse-time constant fold |

**Disambiguation trap worth recording**: PCRE2 resolves `(?(name)` as a
group-reference condition when a group of that name exists and as a recursion
test otherwise. Any conforming implementation must replicate that rule exactly
or it will silently miscompile ambiguous patterns.

## Backtracking control verbs

| syntax | status | becomes | notes |
|---|---|---|---|
| `(*FAIL)` `(*F)` | `REJECTED` | `PLANNED` | module `verbs`. The one verb PCRE2's DFA matcher DOES support: in a priority simulation it is simply a path that never reaches an accept state |
| `(*ACCEPT)` | `REJECTED` | `PLANNED-HARD` | module `verbs`. Expressible in principle (force an accept), but it interacts with the two-pass end-then-start architecture |
| `(*COMMIT)` `(*PRUNE)` `(*SKIP)` `(*SKIP:NAME)` `(*THEN)` `(*MARK:NAME)` `(*:NAME)` | `OUT-OF-SCOPE` | — | these are DEFINED in terms of a backtracking engine's search order — which alternatives to abandon and where to resume. A simulation engine explores all alternatives at once, so there is no backtracking tree to prune. PCRE2's own DFA matcher supports none of them. `(*MARK)` additionally requires reporting state back to the caller |

## Callouts

| syntax | status | becomes | notes |
|---|---|---|---|
| `(?C)` `(?Cn)` `(?C"text")` | `OUT-OF-SCOPE` | — | for now — orthogonal to engine class — PCRE2 supports callouts even in DFA mode. The obstacle is pcrec-specific: generated code has ZERO runtime dependency on pcrec and a fixed `<prefix>_search` contract, and a callout means suspending the scan and calling application code through a defined interface. That is a generated-API change (DD-3) and would tax the hot loop, which D18 puts first. Revisit only with a concrete customer |

## Replacement strings

| syntax | status | becomes | notes |
|---|---|---|---|
| `$1` `${n}` `$<name>` `$&` `` $` `` `$'` `$_` `$+` `$*MARK`, `\l \u \L \U \E` | `OUT-OF-SCOPE` | — | pcrec compiles a MATCHER. It has no substitution API, and APPROACH does not propose one. Listed for completeness because pcre2syntax.html covers it; a substitution layer would be a separate product decision |

---

## How this survey earned its keep

Three findings, all of which existed before the survey and none of which any
test could see.

**1. `\v` was miscompiled, and the oracle agreed with the bug.** PCRE2's `\v` is
vertical whitespace; pcrec decoded it as vertical tab. Measured against
libpcre2 10.46: PCRE2 matches `0x0a 0x0b 0x0c 0x0d 0x85`, pcrec matched `0x0b`
alone — six bytes versus one, inside classes as well as outside. It survived
because python `re`, the base-tier oracle, also reads `\v` as `0x0B`, so
`tests/base/escapes.rxt` asserted the wrong answer and passed. The asymmetry
that gave it away was in the parser itself: `\V` was routed to module `classes`
while `\v` was decoded as a control character — the same construct treated two
different ways, ten lines apart.

The lesson generalises past this one escape: **where python `re` and PCRE2
disagree, a python-verified corpus certifies the divergence instead of catching
it.** That is the argument for the M7 libpcre2 differential work, restated with
a concrete casualty.

**1b. POSIX collating elements were accepted, and PCRE2 rejects them.**
`[[.a.]]` and `[[=a=]]` are collating-element and equivalence-class syntax.
PCRE2 does not implement them and errors out; pcrec compiled them into a class
of literal `[`, `.`, `a` characters — a pattern PCRE2 refuses, given a meaning
PCRE2 never assigns it. python `re` accepts them too (with a FutureWarning), so
again the base-tier oracle could not see it.

The fix was worth doing carefully rather than quickly. The naive reading —
"reject any `[.` inside a class" — over-rejects: PCRE2 only treats it as a
collating element when the matching `.]` terminator actually appears, so
`[.a]`, `[.]`, `[[.]`, `[a[.b]` and `[a.b.]` are ordinary classes that must keep
compiling, and a leading `^` suppresses the rule entirely (`[^.a.]` compiles).
All 18 forms were checked against libpcre2 and pcrec now agrees with it on
every one. The six that must still compile are accept-controls, because
over-rejection is the opposite failure and just as wrong.

**2. The mandate's central guarantee had no test.** "Unsupported constructs
must fail with a clean `requires module 'X'` error, never miscompile" is the
project's core promise, and nothing checked it. It could not live in the .rxt
corpus: a `perr` block requires the python oracle to ALSO fail to compile, and
python accepts `\d`, `\b`, `(?i)` and nearly everything else — so every
module-routed construct was untestable there, and the `# pcre2-only` escape
hatch does not apply because `verify_rxt.py`'s `perr` branch never consults it.

`tests/reject/run_reject_tests.sh` now asserts, per construct, that pcrec exits
exactly 1 (not 0, not a crash), names the expected module, and writes no output
file — 93 constructs, plus 19 accept-controls so the table cannot pass by
rejecting everything. Reproducing the `\v` bug's exact shape on a different
escape (silently decoding `\d` to a literal `d`) fails 2 reject checks and
**zero** corpus and codegen checks.

**Diagnostics fixed while surveying** (all were clean rejections already; none
was a miscompile — they simply failed to name a module, so the caller was told
their syntax was nonsense rather than what would implement it):

| construct | was | now |
|---|---|---|---|
| `(*ACCEPT)`, `(*SKIP)`, `(*CR)`, `(*script_run:…)`, all `(*…)` | `quantifier does not follow a repeatable item` | `(*...) requires module 'verbs'` |
| `\K` | `unknown escape \K` | module `assertions` |
| `\c`, `\o` | `unknown escape` | module `misc` |
| `(?#…)` | module `modifiers` | module `comments` |
| `(?C…)` | module `modifiers` | module `callouts` |
| `(?&name)` | module `modifiers` | module `recursion` |
| `(?\|…)` | module `modifiers` | module `branch-reset` |

## Keeping this current

This report is only worth what its evidence is worth, so update it from
evidence, not from memory:

1. Re-read <https://www.pcre.org/current/doc/html/pcre2syntax.html>. PCRE2 adds
   syntax; a construct absent from this document is invisible to it. Compare
   section-by-section, since the page's own structure is this file's spine.
2. Run `bash tests/reject/run_reject_tests.sh`. Every `REJECTED` row above is
   only true because that table says so — if a row here has no counterpart
   there, it is an assertion, not a status.
3. When a module lands, move its rows from `REJECTED` to `OK`/`OK-LIMITED` and
   add corpus coverage in `tests/<module>/`, then delete its entries from the
   reject table in the same change (a construct cannot be both supported and
   asserted to be rejected — and the reject suite's floor check will notice the
   table shrinking).
4. Any new `DIVERGENCE-PROVEN` row must cite a measurement against libpcre2,
   not a doc reading, and get an entry in `docs/known_issues.md` if it is not
   fixed in the same change.
5. Re-stamp "Last surveyed" and note what moved.

The `PLANNED`/`PLANNED-HARD` split is a judgement about pcrec's architecture,
not a schedule. Treat it as a prediction to be checked the way D18's option
predictions were — and record it here when one turns out wrong.

<!-- BEGIN GENERATED: registry construct index (SR-4) -->

<!-- Generated by tests/registry/compliance_section.py from
     `pcrec --list-syntax`. Do not edit by hand: `make test` fails
     on drift. Add a construct by adding a row to
     src/parse/registry.c, then re-run with --write. -->

## Registry construct index (generated)

Every non-base construct pcrec knows, as the parser itself sees it — 67 rows from one declarative table (D24). The prose sections above carry the analysis; this is the inventory, and it cannot drift from the compiler because it is printed by it.

| doorway | syntax | status | module | engines | PCRE2 semantics |
|---|---|---|---|---|---|
| after `\` | `\d` | `REJECTED` | `classes` | dfa|vm | any decimal digit |
| after `\` | `\D` | `REJECTED` | `classes` | dfa|vm | any character that is not a decimal digit |
| after `\` | `\s` | `REJECTED` | `classes` | dfa|vm | any whitespace character |
| after `\` | `\S` | `REJECTED` | `classes` | dfa|vm | any character that is not whitespace |
| after `\` | `\w` | `REJECTED` | `classes` | dfa|vm | any word character (letter, digit or underscore) |
| after `\` | `\W` | `REJECTED` | `classes` | dfa|vm | any character that is not a word character |
| after `\` | `\h` | `REJECTED` | `classes` | dfa|vm | any horizontal whitespace character |
| after `\` | `\H` | `REJECTED` | `classes` | dfa|vm | any character that is not horizontal whitespace |
| after `\` | `\v` | `REJECTED` | `classes` | dfa|vm | any vertical whitespace character (NOT vertical tab; python re disagrees) |
| after `\` | `\V` | `REJECTED` | `classes` | dfa|vm | any character that is not vertical whitespace |
| after `\` | `\N` | `REJECTED` | `classes` | dfa|vm | any character except newline (PCRE2 forbids it inside a class) |
| after `\` | `\b` | `REJECTED` | `assertions` | dfa|vm | word boundary — but inside a class it is BASE syntax: backspace (0x08) |
| after `\` | `\B` | `REJECTED` | `assertions` | dfa|vm | not a word boundary |
| after `\` | `\A` | `REJECTED` | `assertions` | dfa|vm | start of subject |
| after `\` | `\Z` | `REJECTED` | `assertions` | dfa|vm | end of subject, or before a final newline |
| after `\` | `\z` | `REJECTED` | `assertions` | dfa|vm | end of subject |
| after `\` | `\G` | `REJECTED` | `assertions` | dfa|vm | first matching position in the subject |
| after `\` | `\K` | `REJECTED` | `assertions` | vm | reset the reported start of the match |
| after `\` | `\k<name>` | `REJECTED` | `backrefs` | vm | backreference by name: \k<n> \k'n' \k{n} |
| after `\` | `\g{-1}` | `REJECTED` | `backrefs` | vm | backreference by number or relative position: \g1 \g{-1} \g{name} |
| after `\` | `\p{L}` | `REJECTED` | `unicode-props` | dfa|vm | a character with the given Unicode property |
| after `\` | `\P{L}` | `REJECTED` | `unicode-props` | dfa|vm | a character without the given Unicode property |
| after `\` | `\Q` | `REJECTED` | `quoting` | dfa|vm | begin literal quoting, until \E |
| after `\` | `\E` | `REJECTED` | `quoting` | dfa|vm | end literal quoting begun by \Q |
| after `\` | `\R` | `REJECTED` | `misc` | dfa|vm | any Unicode newline sequence |
| after `\` | `\X` | `REJECTED` | `misc` | dfa|vm | a Unicode extended grapheme cluster |
| after `\` | `\C` | `REJECTED` | `misc` | dfa|vm | one data unit (byte), even in UTF mode |
| after `\` | `\cX` | `REJECTED` | `misc` | dfa|vm | control character: \cX is X xor 0x40 |
| after `\` | `\o{101}` | `REJECTED` | `misc` | dfa|vm | character with the given octal code |
| after `\` | `\0` | `REJECTED` | `backrefs` | dfa|vm | octal escape \0dd — never a backreference (there is no group 0) |
| after `\` | `\1` | `REJECTED` | `backrefs` | vm | backreference to capture group 1 (PCRE2 error 115 if no such group) |
| after `\` | `\2` | `REJECTED` | `backrefs` | vm | backreference to capture group 2 (PCRE2 error 115 if no such group) |
| after `\` | `\3` | `REJECTED` | `backrefs` | vm | backreference to capture group 3 (PCRE2 error 115 if no such group) |
| after `\` | `\4` | `REJECTED` | `backrefs` | vm | backreference to capture group 4 (PCRE2 error 115 if no such group) |
| after `\` | `\5` | `REJECTED` | `backrefs` | vm | backreference to capture group 5 (PCRE2 error 115 if no such group) |
| after `\` | `\6` | `REJECTED` | `backrefs` | vm | backreference to capture group 6 (PCRE2 error 115 if no such group) |
| after `\` | `\7` | `REJECTED` | `backrefs` | vm | backreference to capture group 7 (PCRE2 error 115 if no such group) |
| after `\` | `\8` | `REJECTED` | `backrefs` | vm | backreference to capture group 8 (PCRE2 error 115 if no such group) |
| after `\` | `\9` | `REJECTED` | `backrefs` | vm | backreference to capture group 9 (PCRE2 error 115 if no such group) |
| after `(?` | `(?:...)` | `OK` | — | dfa|vm | non-capturing group |
| after `(?` | `(?=...)` | `REJECTED` | `lookaround` | vm | positive lookahead |
| after `(?` | `(?!...)` | `REJECTED` | `lookaround` | vm | negative lookahead |
| after `(?` | `(?<=...)` | `REJECTED` | `lookaround/named-groups` | vm | lookbehind (?<=...) (?<!...), or named capture group (?<name>...) |
| after `(?` | `(?'name'...)` | `REJECTED` | `named-groups` | vm | named capture group, Perl-style quoting |
| after `(?` | `(?P<name>...)` | `REJECTED` | `named-groups` | vm | python-style named group (?P<n>...), backreference (?P=n), recursion (?P>n) |
| after `(?` | `(?>...)` | `REJECTED` | `atomic-groups` | vm | atomic (non-backtracking) group |
| after `(?` | `(?#...)` | `REJECTED` | `comments` | dfa|vm | comment, discarded up to the next ')' |
| after `(?` | `(?C1)` | `REJECTED` | `callouts` | vm | callout to user code: (?C) (?C1) (?C{text}) |
| after `(?` | `(?\|...)` | `REJECTED` | `branch-reset` | vm | branch reset group: alternatives reuse the same capture numbers |
| after `(?` | `(?(1)a\|b)` | `REJECTED` | `conditionals` | vm | conditional group (?(condition)yes\|no) |
| after `(?` | `(?&name)` | `REJECTED` | `recursion` | vm | recurse into the named group |
| after `(?` | `(?R)` | `REJECTED` | `recursion` | vm | recurse the whole pattern |
| after `(?` | `(?0)` | `REJECTED` | `recursion` | vm | recurse the whole pattern (synonym for (?R)) |
| after `(?` | `(?1)` | `REJECTED` | `recursion` | vm | recurse into capture group 1 |
| after `(?` | `(?2)` | `REJECTED` | `recursion` | vm | recurse into capture group 2 |
| after `(?` | `(?3)` | `REJECTED` | `recursion` | vm | recurse into capture group 3 |
| after `(?` | `(?4)` | `REJECTED` | `recursion` | vm | recurse into capture group 4 |
| after `(?` | `(?5)` | `REJECTED` | `recursion` | vm | recurse into capture group 5 |
| after `(?` | `(?6)` | `REJECTED` | `recursion` | vm | recurse into capture group 6 |
| after `(?` | `(?7)` | `REJECTED` | `recursion` | vm | recurse into capture group 7 |
| after `(?` | `(?8)` | `REJECTED` | `recursion` | vm | recurse into capture group 8 |
| after `(?` | `(?9)` | `REJECTED` | `recursion` | vm | recurse into capture group 9 |
| after `(?` | `(?i)` | `REJECTED` | `modifiers` | dfa|vm | inline option setting or scoping: (?i) (?im-sx:...) (?^) (?-i) |
| after `(*` | `(*...)` | `REJECTED` | `verbs` | vm | backtracking verb ((*SKIP), (*ACCEPT)), start-of-pattern option ((*CR), (*UTF)) or script run ((*script_run:...)) |
| after `[` in a class | `[[:alpha:]]` | `REJECTED` | `classes` | dfa|vm | POSIX character class |
| after `[` in a class | `[[.a.]]` | `AGREES-REJECT` | — | — | POSIX collating element — PCRE2 rejects it, and so must we |
| after `[` in a class | `[[=a=]]` | `AGREES-REJECT` | — | — | POSIX equivalence class — PCRE2 rejects it, and so must we |

<!-- END GENERATED -->
