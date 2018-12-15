def test_readme_usage_example():
    from yalzma import LZMAEncoder
    import lzma

    text = b'Hello, World!'
    enc = LZMAEncoder()
    xz_data = enc.run(text)
    xz_data += enc.finish()
    assert lzma.decompress(xz_data) == text

    # Demonstration of the flush functionality:

    from io import BytesIO

    enc = LZMAEncoder()
    xz_data = enc.run(b'first line\n')
    xz_data += enc.sync_flush()
    assert lzma.open(BytesIO(xz_data), mode='rb').readline() == b'first line\n'

    xz_data += enc.run(b'second line\n')
    xz_data += enc.finish()
    assert lzma.decompress(xz_data) == b'first line\nsecond line\n'
