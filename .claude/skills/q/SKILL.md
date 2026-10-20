---
name: q
description: The owner's next-question command. Presents the open question(s) from docs/dev/owner.md "Questions for you" in plain words with background, example, forces, leaning and consequences, then records the answer. Use when Frank types /q (args - list, kit, bench, a plan tag, or a question id).
---

# /q [arg] — present the owner's next question

The questions live in `docs/dev/owner.md`, section "Questions for you"
(gitignored; the manager keeps it current: `pcrec-manager` §2,
`docs/dev/CLAUDE.md`). This skill only presents and records; maintaining the
file is the manager skill's job.

## Which question

- No arg: the oldest open question that BLOCKS something; if none blocks,
  the highest-value one. Present ONE.
- `list`: one line per open question (id, plain-words summary, what it blocks).
- `kit` / `bench`: the open questions relayed from those sessions.
- A plan tag (`DD-11.5`) or a question id: that question.
- Nothing open: say so in one line and stop.

## How to present (in this order)

1. The question, in plain words.
2. A short background snippet.
3. A concrete regex example where it helps, as the manager writes them
   (e.g. `(?m)^a|\B`).
4. A one-line gloss at first use of every plan tag, decision id or file name.
5. The forces.
6. The manager's leaning.
7. What happens under each plausible answer.

## Rules (memory names)

- `pcrec-plain-words-not-ids`: Frank cannot track item numbers.
- `pcrec-discussion-not-menus`: lettered options are fine, but they are not
  the closed space; leave room to bat it around.
- `pcrec-conclude-before-writing`: finish the analysis first, never flip
  mid-answer.
- `pcrec-no-question-ui`: never AskUserQuestion; ask in plain text with a
  recommendation.
- `pcrec-answer-free-choices-are-mine`: a choice with identical answers and
  equal cost is the manager's call; do not relay it.

## When the owner answers

1. Mark it answered in `owner.md` with the date.
2. If it is a ruling, write it to `docs/dev/decisions.md` and/or
   `docs/dev/plan.md` (same change as the state it moves).
3. If it is the kit's or the bench's, relay it by the channel the
   `pcrec-manager` skill names (kit ledger `memfn/docs/requests.md`; bench
   `inbox_from_pcrec.md`, single-file `[inbox]` commit).
4. Refresh the rest of `owner.md` (Now, Next, Blockers).
