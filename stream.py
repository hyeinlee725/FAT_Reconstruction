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
    
    def read(self, size):
        data = b''
        remaining = size
        
        for extent in self.extents:
            if remaining <= 0:
                break
            
            self.file.seek(extent.start)
            read_size = min(remaining, extent.size)
            data += self.file.read(read_size)
            remaining -= read_size
        
        return data
    
    def read_all(self):
        return self.read(sum(extent.size for extent in self.extents))

if __name__ == "__main__":
    offsets = [0x400080, 0x404040]
    with open("./FAT32_simple1.mdf", "rb") as file:
        init_addr = file.read(0x200)
        boot_record = BootRecord(init_addr)
        
        dentries = []
        extents = []
        nodes = {}
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
        root.add_child(node1)
        root.add_child(node2)

        if not node2.is_dir:
            data_read = node_stream.read(1024)
            print("Stream data read:", data_read[:64])
