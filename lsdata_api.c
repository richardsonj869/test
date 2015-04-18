#include "lsdata_api.h"
#include <string.h>
uint8_t CRC8(const void *vptr, size_t len)
{
  const uint8_t *data = vptr;
  unsigned crc = 0;
  int i, j;
  for (j = len; j; j--, data++) {
    crc ^= (*data << 8);
    for(i = 8; i; i--) {
      if (crc & 0x8000)
	crc ^= (0x1070 << 3);
      crc <<= 1;
    }
  }
  return (uint8_t)(crc >> 8);
}
gdd_err_t gdd_init(gdd_ctx_t* ctx, USARTSendData_Handler handler)
{
  ctx->handler = handler;
  return GDD_ERROR_OK;
}
inline gdd_err_t gdd_log_uint32(const gdd_ctx_t* ctx,
				const gdd_channel_t channel,
				const uint32_t val)
{
  return gdd_log_gen(ctx, channel, &val, GDD_CHTYPE_UINT32, sizeof(uint32_t));
}
inline gdd_err_t gdd_log_string(const gdd_ctx_t* ctx,
				const gdd_channel_t channel,
				const char* val)
{
  return gdd_log_gen(ctx, channel, val, GDD_CHTYPE_STRING, sizeof(char)*strlen(val));
}
gdd_err_t gdd_log_gen(const gdd_ctx_t* ctx,
		      const gdd_channel_t channel,
		      const void* val,
		      const gdd_ch_type_t type,
		      const size_t sz)
{
  // construct the packet, then send it off
  // Packet is structured: [ [gdd_pkt_hdr_t] [gdd_ch_pkt_hdr_t] payload ]
  size_t         pkt_len   = sizeof(gdd_pkt_hdr_t) + sizeof(gdd_ch_hdr_t) + sz;
  uint8_t        pkt[pkt_len];
  gdd_pkt_hdr_t* pkt_hdr   = (gdd_pkt_hdr_t*)pkt;
  gdd_ch_hdr_t*  ch_hdr    = (gdd_ch_hdr_t*)(pkt+sizeof(gdd_pkt_hdr_t));
  void*          payload   = (void*)(pkt+sizeof(gdd_pkt_hdr_t)+sizeof(gdd_ch_hdr_t));

  pkt_hdr->sync    = '>';            // default sync character
  pkt_hdr->version = 1;
  pkt_hdr->type    = GDD_TYPE_1CHAN; // WARNING: ENUM->uint8_t
  pkt_hdr->len     = pkt_len;
  pkt_hdr->crc8    = 0;
  ch_hdr->type     = type;           // WARNING: ENUM->uint8_t
  ch_hdr->channel  = channel;        // WARNING: ENUM->uint8_t

  // Copy over the actual data
  memcpy(payload, val, sz);

  // Finally, calculate the CRC8 checksum with it zeroed out
  pkt_hdr->crc8    = CRC8(pkt, pkt_len);

  // Bang out the bytes. We need something that will take the buffer
  // since we do not know what kind of scheduler this will be running on
  ctx->handler(pkt, pkt_len);
  return GDD_ERROR_OK;
}
