# Known issues — confirmed pcrec bugs (deferred fixes)

Confirmed correctness bugs in pcrec itself (distinct from docs/upstream_issues.md,
which tracks OTHER engines). Each has a minimal repro and a scheduled fix. Repros
live in tests/known_fail/ (NOT run by `make test`, so the suite stays honest about
what it certifies) and become passing regressions when fixed.

Status: `deferred` (scheduled) | `fixing` | `fixed` (moved to a passing corpus).

---

## K1 — FIXED 2026-08-09 (R2)

Zero-width `$` lost priority to a consuming alternative in a repeated group.
Root cause turned out to be general, not `$`-specific: `clo_visit` cut the
ε-path re-entering a loop-entry split, so an empty iteration never reached the
loop exit and never took its rightful priority. Same defect as R2-S1.
**Fix:** loop-entry states are marked in the NFA; on ε re-entry the closure
follows the loop EXIT once (PCRE's empty-iteration rule). Regressions moved to
tests/base/review_r2.rxt (passing). Note the original entry's scoping claim
("ENG_ATTEMPT only") was WRONG — the bug was live in both engines.

---

## K2 — OPEN, deferred to module 'backrefs' (found 2026-08-09, R4 critic pass)

pcrec's diagnostic for `\1`..`\9` describes a PCRE2 behaviour that does not
exist. It reads:

    $ build/pcrec -p rx -o /dev/null '\1'
    pcrec: \1 (backreference/octal) requires module 'backrefs' (pattern offset 0)

"backreference/octal" implies PCRE2 falls back to an octal escape when the
referenced group is absent. It does not — that is Perl/PCRE1 behaviour. Measured
against libpcre2 10.46 via pcre2_compile_8:

    \1  \7  \8  \9   -> error 115 "reference to non-existent subpattern"
    (a)\1  (a)(b)(c)\3 -> accepted
    (a)\2             -> error 115
    \0  \012  \o{101}  -> accepted (the genuine octal forms)

So a SINGLE digit `\1`..`\9` is unconditionally a backreference, and `\0` —
which shares the same diagnostic — can never be one at all, since there is no
group 0.

**R6 CORRECTION, 2026-08-10 — the paragraph above generalised from single digits
and is wrong about the rest.** For a MULTI-digit sequence the reading depends on
the running capture count. Re-measured independently:

    (a)\12                           vs "a\n"           -> match   (octal 012)
    (a)\12                           vs "aa2"           -> nomatch
    (a)(b)...(l)\12  (twelve groups)  vs "abcdefghijkll" -> match   (backref 12)

Same three bytes, opposite constructs, decided by how many capture groups the
parser has seen SO FAR — a forward declaration does not count. So
"(backreference/octal)" is not simply wrong: it is RIGHT for `\ddd` and for
`\0`, and wrong only for a bare single digit.

That makes the fix subtler than this entry first implied. **The correct message
is not a constant** — it depends on parser state the doorway cannot see (D24's
"THE LIMIT OF THE TABLE"). Module 'backrefs' must carry a running capture count
and choose the diagnostic after consulting it.

**Severity: cosmetic today.** pcrec rejects all ten either way, so nothing
miscompiles; the message merely misdescribes PCRE2. It is recorded because the
message becomes wrong ADVICE once module 'backrefs' exists, and because
src/parse/registry.c's notes now state the correct semantics while parse.c still
prints the old text — a divergence that must be resolved rather than forgotten.

**Not fixed now on purpose:** SR-2's acceptance bar is byte-identical output
across the corpus, and changing this string would break that proof for no
correctness gain. **Fix with:** module 'backrefs' (or SR-6), splitting `\0` from
`\1`..`\9`. No tests/known_fail/ repro: the current behaviour is a rejection,
not a wrong match, so there is no failing regression to ratchet.

---

## K3 — FIXED 2026-08-10 (FIX-2)

**Fixed by giving the `:` row `RF_CLASS_DELIM`**, the flag its two neighbours
already had, plus a new `open_msg` field for the one thing that genuinely
differs by position. Both halves went at once, as this entry said they must:
the over-ACCEPTANCE (`[:alpha:]` compiled a matcher for `{: a l p h}`) and the
over-REJECTION (`[a[:b]`, `[[:alpha]`, `[[:]` refused although PCRE2 compiles
them). All five known-wrong pins in tests/reject/ fired on the way past and have
graduated into the normal tables.

**The schema question this entry left for Frank was answered by D26, and the
answer was smaller than the question.** A fifth doorway kind (`RK_CLASSOPEN`)
was proposed because PCRE2 uses different WORDING at a class's own bracket. D26
makes wording tier 3, so that reason evaporated — but a real tier-2 distinction
survived it: inside a class the construct is one PCRE2 SUPPORTS (name the
module), and at the class's own bracket it is one PCRE2 will never accept (name
no module, because none can make it legal). One field, `open_msg`, encodes that.
No new kind, no `RK_COUNT` change, no sweep change.

**And FIX-2 closed the doorway's own over-promise while it was there**
(R8/C4-7): the 14 POSIX class names — 16, once the differential found
`[[:<:]]` and `[[:>:]]` — are now a measured table, so `[[:foo:]]` is "unknown
POSIX class name" rather than a promise that module `classes` will implement it.

Historical record follows.

## K3 — as recorded when OPEN, found 2026-08-10 (SR-2 sabotage validation)

pcrec ACCEPTS `[:alpha:]` as an ordinary five-character class. PCRE2 rejects it.

    $ build/pcrec -p rx -o /dev/null '[:alpha:]'     # accepted
    pcre2:  compile error at offset 0: POSIX named classes are supported
            only within a class

**This is the third find of one shape**, after `\v` and the POSIX collating
elements: pcrec assigns a meaning to a pattern PCRE2 refuses, and python `re` —
the base-tier oracle — accepts it too, so the corpus is structurally unable to
notice. Measured against libpcre2 10.46, not inferred:

    [:alpha:]  [::]  [:ab:]c  [:^alpha:]  [:a:]  [:foo:]  -> ERROR at offset 0
    [:alpha]   [:alpha:x]  [:a.]  [=a:]  [:]              -> accepted
    [^:alpha:]                                            -> accepted
    [x[:alpha:]]  [[:alpha:]]                             -> accepted (POSIX class)

The rule is one pcrec already implements for the two other delimiters: at a
class's OWN opening bracket, `:` behaves exactly like `.` and `=` — it opens a
delimiter-pair construct when the matching `:]` appears later, and a negated
class suppresses it because `^` sits between the bracket and the delimiter.
pcrec has `RF_CLASS_DELIM` rows for `.` and `=` and none for `:`. The 2026-08-09
survey that found the collating bug read `[[.` and `[[=` and did not read `[:`
at class open.

**How it surfaced is the part worth keeping.** Nothing found this by reading the
spec. SR-2 introduced an `at_class_open` guard to preserve existing behaviour,
and the sabotage battery reported that DELETING that guard changes 0 of 4173
hashed emission cases and breaks no test in the suite. A branch no test can see
was the signal; the divergence was what sat behind it. "Which of my new branches
is invisible?" is a question worth asking of every change.

**Severity: over-acceptance**, which D24 rates as seriously as under-acceptance —
pcrec compiles a matcher for a pattern PCRE2 would refuse, so a caller migrating
from PCRE2 gets silent behaviour where they expected a compile error. It cannot
miscompile a pattern PCRE2 accepts.

**The open question in this entry is now measured, and it is a SECOND bug with
the same root cause.** `[a[:b]` was recorded above as unmeasured. Two R5 critics
measured it independently:

    [a[:b]  [[:b]  [[:alpha]  [[:]  [[:a]  [[:^a]  [x[:a]y]   -> PCRE2 ACCEPTS
                                                               -> pcrec REJECTS
                  "POSIX class [:...:] requires module 'classes'"

So the `:` row is missing BOTH halves of `RF_CLASS_DELIM`, and each half is a
bug in the opposite direction: without the class-open half pcrec over-ACCEPTS
`[:alpha:]`, and without the terminator half it over-REJECTS `[a[:b]`. The
second is the one that costs users today — `[a[:b]` is a pattern a person
plausibly writes, and pcrec answers it by naming a module that has nothing to do
with it. It also does NOT go away when module 'classes' lands: the recognition
rule is wrong, not the implementation status.

**Fix (both halves, one change):** give the `:` row the delimiter-pair rule the
`.` and `=` rows already have. Note the diagnostic differs by position — PCRE2
says "POSIX named classes are supported only within a class" at a class's own
bracket and treats `[[:alpha:]]` as a real POSIX class — so one row cannot carry
both messages, and the natural shape is a fifth doorway kind for the class-open
position. That is a D24 schema decision and wants Frank's steer.

**Not fixed in SR-2 on purpose:** SR-2's acceptance bar is byte-identical output,
and this is a behaviour change. Fix it with K4, which lives in the same loop.

---

## K4 — FIXED 2026-08-10 (FIX-2)

**All three scan rules landed together, as this entry insisted.** The scan now
stops at the end of the CLASS rather than the end of the pattern.

**Rule 3 is the one worth reading this entry's wording for.** It says "skip `\]`
and `\\` as a unit", and that is exact. I implemented it twice as something
looser — first "skip any `\X`", then "suppress only a class-ending `]`" — and
PC-3's generated sweep refuted both within minutes. Four measured patterns
separate the three candidate rules, and no weaker rule gets all four:

    [[.\.]]      REJECT   `\.` is NOT a unit, so `.]` closes the pair
    [[.a\\]x.]   accept   `\\` IS a unit, so the `]` is unescaped and ends
                          the class before `.]` is reached
    [a[.b\].]    REJECT   `\]` IS a unit, so that `]` does not end the class
    [[.b].]      accept   a bare `]` ends the class

All four are pinned in tests/reject/, two of them in the MANIFEST as the only
rows ruling out each wrong rule.

**Rule 2 was nearly shipped as an invisible branch.** Deleting it changes no
VERDICT — pcrec rejects the same patterns either way — so a 1680-pattern
generated differential stayed at zero failures without it. What it changes is
the error OFFSET: with it, `[[.a[.b.].]` blames offset 4, the inner opener PCRE2
actually recognises; without it, offset 1, the outer bracket PCRE2 abandoned.
Now pinned. See D26's note on why "don't chase PCRE2's offsets" does not mean
"offsets don't matter".

Historical record follows.

## K4 — as recorded when OPEN, found 2026-08-10 (R5 critics, two independently)

`RF_CLASS_DELIM`'s terminator scan runs to the end of the PATTERN, not the end
of the character class, so a `.]` or `=]` anywhere later — including well
outside the class — makes an ordinary `[.` look like a collating element.
pcrec rejects patterns PCRE2 compiles:

    [.a]x.]   [.a]$.]   x[.a]y.]   [=a]x=]   [a[.b]c.]   [a[.b]xy.]
    [[.a].]   [.a].]    [a[.b]c]d.]           -> PCRE2 ACCEPTS, pcrec REJECTS

`[a[.b]c]d.]` is the sharpest: the `.]` pcrec matched sits at offset 9, outside
the class, which closed at offset 7. The scan reads past the construct's own
boundary.

Measured against PCRE2 10.46, whose rule has three parts the current loop has
none of. Abort the scan when you meet: an unescaped `]` (the class ended); a `[`
followed by the same delimiter (a NESTED opener wins — `[[:a[:alpha:]]` compiles
in PCRE2 because it abandons the outer opener and recognises the inner one); and
skip `\]` and `\\` as a unit. **The three must land together** — adding the `]`
rule without the escape rule flips `[a[.b\].]` from correct rejection to
over-acceptance.

**Pre-existing, not an SR-2 regression:** SR-2 moved `reject_collating`'s loop
verbatim, so the byte-identity proof correctly reported no change. That is worth
stating plainly, because it is the honest limit of an identity proof — **it
cannot see a bug that both sides share.**

**Why the defence missed it:** all seven collating accept-controls in
tests/reject/ put the class at the END of the pattern. Not one appends anything
after the closing `]`, which is exactly the shape that fails. The comment above
them says over-rejection "is the opposite failure and just as wrong" — and that
is the failure they do not cover. Add accept-controls with trailing text in the
same change.

---

## K5 — FIXED 2026-08-10 (FIX-1) — was a MISCOMPILE

A `{m,n}` count above 65535 is silently reinterpreted as literal text.
`try_quant` treats the overflow as "not a quantifier", restores the cursor, and
`{` becomes a literal. PCRE2 raises error 105, "number too big in {} quantifier".

    a{65536}   a{0,65536}   a{100000}   -> PCRE2 error 105; pcrec ACCEPTS

And it does not merely accept — it compiles a matcher for a DIFFERENT LANGUAGE.
The emitted code matches the eight literal characters `a{65536}` and does not
match a run of `a`s. This is the one class the project charter rules out:
"unsupported constructs must fail with a clean error, never miscompile". A user
who writes `a{70000}` gets working, wrong code and no diagnostic.

The boundary is correctly placed on the other side — `a{65535}` is a quantifier
to both engines. Base-tier defect: no registry row and no "requires module"
diagnostic stands between the user and it.

**Fix (FIX-1).** `try_quant` now REMEMBERS the overflow instead of declining on
it, and raises "number too big in {m,n} quantifier" only where it would have
returned true. That two-phase shape is not a nicety — it is what PCRE2 does, and
skipping it over-reaches. Measured against libpcre2 10.46:

    a{65536}  a{100000}  a{0,65536}  a{65536,}  a{,65536}
    a{65535,65536}  a{65536,1}  a{99999999999999999999}   -> error 105
    a{65536   a{65536x}  a{65536,x}                       -> COMPILE, literal

Two orderings that had to be measured rather than guessed: **too-big beats
out-of-order** (`a{65536,1}` is 105, not 104 — and the clamped accumulator makes
it look out-of-order internally, so getting this backwards is a live mistake),
and the reported offset is where the offending number's digits ran out, which
is why each number's end position is kept separately. pcrec's offsets now match
PCRE2's exactly on all eight.

**One inconsistency this introduces, deliberately left alone:** the neighbouring
"numbers out of order" error still reports the `{`, where PCRE2 reports the
closing `}` (`a{3,1}` → pcrec offset 1, PCRE2 offset 5). Aligning it is a
behaviour change to a message that predates this work and wants its own
decision, not a silent ride-along.

**Coverage:** 8 rows in `tests/reject/` pinning the DIAGNOSTIC, 8 corpus `perr`
blocks (7 marked `# pcre2-only` — see U5), 3 over-reach accept-controls, and
`(?:){65535}` pinning the boundary itself. Sabotage-validated: reverting the fix
costs 9 reject + 9 corpus checks; raising the overflow where it is DETECTED
rather than CONFIRMED costs 3 + 5; moving the ceiling to 65534 costs exactly
1 — the boundary pin, and nothing else in the repo.

---

## K6 — FIXED 2026-08-10 (FIX-1) — was a MISCOMPILE

A well-formed `{m,n}` with nothing to quantify is silently literal text.
`try_quant` is only ever called from `p_rep`, AFTER an atom has been parsed, so
a `{` reached by `p_atom` is never tested for quantifier-hood at all.

    {1}   {2,3}   {,5}   {1,}   {1}a   a|{1}   ({1})   (?:{1})
        -> PCRE2 error 109 "quantifier does not follow a repeatable item"
        -> pcrec ACCEPTS, and matches the literal characters

pcrec already has the correct behaviour for `*`, `+` and `?` in that position
(`*a` is rejected at offset 0, agreeing with PCRE2) and is missing it only for
`{`. The discriminator is exactly "did it parse as a quantifier", which
`try_quant` already computes and nobody asks in atom position.

**The fix must not over-reach.** The MALFORMED brace forms are literal in both
engines and must keep compiling: `a{`, `a{}`, `a{,}`, `a{1`, `}`.

**Fix (FIX-1).** `p_atom` gained a `case '{'` beside the existing `* + ?` case.
It rewinds to the `{`, asks `try_quant`, and fails with error 109 only if the
answer is yes; otherwise the `{` is consumed as a literal exactly as before. The
over-reach guard is structural rather than a second list: "malformed" IS
"`try_quant` declined", so the two rules cannot drift apart.

`try_quant` may also fail from inside, and that turns out to be the order PCRE2
uses — measured, `{65536}` is 105 and `{3,1}` is 104, neither is 109. A fix that
asked "is anything repeatable" first would answer all twelve plain cases
correctly and both of these wrongly. Offsets match PCRE2 throughout, because
PCRE2 reports the closing `}` and that is where `try_quant` leaves the cursor.

**Coverage:** 12 rows in `tests/reject/` (10 plain + the two precedence cases),
12 corpus `perr` blocks — python `re` calls these "nothing to repeat", so no
oracle exclusion was needed — and 11 malformed-brace accept-controls with
literal-match corpus cases behind them. Sabotage-validated: reverting the fix
costs 12 reject + 12 corpus checks; the over-reach ("any `{` in atom position is
an error") costs 13 + 18.

---

## K8 — FIXED 2026-08-10 (R7, same checkpoint it was found in) — was a MISCOMPILE

pcrec did not accept SPACE or TAB inside a `{m,n}` quantifier. PCRE2 10.46 does,
following Perl 5.34, so every such pattern was silently demoted to literal text.

    a{ 1}   a{1 }   a{ 1 }   a{1, 2}   a{1 ,2}   a{<TAB>1}
        -> PCRE2: a quantifier; matches ONE 'a'
        -> pcrec: five or more literal characters

**Found by R7's spec critic, and how it was found is the point.** The session's
own 49 hand-picked probes missed it completely, because in QUANTIFIER position
both engines exit 0 — a verdict-only comparison sees nothing, and only the
compiled language differs. The critic generated the brace space combinatorially
instead of listing it, and got 90 verdict disagreements in ATOM position (`{ 1}`
is PCRE2 error 109, pcrec accepted it) plus the silent pair above. It is the
same class as K5 and K6, undetected by the same instrument that had just been
used to certify them.

**The rule, measured gap by gap against libpcre2 10.46 rather than inferred:**

    tolerated bytes:  0x20 space, 0x09 tab — and NO others. 0x0a 0x0b 0x0c 0x0d
                      and 0xa0 all leave the brace literal in both engines.
    positions:        all four gaps, `{` _ m _ `,` _ n _ `}`, any run, mixed.
    never:            inside a number (`a{1 2}` is literal, not `a{12}`), and
                      never in place of one (`a{ }`, `a{ , }`, `a{ ,}` stay
                      literal exactly as `a{}` and `a{,}` do).

**Fix:** a four-line `skip_quant_space` called at exactly those four gaps. Both
"never" clauses fall out of skipping only at the gaps, so there is no second
rule to keep in step. The calls sit AFTER each `end_m`/`end_n` assignment
because PCRE2 reports the offset where the DIGITS ran out — `a{65536 }` is
error 105 at offset 7, the space itself, not at the `}`.

**The oracle situation is the `\v` shape again**: python `re` reads every one of
these as literal, agreeing with the bug, so the tolerated forms cannot be
python-verified (U6) and carry `# pcre2-only`. The bytes that must NOT be
skipped agree with python and are verified normally.

**One test-design trap, recorded because it cost a sabotage to find.** The
obvious corpus guard — `pattern a{\n1}` — does not guard anything. A `.rxt`
pattern line cannot carry a raw control byte, and `\n` written in a pattern is
an escape pcrec decodes in ATOM position, long after `try_quant` has looked at
the brace and seen a backslash. Substituting `isspace()` for the real test left
every such case passing. The working guard needs a raw byte and a discriminating
shape (`a{<LF>65536}` compiles iff the byte is not skipped) and lives in
`tests/reject/`, where bash can supply the byte.

Sabotage-validated: reverting all four gaps costs 5 reject + 12 corpus checks;
`isspace()` costs 4; dropping one gap costs 1 + 4; skipping digits at the gaps
costs 25 + 57; moving the skip before `end_m` costs 1.

---

## K7 — OPEN, found 2026-08-10 (FIX-1, while probing the 65535 boundary)

A large BOUNDED repeat exhausts memory and the process is SIGKILLed, instead of
reaching the DFA state cap that exists to prevent exactly this.

    $ build/pcrec -p rx -o /tmp/o.c 'a{0,65535}'
    Killed                                          # rc 137, empty stderr

**Re-measured 2026-08-10 by a spec-first writer (D27), with two consequences
this entry did not previously record.** `a{65535}` does reach its clean "too
complex" diagnostic — but only after 23.9 s and 2.1 GB RSS, and under a 2 GB
address-space limit `pcrec_compile` ABORTS THE CALLER'S PROCESS with no
diagnostic at all. pcrec is a library; killing the caller is a worse failure
than the SIGKILL recorded below, because a caller that set a limit did so
precisely to avoid this. `a{0,20000}` compiles at 4.7 GB / 49.5 s. The writer
also found TWO CLAIMS IN docs/pcre2_compliance.md that are wrong as written
about this boundary — reconcile them when K7 is fixed.

Measured on a pinned build of `c38934c`, so it PREDATES FIX-1 and is not a
regression from it:

    a{0,65535}   a{,65535}   a{1,65535}   a{0,40000}   -> SIGKILL (rc 137)
    a{0,20000}                                         -> compiles, rc 0
    a{65535}                                           -> clean rc 1,
        "pattern too complex for the DFA engine (>32000 states)"

So the EXACT-count form degrades cleanly and the bounded-optional form does not:
`{0,n}` builds an optional chain that blows past the memory the cap was meant to
bound, before the cap is ever consulted.

**Threshold narrowed by R7's spec critic under `ulimit -v 6000000`**, and the
numbers are worse than "it dies above 40000":

    a{0,20000}              4.68 GB peak RSS, 15.2 s   -> ACCEPTED
    a{0,25000}                                         -> SIGABRT (cap hit)
    a{0,30000}                                         -> SIGKILL
    a{0,32001} .. a{0,65535}                           -> SIGABRT (cap hit)

The `>32000 states` guard is therefore UNREACHABLE for this shape — the process
dies of memory before the state count is consulted — and the last form that
succeeds already costs 4.7 GB. That is the sharper statement of the bug: not
"large repeats crash" but "the cap that exists to prevent this cannot be
reached by the shape that needs it".

No crash of a different shape was found: nested small counts
(`((((a{16}){16}){16}){16})`, `(a{200}){200}`) and exponential subset blowups
reject cleanly with the DFA-guard message once given enough memory.

**Severity: not a miscompile.** No wrong code is emitted and nothing is silently
accepted; the failure is loud, just not clean. It still violates the softer half
of the mandate — a caller gets no diagnostic, no exit code they can interpret,
and on a memory-constrained machine the OOM killer may pick a different victim
entirely.

**Not fixed now on purpose:** FIX-1's scope is the two miscompiles, and the fix
here is a size estimate BEFORE construction (or the M4 VM engine), which is a
design decision about where the cap lives rather than a parser bug. No
`tests/known_fail/` repro: a SIGKILL is not a `perr` (the harness correctly
treats rc >= 124 as a crash, not a rejection), so pinning it needs a
purpose-built check. **Fix with:** M4, or a bounded-repeat pre-estimate.

---

_Four open issues: K2 (cosmetic), K3 and K4 (over-rejection / over-acceptance in
the class-bracket doorway, one fix — FIX-2), K7 (a large bounded repeat is
SIGKILLed rather than diagnosed; not a miscompile). **No open MISCOMPILE
remains** — K5 and K6 were fixed on 2026-08-10 by FIX-1, and K8 by R7's critic
panel the same day. Note that K8 was found in the checkpoint review OF the K5/K6
fix, in the same function, by an instrument the fix itself had not used: worth
remembering before treating a construct as finished. Performance and
architecture debt lives in docs/plan.md; other engines' bugs in
docs/upstream_issues.md._


## K9 — OPEN, found 2026-08-10 (D27 spec-first writer, contract lens)

`pcrec_compile()` takes a NUL-TERMINATED pattern and no length, so a pattern
containing a NUL byte is silently TRUNCATED and the compile reports SUCCESS for
a different pattern than the caller passed.

    pattern "a\0b" (3 bytes)  ->  pcrec compiles `a`, returns 0
    libpcre2 (given the length) ->  compiles the real 3-byte pattern

This is not reachable through argv or through a line-based corpus, which is why
no existing test could express it — `tests/registry/pcre2_check.c`'s
`check_embedded_nul` probes the VERB doorway and says so explicitly, noting that
"pcrec's public entry point takes a NUL-terminated pattern". That comment
recorded the limitation; nothing recorded that it produces a WRONG SUCCESS
rather than a clean refusal, which is the part that matters under the mandate.

Two honest options, and the choice is a public-API decision rather than a bug
fix: take a length in the public API (a breaking change, and DD-3 territory), or
document that patterns are NUL-terminated AND refuse a pattern whose declared
extent the compiler cannot verify. Doing neither leaves a silent wrong compile
in the library's front door.

**Scheduled:** with DD-3 (generated-API versioning/compat policy), because both
are changes to the public contract and should be decided together.

## K10 — FIXED 2026-08-12 (MOD-0.6 phase 2, the K10 slice)

**Resolution.** `RF_CLASS_INVALID` removed from the `{U+` row
(`src/parse/registry.c`, the `\N{U+0041}` row) — the one-flag fix this entry
always said it was. `[\N{U+41}]` now falls through to the ordinary `RS_MODULE`
in-class branch in `ext.c` and reads `\N in a class requires module
'unicode-props'` at the same offset as before (measured: offset unchanged,
1/2/3 for the three repro cells below — `ext.c`'s in-class branches share one
`at`). Bare `\N` in a class is UNCHANGED (`registry.c:310`'s row correctly
keeps the flag; err 171 stays permanent). **The TEST is what this entry always
said was the real work**: the in-class sweep's one-byte-of-tail blindness
(the fourth net below) is closed in the SAME commit by extending
`registry_check.c`'s sweep to probe every tailed/body-carrying row through its
own `syntax` field wrapped in `[...]` — see `docs/design_notes_mod06.md` §4
for the design and `tests/registry/CLAUDE.md` for what landed. Reject-pins for
the new message + offset are in `tests/reject/run_reject_tests.sh`; mech
sabotage `S31` re-flags the row and is caught by the extended sweep.

**Original finding, kept for the history** (R10 panel, C1, found 2026-08-11 —
while probing the ambiguity guard). `\N{U+hhhh}` inside a character class was
refused as permanently-invalid, when PCRE2 recognises it. A tier-2 error,
EXACT under D26: pcrec answered REFUSE where the correct answer is "requires
module 'unicode-props'".

**Repro** (measured 2026-08-11, `build/pcrec` at 2aca7dd):

    $ build/pcrec -o /dev/null -- '[\N{U+41}]'
    pcrec: \N is not valid inside a character class (pattern offset 1)
    $ build/pcrec -o /dev/null -- '[x\N{U+41}]'
    pcrec: \N is not valid inside a character class (pattern offset 2)
    $ build/pcrec -o /dev/null -- '[a-\N{U+41}]'
    pcrec: \N is not valid inside a character class (pattern offset 3)

libpcre2 10.46, every class position including range endpoint and after `^`:

    [\N]           err 171  \N is not supported in a class      <- genuinely not a construct
    [\N{U+41}]     err 193  \N{U+dddd} is supported only in Unicode (UTF) mode
    [x\N{U+41}]    err 193
    [\N{U+41}x]    err 193
    [a-\N{U+41}]   err 193
    [^\N{U+41}]    err 193

Error 171 for bare `\N` is a real refusal. Error 193 for `\N{U+...}` is PCRE2
parsing it as an ordinary class member and then refusing the MODE — a code point
is a perfectly good class member.

**The defect.** `src/parse/registry.c:257-259`, the `{U+` row, carries
`RF_CLASS_INVALID`. It should not. The flag's definition is "PCRE2 forbids this
construct INSIDE a character class, permanently — no option, no version, no
future in which it means anything", and **the row's own `note` says the
opposite**: *"PCRE2 error 193 outside UTF mode, which is recognition, not
rejection"*. The row states 193 is recognition and then wears the flag meaning
permanent refusal.

Provenance: R9/SPEC-classes-F1 added `RF_CLASS_INVALID` to ten escapes —
`A B G K Z z C R X N` — and it landed on an eleventh row that is not one of the
ten. The bare `\N` row correctly has it; the `{U+` row inherited it.

**Fix.** Remove `RF_CLASS_INVALID` from that row. `ext.c:104-105` then answers
`\N in a class requires module 'unicode-props'`, which is the CLAIM PCRE2's 193
warrants. **The fix is one flag; the TEST is the work**, which is why this is
recorded rather than patched in the same commit as a design review.

**Why four independent nets all miss it, which is the part worth keeping**
(updated at MOD-0.2, 2026-08-11, when the first net was retired — its
successors miss it the same way, so the count of blind nets did not shrink):

- `check_tail_precedence` asked which ROW is selected; the right row IS
  selected. RETIRED at MOD-0.2, and its successors inherit the blindness for
  the same reason: `check_row_ranks` asks whether a tailed row can WIN and
  `check_arbitration_liveness` asks how often more than one recogniser
  ANSWERS — K10 is a wrong FLAG on a correctly-selected row, invisible to
  every question about selection.
- The MOD-0.2 ambiguity defect (née the R10/D29 guard) asks how many
  recognisers answer at the winning rank. One answers.
- `registry_check.c:875-876` **EXEMPTS `RF_CLASS_INVALID` rows from the in-class
  sweep by design** (`skip_flag` — RF_CLASS_INVALID since MOD-0.3d, when the
RF_CLASS_BASE half became the separate `excuse_base_cport` boolean) — so the
  flag exempts the row from the one check that would have contradicted it. A
  control that takes its scope from the field it is controlling.
- The in-class sweep's template is `"[\\%c]"`, one byte of tail context, so it
  can only ever probe `[\N]` and never `[\N{U+41}]`.
- PC-3 probes this row once, in the ATOM position only.

`tests/registry/CLAUDE.md`'s claim "`\N{U+hhhh}` versus `\N` are no longer
unswept" was true only in the atom position until this fix; the class-position
half is what MOD-0.6's tail-sweep extension (§4 of the design note) closes.

## K11 — FIXED 2026-08-11 (MOD-0.1's returned-claims epilogue, D33 §5)

**Resolution.** The four doorways now RETURN their terminal answer as an
`ExtResult` (a tagged value: `EXT_NOT_MINE`, or `EXT_REFUSAL` carrying the
diagnostic formatted at claim time), and every call site consumes the value —
`pcrec_ext_finish` is the one epilogue that renders a refusal, and each site
ends in a loud internal-error wall for any outcome it does not handle. The
`noreturn` declarations and the fall-off-the-end call sites are gone, so the
UB this entry records is structurally unrepresentable: there is no discarded
register value to relaunch and no unreachable end to fall off. Re-ran this
entry's own repro shape against the new contract (scratch tree, stub selector
`q` made to return an unhandled outcome, no other change): `a\qb` and
`[a\qb]` both exit 1 with "internal error: escape doorway returned an
unhandled outcome" at the escape's offset, deterministically, no output file
— where the old shape silently miscompiled the first and crashed the
compiler on the second. Diagnostics byte-identical across the change: a
952-pattern differential over every registry probe, every corpus pattern and
per-doorway byte sweeps compared (exit, stdout, stderr, out.c, out.h)
against the pre-epilogue build with zero differences (instrument
sabotage-validated: one reworded message → 10 caught).

**Still owed elsewhere, on purpose:** the flagged-not-reproduced hazard below
(`esc_class_value`'s value feeding `cls_set`'s 32-byte bitmap with no range
check) is NOT discharged by this fix — nothing returns a scalar yet. The
call-site wall's comment assigns the range check to the first module whose
class port returns one, with a probe that is false today (D33 §9.3).

The original entry follows, unedited, as the record of what the defect was.

## K11 (original entry) — OPEN, found 2026-08-11 (R11 panel, M4 — while probing the returning-doorway contract)

**`pcrec_ext_escape`'s two call sites are UNDEFINED BEHAVIOUR the moment that
doorway starts returning a value**, and the two behave differently in the same
binary. Recorded now rather than at MOD-0.1 because it is a CONFIRMED,
reproduced defect that the design work deliberately scoped OUT, and prose in a
design document is not where a live defect belongs.

**Latent today, and that is the only reason it is not a bug report.** Every path
in `pcrec_ext_escape` ends in `ctx_fail`, and the function is declared
`noreturn`, so no input can reach it. It becomes reachable the moment the first
semantic port lands — `unicode-props` (`\p{...}`), `classes` (`\v`) and any
assertion module all eventually need that doorway to return.

**The defect is in the CALL-SITE SHAPE**, not in any one row, so it applies to
all 41 `RK_ESC` rows and every future one. Both call sites invoke the doorway as
the LAST STATEMENT of a value-returning function with **no `return` in front of
it** — legal only because `noreturn` makes falling off the end unreachable:

    src/parse/parse.c:132-140   esc_atom          returns Ast *
    src/parse/parse.c:145-155   esc_class_value   returns int

**Repro** (scratch copy of the tree; declaration changed from `void ... noreturn`
to a value-returning form, one sentinel selector byte `q` made to return a stub
node; no other change):

    a\qb      exit 0, COMPILES, and the stub node reaches the emitted matcher —
              the discarded pointer is relaunched as esc_atom's own return value
              out of %rax by calling-convention coincidence.  5/5 runs.
    [a\qb]    *** SIGSEGV, exit 139 — build/pcrec, the COMPILER ITSELF, crashes
              before emitting anything.  3/3 runs. ***

gcc emits `-Wreturn-type: control reaches end of non-void function` at BOTH
sites — and the build still exits 0, because there is no `-Werror` by default
(`make strict` would catch it). This is the only doorway where the compiler says
anything at all: `pcrec_ext_group` and `pcrec_ext_verb` produce ZERO warnings
for the identical change, because discarding a return value is silent in C.

**Why this is worse than the group doorway's discard** (which MOD-0.1 fixes):
that one is well-defined C — deterministically the same wrong answer on every
platform. This is UB, and it is not even self-consistent across its own two call
sites in one binary. A different compiler, optimisation level or register
allocation could flip which site crashes and which silently corrupts.

**A related hazard, FLAGGED AND NOT REPRODUCED:** `esc_class_value`'s return
feeds `cls_set(a->cls, (unsigned)lo)` in `p_class` with **no range check between
them**, and `cls_set` indexes `b[c >> 3]` into a 32-byte array. A UB-tainted
`int` arriving there is a memory-safety question, not merely a correctness one.
This run happened to segfault before reaching that path. Worth its own probe
independent of this entry.

**Scheduled:** with the first module that needs doorway 1 to return — currently
MOD-0.6 (`unicode-props`), whichever lands first. **MOD-0.1 deliberately does
NOT fix it** (R11 disposition 6 / M4's ruling): MOD-0.1 owns `p_group_body`'s
discard, which is inseparable from building the interface, and bundling a
second, differently-shaped doorway fix into a large refactor is how a regression
hides. **But note `pcrec_ext_verb` shares `p_group_body` with the group doorway
and IS in MOD-0.1's scope** — see R11 disposition 12; a fix touching only the
`?` branch ships incomplete.

## K12 — FIXED 2026-08-11 (MOD-0.1's endpoint-rule slice, design §16 as R14-corrected)

**Resolution.** p_class implements the five-step evaluation order PCRE2's
5,041-pair sweep established — low's own error → high pair-open short-circuit
→ high's own error → either endpoint certifiably SET-shaped → "invalid range
in character class" → scalar ordering — using the two mechanisms the earlier
slices built for it: the returned-claims epilogue lets the range logic SEE a
doorway refusal before it fires (a claim carries `ep_set_certain`, §16.3(e)'s
verdict-shape payload), and the measured `class_expect` column is what
certifies SET-shape. Certification is deliberately scoped to rows whose
measured value covers EVERY form that reaches them: the ten char-type escapes
(the construct is its selector byte) and the bracket doorway's known POSIX
names (both sides, so `[[:alpha:]-z]` and mid-class `[x[:alpha:]-z]` are 150's
analogue too). Body-dependent rows keep the module promise — `[0-\p{Foo}]` is
PCRE2 147, not 150, so certifying `\p` would trade an over-promise for a
wrong verdict; the boundary is pinned in tests/reject/ and owned by MOD-0.6's
property table. Every cell measured first (tests/probes/probe_endpoint_k12.c,
42 cells), ten failing-then-passing pins plus seven boundary pins and two
accept-controls (counts 265/99/65, three MANIFEST entries); the 952-pattern
differential vs the pre-slice build shows exactly the one changed cell it
contains. `pcrec_ext_class_pair_opens` survives as the (bracket, high)
deviating cell's predicate, exactly as R14 ruled.

The original entry follows, unedited.

## K12 (original entry) — OPEN, found 2026-08-11 (D33 design conversation, while probing the range-endpoint rule)

**A class-type escape at a range endpoint is answered with a module promise
where PCRE2 says the range is permanently invalid.** SPEC-FA implemented the
endpoint rule for the BRACKET shape and not for the ESCAPE shape.

**Repro** (measured 2026-08-11 against libpcre2 10.46 via `tests/fuzz/pcre2_abi.h`;
`build/pcrec` at 5173a82):

                    PCRE2                       pcrec
    [0-\d]      err 150 invalid range     "\d in a class requires module 'classes'"
    [0-\p{L}]   err 150 invalid range     "\p in a class requires module 'unicode-props'"
    [a-\d] [\d-x] [a-\v] [\w-z] [\d-\w]   all err 150 in PCRE2

Controls, where pcrec is already correct and must stay so:

    [\d]        COMPILES in PCRE2 (a class member, not an endpoint)
    [\x41-z]    COMPILES — a SCALAR escape is a legal endpoint
    [a-\x41]    err 108 range out of order — i.e. accepted AS a range
    [0-\N{U+41}] err 193, the construct's own mode error, NOT 150 — scalar-shaped
    [0-\q]      err 103, the escape's own error — no construct claimed

**Severity: not a miscompile, and the wording is not the point.** Both engines
reject all of these, so nothing is compiled wrongly and no user gets a wrong
matcher. Two things make it worth recording:

1. pcrec names a module for a pattern that will NEVER compile. `[0-\d]` must
   still be rejected after module `classes` lands. That is the over-promise
   FIX-2 removed for `[[:foo:]]`, in a place SPEC-FA did not reach.
2. **The guard is the unimplemented-ness.** pcrec is right today only because
   `\d` is refused before `parse.c:213`'s range code can look at it. That code
   is `int hi = esc_class_value(cx)` with `lo > hi` and
   `for (i = lo; i <= hi; i++)` behind it. **MOD-0.2 (`classes`) removes the
   guard**, and at that moment a set-shaped value arrives in an `int`.

This is the exact shape `docs/plan.md:577` already records for `(?xx)[a- ]`, one
construct over: *"pcrec is safe today only because `(?x)` is rejected outright
as 'requires module modifiers' — the guard IS the unimplemented-ness, and this
step removes it."*

**Fix:** D33 §6 — the endpoint rule becomes "did a port claim, and is the ROW'S
SHAPE set-valued", a static column covering the bracket and escape shapes with
one rule. Do not fix it as an escape-specific special case: that is the
"fixing the narrowest instance and calling it the class" error, and it would
leave a third shape (a future set-valued construct at some other doorway)
unguarded again.

**Scheduled:** with MOD-0.1 if D33 is adopted (the rule falls out of the shape
column), otherwise with MOD-0.2 (`classes`), which is the step that makes it
live. No `tests/known_fail/` repro: the current behaviour is a rejection with a
misleading message, not a wrong match, so there is no failing regression to
ratchet — the pins belong in `tests/reject/`.

## K13 — FIXED 2026-08-11 ([FIX-3], the first src/ change of the module era)

**Resolution.** `esc_class_value` now implements the class position's real
semantics, measured cell-by-cell against libpcre2 10.46 first
(tests/probes/probe_fix3.c — 41 cells, predictor stated before the run, zero
disagreements): `\0`..`\7` open an octal escape (up to three octal digits;
above `\377` it is PCRE2 error 151 with wording and offset reproduced), and
`\8` `\9` `\g` `\k` are the LITERAL characters — the complete fallback set
over all 62 `[\c]` probes. Tails re-enter the class as ordinary members
(`[\k<n>]` matches k `<` n `>`) and decoded escapes are ordinary range
endpoints (`[0-\k]`, `[\1-\7]`), with no extra code. The twelve registry rows
carried `RF_CLASS_BASE` (retired at MOD-0.3d, 2026-08-12: the same
semantics are the rows' own BASE class ports now, and the doorway IS
entered at class position, the port answering whatever the enabled set
says) — originally the doorway was never entered at class position —
exactly the `\b` shape — and registry_check's derived in-class expectation
flipped from "requires module" to "compiles" with the flag. Pins:
tests/base/class_escape_fallbacks.rxt (127 cases, written first and watched
fail — 122 failing pre-fix, the 5 `perr` blocks already failing for the wrong
reason) plus the `[\400]`/`[\777]`/`[\377]` boundary rows in tests/reject/
(the only home of the new diagnostic's text). The ATOM position is untouched.
One planned-divergence note: the fix landed BEFORE MOD-0.1's byte-identity
bar, per Frank's §18.4 ruling, so the bar measures true identity with no K13
exception entry. Original entry below, kept for the analysis.

**Historical entry (found 2026-08-11, R13 panel, C4/F21 and C3/F6; independently reproduced by the author):**

**Twelve escape rows answer the CLASS position with the wrong module.** pcrec
promises module `backrefs` for constructs that module can never implement,
because at class position they are not backreferences at all. Tier 2 under D26,
where the standard is exact.

**Repro** (measured 2026-08-11; `build/pcrec` at `5173a82`, libpcre2 10.46 via
`tests/fuzz/pcre2_abi.h`; every libpcre2 line below was re-run by the author,
not taken from the panel):

                    libpcre2                      pcrec
    [\8]        matches "8" — LITERAL     "\8 in a class requires module 'backrefs'"
    [\1]        matches "\001" — OCTAL    "\1 in a class requires module 'backrefs'"
    [\12]       octal 012                 "\1 in a class requires module 'backrefs'"
    [\k]        matches "k", not "\"      "\k in a class requires module 'backrefs'"
    [\g]        matches "g"               "\g in a class requires module 'backrefs'"
    [0-\k]      a RANGE 0x30..0x6b        "\k in a class requires module 'backrefs'"

The rows: the ten `ESC_DIGIT` rows (`\0`..`\9`) plus `\g` and `\k`.

**Three distinct wrongnesses behind one message:**

1. `[\8]` — `8` is not an octal digit, so libpcre2 falls back to the LITERAL
   character `8`. pcrec's base grammar already implements literals.
2. `[\1]`, `[\12]` — octal, which is not module `backrefs` under any reading.
   A backreference is not a class member and never can be.
3. `[\k]`, `[\g]` — libpcre2's `check_escape` treats these inside a class as a
   bad escape falling through to **the literal letter**. There is no construct
   to attribute at all.

**Severity: over-promise, not a miscompile — today.** All twelve are refused, so
nothing wrong is emitted. Two things make it worth recording:

- It is the over-promise FIX-2 removed for `[[:foo:]]`, surviving at the escape
  doorway. Module `backrefs` landing does not make `[\k]` legal; it is two
  literals.
- **It becomes a tier-1 MISCOMPILE the day `backrefs` lands**, if the class
  position is not fixed first: a real `\k` handler would be handed `[\k<n>]` and
  emit a backreference matcher for a pattern that means `[k<n>]` — a wrong
  matcher arriving *because* the module was implemented.

**Why every net misses it, which is K10's list again:**

- `check_table_to_parser` derives the expected in-class string from the row's
  own `module` (`registry_check.c:544`) — the control shares its source with
  what it controls.
- the in-class sweep's template is `"[\\%c]"`, one byte of tail, so `[\12]` is
  unreachable (`registry_check.c:875`) — the same one-byte template that hid K10.
- PC-3 probes each row's `syntax` — `\1` — at the ATOM position only.

**Related and smaller, same family:** `\0` carries module `backrefs` at the ATOM
position too, and `\0` can never be a backreference — there is no group 0. K2
records the diagnostic half of this.

**Fix:** with module `backrefs` / the octal-vs-backref row split (K2, and the
extension design's §10.7). **Do not re-attribute the rows without an in-class
sweep that carries a TAIL** — that is K10's warning, and this entry is what
happens when it is not heeded. No `tests/known_fail/` repro: the current
behaviour is a rejection with a wrong module name, not a wrong match, so the
pins belong in `tests/reject/`.

## K14 — FIXED 2026-08-11 (MOD-0.1's first slice, the D34 item-1 ruling)

**Resolution.** The missing axis is now a COLUMN: `Roadmap` — ROADMAP_PLANNED
/ ROADMAP_NEVER, with ROADMAP_NONE meaning "unset" so registry_check can
require the §17.2 pairings (RS_MODULE rows must declare one; RS_REJECTED must
pair with NEVER; RS_BASE must carry none). It lives on `RegRow` AND on
`VerbName` (per-name with the row's value as default — `(*COMMIT)` is NEVER
while `(*pla:...)` is a planned lookaround in verb spelling). A NEVER
construct in a form PCRE2 would accept now answers
"... is outside pcrec's scope and no module will implement it (see
docs/pcre2_compliance.md)" — real, refused, names no module; malformed forms
keep PCRE2's own form errors. 17 verb names (the five backtracking verbs +
MARK's synonym, the four LIMIT_*, the four NO_* knobs, the two casing
options, scs/scan_substring) and the `(?C` row carry it. The one-source
direction is CHECKED, not generated (R14/C2-F8): `compliance_section.py
--names` asserts prose-OUT-OF-SCOPE ⇔ ROADMAP_NEVER in both directions — and
its first run caught `LIMIT_RECURSION` in the tables but missing from the
survey's row. Pins: 14 rows in tests/reject/ (failing first), two manifest
entries; both dumps carry the column (13-field --list-syntax, 5-field
--list-verbs, consumers updated). Original entry below, kept for the
analysis.

**Historical entry (found 2026-08-11, R13 panel, C5/F13; verified independently by the author):**

**pcrec names a module for constructs its own compliance survey says will never
be implemented.** D26's tier-2 row says this in as many words
(`docs/decisions.md:1457`):

> **exact.** Naming a module that will never implement a construct is a defect;
> so is rejecting syntax PCRE2 accepts

**Repro** (measured 2026-08-11, `build/pcrec` at `5173a82`):

    (*COMMIT)         -> (*...) requires module 'verbs'
    (*PRUNE)          -> (*...) requires module 'verbs'
    (*SKIP)           -> (*...) requires module 'verbs'
    (*MARK:x)         -> (*...) requires module 'verbs'
    (*LIMIT_MATCH=3)  -> (*...) requires module 'verbs'
    \d                -> \d requires module 'classes'      <- ACTIVELY PLANNED (MOD-0.2)

The first five and the last are **indistinguishable to a caller**, and they are
opposite promises.

`docs/pcre2_compliance.md:301` says of the backtracking verbs, in its own words:

> `OUT-OF-SCOPE` — these are DEFINED in terms of a backtracking engine's search
> order [...] A simulation engine explores all alternatives at once, so there is
> no backtracking tree to prune. PCRE2's own DFA matcher supports none of them.

and `:221` of the `LIMIT_*` family:

> `OUT-OF-SCOPE` — these bound a BACKTRACKING search. pcrec is O(n) by
> construction, so there is nothing to limit.

These are **architectural exclusions under D22, not backlog.** Module `verbs`
will exist — it is MOD-0.4 — but it will never implement these constructs, so
naming it is precisely the defect D26 defines.

**Weaker, same family, recorded for completeness:** `(?C1)` answers "requires
module 'callouts'", and `pcre2_compliance.md:307` marks callouts `OUT-OF-SCOPE`
*"for now [...] Revisit only with a concrete customer"*. That is a genuine
"not yet" rather than a "never", so it is a lesser instance — but a caller
cannot tell it from either of the other two.

**The missing distinction is an AXIS, not a status** (C5/F13). Three axes are
needed and the table has two:

    1. what PCRE2 does        RS_BASE / RS_MODULE / RS_REJECTED
    2. what this compile does  enabled / disabled     (proposed, not built)
    3. what pcrec will EVER do  will implement / never will   <-- ABSENT

Axis 3 is a fact about pcrec's roadmap: it is not a fact about PCRE2, so axis 1
cannot hold it, and it is not a fact about one compile, so axis 2 cannot hold
it. `docs/extension_design.md` §7.2 proposes `RS_NOT_OFFERED` on axis 1 and
considers a permanently-disabled name on axis 2; **both are category errors and
neither supplies the missing axis.**

**Severity: over-promise, not a miscompile.** Every one of these is refused, so
nothing wrong is emitted. It is recorded because it is tier 2 and EXACT under
D26, because the fact is already written down correctly in
`docs/pcre2_compliance.md` and contradicted by the diagnostic — two homes for
one fact, one of them wrong — and because it is the SAME over-promise shape as
K12, K13 and FIX-2's `[[:foo:]]`, now at a third doorway.

**Fix:** with the status/axis question in `docs/extension_design.md` §7.2 and
§10.1, which is Frank's to answer. The verb rows need an answer that names no
module; `REJECTED`'s existing "agreement IS compliance" wording is close, but
these are constructs PCRE2 DOES support and pcrec will not — a combination the
vocabulary has no slot for. No `tests/known_fail/` repro: the behaviour is a
rejection with a misleading module name, so the pins belong in `tests/reject/`.

## K15 — RULED ACCEPTABLE 2026-08-12 (Frank; D26 tier 2), found 2026-08-12 (R18 panel, engine critic — the sweep-template-misses-the-boundary lesson, third recurrence)

**A verb "name" longer than 128 bytes made of NON-identifier bytes gets the
name-too-long diagnostic where libpcre2 answers "not recognized".** Tier 2
under D26 (the message CATEGORY for a refused construct, no accept/reject
divergence — the engine critic verified a non-identifier run can never match
a table entry, so pcrec always refuses either way). Pre-existing: the move to
mod_verbs.c was byte-identical; this was measured against the migrated tree
and re-confirmed against the pre-move logic.

**Root shape:** `pcrec_verb_name_extent_scan` (scans.c) terminates only on
`)`, `:`, `=`, EOF — every other byte, including space, `*`, `(`, 0x80+, is
"name". libpcre2's own name scan stops at the first non-alnum/`_` byte.
The two agree on every message for runs UNDER the cap; they part company
exactly when a non-identifier run crosses the 128-byte boundary.

**Repro** (measured 2026-08-12, `build/pcrec` at 8e7597d, libpcre2 10.46):

    (* + 130 spaces + )   pcrec: subpattern name is too long (maximum 128 code units)
                          libpcre2: err 160 "(*VERB) not recognized or malformed" at offset 2
    (* + 127 spaces + )   BOTH: not recognized / unknown-name (control: under the cap, they agree)
    (* + 129 x 'A' + )    BOTH: subpattern name is too long — exact text match
                          (control: the 128-byte rule itself is right for identifier names)

**Why every net misses it:** PC-3's only length-boundary generator
(`pool_from_lengths`, pcre2_check.c source 4) builds its 126-130-length
candidates from repeated `A`/`a` — pure identifiers; the mutation pool edits
short names only. The generators structurally cannot express "long AND
non-identifier", the same class as R16's `\N` empty-row lesson and R17's
`(?%c`-always-emits-a-byte lesson.

**RULED, 2026-08-12 (Frank): acceptable, tier 2 per D26.** The linked pair
above landed in the same session, in order: `pool_from_lengths`
(`tests/registry/pcre2_check.c`) now generates non-identifier fillers
(space, `*`, 0x80) across the 126-130 boundary; PC-3 was run with the
generator live and NO guard, and confirmed to FAIL on exactly this cell (78
mismatches, all of them the too-long/not-recognized category split
measured above, zero elsewhere) — the failing-direction measurement the
ruling needed before an exclusion could be trusted; THEN `k15_excluded()`
was added, scoped as narrowly as the ruling allows — only the category
comparison for over-cap non-identifier runs. The two controls this entry
already names stay routed through the ordinary comparison and both still
agree: under-cap non-identifier runs (both "not recognized"), and over-cap
IDENTIFIER runs (both "too long", exact text). Documented at
docs/pcre2_compliance.md's Backtracking control verbs section.

**The extent-vs-cap interaction in `pcrec_verb_name_extent_scan` is left
AS-IS, deliberately** — this ruling accepts the message-CATEGORY
difference; it does not fix the scan. Remeasure when SR-6's real verb
handler lands (module `verbs` first produces, and the extent scan's
semantics get remeasured anyway regardless of this entry) — the original
schedule note stands.
