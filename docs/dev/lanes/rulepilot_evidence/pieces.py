#!/usr/bin/env python3
"""rulepilot step 2, the RULE PIECES (docs/design/pricing_rulepilot.md §3).

A piece is a yes/no question over facts pcrec ALREADY states for a compile: the `facts` and
`decisions` sections of `--emit-facts` (docs/spec/facts_listing.md §4.1, §4.2) on the DEFAULT
compile, plus the pattern's compile options. Nothing is measured from a subject.

Two kinds, both FIXED here before any timing:
  BOOL   a yes/no fact; the search uses it and its negation as two literals;
  NUM    a count with a threshold `value >= t`. Every NUM piece is FITTED: t is chosen ONLY from
         the TRAINING half's own values (search.py), and its negation `value < t` is a literal too.
`kind` says where the value comes from: `fact` (the pattern-facts record), `option` (the compile
options), `decision` (a stamp of today's chooser: a rule that reads one CORRECTS cand_rows rather
than replacing it, and the report keeps such lists apart).

usage: pieces.py FACTS_TSV SITES_TSV     prints one row per site: id, then every piece's value
"""
import csv, json, sys

# common bytes of text, for the one CHOSEN (unmeasured) piece: lower-case letters, digits, space,
# tab, newline, `.` and `,`; any other required byte is called "rare". Labelled CHOSEN, not
# FITTED: it is a guess at text, exactly the kind of constant the standing ruling calls suspect.
COMMON = set(range(ord("a"), ord("z") + 1)) | set(range(ord("0"), ord("9") + 1)) | {32, 9, 10, 46, 44}

def _none(v):
    return v in (None, "", "none", "unset")

def run_len(v):
    if _none(v):
        return 0
    h = v.split("@")[0].split("/")[0]
    return len(h) // 2

def set_size(v):
    if _none(v) or ":" not in v:
        return 0
    try:
        return int(v.split(":")[0])
    except ValueError:
        return 0

def width(v):
    """'[a,b)' / '[a,b]' / '[a,inf)' -> (a, b or None)"""
    if _none(v) or not v.startswith("["):
        return None
    a, b = v[1:-1].split(",")
    return int(a), (None if b == "inf" else int(b))

def listlen(v):
    return 0 if _none(v) else len(v.split(","))

# name -> (type, kind, function of (facts dict, options string) -> value)
PIECES = {
    "anchored":        ("BOOL", "fact", lambda f, o: f.get("F.start_anchor") not in (None, "", "unanchored")),
    "nullable":        ("BOOL", "fact", lambda f, o: f.get("F.nullable") == "yes"),
    "has_req_run":     ("BOOL", "fact", lambda f, o: run_len(f.get("F.req_run")) > 0),
    "req_run_len":     ("NUM",  "fact", lambda f, o: run_len(f.get("F.req_run"))),
    "req_run_caseless": ("BOOL", "fact", lambda f, o: "/" in (f.get("F.req_run") or "")),
    "has_req_byte":    ("BOOL", "fact", lambda f, o: not _none(f.get("F.req_byte"))),
    "req_byte_rare":   ("BOOL", "fact", lambda f, o: (not _none(f.get("F.req_byte"))
                                                      and int(f["F.req_byte"]) not in COMMON)),
    "req_set_size":    ("NUM",  "fact", lambda f, o: listlen(f.get("F.req_set"))),
    "start_set_size":  ("NUM",  "fact", lambda f, o: set_size(f.get("F.start_set"))),
    "start_set_one":   ("BOOL", "fact", lambda f, o: set_size(f.get("F.start_set")) == 1),
    "min_width":       ("NUM",  "fact", lambda f, o: (width(f.get("F.width")) or (0, 0))[0]),
    "fixed_width":     ("BOOL", "fact", lambda f, o: (lambda w: w is not None and w[0] == w[1])(width(f.get("F.width")))),
    "end_pinned":      ("BOOL", "fact", lambda f, o: not _none(f.get("F.end_pin"))),
    "has_kinds":       ("BOOL", "fact", lambda f, o: not _none(f.get("F.kinds"))),
    "land_char":       ("BOOL", "fact", lambda f, o: not _none(f.get("F.land_char"))),
    "kset_len":        ("NUM",  "fact", lambda f, o: listlen(f.get("F.kset_walk"))),
    "caseless":        ("BOOL", "option", lambda f, o: "-i" in o.split()),
    "utf":             ("BOOL", "option", lambda f, o: "utf8" in o or "--ucp" in o),
    "dflt_next_lit":   ("BOOL", "decision", lambda f, o: f.get("D.RX_DFA_PREFILTER", "").startswith(("run-pinned", "offset-set"))),
    "dflt_next_byte":  ("BOOL", "decision", lambda f, o: f.get("D.RX_DFA_PREFILTER", "").startswith(("memchr", "byte-class"))),
    "dflt_next_first": ("BOOL", "decision", lambda f, o: f.get("D.RX_DFA_PREFILTER", "").startswith("first-")
                                                         or f.get("D.RX_VM_START_SCAN", "none") != "none"),
    "dflt_presence":   ("BOOL", "decision", lambda f, o: f.get("D.RX_REQ_WHY") == "emitted"),
    "dflt_locate":     ("BOOL", "decision", lambda f, o: f.get("D.RX_DFA_SCAN") in ("rev-end", "cover")),
    "dflt_vm":         ("BOOL", "decision", lambda f, o: f.get("D.RX_ENGINE") == "vm"),
}

def values(facts, opts):
    out = {}
    for name, (_, _, fn) in PIECES.items():
        try:
            v = fn(facts, opts)
        except (ValueError, KeyError, IndexError):
            v = None
        out[name] = int(v) if isinstance(v, bool) else (v if v is not None else 0)
    return out

def load(facts_tsv, sites_tsv):
    opts = {r["id"]: r["flags"] for r in csv.DictReader(open(sites_tsv), delimiter="\t", quoting=csv.QUOTE_NONE)}
    res = {}
    for r in csv.DictReader(open(facts_tsv), delimiter="\t", quoting=csv.QUOTE_NONE):
        res[r["id"]] = values(json.loads(r["facts_json"]), opts.get(r["id"], "-"))
    return res

if __name__ == "__main__":
    v = load(sys.argv[1], sys.argv[2])
    names = list(PIECES)
    print("id\t" + "\t".join(names))
    for i in sorted(v):
        print(i + "\t" + "\t".join(str(v[i][n]) for n in names))
