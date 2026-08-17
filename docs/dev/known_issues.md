# Known issues — confirmed pcrec bugs (deferred fixes)

Confirmed correctness bugs in pcrec itself (distinct from docs/dev/upstream_issues.md,
which tracks OTHER engines). Each has a minimal repro and a scheduled fix. Repros
live in tests/known_fail/ (NOT run by `make test`, so the suite stays honest about
what it certifies) and become passing regressions when fixed. That directory is
EMPTY as of 2026-08-15: no confirmed bug is currently deferred with a repro on
file.

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
architecture debt lives in docs/dev/plan.md; other engines' bugs in
docs/dev/upstream_issues.md._


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
own `syntax` field wrapped in `[...]` — see `docs/design/design_notes_mod06.md` §4
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
wrong verdict; the boundary is pinned in tests/reject/ and owned by
unicode-props' first WIDE producer (MOD-0.6 landed recogniser-only, 2026-08-12,
and deliberately kept this boundary — design_notes_mod06.md §8.2). Every cell measured first (tests/probes/probe_endpoint_k12.c,
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

This is the exact shape `docs/dev/plan.md:577` already records for `(?xx)[a- ]`, one
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
entries; both dumps carry the column (15-field --list-syntax — 13 at K14
landing, MOD-0.1's later slices appended quantifiable and class_expect the
same day — 5-field --list-verbs, consumers updated). Original entry below, kept for the
analysis.

**Historical entry (found 2026-08-11, R13 panel, C5/F13; verified independently by the author):**

**pcrec names a module for constructs its own compliance survey says will never
be implemented.** D26's tier-2 row says this in as many words
(`docs/dev/decisions.md:1457`):

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
it. `docs/design/extension_design.md` §7.2 proposes `RS_NOT_OFFERED` on axis 1 and
considers a permanently-disabled name on axis 2; **both are category errors and
neither supplies the missing axis.**

**Severity: over-promise, not a miscompile.** Every one of these is refused, so
nothing wrong is emitted. It is recorded because it is tier 2 and EXACT under
D26, because the fact is already written down correctly in
`docs/pcre2_compliance.md` and contradicted by the diagnostic — two homes for
one fact, one of them wrong — and because it is the SAME over-promise shape as
K12, K13 and FIX-2's `[[:foo:]]`, now at a third doorway.

**Fix:** with the status/axis question in `docs/design/extension_design.md` §7.2 and
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

## K16 — RULED ACCEPTABLE-UNTIL-PRODUCER 2026-08-12 (Frank; D26 tier 2), found 2026-08-12 (R19 panel, engine critic — the sweep-template lesson's FOURTH recurrence, one level deeper than K15's)

**pcrec's `\p{...}`/`\P{...}` body scanner never detects libpcre2's
"malformed body byte" class: 164 of 256 possible body bytes are ERR 146
("malformed \P or \p sequence") to libpcre2 the instant they appear —
blamed at the bad byte, ignoring even the 48-char cap — where pcrec scans
past them, folds them into the name buffer, and answers its own
unknown-name/generic category at the scan-completion offset.** Tier 2 under
D26: no producer exists, both engines refuse every such pattern, and module
attribution (`unicode-props`) is correct either way; only the refusal
CATEGORY and OFFSET diverge.

**The malformed set (measured 2026-08-12, libpcre2 10.46, full 256-byte
census of the sole body byte in `\p{X}`):** 0x00-0x08, 0x0E-0x1F (C0
controls other than the whitespace five), `!` `"` `#` `$` `%` (0x21-0x25),
`{` `|` `~` DEL (0x7B/7C/7E/7F), and ALL of 0x80-0xFF. The other 92 bytes
are ERR 147 (dispatched, unknown name) — pcrec's own bucket, agreement.

**Repro** (HEAD a42d604):

    \p{!}       libpcre2: err 146 at 4      pcrec: not-recognised text at 5
    \p{L!}      libpcre2: err 146 at 5      pcrec: generic module text at 6
    47A + '!'   libpcre2: err 146 at 51     pcrec: its own 48-cap fires at 52
                (libpcre2 stops at the byte;  (same "malformed" WORD, wrong
                 the cap never engages)        reason, wrong offset)

**Why every net missed it:** three instruments independently stop at the
brace boundary — the design note's insignificant-byte census tested four
candidate bytes; `probe_uprops.c` swept all 256 TAIL bytes but never the
BODY byte; `check_uprops_differential` generates well-formed-by-construction
cells and says so in its own comment. K15 was the length axis; this is the
content axis of the same lesson.

**RULED (Frank, 2026-08-12, R19 close): acceptable tier 2, fix DEFERRED to
the first unicode-props producer** — when the scanner's buffer gains a real
consumer, the whole algorithm gets remeasured anyway, and the fix (a
measured malformed-byte class table mirroring PCRE2's accepted-name-byte
set, body-byte census like the tail already got) lands with it. Until then:
`tests/reject/`'s `\p{!}`/`\p{9}`/`\p{=}`/`\p{Script=Latin}` pins claim
PCREC'S OWN current behavior (stability, not oracle agreement), and the
divergence is documented in docs/pcre2_compliance.md. **LINKED PAIR, K15's
shape: `check_uprops_differential` must NOT gain malformed-body generation
until this is fixed** — it would fail on the divergence it newly sees; its
well-formed-only scope is deliberate and its comment says so. Forward risk
recorded: a producer built directly on the accumulated buffer without the
malformed-byte check would treat `\p{Sc!ript}` as a lookup miss rather than
a shape PCRE2 never dispatches past — the K12/K13 "guard is the
unimplemented-ness" pattern.

## K17 — FIXED 2026-08-14, found 2026-08-14 (R21 panel, engine critic — the P-1 probe the M4 engine design itself requested)

**A live tier-1 MISCOMPILE in the shipped DFA: leftmost-first priority is
lost for a lazy nullable prefix followed by a nested nullable star inside
an outer star.** K1's 2026-08-09 fix (empty iteration must reach the loop
exit with its rightful priority) did not generalise to this shape.

**Repro** (HEAD ee4a244):

    pattern (?:b*?(?:a*)*)*   subject "ab"
      pcrec  : MATCH span [0,2)
      pcre2  : MATCH span [0,1)
      python : MATCH span [0,1)

Both oracles agree; pcrec's lazy `b*?` wrongly consumes the `b` after the
empty outer iteration should have terminated the loop at pos 1.
Capture-INDEPENDENT (the `(b*?(a*)*)*` capturing form is identical), so
this is the priority subset construction, not erasure.

**Shrunk family (R21 engine critic):** diverges — `(b*?(a*)*)*`,
`(b*?(a*)+)*`, `(b??(a*)*)*`, `(b*?([a]*)*)*`, `(b*?(a*|b*)*)*`.
Does NOT diverge — `(b*?(a*)*)+` (outer +), `(b*?(a+)*)*` (inner
non-nullable), `(b*?(a*)*)` (no outer star), `(b*a*)*` (greedy prefix).
Requires all three: lazy nullable prefix, nullable inner star, outer `*`.
Absent from the corpus (no .rxt pairs a lazy quantifier with a nested
star). Random-sweep context: 910/910 span agreements with libpcre2 on
seed-5 generated capture patterns; only this family diverged.

**Why it matters beyond itself:** it refutes the STRUCTURAL form of
engine_m4.md §6.1's exactness claim (the capture-erased DFA hands the VM
an EXACT span) — the erasure half held under attack; the semantic half
(D3's priority construction computes leftmost-first exactly) is where
this lives. M4.6's DFA-prefilter hybrid would publish the wrong span with
matching-wrong capture offsets, so the FIX IS A PRECONDITION for the
hybrid, and M4.5's internal differential (span(VM) == span(DFA) over the
corpus with a three-way oracle) is the regression net.

**Scheduled:** fix in the DFA priority construction before [M4.6]
(tracked in the R21 review's disposition table); the failing repro joins
tests/known_fail/ with the fix round.

**FIXED 2026-08-14 (k17-fix lane, one commit on branch `k17-fix` carrying the
fix and its guard tests together).** `src/ir/dfa.c` `clo_visit`: the
empty-iteration redirect is no longer a ONE-SHOT. K1's fix followed a loop
entry's exit edge only on the FIRST ε re-arrival per closure (`cl->reent`, a
second generation-stamped mark array); that extra condition has no semantic
reading. The rule is a property of the ARRIVAL, not of the loop — a second
ε-arrival at the same loop entry is a second iteration that consumed nothing,
and it must end the loop exactly like the first.

**Mechanism, measured on the repro's own NFA** (states as pcrec numbers them
for `(?:b*?(?:a*)*)*`: 0 = outer `*` entry, 1 = `b*?` entry, 3 = `(?:a*)*`
entry, 4 = `a*` entry, 6 = ACCEPT). Closing the pre-set `{4}` — the position
after "a" — walks 4 → exit → 3, and 3's own empty iteration spends the
one-shot on the way to 0. The outer star then opens iteration 2, whose lazy
`b*?` PREFERS to skip, which re-arrives at 3 — and with the one-shot spent
that ε-path died. So the `b`-consuming thread (NFA state 2) was appended to
the DFA state's priority list AHEAD of the ACCEPT that the empty outer
iteration should have reached, giving the accepting two-state machine that
matches [0,2). With the redirect firing again, 3 → exit → 0 → (0 is seen,
so it redirects too) → ACCEPT lands first, accept-pruning cuts the `b`
thread, and the span is [0,1).

**Termination did not need the one-shot**, which is why removing it is safe
rather than merely lucky: a state is EXPANDED at most once per closure
(`seen`), so an unbounded walk would need an infinite suffix of redirects
alone — and the redirect graph (loop entry → its continuation) only ever
points outward past the loop, so it is acyclic and every redirect chain is
bounded by loop-nesting depth. `reent` is deleted outright; the marks array
is half the size it was. Compile time measured unchanged on twelve
nested-star/nullable-alternation shapes (worst ratio 1.06, noise).

**Why every net missed it** (house tradition; this one is the R2-M1 lesson
one level deeper, and the answer is NOT that anything excluded the shape):

1. **The corpus never had it — the code author's alphabet, D27's lesson.**
   Measured over the 612 `pattern` lines in `tests/` before this fix: 44 use
   a lazy quantifier, and only 3 of those 44 also contain a quantified group
   with a quantifier inside it. All 3 are in review_r2.rxt and all 3 are
   R2-M1's own shape — a lazy quantifier over an alternation of LITERALS
   (`(?:ab|a){0,2}?b`). Not one paired a lazy NULLABLE prefix with a nested
   NULLABLE star, and not one put that under an outer star. Tests written
   from the fix that was just made inherit the shape of that fix.

2. **The fuzzer could produce it and never did — probability, not
   exclusion.** This is worth stating precisely because the tempting
   conclusion is that a filter hid it, and no filter did: the fuzzer
   compares EXACT SPANS against libpcre2, its grammar can generate every
   piece, and nothing in `EXCLUDED FROM GENERATION` touches this class. It
   needs four independent draws to land together — a quantified group, whose
   body STARTS with a lazy nullable quantifier, followed by a nested nullable
   quantified group, with an outer star over the whole thing — and then a
   subject short enough to expose it. Joint probability ~1e-4..1e-5 per
   pattern. The existing R2 trap templates did not help, because they encode
   R2-M1's overlapping-prefix ALTERNATION, which is the level above this one.

3. **What did find it was a probe aimed at a named blind spot.** The R21
   engine critic ran the refutation that engine_m4.md §6.1's own P-1 asked
   for — "the capture-erased DFA hands the VM an exact span" — instead of
   sampling more of the same space. Seed 5 gave 910/910 agreement and said
   nothing; the family fell out of seed 99. A claim the design marked
   BELIEVED is a better place to point an instrument than a bigger random
   sample, and this file's own history says so repeatedly (K15, K16).

**Countermeasure, landed with this fix:** K17-family TRAP TEMPLATES in
`tests/fuzz/fuzz.py` (six rows beside the R2 ones), which move the class from
~1e-4 of generated patterns to a measured **4%** — 50% of trap draws, traps
being 8% of patterns. They are sabotage-validated in the direction that
matters: exhaustively expanded, the six rows give 111 distinct patterns, and
against the PRE-fix compiler those produce 28 divergences over 1887
pattern/subject cells, against the post-fix compiler 0. The second half of
the countermeasure is the three-way differential gate ruled at D44 (any 2-1
split with pcrec in the minority is a bug, never an oracle exclusion) — the
mechanism that stops the next one being explained away.

**Guard tests:** `tests/base/review_r21.rxt`, 120 cases — the six diverging
family members, one nesting level deeper (`(?:b*?(?:(?:a*)*)*)*`, which
needs the redirect a THIRD time), a witness the post-fix random sweep found
independently, and the four non-diverging neighbours as over-reach controls.
Every expectation generated from python3 `re` and re-measured against
libpcre2 10.46: 120/120 pairs, both oracles, zero disagreements.

**Validation:** the ten-pattern family check — this entry's six diverging
shapes and four neighbours, on ten subjects each — went 18 divergences → 0
with all four neighbours still correct. Random
differential sweep vs python3 `re`, 2400 generated base-tier patterns × 16
subjects over 8 seeds = 38,400 comparisons: **0 cells of K17's shape
remaining, and 14 cells across 4 patterns that are K18 (below)** — every one
of those 14 measured identical on the pre-fix binary, so the fix moved
nothing away from the oracle.

The load-bearing check is the old-binary-vs-new-binary isolation, which asks
the right question directly — not "is pcrec correct" but "did this diff move
any span, and in which direction". 7 seeds × 408 patterns × 18 subjects =
**50,400 cells: 294 changed, 294 of those 294 old-wrong → new-right, 0
regressed, 0 both-wrong.** (The 294 is inflated by the eight positive-control
patterns being re-injected on every seed; the point of the count is the
direction, which is unanimous.)

**Blast radius by EMITTED SOURCE** — the stronger net, and the one
run_trie_identity.sh's comment argues for over subject sampling, because it
cannot miss a difference that the sampled subjects happen not to reach.
Emitting C with the pre-fix and post-fix compilers over 4500 generated
patterns: **4477 byte-identical, 23 differing** — of which 18 are the six
injected controls re-emitted on each of three seeds, so only FIVE generated
patterns changed at all:

    ((?:([^a]{0,2})|(?:[a-c])??)+)*      (?:((?:[ab]{1,2}|[^a]*?){1,2}){2,})*
    c?(?:(?:a?)+|[ab]{2,})*              ((?:(?:[a-c]*|.*)+?)+)*
    ((?:(a*){1,2}|[a-c]{1,2}){2,})*

Across all 23, 76 span cells moved, 76 of 76 toward the oracle, 0 regressed,
0 both-wrong. So the fix's reach is precisely the shape it was aimed at, and
for 99.5% of the sampled language the compiler emits the same bytes it did
before. Full `make test` green, `make strict` clean.

The first isolation attempt reported "0 changed" over 36,000 cells and was
DISCARDED rather than reported: its generator used a broader quantifier
alphabet and never produced a K17 shape at all, so it was a control that
could not have failed — the recurring lesson in this file about checks that
share a blind spot with the thing they check.

**IT DID NOT CLOSE THE CLASS — see K18.** The sweep that validated this fix
also found a structurally distinct sibling that this fix does not reach and
never did: `(?:(?:a|b*?)?)*` on "ab", still [0,2) against both oracles'
[0,1). K17's "requires all three: lazy nullable prefix, nullable inner
star, outer `*`" was a description of the shrunk family, not of the defect
class. Do not read this entry as evidence that the priority construction is
now exact.

---

## K18 — FIXED 2026-08-15, found 2026-08-14 (the K17 fix's own validation sweep)

**A second live tier-1 MISCOMPILE in the shipped DFA, the same root design
fact as K1/K17 and NOT fixed by either: the empty-iteration redirect cannot
be reached through an ALREADY-SEEN NON-LOOP epsilon state.** K17 widened
when the redirect fires AT a loop entry; this shape dies one state short of
ever arriving at one.

**Repro** (k17-fix HEAD, i.e. WITH the K17 fix applied):

    pattern (?:(?:a|b*?)?)*   subject "ab"
      pcrec  : MATCH span [0,2)
      pcre2  : MATCH span [0,1)
      python : MATCH span [0,1)

**Mechanism.** For `(?:(?:a|b*?)?)*` pcrec builds 0 = outer `*` entry
(exit → ACCEPT), 6 = the `?` split, 5 = the alternation split, 2 = `a`,
3 = `b*?` entry, 4 = `b`, and **1 = an N_EPS, the outer star's loop-back
edge**. Closing the pre-set `{1}` — the position after "a" — marks state 1
seen immediately, since it IS the entry point. The walk then reaches the
alternation, emits thread 2, and tries `b*?`, whose lazy PREFERRED branch is
its exit — and that exit edge points at state 1. (**The load-bearing word is
PREFERRED, not lazy** — R23 S8, see the correction below the control list: a
greedy nullable arm written FIRST reaches the same state the same way.)
State 1 is seen and is not
a loop entry, so `clo_visit` returns dead, one hop short of state 0, whose
redirect would have produced the ACCEPT. Thread 4 (`b`) is emitted instead,
ahead of the ACCEPT reached afterwards, and the DFA over-consumes.

**Diverging family (measured):** `(?:(?:a|b*?)?)*`, `((?:a|b*?)?)*`,
`(?:(a|b*?)?)*`, `(?:(?:a+|b*?)?)*`, `(?:(?:a|b??)?)*`, `(?:(?:a?|b*?)?)*`,
`(?:(?:a|b*?)?)+` (on "aab"/"aabb"), `(?:(?:[a]|[b]*?)?)*`,
`(?:(?:a|c|b*?)?)*`. **BOTH ENGINES** — `^(?:(?:a|b*?)?)*` diverges
identically on ENG_ATTEMPT, which is K1's R2-S1a lesson repeating: do not
scope this to one engine without measuring.
**Does NOT diverge** (each removes one ingredient; these are EMPIRICAL
controls — the mechanism above was traced only on the minimal repro, so do
not read a cause into any single row): `(?:(?:a|b*)?)*` and `(?:(?:a|b?)?)*`
(greedy inner), `(?:(?:b*?|a)?)*` (lazy branch preferred),
`(?:(?:a|b*?)*)*` (inner `*` not `?`), `(?:(?:a|b*?))*` (no `?` wrapper),
`(?:(?:a|b*?)?)` (no outer quantifier), `(?:a(?:b*?)?)*` (concatenation, not
alternation), `(?:(?:a|)?)*` (an empty alternative instead of a lazy
quantifier). Note that unlike K17, an outer `+` does NOT save the shape.

> **CORRECTION 2026-08-15 [R23 S8]: two of those parenthesised causes are
> wrong, and their mirror images are LIVE MISCOMPILES.** The rows above still
> measure as stated — each of those patterns really does answer correctly —
> but the reason given for three of them is ARM ORDER, not the ingredient
> named. The defect does not need laziness. It needs the arm whose exit edge
> lands on the already-seen ε state to be the PREFERRED one, and a GREEDY
> nullable arm achieves that simply by being written FIRST:
>
>     (?:(?:b*|a)?)*        "ba"   pcrec [0,2)  both oracles [0,1)   <- "greedy inner", swapped
>     (?:(?:b?|a)?)*        "ba"   pcrec [0,2)  both oracles [0,1)   <- ditto
>     (?:(?:(?:b|)|a)?)*    "ba"   pcrec [0,2)  both oracles [0,1)   <- an EMPTY arm, no quantifier
>     (?:(?:b?|a)(?:b?|d))* "ba"   pcrec [0,2)  both oracles [0,1)   <- CONCATENATION of two
>                                                                       nullable alternations
>
> So "greedy inner" does not save the shape (arm order did), "an empty
> alternative instead of a lazy quantifier" does not save it (arm order did),
> and "concatenation, not alternation" does not save it either. Both oracles
> agree on all four; the divergence is pcrec's. All four are fixed by the
> design note's recommended repair, which covers this sub-case already — the
> defect here is in this entry's CHARACTERISATION and in the acceptance
> corpus, not in the repair.
>
> **Consequence for the corpus below.** All 15 patterns in the .rxt file are
> the lazy shape and its only two non-lazy entries are CONTROLS, so none of
> the four witnesses above is on file. The rewrite lane's guard corpus owes an
> ARM-ORDER axis: every diverging shape in both orders, greedy and lazy
> nullable arms (`k18_memo_design.md` §1.5 and §5 item 1). They are NOT added
> to `tests/known_fail/` here — the ratchet counts that file, and the rewrite
> lane re-scopes the corpus when it moves it live.
>
> This entry's own warning — "do not read a cause into any single row" — was
> right, and was not enough: the causes were written into the parentheses
> anyway, and a reader building a corpus from them built a lazy-only one.

One of these controls is worth reading before trusting the others: for
`(?:(?:b*?|a)?)*` the closure at the position after "a" fails in EXACTLY the
way traced above — thread `b` ahead of the ACCEPT — and the pattern is
correct anyway, because the preferred lazy branch makes the START state
accept an empty match, so both pcrec and both oracles answer [0,0) and the
broken closure is never consulted. A control passing does not mean the
mechanism is absent there; it means the mechanism is not observable there.

**It is reachable by accident, not just by construction.** The four witnesses
below are what a 38,400-comparison random sweep threw up on its own, before
any shrinking; they are recorded because the shrunk repro above makes the
shape look more contrived than it is. All four measured IDENTICAL on the
pre-K17-fix binary, so they are this defect and not fallout from that fix.
The first three are visibly the `(...?)*` shape; the fourth is listed as
same-SIGNATURE (over-consumes by exactly the trailing byte) rather than
same-mechanism, because only the minimal repro's NFA was traced.

    (?:(?:(?:a+|[a-c]*?)?|(?:a+){2,})?)*   "ab"   [0,2) vs [0,1)
    ((?:(?:a?){1,3}?|.+?)*)+?              "ab"   [0,2) vs [0,1)
    ((?:(?:c{1,3}?|.*?)|(b{1,3}?)+?)?)*    "cba"  [0,2) vs [0,1)
    (?:(?:b+|[^a]??)+?(?:a?|[^a]+)+|b{3})+ "abc"  [0,3) vs [0,2)

**Why the K17 fix cannot reach it, and what a real fix costs.** Both bugs are
the same underlying fact: **`clo_visit`'s `seen` set is a GLOBAL per-closure
memo, but the empty-iteration rule makes a closure's result depend on which
loop iterations are currently OPEN on the walk's own path.** Dedup by NFA
state alone conflates two arrivals that the backtracker would treat
differently. K17 was the sub-case where the conflated state is itself a loop
entry, and there the redirect is a complete repair; K18 is the sub-case where
it is an ordinary ε state on the way to one, and no rule stated at loop
entries can see it. The principled fix is to key the closure memo on
(state, open-loop-set) rather than on state alone — a path-sensitive closure,
with the open set maintained as a properly-nested stack. That is a real
rewrite of `clo_visit` with a real compile-time-blowup risk (the memo must
distinguish contexts without losing the dedup that R2-A4's quadratic fix
bought), which is why it is NOT bundled with K17's one-line change.

**Severity: tier 1, same as K17** — a wrong span from the shipped compiler,
both oracles agreeing against pcrec, capture-independent. It carries the same
consequence K17's entry records for M4: it is a precondition for [M4.6]'s
DFA-prefilter hybrid, which would publish this wrong span with matching-wrong
capture offsets, and M4.5's span(VM) == span(DFA) internal differential is
the net that must catch it.

**Repro on file:** `tests/known_fail/k18_empty_exit_through_seen_eps.rxt`
(165 cases: the eight diverging shapes plus seven over-reach controls that
pass today and must still pass after a fix). Every expectation generated
from python3 `re` and re-measured against libpcre2 10.46 — 165/165 pairs,
both oracles, zero disagreements.

**Scheduled:** ASSIGNED by the manager at R21 close (2026-08-14):
DESIGN-FIRST, before [M4.6] opens — a short design note measuring the
compile-time cost of the (state, open-loop-set) memo (the lane's sketch
of the naive path-local version was exponential on `(?:a*|b*){20}`-class
shapes, so the design must find the bounded formulation or a narrower
sound rule), panel-eyed with whatever review gates M4.6's start, then the
rewrite as its own lane with K17's validation methodology (blast-radius
emitted-source diff + isolation sweep with an injected positive control).
Until then: the known_fail ratchet holds it visible; [M4.5]'s three-way
span differential is the net; [M4.6] does NOT open with K18 unfixed
(same precondition status as K17, R21 review E-1 disposition).

**DESIGN NOTE DELIVERED 2026-08-15: `docs/design/k18_memo_design.md`**
(PROPOSED, **AMENDED PER R23** — `docs/dev/reviews/2026-08-15-r23-k18-memo.md`;
the rewrite lane has NOT opened and this entry stays OPEN). It recommends the
(state, open-loop-context) memo this entry sketched, plus an empty-context
fast path, and it settles three things this entry left as expectations:

* **The cost is polynomial, and smaller than the note first reported.** The
  note's original Θ(d⁴) cost law and its 39 s worst case were a PROTOTYPE BUG
  (R23 S16: `clo_visit` restored the open-loop stack's depth but not its
  entries), not a property of the design. Re-measured on the fixed prototype:
  the deepest pattern the parser accepts — 250 nested nullable stars —
  compiles in **0.35 s** against the shipped compiler's 0.004 s, contexts fit
  d²/2 and redirects d³/3, the corpus maximum depth is 4, and aggregate
  inflation is **x1.004 expansions / x0.996 visits**. This entry's "real
  compile-time-blowup risk" is real but small, and **no threshold is proposed
  or needed** — the note's §6 ruling request is WITHDRAWN.
* **The exponential the entry attributes to the naive path-local version is
  CONFIRMED, and it is the absence of the memo, not the path-sensitivity.**
  MEASURED Θ(2ⁿ) on `(?:a*|b*){n}`, out of budget at n=22.
* **This file's 165 cases are NOT a sufficient acceptance criterion.** A
  two-line alternative (an already-seen ordinary ε walked through rather than
  killing the walk) passes all 165 and is still wrong: over a dense
  18,858-pattern sweep it differs from the recommended design on 83 patterns /
  98 cells, and the oracle agrees with the recommended design on 98 of 98.
  Every one is a `{0,2}`-bodied shape — the same conflation happening at a
  SPLIT instead of at an ε, which is a THIRD sub-case of the root fact and is
  not covered by the family recorded above. The rewrite lane owes those 83 a
  guard corpus.
* **A FOURTH sub-case, added by R23 S8: the ingredient is the PREFERRED
  alternation arm, not laziness** — see the correction under this entry's own
  control list. The guard corpus therefore also owes an ARM-ORDER axis, and
  the note's §5 item 1 specifies it.

**FIXED 2026-08-15 (k18-rewrite lane, branch `k18-rewrite`).** `src/ir/dfa.c`:
the epsilon closure is now PATH-SENSITIVE. The memo is keyed on (state,
OPEN-LOOP CONTEXT) and the empty-iteration redirect fires on "this loop is
OPEN on my path" rather than on "this state has been seen somewhere in this
closure" — the design note's prototype A2, unchanged in semantics.

**Mechanism.** A context is an interned chain: ctx 0 is the empty open-loop
stack, every other ctx is (parent ctx, loop-entry state). Taking a loop's BODY
edge opens the loop (interning a child context); a redirect pops the
re-arrived loop AND everything above it by moving to that context's parent.
The memo suppresses a re-arrival only at the same (state, ctx), so the second
arrival at K18's already-seen ε state — which is now in a DIFFERENT context —
survives, reaches the outer loop entry one hop later, and redirects to the
ACCEPT at the priority position the empty iteration earns.

Three properties of the implementation are worth reading before editing it:

* **The empty-context fast path is not optional.** With the stack empty,
  (state, 0) and `state` are the same key, so ctx 0 keeps the pre-K18
  per-state stamp array. Without it a fuzz-found pattern did byte-identical
  work 7x slower, all of it one hash probe replacing one array access 15.7
  million times (note §2a).
* **`clo_walk` has NO recursion.** The design as prototyped descends once per
  CONTEXT rather than once per state, which measures 31,377 C frames at the
  parser's 250-paren nesting cap against the old closure's 253 — ~7 MB of the
  default 8 MB stack, and an outright stack overflow under AddressSanitizer at
  nesting depth 210 (§5 item 12, the one defect R23's own re-measurement
  found). The split's preferred branch now pushes its deferred branch onto an
  explicit LIFO instead, so C-stack depth no longer depends on the pattern.
  `tests/base/k18_deep_nesting.rxt` is the guard, since the rest of the corpus
  tops out at loop-nesting depth 4.
* **The chain is immutable, and that is load-bearing.** The design's hardest
  prototype bug (R23 S3) was a frame restoring the open-loop stack's depth but
  not its ENTRIES, which silently lost redirects — the very defect being
  repaired, reintroduced by the repair. A deferred branch here carries its
  context as one interned int that nothing can rewrite, so the bug is not
  expressible. Both of §3's invariants ship as live `DFA_INVARIANT` aborts:
  the redirect's open loop is the chain top, and no already-open loop is ever
  pushed.

**Guard corpus** (`tests/base/`, moved and grown in the same commit as the fix
— the known-fail ratchet enforces that pairing):

* `k18_empty_exit_through_seen_eps.rxt` — the original 165 acceptance cases,
  moved out of `tests/known_fail/` (26 of which failed before this fix);
* `k18_arm_order.rxt` — 54 patterns / 667 cases, the R23 S8 axis: every
  diverging shape in BOTH alternation orders, greedy as well as lazy nullable
  arms, the empty-alternative and concatenation forms that contain no lazy
  quantifier at all, and nine over-reach controls including K17's own repro;
* `k18_split_shapes.rxt` — 83 patterns / 609 cases, the `{0,2}`-bodied family
  where the conflation happens at a SPLIT rather than an ε. This is the file
  that matters most: the cheap two-line candidate repair passes all 165 of the
  acceptance cases and gets all 98 of these cells wrong;
* `k18_deep_nesting.rxt` — 8 patterns / 24 cases, the resource guard above;
  also the deliberate GROW-PATH test for the three tables the repair adds
  (31,627 contexts against initial capacities of 64 and 256), which neither
  the corpus nor the fuzzer would otherwise drive past their first
  allocation;
* `k18_cost_gates.rxt` — 6 patterns / 29 cases whose point is COMPILE TIME
  rather than spans, riding the harness's own per-invocation pcrec budget:
  the fuzz-found witness that caught the design prototype's 7x
  constant-factor regression on byte-identical work (a `perr` block — every
  binary refuses it on the DFA state cap AFTER building 32,000 states), and
  bounded-repeat × nullable-loop swept in k, the family that runs at
  open-loop depth 1 and would therefore be invisible to any depth-based gate.

1,329 new cases, every expectation generated from python3 `re` AND libpcre2
10.46 with **zero disagreements** (D44's three-way rule). The full `.rxt`
corpus goes **1,704 → 3,198 cases**.

**Non-vacuity, per file, measured by running the PRE-FIX compiler against the
new corpus** — a guard corpus its own bug passes is a control that could not
have failed:

| file | cases | pre-fix failures | post-fix |
|---|---|---|---|
| `k18_empty_exit_through_seen_eps.rxt` | 165 | 26 | 0 |
| `k18_arm_order.rxt` | 667 | **62** | 0 |
| `k18_split_shapes.rxt` | 609 | **63** | 0 |
| `k18_deep_nesting.rxt` | 24 | 0 | 0 |
| `k18_cost_gates.rxt` | 29 | 0 | 0 |

The last two files are the deliberate exceptions and are marked as such: they
guard RESOURCE classes, so their failure modes are a stack overflow under
`make asan` and a blown compile budget, not a wrong span. They are
sabotage-validated in those directions instead — the design's own prototype,
built with the identical asan flags, dies with `stack-overflow` at nesting
depth 210 and 250 where the shipped repair compiles both (0.84 s at 250 under
asan), and the same prototype takes 13.5 s on the cost file's `perr` witness
against the shipped 0.62 s.

The K18 fuzz TRAP TEMPLATES (`tests/fuzz/fuzz.py`, nine rows beside K17's
six) are validated the same way and in the direction that matters:
exhaustively expanded they give 64 distinct patterns / 543 cells, **56
divergences against the pre-fix compiler and 0 against the fixed one**. Both
fuzzer seeds run to completion on the fixed compiler with 0 content
divergences, 0 accept/reject divergences and **0 pcrec compile timeouts of
400 patterns each** — a compile that never finishes is invisible to a
differential that compares answers, so the budget is reported as a count.

**Validation.** Emitted-source blast radius against the pre-fix compiler:
**622 corpus patterns, 555 accepted by both, 547 byte-identical, 8 differing,
0 accepted by only one — and the 8 are exactly the eight K18 shapes**, which
is the design note's §4.2 prediction reproduced pattern for pattern. Over the
lane's dense 18,858-pattern shape space: 18,609 identical, **249 differing**.
Changed-cell direction against python3 `re`, both sweeps: **251 changed cells,
251 old-wrong → new-right, 0 regressed, 0 both-wrong** (226 on the shape
space, reproducing §4.3 digit for digit; 25 on the eight corpus patterns).
Full `make test` green with the corpus grown by 1,494 cases (the 1,329 new
plus the 165 activated); `make strict`,
`make ubsan`, `make asan` (the deep-nesting case included), `make lint`,
`make bench`, `make mech` green; the trie-identity gate run explicitly, since
a path-sensitive closure over an epsilon graph the M2.8 trie CHANGES is
exactly what that gate's erasure argument was not written for.

**What this does NOT close.** The class is K1/K17/K18's shared root fact, and
this repair addresses that fact rather than a shape — but the same sentence
was written about K17. The honest statement is narrower: the closure now
computes the empty-iteration rule as stated, the three known sub-cases (arrival
AT a loop entry, arrival THROUGH a seen ε state, conflation at a SPLIT) are
one mechanism, and the corpus above covers all three in both arm orders.

---

## K19 — FIXED 2026-08-15, found 2026-08-15 (D45's own ruling; the battery that pegged cc1 for 100+ minutes)

**A shipped compiler defect in [M4.5b]'s VM emitter: a bounded repeat over a
choice-bearing body emits megabytes of C that no cap stopped, and gcc's
compile time on that shape is superlinear.**

Not a miscompile — the emitted matcher is CORRECT. The defect is
DISPROPORTION between what the author writes and what the compiler emits, and
its consequence is a build that never finishes.

**Repro** (before the fix):

    $ build/pcrec -p rx -o /tmp/o.c '((a)|b){0,4000}c'   # 16 characters
    $ wc -l /tmp/o.c
    113545 /tmp/o.c                                       # 3.5 MB
    $ gcc -O2 -c /tmp/o.c                                 # minutes
    $ gcc -O1 -fsanitize=undefined -c /tmp/o.c            # 100+ minutes

`PCREC_MAX_VM_NODES` did not stop it: it refused `(a|b){0,65535}` and let this
through, which is what D45's consequence 1 records as the gap.

**Why the emitted size is linear in a number written in three characters:**
engine_m4.md §3.3's ruled reading is that a bounded repeat REPLICATES its body
(PCRE2's own semantics — each copy is an independent opportunity to match), so
`{0,N}` over a body containing an alternation costs N copies of that body's
code.

**Why gcc goes superlinear on it**, measured (project box, 2026-08-15; the full
curves are in docs/testing.md's battery section): the cost tracks the number of
ADDRESS-TAKEN LABELS, not the label count. At the same size, `(a×2000)b` emits
2004 labels with ZERO address-taken labels and compiles in 2.70 s at -O2, while
`((a)|b){0,200}c`'s 2003 labels with 400 address-taken labels take 11.21 s.
Each `&&label` becomes a potential successor of the VM's single `goto *`, so the
indirect edge's fan-out is what gcc's dataflow goes superlinear in. It is R1
A-3's computed-goto cliff, reached from the VM side — which REFUTES
engine_m4.md §2.1 and §13's P-6 ("the VM should therefore never approach" it)
and answers §12's ASK-7 unbidden.

**Fixed** by `PCREC_MAX_VM_REPEAT_COPIES = 64` (src/core/limits.h), checked in
the pre-pass BEFORE emission, with a diagnostic that names the replication
count, the limit, and the two ways out. The number is measured: at 64 copies
the worst allowed artifact costs 1.40 s at -O2 (28% of D45's 5 s plain budget)
and 2.30 s under UBSan; 128 copies would sit at 92% of the plain budget.

The cap is on REPLICATION rather than total size on purpose. A first draft
capped total resume points and refused a 200-branch capture-bearing keyword
alternation, which is entirely healthy — its size is proportionate to the
pattern. Sabotage S44.

**Residual, open and recorded**: a very long capture-bearing LITERAL still
emits a large artifact with zero resume points (20,000 characters → 2.3 MB,
>180 s at both -O1 and -O2), bounded only by `PCREC_MAX_VM_NODES` at 131,072 —
far above what the compile budget absorbs. That shape is proportionate to the
pattern, so the replication cap correctly does not see it, and D45's harness
wrapper now catches it loudly instead of hanging. Lowering the node cap would
refuse patterns that work today and is a ruling, not a fix.

---

## K20 — FIXED 2026-08-15, found 2026-08-15 (while probing K19's boundary)

**A shipped CRASH in [M4.5b]'s VM emitter: unbounded C recursion on the AST
spine, SIGSEGV on the default path with no special flag.**

    $ build/pcrec -p rx -o /tmp/o.c "($(python3 -c "print('a'*20000)"))"
    Segmentation fault (core dumped)          # rc 139, empty stderr

The threshold tracks `ulimit -s` — 8 MB crashes at ~20,000 characters, 2 MB at
~6,000, 64 MB survives — which is what identifies it as stack exhaustion
rather than anything subtler. Capture-bearing patterns only (the VM path);
larger sizes were masked on the default path because the DFA state cap fires
first, but `--engine=vm` crashed at every size above the threshold.

**Root cause**: three pre-pass functions added at [M4.5b] — `vm_nullable`,
`vm_count_slots` and `vm_cost` — recursed on `A_CAT`/`A_ALT` children, so a
left-leaning spine of N elements recursed N deep.

**This is DD-10 / D10 / R1 R-2's bug class for the THIRD time.** `src/ir/nfa.c`
flattens its `A_CAT`/`A_ALT` spines iteratively for exactly this reason and
says so in a comment; `vm_emit` (the emitter proper) was written to match; the
three helper functions beside it were not, and nothing in the tree could see
the difference because no test compiles a 20,000-character pattern.

**Fixed** by flattening all three iteratively, matching nfa.c. Verified at a
1 MB stack: a 100,000-character capture-bearing literal now compiles, where
8 MB previously failed at 20,000 — the recursion is gone, not merely deeper.

**The lesson worth keeping** is not "flatten spines" — the tree already knew
that — it is that the rule was recorded against ONE function rather than
against the AST shape, so the next three functions to walk the same shape
inherited nothing. Any new walk over `A_CAT`/`A_ALT` needs the same treatment,
and `vm_nullable` now carries the comment that says so.

## K21 — FIXED 2026-08-15 (found same day, R23 semantics critic S15; triaged by a follow-up read-only probe)

**The `--emit-main` convenience `main()` treats `<prefix>_search`'s
three-valued return as a boolean, so VM step/frame-budget exhaustion
(RX_ERR_STEPS/RX_ERR_FRAMES, both negative and both C-truthy) is reported
as a successful match with UNINITIALIZED capture-span output.**

**Repro:**

    pattern: (?:(?:(?:(c??){0,4}?(?:d{0,2}?a{0,2}){1,2}){0,3})+.(?:(d{0,2}){2,3}((?:[a-c]{1,2}?|b*?){1,2})?){0,2})*
    subject: "" (this pattern exhausts the step budget on every subject tried,
                 up to length 3)
    the --emit-main binary prints: match 32768 140721206985752  (varies run to run)
    correct behaviour: rx_search returns RX_ERR_STEPS (-2); there is no match
                       to report

Minimal ingredient: any pattern whose VM-emitted `rx_search` exhausts
`RX_STEP_BUDGET`/`RX_BT_FRAMES` on the tested subject. Two more witnesses
(R23 appendix, S15; probe findings) show the same mechanism producing
small plausible-looking wrong numbers instead of obvious garbage — zeroed
stack bytes printed as `match 0 0` — which makes this bug easy to mistake
for a semantic miscompile. Do not triage a "plausible but wrong span from
an emit-main binary" as a priority/closure bug without first ruling out
RX_ERR_STEPS/FRAMES by checking the raw `rx_search` return code (the probe
itself chased that false lead partway).

**Mechanism.** `pcrec_emit_main` (src/gen/emit_dfa.c:993, shared by both
emitters): `if (%s(...caps)) { printf("match ...", caps[0][0], caps[0][1]);`.
The search's give-up path returns the negative sentinel BEFORE calling
`rx_caps_out`, so `main()`'s stack `caps` array is never written; C
truthiness makes -2/-3 take the match branch and print uninitialized
memory. `tests/fuzz/fuzz_driver.c:130-133` already discriminates the
sentinels correctly (the fuzzfix arc's fix) — `pcrec_emit_main` is a
separate call site that arc did not touch. DFA-only artifacts never return
the sentinels, so the bug is VM-artifact-only.

**Severity.** Not a wrong match from the engine — `rx_search` itself
returns the correct sentinel — but the CLI-facing convenience `main()`
fabricates match data when the honest answer is "budget exhausted", which
is worse than silence (D26 tier-1-adjacent).

**Fix direction.** Branch three ways in `pcrec_emit_main` (rc==1 match,
rc==0 nomatch, rc<0 a distinct give-up line + distinct exit code),
matching fuzz_driver.c; plus a test that forces a budget exhaustion under
--emit-main and pins the three-way stdout. Scheduled: immediate small
lane (2026-08-15, R23 close), not deferred.

**Fix landed 2026-08-15.** `pcrec_emit_main` (src/gen/emit_dfa.c) now
captures `rc = %s(...)` and branches on the VALUE: `rc == 1` prints
`match START END` and exits 0 (unchanged), `rc == 0` prints `nomatch` and
exits 1 (unchanged), and `rc < 0` prints a one-word honest give-up line —
`steps` or `frames`, distinguishing which sentinel fired, via the
`%s_ERR_STEPS`/`%s_ERR_FRAMES` macros the same emitted file already
defines — and exits 3, a code that collides with neither match/nomatch
(0/1) nor this same `main()`'s own usage-error exit (2). The wording
mirrors `tests/fuzz/fuzz_driver.c`'s existing `"steps"`/`"frames"` tone
(D26: the exact word is ours to choose; kept short, stable, and
consistent with the driver that already got this right).

Pinned by `tests/cli/run_cli_tests.sh` case15: two small, reliable
witnesses driven to their own limit exactly the way
`tests/vm/run_vm_tests.sh` §4/§4.5 already do — `(a*)*b` under
`--engine=vm --step-budget=50` (step budget) and `((a)|b)*c` under
`--engine=vm --backtrack-frames=4` (frame capacity) — each asserting the
exact stdout line and exit code 3, PLUS the non-firing controls (the same
two patterns under an ample budget/capacity still print an honest
`match START END`), so a give-up path that fired unconditionally could
not pass silently. Verified FAILING against the pre-fix emitter first
(4 of case15's 10 assertions fail — exactly the give-up-path ones; the
match/nomatch and control assertions stay green either way), then
verified green again after restoring the fix. No consumer of the old
two-line `match `/`nomatch` --emit-main contract was found scanning
tests/, scripts/, docs/ for a parser that would choke on the new third
line — the existing green tests never reached the give-up path before
this fix.

**Class closure (2026-08-15, same lane, on review request; 4 of 4
fixed).** K21 is one instance of a recorded SHAPE — `if (rx_search(...))`,
testing a three-valued return as a boolean, so a negative give-up
sentinel takes the match branch under C truthiness — not a one-off in
`pcrec_emit_main` alone. Per the K20 lesson (record against the shape,
not the site), the other known readers of `rx_search`'s return were
surveyed:

- `tests/fuzz/fuzz_driver.c` — already correct (the fuzzfix arc,
  `c225a9f`/`7e27c19`): discriminates `found == 1`/`== 0`/
  `RX_ERR_STEPS`/`RX_ERR_FRAMES` explicitly.
- `tests/harness/driver.c` — HAD the bug (`if (found) { ...caps... }`),
  now FIXED in this same lane: discriminates explicitly, prints
  `steps`/`frames` and exits 3 on a give-up (matching
  `pcrec_emit_main`'s exit-code choice for cross-site consistency), and
  `tests/harness/run.sh`'s per-case loop gained an explicit `trc -eq 3`
  branch treating it as a HARD harness-level failure, the same shape as
  its existing timeout/crash branches — never compared against a
  `match`/`nomatch` expectation. Verified live: the pre-fix driver
  against a `--engine=vm --step-budget=50` artifact printed a fabricated
  `match` line with garbage capture spans; the fixed driver correctly
  prints `steps` and exits 3 on the identical artifact/subject.
  Dormant over the base .rxt corpus (no `flags`/`features` directive can
  select `--engine=vm` or a tiny budget), so no .rxt test was added — see
  the driver's own comment and docs/testing.md's driver-protocol section.
- `tests/registry/pc4_driver.c` — HAD the bug too
  (`if (rx_search(s, len, 0, caps))`), independently of the `89ccd89`
  "sibling" fix in the fuzzfix arc, which fixed a DIFFERENT bug in this
  same file (the `caps[RX_NCAPS][2]` stack-array sizing hazard, since this
  driver is compiled once against a throwaway pattern and reused across
  the PC-4 sweep) — `89ccd89` never touched the truthiness check, so this
  file was genuinely still open when it was first flagged here 2026-08-15.
  **NOW FIXED, same day, same lane.** pc4_driver.c is a DIFFERENTIAL
  driver, not a match/nomatch-only one, so the fix follows a different
  shape from the other three: `pc4_check.c` (the libpcre2 side) already
  had a bucket for a NON-comparable outcome — `mlimits`, libpcre2's own
  match-time give-up, counted separately, excluded from `cells`, never
  compared as a verdict, asserted zero. pc4_driver.c now discriminates
  `found == 1`/`== 0`/otherwise explicitly and prints `giveup steps`/
  `giveup frames` for that subject instead of a fabricated verdict;
  `pc4_check.c` gained the symmetric `pcrec_giveups` bucket, checked
  BEFORE the match/nomatch comparison so a give-up can never enter it as
  a fabricated match, and asserted zero alongside `mlimits`. Verified two
  ways: (1) directly — PC-4's real 271-subject set has nothing long
  enough to burn a tiny step/frame budget, so a scratch driver using the
  identical discrimination logic against a `--engine=vm --step-budget=50`/
  `--backtrack-frames=4` artifact was run standalone, correctly printing
  `giveup steps`/`giveup frames`; (2) `pc4_check.c`'s new branch verified
  in the FAILING direction by splicing one synthetic `giveup steps` line
  into a real `\d` sweep's results file — `cells` dropped by exactly 1,
  `pcrec_giveups` fired naming the count, and no spurious match/nomatch
  disagreement appeared for that cell. The real `run_pc4.sh` sweep is
  unaffected (still dormant: DFA-only pattern space) — unchanged
  273/232/41/62,872/0 populations. See tests/registry/CLAUDE.md for the
  full account.

## K22 — OPEN, found 2026-08-16 (possessify lane, while probing pass compile-time on large bodies)

Nested bounded repeats HANG THE COMPILER with no diagnostic — but ONLY
under `--engine=vm`. `vm_count_slots` (src/gen/emit_vm.c) walks the
replicated copy tree, so nesting depth d costs Θ(2^d) work BEFORE
`PCREC_MAX_VM_NODES` can fire; on the DEFAULT path the NFA 131072-state
cap refuses every such pattern instantly (0.11 s) and is an ACCIDENTAL
guard — `--engine=vm` skips building the NFA/DFA pair entirely (R21
E-6's prefilter-off behavior), so nothing bounds the walk.

Minimal repro (exact patterns + timing sweep + reproduce-loop:
docs/design/possessify_impl/k22_repro.txt; verified on main 949f867
with zero possessify symbols AND by the manager's own run at merge):
a `(?:...){0,2}` tower at depth 15 (140 chars) compiles in 0.32 s;
depth 20–30 refuses cleanly but increasingly slowly (11.82 s at depth
30 — the REFUSAL itself is already exponential); depth ≥35 hangs >30 s
with no diagnostic. Not adversary-tier only in theory: a 365-character
pattern is user-writable.

Tier: robustness (D22) — a pathological pattern must fail honestly,
never hang. The harness is protected (D45 bounds pcrec's own invocation
at 20 s in-suite); an end user on `--engine=vm` is not.

Fix direction, two halves: (1) the REAL fix is [ENG-BREP]'s counter-K
step, which eliminates replication for exactly these shapes (the copy
tree stops existing); (2) the interim guard is a cheap PRODUCT check —
multiply the nesting-path copy counts BEFORE walking (the exact
known-risk interaction eng_brep_design.md §7 names: "replication
factors MULTIPLY and v.maxcopies records only the max") and refuse
above a bound with a D26-tier diagnostic. Scheduled: with [ENG-BREP]'s
counter-K step, or as a small standalone guard lane if that step is
far. Related: the step-budget blind spot recorded in the [ENG-BREP]
plan row (same lane, same session) is the RUNTIME sibling of this
COMPILE-TIME gap — both are "possessification/replication moved work
where an existing budget cannot see it". (That sibling's fix of record
has since MOVED, 2026-08-17: the E-5-shaped entry charge was refuted by
the counter-K lane's measurement — R25 §7.2 — and the ruled fix is the
counter-K design note §7.4's forward-work meter under F-2 settlement 4,
its own bound/field/error code; decisions.md D47 SECOND ADDENDUM.)

**INTERIM GUARD LANDED 2026-08-16 (rung-select lane); the entry stays
OPEN because half (1) is still owed.** `vm_count_slots` now carries a
running PRODUCT of the replication factors down the nesting path and
refuses above `PCREC_MAX_VM_REPLICATION_PRODUCT` (src/core/limits.h)
BEFORE it recurses. The bound is `PCREC_MAX_VM_NODES`'s own value, and
that identity is the guard's whole safety argument rather than a number
to tune: every replicated copy costs at least one `vm_charge`, so the
product is a LOWER BOUND on the emitted node count and the guard can only
move a refusal EARLIER, never widen one. MEASURED (committed and
re-runnable: `docs/design/rungselect_impl/k22_sweep.sh`, outputs
`k22_sweep_{before,after}.txt`) — depth 15 compiles before and after;
depth 30 goes 11.82 s → 0.12 s; depth 35 and 40 go from HANG >30 s to
0.12 s. Depth 18 did not move and refuses through the NODE cap in 0.72 s
both times, because the tower's innermost `(?:a){0,2}` takes the cursor
rung and replicates nothing, so a depth-*d* tower's product is 2^(d−1)
and 18's sits exactly at the limit rather than over it. Pinned by
`tests/vm/run_vm_tests.sh`, where `timeout 5` IS the assertion (a plain
exit-code check would have passed on the defect, since depth 30 already
"refused" before the guard) and a depth-15 positive control leads,
because a guard that refuses everything also makes the hang go away.
The REAL fix, half (1), is unchanged and still owed: [ENG-BREP]'s
counter-K step, which stops the copy tree from existing for these shapes.
The reverse-deterministic rung landed the same day does NOT discharge it —
it declines nested quantifiers by scope bound (single-level only), so a
`{0,2}` tower still replicates.

## K23 — exact-minimum ambiguous-decomposition boundary exhausts the step budget on a 100-byte ordinary input (found 2026-08-16, D27 blinded quantifier corpus)

`(a{10,20}){10,50}` against `'a' * 100` — exactly the minimum total, the
ONLY valid decomposition (10 outer x inner minimum 10; 11 outer would need
110 bytes) — makes the compiled VM matcher return `RX_ERR_STEPS` against
the default 1,000,000-step budget instead of the match. python `re` (the
oracle) answers instantly: span (0,100), group 1 (90,100). Reproduced by
the manager at merge on HEAD's build (exit 3, "steps"). The boundary is
NARROW: 99 bytes reports nomatch in <1 ms (min-total check fails fast);
150+ bytes matches instantly (greedy satisfies an unambiguous
decomposition). The give-up itself is DESIGNED behavior (DD-2/D22:
honest RX_ERR_STEPS, not a hang or wrong answer) — the issue is the
search-space explosion that makes a 100-byte non-adversarial input hit it.

D27 author's characterization (probed black-box, recorded so the fix lane
does not re-derive it): inner-range WIDTH and total interact — `(a{10,12}){10,50}`
(width 2) at 100 matches instantly; `(a{10,15}){10,40}` (width 5) at 100
exhausts; reducing the outer max alone (`{10,30}` vs `{10,50}`) does NOT
avoid it, so it is not simply proportional to the outer ceiling.

NOT fixed by counter-K (choice points are identical across all K by
design — the emission strategy changes size, not the decomposition
space). Candidate mechanisms live with the OPT waves (memoization /
decomposition pruning) or [M4.6]'s engine-selection work; owning
milestone [M4.6] until a better owner exists. Regression:
`tests/known_fail/d27_nested_min_boundary.rxt` (ratchet-watched); the
99/500/1000-byte siblings stay live in `tests/base/d27_nesting.rxt`.

**K22 CLOSED 2026-08-16 (F-1 ruling, decisions.md D47 ADDENDUM,
twenty-seventh session).** The two halves resolve separately: the HANG
half was fixed by the interim product guard above (landed with
rung-select, pinned in tests/vm/run_vm_tests.sh — refusal in 0.12 s at
every depth). The "these shapes should COMPILE" half is NOT a bug under
the ruling: Frank ruled strict eng_brep_design.md §4.5 (K is one
per-artifact constant in v1, no per-quantifier variation), so the
small-count tower family's ruled behavior IS the guard's fast honest
refusal (D22's bar), and compiling them is re-homed as the charter of
plan row [ENG-CLAMP] (deferred; carries the counterk lane's respecified
bottom-up-product algorithm and clamp_arith.py probe as its seed). The
prior sentence in this entry claiming counter-K "stops the copy tree
from existing for these shapes" was REFUTED by the counter-K lane's own
analysis regardless of the ruling (R25 E1: at K=8 every tower count
sits below K and replicates; only a per-quantifier downshift reaches
them) — the record is corrected here rather than rewritten above.

## K24 — pattern-specific DFA throughput regression on the alternation-trie shape, ~1.3x below its D12 floor (found 2026-08-17, [M4.6b] bench lane, during the case (c)/(i) engine-drift investigation)

`(alpha|beta|gamma|delta|epsilon)` compiled `--no-captures` (ENGM_DFA,
verified by the new per-case engine assertion) measures 294.381/304.309
MB/s on two independent quiet-box confirms against its 388.615 MB/s
floors.tsv reference (captured 2026-08-09, reconfirmed ~385-390 on
2026-08-11 runs) — reproducibly ~1.3x slow, with a 1.13-1.16x spread
where this case's history is 1.02-1.06x. NOT the engine-selection drift
(that was cases (c)/(i) silently routing to the VM hybrid under D42.1's
captures-default, fixed 2026-08-17 by pinning + per-case engine
assertions — see tests/bench/compare/CLAUDE.md's finding writeup): this
residual reproduces WITH the pin confirmed stamping ENGM_DFA. Every
other DFA case in the same full-grid run matched or beat its floor, so
it is pattern-specific — the multi-branch keyword-alternation shape is
the M2.8 trie's home turf, and the landing window (2026-08-11 →
2026-08-17: K18's path-sensitive closure rewrite of src/ir/dfa.c is the
prime suspect by file; possessify/revdet/counter-K touch only the VM
emitter) brackets the bisect. REPRODUCER: `CASES=c` via
tests/bench/compare/compare.sh on a quiet box (load-check per its
conventions); the floor row is DELIBERATELY LEFT at 388.615 so gate.sh
reports (c) RED as the live flag until this closes.

**ROOT CAUSE FOUND 2026-08-17 (k24bisect lane, merged cb6c708 —
full evidence docs/design/k24bisect_impl/k24_bisect_note.md):** first
bad = 1dbb6ce, the [M4.4] API break — NOT K18 (exonerated: the emitted
DFA for this pattern is byte-identical from 1dbb6ce to HEAD). The
mechanism is COMPILER LAYOUT, not our algorithm: adding
rx_match/rx_match_caps as same-TU callers of rx_search triggers gcc
-O2's PARTIAL-INLINING pass to split rx_search into a trampoline +
rx_search.part.0 carrying the scan loop; the loop's instructions are
identical before/after, but the split placement is layout-sensitive.
CAUSALLY PROVEN: same gen.c, same driver, -fno-partial-inlining alone
recovers 389.6-391.8 from 288.6-293.8 (pinned, 10 trials, <1% spread);
nm confirms the .part symbol vanishes. Corollary symptom: once split,
the SAME binary measures 287-397 UNPINNED — bench floors must pin
(probe + compare conventions carry this). FIX IS A DESIGN CALL, open:
keep rx_search monolithic (attribute lever on the wrappers or the
entry, e.g. noipa on the cold wrappers), control hot/cold layout, or
accept + re-floor; AND the same-TU-wrapper shape exists in EVERY VM
artifact too (match/match_caps call search), so the fix lane must
audit whether the VM hot path is also being split. Owner: [M4.6]
close-out (a RED D12 floor is M4.6's business). Correctness is
unaffected (the .rxt corpus and the trie's output-preserving
differential are green) — this is a D12/D18 throughput regression, not
a miscompile. Owner: manager triage; bisect queued. Found because
[M4.6b] added a NEW floor-gated case and re-ran the whole matrix —
compare/'s floors are in no battery leg (now marked ages-freely, with
the engine assertions as the cheap in-run tripwire).
