# bspan report: the design note for the SIMD-layer block span (R-47, D201)

## STATE AT HANDOFF

STATE: done (design only; no code, no suite, no timing).
OWED: none The note is
`docs/design/memfn/block_span.md` (rev 1), committed on lane/bspan. The
last rulings entry applied is **R-4** (smallest form). R-1 was applied and
then withdrawn by R-2. R-3's population record is in the note's §0.1. The
note is GATED on one ruling, `scalar-wrap` (OPEN QUESTIONS 1), which
should be settled before the critic round.

## THE JOB

Write the design note for building job 710's confirmed table at the SIMD
layer:
- window site with 16 <= k <= 1000, or scan site with 24 <= k <= 64, gets
  708's avx2-loop block span;
- everything else stays H64.

Cover the site map, the emitted text with its boundary argument, the rows
as a first-match table, the deny, the card, the abi package, G2, the
movers and the build units. The premise test passed: `grep -n 'span-loop'
memfn/src/options.def` hits line 122, and `grep -n WF_SPAN_HEAD
memfn/src/window.c` hits lines 1470, 1476 and 1483. 710's "window" and
"scan" are window.c E-find sites with pick FF_HORS and FF_WALK, facts the
kit has at render time.

## THE DESIGN

- **The premise fork (note §2).** The timed text replaces the span's chain
  inline, mid-line in the walk. The SIMD seam contract does not admit
  that diff (`tests/memfn/simd_floor_check.py` C18 (c), `limits.md`
  §8.3¶1, `tuning.md` §2.43¶4). Brackets must be whole lines
  (`src/core/sb.c`).
  - **Recommended: option A.** Use D155's existing selector shape: an
    eligible stretch calls `vs<j>(S, C)` at every layer, `__body` is
    today's H64 text, and the `w32` helper and the selector's one
    replaced call are added at x86-64-v3. Cost: default-build bytes move
    on eligible sites.
  - **Option B** is a seam change and is out of this lane's remit.
- **One table (note §3).** `wf_span_head`'s if chain becomes THE SPAN FORM
  TABLE, evaluated per stretch, first match: T-deny, T-force, T-lever,
  T-vwin (HORS 16..1000), T-vscan (WALK 24..64), T-head H(64). The deny
  `span-vector` is the V rows' option column.
- **The form (note §4).** 32-B and 16-B nibble blocks only, because no row
  reaches SWAR. The over-read argument is that reads are exactly
  [p, p + K), under the hoisted bound.
- **Fidelity (note §6).** F2 compares machine code against 710's arm
  sources; card C6 then times the shipped compile.
- **Deny (note §7).** `span-vector`, live at both layers under A.
- **Card (note §8).** C6 and `kit-grid@8`.
- **abi (note §9).** The next number at landing, likely 111 after L3's
  110. Readers are listed by grep.
- **Checks (note §10).** G2-V, T-table pins, the identity gate, and four
  sabotage rows.
- **Movers (note §11).** Listed by setting.
- **Units (note §14).** U1 to U6.

## TODAY NUMBERS

All of these are in the note's §16 with their commands. The key ones:
- main's abi is 109 (`src/gen/emit_dfa.c:55`);
- the `memfn` section floor is 14;
- `WF_SPAN_HEAD` is 64;
- every class probed has a window site up to 32 positions at the default
  width and none from 33;
- the machine-code probes:
  - with the `target()` attributes dropped: identical on 6/6;
  - with the `rxs_span` wrapper removed: `cmp` operand order differs on
    dig24 and num64;
  - option A's wrapper: identical on 8/10 at the default width (`\w{20}`
    and `\w{32}` differ), and on 6/8 at width 4095;
- 710: 127/144 WIN, 0 LOSS, A/A 6/448.

The scripts and outputs are in `/var/tmp/pcrec-pcrec/scratch/bspan/`.

## OPEN QUESTIONS

1. **`scalar-wrap`**: option A (moves default-build text, the H64 form
   inside a function) or B (a seam change)? Recommend A, but ask Frank
   whether "scalar stays H64" meant bytes.
2. **`scan-scope`**: should T-vscan cover LIBC/PAIR scans? Recommend WALK
   only (unmeasured otherwise).
3. **`wrap-deny`**: is the deny live at SIMD-off too? Recommend yes; it is
   the wrapper's only control.
4. **`ship-size`**: the added surface against a population of 4 patterns,
   for the go/no-go and the critics.

## OWED RUNS

None from this lane. The build lane owes: the F2 check, `make test`, the
G1 population at both layers, and C6 plus G1 timing in main's window.
