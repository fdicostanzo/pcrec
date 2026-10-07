# Lane k93tri — triage of lane/k93fix's three Linux reds

Source: Linux `make test` of lane/k93fix 051e4fef (worktree k93-lx, test.log), rc=2: test-rxtsource, test-memfn-stamps, test-startset. Branch lane/k93tri, from lane/k93fix 57b56aa5 (see "Process incident").

| section | failing check | cause | class | fix |
|---|---|---|---|---|
| test-rxtsource | C3 version-invariant pin (verifiable 19365 vs 19232) | tests/recursion/k93.rxt's 133 cells are no-python-expression, so verifiable +133 | STALE PIN (predicted by the lane) | C3_VERIFIABLE 19365, C3_SKIP_NOPYTHON 2116 |
| | C3 version-sensitive pins (SKIP 24417 vs 24281, no-python +133) | same, plus 3 `under pcre2-auto-possess` lines | STALE PIN | C3_SKIP 24417 |
| | C3 DOES NOT RECONCILE (41741 vs census 41738) | k93.rxt holds the corpus's FIRST `under` lines. verify_rxt.py counts each as a skip (reason under-convention); the census awk does not count them as case lines. Not predicted by the lane | STALE PIN / missing accounting term | new pin `C3_SKIP_UNDER=3`, asserted against verify_rxt's under-convention bucket; reconcile is `pass+info+skip-UNDER+timeout-file == CENSUS_LINES` |
| | W23-S7 corpus control: `entry files: ?` | `run.sh --dump tests` under `$TIMEOUT_BIN 120`; the suite ran at box load ~21 and the `entry files:` line never printed. Idle re-run: 24 s, `entry files: 273`, `fragments spliced: 0`. The build was not stale (build/pcrec newer than the commit) | TRANSIENT, load-sensitive (the second load-timeout of the day, after axtri's clskit chunks) | none; green on the idle re-run |
| test-startset | `[vm-movers]` auto 1 / vm 18 not in manifest | the k93.rxt blocks are new VM-hat movers (prefilter-less, unanchored). All other `[vm-*]` checks passed over them | STALE PIN | `docs/design/startset/s1/census_s1.py` re-run on the k93fix build on ubuntubudu; the diff vs the committed manifests was EXACTLY +1 (auto) and +18 (forced) k93.rxt rows, nothing else, `manifest_s3_dfa` unchanged |
| test-memfn-stamps | C11 `trace:'(a{1,3})b(?1)(?1)a'` does not compile: `cxi_frame has no member call_top` | REAL BUG, PRE-EXISTING ON MAIN 9b8a4062. Traced `RX_PUSH` wrote `.call_top` on `has_calls`; the member and the untraced line are gated on `has_linked_calls`. A traced artifact with only spliced calls that emits a push does not compile. Repro on main's own binary: `(a+)a(?1)` with `--trace`. Exposed because the K93 fix no longer possessifies `(a+)` against the lexical follow, so k93.rxt's patterns now push | PRE-EXISTING (exposed, not caused) | emit_vm.c gated on `has_linked_calls`; K95 in known_issues.md; codegen `[K95]` check |

## Call-free byte-identity
No moved pin traces to a call-free pattern: the startset diff is only k93.rxt rows, and the census/C3 movers are k93.rxt cells. The one emitter edit (K95) touches only traced artifacts of call-bearing patterns. Spot check (main binary vs fixed, `--trace`, `(x)(?1)`, `(a)b(?1)a`, `^(a(?1)?b)$`): the only byte difference is the dead `call_top` macro-body line (and the include name).

## K95 byte movement (correcting the in-flight ruling's wording)
Traced artifacts of spliced-only call patterns move. Those that emit a push did not compile before. Those that do not (e.g. `(x)(?1)`) compiled and lose one dead macro-body line. No default (untraced) artifact moves. No abi bump (ruled by the manager).

## cc_join
`src/opt/possessify.c` `cc_join`: a call target outside `0..ncc-1` is now `pcrec_ctx_fail(P->cx, 0, "internal error: ...")` (house idiom, as src/opt/lower_enc.c), its own commit. `cc_widen` left quiet. `make strict` clean; `make test-possessify` 22/0.

## Process incident (disclosed)
I began editing and rebuilding in worktrees/k93fix, and committed 57b56aa5 on lane/k93fix, before the manager's constraint arrived while the k93fix Mac chain was live. The chain was safekilled by the manager and its results ruled VOID; lane/k93fix stays at 57b56aa5 as the base. Everything after that was done in worktrees/k93tri.

## Validation (section rc, both boxes)
Linux (ubuntubudu, k93-lx) at 57b56aa5: test-codegen 0, test-memfn-stamps 0, test-startset 0, test-rxtsource 0. Linux at the tip: see handback / BOXES below.
Mac (k93tri worktree): `tests/codegen/run_codegen_tests.sh` 0 failed (including `[K95]`), `make test-possessify` rc 0 (22/0), `make strict` clean. Full Mac `make test` at the tip: OWED, launched async at the end (see handback for the log path).

## Not done / notes
- The Mac per-section re-runs of test-rxtsource, test-startset and test-memfn-stamps are covered by the Mac `make test` at the tip rather than run separately.
- Sabotage of `[K95]`: the check's failing direction was measured on main's binary (the same three patterns fail to compile with 5, 5 and 7 gcc errors); no S-row was added.
