# Critic lens EMIT: emitted vs replaced (round "iter")

SUBJECT 588714855 (worktrees/crit-iter/build/pcrec), BASE = main's build/pcrec (main's src/ == BASE's src/,
checked with `git diff --stat BASE HEAD -- src lib cli memfn`: empty).
Method: `pcrec -p rx [--features all] [-e utf8] --pattern P` with both compilers, `gcc -O2` (Ubuntu gcc 15,
default -fstack-protector-strong), per-symbol `nm -S` and `objdump -d`. Speed is `perf stat -e instructions:u`
(deterministic to 1-3 instructions between runs), with the artifact compiled to its own `.o` and linked to the
driver (a same-TU driver lets gcc inline `rx_search` into the caller and hides entry-level changes; first run
was discarded for that reason). Callgrind with `-g` for per-line attribution.
Scratch: /tmp/claude-1001/crit-iter/emit/ (gen.sh, cmp.sh, syms.sh, fn.sh, drv.c + bench.sh = iterators,
drv2.c + bench2.sh = existing entries BASE vs SUBJECT; bench_sep.out, bench2_sep.out hold the runs).

"L" below = the caller's hand loop before this change: `rx_search(s,n,from,caps)`, then
`from = end > start ? end : rx_next_pos(s,n,start)`, stop after an empty match at n. "N" = `rx_next` loop,
"K k" = `rx_next_n(it, caps, k)` loop. Numbers are instructions:u per match, driver baseline subtracted.

---

## EMIT-1 CONFIRMED (speed): the VM accept-label guard slows EXISTING `_search`/`_match`/`_match_caps` on every vm-guard artifact whose matcher body is out of line

Site: src/gen/emit_vm.c:12922-12938 (the `if (run->notempty && scan_position == ctx->pos) goto fail;` guard),
:11857-11868 (the `notempty` field), :12614-12621 (`run->notempty = 0` in every `_run_state_init`),
:13884-13916 (`<p>__retry`, the second caller of `<p>_match_anchored`, with `notempty = 1`).

The comment at 12930 says "Every other caller leaves `notempty` 0, so it folds away inlined". It folds only
where `<p>_match_anchored` is always_inline (small patterns: `(a*)`, `ab\Kc?`, `(a|b)*c?` measured flat). Where
gcc keeps `<p>_match_anchored` out of line (any larger VM pattern), the guard is a load + test + compare at every
accept, the init pays a store, and the function's code changes shape (callgrind on `(a|b)*?\1?`: the guard line
alone is 4 instructions/call, the store 1, the rest of the +16 is the body's reshuffled fail path:
`rx_match_anchored` 396,066 -> 492,082 instructions over 6,001 calls, static size 125 -> 186 instructions).

Repro: `scratch/gen.sh vg2 '(?:(a)|b)*' --features all; scratch/bench2.sh vg2 'aab ' 2000 10`

| pattern (all RX_ITER_RETRY "vm-guard", matcher out of line) | subject unit | `_search` loop | `_match` each pos | `_match_caps` each pos |
|---|---|---|---|---|
| `(a\|b)*?\1?` | `ab ` | +11.7% (+20/call) | +14.1% (+17/call) | +12.2% (+17/call) |
| `(?:(a)\|b)*` | `aab ` | +10.1% (+30/call) | +11.3% (+29/call) | +10.6% |
| `(x)?(?:y\|z)*\1?` | `xyzx ` | +5.4% | +5.1% | +4.6% |
| `((a+)\|(b+))*` | `aabb ` | +3.7% | +4.3% | +4.0% |
| `(?:(\w)\1)*` | `aabb ` | +2.7% | +4.1% | +3.9% |
| `(\w+)?\s*(\d*)` | `ab 12 ` | +2.3% | +2.0% | +1.8% |
| `([a-z]+)?=?(\d+)?` | `ab=12 ` | +2.1% | +1.8% | -0.1% |

Answers identical (count and offset checksum equal BASE/SUBJECT in every row). Every artifact that does NOT
report an empty span is unaffected (no guard emitted): 12 non-nullable VM/DFA patterns measured flat.

Severity: speed, on entries that existed and that most callers use; for callers who never iterate.
Effort: small. Fix directions (pick by measurement): (a) the guard reads a PARAMETER of `<p>_match_anchored`
rather than a run-state field, so gcc's IPA-CP clones a `notempty=0` body for the six entries (the function
is `static`, not `noclone`); (b) `<p>__retry` gets its own copy of the matcher (a second `always_inline`
expansion) so the entries' body never sees the guard; (c) at minimum the comment's "folds away" claim is
false as stated and must say "where inlined".
Blast radius: every VM artifact with RX_ITER_RETRY "vm-guard" and a non-inlined matcher; all six VM entries.

## EMIT-2 CONFIRMED (speed): on nullable patterns the iterator pays the NOTEMPTY retry at every empty match even where the pattern's priority order makes the retry provably useless (unlock)

`<p>__step` (src/gen/emit_iter.c `emit_step`, retry branch) runs `<p>__retry` after EVERY empty match. The
retry can only find something when, at the empty match's position, a consuming thread ranks BELOW the
empty accept (lazy `*?`/`??`, an empty-first alternation `(?:|a)`). For greedy patterns the preferred match at
p is empty only if no consuming thread at p can accept, so the retry always returns -1 and the step then does
exactly the hand loop's `next_pos` advance. Evidence: on every greedy row below the iterator's answers equal
the hand loop's (count and checksum), while on the lazy `(a|b)*?\1?` they differ (L 1,200,020 vs N 2,000,020
matches): the retry fires there and nowhere else.

| pattern | engine | unit | L | N | K64 | N vs L |
|---|---|---|---|---|---|---|
| `a*` | DFA dfa-root | `aab` | 65.0 | 94.5 | 74.9 | +45% |
| `a*` utf8 | DFA dfa-root | `aéb` | 76.3 | 113.3 | 90.5 | +48% |
| `(a*)` | VM | `aab` | 75.0 | 100.0 | 66.9 | +33% |
| `ab\Kc?` | VM | `abx` | 228.0 | 253.0 | 221.0 | +11% |
| `(?:(a)\|b)*` | VM | `aab ` | 322.0 | 440.0 | 412.9 | +37% |
| `((a+)\|(b+))*` | VM tiered | `aabb ` | 498.0 | 648.5 | 622.9 | +30% |
| `(?:(\w)\1)*` | VM tiered | `aabb ` | 298.5 | 391.5 | 365.9 | +31% |

On the VM rows even `_next_n(64)` stays 22-28% behind the hand loop: the retry is a full anchored attempt
(`_run_state_init` + `<p>_match_anchored` + its failure), per empty match.
Proposed general form: a pattern fact "a consuming thread can rank below an empty accept at the start"
(read off the start closure's priority order, the same order both engines honour); where it is false the
step advances with `next_pos` and the artifact emits no `__retry`, no notempty machine (`Job.nedfa`, DFA:
`rx__retry` 310 B + 268 B tables on `a*`), and no VM guard (which also removes EMIT-1 for those artifacts).
RX_ITER_RETRY would read "none" there. SUSPECTED as to the exact predicate (lookarounds, `\K`, `\G` need
care); CONFIRMED as to the cost. Severity: speed (+11..48% per match on empty-heavy subjects). Effort:
medium (one fact in src/facts + two emitter reads). Blast radius: every reports-empty artifact.

## EMIT-3 CONFIRMED (speed): on the DFA attempt route the iterator loses to the hand loop at every k

`<p>__find` is `noinline` there by design (findall_iter.md §2.2 `shared` row). `_search` is a 2-instruction
tail jump, so the hand loop pays one `jmp`; the controllers call `__find` and spill the cursor around it.

| pattern | unit | L | N | K1 | K4 | K64 |
|---|---|---|---|---|---|---|
| `^a\|b` | `bxb` | 78.0 | 100.0 | 131.0 | 99.5 | 89.7 |
| `(?m)^\w+` | `ab\n` | 123.0 | 145.0 | 176.0 | 144.5 | 134.7 |
| `\Ga` | `a` | 65.0 | 87.0 | 118.0 | 86.5 | 76.7 |

`_next` +22 per match (+17..34%); `_next_n(64)` still +11..15%. objdump of `rx_next_n` (`^a|b`): per match
4 stores + 4 loads of `s`, `n`, `lo`, `caps` to the stack around `call rx__find`, while only rbx/rbp/r12 are
used of the six callee-saved registers. `_next`: 3 stores + 3 loads (`it`, `lo`, `caps`) plus `sub/add rsp`.
The design's §4.1 H3 already records "spilled" for c3; this is the consequence on the route where the call
cannot be inlined: the iterator is slower than what a caller had. Severity: speed. Effort: small-medium (e.g.
pass the cursor to a shared `__find`-plus-advance step so the spill is inside one call, or let the noinline
body be `<p>__step` instead of `<p>__find`). Blast radius: ~233/4,243 corpus artifacts (the note's own count).

## EMIT-4 CONFIRMED (speed): VM artifacts whose `__find` is not always_inline: `_next` and `_next_n(64)` lose to the hand loop

| pattern | unit | L | N | K4 | K64 |
|---|---|---|---|---|---|
| `(a\|ab)(c\|bcd)(d*)` | `abcd ` | 462.1 | 483.1 | 479.8 | 467.9 |
| `(a+)\1` | `aaaa ` | 491.0 | 512.1 | 508.8 | 496.9 |

objdump of `rx_next_n` (`(a|ab)(c|bcd)(d*)`), own-storage path: per match 7 stores + 7 loads to the stack
around `call rx__find`, the run-state bind (4 stores) and the `it->bufs` test redone per step. `rx_search`
pays canary + bind + call too, so the loss is the spill traffic. Contrast: VM artifacts whose `__find` IS
inlined (`(a)`, `a(b|c)+d`, `(a+)(b+)`) win at K>=4 (e.g. `(a+)(b+)` L 385.1, K64 359.0).
Severity: speed (+1..5%; small but the opposite of the next_n premise). Effort: as EMIT-3. Blast radius: VM
artifacts above the inlining threshold.

## EMIT-5 CONFIRMED (speed, minor): `_next_n(it, caps, 1)` costs 23-35 instructions per match more than `_next`

All 19 patterns in bench_sep.out: K1 - N = +28 (`\w+`), +31 (`hello`), +32 (`a*`), +30 (`\b`), +31 (`^a|b`),
+31 (`\Ga`), +26 (`(a+)(b+)`), +33 (`a(b|c)+d`), +23 (`(a)`), +35 (`(a|ab)(c|bcd)(d*)`), +28 (`ab\Kc?`),
+27 (`\w+` utf8). Cause: the controller's fixed prologue/epilogue (NULL-caps test, `k == 0` test, six pushes,
cursor load/store, `i * NCAPS` stride) amortizes only over k. Not wrong; worth one spec/guide sentence ("use
`_next` for one-at-a-time") since `rx_info.next_n` callers may call with k = 1. Severity: doc. Effort: trivial.

## EMIT-6 CONFIRMED (size): every artifact carries three copies of the search body for the iterator, one of them for the cold NULL-caps path only

`<p>__one_local` (emit_iter.c `emit_controllers`) is `noinline` but calls the `always_inline` `<p>__one_call`,
so it holds a full copy of `__step`/`__find`; `_next` and `_next_n` hold one each (VM: two each, the bound-
buffers and own-storage steps). Measured `.text` (BASE -> SUBJECT, whole object):

| pattern | .text | `__one_local` | `_next` | `_next_n` |
|---|---|---|---|---|
| `\w+` | 2,719 -> 4,623 | 468 | 524 | 601 |
| `a*` | 1,435 -> 4,059 | 513 | 507 | 718 (+ `__retry` 310) |
| `(a+)(b+)` (VM) | 4,848 -> 10,296 | 1,578 | 1,659 | 1,955 |
| `(a*)` (VM) | 1,705 -> 5,673 | 1,061 | 1,202 | 1,432 |
| `ab\Kc?` (VM) | 2,800 -> 7,104 | 1,214 | 1,388 | 1,519 |

`.text` grows 1.4x-3.3x per artifact, and `rx_info.next` pins all of it under `--gc-sections` (ruled, i1build
ruling 2; listed here only as the multiplier on this finding). `__one_local` is 24-35% of the iterator's
text. Fix: `__one_local` calls `<p>_next(it, local)` (or a `noinline` `__one_call`) instead of expanding it:
the canary stays out of the hot controllers, the copy goes. Cost: one extra direct call on the NULL-caps path.
Severity: size. Effort: trivial. Blast radius: every artifact.

## EMIT-7 CONFIRMED (speed, minor): VM non-inlined `__find` re-tests `search_from > subject_length` that every caller already tested

emit_vm.c:13161-13166 keeps the range test in `<p>__find`; `vm_emit_search_run_prologue` (:12416) adds it
again in `_run`, and `__step` tests `lo > n` before every call. Where `__find` is out of line the test is
paid twice: `rx_search` 18 -> 21 instructions, `rx_search_in` 32 -> 43 (`(a|ab)(c|bcd)(d*)`, `(a+)\1`),
measured +3 instructions per `_search` call (+0.6%). Fix: drop the body's own test (all callers guard).
Severity: speed (minor). Effort: trivial.

## EMIT-8 CONFIRMED (speed, minor): a compound's attempt-route PART is split into wrapper + `noinline` `__find` although parts never iterate

emit_comb.c:533-541 splits every `PCREC_ENTRY_SEARCH` emission; for a part, `find_body_shared`
(emit_dfa.c:2176) is true on the attempt route (no `comp_shell` in the part's own job), so part F of
`^\s+|\s+$` becomes `rx__f_search` -> `static noinline rx__f__find` where BASE inlined F into the controller
(`rx_search` 71 -> 22 instructions + a call). Measured net effect on that compound: flat or better (`L` -2.3%,
other entries +0), so no speed loss observed; the finding is the split serving no caller and the
part's `copyable` fact now being written for the wrapper, not the body (emit_dfa.c:4172-4178). Severity:
maintenance. Effort: trivial (`pcrec_is_part(cx)` keeps the unsplit body).

---

## PROBED-AND-HELD

- Existing DFA entries (`_search`, `_search_in`, `_match`, `_match_caps`, `_in` siblings, `_next_pos`,
  `_valid_upto`): instruction-multiset identical or register-renamed only on 12 DFA artifacts (`\w+`, `hello`,
  `a*`, `\b`, `a+$`, `a*?b`, `(?=a)`, `\w+` utf8, `a*` utf8, `\w+` utf8 -futf-check, `^\s+|\s+$`, `^|$`);
  perf over L/M/C loops: within +-25 instructions total (constant) except attempt route `_search` +2/call
  (`^a|b`, the designed tail jump) and `\Ga` +0.8/call; `\b`, `a*` utf8, `(?m)^\w+`, `^\s+|\s+$` slightly faster.
- Existing VM entries on 8 non-reports-empty or inlined-matcher artifacts (`(a)`, `a(b|c)+d`, `(a+)(b+)`,
  `(a|ab)(c|bcd)(d*)`, `(a+)\1`, `(a*)`, `ab\Kc?`, `(a|b)*c?`): flat except EMIT-7's +3.
- `__find` body vs BASE `_search_run` body (VM): instruction-identical.
- Residual twins (F-1) under `-fPIC`: BASE `\w+ -e utf8 -futf-check` had 2 PLT calls to `rx_valid_upto`
  inside the artifact, SUBJECT 0; exported forwarders compile to the old body or one `jmp`. Iterators make
  no PLT call in any probed artifact.
- `-futf-check` hand loop is QUADRATIC (each `_search` revalidates the tail): `\w+` utf8 on 20 KB, 8,000
  matches: L 1,729,284,187 instructions vs N 1,575,976 (1,097x). The iterator's once-per-bind check removes it.
- Non-nullable unanchored DFA and inlined-VM artifacts: N within +0..+3 of L (`\w+`, `hello`, `\b`, `(?=a)`,
  `a*?b`, `\w+` utf8, `(a+)(b+)`, `a(b|c)+d`) except `(a)` +16; K4 beats L on all of them, K64 by 5-30%.
- `\b` (dfa-root) and `(?=a)`: retry never needed by subject, N = L.
- `rx_info` grows 16 bytes (two pointers) on every artifact; retry machine duplicates the 256-byte byte-class
  table (identical content to forward/anchored, the anchored machine's precedent).
- Not covered: variable-bearing artifacts (`rx_iter_vars`), bound `_iter_buffers`, the latin-1/ucp byte arm,
  `--part-layout` controls.
