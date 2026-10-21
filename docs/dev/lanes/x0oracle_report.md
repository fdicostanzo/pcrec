# x0oracle — kit_proof X0, the libpcre2 oracle on the reading (2026-10-21, opus)

Brief: the manager's LANE x0oracle message (kit_proof.md §6.4 / §7 step X0). Branch
`lane/x0oracle` from main `d970abbbc`. Measure/instrument lane: nothing under `src/`.
Full record: `docs/design/kit_proof/x0/results.md`.

## Verdict

**X0 NOT PASSED: STOP RULE.** The reading and libpcre2 disagree beyond U1 on real,
non-plant cells. Per the brief, `conj.py`'s reading is NOT patched. On the 1,197 census
patterns kit_proof §1.2 counts, X0 is clean beyond U1:
- part 1: 0 differences, 43,764 prefix nodes × 256 bytes, 443.9M context × prefix × tail cells;
- part 2: 18.95M differential cells, 1,509 differences, all on `(()|^){0}[b]` (upstream U1).

The real cells:
- **R1 (wrong answers).** conj.py's `k_entry` takes the entry of an UNSEEDED anchored
  machine as row 0, and kvdfa assumes "row 0 = start". On `\Zx` the emitter writes
  `anchored_state = 2`, and row 0 is the eol view's target. The reading walks from the
  wrong row and admits impossible bodies as `cover`: `\Zx`, `\zx`, `\zabc`, `-{0,}?\Z-`
  (native and utf8), `[ab]*\z\W` and `\w{0,2}?$\W` (native). That is 10 items at default
  flags (outside the census population) and 10 under `-fno-rev-end`, 29k differential
  cells. Example: `"Zx"`, cover (1,2), where PCRE2 and pcrec's own artifact give no
  match. The fix in the design is sound-M1 extended to the unseeded arm: C6 reads the
  emitted entry constant on BOTH arms.
- **R2 (under-stated hull).** On a non-cover site the plain-walk hull misses bytes
  consumed only through an eol view: `(a$\n)|ab`, a census site in both encodings,
  states `S_1 = {b}` where libpcre2 has `{b, \n}`. The three K1 witnesses read the same
  way (their verdict still correctly declines). This refutes kit_proof §5.2's claim that
  C8's two producers agree on such bodies, and the trace build's
  "producers-disagree = 0" assertion would fire there.
- **K35.** `cover_conj[]` admits 99 census DFA patterns at their own flags that §1.2's
  population (kvcensus's whole/ctx text classes) does not count. 89 of them are clean,
  and the other 10 are R1. §1.2's admitted totals and B1's mover count are low by these.

Controls, all shown able to fail:
- conj.py plants: S1130 239/239 red, S1131 54/54, S1136 its 3 K1 witnesses (0 census
  movers, as the note says), S1139 53/55 (the 2 are `\d$(?!\n)`, where the plant changes
  no answer), S1140 67/67, and S1132/S1133/S1134 300/300 each (sampled).
- S1143 is UNREACHED by design and was not run.
- S1150: the stated-set check reads the union-narrowing statements RED and the correct
  per-thread slice green; S1149 likewise.
- X0's own plants on 150 admitted patterns: under-state S, over-state S, drop from C_k,
  flip absent-after and report k+1 each go red 150/150; add to C_{-1} goes red 11/11
  where it reaches.
- The OWED per-thread witnesses `a(?=b)[a-z]|ac` and `[ab](?<=a)c|bc` read `cover k=2`
  and are clean (`conj.txt` D, `witnesses.txt`).

Oracle defects found and fixed in this lane (results.md §"Oracle defects"):
- hard partial matching over-approximates prefixes (a pending assertion at the end);
- under MATCH_INVALID_UTF it reports PARTIAL at the end of every valid fragment;
- libpcre2 10.46 under MATCH_INVALID_UTF returns ANCHORED matches that start past a
  leading invalid byte (`a` on `"\x80a"` from 0 gives (1,2)); a candidate
  `upstream_issues.md` entry;
- the site witness horizon;
- `--plant` not reaching Python 3.14's forkserver workers;
- a missing "match longer than k" check, found when the C10 plant let 2 movers through.

kvcensus's `kvpcre.is_prefix` has the same hard-partial over-approximation (a note for
that instrument).

## For the manager (rulings / follow-ups, not done here)

1. R1 and R2 are reading defects in conj.py/kvdfa, the prototype Z2's `MkEnd`/`MkLang`
   are modelled on. A revision lane would fix `k_entry` (emitted constant on the
   unseeded arm), decide C8's machine half under eol views, and recount §1.2 from the
   table (K35). X0 re-runs after that: `x0.py run` on a fresh `pop`, about 4 min for the
   admitted roles on 8 cores.
2. libpcre2 MIU anchored-skip: `upstream_issues.md` entry.
3. Not completed: 2 of 1,941 site patterns (`\b[0-9a-f]{32}\b` and the `\b` UUID,
   utf8, seeded: 133 contexts × 256 bytes × budget per node). 8,896 site byte cells are
   inconclusive (witness beyond `exact+8` bytes or budget); there are 0 on the admitted
   roles.

## STATE AT HANDOFF

- Commits on `lane/x0oracle`: WIP `5e2364d10`, `5d139c7cd`, final (this report).
- Validation is COMPLETE; no run is owed. The final admitted-roles run was
  `build/x0/res_final.jsonl` (trailer `== X0 run COMPLETE: items=1449 sec=229.5`), the
  sites run `build/x0/res_v3_sites.jsonl` (1,939/1,941, stopped on the 2 stragglers),
  and the plants `build/x0/res_plant_*.jsonl` / `res_self_*.jsonl`. The transcripts are
  committed in `docs/design/kit_proof/x0/out/`.
- Premise test passed: `conj.py census` reproduces `conj.txt` A/B exactly (77/665
  native, 50/485 utf8), and the kvcensus selftest passes on 10.46.
- Last rulings entry applied: none (`x0oracle_rulings.md` is "(none yet)").
- Box: no process of mine left running; the box lock is free.
