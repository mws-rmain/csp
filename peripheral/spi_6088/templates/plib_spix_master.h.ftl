/*******************************************************************************
  SPI PLIB

  Company:
    Microchip Technology Inc.

  File Name:
    plib_${SPI_INSTANCE_NAME?lower_case}_master.h

  Summary:
    ${SPI_INSTANCE_NAME} Master PLIB Header File

  Description:
    This file has prototype of all the interfaces provided for particular
    SPI peripheral.

*******************************************************************************/

/*******************************************************************************
* Copyright (C) 2018 Microchip Technology Inc. and its subsidiaries.
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

#ifndef PLIB_${SPI_INSTANCE_NAME}_MASTER_H
#define PLIB_${SPI_INSTANCE_NAME}_MASTER__H

#include "device.h"
#include "plib_spi_master_common.h"

/* Provide C++ Compatibility */
#ifdef __cplusplus

    extern "C" {

#endif

/****************************** ${SPI_INSTANCE_NAME} Interface *********************************/

void ${SPI_INSTANCE_NAME}_Initialize( void );

bool ${SPI_INSTANCE_NAME}_WriteRead( void* pTransmitData, size_t txSize, void* pReceiveData, size_t rxSize );

bool ${SPI_INSTANCE_NAME}_Write( void* pTransmitData, size_t txSize );

bool ${SPI_INSTANCE_NAME}_Read( void* pReceiveData, size_t rxSize );

bool ${SPI_INSTANCE_NAME}_TransferSetup( SPI_TRANSFER_SETUP *setup, uint32_t spiSourceClock );

bool ${SPI_INSTANCE_NAME}_IsTransmitterBusy( void );

<#if SPI_NUM_CSR != 1>
void ${SPI_INSTANCE_NAME}_ChipSelectSetup(SPI_CHIP_SELECT chipSelect);
</#if>

<#if SPI_INTERRUPT_MODE == true>
bool ${SPI_INSTANCE_NAME}_IsBusy( void );

void ${SPI_INSTANCE_NAME}_CallbackRegister( const SPI_CALLBACK callback, uintptr_t context );

</#if>

/* Provide C++ Compatibility */
#ifdef __cplusplus

    }

#endif

#endif // PLIB_${SPI_INSTANCE_NAME}_MASTER_H

/*******************************************************************************
 End of File
*/
