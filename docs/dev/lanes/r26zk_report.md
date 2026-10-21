# r26zk — R-26.6 (kit_proof Zk): the REPORT row lands UNROUTED, plus mf_preview

Lane r26zk, 2026-10-21. Branch `lane/memfn-r26zk`, cut from the kit branch
`lane/memfn-r26` @ `6ff4ea64b` (Z1: R-26.1-R-26.5, MF_SITE_ABI 18). Request:
`memfn/docs/requests.md` "## R-26", item R-26.6. Design: `docs/design/kit_proof.md`
rev 2.1 §2.5, §4.3, §7 (Zk; "The harness lever's kit channel"). Frank's build go:
2026-10-21 ("both you and kit please proceed", quoted in the request).

**Verdict: Zk BUILT. No MF_SITE_ABI event (stays 18), no MF_CLASS_V or MF_VOCAB
move, no pcrec abi event, no pcrec caller. Zero artifact movers expected (no pcrec
site states REPORT and nothing in pcrec calls mf_preview); every light check is
green; the nine emit_sweep arms, the mech rows and `make test` are OWED in the
queued job `500-kit-r26zk-heavy` (§6).**

## 0. Questions and findings for the kit manager (none blocks a semantic)

- **Q1 (the widening's type).** F-2 widens the class and field sets to ONE
  `unsigned __int128` (`kit_set`, kit.h). It is GNU C and exists on every 64-bit
  target gcc builds the kit for (x86-64, arm64); it does not exist on 32-bit
  targets. The alternative, a two-word struct, would rewrite every contract
  table's `CM(a) | CM(b)` spelling. Since the kit builds with `-std=gnu11` and
  only for pcrec's 64-bit boxes, I chose the typedef. If the stand-alone kit
  (K3) must build on 32-bit targets, that is the trigger to revisit; the change
  is then local to kit.h (the typedef, CM/FM/MF_ANY, `kit_set_low`).
- **Q2 ("the REQUIRED term's set at d").** Where two REQUIRED terms read the same
  offset (span 0 allows it), I read R-26.3's "proven[d] EQUAL to the REQUIRED
  term's set" as the INTERSECTION of the REQUIRED terms' sets at d (all ones
  where no term reads d). That is what binding plus completeness make true and
  what the host's C14 check can compute. Please confirm.
- **Q3 (no MF_SITE_ABI event).** MF_SITE_ABI is "layout and meaning of every
  struct below". Zk moves no struct, adds no field and changes no field's meaning
  on any art pcrec builds today: a REPORT site is refused on every plain art,
  exactly as at Z1. `mf_preview` is a new ENTRY (B2 added `mf_reach` inside an
  event that also moved layout, so there is no precedent either way). I therefore
  left the number at 18; the memfn.h REPORT text and the include CLAUDE.md
  history say so. If you want the entry counted, it is one event 18 -> 19 with
  the readers Z1 found by grep (§2).
- **Q4 (RPT has no deny row).** The REPORT row moves no byte at Zk, and B1's
  deny is pcrec's FACT deny (`PCREC_NO_KIT_PROOF`, kit_proof §2.2), not a kit
  row. So RPT carries no `options.def` row (`opt` NULL). If B1 wants a kit-side
  OFF arm as well, it is that step's row.
- **F-1 (where RPT sits).** RPT is a slot-FIND row but is LISTED after slot PRES,
  so no earlier row's index moves (`mf_class.pres_row`/`pres_led` carry 1 + an
  index, and pcrec's trace reads them through the listing). Its contract serves
  `site_kind` REPORT alone and every other row's kinds (KD_ALL) leave REPORT
  out, so its place in the walk decides nothing. finder_check.py's "last FIND
  row reads no key" rule now reads RPT (it reads none).
- **F-2 (mf_ask before mf_preview).** `mf_ask` takes a `const mf_art *`, so the
  kit cannot record an ask; an ask made BEFORE `mf_preview` on the same art is
  not refused, and would answer the plain art's decision (a refusal) for a
  REPORT site. kit_proof §7's protocol calls mf_preview at art setup, beside
  mf_reach, before any ask, so pcrec's Z2 meets it; noted, not built (D77).
- **F-3 (what "the kit's choice" is here).** RPT's pick is the composer's own
  first-match form (D2's shape: `fd_nested_walk`), held to EXACTNESS: the row's
  fact `SF_PROOF_EXACT` holds where that form's class proves, at every offset
  in `[MF_PROOF_LO, MF_MAX_FWD)`, exactly the intersection of the REQUIRED terms'
  sets (`kit_report_exact`, compose.c). Where it does not (today: a context item
  wider than one offset stating SATISFIES, r26z1 F-3), the row does not apply and
  the site is refused, never answered with NONE (K96). On the generated REPORT
  sites the walk picks the generic row, the offset-skip function and pf_memchr
  (the forms each site shape already gets), so `foobar`'s REPORT text is its
  run-pinned offset-skip function, as kit_proof §2.4 expects.

## 1. What was built

**F-2 first, its own commit (`18e9840fa`).** kit.h: a class set and a field set
are one `kit_set` (128 bits); `CM`/`FM`/`MF_ANY`, `gate_use`,
`gate_contract.serves` and `gate_verdict` are written in it; `kit_set_low` names
a set's lowest member. gate.c: its set-valued helpers. fields.def: the "space is
full" comments restated. No class or field added there, no contract or verdict
changed: the memfn checks read the same counts as at Z1 (§5).

**R-26.6 (`98c714d7d`).**
- fields.def: the class REPORT (the first past 64), in `site_kind`'s set.
- finder.c:
  - `kind_cl(MF_SK_REPORT)` = CL_REPORT (Z1 mapped it to OTHER); `kind_name`
    knows it.
  - The row RPT: slot FIND, `needs` P, facts SPAN0 | PROOF_EXACT, pick PROOF
    (new form name, "the composer's walk held exact"), routed 0, step
    `R-26.6`, basis DERIVED (from the answer contract), contract `ct_rpt`
    (serves `site_kind` REPORT, `need` REQUIRED, every `ctx`/`absent` class
    its pick's rows serve).
  - `fd_scope` admits a forward REPORT FIND of any form and any span 0.
  - `fd_row_routed(art, r)`: a row decides where routed, or where the art
    previews its step; `fd_route` and `fd_pres` both read it (one mechanism).
  - `fd_previews[]` = { "R-26.6" } and `fd_preview_step`: a step is named only
    if it is in that table and some row's step.
  - `fd_route` takes the selection's gate phases (the exactness fact is asked
    under them) and maps PROOF to `fd_nested_walk`.
- compose.c: `kit_report_exact`; `select_arm` walks a REPORT site only under a
  deciding REPORT row (refusal text names RPT, its step and mf_preview);
  `mf_preview` (refused when the art has failed, twice, after the first
  define, or for a step `fd_preview_step` does not name).
- memfn.h: `mf_preview` (kit_proof §7's text) and the REPORT kind's text.
- `options.def`: untouched, so `mf_opts_check` refuses every spelling.

## 2. Readers (by grep)

- **No number moved**: MF_SITE_ABI 18, MF_CLASS_V 5, MF_VOCAB 4, pcrec abi
  unchanged. The include CLAUDE.md history records "R-26.6 moved no number".
- **The widened sets** (`grep -n 'uint64_t\|1ull' memfn/src/gate.c memfn/src/kit.h`):
  every class/field-set reader is in kit.h and gate.c; the remaining `uint64_t`s
  are MF_D_* deny words. No test reads a set (`proven_check.c` includes kit.h
  and builds unchanged).
- **The finder table's row set** (`grep -rn 'R7w\|ROWS_FLOOR\|FIND_ROWS'`):
  `tests/memfn/rows.tsv` (RPT, reach `pending-site:Z2`, fixture `fd-RPT`,
  control `fd-R7w`), `row_floors.tsv` (RPT `-` / PLACEHOLDER), `run_rows.sh`
  `ROWS_FLOOR` 39 -> 40, `finder_check.py` `FIND_ROWS`, `memfn/docs/finder_history.md`
  (the row's entry). `MF_FINDER_MAX` 32 holds 20.
- **mf_class.pres_row readers** (`src/gen/memfn_sites.c` pcrec_memfn_pres_routed):
  untouched, because RPT is appended after slot PRES.

## 3. The checks (all in `tests/memfn/run_proof.sh`, part `proof` of `make test-memfn-finder`)

- **Family C, extended.** 150 REPORT sites (span 0 of 1..3 REQUIRED SET/RUN
  terms; one or two width-1 context items under either `absent`; the offset-skip
  FUNC shape), each on an art previewing "R-26.6": decided by RPT, `proven[d]`
  EQUAL at every d to the REQUIRED sets computed from the generated MEMBER
  STRINGS (never the input bitset), C-PROOF across the layers on a preview art,
  REFUSED on a plain art naming `site_kind` REPORT, and written to
  `proof_sites.c` for `proof_run.c`, the byte-loop oracle (BIND, PROOF, EXACT,
  COMPL). Every non-REPORT family site renders BYTE-IDENTICALLY on a preview art
  (400/400). Forms reached by the REPORT sites: generic 95, ofsskip 50,
  pf_memchr 5 (floor 2).
- **Family D, new.** mf_preview: accepted control; refused twice, after the
  first define, for seven unnamed steps (R-26.7, R-26.5, B4, B1, "", r-26.6,
  "R-26.6 ") and for no step, each refusal naming mf_preview. Twelve
  `--memfn=` spellings (preview, no-preview, R-26.6, no-R-26.6, mf-preview,
  preview-R-26.6, kit-proof, no-kit-proof, rpt, no-rpt, fd-rpt, no-fd-rpt)
  refused by `mf_opts_check`; no options.def row names the preview or RPT. The
  row's applicability: a REPORT site with a two-offset SATISFIES context item is
  refused on a preview art (the row does not apply); its FAILS twin is served
  by RPT.
- **rows.tsv**: RPT's witness `fd-RPT` (a two-term REPORT site on a preview art,
  signature the shadow's ` row=RPT pick=PROOF`), control `fd-R7w`.

## 4. Sabotage rows (ids reserved by main: S1251-S1256; rulings file entry applied)

Each is `run_proof.sh`'s plant of the same id (FILE@@FROM@@TO), a real row in
`tests/mech/sabotages/`, arm `memfnfinder`, SAB_EXPECT DETECTED, SAB_COUNT 1.
`VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S1251 ... S1256`: "6
definition(s) valid"; `python3 scripts/m6read_check_sab_anchors.py`: 859
sabotages, 889 anchor sites, all resolve. Plants, red then green
(`build/r26zk/light/plants_ids.log`; the unplanted run is green, §5):

| id | plant | red where |
|---|---|---|
| S1251 | mf_preview accepted after the first define (`if (art->nsites)` -> `if (0)`) | D "after the first define: accepted" |
| S1252 | mf_preview accepted twice (`if (art->preview)` -> `if (0)`) | D "twice: accepted" |
| S1253 | accepted for a step the kit does not name (fd_preview_step's table match dropped) | D "unnamed step B4: accepted" |
| S1254 | a `--memfn=` spelling accepted (an options.def row `preview`) | D three checks (two spellings, the no-row check) |
| S1255 | a REPORT site whose proven[d] is not the REQUIRED set accepted (kit_report_exact compares d >= 0 only) | D "two-offset SATISFIES: rendered" |
| S1256 | NONE accepted on a REPORT site: the row drops PROOF_EXACT and replies where it cannot prove | D "two-offset SATISFIES: rendered" |

Two more plants with no id (PROPOSED, if you want rows for them): **ZK6** the
preview leaks (RPT decides on every art) — 152 checks red (A and C's plain-art
refusals); **ZK7** a preview routes nothing — 154 red (C's REPORT sites, D's FAILS
twin). S1255 and S1256 share their one detecting check; the byte-loop oracle cannot
see either (the kit's class stays honest, only equality fails).

## 5. Light checks (cap 4 cores; logs `build/r26zk/light/`)

| check | at F-2 (`18e9840fa`) | at R-26.6 (`98c714d7d`) |
|---|---|---|
| `make strict` | clean | clean |
| `make test-memfn-finder` (part proof included) | 1,959 / 0 (Z1's count) | 2,316 / 0 |
| `make test-memfn-rows` | 244 / 0 | 249 / 0 (RPT's witness and control) |
| `make test-memfn-arms` | 383 / 0 | 383 / 0 (no arm pin moved) |
| `make test-memfn-g2` (quick tier) | 71,217,802 / 0, G2 sites failed 0 | 71,217,802 / 0, G2 sites failed 0 |
| `make test-codegen` | - | 16/16 scripts, no `*** [...test-codegen]` line |
| `run_proof.sh` (standalone) | - | 1,288 / 0 (plain + traced) |
| `run_proof.sh --plants` (14 plants) | - | all RED (`plants_all.log`) |

The emit_sweep arm was NOT run by hand: the box lock was held by
`queue:300-m0build-test` throughout; all nine arms are in the queued job.

## 6. OWED heavy validation (queued, not waited on)

- **Job:** `500-kit-r26zk-heavy` (kit band), source
  `build/r26zk/heavy/500-kit-r26zk-heavy`, adapted from 500-kit-r26z1-heavy; its
  dry run is clean (13 mech rows validated).
- **Runs:** `make -j16`; emit_sweep plain (+dumps), simd, comments, utf8, vm,
  start (against `build/r26zk/sweep/pcrec.ref`, built from `6ff4ea64b`), rwquest
  (`build/r26zk/rwquest_patterns.txt`), variant and trace (`--ref 6ff4ea64b
  --tree-rev` HEAD at run time); ONE `PROCS=4 bash tests/mech/run_sabotage_matrix.sh
  S1221 S1222 S1223 S1224 S1225 S1226 S1251 S1252 S1253 S1254 S1255 S1256 S1083`;
  then `scripts/perfrun --label r26zk -- build/r26zk/heavy/maketest.make.log`.
- **Logs:** `build/r26zk/heavy/<step>.log` per step; the job log
  `worktrees/.boxqueue/{done,failed}/<TS>-500-kit-r26zk-heavy/job.log`.
- **Completion:** `== r26zk heavy: 0 step(s) failed`; nine `emit_sweep: DONE rc=0`;
  `== mech run COMPLETE` in `build/r26zk/heavy/mech.log` with 13 rows DETECTED;
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/r26zk/heavy/maketest.make.log`
  empty, read with its `.perfrun` note.
- **Expected:** zero movers on every stream of every arm (any mover is a finding:
  Zk must move nothing); `make test` green. `--arms start` may show R-25's
  pre-existing manifest miss (`a.{1,5}z`, b3b's DIFFER_PINS row), a known rc 1.

## 7. Charter vs committed

| promise | artifact | state |
|---|---|---|
| F-2: widen the class/field mask as the general mechanism, its own commit, zero movers | `kit_set` (kit.h, gate.c), `18e9840fa` | done (light checks equal Z1's; sweeps OWED, job above) |
| MF_SITE_ABI event only if needed, readers by grep | none needed (Q3); §2 | done (ruling asked, Q3) |
| R-26.6: the REPORT row in fd_rows[], routed false | finder.c RPT | done |
| which form serves REPORT is the kit's (D157) | pick PROOF = the composer's walk held exact (F-3) | done |
| a row that cannot serve every REQUIRED term does not apply (K96) | SF_PROOF_EXACT / kit_report_exact; D two-offset refusal | done |
| NONE is not a legal reply on REPORT | refusal, never NONE; S1256 | done |
| proven[d] EQUALS the REQUIRED set at every d | kit_report_exact; family C's member-string equality (150 sites) | done (host's C14 check is pcrec's, Z2/B1) |
| mf_preview(art, step), harness-only | compose.c, memfn.h | done |
| refused after the first define / twice / unnamed step | family D; S1251/S1252/S1253 | done |
| no options.def row; any `--memfn=` spelling refused | family D (12 spellings + no-row check); S1254 | done |
| on a preview art the kit decides as it will once the step routes | fd_row_routed; family C (REPORT decided by RPT, others byte-identical) | done |
| pcrec does not call mf_preview in Zk | no pcrec source edited | done |
| G2 fixtures in the kit's suite: byte-loop oracle, equality, misuse refusals, spelling refused | run_proof.sh families C/D, proof_run.c | done (they live in `tests/memfn/`, Z1's home for the proof family; movable under `memfn/tests/` if the kit prefers) |
| each plant red then green | §4, `plants_ids.log`, `plants_all.log` | done |
| kit-side sabotage rows | S1251-S1256 written, VALIDATE_ONLY ok; ZK6/ZK7 PROPOSED without ids | done; mech figures OWED (job) |
| zero pcrec movers | no pcrec file touched | OWED measurement: job 500-kit-r26zk-heavy, owner kit manager, trigger the job's end |
| CLAUDE.md for every file whose role changed | memfn/, memfn/include, memfn/src, tests/memfn, tests/mech; finder_history.md | done |
| heavy job queued, report OWED with logs | §6 | queued |

## 8. State at handoff

- Branch `lane/memfn-r26zk`; tip in the handback message. Not merged anywhere.
- Rulings file: last entry applied is main's S1251-S1256 reservation (2026-10-21).
- Scratch (gitignored): `build/r26zk/` (reference tree and binary, light logs,
  heavy job dir).
