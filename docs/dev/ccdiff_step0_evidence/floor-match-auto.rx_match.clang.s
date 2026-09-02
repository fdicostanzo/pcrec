00000000000022d0 <rx_match>:
    22d0:	mov    0x8(%rdi),%rdx
    22d4:	mov    0x10(%rdi),%rcx
    22d8:	mov    $0xffffffffffffffff,%rax
    22df:	cmp    %rdx,%rcx
    22e2:	ja     237f <rx_match+0xaf>
    22e8:	push   %rbp
    22e9:	push   %r14
    22eb:	push   %rbx
    22ec:	mov    (%rdi),%rax
    22ef:	xor    %edi,%edi
    22f1:	mov    $0xffffffffffffffff,%rsi
    22f8:	lea    0xe33(%rip),%r8        # 3132 <rx_match.rx_anchored_end_view>
    22ff:	lea    0xe26(%rip),%r9        # 312c <rx_match.rx_anchored_is_accepting>
    2306:	lea    0xd13(%rip),%r10        # 3020 <rx_match.rx_anchored_byte_class>
    230d:	lea    0xe0c(%rip),%r11        # 3120 <rx_match.rx_anchored_next_state>
    2314:	mov    %rcx,%rbx
    2317:	nopw   0x0(%rax,%rax,1)
    2320:	cmp    %rbx,%rdx
    2323:	je     2354 <rx_match+0x84>
    2325:	mov    %edi,%r14d
    2328:	cmpb   $0x0,(%r14,%r9,1)
    232d:	cmovne %rbx,%rsi
    2331:	cmp    %rbx,%rdx
    2334:	je     236d <rx_match+0x9d>
    2336:	movzbl (%rax,%rbx,1),%r14d
    233b:	inc    %rbx
    233e:	movzbl (%r14,%r10,1),%ebp
    2343:	add    %ebp,%edi
    2345:	movzwl (%r11,%rdi,2),%edi
    234a:	cmp    $0xffff,%edi
    2350:	jne    2320 <rx_match+0x50>
    2352:	jmp    236d <rx_match+0x9d>
    2354:	mov    %edi,%r14d
    2357:	and    $0xfffffffe,%r14d
    235b:	movzwl (%r14,%r8,1),%ebp
    2360:	cmp    $0xffff,%ebp
    2366:	cmove  %edi,%ebp
    2369:	mov    %ebp,%edi
    236b:	jmp    2325 <rx_match+0x55>
    236d:	mov    %rsi,%rax
    2370:	sub    %rcx,%rax
    2373:	cmp    $0xffffffffffffffff,%rsi
    2377:	cmove  %rsi,%rax
    237b:	pop    %rbx
    237c:	pop    %r14
    237e:	pop    %rbp
    237f:	ret

