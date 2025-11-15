# 圆柱全景拼接 - 设计规格文档

**项目名称:** Cylindrical Panorama Stitching
**更新日期:** 2025-11-14
**截止日期:** 2025-11-15

---

## 设计决策总览

本文档记录了项目的所有关键设计决策和技术规格。

---

## 1. 焦距处理策略

### 决策：从EXIF数据读取焦距

**实现要求:**
- 使用Python PIL/Pillow或OpenCV读取图像EXIF信息
- 提取焦距参数 (FocalLength, FocalLengthIn35mmFilm)
- 如果EXIF数据缺失，使用`.env`配置的默认焦距值
- 支持手动覆盖（通过配置文件或命令行参数）

**技术细节:**
```python
# 优先级顺序：
# 1. 命令行参数指定的焦距（如果有）
# 2. EXIF数据中的焦距
# 3. .env文件中的默认焦距
```

**相关配置:**
- `.env` 中添加 `DEFAULT_FOCAL_LENGTH` 参数
- 支持 `FOCAL_LENGTH_OVERRIDE` 强制使用指定焦距

---

## 2. Pipeline运行模式

### 决策：混合模式（Hybrid Mode）

**功能描述:**
- 默认全自动运行完整pipeline（8个步骤）
- 支持通过配置选择性跳过某些步骤
- 保存所有中间结果，便于调试和分析

**执行流程:**
1. 图像预处理（读取+EXIF解析）
2. 圆柱投影变换（Cylindrical Warping）
3. SIFT特征提取
4. 特征匹配 + RANSAC对齐
5. 生成平移列表（Translation List）
6. 漂移校正（Drift Correction）
7. 图像融合（Blending）
8. 裁剪输出（Cropping）

**配置参数:**
```bash
# .env 示例
PIPELINE_MODE=hybrid          # auto / manual / hybrid
ENABLE_DRIFT_CORRECTION=true  # 是否启用漂移校正
SAVE_INTERMEDIATE=true        # 是否保存中间结果
```

---

## 3. 中间结果保存策略

### 决策：全部分步保存，使用时间戳隔离批次

**目录结构:**
```
output/
├── 20251114_143025/          # 执行时间戳目录
│   ├── warped/               # 步骤2: 投影后的图像
│   │   ├── img_0001_warped.jpg
│   │   ├── img_0002_warped.jpg
│   │   └── ...
│   ├── features/             # 步骤3: 特征可视化
│   │   ├── img_0001_features.jpg
│   │   └── ...
│   ├── matches/              # 步骤4: 匹配可视化
│   │   ├── match_0001_0002.jpg
│   │   └── ...
│   ├── translations.json     # 步骤5: 平移列表
│   ├── drift_correction.json # 步骤6: 漂移校正参数
│   ├── blended.jpg           # 步骤7: 融合结果
│   └── final.jpg             # 步骤8: 最终裁剪结果
└── latest -> 20251114_143025/  # 软链接指向最新结果
```

**保存内容清单:**
- ✅ 投影变换后的图像（warped images）
- ✅ 特征点可视化（feature visualizations）
- ✅ 特征匹配可视化（match visualizations）
- ✅ 平移参数列表（translation list - JSON格式）
- ✅ 漂移校正参数（drift correction parameters）
- ✅ 融合后的全景图（blended panorama）
- ✅ 最终裁剪结果（final cropped output）

**时间戳格式:**
```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"output/{timestamp}/"
```

---

## 4. 图像数据集准备

### 决策：在data目录下准备多个测试数据集

**数据集组织结构:**
```
data/
├── official/                 # 官方数据集（已存在）
├── sample_panorama/          # 新增：示例全景数据集
│   ├── set1_building/        # 建筑物全景
│   │   ├── IMG_0001.jpg
│   │   ├── IMG_0002.jpg
│   │   └── ...
│   ├── set2_landscape/       # 风景全景
│   └── set3_360degree/       # 360度全景（用于测试漂移校正）
└── custom/                   # 用户自定义数据集
```

**数据集要求:**
1. **图像序列要求:**
   - 相邻图像需有30%-50%重叠区域
   - 按拍摄顺序命名（支持自动排序）
   - 同一序列使用相同相机参数

2. **文件格式:**
   - 支持 JPEG, PNG
   - 包含完整EXIF信息（焦距、拍摄参数）

3. **推荐场景:**
   - 建筑物全景（测试基本拼接）
   - 风景全景（测试大范围拼接）
   - 360度环绕（测试漂移校正）

**数据来源:**
- 官方数据集: `staff.ustc.edu.cn/~xjchen99/teaching/Project2.htm`
- 自动下载或手动准备示例数据集

---

## 5. 平移列表格式

### 决策：使用JSON格式保存

**JSON结构设计:**
```json
{
  "metadata": {
    "timestamp": "2025-11-14T14:30:25",
    "focal_length": 468.0,
    "focal_length_source": "exif",
    "num_images": 18,
    "drift_corrected": true
  },
  "translations": [
    {
      "pair": [0, 1],
      "image_pair": ["IMG_0001.jpg", "IMG_0002.jpg"],
      "translation": {
        "dx": 234.5,
        "dy": -2.3
      },
      "inliers": 156,
      "total_matches": 203,
      "inlier_ratio": 0.769
    },
    {
      "pair": [1, 2],
      "image_pair": ["IMG_0002.jpg", "IMG_0003.jpg"],
      "translation": {
        "dx": 241.8,
        "dy": 1.7
      },
      "inliers": 178,
      "total_matches": 215,
      "inlier_ratio": 0.828
    }
  ],
  "drift_correction": {
    "gap_angle": 0.0523,
    "corrected_focal_length": 468.0,
    "original_focal_length": 510.0
  }
}
```

**文件保存位置:**
- `output/{timestamp}/translations.json`
- 可被后续步骤重新加载使用

---

## 6. 图像融合方法

### 决策：简单平均法（Simple Averaging）

**算法描述:**
- 对重叠区域的像素值进行简单算术平均
- 不使用复杂的多频段融合（Multi-band Blending）

**实现伪代码:**
```python
def simple_average_blend(canvas, image, offset):
    """
    简单平均融合

    对于重叠区域:
    canvas[y, x] = (canvas[y, x] + image[y', x']) / 2

    对于非重叠区域:
    直接复制像素值
    """
    for y, x in overlapping_region:
        if canvas[y, x] != 0:  # 已有像素
            canvas[y, x] = (canvas[y, x] + image[y', x']) / 2
        else:  # 空白区域
            canvas[y, x] = image[y', x']
```

**优点:**
- 实现简单
- 计算速度快
- 适合光照一致的图像序列

**缺点:**
- 可能出现明显接缝（如果光照差异大）
- 不处理曝光差异

**备选方案（可选实现）:**
- Linear/Feather Blending（线性融合）
- 如果效果不佳，可后期升级

---

## 7. 漂移校正（Drift Correction）

### 决策：完全支持，按PDF要求实现

**适用场景:**
- **必须启用:** 360度全景拼接
- **可选启用:** 部分全景（非360度）

**算法步骤（按PDF第6步）:**

1. **匹配首尾图像**
   - 对第一张和最后一张图像进行特征匹配
   - 使用RANSAC估计平移差异

2. **计算间隙角度 θ_g**
   ```
   θ_g = 计算的水平位移差异对应的角度
   ```

3. **均匀分配校正**
   - 将θ_g平均分配到所有图像对
   - 每对修正角度: θ_correction = θ_g / N_images

4. **更新焦距**
   ```
   f' = f * (1 - θ_g / (2π))
   ```

**配置参数:**
```bash
# .env
ENABLE_DRIFT_CORRECTION=true
DRIFT_CORRECTION_AUTO_DETECT=true  # 自动检测是否需要校正
MIN_ANGLE_FOR_CORRECTION=5.5       # 最小需要校正的角度（弧度）
```

**保存信息:**
- 原始焦距 f
- 间隙角度 θ_g
- 校正后焦距 f'
- 每对的修正量

---

## 8. 命令行参数与配置管理

### 决策：支持命令行参数，无参数时从.env读取

**参数优先级:**
```
命令行参数 > .env 配置 > 程序默认值
```

**命令行接口设计:**
```bash
# 基本用法（全自动，使用.env配置）
python main.py

# 指定输入目录
python main.py --input data/sample_panorama/set1_building/

# 指定焦距
python main.py --focal-length 500

# 禁用漂移校正
python main.py --no-drift-correction

# 仅运行特定步骤
python main.py --steps warp,features,match

# 指定输出目录
python main.py --output output/my_test/

# 完整示例
python main.py \
  --input data/sample_panorama/set3_360degree/ \
  --focal-length 468 \
  --enable-drift-correction \
  --output output/test_360/
```

**主要参数列表:**
| 参数 | .env变量 | 默认值 | 说明 |
|------|----------|--------|------|
| `--input` | `IMAGE_PATH` | `./data/official` | 输入图像目录 |
| `--output` | `OUTPUT_PATH` | `./output/{timestamp}` | 输出目录 |
| `--focal-length` | `DEFAULT_FOCAL_LENGTH` | 从EXIF读取 | 焦距值 |
| `--enable-drift-correction` | `ENABLE_DRIFT_CORRECTION` | `true` | 启用漂移校正 |
| `--blend-method` | `BLEND_METHOD` | `average` | 融合方法 |
| `--save-intermediate` | `SAVE_INTERMEDIATE` | `true` | 保存中间结果 |
| `--steps` | `PIPELINE_STEPS` | `all` | 执行步骤 |

**.env 配置文件示例:**
```bash
# Image data configuration
IMAGE_PATH=./data/official
OUTPUT_PATH=./output

# Focal length configuration
DEFAULT_FOCAL_LENGTH=500
FOCAL_LENGTH_OVERRIDE=
FOCAL_LENGTH_SOURCE=exif  # exif / config / auto

# Pipeline configuration
PIPELINE_MODE=hybrid
PIPELINE_STEPS=all  # all / warp,features,match,blend / ...
SAVE_INTERMEDIATE=true

# Cylindrical warping
# (焦距从EXIF读取或使用DEFAULT_FOCAL_LENGTH)

# Feature extraction (SIFT)
SIFT_N_FEATURES=0           # 0 = 自动
SIFT_CONTRAST_THRESHOLD=0.04
SIFT_EDGE_THRESHOLD=10

# Feature matching
MATCH_RATIO_THRESHOLD=0.7   # Lowe's ratio test

# RANSAC alignment
RANSAC_THRESHOLD=5.0        # 像素
RANSAC_MAX_ITERS=2000
RANSAC_CONFIDENCE=0.995

# Translation list
TRANSLATION_FORMAT=json     # json / csv / pickle

# Drift correction
ENABLE_DRIFT_CORRECTION=true
DRIFT_CORRECTION_AUTO_DETECT=true
MIN_ANGLE_FOR_CORRECTION=0.1  # 弧度

# Blending
BLEND_METHOD=average        # average / linear / multiband

# Cropping
AUTO_CROP=true
CROP_THRESHOLD=10           # 黑色像素阈值

# Output
OUTPUT_FORMAT=jpg           # jpg / png
OUTPUT_QUALITY=95           # JPEG质量 (1-100)
```

**实现方式:**
```python
# config.py
import os
from dotenv import load_dotenv
import argparse

def load_config():
    # 1. 加载 .env 文件
    load_dotenv()

    # 2. 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default=os.getenv('IMAGE_PATH'))
    parser.add_argument('--focal-length', type=float,
                       default=os.getenv('DEFAULT_FOCAL_LENGTH'))
    # ... 其他参数

    args = parser.parse_args()

    # 3. 合并配置（命令行优先）
    config = merge_config(env_config, args)

    return config
```

---

## 9. 交互式查看器（Interactive Viewer）

### 决策：不刻意实现

**说明:**
- 不作为核心功能开发
- 重点放在图像拼接质量和中间结果保存
- 最终输出高质量静态图像即可

**可选替代方案:**
- 使用标准图像查看器打开结果
- 提供简单的matplotlib可视化脚本
- 如果时间充裕，可考虑添加基础的图像浏览功能

**不实现的功能:**
- ❌ 360度全景交互式浏览器
- ❌ Web界面
- ❌ 实时拼接预览

**保留的功能:**
- ✅ 保存高质量最终全景图
- ✅ 提供中间结果可视化（图像文件形式）
- ✅ 使用matplotlib显示结果（可选）

---

## 10. 中间输出完整性

### 决策：全部保存

**完整的中间输出列表:**

### 步骤1: 图像加载
```
output/{timestamp}/metadata.json
  - 图像列表
  - EXIF信息
  - 焦距信息
```

### 步骤2: 圆柱投影
```
output/{timestamp}/warped/
  ├── img_0001_warped.jpg
  ├── img_0002_warped.jpg
  └── ...
```

### 步骤3: 特征提取
```
output/{timestamp}/features/
  ├── img_0001_features.jpg     # 特征点可视化
  ├── img_0001_features.npz     # 特征描述符（可选）
  └── ...
```

### 步骤4: 特征匹配
```
output/{timestamp}/matches/
  ├── match_0001_0002.jpg       # 匹配可视化
  ├── match_0002_0003.jpg
  └── ...
```

### 步骤5: 平移列表
```
output/{timestamp}/translations.json
```

### 步骤6: 漂移校正
```
output/{timestamp}/drift_correction.json
output/{timestamp}/drift_visualization.jpg  # 首尾匹配可视化
```

### 步骤7: 图像融合
```
output/{timestamp}/blended.jpg
output/{timestamp}/blend_overlay.jpg  # 重叠区域可视化（可选）
```

### 步骤8: 裁剪输出
```
output/{timestamp}/final.jpg
output/{timestamp}/final_uncropped.jpg  # 裁剪前对比
```

### 汇总报告
```
output/{timestamp}/report.json
  - 处理时间统计
  - 每步骤参数
  - 质量指标（匹配数、内点率等）
```

**磁盘空间考虑:**
- 提供配置选项控制保存内容详细程度
- 特征描述符等大文件可选保存
- 可视化图像可配置分辨率

---

## 技术栈确认

### 核心依赖
- **Python:** 3.13
- **包管理:** uv
- **图像处理:** OpenCV (cv2)
- **数值计算:** NumPy
- **可视化:** Matplotlib
- **配置管理:** python-dotenv
- **EXIF读取:** PIL/Pillow
- **命令行解析:** argparse

### 文件操作
- **JSON:** 标准库 `json`
- **时间处理:** 标准库 `datetime`
- **路径处理:** 标准库 `pathlib`

---

## 质量保证

### 日志记录
```python
# 使用Python logging模块
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'output/{timestamp}/pipeline.log'),
        logging.StreamHandler()
    ]
)
```

### 错误处理
- 文件不存在：友好提示
- EXIF缺失：使用默认值并警告
- 匹配失败：记录并跳过该对
- 内存不足：降采样处理

### 性能优化
- 图像缓存策略
- 并行特征提取（可选）
- 进度条显示（tqdm）

---

## 项目检查清单

### 功能实现
- [x] ✅ 决策1: EXIF焦距读取
- [x] ✅ 决策2: 混合运行模式
- [x] ✅ 决策3: 时间戳隔离的中间结果保存
- [ ] ⏳ 决策4: 准备示例数据集
- [x] ✅ 决策5: JSON格式平移列表
- [x] ✅ 决策6: 简单平均融合
- [x] ✅ 决策7: 漂移校正完整支持
- [x] ✅ 决策8: 命令行+.env配置
- [x] ✅ 决策9: 不实现交互式查看器
- [x] ✅ 决策10: 完整中间输出

### 文档完整性
- [x] ✅ 设计规格文档
- [ ] ⏳ API文档
- [ ] ⏳ 使用说明
- [ ] ⏳ 配置参数说明

### 代码质量
- [ ] ⏳ 模块化设计
- [ ] ⏳ 类型注解
- [ ] ⏳ 文档字符串
- [ ] ⏳ 错误处理
- [ ] ⏳ 日志记录

---

## 附录：PDF要求对照

### PDF第6步：漂移校正
**PDF要求:**
> "Correct for drift"
> - Matching the first image and the last one
> - Compute the gap angle θ_g
> - Distribute the gap angle evenly across the whole sequence
> - Modify rotations by θ_g/N_image
> - Update focal length f' = f(1 - θ_g/2π)
> - Only works for 1D panorama where the camera is continuously turning in the same direction

**我们的实现:**
✅ 完全按照PDF要求实现
✅ 支持自动检测是否需要校正
✅ 保存校正前后的参数对比

---

## 更新历史

- **2025-11-14:** 初始版本，确定所有核心设计决策
- 后续更新将记录在此处...

---

## 参考资料

- 项目PDF: `Proj2-Cylindrical Panoroma.pdf`
- 官方数据集: http://staff.ustc.edu.cn/~xjchen99/teaching/Project2.htm
- OpenCV SIFT文档: https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html
- 圆柱投影参考: PDF第2页公式
