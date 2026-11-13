# emitted findings

## Findings


### EMIT-1 — CONFIRMED — the stop is asked BEFORE the start-set seek (and never after the entry's seek), so an attempt past the run's last occurrence still runs and can give up
- Severity: speed / give-up (no answer is wrong; the row's own promise "past the last occurrence no attempt can match" is not what the emitted loop enforces). Effort: small (emit order). Blast radius: every `handoff-attempts-unbounded` artifact with a start-set seek; the same ordering exists on the bounded `handoff-attempts` rows (pre-existing).
- Where: src/gen/emit_vm.c:13961 (`pcrec_emit_req_attempt_reentry` before `pcrec_emit_vm_start_seek`); entry: `emit_req_handoff_rest` (src/gen/emit_dfa.c ~1205) sets `attempt_position = search_from` and the entry seek follows with no re-check of `landmark_position`.
- Emitted shape (a+xyz --engine=vm, SUBJECT): `attempt_position++; if (landmark_position < attempt_position) {re-ask; miss -> return 0;} while (!start_set[...]) attempt_position++;` then the next attempt. The seek can carry `attempt_position` past `landmark_position`; that attempt runs with no hit at or after it.
- Repro (budget steps=3000, the rxt witness's own budget), `tools/rxrun.sh subj OUT '(a|aa|b)+cxyz' SUBJ SP --engine=vm --step-budget=3000` vs `tools/p2`:
  - entry case: SUBJ=`cxyz`+30 `a`+`q`, SP=0 -> `err -2` (steps); libpcre2 `nomatch`. (Entry hit L=0; the entry seek moves to 4, past L; the attempt on the a-run gives up. The stop would have answered no match.)
  - entry case 2: SUBJ=`bcxyz`+30 `a`+`q`, SP=1 -> `err -2`; libpcre2 `nomatch`.
  - in-loop case: SUBJ=`bxcxyz`+30 `a`+`q`, SP=0 -> SUBJECT `err -2`, BASE `err -2`, libpcre2 `nomatch` (attempt at 0 fails, advance to 1, L=2 still ahead so no re-ask, seek jumps to 6 past L).
  - The handoff_vm.rxt witness subject is `cxyz`+`aq`+`a`*24+`q`: the `aq` makes the attempt the entry seek lands on fail at once, so the witness does not reach this hole.
- Fix shape: test `landmark_position < attempt_position` (re-ask; miss = NOMATCH) AFTER the seek, i.e. immediately before every attempt (entry included); the bounded rows' move can stay before the seek. Under D-ruled "give-up may become the answer, never the reverse" this only removes give-ups.

### EMIT-2 — CONFIRMED (asm) / SUSPECTED (timing) — per-attempt cost: the second inlined pre-check copy raises register pressure in the attempt loop and grows text ~18% on a small artifact
- Severity: speed (small) + size. Effort: none-to-small (measure first; e.g. mark the re-ask call cold). Blast radius: every unbounded-row artifact; the bounded rows share the text shape.
- Evidence: a+xyz --engine=vm, `gcc -O2 -S`: `rx_search_in` has 0 stack references at -fno-req-handoff, 8 at SUBJECT: the step budget (`subq %rsi,16(%rsp)`), `attempt_max` (`cmpq 8(%rsp),%rbp`) and a setbe flag (`cmpb $0,7(%rsp)`) are spilled and touched once per attempt (not in the innermost a-run loop). `size`: text 3286 (BASE = -fno-req-handoff) -> 3886 (SUBJECT): the kit's `rx_reqrun` body (memchr loop) is inlined twice into each of `rx_search_in`, `rx_next`, `rx_next_n`. For comparison the bounded row on (a|aa){0,10}cxyz grows 8652 -> 8876 (+224).
- What would confirm the speed side: a timing of a dense-start subject (e.g. `[^@ ]+@x` on a long `a@xa@x...` subject) default vs -fno-req-handoff; not run (evening hold).

### EMIT-3 — CONFIRMED (code) — the size-cap rung `drop-handoff` (4a) now also drops the unbounded row, which saves a fixed ~350 bytes, at the price of a full re-compile and the stop
- Severity: design / speed (rare population: artifacts at the 1 MB cap). Effort: small (exclude the unbounded row from `req_handoff_vm`, or order it last). Blast radius: VM artifacts over a size cap that take the row.
- Where: `emit_req_handoff_rest` sets `cx->job->req_handoff_vm = true` whenever `whole`, and the new row has `.whole = true`; `fit_handoff_applies` (src/core/compile.c ~1222) reads only that bit. limits.md §8.4 row 4a now cites ¶8c, so the inclusion is deliberate, but §8.4¶2's "ordered by measured cost" rests on the bounded rows' x2.53 (compile.c comment, still naming only `handoff-attempts[-entry]` and the hybrid re-entry). The unbounded row's text is constant: (alpha|beta|gamma|delta|epsilon)+xyz --engine=vm is 24,190 bytes at -fno-req-handoff and 24,544 at SUBJECT (+354); a+xyz +354 as well. Dropping it can fit an over-cap artifact only at a ~350-byte knife edge, so rung 4a on such an artifact is almost always a wasted full compile, and since fired rungs stay fired, the artifact a later rung (5/6) fits ships without the stop it could have kept.
- Not run: the caps are raise-only (`--max-emit-bytes` below 1,000,000 is refused), so a ladder repro needs a ~1 MB artifact; argued from code.
- Also stale: the compile.c `fit_handoff_applies` header and `Job.req_handoff_vm` comment name only the bounded rows.

### EMIT-4 — CONFIRMED — dead stores and a built-then-discarded buffer in the new branches
- Severity: maintenance / size (emitted text only; gcc removes the stores). Effort: trivial.
- Emitted entry (every unbounded artifact): `size_t handoff_position = rx_reqrun(...); if (handoff_position >= subject_length) return 0; size_t landmark_position = handoff_position; handoff_position = search_from; attempt_position = handoff_position;` -- `handoff_position` is overwritten with `search_from` and only copied on; the plain `landmark_position = rx_reqrun(...)` then `attempt_position = search_from` says the same in two fewer lines.
- `emit_req_landmark_move` (emit_dfa.c ~7853) and `emit_req_handoff_rest` build the `round` round-up StrBuf (`pcrec_emit_start_zero`) before the unbounded early-return/branch and discard it unused.

## PROBED-AND-HELD

Method: `bin/cmp3.sh` (this dir) emits each pattern with BASE, SUBJECT, and SUBJECT `-fno-req-handoff` (each into its own dir, file rx.c, prefix rx), normalizes only `abi 10[35]` / `.abi = 10[35]` and the RX_REQ_HANDOFF value, and diffs. Outputs under emitted/out/<tag>/{b,s,n}/rx.c. ~140 pcrec compiles total, all niced, before 01:00.

(b) PRE-EXISTING forms, BASE vs SUBJECT normalized C: BYTE-IDENTICAL on all 13 that do not take the new row:
- bounded `handoff-attempts` (VM): `(?:xx|y)abc` --engine=vm (K 1); `(a|aa){0,10}cxyz` --engine=vm (K 20), also with -fcomments (comment text identical: the [REQRUN-VM] branch of `pcrec_emit_req_attempt_reentry` is unchanged).
- `handoff-attempts-entry`: `(?:é|ü){2,5}(?i:cat)` --engine=vm -e utf8 (K 10).
- VM hybrid prefilter re-entry (auto -> vm, stamp 6): `([a-z]{2,6})ing\b` --features all.
- VM hybrid with prefilter, no handoff: `(a+)xyz`, `(\w+)@example\.com` (--features all, auto).
- VM, declined (no pre-check row): `(a)\1xyz` --engine=vm --features all (still "none"); `a(b|c)+d` auto (vm).
- DFA routes: `(?:\d{1,3}\.){3}\d{1,3}` (handoff 3), `[a-z]{2,6}ing` (handoff 6), `\d\dxyz`, `a+xyz` auto, `a+xyz(?=q)`, `\w+\bxyz` (--features all, auto -> dfa).
- auto vs --engine=vm: `a+xyz` and `\w+\bxyz` are DFA under auto (identical, "none") and take the new row only under --engine=vm; `([a-z]+)\1xyz` (auto -> vm, backref, no DFA scan) takes the new row under auto.

SUBJECT -fno-req-handoff vs BASE: byte-identical (normalized) on all 10 patterns that take the new row: `a+xyz`, `(a|aa|b)+cxyz`, `[^@ ]+@x`, `.*foobar`, `\w+@example`, `\w+é@x` (-e utf8), `[a-z]+XYZ` (-i), `\w+\bxyz` (all --engine=vm), `([a-z]+)\1xyz` (auto), `(?:alpha|beta|gamma|delta|epsilon)+xyz` --engine=vm; and with -fcomments on a+xyz. So the deny arm is exactly the replaced path.

(a) The new text, every taker: the same 11-line delta (16 with -fcomments): entry keeps the hit (EMIT-4's dead store), the retry gains one compare + a re-ask on pass (the bounded rows' `landmark - pos > K` move is correctly absent; no `round` text emitted for -e utf8). Re-ask count is one per passed occurrence (amortized linear scan: each re-ask scans from the attempt position to the next hit). The min-width stop (`attempt_position >= attempt_max`) precedes the advance and is unchanged; the re-ask sits between the encoding advance and the start-set seek (see EMIT-1 for what that ordering costs). The unbounded row is declined after rung 4a fired (`req_handoff_vm_run` checks `req_handoff_dropped`), code-read only (see EMIT-3).
Answers probed (rxrun vs p2): 7 runs on `(a|aa|b)+cxyz` with steps=3000; every non-give-up answer agreed with libpcre2; the give-ups are EMIT-1.
