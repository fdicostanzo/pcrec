# Lane `k50bnd` — [K50-BNDSTART]: candidate match starts are character boundaries

Branch `lane/k50bnd`, worktree `worktrees/k50bnd`, 2026-09-06. Charter: plan
row `[K50-BNDSTART]`; defect: `docs/dev/known_issues.md` K50.

---

## 0. The headline, and the two things the charter did not know

**K50 is fixed on all three mechanisms, and the caller-startpos guard ships
default-on with its deny arm.** `\B` over `61 CE B1` from `startpos 0` answers
`(3,3)` on both engines, which is libpcre2 10.46's answer under both UTF
option words; it answered `(2,2)` — precisely libpcre2's `options=0` BYTE
answer — before.

Two things came out of the work that the charter could not have contained:

**(1) SITE (2) WAS A LIVE WRONG ANSWER, not a wasted attempt.** K50's site
list names `ENG_ATTEMPT`'s `start++` loop as *"the loop `utf8_design.md` §5.5
and ASK 5 are about"* and files no witness for it, because §5.5 asserts such
starts cannot produce a wrong answer and Frank's ASK 5 ruling was given that
claim. Measured on the shipped tree:

| | |
|---|---|
| pattern | `(?m)^a\|\B` (`--features assertions,modifiers`) |
| subject | `61 CE B1`, `startpos = 1` — a **real character boundary** |
| pcrec `-e utf8` before | `(2,2)` — mid-character |
| libpcre2 10.46 `PCRE2_UTF` | `(3,3)` |

The witness needs two branches and neither is optional: the BOT-family branch
routes the pattern to `ENG_ATTEMPT`, and the nullable second branch keeps an
interior start state live so `start_max` is the subject length. **A pure
`(?m)^` or `\G` pattern is self-gating** — `(?m)^` can hold only after a
newline and a newline is a character-start byte; `\G` gives one attempt at the
caller's own position — which is why the site stood unwitnessed for a whole
milestone. A fix closing only mechanism (1) would have left it standing.

**(2) MY OWN GUARD WAS WRONG ABOUT OFFSET 0, and `make test-axes` found it.**
See §6. It is the finding I would most want a reviewer to check.

---

## 1. What changed

### The engine half (no flag — this is the correctness fix)

One new datum on `PcrecEnc`, asked as a predicate rather than as a step:
`start_cls` (the bytes a character may start at, as a 32-byte class) and its
expression twin `start_guard`. **Both NULL under `byte`**, which is what makes
"the encoding with no defect pays nothing" a construction rather than a
comparison.

| site | mechanism | change |
|---|---|---|
| 1 | `src/ir/nfa.c` `nfa_wrap_unanchored` | **TWO split states.** `nfa->start` stays the ungated split (the caller's own position); the self-loop returns to a second split whose pattern branch is gated by a new `N_CSTART` node |
| 2 | `src/gen/emit_dfa.c` `ENG_ATTEMPT`'s start loop | `if (start > search_from && !(guard)) continue;` |
| 3 | `src/gen/emit_vm.c` hybrid handoff | **no change needed, and the entry's own reasoning is why** — a fix for (1) closes (3), because the prefilter IS a DFA emitted through `pcrec_emit_dfa_engine` and therefore carries the gate |

**Why two splits.** The engine owns the positions it INVENTS; the caller owns
the one it supplied. That split of responsibility is Frank's ruling, and it
buys something concrete: **one machine serves both arms of the deny axis**, so
the flag moves only the emitted entry guard and never the automaton. A gate on
the first split too would make the deny arm answer no-match where
`utf8_design.md` §2.6.1.1 rules `(1,1)` — the axis would have become a second
automaton rather than a guard.

**Why a `continue` at site 2 rather than K49's `advance` text.** Taking the
step means replacing a `for` header's increment with a trailing statement,
which moves every byte artifact — an abi event for the encoding that has no
bug. A guard is additive.

`N_CSTART` is `N_EOL_M`'s shape (one `end_ok` read, one class-axis read, no
direction), and the class axis gains a fourth partition value, `UPC_NOSTART`.
**Its partition precondition is CHECKED, not assumed** — a non-start byte that
were also a word byte would classify `UPC_WORD`, read as a character start to
the gate, and re-open K50 silently. `pcrec_enc_start_cls_ok()` refuses such a
backend by name.

### The caller half (the `-fno-startpos-guard` axis)

`PCREC_ERR_STARTPOS = (-7)`, below `PCREC_ERR_FLOOR`: a refusal of the CALL,
not a give-up — nothing was attempted and no budget was spent.

**The spelling you suggested was the deleted one.** `RX_ERR_STARTPOS` is the
per-artifact `<PREFIX>_ERR_*` form D60/[ABI-NS] deleted (not aliased) on
2026-08-18; `match_api.md` §4 makes these a pcrec-CONTRACT fact in the shared
unprefixed block.

`PCREC_NO_STARTPOS_GUARD` is bit 25. **It is the first member of that enum
that changes an answer**, and everything odd about it follows: it is NOT
masked out of `rx_info.flags` (a caller must be able to read which contract an
artifact carries), and `make test-axes` carries it as a documented divergence
class rather than an identity claim.

One emitter, four call sites (`pcrec_emit_startpos_guard`): `emit_search_head`
gated on `fit.chosen == ENGM_DFA` — the same discriminator the dead-group fill
uses, so the VM hybrid's internal prefilter is not guarded — and the VM's three
`_run` statics, **which is the one point every rung of the [CC-DIFF] STEP 2
entry ladder passes through in both delegation directions** (`plain`/`shared`
run `_in` → un-suffixed; `forward`/`inline` run the other way). Guarding there
makes the six public entries agree by construction rather than by six copies.

**Ordering against `startpos > n` is unforced, and that is a property of the
backend's text rather than of the placement.** `match_api.md` §3.1 promises
`0` there (libpcre2 answers `BADOFFSET`; pcrec does not follow), and the utf8
guard opens `@P >= @N`, so every position the range test owns passes untouched.

---

## 2. The 10.46 measurement, and what it decided

`docs/design/utf8_measurements/out/startbnd.txt`, written by
`probes/probe_startbnd.py` through the lane's own archiver — remote run,
header stamps `libpcre2 10.46 2025-08-27`, `selfcheck clean`, source SHAs for
the bytes that answered.

The charter says to measure BADUTFOFFSET before pinning any compat claim. The
question I asked was sharper than "what does it do", because an O(1) entry
guard can only reproduce a property of the OFFSET: **is the refusal uniform,
or pattern-dependent?**

**Uniform.** 10 patterns × 2 mid-character offsets = **20/20 `ERRM -36`**, and
the same 10 patterns at the three boundary offsets = **30/30 answer normally**.
Vacuity guarded in both directions. That is what licenses the shape.

Two further rows the transcript settles:

- `startoffset > n` under `PCRE2_UTF` is `ERRM -33 (BADOFFSET)` where pcrec
  promises `0`. **A deliberate, recorded divergence**, now stated in
  `match_api.md` §3.1 rather than left for someone to discover.
- §3's ill-formed rows record where pcrec's ruled semantics legitimately part
  company with `MATCH_INVALID_UTF` (`\B` on `61 FF B1` from offset 0: pcrec
  finds `(3,3)`, `MATCH_INVALID_UTF` reports no match, its barrier rule). Not
  chased — §2.6/ASK 1 rules pcrec's answer is the automaton's — but recorded.

**Result, default arm vs 10.46 `PCRE2_UTF` on §2.6.1.1's table, cell for cell:**

| pattern | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| `(?<!.)` pcrec | `(0,0)` | REFUSED | no-match | REFUSED | no-match |
| `(?<!.)` 10.46 | `(0,0)` | `ERRM -36` | no-match | `ERRM -36` | no-match |
| `(?!.)` pcrec | `(4,4)` | REFUSED | `(4,4)` | REFUSED | `(4,4)` |
| `(?!.)` 10.46 | `(4,4)` | `ERRM -36` | `(4,4)` | `ERRM -36` | `(4,4)` |

Identical modulo the code number, which D26 makes the wrong tier.

---

## 3. The abi ritual (D76/D94)

`abi` **23 → 24**. Readers found BY GREP over the current number, all updated:

```
src/gen/emit_dfa.c:1801        .abi = 23           -> 24  (the stamp)
src/gen/emit_dfa.c:1775        the abi comment block      (per-artifact-kind breakdown)
tests/codegen/run_codegen_tests.sh:2761  ABI_EXPECT=23 -> 24  (+ its message)
tests/codegen/run_recursion_identity.sh  FILEPIN            (B) re-pinned
docs/spec/match_api.md:159     "rx_info.abi is 23"  -> 24
docs/spec/match_api.md:1816    "rx_info.abi is 24 on every artifact today"
```

`tests/registry/run_registry_tests.sh:345` mentions abi 23 as *provenance for
a row-count pin*, not as a reader of the number — left alone deliberately.

**(B) is pinned to `9e276472`**, this lane's last `src` commit, per the
lane-pins-its-own/manager-re-pins-at-merge precedent. **You will need to
re-pin it to the merge commit.**

**What moves:** every artifact of both engines gains TWO lines — the
`PCREC_ERR_STARTPOS` define in the shared ABI block and a
`<PREFIX>_STARTPOS_GUARD` selection stamp in the shared prologue. **No `byte`
artifact's PROGRAM moves.** A `utf8` unanchored DFA artifact's MACHINE moves
(the gate is a real automaton state) — only the second bump in that file's
history to move a machine.

**It is the first bump in that list carried by a change that moves an ANSWER**,
so unlike every deny flag before it `-fno-startpos-guard` does not sweep this
to identity and is not meant to.

---

## 4. Validation

| instrument | result |
|---|---|
| identity gate, 4 axes | see §8 (run in the delivery block) |
| `make test-codegen` | see §8 |
| `make test-encoding-checks` | see §8 |
| `make test-startbnd` (new) | 6/6 sections |
| `bash tests/harness/run.sh tests/utf8` | 1342 cases, 0 failures |
| known-fail ratchet | fired `NOW PASSING` on K50's cell, then the cell moved live |
| `tests/rxtsource` | 106 pass / 14 fail, **byte-identical failure set to the branch point** (measured against a build of `1c4c91b4`) — the 14 are the darwin `xargs -a` and padded-`wc` issues that file's own comments already document |
| `python3 tests/harness/verify_rxt.py tests/utf8` | 388 pass / 0 fail / 100% |

### The differential — `tests/utf8/run_startbnd_diff.sh`

The shape is possessify's and **the claim is the opposite one**. Every other
`-fno-` differential checks that two arms AGREE; this axis is the only
non-answer-identical one in `tuning.md`, so agreement everywhere would mean the
flag does nothing. What is checked is WHERE they differ.

Six sections: §1/§2 the arms identical at every boundary and differing ONLY by
the typed refusal at mid-character positions (**340 agreeing, 150 refused, 0
otherwise**, 10 witnesses × 11 subjects); §3 the non-vacuity floor; §4 the byte
encoding paying nothing; §5 the cross-engine cells; §6 §2.6.1.1's ruled
permissive table pinned on the deny arm.

**The floor is DERIVED, not transcribed from a run** — 10 patterns × 14
continuation-byte positions across the subject list, with the per-subject
arithmetic written out at the check, so a reader can tell a shrinking
population from a re-baselined number.

**§5's cells are pinned to libpcre2 10.46 rather than to the other engine**,
and that is the section's whole value: for a milestone BOTH ENGINES ANSWERED
THE SAME WRONG THING, so nothing comparing pcrec against itself could have
caught K50.

### The manager's landing conditions (2026-09-06)

| condition | where it landed |
|---|---|
| site (2) as both-arm cells | `axis11`'s `(?m)^a\|\B` cells (default) + `run_startbnd_diff.sh` §5, which now runs **every** engine cell under BOTH flag settings. There is no divergence for a `.rxt` pair to carry — `startpos = 1` is a real boundary, so both arms must answer `(3,3)` — and that SAMENESS is the claim: the axis moves no position the engine invented |
| K50 gains the second face | `known_issues.md`: "**K50 HAS A SECOND FACE**", with the measurement, where each face is pinned, and the note that S234/S235 fire disjoint cells |
| §5.5 says the claim UNDERSTATED it | done, and the annotation now also says the BOX understated it — written after K49, it refuted §5.5's reason while leaving `ENG_ATTEMPT` looking theoretical |
| self-gating kept in the entry | kept: `(?m)^` can hold only after a newline, `\G` gives one attempt at the caller's position — this is the "why did nothing catch it" and the blast-radius scope |
| below-floor/composed-trap in the spec | `match_api.md` §4, stated as a contract statement with no live trap today |
| **guard ordering PINNED** | **new §5b**: `startpos = n` answers, `n+1` and `n+7` return `0` and not `-7`. It cannot fail today for a reason stronger than placement (the guard opens `@P == 0 \|\| @P >= @N`) — which is exactly why it needs a pin, since that is a property of the BACKEND'S TEXT |
| **byte-tautology as a structural claim** | **new §7 + `startbnd_backend_check.c`**: reads the backend ROWS, because every other statement of "byte pays nothing" is derived from those two pointers. Five assertions; the sharpest is that `start_cls` and `start_guard` agree **per backend** — the IR reads one and the emitters read the other, so supplying one without the other builds a machine whose gate no entry guard matches, which is a wrong answer on no subject a corpus would think to try |
| refutations recorded for the panel | `utf8_design.md` §5.5's box now carries both dead placements with their refutations |

### Sabotage validation — ten directions, all detected

| direction | caught by |
|---|---|
| guard deleted (backend supplies no `start_guard`) | §1's per-pattern "DEFAULT arm emitted NO guard" |
| over-firing at end-of-subject | classification defect (after the driver fix, §6) |
| over-firing on lead bytes | classification defect |
| leaking into the deny arm | the artifact TEXT check, before anything runs |
| leaking into byte artifacts | §4, **three independent ways** (mask, emitter, stamp) |
| IR gate deleted (K50's own defect) | §5's DFA cells — matrix: 8 `startbnd` checks + 4 corpus cells |
| `ENG_ATTEMPT`'s continue deleted | §5's `attempt-startloop` cell **alone** — matrix: 2 + 1 |
| the guard loses its end-of-subject clause | §5b, exactly (`startpos=4 answered rc=-7, want (4,4)`) |
| `byte` declares both backend pointers | §7 and §4 |
| the deny flag reaches the ENGINE's gate | §5's both-arm, naming each cell |

The last two firing DISJOINT cells is the matrix telling two mechanisms apart
rather than scoring one twice. Permanent rows: **S234** (IR gate), **S235**
(`ENG_ATTEMPT`), **S232** (deny-arm leak), **S233** (byte leak), each with
`SAB_REACH` from birth, plus the `startbnd` matrix arm registered before the
rows that name it (R31 C11).

**ALL FOUR ROWS RAN THROUGH THE REAL MATRIX at the merged tree** —
`reach:ok(1/1)`, DETECTED, with 0 unexpected / 0 undetected / 0 unreached /
0 anomalies on each.

**AND THE MATRIX CAUGHT A DEFECT IN MY OWN ROWS ON ITS FIRST RUN, which is the
part worth reading.** All four `SAB_REACH` probes were written as
`... -o probe.c "PAT" && grep -c "NEEDLE" probe.c` — and `grep -c` prints a
COUNT, not the needle, so `SAB_REACH_EXPECT` could never match. Every one of
them would have scored **UNREACHED** forever: not a false green (the matrix
fails loudly on it, which is exactly what `[MECH-REACH]` was built for), but
four rows certifying nothing. Rewritten to the house idiom (`-o -` piped
through `grep -o … | head -1`) and re-run. **I had validated these four
directions by hand before writing the rows, so the sabotages were real — what
was broken was the rows' own reachability probe**, and only running them
through the matrix could show it.

**S234/S235 were S230/S231 until the merge.** Lane `encchk` landed its own
`S230`/`S231` (the `cwmax` pair, arm `mrl`) the same morning; the FILENAMES do
not collide but the `SAB_ID`s do, and an id is what the matrix reports under.
Renumbered here rather than there because encchk merged first.

---

## 5. The §5.5 throughput side-note — REFUTED, and it was worth measuring

The charter asks for §5.5's wasted-attempt claim to be re-measured "as the
fix's own throughput side-note", on the expectation that skipping mid-char
starts is *"also the OPTIMIZATION §5.5 called not optimal"*. **It is not an
optimisation.** Nine interleaved trials per cell (the box's known run-to-run
spread makes uninterleaved trials useless), gcc-16 -O2, M1, against a scratch
build of the same tree with the gate removed:

| route | witness | subject | gated vs ungated |
|---|---|---|---|
| `ENG_ATTEMPT` | `(?m)^zzz\|\bqqq` | 4,000 × 2-byte chars | **1.33× SLOWER** (10,450 vs 7,865 ns/search, no trial overlapping) |
| `ENG_ATTEMPT` | same | 4,000 × 4-byte chars | wash (15,468 vs 15,538 ns, 0.4%) |
| `ENG_UNANCH` | `\Bqqq` | 4,000 × 2-byte chars | wash (194.6 vs 195.6 ns, inside the spread) |

**The mechanism is a branch, not the skipped work.** The guard runs on EVERY
iteration and skips work on only some, and the work it skips is one seed
dispatch that dies immediately. On a 2-byte-character subject the guard's
branch alternates taken/not-taken every iteration — the worst case for a
predictor; on 4-byte it is taken 3 times in 4, more predictable and skipping
more, and the effects cancel. The DFA route pays nothing in TIME and pays in
SIZE: `\Bqqq`'s forward transition table grows 15 → 20 entries.

This changes nothing about the fix, which is a correctness fix paid for
whatever it costs. It changes the sentence, and §5.5's box now carries the
table so nobody cites it the other way.

---

## 6. THE FINDING I MOST WANT REVIEWED: the guard refused offset 0

Wiring the axis into `make test-axes` (charter (iii)) turned 21 oracle-verified
cells red across `tests/utf8/axis01`, `axis03` and `axis09` — `a` on the
one-byte subject `\x80` among them.

**The cause is a real asymmetry between pcrec and libpcre2, not a typo.** The
boundary predicate is LOCAL ("is this byte a continuation byte"), which is
exactly what libpcre2 asks under `PCRE2_UTF` — but libpcre2 asks it only AFTER
a whole-subject validation pass has already rejected an ill-formed subject
(§2.6(b)). **pcrec has no such pass**: ASK 1 rules that an ill-formed sequence
matches nothing, "no validation pass, no error return". So this guard sees
subjects libpcre2's never reaches, and on one that BEGINS with a continuation
byte the local test alone refuses offset 0 — turning "ill-formed input matches
nothing" into "ill-formed input is an error", which is that ruling inverted.

The guard gains `@P == 0 ||`. A caller naming offset 0 cannot have pointed
INSIDE a character, because none precedes it.

**MY OWN DIFFERENTIAL COULD NOT SEE IT**, and that is the second half of the
finding: none of its 9 subjects began with a continuation byte, so the guard's
treatment of offset 0 was unexercised. Two subjects added (`B161`, `8080`), the
driver's contract predicate gained the same clause — **it states the CONTRACT,
not what the backend implements**, which is the whole reason it is recomputed
there — and the floor moved 140 → 150. Re-validated: deleting the clause now
reds the sweep.

A second instrument defect surfaced the same way. **With a zero byte at
`s[n]`, the driver could not see a guard that reads past the end of the
subject** — a guard spelled without its end-of-subject arm read 4/4 GREEN.
The driver now parks `0x80` there.

**AND IT RECURRED IN THE SECOND DRIVER, which is why I am reporting it as a
pattern rather than as two bugs.** Validating the new §5b — the check written
FOR the ordering defect — found it PASSING while only §1/§2 went red, for the
identical reason: `startbnd_engine_driver.c` had no byte at `s[n]` either, so
a guard reading there decided on a zero and accepted. Both drivers park `0x80`
now. The general shape is a check whose claim is about CONTENT resting on an
accident of an uninitialised buffer, and it is the same family as
`run_offset_skip.sh` §4's `tail -n +8` (§10(d)).

---

## 7. Open questions for the manager

**(a) TWO `.rxt` FORMAT DECISIONS, which are yours under dd13b, not a lane's.**
Charter (i) asks for both-arm CELLS riding the `gu <code>` family. Neither half
is expressible today:

- `gu <code>` searches from **offset 0 only**, and offset 0 is always a
  boundary — so a refusal cell has no directive at all. It needs either a
  startpos-bearing give-up kind (`gus <P> <code> "<subject>"`) or a `<P>` on
  `gu`.
- **No directive spells a compile flag.** `flags` defines only `i`.

I did not invent either. The two affected cells (`axis09`'s
`midstart-row2`/`row4`) are PINNED in `run_startbnd_diff.sh` §6 with their
ruled values, and `axis09` carries a pointer at each block saying why it left
and what would bring it back. **If you rule the directives in, the blocks come
back and §6 becomes redundant** — that is the intended shape, not a permanent
arrangement.

**(b) `PCREC_ERR_STARTPOS = -7`, below the floor.** The consequence worth your
eye: §4's "composed call sites must trap below the floor" makes a composed site
trap on it. I think that is right — after this fix every engine-generated
position IS a boundary, so a composed callee seeing a non-boundary means the
engine broke its own rule — and no composed call sites are emitted today, so it
is a contract statement rather than a live trap. Overrule if you disagree.

**(c) THE `rx_info.flags` MASK IS NOW PER-ARTIFACT for this one bit.**
`PCREC_NO_STARTPOS_GUARD` joins `strategy_denials` **only where the encoding
restricts no position**. That is the mask's own rule (observable effect) applied
per artifact rather than a new rule — but it is the first conditional member,
and it is what makes the differential's §4 claim the strong one (a byte
artifact is BYTE-IDENTICAL under either setting, not merely guard-free).

**(d) TWO CHECKS IN THE TREE WERE PINNED TO THINGS THAT MOVE, and both cost
me a red before I understood them.** Recorded as a pattern rather than as two
incidents: `run_offset_skip.sh` §4 pinned a PREAMBLE LENGTH (`tail -n +8`),
and my own differential's first driver pinned a BUFFER'S CONTENT (a zero byte
at `s[n]`, which made a guard that reads past the end of the subject read
green). Both are the same shape — a check whose claim is about CONTENT
expressed as a position or an accident — and the tree has a name for the
family already (docs/dev/learnings.md §3). Worth a row in that file if you
agree; I did not add one, because a lane adding to the digest on the strength
of its own two instances is how a digest gets noisy.

**(e) The full battery is yours.** I ran the targeted suites named in §4 and
§8. `make test`, `make mech` (the four new rows have never run through the real
matrix, only as hand-planted edits), `make test-axes` in full, and the Linux
arm are all unrun here.

**(f) `make test-axes`: CHARTER ITEM (iii) IS DISCHARGED, AND THE ANSWER IS
THAT NO DIVERGENCE CLASS IS NEEDED.** I reported this as owed before measuring
it; measured, it is not.

- The roster derivation picks bit 25 up with no edit (22 bits, matching
  `tuning.md` §2's 22 documented `(bit N)` mentions — the sweep cross-checks
  those two lists and fails if they disagree).
- **`tests/utf8/` is the ONLY directory in the tree with `encoding utf8`
  blocks** (measured by grep; the one other hit is a `.rxtin` fixture, not part
  of a corpus run). Everywhere else compiles under `byte`, where the flag is
  inert AND masked out of `rx_info.flags`, so the two builds are
  byte-identical — which the identity gate independently proves at
  `differing=0`.
- **Scoped to that directory the sweep is CLEAN**: 1,130 cases, `agree=1130`,
  `gained=0`, `mismatches=0`, `refused=0`.

So the population that could diverge is exactly `tests/utf8/`, and within it
nothing does: every corpus cell starts at offset 0 or at a boundary, where the
guard is transparent. That is the charter's own prediction ("corpus BLIND to
the axis by construction") holding, not a gap.

**The distinction that makes this honest** — and it is now stated in
`tuning.md` §2.23 rather than left implicit: an empty divergence population in
the DIFFERENTIAL means a dead guard and is a RED check (§3's floor is 150); an
empty one in the corpus sweep means the corpus cannot see the axis, which was
known before the guard was built. The axis is watched by the instrument that
can see it and swept for identity by the one that cannot.

**Still yours:** the FULL-corpus `make test-axes` run. My scoped run covers the
whole population that can reach the axis, and the remaining ~2,900 patterns are
byte-compiled and provably identical — but "provably" is my argument and the
full sweep is the measurement.

---

## 8. Delivery-block results

Run with the tree settled and nothing else touching `build/` — the sequencing
matters, and I got it wrong twice earlier in the lane before running this
block cleanly (see §10).

**THE IDENTITY GATE: 16/16, all four axes, ZERO DIFFERING on both
comparisons.** This is acceptance condition (d) discharged, and (A) is the one
that carries it:

| axis | (A) program region vs the UNCHANGED pre-module pin `ac4917d` | (B) whole file vs `9e276472` |
|---|---|---|
| default | 2300 identical, **differing=0** | 2424 identical, differing=0 |
| `--engine=vm` | 2279 identical, **differing=0** | 2425 identical, differing=0 |
| `-fno-prefilter` | 2301 identical, **differing=0** | 2424 identical, differing=0 |
| `--no-captures` | 2324 identical, **differing=0** | 2424 identical, differing=0 |

The corpus this gate walks is entirely `byte`-compiled, so **(A) at
`differing=0` IS the proof that no byte artifact's program moved.** It is a
real check here rather than a formality: K50's whole risk was that a fix for a
`utf8` defect would move the encoding that has no defect, and nothing in the
change is `byte`-conditional — the backend supplies no character-start set, so
the IR builds no gate, the class axis never produces `UPC_NOSTART`,
`eqclasses` performs no fourth refinement, `ENG_ATTEMPT`'s loop gains no
`continue`, and the entries emit no guard. The (A) excuse counters
(`island-moved`, `fold-moved`, `size-term-moved`) are the pre-existing ones and
this event added none.

| suite | result |
|---|---|
| identity gate | **16 passed / 0 failed** (re-run after the landing-condition changes: 16/0 again) |
| `make test-axes` scoped to `tests/utf8` | **1130 cases, agree=1130, gained=0, mismatches=0** — see §7(f) |
| `make test-encoding-checks` | **10 / 0** — including K49's advance-agreement in both directions (10,738 cells each, utf8 differing from `pos+1` on 2,268 of them) and §8.5's byte-vs-utf8 ASCII agreement over 250 blocks |
| `make test-startbnd` (new) | **7 / 0** (§1/§2, §3, §4, §5, §5b, §6, §7) |
| known-fail ratchet | `still failing: 1` (K34 alone) `now passing: 0` — K50's file retired |
| `bash tests/harness/run.sh tests/utf8` | **1342 cases / 0 failures** |
| `make test-codegen` | **6/8 scripts, and `run_codegen_tests.sh` reads 104/4 — byte-identical to a build of the branch point.** See the triage below |
| `make strict` | clean (`-Werror -Wshadow`, whole tree) |

### `make test-codegen`, triaged against a build of the branch point

The first run read `run_group: 5/8 scripts passed`. **I did not assume the
reds were the brief's known darwin ones** — I built `1c4c91b4` in a scratch
worktree and ran the same three scripts there. That is what separated them:

| script | branch point | this lane | verdict |
|---|---|---|---|
| `run_codegen_tests.sh` | 104 pass / **4 fail** (OS-0b ×3, K24 de-sugaring) | 103 / **5** | 4 pre-existing (the brief's known darwin reds); the 5th was **MINE** and is fixed |
| `run_offset_skip.sh` | **22 / 0 GREEN** | 21 / 1 | **MINE**, and fixed |
| `run_inline_capability.sh` | `nm could not read arm_a.o` | identical | pre-existing (darwin) |

**The two that were mine, both real and both worth reading:**

**(a) `[TT-9]`: a new `run_*_diff.sh` must be in `tests/lib/san_scripts.txt`
or carry a stated exclusion.** Mine was in neither. It has the manifest's
usual reason (two artifacts per witness in one TU, compiled and run) and one
of its own: its drivers do raw byte-buffer arithmetic over deliberately
ill-formed UTF-8, **including a continuation byte parked at `s[n]`** to catch
a guard that reads past the end of the subject. That planted read is exactly
what a sanitizer axis is for, and the check it feeds would be worth little
unwatched.

**(b) `run_offset_skip.sh` §4 was pinned to a PREAMBLE LENGTH.** It compares
two artifacts built to `p1.c` and `p2.c` — each including its own header, so
that one line differs for a reason nothing to do with the flag — and it
skipped it with `tail -n +8`, the preamble's length on the day it was written.
The `<PREFIX>_STARTPOS_GUARD` stamp joins the SHARED prologue, so the
`#include` moved to line 8, stopped being skipped, and the check went red on a
pair of artifacts that are **byte-identical everywhere the flag could reach**
(verified by hand: `diff` of the two is empty).

I fixed the CHECK rather than moving the stamp, and the reasoning matters
because "edit the check until it passes" is the wrong instinct: a line count is
a pin on every stamp anyone adds later, and the check's own claim — "compare
past each artifact's own header include" — is expressible by CONTENT
(`grep -v '^#include "'`) without that coupling. The stamp belongs in the
prologue with the other selection facts. **A reviewer who disagrees should look
at this one first**; moving the stamp below the include is the alternative and
it would leave the magic number armed for the next lane.

---

## 9. Files

**Engine:** `src/gen/enc/enc.h`, `enc.c`, `enc_byte.c`, `enc_utf8.c`;
`src/core/internal.h`; `src/ir/nfa.c`, `dfa.c`; `src/opt/prefix_k.c`;
`src/gen/emit_dfa.c`, `emit_vm.c`; `lib/pcrec.h`; `cli/main.c`;
`src/parse/axes_dump.c`.

**Tests:** `tests/utf8/run_startbnd_diff.sh`, `startbnd_driver.c`,
`startbnd_engine_driver.c`, `axis11_startpos_boundary.rxt`,
`axis09_nextpos_findall.rxt`; `tests/known_fail/k50_utf8_dfa_midchar_start.rxt`
(deleted); `tests/mech/sabotages/S232..S235`;
`tests/mech/run_sabotage_matrix.sh`; `tests/rxtsource/run_rxtsource_tests.sh`;
`tests/codegen/run_recursion_identity.sh`, `run_codegen_tests.sh`; `Makefile`.

**Docs:** `docs/spec/match_api.md` (§3.1, §4, two abi sentences);
`docs/spec/tuning.md` (§1, new §2.23); `docs/design/utf8_design.md` (§5.5's
box, §2.6.1.1); `docs/dev/known_issues.md` (K50 → FIXED);
`docs/design/utf8_measurements/probes/probe_startbnd.py` +
`out/startbnd.txt`; four directory `CLAUDE.md`s.
