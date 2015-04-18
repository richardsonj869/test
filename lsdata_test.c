#include <stdio.h>
#include <string.h>
#include "lsdata_api.h"

int test1()
{
  char hdr[] = "abcde";
  gdd_pkt_hdr_t *hdrs = (gdd_pkt_hdr_t*)hdr;
  printf("lsdata pkt hdr size: %u\n",sizeof(gdd_pkt_hdr_t));
  printf("%c %c %c %c %c\n",hdrs->sync,hdrs->version,hdrs->type,hdrs->len,hdrs->crc8);
  return 0;
}
void my_sender(uint8_t *data, size_t len)
{
  char *pfx = "Sending data: ";
  printf("%s",pfx);
  int i;

  // First print in hex
  for (i=0;i<len;i++) {
    printf("%02x ", data[i]);
  }
  printf("\n");

  // Fill in the spaces on line 2
  for (i=0;i<strlen(pfx);i++) printf(" ");

  // Print ASCII where possible
  for (i=0;i<len;i++) {
    if (data[i] >= ' ' && data[i] <= '~') {
      printf("%c  ", data[i]);
    } else {
      printf(".  ");
    }
  }
  printf("\n");
}
int test2()
{
  USARTSendData_Handler handler = &my_sender;
  gdd_ctx_t ctx;
  if (GDD_ERROR_OK != gdd_init(&ctx, handler)) {
    printf("Failed to initialize\n");
    return 1;
  } else {
    if (GDD_ERROR_OK != gdd_log_string(&ctx, GDD_CHANNEL_0, "mystring")) {
      printf("Failed string test\n");
    }
    if (GDD_ERROR_OK != gdd_log_uint32(&ctx, GDD_CHANNEL_0, 0x12345678)) {
      printf("Failed uint32 test\n");
    }
    return 0;
  }
}
int main()
{
  test1();
  test2();
  return 0;
}
