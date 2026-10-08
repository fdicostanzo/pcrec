# advtarget — R4h's frozen ADVANCE target (kit text + tests, zero pcrec movers)

Lane advtarget, 2026-10-08, opus; branch lane/advtarget (cut from
lane/memfn-next 9bf09133). Request: the pcrec manager's (2026-10-08),
input to the R4h layout-normalization lane (normscope_report.md,
Q-R4h-1 (b)).

## What was done
- `tests/memfn/arm_fixtures.c`: eight fixtures, one per in-loop ADVANCE
  shape, rendered through the kit's public entry (`mf_emit`, as
  `render_adv` does; `render_adv_x` adds pcrec's member text, cursor and
  indent). Every hook text is the one build/pcrec emits TODAY at the site
  (witnesses compiled at -o rx.c). The member hook returns pcrec's own
  class test verbatim and ignores the offered byte expression (opaque).
  The term's byte set is descriptive only.
- `tests/memfn/pins/arms.tsv`: +16 rows (8 fixtures x def/use, all
  `generic`), `ARMS_ROW_FLOOR` 58 -> 74. No existing row re-pinned.
- `tests/memfn/pins/r4h_target/<fixture>.c` (8 files + CLAUDE.md): a
  3-line header (witness, flags, hook texts, indent), the kit's `.use`
  byte for byte, then a `/* pcrec today:` block quoting the current site.
- `tests/memfn/run_arm_pins.sh` check 8: each target's body equals a
  fresh render (and the `.def` is empty); K35 shape list `R4H_TARGETS`
  and floor `R4H_TARGET_FLOOR` 8; a planted-byte control (line 4's first
  space -> tab on adv-edge-counted-fwd) must compare unequal. Also
  validated by hand: editing adv-vmspan.c's body (`9ULL`->`9UL`, parens
  dropped) read `FAIL: r4h_target/adv-vmspan.c differs ...`, 1 failed.
- `memfn/include/memfn.h`: the ADVANCE comment now says the `member`
  hook is OPAQUE (pasted `&& (member)`, its shape never matters, no class
  claimed) and names the target render. Comment only: MF_SITE_ABI stays 5.
- CLAUDE.md: tests/memfn, memfn/include, new pins/r4h_target.

## Decisions (the kit's, binding; none changed)
All four kept: `more` and `member` always parenthesized; the always-braced
body; the counter step on its own line; the cap as `%llu` + `ULL`. No
correctness or precedence hazard found: every target compiles clean in a
context (`gcc -std=gnu11 -Wall -Wextra -Wparentheses -Wsign-compare
-Werror`, counters `unsigned long`, cursors `size_t`, tables `unsigned
char[256]`).

CAVEAT for R4h: the target assumes pcrec's member hook returns its own
text (as `scan_test` and the VM's `vm_cls_test` write it, reading pcrec's
`peek`). The kit offers `((unsigned char)(<peek>))` as `byte_expr`; a
member hook that rendered FROM that expression would produce different
text (an "other" delta). The fixtures' hook ignores it, and so must
pcrec's.

## Targets (body only; header/trailer in the files)

### adv-stay-fwd
witness `a[^x]*`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c).
```
            while ((scan_position < subject_length) && (rx_forward_stay1[subject[scan_position]])) {
                scan_position++;
            }
```
pcrec today:
```
            while (scan_position < subject_length && rx_forward_stay1[subject[scan_position]]) scan_position++;
```

### adv-stay-rev
witness `a[^x]*`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c).
```
                while ((rewind_position > search_from) && (rx_reverse_stay0[subject[rewind_position - 1]])) {
                    rewind_position--;
                }
```
pcrec today:
```
                while (rewind_position > search_from && rx_reverse_stay0[subject[rewind_position - 1]]) rewind_position--;
```

### adv-stay-view
witness `a[^x]*x$`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c).
```
            while ((scan_position + 1 < subject_length) && (rx_forward_stay1[subject[scan_position]])) {
                scan_position++;
            }
```
pcrec today:
```
            while (scan_position + 1 < subject_length && rx_forward_stay1[subject[scan_position]]) scan_position++;
```

### adv-edge-unbounded
witness `[a-z]*`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c).
```
            while ((scan_position < subject_length) && ((unsigned)(subject[scan_position] - 97) <= 25u)) {
                scan_position++;
            }
```
pcrec today:
```
            while (scan_position < subject_length && (unsigned)(subject[scan_position] - 97) <= 25u) scan_position++;
```

### adv-edge-counted-fwd
witness `a[0-9]{3,20}x`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c).
```
            while ((scan_position < subject_length) && scan_run_length < 3ULL && ((unsigned)(subject[scan_position] - 48) <= 9u)) {
                scan_position++;
                scan_run_length++;
            }
```
pcrec today:
```
            while (scan_position < subject_length && scan_run_length < 3UL
                   && (unsigned)(subject[scan_position] - 48) <= 9u) { scan_position++; scan_run_length++; }
```

### adv-edge-counted-rev
witness `a[0-9]{3,20}x`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c).
```
                while ((rewind_position > search_from) && scan_run_length < 3ULL && ((unsigned)(subject[rewind_position - 1] - 48) <= 9u)) {
                    rewind_position--;
                    scan_run_length++;
                }
```
pcrec today:
```
                while (rewind_position > search_from && scan_run_length < 3UL
                       && (unsigned)(subject[rewind_position - 1] - 48) <= 9u) { rewind_position--; scan_run_length++; }
```

### adv-vmspan-it
witness `(a)[a-z]{2,9}x`, --engine=vm (pcrec 9bf09133 build/pcrec, -o rx.c).
```
        while ((rx_span_cursor + 1 <= lim_) && it_ < 9ULL && ((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u)) {
            rx_span_cursor += 1;
            it_++;
        }
```
pcrec today:
```
        while (rx_span_cursor + 1 <= lim_ && it_ < 9UL && ((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u)) { rx_span_cursor += 1; it_++; }
```

### adv-vmspan
witness `a[a-z]*x`, --engine=vm (pcrec 9bf09133 build/pcrec, -o rx.c).
```
        while ((rx_span_cursor + 1 <= lim_) && ((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u)) {
            rx_span_cursor += 1;
        }
```
pcrec today:
```
        while (rx_span_cursor + 1 <= lim_ && ((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u)) { rx_span_cursor += 1; }
```

## Per-shape delta from today's pcrec text
(a) wrapped vs single-line condition, `) step;` vs `) { step; }`;
(b) `(more)` / `(member)` parens; (c) `%dUL` -> `%lluULL`;
(d) always-braced multi-line body, counter step on its own line.

| shape | (a) | (b) | (c) | (d) | other |
|---|---|---|---|---|---|
| adv-stay-fwd | `) scan_position++;` | more + member | - | yes | none |
| adv-stay-rev | `) rewind_position--;` | more + member | - | yes | none |
| adv-stay-view | `) scan_position++;` | more + member | - | yes | none |
| adv-edge-unbounded | `) scan_position++;` | more + member | - | yes | none |
| adv-edge-counted-fwd | wrapped condition -> one line | more + member | 3UL -> 3ULL | `{ step; cnt++; }` -> 3 lines | none |
| adv-edge-counted-rev | wrapped condition -> one line | more + member | 3UL -> 3ULL | `{ step; cnt++; }` -> 3 lines | none |
| adv-vmspan-it | - (already one line, braced) | more only (member already parenthesized) | 9UL -> 9ULL | `{ step; it_++; }` -> 3 lines | none |
| adv-vmspan | - (already one line, braced) | more only | - | `{ step; }` -> 3 lines | none |

No "other" deltas: indent, operand order, member and step texts are
unchanged. The peek cast never appears (the member hook is opaque).

## Validation (complete)
- `make -j4`, `make -j4 strict` clean.
- `make test-memfn-arms`: 74 rows over 37 fixtures, 39 gate cases, 8 r4h
  targets; 221 passed, 0 failed.
- `make test-memfn-rows`: 117 passed, 0 failed.
- Zero pcrec movers: build/pcrec vs a pre-change copy, same -o rx.c, 9
  witness compiles (the six requested, plus `a[a-z]*x` and
  `(a)[a-z]{2,9}x` default and `a[0-9]{3,20}x --engine=vm`): 0 moved
  (.c and .h). No src/ file changed.
