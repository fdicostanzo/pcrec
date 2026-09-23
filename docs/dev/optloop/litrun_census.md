# [OPTLOOP.litrun] — does gcc fuse a VM literal run, and is there a population to trigger fixing it

Lane `litrun`, 2026-09-23, branch `lane/litrun` from `main`. Measurement
only (D77): no changes under `src/`. Scratch files under the session
scratchpad, not committed.

**The question (Frank).** The VM emits a literal run as N per-byte
if/goto tests (`src/gen/emit_vm.c`'s `A_CLASS` arm — pcrec has no `A_LIT`
kind; every literal byte lowers to a one-byte class node, concatenated by
`A_CAT`'s `vm_cat`/`vm_emit`). The DFA's scan edges (`src/opt/scanedge.c`,
`PCREC_MIN_SCAN_CHAIN`) fuse counted runs of ONE class, not literal runs.
Should the VM fuse literal runs into a word compare / memcmp?

## 1. What gcc already does

`build/pcrec -p rx --engine=vm --emit-main -o X.c --pattern '...'` for
`xyzabcdefgh` (plain), `(?i)xyzabcdefgh` (caseless), `[0-9]+abcdefgh`
(mid-pattern), then `gcc-16 -O2 -c X.c -o X.o && objdump -d X.o`, arm64.

**Emitted C**: 11 separate blocks, each `rx_L<n>: if (scan_position <
subject_length && (subject[scan_position] == <byte>)) { scan_position++;
goto rx_L<n+1>; }` — matches the brief's cited shape; caseless uses
`(subject[scan_position] | 0x20) == <lower-byte>` per byte; mid-pattern
confirms the split — `[0-9]+` fuses into one scan-edge `while` loop, the
trailing `abcdefgh` stays 8 separate per-byte blocks.

**Assembly** (`_rx_match_in`): 11 separate `ldrb`+`cmp`+`b.ne` triplets,
each with its OWN bounds check — no fusion; caseless adds one
`orr w,w,#0x20` per byte; mid-pattern shows 27 total `ldrb` (1 scan-edge
load + 8 literal-run loads, `grep -c ldrb`).

**Hand-rewrite** (`handrewrite.c`): one bounds check
`scan_position+11<=subject_length` then one `&&`-chained expression over
the 11 byte tests. gcc-16 -O2 AND -O3 hoist the 10 redundant bounds
checks into the single one, but still emit **11 separate**
`ldrb`+`cmp`+`b.ne` — no word-compare fusion at either level
(`grep -c ldrb` = 22 across the file's two functions, both -O2/-O3).

**Explicit `memcmp()`** (`memcmpver.c`: one bounds check, then
`memcmp(subject+scan_position, "xyzabcdefgh", 11) == 0`): gcc-16 -O2 folds
this to **3 loads** — one 8-byte `ldr x1,[x0,x2]`+`cmp` against a built
immediate, one 2-byte `ldrh`+`cmp`, one trailing `ldrb`+`cmp`. This is
gcc's constant-length-`memcmp` builtin lowering, not its ordinary
compare-chain merger — the `&&` form never gets it.

**x86_64** (light probe, `ssh duxevents@100.69.121.107`, gcc 15.2.0 -O2,
scratch dir created and removed, two small compiles, no suite): `&&`-chain
is 11 separate `cmpb $imm,off(%rdi,%rdx,1)`+`jne` (load folds into the
compare's memory operand, still one pair per byte); `memcmp()` folds to
**2** compares total — an 8-byte `movabs`+`cmp` covering bytes 0-7, a
4-byte `cmpl` covering bytes 7-10 (overlapping window), tighter than arm64.

**§1 verdict**: gcc never fuses a hand-written `&&` chain of scalar
per-byte tests, -O2 or -O3, on either target. Only `memcmp()` against a
compile-time constant gets gcc's own fusion (11→3 arm64, 11→2 x86_64) —
pcrec has to ask for this explicitly; gcc will not find it on its own.

## 2. The population

Source: `docs/dev/optloop/b2ledger/stampdiff.json` (192 rows = 64
`pcrec-bench/bench/capability/patterns/*.rx` × 3 configs, `fix.RX_ENGINE`
per pattern/route). Loss population: `cycle1_caps_view.md`'s 39 ratio>1
rows (route `auto-caps`) + `cycle1_nocaps_view.md`'s AFTER-pin 21-row
table (route `auto-nocaps`) — 60 losing match-regime cells. Parser:
`scratchpad/litrun/analyze.py`, a rough tokenizer (strips `[...]` classes,
`(){}|^$.`, quantifiers eat back one char, escaped shorthand `\d\w\s\b`
etc). **Limitation found by hand-check, then verified against every
`.rx` file**: it doesn't special-case `(?<name>`/`(?&name)` group syntax
— misreads `bracket-array-define`'s
`(?(DEFINE)(?<brackets>...)(?&brackets))` as a false 10-byte "literal
run".

Of 60 losing cells, 7 route through the VM (`RX_ENGINE "vm"`); 2 are the
`bracket-array-define` false positive; **5 genuine VM-route losing cells
carry a real literal run ≥4**, all `auto-caps` (captures force VM here per
`select_engine.c`):

| pattern | regime | true literal | ratio |
|---|---|---|---|
| `wild-secrets-username-password-pair` | thr | 9B, one per alt branch (`username`/`password`/…) | 55.16x |
| `wild-secrets-aws-access-key-id` | thr / srch | 4B (`AKIA`/`AGPA`/…) | 29.65x / 1.27x |
| `wild-secrets-github-pat` | thr / srch | 11B (`github_pat_`) | 2.66x / 1.01x |

`auto-nocaps` has **zero** VM-route run≥4 losses — every such pattern that
loses there is already on the DFA route.

**Checked before speculating further**: `stampdiff.json`'s `RX_VM_PREFILTER`
for all three is already `"hybrid"` — a skip-ahead search exists. `RX_REQ_RUN`
is set only for `github-pat` (`"6875625f7061745f@3"`, single literal
branch); it is `"none"` for the other two, because `[OPT-REQBYTE]` derives
one run true of EVERY alternative, and these two vary per alt branch
(`AKIA` vs `AGPA` vs …). So the 55.16x/29.65x ratios are NOT explained by
an absent prefilter — the skip-ahead already runs; whatever gap remains is
in the per-attempt match cost itself, which is what a fused compare would
touch.

## 3. The general-mechanism note (no build)

`src/opt/reqbyte.c` (`RX_REQ_RUN`, tier 2b) already derives the
necessary-literal-run fact but only reads it for the `memchr`-class
prefilter. A fused VM compare would be a SECOND reader of that PATFACTS
shape (D120) for `github-pat`'s single-branch case only — §2 shows the
rest of the real population (`username-password-pair`,
`aws-access-key-id`) has NO whole-pattern `REQ_RUN` (alternation,
per-branch literals), so the fusion has to key off each `A_CAT` spine's
own run of single-byte `A_CLASS` children directly in `emit_vm.c`, not
off `reqbyte`'s intersection fact. Cheapest mechanism if triggered:
recognize a maximal run of single-byte `A_CLASS` nodes under one `A_CAT`,
emit one bounds check + `memcmp()` (§1: gcc fuses that form, not `&&`).
Caseless complicates it: PCRE2's per-byte `| 0x20` fold has no `memcmp`
equivalent — needs a hand-built masked word compare per emitted width,
a second code path beside the caseful `memcmp` one (or always emit the
masked-word form, trading away libc's own possibly-SIMD `memcmp` for the
common caseful case). Exactly `[[pcrec-general-mechanisms-not-special-cases]]`'s
territory — stated, not built.

## 4. Verdict: NOT MET, one more measurement named

§1: gcc never fuses the `&&`-chain shape pcrec would naturally emit; only
`memcmp()` gets fused. §2: the real population is thin — 5 cells, not
the naive 20 the raw census suggested (2 of 7 VM-route hits were a
parser false positive). §2 also rules out the prefilter as the cause
(already `"hybrid"` on all three), so a fused compare is aimed at the
right remaining cost.

**Before TRIGGER MET**: isolate the fused compare's OWN contribution.
Hand-patch ONE cell — `github-pat` is cleanest (single alternative, its
own `REQ_RUN` already computed) — to emit the `memcmp` form from §1 in a
copy of its generated matcher (no `src/` change), rebuild just that `.c`,
and re-run its `thr`/`srch` bench cells against the current 2.66x/1.01x
ratios. If the ratio closes substantially, the trigger is met on this
5-cell population; if it barely moves, the gap is elsewhere and the
mechanism's charge buys little against its caseless complication.
