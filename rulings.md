# Manager rulings for lane opt5s1 (read before each phase; do not commit this file)

## R1 (2026-08-31 ~10:1x, from Frank's design question — BINDING)
The scan edge integrates with the D82 forms model at BOTH levels, explicitly:
1. The region-emission decision (scan-edge vs ordinary table walk) is a D82
   SELECTION over candidates — first-applicable, the stamp names the chosen
   object, the deny flag rides the axis machinery. Not an if/then buried in
   the walk emitter.
2. The edge's RUN-EXTENSION BODY is its own form axis with a representation
   object (D82 bound 3 is satisfied — two real forms exist on day one):
   `scan-range` (contiguous class, sub/cmp, two immediates) and
   `scan-bitmap` (arbitrary class, bitmap test — note the bitmap load is
   value-addressed, not result-addressed, so the cursor stays the only
   loop-carried register; state that in the comment). Design the candidate
   list so a future `scan-simd` form ([OPT-SIMD], studies/simd1's
   classify+clz) drops in as a third candidate WITHOUT touching anything
   above the form — same edge, same stamp, same gates. Name the slot in the
   spec hunk.
D82 bounds apply with teeth: (1) zero-cost layering — the accessor must
flatten to the hand-written instruction sequence (objdump equality beside
answer identity); (4) the loop-text move is ONE abi bump, after which form
additions move only the accessor block. If either level resists this
factoring in the real code, STOP and report rather than approximating.

## R2 (2026-08-31 ~10:1x, Frank — BINDING addendum to R1's scan-simd slot)
Frank runs a macOS laptop on Apple silicon (aarch64/NEON) — DO NOT bake an
x86 assumption into the scan-simd slot's NAME or CONTRACT. Name/describe it
ISA-neutrally in the spec hunk ("a SIMD run-extension form, per-ISA gated,
scalar forms always available as fallback"), not as an SSE2 slot. Your
scalar scan-range/scan-bitmap forms are the portable baseline; nothing you
emit in STEP 1 may be ISA-conditional.

## R3 (2026-08-31 ~10:2x, Frank — representation only, NOT scope)
Frank: "isn't a loop over a static string just a memcmp: (?:ab){1,100}" —
yes: a chain whose advance classes CYCLE with period k (singletons = a
string) is the period-k generalization of your scan edge, body = a
counted loop of constant-length compares. DO NOT BUILD IT in STEP 1 —
scope stays period-1. But: give the IR scan-edge representation a
period/сlass-sequence field (period=1 everywhere today) rather than a
single class baked in, IF that costs nothing structural — so the string
form later is a criterion extension + a new body form, not a rewrite.
If a period field genuinely complicates STEP 1, skip it and say so in
the report — the refusal must stay clean either way (mid-period states
with differing exit targets → ordinary walk).
