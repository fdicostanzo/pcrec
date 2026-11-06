# sound critic: arev2
## Findings
### sound-1 — CONFIRMED, severity ANSWER: row 2 (`AUTO EXISTS`) on the NON-ATOMIC form drops every later branch's retry

- **Cell.** `(?<*a{1,2}|(a))b\1` on `aaba`, startpos 0. libpcre2 10.46 (`tools/probe m`): `[2-4,1-2]`.
  The literal design: **nomatch**. Same shape: `(?<*a{1,2}|(a{1,2}))b\1` on `aabaa`: libpcre2
  `[2-5,0-2]`, design nomatch (row 2 then a `range` branch); `(?<*a{1,2}|(b))x\1` on `abxb`:
  libpcre2 `[2-4,1-2]`, design nomatch (row 2 then a `one-length` capturing branch).
- **Admission, literally.** Branch 1 `a{1,2}`: (a) 1 < 2; (b) no backreference/call/callout in the
  BRANCH (the `\1` is in the follow); (c) no BOT node; (d) builds; (e) VM body (backrefs force it);
  read after the build `lang = same` (no erasure) and "the branch has no capturing group". So row 2
  (arev rev 1 §3.1, the table's row 2; "Row 2, per branch i: the guard, the call with bound = 0,
  t < 0 → L_b_(i+1), else goto L_ok").
- **The step that moves the answer.** At cursor 2 the walk accepts (s = 0 or 1), `goto L_ok`,
  NO frame pushed. Follow: `b` matches, `\1` is unset → `rx_fail`. In today's wiring the ONLY way
  back to branch `i+1` is a frame pushed by branch `i`: the one-length row pushes
  `RX_PUSH(&&L_b_(i+1))` after its guard (emitted C of `(?<*ab|(c))x\1` at e20dee230:
  `rx_L4: if (scan_position < 2) goto rx_L7; RX_PUSH(&&rx_L7, scan_position); ...`), and rev 3's
  `range` reaches `L_b_(i+1)` only through its own `L_adv_i` frame → `L_n_i` (vlookbehind rev 3
  §5.1: "L_n_i: scan_position = POS; goto L_b_(i+1)"). Row 2 has neither, so the pop goes below the
  assertion and branch 2 `(a)` (which sets g1 = (1,2) and lets `\1` match) is never tried.
- **The text that claims otherwise** (arev §3.1 "Composition with vm_look"): "On the NON-ATOMIC
  positive form `(?<*...)` the missing frames are retries that a capture-free body cannot make
  observable: every retry ends at the same cursor with the same groups". True for the row-2
  branch's OWN retries; false for the retries the missing frame also carried: every LATER branch,
  which may capture. The cited evidence (vlookbehind_pieces §3, "capture-free sweep cell") is
  capture-free for the whole lookbehind, so it never contains this population. The STOP RULE
  paragraph ("The hand-off is sound on every body the row admits") inherits the error.
- **Not affected:** the atomic `(?<=` and negative `(?<!` forms (`L_ok` cuts to the mark either way);
  row 3 (its exhaustion goes through `L_adv_i` → `L_b_(i+1)`); a row-2 branch that is the LAST
  branch, or whose later branches are all capture-free.
- **Fix (small, either):** (i) row 2 on the non-atomic form pushes `RX_PUSH(&&L_b_(i+1))` before
  `goto L_ok` (the one-length row's own frame; frames +1, trail 0), or (ii) admission conjunct: on
  `(?<*` row 2 needs every LATER branch capture-free (else the branch takes row 3). Add a witness
  WD-NA: the cell above, plant = row 2 with no frame. Model: `sound/model.py revdfa` (literal rows
  2/3) reproduces nomatch; `cursor` gives libpcre2's answer.
- **Sweep** (`sound/sweep.py`, `sweep.out`): 552,900 cells (1-3 branches from 19 bodies × 3 forms ×
  8 follows × 49 subjects) against libpcre2 10.46: the literal `revdfa` evaluator differs on
  **1,702**, ALL `(?<*` cells, all this shape; the `cursor` control (rev 3 range) differs on 0. With
  fix (i) applied (`sound/fix/model.py`), all 1,702 agree with libpcre2.
- Effort: one paragraph + one witness. Blast radius: rows 2's records and the reader table
  (row 2's "push sites 0" becomes 1 on `(?<*`).

### sound-2 — CONFIRMED (text), severity DOC/WITNESS: "read from the byte at `from`" does not decide `$`, `\Z`, `\z` at the cursor

- arev rev 1 §2.5 (last paragraph): "`(?m)$`, `$`, `\Z`, `\z` and `\b` at the cursor are
  RIGHT-context rows, read from the byte at `from`"; §2.3 declares the part's EFFECTS as "reads
  `subject[bound − 1 .. from]`". Taken literally this is wrong for three of the five: `$`/`\Z` at
  `from` hold iff `from == n` or (`from == n − 1` and `s[from] == '\n'`), and `\z` iff
  `from == n` (no byte at all). The DFA already has the facts for this (dfa.c:1430-1432, the
  base/eolv/endv position views; the emitter's view selection, emit_dfa.c:15228-15275), so the
  realization exists; the record does not name it. W2's `from` column has a seed LIST for exactly
  this reason, the L column (`SLOT(POS)`) has none.
- Cell a part keyed on the byte alone gets wrong: `(?<=a{1,2}$)\nb` on `aa\nb` (probe `m x`):
  libpcre2 **nomatch**; "`s[from]` is `\n`, so `$` holds" → row 2 yes → `[2-4]`. Control
  `(?<=a{1,2}$)\n` on `aa\n`: `[2-3]`; `(?<=a{1,2}\z)\n` on `aa\n`: nomatch.
- WD8's three cells all have `from == n` or a word byte at `from`, so the plant "the part reads only
  `s[from]`" survives every listed witness. Fix: state the start-view rule (the `from` reference
  selects the base/eol/end view by position, as the existing views do) in §2.1's L column and §2.3's
  effects ("reads `subject[bound − 1 .. from]` and compares `from` with `subject_length`"); add the
  two cells above to WD8. Effort: two sentences, two cells.

## PROBED-AND-HELD

- Literal row 2/3 evaluator (`sound/model.py revdfa`: rows chosen by the §3.1 table, machine =
  the branch with atomic/possessive/lookaround ERASED, candidates ascending with the moving bound,
  confirm = the body + end-check, today's wiring for the three forms) over 552,900 cells: every
  `(?<=` and `(?<!` cell equals libpcre2 (0 diffs), including row 2 then range / range then row 3 /
  one-length mixes, erased atomic and lookahead branches, `\b` at both ends, lazy, nested `(?<=b)`.
  Every `(?<*` diff is sound-1.
- Named exits, literally: F1 `(?<=\Ga{1,2})b` (declined by (c), N_GSTART is in
  `pcrec_nfa_has_bot`, nfa.c:1342-1352); F2 `^`/`\A`/`(?m)^` (ctxfn_reads_absent_prev rows, same
  predicate; declined BEFORE the build, so dfa.c:1583's DFA_INVARIANT is unreachable); `(?m)^` cells
  run now via probe `m x`: `(?<=(?m)^a{1,2})b` on `c\naab` [4-5], negative nomatch, on `caab`
  nomatch (the "owed by the build's harness" note in WD-A is runnable today). F3 / WD-B, the atomic
  counter-example WD1, WD2, WD3, WD4, WD5, W-restore: model answer = libpcre2.
- Narrowings not reported by has_bot: none found. `\b`/`\B` and one-char lookarounds are N_CTX
  rows without absent-prev reads (context below the accept, S74); `(?<!a)`-style rows that read
  absent prev are has_bot (safe decline); multi-char lookarounds and atomics are erased (widen);
  `\G`/`^` inside an erased atomic stay in the NFA and are reported. Newline conventions other than
  LF are not implemented (`(*CRLF)` needs module 'verbs'), UCP `\b` under utf8 is refused, `\R`/`\X`
  not implemented: latent only.
- UTF-8 / MATCH_INVALID_UTF: a DFA accept at s implies `s[s..POS)` valid, so `$_back_step` reaches
  it (candidates ⊆ range's); pcrec's byte machine is strict (`.x`, `a.{1,2}x`, `(?<=a.)x` on
  surrogate `ED A0 80` and overlong `C0 80`: nomatch in pcrec at e20dee230, nomatch in libpcre2);
  W-UTF hand-traced (`(?<=é{1,2})x` row 2 yes; `(?<=(é{1,2}))x` row 3 first candidate 1, g1 1-5).
  Stray continuation at the cursor: the reverse walk dies, as back_step's sentinel does.
- Work/give-up: row 3's charge (1 per non-empty candidate tried) ≤ range's `lo + K + (tried − 1)`
  on every evaluation; one-way as claimed (sound-1's fix (i) adds one frame, still ≤ range).
