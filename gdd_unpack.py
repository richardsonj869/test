import sys
import getopt
from collections import deque
import itertools
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
    mode = 0
    try:
        opts, args = getopt.getopt(argv, "", ["hex", "bin"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("--hex"):
            mode = 0
        elif opt in ("--bin"):
            mode = 1
    buffer = "\x3e\x00\x0f\x01\x25\x03\x00\x6d\x79\x73\x74\x72\x69\x6e\x67"
#    buffer = "\x3e\x00\x0f\x00\x77\x03\x00\x6d\x79\x73\x74\x3e\x69\x6e\x67"
#    buffer = "\x3e\x00\x03\x3e\x00\x0f\x00\x77\x03\x00\x6d\x79\x73\x74\x3e\x69\x6e\x67"
# assume a clean input
    p = Parser()
    for c in buffer:
        ci = int(ord(c))
        print "%02x"%ci
        p.feedChar2(ci);

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
            print "Attempting to drain once: ",self.rbuffer
            # attempt to parse out a frame starting
            # first remove all leading garbage
            self.ps = ParseState.LF_SYNC
            ret = self.feedCharSM(self.rbuffer[0])
            print "ret for %02x is %d"%(self.rbuffer[0],ret)
            while (ret == FramingState.ERROR and len(self.rbuffer) > 1):
                print "popping off %02x"%self.rbuffer[0]
                self.rbuffer.popleft()
                ret = self.feedCharSM(self.rbuffer[0])
                # so presumably we have FramingState.BEGIN
            if 0 == 1:
                print "crazy"
            else:
                print "keep feeding"
                # keep feeding data until we get an error or end frame
                if len(self.rbuffer) < 2:
                    # we have already fed the only character left
                    return ret
                ret = self.feedCharSM(self.rbuffer[1])
                idx = 2
                while (ret == FramingState.MIDDLE and idx < len(self.rbuffer)):
                    print "feeding char in while loop %02x"%self.rbuffer[idx]
                    ret = self.feedCharSM(self.rbuffer[idx])
                    idx += 1
                    if (ret == FramingState.END):
                        # check the CRC
                        pkt_crc = self.rbuffer[4]
                        self.rbuffer[4] = 0
                        for c in self.rbuffer:
                            print "%02x"%c
                        rl_crc = digest(self.rbuffer)
                        print "PKT LEN = %d PKT CRC = %02x CALC CRC = %02x"%(len(self.rbuffer),pkt_crc,rl_crc)
                        if pkt_crc == rl_crc:
                            print "CRC8 MATCHES"
                            self.completeFrameHandler(self.type,self.seq,list(self.rbuffer)[5:idx])
                        else:
                            print "CRC8 FAILURE"

                        # great pop off the entire frame
                        for i in range(idx):
                            self.rbuffer.popleft()
                        break
                    elif ret == FramingState.ERROR:
                        # just pop off the leftmost and try again
                        self.rbuffer.popleft()
                        continue
                    elif ret == FramingState.MIDDLE:
                        # keep going
                        continue
                    else:
                        print "SM mismatch: expeted ERROR or END or MIDDLE but got %d"%ret
                        return ret
                return ret

    def feedChar2(self, ch):
        self.rbuffer.append(ch)
        ret = self.feedBuffer()
    def feedCharSM(self,ch):
        print "ch %02x state = %d"%(ch,self.ps)
        if self.ps == ParseState.LF_SYNC:
            if ch == 0x3e:
                print ">>>>"
                self.ps = ParseState.LF_TYPE
                return FramingState.BEGINNING
            else:
                return FramingState.ERROR
        elif self.ps == ParseState.LF_TYPE:
            print "type = %02x"%ch
            self.type = ch
            self.ps = ParseState.LF_LEN
            return FramingState.MIDDLE
        elif self.ps == ParseState.LF_LEN:
            print "len = %02x"%ch
            self.len = ch
            self.ps = ParseState.LF_SEQ
            return FramingState.MIDDLE
        elif self.ps == ParseState.LF_SEQ:
            print "seq = %02x"%ch
            self.seq = ch
            self.ps = ParseState.LF_CRC8
            return FramingState.MIDDLE
        elif self.ps == ParseState.LF_CRC8:
            print "crc = %02x"%ch
            self.crc8 = ch
            self.ps = ParseState.LF_PYLD
            self.pyldidx = 0
            return FramingState.MIDDLE
        elif self.ps == ParseState.LF_PYLD:
            print "expected len = %d >= %d"%((self.len-5),self.pyldidx)
            self.pyldidx += 1
            print "pyld = %02x"%ch
            # keep going until end
            if self.pyldidx < self.len-5:
                return FramingState.MIDDLE
            else:
                self.ps = ParseState.LF_SYNC
                return FramingState.END
    def completeFrameHandler(self, type, seq, pyld):
        print "completed frame of len:%d,%02x %d,%d"%(len(pyld),pyld[2],type,seq)
        # extract out the channels
        if len(pyld) < 3:
            print "Payload too short"
        else:
            if (type == 0):
                # single channel
                print "single channel"
                # extract the channel type and number
                ch_type = pyld[0]
                ch_num = pyld[1]
                if (ch_type == ChannelType.STRING):
                    self.stringHandler(seq, (''.join(chr(i) for i in pyld[2:])))
            else:
                print "UNKNOWN channel type %d"%type
    def stringHandler(self, seq, val):
        print "Received string: %s"%val
if __name__ == '__main__':
    main(sys.argv[1:])
