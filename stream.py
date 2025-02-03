from extent import Extent
from dentry import Dentry
from br import BootRecord
from node import Node, NodeType

class NodeStream:
    def __init__(self, extents, file):
        self.extents = extents
        self.file = file
        self.current_offset = 0
    
    def seek(self, offset, whence=0) -> int:
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset -= offset
        else:
            raise Exception("wrong argument")
        return self.offset

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
    with open("./FAT32_simple1.mdf", "rb") as file:
        init_addr = file.read(0x200)
        boot_record = BootRecord(init_addr)

        offsets = [0x400080, 0x404040]
        dentries = []
        extents = []
        for offset in offsets:
            file.seek(offset)
            buffer = file.read(32)
            dentry = Dentry(buffer, boot_record)
            dentries.append(dentry)
            extents.append(Extent(offset, dentry.alloc_size))

        node_stream = NodeStream(extents, file)

        root = Node("root", None, NodeType.Dir)
        node1 = Node("node_400080", dentries[0], NodeType.Dir if dentries[0].is_dir() else NodeType.File)
        node2 = Node("node_404040", dentries[1], NodeType.Dir if dentries[1].is_dir() else NodeType.File)

        root.add_child(node1)
        root.add_child(node2)

        if not node2.is_dir():
            data_read = node_stream.read(1024)
            print("Stream data read (first 64 bytes):", data_read[:64])
