#!/usr/bin/env python
 
from byte_buffer2 import *
from functools import reduce
 
class FatArea:
    def __init__(self, buffer):
        self.entry_count = len(buffer) // 4
        bb = ByteBuffer2(buffer)
        self.fat = []
        for i in range(0, self.entry_count):
            self.fat.append(bb.get_uint4_le())
 
    def all_clusters(self, start):
        clusters = []
        next = start
        while next != 0xfffffff:
            clusters.append(next)
            next = self.fat[next]
 
        return clusters
 
    def __str__(self):
        # check only some entries of fat0
        res = self.fat[2:10]
        return reduce(lambda acc, cur: f"{acc}, {hex(cur)}", res, "")
 
if __name__ == "__main__":
    file = open("./FAT32_simple1.mdf", 'rb')
    file.seek(0x215c00)
    b0 = file.read(0x200)
    fat0 = FatArea(b0)
    print(fat0)
