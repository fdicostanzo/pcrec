# D6 critic — START-SET stage 3 (the DFA hat): SOUNDNESS against the oracle

Critic: read-only, lens "soundness of the engine change against the oracle".
Subject: `lane/ssbuild3` at `29873a3c`, binary `worktrees/ssbuild3/build/pcrec`.
Oracle: libpcre2-8 **10.48 (2026-08-31)**, Homebrew, Mac dev box. gcc-16.
Status: IN PROGRESS (written as I go).

## Method

Scratch harness (`/tmp/sscrit/diff.py`, not committed): per pattern, build
A = branch default and B = `-fno-start-set` (both `--features all`, plus the
row's flags), link both into one gcc-16 driver with libpcre2-8, and for every
subject and EVERY startpos 0..n compare `A_search` vs `B_search` (return +
all capture spans) and A vs `pcre2_match(startoffset=sp)` (all ovector
pairs up to `A_NCAPS`). Subjects: the hand witnesses on the row plus N
random strings over a per-pattern alphabet. Every row prints the artifact's
`ENGINE / VM_PREFILTER / DFA_PREFILTER` so a row that never reached the hat
is visible as such.

Harness calibration note: pcrec `-e utf8` WITHOUT `--ucp` is ASCII `\w`/`\b`
(UCP `\b` under utf8 is refused, "needs [UCP] U3/U4"), so the oracle row is
`PCRE2_UTF` alone; my first pass wrongly added `PCRE2_UCP` and produced
hundreds of HAT==DENY!=PCRE2 rows that were MY error, not pcrec's.
(Side NOTE, not this lens: `pcrec --help` says `--ucp` is "implied by -e
utf8"; the measured behaviour is that it is not.)

## Findings (running)

### F1 — BLOCKER (compile regression; the `T == S` premise is false): the build assertion FIRES on valid patterns at default flags

`pf_dfa_start_set` asserts `nt == ns` ("`E*` is all 256 on every seeded
machine — a byte that begins no thread moves every seed to
`seed[class(b)]`, and two distinct seeds cannot both stay"). The argument
covers only bytes that begin NO thread, i.e. `b ∉ S`. For `b ∈ S` it says
nothing, and it is false: a byte of `S` can leave EVERY seed (and `s0`)
where it is.

Witness `(?<=\w) *a` (also `(?<=\w)-*a`, `(?<=\w) *?a-`, and the
realistic `(?<=\w) *(?:and|or)\b` and `(?<!\s) *[a-z]`), no flags beyond
`--features all`:

| build | result |
|---|---|
| branch default | `rc=1  pcrec: internal error: the DFA hat's T = S & E* dropped 1 start-set byte(s) on a seeded machine (startset.md §4.1a)` |
| branch `-fno-start-set` | `rc=0`, `RX_DFA_PREFILTER "byte-class-bounded"` |
| main `fcc021c9` (`build/pcrec`) | `rc=0`, `RX_DFA_PREFILTER "byte-class-bounded"` |

Mechanism: `S = {' ', a}`. The two live seeds are `u` (non-word context:
the lookbehind fails, no thread) and `w` (word context: the thread
` *a` is live). `u·' ' = u` (a space keeps the non-word context and starts
nothing there); `w·' ' = w` (the thread stays in ` *`, which has exactly
`w`'s future, and the context it leaves is irrelevant to it). `s0 = u`.
So `' ' ∈ S \ E*`, `T = {a}`, and `T = {a}` is a proper subset of `E` (the
word bytes, which move `s0` to `w`) — F admits, then the assertion fires.

The assertion is LOAD-BEARING, not decorative: had it been a silent
`T = S ∩ E*` the artifact would MISCOMPILE. MEASURED with a hand-twin
(the `-fno-start-set` artifact, `-p ry`, its `can_begin_match` skip line
replaced by the hat's exact text with `T = {a}`:
`skip_from`; `while (pos+1<n && s[pos] != 'a') pos++;`; the conditional
re-seed through `ry_forward_seed_state`), driver `/tmp/sscrit/tdrv.c`:
`"x a"` sp=0 deny 1(1,3), twin **0**; `"x  a"` sp=0 deny 1(1,4), twin
**0**; every other (subject, sp) of 21 agrees. libpcre2 10.48:
`(?<=\w) *a` on `x a` → ` a` at (1,3), = deny. Hand-derived: subject `"x a"`,
startpos 0. From `s0`, the skip passes `x` (∉ T) and ` ` (∉ T), lands at 2
and re-seeds `seed[class(' ')] = u`; from `u`, `a` cannot satisfy
`(?<=\w)` (left byte is a space) — no match. The true answer is (1,3)
(`(?<=\w)` holds at 1 after `x`). The induction in §6.4.3 item 2 is exact
only for skipped bytes `∉ S`, and `' '` is in `S`.

Both consequences:
1. A shipped regression: patterns main compiles now refuse with an
   internal error (D26/charter: a construct pcrec implements must never
   produce an internal error). The lane's sweep saw 0 assertion fires over
   3,528 corpus artifacts — the corpus does not contain this shape; the
   population that would reach it (a seeded machine whose `S` holds a byte
   that a seeded thread LOOPS on without changing what the context means to
   it, e.g. a `*`-loop over non-word bytes after a word lookbehind) is not
   in any fixture.
2. The repair is cheap and sound either way: `T = S` (no intersection) is
   sound on EVERY seeded machine by §6.4.3 item 2's own corrected argument
   (`T ⊇ S` is the whole requirement); or turn the assertion into a
   DECLINE. Addendum 1's equivalence claim "(a) `S ∩ E*` ≡ (b) `S` on every
   seeded machine, 0 diffs over 13.58M cells" (r4 sound-F1 resolution) is
   refuted as a universal claim by this witness — it was a population
   measurement, and the population never contained a `b ∈ S \ E*`.

Found by a 3,000-pattern compile-only fuzz (`/tmp/sscrit/fz.py`, random
seeded patterns over `\b \B (?<=…) (?<!…)` + small loops), 1 hit, then
minimized by hand. A second 6,000-pattern run (flags drawn from none,
`-i`, `--no-captures`, `-fprefilter-collapse`, `-e utf8`, `--ucp`) hit 3
more: `(?<!\W) *-` (`-fprefilter-collapse`),
`(?<![a-])(?<!\W)[ab]*?(?:ab|b)+` (`--ucp`), and `(?<=[ab])\W*?b` (no
flags), which drops **193** bytes of `S` (`-fno-start-set`: rc 0,
`byte-class-bounded`).

**The refusal is on EVERY route that reaches the hat**, so nothing absorbs
it: `(?<=\w) *a` refuses identically under `--no-captures`, `-i`,
`-e utf8`, `--tune=min-size`, `--emit-facts`, and as a VM HYBRID's
prefilter (`(?<=\w) *(a)`, `(?<=\w) *(?>a)b`, `--engine=vm -fprefilter`,
`(?<=\w) *a{1,3}x -fprefilter-collapse`). Only a route with no DFA scan
(`(?<=\w) *(a)\1`, VM without prefilter) compiles.

**Recommended repair: `T = S`, and drop the intersection.** Where
`S ∩ E* = S` the intersection is the identity; where it is not, admitting
it is unsound (above). So it never narrows soundly, and `E*` has no role
left except as an optional check. With `T = S` the existing `T ⊆ E` /
proper-subset admission DECLINES F1's witness (`' ' ∉ E`), giving
exactly the deny artifact. That is the decline the "contradiction" was
standing in for. Whichever repair is chosen, the witnesses above belong in
`dfahat.rxt` (compile + answers), and §4.1a's / D148 addendum 1's sentence
"`E*` is all 256 on every seeded machine" needs to be struck.

### F2 — NOTE: the "E* without s0 is equivalent" finding is TRUE, but its stated reason cites a guard that does not cover it

Report §6 item 1 says `s0` IS `s1u[UPC_PLAIN]` "on every `ENG_UNANCH`
machine (`start_pinned_assert_routing` asserts it)". That assertion is
called from one place only: the `pinned` branch of the unanchored emitter
(`emit_dfa.c:8831`, `else start_pinned_assert_routing(...)`). A non-pinned
`ENG_UNANCH` artifact, which includes every hat mover I looked at, never
runs it.

The identity still holds, for a different reason. `s0` and
`s1u[UPC_PLAIN]` are closed with the same atom 0, and they differ only in
the start-of-subject and `\G` bits (`dfa.c:1657-1660`). Every pattern I
built that reads those bits routes to the ATTEMPT scan, not
`ENG_UNANCH`:
`^a|\bb`, `(?:^|-)\b(?:a|b)`, `\Ab|\bc`, `(?:\b|^)(?:ab|c)`,
`(?:^|\b)x(?:a|b)`, `(?:\A|\bq)(?:a|b)`, `(?m)^a|\bb`, `\Ga|\bb` all give
`RX_DFA_SCAN "attempt"`.

I also tried the lookbehind spellings of start-of-subject:
- `(?<!.)a|\bc` reaches the hat. Its seed table is `{5, 0, 10, 10, 10}`,
  `s0 = 0 = seed[\n]`.
- `(?<![\s\S])a|\bc` has seed table `{4, 8, 8, 8}`, so no byte selects
  `s0`. But `s0 == s1u[0]`, because atom 0 means "in no context set",
  which is what the absent side reads.

Both agree with deny and libpcre2 (below), and `dfa_estar` keeps the `s0`
term anyway, so nothing is exposed. The fix is to the citation only: the
identity rests on ENGINE ROUTING (BOL and `\G` force the attempt scan), not
on an assertion. If `ENG_UNANCH` ever admits `^`, the mutant stops being
equivalent, and no guard would say so. That is the "equivalent on a
population that cannot distinguish it" shape the brief asks about.

### F3 — NOTE: the two build assertions cannot be compiled out, and both are reachable or argued

- Both are `pcrec_ctx_fail` calls. That function is `noreturn` and
  longjmps to the driver, so they are not `assert()` and `NDEBUG` cannot
  remove them.
- `T == S` is REACHABLE (F1), and every route surfaces it.
- The size-term ladder's blanket catch (`compile.c` `ST_LADDER`: "a LADDER
  attempt's failure — for ANY reason — means this K is out") does absorb it
  on a VM hybrid's TRIAL attempts. The FINAL attempt re-derives the same
  hat and refuses, so the user still sees it (measured: every hybrid
  variant above refuses).
- The only `pcrec_ctx_fail` sink that converts a failure into success is
  `--emit-facts`' force loop (`pf.forcing`). It does not reach
  `pf_dfa_start_set`: the measured `--emit-facts` run refuses.
- `seeded ⇒ views` is unreachable by construction:
  `views = viewsel || wctx`, and a seed split needs a class context. So it
  can never be exercised (S-row UNREACHED is the right expectation), but
  nothing disables it.
- Silent-disable risk is low. The realistic one is a future edit that
  turns the `nt != ns` contradiction into an early `return false` placed
  BEFORE the admission tests. That would be harmless for soundness (a
  decline) and is in fact the F1 fix.

## Probed and held (both sides of every cell; A = branch default, B = `-fno-start-set`, C = libpcre2 10.48)

The every-startpos differential (A vs B on return + all spans, A vs C on
all ovector pairs; utf8 rows compare C only at character starts), 0
disagreements on every row below:

- **Hat witnesses and the lane's own**: `\b(?:true|false|null)\b`,
  `(?:\b|xy)a` (incl. `xya`), `\B(a|b){1,3}` (incl. `xa`), `\b(?:ab|cd)$`,
  `\Bx`, `\b(?:x|yy)`, `-i \b(?:true|null)`, `--ucp \b(?:x|y)`,
  `(?m)\bx$`, `\b(?:a|b)\z`.
- **Count-collapse relatives (brief item 2), `-fprefilter-collapse`, VM
  hybrid unless noted**: `\B(a|b){1,3}`, `\B(a|b){2,4}?`, `\B(a|b){2}`,
  `\B(?:ab|c){1,3}` (dfa), `\b(a|bb){1,3}\b`, `\B(a|bc){2,3}d`,
  `\B(?:a|b){0,2}c` (dfa), `(?:\B|-)(a|b){2,3}`, `\b(a|b){1,3}?x`. Under
  `-e utf8`: `\B(a|é){1,3}` (first-class-bounded),
  `\B(é|ü){1,3}` (first-memchr-bounded on a multibyte lead),
  `\b(é|a){2,3}\b`. The conditional re-seed held in both directions on all
  of them, with subjects up to 7-8 bytes over the pattern alphabet at every
  startpos.
- **Re-entered-start and in-flight shapes**: `(?:\b|yz)(?:a|yb)`,
  `(?:\B|-)(?:a|b)c`, `(?:a|\bb)+c`, `(?:\bq|x)(?:y|q)`, `(?:\Bab|\bba)`,
  `(?:\B|a)b`, `(?:a|)\bb`, `a?\bb`, `(?:aa)?\bb`, `(?:xa*)?\Bb`,
  `\b(?:a|b)\b|\B-`, `\b(?:aa|a)` (memchr), `\b[ab]+`, `\B[ab]+`.
- **Lookaround seeds**: `(?<=a)\bb|\bc`, `(?<![a-z])b`, `(?<!\w)(?:a|b)`,
  `(?<!.)a|\bc`, `\b(?:a|b)(?<=b)`, `\b(?:a|b)(?=c)`, and as hybrids
  `\b(?=ab)(?:a|c)`, `\b(?!ab)(?:a|c)`, `(?<=a-)\b(?:c|d)`,
  `\b(a)?b|\Bc`, `\b(a)|\B(b)` (captures compared), `\b(?>a|ab)c`.
- **utf8** (pcrec `-e utf8` = ASCII `\b`/`\w`; oracle `PCRE2_UTF`):
  `\b(?:x|y)`, `\B(?:x|y)`, `\b(?:x|y)\b`, `\B(?:é|ü)`, `\B[^a]`,
  `\B\p{Ll}`, `-i \B(?:ſ|k)`, `\b(?:x|y)$`, `(?m)\B(?:x|y)$`,
  `\B(?:é|y)\B`. The hybrids (utf8 lookbehinds route to the VM):
  `(?<=[^é])\b(?:x|y)`, `(?<=[^a])\b(?:x|y)`, `(?<=.)\B(?:x|y)`,
  `(?<=[^\x{100}])\b(?:x|yy)`. The same utf8 rows also ran on RAW-BYTE
  subjects (ill-formed: stray `\x80 \xa9 \xc3 \xff`), A vs B only, 1,500
  subjects each: 0 disagreements.
- **Byte/Latin-1**: `--ucp \b(?:x|\xe9)`, `-i --ucp \b(?:\xe9|a)`,
  `-i \b(?:k|s)`, `\B\s`, `\b\d`.
- **Random population**: 400 generated seeded patterns
  (`/tmp/sscrit/gen.py 7 400`, flags none / `-i` / `-e utf8` / `--ucp` /
  `-fprefilter-collapse` / `--no-captures`, subjects to 12 bytes, 250
  random per pattern, every startpos). 85 of the 400 reached the hat (53
  `first-class-bounded`, 32 `first-memchr-bounded`), with 0 disagreements
  anywhere and 0 compile failures. That generator happened not to build
  F1's shape (a seeded `*`-loop over an `S` byte that keeps every seed).
  The compile-only fuzz did build it, and the refused patterns never reach
  any differential, which is why an answer sweep can never see F1.

**The induction itself held** wherever the hat was admitted. I re-derived
§6.4.3 item 2 independently. The guard compares the state to `s0`, and
`s0`'s future is the fresh start's, whatever in-flight threads re-entered
it. A skipped `b ∉ S` leaves every in-flight and fresh thread unable to
accept, so the state after it is `seed[class(b)]`. Induct over the run.
The conditional is exact both ways: no move means no consumed byte, so the
loop's own `s0` is right; a move means the induction applies. I could not
construct a cell where `if (scan_position > skip_from)` is wrong in either
direction. Every failure I found is the admission letting a `b ∈ S` out of
`T` (F1), which the assertion catches as a refusal.

**`_in` entries**: structural, not run. `rx_search_in` and `rx_search`
both call one `rx_search_run`, which calls one `rx_prefilter` body
(`h.c` for `\B(a|b){1,3}`), so the caller-buffer entries carry the same
hat text.

**Not covered**: `\G` and `(?m)^` with a seed. Every such pattern I built
routes to the attempt scan (F2), so the hat's `ENG_UNANCH` conjunct
excludes them and there was nothing to differ. `\C`, `\X` and `\R` are
refused by this build ("not implemented yet").

STATUS: COMPLETE.
