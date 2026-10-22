# subst — [M4-SUBST] phase A: compiled substitution as an independent element (lane report)

Lane `subst`, opus, 2026-10-21. Branch `lane/subst` off `lane/i2build`
(`c3bfee73a`, abi 84). DESIGN ONLY: no build go, nothing under `src/`,
`cli/`, `lib/` or `tests/` touched. Rulings file
`docs/dev/lanes/subst_rulings.md`: empty at every checkpoint, so no entry was
applied.

## Deliverable

- `docs/design/replace_design.md` **§R2** (REVISION 2), the design revision
  per Frank's 2026-10-21 direction (to be D173). Superseded passages are
  marked in place in `replace_design.md` (§0, §3.8, §4.1-§4.4),
  `subst_template_design.md` (top banner, §4, §5, §6) and
  `variables_roadmap.md` (M9).
- `docs/design/subst_measurements/`: the probe (`glue.c`, `run.sh PCREC
  OUTDIR`, `transcript.txt`, CLAUDE.md).
- `docs/design/CLAUDE.md`: entries updated.

## The design, in five lines

A template compiles to its OWN artifact: a straight-line `<s>_render(slot,
ctx, out, cap)` that renders ONE match, plus a record listing its references.
It binds ONCE to any rx whose `rx_info` shape delivers those references.
Numbered groups are constant slots (D61); names go through a small
caller-owned slot table. Duplicate names resolve per match_api.md §5.4¶6. A
prefix-independent glue in the subst header (`pcrec_subst(rx, it, sub, slot,
limit, out, cap, &outlen)`, over `RX_FOREACH`) copies the gaps, renders,
sizes in a single pass and returns the count. 1:N and M:N are linking. rx
artifacts do not change (no rx abi event).

## What was stale (§R2.1 has 18 rows)

- The charter's "pattern AND template compiled together into one function"
  is SUPERSEDED by Frank. So are first/global as a generation axis (now a
  `limit` argument), repeatable `--replace` (now one template per subst
  artifact, under D88 add. 1) and the `rx_subst(s, n, out, outlen)` /
  `rx_subst(..., vars, nvars)` entries.
- The emitted global loop and its empty-match rule (subst_template_design
  §6), and replace_design §3.8's "seam", are CLOSED. The iterator's
  iteration is PCRE2's global iteration (match_api.md §3.8¶2).
- Compile-time reference resolution, and D44.7's `--no-captures` × `$n`
  error, MOVE to bind, once, before any substitution. The D26 promise holds.
- Q10 (duplicate names) is DUE: `named-groups` and `(?J)` have shipped.
- The template language (tiers, grammar corners, case forcing, `${!...}`
  rule, unset axis, length-only output, `rx_renderfn`) STANDS unchanged.
- The in-place mode is a CONTRACT, not free. Three facts make it so: the
  iterator forbids changing `s` while it is live (§3.8¶8), lookbehind reads
  behind `lo` and LB is internal, and a referenced group can lie before the
  match.

## Measured (answers, no timing)

12 cells plus 1, all `OK`, `fails=0`. The cells are subst_template_design
§6.1's, the §3.1.3¶9 retry class (`|a`, `x*|y`), `ab\K`, an unset group, a
group before the match (lookbehind capture), 1:N, M:N with one named subst
over two rx whose `y`/`m` slots are swapped, a shape refusal (PCRE2 `-49`
class refused at bind) and an undersized buffer (NOSPACE, required 11). Each
compares the glue over the lane's artifacts with libpcre2 10.46
`pcre2_substitute(GLOBAL|UNSET_EMPTY|OVERFLOW_LENGTH)`. Re-run:
`docs/design/subst_measurements/run.sh build/pcrec build/subst_probe/out`;
transcript in that directory. The renders are hand-written stand-ins, so
phase B's D27 corpus is still owed.

## Costs of modularity (§R2.8). STOP RULE not hit.

- One out-of-TU call per match, plus one `int` load per NAMED reference.
  UNMEASURED; it is of the same class as D171's accepted iterator setup cost.
  The measurement that would act on it is a phase-B timing cell: `a` → `b`
  over 1 MiB of `a`, and `(\w+)` → `<$1>` over prose, each run separated
  against a hand-fused twin. A loss there would build the fused one-symbol
  form as a D163 COMPOSITE of the same two elements, not as a third
  mechanism.
- Lost capture pruning: a fused compile could pick the DFA when only `$0` is
  used. The separated design covers this by binding a `$0`-only template to
  a `--no-captures` rx; the bind refuses the unsafe pairing.
- Two spec clarifications are owed in phase B. Neither is an emitted
  change. (1) §3.8 should state that reported spans are ordered and
  non-overlapping, which the gap copy relies on. (2) The spec should say
  which `rx_iter` fields the pcrec-owned glue reads (`s`, `n`, `vars`,
  `nvars`).

## Open questions (§R2.11)

For Frank, with leanings:

1. When a template meets its rx. Leaning: once at run time through the rx's
   record, with an optional build-time check when the pattern is named.
2. Whether a one-symbol "substitute with this pattern" function also ships.
   Leaning: only after phase B's timing shows a loss, or someone asks.
3. First vs all. Leaning: one function with a "how many" argument.
4. In-place. Leaning: the contract is written now, the mode is built on an
   ask.

For the manager:

- Q-M1: output contents after a mid-way failure (leaning: unspecified).
- Q-M2: `${site.group}` for delivered composed groups (leaning: allow).
- Q-M3: the subst block gets its own version number (leaning) or the shared
  abi.
- Q-M4: the NOSPACE and renderer-failure code values must differ. The
  probe's `-1` collides with a renderer's passed-through `-1`.
- Q-M5: whether `rx_substfn` should be `rx_renderfn` with the binding in
  `ctx->user` (leaning: no).

## Not done / for phase B

The plan row text and STATE are untouched (manager's). D173 is not filed
(the manager files it). There is no `src/` code, no `.rxt` production and no
spec hunks; phase B's list is in §R2.4, §R2.5 rule 1 and §R2.7. Sabotage ids
S1346-S1385 are reserved by the brief and none were used.

## STATE AT HANDOFF

Committed on `lane/subst`: `a06d4b8ca` (probe), `ec000249e` (§R2 plus the
in-place markers), plus this report's commit. `make test-spec-history` 11/0
PASS. No owed runs. Last rulings entry applied: none (the file is empty). A
fresh agent resumes from §R2.11's answers. Phase B is a build lane with a
build go: subst artifact emission, the bind/glue block, CLI/`.rxt`/library
surfaces, spec hunks, the D27 corpus and the R2.8 timing cell.
