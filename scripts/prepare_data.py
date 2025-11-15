"""
数据准备脚本
从 USTC 服务器下载全景图数据并解压到 data 目录
"""

import urllib.request
import zipfile
from pathlib import Path


def download_and_extract_pano1():
    """下载并解压 pano1 数据集"""
    # 定义路径
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    pano1_dir = data_dir / "pano1"
    zip_path = data_dir / "pano1.zip"

    # 创建 data 目录
    data_dir.mkdir(exist_ok=True)

    # 下载数据
    url = "http://staff.ustc.edu.cn/~xjchen99/teaching/pano1.zip"
    print(f"正在从 {url} 下载数据...")
    urllib.request.urlretrieve(url, zip_path)
    print(f"下载完成，保存到 {zip_path}")

    # 解压数据
    print(f"正在解压到 {pano1_dir}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(data_dir)
    print("解压完成")

    # 删除 zip 文件
    zip_path.unlink()
    print("已删除临时 zip 文件")

    # 验证文件结构
    if pano1_dir.exists():
        image_files = list(pano1_dir.glob("*"))
        print(f"\n成功！在 {pano1_dir} 中找到 {len(image_files)} 个文件")
        print("文件列表：")
        for f in sorted(image_files)[:10]:  # 只显示前10个文件
            print(f"  - {f.name}")
        if len(image_files) > 10:
            print(f"  ... 以及其他 {len(image_files) - 10} 个文件")
    else:
        print(f"警告：{pano1_dir} 不存在")


if __name__ == "__main__":
    download_and_extract_pano1()
