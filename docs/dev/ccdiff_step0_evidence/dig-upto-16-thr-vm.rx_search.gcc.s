0000000000002330 <rx_search>:
    2330:	endbr64
    2334:	sub    $0x98,%rsp
    233b:	mov    %fs:0x28,%rax
    2344:	mov    %rax,0x88(%rsp)
    234c:	xor    %eax,%eax
    234e:	lea    0x30(%rsp),%r8
    2353:	lea    0x18(%rsp),%rax
    2358:	mov    %rsp,0x40(%rsp)
    235d:	movq   $0x1,0x48(%rsp)
    2366:	mov    %rax,0x50(%rsp)
    236b:	movq   $0x1,0x58(%rsp)
    2374:	call   2250 <rx_search_run>
    2379:	mov    0x88(%rsp),%rdx
    2381:	sub    %fs:0x28,%rdx
    238a:	jne    2394 <rx_search+0x64>
    238c:	add    $0x98,%rsp
    2393:	ret
    2394:	call   20b0 <__stack_chk_fail@plt>
    2399:	nopl   0x0(%rax)

