Yet another LZMA Python wrapper
===============================

This time with support for LZMA_SYNC_FLUSH :tada:

Works directly with liblzma.so via [ctypes](https://docs.python.org/3/library/ctypes.html).
No other dependencies.


What is LZMA?
-------------

LZMA is a compression algorithm - like gzip or bzip2.

The default configuration (of both Python [lzma module](https://docs.python.org/3/library/lzma.html) and this library)
is to use the LZMA2 filter and XZ container format.
So you can directly save the compressed data in a file with the `.xz` suffix and it will work with many other
programs, utilities and systems. For example `xzcat` or `xzgrep`.

Wikipedia: [Lempel–Ziv–Markov chain algorithm](https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Markov_chain_algorithm)

Lot of software uses LZMA compression internally. For example many software package managers.


But why? Python standard library already contains lzma module…
--------------------------------------------------------------

Yes, but it does not support the SYNC FLUSH operation.

There is [`LZMACompressor.flush()`](https://docs.python.org/3/library/lzma.html#lzma.LZMACompressor.flush)
but it does something different - it
[finishes the compression process](https://github.com/python/cpython/blob/0353b4eaaf451ad463ce7eb3074f6b62d332f401/Modules/_lzmamodule.c#L568)
and closes the compressor.
It is not possible to compress more data after `flush()`.

For some of my use cases I need to use "sync flush". The constant `LZMA_SYNC_FLUSH`
[does not even appear in the CPython source code](https://github.com/python/cpython/search?q=LZMA_SYNC_FLUSH&unscoped_q=LZMA_SYNC_FLUSH).


What is LZMA_SYNC_FLUSH?
------------------------

From `lzma/base.h` (by Lasse Collin, public domain):

```c
        LZMA_SYNC_FLUSH = 1,
                /**<
                 * \brief       Make all the input available at output
                 *
                 * Normally the encoder introduces some latency.
                 * LZMA_SYNC_FLUSH forces all the buffered data to be
                 * available at output without resetting the internal
                 * state of the encoder. This way it is possible to use
                 * compressed stream for example for communication over
                 * network.
                 *
                 * Only some filters support LZMA_SYNC_FLUSH. Trying to use
                 * LZMA_SYNC_FLUSH with filters that don't support it will
                 * make lzma_code() return LZMA_OPTIONS_ERROR. For example,
                 * LZMA1 doesn't support LZMA_SYNC_FLUSH but LZMA2 does.
                 *
                 * Using LZMA_SYNC_FLUSH very often can dramatically reduce
                 * the compression ratio. With some filters (for example,
                 * LZMA2), fine-tuning the compression options may help
                 * mitigate this problem significantly (for example,
                 * match finder with LZMA2).
                 *
                 * Decoders don't support LZMA_SYNC_FLUSH.
                 */
```


Installation
------------

Tested on [Debian Linux](https://www.debian.org) and macOS.

You need to have liblzma installed - that means there should be a file
`liblzma.so` (for Linux) or `liblzma.dylib` (for macOS) somewhere in a library
directory (`/usr/lib` or similar). Usually it is already installed.

Install yalzma from current Github master:

```sh
$ pip install git+https://github.com/messa/yalzma
```

Install specific version:

```sh
$ pip install git+https://github.com/messa/yalzma.git@v0.0.4
```

Or add this line to your `requirements.txt`:

```
git+https://github.com/messa/yalzma@v0.0.4#egg=yalzma==0.0.4
```


Usage
-----

```python
from yalzma import LZMAEncoder
import lzma

text = b'Hello, World!'
enc = LZMAEncoder()
xz_data = enc.run(text)
xz_data += enc.finish()
assert lzma.decompress(xz_data) == text
```

Demonstration of the flush functionality:

```python
from io import BytesIO

enc = LZMAEncoder()
xz_data = enc.run(b'first line\n')
xz_data += enc.sync_flush()
assert lzma.open(BytesIO(xz_data), mode='rb').readline() == b'first line\n'

xz_data += enc.run(b'second line\n')
xz_data += enc.finish()
assert lzma.decompress(xz_data) == b'first line\nsecond line\n'
```
