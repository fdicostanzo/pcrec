# lim2 report — [LIM-2] the DFA route's projected-size bail

Lane `lim2`, worktree `worktrees/lim2`, branch `lane/lim2`, from `main` at
`56f34b01` (abi 20). **Status: tonight/write-only phase complete, idle for
`.lift`.** This delivers a working projection + early refusal, measured
timing wins on real altwide witnesses, byte-identity evidence on 11
accepted patterns and 2 refused ones (verdict/reason parity), a permanent
self-contained resource-suite check (written, not run as a suite — the
hold forbids that), and the D80 spec hunk. It does **not** deliver a full
corpus sweep or `make test` — both wait for `.lift` per the brief.

Disclosure (scope mandate): the only injected context that shaped a
decision was the repo `CLAUDE.md` (the situation-index table's rows on
`gnutimeout`/`scripts/watchdog`, the "change anything a caller can observe
→ spec hunk" row, and the general-mechanisms/D77 memory pointers) and the
memory index summaries named in the brief. Nothing else outside the brief
and the charter's own named files influenced the design.

## 1. Where the projection lives, and why the charter's own premise needed revising

**The charter's premise, checked first.** `PCREC_MAX_TABLE_ENTRIES`
(2,000,000 entries, "≈12 MB source") already bounds subset construction's
OWN state cap, and is far above `PCREC_MAX_EMIT_BYTES` (1,000,000 *bytes*,
not entries) — so construction routinely runs to ~150,000+ entries before
the emit-bytes cap would ever have accepted the result. That gap is real
and is exactly [LIM-2]'s target.

**The projection itself lives in `src/ir/dfa.c`'s worklist loop**
(`pcrec_build_dfa`), the same loop that already interns states via
`make_state` and already refuses mid-construction for the state-count and
K7 (`PCREC_MAX_SUBSET_ELEMS`) caps — this is the established idiom for a
during-construction refusal in this file, not a new one. Per finalized
state row (`si`, all `ncls` classes decided), it adds that row's EXACT
text-byte contribution to a running total, using the same nested order and
`" %d,"`/`"\n       "`-every-16-cells layout `src/gen/emit_dfa.c`'s
`emit_tr_table` uses — computed by digit-count arithmetic, never by
building the string.

**It is scoped to ONE call site**: the mandatory forward table-engine
build (`compile.c`'s `cx.job->dfa`), via a new `size_bail` parameter on
`pcrec_build_dfa` (four call sites total; only this one passes `true`).
Not the reverse machine, not the ENG_ATTEMPT/goto engine, not the anchored
machine — see §2 for why forward-only is the sound choice, not just the
convenient one.

**Representation certainty, not a guess.** The projection assumes the
INDEXED table form (`cell_type "short"`, `cell_of(st) = st`) and only acts
once `d->n * d->ncls > PREMUL_MAX_ENTRIES` (65,535) — at which point
`emit_dfa.c`'s `dfa_premul` is PROVABLY false for the rest of this
machine's life (its first conjunct, `ents > PREMUL_MAX_ENTRIES`, is
independent of any deny flag or seed condition), so indexed is the
guaranteed final form for every row counted, including rows decided
before the threshold crossed. `PREMUL_DEAD`/`PREMUL_MAX_ENTRIES` moved
from `emit_dfa.c` to `src/core/internal.h` so both files read one symbol
— this project's own stated anti-pattern is "two literals that must be
kept in step," and duplicating 65535 would have been exactly that.

## 2. What is exact, what is bounded, and the correctness finding that reshaped the design

**What's exact:** the cell-text-byte formula itself (an arithmetic mirror
of `emit_tr_table`'s own loop), and — new since the charter's own framing
— the REVERSE machine's contribution, once it is finished and minimized
(see §3).

**What is NOT exact, and the reason the charter's "states × classes × cell
width is exact" premise needed a correction:** the projection runs DURING
RAW subset construction, but `src/opt/minimize.c` runs AFTER
`pcrec_build_dfa` returns and only ever REMOVES states. Measured on the
worktree's own instrumented build (temporary debug prints, removed before
this diff — not part of the delivered patch):

| witness | raw fwd n | minimized fwd n | fwd shrink | raw rev n | minimized rev n | rev shrink |
|---|---|---|---|---|---|---|
| `w-2048` (altwide) | 9,872 | 9,798 | 0.75% | 9,817 | 6,925 | 29.5% |
| `s-4096` (altwide) | 8,269 | 7,976 | 3.5% | 8,104 | 2,806 | 65.4% |

So a raw-construction byte count is **not** a rigorous lower bound on the
machine's own final (minimized) table bytes — it can overstate it, on the
REVERSE machine substantially. This is why the projection is scoped to
the FORWARD machine only (its own shrink measured small, ≤3.5%, on both
witnesses that actually reach the expensive population) and why it
carries a margin (`BAIL_KEEP_PCT`, §4) rather than triggering on the raw
figure directly. **This is a real, disclosed gap between "exact" as the
charter framed it and what is actually provable without finishing
minimization** — flagged for ruling in §7.

## 3. The reverse-headstart redesign (why a naive forward-only bail was not enough)

The first working version (forward-only, no headstart, a `2×cap` margin)
built and ran, but **did not fire** on `w-2048` — it fell through to the
old post-emission check, unchanged, 10.97s. Measured cause: the forward
table alone is only **~60% of the total artifact** (1,427,829 of
2,379,410 bytes on `w-2048`'s full, uncapped artifact) — so even a raw
forward-only projection with no margin at all could only ever reach
`cap` once forward's own bytes hit `cap`, which for this witness is ~70%
of the way through forward's own growth (and construction time, measured
separately, correlates closely with rows processed — not front-loaded as
first hypothesized).

**Fix**: `compile.c`'s D7 fast path now builds and MINIMIZES the reverse
machine FIRST (reverse construction is cheap regardless — 23-24ms on both
big witnesses, against 10.68s and 19.45s for forward). Its exact,
already-minimized table byte count (`pcrec_dfa_indexed_table_bytes`, a new
small helper, same formula, run once over a finished machine) is passed
into the forward build as `size_bail_headstart`, shrinking the forward
budget needed before the bail can prove anything. This reorder is argued
order-independent for every other observable in `compile.c`'s own comment
at the site (K7's running total is order-independent by construction;
each machine's own state cap is a separate field; no refusal names a
machine) — and is EMPIRICALLY confirmed order-independent below (§5,
byte-identity on accepted patterns; verdict parity on refused ones).

## 4. The margin (`BAIL_KEEP_PCT = 85`) — a judgment call, not a proof

Refuse once `size_bail_headstart + this_machine's_own_raw_bytes × 0.85 >
cap`. The 85% keep factor assumes as little as 85% of the forward
machine's own raw bytes survive minimization — a 15-point margin against
the ≤3.5-point shrink measured on the two witnesses in §2's table. This
follows the SAME "abort factor" methodology this codebase already uses
elsewhere (`compile.c`'s size-term ladder scratch bound, `3×` derived from
a measured 47.8% worst-case prose ratio) — a generous multiple of a
measured worst case, not an assumed one. **It is a margin, not a proof**,
and it is measured on exactly two witnesses. A wider sweep (post-lift,
over the full corpus and altwide set) is the real validation; if it finds
a forward-machine shrink ratio worse than ~15%, the margin needs
tightening. Flagged for ruling.

## 5. The numbers

All single compiles, `scripts/watchdog`-wrapped, this box. "Before" =
`main` at `56f34b01`, exported via `git archive` into scratch and built
there (no new worktree, per the scope mandate) — not a `pcrec-bench`
dependency.

### Refusal timing, altwide witnesses (read-only reference from pcrec-bench)

| pattern | before (wall) | after (wall) | reduction | before msg bytes | after msg bytes (projected) |
|---|---|---|---|---|---|
| `w-2048` | 10.97s | **1.55s** | 86% | 2,379,410 | 1,025,183 |
| `s-4096` | 19.58s | **12.51s** | 36% | 1,621,605 | 1,114,550 |
| `s-2048` | 5.25s | 5.27s | ~0% | 1,260,722 | 1,260,722 (identical — bail never proved it) |
| `sh1-512` | 0.13s | 0.13s | ~0% | 1,525,450 | 1,525,450 (identical) |

**The improvement is real but pattern-dependent, not uniform, and does
NOT reach the charter's "VM route's cost class" (~0.1s) target on every
witness.** `w-2048` gets close (1.55s). `s-4096` improves substantially
but not close to that target — its reverse machine is a smaller share of
its total (~26%, against `w-2048`'s ~36%), so the headstart buys less
runway. `s-2048` and `sh1-512` see NO improvement at all: their bail
threshold, under the current margin, is never crossed before raw
construction would have finished anyway (a SAFE outcome — same verdict,
same message, byte-for-byte on `s-2048` and `sh1-512` — just not a win).
This is the honest state of the feature, not a partial description of a
uniform one.

### Self-contained synthetic witness (no pcrec-bench dependency; the one the permanent check pins)

1,600 literal alternatives, 6-14 lowercase bytes each, `random.seed(1729)`:
before 12.15s (refuses at 2,929,087 bytes) → after **1.02s** (refuses at
1,256,802 bytes). This is the witness `tests/resource/
run_lim2_sizecap_projection.sh` uses.

### Verdict/reason parity, refused patterns

`w-2048`, `s-4096`, `s-2048`, `sh1-512` — before and after both refuse,
same stamped category either way. §5's table was measured before the
wording ruling (§6) landed, so its "after msg bytes" column shows the
OLD same-template wording with a smaller number; post-ruling, `w-2048`
and `s-4096` (where the bail fires early) now read `"projected at least
N bytes of emitted code"` instead, while `s-2048` and `sh1-512` (where
it does not fire) are BYTE-FOR-BYTE identical to "before", wording
included, since they fall through to the unchanged late check.

### Byte identity, accepted patterns

11 altwide patterns confirmed byte-for-byte identical between before and
after (same output basename in separate directories, to avoid a
self-referencing `#include` false mismatch that the first attempt hit and
is worth recording as a methodology note): `floor`, `w-8`, `sh1-64`,
`w-64`, `nar4-64`, `sfx-64`, `ci-256`, `srt-256`, `pfx3-256`, `nar4-256`,
`cnt-64`. This is a MANUAL, one-time sweep (not `make test`, not a
suite — the hold forbids both); the corpus-wide version is a `.lift` item.

## 6. The diagnostic wording — RULED (manager, 2026-09-04, lim2_rulings.md item 2)

The charter asked for "the SAME stamped reason and diagnostic the
post-emission check gives today"; the correction is that the byte figure
an early refusal has is partial, so the wording should say so rather than
imitate an exact one. **Ruled and implemented**: the two stamped fields
(`cx->size_cap_refused`/`_bytes`/`_limit`) and the refusal CATEGORY are
unchanged and identical either way (never `cx->dfa_overflowed` — that
field means "too many STATES", a different refusal). The TEXT now
differs by which check fires:

- post-emission (every route besides the DFA total cap, and the DFA
  route whenever the bail's margin does not prove the cap crossed
  early): unchanged, `"pattern too large: N bytes of emitted C source
  (limit L, ~K KB .o) ..."`, `N` the artifact's true final size.
- DFA route, early bail fires: `"pattern too large: projected at least
  N bytes of emitted code (limit L) ..."` — `N` the running total at
  the point of refusal, always less than the true final size would have
  been, `.o`-size estimate dropped (it is calibrated against a final
  total). Measured live: `pcrec: pattern too large: projected at least
  1256802 bytes of emitted code (limit 1000000). ...` on the §5
  synthetic witness.

`docs/spec/limits.md` §8 has the spec hunk; `tests/resource/
run_lim2_sizecap_projection.sh` asserts the EARLY wording specifically
(a witness that refused via the late wording instead would mean the
bail did not fire — the check's own signal for that regression, not a
pass).

## 7. Rulings received (manager, 2026-09-04, docs/dev/lanes/lim2_rulings.md)

1. **The `BAIL_KEEP_PCT = 85` margin is PROVISIONAL until a population
   proves it.** Ruled: the acceptance is a CENSUS built into the check
   script, post-lift (it needs the corpus) — per machine, over the whole
   corpus and the bench's altwide set, record raw table size vs. minimized
   table size, and ASSERT the margin exceeds the measured MAX forward
   shrink by at least 2×, RED with the distribution table otherwise. If
   the census ever finds a shrink the current margin does not clear, the
   margin moves to the census's number — never the reverse. Not yet
   built (needs `.lift`); §9 below is now sequenced around it.
2. **The diagnostic wording** — ruled and implemented, §6 above.
3. **`tests/resource` is the right home** — confirmed; no change needed.
4. **`size_bail`'s scope (forward table-engine build only)** — accepted
   per D77. The unmeasured machines (reverse, ENG_ATTEMPT/goto, the
   anchored machine) stay this row's named follow-on list, not built.
5. **`s-2048`/`sh1-512` (no benefit under the current margin)** — ruled
   OUT OF THIS STEP: filed as **[LIM-2] STEP 2 — an accept-table
   projection term**, with §5's numbers as its own starting measurement.
   Not built tonight; `docs/dev/plan.md`'s [LIM-2] row should gain a
   STEP 2 sub-line when that work actually begins (per this repo's own
   convention: expand into substeps only when work starts).

## 8. Delivery bar checklist

- [x] Branch builds clean under `make -j2` and `make strict`.
- [x] Projection refuses during construction with the same stamped
      category and message template (byte figure differs when the bail
      fires early — disclosed, §6).
- [~] Refusal-identity check: written (`tests/resource/
      run_lim2_sizecap_projection.sh`, self-contained, wired into `make
      test`), NOT run as a suite (hold). A manual, non-scripted single-
      compile sweep (§5) stands in for tonight.
- [x] Altwide cost table before/after (§5) — mixed results, honestly
      reported, not uniformly at target.
- [x] Byte identity on 11 accepted artifacts (§5), verdict/reason parity
      on 4 refused ones.
- [x] Spec hunk: `docs/spec/limits.md` §8 ("Handling an oversized
      artifact" 's lead-in), disclosing both the mechanism and the
      byte-figure-meaning deviation.
- [x] CLAUDE.md rows: `src/ir/CLAUDE.md`, `src/core/CLAUDE.md`,
      `src/gen/CLAUDE.md`, `tests/resource/CLAUDE.md`.
- [ ] `make test` / `make test-codegen` / `make test-registry` — post-lift
      items, per the brief's own phasing.

## 9. What's next (post-`.lift`) — sequenced per lim2_rulings.md

1. `make test` in the background, poll the log (never foreground-block).
2. **Build the census (ruling item 1)** into `tests/resource/
   run_lim2_sizecap_projection.sh`: per DFA machine, over the whole
   corpus and the bench's altwide set, raw table size vs. minimized
   table size; assert `BAIL_KEEP_PCT`'s margin exceeds the measured MAX
   forward shrink by ≥2×, print the distribution, RED with the table
   otherwise. If it finds a shrink the margin does not clear, move the
   margin to the census's number and re-measure §5's timings (a tighter
   margin fires later, so the wins could shrink — report the real
   numbers, not the ones in this note).
3. Run `tests/resource/run_lim2_sizecap_projection.sh` for real, census
   included.
4. `make test-codegen` — per the ruling, this is where the reverse-first
   build reorder's OWN acceptance lives: the identity gate proves every
   accepted artifact byte-identical, which is the real check on the
   reorder (§5's 11-pattern manual sweep was a spot check, not this).
5. `make test-registry`.
6. `make test-axes` only if the manager's lift message asks for it — this
   lane's own view (§7 item 4's D77 answer) is that no new axis is needed
   since the projection changes no accepted artifact's bytes; open to
   correction.
7. Report final; DELIVERED.
