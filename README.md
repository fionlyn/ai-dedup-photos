# AI 智能清理重复照片

## 项目简介

一个基于 Python 的智能工具，使用感知哈希（Perceptual Hash）和相似度算法自动检测并清理重复或相似的图片。

## 核心特性

- 🔍 **智能检测**：使用感知哈希（pHash）+ 小波哈希（wHash）+ 差异哈希（dHash）多算法融合
- 🎯 **模糊匹配**：支持不同分辨率、格式、轻微编辑的重复图片检测
- 📊 **相似度评分**：精确计算图片相似度百分比
- 🗂️ **批量处理**：支持文件夹递归扫描
- 🛡️ **安全预览**：先预览再删除，避免误删
- 📈 **进度显示**：实时显示处理进度条
- 🎨 **交互式操作**：支持交互式确认删除

## 算法原理

1. **感知哈希 (Perceptual Hash)**：计算图片的 pHash 值，对图片的轻微变化鲁棒
2. **汉明距离 (Hamming Distance)**：比较两个哈希值的差异
3. **相似度计算**：将汉明距离转换为相似度百分比
4. **并查集分组**：使用并查集算法将相似图片分组

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/fionlyn/ai-dedup-photos.git
cd ai-dedup-photos

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 使用方法

```bash
# 扫描文件夹中的重复图片
python dedup_photos.py --scan /path/to/photos

# 设置相似度阈值（默认 0.9）
python dedup_photos.py --scan /path/to/photos --threshold 0.85

# 交互式删除（推荐）
python dedup_photos.py --scan /path/to/photos --interactive

# 自动删除重复图片（保留质量最高的）
python dedup_photos.py --scan /path/to/photos --auto-delete

# 启动 GUI 界面
python gui.py
```

## 项目结构

```
ai-dedup-photos/
├── dedup_photos.py      # 主程序入口
├── image_hasher.py      # 图像哈希算法实现
├── duplicate_finder.py  # 重复检测与分组逻辑
├── utils.py             # 工具函数
├── requirements.txt     # Python 依赖
├── README.md            # 项目说明
└── tests/               # 测试用例
    └── test_dedup.py
```

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- WebP (.webp)
- HEIC/HEIF (.heic, .heif)
- RAW 格式 (.raw, .cr2, .nef, .arw)

## 示例输出

```
╔═══════════════════════════════════════════════════════════╗
║           🤖 AI 智能清理重复照片 v1.0                      ║
║     使用感知哈希算法检测并清理重复/相似图片                 ║
╚═══════════════════════════════════════════════════════════╝

🔍 正在扫描文件夹: /Users/photos
📸 找到 1,234 张图片
🔐 正在计算图片哈希...
处理进度: 100%|████████████████| 1234/1234 [00:15<00:00, 80.12it/s]
✅ 成功计算 1,230 张图片的哈希
🔍 正在查找重复图片...
比较 1230 张图片的相似度...

============================================================
📊 扫描报告
============================================================
总图片数: 1234
成功处理: 1230
重复组数: 23
重复图片: 56
============================================================

⚠️  发现 23 组重复图片:

重复组 #1 (3 张图片)
  📷 保留 IMG_001.jpg (2.3 MB) - 相似度: 98.5%
  📄 删除 IMG_001_copy.jpg (2.3 MB) - 相似度: 97.2%
  📄 删除 IMG_001_edit.jpg (1.8 MB) - 相似度: 95.1%

🎉 完成！可释放空间: 125.6 MB
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--scan` | 要扫描的文件夹路径 | 必填 |
| `--threshold` | 相似度阈值 (0-1) | 0.9 |
| `--auto-delete` | 自动删除重复图片 | False |
| `--interactive` | 交互式确认删除 | False |
| `--output` | 重复图片报告输出路径 | duplicates_report.json |

## 运行测试

```bash
python -m pytest tests/
# 或
python tests/test_dedup.py
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
