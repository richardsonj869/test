#include <stdio.h>
#include "lsdata_types.h"

int main()
{
  char hdr[] = "abcde";
  lsdata_pkt_hdr_t *hdrs = (lsdata_pkt_hdr_t*)hdr;
  printf("lsdata pkt hdr size: %u\n",sizeof(lsdata_pkt_hdr_t));
  printf("%c %c %c %c %c\n",hdrs->sync,hdrs->version,hdrs->type,hdrs->len,hdrs->crc8);
  return 0;
}
