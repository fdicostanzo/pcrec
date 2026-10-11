"""[OPT-GAPREPORT] third-instance sections, computed from gap_rows.json / rank.json.

  best_peer_census(rows)      lead/level/trail per set against the BEST comparator
                              of each cell, not only pcre2-jit
  simd_attributable(rows, rk) cells whose only trailing comparators are SIMD-role,
                              plus the SCAN-SIMD / WIDE-ALT groups
  movement(old_rows, rows, old_rk, rk)
                              per-cell and per-group movement against an earlier
                              instance's gap_rows.json / rank.json

Every threshold is gapconfig's (roles, tiers); MOVE_BAND below is the one
movement criterion, stated here because it is only meaningful between two
instances: a trailing cell whose ratio vs jit changed by less than that factor
is UNCHANGED (the cross-window null band of the loosest scored tier, B).
"""
import collections

import gapconfig as cfg

MOVE_BAND = 1.15
SIMD_GROUPS = ("SCAN-SIMD", "WIDE-ALT")
ROLE = {t: r for t, _c, r, _f in cfg.COMPARATORS}


def _key(r):
    return (r["sb"], r["pattern"], r["regime"], r["form"])


def _verdicts(r, roles):
    return [c["verdict"] for t, c in r["cmp"].items() if ROLE.get(t) in roles]


def best_peer_census(rows):
    """Lead / level / trail per set vs jit, vs the best scalar-or-jit comparator,
    and vs the best non-excluded comparator (adds the SIMD-role rust)."""
    views = [("jit", ("peer",)),
             ("best non-SIMD (jit + scalar engines)", ("peer", "scalar")),
             ("best incl. rust (SIMD prefilters)", ("peer", "scalar", "simd"))]
    out = []
    for name, roles in views:
        cnt = collections.defaultdict(collections.Counter)
        for r in rows:
            if "libpcre2:jit-caps" not in r["cmp"]:
                continue
            v = _verdicts(r, roles)
            k = ("trail" if "behind" in v else
                 "lead" if all(x == "ahead" for x in v) else "level")
            cnt[r["sb"]][k] += 1
        out.append((name, cnt))
    return out


def simd_cells(rows):
    """Trailing cells where no jit and no scalar comparator is behind, but a
    SIMD-role one is: only vectorised engines lead."""
    res = []
    for r in rows:
        beh = {t for t, c in r["cmp"].items() if c["verdict"] == "behind" and c["tier"] != "C"}
        if beh and all(ROLE.get(t) == "simd" for t in beh):
            res.append((r, max(r["cmp"][t]["ratio"] for t in beh)))
    return res


def _worst(entries):
    sc = [e for e in entries if e["tier"] != "C"]
    return max((e["ratio"] for e in sc), default=0.0)


def movement(old, new, old_rk, rk, causes_map, merge):
    """Lines (markdown) comparing two instances."""
    common = {r["sb"] for r in old} & {r["sb"] for r in new}
    O = {_key(r): r for r in old if r["sb"] in common}
    N = {_key(r): r for r in new if r["sb"] in common}
    nn = {(k[0], k[1], k[2]): (O[k]["n"], N[k]["n"]) for k in set(O) & set(N)}
    J = cfg.PEER
    cls = collections.defaultdict(list)          # state -> [(key, oldratio, newratio)]
    for k in sorted(set(O) & set(N)):
        a, b = O[k]["cmp"].get(J), N[k]["cmp"].get(J)
        if not a or not b or a["tier"] == "C" or b["tier"] == "C":
            continue
        ab, bb = a["verdict"] == "behind", b["verdict"] == "behind"
        if O[k]["n"] != N[k]["n"]:
            # the subject set changed between the instances (e.g. capability
            # 0.1 -> 0.2 went from 3 to 11 throughput subjects): the two
            # ratios are over different bytes, so no movement is claimed
            if ab or bb:
                cls["SUBJECTS-CHANGED"].append((k, a["ratio"], b["ratio"]))
            continue
        if ab and not bb:
            st = "CLOSED"
        elif bb and not ab:
            st = "NEW"
        elif ab and bb:
            f = b["ratio"] / a["ratio"]
            st = "SHRANK" if f < 1 / MOVE_BAND else "GREW" if f > MOVE_BAND else "UNCHANGED"
        else:
            continue
        cls[st].append((k, a["ratio"], b["ratio"]))
    L = []
    w = L.append
    both = len(set(O) & set(N))
    w(f"Cells present in both instances: {both} (vs-jit tier A/B only below, same subject count n only; "
      f"a trailing cell moved if its ratio changed by more than x{MOVE_BAND}).\n")
    w("| state | cells |")
    w("|---|---|")
    for st in ("CLOSED", "SHRANK", "UNCHANGED", "GREW", "NEW", "SUBJECTS-CHANGED"):
        w(f"| {st} | {len(cls[st])} |")
    w("")
    gone = sorted(set(O) - set(N))
    came = sorted(set(N) - set(O))
    w(f"Cells only in the earlier instance: {len(gone)}; only in this one: {len(came)} "
      f"(set/version changes, e.g. capability 0.1 -> 0.2, altwide not re-run).\n")

    def grp(rk_):
        g = {}
        for name, G in rk_["groups"].items():
            t = next((m for k, m in merge if k == name), name)
            T = g.setdefault(t, {"peer": [], "ceiling": [], "cells": set()})
            # only cells of the compared sets whose subject count n is unchanged
            keep = lambda e: (e["set"] in common and
                              len(set(nn.get((e["set"], e["pattern"], e["regime"]), (1, 1)))) == 1)
            T["peer"] += [e for e in G["peer"] if keep(e)]
            T["ceiling"] += [e for e in G["ceiling"] if keep(e)]
            T["cells"] |= {(e["set"], e["pattern"], e["regime"]) for e in T["peer"] + T["ceiling"]}
        return g
    og, ng = grp(old_rk), grp(rk)
    w("### By cause group\n")
    w("Cells of the compared sets with an unchanged subject count only (a cell absent from the "
      "earlier instance counts as unchanged).\n")
    w("| group | breadth old -> new | worst vs jit old -> new | worst vs ceiling old -> new |")
    w("|---|---|---|---|")
    for g in sorted(set(og) | set(ng), key=lambda g: -len(ng.get(g, og.get(g))["cells"])):
        a = og.get(g, {"peer": [], "ceiling": [], "cells": set()})
        b = ng.get(g, {"peer": [], "ceiling": [], "cells": set()})
        f = lambda x: ("x%.2f" % x if x else "0")
        w(f"| {g} | {len(a['cells'])} -> {len(b['cells'])} | {f(_worst(a['peer']))} -> {f(_worst(b['peer']))} "
          f"| {f(_worst(a['ceiling']))} -> {f(_worst(b['ceiling']))} |")
    w("")
    for st, title in (("CLOSED", "Closed (trailed jit then, does not now)"),
                      ("SHRANK", "Shrank"), ("GREW", "Grew"), ("NEW", "New (did not trail jit then)"),
                      ("SUBJECTS-CHANGED", "Subject set changed (n differs; ratios over different bytes, "
                       "NOT a movement claim; listed where either side trails)")):
        if not cls[st]:
            continue
        w(f"### {title}\n")
        for k, a, b in sorted(cls[st], key=lambda z: -max(z[1], z[2])):
            w(f"- {k[0]} `{k[1]}` {k[2]}: x{a:.2f} -> x{b:.2f}")
        w("")
    return L
