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

So `\1`..`\9` are unconditionally backreferences, and `\0` — which shares the
same diagnostic — can never be a backreference at all, since there is no group 0.

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

## K3 — OPEN, found 2026-08-10 (SR-2 sabotage validation)

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

**Not fixed in SR-2 on purpose:** SR-2's acceptance bar is byte-identical output,
and this is a behaviour change. **Fix:** its own commit, immediately after —
including the open question of whether the inner-bracket `[[:` case needs the
same terminator condition (`[a[:b]` is unmeasured).

---

_Two open issues: K2 (cosmetic) and K3 (over-acceptance). Performance and
architecture debt lives in docs/plan.md; other engines' bugs in
docs/upstream_issues.md._
