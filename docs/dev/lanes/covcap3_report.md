# covcap3 report — [COVER-CAP] design rev 2 (owner's exact/hull span model)

Lane covcap3 (opus), 2026-11-15. Branch `lane/covcap3`, from main `75d365a0b`. Design and
measurement only. No edits under `src/`, `cli/`, `lib/` or `memfn/`.

## STATE AT HANDOFF

- DONE: `docs/design/cover_cap.md` is at revision 2, status PROPOSED. The REVISION 2 block
  comes first, and rev 1's text is superseded in place. Size: 37.3 KB on disk, against rev
  1's 44.7 KB. That is shorter than rev 1 but about 2 KB over the brief's "~35 KB"; the
  overage is mostly the census table and §3.1's soundness text, which I kept.
- STOP RULE: did not fire. Only 1.6% of today's covers branch when read one NFA thread per
  depth, and 0.2% when read one subset per depth (the form rev 2 adopts). No ruling is
  contradicted by the code.
- PREMISE TEST: holds. `a{20}` lists `span_facts 20:` and `RX_DFA_SCAN "cover"`;
  `[0-9a-f]{32}` lists `24:` and is not a cover (`fixed-width`).
- No rulings file was named. No IDs were taken. No runs are owed. The census was a
  48-second read-only pass in scratch, not a queued job.
- Scratch, not committed: `/var/tmp/pcrec-pcrec/scratch/covcap3/`
  - `probe.diff`: the probe instrumentation over `kset.c`, `facts.h` and `known.c`.
  - `census.py`: the census driver.
  - `census.jsonl`: the route pass.
  - `census4.jsonl`: the line pass.
  - `summary.txt`: one row per cover compile.

## CENSUS

**Method.** I instrumented a scratch copy of the tree (`git archive HEAD`), never the
worktree:
- `pcrec_cover` prints the cover decision's `why`, `k`, the anchored DFA rows per depth,
  and the slice's per-depth thread and subset counts.
- `pcrec_span_walk` additionally walks a "line" three ways:
  - one thread per depth;
  - one subset per depth, with the BFS's exact liveness;
  - one subset per depth, with rev 2's two linear reachability passes (§3.1).
- For the line passes, the scratch budget was raised to 65,536 and the horizon removed, so
  the liveness the line passes read is known deeper. The cover classification itself comes
  from the route pass, which ran the probe with today's walk unchanged.

**Population.** `bench_pop()` + `corpus_pop()` from
`docs/dev/optloop/artrev/gen/census.py`. Each distinct (pattern, encoding, icase) was
compiled under BOTH encodings at `--features all`: 11,738 compiles, 10,795 ok. Bench:
331 byte, 335 utf8. Corpus: 5,029 byte, 5,100 utf8.

**Cover route today (`RX_DFA_SCAN "cover"`):** 1,852 compiles.

| population | covers | one thread/depth branching | one subset/depth lost (exact liveness) | lost under rev 2's rule |
|---|---|---|---|---|
| bench byte | 84 | 0 | 0 | 0 |
| bench utf8 | 62 | 0 | 0 | 0 |
| corpus byte | 1,025 | 16 | 2 | 3 |
| corpus utf8 | 681 | 13 | 0 | 1 |

**The 29 one-thread BRANCHING covers** are 16 distinct corpus patterns, all with k <= 4.
None is a bench pattern.
- `tests/altcls/altnf_rules.rxt:127` `ab|abc|ad`
- `tests/assertions/view_edge.rxt:2607` `(?:[a-z]{0,3}\z|x)[0-9]{3}`
- `tests/base/leftmost_semantics.rxt:60` `a*?a`
- `tests/litscan/reqcube.rxt:29` `(?:S(?i:ab)|(?i:sab))` and `:48` `(?:(?i:sab)|S(?i:ab))` (byte only)
- `tests/lookaround/d27/matrix.rxt:545` `(?:(?!a)z|w)` and `:597` `(?:(?![ab])z|w)`
- `tests/possessify/composition_d27.rxt`:
  - `:713` `-*?(?:\b|\B)\W`
  - `:1268` `a{1,3}?(?=a)?\w`
  - `:9090` `(?:a\b)*a`
  - `:9300` `(?:x*\b)*x` (icase)
  - `:10626` `\b\w*?\B\w`
  - `:10988` `a*?(?:\b|)a`
  - `:11108` `a{2,}?(?:)a`
  - `:11123` `a??(?:\b|)a`
  - `:11153` `a??(?:(?=a)|)a`

Read one SUBSET per depth, only `reqcube.rxt:29` and `:48` still branch. After `S` and
after `s`, the walk holds two different subsets whose languages are equal (non-minimal
states).

Rev 2's no-exploration liveness also loses `view_edge.rxt:2607` in both encodings. Its
side branch is dead only through `\z`, so the rule leaves it undecided.

**Form, and the general rewrite.**
- The walk should read the NFA, one thread SUBSET per depth (design §3.1). That is
  determinization applied along the line's one path: the general form, with no special
  case.
- `(?:ab|ba|aa|bb){11}c` is a straight line even one thread per depth, because altcls's
  sibling MERGE rewrites it to `[ab][ab]`. The spanfacts report's `a[ab]|b[ab]` is what
  `-fno-altcls-merge` builds. On that deny arm the one-subset walk ends at 1 and the cover
  declines (answers are unchanged).
- The 2 remaining shapes would need state equivalence (minimization). I did not pursue
  that: two test patterns, k 3.
- The anchored DFA is one row per depth on all 1,852 covers. It is the alternative that
  loses nothing, rejected in §3.1 for keeping C8's second machine and the fact layer.

**Long shapes.** Every long fixed shape is a straight line to its accept, in both
encodings:

| shape | length |
|---|---|
| bench `lit-l31` | 31 |
| bench `lit-l40` | 40 |
| bench `hex32`, `dig-exact-32`, `hex32-id` | 32 |
| bench `uuid`, `wild-validator-uuid-grok` | 36 |
| bench `github-pat` (capture) | 93 |
| corpus `litrun` | 31 / 32 |
| corpus `spanarms.rxt:96` `(?:abc){20}` | 60 |
| corpus `counterk.rxt:1919` | 49 |
| corpus `a{500}` | 500 |
| corpus `[ab]{1000}` | 1000 |
| corpus `(ab){300}` (capture) | 600 |

**Listing (`span_facts`).** Of 5,680 listing compiles, 76 grow and 221 shrink. The rev 2
rule's line ends are:

| end | compiles |
|---|---|
| accept | 3,324 |
| branch | 1,980 |
| root-branch | 111 |
| branch-undecided | 109 |
| undecided | 73 |
| dead | 59 |
| opaque | 24 |

The rev 2 rule never stated more than the exact-liveness line, except in 26 compiles where
the BFS's own budget left that line unknown. Some of those "opaque" ends are a cycle
artifact of the probe, which walks BFS subsets; the design's repeat rule ends such a line
as dead.

**The subset budget is a length cap.** A straight line uses one subset per position.
`[ab]{1000}` lists 24 today, and its straight length is 1000.

## DESIGN REV 2

`docs/design/cover_cap.md` rev 2, sections:
- §1 maps the owner's model to the code.
- §2 the census.
- §3.1 the straight walk:
  - one subset per depth;
  - it ends at accept, at a branch, or at an undecided successor;
  - liveness from two linear backward passes (possibly live / surely live);
  - a repeated subset means dead;
  - no budget and no length bound;
  - it deletes the BFS, the liveness pass, the 2 x 24 horizon, the 24-deep loop and the
    `PCREC_SPAN_WALK_SUBSETS` limits row.
- §3.2 the machine reading horizon is `exact_len`.
- §3.3 the hull is off the cover path; N is not built and is filed with a trigger.
- §3.4 the two stages and C15.
- §4 the seam and the request.
- §5 checks and witnesses, with new plants (b) one-thread and (c) undecided-as-live.
- §6 movers in both directions.
- §7 re-timing.
- §8 bounds.
- §9 questions.
- §10 the survival list.

**Challenge to the manager's reading.** The subset walk is not a hull producer: it
produces exact sets with liveness. The hull already exists as `kset_walk`. So the subset
walk retires whole. N belongs to the hull, and the hull has no consumer that reads both
spans today, so N has nothing to label yet.

## WHAT REV 1 PARTS SURVIVE

- **Kept:**
  - the bounds inventory (condensed into §8, with rev 2 verdicts);
  - the premise;
  - the machine reading (§3.2);
  - the two stages and C15;
  - the abi handling (§4.4);
  - the spec hunk (§4.5, which now removes a `--list-limits` row and states where the
    line ends);
  - the checks table and the predicted == observed sweep;
  - the re-timing plan.
- **Replaced:** rev 1 §3.1/§3.3 (exploration to the budget, and the cliff).
- **Dropped:**
  - FACT 3/FACT 4 as run and table offers (R-c, R-e); the size measurements stay, as
    request FACT 3;
  - rev 1 owner questions Q2 (size) and Q3 (budget), answered by R-c and R-d;
  - the horizon sabotage plant.
- **Adapted:** the witnesses, the plants and the mover list (now from the census, both
  directions).

## KIT REQUEST DRAFT

Design §4.3, verbatim there. In summary:
- FACT 1: span lengths with no pcrec-side bound; today's population is 31-1000.
- FACT 2: proof equality over `[-1, k]`, and today's refusals at 32/64/33.
- FACT 3: the measured per-position text growth.
- The bounds on the path are listed as theirs.
- ASK 1: a counted span of any length, statement and reply, in their form.
- ASK 2: compact text where positions repeat. pcrec does not mark repeats; they are in the
  span. They also state the run-time cost.
- ASK 3: G2 cases past 32.
- No form is named, and no GO is given.

## QUESTIONS

In plain words, each with a leaning (design §9):

1. **Accept losing four tiny covers for the simpler walk?** Two corpus test patterns, three
   or four characters long, go back to the engine with the same answers. In exchange, the
   512-step budget, its hidden limit near 511 characters, and the exploration code are
   deleted. Leaning: accept.
2. **Keep the hull and its N out of this change?** A cover is fully proven, so hull
   positions add nothing to it. N waits until something offers the kit an exact span
   extended by hull positions. Leaning: yes, filed with that trigger.
3. **What did "hull only for UTF-8, later" mean?** My reading: a multi-byte character class
   (Cyrillic `[а-я]`) is a branch on its first byte, so the exact span stops there, and hull
   positions could carry the filter past it. Cyrillic literals are straight and cover today.
   Leaning: yes, as a separate later row.
4. **One step or two?** (From rev 1, unanswered.) Step one is pcrec only and covers up to 32
   positions; step two waits for the kit. Leaning: two.
5. **Build go for stage 1**, at opus tier. Leaning: request it after the critic round.
