 3a0:	endbr64
 3a4:	push   %r15
 3a6:	push   %r14
 3a8:	push   %r13
 3aa:	push   %r12
 3ac:	push   %rbp
 3ad:	push   %rbx
 3ae:	sub    $0x78,%rsp
 3b2:	mov    %fs:0x28,%rax
 3bb:	mov    %rax,0x68(%rsp)
 3c0:	xor    %eax,%eax
 3c2:	test   %rdx,%rdx
 3c5:	je     598 <rx_next_n+0x1f8>
 3cb:	mov    %rdi,%rbx
 3ce:	mov    %rsi,%r13
 3d1:	mov    %rdx,%r14
 3d4:	xor    %r12d,%r12d
 3d7:	lea    0x40(%rsp),%r15
 3dc:	mov    %r12,%rax
 3df:	shl    $0x5,%rax
 3e3:	add    %r13,%rax
 3e6:	test   %r13,%r13
 3e9:	cmove  %r15,%rax
 3ed:	mov    %rax,%rbp
 3f0:	cmpl   $0x49540302,(%rbx)
 3f6:	jne    580 <rx_next_n+0x1e0>
 3fc:	mov    0x38(%rbx),%rax
 400:	mov    0x10(%rbx),%rdi
 404:	mov    0x18(%rbx),%rsi
 408:	mov    0x20(%rbx),%rdx
 40c:	test   %rax,%rax
 40f:	je     4f8 <rx_next_n+0x158>
 415:	cmp    %rdx,%rsi
 418:	jae    450 <rx_next_n+0xb0>
 41a:	xor    %eax,%eax
 41c:	mov    %rdx,0x20(%rbx)
 420:	mov    %eax,0x4(%rbx)
 423:	movl   $0x49540303,(%rbx)
 429:	mov    0x68(%rsp),%rax
 42e:	sub    %fs:0x28,%rax
 437:	jne    5d3 <rx_next_n+0x233>
 43d:	add    $0x78,%rsp
 441:	mov    %r12,%rax
 444:	pop    %rbx
 445:	pop    %rbp
 446:	pop    %r12
 448:	pop    %r13
 44a:	pop    %r14
 44c:	pop    %r15
 44e:	ret
 44f:	nop
 450:	mov    0x18(%rax),%rcx
 454:	mov    0x10(%rax),%r8
 458:	mov    %rdx,0x18(%rsp)
 45d:	mov    %rsi,0x10(%rsp)
 462:	mov    %rcx,0x28(%rsp)
 467:	lea    0x30(%rsp),%rcx
 46c:	mov    %r8,0x20(%rsp)
 471:	mov    %rdi,0x8(%rsp)
 476:	call   80 <rx_prefilter>
 47b:	mov    0x8(%rsp),%rdi
 480:	mov    0x10(%rsp),%rsi
 485:	cmp    $0x1,%eax
 488:	mov    0x18(%rsp),%rdx
 48d:	mov    0x20(%rsp),%r8
 492:	jne    41a <rx_next_n+0x7a>
 494:	mov    0x30(%rsp),%rax
 499:	cmpq   $0x0,0x28(%rsp)
 49f:	je     5b8 <rx_next_n+0x218>
 4a5:	movl   $0x2,(%r8)
 4ac:	mov    %rax,%rcx
 4af:	movq   $0xffffffffffffffff,0x8(%r8)
 4b7:	cmp    %rsi,%rax
 4ba:	jae    41a <rx_next_n+0x7a>
 4c0:	movzbl (%rdi,%rcx,1),%r9d
 4c5:	add    $0x1,%rcx
 4c9:	cmp    $0x61,%r9b
 4cd:	jne    5a0 <rx_next_n+0x200>
 4d3:	cmpq   $0x1,0x28(%rsp)
 4d9:	je     5b8 <rx_next_n+0x218>
 4df:	movl   $0x3,0x10(%r8)
 4e7:	lea    0x1(%rax),%rdx
 4eb:	movq   $0xffffffffffffffff,0x18(%r8)
 4f3:	jmp    559 <rx_next_n+0x1b9>
 4f5:	nopl   (%rax)
 4f8:	cmp    %rdx,%rsi
 4fb:	jb     41a <rx_next_n+0x7a>
 501:	lea    0x30(%rsp),%rcx
 506:	mov    %rdx,0x18(%rsp)
 50b:	mov    %rsi,0x10(%rsp)
 510:	mov    %rdi,0x8(%rsp)
 515:	call   80 <rx_prefilter>
 51a:	mov    0x8(%rsp),%rdi
 51f:	mov    0x10(%rsp),%rsi
 524:	cmp    $0x1,%eax
 527:	mov    0x18(%rsp),%rdx
 52c:	jne    41a <rx_next_n+0x7a>
 532:	mov    0x30(%rsp),%rax
 537:	mov    %rax,%r8
 53a:	cmp    %rsi,%rax
 53d:	jae    41a <rx_next_n+0x7a>
 543:	movzbl (%rdi,%r8,1),%r9d
 548:	add    $0x1,%r8
 54c:	mov    %r8,%rcx
 54f:	cmp    $0x61,%r9b
 553:	jne    5c2 <rx_next_n+0x222>
 555:	lea    0x1(%rax),%rdx
 559:	add    $0x1,%r12
 55d:	mov    %rax,0x0(%rbp)
 561:	mov    %rdx,0x8(%rbp)
 565:	mov    %rax,0x10(%rbp)
 569:	mov    %rcx,0x18(%rbp)
 56d:	mov    %rdx,0x20(%rbx)
 571:	cmp    %r12,%r14
 574:	jne    3dc <rx_next_n+0x3c>
 57a:	jmp    429 <rx_next_n+0x89>
 57f:	nop
 580:	mov    %rbx,%rdi
 583:	call   0 <rx__enter>
 588:	test   %eax,%eax
 58a:	jne    3fc <rx_next_n+0x5c>
 590:	jmp    429 <rx_next_n+0x89>
 595:	nopl   (%rax)
 598:	xor    %r12d,%r12d
 59b:	jmp    429 <rx_next_n+0x89>
 5a0:	mov    %rcx,%rax
 5a3:	cmp    %rsi,%rcx
 5a6:	jb     4c0 <rx_next_n+0x120>
 5ac:	jmp    41a <rx_next_n+0x7a>
 5b1:	nopl   0x0(%rax)
 5b8:	mov    $0xfffffffd,%eax
 5bd:	jmp    41c <rx_next_n+0x7c>
 5c2:	cmp    %rsi,%r8
 5c5:	jae    41a <rx_next_n+0x7a>
 5cb:	mov    %r8,%rax
 5ce:	jmp    543 <rx_next_n+0x1a3>
 5d3:	call   5d8 <rx_next_n+0x238>
			5d4: R_X86_64_PLT32	__stack_chk_fail-0x4
 5d8:	nopl   0x0(%rax,%rax,1)

