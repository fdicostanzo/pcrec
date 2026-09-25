# varfollow — [VAR] MVP follow-ups

Lane `varfollow`, sonnet, 2026-09-25, branch `lane/varfollow` from
`aa9e8ed4`. Charter: `docs/dev/lanes/varmvp_report.md` §0.2/§0.3/§5/§6,
`tests/vars/gen_corpus_plan.md` §6, D121 + addenda, `docs/design/
variables_pattern.md`. Four items, no code under `src/`/`cli/`/`lib/`
touched.

## 1. Design-note debt (D80: "report, then note")

Two of the five sentences `varmvp_report.md` recorded as "did not survive
the build" were report-only debt — the notes themselves still said the
wrong thing. Both are now edited in place, house style (correction
recorded inline, not silently rewritten):

- `docs/design/variables_pattern.md` §3 — the paragraph proposing that
  `${` resolves against the shipped bare `$` row by SR-9's tail
  arbitration is corrected: `pcrec_registry_find`/`pcrec_ext_gate` are
  never called with `RK_BARE` at all, so nothing ranks anything. `${` is
  recognised directly in `p_atom`, gated by `pcrec_feature_enabled
  (FEAT_VARS)`, exactly the shape `\Q`'s `FEAT_QUOTING` gate takes — the
  `${` `RegRow` exists for the dump and for the D67 `forces_registry`
  stamp, not for arbitration. Matches `src/parse/mod_vars.c`'s own header
  comment, which already carried this correction in code but not in the
  design note.
- `docs/design/variables_common.md` §4.1 — "with the module off today's
  parse stands in full" contradicted `variables_pattern.md` §7's shipped
  refusal table. Corrected: a module-off `${` is a NAMED REFUSAL
  ("requires module 'vars'"), per D34 ruling 5's general rule (recognisers
  are always live, production is gated) — not a fall-through to `$`'s
  ordinary end-of-line-assertion parse. The collision-rule argument
  (§0.2's zero-population proof) is unchanged either way.

`docs/design/CLAUDE.md`'s `[VAR]` entry is updated to say these two are now
edited in, and to list the three sentences that remain report-only per the
same D80 rule (§2.5's UNREACHED prediction, §5's under-priced driver
estimate, the roadmap's understated MECH-M1 wording) — those are historical
claims about what the build found, not standing design text, and are left
as the report records them.

Grepped `docs/spec/` for a missing caller-observable fact: none — `docs/
spec/vars.md` §6 already states the module-off refusal correctly; the
debt was in the design notes' own reasoning, not in the contract page.

## 2. Census plan cells (`gen_corpus_plan.md` §6)

Both OWED items closed, with one correction to the plan's own accounting
found while closing the first:

**The state×operator grid.** The plan said 16 of 18 covered with `${v+w}`
and `${v:+w}` SET-and-non-empty missing. Re-counting the shipped corpus
against the full grid (`${prefix}` SET lives in `basic.rxt`, not
`unset.rxt` — the plan's own file attribution undercounted by one place)
lands on 16 of 18 too, but names the WRONG pair: `${v:+yes}` already had a
SET-and-non-empty cell (`var v "anything"`, `unset.rxt:96-100`); the cell
genuinely missing beside `${v+w}` was the bare-minus `${v-w}`'s. Added
both real gaps to `tests/vars/unset.rxt` (`${v-dev}` SET → "prod" not the
word; `${v+yes}` SET → fires, mirroring the existing `:+` SET cell) and
corrected `gen_corpus_plan.md` §2/§6 to name the actual pair. Grid is now
18/18.

**The lookaround pair.** Added to `tests/vars/basic.rxt`: `(?<=${v})x`
(refused — `pcrec_cwmax` answers unbounded for `A_VAR`, joining `A_BREF`'s
own arm, so `mod_lookaround.c`'s fixed-width rule refuses exactly as it
does for a backreference) and `^a(?=${v})bc$` (an ordinary match, no width
rule). Both verified against the shipped binary before landing (`build/
pcrec --features vars,lookaround`) and via `tests/harness/run.sh` on an
isolated fixture before being added to the real corpus.

Re-pinned in the same change: `tests/rxtsource/run_rxtsource_tests.sh`'s
`CENSUS_FILES`/`CENSUS_BLOCKS`/`CENSUS_LINES` and `RUNSH_*` (+0 files, +4
blocks, +7 lines — 3995→3999 blocks, 29113→29120 lines; verified by
running the file's own awk census standalone against the three `tests/
vars/*.rxt` files: 45/83 against the prior 41/76). **`C3_*` pins are NOT
re-pinned**, per that file's own 2026-09-08 note — they are box-sensitive
on darwin and owed from a Linux/10.46 run; the section's own `RECORD` line
confirms this box's python (3.9) already reads a documented delta against
the pinned 3.14 reference, unrelated to this change.

`tests/vars/CLAUDE.md` updated (`basic.rxt`/`unset.rxt` entries) and
`gen_corpus_plan.md` §2/§6 mark both items CLOSED with the correction
recorded at the site.

## 3. New plan.md row: `[K50-DD12AI-MANIFEST]`

Filed `STATE:not-started`, right after the `[VAR]` row in `docs/dev/
plan.md`. Facts drawn from `varmvp_report.md` §0.0/§0.0a (the fuller
account) and cross-checked against `docs/dev/dev_journal.md`'s 2026-09-23
entries (77th/78th sessions), which restate the same facts with no
additional detail: DD12a(i) (`tests/codegen/run_encoding_checks.sh`'s
hot-loop shape identity) had compared ZERO pairs since D118 retired
`--source` (a bare operand now means a file, so the instrument's `pcrec
--features all -e byte -p rx -o rx.c -- <pattern>` call has read "not an
existing file" ever since); reviving it to verify the M6 seam-pair rename
found three `[K50]` startpos-manifest reds (`tests/codegen/manifests/
k50_gate_refinement.txt`'s "gate-refinement class"), all with no
relationship to variables: `startpos_attempt` never excised; two manifest
rows STALE (first: `\z`); five pairs entered the gate-refinement class
with no manifest row (first: `(?:\Gab)+`). The row states the manifest's
own rule verbatim ("re-derive deliberately, never delete to go green")
and names the trigger (the next lane touching K50's boundary-gate
machinery, the eqclasses refinement, or the manifest itself for any other
reason).

**Reproduced live rather than trusted forward** (`bash tests/codegen/
run_encoding_checks.sh` at the default `ENC_MAX_BLOCKS=250`, backgrounded,
completed) — and the fresh run does NOT read three reds, it reads FIVE:
`checks passed: 10 / checks failed: 5`, not the report's `failed: 1`
figure (that number is the pre-revival, `PAIRS=0` state reproduced at the
branch point — a different run answering a different question). **The
three named above are unchanged and are three of the five.** The other
two are NOT K50-startpos-only in any way this lane could confirm and are
flagged separately in the plan.md row rather than folded into this
charter's three: (4) the manifest's own 11-row `#UNDECLARED`-form exact-
match list no longer matches (4 of 11 reached, 77 unique patterns in the
strict-diverging bucket, first mismatch `(?:a\K)*ab`); (5) 102 of 244
strict-identity pairs differ outside every excused region, and the
printed FINDING lines are dominated by `RX_END_WINDOW`-stamped anchor
patterns (`\A`, `\z`, `\Z`, `b\Z`, `b\z`, `b$`, …) — every one a shape
[OPT-ENDWIN] (delivered 2026-09-22, one day before this instrument was
revived) touches. **This looks like the identical shape as the M6-rename
finding one lane over — a dead check missing a landing — but for
[OPT-ENDWIN] instead of the seam-pair rename, and it was never seen
because DD12a(i) was still `PAIRS=0` when [OPT-ENDWIN] merged.** Not
diagnosed further here — no `src/` access in this lane's charter, and
root-causing an emitter interaction is outside a docs-only follow-up
lane's time box. Full detail, exact FAIL text and the flag for a fresh
triage lane: `docs/dev/plan.md`'s `[K50-DD12AI-MANIFEST]` row, its
"RE-DERIVED, NOT ASSUMED" paragraph. Log at `/tmp/enc_checks.log` on this
box if still present; not committed (session scratchpad).

**This is the one finding in this lane worth flagging to the manager
directly rather than leaving to be read out of the plan row**: items 4
and 5 touch DD-12(7)'s own architectural invariant (no encoding
conditional reaches the hot path) and were not anticipated by this
lane's brief or by `varmvp_report.md`. See the handback message.

## 4. VE_VAR trigger confirmation

`plan.md`'s `[VAR]` row already said "VE_VAR --emit-ir event (D77)" in its
OWED list but did not restate what the trigger IS. Added one sentence
naming it explicitly, from `varmvp_report.md` §6: the first `--emit-ir`
consumer that needs to see which expansion a program point reads, most
likely M9's (the replacement side's) template rendering. `VE_VAR` stays
NOT BUILT — nothing under `src/` touched.

## Validation

- `tests/vars/run_vars_tests.sh`: corpus 83/0 (up from 76/0), oracle 67
  agree / 0 disagree (up from 61/0), both arms PASS.
- `tests/rxtsource/run_rxtsource_tests.sh`: 214 passed / 0 failed / 1
  recorded (the pre-existing, box-sensitive C3 python-version record —
  unrelated to this change). Census reconciles at 216 files / 3999 blocks
  / 29120 lines. Run with `PCREC` as an ABSOLUTE path — a relative one
  produces a spurious `timeout: failed to run command` FAIL in one
  fixture check that re-invokes the binary from a different cwd; not this
  lane's defect, just a footgun for whoever runs this file by hand.
- `make strict` and the full `make test` are OWED — not run from this
  lane; see the manager's slot queue (this lane held slot #2, behind
  `varland`'s slot #1) for when to run them. Targeted validation above
  covers every file this lane touched.

## Files touched

`docs/design/variables_pattern.md`, `docs/design/variables_common.md`,
`docs/design/CLAUDE.md`, `tests/vars/unset.rxt`, `tests/vars/basic.rxt`,
`tests/vars/gen_corpus_plan.md`, `tests/vars/CLAUDE.md`, `tests/rxtsource/
run_rxtsource_tests.sh`, `docs/dev/plan.md`, `docs/dev/lanes/CLAUDE.md`
(this entry), `docs/dev/lanes/varfollow_report.md` (this file).
