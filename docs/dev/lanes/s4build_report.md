# s4build report — [CLS-TREE] S4, the VM decode + kit (2026-09-29/30, lane s4build, opus)

Branch `lane/s4build` from `lane/land3` (`8b6db305`: U2 + S3 + K67). This is
ONE abi event, 46 → 47; the manager serializes the number at merge. The build
plan is `docs/design/cls_tree_design.md` §6.1, committed before any code
(`089ab502`).

## 1. What landed

| piece | where |
|---|---|
| `PCREC_ENCE_DECODE` (`$_decode`): stage 4's caseless decoder, MOVED rather than copied into its own utf8-only entry. `engine_callable`, `static inline`, declared nowhere | `src/enc/enc_utf8.c`, `src/enc/enc.h` |
| two `PcrecEncEntry` columns: `requires` (utf8 `SPAN_CASELESS` → `DECODE`, closed by `pcrec_enc_mask_close` inside every emit function) and `inline_def` (emitted by `pcrec_enc_emit_inline_defs` ahead of the engine bodies; `pcrec_enc_emit_defs` skips it) | `src/enc/enc.{c,h}`, both backends' tables |
| the VM route: `vm_wcls_bytes` (the one route question), `vm_seethru` (the flatteners' narrowed see-through), `vm_wcls` (the pool, and `pcrec_clskit_select` at `cx->opt->tune`), the `A_WCLASS` arm's decode + kit test, `vm_cost`/`vm_count_slots` agreeing, `VE_WCLASS` + its listing row, the matchers emitted beside the class bitmaps, the `<PREFIX>_VM_CLS_KIT` stamp | `src/gen/emit_vm.c` |
| `-fno-cls-kit` (`PCREC_NO_CLS_KIT`, bit 36; D129 Q2's one kit-level deny): axis row, `--list-axes` predicate row, `strategy_denials` | `lib/pcrec.h`, `src/core/axes.def`, `src/dump/axes_dump.c`, `src/gen/emit_dfa.c` |
| cwmax/cwmin: `A_WCLASS` is ONE CHARACTER (D-2, ruled here) | `src/opt/mrl.c` |
| abi 46 → 47: the constant, `ABI_EXPECT` and its narrative, the `match_api.md` §6 paragraph, recursion identity (B) FILEPIN self-pinned to `0d0a514f` | as listed |
| spec: `tuning.md` §2.33 (new), the §4 mirror row, λ's §5.4 row ("unbuilt" → built) and the §5.4 note that λ makes `+2` distinct; `match_api.md` §6 + the `<PREFIX>_VM_CLS_KIT` (b) entry | `docs/spec/` |
| `src/core/tune.c`'s `+2` comment: its become-reachable condition ("the day λ lands") is met | |
| tests: `tests/utf8/wclass_illformed.rxt` + its generator; `run_wclass_census.sh` PART 3 (K1-K7); `run_tune_dial.sh` §3d (the matcher form per position, read off the emitted text); `run_encoding_checks.sh` reads `rx_decode`; K55's `run_axes.sh` refusal entry DELETED | `tests/` |
| sabotage rows S390-S395; S365 re-anchored | `tests/mech/sabotages/` |

## 2. Decisions made here (none needed a ruling; each follows from a ruling or the design)

1. **Which sites switch to the kit** (§6.1's table): an `A_WCLASS` that
   reaches `vm_emit_node` takes one decode + kit test, whatever loop or
   lookbehind it sits in. Every site that consumes the BYTE CHILD first keeps
   doing so: a literal run, an island, a cursor stride, and the whole
   DFA/NFA/prefilter side.
2. **A one-member wide class keeps its bytes.** This departs from the letter
   of §2.2 ("every `A_WCLASS`"), for a measured structural reason. `é` is a
   LITERAL, and the literal forms (`éabc`'s five-byte `memcmp`,
   `café|naïve|résumé`'s island) read its bytes. Routing it to the kit split
   the run and dissolved the island (S3's W1/W3 witnesses), with no answer
   change and no size or speed to gain. This is why `vm_seethru` exists: the
   spine flatteners still unroll exactly the byte-routed wrappers, as S3
   did.
3. **cwmax/cwmin read one CHARACTER** (D-2). Every reader after the lowering
   asks only zero-vs-nonzero (`startanch.c`, `endwin.c:95`), and
   `endwin.c`'s one value-reader declines under a multi-byte encoding first,
   so nothing moves. `pcrec_minw` (bytes, the MRL prune's unit) still walks
   the child.
4. **Row denies are not mapped to public flags.** `-fno-cls-kit` denies the
   whole kit (route = byte child). Form-vs-form answer identity is
   `tests/clskit/`'s exhaustive differential; position-vs-position identity
   is `make test-axes --tune`.

## 3. Findings

See §4 for numbers. Two items are for the manager's attention:

- **`(\p{Xwd})` at default axes STILL REFUSES**, now on TOTAL emitted bytes
  (1,026,701 > 1,000,000). The refusal used to be on code bytes. The VM
  program is small now, but the hybrid's byte-DFA PREFILTER for `\p{Xwd}` is
  what is left. `(\p{L})` fits (784,086 B total). S4 does not shrink the
  prefilter (§3.3). A "drop the VM hybrid's prefilter" rung on the size-cap
  ladder ([K53-SELRETRY]'s shape, and "a second rung needs an ORDER") would
  retire it. That is a RULING, not something this lane built.
- **`-2`'s P3 can emit MORE C SOURCE than K.** The selection compares OBJECT
  bytes as ruled (D131 addendum 1). For example, `\p{Nd}` at `-2` takes P3
  (row size-page3), whose artifact is 17,171 B of source against K's 16,548
  B at `0`. It is recorded, not acted on: source bytes are not the ruled
  quantity, but the size caps are on source bytes.

## 4. Validation

(filled below)

## 5. Owed

(filled below)
