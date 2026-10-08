# r4hprep — [MEMFN] R4h PREP (kit-only, zero pcrec byte movers)

Lane r4hprep, 2026-10-08, branch `lane/r4hprep`. It was cut from the kit
branch `lane/memfn-g2floor` at `5b6064c1`. The ruling it builds is the pcrec
manager's session 97 ruling, recorded in memfn/docs/responses.md:
- "notice: 2026-10-08 — R4h (M3) edit set";
- "ruling recorded: Q-R4h-1 (a)+(b)".

It touches nothing under `src/gen`, `src/opt` or any pcrec emitter, and no
pcrec source at all. The pcrec side waits for C7.

## Charter checklist

| item | artifact | state |
|---|---|---|
| (a) caller-owned counter, MF_SITE_ABI 4 -> 5 | memfn.h `mf_site.count_by_caller` (appended LAST) + contract comment; fields.def field `count_by_caller` (OBLIG, NO/YES/OTHER); compose.c `site_check` (0/1, ADVANCE-only, refused by name); generic.c renders advance+cap, never the declaration; every row's `serves` lists it | DONE |
| (a) refuse/decline when used but unstated | kit.h `gate_use` gains a CONDITIONAL tail (`GATE_WHEN(cls, field)` / `GATE_ALWAYS`), gate.c `uses_at` honours it; generic's entry makes `count` a USE at `count_by_caller` YES, so unstated `count` is R1. The use is refused naming `count` | DONE |
| (a) MF_SITE_ABI readers re-pinned | list below | DONE |
| (G3) hook classes | fields.def `CONJ` (`more`), `POSTFIX` (`peek`), `EXPR_STMT` (`step`); gate.c `conj_shape`/`postfix_shape`/`expr_stmt_shape`, lexical and conservative; memfn.h states each rule | DONE |
| Q-G2-5 recorded ruled | memfn.h ADVANCE comment (range is `more`, empty NOP, no kit empty test); integration.md §14.4 `[R4h-prep]` note | DONE |
| memfn.h:46-48 reverse-SKIP comment vs Q-G2-9 | the `MF_MAX_BACK` comment is rewritten: the -1 is `peek`'s text, not a term offset; the first negative offset is M4's `(?m)^` | DONE |
| fixtures + gate cases | arm_fixtures.c: 2 pinned ADVANCE fixtures (`adv-kit-count`, `adv-caller-count`); 19 gate cases (6 counter, 13 `adv-cls-*`); `--gate-only CASE` | DONE |
| a positive case per class | rows_check.py check E reads each case's classes off an MF_TRACE build against a hand table (`CLASS_EXPECT`); 6 positive cases for each narrow class, 7 OTHER | DONE |
| pins | arms.tsv gains 4 rows (2 fixtures × def/use). No existing digest moved | DONE |
| GATE_EXPECT and floors | `GATE_CASE_FLOOR` 20->39, `ARMS_ROW_FLOOR` 54->58, `FIXTURE_FLOOR` 27->29, new `CLASS_CASE_FLOOR` 15 | DONE |
| CLAUDE.md / PROVENANCE | memfn/, memfn/include/, memfn/src/, tests/memfn/ CLAUDE.md updated. No file was added, so PROVENANCE.md is unchanged | DONE |
| design docs | integration.md §14.3/§14.4 `[R4h-prep]` notes; row_contracts.md §2 (classes, OBLIG list, conditional uses) | DONE |
| zero-mover proof (cheap tier) | below | DONE |
| responses.md / journal.md | the kit session's files (one writer) | OWED to the kit manager |

## Design notes

- **`count_by_caller` sits on `mf_site`, not `mf_hooks`.** It is a semantic
  site fact, read at define.
  - **Why it does not touch pcrec.** pcrec's builder `pcrec_memfn_site`
    allocates zeroed arena memory and sets only the fields it names. G2's
    and the fixtures' sites are memset. So 0 (kit-owned) is what every
    existing builder already states, and no pcrec source changes.
  - **`count_start` keeps its meaning:** the value at the kit's first
    statement. The caller's text makes it so: 1 after the scan edge's peeled
    step, 0 for the VM's `it_`.
- **The conditional `uses` entry** is the general form of "a site fact makes
  a hook required" (memory `pcrec-general-mechanisms-not-special-cases`).
  - Positional `gate_use` initializers needed explicit tails to stay clean
    under `make strict`'s `-Wmissing-field-initializers`. Hence
    `GATE_ALWAYS` on the 20 existing entries, each edited in place with no
    line count moved.
  - generic.c's line citations were re-verified: unchanged, since
    `stmt_advance` kept its line count.
- **The classes are conservative.**
  - CONJ rejects any top-level call, because the macro hazard is invisible
    to a lexical check. It also rejects `||`, `?:`, comma and assignment;
    `<<=`/`>>=` count as assignments and `<=`/`>=` do not.
  - POSTFIX rejects `++`/`--` anywhere, white space outside brackets, and a
    call suffix.
  - EXPR_STMT rejects a leading keyword or declaration, any second `;`,
    braces, and top-level `,`/`?`/`:`.
  - No row serves the narrow classes yet, so no selection moves. The real
    M3 texts all classify narrow: the cases `adv-cls-fwd`, `-view`, `-rev`
    and `-vm` are the STAY, view, reverse and VMSPAN texts read off the
    witness compiles.
- **Finding for R4h (not built).** A byte-identical in-loop row also pastes
  the `member` hook's RETURNED text (EDGE's `scan_test`, for example
  `(unsigned)(subject[x] - 97) <= 25u`) as an unparenthesized `&&` operand.
  - That text exists only at render, so no define-time class covers it.
  - R4h must either classify it at render with `conj_shape` (and refuse,
    since falling back would move bytes) or have pcrec promise it under
    rule 6.
- **Defensive overlap.** `stmt_advance`'s `need()` also refuses an unstated
  caller-owned `count`, and its text names `count` too.
  - So plant P3 (deleting the conditional entry) stays green in
    run_arm_pins.sh.
  - It is caught only by check E (`count` stops being a used field). This
    is recorded so the next reader does not take arm pins as covering it.
- **Pre-existing citation drift.** runcmp.c's `compose.c:230`/`:265`
  comment citations were already stale at the branch point. They were left
  alone, because sabotage anchors may quote those lines.

## MF_SITE_ABI readers (grep `MF_SITE_ABI` over the tree, worktrees excluded)

- **Value statements, re-pinned:**
  - `memfn/include/memfn.h:39` is the define (4 -> 5) and its comment;
  - `memfn/CLAUDE.md` (it read 4; now 5);
  - `memfn/include/CLAUDE.md` (it read **3**, already stale; now 5).
- **Symbolic readers, which follow the define:**
  - `memfn/src/compose.c:319-321` (the abi check);
  - `src/gen/memfn_sites.c:145` (pcrec's builder; untouched);
  - `memfn/tests/g2/g2_gen.c:700,1722,1757` (the last is the `+1`
    mismatch case);
  - `tests/memfn/arm_fixtures.c:191`.
- **Historical, untouched:** `memfn.h`'s "MF_SITE_ABI 3" (Q-G2-18) and
  "MF_SITE_ABI 4" (stamp_int, MF_MISS_N) notes. These are dated rulings.
- **Also untouched:** the journal, responses, the review files and the lane
  reports, and integration.md's revision history (its §14.3 note states 5).
- **pcrec's own abi does not move:** no emitted byte changes, and no reader
  of `PCREC_ARTIFACT_ABI` is involved.

## Validation (cheap tier, Linux dev box)

- `make strict`: clean.
- `make test-memfn-arms` 171/0 (was 138/0). `test-memfn-rows` 117/0 (N4
  measured 70/0; check E adds the rest). `test-memfn-stamps` 14/0, with the
  C11 FORMS half UNREACHED as before.
- **G2 `--quick`**, `taskset -c 12-15`:
  - checks: **45,229,679 passed, 0 failed**;
  - gcc-15: 44,819,572 passed over 11,350 sites, with `coverage-missing 1`
    (the known quick alignment axis);
  - K1 377,000/0; libc record 108 batches agree, 0 disagree;
  - W1/W3 witnesses fired.
  - Log: `build/r4hprep_scratch/g2quick.log` (gitignored).
- **Byte identity:** 18/18 compiles are byte-identical (`.c`, `.h`, rc) at
  the SAME `-o` basename against `build/pcrec` copied at the branch point.
  The two binaries differ.
  - Default witnesses: `a[^x]*`, `a[^x]*x$`, `[a-z]*`, `a[0-9]{3,20}x`.
  - `--engine=vm`: `(a)[a-z]{2,9}x`, `a[a-z]*x`, `a[^x]*`,
    `a[0-9]{3,20}x`, `[a-z]*`.
  - `-e utf8`: two cells, plus one `--engine=vm -e utf8` cell.
  - Kit customers: ofsskip, VM, `-fno-offset-skip`, precheck_assign,
    runcmp words, plus one `-fno-scan-edge` cell.
- `python3 scripts/m6read_check_sab_anchors.py`: 498 sabotages / 516 anchor
  sites, **all anchors resolve**.
- **Failing direction**, each planted and reverted:

  | plant | what it did | detected by |
  |---|---|---|
  | P1 | CONJ accepts `\|\|` | check E red |
  | P2 | generic declares a caller-owned counter | pin moved + check 7 red |
  | P3 | conditional use deleted | check E red (see the defensive-overlap note) |
  | P4 | the 0/1 vocabulary check deleted | gate case red |

## Owed: the slot must still run

1. The identity gate vs this branch's base (`memfn_r4c_gate.py`, all
   streams), expected 0 movers.
2. G2 full (`make test-memfn-g2-full`).
3. `make test`.
4. The mech rows anchored in the changed files (`tests/mech/rows_for.sh`
   over this lane's diff): S68 S185 S265 S267 S279 S285 S443 S444 S445 S447
   S450 S454 S455 S464 S526 S570 S573, each solo.
5. The N2 census on this build, expected would-decline 0 (no row serves a
   narrow class, so nothing moves).
6. Not lane work: the kit manager writes the responses.md entry and the
   journal line.
