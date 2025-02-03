#!/usr/bin/env python
from br import BootRecord
from dentry import Dentry

class Extent:
    def __init__(self, start, size):
        self.start = start
        self.size = size

    def __str__(self):
        return f"Extent(start={hex(self.start)}, size={hex(self.size)})"

if __name__ == "__main__":
    offsets = [0x400080, 0x404040]
    with open("./FAT32_simple1.mdf", "rb") as file:
        init_addr = file.read(0x200)
        boot_record = BootRecord(init_addr)
        
        extents = []
        for offset in offsets:
            file.seek(offset)
            buffer = file.read(32)
            dentry = Dentry(buffer, boot_record)
            extents.append(Extent(offset, dentry.alloc_size))
        
        for extent in extents:
            print(f"Checking extent: {extent}")