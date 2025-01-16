#!/usr/bin/env python
from byte_buffer2 import ByteBuffer2
from br import BootRecord

class FAT:
    def __init__(self, buffer, boot_record):
        self.fat_data = ByteBuffer2(buffer)
        self.br = boot_record
        
    def get_next_cluster(self, cluster_num):
        offset = cluster_num * 4
        self.fat_data.offset = offset
        next_cluster = self.fat_data.get_uint4_le()

        if next_cluster >= 0xFFFFFF8:
            return None
        elif next_cluster == 0xFFFFFF7:
            raise ValueError(f"Bad cluster: {cluster_num}")
        return next_cluster

    def get_cluster_chain(self, start_cluster):
        cluster_chain = []
        current_cluster = start_cluster

        while current_cluster:
            cluster_chain.append(current_cluster)
            current_cluster = self.get_next_cluster(current_cluster)

        return cluster_chain

    def get_data_area_address(self, cluster_num):
        return self.br.data_area + (cluster_num - 2) * self.br.cluster_size

if __name__ == "__main__":
    with open("./FAT32_simple1.mdf", "rb") as file:
        init_addr = file.read(0x200)
        br = BootRecord(init_addr)

        file.seek(br.fat_area_addr)
        fat_data = file.read(br.fat_area_size)

        fat = FAT(br, fat_data)

        start_cluster = 6
        cluster_chain = fat.get_cluster_chain(start_cluster)

        print(f"Cluster Chain: {cluster_chain}")
        for cluster in cluster_chain:
            data_addr = fat.get_data_area_address(cluster)
            print(f"Cluster {cluster} Data Address: {hex(data_addr)}")
