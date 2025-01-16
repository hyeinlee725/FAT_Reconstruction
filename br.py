#!/usr/bin/env python
from byte_buffer2 import ByteBuffer2

class BootRecord:
    def __init__(self, buffer):
        # 주요 영역의 위치, 크기 - 메타데이터 정의
        data = ByteBuffer2(buffer)
        data.offset = 0x0b
        self.sector_size = data.get_uint2_le()
        self.cluster_size = self.sector_size * data.get_uint1() # sector_count

        data.offset = 0x10
        self.num_of_fat = data.get_uint1()
        
        data.offset = 0x0e
        self.fat_area_addr = data.get_uint2_le() * self.sector_size

        data.offset = 0x24
        self.fat_area_size = data.get_uint4_le() * self.sector_size

        data.offset = 0x2C
        self.root_cluster_no = data.get_uint4_le()
        self.data_area = self.fat_area_addr + self.fat_area_size * self.num_of_fat

    def root_dir_addr(self, cluster_num):
        return self.data_area + (cluster_num - 2) * self.cluster_size  
    
    def __str__(self) -> str:
        return (
            f"Sector Size: {hex(self.sector_size)}\n"
            f"Cluster Size: {hex(self.cluster_size)}\n"
            f"Num of FAT: {hex(self.num_of_fat)}\n"
            f"FAT Area Addr: {hex(self.fat_area_addr)}\n"
            f"FAT Area Size: {hex(self.fat_area_size)}\n"
            f"Data Area: {hex(self.data_area)}\n"
            f"Root Cluster No: {hex(self.root_cluster_no)}\n"
        )

if __name__ == "__main__":
    file = open("./FAT32_simple1.mdf", "rb")
    init_addr = file.read(0x200)
    br = BootRecord(init_addr)
    print(br)
    print(hex(br.root_dir_addr(2)))
