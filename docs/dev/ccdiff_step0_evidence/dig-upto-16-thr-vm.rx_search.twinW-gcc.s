0000000000002330 <rx_search>:
    2330:	endbr64
    2334:	sub    $0x68,%rsp
    2338:	mov    %fs:0x28,%rax
    2341:	mov    %rax,0x58(%rsp)
    2346:	xor    %eax,%eax
    2348:	mov    %rsp,%r8
    234b:	movq   $0x0,0x10(%rsp)
    2354:	movq   $0x0,0x18(%rsp)
    235d:	movq   $0x0,0x20(%rsp)
    2366:	movq   $0x0,0x28(%rsp)
    236f:	call   2250 <rx_search_run>
    2374:	mov    0x58(%rsp),%rdx
    2379:	sub    %fs:0x28,%rdx
    2382:	jne    2389 <rx_search+0x59>
    2384:	add    $0x68,%rsp
    2388:	ret
    2389:	call   20b0 <__stack_chk_fail@plt>
    238e:	xchg   %ax,%ax

