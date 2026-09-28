#!/usr/bin/env python3
"""build_census.py PCREC TREE BENCH OUTDIR -- the lacensus lane's own
census: reproduces ucp_study.md's 492/1,101 "VM-only-because-of-lookaround"
population (studies/ucp_study/census_nocap_13b7c202.tsv,
census_13b7c202.tsv, both committed and reused rather than recompiled --
see lookaround_census.md S2 for why that is sound at this pin), then
classifies every lookaround OCCURRENCE in that population by SHAPE
(shape_classify.py), on the pattern's RAW, UNTRUNCATED bytes -- gathered
fresh from the .rxt/.rx sources by ID, the same population-gathering code
studies/ucp_study/census.py uses, never from the committed TSV's own
pattern column (which is escaped AND truncated to 200 bytes -- the
--list-source escaping trap optrev_report.md already names, sidestepped
here by construction rather than by care).

Writes OUTDIR/{nocap,default}_shapes.tsv (one row per classified pattern)
and prints the S3/S4 tables to stdout.
"""
import collections as C
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import shape_classify as sc

PCREC, TREE, BENCH, OUTDIR = sys.argv[1:5]
STUDY = os.path.join(TREE, "studies", "ucp_study")


def decode_escape(s):
    out, b, i = bytearray(), s.encode("utf-8", "surrogateescape"), 0
    while i < len(b):
        c = b[i]
        if c == 0x5C and i + 1 < len(b):
            n = b[i + 1]
            if n in b"tnr\\":
                out.append({ord('t'): 9, ord('n'): 10, ord('r'): 13, 0x5C: 0x5C}[n]); i += 2; continue
            if n == ord('x') and i + 3 < len(b):
                try:
                    out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError:
                    pass
        out.append(c); i += 1
    return bytes(out)


# ---- S2: gather the RAW population by id, exactly census.py's own walk ----
import subprocess

pop_by_id = {}   # id -> (pattern bytes, enc, ci)
for root in ("tests", "examples"):
    for dp, _, fns in os.walk(os.path.join(TREE, root)):
        for fn in sorted(fns):
            if not fn.endswith(".rxt"):
                continue
            path = os.path.join(dp, fn)
            r = subprocess.run([PCREC, "--list-source", path], capture_output=True)
            if r.returncode:
                continue
            hd_enc, hd_flags, seen_pat = "", "", False
            for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                fl = line.split("\t")
                if len(fl) < 10:
                    continue
                if fl[0] in ("pattern", "pattern-esc"):
                    seen_pat = True
                    enc = fl[8] or hd_enc or "byte"
                    flags = fl[5] or hd_flags
                    rid = "%s:%s" % (os.path.relpath(path, TREE), fl[1])
                    pop_by_id[rid] = (decode_escape(fl[4]), enc, "i" in flags)
                elif not seen_pat and fl[0] == "encoding":
                    hd_enc = fl[3]
                elif not seen_pat and fl[0] == "flags":
                    hd_flags = fl[3]
for dp in sorted(os.listdir(os.path.join(BENCH, "bench"))):
    pd = os.path.join(BENCH, "bench", dp, "patterns")
    if not os.path.isdir(pd):
        continue
    for fn in sorted(os.listdir(pd)):
        if fn.endswith(".rx"):
            rid = "%s/%s" % (dp, fn[:-3])
            pop_by_id[rid] = (open(os.path.join(pd, fn), "rb").read().rstrip(b"\n"),
                               "utf8" if dp == "utf8" else "byte", False)

print("gathered %d ids (fresh, untruncated)" % len(pop_by_id), file=sys.stderr)

# ---- lexical family scan, ucp_study.md's census_analyze.py FAM table plus
# ONE addition ("capture": a plain capturing '(' not itself a lookaround/
# named-group/etc. -- the census_analyze.py D2 code never needed this,
# because it only ever ran on the --no-captures census; the "default"
# census here needs it to tell "VM because of a capture" apart from "VM
# because of a lookaround" (brief DO item 1). ----
FAM = [("lookahead", rb"\(\?[=!]|\(\*(pla|nla|positive_lookahead|negative_lookahead):"),
       ("lookbehind", rb"\(\?<[=!]|\(\*(plb|nlb|positive_lookbehind|negative_lookbehind):"),
       ("nonatomic-look", rb"\(\?<?\*|\(\*(napla|naplb|non_atomic_positive_look(ahead|behind)):"),
       ("atomic", rb"\(\?>|\(\*atomic:"),
       ("possessive", rb"(?<!\\)[*+?}]\+"),
       ("backref", rb"\\[1-9]|\\k[<{']|\\g\{?-?\d|\(\?P=|\\g\{[A-Za-z_]"),
       ("\\K", rb"\\K"),
       ("call", rb"\(\?R\)|\(\?[+-]?\d+\)|\(\?&|\(\?P>|\\g<|\\g'"),
       ("var", rb"\$\{"),
       ("cond", rb"\(\?\(")]
CAPTURE_FAM = ("capture", rb"(?<!\\)\((?![?*])")  # a plain '(' that isn't a
# `(?...)` construct or a `(*verb:`/`(*VERB)` opener (the alpha lookaround
# spellings and PCRE2 backtracking verbs both start '(*' and are NOT
# capturing groups -- the FAM regex's very first draft flagged them as
# 'capture' and wrongly excluded tests/lookaround/alpha_spellings.rxt and
# the bench's syntax/lka-verb from the default-census "lookaround-only"
# population; see lookaround_census.md S2's own found-and-fixed note.
LOOK = {"lookahead", "lookbehind", "nonatomic-look"}


def fams(pat, include_capture):
    """include_capture=False reproduces census_analyze.py's own D2 FAM
    table exactly (no 'capture' entry -- correct for the --no-captures
    census, where a plain capturing group in the TEXT no longer forces
    anything). include_capture=True adds it, for the DEFAULT (captures-on)
    census, where a plain capturing group DOES independently force VM and
    must not be missed as "lookaround is the only reason" (brief DO item
    1: "captures force the VM on their own")."""
    fs = {n for n, rx in FAM if re.search(rx, pat)}
    if include_capture and re.search(CAPTURE_FAM[1], pat):
        fs.add(CAPTURE_FAM[0])
    return fs


def has_view_anchor(pat):
    """A rough top-level check for \\b \\B ^ $ \\A \\Z \\z anywhere in the
    pattern text -- a NOTE, not a structural fact (brief item 2's "which
    patterns combine only (a) with the view assertions the DFA already
    has"); good enough because a false positive from one inside a class or
    a lookaround body only makes the note slightly generous, never wrong
    about the shape census itself."""
    return bool(re.search(rb"\\[bBAZz]|(?<!\[)\^|\$", pat))


def load_census(tsv_path):
    rows = []
    with open(tsv_path) as f:
        header = f.readline()
        cols = header.rstrip("\n").split("\t")
        for line in f:
            v = line.rstrip("\n").split("\t")
            r = dict(zip(cols, v))
            pat_field = r["pattern"]
            rid = pat_field.split(" ", 1)[0]
            r["id"] = rid
            rows.append(r)
    return rows


nocap_rows = load_census(os.path.join(STUDY, "census_nocap_13b7c202.tsv"))
default_rows = load_census(os.path.join(STUDY, "census_13b7c202.tsv"))


def build_population(rows, label, with_capture_family):
    """Returns (selected, vm_total, naive_why_lookaround) where `selected`
    is the list of rows whose engine=='vm' and whose OWN lexical family
    scan (over the RAW pattern) is non-empty and a SUBSET of the lookaround
    families -- i.e., lookaround is provably the only excluding family the
    census's own text can see, not merely the first one WHY happened to
    name."""
    vm_rows = [r for r in rows if r["engine"] == "vm" if r["id"] in pop_by_id]
    missing = [r for r in rows if r["engine"] == "vm" and r["id"] not in pop_by_id]
    if missing:
        print("  WARNING %s: %d vm rows have no id match in the fresh gather (corpus/bench drift since 13b7c202) -- sample: %s"
              % (label, len(missing), [m["id"] for m in missing[:5]]), file=sys.stderr)
    naive_why = [r for r in vm_rows if re.search(r"look(ahead|behind)|\(\?[=!<*]", r.get("why", ""))]
    selected = []
    for r in vm_rows:
        pat = pop_by_id[r["id"]][0]
        f = fams(pat, with_capture_family)
        if not f:
            continue
        if f <= LOOK:
            selected.append(r)
    return selected, len(vm_rows), len(naive_why)


nocap_sel, nocap_vm_total, nocap_naive = build_population(nocap_rows, "no-captures", False)
default_sel, default_vm_total, default_naive = build_population(default_rows, "default", True)

print("\n== S2 reproduction ==")
print("no-captures: vm=%d, lookaround-only (own lexical scan)=%d  [ucp_study.md: 492 of 1101]"
      % (nocap_vm_total, len(nocap_sel)))
print("default:     vm=%d, lookaround-only AND capture-free (own lexical scan)=%d, naive WHY-names-a-lookaround=%d"
      % (default_vm_total, len(default_sel), default_naive))

nocap_ids = {r["id"] for r in nocap_sel}
default_ids = {r["id"] for r in default_sel}
print("default_sel == nocap_sel (same pattern set): %s (symmetric diff %d)"
      % (default_ids == nocap_ids, len(default_ids ^ nocap_ids)))
if default_ids != nocap_ids:
    print("  only in default_sel:", sorted(default_ids - nocap_ids)[:10])
    print("  only in nocap_sel:  ", sorted(nocap_ids - default_ids)[:10])

# ---- S3: shape-classify the union of both selections (they are the same
# patterns per the check above; union guards against the rare case they
# are not) ----
union = {}
for r in nocap_sel + default_sel:
    union[r["id"]] = r

os.makedirs(OUTDIR, exist_ok=True)
out_rows = []
unparsed = []
for rid, r in sorted(union.items()):
    pat, enc, ci = pop_by_id[rid]
    occs = sc.classify_pattern(pat)
    if occs is None:
        unparsed.append(rid)
        continue
    if not occs:
        # the FAM regex (lexical, no structural sense of \Q..\E/classes)
        # matched a lookaround-looking substring that the real parser did
        # NOT treat as a lookaround occurrence -- a false positive of the
        # lexical family scan, not of the shape classifier; logged, not
        # counted as a shaped pattern (S3/S4's own headline excludes it).
        unparsed.append(rid + " (FAM false-positive: no real lookaround found)")
        continue
    worst = sc.worst_shape(occs)
    all_a = all(o['shape'] == 'a' for o in occs)
    all_a_or_b_le2 = all(o['shape'] == 'a' or (o['shape'] == 'b' and o.get('k', 99) <= 2) for o in occs)
    view_anchor = has_view_anchor(pat)
    src = "corpus" if ":" in rid else "bench"
    out_rows.append(dict(id=rid, src=src, enc=enc, ci=ci, n_occ=len(occs), worst=worst,
                          all_a=all_a, all_a_or_b_le2=all_a_or_b_le2, view_anchor=view_anchor,
                          shapes=",".join(sorted({o['shape'] for o in occs})),
                          ks=",".join(str(o.get('k', '')) for o in occs if o['shape'] == 'b'),
                          pattern=pat))

with open(os.path.join(OUTDIR, "shapes.tsv"), "w", encoding="utf-8", errors="surrogateescape") as f:
    f.write("id\tsrc\tenc\tci\tn_occ\tworst\tall_a\tall_a_or_b_le2\tview_anchor\tshapes\tks\tpattern\n")
    for row in out_rows:
        f.write("\t".join([row["id"], row["src"], row["enc"], "i" if row["ci"] else "",
                            str(row["n_occ"]), row["worst"], str(row["all_a"]), str(row["all_a_or_b_le2"]),
                            str(row["view_anchor"]), row["shapes"], row["ks"],
                            row["pattern"].decode("utf-8", "backslashreplace")]) + "\n")

if unparsed:
    print("\nUNPARSED (fell back, not classified): %d -- %s" % (len(unparsed), unparsed[:10]))

MATRIX_PREFIX = "tests/lookaround/d27/matrix.rxt"
print("\n== S3. worst-shape distribution, union population (n=%d, %d unparsed excluded) =="
      % (len(out_rows), len(unparsed)))
for label, f in (("all", lambda r: True), ("corpus", lambda r: r["src"] == "corpus"), ("bench", lambda r: r["src"] == "bench"),
                  ("corpus\\matrix.rxt", lambda r: r["src"] == "corpus" and not r["id"].startswith(MATRIX_PREFIX)),
                  ("matrix.rxt only", lambda r: r["id"].startswith(MATRIX_PREFIX))):
    pop = [r for r in out_rows if f(r)]
    cnt = C.Counter(r["worst"] for r in pop)
    print("  %-7s n=%d  %s" % (label, len(pop), dict(sorted(cnt.items()))))

print("\n== S3b. same, restricted to the DEFAULT (captures-on) population (n=%d: lookaround-only AND capture-free) =="
      % len(default_ids))
for label, f in (("all", lambda r: True), ("corpus", lambda r: r["src"] == "corpus"), ("bench", lambda r: r["src"] == "bench")):
    pop = [r for r in out_rows if r["id"] in default_ids and f(r)]
    cnt = C.Counter(r["worst"] for r in pop)
    na = sum(r["all_a"] for r in pop)
    nab = sum(r["all_a_or_b_le2"] for r in pop)
    print("  %-7s n=%d  %s  ALL-(a)=%d  ALL-(a)-or-(b,k<=2)=%d" % (label, len(pop), dict(sorted(cnt.items())), na, nab))

print("\n== per-occurrence shape totals (every lookaround occurrence, not per pattern) ==")
occ_cnt = C.Counter()
k_dist = C.Counter()
for rid, r in sorted(union.items()):
    pat, enc, ci = pop_by_id[rid]
    occs = sc.classify_pattern(pat) or []
    for o in occs:
        occ_cnt[o['shape']] += 1
        if o['shape'] == 'b':
            k_dist[o.get('k')] += 1
print("  ", dict(sorted(occ_cnt.items())))
print("  shape-b k distribution:", dict(sorted(k_dist.items(), key=lambda kv: (kv[0] is None, kv[0]))))

print("\n== S4. HEADLINE: how many VM-only-because-of-lookaround patterns are ALL-(a), or ALL-(a)-or-(b,k<=2) ==")
for label, f in (("all", lambda r: True), ("corpus", lambda r: r["src"] == "corpus"), ("bench", lambda r: r["src"] == "bench"),
                  ("corpus\\matrix.rxt", lambda r: r["src"] == "corpus" and not r["id"].startswith(MATRIX_PREFIX)),
                  ("matrix.rxt only", lambda r: r["id"].startswith(MATRIX_PREFIX))):
    pop = [r for r in out_rows if f(r)]
    n = len(pop)
    na = sum(r["all_a"] for r in pop)
    nab = sum(r["all_a_or_b_le2"] for r in pop)
    print("  %-7s n=%d  ALL-(a)=%d (%.1f%%)  ALL-(a)-or-(b,k<=2)=%d (%.1f%%)"
          % (label, n, na, 100.0 * na / max(n, 1), nab, 100.0 * nab / max(n, 1)))

print("\n== combine only (a) with an existing view anchor (\\b \\B ^ $ \\A \\Z \\z) ==")
combo = [r for r in out_rows if r["all_a"] and r["view_anchor"]]
print("  n=%d of %d ALL-(a) patterns" % (len(combo), sum(r["all_a"] for r in out_rows)))
