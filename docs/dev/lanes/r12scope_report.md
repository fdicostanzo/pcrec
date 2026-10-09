# r12scope — R-12: READ-ONLY scoping of VMLAZY and N7U, the last two `pending` sites

Lane r12scope (opus), 2026-10-09. Worktree `worktrees/r12`, branch
`lane/memfn-r12`, cut from main a681d78f (tip at start 9f61f2aa, the kit's
R-12/R-13 ack). Nothing under `src/`, `memfn/` or `tests/` was edited. No
`make test`, mech or heavy run. One `make -j4` of the worktree, then light
probes, pinned `taskset -c 12-15` under `gnutimeout`. The probe outputs are in
`worktrees/r12/.scratch/` (uncommitted, regenerable). All file:line references
are this branch's tip.

Precedents followed: `m6scope_report.md` (VMSTRIDE/N6, where VMLAZY was found,
Q-R10-7), `m7scope_report.md` (N7, where N7U was split off, Q-R8-1), D147
addendum 12 (N6 retired as "an engine step mirrored, not a search"), and D58
addendum 2 (the seam's no-callback site token, whose revisit clause names N7U).

## 0. Summary (resume from here)

- **VMLAZY: MIGRATE, by RE-EXPRESSION, with no new vocabulary and no kit
  change.** Recommended path in §1.5:
  - The lazy rmin prefix is the cursor rung's mandatory iterations.
  - The rung's other two arms already spell their mandatory iterations a
    different way: through the delegated span scan (`vm_emit_span_scan`,
    VMSPAN/VMSTRIDE, the existing ADVANCE), followed by pcrec's own cursor
    reach test.
  - So the lazy arm can take the same two pieces: one more call of
    `vm_emit_span_scan` with a cap of rmin, then the reach test.
  - That makes it neither of R-12's two candidate gaps (a "counted ADVANCE
    that must reach K", or "VERIFY over a counted run"). The general
    mechanism already exists.
  - **No `MF_SITE_ABI` and no `MF_VOCAB` move.** It IS a pcrec abi event,
    because the emitted text moves.
  - The house shape is advnorm's: (1) pcrec normalizes the prefix to the
    ADVANCE layout plus the reach test (the abi event, object-code movers,
    a G1 null reading), then (2) REPLACE routes it through the door with zero
    movers.
  - The manifest row VMLAZY is then deleted, not flipped (Q-R12-2). Its
    instances are VMSPAN/VMSTRIDE instances.
  - **Retire was argued honestly (§1.4) and declined.** 106 of 135 corpus
    instances are rmin = 1, where the "loop" is the extension step run once.
    But VMRUN, VMSPAN and VMSTRIDE already establish that a multi-position
    verify in the VM is a kit site.
- **N7U: RETIRE BY RULING (recommended), with the criterion stated as a
  rule, not a special case.** The kit's domain is BYTES:
  - every `mf_term` is a byte set or a byte run;
  - every fold fact is a byte relation;
  - every read is `s[...]`.
  - N7U's predicate lives in the encoding's CHARACTER domain: the operands
    come from the encoding's decoder, the fold is over code points, and the
    result's length depends on the encoding.
  - Migrating it would hand the kit two cursors, a loop and a `!=` around
    three pieces of pcrec's text (decode, fold, failure statement), and no
    fact it could act on.
  - That is N6's "parentheses around pcrec's text", one domain over. It is
    also exactly what Q-R10-11 already ruled for the same backend's
    per-character decode steps (`$_back_step`, `next_pos`).
  - **The migrate case is spelled out (§2.3-§2.4) in case Frank keeps it**:
    - `MF_VOCAB` 3 → 4: one new handoff, whose result is promised on EQUAL;
    - `MF_SITE_ABI` +1: a `unit_kind` fact, a `decode` hook, `fold_kind`
      MF_FOLD_CP;
    - a D58 addendum-2 revisit;
    - it should land AFTER R-13 batch 1's and R4j's own `MF_SITE_ABI`
      events.
- **A finding the manifest misses: `$_valid_upto`** (`enc_utf8.c:431-471`,
  [UTF-VALID], abi 50). Its ASCII SWAR skip is a real BYTE-domain search
  site that is not listed:
  - the loop is `while (n - p >= 8) { memcpy(&w, s + p, 8); if (w &
    0x8080…) break; p += 8; }`, a SKIP over {0x00..0x7F};
  - it runs once per call under `-futf-check`;
  - no `search_vocab.tsv` line sees it (checked: 0 of its 40 literals
    match).
  - Under the byte-domain criterion its ASCII skip is the kit's, and its
    decode body is the encoding's. Q-R12-5: list it as `pending` (row VALID).
- **Overlap with R-13: DISJOINT in code, with three serialization points**
  (§3):
  - VMLAZY's edit set is `emit_vm.c` (`vm_cursor_rep`'s lazy arm,
    `vm_emit_span_scan`/`vm_span_advance`'s cap), the manifest/vocab/C12
    files and the abi readers. It touches no `memfn/` file, `fn_rows[]`,
    PREFIX row, sink op or `options.def`.
  - It moves `job->vmsb`'s length, which RQ-3's `pcrec_sb_len_decide` feeds
    to the VM entry-shape knee. That is a mover census item, not a conflict.
  - N7U-if-migrated collides with batch 1 on `memfn.h`: the `MF_SITE_ABI`
    line, and append-last tails on `mf_site`/`mf_hooks` beside batch 1's
    `mf_sink`/`mf_pred` appends. It also collides with `compose.c`'s
    `site_check`/`vocab[]` beside `kit_walk`.
  - pcrec abi numbers serialize with RQ-3 (71) and anything after it.
- **Before R4j/M5?** (§4)
  - **VMLAZY: yes, it may go first.** It is disjoint from the planner,
    needs no kit contract, and takes C17 one row toward 0.
  - **N7U:** rule it now (docs-only if retired). If it migrates, build it
    AFTER R4j, so three `MF_SITE_ABI` events do not interleave.
- **Sabotage ids S706-S715** are free on main, on every worktree and on
  every branch tree. The budget per site is in §5.2. S685 dies with VMLAZY
  and must be retired or re-aimed in the same commit.
- **Open questions:** Q-R12-1..Q-R12-7 (§7).

## 1. VMLAZY — the cursor rung's lazy rmin prefix

### 1.1 The edit set and the emitted text

**Where.** `vm_cursor_rep` (`src/gen/emit_vm.c:4753`), the LAZY arm (the
`else` at 5013). When `rmin > 0` it emits a braced block (5026-5033):

```c
pcrec_sb_puts(b, "    {\n        unsigned long it_ = 0;\n");
pcrec_sb_printf(b, "        while (it_ < %dUL) {\n", a->u.rep.rmin);
pcrec_sb_printf(b, "            if (!(%s_span_cursor + %d <= subject_length%s)) goto %s_fail;\n",
                v->p, stride, test, v->p);
pcrec_sb_printf(b, "            %s_span_cursor += %d; it_++;\n", v->p, stride);
pcrec_sb_puts(b, "        }\n    }\n");
```

`test` is the `&& (m0) && (m1) …` string the member loop (4811-4822) builds
from `vm_cls_test` per position. It is the same `members[i]` the delegated
scan already receives. The arm is reached only when `vm_cuts()` is false (the
loop is not possessified) and the quantifier is lazy.

**Emitted, byte, stride 2** (`--features all (a)(?:ab){2,}?ab`, default auto
→ VM through the capture):
```c
    RX_SET(RX_SLOT_SPAN_LOW0, (ptrdiff_t)scan_position);
    rx_span_cursor = scan_position;
    {
        unsigned long it_ = 0;
        while (it_ < 2UL) {
            if (!(rx_span_cursor + 2 <= subject_length && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98))) goto rx_fail;
            rx_span_cursor += 2; it_++;
        }
    }
    goto rx_L6;
rx_L6: __attribute__((unused));
    if (RX_PRUNE_TOO_SHORT(rx_span_cursor, 2)) goto rx_fail;
    RX_PUSH(&&rx_L7, rx_span_cursor);
    ...
rx_L7: __attribute__((unused));            /* the extension step: ONE block */
    rx_span_cursor = scan_position;
    if (!(rx_span_cursor + 2 <= subject_length && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98))) goto rx_fail;
    rx_span_cursor += 2;
    goto rx_L6;
```

**Emitted, byte, a class member, stride 1** (`--engine=vm (x)(\d{4,}?)\d`):
```c
        while (it_ < 4UL) {
            if (!(rx_span_cursor + 1 <= subject_length && ((unsigned)(subject[rx_span_cursor + 0] - 48) <= 9u))) goto rx_fail;
            rx_span_cursor += 1; it_++;
        }
```

**Emitted, utf8, stride 2** (`-e utf8 --engine=vm (?:é){2,}?é`):
```c
        while (it_ < 2UL) {
            if (!(rx_span_cursor + 2 <= subject_length && (subject[rx_span_cursor + 0] == 195) && (subject[rx_span_cursor + 1] == 169))) goto rx_fail;
            rx_span_cursor += 2; it_++;
        }
```

**For contrast, the GREEDY arm of the same rung** (`--engine=vm
(?:ab){2,}ab`). Its mandatory iterations live inside the delegated scan plus
a reach test. This is the shape §1.5 proposes for the lazy arm:
```c
        rx_span_cursor = scan_position;
        while ((rx_span_cursor + 2 <= lim_) && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {
            rx_span_cursor += 2;
        }
    ...
rx_L3: __attribute__((unused));
    if ((ptrdiff_t)rx_span_cursor < slot_values[2] + 4) goto rx_fail;
```
The capped VMSPAN form already exists byte for byte (`--engine=vm
(?:ab){2,5}c`): `while ((rx_span_cursor + 2 <= subject_length) && it_ < 5ULL
&& (…) && (…)) { rx_span_cursor += 2; it_++; }`.

**Population** (corpus `pattern` lines with a lazy quantifier, 442 unique
patterns, 430 that compile, `--features all`; scratch `cen.out`):

| arm | artifacts carrying the prefix |
|---|---|
| default auto, byte | 39 |
| `--engine=vm`, byte | 111 |
| `--engine=vm`, `-e utf8` | 95 |

Across the 111 `--engine=vm` artifacts there are 135 site instances. By
rmin: 106 at 1 (`+?`), 18 at 2, 10 at 3 and 1 at 200. By stride: almost all
1, with 7 at stride 2. Default-route witnesses include `(a+?)(a+)`,
`(\w+?)\b\1`, `(a{2,3}?){2,3}`, `z(a){3,}?c?` and `(?>a{1,3}?)b`. The census
compiles each `pattern` line with no per-block `flags`/`encoding`, so it is a
floor and not the whole population.

**The edit set under the recommended path (§1.5).**

- **pcrec, `src/gen/emit_vm.c`.**
  - `vm_span_advance` (4669) takes the cap as a parameter: `cap < 0` means
    unbounded. Today it reads `a->u.rep.rmax` for `.count`/`.span`.
  - `vm_emit_span_scan` (4708) takes the same cap and declares `it_` when
    `cap >= 0`. Today it tests `rmax >= 0` at 4713.
  - The two existing callers pass `rmax`: the possessive arm at 4869 and the
    greedy arm at 5000.
  - In the lazy arm, 5026-5033 become `vm_emit_span_scan(v, a, seq, stride,
    members, NULL, rmin)` followed by the reach test
    `if ((ptrdiff_t)<p>_span_cursor < slot_values[low] + lo_off) goto
    <p>_fail;`. This is the SAME line the greedy arm writes at 5010, so it
    becomes one helper with two callers. The cursor init at 5021 is emitted
    only on the `rmin == 0` path (the scan block writes its own).
  - The source comment at 5022-5025 changes. `test` stays: the extension
    step at 5104 still reads it.
- **Checks and pins.**
  - `tests/memfn/site_manifest.tsv`: row VMLAZY (line 55) is deleted
    (Q-R12-2), and `C17_ROW_FLOOR` goes 14 → 13 (`run_site_manifest.sh:38`).
  - `tests/memfn/search_vocab.tsv`: the `span-count` line (42) is deleted,
    because nothing else spells it. The commit names what it stops seeing.
  - `tests/memfn/c12_ceilings.tsv`: the `emit_vm.c span-count 1` row (48) is
    deleted, and `C12_CEIL_ROWS_FLOOR` goes 2 → 1 (`run_form_checks.sh:23`);
    it reaches 0 only if N7U also resolves.
  - `tests/memfn/CLAUDE.md` and `src/gen/CLAUDE.md`: the MIGRATED table's
    "the lazy arm's rmin prefix stays pcrec's" sentence.
  - The abi readers, found by grep at the build.
  - `docs/spec/match_api.md` §6's change-log entry.
  - The `EMITTED_BYTES` manifests: the cpset CHECK 3 rows and any resource
    pins whose witness carries a lazy VM loop. `battriage_report.md`'s
    second reader class means a pin can quote a byte count with no abi digit
    in it.
- **Kit: nothing.** The generic row's `stmt_advance` already renders a
  capped, caller-counted, strided ADVANCE (R4h/M6).

### 1.2 The boundary: what the emitter reads today

The kit gets the loop text between the cursor init and `}`. Everything below
stays pcrec's.

| # | file:line | what it reads |
|---|---|---|
| L1 | 6442, `vm_cursor_fits` | the cursor rung's ADMISSION: `vm_det_seq` (fixed width W, per-position bitmaps `seq`) and `vm_cap_offsets`. This is m6scope V1, unchanged |
| L2 | 4771 | `vm_cuts(a, under_atomic)`: possessify's verdict. False plus `!greedy` selects this arm, and the arm emits no scan today |
| L3 | 5026, 5028 | `a->u.rep.rmin`: the prefix exists iff it is > 0, and it is the count |
| L4 | 4798-4822 | `vm_cls`, `vm_cls_test` → `test` and `members[i]` (T4, rule 6), through `Job.scr_test` and arena fragments. The class-form table, `--tune`, `-fno-cls-kit`, `-fno-cls-fold` and the clspack re-spelling post-pass all act here |
| L5 | 5029, 5031 | `stride` (W) |
| L6 | 5029 | the bound is `subject_length`, ALWAYS: this arm folds no MRL clamp. The MRL test sits at the retry label (5051) and reads `v->mrl`/`fmin`/`fdyn` |
| L7 | throughout | `v->p` (K79's prefix placeholder) |
| L8 | 4790, 4792 | `low` (the low-water slot) and `lo_off = rmin*W`. Today the prefix does not read them; under §1.5 the reach test does, as the greedy arm's does |
| L9 | 5034 | `retry`, the label the prefix falls into |
| L10 | (under §1.5) `pcrec_memfn_site` | `pcrec_memfn_policy`, `--memfn=` opts, the deny map: every delegated site's reads |
| L11 | 5104 | AFTER the site: the extension step re-reads `test` (one block, an engine step, unlisted, as Q-R10-7 said) |

The prefix emits no listing event (`vm_ev`), and §1.5 adds none.

### 1.3 The vocabulary/contract gap

R-12 names two candidate gaps: "a counted ADVANCE that must reach K", and
"VERIFY over a counted run of position sets".

**Neither is needed, because "must reach K" factors into pieces the contract
already has.**
- A capped ADVANCE: `span_hi` = K iterations (Q-R10-5); a caller-owned
  counter (`count_by_caller` 1, `it_`); W SET terms (Q-R10-2).
- Then pcrec's own reach test after the site: `cursor < entry + K*W`, which
  is fail.
- The kit's ADVANCE stops at the cap, at the first block a member rejects,
  or where `more` fails. It never reads past `more`.
- So "reached K" is exactly "cursor == entry + K*W", which pcrec tests after
  the site from slots it already owns. That is how the possessive arm
  (4891) and the greedy arm (5010) already discharge rmin.

**Equivalence, stated for the reviewer.** Today's loop fails at the first
block j < K where `more` or a member fails. The re-expressed form stops at
that same block, the cursor stays below the target, and the reach test fails.
If all K blocks pass, both forms leave the cursor at entry + K·W. Neither form
charges work. The step budget is untouched, because the fail label is reached
the same number of times. Answers are identical by construction; G1 measures
the object code.

**What a zero-mover kit form would cost instead** (option Z, not
recommended). Reproducing today's text byte for byte means the kit renders
`while (it_ < KUL) { if (!(more && m…)) <on_miss>; step; it_++; }`. That is
an ADVANCE whose miss is a non-local exit, which ADVANCE does not have
(Q-G2-4: ADVANCE has no miss). It would need:
- a new handoff, e.g. `MF_H_ADVANCE_ALL` ("advance exactly `span_hi`
  iterations, else run `on_miss`, which leaves"): `MF_VOCAB` 3 → 4;
- `on_miss_leaves` admitted on that handoff, `span_hi` REQUIRED finite, and
  an `MF_SITE_ABI` bump (the field rules move);
- a frozen target, G2's must-reach oracle, gate cases and a row;
- the `%dUL` (not `ULL`) cap and the `step; count++;` single line as
  frozen-target layout.

All of that buys a second spelling of a fact the existing site plus a reach
test already states, for a loop that runs once in 79% of its instances. It is
the parallel-mechanism shape the house rule forbids.

### 1.4 RETIRE vs MIGRATE, argued both ways

**For RETIRE (an engine step).**
- 106 of 135 instances are rmin = 1. There the "loop" is one block,
  `if (!(more && m)) goto fail; cursor += W;`, character for character the
  extension step at the retry label's resume (`rx_L7` above). That step is
  unlisted, and Q-R10-7 itself called it an engine step.
- The frames rung's mandatory copies also emit per-copy class tests, and
  nobody lists them.
- On this reading the prefix is the VM's own forward step, iterated rmin
  times. That is the N6 argument one rung over: retire it, and C17's
  end-state arrives without any work.

**For MIGRATE (a counted verify of a span).**
- For rmin ≥ 2 it is a loop over rmin·W subject bytes against W position
  sets, a predicate applied across a span. That is the kit's charter (D146),
  and §R4.3.4 does not exclude it.
- The house has already put this exact family in the kit:
  - VMRUN: the VM's literal-run compare, the per-byte engine steps of a run
    compressed into one verify, delegated at M1b;
  - VMSPAN/VMSTRIDE: the same rung's forward scan, delegated at R4h/M6;
  - the possessive and greedy arms' mandatory iterations, which already live
    inside that delegated scan.
- Retiring the lazy arm's prefix would leave one of the rung's three arms
  spelling its mandatory iterations by hand while the other two delegate
  them. That is the asymmetry the general mechanism removes.
- The N6 test does not transfer. N6's statement was a single-position step
  interleaved with labels, dispatch and capture writes. This one is a
  self-contained loop with one entry and one exit, and its only exit
  semantics (fail) is pcrec's text.

**Recommendation: MIGRATE, by the re-expression in §1.5.** The rmin = 1
majority is the strongest retire argument, and the re-expression answers it
too: an rmin = 1 prefix becomes a capped ADVANCE of one iteration, the same
site every other arm of the rung uses. The extension step stays pcrec's, as
do the possessive/greedy arms' one-block retreats. The line drawn is "loops
are sites, single steps are not", the line Q-R10-7 already drew.

### 1.5 The recommended path: advnorm's two steps

1. **NORMALIZE (a pcrec abi event; no kit change; object-code movers).**
   - The lazy arm spells its prefix as pcrec's own text in the kit's ADVANCE
     layout. The text is `vm_emit_span_scan`'s block, character for
     character, with cap rmin, followed by the reach-test helper.
   - What moves:
     - the prefix bytes;
     - `<PREFIX>_VM_PROGRAM_BYTES`;
     - possibly the entry-shape rung on an artifact near
       `VM_INLINE_CHAIN_MAX_BYTES` (4096), through RQ-3's
       `pcrec_sb_len_decide`. This needs a census: `RX_VM_ENTRY_SHAPE`
       movers by ID.
   - **Acceptance:**
     - a movers-by-ID census (every mover carries a lazy prefix; no
       off-diagonal);
     - an every-startpos answer differential on the corpus witnesses plus
       stride-2/utf8 and rmin ∈ {1, 2, 3, 200} shapes, plain and ASan;
     - G1 at SIMD-off on the lazy witnesses (D144: a null reading inside
       the floor is acceptance; r4e0b's 326-asm-mover precedent);
     - `docs/spec/match_api.md` §6's entry.
   - D149 needs nothing new: the cap is rmin, a pattern fact.
2. **REPLACE (zero movers; I1 shadow; no abi event).**
   - The lazy arm calls `vm_emit_span_scan(…, rmin)`. The DELEG id is chosen
     by stride, as today (VMSPAN/VMSTRIDE).
   - Manifest VMLAZY deleted, `span-count` vocab and C12 rows deleted, S685
     dealt with (§5.1).
   - The I1 shadow comparator is the R4h/M6 one, over both comment tiers,
     `--engine=vm` and `-e utf8`.

The two steps can be one lane. Q-R12-1 asks whether the NORMALIZE byte move
needs Frank's ruling, since memfn/CLAUDE.md says R4e′.0b is "the one ordered
byte move".

### 1.6 G2 needs (blinded author)

None new. A capped, caller-counted, strided ADVANCE is already in G2's space
since M6 (Q-R10-2..5). The one thing to confirm, in contract terms: "the
cursor ends at c0 + j·W, where j is the least of {the cap, the first failing
block, the last block `more` admits}". This is M6's oracle; §1.3's
equivalence rests on it. G2 needs no change unless Q-R12-2 keeps a distinct
DELEG row.

## 2. N7U — utf8's caseless per-character compare

### 2.1 The edit set and the emitted text

**Where.** `u8_defs_bref_ci` (`src/enc/enc_utf8.c:163-212`). It is the
utf8 backend's `PCREC_ENCE_SPAN_CASELESS` entry: the fold table
(`#include "utf8_fold_pairs.inc"`, CaseFolding.txt C+S), the binary-search
`$_span_ci_fold`, and the compare function. `requires` is
`PCREC_ENCE_DECODE` (`entries_utf8[]`, 499-502). `sites_utf8[]` (478-481)
deliberately has NO SPAN_CASELESS row, which is how it opts out of D58
addendum 2's token.

**Callers.** Every caseless backreference (`vm_bref`) and every caseless
variable (`vm_var`, [VAR], which calls the same entry) in a utf8 artifact.
Corpus census, `-e utf8 --features all`:
- **16** as-written patterns emit a call. That is a floor: per-block
  `flags i` is not applied by the extraction.
- **459** emit a call if every backreference/variable pattern is forced
  caseless.

**Emitted** (`-e utf8 --features all (?i)(k)\1`, also `(?i)a${v}b`):
```c
ptrdiff_t rx_span_match_caseless(const unsigned char *s, size_t n,
                                const unsigned char *ref, size_t reflen,
                                size_t at)
{
    size_t i = 0, j = at;
    while (i < reflen) {
        unsigned x = 0, y = 0;
        size_t lx = rx_decode(ref, reflen, i, &x);
        size_t ly = (j < n) ? rx_decode(s, n, j, &y) : 0;
        if (lx == 0 || ly == 0 ||
            rx_span_ci_fold(x) != rx_span_ci_fold(y))
            return -(ptrdiff_t)(j - at) - 1;
        i += lx;
        j += ly;
    }
    return (ptrdiff_t)(j - at);
}
```
The byte base under `(?i)(k)\1` emits the byte backend's ASCII in-place
compare (N7, delegated) and no `rx_decode`, so N7U is utf8-only.

**The edit set if it is RETIRED (recommended).** No source edit.
- `tests/memfn/site_manifest.tsv` deletes row N7U (line 57), and
  `C17_ROW_FLOOR` goes to 12 (13 if VMLAZY's row is kept).
- `search_vocab.tsv` deletes the `span-decode` line (41). The commit names
  what it stops seeing.
- `c12_ceilings.tsv` deletes `src/enc/enc_utf8.c span-decode 1` (49), and
  `C12_CEIL_ROWS_FLOOR` → 0 once VMLAZY's row also goes. That is the "C12
  reads 0" end state.
- `integration.md` §R4.3.4 adds the exclusion beside Q-R10-11's.
- The D58 addendum 2 revisit clause is closed as "does not migrate".
- Frank's ruling is recorded as a D147 addendum (main's to write).
- `sites_utf8[]`'s comment (474-477) changes "pending its own vocabulary
  step" to "not a kit site (D147 add. N)".

**The edit set if it MIGRATES.**
- **`src/enc/enc_utf8.c`.** The loop lines become `PCREC_ENC_SITE`.
  `sites_utf8[]` gains a SPAN_CASELESS row: the fold kind CP, the fold text
  `$_span_ci_fold(@)`, a DECODE TEXT (new data), and the failure statement
  `return -(ptrdiff_t)(@r - at) - 1;`. That statement READS the kit's cursor,
  so it needs a placeholder or a fixed name; see the result rule in §2.3.
- **`src/enc/enc.h`.** `PcrecEncSite` gains the decode-text column, and the
  "WHY TEXT AND NOT A CALLBACK" note is amended (a D58 revisit, as addendum 2
  itself says).
- **`src/gen/memfn_sites.{c,h}`.** `pcrec_memfn_span_site` gains the unit
  kind, the decode hook, fold CP and the new handoff.
- **`src/gen/memfn_sites.def`.** The N7 row's handoff mask gains the new
  handoff, or a new row N7U is added (Q-R12-4).
- **Kit.**
  - `memfn.h`: `MF_VOCAB` 4, `MF_SITE_ABI` +1, the handoff, the fold value,
    the fact and the hook.
  - `compose.c`: `vocab[]`, `site_check`.
  - `fields.def` and `gate.c`: the new fields and their classes.
  - `mismatch.c`: the unit-decoded render as a row or as a branch of the
    generic row.
  - K1: `mf_ref_mismatch_units`.
  - The frozen target `tests/memfn/pins/n7u_target/` (today's loop
    verbatim), PROVENANCE, and the CLAUDE.md files.
- **Checks.**
  - The manifest flips N7U to delegated.
  - C12's `span-decode` row is deleted.
  - C10 `D91_LOOP` (the compare runs per VM backreference step).
  - The arms fixtures, the rows/floors, and `MF_SITE_ABI` readers by grep
    (53 files at the M6 count).
- **G2 is red until a blinded lane covers the unit-decoded space** (§2.5).
- **No pcrec abi event** at REPLACE (zero movers).

### 2.2 The boundary: what pcrec reads today

| # | where | what it reads |
|---|---|---|
| U1 | `vm_bref` / `vm_var` (emit_vm.c) | `u.bref.caseless` (or the variable's) selects the CASELESS entry at emit time (D18/D23); `Job.enc_mask` gains the bit; the call and the work charge on the negative return stay the engine's |
| U2 | `entries_utf8[]` 499-502 | the entry row, its `requires` (`DECODE`, sabotage S394's anchor) and docs |
| U3 | `enc.c` `pcrec_enc_emit_defs` | the requires closure, the `$` render, the comment gate on `defs_doc` |
| U4 | `utf8_fold_pairs.inc` | the generated fold relation (1,484 pairs; K94's generator) |
| U5 | `emit_dfa.c` `emit_residual_defs` | reads `pcrec_enc_site` for each emitted entry; finds NO row for utf8 SPAN_CASELESS and so leaves the text alone |
| U6 | the return protocol | `>= 0` subject bytes consumed, `< 0` matched prefix (`docs/spec/match_api.md`, D58 entry contract), read by the engine's `took` and its work charge |
| U7 | `$_decode` (entry 8) | the shared one-character decoder ([CLS-TREE] S4), whose ill-formed set is the automaton's |

Under migration the kit would own the loop, the two cursors and the `!=`.
Everything substantive is pcrec's hook text: U4's fold, U7's decode and U6's
protocol. That table is the substance of the retire argument.

### 2.3 The vocabulary/contract gap, and the minimal change

What N7U needs that MISMATCH (F8) does not have:

1. **A unit that is not a byte.** F8's value is "the least byte j…". Here
   both operands advance by a decoded unit's own length, which differs per
   side (Kelvin: `k` is 1 byte in `ref`, U+212A is 3 in `s`). This needs two
   independently advancing cursors, `i` over `ref` and `j` over `s`.
2. **A decode hook.** It is pcrec's text template over (buffer, limit,
   position, out-value), returning the unit length, where 0 means ill-formed
   or truncated. A 0 on EITHER side is a difference. The `ref` side can be
   ill-formed, because `ref` is a slice of the subject.
3. **A fold over unit values, not bytes.** The `fold` hook (EXPR shape) on
   an `unsigned` code point, and a new fold fact MF_FOLD_CP ("the encoding's
   simple fold over its unit values").
   - `MF_FOLD_UCP` today means a BYTE relation, the Latin-1 restriction,
     and stretching it would change its meaning.
   - INPLACE is not needed: the only CP fold is an EXPR.
4. **A length-changing result promised on BOTH outcomes.** The backend's
   tail `return (ptrdiff_t)(j - at);` reads the subject cursor AFTER the site
   on EQUAL. ON_DIFF promises `result` only on a difference ("on EQUAL
   `result` holds no promised value"). N7's tail reads nothing of the kit's,
   which is why ON_DIFF fit.
   - So N7U needs a handoff whose `result` is the subject position after the
     compare: the first differing unit's start on a difference, past the
     last consumed unit on EQUAL.
   - `on_miss` runs on a difference only, must leave, and may read `result`.
   - The ref cursor stays the kit's own.

**The minimal contract** (in contract terms; the kit manager owns the
spelling):
- **`MF_VOCAB` 3 → 4:** one new handoff, `MF_H_ON_DIFF_AT`. It is legal on
  MISMATCH only. The vocab row is `{MISMATCH, ON_DIFF_AT, REF}`.
  - The alternative, overloading ON_DIFF's EQUAL rule under a unit fact,
    gives one handoff two meanings. Q-R8-5 refused exactly that shape for
    ASSIGN.
- **`MF_SITE_ABI` +1** (9, or 10 after R-13 batch 1's bump):
  - `mf_site.unit_kind` (MF_UNIT_BYTE / MF_UNIT_DECODED), appended LAST. It
    is OBLIG: every MISMATCH builder states it, and N7 states BYTE;
  - `mf_hooks.decode`, appended LAST, a template with placeholders for the
    buffer, the limit, the position and the out lvalue;
  - the `mf_fold` value MF_FOLD_CP, legal only with MF_UNIT_DECODED;
  - `result`/`result_decl` named by pcrec (the subject cursor, `size_t `).
    The kit declares the ref cursor itself, and the declaration spelling
    (`size_t i = 0, j = at;`) is a frozen-target fact.
- **Read limits:** `s` in [lo, n) and `ref` in [0, reflen), and only through
  the decode hook, whose own bound is the limit passed to it. The kit itself
  reads no byte, so G2's guard pages cover the hook's reads.
- **No `MF_MAX_*` change.**

### 2.4 RETIRE vs MIGRATE, argued both ways

**For MIGRATE.**
- Q54 ruled N7 (the span compare) a kit site, and N7U is the same entry
  family's caseless member under the other backend. Retiring it leaves
  `span_match` (both encodings), the byte `span_match_caseless` (ASCII and
  UCP) delegated, and exactly one member not.
- There is one real kit opportunity in it: an ASCII-run fast path. While
  both operands are ASCII, compare bytes with the ASCII fold (SWAR or
  vector) and decode only at the first high byte. That is sound because the
  simple fold relates two ASCII characters exactly as the ASCII fold does:
  U+212A and U+017F fold to `k`/`s`, but they are not ASCII, so they leave
  the fast path.
- The house's completeness ruling (Q42 reversed, D147 addendum 5) is "every
  search site migrates".

**For RETIRE.**
- The kit's contract is a byte contract throughout. `mf_term` is a byte set
  or byte run. Every fold fact is a byte relation (NONE/ASCII/UCP-Latin-1).
  Every read is `s[...]`. G2's oracles are byte loops.
- N7U's predicate is in the encoding's character domain. Its operands come
  out of `$_decode`, the fold is over code points, and the result length is
  an encoding property.
- Migrating it makes the kit carry an encoding's unit model: lengths, an
  ill-formed set, a length-changing result. DD-12 (7) and D58 keep that
  sealed in `src/enc/`.
- What the kit would own is the loop, two cursors and `!=`, around three
  pieces of pcrec text: decode, fold, failure. It would hold no fact it
  could act on. That is N6's "a pair of parentheses around pcrec's text".
- The house already drew this line for the same backend. Q-R10-11 ruled
  `$_back_step`/`next_pos` (per-character decode steps) not search sites,
  as "the seam's analogue of T4". N7U is a per-character decode WALK; the
  walk is a loop of those steps, and its unit is still the encoding's.
- The ASCII fast path is a D77 build: no measured cell exists (16
  as-written corpus artifacts, and no bench cell for caseless utf8
  backreferences). If one appears, the fast path is a byte-domain site the
  kit CAN own (a SKIP over {0x00..0x7F} fused with the ASCII fold), filed
  then with its own trigger. The decode walk around it stays the encoding's.
- **Under this criterion the line is principled, not ad hoc:** byte-domain
  loops are the kit's, and character-domain walks are the encoding's. The
  same criterion LISTS a site the manifest missed (§2.6).

**Recommendation: RETIRE N7U by ruling** (Q-R12-3), with the criterion
written into §R4.3.4 beside Q-R10-11 as a rule: "a walk whose unit is the
encoding's character (decode on either operand) is the encoding's; its
byte-domain sub-loops are sites". If Frank keeps it in scope, migrate it
with §2.3's contract AFTER R4j (§4), as its own `MF_VOCAB` 4 prep commit,
then IMPLEMENT/REPLACE (M7's shape).

### 2.5 G2 needs if it migrates (blinded author, contract terms)

1. **Oracle.** For generated unit codes (a toy prefix code with lengths
   1-4, an ill-formed set, and a G2-written decode text) and a generated fold
   over unit values:
   - k = the subject position of the first unit pair that differs under the
     fold, or where either decode returns 0, or where the subject is
     exhausted;
   - EQUAL iff `ref` is consumed;
   - `result` on EQUAL is the subject position past the last unit;
   - `on_miss` runs iff there is a difference, and reads `result` = k.
2. **Space.**
   - length-changing pairs in both directions (1 vs 3 bytes, 3 vs 1);
   - `reflen` 0 (EQUAL, nothing read);
   - truncation on each side at every byte;
   - an ill-formed `ref`;
   - `ref` aliasing `s` and overlapping the window;
   - n − lo around unit boundaries ±1.
3. **Guard pages** on both operands. The kit reads only through the hook,
   so the check is that the hook's limit argument is the stated limit.
4. **Refusals.**
   - BYTE unit with a decode hook, and DECODED unit without one;
   - FOLD_CP under BYTE, and ASCII/UCP under DECODED;
   - ON_DIFF_AT on a non-MISMATCH site;
   - `on_miss_leaves` 0;
   - `MF_SITE_ABI` N−1.

### 2.6 Finding: `$_valid_upto`'s ASCII SWAR skip, an unlisted byte-domain site

`u8_defs_valid_upto` (`enc_utf8.c:431-471`, [UTF-VALID], abi 50) is the
whole-subject validator `-futf-check` calls once per call; `var_valid` is
re-spelled on it. Inside, after an ASCII byte:
```c
            while (n - p >= 8) {
                __builtin_memcpy(&w, s + p, 8);
                if (w & 0x8080808080808080ull) break;
                p += 8;
            }
```
This is a SKIP over the byte set {0x00..0x7F} in SWAR form: a scan over
subject positions for a predicate, in the kit's byte domain. It landed after
the manifest was born, and no `search_vocab.tsv` line matches any of the
entry's 40 string literals (checked line by line in a scratch run of the
vocabulary regexes). So C17 is blind to it, which is §R4.3.4's stated limit
(the same way Q-R10-7 found VMLAZY).

The decode/validate body around it is the encoding's (§2.4's criterion).
Q-R12-5 recommends listing the skip as `pending` row VALID with a vocabulary
line for the SWAR form. Its migration is a D58 addendum-2 token in a second
entry, needs no new vocabulary (a SKIP/ADVANCE over one SET term, with the
kit choosing the form), and is filed behind the end state rather than
blocking it.

## 3. The overlap check against R-13 (batch 1)

R-13 touches the following:
- `memfn/src/ofsskip.c`'s FUNC seam: `fn_rows[]`, PREFIX rows
  `vrun-w32`/`vrun-w16`;
- `levels.def` (born);
- `options.def` (its first rows);
- `mf_sink`'s `simd_open`/`simd_close` in `memfn.h`, with pcrec's
  `pcrec_memfn_sink_simd_*` in `src/gen/memfn_sites.{c,h}`;
- `mf_pred.plan_pos2`;
- `tests/memfn/simd_bounds.tsv`, C18 and G2;
- one `MF_SITE_ABI` bump (§R4.9, integration.md:879-880, 2288).

RQ-3 (lane/rq3, abi 71) touches `emit_vm.c` in three places: `vm_init`
(10210, the witness hook), `vm_plan_entry` (10780, `program_bytes` read
through `pcrec_sb_len_decide`) and the search-body splice (12825).

- **VMLAZY (recommended path) vs R-13: DISJOINT in code.**
  - VMLAZY's code edits are `emit_vm.c` 4669-4725 and 5013-5033, plus the
    two callers at 4869/5000. RQ-3's emit_vm.c hunks are 5,000+ lines away,
    in other functions.
  - It touches no `memfn/` file, no `fn_rows[]`, no PREFIX row, no sink op
    and no `options.def` row. ADVANCE is not in batch 1, and no SIMD
    ADVANCE form exists (F-6: its bound comes in its own bump).
  - **Two serialization points:**
    1. The NORMALIZE commit moves `job->vmsb`'s length, which RQ-3's
       `pcrec_sb_len_decide` hands to the entry-shape knee. Not a conflict:
       its mover census must read `RX_VM_ENTRY_SHAPE` by ID.
    2. Its pcrec abi number comes after RQ-3's 71 (and after anything main
       serializes in between).
- **N7U (if retired) vs R-13: DISJOINT.** Docs and `tests/memfn` TSV rows
  only.
- **N7U (if migrated) vs R-13: OVERLAP, named.**
  - `memfn/include/memfn.h`: both bump `MF_SITE_ABI` and both append LAST,
    batch 1 to `mf_sink`/`mf_pred`, N7U to `mf_site`/`mf_hooks`. That is
    one number line plus adjacent comment blocks: a textual conflict and a
    number that serializes.
  - `memfn/src/compose.c`: N7U edits `site_check` and `vocab[]` in the file
    whose `kit_walk` batch 1's PREFIX rows run through.
  - The readers of `MF_SITE_ABI` by grep: G2's `g2.h`, `rows_check.py`,
    `arm_fixtures.c`, `memfn_sites.c` and the CLAUDE.md files. Both events
    re-pin the same readers.
  - Resolution: N7U-migrate lands after batch 1 (and after R4j, §4), at the
    next number, never in parallel.
- **Mech ids:** S706-S715 (R-12) and S716-S730 (R-13) are disjoint. All ten
  of S706-S715 are free on main, on every `worktrees/*/tests/mech` and in
  every branch tree (an `ls-tree` grep found none). Main's highest is S698;
  lane/rq3 adds S699-S703.

## 4. Which goes before R4j/M5 (the planner moving live)

R4j moves `prefix_k`'s selection into the kit as the scalar layer's live
planner (§R4.3.5). It reaches the PRE/OFS sites, `plan_hint`/`plan_pos`, and
probably `mf_pred` (its own `MF_SITE_ABI` event). Neither pending site is in
its edit set: VMLAZY is a VM ADVANCE (no plan), and N7U is a MISMATCH (no
plan).

- **VMLAZY: may go BEFORE R4j, and should.** It needs no kit contract, its
  abi event is pcrec-only, and it closes one of the two pending rows. That
  puts C17 at 1 pending (or 0, with N7U retired) before the planner work
  starts. A reviewer of R4j's movers census then reads a manifest with no
  pending rows, and C17's rule 4 has nothing left to hide behind.
- **N7U: the RULING before R4j** (cheap, and docs-only if retired). **The
  BUILD, if it migrates, after R4j.** A migrated N7U would be the third
  `MF_SITE_ABI` event in flight (batch 1, R4j, N7U). Its value is
  completeness, not a measured cell, so D77 orders it last.
- **VALID (if listed, Q-R12-5):** filed behind both. It is a new row,
  `pending` until its own step.

## 5. Checks and sabotage

### 5.1 Rows whose anchors or reach move

| row | file | effect | action |
|---|---|---|---|
| S685 | `search_vocab.tsv` `span-count` line; REACH_POP needs the `VMLAZY … pending` row | **dies** (its line and its row are deleted with VMLAZY) | retire in the REPLACE commit, with the equivalence note. Its purpose (a pending row's vocabulary lost) is S511's family, and the next pending row (VALID, or N7U if kept) can carry a successor |
| S511 | `site_manifest.tsv` VMSTRIDE row | durable (VMSTRIDE stays delegated) | none; solo re-run (the manifest's row count moves) |
| S512 | `site_manifest.tsv` SETREST row, REACH_POP = row floor | its floor literal moves 14 → 13/12 | re-pin `SAB_REACH_POP`/`SAB_DOC_FIGURE` with the floor |
| S394 | `enc_utf8.c` entries table, SPAN_CASELESS `requires` | unchanged under retire. Under migrate, the row's neighbour (`sites_utf8[]`) changes, not this line | solo re-run under migrate |
| S56/S57/S61, S37 | `vm_cursor_rep` (`m6scope_report.md` §6.1) | the lazy arm's lines shift. Their anchors are text in unchanged lines | `scripts/m6read_check_sab_anchors.py`, `sabotage_anchors.py --step` per commit |
| S616/S214 | generic.c cap line | the plant (`count_start`) now also reaches the lazy prefix's cap | solo re-run, more reach expected |

### 5.2 New rows, S706-S715 (grepped free), the budget per site

VMLAZY, recommended path (5 ids):

| id | plant | expected detector |
|---|---|---|
| S706 | NORMALIZE/REPLACE: the reach test after the prefix dropped (a run short of rmin is accepted) | harness/vm (`(a)(?:ab){2,}?ac` on "aabac": the scan stops after one block, and without the test the follow matches; correct is no match) |
| S707 | the prefix's cap passed as `rmin - 1` (the reach test then fails every start) | harness/vm (`(a)(?:ab){2,}?ab` on "aababab", correct (0,7)) |
| S708 | the reach test reads `rmin` instead of `rmin * stride` (correct at W = 1, wrong at W = 2) | harness/vm stride-2 witness, utf8 `(?:é){2,}?é` |
| S709 | pcrec re-spells the counted loop (`while (it_ < %dUL)` restored) after the row is deleted | memfnforms (C12: no `span-count` ceiling row), a new vocab line kept as a tripwire, or C17 rule 1. Q-R12-6 decides which line survives |
| S710 | the lazy arm's `vm_emit_span_scan` call keeps the DELEG id VMSPAN at W > 1 | memfndeleg (C10) / the I1 shadow |

N7U (5 ids). If RETIRED, only S711 is used, and S712-S715 return to the
pool:

| id | plant | expected detector |
|---|---|---|
| S711 | retire: the `span-decode` vocab line restored with no manifest row (a pending form with no row) | memfnmanifest (C17 rule 1) |
| S712 | migrate: the kit advances `j` by the REF unit's length | harness/backrefs utf8 caseless (`^(k)\1$` on "k"+U+212A), brefdiff |
| S713 | migrate: a decode 0 on the `ref` side is not a difference | brefdiff ill-formed-ref cells, G2 |
| S714 | migrate: `result` unpromised on EQUAL (the backend's `j - at` reads a stale cursor) | harness, memfnarms pin |
| S715 | migrate: `vocab[]` loses `{MISMATCH, ON_DIFF_AT, REF}` | memfndeleg (C10), harness (every utf8 caseless artifact refused) |

If VALID is listed (Q-R12-5), its vocabulary-line row takes S712 in the
retire case.

### 5.3 Identity-gate reach

- **VMLAZY REPLACE:**
  - `scripts/emit_sweep.py --ref <merge-base>`, judged by
    `memfn_r4c_gate.py --zero-dumps`;
  - both bases and all streams;
  - `--extra --engine=vm`, `-fno-possessify` (it moves lazy loops between
    the possessive and lazy arms), `-fno-length-prune`, `--tune=-2`,
    `-fno-cls-kit`, `-fno-cls-pack`, `-fcomments` and `-fmemfn-simd`.
  - **Reach** (each > 0 per base/stream/arm): artifacts whose lazy arm
    carries a prefix, as a stamp-free text census (the RUNGS listing's
    `lazy` cursor rows with rmin > 0).
  - The NORMALIZE commit's mover set must equal that reach set by ID.
- **N7U (migrate):** M7's §7 gate, utf8 base, with reach =
  `span_match_caseless` definitions under `-e utf8`, using the 459-artifact
  forced-caseless population as the witness pool.

## 6. The standing design questions (docs/design/CLAUDE.md)

1. **Measurement regime.** This applies to VMLAZY's NORMALIZE only. It needs
   G1 at SIMD-off: Linux, pinned, against its own deny or the pre-commit
   build, with the lazy witnesses in find-all and per-call regimes. The
   prefix runs once per lazy-loop entry and is not a per-byte loop, so a
   null result inside the floor is the expected acceptance. N7U-migrate is
   zero movers; under retire there is nothing to measure.
2. **Independent control.** VMLAZY's answers are checked against the
   harness/vm corpus and an every-startpos differential against
   `--engine=dfa` where it compiles, never against the kit. The census reads
   `--emit-ir` RUNGS, not the kit's `moved`.
3. **What moves when data is regenerated.** Nothing for VMLAZY. For
   N7U-migrate, regenerating `utf8_fold_pairs.inc` moves the backend's
   table, not the kit's text, because the fold text is a hook. This is
   unchanged from today.

## 7. Open questions

- **Q-R12-1. Does VMLAZY's NORMALIZE byte move need a ruling?**
  - The problem: memfn/CLAUDE.md says "Each step is zero-mover (R4e′.0b,
    D155, is the one ordered byte move)". The cheapest correct path for
    VMLAZY moves pcrec's own text (not the kit's) before a zero-mover
    REPLACE, as advnorm (abi 66 → 67) did for R4h.
  - The forces:
    - advnorm is direct precedent, and its move was text-only with no
      object movers. This one may move object code (a loop-carried test
      becomes a post-loop test), so G1 is real.
    - The zero-mover alternative costs a new handoff, `MF_VOCAB` 4 and a
      parallel spelling (§1.3, option Z).
  - **Leaning:** treat it as advnorm was treated, a pcrec normalization
    event under the manager's authority with a G1 null reading, and tell
    Frank rather than ask. If the manager reads "the one ordered byte move"
    as binding, it is Frank's call, and the case for it is §1.3's.
- **Q-R12-2. VMLAZY after migration: delete the row, or flip it to
  delegated with its own DELEG id?**
  - Q-R10-6 kept VMSTRIDE as its own row so reach per stride class stayed
    visible.
  - Here the site would be literally the same builder and the same DELEG
    rows (VMSPAN/VMSTRIDE by stride). A distinct id would be a second name
    for one site.
  - **Leaning:** delete the row and fold its history into VMSPAN/VMSTRIDE's
    notes. If per-arm reach matters, it is a census column (lazy-prefix
    instances), not a DELEG row.
- **Q-R12-3. N7U: retire by ruling (byte-domain criterion), or migrate with
  `MF_VOCAB` 4?**
  - This reverses part of Q42's named list, as N6 did, so it is Frank's
    ruling, recorded as a D147 addendum.
  - The forces are §2.4's. The strongest migrate force is family symmetry
    with N7. The strongest retire force is that the kit's whole contract is
    byte-domain, and that Q-R10-11 already put this backend's decode steps
    on the encoding's side.
  - **Leaning: retire,** with the criterion written as a rule, so that the
    next encoding's character walks are classified without a new ruling. If
    migrate, after R4j (§4).
- **Q-R12-4. If N7U migrates: extend DELEG row N7's handoff mask, or a new
  row N7U?**
  - **Leaning:** a new row. Its handoff, unit and fold kind differ, and
    C10's per-row check is cleaner with one meaning per row.
- **Q-R12-5. List `$_valid_upto`'s ASCII SWAR skip as `pending` row VALID?**
  - It is an unlisted byte-domain search site that C17 cannot see (§2.6).
  - The forces:
    - completeness (the end state is "0 pending", which is false while an
      unlisted site exists);
    - this lane's brief is scoping, not listing.
  - **Leaning:** yes. Listing is a manifest row plus a vocabulary line plus
    a C12 ceiling row, the same shape M6's REPLACE used for VMLAZY. Its
    migration is filed with completeness as its trigger and needs no new
    vocabulary. A quick census lane should also re-run the vocabulary over
    every `src/enc/` and `src/gen/` literal added since R4a, so a third such
    site is not found by accident.
- **Q-R12-6. What keeps "pcrec re-spells a counted span loop" visible after
  `span-count` is deleted?**
  - C12's rule "0 outside the kit" needs a vocabulary line to count with.
  - **Leaning:** keep the `span-count` line with C12 ceiling 0 (no row
    needed, since ceilings default to 0). That is what makes S709
    detectable, and it is the walk-open precedent: kept after M6 with its
    doc updated.
- **Q-R12-7. Is the R-12 "responses notice" this report?**
  - The request text says "post a responses notice". The brief says to
    deliver this report. `responses.md` is the kit session's single-writer
    file (D78), so this lane did not write it.
  - **Leaning:** the kit session posts a pointer notice to this report, or
    main relays it.

## Charter checklist

| brief item | section |
|---|---|
| 1. Edit set, functions/lines, 2-3 emitted examples per site | §1.1 (byte s2/s1, utf8 s2, greedy contrast); §2.1 (utf8 caseless, its callers) |
| 2. Boundary: every pcrec read | §1.2 (L1-L11); §2.2 (U1-U7) |
| 3. Vocabulary/contract gap, minimal change, bumps | §1.3 (none needed; option Z priced); §2.3 (`MF_VOCAB` 4, `MF_SITE_ABI` +1) |
| 4. RETIRE vs MIGRATE argued both ways, recommendation | §1.4 (migrate); §2.4 (retire) |
| 5. Overlap with R-13 | §3 (VMLAZY disjoint; N7U-migrate overlaps memfn.h/compose.c, named) |
| 6. Before R4j/M5? | §4 |
| 7. Q-R12-n | §7 |
| Sabotage budget S706-S715 per site | §5.2 |
| Finding beyond the brief | §2.6 (`$_valid_upto`, Q-R12-5) |
