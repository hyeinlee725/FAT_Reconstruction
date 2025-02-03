#!/usr/bin/env python
from enum import Enum
from extent import Extent
from dentry import Dentry
from br import BootRecord

class NodeType(Enum):
    File = 1
    Dir = 2
    SymLink = 3
    HardLink = 4

class State(Enum):
    Normal = 1
    Deleted = 2

class Node:
    def __init__(self, name, stream=None, type=NodeType.File, stat=State.Normal) -> None:
        self.name = name
        self.path = name
        self.stream = stream
        self.alloc_size = stream.alloc_size if stream else 0 
        self.size = stream.file_size if stream else 0
        self.parent = None
        self.children = []
        self.type = type
        self.stat = stat

    def is_file(self):
        return self.type == NodeType.File

    def is_dir(self):
        return self.type == NodeType.Dir

    def is_expandable(self):
        return self.is_dir()

    def is_root(self):
        return self.parent is None

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def clear_children(self):
        self.children.clear()

    def read_all(self):
        if self.is_file() and self.stream:
            return self.stream.read(self.size)
        return None

    def export_to(self, path):
        if self.is_file() and self.stream:
            with open(path, "wb") as f:
                f.write(self.read_all())

    def __str__(self) -> str:
        return f"path: {self.path}, size: {hex(self.size)}, type: {self.type.name}"

if __name__ == "__main__":
    with open("./FAT32_simple1.mdf", "rb") as file:
        init_addr = file.read(0x200)
        boot_record = BootRecord(init_addr)

        offsets = [0x400080, 0x404040]
        dentries = []
        for offset in offsets:
            file.seek(offset)
            buffer = file.read(32)
            dentries.append(Dentry(buffer, boot_record))

        root = Node("root", None, NodeType.Dir)
        node1 = Node("node_400080", dentries[0] if dentries[0].is_file() else None, NodeType.Dir if dentries[0].is_dir() else NodeType.File)
        node2 = Node("node_404040", dentries[1] if dentries[1].is_file() else None, NodeType.Dir if dentries[1].is_dir() else NodeType.File)

        root.add_child(node1)
        root.add_child(node2)

        print("File System Structure:")
        print(root)
        for child in root.children:
            print(f" - {child}")
