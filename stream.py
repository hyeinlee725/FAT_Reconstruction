#!/usr/bin/env python
from br import BootRecord
from dentry import Dentry
from fatarea import FatArea
from extent import Extent

class NodeStream:
    def __init__(self, extent):
        self.file = extent.file
        self.offset = 0
        self.size = extent.size
        self.extents = extent.extents
    
    def seek(self, offset, whence=0) -> int:
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = max(0, self.size - offset)
        return self.offset
    
    def read(self, size):
        data = bytearray()
        remaining = min(size, self.size - self.offset)
        read_position = self.offset
        
        for extent_start, extent_size in self.extents:
            if remaining <= 0:
                break
            extent_end = extent_start + extent_size
            if read_position >= extent_end:
                continue
            
            se = max(extent_start, read_position)
            ee = min(extent_end, se + remaining)
            read_size = max(0, ee - se)
            if read_size > 0:
                self.file.seek(se)
                data.extend(self.file.read(read_size))
                remaining -= read_size
                read_position += read_size
        
        self.offset = read_position
        return bytes(data)

if __name__ == "__main__":        
    with open("./FAT32_simple1.mdf", "rb") as file:
        boot_record = BootRecord(file.read(0x200))
        file.seek(boot_record.fat_area_addr)
        fat_area = FatArea(file.read(boot_record.fat_area_size))
        
        offset = 0x404040
        file.seek(offset)
        dentry = Dentry(file.read(32), boot_record)
        
        if dentry.is_file():
            extent = Extent(file, dentry, boot_record, fat_area)
            node_stream = NodeStream(extent)
            node_stream.seek(0)
            data_read = node_stream.read(node_stream.size)
            print(f"Stream data read (first 64 bytes in hex):", data_read[:64].hex())
            print(f"Total data read size: {hex(len(data_read))} / Expected file size: {hex(node_stream.size)}")
