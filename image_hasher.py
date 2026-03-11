#!/usr/bin/env python3
"""
图像哈希算法模块
使用感知哈希 (Perceptual Hash) 算法计算图片指纹
"""

import cv2
import numpy as np
from PIL import Image
import imagehash
from pathlib import Path
from typing import Optional


class ImageHasher:
    """图像哈希计算器"""
    
    def __init__(self, hash_size: int = 16):
        """
        初始化哈希计算器
        
        Args:
            hash_size: 哈希大小，越大越精确但计算量越大
        """
        self.hash_size = hash_size
    
    def compute_hash(self, image_path: str) -> Optional[str]:
        """
        计算图片的感知哈希值
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            哈希字符串，失败返回 None
        """
        try:
            # 使用 PIL 打开图片
            with Image.open(image_path) as img:
                # 转换为 RGB（处理各种格式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 计算感知哈希 (pHash)
                # 使用 whash (小波哈希) 对图片变化更鲁棒
                hash_value = imagehash.whash(img, hash_size=self.hash_size)
                return str(hash_value)
                
        except Exception as e:
            print(f"计算哈希失败 {image_path}: {e}")
            return None
    
    def compute_phash(self, image_path: str) -> Optional[str]:
        """
        计算图片的 pHash (感知哈希)
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            哈希字符串，失败返回 None
        """
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 使用 phash
                hash_value = imagehash.phash(img, hash_size=self.hash_size)
                return str(hash_value)
                
        except Exception as e:
            print(f"计算 pHash 失败 {image_path}: {e}")
            return None
    
    def compute_dhash(self, image_path: str) -> Optional[str]:
        """
        计算图片的 dHash (差异哈希)
        对图片的轻微变化更敏感
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            哈希字符串，失败返回 None
        """
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                hash_value = imagehash.dhash(img, hash_size=self.hash_size)
                return str(hash_value)
                
        except Exception as e:
            print(f"计算 dHash 失败 {image_path}: {e}")
            return None
    
    def compute_combined_hash(self, image_path: str) -> Optional[str]:
        """
        计算组合哈希 (pHash + dHash)
        提高检测精度
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            组合哈希字符串，失败返回 None
        """
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 组合多种哈希
                phash = imagehash.phash(img, hash_size=self.hash_size)
                dhash = imagehash.dhash(img, hash_size=self.hash_size)
                whash = imagehash.whash(img, hash_size=self.hash_size)
                
                # 组合成字符串
                combined = f"{phash}_{dhash}_{whash}"
                return combined
                
        except Exception as e:
            print(f"计算组合哈希失败 {image_path}: {e}")
            return None
    
    @staticmethod
    def hamming_distance(hash1: str, hash2: str) -> int:
        """
        计算两个哈希值的汉明距离
        
        Args:
            hash1: 第一个哈希值
            hash2: 第二个哈希值
            
        Returns:
            汉明距离（不同位的数量）
        """
        if len(hash1) != len(hash2):
            # 处理组合哈希的情况
            if '_' in hash1 and '_' in hash2:
                parts1 = hash1.split('_')
                parts2 = hash2.split('_')
                distances = []
                for p1, p2 in zip(parts1, parts2):
                    if len(p1) == len(p2):
                        dist = sum(c1 != c2 for c1, c2 in zip(p1, p2))
                        distances.append(dist)
                return sum(distances) // len(distances) if distances else 64
            return 64
        
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
    
    @staticmethod
    def similarity(hash1: str, hash2: str) -> float:
        """
        计算两个哈希值的相似度
        
        Args:
            hash1: 第一个哈希值
            hash2: 第二个哈希值
            
        Returns:
            相似度 (0-1)，1 表示完全相同
        """
        distance = ImageHasher.hamming_distance(hash1, hash2)
        max_distance = len(hash1) * 4  # 十六进制每位 4 个比特
        
        # 处理组合哈希
        if '_' in hash1:
            parts = hash1.split('_')
            max_distance = sum(len(p) * 4 for p in parts)
        
        similarity = 1 - (distance / max_distance)
        return max(0, min(1, similarity))
