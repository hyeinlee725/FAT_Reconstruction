#!/usr/bin/env python
from byte_buffer2 import ByteBuffer2
from br import BootRecord

class Fat_analyzer:
    def __init__(self, buffer,boot_recore):
        self.data = ByteBuffer2(buffer)
        self.br = boot_recore
        self.fat_start = br.fat_area_addr
        self.fat_entry_size = 4
    
    def read_fat_entry(self, cluster_num):
        self.data.offset = self.fat_start + (cluster_num * self.fat_entry_size)
        return self.data.get_uint4_le() & 0x0FFFFFFF # 28bit
    
    def build_cluster_chain(self, start_cluster, visited):
        chain = []
        current_cluster = start_cluster

        while current_cluster < 0xFFFFFF8 and current_cluster not in visited:
            chain.append(current_cluster)
            visited.add(current_cluster)
            next_cluster = self.read_fat_entry(current_cluster)
            if next_cluster < 2 or next_cluster >= 0xFFFFFF8:
                break
            current_cluster = next_cluster
        return chain

    def analyze_clusters(self):
        cluster_chains = {}
        visited = set()
        total_clusters = (self.br.data_area // self.br.cluster_size) + 2

        for cluster in range(2, total_clusters):
            if cluster not in visited:
                chain = self.build_cluster_chain(cluster, visited)
                if chain:
                    cluster_chains[cluster] = chain

        return cluster_chains

    def print_cluster_chains(self, cluster_chains):
        for start_cluster, chain in cluster_chains.items():
            print(f"Cluster {hex(start_cluster)} -> {', '.join(map(lambda x: hex(x), chain))}")

if __name__ == "__main__":
    file = open("./FAT32_simple1.mdf", "rb")
    file_content = file.read()

    init_buffer = file_content[:0x200]
    br = BootRecord(init_buffer)

    fat_analyzer = Fat_analyzer(file_content, br)
    cluster_chains = fat_analyzer.analyze_clusters()
    fat_analyzer.print_cluster_chains(cluster_chains)