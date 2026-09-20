# Grading summary: haiku's name guesses vs. emit_vm.c's comments

226 rows graded, none skipped. Verdicts: 201 correct, 15 partial, 6 wrong, 4 vacuous.

## (a) Verdict counts by kind

| kind | correct | partial | wrong | vacuous | total |
|---|---|---|---|---|---|
| field (72) | 63 | 3 | 2 | 4 | 72 |
| func (129) | 121 | 8 | 0 | 0 | 129 |
| local (25) | 17 | 4 | 4 | 0 | 25 |
| **total** | **201** | **15** | **6** | **4** | **226** |

Functions were nearly all guessed correctly (94%) — this file's function names are
verbs-plus-object (`vm_slot_mark`, `vm_isl_insert`, `vm_render_listing`) and the
convention itself carries most of the meaning. Locals are where haiku did worst:
8 of 25 (32%) were wrong or vacuous-adjacent, all of them single/double-letter
names standing for a whole *struct* or *policy decision* rather than a scalar.

## (b) Confident and wrong (confidence=high, verdict=wrong) — the headline

| kind | name | guess | truth | proposed |
|---|---|---|---|---|
| field | `Vm.b` (really `VEvent.b`) | "string buffer for emitted C code" | It's `VEvent`'s second `int` argument (`int a, b;`), not a buffer at all — haiku's guess is the description of the *other*, real `Vm.b` (a `StrBuf *`) two rows away in the same input. | `arg2` |
| field | `Vm.spl_nw` | "slot savings per region" | Per-target `\|W\|` for a **spliced** call only, and only its CAPTURE half — a specific pre-layout count, not a generic "savings" figure, and it is easily confused with the unrelated `rgn_nw`. | `spl_capture_nw` |
| local | `cut` | "cut mark slot" | No standalone local variable literally named `cut` exists in the file at all — only `cutl` (a label id) and the listing's `"cut"` op-string literal. Haiku appears to have pattern-matched on the file's very frequent use of the *word* "cut" in comments/strings and inferred a variable that isn't there. | n/a — no such local |

`local st` and `local fit` were also both wrong but at **medium** confidence, so they
don't meet the "confident and wrong" bar, though they are worth the same fix (see
top-10 below).

## (c) Vacuous list

All four are struct fields, all high confidence, all in the `rgn_*` family:

- `Vm.rgn_emit` → "region emission flags" (restates the name; the real fact is "does target i still need a SHARED — i.e. non-spliced — region")
- `Vm.has_linked_calls` → "flag: has linked calls" (restates the name; "linked" specifically means "not spliced")
- `Vm.rgn_w` → "region write list arrays" — **this is the manager's own cited example of a vacuous guess**, and it landed exactly as predicted
- `Vm.rgn_nw` → "region write list sizes" (same vacuousness, one level down: it's `|rgn_w[i]|`)

## (d) Top 10 names most worth renaming, ranked

1. **`Vm.b` (the `VEvent` one) → `arg2`.** Two fields spelled `Vm.b` exist in this
   file's own guess set (rows 3 and 6) because `VEvent`'s `int a, b;` pair sits right
   next to `Vm.b`, the real `StrBuf *`. A reader (and haiku) can genuinely confuse
   them; pairing `a`/`b` as `arg1`/`arg2` removes the collision.
2. **`Vm.rgn_w` → `rgn_save_slots`.** The manager's own worked example of "vacuous."
   `w` for "the set of slots a region must save/restore across a call" is opaque at
   every one of its ~6 call sites (`vm_call`, `vm_splice`, `vm_region`,
   `vm_build_region_saves`).
3. **`Vm.rgn_nw` → `rgn_save_slot_count`.** `rgn_w`'s sibling; same fix for the same
   reason (`|W(i)|`).
4. **`Vm.rgn_emit` → `rgn_needs_shared_region`.** The boolean's true meaning
   ("this target is NOT fully spliced, so it needs its own labelled region") is the
   opposite framing from what "emission flag" suggests.
5. **`Vm.has_linked_calls` → `has_nonspliced_calls`.** Same "linked = not spliced"
   fact, at the artifact-wide level; "linked" alone gives no hint of the splice/linkage
   axis this whole module is built around.
6. **`Vm.spl_nw` → `spl_capture_nw`.** Distinguishes it sharply from `rgn_nw`: this
   one is *only* the capture-pair half, and mixing the two up is exactly the class
   of bug `docs/dev/...` records this file having shipped once already (S-SR18/W1.3
   region).
7. **local `st` → `stamp`.** A bare `VmStamp *` parameter named `st` reads as
   "state" to any fresh eye (haiku included) — it is nothing to do with VM execution
   state; it's the precomputed listing-summary struct.
8. **local `u` → `ctx`** (or `userdata`). `void *u` is the callback user-data pointer
   threaded through `vm_walk_caps`/`vm_walk_calls`; `u` reads as C's `unsigned`
   abbreviation and is actively misleading in a file full of real `unsigned` fields.
9. **local `fit` → `engine_fit`.** `job->fit` is an `EngineFit` struct (the engine
   selection's chosen engine, prefilter, and reason) — "fit" alone gives no domain
   hint and haiku guessed a generic "fitness/optimization" meaning.
10. **`Vm.nocap` → `nocap_depth`.** The file's own comment goes out of its way to
    say this is "a counter rather than a bool" so a nested construct can't clear a
    suppression it didn't set — exactly the distinction a `no*` boolean-shaped name
    hides, and haiku's guess ("flag to suppress...") fell into that trap.

## (e) Patterns noticed

- **The `rgn_*`/`spl_*` family is consistently opaque.** Four of this file's six
  worst names (`rgn_w`, `rgn_nw`, `rgn_emit`, `spl_nw`, plus `has_linked_calls`) all
  live in the subroutine-call/splice machinery added by [DD-14]. Each is a
  single/double-letter abbreviation for a *set* or a *policy decision* rather than
  a scalar count, and the family as a whole would benefit from one pass of renaming
  together (they interact: `rgn_w`/`rgn_nw` vs. `spl_nw` is precisely the "two
  answers to a similar-sounding question" pair the design notes say was found wrong
  twice).
- **Names standing for a whole struct, not a scalar, are the ones haiku missed.**
  `st` (`VmStamp*`), `fit` (`EngineFit`), `u` (`void*` context) — all three are
  short, all three read as ordinary English/C words, and all three needed the
  surrounding type to disambiguate. Scalar counters with the `n<family>[_total]`
  convention (`nrev`/`nrev_total`, `nctr`/`nctr_total`, etc.), by contrast, were
  guessed correctly almost without exception — that family's self-documenting
  suffix convention (`_total` = the pre-pass's total, no suffix = the running
  counter) is doing real work.
- **A duplicated identifier across two structs in one guess set (`Vm.b` /
  `VEvent.b`) is a self-inflicted collision** — the file is fine (nothing forces
  `VEvent`'s field to be called `b` instead of, say, `arg2`), but presenting the two
  `Vm.b` rows to a reader with comments stripped reproduces the exact confusion a
  maintainer skimming a diff would have.
- **Functions are this file's strength.** Every miss in the function set was a
  "right area, wording imprecise" partial (e.g. `vm_lifts` guessed as "test repeat
  lifts choice point" when it's really "is this atomic-over-repeat eligible for the
  cut lift") — never a wrong-area or vacuous guess. The `vm_<subsystem>_<verb>`
  naming convention (`vm_isl_*`, `vm_slot_*`, `vm_count_slots*`, `vm_listing_*`)
  is carrying real information on its own.
