# lane `k49fix` — K49 fixed, and its DFA-side sibling found and filed

Branch `lane/k49fix`, worktree `worktrees/k49fix`, based at `ba7a58cb`.
Written 2026-09-05.

**Headline.** K49 is fixed: the emitted VM's unanchored retry advance is now
the ENCODING BACKEND's own step rather than a hard-coded `pos++`, so under
`-e utf8` a retry lands on the next CHARACTER BOUNDARY. Every byte-encoding
artifact is unmoved (the identity gate's whole-file comparison is 2,423/2,423
identical against its current pin on all four axes), so this is not an `abi`
event and nothing was re-pinned there. **On the way I found that the same
defect exists on the DFA side, reachable from an ordinary `startpos=0`, and
that it refutes a design assertion Frank's ASK 5 ruling was given as fact.**
That half is filed as K50 and is NOT fixed here — it is a structural change
this lane had no charter for.

---

## 1. Diagnosis

### 1.1 The site, and it is exactly where the entry suspected

`src/gen/emit_vm.c`'s `sb_printf` for the emitted `<prefix>_search_run` wrote
a literal `attempt_position++;` as the retry advance. Reproduced live at the
lane's base commit with a hand driver (`rx_search` with an explicit
`search_from`), pattern `(?<!.)` under `--features lookaround -e utf8`,
subject `CE B1 CE B2` (alpha, beta; character boundaries 0, 2, 4):

| startpos | before | after | note |
|---|---|---|---|
| 0 | `(0,0)` | `(0,0)` | boundary; axis09 row 1 |
| 1 | `(1,1)` | `(1,1)` | caller-supplied MID-character, ruled legal — unchanged |
| **2** | **`(3,3)`** | **NOMATCH** | **K49** |
| 3 | `(3,3)` | `(3,3)` | caller-supplied MID-character — unchanged |
| 4 | NOMATCH | NOMATCH | |

### 1.2 The mechanism, end to end

At `startpos=2` the assertion genuinely fails (position 2 is a real boundary
and alpha precedes it), so the search retries. `attempt_position++` moves to
3, which is inside beta's two-byte encoding. There the lookbehind's
`<prefix>_back_step` walks back to 2, reads lead byte `0xCE` declaring a
2-byte character against a run of length 1, and returns `BACK_STEP_NONE` —
that is `enc_utf8.c`'s own §5.2.1 malformed-run repair firing correctly on a
TRUNCATED leading character. The body therefore cannot run, and because the
assertion is NEGATIVE, "the body could not run" means the assertion SUCCEEDS.
An empty match is reported at 3.

Nothing here is a bug in `back_step`. Every component behaved as specified;
the defect is that position 3 was tried at all.

### 1.3 The `(?!.)`-vs-`(?<!.)` asymmetry, and it is not about lookbehind

The entry asked why `midstart-row4` — `(?!.)` at `startpos=1`, the same
subject — was green throughout. **Because it never reaches the retry.**
Position 1 is mid-alpha; `.` has no path from a continuation byte; the
negative lookahead therefore succeeds on the FIRST attempt and `(1,1)` is
reported. The advance is not executed.

So the defect was never lookbehind-specific, and the entry's framing of it as
"specific to `(?<!.)` (or lookbehind assertions generally)" is the thing the
diagnosis corrects. The real population is: **any pattern whose first attempt
fails and whose answer at the next BYTE differs from its answer at the next
BOUNDARY.** Row 3 is the only cell in that block built to fail first, which is
why it was the only one that could see it. `\B` is another member (§3).

---

## 2. The fix

### 2.1 Shape: a third kind of contribution on the encoding seam

`PcrecEnc` (`src/gen/enc/enc.h`) gains one field, `advance` — the statements
that move a failed unanchored attempt's start position to the next position
the search may try — plus `pcrec_enc_advance()` to render it.

- `byte`: `@P++;` — the emitter's old line, character for character.
- `utf8`: `@P++;` then a skip over continuation bytes, which is `next_pos`'s
  own boundary rule inline.

Three substitution tokens (`@P` position, `@S` subject, `@N` length) and a
caller-supplied base indent, so one backend text serves call sites at
different depths and different variable names. `$` is deliberately NOT one of
them: an advance names no artifact symbol.

**This is the general form, not a lookbehind special case.** No site anywhere
tests the encoding, so DD-12 (7) holds; the third-encoding recipe grows by one
line ("a backend also writes its `advance`") and stays entirely inside
`src/gen/enc/`.

### 2.2 Why it is inline text and not a call to `next_pos`

`next_pos` computes exactly this position, and calling it would have been the
obvious fix. Two independent reasons forbid it, and they agree:

1. `next_pos` carries `engine_callable = false`. DD-12 (7),
   `tests/codegen/run_codegen_tests.sh`'s `[M5-SEAM]` check (whose fixture
   table declares `next_pos:0` for every shape) and sabotage row S68 all
   forbid an engine body calling it.
2. **A call would have moved the byte artifact** — `attempt_position =
   rx_next_pos(...)` is not `attempt_position++` — turning the hard
   constraint's identity gate from a proof into a re-pin. The entry said to
   stop and report if that happened; it did not happen.

### 2.3 The cost this incurs, and the instrument that pays it

The boundary rule is now spelled TWICE per backend (`advance` and `next_pos`),
which is a drift hazard. `src/gen/enc/` already has the precedent and the
remedy: the caseless compare and `cls_casefold` are two spellings of one fold,
tied by `tests/backrefs/fold_agreement_check.c`.

So `tests/codegen/run_encoding_checks.sh` gains a **K49 advance-agreement
section**. It EXTRACTS the advance from an emitted artifact, compiles it as a
function, and compares it against that same artifact's linked `next_pos` over
an exhaustive sweep of a role-complete byte alphabet (`0x41, 0xC2, 0xE0, 0xF0,
0x80, 0xBF, 0xFF`; all subjects of length 0..4; every `pos < n`). Both sides
are read out of one artifact pcrec actually emitted, and they come from
different files of the backend.

**Non-vacuity is asserted in both directions**, because an alphabet with no
continuation byte would let this pass on a compiler that fixed nothing:
`byte` must answer `pos + 1` on every cell, and `utf8` must NOT on at least
one. An empty extraction is caught explicitly rather than passing as
"agreement over zero cells".

### 2.4 One thing the fix's own bring-up measured

The emitter's render buffer was 512 bytes and the utf8 advance needs 535 once
indented. **The overflow guard fired** — a loud internal error naming the
encoding — rather than emitting a truncated advance. The buffer is 1 KB now
and the comment records that the guard is measured rather than assumed.

---

## 3. THE FINDING: K50, and a refuted design premise

While checking whether the DFA's own "try the next start" mechanism had the
same hazard (the entry asked me to), I found that it does, and worse.

**WITNESS.** `\B` under `--features assertions -e utf8` over `"a\xce\xb1"`
(`61 CE B1`; boundaries 0, 1, 3) at **`startpos=0`** reports `(2,2)`. Byte 2
is the second byte of alpha. No mid-character `startpos` is involved anywhere
in the call — this is an ordinary unanchored search from the start of the
subject.

**IT HAS A REAL ORACLE, unlike K49.** Measured against libpcre2 10.37 through
`docs/design/subroutines_measurements/probes/sr_oracle.py`:

| option word | answer |
|---|---|
| `PCRE2_UTF` | `(3,3)` |
| `PCRE2_UTF｜PCRE2_MATCH_INVALID_UTF` | `(3,3)` |
| `options=0` (byte) | `(2,2)` |

Both UTF option words say `(3,3)`; `(2,2)` is the BYTE answer. So pcrec's
UTF-8 build returns byte semantics, which D26 settles without anyone ruling.

**MECHANISM.** `src/ir/nfa.c:965` `nfa_wrap_unanchored` builds the
start-anywhere self-loop as `memset(nfa->st[any].cls, 0xff, 32)` — every byte.
The `\B` artifact is `RX_ENGINE "dfa"`, `match_form "unwrapped"`, and carries
no retry loop at all, so K49's fix cannot reach it: **the two engines
implement "try the next start" by two different mechanisms and K49 fixed one.**
Before this lane both engines answered `(2,2)` — wrong in agreement, which is
why no cross-engine check caught it.

**WHAT IT REFUTES.** `docs/design/utf8_design.md` §5.5 asserts of
`ENG_ATTEMPT`'s byte start loop: *"Under UTF-8 it would try starts
mid-character. **Those starts have no path** (§2.6) so they cannot produce a
wrong answer; they are wasted attempts... **ASSERTED**: correct but not
optimal."* That is false, and §2.6.1 of the same document — one section
earlier — already contains the counterexample it needed (*"'No path' INVERTS
for a negative assertion"*). §5.5 was written from the positive-only premise
§2.6(e) measured with `.`, and never reconciled with its own neighbour.

**Frank's ASK 5 ruling ("AGREED, leave `ENG_ATTEMPT`'s start loop alone") is
recorded against exactly that claim**, so the ruling rests on a refuted
premise. I have NOT treated it as overturned — I added a boxed refutation at
§5.5 and a re-openable marker in ASK 5's row, and messaged the manager. The
addendum half of the ruling ("VALIDATE AGAINST ORACLES") is the half that
held, and it is what produced §2.6.1.1's table in the first place.

**WHY I DID NOT FIX IT HERE.** The clean general rule is "an unanchored
search's candidate match STARTS are exactly the encoding's character
boundaries". On the DFA that cannot be delivered by making the self-loop
consume whole characters: §2.6(c)'s ruled semantics require a search to still
find matches AFTER an ill-formed byte (`a` on `FF 63` gives `(1,2)`), so the
loop must keep traversing ill-formed bytes. The condition belongs on the SPLIT
into the pattern — a match may start only where the byte is not a continuation
byte — which is an IR/DFA structural change that moves every unanchored `utf8`
DFA artifact, reaches `ENG_ATTEMPT`'s `start++` (`src/gen/emit_dfa.c:6234`)
and the hybrid prefilter's candidate handoff, and is an `abi`-adjacent design
decision rather than a lane decision.

Filed as `docs/dev/known_issues.md` K50 with
`tests/known_fail/k50_utf8_dfa_midchar_start.rxt`.

**NOTE ON THE RATCHET COUNT.** The entry expected the known-fail population to
go 2 → 1 (K34 only). It is 2 → 2: K49's file is deleted and K50's is added.
That is a new bug filed, not K49's fix failing to land — K49's own cell is
live and green in `tests/utf8/axis09_nextpos_findall.rxt`. MEASURED after the
change: `still failing: 2    now passing: 0`, naming K34 and K50. The manager
ruled the same arithmetic independently.

### 3.1 K50's three sites, and whether K49's fix closed the hybrid one

A fix must reach all three "try the next start" mechanisms:
`src/ir/nfa.c:965` (the self-loop, K50's own witness),
`src/gen/emit_dfa.c:6234` (`ENG_ATTEMPT`'s `start++`, ASK 5's loop), and
`src/gen/emit_vm.c:11080-11089` (the HYBRID's retry-window recompute, which
re-seeds `attempt_position` from the inlined DFA prefilter's `window[0][0]`
and therefore inherits the self-loop).

**The manager asked whether my VM fix closes (3). MEASURED: no wrong answer
is reachable through it today — but not because of the fix. The two
populations are disjoint, by coincidence.**

- **MEASURED.** 11 hybrid `-e utf8` artifacts (`RX_VM_PREFILTER "hybrid"`)
  × 6 multi-byte subjects × every startpos = **374 cells, 0 mid-character
  reported starts**. And every nullable VM pattern tried reads
  `RX_VM_PREFILTER "none"` / `RX_ENGINE_SEL "declined-nullable-default"` —
  6 of 6, including `(?<!q)`, `(?<!.)`, `(?!.)`, `(?:(?<!q)a)*`.
- **REASONED** (flagged as an argument, not a measurement): to REPORT a
  mid-character start the VM must MATCH anchored at one, and under `utf8`
  no lowered pattern begins by consuming a continuation byte — so only a
  pattern matching EMPTY there can, and [OPT-4.2]'s
  `declined-nullable-default` gives exactly those no prefilter.

**Nobody wrote that disjointness down**, and it rests on two unrelated
decisions (the UTF-8 lowering's alphabet, and a prefilter decline chosen for
throughput in [OPT-4.2]). So (3) stays on K50's list: a fix for (1) closes it
for free, a fix touching only (2) does not.

### 3.2 One instruction recorded rather than followed

The filing ruling said to mark K50's cell `pcrec-ARGUED` like K49's. **It is
not argued — it has a real oracle**, and the cell and the K50 entry both say
so with the measurement. K49's expectation was ARGUED because no engine
produces that cell at all; K50's witness is an ordinary unanchored search from
offset 0 that every engine answers, and libpcre2 answers `(3,3)` under both
UTF option words. Writing `pcrec-ARGUED` there would have put a false
provenance in the corpus and understated the finding. §2.6.1.1's inversion is
cited in the cell as the SUPPORTING reasoning, which is what it is. Flagged to
the manager rather than decided silently.

---

## 4. What I verified

Every long run was launched in the background and polled from its log.

| # | check | result |
|---|---|---|
| 1 | the K49 witness | `(?<!.)` `-e utf8` startpos 2 → **NOMATCH**; the cell is restored to `tests/utf8/axis09_nextpos_findall.rxt` and the known_fail file is deleted |
| 2 | `tests/harness/run.sh tests/utf8` | see §5 |
| 3 | `make test-encoding-checks` | see §5 |
| 4 | **`run_recursion_identity.sh`** | **GREEN, all four axes, 12 PASS / 0 FAIL. Comparison (B) whole-file byte identity: `differing=0` on `default` (2423), `vm` (2424), `noprefilter` (2423), `nocaptures` (2423), against the current FILEPIN `05b2fe8a`. Comparison (A) program region: `differing=0` on all four.** The byte path did not move; no `abi` bump, no re-pin |
| 5 | `make strict` / `make test-codegen` | see §5 |
| 6 | `tests/mrl`, `tests/encseam` | see §5 |
| 7 | docs | in this change: K49 FIXED marker, K50 entry, §5.5 refutation box + ASK 5 marker, `tests/known_fail/`, `tests/utf8/`, `tests/`, `src/gen/enc/`, `src/gen/` CLAUDE.md |
| 8 | this report | you are reading it |

### 4.1 Byte-path identity, stated precisely

The hard constraint held by CONSTRUCTION and was then measured. The byte
backend's `advance` is the emitter's previous literal reproduced character for
character, and it carries no comment into the artifact on purpose — a comment
there would be new emitted scaffolding on exactly the path D76's gate pins.
Spot-checked directly (`(?<!.)` and `a(b|c)+d` under `-e byte`, identical
apart from the include filename) and then by the gate above over 2,423
patterns × 4 axes.

### 4.2 The ratchet's counts — there are none

The entry said to "check how the ratchet pins its counts and update
deliberately". **It pins none.** `tests/known_fail/run_known_fail.sh`
enumerates `tests/known_fail/*.rxt` with `find` and inverts each file's
verdict; an empty directory is a documented good state. Deleting K49's file
and adding K50's is the whole change there.

### 4.3 The census that DID need re-pinning

`tests/rxtsource/run_rxtsource_tests.sh` pins the corpus census and run.sh's
population as a PAIR, and this change moves them in OPPOSITE directions —
which is the argument for keeping them as two pins rather than deriving one
from the other:

- K49's retirement: census −1 file, ±0 blocks, ±0 lines (the file goes, its
  block and line move into an existing file); run.sh's population +1 block,
  +1 line.
- K50's filing: census +1/+1/+1; run.sh unchanged (known_fail is excluded).

Net: `CENSUS 207→208 / 3883→3884 / 28450→28451`... stated against the pre-lane
`208/3883/28450`, the final values are `208/3884/28451` and
`RUNSH 206/3880/28439`. Both pinned legs now PASS.

### 4.4 A pre-existing red I did NOT absorb

`run_rxtsource_tests.sh` is **108 PASS / 14 FAIL at the lane's base commit**
and 108/14 after my change — I measured the baseline by building `ba7a58cb`
from `git archive` into the scratchpad and running the script there, and the
FAIL sets are line-for-line identical apart from the file count. So `make
test` is already red on this box for reasons that predate this lane. Two
things worth passing on:

- **Most of them are one darwin bug.** BSD `wc -l < file` pads its output
  (`"     207"`), so comparisons like `found      207 ... pinned 207` fail on
  equal numbers. Same family as the `xargs -a` bug the manager fixed in the
  census derivation on the three-merge night, and the same catalogue entry
  ("the script's OTHER derivation legs remain darwin-broken").
- **C3's population pins are stale by 16 cells AT THE BASE** (PASS 13,861 vs
  pinned 13,877; `no-python-expression` 1,907 vs 1,891). My change moves them
  by exactly one cell each in a direction I can account for (the restored
  block is `# pcre2-only`, so −1 PASS / +1 SKIP / +1 pcre2-only). **I did not
  re-pin C3**, because doing so would silently absorb someone else's 16-cell
  drift whose cause I do not know, and this script's own message demands a
  re-pin say which and why. It is an admin-slice item.

---

## 5. Gate results

All runs `CC=gcc-16` on the Mac dev box, launched in the background and polled
from their logs.

| gate | result |
|---|---|
| `tests/codegen/run_recursion_identity.sh` (`PROCS=4`) | **16 PASS / 0 FAIL, exit 0.** (B) whole-file byte identity `differing=0` on all four axes — `default` 2423, `vm` 2424, `noprefilter` 2423, `nocaptures` 2423 — against pin `05b2fe8a`. (A) program region `differing=0` on all four. This is a CLEAN re-run on the final tree; §5.1 says why there was an earlier one |
| `tests/harness/run.sh tests/utf8` | **1336 passed / 0 failed**, 0 compile failures. That is the expected 1335 plus the restored K49 cell |
| `make test-encoding-checks` | **11 passed / 0 failed.** The suite's original 7 plus this change's 4. §8.5: 250 ASCII blocks, **0 divergences**; CHK3 0 stamp differences; DD12a(i) 0 differing engine bodies; DD12a(ii) signatures identical |
| — its K49 section | `byte` advance agrees with `next_pos` on **10,738/10,738** cells and is `pos + 1` on every one; `utf8` agrees on **10,738/10,738** and differs from `pos + 1` on **2,268** of them (the non-vacuity control) |
| `make strict` | **clean** — "whole tree compiles clean with -Werror -Wshadow" |
| `make test-codegen` | **at the darwin baseline, ZERO new.** `run_codegen_tests.sh` **103 passed / 5 failed** — the exact figure the lane entry named. Every other group unchanged (`dfa_stamps` 31/1, `offset_skip` 22/0, `size_term` 31/0, `trie_identity` 7/0, `scan_edge_census` 14/0, `n1_budget` 13/0). I ran the same target on a `git archive` of `ba7a58cb` and the FAIL sets are identical apart from the sabotage-row COUNT (231 → 232), which is S229 being counted |
| `make test-encseam` | **2 passed / 0 failed** |
| `make test-mrl` | **27 passed / 0 failed, exit 0.** It was 26/1 at the lane's base with 21 identical FAIL lines; the manager ruled the repair into this lane and §5.2 is the record |
| `tests/rxtsource` | 108 PASS / 14 FAIL, **identical to the lane's base commit** (§4.4) |
| hybrid composition | a clamp-bearing prefiltered `utf8` artifact puts the advance immediately above the retry-window recompute and compiles `-O1 -Wall -Wextra -Werror` clean |

### 5.1 S229's failing direction, measured

I applied S229 to the working tree by hand, rebuilt, and ran its own arm:
`tests/utf8/axis09_nextpos_findall.rxt` goes from 0 failures to **1** — the
restored K49 cell, which is the row's declared detector. Reverted and rebuilt
before any further gate ran. (I also learned the hard way not to rebuild while
the identity gate is running; the gate was re-run clean afterwards, and the
numbers in the table above are from the clean run.)

### 5.2 THE SECOND FINDING, and the manager ruled its repair into this lane

`make test-mrl` was red at the lane's base and red after the K49 fix, with the
same 21 lines. It is NOT the `wc`-padding family — it is `tests/mrl/
cwmax_check.c`, the instrument that reads `pcrec_cwmax` DIRECTLY and requires
every oracle-verified span in the whole `.rxt` corpus to fit inside its
pattern's max width:

```
FAIL: cwmax: the sweep FAILED
FAIL tests/utf8/axis01_encoded_length.rxt:50:  ORACLE span 2 bytes EXCEEDS cwmax=1 for pattern '[^a]'
FAIL tests/utf8/axis01_encoded_length.rxt:451: ORACLE span 3 bytes EXCEEDS cwmax=1 for pattern '[EUR]'
FAIL tests/utf8/axis01_encoded_length.rxt:466: ORACLE span 4 bytes EXCEEDS cwmax=1 for pattern '[^EUR]'
```

**I VERIFIED THE TRIAGE BEFORE TOUCHING THE CHECK, because the ruling's stop
condition made that the load-bearing step.** If cwmax were genuinely
under-estimating in characters anywhere, this would be an ENGINE bug in the
silent direction — the lookaround fixed-width rule reads this number, and an
under-estimate makes a variable-width lookbehind branch look fixed. It is not.
Every one of the 21 failing cells is a whole-subject span over exactly ONE
multi-byte character (or one character against a `{1,2}`'s cwmax of 2), read
cell by cell off the corpus lines themselves before any code changed:

| pattern | subject | span | in characters | cwmax |
|---|---|---|---|---|
| `[^a]` | `CE B1` | 0..2 | **1** | 1 |
| `[^\x{61}]`, `[^A-a]`, `[α]`, `[Α-α]`, `[αβ]` | 2-byte | 0..2 | **1** | 1 |
| `[€]`, `[₠-€]`, `[^€]`, `[^₠-€]` | 3-byte | 0..3 | **1** | 1 |
| `[^€]`, `[^₠-€]` | 4-byte | 0..4 | **1** | 1 |
| `[^α]{1,2}`, `[€]{1,2}`, `[^€]{1,2}` | 3-byte | 0..3 | **1** | 2 |

So the mismatch was a UNIT mismatch inside the check, exactly as triaged, and
the repair carries **no `src/` change at all**. The second half of the stop
condition is also discharged: no NEW violation appeared under the repair.

**THE PREMISE THAT EXPIRED.** The file's own header said its re-aim into
characters was sound because *"under the `byte` encoding this file parses with,
one character is one byte."* True when written; false the moment `tests/utf8/`
merged, since those blocks carry `encoding utf8` and their oracle spans are
BYTE offsets into multi-byte subjects. The header now carries the new rule,
dated, with that sentence quoted as the thing that stopped being true.

**THE REPAIR IS TWO HALVES THAT MUST MOVE TOGETHER.** A block is now PARSED
under its own `encoding` — so cwmax is computed on the AST the block MEANS,
which matters because under `byte` a literal `[€]` is a class of three BYTES
and under `utf8` it is one CHARACTER — and its oracle span is MEASURED in the
same unit. `byte` blocks keep the byte comparison unchanged to the line. The
encoding name is resolved through `pcrec_enc_by_name`, the seam's own registry,
so this file cannot drift from `enc.c`'s spelling.

**THE CHARACTER COUNT SHARES NO SOURCE WITH WHAT IT CHECKS** (learnings §3):
it is one predicate over the subject's own bytes — non-continuation bytes in
`subject[start..end)` — and never asks pcrec, `next_pos`, or the lowering. A
span counted by the compiler's own notion of a boundary would have made
CHECK 2 a comparison of pcrec against itself. The subject decoder is
transcribed from `tests/harness/verify_rxt.py`'s `decode_subject`, and an
undecodable subject is counted, reported and fails rather than falling through
silently.

**TWO NEW NON-VACUITY FLOORS, both validated in the failing direction**, on
the same rule the file's three existing sabotage modes follow:

| floor | why | validated by |
|---|---|---|
| the `utf8` block population is NONZERO | a lost corpus or a broken `encoding` reader would leave the whole character path unentered and GREEN | disabling the reader → "ZERO utf8 blocks seen", check FAILS |
| at least one compared span's BYTE width EXCEEDS its character width | the first floor alone is satisfied by a `utf8` corpus of ASCII-only subjects, where the two counts coincide and the decode proves nothing | turning the character count back into a byte count → floor fires, and it is caught TWICE (that sabotage also produces 84 CHECK 2 violations) |

MEASURED after the repair: 208 files, 3884 blocks, 3293 parsed, 591 refused,
23,820 nodes (18,698 bounded), 11,222 oracle spans, **216 utf8 blocks / 307
utf8 spans, 101 of them with a byte width exceeding their character width, 0
violations**. `make test-mrl` reads **27/0**. The three existing
`PCREC_CWMAX_SABOTAGE` modes (`zero`, `unbounded`, `swap`) still each make the
binary FAIL, re-verified after the change.

**The Linux arm should follow.** The battery read 26/1 there with the identical
FAIL set, so this is what makes the owed Linux `make test` re-run green; the
repair is platform-neutral (no `wc`, no `xargs`, no shell at all — it is C).

---

## 5.5 Rulings received

| ruling | disposition |
|---|---|
| Fix the VM retry advance per the charter; file the DFA half as K50; annotate §5.5/ASK 5 with the refutation; do NOT start the DFA fix in this lane | done, all four |
| K50 gets its own regression, `k50_utf8_dfa_midchar_start.rxt`, pinning `(3,3)` for the `\B` witness | done, under that filename |
| Mark it `pcrec-ARGUED` like K49's | **RECORDED, NOT FOLLOWED** — it is oracle-backed; §3.2 |
| Keep the ratchet's expected-failing count at 2 (K34 + K50); re-pin the ratchet against that arithmetic and say so in the commit | count MEASURED at 2. **There is no ratchet pin to re-pin** — `run_known_fail.sh` enumerates the directory with `find` and pins no counts. The census that DID need re-pinning is `tests/rxtsource/`'s, and the commit says so |
| Name the hybrid prefilter handoff (`emit_vm.c:11080-11089`) in K50's site list; state whether K49's fix closes it, measuring a witness if cheap | done and MEASURED; §3.1 |
| Put the `back_step` malformed-run-repair interaction in K50's entry as the general amplifier | done — it is the paragraph that generalises the defect off lookbehind and onto the whole negative-assertion family plus `\B` |
| S223 is taken; renumber | **S229** (the highest existing is S228, not S226 — `S227_scan_edge_entry_s0_only.sh` and `S228_cls_fold_recognizer_widened.sh` are both present). Re-verified: `m6read_check_sab_anchors.py` reads 232 rows and flags only the two pre-existing ones (S09, S199) |

---

## 6. What is owed

1. **K50** — the DFA half. Needs a design ruling (§3), and should be taken
   together with `ENG_ATTEMPT`'s `start++` and the hybrid prefilter handoff so
   all three "try the next start" mechanisms end up spelling one rule.
2. **ASK 5** — re-openable on a refuted premise. Frank's call, not mine.
3. **`make test-mrl` is RED at this lane's base and nobody has filed it** —
   `pcrec_maxw`/`cwmax` answers 1 byte for `[^a]` under `-e utf8` while the
   oracle span is 2, on 21 cells of `tests/utf8/axis01_encoded_length.rxt`.
   §5.2 has the detail. It needs its own row, and its failure direction
   (under-estimating a width, which the lookbehind fixed-width rule reads) is
   the unsound one.
4. **The advance-agreement check is not in the mech matrix.**
   `run_encoding_checks.sh` has no suite token in
   `tests/mech/run_sabotage_matrix.sh`, so sabotage row **S229** (K49 planted:
   the utf8 advance reverts to the byte step) scores on the `harness` arm
   against the restored corpus cell only. I validated S229 fires there
   directly — applied it, rebuilt, and `tests/utf8/axis09_nextpos_findall.rxt`
   goes to 1 failure — and reverted. Wiring the encoding checks into the
   matrix is a separate, larger change to that dispatch.
5. **A `\B`-under-`utf8` cell does not exist in `tests/utf8/`.** The corpus
   could not have found K50; the byte-mirror libpcre2 differential that
   directory's own CLAUDE.md already names as an open item would have.

---

## 7. Spec (D80): NO hunk travels, and that is a positive claim

The entry asked me to say so explicitly. Nothing caller-observable moved:

- `docs/spec/match_api.md` never licensed a reported position inside a
  character (only `\K` has a documented exception), so the old behaviour was
  un-licensed rather than contracted.
- `<prefix>_next_pos` and §3.1's find-all protocol are untouched, in text and
  in behaviour.
- The caller-supplied mid-character `startpos`, whose answer utf8_design.md
  §2.6.1 rules DEFINED, is unchanged — verified live at startpos 1 and 3.
- No entry, flag, stamp, limit, diagnostic tier or module behaviour moved. No
  `abi` bump: the byte artifact is byte-identical and the utf8 artifact's
  change is a behaviour fix inside an existing residual, not new scaffolding
  on a pinned path.
