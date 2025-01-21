#!/usr/bin/env python
 
from fat32 import *
 
import pprint
 
fat32 = Fat32("./FAT32_simple1.mdf")
fs = fat32.build_filesystem()
 
pprint.pp(fs.nodes.keys())
leaf = fs["/DIR1/leaf.jpg"]
leaf.export_to("/Users/yielding/Desktop/leaf.jpg")
port = fs["/DIR1/PORT.JPG"]
port.export_to("/Users/yielding/Desktop/port.jpg")
port = fs["/DIR1/thumb_nail.py"]
port.export_to("/Users/yielding/Desktop/thumb_nail.py")
port = fs["/?iger.jpg"]
port.export_to("/Users/yielding/Desktop/tiger.jpg")
