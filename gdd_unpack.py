import sys
import getopt
from collections import deque
import itertools
import struct
import logging
# This is meant to quickly unpack and verify features of a GDD packet.
# Use can be to feed in either binary or hex packet streams into stdin.
# Default mode is hex. Need python -u for binary
# echo 3e 01 00 0b 54 01 00 12 34 56 78 | python gdd_unpack.py --hex


def digest(msg):
    crc = 0
    for c in msg:
        crc = (crc^(c << 8));
        for k in range(8):
            i = 8-k
            if (crc & 0x8000):
                crc = crc ^ (0x1070 << 3)
            crc = crc << 1
    return (crc >> 8)

# Note make fake enums to support Python <3.4
class ParseState:
    LF_SYNC = 1
    LF_TYPE = 2
    LF_LEN  = 3
    LF_SEQ  = 4
    LF_CRC8 = 5
    LF_PYLD = 6
class FramingState:
    BEGINNING = 1
    MIDDLE    = 2
    END       = 3
    ERROR     = 4
class ChannelType:
    INT32   = 0
    UINT32  = 1
    DOUBLE  = 2
    STRING  = 3

def usage():
    print "Usage: gdd_unpack.py --[hex|bin]"

def main(argv):
    # mode = 0 is hex, mode = 1 is bin
    global log
    log = logging.getLogger('gdd')
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler(sys.stdout))

    mode = 0
    try:
        opts, args = getopt.getopt(argv, "", ["hex", "bin"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("--hex"):
            mode = 1
        elif opt in ("--bin"):
            mode = 0

    p = Parser()
    ch = readch(mode)
    while ch != "":
        log.debug("feeding %02x"%ch)
        p.feedChar(ch);
        ch = readch(mode)

def readch(mode):
    if mode == 0:
        ch = sys.stdin.read(1)
        if ch == "":
            return ""
        else:
            return int(ord(ch))
    elif mode == 1:
        hex_str = sys.stdin.read(2)
        if len(hex_str) < 2:
            return ""
        else:
            return int(hex_str,16)
class Frame:
    def __init__(self):
        self.type = 0
        self.seq  = 0
        self.pyld = ''
class Parser:
    def __init__(self):
        self.rbuffer = deque(maxlen=255)
        self.ps      = ParseState.LF_SYNC

    def feedBuffer(self):
        while len(self.rbuffer) > 0:
            log.debug("Attempting to drain once")
            # attempt to parse out a frame starting
            # first remove all leading garbage
            self.ps = ParseState.LF_SYNC
            ret = self.feedCharSM(self.rbuffer[0])
            log.debug("ret for %02x is %d"%(self.rbuffer[0],ret))
            while (ret == FramingState.ERROR and len(self.rbuffer) > 1):
                log.debug("popping off %02x"%self.rbuffer[0])
                self.rbuffer.popleft()
                ret = self.feedCharSM(self.rbuffer[0])
                # so presumably we have FramingState.BEGIN

                log.debug("keep feeding")
            # keep feeding data until we get an error or end frame
            if len(self.rbuffer) < 2:
                # we have already fed the only character left
                return ret
            ret = self.feedCharSM(self.rbuffer[1])
            idx = 2
            while (ret == FramingState.MIDDLE and idx < len(self.rbuffer)):
                log.debug("feeding char in while loop %02x"%self.rbuffer[idx])
                ret = self.feedCharSM(self.rbuffer[idx])
                idx += 1
                if (ret == FramingState.END):
                    # check the CRC
                    pkt_copy = list(self.rbuffer)[:idx];
                    pkt_crc = pkt_copy[4]
                    pkt_copy[4] = 0
                    for c in pkt_copy:
                        log.debug("%02x"%c)
                    rl_crc = digest(pkt_copy)
                    log.debug("PKT LEN = %d PKT CRC = %02x CALC CRC = %02x"%(len(self.rbuffer),pkt_crc,rl_crc))
                    if pkt_crc == rl_crc:
                        log.debug("CRC8 MATCHES")
                        self.completeFrameHandler(self.type,self.seq,list(self.rbuffer)[5:idx])
                        # great pop off the entire frame
                        for i in range(idx):
                            self.rbuffer.popleft()
                        break
                    else:
                        log.debug("CRC8 FAILURE")
                        # pop off the left most and start over
                        self.rbuffer.popleft()
                elif ret == FramingState.ERROR:
                    # just pop off the leftmost and try again
                    self.rbuffer.popleft()
                    continue
                elif ret == FramingState.MIDDLE:
                    # keep going
                    continue
                else:
                    log.error("SM mismatch: expeted ERROR or END or MIDDLE but got %d"%ret)
                    return ret
            return ret

    def feedChar(self, ch):
        self.rbuffer.append(ch)
        ret = self.feedBuffer()
    def feedCharSM(self,ch):
        log.debug("ch %02x state = %d"%(ch,self.ps))
        if self.ps == ParseState.LF_SYNC:
            if ch == 0x3e:
                self.ps = ParseState.LF_TYPE
                return FramingState.BEGINNING
            else:
                return FramingState.ERROR
        elif self.ps == ParseState.LF_TYPE:
            log.debug("type = %02x"%ch)
            self.type = ch
            self.ps = ParseState.LF_LEN
            return FramingState.MIDDLE
        elif self.ps == ParseState.LF_LEN:
            log.debug("len = %02x"%ch)
            self.len = ch
            self.ps = ParseState.LF_SEQ
            return FramingState.MIDDLE
        elif self.ps == ParseState.LF_SEQ:
            log.debug("seq = %02x"%ch)
            self.seq = ch
            self.ps = ParseState.LF_CRC8
            return FramingState.MIDDLE
        elif self.ps == ParseState.LF_CRC8:
            log.debug("crc = %02x"%ch)
            self.crc8 = ch
            self.ps = ParseState.LF_PYLD
            self.pyldidx = 0
            return FramingState.MIDDLE
        elif self.ps == ParseState.LF_PYLD:
            log.debug("expected len = %d >= %d"%((self.len-5),self.pyldidx))
            self.pyldidx += 1
            # keep going until end
            if self.pyldidx < self.len-5:
                return FramingState.MIDDLE
            else:
                self.ps = ParseState.LF_SYNC
                return FramingState.END
    def completeFrameHandler(self, type, seq, pyld):
        log.debug("completed frame of len:%d,%02x %d,%d"%(len(pyld),pyld[2],type,seq))
        # extract out the channels
        if len(pyld) < 3:
            log.error("Payload too short")
        else:
            if (type == 0):
                # single channel
                log.debug("single channel")
                # extract the channel type and number
                ch_type = pyld[0]
                ch_num = pyld[1]
                if ch_type == ChannelType.STRING:
                    self.stringHandler(seq, (''.join(chr(i) for i in pyld[2:])))
                elif ch_type == ChannelType.INT32:
                    # it's stored in network byte order (big endian)
                    s = struct.Struct('>i')
                    val = s.unpack_from(''.join(chr(i) for i in pyld[2:]))[0]
                    self.int32Handler(seq, val)
                elif ch_type == ChannelType.UINT32:
                    # it's stored in network byte order (big endian)
                    s = struct.Struct('>I')
                    val = s.unpack_from(''.join(chr(i) for i in pyld[2:]))[0]
                    self.uint32Handler(seq, val)
                elif ch_type == ChannelType.DOUBLE:
                    print "not handled"
            else:
                print "UNKNOWN channel type %d"%type
    def stringHandler(self, seq, val):
        print "Received string: %s"%val
    def int32Handler(self, seq, val):
        print "Received int32: %d (0x%08x)"%(val,val)
    def uint32Handler(self, seq, val):
        print "Received int32: %d (0x%08x)"%(val,val)

if __name__ == '__main__':
    main(sys.argv[1:])
