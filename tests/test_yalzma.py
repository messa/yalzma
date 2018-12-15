from io import BytesIO
from lzma import decompress, open as lzma_open
from os import urandom

from yalzma import LZMAEncoder


def test_samples():
    samples = [
        b'',
        b'Hello!',
        b''.join(bytes([i]) for i in range(256)),
        urandom(10),
        urandom(100),
    ]
    for sample in samples:

        x = LZMAEncoder()
        data = x.run(sample) + x.finish()
        assert decompress(data) == sample

        split_points = range(len(sample))
        for i in split_points:

            x = LZMAEncoder()
            data = x.run(sample[:i]) + x.run(sample[i:]) + x.finish()
            assert decompress(data) == sample

            x = LZMAEncoder()
            data = x.run(sample[:i]) + x.sync_flush() + x.run(sample[i:]) + x.finish()
            assert decompress(data) == sample

            x = LZMAEncoder()
            data = x.run(sample[:i]) + x.sync_flush()
            f = lzma_open(BytesIO(data), mode='rb')
            assert f.read(i) == sample[:i]
