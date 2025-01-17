from byte_buffer2 import ByteBuffer2
from functools import reduce

class Dentry:
    def __init__(self, buffer):
        self.data = ByteBuffer2(buffer)
        self.name = self.data.get_ascii(8).strip()
        self.extension = self.data.get_ascii(3).strip()
        self.attr = self.data.get_uint1()
        self.first_cluster_high = self.data.get_uint2_le()
        self.first_cluster_low = self.data.get_uint2_le()
        self.file_size = self.data.get_uint4_le()

    def is_vol(self):
        return self.attr & 0x08 != 0

    def is_dir(self):
        return self.attr & 0x10 != 0

    def is_file(self):
        return not self.is_vol() and not self.is_dir()

    def lfn(self):
        return self.attr & 0x0F == 0x0F

    def cluster_no(self):
        return (self.first_cluster_high << 16) | self.first_cluster_low    

    def __str__(self):
        return (f"Name: {self.name}.{self.extension}\n"
                f"Attribute: {hex(self.attr)}\n"
                f"Cluster: {self.cluster_no()}\n"
                f"File Size: {self.file_size} bytes\n"
                f"Directory: {self.is_dir()}\n "
                f"File: {self.is_file()}\n"
                f"Volume: {self.is_vol()}\n"
                f"LFN: {self.lfn()}")

# Test Case
if __name__ == "__main__":
    file = open("./FAT32_simple1.mdf", "rb")
    file.seek(0x404040) # 0x404040 # 0x400080
    dir_buffer = file.read(32)
    dentry = Dentry(dir_buffer)
    print(dentry)
