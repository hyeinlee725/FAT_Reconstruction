from extent import Extent
from dentry import Dentry
from br import BootRecord
from node import Node

class NodeStream:
    def __init__(self, extents, file):
        self.extents = extents
        self.file = file
        self.current_offset = 0
    
    def seek(self, offset):
        self.current_offset = offset
        self.file.seek(offset)
    
    def read(self, size):
        data = b''
        remaining = size
        offset = self.current_offset
        
        for extent in self.extents:
            if offset >= extent.start + extent.size:
                continue
            if remaining <= 0:
                break
            
            relative_offset = max(0, offset - extent.start)
            self.file.seek(extent.start + relative_offset)
            
            read_size = min(remaining, extent.size - relative_offset)
            data += self.file.read(read_size)
            
            remaining -= read_size
            offset += read_size

        self.current_offset = offset
        return data


if __name__ == "__main__":
    offsets = [0x400080, 0x404040]
    with open("./FAT32_simple1.mdf", "rb") as file:
        init_addr = file.read(0x200)
        boot_record = BootRecord(init_addr)
        
        dentries = []
        extents = []
        for offset in offsets:
            file.seek(offset)
            buffer = file.read(32)
            dentry = Dentry(buffer, boot_record)
            dentries.append(dentry)
            extents.append(Extent(offset, dentry.alloc_size))
        
        node_stream = NodeStream(extents, file)
        
        root = Node("root", True)
        node1 = Node("node_400080", dentries[0].is_dir(), root)
        node2 = Node("node_404040", dentries[1].is_dir(), root)
        
        if not node2.is_dir:
            data_read = node_stream.read(1024)
            print("Stream data read (1024 bytes):", data_read[:64])
