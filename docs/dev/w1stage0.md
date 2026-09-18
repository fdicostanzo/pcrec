# [REVW.1] WAVE 1 STAGE 0 — the emission-kit precondition stage

Lane `w1stage0` (sonnet, 2026-09-17/18), against `main` at `272bf970`.
Charter: `docs/dev/reviews/lens_reports/lens10_emission_kit_charter.md`
STAGE 0, plus EP2's two additions in `emitvm_second_pass.md` §5/§7 (the
`irsb` byte-neutrality arm and the listing-reach census). Manager synthesis
`docs/dev/reviews/2026-09-17-code-review.md` §3 wins on any disagreement
with the charter, per that document's own rule — no disagreement was found.

STAGE 0 IS NETS + MEASUREMENT ONLY, per the charter and per this lane's
brief: no kit primitives, no emitter interior refactoring. Everything below
is a new instrument or a new committed baseline; nothing under
`src/`/`cli/`/`lib/` moved.

---

## 1. The long-prefix full-corpus sweep (deliverable 1)

**Why.** The charter's F3b (§4.2): the tree's only long-prefix control
(`tests/cli/run_cli_tests.sh` case3) compiles the pattern `a` at a 60-byte
prefix — a trivial DFA artifact reaching essentially none of `emit_vm.c`'s
40+ literal-sized scratch buffers. Stage 3 (a future wave, not built here)
retires those buffers behind `sb_fragf` and needs a control that actually
reaches the population it moves, at the legal prefix boundary
(`PCREC_MAX_PREFIX_LEN` = 60, `src/core/limits.def:133`).

**What was built.** `tests/codegen/run_longprefix_sweep.sh` +
`docs/dev/w1stage0_evidence/longprefix_sweep.py` (dialtrain_byteid's own
`--list-source`-decode methodology). For every `pattern`/`pattern-esc`
block across the whole corpus: compile at `-p rx`; compile at `-p
<60 x 'a'>`; and, only when the 60-byte pcrec compile succeeds,
gcc-compile the emitted `.c` under the harness's own GENCFLAGS
(`-O1 -std=gnu11 -Wall -Wextra -Werror`). NOT wired into `make test`
(`run_object_neutrality.sh`'s own precedent for a heavy, opt-in tool):
every pattern is compiled twice by pcrec and once more by gcc, roughly
double `test-corpus`'s own compile cost.

**The tripwire.** The wrapper script cross-checks its own row count against
`tests/rxtsource/run_rxtsource_tests.sh`'s independently-derived
`CENSUS_BLOCKS` pin (grepped live, never hand-copied — a second hand-copy of
that number is exactly the kind of drift `docs/dev/learnings.md` §3 warns
about), and hard-fails naming both numbers on any mismatch —
`tests/size/check_size_tripwire.sh`'s unpinned-max-guard shape, applied to
row count instead of to a byte ceiling.

**MEASURED, full corpus, 3,938 pattern lines / 211 files (row count == the
census pin exactly):**

| | count |
|---|---|
| total pattern lines | 3,938 |
| `rx_ok` (compiles at `-p rx`) | 1,500 |
| `p60_ok` (also compiles at the 60-byte prefix) | 1,499 |
| `p60_gcc_ok` (the 60-byte artifact gcc-compiles clean under `-Werror`) | 1,499 |
| pcrec-refused-at-60-only (`rx_ok` & `!p60_ok`) | **1** |
| GCC ANOMALIES (pcrec accepted the 60-byte artifact, gcc did not) | **0** |

**The one `rx_ok`/`!p60_ok` row, read by hand, is NOT a K38 recurrence.**
`tests/base/k18_cost_gates.rxt`'s
`((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,6}(){2,3}){1,2}){2,3}` — a
deliberately pathological witness already sized to sit near
`PCREC_MAX_EMIT_BYTES` — refuses at the 60-byte prefix with `pcrec:
pattern too large: 624083 bytes of emitted code (limit 500000)`. Longer
identifiers under a 60-byte `-p` inflate every emitted symbol in an
already-huge artifact; this is the SIZE CAP working as designed, not a
buffer-truncation miscompile. **Zero rows show a gcc-level failure on code
pcrec itself accepted** — the sharper signal, and the one the charter's own
"a bug filed today, before any refactor" sentence is about — so this stage
finds **no live K38 recurrence** at this wave's branch point.

**Committed baseline:** `docs/dev/w1stage0_evidence/longprefix_baseline.tsv`
(3,938 rows) + `.../longprefix_sweep.log`. This is what a future stage-3
lane diffs its own post-refactor re-run against to claim byte-neutrality
reaches the population this sweep exercises — 1,499 patterns, including
the tree's own largest emitted artifacts (`k18_cost_gates.rxt`,
`counterk.rxt`, the `{m,n}` boundary families), which is a materially
different reach than the pattern `a`.

**abi verdict: NOT an abi event.** Nothing under `src/`/`cli`/`lib/`
touched; no emitted scaffolding moved.

**Rollback:** delete the TSV, the script, and the wrapper; nothing else
depends on them.

---

## 2. The irsb byte-neutrality arm (deliverable 2, EP2's addition)

**Why.** `emitvm_second_pass.md` §1/§5 (EP2): `vm_render_listing` writes
`&job->irsb` — the `--emit-ir` listing — a stream NONE of the four standing
`.c`-artifact byte-identity gates (nor the full-corpus emit-diff above)
ever compares. `tests/codegen/run_ir_listing.sh` is the only existing
comparator for it, and it asserts DERIVED FACTS (label sets, push/resume
pairs, slot writes) rather than the listing's own bytes — so an emitter
interior move in a future wave that changes only ROLE-TEXT WORDING (a
comment, in effect) would pass every existing check while moving `irsb`
bytes with nothing to catch it.

**What was built.** A new BYTE-NEUTRALITY block appended to the existing
per-pattern loop in `tests/codegen/run_ir_listing.sh`, reusing that script's
own fixed 11-pattern `PATTERNS` population (already chosen, per that
file's own comment, "so every emission path that can produce a listing
event is represented"). Per pattern, it diffs the freshly captured
`--emit-ir` listing byte-for-byte against a COMMITTED baseline file
(`tests/codegen/manifests/ir_listing_baseline/<md5>.ir`, one per pattern,
captured at this wave's branch point via the new opt-in
`CAPTURE_IR_BASELINE=1` mode). A missing baseline is a hard FAIL naming the
file to capture — never a silent skip (the K35 shape: an absent baseline
must not read as "no drift found").

**Pins the OUTPUT, not the mechanism (D108).** The comparison is the
listing's raw bytes end to end; no section is parsed and no call structure
is assumed, so the arm stays valid across the future walk→event→render seam
the kit is chartered to become — it will simply see different bytes if that
seam changes what the listing SAYS, and nothing about the arm's own shape
constrains how the seam is built.

**Validated, both directions**, on the current tree (93 checks total across
the whole file, including the 11 new BYTE-NEUTRALITY rows):

- Clean run: 93/0.
- A planted single-byte drift in one pattern's baseline: fails exactly that
  pattern's own row (`checks passed: 92 / checks failed: 1`), naming the
  file and the first differing bytes; the other ten rows stay green.
- A baseline file moved aside (simulating a not-yet-captured pattern):
  fails that pattern's row with the "no baseline" message; restored, the
  suite returns to 93/0.
- Sabotage row **S258** (`tests/mech/sabotages/S258_ir_role_text_drift.sh`,
  the highest S-id on `main` at branch time was S257): rewords one word of
  `vm_alt`'s alternation-entry role text (`"alternation entry (%d
  branches)"` → `"alternation ENTRY (%d branches)"`) — an edit that moves
  `irsb` bytes and moves NO `.c`-artifact byte the four standing identity
  gates would see. **DETECTED** after committing the arm (mech sabotage
  trees are built from `git archive HEAD`, so the row necessarily reads
  UNDETECTED against any commit that predates the arm's own commit — see
  §4 below for the two-step validation this forced).

**abi verdict: NOT an abi event.** The arm reads emitted text; it writes
none. `run_ir_listing.sh`'s own existing checks are unaffected (all
pre-existing PASS lines unchanged).

**Rollback:** delete the new block, the `manifests/ir_listing_baseline/`
directory, and sabotage row S258; the rest of `run_ir_listing.sh` is
untouched by this change.

---

## 3. The listing-reach census (deliverable 3, EP2's addition)

**Why.** `emitvm_second_pass.md` §7 (ADDENDUM 2), the one thing EP2 named
as wanting measured before wave 1 starts: does `run_ir_listing.sh`'s fixed
population actually REACH L8's rung emitters (`vm_alt`, `vm_cursor_rep`,
`vm_rev_emit`, `vm_revdet_rep`, `vm_counter_*`, `vm_star`, `vm_rep`,
`vm_atomic`, "the chains"), whose `vm_rolef` role text is the listing's own
content? Nobody had checked the converse of §1's `irsb` finding — whether
`run_ir_listing.sh`'s population reaches the emitters that WRITE to
`irsb`, as opposed to whether anything compares what they wrote.

**What was built.**
`docs/dev/w1stage0_evidence/listing_reach_census.py`, two halves. STATIC:
every `vm_rolef(v, "..."` call site in `src/gen/emit_vm.c` (41 sites,
cross-checked against a plain grep census: 42 `vm_rolef` mentions minus 1
comment reference), attributed to its enclosing function by a backward scan
for the nearest preceding column-0 function head. DYNAMIC: for a given
population, compile each pattern at `--emit-ir` and check whether each call
site's literal FORMAT PREFIX (the text before its first `%` conversion)
appears anywhere in the listing text. PRIMARY census: `run_ir_listing.sh`'s
own `PATTERNS` array, extracted from that file live rather than
hand-copied. SECONDARY (informational, `--corpus` flag): the whole
`tests/**/*.rxt` corpus at default engine selection.

**Instrument caveat, stated because every instrument in this tree states
its blind spot.** A literal-prefix substring match can in principle be
satisfied by an unrelated role string sharing a prefix — checked by hand
against the full per-site table below and not observed — so this is a
census, not a byte-identity gate; a false positive here would only make a
future population estimate optimistic, never certify wrong bytes. Two of
the 41 sites (`vm_counter_phase`'s two calls at `emit_vm.c:5317,5351`) have
an EMPTY literal prefix — their whole format string is `"%lld * ((ptrdiff_t)
%d - slot_values[%d])"`, a pure arithmetic expression with no fixed words at
all — so they are structurally unreachable by this instrument regardless of
population; this is a fact about the instrument, not a coverage gap, and it
is called out rather than silently counted as unreached-and-fixable.

**MEASURED:**

| population | patterns | VM listings produced | sites reached / 41 |
|---|---:|---:|---:|
| PRIMARY — `run_ir_listing.sh`'s 11 `PATTERNS` | 11 | 11 | **27 (66%)** |
| SECONDARY — full corpus, default engine | 3,938 | 368 | **31 (76%)** |

**Both populations miss the same four families entirely**, all 41-site
census: `vm_look_behind` (lookbehind, 4 of 4 sites unreached in both),
`vm_call`/`vm_splice`/`vm_region` (subroutine-call machinery, 3 of 3
unreached in both), and `vm_counter_phase`'s two zero-prefix sites (above,
instrument-blind either way). The PRIMARY population additionally misses
`vm_counter_rep`'s two counter-rung sites and both optional-copy chain
helpers (`vm_opt_chain`/`vm_poss_chain`); the SECONDARY (corpus-wide)
population reaches all four of those, because the corpus contains ordinary
unbounded-count and possessive-chain patterns that `run_ir_listing.sh`'s 11
hand-picked patterns do not.

**Consequence, stated for stage 3's benefit rather than acted on here
(stage 0 is measurement only).** Section 2's new BYTE-NEUTRALITY arm rides
`run_ir_listing.sh`'s existing PATTERNS array, so it inherits the PRIMARY
row's 66% reach — it is a real, sabotage-verified regression net for
everything it DOES reach (27 of 41 `vm_rolef` sites, all of L8's
`vm_alt`/`vm_cursor_rep`/`vm_rep`/`vm_rev_emit`/`vm_revdet_rep`/`vm_star`
families), but a stage-3 lane touching the counter rung, a lookbehind
branch, or subroutine-call emission should not read this arm's green as
proof those paths are byte-neutral on `irsb` — widening `PATTERNS` (or
adding a second population) is a stage-3-scoped decision, not made here, so
the gap is measured and named rather than quietly patched by growing a
fixture array that stage 0's own charter did not ask this lane to grow.

**abi verdict: NOT an abi event; nothing under `src/` touched.**

**Rollback:** delete the two evidence files; nothing depends on them.

---

## Validation summary

- `make -j4 CC=gcc-16`: clean build.
- `bash tests/codegen/run_longprefix_sweep.sh`: PASS (row count matches
  census; 0 gcc anomalies).
- `bash tests/codegen/run_ir_listing.sh` (`CC=gcc-16`): 93 passed / 0
  failed, including the 11 new BYTE-NEUTRALITY rows.
- `bash tests/rxtsource/run_rxtsource_tests.sh`: unaffected by this stage
  (no `.rxt` file touched); smoke-run to confirm — see the lane report for
  the exact count.
- Sabotage S258: UNDETECTED before the arm's own commit (expected — mech
  builds from `git archive HEAD`), **DETECTED** after; see §2 above and the
  lane report §"Rulings received"-equivalent section for the two-commit
  sequencing this forced.
- `make strict`: clean.
- Full `make test`: see the lane report for the async run's log path and
  final numbers.
