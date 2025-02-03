#!/usr/bin/env python
from extent import Extent
from dentry import Dentry
from br import BootRecord

class Node:
    def __init__(self, name, is_dir, parent=None):
        self.name = name
        self.is_dir = is_dir
        self.parent = parent
        self.children = [] if is_dir else None
    
    def add_child(self, child):
        if self.is_dir:
            self.children.append(child)
            child.parent = self
    
    def parent_name(self):
        return self.parent.name if self.parent else "None"
    
    def __str__(self):
        if self.is_dir:
            return f"Node(name={self.name}, is_dir={self.is_dir}, parent={self.parent_name()}, children={[self.children]})"
        else:
            return f"Node(name={self.name}, is_dir={self.is_dir}, parent={self.parent_name()})"

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
        
        root = Node("root", True)
        node1 = Node("node_400080", dentries[0].is_dir(), root)
        node2 = Node("node_404040", dentries[1].is_dir(), root)
        root.add_child(node1)
        root.add_child(node2)
        
        if node1.is_dir:
            child_node = Node("child_of_400080", True, node1)
            node1.add_child(child_node)
        
        print(f"Node at {hex(offsets[0])}: {node1}")
        if node1.is_dir:
            print(f"Children of node1: {node1.children}")
        
        print(f"Node at {hex(offsets[1])}: {node2}")
