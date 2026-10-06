import sys
src=open(sys.argv[1],'rb').read()
rec=b'\nkey=1&mid=2&key=3\n'
# sparse: one record at 3/4 of the subject, same length
def put(buf, every):
    b=bytearray(buf); n=len(b); pos=every
    cnt=0
    while pos+len(rec)<n:
        b[pos:pos+len(rec)]=rec; pos+=every; cnt+=1
    return bytes(b),cnt
sp,cs=put(src,len(src)*3//4)
de,cd=put(src,4096)
open(sys.argv[2],'wb').write(sp); open(sys.argv[3],'wb').write(de)
print('sparse records',cs,'dense records',cd,len(sp),len(de))
