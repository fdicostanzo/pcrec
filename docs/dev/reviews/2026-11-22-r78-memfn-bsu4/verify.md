# VERIFY r78 memfn-bsu4

(append below; never overwrite)

## Findings


### 1. G2V-1 -- HOLDS (A and D replayed)
Fake roots verify/A, verify/D (symlinks to review tree, copies of g2/ and g2_vspan.py mutated).
- A: g2_vspan_drv.c:161 `win = place ? d + data - (size_t)k : d;` -> `win = d;`; `python3 -I verify/A/memfn/tests/g2_vspan.py unit --root verify/A --lib $W/build/libpcrec.a --work wA`: `checks passed: 2485`, `checks failed: 0`, rc=0 (windows 1177900 x2, wrong 0).
- D: g2_vspan.py:606 `for layer in ("off", "on"):` -> `("off",)`; `... whole ...`: `checks passed: 177 / failed: 0`, rc=0 (find-all runs 45120, half of the clean 90,240, still green). B and C not replayed.

### 2. G2V-2 -- HOLDS
g2_vspan.py:209 `f.write("%d %d %s %s\n" % (c[0], c[6] + 1, c[5], bitmap_hex(c[3])))` (NPOS = k+1); :245-246 `lo, end = f["loops"][0]` / `K = end - lo` (head-0 rendering); :248 `B = 32 if K >= 32 else 16`; :251 compares (kit_lo, kit_k, kit_b, kit_tail) against (lo, K, B, (K, B)) -- kit vs kit. k (the case's own, tuple field 6) appears afterwards only in the message at :252-253; :261 `edge_seen...add(K)` and :263 append (lo, K). No `K == k` or LO-vs-row compare exists (grep of `\bk\b` shows no such line). Mitigation only via the reach floors (:270-273) keyed on K.

### 3. PINS-1 -- HOLDS
`grep -n "own" tests/memfn/span_pins.py` (review tree): only line 14 ("the kit's own answer"), :134 ("# own predicate holds there") and :138 (message string "V's own row holds") -- no C-own term. `eligible` (:96-98) is `return frame == 'E-find' and ((row == 'D-hors' and 16 <= k <= 1000) or (row == 'R7w' and 24 <= k <= 64))`; k_source (:101-114) reads only the loop `end - lo`. The seed census prints only `SPAN-SEED w%d: %d V sites by the k source, %d selector calls ...` (:190); no own count anywhere in the file.
Design (block_span.md at SUBJECT): §10.1 l.1136 "C-own read off the loop's test (no table name)"; §10.2 l.1299-1301 quoted above ("... eligible loop in the census is C-own, §16 item 5 ... population (0) is printed by the k-source census (K35)") -- see the two sed lines in verify/ output; the census does not print it. (Sibling g2_vspan.py:551 computes `own` but prints no count either.)

### 4. PINS-2 + PINS-3 -- HOLDS (both)
Copies of span_pins.py in verify/q_noframe and verify/q_dup (symlinked tests/memfn siblings, scripts/), run `python3 -I verify/q_X/tests/memfn/span_pins.py --pcrec $W/build/pcrec --harness $W/build/pcrec-harness --trace $K/trace/subject/pcrec-trace --tree $W`.
- baseline copy: `checks passed: 65`, `checks failed: 0`.
- PINS-2: :98 `return frame == 'E-find' and ((row == ...` -> `return ((row == ...`: `checks passed: 65 / failed: 0`.
- PINS-3: cell 20's layers `['v3']` -> `['off']` (so cells 19 and 20 are identical): `checks passed: 65 / failed: 0`.
(Own slip, disclosed: an earlier attempt symlinked tests/ and overwrote $W/tests/memfn/span_pins.py with the identical baseline copy; `git status --short` in $W is clean afterwards, and the mutants were rerun from fresh real dirs.)

### 5. PINS-5 -- HOLDS
span_pins.py:158 `kit = {int(h) for h in CALL.findall(text)}` (a set of handles) and :190 sums `len(r[1])`; :157 `byk` is also a set. Doubled-call text (verify/p5.py, CALL regex copied from :75): `2 {1}` -- findall sees two calls, the census set has one element; a kit emitting two selector calls at one site compares equal to the k source's single site. (Pin cells count calls with `len(CALL.findall)`, :144, so only the SPAN-SEED census is blind.)

### 6. PINS-6 -- HOLDS
`grep -n "utf8\|'-e'" tests/memfn/span_pins.py` -> no output (no `-e utf8` anywhere in the k-source census; SEED_FLOOR = {32: 28, 4095: 31} :71, byte only). tests/memfn/span_vector_identity.py: :107 `ENCS = {"byte": [], "utf8": ["-e", "utf8"]}` and :116-117 `FLOORS = {("c-default","byte"): 28, ("c-default","utf8"): 20, ("c-vm",...): 0, ("seed4095","byte"): 31}` -- the 4095 floor exists for byte only, no `("seed4095","utf8")` key (:358 uses FLOORS[("seed4095","byte")] and the seed4095 cell runs no ENCS loop, :353-358); utf8 w32 20 is a kit mover count there, not the k source. Nothing floors utf8 w4095 = 21 (design §10.1 "Under `-e utf8`: 20 and 21", §12 "20 / 21 (utf8) DERIVED ... by the independent k source").

### 7. C18WIRE-1 + C18WIRE-2 -- HOLDS (both)
Copies verify/m/rs_{base,above,par}.py of tests/memfn/routing_shape.py run with no arguments (selftest): base, above, par each `rc=0`, 21 PASS / 0 FAIL (counts below).
- C18WIRE-1: :108-109 `{h for h, d in vheads.items() if d[0][0] < at}` -> `set(vheads)`: survives.
- C18WIRE-2: :106 `if helper[0][1:] != (s_, c_):` -> `if False:`: survives.
Reading: the only V control touching the level (:249, 'V level not defined above') is `VBODY + VSEL.replace('__body(', '__w32(')`, no `__w32` defined at all, so it cannot tell above from absent; no VCONTROL renames __body's parameters.

### 8. C18WIRE-4 + C18WIRE-8 -- HOLDS (both)
`funcs`: tests/memfn/libc_census.py:180-182 `nfunc, why = routing_shape.check(text)` and :217 `self.funcs += nfunc`; printed :377-378 "routing: %d offset-skip/pre-check functions". Diff ad3c8f1c2..023ab6eb8 of run_libc_census.sh: only the full-run `funcs=141` -> `funcs=281` plus the comment "routing_shape.py now counts the vector span's selectors"; the --quick array (`... calls-memcmp=23 funcs=107)`, :60) is untouched.
Replays (verify/lc/, `libc_census.py ... --floor funcs=0 --jobs 4`; gcc legs included, 47 s full):
- FULL, BASE's routing_shape.py (verify/lcb fake tree): `routing: 275 offset-skip/pre-check functions` (1533 artifacts); SUBJECT's: see line below. 275 vs the old floor 141: the BASE checker already measured far above 141.
- QUICK: SUBJECT `routing: 150` (903 artifacts); BASE checker `144`; floor still 107 (43 under the measure; losing all 6 V passes).
- FULL, SUBJECT checker: `routing: 281` (so +6 V selectors; 134 of the 140-jump is slack that BASE already had). The comment at run_libc_census.sh:67-68 therefore misattributes the jump.

### 9. C18WIRE-5 -- HOLDS
`grep -n "MFTRACE\|span-head" tests/memfn/span_vector_identity.py` -> no match (rc 1). `git diff --stat ad3c8f1c2 023ab6eb8 -- scripts/emit_sweep.py tests/memfn/span_vector_identity.py` -> empty. `git show <rev>:scripts/emit_sweep.py | grep -n span-vector` is identical at both revs: :634 `("byte", "--memfn=no-span-vector", "c-default"): (28, 0, b"[0-9]{25}")`, :635 utf8 (20, ...), :636-637 c-vm (0, 0, None). Keys are (encoding, flag, stream) only, no -fmemfn-simd base cell: SIMD-off only, unchanged by U4.

### 10. C18WIRE-6 -- HOLDS
simd_floor_check.py:126-127 `# NAMED is (name, pattern, extra flags [, targets]): the optional fourth column names the` / `# targets a witness is NAMED at (None: every target).`; reader :562-563 `if len(e) > 3 and tn not in e[3]:`. Copy (verify/nm) with :145 fourth column `('x86-64-v3',)` -> `None`; `python3 -I verify/nm/tests/memfn/simd_floor_check.py --pcrec $W/build/pcrec --levels verify/lc/simd_levels --harness $W/build/pcrec-harness --trace $K/trace/subject/pcrec-trace --every 3000 --jobs 2`: rc=1, `File ".../simd_floor_check.py", line 563, in main: if len(e) > 3 and tn not in e[3]: TypeError: argument of type 'NoneType' is not a container or iterable`. LOUD, not silent.

### 11. PLANTSA-1 -- HOLDS (by reading; the witness leg of its consequence not re-run)
memfn_arm.py:414 `full = a.every == 1` and :466 `if full and fl is not None:` (floors applied only at every==1); run_sabotage_matrix.sh:3716 `MEMFN_REACH_ONLY=1 MEMFN_EVERY=40 AXES="--memfn" \` (arm axesmemfn). S3531 header (:2): "the detector is ... memfn_arm.py's span-vector DIFFER rows (28 byte / 20 utf8 floors, both layers; arm axesmemfn)". So under the arm the floors are skipped; the witnesses (:411-412, unioned into allpats regardless of --every) are what can red. Not verified: that the plant reds there (the memfn_arm run on the S3531 tree was not replayed; memfn_arm is a test-axes tool and I did not run it).

### 12. PLANTSB-2 -- HOLDS (both halves)
Pattern file verify/p17.txt = `[0-9a-f]{17}`; `$K/kit/run1.sh plant:S3526 v3 p17.txt Z0000000000000000 OUT`: `match 0 17`, `MATCHER-RC 0`, `ORACLE ` (empty: libpcre2 finds none). Same call on `subject`: `nomatch`, rc 1. With `Z00000000000000000` (18 chars): plant `match 0 17`, ORACLE `1 18`; subject `match 1 18`.
Unit on the plant tree: `python3 -I $T/memfn/tests/g2_vspan.py unit --root $T --lib $T/build/libpcrec.a --work verify/wp` (T = plants/S3526/tree): rc=1, `G2VU cases 1430 rendered-V 0 refused 22`, `G2VU windows 0 (x2 placements) false 0 wrong 0 hashes 0`, `checks passed: 25`, `checks failed: 1244`; first red `unit case 1 ([\x04-\xbb], k 16): the k source reads LO 0 K 16 B 16, the kit's __w32 text (0, 16, 16, None)`. So the unit's red comes from the text-number pin and no window is driven.

## PROBED-AND-HELD
- The unmutated baselines reproduced green: span_pins.py 65/0; routing_shape selftest 21 PASS; g2_vspan unit mutant A and whole mutant D green as claimed.
- Mutants B and C of G2V-1 and the PLANTSA-1 witness leg (memfn_arm on the S3531 tree) were not replayed.
- Own disclosure: one early command wrote an identical copy over $W/tests/memfn/span_pins.py via a symlinked dir; `git status --short` in $W stayed clean.

VERIFY COMPLETE
