# vartriage — TRIAGE of varmvp's five red sections

Lane `vartriage`, sonnet, 2026-09-23, branch `lane/varmvp` (continuing the
delivery, not a separate branch). varmvp's own full `make test` log
(`build/varmvp_make_test.log`) is interleaved output from a non-`-j1`
`make -k` run of `TEST_SECTIONS`, so line-range parsing of that log is
unreliable (confirmed: `test-cli`'s apparent range at the top of the file
carries `test-registry`'s own "registry well-formedness" output). Every
section below was instead reproduced by running its own script(s) standalone
in the worktree, per the brief.

Context: the delivery is the [VAR] MVP pattern half — `${name}` in a
pattern, abi 31→32, the seam pair rename `bref_match`→`span_match` (a
mid-flight M6 ruling, `docs/dev/lanes/varmvp_report.md` §0.0). The lane
re-ran strict/codegen/vars/backrefs/anchors after that rename but not
registry/cpset/cli/assertions — this triage is exactly that gap.

---

## test-cli — STALE PIN, FIXED

**Cause.** `tests/cli/run_cli_tests.sh` case10 hand-maintains a manifest of
the registry rows that "reach no doorway" (RK_BARE: `^`, `$`, `(a)`, plus the
possessive-suffix family) and asserts it against a live `--probe-ask` sweep.
`${name}` joined `RK_BARE` as a fourth no-doorway row (registry.c's own
comment: the `tail` column does not arbitrate this row; `p_atom` recognises
`${` directly, the same way it recognises `$` itself) but the manifest and
its 2×-probe count (16) were never re-pinned.

**Class.** STALE PIN — the row's own `tail`/kind fields say plainly that it
belongs in this set; the check's own arithmetic (one set member, two probes)
predicts the new numbers exactly.

**Diff.** `noroute_expect` gains `'${name}'`; the probe-count pin moves
16 → 18.

**Re-run.** `bash tests/cli/run_cli_tests.sh` → **284 / 0** (was 282/2).

---

## test-registry — ONE REAL DEFECT (FIXED in `src/`) + SIX STALE PINS

### 0.1 `pcrec_construct_built_status` had no arm for `RK_BARE` × `RS_MODULE`

**Cause.** D65's built-status derivation (`src/dump/syntax_dump.c`) forces
every module open and classifies a row by driving its own `syntax` through
the doorway machinery. `RK_BARE` rows have **no doorway** by design
(`internal.h`'s own comment: `pcrec_registry_find`/`arbitrate` are never
called with this kind). Every earlier `RK_BARE` row (`^`, `$`, `(a)`) is
`RS_BASE`, so the exported entry short-circuits to `PCREC_BUILT_NA` before
`built_status_probe` ever runs. `${name}` is the **first** `RK_BARE` row
that is `RS_MODULE`, so it fell all the way into the general doorway arm,
which requires `doorway_route` to recognise the row's `syntax` — and it
never can, by the same "no doorway" fact. Every `RS_MODULE RK_BARE` row
therefore derived `PCREC_BUILT_DEFECT` unconditionally: a registry defect
reported on a construct that is, in fact, built.

**Class.** REAL DEFECT — a genuine classification gap, unambiguous in cause
(confirmed by reading `built_status_probe`'s own dispatch and
`RK_BARE`/`RK_QUANTSUFFIX`'s shared "no doorway" documentation), small in
fix (one new arm, mirroring `RK_QUANTSUFFIX`'s existing one), and
precedented — the row's own header comment in `registry.c` explicitly
anticipates this shape ("RK_QUANTSUFFIX's own precedent applied a third
time"). `pcrec_ast_stamped_by` (`src/opt/atomic.c`), the function the new
arm calls, was ALREADY generic ("the next non-doorway kind gets this arm
for free") and already had an `A_VAR` case — only the caller-side dispatch
in `syntax_dump.c` was missing.

**Fix.** New `if (r->kind == RK_BARE)` arm in `built_status_probe`
(`src/dump/syntax_dump.c`), identical shape to the `RK_QUANTSUFFIX` arm
above it: an ordinary parse at the forced-open gate, classified on whether
`pcrec_ast_stamped_by` finds the row's own node. Also folded `RK_BARE` into
the `setjmp` handler's `PCREC_BUILT_NO` (not `_DEFECT`) branch, symmetric
with `RK_QUANTSUFFIX`/`RF_LEXICAL`.

**No control-shares-source-with-what-it-controls trap here**: the fix adds
a dispatch arm to a function `tests/registry/registry_check.c` calls
independently (via `pcrec_construct_built_status`, the one exported entry,
two callers — the dump and the check), and the check's own population
count moved as a *consequence* of the fix (111 built, up from 110), not as
something the fix could tune to pass.

### 0.2–0.7 Stale pins, all downstream of `${name}`'s registry row existing

Each re-derived from the row's own fields and verified by re-running the
specific check, not asserted from the delta alone:

| pin | file | old → new | why (row fact) |
|---|---|---|---|
| registry row count | `registry_check.c` (2x: the row-count assert + the built-status-population assert) | 138 → 139 | one new row |
| family population | `registry_check.c` | 100/12/50 → 101/12/50 | `${name}` has `family == NULL`, its own family (same shape as `^`/`$`/`(a)`) |
| SR-8 engine capability | `registry_check.c` | qualifying 75→76, wired/built_wired unmoved at 62 | `${name}` is `RS_MODULE`+`VM_ONLY` (qualifies) but `NO_PORT` (can't be wired — same WAVE-F-index-row shape) |
| built-status population | `registry_check.c` | 139=110+12+16 → 139=111+12+16 | `${name}` now classifies `built` (0.1's fix) |
| RK_BARE table→parser loop | `registry_check.c` | assumed every `RK_BARE` row is `RS_BASE` (unconditional `expect_compiles`) | split RS_BASE/RS_MODULE, mirroring the QUANTSUFFIX loop one block above it — `${name}` is `RS_MODULE`, refuses with `"${...} requires module '%s'"` (mod_vars.c's own text) |
| row-ranks / no-ambiguity sweep | `registry_check.c` | both treated "has a non-NULL `tail`" as "arbitrates" | `${name}`'s `tail` ("{") is display-only (registry.c's own comment); excluded `RK_BARE` from both, mirroring the tree's EXISTING `RF_INDEX` exclusion and its stated reasoning verbatim |
| 3 coverage guards | `run_registry_tests.sh` | registry_check 225→226, PC-3 209→210, limits_check 27→29 | one new PASS line each (the row's own check; `check_rows`' generic RK_COUNT iteration; module vars' 2 new `limits.def` rows) — the SECOND READER CLASS this house has named repeatedly (a reader whose text never cites a number still moves with it) |
| compliance doc | `compliance_section.py` + `docs/pcre2_compliance.md` | row-count pin 138→139; doc regenerated with `--write` | mechanical: one new `${name}` row, nothing else moved (diff is 2 lines) |

**Re-run.** `bash tests/registry/run_registry_tests.sh` → **rc 0**, clean.

---

## test-codegen — CONFIRMED: ONLY the expected darwin `nm` red

`make test-codegen CC=gcc-16` → the sole `FAIL:` line in the whole section
is `nm could not read arm_a.o (no rx_search symbol) — no verdict is
evidence here`, the standing pre-existing darwin probe (documented in 29+
other lane reports; not this lane's to fix). Grepped the full log for any
other `FAIL:`/nonzero `checks failed:` line — none. **Nothing changed
here.**

---

## test-assertions — TEST-INFRASTRUCTURE DEFECT, FIXED

**Cause.** `run_endvar_identity.sh`, `run_wordctx_identity.sh` and
`run_mlinectx_identity.sh` each classify the corpus's `pattern` lines with a
small embedded python script that reads the combined pattern file via plain
`open(src)`. Module `vars`' own corpus (`tests/vars/caseless.rxt`)
deliberately carries a raw non-UTF-8 byte in a pattern line
(`^${v:-\xff}$` — the default-value operand's own byte-literal cell, testing
that a `${name:-word}` default may contain an arbitrary byte). That decodes
fine as pattern TEXT inside pcrec, but plain text-mode `open()` cannot read
the line at all — one `UnicodeDecodeError` kills each script before it
classifies a single pattern. Confirmed shared cause: all three failures
carry byte-for-byte the same traceback and the same `open(src)` line;
`run_gstart_identity.sh`, the fourth script in the same `run_group`, reads
the corpus differently and was unaffected — which is why only 3 of 8
sub-scripts in the group failed, not 4.

**Class.** Not a "stale pin" (no number moved) and not a pcrec-behavior
regression (pcrec itself never mis-handled the byte) — a **test-harness
fragility** the new, legitimate corpus content exposed on first contact.
Small, unambiguous fix: the classifier in each script only asks whether
pattern TEXT contains `\z` or a multiline anchor, never decodes it as a
string, so round-tripping the byte through `errors="surrogateescape"` on
both the read and the write `open()` costs nothing. Verified the round-trip
reproduces the exact original byte on write-out (tested standalone before
editing: `open(..., encoding="utf-8", errors="surrogateescape")` read +
write reproduces `b'\xff'` exactly, not a re-encoding of it).

**Fix.** Same three-line change in all three scripts:
`open(src, encoding="utf-8", errors="surrogateescape")` on read,
`open(zout/bout/mout/nout, "w", encoding="utf-8",
errors="surrogateescape")` on write.

**Re-run.** All three scripts standalone: green. Full section:
`make test-assertions CC=gcc-16` → `run_group: 8/8 scripts passed`.

---

## test-cpset-structure — STALE PIN, FIXED

**Cause.** `tests/codegen/run_cpset_structure.sh` CHECK 3's stamp-census
manifest (`tests/codegen/manifests/m5_stage1_stamps.tsv`) was re-pinned for
the abi 31→32 bump in the lane's own `68422ba1` commit (all twelve
`EMITTED_BYTES` rows +1001) — but that commit **predates** the M6
mid-flight ruling (`d93aa931`) that renamed the seam pair
`bref_match`→`span_match`, widening the reference side from two `size_t`
offsets to a pointer+length pair (`const unsigned char *ref, size_t
reflen`). Only the manifest's one backreference-bearing pattern,
`(\w+)\s+\1`, is affected.

**Class.** STALE PIN, verified rather than inferred: built a scratch tree
at the rename's parent commit (`git archive d93aa931^` into the session
scratchpad, `make -j4 CC=gcc-16`) and diffed its `-o -` artifact for
`(\w+)\s+\1` against the current tree's, same basename. The only changed
lines are the `rx_bref_match`/`rx_span_match` declaration, definition, one
call site, `RX_VM_PROGRAM_BYTES` (unrelated — program bytes, not this
manifest's own count), and the loop body operand (`s[ref_start + i]` →
`ref[i]`) — no other manifest row carries a backreference, so none of the
other eleven moved.

**Diff.** `26076` → `26087` (+11).

**Re-run.** `bash tests/codegen/run_cpset_structure.sh` → **28 / 0**
(was 27/1).

---

## test-anchored-match — STALE PIN (eroded cap margin), FIXED

**Cause.** `tests/codegen/run_anchored_match.sh` §6a builds a reference
compiler at `-DPCREC_MAX_EMIT_BYTES=20000` and asserts three witness
patterns drop their optional anchored machine while a fourth, `'ab'` (the
positive control — the cap must NARROW the axis, not disable it), keeps
it. Several same-day landings ([OPTLOOP.1.impl] batches 1+2,
[OPT-PRECHECK-ADMIT], [VAR] itself) each added scaffolding bytes to every
artifact; `'ab'`, the smallest witness, was first to cross 20,000, so the
control started dropping too — "no pattern keeps the unwrapped form" —
while the drop-rung assertion (`dropped >= 3`) kept passing.

**Class.** STALE PIN / eroded margin, same shape `nltriage_report.md`
already named for a sibling check's CPU budget. Re-measured the valid
window by binary search on the cap itself (building the real compiler at
successive `-DPCREC_MAX_EMIT_BYTES=N` and reading the artifact's own
`RX_DFA_MATCH` stamp — more direct and more robust than parsing a
diagnostic's byte count, which the file's own header notes has a
digit-width self-reference): `'ab'` flips `search-filter` → `unwrapped`
between N=20,410 and N=20,420 (its own with-machine size); the
next-smallest drop witness, `'a[bc]d[ef]g[hi]j[kl]m'`, flips the other way
between N=22,650 and N=22,700. `K53_CAP_LO` (15000, a different pair of
witnesses under a full-refusal regime) is unaffected — live-reverified
`'foobarbazqux'` still fully refuses there, quoting 19,665 bytes, well
under that section's own 23,000-byte ceiling.

**Diff.** `K53_CAP_HI` 20000 → 21500 (centered in the (20420, 22700)
window, ~1,080/1,200 bytes of margin either side).

**Re-run.** `bash tests/codegen/run_anchored_match.sh` → **20 / 0**
(was 19/1).

**`tests/anchored/run_anchored_diff.sh`** (the section's other script, a
corpus-wide differential — 3,302 corpus patterns × 18 subjects, 187,758
cells over the whole anchored-entry/capture population): unaffected by
anything in this triage (no cap, no manifest, no registry fact) — run to
completion as confirmation. **7 / 0**, clean.

---

## Validation summary

| section | verdict |
|---|---|
| `bash tests/cli/run_cli_tests.sh` | 284/0 |
| `bash tests/registry/run_registry_tests.sh` | rc 0 |
| `make test-codegen CC=gcc-16` | only the standing darwin `nm` red |
| `make test-assertions CC=gcc-16` | run_group 8/8 |
| `bash tests/codegen/run_cpset_structure.sh` | 28/0 |
| `bash tests/codegen/run_anchored_match.sh` | 20/0 |
| `bash tests/anchored/run_anchored_diff.sh` | 7/0 |
| `make strict CC=gcc-16` | clean |

`test-anchored-match` as a whole (both scripts) is now fully green.

## Rules honored

- Never edited a check to make it pass without stating what it now
  measures — every re-pin above states the DIFF, the DERIVATION, and
  (where feasible) an independent verification (a scratch pre-rename
  build's artifact diff for cpset; a live re-check of the OTHER cap for
  anchored-match).
- The one `src/` fix (§0.1 above) is unambiguous in cause and precedented
  in shape; nothing else under `src/` touched.
- Did not touch the (B) FILEPIN (manager's at merge, per D76/opt5i's
  precedent, already noted OWED in `varmvp_report.md` §5).
- Did not run the full `make test` (the manager's call).
- Did not edit `docs/dev/plan.md` or the journal.
