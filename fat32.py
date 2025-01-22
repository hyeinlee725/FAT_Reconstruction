#!/usr/bin/env python
from collections import defaultdict
from pprint import pprint
from br import BootRecord
from fatarea import FatArea
from dentry import Dentry

class Fat32:
    def __init__(self, file_path):
        self.file_path = file_path
        self.boot_record = None
        self.fat_area = None
        self.fs = defaultdict(dict)
    
    def read_boot_record(self):
        with open(self.file_path, 'rb') as file:
            file.seek(0)
            init_addr = file.read(0x200)
            self.boot_record = BootRecord(init_addr)

    def read_fat_area(self):
        with open(self.file_path, 'rb') as file:
            file.seek(self.boot_record.fat_area_addr)
            buffer = file.read(self.boot_record.fat_area_size)
            self.boot_record = BootRecord(buffer)

    def read_root_directory(self):
        root_dir_addr = self.boot_record.root_dir_addr(self.boot_record.root_cluster_no)
        self.fs['/'] = self.read_directory(root_dir_addr)

    def read_directory(self, dir_addr):
        dentries = []
        with open(self.file_path, 'rb') as file:
            file.seek(dir_addr)
            while True:
                buffer = file.read(32)
                if len(buffer) < 32:
                    break
                dentry = Dentry(buffer)
                dentries.append(dentry)
                if dentry.is_dir() and not dentry.is_lfn():
                    dir_cluster = int(dentry.cluster_no(), 16)
                    if dir_cluster != 0x0:
                        sub_dir_addr = self.boot_record.root_dir_addr(dir_cluster)
                        sub_dentries = self.read_directory(sub_dir_addr)
                        self.fs[dentry.name] = sub_dentries
        return dentries

    def build_filesystem(self):
        self.read_boot_record()
        self.read_fat_area()
        self.read_root_directory()
        return self.fs

if __name__ == "__main__":
    fat32 = Fat32("./FAT32_simple1.mdf")
    fs = fat32.build_filesystem()

    pprint(fs)
