#!/usr/bin/env python3
"""[OPT-GAPREPORT] the one-command driver (D144 addendum 2).

    gapreport.sh --group b120b121-fc719ca4 --out docs/dev/optloop/gapreport_2026-10-04.md
    gapreport.sh --group latest --out ...
    gapreport.sh --check            # fixture self-test, exit nonzero on mismatch

Fetches the named (or latest) bench report group's `.tsv` files and the bench
set inputs read-only from the Linux box, runs extract -> stamps -> nmatch ->
gap -> rank with the current build/pcrec, and renders the report markdown.
The MANAGER JUDGEMENT section is copied from a hand-kept notes file, so a
re-run never overwrites judgement.  The criteria are gapconfig.py's tables.
Stdlib only.  Nothing is written outside --out and --scratch, and nothing in
pcrec-bench (the fetch is ssh + tar, read-only on the remote).
"""
import argparse
import collections
import glob
import json
import math
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gap  # noqa: E402  (compare/med: the cross-form view reuses the metric)
import gapconfig as cfg  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FIXTURE = os.path.join(HERE, "fixture")
REPORT_RE = re.compile(r"^(\d{4}-\d\d-\d\d)-(.+?)-(\d+\.\d+)-(budu-[a-z0-9]+)-(.+)\.tsv$")
MARK_BEGIN = "<!-- MANAGER JUDGEMENT: begin (copied from %s; edit that file, never this section) -->"
MARK_END = "<!-- MANAGER JUDGEMENT: end -->"
NOT_SELECTION = ("code_sha", "c_bytes", "ABI")


def say(msg):
    print(f"gapreport: {msg}", file=sys.stderr)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


# --- step 0: fetch ----------------------------------------------------------

def ssh_cmd(remote, script):
    return ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", remote, script]


def list_groups(remote):
    out = run(ssh_cmd(remote, f"ls {shlex.quote(cfg.REMOTE_BENCH)}/reports"),
              capture_output=True, text=True, timeout=120).stdout.split()
    groups = collections.defaultdict(dict)       # group -> set -> (date, file)
    for fn in out:
        if not fn.endswith(".tsv") or fn.endswith((".matrix.tsv", ".subject-grain.tsv")):
            continue
        m = REPORT_RE.match(fn)
        if m:
            date, sb, _ver, _mach, grp = m.groups()
            if sb not in groups[grp] or groups[grp][sb][0] < date:
                groups[grp][sb] = (date, fn)
    return groups


def pick_group(groups, want):
    if want != "latest":
        if want not in groups:
            sys.exit(f"gapreport: no report group {want!r}; have: "
                     + ", ".join(sorted(groups)[-12:]))
        return want
    return max(groups, key=lambda g: (max(d for d, _ in groups[g].values()),
                                      len(groups[g]), g))


def fetch(remote, group, scratch):
    groups = list_groups(remote)
    group = pick_group(groups, group)
    files = {sb: fn for sb, (_d, fn) in groups[group].items()}
    want = {"email-specimen" if s == "email" else s for s in cfg.SETS}
    if want - set(files):
        say("WARNING group %s lacks report(s) for: %s" % (group, ", ".join(sorted(want - set(files)))))
    rep = os.path.join(scratch, "reports")
    ben = os.path.join(scratch, "bench")
    for d in (rep, ben):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    names = " ".join(shlex.quote(f) for f in sorted(files.values()))
    p = subprocess.Popen(ssh_cmd(remote, f"cd {shlex.quote(cfg.REMOTE_BENCH)}/reports && tar -cf - {names}"),
                         stdout=subprocess.PIPE)
    run(["tar", "-xf", "-", "-C", rep], stdin=p.stdout)
    if p.wait():
        sys.exit("gapreport: report fetch failed")
    items = " ".join(f"{s}/manifest_throughput.tsv {s}/expectations.tsv {s}/patterns" for s in cfg.SETS)
    p = subprocess.Popen(ssh_cmd(remote, f"cd {shlex.quote(cfg.REMOTE_BENCH)}/bench && tar -cf - {items}"),
                         stdout=subprocess.PIPE)
    run(["tar", "-xf", "-", "-C", ben], stdin=p.stdout)
    if p.wait():
        sys.exit("gapreport: bench input fetch failed")
    return group, rep, ben


# --- steps 1-4 ----------------------------------------------------------------

def step(script, args, out, env=None, timeout=None, quiet=False):
    cmd = [sys.executable, os.path.join(HERE, script)] + args
    with open(out, "w") as fh:
        run(cmd, stdout=fh, env=dict(os.environ, **(env or {})), timeout=timeout,
            stderr=subprocess.DEVNULL if quiet else None)


def pipeline(rep, ben, pcrec, scratch, baseline, causes, stamps_timeout, quiet=False):
    a = {k: os.path.join(scratch, k) for k in
         ("cells.json", "stamps.json", "nmatch.json", "gap_rows.json", "rank.json")}
    reports = sorted(glob.glob(os.path.join(rep, "*.tsv")))
    if not reports:
        sys.exit("gapreport: no report .tsv files in " + rep)
    say(f"1/4 extract ({len(reports)} reports)")
    run([sys.executable, os.path.join(HERE, "extract.py"), a["cells.json"]] + reports,
        stderr=subprocess.DEVNULL)
    say("2/4 stamps (serial compile of every bench pattern; slow)")
    stamp_out = os.path.join(scratch, "stamp_art")
    step("stamps.py", ["current"], a["stamps.json"], timeout=stamps_timeout,
         env={"PCREC": pcrec, "BENCH": ben,
              "OUT": stamp_out}, quiet=quiet)
    say("3/4 nmatch + gap")
    step("nmatch.py", [ben], a["nmatch.json"])
    step("gap.py", [a["cells.json"], a["stamps.json"], baseline], a["gap_rows.json"])
    say("4/4 rank")
    step("rank.py", [a["gap_rows.json"], causes, a["nmatch.json"]], a["rank.json"])
    return a


# --- render ---------------------------------------------------------------------

def load_descs(causes):
    d = {}
    for line in open(causes):
        if line.startswith("#group\t"):
            _, g, text = line.rstrip("\n").split("\t", 2)
            d[g] = text
    return d


def merge_groups(groups):
    out = {}
    for g, G in groups.items():
        tgt = next((m for k, m in cfg.GROUP_MERGE if k == g), g)
        T = out.setdefault(tgt, {"peer": [], "ceiling": [], "score_peer": 0.0, "score_ceiling": 0.0,
                                 "sets": set(), "scalar_wins": [], "rust_only": 0, "members": []})
        T["peer"] += G["peer"]
        T["ceiling"] += G["ceiling"]
        T["score_peer"] += G["score_peer"]
        T["score_ceiling"] += G["score_ceiling"]
        T["sets"] |= set(G["sets"])
        T["scalar_wins"] += G["scalar_wins"]
        T["rust_only"] += G["rust_only"]
        T["members"].append(g)
    for G in out.values():
        G["breadth"] = len({(e["set"], e["pattern"], e["regime"]) for e in G["peer"] + G["ceiling"]})
        G["score_combined"] = G["score_peer"] + G["score_ceiling"]
        G["algorithmic"] = bool(G["scalar_wins"])
    return out


def ranked(groups):
    return sorted(groups, key=lambda g: tuple(-groups[g][k] if not isinstance(groups[g][k], bool)
                                              else -int(groups[g][k]) for k in cfg.RANK_KEY) + (g,))


def xr(e):
    if e["tier"] == "C":
        return "%+.1f ns/call" % e["delta_ns_call"]
    r = e["ratio"]
    return "x%.1f" % r if r >= 10 else "x%.2f" % r


def worst(entries):
    sc = [e for e in entries if e["tier"] != "C"]
    if sc:
        e = max(sc, key=lambda e: e["ratio"])
    elif entries:
        e = max(entries, key=lambda e: e["delta_ns_call"])
    else:
        return "0"
    who = "" if e["cmp"] == cfg.PEER else " " + short(e["cmp"])
    return "**%s**%s" % (xr(e), who)


def short(t):
    return t


def cname(e):
    return "%s `%s`" % (e["set"], e["pattern"])


def cell_line(e, peer):
    s = "- %s %s: %s %s" % (cname(e), e["regime"].replace("large-subject-", "").replace("-search", ""),
                            xr(e), "jit" if peer else short(e["cmp"]))
    if e["tier"] == "C":
        s += " (tier C, not scored)"
    if e.get("bytes") and e.get("auto_caps_ns"):
        s += "; auto %.3f ns/B" % (e["auto_caps_ns"] / e["bytes"])
    return s


def geomean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else float("nan")


def selection_diff(cur, base):
    """patterns whose selection stamps (or refusal) differ between two censuses"""
    moves, only = [], []
    norm = lambda t: re.sub(r"\d+", "N", t)
    for sb in sorted(set(cur) | set(base)):
        for pat in sorted(set(cur.get(sb, {})) | set(base.get(sb, {}))):
            c, b = cur.get(sb, {}).get(pat), base.get(sb, {}).get(pat)
            if c is None or b is None:
                only.append((sb, pat, "current" if b is None else "baseline"))
                continue
            if ("refused" in c) != ("refused" in b):
                moves.append((sb, pat, {"refused": (b.get("refused"), c.get("refused"))}))
            elif "refused" in c:
                if norm(c["refused"]) != norm(b["refused"]):
                    moves.append((sb, pat, {"refused": (b["refused"], c["refused"])}))
            else:
                d = {k: (b.get(k), c.get(k)) for k in sorted(set(b) | set(c))
                     if k not in NOT_SELECTION and b.get(k) != c.get(k)}
                if d:
                    moves.append((sb, pat, d))
    return moves, only


def render(a, group, date, causes, judgement, baseline, provenance):
    rows = json.load(open(a["gap_rows.json"]))
    rk = json.load(open(a["rank.json"]))
    cells = json.load(open(a["cells.json"]))
    cur = json.load(open(a["stamps.json"]))
    base = json.load(open(baseline))
    descs = load_descs(causes)
    groups = merge_groups(rk["groups"])
    order = ranked(groups)
    J = cfg.PEER
    sets = sorted({r["sb"] for r in rows})

    census = collections.defaultdict(collections.Counter)
    gm = collections.defaultdict(list)
    for r in rows:
        j = r["cmp"].get(J)
        if j:
            census[r["sb"]][j["verdict"]] += 1
            gm[r["sb"]].append(j["ratio"])
    tot = collections.Counter()
    for c in census.values():
        tot.update(c)
    n_like = sum(tot.values())
    behind = [r for r in rows if r["cmp"].get(J, {}).get("verdict") == "behind"]
    interp = "libpcre2:interp-caps"
    interp_slower = sum(1 for r in behind if r["cmp"].get(interp, {}).get("verdict") == "ahead")

    L = []
    w = L.append
    w(f"# [OPT-GAPREPORT] gap report {date}: report group `{group}`\n")
    w("Generated by `gapreport/gapreport.sh`; the criteria are `gapreport/gapconfig.py`'s tables "
      "(D144 addendum 2, addendum 1). Everything above the MANAGER JUDGEMENT section is "
      "computed and is overwritten by a re-run; the judgement section is copied from a notes "
      "file.\n")
    w("## Summary\n")
    w(f"**Scope.** {n_like} throughput and search cells compare like with like (same subject, same "
      f"regime, both sides `measured`) between pcrec's shipped default (`auto`) and **pcre2-jit**. "
      f"pcrec **leads on {tot['ahead']}, is level on {tot['null']}, and trails on {tot['behind']}**. "
      f"On {interp_slower} of the {tot['behind']} trailing cells pcre2-interp is slower than pcrec "
      f"(past the null band), so the JIT is winning on code generation or SIMD, not on a mechanism "
      f"pcrec lacks.\n")
    if rk["unassigned"]:
        w("**UNASSIGNED: %d losing cell(s) have no entry in causes.tsv; the ranking below omits them "
          "(section 6).**\n" % len(rk["unassigned"]))
    w("| # | cause group | breadth | worst vs jit | worst vs ceiling | algorithmic |")
    w("|---|---|---|---|---|---|")
    for i, g in enumerate(order[:5], 1):
        G = groups[g]
        w(f"| {i} | **{g}**: {descs.get(g) or descs.get(G['members'][0], '')} | {G['breadth']} | "
          f"{worst(G['peer'])} | {worst(G['ceiling'])} | {'yes' if G['algorithmic'] else 'no'} |")
    w("")
    w("## 1. Input, pins, build\n")
    w("| set | report | pcrec testees |")
    w("|---|---|---|")
    for sb in sorted(cells["meta"]):
        m = cells["meta"][sb]
        w(f"| {sb} | `{m['report']}` | version {m['version']} |")
    pins = sorted({v["id"].split("_")[1] for c in cells["cells"].values()
                   for t, v in c["t"].items() if t.startswith("pcrec:")})
    w("")
    w(f"- pcrec records measured at: {', '.join('`%s`' % p for p in pins)} (the pin).")
    w(f"- stamps compiled with: {provenance}; abi {sorted({v.get('ABI') for s in cur['stamps'].values() for v in s.values() if v.get('ABI')})}.")
    w(f"- stamp baseline: `{base.get('label')}` (abi {base.get('abi', '?')}).")
    w("- The metric, tiers and null bands are `gapconfig.TIERS`: " +
      "; ".join(f"{t} >= {f} ns/subject ({m} {p})" for f, t, m, p in cfg.TIERS) + ".\n")
    w("## 2. Ranked cause groups\n")
    w("Order: " + ", then ".join(cfg.RANK_KEY) + " (descending). A group where a scalar engine also "
      "beats auto is algorithmic evidence (D119). Peer = pcre2-jit; ceiling = the worst "
      "non-excluded comparator. Scores are realism x log2(ratio) over tier A/B cells.\n")
    w("| rank | group | breadth (sets) | peer n / worst / score | ceiling n / worst / score | alg. | combined |")
    w("|---|---|---|---|---|---|---|")
    for i, g in enumerate(order, 1):
        G = groups[g]
        alg = "yes" if G["algorithmic"] else ("rust-only" if G["rust_only"] else "no")
        w(f"| {i} | {g} | {G['breadth']} ({', '.join(sorted(G['sets']))}) | {len(G['peer'])} / "
          f"{worst(G['peer'])} / {G['score_peer']:.2f} | {len(G['ceiling'])} / {worst(G['ceiling'])} / "
          f"{G['score_ceiling']:.2f} | {alg} | {G['score_combined']:.2f} |")
    w("")
    for g in order:
        G = groups[g]
        w(f"### 2.{order.index(g) + 1} {g}: {descs.get(g) or descs.get(G['members'][0], '(no description in causes.tsv)')}\n")
        key = lambda e: (e["tier"] == "C", -e["ratio"])
        for e in sorted(G["peer"], key=key):
            w(cell_line(e, True))
        for e in sorted(G["ceiling"], key=key):
            w(cell_line(e, False))
        if G["scalar_wins"]:
            w("- scalar engines also win on: " + "; ".join(
                f"{p} ({r}, {short(t)} x{x})" for p, r, t, x in G["scalar_wins"][:8]) +
              (f"; +{len(G['scalar_wins']) - 8} more" if len(G["scalar_wins"]) > 8 else ""))
        w("")
    w("## 3. Where pcrec leads\n")
    w("| set | ahead | level | behind | geomean auto/jit |")
    w("|---|---|---|---|---|")
    for sb in sets:
        c = census[sb]
        if gm[sb]:
            w(f"| {sb} | {c['ahead']} | {c['null']} | {c['behind']} | {geomean(gm[sb]):.3f} |")
    w("")
    w("## 4. What could not be judged\n")
    nop = collections.defaultdict(set)
    nopeer = collections.Counter()
    for r in rows:
        if r["auto_caps"] is None and r["auto_nocaps"] is None and r["regime"] != "match-compliance":
            nop[r["sb"]].add(r["pattern"])
        elif not r["cmp"].get(J) and r["regime"] != "match-compliance":
            nopeer[r["sb"]] += 1
    w("- **pcrec not measured** (throughput and search; distinct patterns):")
    for sb in sorted(nop):
        names = sorted(nop[sb])
        w(f"  - {sb}: {len(names)}: " + ", ".join(f"`{n}`" for n in names[:10]) +
          (f", +{len(names) - 10} more" if len(names) > 10 else ""))
    if nopeer:
        w("- **no jit peer on a measured pcrec cell:** " + ", ".join(f"{s} {n}" for s, n in sorted(nopeer.items())))
    xf = collections.Counter()
    xf_behind = []
    for r in rows:
        if r["regime"] != "match-compliance" or r["auto_caps"] is None:
            continue
        peer = cells["cells"].get("\t".join((r["sb"], r["pattern"], r["regime"], "plain", r["fact"])))
        jm = gap.med(peer, J) if peer else None
        if jm is None:
            continue
        v = gap.compare(r["auto_caps"], jm, r["n"])
        xf[v["verdict"]] += 1
        if v["verdict"] == "behind":
            xf_behind.append(f"`{r['pattern']}` {xr(v)}")
    w("- **match regime has no same-form peer** (jit plain vs pcrec whole-subject). Read across "
      f"forms, flagged and never ranked: pcrec ahead {xf['ahead']}, level {xf['null']}, "
      f"behind {xf['behind']}" + (": " + ", ".join(sorted(xf_behind)) if xf_behind else "") + ".")
    tiers = collections.Counter(r["cmp"][J]["tier"] for r in rows if J in r["cmp"])
    nulls = sum(1 for r in rows if r["cmp"].get(J, {}).get("verdict") == "null")
    w(f"- **scale:** vs jit, tier A {tiers['A']}, B {tiers['B']}, C {tiers['C']} (ns-scale: absolute "
      f"deltas, never scored); {nulls} cells inside the null band.")
    inc = sorted({(r["sb"], t, s) for r in rows for t, s in r["pcrec_status"].items()
                  if t in ("pcrec:auto-caps", "pcrec:auto-nocaps") and s != "measured"})
    if inc:
        w("- **pcrec auto arms not `measured`:** " +
          ", ".join(f"{sb} {t.split(':')[1]} {s}" for sb, t, s in inc[:8]) +
          (f", +{len(inc) - 8} more" if len(inc) > 8 else "") + ".")
    w("")
    w("## 5. Stamp moves since the baseline census\n")
    moves, only = selection_diff(cur["stamps"], base["stamps"])
    code = sum(1 for sb in cur["stamps"] for p, v in cur["stamps"][sb].items()
               if p in base["stamps"].get(sb, {}) and "refused" not in v and
               v.get("code_sha") != base["stamps"][sb][p].get("code_sha"))
    w(f"Compared with `{base.get('label')}`: {len(moves)} pattern(s) differ in a selection stamp "
      f"or refusal; the emitted text differs on {code} (`code_sha` is a text hash, NOT an identity "
      f"measure; machine-code identity is the bench's `tools/program_identity.py`).\n")
    losing = {(r["sb"], r["pattern"]) for r in behind}
    for sb, pat, d in moves:
        flag = " **(a trailing cell)**" if (("email-specimen" if sb == "email" else sb), pat) in losing else ""
        w(f"- {sb} `{pat}`{flag}: " + "; ".join(f"{k}: {x!r} -> {y!r}" for k, (x, y) in d.items()))
    for sb, pat, side in only:
        w(f"- {sb} `{pat}`: only in the {side} census")
    w("")
    w("## 6. Unassigned cells (need a causes.tsv entry)\n")
    if rk["unassigned"]:
        w("**%d losing cell(s) have no cause group. Add `set<TAB>pattern<TAB>group` rows to "
          "`gapreport/causes.tsv` and re-run.**\n" % len(rk["unassigned"]))
        for sb, pat, regime, jr, cet in rk["unassigned"]:
            w(f"- UNASSIGNED {sb} `{pat}` ({regime}): vs jit " +
              ("x%.2f" % jr if jr else "n/a") + (f", ceiling {cet}" if cet else ""))
    else:
        w("None: every losing cell has a cause group.")
    w("")
    w("## MANAGER JUDGEMENT\n")
    w(MARK_BEGIN % (os.path.basename(judgement) if os.path.exists(judgement) else judgement))
    if os.path.exists(judgement):
        w(open(judgement).read().rstrip("\n"))
    else:
        w(f"(no judgement file yet: create `{judgement}`; its text is copied here on the next run)")
    w(MARK_END)
    return "\n".join(L) + "\n", rk["unassigned"]


# --- main -----------------------------------------------------------------------

def check(bless):
    scratch = tempfile.mkdtemp(prefix="gapreport-check-")
    try:
        a = pipeline(os.path.join(FIXTURE, "reports"), os.path.join(FIXTURE, "inputs"),
                     os.path.join(FIXTURE, "fakepcrec.py"), scratch,
                     os.path.join(FIXTURE, "baseline_stamps.json"),
                     os.path.join(FIXTURE, "causes.tsv"), 300, quiet=True)
        text, _ = render(a, "fixture", "FIXTURE", os.path.join(FIXTURE, "causes.tsv"),
                         os.path.join(FIXTURE, "judgement.md"),
                         os.path.join(FIXTURE, "baseline_stamps.json"), "fakepcrec.py")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    exp = os.path.join(FIXTURE, "expected.md")
    if bless:
        open(exp, "w").write(text)
        say("blessed " + exp)
        return 0
    want = open(exp).read()
    if text == want:
        say("check OK: fixture report identical to fixture/expected.md")
        return 0
    import difflib
    sys.stderr.writelines(difflib.unified_diff(want.splitlines(True), text.splitlines(True),
                                               "expected.md", "actual"))
    say("check FAILED: rendered report differs from fixture/expected.md")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--group", help="bench report group name (e.g. b120b121-fc719ca4) or 'latest'")
    ap.add_argument("--out", help="report path (default docs/dev/optloop/gapreport_<date>.md)")
    ap.add_argument("--date", help="report date (default: today)")
    ap.add_argument("--scratch", help="scratch dir (default: a fresh mkdtemp under $TMPDIR)")
    ap.add_argument("--no-fetch", action="store_true", help="reuse reports/ and bench/ already in --scratch")
    ap.add_argument("--pcrec", default=os.path.join(REPO, "build", "pcrec"))
    ap.add_argument("--baseline", default=os.path.join(HERE, "stamps_main.json"),
                    help="stamp census to diff against (selection-identical to the pin it names)")
    ap.add_argument("--save-stamps", help="also copy the fresh stamp census here (a new baseline)")
    ap.add_argument("--causes", default=os.path.join(HERE, "causes.tsv"))
    ap.add_argument("--judgement", help="hand-kept notes file (default gapreport/judgement_<date>.md)")
    ap.add_argument("--remote", default=cfg.REMOTE)
    ap.add_argument("--stamps-timeout", type=int, default=3600)
    ap.add_argument("--fail-unassigned", action="store_true")
    ap.add_argument("--check", action="store_true", help="run the fixture and diff against expected.md")
    ap.add_argument("--bless", action="store_true", help="with --check: rewrite fixture/expected.md")
    o = ap.parse_args()
    if o.check:
        sys.exit(check(o.bless))
    if not o.group:
        ap.error("--group is required (a group name or 'latest')")
    import datetime
    date = o.date or datetime.date.today().isoformat()
    out = o.out or os.path.join(REPO, "docs", "dev", "optloop", f"gapreport_{date}.md")
    stem = re.sub(r"^gapreport_", "", os.path.basename(out)[:-3]) if out.endswith(".md") else date
    judgement = o.judgement or os.path.join(HERE, f"judgement_{stem}.md")
    if not os.access(o.pcrec, os.X_OK):
        sys.exit(f"gapreport: {o.pcrec} missing; run `make` first (or pass --pcrec)")
    scratch = o.scratch or tempfile.mkdtemp(prefix="gapreport-")
    os.makedirs(scratch, exist_ok=True)
    if o.no_fetch:
        group, rep, ben = o.group, os.path.join(scratch, "reports"), os.path.join(scratch, "bench")
    else:
        group, rep, ben = fetch(o.remote, o.group, scratch)
    say(f"group {group}; scratch {scratch}")
    ver = run([o.pcrec, "--version"], capture_output=True, text=True).stdout.strip()
    sha = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    a = pipeline(rep, ben, o.pcrec, scratch, o.baseline, o.causes, o.stamps_timeout)
    text, unassigned = render(a, group, date, o.causes, judgement, o.baseline,
                              f"{ver} (repo {sha}, {os.path.relpath(o.pcrec, REPO) if o.pcrec.startswith(REPO) else o.pcrec})")
    open(out, "w").write(text)
    say(f"wrote {out}")
    if o.save_stamps:
        shutil.copy(a["stamps.json"], o.save_stamps)
    if unassigned:
        bar = "!" * 72
        say(bar)
        say(f"UNASSIGNED: {len(unassigned)} losing cell(s) have no causes.tsv entry:")
        for u in unassigned:
            say(f"  {u[0]}\t{u[1]}\t({u[2]})")
        say("add `set<TAB>pattern<TAB>group` rows to " + o.causes + " and re-run")
        say(bar)
        if o.fail_unassigned:
            sys.exit(3)
    if not os.path.exists(judgement):
        say(f"no judgement file: create {judgement} (copied into the report on the next run)")


if __name__ == "__main__":
    main()
