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

## STATE AT HANDOFF (phase A, superseded by the revision 3 state below)

Committed on `lane/subst`: `a06d4b8ca` (probe), `ec000249e` (§R2 plus the
in-place markers), plus this report's commit. `make test-spec-history` 11/0
PASS. No owed runs. Last rulings entry applied: none (the file is empty). A
fresh agent resumes from §R2.11's answers. Phase B is a build lane with a
build go: subst artifact emission, the bind/glue block, CLI/`.rxt`/library
surfaces, spec hunks, the D27 corpus and the R2.8 timing cell.

## Revision 3 (lane substr3, opus, 2026-10-22): the panel r1 applied

Design only, on `lane/subst` from 7d44d7016. Nothing under `src/`, `cli/`, `lib/` or
`tests/` was touched. The rulings file was empty at every checkpoint.

### Deliverable

- `docs/dev/reviews/2026-10-22-r1-subst-design.md`: the three critics' 25 findings,
  one row each, with the manager's dispositions (all ACCEPT), the two probe facts,
  candidates C1-C5, PROPOSED sabotage rows S1346-S1355, and the critics' text
  verbatim. Indexed in `docs/dev/reviews/CLAUDE.md`.
- `docs/design/replace_design.md` §R3 (READ FIRST). §R2 passages it replaces carry
  `[R3: ...]` markers; nothing was deleted. §R3.0 maps every finding id to its
  section. The `docs/design/CLAUDE.md` entry is updated.

### The design after R3, in six lines

- The ELEMENT renders a batch of k matches per call (k = 1 is the per-match case),
  with the gap copy inside (`RX_SUBST_GAPS`) and the length in a `size_t` cursor.
- A name binds to a `(first, count)` run of `rx->groups` rows through one helper,
  `rx_group_run`, and the render walks the run per match_api §5.4¶6.
- The BINDING carries the rx, its `ncaps`, a tag and the segment `user`s. It is
  read-only after bind.
- The GLUE drives `next_n` with a VLA sized from `ncaps` (no group ceiling), never
  fetches past `limit`, saturates lengths, and writes `*outlen`/`*nsubst` on every
  path.
- Every span is checked, giving `PCREC_SUBST_BADSPAN`; there are six distinct codes.
- ONE pcrec build serves both artifacts (`#error` plus a bind check), and there is
  no new version number.

### The two probe facts

1. **Termination: YES.** The iterator ends with `rc 0` on both crit1-1 patterns,
   on short subjects and on six units repeated up to 100,000 times (400 KB). The
   match count was at most `n` and no cap was hit. A third witness,
   `^|(?<=(?1))y|(?!)(\Kz)` on "zy", gives `[0,0) [0,2)`; pcrec accepts it and
   PCRE2 returns −60. That is the documented BADSPAN corner (§R3.6).
2. **Ill-formed UTF-8: consistent.** The iterator, the `_search` loop and the
   per-position `_search` agree on 15/15 cells. libpcre2's single searches agree at
   every offset. libpcre2's global loop differs on 6/15 cells because its anchored
   NOTEMPTY retry escapes the anchor (`(2,2)` from 0), which is match_api §9.3¶3's
   class. This is NOT an I1/I2 defect. It is pinned as stated behaviour, and a
   §3.8¶2 spec sentence is candidate C1.

The probe sources and transcripts are in the session scratchpad (`substr3/term.c`,
`utf.c`, `pm.c`, `corner.c` and their `.txt` files), per the brief's "probes in the
scratchpad only". They were not committed. The transcript lines the design rests on
are quoted in §R3.14. If the manager wants them reproducible, they belong in
`docs/design/subst_measurements/r3/`.

### Found by the lane

**F-R3-1.** §R2.4's glue read `it->vars` on a FRESH iterator, which is garbage
without `rx_iter_vars` (match_api §3.8¶5). It is fixed in `rx_subst_ctx_init`, with a
sabotage row (S1352).

### Candidates (the manager numbers them; no D/K ids were taken)

- C1: a match_api §3.8¶2 sentence on ill-formed subjects.
- C2: a shape-contract version under [DD-3]/[RXINFO-REMODEL] (crit2-2's narrower
  form).
- C3: a subst-block version number of its own, under [IFACE-PUSH].
- C4: `rx_group_run` moves into the rx shared block at the next rx abi event.
- C5: a decision record for D173's revision.

### Open

- **For Frank** (§R3.16, plain words): Q-F1 bind at run time; Q-F2 the fused form
  (leaning stronger: no, unless §R3.13's cell shows a loss); Q-F3 one function with
  a count; Q-F4 the in-place contract only.
- **For the manager:** whether `PCREC_SUBST_PAIRS`'s 256 is measured in §R3.13. It
  is an unmeasured default and is labelled as one.

## STATE AT HANDOFF (revision 3)

Committed on `lane/subst`:
- c05f137e9: §R3;
- 106c7f04b: the §R2 markers and the design index;
- 9911ddeb0: the review and the reviews index;
- this report's commit.

`make test-spec-history`: see the handback (run after this commit). No owed runs.
Last rulings entry applied: none (the file is empty).

A fresh agent resumes from §R3.16's answers. Phase B is a build lane with a build
go. Its list is §R3.1-§R3.11 (the element, the binding, the glue, codes, the CLI and
header), the spec hunks (match_api §2¶6, §3.8¶9, the subst section, NOSPACE's minus
one, the overlap and stack sentences), the corpus (both BADSPAN patterns and the
corner, the duplicate-name run, the ill-formed-UTF-8 pin, and the PCRE2 difference
rows), sabotage S1346-S1355 with witnesses, and §R3.13's timing cell.
