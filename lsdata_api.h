#include "lsdata_types.h"
/*
 * In order to use a UART, you'll need to pass in a function pointer
 * to something that will queue up each character onto the UART.
 * Prototype is gdd_err_t write_char(uint8_t c) {}
 */
extern gdd_err_t gdd_init(gdd_ctx_t* ctx, USARTSendData_Handler handler);
extern inline gdd_err_t gdd_log_uint32(const gdd_ctx_t* ctx,
				       const gdd_channel_t channel,
				       const uint32_t val);
extern inline gdd_err_t gdd_log_string(const gdd_ctx_t* ctx,
				       const gdd_channel_t channel,
				       const char* val);
extern gdd_err_t gdd_log_gen(const gdd_ctx_t* ctx,
			     const gdd_channel_t channel,
			     const void* val,
			     const gdd_ch_type_t type,
			     const size_t sz);
