# PCRE2 option/flag disposition survey

Sibling to `pcre2_compliance.md` (construct-by-construct) — this is
option-by-option. Governing plan row: `[PC-5]` in `docs/dev/plan.md`.

> **DISPOSITIONS IN THIS DOCUMENT ARE PROPOSALS, NOT RULINGS.** Every value in
> the `proposed disposition` column is this survey's best-effort placement
> using D18's earn-its-axis test and the vocabulary below. The `ruling` column
> is empty by design — it is Frank's to fill in, and any proposal here can be
> overturned. Nothing in this document authorizes building anything.

## Source information

- **Surveyed against:** libpcre2 **10.46-1build1** (Ubuntu, matches the box's
  installed `libpcre2-8-0`/`libpcre2-16-0` runtime packages — `dpkg -l
  libpcre2-8-0` reports `10.46-1build1`).
- **`pcre2.h` was NOT present on this box** (`libpcre2-dev` is not installed,
  and `sudo` is unavailable to install it system-wide — respecting the repo
  scope mandate, no system package install was performed). The header was
  obtained by `apt-get download libpcre2-dev` (network fetch of the .deb,
  version-matched `10.46-1build1`) and extracted with `dpkg-deb -x` into the
  session scratchpad ONLY — never installed, never committed, not present
  anywhere under the repo. Flag names, values and function signatures below
  are transcribed directly from that header. The `.deb` and extracted tree
  stay in the scratchpad.
- **Fiddly-semantics rows are MEASURED**, not read off documentation alone
  (the Q2/K4 lesson pcre2_compliance.md and D26 both cite). Probes were
  written against this same header, compiled with `gcc -I <scratch>/include
  -o probe probe.c -l:libpcre2-8.so.0 -L/usr/lib/x86_64-linux-gnu` (no `.so`
  dev symlink exists, hence the versioned `-l:` form), and run directly. The
  probe source and full transcript are reproduced in the Measurement Appendix
  at the end of this document; the probe file itself lived only in the
  scratchpad and was not committed, per convention for one-off measurement
  tools (`docs/measurements/CLAUDE.md`'s stable-artifact form was not used
  here since this is a single-session fact-gathering pass, not a re-run
  measurement pipeline).
- Rows without a Measured-evidence note are read from the PCRE2 documentation
  and header comments; their semantics is not in dispute and a probe was
  judged not to earn its cost. Any row that IS subtle but could not be probed
  is marked **UNMEASURED** explicitly rather than asserted.

## Standing constraint: the oracle is pinned at options=0

`tests/registry/pcre2_check.c` compiles every differential probe with
`options = 0` (R10 disposition 3 / D30 §1's resolution: *"bind the option set
... state 'the mode pcrec compiles for' as PCREC'S OWN decision rather than a
claim about PCRE2"*). Every verdict pcrec's suite currently trusts against
libpcre2 is a verdict AT OPTIONS=0. Adopting ANY flag surveyed below — even
one this document proposes as free — is a deliberate re-measurement event:
the differential harness's "ALL COMPILES USE options = 0" invariant
(`pcre2_check.c:50`) has to move first, or the new flag's cells are simply
unverified. This applies whether the flag becomes a real pcrec knob or is
folded away at parse time (D23's precedent: CASELESS folding into the front
end still needed its OWN differential evidence, not a ride on the options=0
baseline).

## Disposition vocabulary (from the [PC-5] plan row)

| tag | meaning |
|---|---|
| `DONE-AS(X)` | already exists in pcrec as X (e.g. CASELESS ≡ `-i`/`(?i)`, D23) |
| `RIDES(owner)` | lands with an owning module/milestone/plan-row; no separate work |
| `GENERATION-AXIS` | a D18 earn-its-axis candidate: a distinct compiled variant, not a runtime branch |
| `API-PARAM` | a runtime parameter on the generated entry point |
| `EMITTED-LOOP` | subsumed by generated iteration — pcrec emits the loop the flag exists to support |
| `LATER` | plausible future work, no current customer or owning row |
| `NEVER(reason)` | architecturally excluded, with the reason stated |

**Overlaps, deliberately not merged here:**
- **DOC-BM** (`docs/dev/plan.md`, deferred) owns the `PCRE2_EXTRA_*` family's
  effect on registry DISPATCH — the EXTRA_* rows below are the
  option-adoption question only; DOC-BM is the authority on what any of them
  do to the recogniser tables, and this survey feeds it rather than
  replacing it.
- **DD-11** (`docs/dev/plan.md`, not-started) owns the NEWLINE CONVENTION
  axis and `\R`'s BSR setting. The NEWLINE/BSR rows below point there rather
  than re-deriving pcrec's newline story.

---

## 1. Compile/match/dfa-match shared bits (the "top of the word" group)

Per `pcre2.h`: *"can be passed to `pcre2_compile()`, `pcre2_match()`, or
`pcre2_dfa_match()`"* — deliberately placed at the most-significant bits so
future compile-only bits can be added without colliding.

| flag | value | what it does | binds | proposed disposition | ruling |
|---|---|---|---|---|---|
| `PCRE2_ANCHORED` | `0x80000000` | forbid the unanchored sliding search; match must start exactly at the given start offset | compile OR match-call | `GENERATION-AXIS` — compiles to the anchored variant; already tracked as `[OS-4]`'s `ENG_ATTEMPT` split (plan.md), and `[OS-0]`'s named entry points (`rx_search_anchored` style) serve callers wanting both without a runtime branch | |
| `PCRE2_NO_UTF_CHECK` | `0x40000000` | skip the UTF validity scan on pattern/subject that PCRE2 normally runs before matching | compile OR match-call (function-scoped, doesn't stick) | `RIDES(M5/UTF)` — meaningless before a UTF matcher exists to validate in the first place; M5 decides whether pcrec's UTF entry point validates by default and whether skipping is an `API-PARAM` or compiled out entirely | |
| `PCRE2_ENDANCHORED` | `0x20000000` | require the match to end exactly at the end of the subject | compile OR match-call | `GENERATION-AXIS` — same family as `ANCHORED`; explicit example in the `[PC-5]` plan row itself | |

---

## 2. Compile-only bits

*"can be passed only to `pcre2_compile()`. However, they may affect
compilation, JIT compilation, and/or interpretive execution"* — the
per-flag `C`/`J`/`M`/`D` tags from `pcre2.h` are carried into the "binds"
column.

| flag | value | what it does | binds | proposed disposition | ruling |
|---|---|---|---|---|---|
| `PCRE2_ALLOW_EMPTY_CLASS` | `0x00000001` | `[]`/`[^]` compile instead of erroring | C | `RIDES(classes)` — whether the empty-class body parses at all is module `classes`'s own recognition rule (`pcre2_compliance.md`), a single hyperspecialized choice per D18, not a caller-facing toggle | |
| `PCRE2_ALT_BSUX` | `0x00000002` | `\U`/`\u`/`\x` follow ECMAScript escaping instead of PCRE2's own | C | `LATER` — dialect-compat surface (ECMAScript, not PCRE2's native grammar); no stated embedder customer; D26 tier-3/4 distance from the core | |
| `PCRE2_AUTO_CALLOUT` | `0x00000004` | insert an automatic numbered callout between every pattern item | C | `RIDES(callouts/M4-CALLOUTS, D36)` | |
| `PCRE2_CASELESS` | `0x00000008` | case-insensitive matching | C | `DONE-AS(-i/(?i), D23)` — folds into the front end, no engine cost; explicit example in the plan row | |
| `PCRE2_DOLLAR_ENDONLY` | `0x00000010` | `$` matches only at the very end of subject, never before a trailing `\n` | J M D | `RIDES(DD-11)` — same EOL-variant/newline-convention family DD-11 already owns. **Measured** (Appendix §4): plain `a$` matches `"a\n"` at `[0,1)`; with `DOLLAR_ENDONLY` it does not match at all | |
| `PCRE2_DOTALL` | `0x00000020` | `.` matches every byte including newline | C | `RIDES(modifiers)` — pcrec's `.`-compiles-to-a-bitmap-complement design (same shape as CASELESS's fold) should land as inline `(?s)` in module `modifiers`; verify current landed status against `tests/modifiers/` before treating as done | |
| `PCRE2_DUPNAMES` | `0x00000040` | allow the same named group to appear more than once | C | `RIDES(M4/captures)` — named-capture bookkeeping is capture-group machinery, M4's territory | |
| `PCRE2_EXTENDED` | `0x00000080` | free-spacing/comment mode (whitespace and `#...` ignored outside classes) | C | `RIDES(modifiers)` — inline `(?x)`; verify landed status against `tests/modifiers/` | |
| `PCRE2_FIRSTLINE` | `0x00000100` | the match must start (not necessarily end) before or at the first newline in the subject | J M D | `RIDES(DD-11)` — newline-convention family. **Measured** (Appendix §5): pattern `b` against `"a\nb"` matches at `[2,3)` plain; with `FIRSTLINE` set it does not match at all | |
| `PCRE2_MATCH_UNSET_BACKREF` | `0x00000200` | a backreference to a group that didn't participate matches an empty string instead of failing | C J M | `RIDES(M4/backrefs)` — only meaningful once backreferences exist; M4's backrefs design note (plan.md) inherits this | |
| `PCRE2_MULTILINE` | `0x00000400` | `^`/`$` also match at internal line boundaries | C | `RIDES(assertions/DD-6)` — explicit example in the plan row | |
| `PCRE2_NEVER_UCP` | `0x00000800` | lock out `PCRE2_UCP` even if a caller or `(*UCP)` requests it | C | `RIDES(M5/UTF-UCP)` — paired lockout for the UCP axis, decide together at M5 | |
| `PCRE2_NEVER_UTF` | `0x00001000` | lock out `PCRE2_UTF`/`(*UTF)` even if requested | C | `RIDES(M5/UTF)` — same family | |
| `PCRE2_NO_AUTO_CAPTURE` | `0x00002000` | unnamed `(...)` becomes non-capturing by default (as if every group were `(?:...)`) | C | `RIDES(M4/captures)` — real PCRE2 inline form is `(?n)`; auto-numbering policy is capture-group bookkeeping | |
| `PCRE2_NO_AUTO_POSSESS` | `0x00004000` | disable PCRE2's automatic possessification optimization | C J M D | `NEVER(generation-time decision in an AOT compiler)` — explicit example in the plan row; cite `[M4-CALLOUTS]`'s `PCRE2_NO_START_OPTIMIZE`-latitude precedent | |
| `PCRE2_NO_DOTSTAR_ANCHOR` | `0x00008000` | disable PCRE2's `.*`-at-start auto-anchoring optimization | C | `NEVER(generation-time decision in an AOT compiler)` — same family as `NO_AUTO_POSSESS`/`NO_START_OPTIMIZE`. **Measured** (Appendix §6): verdict and ovector for `.*a` against `"xxa"` are byte-identical with and without the flag in libpcre2 itself — it is a pure search-strategy hint with zero semantic effect, which is exactly the property that makes it moot for a compiler whose "optimization" happens once, offline, at codegen | |
| `PCRE2_NO_START_OPTIMIZE` | `0x00010000` | disable PCRE2's start-of-match optimizations generally | J M D | `NEVER(generation-time decision in an AOT compiler)` — explicit example in the plan row, with the `[M4-CALLOUTS]` precedent citation | |
| `PCRE2_UCP` | `0x00020000` | `\d`/`\w`/`\s`/POSIX classes and case-folding follow Unicode properties | C J M D | `RIDES(M5)` — explicit example in the plan row | |
| `PCRE2_UNGREEDY` | `0x00040000` | swap default quantifier greediness (`a*` becomes lazy, `a*?` becomes greedy) | C | `RIDES(modifiers)` — pending verification that module `modifiers` implements inline `(?U)` specifically (not just `i`/`s`/`m`/`x`). **Measured** (Appendix §3): inline `(?U)`/`(?-U)` toggles RELATIVE to the compile-time baseline — `opt=UNGREEDY, pat=(?-U)a+` against `"aaa"` matches the full greedy `"aaa"`, i.e. the inline modifier is a real toggle, not an absolute override, so `(?U)` support (once landed) fully subsumes this compile flag's caller-facing effect | |
| `PCRE2_UTF` | `0x00080000` | treat pattern and subject as UTF-8/16/32 | C J M D | `RIDES(M5)` — explicit example in the plan row | |
| `PCRE2_NEVER_BACKSLASH_C` | `0x00100000` | lock out `\C` (match one byte even inside UTF mode) entirely | C | `LATER` — a defensive lockout for embedders worried about `\C` breaking UTF alignment; no stated customer today | |
| `PCRE2_ALT_CIRCUMFLEX` | `0x00200000` | under `MULTILINE`, `^` also matches immediately after a final trailing newline | J M D | `RIDES(assertions/DD-6)` — a multiline-`^` edge case, same owner as `MULTILINE` itself | |
| `PCRE2_ALT_VERBNAMES` | `0x00400000` | backtracking-verb argument names may contain backslash escapes, as an ordinary quoted string would | C | `NEVER(verbs are architecturally excluded)` — backtracking verbs (`(*SKIP)`, `(*PRUNE)`, etc., as distinct from callouts, which D36 re-scoped separately) are incompatible with pcrec's non-backtracking O(n) DFA core; an option that only affects verb-ARGUMENT lexing has nothing to attach to if the verbs themselves are never implemented — **confirm against `pcre2_compliance.md`'s current verb rows before ruling**, since D36 shows this category can move | |
| `PCRE2_USE_OFFSET_LIMIT` | `0x00800000` | enable `pcre2_set_offset_limit()`'s bound on how far an unanchored search may slide before giving up | J M D | `API-PARAM` — a straightforward runtime scalar (search bound), not an axis; no urgent module tie, low scheduling priority | |
| `PCRE2_EXTENDED_MORE` | `0x01000000` | `(?xx)` — like `EXTENDED` but whitespace inside classes is ALSO ignored | C | `RIDES(modifiers)` — `(?xx)`/class-range-endpoint interaction is already live project history (R10 disposition #16 / K10 in `docs/known_issues.md`); confirm current landed status | |
| `PCRE2_LITERAL` | `0x02000000` | treat the ENTIRE pattern as a literal string — no metacharacters at all | C | `GENERATION-AXIS` — arguably the cheapest possible compiled variant to support (literal-string search, no NFA/DFA construction needed at all); `LATER` for scheduling priority, but the shape is a distinct generated-code path, not a runtime branch | |
| `PCRE2_MATCH_INVALID_UTF` | `0x04000000` | invalid UTF-8/16/32 byte sequences are treated as a run of one-unit non-characters instead of raising an error | J M D | `RIDES(M5/UTF)` — a UTF-matcher error-handling policy, M5's to decide | |
| `PCRE2_ALT_EXTENDED_CLASS` | `0x08000000` | enables PCRE2's newer `[...]` set-operator class syntax (union/intersection/subtraction operators inside classes) | C | `RIDES(classes)` — a natural extension of module `classes`; `LATER` priority as a newer/rarer PCRE2 feature (added recently upstream) | |

---

## 3. Compile-context extra options (`PCRE2_EXTRA_*`)

Applied via `pcre2_set_compile_extra_options()` on a `pcre2_compile_context`
— a SECOND options word, separate from the bits above. **DOC-BM is the
owner of what these do to registry DISPATCH; the rows below answer only
"does pcrec adopt this flag," not "how does it change recognition."**

| flag | value | what it does | binds | proposed disposition | ruling |
|---|---|---|---|---|---|
| `PCRE2_EXTRA_ALLOW_SURROGATE_ESCAPES` | `0x00000001` | permit UTF-16/32 surrogate code points via `\x{...}` even in UTF mode | compile context | `RIDES(M5)` — meaningless before UTF exists | |
| `PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL` | `0x00000002` | an unrecognised backslash escape compiles to its literal character instead of erroring | compile context | `RIDES(DOC-BM)` — explicitly named in DOC-BM's own plan-row description ("the `EXTRA_BAD_ESCAPE_IS_LITERAL` 18-cell migration"); do not re-derive here | |
| `PCRE2_EXTRA_MATCH_WORD` | `0x00000004` | implicitly wrap the whole pattern in word-boundary assertions | compile context | `LATER` — caller convenience wrapper, no new syntax; no stated customer | |
| `PCRE2_EXTRA_MATCH_LINE` | `0x00000008` | implicitly wrap the whole pattern in `^...$` | compile context | `LATER` — same family | |
| `PCRE2_EXTRA_ESCAPED_CR_IS_LF` | `0x00000010` | the literal escape `\r` compiles as if it were `\n`, under certain newline conventions | compile context | `RIDES(DD-11)` — newline-convention family | |
| `PCRE2_EXTRA_ALT_BSUX` | `0x00000020` | extends `PCRE2_ALT_BSUX`'s ECMAScript escaping into character-class bodies too | compile context | `LATER` — same dialect-compat family as `PCRE2_ALT_BSUX` above | |
| `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK` | `0x00000040` | permit `\K` inside lookaround assertions (normally rejected — ambiguous there) | compile context | `RIDES(assertions/DD-6)` — `\K`-in-lookaround is assertions-module territory | |
| `PCRE2_EXTRA_CASELESS_RESTRICT` | `0x00000080` | restrict Unicode caseless matching to avoid overly broad fold-equivalences (e.g. Kelvin sign folding to `k`) | compile context | `RIDES(DD-1/M5)` — direct extension of D23's caseless-fold design once Unicode folding lands; D23 itself flags Unicode folding as unresolved | |
| `PCRE2_EXTRA_ASCII_BSD` | `0x00000100` | `\d` matches ASCII digits only, even under `UCP` | compile context | `RIDES(M5)` — per-escape-class UCP override, M5's territory | |
| `PCRE2_EXTRA_ASCII_BSS` | `0x00000200` | `\s` ASCII-only under `UCP` | compile context | `RIDES(M5)` — same family | |
| `PCRE2_EXTRA_ASCII_BSW` | `0x00000400` | `\w` ASCII-only under `UCP` | compile context | `RIDES(M5)` — same family | |
| `PCRE2_EXTRA_ASCII_POSIX` | `0x00000800` | POSIX classes (`[:alpha:]` etc.) ASCII-only under `UCP` | compile context | `RIDES(M5)` — same family | |
| `PCRE2_EXTRA_ASCII_DIGIT` | `0x00001000` | the POSIX `digit`/`xdigit` classes specifically stay ASCII-only under `UCP` (distinct from `ASCII_BSD`'s `\d`) | compile context | `RIDES(M5)` — same family | |
| `PCRE2_EXTRA_PYTHON_OCTAL` | `0x00002000` | octal-escape lexing follows Python's rules instead of PCRE2's own | compile context | `LATER` — dialect-compat, no customer, D26 tier distance | |
| `PCRE2_EXTRA_NO_BS0` | `0x00004000` | forbid `\0` as an octal NUL escape (removes ambiguity with backreference numbering) | compile context | `LATER` — niche, no customer | |
| `PCRE2_EXTRA_NEVER_CALLOUT` | `0x00008000` | lock out ALL callouts at compile time even if the pattern requests them | compile context | `RIDES(callouts/M4-CALLOUTS, D36)` — defensive counterpart to `AUTO_CALLOUT`, same owner | |
| `PCRE2_EXTRA_TURKISH_CASING` | `0x00010000` | locale-flavored casefolding for dotted/dotless I (Turkish/Azeri) | compile context | `RIDES(DD-1/M5)` — extension of Unicode-folding design, same family as `CASELESS_RESTRICT` | |

---

## 4. JIT options

*"for `pcre2_jit_compile()`."* pcrec has no JIT concept: the generated C
source IS the compiled artifact, produced ahead of time. All five are:

| flag | value | what it does | binds | proposed disposition | ruling |
|---|---|---|---|---|---|
| `PCRE2_JIT_COMPLETE` | `0x00000001` | JIT-compile the full-match code path | `pcre2_jit_compile()` | `NEVER(no JIT — the AOT-generated C is already the compiled artifact)` | |
| `PCRE2_JIT_PARTIAL_SOFT` | `0x00000002` | JIT-compile the soft-partial-match code path | `pcre2_jit_compile()` | `NEVER(same reason)` | |
| `PCRE2_JIT_PARTIAL_HARD` | `0x00000004` | JIT-compile the hard-partial-match code path | `pcre2_jit_compile()` | `NEVER(same reason)` | |
| `PCRE2_JIT_INVALID_UTF` | `0x00000100` | JIT support for `MATCH_INVALID_UTF` | `pcre2_jit_compile()` | `NEVER(same reason)` | |
| `PCRE2_JIT_TEST_ALLOC` | `0x00000200` | JIT allocator-failure testing hook | `pcre2_jit_compile()` | `NEVER(JIT debugging knob, doubly inapplicable)` | |

---

## 5. Match / DFA-match / substitute shared options word

*"for `pcre2_match()`, `pcre2_dfa_match()`, `pcre2_jit_match()`, and
`pcre2_substitute()`. Some are allowed only for one of the functions."*
`PCRE2_ANCHORED`, `PCRE2_ENDANCHORED` and `PCRE2_NO_UTF_CHECK` (§1) are also
legal here and are not repeated.

| flag | value | what it does | binds | proposed disposition | ruling |
|---|---|---|---|---|---|
| `PCRE2_NOTBOL` | `0x00000001` | the start of the subject is not treated as the start of a line (affects `^`) | match-call | `API-PARAM` — explicit example in the plan row | |
| `PCRE2_NOTEOL` | `0x00000002` | the end of the subject is not treated as the end of a line (affects `$`) | match-call | `API-PARAM` — explicit example, paired with `NOTBOL` | |
| `PCRE2_NOTEMPTY` | `0x00000004` | an empty-string match is treated as no match, at ANY start position the unanchored search reaches | match-call | `EMITTED-LOOP` — explicit example in the plan row. **Measured** (Appendix §1): with subject `"bb"` (no `a` anywhere) and pattern `a*`, `NOTEMPTY` yields `NOMATCH` outright — the unanchored search slides through every position, finds only empty candidates, and rejects all of them | |
| `PCRE2_NOTEMPTY_ATSTART` | `0x00000008` | an empty-string match is rejected ONLY if it occurs exactly at the caller-supplied start offset; empty matches found by sliding past that offset are allowed | match-call | `EMITTED-LOOP` — explicit example, paired with `NOTEMPTY`. **Measured** (Appendix §1, the discriminating case): same subject `"bb"`, same start offset 0 — `NOTEMPTY_ATSTART` matches empty at `[1,1)`, where plain `NOTEMPTY` returned NOMATCH. This is PCRE2's documented global-match-loop primitive (bump start by one, forbid empty ONLY at the new start, to avoid stalling on repeated empty matches without silently skipping non-empty matches one byte later) — pcrec's own `DD-4`/`M4-SUBST`-emitted global loop needs exactly this same two-flag pairing internally even though neither flag is caller-visible | |
| `PCRE2_PARTIAL_SOFT` | `0x00000010` | if the subject runs out mid-match, remember the partial match but keep searching for a later COMPLETE match; return the partial only if no complete match is ever found | match-call, dfa-match | `RIDES(OS-3/streaming)` — partial matching only makes sense for pcrec once streaming/incremental input (`[OS-3]`, predicted NOT to be a simple wrapper) is designed. **Measured** (Appendix §2): pattern `catfish|cat` (ordered so the first alternative only partially matches) against subject `"cat"` — plain and `PARTIAL_SOFT` both return the COMPLETE match `"cat"` via the second alternative, ignoring the partial found in the first | |
| `PCRE2_PARTIAL_HARD` | `0x00000020` | return a partial match as soon as one is found, without exploring whether a later alternative gives a complete match | match-call, dfa-match | `RIDES(OS-3/streaming)` — same family. **Measured** (Appendix §2): same pattern/subject, `PARTIAL_HARD` returns `PARTIAL [0,3)="cat"` instead of the complete match — confirms `HARD` preempts the search the instant a partial candidate appears, exactly as documented, and this genuinely changes the returned verdict (not just which code path runs) so any future partial-matching work must pick one behavior deliberately | |
| `PCRE2_DFA_RESTART` | `0x00000040` | resume a previous `pcre2_dfa_match()` call using its caller-managed workspace array (dfa-match only) | dfa-match only | `NEVER(no resumable-workspace API surface is planned)` — this exists to resume PCRE2's OWN incremental DFA object across calls; pcrec's DFA is a compile-time artifact with no analogous exposed runtime state. Revisit only if `[OS-3]`/streaming specifically wants this exact shape | |
| `PCRE2_DFA_SHORTEST` | `0x00000080` | return the shortest match at the current start position instead of PCRE2's default ordering (dfa-match only) | dfa-match only | `LATER` — genuinely open design question, not confidently placeable: pcrec's DFA already expresses greedy-vs-lazy through pattern syntax (`a*` vs `a*?`), so it's unclear whether a blanket "shortest" runtime override should reinterpret authored greediness or just pick among simultaneously-accepting DFA states. Needs its own design note before any disposition sticks | |
| `PCRE2_SUBSTITUTE_GLOBAL` | `0x00000100` | replace every match, not just the first | substitute-call only | `RIDES(DD-4/M4-SUBST)` — explicit example in the plan row | |
| `PCRE2_SUBSTITUTE_EXTENDED` | `0x00000200` | replacement text may use PCRE2's extended template syntax (conditionals, case-transform escapes) | substitute-call only | `RIDES(DD-4/M4-SUBST)` — same substitution design note | |
| `PCRE2_SUBSTITUTE_UNSET_EMPTY` | `0x00000400` | a reference to an unset capture group in the replacement text substitutes as empty instead of erroring | substitute-call only | `RIDES(DD-4/M4-SUBST)` — same design note | |
| `PCRE2_SUBSTITUTE_UNKNOWN_UNSET` | `0x00000800` | an unrecognised group name/number in the replacement text is treated as unset rather than erroring | substitute-call only | `RIDES(DD-4/M4-SUBST)` — same design note | |
| `PCRE2_SUBSTITUTE_OVERFLOW_LENGTH` | `0x00001000` | when the output buffer is too small, keep computing the REQUIRED length instead of stopping at the error, so the caller can retry with a bigger buffer | substitute-call only | `RIDES(DD-4/M4-SUBST)` — a buffer-management contract question for the same generated substitution API surface | |
| `PCRE2_NO_JIT` | `0x00002000` | skip a JIT-compiled matcher even if one exists (not for dfa-match) | match-call | `NEVER(no JIT exists to skip)` | |
| `PCRE2_COPY_MATCHED_SUBJECT` | `0x00004000` | `pcre2_match()` takes an internal copy of the subject so match results survive the caller freeing/mutating the original | match-call | `NEVER(pcrec's generated matchers are allocation-free by design)` — an internal defensive copy contradicts the caller-owns-the-buffer model D18's speed-first philosophy commits to; this is a documented non-goal, not a gap | |
| `PCRE2_SUBSTITUTE_LITERAL` | `0x00008000` | treat the replacement text as a literal string, no `$`-escapes at all | substitute-call only | `RIDES(DD-4/M4-SUBST)` — same design note | |
| `PCRE2_SUBSTITUTE_MATCHED` | `0x00010000` | substitute using an ALREADY-COMPUTED `match_data`'s group boundaries instead of re-matching internally | substitute-call only | `RIDES(DD-4/M4-SUBST)` — same design note | |
| `PCRE2_SUBSTITUTE_REPLACEMENT_ONLY` | `0x00020000` | output only the replacement text for each match, not the whole subject-with-substitutions | substitute-call only | `RIDES(DD-4/M4-SUBST)` — same design note | |
| `PCRE2_DISABLE_RECURSELOOP_CHECK` | `0x00040000` | turn off PCRE2's own guard against infinite loops from zero-length recursive subpattern calls (not for dfa-match or jit-match) | match-call | `NEVER(a debugging escape hatch for PCRE2's interpreter, not a semantic the compiled artifact should expose)` — pcrec's architecture (O(n) non-backtracking core, VM engine for captures per M4) needs its own termination argument regardless of caller preference | |

---

## 6. NEWLINE and BSR value sets

Both are CONTEXT settings (`pcre2_set_newline()` / `pcre2_set_bsr()` on a
`pcre2_compile_context`), not option bits. **DD-11 owns this axis in full**
— rows below are placement pointers only, not a re-derivation.

| value set | members | binds | disposition |
|---|---|---|---|
| `PCRE2_NEWLINE_*` | `CR`(1) `LF`(2) `CRLF`(3) `ANY`(4) `ANYCRLF`(5) `NUL`(6) | compile context | `RIDES(DD-11)` — DD-11's own text: *"pcrec is NEWLINE_LF today and that is ANCHORED, not assumed: every oracle measurement runs libpcre2 at options=0 (build default LF on this box)"* |
| `PCRE2_BSR_*` | `UNICODE`(1) `ANYCRLF`(2) | compile context | `RIDES(DD-11)` — `\R`'s BSR setting, same owning row |

---

## 7. Out of scope for this survey

`pcre2_pattern_convert()`'s `PCRE2_CONVERT_*` options (`UTF`,
`NO_UTF_CHECK`, `POSIX_BASIC`, `POSIX_EXTENDED`, `GLOB`,
`GLOB_NO_WILD_SEPARATOR`, `GLOB_NO_STARSTAR`) are a glob/POSIX-BRE/ERE to
PCRE2-pattern TRANSLATOR, orthogonal to compile/match option semantics and
not named in the `[PC-5]` plan row's scope list. Noted here only so a future
reader knows they were seen and deliberately excluded, not missed. Flag for
a future survey if a translator-style consumer is ever proposed.

---

## Summary counts

- Compile/match/dfa top-bit group: 3
- Compile-only bits: 28
- `EXTRA_*` compile-context bits: 17
- JIT options: 5
- Match/dfa-match/substitute shared word: 19
- NEWLINE values: 6, BSR values: 2
- **Total flags/values surveyed: 80**
- Rows carrying independently measured evidence (Appendix): **10** distinct
  flags across 6 probe scenarios (`NOTEMPTY`, `NOTEMPTY_ATSTART`,
  `PARTIAL_SOFT`, `PARTIAL_HARD`, `UNGREEDY`, `DOLLAR_ENDONLY`, `FIRSTLINE`,
  `NO_DOTSTAR_ANCHOR`, plus the inline-modifier interaction for `UNGREEDY`
  and the global-loop pairing for `NOTEMPTY`/`NOTEMPTY_ATSTART`)
- Rows marked `UNMEASURED`: **0** — every row judged subtle enough to need
  evidence had tooling available once the header was recovered from the
  `.deb` (see Source information); nothing was asserted past documentation
  where a probe was warranted

---

## Measurement Appendix

Probe compiled and run in the session scratchpad (not committed):

    gcc -std=c11 -Wall -I<scratch>/pcre2dev/usr/include \
        -o pcre2_probe pcre2_probe.c \
        -l:libpcre2-8.so.0 -L/usr/lib/x86_64-linux-gnu
    ./pcre2_probe

Full transcript:

```
libpcre2 10.46 probe -- pcrec PC-5

-- NOTEMPTY vs NOTEMPTY_ATSTART, pattern "a*", subject "ba" --
plain @0                     MATCH    [0,0) = ""
plain @1                     MATCH    [1,2) = "a"
NOTEMPTY @0                  MATCH    [1,2) = "a"
NOTEMPTY @1                  MATCH    [1,2) = "a"
NOTEMPTY_ATSTART @0          MATCH    [1,2) = "a"
NOTEMPTY_ATSTART @1          MATCH    [1,2) = "a"
  the true discriminator (subject "bb", startoffset 0, no byte is 'a' anywhere):
NOTEMPTY, subj=bb @0         NOMATCH
NOTEMPTY_ATSTART, subj=bb @0 MATCH    [1,1) = ""

-- PARTIAL_SOFT vs PARTIAL_HARD, pattern "catfish|cat", subject "cat" --
plain                        MATCH    [0,3) = "cat"
PARTIAL_SOFT                 MATCH    [0,3) = "cat"
PARTIAL_HARD                 PARTIAL  [0,3) = "cat"

-- UNGREEDY option vs inline (?U)/(?-U), subject "aaa" --
opt=0, pat=a+                MATCH    [0,3) = "aaa"
opt=0, pat=(?U)a+            MATCH    [0,1) = "a"
opt=UNGREEDY, pat=a+         MATCH    [0,1) = "a"
opt=UNGREEDY, (?-U)a+        MATCH    [0,3) = "aaa"

-- DOLLAR_ENDONLY, pattern "a$", subject "a\n" --
plain                        MATCH    [0,1) = "a"
DOLLAR_ENDONLY               NOMATCH

-- FIRSTLINE, pattern "b", subject "a\nb" --
plain                        MATCH    [2,3) = "b"
FIRSTLINE                    NOMATCH

-- NO_DOTSTAR_ANCHOR, pattern ".*a", subject "xxa" via NOTBOL-forced restart semantics --
plain                        MATCH    [0,3) = "xxa"
NO_DOTSTAR_ANCHOR            MATCH    [0,3) = "xxa"
  (NO_DOTSTAR_ANCHOR only changes internal start-optimization,
   verdict/ovector must be identical to plain -- confirms it is a
   pure search-strategy hint, not a semantic option)
```

Probe source (`pcre2_probe.c`, scratchpad-only):

```c
/* PC-5 fact-gathering probe: measured semantics for a handful of PCRE2
 * option flags whose interaction is not obvious from the option-bit
 * comment alone. Linked against the box's installed libpcre2-8 runtime
 * (10.46-1build1) via a header extracted from the libpcre2-dev .deb into
 * the session scratchpad (not installed system-wide; see doc header for
 * the provenance note). Scratch tool only -- never committed.
 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>

static void show_result(const char *label, int rc, pcre2_match_data *md,
                         PCRE2_SPTR subject) {
    if (rc < 0) {
        if (rc == PCRE2_ERROR_NOMATCH) printf("%-28s NOMATCH\n", label);
        else if (rc == PCRE2_ERROR_PARTIAL) {
            PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
            printf("%-28s PARTIAL  [%lu,%lu) = \"%.*s\"\n", label,
                   (unsigned long)ov[0], (unsigned long)ov[1],
                   (int)(ov[1]-ov[0]), subject + ov[0]);
        } else {
            printf("%-28s ERROR %d\n", label, rc);
        }
        return;
    }
    PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
    printf("%-28s MATCH    [%lu,%lu) = \"%.*s\"\n", label,
           (unsigned long)ov[0], (unsigned long)ov[1],
           (int)(ov[1]-ov[0]), subject + ov[0]);
}

static void one_match(const char *label, const char *pat, uint32_t copt,
                       const char *subj, PCRE2_SIZE start, uint32_t mopt) {
    int errcode; PCRE2_SIZE erroff;
    pcre2_code *re = pcre2_compile((PCRE2_SPTR)pat, PCRE2_ZERO_TERMINATED,
                                    copt, &errcode, &erroff, NULL);
    if (!re) {
        PCRE2_UCHAR buf[120];
        pcre2_get_error_message(errcode, buf, sizeof buf);
        printf("%-28s COMPILE FAIL: %s\n", label, buf);
        return;
    }
    pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
    int rc = pcre2_match(re, (PCRE2_SPTR)subj, strlen(subj), start, mopt, md, NULL);
    show_result(label, rc, md, (PCRE2_SPTR)subj);
    pcre2_match_data_free(md);
    pcre2_code_free(re);
}

int main(void) {
    printf("libpcre2 %d.%d probe -- pcrec PC-5\n\n", PCRE2_MAJOR, PCRE2_MINOR);

    printf("-- NOTEMPTY vs NOTEMPTY_ATSTART, pattern \"a*\", subject \"ba\" --\n");
    one_match("plain @0",              "a*", 0, "ba", 0, 0);
    one_match("plain @1",              "a*", 0, "ba", 1, 0);
    one_match("NOTEMPTY @0",           "a*", 0, "ba", 0, PCRE2_NOTEMPTY);
    one_match("NOTEMPTY @1",           "a*", 0, "ba", 1, PCRE2_NOTEMPTY);
    one_match("NOTEMPTY_ATSTART @0",   "a*", 0, "ba", 0, PCRE2_NOTEMPTY_ATSTART);
    one_match("NOTEMPTY_ATSTART @1",   "a*", 0, "ba", 1, PCRE2_NOTEMPTY_ATSTART);
    printf("  the true discriminator (subject \"bb\", startoffset 0, no byte is 'a' anywhere):\n");
    one_match("NOTEMPTY, subj=bb @0",          "a*", 0, "bb", 0, PCRE2_NOTEMPTY);
    one_match("NOTEMPTY_ATSTART, subj=bb @0",  "a*", 0, "bb", 0, PCRE2_NOTEMPTY_ATSTART);
    printf("\n");

    printf("-- PARTIAL_SOFT vs PARTIAL_HARD, pattern \"catfish|cat\", subject \"cat\" --\n");
    one_match("plain",        "catfish|cat", 0, "cat", 0, 0);
    one_match("PARTIAL_SOFT", "catfish|cat", 0, "cat", 0, PCRE2_PARTIAL_SOFT);
    one_match("PARTIAL_HARD", "catfish|cat", 0, "cat", 0, PCRE2_PARTIAL_HARD);
    printf("\n");

    printf("-- UNGREEDY option vs inline (?U)/(?-U), subject \"aaa\" --\n");
    one_match("opt=0, pat=a+",         "a+",      0,                "aaa", 0, 0);
    one_match("opt=0, pat=(?U)a+",     "(?U)a+",  0,                "aaa", 0, 0);
    one_match("opt=UNGREEDY, pat=a+",  "a+",      PCRE2_UNGREEDY,   "aaa", 0, 0);
    one_match("opt=UNGREEDY, (?-U)a+", "(?-U)a+", PCRE2_UNGREEDY,   "aaa", 0, 0);
    printf("\n");

    printf("-- DOLLAR_ENDONLY, pattern \"a$\", subject \"a\\n\" --\n");
    one_match("plain",           "a$", 0,                    "a\n", 0, 0);
    one_match("DOLLAR_ENDONLY",  "a$", PCRE2_DOLLAR_ENDONLY,  "a\n", 0, 0);
    printf("\n");

    printf("-- FIRSTLINE, pattern \"b\", subject \"a\\nb\" --\n");
    one_match("plain",      "b", 0,               "a\nb", 0, 0);
    one_match("FIRSTLINE",  "b", PCRE2_FIRSTLINE,  "a\nb", 0, 0);
    printf("\n");

    printf("-- NO_DOTSTAR_ANCHOR, pattern \".*a\", subject \"xxa\" via NOTBOL-forced restart semantics --\n");
    one_match("plain",              ".*a", 0,                       "xxa", 0, 0);
    one_match("NO_DOTSTAR_ANCHOR",  ".*a", PCRE2_NO_DOTSTAR_ANCHOR,  "xxa", 0, 0);
    printf("  (NO_DOTSTAR_ANCHOR only changes internal start-optimization,\n");
    printf("   verdict/ovector must be identical to plain -- confirms it is a\n");
    printf("   pure search-strategy hint, not a semantic option)\n");
    printf("\n");

    return 0;
}
```
