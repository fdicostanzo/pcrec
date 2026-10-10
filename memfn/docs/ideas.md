# memfn ideas log — raw observations of possible optimizations

Append-only, newest at the bottom. Entries are UNEDITED observations as they
were noticed: a pattern, what the kit emitted, and what might be better. None
is a request, a plan row or a decision. Each waits to be evaluated later
against a measured trigger (D77). When one is evaluated, add a dated
`-> evaluated:` line under it (filed as R-n / plan row X, or dropped and why).
Never rewrite the original text.

Format: `## YYYY-MM-DD — short title`, then the observation, the evidence
(pattern, build, emitted text), and a first guess at impact.

## 2026-10-10 — vrun end bound uses the run's length, not the pattern's minimum remaining length

Seen while answering Frank's questions about vrun-w32 (lane/memfn-r13 build,
`build/pcrec -p rx -fmemfn-simd`). `(?i)cat\d{20}` emits the same end guard as
`(?i)cat`: `if (i + 2 >= n) return n;` (scalar body `cand + 2 >= n`), even
though no match can start in the last 22 bytes. The scan stops at the RUN's
span, not at the pattern's minimum length from the run's start to the
pattern's end. Using that minimum would stop the search earlier and skip
candidates the matcher rejects anyway.
- Answers: unchanged (pure early-out).
- Saving: at most ~min-length bytes of tail per search call. It matters for
  many short subjects with a long fixed tail; it is negligible on long
  subjects.
- It is a general fact, not a vrun one: every search form (scalar and SIMD)
  could use it. Under D157 pcrec would supply it to the kit as a FACT, e.g.
  "min bytes from run start to pattern end", so it starts as a request from
  main.
- First guess: low impact; a BOONIES-class row unless a short-subject
  workload shows it.

## 2026-10-10 — vrun with a repeated byte emits duplicate constants in the C text

`(?i)azzb`: the kit picks KA = `z`@2 and KB = `z`@1 and declares
`ma/va/mb/vb` with the second pair identical to the first. gcc -O2 -mavx2
merges them (one mask register ymm3, one compare register ymm2 for both
loads), so there is no machine-code cost. The cost is text only (artifact
bytes, readability). It could be cleaned up in the kit's renderer if a text
size budget ever needs the bytes.
- Related: when the two picks are the same byte at adjacent offsets
  (`zz`), the second filter still pays for itself (it needs `zz`, not
  just `z`). Worth checking whether the ranking ever picks the same byte
  at a far offset, and whether a different second byte would filter better.

## 2026-10-10 — plain-case literals take no vrun form

`qeeeez`, `azzb` (no `(?i)`): `MEMFN_FORMS "none"`; they stay on the existing
scalar/libc path (memchr on one byte). vrun's two-position vector filter
might beat memchr when the first-picked byte is common in the subject. Open:
was plain-case excluded from batch 1 deliberately (memchr/memmem already
strong), or is it simply not reached yet? Check integration.md §R4.9 before
evaluating.
-> evaluated 2026-10-10: answered, deliberate. integration.md §R4.9.7.1
   ("the glibc-inside trap") excludes `fn-memchr` bodies from batch 1. A
   case-sensitive run scans ONE byte (pcrec's rarest pick: `z` at offset 5 in
   `qeeeez`) with glibc `memchr`, which is already SIMD inside, picked by
   CPU at load time. There is no measured cell showing a w16/w32 row beating
   it. The form is FILED as the `vrun` over `fn-memchr` row, with three
   trigger cells: exact window with a rare pick, exact window with a dense
   pick, and OFS run-pinned (`/user|/users`). This entry adds nothing new
   beyond that row.
