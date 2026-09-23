#!/usr/bin/env python3
"""
onepass_mb.py -- M-B reducer for [OPT-4.2-ish captures-via-DFA] one-pass DFA
candidate (c), per docs/dev/optloop/captures_via_dfa_survey.md section 3.6.

Reduces the raw arm1 (--features all) / arm2 (--features all --no-captures)
ns/byte lines pcrec-bench's lane b76optloop reported in
docs/dev/lanes/b76optloop_report.md block (C) into the VM-pass "share"
(arm1 - arm2) / arm1 per (pattern, subject) cell, then:
  - a per-pattern median share over that pattern's subjects
  - the population median + IQR of those per-pattern medians
  - a regime split (throughput: t-64k/t-256k/t-1m; match: each pattern's
    own search_short/match subject) since captures_via_dfa_survey.md 3.6's
    own decision rule uses two DIFFERENT thresholds by regime (~10% on
    throughput, ~25% on match, "has a target" over 50% on match)

Units: the bench report's table is already reduced to ns/byte (best wall
time over `iters` repetitions of the find-all loop, divided by subject
size in bytes -- see linux_ask_i89.md 0.4's findall.c). arm1 and arm2 are
timed on the SAME subject (same byte count n), so
  (arm1_ns_per_byte - arm2_ns_per_byte) / arm1_ns_per_byte
is algebraically identical to (arm1_time - arm2_time) / arm1_time -- no
further unit conversion is needed or performed.

Re-run: python3 onepass_mb.py [path-to-b76optloop_report.md]
(default: ../../../../../pcrec-bench/docs/dev/lanes/b76optloop_report.md
relative to this file -- i.e. /home/duxevents/pcrec-bench's committed copy)

This script hardcodes the 17x4 (pattern, subject) -> (arm1, arm2) ns/byte
table because the bench report presents it as a markdown table, not a
machine-readable file; a maintainer re-running this after a new bench
report should paste the new table into RAW_TABLE below. The report path
argument is accepted for provenance/citation purposes and is NOT parsed.
"""
import sys
import statistics

# (pattern, subject, arm1_ns_byte, arm2_ns_byte) -- verbatim from
# pcrec-bench docs/dev/lanes/b76optloop_report.md block (C) table,
# commit efec536 (repo pcrec-bench, path docs/dev/lanes/b76optloop_report.md).
# subject in {"t-64k","t-256k","t-1m","own"}; "own" size varies per pattern
# (each pattern's own search_short/match subject) and is NOT one of the
# three pinned throughput subjects (65536/262144/1048576 bytes).
RAW_TABLE = [
    ("codegrammar-flat",                   "t-64k",  1.0286, 1.0286),
    ("codegrammar-flat",                   "t-256k", 1.0250, 1.0326),
    ("codegrammar-flat",                   "t-1m",   1.0976, 1.0491),
    ("codegrammar-flat",                   "own",    22.8174, 18.5599),

    ("codegrammar-xflag",                  "t-64k",  0.5069, 0.5054),
    ("codegrammar-xflag",                  "t-256k", 0.7657, 0.5059),
    ("codegrammar-xflag",                  "t-1m",   0.5102, 0.5107),
    ("codegrammar-xflag",                  "own",    11.3754, 8.5149),

    # date-nested-plus: own-subject MISSING per the ask (empty SID);
    # not run, not synthesized. Only the three throughput subjects exist.
    ("date-nested-plus",                   "t-64k",  0.0005, 0.0006),
    ("date-nested-plus",                   "t-256k", 0.0001, 0.0001),
    ("date-nested-plus",                   "t-1m",   0.0000, 0.0000),

    ("email-nested-plus",                  "t-64k",  0.0206, 0.0206),
    ("email-nested-plus",                  "t-256k", 0.0202, 0.0201),
    ("email-nested-plus",                  "t-1m",   0.0202, 0.0203),
    ("email-nested-plus",                  "own",    10.3998, 7.0819),

    ("logparse-atomic",                    "t-64k",  0.0014, 0.0014),
    ("logparse-atomic",                    "t-256k", 0.0003, 0.0003),
    ("logparse-atomic",                    "t-1m",   0.0001, 0.0001),
    ("logparse-atomic",                    "own",    7.7360, 7.0901),

    ("logparse-atomic-removed",            "t-64k",  0.0014, 0.0012),
    ("logparse-atomic-removed",            "t-256k", 0.0003, 0.0003),
    ("logparse-atomic-removed",            "t-1m",   0.0001, 0.0001),
    ("logparse-atomic-removed",            "own",    7.4055, 4.1910),

    ("numeric-id-nested-plus",             "t-64k",  0.0005, 0.0005),
    ("numeric-id-nested-plus",             "t-256k", 0.0001, 0.0001),
    ("numeric-id-nested-plus",             "t-1m",   0.0000, 0.0000),
    ("numeric-id-nested-plus",             "own",    11.9209, 5.9605),

    ("phone-list-nested-plus",             "t-64k",  0.0006, 0.0006),
    ("phone-list-nested-plus",             "t-256k", 0.0002, 0.0001),
    ("phone-list-nested-plus",             "t-1m",   0.0000, 0.0000),
    ("phone-list-nested-plus",             "own",    13.9698, 7.9162),

    ("wild-datetime-moment-iso8601",       "t-64k",  0.0014, 0.0012),
    ("wild-datetime-moment-iso8601",       "t-256k", 0.0003, 0.0003),
    ("wild-datetime-moment-iso8601",       "t-1m",   0.0001, 0.0001),
    ("wild-datetime-moment-iso8601",       "own",    14.4821, 5.4948),

    ("wild-logparse-syslogbase-expanded",  "t-64k",  3.4491, 3.4181),
    ("wild-logparse-syslogbase-expanded",  "t-256k", 3.4343, 3.4396),
    ("wild-logparse-syslogbase-expanded",  "t-1m",   3.4434, 2.9917),
    ("wild-logparse-syslogbase-expanded",  "own",    9.9951, 8.0327),

    ("wild-secrets-aws-access-key-id",     "t-64k",  3.5437, 3.4917),
    ("wild-secrets-aws-access-key-id",     "t-256k", 3.6009, 3.5376),
    ("wild-secrets-aws-access-key-id",     "t-1m",   3.6277, 3.1684),
    ("wild-secrets-aws-access-key-id",     "own",    5.4948, 3.9814),

    ("wild-secrets-github-pat",            "t-64k",  0.0949, 0.0937),
    ("wild-secrets-github-pat",            "t-256k", 0.1076, 0.1071),
    ("wild-secrets-github-pat",            "t-1m",   0.1229, 0.1231),
    ("wild-secrets-github-pat",            "own",    6.5543, 5.0522),

    ("wild-secrets-slack-webhook-url",     "t-64k",  0.5562, 0.5649),
    ("wild-secrets-slack-webhook-url",     "t-256k", 0.2432, 0.6081),
    ("wild-secrets-slack-webhook-url",     "t-1m",   0.6096, 0.6107),
    ("wild-secrets-slack-webhook-url",     "own",    12.8373, 10.2445),

    ("wild-secrets-username-password-pair","t-64k",  0.0455, 0.0452),
    ("wild-secrets-username-password-pair","t-256k", 0.0446, 0.0447),
    ("wild-secrets-username-password-pair","t-1m",   0.0444, 0.0443),
    ("wild-secrets-username-password-pair","own",    22.1119, 13.6312),

    ("wild-semdiv-empty-alt-repeat-pcre2", "t-64k",  5.6754, 3.3223),
    ("wild-semdiv-empty-alt-repeat-pcre2", "t-256k", 5.8027, 6.9923),
    ("wild-semdiv-empty-alt-repeat-pcre2", "t-1m",   4.9599, 2.8353),
    ("wild-semdiv-empty-alt-repeat-pcre2", "own",    27.2624, 13.6312),

    ("wild-validator-ipv4-owasp",          "t-64k",  0.0014, 0.0014),
    ("wild-validator-ipv4-owasp",          "t-256k", 0.0003, 0.0003),
    ("wild-validator-ipv4-owasp",          "t-1m",   0.0001, 0.0001),
    ("wild-validator-ipv4-owasp",          "own",    26.3310, 9.0592),

    ("wild-validator-us-zip-owasp",        "t-64k",  0.0006, 0.0005),
    ("wild-validator-us-zip-owasp",        "t-256k", 0.0002, 0.0001),
    ("wild-validator-us-zip-owasp",        "t-1m",   0.0000, 0.0000),
    ("wild-validator-us-zip-owasp",        "own",    11.9209, 7.9162),
]

THROUGHPUT_SUBJECTS = {"t-64k", "t-256k", "t-1m"}
THROUGHPUT_THRESHOLD = 0.10   # ~10%, captures_via_dfa_survey.md 3.6
MATCH_THRESHOLD_LOW = 0.25    # ~25%
MATCH_THRESHOLD_HIGH = 0.50   # "over half" -> has a target


def share(arm1, arm2):
    """(arm1-arm2)/arm1, or None if arm1 rounds to 0.0000 (no resolvable
    signal at the report's 4-decimal precision -- 0/0 is not a share)."""
    if arm1 == 0.0:
        return None
    return (arm1 - arm2) / arm1


def iqr(vals):
    if len(vals) < 2:
        return (vals[0], vals[0]) if vals else (None, None)
    q = statistics.quantiles(vals, n=4, method="inclusive")
    return (q[0], q[2])


def write_tsv(path, rows, per_pattern_median, pop_median, pop_q1, pop_q3,
              throughput_vals, t_median, t_q1, t_q3,
              match_vals, m_median, m_q1, m_q3):
    """One flat TSV, `kind` column distinguishes row shape (kept flat
    rather than split across files so a consumer greps one place)."""
    with open(path, "w") as f:
        f.write("kind\tpattern\tsubject\targ1_ns_byte\targ2_ns_byte\tshare\n")
        for pat, subj, a1, a2, s in rows:
            sstr = f"{s:.4f}" if s is not None else "NA"
            f.write(f"cell\t{pat}\t{subj}\t{a1}\t{a2}\t{sstr}\n")
        for pat in sorted(per_pattern_median):
            m = per_pattern_median[pat]
            mstr = f"{m:.4f}" if m is not None else "NA"
            f.write(f"pattern_median\t{pat}\t-\t-\t-\t{mstr}\n")
        for pat, v in throughput_vals:
            f.write(f"pattern_throughput_median\t{pat}\t-\t-\t-\t{v:.4f}\n")
        for pat, v in match_vals:
            f.write(f"pattern_match_share\t{pat}\townsubj\t-\t-\t{v:.4f}\n")
        f.write(f"population\tpooled_pattern_median\t-\t-\t-\t{pop_median:.4f}\n")
        f.write(f"population\tpooled_pattern_median_q1\t-\t-\t-\t{pop_q1:.4f}\n")
        f.write(f"population\tpooled_pattern_median_q3\t-\t-\t-\t{pop_q3:.4f}\n")
        f.write(f"population\tthroughput_regime_median\t-\t-\t-\t{t_median:.4f}\n")
        f.write(f"population\tthroughput_regime_q1\t-\t-\t-\t{t_q1:.4f}\n")
        f.write(f"population\tthroughput_regime_q3\t-\t-\t-\t{t_q3:.4f}\n")
        f.write(f"population\tmatch_regime_median\t-\t-\t-\t{m_median:.4f}\n")
        f.write(f"population\tmatch_regime_q1\t-\t-\t-\t{m_q1:.4f}\n")
        f.write(f"population\tmatch_regime_q3\t-\t-\t-\t{m_q3:.4f}\n")


def main():
    rows = []
    for pat, subj, a1, a2 in RAW_TABLE:
        s = share(a1, a2)
        rows.append((pat, subj, a1, a2, s))

    # Per-pattern median share over ALL its measured subjects (brief's
    # literal ask), resolvable cells only.
    by_pat = {}
    for pat, subj, a1, a2, s in rows:
        by_pat.setdefault(pat, []).append((subj, a1, a2, s))

    per_pattern_median = {}
    for pat, entries in by_pat.items():
        resolvable = [s for _, _, _, s in entries if s is not None]
        per_pattern_median[pat] = statistics.median(resolvable) if resolvable else None

    print("== per (pattern, subject) share ==")
    print("pattern\tsubject\targ1_ns_byte\targ2_ns_byte\tshare")
    for pat, subj, a1, a2, s in rows:
        sstr = f"{s:.4f}" if s is not None else "NA"
        print(f"{pat}\t{subj}\t{a1}\t{a2}\t{sstr}")

    print()
    print("== per-pattern median share (brief's literal ask; all subjects pooled) ==")
    for pat in sorted(per_pattern_median):
        m = per_pattern_median[pat]
        print(f"{pat}\t{m:.4f}" if m is not None else f"{pat}\tNA")

    pooled = [m for m in per_pattern_median.values() if m is not None]
    pop_median = statistics.median(pooled)
    pop_q1, pop_q3 = iqr(sorted(pooled))
    above = sum(1 for m in pooled if m >= THROUGHPUT_THRESHOLD)
    below = sum(1 for m in pooled if m < THROUGHPUT_THRESHOLD)
    print()
    print(f"population median (pooled per-pattern median share): {pop_median:.4f} ({pop_median*100:.2f}%)")
    print(f"population IQR: [{pop_q1:.4f}, {pop_q3:.4f}] ([{pop_q1*100:.2f}%, {pop_q3*100:.2f}%])")
    print(f"n patterns with a resolvable median: {len(pooled)} of {len(by_pat)}")
    print(f"count >= {THROUGHPUT_THRESHOLD*100:.0f}% threshold: {above}")
    print(f"count < {THROUGHPUT_THRESHOLD*100:.0f}% threshold: {below}")

    # Regime split: this is what 3.6's own decision rule actually tests --
    # throughput share (median over each pattern's 3 throughput cells,
    # pooled) vs match share (each pattern's own-subject cell).
    print()
    print("== regime split (the survey's own two-threshold rule) ==")
    throughput_vals = []
    for pat, entries in by_pat.items():
        tvals = [s for subj, _, _, s in entries if subj in THROUGHPUT_SUBJECTS and s is not None]
        if tvals:
            pat_t_median = statistics.median(tvals)
            throughput_vals.append((pat, pat_t_median))
    match_vals = []
    for pat, entries in by_pat.items():
        for subj, _, _, s in entries:
            if subj == "own" and s is not None:
                match_vals.append((pat, s))

    t_pooled = sorted(v for _, v in throughput_vals)
    m_pooled = sorted(v for _, v in match_vals)
    t_median = statistics.median(t_pooled)
    m_median = statistics.median(m_pooled)
    t_q1, t_q3 = iqr(t_pooled)
    m_q1, m_q3 = iqr(m_pooled)

    print(f"throughput regime: n={len(t_pooled)} patterns, median={t_median:.4f} ({t_median*100:.2f}%), "
          f"IQR=[{t_q1*100:.2f}%, {t_q3*100:.2f}%]")
    print(f"  per-pattern throughput median: {sorted(throughput_vals, key=lambda x: x[1])}")
    print(f"match regime (own subject): n={len(m_pooled)} patterns, median={m_median:.4f} ({m_median*100:.2f}%), "
          f"IQR=[{m_q1*100:.2f}%, {m_q3*100:.2f}%]")
    print(f"  per-pattern match share: {sorted(match_vals, key=lambda x: x[1])}")

    over_half_match = sum(1 for _, v in match_vals if v > MATCH_THRESHOLD_HIGH)
    print(f"patterns with match-regime share > 50%: {over_half_match} of {len(m_pooled)}")

    print()
    print("== verdict inputs ==")
    print(f"throughput median {t_median*100:.2f}% vs ~10% kill threshold: "
          f"{'ABOVE (fails the not-the-cost test)' if t_median >= THROUGHPUT_THRESHOLD else 'below (not-the-cost by throughput)'}")
    print(f"match median {m_median*100:.2f}% vs ~25% kill threshold: "
          f"{'ABOVE (fails the not-the-cost test)' if m_median >= MATCH_THRESHOLD_LOW else 'below (not-the-cost by match)'}")
    print(f"match median {m_median*100:.2f}% vs 50% 'has a target' threshold: "
          f"{'ABOVE (has a target)' if m_median > MATCH_THRESHOLD_HIGH else 'at or below (no clean target by this test alone)'}")

    import os
    tsv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "onepass_mb.tsv")
    write_tsv(tsv_path, rows, per_pattern_median, pop_median, pop_q1, pop_q3,
              throughput_vals, t_median, t_q1, t_q3,
              match_vals, m_median, m_q1, m_q3)
    print()
    print(f"wrote {tsv_path}")


if __name__ == "__main__":
    main()
