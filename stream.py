#!/usr/bin/env python
from extent import Extent
from dentry import Dentry
from br import BootRecord
from fatarea import FatArea

class NodeStream:
    def __init__(self, file, dentry, boot_record, fat_area):
        self.file = file
        self.dentry = dentry
        self.boot_record = boot_record
        self.fat_area = fat_area
        self.current_offset = 0
        self.size = dentry.file_size
        self.extents = self.calculate_extents()
    
    def calculate_extents(self):
        start_cluster = int(self.dentry.cluster_no, 16) & 0xFFFF
        if start_cluster < 2 or start_cluster >= len(self.fat_area.fat):
            return []
        clusters = self.fat_area.all_clusters(start_cluster)
        return [Extent(self.boot_record.root_dir_addr(cluster), self.boot_record.cluster_size) for cluster in clusters]
    
    def seek(self, offset, whence=0) -> int:
        if whence == 0:
            self.current_offset = offset
        elif whence == 1:
            self.current_offset += offset
        elif whence == 2:
            self.current_offset = max(0, self.size - offset)
        return self.current_offset

    def read(self, size):
        data = bytearray()
        remaining = min(size, self.size - self.current_offset)
        read_position = self.current_offset

        for extent in self.extents:
            if remaining <= 0:
                break

            extent_start = extent.start
            extent_end = extent.start + extent.size

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
        
        self.current_offset = read_position
        return bytes(data)

if __name__ == "__main__":
    with open("./FAT32_simple1.mdf", "rb") as file:
        boot_record = BootRecord(file.read(0x200))
        file.seek(boot_record.fat_area_addr)
        fat_area = FatArea(file.read(boot_record.fat_area_size))
        
        for offset in [0x400080, 0x404040]:
            file.seek(offset)
            dentry = Dentry(file.read(32), boot_record)
            if dentry.is_file():
                node_stream = NodeStream(file, dentry, boot_record, fat_area)
                node_stream.seek(0)
                data_read = node_stream.read(node_stream.size)
                print(f"Stream data read for {dentry.name} (first 64 bytes in hex):", data_read[:64].hex())
                print(f"Total data read size: {len(data_read)} / Expected file size: {node_stream.size}")
