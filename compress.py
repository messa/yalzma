#!/usr/bin/env python3

'''
This script emulates behavior of "xz" - it reads data from stdin, compresses
them and writes to stdout.

Useful for benchmarking.
'''

import argparse
from sys import stdin, stdout, stderr, exit
from time import monotonic as monotime
from yalzma import LZMAEncoder


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--preset', type=int, default=6)
    args = p.parse_args()
    enc = LZMAEncoder(preset=args.preset)
    stats = Stats()
    try:
        while True:
            buf = stdin.buffer.read(65536)
            if buf == b'':
                break
            out = enc.run(buf)
            stats.compressed(len(buf), len(out))
            stdout.buffer.write(out)
            stats.write_progress()
        stdout.buffer.write(enc.finish())
    except KeyboardInterrupt as e:
        exit(1)


class Stats:

    def __init__(self):
        self.start_mt = monotime()
        self.orig_size = 0
        self.compressed_size = 0
        self.next_progress_mt = self.start_mt

    def compressed(self, chunk_orig_size, chunk_compresed_size):
        self.orig_size += chunk_orig_size
        self.compressed_size += chunk_compresed_size

    def write_progress(self):
        if monotime() < self.next_progress_mt:
            return
        self.next_progress_mt += 1
        running_time_f = monotime() - self.start_mt
        running_time = int(running_time_f)
        msg = '{hours:d}:{minutes:02d}:{seconds:02d}  {comp} / {orig} = {ratio:.3f}  {speed}/s'.format(
            hours=running_time // 3600,
            minutes=(running_time // 60) % 60,
            seconds=running_time % 60,
            orig=human_readable_byte_size(self.orig_size),
            comp=human_readable_byte_size(self.compressed_size),
            ratio=self.compressed_size / self.orig_size,
            speed=human_readable_byte_size(self.orig_size / running_time_f))
        print(msg, file=stderr)


def human_readable_byte_size(n):
    if n >= 2**30:
        return '{:6.1f} GiB'.format(n / 2**30)
    elif n >= 2**20:
        return '{:6.1f} MiB'.format(n / 2**20)
    else:
        return '{:6.1f} KiB'.format(n / 2**10)


if __name__ == '__main__':
    main()
