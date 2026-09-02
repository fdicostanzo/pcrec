0000000000002220 <rx_search>:
    2220:	endbr64
    2224:	sub    $0x68,%rsp
    2228:	mov    %fs:0x28,%r8
    2231:	mov    %r8,0x58(%rsp)
    2236:	mov    %rsp,%r8
    2239:	call   21c0 <rx_search_run>
    223e:	mov    0x58(%rsp),%rdx
    2243:	sub    %fs:0x28,%rdx
    224c:	jne    2253 <rx_search+0x33>
    224e:	add    $0x68,%rsp
    2252:	ret
    2253:	call   20b0 <__stack_chk_fail@plt>
    2258:	nopl   0x0(%rax,%rax,1)

