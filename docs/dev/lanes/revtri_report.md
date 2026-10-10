# revtri — triage of lane/revbuild's landing red

Lane revtri, 2026-10-10, opus. Branch `lane/revtri` from `lane/revbuild`
`5c5d497a` ([OPT-REVEND] L1 + L2 with stage 2, abi 73). Input: the landing
chain's `make test` log (`worktrees/revbuild/build/land/test.log`), red in
test-lookaround, test-assertions, test-premul-table, test-encoding-checks and
test-cand-oracle. Control: main `a15fb77b`, built in a detached worktree.

## 0. The answer-level statement

**No answer regression.** No pcrec answer differs from libpcre2 in any of
the five sections. The only reds that mention libpcre2 are five utf8 cells of
`tests/assertions/rev_end.rxt` (`é+$`, `.$`). Those reds come from two
verifiers that run byte semantics on a block that declares
`encoding utf8`:

- `tests/assertions/verify_pcre2.py`, whose oracle runs at options=0 with no
  PCRE2_UTF;
- the lookaround expansion driver. Its oracle also reads the pattern as
  latin-1, so `é` reached libpcre2 as the single byte E9, which is why
  B == C reported 3 cells.

All eleven utf8 cells of those three blocks were checked against libpcre2
10.46 with PCRE2_UTF (a scratch C probe), and the file's expectations agree
on every one. The same cells under `-e byte` were also run through the
harness, and pcrec matches libpcre2's options=0 answers 11/11. Every other
red is a stale pin, a stale manifest, or a witness that stopped reaching its
site, each caused by revbuild's own changes. None is pre-existing on main in
the light tier. One full-population fact is pre-existing (§2).

## 1. Fix by fix

| section | check | class | evidence | fix | commit |
|---|---|---|---|---|---|
| test-assertions | libpcre2 oracle, rev_end.rxt:267/268/285/286/287 | (b) instrument | rev_end.rxt's 3 utf8 blocks are the first `encoding` blocks in tests/assertions/. The oracle has no PCRE2_UTF. With PCRE2_UTF, libpcre2 gives (1,5), (1,5), (1,3), (1,3), (0,2), which is what the file says | `verify_pcre2.py` skips and counts a non-byte `encoding` block, the existing `flags` mechanism. Result: rev_end 204 verified, 11 skipped | 306db9e6 |
| test-lookaround | `run_expansion_diff.sh` §1 population (12 pins), §1c fidelity (5 cells), B == C (3 cells), policy counts (3) | (b) stale pin + instrument | main's generator gives exactly the old pins (499/12905/...). The delta is rev_end.rxt's 46 blocks / 215 cells / 25 g. The fidelity and B == C cells are the utf8 blocks, scored with byte arms | New rule Q7 in `expand_corpus.py` disqualifies a non-byte `encoding` block (3 blocks / 11 cells). A FATAL guard is added for a non-ASCII qualifying pattern (arm C reads patterns latin-1; population 0). Pins re-derived on HEAD with a DELTA 4 comment: 545/13120/92, qual 337/11249/38, P1 337, P2 444, identity 76/106, lookaround 253/308 | 306db9e6 |
| test-premul-table | `[iff]` ×143 and `[agreement]` 143 drift | (b) check gap | A rev-end artifact contains a DFA scan, the reverse walk, and stamps the reverse machine's table form truthfully. `read_artifact` knew only the forward/attempt/empty/hybrid markers | Scan marker `for (int revend_seed = 0;` added, shared with `run_dfa_stamps.sh` | 306db9e6 |
| test-cand-oracle | `a\Kb\z` does not reach `offset-set-bounded` | (b) [MECH-REACH] | Stage 2 (`928f7d20`) put the VM hybrid's inlined body on `rev-end`. The witness file was last edited at L2.2 (`a2d3f861`), before stage 2 | Witness `a\Kb\b` (default) plus `-fno-rev-end a\Kb\z` (the old witness, pinned to the row the deny lands on) | 306db9e6 |
| test-cand-oracle | take cell `search-from vm ENDSET` reached by no witness | (b) missing witness | Stage 2 declared FIN4's VM ENDSET cell and added no witness. `(\s+)$` reaches it (trace build: a tie inside the inlined body) | Witness `search-from - (\s+)$` | 306db9e6 |
| test-encoding-checks | DD12a(i) [K50]: 4 STALE rows, undeclared-form list mismatch, 11 strict pairs outside the regions | (b) stale manifest | On main, end-pinned nullable patterns (`a*$`, `a{0,4}\Z`, ...) sat in the GATE class's FORM sub-class. Their axis-C view-selector move (eol-only under byte, end+eol under utf8) was DECLARED by the forward scan's `DFA_PREFILTER` stamp changing. The rev-end walk has no forward scan, so the stamp no longer moves, and the same view-selector move now sits undeclared on the reverse walk | Manifest re-derived from a FULL-population DD12a(i) run (`ENC_MAX_BLOCKS=0`, both trees), as a delta. 18 patterns left GATE for strict: 10 manifest rows removed, all 18 listed `#UNDECLARED`. 4 new rev_end.rxt strict patterns listed `#UNDECLARED`. 3 new rev_end.rxt GATE patterns added | 979e19df |

### The encoding check's evidence

For each of the 22 new strict pairs, the byte and utf8 artifacts were
re-emitted with the same prefix and basename and normalized (digits, data
rows, the K50 guard block, the three per-encoding stamps). The residual
bodies (`next_pos`, `valid_upto`) and `.findings` are excised by the check
itself. What remains is the view selector (`view_emit_eol_only` vs
`view_emit_end_and_eol`, `src/gen/emit_dfa.c`), and nothing else:

- on the reverse walk for 21 pairs;
- on the forward scan for `(?:a$)?\b`.

The selector is chosen by machine data (which view tables exist), not by an
encoding conditional. That is the mechanism the existing UNDECLARED rows
record for axis E. The stamp family has no member for axis C either; this is
the same finding the manifest already carries, now on a second axis.

## 2. Findings

1. **A pre-existing full-population red (class c, main `a15fb77b`).** At
   `ENC_MAX_BLOCKS=0`, main's DD12a(i) does not match its own K50 manifest:
   - 87 distinct strict pattern texts against 11 UNDECLARED rows;
   - GATE 240 pairs;
   - GATEFORM 54 against a ceiling of 16.

   `make test` runs the 250-block slice, so this never shows there. It was
   last re-derived at full population on 2026-09-08. This lane re-pinned only
   revbuild's delta, so the slice is green and the full sweep stays red by
   main's own drift. A whole-manifest re-derivation (`K50_HARVEST=file`) is
   owed to whoever schedules the slot's full sweep. The full-run outputs for
   both trees are in this lane's scratch (`build/tri/enc/`, not committed).
2. **Both oracles in this area are byte-only and say nothing about it.**
   `verify_pcre2.py` and `bref_oracle.py` (via the expansion driver) both
   compile at options=0. `bref_oracle.py` additionally hands libpcre2 a
   latin-1 encoding of a UTF-8 pattern. rev_end.rxt was the first
   non-ASCII/utf8 content in tests/assertions/ to reach them. Both now refuse
   such blocks loudly instead of mis-scoring them. A utf8-aware arm would be
   the general fix, if a utf8 assertion population grows enough to want one.
3. **The revbuild report says "light gates green".** None of the five
   sections was in its light list (§7.1), and test-cand-oracle,
   test-premul-table and test-encoding-checks all read stage 2's or the
   walk's population.

## 3. Validation

Each red section was re-run in this worktree with the fix:

- `make test-lookaround`: green, all sub-scripts (expansion diff 11/0,
  38,072 three-way cells).
- `make test-assertions`, `make test-premul-table`, `make test-encoding-checks`
  and `make test-cand-oracle` (84/0): verdicts in §3.1.
- Full `make test` once after the revbuild chain's `CHAIN COMPLETE`: the
  verdict is in §3.2.

### 3.1 Section re-runs

(filled below)

### 3.2 Full make test

(filled below)
