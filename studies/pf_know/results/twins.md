# [PF-KNOW] hand twins — 2026-09-30, Mac M1 (darwin), `twin.py`, gcc-16 -O2

DIRECTIONAL ONLY: darwin, load average 3.6-6.3 during the runs (other
lanes' harness runs were live on the box), 7 alternating trials each, the
median reported, spreads shown. Every twin was ANSWER-IDENTICAL to its base
artifact over the subject (every span of every match hashed) before any
clock was read. `ratio` = base ns/byte over twin ns/byte (>1 = twin faster).

## Sparse regime — the bench-shaped subjects (one match per ~12 KB)

| id | twin | subject | matches | base ns/B | twin ns/B | ratio | spreads (base / twin) |
|---|---|---|---:|---:|---:|---:|---|
| sec-github-pat `\b(github_pat_[0-9a-zA-Z_]{82})\b` | detall (VM never entered) | secrets.bin (capability t-1m + one token per 4 KB) | 86 | 0.2650 | 0.2643 | 1.003 | 0.2609..0.2682 / 0.2614..0.2647 |
| sec-slack-webhook `(?i)https://hooks.slack.com/services/(T[a-z0-9_]{8}/B[a-z0-9_]{8,12}/[a-z0-9_]{24})` | prefix 44 (44 caseless byte tests + the `{8}` loop skipped) | secrets.bin | 85 | 0.7502 | 0.7496 | 1.001 | 0.7384..0.7646 / 0.7292..0.7709 |
| syn-sshd-pid `sshd\[(\d+)\]: ` | prefix 5 (one 5-byte memcmp skipped) | loglines t-1024k-hit | 150 | 0.1132 | 0.1132 | 1.000 | 0.1122..0.1141 / 0.1121..0.1145 |

## Dense regime — match-dense synthetics (one match per 100-200 bytes)

| id | twin | subject | matches | base ns/B | twin ns/B | ratio | spreads (base / twin) |
|---|---|---|---:|---:|---:|---:|---|
| dense-github-pat | detall | secrets_dense.bin (402 KB, 6,000 tokens, `" x "` between) | 2,000 | 2.0330 | 1.8044 | **1.127** | 2.0143..2.0641 / 1.7955..1.8268 |
| dense-slack-webhook | prefix 44 | secrets_dense.bin | 2,000 | 2.1515 | 2.0608 | **1.044** | 2.1307..2.1767 / 2.0127..2.0926 |
| dense-sshd-pid | prefix 5 | sshd_dense.bin (1.28 MB, 60,000 lines `sshd[N]: word`) | 60,000 | 3.0924 | 3.0633 | 1.009 | 3.0213..3.1342 / 2.9937..3.1076 |

The matching gcov cells (`dyn.py`, executed test LINES, same subjects):

| id | attempts | VM lead | VM mid | VM trail | DFA | search | lead/VM | VM/all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| dense-github-pat | 2,000 | 6,000 | 168,000 | 4,000 | 1,333,996 | 14,002 | 3.4% (instrument lower bound; segprobe says det_all = 100%) | 11.7% |
| dense-slack-webhook | 2,000 | 64,000 | 106,000 | 0 | 1,150,000 | 20,002 | 37.6% | 12.7% |
| dense-sshd-pid | 60,000 | 60,000 | 473,330 | 60,000 | 6,253,312 | 360,002 | 10.1% | 8.2% |

Reading: the whole-VM twin (det_all) reaches x1.13 where matches are dense,
which is close to its VM/all test share (11.7%) — the VM's share of executed
tests is a fair proxy for its share of time on these cells. The prefix twin
reaches x1.04 where the prefix is 44 single-byte caseless tests and x1.01
where it is one `memcmp`. In the sparse regime every twin is at the noise
floor: the DFA prefilter's scan over the subject is the whole cost.
