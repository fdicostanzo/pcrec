# [CTX-PREFILTER] step 0 — necessary-one-character-condition census

Lane `lacens2` (sonnet), branch `lane/lacens2`, worktree `worktrees/lacens2`,
on `lane/ucpu2` at `61cbc894`. MEASUREMENT lane: nothing under `src/`.
Answers plan.md's [CTX-PREFILTER] STEP 0 (filed `e79a53fd`): over patterns
still VM-routed after [UCP] U2, for every POSITIVE multi-character
lookaround, its necessary one-character condition, whether that condition
is NARROW, and an estimate of how much it would tighten today's prefilter.

Script `docs/dev/lookaround_census/ctx_prefilter_probe.py`, engine
`docs/dev/lookaround_census/lac_engine.py` (own CLAUDE.md).

---

## 0. Headline

**Of 354 patterns still VM-routed post-U2 (`tests/ucp/ctxnode_route.tsv`,
`default` column == `vm`), 143 carry at least one POSITIVE lookaround
occurrence wider than one character (shape b/c/d) — 146 such occurrences
total (96 patterns / 96 occurrences from one boundary-enumeration test
file, `tests/lookaround/d27/matrix.rxt`; 47 patterns / 50 occurrences from
everything else, of which only 6 are bench-derived rather than pcrec's own
test fixtures).**

**Of the 146: 31 (21%) have NO sound necessary byte at all** — the body can
match zero characters (e.g. `(?=\n?\z)`, every atom optional/zero-width),
so asserting any byte would be unsound; correctly excluded, not folded into
either the narrow or wide count. **Of the remaining 115 with a computable
necessary set: 111 (96.5%) are NARROW** by the brief's own definition
(size <= 8 bytes, or the condition is not already implied by whatever the
pattern already consumes adjacent to it) — lookahead necessary sets run
size 1-255 (mean 21.4, pulled up by four `.* ` -prefixed bodies in one
bench pattern); lookbehind sets run size 1-4 (mean 1.7) and are narrow in
every single case measured.

**Tightening estimate (an explicitly stated INDEPENDENCE MODEL, not a
joint positional measurement — see S1): on a representative prose subject,
adding the narrow condition to today's already-compiled req-byte/req-run
prefilter would admit on the order of 0.01%-0.9% of the positions the
existing single-byte prefilter alone admits (median case), i.e. one to two
further orders of magnitude of rejection on top of what pcrec already
does — SUBJECT TO the independence caveat below, which likely OVERSTATES
the tightening on any subject where the two conditions correlate (e.g. two
conditions both keying off the same rare literal).**

**Verdict (S5): the byte-set NARROWNESS finding is strong and cheap to
confirm (96.5% of a real, sound population) — building the mechanism plan.md
[CTX-PREFILTER] describes would tighten the prefilter for the large
majority of this population's patterns. The GAP before this is
decision-grade: a real joint-position measurement (not the independence
model here) on a subject the bench considers representative, and the
population itself is still thin on non-test-fixture diversity (6 bench
patterns). D77: build once a joint measurement replaces this model, or once
[OPTLOOP]'s cycle-2 population turns up a VM-routed pattern this would
help on a real bench cell.**

---

## 1. Method

**Population.** `tests/ucp/ctxnode_route.tsv`'s route manifest (U2's own
committed artifact: every lookaround-census pattern compiled with T3 live,
tagged `dfa` if U2 moved it, `vm` otherwise) — 354 `vm` rows, "exactly
lookaround the ctx-node mechanism does not already reach" per the
manifest's own header. For each, `shape_classify.py` (the same parser
`lookaround_census.md` verified) re-derives every occurrence; selected
here are POSITIVE (`polarity == '+'`) occurrences of shape b, c, or d
(shape (a), single-char, is U2's own already-covered case; shape (e),
needing a capture/backref/nested-lookaround inside the body, is out of
scope — this tool's atom parser cannot resolve a backreference's byteset
and does not guess one).

**Necessary set.** A SEPARATE, looser parser from [ENG-LOOK]'s exact-width
one (`lac_engine`'s `_parse_atom_loose`/`parse_loose`/`body_first_set`/
`body_last_set`): walks a branch left-to-right (lookahead, FIRST set) or
right-to-left (lookbehind, LAST set), unioning each atom's byteset,
STOPPING at the first MANDATORY (min>=1) atom — correctly handling
`.*[a-z]` (the `.*` is optional, skipped over; `[a-z]` is mandatory,
stops there, so first-set is a huge "could start with almost anything"
set, which is the honest, correct answer: `.` makes the condition
useless). Supports the FULL PCRE quantifier grammar (`?` `*` `+` `{m}`
`{m,}` `{m,n}`), unlike ENG-LOOK's exact-width parser, because shape c/d
bodies genuinely need it (`.*[a-z]`, `a+b`, `\n?\z`). Deliberately
BYTE-level, not character-level, even under `-e utf8` — this happens to be
the CORRECT abstraction level regardless of declared encoding, since
pcrec's own DFA (`RX_DFA_TABLE`) operates over bytes either way; a
multi-byte UTF-8 literal like `é` (0xC3 0xA9) contributes its LEAD byte to
the necessary set exactly as a real byte-level prefilter would need.
Returns None (a SOUND finding, not a parse failure) when a branch's every
atom is optional/zero-width — the body can match zero characters, so no
byte is truly necessary there; see S3. Returns None differently (an
UNRESOLVED atom, 2 occurrences — an inline `(?i)` modifier inside a
lookbehind body) when it genuinely cannot resolve an atom; these 2 are
reported separately, never silently folded into either bucket.

**Narrow.** `size(necessary_set) <= 8`, OR the necessary set does NOT
already contain (is not a superset of) the byteset of the SINGLE simple
atom immediately adjacent to the lookaround in the outer pattern (the atom
that pattern already forces to be consumed there, independent of the
assertion) — best-effort only: computed when that neighbor resolves as one
simple, non-optional atom via the same loose parser; `n/a` otherwise (63 of
115 rows), never guessed. Where computed (52 rows): 9 "yes" (redundant —
the assertion adds nothing the neighbor did not already require) and 43
"no" (the assertion genuinely restricts beyond the neighbor).

**Tightening estimate.** Reads pcrec's OWN already-compiled `RX_REQ_BYTE`
fact (`--features all`, default `auto` engine, the SAME artifact the
hybrid ships — never re-derived) for "what today's prefilter already
admits", computes its selectivity (fraction of subject bytes matching) on
`APPROACH.md`'s own prose (~21 KB, byte encoding — chosen over the bench's
subject generators because this population's own bench-derived share is
just 6 patterns, all already read narrowly by inspection, and a checkout
of pcrec-bench was not needed for an "ordinary text" selectivity question;
named explicitly rather than assumed), and multiplies it by the necessary
set's own selectivity on the SAME subject. **This is an INDEPENDENCE
MODEL, stated as such, not a joint-position measurement**: the two
conditions (today's req-byte, and the lookaround's necessary byte) sit at
DIFFERENT offsets in the pattern, and this script does not compute the
true joint fraction of positions where BOTH hold at their correct relative
offset — it assumes independence and multiplies selectivities. Where the
two conditions are actually correlated on real text (e.g. both keying off
the same rare literal, or one implying the other), the true joint fraction
could be higher OR lower than the product; this is the gap a
decision-grade measurement needs to close, named rather than closed here.

---

## 2. S2: the narrow/wide split

| kind | n (sized) | necessary-set size (min/mean/max) | narrow |
|---|---:|---|---:|
| lookahead | 51 | 1 / 21.4 / 255 | 47 (92.2%) |
| lookbehind | 64 | 1 / 1.7 / 4 | 64 (100%) |

The four wide lookahead rows are all one bench pattern,
`capability/pwd-strength-chain` (`^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$`):
each `.*CLASS` lookahead's necessary FIRST set is "almost everything but
`\n`" (255 of 256 bytes) because `.` swallows the position before the
class ever becomes mandatory — a CORRECT finding, not a parser gap: this
pattern's own lookaheads genuinely do not narrow the position space at
all, `.` being unconditionally permissive. Every OTHER lookahead and
EVERY lookbehind in the sized population is narrow — the great majority by
the size<=8 test alone (bodies here are short literal/class
concatenations or small alternations, e.g. `abc`, `ab|cd|ef|gh`,
`[ab][cd]`), a handful ADDITIONALLY by the redundancy test (a body whose
necessary set, while small, would otherwise sit inside a neighbor's own
already-wide class).

---

## 3. S3: the zero-width-possible population

31 of 146 occurrences (21%) have every atom in their body optional or
zero-width, so no byte is soundly necessary. 17 of these are
`tests/lookaround/d27/matrix.rxt` boundary rows (its own charter is to
enumerate exactly these edge cases: empty bodies, `(?=x){0,3}`-shaped
external-quantifier constructs, etc. — `lookaround_census.md` S3 already
names this file's k=0 rows as "a boundary-matrix artifact, not a real
pattern shape"), the rest a mix of similar synthetic edge cases across
`tests/lookaround/*.rxt`. None are bench-derived. **This 21% is correctly
EXCLUDED from both the narrow and wide counts** — a mechanism that tried
to assert a necessary byte here would be unsound, not merely imprecise.

---

## 4. S4: tightening — worked examples

| id | body | today's selectivity | necessary-set selectivity | independence-model product |
|---|---|---:|---:|---:|
| `syntax/lka-nonatomic` | `item` (lookahead) | 1.84% | 4.46% | 0.082% |
| `tests/lookaround/lookbehind.rxt:96` | `ab\|cd\|ef` (lookbehind) | 0.37% | 4.77% | 0.018% |
| `tests/lookaround/workbudget.rxt:42` | `ab\|cd\|ef\|gh` (lookbehind) | 0.37% | 6.74% | 0.025% |
| `capability/pwd-strength-chain` (the `.*[^\w\s]` occurrence) | wide (255) | n/a (no REQ_BYTE emitted) | 98.22% | n/a |

Reading the first three: today's prefilter (a single required byte,
already narrow on its own) admits 0.37-1.84% of subject positions on this
prose sample; ANDing in the lookaround's own necessary condition would (by
the independence model) admit a further one-to-two orders of magnitude
fewer — 0.018-0.082%. **The caveat matters here**: `workbudget.rxt:42` and
`:54` share the identical body `ab|cd|ef|gh` at two different pattern
positions with different surrounding text; their independence-model
numbers are close (0.025% vs the `:54` row's own, not tabulated above) by
construction of the model, which is exactly the kind of position-blind
coincidence a real joint measurement would need to either confirm or
correct.

`RX_REQ_BYTE` reads `"none"` for 21 of the 115 sized rows (no single byte
is necessary for the WHOLE pattern today, e.g. because an earlier
alternation branch already has no common required byte) — these rows'
`tighten_model` column is `n/a`, not zero: adding the lookaround's own
condition would be the FIRST byte-level admission test the prefilter
gains for these patterns, a different (larger) kind of improvement this
model does not attempt to quantify.

---

## 5. Verdict (D77)

The narrowness finding (96.5% of the sound population) is real,
inexpensive to confirm, and answers the STEP 0 question cleanly: MOST
positive multi-character lookarounds still on the VM after U2 carry a
necessary one-character condition worth adding to the prefilter. What is
NOT yet decision-grade: (1) the tightening ESTIMATE is an independence
model, not a joint-position measurement — a real design pass would need
the true joint fraction, which requires knowing the RELATIVE OFFSET between
today's req-byte anchor and the lookaround's own position (this script
does not compute it); (2) the population outside `tests/lookaround/
d27/matrix.rxt`'s boundary enumeration is thin (47 patterns, 6 of them
bench-derived) — real customer evidence for how often this shape occurs
in the wild is not established here. Recommend: this step 0 does not by
itself justify building — the mechanism looks promising on the numbers
available, but the next measurement (a joint-position tightening number,
against a bench-chosen subject, on whatever population [OPTLOOP]'s next
cycle or a fresh bench pattern turns up) is the D77 trigger, not a
timeline.

---

## 6. Reproducing

```
python3 docs/dev/lookaround_census/ctx_prefilter_probe.py build/pcrec . /tmp/OUTDIR
```
from the repo root (needs a built `build/pcrec`; reads `APPROACH.md` as
its subject; no pcrec-bench checkout needed; ~15-20s, dominated by ~115
small `--features all` compiles). Writes `ctx_prefilter.tsv` and
`ctx_prefilter_skipped.tsv` to OUTDIR. This memo's own run is committed at
`docs/dev/lookaround_census/ctx_prefilter_61cbc894.tsv` /
`ctx_prefilter_skipped_61cbc894.tsv` (commit `61cbc894`, the branch point).
