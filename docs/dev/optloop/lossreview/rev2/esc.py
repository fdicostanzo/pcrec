import sys
b=open(sys.argv[1],'rb').read().rstrip(b"\n")
o=[]
for c in b:
    if c==0x5c:o.append("\\\\")
    elif c==0x22:o.append('\\"')
    elif 0x20<=c<0x7f:o.append(chr(c))
    else:o.append("\\x%02x"%c)
print('"'+"".join(o)+'"',end="")
