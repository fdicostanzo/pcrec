#!/usr/bin/env python3
"""p910 P10 controls: every BENCH pattern whose auto artifact declines the
presence check on the one-attempt row (census: REQ_WHY one-attempt, a
REQ_BYTE), its auto artifact and the two mechanical twins (`pre`, `paced`,
mk_p10_twins.py), find-all over its OWN set's subjects (subjects/ +
throughput/), instructions:u + span hash per file. Writes OUT (tsv rows:
id, variant, file, len, count, hash, instr, cycles). Env: PCREC, BENCH, S
(scratch dir with census.tsv, drv.c, mk_p10_twins.py), OUT."""
import glob, os, subprocess, sys

E = os.environ
PCREC, BENCH, S, OUT = E["PCREC"], E["BENCH"], E["S"], E["OUT"]
TO = ["/usr/bin/gnutimeout", "-k", "2"]
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(S, "census.tsv"))]
h = rows[0]
sel = []
for r in rows[1:]:
    d = dict(zip(h, r))
    if d["pop"] == "bench" and not d["refused"] and d["REQ_WHY"] == "one-attempt" and d["REQ_BYTE"] not in ("none", "-"):
        sel.append(d)
print("one-attempt bench patterns with a req byte:", len(sel), file=sys.stderr)
work = os.path.join(S, "p10c")
os.makedirs(work, exist_ok=True)
with open(OUT, "w") as out:
    for d in sel:
        sb, name = d["id"].split("/", 1)
        dd = os.path.join(work, d["id"].replace("/", "__") + "-auto")
        os.makedirs(dd, exist_ok=True)
        pat = bytes.fromhex(d["pat_hex"])
        cmd = TO + ["60", PCREC, "--features", "all", "-p", "rx", "-o", os.path.join(dd, "rx.c")]
        if d["enc"] == "utf8":
            cmd += ["-e", "utf8"]
        if d.get("icase") == "1":
            pat = b"(?i)" + pat
        if subprocess.run(cmd + ["--pattern", pat], capture_output=True).returncode:
            out.write(f"{d['id']}\t-\tCOMPILE-FAIL\n"); continue
        t = subprocess.run(["python3", "-I", os.path.join(S, "mk_p10_twins.py"), dd], capture_output=True)
        if t.returncode:
            out.write(f"{d['id']}\t-\tNO-TWIN\t{t.stderr.decode()[-200:].strip().splitlines()[-1]}\n"); continue
        files = sorted(glob.glob(os.path.join(BENCH, "bench", sb, "subjects", "*.bin")) +
                       glob.glob(os.path.join(BENCH, "bench", sb, "throughput", "*.bin")))
        for v, vd in (("auto", dd), ("pre", dd + "-pre"), ("paced", dd + "-paced")):
            exe = os.path.join(vd, "drv")
            b = subprocess.run(["gcc", "-O2", "-w", "-DART=" + vd, "-I" + vd, "-o", exe, os.path.join(S, "drv.c")],
                               capture_output=True)
            if b.returncode:
                out.write(f"{d['id']}\t{v}\tBUILD-FAIL\n"); continue
            p = subprocess.run(["taskset", "-c", "7"] + TO + ["600", exe, "5"] + files, capture_output=True)
            for ln in p.stdout.decode().splitlines():
                f = ln.split("\t")
                if f[0] != "TOTAL":
                    out.write(f"{d['id']}\t{v}\t" + ln + "\n")
        out.flush()
