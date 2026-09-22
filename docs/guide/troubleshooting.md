# Troubleshooting

## Reading a refusal

pcrec refuses cleanly rather than miscompiling, and every refusal names
what was wrong. A syntax error names the construct and a byte offset into
the pattern (pcrec's own offset — its own parse position, not
necessarily what libpcre2 would report for the same input, though it
always points at something real pcrec actually reached). A construct
pcrec recognizes but hasn't built support for refuses with `requires
module 'X'` — see [features and modules](features-and-modules.md). A
pattern that's legal but too expensive to compile refuses with a message
naming the resource it exceeded and, often, a way around it (a different
`--engine`, a `--max-*` flag) — see [tuning and limits](tuning-and-limits.md).
None of these three cases are the same kind of problem, even though they
all arrive as a nonzero exit and a stderr line — read the message rather
than assuming "syntax error" for every refusal.

## Three exit-code vocabularies that share small integers and nothing else

This is the one thing about pcrec's numbers most likely to bite a script
that isn't careful:

| vocabulary | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| `pcrec` itself | success | usage error / compile refusal | — | `--explain` internal-dissent-only (steady state: never fires) |
| an `--emit-main` binary | match | no-match | usage error | give-up |
| a generated function's give-up code | (not applicable — see below) | | | |

`pcrec`'s own exit code tells you whether **the compile** succeeded. An
`--emit-main` binary's exit code tells you what **that one run**
concluded about its one subject — a completely different question,
answered by a completely different program. And a generated matcher
function's give-up return value (`PCREC_ERR_STEPS` and friends, all
negative) is a third, C-level vocabulary that has nothing to do with
either exit code — see [using the matcher from C](using-the-matcher-from-c.md).
If you're scripting against pcrec, be explicit about which of the three
you're checking; don't let "0 means good" carry over from one to
another.

## Size-cap refusals

Covered in full in [tuning and limits](tuning-and-limits.md): pcrec
bounds how much C it will emit, as a failsafe. If you hit this, the
message tells you the cap you crossed and pcrec has already tried
dropping optional machinery to fit before refusing — the levers from
there are raising the cap, forcing a smaller unroll factor, changing
engine, or splitting the pattern.

## Give-ups at run time

A negative return from a generated matcher that isn't `-1` (or, for
`<prefix>_search`, `0`) is a give-up: the engine ran out of budget rather
than concluding "no match". This is a real, defined outcome, not an
error in the matcher — see [using the matcher from C](using-the-matcher-from-c.md)
for the code table and [tuning and limits](tuning-and-limits.md) for
where each budget comes from and how to raise it.

## Where to ask

pcrec is pre-1.0 and still moving — if a refusal seems wrong (a
construct pcrec claims doesn't exist but does, or a match that looks
incorrect for syntax pcrec claims to support), that's a real bug, not a
documentation gap. [`CONTRIBUTING.md`](../../CONTRIBUTING.md) has the
process for opening an issue, including what to paste from `make test`
if you're checking whether your build is healthy first.
