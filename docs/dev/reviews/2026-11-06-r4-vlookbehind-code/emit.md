# EMIT findings

Critic lens: emitted-vs-replaced. SUBJECT 48606e0360f1, BASE fb22c62a6856.

## Findings

### EMIT-1 CONFIRMED (doc/diagnostic tier; spec-vs-code) -- a backreference inside a lookbehind is now refused with the shape-7 "PCRE2 refuses it too" sentence, claiming "unbounded", where libpcre2 ACCEPTS it and the spec says shape 5
- Repro (SUBJECT tree): `build/pcrec --features lookaround,backrefs,... -e byte -p rx -o /dev/null --pattern '(a)(?<=\1)x'`
  -> `pcrec: every alternative of a lookbehind must have a bounded length (this one is unbounded) (pattern offset 3)`.
  Same for `(?<=(a)\1)x`, `(?<=(a)\1{0,2})x`, `(a{1,2})(?<=\1{0,1}x)`.
  BASE said `variable-length lookbehind is not implemented: ... (this one is unbounded)` (a capability sentence).
- libpcre2 10.46 (own ctypes, scratch emit/pc.py): `(a)(?<=\1)x` on `ax` -> match 0,2 g1 0,1; `(?<=(a|bc)\1)x` on `bcbcx` -> 4,5 g1 0,2;
  `(?<=(a)\1{0,2})x` on `aax` -> 2,3. All ACCEPTED; libpcre2 refuses only truly unbounded (`(?<=a+)x` err 125).
- Spec says otherwise: docs/spec/pattern_language.md:150 (shape 5 capability: "a backreference inside a lookbehind"), :480 ("So is a lookbehind
  containing a backreference (`(a)(?<=\1)`, shape 5)"), :155 (shape 7 = "PCRE2 refuses it too"). Code: src/parse/mod_lookaround.c:367-381
  (`la_width_refusal`, header "EVERY ARM IS A REFUSAL PCRE2 MAKES TOO"; `LBW_UNBOUNDED` is reached by `A_BREF`'s unbounded cwmax).
- Effect: no answer change; the caller is told something false (the construct is "unbounded" and PCRE2 refuses it), and the shape the spec
  promises for this refusal (5) is not what ships (7). D26: the WORDING is low-tier, but the shape/whether-PCRE2-accepts is the exact tier.
- Fix effort: small (an `A_BREF`-reached arm, or a pre-check in the width walk, emitting a shape-5 "backreference inside a lookbehind is not
  implemented" sentence until stage 2). Blast radius: the refusal text only; tests/reject rows naming the text. Design §6 stage 2 / §10.

### EMIT-2 CONFIRMED (doc) -- design G2 states "0 bytes differ, one exception (the ceiling)", but the subject also moves every default `-e utf8` VM artifact with a retry loop (K137), and G2/the ERRATUM do not say so
- Measured: 105 of 220 compiled BASE/SUBJECT pairs differ beyond the abi stamp; ALL 105 are `-e utf8` (default comments or `-fno-comments`)
  and EVERY moved hunk is exactly the 5-line `[K49] The retry advance ...` comment dropped (checked by filtering those 5 lines: 0 residual lines).
  0 byte artifacts moved; 0 `-fcomments` artifacts moved; 0 `--emit-ir` listings moved (6 checked).
  Repro: `build/pcrec --features ... -e utf8 -p rx -o x.c --pattern '(?<=ab|c)x'` at BASE vs SUBJECT: diff = abi stamp (2 lines) + 5 comment lines.
- This is the RULED K137 fix (docs/dev/known_issues.md:14-18, "Comments are off by default, so the movers are every default `-e utf8` VM
  artifact with a retry loop"), so not a code defect. But design §0 G2 (vlookbehind.md, "The one exception is G1's ceiling"; "Measurable: the
  identity gate ... shows 0 bytes differ") and the ERRATUM block do not name K137 as a second exception, and K137 is not mentioned anywhere
  in the design (grep -c K137 = 0). An identity-gate reader holding G2's text will see 105/105 utf8 movers as a G2 breach.
- Fix: one sentence in G2 (or the ERRATUM) naming K137's movers. Effort trivial; blast radius doc only.

## PROBED-AND-HELD

- (a) G2 stability: 51 patterns (fixed-width lookbehinds of every spelling `(?<=` `(?<!` `(?<*` `(*plb:` `(*naplb:` `(*positive_lookbehind:`
  `(*negative_lookbehind:` `(*non_atomic_positive_lookbehind:`, nested, captures, named groups, backrefs after the assertion, subroutine/
  recursion calls, `\G`, `\b`, classes, caseless, zero-width `(?<=)`/`(?<!)`, inside `+`/`*`/`{3}` repeats) x 5 variants each (byte/utf8 x
  default/`--engine=vm`/`-fno-comments`/`-fcomments`/`--emit-main`) = 255 pairs (510 compiles): 115 SAME, 105 K137-only (EMIT-2), 26 both
  refuse identically, 9 rc differ = the intended newly-accepted VARYING patterns (`(?<=(a|bc))x\1`, `(?<=(?>ab|a)c)x`). 6 `--emit-ir`
  listings: 0 lines differ. Ceiling/cap boundaries vs libpcre2 (7 cells): `a{65535}` both accept, `(?:a{1000}){66}` now refused (err 187
  twin, G1's allowed mover), `a{0,255}`/`a{255}|b{0,2}` accepted, `a{0,256}`/`a{300}|b{0,2}` refused (err 200 twin): all agree with libpcre2.
- (b) Answers vs libpcre2 10.46 (vlb_one.sh: every start, every group span): 103 adversarial cells PASS, 0 differ -- multi-branch with a
  varying branch before/after one-length ones, `(?<*` retried after later failure (incl. inside `(*napla:.*...)` = W-low's shape, and
  in `+`/`{n,m}` repeats with re-entry), nested varying lookbehinds both polarities, captures set by failed candidates, lazy/possessive/
  atomic bodies, `\G`/`\b`/`\B`/`^`/`$`/`(?m)`/`(?i)` inside bodies, recursion/subroutine through varying lookbehinds (6), utf8 (9),
  utf8-invalid (17 incl. 5 under asan; subjects with stray continuations, truncated leads, `C2 80 80`). Own ctypes control (not sharing
  bref_oracle.py): 13 cells on 4 capture-heavy patterns, all equal. 6 cells unanswerable by the oracle (libpcre2 match-limit -47 / -52
  nested recursion) or refused by pcrec as backrefs (EMIT-1) are not counted.
- (c) Storage sizing: read `vm_count_slots_look` (one `low` per varying branch, +1 push for a varying LAST branch), `vm_cost_look`
  (`trail += 2 + nvaries`), emission (`vm_slot_lblow(v, v->nlblow++)` in emission order, region saves over the lblow range): each new
  write/frame is charged. Probes: 21 bounded patterns under `-fsanitize=address,undefined` on long subjects (to 100 bytes), up to 12
  captures, 3 varying lookbehinds in sequence, `{20,40}`/`{1,40}` repeats, nested non-atomic: 0 PCREC_ERR_FRAMES, 0 sanitizer reports.
  Unbounded repeats (stamped default capacity): `(?:(?<=a{0,1})a)*x` gives up (-3) from 769 a's, `(?:(?<*a{0,1})a)*x` from 683 -- where
  `(?:(?<=a)a)*x` never does (no trail) and the pre-existing fixed `(?:(?<=a|ba)a)*x` gives up at BASE too (between 1501 and 2000);
  libpcre2 answers all. Every give-up is ABOVE the artifact's stamped `subject_ceiling` (7 patterns: ceilings 146..512, first give-ups
  257..769), so the stamp is honest; this is the pre-existing honest-give-up class (K136 family), widened by one trail entry per varying
  branch exactly as §5.5 derives. Held, not a finding.
- (d) G4 bound: one varying branch vs the same branch one-length, 4 pairs x 2 encodings x comment modes: per-branch program delta 17 lines
  (far set-up 11, retry 6) + per-artifact `$_fwd_step` (5 lines) + 1 local + 1 slot define; e.g. `(?<=a(?:b|cd))x` vs `(?<=a(?:b|c))x`
  +47/-21 lines (byte, default), +68/-25 (`-fcomments`). Within "one slot, one local, ~20 lines". Where the body writes the trail
  (`a{1,3}` span low), K134's 38-line helper set + one `RX_TRAIL_CHECK()` on the `L_adv -> L_try` back edge appear, as §0 G4 states.
- Code vs §5.1 sketch: emitted text for `(?<=a{1,3})x` matches the sketch line for line (guard, `RX_CHARGE_WORK(lo)`, back-step, LO set
  before the first push, `rx_lb_count = min(d, pos)`, far retry from LO, push at try, end-check declines, `L_adv` exhaustion test against
  LO, `rx_fwd_step(..., POS, pos)`, `L_n_i` restore omitted on the last branch). Mid-character startpos under `-e utf8` with asan: 40 cells,
  no crash, no `RX_R_INTERNAL` (only the entry's -7 refusals).

