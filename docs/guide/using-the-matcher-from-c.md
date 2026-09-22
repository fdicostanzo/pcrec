# Using the matcher from C

Every artifact pcrec generates exports the same shaped set of entry
points, whatever pattern it came from. This chapter is the guided tour;
[`docs/spec/match_api.md`](../spec/match_api.md) is the exact contract —
every signature, every edge case, every measurement behind a number here.

## The three ways to call it

| entry point | what it does | you know the start position? |
|---|---|---|
| `<prefix>_search` | searches `s[startpos..n)` for the leftmost match | no — it finds one |
| `<prefix>_match` | matches only at exactly the position you name, no captures | yes, and you don't want captures |
| `<prefix>_match_caps` | same anchored match, plus captures | yes, and you do want captures |

Reach for `<prefix>_search` unless you already know where to look —
it delivers captures too, given a `caps` buffer, so "find it and get its
groups" is one call. The anchored entries take an `rx_ctx` (the shared
context struct every artifact declares identically) rather than the
`(s, n, startpos, caps)` shape — see `docs/spec/match_api.md` §2/§3.2 for
its fields.

## Return conventions: read this table before you write an `if`

The two families use **opposite conventions for zero**, which is the
single easiest mistake to make against this API:

| entry | success | failure (no match) | give-up |
|---|---|---|---|
| `<prefix>_search` | `1` | `0` | a negative code, `<= PCREC_ERR_FLOOR` region — see below |
| `<prefix>_match` / `<prefix>_match_caps` | matched length (`>= 0`; `0` **is** a zero-length match) | `-1` | same negative codes |

So `<prefix>_search`'s `0` means "no match", while `<prefix>_match`'s `0`
means "matched, zero-length, right here" — two entry points on one
artifact, two meanings for the same integer. On any negative return, the
`caps` (or `caps_out`) array is left completely untouched — never read it
after a failing or give-up call.

## Give-up codes

A negative return that isn't `-1` means the engine spent its budget
without an answer, not that it found "no match" — treat these as a third
outcome, not as failure:

| code | meaning |
|---|---|
| `PCREC_ERR_STEPS` (-2) | backtracking step budget exhausted |
| `PCREC_ERR_FRAMES` (-3) | resume-frame or trail capacity exhausted (the depth ceiling; see [tuning and limits](tuning-and-limits.md)) |
| `PCREC_ERR_WORK` (-4) | forward-work budget exhausted |
| `PCREC_ERR_RECURSE` (-5) | reserved; no artifact produces it today |

These are shared, unprefixed constants (`PCREC_ERR_*`, not
`<PREFIX>_ERR_*`) — identical across every artifact regardless of
`-p`. Two more values sit just below this range and are **not**
give-ups — they mean the call was refused outright before any budget was
spent: `PCREC_ERR_INTERNAL` (the artifact caught its own inconsistency —
essentially never seen) and `PCREC_ERR_STARTPOS` (see
[encodings and subjects](encodings-and-subjects.md) — a `startpos` that
wasn't on a character boundary under UTF-8).

A give-up is retryable: call the same entry again with a larger buffer
(below) and you get a defined, correct answer — the matcher keeps no
state between calls.

## `startpos` and `_next_pos`

`<prefix>_search`'s `startpos` must land on a character boundary of the
artifact's encoding. Under the byte encoding every position qualifies, so
this costs a byte-only caller nothing. Under UTF-8, a `startpos` inside a
multi-byte character is refused (`PCREC_ERR_STARTPOS`) rather than
silently rounded. `<prefix>_next_pos(s, n, pos)` is the supported way to
step to the next valid boundary — use it to advance past a match when
scanning for all matches in a subject, exactly as pcrec's own find-all
examples do.

## The caller-provided buffer (`_in` entries)

A generated matcher never allocates: its backtracking storage is sized at
compile time and lives on the stack. That gives every artifact a fixed
recursion depth ceiling — measured in a subject SIZE, not a count, and
small enough to matter (a couple hundred bytes on some recursive
patterns). Three more entries — `<prefix>_search_in`, `<prefix>_match_in`,
`<prefix>_match_caps_in` — are their un-suffixed siblings plus one extra
argument: a `<prefix>_buffers` descriptor naming caller-supplied storage
to use instead of the compiled-in default. Passing `NULL` there is
defined to behave exactly like the un-suffixed call, so you can write one
call site and choose at runtime. Sizing a buffer, and what a give-up on a
supplied buffer means, is [`docs/spec/match_api.md`](../spec/match_api.md)
§10 in full; the short version is: if your subjects might be deep, or
you're on a small-stack thread, this is the entry you want.

## Reflection: `rx_info` and the compile-time macros

Every artifact exports `extern const struct rx_info <prefix>_info`, a
struct you can read at runtime to ask what this artifact is: which
engine, which limits it was built under, its capture count, and more.
A handful of the same facts are also available as `#if`-able compile-time
macros (`<PREFIX>_ENGINE`, `<PREFIX>_NCAPS`, and others) for code that
needs to branch at compile time rather than read a struct field — the
macro set is deliberately a subset of `rx_info`'s fields, so check
[`docs/spec/match_api.md`](../spec/match_api.md) §6 before assuming a
field you want has one.

## Next

- Compiling patterns without shelling out to the CLI:
  [using the library](using-the-library.md).
- What a give-up or a diagnostic should make you do:
  [tuning and limits](tuning-and-limits.md), [troubleshooting](troubleshooting.md).
