<#if SERCOM_MODE = "SPIM" || SERCOM_MODE = "SPIS">
    ${SERCOM_INSTANCE_NAME}_SPI_Initialize();
<#elseif SERCOM_MODE = "I2CM" || SERCOM_MODE = "I2CS">
    ${SERCOM_INSTANCE_NAME}_I2C_Initialize();
<#elseif SERCOM_MODE = "USART_INT">
    ${SERCOM_INSTANCE_NAME}_USART_Initialize();
</#if>
