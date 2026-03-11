#!/usr/bin/env python3
"""
AI 智能清理重复照片 - 主程序
使用感知哈希算法检测并清理重复/相似图片
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
from tqdm import tqdm

from image_hasher import ImageHasher
from duplicate_finder import DuplicateFinder
from utils import format_size, get_image_files


def print_banner():
    """打印程序横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║           🤖 AI 智能清理重复照片 v1.0                      ║
    ║     使用感知哈希算法检测并清理重复/相似图片                 ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def scan_photos(folder_path: str, threshold: float = 0.9) -> Tuple[List, Dict]:
    """
    扫描文件夹中的重复图片
    
    Args:
        folder_path: 要扫描的文件夹路径
        threshold: 相似度阈值 (0-1)
    
    Returns:
        (重复组列表, 统计信息)
    """
    print(f"🔍 正在扫描文件夹: {folder_path}")
    
    # 获取所有图片文件
    image_files = get_image_files(folder_path)
    print(f"📸 找到 {len(image_files)} 张图片")
    
    if len(image_files) < 2:
        print("❌ 图片数量不足，无法检测重复")
        return [], {}
    
    # 计算图片哈希
    print("🔐 正在计算图片哈希...")
    hasher = ImageHasher()
    hashes = {}
    
    for img_path in tqdm(image_files, desc="处理进度"):
        try:
            hash_value = hasher.compute_hash(img_path)
            if hash_value:
                hashes[img_path] = hash_value
        except Exception as e:
            print(f"⚠️  处理失败 {img_path}: {e}")
    
    print(f"✅ 成功计算 {len(hashes)} 张图片的哈希")
    
    # 查找重复图片
    print("🔍 正在查找重复图片...")
    finder = DuplicateFinder(threshold=threshold)
    duplicate_groups = finder.find_duplicates(hashes)
    
    # 统计信息
    stats = {
        "total_images": len(image_files),
        "processed_images": len(hashes),
        "duplicate_groups": len(duplicate_groups),
        "duplicate_images": sum(len(group) for group in duplicate_groups),
    }
    
    return duplicate_groups, stats


def print_duplicate_report(duplicate_groups: List[List[Tuple[str, float]]], stats: Dict):
    """打印重复图片报告"""
    print("\n" + "="*60)
    print("📊 扫描报告")
    print("="*60)
    print(f"总图片数: {stats['total_images']}")
    print(f"成功处理: {stats['processed_images']}")
    print(f"重复组数: {stats['duplicate_groups']}")
    print(f"重复图片: {stats['duplicate_images']}")
    print("="*60)
    
    if not duplicate_groups:
        print("\n✨ 未发现重复图片！")
        return
    
    print(f"\n⚠️  发现 {len(duplicate_groups)} 组重复图片:\n")
    
    for i, group in enumerate(duplicate_groups, 1):
        print(f"重复组 #{i} ({len(group)} 张图片)")
        
        # 按文件大小排序，最大的（质量最好）排在前面
        sorted_group = sorted(group, key=lambda x: os.path.getsize(x[0]), reverse=True)
        
        for j, (img_path, similarity) in enumerate(sorted_group):
            size = os.path.getsize(img_path)
            size_str = format_size(size)
            marker = "📷 保留" if j == 0 else "📄 删除"
            print(f"  {marker} {os.path.basename(img_path)} ({size_str}) - 相似度: {similarity:.1%}")
        print()


def interactive_delete(duplicate_groups: List[List[Tuple[str, float]]]) -> int:
    """交互式删除重复图片"""
    if not duplicate_groups:
        return 0
    
    freed_space = 0
    deleted_count = 0
    
    print("\n🗑️  交互式删除模式\n")
    
    for i, group in enumerate(duplicate_groups, 1):
        # 按文件大小排序
        sorted_group = sorted(group, key=lambda x: os.path.getsize(x[0]), reverse=True)
        keep_file = sorted_group[0][0]
        
        print(f"\n重复组 #{i}/{len(duplicate_groups)}")
        print(f"📷 建议保留: {os.path.basename(keep_file)}")
        print("📄 待删除文件:")
        
        files_to_delete = []
        for img_path, similarity in sorted_group[1:]:
            size = os.path.getsize(img_path)
            print(f"   - {os.path.basename(img_path)} ({format_size(size)})")
            files_to_delete.append((img_path, size))
        
        choice = input(f"\n是否删除以上 {len(files_to_delete)} 个文件? (y/n/q): ").lower()
        
        if choice == 'q':
            print("👋 退出删除模式")
            break
        elif choice == 'y':
            for img_path, size in files_to_delete:
                try:
                    os.remove(img_path)
                    freed_space += size
                    deleted_count += 1
                    print(f"  ✅ 已删除: {os.path.basename(img_path)}")
                except Exception as e:
                    print(f"  ❌ 删除失败 {os.path.basename(img_path)}: {e}")
        else:
            print("  ⏭️  跳过此组")
    
    print(f"\n🎉 完成！删除 {deleted_count} 个文件，释放空间: {format_size(freed_space)}")
    return freed_space


def auto_delete(duplicate_groups: List[List[Tuple[str, float]]]) -> int:
    """自动删除重复图片（保留最大的文件）"""
    if not duplicate_groups:
        return 0
    
    freed_space = 0
    deleted_count = 0
    
    print("\n🤖 自动删除模式（保留质量最好的图片）\n")
    
    for group in duplicate_groups:
        # 按文件大小排序，保留最大的
        sorted_group = sorted(group, key=lambda x: os.path.getsize(x[0]), reverse=True)
        keep_file = sorted_group[0][0]
        
        for img_path, similarity in sorted_group[1:]:
            size = os.path.getsize(img_path)
            try:
                os.remove(img_path)
                freed_space += size
                deleted_count += 1
                print(f"✅ 已删除: {os.path.basename(img_path)} ({format_size(size)})")
            except Exception as e:
                print(f"❌ 删除失败 {os.path.basename(img_path)}: {e}")
    
    print(f"\n🎉 完成！删除 {deleted_count} 个文件，释放空间: {format_size(freed_space)}")
    return freed_space


def save_report(duplicate_groups: List, stats: Dict, output_path: str):
    """保存报告到 JSON 文件"""
    report = {
        "statistics": stats,
        "duplicate_groups": [
            [
                {"path": path, "similarity": similarity}
                for path, similarity in group
            ]
            for group in duplicate_groups
        ]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 报告已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='AI 智能清理重复照片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --scan ~/Pictures                    # 扫描图片文件夹
  %(prog)s --scan ~/Pictures --threshold 0.85   # 设置相似度阈值
  %(prog)s --scan ~/Pictures --interactive      # 交互式删除
  %(prog)s --scan ~/Pictures --auto-delete      # 自动删除重复
        """
    )
    
    parser.add_argument('--scan', required=True, help='要扫描的文件夹路径')
    parser.add_argument('--threshold', type=float, default=0.9, 
                       help='相似度阈值 (0-1)，默认 0.9')
    parser.add_argument('--auto-delete', action='store_true',
                       help='自动删除重复图片（保留质量最高的）')
    parser.add_argument('--interactive', action='store_true',
                       help='交互式确认删除')
    parser.add_argument('--output', default='duplicates_report.json',
                       help='重复图片报告输出路径')
    
    args = parser.parse_args()
    
    print_banner()
    
    # 验证文件夹
    if not os.path.isdir(args.scan):
        print(f"❌ 错误: 文件夹不存在 {args.scan}")
        sys.exit(1)
    
    # 验证阈值
    if not 0 <= args.threshold <= 1:
        print("❌ 错误: 阈值必须在 0-1 之间")
        sys.exit(1)
    
    # 扫描重复图片
    duplicate_groups, stats = scan_photos(args.scan, args.threshold)
    
    # 打印报告
    print_duplicate_report(duplicate_groups, stats)
    
    # 保存报告
    save_report(duplicate_groups, stats, args.output)
    
    # 删除重复图片
    if duplicate_groups:
        if args.interactive:
            interactive_delete(duplicate_groups)
        elif args.auto_delete:
            confirm = input(f"\n⚠️  即将自动删除 {stats['duplicate_images'] - len(duplicate_groups)} 个文件，确定吗? (y/n): ")
            if confirm.lower() == 'y':
                auto_delete(duplicate_groups)
            else:
                print("❌ 已取消删除操作")
        else:
            print("\n💡 提示: 使用 --interactive 进行交互式删除，或 --auto-delete 自动删除")


if __name__ == '__main__':
    main()
