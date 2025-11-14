# 圆柱全景拼接系统 (Cylindrical Panorama Stitching)

**课程项目:** 图像理解 Project 2
**截止日期:** 2025-11-15

## 项目简介

本项目实现了基于SIFT特征和RANSAC对齐的圆柱全景图像拼接系统，包含完整的8步处理流程。

## 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 配置参数（可选，编辑 .env 文件）
# 查看 .env 了解所有可配置参数

# 3. 运行拼接（使用默认配置）
python main.py

# 4. 指定输入目录
python main.py --input data/sample_panorama/set1_building/

# 5. 查看结果
# 结果保存在 output/{timestamp}/ 目录下
```

## 核心功能

### 完整的8步Pipeline

1. **图像采集** - 支持从目录读取图像序列
2. **圆柱投影** - 使用EXIF焦距或配置参数进行投影变换
3. **特征提取** - SIFT特征检测
4. **特征匹配** - RANSAC鲁棒对齐
5. **平移列表** - JSON格式保存变换参数
6. **漂移校正** - 360度全景的端到端校正
7. **图像融合** - 简单平均融合
8. **裁剪输出** - 自动裁剪黑边

### 关键特性

- ✅ **EXIF焦距读取** - 自动从图像元数据提取焦距
- ✅ **混合运行模式** - 全自动运行，保存所有中间结果
- ✅ **时间戳隔离** - 每次运行使用独立的时间戳目录
- ✅ **JSON格式** - 结构化保存变换参数
- ✅ **简单平均融合** - 快速高效的图像融合
- ✅ **漂移校正** - 完整支持360度全景
- ✅ **CLI + .env配置** - 灵活的参数配置方式
- ✅ **完整中间输出** - 保存所有处理步骤结果

## 项目结构

```
ImageUnderstanding-HW2/
├── .env                      # 配置文件
├── main.py                   # 主入口
├── src/                      # 源代码（待实现）
├── data/                     # 数据集
│   ├── official/             # 官方数据
│   ├── sample_panorama/      # 示例数据集
│   │   ├── set1_building/    # 建筑物全景
│   │   ├── set2_landscape/   # 风景全景
│   │   └── set3_360degree/   # 360度全景
│   └── custom/               # 自定义数据
├── output/                   # 输出结果（按时间戳组织）
│   └── {timestamp}/
│       ├── warped/           # 投影后图像
│       ├── features/         # 特征可视化
│       ├── matches/          # 匹配可视化
│       ├── translations.json # 变换参数
│       ├── blended.jpg       # 融合结果
│       └── final.jpg         # 最终输出
├── doc/                      # 文档
│   ├── design_specification.md  # 设计规格（详细）
│   ├── development_plan.md      # 开发计划
│   └── todo.md                  # 任务清单
└── scripts/                  # 工具脚本
    └── download_sample_data.sh
```

## 配置说明

### 命令行参数

```bash
# 基本用法
python main.py [OPTIONS]

# 常用参数
--input PATH              # 输入图像目录
--output PATH             # 输出目录
--focal-length FLOAT      # 焦距（覆盖EXIF和默认值）
--enable-drift-correction # 启用漂移校正
--no-drift-correction     # 禁用漂移校正
--blend-method METHOD     # 融合方法: average/linear/multiband
--steps STEPS             # 执行步骤: all 或 warp,features,match,...
```

### .env 配置文件

所有参数都可以在 `.env` 文件中配置。主要参数：

```bash
# 图像路径
IMAGE_PATH=./data/official
OUTPUT_PATH=./output

# 焦距配置
DEFAULT_FOCAL_LENGTH=500
FOCAL_LENGTH_SOURCE=exif  # exif/config/auto

# Pipeline配置
PIPELINE_MODE=hybrid
SAVE_INTERMEDIATE=true

# 漂移校正
ENABLE_DRIFT_CORRECTION=true

# 融合方法
BLEND_METHOD=average

# 更多参数见 .env 文件
```

**参数优先级:** `命令行参数 > .env配置 > 程序默认值`

## 设计文档

所有设计决策已确认并文档化：

| # | 决策项 | 选择 | 文档 |
|---|--------|------|------|
| 1 | 焦距处理 | 从EXIF读取（支持手动覆盖） | ✅ |
| 2 | Pipeline模式 | 混合模式（自动+完整输出） | ✅ |
| 3 | 中间结果 | 全部保存，时间戳隔离 | ✅ |
| 4 | 数据集 | 准备多个测试数据集 | ✅ |
| 5 | Translation格式 | JSON | ✅ |
| 6 | 融合方法 | 简单平均 | ✅ |
| 7 | 漂移校正 | 完整支持（可配置） | ✅ |
| 8 | 配置管理 | CLI + .env | ✅ |
| 9 | 交互式查看器 | 不实现 | ✅ |
| 10 | 错误处理 | 继续运行+警告 | ✅ |

**详细设计规格:** 请参考 [`doc/design_specification.md`](doc/design_specification.md)

## 数据集准备

### 官方数据集

下载地址: http://staff.ustc.edu.cn/~xjchen99/teaching/Project2.htm

### 示例数据集

项目提供了三类测试场景的目录结构：

1. **set1_building** - 建筑物全景（~180度）
2. **set2_landscape** - 风景全景（~270度）
3. **set3_360degree** - 360度环绕（测试漂移校正）

使用脚本准备数据集：
```bash
bash scripts/download_sample_data.sh
```

或手动下载图像到对应目录。详见 [`data/sample_panorama/README.md`](data/sample_panorama/README.md)

## 开发进度

- [x] 项目规划和设计
- [x] 配置系统设计
- [x] 数据集目录准备
- [x] 设计文档完成
- [ ] 源代码实现
- [ ] 测试和调优
- [ ] 最终报告

详细任务清单见 [`doc/todo.md`](doc/todo.md)

## 技术栈

- **Python:** 3.13
- **包管理:** uv
- **核心库:**
  - OpenCV (cv2) - 图像处理、SIFT、RANSAC
  - NumPy - 数值计算
  - Matplotlib - 可视化
  - Pillow - EXIF读取
  - python-dotenv - 配置管理

## 文档索引

- **设计规格:** [`doc/design_specification.md`](doc/design_specification.md) - 完整的设计决策和技术规格
- **开发计划:** [`doc/development_plan.md`](doc/development_plan.md) - 项目结构和开发阶段
- **任务清单:** [`doc/todo.md`](doc/todo.md) - 详细的开发任务列表
- **数据集说明:** [`data/sample_panorama/README.md`](data/sample_panorama/README.md) - 数据集准备指南

## 许可证

本项目为课程作业项目。

## 参考资料

- 项目PDF: `Proj2-Cylindrical Panoroma.pdf`
- 官方数据集: http://staff.ustc.edu.cn/~xjchen99/teaching/Project2.htm
