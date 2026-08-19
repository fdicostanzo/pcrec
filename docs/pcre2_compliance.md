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
| `OK-LIMITED` | Supported, correct within a limit stated in the row — and the row must name the limit's KIND: a RESOURCE cap (correct until a measured size, then a clean failure), or a CAPABILITY not yet built (part of the construct's contract unimplemented). A speed-only caveat is not a limit; it stays `OK` with the caveat in the note (DOC-1, 2026-08-11 — the value had accreted three unrelated meanings) |
| `OK-GATED` | Built and oracle-verified (corpus + PC-4's 62,872-cell live differential), but compiled ONLY under an explicit `--features` naming it (the module itself, or a named set that includes it) — NOT reachable via the bare default. Added 2026-08-12 when module `classes` shipped the first producers, when the bare default was still empty; **as of [STD1b] (`ab7592d`, 2026-08-13, D37) the bare default maps to the frozen named set `std1` = {`classes`, `modifiers`}**, so those two modules' rows graduated to plain `OK` — see the Headline. `OK-GATED` remains the correct status for a built module OUTSIDE the current bare-default set (e.g. a future graduate whose named set has not yet become the bare-default mapping per D37's announced-boundary rule); `--features none` still refuses every gated construct with the module name exactly as `REJECTED` describes |
| `REJECTED` | Not supported. Exits 1 with `requires module 'X'`, writes no output, never miscompiles. Pinned construct-by-construct by `tests/reject/` |
| `AGREES-REJECT` | PCRE2 rejects it too, and pcrec rejects it the same way. Refusing the pattern IS compliance here — not a gap |
| `OUT-OF-SCOPE` | Deliberately excluded, with the reason |
| `DIVERGENCE` | An OPEN measured difference from libpcre2. Currently none: the two ever found were fixed on 2026-08-09 and their rows say so |

| becomes | meaning |
|---|---|
| `—` | no plan; the status is the end state. A row's note may still record a revisit TRIGGER — a condition under which the question reopens — which is not a plan and does not change the value (DOC-1, 2026-08-11: three OUT-OF-SCOPE rows carry such triggers, and the column and note were read as contradicting) |
| `PLANNED` | a named module/milestone owns it, no known architectural obstacle |
| `PLANNED-HARD` | owned, but the architecture makes it genuinely difficult — needs the M4 VM engine, or fights the D7 two-pass DFA design. Reason per row |
| `never` | generated index only: the registry's `ROADMAP_NEVER` — real PCRE2 syntax pcrec deliberately excludes, which no module will ever implement, and whose diagnostic says so instead of promising one (K14). Synonymous with a hand-table `OUT-OF-SCOPE`/`—` pairing, rendered from the row so it cannot drift (DOC-1: the value was in use, undefined here) |

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
  alternation, groups, `^`, `$`, the character escapes) is `OK`, with 876
  corpus cases at 100% oracle agreement (844 of them python-verified; the rest
  are `# pcre2-only` blocks checked against libpcre2 directly).
- Modules `classes` and `modifiers` shipped `OK-GATED` on 2026-08-12 (built
  and oracle-verified, compiled only under `--features classes` or
  `--features modifiers`); as of [STD1b] (`ab7592d`, 2026-08-13, D37) both
  are `OK` — the bare default
  now maps to the frozen named set `std1` = {`classes`, `modifiers`}, so a
  bare `pcrec` compiles their constructs with no flag needed. `--features
  none` is the only invocation that still refuses them, with the module name.
- Everything else is `REJECTED` — measured live at this commit (`ab7592d`+,
  [STD1b], 2026-08-13) from `tests/reject/run_reject_tests.sh`'s own summary,
  not transcribed: **274** hand-written rows individually assert exit 1 and
  the right diagnostic (most name a module; some — the base-grammar brace
  errors K5/K6/K8, the verb doorway's outcomes, the `unknown escape` pins —
  name a PCRE2-flavoured wording instead, and offsets are pinned where a
  message alone cannot distinguish sites), **99** accept-controls proving the
  table cannot pass by rejecting everything, **55** `reject_gated` pins
  asserting the still-refused-under-`--features none` half for constructs
  whose bare-default refusal changed at [STD1b] (D37), and (SR-4) **99**
  further checks that iterate `pcrec --list-syntax` so no registry row can
  escape a probe (`tests/reject/`) — **528** checks passing, **0**
  known-wrong. **This paragraph previously cited 144/45/66: those figures
  were already stale independent of the STD1b flip — `tests/reject/CLAUDE.md`'s
  own count history records several unrelated intermediate values this
  survey never caught up to (the file's own maintenance note: "read them
  from a run, never from here"). What is written above is a fresh whole-suite
  measurement, not a same-category update of the old numbers.** The two
  layers (hand-written and iterated) answer different questions and neither
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
| whitespace inside `{ }` in `\g{2}` etc. | `REJECTED` | — | reached only via constructs that are themselves rejected. **This row's scope was too narrow and its dismissal was wrong for the case that mattered** (R7): the REPEAT quantifier is base-tier and very much reached, and pcrec silently compiled `a{ 1}` as literal text until K8. See the Quantifiers section |
| `\u{...}` (ALT_BSUX) | `OUT-OF-SCOPE` | — | an ECMAScript-compatibility spelling gated on a PCRE2 option pcrec does not model |

## Escaped characters

| syntax | status | becomes | notes |
|---|---|---|---|
| `\a` `\e` `\f` `\n` `\r` `\t` | `OK` | — | each verified byte-for-byte against libpcre2 during this survey |
| `\xhh` | `OK` | — | 1–2 hex digits; `digits missing after \x` matches PCRE2 error 178 |
| `\x{hh..}` | `REJECTED` | — | module `unicode-props` |
| `\cx` | `REJECTED` | — | module `misc`. Trivially implementable; base tier simply does not include it |
| `\0dd`, `\ddd` as an ATOM | `REJECTED` | — | module `backrefs` — PCRE2 resolves octal-vs-backreference by context, so they share an owner |
| `\0dd`..`\ddd`, `\8` `\9` `\g` `\k` INSIDE A CLASS | `OK` | — | **FIX-3 (K13), 2026-08-11.** A backreference is impossible inside a class, so PCRE2 falls back and pcrec now agrees: `\0`..`\7` open an octal escape (up to three octal digits; above `\377` it is PCRE2 error 151, wording and offset reproduced), `\8` `\9` `\g` `\k` are the LITERAL characters (the complete fallback set over all 62 `[\c]` probes), tails re-enter as members (`[\k<n>]` matches k `<` n `>`), and decoded escapes are ordinary range endpoints (`[0-\k]`, `[\1-\7]`). Measured cell-by-cell against libpcre2 10.46 — tests/probes/probe_fix3.c, 41 cells, zero disagreements; pinned by tests/base/class_escape_fallbacks.rxt (127 cases) and the `[\400]`/`[\377]` boundary rows in tests/reject/. Until this change all twelve answered "requires module 'backrefs'" here — the K13 over-promise |
| `\o{ddd..}` | `REJECTED` | — | module `misc` |
| `\N{U+hh..}` | `REJECTED` | — | module `unicode-props` — the registry's answer, which is authoritative (this row said `classes` until DOC-1, 2026-08-11, contradicting the generated index below; the pointer it gave to a "note under Character types" pointed at a note that did not exist — it does now) |
| `\U`, `\uhhhh` (ALT_BSUX) | `OUT-OF-SCOPE` | — | option-gated compatibility spellings |

## Character types

| syntax | status | becomes | notes |
|---|---|---|---|
| `.` | `OK` | — | excludes `\n` only, PCRE2's default. `(?s)` dotall is `OK` by default since [STD1b] (module `modifiers`, MOD-0.5c; still refused under `--features none`) |
| `\d \D \s \S \w \W \h \H \V \N` | `OK` | — | module `classes` SHIPPED THESE 2026-08-12 (MOD-0.3): both positions, negation as the probe-asserted complement. Default-on since [STD1b] (`ab7592d`, 2026-08-13): `classes` is in the bare-default named set `std1` (D37), so a bare `pcrec` compiles these with no flag; `--features none` still refuses with the module name, and `--features classes`/`--features std1` are unchanged. Oracles: tests/classes/, PC-4. **The `\N` spelling clash** (the note the Escaped-characters table references): `\N` here is the BARE form only — "any character except newline", a class-shaped predicate owned by `classes`. `\N{U+hh..}` is a DIFFERENT construct (a code point by number, module `unicode-props`; K10 recorded the `[\N{U+41}]` class-position divergence, FIXED 2026-08-12 by MOD-0.6 — see docs/dev/known_issues.md K10), and `\N{name}` is real PCRE2 syntax pcrec will never implement (`never`). Three meanings on one selector byte, resolved by the registry's tails — which is why the two `\N{` rows sit in the registry SHORTEST-tail-first (SR-9's precedence rule) |
| `\v` | `REJECTED` | `PLANNED` | **Was a proven divergence, fixed 2026-08-09.** PCRE2 defines `\v` as vertical WHITESPACE (`0x0a 0x0b 0x0c 0x0d 0x85`, measured against libpcre2 10.46); pcrec decoded it as vertical tab `0x0B` only, inside classes as well as outside. Now `REJECTED` to module `classes` like its negation `\V`. It survived because python `re` also reads `\v` as `0x0B`, so the base-tier oracle agreed with the bug — see "How this survey earned its keep" |
| `\C` | `REJECTED` | `PLANNED` | "one code unit". In the ASCII tier that is just "any byte", i.e. trivial. PCRE2 forbids it under its own DFA matcher in UTF modes for the reason that will apply to us in M5 |
| `\p{..}` `\P{..}` | `REJECTED` | — | module `unicode-props`, M5. Single-position predicates, so DFA-friendly; the work is Unicode tables, not engine |
| `\R` | `REJECTED` | `PLANNED` | module `misc`. Not a single character — a small alternation of literal sequences (CR, LF, CRLF), so still regular and `PLANNED`-feasible |
| `\X` | `REJECTED` | `PLANNED-HARD` | extended grapheme cluster: variable-length, Unicode-table-driven segmentation. Regular in principle, substantial in practice. M5 at the earliest |

## Unicode properties (general category, PCRE2 special, binary, script, bidi)

**A RULED, deliberate tier-2 divergence (K16, D26; Frank, 2026-08-12):**
libpcre2 treats 164 of 256 possible `\p{...}` BODY bytes (`!"#$%`, `{|~`,
DEL, most C0 controls, every byte ≥ 0x80) as malformed the instant they
appear — error 146 at the bad byte, before the name scan continues and
regardless of the 128/48 caps — where pcrec's MOD-0.6 scanner reads past
them as ordinary name characters and refuses in its own
unknown-name/generic category at its scan-completion offset. Both engines
refuse every such pattern and the module attribution is identical, which is
what keeps this tier 2. Found by R19's engine critic
(docs/dev/reviews/2026-08-12-r19-mod06.md); recorded at docs/dev/known_issues.md
K16 with the full byte census; fix deferred to the first `unicode-props`
producer, when the scanner is remeasured anyway. The reject pins for
`\p{!}`/`\p{9}`/`\p{=}` claim pcrec's own current behavior, not oracle
agreement, until then.

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
| `[[:alpha:]]`, `[[:^alpha:]]` and the 14 POSIX names | `OK` | — | module `classes` SHIPPED THESE 2026-08-12 (MOD-0.3): all 14 names, both polarities. Default-on since [STD1b] (`ab7592d`, 2026-08-13): `classes` is in the bare-default named set `std1` (D37); `--features none` still refuses with the module name (`[[:<:]]`/`[[:>:]]` are assertions, module `assertions`, still refused in every configuration — not in `std1`). Oracles: tests/classes/ (every name pinned without libpcre2 since R16), PC-4 |
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
| space/tab inside `{m,n}`, `a{ 1}` | `OK` | — | PCRE2 (following Perl 5.34) skips 0x20 and 0x09 in each of the four gaps `{`_m_`,`_n_`}`, and no other byte. **Was a MISCOMPILE until 2026-08-10 (K8)** — silently literal text, and invisible to a verdict comparison because both engines accept in quantifier position. Whitespace never joins digits (`a{1 2}` is literal) nor stands in for a number (`a{ }`, `a{ , }` stay literal). Found by R7's spec critic, not by the 49 probes that certified K5/K6 |
| brace diagnostic PRECEDENCE | `OK` | — | measured, not assumed: in atom position PCRE2 answers 105 for `{65536}` and 104 for `{3,1}`, not 109; and too-big beats out-of-order, so `a{65536,1}` is 105. pcrec agrees on all three, offsets included |
| large bounded repeat, `a{0,65535}` | `OK-LIMITED` | `PLANNED` | limit kind: RESOURCE cap. **K7, fixed 2026-08-18 ([M4.7b]); this row previously made two claims that were wrong as written, corrected here.** The BOUNDED-OPTIONAL form is correct up to the NFA size cap and refuses above it in ~0.1 s and ~11 MB (bisected: `a{0,31999}` compiles, `a{0,32000}` refuses; `a{0,20000}` compiles at 13 MB; `a{0,65535}` refuses on the 131072-state NFA cap). The EXACT-COUNT form is correct to `a{9795}` (bisected; `a{9796}` refuses) and refuses above it on the subset-element bound (`a{65535}`: 216 MB, 0.9 s). Neither form can exhaust memory or abort a caller any more, and a compile under a caller-set memory limit now reports "out of memory compiling this pattern" rather than killing the caller's process. Not a miscompile; no wrong code is emitted, and no pattern that compiled before this fix compiles to different bytes after it. **The two corrected claims, kept visible because the doc's own vocabulary is what made them wrong:** (1) this row said "limit kind: RESOURCE cap", which the table at the top of this file defines as "correct until a measured size, THEN A CLEAN FAILURE" — the defining property K7 was filed for not having, so the row asserted a category it did not meet; (2) it said the process "is SIGKILLed", which was true only with no limit set — under a caller's limit it SIGABRTed, and the difference matters because a caller who set a limit is exactly the caller the row was describing. A third statement, "`a{65535}` does hit the cap cleanly", was true in verdict but reached that verdict after 2.1 GB and 12.3 s, which is not what "cleanly" means anywhere else in this document |

## Anchors and simple assertions

| syntax | status | becomes | notes |
|---|---|---|---|
| `^` | `OK` | — | start of subject, accepted and correct in every position (probed at class open, mid-pattern, and per alternation branch — DOC-1, 2026-08-11, which found the old `OK-LIMITED` stating no limit; the multiline gap it gestured at is `$`'s too and both rows now carry it the same way). Multiline `^` is `REJECTED` — since MOD-0.5c the gate-open answer names module `assertions` per-letter (the MOD-0.5a ruling); the DFA-state-context design for it is DD-6. One SPEED caveat, not a correctness limit: unanchored patterns with `^` in some branches stay on the slower ENG_ATTEMPT engine until DD-7's unification (D8) |
| `$` | `OK` | — | end of subject or before a final newline — PCRE2's default. Mid-pattern `$` is fully general via EOL-variant states |
| `\A \Z \z` | `OK` | — | module `assertions` SHIPPED THESE 2026-08-19 ([M6.2] wave A), behind the gate: `--features assertions` compiles them, a bare invocation still refuses by name (`assertions` is not in the bare-default set `std1`). `\A` and `\Z` turned out to be EXACT ALIASES of the `^`/`$` nodes pcrec has shipped since M1 — pcrec's own node comments are PCRE2's definitions word for word — so they cost no engine work at all (measured, 1,008 differential cells / 0 disagreements). `\z` is genuinely stronger than `\Z` and needed a third closure view, interned only where it differs from the EOL view, so a `\z`-free pattern's artifact is byte-identical (gated: tests/codegen/run_endvar_identity.sh). Oracle note: python `re` is the WRONG oracle for `\Z` (its `\Z` is PCRE2's `\z`) — tests/assertions/ carries its own libpcre2 verifier, U11 |
| `\b \B \G` | `OK` | — | module `assertions` SHIPPED THESE 2026-08-19 ([M6.2] waves B and D), behind the gate, and this row is CORRECTED — it said `REJECTED` and described the work as pending for two waves after those waves landed. `\b`/`\B` cost a byte-equivalence-class refinement, a bit of DFA state identity, a class-indexed accept and runtime start-state seeding from a byte OUTSIDE the search window at `startpos > 0` (assertions_design.md §3.8, whose reverse TERMINATION half was a lost-match defect found by the R30 re-check). `\G` cost a third closure bit, a second interior start-state family and a three-way start dispatch — and did NOT need DD-4's wrap toggle, because ENG_ATTEMPT already emits the un-self-looped shape and `\G` is `start_max = startpos`. Oracles: tests/assertions/wordb.rxt and gpos.rxt (the latter `# pcre2-only` in its entirety — python has no `\G` at all, U11c) |

## Reported match point setting

| syntax | status | becomes | notes |
|---|---|---|---|
| `\K` | `OK` | — | module `assertions` SHIPPED THIS 2026-08-19 ([M6.2] wave E, the module's last construct), behind the gate. **VM-ONLY, and the old `PLANNED-HARD` reasoning on this row was RIGHT ABOUT THE OBSTRUCTION AND WRONG ABOUT THE SHAPE.** It said `\K` "interacts directly with the reverse machine". It does not: `\K` changes no LANGUAGE, so `src/ir/nfa.c` lowers it to an epsilon and the capture-erased prefilter built for `a\Kb` is the machine `ab` builds — which is exactly what the hybrid needs, since the prefilter's span start is then the PRE-`\K` start and is used only to bound the search. The real obstruction is narrower: the reported position is a property of the WINNING PATH and a subset state is a priority-ordered SET, which does not carry one. A tagged DFA (Laurikari) recovers exactly such positions; pcrec's is not one and this is recorded as closed BY CHOICE rather than by mathematics (assertions_design.md §6.1, R30 E7). PCRE2 likewise does not support `\K` in its own DFA matcher. So a `\K` pattern is VM-forced (the second `forces_*` row in src/opt/select_engine.c) and `--engine=dfa` REFUSES it by name rather than silently downgrading (D44.6). The write is a trailed capture write to group 0's start slot, so a `\K` crossed on a path that then LOSES is undone: `(?:a\K|ax)c` on "axc" is (0,3). Oracle: tests/assertions/kreset.rxt, `# pcre2-only` in its entirety — python has no `\K` at all and a lookbehind is not a translation of it (U11d) |

## Alternation, capturing, atomic groups

| syntax | status | becomes | notes |
|---|---|---|---|
| `a\|b` | `OK` | — | incl. empty branches; leftmost-first preference via priority pruning (D3) |
| `(...)` | `OK-LIMITED` | — | limit kind: CAPABILITY not yet built. Parses and groups correctly, but capture SPANS are not reported — only the overall match. Captures arrive with the M4 VM engine |
| `(?:...)` | `OK` | |
| `(?<name>...)` `(?'name'...)` `(?P<name>...)` | `OK-GATED` | — | module `named-groups`, SHIPPED 2026-08-18 ([M6.3]): all three declaring spellings parse and capture as their group number (opening-paren order, exactly as an unnamed group — including under `(?n)`, which suppresses a PLAIN group's number but NOT a named one's, measured). `rx_info.groups` is populated, sorted by NAME (strcmp, byte-exact and case-sensitive — "name"/"NAME" are two distinct groups, even under `(?i)`, measured both oracles) — PCRE2's own `PCRE2_INFO_NAMETABLE` is sorted the identical way, measured directly (tests/probes/probe_named_groups.c), which is this module's own evidence for the sort key docs/spec/match_api.md §6 had left open (fixed only for today's ref-empty rows — see D59). A duplicate name is a compile error (PCRE2 error 143, no DUPNAMES); `(?J)`/DUPNAMES itself stays OUT OF SCOPE — see its own row below. Backreference-BY-NAME spellings (`\k<n>` `\k'n'` `\k{n}` `(?P=n)`) stay module `backrefs`, unaffected — Since Q2/SR-9 `(?<` names ONLY this module at the DECLARING position: the three lookbehind tails `=` `!` `*` have rows of their own. `--features none` (the bare default) still refuses with the module name; `--features named-groups` compiles. Oracles: tests/named_groups/ |
| `(?>...)`, `(*atomic:...)` | `REJECTED` | `PLANNED-HARD` | module `atomic-groups` / `verbs`. Same reasoning as possessive quantifiers: a cut, not a no-op |

## Comment

| syntax | status | becomes | notes |
|---|---|---|---|
| `(?#....)` | `REJECTED` | `PLANNED` | module `comments` (previously misattributed to `modifiers`; fixed in this survey). Pure lexing, `PLANNED`-trivial |

## Option setting

| syntax | status | becomes | notes |
|---|---|---|---|
| `(?i)` `(?i:...)` `(?-i)` | `OK` | — | module `modifiers` SHIPPED THESE 2026-08-12 (MOD-0.5c): the D23 fold driven by scoped parse state (`cx->mods`), the measured 17/17 group-scope rule (leaks across sibling branches, restored at the enclosing `)`). Default-on since [STD1b] (`ab7592d`, 2026-08-13): `modifiers` is in the bare-default named set `std1` (D37); `--features none` still refuses with the module name, `--features modifiers`/`--features std1` unchanged. Oracles: tests/modifiers/, spec_mod0 check12 |
| `(?s)` dotall | `OK` | — | module `modifiers` SHIPPED 2026-08-12 (MOD-0.5c): `.` census 255 -> 256, measured against the oracle. Default-on since [STD1b] (`ab7592d`, 2026-08-13, D37 `std1` set); `--features none` still refuses with the module name |
| `(?m)` multiline | `OK` | — | module `assertions` SHIPPED THIS 2026-08-19 ([M6.2] wave C). MOD-0.5a's ruling held: `^`/`$` at internal newlines IS assertion-engine work, so the letter is produced by module `modifiers`' option run and attributed to `assertions`, and needs BOTH enabled (`--features assertions,modifiers`; `modifiers` is default-on under `std1`, `assertions` is not, so a bare invocation still refuses by the letter's own name). Scoped by construction: `(?m)` is resolved AT PARSE TIME onto the `^`/`$` node (D62, `Ast.multiline`), so `(?m:...)`, `(?m)...(?-m)` and a mid-pattern `(?m)` are right without any downstream pass re-deriving scope — and the SCOPED cells are the ones D47.5's own wording did not ask for and the pre-cure code got wrong. `\A`/`\Z`/`\z` are UNAFFECTED under `(?m)`, PCRE2's own rule. **`(?m)^` is NOT the mirror of `(?m)$`**: PCRE2's multiline `^` does not match after a newline that ENDS the string (python3 `re`'s does — upstream_issues.md U11b, found here as a live defect first). `(?-m)` remains an accepted no-op. Oracles: tests/assertions/multiline.rxt (both oracles, 2,700+ cells), tests/assertions/run_mline_diff.sh (a generated sweep against libpcre2 on both engines) |
| `(?x)` `(?xx)` extended | `OK` | — | module `modifiers` SHIPPED THESE 2026-08-12 (MOD-0.5d): skip set {09,0A,0B,0C,0D,20,85} (NOT `\s`'s set — NEL is skipped), `#`-comments to 0x0A only (the NEWLINE_LF convention), xx's class-interior {09,20} deletion ahead of the endpoint rule (the D30 §7 `(?xx)[a- ]` hazard, now compiled correctly), doubled-x ADJACENCY rule incl. the later-bare-x downgrade — every clause probe-measured (probe_mod05*.c). Default-on since [STD1b] (`ab7592d`, 2026-08-13, D37 `std1` set); `--features none` still refuses with the module name |
| `(?U)` ungreedy | `OK` | — | module `modifiers` SHIPPED 2026-08-12 (MOD-0.5c): default greed inverted at quantifier construction, `?` re-inverts; NOT reset by `(?^)` (measured). Default-on since [STD1b] (`ab7592d`, 2026-08-13, D37 `std1` set); `--features none` still refuses with the module name |
| `(?n)` no-auto-capture | `OK` | — | module `modifiers` SHIPPED 2026-08-12 (MOD-0.5c): plain `(` stops counting (`--count-groups` oracle-tied via check02's channel); does NOT imply J (measured). Default-on since [STD1b] (`ab7592d`, 2026-08-13, D37 `std1` set); `--features none` still refuses with the module name |
| `(?J)` dup names | `REJECTED` | `planned` | Per-letter attributed to module `named-groups` (duplicate NAMES are named-group semantics — the same dispatch logic `(?m)` already uses for `assertions`), MOD-0.5a's original ruling ("J is observable only through named groups") — [M6.3] (2026-08-18) briefly moved this to a K14 OUT-OF-SCOPE reading and then RULED it back: `docs/pcre2_options.md`'s `PCRE2_DUPNAMES` row is `RIDES(M4/captures)`, RATIFIED D38, a PLANNED-LATER disposition, not NEVER — (?J) does not meet K14's "architecturally out of scope per the survey" bar. The letter refuses UNCONDITIONALLY, gate open or closed, naming its true owning module WITHOUT the false "requires" framing ("module 'named-groups' does not implement duplicate group names" — "requires module 'named-groups'" would read as "enabling it fixes this", which named-groups shipping (without dupnames) disproved); `(?-J)` accepted no-op. Pin: tests/reject/ reject_gated |
| `(?a)` `(?aD)` `(?aS)` `(?aW)` `(?aP)` `(?aT)` `(?r)` | `OK` | — | MEASURED NO-OPS at options=0 C locale (probe_mod05.c: `(?ri)` vs `(?i)` 0 diff cells over 256x256; all four a-sub pairs census-identical) — accepted and applied as nothing, which is exactly PCRE2's observable behaviour in this mode. They become real under UTF/UCP: MOD-0.6/M5 own that day (DD-12). Default-on since [STD1b] (`ab7592d`, 2026-08-13, D37 `std1` set); `--features none` still refuses with the module name |
| `(?^)` reset options | `OK` | — | module `modifiers` SHIPPED 2026-08-12 (MOD-0.5c): resets i,m,n,s,x,xx to the HARDWIRED defaults; U and J SURVIVE — "unset imnsx" is the measured rule, and the reset is to-constant, not to-compile-option (both from probe_mod05b.c). Default-on since [STD1b] (`ab7592d`, 2026-08-13, D37 `std1` set); `--features none` still refuses with the module name |
| `(*LIMIT_DEPTH=)` `(*LIMIT_HEAP=)` `(*LIMIT_MATCH=)` `(*LIMIT_RECURSION=)` | `OUT-OF-SCOPE` | — | these bound a BACKTRACKING search. pcrec is O(n) by construction, so there is nothing to limit. D22 also removes the adversarial-input motivation. `LIMIT_RECURSION` is PCRE2's older synonym for `LIMIT_DEPTH` — it was in pcrec's verb tables but missing from this row until the K14 check compared them (2026-08-11) |
| `(*NO_JIT)` `(*NO_START_OPT)` `(*NO_AUTO_POSSESS)` `(*NO_DOTSTAR_ANCHOR)` | `OUT-OF-SCOPE` | — | knobs for PCRE2 implementation internals that pcrec does not have |
| `(*NOTEMPTY)` `(*NOTEMPTY_ATSTART)` | `REJECTED` | `PLANNED` | match-time semantics, expressible; no owner yet |
| `(*UTF)` `(*UCP)` | `REJECTED` | `PLANNED` | module `verbs`; the underlying capability is M5 |
| `(*CASELESS_RESTRICT)` `(*TURKISH_CASING)` | `OUT-OF-SCOPE` | — | for the ASCII tier — revisit with DD-1's Unicode work |

**A RULED, deliberate tier-2 divergence (D26; manager ruling 2026-08-12,
MOD-0.8c): the per-letter MODULE GATE answers before the option run's own
VALIDITY check.** An option run that is BOTH invalid as a run AND contains a
letter pcrec defers to another module is reported as the deferral, not as the
invalidity:

    $ build/pcrec --features modifiers -o - '(?m--)'
    pcrec: inline option 'm' (multiline) requires module 'assertions'
    libpcre2 10.46: error 194, "invalid hyphen in option setting"

`(?i--)`, whose letters are all implemented, IS diagnosed as the malformed run
it is — so the ordering is only observable through a deferred letter. At
measurement time (2026-08-12) that was exactly two letters, `m` (→
`assertions`) and `J` (→ `named-groups`) — both still true after [M6.3]
(2026-08-18): `J`'s wording moved (twice, same day — see the `(?J)` row
above) but it still names `named-groups` as its owning module, so both
letters remain MODULE-shaped deferrals, just with `J`'s phrasing avoiding
the false "requires" framing (`named-groups` IS enabled once this
diagnostic is reachable; enabling it again would not fix anything).

**Why this is tier 2 and not tier 1.** Both engines REFUSE, and neither emits
anything: what differs is which REFUSAL CATEGORY the user is told about, which
is the same distinction that keeps K15 at tier 2. Nothing miscompiles, no
pattern changes meaning, and pcrec's answer is not false — `(?m--)` genuinely
does need module `assertions` before it could ever compile. It is simply the
less useful of two true sentences, and D26 puts diagnostic category for a
construct pcrec has not implemented outside the exact tier.

**MEASURED 2026-08-12** (re-measured for this entry, not transcribed from the
report that found it):

- Over `tests/spec_mod0/check14_option_runs.c`'s generated space: **286
  deferred cells of 4,385 compared — 189 by letter, 97 by doorway byte.**
  That is every deferral, of which the ordering divergence is the subset
  landing on an invalid run.
- Over PC-3's own option-run space (19,448 cells: the Q2 alphabet, runs of
  length 0-3, both terminator shapes), **14,986 cells are runs libpcre2 calls
  invalid** (error 111 or 194). Of those, pcrec diagnoses 14,844 as invalid and
  DEFERS on **142** at the closed gate — all to `modifiers`, the
  row-level deferral before the run is ever read — and diagnoses 14,978 and
  defers on **8** with the gate open (4 to `assertions`, 4 to `named-groups`:
  `(?m--)`, `(?m--:a)`, `(?^m-)`, `(?^m-:a)` and the `J` equivalents). Nothing
  is accepted in either state. **"Closed gate" here meant the bare default at
  measurement time (2026-08-12), when the bare default was empty; since
  [STD1b] (`ab7592d`, 2026-08-13, D37 `std1` = {`classes`, `modifiers`}) the
  BARE default reproduces the 8-cell gate-open figures for `modifiers`
  letters (verified live: bare `(?m--)` and `--features modifiers '(?m--)'`
  both give `requires module 'assertions'`) — only `--features none`
  reproduces the original 142-cell closed-gate figure now.**

**The population still shrinks toward zero, and [M6.3] changed WHICH event
closes the `J`-half, not whether it closes.** 142 → 8 is what opening the
gate already does: every letter whose module lands and VALIDATES the
letter stops deferring. `m`'s 4 cells close when `assertions` lands. `J`'s
4 cells DO NOT close when `named-groups` (the module already shipped,
2026-08-18) lands a producer — they close only when a FUTURE dupnames
producer lands inside it (`docs/pcre2_options.md`'s `PCRE2_DUPNAMES` row,
RIDES(M4/captures), RATIFIED D38 — so this is a real, scheduled-later
event, not the settled-forever state a same-day intermediate draft of
this entry briefly recorded). Until then `J`'s cells keep deferring, with
the true-owning-module wording the `(?J)` row above states.

**REVISIT TRIGGER**, therefore, is TWO events, not one: re-measure when
`assertions` lands and delete the `m`-half of this entry when its
open-gate count reaches zero; re-measure when a dupnames producer lands
inside `named-groups` and delete the `J`-half the same way. Re-ordering
the check so run validity is decided before the module gate was
considered and NOT taken: it would move a grammar decision ahead of the
gate for a benefit that expires on its own, and the option-run grammar is
one home (`mod_modifiers.c`) precisely so the doorway does not acquire a
second copy of it.

Found by the MOD-0.8b D27 blinded writer (recorded in
`docs/dev/reviews/2026-08-12-r20-mod08.md` as SPEC divergence 2) and ruled
document-don't-reorder. **No K row**: `docs/dev/known_issues.md` is for confirmed
BUGS deferred rather than fixed, and this is a ruled category divergence with a
self-closing population — the same treatment shape as this file's K15 and K16
paragraphs, minus the defect.

## Newline convention and `\R`

| syntax | status | becomes | notes |
|---|---|---|---|
| `(*CR)` `(*LF)` `(*CRLF)` `(*ANYCRLF)` `(*ANY)` `(*NUL)` | `REJECTED` | `PLANNED` | module `verbs`. Newline convention is a compile-time parameter affecting `$`, `.` and `\R` — exactly the kind of thing D18 says should be hyperspecialized away |
| `(*BSR_ANYCRLF)` `(*BSR_UNICODE)` | `REJECTED` | `PLANNED` | same, scoped to `\R` |

## Lookaround

| syntax | status | becomes | notes |
|---|---|---|---|
| `(?=...)` `(?!...)` | `REJECTED` | `PLANNED-HARD` | module `lookaround`. Lookahead is automaton intersection — feasible, not cheap, and it multiplies states |
| `(?<=...)` `(?<!...)` | `REJECTED` | `PLANNED-HARD` | module `lookaround`. Fixed-length lookbehind is tractable via the reverse machine D7 already builds; variable-length is much harder |
| `(*pla:)` `(*nla:)` `(*plb:)` `(*nlb:)` verbose spellings | `REJECTED` | — | module `verbs`; same underlying feature |
| `[[:<:]]` `[[:>:]]` | `REJECTED` | `PLANNED` | module `assertions` since MOD-0.3a (2026-08-12; the split the earlier text assigned to whoever implemented the doorway) — they are NOT character classes but zero-width WORD BOUNDARY assertions PCRE2 inherited from its Unix ancestry, measured on "abc def" (`[[:<:]]def` matches [4,7), `abc[[:>:]]` matches [0,3)); `^` does not negate them. Found by PC-3's generated name differential (FIX-2), not by reading. **And they are POSITION-RESTRICTED (R9/C3-4):** libpcre2 accepts them ONLY as a class's ENTIRE content, so `[[:<:]]` compiles while `[x[:<:]]`, `[[:<:]a]` and even `[^[:<:]]` are all error 130 — unlike every ordinary POSIX name, which works in any position. pcrec promised module `classes` for all of those until R9; it now answers "unknown POSIX class name", and `check_posix_positions` in tests/registry/ crosses name against position, which is the axis pair neither earlier differential varied |
| `(?*...)` `(?<*...)` `(*napla:)` `(*naplb:)` non-atomic lookaround | `REJECTED` | `PLANNED-HARD` | module `lookaround`. The non-atomic variants are defined by their backtracking behaviour. **This row was RIGHT and the registry was WRONG** until R8/C4-8: `(?*...)` had no registry row, so the `(?` catch-all answered "requires module 'modifiers'" for it. Three homes, one disagreeing — the `\v` shape exactly, and found the same way, by reading an outside source rather than by any test |

## Substring scan, script runs

| syntax | status | becomes | notes |
|---|---|---|---|
| `(*scan_substring:...)` `(*scs:...)` | `OUT-OF-SCOPE` | — | (revisit post-M4) — re-matches against previously CAPTURED text, so it needs capture state at match time |
| `(*script_run:...)` `(*sr:...)` `(*atomic_script_run:...)` `(*asr:...)` | `REJECTED` | — | module `verbs`. Needs Unicode script data (M5); the assertion itself is regular |

## Backreferences

| syntax | status | becomes | notes |
|---|---|---|---|
| `\1` `\g1` `\g{n}` `\g{+n}` `\g{-n}` `\k<n>` `\k'n'` `\k{n}` `(?P=n)` | `REJECTED` | `PLANNED-HARD` | module `backrefs`. **Backreferences are not a regular language** — no DFA can do them, and PCRE2's own DFA matcher does not. They need the M4 VM engine plus capture state. Note also D23's boundary: a CASELESS backreference compares subject text to subject text, which cannot fold into the automaton and needs a match-time comparison. All ATOM position: inside a class these spellings are not backreferences at all — octal or literal fallback, supported since FIX-3 (K13); see Escaped characters. The module, when it lands, must not touch the class position |

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

**Since Q1 (2026-08-10, D25) the `(*` doorway distinguishes NAMES.** Everything
in this section is still `REJECTED`, but a name PCRE2 does not have is now told
so — `(*NOTAVERB)` gets PCRE2's own "(*VERB) not recognized or malformed"
instead of a promise that module `verbs` will one day implement it. The
distinction runs deeper than the table below shows: PCRE2 keeps TWO name tables
selected by the CASE of the first byte, with a different error for each, and its
argument rules are PER-NAME (`(*ACCEPT:x)` compiles, `(*CR:x)` does not,
`(*MARK)` alone is an error, `LIMIT_*` takes `=digits` with a magnitude limit,
and a name over 128 bytes is a third complaint again). pcrec reproduces all of
it, and `tests/registry/pcre2_check.c` re-measures every bit of it against
libpcre2 on each run. `pcrec --list-verbs` prints the tables.

**A RULED, deliberate tier-2 divergence (K15, D26; Frank, 2026-08-12):** for a
verb "name" over the 128-code-unit cap made ENTIRELY of non-identifier bytes,
pcrec answers "subpattern name is too long (maximum 128 code units)" where
libpcre2 10.46 answers error 160, "(*VERB) not recognized or malformed", at
offset 2. Root cause: pcrec's extent scan (`pcrec_verb_name_extent_scan`,
scans.c) reads every byte up to `)` `:` `=` EOF before it ever compares the run
to a table entry, so an over-cap run hits the length check first; libpcre2's
own scan stops at the first non-alnum/`_` byte and reports "not recognized"
about the short prefix it actually extracted. Both are honest refusals of a
name that can never match a real verb — the two engines diverge on which
REFUSAL CATEGORY, never on accept vs. reject, which is what keeps this at tier
2 rather than tier 1. Found by the R18 panel's engine critic
(docs/dev/reviews/2026-08-12-r18-mod04.md), recorded at docs/dev/known_issues.md K15,
and confirmed on both controls: UNDER the 128-byte cap a non-identifier run
gets "not recognized" on both sides (agreement — K15's own control), and OVER
the cap an IDENTIFIER run gets the exact same "too long" text on both sides
(also agreement — the 128-byte rule itself is right for identifier names).
`tests/registry/pcre2_check.c`'s `k15_excluded()` carries the one exclusion
this divergence needs, scoped to that single cell; extending the extent scan
to stop at the first non-identifier byte is deferred to SR-6, when module
`verbs` first produces and the scan's semantics get remeasured anyway.

What pcrec does NOT yet claim is which MODULE owns each name: `(*atomic:…)` and
`(*pla:…)` are answered "requires module 'verbs'" though they are atomic groups
and lookarounds, and correcting that belongs to SR-6 with the module itself.

**Since MOD-0.1's K14 fix (2026-08-11) the diagnostic honours this section's
own OUT-OF-SCOPE calls:** every name below marked OUT-OF-SCOPE carries
`ROADMAP_NEVER` in the verb tables and answers "... is outside pcrec's scope
and no module will implement it" instead of promising module `verbs`.
`compliance_section.py --names` holds this section and the column together in
both directions, so editing an OUT-OF-SCOPE cell here without moving the
column (or vice versa) fails `make test`. (`(?C` callouts at the `(?` doorway
carried the same OUT-OF-SCOPE/`ROADMAP_NEVER` pairing until [M4-CALLOUTS] step
1 moved it to `PLANNED` — see the Callouts section below. The live population
of non-verb `ROADMAP_NEVER` rows is zero as a result; the check that ties this
column to the prose stays column-derived rather than deleted, so it re-arms
the day a second such row exists.)

| syntax | status | becomes | notes |
|---|---|---|---|
| `(*FAIL)` `(*F)` | `REJECTED` | `PLANNED` | module `verbs`. The one verb PCRE2's DFA matcher DOES support: in a priority simulation it is simply a path that never reaches an accept state |
| `(*ACCEPT)` | `REJECTED` | `PLANNED-HARD` | module `verbs`. Expressible in principle (force an accept), but it interacts with the two-pass end-then-start architecture |
| `(*COMMIT)` `(*PRUNE)` `(*SKIP)` `(*SKIP:NAME)` `(*THEN)` `(*MARK:NAME)` `(*:NAME)` | `OUT-OF-SCOPE` | — | these are DEFINED in terms of a backtracking engine's search order — which alternatives to abandon and where to resume. A simulation engine explores all alternatives at once, so there is no backtracking tree to prune. PCRE2's own DFA matcher supports none of them. `(*MARK)` additionally requires reporting state back to the caller |

## Callouts

**[M4-CALLOUTS] step 1 (D36, Frank, 2026-08-12; flipped 2026-08-14):**
re-scoped from `OUT-OF-SCOPE` to `PLANNED`, module `callouts`, explicitly LOW
priority — parked behind the M4 VM engine that hosts the behavior (callouts
are engine-forcing like backrefs: the compiled DFA erases the pattern
positions a callout fires at, so callout patterns compile to the VM engine
only). The PATTERN layer (syntax, where callouts may appear) is D26-exact and
PCRE2-compatible; the CALLBACK CONTRACT mirrors `pcre2_callout_block` field
for field; the REGISTRATION API is pcrec-native (a compile-time-bound `extern`
the embedding program defines, zero cost when absent) rather than a runtime
`pcre2_set_callout`-style registration. The obstacle that kept this
`OUT-OF-SCOPE` no longer applies as a permanent one: generated code's zero
runtime dependency on pcrec is preserved by the static-extern binding, not by
refusing the construct. Step 2 (the behavior itself) is not yet built — see
`docs/dev/plan.md`'s `[M4-CALLOUTS]` row.

| syntax | status | becomes | notes |
|---|---|---|---|
| `(?C)` `(?Cn)` `(?C"text")` | `REJECTED` | `PLANNED` | module `callouts`, M4-hosted, VM-only (D36). Callback block and return semantics (0/positive/negative) mirror `pcre2_callout_block` field for field; fire-point precision is documented engine-relative, with PCRE2's own `PCRE2_NO_START_OPTIMIZE` latitude as the cited precedent that fire counts are not the contract |

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
corpus: a `perr` block asserts only THAT a pattern is rejected, never WHY, and
the module name is the caller's only pointer to what would implement the
construct.

**CORRECTED 2026-08-10 (R7).** This paragraph used to give a second reason —
that a `perr` block also needs the python oracle to fail, and that the
`# pcre2-only` escape hatch "does not apply because `verify_rxt.py`'s `perr`
branch never consults it". The first half is true; the second is FALSE and was
never measured. `verify_rxt.py`'s skip test precedes its `perr` branch, so a
marked block is skipped like any other case while `run.sh` still asserts it
against pcrec. FIX-1 corrected the claim in `tests/reject/`, and a critic found
this third copy still standing here, in the present tense, unflagged — the same
"one claim, several files, never measured" shape the document elsewhere warns
about.

`tests/reject/run_reject_tests.sh` asserts, per construct, that pcrec exits
exactly 1 (not 0, not a crash, not a timeout), carries the right diagnostic,
and writes no output file — 144 rows, plus 45 accept-controls, at R7 when this
was first built; the count has moved several times since and the same
hand-copied-figures failure mode this document warns about elsewhere (see
"Keeping this current") applied here too. **Current whole-suite figures,
measured live at [STD1b] (`ab7592d`, 2026-08-13): 274 hand-written rows, 99
accept-controls, 55 `reject_gated` pins, 99 iterated, 528 checks passing, 0
known-wrong — see the Headline above; do not re-copy these either, re-run the
script.** The table also carries a short manifest naming the rows whose
deletion the counts alone would not catch. Reproducing the `\v` bug's exact shape on a different
escape (silently decoding `\d` to a literal `d`) fails 2 reject checks and
**zero** corpus and codegen checks.

**Diagnostics fixed while surveying** (all were clean rejections already; none
was a miscompile — they simply failed to name a module, so the caller was told
their syntax was nonsense rather than what would implement it):

| construct | was | now |
|---|---|---|---|
| `(*ACCEPT)`, `(*SKIP)`, `(*CR)`, `(*script_run:…)`, all `(*…)` | `quantifier does not follow a repeatable item` | `(*...) requires module 'verbs'` — and since Q1, only for names PCRE2 actually has; `(*)` went back to the quantifier error, which is what PCRE2 says |
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
   not a doc reading, and get an entry in `docs/dev/known_issues.md` if it is not
   fixed in the same change.
5. Re-stamp "Last surveyed" and note what moved.

The `PLANNED`/`PLANNED-HARD` split is a judgement about pcrec's architecture,
not a schedule. Treat it as a prediction to be checked the way D18's option
predictions were — and record it here when one turns out wrong.

### How to read the generated index below (added 2026-08-19, [M6.2] repair slice)

Its `status` and `roadmap` columns are the REGISTRY's two fields (`RegStatus`
and `Roadmap`, `src/core/internal.h`), and **neither one says whether the
module that owns a construct has been BUILT.** `status` is a fact about
PCRE2 and about pcrec's BASE grammar: `REJECTED` renders `RS_MODULE`, "the
base grammar does not implement this, and the `module` column names what
does". It reads exactly that for `\d`, `(?i)` and `\b` alike, and all three
compile today.

MEASURED 2026-08-19 (`pcrec --list-syntax`, counted by module): **34 rows of
this index name a module that is SHIPPED** — `classes` 12, `modifiers` 12,
`assertions` 7, `named-groups` 3 — **and every one of them reads
`REJECTED | planned`.**

**The shipped status lives in the PROSE rows above, not here**, and that is
this section's design rather than an oversight: `compliance_section.py`'s own
docstring says "the inventory is generated and the analysis is not". A reader
asking whether a construct compiles today reads its prose row (`OK`,
`OK-GATED`, `OK-LIMITED`) and "Keeping this current" item 3, which is about
those rows and only those rows.

This is recorded because it has already misled once. The [M6.2] wave E lane
read `REJECTED | planned` on module `assertions`' rows as staleness SPECIFIC
to that module and returned a whole-module registry flip as a finding; the
repair slice measured the population above and flipped nothing, because the
eight `assertions` constructs are marked exactly as the other 27 shipped
constructs are and changing only them would make the index inconsistent
rather than current. Flipping them to `RS_BASE` would additionally be false
(they need `--features assertions`), would break the `RS_BASE => ROADMAP_NONE`
pairing `registry_check` enforces, and would delete the module name from the
gate-CLOSED diagnostic that `tests/reject/`'s rows assert. Giving the registry
a "the owning module is built" field so this index could answer the question
is a real, small design question, and it is a whole-registry one — not a
per-module repair.

<!-- BEGIN GENERATED: registry construct index (SR-4) -->

<!-- Generated by tests/registry/compliance_section.py from
     `pcrec --list-syntax`. Do not edit by hand: `make test` fails
     on drift. Add a construct by adding a row to
     src/parse/registry.c, then re-run with --write. -->

## Registry construct index (generated)

Every non-base construct pcrec knows, as the parser itself sees it — 100 rows from one declarative table (D24). The prose sections above carry the analysis; this is the inventory, and it cannot drift from the compiler because it is printed by it.

| doorway | syntax | status | roadmap | module | engines | PCRE2 semantics |
|---|---|---|---|---|---|---|
| after `\` | `\d` | `REJECTED` | planned | `classes` | dfa|vm | any decimal digit |
| after `\` | `\D` | `REJECTED` | planned | `classes` | dfa|vm | any character that is not a decimal digit |
| after `\` | `\s` | `REJECTED` | planned | `classes` | dfa|vm | any whitespace character |
| after `\` | `\S` | `REJECTED` | planned | `classes` | dfa|vm | any character that is not whitespace |
| after `\` | `\w` | `REJECTED` | planned | `classes` | dfa|vm | any word character (letter, digit or underscore) |
| after `\` | `\W` | `REJECTED` | planned | `classes` | dfa|vm | any character that is not a word character |
| after `\` | `\h` | `REJECTED` | planned | `classes` | dfa|vm | any horizontal whitespace character |
| after `\` | `\H` | `REJECTED` | planned | `classes` | dfa|vm | any character that is not horizontal whitespace |
| after `\` | `\v` | `REJECTED` | planned | `classes` | dfa|vm | any vertical whitespace character (NOT vertical tab; python re disagrees) |
| after `\` | `\V` | `REJECTED` | planned | `classes` | dfa|vm | any character that is not vertical whitespace |
| after `\` | `\N` | `REJECTED` | planned | `classes` | dfa|vm | any character except newline (PCRE2 forbids it inside a class) |
| after `\` | `\N{name}` | `AGREES-REJECT` | never | — | — | \N{name} — PCRE2 states it does not support this Perl construct |
| after `\` | `\N{U+0041}` | `REJECTED` | planned | `unicode-props` | dfa|vm | a Unicode code point by number — PCRE2 error 193 outside UTF mode, which is recognition, not rejection |
| after `\` | `\b` | `REJECTED` | planned | `assertions` | dfa|vm | word boundary — but inside a class it is BASE syntax: backspace (0x08) |
| after `\` | `\B` | `REJECTED` | planned | `assertions` | dfa|vm | not a word boundary |
| after `\` | `\A` | `REJECTED` | planned | `assertions` | dfa|vm | start of subject |
| after `\` | `\Z` | `REJECTED` | planned | `assertions` | dfa|vm | end of subject, or before a final newline |
| after `\` | `\z` | `REJECTED` | planned | `assertions` | dfa|vm | end of subject |
| after `\` | `\G` | `REJECTED` | planned | `assertions` | dfa|vm | first matching position in the subject |
| after `\` | `\K` | `REJECTED` | planned | `assertions` | vm | reset the reported start of the match |
| after `\` | `\k<name>` | `REJECTED` | planned | `backrefs` | vm | backreference by name: \k<n> \k'n' \k{n} — literal 'k' inside a class |
| after `\` | `\g{-1}` | `REJECTED` | planned | `backrefs` | vm | backreference by number or relative position: \g1 \g{-1} \g{name} — literal 'g' inside a class |
| after `\` | `\p{L}` | `REJECTED` | planned | `unicode-props` | dfa|vm | a character with the given Unicode property |
| after `\` | `\P{L}` | `REJECTED` | planned | `unicode-props` | dfa|vm | a character without the given Unicode property |
| after `\` | `\Q` | `REJECTED` | planned | `quoting` | dfa|vm | begin literal quoting, until \E |
| after `\` | `\E` | `REJECTED` | planned | `quoting` | dfa|vm | end literal quoting begun by \Q |
| after `\` | `\R` | `REJECTED` | planned | `misc` | dfa|vm | any Unicode newline sequence |
| after `\` | `\X` | `REJECTED` | planned | `misc` | dfa|vm | a Unicode extended grapheme cluster |
| after `\` | `\C` | `REJECTED` | planned | `misc` | dfa|vm | one data unit (byte), even in UTF mode |
| after `\` | `\cX` | `REJECTED` | planned | `misc` | dfa|vm | control character: \cX is X xor 0x40 |
| after `\` | `\o{101}` | `REJECTED` | planned | `misc` | dfa|vm | character with the given octal code |
| after `\` | `\0` | `REJECTED` | planned | `backrefs` | dfa|vm | octal escape \0dd — never a backreference (there is no group 0) |
| after `\` | `\1` | `REJECTED` | planned | `backrefs` | vm | backreference to capture group 1 (PCRE2 error 115 if no such group) |
| after `\` | `\2` | `REJECTED` | planned | `backrefs` | vm | backreference to capture group 2 (PCRE2 error 115 if no such group) |
| after `\` | `\3` | `REJECTED` | planned | `backrefs` | vm | backreference to capture group 3 (PCRE2 error 115 if no such group) |
| after `\` | `\4` | `REJECTED` | planned | `backrefs` | vm | backreference to capture group 4 (PCRE2 error 115 if no such group) |
| after `\` | `\5` | `REJECTED` | planned | `backrefs` | vm | backreference to capture group 5 (PCRE2 error 115 if no such group) |
| after `\` | `\6` | `REJECTED` | planned | `backrefs` | vm | backreference to capture group 6 (PCRE2 error 115 if no such group) |
| after `\` | `\7` | `REJECTED` | planned | `backrefs` | vm | backreference to capture group 7 (PCRE2 error 115 if no such group) |
| after `\` | `\8` | `REJECTED` | planned | `backrefs` | vm | backreference to capture group 8 (PCRE2 error 115 if no such group) |
| after `\` | `\9` | `REJECTED` | planned | `backrefs` | vm | backreference to capture group 9 (PCRE2 error 115 if no such group) |
| after `(?` | `(?:...)` | `OK` | — | — | dfa|vm | non-capturing group |
| after `(?` | `(?=...)` | `REJECTED` | planned | `lookaround` | vm | positive lookahead |
| after `(?` | `(?!...)` | `REJECTED` | planned | `lookaround` | vm | negative lookahead |
| after `(?` | `(?<=...)` | `REJECTED` | planned | `lookaround` | vm | positive lookbehind |
| after `(?` | `(?<!...)` | `REJECTED` | planned | `lookaround` | vm | negative lookbehind |
| after `(?` | `(?<*a)` | `REJECTED` | planned | `lookaround` | vm | non-atomic positive lookbehind — the (? spelling of (*naplb:...) |
| after `(?` | `(?<name>a)` | `REJECTED` | planned | `named-groups` | dfa|vm | named capture group (?<name>...) — the lookbehinds take = ! * and have their own rows |
| after `(?` | `(?'name'...)` | `REJECTED` | planned | `named-groups` | dfa|vm | named capture group, Perl-style quoting |
| after `(?` | `(?P<name>a)` | `REJECTED` | planned | `named-groups` | dfa|vm | python-style named capture group |
| after `(?` | `(?P=n)` | `REJECTED` | planned | `backrefs` | vm | python-style backreference to a named group |
| after `(?` | `(?P>n)` | `REJECTED` | planned | `recursion` | vm | python-style subroutine call into a named group |
| after `(?` | `(?PX)` | `AGREES-REJECT` | never | — | — | only (?P< (?P= and (?P> exist — every other byte after (?P is PCRE2 error 141 |
| after `(?` | `(?>...)` | `REJECTED` | planned | `atomic-groups` | vm | atomic (non-backtracking) group |
| after `(?` | `(?*a)` | `REJECTED` | planned | `lookaround` | vm | non-atomic positive lookahead — the (? spelling of (*napla:...) |
| after `(?` | `(?#...)` | `REJECTED` | planned | `comments` | dfa|vm | comment, discarded up to the next ')' |
| after `(?` | `(?C1)` | `REJECTED` | planned | `callouts` | vm | callout to user code: (?C) (?C1) (?C{text}) -- PLANNED (D36): M4-hosted, VM-only; the compiled DFA erases the pattern positions a callout fires at |
| after `(?` | `(?\|...)` | `REJECTED` | planned | `branch-reset` | vm | branch reset group: alternatives reuse the same capture numbers |
| after `(?` | `(?(1)a\|b)` | `REJECTED` | planned | `conditionals` | vm | conditional group (?(condition)yes\|no) |
| after `(?` | `(?&name)` | `REJECTED` | planned | `recursion` | vm | recurse into the named group |
| after `(?` | `(?R)` | `REJECTED` | planned | `recursion` | vm | recurse the whole pattern |
| after `(?` | `(?0)` | `REJECTED` | planned | `recursion` | vm | recurse the whole pattern (synonym for (?R)) |
| after `(?` | `(?1)` | `REJECTED` | planned | `recursion` | vm | recurse into capture group 1 |
| after `(?` | `(?2)` | `REJECTED` | planned | `recursion` | vm | recurse into capture group 2 |
| after `(?` | `(?3)` | `REJECTED` | planned | `recursion` | vm | recurse into capture group 3 |
| after `(?` | `(?4)` | `REJECTED` | planned | `recursion` | vm | recurse into capture group 4 |
| after `(?` | `(?5)` | `REJECTED` | planned | `recursion` | vm | recurse into capture group 5 |
| after `(?` | `(?6)` | `REJECTED` | planned | `recursion` | vm | recurse into capture group 6 |
| after `(?` | `(?7)` | `REJECTED` | planned | `recursion` | vm | recurse into capture group 7 |
| after `(?` | `(?8)` | `REJECTED` | planned | `recursion` | vm | recurse into capture group 8 |
| after `(?` | `(?9)` | `REJECTED` | planned | `recursion` | vm | recurse into capture group 9 |
| after `(?` | `(?+1)(a)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call to the Nth group to the RIGHT |
| after `(?` | `(a)(?-01)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call, leading zero |
| after `(?` | `(a)(?-1)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call to the group 1 to the LEFT |
| after `(?` | `(a)(a)(?-2)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call, 2 to the left |
| after `(?` | `(a)(a)(a)(?-3)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call, 3 to the left |
| after `(?` | `(a)(a)(a)(a)(?-4)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call, 4 to the left |
| after `(?` | `(a)(a)(a)(a)(a)(?-5)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call, 5 to the left |
| after `(?` | `(a)(a)(a)(a)(a)(a)(?-6)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call, 6 to the left |
| after `(?` | `(a)(a)(a)(a)(a)(a)(a)(?-7)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call, 7 to the left |
| after `(?` | `(a)(a)(a)(a)(a)(a)(a)(a)(?-8)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call, 8 to the left |
| after `(?` | `(a)(a)(a)(a)(a)(a)(a)(a)(a)(?-9)` | `REJECTED` | planned | `recursion` | vm | relative subroutine call, 9 to the left |
| after `(?` | `(?[[a]])` | `REJECTED` | planned | `extended-classes` | dfa|vm | extended character class with set operations: (?[[a]&&[b]]) (?[[a]-[b]]) |
| after `(?` | `(?)` | `REJECTED` | planned | `modifiers` | dfa|vm | empty option setting |
| after `(?` | `(?-i)` | `REJECTED` | planned | `modifiers` | dfa|vm | unset options: (?-i) (?-im:...) |
| after `(?` | `(?^)` | `REJECTED` | planned | `modifiers` | dfa|vm | reset all options to their default |
| after `(?` | `(?J)` | `REJECTED` | planned | `modifiers` | dfa|vm | allow duplicate names (PCRE2_DUPNAMES) |
| after `(?` | `(?U)` | `REJECTED` | planned | `modifiers` | dfa|vm | ungreedy: invert the greediness of quantifiers |
| after `(?` | `(?a)` | `REJECTED` | planned | `modifiers` | dfa|vm | ASCII-restrict class escapes (PCRE2_EXTRA_ASCII_*) |
| after `(?` | `(?i)` | `REJECTED` | planned | `modifiers` | dfa|vm | caseless |
| after `(?` | `(?m)` | `REJECTED` | planned | `modifiers` | dfa|vm | multiline: ^ and $ match at internal newlines |
| after `(?` | `(?n)` | `REJECTED` | planned | `modifiers` | dfa|vm | no auto-capture: plain (...) stops capturing |
| after `(?` | `(?r)` | `REJECTED` | planned | `modifiers` | dfa|vm | restrict caseless matching to within ASCII or non-ASCII |
| after `(?` | `(?s)` | `REJECTED` | planned | `modifiers` | dfa|vm | dotall: . matches newline |
| after `(?` | `(?x)` | `REJECTED` | planned | `modifiers` | dfa|vm | extended: ignore unescaped whitespace and # comments |
| after `(?` | `(?q)` | `AGREES-REJECT` | never | — | — | no construct begins with this byte — PCRE2 error 111 |
| after `(*` | `(*ACCEPT)` | `REJECTED` | planned | `verbs` | vm | backtracking verb ((*SKIP), (*ACCEPT)), start-of-pattern option ((*CR), (*UTF)) or script run ((*script_run:...)) |
| after `[` in a class | `[[:alpha:]]` | `REJECTED` | planned | `classes` | dfa|vm | POSIX character class |
| after `[` in a class | `[[.a.]]` | `AGREES-REJECT` | never | — | — | POSIX collating element — PCRE2 rejects it, and so must we |
| after `[` in a class | `[[=a=]]` | `AGREES-REJECT` | never | — | — | POSIX equivalence class — PCRE2 rejects it, and so must we |

<!-- END GENERATED -->
