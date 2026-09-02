0000000000002440 <rx_match>:
    2440:	endbr64
    2444:	mov    %rdi,%rax
    2447:	mov    0x8(%rdi),%rdi
    244b:	mov    0x10(%rax),%r11
    244f:	cmp    %r11,%rdi
    2452:	jb     24eb <rx_match+0xab>
    2458:	push   %rbx
    2459:	mov    %r11,%rcx
    245c:	mov    (%rax),%rbx
    245f:	xor    %esi,%esi
    2461:	mov    $0xffffffffffffffff,%rax
    2468:	lea    0xd91(%rip),%r8        # 3200 <rx_anchored_is_accepting.2>
    246f:	lea    0xc8a(%rip),%r10        # 3100 <rx_anchored_byte_class.1>
    2476:	lea    0xc5b(%rip),%r9        # 30d8 <rx_anchored_next_state.0>
    247d:	jmp    24aa <rx_match+0x6a>
    247f:	nop
    2480:	mov    %esi,%edx
    2482:	cmpb   $0x0,(%r8,%rdx,1)
    2487:	cmovne %rcx,%rax
    248b:	add    $0x1,%rcx
    248f:	movzbl -0x1(%rbx,%rcx,1),%edx
    2494:	movzbl (%r10,%rdx,1),%edx
    2499:	add    %esi,%edx
    249b:	mov    %edx,%edx
    249d:	movzwl (%r9,%rdx,2),%esi
    24a2:	cmp    $0xffff,%esi
    24a8:	je     24cd <rx_match+0x8d>
    24aa:	cmp    %rdi,%rcx
    24ad:	jne    2480 <rx_match+0x40>
    24af:	mov    %esi,%edi
    24b1:	lea    0xd4e(%rip),%rdx        # 3206 <rx_anchored_end_view.3>
    24b8:	shr    $1,%edi
    24ba:	movzwl (%rdx,%rdi,2),%edx
    24be:	cmp    $0xffff,%dx
    24c2:	je     24e0 <rx_match+0xa0>
    24c4:	cmpb   $0x0,(%r8,%rdx,1)
    24c9:	cmovne %rcx,%rax
    24cd:	cmp    $0xffffffffffffffff,%rax
    24d1:	je     24f3 <rx_match+0xb3>
    24d3:	sub    %r11,%rax
    24d6:	pop    %rbx
    24d7:	ret
    24d8:	nopl   0x0(%rax,%rax,1)
    24e0:	cmpb   $0x0,(%r8,%rsi,1)
    24e5:	cmovne %rcx,%rax
    24e9:	jmp    24cd <rx_match+0x8d>
    24eb:	mov    $0xffffffffffffffff,%rax
    24f2:	ret
    24f3:	mov    $0xffffffffffffffff,%rax
    24fa:	pop    %rbx
    24fb:	ret
    24fc:	nopl   0x0(%rax)

