# bsu5fix2 report: the selftest_rev12 crash on lane/bsu5fix

## STATE AT HANDOFF
Branch lane/bsu5fix2 (cut from lane/bsu5fix 36548a3a9). One code file changed: memfn/tests/span_forms/cards.py. The rulings
file bsu5fix2_rulings.md was empty at every checkpoint (no entry applied). No timing run, no memfn/src change, no emitted byte moved.
Owed run: job 749-kit-bsu5fix2-selftest (below).

## CAUSE
NOT F3. Commit 7f870f6d6 (R-47 U5 WIP, already in lane/bsu5 and in 28b2da326) changed `variant_key(key, pre, fl)` to
`variant_key(key, pre, fl, cc=None)` calling `cc_ident(cc)` (it was `cc_ident()`), and `cc_ident()` to `cc_ident(cc=None)`.
The r44 I drill in selftest_rev12 (since 49138f6f1) stubs `cc_ident` with `lambda ident=ident: ident` and calls
`variant_key("t0", 16, [...])` with no compiler: `cc_ident(None)` now binds `ident=None`, the stub returns None, and `_h` does
`None.encode`. lane/bsu5's selftest would crash identically (748 was the first full selftest run past that point). F3 (ac807e97a)
only made the compiler a layer-table column; it did not touch this call. Line at fault: cards.py
`return _h(key, str(pre), " ".join(fl), cc_ident(cc))` with `cc` defaulted to None.

## FIX
No hidden default: `cc_ident(cc)` and `variant_key(key, pre, fl, cc)` now REQUIRE the compiler (the `cc or CC` fallback is gone).
The only production caller, `build_cell`, already passes `cc_of(layer)`. The r44 I drill names gcc explicitly: stub
`lambda cc, ident=ident: ident` and `variant_key("t0", 16, ["-fno-align-loops"], CC)`. Net 5 insertions, 6 deletions.

## KEY IDENTITY
Loaded lane/bsu5 28b2da326's cards.py and this tip, 80 inputs (4 text keys x 5 preludes x 4 flag lists), gcc: old
`variant_key(k,p,f,CC)`, old `variant_key(k,p,f)` (defaulted) and new `variant_key(k,p,f,CC)` are equal in 80 of 80; `cc_ident`
equal. Sample ('t0', 0, ['-fno-align-loops']) gives 7e1d54ba77d35741 in both. `text_key`, `c6_reach` and the header's `cc.*` use
`cc_ident(cc_of(layer))`, unchanged.

## SWEEP
- variant_key: build_cell (passes cc_of(layer), OK); r44 I drill (fixed).
- cc_ident: variant_key (OK); text_key `cc_ident(cc_of(layer))` (OK); c6_header `cc_ident(cc_of(ly))` (OK); r44 I stub (fixed).
- _h: signature unchanged. cc_of/opt_of/layer_flags/align_variants_of take a layer; every caller passes one.
- Selftest sub-drills after selftest_rev12 in cmd_selftest's order: J2 (time_cells) and J7 (source reach) only; each run
  through a python -I harness: both ok.

## IN-LANE RUNS
- `cards.py plan`: ok. `dry RD --quick --cards C6,C6c`: rc 0, 276 cells built and gated, 0 failures. `c6selftest RD`: 27 rows, 0 failed.
- r44 I harness: ok (the two compilers' keys differ). J2 harness ok (200 launches, 40 rows). J7 harness ok.
- `selftest --rev12` was started in the background; at report time it had 9 `ok` rows and no FAIL (slow Monte Carlo; the full
  selftest is the owed job).

## OWED RUNS
749-kit-bsu5fix2-selftest: full `cards.py selftest` at this tip, TMPDIR set, cap 7200 s, log
/var/tmp/pcrec-pcrec/scratch/bsu5fix2/selftest_full.log.
