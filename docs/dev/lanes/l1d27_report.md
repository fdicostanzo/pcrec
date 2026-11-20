# l1d27: D27 goal-level witnesses for lookaround L1

## Summary

I wrote 88 witnesses from the promise alone: 50 for (A), 28 for (B) and 10 look-alike controls (C). Together they cover 264 subjects and 247 oracle matches. Every expectation comes from libpcre2-8 10.46, driven through python3 ctypes and following the find-all protocol of match_api §3.1. None comes from pcrec.

**Answers: no disagreement.** Every witness was compiled twice: with the default engine and with `--engine=vm`. In both builds the matcher's full find-all span list equals PCRE2's on every subject of all 88 witnesses. Every (B) pattern matches nothing, as PCRE2 says. Every (C) control matches as PCRE2 says.

**Soundness: no violation.** Every `req_whole_run` the listing states lies inside every oracle match span. The check accepts a set at any position (masks and bracketed classes are parsed). No run takes bytes from outside the match. Two witnesses guard this: `(?<=nop)st` lists `st` and not `nopst` (facts_listing §4.1.2¶8), and `[a-z]{2}(?=wvz)[a-z]{2}` stops before `z`.

**Listing: 29 witnesses fail the promise.** 22 are (A) witnesses whose lookaround bytes were not joined, and 7 are (B) witnesses not listed `dead`. They group into five findings. Nothing listed `dead` is false, and every control (C) is listed not dead. All five findings are MISSED facts, never wrong ones:

- **F1, the main one.** A consumed position whose class has more than 128 members (`.`, `[^z]`, `[^kK]`, `[\x00-\x80]`) is never narrowed by a positive lookaround that overlaps it, in either direction.
  - The boundary was measured: `(?=kev)[\x01-\x80]{3}` (128 members) lists `6b6576`; `(?=kev)[\x00-\x80]{3}` (129 members) lists `none`.
  - So `jo(?=wl)..` lists `6a6f` where the spec's `look` arm (§4.1.3¶4a: "those bytes narrow the consumed run positions they overlap") gives `6a6f776c`.
  - The same cause loses dead proofs: `(?=xyz)xy[^z]` and `(?i)(?=k)(?-i)[^kK]z` are not listed `dead`, while their ≤128-member twins `(?=xyz)xy[a-y]` and `(?i)(?=k)(?-i)[a-jl-z]z` are.
  - Witnesses: A01-A04, A07-A11, A14, A16, A18, A21, A23-A26, A30 (twin A29), B07, B17.
- **F2.** A wide class (more than 128 members) inside a LOOKBEHIND body drops the whole lookbehind, its exact bytes included. `abc(?<=x[^z]c)` and `abc(?<=x..)` are not `dead`; `abc(?<=x[a-y]c)` is. In a lookahead body, the bytes before a wide class survive: `(?=wq.)[a-z]{3}` lists `7771[61-7a]`. Witnesses: B15, B22 (twin B21).
- **F3.** A counted repeat `{n}` inside a LOOKAHEAD body drops the fixed bytes after it. The same language spelled out joins them, so the listing depends on spelling:
  - `(?=a[a-z]{2}l)[a-z]{4}` lists `61[61-7a][61-7a][61-7a]`, while `(?=a[a-z][a-z]l)[a-z]{4}` lists `61[61-7a][61-7a]6c`.
  - `a(?=[a-z]{2}z)bcy` is not `dead`, while `a(?=[a-z][a-z]z)bcy` is.
  - A lookbehind body is unaffected: `abc(?<=x[a-z]{2})` is `dead`.
  - Witnesses: A31 (twin A32), A26k, B14k (twin B20), B14.
- **F4.** A lookbehind nested in a lookahead body is not joined. `(?=[a-z][a-z](?<=xy))[a-z]{2}z` lists `none`, where the spec allows `78797a`. A nested lookahead in a lookahead does join: `(?=r(?=ne))[a-z]{3}` lists `726e65`. Witnesses: A11, A11k, A11w. This is lower-tier: the spec does not name nesting explicitly.
- **F5.** Two contradicting lookaheads followed by a variable repeat lose `dead`. `(?=xy)(?=xz)\w+` is not dead. `(?=xy)(?=xz)` and `(?=xy)(?=xz)\w\w` are. Witness: B05 (twins B23, B24). This is lower-tier: §4.1.3¶1a names two lookbehinds and not two lookaheads, and `dead` is one-sided. It is still the same impossibility listed two ways.

## Witnesses

Files, all in `/home/pcrec/projects/pcrec/worktrees/l1d27-cell/`:

- `l1d27_witnesses.rxt`: the 88 blocks. Each carries `features lookaround,classes,modifiers` (`encoding utf8` where needed), the file-level `oracle pcre2/10.46`, and a `# WITNESS <id> kind=<A|B|C>` comment.
  - Each subject has the first match (`m`/`n`), every later match as `ms <resume> ... s e`, a final `ns <resume>`, and an `mc` find-all count.
  - The 7 blocks python `re` cannot express or answers differently (`\x{..}`, mid-pattern `(?-i)`) carry `# pcre2-only`.
  - The file parses: `build/pcrec --list-source` exits 0.
  - Every case is PCRE2's answer, and pcrec was checked against each one by my own driver. The repository harness is not in the cell, so the file has not been run through `tests/harness/run.sh`.
- `l1d27_listing.tsv`: the listing half the format cannot express. One row per witness with: id, kind, pattern, encoding, the oracle's spans per subject, whether the auto and vm matchers matched the oracle, the listing's `req_whole_run` value and `why`, the spec expectation, PASS/FAIL, and the finding text.

The witness families:

- **(A), 50 witnesses: lookaround bytes join the run.**
  - Lookahead and lookbehind, each alone, on both sides, and both at once: A09k `[a-z]{2}(?<=ws)(?=tk)[a-z]{2}` lists `7773746b`.
  - Nested: A10k, A11w.
  - Alternation before and inside the lookaround: A25k, C08.
  - Classes and cubes: A12 `707879/feffff`, A28k `776f[213f]`.
  - Repeats: A14k `(?:(?=ln)[a-z]{2}){2}` lists `6c6e6c6e`; A31/A32.
  - Case-insensitive: A15 and A27k `444f56/dfdfdf`. A16k `(?i)[a-z]{3}(?-i)(?<=dov)` lists exact `646f76`.
  - utf8: A24k `c3a965`.
  - One-character lookarounds: A19, A20.
  - Lookaround bytes outside the match that must stay out: A21k, A22.
  - Each (A) witness has a `.`/wide form and a class form (`k` suffix), so F1 is separated from the mechanism working on narrow classes.
- **(B), 28 witnesses: contradicted lookarounds are dead.**
  - Lookahead and lookbehind against consumed text: B01-B03.
  - Two lookbehinds: B04, B18.
  - Two lookaheads: B05, B23, B24.
  - Classes: B06, B10, B16, B17, B19.
  - Case-insensitive: B07, B07k, B08.
  - Nested: B09.
  - A repeated body: B11.
  - utf8: B13.
  - Reaching across consumed text: B12, B14, B15, B20-B22.
- **(C), 10 controls: look-alikes that must NOT be listed dead.** These are the shapes §4.1.3¶1a exempts: an optional part (C01), one branch (C02, C08), a negative lookaround (C03, C09), a zero or star repeat (C04, C05), a caseless agreement (C06), compatible lookbehinds (C07), and an alternation inside the lookaround (C10). All 10 are listed not-dead and match as PCRE2.

Scratch, which is reproducible: `/var/tmp/pcrec-pcrec/scratch/l1d27/bin/` holds `run.py` (oracle plus pcrec plus the checks), `witnesses.py`, `driver_tail.c` (the find-all loop appended to each artifact) and `emit.py`. Results are in `../out.json` and `../run.log`.

## How each can fail

- **Answer leg (all 88).** The pcrec matcher's full span list must equal PCRE2's on every subject, under both the auto and the vm engine.
  - It fails if the lookaround's bytes are wrongly used as a filter: an over-joined run or a wrong `dead` makes the artifact reject a subject PCRE2 matches. The several-match subjects (`kevkevkev`, `lnlnlnln`, `wo!wo?`) catch a wrong resume or skip.
  - In the `.rxt`, every `m`/`ms`/`ns`/`mc` line is that check in harness form.
- **Soundness leg (A, C).** The stated run, with masks and classes, must lie inside every oracle match span. It fails if the run takes a lookbehind byte before the start (A22) or a lookahead byte past the end (A21k, A03k).
- **Join leg (A).** The listing's run must contain the spec-allowed narrowed stretch at some position. It fails if the lookaround's bytes are ignored: the "old form" the `look` arm describes would list `6a6f` for A03k, `none` for A01k and `[61-7a]{3}` for A27k. This leg is what fails today for F1, F3 and F4.
- **Dead leg (B).** `why` must read `dead`, and the oracle must find no match. The second half catches my own witness errors; one was found and replaced (`(?<=q)[a-p]`). The leg fails if the contradiction proof is lost. F1, F2, F3 and F5 are where it fails today.
- **Control leg (C).** `why` must NOT read `dead`, and PCRE2 must find a match. It fails if the proof over-reaches into an optional part, one branch, a negative lookaround or a zero repeat. A wrong `dead` there would be the dangerous direction if a pass ever consumed it.

## Disclosure

Spawn-time context showed me two things beyond the cell:

- The session-root `CLAUDE.md`: process and tooling rules, nothing about how lookarounds are compiled.
- The memory index (`MEMORY.md`). It names, in one line each, a stream roadmap whose "payoff is cross-engine pieces (reverse DFA in a VM lookbehind)", plus kit/span vocabulary. None of it states how the run walk treats lookarounds. I did not use it.

The cell's `REQ-LOOKAROUND.md` (the `(?<=foo)bar` one-span ruling) is in scope and was read. It describes a future step (the ruling's "after this lands"), so I did not test it as a current promise.

The `--emit-facts` `note` column prints owner source paths (`src/facts/req.c` and others). I saw those names in the listing output and opened no file outside the cell. I read no `src/`, no `tests/` and no git history.
