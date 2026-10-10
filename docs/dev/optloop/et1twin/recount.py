#!/usr/bin/env python3
"""docs/dev/optloop/et1twin/recount.py -- Step A: the K12 population
re-counted at current main under D151's gates, by walk_survey's own method.

    recount.py k12_cells_now.tsv

Input: studies/walk_survey/analyze.py's cells_bench.tsv restricted to the
default config's K12 cells (G_K12 > 0), produced by re-running the walk
survey's instrument (wsdrv5.c, m_gap) over the K12 patterns at this lane's
pin. The estimate is the survey's: est_ns_K12 = bench median x m_gap / T
(bench_times.tsv, the survey's own weights), excluding cells K1 owns.

GATES is the per-pattern hand reading of where_to_start.md §2.4 against
each pattern's text (the inner-landmark split fact does not exist yet, so
no compiler output can be read for it). Columns: route gate (DFA route,
start-unanchored, today's start form not already exact), G1, G2 as the
formula states it (fixed_width(P) or not bytes(L) <= alphabet(P)), and the
factor-free refinement this lane proposes (no string of P contains L, and
L is border-free), each with the P / L split it was read on."""
import sys

# pid: (split P | L, route, G1, G2 formula, G2 factor-free, verdict, note)
GATES = {
    "loglines/ipv6": ("[0-9a-f]{1,4} | ':' (head of both branches)", "dfa", "y", "y", "y", "SURVIVES",
                      "':' not in [0-9a-f]; the split reads through the top-level alternation's common head"),
    "altwide/sfx-64": ("64 stems | 'ing' (S empty)", "dfa", "y", "n", "y", "REFINED-ONLY",
                       "stems span a-z (i,n,g in alphabet(P)), widths 3-9; no stem contains 'ing', 'ing' border-free"),
    "altwide/sfx-256": ("256 stems | 'ing'", "dfa", "y", "n", "y", "REFINED-ONLY", "as sfx-64"),
    "altwide/sfx-512": ("512 stems | 'ing'", "dfa", "y", "n", "y", "REFINED-ONLY", "as sfx-64"),
    "syntax/cls-s-uc": ("\\S+ | '@'", "dfa", "y", "n", "n", "FAILS-G2", "'@' is in \\S; P contains '@' as a factor"),
    "email/orig": ("local part | '@'", "dfa", "y", "n", "n", "FAILS-G2",
                   "the quoted local part's class \\x23-\\x5b holds '@': genuinely ambiguous split"),
    "email/factored": ("local part | '@'", "dfa", "y", "n", "n", "FAILS-G2", "as email/orig"),
    "capability/wild-logparse-syslogbase-expanded": ("timestamp prefix | ':'", "vm", "n", "y", "y", "OFF-ROUTE",
                   "VM hybrid (captures; size-cap retry); P holds (?!<[0-9]) lookahead: stage 2 at most"),
    "capability/wild-logparse-winpath-grok": ("(?>...) | '\\\\'", "vm", "n", "-", "-", "OFF-ROUTE", "atomic group in P; VM"),
    "loglines/kv-quoted": ("\\b[a-z_][a-z0-9_]{0,31} | '=\"'", "dfa", "y", "y", "y", "SURVIVES",
                           "'=' not in alphabet(P); today: K82 handoff at c-32 already"),
    "bounded/csv5": ("[^,\\n]{0,32} | ','", "dfa", "y", "y", "y", "SURVIVES", "search_short only"),
    "loglines/uuid": ("\\b[0-9a-f]{8} | '-'", "dfa", "y", "y", "y", "SURVIVES",
                      "fixed width 8; today end-minus-width (start exact, K3)"),
    "capability/wild-validator-uuid-grok": ("[A-Fa-f0-9]{8} | '-'", "dfa", "y", "y", "y", "SURVIVES", "as loglines/uuid"),
}
ANCHORED = "start-anchored (^ / one attempt): the tactic declines (where_to_start.md §2.5)"
for p in ("capability/email-nested-plus", "capability/uuid-near-miss", "capability/wild-datetime-moment-iso8601",
          "capability/wild-validator-email-owasp", "capability/winpath-near-miss", "sentinel/uuid-near-miss",
          "sentinel/wild-validator-email-owasp", "sentinel/winpath-near-miss"):
    GATES[p] = ("-", "-", "-", "-", "-", "ANCHORED", ANCHORED)

rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1])]
h = {k: i for i, k in enumerate(rows[0])}
tot, per = {}, {}
for r in rows[1:]:
    pid = r[h["pid"]]
    if float(r[h["est_ns_K1"]] or 0) > 0:
        continue
    est = float(r[h["est_ns_K12"]] or 0)
    v = GATES.get(pid, ("?",) * 6 + ("unclassified",))[5]
    tot[v] = tot.get(v, 0) + est
    per.setdefault(pid, []).append((r[h["regime"]], r[h["DFA_START"]], r[h["REQ_HANDOFF"]], est))
print("| pattern | split P · L | G1 | G2 (formula) | G2 (factor-free) | today (DFA_START, handoff) | cells: regime est ms | verdict | note |")
print("|---|---|---|---|---|---|---|---|---|")
for pid in sorted(per, key=lambda p: -sum(c[3] for c in per[p])):
    g = GATES.get(pid, ("?",) * 6 + ("unclassified",))
    cells = per[pid]
    today = "%s, %s" % (cells[0][1], cells[0][2])
    cs = "; ".join("%s %.4f" % (c[0], c[3] / 1e6) for c in cells)
    print("| `%s` | %s | %s | %s | %s | %s | %s | **%s** | %s |" % (pid, g[0].replace(" | ", " · "), g[2], g[3], g[4], today, cs, g[5], g[6]))
print()
grand = sum(tot.values())
print("| verdict | est ms (walk_survey weights) |")
print("|---|---|")
for v in sorted(tot, key=lambda v: -tot[v]):
    print("| %s | %.3f |" % (v, tot[v] / 1e6))
print("| **all K12 cells (cf. walk_survey 15.8)** | **%.3f** |" % (grand / 1e6))
