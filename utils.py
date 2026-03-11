#!/usr/bin/env python3
"""
工具函数模块
"""

import os
from pathlib import Path
from typing import List


# 支持的图片格式
SUPPORTED_FORMATS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
    '.webp', '.heic', '.heif', '.raw', '.cr2', '.nef', '.arw'
}


def get_image_files(folder_path: str) -> List[str]:
    """
    获取文件夹中的所有图片文件
    
    Args:
        folder_path: 文件夹路径
        
    Returns:
        图片文件路径列表
    """
    image_files = []
    folder = Path(folder_path)
    
    for ext in SUPPORTED_FORMATS:
        # 不区分大小写匹配
        image_files.extend(folder.rglob(f'*{ext}'))
        image_files.extend(folder.rglob(f'*{ext.upper()}'))
    
    # 转换为字符串并去重
    return list(set(str(f) for f in image_files))


def format_size(size_bytes: int) -> str:
    """
    将字节大小格式化为人类可读格式
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化后的字符串 (如: 1.5 MB)
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def get_file_info(file_path: str) -> dict:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件信息字典
    """
    try:
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'size_formatted': format_size(stat.st_size),
            'modified_time': stat.st_mtime,
        }
    except Exception as e:
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'error': str(e)
        }


def ensure_dir(dir_path: str) -> bool:
    """
    确保目录存在，不存在则创建
    
    Args:
        dir_path: 目录路径
        
    Returns:
        是否成功
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败 {dir_path}: {e}")
        return False


def is_image_file(file_path: str) -> bool:
    """
    检查文件是否为图片
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否为图片文件
    """
    ext = Path(file_path).suffix.lower()
    return ext in SUPPORTED_FORMATS


def get_folder_size(folder_path: str) -> int:
    """
    计算文件夹总大小
    
    Args:
        folder_path: 文件夹路径
        
    Returns:
        总字节数
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except:
                pass
    return total_size
