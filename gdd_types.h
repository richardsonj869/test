#include <stdint.h>
#include <stddef.h>

/*
 * USARTSendData_Handler: Function prototype to handle sending string over UART
 *
 * Note that the data does is not necessarily a string, and is not null terminated
 * so the length parameter must be respected.
 *
 * For example:
 *     void my_sender(uint8_t *data, size_t len) {
 *         // You CANNOT just printf("%s",data)
 *     }
 */
typedef void (*USARTSendData_Handler)(uint8_t *data, size_t len);

/*
 * gdd_err_t: Error codes
 *
 * GDD_ERROR_OK:      success
 * GDD_ERROR_TIMEOUT: something timed out
 * GDD_ERROR_UNKNOWN: unknown failure (hopefully this never gets returned)
 */
typedef enum {
  GDD_ERROR_OK,
  GDD_ERROR_TIMEOUT,
  GDD_ERROR_UNKNOWN
} gdd_err_t;

/*
 * gdd_channel_t: Indicates number of supported channels
 */
typedef enum {
  GDD_CHANNEL_0,
  GDD_CHANNEL_1,
  GDD_CHANNEL_2,
  GDD_CHANNEL_3
} gdd_channel_t;

/*
 * gdd_ch_type_t: supported channel data types
 *
 * GDD_CHTYPE_INT32:  no implemented
 * GDD_CHTYPE_UINT32: big endian over transport
 * GDD_CHTYPE_DOUBLE: no implemented
 * GDD_CHTYPE_STRING: complete
 */
typedef enum {
  GDD_CHTYPE_INT32,
  GDD_CHTYPE_UINT32,
  GDD_CHTYPE_DOUBLE,
  GDD_CHTYPE_STRING,
  GDD_CHTYPE_MAX
} gdd_ch_type_t;

/* 
 * gdd_pkt_type_t: supported channel packet formats
 *
 * GDD_TYPE_1CHAN:  one channel of data only in the payload
 */
typedef enum {
  GDD_TYPE_1CHAN,
} gdd_pkt_type_t;

typedef struct gdd_pkt_hdr {
  uint8_t    sync;
  uint8_t    version;
  uint8_t    type;
  uint8_t    len;
  uint8_t    crc8;
} gdd_pkt_hdr_t;

typedef struct gdd_ch_pkt_hdr {
  uint8_t    type;
  uint8_t    channel;
} gdd_ch_hdr_t;

typedef struct gdd_ctx {
  USARTSendData_Handler handler;
} gdd_ctx_t;
