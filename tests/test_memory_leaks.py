from os import urandom
from pathlib import Path
from pytest import skip

from yalzma import LZMAEncoder


sample_data = urandom(1000) + 1000 * b'test'


def run():
    x = LZMAEncoder()
    compressed = x.run(sample_data) + x.finish()
    del x


def status():
    st = {}
    for line in Path('/proc/self/status').read_text().splitlines():
        k, v = line.split(':', 1)
        st[k.strip()] = v.strip()
    return st


def test_memory_leaks():
    try:
        st = status()
    except FileNotFoundError as e:
        skip(str(e))
    run()
    st = status()
    vm_peak_before = st['VmPeak']
    for i in range(100):
        run()
    st = status()
    vm_peak_after = st['VmPeak']
    assert vm_peak_after == vm_peak_before
