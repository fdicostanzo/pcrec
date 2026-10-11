# r14p — [MEMFN] R-14 follow-up: the PADDED WORD verify in vrun's main path

Lane r14p (opus), 2026-10-11. Branch `lane/r14p`, cut from the kit branch
`lane/memfn-r14` @ 14143d53, which holds r14b's trimmed verify. Charter: the
manager's brief, after Frank's 2026-10-11 point that a verify costs loads
and branches, not bytes. Background: `memfn/docs/requests.md` R-14, D147
addendum 15 and `docs/dev/lanes/r14b_report.md`.

## 1. Summary (resume from here)

- **What changed.** This applies in the MAIN block loop of the
  `vrun-w16`/`vrun-w32` helpers, to runs of 3 or 5-7 bytes. Before, such a
  run was verified by two overlapping words. Now it is verified by ONE word
  of the next width up (4 bytes for L 3, 8 bytes for L 5-7):
  - the mask is 0x00 past the run's end and at the positions the filter
    proved;
  - the compare is against the run padded with zeros.

  That is one load and one branch per candidate, where the words form took
  two (§4).
  - The final block keeps r14b's trimmed compare.
  - The scalar `__body` is unchanged.
  - L 2, 4 and 8 are unchanged: the words form is already one word there.
  - L > 8 is unchanged (§6).
- **THE MARGIN.** The brief asked for the margin. It also corrects the
  brief's premise.
  - A main block at i is taken when `i + R <= n`, with R = VW + T.
  - Lane j's candidate is c = i + j, and its run ends at c + T.
  - So the bytes readable past the run are `n - 1 - (c + T) >= VW - 1 - j`.
  - At the TOP lane (j = VW - 1) that is **0**. The loop guarantees bytes
    ahead of the low lanes only, not of every candidate.

  The padded word is therefore legal only because the main guard now holds
  E = P - L more bytes: `if (i + R + E <= n)`. That gives every lane at
  least `(VW - 1 - j) + E >= E` bytes. E is 1 for L 3 and L 7, 2 for L 6,
  and 3 for L 5.

  A block that the main guard no longer takes can still lie inside the
  subject (`n - R - E < i <= n - R`). It becomes a final block with
  `f = i`: one clamp line, `if (f > i) f = i;`, and nothing masked. After
  it comes the overlapped block at `n - R`, as before. Both read only
  `[pos, n)` (vrun.c's OVER-READ argument, extended).
- **How it is built.**
  - runcmp.c gains the padded form: `run_cmp_pad_over`, `run_cmp_pad_decl`
    and `run_cmp_render_pad`. It is the words form's spelling for a caller
    that STATES how many bytes past the run it may read.
  - That margin is the argument `over`, which has no default. A call whose
    `over` is short of the form's need is a refusal (`kit_fail`).
  - The form applies only where the walk picked a words-form row, so
    `MF_D_RUN_OVERLAP` reaches it as it reaches those rows.
  - vrun.c's `vrun_pad` computes E, writes the main guard `i + R + E`, and
    passes `over = E`. Its `vrun_verify` writes both of a padded helper's
    verify loops.
- **No helper declaration (the floor rule).** `run_cmp_prepare` declares,
  outside the guard, the largest width that FITS the run. The padded width
  is never that width. A `<p>_w4`/`<p>_w8` declared inside the guard would
  mark the width emitted for a later scalar use. Declared outside, it would
  be text the SIMD-off artifact lacks. So the form loads through three
  locals that the helper declares after its broadcasts:
  - `uint64_t pw, pk, pt;`;
  - two `memcpy` lines from string literals (the words form's
    endian-neutral idiom, which gcc folds to immediates);
  - the verify, `((memcpy(&pw, subject + cand, 8), pw) & pk) == pt`, a
    single expression.
- **The deny.** `--memfn=no-vrun-pad` (options.def: DENY, scan, simd)
  renders r14b's text byte for byte. Against 14143d53 it has 0 movers
  (§5.3).
- **SIMD-off is untouched.** There are 0 movers on c-default, c-vm and
  emit-ir. The only dump that moves is `--list-axes`, by the `vrun-pad`
  row. This is not a pcrec abi event.
- **G2's SIMD family** gains:
  - a `deny-pad` class;
  - THE PADDED VERIFY check (1d), whose expectations come from G2's
    GENERATED run;
  - an EDGE counter (main-path padded verifies whose word ends at the
    subject's last byte, next to the guard page) with floors;
  - a `pad-margin` plant (E one short), which must FAULT.

  `--quick`: 1,613 passed / 0 failed.
- **Bounds did not move.** The padded form applies only to runs of at most
  7 bytes. The guarded worst case is still the 32-byte site: 2,661 / 2,721
  alone and 5,214 for both (§5.2).

## 2. Commits

| commit | content |
|---|---|
| fd0f3f9b | runcmp.c padded form (`rc_pad_width`, `rc_pad_bytes`, `run_cmp_pad_over`/`_decl`, `run_cmp_render_pad`); vrun.c `vrun_pad`, `vrun_verify`, the padded main path and the clamped final block; kit.h; options.def `vrun-pad` |
| 1d17becd | vrun.c module comment (PADDED VERIFY, the margin, OVER-READ extended, D149 row for E/P); G2 generator (`deny-pad` class, `overlap` meta column, the alone measurement over four trim x pad arms), driver + header (`g2v_edge`), runner (1d check, edge floors, `pad-margin` plant); cli cases; registry.md §6¶8a row + §6¶8b floor 4 -> 5; tuning.md §2.43¶3b; `simd_accept.tsv` 4 CANDIDATE lines; S797-S799; memfn/src, memfn/tests CLAUDE.md; integration.md row; simd_bounds.tsv / VRUN_W*_GUARDED_MAX comments |
| e37e893d | the `no-verify` plant keeps the padded locals used (`if (1 \|\| (...))`); S717 (SAB_COUNT 2), S719 and S720 re-anchored on `vrun_verify`'s text |
| ebfe981a | G2 SIMD runner: an instrumentation failure is a red check, not a crash |
| (tip) | this report, lanes/CLAUDE.md line |

## 3. Design decisions

**The margin is held by the guard, not assumed.** See §1. The alternative
was to pad BELOW the run, reading from `cand + off - E`. That is legal only
where `off >= E` or the lane is above `pos + E`, so it is not general.
Extending the main guard costs one comparison constant and up to E < 8
positions handled by the final block. That is nothing per byte.

**Always padded where it applies, even where the trim already left one
word.** Examples are `(?i)cat` and `(?i)union` with KB on (§4). There the
padded word is no cheaper (1 load, 1 branch either way) and no dearer. The
alternative, "padded only where it saves a word", would make the rule
depend on the trim's window arithmetic. That is a second copy of
rc_emit_words' logic in the selection, and a second thing for G2 to
re-derive. So the rule is the simple one: L in {3, 5, 6, 7}, a words row,
something left to verify, and no deny. The cost is the guard extension and
the duplicated final-block loop, about 17 instructions of helper text for
`(?i)eqeeez` (99 vs 82, gcc 15.2 -O2).

**Proven positions are zeroed in the padded mask.** Re-comparing them would
be free inside the word, and zeroing them is also free. It keeps the
compared set identical to the trimmed one, so G2's 1c rule covers both
verifies with one expected set.

**Deny-trim plus padded.** With `--memfn=no-vrun-trim`, the padded word
covers the whole run. The deny means "verify the whole run", not "use the
words". `no-vrun-trim,no-vrun-pad` is r14b's deny text.

**An observed codegen cost (not acted on).** gcc 15.2 keeps `pk` in a
register that the `and mem, reg` form clobbers, so for an 8-byte word it
re-materializes the `movabs` once per candidate (`(?i)eqeeez`). That is one
10-byte instruction with no load and no branch. Spelling the AND the other
way round would not change the text's meaning. Left for the re-timing to
show whether it matters.

## 4. Before / after (w16 helper; the w32 helper's verify text is identical in every case below, checked; its guard is 16 larger)

Arms: FULL = `--memfn=no-vrun-trim,no-vrun-pad` (r14b's deny, the whole
run), TRIM = `--memfn=no-vrun-pad`, which is byte-identical to 14143d53
(checked for all eight pattern x KB cells), and PAD = the default. KB off
adds `no-vrun-kb`. "Loads / branches" counts the per-candidate verify in
the main path: subject word loads and conditional compares, worst case (a
near miss that passes all but the last compare). gcc lowers each `&&` term
to a load, an and, a cmp and a branch (objdump of the `(?i)eqeeez` helper:
the trimmed verify is `mov; and; cmp; jne; mov; and; cmp; jne`, and the
padded one is `and (mem),reg; cmp; je`).

| pattern | KB | FULL | TRIM | PAD (main path) | main guard w16 (w32): before -> after |
|---|---|---|---|---|---|
| `(?i)cat` (L 3, E 1) | on | 2 / 2 | 1 / 1 | 1 / 1 | 18 (34) -> 19 (35) |
| `(?i)cat` | off | 2 / 2 | 2 / 2 | 1 / 1 | 18 (34) -> 19 (35) |
| `(?i)union` (L 5, E 3) | on | 2 / 2 | 1 / 1 | 1 / 1 | 20 (36) -> 23 (39) |
| `(?i)union` | off | 2 / 2 | 2 / 2 | 1 / 1 | 20 (36) -> 23 (39) |
| `(?i)eqeeez` (L 6, E 2) | on | 2 / 2 | 2 / 2 | 1 / 1 | 21 (37) -> 23 (39) |
| `(?i)eqeeez` | off | 2 / 2 | 2 / 2 | 1 / 1 | 21 (37) -> 23 (39) |
| `(?i)select` (L 6, E 2) | on | 2 / 2 | 2 / 2 | 1 / 1 | 21 (37) -> 23 (39) |
| `(?i)select` | off | 2 / 2 | 2 / 2 | 1 / 1 | 21 (37) -> 23 (39) |

The texts. In every case the final block's verify after the change is the
TRIM text, byte for byte.

`(?i)cat` (KA C@0, KB A@1):

| arm | main-path verify |
|---|---|
| KB on, before (TRIM) | `if ((rx_w2(subject + cand + 1) & rx_w2("\000\337")) == rx_w2("\000T")) return cand;` |
| KB on, after (PAD) | decl `memcpy(&pk, "\000\000\337\000", 4); memcpy(&pt, "\000\000T\000", 4);`, verify `if (((memcpy(&pw, subject + cand, 4), pw) & pk) == pt) return cand;` |
| KB off, before | `if ((rx_w2(subject + cand) & rx_w2("\000\337")) == rx_w2("\000A") && (rx_w2(subject + cand + 1) & rx_w2("\000\337")) == rx_w2("\000T")) return cand;` |
| KB off, after | `pk` = `"\000\337\337\000"`, `pt` = `"\000AT\000"`, the same verify line |

`(?i)union` (KA U@0, KB N@4):

| arm | main-path verify |
|---|---|
| KB on, before | `if ((rx_w4(subject + cand) & rx_w4("\000\337\337\337")) == rx_w4("\000NIO")) return cand;` |
| KB on, after | `pk` = `"\000\337\337\337\000\000\000\000"`, `pt` = `"\000NIO\000\000\000\000"`; `if (((memcpy(&pw, subject + cand, 8), pw) & pk) == pt) return cand;` |
| KB off, before | `... == rx_w4("\000NIO") && (rx_w4(subject + cand + 1) & rx_w4("\000\000\000\337")) == rx_w4("\000\000\000N")) return cand;` |
| KB off, after | `pk` = `"\000\337\337\337\337\000\000\000"`, `pt` = `"\000NION\000\000\000"`, the same verify line |

`(?i)eqeeez` (KA Z@5, KB Q@1):

| arm | main-path verify |
|---|---|
| KB on, before | `if ((rx_w4(subject + cand) & rx_w4("\337\000\337\337")) == rx_w4("E\000EE") && (rx_w4(subject + cand + 2) & rx_w4("\000\000\337\000")) == rx_w4("\000\000E\000")) return cand;` |
| KB on, after | `pk` = `"\337\000\337\337\337\000\000\000"`, `pt` = `"E\000EEE\000\000\000"`; one 8-byte word |
| KB off, before | `if ((rx_w4(subject + cand) & rx_w4("\337\337\337\337")) == rx_w4("EQEE") && (rx_w4(subject + cand + 2) & rx_w4("\000\000\337\000")) == rx_w4("\000\000E\000")) return cand;` |
| KB off, after | `pk` = `"\337\337\337\337\337\000\000\000"`, `pt` = `"EQEEE\000\000\000"` |

`(?i)select` (6 bytes; KA C@4, KB L@2):

| arm | main-path verify |
|---|---|
| KB on, before | `if ((rx_w4(subject + cand) & rx_w4("\337\337\000\337")) == rx_w4("SE\000E") && (rx_w4(subject + cand + 2) & rx_w4("\000\000\000\337")) == rx_w4("\000\000\000T")) return cand;` |
| KB on, after | `pk` = `"\337\337\000\337\000\337\000\000"`, `pt` = `"SE\000E\000T\000\000"`; one 8-byte word |
| KB off, before | `if ((rx_w4(subject + cand) & rx_w4("\337\337\337\337")) == rx_w4("SELE") && (rx_w4(subject + cand + 2) & rx_w4("\000\000\000\337")) == rx_w4("\000\000\000T")) return cand;` |
| KB off, after | `pk` = `"\337\337\337\337\000\337\000\000"`, `pt` = `"SELE\000T\000\000"` |

The full `(?i)cat` w16 helper after the change (the shape every padded
helper has):

```c
    if (pos >= n || n - pos < 18) return rx_reqrun__body(subject, n, pos);
    const __m128i ma = ..., va = ..., mb = ..., vb = ...;
    uint32_t pw, pk, pt;
    memcpy(&pk, "\000\000\337\000", 4);
    memcpy(&pt, "\000\000T\000", 4);
    size_t i = pos;
    for (;;) {
        unsigned m;
        if (i + 19 <= n) {
            m = <mask at i>;
            while (m) {
                size_t cand = i + (size_t)__builtin_ctz(m);
                if (((memcpy(&pw, subject + cand, 4), pw) & pk) == pt) return cand;
                m &= m - 1;
            }
            i += 16;
            continue;
        }
        if (i + 2 >= n) return n;
        size_t f = n - 18;
        if (f > i) f = i;
        m = <mask at f> & (~0u << (i - f));
        i = f;
        while (m) { ... the TRIM verify ... }
        i += 16;
    }
```

## 5. Validation (light only; pinned `taskset -c 12-15`, `-j4`, gcc 15.2, the Linux dev box; times 2026-10-11 EDT)

Logs: `/home/pcrec/.claude/jobs/e99da2a5/tmp/r14p/` (`light/`, `g2s*.log`,
`sweep_*.log`, `movers.log`, `sab_*.log`). The chain is `chain.sh` there.
It ran §5.1-5.3 on tree e37e893d. ebfe981a changes only the G2 runner's
error path.

### 5.1 Suites

| check | start-end | verdict |
|---|---|---|
| `make -j4` (all) | 02:11:18-02:11:19 | rc 0 |
| `make strict` | 02:11:19-02:11:29 | rc 0 |
| `make test-codegen` | 02:11:29-02:14:50 | rc 0; [SABANCHOR] all 677 rows' anchors resolve (S797-S799 and the re-anchored S717/S719/S720 among them) |
| `make test-registry` | 02:14:50-02:15:40 | rc 0; `[memfn floor] 5 row(s), floor 5`; the axes coverage pin is unchanged at 226 |
| `make test-spec-history` | 02:15:40-02:15:43 | rc 0 |
| `make test-memfn-simdfloor` | 02:15:43-02:16:09 | rc 0, 51/0 |
| `make test-memfn-rank` | 02:16:09-02:16:20 | rc 0, 11/0 |
| `make test-memfn-arch` | 02:16:20-02:16:27 | rc 0, 15/0 |
| `make test-memfn-stamps` | 02:16:27-02:16:46 | rc 0, 25/0 |
| `make test-memfn-guarded` | 02:16:46-02:17:52 | rc 0, 10/0 |
| `make test-memfn-rows` | 02:17:52-02:17:53 | rc 0, 152/0 (151 + the `vrun-pad` row) |
| `make test-cli` | 02:17:53-02:18:06 | rc 0, 0 failed; 319 PASS lines (r14b 317, plus the two `no-vrun-pad` cases) |
| `make test-memfn-arms` | 02:18:06-02:18:07 | rc 0, 338/0 (the scalar arm pins unchanged) |
| `make test-memfn-deleg` | 02:18:07 | rc 0, 5/0 |

### 5.2 G2 SIMD family, standalone `--quick` (`python3 memfn/tests/run_g2_simd.py --quick`)

| run | tree | start-end | verdict |
|---|---|---|---|
| g2s1 | fd0f3f9b + the runner (floors 0, measuring) | 02:03:02-02:04:58 | 1,601 / 2. The 2 failures were the runner's own bug: `plant_text`'s inner `name` shadowed the plant name. Fixed |
| g2s2 | the same, with floors set | 02:05:38-02:08:01 | 1,610 / 3. The `no-verify` plant's `if (1)` left `pw`/`pk`/`pt` unused, so the build failed under -Werror. Fixed: the plant is now `if (1 \|\| (...))` |
| **g2s3** | e37e893d's content | 02:08:23-02:10:51 | **1,613 passed / 0 failed** |
| **g2s4** (final) | ebfe981a, the code tip | 02:34:54-02:37:27 | **1,613 passed / 0 failed**: identical to g2s3 |

g2s3, in full:

- **Answers.** Every build ran 19,250,552 answer checks with 0 fails and 0
  faults: x86-64, x86-64-v3, x86-64-v4, gpr-only and asan-x86-64-v3.
- **Classes.** pos 213, and every other class 17, `deny-pad` included.
  `deny-pad` takes the 10th slot of every 20 from pos. The generator's
  random stream is unchanged, so every class except pos and deny-pad
  covers the same sites as before.
- **Verify shapes.** none 24, gap 344, whole 34, bytes 67 and words 437:
  unchanged from r14b. **padded 172**, against a floor of 137.
- **Edge.** These are main-path padded verifies whose word ends at
  `s[n - 1]`, where layout E puts a PROT_NONE page right after it:

  | build | level | evaluated | verified |
  |---|---|---|---|
  | x86-64 | w16 | 6,028 | 2,410 |
  | x86-64-v3 | w16 | 3,224 | 1,392 |
  | x86-64-v3 | w32 | 2,078 | 804 |

  The floor is (1,650, 640). Compiled-out levels read exactly 0.
- **Plants.** Every plant is RED where its level is live and green where it
  is compiled out. The new `pad-margin` plant (E one short) FAULTS at every
  live level.
- **Guarded bytes.** alone:vrun-w16 2,661 (bound 2,700), alone:vrun-w32
  2,721 (2,800) and `vrun@w32+w16` 5,214 (5,500). All are unchanged, now
  measured as the maximum over the four trim x pad arms.

### 5.3 Identity, light tier (the r14b method: the 1-in-8 corpus sample plus 8 vrun witnesses, 575 patterns, 537 reached; `scripts/emit_sweep.py --ref-bin <14143d53 build> --no-corpus`)

| arm | streams | result |
|---|---|---|
| SIMD-off (default) | c-default, c-vm, emit-ir-vm, dumps | **0 artifact movers** on all three artifact streams. The one dump that moves is `--list-axes`, by exactly the `vrun-pad` row (`sweep_off.log`, 02:18:07-09; its rc 1 is that dump). The self-check passed |
| `--extra=-fmemfn-simd` | c-default, c-vm | 9 movers each (`sweep_on.log`, 02:18:09-13). `movers.py` (`movers.log`, 02:18:18-20): 10 vrun artifacts, 9 movers, 9 of them padded, **0 bad**. Every changed line lies inside a guarded `__w16`/`__w32` helper or is the `SIMD_GUARDED_BYTES` stamp. The one vrun artifact that did not move is `(?i)abcdefghijklmnopqrstuvwxyz0123` (L > 8) |
| tree `--memfn=no-vrun-pad` (a wrapper `--bin`, `paddeny_bin.sh`) vs base, both `-fmemfn-simd` | c-default, c-vm | **0 movers** on both (`sweep_deny.log`, 02:18:13-18): the deny arm IS r14b's rendering |

Note: the moved lines are no longer only "verify lines + the stamp", as
they were for r14b. A padded helper also moves its main guard, gains the
`pw/pk/pt` declarations, gains the main path's own verify loop and
`continue`, and has its final block un-nested with the clamp line. The
check is therefore "inside a guarded vrun helper", which is stricter than
"guarded" and looser than r14b's line rule.

### 5.4 Sabotage, each run SOLO (`PROCS=1 bash tests/mech/run_sabotage_matrix.sh SNNN`, `git archive HEAD` of e37e893d)

| id | edit | arms | solo verdict (tree) |
|---|---|---|---|
| S797 | (a) the pad mask does not zero past the run end (0xDF there, compared against the zero padding) | cli g2simd | DETECTED: cli 1 fail; g2simd 189 fail / 1,424 pass (02:18:20-02:21:07, e37e893d) |
| S798 | (b) the padded form used in the final block too (`vrun_verify(..., (unsigned)e, ...)`): an over-read past n | g2simd | DETECTED: g2simd 187 fail / 1,415 pass (02:32:12-02:34:40, ebfe981a). The answers: x86-64 59,281 faults, x86-64-v3 / -v4 61,826 faults each (layout E's guard page), and the ASan build aborts on the read. The 1d check names it too ("verify 1 is padded"). The first solo run (02:21:07-02:21:12, e37e893d) read ANOMALY: the runner's instrumentation raised on the doubled padded line and crashed before printing its counts. Fixed in ebfe981a (an instrumentation failure is now a red check), then re-run |
| S799 | (c) the `vrun-pad` deny ignored | cli g2simd | DETECTED: cli 1 fail; g2simd 12 fail / 1,601 pass (02:21:12-02:25:47, e37e893d) |
| S719 | re-anchored: every verify made to accept (`if (1 \|\| ...)`), trimmed, whole or padded | g2simd | DETECTED: 573 / 1,034 (02:25:47-02:27:26, ebfe981a) |
| S720 | re-anchored: the lanes tried highest first, in both verify loops | g2simd | DETECTED: 11 / 1,598 (02:27:26-02:29:46, ebfe981a) |
| S717 | SAB_COUNT 1 -> 2: the final block's lane mask off by one, both spellings | g2simd | DETECTED: 11 / 1,598 (02:29:46-02:32:03, ebfe981a) |

S797-S799 consumed R-14's remaining ids; S800 is next free.

How S798's over-read is caught: G2's driver calls every site at every span
length in layout E. There the subject ends exactly at a PROT_NONE page, so
a final-block candidate whose padded word reaches past `n` SIGSEGVs, and
the driver counts that as a fault. The ASan build (`asan-x86-64-v3`)
poisons `[s + n, end)` and reports the same read. The 1d text check also
names it independently: the final verify is padded.

## 6. Runs longer than 8 bytes: what a vector verify would buy (not built)

Today a masked run of 9-32 bytes is verified by the words form, which
costs 2-4 eight-byte words. Two examples:

- L 9: words at offsets 0 and 1, so 2 loads and 2 branches.
- L 32: 4 words, so 4 loads and 4 branches.

A vector verify (L <= 16 one `__m128i`; 17-32 one `__m256i` in the w32
helper, two `__m128i` in the w16 one) would work like this:

- one unaligned load at `cand + off`;
- an AND with a mask vector (0x00 past the run and at proven positions);
- a cmpeq against the padded run;
- a movemask, then one compare and branch on all-ones.

That is 1 load and 1 branch (2 and 2 for 17-32 at w16), against 2-4 / 2-4.

The costs:

- **The margin grows.** E = 16 - L or 32 - L, up to 7 or 15. That is the
  same guard extension as here, only larger.
- **Two more vector constants** stay live beside ma/va/mb/vb.
- **A longer dependency chain.** vpand -> vpcmpeqb -> vpmovmskb -> cmp, a
  few cycles more than a scalar and+cmp.

For a 9-15 byte run, the scalar form's 2 loads are already close. The win
is real only at L 17-32 (4 words -> 1 vector). Whether it is measurable is
the re-timing's question: the dense-hit cells are where verify cost shows.

## 7. OWED (heavy; the kit manager's slot)

1. **Identity, the full gate, on every arm, both layers**, against
   lane/memfn-r14 @ 14143d53:
   - `python3 scripts/emit_sweep.py --tree . --ref 14143d53 --jobs 12`,
     then the same with `--arms start` and with `--variant all`. Expected:
     0 artifact movers; only the `--list-axes` dump moves, by the
     `vrun-pad` row.
   - `--extra=-fmemfn-simd`: the movers are vrun FUNC artifacts with
     L in {3, 5, 6, 7}, every changed line inside a guarded vrun helper,
     plus the stamp.
   - `-fmemfn-simd` with `--memfn=no-vrun-pad` on the tree side (the
     wrapper-bin method): 0 movers.
2. **G2:** `make test-memfn-g2-full` and `make test-memfn-g2` (all
   families). Only the SIMD family ran standalone (§5.2).
3. **make test:** `scripts/perfrun --label r14p -- <log>`. Read it with
   `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`.
4. **The mech rows anchored in vrun.c / runcmp.c.** These were not re-run
   here beyond §5.4:
   - S716, S718, S721-S723, S750-S754, S793-S796, S267, S285, S443-S445,
     S570 and S573. Their anchors resolve ([SABANCHOR], §5.1).
   - S793-S796 keep their sites.
   - S723 (RUN_WORDS) now also covers the padded path:
     `vrun_verify`'s `art->words = words` restore wraps every verify.
5. **Re-timing** (R-14's slot; ask main for the GO). Add the arm
   `--memfn=no-vrun-pad` beside DEFAULT, `no-vrun-trim`, `no-vrun-kb` and
   OFF, using slot20's RQ4 cells (dense-hit, the spacing ladder,
   pc16/short75):
   - DEFAULT vs `no-vrun-pad` isolates the padded word (the `(?i)eqeeez`
     and `(?i)select` shapes, 2 -> 1 loads);
   - `no-vrun-pad` vs `no-vrun-trim,no-vrun-pad` isolates r14b's trim.

   Watch §3's `movabs` re-materialization in the dense-hit cells.

## 8. Charter vs delivered

| charter item | state |
|---|---|
| work out and state the exact margin for cand within the block | DONE (§1): `>= VW - 1 - j` past the run for lane j, which is 0 at the top lane; held to `>= E` by the main guard `i + R + E <= n` |
| runcmp form `padded`: one over-wide masked word, smallest of w2/w4/w8 covering the run, mask 0 past the end and at proven positions, case fold on masked positions, compared to the padded folded run | DONE (`run_cmp_render_pad`; w2 never applies because L 2 is one word already). The fold is the run's own mask bytes (0xDF on a caseless letter), as in the words form |
| legal only on an explicit caller statement, never a default | DONE: `over` is a mandatory argument; a short `over` is a refusal |
| vrun uses it in the w16/w32 main path for runs <= 8; tail and `__body` unchanged; runs > 8 unchanged | DONE; L 2/4/8 are also unchanged (already one word); §6 for > 8 |
| `vrun-pad` deny + the same-change moves | DONE: options.def; registry.md §6¶8a row and §6¶8b floor 4 -> 5; tuning.md §2.43¶3b; 4 `simd_accept.tsv` CANDIDATE lines; cli cases; coverage pin 226 unchanged (verified); guarded bounds measured unchanged (comments updated) |
| SIMD-off byte-identical, light identity proof, deny == 14143d53 | DONE (§5.3) |
| G2: verify-read check (padded only in the main path, padding masked), expectations from generated data, a site at the main-path margin | DONE: 1d; the edge counter with floors (padded words ending at `s[n - 1]`); the `pad-margin` plant must fault |
| S797-S799 solo DETECTED | §5.4 |
| before/after for (?i)cat, (?i)union, (?i)eqeeez, (?i)select at w16/w32, KB on/off; load/branch counts full/trim/padded | §4 |
| OWED heavy list | §7 |
