#!/usr/bin/env python3
"""
重复图片查找器
使用哈希值比较找出相似的图片
"""

from typing import Dict, List, Tuple
from collections import defaultdict
from image_hasher import ImageHasher


class DuplicateFinder:
    """重复图片查找器"""
    
    def __init__(self, threshold: float = 0.9):
        """
        初始化查找器
        
        Args:
            threshold: 相似度阈值 (0-1)，高于此值认为是重复
        """
        self.threshold = threshold
        self.hasher = ImageHasher()
    
    def find_duplicates(self, hashes: Dict[str, str]) -> List[List[Tuple[str, float]]]:
        """
        从哈希字典中查找重复图片
        
        Args:
            hashes: {图片路径: 哈希值} 的字典
            
        Returns:
            重复组列表，每组是 (图片路径, 相似度) 的列表
        """
        if len(hashes) < 2:
            return []
        
        # 转换为列表便于处理
        items = list(hashes.items())
        n = len(items)
        
        # 构建相似度图
        similar_pairs = []
        
        print(f"🔍 比较 {n} 张图片的相似度...")
        
        for i in range(n):
            for j in range(i + 1, n):
                path1, hash1 = items[i]
                path2, hash2 = items[j]
                
                # 计算相似度
                similarity = self.hasher.similarity(hash1, hash2)
                
                if similarity >= self.threshold:
                    similar_pairs.append((path1, path2, similarity))
        
        # 使用并查集将相似的图片分组
        return self._group_duplicates(similar_pairs)
    
    def _group_duplicates(self, similar_pairs: List[Tuple[str, str, float]]) -> List[List[Tuple[str, float]]]:
        """
        使用并查集将相似图片分组
        
        Args:
            similar_pairs: (图片1, 图片2, 相似度) 的列表
            
        Returns:
            重复组列表
        """
        if not similar_pairs:
            return []
        
        # 收集所有图片路径
        all_paths = set()
        for path1, path2, _ in similar_pairs:
            all_paths.add(path1)
            all_paths.add(path2)
        
        # 初始化并查集
        parent = {path: path for path in all_paths}
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # 合并相似图片
        for path1, path2, _ in similar_pairs:
            union(path1, path2)
        
        # 分组
        groups = defaultdict(list)
        for path in all_paths:
            root = find(path)
            groups[root].append(path)
        
        # 计算每组内部的相似度并格式化输出
        result = []
        for root, paths in groups.items():
            if len(paths) >= 2:
                # 计算每张图片与组内其他图片的平均相似度
                group_with_similarity = []
                for path in paths:
                    avg_similarity = self._compute_avg_similarity(path, paths, similar_pairs)
                    group_with_similarity.append((path, avg_similarity))
                
                # 按相似度排序
                group_with_similarity.sort(key=lambda x: x[1], reverse=True)
                result.append(group_with_similarity)
        
        # 按组大小排序（大的组在前）
        result.sort(key=lambda x: len(x), reverse=True)
        
        return result
    
    def _compute_avg_similarity(self, target_path: str, group_paths: List[str], 
                                similar_pairs: List[Tuple[str, str, float]]) -> float:
        """
        计算目标图片与组内其他图片的平均相似度
        
        Args:
            target_path: 目标图片路径
            group_paths: 组内所有图片路径
            similar_pairs: 相似对列表
            
        Returns:
            平均相似度
        """
        similarities = []
        
        for path1, path2, sim in similar_pairs:
            if path1 == target_path and path2 in group_paths:
                similarities.append(sim)
            elif path2 == target_path and path1 in group_paths:
                similarities.append(sim)
        
        if not similarities:
            return 1.0  # 自己与自己的相似度
        
        return sum(similarities) / len(similarities)
    
    def find_exact_duplicates(self, hashes: Dict[str, str]) -> List[List[str]]:
        """
        查找完全重复的图片（哈希值完全相同）
        
        Args:
            hashes: {图片路径: 哈希值} 的字典
            
        Returns:
            完全重复组列表
        """
        # 按哈希值分组
        hash_groups = defaultdict(list)
        for path, hash_value in hashes.items():
            hash_groups[hash_value].append(path)
        
        # 返回有重复的分组
        return [paths for paths in hash_groups.values() if len(paths) >= 2]
    
    def find_near_duplicates(self, hashes: Dict[str, str], 
                            threshold: float = 0.85) -> List[List[Tuple[str, float]]]:
        """
        查找近似重复的图片（相似度在一定范围内）
        
        Args:
            hashes: {图片路径: 哈希值} 的字典
            threshold: 相似度阈值
            
        Returns:
            近似重复组列表
        """
        original_threshold = self.threshold
        self.threshold = threshold
        result = self.find_duplicates(hashes)
        self.threshold = original_threshold
        return result
