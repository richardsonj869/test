#ifndef __GDD_API_H__
#define __GDD_API_H__
#include "gdd_types.h"
/*
 * In order to use a UART, you'll need to pass in a function pointer
 * to something that will queue up each character onto the UART.
 * Prototype is gdd_err_t write_char(uint8_t c) {}
 */
extern gdd_err_t gdd_init(gdd_ctx_t* ctx, USARTSendData_Handler handler);
extern gdd_err_t gdd_log_uint32(gdd_ctx_t* ctx,
				       const gdd_channel_t channel,
				       const uint32_t val);
extern inline gdd_err_t gdd_log_string(gdd_ctx_t* ctx,
				       const gdd_channel_t channel,
				       const char* val);
extern gdd_err_t gdd_log_gen(gdd_ctx_t* ctx,
			     const gdd_channel_t channel,
			     const void* val,
			     const gdd_ch_type_t type,
			     const size_t sz);
#endif /* __GDD_API_H__ */
