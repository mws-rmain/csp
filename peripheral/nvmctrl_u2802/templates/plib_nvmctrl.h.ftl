/*******************************************************************************
  Non-Volatile Memory Controller(${NVMCTRL_INSTANCE_NAME}) PLIB.

  Company:
    Microchip Technology Inc.

  File Name:
    plib_${NVMCTRL_INSTANCE_NAME?lower_case}.h

  Summary:
    Interface definition of ${NVMCTRL_INSTANCE_NAME} Plib.

  Description:
    This file defines the interface for the ${NVMCTRL_INSTANCE_NAME} Plib.
    It allows user to Program, Erase and lock the on-chip Non Volatile Flash
    Memory.
*******************************************************************************/

// DOM-IGNORE-BEGIN
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
// DOM-IGNORE-END

#ifndef PLIB_${NVMCTRL_INSTANCE_NAME}_H
#define PLIB_${NVMCTRL_INSTANCE_NAME}_H

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************

#include "device.h"
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// DOM-IGNORE-BEGIN
#ifdef __cplusplus // Provide C++ Compatibility
 extern "C" {
#endif

// DOM-IGNORE-END

#define ${NVMCTRL_INSTANCE_NAME}_FLASH_START_ADDRESS        (${.vars["FLASH_START_ADDRESS"]}U)
#define ${NVMCTRL_INSTANCE_NAME}_FLASH_PAGESIZE             (${FLASH_PROGRAM_SIZE}U)
#define ${NVMCTRL_INSTANCE_NAME}_FLASH_ROWSIZE              (${FLASH_ERASE_SIZE}U)

<#if FLASH_DATAFLASH_START_ADDRESS??>
#define ${NVMCTRL_INSTANCE_NAME}_DATAFLASH_START_ADDRESS    (${.vars["FLASH_DATAFLASH_START_ADDRESS"]}U)
#define ${NVMCTRL_INSTANCE_NAME}_DATAFLASH_PAGESIZE         (${FLASH_DATAFLASH_PROGRAM_SIZE}U)
#define ${NVMCTRL_INSTANCE_NAME}_DATAFLASH_ROWSIZE          (${FLASH_DATAFLASH_ERASE_SIZE}U)
</#if>

<#if DRV_MEMORY_CONNECTED == true>
    <#lt>#define ${NVMCTRL_INSTANCE_NAME}_START_ADDRESS              0x${START_ADDRESS}
    <#lt>#define ${NVMCTRL_INSTANCE_NAME}_MEDIA_SIZE                 ${MEMORY_MEDIA_SIZE}
    <#lt>#define ${NVMCTRL_INSTANCE_NAME}_ERASE_BUFFER_SIZE          ${ERASE_BUFFER_SIZE}
</#if>

typedef enum
{
    /* No error */
    NVMCTRL_ERROR_NONE = 0x0,

    /* NVMCTRL invalid commands and/or bad keywords error */
    NVMCTRL_ERROR_PROG = 0x2,

    /* NVMCTRL lock error */
    NVMCTRL_ERROR_LOCK = 0x4,

    /* NVMCTRL programming or erase error */
    NVMCTRL_ERROR_NVM = 0x8,


    /* Key Error */
    NVMCTRL_ERROR_KEY = 0x10

} NVMCTRL_ERROR;

typedef enum
{
    NVMCTRL_MEMORY_REGION_APPLICATION = NVMCTRL_NSULCK_ANS_Msk,
<#if NVMCTRL_NSULCK_BNS == true>
    NVMCTRL_MEMORY_REGION_BOOTLOADER = NVMCTRL_NSULCK_BNS_Msk,
</#if>
    NVMCTRL_MEMORY_REGION_DATA = NVMCTRL_NSULCK_DNS_Msk
} NVMCTRL_MEMORY_REGION;

<#if __TRUSTZONE_ENABLED?? && __TRUSTZONE_ENABLED == "true">
typedef enum
{
    NVMCTRL_SECURE_MEMORY_REGION_APPLICATION = NVMCTRL_SULCK_AS_Msk,
    NVMCTRL_SECURE_MEMORY_REGION_BOOTLOADER = NVMCTRL_SULCK_BS_Msk,
    NVMCTRL_SECURE_MEMORY_REGION_DATA = NVMCTRL_SULCK_DS_Msk
} NVMCTRL_SECURE_MEMORY_REGION;

</#if>
<#if INTERRUPT_ENABLE == true>
    <#lt>typedef void (*NVMCTRL_CALLBACK)(uintptr_t context);
</#if>

void ${NVMCTRL_INSTANCE_NAME}_Initialize(void);

bool ${NVMCTRL_INSTANCE_NAME}_Read( uint32_t *data, uint32_t length, uint32_t address );

bool ${NVMCTRL_INSTANCE_NAME}_PageWrite( uint32_t* data, uint32_t address );

bool ${NVMCTRL_INSTANCE_NAME}_RowErase( uint32_t address );

NVMCTRL_ERROR ${NVMCTRL_INSTANCE_NAME}_ErrorGet( void );

bool ${NVMCTRL_INSTANCE_NAME}_IsBusy( void );

void ${NVMCTRL_INSTANCE_NAME}_RegionLock (NVMCTRL_MEMORY_REGION region);

void ${NVMCTRL_INSTANCE_NAME}_RegionUnlock (NVMCTRL_MEMORY_REGION region);

<#if __TRUSTZONE_ENABLED?? && __TRUSTZONE_ENABLED == "true">
    <#lt>void ${NVMCTRL_INSTANCE_NAME}_SecureRegionLock (NVMCTRL_SECURE_MEMORY_REGION region);

    <#lt>void ${NVMCTRL_INSTANCE_NAME}_SecureRegionUnlock (NVMCTRL_SECURE_MEMORY_REGION region);

    <#lt>void ${NVMCTRL_INSTANCE_NAME}_DataScrambleKeySet(uint32_t dsckey);

    <#lt>void ${NVMCTRL_INSTANCE_NAME}_DataScrambleEnable(bool enable);
</#if>

<#if INTERRUPT_ENABLE == true>
    <#lt>void ${NVMCTRL_INSTANCE_NAME}_CallbackRegister ( NVMCTRL_CALLBACK callback, uintptr_t context );
</#if>

<#if NVMCTRL_CACHE_ENABLE == true>
    <#lt>void ${NVMCTRL_INSTANCE_NAME}_CacheInvalidate ( void );
</#if>

<#if NVMCTRL_WRITE_POLICY == "MANUAL">
bool ${NVMCTRL_INSTANCE_NAME}_PageBufferWrite( uint32_t *data, const uint32_t address);

bool ${NVMCTRL_INSTANCE_NAME}_PageBufferCommit( const uint32_t address);
</#if>

// DOM-IGNORE-BEGIN
#ifdef __cplusplus // Provide C++ Compatibility
}
#endif
// DOM-IGNORE-END
#endif // PLIB_${NVMCTRL_INSTANCE_NAME}_H
