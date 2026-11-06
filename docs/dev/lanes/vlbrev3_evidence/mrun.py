import sys
sys.path.insert(0, sys.argv[1]); import model
for line in sys.stdin:
    f = line.rstrip("\n").split("\t")
    if len(f) > 2: print("%s\t%s\tn/a (startpos)" % (f[0], f[1])); continue
    out = []
    for mode in ("cursor", "range"):
        try: out.append(model.run(mode, f[0], f[1]))
        except Exception as e: out.append("n/a (%s)" % e)
    print("%s\t%s\t%s\t%s" % (f[0], f[1], out[0], out[1]))
