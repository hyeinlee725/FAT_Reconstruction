#!/usr/bin/env python
from byte_buffer2 import ByteBuffer2

class Dentry:
    def __init__(self, buffer):
        self.data = ByteBuffer2(buffer)
        self._parse_entry()

    def _parse_entry(self):
        self.data.offset = 0
        self.name = self.data.get_ascii(8).strip()
        extension = self.data.get_ascii(3).strip()
        self.attr = self.data.get_uint1()
        self.data.offset = 0x14
        cluster_hi = self.data.get_uint2_le()
        self.data.offset = 0x1A
        cluster_lo = self.data.get_uint2_le()
        self.cluster_no = hex((cluster_lo << 8) | cluster_hi)
        self.file_size = self.data.get_uint4_le()
        if self.is_file():
            self.name = f"{self.name}.{extension}" if extension else self.name

    def alloc_size(self, cluster_size, fat_table):
        cluster_count = len(fat_table.all_clusters(int(self.cluster_no, 16)))
        return cluster_count * cluster_size

    def is_vol(self):
        return self.attr & 0x08 != 0

    def is_dir(self):
        return self.attr & 0x10 != 0

    def is_file(self):
        return not self.is_vol() and not self.is_dir()

    def is_lfn(self):
        return self.attr & 0x0F == 0x0F

    def __str__(self):
        return (f"Name: {self.name}\n"
                f"Attribute: {hex(self.attr)}\n"
                f"Cluster: {self.cluster_no}\n"
                f"File Size: {hex(self.file_size)} bytes\n"
                f"Directory: {self.is_dir()}\n"
                f"File: {self.is_file()}\n"
                f"Volume: {self.is_vol()}\n"
                f"LFN: {self.is_lfn()}\n")

if __name__ == "__main__":
    with open("./FAT32_simple1.mdf", "rb") as file:
        offsets = [0x400080, 0x404040]
        dentries = [Dentry(file.read(32)) for offset in offsets for _ in [file.seek(offset)]]
        for entry in dentries:
            print(entry)
