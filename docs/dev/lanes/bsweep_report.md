# LANE bsweep — [BSWEEP] the COMMITTED emitter byte-neutrality sweep (admin column)

Branch `lane/bsweep`, branched from `main` at `7ee40500`. Built
`scripts/emit_sweep.py`, the emitter byte-neutrality sweep five wave-2 lanes
(w2a, w2b, w2x, w2y, w2census) each rebuilt from prose in their own
scratchpads, landing on three different composition-arm populations. This
report is the delivery: what was built, the three required validations
with counts, and the reconciliation of the five prior lanes' figures.

---

## 0. What was built

`scripts/emit_sweep.py` — a self-contained python driver, invoked directly
(`alt_census.py`'s own precedent — no `.sh` wrapper is needed or added).
Compares a REFERENCE `pcrec` (`git archive REF`, or a pre-built
`--ref-bin`) against a WORKING `pcrec` (the caller's `build/pcrec` by
default, or a second historical revision via `--tree-rev`) across the four
streams the brief names, all unconditionally under `--features all`:

1. corpus argv, `.c` at the default engine
2. corpus argv, `.c` at `--engine=vm`
3. corpus argv, `--emit-ir` at `--engine=vm` (always forced VM — see §1.2)
4. composition: `--source FILE` over every `.rxt`/`.rxtin` under `tests/`

Self-checks itself first (two independent builds of the SAME reference
revision, byte-identical at full reach expected) unless `--no-self-check`.
Reach and composition-population expectations are FLOORS pinned in the
script's own `PINS` dict (D110's shape, with a much smaller margin than
that ruling's "half the measured value" — see §2 for why). An independent
DELIVER-block witness (§1.3) checks that the composition arm is actually
reaching `vm_splice`'s DELIVER block, not merely that a population count
looks healthy.

Also delivered: a `docs/testing.md` section ("Emitter byte-neutrality
sweep"), a `scripts/CLAUDE.md` entry, a `build-emitsweep/` `.gitignore`
line (the tool's scratch tree, never `build/`), and this report.

**One r1 fix landed mid-flight** (§1.3): the composition arm's
per-file comparison was gated on `rc == 0`, undercounting reach by two
files (a partial-success fixture, a contention timeout under the arm's
own concurrency). Fixed, and the composition arm now gets its own
`--comp-timeout`/`--comp-jobs` (more generous, less concurrent than the
argv streams by default) since a composition item can be heavier —
`bench_altwide_0_2.rxtin` alone declares 11 targets.

### 0.1 The corpus-population derivation

Reused rather than re-derived: `--list-source` over every `.rxt` under
`tests/`, decoding column 5's `\t \n \r \\ \xNN` escapes — the exact
methodology `docs/dev/w1stage0_evidence/longprefix_sweep.py` and
`docs/dev/dialtrain_byteid_evidence/byteid_sweep.py` already use (both
copies are textually identical decoders; the header comment says why a
third independent copy would be the thing memory
`pcrec-general-mechanisms-not-special-cases` warns about). The composition
file set is every `.rxt`/`.rxtin` under `tests/` by `find`, matching
w2a/w2b/w2x/w2y's own "304 files" figure exactly (211 `.rxt` + 93
`.rxtin`, counted independently here by a second `find` invocation before
writing this report).

---

## 1. Three findings while building it

### 1.1 The DELIVER role text never reaches `.c` output at all

The brief's own witness language ("at least one composition artifact
contains a DELIVER block") reads as though the DELIVER loop's role
string — `vm_set`'s fourth argument, "DELIVER: keep the callee's exported
span…" — were somewhere in the emitted comment text. It is not: `vm_set`
(`src/gen/emit_vm.c:3054`) writes the role ONLY into the `vm_ev()` event
stream that backs `--emit-ir`'s listing, never into the `.c` file. And
`--emit-ir` cannot be combined with `--source` (`cli/main.c:1471-1481`
refuses composing any query with a compile mode), so there is no way to
get an IR listing of a composed target at all — the DELIVER mechanism is
structurally invisible to the one stream that carries its own prose.

So the witness has to be structural instead. Confirmed by direct
inspection of `deliver_forms.rxtin`'s four artifacts and
`compose_delivers.rxtin`'s one: the DELIVER loop's actual emitted CODE
shape is two adjacent
`<PREFIX>_SET(<PREFIX>_SLOT_GROUP<A>_START/_END, slot_values[<PREFIX>_SLOT_GROUP<B>_...])`
statements with `A != B` — a cross-group span copy. Ordinary
backtrack-restore code (the surrounding lines in the same functions) only
ever copies a group's own PRIOR value back into itself, same group number
both sides, because a composed call's caller and callee never share a
group number. `plaincall.c` (the same fixture's non-delivering fourth call
form) carries no capture-slot `_SET` calls at all — the cleanest possible
negative control, because `plaincall` exports nothing, so its captures are
entirely erased.

This is corroborating, not load-bearing on its own — the load-bearing
protection is the whole-artifact byte-identity comparison every
composition file already gets, which necessarily covers these bytes
whenever they exist. My first draft of the regex used
`<PREFIX>_GROUP<N>_...` (missing `_SLOT`) and matched nothing on either
fixture; caught immediately by testing it against the known-good text
before trusting it (`DELIVER_RE`'s own header names the corrected form).

### 1.2 `--emit-ir` must force `--engine=vm`, independent of stream 1's engine

w2x_report.md §5 already found this once ("a 53% reach loss that reads as
a perfectly healthy green"): `--emit-ir` at the default engine refuses on
every DFA-winning pattern, because it prints "a VM program; this pattern
compiles to the DFA engine". Stream 3 forces `--engine=vm` unconditionally
in `compile_stream_ir`, regardless of what stream 1 does — confirmed by
measurement (§2): stream 3's reach (3,518) exceeds stream 1's (3,517) by
exactly the count of patterns the DFA wins that the VM can also compile,
matching w2b's own recorded figure.

### 1.3 The composition arm's "artifact" unit, and the two bugs a first cut of THIS tool had

"Artifact" is defined here as every file (`.c` and `.h` both) written into
a per-file `-o <dir>` output directory — not the target/`.c` count alone.

**This lane's first cut measured 30 producing files / 72 artifacts**, which
matched `w2x_report.md`'s own recorded "30 producing 72 artifacts" exactly
but not `w2y_report.md`'s "32 producing 96 artifacts" (also claimed at
`--features all`), nor `w2a_report.md`'s "74 artifacts", nor `w2census`'s
figures. The manager asked for the cause rather than a note that the
numbers disagree — investigated below, and the tool now measures **32
producing / 96 artifacts**, matching w2y EXACTLY, because the first cut
was undercounting by precisely those two files, for two independent
reasons, neither a corpus fact:

**Bug 1 — `compose_encoding_clash.rxtin` was skipped despite genuinely
producing.** This fixture deliberately declares two targets: `ok`
(compiles cleanly) and `clash` (a later definition's `encoding utf8`
conflicts with the artifact's own `byte` encoding — a REFUSAL by design,
`docs/spec/rxt_format.md`'s per-artifact-encoding rule). `--source` writes
each target's artifact in file order and stops on the first failure, so
`ok.c`/`ok.h` are genuinely on disk when the process exits 1. The first
cut of `sweep_composition` gated its ENTIRE per-file byte comparison on
`rc == 0`, so this file's two real, on-disk artifacts were silently
skipped and counted as `both_refuse` — the wrong bucket, since something
WAS produced and deserved comparing. Fixed: compare artifacts whenever
BOTH sides agree on rc AND on the artifact name set, never gated on
`rc == 0` alone (an rc or name-set mismatch between the two sides is still
a real asymmetry, still caught, still reported).

**Bug 2 — `bench_altwide_0_2.rxtin` timed out under the sweep's OWN
concurrency.** This is pcrec-bench's own witness file and the single
largest composition fixture: 11 targets, 22 artifacts. Diagnosed by
running the composition arm standalone (no other stream competing for
CPU) and finding it completes comfortably; under the argv streams' own
30-second timeout AND 12-way concurrency (every other composition file
compiling at the same time), it did not finish within budget — a
contention artifact of this tool's own parallelism, not a corpus fact.
Confirmed directly: `run_composition`'s return for this file was
`(rc=None, err="TIMEOUT")` under the original settings, and clean under
more generous ones. Fixed with `--comp-timeout` (default
`max(3x --timeout, 90)`) and `--comp-jobs` (default `min(--jobs, 6)`) —
composition items are heavier per-item than a single-pattern argv
compile and get their own, less contended budget.

**Both bugs were found by isolating the per-file logic and comparing it
against a hand-replicated version of the same code outside
`sweep_composition`** — the replica (same `run_composition` calls, same
tags, no `rc`-gate) measured 32/96 on the same binary the buggy function
measured 30/72 on, which is what made "the function itself, not the
population" the right place to look. See §2/§3 below for the corrected,
re-validated numbers; §4 for the sabotage re-run against the fixed tool.

---

## 2. Validation 1 — self-check at `ac21aaaf`

`python3 scripts/emit_sweep.py --ref ac21aaaf --tree-rev 7f0f1e55` runs the
self-check automatically first: two independent `git archive`+`make`
builds of `ac21aaaf` (catching a build-nondeterminism confound as a
bonus), full sweep between them. Numbers below are from the RE-RUN against
the fixed tool (§1.3); the first (buggy) run also came back all-identical,
just at the undercounted composition population (30/72).

**MEASURED: all-identical, full reach, on all four streams.**

| stream | population | reach (both_ok) | movers | asymmetric |
|---|---:|---:|---:|---:|
| corpus argv, `.c` default engine | 3,938 | 3,517 | 0 | 0 |
| corpus argv, `.c` `--engine=vm` | 3,938 | 3,518 | 0 | 0 |
| corpus argv, `--emit-ir` `--engine=vm` | 3,938 | 3,518 | 0 | 0 |
| composition, `--source` | 304 | 32 (producing 32 / artifacts 96) | 0 | 0 |

`SELF-CHECK PASSED` — the instrument is trusted for the real comparison
below.

## 3. Validation 2 — ref `ac21aaaf` vs. tree at main `7f0f1e55` (wave 2 slice E merged)

Same invocation's real-run half. Neither side touches any live `build/`
directory — both are `git archive`+`make` extractions into
`build-emitsweep/`'s scratch tree (`ac21aaaf` and `7f0f1e55` respectively),
so the scope mandate's "never write outside your own worktree" holds even
though this compares two commits neither of which is this lane's own
branch point.

**MEASURED: 0 movers, 0 asymmetric rows, on all four streams — full
byte-identity, matching the self-check's own reach numbers exactly.**

| stream | population | reach | movers | asymmetric |
|---|---:|---:|---:|---:|
| corpus argv, `.c` default engine | 3,938 | 3,517 | 0 | 0 |
| corpus argv, `.c` `--engine=vm` | 3,938 | 3,518 | 0 | 0 |
| corpus argv, `--emit-ir` `--engine=vm` | 3,938 | 3,518 | 0 | 0 |
| composition, `--source` | 304 | 32 (producing 32 / artifacts 96) | 0 | 0 |

DELIVER witness: OK — both `compose_delivers.rxtin` and
`deliver_forms.rxtin` produce, and the cross-group `SET`-pair shape is
present. All floors clear (composition producing sits exactly at its
zero-slack floor of 32, by design — see the PINS dict's own comment).

### 3.1 The five-lane composition reconciliation

| lane | producing | artifacts | features | note |
|---|---:|---:|---|---|
| w2a | — | 74 | `--features all` | no producing count recorded |
| w2b | 32 | 96 | `--features all` | matches this tool's corrected number |
| w2x | 30 | 72 | `--features all` | matches this tool's FIRST (buggy) number |
| w2y | 29 / **32** | 84 / **96** | default / `--features all` | the `--features` finding itself; `--features all` row matches this tool exactly |
| w2census | — | — | — | not a composition-count lane |
| **bsweep (this tool, corrected)** | **32** | **96** | `--features all` | matches w2b and w2y's `--features all` row exactly |

Three of five recorded `--features all` figures now agree (w2b, w2y,
bsweep) at 32/96. w2x's 30/72 is now EXPLAINED, not merely unmatched:
w2x's own hand-rolled driver most likely shares this tool's first-cut
mistake in some form (an `rc`-gated comparison, a tighter timeout under
its own concurrency, or both) — its report does not carry enough
implementation detail to say which, and re-deriving w2x's own scratch
driver (long gone, per that lane's own report) is not a productive use of
this lane's remaining time. w2a's 74 has no producing count to compare
against and is not further explained here. **The reconciliation that
matters going forward is that this tool's number is now independently
arrived at by TWO different lanes' worth of methodology (w2b's own
sweep, and this tool's corrected one) and matches exactly** — ending the
three-different-numbers problem the brief chartered this tool to solve.

**This is an independent, committed-tool re-verification of
`w2y_report.md` §3's own claim** ("Zero movers, zero asymmetric rows … on
every stream at every step") — a second instrument, built from scratch
against the brief rather than against w2y's own driver, agreeing with it
exactly on both the identity result and the reach numbers.

## 4. Validation 3 — three scratch sabotages, each isolated and reverted

Each edit made, rebuilt, swept against a saved pre-edit binary (copied out
to `/tmp/bsweep_sabotage/clean_pcrec` before any edit), reverted, rebuilt
again to confirm the SOURCE diff is empty — never committed. `git diff`
over the whole tree is empty at the start of §4.1 and after every revert
below.

### 4.1 `.c` streams: the header comment (`emit_pattern_comment`, `src/gen/emit_dfa.c:94`)

Edit: `"/* Generated by pcrec. Pattern: "` → `"/* [BSWEEP-SCRATCH]
Generated by pcrec. Pattern: "` — the one line both DFA- and VM-engine
emitters call to open every artifact, unconditionally. Run TWICE: once
against the tool's first cut (composition undercounted, §1.3) and once
after the composition-arm fix landed — both below, since the difference
between the two composition rows is itself a confirmation of the fix
(72 → 96, exactly the artifact-count delta the fix corrected generally).

**MEASURED (first cut):**

| stream | movers | reach | asymmetric |
|---|---:|---:|---:|
| corpus argv, `.c` default engine | **3,517** (= reach, every producing row) | 3,517 | 0 |
| corpus argv, `.c` `--engine=vm` | **3,518** (= reach) | 3,518 | 0 |
| corpus argv, `--emit-ir` `--engine=vm` | **0** | 3,518 | 0 |
| composition | **72** (= artifacts, every one reached) | 250 | 0 |

**MEASURED (after the composition-arm fix):**

| stream | movers | reach | asymmetric |
|---|---:|---:|---:|
| corpus argv, `.c` default engine | 3,517 | 3,517 | 0 |
| corpus argv, `.c` `--engine=vm` | 3,518 | 3,518 | 0 |
| corpus argv, `--emit-ir` `--engine=vm` | 0 | 3,518 | 0 |
| composition | **96** (= artifacts, every one reached) | 32 | 0 |

Exactly as required, in both runs: reported on both `.c` streams (every
producing row moves, since the header line is unconditional), NOT on the
`--emit-ir` stream (that render path never calls `emit_pattern_comment`),
and — an honest, expected overlap the brief's wording does not forbid —
also on composition, since a composed target's `.c`/`.h` pair is built by
the exact same emitter code path; the fixed run's composition movers
count (96) equals its own artifact count exactly, as the first cut's (72)
did against ITS artifact count, confirming the fix changed only WHICH
files are compared, never the mover LOGIC. Reverted after each run;
`git diff src/gen/emit_dfa.c` empty; rebuild's emitted `.c` text
(spot-checked on the pattern above) matches the pre-edit text exactly.

### 4.2 `--emit-ir` only: `vm_render_listing`'s header (`src/gen/emit_vm.c:8480`)

Edit: `"; pcrec VM program listing (DD-8; …)"` → `"; [BSWEEP-SCRATCH] pcrec
VM program listing (DD-8; …)"`. `vm_render_listing` fires only inside
`if (cx->want_ir)` (`src/gen/emit_vm.c` ~line 11850) — `want_ir` is set
only by `--emit-ir`, never by an ordinary `.c` or composition compile, so
this line is structurally unreachable from the other three streams before
any measurement.

**MEASURED** (run before the composition-arm fix landed; unaffected by
it either way, since this edit's mechanism has nothing to do with
`sweep_composition`'s per-file rc/name-set logic — the composition row's
`reach=250` reads the FIRST cut's semantics, `movers=0` would be identical
under the fixed one):

| stream | movers | reach | asymmetric |
|---|---:|---:|---:|
| corpus argv, `.c` default engine | 0 | 3,517 | 0 |
| corpus argv, `.c` `--engine=vm` | 0 | 3,518 | 0 |
| corpus argv, `--emit-ir` `--engine=vm` | **3,518** (= reach, every listing) | 3,518 | 0 |
| composition | 0 | 250 | 0 |

Exactly the required shape: `--emit-ir` only. Reverted; `git diff
src/gen/emit_vm.c` empty; the listing text (spot-checked) matches pre-edit.

### 4.3 Composition arm only: `vm_splice`'s DELIVER loop (`src/gen/emit_vm.c:7583-7590`)

Run AFTER the composition-arm fix (§1.3), against the fixed tool, so its
composition population reads 32/96 throughout.

`vm_set`'s own role-string argument to this loop never reaches `.c` output
(§1.1), so perturbing IT would be invisible to every stream this tool
compares, including composition. Instead: one `sb_puts(v->b, "/*
[BSWEEP-SCRATCH-DELIVER] */\n");` inserted as the loop's first statement —
text that lands in the emitted `.c` ITSELF, and only when `deliver_n > 0`,
which is written exclusively by `src/parse/rxt_compose.c` and reachable
from no argv pattern.

**MEASURED:**

| stream | movers | reach | asymmetric |
|---|---:|---:|---:|
| corpus argv, `.c` default engine | 0 | 3,517 | 0 |
| corpus argv, `.c` `--engine=vm` | 0 | 3,518 | 0 |
| corpus argv, `--emit-ir` `--engine=vm` | 0 | 3,518 | 0 |
| composition | **4** | 32 | 0 |

Exactly the required shape: composition arm only, zero reach anywhere
else — direct, measured confirmation that the DELIVER mechanism really is
unreachable from any argv pattern, not merely believed to be (w2a §2's own
"MEASURED REACH, not assumed" discipline, one commit over). The four
movers are surgically exact: `compose_delivers.rxtin::user.c` (its one
delivering target) and `deliver_forms.rxtin::flatcall.c` /
`::selfcall.c` / `::sitecall.c` — its three delivering call forms —
while `deliver_forms.rxtin::plaincall.c` (`deliver_n == 0`, the loop body
never runs) is UNTOUCHED, the cleanest possible negative control inside
the very fixture the mechanism lives in. The diff hunk in each mover is
one line downstream of the inserted comment (a `..._VM_PROGRAM_BYTES`
size macro shifting by the comment's own byte count), not the comment
line itself — `first_diff_hunk`'s one-hunk window found the nearest
difference to the file's OWN size-stamp macro rather than the literal
insertion point, which is still a correct mover detection, just not a
literal echo of the edit. Reverted; `git diff src/gen/emit_vm.c` empty.

### 4.4 Final clean state

`git status --short` after all three reverts: only this report and the
already-committed script/docs changes from earlier in this branch — no
residual edit under `src/`. `make strict CC=gcc-16` clean.

