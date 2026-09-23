# [B83] lane report -- I-103/I-103a's run-form discriminator, one timed block

Executor lane, I-57 terms. Report, never diagnose. Every command run, every
raw number, stated as MEASURED.

**Revision note (2026-09-23, same day).** This report was first delivered
with keyword's arm (d) STOPPED (a byte-offset ambiguity in I-103a's
literal template). The manager's ruling overrode that STOP: build it,
offset-corrected, per the reading given below in section 3 -- the same
correction this lane's own STOP text had already identified, just not
applied unilaterally. Section 0 deviation 4, section 3, and every numeric
table below are from a SINGLE re-run of the full grid (all 24
pattern/config/arm cells, including keyword's now-built arm (d)) so every
number in this report comes from one self-consistent measurement session
rather than two spliced together. The qualitative router/keyword findings
below are corroborated by, but supersede, the first (16-of-22-cell)
delivery's own numbers.

## 0. Deviations from I-103/I-103a's literal text (all listed up front)

1. **Instrument form delivered: the O-50/[B81] fallback shape, exactly as
   `docs/dev/lanes/b81blockd_report.md` documents it.** The REAL
   `testees.pcrec.adapter.Adapter` instance (via `pcrecbench.adapters.
   discover()["pcrec"]`), used ONLY for its `.measure()` method (which calls
   `pcrecbench.driverrun.per_trial`, the real driver-invocation loop)
   against hand-built `handle` dicts pointing at each variant's `.so`; the
   real `pcrecbench.subbench.find("capability")` / `.subjects_for(
   "throughput")` / `.expectation(...)` / `.subject(...)`; the real
   `pcrecbench.harness.calibrate` / `outcome_for` / `classify_giveup` /
   `truncation_for`; the real `pcrecbench.record.match_row`; and the real
   `pcrecbench.reduce.reduce_set_cell` / `judge_trial_agreement` /
   `agreement_line`. No line of `pcrecbench/` or `testees/` was edited. No
   record was written to any store. Runner script:
   `/tmp/optloop5/b83/run_instrument.py` (scratch, not committed).
2. **The throughput subject trees were regenerated in this worktree.**
   `bench/capability/throughput/*.bin` are GENERATED and gitignored
   (harness_contract's own rule); a fresh `git worktree add` does not carry
   them. Ran `python3 bench/capability/gen_throughput_subjects.py` once;
   sha256 confirmed byte-identical to the main tree's already-generated
   copies (`d2e4f134…/t-64k`, `3cf7b248…/t-256k`, `ccbdf7eb…/t-1m` --
   matching `docs/dev/lanes/b81blockd_report.md`'s own recorded hashes).
3. **CONFIG RECONCILIATION (I-103 vs I-103a), per the brief's own
   instruction to follow I-103a's wider list.** I-103's literal text names
   ONE config per pattern, `(auto, --no-captures)` -- `pcrec-nocaps`'s flag
   shape (`--features all --no-captures`). I-103a widens this to "the two
   DFA-route auto configs where the +80.8%/+59.7% live, plus the
   forced-VM pair for router" -- read here as `auto-caps` (`pcrec-auto`'s
   shape, `--features all`, captures ON) and `auto-nocaps` (I-103's own
   config) for BOTH patterns, plus `vm-caps` (`pcrec-vm`'s shape,
   `--features all --engine=vm`) and `vm-in-caps` (`pcrec-vm-in`'s shape,
   same flags + `buffer_frames=32768`/`buffer_trail=131072`) for ROUTER
   ONLY -- exactly the four-testee naming I-102 uses elsewhere in the same
   inbox batch (`auto-caps, auto-nocaps, vm-caps, vm-in-caps`). This is the
   full grid measured below: router x 4 configs, keyword x 2 configs.
4. **Arm (d) on keyword: an initial STOP, OVERRIDDEN by the manager's
   ruling -- built, offset-corrected, in this revision.** I-103a's literal
   inline-loop template is `subject[rp_c] == <byte> && !memcmp(subject +
   rp_c, "<run>", <runlen>)`, which assumes the scanned byte sits at
   OFFSET 0 of the run. Router's own default artifact confirms offset 0
   ("the scan is on byte 47 at offset 0 of the run"; run "/user", byte 47
   = '/', the run's own first character) -- the template applies
   literally there, no interpretation needed. Keyword's default artifact
   states plainly: "the scan is on byte 110 at offset 1 of the run" (run
   "in", byte 110 = 'n' = the run's SECOND character; verbatim region in
   section 3). This lane's first delivery STOPPED here, reading the
   offset correction as a judgment call beyond I-103a's literal text. The
   manager's ruling (quoted in full at the top of section 3) directs the
   correction be applied: "test the scan byte at its actual offset within
   the run... the same found/not-found wiring, no other change" -- the
   SAME reading this lane's own STOP text had already identified, now
   applied. Built and measured on both of keyword's configs below.

## 1. Box facts, pin, subjects

`gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0`. pcrec pin `b1885a83`
(`/home/duxevents/pcrec-bench/build/pcrec-b1885a83`, `PIN.tsv`: commit
`b1885a83dea907d9f942bb0fc19760af3d463b2c`) -- ALREADY BUILT, reused
unmodified, no new pcrec build (I-103's own note). Worktree
`worktrees/b83runform` (branch `lane/b83runform`). Scratch:
`/tmp/optloop5/b83/` (`run_instrument.py`, `work/`, `*.json`,
`run_instrument.log`). `uptime` immediately before THIS (final) run:
`load average: 0.13, 0.15, 0.35` (quiet). Subjects:
`bench/capability/throughput/{t-64k,t-256k,t-1m}.bin` (65,536 / 262,144 /
1,048,576 B), the capability set's own three committed throughput
subjects. Regime: `throughput` (`--find-all`, the driver protocol's
non-overlapping-match count operation).

## 2. Building the variants

Phase-1 argv, mirroring `testees/pcrec/adapter.py::_compile_one` exactly
(`-fcomments` as the fixed protocol token, never in `cfg["flags"]`; the
pattern element as raw bytes, the I-72 convention):

    build/pcrec-b1885a83/build/pcrec -p rx -fcomments <cfg flags> \
        [-fno-req-run | -fno-req-byte] -o artifact.c --pattern <PATTERN>

Phase-2 argv, mirroring the adapter's phase 2 exactly (no `cflags`
axis on any of these configs):

    gcc -O2 -std=gnu11 -fPIC -shared -o artifact.so \
        testees/pcrec/shim.c -DPB_ARTIFACT="<dir>/artifact.c" -I <dir>

Configs (pcrec flags, from `testees/pcrec/configs.toml`):

| config | flags |
|---|---|
| `auto-caps` | `--features all` |
| `auto-nocaps` | `--features all --no-captures` |
| `vm-caps` | `--features all --engine=vm` |
| `vm-in-caps` | `--features all --engine=vm` + driver `--buffer-frames 32768 --buffer-trail 131072` |

Arms: (a) default: config flags only. (b) `+ -fno-req-run`. (c)
`+ -fno-req-byte`. (d) the inline-run hand-twin -- see section 3, now
built on ALL SIX pattern-config pairs.

**sha256 of every built `artifact.c`** (deterministic: identical to the
first delivery's own hashes on every cell built both times):

    d43feb8f87ad53d6...  router-prefix-order/auto-caps/a       (24,157 B)
    51dbd5fd378aa170...  router-prefix-order/auto-nocaps/a     (24,157 B)
    5bca8f4114037205...  router-prefix-order/vm-caps/a         (22,169 B)
    5bca8f4114037205...  router-prefix-order/vm-in-caps/a      (22,169 B) <- IDENTICAL to vm-caps/a
    40edf48a559e7ff7...  router-prefix-order/auto-caps/b       (23,691 B)
    5eda371652181ebc...  router-prefix-order/auto-nocaps/b     (23,691 B)
    af9d62b4d39cadea...  router-prefix-order/vm-caps/b         (21,703 B)
    af9d62b4d39cadea...  router-prefix-order/vm-in-caps/b      (21,703 B) <- IDENTICAL to vm-caps/b
    bfd7e29eaaaf146f...  router-prefix-order/auto-caps/c       (23,442 B)
    9b7e7143902962e3...  router-prefix-order/auto-nocaps/c     (23,442 B)
    892fea2568e2fda5...  router-prefix-order/vm-caps/c         (21,434 B)
    892fea2568e2fda5...  router-prefix-order/vm-in-caps/c      (21,434 B) <- IDENTICAL to vm-caps/c
    0857eb11514f7231...  router-prefix-order/auto-caps/d       (23,979 B)
    9aa54ce420718e48...  router-prefix-order/auto-nocaps/d     (23,979 B)
    e73504317b9f1af4...  router-prefix-order/vm-caps/d         (21,991 B)
    e73504317b9f1af4...  router-prefix-order/vm-in-caps/d      (21,991 B) <- IDENTICAL to vm-caps/d
    aedbb97641aa9c55...  keyword-prefix-order/auto-caps/a      (26,269 B)
    078d176193b3a51a...  keyword-prefix-order/auto-nocaps/a    (26,269 B)
    fe6ab38969bd35d4...  keyword-prefix-order/auto-caps/b      (25,780 B)
    6092e9397a8ec170...  keyword-prefix-order/auto-nocaps/b    (25,780 B)
    41207c93dd3d1d07...  keyword-prefix-order/auto-caps/c      (25,528 B)
    15ac5afab757e4c8...  keyword-prefix-order/auto-nocaps/c    (25,528 B)
    52d9dced5f78b316...  keyword-prefix-order/auto-caps/d      (26,047 B)   <- NEW, this revision
    c20183ecd1a0d16c...  keyword-prefix-order/auto-nocaps/d    (26,047 B)  <- NEW, this revision

The `vm-caps`/`vm-in-caps` sha256 identity per arm is a CONTROL, not
decoration: it confirms the `--buffer-*` driver flags never touch the
emitted artifact, only the runtime call (`rx_search_in` forwards to
`rx_search` on a DFA artifact and, per `rx_search_run`'s own body on the
VM route, the buffer descriptor only rebinds `rx_run_state`'s storage --
the guard block sits in `rx_search_run`, shared by both entries, exactly
as `testees/pcrec/CLAUDE.md`'s cf0962e3-era note ("the guard lives in the
shared search prologue") predicts).

## 3. The guard region, and the manager's ruling on keyword's arm (d)

**The manager's ruling, quoted in full** (2026-09-23, overriding this
lane's own STOP): "BUILD IT, offset-corrected... I-103a's intent is 'an
inline scalar loop of the same semantics as the memchr run-loop'; the
template's offset-0 shape is an authoring artifact of the router example,
and your own reading of keyword's artifact ('scan byte 110 at offset 1 of
the run') gives the unambiguous correction: test the scan byte at its
actual offset within the run, i.e. `for (rp_c = rp_pos; rp_c + 2 <=
subject_length; rp_c++) if (subject[rp_c+1]==110 && !memcmp(subject+rp_c,
"in", 2)) break;` -- the same found/not-found wiring, no other change."

**Router's default guard** (`rx_search`, DFA route; `rx_search_run`,
VM route -- identical text either way), byte 47 offset 0:

    /* [OPT-REQPOS] every match of this pattern contains the 5 bytes
     * "/user", so a window without them holds no match at all;
     * the scan is on byte 47 at offset 0 of the run. */
    if (subject_length <= search_from) return 0;
    {
        size_t rp_pos = search_from;
        for (;;) {
            const void *rp_q = memchr(subject + rp_pos, 47, subject_length - rp_pos);
            size_t rp_c;
            if (!rp_q) return 0;
            rp_c = (size_t)((const unsigned char *)rp_q - subject);
            if (rp_c + 5 <= subject_length
                && !memcmp(subject + rp_c, "/user", 5)) break;
            rp_pos = rp_c + 1;
            if (rp_pos >= subject_length) return 0;
        }
    }

**Router's arm (d)** (the ONLY edit; the two-line comment above it is left
in place, byte-identical text, describing a guard that is no longer
literally a memchr call -- inert prose, not re-derived):

    if (subject_length <= search_from) return 0;
    {
        size_t rp_pos = search_from;
        size_t rp_c;
        for (rp_c = rp_pos; rp_c + 5 <= subject_length; rp_c++)
            if (subject[rp_c + 0] == 47 && !memcmp(subject + rp_c, "\x2f\x75\x73\x65\x72", 5))
                break;
        if (rp_c + 5 > subject_length) return 0;
    }

**Keyword's default guard**, byte 110 offset 1:

    /* [OPT-REQPOS] every match of this pattern contains the 2 bytes
     * "in", so a window without them holds no match at all;
     * the scan is on byte 110 at offset 1 of the run. */
    if (subject_length <= search_from) return 0;
    {
        size_t rp_pos = search_from;
        for (;;) {
            const void *rp_q = memchr(subject + rp_pos, 110, subject_length - rp_pos);
            size_t rp_c;
            if (!rp_q) return 0;
            rp_c = (size_t)((const unsigned char *)rp_q - subject);
            if (rp_c - search_from >= 1 && rp_c - 1 + 2 <= subject_length
                && !memcmp(subject + rp_c - 1, "in", 2)) break;
            rp_pos = rp_c + 1;
            if (rp_pos >= subject_length) return 0;
        }
    }

**Keyword's arm (d), built per the ruling above** -- `subject[rp_c + 1]`
tests the byte at its own documented offset, `memcmp` still compares the
window starting AT `rp_c` (the run's own start), so `rp_c` is a RUN-START
candidate throughout, exactly as the ruling's own formula spells it:

    if (subject_length <= search_from) return 0;
    {
        size_t rp_pos = search_from;
        size_t rp_c;
        for (rp_c = rp_pos; rp_c + 2 <= subject_length; rp_c++)
            if (subject[rp_c + 1] == 110 && !memcmp(subject + rp_c, "\x69\x6e", 2))
                break;
        if (rp_c + 2 > subject_length) return 0;
    }

Same found/not-found wiring as the original on both patterns: the block
falls through (into the forward-table scan) exactly when a run occurrence
exists at or after `search_from`, and `return 0`s exactly when none does.
Answer-check (section 4) confirms this by measurement, not merely by
inspection: keyword's arm (d) answers the identical `nmatches` as arms
(a)/(b)/(c) on all three subjects.

## 4. Answer-check, before any timing

One `iters=1 --find-all` call per variant, all three subjects, via the
real `adapter.measure()` (`work/answer_check.json` carries the full
per-variant per-subject `nmatches`):

| pattern | subject | expected nmatches (expectations.tsv) | measured (every arm, every config, incl. keyword's (d)) |
|---|---|---:|---:|
| router-prefix-order | t-64k | 9 | 9 |
| router-prefix-order | t-256k | 58 | 58 |
| router-prefix-order | t-1m | 245 | 245 |
| keyword-prefix-order | t-64k | 433 | 433 |
| keyword-prefix-order | t-256k | 1791 | 1791 |
| keyword-prefix-order | t-1m | 7243 | 7243 |

**EQUAL across all FOUR arms on every config, on every subject, both
patterns** -- confirmed BEFORE any timed round (full per-variant answer
dump in `work/answer_check.json`; the equality table itself in
`run_instrument.log`). Keyword's offset-corrected arm (d) answers exactly
as (a)/(b)/(c) do.

## 5. Calibration (`harness.calibrate`, real function, one probe per variant)

    router-prefix-order  auto-caps    a  iters=?   (probe run per variant; see run_instrument.log)
    keyword-prefix-order auto-caps    d  iters=58  (865.674 us/iter, t-256k)
    keyword-prefix-order auto-nocaps  d  iters=59  (859.105 us/iter, t-256k)

(full 24-row table in `run_instrument.log`, "=== calibration ===" section)
-- `n_iters` is calibrated PER VARIANT (own probe, own `SetCell`), the
same shape `docs/dev/lanes/b81blockd_report.md` used; `reduce.
reduce_set_cell`'s numbers are ns/call, already iteration-normalized, so
the grid below compares apples to apples regardless.

## 6. Timed rounds -- interleaved a,b,c,d x 5, `uptime` before each round

    round 1 uptime: load average 0.20, 0.16, 0.36
    round 2 uptime: load average 0.26, 0.18, 0.36
    round 3 uptime: load average 0.32, 0.19, 0.36
    round 4 uptime: load average 0.32, 0.19, 0.36
    round 5 uptime: load average 0.37, 0.20, 0.37

Quiet throughout (load1 <= 0.37); the whole run (build + answer-check +
calibration + 5 rounds x 22-24 variants) completed in under 20 seconds
wall time.

**Per-variant `SetCell` (median / min / max / IQR over 5 trials, ns, sum
over the 3 throughput subjects per trial) -- ONE self-consistent run, all
24 cells including keyword's arm (d):**

| pattern | config | arm | median ns | min ns | max ns | IQR (Q3-Q1) |
|---|---|---|---:|---:|---:|---:|
| router-prefix-order | auto-caps | a | 787,317.3 | 782,882.1 | 808,872.4 | 15,985.8 |
| router-prefix-order | auto-caps | b | 412,632.2 | 403,596.9 | 413,016.3 | 5,166.7 |
| router-prefix-order | auto-caps | c | 431,619.2 | 427,425.7 | 461,723.9 | 19,230.2 |
| router-prefix-order | auto-caps | d | 1,156,215.7 | 1,103,178.2 | 1,184,377.9 | 45,547.3 |
| router-prefix-order | auto-nocaps | a | 781,903.2 | 744,590.0 | 786,596.0 | 23,445.8 |
| router-prefix-order | auto-nocaps | b | 408,907.9 | 408,175.7 | 410,081.3 | 1,154.0 |
| router-prefix-order | auto-nocaps | c | 394,955.5 | 393,688.6 | 429,334.7 | 33,874.3 |
| router-prefix-order | auto-nocaps | d | 1,192,511.6 | 1,189,648.6 | 1,201,649.3 | 9,942.6 |
| router-prefix-order | vm-caps | a | 4,761,028.5 | 4,447,090.6 | 4,831,497.2 | 300,880.9 |
| router-prefix-order | vm-caps | b | 4,164,823.9 | 4,049,445.1 | 4,406,439.9 | 347,196.2 |
| router-prefix-order | vm-caps | c | 4,416,365.7 | 4,029,293.6 | 4,440,226.5 | 259,407.3 |
| router-prefix-order | vm-caps | d | 5,229,966.7 | 4,820,662.4 | 5,279,757.4 | 266,001.0 |
| router-prefix-order | vm-in-caps | a | 4,745,346.3 | 4,722,679.5 | 4,804,602.0 | 58,416.5 |
| router-prefix-order | vm-in-caps | b | 4,306,501.3 | 4,048,463.6 | 4,311,078.3 | 259,957.1 |
| router-prefix-order | vm-in-caps | c | 4,337,308.7 | 4,321,602.8 | 4,396,859.0 | 46,477.9 |
| router-prefix-order | vm-in-caps | d | 5,148,141.3 | 5,135,412.6 | 5,162,436.4 | 14,816.9 |
| keyword-prefix-order | auto-caps | a | 1,370,019.7 | 1,282,352.7 | 1,371,686.2 | 59,446.9 |
| keyword-prefix-order | auto-caps | b | 845,451.5 | 800,959.2 | 847,759.8 | 24,556.0 |
| keyword-prefix-order | auto-caps | c | 805,944.6 | 732,874.9 | 807,673.7 | 38,964.0 |
| keyword-prefix-order | auto-caps | d | 1,949,727.7 | 1,938,825.1 | 2,033,898.5 | 57,121.3 |
| keyword-prefix-order | auto-nocaps | a | 1,356,966.4 | 1,343,822.2 | 1,370,450.7 | 14,512.7 |
| keyword-prefix-order | auto-nocaps | b | 844,275.9 | 775,759.6 | 858,945.6 | 65,093.6 |
| keyword-prefix-order | auto-nocaps | c | 799,039.7 | 732,831.2 | 803,786.8 | 37,751.5 |
| keyword-prefix-order | auto-nocaps | d | 1,948,221.2 | 1,941,891.1 | 1,956,407.5 | 12,009.0 |

All 24 cells: `failing_subjects=[]`, `n_wrong=0`, `n_gave_up=0`, trial
agreement **`agree`** (`reduce.judge_trial_agreement`, rule `v1.4-group`,
k=1.5, d_min=2, share_c=3, 5 trials -- a record built from any of these
would stamp `measured`, none `inconclusive-spread`; raw per-round sums
and full agreement lines in `results.json`).

## 7. The EXPECT call counts (I-103/I-103a, quoted) beside the measured deltas

| pattern | config | (a)-(c) ns | (b)-(c) ns | (d)-(a) ns | (d)-(c) ns |
|---|---|---:|---:|---:|---:|
| router | auto-caps | +355,698.1 | -18,987.0 | +368,898.4 | +724,596.5 |
| router | auto-nocaps | +386,947.7 | +13,952.4 | +410,608.4 | +797,556.1 |
| router | vm-caps | +344,662.8 | -251,541.8 | +468,938.2 | +813,601.0 |
| router | vm-in-caps | +408,037.6 | -30,807.4 | +402,795.0 | +810,832.6 |
| keyword | auto-caps | +564,075.1 | +39,506.9 | +579,708.0 | +1,143,783.1 |
| keyword | auto-nocaps | +557,926.7 | +45,236.2 | +591,254.8 | +1,149,181.5 |

I-103's own EXPECT, quoted: "router: (a) 39,098 memchr calls, (b) 315, (c)
0 -- so (a) - (c) ~ +322,000 ns and (b) - (c) ~ 0"; "keyword: (a) 44,135,
(b) 9,470, (c) 9,467 in the prefilter alone". I-103a's own hit-rate facts,
quoted: "router '/' 39,095 hits in 1,375,008 B = 2.8%; keyword 'n' 44,132
in 1,376,256 B = 3.2%".

## 8. The (b)-vs-(c) decision line (I-103's own bar: |Δ| vs max(IQR_b, IQR_c))

| pattern / config | \|(b)-(c)\| ns | max(IQR_b, IQR_c) | verdict |
|---|---:|---:|---|
| router / auto-caps | 18,987.0 | 19,230.2 | **within IQR** (margin 243.2 ns, 1.3%) |
| router / auto-nocaps | 13,952.4 | 33,874.3 | **within IQR** |
| router / vm-caps | 251,541.8 | 347,196.2 | **within IQR** |
| router / vm-in-caps | 30,807.4 | 259,957.1 | **within IQR** |
| keyword / auto-caps | 39,506.9 | 38,964.0 | **outside IQR** (margin 542.9 ns, 1.4%) -- (b) materially worse |
| keyword / auto-nocaps | 45,236.2 | 65,093.6 | **within IQR** on THIS run |

**ROUTER reads exactly as I-103 predicted, on all four configs**: the
byte-only guard (b) is statistically indistinguishable from no guard at
all (c) on every one -- the run form (memcmp-on-top-of-memchr) is the
WHOLE cost of router's pre-check.

**KEYWORD is BORDERLINE, and this report says so honestly rather than
picking the cleaner-sounding of two runs.** In THIS run: `auto-caps`
crosses the IQR bar (by 1.4% of the bar itself -- a thin margin);
`auto-nocaps` does NOT (its own (b) arm's IQR widened to 65,093.6 ns this
round, versus a much tighter 1,583.1 ns in this lane's FIRST delivery,
where the SAME cell's (b)-(c) delta of 48,346.2 ns read clearly outside
it). The (b)-(c) DELTA itself is consistently POSITIVE and of similar
magnitude across both measurement sessions (39,507-48,346 ns on
`auto-caps`, 13,952-45,236 ns... on `auto-nocaps` the two sessions
diverge more, 48,346 ns first vs 45,236 ns here -- both far from zero in
absolute terms) -- the DIRECTION is robust, but whether it clears THIS
particular IQR decision rule depends on which round's own arm-(b) noise
happened to land. Per I-103's own reading rule ("if (b) is materially
worse than (c), the one-byte form costs something too and G1's existing
dominance rule is under-measured") this reads as: keyword's byte-only
guard costs something REAL and directionally consistent (tens of
thousands of ns, not noise-shaped zero, on THE SAME order across two
independent 5-trial sessions), but the specific IQR-crossing bar used
here is sensitive to single-run noise at keyword's own scale -- a finding
about the DECISION RULE's robustness at this sample size, stated as
measured, not smoothed over. Likely mechanism (stated, not diagnosed
further): keyword's match density is far higher than router's on the
same three subjects (nmatches 433/1,791/7,243 vs 9/58/245), so `rx_search`
(and therefore the byte-only guard's single `memchr` call) is invoked
roughly 30x more often on keyword than on router -- a per-CALL cost times
a much larger call count than I-103's own "calls in the prefilter alone"
figures (9,470 vs 9,467) appear to reflect.

## 9. Inline-vs-memchr (BOTH patterns, arm (d) now built on all six pattern-config pairs)

| pattern / config | (d) vs (a) | max(IQR_a, IQR_d) | verdict |
|---|---:|---:|---|
| router / auto-caps | +368,898.4 (+46.9%) | 45,547.3 | **outside IQR -- memchr-run clearly beats inline** |
| router / auto-nocaps | +410,608.4 (+52.5%) | 23,445.8 | **outside IQR -- memchr-run clearly beats inline** |
| router / vm-caps | +468,938.2 (+9.9%) | 300,880.9 | **outside IQR -- memchr-run clearly beats inline** |
| router / vm-in-caps | +402,795.0 (+8.5%) | 58,416.5 | **outside IQR -- memchr-run clearly beats inline** |
| keyword / auto-caps | +579,708.0 (+42.3%) | 59,446.9 | **outside IQR -- memchr-run clearly beats inline** |
| keyword / auto-nocaps | +591,254.8 (+43.6%) | 14,512.7 | **outside IQR -- memchr-run clearly beats inline** |

**Confirms I-103a's own EXPECT on BOTH patterns, all six configs**:
"at 2.8-3.2% memchr-run should still beat the inline scalar loop" --
memchr-run wins by a wide, IQR-clearing margin everywhere it was
measured, at both router's 2.8% and keyword's 3.2% byte frequency. Since
keyword's arm (d) is now built (section 3, the offset-corrected form),
this verdict is no longer router-only.

## 10. Derived constants and the crossover arithmetic, WITH keyword's inline datapoint

**Does the added point condition the system? NO -- shown explicitly, per
the ruling's own instruction, and stopped there rather than forced.**
Both the memchr and the inline two-equation solves remain ill-conditioned
with keyword's own inline point in hand, for the SAME underlying reason
as before: the two patterns' three throughput subjects have nearly
IDENTICAL total byte counts (1,375,008 vs 1,376,256, a 0.09% spread) --
adding a SECOND mechanism's equation pair over the same two subject-count
totals does not change that. Using the `auto-nocaps` cell (I-103's own
originally-asked config) for both patterns, both mechanisms:

    MEMCHR (ΔT = (a)-(c)):
      router:  1,375,008*c_byte +  39,095*c_hit =   386,947.7
      keyword: 1,376,256*c_byte +  44,132*c_hit =   557,926.7
      => (eliminating c_byte) 5,001.5*c_hit = 170,626.8  =>  c_hit = 34.11 ns/hit
      => c_byte = (386,947.7 - 39,095*34.11) / 1,375,008 = -0.689 ns/B  (UNPHYSICAL)

    INLINE (ΔT = (d)-(c), keyword's point now real, not assumed):
      router:  1,375,008*c_byte +  39,095*c_hit =   797,556.1
      keyword: 1,376,256*c_byte +  44,132*c_hit = 1,149,181.5
      => (eliminating c_byte) 5,001.5*c_hit = 350,900.7  =>  c_hit = 70.15 ns/hit
      => c_byte = (797,556.1 - 39,095*70.15) / 1,375,008 = -1.414 ns/B  (UNPHYSICAL)

Both solves land on a negative (unphysical) byte term -- WORSE in
magnitude for the inline system than the memchr one, not better. The root
cause is the FREQUENCY gap, not merely the byte-count gap: router's 2.8%
and keyword's 3.2% differ by only 0.36 percentage points (2.8433% vs
3.2067% on this window's own three subjects, to be precise -- see below),
and a two-parameter linear fit's slope term is proportional to 1/(that
gap), so any few-percent measurement noise in ΔT is amplified into a
wildly wrong intercept. **Reported instead, as single-term bounding
estimates** (assuming the OTHER term negligible, one at a time -- I-103a's
own model implies this is a reasonable simplification, since its assumed
memchr byte term contributes a minority of the total at these
frequencies):

    memchr, per-hit only (assume c_byte ~ 0), auto-nocaps:
      router:  386,947.7 /  39,095 hits =  9.90 ns/hit
      keyword: 557,926.7 /  44,132 hits = 12.64 ns/hit
    (I-103a's own assumed memchr constant: 7.7 ns/hit)

    inline, per-byte only (assume c_hit ~ 0), auto-nocaps:
      router:  797,556.1   / 1,375,008 B = 0.580 ns/B
      keyword: 1,149,181.5 / 1,376,256 B = 0.835 ns/B
    (I-103a's own assumed inline constant: 0.5 ns/B)

Both single-term estimates are HIGHER on keyword than on router (12.64
vs 9.90 ns/hit; 0.835 vs 0.580 ns/B) -- exactly what the neglected term
being nonzero and hit-frequency-correlated would produce (a
per-hit-only reading absorbs a growing byte-term contribution as
frequency rises, and vice versa), which is itself indirect evidence the
two-parameter model is real even though this window's two frequency
points sit too close together to solve it.

**Crossover, using I-103a's OWN stated model constants** (0.017 ns/B +
7.7 ns/hit memchr; 0.5 ns/B + 2 ns/hit inline; f = hits per byte scanned):

    0.017 + 7.7f = 0.5 + 2f
    5.7f = 0.483
    f = 0.0847  (8.47%, matching I-103a's own "near 8%")

**This lane's measurements corroborate the order of magnitude of both
model constants on BOTH patterns now (memchr per-hit: 9.90/12.64 ns
measured vs 7.7 ns assumed; inline per-byte: 0.580/0.835 ns measured vs
0.5 ns assumed) but still cannot independently re-derive the crossover
frequency, and the added keyword point does not fix this** -- it is
STOPPED here per the ruling's own instruction ("if it still can't
separate the byte/hit terms cleanly, show it and stop there, no
forcing"). A genuinely independent crossover estimate needs frequency
points spread much further apart than 2.8%/3.2% (a byte much rarer, one
much commoner) or subject sets whose total BYTE COUNTS differ enough to
break the near-collinearity directly -- neither is available from this
window's three fixed-size, shared-across-patterns throughput subjects.

## Summary of what changed vs I-103/I-103a's literal asks

- Config set: I-103a's wider four/two-config grid, reconciled explicitly
  (deviation 3) -- I-103's own single `(auto, --no-captures)` cell is the
  `auto-nocaps` row throughout.
- Arm (d): built and measured on ALL SIX pattern-config pairs (router's
  four, keyword's two) after the manager's ruling overrode this lane's
  initial STOP on keyword's offset-1 case -- the offset-corrected form is
  quoted in section 3 and answer-checked equal to (a)/(b)/(c) before any
  timing.
- Everything else -- 5 interleaved trials, load gate, answer-check
  before any timing, the O-50/[B81] fallback instrument shape -- follows
  I-98's protocol and I-103/I-103a's text verbatim.

Scratch artifacts (not committed, per the mandate): `/tmp/optloop5/b83/`
(`run_instrument.py`, `run_instrument.log`, `work/`, `answer_check.json`,
`rows_by_variant.json`, `results.json`, `deviations.json`) -- held per the
brief's own instruction until "I-103 logs fetched".
