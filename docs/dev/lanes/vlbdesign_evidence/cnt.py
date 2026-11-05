import re,sys
t=open(sys.argv[1]).read()
m=re.search(r'rx_reverse_byte_class\[256\]\s*=\s*\{([^}]*)\}',t)
if not m: print("no reverse machine"); sys.exit()
nc=max(int(x) for x in re.findall(r'\d+',m.group(1)))+1
n=int(re.search(r'rx_reverse_next_state\[(\d+)\]',t).group(1))
print(f"classes={nc} next_entries={n} states~={n/nc:.1f}")
