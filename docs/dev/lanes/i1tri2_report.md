# i1tri2 — triage of I1's red `make test` (job 611), round 2 (lane report)

Lane i1tri2 (opus), 2026-10-21, continuing `lane/i1build` from `9c28ed624`.
Brief: diagnose and fix the eight red sections of queue job
`611-i1build-maketest` (test-codegen, test-compound, test-cpset-structure,
test-encoding-checks, test-memfn-arch, test-memfn-finder, test-partlayout,
test-startset), say why round 1's codegen and cpset fixes did not hold, and
re-queue the chain. Rulings file `i1tri2_rulings.md`: empty at every
checkpoint (no entry applied).

## 0. Premise

`scripts/verdict` on 611's `job.log.make` names exactly the eight sections
(premise holds); 611 ran to completion (`perfrun: DONE rc=2`,
`class=RED-REAL`). No red is load contamination, and none is caused by the
branch being behind main: main was NOT merged into the branch.

Why round 1's two "fixed" sections were still red: both were later round 1
moves, not undone fixes. test-codegen: round 1 retargeted `body()` to
`rx__find`, which (a) made OS-1's entry-signature grep read the body instead
of the entry and (b) gave OS-0b's two-engine fixture an engine B (`^a|b`,
DFA attempt route) whose `__find` is `static noinline`, a head the rename
sed did not strip. test-cpset-structure: round 1's fix 6 made
`<p>_iter_buffers`' comment non-essential AFTER the I1 re-record of the
EMITTED_BYTES manifest, so all twelve rows moved by exactly its 145 bytes.

## 1. Fix-by-fix

| # | section / check | diagnosis | fix | commit |
|---|---|---|---|---|
| 1 | codegen OS-1 entry signature | STALE (round 1's own retarget): the grep read `casehot.body`, now `rx__find`'s | the grep reads the artifact `casehot.c` (the definition head ends `)$`, so the prototype does not match) | b0d11cc6a |
| 2 | codegen OS-0b two-engine fixture (2 FAILs) | STALE: engine B's `__find` is `static __attribute__((noinline))` (attempt route); the sed stripped only the `always_inline` head, so `rx_search_b` was a static definition after an extern declaration | the sed strips both heads | b0d11cc6a |
| 3 | cpset-structure [3] manifest | LEGITIMATE MOVE: twelve EMITTED_BYTES rows -145 = the two-line `iter_buffers` comment round 1 made non-essential; nothing else moved | rows re-recorded, history paragraph added | b0d11cc6a |
| 4 | memfn-arch C4 class 6 | LEGITIMATE: I1's `run_residual_twins.sh` parses `R_X86_64_PLT32|PC32` out of objdump, the same use `run_scan_edge_dispatch.sh` already has allowed | one allowlist row (count 1) | b0d11cc6a |
| 5 | memfn-finder `run_presence.sh` [pr8] (8 FAILs) | STALE: both engines' presence verdict and first attempt now live in `rx__find` (DFA: `_search` is the wrapper; VM: `_search_run` is range test + guard) | `order_reason`/`plant` read `int rx__find(const unsigned char` | b0d11cc6a |
| 6 | partlayout object, witness `split` (`^\s+|\s+$` under `--part-layout=compound:*`) | **REAL I1 DEFECT (a)**: the compound shell's `rx__find` is `always_inline`, so its parts are called from `_search` AND `_next`, but `pl.owned_inline` never got the FIND bit: the part table counted 1 caller and held part q at P3 | `emit_search_head` sets `owned_inline |= FIND` where it writes `always_inline` on `__find` (A1's owner shape) | 94a5c4d50 |
| 7 | partlayout object, same witness | **REAL I1 DEFECT (b)**: a label-table `__find` (attempt route, `noinline`) still set the job-wide `pl.uncopyable`, so part f (subject `rx__f_search`, now a copyable wrapper) was held at P2 | `emit_attempt` sets `uncopyable` only when the label-table body is not a `__find` | 94a5c4d50 |
| 8 | partlayout census writers.tsv | LEGITIMATE: I1's new attribute writers (`__find` inline/noinline, `__step`/`__step_own`/`__retry`/`__step_deep`, `_next`'s and the twins' `noclone`, the retry machine's state helpers) | A3 and A6 widened, seven `I1` rows | 94a5c4d50 |
| 9 | compound B0 (`[byte]` 550, `[utf8-check]` 1659, `[utf8]` 559 failures) | **REAL I1 DEFECT (c)**: a STATIC (kept) residual entry is "its twin alone" (enc.c's own rule) but `pcrec_enc_emit_decls` still wrote `static size_t rx_<name>(...)`, defined nowhere: `-Werror` "declared static but never defined" (export-search under `-futf-check`), and B0's keep stub named `rx_next_pos`, which no longer exists | `pcrec_enc_emit_decls` writes no `stat` entry (enc.h doc says so); B0 maps a kept residual to its twin `rx__<name>` where the plain object has that local symbol | 94a5c4d50 |
| 10 | compound E0 fixture (14) + re-seed population (~110) | STALE (predicted by i1build §4): a DFA body's call sites are `find`'s (`rx__find`), a VM `search_run`'s are in its loop `rx__find`, residual calls name the twin | fixture rows re-pinned (from/site/count read off the emitted C), `c_name('find')`, `entry_body` adds `rx__find` to a VM `search_run` | 94a5c4d50 |
| 11 | encoding-checks DD12a(i) (5 FAILs: 231 strict FINDINGs, K50 class collapsed, `var_valid_call` never excised) | STALE (predicted): (a) an out-of-line entry's encoding-owned body is now the twin `rx__<name>` (SIG_RE matched only `rx_<name>`, now the forwarder); (b) `rx__bind_checks` + its call in `rx__enter` exist only where the K50 prologue has text; (c) the var_valid call is `rx__var_valid(`; (d) the VM retry writes K73's rule on `ctx.pos` | twins excised with their guarded-attribute/`static` lines (key = entry), forwarders under `forwarder`, new region `bind_checks`, both regexes widened | ca3b0bfc6 |
| 12 | startset [vm-movers] forced | LEGITIMATE: I1's new corpus file `tests/findall/global.rxt` adds 13 forced-VM movers (manifest rows never added) | see §3 | (§3) |

No ABI shape, entry or I1 design element changed. Fixes 6, 7 and 9 are in
I1's own code under the I1 build go; none moves a default-request byte
(T0 has no marks; `stat` is 0 under the default request; checked on the
compound witness, default and `-e utf8 -futf-check`).

## 2. Validation done here (direct, single-process unless noted)

- `run_codegen_tests.sh` (the file test-codegen runs): 331 passed, 0 failed
  (before fixes 6/7/9; those move no default byte).
- `run_cpset_structure.sh`: 29/0. `run_arch_blind.sh`: 17/0.
  `run_presence.sh`: 24/0 (pr8 6/6, negative 6/6).
- partlayout: the scratch attribute census (`run_partlayout.py`'s own
  `attributes()` over 16 DFA/VM/hybrid/compound/utf8/`-futf-check`/vars
  artifacts): only `P_vars_resolve` unlisted, pre-I1 and outside the census
  population. The split witness now stamps `compound=inline` /
  `compound=shared` with both parts laid out.
- compound B0: `check_one` over 5 witnesses x 3 arms (45 cells): 0
  failures. E0 fixture half: 10 rows, 0 failures; population half on 8
  hybrids: R3 iff two `rx_prefilter(` sites.
- encoding-checks: `excise()` on 9 pairs: strict pairs compare equal;
  nullable pairs are data-only (the K50 class).
- `scripts/m6read_check_sab_anchors.py`: 891 sabotages, all 922 anchors
  resolve after the src edits.
- NOT run here: the five multi-process sections end to end, `make strict`,
  the full suite. They are job 609's and 612's.

Box note: kit job `575-kit-adatwin` (a timing window, quiet gate) held the
box from 20:37. The direct runs above were single-process but some ran
during that window before its quiet gate (the gate read load1 1.32 when it
passed); report this to the kit if its numbers look off.

## 3. test-startset

PENDING at this commit, see STATE AT HANDOFF.

## 4. Ids and proposals

No sabotage, D or K ids used. Proposal for the manager: the partlayout
P2 population (`p2:` line, floor 35, 67 at 611) may shrink now that a
compound part's subject is copyable (fix 7); if job 609 reads it below the
floor, that is fix 7's move, not a regression.

## STATE AT HANDOFF

PENDING.
