import ctypes
import logging


DEFAULT_PRESET = 6

logger = logging.getLogger(__name__)


_liblzma = None

try_names = [
    'liblzma.so.5',
    'liblzma.so',
    'liblzma.dylib',
]

def get_liblzma():
    global _liblzma
    if _liblzma is None:
        for name in try_names:
            try:
                _liblzma = ctypes.cdll.LoadLibrary(name)
            except OSError as e:
                logging.debug('Failed to load library %r: %r', name, e)
                continue
            else:
                logging.debug('Succeeded to load library %r', name)
                break
        else:
            assert _liblzma is None
            raise Exception('Failed to import liblzma - is it installed?')
        assert _liblzma
    return _liblzma


LZMA_CHECK_CRC64 = 4
LZMA_OK = 0
LZMA_STREAM_END = 1
LZMA_RUN = 0
LZMA_SYNC_FLUSH = 1
LZMA_FINISH = 3


# typedef struct {
#         const uint8_t *next_in; /**< Pointer to the next input byte. */
#         size_t avail_in;    /**< Number of available input bytes in next_in. */
#         uint64_t total_in;  /**< Total number of bytes read by liblzma. */
#
#         uint8_t *next_out;  /**< Pointer to the next output position. */
#         size_t avail_out;   /**< Amount of free space in next_out. */
#         uint64_t total_out; /**< Total number of bytes written by liblzma. */
#
#         ...
# } lzma_stream;

sizeof_lzma_stream = 136


class LZMAStream (ctypes.Structure):

    _fields_ = [
        ('next_in', ctypes.POINTER(ctypes.c_char)),
        ('avail_in', ctypes.c_size_t),
        ('total_in', ctypes.c_uint64),
        ('next_out', ctypes.POINTER(ctypes.c_char)),
        ('avail_out', ctypes.c_size_t),
        ('total_out', ctypes.c_uint64),
        ('reserved', ctypes.c_byte * sizeof_lzma_stream),
    ]


class LZMAEncoder:

    def __init__(self, preset=DEFAULT_PRESET):
        self._needs_free = False
        self.liblzma = get_liblzma()
        self.stream = LZMAStream()
        self.stream_ptr = ctypes.pointer(self.stream)
        ret = self.liblzma.lzma_easy_encoder(self.stream_ptr, preset, LZMA_CHECK_CRC64)
        if ret != LZMA_OK:
            raise Exception('lzma_easy_encoder failed: {}'.format(ret))
        self._needs_free = True

    def __del__(self):
        if self._needs_free:
            self.liblzma.lzma_end(self.stream_ptr)
            self._needs_free = False

    def run(self, data):
        assert isinstance(data, bytes)
        compressed_data = []
        self.stream.next_in = ctypes.create_string_buffer(data)
        self.stream.avail_in = len(data)
        out_buf_size = 65536
        out_buf = ctypes.create_string_buffer(out_buf_size)
        self.stream.next_out = out_buf
        self.stream.avail_out = out_buf_size
        while self.stream.avail_in > 0:
            ret = self.liblzma.lzma_code(self.stream_ptr, LZMA_RUN)
            write_size = out_buf_size - self.stream.avail_out
            if write_size:
                compressed_data.append(out_buf.raw[:write_size])
                self.stream.next_out = out_buf
                self.stream.avail_out = out_buf_size
            if ret != LZMA_OK:
                if ret == LZMA_STREAM_END:
                    break
                else:
                    raise Exception('lzma_code failed: {}'.format(ret))
        assert self.stream.avail_out == out_buf_size
        return b''.join(compressed_data)

    def sync_flush(self):
        compressed_data = []
        out_buf_size = 4096
        out_buf = ctypes.create_string_buffer(out_buf_size)
        self.stream.next_out = out_buf
        self.stream.avail_out = out_buf_size
        while True:
            ret = self.liblzma.lzma_code(self.stream_ptr, LZMA_SYNC_FLUSH)
            write_size = out_buf_size - self.stream.avail_out
            if write_size:
                compressed_data.append(out_buf.raw[:write_size])
                self.stream.next_out = out_buf
                self.stream.avail_out = out_buf_size
            if ret != LZMA_OK:
                if ret == LZMA_STREAM_END:
                    break
                else:
                    raise Exception('lzma_code failed: {}'.format(ret))
        assert self.stream.avail_out == out_buf_size
        return b''.join(compressed_data)

    def finish(self):
        compressed_data = []
        out_buf_size = 4096
        out_buf = ctypes.create_string_buffer(out_buf_size)
        self.stream.next_out = out_buf
        self.stream.avail_out = out_buf_size
        while True:
            ret = self.liblzma.lzma_code(self.stream_ptr, LZMA_FINISH)
            write_size = out_buf_size - self.stream.avail_out
            if write_size:
                compressed_data.append(out_buf.raw[:write_size])
                self.stream.next_out = out_buf
                self.stream.avail_out = out_buf_size
            if ret != LZMA_OK:
                if ret == LZMA_STREAM_END:
                    break
                else:
                    raise Exception('lzma_code failed: {}'.format(ret))
        assert self.stream.avail_out == out_buf_size
        self.liblzma.lzma_end(self.stream_ptr)
        self._needs_free = False
        del self.stream
        del self.stream_ptr
        return b''.join(compressed_data)
