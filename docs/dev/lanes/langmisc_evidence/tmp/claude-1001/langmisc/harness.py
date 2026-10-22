"""Differential harness: pcrec (cell build) vs libpcre2 10.46.
usage: python3 -I harness.py probes_X.py [...]  -> appends results/*.jsonl, prints divergences"""
import sys, os, subprocess, json, hashlib, concurrent.futures as cf, runpy
CELL = "/home/pcrec/projects/pcrec/worktrees/langmisc-cell"
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
PCREC = os.path.join(CELL, "build/pcrec")

ENC=["byte"]
def b(x, enc=None):
    if isinstance(x, bytes): return x
    return x.encode("utf-8" if (enc or ENC[0])=="utf8" else "latin-1")

def norm_subj(s, enc="byte"):
    if isinstance(s, tuple): return (b(s[0], enc), s[1])
    return (b(s, enc), 0)

def run(cmd, t=60):
    try:
        r = subprocess.run(["timeout", str(t)] + cmd, capture_output=True)
        return r.returncode, r.stdout.decode("latin-1"), r.stderr.decode("latin-1")
    except Exception as e:
        return 99, "", str(e)

def pcrec_side(p, d):
    pat = b(p["pat"], p.get("enc","byte"))
    args = [PCREC, "-p", "rx", "-o", os.path.join(d, "rx.c")]
    if p.get("enc", "byte") == "utf8": args += ["-e", "utf8"]
    if p.get("i"): args.append("-i")
    if p.get("ucp"): args.append("--ucp")
    if p.get("feats") is not None: args += ["--features", p["feats"]]
    args += p.get("extra", [])
    if any(c >= 0x80 or c < 0x20 for c in pat) or p.get("esc"):
        e = "".join("\\\\" if c == 0x5c else '\\"' if c == 0x22 else chr(c) if 0x20 <= c < 0x7f else "\\x%02x" % c for c in pat)
        args += ["--pattern-esc", "--pattern", '"' + e + '"']
    else:
        args += ["--pattern", pat]
    rc, out, err = run(args)
    if rc != 0 or not os.path.exists(os.path.join(d, "rx.c")):
        return {"refused": True, "rc": rc, "msg": (err + out).strip()[:400]}
    rc, out, err = run(["gcc", "-O1", "-w", "-I", d, '-DRXH="rx.h"', "-o", os.path.join(d, "a.out"),
                        os.path.join(HERE, "drv.c"), os.path.join(d, "rx.c")], 120)
    if rc != 0:
        return {"refused": False, "cc_error": err[:600]}
    subj = [norm_subj(s, p.get("enc","byte")) for s in p.get("subj", [])]
    rc, out, err = run([os.path.join(d, "a.out")] + ["%d:%s" % (sp, s.hex()) for s, sp in subj], 30)
    lines = out.strip().split("\n")
    return {"refused": False, "rc": rc, "ncap": int(lines[0].split()[1]) if lines and lines[0].startswith("OK") else None,
            "res": lines[1:], "err": err[-300:] if rc != 0 else ""}

def pcre2_side(p):
    f = ""
    if p.get("enc", "byte") == "utf8": f += "u"
    if p.get("i"): f += "i"
    if p.get("ucp"): f += "p"
    f += p.get("p2flags", "")
    pat = b(p.get("p2pat", p["pat"]), p.get("enc","byte"))
    subj = [norm_subj(s, p.get("enc","byte")) for s in p.get("subj", [])]
    rc, out, err = run([os.path.join(HERE, "p2probe"), f or "-", pat.hex()] + ["%d:%s" % (sp, s.hex()) for s, sp in subj])
    lines = out.strip().split("\n")
    if lines[0].startswith("ERR"):
        return {"refused": True, "msg": lines[0]}
    return {"refused": False, "ncap": int(lines[0].split()[1]), "res": lines[1:]}

def cmp(p, a, o):
    """verdict: AGREE, BOTH-REFUSE, PCREC-REFUSE, PCREC-ACCEPT, DIFF, GIVEUP, CRASH, CCERR"""
    if not a["refused"] and a.get("cc_error"): return "CCERR"
    if a["refused"] and o["refused"]: return "BOTH-REFUSE"
    if a["refused"]: return "PCREC-REFUSE"
    if a.get("rc", 0) != 0: return "CRASH"
    if o["refused"]: return "PCREC-ACCEPT"
    nocap = "--no-captures" in p.get("extra", [])
    if not nocap and a["ncap"] != o["ncap"]: return "DIFF"
    for x, y in zip(a["res"], o["res"]):
        if x.startswith("E "): 
            if x != y: return "GIVEUP"
            continue
        if nocap and x.startswith("M") and y.startswith("M"):
            if x.split()[1:3] != y.split()[1:3]: return "DIFF"
            continue
        if x != y: return "DIFF"
    if len(a["res"]) != len(o["res"]): return "DIFF"
    return "AGREE"

def one(p):
    key = hashlib.sha1(json.dumps({k: (v.hex() if isinstance(v, bytes) else v) for k, v in p.items()
                                   if k != "subj"}, sort_keys=True, default=str).encode()).hexdigest()[:12]
    d = os.path.join(WORK, key); os.makedirs(d, exist_ok=True)
    a = pcrec_side(p, d); o = pcre2_side(p)
    v = cmp(p, a, o)
    return p, a, o, v

def main():
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    for f in sys.argv[1:]:
        probes = runpy.run_path(f)["PROBES"]
        name = os.path.splitext(os.path.basename(f))[0]
        out = open(os.path.join(HERE, "results", name + ".jsonl"), "w")
        with cf.ThreadPoolExecutor(6) as ex:
            for p, a, o, v in ex.map(one, probes):
                rec = {"id": p.get("id"), "pat": b(p["pat"], p.get("enc","byte")).decode("latin-1"), "opts": {k: p[k] for k in ("enc","i","ucp","feats","extra","p2flags") if k in p},
                       "subj": [(s.decode("latin-1"), sp) for s, sp in [norm_subj(x, p.get("enc","byte")) for x in p.get("subj", [])]],
                       "pcrec": a, "pcre2": o, "verdict": v, "note": p.get("note", ""), "expect": p.get("expect")}
                out.write(json.dumps(rec) + "\n")
                exp = p.get("expect")
                flag = v not in ("AGREE", "BOTH-REFUSE") or (exp and exp != v)
                tag = "!!" if flag else "  "
                print(f"{tag} {v:13} {p.get('id','')} {rec['pat']!r} {rec['opts']}")
                if flag:
                    print("     pcrec:", json.dumps({k: a.get(k) for k in ('msg','res','ncap','err','cc_error') if a.get(k) is not None})[:500])
                    print("     pcre2:", json.dumps({k: o.get(k) for k in ('msg','res','ncap') if o.get(k) is not None})[:500])
                    if p.get("note"): print("     note:", p["note"])
main()
