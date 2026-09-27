# Lane q4amend — D126 Q4: the prior's NONE answer spelled once per question kind

Lane `q4amend` (opus), 2026-09-27, branch `lane/q4amend` from main
`acc9e990`. DESIGN-DOC ONLY: no code, no `make`, no suites. Every code
site cited in the amended text was read on this tree.

**Task.** D126 Q4 (`docs/dev/decisions.md:8633`): amend
`docs/design/findings/design.md` §6.1-§6.3 before B1, so that each rate
QUESTION KIND spells its NONE answer once, beside its primitive, and no
reader or call site spells one. Bring §6.1-§6.3 in line with PATFACTS
rev 2's B1 (step 3.1).

## What changed, per subsection

**§6.1 Signatures.**
- New revision note at the head: `[D126 Q4]`, why (R13), and what now
  matches PATFACTS §0 item 5(b)/§6.3/§8.1/§9.
- New primitives: `pcrec_find_pick`, `pcrec_find_no_commoner` and
  `pcrec_find_seq_mass`, beside the existing `pcrec_find_set_mass`.
  `pcrec_find_byte_rate` gains the sentence "a reader never tests it".
- New paragraph: why NONE is per KIND and not a uniform table. This is
  R24's own warning, made concrete: a uniform table is right for MASS,
  gives R13's leftmost for `rn_scan_index`'s PICK, and returns `true`
  for every COMPARE. R24 is restated as "each KIND states its NONE
  answer; each reader states its kind".
- `run-rarity` is marked PROVISIONAL. Q4 binds it too, and B4 spells its
  NONE answer inside the primitive.
- "These three are the whole surface" becomes six functions. The
  deletion list gains `pcrec_byte_freq_total_ppm` and the `internal.h`
  declarations.
- New paragraph: where the rate readers live (carve-out (b)).

**§6.2 Customers.**
- Retitled "→ question kind → NONE answer".
- The per-reader paragraph is replaced by the per-kind rule.
- New kind table (PICK / COMPARE / MASS / run-rarity → primitive → NONE
  → readers).
- The C1-C11 table gains a column: the candidates, in the order the
  reader passes them.
- C2 splits into C2a (PICK) and C2b (MASS over a sequence), matching
  §6.2a's names. The stale "leftmost" for C2a is corrected to rightmost.
- C5, C6, C7 and C8 lose their per-reader NONE fallbacks.
- Every C1-C4 site is re-cited against main.

**§6.3 Sites (B1).**
- Rewritten against main and PATFACTS B1: 3.0 is a hard prerequisite,
  and the lines are today's (the lane re-greps them on 3.0's tree).
- One row per site, with today's code and after-B1 code: the three
  `reqbyte.c` readers, the `bytekey` line, G1's density line, `set_ppm`,
  and the table deletion.
- New list of other readers of the moved and deleted names, found by
  grep:
  - sabotage rows S266, S294 and S288 re-anchor;
  - S270, S286 and S265 are untouched;
  - prose in `run_prechecks.sh`, `run_recursion_identity.sh` and two
    CLAUDE.md files;
  - `run_offset_skip.sh` §1's C program.
- New structural-check paragraph, widening §11.7.
- Byte-identity and `utf8`-mover paragraph restated per kind.

**Outside §6.1-§6.3.**
- §0 item 8's cross-reference, "Decided (§6.3)", now reads §6.1 / the
  MASS kind.
- `docs/design/findings/CLAUDE.md`: "the three-call accessor" is
  replaced by the per-kind primitives. The file's role is unchanged.

## Each NONE rule as now spelled (findings §6.1)

| kind | primitive | NONE answer | readers |
|---|---|---|---|
| PICK | `int pcrec_find_pick(rate, cand, n, rightmost)` → index; argmin, ties to the EARLIEST | `rightmost`: the reader's positional rightmost candidate (PCRE2 LASTCODEUNIT) | C1 `rb_pick` (`[pick, 255..0 \ pick]`, 0), C2a `rn_scan_index` (`bytes`, n-1), C8 |
| COMPARE | `bool pcrec_find_no_commoner(rate, p, q)` | `false` (identity stays the caller's conjunct) | C3 G1 |
| MASS | `pcrec_find_set_mass(rate, set)` (capped 10^6), `pcrec_find_seq_mass(rate, bytes, n)` | uniform-rate mass ⌊k·10^6/256⌋, k = \|set\| or n (cardinality); empty → 0 | C2b `rn_window_start`, C4 `set_ppm`, C5, C7, C9 |
| run-rarity | `pcrec_find_run_rarity` | spelled in the primitive at B4 | C5 restart, C6 |

Under `-e byte` + default, every reader is byte-identical. Under `-e utf8`
+ default, only MASS moves (offset-k). That is `b1_utf8_movers`.

## Left open for the manager / Frank

1. **Seq-mass NONE is the uniform mass ⌊n·10^6/256⌋, not PATFACTS §6.3's
   `n`.** The two are equivalent in effect, because only equal-length
   windows are compared. I chose the uniform mass so that MASS has
   literally one NONE rule. PATFACTS §6.3's MASS row should pick it up,
   or the manager reverts to `n`.
2. **The primitives take `rate` (PATFACTS' spelling), not `Ctx *`.** The
   `Ctx *` alternative would make "no reader tests `rate`" structural
   rather than a grep check. It would also make the consumption-record
   ask pattern-conditional (an empty set would never ask), which works
   against §6.4 rule 1. So I kept `rate` and added the widened grep check
   with a sabotage row.
3. **I named `src/core/findings.c` as the file the moved readers live
   in.** PATFACTS carve-out (b) says only "beside the primitives". A
   separate `findings_rate.c` is equally consistent.
4. **Owed at PATFACTS 3.0, not stated there:** the core "necessary SET"
   fact must publish the set's threaded rightmost `pick` beside its bits.
   Today `ReqSet` is bits only (`internal.h:2458`, filled at `reqbyte.c:617`), and `rb_pick`'s
   candidate order needs `pick`.
5. **C8 `[OPT-A]`:** if its no-information answer (r2's
   `cand_from_escapes`) is not a candidate the row can place at
   `rightmost`, it is a new KIND with its own primitive. Its row decides.
6. **`run-rarity`'s NONE answer** is deferred to B4 (D77). The
   per-position cardinality model is named as the candidate.

## Stale spots noticed, NOT fixed (outside the brief's sections)

findings `design.md`:
- §1 table row 13 lists only `byte_rate`/`set_mass`/`run_rarity`.
- §6.2a still names `dfa_cand_scan_byte` (now `dfa_cand_scan`,
  `emit_dfa.c:5837`) and cites `emit_dfa.c:5495/5507`
  (`req_byte_dominated_by` is at `:5933`; `pcrec_artifact_has_dfa_scan`
  is at `:356`).
- §6.4 rule 1: "C1/C2 are the named exception" should become PATFACTS
  §7.4's "every fact-deny's derived facts".
- §9 (line 1218): "the reader takes its NONE fallback (§6.2)" should
  read "the kind's NONE answer".
- §11.2 has no sabotage row yet for "a reader-local `!rate` branch".
- §11.7 owes the widened check's text.
- §13's B1 row names only `byte_rate`/`set_mass` and "prefix_k's
  cardinality fallback". It should list the new primitives, the reader
  moves and the `reqbyte.c` deletion.
- §14's `findings.md` hunk says "per-reader NONE fallbacks (§6.2)" (it
  should be per kind), and its `tuning.md` hunk says "offset-k's
  cardinality NONE fallback".
- §15's R24 row says "per-reader fallbacks (§6.2)".

findings `requirements.md`: R24's "per reader" wording is left alone as
the historical step-1 record. The design now amends it.

PATFACTS `design.md` line citations drifted against `acc9e990`:
- `reqbyte.c:539/559` are now `:560/:580`;
- `emit_dfa.c:5917` (§4.2.2(c)) is now `:5933`;
- §6.2's `reqbyte.c:543/567` are now `:564/:588`, and `emit_dfa.c:5925`
  is now `:5941`;
- §8.1's `prefix_k.c:112-165` is now `:112-162`.

Plus item 1 above (the MASS row's `n`).

## Validation

None run: design-doc lane, no build or suite, per the brief. The
citations were verified by reading `src/opt/reqbyte.c`,
`src/opt/prefix_k.c`, `src/gen/emit_dfa.c`, `src/core/compile.c`,
`src/core/internal.h` and the sabotage files on this tree.
