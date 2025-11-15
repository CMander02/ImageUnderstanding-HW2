#!/bin/bash

# ========================================
# 示例数据集下载脚本
# ========================================
# 用途: 从官方网站下载测试图像
# 使用: bash scripts/download_sample_data.sh
# ========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_ROOT/data"

echo "========================================="
echo "圆柱全景拼接 - 示例数据集下载"
echo "========================================="
echo ""

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 官方数据集URL
OFFICIAL_URL="http://staff.ustc.edu.cn/~xjchen99/teaching/Project2.htm"

echo -e "${YELLOW}官方数据集地址:${NC}"
echo "$OFFICIAL_URL"
echo ""

echo -e "${YELLOW}数据集将保存到:${NC}"
echo "$DATA_DIR"
echo ""

# 创建目录
mkdir -p "$DATA_DIR/sample_panorama/set1_building"
mkdir -p "$DATA_DIR/sample_panorama/set2_landscape"
mkdir -p "$DATA_DIR/sample_panorama/set3_360degree"
mkdir -p "$DATA_DIR/custom"

echo -e "${GREEN}✓${NC} 数据集目录已创建"
echo ""

# 检查是否安装了wget或curl
if command -v wget &> /dev/null; then
    DOWNLOAD_CMD="wget"
elif command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -O"
else
    echo -e "${RED}错误: 未找到 wget 或 curl${NC}"
    echo "请手动从以下地址下载图像:"
    echo "$OFFICIAL_URL"
    exit 1
fi

echo -e "${YELLOW}提示:${NC}"
echo "由于官方网站结构未知，请执行以下步骤手动下载:"
echo ""
echo "1. 访问官方网站:"
echo "   $OFFICIAL_URL"
echo ""
echo "2. 下载图像序列到相应目录:"
echo "   - 建筑物全景 → $DATA_DIR/sample_panorama/set1_building/"
echo "   - 风景全景   → $DATA_DIR/sample_panorama/set2_landscape/"
echo "   - 360度全景  → $DATA_DIR/sample_panorama/set3_360degree/"
echo ""
echo "3. 图像命名建议:"
echo "   - IMG_0001.jpg, IMG_0002.jpg, ... (按拍摄顺序)"
echo "   - 或 image_001.jpg, image_002.jpg, ..."
echo ""
echo "4. 确保图像包含EXIF信息（特别是焦距）"
echo ""

# 示例: 如果知道具体文件列表，可以这样下载
# echo "正在下载示例图像..."
# cd "$DATA_DIR/sample_panorama/set1_building"
# for i in {1..10}; do
#     IMG_NUM=$(printf "%04d" $i)
#     $DOWNLOAD_CMD "http://example.com/images/IMG_$IMG_NUM.JPG"
# done

echo -e "${GREEN}✓${NC} 数据集目录结构已准备完成"
echo ""
echo "========================================="
echo "下载完成后，可以使用以下命令测试:"
echo "  python main.py --input data/sample_panorama/set1_building/"
echo "========================================="
