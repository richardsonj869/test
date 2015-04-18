#include <stdint.h>
/*
 * Supported data types:
 *    unsigned int 32-bit
 *    signed int 32-bit
 *    unsigned short 16-bit
 *    signed short 16-bit
 *    unsigned char 8-bit
 *    signed char 8-bit
 *    float 32-bit
 *    string (non-null terminated)
 *
 * Sample usage:
 * lsdata_init(&ctx,UART0);
 * lsdata_log_uint32(&ctx,CHANNEL_0,some_val);
 */
typedef struct lsdata_pkt_hdr {
  uint8_t    sync;
  uint8_t    version;
  uint8_t    type;
  uint8_t    len;
  uint8_t    crc8;
} lsdata_pkt_hdr_t;
typedef struct lsdata_ch_pkt_hdr {
  // lower half (0x0f) is data type=>implicitly determines length?
  // upper half (0xf0) is channel# (0~15)
  uint8_t    channel;
} lsdata_ch_pkt_hdr_t;
typedef struct lsdata_ctx {
} lsdata_ctx_t;
typedef enum {
  LSDATA_ERROR_OK,
  LSDATA_ERROR_TIMEOUT,
  LSDATA_ERROR_FALSE
} lsdata_err_t;
typedef enum {
  LSDATA_CHANNEL_0,
  LSDATA_CHANNEL_1,
  LSDATA_CHANNEL_2,
  LSDATA_CHANNEL_3
} lsdata_channel_t;

/*
 * In order to use a UART, you'll need to pass in a function pointer
 * to something that will queue up each character onto the UART.
 * Prototype is lsdata_err_t write_char(uint8_t c) {}
 */
extern lsdata_err_t lsdata_init(lsdata_ctx_t* ctx);
extern lsdata_err_t lsdata_log_uint32(lsdata_ctx_t* ctx, lsdata_channel_t channel, uint32_t val);
