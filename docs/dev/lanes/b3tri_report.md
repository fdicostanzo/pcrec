# b3tri — TRIAGE of B3's heavy chain reds (lane report)

Lane b3tri (sonnet), 2026-10-13, `lane/b3tri` from `lane/b3build` (45ae66649), with `main`
(ddfac0b93 + the kit G2 ISA merge) merged in first. Tests and test manifests only; no `src/`
or `lib/` change. Logs read: `worktrees/b3build/build/land/{chain,test,axes,recid}.log`.

## 0. Verdict

B3 has NO real regression in the make-test reds. Four of the five red sections are stale
instruments (readers of emitted text/shape that B3 deliberately moved, or a population shift);
the fifth (test-resource) was restri's already-landed pin. The two other chain failures are
a pre-existing classifier bug (recursion-identity) and a budget finding (test-axes). Sections
re-run in this worktree at -j2 / PROCS=2 are green; the owed runs are in section 7.

Chain facts: TEST_RC=2 (perfrun class RED-REAL, 5 sections: test-assertions, test-premul-table,
test-resource, test-cpset-structure, test-encoding-checks; wall 1416 s), AXES_RC=124,
RECID_RC=2 (not named in the brief; found in `recid.log`).

## 2. make test, section by section

| section | cause | class | fix | verdict (here) |
|---|---|---|---|---|
| test-resource | `a{5,25000}` rescue 762911 vs pin 762884 | stale pin, restri's (B4's RX_COMPOUND stamp, +27) | none: arrived with `git merge main` | 42/0 PASS; B3's abi 77 -> 78 does not move the size (same digit count) |
| test-premul-table | 124 `[iff]` + 3 `[bound]` | stale reader (below) | `tests/codegen/run_premul_table.sh` | 16/0 PASS |
| test-assertions | only `run_endvar_identity.sh` (7/8 scripts) | stale premise (below) | `tests/codegen/run_endvar_identity.sh` | endvar 4/0 PASS; section result in section 7 |
| test-cpset-structure | `[2b]` `src/parse/definitions.c:426` reads `u.cls.iv` | new B3 reader of the class payload | function-scoped allowance in `run_cpset_structure.sh` | 29/0 (+17, +59) PASS |
| test-encoding-checks | DD12a(i) K50 manifest | stale manifest (below) | `tests/codegen/manifests/k50_gate_refinement.txt` | 11/0 PASS |

None is a merge-resolution error by b3land and none is a real B3 regression.

### 2.1 test-premul-table (two stale readers, both in the awk `read_artifact`)
B3's F1 one-seed and F2 tagged rev-end walks have no `for (int revend_seed = 0;` loop, so the
section's scan marker read 124 rev-end artifacts as "stamps RX_DFA_TABLE with no scan"
(run_dfa_stamps.sh and run_rev_end.sh already carry the three-form marker set; this file had
only the old one). Added the other two (`if (subject_length > 0 && subject[...] ==`,
`unsigned revend_dist = 0;`). That exposed the second reader: the one-seed form seeds the dead
state INLINE (`reverse_state = -1;` as initializer or under the final-newline test) rather than
through a `*_seed_state` table, so `\d$(?!\n)`, `\d+$(?=\n)`, `a\Z(?=\n)` read as "indexed with
no dead seed cell". The new rule reads exactly the two one-seed statement shapes (4-space
declaration, 8-space assignment; a looser match hit a deeper `reverse_state = 65535;` in an
unrelated walk and made `(?:\W{0,2}\b\w)+` a false [bound] hit, found and tightened).

### 2.2 test-assertions: endvar identity
`run_endvar_identity.sh` claims "`\z`-free => no end view => byte-identical with
`-DPCREC_NO_ENDVAR`". Under B3's F2 tagged walk the reverse machine's accept value is the
match-end distance, so its END view differs from its EOL view without any `\z`: the distinct
end view IS the tag (endmark.md section R.3; section R.8 keeps the eol/end views on non-F2 machines).
50 of 4073 patterns differed; ALL 50 carry the tagged walk (`unsigned revend_dist = 0;`
in the default artifact). The script now classifies them out of the identity count by that
emitted text (read off the SUBJECT artifact, which the reference knob cannot move), counts them,
and FAILS if the exempt class is empty (a dead marker must not turn the gate vacuous). The other
4023 patterns stay byte-identical, the positive control (154 differ, 0 agree unexplained) is
unchanged.

### 2.3 test-cpset-structure [2b]
B3's `eol_tail_plain` (`src/parse/definitions.c`) asks "is every interval of this class
<= 0x7F", a code-point question above the lowering, where a byte-bitmap render would be wrong.
Same shape as possessify `cls_polarity` and derive `is_never_leaf`: added
`src/parse/definitions.c:eol_tail_plain` to `ALLOW_FN` (function-scoped, so the rest of
definitions.c stays policed) with its reviewed-artifact comment. Not routed through
`pcrec_cls_bits`: that would answer wrongly for a class past the byte range.

### 2.4 test-encoding-checks (K50 manifest, a population shift AND a real B3 effect)
Two things combined. (a) The default slice is the first 250 ASCII blocks in sorted file order;
`tests/endmark/b3_rows.rxt` sorts early and pushed `$`, `\Z`, `a*$`, `a*\Z`, `a{0,4}$`,
`a{0,4}\Z` into the slice. (b) Measured at the full population (ENC_MAX_BLOCKS=0): of the
33 `#UNDECLARED` rows, 24 no longer diverge in emitted form under utf8 and are now plain
gate-refinement members (data-only difference: the K50 alphabet class). Cause: [OPT-REVEND] L2
had put these in UNDECLARED because the reverse walk's EOL-vs-END view selector differed per
encoding; B3 removes that selector on end-pinned patterns (F1/F2), so they return to the class
they left. They are all in `GATEPAT`, none in the FORM sub-class (ceiling 16 untouched).
Fix: the 24 rows move from `#UNDECLARED` to plain gate rows, with a dated block. The `\b`/`\B`
FINDING lines in the red log were only the consequence of the failed exact-match (they stay
on the exception list; DIVERGE_STRICT is zeroed on a match).
NOT B3's: at the full population this section is red on main-shaped noise (126 unmanifested
gate pairs, FORM sub-class 63 against a ceiling of 16, K51 rows, `a.{1,50000}z`); the manifest
header already says main does not match at full population. Not touched.

## 3. recursion-identity (RECID_RC=2): pre-existing classifier bug
`FAIL: [default] positive control: the pre-module reference compiled 1 of 421 call-bearing
patterns`. The one pattern is the SQL-keyword line in `tests/compound/split.rxt` (B4's G1
corpus), whose `\(?` is an escaped paren followed by `?`. `mask_classes` kept `\(` verbatim
outside a class and `GROUP_OPEN` (`\(\?`) matched the `(?` inside it, then the fail-safe
filed it as a call. B4's own `cpb4/build/sc/recid.log` shows the identical FAIL (419 patterns).
Fix: an escaped `(` is masked to `\X`; three self-test rows added (escaped paren, escaped
backslash before a real `(?:`, before a real call). Classifier self-test passes with the real
pattern now call-free. The FULL section is not re-run here (owed, section 7).

## 4. test-axes (AXES_RC=124): a budget finding, not a hang
- `axes.log`: 50 `axes: axis` lines, every one `mismatches=0 lost=0 gained=0`; the last,
  `--harness=no-compound`, completed with agree=62360. `make: *** [test-axes] Terminated` came
  after it. Not run: the final `--engine=vm` arm only. No FAIL anywhere in the log.
- The chain kills at `gnutimeout 7200`: test.log closed 07:21, axes.log last written 09:21 (7200 s later).
- B4's run (cpb4 posthold log): 03:49:11 -> 05:49:11, i.e. the same 7200 s, rc 0. So B4 already
  consumed the whole ceiling; the registry then grew by one axis (49 -> 50 bit axes:
  `-fno-rev-end-onewalk`, bit 56, about 140 s each if the 7200 s were spread evenly over 51 arms, an ESTIMATE: axes.log carries no per-axis timestamps), and the chain ran with other
  heavy lanes on the box (perfrun `contaminated=YES`, load ~9). Any growth tips it.
- Cause: growth past a budget with zero headroom. The 7200 is the CHAIN's wrapper, not a
  Makefile budget. Proposal: `gnutimeout 10800` for the axes stage on this box (a bigger budget
  is justified here only because the cause is named; the axis count has grown 4 times since the
  budget was set).
- The unrun `--engine=vm` arm was re-run alone in this worktree (section 7).

## 5. Changes (all under tests/)
`run_premul_table.sh`, `run_endvar_identity.sh`, `run_cpset_structure.sh`,
`run_recursion_identity.sh`, `manifests/k50_gate_refinement.txt`. No abi/stamp/spec change.

## 6. Learnings
- Four of five reds were readers of one shared text marker (`revend_seed`) that three scripts
  carried and two did not: when a form family gains a spelling, grep EVERY reader of the old
  marker (the D94 lesson again), `WALK_RE` in run_rev_end.sh is the list to grep from.
- A population-shift red (the 250-block slice) can surface a stale claim that a feature made
  true: read the full-population classification before editing a manifest.

## 7. Owed / verified
Verified here: test-resource, test-premul-table, test-cpset-structure, test-encoding-checks
(slice), run_endvar_identity.sh, the recid classifier self-test. See the final message for
test-assertions (whole section) and `--engine=vm` axis results if they had finished at write time.
OWED (heavy, not run): `make test-recursion-identity` (RECID), the rest of the chain after
B3's current stages (mech S74.. list) is B3's own, and a full `make test` on the merged tree.
