# 圆柱全景拼接 - 项目规格文档

**截止日期:** 2025-11-15
**更新日期:** 2025-11-15

---

## 项目目标

实现完整的圆柱全景图像拼接系统，包含PDF要求的8个步骤。

---

## Pipeline流程

### 1. 图像采集
- 从指定目录读取图像序列
- 提取EXIF元数据(焦距、图像尺寸等)
- 按文件名排序

### 2. 圆柱投影变换

**核心公式 (PDF第2页):**
```
给定焦距 f 和图像中心 (xc, yc):

θ = (x_cyl - xc) / f
h = (y_cyl - yc) / f

x̂ = sin(θ)
ŷ = h
ẑ = cos(θ)

x = f * x̂/ẑ + xc
y = f * ŷ/ẑ + yc
```

**实现要点:**
- 使用反向变换(backward warping)避免空洞
- 双线性插值处理子像素坐标
- 焦距优先级: CLI参数 > EXIF数据 > .env默认值

### 3. SIFT特征提取
- 对投影后的图像提取SIFT特征
- 返回关键点和描述符
- 可视化保存(可选)

### 4. RANSAC特征匹配
- 使用FLANN/BFMatcher匹配相邻图像对
- Lowe's ratio test过滤匹配
- RANSAC估计平移变换(dx, dy)
- 记录内点/外点统计

### 5. 生成平移列表
**JSON格式:**
```json
{
  "metadata": {
    "timestamp": "2025-11-15T10:30:00",
    "focal_length": 468.0,
    "num_images": 18
  },
  "translations": [
    {
      "pair": [0, 1],
      "translation": {"dx": 234.5, "dy": -2.3},
      "inliers": 156,
      "total_matches": 203
    }
  ]
}
```

### 6. 漂移校正 (PDF第6步)

**适用场景:** 360度全景拼接

**算法步骤:**
1. 匹配第一张和最后一张图像
2. 计算间隙角度 θ_g
3. 均匀分配校正: 每对修正 θ_g / N_images
4. 更新焦距: **f' = f × (1 - θ_g / 2π)**

**配置:** `ENABLE_DRIFT_CORRECTION=true`

### 7. 图像融合
- 创建全景画布(根据累积平移计算尺寸)
- 放置投影后的图像
- 重叠区域使用简单平均融合

### 8. 裁剪输出
- 检测黑边
- 计算最大有效区域
- 裁剪并保存最终结果

---

## 技术栈

- **Python:** 3.13
- **包管理:** uv
- **格式化:** ruff
- **核心库:** OpenCV, NumPy, Matplotlib, Pillow, python-dotenv

**项目结构:**
- 启动入口: `./main.py`
- 源代码包: `./src/` (通过 `uv pip install -e .` 安装)

---

## 配置系统

### 参数优先级
```
CLI参数 > .env配置 > 程序默认值
```

### 关键配置项

**.env 示例:**
```bash
# 输入输出
IMAGE_PATH=./data/pano
OUTPUT_PATH=./output

# 焦距
DEFAULT_FOCAL_LENGTH=500
FOCAL_LENGTH_SOURCE=exif  # exif | config | auto

# Pipeline
SAVE_INTERMEDIATE=true

# SIFT
SIFT_N_FEATURES=0
SIFT_CONTRAST_THRESHOLD=0.04

# 匹配
MATCH_RATIO_THRESHOLD=0.7

# RANSAC
RANSAC_THRESHOLD=5.0
RANSAC_MAX_ITERS=2000

# 漂移校正
ENABLE_DRIFT_CORRECTION=true

# 融合
BLEND_METHOD=average  # average | linear | multiband

# 输出
OUTPUT_FORMAT=jpg
OUTPUT_QUALITY=95
```

### CLI接口
```bash
# 基本用法
python main.py

# 常用选项
python main.py --input data/pano1
python main.py --focal-length 468
python main.py --no-drift-correction
python main.py --output output/my_test/
```

---

## 输出结构

```
output/{timestamp}/
├── metadata.json           # 运行元数据
├── warped/                 # 步骤2: 投影后图像
│   ├── img_0001_warped.jpg
│   └── ...
├── features/               # 步骤3: 特征可视化
│   ├── img_0001_features.jpg
│   └── ...
├── matches/                # 步骤4: 匹配可视化
│   ├── match_0001_0002.jpg
│   └── ...
├── translations.json       # 步骤5: 平移列表
├── drift_correction.json   # 步骤6: 漂移校正参数
├── blended.jpg             # 步骤7: 融合结果
├── final.jpg               # 步骤8: 最终输出
├── pipeline.log            # 运行日志
└── report.json             # 处理统计
```

---

## 代码结构

```
src/
├── __init__.py
├── config.py              # 配置加载(CLI + .env)
├── utils/
│   ├── image_io.py        # 图像读写
│   └── visualization.py   # 可视化工具
├── warping/
│   └── cylindrical.py     # 圆柱投影
├── features/
│   └── sift.py            # SIFT特征提取
├── alignment/
│   ├── matcher.py         # 特征匹配
│   └── ransac.py          # RANSAC对齐
├── stitching/
│   ├── drift.py           # 漂移校正
│   ├── blending.py        # 图像融合
│   └── crop.py            # 裁剪
└── pipeline.py            # 主流程编排
```

---

## 数据集

### 目录组织
```
data/
├── official/              # 官方数据集
└── sample_panorama/
    ├── set1_building/     # 建筑全景 (~180°)
    ├── set2_landscape/    # 风景全景 (~270°)
    └── set3_360degree/    # 360°全景(测试漂移校正)
```

### 图像要求
- 相邻图像30%-50%重叠
- 包含EXIF焦距信息
- 按拍摄顺序命名
- 格式: JPEG/PNG

---

## 关键设计决策

| # | 决策项 | 选择方案 |
|---|--------|----------|
| 1 | 焦距获取 | EXIF优先,支持CLI覆盖 |
| 2 | 运行模式 | 全自动,保存所有中间结果 |
| 3 | 结果隔离 | 时间戳目录 |
| 4 | 平移格式 | JSON |
| 5 | 融合方法 | 简单平均 |
| 6 | 漂移校正 | 完整实现,可配置 |
| 7 | 配置管理 | CLI + .env |
| 8 | 交互查看器 | 不实现 |

---

## 质量保证

### 日志
- 使用Python `logging`模块
- 同时输出到文件和控制台
- 保存到 `output/{timestamp}/pipeline.log`

### 错误处理
- EXIF缺失 → 使用默认值并警告
- 匹配失败 → 记录日志,跳过该对
- 文件不存在 → 友好提示
- 内存不足 → 降采样(可选)

### 进度显示
- 使用 `tqdm` 显示进度条(可选)
- 关键步骤输出状态信息

---

## 参考

- **项目PDF:** `Proj2-Cylindrical Panoroma.pdf`
- **官方数据集:** http://staff.ustc.edu.cn/~xjchen99/teaching/Project2.htm
- **OpenCV SIFT:** https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html
