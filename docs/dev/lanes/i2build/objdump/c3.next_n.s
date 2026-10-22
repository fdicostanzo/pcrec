 280:	endbr64
 284:	push   %r15
 286:	push   %r14
 288:	push   %r13
 28a:	push   %r12
 28c:	push   %rbp
 28d:	push   %rbx
 28e:	sub    $0x48,%rsp
 292:	mov    %rsi,0x8(%rsp)
 297:	mov    %rdx,0x18(%rsp)
 29c:	mov    %fs:0x28,%rax
 2a5:	mov    %rax,0x38(%rsp)
 2aa:	xor    %eax,%eax
 2ac:	test   %rdx,%rdx
 2af:	je     4b5 <rx_next_n+0x235>
 2b5:	mov    %rdi,%r12
 2b8:	xor    %r15d,%r15d
 2bb:	lea    0x0(%rip),%rbp        # 2c2 <rx_next_n+0x42>
			2be: R_X86_64_PC32	.rodata+0x45c
 2c2:	lea    0x0(%rip),%rbx        # 2c9 <rx_next_n+0x49>
			2c5: R_X86_64_PC32	.rodata+0x55c
 2c9:	mov    0x8(%rsp),%rdi
 2ce:	mov    %r15,%rax
 2d1:	lea    0x20(%rsp),%rdx
 2d6:	shl    $0x4,%rax
 2da:	add    %rdi,%rax
 2dd:	test   %rdi,%rdi
 2e0:	cmove  %rdx,%rax
 2e4:	mov    %rax,0x10(%rsp)
 2e9:	cmpl   $0x49540302,(%r12)
 2f1:	jne    4a0 <rx_next_n+0x220>
 2f7:	mov    0x18(%r12),%r8
 2fc:	mov    0x20(%r12),%rcx
 301:	cmp    %rcx,%r8
 304:	jb     488 <rx_next_n+0x208>
 30a:	mov    0x10(%r12),%rdi
 30f:	mov    %rcx,%r14
 312:	xor    %edx,%edx
 314:	xor    %eax,%eax
 316:	mov    $0xffffffffffffffff,%r9
 31d:	lea    0x0(%rip),%r13        # 324 <rx_next_n+0xa4>
			320: R_X86_64_PC32	.rodata+0x35c
 324:	lea    0x0(%rip),%r11        # 32b <rx_next_n+0xab>
			327: R_X86_64_PC32	.rodata+0x33c
 32b:	lea    0x0(%rip),%r10        # 332 <rx_next_n+0xb2>
			32e: R_X86_64_PC32	.rodata+0x23c
 332:	test   %dl,%dl
 334:	cmovne %rcx,%r9
 338:	test   $0x1,%al
 33a:	jne    346 <rx_next_n+0xc6>
 33c:	cmp    $0xffffffffffffffff,%r9
 340:	je     458 <rx_next_n+0x1d8>
 346:	cmp    %r8,%rcx
 349:	jae    3f0 <rx_next_n+0x170>
 34f:	movzbl (%rdi,%rcx,1),%edx
 353:	lea    0x1(%rcx),%rsi
 357:	movzbl 0x0(%r13,%rdx,1),%edx
 35d:	add    %edx,%eax
 35f:	mov    %eax,%eax
 361:	movzwl (%r11,%rax,2),%eax
 366:	cmp    $0x1,%ax
 36a:	jbe    3a0 <rx_next_n+0x120>
 36c:	cmp    $0xffff,%eax
 371:	je     3f0 <rx_next_n+0x170>
 373:	cmpb   $0x0,(%rbx,%rax,1)
 377:	cmovne %rsi,%r9
 37b:	cmp    $0x2,%eax
 37e:	jne    3e0 <rx_next_n+0x160>
 380:	cmp    %r8,%rsi
 383:	jae    3f0 <rx_next_n+0x170>
 385:	movzbl 0x1(%rdi,%rcx,1),%edx
 38a:	cmpb   $0x0,(%r10,%rdx,1)
 38f:	jne    3b0 <rx_next_n+0x130>
 391:	mov    %rsi,%rcx
 394:	jmp    34f <rx_next_n+0xcf>
 396:	cs nopw 0x0(%rax,%rax,1)
 3a0:	movzbl (%rbx,%rax,1),%edx
 3a4:	mov    %rsi,%rcx
 3a7:	jmp    332 <rx_next_n+0xb2>
 3a9:	nopl   0x0(%rax)
 3b0:	lea    0x2(%rcx),%rsi
 3b4:	cmp    %r8,%rsi
 3b7:	jb     3cd <rx_next_n+0x14d>
 3b9:	jmp    498 <rx_next_n+0x218>
 3be:	xchg   %ax,%ax
 3c0:	add    $0x1,%rsi
 3c4:	cmp    %r8,%rsi
 3c7:	jae    498 <rx_next_n+0x218>
 3cd:	movzbl (%rdi,%rsi,1),%eax
 3d1:	cmpb   $0x0,(%r10,%rax,1)
 3d6:	jne    3c0 <rx_next_n+0x140>
 3d8:	mov    %rsi,%r9
 3db:	mov    $0x2,%eax
 3e0:	cmp    %r8,%rsi
 3e3:	jb     391 <rx_next_n+0x111>
 3e5:	data16 cs nopw 0x0(%rax,%rax,1)
 3f0:	cmp    $0xffffffffffffffff,%r9
 3f4:	je     488 <rx_next_n+0x208>
 3fa:	mov    0x10(%rsp),%rax
 3ff:	cmp    %r9,%r14
 402:	mov    %r9,0x8(%rax)
 406:	mov    %r14,(%rax)
 409:	lea    0x1(%r14),%rax
 40d:	cmovge %rax,%r9
 411:	add    $0x1,%r15
 415:	mov    %r9,0x20(%r12)
 41a:	cmp    %r15,0x18(%rsp)
 41f:	jne    2c9 <rx_next_n+0x49>
 425:	data16 cs nopw 0x0(%rax,%rax,1)
 430:	mov    0x38(%rsp),%rax
 435:	sub    %fs:0x28,%rax
 43e:	jne    4bd <rx_next_n+0x23d>
 440:	add    $0x48,%rsp
 444:	mov    %r15,%rax
 447:	pop    %rbx
 448:	pop    %rbp
 449:	pop    %r12
 44b:	pop    %r13
 44d:	pop    %r14
 44f:	pop    %r15
 451:	ret
 452:	nopw   0x0(%rax,%rax,1)
 458:	cmp    %r8,%rcx
 45b:	jb     469 <rx_next_n+0x1e9>
 45d:	jmp    488 <rx_next_n+0x208>
 45f:	nop
 460:	add    $0x1,%rcx
 464:	cmp    %rcx,%r8
 467:	je     488 <rx_next_n+0x208>
 469:	movzbl (%rdi,%rcx,1),%edx
 46d:	cmpb   $0x0,0x0(%rbp,%rdx,1)
 472:	je     460 <rx_next_n+0x1e0>
 474:	cmp    %r8,%rcx
 477:	jae    488 <rx_next_n+0x208>
 479:	mov    %rcx,%r14
 47c:	jmp    34f <rx_next_n+0xcf>
 481:	nopl   0x0(%rax)
 488:	movq   $0x49540303,(%r12)
 490:	jmp    430 <rx_next_n+0x1b0>
 492:	nopw   0x0(%rax,%rax,1)
 498:	mov    %rsi,%r9
 49b:	jmp    3f0 <rx_next_n+0x170>
 4a0:	mov    %r12,%rdi
 4a3:	call   0 <rx__enter>
 4a8:	test   %eax,%eax
 4aa:	jne    2f7 <rx_next_n+0x77>
 4b0:	jmp    430 <rx_next_n+0x1b0>
 4b5:	xor    %r15d,%r15d
 4b8:	jmp    430 <rx_next_n+0x1b0>
 4bd:	call   4c2 <rx_next_n+0x242>
			4be: R_X86_64_PLT32	__stack_chk_fail-0x4
 4c2:	nopl   (%rax)
 4c5:	data16 cs nopw 0x0(%rax,%rax,1)

