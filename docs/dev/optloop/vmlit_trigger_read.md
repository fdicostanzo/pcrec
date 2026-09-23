# `[OPT-VMLIT]` trigger read — does gcc fuse a VM literal run, and is the row's own trigger met

Lane `litrun`, 2026-09-23, branch `lane/litrun` from `main`. Measurement
only (D77): no changes under `src/`. This memo reads against
`docs/dev/plan.md`'s `[OPT-VMLIT]` row verbatim rather than re-deriving
the question from scratch — read that row first:

> **[OPT-VMLIT] STATE:not-started (TRIGGER PARTIALLY MEASURED 2026-08-31
> by [OPT-5] STEP 0: literal words confirmed one-byte-per-label consume
> chains in emitted C, never memcmp; [...])** [...] MEASURED-NEED TRIGGER
> (D77): the literal-stepping share of a VM verify on the bench's
> ctx/level-context cells — the alternation branches there are literal
> WORDS stepped per byte on every verify, and the post-[OPT-4.1] residual
> vs the JIT (1.5-2.9×) is plausibly mostly this [...]

Two halves: (1) does gcc find the fusion on its own, or must pcrec emit
it — the row's own "never memcmp" clause, left open whether that is
compiler behavior or emission choice; (2) is there a measured-need
population. §1 closes (1). §2 answers (2) for a DIFFERENT population than
the row names, and states plainly that the row's own named population
(ctx/level-context vs JIT) is still unmeasured.

## 1. What gcc already does — closes the row's "never memcmp" clause

**This is not a new question.** `docs/design/reqpos_2b.md` §3.2 (lines
45-50) already measured that `gcc-16 -O2` lowers a constant-length
`memcmp` to one word load + one compare, no call — `memcmp(p, "abcd", 4)`
to a 32-bit load, `memcmp(p, "github_p", 8)` to a 64-bit load (note: the
SAME real pattern, `wild-secrets-github-pat`, that §2 below reaches
independently) — for the `[OPT-REQPOS]` tier-2b SEARCH-side prefilter
(one `memchr`-class pass over the whole window, not the VM's per-attempt
literal consume `[OPT-VMLIT]` is about). **That result is prior art here,
cited rather than re-run.**

What was NOT yet measured, and what `[OPT-VMLIT]`'s own trigger clause
leaves open, is whether gcc finds this fusion on its own from the
if/goto or `&&` shapes pcrec would naturally emit, or whether pcrec has
to ask for it explicitly by emitting `memcmp` directly. This lane
measured that gap.

Commands (arm64, this Mac, `gcc-16 -O2`/`-O3`):
`build/pcrec -p rx --engine=vm --emit-main -o X.c --pattern '...'` for
`xyzabcdefgh` (plain), `(?i)xyzabcdefgh` (caseless), `[0-9]+abcdefgh`
(mid-pattern), then `gcc-16 -O2 -c X.c -o X.o && objdump -d X.o`.

**Emitted C confirms `[OPT-5]` STEP 0's "never memcmp" holds at this
pin**: 11 separate blocks, each `rx_L<n>: if (scan_position <
subject_length && (subject[scan_position] == <byte>)) { scan_position++;
goto rx_L<n+1>; }` (`emit_vm.c`'s `A_CLASS` arm — pcrec has no `A_LIT`
kind, every literal byte is a one-byte class node under `A_CAT`); mid-
pattern shows `[0-9]+` fusing into one scan-edge `while` loop while the
trailing `abcdefgh` stays 8 per-byte blocks.

**Assembly** (`_rx_match_in`): 11 separate `ldrb`+`cmp`+`b.ne` triplets,
each with its own bounds check — no fusion, matching the emitted C.

**Hand-rewrite** (`handrewrite.c`: one bounds check, then one
`&&`-chained expression over the 11 byte tests — the shape a reviewer
might expect gcc to find on its own): gcc-16 -O2 AND -O3 hoist the 10
redundant bounds checks into one, but still emit **11 separate**
`ldrb`+`cmp`+`b.ne` — **no word-compare fusion at either optimization
level.** This is the new fact beyond `reqpos_2b.md` §3.2, which measured
`memcmp` directly and never tested whether an ordinary compare chain gets
the same treatment on its own.

**Explicit `memcmp()`** (`memcmpver.c`): gcc-16 -O2 folds
`memcmp(subject+scan_position, "xyzabcdefgh", 11) == 0` to **3 loads** —
an 8-byte `ldr x1,[x0,x2]`+`cmp`, a 2-byte `ldrh`+`cmp`, a trailing
`ldrb`+`cmp` — reproducing `reqpos_2b.md`'s finding independently at a
different call site.

**x86_64** (light probe, `ssh duxevents@100.69.121.107`, gcc 15.2.0 -O2,
scratch dir created and removed, two small compiles, no suite): `&&`-chain
stays 11 separate `cmpb $imm,off(%rdi,%rdx,1)`+`jne`; `memcmp()` folds to
**2** compares — an 8-byte `movabs`+`cmp` covering bytes 0-7, a 4-byte
`cmpl` covering bytes 7-10 (overlapping window), tighter than arm64.

**§1 verdict — the row's open half is now closed**: gcc never fuses a
compare-chain shape on its own, `&&` included, -O2 or -O3, either target.
Only explicit `memcmp()` against a compile-time constant gets gcc's own
fusion. `[OPT-VMLIT]`'s "never memcmp" is confirmed as an EMISSION choice,
not a missed compiler opportunity — pcrec must emit the `memcmp` form
itself; there is no free lunch to wait for from a newer gcc.

## 2. The population — NOT the row's own named target, stated plainly

`[OPT-VMLIT]`'s own MEASURED-NEED TRIGGER names a specific population:
"the bench's ctx/level-context cells" (`bench/bounded/patterns/
ctx-lazy-256.rx`, `ctx-greedy-256.rx`, `ctx-lazy-1024.rx`,
`ctx-lazy-64.rx`, `bench/loglines/patterns/level-context.rx`) against
`pcre2-jit`, residual "1.5-2.9×". **This lane did not measure that
population** — those subbenches (`bounded`, `loglines`) are outside the
`capability@0.1` bench this lane's tooling reaches, and a fresh JIT-ratio
bench run is a heavier bench-window operation than this lane's light-probe
scope covers. Read the patterns directly instead of timing them: they ARE
exactly what the row's premise describes —
`\b(?:fail|abort|panic)\b.{0,256}?\b(?:disk|memory|socket|quota)\b` and
`\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|
unreachable)\b` — literal-word alternation branches, each branch a
per-byte if/goto chain by §1, stepped on every verify attempt the lazy/
greedy `.{0,N}` body generates. **The row's own trigger measurement (ctx/
level-context throughput vs `pcre2-jit` at the current pin) is still
owed** — named explicitly in §4, not assumed answered by anything below.

What this lane DID measure, as a second, independently-found population:
crossed `docs/dev/optloop/b2ledger/stampdiff.json`'s per-pattern
`RX_ENGINE` against the 60 losing match-regime cells of
`cycle1_caps_view.md` + `cycle1_nocaps_view.md` (AFTER pin) — the
`capability@0.1` bench, not `bounded`/`loglines`. Literal-run parser:
`scratchpad/litrun/analyze.py`, a rough tokenizer (strips `[...]`
classes, `(){}|^$.`, quantifiers eat back one char, escaped shorthand
`\d\w\s\b` etc). **Limitation found by hand-check, then verified against
every `.rx` file**: it doesn't special-case `(?<name>`/`(?&name)` group
syntax — misreads `bracket-array-define`'s
`(?(DEFINE)(?<brackets>...)(?&brackets))` as a false 10-byte "literal
run".

Of 60 losing cells, 7 route through the VM (`RX_ENGINE "vm"`); 2 are the
`bracket-array-define` false positive; **5 genuine VM-route losing cells
carry a real literal run ≥4**, all `auto-caps` (captures force VM here
per `select_engine.c`):

| pattern | regime | true literal | ratio |
|---|---|---|---|
| `wild-secrets-username-password-pair` | thr | 9B, one per alt branch (`username`/`password`/…) | 55.16x |
| `wild-secrets-aws-access-key-id` | thr / srch | 4B (`AKIA`/`AGPA`/…) | 29.65x / 1.27x |
| `wild-secrets-github-pat` | thr / srch | 11B (`github_pat_`) | 2.66x / 1.01x |

`auto-nocaps` has **zero** VM-route run≥4 losses. Checked
`RX_VM_PREFILTER` before speculating further: already `"hybrid"` on all
three, so these ratios are not an absent-prefilter artifact — whatever
gap remains is per-attempt match cost, which a fused compare would touch.

## 3. The general-mechanism note (no build) — pointing at the shipped design, not inventing one

`src/opt/reqbyte.c` (`RX_REQ_RUN`, tier 2b) derives the necessary-run
fact but only for the search-side prefilter. A `[OPT-VMLIT]` fused VM
compare would be a second PATFACTS reader of that shape (D120) for
`github-pat`'s single-branch case only — §2 shows the rest of the real
population (`username-password-pair`, `aws-access-key-id`) has no
whole-pattern `REQ_RUN` (alternation, per-branch literals), so the
fusion has to key off each `A_CAT` spine's own run of single-byte
`A_CLASS` children directly in `emit_vm.c`, the way `[OPT-VMLIT]`'s own
row already describes (the M2.8 trie's non-branching chains as the
finder). Cheapest caseful form per §1: recognize a maximal single-byte
`A_CLASS` run, emit one bounds check + `memcmp()`.

**Caseless is not this lane's to redesign — `[WORD-FOLD]` already owns
it.** That row (plan.md, "8 byte masks then compare?") specifies the
canonical form exactly: `memcpy(&w, subject+pos, 8); (w & K) == T`,
per-byte `K`/`T` built from each position's accepted-byte cube (exact
byte `K=0xFF`, caseless letter `K=0xDF`), uniform across exact and
caseless positions and the window's tail alike — not a new masked
compare invented here. `[WORD-FOLD]`'s own D77 gate is an unrun census
(corpus+bench literal runs ≥4-8 bytes with a cube-but-not-singleton
position); §2's `wild-secrets-*` cells are candidate population for that
census, not built or counted against it here (out of this memo's scope).
`[OPT-VMLIT]`'s SIBLING note already ties the two rows together — this
memo does not re-tie them.

**`[CLS-TREE]`/`[OPT-CLSPACK]` is the adjacent but different kit member,
not the answer here.** `form_char_step0.md:84`'s "atom" form — one
shared byte→atom partition table plus a 64-bit mask per class — is a
PER-POSITION single-character class test (`vm_cls_test`'s general form).
`[WORD-FOLD]`'s cube compare is SEQUENCE-level, vectorized ACROSS
positions in one window load. `[OPT-VMLIT]`'s literal-run fusion is
sequence-level too (a run of exact or fold-pair positions), so it is
`[WORD-FOLD]`'s territory for the caseless case, not `[CLS-TREE]`'s.

## 4. Row disposition recommended for `[OPT-VMLIT]`

**Stay `STATE:not-started`.** Update the row's own trigger annotation to
record that the "never memcmp" clause is now FULLY measured (cite this
memo): confirmed at this pin, on both engines this lane reached, that
gcc will not find the fusion from an if/goto or `&&` chain on its own —
only explicit `memcmp()` emission gets it, closing the compiler-vs-
emission ambiguity the row's 2026-08-31 partial measurement left open.

**Do NOT open the row in cycle 3 on §2's `wild-secrets-*` numbers** —
that is a real but SECOND population, not the row's own named trigger.
**The one measurement still owed before the row can open**: a bench pass
timing `bench/bounded`'s `ctx-lazy-*`/`ctx-greedy-*` and
`bench/loglines`'s `level-context` cells against `pcre2-jit` at the
current pin (the row's own stated "1.5-2.9× residual, plausibly mostly
this" needs a current number, not the 2026-08-30-vintage one the row's
text carries) — a heavier bench-window operation, not a light probe, so
named here rather than run. If that residual is still real and still
substantially literal-stepping, `[OPT-VMLIT]` opens on its own named
population; §2's 5-cell `capability` population is then a second,
already-measured witness set the design note can also cite.
