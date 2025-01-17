from byte_buffer2 import ByteBuffer2
from functools import reduce

class Dentry:
    def __init__(self, buffer):
        self.data = ByteBuffer2(buffer)
        self.name = self.data.get_ascii(8).strip()
        self.extension = self.data.get_ascii(3).strip()
        self.attr = self.data.get_uint1()
        self.data.offset = 0x14
        self.cluster_hi = self.data.get_uint2_le()
        self.data.offset = 0x1A
        self.cluster_lo = self.data.get_uint2_le()
        self.file_size = self.data.get_uint4_le()

    def cluster_no(self):
        return hex((self.cluster_lo << 8) | self.cluster_hi)
        
    def is_vol(self):
        return self.attr & 0x08 != 0

    def is_dir(self):
        return self.attr & 0x10 != 0

    def is_file(self):
        return not self.is_vol() and not self.is_dir()

    def is_lfn(self):
        return self.attr & 0x0F == 0x0F
    
    def dentries_class(dentries, key_func, init_val):
        return reduce(lambda acc, entry: acc + key_func(entry), dentries, init_val)
        pass
    def __str__(self):
        return (f"Name: {self.name}.{self.extension}\n"
                f"Attribute: {hex(self.attr)}\n"
                f"Cluster: {self.cluster_no()}\n"
                f"File Size: {hex(self.file_size)} bytes\n"
                f"Directory: {self.is_dir()}\n"
                f"File: {self.is_file()}\n"
                f"Volume: {self.is_vol()}\n"
                f"LFN: {self.is_lfn()}\n")

# Test Case
if __name__ == "__main__":
     with open("./FAT32_simple1.mdf", "rb") as file:
        offsets = [0x400080, 0x404040]
        dir_buffers = [file.read(32) for offset in offsets for _ in [file.seek(offset)]]
        dentries = [Dentry(buffer) for buffer in dir_buffers]
        for entry in dentries:
            print(str(entry))
