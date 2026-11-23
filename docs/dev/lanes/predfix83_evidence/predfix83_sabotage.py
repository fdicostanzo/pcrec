import os, re, subprocess, sys
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "predfix83_model.py")
TARGET = {1: "CONTROL", 2: "AMBOUT", 3: "BAREAMB", 4: "LISTCALL", 5: "OUTSIDE", 6: "OWNUSE", 7: "TWOUSE", 8: "EXPR",
          9: "PARAM", 10: "ARGOWN", 11: "LISTCOLL", 12: "EXAMPLE", 13: "SETAND", 14: "VISIBLE", 15: "GRID", 16: "SWEEP",
          17: "SUCCESSOR", 18: "NULLABLE", 19: "QUOTES", 20: "MARKS", 21: "DOC", 22: "AWAITS", 23: "UNMARKED",
          24: "TOPLEVEL", 25: "WITNESS"}
bad = 0
for n, t in TARGET.items():
    env = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE")}
    env["PREDFIX83_SABOTAGE"] = "s%d" % n
    p = subprocess.run([sys.executable, "-I", "-B", F], capture_output=True, text=True, env=env, timeout=1500)
    out = p.stdout + p.stderr
    last = out.rstrip("\n").split("\n")[-1]
    tb = "Traceback" in out
    fl = next((l for l in out.split("\n") if l.startswith("FAIL %s:" % t)), "")
    ok = (not tb) and bool(fl) and p.returncode != 0
    bad += not ok
    print("s%-2d -> %-9s %s rc=%d traceback=%s" % (n, t, "CAUGHT" if ok else "NOT CAUGHT", p.returncode, tb))
    print("     last line: %s" % last)
    print("     its FAIL line: %s" % fl[:400])
print("predfix83 sabotage: %d plants, %d not caught by their target" % (len(TARGET), bad))
