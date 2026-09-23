# I-93 blocks A-E — the five discrimination blocks answering the batch-1 ledger's carve-out findings

Raw transcripts of pcrec-bench lane `[B78]` (`docs/dev/lanes/b78blocks_report.md`,
454 lines; full text is the source of record, not this excerpt), executed
per `docs/dev/optloop/cycle1_ledger_reading.md` §8's I-91 block, forwarded
to the bench as inbox item I-93. Run on ubuntubudu (AMD Ryzen 5 1600),
`gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0`, GNU Binutils 2.46, load1 < 0.5
before every timed phase, 5 trials median interleaved. Bench outbox entry:
`docs/dev/outbox_to_pcrec.md` O-48 (2026-09-23, pcrec-bench commit
`b223caf`).

**Pins.** BEFORE = pcrec `25b1984f` (abi 27, the bench's own committed
build, pre-D118 CLI shape). AFTER = pcrec `8d716693` (abi 29, batch 1's
merge, D118 CLI shape). Fetched by `scp` from `duxevents@100.69.121.107:
/tmp/optloop3/` (tailnet), read-only, 2026-09-23. Per the scope mandate
and the `optvmfl0`/`ccdiff_step0` archival precedent, **generated
artifacts are NOT archived** (the per-pattern emitted `.c`/`.h` files
under each block's own `work/` subdirectory, and the compiled ELF
binaries `bin_a_asis`/`bin_b_deleted`/`bin_c_moved`/`bin_d_nopartial` and
`<pattern>__<variant>`) — they regenerate byte-identically from the
pinned compiler, the named pattern text, and (for Block D's four hand-twin
variants) the three-line edit `b78blocks_report.md`'s own Block D section
quotes verbatim. What is archived here is the TEXT this repository has no
other copy of: the driver source, the build scripts, and every raw
timing/census/disassembly transcript the report's tables are drawn from.

**Verdict, one line per block** (see `docs/dev/optloop/cycle1_ledger_reading.md`
§9 for the reconciliation against the pcrec-side ledger):

- **E** — `perf_event_paranoid=4`, skipped as expected.
- **B** — two-sided null band, 120 program-identical cells, min −5.74% /
  max +8.46% / median −0.08%, 41 regressing / 79 improving. 15
  program-identical patterns by the bench's stamp-equality criterion
  (ours: 16, §9 below).
- **A** — every EXPECT direction held; absolute-recovery numbers not
  verifiable on the `findall.c` instrument (systematic 2×-10× scale gap
  vs. the store's own driver, present on every cell).
- **C** — the arm64/gcc-16 `.part.0` partial-inlining split **does not
  reproduce** on gcc-15.2/x86_64: `rx_search_run` carries no `.part.0`
  symbol at EITHER pin, on any of the three patterns that have the symbol
  at all. The req_byte `memchr` pre-check compiles inline into
  `rx_search_run` at the AFTER pin (confirmed by relocation records and
  the exact stamped byte constant). `wild-secrets-github-pat` has no
  `rx_search_run` symbol at either pin (§9 explains: it is a FRAMELESS VM
  artifact, `RX_VM_ENTRY_SHAPE "inline"`, so `rx_search_run` is
  `static inline __attribute__((always_inline))` and is folded entirely
  into its three callers — a [CC-DIFF] STEP 1 fact, unrelated to batch 1).
- **D** — none of the three EXPECT clauses resolves; every measured delta
  sits inside the per-variant IQR (300K-1.5M ns on an 8.4M-9.9M ns
  median), and variant (b)'s sign flips between the two internal-iters
  settings tried.

Files (all fetched verbatim, no edits):

- `blockA_build.sh`, `blockA_findall.c`, `blockA_time.py` — Block A's
  build/timing driver (the I-89 §0.4 `findall.c` instrument).
- `blockA_time_output.txt` — Block A's raw 5-trial timing output, all
  four patterns × four variants (default/noreqbyte/noendwin/noboth).
- `blockB_blockb.py` — Block B's read-only reduction script (imports
  `pcrecbench.reduce` directly against the eight committed
  `capability@0.1` records; no new runs).
- `blockB_output_onesided.txt` — Block B's first pass (regressions only,
  the shape the pcrec ledger's §2.1 table used).
- `blockB_output_twosided.txt` — Block B's full 120-cell two-sided table
  (both directions; the null band's own source).
- `blockC_build.sh` — Block C's standalone-`.o` build shape
  (`gcc -O2 -std=gnu11 -fPIC -c`, matching the bench's real compile flag).
- `blockC_disasm_search_run.txt` — Block C's full `nm`/`objdump -dr`
  transcript for all four patterns, both pins (the `.part.0` check, the
  relocation-record confirmation of the inlined `memchr` pre-check, frame
  size, `__stack_chk`, hot-loop alignment).
- `blockD_findall.c`, `blockD_time.py` — Block D's driver (same shape as
  Block A's, separate copy since the block ran independently).
- `blockD_time_output_iters5.txt`, `blockD_time_output_iters25.txt` —
  Block D's raw timing output for the four hand-twin variants
  (as-is / deleted / moved / `-fno-partial-inlining`) at both internal
  iteration counts tried.

Not archived (regenerable, per mandate): `/tmp/optloop3/blockA/work/*`,
`/tmp/optloop3/blockC/work/*/{before,after}/*`,
`/tmp/optloop3/blockD/{a_asis,b_deleted,c_moved,d_nopartial}.{c,h}`,
`/tmp/optloop3/blockD/art.h`, and every `bin_*`/`<pattern>__<variant>`
ELF binary. The scratch tree `/tmp/optloop3/` on ubuntubudu was held per
O-48's own note ("held until 'I-93 logs fetched'") — now fetched; its
disposal is the bench's own call, not pcrec's (read-only reference).
