# u1rev21 — kit_proof.md revision 2.1 (lane report)

Lane `u1rev21` (opus), 2026-10-18, branch `lane/u1rev21` from main `fa322a7f6`. DESIGN
ONLY. The only runs were single-pattern compiles and the small checks named below, all
under `nice -n 19`, finished by 17:10. Nothing is under `src/`, `memfn/` or `tests/`.

## What it did

It applied the re-check of revision 2 (`docs/dev/reviews/2026-10-18-r3-kit-proof-u1.md`,
"Re-check of revision 2", all ACCEPTED) to `docs/design/kit_proof.md`. The note's §R2.1
maps each id to its section, and changed text is marked `[r3rc <id>]`.

- **K1 (BLOCKER).** C9 is now "no row at depth 0..k carries a non-identity eol view".
  - `conj.py` implements it through `rows_by_depth`. `CONJ_PLANT=c9-depth-k` restores
    revision 2's C9, which is the plant.
  - `witnesses.txt` gains `ab|a$\n`, `ab|a\Z\n` and `ab|a$\n\z`.
  - §5.2 states that `span_facts` passes a mid-pattern `$`/`\Z` to the hull, so C9 (not
    C8) is the conjunct that has to decline these bodies.
  - S1136 is re-aimed to the K1 plant.
  - X0's subject families gain "each literal path at the subject end".
- **M-A.** C2 is retired. Its number is kept so other references stay valid.
  - `conj.py`'s census applies nothing after the table, so the `why` histogram is
    first-match in table order.
  - The recount puts U-ctxorigin's joins in U1: 12 / 9 corpus context joins, plus 5 bench
    / 27 corpus native and 1 / 7 utf8 whole-cover patterns with no start-origin site.
  - Admitted populations are now 77 / 665 native and 50 / 485 utf8. These equal the
    critic's `eolwalk.py` counts.
- **M-B.** The kit-side channel is `mf_preview(mf_art *, const char *step)`.
  - It follows the `mf_reach` precedent. It is reached only through
    `PcrecHarnessOptions.kit_proof`, which only `pcrec_harness_compile` sets. That is the
    compound lever's single reserved-prefix global, so the fence count does not change.
  - It is not an `options.def` row, so `mf_opts_check` refuses any `--memfn=` spelling of
    it.
  - The wording is D157-neutral: pcrec names its own routing step and never a row or a
    form.
  - §7's re-run condition is now "if pcrec's row OR the kit text differs at B1 from Z2,
    B4 included", checked mechanically by a byte diff of the harness-routed witnesses.
- **M-C.** S1143 is declared UNREACHED. 21 nullable probes under the plant all decline,
  at C4 or C10, and a body with `k` = 0 has no BOUNDED span 0 for C13. S1139 is now two
  edits. With C9 dropped alone, C11 masks it. With both edits it is red: `cat$` under
  `-fno-rev-end` on `"9cat\n"` from 0 gives PCRE2 (1,4) and the plant none, on 9 of 1,495
  cells.
- **m1-m8.**
  - m1: C14 is equality on REPORT, and `kit-none` covers both directions.
  - m2: the C8 `why` splits into `exact/machine-inexact` and `exact/producers-disagree`,
    with a trace assertion of 0 for the latter.
  - m3: `consumer = MF_C_RESULT` is stated in §2.5, §4.1 and R-26.3.
  - m4: MLINE's predicate is named in lift item 2, and the carrier is spelled
    `const mf_pred *ctx; uint8_t nctx;`.
  - m5: a CONTEXT term below the floor but inside the subject has no verdict, so
    `MF_FLOOR_LO` with a below-origin term is refused. S1137's detector moves to match.
  - m6: X5 is "modulo the abi readers".
  - m7: the getwidth superset is stated per encoding (utf8: `1 ≤ min`, `max ≤ 4·min`;
    `é|ab`).
  - m8: Q2's PENDING label is deleted and the RULED text kept. fam-M7's claim is
    corrected: neither A1 nor A5 moves in stage 1. The note now records that `conj.py`
    has no C5.
- **PARTIAL items, stated as owed.**
  - The `span_facts` half of C8 is OWED at Z2.
  - X0/X1 and the getwidth floor are OWED at step X0, before Z2. The critic's runs are
    precursors, not X0.
- **UL-n1** is done. **UL-n2** and **UL-n3** are filed with triggers.
- **CLAUDE.md files.** `docs/design/kit_proof/CLAUDE.md` and `docs/design/CLAUDE.md` are
  updated, and `conj.txt` is regenerated.

## Validation (all compile-only, `nice -n 19`)

| check | command / tool | result |
|---|---|---|
| revision 2 baseline reproduces | rev 2 `conj.py census` on this build vs committed `conj.txt` A/B/E | identical |
| admitted set, rev 2 vs rev 2.1 | the critic's `.scratch-k3rc/admitted.py` (unmodified, rev 2 `conj.py`) vs a copy pointed at rev 2.1 `conj.py` | 1,197 → 1,197, `diff` empty: nothing newly declined |
| deep eol on the admitted set | the critic's `eolwalk.py` (unmodified) | 0 in every stratum (77 / 50 / 665 / 485) |
| K1 witnesses decline | a copy of the critic's `x0lite.py` pointed at rev 2.1 `conj.py` (sys.path line only) | 3 of 3 `no-eol-view` |
| K1 plant red | the critic's `x0lite.py` as is (= rev 2 C9), and rev 2.1 under `CONJ_PLANT=c9-depth-k` | `cover`, 10 and 18 diffs on `\Z\n` and `$\n\z`. `ab\|a$\n` read 0 on x0lite's random subjects, and the directed cell through the critic's `coversim.py` is red on all three (`"a\n"` from 0: plant NOMATCH, PCRE2 (0,2)) |
| `conj.txt` regenerated | `conj.py` census + rarm + witnesses | B: `no-start-site` → `cover` only. C: unchanged. D: plus the 3 K1 rows |
| S1139 two-edit reach | the critic's `x0lite_p.py C9E` / `C9` | C9E red on `cat$` (9 cells) and `cat\Z` (1). C9 alone declines at `after-agree` |
| S1143 reach | `x0lite` copy, plant C7, 21 nullable probes | all decline (C4 or C10) |

Scratch (not committed) is in `worktrees/u1rev21/build/u1rc/`: the baselines, the
admitted lists, the copied tools and `k1direct.py`.

**Admitted-set delta: 0.** Nothing was newly declined, and no row changed verdict
between `cover` and a decline. The census delta in `conj.txt` B comes only from retiring
C2.

**`make test-spec-history`** (`build/` light check, 2026-10-18): revision 2's three
`match_api.md:<line>` citations in `kit_proof.md` (lines 106, 491, 880 at main
`fa322a7f6`) made it red on main too. They now cite §6.3.4¶11 and §5.5¶12 instead. One red
remains, `docs/dev/reviews/2026-10-18-r3-kit-proof-u1.md:84` (`match_api.md:1823`). That is
a review record, so this lane left it unedited; the fix is one token, for the manager.
Result: 144 passed, 1 failed.

## Not discharged

- X0 and X1 themselves: the independent per-position, per-byte libpcre2 oracle and the
  full differential. These are heavy and were not run under the box rule. They are owed
  at step X0, before Z2.
- The getwidth K35 floor's number. The instrument is designed and has not been run.
- The `span_facts` half of C8. It needs the Z2 build.
- The K96 per-field `serves`/`uses` cells for the new fields, including `mf_preview`'s
  refusal fixture. Those belong to the kit, at Z1/Zk.
- `mf_preview` is a DRAFT spelling for R-26.6, filed through the manager like the rest of
  R-26. The kit owns the final name.
