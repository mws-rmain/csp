/*******************************************************************************
* Copyright (C) 2019 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*******************************************************************************/

#ifndef TOOLCHAIN_SPECIFICS_H
#define TOOLCHAIN_SPECIFICS_H

#ifdef __cplusplus  // Provide C++ Compatibility
extern "C" {
#endif

<#if CoreArchitecture?contains("ARM926")>

    <#lt>#ifndef __NOP
    <#lt>#define __NOP __arm926_nop
    <#lt>static inline void __arm926_nop(void)
    <#lt>{
    <#lt>    asm("nop");
    <#lt>}
    <#lt>#endif //__NOP

    <#lt>static inline void __disable_irq( void )
    <#lt>{   // read, modify and write back the CPSR
    <#lt>    asm("MRS r0, cpsr");
    <#lt>    asm("ORR r0, r0, #0xC0");
    <#lt>    asm("MSR cpsr_c, r0");
    <#lt>}

    <#lt>static inline void __enable_irq( void )
    <#lt>{   // read, modify and write back the CPSR
    <#lt>    asm("MRS r0, cpsr");
    <#lt>    asm("BIC r0, r0, #0x80");
    <#lt>    asm("MSR cpsr_c, r0");
    <#lt>}

    <#lt>#ifndef __DMB
    <#lt>#define __DMB    __arm926_dmb
    <#lt>static inline void __arm926_dmb(void)
    <#lt>{
    <#lt>    asm("" ::: "memory");
    <#lt>}
    <#lt>#endif //__DMB

    <#lt>#ifndef __DSB
    <#lt>#define __DSB    __arm926_dsb
    <#lt>static inline void __arm926_dsb(void)
    <#lt>{
    <#lt>    asm("mcr p15, 0, %0, c7, c10, 4" :: "r"(0) : "memory");
    <#lt>}
    <#lt>#endif //__DSB

    <#lt>#ifndef __ISB
    <#lt>#define __ISB __arm926_isb
    <#lt>static inline void __arm926_isb(void)
    <#lt>{
    <#lt>    asm("" ::: "memory");
    <#lt>}
    <#lt>#endif //__ISB

    <#if COMPILER_CHOICE == "IAR" || CoreArchitecture?contains("ARM926")>
        <#lt>#define __ALIGNED(x) __attribute__((aligned(x)))
    </#if>

    <#lt>#ifndef __STATIC_INLINE
    <#lt>#define __STATIC_INLINE static inline
    <#lt>#endif //__STATIC_INLINE

    <#lt>#ifndef   __WEAK
    <#lt>#define __WEAK __attribute__((weak))
    <#lt>#endif // __WEAK
</#if>
<#if "XC32" == COMPILER_CHOICE>
    <#if CoreArchitecture?contains("ARM926") == false >
        <#lt>#pragma GCC diagnostic push
        <#lt>#ifndef __cplusplus
        <#lt>   #pragma GCC diagnostic ignored "-Wnested-externs"
        <#lt>#endif
        <#lt>#pragma GCC diagnostic ignored "-Wsign-conversion"
        <#lt>#pragma GCC diagnostic ignored "-Wattributes"
        <#lt>#pragma GCC diagnostic ignored "-Wundef"
        <#lt>#include "cmsis_compiler.h"
        <#lt>#pragma GCC diagnostic pop

    </#if>
    <#lt>#include <sys/types.h>

    <#lt>#define NO_INIT        __attribute__((section(".no_init")))
    <#lt>#define SECTION(a)     __attribute__((__section__(a)))
    <#if CACHE_ALIGN?? >

        <#lt>#define CACHE_LINE_SIZE    (${CACHE_ALIGN}u)
        <#lt>#define CACHE_ALIGN        __ALIGNED(CACHE_LINE_SIZE)
    <#else>

        <#lt>#define CACHE_LINE_SIZE    (4u)
        <#lt>#define CACHE_ALIGN
    </#if>

	<#lt>#define CACHE_ALIGNED_SIZE_GET(size)     (size + ((size % CACHE_LINE_SIZE)? (CACHE_LINE_SIZE - (size % CACHE_LINE_SIZE)) : 0))
	
    <#lt>#ifndef FORMAT_ATTRIBUTE
    <#lt>   #define FORMAT_ATTRIBUTE(archetype, string_index, first_to_check)  __attribute__ ((format (archetype, string_index, first_to_check)))
    <#lt>#endif

<#elseif "IAR" == COMPILER_CHOICE>
    <#if CoreArchitecture?contains("ARM926") == false >
        <#lt>#include "cmsis_compiler.h"
    </#if>
    <#lt>#include <stdint.h>

    <#lt>#define COMPILER_PRAGMA(arg)            _Pragma(#arg)
    <#lt>#define SECTION(a)                      COMPILER_PRAGMA(location = a)
    <#lt>#define NO_INIT                         __no_init

    <#lt>#define __inline__                      inline

    <#lt>#ifndef _SSIZE_T_DECLARED
    <#lt>#ifdef __SIZE_T_TYPE__
    <#lt>/* If __SIZE_T_TYPE__ is defined (IAR) we define ssize_t based on size_t.
    <#lt>We simply change "unsigned" to "signed" for this single definition
    <#lt>to make sure ssize_t and size_t only differ by their signedness. */
    <#lt>#define unsigned signed
    <#lt>typedef __SIZE_T_TYPE__ _ssize_t;
    <#lt>#undef unsigned
    <#lt>#else
    <#lt>#if defined(__INT_MAX__) && __INT_MAX__ == 2147483647
    <#lt>typedef int _ssize_t;
    <#lt>#else
    <#lt>typedef long _ssize_t;
    <#lt>#endif
    <#lt>#endif
    <#lt>typedef _ssize_t ssize_t;
    <#lt>#define    _SSIZE_T_DECLARED
    <#lt>#endif
    <#if CACHE_ALIGN?? >

        <#lt>#define CACHE_LINE_SIZE                 (${CACHE_ALIGN}u)
        <#lt>#define CACHE_ALIGN                     __ALIGNED(CACHE_LINE_SIZE)
    <#else>

        <#lt>#define CACHE_LINE_SIZE                 (4u)
        <#lt>#define CACHE_ALIGN
    </#if>

	<#lt>#define CACHE_ALIGNED_SIZE_GET(size)     (size + ((size % CACHE_LINE_SIZE)? (CACHE_LINE_SIZE - (size % CACHE_LINE_SIZE)) : 0))
	
    <#lt>#ifndef FORMAT_ATTRIBUTE
    <#lt>   #define FORMAT_ATTRIBUTE(archetype, string_index, first_to_check)
    <#lt>#endif

    <#lt>// Usually defined in errno.h, include extended E codes not provided in IAR errno.h
    <#lt>// H3_IAR_ERRNO
    <#lt>extern __attribute__((section(".bss.errno"))) int errno;

    <#lt>/*
    <#lt> * List of system errors numbers from:
    <#lt> *
    <#lt> *    The Open Group Base Specifications Issue 7
    <#lt> *    IEEE Std 1003.1-2008, 2016 Edition
    <#lt> *    http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/errno.h.html
    <#lt> */
    <#lt>#define E2BIG           ( 1) /* Argument list too long */
    <#lt>#define EACCES          ( 2) /* Permission denied */
    <#lt>#define EADDRINUSE      ( 3) /* Address in use */
    <#lt>#define EADDRNOTAVAIL   ( 4) /* Address not available */
    <#lt>#define EAFNOSUPPORT    ( 5) /* Address family not supported */
    <#lt>#define EAGAIN          ( 6) /* Resource unavailable, try again */
    <#lt>#define EALREADY        ( 7) /* Connection already in progress */
    <#lt>#define EBADF           ( 8) /* Bad file descriptor */
    <#lt>#define EBADMSG         ( 9) /* Bad message */
    <#lt>#define EBUSY           (10) /* Device or resource busy */
    <#lt>#define ECANCELED       (11) /* Operation canceled */
    <#lt>#define ECHILD          (12) /* No child processes */
    <#lt>#define ECONNABORTED    (13) /* Connection aborted */
    <#lt>#define ECONNREFUSED    (14) /* Connection refused */
    <#lt>#define ECONNRESET      (15) /* Connection reset */
    <#lt>#define EDEADLK         (16) /* Resource deadlock would occur */
    <#lt>#define EDESTADDRREQ    (17) /* Destination address required */
    <#lt>#define EDOM            (18) /* Mathematics argument out of domain of function */
    <#lt>#define EDQUOT          (19) /* Reserved */
    <#lt>#define EEXIST          (20) /* File exists */
    <#lt>#define EFAULT          (21) /* Bad address */
    <#lt>#define EFBIG           (22) /* File too large */
    <#lt>#define EHOSTUNREACH    (23) /* Host is unreachable */
    <#lt>#define EIDRM           (24) /* Identifier removed */
    <#lt>#define EILSEQ          (25) /* Illegal byte sequence */
    <#lt>#define EINPROGRESS     (26) /* Operation in progress */
    <#lt>#define EINTR           (27) /* Interrupted function */
    <#lt>#define EINVAL          (28) /* Invalid argument */
    <#lt>#define EIO             (29) /* I/O error */
    <#lt>#define EISCONN         (30) /* Socket is connected */
    <#lt>#define EISDIR          (31) /* Is a directory */
    <#lt>#define ELOOP           (32) /* Too many levels of symbolic links */
    <#lt>#define EMFILE          (33) /* File descriptor value too large */
    <#lt>#define EMLINK          (34) /* Too many links */
    <#lt>#define EMSGSIZE        (35) /* Message too large */
    <#lt>#define EMULTIHOP       (36) /* Reserved */
    <#lt>#define ENAMETOOLONG    (37) /* Filename too long */
    <#lt>#define ENETDOWN        (38) /* Network is down */
    <#lt>#define ENETRESET       (39) /* Connection aborted by network */
    <#lt>#define ENETUNREACH     (40) /* Network unreachable */
    <#lt>#define ENFILE          (41) /* Too many files open in system */
    <#lt>#define ENOBUFS         (42) /* No buffer space available */
    <#lt>#define ENODATA         (43) /* No message is available on the STREAM head read queue */
    <#lt>#define ENODEV          (44) /* No such device */
    <#lt>#define ENOENT          (45) /* No such file or directory */
    <#lt>#define ENOEXEC         (46) /* Executable file format error */
    <#lt>#define ENOLCK          (47) /* No locks available */
    <#lt>#define ENOLINK         (48) /* Reserved */
    <#lt>#define ENOMEM          (49) /* Not enough space */
    <#lt>#define ENOMSG          (50) /* No message of the desired type */
    <#lt>#define ENOPROTOOPT     (51) /* Protocol not available */
    <#lt>#define ENOSPC          (52) /* No space left on device */
    <#lt>#define ENOSR           (53) /* No STREAM resources */
    <#lt>#define ENOSTR          (54) /* Not a STREAM */
    <#lt>#define ENOSYS          (55) /* Functionality not supported */
    <#lt>#define ENOTCONN        (56) /* The socket is not connected */
    <#lt>#define ENOTDIR         (57) /* Not a directory or a symbolic link to a directory */
    <#lt>#define ENOTEMPTY       (58) /* Directory not empty */
    <#lt>#define ENOTRECOVERABLE (59) /* State not recoverable */
    <#lt>#define ENOTSOCK        (60) /* Not a socket */
    <#lt>#define ENOTSUP         (61) /* Not supported */
    <#lt>#define ENOTTY          (62) /* Inappropriate I/O control operation */
    <#lt>#define ENXIO           (63) /* No such device or address */
    <#lt>#define EOPNOTSUPP      (64) /* Operation not supported on socket */
    <#lt>#define EOVERFLOW       (65) /* Value too large to be stored in data type */
    <#lt>#define EOWNERDEAD      (66) /* Previous owner died */
    <#lt>#define EPERM           (67) /* Operation not permitted */
    <#lt>#define EPIPE           (68) /* Broken pipe */
    <#lt>#define EPROTONOSUPPORT (69) /* Protocol not supported */
    <#lt>#define EPROTO          (70) /* Protocol error */
    <#lt>#define EPROTOTYPE      (71) /* Protocol wrong type for socket */
    <#lt>#define ERANGE          (72) /* Result too large */
    <#lt>#define EROFS           (73) /* Read-only file system */
    <#lt>#define ESPIPE          (74) /* Invalid seek */
    <#lt>#define ESRCH           (75) /* No such process */
    <#lt>#define ESTALE          (76) /* Reserved */
    <#lt>#define ETIMEDOUT       (77) /* Connection timed out */
    <#lt>#define ETIME           (78) /* Stream ioctl() timeout */
    <#lt>#define ETXTBSY         (79) /* Text file busy */
    <#lt>#define EWOULDBLOCK     (80) /* Operation would block */
    <#lt>#define EXDEV           (81) /* Cross-device link */

<#elseif "KEIL" == COMPILER_CHOICE>
    <#if CoreArchitecture?contains("ARM926") == false >
        <#lt>#include "cmsis_compiler.h"
    </#if>

    <#lt>#ifndef _SSIZE_T_DECLARED
    <#lt>#ifdef __SIZE_TYPE__
    <#lt>/* If __SIZE_TYPE__ is defined (armclang) we define ssize_t based on size_t.
    <#lt>We simply change "unsigned" to "signed" for this single definition
    <#lt>to make sure ssize_t and size_t only differ by their signedness. */
    <#lt>#define unsigned signed
    <#lt>typedef __SIZE_TYPE__ _ssize_t;
    <#lt>#undef unsigned
    <#lt>#else
    <#lt>#if defined(__INT_MAX__) && __INT_MAX__ == 2147483647
    <#lt>typedef int _ssize_t;
    <#lt>#else
    <#lt>typedef long _ssize_t;
    <#lt>#endif
    <#lt>#endif
    <#lt>typedef _ssize_t ssize_t;
    <#lt>#define    _SSIZE_T_DECLARED
    <#lt>#endif

    <#lt>#define NO_INIT        __attribute__((section(".no_init")))
    <#lt>#define SECTION(a)     __attribute__((__section__(a)))

    <#if CACHE_ALIGN?? >
        <#lt>#define CACHE_LINE_SIZE    (${CACHE_ALIGN}u)
        <#lt>#define CACHE_ALIGN        __ALIGNED(CACHE_LINE_SIZE)
    <#else>
        <#lt>#define CACHE_LINE_SIZE    (4u)
        <#lt>#define CACHE_ALIGN
    </#if>

    <#lt>#define CACHE_ALIGNED_SIZE_GET(size)     (size + ((size % CACHE_LINE_SIZE)? (CACHE_LINE_SIZE - (size % CACHE_LINE_SIZE)) : 0))

    <#lt>#ifndef FORMAT_ATTRIBUTE
    <#lt>   #define FORMAT_ATTRIBUTE(archetype, string_index, first_to_check)  __attribute__ ((format (archetype, string_index, first_to_check)))
    <#lt>#endif
</#if>

#ifdef __cplusplus
}
#endif

#endif // end of header

