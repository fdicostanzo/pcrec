#!/usr/bin/env python3
"""gen_report.py -- writes docs/dev/summaries/2026-10-11-prior-cost-inputs.html,
ONE self-contained HTML file (inline SVG, inline CSS/JS, no fetches).

Usage (from the repository root):
    python3 docs/dev/summaries/prior_cost_inputs/gen_report.py

Inputs: data.py (the content, verified against the code), reach_summary.tsv
(reach_probe.py's stamp counts) and src/findings/default.rxt (the shipped
prior, read for the byte rug in chart b). The decision boundaries in chart b
are COMPUTED here with the shipped integer arithmetic replicated exactly
(admit4, model_cost, verify_cost below mirror emit_dfa.c:7786 and
prefix_k.c:96-114).

Palette: the dataviz skill's reference categorical slots 1-3 (blue, orange,
aqua), validated all-pairs in both modes with its validate_palette.py
(light: CVD worst 9.2, normal 24.0, aqua contrast WARN -> every chart has a
table view and direct labels; dark: all PASS).
"""
import html
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data as D  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "..", "2026-10-11-prior-cost-inputs.html")

E = html.escape


def fmt(v):
    if isinstance(v, float) and not v.is_integer():
        return f"{v:g}"
    return f"{int(v):,}"


# ---------------------------------------------------------------- arithmetic
M = 10 ** 6


def admit4(h, m, K):
    """emit_dfa.c:7786 req_landmark_admits, verbatim in integers."""
    if h == 0:
        return True
    if K * h >= M:
        return False
    return (M - K * h) * m > M * h


def hstar(m, K):
    """largest landmark hit rate h (ppm) still admitted, or 0."""
    if not admit4(1, m, K):
        return 0
    lo, hi = 1, M
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if admit4(mid, m, K):
            lo = mid
        else:
            hi = mid - 1
    return lo


def verify_cost(p):
    t = min(p, M - p)
    return 250 + 1500 * t // M


def model_cost(sc, sp, vcost, vr):
    return sc + sp * vcost // M + sp * vr // M * 2000 // M


def adopt7(p, b, v0):
    """prefix_k: one singleton scan offset at rate p, offset 0 verified at
    rate v0, against a bitmap baseline over k0 of mass b; MATERIAL 2/1."""
    base = model_cost(116, b, 0, M)
    new = model_cost(6, p, verify_cost(v0), v0)
    return new < base and new * 2 < base


def pstar(b, v0):
    if not adopt7(2, b, v0):
        return 0
    lo, hi = 2, M
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if adopt7(mid, b, v0):
            lo = mid
        else:
            hi = mid - 1
    return lo


def default_prior():
    rate = {}
    with open(os.path.join(ROOT, "src", "findings", "default.rxt")) as f:
        for line in f:
            m = re.match(r"\s+row ([0-9a-f]{2}) (\d+)\s*$", line)
            if m:
                rate[int(m.group(1), 16)] = int(m.group(2))
    assert len(rate) == 256 and sum(rate.values()) == M, "default.rxt moved"
    return rate


def reach():
    out = []
    with open(os.path.join(HERE, "reach_summary.tsv")) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            name, val, how = line.rstrip("\n").split("\t")
            out.append((name, int(val), how))
    return out


# ---------------------------------------------------------------- svg kit
def lg(v):
    return math.log10(v)


class Log:
    def __init__(self, lo, hi, x0, x1):
        self.lo, self.hi, self.x0, self.x1 = lo, hi, x0, x1

    def __call__(self, v):
        v = max(v, self.lo)
        return self.x0 + (lg(v) - lg(self.lo)) / (lg(self.hi) - lg(self.lo)) * (self.x1 - self.x0)


def tip_attr(text):
    return f' tabindex="0" data-tip="{E(text)}"'


def text(x, y, s, cls="t-sec", anchor="start", size=12, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" '
            f'font-size="{size}"{extra}>{E(s)}</text>')


def decade_label(e):
    v = 10 ** e
    if e < 0:
        return f"{v:g}"
    if v >= 10 ** 6:
        return "10⁶"
    if v >= 1000:
        return f"{v // 1000:,}K"
    return f"{int(v)}"


SHAPES = {"zen1": "circle", "mac": "square", "none": "diamond"}
PROV_VAR = {"measured": "--series-1", "derived": "--series-2", "chosen": "--series-3"}


def mark(shape, x, y, var, tip):
    ring = 'stroke="var(--surface-1)" stroke-width="2"'
    if shape == "circle":
        m = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="var({var})" {ring}/>'
    elif shape == "square":
        m = f'<rect x="{x - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" rx="1.5" fill="var({var})" {ring}/>'
    else:
        m = (f'<path d="M{x:.1f},{y - 6.5:.1f} L{x + 6.5:.1f},{y:.1f} L{x:.1f},{y + 6.5:.1f} '
             f'L{x - 6.5:.1f},{y:.1f} Z" fill="var({var})" {ring}/>')
    return (f'<g class="hit"{tip_attr(tip)}><rect x="{x - 12:.1f}" y="{y - 12:.1f}" width="24" '
            f'height="24" fill="transparent"/>{m}</g>')


# ---------------------------------------------------------------- chart a
def chart_constants():
    facets = []
    for c in D.CONSTANTS:
        unit = c[2]
        for f in facets:
            if f[0] == unit:
                f[1].append(c)
                break
        else:
            facets.append((unit, [c]))
    W, LX, X0, X1 = 900, 16, 300, 860
    row, head, axis = 22, 24, 26
    y = 8
    parts = []
    for unit, cs in facets:
        vals = [c[1] for c in cs]
        e0 = math.floor(lg(min(vals))) if min(vals) > 0 else 0
        e1 = math.ceil(lg(max(vals)))
        if e1 == e0:
            e1 += 1
        if e1 - e0 < 2:
            e0 -= 1 if min(vals) < 3 * 10 ** e0 else 0
            e1 += 1 if max(vals) > 10 ** e1 / 3 else 0
        sc = Log(10 ** e0, 10 ** e1, X0, X1)
        parts.append(text(LX, y + 15, unit, cls="t-pri", size=13, extra=' font-weight="600"'))
        y += head
        top = y
        for c in cs:
            name, val, _u, member, prov, box, prov_text = c
            cy = y + row / 2
            parts.append(f'<line x1="{X0}" x2="{X1}" y1="{cy:.1f}" y2="{cy:.1f}" class="grid"/>')
            parts.append(text(LX + 10, cy + 4, f"{name}  ({member})", size=12))
            x = sc(val)
            tip = (f"{name} = {fmt(val)} {unit}\nmember: {member}\n"
                   f"provenance: {D.PROV_LABEL[prov]}; box: {D.BOX_LABEL[box]}\n{prov_text}")
            parts.append(mark(SHAPES[box], x, cy, PROV_VAR[prov], tip))
            lab = fmt(val)
            if x > X1 - 50:
                parts.append(text(x - 12, cy + 4, lab, cls="t-pri", anchor="end", size=11))
            else:
                parts.append(text(x + 12, cy + 4, lab, cls="t-pri", size=11))
            y += row
        parts.append(f'<line x1="{X0}" x2="{X1}" y1="{y + 2}" y2="{y + 2}" class="axis"/>')
        for e in range(e0, e1 + 1):
            x = sc(10 ** e)
            parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{y + 2}" class="grid"/>')
            parts.append(text(x, y + 16, decade_label(e), cls="t-mut", anchor="middle", size=11))
        y += axis
    H = y + 4
    svg = (f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
           f'aria-label="Every hand-set constant in the family, one row each, faceted by unit, '
           f'log scale per facet">{"".join(parts)}</svg>')
    legend = legend_html(
        [("square-less", "--series-1", "measured"), ("", "--series-2", "derived (part measured, part assumed)"),
         ("", "--series-3", "chosen / no measurement record")],
        [("circle", "Zen 1 (ubuntubudu)"), ("square", "Mac M1"), ("diamond", "no box (chosen, codegen, or not stated)")])
    rows = "".join(
        f"<tr><td>{E(c[0])}</td><td class='num'>{E(fmt(c[1]))}</td><td>{E(c[2])}</td><td>{E(c[3])}</td>"
        f"<td>{E(D.PROV_LABEL[c[4]])}</td><td>{E(D.BOX_LABEL[c[5]])}</td><td>{E(c[6])}</td></tr>"
        for c in D.CONSTANTS)
    table = ("<details><summary>Table view: every constant</summary><table><thead><tr><th>constant</th>"
             "<th>value</th><th>unit</th><th>read by</th><th>provenance</th><th>box</th><th>source</th>"
             f"</tr></thead><tbody>{rows}</tbody></table></details>")
    return legend + svg + table


def legend_html(colors, shapes):
    items = []
    for _s, var, lab in colors:
        items.append(f'<span class="lg"><svg width="14" height="14"><rect x="2" y="2" width="10" '
                     f'height="10" rx="2" fill="var({var})"/></svg>{E(lab)}</span>')
    for shape, lab in shapes:
        g = mark(shape, 7, 7, "--text-secondary", "").replace(' tabindex="0" data-tip=""', "")
        items.append(f'<span class="lg"><svg width="16" height="16" viewBox="0 0 14 14" '
                     f'overflow="visible">{g}</svg>{E(lab)}</span>')
    return f'<div class="legend">{"".join(items)}</div>'


# ---------------------------------------------------------------- chart b
def panel_r4(prior):
    W, X0, X1 = 900, 150, 860
    sc = Log(1, M, X0, X1)
    parts = []
    y = 30
    parts.append(text(16, 18, "#3 R4 adaptive-dense · x = mass of the set the retry scan tests (ppm, log)",
                      cls="t-pri", size=13, extra=' font-weight="600"'))
    rows = [("frameless (gap 16 B)", 16), ("framed (gap 4 B)", 4)]
    for lab, gap in rows:
        y += 44
        flip = M // gap  # dense iff ppm * gap > 10^6, i.e. ppm > 10^6/gap
        xf = sc(flip)
        parts.append(text(16, y + 4, lab, size=12))
        parts.append(f'<line x1="{X0}" x2="{xf:.1f}" y1="{y}" y2="{y}" class="track"/>')
        parts.append(f'<line x1="{xf:.1f}" x2="{X1}" y1="{y}" y2="{y}" stroke="var(--series-1)" '
                     f'stroke-width="6" stroke-linecap="round"/>')
        parts.append(f'<g class="hit"{tip_attr(f"{lab}: dense iff mass × {gap} > 10^6, i.e. mass > {flip:,} ppm (mean gap < {gap} bytes). Left: starts in probation (adaptive). Right: starts armed (adaptive-dense).")}>'
                     f'<rect x="{X0}" y="{y - 10}" width="{X1 - X0}" height="20" fill="transparent"/></g>')
        parts.append(f'<line x1="{xf:.1f}" x2="{xf:.1f}" y1="{y - 9}" y2="{y + 9}" class="flip"/>')
        parts.append(text(xf - 6, y - 11, f"flips at {flip:,} ppm", cls="t-pri", anchor="end", size=11))
    parts.append(text(X1, y + 22, "thick = starts armed ('adaptive-dense'); thin = starts in probation ('adaptive')",
                      cls="t-mut", anchor="end", size=11))
    # rug: the shipped default prior (single-byte scans)
    y += 54
    parts.append(text(16, y + 4, "default prior, one byte", size=12))
    named = {0x20: "space", 0x65: "e", 0x30: "0-9", 0x3a: ":", 0x40: "@", 0x7a: "z"}
    for b, r in sorted(prior.items(), key=lambda kv: kv[1]):
        x = sc(r)
        ch = chr(b) if 0x21 <= b < 0x7f else f"0x{b:02x}"
        dense = ("frameless+framed" if r * 4 > M else "frameless only" if r * 16 > M else "neither")
        parts.append(f'<g class="hit"{tip_attr(f"byte {ch}: {r:,} ppm in the default prior; dense on {dense}")}>'
                     f'<rect x="{x - 3:.1f}" y="{y - 10}" width="6" height="20" fill="transparent"/>'
                     f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y - 7}" y2="{y + 7}" class="rug"/></g>')
    labels = [(prior[0x20], "space", -12), (prior[0x65], "e", 20), (prior[0x30], "each digit", -12),
              (prior[0x40], "@", 20), (2, "floor: 158 bytes at 2", -12)]
    for r, lab, dy in labels:
        parts.append(text(sc(r), y + dy, lab, cls="t-sec", anchor="middle", size=11))
    # NONE: cardinality
    y += 46
    parts.append(text(16, y + 4, "no prior (NONE)", size=12))
    for k, lab, dy in [(1, "1 byte", -12), (17, "17 bytes", 20), (64, "64 bytes", -12), (65, "65 bytes", 20)]:
        r = k * M // 256
        x = sc(r)
        parts.append(f'<g class="hit"{tip_attr(f"NONE: a {k}-byte set reads floor({k}·10^6/256) = {r:,} ppm")}>'
                     f'<rect x="{x - 4:.1f}" y="{y - 10}" width="8" height="20" fill="transparent"/>'
                     f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{y - 7}" y2="{y + 7}" class="rug"/></g>')
        parts.append(text(x, y + dy, lab, cls="t-sec", anchor="middle", size=11))
    y += 30
    parts += axis_x(sc, 0, 6, y, 64, "ppm")
    H = y + 34
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="R4 decision by scanned-set mass">{"".join(parts)}</svg>'


def axis_x(sc, e0, e1, y, ytop, unit):
    parts = [f'<line x1="{sc.x0}" x2="{sc.x1}" y1="{y}" y2="{y}" class="axis"/>']
    for e in range(e0, e1 + 1):
        x = sc(10 ** e)
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{ytop}" y2="{y}" class="grid"/>')
        parts.append(text(x, y + 15, decade_label(e), cls="t-mut", anchor="middle", size=11))
    parts.append(text(sc.x1, y + 30, unit, cls="t-mut", anchor="end", size=11))
    return parts


def line_panel(title, xlab, ylab, series, xlo, xhi, ylo, yhi, note, aria, tipfmt):
    """series: [(label, var, [(x, y), ...])]; y may be 0 (= no admission)."""
    W, X0, X1, Y0, Y1 = 900, 80, 800, 64, 320
    sx = Log(xlo, xhi, X0, X1)
    syl = Log(ylo, yhi, 0, 1)

    def sy(v):
        return Y1 - syl(v) * (Y1 - Y0)
    parts = [text(16, 18, title, cls="t-pri", size=13, extra=' font-weight="600"')]
    for e in range(round(lg(ylo)), round(lg(yhi)) + 1):
        yy = sy(10 ** e)
        parts.append(f'<line x1="{X0}" x2="{X1}" y1="{yy:.1f}" y2="{yy:.1f}" class="grid"/>')
        parts.append(text(X0 - 6, yy + 4, decade_label(e), cls="t-mut", anchor="end", size=11))
    parts.append(text(16, Y0 - 22, ylab, cls="t-mut", size=11))
    parts += axis_x(sx, round(lg(xlo)), round(lg(xhi)), Y1, Y0, xlab)
    for lab, var, pts in series:
        good = [(x, y) for x, y in pts if y > 0]
        d = " ".join(f"{'M' if i == 0 else 'L'}{sx(x):.1f},{sy(y):.1f}" for i, (x, y) in enumerate(good))
        parts.append(f'<path d="{d}" fill="none" stroke="var({var})" stroke-width="2" '
                     f'stroke-linejoin="round" stroke-linecap="round"/>')
    # direct end labels, spread so they never overlap
    ends = sorted(((sy([p for p in pts if p[1] > 0][-1][1]), lab, var) for lab, var, pts in series))
    last = -1e9
    for yy, lab, var in ends:
        yy = max(yy, last + 15)
        last = yy
        parts.append(f'<line x1="{X1 + 4}" x2="{X1 + 16}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="var({var})" stroke-width="2"/>')
        parts.append(text(X1 + 20, yy + 4, lab, cls="t-pri", size=11))
    # crosshair hit columns
    xs = [x for x, _ in series[0][2]]
    for i, x in enumerate(xs):
        xl = sx(xs[i - 1]) if i else sx(x)
        xr = sx(xs[i + 1]) if i + 1 < len(xs) else sx(x)
        a, b = (sx(x) + xl) / 2 if i else X0, (sx(x) + xr) / 2 if i + 1 < len(xs) else X1
        lines = [tipfmt(x)] + [f"{lab}: {fmtpt(s[2][i][1])}" for s in series for lab in [s[0]]]
        parts.append(f'<g class="hit col" data-x="{sx(x):.1f}"{tip_attr(chr(10).join(lines))}>'
                     f'<rect x="{a:.1f}" y="{Y0}" width="{max(b - a, 1):.1f}" height="{Y1 - Y0}" fill="transparent"/>'
                     f'<line class="xhair" x1="{sx(x):.1f}" x2="{sx(x):.1f}" y1="{Y0}" y2="{Y1}"/></g>')
    parts.append(text(X0, Y1 + 46, note, cls="t-mut", size=11))
    H = Y1 + 56
    return f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{E(aria)}">{"".join(parts)}</svg>'


def fmtpt(v):
    return "never admitted" if v == 0 else f"{v:,} ppm"


def logspace(lo, hi, n):
    return sorted({int(round(10 ** (lg(lo) + (lg(hi) - lg(lo)) * i / (n - 1)))) for i in range(n)})


def chart_boundaries(prior):
    p1 = panel_r4(prior)
    ms = logspace(2, M, 49)
    s4 = [(f"K = {K}", var, [(m, hstar(m, K)) for m in ms])
          for K, var in [(1, "--series-1"), (8, "--series-2"), (64, "--series-3")]]
    p2 = line_panel(
        "#4 handoff K admission · admitted below the curve",
        "m = mass of the displaced start-byte row's set (ppm); 10⁶ = it scans nothing",
        "largest admitted landmark hit rate h (ppm)", s4, 2, M, 1, M,
        "Admit iff 10⁶/h − K > 10⁶/m. No hand-set constant: K is the landmark's structural max offset.",
        "K admission boundary", lambda m: f"displaced row mass m = {m:,} ppm")
    bs = logspace(100, M, 41)
    s7 = [(f"v₀ = {v0:,}", var, [(b, pstar(b, v0)) for b in bs])
          for v0, var in [(M, "--series-1"), (300000, "--series-2"), (30000, "--series-3")]]
    p3 = line_panel(
        "#7 prefix_k adoption · one scan offset + the offset-0 verify (its set's mass v₀), adopted below the curve",
        "b = mass of today's offset-0 filter set k0, |k0| > 1 so the baseline is the bitmap walk (ppm)",
        "largest adopted scan-byte rate p (ppm)", s7, 100, M, 10 ** 3, M,
        "Adopt iff 2·cost(new) < cost(base), costs in hundredths of a cycle per byte (C_MEMCHR, C_BITMAP, C_VERIFY, C_MISPRED, C_ENTER).",
        "prefix_k adoption boundary", lambda b: f"baseline k0 mass b = {b:,} ppm")
    # table view
    rows = ["<tr><th colspan='4'>#3 R4: flip point (dense iff mass × gap &gt; 10⁶)</th></tr>",
            "<tr><td>frameless, gap 16 B</td><td class='num'>62,500 ppm</td><td colspan='2'>under NONE: sets of ≥ 17 bytes</td></tr>",
            "<tr><td>framed, gap 4 B</td><td class='num'>250,000 ppm</td><td colspan='2'>under NONE: sets of ≥ 65 bytes</td></tr>",
            "<tr><th>#4: m (ppm)</th><th>h* at K = 1</th><th>K = 8</th><th>K = 64</th></tr>"]
    for i, m in enumerate(ms):
        if i % 6 == 0 or i == len(ms) - 1:
            rows.append(f"<tr><td class='num'>{m:,}</td>" + "".join(
                f"<td class='num'>{E(fmtpt(s[2][i][1]))}</td>" for s in s4) + "</tr>")
    rows.append("<tr><th>#7: b (ppm)</th><th>p* at v₀ = 10⁶</th><th>v₀ = 300,000</th><th>v₀ = 30,000</th></tr>")
    for i, b in enumerate(bs):
        if i % 5 == 0 or i == len(bs) - 1:
            rows.append(f"<tr><td class='num'>{b:,}</td>" + "".join(
                f"<td class='num'>{E(fmtpt(s[2][i][1]))}</td>" for s in s7) + "</tr>")
    table = f"<details><summary>Table view: the boundaries</summary><table><tbody>{''.join(rows)}</tbody></table></details>"
    return p1 + p2 + p3 + table


# ---------------------------------------------------------------- chart c
def chart_map():
    cols = D.MAP_COLS
    rowsids = list(D.MAP_ROWS)
    names = {m["id"]: m["name"].split(" (")[0] for m in D.MEMBERS}
    kinds = {m["id"]: m["kind"] for m in D.MEMBERS}
    CW, X0, Y0, RH = 34, 250, 230, 26
    W = X0 + CW * len(cols) + 90
    parts = []
    groups = [("prior", "the byte-rate prior, via"), ("constant", "hand-set constants"),
              ("fact", "structural facts")]
    for g, lab in groups:
        idx = [i for i, c in enumerate(cols) if c[0] == g]
        xa, xb = X0 + CW * idx[0], X0 + CW * (idx[-1] + 1)
        parts.append(f'<line x1="{xa + 2}" x2="{xb - 2}" y1="16" y2="16" class="axis"/>')
        parts.append(text((xa + xb) / 2, 11, lab, cls="t-pri", anchor="middle", size=12,
                          extra=' font-weight="600"'))
    for i, c in enumerate(cols):
        x = X0 + CW * i + CW / 2
        parts.append(f'<text class="t-sec" font-size="11" transform="translate({x + 4:.1f},{Y0 - 8}) rotate(-60)">{E(c[1])}</text>')
        if i and cols[i - 1][0] != c[0]:
            parts.append(f'<line x1="{X0 + CW * i}" x2="{X0 + CW * i}" y1="{Y0 - 4}" y2="{Y0 + RH * len(rowsids)}" class="axis"/>')
    for r, mid in enumerate(rowsids):
        y = Y0 + RH * r
        if r % 2 == 0:
            parts.append(f'<rect x="0" y="{y}" width="{W}" height="{RH}" class="band"/>')
        parts.append(text(8, y + 17, f"{mid} {names[mid]}", size=12))
        parts.append(text(X0 - 8, y + 17, kinds[mid], cls="t-mut", anchor="end", size=10))
        for i, c in enumerate(cols):
            cx, cy = X0 + CW * i + CW / 2, y + RH / 2
            hit = c[1] in D.MAP_ROWS[mid]
            tip = f"{mid} {names[mid]} {'READS' if hit else 'does not read'}: {c[1]} ({c[2]})"
            dot = (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="var(--series-1)"/>' if hit else
                   f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.5" class="dotoff"/>')
            parts.append(f'<g class="hit"{tip_attr(tip)}><rect x="{cx - 12:.1f}" y="{y}" width="24" '
                         f'height="{RH}" fill="transparent"/>{dot}</g>')
    # count row
    y = Y0 + RH * len(rowsids) + 18
    parts.append(text(X0 - 8, y, "members reading it", cls="t-mut", anchor="end", size=10))
    for i, c in enumerate(cols):
        n = sum(1 for mid in rowsids if c[1] in D.MAP_ROWS[mid])
        parts.append(text(X0 + CW * i + CW / 2, y, str(n), cls="t-pri", anchor="middle", size=11))
    H = y + 12
    svg = (f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Which member reads '
           f'which input">{"".join(parts)}</svg>')
    head = "".join(f"<th>{E(c[1])}</th>" for c in cols)
    body = "".join(
        f"<tr><td>{E(mid)} {E(names[mid])}</td>" + "".join(
            f"<td class='num'>{'●' if c[1] in D.MAP_ROWS[mid] else ''}</td>" for c in cols) + "</tr>"
        for mid in rowsids)
    table = (f"<details><summary>Table view: the family map</summary><div class='scroll'><table><thead><tr>"
             f"<th>member</th>{head}</tr></thead><tbody>{body}</tbody></table></div></details>")
    return svg + table


# ---------------------------------------------------------------- page
CSS = r"""
.viz-root{color-scheme:light;--surface-1:#fcfcfb;--page:#f9f9f7;--text-primary:#0b0b0b;
--text-secondary:#52514e;--muted:#898781;--grid:#e1e0d9;--axis:#c3c2b7;--band:#f3f2ee;
--series-1:#2a78d6;--series-2:#eb6834;--series-3:#1baf7a;--border:rgba(11,11,11,.10)}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{color-scheme:dark;
--surface-1:#1a1a19;--page:#0d0d0d;--text-primary:#f0efec;--text-secondary:#c3c2b7;--muted:#898781;
--grid:#2c2c2a;--axis:#383835;--band:#21211f;--series-1:#3987e5;--series-2:#d95926;--series-3:#199e70;
--border:rgba(255,255,255,.10)}}
:root[data-theme="dark"] .viz-root{color-scheme:dark;--surface-1:#1a1a19;--page:#0d0d0d;
--text-primary:#f0efec;--text-secondary:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;
--band:#21211f;--series-1:#3987e5;--series-2:#d95926;--series-3:#199e70;--border:rgba(255,255,255,.10)}
body{margin:0}
.viz-root{background:var(--page);color:var(--text-primary);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;min-height:100vh}
main{max-width:980px;margin:0 auto;padding:24px 20px 80px}
h1{font-size:26px;margin:8px 0 4px}h2{font-size:20px;margin:40px 0 8px;border-top:1px solid var(--grid);padding-top:20px}
h3{font-size:16px;margin:24px 0 6px}
.sub{color:var(--text-secondary);margin:0 0 16px}
.card{background:var(--surface-1);border:1px solid var(--border);border-radius:10px;padding:14px 18px;margin:14px 0}
.chart{background:var(--surface-1);border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin:14px 0}
code,pre{font:12.5px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace}
pre{background:var(--page);border:1px solid var(--border);border-radius:6px;padding:8px 10px;overflow-x:auto;margin:6px 0}
.math{font:13px/1.5 ui-monospace,Menlo,monospace;background:var(--page);border-left:3px solid var(--axis);padding:6px 10px;margin:6px 0}
table{border-collapse:collapse;width:100%;font-size:13px;margin:8px 0}
th,td{border-bottom:1px solid var(--grid);padding:5px 6px;text-align:left;vertical-align:top}
th{color:var(--text-secondary);font-weight:600}td.num{text-align:right;font-variant-numeric:tabular-nums}
.scroll{overflow-x:auto}
summary{cursor:pointer;color:var(--text-secondary);font-size:13px;margin-top:6px}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:12.5px;color:var(--text-secondary);margin:2px 0 6px}
.lg{display:inline-flex;align-items:center;gap:6px}
.t-pri{fill:var(--text-primary)}.t-sec{fill:var(--text-secondary)}.t-mut{fill:var(--muted)}
.grid{stroke:var(--grid);stroke-width:1}.axis{stroke:var(--axis);stroke-width:1}
.track{stroke:var(--axis);stroke-width:2}.flip{stroke:var(--text-primary);stroke-width:1.5}
.rug{stroke:var(--text-secondary);stroke-width:1}.band{fill:var(--band)}.dotoff{fill:var(--axis)}
.xhair{stroke:var(--text-secondary);stroke-width:1;opacity:0}
.col:hover .xhair,.col:focus .xhair{opacity:1}
.hit{outline:none}.hit:hover circle,.hit:focus circle,.hit:hover path,.hit:focus path,.hit:hover rect+rect{filter:brightness(1.15)}
.hit:focus-visible{outline:2px solid var(--series-1)}
#tip{position:fixed;pointer-events:none;background:var(--surface-1);color:var(--text-primary);border:1px solid var(--border);
border-radius:8px;padding:7px 10px;font-size:12.5px;white-space:pre-line;max-width:420px;box-shadow:0 4px 18px rgba(0,0,0,.18);display:none;z-index:9}
.verdict{font-weight:600}.v-delib{color:var(--text-primary)}
.pill{display:inline-block;border:1px solid var(--axis);border-radius:999px;padding:0 8px;font-size:12px;color:var(--text-secondary)}
button.theme{float:right;background:var(--surface-1);color:var(--text-primary);border:1px solid var(--border);border-radius:8px;padding:4px 10px;cursor:pointer}
ol li,ul li{margin:4px 0}
"""

JS = r"""
(function(){
 var tip=document.getElementById('tip');
 function show(el,x,y){tip.textContent=el.getAttribute('data-tip');tip.style.display='block';
  var w=tip.offsetWidth,h=tip.offsetHeight;var nx=x+14,ny=y+14;
  if(nx+w>innerWidth-8)nx=x-w-14;if(ny+h>innerHeight-8)ny=y-h-14;tip.style.left=nx+'px';tip.style.top=ny+'px';}
 document.querySelectorAll('[data-tip]').forEach(function(el){
  if(!el.getAttribute('data-tip'))return;
  el.addEventListener('pointermove',function(e){show(el,e.clientX,e.clientY);});
  el.addEventListener('pointerleave',function(){tip.style.display='none';});
  el.addEventListener('focus',function(){var r=el.getBoundingClientRect();show(el,r.right,r.top);});
  el.addEventListener('blur',function(){tip.style.display='none';});});
 var b=document.getElementById('theme');b.addEventListener('click',function(){
  var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||
   (!r.getAttribute('data-theme')&&matchMedia('(prefers-color-scheme: dark)').matches);
  r.setAttribute('data-theme',dark?'light':'dark');});
})();
"""


def member_card(m):
    code = "".join(f"<div><code>{E(loc)}</code><pre>{E(src)}</pre></div>" for loc, src in m["code"])
    inp = "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td></tr>"
                  for a, b, c, d in m["inputs"])
    note = f"<p><b>Note.</b> {E(m['note'])}</p>" if m.get("note") else ""
    return f"""<div class="card"><h3>{E(m['id'])} {E(m['name'])} <span class="pill">{E(m['kind'])}</span></h3>
<p><b>Question.</b> {E(m['question'])}</p>
<p><b>Unit of the comparison.</b> {E(m['unit'])}</p>
<div class="math">{E(m['math'])}</div>
<details open><summary>As shipped (the C)</summary>{code}</details>
<table><thead><tr><th>input</th><th>where the number comes from</th><th>unit</th><th>box / when</th></tr></thead><tbody>{inp}</tbody></table>
<p><b>Hand-set constants.</b> {E(m['constants'])}</p>
<p><b>With no prior (NONE).</b> {E(m['none'])}</p>{note}</div>"""


def build():
    prior = default_prior()
    rc = reach()
    rch = {n: v for n, v, _ in rc}
    members = "".join(member_card(m) for m in D.MEMBERS)
    cand_rows = "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td></tr>"
                        for a, b, c, d, e in D.CANDIDATES)
    adapters = "".join(
        f"<tr><td><b>{E(a['id'])}</b></td><td>{E(a['member'])}</td><td>{E(a['quirk'])}</td><td>{E(a['why'])}</td>"
        f"<td class='verdict'>{E(a['vtext'])}</td><td>{E(a['reach'])}</td></tr>" for a in D.ADAPTERS)
    reach_rows = "".join(f"<tr><td>{E(n)}</td><td class='num'>{v:,}</td><td><code>{E(h)}</code></td></tr>"
                         for n, v, h in rc)
    cmp_rows = """
<tr><td>#1 G1</td><td>COMPARE</td><td>ppm vs ppm</td><td>prior (rate[p], rate[q])</td><td>—</td><td>false (keep the pre-check)</td></tr>
<tr><td>#2 set-leads</td><td>PICK</td><td>ppm, argmin of 2</td><td>prior via PICK, req_run, req_set</td><td>shares PICK/cube mass with #14, #15a, #15b</td><td>cardinality</td></tr>
<tr><td>#3 R4</td><td>VERDICT (really: an arm's starting state)</td><td>bytes (mean gap vs crossover)</td><td>prior via MASS; scan set; program class</td><td>R4 gap 16/4 B (Mac M1): read by no other member</td><td>cardinality; no scan → 10⁶ (A5)</td></tr>
<tr><td>#4 K admission</td><td>VERDICT (an advance comparison)</td><td>bytes (jump vs skip)</td><td>prior via MASS; K; displaced row</td><td>no constant at all</td><td>cardinality; non-scanning displaced row → 10⁶ (A2)</td></tr>
<tr><td>#7 prefix_k</td><td>VERDICT (argmin planner)</td><td>hundredths of a cycle per byte</td><td>prior via MASS; kset walk; k0</td><td>C_MEMCHR, C_BITMAP, C_ENTER, C_VERIFY, C_MISPRED, MATERIAL, MAX_SET: read by no other member</td><td>cardinality</td></tr>
<tr><td>#13 window start</td><td>PICK</td><td>ppm, argmin of window sums</td><td>prior via sequence MASS; run</td><td>MAX_REQ_RUN_EMIT 8 (window length)</td><td>cardinality, ties leftmost</td></tr>
<tr><td>#15a scan index</td><td>PICK</td><td>ppm, argmin</td><td>prior via PICK; run</td><td>—</td><td>cardinality, ties rightmost</td></tr>
<tr><td>#14 run pin</td><td>PICK</td><td>ppm, argmin</td><td>prior via PICK; run; kset walk</td><td>—</td><td>rightmost</td></tr>
<tr><td>#15b req pick</td><td>PICK</td><td>ppm, argmin</td><td>prior via PICK; set; run</td><td>—</td><td>rightmost</td></tr>
<tr><td>#21 RQ-2 rank</td><td>PICK (full order)</td><td>ppm, sort</td><td>prior via cube mass; run term</td><td>—</td><td>cube size, then rightmost</td></tr>"""
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>[PRIOR-COST-UNIFY]: what goes into each decision today</title><style>{CSS}</style></head>
<body><div class="viz-root"><main>
<button class="theme" id="theme" type="button">Light / dark</button>
<h1>The prior-cost family: what goes into each decision today</h1>
<p class="sub">Report for Frank · lane <code>pcureport</code> · {D.DATE} · read at main <code>{D.COMMIT}</code> (abi 75).
Sources: <code>docs/design/prior_cost_unify.md</code> rev 2 and its derived census; every formula below re-read in the code it cites. Where the note and the code disagree, the code is reported. No advocacy for or against the unification: this describes what ships.</p>

<div class="card"><h3 style="margin-top:4px">The five plainest findings</h3><ol>
<li><b>The three "VERDICT" members ask three different questions in three different units.</b> #4 compares two expected jump lengths in bytes and has no hand-set constant. #3 compares a mean gap in bytes against a crossover measured on a Mac, and only picks the <i>starting state</i> of a retry arm that runs either way. #7 is the only cost model: hundredths of a cycle per byte, five cycle constants (three from Zen 1, two with no measurement record) and a 2× bar. No cost constant (a cycle price or a crossover) is read by two members; the only shared hand-set numbers are the prior's 2 ppm floor and the 16-bit run-admission floor, which gate inputs rather than price them.</li>
<li><b>The real overlaps are small and specific.</b> #3 and #4 both reduce to "is the mean distance between scan stops, 10⁶/ppm bytes, shorter than some byte distance?". The six PICKs already share one primitive and one NONE rule. #7's cycle model and G1's NONE = false do not fit either group.</li>
<li><b>The adapters preserve quirks of very different weight.</b> A2 preserves a case with zero corpus reach (0 of 181 handoff artifacts). A5's "no scan means 10⁶" branch produces 16 of the 35 corpus <code>adaptive-dense</code> answers: almost half of R4's dense verdicts never read the prior. A1 pairs a documented UP rounding (#4) with an undocumented integer truncation (#7). A4 is a rule, not an adapter.</li>
<li><b>Two of #7's constants have no measurement record.</b> Rev 2 §3.2 labels <code>C_VERIFY</code> (2.5 c) and <code>C_MISPRED</code> (15 c) "MEASURED, Zen 1"; <code>offset_k_skip.md</code> §4.2 gives a description and no source for either. <code>C_ENTER</code> is half assumed, and <code>C_MEMCHR</code> ships as 0.06 c/B against a measured 0.055.</li>
<li><b>The unified cost cannot be evaluated today.</b> Its new term, <code>stop_reentry</code>, is unmeasured on every box. The constants that do exist come from two boxes in two units (Zen 1 cycles, Mac ns), and rev 2's own same-box rule forbids combining them.</li>
</ol></div>

<h2>1. The members, one by one</h2>
<p>The ten decisions that read the byte-rate prior today (rev 2 §1.1 part A, derived by call graph). Every <code>file:line</code> is at <code>{D.COMMIT}</code>. "The prior" throughout is <code>src/findings/default.rxt</code>: an authored table (English letter frequencies plus log-line punctuation, floor 2 ppm, 2026-08-28) that serves <code>-e byte</code> only. Under <code>-e utf8</code> with no analysis it is NONE, and each primitive answers by cardinality.</p>
{members}
<h3>Candidates that compare scan alternatives without the prior</h3>
<p>Rev 2 lists these by hand (part B). They are included for completeness; none reads a rate today.</p>
<table><thead><tr><th>#</th><th>decision</th><th>state</th><th>today's test</th><th>its constant and label</th></tr></thead><tbody>{cand_rows}</tbody></table>

<h2>2. Side by side</h2>
<table><thead><tr><th>member</th><th>kind</th><th>unit of the comparison</th><th>inputs</th><th>hand-set constants, and who else reads them</th><th>NONE</th></tr></thead><tbody>{cmp_rows}</tbody></table>
<p>What every member shares is the prior itself and its 2 ppm floor; six also share the 16-bit run-admission floor through <code>req_run</code>. What no two members share is a cost constant: every cycle price and every crossover has exactly one reader. The map below shows it cell by cell.</p>
<div class="chart"><h3 style="margin-top:2px">Chart C. Which member reads which input</h3>
<p class="sub">A filled dot means the member's code reads that input. Columns are grouped by where the number comes from.</p>
{chart_map()}</div>

<h2>3. The adapters rev 2 needs</h2>
<p>Rev 2 §4.2 says step U1 is zero-mover only if each member's quirk is reproduced by a stated mapping (an "adapter"). For each: what the quirk is in today's code, whether a reason is recorded, and how many corpus artifacts it touches. <b>DELIBERATE</b> means a reason is written in the code or a design record; <b>INCIDENTAL</b> means none was found.</p>
<div class="scroll"><table><thead><tr><th>id</th><th>member</th><th>the quirk, in today's code</th><th>why it exists</th><th>verdict</th><th>reach (corpus)</th></tr></thead><tbody>{adapters}</tbody></table></div>
<details><summary>Where the reach numbers come from</summary>
<p><code>docs/dev/summaries/prior_cost_inputs/reach_probe.py</code>: every <code>pattern</code> line of every <code>tests/**/*.rxt</code> (emit_sweep's own enumerator), compiled <code>-p rx --features all</code> at the default engine and <code>-e byte</code>, stamps read; each <code>handoff</code> artifact compiled again with <code>-fno-req-handoff</code> to see the displaced row. This is the test corpus, not the bench, and <code>-e byte</code> only.</p>
<table><tbody>{reach_rows}</tbody></table></details>
<p><b>Reading the table.</b> A2 and A5 both turn "there is no scan to price" into "every byte is a stop" (10⁶ ppm). For #4's <code>none</code> row a reason is written down; for A2's offset rows and for A5 it is not, and A5 decides 16 artifacts. A1 needs two different rounding directions because #4 rounds up deliberately and #7 truncates as a side effect of integer division. A3 is a choice about which byte the retry's gap is measured on, and it is written down, but why the verify chain may be ignored is not.</p>

<h2>4. Assessment: same question, or only alike?</h2>
<h3>Genuinely the same question, same units</h3>
<ul>
<li><b>The six PICKs (#2, #13, #14, #15a, #15b, #21).</b> Each is an argmin (or a sort) of byte masses in ppm, through <code>pcrec_find_pick</code> / <code>cube_mass</code> / <code>seq_mass</code>, with one tie and NONE rule (rightmost, or leftmost for the window). They are already one mechanism; there is nothing left to unify. Evidence: <code>src/core/findings.c:421-611</code>.</li>
<li><b>#3 and #4, as advance comparisons.</b> R4 asks "is 10⁶/mass(S) &lt; gap?" and the K admission asks "is 10⁶/h − K &gt; 10⁶/m?". Both are distances in subject bytes derived from stop rates. A shared, exact advance comparison (rev 2's cross-multiplied <code>adv</code>) would serve both without changing either formula. Rev 2's own grid shows #3's rational form is exact (0 of 1,332 cells differ).</li>
</ul>
<h3>Only alike: different questions or units</h3>
<ul>
<li><b>#7 against #3 and #4.</b> #7 prices cycles per byte with five constants and adopts only at a 2× margin. #3 and #4 have no cycle term at all. Putting #3 and #4 on #7's cost scale means giving them constants they do not use today (rev 2's <code>stop_reentry</code>, <code>step_byte</code>), none of which is measured. That is a new model, not a unification of the existing ones.</li>
<li><b>#3's outcome is not pay-or-decline.</b> <code>adaptive-dense</code> and <code>adaptive</code> run the same arm (<code>CAND_RS_A_ADAPT</code>); the decision only sets where it starts (<code>emit_dfa.c:9078-9092</code>). A cost VERDICT answering PAYS/DECLINE is a different shape of answer.</li>
<li><b>G1 (#1) against the VERDICTs.</b> G1's NONE answer is <code>false</code> (keep the pre-check), while every VERDICT prices NONE by cardinality. Rev 2 F-2 itself says a single NONE answer would move G1 under <code>-e utf8</code>.</li>
<li><b>The rev 2 primitive's NONE against today's members.</b> Rev 2 defines "no scan" as zero stops. Today A2 and A5 treat it as 10⁶ stops, and rev 2 must add adapters to undo its own definition at both sites.</li>
<li><b>The constants' boxes.</b> #7's constants are Zen 1 cycles (2026-08-26) or have no record; #3's are Mac M1 nanosecond crossovers (2026-09-29/30). Rev 2's Q3 (settled) allows only same-box ratios, so no shipped constant pair can be combined.</li>
</ul>

<h2>Chart A. Every hand-set constant</h2>
<div class="chart"><p class="sub">One row per constant, grouped by unit; each group has its own log axis. Colour is provenance, shape is the box it was measured on. Hover a mark for its source.</p>
{chart_constants()}</div>

<h2>Chart B. Where each VERDICT member flips</h2>
<div class="chart"><p class="sub">Three panels, because the three members read different rates and decide different things. The x axis is a byte rate in ppm in every panel, but it is a different set's rate in each. Boundaries are computed with the shipped integer arithmetic.</p>
{chart_boundaries(prior)}</div>

<h2>Method and caveats</h2>
<ul>
<li>Every formula was re-read in the code at <code>{D.COMMIT}</code>; line numbers match rev 2's except where noted. The code's own comments are quoted where a reason is recorded.</li>
<li>Reach numbers are stamp counts over the test corpus at <code>-e byte</code> (5,194 compiling pattern lines), not the bench and not <code>-e utf8</code>.</li>
<li>Chart B's #7 panel fixes one scan offset and the mandatory offset-0 verify; the real planner also adds verifies greedily, which moves the curves but not their shape.</li>
<li>Discrepancies with rev 2 found here: <code>C_VERIFY</code>/<code>C_MISPRED</code> provenance (§3.2 says MEASURED; no record found), and <code>C_MEMCHR</code>'s coded value (6 hundredths, not 5.5).</li>
<li>Generated by <code>docs/dev/summaries/prior_cost_inputs/gen_report.py</code>.</li>
</ul>
</main><div id="tip" role="tooltip"></div></div><script>{JS}</script></body></html>
"""
    with open(OUT, "w") as f:
        f.write(page)
    print(f"wrote {os.path.relpath(OUT, ROOT)} ({len(page):,} bytes)")


if __name__ == "__main__":
    build()
