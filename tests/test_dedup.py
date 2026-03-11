#!/usr/bin/env python3
"""
测试用例
"""

import unittest
import os
import tempfile
from pathlib import Path

from image_hasher import ImageHasher
from duplicate_finder import DuplicateFinder
from utils import format_size, get_image_files, is_image_file


class TestImageHasher(unittest.TestCase):
    """测试图像哈希模块"""
    
    def setUp(self):
        self.hasher = ImageHasher(hash_size=8)
    
    def test_hamming_distance(self):
        """测试汉明距离计算"""
        hash1 = "ffffffff"
        hash2 = "ffffffff"
        self.assertEqual(ImageHasher.hamming_distance(hash1, hash2), 0)
        
        hash3 = "00000000"
        self.assertEqual(ImageHasher.hamming_distance(hash1, hash3), 8)
    
    def test_similarity(self):
        """测试相似度计算"""
        hash1 = "ffffffff"
        hash2 = "ffffffff"
        self.assertEqual(ImageHasher.similarity(hash1, hash2), 1.0)
        
        hash3 = "00000000"
        sim = ImageHasher.similarity(hash1, hash3)
        self.assertEqual(sim, 0.0)


class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_format_size(self):
        """测试文件大小格式化"""
        self.assertEqual(format_size(512), "512 B")
        self.assertEqual(format_size(1024), "1.0 KB")
        self.assertEqual(format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(format_size(1024 * 1024 * 1024), "1.00 GB")
    
    def test_is_image_file(self):
        """测试图片文件判断"""
        self.assertTrue(is_image_file("test.jpg"))
        self.assertTrue(is_image_file("test.JPG"))
        self.assertTrue(is_image_file("test.png"))
        self.assertFalse(is_image_file("test.txt"))
        self.assertFalse(is_image_file("test.exe"))


class TestDuplicateFinder(unittest.TestCase):
    """测试重复查找器"""
    
    def setUp(self):
        self.finder = DuplicateFinder(threshold=0.9)
    
    def test_find_exact_duplicates(self):
        """测试查找完全重复"""
        # 模拟哈希数据
        hashes = {
            "/path/to/img1.jpg": "abc123",
            "/path/to/img2.jpg": "abc123",  # 完全重复
            "/path/to/img3.jpg": "def456",
            "/path/to/img4.jpg": "def456",  # 完全重复
            "/path/to/img5.jpg": "xyz789",  # 唯一
        }
        
        duplicates = self.finder.find_exact_duplicates(hashes)
        
        # 应该找到 2 组重复
        self.assertEqual(len(duplicates), 2)
        
        # 检查每组大小
        group_sizes = [len(g) for g in duplicates]
        self.assertIn(2, group_sizes)


if __name__ == '__main__':
    unittest.main()
