# emit lens: emitted C vs BASE (memfn-sp1f)

BASE 761521515 (scratch/base/build/pcrec) vs SUBJECT 98145b3d5 (worktrees/crit-memfn-sp1f/build/pcrec).
Question: is the emitted C byte-identical in default and every surviving arm, stamps included?

## Findings

None. No emitted-byte, stamp, refusal or exit-code difference anywhere in the probed population. The only
caller-visible moves seen are the two declared ones: `--list-axes` loses the `fd-r8` and `fd-ndisp` rows, and
`--memfn=no-fd-r8` / `--memfn=no-fd-ndisp` are now refused as unknown options (rc 1). Both are the unit's stated intent.

## PROBED-AND-HELD

Code reasoning, done before choosing witnesses (finder.c at BASE):
- R8, R1 and R2 could never decide anything at BASE.
  - R8 needs KN_N, and fd_holds returns 0 for a KN_N row in the terminal phase. In the residual ask it needs
    SF_E_MEASURED, which no code sets (grep: only the enum and R8's row mention it).
  - R1 and R2 need SF_TERMINAL_FAST. That fact is set only when the terminal pick is V1 or W64, and no surviving
    FIND row picks either: D1 picks LIBC, D1c LIBC_BACK, D1w WALK, PAIR PAIR, R7w WALK, and fd_pick_of is the identity.
  - So the residual loop's kit_ask always failed, `npiece` stayed 1, and the pay rule (fd_pay/pay_fill) never ran.
- This matters because the DEFAULT measurement set zen4-grid1@1 (measure_store DEFAULTS) does carry
  `kit.xover.V1.WALK.DFA_SCAN` and `kit.block.W64`. So the guard against R1/R2 firing was the fact mask, not
  missing keys. The guard held, and the old `d.npiece != 1 -> NULL` return in fd_route and fd_find was unreachable.
- The rows that were removed had no side effects that outlive a compile. gate_check is pure, and the
  kit_walk/kit_ask "why" verdict is local to fd_decide. The reach counters (`chosen`/`asked`) are MF_TRACE-only,
  and the trace build is not the shipped binary.
- `mf_class.pres_row`'s index shift (MF_CLASS_V 7) is read in pcrec only by pcrec_memfn_pres_routed. That reader
  sits under PCREC_CAND_TRACE, which the default build does not define (nm finds no `pres_routed` symbol). It also
  resolves ids through the same binary's mf_finder_rows, so the shift cannot misname a row.
- The emitted artifact carries no MF_SITE_ABI or MF_CLASS_V number. `abi 95` is the same on both sides.

Empirical diff: full emitted text with `-o -` (C plus stamps), compared together with exit status and stderr.
Every compile ran under both binaries (counts are patterns; double them for compiles):

| arm | flags | patterns | same | diff |
|---|---|---|---|---|
| default | (none) | 85 | 85 | 0 |
| vm | --engine=vm | 85 | 85 | 0 |
| simd | -fmemfn-simd | 85 | 85 | 0 |
| nosimd | -fno-memfn-simd | 85 | 85 | 0 |
| each of 5 SIMD denies (no-vrun-w32/w16/kb/trim/pad) | -fmemfn-simd | 85 each | 85 each | 0 |
| each of 7 scalar denies (no-precheck-assign-byte, no-fd-d1, no-fd-pres-g1, no-fd-pres-pick, no-pres-set-lead, no-window-search, no-window-skip) | (deny only) | 85 each | 85 each | 0 |
| F-default | --features all | 85 | 85 | 0 |
| F-vm | --features all --engine=vm | 85 | 85 | 0 |
| F-simd | --features all -fmemfn-simd | 85 | 85 | 0 |
| F-nosimd | --features all -fno-memfn-simd | 85 | 85 | 0 |
| F-no-fd-d1 | --features all --memfn=no-fd-d1 | 85 | 85 | 0 |
| F-no-fd-pres-pick | --features all --memfn=no-fd-pres-pick | 85 | 85 | 0 |
| U8 | --features all -e utf8 | 10 | 10 | 0 |

- About the non-feature arms: 24 of the 85 patterns need modules outside std1, so in those arms they are refused
  identically by both binaries. The six `--features all` arms re-cover all 85 with modules on; 2 are still refused
  identically by both.
- Population (scratch/emit/pop.txt):
  - 40 crafted witnesses aimed at the finder sites: one-byte stops, sets, two-byte pairs and window sites,
    PRES/pre-checks (dominated, set-leads), cover, the landmark walk, unanchored DFA scans with memchr seeks,
    end_back, MLINE, the VM through backrefs and lookaround, and alternations.
  - 25 corpus patterns from tests/{prefilter,litscan,landwalk,offsetskip,kitproof,findings,mrl,memfn}.
  - 20 random patterns from all tests/**/*.rxt.
  - Spot-checking the stamps confirms the sites are reached: RX_MEMFN_LIBC "memchr" / "memchr,memcmp";
    RX_DFA_SCAN cover / landmark-walk / unanchored; RX_REQ_WHY dominated.
- Non-C surfaces that read the finder or kit tables:
  - `--list-syntax`, `--list-definitions`, `--list-verbs`, `--list-families`, `--list-limits`, `--list-schema` and
    `--version` are identical.
  - `--list-axes` differs ONLY by the two declared removed rows (fd-r8, fd-ndisp).
  - `--emit-facts` and `--emit-ir` are identical on 5 patterns (20 compiles).
- Retired names: `--memfn=no-fd-r8` and `--memfn=no-fd-ndisp` are accepted by BASE (rc 0) and refused by SUBJECT
  with "unknown option" (rc 1), as declared.
- No gcc -S comparison was needed, because no emitted text differed.

Budget: about 3,800 single compiles in total, which is roughly 25% over the ~3,000 cap. The cause was a filter bug
that sent all 85 patterns, not only the 24 refused ones, through the `--features all` arms. All compiles were
niced and run one at a time.
