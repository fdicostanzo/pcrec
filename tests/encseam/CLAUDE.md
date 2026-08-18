# tests/encseam — the ENCODING SEAM's behavioural suite

[M5-SEAM] (D58, 2026-08-18). Part of `make test`; section target
`make test-encseam`. Also on the `make ubsan` / `make asan` suite lists,
because it RUNS generated code and those axes instrument what it runs.

## What this covers that nothing else does

The `.rxt` corpus checks what a pattern MATCHES, one search at a time. It
never runs a find-all LOOP — so `docs/spec/match_api.md` §3.1's protocol,
the one piece of the match contract a caller has to write themselves, was
documented and measured under R29 but never pinned by a test. This suite
compiles that loop against real artifacts and runs it.

It is also where `<prefix>_next_pos` — the encoding residual, [M5-SEAM]'s
first pulled entry (spec §3.1.1) — is exercised the way a caller uses it,
as opposed to `tests/codegen`'s structural check, which asserts the
NEGATIVE (no engine body calls it). The two see different things and
neither substitutes for the other.

Every case runs on BOTH engines: once as compiled (captures on, so a
capture-bearing pattern takes the VM) and once `--no-captures` (always the
DFA). The find-all protocol is a property of the search ENTRY, not of an
engine, and the two engines reach a span through completely different code.

## Files

- **run_encseam_tests.sh** — the runner.
- **findall_driver.c** — spec §3.1's loop, TRANSCRIBED. If it and the spec
  ever differ, one of them is wrong and the check has stopped meaning what
  it says. Its advance goes through `fa_next_pos`, not a literal `+ 1`,
  which is [M5-SEAM]'s whole claim. Prefix fixed at `fa` (a driver cannot
  be generic over a C identifier prefix).
- **findall_cases.txt** — TAB-separated CLASS / PATTERN / SUBJECT. The
  twelve agreeing pairs and three lossy ones are R29's set, re-measured
  here rather than cited; ten more were added at [M5-SEAM], including two
  over the EMPTY subject.
- **findall_oracle.py** — python3 `re`, TWO-ANSWERED per case.

## The two-answered oracle, and why the class is checked both ways

§3.1's loop is NOT `re.finditer`. On finding an empty match at `p`, PCRE2
and python retry at `p` under "empty match not permitted here"
(`PCRE2_NOTEMPTY_ATSTART`) and report the non-empty match too; pcrec's
entry points cannot express that retry, so for an empty-PREFERRING pattern
the protocol is knowingly LOSSY. Comparing pcrec against `finditer` alone
would therefore either fail the honest cases or force the check to accept
any difference at all — which is how a check goes vacuous.

So the oracle reports both answers, and:

- pcrec must equal the PROTOCOL answer **exactly**;
- an `exact` case must have protocol == finditer — if it starts diverging,
  the case FAILS rather than being reclassified;
- a `lossy` case must have protocol != finditer — if the divergence
  disappears, that is a spec event and the case FAILS;
- a `lossy` case's spans must be a strict SUBSET of finditer's. This is the
  clause that matters: the documented divergence is one of OMISSION only,
  and "differs somehow" would pass a genuine miscompile.

**What the oracle shares with the implementation is the LOOP RULE — which
is the spec text under verification — and nothing else.** Every span in it
comes from python's own independent leftmost-first engine via
`re.search(subject, pos)`. This directory is aware of this project's
standing lesson (a control sharing a source with what it controls); the
line is drawn at the matcher, deliberately.

## Non-vacuity, measured

Sabotaging the driver's advance (`fa_next_pos(s, n, caps[0][0])` ->
`caps[0][0] + 2`) produced 26 failures and 0 passes. Do not trust a green
run here after changing the driver without re-running that control.

## Adding a case

Append a TAB-separated line to `findall_cases.txt`. Subjects travel through
`argv`, so keep them printable ASCII with no tabs; a line with an empty
third field is the EMPTY subject and is a case worth having. Choose the
class by what python actually does, not by what looks right — run
`python3 findall_oracle.py < findall_cases.txt` and read both answers.

Maintenance: update this file when files are added/removed or their roles
change.
