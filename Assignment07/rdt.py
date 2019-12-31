import struct
from datetime import time
import udp
import enum
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

#GOLBAL CLASSICAL VALUES
WINDOWS_SIZE = 8
maxl = 1024 #max length
maxre = 10 #max retry if timeout
Reset_bit = 8
SYN = 4
NIF = 2
ACK = 1
udp_packet_length = 500
begin_bytes = b'000000000000000'
user_address = ("127.0.0.1", 9942)

class TODO(enum.Enum):
    A = 0   #bind
    B = 1   #listen
    C = 2   #accept
    D = 3   #connect_requested
    E = 4   #connect
    F = 5   #close_requested
    G = 6   #close

class CONDITION(enum.Enum):
    A = 0   #OPENED
    B = 1   #LISTING
    C = 2   #CONNECTING
    D = 3   #CONNECTED
    E = 4   #CLOSING
    F = 5   #CLOSED


class FSM(object):
    def __init__(self, condition=None):
        sc = self._current
        sc = None
        if type(condition) == CONDITION:
            sc = condition
        elif type(condition) == int:
            sc = CONDITION(condition)
        elif condition is None:
            sc = CONDITION.A
        else:
            raise ValueError("Invalid condition")

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, current: CONDITION):
        self._current = current
        logging.info('Change From %s to %s', self._current, current)

    def dispatch(self, todo: str):
        sc = self._current
        if sc == CONDITION.A:
            if todo == TODO.A:
                sc = CONDITION.B
            elif todo == TODO.B:
                sc = CONDITION.B
            elif todo == TODO.E:
                sc = CONDITION.D
            else:
                raise ValueError("Invalid action")
        elif sc == CONDITION.D:
            if todo == TODO.F:
                sc = CONDITION.E
            elif todo == TODO.G:
                sc = CONDITION.F
            else:
                raise ValueError("Invalid action")
        elif sc == CONDITION.B:
            if todo == TODO.D:
                sc = CONDITION.C
            else:
                raise ValueError("Invalid action")
        elif sc == CONDITION.E:
            if todo == TODO.G:
                ssc = CONDITION.F
            else:
                raise ValueError("Invalid action")
        elif sc == CONDITION.C:
            if todo == TODO.C:
                sc = CONDITION.D
            else:
                raise ValueError("Invalid action")
        else:
            logging.warning("Nothing to do")


class datagram(object):
    def _set_header(self, offset, value):
        tmp = list(self._header)
        for index, byte in enumerate(value):
            tmp[offset + index] = byte
        self._header = bytes(tmp)

    # For datagram type
    @property
    def dtype(self) -> int:
        return self._dtype

    @dtype.setter
    def dtype(self, dtype: int):
        self._dtype = dtype
        self._set_header(0, self._dtype.to_bytes(1, 'big'))

    # For Seq
    @property
    def seq(self):
        return int.from_bytes(self._seq, 'big')

    @seq.setter
    def seq(self, seq):
        if type(seq) == int:
            self._seq = seq.to_bytes(4, 'big')
            self._set_header(1, self._seq)
        else:
            raise ValueError("Seq number must be an integer")

    # For SEQ_ACK
    @property
    def seq_ack(self):
        return int.from_bytes(self._seq_ack, 'big')

    @seq_ack.setter
    def seq_ack(self, seq_ack):
        if type(seq_ack) == int:
            self._seq_ack = seq_ack.to_bytes(4, 'big')
            self._set_header(5, self._seq_ack)
        else:
            raise ValueError("SEQ_ACK number must be an integer")

    # For LEN
    @property
    def length(self):
        return int.from_bytes(self._length, 'big')

    @length.setter
    def length(self, length):
        raise NotImplementedError("Length cannot be set.")

    # For CHECKSUM
    @property
    def checksum(self):
        tmp = self._header[0:13] + b'\x00\x00' + self._payload
        sum = 0
        for byte in tmp:
            sum += byte
            sum = -(sum % 256)
        return (sum & 0xFF)

    @checksum.setter
    def checksum(self, checksum):
        raise NotImplementedError("Checksum cannot be set.")

    @property
    def valid(self):
        return self.checksum == int.from_bytes(self._checksum, 'big')

    # For PAYLOAD
    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, payload):
        if type(payload) == bytes:
            self._length = len(payload).to_bytes(4, 'big')
            self._payload = payload
        else:
            raise TypeError("a bytes-like object is expected")

    def __init__(self, raw_data=None):
        if type(raw_data) == bytes:
            self._decode(raw_data)
        else:
            self._header = bytes(15)
            self._dtype = 0
            self._seq = bytes(4)
            self._seq_ack = bytes(4)
            self._length = bytes(4)
            self._checksum = bytes(2)
            self._payload = b''

    def _decode(self, raw_data: bytes):
        if len(raw_data) < 15:
            raise ValueError("Invalid data!")
        self._header = raw_data[0:15]
        self._dtype = self._header[0]
        self._seq = self._header[1: 5]
        self._seq_ack = self._header[5: 9]
        self._length = self._header[9: 13]
        self._checksum = self._header[13: 15]

        self._payload = raw_data[15:]

    def _encode(self):
        self._set_header(13, self.checksum.to_bytes(2, 'big'))
        return self._header + self._payload

    def __call__(self):
        return self._encode()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        try:
            res = "Type:\t{}\nSeq:\t{}\nSEQ_ACK:\t{}\nLENGTH:\t{}\nChecksum:\t{}\nPayload:\t{}".format(
                self.dtype, self.seq, self.seq_ack, self.length, self.checksum, self.payload)
            return res
        except Exception:
            return "Invalid"


def check_sum(data):
    pass

def header_send(args):
    pass

class socket(udp.UDPsocket):
    def __init__(self, ):
        super().__init__()
        self.condition = FSM(CONDITION.A)
        self.seq = 0
        self.seq_ack = 0
        self.accept_null = True

    def bind(self, addr):
        self.condition.dispatch(TODO.A)
        super().bind(addr)

    def accept(self):
        print("Accept is not implemented for connectionless rdt")
        raise NotImplementedError

    def connect(self, addr):
        self.to = addr

    def close(self):
        print("Close is not implemented for connectionless ")
        raise NotImplementedError

    def recvfrom(self, bufsize=2048):
        QvQ = super().recvfrom(bufsize)
        if QvQ is None:
            raise udp.timeout

        data, addr = QvQ
        data = datagram(data)
        if data.valid:
            return data, addr
        raise Exception("Invalid packet")

    def recv(self, bufsize: int):

        rcvd_data = b''
        timeout_count = -1
        expected = self.seq_ack

        ack = datagram()

        logging.info('receive Ready ...')
        while True:
            try:
                data, addr = self.recvfrom(bufsize)

                logging.debug('received raw segment')
                timeout_count = 0  # no timeout, reset

                logging.info('expected: #%d, received: #%d', expected, data.seq)
                if data.seq == expected:
                    if data.dtype & NIF:
                        logging.info('FIN Recieved')
                        break
                    else:
                        rcvd_data += data.payload
                    expected += 1
                ack.seq = self.seq
                ack.seq_ack = expected
                super().sendto(ack(), addr)
            except udp.timeout:
                if timeout_count < 0:
                    continue
                timeout_count += 1
                logging.info('timed out, count=%d', timeout_count)
                if timeout_count > maxre:
                    raise ConnectionAbortedError('timed out')
            except ValueError:
                ack.seq = self.seq
                ack.seq_ack = expected
                super().sendto(ack(), addr)
            except Exception as e:
                logging.warning(e)

        self.seq += 1
        self.seq_ack = expected + 1

        nif_ack = datagram()
        nif_ack.dtype |= NIF
        nif_ack.dtype |= ACK
        nif_ack.seq = self.seq
        nif_ack.seq_ack = self.seq_ack
        nif_err_count = 0
        self.sendto(nif_ack(), addr)

        logging.info('----------- receipt finished -----------')
        return rcvd_data

    def recv_(self, buffersize=None, header_format=None, data_format=None):
        print("data in")
        try:
            data_uesless, addr_uesless = self.recvfrom(buffersize)
        except BlockingIOError:
            pass
        except TypeError:
            pass
        temp_ack = self.seq_ack
        data_willsend = ""
        count = 0
        while True:
            time.sleep(0.01)
            try:
                data, addr = self.recvfrom(buffersize)
            except BlockingIOError:
                continue
            except TypeError:
                continue
            if check_sum(data):
                continue
            data_header = struct.unpack(header_format, data[0:15])
            try:
                datas = str(struct.unpack("{}s".format(str(data_header[3])), data[15:])[0].decode(data_format))
            except UnicodeDecodeError:
                continue
            except struct.error:
                continue
            if datas == "" and self.accept_null:
                continue
            else:
                print("this time recieve {}".format(datas))
            self.segment = data_header[0]
            if not check_sum(data) and data_header[1] == temp_ack:
                count += 1
                data_willsend += datas
                print(header_send)
                for i in range(0, 3, 1):
                    self.sendto(header_send, self.client_address)
                temp_ack += len(datas)
            if self.segment == count:
                break
        for i in range(0, 100, 1):
            time.sleep(0.01)
        print("recieve finish")
        self.seq_ack = temp_ack
        self.accept_null = False
        return data_willsend

    def send(self, content: bytes, reciver_addr):
        acked = []
        buffer = []

        base = self.seq
        now = 0

        for i in range(0, len(content), maxl):
            cl = min(maxl, len(content) - i)
            data = datagram()
            data.payload = content[i:i + cl]
            data.seq = base + now
            now += 1
            buffer.append(data)
            acked.append(False)

        tn = 0 #counting timeout number
        l, r = 0, 0
        while l < len(buffer):
            r = min(len(buffer), l + WINDOWS_SIZE)

            logging.info('Send packet from [%d, %d]' % (buffer[l].seq, buffer[r - 1].seq))
            for i in range(l, r):
                pkt = buffer[i]
                pkt.seq_ack = self.seq_ack
                self.sendto(pkt(), reciver_addr)

            while True:
                conuti = 0;
                try:
                    data, addr = self.recvfrom(2048)
                    assert addr == reciver_addr
                    tn = 0
                    logging.info('#%d acked', data.seq_ack)
                    assert buffer[l].seq <= data.seq_ack <= buffer[r - 1].seq + 1
                    l = max(l, data.seq_ack - base)
                    logging.debug('base=%d', base)
                    logging.info('Window length = %d', r - l)
                    if r - l == 0:
                        logging.info('Finish sending')
                        break
                except ValueError:
                    conuti += 1
                    continue
                except AssertionError:
                    conuti += 1
                    continue
                except BlockingIOError:
                    conuti += 1
                    continue
                except TypeError:
                    conuti += 1
                    continue
                except udp.timeout:
                    tn += 1
                    logging.info('timed out, count=%d', tn)
                    if tn > maxre:
                        raise ConnectionError('time out')
                    break
                except Exception:
                    logging.warning(Exception)

        # Finish
        nif = datagram()
        nif.dtype = NIF
        nif.seq = base + now
        nif.seq_ack = self.seq_ack
        nif_err_count = 0
        while True:
            try:
                self.sendto(nif(), reciver_addr)
                data, addr = self.recvfrom(2048)

                if data.dtype & ACK and data.dtype & NIF and data.seq_ack == base + now + 1:
                    break
            except (udp.timeout, ValueError):
                nif_err_count += 1
                if nif_err_count > maxre:
                    break
            except Exception:
                logging.warning(Exception)

        self.seq = base + now + 1
        logging.info('----------- all sent -----------')
