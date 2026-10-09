# m6scope — R-10 / M6 step 1: READ-ONLY scoping of N6 (the backward walk) and VMSTRIDE (the strided VM span)

Lane m6scope (opus), 2026-10-08. Tree read: `worktrees/memfn`, branch
`lane/memfn-m7` @ 70366459 (main 5ddd2f04 + M7 + the kit's R-8/R-10 acks).
Nothing was edited and nothing was committed. No make and no suite ran.
Probes used the existing `worktrees/memfn/build/pcrec` (built 17:45) under
`gnutimeout 60`. Their outputs are in `worktrees/memfn-slot/m6scope/probes/`
(gitignored scratch, regenerable). `probes/texts_by_probe.txt` holds the
extracted loop and walk bodies. All file:line references are this branch's
tip.

## 0. Summary (resume from here)

- **VMSTRIDE needs NO new vocabulary: no `MF_VOCAB` bump.** The strided
  loop `vm_stride_loop` (emit_vm.c:4682-4692) is the kit's existing
  SKIP/ADVANCE generic render over W SET terms instead of one. The text is
  byte for byte what `stmt_advance` (memfn/src/generic.c:565-591) writes,
  provided its one `&& (member)` becomes `&& (m0) && (m1) ...`, one per term
  (§1.2). What has to change is the CONTRACT:
  - Q-G2-9 ("SKIP's one SET term at offset 0", compose.c:288-291) is
    relaxed on ADVANCE to W REQUIRED SET terms at offsets 0..W-1;
  - `MF_MAX_TERM` (8) must hold `VM_MAX_STRIDE` (32). Strides of 30 and 32
    are probed live;
  - `span_hi` is restated as the counter's cap in iterations.
  That is **`MF_SITE_ABI` 7 → 8**, a kit-only prep commit (§3.1).
- **N6 is not a search site under §R4.3.4's own exclusion.**
  - `vm_rev_emit`'s one subject-reading statement per node,
    `if (CUR > FLOOR && (T4)) { CUR--; goto L; }`, is the VM's
    one-position engine step, mirrored. Its forward twin,
    `{ scan_position++; goto L; }`, is unlisted as "the engine".
  - Everything else in the walk is engine: labels, the byte-selected
    alternation dispatch, exact-count replication, and the capture-recovery
    writes ("captures in flight").
  - A zero-mover migration would hand the kit a pair of parentheses around
    pcrec's own T4 text (§3.2).
  - **Recommendation (Q-R10-1): retire N6 by ruling.** This needs Frank,
    because Q42 named it. Delete the manifest row, the `walk-back`
    vocabulary line and its C12 row. There is then no kit change for N6.
- **A finding the manifest misses: the LAZY cursor rung's rmin prefix
  loop** (emit_vm.c:5026-5032) is an unlisted span loop at stride 1 and
  stride > 1. It is a fixed-count verify of rmin blocks. C17's vocabulary
  cannot see it (§1.4). See Q-R10-7.
- **Edit set (VMSTRIDE).**
  - pcrec side: 4 source files (emit_vm.c, memfn_sites.{c,h,def}; emit_dfa.c
    only for an explicit `stride = 1` at the two other ADVANCE builders),
    plus checks and pins.
  - Kit side: memfn.h, compose.c, generic.c, fields.def/gate.c, K1, fixtures,
    pins and CLAUDE.md files.
  - No pcrec abi event and no `docs/spec/` hunk.
- **The boundary**: V1-V15 (VMSTRIDE) and N-R1..N-R11 (N6) are named in §2.
  Every rung, admission, MRL bound, class form and stride decision stays
  pcrec's. The kit gets the loop text only.
- **Overlap verdict: DISJOINT.**
  - B4 (lane/decfbB4, 4 ahead, unmerged) edits emit_vm.c only at the
    `--emit-ir` listing (9161-9541) and the epilogue (~14042).
  - B5's sites are `esel_of` (select_engine.c:1105), `VM_PREFILTER_WHY`
    (emit_vm.c:11326) and compile.c.
  - M6 edits emit_vm.c:4654-5010 only.
  - No branch touches the span loop, `vm_rev_emit` or `stmt_advance`.
  - One sequencing note: the generated line-number maps (start_table/*,
    dec_fallback/*) conflict on merge. Regenerate them, never hand-merge
    them.
- **Ids**: S676-S685 are free on main, on every worktree and on every
  branch tree. The highest used is S651 on main and S673 on the branch.
- **Open questions:** Q-R10-1..Q-R10-12 (§8).

## 1. The edit set

### 1.1 The two migrating emitters and every site that reaches them

**VMSTRIDE.** The cursor rung `vm_cursor_rep` (emit_vm.c:4758) is
selected by `vm_rep`'s ladder (6424; the cursor rung at 6440). It calls
`vm_emit_span_scan` (4710) from two arms:
- the possessive arm (4872), with no clamp;
- the greedy arm (5003-5004), with the MRL-folded `lim_` when
  `vm_mrl_test` folds.

The lazy arm never calls it. `vm_emit_span_scan` branches on `stride`
(4721):
- stride 1 → the kit (VMSPAN, R4h);
- stride > 1 → `vm_stride_loop` (4682-4692), pcrec's text.

The body is DETERMINISTIC FIXED-LENGTH. `vm_cursor_fits` (2005) bounds W by
`VM_MAX_STRIDE` = 32 (emit_vm.c:226).

**N6.** `vm_rev_emit` (5383-5520) is reached only from `vm_revdet_rep`
(5558; walk at 5781), the reverse-deterministic rung. It is selected by
`vm_revdet_fits` (6467), which reads `revdet.c`'s verdict
`a->u.rep.revbody`.
- **Lookbehind does NOT reach N6.** `vm_look_behind_branch` (6886) steps
  back through the seam's `$_back_step` and runs the branch FORWARD.
- The seam's utf8 `$_back_step` (enc_utf8.c:302-) and `next_pos` are
  per-character decode steps, bounded at 4 bytes. They are not listed and
  are not searches (Q-R10-11).

### 1.2 Emitted text, probed

All probes use `-p rx`. The texts are in `probes/texts_by_probe.txt`.

**VMSTRIDE, byte.** The possessive arm, `--engine=vm (?:ab){2,5}c`
(probe s2):
```
    {
        unsigned long it_ = 0;
        rx_span_cursor = scan_position;
        while ((rx_span_cursor + 2 <= subject_length) && it_ < 5ULL && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {
            rx_span_cursor += 2;
            it_++;
        }
    }
```
- The greedy arm with the MRL fold (`x(?:ab)*abc`, s8) has the same loop
  over `lim_`. The block declares
  `const size_t lim_ = RX_PRUNE_CLAMP_SPAN(scan_position, 3, 2);`.
- `-fno-length-prune` (t2) puts `subject_length` back.
- `-fno-possessify` (t4) moves `(?:ab)*c` from the possessive arm to the
  greedy arm (`lim_`).
- Default auto routes to the VM through a capture: `(ab)+c` (s3,
  `RX_ENGINE "vm"`). A backreference routes there with `--features all`:
  `(a)\1(?:bc)+d` (t7).
- Range members: `(?:[a-z][0-9])+@` (s5) emits
  `((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u) && ...`.
- The stride bound is live:
  - `(?:abcdefghijklmnopqrstuvwxyz0123)+!` → `rx_span_cursor + 30 <=` (t5);
  - a 32-byte body → `+ 32 <=` (t6). That is 32 SET terms in one site.

**VMSTRIDE, `-e utf8`:**
- `é+x` and `[éè]+x` → stride 2 (`== 195) && (... == 169`);
- `(?:aé)+x` → stride 3;
- `(?:é){2,5}x` → stride 2 with the `it_` cap;
- default `(é+)x` → stride 2 through the capture route (u1-u4).

**The kit's ADVANCE render** (generic.c:582-590):
```
ind while ((more)[ && cnt < <span_hi>ULL] && <test>) {
ind     step;
ind     cnt++;
ind }
```
Here `<test>` is `member_test`'s `(m)` (generic.c:132-141).

With the hooks:
- `more` = `rx_span_cursor + W <= bound`;
- `step` = `rx_span_cursor += W`;
- `count` = `it_` (`count_by_caller` 1);
- `span_hi` = rmax;
- `indent` 8 spaces.

This reproduces the strided text EXACTLY if `<test>` is the ` && `-joined
`(m_i)` over W terms. Each `m_i` is pcrec's own `vm_cls_test` text for
position i (4814-4822); today they are concatenated into `test`. Nothing
else differs: the parenthesized `more`, the `%lluULL` cap, the `;`-less
step and the `it_++` line all match. The kit text is stride-1's VMSPAN
render with the member loop generalized.

**N6, byte** (`((a)|b){0,4}c`, r1; auto via the captures). The walk runs
from the commit label:
```
rx_L9:  if (rx_rv0_cursor <= (size_t)slot_values[6]) goto rx_L12;
        goto rx_L10;
rx_L10: if (!rx_revdet_group_seen[0]) rx_revdet_group_span[0][1] = (ptrdiff_t)rx_rv0_cursor;
        goto rx_L20;
rx_L20: if (rx_rv0_cursor <= (size_t)slot_values[6]) goto rx_L12;
        if (subject[rx_rv0_cursor - 1] == 97) goto rx_L22;
        if (subject[rx_rv0_cursor - 1] == 98) goto rx_L23;
        goto rx_L12;
rx_L22: if (!rx_revdet_group_seen[1]) rx_revdet_group_span[1][1] = (ptrdiff_t)rx_rv0_cursor;
        goto rx_L24;
rx_L24: if (rx_rv0_cursor > (size_t)slot_values[6] && (subject[rx_rv0_cursor - 1] == 97)) { rx_rv0_cursor--; goto rx_L25; }
        goto rx_L12;
rx_L25: if (!rx_revdet_group_seen[1]) { rx_revdet_group_span[1][0] = ...; rx_revdet_group_seen[1] = 1; rx_rv0_groups_seen++; }
        ...
rx_L11: if (rx_rv0_prev_position < 0) rx_rv0_prev_position = (ptrdiff_t)rx_rv0_cursor;
        if (rx_rv0_groups_seen >= 2) goto rx_L12;
        goto rx_L9;
```
(The `__attribute__((unused))` label suffixes are elided.)

The walk is reached by:
- `((a)|b)*c`, `((x)y|z){0,4}w` and `(?:x((a)|b){2}y){0,3}z` (10 steps);
- the lazy `((a)|b){0,4}?a`;
- `((H)|I){3}J` and `(([\x80-\x8f])|b){0,4}c`;
- `(?i)((a)|b){0,4}c` under both encodings;
- `-e utf8 ((a)|b){0,4}c`.

It is NOT reached by:
- `-e utf8 ((é)|b){0,4}c`: the encoding lowering clears `revbody`
  (`vm_rev_emit`'s A_WCLASS note);
- `-fno-revdet` (t3);
- `(x)(?:ab|b){0,4}c` and `(?:(x)(?:y|z)){0,3}w`, which take other rungs.

Its only C12-vocabulary form is the A_CLASS line (5407,
`")) { %s--; goto %s_L%d; }\n"`), matched by `walk-back`.

### 1.3 What moves and what stays (recommended design: VMSTRIDE migrates; N6 is retired, Q-R10-1 (a))

**pcrec side.**
- **`src/gen/emit_vm.c`.**
  - `vm_span_advance` (4654-4674) becomes THE builder for any W. It takes
    `seq` (W bitmaps) and the W member texts. It writes W sets, `more`
    `cur + W <= bound`, `step` `cur += W`, `peek` `subject[cur + 0]`, the
    cursor, `count`/`span` as today, and `stride` = W. The comment changes.
  - `vm_stride_loop` (4676-4692) is **deleted** at REPLACE.
  - `vm_emit_span_scan` (4694-4731): the signature takes `seq` + `members`
    instead of `set0`/`test`/`member`. The `stride == 1` branch (4721-4728)
    collapses to one door call, with the DELEG id chosen by W (VMSPAN at 1,
    VMSTRIDE above; Q-R10-6).
  - `vm_cursor_rep`:
    - the member loop (4810-4824) also records each position's text into a
      `members[W]` array;
    - `test` stays, because the LAZY arm still reads it (5028, 5106);
    - the two call sites (4872, 5003-5004) pass `seq`/`members`.
  - Beside `VM_MAX_STRIDE` (226): `_Static_assert(MF_MAX_TERM >=
    VM_MAX_STRIDE, ...)`, emit_dfa.c:1139's precedent (Q-R10-3).
- **`src/gen/memfn_sites.h`.** `PcrecAdvance` (171-183):
  - `set`/`member` become W-element arrays plus `stride`, or the position-0
    fields are kept and `stride`/arrays added. Either way it is set
    EXPLICITLY by every builder (no silent default, Q-R10-12);
  - the `pcrec_memfn_advance_site` doc (184-191).
- **`src/gen/memfn_sites.c`.**
  - `adv_member` (356-361) returns `members[term]` (it ignores the term
    today).
  - `pcrec_memfn_advance_site` (364-387) writes `pred.nterm = W` and W
    terms at offsets 0..W-1 through `pcrec_memfn_term_set`. Under Q-R10-4
    (A1) it also states `s` and `cursor`.
- **`src/gen/memfn_sites.def`.** New row after VMSPAN (47):
  `DELEG_SITE(VMSTRIDE, MF_OP_SKIP, DELEG_H(MF_H_ADVANCE), MF_TK_SET,
  DELEG_LOOP, MF_USE_POSITION)`.
- **`src/gen/emit_dfa.c`.** `stay_advance` (7450-7462) and `edge_advance`
  (9118-) state `stride = 1` (or `nterm 1`) explicitly. These are not in
  refactor B's edit set.
- **`src/gen/CLAUDE.md`** and **`src/gen/memfn_sites` comments**: VMSTRIDE
  delegated.

**Kit side** (the kit manager owns the spelling).
- **`memfn/include/memfn.h`:**
  - `MF_SITE_ABI` 7 → 8 (39-52);
  - `MF_MAX_TERM` 8 → 32 (58; Q-R10-3);
  - the `MF_OP_SKIP` comment (100-102): the Q-G2-9 relaxation on ADVANCE;
  - the ADVANCE hook comment (398-431): member per term, the byte at
    offset i (Q-R10-4), `span_hi` = iterations (Q-R10-5), and
    "`more` ⇒ the W bytes are readable";
  - optionally a K1 `mf_ref_skip_blocks` beside `mf_ref_skip_in_set` (645).
- **`memfn/src/compose.c`.** `site_check` (288-291): SKIP/ADVANCE takes
  1..MF_MAX_TERM REQUIRED SET terms at offsets 0..nterm-1, ascending.
  `reverse` is refused when nterm > 1. Every other SKIP keeps exactly one
  term at offset 0.
- **`memfn/src/generic.c`.**
  - `stmt_advance` (565-591): the `member_test` call (579) becomes a loop
    over `nterm` joined by ` && `, each term with its own byte expression.
  - The uses table (757-760) gains `s`/`cursor` under a strided-site gate
    if Q-R10-4 (A1).
- **`memfn/src/fields.def`, `gate.c`.** A class for "an ADVANCE predicate
  with nterm > 1" so the row contract (K96) states it. The generic row is
  the only ADVANCE row (rows.tsv).
- **Kit docs.** `memfn/{,include/,src/}CLAUDE.md`, the readers of
  `MF_SITE_ABI` found by grep (53 files today, 15 of them code or check scripts, including g2.h,
  rows_check.py, arm_fixtures.c and memfn_sites.c), and PROVENANCE if K1
  grows.
- **`memfn/tests/` (G2)** belongs to the blinded lane (§3.3).

**Checks and pins** (§5): `site_manifest.tsv`, `c12_ceilings.tsv`,
`run_deleg_sites.sh:30`, `run_form_checks.sh:23`, form_checks.py C14,
arm_fixtures + a frozen `pins/m6_target/`, rows/row_floors, gate cases, and
the S511/S526 re-aims. **Docs**: integration.md §15.x (VMSTRIDE as built),
§22 M6, §R4.3.4 (N6's disposition), and the §8.5 inventory rows at 1985,
2122 and 3570.

**N6 under (a):** no source edit. `tests/memfn/site_manifest.tsv` drops
row 54, `search_vocab.tsv` drops line `walk-back` (the commit names what it
stops seeing), and `c12_ceilings.tsv` drops `src/gen/emit_vm.c walk-back`.
It needs a D147 addendum, which is main's (Q-R10-1).

### 1.4 Finding: an unlisted span loop in the cursor rung's LAZY arm

When the lazy arm is not possessified (`a{3,}?a`, `(?:ab){2,}?ab`,
`(?:ab){2,5}?ab`, `(a)(?:ab){2,}?ab`; probe `lazy4.c`), it emits:
```
    {
        unsigned long it_ = 0;
        while (it_ < 2UL) {
            if (!(rx_span_cursor + 2 <= subject_length && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98))) goto rx_fail;
            rx_span_cursor += 2; it_++;
        }
    }
```
(emit_vm.c:5024-5032). This is a span compare over rmin×W bytes: every
block must be a member, else `goto rx_fail`. It appears at stride 1 too.

**No `search_vocab.tsv` line matches it.** `walk-open` needs an open
condition, and this `while (it_ < %dUL) {` is closed; the `if (!(...))`
is not a loop form. So C17 rule 1 is blind to it (§R4.3.4's stated limit).

The one-block extension at 5104-5107 and the greedy retreat (5099) are one
iteration each. They are engine steps, like the forward VM step. Q-R10-7
asks whether the rmin loop is a site.

## 2. The BOUNDARY: every read the migrating emitters do today

The kit gets: the loop text between `cursor init` and `}`. pcrec keeps every
decision below. Nothing here moves into the kit.

### 2.1 VMSTRIDE (V1-V15)

| # | file:line | what it reads |
|---|---|---|
| V1 | emit_vm.c:6440, `vm_cursor_fits` 2005-2015 | the cursor rung's ADMISSION: `vm_det_seq(rep->l, seq, VM_MAX_STRIDE)` (fixed length W, per-position bitmaps `seq`) and `vm_cap_offsets <= VM_MAX_BODY_CAPS`. The same predicate is read by the slot counter (2365, 2449, 2502) and the capacity analysis (3020): three sites that must agree |
| V2 | emit_vm.c:6424-6470 `vm_rep` | the rung LADDER: X{0}, then cursor, revdet, counter, frames |
| V3 | 4780 | `poss = vm_cuts(a, under_atomic)`: possessify's verdict (`a->u.rep.possessive`, `-fno-possessify`, [ART-POSS-ARMS]). It chooses which arm emits the scan (possessive 4872 / greedy 5003 / lazy none) |
| V4 | 4785-4790 | the lazy-without-verdict internal assertion |
| V5 | 4795 | `v->nocap` (inside an enclosing revdet scan) → `ncaps` |
| V6 | 4803-4804 | `vm_cls(v, seq[i])`, the class pool (the `-fno-cls-pack` atom-table re-spelling post-pass rewrites its table reads, which still pass through pcrec's buffer) |
| V7 | 4814-4822 | `vm_cls_test(v, t, ci[i], "subject[<p>_span_cursor + i]")`: each position's MEMBER TEXT (T4, rule 6). It reads the class-form table (`vm_cls_shape`/clskit ROWS; `--tune`, `-fno-cls-kit`, `-fno-cls-fold`). Passed opaque |
| V8 | 4997-4998, 4869 | MRL: `v->mrl`, `v->fmin`, `v->fdyn`, `vm_mrl_test` (the FOLD decision), `vm_mrl_amt` → `clamp` (`-fno-length-prune`) |
| V9 | 4713, 4715-4718 | `a->u.rep.rmax >= 0` → pcrec's `it_` declaration; `lim_ = <UP>_PRUNE_CLAMP_SPAN(scan_position, clamp, W)`; the cursor init |
| V10 | 4720 | `bound` = `lim_` or `subject_length`: the `more` text |
| V11 | 4721 | `W == 1` vs `> 1`: which DELEG row describes the site (VMSPAN/VMSTRIDE). A fact read, not a cost |
| V12 | 4889-4931 (poss), 5006-5013 (greedy) | AFTER the site, reading the cursor as a position: the counter-K work charge `/ W`, the rmin test, the MRL test, the capture writes from the cursor (S37's lines), `scan_position = cursor`, and the greedy frame push |
| V13 | throughout | `v->p`/`v->up`, the K79 prefix placeholder, rendered after emission by `pcrec_sb_render_prefix` |
| V14 | 4839-4860 | the listing: `vm_lbl` role, `vm_rung_mark`, `vm_prune_mark` (stream `irsb`) |
| V15 | `pcrec_memfn_site` | `pcrec_memfn_policy` (`-fmemfn-simd`), `--memfn=` opts, the deny map |

### 2.2 N6 (N-R1..N-R11), all in emit_vm.c

| # | line | what it reads |
|---|---|---|
| N-R1 | 6467 `vm_revdet_fits` | `a->u.rep.revbody`: `revdet.c`'s verdict (rd_shape, reverse one-unambiguity, `rd_alt_disjoint`), `-fno-revdet`, the [M6.4.2] exact-count lift decline |
| N-R2 | 5562-5574 | `vm_cuts`, `vm_rev_canmove`, `greedy` → `walk` (whether any walk is emitted) |
| N-R3 | 5571 | `vm_rev_caps(…, PCREC_MAX_REVDET_BODY_GROUPS)`: the body's groups, the "captures in flight" |
| N-R4 | 5563-5566, 5591 | `vm_slot_rev(loop, 0..2)` → the floor `(size_t)slot_values[se]` |
| N-R5 | 5589-5590, 5752-5755 | the names `cur`/`rv`/`ga`/`gs`/`ns` and `R.faill = wendl` |
| N-R6 | 5387 | `vm_charge`: the `PCREC_MAX_VM_NODES` limit |
| N-R7 | 5401-5407 | A_CLASS: `pcrec_cls_bits` (encoding confinement), `vm_cls`, `vm_cls_test` (T4), `vm_ev` VE_CLASS "consumed BACKWARD" (listing) |
| N-R8 | 5428-5447 | A_CAP: `vm_rev_index`, the end/start span and seen-flag writes (S52's anchor) |
| N-R9 | 5470-5499 | A_ALT: `pcrec_revdet_first` per branch, the floor test, the byte-selected dispatch |
| N-R10 | 5501-5512 | A_REP: exact-count replication |
| N-R11 | 5516-5519 | A_WCLASS loud; every other kind a hard error |

N6's statement carries no fact the kit could act on. Its member is T4;
`more` is the floor; the step and jump are labels. That is the substance of
Q-R10-1.

## 3. The VOCABULARY gap

### 3.1 VMSTRIDE: the existing triple, a relaxed rule (no `MF_VOCAB` bump; `MF_SITE_ABI` 7 → 8)

The vocab row `{MF_OP_SKIP, MF_H_ADVANCE, MF_TK_SET}` (compose.c:532)
already covers the site. A strided span is a SKIP over a predicate that is a
CONJUNCTION of position terms, which is `mf_pred`'s own meaning. Contract
additions, in contract terms:

1. **Strided ADVANCE.** On `MF_H_ADVANCE`, `pred` holds W in
   1..MF_MAX_TERM SET terms, all REQUIRED, term i at offset i (ascending,
   contiguous). The cursor advances while `more`, the cap and EVERY term
   hold at the cursor. pcrec's `step` advances it by exactly W: a caller
   precondition, the floor ≤ lo precedent.
   - The kit renders each term's membership in term order, `&&`-joined.
   - The `member` hook is called once per term with that term's id
     (generic.c:179's `pidx*MF_MAX_TERM + t`, pidx 0). It stays T4 and
     opaque.
   - `reverse` is refused when W > 1 (no customer, D77).
   - Every non-ADVANCE SKIP keeps Q-G2-9 (one term at offset 0).
2. **Reads.** With W > 1 the kit's text reads the subject only at
   `[cursor, cursor + W)`, and only while `more` holds. pcrec's `more`
   PROVES those W bytes readable: `cur + W <= bound`, with bound ≤ n.
3. **The byte at offset i** (needed only by a form that does not use the
   member hook: G2's generated sites, or a later SIMD row). See Q-R10-4.
   - **(A1)** the kit forms it as `s[cursor + i]`, so a strided site states
     `s` and `cursor` (forward only).
   - **(A2)** `peek` becomes a template with `@` for the offset (M7's
     `fold` precedent).
   - Recommend (A1).
4. **`span_hi` on ADVANCE caps the COUNTER**, which counts ITERATIONS (W
   bytes each). The proven byte span is `span_hi × W`. This is identical to
   today's reading at W = 1, and it keeps `it_ < <rmax>ULL` byte-identical.
5. **`MF_MAX_TERM` ≥ 32** (`VM_MAX_STRIDE`). This is a layout change
   (`mf_pred.term[]`). A 32-byte body is probed live (t6), and a declined
   W > 8 would leave a half-delegated site (D122 forbids it).

The generic row renders it. That is the totality obligation (§14.6), and it
is already the only ADVANCE row. The frozen-target rule (R4h
`pins/r4h_target/`) applies: one pinned file per strided shape, taken
verbatim from pcrec's `vm_stride_loop` text before REPLACE. The shapes are
poss/`subject_length`, greedy/`lim_`, with and without `it_`, and W = 2, 3
and 32.

**Alternative (B), not recommended:** a new term kind "a run of byte sets"
(`MF_T_SETRUN`: `run_len` = W, `sets` pointer). It keeps `nterm = 1` and
`MF_MAX_TERM`. But it costs `MF_VOCAB` 4, a new per-position member-id
convention, and a second spelling of "conjunction of positions" beside
`mf_pred`.

### 3.2 N6: what the vocabulary would have to be, and why the recommendation is no vocabulary

There are three ways to describe the walk to the kit.

- **(a) Retire (recommended).** §R4.3.4 excludes "any DFA or VM step" and
  T4 one-position membership. N6's statement is exactly a VM step on a T4
  test. The house already says so for the forward direction: the
  `walk-back` line's own doc says "the forward VM's own per-byte step is
  the engine and is `++`".
  - "Every search site migrates" is satisfied because N6 is not one.
  - **C17 end state:** 0 pending once N7U migrates, and Q-R10-7's
    resolution decides the lazy loop.
- **(b) Per-node, no new vocabulary (vacuous).**
  - **Describe the step as an existing site.** Each A_CLASS state's test is
    an EXPR `VERIFY/BOOL` over one SET term at offset 0, with
    `cand = CUR - 1`, `guard_by_caller` 1 (pcrec's `CUR > FLOOR` is the
    guard) and the member hook T4.
  - **What the kit's generic render (`pred_test`, generic.c:147-215) does
    with it.** It wraps `(m)` in a second pair. The result is
    `if (CUR > FLOOR && ((T4)))`: one paren pair moves per backward step.
  - **Getting to zero movers.** It needs either:
    - a pcrec-side normalization abi event first (advnorm's abi-67
      precedent), or
    - a kit row that renders a guarded single-member predicate bare.
  - **Why it is still the wrong answer.** Either way the kit owns two
    parentheses around pcrec's text. Completeness would then also demand
    the forward step (vm_emit A_CLASS and the wide-class arms at 8743,
    8845 and 8863: same shape, `++`). That pulls the engine's per-byte
    step into the manifest.
- **(c) A "backward walk with captures in flight" vocabulary.** This is
  what §R4.3.4 anticipated. The kit would render maximal backward literal
  runs as one compare, with pcrec statements (the A_CAP span writes, the
  A_ALT dispatch) pasted at in-flight positions.
  - It is a MOVER: the per-byte labels collapse.
  - compare_stack.md §5 already files it with a trigger: "a census of
    cursor/backward bodies of length >= 3 plus a cell".
  - It is not completeness work (D77).

### 3.3 G2 needs, in contract terms (for the blinded author)

1. **The oracle (strided ADVANCE).** Given a cursor c0, W sets S_0..S_{W-1},
   an optional cap K and a bound B:
   - the final cursor is c0 + j·W, where j is the least j ≥ 0 such that
     c0 + (j+1)·W > B, or j = K (if capped), or some i < W has
     s[c0 + j·W + i] ∉ S_i;
   - the counter is incremented exactly j times from its start;
   - at W = 1 this is today's ADVANCE.
2. **The generated space.**
   - W ∈ {1, 2, 3, 7, 8, 9, 16, 31, 32}, plus MF_MAX_TERM + 1 refused;
   - B − c0 around every multiple of W ± 1 (a partial final block is never
     read);
   - caps 0, 1, K just below or above the run length, and unbounded;
   - per-position sets: singleton, range, sparse bitmap, full, and EMPTY at
     one position (j = 0);
   - subjects where position i fails at every i < W.
3. **Read bounds under guard pages:** the subject ending exactly at B (no
   read of `s[B]`), and `s` NULL with B = 0 (`more` false at entry; nothing
   read).
4. **Hook spellings.**
   - `count_by_caller` 0 and 1;
   - the member hook present (pcrec's shape) and absent (the kit's own set
     test, which exercises Q-R10-4's byte at offset i);
   - `more` CONJ, `step` EXPR_STMT, `peek` POSTFIX as today.
5. **Refusals and declines.**
   - W > 1 with `reverse` 1;
   - offsets not 0..W-1, or not ascending;
   - an OPTIONAL term;
   - a non-SET term;
   - W > MF_MAX_TERM;
   - a non-ADVANCE SKIP with nterm > 1 (Q-G2-9 still holds there);
   - `MF_SITE_ABI` 7 at an 8 kit.
6. **Rows:** check (b) reaches the generic row on strided sites. FLOOR_ROWS
   is unchanged, because there is no new row. `G2_MAXT` (g2.h:33, "the
   header's MF_MAX_TERM") is re-read.

## 4. The OVERLAP CHECK (D153)

- **Worktrees** (`git -C`, each vs main 5ddd2f04):
  - decfbB0, decfbB2, decfbB3 and r9d: 0 ahead, clean.
  - m4, r4h: 0 ahead (an untracked rulings file only).
  - g2u, m7, s670cell: inside `lane/memfn-m7`'s history (M7/G2m7).
    s670cell has dirty `tests/backrefs` corpora and rxtsource, none in
    M6's set.
  - **decfbB4: 4 ahead, unmerged.**
- **Branches:** `for-each-ref` finds ONE branch ahead of `lane/memfn-m7`
  that touches an M6 file, lane/decfbB4 (emit_vm.c).
- **B4** (`d78a0b97..2eaa2429`). Its emit_vm.c hunks are at 9161 and 9386
  (deleted blocks), 9474-9541 (`vm_render_listing`'s `--emit-ir` prefilter
  chain, now the row's listing cells) and ~14042 (`vm_emit_epilogue`). It
  also edits select_engine.c, compile.c (6 lines), internal.h and tests.
  **None is in 4654-5830, `memfn_sites*`, `emit_dfa.c` or `memfn/`.** Its
  hard gate is the emit-ir-auto stream identical, so it has no movers.
- **B5** (not started; dec_fallback.md:633-634): `esel_of`
  (select_engine.c:1105), the PFLW ternary and `size_term_why`
  (compile.c), and `VM_PREFILTER_WHY` (emit_vm.c:11326). **Disjoint.**
- **Strided span loop / backward walk in flight:** none. No plan.md row is
  live on the cursor rung, revdet or the span loop: [OPT-VMLIT] and
  [ENG-DIRECT] are not-started.
- **R-9** (lane r9d, R4e′ design pass, at main, design only) is the one
  CONCEPTUAL neighbour. A SIMD form of VMSPAN/VMSTRIDE reads what §3.1
  states (the per-position sets, the subject and the cursor) and needs a
  numeric bound that `more` (a CONJ predicate) does not give. See
  Q-R10-10.
- **VERDICT: DISJOINT.** Sequencing notes:
  1. **Ref.** The identity gate's `--ref` is M6's merge-base. If B4 or B5
     merges to main first, merge main into the M6 branch, then re-take the
     ref.
  2. **Generated maps.** `docs/design/start_table/{call_graph.txt,
     sabotage_anchors.tsv}` and `docs/design/dec_fallback/{call_graph_fallback.txt,
     sabotage_anchors.tsv,...}` record emit_vm.c LINES. B4 regenerates the
     latter, and M6 shifts emit_vm.c lines above B4's hunks. Expect a
     generated-file conflict: re-run the generators after the merge and
     never hand-merge. Run `git merge` alone.
  3. **Re-aims.** B4 re-aims S102, S165, S176, S216, S272, S612, S625 and
     S640. None is in M6's anchor set.

## 5. Checks

- **`tests/memfn/site_manifest.tsv`.**
  - Under VMSTRIDE delegated: its emitters are `vm_span_advance,
    vm_emit_span_scan`, and its companions are `vm_cursor_rep` (an
    existence check).
  - N6: retired under Q-R10-1 (a) (row 54 deleted). Under (b) it would be
    flipped to delegated.
  - `C17_ROW_FLOOR` (`run_site_manifest.sh:38`): 14 → 13 under (a). Add 1
    if Q-R10-7 lists the lazy loop.
- **`search_vocab.tsv`.**
  - `walk-open` stays. Its doc's "span loops whose byte test is not theirs"
    still describes nothing pcrec spells once VMSTRIDE leaves, so add the
    note.
  - `walk-back` is deleted under (a), and the commit names what it stops
    seeing.
  - If Q-R10-7 lists the lazy loop, a new line is needed, e.g.
    `while \(it_ < %dUL\) \{`. Then rule 4 can see the pending row.
- **C12 (`c12_ceilings.tsv`).**
  - Delete `src/gen/emit_vm.c walk-open 1`, since the strided loop was its
    last form outside the kit. Under (a) also delete `walk-back 1`.
  - `C12_CEIL_ROWS_FLOOR` (`run_form_checks.sh:23`): 3 → 1 under (a)
    (only `enc_utf8.c span-decode` stays), or 3 → 2 if N6 stays pending.
- **C10 (`run_deleg_sites.sh:30`).** `D91_LOOP` gains VMSTRIDE (budget 2:
  the span loop runs per VM step). `{SKIP, ADVANCE, SET}` passes
  `mf_vocab_has` unchanged.
- **C14 (form_checks.py:151-199, emit_dfa.c:1139).**
  - Add `MF_MAX_TERM >= VM_MAX_STRIDE`. `VM_MAX_STRIDE` is an emit_vm.c
    enum, not a limits.def row. Moving it into limits.def would add a
    `--list-limits` row, which is caller-observable and needs a spec hunk:
    avoid it.
  - Use a `_Static_assert` in emit_vm.c beside line 226, and add
    form_checks.py's control for it.
- **C5 (arm pins).**
  - Strided fixtures in `arm_fixtures.c`.
  - A frozen `tests/memfn/pins/m6_target/` (verbatim `vm_stride_loop`
    text), with run_arm_pins.sh's byte-for-byte check and a planted
    control.
  - ARMS_ROW_FLOOR and the gate cases for each §3.3 refusal.
- **N4 rows.** `rows.tsv`/`row_floors.tsv`: the generic row's witness
  `a[^x]*` is unchanged. Consider a second witness signature for the
  strided render (`&& (subject[rx_span_cursor + 1]`).
- **S511** (re-aimed to VMSTRIDE at M4; its anchor, the `while ((` line at
  4686, is DELETED at REPLACE). Two targets:
  - **Recommended (durable):** plant on `tests/memfn/site_manifest.tsv`,
    flipping a `delegated` row (VMSTRIDE) to `pending`. Its emitter spells
    no form, so rule 4 fires.
    - It survives N7U's migration, after which there is nothing pending to
      plant on.
    - `SAB_REACH_POP` becomes `^VMSTRIDE[[:space:]]+vm_span_advance.*delegated`.
  - **Alternative:** N7U's one form, enc_utf8.c:199
    `"... ? $_decode(s, n, j, &y) : 0;\n"` → `$_decode (s, ...`. The space
    defeats `\$_decode\(s,` but keeps valid C. Rule 4 fires on N7U, and
    C12's `span-decode` ceiling reads 0 < 1. This dies when N7U migrates.

## 6. Sabotage

### 6.1 Rows whose anchors move, or whose detection now runs through the moved text

| row | file | effect of M6 | action |
|---|---|---|---|
| S511 | emit_vm.c:4686 | **anchor deleted** (vm_stride_loop) | re-aim (§5) |
| S526 | memfn.h:58 `#define MF_MAX_TERM 8` (+ emit_dfa.c:1139) | **moves** if MF_MAX_TERM → 32 | re-anchor; the plant lowers below the new C14 bound (both `_Static_assert`s fire) |
| S616 | generic.c cap line | text unchanged; the plant (`count_start != 0`) now also drops VMSTRIDE's cap | solo re-run; DETECTED with more reach |
| S214 | generic.c cap line | the same line; scoped `count_start != 1` (the scan edge) | solo re-run |
| S37, S39, S56, S57, S61 | vm_cursor_rep (4934/5081, 4946/5095, 4896/5006/5015, 4863, 4997) | text anchors in unchanged lines (the member loop and call lines move around them) | solo confidence set (vm, counterkdiff, mrl/mrldiff) |
| S51, S52 | vm_revdet_rep 5722, vm_rev_emit 5434/5441 | unchanged under Q-R10-1 (a) | none; under (b), re-run S52 (harness, rungdiff) |
| S68, S185, ... | other kit files | untouched | — |

Run `scripts/m6read_check_sab_anchors.py`, and
`sabotage_anchors.py --step` per commit (the admin1008b diff-derived
`rerun_at`).

### 6.2 Proposed new rows (S676-S685, grepped free)

| id | plant | expected detector |
|---|---|---|
| S676 | kit `stmt_advance`: only term 0's member rendered when nterm > 1 | harness/vm (`(?:ab)+c` accepts "axc…"), memfnarms (pin) |
| S677 | kit: the strided members joined by `\|\|` | harness/vm, memfnarms |
| S678 | pcrec `adv_member` ignores `term` again (returns members[0] for every term) | harness/vm (`(?:ab)+` vs "aa"), memfnarms |
| S679 | pcrec `vm_span_advance`'s `more` keeps `+ 1` at W > 1 (a partial final block is read) | san/asan arm (reads `s[n]`); harness possibly. MEASURE |
| S680 | VMSTRIDE builder states `span` UNBOUNDED (the `it_` cap lost) | harness (`(?:ab){2,5}c` on "ababababababc"), S616's sibling |
| S681 | kit `site_check` accepts `reverse` 1 with nterm > 1 | memfnarms gate case, G2 |
| S682 | kit `site_check` accepts non-contiguous offsets (0, 2) | memfnarms gate case, G2 |
| S683 | `memfn_sites.def` VMSTRIDE budget `DELEG_SCAN` | memfndeleg (C10) |
| S684 | pcrec re-spells the strided loop (`vm_stride_loop` restored) while VMSTRIDE is delegated | memfnmanifest (C17 rule 3), memfnforms (C12 walk-open ceiling 0). S673's analogue |
| S685 | under Q-R10-7 "list": the lazy-loop vocabulary line deleted (C17 rule 4 then fires on the pending row). Otherwise: MF_MAX_TERM lowered to 31 (the `_Static_assert` at emit_vm.c fires at build) | memfnmanifest, or memfnforms + every build |

Recommended minimum: S676, S678, S680, S681 and S684. S679 is MEASURE
first. Under Q-R10-1 (b), add one row on N6's new site and take the next
block.

## 7. Identity-gate reach (zero movers)

- **The sweep.** `scripts/emit_sweep.py --ref <M6 merge-base>`, judged by
  `docs/design/memfn/probes/lxrun/memfn_r4c_gate.py --zero-dumps`. Both
  bases, `byte,utf8` (the default), all six streams.
- **`--extra` arms:**
  - `--engine=vm` (the cursor rung on every fixed-length repeat);
  - `-fno-possessify` (moves the scan between the possessive and greedy
    arms);
  - `-fno-length-prune` (`subject_length` instead of `lim_`);
  - `-fno-revdet` (it removes N6 and pushes revdet bodies to
    counter/frames; a null arm under (a));
  - `--tune=-2` and `-fno-cls-kit` (member text shapes);
  - `-fno-cls-pack` (the atom re-spelling post-pass over kit text);
  - `-fcomments`;
  - `-fmemfn-simd`.
- **Reach, printed per (base, stream, arm), each > 0:**
  - VMSTRIDE: artifacts matching `_span_cursor \+ ([2-9]|[1-9][0-9]+) <=`;
  - VMSPAN (a control): `_span_cursor \+ 1 <=`;
  - N6: `_rv[0-9]+_cursor - 1\]`.
  - A sweep that never reaches the site proves nothing (MECH-REACH).
- **The I1 shadow comparator** (R4h's `pcrec_memfn_advance_shadow`, M4/M7
  shape) is extended to W > 1 at IMPLEMENT. It runs over both comment
  tiers, `--engine=vm` and `-e utf8`.

**Witness tier** (`.c`, `.h`, rc and stderr against a pre-edit binary copy):
- **byte:**
  - `(?:ab)*c` (possessive, `subject_length`);
  - `(?:ab){2,5}c` (`it_` cap);
  - `x(?:ab)*abc` (greedy, `lim_`), the same with `-fno-length-prune`, and
    `-fno-possessify (?:ab)*c`;
  - `(ab)+c` (DEFAULT auto, capture route);
  - `--features all (a)\1(?:bc)+d` (backreference route);
  - `(?:[a-z][0-9])+@`, and the same with `--tune=-2`/`-fno-cls-kit`;
  - a bitmap-member body such as `(?:[aeiou][^aeiou])+x`;
  - `(?:abcdefghijklmnopqrstuvwxyz0123)+!` (W = 30) and
    `(?:abcdefghijklmnopqrstuvwxyz012345)+!` (W = 32, the bound).
- **utf8 (`-e utf8`):**
  - `é+x`, `[éè]+x`, `(?:aé)+x` (W = 3), `(?:é){2,5}x`;
  - default `(é+)x`.
- **Controls that must stay byte-identical with NO site:**
  - the lazy `(?:ab){2,}?ab` and `a{3,}?a` (the unlisted lazy loop);
  - stride-1 `a[^x]*` (VMSPAN).
- **N6 (expected unchanged under (a)):**
  - `((a)|b){0,4}c`, `((a)|b)*c`, `(?:x((a)|b){2}y){0,3}z`,
    `((a)|b){0,4}?a`, `(([\x80-\x8f])|b){0,4}c`;
  - `(?i)((a)|b){0,4}c` under both encodings, and `-e utf8 ((a)|b){0,4}c`;
  - controls: `-e utf8 ((é)|b){0,4}c` and `-fno-revdet ((a)|b){0,4}c`
    (no walk).
- **Cross-cuts:** `-p <60-byte prefix>`, `--emit-main`, split output
  (`-o x.c` writes `.h`).
- **Engine flags that reach the VM:** default `auto` (a capture, backref or
  lookbehind forces `RX_ENGINE "vm"`), `--engine=vm`, and `--features all`
  (backrefs, recursion, vars). `--no-captures (ab)+c` routes to the DFA:
  a reach control, not a witness.

**Answer-level suites that must stay green** (zero movers, so they are
controls): vm, harness corpus, counterkdiff, mrl/mrldiff, rungdiff,
possdiff and `test-memfn-*`.

## 8. Risks and open questions

- **Q-R10-1. N6's disposition.**
  - The options:
    - (a) retire it as an engine site: manifest row, `walk-back` line and
      C12 row deleted; no kit change;
    - (b) per-node `VERIFY/BOOL` with `guard_by_caller`: needs a paren
      normalization or a bare-render row; the kit owns nothing; and
      completeness then pulls in the forward VM step;
    - (c) a backward-run vocabulary with in-flight hooks: a mover, already
      filed with a D77 trigger.
  - **Recommend (a).** It reverses part of Q42's named list, so it is
    Frank's ruling, recorded as a D147 addendum (main's). If Frank keeps
    N6 in scope, prefer (b) with a pcrec normalization abi event first
    (advnorm precedent), and file the forward-step consequence.
- **Q-R10-2. VMSTRIDE's vocabulary.**
  - The options:
    - (A) W SET terms on ADVANCE: no `MF_VOCAB` bump, `MF_SITE_ABI` 8;
    - (B) a SET-RUN term kind: `MF_VOCAB` 4.
  - **Recommend (A).** It is the predicate's existing meaning, reuses the
    per-term member callback unchanged, and adds no second spelling.
  - R-10's text expects an `MF_VOCAB` bump. This scoping finds none is
    needed.
- **Q-R10-3. The term bound.**
  - The options:
    - raise `MF_MAX_TERM` to 32, with `_Static_assert(MF_MAX_TERM >=
      VM_MAX_STRIDE)` in emit_vm.c;
    - a separate stride bound;
    - decline W > 8 (rejected: two spellings of one site).
  - **Recommend raise.** The ripple:
    - `mf_pred` grows (~2 KB per site, arena);
    - S526 is re-anchored;
    - G2's `G2_MAXT` and its `nterm-over-max` case are re-read;
    - emit_dfa.c:1127's `sig` buffer scales by itself.
- **Q-R10-4. The byte at offset i for kit-owned reads.**
  - The options:
    - (A1) `s[cursor + i]`: a strided site states `s` and `cursor`, forward
      only;
    - (A2) a `peek` template with `@`.
  - **Recommend (A1).** No new hook, and it is what a SIMD ADVANCE row
    needs anyway. pcrec's route never uses it (the member hook), so it is
    zero movers either way.
- **Q-R10-5. `span_hi` on ADVANCE.** **Recommend:** restate it as the
  counter's cap in ITERATIONS. At W = 1 nothing changes, and it keeps
  `it_ < <rmax>ULL`. Under the bytes reading, pcrec would pass rmax·W and
  the kit would divide.
- **Q-R10-6. One builder, and one DELEG row or two.** **Recommend:**
  - ONE builder (`vm_span_advance`, generalized), and `vm_stride_loop`
    deleted;
  - keep a distinct `DELEG_SITE(VMSTRIDE)` row and manifest row. Reach and
    C10 accounting per stride class then stay visible, and the manifest
    keeps its history.
  - The alternative folds VMSTRIDE into VMSPAN (C17 floor −1).
- **Q-R10-7. The lazy cursor rung's rmin prefix loop** (emit_vm.c:5024-5032,
  §1.4). It is an unlisted span loop at every stride, and C17's vocabulary
  is blind to it.
  - **Recommend:** list it now as `pending` (row e.g. VMLAZY, emitter
    `vm_cursor_rep`, with a new vocabulary line), in M6's prep or REPLACE
    commit.
  - Migrate it later. It needs a counted ADVANCE with a must-reach-K exit,
    or VERIFY over a counted run of position sets: either is a vocabulary
    step with its own G2.
  - The alternative is to rule it an engine step. It is not: it reads
    rmin×W bytes in a loop.
- **Q-R10-8. S511.** **Recommend** the durable manifest-status plant (§5).
  The N7U decode plant dies when N7U migrates.
- **Q-R10-9. The gate's ref under refactor B.** **Recommend** ref = M6's
  merge-base; merge main after any B merge and re-take it. Regenerate the
  line-number maps after merges (§4).
- **Q-R10-10. R-9 coordination.**
  - A SIMD form of VMSPAN/VMSTRIDE needs the per-position sets (§3.1), the
    subject and cursor (Q-R10-4 A1) and a NUMERIC bound. ADVANCE gives only
    `more`, a predicate (Q-G2-5).
  - **Recommend:** M6's ADVANCE statement lands first, or R-9 cites it.
  - A numeric bound waits for R-9's first ADVANCE SIMD form (D77: not
    added in M6).
- **Q-R10-11. The seam's utf8 `$_back_step`/`next_pos` loops** (bounded
  per-character decode steps, enc_utf8.c:302-). **Recommend:** record them
  explicitly as NOT search sites, beside T4 in §R4.3.4's exclusion list, so
  the completeness reading is not re-litigated.
- **Q-R10-12. `PcrecAdvance`'s new stride field.** The STAY/EDGE builders
  use compound literals, and an omitted field is a silent 0. **Recommend:**
  every builder states `stride` (and `nterm`) explicitly, emit_dfa.c:7454
  and 9123. `pcrec_memfn_advance_site` refuses 0 (no presumed value).

**Other risks:**
1. CLSPACK's atom-table re-spelling runs over the finished buffer, so it
   reaches the kit's text. VMSPAN already proves this path; witness a
   strided body with ≥ 11 table-read classes.
2. `MF_SITE_ABI` 8 touches 53 files by grep (15 code or check scripts), G2 included. G2 is red
   until the blinded lane lands, as at M4 and M7.
3. `vm_emit_span_scan`'s new signature has two callers. `test` stays alive
   for the lazy arm. Do not delete it with `vm_stride_loop`.
4. The member texts are Job-scratch-backed today (`Job.scr_test`). The
   per-position copies must be arena fragments (`vm_rolef`, as `member`
   already is) so they live until `mf_art_end` (Q-G2-7).

## Charter checklist

| item | section |
|---|---|
| 1. Edit set (file:line, emitted text per site, both encodings, what moves vs stays) | §1.1-§1.4; probes/ |
| 2. The boundary: every read named (V1-V15, N-R1..N-R11) | §2.1-§2.2 |
| 3. Vocabulary gap: contract additions, bumps, G2 needs; existing-op answer | §3.1-§3.3 |
| 4. Overlap check (B4, B5, worktrees, branches, plan rows, R-9); verdict | §4 |
| 5. Checks: manifest, C17/C12/C10/C14 literals and floors, S511 re-aim | §5 |
| 6. Sabotage: moved anchors; new rows S676-S685 (grepped free) | §6.1-§6.2 |
| 7. Identity-gate reach: witnesses, arms, both encodings, VM engine flags | §7 |
| 8. Risks and Q-R10-n with recommendations | §8 |
