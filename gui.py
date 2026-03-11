#!/usr/bin/env python3
"""
GUI 界面模块 - 使用 tkinter 提供图形界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
from pathlib import Path

from image_hasher import ImageHasher
from duplicate_finder import DuplicateFinder
from utils import get_image_files, format_size


class DedupGUI:
    """重复图片清理 GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 AI 智能清理重复照片")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        self.folder_path = tk.StringVar()
        self.threshold = tk.DoubleVar(value=0.9)
        self.is_scanning = False
        self.duplicate_groups = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        ttk.Label(
            title_frame, 
            text="🤖 AI 智能清理重复照片",
            font=("Helvetica", 20, "bold")
        ).pack()
        
        ttk.Label(
            title_frame,
            text="使用感知哈希算法自动检测并清理重复/相似图片",
            font=("Helvetica", 10)
        ).pack()
        
        # 配置区域
        config_frame = ttk.LabelFrame(self.root, text="配置", padding="10")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 文件夹选择
        folder_frame = ttk.Frame(config_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(folder_frame, text="📁 文件夹:").pack(side=tk.LEFT)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="浏览...", command=self._browse_folder).pack(side=tk.LEFT)
        
        # 阈值设置
        threshold_frame = ttk.Frame(config_frame)
        threshold_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(threshold_frame, text="🎯 相似度阈值:").pack(side=tk.LEFT)
        ttk.Scale(
            threshold_frame, 
            from_=0.5, to=1.0, 
            variable=self.threshold,
            orient=tk.HORIZONTAL,
            length=200
        ).pack(side=tk.LEFT, padx=5)
        ttk.Label(threshold_frame, textvariable=self.threshold).pack(side=tk.LEFT)
        
        # 操作按钮
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        self.scan_btn = ttk.Button(
            button_frame, 
            text="🔍 开始扫描",
            command=self._start_scan
        )
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(
            button_frame,
            text="🗑️ 删除选中",
            command=self._delete_selected,
            state=tk.DISABLED
        )
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(
            self.root, 
            orient=tk.HORIZONTAL, 
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(self.root, text="扫描结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建树形视图
        columns = ('group', 'filename', 'size', 'similarity', 'action')
        self.tree = ttk.Treeview(
            result_frame, 
            columns=columns,
            show='headings',
            selectmode='extended'
        )
        
        self.tree.heading('group', text='组')
        self.tree.heading('filename', text='文件名')
        self.tree.heading('size', text='大小')
        self.tree.heading('similarity', text='相似度')
        self.tree.heading('action', text='建议操作')
        
        self.tree.column('group', width=50)
        self.tree.column('filename', width=300)
        self.tree.column('size', width=80)
        self.tree.column('similarity', width=80)
        self.tree.column('action', width=80)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.root, text="日志", padding="5")
        log_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=6,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _browse_folder(self):
        """浏览文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
    
    def _log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def _start_scan(self):
        """开始扫描"""
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("错误", "请选择有效的文件夹")
            return
        
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.scan_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.tree.delete(*self.tree.get_children())
        
        # 在后台线程中扫描
        thread = threading.Thread(target=self._scan_thread, args=(folder,))
        thread.daemon = True
        thread.start()
    
    def _scan_thread(self, folder):
        """扫描线程"""
        try:
            self.root.after(0, lambda: self._log(f"🔍 开始扫描: {folder}"))
            
            # 获取图片文件
            image_files = get_image_files(folder)
            self.root.after(0, lambda: self._log(f"📸 找到 {len(image_files)} 张图片"))
            
            if len(image_files) < 2:
                self.root.after(0, lambda: self._log("❌ 图片数量不足"))
                return
            
            # 计算哈希
            self.root.after(0, lambda: self._log("🔐 计算图片哈希..."))
            hasher = ImageHasher()
            hashes = {}
            
            for i, img_path in enumerate(image_files):
                try:
                    hash_value = hasher.compute_hash(img_path)
                    if hash_value:
                        hashes[img_path] = hash_value
                    
                    # 更新进度
                    progress = (i + 1) / len(image_files) * 50
                    self.root.after(0, lambda p=progress: self.progress.config(value=p))
                except Exception as e:
                    self.root.after(0, lambda msg=str(e): self._log(f"⚠️  {msg}"))
            
            self.root.after(0, lambda: self._log(f"✅ 成功计算 {len(hashes)} 张图片的哈希"))
            
            # 查找重复
            self.root.after(0, lambda: self._log("🔍 查找重复图片..."))
            finder = DuplicateFinder(threshold=self.threshold.get())
            self.duplicate_groups = finder.find_duplicates(hashes)
            
            # 显示结果
            self.root.after(0, self._display_results)
            
        except Exception as e:
            self.root.after(0, lambda msg=str(e): self._log(f"❌ 错误: {msg}"))
        finally:
            self.is_scanning = False
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
    
    def _display_results(self):
        """显示扫描结果"""
        if not self.duplicate_groups:
            self._log("✨ 未发现重复图片！")
            messagebox.showinfo("完成", "未发现重复图片！")
            return
        
        self._log(f"⚠️  发现 {len(self.duplicate_groups)} 组重复图片")
        
        for group_idx, group in enumerate(self.duplicate_groups, 1):
            # 按文件大小排序
            sorted_group = sorted(group, key=lambda x: os.path.getsize(x[0]), reverse=True)
            
            for item_idx, (img_path, similarity) in enumerate(sorted_group):
                size = os.path.getsize(img_path)
                action = "保留" if item_idx == 0 else "删除"
                
                self.tree.insert('', tk.END, values=(
                    group_idx,
                    os.path.basename(img_path),
                    format_size(size),
                    f"{similarity:.1%}",
                    action
                ))
        
        self.delete_btn.config(state=tk.NORMAL)
        self.progress.config(value=100)
        
        messagebox.showinfo(
            "扫描完成", 
            f"发现 {len(self.duplicate_groups)} 组重复图片\n"
            f"共 {sum(len(g) for g in self.duplicate_groups)} 张图片"
        )
    
    def _delete_selected(self):
        """删除选中的文件"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的文件")
            return
        
        if not messagebox.askyesno("确认", "确定要删除选中的文件吗？"):
            return
        
        deleted = 0
        freed_space = 0
        
        for item in selected:
            values = self.tree.item(item, 'values')
            filename = values[1]
            
            # 查找完整路径
            for group in self.duplicate_groups:
                for img_path, _ in group:
                    if os.path.basename(img_path) == filename:
                        try:
                            size = os.path.getsize(img_path)
                            os.remove(img_path)
                            deleted += 1
                            freed_space += size
                            self._log(f"✅ 已删除: {filename}")
                            self.tree.delete(item)
                        except Exception as e:
                            self._log(f"❌ 删除失败 {filename}: {e}")
                        break
        
        messagebox.showinfo(
            "完成",
            f"删除 {deleted} 个文件\n释放空间: {format_size(freed_space)}"
        )


def main():
    """GUI 入口"""
    root = tk.Tk()
    app = DedupGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
