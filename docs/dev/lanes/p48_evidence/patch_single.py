# p48: the SINGLETON twin (scanedge.c): pre-[SCANEDGE-SET] admission, a scan
# set of exactly one byte class.
import sys
p = sys.argv[1] + '/src/opt/scanedge.c'
t = open(p).read()
old = """        if (tr[c] == tr[cls]) {
            if (c < cls) return false;               /* not the set's key */
            continue;
        }"""
new = """        if (tr[c] == tr[cls]) {
            if (c != cls) return false;   /* P48 TWIN: singleton sets only */
            continue;
        }"""
assert t.count(old) == 1
open(p, 'w').write(t.replace(old, new))
